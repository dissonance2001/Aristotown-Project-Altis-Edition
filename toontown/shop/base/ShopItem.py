from __future__ import annotations
from toontown.shop.base.ShopPriceTag import ShopPriceTag, PriceTags
from toontown.shop.base.ShopPurchaseRequirement import ShopPurchaseRequirement, PurchaseRequirements

from typing import Tuple, Optional, Any
from abc import ABC

from typing import TYPE_CHECKING

from toontown.utils.AstronStruct import AstronStruct
from panda3d.core import *

if TYPE_CHECKING:
    from toontown.toon.DistributedToonAI import DistributedToonAI


class ShopItem(ABC, AstronStruct):
    """
    A Shop Item is a generic item dataclass that has all of the parameters
    required to form a completely "purchaseable" item from players.

    This class is intended to be overwritten.
    """

    def __init__(self, priceTags: PriceTags, purchaseReqs: PurchaseRequirements | None = None):
        self._internal_item_index = 0
        self._priceTags = priceTags
        # Purchase requirements are optional
        self._purchaseRequirements = purchaseReqs or tuple()

    def __repr__(self):
        return f"{self.getName()} " \
               f"({', '.join(map(repr, [priceTag for priceTag in self.getPriceTags()]))})" \
               f"({', '.join(map(repr, [priceReq for priceReq in self.getPurchaseReqs()]))})"

    def __eq__(self, other):
        return isinstance(other, ShopItem) and self.getItemIndex() == other.getItemIndex()

    ### Boring Networking Stuff ###

    def setInternalItemIndex(self, index: int):
        self._internal_item_index = index

    def getItemIndex(self) -> int:
        return self._internal_item_index

    def toStruct(self) -> int:
        return self._internal_item_index

    @classmethod
    def fromStruct(cls, itemIndex, itemCatalogue = None, **kwargs) -> Optional['ShopItem']:
        # We need an item catalogue passed in!
        assert itemCatalogue is not None

        # Return our item.
        return itemCatalogue.getItemFromIndex(itemIndex, **kwargs)

    @classmethod
    def fromStructList(cls, struct, itemCatalogue = None):
        return [cls.fromStruct(substruct, itemCatalogue=itemCatalogue) for substruct in struct]

    ### Item Redemption ###

    def attemptPurchase(self, av) -> bool:
        """
        Attempts to purchase the item now.
        :type av: DistributedToonAI
        """
        return all(priceTag.attemptPurchase(av) for priceTag in self.getPriceTags())

    def grantItem(self, av) -> Any:
        """
        Grants an avatar this shop item.
        Note that NO KIND OF CHECKING must be done here! The item must be given successfully.
        Any validation must be handled by overwriting ShopItem.canPurchase.

        :type av: DistributedToonAI
        """
        raise NotImplementedError

    ### Getters ###

    def getName(self, av=None) -> str:
        """Gets the name of the ShopItem."""
        raise NotImplementedError

    def getDescription(self, av=None) -> str:
        """Gets the description of the ShopItem."""
        raise NotImplementedError

    def getPriceTags(self) -> Tuple[ShopPriceTag]:
        """Gets any and all 'price tags' of the ShopItem."""
        if not isinstance(self._priceTags, tuple):
            return self._priceTags,
        return self._priceTags

    def getPurchaseReqs(self) -> Tuple[ShopPurchaseRequirement]:
        """Gets any and all 'purchase requirements' of the ShopItem."""
        if not isinstance(self._purchaseRequirements, tuple):
            return self._purchaseRequirements,
        return self._purchaseRequirements

    def getGuiItemModel(self) -> NodePath:
        # Intended to be overridden in subclasses
        return NodePath('ShopItem-GuiItemModel')

    def getLocalAvUpdateMessage(self):
        """
        What message should this shop item listen to on GUI elements to tell when the av has purchased it?
        """
        return 'inventoryDelta'

    ### Complex Getters ###

    def canPurchase(self, av) -> bool:
        """
        A general method for determining if the item is purchaseable.
        Subclasses can overwrite for various determination.
        :type av: DistributedToonAI
        """
        return self.canAfford(av) and self.purchaseReqsPass(av)

    def canAfford(self, av) -> bool:
        """
        Can we afford this item?
        :type av: DistributedToonAI
        """
        return all(priceTag.canAfford(av) for priceTag in self.getPriceTags())

    def purchaseReqsPass(self, av):
        """
        Does the av pass the purchase requirement checks?
        :type av: DistributedToonAI
        """
        return all(purchaseReq.meetsPurchaseRequirement(av) for purchaseReq in self.getPurchaseReqs())

    def ownsItem(self, av) -> bool:
        """
        Do we own the item?
        """
        return False
