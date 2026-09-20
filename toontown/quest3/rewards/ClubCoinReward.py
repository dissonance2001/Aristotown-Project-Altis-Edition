"""
Club Coin reward class for quests.
"""
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.QuestLocalizer import RWD_ClubCoins
from toontown.quest3.base.QuestReward import QuestReward
from toontown.quest3.base.Quester import Quester


class ClubCoinReward(QuestReward):

    def __init__(self, coins: int):
        self.coins = coins

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        return  # does nothing, UD has to reward the club

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return [RWD_ClubCoins % round(self.coins * multiplier)]

    def __repr__(self):
        return f'ClubCoinReward({self.coins})'
