from direct.gui.DirectGui import *
from toontown.menu.MainMenuScreen import MainMenuScreen
from toontown.dmenu import DMenuOptions
from toontown.toonbase import TTLocalizer
from toontown.toontowngui.TTGui import btnDn, btnRlvr, btnUp


class MainMenuScreenOptions(MainMenuScreen):
    def __init__(self):
        self.optionsMgr = None
        self.backButton = None
        MainMenuScreen.__init__(self)

    def createUI(self):
        self.optionsMgr = DMenuOptions.DMenuOptions()
        self.optionsMgr.showOptions(animate=False)

        self.backButton = DirectButton(
            parent=self.optionsMgr.optionsNode,
            relief=None,
            image=(btnUp, btnDn, btnRlvr),
            text='Back',
            text_fg=(0, 0, 0, 1),
            text_scale=TTLocalizer.AClogoutButton,
            text_pos=(0, -0.035),
            image_scale=1,
            image1_scale=1.05,
            image2_scale=1.05,
            scale=0.7,
            command=self.__goBack
        )
        self.backButton.setPos(0, 1, -.75)
        self.backButton.show()
        self.uiItems.append(self.backButton)

    def __goBack(self):
        base.cr.mainmenu.request('Play')

    def destroy(self):
        if self.optionsMgr:
            try:
                self.optionsMgr.hideOptions(animate=False)
            except:
                try:
                    self.optionsMgr.delAllOptions()
                except:
                    pass
            self.optionsMgr = None
        MainMenuScreen.destroy(self)
