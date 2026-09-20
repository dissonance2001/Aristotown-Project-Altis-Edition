import math
import random
from toontown.golf import GolfGlobals

from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import AuxillaryText_Against, AuxillaryText_Complete, HL_Damage, HL_Golf, \
    PROG_Damage, PROG_GolfHits, QuestProgress_Complete, SC_Damage, SC_GolfHits
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.context.CogBossContext import BossbotBossContext
from ..daily.DailyConstants import QuestTier
from toontown.quest3.objectives.DamageBossObjective import DamageBossObjective
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, \
    DaisyGardens, MinniesMelodyland, TheBrrrgh


class GolfDamageObjective(DamageBossObjective):
    def calculateProgress(self, context: BossbotBossContext, questReference: QuestReference, quester: Quester) -> int:
        if not isinstance(context, BossbotBossContext):
            return 0
        if self.cogTrack is not None and self.cogTrack != context.getCogTrack():
            return 0
        return context.getGolfHits()
    
    def getCompletionRequirement(self) -> int:
        return self.damageAmount

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock, YeOlde, DaisyGardens,
                          MinniesMelodyland, TheBrrrgh):
                return None
        elif questSource == QuestSource.DailyQuest:
            questTier = extraArgs.get("questTier")
            if questTier in (QuestTier.NEWBIE, QuestTier.TTC, QuestTier.BB, QuestTier.YOTT,
                             QuestTier.DG, QuestTier.MML, QuestTier.TB):
                return

        if questerType == QuesterType.Toon:
            return 3, None
        elif questerType == QuesterType.Club:
            return None
        else:
            return 3, None

    @classmethod
    def generateFromDifficulty(cls, rng, difficulty: float, questSource: QuestSource, **extraArgs):
        """
        Given an arbitrary difficulty value, generate a QuestObjective.
        For more info, seek QuestGenerator.py.

        :param rng:        A seeded Random instance. Use this for .random() or .randint() calculations.
        :param difficulty: The arbitrary difficulty of the task.
        :return:           This QuestObjective, set with values to match the arbitrary difficulty.
        """
        # Set initial parameters.
        damageAmount = 1.8 * (difficulty ** 1.475)
        
        # Round off our cog count so that it is pretty.
        damageAmount = math.ceil(damageAmount)
        if damageAmount < 1:
            damageAmount = 1
        elif damageAmount < 10:
            pass
        elif damageAmount < 20:
            damageAmount = round(round(damageAmount / 2) * 2)
        elif damageAmount < 50:
            damageAmount = round(round(damageAmount / 5) * 5)
        elif damageAmount < 100:
            damageAmount = round(round(damageAmount / 10) * 10)
        else:
            damageAmount = round(round(damageAmount / 20) * 20)

        # Return our objective.
        return cls(
            damageAmount=math.ceil(damageAmount),
            cogType='ceo',
            cogTrack='c',
            npcReturnable=False,
        )

    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        return 8

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Golf
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.damageAmount == 1:
            return ''
        return PROG_GolfHits.format(value=min(progress, self.damageAmount), range=self.damageAmount)
    
    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        cogPoster = poster.RIGHT if not (complete and self.npcReturnable) else poster.LEFT
        self.setCogFrame(cogPoster, poster)

        if not (complete and self.npcReturnable):
            geom = loader.loadModel('phase_6/models/golf/golf_ball')
            geom.setColorScale(*random.choice(GolfGlobals.PlayerColors))
            poster.visual_setFrameGeom(poster.LEFT, geom, 0.2)
            poster.visual_setFrameColor(poster.LEFT, 'orange')
            poster.visual_setFrameText(poster.LEFT, f'Golf {self.damageAmount} Hits')
        
        poster.visual_setAuxText(AuxillaryText_Against)
        poster.label_auxillaryText.show()

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'orange')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.visual_setAuxText(AuxillaryText_Complete)
        # And if we're not, show progress
        else:
            value, range, textFormat = self.getProgressFormat(questReference)
            poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)
    
    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.damageAmount, PROG_GolfHits
    
    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        cogName = self.getCogNameString()
        return SC_GolfHits % (cogName, self.damageAmount),

    """text makin methods"""

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.damageAmount != 1:
            kwargstr += f'damageAmount={self.damageAmount}, '
        return kwargstr


GolfDamageObjective() # thanks m ai n
