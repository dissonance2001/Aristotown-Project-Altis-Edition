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
from toontown.toon.npc.shop.gui.NPCToonShopItem import NPCToonShopItem
from toontown.toon.npc.shop import NPCToonShopGlobals

from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils import ColorHelper, Nodes
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from panda3d.core import *


class NPCToonShopItemList(ScaledFrame, Bounds):
    """
    A grid of items that can be bought in a shop
    """
    MaxShopItems = NPCToonShopGlobals.ShopItemsPerPage
    ShopItemPos = [
        # Top left
        (-0.35, 0, -0.0625 + (0.4875*.66)),
        # Top mid
        (0, 0, -0.0625 + (0.4875*.66)),
        # Top right
        (0.35, 0, -0.0625 + (0.4875 * .66)),
        # Mid left
        (-0.35, 0, -0.0625),
        # Mid mid
        (0, 0, -0.0625),
        # Mid right
        (0.35, 0, -0.0625),
        # Bottom left
        (-0.35, 0, -0.0625 + (-0.4875 * .66)),
        # Bottom mid
        (0, 0, -0.0625 + (-0.4875 * .66)),
        # Bottom right
        (0.35, 0, -0.0625 + (-0.4875 * .66)),
    ]

    @InjectorTarget
    def __init__(self, parent, shopGui, **kw):
        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),
            relief=None,
            scale=1.0,
            frameSize=(-0.55, 0.55, -0.55, 0.425),
            borderScale=0.045,

            shopItemList=[[], self.place],
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(NPCToonShopItemList)

        self.shopGui = shopGui

        # Set GUI prototypes here.
        self.item_frames = []

        # Call these two.
        self.__create()
        self.place()

    def __create(self):
        for i in range(self.MaxShopItems):
            itemFrame = NPCToonShopItem(
                parent=self,
                shopItem=None,
                scale=0.35,
                pos=self.ShopItemPos[i]
            )
            itemFrame.setItemButtonCommand(command=self.shopGui.clickedItem, extraArgs=[itemFrame])
            self.item_frames.append(itemFrame)

    def place(self):
        if not self.postInitialized:
            return
        for i in range(self.MaxShopItems):
            if i < len(self['shopItemList']):
                self.item_frames[i]['shopItem'] = self['shopItemList'][i]
            else:
                self.item_frames[i]['shopItem'] = None

    def destroy(self):
        self.shopGui = None
        super().destroy()


if __name__ == "__main__":
    gui = NPCToonShopItemList(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        gui,
        'pos', 'scale'
    )
    base.run()
