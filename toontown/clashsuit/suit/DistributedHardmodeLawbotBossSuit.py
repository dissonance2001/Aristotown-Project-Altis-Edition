from .ClashLawbotBossSuit import *


class DistributedHardmodeLawbotBossSuit(ClashLawbotBossSuit):

    def __init__(self, cr):
        ClashLawbotBossSuit.__init__(self, cr)
        self.cannonBossState = 'BattleThree'
