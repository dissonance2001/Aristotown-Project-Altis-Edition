"""
This module defines the behavior for each inventory type.
"""
from __future__ import annotations
from toontown.inventory.base.InventoryBehavior import InventoryBehavior
from toontown.inventory.enums.InventoryEnums import InventoryType

__InventoryBehaviorDefinitions = {
    InventoryType.FullBehavior: InventoryBehavior(
        maxSize=999,
    ),
    InventoryType.Test: InventoryBehavior(
        maxSize=5,
    ),

    InventoryType.Player: InventoryBehavior(
        maxSize=5000,
        canSwapBetweenSameType=False,
    ),
    InventoryType.Chest: InventoryBehavior(
        maxSize=20,
        canAddItems=False,
        canDeleteItems=False,
        canSwapItemsIn=False,
        canEquipItems=False,
    ),
    InventoryType.Cache: InventoryBehavior(
        canAddItems=False,
        canDeleteItems=False,
        canEquipItems=False,
        canSwapItemsIn=False,
        canSwapBetweenSameType=False,
    ),
}

# NOTE: Clash gated a larger dev-realm inventory size here via RealmGlobals.getCurrentRealm().isDevRealm().
# Altis has no equivalent realm/environment concept, so this override was dropped.
# If Altis later adds a dev/staging flag, reintroduce an override on InventoryType.Player here.


def getInventoryBehaviorDefinition(inventoryType: InventoryType) -> InventoryBehavior:
    assert inventoryType in __InventoryBehaviorDefinitions, \
           f"Undefined inventory behavior for {inventoryType}."
    return __InventoryBehaviorDefinitions.get(inventoryType)
