from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.KnockKnockContext import KnockKnockContext
from toontown.quest3.QuestLocalizer import Anywhere, HL_KNOCK, OBJ_Knock, QuestProgress_Complete, SC_Knock, PROG_Times


class KnockKnockObjective(QuestObjective):

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)

    def calculateProgress(self, context: KnockKnockContext, questReference: QuestReference, quester: Quester) -> int:
        return type(context) is KnockKnockContext

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        knockPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(knockPoster, 'blue')
        poster.visual_setFrameText(knockPoster, "Laugh at a Joke")
        poster.visual_setFrameQuestionGeom(knockPoster)

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
        return SC_Knock,

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_KNOCK
    
    def getObjectiveGoal(self) -> str:
        return OBJ_Knock

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), 1, PROG_Times

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        return ''

    def __repr__(self):
        return f'KnockKnockObjective({self._getKwargStr()[:-2]})'
