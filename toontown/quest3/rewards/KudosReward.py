"""
Kudos reward class for kudos quests.
"""
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.QuestLocalizer import RWD_Kudos
from toontown.quest3.base.QuestReward import QuestReward
from toontown.quest3.base.Quester import Quester
from toontown.toonbase import TTLocalizer


class KudosReward(QuestReward):
    RibbonTypes = {
        1: 'Bronze',
        2: 'Silver',
        3: 'Gold',
    }

    def __init__(self, zoneId: int, kudos: int):
        self.zoneId = zoneId
        self.kudos = kudos

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        if quester.questerType == QuesterType.Toon:
            simbase.air.kudosManager.giveKudos(quester, self.getKudos(), self.zoneId)
            # quester.queueScavenge(1, ScavengeType.KudosXP, [self.zoneId, 0, self.getKudos()])

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [RWD_Kudos % (self.getRibbonType(), self.getKudos(), TTLocalizer.ShorthandPlaygroundNames[self.zoneId])]

    def getKudos(self):
        return self.kudos

    def getRibbonType(self):
        return self.RibbonTypes.get(self.getKudos(), 'Bronze')

    def __repr__(self):
        return f'KudosReward({self.getKudos()})'
