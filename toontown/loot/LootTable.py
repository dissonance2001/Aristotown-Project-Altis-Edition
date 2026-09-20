"""
File containing all classes related to loot tables, including LootEntry and LootTable.
"""
from __future__ import annotations
import random
from enum import Enum, auto
from typing import List
from toontown.loot.LootBase import LootBase


class LootRarity(Enum):
    Guaranteed = auto()
    Common = auto()
    Uncommon = auto()
    Rare = auto()
    VeryRare = auto()
    Legendary = auto()


# region -=- Base Classes -=-
class LootEntry:
    """
    Represents an entry in a LootTable.
    Gives the chance of a successful roll and handles giving out the loot object.
    """
    def __init__(self, loot: LootBase | list[LootBase], chance: float, rarity: LootRarity = LootRarity.Common):
        """
        :param loot: Loot to be given on success.
        :param chance: Chance for a success.
        :param rarity: Rarity indicator, common by default. Purely for client display.
        """
        self.loot: LootBase = loot
        self.chance: float = chance
        self.rarity: LootRarity = rarity

    def getChance(self, roller, extraArgs=None) -> float:
        """
        Gives chance for this entry to be successfully rolled.
        :param roller: The player that is rolling for this entry.
        :param extraArgs: Potential extra arguments that have been passed to the loot.
        :return: Chance of successful roll.
        """
        return self.chance

    def handleSuccess(self, winner) -> None:
        """
        Called on successful loot roll, gives the loot to a recipient.
        :param winner: The player that succeeded at rolling for this entry.
        """
        if isinstance(self.loot, (tuple, list)):
            for loot in self.loot:
                loot.handleLoot(winner)
        else:
            self.loot.handleLoot(winner)

    @property
    def wantShow(self):
        """
        Returns if this loot should be shown to the client when it visualizes loot info
        """
        return True

    def test(self):
        """
        Makes sure the loot entry and everything associated with it is defined properly.
        :return: Returns True if everything checks out. False otherwise.
        """
        if isinstance(self.loot, (tuple, list)):
            for loot in self.loot:
                if not loot.test():
                    return False
        else:
            if not self.loot.test():
                return False
        if self.chance < 0 or self.chance > 1:
            return False
        return True


class LootTable:
    """
    Contains possible loot drops and their percentage chance to drop.
    Can either roll each potential loot independently for the chance to drop each one,
    or weight each item based on their chance and output one loot on roll.
    """
    def __init__(self, entries: List[LootEntry] = None, independentRolls: bool = True):
        """
        :param entries: Loot entries to roll on.
        :param independentRolls: Whether each individual entry should be rolled separately or not.
        """
        self.entries = entries or []
        self.independentRolls = independentRolls

    def rollTable(self, roller, extraArgs=None):
        """
        Roll the loot table for a player.
        :param roller: The player that is rolling for this table.
        """
        if self.independentRolls:
            for entry in self.entries:
                rollResult = random.random()
                if rollResult < entry.getChance(roller, extraArgs=extraArgs):
                    entry.handleSuccess(roller)
        else:
            # TODO: Add weighting table based on chances and outputting one result.
            raise NotImplementedError

    def addEntry(self, entry: LootEntry):
        self.entries.append(entry)

    def test(self):
        """
        Makes sure the loot entry and everything associated with it is defined properly.
        :return: Returns True if everything checks out. False otherwise.
        """
        for entry in self.entries:
            if not entry.test():
                return False
        return True
# endregion


# region Variant Classes
class PityLootEntry(LootEntry):
    """
    LootEntry that increases it's chance based on some field on the player.
    """
    def __init__(self, loot: LootBase | list[LootBase], chance: float, chancePerPity: float, rarity: LootRarity = LootRarity.Common):
        super().__init__(loot, chance, rarity=rarity)
        self.chancePerPity = chancePerPity

    def getPityValue(self, pitiableBeing, extraArgs=None) -> int:
        """
        :param pitiableBeing: The player that we are checking to see how much we should pity them.
        :return: Amount of pity we should give them.
        """
        raise NotImplementedError

    def getChance(self, roller, extraArgs=None) -> float:
        return self.chance + (self.chancePerPity * self.getPityValue(roller, extraArgs=extraArgs))



class HolidayLootEntry(LootEntry):
    """
    LootEntry that is available based on a given active Holiday ID.
    """
    def __init__(self, loot: LootBase | list[LootBase], chance: float, holidayIds: List[int], rarity: LootRarity = LootRarity.Common):
        super().__init__(loot, chance, rarity=rarity)
        self.holidayIds = holidayIds

    @property
    def wantShow(self):
        return self.checkActiveHoliday()

    def checkActiveHoliday(self):
        for holiday in self.holidayIds:
            if base.cr.newsManager.isHolidayRunning(holiday):
                return True
        return False


class DefeatPityLootEntry(PityLootEntry):
    """
    PityLootEntry that's chance is based on how many times the roller has defeated an enemy.
    """
    def __init__(self, loot: LootBase | list[LootBase], chance: float, chancePerPity: float, enemyName: str, rarity: LootRarity = LootRarity.Common):
        super().__init__(loot, chance, chancePerPity, rarity=rarity)
        self.enemyName = enemyName

    def getPityValue(self, pitiableBeing, extraArgs=None) -> int:
        bonusAmount = 0
        if extraArgs is not None:
            bonusAmount = extraArgs[0]

        return pitiableBeing.suitGalleryDict.get(self.enemyName, 0) + bonusAmount


class DefeatAmountLootEntry(LootEntry):
    """
    LootEntry that either has a 0% chance or a 100% chance to drop something based on kill count.
    """
    def __init__(self, loot: LootBase | list[LootBase], enemyAmount: int, enemyName: str):
        super().__init__(loot, chance=0, rarity=LootRarity.Common)
        self.enemyAmount = enemyAmount
        self.enemyName = enemyName

    def getKillCount(self, pitiableBeing, extraArgs=None) -> int:
        bonusAmount = 0
        if extraArgs is not None:
            bonusAmount = extraArgs[0]

        # We add one to this because loot drops are checked before
        # the user's kill count is updated
        return pitiableBeing.suitGalleryDict.get(self.enemyName, 0) + 1 + bonusAmount

    def getChance(self, roller, extraArgs=None) -> float:
        return float(bool(self.getKillCount(roller, extraArgs=extraArgs) >= self.enemyAmount))
# endregion
