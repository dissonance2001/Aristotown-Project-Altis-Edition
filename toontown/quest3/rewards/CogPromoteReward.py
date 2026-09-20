"""
Cog promotion reward class for quests.
"""
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.QuestLocalizer import RWD_SuitPromote
from toontown.quest3.base.QuestReward import QuestReward
from toontown.quest3.base.Quester import Quester


class CogPromoteReward(QuestReward):

    def __init__(self, dept: int):
        self.dept = dept

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        if quester.questerType == QuesterType.Toon:
            quester.cogReviveTierPromote(self.dept)
            # Funny dust cloud for the transition
            quester.d_doDustCloud()
            quester.b_setCogIndex(self.dept)

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [RWD_SuitPromote]

    def __repr__(self):
        return f'CogPromoteReward({self.dept})'
