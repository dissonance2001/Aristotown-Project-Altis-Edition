"""
Item catalogue for DistributedNPCTailor(AI), using the generic NPC shop system
ported from Clash (toontown/shop/, toontown/toon/npc/shop/).

Mirrors Clash's exact "Clothing" category catalogue (from
toontown/toon/npc/shop/NPCToonShopGlobals.py, originally sold by the racing
NPCs Anita Winn/Ivona Race) -- same 13 items, same 500-jellybean price, same
ActivityLevelPurchaseRequirement(ACTIVITY_RACING, 29) gate.

NOTE: Altis has no racing activity-level tracking system yet (planned for
later) -- DistributedToonAI.getActivityLevel() is currently a stub that always
returns 0, so these items are structurally wired and priced correctly but will
stay locked for everyone until that system exists.
"""
from enum import auto

from toontown.shop.base.ShopCategoryEnum import ShopCategoryEnum
from toontown.shop.base.ShopItemCatalogue import ShopItemCatalogue
from toontown.shop.base.ShopItemListing import ShopItemListing
from toontown.shop.item.InventoryShopItem import InventoryShopItem
from toontown.shop.cost.JellybeanPriceTag import JellybeanPriceTag
from toontown.shop.requirement.ActivityLevelPurchaseRequirement import ActivityLevelPurchaseRequirement

from toontown.toonbase import ToontownGlobals
from toontown.inventory.enums.ItemEnums import ClothingTopItemType, ClothingBottomItemType


class TailorShopCategory(ShopCategoryEnum):
    """The current category of the Tailor's shop."""
    Clothing = auto()


ShopCategoryToTitle = {
    TailorShopCategory.Clothing: 'Clothing',
}

_racingGate = ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)

TailorShopItems = ShopItemCatalogue({
    TailorShopCategory.Clothing: ShopItemListing([
        InventoryShopItem(ClothingTopItemType.RacerJumpsuit, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingTopItemType.RacingFlag, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingTopItemType.RoadsterRaceway, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingTopItemType.Roadster, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.CheckeredRacingShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.BlueRacingShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.IndigoRacingShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.DarkBlueRacingShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.RacingStripeShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.RedCheckeredSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.BlueCheckeredRacingSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.IndigoRacingSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.DarkBlueRacingSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
        InventoryShopItem(ClothingBottomItemType.RacingStripeSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=_racingGate),
    ]),
})
