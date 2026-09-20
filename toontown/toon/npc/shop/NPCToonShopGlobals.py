from __future__ import annotations
"""
Contains item catalogues and other global data for NPCs marked as ITEM_SELLER.
This allows any NPC to sell items with a generic interface.
"""

from toontown.toon.npc.NPCToonConstants import NPCToonID
from toontown.shop.base.ShopCategoryEnum import ShopCategoryEnum
from toontown.shop.item.InventoryShopItem import InventoryShopItem
from toontown.shop.item.FishingBucketUpgradeShopItem import FishingBucketUpgradeShopItem
from toontown.shop.base.ShopItemCatalogue import ShopItemCatalogue
from toontown.shop.base.ShopItemListing import ShopItemListing
from toontown.shop.cost.JellybeanPriceTag import JellybeanPriceTag
from toontown.shop.requirement.LevelPurchaseRequirement import LevelPurchaseRequirement
from toontown.shop.requirement.ActivityLevelPurchaseRequirement import ActivityLevelPurchaseRequirement
from toontown.shop.requirement.SuitDefeatPurchaseRequirement import SuitDefeatPurchaseRequirement

from toontown.toonbase import ToontownGlobals, TTLocalizer

from toontown.inventory.enums.ItemEnums import *

from toontown.utils import ColorHelper
from enum import auto
from panda3d.core import *


ShopItemsPerPage = 9


class NPCShopCategory(ShopCategoryEnum):
    """The current category of an NPC shop."""
    Social          = auto()
    Profile         = auto()
    Clothing        = auto()
    Booster         = auto()
    EstateKits      = auto()
    EstateFurniture = auto()
    Fishing         = auto()
    Racing          = auto()
    Battle          = auto()
    Upgrades        = auto()

    TTC  = auto()
    BB   = auto()
    YOTT = auto()
    DG   = auto()
    MML  = auto()
    TB   = auto()
    AA   = auto()
    DDL  = auto()


ShopCategoryToTitle = {
    NPCShopCategory.Social: 'Social',
    NPCShopCategory.Profile: 'Profile',
    NPCShopCategory.Clothing: 'Clothing',
    NPCShopCategory.Booster: 'Booster',
    NPCShopCategory.EstateKits: 'Estate Kits',
    NPCShopCategory.EstateFurniture: 'Furniture',
    NPCShopCategory.Fishing: 'Fishing',
    NPCShopCategory.Racing: 'Racing',
    NPCShopCategory.Battle: 'Battle',

    NPCShopCategory.TTC: TTLocalizer.lToontownCentral,
    NPCShopCategory.BB: TTLocalizer.lDonaldsDock,
    NPCShopCategory.YOTT: TTLocalizer.lYeOlde,
    NPCShopCategory.DG: TTLocalizer.lDaisyGardens,
    NPCShopCategory.MML: TTLocalizer.lMinniesMelodyland,
    NPCShopCategory.TB: TTLocalizer.lTheBrrrgh,
    NPCShopCategory.AA: TTLocalizer.lOutdoorZone,
    NPCShopCategory.DDL: TTLocalizer.lDonaldsDreamland,

    # This "Upgrades" category is purely for backend and is not meant to be displayed to the user.
    NPCShopCategory.Upgrades: '',
}


# region NPC Shop Catalogue Definitions
# Make sure to only define one "upgrade" item type per NPC if any

NPCShopItems: dict[NPCToonID, ShopItemCatalogue] = {
    # Tell Tale Carp, Fishing Shop
    NPCToonID.EdgarAllanPole: ShopItemCatalogue({
        NPCShopCategory.Fishing: ShopItemListing([
            InventoryShopItem(FishingRodItemType.Twig, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 10-1)),
            InventoryShopItem(FishingRodItemType.Bamboo, priceTags=JellybeanPriceTag(1250),
                              purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 20-1)),
            InventoryShopItem(FishingRodItemType.Hardwood, priceTags=JellybeanPriceTag(2500),
                              purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 30-1)),
            InventoryShopItem(FishingRodItemType.Steel, priceTags=JellybeanPriceTag(5000),
                              purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 40-1)),
            InventoryShopItem(FishingRodItemType.Gold, priceTags=JellybeanPriceTag(7500),
                              purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 50-1)),
            InventoryShopItem(FishingRodItemType.Platinum, priceTags=JellybeanPriceTag(10000),
                              purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 60-1)),
        ]),
        NPCShopCategory.Upgrades: ShopItemListing([
            FishingBucketUpgradeShopItem(upgradeAmount=10, minBucketAmount=20, priceTags=JellybeanPriceTag(500),
                                         purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 8-1)),
            FishingBucketUpgradeShopItem(upgradeAmount=10, minBucketAmount=30, priceTags=JellybeanPriceTag(1000),
                                         purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 16-1)),
            FishingBucketUpgradeShopItem(upgradeAmount=10, minBucketAmount=40, priceTags=JellybeanPriceTag(1500),
                                         purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 24-1)),
            FishingBucketUpgradeShopItem(upgradeAmount=10, minBucketAmount=50, priceTags=JellybeanPriceTag(2000),
                                         purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 32-1)),
            FishingBucketUpgradeShopItem(upgradeAmount=10, minBucketAmount=60, priceTags=JellybeanPriceTag(2500),
                                         purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 40-1)),
            FishingBucketUpgradeShopItem(upgradeAmount=10, minBucketAmount=70, priceTags=JellybeanPriceTag(3000),
                                         purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 48-1)),
            FishingBucketUpgradeShopItem(upgradeAmount=10, minBucketAmount=80, priceTags=JellybeanPriceTag(3500),
                                         purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 56-1)),
            FishingBucketUpgradeShopItem(upgradeAmount=10, minBucketAmount=90, priceTags=JellybeanPriceTag(4000),
                                         purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_FISHING, 64-1)),
        ]),
    }),
    # Toon Tunes, Music Disk Shop
    NPCToonID.JuneLoon: ShopItemCatalogue({
        NPCShopCategory.TTC: ShopItemListing([
            InventoryShopItem(MusicDiscItemType.Merc_Street_DuckShuffler, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('duckshfl', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Prethinker_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('prethink', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Prethinker_2, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('prethink', 5)),
        ]),
        NPCShopCategory.BB: ShopItemListing([
            InventoryShopItem(MusicDiscItemType.Merc_Street_DeepDiver, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('ddiver', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Rainmaker_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('rainmake', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Rainmaker_2, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('rainmake', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Rainmaker_3, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('rainmake', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Rainmaker_4, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('rainmake', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Rainmaker_5, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('rainmake', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Rainmaker_6, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('rainmake', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Rainmaker_7, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('rainmake', 5)),
        ]),
        NPCShopCategory.YOTT: ShopItemListing([
            InventoryShopItem(MusicDiscItemType.Merc_Street_Gatekeeper, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('gatekeep', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_WitchHunter_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('whunter', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_WitchHunter_2, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('whunter', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_WitchHunter_3, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('whunter', 5)),
        ]),
        NPCShopCategory.DG: ShopItemListing([
            InventoryShopItem(MusicDiscItemType.Merc_Street_Bellringer, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('bellring', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Multislacker_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('mslacker', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Multislacker_2, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('mslacker', 5)),
        ]),
        NPCShopCategory.MML: ShopItemListing([
            InventoryShopItem(MusicDiscItemType.Merc_Street_Mouthpiece, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('mouthp', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_MajorPlayer_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('mplayer', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_MajorPlayer_2, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('mplayer', 5)),
        ]),
        NPCShopCategory.TB: ShopItemListing([
            InventoryShopItem(MusicDiscItemType.Merc_Street_Firestarter, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('fires', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Plutocrat_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('pcrat', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Plutocrat_2, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('pcrat', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Plutocrat_3, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('pcrat', 5)),
        ]),
        NPCShopCategory.AA: ShopItemListing([
            InventoryShopItem(MusicDiscItemType.Merc_Street_Treekiller, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('treek', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_ChainsawConsultant_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('chainsaw', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_ChainsawConsultant_2, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('chainsaw', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_ChainsawConsultant_3, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('chainsaw', 5)),
        ]),
        NPCShopCategory.DDL: ShopItemListing([
            InventoryShopItem(MusicDiscItemType.Merc_Street_Featherbedder, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('fbed', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Pacesetter_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('psetter', 5)),
            InventoryShopItem(MusicDiscItemType.Merc_Pacesetter_2, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=SuitDefeatPurchaseRequirement('psetter', 5)),
        ]),
    }),
    # Professor Pete, Schoolhouse Furniture
    NPCToonID.ProfessorPete: ShopItemCatalogue({
        NPCShopCategory.EstateFurniture: ShopItemListing([
            InventoryShopItem(FurnitureItemType.Prop_Schoolhouse_Classroom_Desk_Student, priceTags=JellybeanPriceTag(150)),
            InventoryShopItem(FurnitureItemType.Prop_Schoolhouse_Classroom_Canvas, priceTags=JellybeanPriceTag(150)),
            InventoryShopItem(FurnitureItemType.Prop_Schoolhouse_Training_Bench, priceTags=JellybeanPriceTag(300),
                              purchaseReqs=LevelPurchaseRequirement(40 - 1)),
            InventoryShopItem(FurnitureItemType.Prop_Schoolhouse_Training_Watercooler, priceTags=JellybeanPriceTag(300),
                              purchaseReqs=LevelPurchaseRequirement(40 - 1)),
            InventoryShopItem(FurnitureItemType.Prop_Schoolhouse_Training_GagBarrel, priceTags=JellybeanPriceTag(300),
                              purchaseReqs=LevelPurchaseRequirement(40 - 1)),
            InventoryShopItem(FurnitureItemType.Prop_Schoolhouse_Training_Weights, priceTags=JellybeanPriceTag(300),
                              purchaseReqs=LevelPurchaseRequirement(40 - 1)),
            InventoryShopItem(FurnitureItemType.Prop_Schoolhouse_Basement_Chair_1, priceTags=JellybeanPriceTag(500),
                              purchaseReqs=LevelPurchaseRequirement(80 - 1)),
        ]),
    }),
}

# Region Kart clerk items
NPCShopRacingItems = ShopItemCatalogue({
    NPCShopCategory.Racing: ShopItemListing([
        InventoryShopItem(FurnitureItemType.Prop_RR_Crate, priceTags=JellybeanPriceTag(300),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 20-1)),
        InventoryShopItem(FurnitureItemType.Prop_RR_BigTires, priceTags=JellybeanPriceTag(300),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 20 - 1)),
        InventoryShopItem(FurnitureItemType.Prop_RR_WrenchJack, priceTags=JellybeanPriceTag(300),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 20 - 1)),
        InventoryShopItem(FurnitureItemType.Prop_RR_Mailbox, priceTags=JellybeanPriceTag(300),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 20 - 1)),
        InventoryShopItem(FurnitureItemType.Prop_RR_Lamppost, priceTags=JellybeanPriceTag(300),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 20 - 1)),
        InventoryShopItem(FurnitureItemType.Prop_RR_Announcer, priceTags=JellybeanPriceTag(300),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 20 - 1)),
        InventoryShopItem(FurnitureItemType.Prop_RR_Cone, priceTags=JellybeanPriceTag(300),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 20 - 1)),
        InventoryShopItem(FurnitureItemType.Prop_RR_LeaderboardSign, priceTags=JellybeanPriceTag(300),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 20 - 1)),
    ]),
    NPCShopCategory.Clothing: ShopItemListing([
        InventoryShopItem(ClothingTopItemType.RacerJumpsuit, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingTopItemType.RacingFlag, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingTopItemType.RoadsterRaceway, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingTopItemType.Roadster, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.CheckeredRacingShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.BlueRacingShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.IndigoRacingShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.DarkBlueRacingShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.RacingStripeShorts, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.RedCheckeredSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.BlueCheckeredRacingSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.IndigoRacingSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.DarkBlueRacingSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
        InventoryShopItem(ClothingBottomItemType.RacingStripeSkirt, priceTags=JellybeanPriceTag(500),
                          purchaseReqs=ActivityLevelPurchaseRequirement(ToontownGlobals.ACTIVITY_RACING, 30 - 1)),
    ])
})
NPCShopItems[NPCToonID.AnitaWinn] = NPCShopRacingItems
NPCShopItems[NPCToonID.IvonaRace] = NPCShopRacingItems
# endregion

# endregion


# region NPC Shop Visual Definitions

class ShopVisualDefinition:
    def __init__(self, scaledTexture=None, scaledColor=None, borderScale=None, patternTexture=None, patternSpeed=None,
                 patternScale=None, patternColor=None, shadowStrength=None):
        self.scaledTexture = scaledTexture or 'core/gui/maps/cc_t_gui_gen_bg_sframe_desat.png'
        self.scaledColor = scaledColor or Vec4(48 / 255, 181 / 255, 105 / 255, 1.0)
        self.borderScale = borderScale or 0.045
        self.patternTexture = patternTexture or 'core/gui/maps/cc_t_gui_sframe_pat_testgrayscale.png'
        # Specifically do None check because patternSpeed can be 0 for non-moving bgs
        self.patternSpeed = patternSpeed if patternSpeed is not None else (0.015, -0.015)
        self.patternScale = patternScale or 0.14
        self.patternColor = patternColor or ColorHelper.hexToPCol('406d89')
        self.shadowStrength = shadowStrength or 0.04


NPCShopVisualDefinitions: dict[NPCToonID, ShopVisualDefinition] = {
    NPCToonID.EdgarAllanPole: ShopVisualDefinition(),
    NPCToonID.JuneLoon: ShopVisualDefinition(
        patternTexture='core/gui/maps/cc_t_gui_sframe_pat_music_notes.png',
    ),
}

# endregion
# region Shop Exterior Nametag Defs


class ShopExteriorDefinition:
    def __init__(self, textProperty='shop_tag', subTag=None, subTagProperty='shop_subtag'):
        self.textProperty = textProperty
        self.subTag = subTag
        self.subTagProperty = subTagProperty


# Based on branch zone and block number
NPCShopExteriorDefinitions: dict[int, dict[int, ShopExteriorDefinition]] = {
    ToontownGlobals.DonaldsDock: {
        11: ShopExteriorDefinition(subTag='Fishing Rod Shop')
    },
    ToontownGlobals.BaritoneBoulevard: {
        31: ShopExteriorDefinition(subTag='Music Disc Shop')
    }
}
# endregion
# region Getter Funcs


def getNPCItemCatalogue(npcID: NPCToonID | int) -> ShopItemCatalogue:
    return NPCShopItems.get(npcID, ShopItemCatalogue(dict()))


def getNPCShopVisualDef(npcID: NPCToonID | int) -> ShopVisualDefinition:
    return NPCShopVisualDefinitions.get(npcID, ShopVisualDefinition())


def getNPCShopExteriorDef(branchZone: int, blockNumber: int) -> ShopExteriorDefinition:
    return NPCShopExteriorDefinitions.get(branchZone, dict()).get(blockNumber)

# endregion
