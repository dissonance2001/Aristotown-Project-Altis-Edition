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
from toontown.gui.GUINode import GUINode
from toontown.gui.CornerAnchor import CornerAnchor
from toontown.gui import UiHelpers
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.gui.EasyManagedButton import EasyManagedButton
from toontown.gui.EasyScrolledFrame import EasyScrolledFrame
from toontown.gui.Bounds import Bounds
from toontown.gui.GUIPositionGlobals import ScreenCorner
from toontown.gui.ScaledFrame import ScaledFrame
from toontown.gui.TilingScaledFrame import TilingScaledFrame
from toontown.gui.UiLerper import UILerper
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import ToontownGlobals
from toontown.utils.text import getTextScaleAfterLength

from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils import ColorHelper, Nodes
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from panda3d.core import *


class NPCToonShopItem(DirectButton, Bounds):
    """
    A single shop item within a NPCToonShopGUI interface.
    """

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            relief=None,

            shopItem=[None, self.place],
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(NPCToonShopItem)

        # Set state here.
        self.__itemUpdateMessage = None

        # Set GUI prototypes here.
        self.button: EasyManagedButton | None = None
        self.model: NodePath | None = None
        self.ival: MetaInterval | None = None
        self.label_purchased: DirectLabel | None = None

        # Call these two.
        self.__create()
        self.place()

    def __create(self):
        self.button = EasyManagedButton(
            parent=self,
            relief=None,
            frameSize=(-0.3, 0.3, -0.3, 0.3),
            text_scale=0.1,
            text_fg=(0, 0, 0, 1),
            textMayChange=1,
        )
        # Also used to indicate "can't afford" label
        self.label_purchased = DirectLabel(
            parent=self,
            relief=None,
            text='Purchased',
            text_scale=0.075,
            text_fg=(0.45, 0, 0, 1),
            text_pos=(-0.15, 0.15),
            text_align=TextNode.ACenter,
        )
        self.label_purchased.setBin('sorted-gui-popup', GuiBinGlobals.NPCToonShopPurchaseTextBin)
        self.label_purchased.hide()

    def place(self):
        if not self.postInitialized:
            return
        if self.ival:
            self.ival.finish()
            self.ival = None
        if self.model:
            self.model.removeNode()
            self.model = None
        self.button['geom'] = None
        self.button['text'] = None
        self.label_purchased.hide()

        if self.__itemUpdateMessage:
            self.ignore(self.__itemUpdateMessage)

        if not self['shopItem']:
            return

        self.__itemUpdateMessage = self['shopItem'].getLocalAvUpdateMessage()
        self.accept(self.__itemUpdateMessage, self.__gotItemUpdate)

        itemModel = self['shopItem'].getGuiItemModel()
        self.model = NodePath('item-holder')
        itemModel.reparentTo(self.model)
        self.button['geom'] = self.model
        self.button['geom_scale'] = 2.25
        self.button['geom_color'] = (1, 1, 1, 1)
        self.button['text'] = self['shopItem'].getPriceTags()[0].getLabelString(av=base.localAvatar)
        self.button['text_scale'] = 0.15
        self.button['text_pos'] = (0, -0.3)

        purchaseReqsNotMet = base.localAvatar and not self['shopItem'].purchaseReqsPass(base.localAvatar)
        avOwnsItem = base.localAvatar and self['shopItem'].ownsItem(base.localAvatar)
        cantAfford = base.localAvatar and not self['shopItem'].canAfford(base.localAvatar)

        if avOwnsItem:
            self.label_purchased['text'] = 'Purchased'
            self.label_purchased['text_fg'] = (0, 0.45, 0, 1)
            self.label_purchased.show()
            self.button['text'] = None
            self.button['geom_color'] = (0.75, 0.75, 0.75, 1.0)
        elif purchaseReqsNotMet:
            self.label_purchased['text'] = self['shopItem'].getPurchaseReqs()[0].getRequirementText()
            self.label_purchased['text_fg'] = (0, 0, 0.45, 1)
            self.label_purchased.show()
            self.button['geom_color'] = (0.75, 0.75, 0.75, 1.0)
        elif cantAfford:
            self.label_purchased['text'] = "Can't Afford"
            self.label_purchased['text_fg'] = (0.45, 0, 0, 1)
            self.label_purchased.show()
            self.button['geom_color'] = (0.75, 0.75, 0.75, 1.0)
        else:
            self.label_purchased.hide()

    def setItemButtonCommand(self, command, extraArgs=None):
        self.button['command'] = command
        self.button['extraArgs'] = extraArgs or []

    def __gotItemUpdate(self, *args, **kwargs):
        self.place()

    def destroy(self):
        self.ignoreAll()
        super().destroy()


if __name__ == "__main__":
    gui = NPCToonShopItem(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        gui,
        'pos', 'scale'
    )
    base.run()
