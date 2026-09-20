from typing import Optional

from direct.showbase.MessengerGlobal import messenger
from panda3d.core import Point3, Vec4
from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedNode import DistributedNode
from direct.fsm.FSM import FSM
from direct.gui.DirectGui import DirectLabel, DirectButton
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil

from toontown.gui.game.condition import ConditionGlobals
from toontown.safezone.picnicgame.PicnicGameHelpPanel import PicnicGameHelpPanel
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownTimer import ToontownTimer


class DistributedPicnicGame(DistributedNode, FSM):
    gameMusicKey = None
    discordPreset = None
    guiState: ConditionGlobals.ConditionState = None

    def __init__(self, cr) -> None:
        DistributedNode.__init__(self, cr)
        FSM.__init__(self, self.__class__.__name__)

        self.players = []
        self.spectators = []

        self.table = None
        self.tableDoId = None

        self.clockNode = ToontownTimer()
        self.clockNode.posInBottomRightCorner()
        self.clockNode.setScale(0.35)
        self.clockNode.hide()

        self.timerEnd = None

        self.helpButton: Optional[DirectButton] = None

        self.currentPlayer: int = -1
        self.winner: int = 0
        self.gameType: int = 0

        self.camTrack: Optional[Sequence] = None
        self.labelSeq: Optional[Sequence] = None

        self.helpPanel: Optional[PicnicGameHelpPanel] = None

        self.victorySfx = base.loader.loadSfx("phase_6/audio/sfx/Golf_Crowd_Applause.ogg")
        self.drawSfx = base.loader.loadSfx("phase_6/audio/sfx/Golf_Sad_Noise_Kicked_Off_Hole.ogg")
        self.loseSfx = base.loader.loadSfx("phase_6/audio/sfx/Golf_Crowd_Miss.ogg")
        self.turnChangeSfx = base.loader.loadSfx("phase_4/audio/sfx/SZ_trolley_bell.ogg")

        self.gameMusic = base.musicMgr.loadMusic(self.gameMusicKey)
        self.storedMusic = None

        self.toonHeadPanel = base.loader.loadModel('phase_6/models/golf/headPanel')
        self.questionGui = base.loader.loadModel('phase_3/models/gui/quest_question.bam')

    def announceGenerate(self) -> None:
        super().announceGenerate()

        if self.playerToon:
            self.applyDiscordPreset()

    def delete(self) -> None:
        self.removeAllTasks()
        self.ignoreAll()

        self.toonHeadPanel.removeNode()
        self.toonHeadPanel = None

        self.questionGui.removeNode()
        self.questionGui = None

        self.victorySfx = None
        self.drawSfx = None
        self.loseSfx = None
        self.turnChangeSfx = None

        self.destroyHelpButton()
        self.destroyTimer()
        self.stopGameMusic()
        self.revertDiscordPreset()
        self.closeHelpPanel()

        self.gameMusic = None
        self.storedMusic = None

        self.timerEnd = None

        self.players = []
        self.spectators = []
        self.table = None
        self.tableDoId = None

        FSM.cleanup(self)
        super().delete()

    def d_requestGameState(self) -> None:
        self.sendUpdate("requestGameState")

    def createConditionalUI(self):

        def updateConditionUI(task=None):
            task.delayTime = 0.5
            messenger.send(ConditionGlobals.RefreshMsg)
            return task.again

        stateArgs = ConditionGlobals.ConditionStateArgs()
        stateArgs[ConditionGlobals.ConditionStateArg.PICNIC_GAME] = self
        messenger.send(ConditionGlobals.SetStateMsg, [self.guiState, stateArgs])
        self._addTask(
            self.doMethodLater(1.0, updateConditionUI, name=self.uniqueName('updateConditionUI'))
        )

    def avatarEnter(self, avId: int) -> None:
        if avId != base.localAvatar.doId:
            return

        self.moveCamera()
        self.playGameMusic()
        self.applyDiscordPreset()
        self.createConditionalUI()

    def avatarExit(self, avId: int) -> None:
        if avId != base.localAvatar.doId:
            return

        self.stopMoveCamera()
        self.destroyHelpButton()
        self.stopGameMusic()
        self.revertDiscordPreset()

        # Have condition manager go back to normal
        messenger.send(ConditionGlobals.SetStateMsg, [ConditionGlobals.ConditionState.GLOBAL])

    def setGameType(self, gameType: int) -> None:
        self.gameType = gameType

    def setState(self, state: str) -> None:
        self.request(state)

    def setPlayers(self, players) -> None:
        self.players = players

    def setSpectators(self, spectators) -> None:
        self.spectators = spectators

    def setTableDoId(self, tableDoId: int) -> None:
        self.tableDoId = tableDoId
        self.table = base.cr.getDo(tableDoId)
        if self.table is None:
            return

        if getattr(self.table, "tableCloth", None) is None:
            self.reparentTo(aspect2d)
        else:
            self.reparentTo(self.table.tableCloth)

    def setTimerEnd(self, timerEnd: int) -> None:
        now = globalClock.getFrameTime()
        self.timerEnd = globalClockDelta.networkToLocalTime(timerEnd, now, bits=32)
        if self.isGameVisible:
            self.startTimer()

    def setCurrentPlayer(self, avId: int) -> None:
        self.currentPlayer = avId

    def setWinner(self, avId: int) -> None:
        self.winner = avId

    def startTimer(self) -> None:
        if self.timerEnd is None or self.clockNode is None:
            return

        # Stop the timer in case it's still running.
        self.clockNode.stop()

        now = globalClock.getFrameTime()
        timeLeft = self.timerEnd - now

        self.clockNode.countdown(timeLeft, self.stopTimer)
        self.clockNode.show()

    def stopTimer(self) -> None:
        if self.clockNode is None:
            return

        self.clockNode.stop()
        self.clockNode.hide()

    def destroyTimer(self) -> None:
        if self.clockNode is None:
            return

        self.stopTimer()
        self.clockNode.destroy()
        self.clockNode = None

    def moveCamera(self) -> None:
        if not self.table or self.table.cameraControl:
            return

        heading = PythonUtil.fitDestAngle2Src(camera.getH(self.table.tableCloth), self.playerHeading)

        self.camTrack = camera.posHprInterval(2, Point3(0, 0, self.cameraHeight), Point3(heading, -90, 0),
                                              blendType='easeInOut')
        self.camTrack.start()

    def stopMoveCamera(self) -> None:
        if self.camTrack is not None:
            self.camTrack.finish()
            self.camTrack = None

    def destroyHelpButton(self) -> None:
        if self.helpButton is not None:
            self.helpButton.destroy()
            self.helpButton = None

    def playLabelSeq(self, label: DirectLabel) -> None:
        labelScale = label.getScale()

        self.labelSeq = Sequence(
            label.scaleInterval(.2, labelScale * 1.1, startScale=0.01, blendType='easeInOut'),
            label.scaleInterval(.2, labelScale, blendType='easeInOut'),
            Wait(3.0),
            LerpColorScaleInterval(label, 1.0, Vec4(1.0, 1.0, 1.0, 0.0)),
        )
        self.labelSeq.start()

    def playSfx(self, sfx) -> None:
        """
        Play a sfx but make sure that the local toon is seated at the table
        to prevent people who are off of the table from hearing it.
        :param sfx:
        :return:
        """
        if self.isGameVisible:
            base.playSfx(sfx)

    def playGameMusic(self) -> None:
        """
        Smoothly transition between the playground music track and the
        current game's music track.
        """
        messenger.send("playPicnicMusic", [self.gameMusic])

        if not self.playerToon or self.gameMusic is None or not base.musicMgr.playingMusic.keys():
            return

        self.storedMusic = list(base.musicMgr.playingMusic.keys())[0]
        base.musicMgr.crossfadeIntoMusic(self.gameMusic, duration=1.5, musicCode=self.gameMusicKey)

    def stopGameMusic(self) -> None:
        """
        Smoothly transition between the current game's music track and the
        playground music.
        """
        messenger.send("stopPicnicMusic", [self.gameMusic])

        if self.storedMusic is None:
            return

        base.musicMgr.crossfadeIntoMusic(self.storedMusic, duration=1.5)
        self.storedMusic = None

    def applyDiscordPreset(self) -> None:
        """Update the player's Discord RPC depending on the current game.
        """
        base.discord.applyPreset(self.discordPreset)

    def revertDiscordPreset(self) -> None:
        """Revert the Discord RPC back to their current zone.
        """
        base.discord.setZone(base.localAvatar.zoneId)

    """
    Info button
    """

    def openHelpPanel(self, game: int) -> None:
        if self.helpPanel is None:
            self.helpPanel = PicnicGameHelpPanel(game)
            self.acceptOnce(PicnicGameHelpPanel.CLOSE_EVENT, self.closeHelpPanel)

    def closeHelpPanel(self) -> None:
        if self.helpPanel is not None:
            self.helpPanel.destroy()
            self.helpPanel = None

    def makeQuestionButton(self, game: int, **kwargs) -> DirectButton:
        helpText = TTLocalizer.PGTHelpQuestionText
        return DirectButton(
            relief=None, image=self.questionGui.find("**/quest_exclaim"), scale=0.12,
            text=("", helpText, helpText, ""),
            text_pos=(0, -0.9), text_scale=0.4,
            command=self.openHelpPanel, extraArgs=[game], **kwargs
        )

    """
    FSM states
    """

    def enterPrepareGame(self):
        if self.isGameVisible:
            self.moveCamera()
            self.playGameMusic()
            self.createConditionalUI()

    def exitPrepareGame(self):
        if self.isGameVisible:
            self.stopMoveCamera()

    def enterPlaying(self):
        pass

    def exitPlaying(self):
        self.destroyTimer()

    def enterReward(self):
        pass

    def exitReward(self):
        if self.labelSeq is not None:
            self.labelSeq.finish()
            self.labelSeq = None

    """
    Properties
    """

    @property
    def playerToon(self) -> bool:
        return base.localAvatar.doId in self.players

    @property
    def isGameVisible(self) -> bool:
        return base.localAvatar.doId in self.players + self.spectators

    @property
    def playerHeading(self) -> int:
        return 0 if self.table.localSeatIndex < 3 else 180

    @property
    def cameraHeight(self) -> int:
        return 17
