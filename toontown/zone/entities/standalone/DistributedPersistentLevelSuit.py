import time

from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.fsm.FSM import FSM

from toontown.suit import SuitTimings
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.suit.DistributedSuitBase import DistributedSuitBase
from toontown.suit.SuitGlobals import SuitSpawnMethod, SpawnMethodToTiming
from toontown.toonbase import ToontownGlobals
from toontown.distributed.DelayDeletable import DelayDeletable


@DirectNotifyCategory()
class DistributedPersistentLevelSuit(DistributedSuitBase, FSM, DelayDeletable):
    defaultTransitions = {
        "Off": ["Walk", "FlyIn", "FlyAway", "Battle", "WalkToBuilding", "DanceThenFlyAway"],
        "Walk": ["WaitForBattle", "Battle", "FlyAway", "WalkToBuilding"],
        "Battle": ["Walk", "WaitForBattle", "Victory", "DanceThenFlyAway"],
        "Victory": ["Off", "FlyAway"],
        "FlyIn": ["Walk", "FlyAway"],
        "WaitForBattle": ["Battle"],
        # These states will be called down from the AI, and may need to be stored until
        # the path is finalized before they can go off.
        "FlyAway": ["Off"],
        "DanceThenFlyAway": ["Off"],
        "WalkToBuilding": ["Off"],
    }

    def __init__(self, cr):
        try:
            self.DistributedSuit_initialized
            return
        except:
            self.DistributedSuit_initialized = 1

        DistributedSuitBase.__init__(self, cr)
        FSM.__init__(self, self.__class__.__name__)
        self.needStateTransition = None
        # Store when special state transitions were requested to happen
        self.stateTransitionTimestamp = 0
        self.walkTrack = None
        self.walkTrackStartT = 0
        self.stateTrack = None
        self.stateTrackStartT = 0
        self.levelRequest = None
        self.persistentLevel = None
        self.doorId = None
        self.doorRequest = None
        self.pathIsReady = False
        # This only matters if the client physically sees this suit spawn.
        self.firstWalkDone = True
        self.spawnPoint = None
        self.spawnPathCollection = None
        self.spawnPointId = None
        self.spawnPathCollectionId = None
        self.spawnMethod = None
        self.spawnTimestamp = 0
        self.currentPathPoint = None
        self.spawnMethodDict = {
            SuitSpawnMethod.FlyIn: self.__handleFlyIn,
        }
        self.request("Off")

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedSuitBase.generate(self)

    def enterOff(self, *args):
        self.hideNametag3d()
        if not self.subclassManagesParent():
            self.setParent(ToontownGlobals.SPHidden)

    def exitOff(self):
        if not self.subclassManagesParent():
            self.setParent(ToontownGlobals.SPRender)
        self.showNametag3d()
        self.loop('neutral', 0)

    def setLevelDoId(self, levelDoId):
        self.notify.debug('setLevelDoId(%s)' % levelDoId)
        self.levelDoId = levelDoId

    def denyBattle(self):
        self.notify.warning('denyBattle()')
        place = self.cr.playGame.getPlace()
        if place.getCurrentOrNextState() == 'WaitForBattle':
            place.setState('Walk')

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        self.notify.debug('announceGenerate %s' % self.doId)

        def onLevelGenerate(levelList, self=self):
            self.persistentLevel = levelList[0]
            totalGenerated = 0

            def onEntityReady(self=self):
                self.notify.debug('level ready, set paths')
                nonlocal totalGenerated
                totalGenerated += 1
                if totalGenerated >= 2:
                    self.spawnPoint = self.persistentLevel.getEntity(self.spawnPointId)
                    self.spawnPathCollection = self.persistentLevel.getEntity(self.spawnPathCollectionId)
                    self.spawnPathCollection.activeSuits.append(self)

                    # Make sure all suit points are ready before continuing
                    if self.spawnPathCollection.allPointsReady:
                        self.spawnPointsReady()
                    else:
                        self.acceptOnce(self.spawnPathCollection.getAllPointsReadyEvent(), self.spawnPointsReady)

                self.levelRequest = None
                return

            self.persistentLevel.setEntityCreateCallback(self.spawnPathCollectionId, onEntityReady)
            self.persistentLevel.setEntityCreateCallback(self.spawnPointId, onEntityReady)

        self.levelRequest = self.cr.relatedObjectMgr.requestObjects([self.levelDoId], onLevelGenerate)
        DistributedSuitBase.announceGenerate(self)

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        self.ignoreAll()
        if self.levelRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.levelRequest)
            self.levelRequest = None
        self.notify.debug('DistributedSuit %d: disabling' % self.getDoId())
        self.setState('Off')
        if self.walkTrack:
            self.walkTrack.pause()
            self.walkTrack = None
        if self.stateTrack:
            self.stateTrack.pause()
            self.stateTrack = None
        DistributedSuitBase.disable(self)

    def delete(self):
        try:
            self.DistributedSuit_deleted
            return
        except:
            self.DistributedSuit_deleted = 1

        self.notify.debug('DistributedSuit %d: deleting' % self.getDoId())
        FSM.cleanup(self)
        DistributedSuitBase.delete(self)

    def initializeBodyCollisions(self, collIdStr):
        """
        Tiny hack, since suits that are already
        available in a level before a toon enters
        the zone will not have battle collisions set up.
        """
        DistributedSuitBase.initializeBodyCollisions(self, collIdStr)
        if self.getCurrentOrNextState() == 'Walk':
            self.enableBattleDetect('walk', self.__handleToonCollision)

    def d_requestBattle(self, pos, hpr):
        self.cr.playGame.getPlace().setState('WaitForBattle')
        self.persistentLevel.lockVisibility(zoneNum=self.persistentLevel.getEntityZoneEntId(self.spawnPathCollection.parentEntId))
        self.sendUpdate('requestBattle', [pos[0], pos[1], pos[2], hpr[0], hpr[1], hpr[2]])

    def handleBattleBlockerCollision(self):
        self.__handleToonCollision(None)

    def __handleToonCollision(self, collEntry):
        if collEntry:
            if collEntry.getFromNodePath().getParent().getKey() != localAvatar.getKey():
                return

        if not base.localAvatar.wantBattles:
            return
        if base.localAvatar.isStunned:
            # Local avatar may be "stunned" as they receive i-frames after exiting a cog building
            return

        toonId = base.localAvatar.getDoId()
        self.notify.debug('Distributed suit %d: requesting a Battle with toon: %d' % (self.doId, toonId))
        self.d_requestBattle(self.getPos(), self.getHpr())
        self.setState('WaitForBattle')

    def getTimeSinceSpawn(self):
        return time.time() - self.spawnTimestamp

    def getSpawnFunc(self):
        return self.spawnMethodDict[self.spawnMethod]

    def spawnPointsReady(self):
        self.pathIsReady = True
        self.currentPathPoint = self.spawnPoint

        # We may have stored a state transition from before this Suit was fully ready
        # We can go ahead and do that now instead of whatever else
        if self.needStateTransition is not None:
            self.setState(self.needStateTransition)
            self.needStateTransition = None
            return

        timeDiff = self.getTimeSinceSpawn()
        if timeDiff < 0:
            # We're still in our spawn, let's go and do that
            self.getSpawnFunc()()
        else:
            # We've passed our spawn time, let's move straight to our path movement
            self.setPath()

    def __handleFlyIn(self):
        # Mark the first walk as not done
        # This will make sure the suit ignores it's first "resync"
        # of the walk cycle, as it is unnecessary and we can do it later
        self.firstWalkDone = False
        self.reparentTo(render)
        timeDiff = self.getTimeSinceSpawn()
        self.stateTrack = self.getFlyInTrack()
        # Time Diff will be a negative here as they *technically* haven't
        # spawned and started walking yet
        self.stateTrackStartT = self.stateTrack.getDuration() + timeDiff
        self.setState("FlyIn")

    def getFlyInTrack(self):
        def suitHeadsUp():
            nextPathId = self.currentPathPoint.pointsTo
            if nextPathId == 0:
                self.headsUp(self.spawnPoint.getPos(render))
            else:
                nextPath = self.persistentLevel.getEntity(nextPathId)
                self.headsUp(nextPath.getPos(render))

        pointPos = self.currentPathPoint.getPos(render)

        return Sequence(
            Func(self.reparentTo, render),
            Func(self.setPos, pointPos),
            Parallel(
                self.beginSupaFlyMove(pointPos, 1, 'flyIn'),
                Func(suitHeadsUp),
            ),
            Func(self.setPath),
        )

    def enterFlyIn(self):
        self.stateTrack.start(self.stateTrackStartT)

    def exitFlyIn(self):
        if self.stateTrack:
            self.stateTrack.pause()
            self.stateTrack = None
        self.loop('neutral')

    def getWalkTrack(self):
        return Sequence(self.spawnPathCollection.getWalkTrack(self), Func(self.doNextPathPoint))

    def doNextPathPoint(self):
        if self.walkTrack:
            self.walkTrack.pause()
        self.walkTrack = self.getWalkTrack()
        self.walkTrack.start()

    def getPointAndLeftoverBasedOnTime(self):
        # We have no place to go, we haven't moved.
        if self.spawnPathCollection.pathCompletionTime <= 0:
            return self.spawnPoint, 0.0

        currPoint = self.spawnPoint

        # Get the amount of time that has happened since they spawned
        timeDiff = self.getTimeSinceSpawn()
        # Time difference may be eeeever so slightly below 0 if we're coming out of a spawn.
        # We can go ahead and fix that.
        timeDiff = max(timeDiff, 0)
        if timeDiff <= 0:
            return currPoint, 0.0

        leftover = timeDiff % self.spawnPathCollection.pathCompletionTime

        # Do some course correction, this suit may have spawned a long time ago
        while leftover > 0:
            nextPathId = currPoint.pointsTo
            if nextPathId == 0:
                break

            walkTime = self.spawnPathCollection.pointToWalkTime[currPoint.entId]
            leftover -= walkTime
            if leftover <= 0:
                return currPoint, leftover
            else:
                # Leftover is greater than zero, so they still have an amount to walk.
                # We're done if its less than zero.
                currPoint = self.persistentLevel.getEntity(nextPathId)

        # Leftover will either be zero or a negative number.
        # If zero, their current point is fine and we can continue onwards.
        # If it's negative, then that value indicates how much time
        # we have towards the next path point
        return currPoint, leftover

    def setPath(self):
        # Correct their current position based on timestamp.
        self.currentPathPoint, leftover = self.getPointAndLeftoverBasedOnTime()
        self.walkTrack = self.getWalkTrack()

        if leftover == 0:
            # If the cog's time difference was already on-track, we don't need to adjust anything.
            self.walkTrackStartT = 0
        else:
            # Else, we're gonna have a negative leftover value that indicates
            # how close to the end of the current path they are.
            self.setPos(self.spawnPathCollection.getSuitPosOnPath(self))
        self.setState('Walk')
        self.reparentTo(render)

    def subclassManagesParent(self):
        return 0

    def enterWalk(self, ts=0):
        self.enableBattleDetect('walk', self.__handleToonCollision)
        self.walkTrack.start(self.walkTrackStartT)
        self.loop('walk')

    def exitWalk(self):
        self.disableBattleDetect()
        if self.walkTrack:
            self.walkTrack.pause()
            self.walkTrack = None
        self.loop('neutral')

    def resumePath(self, state):
        self.setState('Walk')

    def setActive(self, active):
        if active:
            self.setState('Walk')
        else:
            self.setState('Off')

    def disableBodyCollisions(self):
        self.disableBattleDetect()
        self.enableRaycast(0)
        if self.cRayNodePath:
            self.cRayNodePath.removeNode()
        if hasattr(self, 'cRayNode'):
            del self.cRayNode
        if hasattr(self, 'cRay'):
            del self.cRay
        if hasattr(self, 'lifter'):
            del self.lifter

    def removeCollisions(self):
        self.enableRaycast(0)
        self.cRay = None
        self.cRayNode = None
        self.cRayNodePath = None
        self.lifter = None
        self.cTrav = None
        return

    def setVirtual(self, isVirtual=1):
        self.virtual = isVirtual
        if self.virtual:
            actorNode = self.find('**/__Actor_modelRoot')
            actorCollection = actorNode.findAllMatches('*')
            for thing in actorCollection:
                if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
                    thing.setColorScale(1.0, 0.0, 0.0, 1.0)
                    thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                    thing.setDepthWrite(False)
                    thing.setBin('fixed', 1)

    def getVirtual(self):
        return self.virtual

    def setSpawnInformation(self, spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp):
        self.spawnPointId, self.spawnPathCollectionId, self.spawnMethod, self.spawnTimestamp = spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp

    def beginFlyAway(self, timestamp):
        # If path is ready, move to this state now
        # If it's not, then we can just wait until the path is ready.
        self.stateTransitionTimestamp = timestamp
        if self.pathIsReady:
            self.setState("FlyAway")
        else:
            self.needStateTransition = "FlyAway"

    def enterFlyAway(self):
        if self.stateTrack:
            self.stateTrack.finish()
            self.stateTrack = None

        self.reparentTo(render)
        suitPos = self.spawnPathCollection.getSuitPosOnPath(self)
        self.setPos(suitPos)
        nextPathId = self.currentPathPoint.pointsTo
        if nextPathId == 0:
            self.headsUp(self.spawnPoint.getPos(render))
        else:
            nextPath = self.persistentLevel.getEntity(nextPathId)
            self.headsUp(nextPath.getPos(render))

        self.stateTrack = Sequence(
            self.beginSupaFlyMove(suitPos, 0, 'flyAway'),
            Func(self.setState, "Off"),
        )

        timeDiff = time.time() - self.stateTransitionTimestamp
        self.stateTrack.start(timeDiff)

    def exitFlyAway(self):
        if self.stateTrack:
            self.stateTrack.finish()
            self.stateTrack = None

    def beginDanceThenFlyAway(self, timestamp):
        # If path is ready, move to this state now
        # If it's not, then we can just wait until the path is ready.
        self.stateTransitionTimestamp = timestamp
        if self.pathIsReady:
            self.setState("DanceThenFlyAway")
        else:
            self.needStateTransition = "DanceThenFlyAway"

    def enterDanceThenFlyAway(self):
        if self.stateTrack:
            self.stateTrack.finish()
            self.stateTrack = None

        self.wrtReparentTo(render)

        self.stateTrack = Sequence(
            self.actorInterval('victory'),
            self.beginSupaFlyMove(Point3(0, 0, 0), 0, 'flyAway', flyOutBasedOnCurrentPos=True),
            Func(self.setState, "Off"),
        )

        timeDiff = time.time() - self.stateTransitionTimestamp
        self.stateTrack.start(timeDiff)

    def exitDanceThenFlyAway(self):
        if self.stateTrack:
            self.stateTrack.finish()
            self.stateTrack = None

    def beginTakeOverBuilding(self, doorId, timestamp):
        self.doorId = doorId
        # If path is ready, move to this state now
        # If it's not, then we can just wait until the path is ready.
        self.stateTransitionTimestamp = timestamp
        if self.pathIsReady:
            self.setState("WalkToBuilding")
        else:
            self.needStateTransition = "WalkToBuilding"

    def enterWalkToBuilding(self):
        if self.stateTrack:
            self.stateTrack.finish()
            self.stateTrack = None

        self.reparentTo(render)
        suitPos = self.spawnPathCollection.getSuitPosOnPath(self, timestamp=self.stateTransitionTimestamp)
        self.setPos(suitPos)
        self.loop('neutral')

        def onDoorGenerate(doorList):
            door = doorList[0]
            self.doorRequest = None

            doorNode = door.getDoorNodePath()
            temp = doorNode.attachNewNode('foo')
            temp.setPos(door.doorX, -5.0, ToontownGlobals.FloorOffset)
            doorPos = temp.getPos(render)
            doorDist = Vec3(self.getPos(render) - doorPos).length()
            temp.removeNode()
            maxTime = SuitTimings.LevelSuitTakeoverBuildingWalkTime
            walkTime = min(doorDist / ToontownGlobals.SuitWalkSpeed, maxTime)

            self.stateTrack = Sequence(
                Func(self.headsUp, doorNode),
                Wait(max(maxTime - walkTime, 0)),
                Func(self.loop, 'walk'),
                LerpPosInterval(self, walkTime, doorPos),
                # Cog begins walking into door at this time, handled by server
                Wait(4.0),
                Func(self.setState, "Off"),
            )

            timeDiff = time.time() - self.stateTransitionTimestamp
            self.stateTrack.start(timeDiff)

        self.doorRequest = self.cr.relatedObjectMgr.requestObjects([self.doorId], onDoorGenerate)

    def exitWalkToBuilding(self):
        if self.doorRequest:
            self.cr.relatedObjectMgr.abortRequest(self.doorRequest)
            self.doorRequest = None
        if self.stateTrack:
            self.stateTrack.finish()
            self.stateTrack = None
