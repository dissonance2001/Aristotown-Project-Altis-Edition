from typing import List, Optional, Tuple, Dict

from toontown.safezone.picnicgame.BoardGameGlobals import BoardGameColor, AXIS_LENGTH, BOARD_SIZE

FINAL_RANK: Dict[BoardGameColor, int] = {
    BoardGameColor.WHITE: 7,
    BoardGameColor.BLACK: 0
}


class CheckerSquare:

    def __init__(self, index: int, color: BoardGameColor = BoardGameColor.NONE, king: bool = False):
        self.index = index
        self.color = color
        self.king = king

    def setPiece(self, color: BoardGameColor, king: bool = False) -> None:
        self.color = color
        self.king = king

    def getPiece(self) -> Tuple[BoardGameColor, bool]:
        return self.color, self.king

    def emptyPiece(self) -> None:
        self.color = BoardGameColor.NONE
        self.king = False


class CheckerMove:

    def __init__(self, start: int, target: int, captures: Optional[List[int]] = None) -> None:
        self.start = start
        self.target = target
        self.captures = captures or []

    def __repr__(self) -> str:
        return f"CheckerMove(start={self.start}, target={self.target}, captures={self.captures})"


class CheckerBoard:

    def __init__(self) -> None:
        self.__board = [CheckerSquare(i) for i in range(BOARD_SIZE)]
        for y in [y for y in range(AXIS_LENGTH) if y not in (3, 4)]:
            for x in [x for x in range(AXIS_LENGTH) if x % 2 == ((y + 1) % 2)]:
                # Fill the lower half of the board with white pieces.
                if y < 3:
                    self.__board[AXIS_LENGTH * y + x].setPiece(BoardGameColor.WHITE)
                # Fill the upper half of the board with black pieces.
                elif y > 4:
                    self.__board[AXIS_LENGTH * y + x].setPiece(BoardGameColor.BLACK)

        # The color currently playing, as well as its enemy. Both of these values are updated
        # every time the turn changes.
        self.currentColor: BoardGameColor = BoardGameColor.BLACK
        self.enemyColor: BoardGameColor = BoardGameColor.WHITE

        # A list of moves generated at the beginning of every turn for the current color.
        self.moves: List[CheckerMove] = []

    def __next__(self) -> bool:
        """
        Attempts to start the next turn.
        :return: Whether the game has ended.
        """
        # Swap the colors.
        self.currentColor, self.enemyColor = self.enemyColor, self.currentColor

        self.generateMoves()

        # If there are no more moves that the current player can make, the game is over.
        return not self.moves

    def cleanup(self) -> None:
        self.__board = None
        self.moves = []

    def getBoard(self) -> List[CheckerSquare]:
        return self.__board

    """
    Board state
    """

    def loadBoardFromState(self, state: List[List[int]]) -> None:
        for index, color, king in state:
            self.__board[index].setPiece(BoardGameColor(color), king)

    def getBoardState(self) -> List[List[int]]:
        return [[p.index, p.color, p.king] for p in self.__board]

    """
    Move generation
    """

    def requestMove(self, start: int, target: int) -> Optional[CheckerMove]:
        """
        Handle a request to move a checker piece from one square to another.
        :param start: The location of the piece being moved.
        :param target: The location which to move the piece to.
        :return: Whether the move was made successfully.
        """
        move = self.getMove(start, target)
        if move is None:
            return

        self.makeMove(start, target, move.captures)
        return move

    def makeMove(self, start: int, target: int, captures: List[int]) -> None:
        # Unpack the piece info from the start square.
        color, king = self.__board[start].getPiece()

        # Determine if we're able to crown this piece based on its new rank.
        if not king:
            rank = target // 8
            king = rank == FINAL_RANK[self.currentColor]

        # Replace the target square with our selected piece info.
        self.__board[target].setPiece(color, king)
        # Empty the square we started with.
        self.__board[start].emptyPiece()

        # Remove all captures from the board.
        for capture in captures:
            self.__board[capture].emptyPiece()

    def getMove(self, start: int, target: int) -> Optional[CheckerMove]:
        moves = [move for move in self.moves if move.start == start and move.target == target]
        return moves[0] if moves else None

    def getMoves(self, start: int) -> List[CheckerMove]:
        return [move for move in self.moves if move.start == start]

    def generateMoves(self) -> None:
        """
        Generates all possible moves for the currently active color.
        :return: None
        """
        self.moves = []

        isWhite = self.currentColor == BoardGameColor.WHITE

        def traverseBoard(p: CheckerSquare, start: int, stop: int, step: int, col: int, direction: int,
                          skippedPieces: Optional[List[int]] = None):
            lastMove = []
            skippedPieces = skippedPieces or []

            # check the potential rows this piece can get to
            for r in range(start, stop, step):
                # We're at the edge of the board.
                if not 0 <= col < AXIS_LENGTH:
                    break

                # Pull the current square.
                index = AXIS_LENGTH * r + col
                current = self.__board[index]

                # we've been here before.
                if index in skippedPieces:
                    break

                # This is an empty square.
                if current.color == BoardGameColor.NONE:
                    # We've skipped before, but we don't have anything else we can skip over.
                    if skippedPieces and not lastMove:
                        break
                    # We've skipped over multiple pieces.
                    elif skippedPieces:
                        self.moves.append(CheckerMove(p.index, index, lastMove + skippedPieces))
                    # We're skipping over a single piece.
                    elif lastMove:
                        self.moves.append(CheckerMove(p.index, index, lastMove))
                    # We haven't skipped.
                    else:
                        self.moves.append(CheckerMove(p.index, index))

                    # We skipped over something before, prepare to see if we can
                    # double or triple jump.
                    if lastMove:
                        # See if we can jump multiple times from this position.
                        if not isWhite or p.king:
                            traverseBoard(p, r - 1, max(r - 3, -1), -1, col - 1, direction=-1,
                                          skippedPieces=lastMove + skippedPieces)
                            traverseBoard(p, r - 1, max(r - 3, -1), -1, col + 1, direction=1,
                                          skippedPieces=lastMove + skippedPieces)
                        if isWhite or p.king:
                            traverseBoard(p, r + 1, min(r + 3, AXIS_LENGTH), 1, col - 1, direction=-1,
                                          skippedPieces=lastMove + skippedPieces)
                            traverseBoard(p, r + 1, min(r + 3, AXIS_LENGTH), 1, col + 1, direction=1,
                                          skippedPieces=lastMove + skippedPieces)

                    break
                # We can't move here because this piece is our own color.
                elif current.color == self.currentColor:
                    break
                # We can move here assuming that there's an empty square next.
                else:
                    lastMove = [index]

                col += direction

        for piece in self.allyPieces:
            rank = piece.index // AXIS_LENGTH  # y axis
            file = piece.index - rank * AXIS_LENGTH  # x axis
            left = file - 1
            right = file + 1

            if not isWhite or piece.king:
                traverseBoard(piece, rank - 1, max(rank - 3, -1), -1, left, direction=-1)
                traverseBoard(piece, rank - 1, max(rank - 3, -1), -1, right, direction=1)
            if isWhite or piece.king:
                traverseBoard(piece, rank + 1, min(rank + 3, AXIS_LENGTH), 1, left, direction=-1)
                traverseBoard(piece, rank + 1, min(rank + 3, AXIS_LENGTH), 1, right, direction=1)

    def getPiecesOfColor(self, color: BoardGameColor) -> List[CheckerSquare]:
        return [square for square in self.__board if square.color == color]

    """
    Properties
    """

    @property
    def allyPieces(self) -> List[CheckerSquare]:
        return self.getPiecesOfColor(self.currentColor)
