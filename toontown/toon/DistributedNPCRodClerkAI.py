"""
DistributedNPCRodClerkAI -- rewritten to use Clash's generic NPC item-shop
system (toontown/shop/, toontown/toon/npc/shop/) instead of the old
money/index-based rod-selling flow (completeSale/NPCToons movie codes,
avatar.fishingRods/b_setFishingRod).

Unlike DistributedNPCTailorAI (a generic NPC type shared by many placements,
so it uses one static catalogue), this NPC IS a specific named individual --
Tell-Tale Carp, Clash's NPCToonID.EdgarAllanPole -- and Altis already has a
full, better catalogue for it sitting in NPCToonShopGlobals.py (proper
fishing-activity-level gating via ActivityLevelPurchaseRequirement, plus
fishing bucket upgrades), so we pull from there instead of duplicating it.

NOTE: this class's dclass in the .dc file needs to declare the same fields
DistributedNPCTailor(AI) has for the generic shop system to work:
requestItemPurchase (client->AI), toonInteracted (client->AI),
onItemPurchase / handleBuyResponse / handleInteraction (AI->client). The old
avatarEnter/completeSale/setMovie fields this class used to rely on are no
longer called by this file.
"""
import random

from toontown.toon.DistributedNPCToonBaseAI import *
from toontown.shop.ShopManagerAI import ShopManagerAI
from toontown.shop.base.ShopItem import ShopItem
from toontown.toon.npc.NPCToonConstants import NPCToonID
from toontown.toon.npc.shop.NPCToonShopGlobals import getNPCItemCatalogue
from toontown.toonbase import TTLocalizer


class DistributedNPCRodClerkAI(DistributedNPCToonBaseAI, ShopManagerAI):

    def __init__(self, air, npcId):
        DistributedNPCToonBaseAI.__init__(self, air, npcId)
        ShopManagerAI.__init__(self, air, getNPCItemCatalogue(NPCToonID.EdgarAllanPole))

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
