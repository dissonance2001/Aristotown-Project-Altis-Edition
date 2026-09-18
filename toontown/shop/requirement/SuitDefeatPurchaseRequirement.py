from toontown.shop.base.ShopPurchaseRequirement import ShopPurchaseRequirement
from toontown.toonbase import TTLocalizer
from toontown.utils import text


class SuitDefeatPurchaseRequirement(ShopPurchaseRequirement):
    def __init__(self, suitName: str, amount: int) -> None:
        self.suitName = suitName
        self.amount = amount

    def meetsPurchaseRequirement(self, av) -> bool:
        """Does the av meet the requirements to be able to purchase this item?"""
        return av.getGalleryStatus().get(self.suitName, 0) >= self.amount

    def getRequirementText(self) -> str:
        return f"Defeat {TTLocalizer.suitName(self.suitName)} {self.amount} time{text.plural(self.amount)}"
