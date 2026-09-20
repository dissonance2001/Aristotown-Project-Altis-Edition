import math

from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.IceGameContext import IceGameContext
from toontown.quest3.QuestLocalizer import (HL_Collect, IceSlide, OBJ_Collect, OnDaTrolley, PROG_Collect,
                                            QuestProgress_Complete, SC_IceSlide)


class IceGameObjective(QuestObjective):
    def __init__(self,
                 npc=2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 treasureCount: int = None,
                 zoneId: int = None):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)
        self.treasureCount = treasureCount
        self.zoneId = zoneId

    def calculateProgress(self, context: IceGameContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not IceGameContext:
            return 0
        if self.zoneId is not None and context.getZoneId() != self.zoneId:
            return 0
        return context.getTreasuresCollected()

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        """
        Returns the difficulty range required to use this objective in random quest generation.

        :return: Any of the following:
                 A) Two floats, for a lower and upper bound
                 B) A float and None, for a lower bound and no upper bound
                 C) None and a float, for no lower bound and an upper bound
                 D) Two nones, for no difficulty bound
                 E) One none, for "cannot be used"
        """
        return None  # die

    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        """
        The likelihood for this objective to be chosen in a pool.
        The de facto amount is 100.
        """
        return 7

    @classmethod
    def generateFromDifficulty(cls, rng, difficulty: float, questSource: QuestSource, **extraArgs):
        """
        Given an arbitrary difficulty value, generate a QuestObjective.
        For more info, seek QuestGenerator.py.

        :param rng:        A seeded Random instance. Use this for .random() or .randint() calculations.
        :param difficulty: The arbitrary difficulty of the task.
        :return:           This QuestObjective, set with values to match the arbitrary difficulty.
        """
        treasureCount = 0.7 * (difficulty ** 1.2)
        treasureCount += treasureCount * (rng.random() * rng.choice((-0.2, 0.2)))

        # Round off our cog count so that it is pretty.
        treasureCount = math.ceil(treasureCount)
        if treasureCount < 1:
            treasureCount = 1
        elif treasureCount < 10:
            pass
        elif treasureCount < 20:
            treasureCount = round(round(treasureCount / 2) * 2)
        elif treasureCount < 40:
            treasureCount = round(round(treasureCount / 5) * 5)
        else:
            treasureCount = round(round(treasureCount / 20) * 20)

        # Fruit time
        return cls(
            treasureCount=treasureCount,
            npcReturnable=False,
            zoneId=extraArgs.get("zoneId")
        )
    
    def getCompletionRequirement(self) -> int:
        return self.treasureCount

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        searchPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameColor(searchPoster, 'lightBlue')

        if self.treasureCount == 1:
            frameText = 'Collect a Treasure Barrel'
        else:
            frameText = f'Collect {self.treasureCount} Treasure Barrels'

        poster.visual_setFrameText(searchPoster, frameText)

        geom = loader.loadModel('phase_4/models/minigames/ice_game_barrel')
        poster.visual_setFrameGeom(
            searchPoster, geom,
            pos=(-0.012, 10, -0.046),
            hpr=(30, 30, 0),
            scale=0.044,
        )

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'lightBlue')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        else:
            if self.treasureCount > 1:
                value, range, textFormat = self.getProgressFormat(questReference)
                poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.treasureCount, PROG_Collect

    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            return super().getInfoTextStrings(questReference)

        return IceSlide, OnDaTrolley, self.getLocationName(self.zoneId),

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get book specific message
        return SC_IceSlide,

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Collect
    
    def getObjectiveGoal(self) -> str:
        return OBJ_Collect % "some Treasure Barrels"
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.treasureCount == 1:
            return ''
        return PROG_Collect.format(value=min(progress, self.treasureCount), range=self.treasureCount)
    
    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.treasureCount is not None:
            kwargstr += f'treasureCount={self.treasureCount}, '
        return kwargstr

    def __repr__(self):
        return f'IceGameObjective({self._getKwargStr()[:-2]})'


IceGameObjective() # thanks m a in
