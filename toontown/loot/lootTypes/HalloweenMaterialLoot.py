"""
Material loot class.
"""
from toontown.loot.LootBase import LootBase
from toontown.toonbase.ToontownGlobals import HALLOWEEN_MIX_WINTER_HOLIDAY, HALLOWEEN, APRIL_FOOLS
import random


class HalloweenMaterialLoot(LootBase):
    """
    Gives a specified number of material stacks to the recipient.
    """

    def __init__(self, materialStacks):
        self.materialStacks = materialStacks

    def handleLoot(self, recipient) -> None:
        if not self.checkHolidays():
            return
        for stack in range(self.materialStacks):
            materialList = recipient.getUnmaxedMaterials()
            material = random.choice(materialList) if materialList else 0
            amount = random.randint(10, 20)
            recipient.addCraftMaterial(material, amount)

    def checkHolidays(self):
        for holiday in (HALLOWEEN_MIX_WINTER_HOLIDAY, HALLOWEEN, APRIL_FOOLS):
            if simbase.air.holidayManager.isHolidayRunning(holiday):
                return True
        return False

    def getName(self):
        return f'{self.materialStacks} Bundles of Materials'

    def avHasLoot(self, av):
        return False

    def test(self):
        return True

    def __repr__(self):
        return f'{self.__class__.__name__}({self.materialStacks})'
