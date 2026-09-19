if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()
    # base.initTalkAssistant()

from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class TrackStarGUI(DirectFrame):
    """
    A prestige star.
    """

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        gagSelectGui = loader.loadModel('phase_3.5/models/gui/battlegui/gag_selection_panels')
        prestigeStarFilled = gagSelectGui.find('**/prestige_star')
        prestigeStarEmpty = gagSelectGui.find('**/prestige_star_empty')
        optiondefs = kwargsToOptionDefs(
            pos = (0, 0, 0),
            scale = 1.0,
            relief = None,
            image=prestigeStarEmpty,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        self.prestigeStar = DirectFrame(
            parent=self, relief=None,
            pos=(0, 0, 0),
            scale=1.06, image=prestigeStarFilled,
        )
        self.prestigeStar.hide()
        gagSelectGui.removeNode()

    def setStar(self, mode: bool):
        if mode:
            self.prestigeStar.show()
        else:
            self.prestigeStar.hide()


if __name__ == "__main__":
    gui = TrackStarGUI(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        guiAffected=gui,
        guiKeys=('pos', 'scale'),
    )
    base.run()
