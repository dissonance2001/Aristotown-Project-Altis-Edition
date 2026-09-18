
from __future__ import annotations
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.base.ItemDefinition import ItemDefinition
from toontown.inventory.enums.ItemEnums import IOUItemType
from toontown.inventory.enums.RarityEnums import Rarity
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.toon.npc.NPCToonConstants import NPCToonID
from toontown.toonbase import TTLocalizer
from typing import Dict, Optional
from enum import IntEnum

from toontown.inventory.registry.MaterialRegistry import MaterialItemDefinition


class IOUItemDefinition(MaterialItemDefinition):
    """
    Definition structure for any type of IOU.
    """

    def __init__(self,
                 gagTrack: AttackEnum | int,
                 uses: int,
                 boost: int,
                 npcId: NPCToonID,
                 stars: int,
                 **kwargs):
        super().__init__(**kwargs)
        self.gagTrack = gagTrack
        self.uses = uses
        self.boost = boost
        self.npcId = npcId
        self.stars = stars

    def getItemTypeName(self):
        return 'IOU'

    def getGagTrack(self) -> AttackEnum:
        return self.gagTrack

    def getUses(self) -> int:
        return self.uses

    def getBoost(self) -> int:
        return self.boost

    def getNpcId(self) -> NPCToonID:
        return self.npcId

    def getStars(self) -> int:
        return self.stars

    def getItemTypeDescriptionInfo(self, item: Optional[InventoryItem] = None) -> str:
        boostTerm = {AttackEnum.TOON_HEAL: 'Healing', AttackEnum.TOON_LURE: 'Knockback'}.get(self.getGagTrack(), 'Damage')
        return f"{boostTerm} Boost: +{self.getBoost()}\nUses: {self.getUses()}"

    # Override for auto generated names and descriptions

    def getName(self, item: Optional[InventoryItem] = None) -> str:
        gagTrack = 'Global' if self.getGagTrack() == -1 else f"{TTLocalizer.BattleGlobalTracksUpper[self.getGagTrack()]}"
        return f"{self.getStars()}-Star {gagTrack} IOU"

    def getDescription(self) -> str:
        gagTrack = 'all' if self.getGagTrack() == -1 else TTLocalizer.BattleGlobalTracksUpper[self.getGagTrack()]
        return f"An IOU that boosts {gagTrack} Gags"


# The registry dictionary for IOUs.
IOURegistry: Dict[IntEnum, IOUItemDefinition] = {
    # region Toon-Up
    IOUItemType.ToonUpThreeStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_HEAL,
        uses=3,
        boost=25,
        npcId=NPCToonID.MadamChuckle,
        stars=3,
    ),
    IOUItemType.ToonUpFourStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_HEAL,
        uses=2,
        boost=35,
        npcId=NPCToonID.DaffyDon,
        stars=4,
    ),
    IOUItemType.ToonUpFiveStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_HEAL,
        uses=1,
        boost=60,
        npcId=NPCToonID.Flippy,
        stars=5,
    ),
    # endregion
    # region Trap
    IOUItemType.TrapThreeStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_TRAP,
        uses=3,
        boost=65,
        npcId=NPCToonID.Will,
        stars=3,
    ),
    IOUItemType.TrapFourStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_TRAP,
        uses=2,
        boost=90,
        npcId=NPCToonID.Penny_01,
        stars=4,
    ),
    IOUItemType.TrapFiveStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_TRAP,
        uses=1,
        boost=170,
        npcId=NPCToonID.Clara,
        stars=5,
    ),
    # endregion
    # region Lure
    IOUItemType.LureThreeStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_LURE,
        uses=3,
        boost=15,
        npcId=NPCToonID.StinkyNed,
        stars=3,
    ),
    IOUItemType.LureFourStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_LURE,
        uses=2,
        boost=20,
        npcId=NPCToonID.NancyGas,
        stars=4,
    ),
    IOUItemType.LureFiveStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_LURE,
        uses=1,
        boost=35,
        npcId=NPCToonID.LilOldman,
        stars=5,
    ),
    # endregion
    # region Sound
    IOUItemType.SoundThreeStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_SOUND,
        uses=3,
        boost=15,
        npcId=NPCToonID.BarbaraSeville,
        stars=3,
    ),
    IOUItemType.SoundFourStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_SOUND,
        uses=2,
        boost=20,
        npcId=NPCToonID.SidSonata,
        stars=4,
    ),
    IOUItemType.SoundFiveStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_SOUND,
        uses=1,
        boost=35,
        npcId=NPCToonID.MoeZart,
        stars=5,
    ),
    # endregion
    # region Squirt
    IOUItemType.SquirtThreeStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_SQUIRT,
        uses=3,
        boost=25,
        npcId=NPCToonID.SidSquid,
        stars=3,
    ),
    IOUItemType.SquirtFourStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_SQUIRT,
        uses=2,
        boost=35,
        npcId=NPCToonID.SanjaySplash,
        stars=4,
    ),
    IOUItemType.SquirtFiveStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_SQUIRT,
        uses=1,
        boost=60,
        npcId=NPCToonID.SharkyJones,
        stars=5,
    ),
    # endregion
    # region Zap
    IOUItemType.ZapThreeStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_ZAP,
        uses=3,
        boost=25,
        npcId=NPCToonID.DentistDaniel,
        stars=3,
    ),
    IOUItemType.ZapFourStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_ZAP,
        uses=2,
        boost=35,
        npcId=NPCToonID.ElectraEel,
        stars=4,
    ),
    IOUItemType.ZapFiveStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_ZAP,
        uses=1,
        boost=60,
        npcId=NPCToonID.Nat,
        stars=5,
    ),
    # endregion
    # region Throw
    IOUItemType.ThrowThreeStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_THROW,
        uses=3,
        boost=30,
        npcId=NPCToonID.Cleff,
        stars=3,
    ),
    IOUItemType.ThrowFourStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_THROW,
        uses=2,
        boost=40,
        npcId=NPCToonID.CindySprinkles,
        stars=4,
    ),
    IOUItemType.ThrowFiveStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_THROW,
        uses=1,
        boost=70,
        npcId=NPCToonID.Pierce,
        stars=5,
    ),
    # Unobtainable Throw IOU
    IOUItemType.ThrowThreeStar_Unobtainable: IOUItemDefinition(
        rarity=Rarity.VeryRare,
        gagTrack=AttackEnum.TOON_THROW,
        uses=3,
        boost=30,
        npcId=NPCToonID.NedSlinger,
        stars=3,
    ),
    # endregion
    # region Drop
    IOUItemType.DropThreeStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_DROP,
        uses=3,
        boost=35,
        npcId=NPCToonID.ClumsyNed,
        stars=3,
    ),
    IOUItemType.DropFourStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_DROP,
        uses=2,
        boost=45,
        npcId=NPCToonID.FranzNeckvein,
        stars=4,
    ),
    IOUItemType.DropFiveStar: IOUItemDefinition(
        rarity=Rarity.Uncommon,
        gagTrack=AttackEnum.TOON_DROP,
        uses=1,
        boost=80,
        npcId=NPCToonID.BarnacleBessie,
        stars=5,
    ),
    # endregion
    # region Misc
    IOUItemType.AllBoost: IOUItemDefinition(
        rarity=Rarity.Common,
        gagTrack=-1,
        uses=1,
        boost=15,
        npcId=NPCToonID.Rain,
        stars=3,
    ),
    # endregion
}
