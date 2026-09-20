from toontown.inventory.enums.ItemEnums import BackgroundItemType, NameplateItemType, ProfilePoseItemType, \
    NametagFontItemType, CheesyEffectItemType, ClothingTopItemType, ClothingBottomItemType, HatItemType, BackpackItemType
from toontown.quest3.QuestEnums import QuestSource, QuestCollectable, QuestItemName
from toontown.quest3.base.QuestChain import QuestChain
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.base.QuestObjective import MultiObjective
from toontown.quest3.rewards import *
from toontown.quest3.requirements import *
from toontown.quest3.objectives import *
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import getNotify

notify = getNotify("SideQuestLine")

"""
Code specific to time sensitive sidequests.
"""
from toontown.toonbase.ToontownGlobals import (
    CHRISTMAS
)
from toontown.ai import HolidayGlobals

from datetime import timedelta

toonselTownDateRange = HolidayGlobals.HOLIDAY2RANGE[CHRISTMAS]


class SideQuestLineContainer(QuestLine):
    questSource = QuestSource.SideQuest


SideQuestLine = SideQuestLineContainer(
    questLine={
        1: QuestChain(
            rewards=(TeleportReward(2000), BeanReward(15 * 2), ExpReward(232 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: DefeatCogObjective(
                    npc=2003, cogCount=10, cogLocation=ToontownGlobals.ToontownCentral
                ),
                2: RecoverFromCogObjective(
                    npc=2003,
                    recoverItem=QuestItemName.HeavyCogGears,
                    recoverChance=0.7,
                    recoverRequired=2,
                ),
                3: RecoverFromCogObjective(
                    npc=2003,
                    recoverItem=QuestItemName.MechanicalBelt,
                    recoverChance=0.7,
                    recoverRequired=2,
                ),
            },
        ),
        2: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.TrashcatsRags), InventoryReward(ClothingBottomItemType.Shorts_Travis_Rags),
                BeanReward(15 * 2),
                ExpReward(264 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: QuestFishObjective(
                    npc=2024, fishType=QuestItemName.PBJFish, fishChance=0.5
                ),
                2: VisitObjective(npc=(2024, 2103)),
                3: RecoverFromCogObjective(
                    npc=2103,
                    cogType="ins",
                    recoverItem=QuestItemName.BeardSupply,
                    recoverChance=0.75,
                ),
                4: VisitObjective(npc=(2103, 2024)),
                5: DeliverGagObjective(npc=2024, gagCount=5, gagLevel=1),
                6: VisitObjective(npc=(2024, 2001)),
                7: VisitObjective(npc=(2001, 2024)),
            },
        ),
        3: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.Invisible), BeanReward(15 * 2), ExpReward(258 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=2216,
                    cogTrack="l",
                    recoverItem=QuestItemName.SampleOfInk,
                    recoverChance=0.65,
                    recoverRequired=5,
                ),
                2: QuestFishObjective(
                    npc=2216,
                    fishType=QuestItemName.BagOfSalt,
                    fishCount=4,
                    fishChance=1.0,
                ),
                3: RecoverFromCogObjective(
                    npc=2216,
                    recoverItem=QuestItemName.PlasticContainer,
                    recoverChance=0.7,
                    recoverRequired=3,
                ),
                4: DefeatCogObjective(npc=2216, cogCount=10),
            },
        ),
        4: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.Shirt_TTC_Firefighter),
                InventoryReward(ClothingBottomItemType.Shorts_TTC_Firefighter),
                InventoryReward(ClothingBottomItemType.Skirt_TTC_Firefighter),
                BeanReward(15 * 2),
                ExpReward(115 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=2222,
                    recoverItem=QuestItemName.Igniter,
                    recoverChance=0.75,
                    recoverRequired=5,
                ),
                2: RecoverFromCogObjective(
                    npc=2222,
                    recoverItem=QuestItemName.MetalCasing,
                    recoverChance=0.65,
                    recoverRequired=5,
                ),
                3: RecoverFromCogObjective(
                    npc=2222,
                    recoverItem=QuestItemName.MetalPlate,
                    recoverChance=0.55,
                    recoverRequired=5,
                ),
            },
        ),
        5: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Zany), BeanReward(15 * 2), ExpReward(279 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(2415, 2416)),
                2: VisitObjective(npc=(2416, 2415)),
                3: DefeatCogObjective(
                    npc=2415, cogCount=6, cogLocation=ToontownGlobals.WackyWay
                ),
                4: VisitObjective(npc=(2415, 2318)),
                5: RecoverFromCogObjective(
                    npc=2318,
                    cogLocation=ToontownGlobals.ToontownCentral,
                    cogType="f",
                    recoverItem=QuestItemName.Baloney,
                    recoverChance=0.5,
                ),
                6: VisitObjective(npc=(2318, 2415)),
                7: VisitObjective(npc=(2415, 2416)),
            },
        ),
        6: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Selfie), BeanReward(15 * 2), ExpReward(119 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(90042, 2005)),
                2: RecoverFromCogObjective(
                    npc=(2005, 90042),
                    cogTrack="l",
                    recoverItem=QuestItemName.TravelGuidePage,
                    recoverChance=0.85,
                    recoverRequired=5,
                ),
                3: TrolleyObjective(npc=90042),
            },
        ),
        7: QuestChain(
            rewards=(TeleportReward(1000), BeanReward(100 * 2), ExpReward(1194 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 11),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=1406,
                    cogLocation=ToontownGlobals.DonaldsDock,
                    cogType="gh",
                    recoverItem=QuestItemName.Propeller,
                    recoverChance=0.9,
                    recoverRequired=3,
                ),
                2: DefeatCogObjective(npc=1406, cogCount=7, cogLevelMin=4),
                3: RecoverFromBuildingObjective(
                    npc=1406,
                    buildingLocation=ToontownGlobals.DonaldsDock,
                    recoverItem=QuestItemName.WindowPanes,
                    recoverChance=100,
                ),
            },
        ),
        8: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.BBSailor),
                InventoryReward(ClothingBottomItemType.Shorts_BB_Sailor),
                InventoryReward(ClothingBottomItemType.Skirt_BB_Sailor),
                BeanReward(100 * 2),
                ExpReward(1197 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 11),),
            deletable=True,
            steps={
                1: TreasureObjective(npc=1103, treasureCount=10, treasureType=1),
                2: RecoverFromCogObjective(
                    npc=1103,
                    cogType="mm",
                    recoverItem=QuestItemName.SmallSewingNeedles,
                    recoverChance=0.45,
                ),
                3: RecoverFromCogObjective(
                    npc=1103, recoverItem=QuestItemName.PieceofThread, recoverChance=0.9
                ),
                4: BuildingObjective(npc=1103),
            },
        ),
        9: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.BigLegs), InventoryReward(NametagFontItemType.Nautical), BeanReward(100 * 2), ExpReward(1290 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 11),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=1420, cogCount=12, cogLevelMin=3),
                2: BuildingObjective(npc=1420, buildingCount=2),
                3: DefeatCogObjective(npc=1420, cogCount=3, cogType="ym"),
                4: DeliverGagObjective(npc=1420, gagCount=5, gagLevel=2),
            },
        ),
        11: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Boardwalk), BeanReward(100 * 2), ExpReward(1280 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 11),),
            deletable=True,
            steps={
                1: DefeatCogObjective(
                    npc=1319, cogCount=15, cogLocation=ToontownGlobals.DonaldsDock
                ),
                2: VisitObjective(npc=(1319, 1121)),
                3: DefeatCogObjective(
                    npc=1121, cogCount=7, cogLocation=ToontownGlobals.BuccaneerBoulevard, npcReturnable=False,
                ),
                4: DeliverJellybeanObjective(npc=1121, jellybeans=50),
                5: DeliverObjective(npc=(1121, 1319), recoverItem=QuestItemName.Lumber),
            },
        ),
        12: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Wonky), BeanReward(100 * 2), ExpReward(1248 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 11),),
            deletable=True,
            steps={
                1: DefeatCogObjective(
                    npc=1118,
                    cogCount=15,
                    cogLocation=ToontownGlobals.DonaldsDock,
                    cogTrack="l",
                ),
                2: TreasureChestObjective(npc=1118, chestCount=1),
            },
        ),
        13: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Diving), BeanReward(100 * 2), ExpReward(1304 * 2)),
            required=(
                QuestCompletionRequirement(QuestSource.MainQuest, 11),
                QuestCompletionRequirement(QuestSource.SideQuest, 6),
            ),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=90043,
                    cogType="cv",
                    recoverItem=QuestItemName.PairofGoggles,
                    recoverChance=1.0,
                ),
                2: VisitObjective(npc=(90043, 1221)),
                3: BuildingObjective(npc=1221),
                4: DeliverObjective(
                    npc=(1221, 90043), recoverItem=QuestItemName.Sunscreen
                ),
                5: SwimObjective(npc=90043),
            },
        ),
        14: QuestChain(
            rewards=(TeleportReward(7000), BeanReward(150 * 2), ExpReward(3088 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 21),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=7219,
                    cogLocation=ToontownGlobals.YeOlde,
                    recoverItem=QuestItemName.StrongWire,
                    recoverChance=0.65,
                    recoverRequired=5,
                ),
                2: DefeatCogObjective(
                    npc=7219,
                    cogCount=15,
                    cogLevelMin=6,
                    cogLocation=ToontownGlobals.YeOlde,
                ),
                3: RecoverFromCogObjective(
                    npc=7219,
                    cogType="sd",
                    recoverItem=QuestItemName.Bandage,
                    recoverChance=0.42,
                ),
            },
        ),
        15: QuestChain(
            rewards=(DummyReward('Olde Black & White Filter'), BeanReward(150 * 2), ExpReward(3032 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 21),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=7010,
                    cogType="mb",
                    recoverItem=QuestItemName.MoneyBag,
                    recoverChance=0.8,
                    recoverRequired=5,
                ),
                2: VisitObjective(npc=(7010, 7202)),
                3: DefeatCogObjective(
                    npc=7202,
                    cogCount=20,
                    cogLevelMin=5,
                    cogLocation=ToontownGlobals.YeOlde,
                ),
                4: DeliverObjective(npc=(7202, 7010), recoverItem=QuestItemName.Food),
                5: RecoverFromBuildingObjective(
                    npc=7010,
                    buildingLocation=ToontownGlobals.YeOlde,
                    recoverItem=QuestItemName.MechanicalPieces,
                    recoverChance=100,
                ),
            },
        ),
        16: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.YOTTKnight),
                InventoryReward(ClothingBottomItemType.Shorts_YOTT_Knight),
                InventoryReward(ClothingBottomItemType.Skirt_YOTT_Knight),
                BeanReward(150 * 2),
                ExpReward(3074 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 21),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=7114, cogCount=30, cogLevelMin=6),
                2: DefeatCogObjective(npc=7114, cogCount=20, cogLevelMin=7),
            },
        ),
        17: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.Transparent), BeanReward(150 * 2), ExpReward(3112 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 21),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=7305, cogCount=10, cogLevelMin=5),
                2: DefeatCogObjective(npc=7305, cogCount=5, cogType="dt"),
                3: DeliverGagObjective(
                    npc=7305, gagCount=1, gagLevel=4, rewards=[InventoryReward(NametagFontItemType.Poetic)]
                ),
                4: BuildingObjective(npc=7305, floorMinimum=3, buildingCount=2),
                5: DefeatCogObjective(npc=7305, cogCount=10, cogLevelMin=5),
                6: DefeatCogObjective(npc=7305, cogCount=5, cogType="b"),
            },
        ),
        19: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.SmallHead), BeanReward(150 * 2), ExpReward(3016 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 21),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=7107, cogCount=15, cogType="mm"),
            },
        ),
        20: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Casting), BeanReward(150 * 2), ExpReward(3177 * 2)),
            required=(
                QuestCompletionRequirement(QuestSource.MainQuest, 21),
                QuestCompletionRequirement(QuestSource.SideQuest, 13),
            ),
            deletable=True,
            steps={
                1: RecoverFromBuildingObjective(
                    npc=90044,
                    cogTrack="m",
                    recoverItem=QuestItemName.GoldPenny,
                    recoverChance=100,
                ),
                2: DeliverObjective(
                    npc=(90044, 7003), recoverItem=QuestItemName.GoldPenny
                ),
                3: RecoverFromCogObjective(
                    npc=7003,
                    cogType="shw",
                    recoverItem=QuestItemName.Monocle,
                    recoverChance=0.95,
                ),
                4: DeliverObjective(
                    npc=(7003, 7300), recoverItem=QuestItemName.GoldPenny
                ),
                5: DefeatCogObjective(
                    npc=7300,
                    cogCount=10,
                    cogLocation=ToontownGlobals.YeOlde,
                    cogTrack="m",
                ),
                6: DeliverObjective(
                    npc=(7300, 90044), recoverItem=QuestItemName.ChocolateCoin
                ),
            },
        ),
        21: QuestChain(
            rewards=(TeleportReward(5000), BeanReward(150 * 2), ExpReward(5729 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 31),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=5208, cogCount=10, cogType="nc"),
                2: VisitObjective(npc=(5208, 5310)),
                3: DefeatCogObjective(npc=5310, cogCount=10, cogType="ds", npcReturnable=False),
                4: BuildingObjective(npc=5310, floorMinimum=3, buildingCount=2),
                5: VisitObjective(npc=(5310, 5208)),
                6: DefeatCogObjective(
                    npc=5208,
                    cogCount=10,
                    cogLocation=ToontownGlobals.DaisyGardens,
                    cogTrack="g",
                ),
            },
        ),
        22: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.DGGardening),
                InventoryReward(ClothingBottomItemType.Shorts_DG_Gardening),
                InventoryReward(ClothingBottomItemType.Skirt_DG_Gardening),
                BeanReward(150 * 2),
                ExpReward(5660 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 31),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=5220,
                    cogLocation=ToontownGlobals.DaisyGardens,
                    recoverItem=QuestItemName.PieceofPlastic,
                    recoverChance=0.6,
                    recoverRequired=4,
                ),
                2: RecoverFromCogObjective(
                    npc=5220,
                    cogType="mi",
                    recoverItem=QuestItemName.TrustyTrowel,
                    recoverChance=0.65,
                ),
                3: TreasureObjective(npc=5220, treasureCount=10, treasureType=2),
            },
        ),
        23: QuestChain(
            rewards=(InventoryReward(HatItemType.Hat_Samba_Classic), BeanReward(150 * 2), ExpReward(5722 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 31),),
            deletable=True,
            steps={
                1: MultiObjective(
                    CatchingGameObjective(
                        npc=5216, fruitCount=10, zoneId=2000, npcReturnable=False
                    ),
                    CatchingGameObjective(
                        npc=5216, fruitCount=10, zoneId=1000, npcReturnable=False
                    ),
                    CatchingGameObjective(
                        npc=5216, fruitCount=7, zoneId=5000, npcReturnable=False
                    ),
                    CatchingGameObjective(
                        npc=5216, fruitCount=5, zoneId=3000, npcReturnable=False
                    ),
                    CatchingGameObjective(
                        npc=5216, fruitCount=5, zoneId=9000, npcReturnable=False
                    ),
                    JungleGameObjective(npc=5216, bananaCount=2, npcReturnable=False),
                ),
                2: DeliverObjective(npc=5216, recoverItem=QuestItemName.LotsOfFruit),
            },
        ),
        24: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.FlatPortrait), BeanReward(150 * 2), ExpReward(5686 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 31),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=5202,
                    cogType="bgh",
                    recoverItem=QuestItemName.MoustacheHair,
                    recoverChance=0.55,
                    recoverRequired=3,
                ),
                2: RecoverFromCogObjective(
                    npc=5202,
                    cogType="nc",
                    recoverItem=QuestItemName.MetallicSeven,
                    recoverChance=0.45,
                ),
                3: TrolleyObjective(npc=5202, rewards=[InventoryReward(NametagFontItemType.Silly)]),
                4: VisitObjective(npc=(5202, 5225)),
                5: RecoverFromBuildingObjective(
                    npc=5225,
                    cogTrack="m",
                    recoverItem=QuestItemName.JellybeanRegister,
                    recoverChance=100,
                ),
                6: RecoverFromCogObjective(
                    npc=5225, recoverItem=QuestItemName.LightBulb, recoverChance=0.45
                ),
            },
        ),
        26: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.GreenToon), BeanReward(150 * 2), ExpReward(5687 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 31),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=5312,
                    cogType="bc",
                    recoverItem=QuestItemName.MagicBean,
                    recoverChance=0.75,
                    recoverRequired=5,
                ),
                2: RecoverFromCogObjective(
                    npc=5312,
                    cogTrack="g",
                    recoverItem=QuestItemName.PieceofDenim,
                    recoverChance=0.75,
                    recoverRequired=5,
                ),
            },
        ),
        27: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Running), BeanReward(150 * 2), ExpReward(5688 * 2)),
            required=(
                QuestCompletionRequirement(QuestSource.MainQuest, 31),
                QuestCompletionRequirement(QuestSource.SideQuest, 20),
            ),
            deletable=True,
            steps={
                1: VisitObjective(npc=(90045, 5206)),
                2: QuestFishObjective(
                    npc=5206,
                    fishType=QuestItemName.SewingNeedle,
                    fishCount=4,
                    fishChance=0.95,
                ),
                3: RecoverFromCogObjective(
                    npc=5206,
                    recoverItem=QuestItemName.Button,
                    recoverChance=0.9,
                    recoverRequired=5,
                ),
                4: DeliverObjective(
                    npc=(5206, 90045), recoverItem=QuestItemName.Tuxedo
                ),
                5: VisitObjective(npc=(90045, 5215)),
                6: RecoverFromCogObjective(
                    npc=5215,
                    cogType="mh",
                    recoverItem=QuestItemName.DiamondRing,
                    recoverChance=0.95,
                ),
                7: QuestCollectableObjective(
                    npc=(5215, 90045), collectable=QuestCollectable.TumblesTiara, npcReturnable=False,
                ),
                8: DeliverObjective(npc=90045, recoverItem=QuestItemName.DiamondRing),
            },
        ),
        28: QuestChain(
            rewards=(TeleportReward(4000), BeanReward(150 * 2), ExpReward(9162 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 41),),
            deletable=True,
            steps={
                1: DefeatCogObjective(
                    npc=4128, cogCount=15, cogLevelMin=6, executive=True
                ),
                2: DefeatCogObjective(
                    npc=4128,
                    cogCount=20,
                    cogLevelMin=5,
                    cogLocation=ToontownGlobals.AltoAvenue,
                ),
                3: BuildingObjective(npc=4128, floorMinimum=4, buildingCount=3),
            },
        ),
        29: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.MMLBand),
                InventoryReward(ClothingBottomItemType.Shorts_MML_Band),
                BeanReward(150 * 2),
                ExpReward(9117 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 41),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=4129,
                    cogType="cr",
                    recoverItem=QuestItemName.PieceofGold,
                    recoverChance=0.75,
                    recoverRequired=6,
                ),
                2: DefeatCogObjective(
                    npc=4129, cogCount=15, cogLevelMin=7, executive=True
                ),
            },
        ),
        30: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.FlatProfile), InventoryReward(NametagFontItemType.Whimsical), BeanReward(150 * 2), ExpReward(9142 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 41),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=4408, cogCount=10, cogLevelMin=6),
                2: DefeatCogObjective(npc=4408, cogCount=10, cogType="ms"),
                3: TreasureObjective(
                    npc=4408,
                    treasureCount=10,
                    treasureType=4,
                ),
                4: RecoverFromBuildingObjective(
                    npc=4408, recoverItem=QuestItemName.Tuner, recoverChance=100
                ),
                5: DefeatCogObjective(npc=4408, cogCount=10, cogLevelMin=6),
            },
        ),
        32: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.BigHead), BeanReward(150 * 2), ExpReward(9174 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 41),),
            deletable=True,
            steps={
                1: DefeatCogObjective(
                    npc=4401, cogCount=25, cogLocation=ToontownGlobals.MinniesMelodyland
                ),
                2: VisitObjective(npc=(4401, 2024)),
            },
        ),
        33: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Fancy), BeanReward(150 * 2), ExpReward(9102 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 41),),
            deletable=True,
            steps={
                1: BuildingObjective(npc=4137, buildingCount=6),
            },
        ),
        34: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Presenting), BeanReward(150 * 2), ExpReward(9271 * 2)),
            required=(
                QuestCompletionRequirement(QuestSource.MainQuest, 41),
                QuestCompletionRequirement(QuestSource.SideQuest, 27),
            ),
            deletable=True,
            steps={
                1: VisitObjective(npc=(90046, 4405)),
                2: RecoverFromCogObjective(
                    npc=4405,
                    cogType="tw",
                    recoverItem=QuestItemName.PianoKey,
                    recoverChance=0.85,
                    recoverRequired=4,
                ),
                3: DeliverObjective(npc=(4405, 90046), recoverItem=QuestItemName.Piano),
                4: QuestFishObjective(
                    npc=90046, fishType=QuestItemName.PianoTuna, fishChance=0.95
                ),
                5: TreasureObjective(npc=90046, treasureCount=10, treasureType=4),
                6: RecoverFromCogObjective(
                    npc=90046,
                    cogType="rb",
                    recoverItem=QuestItemName.RollofFilm,
                    recoverChance=0.95,
                ),
            },
        ),
        35: QuestChain(
            rewards=(TeleportReward(3000), BeanReward(150 * 2), ExpReward(13420 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 48),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=3227,
                    cogLocation=ToontownGlobals.TheBrrrgh,
                    recoverItem=QuestItemName.SolarCellPart,
                    recoverChance=0.45,
                    recoverRequired=10,
                ),
                2: BuildingObjective(npc=3227, floorMinimum=4, buildingCount=5),
                3: DefeatCogObjective(npc=3227, cogCount=15, cogLevelMin=8),
            },
        ),
        36: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.BrrrghSnowflakes),
                InventoryReward(ClothingBottomItemType.Shorts_TB_Sweater),
                InventoryReward(ClothingBottomItemType.Skirt_TB_Sweater),
                BeanReward(150 * 2),
                ExpReward(13394 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 48),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(3318, 3305)),
                2: InvestigateObjective(npc=3305, zoneId=3815),
                3: RecoverFromCogObjective(
                    npc=3305,
                    cogType="ms",
                    recoverItem=QuestItemName.ElasticBand,
                    recoverChance=0.5,
                    recoverRequired=3,
                ),
                4: DeliverObjective(
                    npc=(3305, 3318), recoverItem=QuestItemName.XXLKittenMittens
                ),
                5: VisitObjective(npc=(3318, 3319)),
                6: DefeatCogObjective(npc=3319, cogCount=12, cogType="ds"),
                7: DeliverObjective(
                    npc=(3319, 3318), recoverItem=QuestItemName.SuperHat
                ),
            },
        ),
        37: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.NoColor), BeanReward(150 * 2), ExpReward(13372 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 48),),
            deletable=True,
            steps={
                1: MultiObjective(
                    DefeatCogObjective(
                        npc=3304, cogCount=15, cogTrack="s", npcReturnable=False
                    ),
                    DefeatCogObjective(
                        npc=3304, cogCount=15, cogTrack="m", npcReturnable=False
                    ),
                    DefeatCogObjective(
                        npc=3304, cogCount=15, cogTrack="l", npcReturnable=False
                    ),
                    DefeatCogObjective(
                        npc=3304, cogCount=15, cogTrack="c", npcReturnable=False
                    ),
                    DefeatCogObjective(
                        npc=3304, cogCount=15, cogTrack="g", npcReturnable=False
                    ),
                ),
                2: VisitObjective(npc=3304),
            },
        ),
        38: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.Wireframe), BeanReward(150 * 2), ExpReward(13426 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 48),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=3015, cogCount=25),
                2: DefeatCogObjective(npc=3015, cogCount=50),
                3: VisitObjective(npc=(3015, 3217)),
                4: DefeatCogObjective(npc=3217, cogCount=10, cogLevelMin=8),
                5: BuildingObjective(npc=3217, floorMinimum=4, buildingCount=3),
                6: VisitObjective(npc=(3217, 3015), rewards=[InventoryReward(NametagFontItemType.Shivering)]),
                7: VisitObjective(npc=(3015, 3217)),
                8: RecoverFromCogObjective(
                    npc=3217,
                    cogLocation=ToontownGlobals.SleetStreet,
                    recoverItem=QuestItemName.OilCoveredStick,
                    recoverChance=0.45,
                ),
                9: DeliverObjective(
                    npc=(3217, 3015), recoverItem=QuestItemName.BurningStick
                ),
            },
        ),
        40: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.BigWhite), BeanReward(150 * 2), ExpReward(13347 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 48),),
            deletable=True,
            steps={
                1: MultiObjective(
                    DefeatCogObjective(
                        npc=3306,
                        cogCount=5,
                        cogLocation=ToontownGlobals.LoopyLane,
                        npcReturnable=False,
                    ),
                    DefeatCogObjective(
                        npc=3306,
                        cogCount=6,
                        cogLocation=ToontownGlobals.AnchorAvenue,
                        npcReturnable=False,
                    ),
                    DefeatCogObjective(
                        npc=3306,
                        cogCount=7,
                        cogLocation=ToontownGlobals.WizardWay,
                        npcReturnable=False,
                    ),
                    DefeatCogObjective(
                        npc=3306,
                        cogCount=8,
                        cogLocation=ToontownGlobals.SunflowerStreet,
                        npcReturnable=False,
                    ),
                    DefeatCogObjective(
                        npc=3306,
                        cogCount=9,
                        cogLocation=ToontownGlobals.SopranoStreet,
                        npcReturnable=False,
                    ),
                ),
                2: VisitObjective(npc=3306),
            },
        ),
        41: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Surprised), BeanReward(150 * 2), ExpReward(13349 * 2)),
            required=(
                QuestCompletionRequirement(QuestSource.MainQuest, 48),
                QuestCompletionRequirement(QuestSource.SideQuest, 34),
            ),
            deletable=True,
            steps={
                1: RecoverFromBuildingObjective(
                    npc=90047,
                    buildingLocation=ToontownGlobals.TheBrrrgh,
                    recoverItem=QuestItemName.WarmItem,
                    recoverChance=100,
                    recoverRequired=2,
                ),
                2: VisitObjective(npc=(90047, 3230)),
                3: RecoverFromCogObjective(
                    npc=3230,
                    cogType="br",
                    recoverItem=QuestItemName.IceCap,
                    recoverChance=0.95,
                    recoverRequired=3,
                ),
                4: DeliverObjective(
                    npc=(3230, 90047), recoverItem=QuestItemName.IceCap
                ),
                5: RecoverFromCogObjective(
                    npc=90047,
                    recoverItem=QuestItemName.Boot,
                    recoverChance=0.95,
                    recoverRequired=2,
                ),
            },
        ),
        42: QuestChain(
            rewards=(TeleportReward(6000), BeanReward(150 * 2), ExpReward(18434 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 56),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=6305,
                    cogType="tbc",
                    recoverItem=QuestItemName.GolfClub,
                    recoverChance=0.75,
                    recoverRequired=10,
                ),
                2: RecoverFromCogObjective(
                    npc=6305,
                    recoverItem=QuestItemName.GolfBall,
                    recoverChance=0.85,
                    recoverRequired=30,
                ),
                3: RecoverFromCogObjective(
                    npc=6305,
                    cogType="hho",
                    recoverItem=QuestItemName.GolfCap,
                    recoverChance=0.47,
                    recoverRequired=7,
                ),
            },
        ),
        43: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.AAParkRanger),
                InventoryReward(ClothingBottomItemType.Shorts_AA_ParkRanger),
                BeanReward(150 * 2),
                ExpReward(18424 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 56),),
            deletable=True,
            steps={
                1: TreasureObjective(npc=6104, treasureCount=8, treasureType=6),
                2: RecoverFromCogObjective(
                    npc=6104,
                    cogType="rb",
                    recoverItem=QuestItemName.Goldentooth,
                    recoverChance=0.75,
                    recoverRequired=3,
                ),
                3: QuestFishObjective(
                    npc=6104,
                    fishType=QuestItemName.Greenplant,
                    fishCount=5,
                    fishChance=0.75,
                ),
                4: RecoverFromCogObjective(
                    npc=6104,
                    recoverItem=QuestItemName.BeltandButtons,
                    recoverChance=0.45,
                ),
            },
        ),
        44: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.SmallLegs), BeanReward(150 * 2), ExpReward(18432 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 56),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=6114, cogCount=20, cogLevelMin=7),
                2: RecoverFromBuildingObjective(
                    npc=6114, recoverItem=QuestItemName.QualityMetal, recoverChance=50
                ),
                3: RecoverFromCogObjective(
                    npc=6114,
                    cogType="tbc",
                    recoverItem=QuestItemName.PieceofCheese,
                    recoverChance=0.85,
                    recoverRequired=6,
                ),
            },
        ),
        45: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.BigToon), BeanReward(150 * 2), ExpReward(18472 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 56),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=6106, cogCount=20, cogLevelMin=6),
                2: BuildingObjective(npc=6106, floorMinimum=3, buildingCount=2),
            },
        ),
        46: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Practical), BeanReward(150 * 2), ExpReward(18510 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 56),),
            deletable=True,
            steps={
                1: MultiObjective(
                    DefeatCogObjective(
                        npc=6416,
                        cogCount=10,
                        cogLocation=ToontownGlobals.LegumeLane,
                        npcReturnable=False,
                    ),
                    DefeatCogObjective(
                        npc=6416,
                        cogCount=10,
                        cogLocation=ToontownGlobals.AlmondAvenue,
                        npcReturnable=False,
                    ),
                    DefeatCogObjective(
                        npc=6416,
                        cogCount=10,
                        cogLocation=ToontownGlobals.WalnutWay,
                        npcReturnable=False,
                    ),
                    DefeatCogObjective(
                        npc=6416,
                        cogCount=10,
                        cogLocation=ToontownGlobals.PeanutPlace,
                        npcReturnable=False,
                    ),
                ),
                2: VisitObjective(npc=6416),
            },
        ),
        47: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Greened), BeanReward(150 * 2), ExpReward(18791 * 2)),
            required=(
                QuestCompletionRequirement(QuestSource.MainQuest, 56),
                QuestCompletionRequirement(QuestSource.SideQuest, 41),
            ),
            deletable=True,
            steps={
                1: VisitObjective(npc=(90048, 6203)),
                2: RecoverFromCogObjective(
                    npc=6203,
                    cogType="ds",
                    recoverItem=QuestItemName.Briefcase,
                    recoverChance=0.7,
                ),
                3: RecoverFromCogObjective(
                    npc=6203,
                    cogType="shw",
                    recoverItem=QuestItemName.Stick,
                    recoverChance=0.9,
                    recoverRequired=2,
                ),
                4: RecoverFromCogObjective(
                    npc=6203,
                    cogType="ac",
                    recoverItem=QuestItemName.Bandage,
                    recoverChance=0.9,
                    recoverRequired=3,
                ),
                5: VisitObjective(npc=(6203, 6410)),
                6: BuildingObjective(npc=6410, floorMinimum=5, buildingCount=2),
                7: DeliverObjective(
                    npc=(6410, 6203), recoverItem=QuestItemName.PackofTrailMix
                ),
                8: VisitObjective(npc=(6203, 6112)),
                9: DefeatCogObjective(npc=6112, cogType="sh"),
                10: DeliverObjective(
                    npc=(6112, 6203), recoverItem=QuestItemName.Smores
                ),
                11: DeliverObjective(
                    npc=(6203, 90048), recoverItem=QuestItemName.SurvivalKit
                ),
            },
        ),
        48: QuestChain(
            rewards=(TeleportReward(9000), BeanReward(150 * 2), ExpReward(15610 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 66),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(9202, 9208)),
                2: BuildingObjective(npc=9208, floorMinimum=5, buildingCount=8),
                3: VisitObjective(npc=(9208, 9202)),
                4: VisitObjective(npc=(9202, 9222)),
                5: RecoverFromCogObjective(
                    npc=9222,
                    recoverItem=QuestItemName.Tie,
                    recoverChance=0.6,
                    recoverRequired=7,
                ),
                6: VisitObjective(npc=(9222, 9202)),
                7: VisitObjective(npc=(9202, 9219)),
                8: RecoverFromCogObjective(
                    npc=9219,
                    cogType="mh",
                    recoverItem=QuestItemName.Shades,
                    recoverChance=0.75,
                    recoverRequired=10,
                ),
                9: VisitObjective(npc=(9219, 9202)),
            },
        ),
        49: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.DrowsyDreamland),
                InventoryReward(ClothingBottomItemType.Shorts_DDL_Sleeper),
                BeanReward(150 * 2),
                ExpReward(15627 * 2),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 66),),
            deletable=True,
            steps={
                1: TreasureObjective(npc=9221, treasureCount=10, treasureType=5),
                2: RecoverFromCogObjective(
                    npc=9221,
                    cogTrack="s",
                    recoverItem=QuestItemName.PieceofZephyrCloth,
                    recoverChance=0.7,
                    recoverRequired=25,
                ),
                3: RecoverFromCogObjective(
                    npc=9221,
                    cogType="bw",
                    recoverItem=QuestItemName.ZanyMaterials,
                    recoverChance=0.4,
                ),
            },
        ),
        50: QuestChain(
            rewards=(InventoryReward(CheesyEffectItemType.SmallToon), BeanReward(150 * 2), ExpReward(15622 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 66),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=9115, cogCount=5, cogType="sc"),
                2: DefeatCogObjective(npc=9115, cogCount=5, cogType="mm"),
                3: DefeatCogObjective(npc=9115, cogCount=5, cogType="ds"),
                4: DefeatCogObjective(npc=9115, cogCount=5, cogType="hho"),
                5: DefeatCogObjective(npc=9115, cogCount=25, cogLevelMin=9),
                6: BuildingObjective(
                    npc=9115,
                    floorMinimum=4,
                    buildingCount=3,
                    rewards=[InventoryReward(NametagFontItemType.Action)],
                ),
                7: DefeatCogObjective(npc=9115, cogType="f"),
            },
        ),
        53: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Western), BeanReward(150 * 2), ExpReward(15522 * 2)),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 66),),
            deletable=True,
            steps={
                1: DefeatCogObjective(npc=9222, cogCount=5, cogType="mg"),
                2: RacingObjective(npc=9222),
                3: QuestFishObjective(
                    npc=9222,
                    fishType=QuestItemName.RustyCan,
                    fishCount=5,
                    fishChance=0.85,
                ),
            },
        ),
        54: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Yawn), BeanReward(150 * 2), ExpReward(16291 * 2)),
            required=(
                QuestCompletionRequirement(QuestSource.MainQuest, 66),
                QuestCompletionRequirement(QuestSource.SideQuest, 47),
            ),
            deletable=True,
            steps={
                1: DeliverObjective(
                    npc=(90049, 9120), recoverItem=QuestItemName.BrokenCamera
                ),
                2: DefeatCogObjective(npc=9120, cogCount=20, cogLevelMin=9),
                3: BuildingObjective(npc=9120, floorMinimum=6),
                4: VisitObjective(npc=(9120, 9130)),
                5: RecoverFromCogObjective(
                    npc=9130,
                    cogLocation=ToontownGlobals.TwilightTerrace,
                    cogTrack="g",
                    recoverItem=QuestItemName.MetalPlate,
                    recoverChance=0.8,
                    recoverRequired=5,
                ),
                6: RecoverFromCogObjective(
                    npc=9130, recoverItem=QuestItemName.MetalPolish, recoverChance=0.65
                ),
                7: DeliverObjective(
                    npc=(9130, 90049), recoverItem=QuestItemName.FixedCamera
                ),
            },
        ),
        55: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.BetaToon),
                InventoryReward(ClothingBottomItemType.Shorts_BetaToon),
                InventoryReward(ClothingBottomItemType.Skirt_BetaToon),
            ),
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=2023,
                    cogLocation=ToontownGlobals.ToontownCentral,
                    recoverItem=QuestItemName.BugSuitPart,
                    recoverChance=0.45,
                    recoverRequired=5,
                ),
                2: DefeatCogObjective(
                    npc=2023,
                    cogCount=5,
                    cogLocation=ToontownGlobals.ToontownCentral,
                    cogType="f",
                ),
                3: DefeatCogObjective(
                    npc=2023, cogCount=10, cogLocation=ToontownGlobals.ToontownCentral
                ),
            },
        ),
        56: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.GingerbreadA),
                InventoryReward(ClothingTopItemType.GingerbreadB),
                InventoryReward(ClothingBottomItemType.Shorts_Gingerbread),
                InventoryReward(ClothingBottomItemType.Skirt_Gingerbread),
            ),
            startDate=toonselTownDateRange.startDatetime,
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: TreasureObjective(npc=18504, treasureCount=10, treasureType=0),
                2: RecoverFromCogObjective(
                    npc=18504,
                    cogType="shw",
                    recoverItem=QuestItemName.Egg,
                    recoverChance=0.75,
                    recoverRequired=10,
                ),
                3: VisitObjective(npc=(18504, 2003)),
                4: RecoverFromCogObjective(
                    npc=2003,
                    cogTrack="c",
                    recoverItem=QuestItemName.ContainerofSalt,
                    recoverChance=0.5,
                    recoverRequired=10,
                ),
                5: DeliverObjective(
                    npc=(2003, 18504), recoverItem=QuestItemName.BakingSoda
                ),
                6: SnowballObjective(npc=18504),
            },
        ),
        57: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.TinSoldierTraditional),
                InventoryReward(ClothingBottomItemType.Shorts_Soldier_Traditional),
                InventoryReward(ClothingTopItemType.RagdollTraditional),
                InventoryReward(ClothingBottomItemType.Skirt_Ragdoll_Traditional),
                InventoryReward(ClothingBottomItemType.Shorts_Ragdoll_Traditional),
            ),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=1),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(18501, 18502)),
                2: RecoverFromCogObjective(
                    npc=18502,
                    cogTrack="l",
                    recoverItem=QuestItemName.PieceofRedTape,
                    recoverChance=0.65,
                    recoverRequired=10,
                ),
                3: DeliverObjective(
                    npc=(18502, 18501), recoverItem=QuestItemName.IncompleteClothing
                ),
                4: BuildingObjective(npc=18501, buildingCount=3),
                5: TreasureObjective(npc=18501, treasureCount=10, treasureType=3),
            },
        ),
        58: QuestChain(
            rewards=(InventoryReward(ClothingTopItemType.UglySweater),),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=2),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=18502,
                    cogTrack="l",
                    recoverItem=QuestItemName.PieceofRedTape,
                    recoverChance=0.5,
                    recoverRequired=10,
                ),
                2: RecoverFromCogObjective(
                    npc=18502,
                    cogType="dt",
                    recoverItem=QuestItemName.GooglyEyes,
                    recoverChance=0.4,
                ),
                3: InvestigateObjective(npc=18502, zoneId=18506),
                4: RecoverFromCogObjective(
                    npc=18502,
                    cogTrack="m",
                    recoverItem=QuestItemName.GreenThread,
                    recoverChance=0.5,
                    recoverRequired=10,
                ),
            },
        ),
        59: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Event_Wrapping),),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=3),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(18503, 18506)),
                2: RecoverFromCogObjective(
                    npc=(18506, 18503),
                    recoverItem=QuestItemName.SomethingShiny,
                    recoverChance=0.5,
                ),
                3: TreasureChestObjective(npc=18503, chestCount=3),
                4: RecoverFromCogObjective(
                    npc=18503,
                    cogTrack="m",
                    recoverItem=QuestItemName.GoldCoin,
                    recoverChance=0.55,
                    recoverRequired=10,
                ),
                5: VisitObjective(npc=(18503, 18502)),
                6: DeliverObjective(
                    npc=(18502, 18503), recoverItem=QuestItemName.StickyRedTape
                ),
            },
        ),
        60: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.PresentUniform),
                InventoryReward(ClothingBottomItemType.PresentUniformShorts),
                InventoryReward(ClothingBottomItemType.PresentUniformSkirt),
            ),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=4),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(18506, 2109)),
                2: RecoverFromCogObjective(
                    npc=2109,
                    cogLocation=ToontownGlobals.SillyStreet,
                    recoverItem=QuestItemName.Ticket,
                    recoverChance=0.45,
                ),
                3: VisitObjective(npc=(2109, 18506)),
                4: VisitObjective(npc=(18506, 1106)),
                5: QuestFishObjective(
                    npc=1106, fishType=QuestItemName.RedSuit, fishChance=1.0
                ),
                6: VisitObjective(npc=(1106, 18506)),
                7: VisitObjective(npc=(18506, 4133)),
                8: RecoverFromCogObjective(
                    npc=18506,
                    cogLocation=ToontownGlobals.AltoAvenue,
                    recoverItem=QuestItemName.SantasSuit,
                    recoverChance=0.45,
                ),
            },
        ),
        61: QuestChain(
            rewards=(InventoryReward(HatItemType.Hat_Santa_Red),),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=5),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=18506,
                    cogType="mb",
                    recoverItem=QuestItemName.Bag,
                    recoverChance=0.9,
                    recoverRequired=5,
                ),
                2: VisitObjective(npc=(18506, 18502)),
                3: RecoverFromCogObjective(
                    npc=18502,
                    cogTrack="m",
                    recoverItem=QuestItemName.DollarBill,
                    recoverChance=0.9,
                    recoverRequired=5,
                ),
                4: TreasureObjective(npc=18502, treasureCount=10, treasureType=0),
                5: RecoverFromCogObjective(
                    npc=(18502, 18506),
                    cogType="mb",
                    recoverItem=QuestItemName.SantasBag,
                    recoverChance=0.75,
                ),
            },
        ),
        62: QuestChain(
            rewards=(AntlersReward(HatItemType.Headband_Antlers),),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=6),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=18505,
                    cogTrack="s",
                    recoverItem=QuestItemName.PieceofRedTape,
                    recoverChance=0.65,
                    recoverRequired=4,
                ),
                2: DefeatCogObjective(npc=18505, cogCount=10, cogType="p"),
                3: DefeatCogObjective(npc=18505, cogCount=15, cogLevelMin=4),
                4: RecoverFromCogObjective(
                    npc=18505,
                    cogType="ms",
                    recoverItem=QuestItemName.Mustache,
                    recoverChance=0.65,
                    recoverRequired=4,
                ),
            },
        ),
        63: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.RedElfShirt),
                InventoryReward(ClothingBottomItemType.Shorts_Elf_Red),
            ),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=7),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(18506, 3226)),
                2: DefeatCogObjective(npc=3226, cogCount=15),
                3: CatchingGameObjective(npc=3226, fruitCount=5, zoneId=9000),
                4: QuestCollectableObjective(
                    npc=(3226, 18506), collectable=QuestCollectable.ToonselPresent
                ),
            },
        ),
        64: QuestChain(
            rewards=(
                InventoryReward(HatItemType.Hat_Soldier_Tradi),
                InventoryReward(HatItemType.Hat_Ragdoll_Regal),
            ),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=8),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=18501,
                    recoverItem=QuestItemName.ItemwithFlair,
                    recoverChance=0.65,
                    recoverRequired=10,
                ),
                2: RecoverFromCogObjective(
                    npc=18501,
                    cogType="pph",
                    recoverItem=QuestItemName.PaperMaterial,
                    recoverChance=0.75,
                    recoverRequired=5,
                ),
                3: TreasureObjective(npc=18501, treasureCount=10, treasureType=4),
            },
        ),
        65: QuestChain(
            rewards=(InventoryReward(HatItemType.Hat_Star),),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=9),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=18516,
                    cogType="gh",
                    recoverItem=QuestItemName.Glove,
                    recoverChance=0.5,
                    recoverRequired=2,
                ),
                2: RecoverFromCogObjective(
                    npc=18516,
                    cogTrack="l",
                    recoverItem=QuestItemName.ThickSuit,
                    recoverChance=0.4,
                ),
            },
        ),
        66: QuestChain(
            rewards=(InventoryReward(BackpackItemType.CandyCane),),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=10),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: MultiObjective(
                    TreasureObjective(
                        npc=18504, treasureCount=10, treasureType=6, npcReturnable=False
                    ),
                    TreasureObjective(
                        npc=18504, treasureCount=10, treasureType=0, npcReturnable=False
                    ),
                    SwimObjective(npc=18504, npcReturnable=False),
                ),
                2: VisitObjective(npc=18504),
                3: DeliverJellybeanObjective(npc=18504, jellybeans=100),
                4: RecoverFromCogObjective(
                    npc=18504,
                    cogType="tw",
                    recoverItem=QuestItemName.PackageofPlasticWrap,
                    recoverChance=1.0,
                    recoverRequired=5,
                ),
            },
        ),
        67: QuestChain(
            rewards=(InventoryReward(BackpackItemType.Snowboard),),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=11),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: QuestFishObjective(
                    npc=18523, fishType=QuestItemName.PlasticBoard, fishChance=1.0
                ),
                2: RecoverFromCogObjective(
                    npc=18523,
                    cogTrack="g",
                    recoverItem=QuestItemName.PieceofLining,
                    recoverChance=0.5,
                    recoverRequired=5,
                ),
                3: RecoverFromCogObjective(
                    npc=18523,
                    cogType="cbr",
                    recoverItem=QuestItemName.LeatherStrap,
                    recoverChance=0.75,
                    recoverRequired=2,
                ),
                4: TossPieObjective(npc=18523, pieType=10),
            },
        ),
        68: QuestChain(
            rewards=(InventoryReward(BackgroundItemType.Event_Winter2018_B),),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=12),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: QuestFishObjective(
                    npc=18523,
                    fishType=QuestItemName.Stick,
                    fishCount=5,
                    fishChance=1.0,
                    fishLocation=ToontownGlobals.OutdoorZone,
                ),
                2: VisitObjective(npc=(18523, 18501)),
                3: VisitObjective(npc=(18501, 18504)),
                4: VisitObjective(npc=(18504, 18506)),
                5: DeliverObjective(
                    npc=(18506, 18523), recoverItem=QuestItemName.SortaStockings
                ),
                6: DefeatCogObjective(npc=18523, cogType="f"),
            },
        ),
        69: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.ToonsmasPast),
                InventoryReward(ClothingBottomItemType.Skirt_ToonsmasPast),
                InventoryReward(ClothingBottomItemType.Shorts_ToonsmasPast),
                InventoryReward(HatItemType.Hat_Candle),
                InventoryReward(BackpackItemType.Extinguisher),
            ),
            startDate=toonselTownDateRange.startDatetime + timedelta(days=1),
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 2),),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(
                    npc=18517,
                    cogType="f",
                    recoverItem=QuestItemName.FlunkyGlasses,
                    recoverChance=0.85,
                ),
                2: VisitObjective(npc=(18517, 9230)),
                3: RecoverFromCogObjective(
                    npc=9230,
                    cogType="pp",
                    recoverItem=QuestItemName.Bandana,
                    recoverChance=0.9,
                    recoverRequired=10,
                ),
                4: VisitObjective(npc=(9230, 18517)),
                5: VisitObjective(npc=(18517, 1410)),
                6: VisitObjective(npc=(1410, 18517)),
            },
        ),
        70: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.ToonsmasPresent),
                InventoryReward(ClothingBottomItemType.Skirt_ToonsmasPresent),
                InventoryReward(ClothingBottomItemType.Shorts_ToonsmasPresent),
                InventoryReward(HatItemType.Headband_Present),
                InventoryReward(BackpackItemType.PresentCorn),
            ),
            startDate=toonselTownDateRange.startDatetime,
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.SideQuest, 69),),
            deletable=True,
            steps={
                1: VisitObjective(npc=(18518, 2320)),
                2: DefeatCogObjective(
                    npc=(2320, 18518),
                    cogCount=5,
                    cogLevelMin=3,
                    cogLocation=ToontownGlobals.PunchlinePlace,
                ),
                3: VisitObjective(npc=(18518, 1403)),
                4: DefeatCogObjective(
                    npc=(1403, 18518),
                    cogCount=5,
                    cogLevelMin=4,
                    cogLocation=ToontownGlobals.AnchorAvenue,
                ),
                5: VisitObjective(npc=(18518, 7101)),
                6: DefeatCogObjective(
                    npc=(1403, 18518),
                    cogCount=5,
                    cogLevelMin=4,
                    cogLocation=ToontownGlobals.KnightKnoll,
                ),
                7: VisitObjective(npc=(18518, 5213)),
                8: DefeatCogObjective(
                    npc=(5213, 18518),
                    cogCount=5,
                    cogLevelMin=5,
                    cogLocation=ToontownGlobals.DaisyDrive,
                ),
                9: VisitObjective(npc=(18518, 4116)),
                10: DefeatCogObjective(
                    npc=(4116, 18518),
                    cogCount=5,
                    cogLevelMin=6,
                    cogLocation=ToontownGlobals.AltoAvenue,
                ),
                11: VisitObjective(npc=(18518, 3327)),
                12: DefeatCogObjective(
                    npc=(3327, 18518),
                    cogCount=5,
                    cogLevelMin=6,
                    cogLocation=ToontownGlobals.PolarPlace,
                ),
                13: VisitObjective(npc=(18518, 6115)),
                14: RecoverFromCogObjective(
                    npc=6115,
                    cogLocation=ToontownGlobals.AlmondAvenue,
                    recoverItem=QuestItemName.AcornsontheCob,
                    recoverChance=0.95,
                    recoverRequired=5,
                ),
                15: VisitObjective(npc=(6115, 18518)),
                16: VisitObjective(npc=(18518, 9212)),
                17: RecoverFromCogObjective(
                    npc=(9112, 9212),
                    cogLocation=ToontownGlobals.PajamaPlace,
                    recoverItem=QuestItemName.IceCream,
                    recoverChance=0.95,
                    recoverRequired=5,
                ),
                18: VisitObjective(npc=(9212, 18518)),
            },
        ),
        71: QuestChain(
            rewards=(
                InventoryReward(ClothingTopItemType.ToonsmasFuture),
                InventoryReward(ClothingBottomItemType.Skirt_ToonsmasFuture),
                InventoryReward(ClothingBottomItemType.Shorts_ToonsmasFuture),
                InventoryReward(HatItemType.Hood_Future),
                InventoryReward(BackpackItemType.FutureWing),
                InventoryReward(BackpackItemType.FutureCloak),
                InventoryReward(BackpackItemType.FutureWingCloak),
            ),
            startDate=toonselTownDateRange.startDatetime,
            endDate=toonselTownDateRange.endDatetime,
            required=(QuestCompletionRequirement(QuestSource.SideQuest, 70),),
            deletable=True,
            steps={
                1: DeliverObjective(
                    npc=(18519, 18517), recoverItem=QuestItemName.Present
                ),
                2: DeliverObjective(
                    npc=(18517, 18518), recoverItem=QuestItemName.PairofGlasses
                ),
                3: VisitObjective(npc=(18518, 18517)),
                4: DeliverObjective(
                    npc=(18517, 18519), recoverItem=QuestItemName.Present
                ),
                5: DeliverObjective(
                    npc=(18519, 18518), recoverItem=QuestItemName.Present
                ),
                6: DeliverObjective(
                    npc=(18518, 18519), recoverItem=QuestItemName.LeftoverAcornsontheCob
                ),
                7: DeliverObjective(
                    npc=(18519, 2001), recoverItem=QuestItemName.Present
                ),
                8: VisitObjective(npc=(2001, 18519)),
            },
        ),
    },
)
