from toontown.shop.base.ShopPriceTag import ShopPriceTag


class JellybeanPriceTag(ShopPriceTag):
    """
    The jellybean price tag.
    """

    def __repr__(self):
        return f'{self.getCost()} jellybeans'

    def canAfford(self, av) -> bool:
        return av.getTotalMoney() >= self.getCost()

    def attemptPurchase(self, av) -> bool:
        return av.takeMoney(self.getCost())

    def getLabelString(self, av=None, override=None):
        cost = override if override is not None else self.getCost()
        if av and av.getTotalMoney() < cost:
            # Can't afford
            costStr = f'\1deepRed\1{cost:,}\2'
        else:
            # Can afford
            costStr = f'{cost:,}'
        return f'\1white\1\5reward_beanJarIcon\5\2 {costStr}'

    def getCostName(self):
        return 'Jellybeans'

    def getAvatarOwnedAmount(self, av):
        return av.getMoney()

    @staticmethod
    def getCostTypeOwnedDisplayGui(parent, amount=None):
        """
        Returns a GUI element that displays the amount the user currently owns of this price tag type.
        i.e. Returns a bean jar element that shows current beans for items that cost beans.
        """
        from toontown.gui.JellybeanBank import JellybeanBank
        beanBank = JellybeanBank(parent, money=amount)
        beanBank.setToShowTotal()
        return beanBank

    def getPriceTagGui(self, av, parent, amount=None):
        """
        Returns a GUI element that displays the cost amount of this price tag type.
        """
        from toontown.shop.cost.gui.JellybeanPriceTagFrame import JellybeanPriceTagFrame
        beanBank = JellybeanPriceTagFrame(parent, money=amount)
        if av and not self.canAfford(av):
            beanBank.makeTextColorRed()
        return beanBank
