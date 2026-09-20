"""
All of the defined definitions for the Instance Mercenaries for 1.3.
Can be expanded with more and more zones, in case we want to make more instance bosses.
"""

from enum import IntEnum, auto
from typing import Optional

from direct.showbase.PythonUtil import invertDict

from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from toontown.quest3.QuestEnums import QuestSource
from toontown.quest3.base.QuestHistory import QuestHistory
from toontown.quest3.base.QuestReference import QuestId
from toontown.toonbase.ToontownGlobals import getNewReservedZoneId, Gagsoline

# Some of the difficulty enums.
NORMAL = 0
OVERCLOCKED = 1


# Class to hold information for each merc.
class MercDefinition:
    """Simple class to hold information about a defined merc."""
    def __init__(self, cogName, zoneId, requiredTaskID, cogLevelsInDifficulty,
                 battleCap, safeZone, musicKeySuffix, difficultyKey,
                 contentSync: ContentSyncType = None):
        self.cogName = cogName
        self.zoneId = zoneId
        self.requiredTaskID: QuestId = requiredTaskID
        self.reservedZone = getNewReservedZoneId()
        self.cogLevelsInDifficulty = cogLevelsInDifficulty
        self.difficultyCount = len(cogLevelsInDifficulty)
        self.battleCap = battleCap
        self.startingDifficulty = 2 - self.difficultyCount
        self.safeZone = safeZone
        self.musicKeySuffix = musicKeySuffix
        self.difficultyKey = difficultyKey
        self.contentSync = contentSync

    def getContentSync(self) -> Optional[ContentSyncType]:
        return self.contentSync

    def getSafeZone(self) -> int:
        return self.safeZone

    def makeDifficultyRange(self) -> tuple:
        """Makes the difficulty range to be use for boarding parties."""
        assert self.difficultyKey in ElevatorInstanceDifficulty
        return ElevatorInstanceDifficulty[self.difficultyKey]


class MercDefinitionError(Exception):
    pass


# Enums for every existing merc.
MERC_PRETHINKER   = 1
MERC_RAINMAKER    = 2
MERC_WITCHHUNTER  = 3
MERC_MULTISLACKER = 4
MERC_MAJORPLAYER  = 5
MERC_PLUTOCRAT    = 6
MERC_CHAINSAW     = 7
MERC_PACESETTER   = 8
MERC_HIGHROLLER   = 9

# Definitions for each merc enum.
MercDefinitions = {
    MERC_PRETHINKER:   MercDefinition('prethink', 2000,  QuestId(QuestSource.KudosQuest, 9, 5),  (12, 12), (4, 4),  2000, 'prethinker',   'normal-overclocked', ContentSyncType.KUDOS_TTC),
    MERC_RAINMAKER:    MercDefinition('rainmake', 1315,  QuestId(QuestSource.KudosQuest, 19, 7), (16, 16), (4, 6),  1000, 'rainmaker',    'normal-overclocked', ContentSyncType.KUDOS_BB),
    MERC_WITCHHUNTER:  MercDefinition('whunter',  7000,  QuestId(QuestSource.KudosQuest, 29, 6), (20, 20), (4, 5),  7000, 'witchhunter',  'normal-overclocked', ContentSyncType.KUDOS_YOTT),
    MERC_MULTISLACKER: MercDefinition('mslacker', 10101, QuestId(QuestSource.KudosQuest, 39, 4), (24, 24), (4, 6),  5000, 'multislacker', 'normal-overclocked', ContentSyncType.KUDOS_DG),
    MERC_MAJORPLAYER:  MercDefinition('mplayer',  4874,  QuestId(QuestSource.KudosQuest, 49, 4), (28, 28), (4, 5),  4000, 'majorplayer',  'normal-overclocked', ContentSyncType.KUDOS_MML),
    MERC_PLUTOCRAT:    MercDefinition('pcrat',    3740,  QuestId(QuestSource.KudosQuest, 59, 7), (38, 38), (4, 5),  3000, 'plutocrat',    'normal-overclocked', ContentSyncType.KUDOS_TB),
    MERC_CHAINSAW:     MercDefinition('chainsaw', 6837,  QuestId(QuestSource.KudosQuest, 69, 5), (50, 50), (4, 5),  6000, 'chainsaw',     'normal-overclocked', ContentSyncType.KUDOS_AA),
    MERC_PACESETTER:   MercDefinition('psetter',  9613,  QuestId(QuestSource.KudosQuest, 79, 2), (66, 66), (5, 6),  9000, 'pacesetter',   'normal-overclocked', ContentSyncType.KUDOS_DDL),
    MERC_HIGHROLLER:   MercDefinition('hroller',  4874,  None, (100, 100), (4, 5),  4000, 'highroller', 'overclocked',      ContentSyncType.EVENT_HIGH_ROLLER),
}

# Keys to define instance difficulty.
ElevatorInstanceDifficulty = {
    'normal-overclocked': (
        NORMAL,
        OVERCLOCKED,
    ),
    'overclocked': (
        OVERCLOCKED,
    ),
}

# Merc ID to InstanceNotAvailable index
MercIdToQuestINADenial = {
    MERC_MAJORPLAYER: 10,
    MERC_PACESETTER: 13,
}


# I have to do this to be able to properly pass their names through astron,
# for when the plutocrat talks when each investor dies. I do not like it.
class SatelliteInvestorsEnum(IntEnum):
    CHARON = auto()
    NIX = auto()
    HYDRA = auto()
    STYX = auto()
    KERBEROS = auto()


InvestorName2Enum = {
    'charon': SatelliteInvestorsEnum.CHARON,
    'nix': SatelliteInvestorsEnum.NIX,
    'hydra': SatelliteInvestorsEnum.HYDRA,
    'styx': SatelliteInvestorsEnum.STYX,
    'kerberos': SatelliteInvestorsEnum.KERBEROS
}
InvestorEnum2Name = invertDict(InvestorName2Enum)


# Helper lists.
MercDefinitionsList = list(MercDefinitions.values())
MercNames           = list(mercDef.cogName for mercDef in MercDefinitionsList)
MercInstanceIDs     = list(mercDef.zoneId  for mercDef in MercDefinitionsList)

# Chances for dropping stickers/accessories from mercs
MercLootBaseChance = 0.015
MercLootPity = 0.0035
# Same, but for specifically legendary rarity
MercLootLegendaryChance = 0.0
MercLootLegendaryPity = 0.001
# I am the commonwealth
MercLootCommonChance = 0.25
MercLootCommonPity = 0.05


# Helper functions.
def mercEnumToZoneId(mercEnum) -> int:
    """Gets a merc enumerator, returns its zone id."""
    return MercDefinitions[mercEnum].zoneId


def mercEnumToCogName(mercEnum) -> str:
    """Gets a merc enumerator, returns its cog key."""
    return MercDefinitions[mercEnum].cogName


def mercZoneIdToMercEnum(zoneId) -> int:
    """Take's a merc's zone ID, returns its MercDefinition."""
    for mercEnum in MercDefinitions:
        if MercDefinitions[mercEnum].zoneId == zoneId:
            return mercEnum
    raise MercDefinitionError(f"Non-existent zoneId was passed! {zoneId}")


def mercZoneIdToMercDefinition(zoneId) -> MercDefinition:
    """Take's a merc's zone ID, returns its MercDefinition."""
    return MercDefinitions[mercZoneIdToMercEnum(zoneId)]


def mercZoneIdToReservedZone(zoneId) -> int:
    """Takes a merc's zone ID, returns its reserved zone."""
    return mercZoneIdToMercDefinition(zoneId).reservedZone


def mercReservedZoneToMercEnum(reservedZone) -> int:
    """Take's a merc's reservedZone, returns its MercDefinition."""
    for mercEnum in MercDefinitions:
        if MercDefinitions[mercEnum].reservedZone == reservedZone:
            return mercEnum
    raise MercDefinitionError(f"Non-existent reservedZone was passed! {reservedZone}")


def mercReservedZoneToMercDefinition(reservedZone) -> MercDefinition:
    """Take's a merc's reservedZone, returns its MercDefinition."""
    return MercDefinitions[mercReservedZoneToMercEnum(reservedZone)]


def mercDefinitionToEnum(mercDef: MercDefinition) -> int:
    """Take's a merc's definition object, returns its enum."""
    for mercEnum in MercDefinitions:
        if MercDefinitions[mercEnum] == mercDef:
            return mercEnum
    raise MercDefinitionError(f"Non-existent MercDefinition was passed! {mercDef}")
