from direct.showbase.MessengerGlobal import messenger

from toontown.club.ClubIconGUI import ClubIconGUI

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from toontown.gui import TTGui
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.EasyManagedItem import EasyManagedItem

from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from toontown.utils.InjectorHelper import *


class PicnicGameArrowButton(EasyManagedItem):
    """
    An arrow button which is placed next to a conditional frame.
    """

    @InjectorTarget
    def __init__(self, parent, buttonEvent: str, buttonArgs: list, **kw):
        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),  # controlled by Dad
            scale=1.0,
            frameSize=(-0.5, 0.5, -0.5, 0.5),
            relief=None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(PicnicGameArrowButton)

        self.button = DirectButton(
            self, relief=None,
            geom=ClubIconGUI.getThatSillyArrow(),
            geom_scale=(1, 1, 0.7),
            geom_hpr=(0, 0, -90),
            geom_color=(1, 1, 1, 1),
            command=messenger.send,
            extraArgs=[buttonEvent, buttonArgs]
        )

        self.__seq: Sequence | None = None

    def destroy(self):
        self.finishSequence()

        self.button.destroy()
        self.button = None

        super().destroy()

    def finishSequence(self) -> None:
        if self.__seq is not None:
            self.__seq.finish()
            self.__seq = None

    def startColorLoop(self, color: tuple[int]) -> None:
        self.finishSequence()

        self.__seq = Sequence(
            LerpColorScaleInterval(self, 1, color, blendType='easeInOut'),
            LerpColorScaleInterval(self, 1, (1, 1, 1, 1), blendType='easeInOut'),
        )
        self.__seq.loop()


if __name__ == "__main__":
    gui = PicnicGameArrowButton(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        gui,
        'pos', 'scale'
    )
    base.run()
