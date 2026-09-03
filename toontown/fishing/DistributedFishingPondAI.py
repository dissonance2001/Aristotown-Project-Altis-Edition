from direct.distributed.DistributedObjectAI import DistributedObjectAI
from toontown.fishing import FishingTargetGlobals
from toontown.fishing.DistributedFishingTargetAI import DistributedFishingTargetAI
from toontown.fishing.DistributedPondBingoManagerAI import DistributedPondBingoManagerAI
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedFishingPondAI(DistributedObjectAI):
    """
    DistributedFishingPondAI(DistributedObjectAI)
    """

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

        self.area = None
        self.targets = {}
        self.spots = {}
        self.bingoMgr = None

    def delete(self):
        # ensure we are all deleted and stuffs
        # first, ignore all the things
        self.ignoreAll()
        # next, the bingoMgr
        if self.bingoMgr:
            self.bingoMgr.requestDelete()
            self.bingoMgr = None
        # now, the fish targets
        self.targets = {}
        # don't forget dem fishing spots
        self.spots = {}
        # finally, the area
        self.area = None
        # and let the superclass do their own stuff
        DistributedObjectAI.delete(self)

    def start(self):
        # if self.air.holidayManager.isHolidayRunning(ToontownGlobals.WEALTHY_WEDNESDAY) or \
        #         self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_SATURDAY_WEALTHY):
        #     self.startBingo()
        #
        # self.accept('startBingo', self.startBingo)
        # self.accept('stopBingo', self.stopBingo)
        self.startBingo()
        for _ in range(FishingTargetGlobals.getNumTargets(self.area)):
            fishingTarget = DistributedFishingTargetAI(simbase.air)
            fishingTarget.setPondDoId(self.doId)
            fishingTarget.generateWithRequired(self.zoneId)

    def startBingo(self):
        if self.bingoMgr:
            self.notify.warning('Bingo manager failed to generate, already exists on pond id %s!' % self.doId)
            return

        self.bingoMgr = DistributedPondBingoManagerAI(self.air)
        self.bingoMgr.setPondDoId(self.doId)
        self.bingoMgr.generateWithRequired(self.zoneId)
        self.bingoMgr.enableBingo()
        self.bingoMgr.d_enableBingo()

    def stopBingo(self):
        if not self.bingoMgr:
            self.notify.warning('Bingo manager was requested to stop, but it never begun on pond id %s!' % self.doId)
            return

        self.bingoMgr.requestDelete()
        self.bingoMgr = None

    def hitTarget(self, target):
        avId = self.air.getAvatarIdFromSender()
        # See if the target bites
        if self.targets.get(target) is None:
            self.air.writeServerEvent('suspicious', avId, 'Toon tried to hit nonexistent fishing target!')
            return

        # You must be fishing at a spot to hit a target
        spot = self.hasToon(avId)
        if spot:
            spot.rewardIfValid(target)
            return
        self.air.writeServerEvent('suspicious', avId, 'Toon tried to catch fish while not fishing!')

    def addTarget(self, target):
        self.targets[target.doId] = target

    def addSpot(self, spot):
        self.spots[spot.doId] = spot

    def setArea(self, area):
        self.area = area

    def getArea(self):
        return self.area

    def hasToon(self, avId):
        for spot in self.spots:
            if self.spots[spot].avId == avId:
                return self.spots[spot]
