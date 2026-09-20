"""
This module contains the full QuestLine dictionary.
"""
from toontown.inventory.enums.ItemEnums import BackgroundItemType, HatItemType, BackpackItemType, GlassesItemType, ClothingTopItemType, FurnitureItemType
from toontown.quest3.QuestEnums import QuestSource, QuestCollectable, QuestItemName
from toontown.quest3.base.QuestChain import QuestChain
from toontown.quest3.base.QuestHistory import QuestHistory
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.base.QuestObjective import MultiObjective
from toontown.quest3.base.QuestReference import QuestId, QuestReference
from toontown.quest3.rewards import *
from toontown.quest3.objectives import *
from toontown.toonbase import ToontownGlobals

# TODO: Audit quests for legacy boardbots!

class MainQuestLineContainer(QuestLine):
    questSource = QuestSource.MainQuest

    def getStarterQuestData(self, skipTutorial: bool):
        """
        Gets the starter quest data.
        """
        if not skipTutorial:
            # Get the starter quests, from the start of the toontorial.
            startingQuestRef = [
                QuestReference(
                    QuestId(
                        questSource=self.questSource,
                        chainId=1,
                        objectiveId=1,
                    )
                ).toStruct()
            ]
            startingQuestHistory = []
        else:
            # Skip the toontorial, and get the refs/quest history resulting.
            startingQuestRef = [
                QuestReference(
                    QuestId(
                        questSource=self.questSource,
                        chainId=3,
                        objectiveId=1,
                    )
                ).toStruct()
            ]
            startingQuestHistory = [
                QuestHistory(QuestSource.MainQuest, 1).toStruct(),
                QuestHistory(QuestSource.MainQuest, 2).toStruct(),
            ]
        return startingQuestRef, startingQuestHistory


MainQuestLine = MainQuestLineContainer(
    questLine={
        1: QuestChain(
            nextChain=2,
            rewards=(MaxQuestCarryReward(4)),
            steps={
                1: VisitObjective(npc=2001),
            }
        ),
        2: QuestChain(
            nextChain=3,
            rewards=(InventoryReward(BackgroundItemType.PG_TTC), ExpReward(45)),
            dynamicRewards=(ExpReward(45),),
            steps={
                1: VisitObjective(npc=(2001, 2007), rewards=BeanReward(20)),
                2: TrolleyObjective(npc=2007),
                3: DefeatCogObjective(npc=2007, cogCount=2, cogLocation=ToontownGlobals.ToontownCentral,
                                      nextStep=(4, 5, 6, 7, 8)),
                4: DefeatCogObjective(npc=2007, cogCount=3, cogTrack='s', nextStep=9),
                5: DefeatCogObjective(npc=2007, cogCount=3, cogTrack='m', nextStep=9),
                6: DefeatCogObjective(npc=2007, cogCount=3, cogTrack='l', nextStep=9),
                7: DefeatCogObjective(npc=2007, cogCount=3, cogTrack='c', nextStep=9),
                8: DefeatCogObjective(npc=2007, cogCount=3, cogTrack='g', nextStep=9),
                9: VisitObjective(npc=(2007, 2008)),
            }
        ),
        3: QuestChain(
            nextChain=4,
            rewards=(BeanReward(10), ExpReward(234)),
            dynamicRewards=(BeanReward(10), ExpReward(234)),
            steps={
                1: VisitObjective(npc=(2008, 2311)),
                2: RecoverFromCogObjective(npc=2311, cogLocation=ToontownGlobals.ToontownCentral,
                                           recoverItem=QuestItemName.ExerciseSupplies, recoverChance=0.8),
                3: DefeatCogObjective(npc=2311, cogCount=3, cogLocation=ToontownGlobals.ToontownCentral),
                4: VisitObjective(npc=(2311, 2008)),
            }
        ),
        4: QuestChain(
            nextChain=5,
            rewards=(BeanReward(15), ExpReward(260)),
            dynamicRewards=(BeanReward(15), ExpReward(260)),
            steps={
                1: VisitObjective(npc=(2008, 2126)),
                2: RecoverFromCogObjective(npc=2126, cogLocation=ToontownGlobals.ToontownCentral,
                                           recoverItem=QuestItemName.LaughingGas, recoverChance=0.75),
                3: VisitObjective(npc=(2126, 2118)),
                4: RecoverFromCogObjective(npc=2118, cogLocation=ToontownGlobals.ToontownCentral,
                                           recoverItem=QuestItemName.JokeRepairTools, recoverChance=0.65),
                5: DeliverObjective(npc=(2118, 2126), recoverItem=QuestItemName.JokeRepairTools),
                6: VisitObjective(npc=(2126, 2008)),
            }
        ),
        5: QuestChain(
            nextChain=6,
            rewards=(BeanReward(18), ExpReward(279)),
            dynamicRewards=(BeanReward(18), ExpReward(279)),
            steps={
                1: VisitObjective(npc=(2008, 2009)),
                2: VisitObjective(npc=(2009, 2208)),
                3: ObtainObjective(npc=(2208, 2134), recoverItem=QuestItemName.ReservationTicket),
                4: DeliverObjective(npc=(2134, 2208), recoverItem=QuestItemName.ReservationTicket),
                5: RecoverFromCogObjective(npc=2208, cogLocation=ToontownGlobals.ToontownCentral,
                                           recoverItem=QuestItemName.UnstickingObject, recoverChance=0.5),
                6: DeliverObjective(npc=(2208, 2009), recoverItem=QuestItemName.DecorativeGlue),
                7: VisitObjective(npc=(2009, 2208)),
                8: QuestFishObjective(npc=2208, fishType=QuestItemName.GlassJar, fishChance=1.0,
                                      fishLocation=ToontownGlobals.ToontownCentral),
                9: DeliverObjective(npc=(2208, 2009), recoverItem=QuestItemName.Glue),
            }
        ),
        6: QuestChain(
            nextChain=7,
            rewards=(BeanReward(20), ExpReward(280)),
            dynamicRewards=(BeanReward(20), ExpReward(280)),
            steps={
                1: VisitObjective(npc=(2009, 2010)),
                2: VisitObjective(npc=(2010, 2002)),
                3: RecoverFromCogObjective(npc=2002, cogLocation=ToontownGlobals.ToontownCentral, cogType='pp',
                                           recoverItem=QuestItemName.AddingMachine, recoverChance=0.6),
                4: VisitObjective(npc=(2002, 2408)),
                5: RecoverFromCogObjective(npc=2408, cogLocation=ToontownGlobals.ToontownCentral,
                                           recoverItem=QuestItemName.MachineParts, recoverChance=0.85,
                                           recoverRequired=3),
                6: DeliverObjective(npc=(2408, 2002), recoverItem=QuestItemName.AddingMachine),
                7: VisitObjective(npc=(2002, 2010)),
            }
        ),
        7: QuestChain(
            nextChain=8,
            rewards=(BeanReward(20), ExpReward(288)),
            dynamicRewards=(BeanReward(20), ExpReward(288)),
            steps={
                1: VisitObjective(npc=(2010, 2201)),
                2: RecoverFromCogObjective(npc=2201, cogLocation=ToontownGlobals.ToontownCentral, cogType='cc',
                                           recoverItem=QuestItemName.PapercutProofGloves, recoverChance=0.7,
                                           recoverRequired=2),
                3: RecoverFromCogObjective(npc=2201, cogLocation=ToontownGlobals.ToontownCentral, cogType='p',
                                           recoverItem=QuestItemName.MailPackage, recoverChance=0.7),
                4: DeliverObjective(npc=(2201, 2128), recoverItem=QuestItemName.MailPackage),
                5: QuestFishObjective(npc=2128, fishType=QuestItemName.ClownTires, fishCount=4, fishChance=1.0,
                                      fishLocation=ToontownGlobals.ToontownCentral),
                6: VisitObjective(npc=(2128, 2010)),
            }
        ),
        8: QuestChain(
            nextChain=9,
            rewards=(BeanReward(22), ExpReward(316)),
            dynamicRewards=(BeanReward(22), ExpReward(316)),
            steps={
                1: VisitObjective(npc=(2010, 2007)),
                2: VisitObjective(npc=(2007, 2324)),
                3: VisitObjective(npc=(2324, 2315)),
                4: DefeatCogObjective(npc=2315, cogCount=5, cogLevelMin=2, 
                                      cogLocation=ToontownGlobals.ToontownCentral),
                5: VisitObjective(npc=(2315, 2324)),
                6: VisitObjective(npc=(2324, 2316)),
                7: DefeatCogObjective(npc=2316, cogCount=2, cogLocation=ToontownGlobals.ToontownCentral, cogType='pph'),
                8: VisitObjective(npc=(2316, 2324)),
                9: VisitObjective(npc=(2324, 2219)),
                10: DefeatCogObjective(npc=2219, cogCount=4, cogLocation=ToontownGlobals.LoopyLane),
                11: DeliverObjective(npc=(2219, 2324), recoverItem=QuestItemName.BoxOfMeatballProduct),
                12: VisitObjective(npc=(2324, 2007)),
            }
        ),
        9: QuestChain(
            nextChain=10,
            rewards=(BeanReward(20), ExpReward(320)),
            dynamicRewards=(BeanReward(20), ExpReward(320)),
            steps={
                1: VisitObjective(npc=(2007, 2404)),
                2: DefeatCogObjective(npc=2404, cogCount=3, cogLocation=ToontownGlobals.WackyWay),
                3: VisitObjective(npc=(2404, 2007)),
                4: VisitObjective(npc=(2007, 2117)),
                5: RecoverFromCogObjective(npc=2117, cogLocation=ToontownGlobals.ToontownCentral, cogType='p',
                                           recoverItem=QuestItemName.PencilShavings, recoverChance=0.95,
                                           recoverRequired=3),
                6: VisitObjective(npc=(2117, 2007)),
                7: VisitObjective(npc=(2007, 2215)),
                8: RecoverFromCogObjective(npc=2215, cogLocation=ToontownGlobals.ToontownCentral,
                                           recoverItem=QuestItemName.Springs, recoverChance=0.85, recoverRequired=3),
                9: VisitObjective(npc=(2215, 2007)),
            }
        ),
        10: QuestChain(
            nextChain=11,
            rewards=(BeanReward(20), ExpReward(322)),
            dynamicRewards=(BeanReward(20), ExpReward(322)),
            steps={
                1: VisitObjective(npc=(2007, 2001)),
                2: VisitObjective(npc=(2001, 2301)),
                3: VisitObjective(npc=(2301, 2312)),
                4: ObtainObjective(npc=(2312, 2301), recoverItem=QuestItemName.LoveLetter),
                5: RecoverFromCogObjective(npc=2301, cogType='dt', recoverItem=QuestItemName.LoveLetter,
                                           recoverChance=0.9),
                6: QuestFishObjective(npc=2301, fishType=QuestItemName.SupplyOfInk, fishChance=1.0,
                                      fishLocation=ToontownGlobals.ToontownCentral),
                7: DeliverObjective(npc=(2301, 2312), recoverItem=QuestItemName.LoveLetter),
                8: VisitObjective(npc=(2312, 2001)),
            }
        ),
        11: QuestChain(
            nextChain=12,
            rewards=(InventoryReward(BackgroundItemType.PG_BB), BeanReward(22), ExpReward(332)),
            dynamicRewards=(BeanReward(22), ExpReward(332)),
            steps={
                1: VisitObjective(npc=(2001, 2007)),
                2: VisitObjective(npc=(2007, 2402)),
                3: VisitObjective(npc=(2402, 2403)),
                4: InvestigateObjective(npc=(2402, 2403), zoneId=ToontownGlobals.Gagsoline),
                5: RecoverFromCogObjective(npc=(2403, 2007), cogLocation=ToontownGlobals.ToontownCentral, cogTrack='c',
                                           recoverItem=QuestItemName.Keys, recoverChance=0.5,
                                           zoneUnlocks=[ToontownGlobals.Gagsoline]),
                6: InvestigateObjective(npc=2007, zoneId=ToontownGlobals.Gagsoline),
                7: DefeatCogObjective(npc=2007, cogLocation=ToontownGlobals.WackyWay, cogType='derrman', taskManagerBoss=True),
            }
        ),
        12: QuestChain(
            nextChain=13,
            rewards=(BeanReward(50), ExpReward(1247)),
            dynamicRewards=(BeanReward(50), ExpReward(1247)),
            steps={
                1: VisitObjective(npc=(2007, 2001)),
                2: VisitObjective(npc=(2001, 1116)),
                3: VisitObjective(npc=(1116, 1003)),
                4: VisitObjective(npc=(1003, 1005)),
                5: VisitObjective(npc=(1005, 1328)),
                6: RecoverFromCogObjective(npc=1328, cogLocation=ToontownGlobals.DonaldsDock,
                                           recoverItem=QuestItemName.LostItem, recoverChance=0.7, recoverRequired=3),
                7: RecoverFromCogObjective(npc=1328, cogLocation=ToontownGlobals.DonaldsDock,
                                           recoverItem=QuestItemName.LostandFoundBox, recoverChance=0.65),
            }
        ),
        13: QuestChain(
            nextChain=14,
            rewards=(InventoryReward(HatItemType.Hat_Pirate_Classic), BeanReward(50), ExpReward(1439)),
            dynamicRewards=(BeanReward(50), ExpReward(1439)),
            steps={
                1: VisitObjective(npc=(1328, 1005)),
                2: VisitObjective(npc=(1005, 1203)),
                3: DefeatCogObjective(npc=1203, cogCount=6, cogLocation=ToontownGlobals.DonaldsDock),
                4: VisitObjective(npc=(1203, 1311)),
                5: RecoverFromCogObjective(npc=1311, cogType='dt', recoverItem=QuestItemName.SuitThread,
                                           recoverChance=0.85),
            }
        ),
        14: QuestChain(
            nextChain=15,
            rewards=(BeanReward(50), ExpReward(1454)),
            dynamicRewards=(BeanReward(50), ExpReward(1454)),
            steps={
                1: VisitObjective(npc=(1311, 1005)),
                2: VisitObjective(npc=(1005, 1004)),
                3: VisitObjective(npc=(1004, 1404)),
                4: RecoverFromCogObjective(npc=1404, cogType='p', recoverItem=QuestItemName.Pencil, recoverChance=0.9,
                                           recoverRequired=3),
                5: RecoverFromCogObjective(npc=1404, cogTrack='l', recoverItem=QuestItemName.Book, recoverChance=0.9,
                                           recoverRequired=2),
                6: VisitObjective(npc=(1404, 1004)),
            }
        ),
        15: QuestChain(
            nextChain=16,
            rewards=(BeanReward(50), ExpReward(1455)),
            dynamicRewards=(BeanReward(50), ExpReward(1455)),
            steps={
                1: VisitObjective(npc=(1004, 1101)),
                2: QuestFishObjective(npc=1101, fishType=QuestItemName.Binnacle, fishChance=0.55,
                                      fishLocation=ToontownGlobals.LighthouseLane),
                3: VisitObjective(npc=(1101, 1105)),
                4: DefeatCogObjective(npc=1105, cogCount=3, cogLevelMin=3,
                                      cogLocation=ToontownGlobals.DonaldsDock),
            }
        ),
        16: QuestChain(
            nextChain=17,
            rewards=(BeanReward(50), ExpReward(1464)),
            dynamicRewards=(BeanReward(50), ExpReward(1464)),
            steps={
                1: VisitObjective(npc=(1105, 1101)),
                2: VisitObjective(npc=(1105, 1122)),
                3: RecoverFromCogObjective(npc=1122, cogLocation=ToontownGlobals.DonaldsDock,
                                           recoverItem=QuestItemName.SparePart, recoverChance=0.9, recoverRequired=4),
                4: DefeatCogObjective(npc=1122, cogCount=3, cogLocation=ToontownGlobals.DonaldsDock),
                5: VisitObjective(npc=(1122, 1101)),
                6: VisitObjective(npc=(1101, 1419)),
                7: RecoverFromCogObjective(npc=1419, cogLocation=ToontownGlobals.DonaldsDock,
                                           recoverItem=QuestItemName.SpareMetal, recoverChance=0.7, recoverRequired=2),
                8: DeliverObjective(npc=(1419, 1101), recoverItem=QuestItemName.Binnacle),
                9: VisitObjective(npc=(1101, 1004)),
            }
        ),
        17: QuestChain(
            nextChain=18,
            rewards=(BeanReward(50), ExpReward(1470)),
            dynamicRewards=(BeanReward(50), ExpReward(1470)),
            steps={
                1: VisitObjective(npc=(1004, 1006)),
                2: VisitObjective(npc=(1006, 1402)),
                3: MultiObjective(
                    DefeatCogObjective(npc=1402, cogCount=2, cogLocation=ToontownGlobals.AnchorAvenue,
                                       npcReturnable=False),
                    DefeatCogObjective(npc=1402, cogCount=3, cogLocation=ToontownGlobals.LighthouseLane, cogTrack='l',
                                       npcReturnable=False),
                    DefeatCogObjective(npc=1402, cogLocation=ToontownGlobals.BuccaneerBoulevard, cogType='mm',
                                       npcReturnable=False),
                    DefeatCogObjective(npc=1402, cogCount=2, cogLevelMin=4, cogLocation=ToontownGlobals.SeaweedStreet,
                                       npcReturnable=False),
                ),
                4: VisitObjective(npc=1402),
                5: VisitObjective(npc=(1402, 1006)),
            }
        ),
        18: QuestChain(
            nextChain=19,
            rewards=(BeanReward(50), ExpReward(1484)),
            dynamicRewards=(BeanReward(50), ExpReward(1484)),
            steps={
                1: VisitObjective(npc=(1006, 1125)),
                2: DeliverGagObjective(npc=1125, gagCount=1, gagLevel=3),
                3: DefeatCogObjective(npc=1125, cogCount=2, cogLevelMin=4, 
                                      cogLocation=ToontownGlobals.BuccaneerBoulevard),
                4: VisitObjective(npc=(1125, 1006)),
            }
        ),
        19: QuestChain(
            nextChain=20,
            rewards=(BeanReward(50), ExpReward(1486)),
            dynamicRewards=(BeanReward(50), ExpReward(1486)),
            steps={
                1: VisitObjective(npc=(1006, 1003)),
                2: VisitObjective(npc=(1003, 1204)),
                3: RecoverFromCogObjective(npc=1204, cogLocation=ToontownGlobals.DonaldsDock,
                                           recoverItem=QuestItemName.BoxingGloves, recoverChance=0.6),
                4: VisitObjective(npc=(1204, 1107)),
                5: DefeatCogObjective(npc=(1204, 1107), cogCount=4, cogLevelMin=3, 
                                      cogLocation=ToontownGlobals.BuccaneerBoulevard),
                6: VisitObjective(npc=(1107, 1304)),
                7: DefeatCogObjective(npc=1304, cogCount=4, cogLevelMin=4, cogLocation=ToontownGlobals.DonaldsDock),
                8: VisitObjective(npc=(1304, 1418)),
                9: QuestFishObjective(npc=1418, fishType=QuestItemName.Swordfish, fishChance=1.0),
                10: RecoverFromCogObjective(npc=1418, cogLocation=ToontownGlobals.DonaldsDock,
                                            recoverItem=QuestItemName.MetalPlate, recoverChance=0.9),
                11: VisitObjective(npc=(1418, 1003)),
            }
        ),
        20: QuestChain(
            nextChain=21,
            rewards=(BeanReward(50), ExpReward(1492)),
            dynamicRewards=(BeanReward(50), ExpReward(1492)),
            steps={
                1: VisitObjective(npc=(1003, 1202)),
                2: RecoverFromCogObjective(npc=1202, cogLocation=ToontownGlobals.DonaldsDock, cogType='gh',
                                           recoverItem=QuestItemName.Shoe, recoverChance=0.95),
                3: RecoverFromCogObjective(npc=1202, cogLocation=ToontownGlobals.DonaldsDock, cogType='bc',
                                           recoverItem=QuestItemName.Numbers, recoverChance=0.95),
                4: RecoverFromCogObjective(npc=1202, cogLocation=ToontownGlobals.DonaldsDock, cogType='ins',
                                           recoverItem=QuestItemName.DebriefingList, recoverChance=1.0),
                5: VisitObjective(npc=(1202, 1003)),
                6: DeliverObjective(npc=(1003, 1116), recoverItem=QuestItemName.CogActivityChart),
                7: VisitObjective(npc=(1116, 1104)),
                8: RecoverFromCogObjective(npc=1104, cogLocation=ToontownGlobals.DonaldsDock, cogType='f',
                                           recoverItem=QuestItemName.GlassLens, recoverChance=0.5),
                9: VisitObjective(npc=(1104, 1405)),
                10: DefeatCogObjective(npc=1405, cogCount=7, cogLocation=ToontownGlobals.DonaldsDock),
                11: DeliverObjective(npc=(1405, 1104), recoverItem=QuestItemName.Telescope),
                12: ObtainObjective(npc=(1104, 1124), recoverItem=QuestItemName.Shoe),
                13: DeliverObjective(npc=(1405, 1104), recoverItem=QuestItemName.Shoe),
                14: VisitObjective(npc=(1104, 1116)),
            }
        ),
        21: QuestChain(
            nextChain=22,
            rewards=(InventoryReward(BackgroundItemType.PG_YOTT), BeanReward(50), ExpReward(1498)),
            dynamicRewards=(BeanReward(50), ExpReward(1498)),
            steps={
                1: VisitObjective(npc=(1116, 1302)),
                2: TreasureChestObjective(npc=1302, chestCount=2),
                3: VisitObjective(npc=(1302, 1124)),
                4: RecoverFromCogObjective(npc=1124, cogLocation=ToontownGlobals.DonaldsDock,
                                           recoverItem=QuestItemName.WoodenPlank, recoverChance=0.75,
                                           recoverRequired=3),
                5: VisitObjective(npc=(1124, 1121)),
                6: RecoverFromCogObjective(npc=1121, cogLocation=ToontownGlobals.DonaldsDock,
                                           recoverItem=QuestItemName.WoodcuttingTools, recoverChance=0.85,
                                           recoverRequired=3),
                7: DeliverObjective(npc=(1121, 1124), recoverItem=QuestItemName.HullParts),
                8: VisitObjective(npc=(1121, 1302)),
                9: DefeatCogObjective(npc=1302, cogCount=5, cogLocation=ToontownGlobals.LighthouseLane),
                10: VisitObjective(npc=(1302, 1116)),
                11: DefeatCogObjective(npc=(1116, 1410), cogCount=3, cogLevelMin=5,
                                       cogLocation=ToontownGlobals.AnchorAvenue, npcReturnable=False),
                12: VisitObjective(npc=(1116, 1410)),
                13: VisitObjective(npc=(1410, 1116)),
                14: DefeatCogObjective(npc=1116, cogLocation=ToontownGlobals.AnchorAvenue, cogType='dlao', taskManagerBoss=True),
            }
        ),
        22: QuestChain(
            nextChain=23,
            rewards=(BeanReward(100), ExpReward(3526)),
            dynamicRewards=(BeanReward(100), ExpReward(3526)),
            steps={
                1: VisitObjective(npc=(1116, 2001)),
                2: VisitObjective(npc=(2001, 7004)),
                3: VisitObjective(npc=(7004, 7113)),
                4: DefeatCogObjective(npc=7113, cogTrack='s', cogCount=5, npcReturnable=False),
                5: VisitObjective(npc=(7113, 7115)),
                6: DefeatCogObjective(npc=7115, cogTrack='m', cogCount=6, npcReturnable=False),
                7: VisitObjective(npc=(7115, 7300)),
                8: DefeatCogObjective(npc=7300, cogTrack='l', cogCount=6, npcReturnable=False),
                9: VisitObjective(npc=(7300, 7212)),
            }
        ),
        23: QuestChain(
            nextChain=24,
            rewards=(BeanReward(100), ExpReward(3539)),
            dynamicRewards=(BeanReward(100), ExpReward(3539)),
            steps={
                1: DefeatCogObjective(npc=7212, cogTrack='c', cogCount=7, npcReturnable=False),
                2: VisitObjective(npc=(7212, 7202)),
                3: DefeatCogObjective(npc=7202, cogTrack='g', cogCount=7, npcReturnable=False),
                4: VisitObjective(npc=(7202, 7004)),
            }
        ),
        24: QuestChain(
            nextChain=25,
            rewards=(BeanReward(100), ExpReward(3547)),
            dynamicRewards=(BeanReward(100), ExpReward(3547)),
            steps={
                1: VisitObjective(npc=(7004, 7002)),
                2: VisitObjective(npc=(7002, 7212)),
                3: RecoverFromCogObjective(npc=7212, cogType='mm', recoverItem=QuestItemName.Package, recoverChance=1.0),
                4: BuildingObjective(npc=(7212, 7002)),
            }
        ),
        25: QuestChain(
            nextChain=26,
            rewards=(BeanReward(100), ExpReward(3545)),
            dynamicRewards=(BeanReward(100), ExpReward(3545)),
            steps={
                1: VisitObjective(npc=(7002, 7304)),
                2: MultiObjective(
                    RecoverFromCogObjective(npc=(7304, 7002), cogLocation=ToontownGlobals.KnightKnoll,
                                            recoverItem=QuestItemName.Information, recoverChance=1.0, 
                                            recoverRequired=3, npcReturnable=False),
                    RecoverFromCogObjective(npc=(7304, 7002), cogLocation=ToontownGlobals.NobleNook,
                                            recoverItem=QuestItemName.Information, recoverChance=1.0,
                                            recoverRequired=3, npcReturnable=False),
                    RecoverFromCogObjective(npc=(7304, 7002), cogLocation=ToontownGlobals.WizardWay,
                                            recoverItem=QuestItemName.Information, recoverChance=1.0,
                                            recoverRequired=3, npcReturnable=False),
                ),
                3: DeliverObjective(npc=(7304, 7002), recoverItem=QuestItemName.Information),
            }
        ),
        26: QuestChain(
            nextChain=27,
            rewards=(InventoryReward(HatItemType.Helmet_Conquistador_Classic), BeanReward(100), ExpReward(3563)),
            dynamicRewards=(BeanReward(100), ExpReward(3563)),
            steps={
                1: VisitObjective(npc=(7002, 7003)),
                2: VisitObjective(npc=(7003, 7313)),
                3: VisitObjective(npc=(7313, 7106)),
                4: RecoverFromCogObjective(npc=7106, cogLocation=ToontownGlobals.YeOlde,
                                           recoverItem=QuestItemName.JugglingStick, recoverChance=0.6,
                                           recoverRequired=3, npcReturnable=False),
                5: VisitObjective(npc=(7106, 7303)),
                6: DefeatCogObjective(npc=(7303, 7106), cogCount=3, cogLevelMin=5),
            }
        ),
        27: QuestChain(
            nextChain=28,
            rewards=(InventoryReward(BackpackItemType.PirateSword), BeanReward(100), ExpReward(3581)),
            dynamicRewards=(BeanReward(100), ExpReward(3581)),
            steps={
                1: VisitObjective(npc=(7106, 7112)),
                2: RecoverFromBuildingObjective(npc=7112, buildingLocation=ToontownGlobals.YeOlde,
                                                recoverItem=QuestItemName.SwordMaterials, recoverChance=1.0),
            }
        ),
        28: QuestChain(
            nextChain=29,
            rewards=(BeanReward(100), ExpReward(3606)),
            dynamicRewards=(BeanReward(100), ExpReward(3606)),
            steps={
                1: VisitObjective(npc=(7112, 7313)),
                2: DefeatCogObjective(npc=(7313, 7003), cogCount=3, executive=True),
                3: VisitObjective(npc=(7003, 7104)),
                4: RecoverFromCogObjective(npc=7104, recoverItem=QuestItemName.ExecutivePromotionPapers, recoverChance=0.65, executive=True),
                5: VisitObjective(npc=(7104, 7116)),
                6: VisitObjective(npc=(7116, 7310)),
                7: RecoverFromCogObjective(npc=(7310, 7116), recoverItem=QuestItemName.StolenPotion, cogLevelMin=6),
                8: DefeatCogObjective(npc=7116, cogCount=6, executive=True),
                9: VisitObjective(npc=(7116, 7003)),
            }
        ),
        29: QuestChain(
            nextChain=30,
            rewards=(BeanReward(100), ExpReward(3615)),
            dynamicRewards=(BeanReward(100), ExpReward(3615)),
            steps={
                1: VisitObjective(npc=(7003, 7201)),
                2: DefeatCogObjective(npc=7201, cogCount=7),
                3: VisitObjective(npc=(7201, 7317)),
                4: DefeatCogObjective(npc=7317, cogCount=3, cogType='bs', npcReturnable=False),
                5: InvestigateObjective(npc=7317, zoneId=7301),  # Iconic.
                6: VisitObjective(npc=(7317, 7209)),
                7: DefeatCogObjective(npc=(7209, 7317), cogCount=8, cogLevelMin=4),
                8: VisitObjective(npc=(7317, 7314)),
                9: DefeatCogObjective(npc=(7314, 7317), cogCount=5, executive=True),
            }
        ),
        30: QuestChain(
            nextChain=31,
            rewards=(BeanReward(100), ExpReward(3616)),
            dynamicRewards=(BeanReward(100), ExpReward(3616)),
            steps={
                1: VisitObjective(npc=(7317, 7204)),
                2: DefeatCogObjective(npc=7204, cogCount=5, cogLevelMin=5, npcReturnable=False),
                3: VisitObjective(npc=(7204, 7214)),
                4: RecoverFromCogObjective(npc=(7214, 7204), recoverItem=QuestItemName.Wiring, recoverChance=1.0, recoverRequired=8),
                5: VisitObjective(npc=(7204, 7317)),
                6: VisitObjective(npc=(7317, 7316)),
                7: RecoverFromCogObjective(npc=(7316, 7317), cogType='ms', recoverItem=QuestItemName.Furniture, recoverChance=1.0),
                8: VisitObjective(npc=(7317, 7003)),
                9: DefeatCogObjective(npc=7003, cogLocation=ToontownGlobals.YeOlde, cogType='dopr', taskManagerBoss=True),
            }
        ),
        31: QuestChain(
            nextChain=32,
            rewards=(InventoryReward(BackgroundItemType.PG_DG), BeanReward(100), ExpReward(3620)),
            dynamicRewards=(BeanReward(100), ExpReward(3620)),
            steps={
                1: VisitObjective(npc=(7003, 2001)),
                2: VisitObjective(npc=(2001, 2003)),
                3: RecoverFromCogObjective(npc=2003, recoverItem=QuestItemName.MetalFraming, recoverChance=1.0, recoverRequired=5),
            }
        ),
        32: QuestChain(
            nextChain=33,
            rewards=(BeanReward(150), ExpReward(6478)),
            dynamicRewards=(BeanReward(150), ExpReward(6478)),
            steps={
                1: VisitObjective(npc=2001),
                2: VisitObjective(npc=(2001, 5313)),
                3: VisitObjective(npc=(5313, 5003)),
                4: VisitObjective(npc=(5003, 5207)),
                5: RecoverFromCogObjective(npc=5207, cogLocation=ToontownGlobals.DaisyGardens, cogTrack='s',
                                           recoverItem=QuestItemName.SellbotMetalPiece, recoverChance=0.75,
                                           recoverRequired=5),
                6: VisitObjective(npc=(5207, 5305)),
                7: DefeatCogObjective(npc=5305, cogCount=10, cogLocation=ToontownGlobals.TulipTerrace, cogTrack='s'),
                8: DeliverObjective(npc=(5305, 5207), recoverItem=QuestItemName.BoxofSunflowers),
                9: SwimObjective(npc=5207),
                10: VisitObjective(npc=(5207, 5003)),
                11: VisitObjective(npc=(5003, 5411)),
                12: BuildingObjective(npc=5411, floorMinimum=3),
                13: VisitObjective(npc=(5411, 5218)),
                14: DefeatCogObjective(npc=5218, cogCount=10, cogLocation=ToontownGlobals.DaisyGardens),
                15: VisitObjective(npc=(5218, 5411)),
                16: VisitObjective(npc=(5411, 5003)),
            }
        ),
        33: QuestChain(
            nextChain=34,
            rewards=(InventoryReward(HatItemType.Hair_Pompadour_Classic), BeanReward(150), ExpReward(6628)),
            dynamicRewards=(BeanReward(150), ExpReward(6628)),
            steps={
                1: VisitObjective(npc=(5003, 5002)),
                2: VisitObjective(npc=(5002, 5204)),
                3: VisitObjective(npc=(5204, 5002)),
                4: DefeatCogObjective(npc=5002, cogCount=6, cogLevelMin=6, cogLocation=ToontownGlobals.DaisyGardens),
                5: VisitObjective(npc=(5002, 5315)),
                6: DefeatCogObjective(npc=5315, cogCount=2, cogLocation=ToontownGlobals.DaisyGardens, cogType='mb'),
                7: VisitObjective(npc=(5315, 5308)),
                8: VisitObjective(npc=(5308, 5318)),
                9: DefeatCogObjective(npc=5318, cogCount=5, cogLocation=ToontownGlobals.DaisyGardens),
                10: DeliverObjective(npc=(5318, 5315), recoverItem=QuestItemName.CaesarSalad),
                11: VisitObjective(npc=(5315, 5204)),
                12: VisitObjective(npc=(5204, 5002)),
                13: VisitObjective(npc=(5002, 5416)),
                14: RecoverFromCogObjective(npc=5416, cogType='ms', recoverItem=QuestItemName.Hair, recoverChance=1.0,
                                            recoverRequired=4),
            }
        ),
        34: QuestChain(
            nextChain=35,
            rewards=(InventoryReward(GlassesItemType.Glasses_Miniblinds_Classic_White), BeanReward(150), ExpReward(6640)),
            dynamicRewards=(BeanReward(150), ExpReward(6640)),
            steps={
                1: RecoverFromCogObjective(npc=5416, cogLocation=ToontownGlobals.DaisyGardens,
                                           recoverItem=QuestItemName.Plastics, recoverChance=0.45),
            }
        ),
        35: QuestChain(
            nextChain=36,
            rewards=(BeanReward(150), ExpReward(6650)),
            dynamicRewards=(BeanReward(150), ExpReward(6650)),
            steps={
                1: VisitObjective(npc=(5416, 5002)),
                2: VisitObjective(npc=(5002, 5001)),
                3: VisitObjective(npc=(5001, 5102)),
                4: VisitObjective(npc=(5102, 5113)),
                5: VisitObjective(npc=(5113, 5102)),
                6: DefeatCogObjective(npc=(5102, 5113), cogCount=10, cogLocation=ToontownGlobals.PetuniaPlace),
                7: RecoverFromCogObjective(npc=(5113, 5102), cogLocation=ToontownGlobals.DaisyGardens, cogType='sd',
                                           recoverItem=QuestItemName.CompressPack, recoverChance=0.9,
                                           recoverRequired=2),
                8: VisitObjective(npc=(5102, 5001)),
                9: VisitObjective(npc=(5001, 5321)),
            }
        ),
        36: QuestChain(
            nextChain=37,
            rewards=(InventoryReward(HatItemType.Hat_Gag_Classic_FlowerPot), BeanReward(150), ExpReward(6654)),
            dynamicRewards=(BeanReward(150), ExpReward(6654)),
            steps={
                1: VisitObjective(npc=(5321, 5123)),
                2: DefeatCogObjective(npc=5123, cogCount=4, cogType='dl'),
                3: VisitObjective(npc=(5123, 5321)),
                4: VisitObjective(npc=(5321, 5400)),
                5: DefeatCogObjective(npc=5400, cogCount=2, cogType='bs'),
                6: VisitObjective(npc=(5400, 5321)),
                7: VisitObjective(npc=(5321, 5206)),
                8: RecoverFromCogObjective(npc=5206, cogTrack='g', recoverItem=QuestItemName.LightBlueButton,
                                           recoverChance=0.45),
            }
        ),
        37: QuestChain(
            nextChain=38,
            rewards=(BeanReward(150), ExpReward(6675)),
            dynamicRewards=(BeanReward(150), ExpReward(6675)),
            steps={
                1: VisitObjective(npc=(5206, 5321)),
                2: VisitObjective(npc=(5321, 5001)),
                3: VisitObjective(npc=(5001, 5004)),
            }
        ),
        38: QuestChain(
            nextChain=39,
            rewards=(BeanReward(150), ExpReward(6682)),
            dynamicRewards=(BeanReward(150), ExpReward(6682)),
            steps={
                1: CogFriendObjective(npc=5004),
                2: DefeatCogObjective(npc=5004, cogCount=12, cogLevelMin=5, cogLocation=ToontownGlobals.DaisyGardens),
                3: VisitObjective(npc=(5004, 5225)),
                4: DeliverObjective(npc=(5225, 5004), recoverItem=QuestItemName.LeavesAndPocketLint),
                5: VisitObjective(npc=(5004, 5128)),
                6: RecoverFromCogObjective(npc=5128, cogLocation=ToontownGlobals.DaisyGardens,
                                           recoverItem=QuestItemName.ClockParts, recoverChance=0.5, recoverRequired=5),
                7: DeliverObjective(npc=(5128, 5004), recoverItem=QuestItemName.Clock),
                8: DeliverObjective(npc=(5004, 5313), recoverItem=QuestItemName.Clock),
                9: VisitObjective(npc=(5313, 5004)),
            }
        ),
        39: QuestChain(
            nextChain=40,
            rewards=(BeanReward(150), ExpReward(6682)),
            dynamicRewards=(BeanReward(150), ExpReward(6682)),
            steps={
                1: RecoverFromCogObjective(npc=5004, cogType='shw', recoverItem=QuestItemName.ReedsBlankie,
                                           recoverChance=0.65),
                2: VisitObjective(npc=(5004, 5003)),
                3: VisitObjective(npc=(5003, 5313)),
                4: InvestigateObjective(npc=5313, zoneId=5830),
                5: InvestigateObjective(npc=5313, zoneId=10000),
                6: RecoverFromCogObjective(npc=5313, cogLocation=10000, recoverItem=QuestItemName.Information,
                                           recoverChance=0.45),
                7: InvestigateObjective(npc=5313, zoneId=10200),
            }
        ),
        40: QuestChain(
            nextChain=41,
            rewards=(BeanReward(150), ExpReward(6685)),
            dynamicRewards=(BeanReward(150), ExpReward(6685)),
            steps={
                1: CogDisguiseObjective(npc=5313, dept=4),
            }
        ),
        41: QuestChain(
            nextChain=42,
            rewards=(InventoryReward(BackgroundItemType.PG_MML), BeanReward(150), ExpReward(6692)),
            dynamicRewards=(BeanReward(150), ExpReward(6692)),
            steps={
                1: InvestigateObjective(npc=5313, zoneId=10100),
                2: BuildingObjective(npc=5313, floorMinimum=3, cogTrack='s'),
                3: DeliverGagObjective(npc=5313, gagCount=2, gagLevel=4),
                4: DefeatBossObjective(npc=5313, cogTrack='s'),
            }
        ),
        42: QuestChain(
            nextChain=43,
            rewards=(BeanReward(150), ExpReward(15144)),
            dynamicRewards=(BeanReward(150), ExpReward(15144)),
            steps={
                1: VisitObjective(npc=(5313, 2001)),
                2: VisitObjective(npc=(2001, 4002)),
                3: VisitObjective(npc=(4002, 4224)),
                4: RecoverFromCogObjective(npc=4224, cogLocation=ToontownGlobals.MinniesMelodyland,
                                           recoverItem=QuestItemName.Riddle, recoverChance=0.75, recoverRequired=4),
                5: MultiObjective(
                    QuestCollectableObjective(npc=4224, collectable=QuestCollectable.SwingsetA, npcReturnable=False),
                    QuestCollectableObjective(npc=4224, collectable=QuestCollectable.SwingsetB, npcReturnable=False),
                    QuestCollectableObjective(npc=4224, collectable=QuestCollectable.SwingsetC, npcReturnable=False),
                    QuestCollectableObjective(npc=4224, collectable=QuestCollectable.SwingsetD, npcReturnable=False),
                    wantAll=True,
                ),
                6: DeliverObjective(npc=4224, recoverItem=QuestItemName.Swingsets, rewards=(InventoryReward(FurnitureItemType.Prop_Candy_SwingSet))),
                7: VisitObjective(npc=(4224, 4002)),
            }
        ),
        43: QuestChain(
            nextChain=44,
            rewards=(BeanReward(150), ExpReward(15204)),
            dynamicRewards=(BeanReward(150), ExpReward(15204)),
            steps={
                1: VisitObjective(npc=(4002, 4213)),
                2: VisitObjective(npc=(4213, 4108)),
                3: TossPieObjective(npc=4108, pieType=5),
                4: DefeatCogObjective(npc=4108, cogCount=5, cogLevelMin=7, cogLocation=ToontownGlobals.MinniesMelodyland),
                5: BuildingObjective(npc=(4108, 4213), buildingCount=2),
                6: VisitObjective(npc=(4213, 4002)),
            }
        ),
        44: QuestChain(
            nextChain=45,
            rewards=(BeanReward(150), ExpReward(15232)),
            dynamicRewards=(BeanReward(150), ExpReward(15232)),
            steps={
                1: VisitObjective(npc=(4002, 4319)),
                2: DefeatCogObjective(npc=4319, cogCount=10, cogLevelMin=6, cogLocation=ToontownGlobals.MinniesMelodyland),
                3: VisitObjective(npc=(4319, 4406)),
                4: RecoverFromCogObjective(npc=4406, cogLocation=ToontownGlobals.MinniesMelodyland,
                                           recoverItem=QuestItemName.Kazoo, recoverChance=0.3),
                5: VisitObjective(npc=(4406, 4319)),
                6: BuildingObjective(npc=4319, floorMinimum=4),
                7: VisitObjective(npc=(4319, 4002)),
            }
        ),
        45: QuestChain(
            nextChain=46,
            rewards=(BeanReward(150), ExpReward(15238)),
            dynamicRewards=(BeanReward(150), ExpReward(15238)),
            steps={
                1: VisitObjective(npc=(4319, 4221)),
                2: DefeatCogObjective(npc=4221, cogCount=7, cogLevelMin=6, 
                                      cogLocation=ToontownGlobals.BaritoneBoulevard),
                3: RecoverFromCogObjective(npc=4221, cogType='ls', recoverItem=QuestItemName.MetalParts,
                                           recoverChance=0.8, recoverRequired=5),
                4: VisitObjective(npc=(4221, 4216)),
                5: RecoverFromCogObjective(npc=4216, cogTrack='g', recoverItem=QuestItemName.RubberCement,
                                           recoverChance=0.7),
                6: VisitObjective(npc=(4216, 4221)),
                7: VisitObjective(npc=(4319, 4219)),
                8: DefeatCogObjective(npc=4219, cogCount=3, cogType='le'),
                9: DeliverObjective(npc=(4219, 4221), recoverItem=QuestItemName.InsurancePapers),
                10: VisitObjective(npc=(4221, 4002)),
            }
        ),
        46: QuestChain(
            nextChain=47,
            rewards=(BeanReward(150), ExpReward(15257)),
            dynamicRewards=(BeanReward(150), ExpReward(15257)),
            steps={
                1: VisitObjective(npc=(4002, 4119)),
                2: InvestigateObjective(npc=4119, zoneId=4926),
                3: VisitObjective(npc=(4119, 4302)),
                4: RecoverFromCogObjective(npc=4302, cogType='nc', recoverItem=QuestItemName.BookingChart,
                                           recoverChance=0.75),
                5: VisitObjective(npc=(4302, 4119)),
                6: VisitObjective(npc=(4119, 4115)),
                7: RecoverFromCogObjective(npc=4115, cogLocation=ToontownGlobals.MinniesMelodyland,
                                           recoverItem=QuestItemName.Note, recoverChance=0.3),
                8: RecoverFromCogObjective(npc=4115, cogType='ls', recoverItem=QuestItemName.KitchenUtensils,
                                           recoverChance=1.0),
                9: VisitObjective(npc=(4115, 4119)),
                10: VisitObjective(npc=(4119, 4407)),
                11: RecoverFromCogObjective(npc=4407, cogType='ds', recoverItem=QuestItemName.Tweezers,
                                            recoverChance=0.72),
                12: VisitObjective(npc=(4407, 4119)),
            }
        ),
        47: QuestChain(
            nextChain=48,
            rewards=(BeanReward(150), ExpReward(15270)),
            dynamicRewards=(BeanReward(150), ExpReward(15270)),
            steps={
                1: VisitObjective(npc=(4119, 2003)),
                2: VisitObjective(npc=(2003, 4119)),
                3: InvestigateObjective(npc=4119, zoneId=11000),
                4: CogDisguiseObjective(npc=4119, dept=3),
            }
        ),
        48: QuestChain(
            nextChain=49,
            rewards=(InventoryReward(BackgroundItemType.PG_TB), BeanReward(150), ExpReward(15281)),
            dynamicRewards=(BeanReward(150), ExpReward(15281)),
            steps={
                1: VisitObjective(npc=(4119, 2008)),
                2: DefeatBossObjective(npc=(2008, 4119), cogTrack='m'),
                3: VisitObjective(npc=(4119, 4002)),
            }
        ),
        49: QuestChain(
            nextChain=50,
            rewards=(BeanReward(175), ExpReward(19481)),
            dynamicRewards=(BeanReward(175), ExpReward(19481)),
            steps={
                1: VisitObjective(npc=(4002, 3004)),
                2: VisitObjective(npc=(3004, 7003)),
                3: VisitObjective(npc=(7003, 3004)),
                4: InvestigateObjective(npc=3004, zoneId=3655, npcReturnable=False),
                5: DefeatCogObjective(npc=3004, cogCount=15, cogLevelMin=6, cogLocation=ToontownGlobals.WalrusWay),
                6: VisitObjective(npc=(3004, 3113)),
                7: DefeatCogObjective(npc=3113, cogLocation=ToontownGlobals.TheBrrrgh, cogType='mm'),
                8: VisitObjective(npc=(3113, 3107)),
                9: RecoverFromCogObjective(npc=3107, cogType='cr', recoverItem=QuestItemName.Earrings,
                                           recoverChance=0.8, recoverRequired=2),
                10: RecoverFromCogObjective(npc=3107, recoverItem=QuestItemName.Records, recoverChance=0.5),
                11: VisitObjective(npc=(3107, 3113)),
                12: VisitObjective(npc=(3113, 3311)),
                13: RecoverFromCogObjective(npc=3311, cogType='shw', recoverItem=QuestItemName.Pinecones,
                                            recoverChance=0.8, recoverRequired=3),
                14: VisitObjective(npc=(3311, 3113)),
            }
        ),
        50: QuestChain(
            nextChain=51,
            rewards=(BeanReward(175), ExpReward(19491)),
            dynamicRewards=(BeanReward(175), ExpReward(19491)),
            steps={
                1: VisitObjective(npc=(3113, 3128)),
                2: RecoverFromCogObjective(npc=3128, cogLocation=ToontownGlobals.TheBrrrgh, cogTrack='c',
                                           recoverItem=QuestItemName.StickyGeorgesKeys, recoverChance=0.4),
                3: VisitObjective(npc=(3311, 3217)),
                4: BuildingObjective(npc=3217, floorMinimum=4, buildingCount=2, npcReturnable=False),
                5: DeliverObjective(npc=3217, recoverItem=QuestItemName.HeaterParts),
                6: VisitObjective(npc=(3217, 3231)),
                7: RecoverFromCogObjective(npc=3231, recoverItem=QuestItemName.DryIce, recoverChance=0.3),
                8: VisitObjective(npc=(3231, 3310)),
                9: RecoverFromCogObjective(npc=3310, cogType='ms', recoverItem=QuestItemName.Teeth, recoverChance=0.5,
                                           recoverRequired=3),
                10: RecoverFromCogObjective(npc=3310, cogLocation=ToontownGlobals.TheBrrrgh, cogType='sd',
                                            recoverItem=QuestItemName.HeadMirror, recoverChance=0.8),
                11: ObtainObjective(npc=(3310, 3231), recoverItem=QuestItemName.DicedIce),
                12: DeliverObjective(npc=(3231, 3128), recoverItem=QuestItemName.DicedIce),
                13: VisitObjective(npc=(3128, 3113)),
                14: VisitObjective(npc=(3113, 3139)),
                15: BuildingObjective(npc=3139, floorMinimum=5),
                16: VisitObjective(npc=(3217, 7200)),
                17: DefeatCogObjective(npc=7200, cogCount=5, cogLevelMin=5, cogLocation=ToontownGlobals.YeOlde),
                18: VisitObjective(npc=(7200, 3113)),
            }
        ),
        51: QuestChain(
            nextChain=52,
            rewards=(BeanReward(175), ExpReward(19494)),
            dynamicRewards=(BeanReward(175), ExpReward(19494)),
            steps={
                1: VisitObjective(npc=(3113, 3111)),
                2: VisitObjective(npc=(3111, 3208)),
                3: BuildingObjective(npc=3208, cogTrack='l', floorMinimum=3, buildingCount=3),
                4: DefeatCogObjective(npc=3208, cogCount=15, cogLocation=ToontownGlobals.TheBrrrgh, cogTrack='l'),
                5: VisitObjective(npc=(3208, 3402)),
                6: DefeatCogObjective(npc=3402, cogCount=50),
                7: DeliverObjective(npc=(3402, 3111), recoverItem=QuestItemName.Puppies),
                8: MultiObjective(
                    RecoverFromCogObjective(npc=3111, cogType='shw', recoverItem=QuestItemName.Fin,
                                            recoverChance=1.0, npcReturnable=False),
                    RecoverFromCogObjective(npc=3111, cogType='tbc', recoverItem=QuestItemName.Cheese,
                                            recoverChance=1.0, npcReturnable=False),
                    RecoverFromCogObjective(npc=3111, cogType='bw', recoverItem=QuestItemName.FlavoringPowder,
                                            recoverChance=1.0, npcReturnable=False),
                ),
                9: DeliverObjective(npc=3111, recoverItem=QuestItemName.BigBurgerIngredients),
                10: DefeatCogObjective(npc=3111, cogCount=5, cogLocation=ToontownGlobals.WalrusWay),
                11: VisitObjective(npc=(3111, 3113)),
            }
        ),
        52: QuestChain(
            nextChain=53,
            rewards=(BeanReward(175), ExpReward(19514)),
            dynamicRewards=(BeanReward(175), ExpReward(19514)),
            steps={
                1: VisitObjective(npc=(3113, 3218)),
                2: RecoverFromBuildingObjective(npc=3218, cogTrack='l', recoverItem=QuestItemName.StorageDocuments,
                                                recoverChance=100, zoneUnlocks=[ToontownGlobals.BlizzardWizard]),
            }
        ),
        53: QuestChain(
            nextChain=54,
            rewards=(BeanReward(175), ExpReward(19533)),
            dynamicRewards=(BeanReward(175), ExpReward(19533)),
            steps={
                1: InvestigateObjective(npc=(3218, 3112), zoneId=ToontownGlobals.BlizzardWizard,
                                        npcReturnable=False, zoneUnlocks=[ToontownGlobals.BlizzardWizard]),
                2: VisitObjective(npc=3112),
                3: CogFriendObjective(npc=3112),
                4: DefeatCogObjective(npc=3112, cogCount=7, cogType='mi'),
                5: BuildingObjective(npc=3112, cogTrack='s', floorMinimum=3, buildingCount=2),
                6: DeliverGagObjective(npc=3112, gagCount=30, gagLevel=0),
                7: DeliverGagObjective(npc=3112, gagCount=1, gagLevel=6),
            }
        ),
        54: QuestChain(
            nextChain=55,
            rewards=(BeanReward(175), ExpReward(19542)),
            dynamicRewards=(BeanReward(175), ExpReward(19542)),
            steps={
                1: RecoverFromCogObjective(npc=3112, cogType='hho', recoverItem=QuestItemName.Tie,
                                           recoverChance=0.85, zoneUnlocks=[ToontownGlobals.BlizzardWizard]),
                2: RecoverFromCogObjective(npc=3112, cogType='f', recoverItem=QuestItemName.Glasses, recoverChance=0.5),
                3: RecoverFromCogObjective(npc=3112, cogType='shw', recoverItem=QuestItemName.Monacle,
                                           recoverChance=0.5),
                4: RecoverFromCogObjective(npc=3112, cogType='mh', recoverItem=QuestItemName.Shades,
                                           recoverChance=0.95),
                5: VisitObjective(npc=(3112, 3204)),
                6: DefeatCogObjective(npc=3204, cogCount=14, cogLocation=ToontownGlobals.SleetStreet),
                7: DeliverObjective(npc=(3204, 3112), recoverItem=QuestItemName.Shades),
                8: TreasureObjective(npc=3112, treasureCount=10, treasureType=7),
                9: RecoverFromCogObjective(npc=3112, cogLocation=11000, cogType='supervis',
                                           recoverItem=QuestItemName.CoinFlavoredBreathMint, recoverChance=1.0),
                10: BuildingObjective(npc=3112, floorMinimum=4, buildingCount=10),
                11: BuildingObjective(npc=3112, floorMinimum=5),
            }
        ),
        55: QuestChain(
            nextChain=56,
            rewards=(BeanReward(175), ExpReward(19578)),
            dynamicRewards=(BeanReward(175), ExpReward(19578)),
            steps={
                1: VisitObjective(npc=(3112, 3004), zoneUnlocks=[ToontownGlobals.BlizzardWizard]),
                2: VisitObjective(npc=(3004, 3112)),
                3: InvestigateObjective(npc=3112, zoneId=12000),
                4: DefeatCogObjective(npc=3112, cogCount=20, cogLocation=12000, npcReturnable=False),
                5: DeliverObjective(npc=3112, recoverItem=QuestItemName.CogParts),
                6: VisitObjective(npc=(3112, 3310)),
                7: RecoverFromCogObjective(npc=3310, cogLocation=ToontownGlobals.TheBrrrgh,
                                           recoverItem=QuestItemName.ExternalTemperatureSensor, recoverChance=0.6,
                                           recoverRequired=5),
                8: DeliverObjective(npc=(3310, 3112), recoverItem=QuestItemName.SensorSuitPiece),
                9: CogDisguiseObjective(npc=3112, dept=2),
            }
        ),
        56: QuestChain(
            nextChain=57,
            rewards=(InventoryReward(BackgroundItemType.PG_AA), BeanReward(175), ExpReward(19606)),
            dynamicRewards=(BeanReward(175), ExpReward(19606)),
            steps={
                1: VisitObjective(npc=(3112, 3004)),
                2: VisitObjective(npc=(3004, 2009)),
                3: DefeatBossObjective(npc=(2009, 3004), cogTrack='l'),
            }
        ),
        57: QuestChain(
            nextChain=58,
            rewards=(BeanReward(200), ExpReward(21460)),
            dynamicRewards=(BeanReward(200), ExpReward(21460)),
            steps={
                1: VisitObjective(npc=(3004, 2001)),
                2: VisitObjective(npc=(2001, 2010)),
                3: VisitObjective(npc=(2010, 6203)),
                4: DefeatCogObjective(npc=6203, cogCount=75, cogLevelMin=5),
                5: DefeatCogObjective(npc=6203, cogCount=35, cogLevelMin=7),
                6: BuildingObjective(npc=6203, floorMinimum=5, buildingCount=2),
            }
        ),
        58: QuestChain(
            nextChain=59,
            rewards=(BeanReward(200), ExpReward(21485)),
            dynamicRewards=(BeanReward(200), ExpReward(21485)),
            steps={
                1: VisitObjective(npc=(6203, 6004)),
                2: VisitObjective(npc=(6004, 6401)),
                3: RecoverFromCogObjective(npc=6401, cogType='cr', recoverItem=QuestItemName.Purse, recoverChance=0.65),
                4: DefeatCogObjective(npc=6401, cogCount=20, cogLocation=ToontownGlobals.OutdoorZone),
                5: VisitObjective(npc=(6401, 6409)),
                6: DefeatCogObjective(npc=6409, cogCount=25, cogTrack='s'),
            }
        ),
        59: QuestChain(
            nextChain=60,
            rewards=(BeanReward(200), ExpReward(21488)),
            dynamicRewards=(BeanReward(200), ExpReward(21488)),
            steps={
                1: VisitObjective(npc=(6409, 6004)),
                2: VisitObjective(npc=(6004, 6403)),
                3: DefeatCogObjective(npc=6403, cogCount=15, cogLevelMin=8),
                4: DefeatCogObjective(npc=6403, cogCount=20, cogTrack='c'),
                5: VisitObjective(npc=(6403, 6209)),
                6: RecoverFromCogObjective(npc=6209, cogLocation=ToontownGlobals.OutdoorZone,
                                           recoverItem=QuestItemName.Camera, recoverChance=0.65, recoverRequired=5),
                7: DeliverObjective(npc=(6209, 6403), recoverItem=QuestItemName.Film),
            }
        ),
        60: QuestChain(
            nextChain=61,
            rewards=(BeanReward(200), ExpReward(21535)),
            dynamicRewards=(BeanReward(200), ExpReward(21535)),
            steps={
                1: VisitObjective(npc=(6403, 6004)),
                2: VisitObjective(npc=(6004, 6216)),
                3: RecoverFromCogObjective(npc=6216, cogLocation=ToontownGlobals.OutdoorZone,
                                           recoverItem=QuestItemName.ShinyMetalPlates, recoverChance=0.65,
                                           recoverRequired=5),
                4: BuildingObjective(npc=6216, floorMinimum=5),
                5: VisitObjective(npc=(6216, 6303)),
                6: RecoverFromCogObjective(npc=6303, cogTrack='g', recoverItem=QuestItemName.ShinyMetalPlates,
                                           recoverChance=0.8, recoverRequired=5),
                7: VisitObjective(npc=(6303, 6216)),
                8: RecoverFromCogObjective(npc=6216, cogLocation=ToontownGlobals.OutdoorZone,
                                           recoverItem=QuestItemName.CrazyDynamite, recoverChance=0.4),
            }
        ),
        61: QuestChain(
            nextChain=62,
            rewards=(BeanReward(200), ExpReward(21536)),
            dynamicRewards=(BeanReward(200), ExpReward(21536)),
            steps={
                1: VisitObjective(npc=(6216, 6004)),
                2: VisitObjective(npc=(6004, 6413)),
                3: QuestFishObjective(npc=6413, fishType=QuestItemName.WoodenPlank, fishCount=5, fishChance=0.85),
                4: DefeatFacilityObjective(npc=6413, facilityId=10000, npcReturnable=False),
                5: DeliverObjective(npc=6413, recoverItem=QuestItemName.SuitSealantPaste),
            }
        ),
        62: QuestChain(
            nextChain=63,
            rewards=(BeanReward(200), ExpReward(21541)),
            dynamicRewards=(BeanReward(200), ExpReward(21541)),
            steps={
                1: VisitObjective(npc=(6413, 6004)),
                2: VisitObjective(npc=(6004, 6111)),
                3: RecoverFromCogObjective(npc=6111, cogType='bw', recoverItem=QuestItemName.Wig, recoverChance=0.65),
            }
        ),
        63: QuestChain(
            nextChain=64,
            rewards=(BeanReward(200), ExpReward(21550)),
            dynamicRewards=(BeanReward(200), ExpReward(21550)),
            steps={
                1: VisitObjective(npc=(6413, 6004)),
                2: VisitObjective(npc=(6004, 6301)),
                3: DefeatCogObjective(npc=6301, cogCount=45),
            }
        ),
        64: QuestChain(
            nextChain=65,
            rewards=(BeanReward(200), ExpReward(21552)),
            dynamicRewards=(BeanReward(200), ExpReward(21552)),
            steps={
                1: VisitObjective(npc=(6413, 6004)),
                2: VisitObjective(npc=(6004, 6306)),
                3: DefeatCogObjective(npc=6306, cogCount=35, npcReturnable=False),
                4: DefeatCogObjective(npc=6306, cogCount=15, cogLevelMin=8, executive=True, npcReturnable=False),
                5: BuildingObjective(npc=6306, floorMinimum=5),
            }
        ),
        65: QuestChain(
            nextChain=66,
            rewards=(InventoryReward(HatItemType.Helmet_Roman_Classic), BeanReward(200), ExpReward(21578)),
            dynamicRewards=(BeanReward(200), ExpReward(21578)),
            steps={
                1: VisitObjective(npc=(6306, 6004)),
                2: DeliverGagObjective(npc=6004, gagCount=1, gagLevel=7),
                3: VisitObjective(npc=(6306, 6203)),
            }
        ),
        66: QuestChain(
            nextChain=67,
            rewards=(InventoryReward(BackgroundItemType.PG_DDL), BeanReward(200), ExpReward(21578)),
            dynamicRewards=(BeanReward(200), ExpReward(21578)),
            steps={
                1: CogDisguiseObjective(npc=6203, dept=1),
                2: VisitObjective(npc=(6203, 2010)),
                3: DefeatBossObjective(npc=(2010, 6203), cogTrack='c'),
            }
        ),
        67: QuestChain(
            nextChain=68,
            rewards=(BeanReward(250), ExpReward(20164)),
            dynamicRewards=(BeanReward(250), ExpReward(20164)),
            steps={
                1: VisitObjective(npc=(6203, 2001)),
                2: VisitObjective(npc=(2001, 2003)),
                3: VisitObjective(npc=(2003, 9801)),
                4: DefeatCogObjective(npc=9801, cogCount=45, executive=True),
                5: VisitObjective(npc=(9801, 9005)),
            }
        ),
        68: QuestChain(
            nextChain=69,
            rewards=(BeanReward(250), ExpReward(20172)),
            dynamicRewards=(BeanReward(250), ExpReward(20172)),
            steps={
                1: QuestFishObjective(npc=9005, fishType=QuestItemName.OldBoot, fishCount=4, fishChance=1.0),
                2: TossPieObjective(npc=9005, pieType=9),
                3: RecoverFromCogObjective(npc=9005, cogType='mi', recoverItem=QuestItemName.Key, recoverChance=1.0,
                                           recoverRequired=5),
                4: RecoverFromCogObjective(npc=9005, cogType='le', recoverItem=QuestItemName.Key, recoverChance=1.0,
                                           recoverRequired=5),
                5: VisitObjective(npc=(9005, 9004)),
                6: TreasureObjective(npc=9004, treasureCount=10, treasureType=5),
                7: DefeatCogObjective(npc=9004, cogCount=10, cogType='ls'),
                8: VisitObjective(npc=(9004, 9801)),
                9: VisitObjective(npc=(9801, 9004)),
            }
        ),
        69: QuestChain(
            nextChain=70,
            rewards=(BeanReward(250), ExpReward(20174)),
            dynamicRewards=(BeanReward(250), ExpReward(20174)),
            steps={
                1: VisitObjective(npc=(9004, 9203)),
                2: RecoverFromCogObjective(npc=9203, cogType='tbc', recoverItem=QuestItemName.StinkyCheese,
                                           recoverChance=0.65),
                3: BuildingObjective(npc=9203, floorMinimum=6),
                4: DefeatFacilityObjective(npc=(9203, 9004), facilityId=12000),
                5: VisitObjective(npc=(9004, 9102)),
                6: DefeatCogObjective(npc=9102, cogCount=40, cogLocation=ToontownGlobals.DonaldsDreamland),
                7: RecoverFromCogObjective(npc=9102, cogTrack='c', recoverItem=QuestItemName.PieceofCloth,
                                           recoverChance=0.75, recoverRequired=5),
                8: DeliverObjective(npc=(9102, 9216), recoverItem=QuestItemName.Pajamas),
                9: RecoverFromCogObjective(npc=(9216, 9102), cogLocation=ToontownGlobals.DonaldsDreamland,
                                           recoverItem=QuestItemName.Pajamas, recoverChance=0.4),
                10: VisitObjective(npc=(9216, 9004)),
            }
        ),
        70: QuestChain(
            nextChain=71,
            rewards=(BeanReward(250), ExpReward(20188)),
            dynamicRewards=(BeanReward(250), ExpReward(20188)),
            steps={
                1: VisitObjective(npc=(9004, 9006)),
                2: DefeatCogObjective(npc=9006, cogCount=35, cogTrack='c'),
                3: DeliverObjective(npc=(9006, 9801), recoverItem=QuestItemName.Drawing),
                4: VisitObjective(npc=(9801, 9006)),
                5: VisitObjective(npc=(9006, 9127)),
                6: VisitObjective(npc=(9127, 9128)),
                7: DefeatCogObjective(npc=9128, cogCount=15, cogLocation=ToontownGlobals.LullabyLane),
                8: BuildingObjective(npc=(9128, 9127), buildingLocation=ToontownGlobals.DonaldsDreamland),
                9: VisitObjective(npc=(9127, 9126)),
                10: RecoverFromCogObjective(npc=9126, cogType='shw', recoverItem=QuestItemName.Feather,
                                            recoverChance=0.9, recoverRequired=3),
                11: RecoverFromCogObjective(npc=9126, cogType='bw', recoverItem=QuestItemName.Wig, recoverChance=0.9,
                                            recoverRequired=5),
                12: VisitObjective(npc=(9126, 9127)),
                13: VisitObjective(npc=(9127, 9006)),
            }
        ),
        71: QuestChain(
            nextChain=72,
            rewards=(BeanReward(250), ExpReward(20189)),
            dynamicRewards=(BeanReward(250), ExpReward(20189)),
            steps={
                1: VisitObjective(npc=(9006, 9805)),
                2: DefeatCogObjective(npc=9805, cogCount=15, cogLevelMin=11),
                3: RecoverFromCogObjective(npc=9805, cogType='mh', recoverItem=QuestItemName.MagicBeamProjectorParts,
                                           recoverChance=0.5),
                4: VisitObjective(npc=(9805, 9006)),
                5: VisitObjective(npc=(9006, 9129)),
                6: DefeatCogObjective(npc=9129, cogCount=20, cogLevelMin=8, executive=True),
                7: VisitObjective(npc=(9129, 9131)),
                8: VisitObjective(npc=(9131, 9129)),
                9: DefeatCogObjective(npc=9129, cogCount=20, cogLevelMin=12),
                10: VisitObjective(npc=(9129, 9131)),
                11: VisitObjective(npc=(9131, 9006)),
            }
        ),
        72: QuestChain(
            nextChain=73,
            rewards=(BeanReward(250), ExpReward(20190)),
            dynamicRewards=(BeanReward(250), ExpReward(20190)),
            steps={
                1: VisitObjective(npc=(9006, 9007)),
                2: VisitObjective(npc=(9007, 9111)),
                3: DeliverJellybeanObjective(npc=9111, jellybeans=2000),
                4: VisitObjective(npc=(9111, 9007)),
                5: VisitObjective(npc=(9007, 9217)),
                6: DefeatCogObjective(npc=9217, cogType='shw'),
                7: RecoverFromCogObjective(npc=9217, cogTrack='m', recoverItem=QuestItemName.Dime, recoverChance=0.8),
                8: VisitObjective(npc=(9217, 9007)),
                9: VisitObjective(npc=(9007, 9005)),
            }
        ),
        73: QuestChain(
            nextChain=74,
            rewards=(BeanReward(250), ExpReward(20204)),
            dynamicRewards=(BeanReward(250), ExpReward(20204)),
            steps={
                1: VisitObjective(npc=(9005, 9214)),
                2: VisitObjective(npc=(9214, 9803)),
                3: VisitObjective(npc=(9803, 9125)),
                4: VisitObjective(npc=(9125, 9005)),
            }
        ),
        74: QuestChain(
            nextChain=75,
            rewards=(BeanReward(250), ExpReward(20249)),
            dynamicRewards=(BeanReward(250), ExpReward(20249)),
            steps={
                1: VisitObjective(npc=(9005, 9801)),
                2: VisitObjective(npc=(9801, 9804)),
                3: DefeatFacilityObjective(npc=9804, facilityId=10000),
                4: DefeatBossObjective(npc=9804, cogTrack='s'),
                5: DefeatFacilityObjective(npc=9804, facilityId=13000),
                6: DeliverObjective(npc=(9804, 9801), recoverItem=QuestItemName.FolderofDocuments),
                7: VisitObjective(npc=(9801, 2007)),
                8: VisitObjective(npc=(2007, 2001)),
                9: DefeatDirectorsObjective(npc=(2001, 2007)),
            }
        ),
        75: QuestChain(
            rewards=(InventoryReward(ClothingTopItemType.GoldMedal), BeanReward(250), ExpReward(20308)),
            dynamicRewards=(BeanReward(250), ExpReward(20308)),
            steps={
                1: VisitObjective(npc=(2007, 2001)),
            }
        ),
    }
)
