from direct.gui.DirectGui import DirectLabel, DirectButton
from direct.showbase.MessengerGlobal import messenger

from toontown.gui.ScaledFrame import ScaledFrame

from toontown.safezone.picnicgame import PicnicGameGlobals
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import TTLocalizer


class PicnicGameHelpPanel(ScaledFrame):
    CLOSE_EVENT = "PicnicGameHelpPanel_CloseButton"

    def __init__(self, game: int) -> None:
        super().__init__(
            parent=aspect2d, relief=None, popIn=True,
            frameSize=(-1 / 2, 1 / 2, -1 / 2 * 1.3, 1 / 2 * 1.3),
        )
        self.initialiseoptions(PicnicGameHelpPanel)
        self["shadowStrength"] = 0.04

        self.createcomponent(
            "title", (), None, DirectLabel,
            parent=self, relief=None,
            text=TTLocalizer.PGTGameNames[game],
            text_scale=0.1, pos=(0, 0, 0.55),
        )

        minPlayers, maxPlayers = PicnicGameGlobals.PGT_PLAYER_LIMITS[game]

        if minPlayers == maxPlayers:
            playerLimit = TTLocalizer.PGTHelpPanelPlayerLimit.format(maxPlayers)
        else:
            playerLimit = TTLocalizer.PGTHelpPanelPlayerLimits.format(minPlayers, maxPlayers)

        self.createcomponent(
            "playerLimits", (), None, DirectLabel,
            parent=self, relief=None,
            text=playerLimit,
            text_scale=0.07, pos=(0, 0, 0.45),
        )

        self.createcomponent(
            "howToPlay", (), None, DirectLabel,
            parent=self, relief=None,
            text=TTLocalizer.PgtHelpPanelHowToPlay,
            text_scale=0.08, pos=(0, 0, 0.3),
        )

        self.createcomponent(
            "description", (), None, DirectLabel,
            parent=self, relief=None,
            text=TTLocalizer.PGTHelpPanelDescs[game],
            text_scale=0.05, pos=(0, 0, 0.2), text_wordwrap=17,
        )

        self.createcomponent(
            "goal", (), None, DirectLabel,
            parent=self, relief=None,
            text=TTLocalizer.PGTHelpPanelGoal,
            text_scale=0.08, pos=(0, 0, -0.2),
        )

        self.createcomponent(
            "goalDesc", (), None, DirectLabel,
            parent=self, relief=None,
            text=TTLocalizer.PGTHelpPanelGoals[game],
            text_scale=0.05, pos=(0, 0, -0.3), text_wordwrap=17,
        )

        gui = base.loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')

        self.createcomponent(
            "exitButton", (), None, DirectButton,
            parent=self, relief=None,
            image=(
                gui.find('**/CloseBtn_UP'),
                gui.find('**/CloseBtn_DN'),
                gui.find('**/CloseBtn_Rllvr'),
                gui.find('**/CloseBtn_UP')
            ),
            pos=(0.45, 0, -0.6),
            command=messenger.send,
            extraArgs=[PicnicGameHelpPanel.CLOSE_EVENT]
        )

        gui.removeNode()

        base.transitions.fadeScreen(0.5)

        self.setBin('sorted-gui-popup', GuiBinGlobals.TTDialogBin)

    def destroy(self) -> None:
        base.transitions.noFade()
        super().destroy()
