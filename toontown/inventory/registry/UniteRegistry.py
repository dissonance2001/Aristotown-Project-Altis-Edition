
from __future__ import annotations
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.base.ItemDefinition import ItemDefinition
from toontown.inventory.enums.ItemEnums import MaterialItemType, UniteItemType
from toontown.inventory.enums.RarityEnums import Rarity
from toontown.toonbase import ProcessGlobals
from typing import Dict, List
from enum import IntEnum

from toontown.inventory.registry.MaterialRegistry import MaterialItemDefinition

if ProcessGlobals.getCurrentProcess() == ProcessGlobals.Process.Client:
    from direct.interval.IntervalGlobal import *
    from toontown.battle import BattleParticles


class UniteItemDefinition(MaterialItemDefinition):
    """
    Definition structure for any type of unite.
    """

    def __init__(self,
                 value,
                 realtimeCooldown,
                 battleCooldown,
                 chatText='Toons of the world, Unite!',
                 radius=30,
                 **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.realtimeCooldown = realtimeCooldown
        self.battleCooldown = battleCooldown
        self.chatText = chatText
        self.radius = radius

    def getItemTypeName(self):
        return 'Unite'

    def getUniteValue(self):
        return self.value

    def getRealtimeCooldown(self):
        return self.realtimeCooldown

    def getBattleCooldown(self):
        return self.battleCooldown

    def getChatText(self):
        return self.chatText

    def getRadius(self):
        return self.radius

    def doEffect(self, speakingToon, nearbyToons):
        effect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
        fadeColor = VBase4(1, 0.5, 1, 1)

        recolorToons = Parallel()
        for toonId in nearbyToons:
            toon = base.cr.doId2do.get(toonId)
            if toon and (not toon.ghostMode):
                recolorToons.append(Func(toon.doResistanceSeq, fadeColor))

        i = Parallel(
            ParticleInterval(effect, speakingToon, worldRelative=0, duration=3, cleanup=True),
            Sequence(Wait(0.2), recolorToons),
            autoFinish=1
        )
        i.start()


# The registry dictionary for Unites.
UniteRegistry: Dict[IntEnum, UniteItemDefinition] = {
    UniteItemType.ToonUpLow: UniteItemDefinition(
        name="20% Toon-Up",
        description="A Unite phrase that will instantly heal the Toons around you for 20% of their max Laff.",
        rarity=Rarity.Uncommon,
        value=0.2,
        realtimeCooldown=60,
        battleCooldown=3,
        chatText="Toons of the world, Toon-Up!"
    ),
    UniteItemType.ToonUpMid: UniteItemDefinition(
        name="30% Toon-Up",
        description="A Unite phrase that will instantly heal the Toons around you for 30% of their max Laff.",
        rarity=Rarity.Uncommon,
        value=0.3,
        realtimeCooldown=90,
        battleCooldown=5,
        chatText="Toons of the world, Toon-Up!"
    ),
    UniteItemType.ToonUpHigh: UniteItemDefinition(
        name="40% Toon-Up",
        description="A Unite phrase that will instantly heal the Toons around you for 40% of their max Laff.",
        rarity=Rarity.Uncommon,
        value=0.4,
        realtimeCooldown=120,
        battleCooldown=7,
        chatText="Toons of the world, Toon-Up!"
    )
}


def validateUnite(item: InventoryItem) -> bool:
    return item.getItemSubtype() in UniteRegistry and item.getQuantity() > 0


def getDefs() -> List[UniteItemDefinition]:
    return list(UniteRegistry.values())


def getTypes() -> List[UniteItemType]:
    return list(UniteRegistry.keys())


def get(uniteType: IntEnum) -> UniteItemDefinition:
    return UniteRegistry[uniteType]
