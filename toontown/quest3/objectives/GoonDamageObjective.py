import math
from typing import Optional

from toontown.clashsuit.suit import BossCogGlobals
from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import AuxillaryText_Against, AuxillaryText_Complete, HL_Damage, PROG_Damage, \
    QuestProgress_Complete, SC_Damage, SC_DamageWeapon
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.context.CogBossContext import CashbotBossContext
from ..daily.DailyConstants import QuestTier
from toontown.quest3.objectives.DamageBossObjective import DamageBossObjective
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, \
    DaisyGardens


class GoonDamageObjective(DamageBossObjective):
    AllowUnstunnedGoonZones = (
        ToontownGlobals.OutdoorZone,
        ToontownGlobals.DonaldsDreamland
    )

    def __init__(self,
                 npc=2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 damageAmount: int = 1,
                 unstunned: bool = False,
                 cogTrack: str = None,
                 cogType: str = None,
                 zoneId: int = None):
        super().__init__(
            npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
            damageAmount=damageAmount, cogTrack=cogTrack, cogType=cogType, zoneId=zoneId,
        )
        self.unstunned = unstunned

    def calculateProgress(self, context: CashbotBossContext, questReference: QuestReference, quester: Quester) -> int:
        if not isinstance(context, CashbotBossContext):
            return 0
        if self.cogTrack is not None and self.cogTrack != context.getCogTrack():
            return 0
        return context.getUnstunnedGoonDamage() if self.unstunned else context.getTotalGoonDamage()

    def getCompletionRequirement(self) -> int:
        return self.damageAmount

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        # Actually people hate these so remove all generation for these
        return None

        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock, YeOlde, DaisyGardens):
                return None
        elif questSource == QuestSource.DailyQuest:
            questTier = extraArgs.get("questTier")
            if questTier in (QuestTier.NEWBIE, QuestTier.TTC, QuestTier.BB, QuestTier.YOTT,
                             QuestTier.DG):
                return None

        if questerType == QuesterType.Toon:
            return 3, None
        elif questerType == QuesterType.Club:
            return 25, None
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
        averageBossHp = BossCogGlobals.CashbotBossMaxDamage[1]
        damageAmount = int(averageBossHp * 0.45) * (difficulty ** 1.3) // 40

        # Chance for it to ask for unstunned goons specifically, in later playgrounds
        unstunned = False
        if extraArgs.get('zoneId') in cls.AllowUnstunnedGoonZones and rng.random() < 0.2:
            unstunned = True
            damageAmount *= 0.25

        if questSource == QuestSource.ClubQuest:
            damageAmount *= 0.5

        # Round off our damage count so that it is pretty.
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
            unstunned=unstunned,
            cogType='cfo',
            cogTrack='m',
            npcReturnable=False,
        )

    def getLowestToonLevel(self) -> Optional[int]:
        return 48

    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        return 6

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Damage

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.damageAmount == 1:
            return ''
        return PROG_Damage.format(value=min(progress, self.damageAmount), range=self.damageAmount)

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        cogPoster = poster.RIGHT if not (complete and self.npcReturnable) else poster.LEFT
        self.setCogFrame(cogPoster, poster)

        if not (complete and self.npcReturnable):
            goon = loader.loadModel('phase_9/models/char/Cog_Goonie-zero')
            geom = goon.find('**/joint8')
            geom.find('**/security_hat').hide()
            poster.visual_setFrameGeom(poster.LEFT, geom, scale=0.08, pos=(0, 10, -0.025))
            poster.visual_setFrameColor(poster.LEFT, 'orange')
            poster.visual_setFrameText(poster.LEFT, f'Deal {self.damageAmount}{" Unstunned" if self.unstunned else ""} Goon Damage')

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
        return questReference.getQuestProgress(self.objectiveIndex), self.damageAmount, PROG_Damage

    @property
    def weaponType(self):
        return "an unstunned goon" if self.unstunned else "a goon"

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        cogName = self.getCogNameString()
        return SC_DamageWeapon % (self.damageAmount, cogName, self.weaponType),


GoonDamageObjective()  # thanks m ai n
