import random

from toontown.hood import ZoneUtil
from toontown.shtiker.CogPageGlobals import indexToCogDepartment
from toontown.toonbase import ToontownGlobals
from toontown.building import ClashSuitBuildingGlobals

from typing import Tuple, Dict, List

from toontown.utils import text

from toontown.clashsuit.suit import SuitDNA
from toontown.clashbattle.battle.SuitBattleGlobals import SuitAttributes


class CogSpawnDefinition:
    """
    A data class for defining the various rates of how Cogs spawn.
    """

    def __init__(self,
                 cogTrackChances: Dict[str, int],
                 suitLevelMin: int,
                 suitLevelMax: int,
                 maxSpawnCogType: int = 6,
                 maxInvasionCogTier: int = 0,
                 executiveSpawnChance: int = 0,
                 skelecogSpawnChance: int = 0,
                 ):
        """
        Defines cog spawn data.
        :param cogTrackChances:      Chances for a given Cog dept to spawn on the street.
        :param suitLevelMin:         The minimum Cog Level that can spawn.
        :param suitLevelMax:         The maximum Cog Level that can spawn.
        :param maxSpawnCogType:      The max "cog type" that can naturally spawn (1=Flunky, 8=Big Cheese).
        :param maxInvasionCogTier:   The max "cog type" that can spawn (1=Flunky, 8=Big Cheese) from invasions.
                                     Set to 0 for the area being immune to invasions.
        :param executiveSpawnChance: The spawn chance for executive cogs.
        :param skelecogSpawnChance:  The spawn chance for skelecogs.
        """
        self.cogTrackChances = cogTrackChances
        self.suitLevelMin = suitLevelMin
        self.suitLevelMax = suitLevelMax
        self.maxSpawnCogType = maxSpawnCogType
        self.maxInvasionCogTier = maxInvasionCogTier
        self.executiveSpawnChance = executiveSpawnChance
        self.skelecogSpawnChance = skelecogSpawnChance

    def getCogTrackChances(self) -> Dict[str, int]:
        return self.cogTrackChances

    def pickRandomCogTrack(self) -> str:
        trackChances = self.getCogTrackChances()
        return random.choices(
            population=list(trackChances.keys()),
            weights=list(trackChances.values()),
        )[0]

    def getSuitLevelRange(self) -> Tuple[int]:
        return tuple(range(self.getSuitLevelMin(), self.getSuitLevelMax() + 1))

    def getSuitLevelMin(self) -> int:
        return self.suitLevelMin

    def getSuitLevelMax(self) -> int:
        return self.suitLevelMax

    def getMaxSpawnCogType(self) -> int:
        return self.maxSpawnCogType

    def getMaxInvasionCogTier(self) -> int:
        return self.maxInvasionCogTier

    def getExecutiveSpawnChance(self) -> int:
        return self.executiveSpawnChance

    def getSkelecogSpawnChance(self) -> int:
        return self.skelecogSpawnChance


class SuitBranchDefinition:
    """
    A data class for defining how cogs can spawn in a playground.
    """

    def __init__(self,
                 cogSpawnDefinition: CogSpawnDefinition,
                 cogCountRange: Tuple[int, int] = (12, 28),
                 minCogBuildings: int = 0,
                 maxCogBuildings: int = 0,
                 buildingSpawnChance: int = 0,
                 ):
        """
        Defines the params for Suits spawning in a hood.
        :param cogSpawnDefinition: Defines how cogs can spawn in the branch.
        :param cogCountRange: Min/Max of suits that can fly into the zone. Suits that
                              walk in from buildings are on top of this limit, and each
                              suit building contributes SUIT_BUILDING_NUM_SUITS to the
                              expected number of suits in a particular branch.
        :param minCogBuildings: The minimum number of Cog Buildings in a given branch.
        :param maxCogBuildings: The maximum number of Cog Buildings in a given branch.
        :param buildingSpawnChance: The chance for a Cog Building to spawn.
        """
        self.cogSpawnDefinition = cogSpawnDefinition
        self.cogCountRange = cogCountRange
        self.minCogBuildings = minCogBuildings
        self.maxCogBuildings = maxCogBuildings
        self.buildingSpawnChance = buildingSpawnChance
        self.buildingHeights = []  # internal state for determining building heights

    def getCogSpawnDefinition(self) -> CogSpawnDefinition:
        return self.cogSpawnDefinition

    def getCogCountRange(self) -> Tuple[int, int]:
        return self.cogCountRange

    def getCogMin(self) -> int:
        return self.cogCountRange[0]

    def getCogMax(self) -> int:
        return self.cogCountRange[1]

    def getCogMean(self) -> int:
        return (self.getCogMin() + self.getCogMax()) // 2

    def getMinCogBuildings(self) -> int:
        return self.minCogBuildings

    def getMaxCogBuildings(self) -> int:
        return self.maxCogBuildings

    def getBuildingWeight(self) -> int:
        return 100

    def getBulidingHeights(self) -> List[int]:
        return self.buildingHeights

    def getBuildingSpawnChance(self) -> int:
        return self.buildingSpawnChance

    def getZoneId(self) -> int:
        for zoneId, branchDef in SuitHoodInfo.items():
            if branchDef is self:
                return zoneId
        raise KeyError


SuitHoodInfo: Dict[int, SuitBranchDefinition] = {
    ###                  ###
    ### TOONTOWN CENTRAL ###
    ###                  ###
    ToontownGlobals.SillyStreet: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 20, 'm': 20, 'l': 20, 'c': 20, 'g': 20},
            suitLevelMin=1, suitLevelMax=3,
            executiveSpawnChance=10,
        ),
        minCogBuildings=0, maxCogBuildings=2,
        buildingSpawnChance=2,
    ),
    ToontownGlobals.LoopyLane: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 5, 'l': 40, 'c': 30, 'g': 20},
            suitLevelMin=1, suitLevelMax=4,
            executiveSpawnChance=5,
        ),
        minCogBuildings=0, maxCogBuildings=3,
        buildingSpawnChance=2,
    ),
    ToontownGlobals.PunchlinePlace: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 40, 'm': 40, 'l': 5, 'c': 5, 'g': 10},
            suitLevelMin=1, suitLevelMax=4,
            executiveSpawnChance=5,
        ),
        minCogBuildings=0, maxCogBuildings=2,
        buildingSpawnChance=2,
    ),
    ToontownGlobals.WackyWay: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 5, 'l': 20, 'c': 30, 'g': 40},
            suitLevelMin=1, suitLevelMax=4,
            executiveSpawnChance=5,
        ),
        minCogBuildings=0, maxCogBuildings=3,
        buildingSpawnChance=10,
    ),

    ###                   ###
    ### BARNACLE BOATYARD ###
    ###                   ###
    ToontownGlobals.BuccaneerBoulevard: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'l': 10, 'c': 80, 'g': 10},
            suitLevelMin=2, suitLevelMax=5, maxInvasionCogTier=3,
            executiveSpawnChance=8,
        ),
        minCogBuildings=1, maxCogBuildings=5,
        buildingSpawnChance=45,
    ),
    ToontownGlobals.SeaweedStreet: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 30, 'm': 60, 'l': 10},
            suitLevelMin=2, suitLevelMax=5, maxInvasionCogTier=3,
            executiveSpawnChance=10,
        ),
        minCogBuildings=1, maxCogBuildings=5,
        buildingSpawnChance=45,
    ),
    ToontownGlobals.LighthouseLane: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 5, 'l': 35, 'g': 55},
            suitLevelMin=2, suitLevelMax=5, maxInvasionCogTier=3,
            executiveSpawnChance=15,
        ),
        minCogBuildings=1, maxCogBuildings=5,
        buildingSpawnChance=45,
    ),
    ToontownGlobals.AnchorAvenue: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 55, 'c': 35, 'g': 10},
            suitLevelMin=2, suitLevelMax=5, maxInvasionCogTier=3,
            executiveSpawnChance=10,
        ),
        minCogBuildings=1, maxCogBuildings=5,
        buildingSpawnChance=45,
    ),

    ###                   ###
    ### YE OLDE TOONTOWNE ###
    ###                   ###
    ToontownGlobals.KnightKnoll: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 45, 'm': 45, 'l': 5, 'c': 5},
            suitLevelMin=3, suitLevelMax=6, maxInvasionCogTier=4,
            executiveSpawnChance=10,
        ),
        minCogBuildings=2, maxCogBuildings=6,
        buildingSpawnChance=60,
    ),
    ToontownGlobals.NobleNook: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'l': 10, 'c': 40, 'g': 50},
            suitLevelMin=3, suitLevelMax=5, maxInvasionCogTier=4,
            executiveSpawnChance=10,
        ),
        minCogBuildings=2, maxCogBuildings=6,
        buildingSpawnChance=60,
    ),
    ToontownGlobals.WizardWay: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 5, 'l': 70, 'c': 20},
            suitLevelMin=3, suitLevelMax=6, maxInvasionCogTier=4,
            executiveSpawnChance=12,
        ),
        minCogBuildings=2, maxCogBuildings=6,
        buildingSpawnChance=60,
    ),

    ###                  ###
    ### DAFFODIL GARDENS ###
    ###                  ###
    ToontownGlobals.PetuniaPlace: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 50, 'l': 45},
            suitLevelMin=4, suitLevelMax=7, maxInvasionCogTier=5,
            executiveSpawnChance=8,
        ),
        minCogBuildings=2, maxCogBuildings=6,
        buildingSpawnChance=70,
    ),
    ToontownGlobals.DaisyDrive: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 10, 'm': 10, 'c': 15, 'g': 65},
            suitLevelMin=4, suitLevelMax=6, maxInvasionCogTier=5,
            executiveSpawnChance=10,
        ),
        minCogBuildings=2, maxCogBuildings=6,
        buildingSpawnChance=70,
    ),
    ToontownGlobals.TulipTerrace: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 80, 'm': 5, 'l': 5, 'c': 5, 'g': 5},
            suitLevelMin=4, suitLevelMax=7, maxInvasionCogTier=5,
            executiveSpawnChance=15,
        ),
        minCogBuildings=2, maxCogBuildings=6,
        buildingSpawnChance=70,
    ),
    ToontownGlobals.SunflowerStreet: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 10, 'm': 10, 'l': 10, 'c': 60, 'g': 10},
            suitLevelMin=4, suitLevelMax=7, maxInvasionCogTier=5,
            executiveSpawnChance=10,
        ),
        minCogBuildings=2, maxCogBuildings=6,
        buildingSpawnChance=70,
    ),

    ###                  ###
    ### MEZZO MELODYLAND ###
    ###                  ###
    ToontownGlobals.AltoAvenue: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 50, 'm': 25, 'g': 25},
            suitLevelMin=5, suitLevelMax=7, maxInvasionCogTier=6,
            executiveSpawnChance=8,
        ),
        minCogBuildings=3, maxCogBuildings=7,
        buildingSpawnChance=70,
    ),
    ToontownGlobals.BaritoneBoulevard: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 10, 'm': 40, 'g': 50},
            suitLevelMin=5, suitLevelMax=8, maxInvasionCogTier=6,
            executiveSpawnChance=10,
        ),
        minCogBuildings=3, maxCogBuildings=7,
        buildingSpawnChance=70,
    ),
    ToontownGlobals.TenorTerrace: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'l': 40, 'c': 40, 'g': 20},
            suitLevelMin=5, suitLevelMax=8, maxInvasionCogTier=6,
            executiveSpawnChance=15,
        ),
        minCogBuildings=3, maxCogBuildings=7,
        buildingSpawnChance=70,
    ),
    ToontownGlobals.SopranoStreet: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 80, 'l': 5, 'c': 5, 'g': 5},
            suitLevelMin=5, suitLevelMax=8, maxInvasionCogTier=6,
            executiveSpawnChance=25,
        ),
        minCogBuildings=5, maxCogBuildings=10,
        buildingSpawnChance=70,
    ),

    ###            ###
    ### THE BURGER ###
    ###            ###
    ToontownGlobals.WalrusWay: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'l': 5, 'c': 75, 'g': 20},
            suitLevelMin=6, suitLevelMax=8, maxInvasionCogTier=7,
            executiveSpawnChance=20,
        ),
        minCogBuildings=5, maxCogBuildings=10,
        buildingSpawnChance=75,
    ),
    ToontownGlobals.SleetStreet: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 60, 'm': 30, 'g': 10},
            suitLevelMin=6, suitLevelMax=9, maxInvasionCogTier=7,
            executiveSpawnChance=20,
        ),
        minCogBuildings=5, maxCogBuildings=10,
        buildingSpawnChance=75,
    ),
    ToontownGlobals.PolarPlace: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 5, 'l': 80, 'c': 5, 'g': 5},
            suitLevelMin=6, suitLevelMax=9, maxInvasionCogTier=7,
            executiveSpawnChance=25,
        ),
        minCogBuildings=5, maxCogBuildings=10,
        buildingSpawnChance=75,
    ),
    ToontownGlobals.ArcticAvenue: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 10, 'm': 5, 'l': 5, 'c': 10, 'g': 70},
            suitLevelMin=6, suitLevelMax=9, maxInvasionCogTier=7,
            executiveSpawnChance=25,
        ),
        minCogBuildings=5, maxCogBuildings=10,
        buildingSpawnChance=75,
    ),

    ###             ###
    ### ACORN ACRES ###
    ###             ###
    ToontownGlobals.AlmondAvenue: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 20, 'm': 10, 'l': 10, 'c': 10, 'g': 50},
            suitLevelMin=7, suitLevelMax=10, maxInvasionCogTier=8,
            executiveSpawnChance=20,
        ),
        minCogBuildings=3, maxCogBuildings=7,
        buildingSpawnChance=60,
    ),
    ToontownGlobals.PeanutPlace: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 30, 'm': 30, 'l': 30, 'g': 10},
            suitLevelMin=7, suitLevelMax=10, maxInvasionCogTier=8,
            executiveSpawnChance=20,
        ),
        minCogBuildings=3, maxCogBuildings=7,
        buildingSpawnChance=60,
    ),
    ToontownGlobals.WalnutWay: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 5, 'l': 5, 'c': 80, 'g': 5},
            suitLevelMin=7, suitLevelMax=10, maxInvasionCogTier=8,
            executiveSpawnChance=20,
        ),
        minCogBuildings=3, maxCogBuildings=7,
        buildingSpawnChance=60,
    ),
    ToontownGlobals.LegumeLane: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'m': 40, 'l': 40, 'c': 20},
            suitLevelMin=7, suitLevelMax=10, maxInvasionCogTier=8,
            executiveSpawnChance=20,
        ),
        minCogBuildings=3, maxCogBuildings=7,
        buildingSpawnChance=60,
    ),

    ###                  ###
    ### DROWSY DREAMLAND ###
    ###                  ###
    ToontownGlobals.LullabyLane: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 40, 'm': 40, 'l': 5, 'c': 5, 'g': 10},
            suitLevelMin=8, suitLevelMax=10, maxInvasionCogTier=8,
            executiveSpawnChance=25,
        ),
        minCogBuildings=5, maxCogBuildings=10,
        buildingSpawnChance=80,
    ),
    ToontownGlobals.PajamaPlace: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 5, 'l': 40, 'c': 40, 'g': 10},
            suitLevelMin=8, suitLevelMax=11, maxInvasionCogTier=8,
            executiveSpawnChance=25,
        ),
        minCogBuildings=5, maxCogBuildings=10,
        buildingSpawnChance=80,
    ),
    ToontownGlobals.TwilightTerrace: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 5, 'm': 5, 'l': 5, 'c': 5, 'g': 80},
            suitLevelMin=8, suitLevelMax=11, maxInvasionCogTier=8,
            executiveSpawnChance=30,
        ),
        minCogBuildings=5, maxCogBuildings=10,
        buildingSpawnChance=80,
    ),

    ###         ###
    ### COG HQS ###
    ###         ###
    ToontownGlobals.SellbotHQ: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 92, 'm': 2, 'l': 2, 'c': 2, 'g': 2},
            suitLevelMin=4, suitLevelMax=8,
            maxSpawnCogType=7,
            executiveSpawnChance=20,
            skelecogSpawnChance=15,
        ),
        cogCountRange=(6, 14),
    ),
    ToontownGlobals.SellbotFactoryExt: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 100},
            suitLevelMin=5, suitLevelMax=8,
            maxSpawnCogType=8,
            executiveSpawnChance=20,
            skelecogSpawnChance=15,
        ),
        cogCountRange=(12, 28),
    ),
    ToontownGlobals.CashbotHQ: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 2, 'm': 92, 'l': 2, 'c': 2, 'g': 2},
            suitLevelMin=5, suitLevelMax=9,
            maxSpawnCogType=8,
            executiveSpawnChance=20,
            skelecogSpawnChance=15,
        ),
        cogCountRange=(12, 28),
    ),
    ToontownGlobals.LawbotHQ: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 2, 'm': 2, 'l': 92, 'c': 2, 'g': 2},
            suitLevelMin=5, suitLevelMax=10,
            maxSpawnCogType=7,
            executiveSpawnChance=20,
            skelecogSpawnChance=15,
        ),
        cogCountRange=(6, 14),
    ),
    ToontownGlobals.LawbotOfficeExt: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'l': 100},
            suitLevelMin=7, suitLevelMax=10,
            maxSpawnCogType=8,
            executiveSpawnChance=20,
            skelecogSpawnChance=15,
        ),
        cogCountRange=(6, 14),
    ),
    ToontownGlobals.BossbotHQ: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 2, 'm': 2, 'l': 2, 'c': 92, 'g': 2},
            suitLevelMin=5, suitLevelMax=11,
            maxSpawnCogType=8,
            executiveSpawnChance=20,
            skelecogSpawnChance=15,
        ),
        cogCountRange=(6, 14),
    ),
    ToontownGlobals.BoardbotHQ: SuitBranchDefinition(
        cogSpawnDefinition=CogSpawnDefinition(
            cogTrackChances={'s': 2, 'm': 2, 'l': 2, 'c': 2, 'g': 92},
            suitLevelMin=5, suitLevelMax=9,
            maxSpawnCogType=8,
            executiveSpawnChance=20,
            skelecogSpawnChance=15,
        ),
        cogCountRange=(6, 14),
    ),
}


# Some invasion functions.
def isZoneInvasionableClient(zoneId: int = None) -> bool:
    # Get the current invasion.
    currentShard = None
    if currentShard is None:
        return False
    zoneId = zoneId or base.localAvatar.zoneId
    zoneId = ZoneUtil.getHoodId(zoneId) + 100
    if zoneId <= 100:
        return False

    # if the invasionType is a department, set track instead of type
    if currentShard.invasionType in SuitDNA.suitDepts:
        return isZoneCogInvasionable(zoneId, None, currentShard.invasionType)
    return isZoneCogInvasionable(zoneId, currentShard.invasionType)


def isZoneInvasionableAI(zoneId: int, includeEmpty: bool = False) -> bool:
    # Get the current invasion.
    if not simbase.air.suitInvasionManager.getInvading():
        if includeEmpty:
            return True
        return False
    suitTrack, suitName, flags = simbase.air.suitInvasionManager.getInvadingCog()
    zoneId = ZoneUtil.getHoodId(zoneId) + 100
    return isZoneCogInvasionable(zoneId, suitName, suitTrack)


def isZoneCogInvasionable(zoneId: int, cogType: str, suitTrack: str = None) -> bool:
    """
    Checks if a Zone is invasionable.
    :param zoneId:  The relevant zone in question.
    :param cogType: The type of Cog that is invading.
    """
    # Get the spawn def.
    branchDef = SuitHoodInfo.get(zoneId)
    if branchDef is None:
        return False
    spawnDef = branchDef.getCogSpawnDefinition()

    # If there is no suit (type), but there is a track, then it's a dept invasion. don't invade TTC
    if cogType is None and suitTrack is not None and spawnDef.maxInvasionCogTier > 0:
        return True

    # Get the cog tier.
    suitDef = SuitDefinitions.get(cogType)
    if suitDef is None:
        # Cog type not real
        return False
    cogTier = suitDef.getCogTier()
    if cogTier is None:
        # No tier specified. Bye!
        return False
    if not suitDef.spawnsInInvasion:
        # Please do not try this
        return False

    # Is this tier OK to spawn?
    if cogTier > spawnDef.getMaxInvasionCogTier():
        # We are not allowed to spawn this Cog.
        return False

    # Are the level ranges OK?
    minSuitLevel, maxSuitLevel = suitDef.levelRange
    minBranchLvl = spawnDef.getSuitLevelMin() + 1  # nerf lower level cogs spawning in higher pgs
    maxBranchLvl = spawnDef.getSuitLevelMax()
    if minSuitLevel > maxBranchLvl:
        # The branch is too low level for this cog.
        return False
    if minBranchLvl > maxSuitLevel:
        # The branch is too high level for this cog.
        return False

    # The cog can spawn here!
    return True


def getInvadingZonesString(cogType: str) -> str:
    invadingZones = text.makeCommaSeparatedItems(
        list(map(str, getInvadingHoodIds(cogType)))
    )
    if not invadingZones:
        return 'Nowhere'
    return invadingZones


def getInvadingHoodIds(cogType: str) -> List[int]:
    """Given a cog type, return all of the hoodIds that it can invade."""
    successHoods = []
    for branchId in SuitHoodInfo.keys():
        hoodId = ZoneUtil.getHoodId(branchId)
        if hoodId in successHoods:
            continue
        if isZoneCogInvasionable(branchId, cogType):
            successHoods.append(hoodId)
    return successHoods


# Zones that will only allow 1 cog per toon in battle
ONE_TO_ONE_ZONES = [
    ToontownGlobals.SillyStreet,
    ToontownGlobals.LoopyLane,
    ToontownGlobals.PunchlinePlace,
    ToontownGlobals.WackyWay
]


# highest available suit type (flunky, pencil pusher, etc)(1-based)
MAX_SUIT_TYPES_DEFAULT = 0
# same, but in cog hqs
MAX_SUIT_TYPES_HQ = 1
# same, but in facility exteriors
MAX_SUIT_TYPES_HQ_EXTERIOR = 2
# How often should skelecogs spawn in cog hqs?
HQ_SKELE_CHANCE = 0.15
# How often to upkeep and adjust suit population, in seconds.
POP_UPKEEP_DELAY = 10
POP_ADJUST_DELAY = 200
# How often to spawn a Magnate on Twilight Terrace
TWILIGHT_TERRACE_MAGNATE_CHANCE = 0.12

# Percent chance that a suit will try to join a battle based on the ratio of toons currently in the
# battle to suits that have *ever* been in the battle.  There are six possible combinations
# where a suit might be able to join.
# Starting from the left most entry,
# the first is if the suits outnumber the toons by 2,
# the second is if the suits outnumber the toons by 1,
# the third is if the suits and toons are balanced,
# the fourth is if the toons outnumber the suits by 1,
# the fifth is if the toons outnumber the suits by 2,
# and the last is if the toons outnumber the suits by 3.
# So in general, as toons outnumber suits, the chance of
# new suits joining the battle increases (at least
# with the current sets of numbers).
SUIT_JOIN_CHANCE = (1, 5, 10, 40, 60, 80)

# The time along a path, in seconds, that will be maintained
# between any two suits for spacing.
PATH_COLLISION_BUFFER = 5
# A hard maximum on the number of suits we try to put in the zone.
# This overrides any per-zone maximum specified in the above
# table, and also includes the count of building suits.  The main
# purpose of this limit is to keep us from wasting resources
# trying to squeeze 200 suits into a street where they can't
# possibly fit.  Empirically, with PATH_COLLISION_BUFFER set to 5,
# we can get as many as 80 suits on one of the long streets in
# TTC, but only about 40 on some of the shorter streets.
TOTAL_MAX_SUITS = 120

# The minimum and maximum length of a path that will be acceptable
# for a given suit assignment, in number of suit points passed.

# MIN_PATH_LEN should be at least 2, because less than that will
# cause the AI to crash with assertion failures and array
# underruns.

# The longest street is Silly Street with 192 points; a path might
# therefore need to be as long as 192 + MIN_PATH_LEN points to
# reach completion.  We define MAX_PATH_LEN to be 300 to give a
# comfortable margin; setting it higher just makes it take longer
# to discover disconnected graphs.
MIN_PATH_LEN = 40
MAX_PATH_LEN = 300

# Suits on the takeover march are allowed shorter paths.
MIN_TAKEOVER_PATH_LEN = 2
SUITS_ENTER_BUILDINGS = 1

# The number of additional suits contributed to the zone by each
# building, at any given time.  This may be a floating-point
# number if necessary.
SUIT_BUILDING_NUM_SUITS = 1.5

# Suit building timeouts.  A particular hood may only have so many
# suit buildings.  After a building has been a suit building for a
# length of time, it is automatically reconverted to a toon
# building; however, this timeout is based on the number of suit
# buildings in the block.  Thus, the more suit buildings there are
# on a particular block, the more quickly they will reconvert to
# toon buildings.  This is intended to prevent suit buildings from
# accumulating in the harder streets and never getting reclaimed.

# This table is the length of time, in *hours*, for buildings,
# with one entry for each number of buildings in the street.  None
# means no timeout.
SUIT_BUILDING_TIMEOUT = [
    None, None, None, None, None, None,
    72, 60, 48, 36, 24, 12, 6, 3, 1, 0.5
]

# How many suit buildings should there be in the whole world at
# any given time?  This is expressed as a percentage of the total
# number of buildings.
TOTAL_SUIT_BUILDING_PCT = 18

# What is the balance of suit building heights in the world?  The
# SuitPlanner will attempt to keep this relative weighted ratio of
# building heights.  For example, if the first number in the
# following list is 12 and the second number is 24, and the sum of
# all of the numbers in the list is 85, then 12/85 of the
# buildings in the world will be 1-story, and 24/85 will be
# 2-story.
BUILDING_HEIGHT_DISTRIBUTION = [14, 18, 25, 23, 20]

TOTAL_BWEIGHT = 0
TOTAL_BWEIGHT_PER_TRACK = {dept: 0 for dept in indexToCogDepartment}
TOTAL_BWEIGHT_PER_HEIGHT = {level: 0 for level in range(6)}

for currHoodInfo in SuitHoodInfo.values():
    weight = currHoodInfo.getBuildingWeight()
    tracks = currHoodInfo.getCogSpawnDefinition().getCogTrackChances()
    levels = currHoodInfo.getCogSpawnDefinition().getSuitLevelRange()
    heights = [0, 0, 0, 0, 0, 0]
    for level in levels:
        maxFloors = ClashSuitBuildingGlobals.getSuitBuildingInfo(level - 1).floors
        for i in range(maxFloors - 1, maxFloors):
            heights[i] += 1

    currHoodInfo.buildingHeights = heights
    TOTAL_BWEIGHT += weight
    for dept, trackWeight in tracks.items():
        TOTAL_BWEIGHT_PER_TRACK[dept] += weight * trackWeight

    for i in range(0, 6):  # we have 6 possible building levels
        TOTAL_BWEIGHT_PER_HEIGHT[i] += weight * heights[i]
