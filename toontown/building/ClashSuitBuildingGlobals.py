"""
Date: 8/14/01
Author: jlbutler
"""

from enum import IntEnum, auto

from panda3d.core import ConfigVariableDouble, ConfigVariableInt

from toontown.building.ElevatorConstants import *
from toontown.toonbase import ToontownGlobals


VICTORY_RUN_TIME = ElevatorData[ELEVATOR_NORMAL]['openTime'] + TOON_VICTORY_EXIT_TIME
TO_TOON_BLDG_TIME = 8
VICTORY_SEQUENCE_TIME = VICTORY_RUN_TIME + TO_TOON_BLDG_TIME
CLEAR_OUT_TOON_BLDG_TIME = 4
TO_SUIT_BLDG_TIME = 8

LEVEL_CLEAR_OUT_TOON_BLDG_TIME = 9


class SuitPlannerEnum(IntEnum):
    BLDG_FLOOR_1 = 0
    BLDG_FLOOR_2 = auto()
    BLDG_FLOOR_3 = auto()
    BLDG_FLOOR_4 = auto()
    BLDG_FLOOR_5 = auto()
    BLDG_FLOOR_6 = auto()
    BLDG_FLOOR_7 = auto()
    BLDG_FLOOR_8 = auto()
    BLDG_FLOOR_9 = auto()
    BLDG_FLOOR_10 = auto()
    BLDG_FLOOR_11 = auto()
    # Boss Planners
    VP = auto()
    VP_SKELECOGS = auto()
    CFO = auto()
    CFO_SKELECOGS = auto()
    CLO = auto()
    CLO_SKELECOGS = auto()
    CEO = auto()
    CEO_DINERS = auto()
    CM = auto()
    CM_SKELECOGS = auto()
    VP_EASY = auto()
    VP_SKELECOGS_EASY = auto()
    VP_HARD = auto()
    VP_SKELECOGS_HARD = auto()
    VP_VERY_EASY = auto()
    VP_SKELECOGS_VERY_EASY = auto()
    CFO_EASY = auto()
    CFO_SKELECOGS_EASY = auto()
    CFO_HARD = auto()
    CFO_SKELECOGS_HARD = auto()
    CLO_EASY = auto()
    CLO_SKELECOGS_EASY = auto()
    CLO_HARD = auto()
    CLO_SKELECOGS_HARD = auto()
    CEO_EASY = auto()
    CEO_HARD = auto()
    HARDMODE_CLO = auto()
    HARDMODE_CLO_SKELECOGS = auto()

    DERRICK_MAN = auto()
    LAND_ACQUISITION = auto()
    COUNT_SKELECOGS_VERY_EASY = auto()
    COUNT_SKELECOGS_EASY = auto()
    COUNT_SKELECOGS = auto()
    COUNT_SKELECOGS_HARD = auto()
    COUNT_SKELECOGS_VERY_HARD = auto()
    COUNT_SKELECOGS_SUPER_VERY_HARD = auto()
    WSI_BACKUP = auto()

    def __repr__(self):
        for m in self.__class__:
            if m.value == self.value:
                return m.name
        return ""

# Handy dandy alias
SPE = SuitPlannerEnum

AllSuitBuildingInfo = {}

class SuitBuildingInfo:
    def __init__(self, suitPlannerEnum: SPE, floors: int=1,
                 suitLevels: tuple=(1, 1), suitBossLevels: tuple=(1, 1),
                 levelPool: tuple=(1, 1), levelPoolMults: tuple=(1, 1),
                 exeChance: float=0.0, revives: tuple=(0, 0)) -> None:
        self.suitPlannerEnum = suitPlannerEnum
        self.floors = floors
        self.suitLevels = suitLevels
        self.suitBossLevels = suitBossLevels
        self.levelPool = levelPool
        self.levelPoolMults = levelPoolMults
        self.exeChance = exeChance
        self.revives = revives
        AllSuitBuildingInfo[suitPlannerEnum] = self


def getSuitBuildingInfo(difficulty: int) -> SuitBuildingInfo:
    return AllSuitBuildingInfo[SPE(difficulty)]


SuitBuildingInfo(
    SPE.BLDG_FLOOR_1, floors=1, suitLevels=(1, 2), suitBossLevels=(3, 3),
    levelPool=(8, 10), levelPoolMults=(1,), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_2, floors=2, suitLevels=(2, 3), suitBossLevels=(4, 4),
    levelPool=(10, 11), levelPoolMults=(1, 1.2), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_3, floors=2, suitLevels=(3, 4), suitBossLevels=(5, 5),
    levelPool=(12, 13), levelPoolMults=(1, 1.3, 1.6), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_4, floors=3, suitLevels=(4, 6), suitBossLevels=(7, 7),
    levelPool=(14, 15), levelPoolMults=(1, 1.4, 1.8), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_5, floors=3, suitLevels=(5, 7), suitBossLevels=(8, 8),
    levelPool=(16, 17), levelPoolMults=(1, 1.6, 1.8, 2), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_6, floors=4, suitLevels=(6, 8), suitBossLevels=(9, 9),
    levelPool=(17, 18), levelPoolMults=(1, 1.6, 2, 2.4), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_7, floors=4, suitLevels=(7, 9), suitBossLevels=(10, 10),
    levelPool=(18, 19), levelPoolMults=(1, 1.6, 1.8, 2.2, 2.4), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_8, floors=5, suitLevels=(8, 12), suitBossLevels=(13, 13),
    levelPool=(18, 19), levelPoolMults=(1, 1.8, 2.4, 3, 3.2), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_9, floors=5, suitLevels=(9, 13), suitBossLevels=(14, 14),
    levelPool=(20, 22), levelPoolMults=(1.4, 1.8, 2.6, 3.4, 4, 4.8), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_10, floors=6, suitLevels=(10, 15), suitBossLevels=(16, 16),
    levelPool=(22, 26), levelPoolMults=(1.8, 2.6, 3.4, 4, 4.8, 5.6), exeChance=0.2
)
SuitBuildingInfo(
    SPE.BLDG_FLOOR_11, floors=6, suitLevels=(11, 16), suitBossLevels=(17, 17),
    levelPool=(24, 30), levelPoolMults=(2.0, 2.8, 3.6, 4.2, 5, 5.8), exeChance=0.2
)
SuitBuildingInfo(
    SPE.VP, suitLevels=(5, 13), suitBossLevels=(13, 13),
    levelPool=(100, 100), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.VP_SKELECOGS, suitLevels=(8, 13), suitBossLevels=(13, 13),
    levelPool=(125, 125), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CFO, suitLevels=(6, 14), suitBossLevels=(14, 14),
    levelPool=(100, 100), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CFO_SKELECOGS, suitLevels=(8, 14), suitBossLevels=(14, 14),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CLO, suitLevels=(6, 16), suitBossLevels=(16, 16),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CLO_SKELECOGS, suitLevels=(9, 16), suitBossLevels=(16, 16),
    levelPool=(175, 175), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CEO, suitLevels=(8, 18), suitBossLevels=(18, 18),
    levelPool=(200, 200), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CEO_DINERS, suitLevels=(10, 12), suitBossLevels=(12, 12),
    levelPool=(206, 206), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CM, suitLevels=(5, 20), suitBossLevels=(20, 20),
    levelPool=(206, 206), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CM_SKELECOGS, suitLevels=(10, 20), suitBossLevels=(20, 20),
    levelPool=(206, 206), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.VP_EASY, suitLevels=(5, 12), suitBossLevels=(12, 12),
    levelPool=(100, 100), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.VP_SKELECOGS_EASY, suitLevels=(7, 12), suitBossLevels=(12, 12),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.VP_HARD, suitLevels=(6, 14), suitBossLevels=(14, 14),
    levelPool=(100, 100), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.25
)
SuitBuildingInfo(
    SPE.VP_SKELECOGS_HARD, suitLevels=(9, 14), suitBossLevels=(14, 14),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.25
)
SuitBuildingInfo(
    SPE.VP_VERY_EASY, suitLevels=(5, 11), suitBossLevels=(11, 11),
    levelPool=(100, 100), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.VP_SKELECOGS_VERY_EASY, suitLevels=(6, 11), suitBossLevels=(11, 11),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CFO_EASY, suitLevels=(5, 13), suitBossLevels=(13, 13),
    levelPool=(100, 100), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CFO_SKELECOGS_EASY, suitLevels=(8, 13), suitBossLevels=(13, 13),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CFO_HARD, suitLevels=(7, 15), suitBossLevels=(15, 15),
    levelPool=(100, 100), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.25
)
SuitBuildingInfo(
    SPE.CFO_SKELECOGS_HARD, suitLevels=(9, 15), suitBossLevels=(15, 15),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.25
)
SuitBuildingInfo(
    SPE.CLO_EASY, suitLevels=(5, 15), suitBossLevels=(15, 15),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CLO_SKELECOGS_EASY, suitLevels=(8, 15), suitBossLevels=(15, 15),
    levelPool=(175, 175), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CLO_HARD, suitLevels=(7, 17), suitBossLevels=(17, 17),
    levelPool=(150, 150), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.25
)
SuitBuildingInfo(
    SPE.CLO_SKELECOGS_HARD, suitLevels=(9, 17), suitBossLevels=(17, 17),
    levelPool=(175, 175), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.25
)
SuitBuildingInfo(
    SPE.CEO_EASY, suitLevels=(7, 17), suitBossLevels=(17, 17),
    levelPool=(200, 200), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.CEO_HARD, suitLevels=(9, 19), suitBossLevels=(19, 19),
    levelPool=(200, 200), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.25
)
SuitBuildingInfo(
    SPE.HARDMODE_CLO, suitLevels=(10, 20), suitBossLevels=(20, 20),
    levelPool=(170, 170), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.HARDMODE_CLO_SKELECOGS, suitLevels=(12, 20), suitBossLevels=(20, 20),
    levelPool=(170, 170), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.DERRICK_MAN, suitLevels=(1, 4), suitBossLevels=(4, 4),
    levelPool=(12, 12), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.LAND_ACQUISITION, suitLevels=(3, 5), suitBossLevels=(5, 5),
    levelPool=(36, 36), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.2
)
SuitBuildingInfo(
    SPE.COUNT_SKELECOGS_VERY_EASY, suitLevels=(5, 7), suitBossLevels=(10, 10),
    levelPool=(144, 144), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.3
)
SuitBuildingInfo(
    SPE.COUNT_SKELECOGS_EASY, suitLevels=(6, 8), suitBossLevels=(11, 11),
    levelPool=(144, 144), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.3
)
SuitBuildingInfo(
    SPE.COUNT_SKELECOGS, suitLevels=(7, 9), suitBossLevels=(12, 12),
    levelPool=(144, 144), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.3
)
SuitBuildingInfo(
    SPE.COUNT_SKELECOGS_HARD, suitLevels=(8, 10), suitBossLevels=(13, 13),
    levelPool=(144, 144), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.3
)
SuitBuildingInfo(
    SPE.COUNT_SKELECOGS_VERY_HARD, suitLevels=(9, 11), suitBossLevels=(14, 14),
    levelPool=(144, 144), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.3
)
SuitBuildingInfo(
    SPE.COUNT_SKELECOGS_SUPER_VERY_HARD, suitLevels=(10, 12), suitBossLevels=(15, 15),
    levelPool=(144, 144), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.3
)
SuitBuildingInfo(
    SPE.WSI_BACKUP, suitLevels=(12, 17), suitBossLevels=(17, 17),
    levelPool=(300, 300), levelPoolMults=(1, 1, 1, 1, 1), exeChance=0.33
)
