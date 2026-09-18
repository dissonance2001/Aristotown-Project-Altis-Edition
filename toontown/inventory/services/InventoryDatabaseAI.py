from direct.showbase.DirectObject import DirectObject

from toontown.inventory.base import DefaultInventory
from toontown.inventory.base.Inventory import Inventory

from typing import TYPE_CHECKING, Optional
from pymongo.collection import Collection


if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


class InventoryDatabaseAI(DirectObject):
    """
    Provides an interface for direct query & interfaces for Toon inventories.
    Uses a cache local to the district for inventories, though
    subclasses may implement their own DB interface.
    """

    AUTOSAVE_DURATION = 30

    def __init__(self, air):
        """:type air: ToontownAIRepository"""
        self.air = air  # type: ToontownAIRepository
        self.inventoryCache = {}

    """
    Inventory Saving
    """

    def startInventorySaving(self, avId: int):
        """
        Starts a task to save inventory changes to DB.
        """
        self.doMethodLater(
            delayTime=self.AUTOSAVE_DURATION,
            funcOrTask=self.__inventorySaveTask,
            name=self.inventorySaveTaskName(avId),
            extraArgs=[avId],
        )

    def endInventorySaving(self, avId: int, inventory: Inventory):
        """
        Ends inventory auto-saving.
        """
        self.__doInventorySave(avId, inventory)
        self.removeTask(self.inventorySaveTaskName(avId))

    def __inventorySaveTask(self, avId: int):
        # Get the av.
        av = self.air.doId2do.get(avId, None)
        if av is None:
            # The av is gone -- end the task.
            return

        # Find the av's inventory.
        inventory = self.air.inventoryManager.getInventory(avId)
        if not inventory:
            return

        # Has the av hammerspace updated recently?
        if inventory.cache.getTimeSinceModified() < self.AUTOSAVE_DURATION:
            self.__doInventorySave(avId, inventory)

        # Re-do the task.
        self.startInventorySaving(avId)

    def __doInventorySave(self, avId: int, inventory: Inventory):
        self.saveInventory(avId, inventory)

    @staticmethod
    def inventorySaveTaskName(avId: int):
        return f'InventoryDatabaseAI-Autosave-{avId}'

    """
    Inventory Interface
    """

    def queryInventory(self, avId: int, create: bool = False) -> Optional[Inventory]:
        """
        Queries for an avatar's inventory.
        """
        if avId not in self.inventoryCache:
            if create:
                return self.makeInventory(avId, force=True)
            else:
                return None
        return self.inventoryCache.get(avId)

    def saveInventory(self, avId: int, inventory: Inventory) -> None:
        """
        Saves an avatar's inventory.
        """
        self.inventoryCache[avId] = inventory

    def makeInventory(self, avId: int, force: bool = False) -> Inventory:
        """
        Creates an avatar's default inventory.
        """
        if not force and avId in self.inventoryCache:
            raise AttributeError

        # Make default inventory.
        inventory = DefaultInventory.getDefaultInventory()
        self.inventoryCache[avId] = inventory
        return inventory