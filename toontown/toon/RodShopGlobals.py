"""
Item catalogue for DistributedNPCRodClerk(AI), using the generic NPC shop
system ported from Clash (toontown/shop/, toontown/toon/npc/shop/), same
pattern as TailorShopGlobals.py.

Sells every fishing rod except Cardboard (the free starter rod everyone
gets automatically -- see DefaultInventory.py), gated by the same
per-rod jellybean price (FishGlobals.FishingRodCosts) and level minimum
(FishingRodRegistry's levelMinimum) that the rod's own FishingRodDefinition
already declares, so there's only one place that ever needs updating if
rod pricing/leveling changes.
"""
from enum import auto

from toontown.shop.base.ShopCategoryEnum import ShopCategoryEnum
from toontown.shop.base.ShopItemCatalogue import ShopItemCatalogue
from toontown.shop.base.ShopItemListing import ShopItemListing
from toontown.shop.item.InventoryShopItem import InventoryShopItem
from toontown.shop.cost.JellybeanPriceTag import JellybeanPriceTag
from toontown.shop.requirement.LevelPurchaseRequirement import LevelPurchaseRequirement

from toontown.inventory.enums.ItemEnums import FishingRodItemType
from toontown.inventory.registry.ItemTypeRegistry import getItemDefinition
from toontown.fishing.FishGlobals import FishingRodCosts, AllShopRods


class RodShopCategory(ShopCategoryEnum):
    """The current category of the Rod Clerk's shop."""
    FishingRods = auto()


ShopCategoryToTitle = {
    RodShopCategory.FishingRods: 'Fishing Rods',
}


def _makeRodShopItem(rodSubtype: FishingRodItemType) -> InventoryShopItem:
    rodDef = getItemDefinition(rodSubtype)
    return InventoryShopItem(
        rodSubtype,
        priceTags=JellybeanPriceTag(FishingRodCosts[rodSubtype]),
        purchaseReqs=LevelPurchaseRequirement(rodDef.getLevelMinimum()),
    )


RodShopItems = ShopItemCatalogue({
    RodShopCategory.FishingRods: ShopItemListing([
        _makeRodShopItem(rodSubtype) for rodSubtype in AllShopRods
    ]),
})
