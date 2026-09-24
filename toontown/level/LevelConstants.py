"""LevelConstants module: contains Level-related constants"""

from enum import Enum, auto

# zone Num from model is also the Zone Entity's entId
MinZoneNum = 0
MaxZoneNum = 999

# zoneNum 0 is reserved for UberZone
UberZoneEntId = 0

# system-allocated entities start at 1000
LevelMgrEntId = 1000
EditMgrEntId = 1001
BuildingMgrEntId = 1002


class LevelType(Enum):
    Standard = auto()
    Persistent = auto()


# Bulletin Board values
Bulletin_IgnoreLoad = 'DistributedPersistentLevel-IgnoreLoad'
Bulletin_IgnoreTitleText = 'DistributedPersistentLevel-IgnoreTitleText'
