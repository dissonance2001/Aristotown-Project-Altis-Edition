from enum import IntEnum, auto

class ChairTypeEnum(IntEnum):
    COUCH = auto()
    CHAIR = auto()
    BOOTH = auto()
    BENCH = auto()
    GAMING_CHAIR = auto()
    TRASH_CAN = auto()

class MusicTypeEnum(IntEnum):
    DEFAULT = auto()
    LAWBBY = auto()
    OCLO = auto()
    PACESETTER = auto()

musicEnum2Name = {MusicTypeEnum.DEFAULT: "picnic",
                  MusicTypeEnum.LAWBBY: "lawfice_lobby",
                  MusicTypeEnum.OCLO: "oclo",
                  MusicTypeEnum.PACESETTER: "pacesetter"}

# Chairs that take the true position, ignoring position offsets
truePositionChairs = {
    ChairTypeEnum.TRASH_CAN,
}

# Chairs that have you stand in them.
standingChairs = {
    ChairTypeEnum.TRASH_CAN,
}
