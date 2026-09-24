from .DistributedLawbotCannonAI import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedHardmodeLawbotCannonAI(DistributedLawbotCannonAI):

    def __init__(self, air, lawbotBoss, index, x, y, z, h, p, r):
        DistributedLawbotCannonAI.__init__(self, air, lawbotBoss, index, x, y, z, h, p, r)
        self.wantedBossState = 'BattleThree'
