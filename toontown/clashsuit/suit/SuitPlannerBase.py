""" SuitPlannerBase module:  contains common code that both the server
    and client use when managing a collection of suits."""

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.hood import ZoneUtil, HoodUtil
from toontown.battle import BattleGlobals
from toontown.suit.SuitHoodGlobals import *
from toontown.dna.DNAParser import DNASuitPoint, DNAStorage, DNAInteractiveProp, loadDNAFileAI



@DirectNotifyCategory()
class SuitPlannerBase:
    """
    Manages all suits which exist within a single neighborhood (or street), this base version contains general code that
    both the server and client can use, such as path generation code, dna storage, path point type storage
    """
    

    def __init__(self):
        # initialize some values that we will be using
        self.suitWalkSpeed = ToontownGlobals.SuitWalkSpeed
        # now load up the dna file for the neighborhood that this suit
        # planner is created for
        self.dnaStore = None
        # keep a map of point indexes and the actual point so when
        # suits need to look up information from a point's index, they
        # can do it quickly without having to ask the dnaStore
        self.pointIndexes = {}
        self.battlePosDict = {}
        self.cellToGagBonusDict = {}
        self.streetPointList = []
        self.frontdoorPointList = []
        self.sidedoorPointList = []
        self.cogHQDoorPointList = []
        self.zoneId = 0

    def delete(self):
        del self.dnaStore

    def setupDNA(self):
        """
        Load up DNA information for the neighborhood that this suit planner is in control of. The DNA contains suit path
        information as well as visgroup (zone) information

        :todo this really should be inside __init__?
        """

        if self.dnaStore:
            return

        self.dnaStore = DNAStorage()
        loadDNAFileAI(self.dnaStore, self.genDNAFileName())
        # now create vis group (zone) information
        self.initDNAInfo()

    def genDNAFileName(self):
        """
        Determines the name of the DNA file that should be loaded for the neighborhood that this suit planner manages
        """
        zoneId = ZoneUtil.getCanonicalZoneId(self.getZoneId())
        hoodId = ZoneUtil.getCanonicalHoodId(zoneId)
        hood = ToontownGlobals.dnaMap[hoodId]
        phase = ToontownGlobals.streetPhaseMap[hoodId]
        if hoodId == zoneId:
            zoneId = 'sz'
        if zoneId == 20000:
            phase = 4
        return 'phase_%s/dna/%s_%s.pdna' % (phase, hood, zoneId)

    def getZoneId(self):
        """
        Intended to be overridden by any inheriting suit planner class, and that class should be a distributed object or
        at least have an attribute named 'zoneId'

        :todo Nobody actually overrides this
        """
        return self.zoneId

    def setZoneId(self, zoneId):
        self.notify.debug('setting zone id for suit planner')
        self.zoneId = zoneId
        self.setupDNA()

    @staticmethod
    def extractGroupName(groupFullName):
        # The Idea here is that group names may have extra flags associated
        # with them that tell more information about what is special about
        # the particular vis zone. A normal vis zone might just be "13001",
        # but a special one might be "14356:safe_zone" or
        # "345:safe_zone:exit_zone"... These are hypotheticals. The main
        # idea is that there are colon separated flags after the initial
        # zone name.
        return groupFullName.split(':', 1)[0]

    def initDNAInfo(self):
        """
        load up vis group information into a dictionary copied from HoodMgr.py

        :todo should be part of __init__?
        """
        numGraphs = self.dnaStore.discoverContinuity()
        if numGraphs != 1:
            self.notify.info('zone %s has %s disconnected suit paths.' % (self.zoneId, numGraphs))

        # Construct a dictionary of zone ids to battle cell center points
        self.battlePosDict = {}
        self.cellToGagBonusDict = {}
        for i in range(self.dnaStore.getNumDNAVisGroupsAI()):
            vg = self.dnaStore.getDNAVisGroupAI(i)
            zoneId = int(self.extractGroupName(vg.getName()))
            # There is only 1 battle cell per zone
            if vg.getNumBattleCells() == 1:
                self.battlePosDict[zoneId] = vg.getBattleCell(0).getPos()
            elif vg.getNumBattleCells() > 1:
                self.notify.warning('multiple battle cells for zone: %d' % zoneId)
                # Just pick the first one
                self.battlePosDict[zoneId] = vg.getBattleCell(0).getPos()
                
            if True:
                # lets find the interactive props connected to this battle cell
                for i in range(vg.getNumChildren()):
                    childDnaGroup = vg.at(i)
                    if isinstance(childDnaGroup, DNAInteractiveProp):
                        self.notify.debug('got interactive prop %s' % childDnaGroup)
                        battleCellId = childDnaGroup.getCellId()
                        if battleCellId == -1:
                            self.notify.warning('interactive prop %s  at %s not associated with a a battle' % (childDnaGroup, zoneId))
                        elif battleCellId == 0:
                            if zoneId in self.cellToGagBonusDict:
                                self.notify.error('FIXME battle cell at zone %s has two props %s %s linked to it' % (zoneId, self.cellToGagBonusDict[zoneId], childDnaGroup))
                            else:
                                # based on the name of the prop, figure out which gag track bonus
                                name = childDnaGroup.getName()
                                propType = HoodUtil.calcPropType(name)
                                if propType in BattleGlobals.PropTypeToTrackBonus:
                                    trackBonus = BattleGlobals.PropTypeToTrackBonus[propType]
                                    self.cellToGagBonusDict[zoneId] = trackBonus

        # Now that we have extracted the vis groups we do not need
        # the dnaStore to keep them around
        self.dnaStore.resetDNAGroups()
        self.dnaStore.resetDNAVisGroups()
        self.dnaStore.resetDNAVisGroupsAI()

        # now load up the suit path points, separate them into types
        self.streetPointList = []
        self.frontdoorPointList = []
        self.sidedoorPointList = []
        self.cogHQDoorPointList = []

        numPoints = self.dnaStore.getNumSuitPoints()
        for i in range(numPoints):
            point = self.dnaStore.getSuitPointAtIndex(i)
            if point.getPointType() == DNASuitPoint.FRONT_DOOR_POINT:
                self.frontdoorPointList.append(point)
            elif point.getPointType() == DNASuitPoint.SIDE_DOOR_POINT:
                self.sidedoorPointList.append(point)
            elif (point.getPointType() == DNASuitPoint.COGHQ_IN_POINT) or (point.getPointType() == DNASuitPoint.COGHQ_OUT_POINT):
                self.cogHQDoorPointList.append(point)
            else:
                self.streetPointList.append(point)
            self.pointIndexes[point.getIndex()] = point

    def genPath(self, startPoint, endPoint, minPathLen, maxPathLen):
        return self.dnaStore.getSuitPath(startPoint, endPoint, minPathLen, maxPathLen)
