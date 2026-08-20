from __future__ import absolute_import
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGui import DGG


class MainMenuScreen(DirectFrame):
    def __init__(self):
        DirectFrame.__init__(self)
        self.uiItems = []
        self.createUI()

    def createUI(self):
        pass

    def destroy(self):
        for item in self.uiItems:
            if item:
                if isinstance(item, DirectButton):
                    item.unbind(DGG.ENTER)
                    item.unbind(DGG.EXIT)
                item.destroy()
        self.uiItems = []
        DirectFrame.destroy(self)

    def enterDisplay(self):
        pass

    def exitDisplay(self):
        pass
