from toontown.crafting.CraftingGlobals import HalloweenMaterial
from toontown.shop.base.ShopPriceTag import ShopPriceTag
from toontown.toonbase import TTLocalizer


class HalloweenPriceTag(ShopPriceTag):
    """
    The price tag for Halloween materials.
    """

    def __init__(self, material: HalloweenMaterial, cost: int):
        super().__init__(cost=cost)
        self.material = material

    def __repr__(self):
        if self.material == -1:
            return f'x{self.getCost()} of all'
        return f'x{self.getCost()} {TTLocalizer.MaterialNamesPlural[self.material]}'

    def canAfford(self, av) -> bool:
        if self.material == -1:
            return all(av.getCraftMaterial(material) >= self.getCost() for material in HalloweenMaterial)
        return av.getCraftMaterial(self.material) >= self.getCost()

    def attemptPurchase(self, av) -> bool:
        if self.material == -1:
            # Consume all mats
            for material in HalloweenMaterial:
                total = av.getCraftMaterial(material)
                av.setCraftMaterial(material, total - self.cost)
            return True
        else:
            # Consume just the one
            total = av.getCraftMaterial(self.material)
            av.setCraftMaterial(self.material, total - self.cost)
            return True

    def getMaterialType(self) -> HalloweenMaterial:
        return self.material
