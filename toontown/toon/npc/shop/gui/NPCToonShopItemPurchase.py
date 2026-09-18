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
from toontown.utils.text import fitLabelTextToBounds
from toontown.gui.hover.HoverFrameTypes import HoverFrameTypes

from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils import ColorHelper, Nodes
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from panda3d.core import *

from enum import Enum, auto


class BuyButtonHoverState(Enum):
    Standard = auto()
    CantAfford = auto()
    FailedReqs = auto()


class NPCToonShopItemPurchase(ScaledFrame, Bounds):
    """
    The frame for when you click on an item and are viewing it on the right pane.
    """

    @InjectorTarget
    def __init__(self, parent, shopGui, **kw):
        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            frameSize=(-0.275, 0.275, -0.55, 0.425),
            borderScale=0.045,

            shopItem=[None, self.place],
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(NPCToonShopItemPurchase)

        self.shopGui = shopGui

        # Set state here.
        self.__itemUpdateMessage = None
        self.__buyButtonHoverState = BuyButtonHoverState.Standard

        # Set GUI prototypes here.
        self.anchor_top: CornerAnchor | None = None
        self.anchor_bottom_right: CornerAnchor | None = None
        self.anchor_bottom_left: CornerAnchor | None = None
        self.label_name: DirectLabel | None = None
        self.label_desc: DirectLabel | None = None
        self.frame_model: ScaledFrame | None = None
        self.model_node: GUINode | None = None
        self.model: NodePath | None = None
        self.button_purchase: EasyManagedButton | None = None
        self.node_currency: GUINode | None = None
        self.element_currency = None
        self.label_purchased: DirectLabel | None = None
        self.frame_purchaseHover: DirectFrame | None = None

        # Call these two.
        self.__create()
        self.place()

    def __create(self):
        self.anchor_top = CornerAnchor(parent=self, corner=ScreenCorner.TOP_MIDDLE)
        self.anchor_bottom_right = CornerAnchor(parent=self, corner=ScreenCorner.BOTTOM_RIGHT)
        self.anchor_bottom_left = CornerAnchor(parent=self, corner=ScreenCorner.BOTTOM_LEFT)
        self.label_name = DirectLabel(
            parent=self.anchor_top,
            relief=None,
            pos=(0, 0, -0.075),
            scale=1,
            text_fg=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
            text_wordwrap=12,
        )
        self.label_desc = DirectLabel(
            parent=self.anchor_top,
            relief=None,
            pos=(0, 0, -0.98),
            scale=1,
            text_fg=(0, 0, 0, 1),
            text_align=TextNode.ACenter,
            text_wordwrap=12,
        )
        self.frame_model = ScaledFrame(
            parent=self.anchor_top,
            relief=None,
            pos=(0, 0, -0.25),
            frameSize=(-0.2, 0.2, -0.2, 0.2),
        )
        self.model_node = GUINode(parent=self.frame_model)
        sp_gui = loader.loadModel('phase_3.5/models/gui/socialpanel/social_panel')
        self.button_purchase = EasyManagedButton(
            parent=self.anchor_bottom_right,
            relief=None,
            pos=(-0.08, 0, 0.08),
            scale=0.15,
            geom=UiHelpers.generateButtonImages(sp_gui, "Button_Blank_", normal="N", hover="H", pressed="P"),
            geom_color=(0.5, 1.0, 0.5, 1.0),
            text='Buy',
            text_scale=0.35,
            text_pos=(0, -0.1),
            command=self.purchaseItem,
        )
        sp_gui.removeNode()

        self.node_currency = GUINode(parent=self.anchor_bottom_left, pos=(0.15, 0, 0.1), scale=0.35)
        self.label_purchased = DirectLabel(
            parent=self.anchor_top,
            relief=None,
            pos=(0, 0, -0.925),
            text_scale=0.075,
            text='Purchased',
            text_fg=(0, 0.45, 0, 1),
        )
        self.label_purchased.hide()
        self.frame_purchaseHover = DirectFrame(
            parent=self.anchor_bottom_right,
            relief=None,
            frameSize=(-0.6, 0.6, -0.6, 0.6),
            pos=(-0.08, 0, 0.08),
            scale=0.15,
        )
        self.frame_purchaseHover.bind(DGG.WITHIN, self.__hoverPurchaseButton)
        self.frame_purchaseHover.bind(DGG.WITHOUT, self.__exitHoverPurchaseButton)
        self.frame_purchaseHover['state'] = DGG.NORMAL
        self.frame_purchaseHover.hide()

    def place(self):
        if not self.postInitialized:
            return
        self.anchor_top.place()
        self.anchor_bottom_right.place()
        self.anchor_bottom_left.place()
        if self.model:
            self.model.removeNode()
            self.model = None
        self.frame_model['image'] = None
        self.frame_model.hide()
        self.button_purchase.hide()
        self.frame_purchaseHover.hide()
        self.__buyButtonHoverState = BuyButtonHoverState.Standard

        if self.element_currency:
            self.element_currency.destroy()
            self.element_currency = None

        if self.__itemUpdateMessage:
            self.ignore(self.__itemUpdateMessage)

        if self['shopItem']:
            self.__itemUpdateMessage = self['shopItem'].getLocalAvUpdateMessage()
            self.accept(self.__itemUpdateMessage, self.__gotItemUpdate)
            # Item title
            self.label_name['text'] = self['shopItem'].getName(base.localAvatar)
            fitLabelTextToBounds(0.5, 0.08, self.label_name, 'text0', maxLines=1)
            # Item desc
            self.label_desc['text'] = self['shopItem'].getDescription(base.localAvatar)
            fitLabelTextToBounds(0.5, 0.24, self.label_desc, 'text0', keepTopOfTextAligned=True, maxScale=0.05)

            itemModel = self['shopItem'].getGuiItemModel()
            self.model = NodePath('frame-holder')
            itemModel.reparentTo(self.model)
            self.model.setScale(1.8)
            self.model.reparentTo(self.model_node)
            self.frame_model.show()
            self.shopGui.checkUpdateUserCurrency()

            if base.localAvatar and self['shopItem'].ownsItem(base.localAvatar):
                # Can't buy more of the item
                self.label_purchased.show()
                self.button_purchase.hide()
            else:
                # Can buy more of the item
                # Update price tag frame
                priceTag = self['shopItem'].getPriceTags()[0]
                self.element_currency = priceTag.getPriceTagGui(base.localAvatar, self.node_currency, amount=priceTag.getCost())
                self.label_purchased.hide()

                if base.localAvatar and not self['shopItem'].purchaseReqsPass(base.localAvatar):
                    self.button_purchase['state'] = DGG.DISABLED
                    self.button_purchase.setColorScale(0.5, 0.5, 0.5, 1.0)
                    self.frame_purchaseHover.show()
                    self.__buyButtonHoverState = BuyButtonHoverState.FailedReqs
                elif base.localAvatar and not priceTag.canAfford(base.localAvatar):
                    self.button_purchase['state'] = DGG.DISABLED
                    self.button_purchase.setColorScale(0.5, 0.5, 0.5, 1.0)
                    self.frame_purchaseHover.show()
                    self.__buyButtonHoverState = BuyButtonHoverState.CantAfford
                else:
                    self.button_purchase['state'] = DGG.NORMAL
                    self.button_purchase.setColorScale(1, 1, 1, 1)
                self.button_purchase.show()

    def purchaseItem(self):
        self.shopGui.purchaseItem(self['shopItem'])

    def __gotItemUpdate(self, *args, **kwargs):
        self.place()
        if self.shopGui:
            self.shopGui.checkNeedNewUpgradeItem(self['shopItem'])

    def __hoverPurchaseButton(self, _=None):
        if self.__buyButtonHoverState == BuyButtonHoverState.Standard:
            # No hover for standard (able to purchase)
            return
        elif self.__buyButtonHoverState == BuyButtonHoverState.CantAfford:
            base.hoverMgr.hoverObject(self.frame_purchaseHover, item=self['shopItem'],
                                      itemType=HoverFrameTypes.ShopBuyCantAfford, frameDir='right',
                                      frameScale=0.8, fitToTextWidth=True)
        else:
            base.hoverMgr.hoverObject(self.frame_purchaseHover, item=self['shopItem'],
                                      itemType=HoverFrameTypes.ShopBuyFailedReq, frameDir='right',
                                      frameScale=0.8, fitToTextWidth=True)

    def __exitHoverPurchaseButton(self, _=None):
        base.hoverMgr.unhoverObject()

    def destroy(self):
        self.shopGui = None
        self.ignoreAll()
        super().destroy()


if __name__ == "__main__":
    gui = NPCToonShopItemPurchase(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        gui,
        'pos', 'scale'
    )
    base.run()
