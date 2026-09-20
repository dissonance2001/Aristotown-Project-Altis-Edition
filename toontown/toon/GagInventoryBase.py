from copy import deepcopy
from typing import Optional

from toontown.toonbase import ToontownGlobals
from toontown.clashbattle.battle.BattleGlobals import *
from toontown.toon.gui.ToonTipGlobals import TTE
from toontown.hood import ZoneUtil
from direct.showbase import DirectObject
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator


@DirectNotifyCategory()
class GagInventoryBase(DirectObject.DirectObject):
    def __init__(self, toon, invStr=None):
        """
        Create a default inv if no netString given, or create an inv from the given netString.
        We need the experience object of the toon to determine max number of an item and the maxHp
        to determine the total number of items.
        We get these both from the toon.

        :param Toon.Toon toon: Toon
        :param invStr: netString
        """
        self.toon = toon
        # check to see if config overrides exp
        if invStr is None:
            # create default lvl one inv
            self.inventory = []
            for track in range(0, len(Tracks)):
                level = []
                for thisLevel in range(0, len(Levels[track])):
                    level.append(0)
                self.inventory.append(level)
        else:
            # de-stringify the one that came in
            self.inventory = self.makeFromNetString(invStr)
        self.calcTotalProps()

    def unload(self):
        del self.toon

    def duplicate(self) -> 'GagInventoryBase':
        newInventory = GagInventoryBase(toon=self.toon)
        newInventory.inventory = deepcopy(self.inventory)
        return newInventory

    def __str__(self):
        """
        Inventory print function
        """
        retStr = 'totalProps: %d\n' % self.totalProps
        for track in range(0, len(Tracks)):
            retStr += Tracks[track] + ' = ' + str(self.inventory[track]) + '\n'
        return retStr

    def updateInvString(self, invString):
        inventory = self.makeFromNetString(invString)
        self.updateInventory(inventory)

    def updateInventory(self, inv):
        self.inventory = inv
        self.calcTotalProps()

    def makeNetString(self):
        """
        Make a network packet (netString) out of the inventory
        """
        dataList = self.inventory
        datagram = PyDatagram()
        for track in range(0, len(Tracks)):
            for level in range(0, len(Levels[track])):
                datagram.addUint8(dataList[track][level])
        dgi = PyDatagramIterator(datagram)
        return dgi.getRemainingBytes()

    def makeFromNetString(self, netString):
        """
        Make an inventory from a network packet
        """
        dataList = []
        dg = PyDatagram(netString)
        dgi = PyDatagramIterator(dg)
        for track in range(0, len(Tracks)):
            subList = []
            for level in range(0, len(Levels[track])):
                if dgi.getRemainingSize() > 0:
                    value = dgi.getUint8()
                else:
                    value = 0
                subList.append(value)

            dataList.append(subList)

        return dataList

    def makeFromNetStringForceSize(self, netString, numTracks, numLevels):
        """
        Make an inventory from a network packet
        """
        dataList = []
        dg = PyDatagram(netString)
        dgi = PyDatagramIterator(dg)
        for track in range(0, numTracks):
            subList = []
            for level in range(0, numLevels):
                if dgi.getRemainingSize() > 0:
                    value = dgi.getUint8()
                else:
                    value = 0
                subList.append(value)
            dataList.append(subList)
        return dataList

    # setters and getters

    def addItem(self, track, level):
        """
        Add an item to the given track and level

        :type track: int | str
        :type level: int
        """
        return self.addItems(track, level, 1)

    def addItems(self, track, level, amount):
        """
        Add amount of an item to the given track and level.

        :returns: total items in given level and track if successful, 0 if insufficient skill level, -1 if over item max,
        -2 if over total max.

        :type track: int | str
        :type level: int
        :type amount: int
        """
        if isinstance(track, str):
            track = Tracks.index(track)

        max = self.getMax(track, level)

        # check against current skill level
        if (not hasattr(self.toon, 'experience')) or (not hasattr(self.toon.experience, 'getExpLevel')):
            # deleted object
            return 0
        if not (self.toon.getExperience().getExpLevel(track) >= level and self.toon.hasTrackAccess(track)):
            # insufficient skill or no access to track
            return 0
        if self.numItem(track, level) > max - amount:
            # over item max
            return -1
        if not (self.totalProps + amount <= self.toon.getMaxCarry() or level > LAST_REGULAR_GAG_LEVEL):
            # over total max
            return -2

        self.inventory[track][level] += amount
        self.totalProps += amount
        return self.inventory[track][level]

    def addItemWithList(self, track, levelList):
        """
        This is for adding one new item for each of the new gags you earned on a track during a reward sequence.
        Generally, levelList will only contain one level, or no levels.

        :type track: int | str
        :type levelList: list[int]
        """
        for level in levelList:
            self.addItem(track, level)

    def numItem(self, track, level):
        """
        :return: the number of items in the given track and level

        :type track: int | str
        :type level: int
        """
        if isinstance(track, str):
            track = Tracks.index(track)
        if track > len(Tracks) - 1 or level > len(Levels):
            self.notify.warning("%s is using a gag that doesn't exist %s %s!" % (self.toon.doId, track, level))
            return -1
        return self.inventory[track][level]

    def useItem(self, track, level, fullRecalcProps: bool = True):
        """
        If possible, use one item of given track and level

        :type track: int | str
        :type level: int
        """
        if isinstance(track, str):
            track = Tracks.index(track)
        if self.numItem(track, level) > 0:
            self.inventory[track][level] -= 1
            if fullRecalcProps:
                self.calcTotalProps()
            else:
                # performant way to do it in case we're sure there's no issues
                self.totalProps -= 1
            return 1
        # check for cheaters
        elif self.numItem(track, level) == -1:
            return -1

    def setItem(self, track, level, amount):
        """
        Set the number of items directly.
        We should check validity here probably

        :type track: int | str
        :type level: int
        :type amount: int
        """
        if isinstance(track, str):
            track = Tracks.index(track)

        max = self.getMax(track, level)
        curAmount = self.numItem(track, level)

        # check against current skill level
        if self.toon.getExperience().getExpLevel(track) >= level:
            if amount <= max:
                if self.totalProps - curAmount + amount <= self.toon.getMaxCarry():
                    self.inventory[track][level] = amount
                    self.totalProps = self.totalProps - curAmount + amount
                    return self.inventory[track][level]
                else:
                    # over total max
                    return -2
            else:
                # over item max
                return -1
        else:
            # insufficient skill
            return 0

    def getMax(self, track, level, forcedCarryLimitLevel: Optional[int] = None):
        """
        :return: the maximum of an item of given track and level

        :type track: int | str
        :type level: int
        :param forcedCarryLimitLevel: Returns the max, but with a forced carry limit level.
        """
        if isinstance(track, str):
            track = Tracks.index(track)

        # find max for this track/level
        maxList = CarryLimits[track]

        try:
            # RAU we create a dummy DistributedToonAI when we abort from a building battle so experience may still be
            # None, if so, just return 0
            if self.toon.getExperience() is not None:
                gagLevel = forcedCarryLimitLevel or self.toon.getExperience().getExpLevel(track)
                return maxList[gagLevel][level]
        except:
            return 0
        return 0

    def calcTotalProps(self):
        """
        Tally the current total number of props
        """
        self.totalProps = 0
        for track in range(0, len(Tracks)):
            for level in range(0, len(Levels[track])):
                if level <= LAST_REGULAR_GAG_LEVEL:
                    self.totalProps += self.numItem(track, level)
        # No Gags Tip
        # self.toon.sendUpdate('requestToonTip', [TTE.TIP_EMPTY_GAGS])

    def countPropsInList(self, invList):
        totalProps = 0
        for track in range(len(Tracks)):
            for level in range(len(Levels[track])):
                if level <= LAST_REGULAR_GAG_LEVEL:
                    totalProps += invList[track][level]
        return totalProps

    def setToMin(self, newInventory):
        """
        Given a new proposed inventory, set each value of the current inventory to new value, only if it is lower.
        This is used by the AI when players attempt to delete items, to prevent cheating.
        """
        for track in range(len(Tracks)):
            for level in range(len(Levels[track])):
                self.inventory[track][level] = min(self.inventory[track][level], newInventory[track][level])
        self.calcTotalProps()

    def validateItemsBasedOnExp(self, newInventory, allowUber=0):
        if isinstance(newInventory, str):
            tempInv = self.makeFromNetString(newInventory)
        else:
            tempInv = newInventory
        for track in range(len(Tracks)):
            for level in range(len(Levels[track])):
                if tempInv[track][level] > self.getMax(track, level):
                    return 0
                if tempInv[track][level] > 0 and not self.toon.hasTrackAccess(track):
                    return 0
                if level > LAST_REGULAR_GAG_LEVEL and tempInv[track][level] > self.inventory[track][level] or allowUber:
                    return 0
        return 1

    def getMinCostOfPurchase(self, newInventory):
        # BUG : check items deleted
        return self.countPropsInList(newInventory) - self.totalProps

    def validatePurchase(self, newInventory, currentMoney, newMoney):
        """
        Given a new proposed inventory, and the number of money that was presumably used to purchase this new inventory,
        test for the validity of the purchase.
        If it is valid, then update the inventory and new money balance appropriately.
        """
        # Sanity check, you should not be able to make money during the purchase screen
        if newMoney > currentMoney:
            self.notify.warning('Somebody lied about their money! Rejecting purchase.')
            return 0

        newItemTotal = self.countPropsInList(newInventory)
        if newItemTotal > self.toon.getMaxCarry():
            self.notify.warning('Cannot carry %s items! Rejecting purchase.' % newItemTotal)
            return 0
        if not self.validateItemsBasedOnExp(newInventory):
            self.notify.warning('Somebody is trying to buy forbidden items! ' + 'Rejecting purchase.')
            return 0
        # The purchase is valid.
        self.updateInventory(newInventory)
        return 1

    def maxOutInv(self, filterUberGags=0):
        """
        Iterate over all the props we might be able to use, and keep adding props until we have reached our max.
        This is for debugging.
        """

        # First, add at least one gag at each level.
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                for level in range(len(Levels[track])):
                    if level <= LAST_REGULAR_GAG_LEVEL or not filterUberGags:
                        self.addItem(track, level)

        # Now, add from the top level down, so we end up with mostly higher-level gags.
        addedAnything = 1
        while addedAnything:
            addedAnything = 0
            result = 0
            for track in range(len(Tracks)):
                if self.toon.hasTrackAccess(track):
                    level = len(Levels[track]) - 1
                    if level > LAST_REGULAR_GAG_LEVEL and filterUberGags:
                        level = LAST_REGULAR_GAG_LEVEL
                    result = self.addItem(track, level)
                    level -= 1
                    while result <= 0 and level >= 0:
                        result = self.addItem(track, level)
                        level -= 1
                    if result > 0:
                        addedAnything = 1

        self.calcTotalProps()

    def NPCMaxOutInv(self, targetTrack=-1, maxLevelIndex=6):
        """
        Iterate over all the props we might be able to use, and keep adding props until we have reached our max.
        """
        result = 0
        # Used to set caps for unite restocks.
        amountRestocked = 0

        # Go through the highest level(s) of gags and add as many as possible, then move down to the next highest
        for level in range(maxLevelIndex, -1, -1):
            anySpotsAvailable = 1
            while anySpotsAvailable == 1:
                anySpotsAvailable = 0
                trackResults = []
                for track in range(len(Tracks)):
                    if targetTrack != -1 and targetTrack != track:
                        continue
                    result = self.addItem(track, level)
                    trackResults.append(result)
                    if result > 0:
                        amountRestocked += 1

                # See if we need to make another pass
                for res in trackResults:
                    if res > 0:
                        anySpotsAvailable = 1
            if result == -2:
                break

        self.calcTotalProps()

    def NPCLoadGagPreset(self, targetTrack=-1, maxLevelIndex=5):
        self.zeroInv()
        gagPreset = self.makeFromNetString(self.toon.getGagPreset())
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                for level in range(self.toon.getExperience().getExpLevel(track) + 1):
                    self.inventory[track][level] = gagPreset[track][level]
        self.calcTotalProps()

    def zeroInv(self, killUber=1):
        """
        Erase all our props.
        """
        for track in range(len(Tracks)):
            for level in range(LAST_REGULAR_GAG_LEVEL):
                self.inventory[track][level] = 0
            if killUber:
                self.inventory[track][LAST_REGULAR_GAG_LEVEL] = 0
            if self.inventory[track][LAST_REGULAR_GAG_LEVEL] > 1:
                self.inventory[track][LAST_REGULAR_GAG_LEVEL] = 1
        self.calcTotalProps()

    def zeroTrack(self, track, killUber=1):
        for level in range(LAST_REGULAR_GAG_LEVEL + 1):
            self.inventory[track][level] = 0
        if killUber:
            self.inventory[track][LAST_REGULAR_GAG_LEVEL] = 0
        if self.inventory[track][LAST_REGULAR_GAG_LEVEL] > 1:
            self.inventory[track][LAST_REGULAR_GAG_LEVEL] = 1
        self.calcTotalProps()

    def restockTrack(self,
                     track,
                     maxLevel: int = LAST_REGULAR_GAG_LEVEL,
                     amount: Optional[int] = 100,
                     reduceCarryLimits: bool = False,
                     removeExcess: bool = False) -> int:
        """
        Restocks a track in the inventory.

        :param track:    The track to restock.
        :param maxLevel: The level which to restock up to.
        :param amount:   The amount of gags to restore.
        :param reduceCarryLimits: Should the gag carry limits be equal to maxLevel?
        :param removeExcess:      Should this method be in charged of removing excess gags?
        :return: The amount of gags left over.
        """
        forcedCarryLimitLevel = maxLevel if reduceCarryLimits else self.toon.getExperience().getExpLevel(track)

        # Restock the track from the top going down.
        for level in range(maxLevel, -1, -1):
            # Any gags left?
            if amount <= 0:
                break

            # Get the values we have at this level.
            numItems = self.numItem(track=track, level=level)
            maxItems = self.getMax(track=track, level=level, forcedCarryLimitLevel=forcedCarryLimitLevel)

            # Do we have gags to add?
            itemsToAdd = maxItems - numItems

            # If we have too many items, we'll get rid of some if we're asked to.
            while itemsToAdd < 0 and removeExcess:
                # Use the item.
                self.useItem(track=track, level=level, fullRecalcProps=False)

                # Account for the difference.
                itemsToAdd += 1
                amount += 1

            # Break out of here if we're out of items.
            if itemsToAdd <= 0:
                continue

            # Attempt to add gags until something goes wrong.
            while itemsToAdd:
                # OK hopefully we can even add any gags
                if self.totalProps >= self.toon.getMaxCarry():
                    break

                # Add at this level.
                result = self.addItem(track=track, level=level)

                # If we failed, we break out of the loop.
                if result <= 0:
                    break

                # Add one item for this.
                itemsToAdd -= 1
                amount -= 1

                # If we're out of items, break out of the loop.
                if (itemsToAdd <= 0) or (amount <= 0):
                    break

        # Return the amount of gags we have left over.
        return amount

    def saveGagPreset(self):
        """
        Saves a new gag preset.
        """
        self.toon.saveNewGagPreset(self.makeNetString())

    def canToonLoadPreset(self):
        gagPreset = self.makeFromNetString(self.toon.getGagPreset())
        cost = self.getTotalCost(gagPreset)
        money = self.toon.getMoney()
        if money < cost:  # Toon doesn't have enough money
            return (False, cost)
        else:
            return (True, cost)

    def loadGagPreset(self):
        gagPreset = self.makeFromNetString(self.toon.getGagPreset())
        totalCost = self.getTotalCost(gagPreset)  # total bean cost
        if totalCost <= self.toon.getMoney():
            for track in range(len(Tracks)):
                if self.toon.hasTrackAccess(track):
                    for level in range(self.toon.getExperience().getExpLevel(track) + 1):
                        self.inventory[track][level] = gagPreset[track][level]
            self.toon.setMoney(self.toon.getMoney() - totalCost)
        self.calcTotalProps()

    def getTotalCost(self, gagPreset):
        cost = 0
        for track in range(len(Tracks)):
            if self.toon.hasTrackAccess(track):
                for level in range(self.toon.getExperience().getExpLevel(track) + 1):
                    cost += max(0, (gagPreset[track][level] - self.inventory[track][level]) * (level + 1))
        zone = self.toon.zoneId
        # Kinda hacky, would like to rework purchases at some point
        if ZoneUtil.getCanonicalBranchZone(zone) != ZoneUtil.getHoodId(zone):
            cost *= 2

        # Find out if they have a discount in their
        # current safezone.
        safezoneId = ZoneUtil.getSafeZoneId(self.toon.zoneId)
        if zone >= 61000:  # Trolley
            safezoneId = ZoneUtil.getSafeZoneId(base.cr.playGame.hood.hoodId)
        discount = self.toon.getPlaygroundGagDiscount(safezoneId)
        if discount:
            cost *= discount
        return math.ceil(cost)

    def _garbageInfo(self):
        """
        :return: ''
        """
        return ''
