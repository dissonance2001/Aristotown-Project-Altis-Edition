from direct.showbase.DirectObject import DirectObject
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.level import Entity


@DirectNotifyCategory()
class SuitPathPointAI(Entity.Entity, DirectObject):
    """
     SuitPathPointAI(Entity.Entity)

    A point on a suit's path that dictates where they move in a level environment, but as an AI representation.
    """
    def __init__(self, level=None, entId=None):
        Entity.Entity.__init__(self, level, entId)
        DirectObject.__init__(self)
        self.suitPathCollection = None

    def setSuitPathCollection(self, suitPathCollection):
        self.suitPathCollection = suitPathCollection

    def destroy(self):
        self.suitPathCollection = None
        Entity.Entity.destroy(self)
