from typing import Dict, List

from otp.ai.AIBaseGlobal import simbase
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.safezone.picnicgame.BoardGameGlobals import PLAYER_TIME, PLAYER_TIME_INC, PLAYER_TIME_MAX, ChessClock, \
    REWARD_TURN_LIMIT, REWARD_TIME_LIMIT
from toontown.safezone.picnicgame.CheckersGlobals import CheckerBoard
from toontown.safezone.picnicgame.DistributedPicnicGameAI import DistributedPicnicGameAI


class DistributedCheckersAI(DistributedPicnicGameAI):

    def __init__(self, air, table, specialZone: SpecialQuestZones = None) -> None:
        super().__init__(air, table, specialZone)
        self.board = CheckerBoard()
        self.clock = ChessClock(self.players)

    def delete(self) -> None:
        self.board.cleanup()
        self.board = None

        self.clock.cleanup()
        self.clock = None

        super().delete()

    def requestGameState(self) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        if self.ratelimiter is None or self.ratelimiter.userBlocked(avId):
            return

        av = simbase.air.getDo(avId)
        if av is None:
            return

        self.sendUpdateToAvatarId(avId, "setGameState", [self.board.getBoardState(), self.clock.toStruct()])

    def requestMove(self, start: int, target: int) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        # This avatar doesn't exist.
        if av is None:
            return

        # This avatar isn't the current player.
        if avId != self.currentPlayer:
            return

        move = self.board.requestMove(start, target)
        if not move:
            return

        self.d_movePiece(move.start, move.target, move.captures)
        self.beginTurn()

    def beginTurn(self, task=None) -> None:
        # This function was called by the timer task, which means the current
        # player ran out of time. Declare the other player as the winner.
        if task is not None:
            self.declareWinner(next(self.playerOrder))
            return

        # Progress the board.
        if next(self.board):
            # The game ended by way of the opponent running out of moves to make.
            self.declareWinner(self.currentPlayer)
            return

        if self.turnEndTime is not None:
            # Their turn is over, store how much time they have left.
            self.clock[self.currentPlayer] = self.turnEndTime - globalClock.getFrameTime()

        super().beginTurn(task)

    def d_movePiece(self, start: int, target: int, captures: List[int]) -> None:
        self.sendUpdate("movePiece", [start, target, captures])

    def setTimerEnd(self) -> None:
        # Take the amount of time that the current player has left, add it with
        # the current frame time and the increment per player turn.
        if self.turnEndTime is None:
            self.turnEndTime = PLAYER_TIME + globalClock.getFrameTime()
        else:
            # Increment the time this player has.
            turnTime = self.clock[self.currentPlayer] + PLAYER_TIME_INC

            # Cap the amount of time they have.
            limitTurnTime = min(turnTime, PLAYER_TIME_MAX)

            self.turnEndTime = limitTurnTime + globalClock.getFrameTime()

    """
    Properties
    """

    @property
    def playerRewards(self) -> Dict[int, int]:
        # Prevent giving rewards if they haven't invested enough time into the current game.
        if self.turns <= REWARD_TURN_LIMIT or self.getGameTime() <= REWARD_TIME_LIMIT:
            return {}
        return super().playerRewards

    @property
    def batcoinRewards(self) -> int:
        # Prevent giving rewards if they haven't invested enough time into the current game.
        if self.turns <= REWARD_TURN_LIMIT or self.getGameTime() <= REWARD_TIME_LIMIT:
            return 0
        return super().batcoinRewards
