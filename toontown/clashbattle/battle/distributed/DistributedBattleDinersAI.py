from toontown.clashbattle.battle.BattleGlobals import BattleStateEnum
from toontown.clashbattle.battle.distributed import DistributedBattleFinalAI


class DistributedBattleDinersAI(DistributedBattleFinalAI.DistributedBattleFinalAI):
    def __init__(self, air, bossCog, roundCallback, finishCallback, battleSide):
        DistributedBattleFinalAI.DistributedBattleFinalAI.__init__(self, air, bossCog, roundCallback, finishCallback, battleSide)

    def startBattle(self, toonIds, suits):
        self.joinable = True
        for toonId in toonIds:
            toon = self.air.doId2do.get(toonId)
            if self.addToon(toonId) and toon:
                toon.setBattleState(BattleStateEnum.ACTIVE)

        # We have to be sure to tell the players that they're active
        # before we start adding suits.
        self.d_setMembers()

        for suit in suits:
            suit.setBattleState(BattleStateEnum.PENDING)

        self.d_setMembers()
        self.b_setState('ReservesJoining')
        self.waitForReservesJoining()
