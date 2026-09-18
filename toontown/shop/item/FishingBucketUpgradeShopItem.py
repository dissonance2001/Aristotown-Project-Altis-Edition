from __future__ import annotations
from enum import IntEnum
from typing import Any, Optional
from panda3d.core import *

from toontown.inventory.base.Inventory import Inventory
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.registry import ItemTypeRegistry
from toontown.shop.base.ShopItem import ShopItem
from toontown.shop.base.ShopPriceTag import PriceTags
from toontown.shop.base.ShopPurchaseRequirement import PurchaseRequirements


class FishingBucketUpgradeShopItem(ShopItem):
    def __init__(self, upgradeAmount: int, minBucketAmount: int, priceTags: PriceTags,
                 purchaseReqs: PurchaseRequirements | None = None):
        super().__init__(priceTags=priceTags, purchaseReqs=purchaseReqs)
        # How much should this bucket upgrade change our capacity by
        self.upgradeAmount = upgradeAmount
        # The bucket upgrade will not be purchaseable until this bucket threshold is reached
        self.minBucketAmount = minBucketAmount

    def grantItem(self, av) -> Any:
        av.b_setMaxFishTank(av.getMaxFishTank() + self.upgradeAmount)

    def getName(self, av=None) -> str:
        return f'Fishing Bucket Upgrade ({self.getAfterUpgradeAmount()})'

    def getDescription(self, av=None) -> str:
        baseStr = f'Upgrades the capacity of your Fishing Bucket by +{self.upgradeAmount}!'
        return baseStr

    def canPurchase(self, av) -> bool:
        return super().canPurchase(av) and self.getAfterUpgradeAmount() > av.getMaxFishTank() >= self.minBucketAmount

    def ownsItem(self, av) -> bool:
        return av.getMaxFishTank() >= self.getAfterUpgradeAmount()

    def getAfterUpgradeAmount(self):
        return self.minBucketAmount + self.upgradeAmount

    def getGuiItemModel(self) -> NodePath:
        gui = loader.loadModel('phase_4/models/gui/fishingGui')
        bucket = gui.find('**/bucket')
        bucketHolder = NodePath('bucket-holder')
        bucket.reparentTo(bucketHolder)
        bucket.setPos(-1.15, 0, 1.15)
        bucketHolder.setScale(0.2)
        gui.removeNode()
        return bucketHolder

    def getLocalAvUpdateMessage(self):
        """
        What message should this shop item listen to on GUI elements to tell when the av has purchased it?
        """
        return 'localMaxFishTankChange'
