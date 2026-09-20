from toontown.clashbattle.battle.distributed import ClashBattleFinalAI


class DistributedBattleVirtualAI(ClashBattleFinalAI.ClashBattleFinalAI):
    def __init__(self, air, bossCog, roundCallback, finishCallback, battleSide):
        ClashBattleFinalAI.ClashBattleFinalAI.__init__(self, air, bossCog, roundCallback, finishCallback, battleSide)
