from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.SnowballContext import SnowballContext
from toontown.quest3.QuestLocalizer import (HL_Collect, InThePlayground, OBJ_Collect, QuestProgress_Complete,
                                            SC_Snowball, PROG_Collect)


class SnowballObjective(QuestObjective):

    poster_canUpdateAux = False

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)

    def calculateProgress(self, context: SnowballContext, questReference: QuestReference, quester: Quester) -> int:
        return type(context) is SnowballContext

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, 'lightBlue')
        poster.visual_setFrameText(searchPoster, "Collect snowballs")
        poster.visual_setSnowballGeom(searchPoster)

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

        return InThePlayground,

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get book specific message
        return SC_Snowball,

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Collect

    def getObjectiveGoal(self) -> str:
        return OBJ_Collect % "some Snowballs"

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), 1, PROG_Collect

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        return ''

    def __repr__(self):
        return f'SnowballObjective({self._getKwargStr()[:-2]})'
