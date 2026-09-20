"""
Suit switcher reward class for quests.
"""
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.QuestLocalizer import RWD_SuitSwitch
from toontown.quest3.base.QuestReward import QuestReward
from toontown.quest3.base.Quester import Quester
from toontown.clashsuit.suit.SuitDNA import suitDeptFullnames, suitDepts
from toontown.toonbase import ToontownGlobals


class SuitSwitchReward(QuestReward):

    def __init__(self, dept: int):
        self.dept = dept

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        if quester.questerType == QuesterType.Toon:
            quester.addSwitch(self.dept)

    def getRewardString(self, multiplier: float = 1.0) -> list:
        deptName = suitDeptFullnames.get(suitDepts[self.dept])
        return [RWD_SuitSwitch % deptName]

    def __repr__(self):
        return f'SuitSwitchReward({self.dept})'
