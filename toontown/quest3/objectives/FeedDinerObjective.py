import math
import random
from typing import Optional

from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import AuxillaryText_Against, AuxillaryText_Complete, AuxillaryText_To, HL_Damage, \
    HL_Feed, PROG_Damage, PROG_Feed, QuestProgress_Complete, SC_Damage, SC_Feed, OBJ_Feed
from toontown.quest3.base.QuestObjective import QuestObjective
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.quest3.context.CogBossContext import BossbotBossContext
from ..daily.DailyConstants import QuestTier
from toontown.quest3.objectives.CogBossObjective import CogBossObjective
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, \
    DaisyGardens, MinniesMelodyland, TheBrrrgh
from panda3d.core import NodePath


class FeedDinerObjective(CogBossObjective):
    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 cogAmount: int = 1,
                 executive: bool = False,
                 cogTrack: str = None,
                 cogType: str = None,
                 zoneId: int = None):
        super().__init__(
            npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
            cogTrack=cogTrack, cogType=cogType, zoneId=zoneId,
        )
        self.cogAmount = cogAmount
        self.executive = executive

    def calculateProgress(self, context: BossbotBossContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not BossbotBossContext:
            return 0
        if self.cogTrack is not None and self.cogTrack != context.getCogTrack():
            return 0
        if self.executive:
            return context.getExesFed()
        return context.getDinersFed()
    
    def getCompletionRequirement(self) -> int:
        return self.cogAmount

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
            return None  # no club quests for this objective
        else:
            return 3, None

    @classmethod
    def generateFromDifficulty(cls, rng: random.Random, difficulty: float, questSource: QuestSource, **extraArgs):
        """
        Given an arbitrary difficulty value, generate a QuestObjective.
        For more info, seek QuestGenerator.py.

        :param rng:        A seeded Random instance. Use this for .random() or .randint() calculations.
        :param difficulty: The arbitrary difficulty of the task.
        :return:           This QuestObjective, set with values to match the arbitrary difficulty.
        """
        # Set initial parameters.
        cogAmount = 0.7 * (difficulty ** 1.4) * lerp(0.9, 1.1, rng.random())
        executive = rng.random() <= 0.05

        # Cut down on the amount of diners if they're executive.
        if executive:
            cogAmount *= 0.33
        
        # Round off our cog count so that it is pretty.
        cogAmount = math.ceil(cogAmount)
        if cogAmount < 1:
            cogAmount = 1
        elif cogAmount < 10:
            pass
        else:
            cogAmount = round(round(cogAmount / 2) * 2)

        # Return our objective.
        return cls(
            cogAmount=math.ceil(cogAmount),
            cogType='ceo',
            cogTrack='c',
            npcReturnable=False,
            executive=executive
        )

    def getLowestToonLevel(self) -> Optional[int]:
        return 68

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Feed
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.cogAmount == 1:
            return ''
        return PROG_Feed.format(value=min(progress, self.cogAmount), range=self.cogAmount)

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        oilCan = poster.LEFT
        stomach = poster.RIGHT

        banquetIcons = loader.loadModel('phase_12/models/bossbotHQ/BanquetIcons')
        oilCanGeom = banquetIcons.find("**/Food")
        stomachGeom = banquetIcons.find("**/Hunger")
        banquetIcons.removeNode()

        if self.executive:
            stomachGeom.setColorScale(0.2, 0.2, 0.2, 1)

        poster.visual_setFrameColor(oilCan, 'orange')
        poster.visual_setFrameText(oilCan, f"Feed {self.cogAmount} Oil Cans")
        poster.visual_setFrameGeom(oilCan, oilCanGeom, scale=0.35)

        poster.visual_setAuxText(AuxillaryText_To)
        poster.label_auxillaryText.show()

        if not (complete and self.npcReturnable):
            poster.visual_setFrameColor(stomach, 'orange')

            if self.executive:
                hungerText = "Hungry Executive Diners"  # :)
            else:
                hungerText = "Hungry Diners"

            poster.visual_setFrameText(stomach, hungerText)
            poster.visual_setFrameGeom(stomach, stomachGeom, scale=0.35)

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
        return questReference.getQuestProgress(self.objectiveIndex), self.cogAmount, PROG_Feed
    
    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        cogName = "Hungry Executive Diners" if self.executive else "Hungry Diners"
        locString = TTLocalizer.AvatarDetailPanelDynamicZoneLocations[7]
        return SC_Feed % (f"{self.cogAmount} {cogName.lower()}", f"in the {locString}"),

    def getObjectiveGoal(self) -> str:
        return OBJ_Feed % f"{self.cogAmount} {'Executive ' if self.executive else ''}Diners"

    """text makin methods"""

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.cogAmount != 1:
            kwargstr += f'cogAmount={self.cogAmount}, '
        kwargstr += f'executive={self.executive}'
        return kwargstr


FeedDinerObjective()  # thanks m ai n
