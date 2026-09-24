from toontown.clashsuit.suit import BossCogGlobals
from toontown.coghq import DistributedCashbotBossCraneAI
from direct.fsm import FSM
from typing import TYPE_CHECKING
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


@DirectNotifyCategory()
class DistributedCashbotBossCraneFastAI(DistributedCashbotBossCraneAI.DistributedCashbotBossCraneAI, FSM.FSM):
    """
    DistributedCashbotBossCraneFastAI(DistributedCashbotBossCraneAI, FSM)

    Controls the smaller cranes that are hypotenuse to the normal cranes.
    """

    def __init__(self, air, boss, index):
        """
        :type air: ToontownAIRepository
        :param boss: The CFO Boss himself
        """
        DistributedCashbotBossCraneAI.DistributedCashbotBossCraneAI.__init__(self, air, boss, index)
        FSM.FSM.__init__(self, 'DistributedCashbotBossCraneFastAI')
        self.craneType = BossCogGlobals.CashbotBossCraneTypeFast  # 1
