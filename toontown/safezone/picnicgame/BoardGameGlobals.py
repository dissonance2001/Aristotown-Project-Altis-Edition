from enum import IntEnum
from typing import Dict, List, Optional

from direct.distributed.ClockDelta import globalClockDelta
from panda3d.core import Vec4

from toontown.utils.AstronStruct import AstronStruct


# How many turns must pass before we give out rewards?
REWARD_TURN_LIMIT = 20
# How much time must pass since starting the game before we give out rewards?
REWARD_TIME_LIMIT = 120


class BoardGameColor(IntEnum):
    NONE = 0
    WHITE = 1
    BLACK = 2


# Total size of the board.
BOARD_SIZE: int = 64
# The length of either axis. (x, y)
AXIS_LENGTH: int = 8

VALID_MOVE_COLOR_ON = (1, 1, 1, 0.5)
VALID_MOVE_COLOR_OFF = (1, 1, 1, 0.1)

# Constants for chess clock
PLAYER_TIME = 300  # How much time to start with initially (in sec)
PLAYER_TIME_INC = 12  # How much to increment the player's clock by for each turn (in sec)
PLAYER_TIME_MAX = 600  # How much time can a player have at max (in sec)

PIECE_TINT_COLOR = Vec4(.25, .25, .25, .5)

PIECE_COLORS = {
    BoardGameColor.WHITE: (1, 1, 1, 1),
    BoardGameColor.BLACK: (0.2, 0.2, 0.2, 1)
}


def getToonPanels():
    from toontown.gui.game.condition.ConditionGlobals import ConditionSide

    return list(base.cr.gameGui.getConditionUIManager().objectFrames[ConditionSide.LEFT].values())


class ChessClock(AstronStruct):
    """
    Responsible for keeping track of the amount of time remaining for each player to make their move.
    """

    def __init__(self, players: Optional[List[int]] = None) -> None:
        self.playerTimeLeft: Dict[int, float] = {avId: PLAYER_TIME for avId in (players or [])}

    def __setitem__(self, key: int, value: float) -> None:
        self.playerTimeLeft[key] = value

    def __getitem__(self, item: int) -> float:
        return self.playerTimeLeft[item]

    def cleanup(self) -> None:
        self.playerTimeLeft = {}

    def toStruct(self):
        return [(avId, self.convertLocalToNetworkT(timeLeft)) for avId, timeLeft in self.playerTimeLeft.items()]

    def fromStruct(self, struct):
        self.playerTimeLeft = {avId: self.convertNetworkToLocalT(timeLeft) for avId, timeLeft in struct}

    def setPlayerTimeLeft(self, avId: int, t: float) -> None:
        self.playerTimeLeft[avId] = self.convertNetworkToLocalT(t)

    def copy(self):
        return self.playerTimeLeft.copy()

    @staticmethod
    def convertNetworkToLocalT(t: float) -> float:
        return globalClockDelta.networkToLocalTime(t, globalClock.getFrameTime(), bits=32)

    @staticmethod
    def convertLocalToNetworkT(t: float) -> float:
        return globalClockDelta.localToNetworkTime(t + globalClock.getFrameTime(), bits=32)
