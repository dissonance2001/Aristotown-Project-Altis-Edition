from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.clashsuit.suit import DistributedFactorySuitAI



@DirectNotifyCategory()
class DistributedStageSuitAI(DistributedFactorySuitAI.DistributedFactorySuitAI):
    

    def isForeman(self):
        return 0

    def isSupervisor(self):
        return 0

    def isClerk(self):
        return self.boss

    def isVirtual(self):
        return self.virtual
