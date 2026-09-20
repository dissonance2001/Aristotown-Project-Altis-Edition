from typing import Dict, List, Optional

from panda3d.core import NodePath
from direct.gui.DirectLabel import DirectLabel
from direct.interval.IntervalGlobal import *

from toontown.gui.game.condition.ConditionGlobals import ConditionState
from toontown.safezone.picnicgame import PicnicGameGlobals
from toontown.safezone.picnicgame.BoardGameGlobals import BoardGameColor, VALID_MOVE_COLOR_ON, VALID_MOVE_COLOR_OFF, \
    PIECE_TINT_COLOR, PIECE_COLORS, ChessClock
from toontown.safezone.picnicgame.CheckerBoardNode import CheckerBoardNode
from toontown.safezone.picnicgame.CheckersGlobals import CheckerBoard, CheckerMove
from toontown.safezone.picnicgame.ChessClockNode import ChessClockNode
from toontown.safezone.picnicgame.DistributedPicnicGame import DistributedPicnicGame
from toontown.toonbase import TTLocalizer, ToontownGlobals


class DistributedCheckers(DistributedPicnicGame):
    gameMusicKey = "picnic_checkers"
    discordPreset = "checkers"
    guiState = ConditionState.PGT_CHECKERS

    def __init__(self, cr) -> None:
        super().__init__(cr)

        self.board = CheckerBoard()
        self.clock = ChessClock()
        self.clocks: dict[int, ChessClockNode] = {}
        self.pieces: Dict[int, NodePath] = {}
        self.selectedPiece: int = -1
        self.validMoves: List[CheckerMove] = []
        self.receivedGameState: bool = False
        self.currentColor: BoardGameColor = BoardGameColor.WHITE

        self.boardNode: Optional[CheckerBoardNode] = None

        self.blinkerTrack: Optional[Sequence] = None
        self.validMoveTracks: Dict[NodePath, Sequence] = {}

        self.checkerPieces: Dict[BoardGameColor, NodePath] = {
            BoardGameColor.WHITE: base.loader.loadModel(f"phase_6/models/golf/regular_checker_piecewhite.bam"),
            BoardGameColor.BLACK: base.loader.loadModel(f"phase_6/models/golf/regular_checker_pieceblack.bam")
        }

        # Sound effects for board games.
        self.knockSfx = base.loader.loadSfx("phase_5/audio/sfx/GUI_knock_1.ogg")
        self.clickSfx = base.loader.loadSfx("phase_3/audio/sfx/GUI_balloon_popup.ogg")
        self.moveSfx = base.loader.loadSfx("phase_6/audio/sfx/CC_move.ogg")

        self.player2color: Dict[int, BoardGameColor] = {}

    def delete(self) -> None:
        super().delete()

        self.destroyClocks()
        self.clearValidMoveTracks()
        self.finishBlinkerTrack()

        self.board.cleanup()
        self.board = None

        self.clock.cleanup()
        self.clock = None

        if self.boardNode is not None:
            self.boardNode.cleanup()
            self.boardNode = None

        for piece in self.pieces.values():
            piece.removeNode()

        self.pieces = {}

        for piece in self.checkerPieces.values():
            piece.removeNode()

        self.checkerPieces = {}

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

    def getPiecesAmount(self, avId: int) -> Optional[int]:
        if avId not in self.player2color:
            return

        color: BoardGameColor = self.player2color[avId]
        return len(self.board.getPiecesOfColor(color))

    def setPlayers(self, players) -> None:
        super().setPlayers(players)

        if len(self.players) == 2:
            self.player2color = {
                self.players[0]: BoardGameColor.WHITE,
                self.players[1]: BoardGameColor.BLACK,
            }

    def createPiece(self, index: int, color: BoardGameColor, king: bool, zOffset: float = 0) -> NodePath:
        pieceNode = self.checkerPieces[color].copyTo(NodePath())
        pieceNode.setColor(1, 1, 1, 1)
        pieceNode.reparentTo(self.boardNode.locators[index])

        if zOffset:
            pieceNode.setZ(pieceNode.getZ() + zOffset)

        if not king:
            pieceNode.find("**/checker_k*").hide()

        # Rotate the piece to match our local seated toon, if necessary.
        if self.isGameVisible:
            pieceNode.setH(self.playerHeading)

        return pieceNode

    def setGameState(self, gameState: List[List[int]], timeLeftInfo: List[List[int]]) -> None:
        # Load the board.
        self.board.loadBoardFromState(gameState)

        # Load the pieces.
        for square in self.board.getBoard():
            if square.color == BoardGameColor.NONE:
                continue
            self.pieces[square.index] = self.createPiece(square.index, square.color, square.king)

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

        self.d_requestMove(move.start, move.target)
        return True

    def d_requestMove(self, start: int, target: int) -> None:
        self.sendUpdate("requestMove", [start, target])

    def movePiece(self, start: int, target: int, captures: List[int]) -> None:
        if not self.receivedGameState:
            return

        self.selectedPiece = -1
        self.validMoves = []

        # Update the board representation with this move.
        self.board.makeMove(start, target, captures)

        piece = self.pieces.get(start)
        if piece is None:
            return

        del self.pieces[start]

        # Ensure that the piece that was sitting on this square is gone.
        oldPiece = self.pieces.get(target)
        if oldPiece is not None:
            oldPiece.removeNode()

        # Move the piece to the target square.
        piece.setPos(0, 0, 0)
        piece.reparentTo(self.boardNode.locators[target])

        # Ensure that the king is crowned.
        if self.board.getBoard()[target].king:
            piece.find("**/checker_k*").show()

        self.pieces[target] = piece

        # Remove the captured pieces from the board.
        for capture in captures:
            capturePiece = self.pieces.get(capture)
            if capturePiece is None:
                continue

            capturePiece.removeNode()
            del self.pieces[capture]

        self.playSfx(self.moveSfx)

    def displayValidMoves(self) -> None:
        """
        Displays all the valid moves that the current selected piece can
        make in the form of duplicates of the piece with blinker loops.
        :return: None
        """
        start = self.board.getBoard()[self.selectedPiece]

        for move in self.validMoves:
            piece = self.createPiece(move.target, start.color, start.king, zOffset=0.02)

            onColor = VALID_MOVE_COLOR_ON
            offColor = VALID_MOVE_COLOR_OFF

            self.validMoveTracks[piece] = Sequence(
                LerpColorScaleInterval(piece, 1, onColor, offColor),
                LerpColorScaleInterval(piece, 1, offColor, onColor)
            )
            self.validMoveTracks[piece].loop()

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
                PicnicGameGlobals.PicnicGame.CHECKERS, parent=base.a2dBottomRight,
                pos=(-0.173, 1, 0.70), text_fg=(1, 1, 1, 1),
            )

    def exitPrepareGame(self) -> None:
        self.boardNode.popUpStop()
        super().exitPrepareGame()

    def enterPlaying(self) -> None:
        if self.isGameVisible:
            self.createClocks()

    def exitPlaying(self) -> None:
        for clock in self.clocks.values():
            clock.stop()

        self.boardNode.disableMouseCollisions()

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
