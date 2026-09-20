from enum import IntEnum, auto
from typing import List, Dict, Optional, Union, Tuple

from toontown.safezone.picnicgame.BoardGameGlobals import BoardGameColor, AXIS_LENGTH, BOARD_SIZE
from toontown.toonbase.PythonUtil import getSignOfNum


class ChessPiece(IntEnum):
    EMPTY = auto()
    PAWN = auto()
    ROOK = auto()
    KNIGHT = auto()
    BISHOP = auto()
    KING = auto()
    QUEEN = auto()


class ChessMoveFlag(IntEnum):
    NONE = auto()
    PAWN_PROMOTE_QUEEN = auto()
    PAWN_PROMOTE_ROOK = auto()
    PAWN_PROMOTE_BISHOP = auto()
    PAWN_PROMOTE_KNIGHT = auto()
    PAWN_DOUBLE_MOVE = auto()
    EN_PASSANT = auto()
    CASTLING_KINGSIDE = auto()
    CASTLING_QUEENSIDE = auto()


class ChessGameState(IntEnum):
    PLAYING = auto()
    CHECKMATE_WHITE = auto()
    CHECKMATE_BLACK = auto()
    STALEMATE = auto()
    FIFTY_ROUNDS = auto()
    THREEFOLD_REPETITION = auto()
    INSUFFICIENT_MATERIAL = auto()


class ChessMove:
    """
    Container for information about a move which a piece on the board can make.
    """

    def __init__(self, start: int, target: int, flag: ChessMoveFlag = ChessMoveFlag.NONE) -> None:
        """
        :param start: The position of the piece being moved.
        :param target: The destination square of the piece being moved.
        :param flag: A flag associated with the move. (i.e. pawn promotion, en passant, etc.)
        """
        self.start = start
        self.target = target
        self.flag = flag

    def __repr__(self) -> str:
        return f"ChessMove(start={self.start}, target={self.target}, flag={repr(self.flag)})"


class ChessSquare:
    """
    Container for information about a chess square.
    """

    def __init__(self, index: int, piece: ChessPiece = ChessPiece.EMPTY,
                 color: BoardGameColor = BoardGameColor.NONE) -> None:
        """
        :param index: The position of the square on the board.
        :param piece: The type of piece that exists on this square.
        :param color: The color of piece that exists on this square.
        """
        self.index = index
        self.piece = piece
        self.color = color

        self.moved = False

    def __repr__(self) -> str:
        return (f"ChessSquare(index={self.index}, piece={repr(self.piece)}, color={repr(self.color)}, "
                f"moved={self.moved})")

    def setPiece(self, piece: ChessPiece, color: BoardGameColor, moved: bool = False) -> None:
        self.piece = piece
        self.color = color
        self.moved = moved

    def getPiece(self) -> Tuple[ChessPiece, BoardGameColor]:
        return self.piece, self.color

    def emptyPiece(self) -> None:
        self.piece = ChessPiece.EMPTY
        self.color = BoardGameColor.NONE
        self.moved = False


# Map of every pawn promotion flag to its respective piece type.
PAWN_PROMOTIONS: Dict[ChessMoveFlag, ChessPiece] = {
    ChessMoveFlag.PAWN_PROMOTE_KNIGHT: ChessPiece.KNIGHT,
    ChessMoveFlag.PAWN_PROMOTE_ROOK: ChessPiece.ROOK,
    ChessMoveFlag.PAWN_PROMOTE_BISHOP: ChessPiece.BISHOP,
    ChessMoveFlag.PAWN_PROMOTE_QUEEN: ChessPiece.QUEEN,
}

# A dictionary with data for each piece assigned to a unique location on the board.
GAME_DATA: Dict[int, Tuple[Union[ChessPiece, BoardGameColor]]] = {
    0: (ChessPiece.ROOK, BoardGameColor.WHITE),
    1: (ChessPiece.KNIGHT, BoardGameColor.WHITE),
    2: (ChessPiece.BISHOP, BoardGameColor.WHITE),
    3: (ChessPiece.QUEEN, BoardGameColor.WHITE),
    4: (ChessPiece.KING, BoardGameColor.WHITE),
    5: (ChessPiece.BISHOP, BoardGameColor.WHITE),
    6: (ChessPiece.KNIGHT, BoardGameColor.WHITE),
    7: (ChessPiece.ROOK, BoardGameColor.WHITE),

    8: (ChessPiece.PAWN, BoardGameColor.WHITE),
    9: (ChessPiece.PAWN, BoardGameColor.WHITE),
    10: (ChessPiece.PAWN, BoardGameColor.WHITE),
    11: (ChessPiece.PAWN, BoardGameColor.WHITE),
    12: (ChessPiece.PAWN, BoardGameColor.WHITE),
    13: (ChessPiece.PAWN, BoardGameColor.WHITE),
    14: (ChessPiece.PAWN, BoardGameColor.WHITE),
    15: (ChessPiece.PAWN, BoardGameColor.WHITE),

    48: (ChessPiece.PAWN, BoardGameColor.BLACK),
    49: (ChessPiece.PAWN, BoardGameColor.BLACK),
    50: (ChessPiece.PAWN, BoardGameColor.BLACK),
    51: (ChessPiece.PAWN, BoardGameColor.BLACK),
    52: (ChessPiece.PAWN, BoardGameColor.BLACK),
    53: (ChessPiece.PAWN, BoardGameColor.BLACK),
    54: (ChessPiece.PAWN, BoardGameColor.BLACK),
    55: (ChessPiece.PAWN, BoardGameColor.BLACK),

    56: (ChessPiece.ROOK, BoardGameColor.BLACK),
    57: (ChessPiece.KNIGHT, BoardGameColor.BLACK),
    58: (ChessPiece.BISHOP, BoardGameColor.BLACK),
    59: (ChessPiece.QUEEN, BoardGameColor.BLACK),
    60: (ChessPiece.KING, BoardGameColor.BLACK),
    61: (ChessPiece.BISHOP, BoardGameColor.BLACK),
    62: (ChessPiece.KNIGHT, BoardGameColor.BLACK),
    63: (ChessPiece.ROOK, BoardGameColor.BLACK),
}

# Directional offsets used to navigate the board (0-63)
# Directions:                  N, S, W, E, NW, SE, NE, SW
DirectionOffsets: List[int] = [8, -8, -1, 1, 7, -7, 9, -9]

# Directions in which each colored pawn can attack. (NW, NE for white, SW, SE for black)
PawnAttackDirections: Dict[BoardGameColor, Tuple[int, int]] = {
    BoardGameColor.WHITE: (6, 4), BoardGameColor.BLACK: (7, 5)
}

# Offsets used to navigate the board for ChessPiece.KNIGHT jumps.
KnightJumps: List[int] = [15, 17, -17, -15, 10, -6, 6, -10]

# Contains all movement data generated upon startup for all pieces except for pawns, which are uniquely handled.
ChessMoveData: Dict[ChessPiece, Dict[int, List[int]]] = {
    ChessPiece.KNIGHT: {},
    ChessPiece.BISHOP: {},
    ChessPiece.ROOK: {},
    ChessPiece.QUEEN: {},
    ChessPiece.KING: {},
}

# Contains all capture moves that a pawn can make at any position.
ChessPawnAttacks: Dict[int, Dict[BoardGameColor, List[int]]] = {}

# Map of every square index to the amount of squares that exist from themselves to the edge of the board,
# in each direction.
SquaresToEdge: Dict[int, List[int]] = {}
DirectionLookup: List[int] = []

# Square indices of king side castling rooks.
CastlingKingSide: Dict[BoardGameColor, int] = {BoardGameColor.WHITE: 5, BoardGameColor.BLACK: 61}
# Square indices of queen side castling rooks.
CastlingQueenSide: Dict[BoardGameColor, int] = {BoardGameColor.WHITE: 3, BoardGameColor.BLACK: 59}


def generateSlidingMoves(index: int, dirStart: int, dirEnd: int) -> List[int]:
    return [
        index + direction * (n + 1)
        for i, direction in enumerate(DirectionOffsets[dirStart:dirEnd])
        for n in range(SquaresToEdge[index][i])
    ]


def generateKnightMoves(index: int, x: int, y: int) -> List[int]:
    moves = []
    for knightJump in KnightJumps:
        knightJumpSquare = index + knightJump
        # Ensure this move is within the board.
        if not 0 <= knightJumpSquare < BOARD_SIZE:
            continue

        # Ensure the knight is not jumping to the other side of the board.
        knightY = knightJumpSquare // AXIS_LENGTH
        knightX = knightJumpSquare - knightY * AXIS_LENGTH
        if max(abs(x - knightX), abs(y - knightY)) == 2:
            moves.append(knightJumpSquare)

    return moves


def generateKingMoves(index: int, x: int, y: int) -> List[int]:
    moves = []
    for direction in DirectionOffsets:
        kingJumpSquare = index + direction
        # Ensure this move is within the board.
        if not 0 <= kingJumpSquare < BOARD_SIZE:
            continue

        # Ensure the king is not jumping to the other side of the board.
        kingY = kingJumpSquare // AXIS_LENGTH
        kingX = kingJumpSquare - kingY * AXIS_LENGTH
        if max(abs(x - kingX), abs(y - kingY)) == 1:
            moves.append(kingJumpSquare)

    return moves


def generatePawnMoves(index: int, file: int, rank: int) -> Dict[BoardGameColor, List[int]]:
    moves = {BoardGameColor.WHITE: [], BoardGameColor.BLACK: []}
    # Ensure we're not on either edge of the board when adding the capture.
    if file > 0:
        # 7 is the last rank; pawns cannot exist there.
        if rank < 7:
            moves[BoardGameColor.WHITE].append(index + 7)
        # 0 is the first rank; pawns cannot exist there.
        if rank > 0:
            moves[BoardGameColor.BLACK].append(index - 9)
    if file < 7:
        # 7 is the last rank; pawns cannot exist there.
        if rank < 7:
            moves[BoardGameColor.WHITE].append(index + 9)
        # 0 is the first rank; pawns cannot exist there.
        if rank > 0:
            moves[BoardGameColor.BLACK].append(index - 7)
    return moves


def generateChessMoveData() -> None:
    """
    A function called once upon startup to generate all necessary movement data for each piece in every square
    on the board.
    :return: None
    """
    for index in range(BOARD_SIZE):
        rank = index // AXIS_LENGTH  # y axis
        file = index - rank * AXIS_LENGTH  # x axis

        north = 7 - rank
        south = rank
        west = file
        east = 7 - file

        SquaresToEdge[index] = [
            north, south, west, east,
            min(north, west), min(south, east), min(north, east), min(south, west)
        ]

        orthogonalMoves = generateSlidingMoves(index, 0, 4)
        diagonalMoves = generateSlidingMoves(index, 4, 8)

        ChessMoveData[ChessPiece.ROOK][index] = orthogonalMoves
        ChessMoveData[ChessPiece.BISHOP][index] = diagonalMoves
        ChessMoveData[ChessPiece.QUEEN][index] = orthogonalMoves + diagonalMoves
        ChessMoveData[ChessPiece.KNIGHT][index] = generateKnightMoves(index, file, rank)
        ChessMoveData[ChessPiece.KING][index] = generateKingMoves(index, file, rank)

        ChessPawnAttacks[index] = generatePawnMoves(index, file, rank)

    for i in range(127):
        offset = i - 63
        offsetAbs = abs(offset)
        if offsetAbs % 9 == 0:
            absDir = 9
        elif offsetAbs % 8 == 0:
            absDir = 8
        elif offsetAbs % 7 == 0:
            absDir = 7
        else:
            absDir = 1

        DirectionLookup.append(absDir * getSignOfNum(offset))


# Generate the chess data upon this module being created.
generateChessMoveData()


def isMovingAlongRay(rayDir: int, start: int, target: int) -> bool:
    """
    Determine if, given a direction, the start index is on the same line as the target.
    :param rayDir: The direction we're going in. (see DirectionOffsets)
    :param start: The start index.
    :param target: The end index.
    :return:
    """
    moveDir = DirectionLookup[target - start + 63]
    return moveDir in (rayDir, -rayDir)


def getKingsideRook(index: int) -> int:
    return index + SquaresToEdge[index][3]


def getQueensideRook(index: int) -> int:
    return index - SquaresToEdge[index][2]


# Map each chess piece to the char used to load the piece model.
CHESS_PIECE_TO_CHAR: Dict[ChessPiece, str] = {
    ChessPiece.PAWN: "p",
    ChessPiece.ROOK: "r",
    ChessPiece.KNIGHT: "n",
    ChessPiece.BISHOP: "b",
    ChessPiece.KING: "k",
    ChessPiece.QUEEN: "q",
}

# Map each color to the char used to load the piece model.
COLOR_TO_CHAR: Dict[BoardGameColor, str] = {
    BoardGameColor.WHITE: "w",
    BoardGameColor.BLACK: "b",
}


class ChessBoard:
    """
    Internal representation of the Chess Board.
    """

    def __init__(self) -> None:
        # The board is represented by a 1d array of 64 chess squares. Each of these squares contains info about
        # the piece that exists on it, or lack thereof.
        self.__board: List[ChessSquare] = [ChessSquare(i, *GAME_DATA.get(i, [])) for i in range(BOARD_SIZE)]

        # The color currently playing, as well as its enemy. Both of these values are updated
        # every time the turn changes.
        self.currentColor: BoardGameColor = BoardGameColor.BLACK
        self.enemyColor: BoardGameColor = BoardGameColor.WHITE

        # A map which keeps track of which chess pieces belong to which color to easily grab them whenever necessary.
        self.pieces: Dict[ChessPiece, Dict[BoardGameColor, List[ChessSquare]]] = {}

        # A list of moves that the current color can make, which is generated at the beginning of each turn.
        self.moves: List[ChessMove] = []
        # The previous move that was made.
        self.previousMove: Optional[ChessMove] = None

        # A list of all squares on the board which are being attacked by an enemy piece. This list is generated
        # immediately prior to the moves list.
        self.attacks: List[int] = []
        # A list of all pawns which can perform en passant, but cannot do so without jeopardizing their king.
        self.pinnedEpPawns: List[int] = []
        # A list of all squares which keep the king in check. The king cannot move to these squares.
        self.checkAttacks: List[int] = []
        # A list of all pinned allies. Being pinned means that they cannot move from their square without jeopardizing
        # their king.
        self.pinnedSquares: List[int] = []
        # Is the current color in check?
        self.check: bool = False
        # Is the current color in double check? If so, they can only move their king.
        self.doubleCheck: bool = False
        # Keep track of how many moves have been made without a capture or a moved pawn.
        self.fiftyMoveCount: int = 0
        # Keep track of the fen notation of the board for each move made. This is used to handle threefold repetition.
        self.moveHistory: List[str] = []
        # Keep track of the castling moves each color has made.
        self.castlingRights: Dict[BoardGameColor, str] = {
            BoardGameColor.WHITE: "",
            BoardGameColor.BLACK: "",
        }

    def __next__(self) -> ChessGameState:
        """
        Attempts to start the next turn.
        :return: The current game state.
        """
        # Swap the colors.
        self.currentColor, self.enemyColor = self.enemyColor, self.currentColor

        self.generateMoves()

        # Determine checkmate or stalemate.
        if not self.moves:
            if self.check:
                return (ChessGameState.CHECKMATE_WHITE
                        if self.currentColor == BoardGameColor.WHITE
                        else ChessGameState.CHECKMATE_BLACK)
            return ChessGameState.STALEMATE

        # Increment 50 move counter.
        self.fiftyMoveCount += 1

        # If we surpassed 50 moves, we end in a stalemate.
        if self.fiftyMoveCount >= 50:
            return ChessGameState.FIFTY_ROUNDS

        # Add the board state to the move history.
        fen = self.generateFen()
        self.moveHistory.append(fen)

        # The same board state has been recorded 3 times.
        if self.moveHistory.count(fen) == 3:
            return ChessGameState.THREEFOLD_REPETITION

        # Handle stalemate case of insufficient material.
        allyPieces = len(self.getPiecesOfColor(self.currentColor))
        enemyPieces = len(self.getPiecesOfColor(self.enemyColor))

        # It's a king vs king situation.
        if allyPieces == 1 and enemyPieces == 1:
            return ChessGameState.INSUFFICIENT_MATERIAL

        if allyPieces < 3 and enemyPieces < 3:
            allyBishop = self.pieces[ChessPiece.BISHOP][self.currentColor]
            enemyBishop = self.pieces[ChessPiece.BISHOP][self.enemyColor]

            # Each side has a bishop that belongs on the same colored square.
            if allyBishop and enemyBishop and allyBishop[0].index % 2 == enemyBishop[0].index % 2:
                return ChessGameState.INSUFFICIENT_MATERIAL

            enemyKnight = self.pieces[ChessPiece.KNIGHT][self.enemyColor]

            # The current player only has their king while the enemy has their king and a bishop/knight.
            if allyPieces == 1 and (enemyBishop or enemyKnight):
                return ChessGameState.INSUFFICIENT_MATERIAL

        # We can continue the game.
        return ChessGameState.PLAYING

    def cleanup(self) -> None:
        self.__board = []
        self.pieces = {}
        self.moves = []
        self.previousMove = None
        self.attacks = []
        self.pinnedEpPawns = []
        self.checkAttacks = []
        self.pinnedSquares = []
        self.castlingRights = {}
        self.moveHistory = []

    def getBoard(self) -> List[ChessSquare]:
        """
        Gets the internal board list for outside usage.
        :return:
        """
        return self.__board

    def generateFen(self) -> str:
        """
        Generates part of a fen string, used to determine a draw by threefold repetition.
        :return:
        """
        fen = ""

        # First, let's iterate the board.
        emptySquares = 0
        for i, square in enumerate(self.__board):
            if square.piece != ChessPiece.EMPTY:
                # We reached a new piece, add the amount of empty pieces to the str.
                if emptySquares:
                    fen += str(emptySquares)
                    emptySquares = 0

                # Uppercase letters are black, lowercase are white.
                c = CHESS_PIECE_TO_CHAR[square.piece]
                fen += c.upper() if square.color == BoardGameColor.BLACK else c
            else:
                # This square is empty, increment the empty squares.
                emptySquares += 1

            # We have reached the end of the row.
            if i + 1 % AXIS_LENGTH == 0:
                # Add the amount of empty squares encountered.
                if emptySquares:
                    fen += str(emptySquares)
                    emptySquares = 0

                # Add a slash if we're not at the end of the board.
                if i < BOARD_SIZE - 1:
                    fen += "/"

        # Add the currently active color.
        fen += f" {COLOR_TO_CHAR[self.currentColor]} "

        # Add the castling rights.
        castlingRights = ''.join(self.castlingRights.values())
        fen += f" {castlingRights} " if castlingRights else " - "

        # Add the en passant target.
        fen += f" {self.enPassantIndex}"

        # We are done here.
        return fen

    """
    Board state
    """

    def loadBoardFromState(self, state: List[List[int]]) -> None:
        for index, pieceType, pieceColor in state:
            self.__board[index].setPiece(ChessPiece(pieceType), BoardGameColor(pieceColor))

    def getBoardState(self) -> List[List[int]]:
        return [[p.index, p.piece, p.color] for p in self.__board]

    """
    Move requesting
    """

    def requestMove(self, start: int, target: int, flag: ChessMoveFlag) -> bool:
        """
        Handles a request to move a chess piece from one square to another.
        :param start: The location of the piece being moved.
        :param target: The location which to move the piece to.
        :param flag: The flag associated with the move.
        :return: Whether the move was made successfully.
        """
        move = self.getMove(start, target, flag)
        if move is None:
            return False

        self.makeMove(start, target, flag)

        # Store the move as the previously made move.
        self.previousMove = move

        return True

    def makeMove(self, start: int, target: int, flag: ChessMoveFlag) -> None:
        # Unpack the piece info from the start square.
        pieceType, pieceColor = self.__board[start].getPiece()

        # Handle the flag associated with the move.

        if flag == ChessMoveFlag.EN_PASSANT:
            # Remove the en passant capture.
            self.__board[target - (8 if self.currentColor == BoardGameColor.WHITE else -8)].emptyPiece()

        elif flag == ChessMoveFlag.CASTLING_KINGSIDE:
            # Empty the square the rook was in.
            self.__board[getKingsideRook(target)].emptyPiece()
            # Then move the rook to the left of the king.
            self.__board[target - 1].setPiece(ChessPiece.ROOK, self.currentColor, True)
            # Increment the amount of castling moves made.
            self.castlingRights[self.currentColor] += "K" if self.currentColor == BoardGameColor.BLACK else "k"

        elif flag == ChessMoveFlag.CASTLING_QUEENSIDE:
            # Empty the square the rook was in.
            self.__board[getQueensideRook(target)].emptyPiece()
            # Then move the rook to the right of the king.
            self.__board[target + 1].setPiece(ChessPiece.ROOK, self.currentColor, True)
            # Increment the amount of castling moves made.
            self.castlingRights[self.currentColor] += "Q" if self.currentColor == BoardGameColor.BLACK else "q"

        elif flag in PAWN_PROMOTIONS:
            # Replace the piece type.
            pieceType = PAWN_PROMOTIONS[flag]

        # Reset 50 move count if a pawn is being moved or if this is a capture.
        if pieceType == ChessPiece.PAWN or self.__board[target].piece != ChessPiece.EMPTY:
            self.fiftyMoveCount = 0

        # Replace the target square info with our selected piece info.
        # We're also setting the moved flag to True, since the piece is obviously moving.
        self.__board[target].setPiece(pieceType, pieceColor, True)
        # Empty the square that we started with.
        self.__board[start].emptyPiece()

    def getMove(self, start: int, target: int, flag: Optional[ChessMoveFlag] = None) -> Optional[ChessMove]:
        moves = [move for move in self.moves
                 if move.start == start and move.target == target and (flag is None or move.flag == flag)]
        return moves[0] if moves else None

    def getMoves(self, start: int) -> List[ChessMove]:
        return [move for move in self.moves if move.start == start]

    """
    Valid move generation
    """

    def generateKingMoves(self) -> None:
        kingIndex = self.allyKing.index
        kingMoved = self.allyKing.moved

        for target in ChessMoveData[ChessPiece.KING][kingIndex]:
            targetPiece = self.__board[target]

            # Ignore pieces of our own color.
            if targetPiece.color == self.currentColor:
                continue

            # Unless it's a capture, disallow this move if this square is under enemy control.
            capture = targetPiece.color == self.enemyColor
            if not capture and self.check and target in self.checkAttacks:
                continue

            # Is it safe for the king to move here?
            if target in self.attacks:
                continue

            self.moves.append(ChessMove(kingIndex, target))

            # Disallow castling if the king is in check, if this was a capture, or if the king has moved before.
            if self.check or capture or kingMoved:
                continue

            # Check for castling king side.
            if target == CastlingKingSide[self.currentColor]:
                # They can only castle if the respective rook is in the correct position and has yet to move.
                rookIndex = getKingsideRook(target)
                rookPiece = self.__board[rookIndex]
                if rookPiece.piece != ChessPiece.ROOK or rookPiece.moved:
                    continue

                # Kingside is on the right side of the board.
                targetKingside = target + 1

                # Ensure that the square the king moves to is empty and not under attack.
                if self.__board[targetKingside].piece == ChessPiece.EMPTY and targetKingside not in self.attacks:
                    self.moves.append(ChessMove(kingIndex, targetKingside, ChessMoveFlag.CASTLING_KINGSIDE))

            # Check for castling queen side.
            elif target == CastlingQueenSide[self.currentColor]:
                # They can only castle if the respective rook is in the correct position and has yet to move.
                rookIndex = getQueensideRook(target)
                rookPiece = self.__board[rookIndex]
                if rookPiece.piece != ChessPiece.ROOK or rookPiece.moved:
                    continue

                # Queenside is on the left side of the board.
                targetQueenside = target - 1

                # Ensure that the square the king moves to is empty and not under attack.
                if self.__board[targetQueenside].piece == ChessPiece.EMPTY and targetQueenside not in self.attacks:
                    self.moves.append(ChessMove(kingIndex, targetQueenside, ChessMoveFlag.CASTLING_QUEENSIDE))

    def generateKnightMoves(self) -> None:
        for knight in self.knights[self.currentColor]:
            # This knight is pinned; it cannot move.
            if knight.index in self.pinnedSquares:
                continue

            for target in ChessMoveData[ChessPiece.KNIGHT][knight.index]:
                targetPiece = self.__board[target]

                # Don't move here if this squares has a friendly piece, or we're in check and
                # this move does not take us out of check.
                if targetPiece.color == self.currentColor or (self.check and target not in self.checkAttacks):
                    continue

                self.moves.append(ChessMove(knight.index, target))

    def generatePawnPromotionMoves(self, start: int, target: int) -> None:
        """
        Populate the moves list with every promotion that the pawn can make.
        :param start:
        :param target:
        :return: None
        """
        for flag in list(PAWN_PROMOTIONS):
            self.moves.append(ChessMove(start, target, flag))

    def generatePawnMoves(self) -> None:
        # Set some constants for pawn move generation based on current color.
        if self.currentColor == BoardGameColor.WHITE:
            pawnOffset = DirectionOffsets[0]
            firstRank = 1
            promoteRank = 6
        else:
            pawnOffset = DirectionOffsets[1]
            firstRank = 6
            promoteRank = 1

        # Get the en passant capture square if applicable.
        enPassantIndex = self.enPassantIndex
        if enPassantIndex != -1:
            enPassantSquare = enPassantIndex + pawnOffset
        else:
            enPassantSquare = -1

        for pawn in self.pawns[self.currentColor]:
            start = pawn.index
            rank = start // 8
            canPromote = rank == promoteRank
            oneAhead = start + pawnOffset

            # Check if the square in front of this pawn is empty.
            if self.__board[oneAhead].piece == ChessPiece.EMPTY:
                if start not in self.pinnedSquares or isMovingAlongRay(pawnOffset, start, self.allyKing.index):
                    # Add the move if we're not in check or the square is in the way of a checking piece.
                    if not self.check or oneAhead in self.checkAttacks:
                        if canPromote:
                            self.generatePawnPromotionMoves(start, oneAhead)
                        else:
                            self.moves.append(ChessMove(start, oneAhead))

                    # Allow the pawn to move two spaces ahead if it's on its starting square.
                    if rank == firstRank:
                        twoAhead = oneAhead + pawnOffset
                        if self.__board[twoAhead].piece == ChessPiece.EMPTY:
                            # Add the move if we're not in check or the square is in the way of a checking piece.
                            if not self.check or twoAhead in self.checkAttacks:
                                self.moves.append(ChessMove(start, twoAhead, ChessMoveFlag.PAWN_DOUBLE_MOVE))

            # Iterate through the diagonal movements that the pawn can make for captures.
            for attackDirection in PawnAttackDirections[self.currentColor]:
                # Ignore it if it's going off the board.
                if SquaresToEdge[start][attackDirection] <= 0:
                    continue

                dirOffset = DirectionOffsets[attackDirection]
                target = start + dirOffset
                square = self.__board[target]

                # Skip this capture if our pawn is pinned and the target square is not on the same line as the pin.
                if start in self.pinnedSquares and not isMovingAlongRay(dirOffset, self.allyKing.index, start):
                    continue

                # Handle a regular capture.
                if square.color == self.enemyColor:
                    # This capture would not stop our king from being in check, continue.
                    if self.check and target not in self.checkAttacks:
                        continue

                    if canPromote:
                        self.generatePawnPromotionMoves(start, target)
                    else:
                        self.moves.append(ChessMove(start, target))

                # Handle an en passant capture.
                if start not in self.pinnedEpPawns and target == enPassantSquare:
                    self.moves.append(ChessMove(start, target, ChessMoveFlag.EN_PASSANT))

    def generateSlidingMoves(self, start: int, dirStart: int, dirEnd: int) -> None:
        pinned = start in self.pinnedSquares

        # This piece can't move if they're in check while being pinned.
        if self.check and pinned:
            return

        for direction in range(dirStart, dirEnd):
            offset = DirectionOffsets[direction]

            # Don't go in this direction if this piece is pinned and moving this direction would move the piece
            # out of the way of an incoming attack to the king, thus jeopardizing it.
            if pinned and not isMovingAlongRay(offset, self.allyKing.index, start):
                continue

            for n in range(SquaresToEdge[start][direction]):
                target = start + offset * (n + 1)
                square = self.__board[target]

                # Stop going in this direction if the square is occupied by a friendly piece.
                if square.color == self.currentColor:
                    break

                capture = square.color == self.enemyColor

                # Allow this move to be made if doing so would prevent check from happening, either by way of
                # capturing the attacker, or moving in the way of the attacker.
                # Keep in mind that since this piece can move during check, it means that it's not pinned and
                # double check is not in effect, so doing this would successfully defend from the check.
                preventsCheck = self.check and target in self.checkAttacks
                if preventsCheck or not self.check:
                    self.moves.append(ChessMove(start, target))

                # Don't allow them to move past this point if this is a piece we're capturing, or if moving here
                # would prevent check from happening.
                if capture or preventsCheck:
                    break

    def generateSlidingAttacks(self, start: int, dirStart: int, dirEnd: int) -> None:
        epPawns = self.enPassantPawns

        for direction in range(dirStart, dirEnd):
            offset = DirectionOffsets[direction]
            epPawnsAttacked = []

            for n in range(SquaresToEdge[start][direction]):
                target = start + offset * (n + 1)
                square = self.__board[target]

                # Add the attack as long as we're not abiding by the whim of an en passant.
                if not epPawnsAttacked:
                    self.attacks.append(target)

                if target != self.allyKing.index and square.piece != ChessPiece.EMPTY:
                    # We've encountered a pawn involved in a possible en passant, let's continue
                    # down this path until we're either blocked by a piece not involved in en passant or the king.
                    if square in epPawns:
                        epPawnsAttacked.append(square.index)
                        continue
                    break
                elif target == self.allyKing.index and epPawnsAttacked:
                    # We found the king, pin the attacked en passant pawns of our current color.
                    self.pinnedEpPawns.extend([square for square in epPawnsAttacked
                                               if self.__board[square].color == self.currentColor])

    def generateAttacks(self) -> None:
        # Generate attacks for the enemy king.
        self.attacks.extend(ChessMoveData[ChessPiece.KING][self.enemyKing.index])

        # Generate attacks for the enemy rooks.
        for enemyRook in self.rooks[self.enemyColor]:
            self.generateSlidingAttacks(enemyRook.index, 0, 4)

        # Generate attacks for the enemy bishops
        for enemyBishop in self.bishops[self.enemyColor]:
            self.generateSlidingAttacks(enemyBishop.index, 4, 8)

        # Generate attacks for the enemy queens.
        for enemyQueen in self.queens[self.enemyColor]:
            self.generateSlidingAttacks(enemyQueen.index, 0, 8)

        # Next, let's handle pins and checks from sliding pieces. (queens/bishops/rooks)
        if self.queens[self.enemyColor]:
            dirStart = 0
            dirEnd = 8
        else:
            dirStart = 0 if self.rooks[self.enemyColor] else 4
            dirEnd = 8 if self.bishops[self.enemyColor] else 4

        for direction in range(dirStart, dirEnd):
            diagonal = direction > 3
            offset = DirectionOffsets[direction]

            # Keep track of if the current path is blocked by a friendly piece.
            allyBlocking = False
            # Keep track of all attacked squares between the start and the target, in the case we declare a check.
            checkAttacks = []

            for i in range(SquaresToEdge[self.allyKing.index][direction]):
                target = self.allyKing.index + offset * (i + 1)
                square = self.__board[target]
                checkAttacks.append(target)

                # The square is empty, continue.
                if square.piece == ChessPiece.EMPTY:
                    continue

                # The path is blocked by a friendly piece.
                if square.color == self.currentColor:
                    if not allyBlocking:
                        allyBlocking = True
                        continue

                    # It's the second friendly piece in the way, the king is completely safe from their attack.
                    break

                # We ran into an enemy piece; determine what to do based on whether a friendly piece is blocking it.
                pieceType = square.piece
                if (
                    pieceType == ChessPiece.QUEEN
                    or (diagonal and pieceType == ChessPiece.BISHOP)
                    or (not diagonal and pieceType == ChessPiece.ROOK)
                ):
                    # If a friendly piece is blocking it, ensure that it cannot make a move that would
                    # jeopardize their king.
                    if allyBlocking:
                        self.pinnedSquares.extend(checkAttacks)
                    # Otherwise, the current player is in check. Extend the check attacks with all the squares
                    # that this piece traversed to get here.
                    else:
                        self.checkAttacks.extend(checkAttacks)
                        # They're in double check if they were already in check.
                        self.doubleCheck = self.check
                        self.check = True
                break

            # Let's stop searching for pins, as the king is the only piece allowed to move in double check.
            if self.doubleCheck:
                break

        # Handle any attacks that the enemy knights can make.
        knightCheck = False
        for knight in self.knights[self.enemyColor]:
            start = knight.index
            moves = ChessMoveData[ChessPiece.KNIGHT][start]
            self.attacks.extend(moves)

            if not knightCheck and self.allyKing.index in moves:
                knightCheck = True
                self.checkAttacks.append(start)
                # They're in double check if they were already in check.
                self.doubleCheck = self.check
                self.check = True

        # Handle any attacks that the enemy pawns can make.
        pawnCheck = False
        for pawn in self.pawns[self.enemyColor]:
            start = pawn.index
            moves = ChessPawnAttacks[start][self.enemyColor]
            self.attacks.extend(moves)

            if not pawnCheck and self.allyKing.index in moves:
                pawnCheck = True
                self.checkAttacks.append(start)
                # They're in double check if they were already in check.
                self.doubleCheck = self.check
                self.check = True

    def generateMoves(self) -> None:
        """
        Generates all possible moves for the currently active color.
        :return: None
        """

        # Reset values that may contain results from the previous round.
        self.check = False
        self.doubleCheck = False
        self.moves = []
        self.attacks = []
        self.pinnedEpPawns = []
        self.checkAttacks = []
        self.pinnedSquares = []

        self.pieces = {pieceType: {BoardGameColor.WHITE: [], BoardGameColor.BLACK: []}
                       for pieceType in list(ChessPiece)[1:]}

        for square in self.__board:
            if square.piece == ChessPiece.EMPTY:
                continue

            self.pieces[square.piece][square.color].append(square)

        self.generateAttacks()
        self.generateKingMoves()

        # Only the king is allowed to move in double check.
        if self.doubleCheck:
            return

        for rook in self.rooks[self.currentColor]:
            self.generateSlidingMoves(rook.index, 0, 4)

        for bishop in self.bishops[self.currentColor]:
            self.generateSlidingMoves(bishop.index, 4, 8)

        for queen in self.queens[self.currentColor]:
            self.generateSlidingMoves(queen.index, 0, 8)

        self.generateKnightMoves()
        self.generatePawnMoves()

    def getPiecesOfColor(self, color: BoardGameColor) -> List[ChessSquare]:
        return [square for square in self.__board if square.color == color]

    """
    Properties
    """

    @property
    def pawns(self):
        return self.pieces[ChessPiece.PAWN]

    @property
    def rooks(self):
        return self.pieces[ChessPiece.ROOK]

    @property
    def bishops(self):
        return self.pieces[ChessPiece.BISHOP]

    @property
    def knights(self):
        return self.pieces[ChessPiece.KNIGHT]

    @property
    def queens(self):
        return self.pieces[ChessPiece.QUEEN]

    @property
    def allyKing(self):
        return self.pieces[ChessPiece.KING][self.currentColor][0]

    @property
    def enemyKing(self):
        return self.pieces[ChessPiece.KING][self.enemyColor][0]

    @property
    def enPassantIndex(self) -> int:
        if self.previousMove is None or self.previousMove.flag != ChessMoveFlag.PAWN_DOUBLE_MOVE:
            return -1

        return self.previousMove.target

    @property
    def enPassantPawns(self) -> List[ChessSquare]:
        """
        Returns a list of pawns which can perform en passant this turn.
        :return:
        """
        if self.previousMove is None or self.previousMove.flag != ChessMoveFlag.PAWN_DOUBLE_MOVE:
            return []

        target = self.previousMove.target
        rank = target // AXIS_LENGTH
        file = target - rank * AXIS_LENGTH
        pawns = []
        for i in (-1, 1):
            adjacent = file + i

            # Don't go out of bounds.
            if not 0 <= adjacent < AXIS_LENGTH:
                continue

            # If the adjacent square contains a pawn of the current color, add them, as they can do
            # an en passant capture.
            adjacentSquare = self.__board[8 * rank + adjacent]
            if adjacentSquare.piece == ChessPiece.PAWN and adjacentSquare.color == self.currentColor:
                pawns.append(adjacentSquare)

        # Only count the en passant capture if there are pawns which are eligible to do so.
        if pawns:
            pawns.insert(0, self.__board[self.previousMove.target])

        return pawns
