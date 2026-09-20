from direct.showbase.DirectObject import DirectObject
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.level import Entity


@DirectNotifyCategory()
class SuitBattleCellAI(Entity.Entity, DirectObject):
    """
     SuitBattleCellAI(Entity.Entity)

    A battle cell on the street to be used for level suit battles, but as an AI representation.
    """
    def __init__(self, level=None, entId=None):
        Entity.Entity.__init__(self, level, entId)
        DirectObject.__init__(self)
        self.active = False

    def setActive(self, active) -> None:
        self.active = active

    def getActive(self) -> bool:
        return self.active
