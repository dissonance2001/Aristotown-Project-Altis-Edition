"""
Playground gag multiplier reward class for quests.
"""
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.QuestLocalizer import RWD_PGMult
from toontown.quest3.base.QuestReward import QuestReward
from toontown.quest3.base.Quester import Quester
from toontown.toonbase import TTLocalizer, ToontownGlobals


class PlaygroundGagMultiplierReward(QuestReward):
    def __init__(self, zoneId: int, amount: int):
        self.zoneId = zoneId
        self.amount = amount

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        if quester.questerType == QuesterType.Toon:
            quester.updatePlaygroundGagMultiplier(self.zoneId, self.amount)
            # quester.queueScavenge(1, ScavengeType.KudosPGGagXP, [self.zoneId, self.amount])

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [RWD_PGMult.format(track=6, level=0, amount=self.amount,
                                  location=TTLocalizer.ShorthandPlaygroundNames[self.zoneId])]

    def __repr__(self):
        return f'PlaygroundGagMultiplierReward({self.zoneId}, {self.amount})'
