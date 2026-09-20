from enum import IntEnum
import math

from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import HL_Collect, PROG_Collect, PROG_Stomp, QuestProgress_Complete, SC_Collect, \
    OBJ_Collect
from toontown.quest3.base.QuestObjective import QuestObjective
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.quest3.context.CollectBarrelContext import CollectBarrelContext
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, DaisyGardens, \
    MinniesMelodyland, TheBrrrgh, SpecialQuestCogHQZones2Facility
from panda3d.core import NodePath


class CollectBarrelObjective(QuestObjective):
    zoneIdMods = {
        None: 1.1,
        SpecialQuestZones.SellbotFactory: 0.4,
        SpecialQuestZones.CashbotMints: 0.8,
        SpecialQuestZones.LawbotLawfices: 0.8,
        SpecialQuestZones.BossbotGolfCourses: 0.8,
    }

    # Constants for ease of use
    ALL = [SpecialQuestZones.SellbotFactory, SpecialQuestZones.CashbotMints, SpecialQuestZones.LawbotLawfices,
           SpecialQuestZones.BossbotGolfCourses]

    zoneId2Facilities = {
        DaisyGardens: [SpecialQuestZones.SellbotFactory],
        MinniesMelodyland: [SpecialQuestZones.SellbotFactory, SpecialQuestZones.CashbotMints],
        TheBrrrgh: [SpecialQuestZones.SellbotFactory, SpecialQuestZones.CashbotMints, SpecialQuestZones.LawbotLawfices],
    }

    class BarrelType(IntEnum):
        HEAL = 0
        GAG  = 1
        BEAN = 2

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 barrels: int = 1,
                 barrelType: BarrelType = None,
                 zoneId: int = None):
        super().__init__(
            npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
        )
        self.barrels = barrels
        self.barrelType = barrelType
        self.zoneId = zoneId

    def calculateProgress(self, context: CollectBarrelContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not CollectBarrelContext:
            return 0
        if self.zoneId is not None and not self.checkLocation(context):
            return 0

        barrelTypes = {
            self.BarrelType.HEAL: context.getHealBarrels(),
            self.BarrelType.GAG: context.getGagBarrels(),
            self.BarrelType.BEAN: context.getBeanBarrels(),
        }
        barrels = barrelTypes.get(self.barrelType)

        if barrels is not None:
            return barrels
    
        return sum(barrelTypes.values())

    def checkLocation(self, context: CollectBarrelContext):
        if self.zoneId == context.getZoneId():
            return True
        elif context.getZoneId() in SpecialQuestCogHQZones2Facility[self.zoneId]:
            return True
        return False

    def getCompletionRequirement(self) -> int:
        return self.barrels

    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock, YeOlde):
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
        return 6

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
        barrels = 1.0 * (difficulty ** 1.4)
        barrels += barrels * (rng.random() * rng.choice((-0.2, 0.2)))

        zoneIdChoices = [None] + cls.zoneId2Facilities.get(
            extraArgs.get('zoneId'), 
            cls.ALL
        )

        zoneId = rng.choices(list(zoneIdChoices), [(i + 1) ** -(difficulty / 10) for i in range(len(zoneIdChoices))])[0]

        # Use the goon amount modifier based on the zone id.
        barrels *= cls.zoneIdMods.get(zoneId, 1)

        # Choose a random barrel type.
        barrelTypes = [None] + list(cls.BarrelType)
        if zoneId == SpecialQuestZones.BossbotGolfCourses:
            barrelTypes.remove(cls.BarrelType.HEAL)
        if zoneId != SpecialQuestZones.SellbotFactory:
            barrelTypes.remove(cls.BarrelType.BEAN)
        barrelType = rng.choice(barrelTypes)

        if barrelType == cls.BarrelType.HEAL:
            barrels *= 0.2
        elif barrelType == cls.BarrelType.GAG:
            barrels *= 0.5
        elif barrelType == cls.BarrelType.BEAN:
            barrels *= 0.2

        # Round off our goon count so that it is pretty.
        barrels = math.ceil(barrels)
        if barrels < 1:
            barrels = 1
        elif barrels < 10:
            pass
        else:
            barrels = round(round(barrels / 2) * 2)

        # Return our objective.
        return cls(
            barrels=math.ceil(barrels),
            zoneId=zoneId,
            npcReturnable=False,
            barrelType=barrelType,
        )

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Collect

    def getObjectiveGoal(self) -> str:
        frameTexts = {
            self.BarrelType.HEAL: " Laff",
            self.BarrelType.GAG: " Gag",
            self.BarrelType.BEAN: " Bean",
        }
        frameText = f"{frameTexts.get(self.barrelType, '')} "
        if self.barrels == 1:
            frameText = f"Collect a{frameText}Barrel"
        else:
            frameText = f"Collect {self.barrels}{frameText}Barrels"

        return frameText

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.barrels == 1:
            return ''
        return PROG_Stomp.format(value=min(progress, self.barrels), range=self.barrels)
    
    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            # Return the goal location
            return super().getInfoTextStrings(questReference)

        if self.zoneId is None:
            return "Any Cog HQ",

        return self.getLocationName(self.zoneId),

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        cogPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        geom = loader.loadModel('phase_4/models/cogHQ/gagTank')
        poster.visual_setFrameGeom(cogPoster, geom, scale=0.05, pos=(0, 10, -0.058))
        poster.visual_setFrameColor(cogPoster, 'green')

        frameTexts = {
            self.BarrelType.HEAL: " Laff",
            self.BarrelType.GAG: " Gag",
            self.BarrelType.BEAN: " Bean",
        }
        frameText = f"{frameTexts.get(self.barrelType, '')} "
        if self.barrels == 1:
            frameText = f"Collect a{frameText}Barrel"
        else:
            frameText = f"Collect {self.barrels}{frameText}Barrels"

        poster.visual_setFrameText(cogPoster, frameText)

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'green')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        # And if we're not, show progress
        else:
            value, range, textFormat = self.getProgressFormat(questReference)
            poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)
    
    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.barrels, PROG_Collect
    
    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        if self.zoneId is not None:
            locString = self.getLocationName(self.zoneId)
        else:
            locString = ''

        return SC_Collect % ("some barrels", locString),

    """text makin methods"""

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.barrels != 1:
            kwargstr += f'barrels={self.barrels}, '
        if self.zoneId:
            kwargstr += f'cogLocation={self._numToLocStr(self.zoneId)}, '
        return kwargstr


CollectBarrelObjective()  # thanks m ai n
