if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase()
    base.initCR()
    base.generateLocalAvatar()

from typing import List, Optional

from direct.gui.DirectGuiGlobals import NO_FADE_SORT_INDEX
from panda3d.core import *
from otp import *
from toontown.crafting import CraftingGlobals
from toontown.gui import TTDialog
from toontown.gui.TTDialog import *
from toontown.toonbase import ToontownTimer
from toontown.events.halloween.HalloweenStoreItems import HalloweenShopItems
from toontown.crafting.CraftingGlobals import HalloweenMaterial
from toontown.shop.base.ShopItemListing import ShopItemListing
from toontown.shop.cost.HalloweenPriceTag import HalloweenPriceTag
from toontown.shop.item.InventoryShopItem import InventoryShopItem
from toontown.toonbase.MarginManagerCell import ScreenCellFlag


class HalloweenStoreGUI(DirectFrame):
    """
    The GUI used for the Halloween store shop.
    """

    timerDuration = 240
    if __debug__:
        timerDuration = 69420

    def __init__(self, npcWitch, *args, **kwargs):
        """
        :param DistributedNPCElphabat npcWitch: Distributed Witch NPC
        """
        opts = {
            'relief': None,
            'scale': 1.6
        }
        opts.update(kwargs)
        DirectFrame.__init__(self, *args, **opts)
        self.gui = loader.loadModel('phase_13/models/events/halloween/cc_m_gui_hw_shop_menu')
        self['geom'] = self.gui.find('**/shop_menu')
        self.npcWitch = npcWitch
        self.createGui()

        # Generate timer
        self.timer = ToontownTimer.ToontownTimer()
        self.timer.reparentTo(aspect2d)
        self.timer.posInTopRightCorner()
        self.timer.countdown(self.timerDuration, self.__handleExit)

        # run wakeup calls to make sure the toon doesn't fall asleep
        self.keepAliveTaskName = self.uniqueName('keepAlive')
        self.__startKeepAlive()

    def __keepAlive(self, task):
        """Keeps the localAvatar awake while they are using this UI."""
        if hasattr(base, 'localAvatar') and base.localAvatar:
            base.localAvatar.wakeUp()
        task.delayTime = 30
        return task.again

    def __startKeepAlive(self):
        taskMgr.add(self.__keepAlive, self.keepAliveTaskName, 30)

    def __endKeepAlive(self):
        taskMgr.remove(self.keepAliveTaskName)

    def createGui(self):
        buttons = loader.loadModel('phase_3/models/gui/ttcc_gui_generalButtons')
        materialIcons = loader.loadModel("phase_3.5/models/gui/material_icons")

        self.pageIndex = 0
        self.itemBoxes = {}

        self.closeStoreButton = DirectButton(self,
                                             image=(buttons.find('**/CloseBtn_UP'),
                                                    buttons.find('**/CloseBtn_DN'),
                                                    buttons.find('**/CloseBtn_Rllvr')),
                                             image_scale=1,
                                             scale=1,
                                             pos=(LPoint3f(-0.423613, 0, 0.439236)),
                                             relief=None,
                                             command=self.__handleExit)
        self.nextPageButton = DirectButton(self,
                                           relief=None,
                                           scale=0.6,
                                           pos=(LPoint3f(0.409, 0, -0.454861)),
                                           image=[self.gui.find('**/shop_btn_note_2_up'),
                                                  self.gui.find('**/shop_btn_note_2_down'),
                                                  self.gui.find('**/shop_btn_note_2_rlvr'),
                                                  self.gui.find('**/shop_btn_note_2_up')],
                                           image_color=(0.9, 0.9, 0.9, 1),
                                           image_scale=(0.125, 0.125, 0.125),
                                           image2_color=(1, 1, 1, 1),
                                           command=self.__handleNext)
        self.previousPageButton = DirectButton(self,
                                               relief=None,
                                               scale=0.6,
                                               pos=(LPoint3f(-0.145, 0, -0.454861)),
                                               image=[self.gui.find('**/shop_btn_note_1_up'),
                                                      self.gui.find('**/shop_btn_note_1_down'),
                                                      self.gui.find('**/shop_btn_note_1_rlvr'),
                                                      self.gui.find('**/shop_btn_note_1_up')],
                                               image_color=(0.9, 0.9, 0.9, 1),
                                               image_scale=(0.125, 0.125, 0.125),
                                               image2_color=(1, 1, 1, 1),
                                               command=self.__handlePrevious)
        self.icons = []
        self.underneathFrame = DirectFrame(parent=self, pos=(0.02, 0.0, -0.47))
        self.searchBar = DirectEntry(parent=self.underneathFrame,
                                     initialText='1',
                                     text_align=TextNode.ACenter,
                                     text_fg=(1, 1, 1, 1),
                                     relief=None,
                                     scale=0.05,
                                     pos=(0.1, 0.0, 0.0),
                                     width=1.5,
                                     numLines=1,
                                     focus=0,
                                     cursorKeys=1,
                                     command=self.finishSearch)
        self.maxPages = len(HalloweenShopItems.getAllCategories()) - 1
        self.searchText = DirectLabel(parent=self.underneathFrame,
                                      relief=None,
                                      text=TTLocalizer.CatalogPagePrefix + '       /',
                                      text_align=TextNode.ALeft,
                                      text_fg=(1, 1, 1, 1),
                                      scale=0.05,
                                      pos=(-0.06, 0, 0))
        self.underline = DirectLabel(parent=self.underneathFrame,
                                     relief=None,
                                     text='___',
                                     text_align=TextNode.ACenter,
                                     text_fg=(1, 1, 1, 1),
                                     scale=0.05,
                                     pos=(0.1, 0.0, 0))
        self.maxText = DirectLabel(parent=self.underneathFrame,
                                   relief=None,
                                   text=str(self.maxPages+1),
                                   scale=0.05,
                                   text_align=TextNode.ACenter,
                                   text_fg=(1, 1, 1, 1),
                                   pos=(0.225, 0, 0))
        self.searchBar.flattenMedium()
        self.searchBar.setTransparency(1)
        self.searchBar.bind(DGG.B1PRESS, self.updateSearch)
        self.pageFlashIval = None
        self.startPageFlashIval()

        # Display the total amount of materials the player has on the left side.
        offset = 0
        av = base.localAvatar
        for iconIndex in range(CraftingGlobals.TOTAL_CRAFT_MATERIALS):
            iconGeom = materialIcons.find('**/' + CraftingGlobals.MaterialIconNames[iconIndex])
            if av:
                amount = av.getCraftMaterial(iconIndex)
            else:
                amount = 0
            iconFrame = DirectFrame(parent=self,
                                    relief=None,
                                    geom=iconGeom,
                                    pos=(-0.39, 0, 0.21 + offset),
                                    geom_scale=0.325,
                                    text='x' + str(amount),
                                    text_scale=0.05,
                                    text_align=TextNode.ALeft,
                                    text_pos=(0.025, -0.015, 0))

            offset -= 0.04
            self.icons.append(iconFrame)

        # Create slots to preview the shop items
        itemSlots = [
            (-0.03, 0, 0.375),   # top left
            (-0.03, 0, -0.035),  # middle left
            (-0.03, 0, -0.44),  # bottom left

            (0.46, 0, 0.375),  # top right
            (0.46, 0, -0.035),   # middle right
            (0.46, 0, -0.44),   # bottom right
        ]
        itemIndex = 0
        for itemSlot in itemSlots:
            item = StoreItem(itemSlot, self.npcWitch, self)
            self.itemBoxes[itemIndex] = item
            itemIndex += 1

        self.disableArrows()
        self.updatePage()

        base.flagScreenCells(ScreenCellFlag.halloweenShop, [base.bottomCells[2], base.bottomCells[3]])
        self.accept('attemptWitchPurchase', self.__changeAllButtonStates)
        self.accept(base.MAP_PAGE_HOTKEY, self.__handleExit)
        self.accept('setDeliverySchedule-%s' % base.localAvatar.doId, self.updatePage)

    def updateMaterialAmounts(self):
        av = base.localAvatar
        for icon in self.icons:
            icon['text'] = 'x' + str(av.getCraftMaterial(self.icons.index(icon)))

    def __handleExit(self):
        messenger.send('halloweenStoreCleanupDialogue')
        base.cr.playGame.getPlace().setState('Walk')
        base.localAvatar.unlockControlsForEntry()
        for panel in list(self.itemBoxes.keys()):
            self.itemBoxes[panel].destroy()
            del self.itemBoxes[panel]
        if hasattr(self, 'timer') and self.timer:
            self.timer.stop()
            self.timer.destroy()
            self.timer = None
        base.unflagScreenCells(ScreenCellFlag.halloweenShop, [base.bottomCells[2], base.bottomCells[3]])
        self.stopPageFlashIval()
        self.__endKeepAlive()
        self.ignoreAll()
        self.destroy()
        self.npcWitch.doExit()
        del self.npcWitch

    def disableArrows(self):
        if self.pageIndex <= 0:
            self.pageIndex = 0
            self.previousPageButton['state'] = DGG.DISABLED
            self.previousPageButton.hide()
        else:
            self.previousPageButton['state'] = DGG.NORMAL
            self.previousPageButton.show()

        if self.pageIndex >= self.maxPages:
            self.pageIndex = self.maxPages
            self.nextPageButton['state'] = DGG.DISABLED
            self.nextPageButton.hide()
        else:
            self.nextPageButton['state'] = DGG.NORMAL
            self.nextPageButton.show()

    def __handleNext(self):
        self.pageIndex += 1
        self.disableArrows()
        self.updatePage()

    def __handlePrevious(self):
        self.pageIndex -= 1
        self.disableArrows()
        self.updatePage()

    def updateSearch(self, temp):
        base.localAvatar.lockControlsForEntry()
        self.stopPageFlashIval()
        self.searchBar.set('')

    def finishSearch(self, temp=None):
        self.searchBar['focus'] = 0  # Unfocus the search bar just in case it is focused when we are entering
        base.localAvatar.unlockControlsForEntry()
        page = self.searchBar.get()
        try:
            self.pageIndex = int(page) - 1
            self.disableArrows()
            self.searchBar.set(str(self.pageIndex + 1))
            self.updatePage()
        except (ValueError, TypeError):
            self.searchBar.set(str(self.pageIndex + 1))

    def __changeAllButtonStates(self, enable=True):
        if enable:
            self.closeStoreButton['state'] = DGG.NORMAL
            self.searchBar['state'] = DGG.NORMAL
            self.disableArrows()
            self.updatePage()
        else:
            self.closeStoreButton['state'] = DGG.DISABLED
            self.nextPageButton['state'] = DGG.DISABLED
            self.searchBar['state'] = DGG.DISABLED
            self.closeStoreButton['state'] = DGG.NORMAL
            for itemFrame in list(self.itemBoxes.values()):
                itemFrame.buyButton['state'] = DGG.DISABLED
                itemFrame.nextItemButton['state'] = DGG.DISABLED
                itemFrame.previousItemButton['state'] = DGG.DISABLED

    def updatePage(self):
        items: ShopItemListing = HalloweenShopItems.getItemListing(category=self.pageIndex)
        self.searchBar.set(str(self.pageIndex + 1))
        for panel in list(self.itemBoxes.keys()):
            self.itemBoxes[panel].clearBox(True)

        for boxIndex, itemGroup in enumerate(items.getItems()):
            # bad hacks bc this gui code is bad...
            itemList: List[InventoryShopItem] = [itemGroup] if not isinstance(itemGroup, list) else itemGroup
            currentItem: InventoryShopItem = itemGroup if not isinstance(itemGroup, list) else itemGroup[0]

            # get the pricetag mat
            pricetag: HalloweenPriceTag = currentItem.getPriceTags()[0]
            itemMaterial: HalloweenMaterial = pricetag.getMaterialType()
            itemCost: int = pricetag.getCost()

            if itemMaterial == CraftingGlobals.CRAFT_MAT_ALL:
                hasEnough = all([base.localAvatar.getCraftMaterial(material) >= itemCost for material in HalloweenMaterial])
            else:
                hasEnough = base.localAvatar.getCraftMaterial(itemMaterial) >= itemCost

            # clear and update
            itemBox = self.itemBoxes[boxIndex]
            itemBox.clearBox()
            self.updateMaterialAmounts()
            itemBox.updatePanel(
                currentItem,
                itemMaterial,
                hasEnough,
                itemCost=itemCost,
                itemList=itemList,
            )

    def startPageFlashIval(self):
        self.stopPageFlashIval()

        def setPageColor(color):
            self.searchBar['image_color'] = color

        self.pageFlashIval = Sequence(
            LerpFunctionInterval(setPageColor, 2, Vec4(1.0, 1.0, 1.0, 1.0), Vec4(1.0, 0.9, 0.4, 1.0)),
            LerpFunctionInterval(setPageColor, 2, Vec4(1.0, 0.9, 0.4, 1.0), Vec4(1.0, 1.0, 1.0, 1.0)))
        self.pageFlashIval.loop()

    def stopPageFlashIval(self):
        if self.pageFlashIval:
            self.pageFlashIval.finish()
            self.pageFlashIval = None


class StoreItem(DirectFrame):
    def __init__(self, pos, npcWitch, parent):
        DirectFrame.__init__(self,
                             parent=aspect2d,
                             relief=None,
                             geom=DGG.getDefaultDialogGeom(),
                             geom_color=(1, 1, 1, 0),
                             geom_scale=(0.43, 1, 0.33),
                             pos=pos)
        self.initialiseoptions(StoreItem)
        self.item: Optional[InventoryShopItem] = None
        self.itemPreview = None
        self.itemCost = 20
        self.material = None
        self.itemMaterial = None
        self.itemAnimation = None
        self.itemIndex = 0
        self.HWStoreGUI = parent
        buttonModels = loader.loadModel('phase_3.5/models/gui/inventory_gui')
        upButton = buttonModels.find('**/InventoryButtonUp')
        downButton = buttonModels.find('**/InventoryButtonDown')
        rolloverButton = buttonModels.find('**/InventoryButtonRollover')

        multiItem = loader.loadModel('phase_5.5/models/gui/catalog_gui')
        nextUp = multiItem.find('**/arrow_up')
        nextDown = multiItem.find('**/arrow_Down')
        nextRollover = multiItem.find('**/arrow_Rollover')

        buyText = TTLocalizer.CatalogBuyText
        buyTextScale = TTLocalizer.CIPbuyButton
        self.nextItemButton = DirectButton(self,
                                           relief=None,
                                           scale=0.5,
                                           pos=(LPoint3f(0.15, 0, 0)),
                                           image=[nextUp,
                                                  nextDown,
                                                  nextRollover,
                                                  nextUp],
                                           image_color=(0.99, 0.98, 0.9, 1),
                                           image2_color=(1, 1, 1, 1),
                                           command=self.__handleNextItem)
        self.previousItemButton = DirectButton(self,
                                               relief=None,
                                               scale=0.5,
                                               pos=(LPoint3f(-0.155, 0, 0)),
                                               hpr=(180, 0, 0),
                                               image=[nextUp,
                                                      nextDown,
                                                      nextRollover,
                                                      nextUp],
                                               image_color=(0.99, 0.98, 0.9, 1),
                                               image2_color=(1, 1, 1, 1),
                                               command=self.__handlePreviousItem)
        self.buyButton = DirectButton(parent=self, relief=None,
                                      pos=(0.17, 0, 0.13),
                                      scale=(0.5, 1, 0.6),
                                      text=buyText,
                                      text_scale=buyTextScale,
                                      text_pos=(-0.005, -0.01),
                                      image=(upButton,
                                             downButton,
                                             rolloverButton,
                                             upButton),
                                      image_color=(1.0, 0.2, 0.2, 1),
                                      image0_color=Vec4(1.0, 0.4, 0.4, 1),
                                      image3_color=Vec4(1.0, 0.4, 0.4, 0.4),
                                      command=self.__handlePurchaseRequest)
        self.buyConfirmDialog = None
        self.npcWitch = npcWitch
        self.alreadyPurchased = DirectLabel(parent=self,
                                            relief=None,
                                            text=TTLocalizer.CatalogPurchasedText,
                                            pos=(-0.18, 0, 0.13),
                                            text_fg=(1, 1, 1, 1),
                                            scale=0.03)
        self.alreadyPurchased.setHpr(0, 0, -30)
        self.alreadyPurchased.hide()
        self.accept('halloweenStoreCleanupDialogue', self.cleanupBuyConfirmDialog)

    def clearBox(self, clearIndex=False):
        if hasattr(self, 'itemPreview') and self.itemPreview:
            self.itemPreview.removeNode()

        if hasattr(self, 'itemMaterial') and self.itemMaterial:
            self.itemMaterial.removeNode()

        if hasattr(self, 'itemAnimation') and self.itemAnimation:
            self.itemAnimation.finish()

        if hasattr(self, 'buyButton') and self.buyButton:
            self.buyButton.hide()

        if hasattr(self, 'alreadyPurchased') and self.alreadyPurchased:
            self.alreadyPurchased.hide()

        if hasattr(self, 'nextItemButton') and self.nextItemButton:
            self.nextItemButton.hide()

        if hasattr(self, 'previousItemButton') and self.previousItemButton:
            self.previousItemButton.hide()

        self.cleanupBuyConfirmDialog()

        self.itemPreview = None
        self.itemMaterial = None
        self.itemAnimation = None
        self.buyConfirmDialog = None
        self.material = None
        if clearIndex:
            self.itemIndex = 0

    def updateArrows(self):
        if self.itemIndex <= 0:
            self.itemIndex = 0
            self.previousItemButton['state'] = DGG.DISABLED
            self.previousItemButton.hide()
        else:
            self.previousItemButton['state'] = DGG.NORMAL
            self.previousItemButton.show()

        if self.itemIndex >= (len(self.itemList)-1):
            self.itemIndex = (len(self.itemList)-1)
            self.nextItemButton['state'] = DGG.DISABLED
            self.nextItemButton.hide()
        else:
            self.nextItemButton['state'] = DGG.NORMAL
            self.nextItemButton.show()

    def disableArrows(self):
        self.previousItemButton['state'] = DGG.DISABLED
        self.previousItemButton.hide()
        self.nextItemButton['state'] = DGG.DISABLED
        self.nextItemButton.hide()

    def __handleNextItem(self):
        self.itemIndex += 1
        itemCost = self.itemCost
        material = self.material
        self.updateArrows()
        self.clearBox()

        if self.material == CraftingGlobals.CRAFT_MAT_ALL:
            self.hasEnough = all([base.localAvatar.getCraftMaterial(i) >= itemCost for i in range(CraftingGlobals.TOTAL_CRAFT_MATERIALS)])
        else:
            self.hasEnough = base.localAvatar.getCraftMaterial(material) >= itemCost

        self.updatePanel(self.itemList[self.itemIndex],
                         material,
                         hasEnough=self.hasEnough,
                         itemCost=itemCost,
                         itemList=self.itemList)

    def __handlePreviousItem(self):
        self.itemIndex -= 1
        itemCost = self.itemCost
        material = self.material
        self.updateArrows()
        self.clearBox()

        if self.material == CraftingGlobals.CRAFT_MAT_ALL:
            self.hasEnough = all([base.localAvatar.getCraftMaterial(i) >= itemCost for i in range(CraftingGlobals.TOTAL_CRAFT_MATERIALS)])
        else:
            self.hasEnough = base.localAvatar.getCraftMaterial(material) >= itemCost

        self.updatePanel(self.itemList[self.itemIndex],
                         material,
                         hasEnough=self.hasEnough,
                         itemCost=itemCost,
                         itemList=self.itemList)

    def canScroll(self):
        if self.itemList and len(self.itemList) > 1:
            self.updateArrows()
        else:
            self.disableArrows()

    def updatePanel(self, shopItem: InventoryShopItem, material, hasEnough, itemCost=20, itemList: List[InventoryShopItem] = []):
        self.item = shopItem
        self.itemPreview = shopItem.itemDef.getGuiItemModel()
        self.itemPreview.reparentTo(self)
        self.itemPreview.setScale(0.11)
        if self.itemAnimation:
            self.itemAnimation.loop()
        self.material = material
        self.itemCost = itemCost
        self.itemList = itemList
        self.hasEnough = hasEnough
        if material == CraftingGlobals.CRAFT_MAT_ALL:
            labelText = str(self.itemCost) + ' ' + TTLocalizer.MaterialNamesAllMats
        else:
            labelText = str(self.itemCost) + ' ' + TTLocalizer.MaterialNamesPlural[self.material]
        self.itemMaterial = DirectLabel(parent=self,
                                        relief=None,
                                        text=labelText,
                                        pos=(0, 0, -0.17),
                                        text_fg=(0, 0, 0, 1),
                                        scale=0.04)

        if self.item.ownsItem(base.localAvatar):
            self.alreadyPurchased.show()
            self.buyButton.hide()
            self.canScroll()
            return
        else:
            self.buyButton.show()

        self.canScroll()

        if not self.hasEnough:
            self.buyButton['state'] = DGG.DISABLED
        else:
            self.buyButton['state'] = DGG.NORMAL

    def __handlePurchaseRequest(self):
        self.buyButton['state'] = DGG.DISABLED
        # Make sure we clean up any dialog, so we don't create any orphaned dialog prompts. (Thanks, autoclickers.)
        self.cleanupBuyConfirmDialog()
        self.buyConfirmDialog = TTDialog(text=TTLocalizer.halloweenWitchBuyDialog % (self.item.getName(), self.itemMaterial['text']),
                                         text_scale=TTLocalizer.TPdialog,
                                         fadeScreen=0.5,
                                         text_align=TextNode.ACenter,
                                         text_wordwrap=TTLocalizer.TPdialogWordwrap,
                                         command=self.__handlePurchaseRequestResult,
                                         style=TwoChoice,
                                         buttonTextList=[TTLocalizer.AvatarChoiceDeleteOK, TTLocalizer.AvatarChoiceDeleteCancel],
                                         button_text_scale=TTLocalizer.TPbuttonTextList,
                                         sortOrder=NO_FADE_SORT_INDEX)
        self.buyConfirmDialog.show()
        messenger.send('attemptWitchPurchase', [False])

    def __handlePurchaseRequestResult(self, option):
        if option == 1:
            self.__handleBuy()
        else:
            self.buyButton['state'] = DGG.NORMAL
            
        self.cleanupBuyConfirmDialog()
        self.HWStoreGUI.updatePage()
        messenger.send('attemptWitchPurchase', [True])

    def __handleBuy(self):
        self.npcWitch.sendUpdate('requestItemPurchase', [self.item.toStruct()])

    def cleanupBuyConfirmDialog(self):
        if hasattr(self, 'buyConfirmDialog') and self.buyConfirmDialog:
            self.buyConfirmDialog.cleanup()
            self.buyConfirmDialog = None


if __name__ == "__main__":

    # Lazy DWitchNPC
    class Witch:
        def sendUpdate(self, *args):
            pass

        def doExit(self, *args):
            pass


    gui = HalloweenStoreGUI(npcWitch=Witch())
    base.run()
