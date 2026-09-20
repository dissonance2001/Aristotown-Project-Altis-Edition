from typing import Optional
from enum import Enum, auto

from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.clashbattle.battle import PassiveAttributeDefs
from panda3d.core import VBase4
import math

"""
A file to describe several base factors and definitions for each suit.
For where all of the suits actually get defined, look at SuitDefinitions.py
"""

### Several default definitions regarding suits. ###
ReviveDefaults = (0.5, 1.5)  # 0.5x damage, 1.5x damage multiplier

# Frequency Defaults (on the Suit itself). #
DefaultFreqLists = {  # default freqs
    1: (100),
    2: (50, 50),
    5: (50, 30, 10, 5, 5),
    7: (50, 10, 10, 10, 10, 5, 5),
    9: (40, 20, 10, 5, 5, 5, 5, 5, 5)
}
DefinedFreqLists = {
    'tier8': (50, 30, 15, 15, 10)  # Applies a lot of 5s afterwards in the class.
}
DefaultFreqEscalation = 5

### Several enums for definition usage. ###

# Hand Colors #
corpPolyColor = VBase4(0.95, 0.75, 0.75, 1.0)
legalPolyColor = VBase4(0.75, 0.75, 0.95, 1.0)
moneyPolyColor = VBase4(0.65, 0.95, 0.85, 1.0)
salesPolyColor = VBase4(0.95, 0.75, 0.95, 1.0)
boardPolyColor = VBase4(.45, 0.45, .45, 1.0)

# Body Size Definitions #
aSize = 6.06  # Size of body type 'a'
bSize = 5.29  # Size of body type 'b'
cSize = 4.14  # Size of body type 'c'

# Cog Type Enums #
BOARDBOT = 'g'
BOSSBOT = 'c'
LAWBOT = 'l'
CASHBOT = 'm'
SELLBOT = 's'
DEPARTMENT_ORDER = (BOARDBOT, BOSSBOT, LAWBOT, CASHBOT, SELLBOT)

# Body Type Enums #
SUIT_A = 'a'
SUIT_B = 'b'
SUIT_C = 'c'

# Body type to width coefficient.
# The higher the coefficient, the more battle space to reserve for the suit type.
SUIT_BODY_TYPE_WIDTH = {
    SUIT_A: 4.3,
    SUIT_B: 3.5,
    SUIT_C: 4.5,
}

# Skelecog Default Head Type Enums #
SKELE_HEAD_A = 'phase_5/models/char/suitA_skeleton_skull-zero'
SKELE_HEAD_B = 'phase_5/models/char/suitB_skeleton_skull-zero'
SKELE_HEAD_C = 'phase_5/models/char/suitC_skeleton_skull-zero'

ALL_SKELE_HEADS = (SKELE_HEAD_A, SKELE_HEAD_B, SKELE_HEAD_C)

# Tie Type Enums #
TIE_NONE = -1
TIE_BROAD = 0
TIE_SKINNY = 1
TIE_BOW = 2

# Body Tex Enums
TEX_BOARD = '**/suit_body_board_gen'
TEX_CORP = '**/suit_body_boss_gen'
TEX_LEGAL = '**/suit_body_law_gen'
TEX_MONEY = '**/suit_body_cash_gen'
TEX_SALES = '**/suit_body_sell_gen'

# Specialization Enums #
NORMAL = 0
DEFENSE = 1
ATTACK = 2


class BodyModelType(Enum):
    Normal = auto()
    Curvy = auto()
    HighCollar = auto()
    OpenShirt = auto()
    HighRoller = auto()
    LongCoat = auto()


BodyModelPathBase = 'phase_3.5/models/char/suit'
BodyModelTypeToPath = {
    BodyModelType.Normal: BodyModelPathBase + '{suitType}-mod',
    BodyModelType.Curvy: BodyModelPathBase + '{suitType}_f-mod',
    BodyModelType.HighCollar: BodyModelPathBase + '{suitType}_highcollar-mod',
    BodyModelType.OpenShirt: BodyModelPathBase + '{suitType}_open-mod',
    BodyModelType.HighRoller: BodyModelPathBase + '{suitType}_hroller-mod',
    BodyModelType.LongCoat: BodyModelPathBase + '{suitType}_longcoat-mod'
}

BodyModelTypeToUnemployedPath = {
    BodyModelType.HighCollar: 'phase_3.5/maps/ttcc_ene_suittex_highcollar_unemployed.png',
}


### Dictionaries of information in this file. ###
SuitDefinitions = {}
MainlineCogs = {BOARDBOT: [], BOSSBOT: [], LAWBOT: [], CASHBOT: [], SELLBOT: []}

BountyGroupsToCogs = {}


class SuitDefinition:
    """
    A Suit Definition object, which hosts all information and data on a given suit.
    """

    def __init__(self, name: str, cogType: str, bodyHeight: float, specialization: int = NORMAL, miniboss: bool = False,
                 isMainline: bool = False, onRadar: bool = False, isMerc: bool = False, nerfDamageForExe: bool = False,
                 isFemale: bool = False, spawnsInInvasion: bool = False, departmentOverride: str = None,
                 hideDepartment: bool = False, cogTier: Optional[int] = None):
        # Initial definitions
        self.name = name
        self.cogType = cogType
        self.bodyHeight = bodyHeight
        self.miniboss = miniboss
        self.specialization = specialization
        self.nerfDamageForExe = nerfDamageForExe  # nerfs all damage by 20% in case this suit is a miniboss
        self.cogTier = cogTier
        # Body model may be overriden in defineParts
        self.bodyModelType = BodyModelType.Curvy if isFemale else BodyModelType.Normal

        # Mainline cogs are the 8 suits that make up the 'default' promotion tree.
        # They must be defined in order.
        self.isMainline = isMainline
        self.__exception("Defined cog had non-existent type!", self.cogType not in list(MainlineCogs.keys()))
        if isMainline:
            MainlineCogs[self.cogType].append(self.name)
        self.onRadar = onRadar
        self.isMerc = isMerc
        self.isFemale = isFemale
        self.spawnsInInvasion = spawnsInInvasion
        self.departmentOverride = departmentOverride
        self.hideDepartment = hideDepartment

        self.__exception("Suit name already taken!", name in SuitDefinitions)
        SuitDefinitions[name] = self

        # Crucial, unset definitions.
        self.localizerName = None
        self.localizerNameSingular = None
        self.localizerNamePlural = None
        self.localizerShort = None
        self.localizerWordwrap = None
        self.defineNames()
        self.levelRange = (0, 0)
        self.freqRange = None
        self.attacks = {}

        # Visual definitions
        self.suitSize = None
        self.handColor = None
        self.headModel = None
        self.skeleHeadModel = None
        self.suitType = SUIT_A
        self.textureOverride = ''
        self.isSpecial = False
        self.noShowUntilDiscovered = False
        self.alwaysSkelecog = False
        self.alwaysExecutive = False

        # Battle definitions
        self.passives = None

        # Movie definitions
        self.movieAttributes = dict(overrideDeaths=False, extendMovieTime=0)

        # Street definitions
        self.joinChanceOverride = None
        self.isStubborn = None
        self.maxCogOnStreet = None
        self.battleCogCap = None
        self.canJoinBattles = None

        # Misc attributes
        self.reviveAttributes = None
        self.forceHp = {}
        self.iterativeChat = False
        self.bounty = {}
        self.loot = []
        # Determines if this cog should have their loot split to 2 different sections, rarity and kill count
        self.loot_holdShiftToSwap = False
        self.attackBehavior = SEE.EFFECT_SUIT
        self.overlevelDamageFactor = 1
        self.extraPadding = 1.0
        self.disallowSpawn = False

    ### Required methods, factored out to be less of a pain to read. ###
    def defineNames(self):
        """Attach name localization to the cog."""
        self.__exception("Suit names were not defined for the suit!", self.name not in TTLocalizer.SuitNameDefs)
        a, b, c, short, wordwrap = TTLocalizer.SuitNameDefs[self.name]
        self.localizerName = a
        self.localizerNameSingular = b
        self.localizerNamePlural = c
        self.localizerShort = short
        self.localizerWordwrap = wordwrap

    def defineLevelRange(self, minimumLevel, maximumLevel=None):
        """Defines the cog's level range."""
        if maximumLevel is None:
            maximumLevel = minimumLevel
        self.levelRange = (minimumLevel, maximumLevel)
        self.setFreqRange()

    def defineParts(self, suitSize: float, handColor: tuple, headModel: list, skeleHeadModel: list = None,
                    suitType=SUIT_A, textureOverride='', skeleTextureOverride='', tieType=TIE_BROAD,
                    bodyTex=TEX_CORP, skeleBodyTex=None, bodyTint=None, custom=True, extraPadding: float = 1.0,
                    bodyModelType: BodyModelType = None):
        """Describes the information for the parts of the suit. of the suit."""
        self.suitSize = suitSize
        self.handColor = handColor
        self.headModel = headModel
        if skeleHeadModel is None:
            skeleHeadModel = {
                SUIT_A: [SKELE_HEAD_A],
                SUIT_B: [SKELE_HEAD_B],
                SUIT_C: [SKELE_HEAD_C],
            }.get(suitType)
        self.skeleHeadModel = skeleHeadModel
        self.suitType = suitType
        self.textureOverride = textureOverride
        self.skeleTextureOverride = skeleTextureOverride
        self.tieType = tieType
        self.bodyTex = bodyTex
        self.skeleBodyTex = skeleBodyTex
        self.bodyTint = bodyTint
        self.isSpecial = custom
        self.extraPadding = extraPadding
        if bodyModelType is not None:
            self.bodyModelType = bodyModelType

    ### Describes a part of the suit. Meant to be called several times. ###
    def describeAttack(self, attackEnum: int,
                       attack=0, accuracy=0, frequency=0):
        """
        Defines an attack that the Cog can do.

        The range variables can be called as a singular int to describe it for all levels,
        or a tuple with two values to automatically place it over a range,
        or a tuple with three or more values to define it manually.
        """
        self.__exception("describeAttack was given an invalid type!", not isinstance(attackEnum, int))
        self.__exception("Attack was already defined!", attackEnum in self.attacks)
        self.__mustHave(self.levelRange)

        def buildNums(numTuple, size=1):
            """Handles this tuple based on its length"""
            if type(numTuple) == int:
                # Wrap the int in a tuple.
                return tuple([numTuple] * self.__getLevelSize())

            elif type(numTuple) == tuple:
                if len(numTuple) == 1:
                    # Just return the tuple by itself.
                    return numTuple

                elif len(numTuple) == 2:
                    # Build the tuple out by the level range.
                    a, b = numTuple
                    length = self.__getLevelSize()
                    abLength = (b - a) / (length - 1)
                    newRange = []
                    for i in range(length):
                        newRange.append(math.floor((a + (abLength * i)) / size) * size)
                    return tuple(newRange)

                else:
                    # Build the tuple out manually.
                    # If it's shorter than expected, repeat the last value.
                    if self.__getLevelSize() != len(numTuple):
                        maxVal = numTuple[-1]
                        additions = self.__getLevelSize() - len(numTuple)
                        numTuple = tuple(list(numTuple) + ([maxVal] * additions))
                    return numTuple

            self.__exception("describeAttack was given an invalid type!")

        attackNums: tuple = buildNums(attack)
        accuracyNums: tuple = buildNums(accuracy, size=5)
        frequencyNums: tuple = buildNums(frequency, size=5)

        if self.nerfDamageForExe:
            attackNums = list(attackNums)
            for i in range(len(attackNums)):
                attackNums[i] = math.ceil(attackNums[i] * 0.8333)
            attackNums = tuple(attackNums)

        self.attacks[attackEnum] = (attackNums, accuracyNums, frequencyNums)

    ### Methods to set general battle information on the suit. ###
    def setFreqRange(self, freqTuple=None):
        """Sets the frequency range of the cog."""
        self.__mustHave(self.levelRange)

        if freqTuple is None:
            # Sets the cog's frequency range based on its level range.
            size = self.__getLevelSize()
            freqTuple = (100,)
            if size in DefaultFreqLists:
                freqTuple = DefaultFreqLists[size]
            self.freqRange = freqTuple
        else:
            # Sets a cog's frequency range based on the method input.
            if type(freqTuple) == str:
                if freqTuple in DefinedFreqLists:
                    self.freqRange = DefinedFreqLists[freqTuple]
                else:
                    self.__exception("setFreqRange called with an undefined str.")
            elif type(freqTuple) == tuple:
                self.freqRange = tuple
            else:
                self.__exception("setFreqRange was called with a bad input.")

        # Makes sure that we have set frequency for all level sizes.
        if type(self.freqRange) != tuple:
            self.freqRange = (self.freqRange,)
        sizeDiff = self.__getLevelSize() - len(self.freqRange)
        self.freqRange = tuple(list(self.freqRange) + [DefaultFreqEscalation] * max(sizeDiff, 0))

        self.__exception("setFreqRange got too low of a frequency range!", sum(self.freqRange) < 100)

    def setPassives(self, **kwargs):
        """Sets the cog's passive attributes."""
        self.passives = kwargs

    def setReviveAttributes(self, hpMult: float = ReviveDefaults[0], dmgMult: float = ReviveDefaults[1]):
        """Sets the cog's revive attributes (aka v2.0 death)."""
        self.reviveAttributes = (hpMult, dmgMult)

    def setMovieAttributes(self, overrideDeaths=None, extendMovieTime=None):
        """Sets the cog's movie attributes (override deaths, movie extension time)."""
        if overrideDeaths is not None:
            self.movieAttributes['overrideDeaths'] = overrideDeaths
        if extendMovieTime is not None:
            self.movieAttributes['extendMovieTime'] = extendMovieTime

    def setHpPerLevel(self, hpDict):
        """
        Sets the HP that this suit should have on each level.
        :param hpDict: A dictionary from {level: hp}.
        """
        self.forceHp = hpDict
    
    def setAttackBehavior(self, statusId: int):
        self.attackBehavior = statusId

    ### Methods to set information on the suit. ###
    def makeHidden(self):
        """Makes the cog hidden in the Cog Menu until discovered."""
        self.noShowUntilDiscovered = True

    def isHidden(self) -> bool:
        """Checks if the defined cog is hidden on the cog page."""
        return self.noShowUntilDiscovered

    def makeAlwaysSkelecog(self):
        """Makes the cog always a skelecog when spawning."""
        self.alwaysSkelecog = True

    def isAlwaysSkelecog(self) -> bool:
        """Checks if the defined cog is always a skelecog when spawning."""
        return self.alwaysSkelecog

    def makeAlwaysExecutive(self):
        """Makes the cog always an executive when spawning."""
        self.alwaysExecutive = True

    def isAlwaysExecutive(self) -> bool:
        """Checks if the defined cog is always an executive when spawning."""
        return self.alwaysExecutive

    def makeChatIterative(self):
        """Makes the cog talk in iterative chat."""
        self.iterativeChat = True

    def isChatIterative(self) -> bool:
        """Checks if the defined cog talks in iterative chat."""
        return self.iterativeChat

    def makeSpawnDisallowed(self):
        """Makes the cog not able to be spawned via commands."""
        self.disallowSpawn = True

    def isSpawnDisallowed(self):
        """Checks if the defined cog is disallowed from spawning."""
        return self.disallowSpawn

    def setStreetAttributes(self, joinChanceOverride=None,
                            isStubborn=None, maxCogOnStreet=None,
                            battleCogCap=None, canJoinBattles=None):
        """Sets the cog's properties when put on the street."""
        # A cog that is Stubborn will be very unlikely to leave a street zone
        # through traditional means, whether that is an invasion summoning/retreating,
        # entering a cog building, or by walking into another battle.
        self.joinChanceOverride = joinChanceOverride
        self.isStubborn = isStubborn
        self.maxCogOnStreet = maxCogOnStreet
        self.battleCogCap = battleCogCap
        self.canJoinBattles = canJoinBattles

    def setBounty(self, bountyDict):
        self.bounty = bountyDict
        if 'group' in bountyDict:
            BountyGroupsToCogs.setdefault(bountyDict['group'], [])
            BountyGroupsToCogs[bountyDict['group']].append(self.name)

    def getBounty(self):
        return self.bounty

    def setLoot(self, lootList, shiftSwap=False):
        self.loot = lootList
        self.loot_holdShiftToSwap = shiftSwap

    def getLoot(self):
        return self.loot

    def getLootShiftToSwap(self):
        return self.loot_holdShiftToSwap

    def getCogTier(self) -> Optional[int]:
        return self.cogTier

    ### General private methods.
    def __getLevelSize(self):
        a, b = self.levelRange
        return (b - a) + 1

    def __getSizeVar(self, suitEnum):
        if suitEnum == SUIT_A:
            return aSize
        elif suitEnum == SUIT_B:
            return bSize
        elif suitEnum == SUIT_C:
            return cSize
        self.__exception("__getSizeVar called with an illegal suit enum!")

    def __mustHave(self, variable):
        if not variable or variable is None:
            self.__exception("Necessary variable was undefined!")

    def __exception(self, exceptionString="Suit was defined wrongly!", check=True):
        if check:
            raise Exception(exceptionString)

    ### Testing methods. ###
    def test(self):
        """Makes sure all of the Suit's information is consistent and not prone to errors."""
        def kill():
            self.__exception("Suit definition test failed.")

        # First, make sure that our necessary variables are set.
        if self.levelRange == (0, 0):
            kill()
        if self.freqRange is None or self.suitSize is None\
            or self.handColor is None or self.headModel is None:
            kill()
        if not self.attacks:
            kill()
        # Second, go through all of our attacks, and make sure that their
        # frequency set for each level adds up to a nice round 100.
        frequenciesTuple = list(attackTuple[2] for attackTuple in list(self.attacks.values()))
        runningTotal = list(frequenciesTuple[0])
        for frequencyTuple in frequenciesTuple[1:]:
            for i in range(len(runningTotal)):
                runningTotal[i] += frequencyTuple[i]
        for check in runningTotal:
            if check != 100:
                kill()

        # Check our per-cog bounties
        for bountyType, bountyNum in list(self.bounty.items()):
            if bountyType in ('group', ToontownGlobals.CogBountyTypes.HolidayList):
                continue
            # Can't have invalid bounty types
            if bountyType not in list(ToontownGlobals.CogBountyTypes):
                kill()
            # Can't have non-positive bounty rewards
            if bountyNum <= 0:
                kill()

        for lootTable in self.loot:
            if not lootTable.test():
                kill()

        return True  # all tests passed

    def isMiniboss(self) -> bool:
        """Checks if the defined cog is a miniboss."""
        return self.miniboss

    ### Methods that represent parts of the suit definition in useful ways. ###
    def buildSuitAttributes(self) -> dict:
        """Returns a described list for the Suit Attributes."""
        buildDict = {
            "name": self.localizerName,
            "singularname": self.localizerNameSingular,
            "pluralname": self.localizerNamePlural,
            "level": self.levelRange[0] - 1,
            'maxLevel': self.levelRange[1] - 1,
            "freq": self.freqRange,
            # "acc": (35, 40, 45, 50, 55), todo - is this even necessary?
            "attacks": self.attacks,
            "attackBehavior": self.attackBehavior,
            "overlevelDamageFactor": self.overlevelDamageFactor,
            "extraPadding": self.extraPadding,
        }
        if self.passives is not None:
            buildDict['passives'] = self.passives
        if self.specialization != NORMAL:
            buildDict['specialization'] = self.specialization
        return buildDict

    def buildHeadAttributes(self) -> tuple:
        baseTuple: list = [
            self.suitSize / self.__getSizeVar(self.suitType),
            self.handColor, self.headModel, self.skeleHeadModel, self.textureOverride, self.skeleTextureOverride,
            self.tieType, self.bodyTex, self.skeleBodyTex, self.bodyTint, self.bodyHeight, self.bodyModelType,
        ]
        if self.isSpecial:
            baseTuple.append(self.cogType)
            baseTuple.append(self.suitType)
        return tuple(baseTuple)
        # 'f': (4.0 / cSize, corpPolyColor, ['flunky', 'glasses'], '', 4.88),

    def getAbridgedName(self) -> str:
        """Returns the abridged name of a suit."""
        if self.localizerShort:
            return self.localizerShort
        return self.localizerName

    def getNameWordwrap(self) -> float:
        """Returns the wordwrap value of the name of a suit."""
        return self.localizerWordwrap

    def getAttackEnums(self) -> list:
        """Returns all of the attack enums of this Suit Definition."""
        return list(self.attacks.keys())


# Functions to access various properties of SuitDefinitions.
def suitDefinitionObjects() -> list:
    """Returns a list of all of the suit definition objects."""
    return list(SuitDefinitions.values())


def suitGetMinibosses() -> list:
    """Returns a list of all of the Suit minibosses."""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.isMiniboss()]


def suitGetMercs() -> list:
    """Returns a list of all of the Suit mercenaries."""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.isMerc]


def suitGetNotMinibosses() -> list:
    """Returns a list of all of the not Suit minibosses."""
    return [suitDef for suitDef in suitDefinitionObjects() if not suitDef.isMiniboss()]


def suitBuildBattleAttributeDict() -> dict:
    """Returns a dict of all Suit battle attributes"""
    retdict = {}
    Defs = suitDefinitionObjects()
    for Def in Defs:
        retdict[Def.name] = Def.buildSuitAttributes()
    return retdict


def suitBuildHeadAttributeDict() -> dict:
    """Returns a dict of all Suit head attributes"""
    retdict = {}
    Defs = suitDefinitionObjects()
    for Def in Defs:
        retdict[Def.name] = Def.buildHeadAttributes()
    return retdict


def suitGetCogPageHidden() -> list:
    """Returns a list containing all Suit Definitions that are hidden in the cog page"""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.isHidden()]


def suitGetCogPageHiddenNamesCode() -> list:
    """Returns a tuple of all cog page hidden code names."""
    return [Def.name for Def in suitGetCogPageHidden()]


def suitGetAlwaysSkelecog() -> list:
    """Returns a list containing all Suit Definitions that are always skelecogs"""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.isAlwaysSkelecog()]


def suitGetAlwaysSkelecogNamesCode() -> tuple:
    """Returns a tuple of all code names for cogs that are always skelecogs."""
    return tuple([Def.name for Def in suitGetAlwaysSkelecog()])


def suitGetAlwaysExecutive() -> list:
    """Returns a list containing all Suit Definitions that are always executives"""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.isAlwaysExecutive()]


def suitGetAlwaysExecutiveNamesCode() -> tuple:
    """Returns a tuple of all code names for cogs that are always executives."""
    return tuple([Def.name for Def in suitGetAlwaysExecutive()])


def suitGetIterativeChat() -> list:
    """Returns a list containing all Suit Definitions that have iterative chat"""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.isChatIterative()]


def suitGetIterativeChatNamesCode() -> tuple:
    """Returns a tuple of all code names for cogs that have iterative chat."""
    return tuple([Def.name for Def in suitGetIterativeChat()])


def suitGetDisallowedSpawns() -> list:
    """Returns a list containing all Suit Definitions that are disallowed from being spawned"""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.isSpawnDisallowed()]


def suitGetDisallowedSpawnsNamesCode() -> tuple:
    """Returns a tuple of all code names for cogs that are disallowed from being spawned"""
    return tuple([Def.name for Def in suitGetDisallowedSpawns()])


def suitGetMinibossNamesCode() -> tuple:
    """Returns a tuple of all miniboss's code names."""
    return tuple([Def.name for Def in suitGetMinibosses()])


def suitGetMinibossNamesAbridged() -> dict:
    """Returns a dict of all miniboss's abridged names."""
    bossDefs = suitGetMinibosses()
    retdict = {}
    for Def in bossDefs:
        retdict[Def.name] = Def.getAbridgedName()
    return retdict


def suitGetNameWordwraps() -> dict:
    """Returns a dict of all cog's name wordwraps."""
    suitDefs = suitDefinitionObjects()
    retdict = {}
    for Def in suitDefs:
        retdict[Def.name] = Def.getNameWordwrap()
    return retdict


def suitGetBounties() -> list:
    """Returns a list containing all Suit Definitions that have bounties"""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.getBounty()]


def suitGetBountyNamesCode() -> dict:
    """Returns a dict of all code names for cogs that have bounties, and their respective bounty."""
    return {Def.name: Def.getBounty() for Def in suitGetBounties()}


def suitGetBountyGroupsByType() -> dict:
    """Returns a dict of all bounty groups and the cogs that make them up."""
    return BountyGroupsToCogs.copy()


def suitGetLoot() -> list:
    """Returns a list containing all Suit Definitions that have loot"""
    return [suitDef for suitDef in suitDefinitionObjects() if suitDef.getLoot()]


def suitGetLootNamesCode() -> dict:
    """Returns a dict of all code names for cogs that have loot, and their respective loot."""
    return {Def.name: Def.getLoot() for Def in suitGetLoot()}


def suitGetLootShiftSwapNamesCode() -> list:
    """Returns a listof all code names for cogs that have the 'shift to swap' feature for their loot info."""
    return [suitDef.name for suitDef in suitDefinitionObjects() if suitDef.getLootShiftToSwap()]


def suitGetSuitSizes() -> dict:
    """Returns a dict of all suit's suit sizes."""
    retdict = {}
    Defs = suitDefinitionObjects()
    for Def in Defs:
        retdict[Def.name] = Def.suitSize
    return retdict


def suitGetStreetInfo() -> tuple:
    """
    Returns a tuple with this information:
    (JOIN_CHANCE_OVERRIDES (dict), STUBBORN_COGS (list), STREET_MAX_COG (dict))
    """
    overrides = {}
    stubborn = []
    maxcog = {}
    battlecap = {}
    canjoin = set()
    Defs = suitDefinitionObjects()
    for Def in Defs:
        over = Def.joinChanceOverride
        stub = Def.isStubborn
        mcog = Def.maxCogOnStreet
        bcap = Def.battleCogCap
        join = Def.canJoinBattles
        if over is not None:
            overrides[Def.name] = over
        if stub is not None:
            stubborn.append(Def.name)
        if mcog is not None:
            maxcog[Def.name] = mcog
        if bcap is not None:
            battlecap[Def.name] = bcap
        if join is not None:
            canjoin.add(Def.name)
    return (overrides, stubborn, maxcog, battlecap, canjoin)


def suitGetReviveInfo() -> dict:
    """Returns a dict with all of the revive info for suits."""
    retdict = {'standard': ReviveDefaults}
    Defs = suitDefinitionObjects()
    for Def in Defs:
        if Def.reviveAttributes is not None:
            retdict[Def.name] = Def.reviveAttributes
    return retdict


def suitGetOverrideDeaths() -> list:
    """Returns a list of all cog names who override movie deaths"""
    Defs = suitDefinitionObjects()
    return [Def.name for Def in Defs if Def.movieAttributes['overrideDeaths']]


def suitGetExtendMovieTime() -> dict:
    """Returns a dict of all cog names who extend movies, and by how much"""
    Defs = suitDefinitionObjects()
    return {Def.name: Def.movieAttributes['extendMovieTime'] for Def in Defs}


def suitGetAllNamesCode() -> tuple:
    """Returns a tuple of all code names."""
    return tuple([Def.name for Def in suitDefinitionObjects()])


def suitGetMercNamesCode() -> tuple:
    """Returns a tuple of all merc's code names."""
    return tuple([Def.name for Def in suitGetMercs()])


def suitGetSuitNameByDept(dept) -> tuple:
    """Returns a tuple of all cogs of a specified department."""
    return tuple(Def.name for Def in suitDefinitionObjects() if Def.cogType == dept and \
        any([Def.isMainline, Def.specialization != NORMAL]))


def suitGetAllSuitNameByDept(dept) -> tuple:
    """Returns a tuple of all cogs of a specified department, including special Cogs."""
    return tuple(Def.name for Def in suitDefinitionObjects() if Def.cogType == dept)


def suitGroupSuitsByDept() -> dict:
    """Returns a dictionary mapping every cog to their respective department."""
    return {dept: suits for dept, suits in zip(
            DEPARTMENT_ORDER, (suitGetSuitNameByDept(dept) for dept in DEPARTMENT_ORDER))}


def suitGroupAllSuitsByDept() -> dict:
    """Returns a dictionary mapping every cog to their respective department, including special Cogs."""
    return {dept: suits for dept, suits in zip(
            DEPARTMENT_ORDER, (suitGetAllSuitNameByDept(dept) for dept in DEPARTMENT_ORDER))}


def suitGetInvasionableSuits() -> dict:
    """Returns a dictionary mapping every cog to their respective department if they are invasionable."""
    return {dept: suits for dept, suits in zip(
        DEPARTMENT_ORDER, (tuple(Def.name for Def in suitDefinitionObjects() if Def.spawnsInInvasion and Def.cogType == dept) for dept in DEPARTMENT_ORDER))}


def suitGetFemales() -> tuple:
    """Returns a tuple of all female cogs."""
    return tuple(Def.name for Def in suitDefinitionObjects() if Def.isFemale)


def suitGetBowtieSuits() -> tuple:
    """Returns a tuple of all cogs with bowties."""
    return tuple(Def.name for Def in suitDefinitionObjects() if Def.tieType == TIE_BOW)


def suitGetNoTieSuits() -> tuple:
    """Returns a tuple of all cogs with no ties."""
    return tuple(Def.name for Def in suitDefinitionObjects() if Def.tieType == TIE_NONE)
