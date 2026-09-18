from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.shop.base.ShopPriceTag import ShopPriceTag


class GumballsPriceTag(ShopPriceTag):
    """
    The gumball price tag.
    """

    def __repr__(self):
        return f'{self.getCost()} gbs'

    def canAfford(self, av) -> bool:
        return av.getMoney(currencyType=MaterialItemType.Gumballs) >= self.getCost()

    def attemptPurchase(self, av) -> bool:
        return av.takeMoney(self.getCost(), currencyType=MaterialItemType.Gumballs)
