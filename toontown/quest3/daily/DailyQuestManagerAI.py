from time import time

from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr, Task

from toontown.quest3.QuestEnums import QuestSource
from toontown.quest3.base.QuestReference import QuestReference, QuestId
from toontown.quest3.base.Quester import Quester
from toontown.quest3.questlines.DailyQuestLine import DailyQuestLine
from toontown.time import TimeUtil


class DailyQuestManagerAI:
    """
    DailyQuestManagerAI: Handles functionality for daily quests
    such as rerolling and updating dailies at midnight.
    """
    
    def __init__(self):
        # Begin a daily task which will update the daily quests
        # of every online toon in the district.
        self.dailyUpdateTask = "daily_dailyQuestUpdate"
        timestamp = TimeUtil.getNextTimestampOfMidnight()
        taskMgr.doMethodLater(
            timestamp - time() + 0.5,
            self.updateDailyQuests,
            self.dailyUpdateTask
        )

    @staticmethod
    def updateDailyQuests(task: Task.Task) -> None:
        """Method called every 24 hours to update the daily quests
        of all online toons in the district. This update entails
        populating their daily quests with a new one if possible.
        """
        messenger.send("daily_dailyQuestUpdate")
        task.delayTime = TimeUtil.getNextTimestampOfMidnight() - time()
        return task.again

    @staticmethod
    def requestRerollQuest(quester: Quester, questRef: QuestReference):
        """Requests for a quest to be rerolled."""
        # They need to have this quest, and can successfully spend a reroll.
        if questRef not in quester.getQuestReferencesOfSource(QuestSource.DailyQuest):
            return

        # Definitely make sure it is here.
        questRefs = quester.getQuestReferences()
        if questRef not in questRefs:
            return
        questRefIndex = questRefs.index(questRef)

        # And they can afford it?
        if not quester.spendDailyQuestReroll():
            return

        # OK, reroll this quest for them.
        chainId = DailyQuestLine.getRandomDailyQuestChainId(quester)
        questRefs[questRefIndex] = QuestReference(
            questId=QuestId(QuestSource.DailyQuest, chainId, 1)
        )
        quester.updateQuestProgress()
