"""
Dummy reward.
"""
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.base.QuestReward import QuestReward
from toontown.quest3.base.Quester import Quester
from toontown.toonbase import TTLocalizer


class DummyReward(QuestReward):

    def __init__(self, rewardName: str):
        self.rewardName = rewardName

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        pass

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [f'\1white\1\5reward_packageIcon\5\2 {self.rewardName}']

    def __repr__(self):
        return f'DummyReward({self.rewardName})'


"""
Other Dummy Rewards
"""


class GumballMachineBoosterReward(DummyReward):
    def __init__(self, zoneId):
        super().__init__('+1 G.U.M.B.A.L.L. Machine Booster')
        self.zoneId = zoneId

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        pass
        # if quester.questerType == QuesterType.Toon:
        #     quester.queueScavenge(1, ScavengeType.BoosterSlot, [self.zoneId])

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [f'\1white\1\5reward_gumballIcon\5\2 {self.rewardName}']


class KudosRankUpReward(DummyReward):
    def __init__(self, location, rank):
        self.location = location
        self.rank = rank
        super().__init__('Kudos Rank-Up')

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        #if quester.questerType == QuesterType.Toon:
         #  quester.queueScavenge(1, ScavengeType.KudosXP, [self.location, self.rank, 0])
        pass

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [f'\1white\1\5reward_kudosRankUpSmall\5\2 {TTLocalizer.ShorthandPlaygroundNames[self.location]} {self.rewardName}']


class PlaygroundHealBoostReward(DummyReward):
    def __init__(self, location, amount):
        self.location = location
        self.amount = amount
        super().__init__('Playground Heal Boost')

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        if quester.questerType == QuesterType.Toon:
            quester.queueScavenge(1, ScavengeType.PlaygroundHealBoost, [self.location, self.amount])

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [f'\1white\1\5reward_laffIcon{self.amount}\5\2 Heal in {TTLocalizer.ShorthandPlaygroundNames[self.location]}']
