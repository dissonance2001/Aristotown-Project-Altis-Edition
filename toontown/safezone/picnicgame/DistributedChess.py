from typing import List, Optional, Dict, Tuple

from direct.gui import DirectGuiGlobals
from panda3d.core import NodePath
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from toontown.gui.game.condition.ConditionGlobals import ConditionState
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.safezone.picnicgame.BoardGameGlobals import BoardGameColor, VALID_MOVE_COLOR_ON, VALID_MOVE_COLOR_OFF, \
    PIECE_TINT_COLOR, PIECE_COLORS, ChessClock
from toontown.safezone.picnicgame.CheckerBoardNode import CheckerBoardNode
from toontown.safezone.picnicgame.ChessClockNode import ChessClockNode
from toontown.safezone.picnicgame.ChessGlobals import ChessBoard, ChessMove, ChessMoveFlag, PAWN_PROMOTIONS, \
    ChessPiece, getKingsideRook, getQueensideRook, DirectionOffsets, CHESS_PIECE_TO_CHAR, COLOR_TO_CHAR
from toontown.safezone.picnicgame.DistributedPicnicGame import DistributedPicnicGame
from toontown.safezone.picnicgame.PicnicGameGlobals import PicnicGame
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toonbase.ToontownGlobals import getMinnieFont

# Positions of the pawn promotion buttons on the choice panel.
PROMOTE_BUTTON_POS: Dict[ChessPiece, Tuple[float, float, float]] = {
    ChessPiece.QUEEN: (0.25, 0.0, -0.25),
    ChessPiece.KNIGHT: (0.25, 0.0, 0.25),
    ChessPiece.ROOK: (-0.25, 0.0, -0.25),
    ChessPiece.BISHOP: (-0.25, 0.0, 0.25),
}


class DistributedChess(DistributedPicnicGame):
    gameMusicKey = "picnic_chess"
    discordPreset = "chess"
    guiState = ConditionState.PGT_CHESS

    def __init__(self, cr) -> None:
        super().__init__(cr)

        self.board = ChessBoard()
        self.clock = ChessClock()
        self.clocks: dict[int, ChessClockNode] = {}
        self.pieces: Dict[int, NodePath] = {}
        self.selectedPiece: int = -1
        self.validMoves: List[ChessMove] = []
        self.receivedGameState: bool = False
        self.currentColor: BoardGameColor = BoardGameColor.WHITE

        self.boardNode: Optional[CheckerBoardNode] = None

        self.blinkerTrack: Optional[Sequence] = None
        self.validMoveTracks: Dict[NodePath, Sequence] = {}
        self.pieceMoveTracks: Dict[int, Sequence] = {}

        self.promotePawnFrame: Optional[DirectFrame] = None
        self.promotePawnFrameSeq: Optional[Sequence] = None

        self.chessPieces = base.loader.loadModel("phase_6/models/golf/chess_pieces.bam")

        # Sound effects for board games.
        self.knockSfx = base.loader.loadSfx("phase_5/audio/sfx/GUI_knock_1.ogg")
        self.clickSfx = base.loader.loadSfx("phase_3/audio/sfx/GUI_balloon_popup.ogg")
        self.moveSfx = base.loader.loadSfx("phase_6/audio/sfx/CC_move.ogg")

        self.player2color: Dict[int, BoardGameColor] = {}

        self.drawButton: Optional[MainMenuButton] = None
        self.drawVoteLabel: Optional[DirectLabel] = None

    def delete(self) -> None:
        super().delete()

        self.destroyClocks()
        self.clearValidMoveTracks()
        self.finishBlinkerTrack()
        self.destroyDrawButton()

        for seq in list(self.pieceMoveTracks.values()):
            seq.finish()

        self.pieceMoveTracks = {}

        self.chessPieces.removeNode()
        self.chessPieces = None

        for piece in self.pieces.values():
            piece.removeNode()

        self.pieces = {}

        self.board.cleanup()
        self.board = None

        self.clock.cleanup()
        self.clock = None

        if self.boardNode is not None:
            self.boardNode.cleanup()
            self.boardNode = None

        self.destroyPromotePawnFrame()
        self.stopPromotePawnFrameSeq()

    def generate(self) -> None:
        super().generate()

        self.boardNode = CheckerBoardNode(self.handleMouseClick)
        self.boardNode.reparentTo(self)

    def announceGenerate(self) -> None:
        super().announceGenerate()
        self.d_requestGameState()

    def avatarEnter(self, avId: int) -> None:
        if avId != base.localAvatar.doId:
            return

        if self.getCurrentOrNextState() == "Playing":
            for piece in self.pieces.values():
                piece.setH(self.playerHeading)

            self.createClocks()
            self.clocks[self.currentPlayer].startClock()
            self.updateClocks()

        super().avatarEnter(avId)

    def avatarExit(self, avId: int) -> None:
        if avId != base.localAvatar.doId:
            return

        self.destroyClocks()
        super().avatarExit(avId)

    def setPlayers(self, players) -> None:
        super().setPlayers(players)

        if len(self.players) == 2:
            self.player2color = {
                self.players[0]: BoardGameColor.WHITE,
                self.players[1]: BoardGameColor.BLACK,
            }

    def createPiece(self, index: int, piece: ChessPiece, color: BoardGameColor, zOffset: float = 0) -> NodePath:
        pieceStr = CHESS_PIECE_TO_CHAR[piece]
        colorStr = COLOR_TO_CHAR[color]

        pieceNode = self.chessPieces.find(f"**/{colorStr}{pieceStr}").copyTo(NodePath())
        pieceNode.setP(-90)
        pieceNode.setScale(0.6)
        pieceNode.setColor(1, 1, 1, 1)
        pieceNode.reparentTo(self.boardNode.locators[index])

        if zOffset:
            pieceNode.setZ(pieceNode.getZ() + zOffset)

        # Rotate the piece to match our local seated toon, if necessary.
        if self.isGameVisible:
            pieceNode.setH(self.playerHeading)

        return pieceNode

    def setGameState(self, gameState: List[List[int]], timeLeftInfo: List[List[int]]) -> None:
        # Load the board.
        self.board.loadBoardFromState(gameState)

        # Load the pieces.
        for square in self.board.getBoard():
            if square.piece == ChessPiece.EMPTY:
                continue
            self.pieces[square.index] = self.createPiece(square.index, square.piece, square.color)

        # We have now received the game state.
        self.receivedGameState = True

        self.clock.fromStruct(timeLeftInfo)

        self.updateClocks()

    def setTimerEnd(self, t: int) -> None:
        self.clock.setPlayerTimeLeft(self.currentPlayer, t)

        if self.isGameVisible:
            self.clocks[self.currentPlayer].setTimeLeft(self.clock[self.currentPlayer], animated=True)

    def setCurrentPlayer(self, playerAvId: int) -> None:
        if self.receivedGameState:
            # Progress the board.
            next(self.board)

        super().setCurrentPlayer(playerAvId)

        self.currentColor = self.player2color[playerAvId]

        if not self.isGameVisible:
            return

        self.updateClocks()

        if not self.playerToon:
            return

        self.finishBlinkerTrack()
        self.destroyPromotePawnFrame()
        self.stopPromotePawnFrameSeq()
        self.clearValidMoveTracks()

        if base.localAvatar.doId == playerAvId:
            base.discord.applyPreset(self.discordPreset)
            self.playSfx(self.turnChangeSfx)

            self.boardNode.enableMouseCollisions()
        else:
            self.boardNode.disableMouseCollisions()

    def handleMouseClick(self, index: int) -> None:
        selected = self.selectPiece(index)
        if not selected:
            return

        pieceGeom = self.pieces[self.selectedPiece]
        color = pieceGeom.getColor()

        self.blinkerTrack = Sequence(
            LerpColorScaleInterval(pieceGeom, .7, PIECE_TINT_COLOR, startColorScale=color, blendType="easeIn"),
            LerpColorScaleInterval(pieceGeom, .7, color, startColorScale=PIECE_TINT_COLOR, blendType="easeIn")
        )
        self.blinkerTrack.loop()

        self.playSfx(self.clickSfx)

        self.displayValidMoves()

    def selectPiece(self, index: int) -> bool:
        if index == self.selectedPiece:
            return False

        # We're clicking a piece other than the one we selected. Remove the valid moves and blink tracks.
        self.clearValidMoveTracks()
        self.finishBlinkerTrack()

        piece = self.board.getBoard()[index]

        # The player is trying to move their selected piece somewhere else.
        if self.selectedPiece != -1 and piece.color != self.currentColor:
            # Attempt to move their piece to the indicated coordinates.
            if not self.attemptMovePiece(index):
                # Unable to move to these coordinates, unselect the piece.
                self.selectedPiece = -1
                return False

        # If this is a valid piece, select it.
        if piece.color == self.currentColor:
            self.selectedPiece = index

            # Calculate all the valid moves at this point.
            self.validMoves = self.board.getMoves(index)
            return True

        return False

    def attemptMovePiece(self, target: int) -> bool:
        if self.selectedPiece == -1:
            return False

        move = self.board.getMove(self.selectedPiece, target)
        if move is None:
            return False

        if move.flag in PAWN_PROMOTIONS:
            self.pawnPromoteChoice(target)
        else:
            self.d_requestMove(move.start, move.target, move.flag)
        return True

    def d_requestMove(self, start: int, target: int, flag: int) -> None:
        self.sendUpdate("requestMove", [start, target, flag])

    def movePiece(self, start: int, target: int, flag: int) -> None:
        if not self.receivedGameState:
            return

        self.selectedPiece = -1
        self.validMoves = []

        flag = ChessMoveFlag(flag)

        # Update the board representation with this move.
        self.board.makeMove(start, target, flag)
        # Store the move as the previously made move.
        self.board.previousMove = ChessMove(start, target, flag)

        piece = self.pieces.get(start)
        if piece is None:
            return

        color = self.currentColor

        def movePieceNode():
            # Ensure that the piece that was sitting on this square is gone.
            oldPiece = self.pieces.get(target)
            if oldPiece is not None:
                oldPiece.removeNode()

            # If they promoted a pawn, replace the piece node with the piece we're promoting to.
            if flag in PAWN_PROMOTIONS:
                piece.removeNode()
                self.pieces[target] = self.createPiece(target, PAWN_PROMOTIONS[flag], color)
            else:
                piece.setPos(0, 0, 0)
                piece.reparentTo(self.boardNode.locators[target])
                self.pieces[target] = piece

            # Remove the piece we're moving from the start index.
            if start in self.pieces:
                del self.pieces[start]

            # If castling has occurred, move the rook as well.
            if rookIndex != -1:
                rook = self.pieces[rookIndex]
                rook.setPos(0, 0, 0)
                rook.reparentTo(self.boardNode.locators[castlingIndex])

                self.pieces[castlingIndex] = rook
                if rookIndex in self.pieces:
                    del self.pieces[rookIndex]

            # Handle removing the en passant piece node from the board.
            if flag != ChessMoveFlag.EN_PASSANT:
                return

            epTarget = target + DirectionOffsets[0 if self.currentColor == BoardGameColor.WHITE else 1]
            epCapture = self.pieces.get(epTarget)
            if epCapture is None:
                return

            epCapture.removeNode()
            del self.pieces[epTarget]

        # Handle moving the rook during castling.
        castlingSeq = Sequence()
        rookIndex = -1
        castlingIndex = -1

        # Get the indices for the rook to move between.
        if flag == ChessMoveFlag.CASTLING_KINGSIDE:
            rookIndex = getKingsideRook(target)
            castlingIndex = target - 1
        elif flag == ChessMoveFlag.CASTLING_QUEENSIDE:
            rookIndex = getQueensideRook(target)
            castlingIndex = target + 1

        # Move the rook slightly after the king if castling happened.
        if rookIndex != -1:
            castlingSeq.append(Parallel(
                LerpPosInterval(self.pieces[rookIndex], 0.2,
                                self.boardNode.locators[castlingIndex].getPos(self.boardNode.locators[rookIndex])),
                Func(self.playSfx, self.moveSfx)
            ))

        self.pieceMoveTracks[start] = Sequence(
            Parallel(
                LerpPosInterval(piece, 0.2,
                                self.boardNode.locators[target].getPos(self.boardNode.locators[start])),
                Func(self.playSfx, self.moveSfx)
            ),
            castlingSeq,
            Func(movePieceNode),
            Func(self.removeMoveSeq, start)
        )
        self.pieceMoveTracks[start].start()

    def removeMoveSeq(self, index: int) -> None:
        if index in self.pieceMoveTracks:
            self.pieceMoveTracks[index].finish()
            del self.pieceMoveTracks[index]

    def pawnPromoteChoice(self, target: int) -> None:
        self.promotePawnFrame = DirectFrame(
            parent=aspect2d, relief=None, image=DGG.getDefaultDialogGeom(),
            image_color=ToontownGlobals.GlobalDialogColor,
            scale=0.5,
        )
        self.promotePawnFrame.hide()

        color = COLOR_TO_CHAR[self.currentColor]

        for promo, piece in PAWN_PROMOTIONS.items():
            pathPiece = CHESS_PIECE_TO_CHAR[piece]
            DirectButton(
                parent=self.promotePawnFrame, relief=None,
                geom=self.chessPieces.find(f"**/{color}{pathPiece}"),
                scale=0.5,
                pos=PROMOTE_BUTTON_POS[piece],
                command=self.finishPawnPromoteChoice,
                extraArgs=[target, promo]
            )

        scale = self.promotePawnFrame.getScale()

        self.promotePawnFrameSeq = Sequence(
            Func(self.promotePawnFrame.show),
            LerpScaleInterval(self.promotePawnFrame, .2, scale * 1.2, 0.01, blendType="easeInOut"),
            LerpScaleInterval(self.promotePawnFrame, .2, scale, scale, blendType="easeInOut"),
        )
        self.promotePawnFrameSeq.start()

    def finishPawnPromoteChoice(self, target: int, promo: ChessMoveFlag) -> None:
        self.d_requestMove(self.selectedPiece, target, promo)

        if self.promotePawnFrame is None:
            return

        scale = self.promotePawnFrame.getScale()

        self.promotePawnFrameSeq = Sequence(
            LerpScaleInterval(self.promotePawnFrame, .2, scale * 1.2, scale, blendType="easeInOut"),
            LerpScaleInterval(self.promotePawnFrame, .2, 0.01, scale * 1.2, blendType="easeInOut"),
            Func(self.destroyPromotePawnFrame)
        )
        self.promotePawnFrameSeq.start()

    def destroyPromotePawnFrame(self) -> None:
        if self.promotePawnFrame is not None:
            self.promotePawnFrame.destroy()
            self.promotePawnFrame = None

    def stopPromotePawnFrameSeq(self) -> None:
        if self.promotePawnFrameSeq is not None:
            self.promotePawnFrameSeq.finish()
            self.promotePawnFrameSeq = None

    def displayValidMoves(self) -> None:
        """
        Displays all the valid moves that the current selected piece can
        make in the form of duplicates of the piece with blinker loops.
        :return: None
        """
        start = self.board.getBoard()[self.selectedPiece]

        for move in self.validMoves:
            piece = self.createPiece(move.target, start.piece, start.color, zOffset=0.02)

            onColor = VALID_MOVE_COLOR_ON
            offColor = VALID_MOVE_COLOR_OFF

            self.validMoveTracks[piece] = Sequence(
                LerpColorScaleInterval(piece, 1, onColor, offColor),
                LerpColorScaleInterval(piece, 1, offColor, onColor)
            )
            self.validMoveTracks[piece].loop()

    def getPiecesAmount(self, avId: int) -> Optional[int]:
        if avId not in self.player2color:
            return

        color: BoardGameColor = self.player2color[avId]
        return len(self.board.getPiecesOfColor(color))

    def createClocks(self) -> None:
        self.clocks = {avId: ChessClockNode(avId) for avId in self.players if base.cr.getDo(avId)}

    def updateClocks(self) -> None:
        for avId, clock in self.clocks.items():
            clock.setTimeLeft(self.clock[avId])
            if avId != self.currentPlayer:
                clock.stop()

    def destroyClocks(self) -> None:
        for clock in self.clocks.values():
            clock.destroy()

        self.clocks = {}

    def d_requestDraw(self) -> None:
        self.sendUpdate("requestDraw")

    def handleDrawVote(self, votes: int, avId: int) -> None:
        if not self.playerToon:
            return

        if avId == base.localAvatar.doId:
            self.drawButton["state"] = DirectGuiGlobals.DISABLED

        if votes:
            self.drawVoteLabel.show()
        else:
            self.drawVoteLabel.hide()

    def createDrawButton(self) -> None:
        self.drawButton = MainMenuButton(parent=base.a2dBottomRight, text="Offer Draw", text_scale=0.05,
                                         command=self.d_requestDraw, pos=(-0.2, 0, 0.3))
        self.drawVoteLabel = DirectLabel(parent=self.drawButton, relief=None, text_font=getMinnieFont(),
                                         text_scale=0.05, text="Votes: 1/2", pos=(0, 0, 0.1), text_fg=(1, 1, 1, 1))
        self.drawVoteLabel.hide()

    def destroyDrawButton(self) -> None:
        if self.drawButton is not None:
            self.drawButton.destroy()
            self.drawButton = None

        if self.drawVoteLabel is not None:
            self.drawVoteLabel.destroy()
            self.drawVoteLabel = None

    def clearValidMoveTracks(self) -> None:
        for geom, seq in list(self.validMoveTracks.items()):
            seq.finish()
            geom.removeNode()

        self.validMoveTracks = {}

    def finishBlinkerTrack(self) -> None:
        if self.blinkerTrack is not None:
            self.blinkerTrack.finish()
            self.blinkerTrack = None

    """
    FSM states
    """

    def enterPrepareGame(self) -> None:
        super().enterPrepareGame()

        self.boardNode.popUpStart()

        if self.isGameVisible:
            self.helpButton = self.makeQuestionButton(
                PicnicGame.CHESS, parent=base.a2dBottomRight,
                pos=(-0.173, 1, 0.70), text_fg=(1, 1, 1, 1),
            )

    def exitPrepareGame(self) -> None:
        self.boardNode.popUpStop()
        super().exitPrepareGame()

    def enterPlaying(self) -> None:
        if self.isGameVisible:
            self.createClocks()

        if self.playerToon:
            self.createDrawButton()

    def exitPlaying(self) -> None:
        self.boardNode.disableMouseCollisions()
        self.destroyDrawButton()

    def enterReward(self) -> None:
        if not self.isGameVisible:
            return

        self.updateClocks()

        if self.winner == 0:
            labelColor = (1, 0, 0, 1)
            labelText = TTLocalizer.PGTStalemate

            self.playSfx(self.drawSfx)
        else:
            avId, color = self.winner, self.player2color[self.winner]

            av = base.cr.doId2do.get(avId)
            if av is None:
                return

            labelColor = PIECE_COLORS[color]
            labelText = TTLocalizer.PGTPlayerWonGame.format(av.getName())

            if base.localAvatar.doId == self.winner:
                self.playSfx(self.victorySfx)
            else:
                self.playSfx(self.loseSfx)

        label = DirectLabel(
            relief=None, text=labelText,
            pos=(0.0, 0.0, 0.6), text_fg=labelColor, text_scale=0.08,
            text_font=ToontownGlobals.getSignFont(), scale=1.2,
        )

        self.playLabelSeq(label)

    """
    Properties
    """

    @property
    def playerHeading(self) -> int:
        if base.localAvatar.doId in self.players:
            if self.players.index(base.localAvatar.doId) == 0:
                return 0
            else:
                return 180

        return super().playerHeading

    @property
    def cameraHeight(self) -> int:
        return 8
