"""
Antlers reward class for quests.
"""
import time
from enum import IntEnum

from toontown.inventory.base.Inventory import Inventory
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.QuestLocalizer import RWD_Antlers
from toontown.quest3.base.QuestReward import QuestReward
from toontown.toonbase import ToontownGlobals
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.toon.DistributedToonAI import DistributedToonAI


class AntlersReward(QuestReward):

    def __init__(self, itemId: IntEnum):
        self.itemId = itemId

    def handleReward(self, quester, multiplier: float = 1.0) -> None:
        """:type quester: DistributedToonAI"""
        if quester.questerType == QuesterType.Toon:
            if quester.dna.head[0] == 'x':
                if 1 not in quester.animalEffects:
                    quester.giveAnimalEffect(1)

            hs: Inventory = quester.getHammerspace()
            if hs:
                hs.addItem(self.itemId)

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [RWD_Antlers]

    def __repr__(self):
        return f'AntlersReward({self.itemId})'
