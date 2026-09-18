"""
Globals-specific definitions file for Estate doors.
"""
from enum import Enum, unique, auto


@unique
class EstateDoorType(Enum):
    # Determines the type of Door spawned.
    DEBUG = auto()

    # Classic Doors (doors_practical)
    CLASSIC_DOUBLE_PILLARS_UR = auto()
    CLASSIC_DOUBLE_CURVED_UR  = auto()
    CLASSIC_DOUBLE_SQUARE_UR  = auto()
    CLASSIC_DOUBLE_ROUND_UR   = auto()
    CLASSIC_DOUBLE_CLOTHSHOP  = auto()

    SELLBOT_COG_HQ = auto()

