"""
DistributedNPCTailorAI -- rewritten to use Clash's generic NPC item-shop system
(toontown/shop/, toontown/toon/npc/shop/) instead of the old DNA-swap-based
clothes-changing flow. Sells items from TailorShopGlobals.TailorShopItems.

Pattern adapted from Clash's DistributedNPCItemSellerAI
(toontown/toon/npc/NPCToonClassesAI.py). Every Tailor NPC gets the same
static catalogue (Altis's Tailor is a generic NPC type, not a specific named
individual the way Clash's shop NPCs are), rather than looking one up per npcId.
"""
import random

from toontown.toon.DistributedNPCToonBaseAI import *
from toontown.shop.ShopManagerAI import ShopManagerAI
from toontown.shop.base.ShopItem import ShopItem
from toontown.toon.TailorShopGlobals import TailorShopItems
from toontown.toonbase import TTLocalizer


class DistributedNPCTailorAI(DistributedNPCToonBaseAI, ShopManagerAI):

    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        ShopManagerAI.__init__(self, air, TailorShopItems)

    def sendPurchaseNotification(self, av):
        pass

    def callbackAvatarCannotAfford(self, shopItem: ShopItem, av):
        self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [1])

    def performAdditionalPurchaseChecks(self, shopItem: ShopItem, av) -> bool:
        return super().performAdditionalPurchaseChecks(shopItem=shopItem, av=av)

    def callbackAvatarCannotPurchase(self, shopItem: ShopItem, av):
        self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [3])

    def callbackPurchaseAttemptFailed(self, shopItem: ShopItem, av):
        self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [4])

    def callbackPurchaseSuccessful(self, shopItem: ShopItem, av, returnValue=None):
        if returnValue is True:
            self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [5])
        else:
            self.sendUpdateToAvatarId(av.doId, 'handleBuyResponse', [0])

    def toonInteracted(self, contextCode):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return

        # Get the pool of phrases we can say using the context code.
        # Since this is given from the client, make sure it's allowed.
        phrasePool = TTLocalizer.NPCStoreEnterExitResponses.get(contextCode)
        if not phrasePool:
            return

        phraseIndex = random.randint(0, len(phrasePool) - 1)
        self.sendUpdateToAvatarId(avId, 'handleInteraction', [contextCode, phraseIndex])
