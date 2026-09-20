"""
This module contains the QuestLine class for Clubs.
It uses random quest generation from a ChainID for seeding.
"""
import random

from toontown.club import ClubTaskPricing
from toontown.quest3.QuestEnums import QuestSource, QuesterType
from toontown.quest3.base.QuestChain import QuestChain
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.base.Quester import Quester
from toontown.quest3.generator.QuestGenerator import QuestGenerator
from toontown.quest3.rewards import ClubCoinReward


class ClubsQuestLineContainer(QuestLine):
    questSource = QuestSource.ClubQuest

    def __init__(self):
        super().__init__(questLine={})

    @classmethod
    def getQuestChainFromChainId(cls, questSource: int, chainId: int, quester: Quester) -> QuestChain:
        """
        The trick for ClubsQuest is that we override this
        class to create our own QuestChain dynamically!

        Using the chainId as a seed, we let the 0-999,999 represent
        a randomly generated seed for the task, and then the 1,000,000s field
        represents the capacity of the club.
        """
        # Get our input values.
        seed = chainId % 1_000_000

        # The minimum chainId is 1,000,000, and the max is 72,999,999.
        # So, we interp a difficulty range from 2 to 111.424.
        difficulty = 1.0 + ((chainId // 1_000_000) ** 1.1)

        # Initialize a QuestGenerator.
        questGenerator = QuestGenerator(seed=seed)

        # Generate a MultiObjective.
        multiObjective = questGenerator.generateTask(questerType=QuesterType.Club, difficulty=difficulty, questSource=questSource,
                                                     forcedObjectiveCount=1)

        # Use a base Club Coin reward for client view.
        coinRewardAmount = ClubTaskPricing.calculateTaskReward(chainId)
        clubCoinReward = ClubCoinReward(coins=coinRewardAmount)

        # Return our quest chain.
        return QuestChain(steps={1: multiObjective}, rewards=clubCoinReward)


ClubsQuestLine = ClubsQuestLineContainer()
