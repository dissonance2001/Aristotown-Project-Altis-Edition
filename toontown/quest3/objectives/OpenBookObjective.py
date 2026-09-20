from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.OpenBookContext import OpenBookContext
from toontown.quest3.QuestLocalizer import Anywhere, HL_Book, OBJ_OpenBook, QuestProgress_Complete, SC_Book


class OpenBookObjective(QuestObjective):

    poster_canUpdateAux = False

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)

    def calculateProgress(self, context: OpenBookContext, questReference: QuestReference, quester: Quester) -> int:
        return type(context) is OpenBookContext

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, 'lightBlue')
        poster.visual_setFrameText(searchPoster, "Open your Shtickerbook")
        poster.visual_setShtikerBookGeom(searchPoster)

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'lightBlue')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        # If we're complete and demand NPC completion, point to NPC instead
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            return super().getInfoTextStrings(questReference)

        return Anywhere,

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get book specific message
        return SC_Book,

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Book
    
    def getObjectiveGoal(self) -> str:
        return OBJ_OpenBook
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        return ''

    def __repr__(self):
        return f'OpenBookObjective({self._getKwargStr()[:-2]})'
