import math
import random
from typing import Optional

from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import AuxillaryText_Against, AuxillaryText_Complete, HL_Stun, PROG_Stun, QuestProgress_Complete, SC_Stun, OBJ_Stun
from toontown.quest3.base.QuestObjective import QuestObjective
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.context.CogBossContext import CogBossContext
from ..daily.DailyConstants import QuestTier
from toontown.quest3.objectives.CogBossObjective import CogBossObjective
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, \
    DaisyGardens, MinniesMelodyland, TheBrrrgh


class StunBossObjective(CogBossObjective):
    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 stunCount: int = 1,
                 cogTrack: str = None,
                 cogType: str = None,
                 zoneId: int = None):
        super().__init__(
            npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
            cogTrack=cogTrack, cogType=cogType, zoneId=zoneId,
        )
        self.stunCount = stunCount

    def calculateProgress(self, context: CogBossContext, questReference: QuestReference, quester: Quester) -> int:
        if not isinstance(context, CogBossContext):
            return 0
        if self.cogTrack is not None and self.cogTrack != context.getCogTrack():
            return 0
        return context.getStunCount()
    
    def getCompletionRequirement(self) -> int:
        return self.stunCount

    def getObjectiveGoal(self) -> str:
        type2Name = {'g': 'the Chairman',
                     'c': 'the CEO',
                     'l': 'the CLO',
                     'm': 'the CFO',
                     's': 'the VP'}
        bossName = type2Name.get(self.cogTrack, 'a boss')
        return OBJ_Stun % f"{bossName} {self.stunCount} times"

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock, YeOlde):
                return None
        elif questSource == QuestSource.DailyQuest:
            questTier = extraArgs.get("questTier")
            if questTier in (QuestTier.NEWBIE, QuestTier.TTC, QuestTier.BB, QuestTier.YOTT):
                return

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
        zoneId = extraArgs.get("zoneId")
        if zoneId == DaisyGardens:
            stunCount = 1
        else:
            stunCount = 0.035 * (difficulty ** 2.1) + rng.randint(-1, 1)
        stunCount = max(stunCount, 1)

        if questSource == QuestSource.ClubQuest:
            stunCount *= 0.125  # Drastically reduce the stuns required for clubs, the difficulty scales it way too aggressively

        if rng.random() < 0.5:
            if zoneId == DaisyGardens:
                eligibleDepts = ['s']
            elif zoneId == MinniesMelodyland:
                eligibleDepts = ['s', 'm']
            elif zoneId == TheBrrrgh:
                eligibleDepts = ['s', 'm', 'l']
            else: # todo: boardbot
                eligibleDepts = ['s', 'm', 'l', 'c']
            cogTrack = rng.choice(eligibleDepts)
        else:
            cogTrack = None
            stunCount = math.ceil(stunCount * 1.5) # 50% more stuns if universal

        type2Name = {'g': 'chairman',
                     'c': 'ceo',
                     'l': 'clo',
                     'm': 'cfo',
                     's': 'vp'}
        cogType = type2Name.get(cogTrack, None)

        # Return our objective.
        return cls(
            stunCount=math.ceil(stunCount),
            cogType=cogType,
            cogTrack=cogTrack,
            npcReturnable=False,
        )

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Stun

    def getLowestToonLevel(self) -> Optional[int]:
        return {
            's': 38,
            'm': 48,
            'l': 58,
            'c': 68,
            'g': 78,
        }.get(self.cogTrack)
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.stunCount == 1:
            return ''
        return PROG_Stun.format(value=min(progress, self.stunCount), range=self.stunCount)
    
    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        cogPoster = poster.RIGHT if not (complete and self.npcReturnable) else poster.LEFT
        self.setCogFrame(cogPoster, poster)

        if not (complete and self.npcReturnable):
            statusEffectImages = base.loader.loadModel('phase_3.5/models/gui/battlegui/status_effects')
            icon = statusEffectImages.find(f'**/confusion_icon')
            poster.visual_setFrameGeom(poster.LEFT, icon, 0.2)
            poster.visual_setFrameColor(poster.LEFT, 'orange')
            frameText = 'Get a Stun' if self.stunCount == 1 else f'Get {self.stunCount} Stuns'
            poster.visual_setFrameText(poster.LEFT, frameText)
            statusEffectImages.removeNode()
        
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
        elif self.stunCount > 1:
            value, range, textFormat = self.getProgressFormat(questReference)
            poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)
    
    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.stunCount, PROG_Stun
    
    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        cogName = self.getCogNameString()
        return SC_Stun % (cogName, f"{self.stunCount} time{'s' if self.stunCount > 1 else ''}"),

    """text makin methods"""

    def getCogNameString(self, forcePlural=False, declarative=True, speedchat=False, count=0):
        nameSingle, _ = TTLocalizer.BossNames[self.cogTrack]
        return nameSingle[0].upper() + nameSingle[1:]

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.stunCount != 1:
            kwargstr += f'stunCount={self.stunCount}, '
        return kwargstr


StunBossObjective()  # thanks m ai n
