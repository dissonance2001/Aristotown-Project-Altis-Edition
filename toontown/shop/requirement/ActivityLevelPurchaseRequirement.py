from toontown.shop.base.ShopPurchaseRequirement import ShopPurchaseRequirement
from toontown.toonbase import TTLocalizer


class ActivityLevelPurchaseRequirement(ShopPurchaseRequirement):
    def __init__(self, activity, level: int) -> None:
        self.activity = activity
        self.level = level

    def meetsPurchaseRequirement(self, av) -> bool:
        """Does the av meet the requirements to be able to purchase this item?"""
        return av.getActivityLevel(self.activity) >= self.level

    def getRequirementText(self) -> str:
        return f"{TTLocalizer.ActivityExpBarLevel[self.activity]}{self.level+1}"
