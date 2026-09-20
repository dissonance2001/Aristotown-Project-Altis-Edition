from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.GoSadContext import GoSadContext
from toontown.quest3.QuestLocalizer import Anywhere, HL_SAD, OBJ_Sad, QuestProgress_Complete, SC_Sad, PROG_Times


class GoSadObjective(QuestObjective):

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)

    def calculateProgress(self, context: GoSadContext, questReference: QuestReference, quester: Quester) -> int:
        return type(context) is GoSadContext

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        sadPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(sadPoster, 'blue')
        poster.visual_setFrameText(sadPoster, "Go Sad")
        poster.visual_setLaffMeterGeom(sadPoster, 0)

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'blue')
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
        return SC_Sad,

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_SAD
    
    def getObjectiveGoal(self) -> str:
        return OBJ_Sad

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), 1, PROG_Times

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        return ''

    def __repr__(self):
        return f'GoSadObjective({self._getKwargStr()[:-2]})'
