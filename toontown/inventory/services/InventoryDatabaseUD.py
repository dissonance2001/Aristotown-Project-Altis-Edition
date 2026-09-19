from direct.showbase.DirectObject import DirectObject

from toontown.inventory.base import DefaultInventory
from toontown.inventory.base.Inventory import Inventory

from typing import TYPE_CHECKING
from pymongo.collection import Collection

if TYPE_CHECKING:
    from toontown.uberdog.ToontownUberRepository import ToontownUberRepository


class InventoryDatabaseUD(DirectObject):
    """
    A stripped-down, read-only version of InventoryDatabaseAI for the
    Uberdog process. The AI repository's inventoryDb (InventoryMongoDatabaseAI)
    is not reachable from here -- the Uberdog runs as a separate process/
    repository -- so this queries the same Mongo 'inventory' collection
    directly using the Uberdog's own Mongo connection instead.

    Used by ClientServicesManagerUD to fetch a toon's equipped items when
    building the avatar-picker list (setAvatars), so the Pick-A-Toon /
    avatar-select screen can show the toon's actual equipped clothes and
    accessories.
    """

    def __init__(self, udr):
        """:type udr: ToontownUberRepository"""
        self.udr = udr  # type: ToontownUberRepository
        self.collection: Collection = self.udr.mongodb.inventory
        self.defaultInventory = DefaultInventory.getDefaultInventory()

    def queryInventory(self, avId: int) -> Inventory:
        """
        Queries for an avatar's inventory.
        """
        inventoryJson = self.collection.find_one({'_id': avId})
        if not inventoryJson:
            # No document found, assume default.
            return self.defaultInventory

        return Inventory.fromMongo(inventoryJson)
