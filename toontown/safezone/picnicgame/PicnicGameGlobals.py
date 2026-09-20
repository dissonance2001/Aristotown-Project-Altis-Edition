from enum import IntEnum, auto

from panda3d.core import Vec4

# The amount of seats on the picnic table model.
NUM_SEATS = 6

# The amount of time allotted for toons to enter/exit and decide what game
# they would like to play.
BOARDING_TIME = 90

# Positions for the game choice buttons on the first leader page.
GAME_BUTTON_POS = (
    (-0.55, 0.0, -0.0),
    (0.0, 0.0, -0.0),
    (0.55, 0.0, -0.0),
)

# Map representing the player order based on their seat index.
SEAT_INDEX_ORDER = {
    0: 1,
    1: 2,
    2: 3,
    3: 6,
    4: 5,
    5: 4
}

ARROW_COLOR_RED = (1, 0, 0, 1)
ARROW_COLOR_GREEN = (0, 1, 0, 1)


# Enum for every picnic game table.
class PicnicGame(IntEnum):
    CHECKERS = 0
    CHESS    = auto()
    TOONO    = auto()


class PicnicTableState(IntEnum):
    SPECTATOR = auto()
    PLAYER = auto()
    LEADER = auto()


PGT_GAME_NAMES = ("checkers", "chess", "toono")

# How many players can play each game?
PGT_PLAYER_LIMITS = {
    PicnicGame.CHECKERS: (2, 2),
    PicnicGame.CHESS: (2, 2),
    PicnicGame.TOONO: (2, 6),
}

PGT_BASE_BEANS = 25
PGT_WINNER_MULT = 1.5


class PlayerOrder:
    """
    Represents an interface to an iterable which can be infinitely cycled (like itertools.cycle), and can be reversed.

    Starts at the first item (index 0), unless reversed before first iteration,
    in which case starts at the last item.

    >>> po = PlayerOrder(range(3))
    >>> next(po)
    0
    >>> next(po)
    1
    >>> po.reverse()
    >>> next(po)
    0
    >>> next(po)
    2
    """

    def __init__(self, players) -> None:
        self.players = list(players)
        self.startPos = 0
        self._reverse = False
        self._position = None

    def __next__(self) -> int:
        if not self.players:
            return 0
        if self._position is None:
            self.position = (-1 - self.startPos) if self._reverse else self.startPos
        else:
            self.position += self.delta
        return self.players[self.position]

    def __len__(self) -> int:
        return len(self.players)

    def reverse(self):
        self._reverse = not self._reverse

    def remove(self, player: int) -> None:
        if player in self.players:
            self.players.remove(player)

    def getNext(self) -> int:
        if not self.players:
            return 0

        if self._position is None:
            pos = -1 if self._reverse else 0
        else:
            pos = self.position + self.delta
        return self.players[pos % len(self.players)]

    def index(self, player: int) -> int:
        if player in self.players:
            return self.players.index(player)
        return -1
    
    def setStartPos(self, startPos: int) -> None:
        self.startPos = startPos

    @property
    def delta(self) -> int:
        return -1 if self._reverse else 1

    @property
    def position(self) -> int:
        return self._position

    @position.setter
    def position(self, position: int) -> None:
        self._position = position % max(len(self.players), 1)
