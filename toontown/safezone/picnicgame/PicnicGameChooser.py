from typing import Optional

from direct.fsm.FSM import FSM
from direct.gui import DirectGuiGlobals
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel

from toontown.gui.ScaledFrame import ScaledFrame
from toontown.gui.TTGui import ScalingButton
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.safezone.picnicgame.BoardGameGlobals import getToonPanels
from toontown.safezone.picnicgame.HouseRulesFrame import HouseRulesFrame
from toontown.safezone.picnicgame.PicnicGameArrowButton import PicnicGameArrowButton
from toontown.safezone.picnicgame.PicnicGameGlobals import PGT_PLAYER_LIMITS, GAME_BUTTON_POS, PGT_GAME_NAMES, \
    PicnicGame, ARROW_COLOR_GREEN, ARROW_COLOR_RED
from toontown.safezone.picnicgame.PicnicGameHelpPanel import PicnicGameHelpPanel
from toontown.toonbase import ToontownGlobals, TTLocalizer


class PicnicGameChooser(ScaledFrame, FSM):
    EVENT_CHOICE_ARROW = "ChoiceArrowRequest"

    def __init__(self, table):
        self.table = table

        ScaledFrame.__init__(
            self, parent=aspect2d, relief=None,
            frameSize=(-1 / 2 * 1.7, 1 / 2 * 1.7, -1 / 2, 1 / 2)
        )
        self.initialiseoptions(PicnicGameChooser)
        self["shadowStrength"] = 0.04

        FSM.__init__(self, "PicnicGameChooser")

        self.choiceArrows: dict[int, PicnicGameArrowButton] = {}

        self.accept(self.EVENT_CHOICE_ARROW, self.togglePlayer)

        # Listen for any toons entering.
        self.accept(self.table.uniqueName("enteredTableSeat"), self.handleEnteredSeat)

        # Listen for any toons exiting.
        self.accept(self.table.uniqueName("exitedTableSeat"), self.handleExitedSeat)

        # Listen for changes in leadership.
        self.accept(self.table.uniqueName("pgt_leader_updated"), self.setLeader)

        # Listen for when the chosen game changes.
        self.accept(self.table.uniqueName("pgt_chosenGame_updated"), self.setGameChosen)

        # Listen for when the list of players changes.
        self.accept(self.table.uniqueName("pgt_playerList_updated"), self.setPlayerList)

        self.leaderMode = False
        self.leader = 0

        # This is the game index that the leader has chosen that was sent from and approved by the server.
        self.gameChosen = -1

        # This is the game index that the leader has chosen, but hasn't sent to the server yet.
        self.localGameChosen = -1

        self.playerList = []

        self.questionButtons = []

        self.helpPanel: Optional[PicnicGameHelpPanel] = None
        self.questionGui = base.loader.loadModel('phase_3/models/gui/quest_question.bam')

        self.frame_houseRules: Optional[HouseRulesFrame] = None

        self.houseRulesChosen = DirectLabel(
            parent=self, relief=None, pos=(0, 0, -0.25),
            text=TTLocalizer.PGTHouseRulesChosen.format("None"),
            text_scale=0.05, textMayChange=True, text_wordwrap=20,
        )
        self.houseRulesChosen.hide()

    def destroy(self):
        FSM.cleanup(self)

        self.questionGui.removeNode()
        self.questionGui = None

        self.destroyHouseRules()
        self.destroyChoiceArrows()

        self.houseRulesChosen.destroy()
        del self.houseRulesChosen

        self.ignoreAll()

        ScaledFrame.destroy(self)

    def getToonPanel(self, avId: int):
        panels = [panel for panel in getToonPanels() if panel.obj.doId == avId]
        if panels:
            return panels[0]

    def createChoiceArrow(self, panel, avId: int) -> None:
        self.choiceArrows[avId] = PicnicGameArrowButton(
            panel.flipAnchor, self.EVENT_CHOICE_ARROW, [avId],
            pos=(0.14, 0, 0), scale=0.2,
        )
        if avId in self.playerList:
            self.choiceArrows[avId].startColorLoop(ARROW_COLOR_GREEN)
        else:
            self.choiceArrows[avId].startColorLoop(ARROW_COLOR_RED)

    def destroyChoiceArrows(self) -> None:
        for arrow in self.choiceArrows.values():
            arrow.destroy()

        self.choiceArrows = {}

    """
    Message handlers
    """

    def handleEnteredSeat(self, avId: int) -> None:
        if self.getCurrentOrNextState() != "LeaderTwo":
            return

        panel = self.getToonPanel(avId)
        if panel:
            self.createChoiceArrow(panel, avId)

    def handleExitedSeat(self, avId: int) -> None:
        if self.getCurrentOrNextState() != "LeaderTwo":
            return

        if avId in self.choiceArrows:
            self.choiceArrows[avId].destroy()
            del self.choiceArrows[avId]

    """
    Setter functions
    """

    def requestState(self, state: str) -> None:
        """Safe way of requesting a new state which ensures that the requested
        state isn't the same as the current state.
        """
        if state == self.getCurrentOrNextState():
            return

        # It's safe to request this state.
        self.request(state)

    def setLeaderMode(self, leaderMode: bool) -> None:
        self.leaderMode = leaderMode

        self.updateState()

    def setLeader(self, leader: int) -> None:
        self.leader = leader

        self.setLeaderMode(leader == base.localAvatar.doId)

    def setGameChosen(self, gameChosen: int) -> None:
        self.gameChosen = gameChosen
        self.updateState()

    def setPlayerList(self, players) -> None:
        self.playerList = players
        self.updatePlayerList()

    """
    Button handlers
    """

    def openHouseRules(self) -> None:
        self.frame_houseRules = HouseRulesFrame(self, self.table)

    def switchPage(self, pageNum: int) -> None:
        """Sends an update to the server depending on which page is being
        turned to. If it's the first page, reset the game chosen, or if it's
        the second page, send the local game chosen by the leader.
        """
        if pageNum == 1:
            self.table.d_requestChosenGame(-1)
        else:
            self.table.d_requestChosenGame(self.localGameChosen)

    def gameButtonCommand(self, game_index: int) -> None:
        self.localGameChosen = game_index

        for button in self.gameButtons:
            button["state"] = DirectGuiGlobals.NORMAL

        self.gameButtons[game_index]["state"] = DirectGuiGlobals.DISABLED

        self.switchPage(2)

    def updateState(self) -> None:
        """Whenever leadership is changed or the game chosen is changed, this
        should be called to update the state.
        """
        state_lm = "Leader" if self.leaderMode else "Player"
        state_gc = "One" if self.gameChosen == -1 else "Two"

        self.requestState(state_lm + state_gc)

    def togglePlayer(self, avId: int) -> None:
        if avId in self.playerList:
            self.playerList.remove(avId)
        else:
            self.playerList.append(avId)

        self.sendPlayerList()

    def sendPlayerList(self) -> None:
        self.table.d_requestPlayerList(self.playerList)

    def updatePlayerList(self) -> None:
        if self.state == "LeaderTwo":
            playerMin, playerMax = PGT_PLAYER_LIMITS[self.gameChosen]
            if playerMin <= len(self.playerList) <= playerMax:
                self.playGameButton["state"] = DirectGuiGlobals.NORMAL
            else:
                self.playGameButton["state"] = DirectGuiGlobals.DISABLED

            for avId, arrow in self.choiceArrows.items():
                if avId in self.playerList:
                    arrow.startColorLoop(ARROW_COLOR_GREEN)
                else:
                    arrow.startColorLoop(ARROW_COLOR_RED)

        if self.state in ("LeaderTwo", "PlayerTwo"):
            self.updatePlayersLabel(len(self.playerList))

    def requestPlayGame(self):
        self.table.d_requestPlayGame()

    def destroyQuestionButtons(self) -> None:
        for button in self.questionButtons:
            button.destroy()

        self.questionButtons = []

        self.closeHelpPanel()

    def updatePlayersLabel(self, players: int) -> None:
        playerMin, playerMax = PGT_PLAYER_LIMITS[self.gameChosen]

        if playerMin == playerMax:
            playerCount = str(playerMax)
        else:
            playerCount = f"{playerMin} - {playerMax}"

        self.playersLabel["text"] = TTLocalizer.PGTPlayersChosen.format(players, playerCount)

    def destroyHouseRules(self) -> None:
        if self.frame_houseRules is not None:
            self.frame_houseRules.destroy()
            self.frame_houseRules = None

    def showHouseRulesChosen(self) -> None:
        self.accept(self.table.uniqueName("pgt_houseRules_updated"), self.houseRulesUpdated)
        self.houseRulesChosen.show()
        self.houseRulesUpdated(self.table.houseRules)

    def hideHouseRulesChosen(self) -> None:
        self.houseRulesChosen.hide()
        self.ignore(self.table.uniqueName("pgt_houseRules_updated"))

    def houseRulesUpdated(self, houseRules) -> None:
        if not self.houseRulesChosen.isHidden():
            houseRulesEnabled = ", ".join([
                TTLocalizer.PGTHouseRuleNames.get(houseRule) \
                for houseRule, status in houseRules.items() if status])

            if not houseRulesEnabled:
                houseRulesEnabled = "None"

            self.houseRulesChosen["text"] = TTLocalizer.PGTHouseRulesChosen.format(houseRulesEnabled)

    """
    Info button
    """

    def openHelpPanel(self, game: int) -> None:
        if self.helpPanel is None:
            self.helpPanel = PicnicGameHelpPanel(game)
            self.accept(PicnicGameHelpPanel.CLOSE_EVENT, self.closeHelpPanel)

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

    def enterLeaderOne(self):
        self.title = DirectLabel(
            self, relief=None, text=TTLocalizer.PGTLOneTitle,
            pos=(0.0, 0.0, 0.4), text_fg=(1, 0, 0, 1), text_scale=0.08,
            text_font=ToontownGlobals.getSignFont(),
        )

        self.gameButtons = []

        gui = base.loader.loadModel("phase_6/models/gui/minigame_select_buttons")

        for i in range(len(PicnicGame)):
            pos = GAME_BUTTON_POS[i]
            name = PGT_GAME_NAMES[i]
            button = ScalingButton(
                self, pos=pos,
                image=(gui.find(f"**/{name}_UP"), gui.find(f"**/{name}_DN"), gui.find(f"**/{name}_RLVR")),
                image_scale=(0.53, 0, 0.3),
                command=self.gameButtonCommand, extraArgs=[i],
            )
            self.gameButtons.append(button)

            self.questionButtons.append(self.makeQuestionButton(i, parent=self, pos=(pos[0], 1, pos[2] - 0.2)))

        gui.remove_node()

    def exitLeaderOne(self):
        self.title.destroy()
        self.title = None

        for button in self.gameButtons:
            button.destroy()

        self.gameButtons = []

        self.destroyQuestionButtons()

    def enterLeaderTwo(self):
        self.title = DirectLabel(
            self, relief=None, text=TTLocalizer.PGTLTwoTitle,
            pos=(0.0, 0.0, 0.4), text_fg=(1, 0, 0, 1), text_scale=0.08,
            text_font=ToontownGlobals.getSignFont(),
        )

        self.gameLabel = DirectLabel(
            self, relief=None,
            text=TTLocalizer.PGTGameChosen.format(TTLocalizer.PGTGameNames[self.gameChosen]),
            pos=(-0.4, 0.0, 0.0), text_scale=0.08,
        )

        self.questionButtons.append(self.makeQuestionButton(self.gameChosen, parent=self, pos=(0, 1, 0)))

        self.playersLabel = DirectLabel(
            self, relief=None,
            text="", textMayChange=True,
            pos=(0.4, 0.0, 0.0), text_scale=0.08
        )
        self.updatePlayersLabel(0)

        self.backButton = MainMenuButton(
            self, pos=(-0.65, 0.0, -0.425),
            text=TTLocalizer.lBack,
            command=self.switchPage, extraArgs=[1],
        )

        self.playGameButton = MainMenuButton(
            self, pos=(0.65, 0.0, -0.425),
            text=TTLocalizer.PGTPlayGame,
            command=self.requestPlayGame
        )
        self.playGameButton["state"] = DirectGuiGlobals.DISABLED

        self.helpLabel = DirectLabel(
            self, relief=None, text=TTLocalizer.PGTPlayerPickHelp,
            pos=(0.0, 0.0, 0.3), text_scale=0.06, text_wordwrap=24
        )

        self.playerList = [self.table.leader]
        self.sendPlayerList()

        if self.gameChosen == PicnicGame.TOONO:
            button_size = (.35, .15, .15)
            self.houseRulesButton = MainMenuButton(
                self, pos=(0.0, 0.0, -0.425),
                text=TTLocalizer.PGTHouseRules,
                command=self.openHouseRules,
                image_scale=button_size,
                image1_scale=button_size,
                image2_scale=button_size,
            )
            self.showHouseRulesChosen()

        self.destroyChoiceArrows()

        for panel in getToonPanels():
            avId = panel.obj.doId
            # Ignore our own panel.
            if panel.obj.isLocal():
                continue

            self.createChoiceArrow(panel, avId)

    def exitLeaderTwo(self):
        self.destroyQuestionButtons()
        self.destroyChoiceArrows()

        self.title.destroy()
        self.title = None

        self.gameLabel.destroy()
        self.gameLabel = None

        self.playersLabel.destroy()
        self.playersLabel = None

        self.backButton.destroy()
        self.backButton = None

        self.playGameButton.destroy()
        self.playGameButton = None

        self.helpLabel.destroy()
        self.helpLabel = None

        self.playerList = []
        self.sendPlayerList()

        if hasattr(self, "houseRulesButton") and self.houseRulesButton is not None:
            self.houseRulesButton.destroy()
            self.houseRulesButton = None

        self.destroyHouseRules()
        self.hideHouseRulesChosen()

    def enterPlayerOne(self):
        self.title = DirectLabel(
            self, relief=None, text=TTLocalizer.PGTPlayerGameWaiting,
            pos=(0.0, 0.0, 0.0),  # text_fg=(1, 1, 1, 1),
            text_scale=0.08,
            # text_font=ToontownGlobals.getSignFont(),
        )

    def exitPlayerOne(self):
        self.title.destroy()
        self.title = None

    def enterPlayerTwo(self):
        self.gameLabel = DirectLabel(
            self, relief=None,
            text=TTLocalizer.PGTGameChosen.format(TTLocalizer.PGTGameNames[self.gameChosen]),
            pos=(-0.4, 0.0, 0.0), text_scale=0.08,
        )

        self.questionButtons.append(self.makeQuestionButton(self.gameChosen, parent=self, pos=(0, 1, 0)))

        self.playersLabel = DirectLabel(
            self, relief=None,
            text="", textMayChange=True,
            pos=(0.4, 0.0, 0.0), text_scale=0.08
        )
        self.updatePlayersLabel(0)

        self.title = DirectLabel(
            self, relief=None, text=TTLocalizer.PGTPlayerPlayersWaiting,
            pos=(0.0, 0.0, 0.4), text_scale=0.08,
        )

        if self.gameChosen == PicnicGame.TOONO:
            self.showHouseRulesChosen()

    def exitPlayerTwo(self):
        self.title.destroy()
        self.title = None

        self.gameLabel.destroy()
        self.gameLabel = None

        self.playersLabel.destroy()
        self.playersLabel = None

        self.destroyQuestionButtons()
        self.hideHouseRulesChosen()
