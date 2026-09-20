import math

from toontown.quest3.QuestEnums import QuesterType, QuestSource
from toontown.quest3.QuestLocalizer import HL_Stomp, PROG_Stomp, QuestProgress_Complete, SC_Stomp
from toontown.quest3.base.QuestObjective import QuestObjective
from toontown.quest3.base.QuestReference import QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.quest3.context.StompGoonContext import StompGoonContext
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from ..daily.DailyConstants import QuestTier
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import ToontownCentral, DonaldsDock, YeOlde, DaisyGardens, \
    SpecialQuestCogHQZones2Facility, CashbotLobby


class StompGoonObjective(QuestObjective):
    zoneIdMods = {
        None: 1.5,
        SpecialQuestZones.SellbotFactory: 0.5,
        SpecialQuestZones.CashbotMints: 0.8,
        CashbotLobby: 1.0,
    }

    def __init__(self,
                 npc = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 zoneUnlocks=None,
                 goons: int = 1,
                 zoneId: int = None):
        super().__init__(
            npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable, zoneUnlocks=zoneUnlocks,
        )
        self.goons = goons
        self.zoneId = zoneId

    def calculateProgress(self, context: StompGoonContext, questReference: QuestReference, quester: Quester) -> int:
        if type(context) is not StompGoonContext:
            return 0
        if self.zoneId is not None and not self.checkLocation(context):
            return 0
        return context.getGoonsStomped()

    def checkLocation(self, context: StompGoonContext):
        if self.zoneId == context.getZoneId():
            return True
        elif context.getZoneId() in SpecialQuestCogHQZones2Facility.get(self.zoneId, []):
            return True
        return False

    def getCompletionRequirement(self) -> int:
        return self.goons

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
        goons = 1.4 * (difficulty ** 1.4)

        if extraArgs.get('zoneId') == DaisyGardens:
            zoneId = SpecialQuestZones.SellbotFactory
        else:
            zoneIdChoices = {
                None: 75,
                SpecialQuestZones.SellbotFactory: 20,
                SpecialQuestZones.CashbotMints: 40,
                CashbotLobby: 120,
            }
        
            zoneId = rng.choices(list(zoneIdChoices), list(zoneIdChoices.values()))[0]

        # Use the goon amount modifier based on the zone id.
        goons *= cls.zoneIdMods.get(zoneId, 1)

        # Round off our goon count so that it is pretty.
        goons = math.ceil(goons)
        if goons < 1:
            goons = 1
        elif goons < 10:
            pass
        else:
            goons = round(round(goons / 2) * 2)

        # Return our objective.
        return cls(
            goons=math.ceil(goons),
            zoneId=zoneId,
            npcReturnable=False,
        )

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Stomp
    
    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.goons == 1:
            return ''
        return PROG_Stomp.format(value=min(progress, self.goons), range=self.goons)
    
    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            # Return the goal location
            return super().getInfoTextStrings(questReference)

        locations = TTLocalizer.AvatarDetailPanelDynamicZoneLocations
        if self.zoneId == CashbotLobby:
            return locations[5],

        return self.getLocationName(self.zoneId),
    
    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)
        cogPoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        goon = loader.loadModel('phase_9/models/char/Cog_Goonie-zero')
        geom = goon.find('**/joint8')
        geom.find('**/security_hat').hide()
        poster.visual_setFrameGeom(cogPoster, geom, scale=0.08, pos=(0, 10, -0.025))
        poster.visual_setFrameColor(cogPoster, 'blue')
        poster.visual_setFrameText(cogPoster, f"Stomp {self.goons} Goons")
        goon.removeNode()

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
        return questReference.getQuestProgress(self.objectiveIndex), self.goons, PROG_Stomp
    
    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            if self.npcReturnable:
                return self.getFinishToontaskStrings()
            return tuple()

        # Get the message formatting.
        if self.zoneId == CashbotLobby:
            locations = TTLocalizer.AvatarDetailPanelDynamicZoneLocations
            locString = f" in the {locations[5]}"
        elif self.zoneId is not None:
            locString = self.getLocationName(self.zoneId)
        else:
            locString = ''

        return SC_Stomp % ("some goons", locString),

    """text makin methods"""

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.goons != 1:
            kwargstr += f'goons={self.goons}, '
        if self.zoneId:
            kwargstr += f'cogLocation={self._numToLocStr(self.zoneId)}, '
        return kwargstr


StompGoonObjective()  # thanks m ai n
