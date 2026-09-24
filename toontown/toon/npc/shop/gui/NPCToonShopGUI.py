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
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toon.npc.shop.gui.NPCToonShopItemList import NPCToonShopItemList
from toontown.toon.npc.shop.gui.NPCToonShopItemPurchase import NPCToonShopItemPurchase
from toontown.toon.npc.shop.gui.NPCToonShopItem import NPCToonShopItem
from toontown.shop.cost.JellybeanPriceTag import JellybeanPriceTag

from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils import ColorHelper, Nodes
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from panda3d.core import *

from toontown.gui import TTDialog

from toontown.toon.npc.NPCToonConstants import NPCToonID
from toontown.toon.npc.shop import NPCToonShopGlobals
from toontown.toon.npc.shop.gui.NPCToonShopCategoryButton import NPCToonShopCategoryButton
from toontown.toonbase import ToontownTimer
from toontown.gui.GenericCloseButton import GenericCloseButton
from toontown.toonbase.MarginManagerCell import ScreenCellFlag


class NPCToonShopGUI(TilingScaledFrame, Bounds):
    """
    A shop interface for generic toon shops, including the general store and the Tell Tale Carp.
    """
    MaxShopItems = NPCToonShopGlobals.ShopItemsPerPage

    timerDuration = 240
    if __debug__:
        timerDuration = 69420

    @InjectorTarget
    def __init__(self, parent, npc, **kw):
        shopVisualDef = NPCToonShopGlobals.getNPCShopVisualDef(npc.npc_id)
        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            relief=None,
            frameSize=(-1.0, 1.0, -0.7, 0.7),

            # TilingScaledFrame attrs
            scaledTexture=shopVisualDef.scaledTexture,
            scaledColor=shopVisualDef.scaledColor,
            borderScale=shopVisualDef.borderScale,
            patternTexture=shopVisualDef.patternTexture,
            patternSpeed=shopVisualDef.patternSpeed,
            patternScale=shopVisualDef.patternScale,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(NPCToonShopGUI)
        self['shadowStrength'] = shopVisualDef.shadowStrength
        self.patternNode.setColorScale(shopVisualDef.patternColor)

        # Set state here.
        self.npc = npc
        self.itemCatalogue = NPCToonShopGlobals.getNPCItemCatalogue(npc.npc_id)
        self.currentCategory = list(self.itemCatalogue.itemCatalogue.keys())[0]
        self.currentPage = 0
        self.currentPriceTagType = None

        # Set GUI prototypes here.
        # Anchors
        self.anchor_left: CornerAnchor | None = None
        self.anchor_right: CornerAnchor | None = None
        self.anchor_bottom: CornerAnchor | None = None
        self.anchor_top: CornerAnchor | None = None
        self.anchor_top_right: CornerAnchor | None = None
        # Arrows
        self.arrow_left: EasyManagedButton | None = None
        self.arrow_right: EasyManagedButton | None = None
        # Main nodes and frames
        self.node_left: GUINode | None = None
        self.shop_list: NPCToonShopItemList | None = None
        self.node_right: GUINode | None = None
        self.shop_purchase: NPCToonShopItemPurchase | None = None
        self.node_arrows: GUINode | None = None
        self.label_page: TTGui.OnscreenTextOutline | None = None
        self.node_currency: GUINode | None = None
        self.element_currency = None
        self.button_close: GenericCloseButton | None = None
        self.button_upgrades: EasyManagedButton | None = None
        self.categoryButtons: list = []

        self.confirmDialog = None

        # Call these two.
        self.__create()
        self.place()

        self.accept('inventoryDelta', self.__gotInventoryDelta)
        self.accept('clearOutToonInterior', self.handleExit)

        if base.localAvatar:
            # Generate timer
            self.timer = ToontownTimer.ToontownTimer()
            self.timer.reparentTo(aspect2d)
            self.timer.posInTopRightCorner()
            self.timer.countdown(self.timerDuration, self.handleExit)

            # run wakeup calls to make sure the toon doesn't fall asleep
            self.keepAliveTaskName = self.uniqueName('keepAlive')
            self.__startKeepAlive()

            base.flagScreenCells(ScreenCellFlag.npcShop, [base.bottomCells[2], base.bottomCells[3]])

    def __create(self):
        self.anchor_left = CornerAnchor(parent=self, corner=ScreenCorner.LEFT_MIDDLE)
        self.anchor_right = CornerAnchor(parent=self, corner=ScreenCorner.RIGHT_MIDDLE)
        self.anchor_bottom = CornerAnchor(parent=self, corner=ScreenCorner.BOTTOM_MIDDLE)
        self.anchor_top = CornerAnchor(parent=self, corner=ScreenCorner.TOP_MIDDLE)
        self.anchor_top_right = CornerAnchor(parent=self, corner=ScreenCorner.TOP_RIGHT)

        self.node_left = GUINode(parent=self)
        self.shop_list = NPCToonShopItemList(
            parent=self.node_left,
            shopGui=self,
            pos=(0, 0, 0.075),
            shopItemList=self.getShopItems(),
        )

        self.node_right = GUINode(parent=self)
        self.shop_purchase = NPCToonShopItemPurchase(
            parent=self.node_right,
            shopGui=self,
            pos=(0, 0, 0.075),
        )

        self.node_arrows = GUINode(parent=self.node_left, pos=(0, 0, -0.625))

        arrowGui = loader.loadModel('phase_13/models/events/halloween/cc_m_gui_hw_shop_menu')

        self.arrow_left = EasyManagedButton(
            parent=self.node_arrows,
            relief=None,
            pos=(-0.3, 0, 0),
            scale=0.15,
            image=UiHelpers.generateButtonImages(arrowGui, prefix="shop_btn_note_1_", normal="up", pressed="down",
                                                 hover="rlvr", disable="down"),
            command=self.changePage,
            extraArgs=[-1],
        )
        self.arrow_right = EasyManagedButton(
            parent=self.node_arrows,
            relief=None,
            pos=(0.3, 0, 0),
            scale=0.15,
            image=UiHelpers.generateButtonImages(arrowGui, prefix="shop_btn_note_2_", normal="up", pressed="down",
                                                 hover="rlvr", disable="down"),
            command=self.changePage,
            extraArgs=[1],
        )

        arrowGui.removeNode()

        self.label_page = TTGui.OnscreenTextOutline(
            parent=self.node_arrows,
            pos=(0.0, -0.035),
            scale=0.1,
            text='1/1',
            align=TextNode.ACenter,
            text_dist=0.008,
            precision=12,
            outline_fg=(0, 0, 0, 1),
            fg=(1, 1, 1, 1),
        )

        self.node_currency = GUINode(parent=self.node_right, pos=(0, 0, -0.62), scale=0.35)

        for key in self.itemCatalogue.itemCatalogue.keys():
            if key == NPCToonShopGlobals.NPCShopCategory.Upgrades:
                # Don't show the upgrades category button, as it has a special button
                continue
            newButton = NPCToonShopCategoryButton(
                parent=self.anchor_top,
                relief=None,
                scale=0.12075,
                shopCategory=key,
                command=self.changeCategory,
                extraArgs=[key],
            )
            self.categoryButtons.append(newButton)
        UiHelpers.placeElementsInHorizontalLine(self.categoryButtons, startPos=(-0.84985, 0, -0.06917), scale=0.1)

        # Default to jellybean price tag
        self.element_currency = JellybeanPriceTag.getCostTypeOwnedDisplayGui(self.node_currency)
        self.button_close = GenericCloseButton(parent=self.anchor_top_right, command=self.handleExit, scale=1.55)

        sp_gui = loader.loadModel('phase_3.5/models/gui/socialpanel/social_panel')
        self.button_upgrades = EasyManagedButton(
            parent=self.node_left,
            relief=None,
            pos=(0.415, 0, -0.625),
            scale=0.28,
            geom=UiHelpers.generateButtonImages(sp_gui, "Button_Blank_", normal="N", hover="H", pressed="P"),
            geom_color=(0.5, 1.0, 0.5, 1.0),
            geom_scale=UiHelpers.calculateImageScale(195, 96),
            text='Upgrades',
            text_scale=0.2,
            text_pos=(0, -0.05),
            command=self.selectUpgrade,
        )
        sp_gui.removeNode()

    def place(self):
        if not self.postInitialized:
            return
        self.anchor_left.place()
        self.anchor_right.place()
        self.anchor_bottom.place()
        self.anchor_top.place()
        self.anchor_top_right.place()
        self.node_left.setPos(self['frameSize'][0] + (self.getBoundWidth()*.325), 0, 0)
        self.node_right.setPos(self['frameSize'][0] + (self.getBoundWidth()*.815), 0, 0)
        self.label_page['text'] = f'{self.currentPage+1}/{self.maxPageNumber+1}'

        if self.hasUpgradeAvailable:
            self.button_upgrades.show()
            self.node_arrows.setPos(-0.2, 0, -0.625)
        else:
            self.button_upgrades.hide()
            self.node_arrows.setPos(0, 0, -0.625)

    def __gotInventoryDelta(self, delta=None):
        self.place()

    def updatePage(self):
        self.place()
        self.shop_list.place()
        self.shop_purchase.place()

    def getShopItems(self):
        # Only return a max of 6 shop items at a given time
        allShopItems = self.itemCatalogue.getItemListing(self.currentCategory).getItems()[:]
        shopItemSelection = allShopItems[self.currentPage*self.MaxShopItems:max((self.currentPage+1)*self.MaxShopItems, len(allShopItems))]
        return shopItemSelection

    def changePage(self, value: int):
        self.updatePageNumber(min(max(self.currentPage + value, 0), self.maxPageNumber))

    def updatePageNumber(self, value: int):
        self.currentPage = value
        self.shop_list['shopItemList'] = self.getShopItems()
        self.label_page['text'] = f'{self.currentPage + 1}/{self.maxPageNumber + 1}'

    @property
    def maxPageNumber(self):
        shopItems = self.itemCatalogue.itemCatalogue[self.currentCategory].getItems()[:]
        if not len(shopItems):
            return 0
        return (len(shopItems) - 1) // self.MaxShopItems

    def changeCategory(self, value):
        if self.currentCategory == value:
            return
        self.currentCategory = value
        self.updatePageNumber(0)

    def clickedItem(self, item: NPCToonShopItem):
        if not item['shopItem']:
            return
        self.shop_purchase.configure(shopItem=item['shopItem'])

    def checkUpdateUserCurrency(self):
        if not self.postInitialized:
            return
        priceTagClass = self.shop_purchase['shopItem'].getPriceTags()[0].__class__
        if self.currentPriceTagType is priceTagClass:
            return
        if self.element_currency:
            self.element_currency.destroy()
        self.currentPriceTagType = priceTagClass
        self.element_currency = priceTagClass.getCostTypeOwnedDisplayGui(self.node_currency)

    def purchaseItem(self, item=None):
        if not item:
            return

        priceTag = item.getPriceTags()[0]
        ownedAmount = priceTag.getAvatarOwnedAmount(base.localAvatar) if base.localAvatar else 0
        text = TTLocalizer.NPCStorePurchase.format(
            name=item.getName(base.localAvatar),
            costType=priceTag.getLabelString(),
            costName=priceTag.getCostName(),
            amountOwned=priceTag.getLabelString(override=ownedAmount),
        )
        self.confirmDialog = TTDialog.TTDialog(
            parent=aspect2d,
            text=text,
            text_scale=0.06,
            text_align=TextNode.ACenter,
            text_wordwrap=25,
            command=self.confirmPurchase,
            style=TTDialog.YesNo,
            buttonPadSF=4)
        self.confirmDialog.show()

    def confirmPurchase(self, result):
        if not self.confirmDialog:
            return
        self.confirmDialog.destroy()
        self.confirmDialog = None
        item = self.shop_purchase['shopItem']
        if result == DGG.DIALOG_OK and item:
            self.npc.sendUpdate('requestItemPurchase', [item.toStruct()])

    def selectUpgrade(self):
        if not self.hasUpgradeAvailable:
            return

        firstUpgrade = self.getFirstUpgradeAvailable()
        self.shop_purchase['shopItem'] = firstUpgrade

    def getFirstUpgradeAvailable(self):
        upgrades = self.itemCatalogue.getItemListing(NPCToonShopGlobals.NPCShopCategory.Upgrades).getItems()[:]
        for i, upgrade in enumerate(upgrades):
            if not upgrade.ownsItem(base.localAvatar):
                return upgrade
            # We owned all of them, just return this upgrade as its the last one
            elif i == len(upgrades) - 1:
                return upgrade

    @property
    def hasUpgradeAvailable(self):
        if not base.localAvatar:
            return False
        if NPCToonShopGlobals.NPCShopCategory.Upgrades not in self.itemCatalogue.itemCatalogue.keys():
            return False
        availableUpgrades = [not shopItem.ownsItem(base.localAvatar) for shopItem in
                             self.itemCatalogue.getItemListing(NPCToonShopGlobals.NPCShopCategory.Upgrades).getItems()[:]]
        if not len(availableUpgrades):
            return False
        return any(availableUpgrades)

    def checkNeedNewUpgradeItem(self, shopItem):
        """
        After the purchase of an item, checks if we need to move the item to the next upgrade
        if it happens to be an upgrade item.
        """
        if NPCToonShopGlobals.NPCShopCategory.Upgrades not in self.itemCatalogue.itemCatalogue.keys():
            return False
        upgrades = self.itemCatalogue.getItemListing(NPCToonShopGlobals.NPCShopCategory.Upgrades).getItems()[:]
        if shopItem not in upgrades:
            return
        nextUpgrade = self.getFirstUpgradeAvailable()
        if shopItem is nextUpgrade:
            return
        self.shop_purchase['shopItem'] = nextUpgrade

    def handleExit(self):
        base.cr.playGame.getPlace().setState('walk')
        base.localAvatar.unlockControlsForEntry()
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
            self.timer.destroy()
            self.timer = None
        base.unflagScreenCells(ScreenCellFlag.npcShop, [base.bottomCells[2], base.bottomCells[3]])
        self.__endKeepAlive()
        self.ignoreAll()
        self.npc.doExit()
        self.destroy()

    def __startKeepAlive(self):
        taskMgr.add(self.__keepAlive, self.keepAliveTaskName, 30)

    def __endKeepAlive(self):
        taskMgr.remove(self.keepAliveTaskName)

    def __keepAlive(self, task):
        """Keeps the localAvatar awake while they are using this UI."""
        if hasattr(base, 'localAvatar') and base.localAvatar:
            base.localAvatar.wakeUp()
        task.delayTime = 30
        return task.again

    def destroy(self):
        self.npc = None
        self.itemCatalogue = None
        if self.confirmDialog:
            self.confirmDialog.destroy()
            self.confirmDialog = None
        super().destroy()


if __name__ == "__main__":
    # Lazy NPCToon
    class NPC:
        def __init__(self, npc_id):
            self.npc_id = npc_id

        def sendUpdate(self, *args):
            pass

        def doExit(self, *args):
            pass

    gui = NPCToonShopGUI(
        parent=aspect2d,
        npc=NPC(NPCToonID.EdgarAllanPole),
        # any kwargs go here
    )
    GUITemplateSliders(
        gui.categoryButtons[0],
        'pos', 'scale'
    )
    base.setBackgroundColor(0.7, 0.7, 0.7)
    base.run()
