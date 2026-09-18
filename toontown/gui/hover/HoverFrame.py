from __future__ import annotations
if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from typing import Optional
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.GUINode import GUINode
from toontown.gui import UiHelpers
from toontown.gui.ScaledFrame import ScaledFrame
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.utils.text import capTextScaleToWidth
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.toon.gui import GuiBinGlobals
from toontown.gui.hover.HoverFrameTypes import HoverFrameTypes
from panda3d.core import *
from direct.gui.DirectGui import *
from typing import Union, Any, Tuple


@DirectNotifyCategory()
class HoverFrame(ScaledFrame):
    """
    This GUI frame can be used to render detailed information about an item when its frame is hovered over.
    """
    UnderlineStr = '\1item_hover_underline\1____________________________________\2\n\n'

    @InjectorTarget
    def __init__(self, parent, **kw):
        self.item: Any | None = None
        self.itemType: HoverFrameTypes | None = None
        # GUI boilerplate.
        optiondefs = kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            frameSize=(-0.475, 0.475, -0.4, 0.0),
            scaledTexture='phase_3/maps/gui/ttcc_gui_scaledFrame_shadow.png',
            # ScaledFrame tints its image via colorScale, not frameColor (relief
            # stays None here) -- this is what actually darkens the tooltip.
            # Lower the RGB values further (keep alpha at 1.0) for an even
            # darker look.
            scaledColor=(0.35, 0.35, 0.35, 1.0),
            borderScale=0.04,
            frameXWidth=0.475,
            # relief = None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(HoverFrame)
        self.setBin('item-hover-tooltip', GuiBinGlobals.ItemHoverFrameBin)
        # Guarantee this never gets hidden behind other 2D GUI regardless of
        # bin/depth quirks elsewhere in the inventory UI.
        self.setDepthWrite(False)
        self.setDepthTest(False)
        # Double up on shadow so that the texture is more opaque and thus easier to read text on
        self['shadowStrength'] = 0.001

        self._wantFitToWidth: bool = False

        self.text_title: DirectLabel | None = None
        self.text_description: DirectLabel | None = None

        self.__getDataFuncs = {
            HoverFrameTypes.InventoryItem: self.__getData_inventoryItem,
            HoverFrameTypes.ToonTip: self.__getData_clickToDismiss,
            HoverFrameTypes.Scavenge: self.__getData_itemScavenge,
            HoverFrameTypes.ShopBuyCantAfford: self.__getData_shopBuyCantAfford,
            HoverFrameTypes.ShopBuyFailedReq: self.__getData_shopBuyFailedReq,
        }

        self._create()
        self.place()

    def destroy(self):
        self.setItem(None, None)
        super().destroy()

    def _create(self):
        self.text_title = DirectLabel(parent=self, pos=(0.0, 0, -0.06), text='Title', text_scale=0.065, relief=None,
                                      text_align=TextNode.ACenter, text_fg=(1, 1, 1, 1))
        self.text_description = DirectLabel(parent=self, pos=(-0.45, 0, -0.09), text='Description', text_scale=0.05,
                                            relief=None, text_align=TextNode.ALeft, text_wordwrap=18,
                                            text_fg=(1, 1, 1, 1))

    def place(self):
        if self.item is None or self.itemType is None:
            return

        getDataFunc = self.__getDataFuncs.get(self.itemType)
        if getDataFunc:
            title, desc = getDataFunc()
        else:
            title, desc = 'ERROR', 'ERROR'

        self.text_title['text_scale'] = 0.065
        self.text_title['text'] = title
        capTextScaleToWidth(self.text_title, 0.85)
        self.text_description['text'] = desc

        if self._wantFitToWidth:
            self.fitXWidthToTitle()

        # Scale frame size downwards dependent on the sizing of the description text.
        # Longer description = frame size goes further down
        descHeight = 0.03
        if desc != '':
            tightBounds = self.text_description.component('text0').getTightBounds()
            if tightBounds:
                descHeight = tightBounds[0][2]

        # Hard cap on how tall this can get. Without this, an item with a
        # long/multi-line description (extended description, click-reason
        # text, etc.) can produce a frame tall enough to blanket several
        # rows of the surrounding icon grid -- which is what was happening
        # here. This keeps the popup from ever growing past a reasonable
        # size; if you want the full text to always be visible instead,
        # this needs to shrink the description's text_scale rather than
        # clamp, but clamping is the safe default.
        MaxFrameHeight = 0.9
        descHeight = max(descHeight, -(MaxFrameHeight - 0.11))

        self['frameSize'] = (-self['frameXWidth'], self['frameXWidth'], descHeight - 0.11, 0.0)

    def setItem(self, item: Any | None = None, itemType: HoverFrameTypes | None = None):
        """Sets the item within the ItemFrame."""
        self.item = item
        self.itemType = itemType
        self.place()

    def setHoverDataStyle(self, frameWidth: float, descAlign=TextNode.ALeft, fitToTextWidth=False):
        self['frameXWidth'] = frameWidth
        self.text_description['text_align'] = descAlign
        self.text_description.setPos((0.0, 0, -0.09) if descAlign == TextNode.ACenter else (-0.45, 0, -0.09))
        if fitToTextWidth:
            self._wantFitToWidth = True
            self.fitXWidthToTitle()
        else:
            self._wantFitToWidth = False

    def fitXWidthToTitle(self):
        textBounds = self.text_title.component('text0').getTightBounds()
        if textBounds:
            xWidth = abs(textBounds[1][0] - textBounds[0][0]) * 0.5
            self['frameXWidth'] = xWidth

    # region HoverFrameTypes placements

    def __getData_inventoryItem(self) -> Tuple[str, str]:
        isEquipped = base.localAvatar and self.item in base.localAvatar.getEquippedItems()
        title = self.item.getItemDefinition().getName()
        quantity = self.item.getQuantity()
        if quantity > 1:
            quantityText = f' (x{quantity})'
        else:
            quantityText = ''
        title += quantityText
        if isEquipped:
            # TODO: This equip indicator is temporary, we need an icon
            title += ' \1deepYellow\1(E)\2'
        desc = self.UnderlineStr

        itemDesc = self.item.getItemDefinition().getItemTypeDescriptionInfo(self.item)
        if itemDesc:
            desc += itemDesc
            desc += f'\n{self.UnderlineStr}'

        standardDesc = self.item.getItemDefinition().getDescription()
        if standardDesc:
            desc += standardDesc
            desc += '\1TextShrink\1\n\n\2'
        desc += self.item.getItemDefinition().getExtendedDescription(self.item)

        clickable, reason = self.item.getItemDefinition().getClickable()
        if not clickable:
            desc += f"\n{self.UnderlineStr}\1SlightSlant\1{reason}\2"

        return title, desc

    def __getData_clickToDismiss(self) -> Tuple[str, str]:
        return 'Click to Dismiss', ''

    def __getData_itemScavenge(self) -> Tuple[str, str]:
        title, desc = self.__getData_inventoryItem()
        desc += '\n' + self.UnderlineStr
        desc += 'Click to Dismiss'
        return title, desc

    def __getData_shopBuyCantAfford(self) -> Tuple[str, str]:
        return "Can't Afford", ""

    def __getData_shopBuyFailedReq(self) -> Tuple[str, str]:
        return f"Required: {self.item.getPurchaseReqs()[0].getRequirementText()}", ""

    # endregion


if __name__ == "__main__":
    from toontown.inventory.enums.ItemEnums import BackgroundItemType
    from toontown.inventory.enums.ItemEnums import ChatStickersItemType
    from toontown.inventory.enums.ItemEnums import FishingRodItemType
    from toontown.inventory.enums.ItemEnums import ProfilePoseItemType
    for i, invItem in enumerate([
        InventoryItem.fromSubtype(BackgroundItemType.Event_Winter2018_A),
        InventoryItem.fromSubtype(ChatStickersItemType.GreenedCat),
        InventoryItem.fromSubtype(FishingRodItemType.Platinum)
            ]):
        gui = HoverFrame(
            parent=aspect2d,
            scale=1.0,
            pos=(-1.1 + (i * 1.1), 0, 0),
        )
        gui.setItem(invItem)

    base.setBackgroundColor(0.5, 0.5, 1)

    # GUITemplateSliders(
    #     gui.text_quantity,
    #     'text_pos', 'text_scale'
    # )
    base.run()
