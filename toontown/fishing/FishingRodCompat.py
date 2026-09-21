"""
FishingRodCompat.py

TEMPORARY compatibility shim.

Corporate Clash looks up rod stats (weight range, fish-rarity factor) through
its full inventory item-registry system (toontown.inventory.enums.ItemEnums,
toontown.inventory.registry.ItemTypeRegistry / FishingRodRegistry). That
system isn't wired up in Altis yet, so this module reproduces just the two
numbers FishGlobals.py actually needs per rod, using the same balancing
values Clash uses.

When Altis's real inventory/item system is ported in, replace the contents
of this file with:

    from toontown.inventory.enums.ItemEnums import FishingRodItemType
    from toontown.inventory.registry.ItemTypeRegistry import getItemDefinition as getRodDefinition

...and delete this file. Every other file in toontown/fishing imports the
rod enum and the lookup function from *this* module rather than from
toontown.inventory directly, specifically so that swap is a one-file change.
"""
from enum import IntEnum
from collections import namedtuple


class FishingRodItemType(IntEnum):
    """
    Item subtype enum for fishing rods. Values match Corporate Clash's
    toontown.inventory.enums.ItemEnums.FishingRodItemType so that save data
    / balancing stays consistent if the real inventory system is ported in
    later.
    """
    Cardboard = 1
    Twig = 2
    Bamboo = 3
    Hardwood = 4
    Steel = 5
    Gold = 6
    Platinum = 7


# Higher numbers mean the rare fish are even more rare.
# Kept identical to Corporate Clash's FishingRodRegistry.GlobalRarityDialBase.
GlobalRarityDialBase = 4.3

_RodStats = namedtuple(
    '_RodStats',
    ['weightRange', 'fishRarityFactor', 'castCost', 'beanBountyAmount', 'levelMinimum'],
)


class RodDefinition(_RodStats):
    """Minimal stand-in for Clash's FishingRodDefinition (ItemDefinition subclass).

    Only exposes the accessor methods FishGlobals.py actually calls.
    """

    def getWeightRange(self):
        return self.weightRange

    def getMinWeight(self):
        return self.weightRange[0]

    def getMaxWeight(self):
        return self.weightRange[1]

    def getFishRarityFactor(self):
        return self.fishRarityFactor

    def getCastCost(self):
        return self.castCost

    def getBeanBountyAmount(self):
        return self.beanBountyAmount

    def getLevelMinimum(self):
        return self.levelMinimum


# Stat values copied from Corporate Clash's FishingRodRegistry so catch odds
# and weight ranges behave identically to Clash out of the box.
_FishingRodStats = {
    FishingRodItemType.Cardboard: RodDefinition((0, 4), 1.0 / (GlobalRarityDialBase * 1), 1, 50, 0),
    FishingRodItemType.Twig: RodDefinition((1, 6), 1.0 / (GlobalRarityDialBase * 0.975), 2, 100, 10 - 1),
    FishingRodItemType.Bamboo: RodDefinition((2, 9), 1.0 / (GlobalRarityDialBase * 0.95), 3, 175, 20 - 1),
    FishingRodItemType.Hardwood: RodDefinition((3, 12), 1.0 / (GlobalRarityDialBase * 0.9), 4, 250, 30 - 1),
    FishingRodItemType.Steel: RodDefinition((4, 15), 1.0 / (GlobalRarityDialBase * 0.85), 5, 325, 40 - 1),
    FishingRodItemType.Gold: RodDefinition((5, 18), 1.0 / (GlobalRarityDialBase * 0.8), 6, 400, 50 - 1),
    FishingRodItemType.Platinum: RodDefinition((6, 20), 1.0 / (GlobalRarityDialBase * 0.75), 7, 500, 60 - 1),
}


def getRodDefinition(rodSubtype):
    """Drop-in replacement for ItemTypeRegistry.getItemDefinition(rodSubtype)."""
    return _FishingRodStats[FishingRodItemType(rodSubtype)]
