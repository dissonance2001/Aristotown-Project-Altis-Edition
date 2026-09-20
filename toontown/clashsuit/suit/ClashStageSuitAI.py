from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.clashsuit.suit import ClashFactorySuitAI



@DirectNotifyCategory()
class ClashStageSuitAI(ClashFactorySuitAI.ClashFactorySuitAI):
    

    def isForeman(self):
        return 0

    def isSupervisor(self):
        return 0

    def isClerk(self):
        return self.boss

    def isVirtual(self):
        return self.virtual
