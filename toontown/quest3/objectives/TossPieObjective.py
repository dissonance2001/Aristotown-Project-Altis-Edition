import math

from direct.gui.OnscreenImage import OnscreenImage

from toontown.quest3.base.QuestObjective import *
from toontown.quest3.context.NPCInteractContext import NPCInteractContext
from toontown.quest3.context.TossPieContext import TossPieContext
from toontown.quest3.objectives import VisitObjective
from toontown.quest3.QuestLocalizer import HL_Throw, OBJ_Throw, PROG_Throw, QuestProgress_Complete, SC_ThrowPies, \
    PFX_THROW
from toontown.clashbattle.battle.BattleGlobals import AvPropsNew, AvPropStringsPlural, AvPropStringsSingular
from toontown.toonbase.ToontownGlobals import DonaldsDock, YeOlde, ToontownCentral


class TossPieObjective(VisitObjective):

    def __init__(self,
                 npc: int = 2001,
                 rewards=None,
                 nextStep=None,
                 npcReturnable: bool = True,
                 pieType: int = None,
                 pieAmount: int = 10,
                 zoneId: int = None,
                 restock: bool = True):
        super().__init__(npc=npc, rewards=rewards, nextStep=nextStep, npcReturnable=npcReturnable)
        self.pieType = pieType
        self.pieAmount = pieAmount
        self.zoneId = zoneId
        self.restock = restock

    def calculateProgress(self, context: QuestContext, questReference: QuestReference, quester: Quester) -> int:
        """This quest type is fairly unique, as it requires interacting with the NPC to restock pies,
        as well as tossing said pies. This function accounts for both actions. While interacting
        doesn't progress the objective, tossing the pies does.
        """
        if type(context) is NPCInteractContext:
            # Do not give them pies if the restock flag is false.
            if not self.restock:
                return 0

            result = super().calculateProgress(context, questReference, quester)

            # This is the correct NPC, restock our pies.
            if result:
                quester.b_setPieType(self.pieType)
                quester.b_setNumPies(self.pieAmount)
        elif type(context) is TossPieContext:
            # A pie type was described, but the context doesn't match.
            if self.pieType is not None and context.getPieType() != self.pieType:
                return 0
            if self.zoneId is not None and context.getZoneId() != self.zoneId:
                return 0
            # We threw a pie! Great.
            return context.getPieAmount()
        
        return 0
    
    @staticmethod
    def getDifficultyRange(questerType: QuesterType, questSource: QuestSource, **extraArgs):
        if questSource == QuestSource.KudosQuest:
            zoneId = extraArgs.get("zoneId")
            if zoneId in (ToontownCentral, DonaldsDock, YeOlde):
                return None

        if questerType == QuesterType.Toon:
            return 3, None
        elif questerType == QuesterType.Club:
            return None  # Die
        else:
            return 3, None
    
    @staticmethod
    def getObjectiveWeight(questerType: QuesterType) -> int:
        """
        The likelihood for this objective to be chosen in a pool.
        The de facto amount is 100.
        """
        return 5

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
        pies = 2.0 * (difficulty ** 1.7)

        # Only use the VP for pie toss random kudos quests
        pieType = 4
        zoneId = SpecialQuestZones.SellbotBoss

        # Round off our goon count so that it is pretty.
        pies = math.ceil(pies)
        if pies < 1:
            pies = 1
        elif pies < 10:
            pass
        elif pies < 20:
            pies = round(round(pies / 2) * 2)
        elif pies < 200:
            pies = round(round(pies / 5) * 5)
        elif pies < 500:
            pies = round(round(pies / 10) * 10)
        elif pies < 2000:
            pies = round(round(pies / 50) * 50)
        else:
            pies = round(round(pies / 100) * 100)
        
        # Add some variability to the evidence counts
        if rng.random() > 0.5:
            if pies > 20 and pies < 100:
                pies += rng.choice((5, 0))
            elif pies < 400:
                pies += rng.choice((5, 10, 15))
            elif pies >= 400:
                pies += rng.choice((25, 45, 65, 80))

        # Return our objective.
        return cls(
            pieAmount=math.ceil(pies),
            zoneId=zoneId,
            npcReturnable=False,
            pieType=pieType,
            restock=False,
        )

    def getPieInfo(self, pieType):
        if pieType >= 10:
            gui = loader.loadModel("gui/common/models/cc_m_txc_gui_icon_throwables")
            geom = gui.find('**/snowball_1')
            gui.removeNode()
            scale = 0.075
            text = "a Snowball" if self.pieAmount == 1 else "Snowballs"
        elif pieType == 9:
            gui = loader.loadModel("gui/common/models/cc_m_txc_gui_icon_throwables")
            geom = gui.find('**/pineapple_1')
            gui.removeNode()
            scale = 0.15
            text = "a Pineapple" if self.pieAmount == 1 else "Pineapples"
        elif pieType == 8:
            gui = loader.loadModel('gui/common/models/cc_m_txc_gui_icon_throwables')
            geom = gui.find('**/summons_1')
            gui.removeNode()
            scale = 0.1
            text = "Evidence"
        else:
            gui = loader.loadModel('phase_3.5/models/gui/inventory_icons')
            geom = gui.find('**/' + AvPropsNew[6][pieType])
            gui.removeNode()
            scale = 1

            if self.pieAmount == 1:
                text = AvPropStringsSingular[6][pieType]
            else:
                text = AvPropStringsPlural[6][pieType]

        return geom, scale, text

    def modifyPoster(self, questReference: QuestReference, poster):
        complete = questReference.isQuestComplete(base.localAvatar, self.objectiveIndex)

        # No pie was specified, pick a random one.
        if self.pieType is None:
            pie = random.randint(0, 7)
        else:
            pie = self.pieType

        geom, scale, text = self.getPieInfo(pie)

        piePoster = poster.CENTER if not (complete and self.npcReturnable) else poster.LEFT

        poster.visual_setFrameGeom(piePoster, geom=geom, scale=scale)
        poster.visual_setFrameColor(piePoster, 'lightBlue')

        if self.pieAmount == 1:
            text = f'a {text}'
        else:
            text = f'{self.pieAmount} {text}'
        poster.visual_setFrameText(piePoster, PFX_THROW + text)

        # If we're complete, bonus info
        if complete:
            if self.npcReturnable:
                poster.visual_setFrameColor(poster.RIGHT, 'lightBlue')
                poster.visual_setNpcFrame(poster.RIGHT, self.getToNpcId())
                poster.visual_setFrameText(poster.RIGHT, self.getToNpcName())
                poster.label_auxillaryText.show()
        # And if we're not, show progress
        else:
            if self.pieAmount > 1:
                value, range, textFormat = self.getProgressFormat(questReference)
                poster.visual_setProgressInfo(value=value, range=range, textFormat=textFormat)

    def getProgressFormat(self, questReference):
        return questReference.getQuestProgress(self.objectiveIndex), self.pieAmount, PROG_Throw

    def getSpeedchatMessages(self, quester, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(quester, self.objectiveIndex):
            return tuple()
        if self.restock:
            return tuple([SC_ThrowPies] + list(self.getFinishToontaskStrings()))
        return SC_ThrowPies,
    
    def getInfoTextStrings(self, questReference: QuestReference) -> tuple:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex) and self.npcReturnable:
            # Return the goal location
            return super().getInfoTextStrings(questReference)

        if self.restock:
            return f"See {TTLocalizer.NPCToonNames[self.getFromNpcId()]} for more {self.getPieName()}!", \
                self.getFromNpcBuildingName(), self.getFromNpcStreetName()

        return self.getLocationName(self.zoneId),

    def getHeadline(self, questReference: QuestReference, objectiveSelected: int = 0) -> str:
        return HL_Throw
    
    def getCompletionRequirement(self) -> int:
        return self.pieAmount
    
    """
    Text methods
    """

    def getPieName(self) -> str:
        if self.pieType is None:
            return "throwables"

        pie = self.pieType

        if self.pieType >= 10:
            return "Snowballs"
        elif self.pieType == 9:
            return "Pineapples"
        elif self.pieType == 8:
            return "Evidence"

        return AvPropStringsPlural[6][pie]
    
    def getObjectiveGoal(self) -> str:
        return OBJ_Throw % f"some {self.getPieName()}"

    def getProgressString(self, questReference: QuestReference, progress: int) -> str:
        if questReference.isQuestComplete(base.localAvatar, self.objectiveIndex):
            return QuestProgress_Complete
        elif self.pieAmount == 1:
            return ''
        return PROG_Throw.format(value=min(progress, self.pieAmount), range=self.pieAmount)

    def _getKwargStr(self):
        kwargstr = super()._getKwargStr()
        if self.pieType is not None:
            kwargstr += f'pieType={self.pieType}, '
        if self.pieAmount != 10:
            kwargstr += f'pieAmount={self.pieAmount}, '
        return kwargstr

    def __repr__(self):
        return f'TossPieObjective({self._getKwargStr()[:-2]})'

