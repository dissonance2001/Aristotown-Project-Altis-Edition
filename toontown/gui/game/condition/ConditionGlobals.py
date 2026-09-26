"""
A module for storing constant definitions for the Condition UI system.
"""
from enum import IntEnum, auto

from toontown.gui.GUIPositionGlobals import ScreenCorner
from toontown.toonbase import ToontownGlobals

"""
UIManager-specific enums
"""


class ConditionSide(IntEnum):
    LEFT = auto()
    RIGHT = auto()


SideAnchors = {
    ConditionSide.LEFT:  base.a2dBottomLeft,
    ConditionSide.RIGHT: base.a2dBottomRight,
}

SideCorners = {
    ConditionSide.LEFT:  ScreenCorner.LEFT_MIDDLE,
    ConditionSide.RIGHT: ScreenCorner.RIGHT_MIDDLE,
}
SideReverseCorners = {
    ConditionSide.LEFT:  ScreenCorner.RIGHT_MIDDLE,
    ConditionSide.RIGHT: ScreenCorner.LEFT_MIDDLE,
}

StandardFrameScale = 1.0
SmallFrameScale = 0.72
SmallBattleFrameScale = 0.90


"""
Condition Args
These provide information for Condition Subframes.
(Basically just a glorified dictionary...)  
"""


class ConditionArg(IntEnum):
    """
    Enums for condition args
    """

    # General
    AVID = auto()
    NAME = auto()
    TOON_LEVEL = auto()
    HEAD_DATA = auto()
    HP = auto()
    MAX_HP = auto()
    TOON_XP = auto()
    TOON_MAX_XP = auto()
    SYNC = auto()

    # Dept exp
    DEPT_XP = auto()
    DEPT_MAX_XP = auto()
    DEPT_LEVEL = auto()
    DEPT_TYPE = auto()

    # Activity exp
    ACTIVITY_XP = auto()
    ACTIVITY_MAX_XP = auto()
    ACTIVITY_LEVEL = auto()
    ACTIVITY_TYPE = auto()

    # Activity specific
    RACING_PLACEMENT = auto()
    PGT_PLAYER_STATE = auto()
    PGT_PLAYER_INFO = auto()
    PGT_GAME_TYPE = auto()

    # Suits (For suit subframes)
    SUIT_LEVEL = auto()
    SUIT_DEPT = auto()
    SUIT_TYPE = auto()
    SUIT_EXE = auto()
    SUIT_MINIBOSS = auto()
    SUIT_REVIVES = auto()

    # Bosses (For toon subframes)
    BOSS_PIE_TYPE = auto()
    BOSS_PIE_COUNT = auto()
    BOSS_CRANE_CONTROLLED = auto()
    BOSS_SOUND_TYPE = auto()
    BOSS_SOUND_COUNT = auto()
    BOSS_TABLE_CONTROLLED = auto()

    # Bosses (For boss subframes)
    BOSS_DEPT = auto()
    BOSS_SAFE_STATE = auto()

    # Toon Tips
    TIP_TITLE = auto()
    TIP_DESCRIPTION = auto()

    # All timed release frames
    TIMED_RELEASE_DURATION = auto()

    HAMMERSPACE_ITEM = auto()


class ConditionArgs(dict):
    pass


"""
ConditionState logic
"""


class ConditionState(IntEnum):
    """
    Enums for states
    """
    GLOBAL = auto()

    BOARDING = auto()

    BATTLE_TURN = auto()
    BATTLE_MOVIE = auto()

    BOSS_VP = auto()
    BOSS_CFO = auto()
    BOSS_CLO = auto()
    BOSS_CEO = auto()

    ACTIVITY_FISHING = auto()
    ACTIVITY_GOLFING = auto()
    ACTIVITY_RACING = auto()
    ACTIVITY_TROLLEY = auto()

    PGT_TABLE = auto()
    PGT_TOONO = auto()
    PGT_CHECKERS = auto()
    PGT_CHESS = auto()


BOSS_CONDITION_STATES: dict[ConditionState, int] = {
    ConditionState.BOSS_VP: 4,
    ConditionState.BOSS_CFO: 3,
    ConditionState.BOSS_CLO: 2,
    ConditionState.BOSS_CEO: 1,
}

ACTIVITY_CONDITION_STATES: dict[ConditionState, int] = {
    ConditionState.ACTIVITY_FISHING: ToontownGlobals.ACTIVITY_FISHING,
    ConditionState.ACTIVITY_GOLFING: ToontownGlobals.ACTIVITY_GOLFING,
    ConditionState.ACTIVITY_RACING: ToontownGlobals.ACTIVITY_RACING,
    ConditionState.ACTIVITY_TROLLEY: ToontownGlobals.ACTIVITY_TROLLEY,
}

PGT_STATES = [ConditionState.PGT_TABLE, ConditionState.PGT_TOONO, ConditionState.PGT_CHESS, ConditionState.PGT_CHECKERS]

"""
Condition State Kwargs
(I can't help myself)
"""


class ConditionStateArg(IntEnum):
    """
    Enums for condition state args
    """
    BOSS = auto()
    BATTLE = auto()
    RACETRACK = auto()
    ELEVATOR = auto()
    TROLLEY = auto()
    PICNIC_TABLE = auto()
    PICNIC_GAME = auto()


class ConditionStateArgs(dict):
    pass


"""
Condition Icons
"""


class ConditionIconType(IntEnum):
    """
    The type of ConditionIcon to be present.
    """
    TARGET_ARROW = auto()
    HEAL_ARROW = auto()

    RACING_GAG_BANANA = auto()
    RACING_GAG_BATTERY = auto()
    RACING_GAG_PIE = auto()
    RACING_GAG_TNT = auto()
    RACING_GAG_LIGHTNING = auto()
    RACING_GAG_QUICKSAND = auto()
    RACING_GAG_PIE_SLICE = auto()
    RACING_GAG_TEETH = auto()
    RACING_GAG_PIXIE_DUST = auto()
    RACING_GAG_BOWLING_BALL = auto()


"""
Message Definitions
"""

RefreshMsg         = 'CONDITION-UI-REFRESH'  # []
SetStateMsg        = 'CONDITION-UI-SET-STATE'  # [ConditionState, ConditionStateArgs (optional)]
AskIconMsg         = 'CONDITION-UI-ICON'  # [obj, ConditionIconType]
AddTimedReleaseMsg = 'CONDITION-UI-ADD-TIMED-RELEASE-FRAME'  # [obj, duration]
