from toontown.building.ElevatorConstants import *
from toontown.building import DistributedBossElevatorAI
from toontown.suit import BossSelectionGlobals


class DistributedVPElevatorAI(DistributedBossElevatorAI.DistributedBossElevatorAI):

    def __init__(self, air, bldg, zone, antiShuffle = 0, minLaff = 0):
        self.bossType = BossSelectionGlobals.DEFAULT_SELLBOT_BOSS
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=minLaff)
        self.type = ELEVATOR_VP
        self.countdownTime = ElevatorData[self.type]['countdown']

    # ---- boss selection ----
    def getBossType(self):
        return self.bossType

    def d_setBossType(self, bossType):
        self.sendUpdate('setBossType', [bossType])

    def b_setBossType(self, bossType):
        self.bossType = bossType
        self.d_setBossType(bossType)

    def getBossOptions(self):
        getter = getattr(self.bldg, 'getBossOptions', None)
        return getter() if getter else []

    def getBossTypeForTrip(self):
        if self.bossType in self.getBossOptions():
            return self.bossType
        return None

    def getLeaderAvId(self):
        """The first toon aboard (lowest occupied seat) picks the boss."""
        for avId in self.seats:
            if avId:
                return avId
        return None

    def requestBossType(self, bossType):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.seats:
            self.notify.warning('avId %s requested boss type %s without being aboard' % (avId, bossType))
            return
        if avId != self.getLeaderAvId():
            return
        if bossType not in self.getBossOptions():
            self.notify.warning('avId %s requested invalid boss type %s' % (avId, bossType))
            return
        if self.fsm.getCurrentState().getName() not in ('waitEmpty', 'waitCountdown'):
            return
        if bossType != self.bossType:
            self.b_setBossType(bossType)

    def enterWaitEmpty(self):
        DistributedBossElevatorAI.DistributedBossElevatorAI.enterWaitEmpty(self)
        # Nobody aboard anymore: the next group starts from the default boss.
        if self.bossType != BossSelectionGlobals.DEFAULT_SELLBOT_BOSS:
            self.b_setBossType(BossSelectionGlobals.DEFAULT_SELLBOT_BOSS)
