from enum import IntEnum
import math

from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import AuxillaryText_Complete, AuxillaryText_With, HL_Destroy, \
    PROG_Destroy, QuestProgress_Complete, SC_Destroy, PFX_DESTROY, OBJ_Destroy
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.context.CogBossContext import LawbotBossContext
from ..daily.DailyConstants import QuestTier
from toontown.quest3.objectives.CogBossObjective import CogBossObjective
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, \
    DaisyGardens, MinniesMelodyland


class DestroyLawyerObjective(CogBossObjective):

    class ActiveRounds(IntEnum):
        CANNON = 0
        FINAL = 1

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 lawyers: int = 1,
                 executive: bool=False,
                 cogTrack: str = None,
                 cogType: str = None,
                 zoneId: int = None,
                 activeRound: ActiveRounds = ActiveRounds.CANNON):
        super().__init__(
            npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
            cogTrack=cogTrack, cogType=cogType, zoneId=zoneId,
        )
        self.lawyers = lawyers
        self.executive = executive
        self.activeRound = activeRound

    def calculateProgress(self, context: LawbotBossContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not LawbotBossContext:
            return 0
        if self.cogTrack is not None and self.cogTrack != context.getCogTrack():
            return 0
        if self.executive:
            return context.getExesDestroyed(self.activeRound)
        return context.getCogsDestroyed(self.activeRound)
    
    def getCompletionRequirement(self) -> int:
        return self.lawyers

    def getObjectiveGoal(self) -> str:
        return OBJ_Destroy % f"{self.lawyers} {'executive ' if self.executive else ''}lawyers with {'sound' if self.activeRound == self.ActiveRounds.FINAL else 'a cannon'}"

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock, YeOlde, DaisyGardens,
                          MinniesMelodyland):
                return None
        elif questSource == QuestSource.DailyQuest:
            questTier = extraArgs.get("questTier")
            if questTier in (QuestTier.NEWBIE, QuestTier.TTC, QuestTier.BB, QuestTier.YOTT,
                             QuestTier.DG, QuestTier.MML):
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
        lawyers = 1.5 * (difficulty ** 1.5)

        # Pick the CLO active round that this quest should apply to.
        activeRound = rng.choice([cls.ActiveRounds.CANNON, cls.ActiveRounds.FINAL])

        # Lower the requirement for cannon round quests.
        if activeRound == cls.ActiveRounds.CANNON:
            lawyers *= 0.7

        executive = rng.random() <= min(0.01 * difficulty, 0.3)

        # Lower the requirement for executive quests.
        if executive:
            lawyers *= 0.33

        # Round off our cog count so that it is pretty.
        lawyers = math.ceil(lawyers)
        if lawyers < 1:
            lawyers = 1
        elif lawyers < 10:
            pass
        elif lawyers < 20:
            lawyers = round(round(lawyers / 2) * 2)
        elif lawyers < 200:
            lawyers = round(round(lawyers / 5) * 5)
        elif lawyers < 500:
            lawyers = round(round(lawyers / 10) * 10)
        elif lawyers < 2000:
            lawyers = round(round(lawyers / 50) * 50)
        else:
            lawyers = round(round(lawyers / 100) * 100)
        
        # Add some variability to the evidence counts
        if rng.random() > 0.5:
            if lawyers > 20 and lawyers < 100:
                lawyers += rng.choice((5, 0))
            elif lawyers < 400:
                lawyers += rng.choice((5, 10, 15))
            elif lawyers >= 400:
                lawyers += rng.choice((25, 45, 65, 80))

        # Return our objective.
        return cls(
            lawyers=math.ceil(lawyers),
            executive=executive,
            cogType='clo',
            cogTrack='l',
            activeRound=activeRound,
            npcReturnable=False,
        )

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Destroy
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.lawyers == 1:
            return ''
        return PROG_Destroy.format(value=min(progress, self.lawyers), range=self.lawyers)
    
    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        cogPoster = poster.LEFT

        crosshair = loader.loadModel('phase_11/models/gui/cog_crosshair')
        crosshair.setDepthTest(0)
        crosshair.setDepthWrite(0)
        if self.executive:
            crosshair.setColorScale(0.2, 0.2, 0.2, 1)
        poster.visual_setFrameGeom(cogPoster, crosshair, scale=0.13)
        crosshair.removeNode()
        poster.visual_setFrameColor(cogPoster, 'orange')

        frameText = f"{self.lawyers} Executive Lawyers" if self.executive else f"{self.lawyers} Lawyers"
        poster.visual_setFrameText(cogPoster, PFX_DESTROY + frameText)

        poster.visual_setAuxText(AuxillaryText_With)
        poster.label_auxillaryText.show()

        if not (complete and self.npcReturnable):
            if self.activeRound == self.ActiveRounds.FINAL:
                geom = base.localAvatar.inventory.buttonLookup(3, 6)  # Foghorn
                poster.visual_setFrameGeom(poster.RIGHT, geom, scale=1)
                poster.visual_setFrameColor(poster.RIGHT, 'orange')
                poster.visual_setFrameText(poster.RIGHT, "Sound Evidence")
            else:
                cannon = loader.loadModel('phase_4/models/minigames/toon_cannon')
                cannon.find('**/cannon').setHpr(0, 45, 0)
                poster.visual_setFrameGeom(poster.RIGHT, cannon, scale=0.017, pos=(-0.02, 10, -0.065), hpr=(-90, 0, 0))
                poster.visual_setFrameColor(poster.RIGHT, 'orange')
                poster.visual_setFrameText(poster.RIGHT, "A Cannon")

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
        return questReference.getQuestProgress(self.objectiveIndex), self.lawyers, PROG_Destroy
    
    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        locString = TTLocalizer.AvatarDetailPanelDynamicZoneLocations[6]
        cogText = "some executive lawyers" if self.executive else "some lawyers"
        weapon = "a cannon" if self.activeRound == self.ActiveRounds.CANNON else "sound evidence"
        return SC_Destroy % (cogText, f"in the {locString}", weapon),

    """text makin methods"""

    def getCogNameString(self, forcePlural=False, declarative=True, speedchat=False, count=0):
        nameSingle, _ = TTLocalizer.BossNames[self.cogTrack]
        return nameSingle

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.lawyers != 1:
            kwargstr += f'lawyers={self.lawyers}, '
        return kwargstr


DestroyLawyerObjective()  # thanks m ai n
