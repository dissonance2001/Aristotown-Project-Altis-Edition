"""
This module defines the behavior for how each ItemType reacts in an inventory.
"""
from __future__ import annotations
from toontown.inventory.base.InventoryItemBehavior import InventoryItemBehavior, EquipAction
from toontown.inventory.enums.ItemEnums import ItemType


__InventoryItemBehaviorDefinitions = {

    ### Cosmetics ###
    ItemType.Cosmetic_Clothing_Top:    InventoryItemBehavior(canEquip=True, minEquipped=1, maxEquipped=1),
    ItemType.Cosmetic_Clothing_Bottom:   InventoryItemBehavior(canEquip=True, minEquipped=1, maxEquipped=1),
    ItemType.Cosmetic_Hat:      InventoryItemBehavior(canEquip=True, maxEquipped=3),
    ItemType.Cosmetic_Glasses:  InventoryItemBehavior(canEquip=True, maxEquipped=1),
    ItemType.Cosmetic_Backpack: InventoryItemBehavior(canEquip=True, maxEquipped=1),
    ItemType.Cosmetic_Shoes:    InventoryItemBehavior(canEquip=True, maxEquipped=1),
    ItemType.Cosmetic_Neck:     InventoryItemBehavior(canEquip=True, maxEquipped=1),

    ### Social ###
    ItemType.Social_CheesyEffect:    InventoryItemBehavior(canEquip=True, forceEquipOnAdd=True, maxEquipped=1),
    ItemType.Social_CustomSpeedchat: InventoryItemBehavior(canEquip=True, forceEquipOnAdd=True, maxEquipped=20),
    ItemType.Social_ChatStickers:    InventoryItemBehavior(canEquip=True, forceEquipOnAdd=True, maxEquipped=32),
    ItemType.Social_NametagFont:     InventoryItemBehavior(canEquip=True, forceEquipOnAdd=True, minEquipped=1, maxEquipped=1),
    ItemType.Social_Emote:           InventoryItemBehavior(canEquip=True, forceEquipOnAdd=True, maxEquipped=20),

    ### Profile Items ###
    ItemType.Profile_Nameplate:  InventoryItemBehavior(canEquip=True, minEquipped=1, maxEquipped=1),
    ItemType.Profile_Background: InventoryItemBehavior(canEquip=True, minEquipped=1, maxEquipped=1),
    ItemType.Profile_Pose:       InventoryItemBehavior(canEquip=True, minEquipped=1, maxEquipped=1),

    ### Fishing ###
    ItemType.Fishing_Rod:    InventoryItemBehavior(canEquip=True, forceEquipOnAdd=True, minEquipped=1, maxEquipped=1),

    ### Furniture ###
    ItemType.Estate_Furniture:   InventoryItemBehavior(canEquip=False, stackSize=999),
    ItemType.Estate_Style: InventoryItemBehavior(canEquip=False, stackSize=999),
    ItemType.Estate_Texture: InventoryItemBehavior(canEquip=False, stackSize=999),
    ItemType.Estate_Ticket: InventoryItemBehavior(canEquip=False, stackSize=1, maxSubtypeQuantity=999),

    ### Consumables ###
    ItemType.Consumable_Boosters: InventoryItemBehavior(canEquip=True, equipAction=EquipAction.BOOSTER, maxSubtypeQuantity=999),

    ### Misc ###
    ItemType.Material: InventoryItemBehavior(stackSize=999_999_999),
    ItemType.Unite: InventoryItemBehavior(stackSize=999_999_999),
    ItemType.IOU: InventoryItemBehavior(stackSize=999_999_999),
    ItemType.Music_Disc: InventoryItemBehavior(),
}


def getInventoryItemBehaviorDefinition(itemType: ItemType) -> InventoryItemBehavior:
    assert itemType in __InventoryItemBehaviorDefinitions, \
           f"Undefined inventory item behavior for {itemType}."
    return __InventoryItemBehaviorDefinitions.get(itemType)
