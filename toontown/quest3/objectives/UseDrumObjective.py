import math

from toontown.quest3 import QuestLocalizer
from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.UseDrumContext import UseDrumContext
from toontown.quest3.QuestLocalizer import HL_JumpOn, OBJ_JumpOn, PROG_Jumps, QuestProgress_Complete, SC_JumpOn, PFX_JUMP_ON_MML


class UseDrumObjective(QuestObjective):
    def __init__(self,
                 npc=2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 useCount: int = 1):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)
        self.useCount = useCount

    def calculateProgress(self, context: UseDrumContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not UseDrumContext:
            return 0
        return 1

    def getCompletionRequirement(self) -> int:
        return self.useCount

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        # Can only show up for Kudos quests
        if questSource != QuestSource.KudosQuest:
            return None

        # Can only show up in MML
        zoneId = extraArgs.get("zoneId")
        if zoneId != ToontownGlobals.MinniesMelodyland:
            return None

        # We are now free to give this quest out
        return None, None

    @classmethod
    def generateFromDifficulty(cls, rng, difficulty: float, questSource: QuestSource, **extraArgs):
        """
        Given an arbitrary difficulty value, generate a QuestObjective.
        For more info, seek QuestGenerator.py.

        :param rng:        A seeded Random instance. Use this for .random() or .randint() calculations.
        :param difficulty: The arbitrary difficulty of the task.
        :return:           This QuestObjective, set with values to match the arbitrary difficulty.
        """

        # Return our objective.
        return cls(
            useCount=round(difficulty * 2.5),
            npcReturnable=False,
        )

    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        return 1

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, 'green' if complete and self.npcReturnable else 'lightBlue')
        poster.visual_setFrameText(searchPoster, PFX_JUMP_ON_MML + (f'{self.useCount} Times'
                                                                    if self.useCount > 1 else 'Time'))

        geom = loader.loadModel('phase_4/models/props/mml-treasure')
        poster.visual_setFrameGeom(searchPoster, geom, scale=0.042, pos=(0, 10, -0.062))
        geom.removeNode()

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'green')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        else:
            if self.useCount > 1:
                value, range, textFormat = self.getProgressFormat(questReference)
                poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.useCount, PROG_Jumps

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            return super().getInfoTextStrings(questReference)
        return TTLocalizer.lMinniesMelodyland,

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get book specific message
        return SC_JumpOn % (self.useCount, 's' if self.useCount > 1 else ''),

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_JumpOn

    def getObjectiveGoal(self) -> str:
        return OBJ_JumpOn % 'a Drum'

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.useCount == 1:
            return ''
        return PROG_Jumps.format(value=min(progress, self.useCount), range=self.useCount)

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.useCount != 1:
            kwargstr += f'useCount={self.useCount}, '
        return kwargstr

    def __repr__(self):
        return f'UseDrumObjective({self._getKwargStr()[:-2]})'
