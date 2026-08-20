from __future__ import absolute_import
from direct.showbase.DirectObject import DirectObject
from toontown.menu import MainMenu


class DMenuScreen(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        base.cr.DMENU_SCREEN = self
        self.mainmenu = MainMenu.MainMenu()
        base.cr.mainmenu = self.mainmenu

    def murder(self):
        if self.mainmenu:
            self.mainmenu.exitMenu()
            self.mainmenu = None
