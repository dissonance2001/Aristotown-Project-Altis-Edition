import math

from toontown.quest3 import QuestLocalizer
from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.InteractibleEntityContext import InteractibleEntityContext
from toontown.quest3.QuestLocalizer import HL_Interact, OBJ_Interact, QuestProgress_Complete, SC_Interact, \
    PFX_INTERACT, PROG_Interact

from toontown.zone.entities.quest.QuestInteractibleGlobals import QuestInteractibleType, QuestInteractibleNames


class InteractibleEntityObjective(QuestObjective):
    def __init__(self,
                 npc=2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 interactibleType: QuestInteractibleType = 'test_crate',
                 zoneId: int = None):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)
        self.interactibleType = interactibleType
        self.zoneId = zoneId

    def calculateProgress(self, context: InteractibleEntityContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not InteractibleEntityContext:
            return 0
        if context.getInteractibleType() != self.interactibleType:
            return 0
        if self.zoneId is not None and not self.checkLocation(context):
            return 0
        return 1

    def checkLocation(self, context: InteractibleEntityContext):
        if self.zoneId == context.getZoneId():
            return True
        elif self.zoneId == ZoneUtil.getHoodId(context.getZoneId()):
            return True
        return False

    def getCompletionRequirement(self) -> int:
        return 1

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        return None

    def getInteractName(self) -> str:
        return QuestInteractibleNames.get(self.interactibleType, 'something')

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, 'green' if complete and self.npcReturnable else 'lightBlue')
        poster.visual_setFrameText(searchPoster, PFX_INTERACT + self.getInteractName())

        questIcons = loader.loadModel('phase_3.5/models/gui/quests/ttcc_quest_icons')
        glass = questIcons.find('**/magnifyingGlass')
        questIcons.removeNode()
        poster.visual_setFrameGeom(
            positionIndex=searchPoster,
            geom=glass,
            scale=0.1425
        )

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'green')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        else:
            value, range, textFormat = self.getProgressFormat(questReference)
            poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), 1, PROG_Interact

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            return super().getInfoTextStrings(questReference)
        return self.getLocationName(self.zoneId),

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get book specific message
        return SC_Interact % self.getInteractName(),

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Interact

    def getObjectiveGoal(self) -> str:
        return OBJ_Interact % self.getInteractName()

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        return ''

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.interactibleType:
            kwargstr += f'interactibleType={self.interactibleType}, '
        if self.zoneId:
            kwargstr += f'zoneId={self.zoneId}, '
        return kwargstr

    def __repr__(self):
        return f'InteractibleEntityObjective({self._getKwargStr()[:-2]})'
