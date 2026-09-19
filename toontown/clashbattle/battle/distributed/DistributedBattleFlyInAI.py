from toontown.battle.distributed import DistributedBattleFinalAI


class DistributedBattleFlyInAI(DistributedBattleFinalAI.DistributedBattleFinalAI):
    def __init__(self, air, bossCog, roundCallback, finishCallback, battleSide):
        DistributedBattleFinalAI.DistributedBattleFinalAI.__init__(self, air, bossCog, roundCallback, finishCallback, battleSide)
