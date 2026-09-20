import math

from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import HL_Stomp, PROG_Stomp, QuestProgress_Complete, SC_Stomp
from toontown.quest3.base.QuestObjective import QuestObjective
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.context.MoleStompContext import MoleStompContext
from toontown.quest3.context.StompGoonContext import StompGoonContext
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import BossbotCountryClubIntA, BossbotCountryClubIntB, BossbotCountryClubIntC, \
    ToontownCentral, DonaldsDock, YeOlde, DaisyGardens, MinniesMelodyland, TheBrrrgh


class MoleStompObjective(QuestObjective):
    zoneIdMods = {
        BossbotCountryClubIntA : 0.8,
        BossbotCountryClubIntB : 0.6,
        BossbotCountryClubIntC : 0.4,
    }

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 moles: int = 1,
                 zoneId: int = None):
        super().__init__(
            npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
        )
        self.moles = moles
        self.zoneId = zoneId

    def calculateProgress(self, context: MoleStompContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not MoleStompContext:
            return 0
        if self.zoneId is not None and self.zoneId != context.getZoneId():
            return 0
        return context.getMolesStomped()
    
    def getCompletionRequirement(self) -> int:
        return self.moles

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock, YeOlde, 
                          DaisyGardens, MinniesMelodyland, TheBrrrgh):
                return None

        if questerType == QuesterType.Toon:
            return 3, None
        elif questerType == QuesterType.Club:
            return None
        else:
            return 3, None
    
    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        """
        The likelihood for this objective to be chosen in a pool.
        The de facto amount is 100.
        """
        return 8

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
        moles = 1.3 * (difficulty ** 1.07)

        choices = {
            None                   : 100,
            BossbotCountryClubIntA : 0,  # 75,
            BossbotCountryClubIntB : 0,  # 50,
            BossbotCountryClubIntC : 0,  # 25,
        }

        zoneId = rng.choices(list(choices), list(choices.values()))[0]

        # Use the goon amount modifier based on the zone id.
        moles *= cls.zoneIdMods.get(zoneId, 1)

        # Round off our goon count so that it is pretty.
        moles = math.ceil(moles)
        if moles < 1:
            moles = 1
        elif moles < 10:
            pass
        elif moles < 20:
            moles = round(round(moles / 2) * 2)
        elif moles < 200:
            moles = round(round(moles / 5) * 5)
        elif moles < 500:
            moles = round(round(moles / 10) * 10)
        elif moles < 2000:
            moles = round(round(moles / 50) * 50)
        else:
            moles = round(round(moles / 100) * 100)
        
        # Add some variability to the evidence counts
        if rng.random() > 0.5:
            if 20 < moles < 100:
                moles += rng.choice((5, 0))
            elif moles < 400:
                moles += rng.choice((5, 10, 15))
            elif moles >= 400:
                moles += rng.choice((25, 45, 65, 80))

        # Return our objective.
        return cls(
            moles=math.ceil(moles),
            zoneId=zoneId,
            npcReturnable=False,
        )

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Stomp
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.moles == 1:
            return ''
        return PROG_Stomp.format(value=min(progress, self.moles), range=self.moles)
    
    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            # Return the goal location
            return super().getInfoTextStrings(questReference)

        return self.getLocationName(self.zoneId),
    
    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        cogPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        mole = loader.loadModel('phase_12/models/bossbotHQ/mole_cog')
        poster.visual_setFrameGeom(cogPoster, mole, scale=0.04, pos=(0, 10, -0.085))
        poster.visual_setFrameColor(cogPoster, 'blue')
        poster.visual_setFrameText(cogPoster, f"Stomp {self.moles} Red Moles")

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'blue')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        # And if we're not, show progress
        else:
            value, range, textFormat = self.getProgressFormat(questReference)
            poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)
    
    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.moles, PROG_Stomp
    
    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        locName = self.getLocationName(self.zoneId) if self.zoneId else ''

        # Get the message formatting.
        return SC_Stomp % ("some red moles", f"{locName}"),

    """text makin methods"""

    def getLocationName(self, zoneId: int = None, lowercaseAnywhere: bool = False):
        locName = super().getLocationName(zoneId=zoneId, lowercaseAnywhere=lowercaseAnywhere)
        if zoneId is None:
            locName = 'in any Cog Golf Course'

        return locName

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.moles != 1:
            kwargstr += f'moles={self.moles}, '
        if self.zoneId:
            kwargstr += f'zoneId={self._numToLocStr(self.zoneId)}, '
        return kwargstr


MoleStompObjective() # thanks m ai n
