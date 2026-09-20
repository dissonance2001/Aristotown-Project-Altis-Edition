"""
Inventory loot class
"""
from enum import IntEnum

from toontown.inventory.base.Inventory import Inventory
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.registry import ItemTypeRegistry
from toontown.loot.LootBase import LootBase


class InventoryLoot(LootBase):
    """
    Gives an inventory item to the recipient.
    """

    def __init__(self, itemSubtype: IntEnum, quantity: int = 1):
        self.itemSubtype = itemSubtype
        self.quantity = quantity

    def getItemDefinition(self):
        return ItemTypeRegistry.getItemDefinition(self.itemSubtype)

    def handleLoot(self, recipient) -> None:
        recipient.addItem(self.itemSubtype, self.quantity)

    def getName(self):
        item = InventoryItem.fromSubtype(self.itemSubtype, self.quantity)
        return self.getItemDefinition().getRewardName(item)

    def avHasLoot(self, av):
        inventory: Inventory = av.getHammerspace()
        inventoryItem = inventory.findItems(self.itemSubtype)
        if inventoryItem:
            newItem = InventoryItem.fromSubtype(self.itemSubtype, quantity=self.quantity)
            if inventory.cache.getItemsOfSubtype(self.itemSubtype):
                return True
            if not inventory.canAddItem(newItem):
                return True

        return False

    def test(self):
        # I don't know what to test this for right now so oh well
        return True

    def __repr__(self):
        return f'{self.__class__.__name__}({self.itemSubtype}) [Quantity: {self.quantity}]'
