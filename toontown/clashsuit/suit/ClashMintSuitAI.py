from toontown.clashsuit.suit import ClashFactorySuitAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ClashMintSuitAI(ClashFactorySuitAI.ClashFactorySuitAI):
    

    def isForeman(self):
        return 0

    def isSupervisor(self):
        return self.boss

    def isVirtual(self):
        return 0
