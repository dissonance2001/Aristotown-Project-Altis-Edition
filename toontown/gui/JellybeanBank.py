from toontown.toonbase import ToontownGlobals
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.gui.DirectGui import *

from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils.text import reduceNumberIntoString


@DirectNotifyCategory()
class JellybeanBank(DirectFrame):
    """
    Shows a rendered JellybeanBank on the screen.
    """
    jarGui = loader.loadModel('phase_3.5/models/gui/jar_gui')

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = kwargsToOptionDefs(
            relief=None,
            text=str(base.localAvatar.getMoney() if base.localAvatar else '0'),
            text_scale=0.18,
            text_fg=(0.95, 0.95, 0, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0, -0.1),
            text_font=ToontownGlobals.getSignFont(),
            image=self.jarGui.find('**/Jar'),
            money=None,
            reduceKwargs=None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # Define objects of this GUI.
        # self.bankDisplay = None

        # Load elements of this GUI.
        self.load()

        # Handle money override.
        money = self.cget('money')
        if money is not None:
            self.setMoney(money)
        elif base.localAvatar:
            # No money override, listen for moneyChange
            self.accept(base.localAvatar.uniqueName('moneyChange'), self.setMoney)

    """
    Loading methods
    """

    def load(self):
        return

    def destroy(self):
        self.ignoreAll()
        super().destroy()

    """
    Jellybean Bank Visual Adjustment
    """

    def updateToJarAndBank(self):
        if not base.localAvatar:
            return

        self.setTextNumerical(value=base.localAvatar.getMoney())

    def setTextNumerical(self, value: int = None):
        setTextFunc = self.setText
        # Reduce the kwargs if necessary.
        reduceKwargs = self.cget('reduceKwargs')
        if reduceKwargs is not None:
            # We set the text, but reduced.
            setTextFunc(reduceNumberIntoString(value, **reduceKwargs))
        else:
            # Just set the text.
            setTextFunc(str(value))

    def setMoney(self, money):
        self.setTextNumerical(money)

    def setToShowTotal(self):
        """
        Sets the Jellybean Jar to show
        the TOTAL amount of money the localAv has.
        """
        self.setTextNumerical(base.localAvatar.getTotalMoney() if base.localAvatar else 0)

    def makeTextColorRed(self):
        """
        Sets the text color to be red.
        """
        self['text_fg'] = (1, 0, 0, 1)
        self['text_shadow'] = (0, 0, 0, 0)
