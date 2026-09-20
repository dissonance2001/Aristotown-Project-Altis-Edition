import math

from direct.gui.OnscreenImage import OnscreenImage

from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import AuxillaryText_Complete, AuxillaryText_With, HL_Collect, PROG_Collect, QuestProgress_Complete, SC_Collect
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.context.CogBossContext import LawbotBossContext
from ..daily.DailyConstants import QuestTier
from toontown.quest3.objectives.CogBossObjective import CogBossObjective
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, \
    DaisyGardens, MinniesMelodyland


class CollectSoundObjective(CogBossObjective):

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 evidence: int = 1,
                 cogTrack: str = None,
                 cogType: str = None,
                 zoneId: int = None):
        super().__init__(
            npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
            cogTrack=cogTrack, cogType=cogType, zoneId=zoneId,
        )
        self.evidence = evidence

    def calculateProgress(self, context: LawbotBossContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not LawbotBossContext:
            return 0
        if self.cogTrack is not None and self.cogTrack != context.getCogTrack():
            return 0
        return context.getEvidence()
    
    def getCompletionRequirement(self) -> int:
        return self.evidence

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
        evidence = 3 * (difficulty ** 1.6)

        # Round off our evidence count so that it is pretty.
        evidence = math.ceil(evidence)
        if evidence < 1:
            evidence = 1
        elif evidence < 10:
            pass
        elif evidence < 20:
            evidence = round(round(evidence / 2) * 2)
        elif evidence < 200:
            evidence = round(round(evidence / 5) * 5)
        elif evidence < 500:
            evidence = round(round(evidence / 10) * 10)
        elif evidence < 2000:
            evidence = round(round(evidence / 50) * 50)
        else:
            evidence = round(round(evidence / 100) * 100)

        # Add some variability to the evidence counts
        if rng.random() > 0.5:
            if evidence > 20 and evidence < 100:
                evidence += rng.choice((5, 0))
            elif evidence < 400:
                evidence += rng.choice((5, 10, 15))
            elif evidence >= 400:
                evidence += rng.choice((25, 45, 65, 80))

        # Return our objective.
        return cls(
            evidence=math.ceil(evidence),
            cogType='clo',
            cogTrack='l',
            npcReturnable=False,
        )

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Collect
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.evidence == 1:
            return ''
        return PROG_Collect.format(value=min(progress, self.evidence), range=self.evidence)
    
    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        cogPoster = poster.LEFT

        evidenceTex = loader.loadTexture('phase_11/maps/paper_rain.png')
        evidenceTex.setMinfilter(Texture.FTLinearMipmapLinear)
        evidenceTex.setMagfilter(Texture.FTLinear)

        evidenceIcon = OnscreenImage(image=evidenceTex)
        evidenceIcon.setTransparency(1)
        poster.visual_setFrameGeom(cogPoster, evidenceIcon, scale=0.06)
        poster.visual_setFrameColor(cogPoster, 'orange')
        poster.visual_setFrameText(cogPoster, f"Collect {self.evidence} Sound Evidence")

        poster.visual_setAuxText(AuxillaryText_With)
        poster.label_auxillaryText.show()

        if not (complete and self.npcReturnable):
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
        return questReference.getQuestProgress(self.objectiveIndex), self.evidence, PROG_Collect
    
    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        locString = TTLocalizer.AvatarDetailPanelDynamicZoneLocations[6]
        return SC_Collect % ("some sound evidence", f" in the {locString}"),

    """text makin methods"""

    def getCogNameString(self, forcePlural=False, declarative=True, speedchat=False, count=0):
        nameSingle, _ = TTLocalizer.BossNames[self.cogTrack]
        return nameSingle

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.evidence != 1:
            kwargstr += f'evidence={self.evidence}, '
        return kwargstr


CollectSoundObjective()  # thanks m ai n
