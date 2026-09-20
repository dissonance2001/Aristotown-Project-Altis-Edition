from panda3d.core import Vec3, VBase4
from direct.gui.DirectGui import DGG, DirectLabel, DirectButton

from toontown.gui.ScaledFrame import ScaledFrame
from toontown.menu.MainMenuGui import MainMenuButton, hoverButton
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import ToontownGlobals, TTLocalizer


class HouseRulesFrame(ScaledFrame):
    """HouseRulesFrame: interface for updating house rules for the current game.
    """

    def __init__(self, uiParent, distObj) -> None:
        super().__init__(
            parent=uiParent,
            relief=None,
            image_color=ToontownGlobals.GlobalDialogColor,
            popIn=True,
            frameSize=(-1/2 * 1.5, 1/2 * 1.5, -1/2 * 1.2, 1/2 * 1.2)
        )
        self.initialiseoptions(HouseRulesFrame)
        self["shadowStrength"] = 0.04

        self.uiParent = uiParent
        self.distObj = distObj

        self.houseRules = self.distObj.houseRules

        self.createcomponent(
            "title", (), None, DirectLabel,
            parent=self, relief=None, text=TTLocalizer.PGTHouseRulesTitle,
            text_scale=0.1, pos=(0, 0, 0.5),
        )

        self.houseRuleInfo = self.createcomponent(
            "houseRuleInfo", (), None, DirectLabel,
            parent=self, relief=None, pos=(0, 0, -0.4), text=TTLocalizer.PGTHouseRuleDescDefault, 
            textMayChange=True, text_scale=0.05, text_wordwrap=20,
        )

        self.houseRuleButtons = {}

        index = 0
        for houseRule, value in self.houseRules.items():
            z = 0.35 - (0.15 * index)

            self.createcomponent(
                f"houseRuleLabel{index}", (), None, DirectLabel,
                parent=self, relief=None, text=TTLocalizer.PGTHouseRuleNames.get(houseRule, ""), text_scale=0.05,
                pos=(-0.25, 0.0, z)
            )
            button_size = (.30, .15, .125)
            houseRuleButton = self.createcomponent(
                f"houseRuleButton{index}", (), None, MainMenuButton,
                parent=self, pos=(0.3, 0.0, z + 0.0125),
                text=self.getValueText(value),
                command=self.toggleHouseRule, extraArgs=[houseRule],
                image_scale=button_size, image1_scale=button_size,
                image2_scale=button_size,
            )
            houseRuleButton.bind(DGG.ENTER, self.showHouseRuleInfo, extraArgs=[houseRuleButton, houseRule])
            houseRuleButton.bind(DGG.EXIT, self.hideHouseRuleInfo, extraArgs=[houseRuleButton])

            self.houseRuleButtons[houseRule] = houseRuleButton

            index += 1

        gui = base.loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')

        self.createcomponent(
            "exitButton", (), None, DirectButton,
            parent=self, relief=None, scale=1.25,
            image=(
                gui.find('**/CloseBtn_UP'),
                gui.find('**/CloseBtn_DN'),
                gui.find('**/CloseBtn_Rllvr'),
                gui.find('**/CloseBtn_UP')
            ),
            text_fg=VBase4(0, 0, 0, 1), pos=(0.7, 0, -0.55),
            # This method can exist on either the distributed object or the ui parent.
            command=getattr(self.distObj, "destroyHouseRules", None) or \
                getattr(self.uiParent, "destroyHouseRules", None),
        )

        gui.removeNode()

        base.transitions.fadeScreen(0.5)

        self.setBin('sorted-gui-popup', GuiBinGlobals.FadeBin + 1)
    
    def destroy(self) -> None:
        base.transitions.noFade()

        self.sendHouseRules()

        if hasattr(self, "houseRuleButtons"):
            for button in self.houseRuleButtons.values():
                button.destroy()

            del self.houseRuleButtons
        
        if hasattr(self, "houseRuleInfo"):
            self.houseRuleInfo.destroy()
            del self.houseRuleInfo

        del self.uiParent
        del self.distObj

        super().destroy()
    
    @staticmethod
    def getValueText(value: bool) -> str:
        return TTLocalizer.PGTHouseRuleEnabled if value else TTLocalizer.PGTHouseRuleDisabled
    
    def toggleHouseRule(self, houseRule: str) -> None:
        if houseRule not in self.houseRules:
            return

        self.houseRules[houseRule] = not self.houseRules[houseRule]
        self.houseRuleButtons[houseRule]["text"] = self.getValueText(self.houseRules[houseRule])
    
    def sendHouseRules(self) -> None:
        houseRuleData = [(houseRule, value) for houseRule, value in self.houseRules.items()]
        self.distObj.d_sendHouseRules(houseRuleData)
    
    def showHouseRuleInfo(self, button: DirectButton, houseRule: int, event) -> None:
        self.houseRuleInfo["text"] = TTLocalizer.PGTHouseRuleDesc.get(houseRule)
        hoverButton(button, 1.1, None)

    def hideHouseRuleInfo(self, button: DirectButton, event) -> None:
        self.houseRuleInfo["text"] = TTLocalizer.PGTHouseRuleDescDefault
        hoverButton(button, 1, None)
