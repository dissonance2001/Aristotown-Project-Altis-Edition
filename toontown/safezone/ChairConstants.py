class ChairTypeEnum:
    COUCH = 1
    CHAIR = 2
    BOOTH = 3
    BENCH = 4
    GAMING_CHAIR = 5
    TRASH_CAN = 6


class MusicTypeEnum:
    DEFAULT = 1
    LAWBBY = 2
    OCLO = 3
    PACESETTER = 4


musicEnum2Name = {
    MusicTypeEnum.DEFAULT: "picnic",
    MusicTypeEnum.LAWBBY: "lawfice_lobby",
    MusicTypeEnum.OCLO: "oclo",
    MusicTypeEnum.PACESETTER: "pacesetter",
}

# Chairs that take the true position, ignoring position offsets
truePositionChairs = {
    ChairTypeEnum.TRASH_CAN,
}

# Chairs that have you stand in them.
standingChairs = {
    ChairTypeEnum.TRASH_CAN,
}