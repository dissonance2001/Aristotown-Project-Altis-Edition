from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.base.Quester import Quester
from .QuestRequirement import QuestRequirement


class SuitDisguiseRequirement(QuestRequirement):
    """
    This requirement checks that the Toon has the tier and level of suit defined, or higher.
    """

    def __init__(self, dept: int, tier: int, level: int, executive: bool=False):
        """
        :param dept: Department of suit (starts at 0).
        :param tier: Tier of suit (starts at 0).
        :param level: Level of suit (starts at 0).
        :param executive: Executive suit or not.
        """
        self.dept = dept
        self.tier = tier
        self.level = level
        self.executive = executive

    def check(self, quester: Quester):
        if quester.questerType == QuesterType.Toon:
            if self.executive:
                if quester.cogReviveLevels[self.dept] > -1:
                    return self.checkTierAndLevel(quester.cogTypes[self.dept], quester.cogReviveLevels[self.dept])
                return False
            if quester.cogReviveLevels[self.dept] > -1:
                return True
            return self.checkTierAndLevel(quester.cogTypes[self.dept], quester.cogLevels[self.dept])
        return super().check()

    def checkTierAndLevel(self, avTier, avLevel):
        if self.tier < avTier:
            return True
        elif self.tier == avTier and self.level <= avLevel:
            return True
        return False
    
    def __repr__(self) -> str:
        return f"SuitDisguiseRequirement({self.dept}, {self.tier}, {self.level}, {self.executive})" 
