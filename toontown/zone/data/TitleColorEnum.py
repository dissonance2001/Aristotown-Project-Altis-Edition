from typing import Dict

from panda3d.core import Vec4
from strenum import StrEnum


class TitleColorEnum(StrEnum):
    Default = "default"
    TTC = "ttc"
    BB = "bb"
    YOTT = "yott"
    YOTT_FILTER = "yott_filter"
    DG = "dg"
    MML = "mml"
    TB = "tb"
    TST = "tst"
    AA = "aa"
    RR = "rr"
    MG = "mg"
    SC = "sc"
    DDL = "ddl"
    CogHQ = "coghq",
    SBHQ = "sbhq",
    CBHQ = "cbhq",
    LBHQ = "lbhq",
    BBHQ = "bbhq",
    BDHQ = "bdhq",


TitleColorRegistry: Dict[StrEnum, Vec4] = {
    TitleColorEnum.Default: (0.3, 0.3, 1.0, 1.0),
    TitleColorEnum.TTC: (1.0, 0.5, 0.4, 1.0),
    TitleColorEnum.BB: (0.8, 0.6, 0.5, 1.0),
    TitleColorEnum.YOTT_FILTER: (0.8, 0.8, 0.8, 1.0),
    TitleColorEnum.YOTT: (0.6, 0.5, 0.8, 1.0),
    TitleColorEnum.DG: (0.8, 0.6, 1.0, 1.0),
    TitleColorEnum.MML: (1.0, 0.5, 0.5, 1.0),
    TitleColorEnum.TB: (0.3, 0.6, 1.0, 1.0),
    TitleColorEnum.AA: (0.6, 0.45, 0.25, 1.0),
    TitleColorEnum.DDL: (1.0, 0.9, 0.5, 1.0),
    TitleColorEnum.RR: (1.0, 0.5, 0.4, 1.0),
    TitleColorEnum.MG: (1.0, 0.5, 0.4, 1.0),
    TitleColorEnum.TST: (0.3, 0.6, 1.0, 1.0),
    TitleColorEnum.SC: (0.3, 0.6, 1.0, 1.0),
    TitleColorEnum.CogHQ: (0.5, 0.5, 0.5, 1.0),
    TitleColorEnum.SBHQ: (0.761, 0.678, 0.69, 1.0),
    TitleColorEnum.CBHQ: (0.596, 0.714, 0.659, 1.0),
    TitleColorEnum.LBHQ: (0.588, 0.635, 0.671, 1.0),
    TitleColorEnum.BBHQ: (0.647, 0.608, 0.596, 1.0),
    TitleColorEnum.BDHQ: (0.5, 0.5, 0.5, 1.0),
}
