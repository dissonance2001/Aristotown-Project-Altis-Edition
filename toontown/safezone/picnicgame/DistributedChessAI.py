from typing import Dict, Optional, List

from otp.ai.AIBaseGlobal import simbase
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.safezone.picnicgame.BoardGameGlobals import PLAYER_TIME, PLAYER_TIME_INC, PLAYER_TIME_MAX, ChessClock, \
    REWARD_TIME_LIMIT, REWARD_TURN_LIMIT
from toontown.safezone.picnicgame.ChessGlobals import ChessBoard, ChessGameState, ChessMoveFlag
from toontown.safezone.picnicgame.DistributedPicnicGameAI import DistributedPicnicGameAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedChessAI(DistributedPicnicGameAI):

    def __init__(self, air, table, specialZone: Optional[SpecialQuestZones] = None) -> None:
        super().__init__(air, table, specialZone)
        self.board = ChessBoard()
        self.clock = ChessClock(self.players)
        self.drawVotes: List[int] = []

    def delete(self) -> None:
        self.board.cleanup()
        self.board = None

        self.clock.cleanup()
        self.clock = None

        self.drawVotes = []

        super().delete()

    def requestGameState(self) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        if self.ratelimiter is None or self.ratelimiter.userBlocked(avId):
            return

        av = simbase.air.getDo(avId)
        if av is None:
            return

        self.sendUpdateToAvatarId(avId, "setGameState", [self.board.getBoardState(), self.clock.toStruct()])

    def requestMove(self, start: int, target: int, flag: int) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)
        if av is None:
            return

        # This avatar isn't the current player.
        if avId != self.currentPlayer:
            return

        flag = ChessMoveFlag(flag)

        success = self.board.requestMove(start, target, flag)
        if not success:
            return

        self.d_movePiece(start, target, flag)
        self.beginTurn()

    def requestDraw(self) -> None:
        avId = simbase.air.getAvatarIdFromSender()
        if self.gameActionRatelimiter is None or self.gameActionRatelimiter.userBlocked(avId):
            return

        av = simbase.air.doId2do.get(avId)
        if av is None:
            return

        # This avatar isn't a player.
        if avId not in self.players:
            return

        # This avatar has already voted.
        if avId in self.drawVotes:
            return

        self.drawVotes.append(avId)

        # Send the vote to the client if we require the other player to vote.
        if len(self.drawVotes) < len(self.players):
            self.sendUpdate("handleDrawVote", [len(self.drawVotes), avId])
        # Otherwise, both players have voted. We can end the game.
        else:
            self.declareWinner(0)

    def beginTurn(self, task=None) -> None:
        # This function was called by the timer task, which means the current
        # player ran out of time. Declare the other player as the winner.
        if task is not None:
            self.declareWinner(next(self.playerOrder))
            return

        # Progress the board.
        gameState = next(self.board)

        if gameState != ChessGameState.PLAYING:
            # The game ended by the current player placing the opponent into checkmate.
            if gameState in (ChessGameState.CHECKMATE_WHITE, ChessGameState.CHECKMATE_BLACK):
                self.declareWinner(self.currentPlayer)
            # The game ended in a stalemate.
            else:
                self.declareWinner(0)
            return

        if self.turnEndTime is not None:
            # Their turn is over, store how much time they have left.
            self.clock[self.currentPlayer] = self.turnEndTime - globalClock.getFrameTime()

        super().beginTurn(task)

    def d_movePiece(self, start: int, target: int, flag: int) -> None:
        self.sendUpdate("movePiece", [start, target, flag])

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
