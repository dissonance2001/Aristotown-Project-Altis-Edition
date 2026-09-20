"""
This module contains the QuestLine class for Daily Tasks.
It uses random quest generation from a ChainID for seeding.

Daily Tasks are also wrapped in a unique MultiObjective,
which allows them to only be "completed" through a unique context.
"""
import random
import time

from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.quest3.QuestEnums import QuestSource, QuesterType
from toontown.quest3.base.QuestChain import QuestChain
from toontown.quest3.base.QuestContext import QuestContext
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.base.QuestObjective import MultiObjective
from toontown.quest3.base.QuestReference import QuestReference, QuestId
from toontown.quest3.base.QuestReward import QuestReward
from toontown.quest3.base.Quester import Quester
from toontown.quest3.context.ManualContext import ManualContext
from toontown.quest3.daily.DailyConstants import QuestChainToTier, QuestTier, DailyGumballReward
from toontown.quest3.generator.QuestGenerator import QuestGenerator
from toontown.quest3.rewards import *
from toontown.toon.ToonStatsGlobals import ToonStats


class DailyQuestLineContainer(QuestLine):
    questSource = QuestSource.DailyQuest

    def __init__(self):
        super().__init__(questLine={})

    @classmethod
    def getQuestChainFromChainId(cls, questSource: int, fullChainId: int, quester: Quester) -> QuestChain:
        """
        The trick for daily quests is that we override this
        class to create our own QuestChain dynamically!

        Using the chainId as a seed, we let the 0-999,999 represent
        a randomly generated seed for the task, and then the 1,000,000s field
        represents the capacity of the club.
        """
        # Parse the chain id and separate it into the difficulty,
        # the npc index, and the chain id.
        chainId = str(fullChainId)
        questTier, difficulty, chainId = int(chainId[0]), int(chainId[1]), int(chainId[2:])

        # Get our input values.
        seed = chainId % 1_000_000

        # Difficulty is an integer between 1 and 3 to add variance.
        difficulty = 1.5 + ((questTier - 1) * 0.7) * ((difficulty + 7) / 10)

        # Initialize a QuestGenerator.
        questGenerator = QuestGenerator(seed=seed)

        # Generate a MultiObjective.
        multiObjective = questGenerator.generateTask(
            questerType=QuesterType.Toon,
            difficulty=difficulty, questSource=questSource,
            questTier=QuestTier(questTier - 1), forcedObjectiveCount=1,
            # multiObjectiveCls=ManualMultiObjective,
        )

        rewards = [InventoryReward(MaterialItemType.Gumballs, quantity=50), DailyTaskCompletion(fullChainId)]
        # if quester:
        #     rewards.append(BoosterReward(getReasonableBooster(quester, includeSuper=True, seed=seed), 2))

        # Return our quest chain.
        return QuestChain(
            steps={1: multiObjective}, 
            rewards=tuple(rewards),
        )

    @staticmethod
    def getRandomDailyQuestChainId(quester: Quester) -> int:
        # Generate a random difficulty.
        difficulty = random.randint(1, 3)

        questProgression = quester.getHighestChainIdOfSource(QuestSource.MainQuest)
        if questProgression is not None:
            questTier = len([chainId for chainId in QuestChainToTier if chainId < questProgression])
        else:
            questTier = 0

        # Choose a random seed between the lower and upper bounds.
        for attempts in range(16):
            seed = random.randint(0, 999999)
            chainId = ((questTier + 1) * 1_000_000) + seed

            # Create the real chain id used to generate the quest.
            realChainId = int(str(questTier) + str(difficulty) + str(chainId).zfill(7))

            questObjective = DailyQuestLine.getQuestObjectiveFromId(
                QuestId(QuestSource.DailyQuest, realChainId, 1), quester
            ).getInitialObjective()

            # Validate this daily task.
            if attempts < 8:
                # In earlier attempts, try to avoid duplicate objectives.
                if quester.getQuestObjectivesOfType(type(questObjective), source=QuestSource.DailyQuest):
                    continue

            # Make sure this isn't STUPID to offer early.
            lowestToonLevel = questObjective.getLowestToonLevel()
            if lowestToonLevel and quester.getToonLevel() < lowestToonLevel:
                continue

            # good.
            break

        return realChainId


class ManualMultiObjective(MultiObjective):
    """
    A container class for Daily Task objectives that require
    a manual completion of a daily task.
    """

    def isComplete(self, questReference: QuestReference, context: QuestContext, quester: Quester) -> bool:
        """
        Given a QuestReference, determines if the quest container is complete or not.
        Subclasses of MultiObjective can override this for unique functionality.
        """
        # The context must be manual.
        if not isinstance(context, ManualContext):
            return False

        # The ID of the ManualContext must be the same as the daily task.
        if context.getId() != questReference.getChainId():
            return False

        # We then do standard logic to ask if all objectives are complete.
        return all(questObjective.isComplete(questReference=questReference,
                                             objectiveIndex=index, quester=quester)
                   for index, questObjective in enumerate(self.getQuestObjectives()))


class DailyTaskCompletion(QuestReward):

    def __init__(self, chainId: int):
        self.chainId = chainId

    def handleReward(self, quester: Quester, multiplier: float = 1.0) -> None:
        if quester.questerType == QuesterType.Toon:
            # quester.queueScavenge(
            #     amount=1,
            #     scavengeType=ScavengeType.DailyTask,
            #     extraArgs=[self.chainId, 1]
            # )
            quester.addStat(ToonStats.DAILY_TASKS)

    def getRewardString(self, multiplier: float = 1.0) -> list:
        return []

    def __repr__(self):
        return f'DailyTaskCompletion()'



DailyQuestLine = DailyQuestLineContainer()

# Rng for daily objective rewards.
DAILY_RNG = random.Random()
