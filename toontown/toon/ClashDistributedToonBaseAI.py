from __future__ import annotations
from typing import List, Optional

from direct.distributed.ClockDelta import globalClockDelta
from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI

from otp.avatar.DistributedAvatarAI import DistributedAvatarAI
from toontown.chat.models.ChatMessage import ChatMessage
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.enums.ItemEnums import ItemType
from toontown.inventory.registry.ItemTypeRegistry import ItemTypeRegistry
from toontown.battle import BattleGlobals
from toontown.modifiers.ModifiableDOAI import ModifiableDOAI
from toontown.modifiers.ModifierEnums import HP_MODIFIERS, ModifierType
from toontown.toon.Experience import Experience
from toontown.toon.GagInventoryBase import GagInventoryBase
from toontown.toon.ToonDNA import ToonDNA


class ClashDistributedToonBaseAI(DistributedAvatarAI, DistributedSmoothNodeAI, BattleAvatar):
    """DistributedToonBaseAI: Server representation of the base class 
    for ALL distributed toon objects (players and npcs).
    """

    def __init__(self, air, name=None):
        DistributedAvatarAI.__init__(self, air)
        DistributedSmoothNodeAI.__init__(self, air)
        BattleAvatar.__init__(self)
        
        # Record the repository
        self.air = air
        # Initialize our empty DNA.
        self.dna = ToonDNA()

        self.hat = (0, 0, 0)
        self.glasses = (0, 0, 0)
        self.backpack = (0, 0, 0)
        self.shoes = (0, 0, 0)

        self.inventory = None
        self.trackArray = []
        self.trackBonusLevel = [0] * 9

        self.ghostMode = 0
        self.immortalMode = 0
        self.unlimitedGags = 0

        # Most of the time, this is false.
        # But during a battle round, we set this true, to tell the toon to temporarily accumulate
        # toonups beyond full health (and not to broadcast current hp to the client), so that it can be fixed up after
        # the battle round is over.
        self.hpOwnedByBattle = 0
        self.hpAdjustBattle = 0

        self.clubName = ''
        self.clubColor = 1000

        self.equippedItems: List[InventoryItem] = []
    
    def delete(self) -> None:
        del self.dna
        ModifiableDOAI.cleanup(self)
        self.cleanupBattle()
        DistributedSmoothNodeAI.delete(self)
        DistributedAvatarAI.delete(self)

    def announceGenerate(self):
        super().announceGenerate()
        self.hookCallbackToModifier(
            *HP_MODIFIERS,
            method=self.toonUp,
            extraArgs=[0],
        )
    
    def b_setDNAString(self, string):
        self.d_setDNAString(string)
        self.setDNAString(string)

    def d_setDNAString(self, string):
        self.sendUpdate('setDNAString', [string])

    def setDNAString(self, string):
        self.dna.makeFromNetString(string)

    def getDNAString(self):
        """
        Function:    retrieve the dna information from this suit, called
                     whenever a client needs to create this suit
        Returns:     netString representation of this suit's dna
        """
        return self.dna.makeNetString()

    def getStyle(self):
        # Returns the dna.  This mimicks a similar function on Avatar.py.
        return self.dna
    
    def b_setAnimState(self, animName, animMultiplier):
        self.setAnimState(animName, animMultiplier)
        self.d_setAnimState(animName, animMultiplier)

    def d_setAnimState(self, animName, animMultiplier):
        timestamp = globalClockDelta.getRealNetworkTime()
        self.sendUpdate("setAnimState", [animName, animMultiplier, timestamp])
        
    def setAnimState(self, animName, animMultiplier, timestamp=0):
        self.animName = animName
        self.animMultiplier = animMultiplier

    def b_receiveChatMessage(self, channelId: int, modifier: int, contentTypeId: int, content: str, message: ChatMessage):
        self.d_receiveChatMessage(channelId, modifier, contentTypeId, content)
        self.receiveChatMessage(message)

    def d_receiveChatMessage(self, channelId: int, modifier: int, contentTypeId: int, content: str):
        self.sendUpdate("receiveChatMessage", [channelId, modifier, contentTypeId, content])

    def receiveChatMessage(self, message: ChatMessage):
        pass

    def b_setExperience(self, experience):
        self.d_setExperience(experience)
        self.setExperience(experience)

    def d_setExperience(self, experience):
        self.sendUpdate('setExperience', [experience])

    def setExperience(self, experience):
        self.experience = Experience(*experience)

    def getExperience(self):
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                e = Experience()
                e.maxOut()
                return e
        return self.experience

    def b_setInventory(self, inventory):
        self.setInventory(inventory)
        self.d_setInventory(self.getInventory())

    def d_setInventory(self, inventory):
        self.sendUpdate('setInventory', [inventory])

    def setInventory(self, inventoryNetString):
        if self.inventory:
            # Update the inventory
            self.inventory.updateInvString(inventoryNetString)
        else:
            self.inventory = GagInventoryBase(self, inventoryNetString)

        # here we look to see if new gags have been added
        emptyInv = GagInventoryBase(self)
        emptyString = emptyInv.makeNetString()
        lengthMatch = len(inventoryNetString) - len(emptyString)
        if lengthMatch != 0:
            # Moving from 7 tracks and 6 levels to 7 tracks and 7 levels
            if len(inventoryNetString) == 56:
                oldTracks = 8
                oldLevels = 7
            elif len(inventoryNetString) == 64:
                oldTracks = 8
                oldLevels = 8
            else:
                # flags for when the solution is unknown
                oldTracks = 0
                oldLevels = 0

            if oldTracks == 0 and oldLevels == 0:
                # if no handcoded solution exists we reset the toon's inventory and give them
                # a restock, only including gags you can buy in the shop
                self.notify.warning('resetting invalid inventory to MAX on toon: %s' % self.doId)
                self.inventory.zeroInv()
                self.inventory.maxOutInv(1)
            else:
                # handles the conversion for known solutions
                newInventory = GagInventoryBase(self)
                oldList = emptyInv.makeFromNetStringForceSize(inventoryNetString, oldTracks, oldLevels)
                for indexTrack in range(0, oldTracks):
                    for indexGag in range(0, oldLevels):
                        newInventory.addItems(indexTrack, indexGag, oldList[indexTrack][indexGag])
                self.inventory.unload()
                self.inventory = newInventory
            self.d_setInventory(self.getInventory())
        emptyInv.unload()
        del emptyInv

    def getInventory(self):
        """
        :return: the inventory formatted for the net, not directly usable.
        """
        return self.inventory.makeNetString()

    def b_setMaxCarry(self, maxCarry):
        self.setMaxCarry(maxCarry)
        self.d_setMaxCarry(maxCarry)

    def d_setMaxCarry(self, maxCarry):
        self.sendUpdate('setMaxCarry', [maxCarry])

    def setMaxCarry(self, maxCarry):
        self.maxCarry = maxCarry

    def getMaxCarry(self):
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                return 100
        return self.maxCarry

    def getTrueMaxCarry(self):
        return self.maxCarry

    def b_setTrackAccess(self, trackArray):
        self.setTrackAccess(trackArray)
        self.d_setTrackAccess(trackArray)

    def d_setTrackAccess(self, trackArray):
        self.sendUpdate('setTrackAccess', [trackArray])

    def setTrackAccess(self, trackArray):
        self.trackArray = trackArray

    def getTrackAccess(self):
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                return [1 for _ in range(BattleGlobals.NUM_GAG_TRACKS)]
        return self.trackArray

    def hasGagTrack(self, track):
        return self.getTrackAccess()[track] == 1

    def b_setTrackBonusLevel(self, trackBonusLevelArray):
        self.setTrackBonusLevel(trackBonusLevelArray)
        self.d_setTrackBonusLevel(trackBonusLevelArray)

    def d_setTrackBonusLevel(self, trackBonusLevelArray):
        self.sendUpdate('setTrackBonusLevel', [trackBonusLevelArray])

    def setTrackBonusLevel(self, trackBonusLevelArray):
        self.trackBonusLevel = [8 if (trackBonusLevelArray or ([-1] * BattleGlobals.NUM_GAG_TRACKS + 1))[i] >= 1 else -1
                                for i in range(min(len(trackBonusLevelArray), BattleGlobals.NUM_GAG_TRACKS))]

    def getTrackBonusLevel(self, track=None):
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                return [8 for _ in range(BattleGlobals.NUM_GAG_TRACKS)] if track is None else 1
        return self.trackBonusLevel if track is None else self.trackBonusLevel[track]

    def checkGagBonus(self, track, level):
        return self.getTrackBonusLevel(track) >= 1

    def addTrackAccess(self, track):
        """
        Give this toon access to gags on this track
        """
        self.trackArray[track] = 1
        self.b_setTrackAccess(self.trackArray)

    def removeTrackAccess(self, track):
        """
        Deny this toon access to gags on this track
        """
        self.trackArray[track] = 0
        self.b_setTrackAccess(self.trackArray)

    def hasTrackAccess(self, track):
        """
        Can this toon use this track?

        :return: bool 0/1
        """
        for gagModifier in self.getModifiersOfType(ModifierType.GagsContentSync):
            if gagModifier.getForceMaxed():
                return 1
        if self.trackArray and track < len(self.trackArray):
            return self.trackArray[track]
        else:
            # RAU this case can happen if we are opening the closet of another toon
            return 0

    def getBattleId(self):
        if self.battleId >= 0:
            return self.battleId
        else:
            return 0

    def b_setBattleId(self, battleId):
        self.setBattleId(battleId)
        self.d_setBattleId(battleId)

    def d_setBattleId(self, battleId):
        if self.battleId >= 0:
            self.sendUpdate('setBattleId', [battleId])
        else:
            self.sendUpdate('setBattleId', [0])

    def setBattleId(self, battleId):
        self.battleId = battleId
    
    def toonUp(self, hpGained, quietly = 0, sendTotal = 1):
        """
        Adds the indicated hit points to the avatar's total.

        :param int | bool quietly: if 0, numbers will fly out of his head;
        :param int sendTotal: if 1, the resulting hp value will be sent as well to ensure client and AI are in agreement.
         (w/o sendTotal, the client will do the arithmetic himself, and presumably will still arrive at the same value.)
        """
        # first clamp toonup to hp limit
        if hpGained > self.getMaxHp():
            hpGained = self.getMaxHp()

        # First, send the message to make the numbers fly out.
        if not quietly:
            self.sendUpdate('toonUp', [hpGained])

        # Then, we recompute the HP.

        # If hp is below zero, it means we're at a timeout in the playground, in which case we respect that it is below
        # zero until we get our head above water.
        # If our toonup takes us above zero, then pretend we started at zero in the first place, ignoring the timeout.
        if self.hp + hpGained <= 0:
            self.hp += hpGained
        else:
            self.hp = max(self.hp, 0) + hpGained

        clampedHp = min(self.hp, self.getMaxHp())
        if not self.hpOwnedByBattle:
            self.hp = clampedHp

        # Finally, send the new total to the client so he's with us.
        if sendTotal and not self.hpOwnedByBattle:
            self.d_setHp(clampedHp)

        # self.air.clubMgr.sendUpdate('clubAvHp', [self.doId, clampedHp])
    
    def takeDamage(self, hpLost, quietly = 0, sendTotal = 1):
        """
        Adds the indicated hit points to the avatar's total.

        If quietly is 0 (the default), numbers will fly out of his head;
        if sendTotal is 1 (the default), the resulting hp value will be sent as well to ensure client and AI are in agreement.
        (Without sendTotal, the client will do the arithmetic himself, and presumably will still arrive at the same value.)
        """
        if not self.immortalMode:
            # First, send the message to make the numbers fly out.
            if not quietly:
                self.sendUpdate('takeDamage', [hpLost])
            # Then, we recompute the HP.
            if hpLost > 0 and self.hp > 0:
                self.hp -= hpLost
                if self.hp <= 0:
                    # If you get killed, set your HP to -1 so you have
                    # a timeout in the safezone.
                    self.hp = -1
        if not self.hpOwnedByBattle:
            # We still need to check maxHp even in takeDamage(), since
            # we might have had self.hpOwnedByBattle set previously,
            # allowing the toon to go above maxHp for a time.
            self.hp = min(self.hp, self.getMaxHp())

            # Finally, send the new total to the client so he's with us.
            if sendTotal:
                self.d_setHp(self.hp)
    
    def showToonTip(self, _):
        pass

    def addStat(self, *args, **kwargs):
        pass

    def b_setEquippedItems(self, equippedItems: List[InventoryItem]):
        self.setEquippedItems(equippedItems)
        self.d_setEquippedItems(equippedItems)

    def d_setEquippedItems(self, equippedItems: List[InventoryItem]):
        self.sendUpdate('setEquippedItems', [InventoryItem.toStructList(equippedItems)])

    def setEquippedItems(self, equippedItems: List[InventoryItem]):
        self.equippedItems = equippedItems

    def getEquippedItems(self):
        return self.equippedItems

    def getEquippedItemsOfType(self, itemType: ItemType):
        equippedItems = self.getEquippedItems()
        equippedOfType = InventoryItem.findItemTypesFromItemList(itemType, equippedItems)

        return equippedOfType
