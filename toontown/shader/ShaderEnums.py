from enum import IntEnum, auto


class ShaderType(IntEnum):
    """
    A class for defining the different types of shaders.
    """
    Passthrough = auto()
    Wobble      = auto()
    LowPoly     = auto()

    Waterfall = auto()
    Ripple    = auto()

    LUT_Default    = auto()
    LUT_Augusta    = auto()
    LUT_Bloomy     = auto()
    LUT_Dark       = auto()
    LUT_Dramatic   = auto()
    LUT_Contrast   = auto()
    LUT_Monochrome = auto()
    LUT_StrongMono = auto()
    LUT_Moody      = auto()
    LUT_Pop        = auto()
    LUT_RedBlack   = auto()
    LUT_Sunset     = auto()

    LUT_Monochromacy  = auto()
    LUT_Deuteranomaly = auto()
    LUT_Protanomaly   = auto()
    LUT_Tritanomaly   = auto()
    LUT_BlueCone      = auto()
    LUT_Deuteranopia  = auto()
    LUT_Protanopia    = auto()
    LUT_Tritanopia    = auto()
