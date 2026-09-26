from toontown.gui.EasyManagedItem import EasyManagedItem

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from toontown.gui.game.condition.ConditionGlobals import ConditionArgs, ConditionArg, ConditionSide

from toontown.gui import TTGui
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.CornerAnchor import CornerAnchor
from toontown.gui.Bounds import Bounds
from toontown.gui.GUIPositionGlobals import ScreenCorner
from toontown.toon.gui import GuiBinGlobals

from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *


class ConditionSubframeBase(EasyManagedItem):
    """
    A ConditionSubframe is a small frame that contains a kind of player-relevant data
    that sits to the right of Laff Meters on the on-screen GUI.

    For example, player name lives in a NameConditionSubframe, or XP bar lives in a XPConditionSubframe.
    """

    requiredConditionalDataArgs: list[ConditionArg] = []

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos = (0, 0, 0),
            scale = 1.0,
            relief = None,

            easyWidth=1.0,
            easyHeight=-0.1,
            extraDist=0.0,

            conditionArgs = ConditionArgs(),
            side=ConditionSide.LEFT,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(ConditionSubframeBase)
        self.setBin('sorted-gui-popup', GuiBinGlobals.ConditionSubframe)

        # The corner is reset below.
        self.anchor: CornerAnchor = CornerAnchor(parent=self, corner=ScreenCorner.LEFT_MIDDLE)

    def place(self):
        if not self.postInitialized:
            return

        # Set anchor (this call auto-places it too)
        self['frameSize'] = (-self['easyWidth'], 0, self['easyHeight'], 0) if (self.side != ConditionSide.LEFT) else (0, self['easyWidth'], self['easyHeight'], 0)
        self.anchor['corner'] = ScreenCorner.LEFT_MIDDLE if (self.side == ConditionSide.LEFT) else ScreenCorner.RIGHT_MIDDLE

    def setDistance(self, amount: float):
        l, r, d, u = self.getDefinedBounds()
        if self.side == ConditionSide.LEFT:
            self['frameSize'] = (l, amount, d, u)
        else:
            self['frameSize'] = (amount, r, d, u)

    @property
    def height(self) -> float:
        l, r, d, u = self.getDefinedBounds()
        return u - d

    @property
    def conditionArgs(self) -> ConditionArgs:
        return self['conditionArgs']

    @property
    def corner(self) -> ScreenCorner:
        return self['corner']

    @property
    def side(self) -> ConditionSide:
        return self['side']

    @property
    def extraDist(self) -> float:
        return self['extraDist']

    @classmethod
    def validateArgs(cls, data: ConditionArgs) -> bool:
        for arg in cls.requiredConditionalDataArgs:
            if arg not in data:
                return False
        return True


if __name__ == "__main__":
    gui = ConditionSubframeBase(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        gui,
        'pos', 'scale'
    )
    base.run()
