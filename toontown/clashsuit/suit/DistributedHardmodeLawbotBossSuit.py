from .DistributedLawbotBossSuit import *


class DistributedHardmodeLawbotBossSuit(DistributedLawbotBossSuit):

    def __init__(self, cr):
        DistributedLawbotBossSuit.__init__(self, cr)
        self.cannonBossState = 'BattleThree'
