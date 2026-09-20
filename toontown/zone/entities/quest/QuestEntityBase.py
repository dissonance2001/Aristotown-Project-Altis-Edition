from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.level.Entity import Entity
from toontown.level.editor import EditorGlobals
from toontown.quest3.base.QuestReference import QuestReference, QuestId
from toontown.quest3.base.QuestHistory import QuestHistory


@DirectNotifyCategory(debug=True)
class QuestEntityBase(Entity):
    """
    The base class for any Level entity that functions based on
    the local avatar's quest progress.

    When the local avatar receives the quest we are checking for:
        handleReceivedWantedQuest()
    When the local avatar finishes the quest we are checking for:
        handleFinishedWantedQuest()
    """

    def __init__(self, level=None, entId=None):
        Entity.__init__(self, level=level, entId=entId)
        self.callSetters('wantedQuest')
        self.hadWantedQuest = self.localAvHasQuest()
        self.accept('questsChanged', self.__localAvQuestsChanged)

    @property
    def wantedQuestSource(self):
        return self.wantedQuest.questSource

    @property
    def wantedQuestChain(self):
        return self.wantedQuest.chainId

    @property
    def wantedQuestStep(self):
        return self.wantedQuest.objectiveId

    def localAvHasQuest(self) -> bool:
        # Try to find it in their quest references.
        for questReference in base.localAvatar.getQuestReferences():
            questReference: QuestReference
            if questReference.getQuestSource() == self.wantedQuestSource and \
                    questReference.getChainId() == self.wantedQuestChain and \
                    questReference.getObjectiveId() == self.wantedQuestStep:
                return True

        return False

    def localAvHasFurtherQuest(self):
        for questReference in base.localAvatar.getQuestReferences():
            questReference: QuestReference
            if questReference.getQuestSource() != self.wantedQuestSource:
                # Ignore if quest source isnt the same
                continue
            if questReference.getChainId() < self.wantedQuestChain:
                # Ignore if the chain ID is less than our wanted one
                continue
            if questReference.getChainId() > self.wantedQuestChain:
                # Always return true if chain ID is higher
                return True
            if questReference.getChainId() == self.wantedQuestChain:
                # If the chain ID is the same, return true if:
                # 1. The objective ID is higher, or
                # 2. The objective ID is the same, but its marked as completed
                if questReference.getObjectiveId() > self.wantedQuestStep:
                    return True
                elif questReference.getObjectiveId() == self.wantedQuestStep and \
                        questReference.isQuestComplete(base.localAvatar):
                    return True

        return False

    def localAvHasQuestHistory(self):
        questHistory = QuestHistory(self.wantedQuestSource, self.wantedQuestChain)
        return questHistory in base.localAvatar.getQuestHistory()

    @property
    def localAvMovedToNextStep(self) -> bool:
        if not self.hadWantedQuest:
            # We never had the quest to begin with, so we couldn't have moved on to the next step.
            return False

        return self.localAvHasFurtherQuest()

    def setWantedQuest(self, wantedQuest) -> None:
        if type(wantedQuest) is tuple:
            self.wantedQuest = QuestId(*wantedQuest)
        else:
            self.wantedQuest = wantedQuest

    def __localAvQuestsChanged(self) -> None:
        self.notify.debug('QuestEntityBase.__localAvQuestsChanged()')
        if self.localAvMovedToNextStep:
            # We've moved on to the next step of the quest,
            # The entity can now decide what to do with itself from here.
            self.hadWantedQuest = False
            self.handleFinishedWantedQuest()
        elif not self.hadWantedQuest and self.localAvHasQuest():
            # We did not have the quest before, but now we do.
            # Some quests may want to do something special.
            self.hadWantedQuest = True
            self.handleReceivedWantedQuest()

    def handleFinishedWantedQuest(self) -> None:
        # Override this to define custom behavior when the local avatar
        # finishes the quest we are checking for
        self.notify.debug('QuestEntityBase.handleFinishedWantedQuest()')

    def handleReceivedWantedQuest(self) -> None:
        # Override this to define custom behavior when the local avatar
        # receives the quest we are checking for
        self.notify.debug('QuestEntityBase.handleReceivedWantedQuest()')


@DirectNotifyCategory(debug=True)
class QuestCutsceneEntityBase(QuestEntityBase):
    @property
    def cutsceneObjects(self) -> list:
        return [self]

    def handleFinishedWantedQuest(self) -> None:
        super().handleFinishedWantedQuest()
        # We have a key for finished quests, go ahead and run the cutscene.
        if self.ctsc_finQuest_key:
            self.level.cutsceneHandler.addCutscene(self.ctsc_finQuest_key, objects=self.cutsceneObjects, args=self.ctsc_finQuest_args)

    def handleReceivedWantedQuest(self) -> None:
        super().handleReceivedWantedQuest()
        # We have a key for received quests, go ahead and run the cutscene.
        if self.ctsc_getQuest_key:
            self.level.cutsceneHandler.addCutscene(self.ctsc_getQuest_key, objects=self.cutsceneObjects, args=self.ctsc_getQuest_args)
