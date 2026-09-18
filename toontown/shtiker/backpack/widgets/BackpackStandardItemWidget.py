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
from toontown.inventory.gui.general.ItemFrameGrid import ItemFrameGrid
from toontown.menu.MainMenuGui import GoodMainMenuButton

from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils import ColorHelper, Nodes
from direct.gui import DirectGuiGlobals as DGG
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from direct.showbase import PythonUtil
from panda3d.core import *
from enum import Enum, auto


class EquipButtonState(Enum):
    Equip = auto()
    Unequip = auto()
    Equipped = auto()
    Waiting = auto()


class BackpackStandardItemWidget(DirectFrame, Bounds):
    """
    A widget for the left side of the backpack page that shows a standard item
    """
    EquipWaitTaskName = 'BackpackStandardItemWidget-WaitForEquip-Timeout'

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            relief=None,

            inventoryItem=[None, self.place],
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.postInitialized = False
        self.postInitialiseFuncList.append(lambda: setattr(self, 'postInitialized', True))
        self.initialiseoptions(BackpackStandardItemWidget)

        # Gui prototypes
        self.main_node = None
        self.main_item_node = None
        self.current_node = None
        self.new_node = None
        self.label_title = None
        self.label_description = None
        self.label_current = None
        self.label_new = None
        self.item_main = None
        self.item_current = None
        self.item_new = None
        self.arrow_new = None
        self.button_equip = None
        self.button_equip_state = None

        # Call these two.
        self.__create()
        self.place()

        # Start accepting equip item messages
        self.accept(f'EquippedInventorySet-{base.localAvatar.doId}', self.__handleNewEquippedInventory)

    def __create(self):
        # Nodes
        self.main_node = GUINode(parent=self)
        self.main_item_node = GUINode(parent=self, pos=(0, 0, 0.2))
        self.current_node = GUINode(parent=self, pos=(-0.25, 0, -0.35))
        self.new_node = GUINode(parent=self, pos=(0.25, 0, -0.35))

        # Labels
        self.label_title = DirectLabel(
            parent=self.main_item_node,
            relief=None,
            pos=(0, 0, 0.15),
            text='Item Title',
            text_scale=0.055,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=Vec4(0, 0, 0, 1),
            textMayChange=1,
        )
        self.label_description = DirectLabel(
            parent=self.main_item_node,
            relief=None,
            pos=(0, 0, -0.16),
            text='Item Description',
            text_scale=0.04,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=Vec4(0, 0, 0, 1),
            text_wordwrap=18.0,
            textMayChange=1,
        )
        self.label_current = DirectLabel(
            parent=self.current_node,
            relief=None,
            pos=(0, 0, 0.1),
            text='Current',
            text_scale=0.055,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=Vec4(0, 0, 0, 1),
            textMayChange=1,
        )
        self.label_new = DirectLabel(
            parent=self.new_node,
            relief=None,
            pos=(0, 0, 0.1),
            text='New',
            text_scale=0.055,
            text_align=TextNode.ACenter,
            text_font=ToontownGlobals.getInterfaceFont(),
            text_fg=Vec4(0, 0, 0, 1),
            textMayChange=1,
        )

        # Items
        # These are 1x1 item frame grids on purpose so that they get the item hover
        self.item_main = ItemFrameGrid(
            parent=self.main_item_node,
            pos=(0.0, 0, 0.0),
            scale=1.0,
            gridWidth=1,
            gridHeight=1,
            gridDistance=0.0,
            gridScale=1.1,
            scrollEnabled=False
        )
        self.item_current = ItemFrameGrid(
            parent=self.current_node,
            pos=(0.0, 0, 0.0),
            scale=0.75,
            gridWidth=1,
            gridHeight=1,
            gridDistance=0.0,
            gridScale=1.1,
            scrollEnabled=False
        )
        self.item_new = ItemFrameGrid(
            parent=self.new_node,
            pos=(0.0, 0, 0.0),
            scale=0.75,
            gridWidth=1,
            gridHeight=1,
            gridDistance=0.0,
            gridScale=1.1,
            scrollEnabled=False
        )

        # Misc
        arrow = loader.loadModel('phase_3/models/gui/arrow')
        arrow.setColor(0.2, 0.9, 0.2, 1)
        self.arrow_new = DirectFrame(
            parent=self.main_node,
            relief=None,
            pos=(0, 0, -0.35),
            geom=arrow,
            geom_scale=0.12,
        )
        self.button_equip = GoodMainMenuButton(
            parent=self.main_node,
            text='Equip',
            pos=(0.0, 0, -0.575),
            image_color=(0.2, 0.9, 0.2, 1),
            command=self.__handleEquip,
        )

    def place(self):
        if not self.postInitialized:
            return
        if not self['inventoryItem']:
            return

        self.removeTask(self.EquipWaitTaskName)

        itemDef = self['inventoryItem'].getItemDefinition()
        itemType = self['inventoryItem'].getItemType()
        self.item_main.setItemList([self['inventoryItem']])
        self.label_title['text'] = itemDef.getName()
        self.label_description['text'] = itemDef.getDescription()

        self.label_current.hide()
        self.label_new.hide()
        self.item_current.hide()
        self.item_new.hide()
        self.button_equip.hide()
        self.arrow_new.hide()

        # Handle equippable logic
        behavior = self['inventoryItem'].getInventoryItemBehavior()
        if behavior.canEquip():
            self.main_item_node.setPos(0, 0, 0.2)
            self.button_equip.setPos(0, 0, -0.575)

            equippedItems = base.localAvatar.getEquippedItemsOfType(itemType)
            isEquipped = self['inventoryItem'] in equippedItems
            cantUnequip = isEquipped and len(equippedItems) - 1 < (behavior.getMinEquipped() or 0)
            if isEquipped:
                equipState = EquipButtonState.Equipped if cantUnequip else EquipButtonState.Unequip
            else:
                equipState = EquipButtonState.Equip
            self.setEquipButtonState(equipState)

            isMaxedEquip = len(equippedItems) >= behavior.getMaxEquipped()
            if (not isEquipped) and isMaxedEquip and not cantUnequip:
                self.item_current.setItemList([equippedItems[0]])
                self.item_current.show()
                self.item_new.setItemList([self['inventoryItem']])
                self.item_new.show()
                self.arrow_new.show()
                self.label_current.show()
                self.label_new.show()
            else:
                self.main_item_node.setPos(0, 0, 0.15)
                self.button_equip.setPos(0, 0, -0.475)

            self.button_equip.show()
        else:
            self.main_item_node.setPos(0, 0, 0.05)

    def setEquipButtonState(self, equipButtonState: EquipButtonState):
        if equipButtonState == EquipButtonState.Equip:
            self.button_equip['text'] = 'Equip'
            self.button_equip['image_color'] = (0.2, 0.9, 0.2, 1)
            self.button_equip['state'] = DGG.NORMAL
        elif equipButtonState == EquipButtonState.Unequip:
            self.button_equip['text'] = 'Un-equip'
            self.button_equip['image_color'] = (1.0, 0.45, 0.45, 1.0)
            self.button_equip['state'] = DGG.NORMAL
        else:
            self.button_equip['text'] = 'Equipped' if equipButtonState == EquipButtonState.Equipped else 'Waiting...'
            self.button_equip['image_color'] = (0.5, 0.5, 0.5, 0.5)
            self.button_equip['state'] = DGG.DISABLED
        self.button_equip_state = equipButtonState

    def destroy(self):
        self.ignoreAll()
        super().destroy()

    def __handleEquip(self):
        if self.button_equip_state == EquipButtonState.Equipped:
            return
        elif self.button_equip_state == EquipButtonState.Equip:
            base.localAvatar.d_requestEquipItems([self['inventoryItem']])
        else:
            base.localAvatar.d_requestUnequipItems([self['inventoryItem']])
        # Disable the button until we get a server response
        self.setEquipButtonState(EquipButtonState.Waiting)
        # Add a timeout task just in case something goofy happens
        self.doMethodLater(5.0, self.__handleNewEquippedInventory, name=self.EquipWaitTaskName, extraArgs=[])

    def __handleNewEquippedInventory(self):
        self.removeTask(self.EquipWaitTaskName)
        # Find the same item from the updated inventory and set it again
        # This will update the panel with the new equip information
        hammerspace = base.localAvatar.getHammerspace()
        newItem = hammerspace.findItemOfID(self['inventoryItem'].getItemID()) if hammerspace else None
        if newItem:
            self['inventoryItem'] = newItem
            self.place()


if __name__ == "__main__":
    gui = BackpackStandardItemWidget(
        parent=aspect2d,
        # any kwargs go here
    )
    GUITemplateSliders(
        gui,
        'pos', 'scale'
    )
    base.run()
