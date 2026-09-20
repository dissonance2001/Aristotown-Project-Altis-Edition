"""
The LootContainer module.
This is simply a Loot drop that will contain multiple other loot drops inside of it
It has a friendly name to identify itself.
"""
from typing import List

from toontown.loot.LootBase import LootBase


class LootContainer(LootBase):
    """
    A container that holds multiple other kinds of loot inside of it.
    """

    def __init__(self, lootList: List[LootBase], friendlyName: str):
        self.lootList = lootList
        self.friendlyName = friendlyName

    def handleLoot(self, recipient) -> None:
        [lootEntry.handleLoot(recipient) for lootEntry in self.lootList]

    def avHasLoot(self, av):
        return all([lootEntry.avHasLoot(av) for lootEntry in self.lootList])

    def test(self):
        return all([lootEntry.test() for lootEntry in self.lootList])

    def getName(self):
        return self.friendlyName

    def __repr__(self):
        return f'{self.__class__.__name__}({[repr(lootEntry) for lootEntry in self.lootList]})'
