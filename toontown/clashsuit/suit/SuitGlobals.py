# SuitGlobals are used to set the appearance of Cogs.
from enum import IntEnum, auto
from panda3d.core import VBase4
from toontown.clashsuit.suit.SuitDefinitions import suitBuildHeadAttributeDict, MainlineCogs, SUIT_BODY_TYPE_WIDTH
from toontown.clashsuit.suit import SuitTimings

SCALE_INDEX = 0  # The scale of the cog
HAND_COLOR_INDEX = 1  # The hand color
HEADS_INDEX = 2  # A list of heads
SKELE_HEADS_INDEX = 3  # A list of heads to use for skelecogs
HEAD_TEXTURE_INDEX = 4  # The texture to use for the head
SKELE_HEAD_TEXTURE_INDEX = 5  # The texture to use for the skelecog head
TIE_INDEX = 6  # The tie type of the cog
BODY_TEXTURE_INDEX = 7  # The body texture of the cog
SKELE_BODY_TEXTURE_INDEX = 8  # The body texture of the skelecog
BODY_TINT_INDEX = 9  # The tint of the cog
HEIGHT_INDEX = 10  # The height of the cog
BODY_MODEL_INDEX = 11  # The body model type of the cog
# NOTE: THE FOLLOWING ARE USED FOR SPECIAL COGS ONLY
DEPT_INDEX = 12  # The dept of the cog
BODY_INDEX = 13  # The body type of the cog

ColdCallerHead = VBase4(0.25, 0.35, 1.0, 1.0)  # Head used by Cold Caller

suitIndexToLetter = MainlineCogs

suitProperties = suitBuildHeadAttributeDict()

DeptColors = (VBase4(0.531, 0.703, 0.744, 1.0),
              VBase4(0.647, 0.608, 0.596, 1.0),
              VBase4(0.588, 0.635, 0.671, 1.0),
              VBase4(0.596, 0.714, 0.659, 1.0),
              VBase4(0.761, 0.678, 0.69, 1.0))

DeptCharToInt = {
    'g': 0,
    'c': 1,
    'l': 2,
    'm': 3,
    's': 4,
}
DeptIntToChar = {
    0: 'g',
    1: 'c',
    2: 'l',
    3: 'm',
    4: 's',
}

DeptCharToTexShorthand = {
    'g': 'board',
    'c': 'boss',
    'l': 'law',
    'm': 'cash',
    's': 'sell',
}


class SuitSpawnMethod(IntEnum):
    FlyIn = auto()
    FromDoor = auto()


SpawnMethodToTiming = {
    SuitSpawnMethod.FlyIn: SuitTimings.fromSky
}
