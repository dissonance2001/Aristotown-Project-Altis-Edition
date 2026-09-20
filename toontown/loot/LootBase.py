"""
The module class for LootBase.
When you make a new Loot class, make a file in lootTypes and add it to the __init__ file there.
"""


class LootBase:
    """
    The base class for Loot.
    """
    LootIcon = 'reward_packageIcon'

    def handleLoot(self, recipient) -> None:
        """
        Gives a player this loot.
        :param recipient: The player that will receive the loot.
        """
        raise NotImplementedError

    def getName(self):
        return 'Loot'

    def avHasLoot(self, av):
        return False

    def test(self):
        """
        Makes sure the loot and everything associated with it is defined properly.
        :return: Returns True if everything checks out. False otherwise.
        """
        raise NotImplementedError
