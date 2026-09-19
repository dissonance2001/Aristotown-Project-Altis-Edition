"""
Module imported on both client and server
Don't get cocky!!
"""
from enum import IntEnum, auto


class EnvironmentalEnum(IntEnum):
    BASE                      = auto()
    PERSISTENT_STATUS_EFFECTS = auto()
    CONTENT_SYNC              = auto()
    HECK_YOUR_GAG_ORDER = auto()

    RAINMAKER_WEATHER         = auto()
    PLUTOCRAT_WEATHER         = auto()
    OVERCHARGE_ALL            = auto()

    MAJOR_PLAYER_REVIVE_HANDLER = auto()
    MAJOR_PLAYER_SHUFFLE_HANDLER = auto()
    PACESETTER_GAG_ORDER = auto()
    HIGH_ROLLER_CLONE_HANDLER = auto()
    ADAPTIVE_LAFF = auto()

    # region Events
    FTF_ATTORNEY_OVERSEER = auto()
    FTF_GENERAL_RUSHJOB_TRACKER = auto()
    FTF_SUPERVISOR_CONTROLLING = auto()
    FTF_SUPERVISOR_CONFUSED_GAG_ORDER = auto()
    FTF_PRESIDENT_SHIVERING = auto()
    FTF_PRESIDENT_HIGHSTAKES = auto()
    # endregion


ENV_ENUM = EnvironmentalEnum


class RainmakerWeather(IntEnum):
    NORMAL     = auto()
    OIL_RAIN   = auto()
    FOG        = auto()
    HEAVY_RAIN = auto()
    STORM_CELL = auto()
    MONSOON    = auto()
    FINALE     = auto()


class PlutocratWeather(IntEnum):
    NORMAL      = auto()
    SNOW_SQUALL = auto()
