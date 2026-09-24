from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.toonbase import ToontownGlobals
from toontown.gui.TTGui import kwargsToOptionDefs, OnscreenTextOutline
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.gui.DirectGui import *

from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils.text import reduceNumberIntoString


@DirectNotifyCategory()
class GumballBank(DirectFrame):
    """
    Shows a rendered Gumball bank on the screen.
    """

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        tex = loader.loadTexture('gui/common/maps/cc_t_gui_icon_gumball_1.png')
        tex.setMinfilter(Texture.FTLinearMipmapLinear)
        tex.setMagfilter(Texture.FTLinear)
        optiondefs = kwargsToOptionDefs(
            relief=None,
            image=tex,
            prefix='',
            money=None,
            reduceKwargs=None,
            update=False,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(GumballBank)
        self.component('image0').setTransparency(TransparencyAttrib.MAlpha)

        self.text = OnscreenTextOutline(
            parent=self, text_dist=0.02,
            pos=(0.0, -0.32928), scale=1.0,
            text=self.prefix + '0',
            fg=(242/255, 136/255, 165/255, 1.0),
            font=ToontownGlobals.getSignFont(),
        )

        # Handle money override.
        money = self.cget('money')
        if money is not None:
            self.setMoney(money)

        if self['update']:
            self.accept('gumballs-updated', self.updateGumballs)

    def destroy(self):
        super().destroy()
        self.ignoreAll()

    @property
    def prefix(self):
        return self['prefix']

    def setTextNumerical(self, value: int = None):
        # Reduce the kwargs if necessary.
        reduceKwargs = self.cget('reduceKwargs')
        if reduceKwargs is not None:
            # We set the text, but reduced.
            self.text['text'] = (self.prefix + reduceNumberIntoString(value, **reduceKwargs))
        else:
            # Just set the text.
            self.text['text'] = (self.prefix + str(value))

    def setMoney(self, money):
        self.setTextNumerical(money)

    def updateGumballs(self):
        if not base.localAvatar:
            return
        self.setMoney(base.localAvatar.getMoney(currencyType=MaterialItemType.Gumballs))
