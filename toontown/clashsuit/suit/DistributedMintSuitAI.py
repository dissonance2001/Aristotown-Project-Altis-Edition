from toontown.suit import DistributedFactorySuitAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedMintSuitAI(DistributedFactorySuitAI.DistributedFactorySuitAI):
    

    def isForeman(self):
        return 0

    def isSupervisor(self):
        return self.boss

    def isVirtual(self):
        return 0
