from toontown.clashbattle.battle.distributed import DistributedBattleFinalAI


class DistributedBattleVirtualAI(DistributedBattleFinalAI.DistributedBattleFinalAI):
    def __init__(self, air, bossCog, roundCallback, finishCallback, battleSide):
        DistributedBattleFinalAI.DistributedBattleFinalAI.__init__(self, air, bossCog, roundCallback, finishCallback, battleSide)
