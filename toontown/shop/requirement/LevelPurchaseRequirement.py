from toontown.shop.base.ShopPurchaseRequirement import ShopPurchaseRequirement


class LevelPurchaseRequirement(ShopPurchaseRequirement):
    def __init__(self, level: int) -> None:
        self.level = level

    def meetsPurchaseRequirement(self, av) -> bool:
        """Does the av meet the requirements to be able to purchase this item?"""
        return av.getToonLevel() >= self.level

    def getRequirementText(self) -> str:
        return f"Level {self.level+1}"
