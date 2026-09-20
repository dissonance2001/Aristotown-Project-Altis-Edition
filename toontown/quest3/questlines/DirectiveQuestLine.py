from toontown.inventory.enums.ItemEnums import BackgroundItemType, NameplateItemType, ProfilePoseItemType
from toontown.quest3.QuestEnums import QuestSource, QuestItemName
from toontown.quest3.base.QuestChain import QuestChain
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.rewards import *
from toontown.quest3.requirements import *
from toontown.quest3.objectives import *
from toontown.toonbase import ToontownGlobals


class DirectiveContainer(QuestLine):
    questSource = QuestSource.Directive


DirectiveQuestLine = DirectiveContainer(
    questLine={
        1: QuestChain(
            required=(QuestCompletionRequirement(QuestSource.MainQuest, 56), SuitDisguiseRequirement(2, 7, 7, False)),
            rewards=DummyReward('Executive Lobby Key'),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(npc=12101, cogLocation=12000, cogType='clerk', recoverItem=QuestItemName.PatentReport, recoverChance=1.0, recoverRequired=2),
                2: RecoverFromBuildingObjective(npc=12101, cogTrack='l', recoverItem=QuestItemName.BusinessReport, recoverChance=100),
                3: RecoverFromCogObjective(npc=12101, cogType='mm', recoverItem=QuestItemName.Assignment, recoverChance=0.5),
                4: RecoverFromCogObjective(npc=12101, cogType='bw', executive=True, recoverItem=QuestItemName.Assignment, recoverChance=0.75),
            }
        ),
        2: QuestChain(
            rewards=(CogPromoteReward(2), InventoryReward(BackgroundItemType.Tasks_Judy)),
            required=(QuestCompletionRequirement(QuestSource.Directive, 1), SuitDisguiseRequirement(2, 1, 6, True)),
            deletable=True,
            steps={
                1: VisitObjective(npc=(12101, 7105)),
                2: VisitObjective(npc=(7105, 7317)),
                3: DefeatFacilityObjective(npc=7317, facilityId=12000),
                4: DefeatBossObjective(npc=7317, cogTrack='l'),
                5: BuildingObjective(npc=7317, floorMinimum=5, buildingCount=2),
                6: VisitObjective(npc=(7317, 12101)),
            }
        ),
        3: QuestChain(
            rewards=(CogPromoteReward(2), LaffReward(1)),
            required=(QuestCompletionRequirement(QuestSource.Directive, 2), SuitDisguiseRequirement(2, 2, 9, True)),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(npc=12101, cogType='nn', recoverItem=QuestItemName.Needle, recoverChance=0.5, recoverRequired=2),
                2: VisitObjective(npc=(12101, 5312)),
                3: RecoverFromCogObjective(npc=5312, cogType='bc', recoverItem=QuestItemName.BeanString, recoverChance=0.75, recoverRequired=8),
                4: VisitObjective(npc=(5312, 12101)),
                5: VisitObjective(npc=(12101, 7317)),
                6: VisitObjective(npc=(7317, 5128)),
                7: BuildingObjective(npc=5128, cogTrack='l', floorMinimum=6),
                8: DefeatFacilityObjective(npc=5128, facilityId=12000),
                9: VisitObjective(npc=(5128, 12101)),
            }
        ),
        4: QuestChain(
            rewards=(CogPromoteReward(2), InventoryReward(ProfilePoseItemType.Megaphone)),
            required=(QuestCompletionRequirement(QuestSource.Directive, 3), SuitDisguiseRequirement(2, 3, 7, True)),
            deletable=True,
            steps={
                1: VisitObjective(npc=(12101, 3231)),
                2: RecoverFromBuildingObjective(npc=(3231, 12101), cogTrack='s', recoverItem=QuestItemName.Ice, recoverChance=100, recoverRequired=3),
                3: DefeatFacilityObjective(npc=12101, facilityId=12000, facilityCount=3),
                4: VisitObjective(npc=(12101, 3303)),
                5: VisitObjective(npc=(3303, 1405)),
                6: DefeatCogObjective(npc=1405, cogCount=3, cogType='cv'),
                7: DefeatCogObjective(npc=1405, cogCount=6, cogType='cv'),
                8: VisitObjective(npc=(1405, 12101)),
            }
        ),
        5: QuestChain(
            rewards=(CogPromoteReward(2), LaffReward(1)),
            required=(QuestCompletionRequirement(QuestSource.Directive, 4), SuitDisguiseRequirement(2, 4, 14, True)),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(npc=12101, cogType='p', recoverItem=QuestItemName.Pencil, recoverChance=0.33),
                2: RecoverFromCogObjective(npc=12101, cogType='mi', recoverItem=QuestItemName.Pen, recoverChance=0.33),
                3: VisitObjective(npc=(12101, 3004)),
                4: VisitObjective(npc=(3004, 7205)),
                5: DefeatCogObjective(npc=7205, cogCount=50),
                6: VisitObjective(npc=(7205, 4135)),
                7: DefeatCogObjective(npc=4135, cogCount=20, cogLocation=12000),
                8: VisitObjective(npc=(4135, 12101)),
                9: DefeatCogObjective(npc=12101, cogCount=2, cogLocation=12000, cogType='clerk'),
            }
        ),
        6: QuestChain(
            rewards=(CogPromoteReward(2), InventoryReward(NameplateItemType.Tasks_Judy)),
            required=(QuestCompletionRequirement(QuestSource.Directive, 5), SuitDisguiseRequirement(2, 5, 11, True)),
            deletable=True,
            steps={
                1: RecoverFromCogObjective(npc=12101, cogType='cc', recoverItem=QuestItemName.WaterCoolerWater, recoverChance=0.33),
                2: DefeatCogObjective(npc=12101, cogCount=20, executive=True),
                3: DefeatBossObjective(npc=12101, cogTrack='c'),
                4: DefeatBossObjective(npc=12101, cogTrack='s'),
                5: DefeatFacilityObjective(npc=12101, facilityId=12000),
                6: RecoverFromCogObjective(npc=(12101, 3308), cogType='bw', recoverItem=QuestItemName.WigPowderDirections, recoverChance=0.33),
                7: DefeatCogObjective(npc=3308, cogCount=20, cogType='bw'),
                8: VisitObjective(npc=(3308, 12101)),
            }
        ),
        7: QuestChain(
            rewards=(CogPromoteReward(2), SuitSwitchReward(2), LaffReward(1)),
            required=(QuestCompletionRequirement(QuestSource.Directive, 6), SuitDisguiseRequirement(2, 6, 13, True)),
            deletable=True,
            steps={
                1: DefeatBossObjective(npc=12101, cogTrack='c'),
                2: VisitObjective(npc=(12101, 3136)),
                3: DefeatCogObjective(npc=3136, cogCount=10, cogType='br'),
                4: VisitObjective(npc=(3136, 7110)),
                5: VisitObjective(npc=(7110, 6109)),
                6: RecoverFromCogObjective(npc=6109, cogType='shw', recoverItem=QuestItemName.Wood, recoverChance=0.33, npcReturnable=False),
                7: VisitObjective(npc=(6199, 7110)),
                8: VisitObjective(npc=(7110, 1221)),
                9: DefeatCogObjective(npc=1221, cogCount=40, cogTrack='s'),
                10: VisitObjective(npc=(1221, 7110)),
                11: VisitObjective(npc=(7110, 5101)),
                12: RecoverFromCogObjective(npc=5101, recoverItem=QuestItemName.Tie, recoverChance=0.5, recoverRequired=20),
                13: VisitObjective(npc=(5101, 3136)),
                14: VisitObjective(npc=(3136, 12101)),
                15: DefeatBossObjective(npc=12101, cogType='clo_hm', cogTrack='l'),
                16: DefeatBossObjective(npc=12101, cogType='clo_hm', cogTrack='l'),
                17: QuestFishObjective(npc=12101, fishType=QuestItemName.Ink, fishCount=4, fishChance=0.8, fishLocation=ToontownGlobals.ToontownCentral),
            }
        ),
    }
)
