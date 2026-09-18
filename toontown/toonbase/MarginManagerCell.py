"""
To help manage the MarginManager, we use enums to directly reference each cell on screen.
This also holds the areas for CellFlags, which marks a cell to be disabled if it has flags.
"""
from enum import Enum, auto


class ScreenCell(Enum):
    """
    Direct reference to a cell on the screen.
    """
    LeftTop = auto()
    LeftMiddle = auto()
    LeftBottom = auto()
    BottomLeft = auto()
    BottomMidLeft = auto()
    BottomMiddle = auto()
    BottomMidRight = auto()
    BottomRight = auto()
    RightTop = auto()
    RightBottom = auto()


class ScreenCellFlag(Enum):
    """
    A reason to mark the cell as being inactive for whatever reason.

    Generally make sure to leave this to be unique to whatever source
    is marking cells as inactive or not.
    """
    inBattle = auto()
    inCGCGolf = auto()
    inGolf = auto()
    cloEvidenceMeter = auto()
    cannonGui = auto()
    inCannon = auto()
    houseDesign = auto()
    halloweenShop = auto()
    npcShop = auto()
    mazeGame = auto()
    tagGame = auto()
    questChoice = auto()
    isFishing = auto()
    shtikerBook = auto()
    groupPanel = auto()
    socialPanel = auto()
    chainsawMeter = auto()
    newStickerBook = auto()

    UNUSED = auto()
