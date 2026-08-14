from direct.gui.DirectGui import *
from toontown.menu.MainMenuScreen import MainMenuScreen
from toontown.menu.MainMenuGui import MainMenuButton
from toontown.dmenu import DMenuOptions


class MainMenuScreenOptions(MainMenuScreen):
    def __init__(self):
        self.optionsMgr = None
        self.backButton = None
        MainMenuScreen.__init__(self)

    def createUI(self):
        self.optionsMgr = DMenuOptions.DMenuOptions()
        self.optionsMgr.showOptions(animate=False)
        self.backButton = MainMenuButton(
            parent=base.a2dTopLeft,
            text='Back',
            pos=(.2, 0, -.1),
            command=lambda: base.cr.mainmenu.request('Play')
        )
        self.uiItems.append(self.backButton)

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
