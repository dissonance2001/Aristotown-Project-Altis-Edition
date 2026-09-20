from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.objectives.DefeatCogObjective import DefeatCogObjective
from toontown.quest3.SpecialQuestZones import SpecialQuestZones as SQZ
from toontown.quest3.QuestLocalizer import PROG_Defeat, SC_DefeatLocation, QuestProgress_Complete, PFX_DEFEAT, OBJ_Defeat
from toontown.toonbase import ToontownGlobals


DirectorsString = 'the Directors'
PosterInfo = (
    ('dopa', ''),
    ('dold', PFX_DEFEAT + DirectorsString),
    ('derrhand', '')
)


class DefeatDirectorsObjective(DefeatCogObjective):
    def __init__(self,
                 npc=2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None):
        super().__init__(npc=npc,
                         rewards=rewards,
                         nextStep=nextStep,
                         npcReturnable=npcReturnable,
                         zoneUnlocks=zoneUnlocks,
                         cogCount=1,
                         cogLocation=SQZ.CeosOffice,
                         cogType='dopa',
                         cogLevelMin=None,
                         cogTrack=None,
                         skelecog=False,
                         virtual=False,
                         revives=False,
                         executive=False,
                         manager=False,
                         boss=False)

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        # We do not want this quest to be appearing in random generation
        return None

    def doesLocationCount(self, zoneId):
        if zoneId == ToontownGlobals.BossbotHQ:
            return True

        return False

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)

        for i, cogPoster in enumerate((poster.LEFT, poster.CENTER, poster.RIGHT)):
            self.setCogFrame(cogPoster, poster, cogType=PosterInfo[i][0], forceName=PosterInfo[i][1])

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_hideFrame(poster.CENTER)
                poster.visual_setFrameText(poster.LEFT, DirectorsString)
                # Do this again to clear the silhouette
                poster.visual_setSuitHead(poster.LEFT, 'dopa')
                poster.visual_setFrameColor(poster.RIGHT, 'red')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        # And if we're not, show progress
        else:
            value, range, textFormat = self.getProgressFormat(questReference)
            poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete

        return PROG_Defeat.format(value=0, range=3)

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), 3, PROG_Defeat

    def getObjectiveGoal(self) -> str:
        return OBJ_Defeat % 'the Directors'

    def setCogFrame(self, cogPoster, poster, declarative=False, cogType='dopa', forceName=None):
        poster.visual_setFrameColor(cogPoster, 'red')
        nameText = forceName if forceName is not None else self.getCogNameString(declarative=declarative, count=self.cogCount)
        poster.visual_setFrameText(cogPoster, nameText)
        # Make an suit head uwu
        poster.visual_setSuitHead(cogPoster, cogType, silhouette=True)

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        message = SC_DefeatLocation
        locName = self.getLocationName(zoneId=self.cogLocation)
        return message % (DirectorsString, locName),
