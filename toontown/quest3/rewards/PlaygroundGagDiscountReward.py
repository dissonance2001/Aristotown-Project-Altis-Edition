"""
Playground gag discount reward class for quests.
"""
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.QuestLocalizer import RWD_PGDiscount
from toontown.quest3.base.QuestReward import QuestReward
from toontown.quest3.base.Quester import Quester
from toontown.quest3.kudos import KudosConstants
from toontown.toonbase import TTLocalizer


class PlaygroundGagDiscountReward(QuestReward):

    def __init__(self, zoneId: int, amount: float):
        self.zoneId = zoneId
        self.amount = amount

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        if quester.questerType == QuesterType.Toon:
            quester.updatePlaygroundGagDiscount(self.zoneId, self.amount)
            # quester.queueScavenge(1, ScavengeType.KudosPGGagDiscount, [self.zoneId, self.amount])

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [RWD_PGDiscount % (self.getDisplayAmount(), TTLocalizer.ShorthandPlaygroundNames[self.zoneId])]

    def getDisplayAmount(self):
        return int(100 - (KudosConstants.getPlaygroundDiscountAmount(self.amount) * 100))

    def __repr__(self):
        return f'PlaygroundGagDiscountReward({self.zoneId}, {self.amount})'
