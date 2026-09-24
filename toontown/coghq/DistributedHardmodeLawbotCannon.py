from .DistributedLawbotCannon import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedHardmodeLawbotCannon(DistributedLawbotCannon):

    def __init__(self, cr):
        DistributedLawbotCannon.__init__(self, cr)
        self.wantedBossState = 'BattleThree'
