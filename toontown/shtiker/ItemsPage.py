import math

from direct.gui.DirectGui import *
from panda3d.core import *

from toontown.gui import UiHelpers
from toontown.gui.GUINode import GUINode
from toontown.gui.TTGui import LockingEntry
from toontown.inventory.gui.general.ItemFrameGrid import ItemFrameGrid
from toontown.shtiker import ShtikerPage
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.shtiker.backpack import BackpackCategoryGlobals
from toontown.shtiker.backpack.BackpackCategoryButton import BackpackCategoryButton
from toontown.shtiker.backpack.widgets import *

from typing import Type


class ItemsPage(ShtikerPage.ShtikerPage):
    TotalCategoryButtons = 12
    CategoryButtonsPerSide = 6
    ItemRows = 5
    ItemColumns = 4

    BackpackTabCategories = [
        BackpackCategoryGlobals.BackpackCategory.All,
        BackpackCategoryGlobals.BackpackCategory.Social,
        BackpackCategoryGlobals.BackpackCategory.Profile,
        BackpackCategoryGlobals.BackpackCategory.Battle,
        BackpackCategoryGlobals.BackpackCategory.Estates,
        BackpackCategoryGlobals.BackpackCategory.Activities,
        BackpackCategoryGlobals.BackpackCategory.Misc,
    ]
    WardrobeTabCategories = [
        BackpackCategoryGlobals.BackpackCategory.W_All,
        BackpackCategoryGlobals.BackpackCategory.W_Shirts,
        BackpackCategoryGlobals.BackpackCategory.W_Shorts,
        BackpackCategoryGlobals.BackpackCategory.W_Skirts,
        BackpackCategoryGlobals.BackpackCategory.W_Hats,
        BackpackCategoryGlobals.BackpackCategory.W_Glasses,
        BackpackCategoryGlobals.BackpackCategory.W_Neck,
        BackpackCategoryGlobals.BackpackCategory.W_Backpack,
        BackpackCategoryGlobals.BackpackCategory.W_Shoes,
    ]

    def __init__(self):
        ShtikerPage.ShtikerPage.__init__(self)
        self.title = None
        self.grid = None

        # Tabs
        self.backpackTab = None
        self.wardrobeTab = None
        self.codesTab = None
        self.tabs = []

        # Categories
        self.selectedCategory = BackpackCategoryGlobals.BackpackCategory.All
        self.categoryButtons = []
        self.leftCategoryButtons = []
        self.rightCategoryButtons = []

        # Search
        self.searchBar = None
        self.searchQuery = ''

        # Grid page number
        self.pageNumber = 0
        self.pageLabel = None
        self.leftArrow = None
        self.rightArrow = None

        # Item widget
        self.widgetNode = None
        self.currWidget = None

    def load(self):
        ShtikerPage.ShtikerPage.load(self)
        self.title = DirectLabel(parent=self, relief=None, text=TTLocalizer.ItemsPageTitle, text_scale=0.09,
                                 textMayChange=1, pos=(0, 0, 0.635))
        self.grid = ItemFrameGrid(
            parent=self,
            pos=(0.4375, 0, -0.1),
            scale=0.75,
            gridWidth=self.ItemColumns,
            gridHeight=self.ItemRows,
            gridDistance=0.04,
            gridScale=1.1,
            scrollEnabled=False,
            allowPageOvershoot=True,
            callback=self.__handleClickedItem,
        )

        # Tabs
        self.backpackTab = self.generateTab(text=TTLocalizer.ItemsPageTitle, pos=(-0.5, 0, 0.785), scale=(0.038, 0, 0.045),
                                            command=self.switchToBackpack)
        self.wardrobeTab = self.generateTab(text=TTLocalizer.ItemsPageWardrobeTab, pos=(0, 0, 0.785), scale=(0.038, 0, 0.045),
                                            command=self.switchToWardrobe)
        self.codesTab = self.generateTab(text=TTLocalizer.ItemsPageCodesTab, pos=(0.5, 0, 0.785), scale=(0.038, 0, 0.045),
                                         command=self.switchToCodes)
        self.tabs = [self.backpackTab, self.wardrobeTab, self.codesTab]

        # Categories
        self.categoryButtons = [BackpackCategoryButton(parent=self, scale=0.1) for _ in range(self.TotalCategoryButtons)]
        self.leftCategoryButtons = self.categoryButtons[:self.CategoryButtonsPerSide]
        self.rightCategoryButtons = self.categoryButtons[self.CategoryButtonsPerSide:]
        UiHelpers.placeElementsInHorizontalLine(self.leftCategoryButtons, startPos=(-0.8, 0, 0.55), scale=0.1)
        UiHelpers.placeElementsInHorizontalLine(self.rightCategoryButtons, startPos=(0.1, 0, 0.55), scale=0.1)

        # Search
        self.searchBar = LockingEntry(
            parent=self, relief=DGG.FLAT,
            pos=(0.045, 0, 0.415), scale=0.07795,
            borderWidth=(0.05, 0.05),
            frameColor=(0.7, 0.7, 0.7, 1.0), state=DGG.NORMAL,
            text_align=TextNode.ALeft, text_scale=0.7, width=14.35, numLines=1,
            focus=0, backgroundFocus=0, cursorKeys=1, text_fg=(0, 0, 0, 1), suppressMouse=1, suppressKeys=1, autoCapitalize=0,
            initialText=TTLocalizer.FriendsListSearchBarDefaultText, clearOnFocus=True,
            funcOnAccept=self.setSearchQuery,
        )

        # Grid page number
        self.pageLabel = DirectLabel(
            parent=self,
            relief=None,
            pos=(0.4375, 0, -0.683),
            text='1/1',
            text_scale=0.065,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_align=TextNode.ACenter,
            textMayChange=1,
            text_fg=Vec4(0, 0, 0, 1),
        )
        m = loader.loadModel('phase_3.5/models/gui/clothingpage/clothing_page')
        self.leftArrow = DirectButton(parent=self, relief=None, pos=(0.2375, 0, -0.665),
                                      image=(m.find('**/Arrow_N'), m.find('**/Arrow_P'), m.find('**/Arrow_H')),
                                      image_scale=(1.2 / 8, 1.0, 1.2 / 16),
                                      frameColor=(0.7, 0.7, 0.7, 1),
                                      command=self.__handleArrow,
                                      extraArgs=[-1])
        self.rightArrow = DirectButton(parent=self, relief=None, pos=(0.6375, 0, -0.665),
                                       image=(m.find('**/Arrow_N'), m.find('**/Arrow_P'), m.find('**/Arrow_H')),
                                       image_scale=(-1.2 / 8, 1.0, 1.2 / 16),
                                       frameColor=(0.7, 0.7, 0.7, 1),
                                       command=self.__handleArrow,
                                       extraArgs=[1])
        m.removeNode()

        # Item widget
        self.widgetNode = GUINode(parent=self, pos=(-0.4375, 0, 0))
        self.currWidget = BackpackToonWidget(parent=self.widgetNode)
        self._inventoryRefreshTask = None

    def enter(self):
        ShtikerPage.ShtikerPage.enter(self)
        self.accept('LocalInventorySet', self.refreshItemList)
        self.accept('inventoryDelta', self.refreshItemList)
        self.refreshItemList()
        taskMgr.remove(self.uniqueName('inventoryRefresh'))
        self._inventoryRefreshTask = taskMgr.doMethodLater(0.1, self.__retryInventoryRefresh, self.uniqueName('inventoryRefresh'))

        # Finally, swap to the backpack tab
        self.switchToBackpack()

    def refreshItemList(self, delta=None):
        hammerspace = base.localAvatar.getHammerspace()
        if hammerspace is None:
            return

        if self._inventoryRefreshTask is not None:
            taskMgr.remove(self.uniqueName('inventoryRefresh'))
            self._inventoryRefreshTask = None

        items = hammerspace.getItems()

        def baseFilter(item):
            return BackpackCategoryGlobals.isItemValidForCategory(item, self.selectedCategory)
        filterFunc = baseFilter

        if self.searchQuery and self.searchQuery != '':
            strippedQuery = self.searchQuery.lower().replace(' ', '')
            if strippedQuery != '':
                def searchFilter(item):
                    itemDef = item.getItemDefinition()
                    itemName = itemDef.getName().lower().replace(' ', '')
                    itemType = itemDef.getItemTypeName().lower().replace(' ', '')
                    return (strippedQuery in itemName or strippedQuery in itemType) and baseFilter(item)
                filterFunc = searchFilter

        self.grid.setItemList(list(filter(lambda item: filterFunc(item), items)))

    def __retryInventoryRefresh(self, task):
        self._inventoryRefreshTask = None
        if not self.isVisible():
            return task.done
        if base.localAvatar.getHammerspace() is None:
            self._inventoryRefreshTask = taskMgr.doMethodLater(0.1, self.__retryInventoryRefresh, self.uniqueName('inventoryRefresh'))
            return task.done
        self.refreshItemList()
        return task.done

    def exit(self):
        ShtikerPage.ShtikerPage.exit(self)
        self.ignore('LocalInventorySet')
        self.ignore('inventoryDelta')
        taskMgr.remove(self.uniqueName('inventoryRefresh'))
        self._inventoryRefreshTask = None

    def unload(self):
        if self.grid:
            self.grid.destroy()
            self.grid = None
        self.title = None
        self.backpackTab = None
        self.wardrobeTab = None
        self.codesTab = None
        self.tabs = []
        self.categoryButtons = []
        self.leftCategoryButtons = []
        self.rightCategoryButtons = []
        self.pageLabel = None
        self.leftArrow = None
        self.rightArrow = None
        self.searchBar = None
        self.widgetNode = None
        self.currWidget = None

        ShtikerPage.ShtikerPage.unload(self)

    # region Helper stuff

    def generateTab(self, text, pos, scale, command) -> DirectButton:
        # Creates a tab to go on the top of the Book. Will run command when clicked.
        normalColor = (1, 1, 1, 1)
        clickColor = (0.8, 0.8, 0, 1)
        rolloverColor = (0.15, 0.82, 1.0, 1)
        disabledColor = (1.0, 0.98, 0.15, 1)
        return DirectButton(parent=self, relief=None, text=text,
                            text_scale=TTLocalizer.GPrecordsTab, text_align=TextNode.ACenter,
                            image=loader.loadModel('phase_3.5/models/gui/fishingBook').find('**/tabs/polySurface2'),
                            image_pos=(0, 0, -1.06),
                            image_hpr=(0, 0, -90), image_scale=scale, image_color=normalColor,
                            image1_color=clickColor, image2_color=rolloverColor, image3_color=disabledColor,
                            text_fg=Vec4(0.2, 0.1, 0, 1), command=command,
                            pos=pos, scale=0.9)

    def makeTabActive(self, tab: DirectFrame) -> None:
        # Selects a tab as the current page, highlighting it and making it unselectable.
        tab['state'] = DGG.DISABLED
        for bTab in [pTab for pTab in self.tabs if pTab is not tab]:
            bTab['state'] = DGG.NORMAL

    def setCategory(self, category: BackpackCategoryGlobals.BackpackCategory) -> None:
        self.selectedCategory = category
        self.setPageNumber(0)
        self.refreshItemList()
        self.updatePageLabel()
        self.swapToWidgetType(BackpackToonWidget)
        self.currWidget.exitCodesMode()

    def makeCategoryButtonsActive(self, categoryList: list[BackpackCategoryGlobals.BackpackCategory]) -> None:
        # Run through all buttons and make the ones active that we need
        for i, button in enumerate(self.categoryButtons):
            if i > len(categoryList) - 1:
                button.configure(command=None, extraArgs=None)
                button.hide()
                continue
            button.configure(backpackCategory=categoryList[i], command=self.setCategory, extraArgs=[categoryList[i]])
            button.show()

    def __handleArrow(self, value: int):
        if self.grid.maxPages <= 0:
            return
        newValue = self.pageNumber + value
        if newValue > self.numFullPages or newValue < 0:
            return
        self.setPageNumber(newValue)
        self.grid.refresh(force=True)
        self.updatePageLabel()

    def setPageNumber(self, value: int):
        self.pageNumber = value
        self.grid.currentPage = self.pageNumber * self.ItemRows

    def updatePageLabel(self):
        self.pageLabel['text'] = f'{self.pageNumber + 1}/{self.numFullPages + 1}'

    @property
    def numFullPages(self):
        return int(math.ceil(self.grid.maxPages / self.ItemRows))

    def setSearchQuery(self):
        searchText = self.searchBar.get()
        if searchText in (TTLocalizer.FriendsListSearchBarDefaultText, ''):
            self.searchBar.set(TTLocalizer.FriendsListSearchBarDefaultText)
            searchText = ''

        newQuery = searchText.lower().replace(' ', '')
        if newQuery == self.searchQuery:
            return

        self.searchQuery = newQuery
        self.setPageNumber(0)
        self.refreshItemList()
        self.updatePageLabel()

    def getWidgetForItem(self, item):
        return BackpackStandardItemWidget

    def swapToWidgetType(self, widgetType: Type[DirectFrame]):
        if self.currWidget and self.currWidget.__class__ is widgetType:
            return

        if self.currWidget:
            self.currWidget.destroy()
        self.currWidget = widgetType(parent=self.widgetNode)

    def __handleClickedItem(self, item):
        self.swapToWidgetType(self.getWidgetForItem(item))
        self.currWidget['inventoryItem'] = item

    # endregion
    # region Backpack

    def switchToBackpack(self) -> None:
        self.title['text'] = TTLocalizer.ItemsPageTitle

        # UI Hide/Show
        self.grid.show()
        self.pageLabel.show()
        self.leftArrow.show()
        self.rightArrow.show()
        self.searchBar.show()
        if self.currWidget:
            self.currWidget.show()

        self.setCategory(BackpackCategoryGlobals.BackpackCategory.All)
        self.makeCategoryButtonsActive(self.BackpackTabCategories)
        self.makeTabActive(self.backpackTab)
        # Widget swap is handled in setCategory
        messenger.send('wakeup')

    # endregion
    # region Wardrobe

    def switchToWardrobe(self):
        self.title['text'] = TTLocalizer.ItemsPageWardrobeTab

        # UI Hide/Show
        self.grid.show()
        self.pageLabel.show()
        self.leftArrow.show()
        self.rightArrow.show()
        self.searchBar.show()
        if self.currWidget:
            self.currWidget.show()

        self.setCategory(BackpackCategoryGlobals.BackpackCategory.W_All)
        self.makeCategoryButtonsActive(self.WardrobeTabCategories)
        self.makeTabActive(self.wardrobeTab)
        # Widget swap is handled in setCategory
        messenger.send('wakeup')

    # endregion
    # region Codes

    def switchToCodes(self):
        self.title['text'] = TTLocalizer.ItemsPageCodesTab

        # UI Hide/Show
        self.grid.hide()
        self.pageLabel.hide()
        self.leftArrow.hide()
        self.rightArrow.hide()
        self.searchBar.hide()
        [button.hide() for button in self.categoryButtons]

        self.makeTabActive(self.codesTab)
        self.swapToWidgetType(BackpackToonWidget)
        self.currWidget.enterCodesMode()
        messenger.send('wakeup')

    # endregion
