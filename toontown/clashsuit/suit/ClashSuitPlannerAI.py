"""
ClashSuitPlannerAI module:  contains the ClashSuitPlannerAI
class which handles management of all suits within a single neighborhood.
"""

import random
import time
from typing import TYPE_CHECKING, Dict

from direct.distributed import DistributedObjectAI
from direct.task.Task import Task
from direct.showbase import PythonUtil
from panda3d.core import ConfigVariableBool

from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.dna.DNASuitPoint import DNASuitPoint
from toontown.notifications.notificationData.GenericTextNotification import GenericTextNotification, GenericTextId
from toontown.quest3.base import QuestGlobals
from toontown.clashsuit.suit import ClashSuitAI, SuitTimings
from toontown.clashsuit.suit import SuitDNA
from toontown.clashsuit.suit import SuitPlannerBase
from toontown.clashbattle.battle import BattleManagerAI
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.building import ClashSuitBuildingGlobals
from toontown.hood import ZoneUtil
from toontown.clashsuit.suit.SuitInvasionGlobals import IFSkelecog, IFWaiter, IFV2, IFExe
from toontown.clashsuit.suit.SuitLegList import SuitLeg
from toontown.clashsuit.suit import SuitHoodGlobals as SHG
from toontown.clashbattle.battle import BattleGlobals
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.RateLimiter import RateLimiter

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


@DirectNotifyCategory()
class ClashSuitPlannerAI(DistributedObjectAI.DistributedObjectAI, SuitPlannerBase.SuitPlannerBase):
    """
    manages all suits which exist within
    a single neighborhood (or street), this includes suits in buildings.
    It handles creating suits if the neighborhood needs more, or removing
    suits if there are too many.  This object only exists on the server
    AI.

    Attributes:
        suitList (list), list of all suits that this planner controls
    """
    defaultSuitName = ConfigVariableString('suit-type', 'random').getValue()
    if defaultSuitName == 'random':
        defaultSuitName = None

    def __init__(self, air, zoneId):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        SuitPlannerBase.SuitPlannerBase.__init__(self)
        self.air = air  # type: ToontownAIRepository
        self.zoneId = zoneId
        self.canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)

        # remember which entry in SuitHoodInfo this suit planner will be
        # using, this is based on the zone id assigned
        self.branchDef = SHG.SuitHoodInfo.get(zoneId, None)
        assert self.branchDef is not None, "SuitPlannerAI missing branch def"
        self.spawnDef = self.branchDef.getCogSpawnDefinition()

        # remember the number of suits we want in this hood
        # this could vary based on toons currently in the hood and
        # a random population range that changes over time
        # currDesired is a manual override to create a specific number
        # of suits if it is set to a valid number
        self.currDesired = None
        self.baseNumSuits = self.branchDef.getCogMean()

        # Remember the number of buildings we are assigned for this
        # particular street.  This will vary between streets as
        # buildings are reclaimed by toons to keep the global number
        # of suit buildings across the shard constant.  But, we have
        # to start out with at least the specified minimum.
        self.targetNumSuitBuildings = self.branchDef.getMinCogBuildings()

        # This records the tracks requested for the pending buildings.
        # As each building is created, it selects a track from this
        # list, if the list is nonempty.
        self.pendingBuildingTracks = []

        # Similarly, for the number of floors requested for pending
        # buildings.
        self.pendingBuildingHeights = []
        # various lists of suits, most are temporary holding lists,
        # the main list is 'suitList'
        self.suitList = []
        self.numFlyInSuits = 0
        self.numBuildingSuits = 0
        self.numAttemptingTakeover = 0

        self.suitQueue = []

        self.zoneInfo = {}

        self.zoneIdToPointMap = None

        # This may be filled in with a list of lobby doors if this
        # happens to be a SuitPlanner for a CogHQExterior.
        self.cogHQDoors = []

        self.battleList = []

        # Create a battle manager AI for the street
        self.battleMgr = BattleManagerAI.BattleManagerAI(self.air)

        # load up the dna to fill in the suit path point information
        self.setupDNA()

        if self.notify.getDebug():
            self.notify.debug('Creating a building manager AI in zone' + str(self.zoneId))
        self.buildingMgr = self.air.buildingManagers.get(self.zoneId)

        # tell all buildings in this building manager which suit
        # planner is in the same hood, and if the building is a
        # suit building, make sure to add it to our list of suit
        # blocks (used to find suit source and destination locations
        # when creating paths)
        if self.buildingMgr:
            result = self.buildingMgr.getDNABlockLists()

            blocks = result[0]  # normal buildings
            # hqBlocks         = result[1]   # not needed here
            # uncapturableBlocks = result[2]
            # gagshopBlocks    = result[3]
            # petshopBlocks    = result[4]
            # kartshopBlocks   = result[5]
            animBldgBlocks = result[6]

            for currBlock in blocks:
                bldg = self.buildingMgr.getBuilding(currBlock)
                bldg.setSuitPlannerExt(self)

            for currBlock in animBldgBlocks:
                bldg = self.buildingMgr.getBuilding(currBlock)
                if bldg is not None:
                    bldg.setSuitPlannerExt(self)
        # The block number to zone map was created for the building
        # and door creation.  Now that it's done, we clear the map:
        self.dnaStore.resetBlockNumbers()
        # now let all of the buildings know what path points they should
        # be associated with
        self.initBuildingsAndPoints()
        # set the suit number override if one is provided in the prc
        numSuits = ConfigVariableInt('suit-count', -1).getValue()
        if numSuits >= 0:
            self.currDesired = numSuits
        suitHood = ConfigVariableInt('suits-only-in-hood', -1).getValue()
        if suitHood >= 0:
            if self.zoneId != suitHood:
                self.currDesired = 0

        # an adjustment to the base desired num suits in this hood, this
        # adjustment changes gradually over time
        self.suitCountAdjust = 0

        # Ratelimiters for building/suit queries, prevents spamming
        self.ratelimiters = {}

    def cleanup(self):
        """
        called before this guy is deleted, remove any
        pending tasks
        """
        # remove the task that updates the suitPlannerAI periodically
        simbase.taskMgr.remove(self.taskName('sptUpkeepPopulation'))
        simbase.taskMgr.remove(self.taskName('sptAdjustPopulation'))
        for suit in self.suitList:
            suit.stopTasks()
            if suit.isGenerated():
                self.zoneChange(suit, suit.zoneId)
                suit.requestDelete()

        self.suitList = []
        self.numFlyInSuits = 0
        self.numBuildingSuits = 0
        self.numAttemptingTakeover = 0

    def delete(self):
        self.cleanup()
        DistributedObjectAI.DistributedObjectAI.delete(self)
        SuitPlannerBase.SuitPlannerBase.delete(self)

    def initBuildingsAndPoints(self):
        """
        let all the buildings know about the suit path
        points that are in front of them, this way the suit
        planner can ask the building for path points which
        suits can use to enter and exit the building
        """
        if not self.buildingMgr:
            return
        if self.notify.getDebug():
            self.notify.debug('Initializing building points')

        # We need to associate buildings with their doors.  This just
        # builds a reverse lookup based on the data we already
        # extracted from the DNA file.  Each building should have
        # one front door and one or more side doors.

        self.buildingFrontDoors = {}
        self.buildingSideDoors = {}

        for p in self.frontdoorPointList:
            blockNumber = p.getLandmarkBuildingIndex()
            if blockNumber < 0:
                self.notify.debug('No landmark building for (%s) in zone %s' % (str(p), self.zoneId))
                continue
            if blockNumber in self.buildingFrontDoors:
                self.notify.debug('Multiple front doors for building %s in zone %s' % (blockNumber, self.zoneId))
                continue
            self.buildingFrontDoors[blockNumber] = p

        for p in self.sidedoorPointList:
            blockNumber = p.getLandmarkBuildingIndex()
            if blockNumber < 0:
                self.notify.debug('No landmark building for (%s) in zone %s' % (str(p), self.zoneId))
                continue
            if blockNumber in self.buildingSideDoors:
                self.buildingSideDoors[blockNumber].append(p)
                continue
            self.buildingSideDoors[blockNumber] = [p]

        # Now make sure that each building has *at least* one of each
        # kind of door.
        #from toontown.building.DistributedUncapturableBuildingAI import DistributedUncapturableBuildingAI
       # for bldg in self.buildingMgr.getBuildings():
        #    if isinstance(bldg, DistributedUncapturableBuildingAI):
                # Move to the next one
         #       continue
          #  blockNumber = bldg.getBlock()[0]
          #  if blockNumber not in self.buildingFrontDoors:
          #      self.notify.debug('No front door for building %s in zone %s' % (blockNumber, self.zoneId))
          #  if blockNumber not in self.buildingSideDoors:
           #     self.notify.debug('No side door for building %s in zone %s' % (blockNumber, self.zoneId))

    def countNumSuitsPerTrack(self, count):
        """
        countNumSuitsPerTrack(self, map count)
        Given that count is a map of track letters to counts, e.g. {
        'c':0, 'l':0, 'm':0, 's':0 }, or an empty map, increment each
        count corresponding to the number of suits of that type in the
        neighborhood.  This is only used for magic word fulfillment
        and debug output.
        """
        for suit in self.suitList:
            if suit.track in count:
                count[suit.track] += 1
                continue
            count[suit.track] = 1

    def countNumBuildingsPerTrack(self, count):
        """
        countNumBuildingsPerTrack(self, map count)
        Given that count is a map of track letters to counts, e.g. {
        'c':0, 'l':0, 'm':0, 's':0 }, or an empty map, increment each
        count corresponding to the number of suit buildings of that
        type in the neighborhood.
        """
        if not self.buildingMgr:
            return
        for building in self.buildingMgr.getBuildings():
            if building.isSuitBuilding():
                if building.track in count:
                    count[building.track] += 1
                else:
                    count[building.track] = 1

    def countNumBuildingsPerHeight(self, count):
        """
        countNumBuildingsPerHeight(self, map count)
        Given that count is a map of heights to counts, e.g. { 0:0,
        1:0, 2:0, 3:0, 4:0 }, or an empty map, increment each count
        corresponding to the number of suit buildings of that height
        in the neighborhood.
        Note that the building "height" is the zero-based index into
        the number of floors: height = numFloors - 1.
        """
        if not self.buildingMgr:
            return
        for building in self.buildingMgr.getBuildings():
            if building.isSuitBuilding():
                height = building.numFloors - 1
                if height in count:
                    count[height] += 1
                else:
                    count[height] = 1

    def isSuitInPlanner(self, suitType):
        return suitType in [suit.dna.name for suit in self.suitList]

    def countSuitsInPlanner(self, suitName):
        # this also counts suits in battles in its zone
        return sum([1 for suit in self.suitList if suit.dna.name == suitName])

    def countBldgDifficultiesInPlanner(self, difficulty):
        return sum([1 for bldg in self.buildingMgr.getBuildings() if hasattr(bldg, 'difficulty') and bldg.difficulty == difficulty])

    def formatNumSuitsPerTrack(self, count):
        """
        formatNumSuitsPerTrack(self, map count)
        Given a map filled in by a previous call to
        countNumSuitsPerTrack() or countNumBuildingsPerTrack(),
        formats the result as a string.
        """
        result = ' '
        for (track, num) in list(count.items()):
            result += ' %s:%s' % (track, num)
        return result[2:]

    def calcDesiredNumFlyInSuits(self):
        """
        Returns the number of fly-in suits that should be walking
        around the neighborhood.
        """

        # first check to see if a manual suit count override has been
        # specified, if not, return base number of suits plus any
        # previously calculated adjustment
        if self.currDesired is not None:
            return 0
        return self.baseNumSuits + self.suitCountAdjust

    def calcDesiredNumBuildingSuits(self):
        """
        Returns the number of building suits that should be walking
        around the neighborhood.
        """
        if self.currDesired is not None:
            return self.currDesired
        if not self.buildingMgr:
            return 0
        suitBuildings = self.buildingMgr.getEstablishedSuitBlocks()
        return int(len(suitBuildings) * SHG.SUIT_BUILDING_NUM_SUITS)

    def getZoneIdToPointMap(self):
        """
        Creates a reverse lookup from street zoneId's to lists of
        DNASuitPoints.  This is only used for magic word fulfillment,
        so the map isn't created until it is demanded.  It's fairly
        expensive to create this map, since the points aren't really
        designed to be looked up this way.
        """
        if self.zoneIdToPointMap is not None:
            return self.zoneIdToPointMap

        self.zoneIdToPointMap = {}

        for point in self.streetPointList:
            # Determine the zones the point intersects by pulling out
            # all the points adjacent to this one.
            points = self.dnaStore.getAdjacentPoints(point)
            i = points.getNumPoints() - 1
            while i >= 0:
                pi = points.getPointIndex(i)
                p = self.pointIndexes[pi]
                i -= 1
                zoneId = self.dnaStore.getSuitEdgeZone(point.getIndex(), p.getIndex())
                if zoneId in self.zoneIdToPointMap:
                    self.zoneIdToPointMap[zoneId].append(point)
                    continue
                self.zoneIdToPointMap[zoneId] = [point]
        return self.zoneIdToPointMap

    def getStreetPointsForBuilding(self, blockNumber):
        """
        getStreetPointsForBuilding(self, int blockNumber)
        Returns a list of street points in front of the indicated
        building.  This function is only used for magic word
        fulfillment.
        """
        pointList = []
        if blockNumber in self.buildingSideDoors:
            for doorPoint in self.buildingSideDoors[blockNumber]:
                # given the door point, find the street points in
                # front of it.
                points = self.dnaStore.getAdjacentPoints(doorPoint)

                i = points.getNumPoints() - 1
                while i >= 0:
                    pi = points.getPointIndex(i)
                    point = self.pointIndexes[pi]
                    if point.getPointType() in (DNASuitPoint.STREET_POINT, DNASuitPoint.HIDDEN_STREET_POINT):
                        pointList.append(point)
                    i -= 1

        if blockNumber in self.buildingFrontDoors:
            doorPoint = self.buildingFrontDoors[blockNumber]
            points = self.dnaStore.getAdjacentPoints(doorPoint)

            i = points.getNumPoints() - 1
            while i >= 0:
                pi = points.getPointIndex(i)
                pointList.append(self.pointIndexes[pi])
                i -= 1

        return pointList

    def createNewSuit(self, blockNumbers, streetPoints, toonBlockTakeover=None, minPathLen=None, maxPathLen=None,
            buildingHeight=None, suitLevel=None, suitType=None, suitTrack=None,
            suitName=None, skelecog=None, revives=None, waiter=None, exe=None, summoned=False):
        """
        createNewSuit(self, list blockNumbers, list streetPoints)
        Chooses a suitable point from streetPoints (if the list is
        nonempty), or a suit building from blockNumbers, in which to
        create the suit.  Removes unsuitable points from either array.
        If no suitable point or building can be found, returns 0.
        If a suitable starting point is found, creates a new suit and
        starts it walking around.  If the starting point is from the
        streetPoints, the street is flown in from the sky; otherwise,
        it walks out of the chosen building.
        The return value is the suit if one is created, or None otherwise.
        The additional keyword arguments are primarily for the benefit
        of magic words to create suits for special purposes.
        toonBlockTakeover, if specified, is the block number of a toon
        building to take over specifically.  minPathLen and maxPathLen
        put limits on the length of the suit's path, in number of suit
        points.  suitLevel, suitType, and suitTrack define the
        particular kind of suit to create; otherwise, a random suit is
        chosen based on the neighborhood parameters.  suitName is
        another way to specify a type of suit; it may be any of the
        one- or two-letter suit codes, like 'pp' or 'ym'.

        Dear reader:
        If you are passing streetPoints to this function, make sure it's
        a COPY of the SuitPlanner's streetPointList. Otherwise,
        you are at risk of deleting them permanently.
        """
        # Do we have a more important cog to spawn?
        if self.suitQueue:
            blockNumbers, streetPoints, toonBlockTakeover, minPathLen, maxPathLen, \
            buildingHeight, suitLevel, suitType, suitTrack, \
            suitName, skelecog, revives, waiter, exe, summoned = self.suitQueue.pop()
            streetPoints = self.streetPointList[:]
        # First, choose a good starting point for the suit.
        startPoint = None
        blockNumber = None
        stubborn = suitName in SuitBattleGlobals.STUBBORN_COGS
        self.skeleChance = 0
        self.isElite = True if exe else False
        queueArgs = [blockNumbers, streetPoints, toonBlockTakeover, minPathLen, maxPathLen,
                     buildingHeight, suitLevel, suitType, suitTrack,
                     suitName, skelecog, revives, waiter, exe, summoned]

        if self.notify.getDebug():
            self.notify.debug('Choosing origin from %d+%d possibles.' % (len(streetPoints), len(blockNumbers)))

        # This cog is stubborn, so we will have to allocate room for them.
        if stubborn:
            streetPoints = self.streetPointList[:]
            for _ in range(2):
                self.removeRandomSuit(makeFly=True)

        # Knowing the suit type, let's see if it's already capped in the suit planner.
        if suitName in SuitBattleGlobals.STREET_MAX_COG:
            maxSuit = SuitBattleGlobals.STREET_MAX_COG[suitName]
            # This function also counts what is in the battles.
            if self.countSuitsInPlanner(suitName) >= maxSuit:
                # We probably shouldn't queue here.
                return None

        # First, try to create a from-building suit.
        if not stubborn:
            while startPoint is None and len(blockNumbers) > 0:
                bn = random.choice(blockNumbers)
                blockNumbers.remove(bn)
                if bn in self.buildingSideDoors:
                    for doorPoint in self.buildingSideDoors[bn]:
                        # given the door point, find the street points in
                        # front of it.
                        points = self.dnaStore.getAdjacentPoints(doorPoint)

                        # Now iterate through all the street points.
                        # We'll count down from the end just because
                        # that's easier.
                        i = points.getNumPoints() - 1
                        while blockNumber is None and i >= 0:
                            pi = points.getPointIndex(i)
                            p = self.pointIndexes[pi]
                            i -= 1

                            # Now include the travel time from the door point
                            # to the street.
                            startTime = SuitTimings.fromSuitBuilding
                            startTime += self.dnaStore.getSuitEdgeTravelTime(doorPoint.getIndex(), pi, self.suitWalkSpeed)
                            if not self.pointCollision(p, doorPoint, startTime):
                                # reset the start time back to our first point.
                                startTime = SuitTimings.fromSuitBuilding
                                startPoint = doorPoint
                                blockNumber = bn

        # Failing that, just fly a suit in.
        while startPoint is None and len(streetPoints) > 0:
            p = random.choice(streetPoints)
            streetPoints.remove(p)

            if not self.pointCollision(p, None, SuitTimings.fromSky):
                startPoint = p
                startTime = SuitTimings.fromSky
                continue
        if startPoint is None:
            if stubborn:
                self.queueSuit(queueArgs)
            return None

        newSuit = ClashSuitAI.ClashSuitAI(simbase.air, self)
        newSuit.startPoint = startPoint
        if blockNumber is not None:
            # The suit originates from a building.  This also means it
            # inherits the building's track.
            newSuit.buildingSuit = 1
            if suitTrack is None:
                suitTrack = self.buildingMgr.getBuildingTrack(blockNumber)

        else:
            # The suit flies in from the sky.
            newSuit.flyInSuit = 1

            # Only fly-in suits may attempt building takeovers.  This
            # helps preserve the balance of building tracks on a
            # particular street.  If we did not do this, once a
            # particular building track got a toehold it would have an
            # advantage over the other tracks.
            newSuit.attemptingTakeover = self.newSuitShouldAttemptTakeover()

            if suitName in SuitBattleGlobals.MERCS:
                newSuit.attemptingTakeover = False
            elif suitName in SuitBattleGlobals.STUBBORN_COGS:
                newSuit.attemptingTakeover = False
            if newSuit.attemptingTakeover:
                # Also, if he's attempting a takeover, make him be a
                # suitable track.
                if suitTrack is None and len(self.pendingBuildingTracks) > 0:
                    suitTrack = self.pendingBuildingTracks[0]

                    # Move the suitTrack to the end of the queue, so
                    # the next suit will choose a different track.  We
                    # can't remove it from the queue until the
                    # building actually gets created.
                    del self.pendingBuildingTracks[0]
                    self.pendingBuildingTracks.append(suitTrack)

                if buildingHeight is None and len(self.pendingBuildingHeights) > 0:
                    buildingHeight = self.pendingBuildingHeights[0]
                    del self.pendingBuildingHeights[0]
                    self.pendingBuildingHeights.append(buildingHeight)

        # Don't let invasion apply if we are in TTC.
        respectsInvasion = self.shouldRespectInvasion()

        # If we're constrained to create only a particular type of
        # suit, do so.
        if not suitName:
            if respectsInvasion and self.air.suitInvasionManager.getInvading():
                # If there is an invasion, the suit name will be picked for us
                suitTrack, suitName, flags = self.air.suitInvasionManager.getInvadingCog()
                # Apply all invasion flags
                if flags & IFSkelecog:
                    skelecog = 1
                if flags & IFWaiter:
                    waiter = True
                if flags & IFV2:
                    revives = 1
                if flags & IFExe:
                    self.isElite = True
            # If we are still at none, use the default suit
            if not suitName:
                suitName = self.defaultSuitName

        if not suitType and suitName:
            suitType = SuitDNA.getSuitType(suitName)
            suitTrack = SuitDNA.getSuitDept(suitName)

        if suitLevel is None and buildingHeight is not None:
            # Choose an appropriate level suit that will make a
            # building of the requested height.
            suitLevel = self.chooseSuitLevel(self.spawnDef.getSuitLevelMin(),
                                             self.spawnDef.getSuitLevelMax(),
                                             buildingHeight)

        # Now fill in the level, type, and track parameters that
        # haven't been specified yet.
        suitLevel, suitType, suitTrack = self.pickLevelTypeAndTrack(suitLevel, suitType, suitTrack, suitName)
        if suitType > 8:  # Start of custom cog range
            newSuit.setupCustomSuitDNA(suitName, suitTrack, suitLevel)
        elif summoned:
            if SuitDNA.isAlternate(suitName):
                newSuit.setupCustomSuitDNA(suitName, suitTrack, suitLevel)
            else:
                newSuit.setupSuitDNA(suitLevel, suitType, suitTrack, respectsInvasion=False, wantAlts=False)
        else:
            newSuit.setupSuitDNA(suitLevel, suitType, suitTrack, respectsInvasion=respectsInvasion, wantAlts=True)
        newSuit.buildingHeight = buildingHeight
        gotDestination = self.chooseDestination(newSuit, startTime, toonBlockTakeover = toonBlockTakeover, minPathLen = minPathLen, maxPathLen = maxPathLen)
        if not gotDestination:
            # No good destination, for some reason.  Delete the suit
            # and return 0 to try again.
            self.notify.debug("Couldn't get a destination in %d!" % self.zoneId)
            newSuit.doNotDeallocateChannel = None
            newSuit.delete()
            if stubborn:
                self.queueSuit(queueArgs)
            return None

        # Initialize all the path information for passing down to
        # clients.
        newSuit.initializePath()

        # be sure to flag the zone change when this suit is first
        # created
        self.zoneChange(newSuit, None, newSuit.zoneId)

        # if this suit is a skeleton...
        if skelecog:
            newSuit.setSkelecog(skelecog)

        # if this suit is a version 2.0...
        if self.skeleChance == 1:
            newSuit.setSkelecog(1)

        if revives is not None:
            newSuit.setSkeleRevives(revives)

        if self.isElite:
            newSuit.setElite(1)

        # call 'generate' to create all versions of this suit,
        # including the local server side version, as well as all of
        # the client side versions, this also creates the suit's
        # unique distributed object id
        newSuit.generateWithRequired(newSuit.zoneId)

        if waiter:
            newSuit.b_setWaiter(1)

        newSuit.d_setSPDoId(self.doId)

        # And now we can start the suit walking.
        newSuit.moveToNextLeg(None)
        # now add the suit to our list so we can do things with it when
        # needed
        self.suitList.append(newSuit)

        if newSuit.flyInSuit:
            self.numFlyInSuits += 1

        if newSuit.buildingSuit:
            self.numBuildingSuits += 1

        if newSuit.attemptingTakeover:
            self.numAttemptingTakeover += 1

        return newSuit

    def queueSuit(self, argList):
        """
        Some suits really want to spawn, so even if createNewSuit fails,
        they'll try again several seconds later.
        """
        self.suitQueue.append(argList)

    def countNumNeededBuildings(self):
        """
        Returns the number of additional suit buildings we want to try
        to take over.
        """
        if not self.buildingMgr:
            return False
        numSuitBuildings = len(self.buildingMgr.getSuitBlocks())
        if (random.random() * 100) < self.branchDef.getBuildingSpawnChance():
            bmax = self.branchDef.getMaxCogBuildings()
            numNeeded = bmax - numSuitBuildings
        else:
            numNeeded = self.targetNumSuitBuildings - numSuitBuildings
        return numNeeded

    def newSuitShouldAttemptTakeover(self):
        """
        Decides whether it is time for a newly-created suit to attempt
        to take over an innocent toon building.  Returns true if so,
        false otherwise.
        """
        if not SHG.SUITS_ENTER_BUILDINGS:
            return False
        numNeeded = self.countNumNeededBuildings()

        if self.numAttemptingTakeover >= numNeeded:
            # There's already enough suits on the march.  Never mind.
            self.pendingBuildingTracks = []
            return False
        self.notify.debug('DSP %s is planning a takeover attempt in zone %s' % (self.getDoId(), self.zoneId))
        return True

    def chooseDestination(self, suit, startTime: float, toonBlockTakeover=None, minPathLen=None, maxPathLen=None):
        """
        chooseDestination(self, ClashSuitAI suit, float startTime)
        Given that the suit has already been assigned a starting point
        (suit.startPoint) and that it has already decided whether it
        will attempt to take over a toon building
        (suit.attemptingTakeover), choose a suitable destination point
        for the suit.
        startTime is the number of seconds from now at which the suit
        will start on the path.  This is needed to properly separate
        the suit from other suits.
        The return value is true if a path can be found, or false if not.
        """
        # First, build up the list of all of our possible destinations.
        possibles = []
        destinationDict = {}
        if toonBlockTakeover is not None:
            # The suit is specifically charged with taking over this
            # particular toon building.  This will only happen due to
            # a magic word or something.
            suit.attemptingTakeover = 1

            blockNumber = toonBlockTakeover
            if blockNumber in self.buildingFrontDoors:
                point = self.buildingFrontDoors[blockNumber]
                possibles.append(point)
                destinationDict[point] = blockNumber
        elif suit.attemptingTakeover:
            # We have all of the toon buildings to choose from, except
            # for the "protected" buildings.
            if self.buildingMgr:
                for blockNumber in self.buildingMgr.getToonBlocks():
                    building = self.buildingMgr.getBuilding(blockNumber)
                    (extZoneId, intZoneId) = building.getExteriorAndInteriorZoneId()
                    if not QuestGlobals.isZoneProtected(intZoneId):
                        if blockNumber in self.buildingFrontDoors:
                            point = self.buildingFrontDoors[blockNumber]
                            possibles.append(point)
                            destinationDict[point] = blockNumber

        elif self.buildingMgr and not suit.isStubborn():
            # We have all of the suit buildings that match our DNA
            # track to choose from (corporate suits don't mingle with
            # legal suits), as well as all points in the street.
            for blockNumber in self.buildingMgr.getSuitBlocks():
                track = self.buildingMgr.getBuildingTrack(blockNumber)
                if (track == suit.dna.dept) and (blockNumber in self.buildingSideDoors):
                    for doorPoint in self.buildingSideDoors[blockNumber]:
                        possibles.append(doorPoint)
                        destinationDict[doorPoint] = blockNumber

        # Figure out our path length.
        if minPathLen is None:
            if suit.attemptingTakeover:
                minPathLen = SHG.MIN_TAKEOVER_PATH_LEN
            else:
                minPathLen = SHG.MIN_PATH_LEN
        if maxPathLen is None:
            maxPathLen = SHG.MAX_PATH_LEN

        # Fallback on possibles if somehow we didn't get any.
        if not possibles:
            possibles = self.streetPointList[:]

        # Now pull destinations out at random, one at a time, until
        # we're happy with the resulting path.
        retryCount = 0
        random.shuffle(possibles)
        while possibles and (retryCount < 25):
            # Grab our point.
            point = possibles.pop()

            if len(possibles) == 0:
                # We cannot choose to give up here! Keep trying!!
                possibles = self.streetPointList[:]
                random.shuffle(possibles)

            # Build our path.
            path = self.genPath(suit.startPoint, point, minPathLen, maxPathLen)
            if path and (not self.pathCollision(path, startTime)):
                # The path looks good; take it!
                suit.endPoint = point
                suit.minPathLen = minPathLen
                suit.maxPathLen = maxPathLen
                suit.buildingDestination = destinationDict.get(point, None)
                suit.setPath(path)
                return 1

            retryCount += 1

        # None of our destinations were suitable.  Probably there was
        # a battle going on very near our starting point, trapping us
        # in a corner or something.
        return 0

    def pathCollision(self, path, elapsedTime):
        """pathCollision(self, DNASuitPath path)
        Returns true if the path is unsuitable because another suit
        will be walking too close by its first point in elapsedTime
        seconds or if there is a battle there right now, or false
        otherwise.
        """
        i = 0
        pi = path.getPointIndex(i)
        point = self.pointIndexes[pi]

        # Start off with adjacentPoint indicating the second point in
        # the path, in case the first point happens to be a street
        # point.
        adjacentPoint = self.pointIndexes[path.getPointIndex(i + 1)]
        while (point.getPointType() == DNASuitPoint.FRONT_DOOR_POINT) or (
                point.getPointType() == DNASuitPoint.SIDE_DOOR_POINT):
            i += 1
            lastPi = pi
            pi = path.getPointIndex(i)
            adjacentPoint = point
            point = self.pointIndexes[pi]
            elapsedTime += self.dnaStore.getSuitEdgeTravelTime(lastPi, pi, self.suitWalkSpeed)
        result = self.pointCollision(point, adjacentPoint, elapsedTime)

        return result

    def pointCollision(self, point, adjacentPoint, elapsedTime):
        """pointCollision(self, DNASuitPoint point, DNASuitPoint adjacentPoint,
                          float elapsedTime)
        Returns true if the point is unsuitable for starting a path
        because another suit will be walking right there in
        elapsedTime seconds, or if there is a battle there right now.
        See also pathCollision().
        If adjacentPoint is not None, it is a point adjacent to the
        point we are testing, which is used to determine what zone the
        point in question is in (for checking for battles).  If
        adjacentPoint is None, then all adjacent points will be
        checked.
        """
        for suit in self.suitList:
            if suit.pointInMyPath(point, elapsedTime):
                return 1
        if adjacentPoint is not None:
            return self.battleCollision(point, adjacentPoint)
        else:
            # Go through all the points adjacent to the indicated one.
            # If there's a battle in any of these, it counts.

            points = self.dnaStore.getAdjacentPoints(point)
            i = points.getNumPoints() - 1
            while i >= 0:
                pi = points.getPointIndex(i)
                p = self.pointIndexes[pi]
                i -= 1

                if self.battleCollision(point, p):
                    return 1

        # No suits or battles in sight.
        return 0

    def battleCollision(self, point, adjacentPoint):
        """battleCollision(self, DNASuitPoint point, DNASuitPoint adjacentPoint)
        Returns true if there is a battle currently underway in the
        zone containing the edge connecting point and adjacentPoint.
        """
        zoneId = self.dnaStore.getSuitEdgeZone(point.getIndex(), adjacentPoint.getIndex())
        return self.battleMgr.cellHasBattle(zoneId)

    def removeRandomSuit(self, makeFly=False):
        """
        Removes a random suit from the planner.
        """
        suitRemovable = []
        for suit in self.suitList:
            if suit.pathState == 1:
                suitRemovable.append(suit)
        if suitRemovable:
            self.removeSuit(random.choice(suitRemovable), makeFly=makeFly)

    def removeSuit(self, suit, makeFly=False):
        """
        Removes a suit that's no longer needed.  This deletes the
        DistributedObject and also cleans up any data structures
        referencing the suit in the planner.
        """

        # be sure to clear the zone that the suit is in since it
        # is going to be removed completely
        self.zoneChange(suit, suit.zoneId)

        if self.suitList.count(suit) > 0:
            self.suitList.remove(suit)

            if suit.flyInSuit:
                self.numFlyInSuits -= 1
            if suit.buildingSuit:
                self.numBuildingSuits -= 1
            if suit.attemptingTakeover:
                self.numAttemptingTakeover -= 1
        if makeFly:
            suit.flyAwayNow(forceRemove=True)
        else:
            suit.requestDelete()

    def countTakeovers(self):
        """
        Returns the number of suits *actually* attempting takeover.
        This is just a verification check against
        self.numAttemptingTakeover; it only gets called when
        assertions are enabled.
        """
        count = 0
        for suit in self.suitList:
            if suit.attemptingTakeover:
                count += 1
        return count

    def __waitForNextUpkeep(self):
        t = 15
        taskMgr.doMethodLater(t, self.upkeepSuitPopulation, self.taskName('sptUpkeepPopulation'))

    def __waitForNextAdjust(self):
        t = 15
        taskMgr.doMethodLater(t, self.adjustSuitPopulation, self.taskName('sptAdjustPopulation'))

    def upkeepSuitPopulation(self, task):
        """
        examine the number of suits that exist and remove
        or add some in order to keep a reasonable balance,
        this should be called every once in a while
        """

        # How many fly-in suits do we expect to have?
        targetFlyInNum = self.calcDesiredNumFlyInSuits()
        targetFlyInNum = min(targetFlyInNum, SHG.TOTAL_MAX_SUITS - self.numBuildingSuits)

        # We'll need a copy of the list of street points, so we can
        # modify this as we eliminate choices.
        streetPoints = self.streetPointList[:]

        # We create one-fourth of the required number of suits each
        # time.  This will help us get caught up if we are way behind
        # in suits.
        flyInDeficit = ((targetFlyInNum - self.numFlyInSuits) + 3) // 4
        while flyInDeficit > 0:
            if not self.createNewSuit([], streetPoints):
                break

            flyInDeficit -= 1

        # How many from-building suits do we expect to have?  Here we
        # count up the number of from-building suits we want, and add
        # in the number of fly-in suits we couldn't have from above,
        # to bring our total suit count to as close an approximation
        # as possible of our actual target.
        if self.buildingMgr:
            suitBuildings = self.buildingMgr.getEstablishedSuitBlocks()
        else:
            suitBuildings = []

        if self.currDesired is not None:
            targetBuildingNum = max(0, self.currDesired - self.numFlyInSuits)
        else:
            targetBuildingNum = int(len(suitBuildings) * SHG.SUIT_BUILDING_NUM_SUITS)

        targetBuildingNum += flyInDeficit
        targetBuildingNum = min(targetBuildingNum, SHG.TOTAL_MAX_SUITS - self.numFlyInSuits)

        buildingDeficit = ((targetBuildingNum - self.numBuildingSuits) + 3) // 4

        # Also, while we create from-building suits, we allow them to
        # fall back to fly-in suits if they can't find a door to walk
        # out of.
        while buildingDeficit > 0:
            if not self.createNewSuit(suitBuildings, streetPoints):
                break

            buildingDeficit -= 1
        if self.notify.getDebug() and self.currDesired is None:
            self.notify.debug('zone %d has %d of %d fly-in and %d of %d building suits.' % (self.zoneId, self.numFlyInSuits, targetFlyInNum, self.numBuildingSuits, targetBuildingNum))
            if buildingDeficit != 0:
                self.notify.debug('remaining deficit is %d.' % buildingDeficit)

        # Finally, automatically reconvert the oldest suit building to
        # a toon building, if it's very old.  If no one's taken it
        # over by now, let it go back into the pool.

        if self.buildingMgr:
            suitBuildings = self.buildingMgr.getEstablishedSuitBlocks()
            timeoutIndex = min(len(suitBuildings), len(SHG.SUIT_BUILDING_TIMEOUT) - 1)
            timeout = SHG.SUIT_BUILDING_TIMEOUT[timeoutIndex]
            if timeout is not None:
                timeout *= 3600.0

                # Determine the oldest (unoccupied) suit building.
                oldest = None
                oldestAge = 0
                now = time.time()
                for b in suitBuildings:
                    building = self.buildingMgr.getBuilding(b)
                    if hasattr(building, 'elevator'):
                        if building.elevator.fsm.getCurrentState().getName() == 'waitEmpty':
                            age = now - building.becameSuitTime
                            if age > oldestAge:
                                oldest = building
                                oldestAge = age

                if oldestAge > timeout:
                    # It's time to reconvert a building.
                    self.notify.info('Street %d has %d buildings; reclaiming %0.2f-hour-old building.' % (self.zoneId, len(suitBuildings), oldestAge / 3600.0))
                    oldest.b_setVictorList([0, 0, 0, 0])
                    # Update the trophy manager to let it know these rescuers no longer
                    # get credit for this building
                    oldest.updateSavedBy(None)
                    oldest.toonTakeOver()

        self.__waitForNextUpkeep()
        return Task.done

    def adjustSuitPopulation(self, task):
        """
        randomly adjust the actual suit population over time
        """
        # if our base number of suits is zero, dont do any adjustments since
        # in this case there is most likely a reason we want zero suits in
        # the first place
        if self.branchDef.getCogMax() == 0:
            self.__waitForNextAdjust()
            return Task.done
        minSuits, maxSuits = self.branchDef.getCogCountRange()
        adjustment = random.choice((-2, -1, -1, 0, 0, 0, 1, 1, 2))

        # update the count adjustment to the base number of suits wanted
        # in this hood
        self.suitCountAdjust += adjustment
        # if amount is past the min or max, stop there.
        desiredNum = self.calcDesiredNumFlyInSuits()

        if desiredNum < minSuits:
            self.suitCountAdjust = minSuits - self.baseNumSuits
        elif desiredNum > maxSuits:
            self.suitCountAdjust = maxSuits - self.baseNumSuits

        self.__waitForNextAdjust()
        return Task.done

    def suitTakeOver(self, blockNumber, suitTrack, difficulty, buildingHeight):
        if self.pendingBuildingTracks.count(suitTrack) > 0:
            self.pendingBuildingTracks.remove(suitTrack)
        if self.pendingBuildingHeights.count(buildingHeight) > 0:
            self.pendingBuildingHeights.remove(buildingHeight)
        building = self.buildingMgr.getBuilding(blockNumber)
        if building is None:
            return
        building.suitTakeOver(suitTrack, difficulty, buildingHeight)

    def recycleBuilding(self):
        # Ok, now that a building has been reclaimed by a toon, make
        # sure a new building will pop up somewhere else.

        # What's the minimum number of suit buildings on this street?
        bmin = self.branchDef.getMinCogBuildings()
        # How many suit buildings do we actually have on this street?
        current = len(self.buildingMgr.getSuitBlocks())
        if (self.targetNumSuitBuildings > bmin) and (current <= self.targetNumSuitBuildings):
            # If we have more than the minimum here, and we haven't
            # passed our target number anyway, we can allow the suit
            # building to show up in a different zone.
            self.targetNumSuitBuildings -= 1
            self.assignSuitBuildings(1)

        # If we already have only the minimum number of buildings on
        # this street, we'll just keep the building here.

    def createInitialSuitBuildings(self):
        if self.buildingMgr is None:
            return

        # If we aren't at our minimum number of buildings, let's spawn some!
        suitBlockCount = len(self.buildingMgr.getSuitBlocks())
        if suitBlockCount < self.targetNumSuitBuildings:
            for _ in range(self.targetNumSuitBuildings - suitBlockCount):
                blockNumber = random.choice(self.buildingMgr.getToonBlocks())
                building = self.buildingMgr.getBuilding(blockNumber)
                if building is None:
                    continue
                if QuestGlobals.isZoneProtected(building.getExteriorAndInteriorZoneId()[1]):
                    continue
                track, suitName, flags = self.air.suitInvasionManager.getInvadingCog()

                index = 0
                for altList in SuitDNA.suitAlternates:
                    if suitName in altList:
                        suitType = index
                        suitType %= SuitDNA.suitsPerDept
                        break
                    index += 1

                if not suitName:
                    suitType = None
                elif suitName in SuitDNA.suitHeadTypes:
                    suitType = SuitDNA.suitHeadTypes.index(suitName)
                    suitType %= SuitDNA.suitsPerDept
                else:
                    # Suit doesn't exist as a conventional cog, prolly a special invasion.
                    # Set to 9 as to prevent other checks
                    suitType = 9

                (suitLevel, suitType, suitTrack) = self.pickLevelTypeAndTrack(None, suitType, track)

                building.suitTakeOver(suitTrack, suitLevel, None)

    def assignInitialSuitBuildings(self):
        """
        This is called at startup after all the
        ClashSuitPlannerAI objects have been created.  It
        decides how many suit buildings there should be in the world
        and assigns them to random zones, just to get the leaf blower
        system started.
        """
        # First, count up the total number of buildings in the world,
        # and also the total number of suit buildings we've already
        # got assigned (e.g. from minimums per zone).

        totalBuildings = 0
        targetSuitBuildings = 0
        actualSuitBuildings = 0
        for sp in list(self.air.suitPlanners.values()):
            totalBuildings += len(sp.frontdoorPointList)
            targetSuitBuildings += sp.targetNumSuitBuildings
            if sp.buildingMgr:
                actualSuitBuildings += len(sp.buildingMgr.getSuitBlocks())
        wantedSuitBuildings = int((totalBuildings*SHG.TOTAL_SUIT_BUILDING_PCT) / 100)
        self.notify.debug('Want %s out of %s total suit buildings; we currently have %s assigned, %s actual.' % (wantedSuitBuildings, totalBuildings, targetSuitBuildings, actualSuitBuildings))
        if actualSuitBuildings > 0:
            # If we already have *some* suit buildings in the world,
            # make sure they're all accounted for before we start
            # handing out more.
            numReassigned = 0

            for sp in list(self.air.suitPlanners.values()):
                if sp.buildingMgr:
                    numBuildings = len(sp.buildingMgr.getSuitBlocks())
                else:
                    numBuildings = 0
                if numBuildings > sp.targetNumSuitBuildings:
                    more = numBuildings - sp.targetNumSuitBuildings
                    sp.targetNumSuitBuildings += more
                    targetSuitBuildings += more
                    numReassigned += more

            if numReassigned > 0:
                self.notify.debug('Assigned %s buildings where suit buildings already existed.' % numReassigned)
        if wantedSuitBuildings > targetSuitBuildings:
            # Ask for more buildings.
            additionalBuildings = wantedSuitBuildings - targetSuitBuildings
            self.assignSuitBuildings(additionalBuildings)

        elif wantedSuitBuildings < targetSuitBuildings:
            # Hmm, we have to remove some targeted buildings somewhere.
            extraBuildings = targetSuitBuildings - wantedSuitBuildings
            self.unassignSuitBuildings(extraBuildings)

    def assignSuitBuildings(self, numToAssign):
        """
        After a suit building has been reclaimed by a toon (or at
        startup), locates a new street to assign each new suit building
        to.  This implements the so-called "leaf blower" model of suit
        building management, where reclaiming a building on one street
        causes a building to be taken over on a new street--all you
        can do is push buildings from one place to another; the total
        number of buildings in the world stays constant.
        """
        # Look for a suitable zone.  First, get a copy of the
        # SuitHoodInfo array, so we can remove elements from it as we
        # discover they're unsuitable.
        hoodInfo = SHG.SuitHoodInfo.copy()
        totalWeight = SHG.TOTAL_BWEIGHT
        totalWeightPerTrack = SHG.TOTAL_BWEIGHT_PER_TRACK.copy()
        totalWeightPerHeight = SHG.TOTAL_BWEIGHT_PER_HEIGHT.copy()

        # Count up the number of each track of building already in the
        # world, so we can try to balance the world by preferring the
        # rarer tracks.
        numPerTrack = {
            'c': 0,
            'l': 0,
            'm': 0,
            's': 0,
            'g': 0
        }
        for sp in list(self.air.suitPlanners.values()):
            sp.countNumBuildingsPerTrack(numPerTrack)
            numPerTrack['c'] += sp.pendingBuildingTracks.count('c')
            numPerTrack['l'] += sp.pendingBuildingTracks.count('l')
            numPerTrack['m'] += sp.pendingBuildingTracks.count('m')
            numPerTrack['s'] += sp.pendingBuildingTracks.count('s')
            numPerTrack['g'] += sp.pendingBuildingTracks.count('g')

        # Also count up the number of each height of building.
        numPerHeight = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0
        }
        for sp in list(self.air.suitPlanners.values()):
            sp.countNumBuildingsPerHeight(numPerHeight)
            numPerHeight[0] += sp.pendingBuildingHeights.count(0)
            numPerHeight[1] += sp.pendingBuildingHeights.count(1)
            numPerHeight[2] += sp.pendingBuildingHeights.count(2)
            numPerHeight[3] += sp.pendingBuildingHeights.count(3)
            numPerHeight[4] += sp.pendingBuildingHeights.count(4)
            numPerHeight[5] += sp.pendingBuildingHeights.count(5)

        # For each building:
        while numToAssign > 0:

            # Choose the track with the smallest representation for
            # this building.
            smallestCount = None
            smallestTracks = []
            for trackIndex in range(4):
                if totalWeightPerTrack[trackIndex]:
                    track = SuitDNA.suitDepts[trackIndex]
                    count = numPerTrack[track]
                    if (smallestCount is None) or (count < smallestCount):
                        smallestTracks = [track]
                        smallestCount = count
                    elif count == smallestCount:
                        smallestTracks.append(track)

            if not smallestTracks:
                self.notify.info('No more room for buildings, with %s still to assign.' % numToAssign)
                return

            # Now smallestTracks is the list of all tracks with the
            # fewest number of buildings.  (There might be more than
            # one with the same number.)
            buildingTrack = random.choice(smallestTracks)
            buildingTrackIndex = SuitDNA.suitDepts.index(buildingTrack)

            # Do that again, choosing a suitable height.
            smallestCount = None
            smallestHeights = []
            for height in range(5):
                if totalWeightPerHeight[height]:
                    count = float(numPerHeight[height]) / float(SHG.BUILDING_HEIGHT_DISTRIBUTION[height])
                    if (smallestCount is None) or (count < smallestCount):
                        smallestHeights = [height]
                        smallestCount = count
                    elif count == smallestCount:
                        smallestHeights.append(height)

            if not smallestHeights:
                self.notify.info('No more room for buildings, with %s still to assign.' % numToAssign)
                return

            # Remember, buildingHeight is numFloors - 1.
            buildingHeight = random.choice(smallestHeights)
            self.notify.info('Existing buildings are (%s, %s), choosing from (%s, %s), chose %s, %s.' % (self.formatNumSuitsPerTrack(numPerTrack), self.formatNumSuitsPerTrack(numPerHeight), smallestTracks, smallestHeights, buildingTrack, buildingHeight))

            # Look for a suitable street to have this building.
            repeat = True
            zoneId = None
            sp = None
            while repeat and (buildingTrack is not None) and (buildingHeight is not None):
                if not hoodInfo:
                    self.notify.warning(f'No more streets can have suit buildings, with {numToAssign} buildings unassigned!')
                    return

                repeat = False

                currHoodInfo = self.chooseStreetWithPreference(hoodInfo, buildingTrack, buildingHeight)
                spawnDef = currHoodInfo.getCogSpawnDefinition()
                # Get the ClashSuitPlannerAI associated with this zone.
                zoneId = currHoodInfo.getZoneId()
                if zoneId in self.air.suitPlanners:
                    sp = self.air.suitPlanners[zoneId]

                    # How many suit buildings does this zone already have?
                    numTarget = sp.targetNumSuitBuildings
                    numTotalBuildings = len(sp.frontdoorPointList)
                else:
                    # There's no SuitPlanner for this zone.  We must
                    # be running with want-suits-everywhere turned
                    # off.
                    numTarget = 0
                    numTotalBuildings = 0
                if numTarget >= self.branchDef.getMaxCogBuildings() or numTarget >= numTotalBuildings:
                    # This zone has enough buildings.
                    self.notify.info('Zone %s has enough buildings.' % zoneId)
                    hoodInfo.pop(zoneId)
                    weight = currHoodInfo.getBuildingWeight()
                    tracks = spawnDef.getCogTrackChances()
                    heights = currHoodInfo.getBulidingHeights()
                    totalWeight -= weight

                    for dept, trackWeight in tracks.items():
                        totalWeightPerTrack[dept] -= weight * trackWeight

                    for i in range(0, 6):  # we have 6 possible building heights
                        totalWeightPerHeight[i] -= weight * heights[i]

                    if totalWeightPerTrack[buildingTrackIndex] <= 0:
                        # Oops, no more of this building track can be
                        # allocated.
                        buildingTrack = None

                    if totalWeightPerHeight[buildingHeight] <= 0:
                        # Oops, no more of this building height can be
                        # allocated.
                        buildingHeight = None

                    repeat = True

            # Ok, now we've got a randomly-chosen zone that wants a
            # building.  Hand it over.
            if buildingTrack is not None and buildingHeight is not None and sp:
                sp.targetNumSuitBuildings += 1
                sp.pendingBuildingTracks.append(buildingTrack)
                sp.pendingBuildingHeights.append(buildingHeight)
                self.notify.info(f"Assigning building to "
                                 f"zone {zoneId}, "
                                 f"pending tracks = {sp.pendingBuildingTracks}, "
                                 f"pending heights = {sp.pendingBuildingHeights}"
                )
                numPerTrack[buildingTrack] += 1
                numPerHeight[buildingHeight] += 1
                numToAssign -= 1

    def unassignSuitBuildings(self, numToAssign):
        """
        The opposite of assignSuitBuildings(), this removes the
        assignment for the indicated number of buildings.  The
        buildings will remain suit buildings, but when they are
        eventually reclaimed by toons, they will not be replaced by
        more suit buildings.
        This is just called at startup in the case where we have more
        buildings in the world than we actually want to keep.
        """
        # Look for a suitable zone.  First, get a copy of the
        # SuitHoodInfo array, so we can remove elements from it as we
        # discover they're unsuitable.
        hoodInfo = SHG.SuitHoodInfo.copy()
        totalWeight = SHG.TOTAL_BWEIGHT

        # For each building:
        while numToAssign > 0:
            # Look for a suitable street to pull a building from.
            repeat = True
            sp = None
            while repeat:
                if not hoodInfo:
                    self.notify.warning('No more streets can remove suit buildings, with %s buildings too many!' % numToAssign)
                    return

                repeat = 0
                currHoodInfo = self.chooseStreetNoPreference(hoodInfo, totalWeight)

                # Get the ClashSuitPlannerAI associated with this zone.
                zoneId = currHoodInfo.getZoneId()

                if zoneId in self.air.suitPlanners:
                    sp = self.air.suitPlanners[zoneId]

                    # How many suit buildings does this zone already have?
                    numTarget = sp.targetNumSuitBuildings
                else:
                    # There's no SuitPlanner for this zone.  We must
                    # be running with want-suits-everywhere turned
                    # off.
                    numTarget = 0

                if numTarget <= self.branchDef.getMinCogBuildings():
                    self.notify.info(f"Zone {self.zoneId} can't remove any more buildings.")
                    hoodInfo.pop(zoneId)
                    totalWeight -= currHoodInfo.getBuildingWeight()
                    repeat = True

            # Ok, now we've got a randomly-chosen zone that can remove a
            # building.
            self.notify.info(f'Unassigning building from zone {self.zoneId}.')
            if sp:
                sp.targetNumSuitBuildings -= 1
            numToAssign -= 1

    def chooseStreetNoPreference(self, hoodInfo, totalWeight):
        """ Chooses a random street (neighborhood) from the supplied
        SuitHoodInfo list, without preference for any particular track
        or level.  The random decision is weighted based on the
        likelihood of a building appearing in the street at all. """
        c = random.random() * totalWeight

        # Which element does this correspond to?
        t = 0
        for currHoodInfo in hoodInfo:
            t += currHoodInfo.getBuildingWeight()
            if c < t:
                return currHoodInfo

        # This shouldn't be possible!
        self.notify.warning('Weighted random choice failed! Total is %s, chose %s' % (t, c))
        return random.choice(hoodInfo)

    def chooseStreetWithPreference(self, hoodInfo: Dict[int, SHG.SuitBranchDefinition], buildingTrack, buildingHeight):
        """
        As above, but the random decision is weighted based on the
        requested track and building height, so that streets that are
        more likely to have buildings of the indicated track and
        height are more likely to be selected.
        """
        # First, we need to figure the total distribution.
        dist = []
        for branchDef in hoodInfo.values():
            spawnDef = branchDef.getCogSpawnDefinition()
            weight = branchDef.getBuildingWeight()
            trackPercentages = spawnDef.getCogTrackChances()
            thisValue = weight * trackPercentages.get(buildingTrack, 0) * branchDef.getBulidingHeights()[buildingHeight]
            dist.append(thisValue)

        totalWeight = sum(dist)
        # Pick a random number in the range [0, totalWeight]
        c = random.random() * totalWeight

        t = 0
        for i, branchDef in enumerate(list(hoodInfo.values())):
            t += dist[i]
            if c < t:
                return branchDef

        # This shouldn't be possible!
        self.notify.warning('Weighted random choice failed! Total is %s, chose %s' % (t, c))
        return random.choice(list(hoodInfo.values()))

    def chooseSuitLevel(self, levelMin, levelMax, buildingHeight):
        """ Chooses an appropriate suit level, based on the list of
        possible suit levels allowed on this street, for a suit that
        will produce a building     of the requested height. """

        choices = []
        for level in range(levelMin, levelMax + 1):
            maxFloors = ClashSuitBuildingGlobals.getSuitBuildingInfo(level - 1).floors
            # Remember that buildingHeight is numFloors - 1
            if buildingHeight + 1 == maxFloors:
                # This level is allowed.
                choices.append(level)

        return random.choice(choices)

    def initTasks(self):
        """
        this should be called just after creating the
        suit planner in order to set up tasks that will
        update the suit planner occasionally
        """
        self.createInitialSuitBuildings()

        # create a looping task sequence that will occasionally update the
        # suit population in the local neighborhood
        self.__waitForNextUpkeep()

        # create a looping task sequence that will occasionally update the
        # adjustment to the number of suits desired in this hood, this gradually
        # changes over time
        self.__waitForNextAdjust()

    def resyncSuits(self):
        """
        This calls resync() on every suit managed by the planner.
        See the comments in ClashSuitAI.resync().
        """
        for suit in self.suitList:
            suit.resync()

    def flySuits(self):
        """
        This asks all the suits to fly away abruptly.
        """
        # Don't make them fly away if we are in TTC.
        if self.shouldRespectInvasion():
            for suit in self.suitList:
                if suit.isStubborn():
                    return
                if suit.pathState == 1:
                    suit.flyAwayNow()

    def shouldRespectInvasion(self):
        return SHG.isZoneInvasionableAI(self.zoneId, includeEmpty=True)

    def requestBattle(self, zoneId, suit, toonId):
        self.notify.debug('requestBattle() - zone: %s suit: %s toon: %s' % (zoneId, suit.doId, toonId))
        canonicalZoneId = ZoneUtil.getCanonicalZoneId(zoneId)
        if canonicalZoneId not in self.battlePosDict:
            # If the zone doesn't have a battle cell, brush off the toon.
            return 0

        toon = self.air.doId2do.get(toonId)

        # There is a problem of being able to join two battles at once,
        # so check if we are already in a battle first.
        if toon.getBattleId() > 0:
            self.notify.warning(f'{toonId} tried to request a battle when the toon was already in battle')
            return 0

        # Then set our battleID right up here, to lock out any further requests from getting triggered.
        if toon:
            if hasattr(toon, 'doId'):
                toon.b_setBattleId(toonId)

        pos = self.battlePosDict[canonicalZoneId]
        interactivePropTrackBonus = -1

        self.battleMgr.newBattle(
            zoneId, zoneId, pos, suit, toonId, self.__battleFinished,
            4, interactivePropTrackBonus)

        # make sure to pull in any suits currently in this zone into
        # the battle, but only if they are in 'Bellicose' and are
        # ready to enter a battle.  We used to make the non-bellicose
        # suits fly away, but that seems like a mistake, since these
        # suits will be entering a door or already flying away or
        # something else equally harmless.

        for currOther in self.zoneInfo[zoneId]:
            self.notify.debug('Found suit %s in this new battle zone %s' % (currOther.getDoId(), zoneId))
            if currOther != suit:
                if currOther.pathState == 1 and currOther.legType == SuitLeg.TWalk:
                    self.checkForBattle(zoneId, currOther)

        return 1

    def __battleFinished(self, zoneId):
        """
        zoneId, the zone in which the battle exists

        called when a battle in this neighborhood finishes
        """
        # remove any references to this battle from our battle list
        self.notify.debug('DistSuitPlannerAI: battle in zone ' + str(zoneId) + ' finished')
        currBattleIdx = 0
        while currBattleIdx < len(self.battleList):
            currBattle = self.battleList[currBattleIdx]
            if currBattle[0] == zoneId:
                self.notify.debug('DistSuitPlannerAI: battle removed')
                self.battleList.remove(currBattle)
            currBattleIdx = currBattleIdx + 1

    def __suitCanJoinBattle(self, zoneId: int, suit: ClashSuitAI) -> bool:
        """
        Function:    look at a battle in a specific zone and calculate
                     if a suit is able to join the battle based on the
                     various join-chance values specified for this suit
                     planner
        Parameters:  zoneId, the zone in which a battle exists
        Returns:     True if the suit can join, False otherwise
        """
        battle = self.battleMgr.getBattle(zoneId)
        maxSuits = battle.maxSuitsIncludingOverrides
        if len(battle.suits) >= maxSuits:
            return False

        # Can this Suit even join battles?
        if suit.dna.name in SuitBattleGlobals.CANT_JOIN_BATTLES:
            return False

        # First, let's see if the battle has any cogs that would
        # override the chance for a suit to join the battle.
        suitNames = [suit.dna.name for suit in battle.suits]
        checkRatio = -1
        for potentialSuit in SuitBattleGlobals.JOIN_CHANCE_OVERRIDES:
            if potentialSuit in suitNames:
                # Aha, we found a suit with an override.
                # Time to get ratioed.
                checkRatio = max(SuitBattleGlobals.JOIN_CHANCE_OVERRIDES[potentialSuit], checkRatio)
        if checkRatio >= 0:
            return random.randint(0, 99) < checkRatio
        # Check to see if more cogs should join this battle based on
        # the total amount of cogs ever in this battle.
        limit = len(battle.toons) + 1
        if self.zoneId in SHG.ONE_TO_ONE_ZONES:
            limit -= 1
        if battle.numSuitsEver + 1 > limit:
            return False
        if battle:
            # the chance of a suit joining a battle depends on the suit to
            # toon ratio of the battle, once this chance is obtained, the
            # suit randomly decides if it should join, first check to see
            # if we have a config to tell us that suits always join battles
            # with an empty slot
            #
            if ConfigVariableBool('suits-always-join', False).getValue():
                return True
            jChanceList = SHG.SUIT_JOIN_CHANCE
            ratioIdx = (len(battle.toons) - battle.numSuitsEver) + 2
            if ratioIdx >= 0:
                if ratioIdx < len(jChanceList):
                    if random.randint(0, 99) < jChanceList[ratioIdx]:
                        return True
                else:
                    self.notify.warning('__suitCanJoinBattle idx out of range!')
                    return True
        return False

    def checkForBattle(self, zoneId, suit):
        # See if zone has a battle or not
        if self.battleMgr.cellHasBattle(zoneId):
            # If zone has a battle, see if there are any spots in it
            # but first, randomly decide if this suit should even try
            # to join the battle based on the hood's join battle
            # randomness
            if suit.isStubborn():
                # The suit is stubborn, so it will try really hard
                # to join the battle. If the battle manager isn't happy,
                # then the suit will simply ignore the battle entirely.
                if suit.dna.name not in SuitBattleGlobals.CANT_JOIN_BATTLES and self.battleMgr.requestBattleAddSuit(zoneId, suit):
                    return 1
                return 0
            if self.__suitCanJoinBattle(zoneId, suit) and self.battleMgr.requestBattleAddSuit(zoneId, suit):
                # The suit gets added to the battle and the battle
                # takes control
                return 1
            # Make the suit fly away
            suit.flyAwayNow()
            return 1
        else:
            # There is no battle, so continue
            return 0

    def postBattleResumeCheck(self, suit):
        """
        Function:    check to see if a specific suit should, after it
                     gets out of a battle, resume its previous path or
                     if that path is already occupied and the suit
                     should fly away
        Changes:     1 if suit should resume path, 0 to fly away
        """
        self.notify.debug('DistSuitPlannerAI:postBattleResumeCheck: suit ' + str(suit.getDoId()) + ' is leaving battle')
        battleIndex = 0
        for currBattle in self.battleList:
            if suit.zoneId == currBattle[0]:
                self.notify.debug(' battle found' + str(suit.zoneId))
                # now that we found the zone in our list of battles, check
                # the first path to see if there is any intersection between
                # the path and this suit's path, if so, then this suit will
                # probably end up conflicting with a previously resumed suit.
                # So lets tell this suit to fly away
                for currPath in currBattle[1]:
                    for currPathPtSuit in range(suit.currWpt, suit.myPath.getNumPoints()):
                        ptIdx = suit.myPath.getPointIndex(currPathPtSuit)
                        if self.notify.getDebug():
                            self.notify.debug(' comparing' + str(ptIdx) + 'with' + str(currPath))
                        if currPath == ptIdx:
                            if self.notify.getDebug():
                                self.notify.debug(' match found, telling' + 'suit to fly')
                            return 0
            battleIndex += 1

        # battle was not found, so add one to the list and generate a
        # list of indexes which represent each of the next several
        # path points in this suit's path, so any future suit that
        # exits a battle in this zone will compare its path to this
        # path to check for collisions when they disperse and leave
        # the battle
        pointList = []
        for currPathPtSuit in range(suit.currWpt, suit.myPath.getNumPoints()):
            ptIdx = suit.myPath.getPointIndex(currPathPtSuit)
            if self.notify.getDebug():
                self.notify.debug(' appending point with index of' + str(ptIdx))
            pointList.append(ptIdx)

        # add the zone id and the list of indexes
        self.battleList.append([suit.zoneId, pointList])
        return 1

    def zoneChange(self, suit, oldZone, newZone=None):
        """
        Function:    notify the suit planner when a suit changes zones
        Parameters:  suit, the suit that is changing zones
                     oldZone, where the suit was previously
                     newZone, where suit is now, None if suit is bye-bye
        """
        # remove any old reference of the suit from the zones list
        if (oldZone in self.zoneInfo) and (suit in self.zoneInfo[oldZone]):
            self.zoneInfo[oldZone].remove(suit)

        # add the suit to the appropriate zone if one was given
        if newZone is not None:
            if newZone not in self.zoneInfo:
                self.zoneInfo[newZone] = []
            self.zoneInfo[newZone].append(suit)

    def d_setZoneId(self, zoneId):
        self.sendUpdate('setZoneId', [self.getZoneId()])

    def rateLimited(self, avId):
        if avId not in self.ratelimiters:
            self.ratelimiters[avId] = RateLimiter(max_hits=2, period=1)  # 2 requests allowed, since we do both suits and buildings
        ratelimiter = self.ratelimiters.get(avId)
        return ratelimiter.tryRequest()

    def suitListQuery(self):
        avId = self.air.getAvatarIdFromSender()
        if self.rateLimited(avId):
            return

        # just send back a list of suit type indices
        suitIndexList = []
        for suit in self.suitList:
            suitIndexList.append(suit.dna.name)
        self.sendUpdateToAvatarId(avId, 'suitListResponse', [suitIndexList])

    def buildingListQuery(self):
        avId = self.air.getAvatarIdFromSender()
        if self.rateLimited(avId):
            return

        # send back a list of suit buildings in the format:
        #      [numBoard, numCorp, numLegal, numMoney, numSales]
        buildingDict = {}
        self.countNumBuildingsPerTrack(buildingDict)
        buildingList = [0, 0, 0, 0, 0]
        for dept in SuitDNA.suitDepts:
            if dept in buildingDict:
                buildingList[SuitDNA.suitDepts.index(dept)] = buildingDict[dept]
        self.sendUpdateToAvatarId(avId, 'buildingListResponse', [buildingList])

    def pickLevelTypeAndTrack(self, level=None, type=None, track=None, suitName=None):
        """
        Chooses a suitable suit description in terms of its level and
        type numbers, and track letter.  Normally, all three
        parameters are chosen at random, but for special purposes
        (e.g. magic words), one or more may be passed in as non-None.
        """
        # first randomly choose a level from those available for this hood
        if level is None:
            level = random.choice(self.spawnDef.getSuitLevelRange())

        # now randomly choose a type of suit based on the level, any given
        # type of suit can only be one of 5 levels
        if type is None:
            typeMax = self.spawnDef.getMaxSpawnCogType()
            typeChoices = list(range(max(level - 4, 1), min(level, typeMax) + 1))
            if typeChoices:
                if level == 10: # hack, i absolutely need to rework how this spawning tech works but its late at night so i'll do it later
                    typeChoices.append(5)
                type = random.choice(typeChoices)
            else:
                type = typeMax
            if random.random() < (self.spawnDef.getSkelecogSpawnChance() / 100.0):
                self.skeleChance = 1
        if type > SuitDNA.suitsPerDept:
            return level, type, track
        if random.random() <= (self.spawnDef.getExecutiveSpawnChance() / 100.0):
            self.isElite = True
        if suitName and SuitDNA.isAlternate(suitName):
            suitInfo = SuitBattleGlobals.SuitAttributes[suitName]
            suitMinLevel = suitInfo['level'] + 1
            suitMaxLevel = suitMinLevel + len(suitInfo['freq']) - 1
            level = PythonUtil.clampScalar(level, suitMinLevel, suitMaxLevel)
        else:
            if level > 12:
                pass
            else:
                if type == 6:
                    level = min(max(level, type), type + 6)
                elif type == 5:
                    level = min(max(level, type), type + 5)
                else:
                    level = min(max(level, type), type + 4)

        # now randomly choose a suit 'department', or track, or whatever
        # we are calling it.
        if not track:
            track = self.spawnDef.pickRandomCogTrack()

        # then a bit of stupid custom logic for Magnates to spawn in the wide-open pond known as Twilight Terrace
        if (
            self.zoneId == ToontownGlobals.TwilightTerrace
            and track == 'g'
            and level in range(7, 16)  # You never know
            and random.random() < SHG.TWILIGHT_TERRACE_MAGNATE_CHANCE
        ):
            type = 7

        self.notify.debug('pickLevelTypeAndTrack: %s %s %s' % (level, type, track))
        return level, type, track
