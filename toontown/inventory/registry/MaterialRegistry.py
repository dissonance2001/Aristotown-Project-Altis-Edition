"""
This module contains the item data for the different materials/currencies of Toontown.
"""
from __future__ import annotations
from panda3d.core import NodePath

from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.base.ItemDefinition import ItemDefinition
from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.inventory.enums.RarityEnums import Rarity
from typing import Dict, Optional, List
from enum import IntEnum


class MaterialItemDefinition(ItemDefinition):
    """
    The definition structure for material items.
    """

    def __init__(self,
                 textIcon='package',
                 wantPlural=True,
                 **kwargs):
        super().__init__(**kwargs)
        self.matTextIcon = textIcon
        self.wantPlural = wantPlural

    def getMaterialTextIcon(self):
        return self.matTextIcon

    def getWantPlural(self):
        return self.wantPlural

    def getItemTypeName(self):
        return 'Material'

    def getRewardName(self, item: Optional[InventoryItem] = None) -> str:
        return f"{item.getQuantity()} {self.getName(item)}{'s' if item.getQuantity() != 1 and self.getWantPlural() else ''}"

    def getGuiItemModel(self, item: Optional[InventoryItem] = None, *args, **kwargs) -> NodePath:
        """
        Returns a nodepath that is to be used in 2D space.
        """
        return super().getGuiItemModel(item=item, useModel=self.renderTextForGuiModel(item), *args, **kwargs)

    def getTextIcon(self, item: Optional[InventoryItem] = None) -> str:
        """
        Appears on:
        - Mini icons for quest reward text
        """
        return f'\1white\1\5reward_{self.getMaterialTextIcon()}Icon\5\2'

# The registry dictionary for currencies.
MaterialRegistry: Dict[IntEnum, MaterialItemDefinition] = {
    MaterialItemType.Jellybeans: MaterialItemDefinition(
        name="Jellybean",
        description='The main currency of Toontown.',
        textIcon='beanJar',
    ),
    MaterialItemType.Gumballs: MaterialItemDefinition(
        name="Gumball",
        description='Special currency that can be used in the Gumball Machine in all Toon Headquarters.',
        textIcon='gumball'
    ),
    MaterialItemType.Batcoin: MaterialItemDefinition(
        name="Batcoin",
        description='Crypt-o-currency. Redeem at Hexadecimal for prizes!',
        wantPlural=False,
    ),

    # Rewards
    MaterialItemType.Counterfeits: MaterialItemDefinition(
        name="Counterfeit",
        description="Counterfeits can be used to Forge any Gag, allowing you to use it once for free!"
    ),
    MaterialItemType.CeaseAndDesists: MaterialItemDefinition(
        name="Cease and Desist",
        description="Cease and Desists can stun any non-manager Cog in battle for up to five rounds."
    ),
    MaterialItemType.PinkSlips: MaterialItemDefinition(
        name="Pink Slip",
        description="Pink Slips can be used to fire any non-manager Cog from the battle!"
    ),
}
