from toontown.club import ClubGlobals
from toontown.club.ClubContainerBase import ClubContainerBase


class ClubContainerAI(ClubContainerBase):
    """
    The AI-side representation of a ClubContainer.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Local caches
        self.cachedQuestProgress = [task.getTaskProgress()[0] for task in self.getClubTasks()]
        self.progressCache = []

    def getProgressTaskName(self) -> str:
        return f'ClubContainerAI-{self.getClubId()}-QuestProgressDebounce'

    def updateQuestProgress(self) -> None:
        if not self.cachedQuestProgress:
            # We should have this existing by now.
            return

        # Figure out the difference in quest progress.
        incrementedProgress = []
        for taskIndex, task in enumerate(self.getClubTasks()):
            oldVal = self.cachedQuestProgress[taskIndex]
            newVal = task.getTaskProgress()[0]

            # Find the incremented progress.
            increase = max(newVal - oldVal, 0)
            incrementedProgress.append(increase)

        # Update the cache.
        self.cachedQuestProgress = [task.getTaskProgress()[0] for task in self.getClubTasks()]
        self.progressCache.append(incrementedProgress)

        # Debounce a progress task.
        taskMgr.remove(self.getProgressTaskName())
        taskMgr.doMethodLater(
            0.1, self.sendProgressCall, self.getProgressTaskName(), extraArgs=[]
        )

    def sendProgressCall(self):
        questProgress = [0] * ClubGlobals.ClubTaskCount
        for cachedProgress in self.progressCache:
            for progressIndex, progress in enumerate(cachedProgress):
                questProgress[progressIndex] += progress
        self.progressCache = []
        if sum(questProgress) > 0:
            simbase.air.clubMgr.updateQuestProgressAI(
                self.getClubId(),
                [task.getChainId() for task in self.getClubTasks()],
                questProgress,
            )
