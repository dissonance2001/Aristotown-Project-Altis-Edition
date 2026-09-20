"""
This module contains the QuestLine class for Kudos.
It uses random quest generation from a ChainID for seeding.
"""
from datetime import datetime
import math
import random

from direct.showbase import PythonUtil

from toontown.hood import ZoneUtil
from toontown.inventory.enums.ItemEnums import BackgroundItemType, NameplateItemType, ProfilePoseItemType, \
    NametagFontItemType
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.quest3.base.QuestChain import QuestChain
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.base.QuestObjective import QuestObjective, MultiObjective
from toontown.quest3.base.QuestReference import QuestId
from toontown.quest3.base.Quester import Quester
from toontown.quest3.generator.QuestGenerator import QuestGenerator
from toontown.quest3.kudos import KudosConstants
from toontown.quest3.objectives import *
from toontown.quest3.objectives.UseDrumObjective import UseDrumObjective
from toontown.quest3.objectives.TreasureObjective import ZoneId2TreasureType
from toontown.quest3.QuestEnums import QuesterType, QuestSource, QuestItemName, QuestCollectable
from toontown.quest3.requirements import *
from toontown.quest3.rewards import *
from toontown.time import TimeUtil
from toontown.toon.npc import NPCToons
from toontown.toon.npc.NPCToonConstants import NPCToonEnum
from toontown.toonbase import ToontownGlobals
from toontown.racing import RaceGlobals


KudosRng = random.Random()


class KudosQuestLineContainer(QuestLine):
    questSource = QuestSource.KudosQuest

    def __init__(self, questLine) -> None:
        super().__init__(questLine)
        self.addXPRewardsToTaskline()

    def addXPRewardsToTaskline(self):
        """Adds toon exp rewards for each quest chain."""
        for chainId, questChain in self.questLine.items():
            # Get some variables, calculate the XP.
            pgTier, taskIndex = KudosConstants.calculatePgAndTaskIndexFromRankupChainId(chainId)
            expTotal = KudosConstants.PG_TIER_TO_EXP_TOTAL.get(pgTier)
            rankupXpPool = expTotal * KudosConstants.KUDOS_RANKUP_TASK_XP
            xpPercentageShare = KudosConstants.KUDOS_RANKUP_XP_SHARES[taskIndex]
            taskXp = rankupXpPool * xpPercentageShare / 100

            # Add the reward.
            reward = ExpReward(toonExp=round(taskXp))
            questChain.addReward(reward)
            # Also add a bogus "rank up" dummy reward
            questChain.addReward(KudosRankUpReward(location=KudosConstants.KUDOS_ZONES[pgTier - 1],
                                                   rank=taskIndex + 2))

            #.... OH YEAH
            questChain.setDeletable()

    @classmethod
    def getQuestChainFromChainId(cls, questSource: int, chainId: int, quester: Quester) -> QuestChain:
        """
        The trick for KudosQuest is that we override this
        class to create our own QuestChain dynamically!
        """
        # If the chain id is below 1000, it's a rank up quest.
        # We can retrieve this one normally.
        if chainId < 1000:
            return super().getQuestChainFromChainId(questSource, chainId, quester)

        # Parse the chain id and separate it into the difficulty,
        # the npc index, and the chain id.
        chainId = str(chainId)
        difficulty, npcIndex, chainId = int(chainId[0]), int(chainId[1:3]), int(chainId[3:])

        # Get the amount of kudos based on the difficulty
        # of the kudos quest.
        kudos = max(1, min(difficulty, 3))

        # Get the npc's safezone id.
        npcId = KudosConstants.getKudosNPCId(npcIndex)
        zoneId = KudosConstants.getKudosNPCHood(npcId)

        # Get the kudos quest tier.
        kudosTier = KudosSafezoneIdToTier.get(zoneId)
        if kudosTier is None:
            kudosTier = 1
            simbase.air.quest3Manager.notify.warning(f'KudosQuestLine got a bad zoneId: npcIndex {npcIndex}, npcId {npcId}, zoneId {zoneId}. Falling back to tier 1')

        # Calculate the bean and exp rewards.
        if kudosTier in KudosTierToBeanRewards:
            # Calculate beans.
            beans = math.ceil(KudosTierToBeanRewards[kudosTier] * kudos)

            # Calculate the EXP.
            expTotal = KudosConstants.PG_TIER_TO_EXP_TOTAL.get(kudosTier)
            taskXpPool = expTotal * KudosConstants.KUDOS_TASK_XP
            exp = round((taskXpPool * kudos) / KudosConstants.MAXIMUM_KUDOS)
        else:
            beans, exp = 0, 0

        # Get our input values.
        seed = chainId % 1_000_000

        # Randomize the beans and XP values by +/- 5%
        KudosRng.seed(seed)
        exp = int(round(exp + PythonUtil.lerp(exp * -0.05, exp * 0.05, KudosRng.random())))
        beans = int(round(beans + PythonUtil.lerp(beans * -0.05, exp * 0.05, KudosRng.random())))

        # Our difficulty is our tier (mapped 1-8), with a flat x1.5 constant,
        # and then we scale by the actual Kudos difficulty itself.
        # We also add a very light (seeded) difficulty variance.
        difficultyVariance = PythonUtil.lerp(0.92, 1.08, seed / 1000000)
        questDifficulty = kudosTier * 1.5 * (0.8 + (difficulty * 0.2)) * difficultyVariance

        # Initialize a QuestGenerator.
        questGenerator = QuestGenerator(seed=seed)

        # Generate a MultiObjective.
        multiObjective = questGenerator.generateTask(
            questerType=QuesterType.Toon, difficulty=questDifficulty, questSource=questSource,
            zoneId=zoneId, chainId=chainId, forcedObjectiveCount=1
        )

        steps = {
            1: multiObjective,
            2: VisitHQOfficerObjective(npc=npcId, npcZone=zoneId, npcReturnable=False, fromRandomKudosQuest=True),
        }

        # Force all of the objectives to be not npc returnable
        objectives = multiObjective.getQuestObjectives()  # type: list[QuestObjective]

        for objective in objectives:
            if not isinstance(objective, DeliverJellybeanObjective):
                objective.npc = (npcId, npcId)

        for objective in objectives:
            objective.npcReturnable = False

        # Get the quest requirement for the kudos rank.
        if kudosTier in KudosTierToQuest:
            reqChainId, reqObjectiveId = KudosTierToQuest[kudosTier]
        else:
            reqChainId, reqObjectiveId = 1, 1

        # Return our quest chain.
        return QuestChain(
            rewards=(KudosReward(zoneId, kudos), BeanReward(beans), ExpReward(exp)),
            steps=steps,
            deletable=True,
            required=QuestCompletionRequirement(QuestSource.MainQuest, reqChainId, reqObjectiveId),
        )

    @staticmethod
    def getRandomKudosQuestChainId(zoneId: int, npcId: int, index: int):
        """Method used for generating random kudos quests based
        on the current kudos tier.
        """
        rng = random.Random()
        rng.seed(TimeUtil.getNextTimestampOfInterval(KudosConstants.KUDOS_RESET_INTERVAL) + (npcId * 100) + index)
        zoneId = ZoneUtil.getSafeZoneId(zoneId)
        tier = KudosSafezoneIdToTier.get(zoneId)

        # Generate a random difficulty.
        difficulty = index + 1

        # Determine the RNG seed bounds based on the
        # difficulty selected for the quest.
        lowerBound = 1_000_000 * (tier - 1)
        if difficulty == 1:
            upperBound = lowerBound + 400_000
        elif difficulty == 2:
            lowerBound += 400_000
            upperBound = lowerBound + 700_000
        else:
            lowerBound += 700_000
            upperBound = 1_000_000 * tier

        # Ensure the lower number never gets below 1000.
        # We don't want it to interfere with the rank up quests.
        lowerBound = max(lowerBound, 1000)

        # Choose a random seed between the lower and upper bounds.
        seed = rng.randint(lowerBound, upperBound)
        tier = round((1.0 + (1 / tier)) ** 1.06)
        chainId = (tier * 1_000_000) + seed

        # Failsafe just in case.
        if npcId in KudosConstants.KUDOS_NPC_IDS:
            npcIndex = KudosConstants.KUDOS_NPC_IDS.index(npcId)
        else:
            npcIndex = 0

        # Do some funny string manipulation to ensure we get
        # the number that we desire.
        return int(str(difficulty) + str(npcIndex).zfill(2) + str(chainId).zfill(7))

    @staticmethod
    def getAvailableKudosQuests(zoneId: int) -> list:
        """
        Returns all available kudos quests from a zone ID.
        Returns as a list of quest IDs.
        """
        hqOfficers = KudosConstants.getKudosNPCId(hoodId=ZoneUtil.getHoodId(zoneId))
        if not hqOfficers:
            return []

        # Find some quest IDs.
        questIds = []
        for i in range(KudosConstants.KUDOS_QUESTS_PER_NPC * len(hqOfficers)):
            chainId = KudosQuestLine.getRandomKudosQuestChainId(
                zoneId=zoneId,
                npcId=hqOfficers[i // KudosConstants.KUDOS_QUESTS_PER_NPC],
                index=i % KudosConstants.KUDOS_QUESTS_PER_NPC,
            )
            questIds.append(QuestId(
                questSource=QuestSource.KudosQuest,
                chainId=chainId,
                objectiveId=1,
            ))

        # Return them.
        return questIds


KudosQuestLine = KudosQuestLineContainer(
    questLine={
        # Toontown Central
        1: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.ToontownCentral, 1),
            steps={
                1: VisitObjective(npc=2024),
                2: VisitObjective(npc=(2024, 2405)),
                3: DefeatCogObjective(npc=2405, cogCount=3, cogType="sc"),
                4: QuestFishObjective(npc=2405, fishType=QuestItemName.BarOfSoap, fishChance=0.95),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.ToontownCentral),
            },
        ),
        2: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.ToontownCentral, 1), GumballMachineBoosterReward(ToontownGlobals.ToontownCentral)),
            steps={
                1: VisitObjective(npc=2002),
                2: PurchaseGagObjective(npc=2002),
                3: DefeatCogObjective(npc=2002, cogCount=5, cogTrack="m", cogLevelMin=2),
                4: TrolleyObjective(npc=2002),
            },
        ),
        3: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Kudos_TTC), InventoryReward(BackgroundItemType.Kudos_TTC)),
            steps={
                1: VisitObjective(npc=2412),
                2: DefeatCogObjective(npc=2412, cogCount=1),
                3: DefeatCogObjective(npc=2412, cogCount=7),
                4: DefeatCogObjective(npc=2412, cogCount=1, cogType="pf"),
                5: RecoverFromCogObjective(npc=2412, recoverItem=QuestItemName.ClassifiedDocs, recoverChance=0.8),
            },
        ),
        4: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.BecomeDuck), PlaygroundHealBoostReward(ToontownGlobals.ToontownCentral, 6)),
            steps={
                1: VisitObjective(npc=2139),
                2: DeliverObjective(npc=(2139, 2301), recoverItem=QuestItemName.MedicalEval),
                3: RecoverFromCogObjective(npc=2139, cogType="sc", recoverItem=QuestItemName.RubberDuck, recoverChance=0.7),
                4: DefeatCogObjective(npc=2139, cogCount=1, cogType="duckshfl", taskManagerBoss=True, cogLocation=ToontownGlobals.ToontownCentral),
            },
        ),
        5: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.ToontownCentral, 2), GumballMachineBoosterReward(ToontownGlobals.ToontownCentral)),
            steps={
                1: VisitObjective(npc=2314),
                2: VisitObjective(npc=(2314, 2220)),
                3: DefeatCogObjective(npc=2220, cogCount=8, cogLevelMin=4),
                4: VisitObjective(npc=(2220, 2314)),
                5: DefeatCogObjective(npc=2314, cogCount=5, cogLocation=ToontownGlobals.ToontownCentral),
                6: DefeatCogObjective(npc=2314, cogCount=10, cogLocation=ToontownGlobals.ToontownCentral),
            },
        ),
        6: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.ToontownCentral, 2),
            steps={
                1: VisitObjective(npc=2322),
                2: VisitObjective(npc=(2322, 2108)),
                3: KnockKnockObjective(npc=2322),
                4: VisitObjective(npc=(2322, 2125)),
                5: DefeatCogObjective(npc=2322, cogCount=10, cogLevelMin=4),
            },
        ),
        7: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.IceCream), PlaygroundHealBoostReward(ToontownGlobals.ToontownCentral, 6)),
            steps={
                1: VisitObjective(npc=2402),
                2: VisitObjective(npc=(2402, 2131)),
                3: RecoverFromCogObjective(npc=2131, cogTrack="s", recoverRequired=10, recoverItem=QuestItemName.Coil, recoverChance=0.8),
                4: VisitObjective(npc=(2131, 2402)),
            },
        ),
        8: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.ToontownCentral, 3), GumballMachineBoosterReward(ToontownGlobals.ToontownCentral)),
            steps={
                1: VisitObjective(npc=2218),
                2: RecoverFromCogObjective(npc=2218, cogLevelMin=4, recoverRequired=10, recoverItem=QuestItemName.Memo, recoverChance=0.9),
                3: RecoverFromCogObjective(npc=2218, executive=True, recoverItem=QuestItemName.Memo, recoverChance=0.9),
                4: DefeatCogObjective(npc=2218, cogTrack="s"),
            },
        ),
        9: QuestChain(
            rewards=LaffReward(1),
            steps={
                1: VisitObjective(npc=2003),
                2: RecoverFromCogObjective(npc=2003, cogLevelMin=4, recoverItem=QuestItemName.CogRadarUnit, recoverChance=0.75),
                3: DeliverObjective(npc=(2003, 2402), recoverItem=QuestItemName.CogRadarUnit),
                4: VisitObjective(npc=(2402, 2003)),
                5: DefeatCogObjective(npc=2003, cogType="prethink", taskManagerBoss=True, cogLocation=ToontownGlobals.SchoolHouse),
            },
        ),
        
        # Barnacle Boatyard
        11: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.DonaldsDock, 1),
            steps={
                1: VisitObjective(npc=1223),
                2: DefeatCogObjective(npc=1223, cogCount=5, cogLocation=ToontownGlobals.SeaweedStreet),
                3: BuildingObjective(npc=1223, buildingCount=1, buildingLocation=ToontownGlobals.DonaldsDock),
            },
        ),
        12: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DonaldsDock, 1), GumballMachineBoosterReward(ToontownGlobals.DonaldsDock)),
            steps={
                1: VisitObjective(npc=1411),
                2: SwimObjective(npc=1411),
                3: QuestFishObjective(npc=1411, fishType=QuestItemName.Starfish, fishChance=1.0),
                4: VisitObjective(npc=(1411, 1121)),
                5: DefeatCogObjective(npc=1121, cogCount=6, cogLocation=ToontownGlobals.BuccaneerBoulevard),
                6: VisitObjective(npc=(1121, 1411)),
                7: RecoverFromCogObjective(npc=1411, executive=True,
                                           recoverItem=QuestItemName.CogGears, recoverChance=0.8),
            },
        ),
        13: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Kudos_BB), InventoryReward(BackgroundItemType.Kudos_BB)),
            steps={
                1: VisitObjective(npc=1212),
                2: DefeatCogObjective(npc=1212, cogCount=8, cogTrack='c'),
                3: RecoverFromCogObjective(npc=1212, cogType='mm',
                                           recoverItem=QuestItemName.Memo, recoverChance=0.95),
                4: RecoverFromBuildingObjective(npc=1212, cogTrack='c',
                                                recoverItem=QuestItemName.DiningSet, recoverChance=1.0),
            },
        ),
        14: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Treasure), PlaygroundHealBoostReward(ToontownGlobals.DonaldsDock, 6)),
            steps={
                1: VisitObjective(npc=1417),
                2: BuildingObjective(npc=1417, cogTrack='g'),
                3: RecoverFromCogObjective(npc=1417, cogType='ins',
                                           recoverItem=QuestItemName.Memo, recoverChance=0.85),
                4: DefeatCogObjective(npc=1417, cogType="ddiver", taskManagerBoss=True, cogLocation=ToontownGlobals.DonaldsDock),
            },
        ),
        15: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DonaldsDock, 2), GumballMachineBoosterReward(ToontownGlobals.DonaldsDock)),
            steps={
                1: VisitObjective(npc=1220),
                2: VisitObjective(npc=(1220, 1402)),
                3: VisitObjective(npc=(1402, 1221)),
                4: BuildingObjective(npc=1221, buildingCount=2, buildingLocation=ToontownGlobals.SeaweedStreet),
                5: VisitObjective(npc=(1221, 1220)),
                6: DefeatCogObjective(npc=1220, cogCount=10, cogLocation=ToontownGlobals.SeaweedStreet),
            },
        ),
        16: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.DonaldsDock, 2),
            steps={
                1: VisitObjective(npc=1322),
                2: JungleGameObjective(npc=1322, bananaCount=3),
                3: VisitObjective(npc=(1322, 1415)),
                4: VisitObjective(npc=(1415, 1322)),
                5: DeliverGagObjective(npc=1322, gagCount=5, gagLevel=3),
                6: DefeatCogObjective(npc=1322),
                7: DefeatCogObjective(npc=1322, executive=True, cogCount=6),
            },
        ),
        17: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Pirate), PlaygroundHealBoostReward(ToontownGlobals.DonaldsDock, 6)),
            steps={
                1: VisitObjective(npc=1213),
                2: RecoverFromCogObjective(npc=1213, cogType='sc',
                                           recoverItem=QuestItemName.SmallClockHand, recoverChance=0.8),
                3: RecoverFromCogObjective(npc=1213, cogType='pp',
                                           recoverItem=QuestItemName.BigClockHand, recoverChance=0.8),
                4: RecoverFromCogObjective(npc=1213, recoverItem=QuestItemName.Washer, recoverChance=0.7, recoverRequired=8),
                5: RecoverFromCogObjective(npc=1213, executive=True,
                                           recoverItem=QuestItemName.ReinforcedBolt, recoverChance=0.85, recoverRequired=5),
                6: VisitObjective(npc=(1213, 1105)),
                7: VisitObjective(npc=(1105, 1213)),
            },
        ),
        18: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DonaldsDock, 3), GumballMachineBoosterReward(ToontownGlobals.DonaldsDock)),
            steps={
                1: VisitObjective(npc=1201),
                2: RecoverFromCogObjective(npc=1201, cogType='bc',
                                           recoverItem=QuestItemName.BeanJar, recoverChance=0.9, recoverRequired=5),
                3: BuildingObjective(npc=1201, cogTrack='m', floorMinimum=2),
                4: RecoverFromCogObjective(npc=1201, cogTrack='m', cogLocation=ToontownGlobals.DonaldsDock,
                                           recoverItem=QuestItemName.JellybeanBag, recoverChance=0.7, recoverRequired=4),
            },
        ),
        19: QuestChain(
            rewards=LaffReward(1),
            steps={
                1: VisitObjective(npc=1116),
                2: VisitObjective(npc=(1116, 1405)),
                3: RecoverFromCogObjective(npc=1405, cogLocation=ToontownGlobals.DonaldsDock, cogLevelMin=3,
                                           recoverItem=QuestItemName.StrongWire, recoverChance=0.85, recoverRequired=10),
                4: RecoverFromCogObjective(npc=1405, cogLocation=ToontownGlobals.DonaldsDock, cogLevelMin=5,
                                           recoverItem=QuestItemName.Motor, recoverChance=0.85),
                5: VisitObjective(npc=(1405, 1116)),
                6: BuildingObjective(npc=1116, buildingCount=2, buildingLocation=ToontownGlobals.DonaldsDock),
                7: DefeatCogObjective(npc=1116, cogType='rainmake', taskManagerBoss=True, cogLocation=ToontownGlobals.LighthouseInt),
            },
        ),
        
        # Ye Olde Toontown
        21: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.YeOlde, 1),
            steps={
                1: VisitObjective(npc=7112),
                2: DefeatCogObjective(npc=7112, cogCount=4, cogLocation=ToontownGlobals.ToontownCentral),
                3: DefeatCogObjective(npc=7112, cogCount=2, cogLevelMin=6),
                4: DefeatCogObjective(npc=7112, cogCount=3, executive=True),
            },
        ),
        22: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.YeOlde, 1), GumballMachineBoosterReward(ToontownGlobals.YeOlde)),
            steps={
                1: VisitObjective(npc=7302),
                2: RecoverFromCogObjective(npc=7302, cogType='ad',
                                           recoverItem=QuestItemName.BoxButNotReally, recoverChance=0.95),
                3: BuildingObjective(npc=7302, cogTrack='l', floorMinimum=2),
                4: QuestCollectableObjective(npc=7302, collectable=QuestCollectable.KudosBox),
            },
        ),
        23: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Kudos_YOTT), InventoryReward(BackgroundItemType.Kudos_YOTT)),
            steps={
                1: VisitObjective(npc=7203),
                2: VisitObjective(npc=(7203, 7208)),
                3: BuildingObjective(npc=7208, cogTrack='g', buildingLocation=ToontownGlobals.YeOlde),
                4: DefeatCogObjective(npc=7208, cogCount=4, cogTrack='g', cogLocation=ToontownGlobals.NobleNook),
                5: DeliverObjective(npc=(7208, 7203), recoverItem=QuestItemName.FreshlyBakedPies),
                6: RecoverFromCogObjective(npc=7203, cogType='f',
                                           recoverItem=QuestItemName.Handkerchief, recoverChance=0.9, recoverRequired=4),
            },
        ),
        24: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.AtTheGate), PlaygroundHealBoostReward(ToontownGlobals.YeOlde, 6)),
            steps={
                1: VisitObjective(npc=7313),
                2: DefeatCogObjective(npc=7313, cogCount=5, executive=True),
                3: RecoverFromCogObjective(npc=7313, cogType='cv',
                                           recoverItem=QuestItemName.Memo, recoverChance=1.0),
                4: DefeatCogObjective(npc=7313, npcReturnable=False, cogType='gatekeep', taskManagerBoss=True, cogLocation=ToontownGlobals.YeOlde),
                5: VisitObjective(npc=(7313, 7003)),
            },
        ),
        25: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.YeOlde, 2), GumballMachineBoosterReward(ToontownGlobals.YeOlde)),
            steps={
                1: VisitObjective(npc=7213),
                2: VisitObjective(npc=(7213, 7010)),
                3: RecoverFromCogObjective(npc=7010, cogType='nc',
                                           recoverItem=QuestItemName.Number, recoverChance=0.9, recoverRequired=4),
                4: RecoverFromCogObjective(npc=7010, cogType='nn',
                                           recoverItem=QuestItemName.PieceofThread, recoverChance=0.9, recoverRequired=5),
                5: RecoverFromCogObjective(npc=7010, cogType='ym',
                                           recoverItem=QuestItemName.GolfClub, recoverChance=0.85),
                6: VisitObjective(npc=(7010, 7213)),
            },
        ),
        26: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.YeOlde, 2),
            steps={
                1: VisitObjective(npc=7211),
                2: RecoverFromCogObjective(npc=7211, cogType='bf',
                                           recoverItem=QuestItemName.Garbage, recoverChance=0.8, recoverRequired=5),
                3: RecoverFromCogObjective(npc=7211, cogType='bf', executive=True,
                                           recoverItem=QuestItemName.Garbage, recoverChance=1.0, recoverRequired=2),
                4: VisitHQOfficerObjective(npcZone=ToontownGlobals.YeOlde),
            },
        ),
        27: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Medieval), PlaygroundHealBoostReward(ToontownGlobals.YeOlde, 6)),
            steps={
                1: VisitObjective(npc=7308),
                2: QuestFishObjective(npc=7308, fishType=QuestItemName.QualityFishingRod, fishChance=0.65, fishLocation=ToontownGlobals.YeOlde),
                3: VisitObjective(npc=(7308, 7212)),
                4: RecoverFromCogObjective(npc=(7212, 7308), cogType='shw',
                                           recoverItem=QuestItemName.PackageOfFishBait, recoverChance=0.9),
                5: VisitObjective(npc=(7308, 7108)),
                6: DefeatCogObjective(npc=7108, cogCount=15, cogLocation=ToontownGlobals.YeOlde),
                7: VisitObjective(npc=(7108, 7308)),
            },
        ),
        28: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.YeOlde, 3), GumballMachineBoosterReward(ToontownGlobals.YeOlde)),
            steps={
                1: VisitObjective(npc=7113),
                2: RecoverFromCogObjective(npc=7113, cogTrack='s', executive=True,
                                           recoverItem=QuestItemName.MaroonGem, recoverChance=0.95),
                3: RecoverFromCogObjective(npc=7113, cogTrack='m', executive=True,
                                           recoverItem=QuestItemName.GreenGem, recoverChance=0.95),
                4: RecoverFromCogObjective(npc=7113, cogTrack='l', executive=True,
                                           recoverItem=QuestItemName.IndigoGem, recoverChance=0.95),
            },
        ),
        29: QuestChain(
            rewards=LaffReward(1),
            steps={
                1: VisitObjective(npc=7300),
                2: RecoverFromBuildingObjective(npc=7300, cogTrack='l',
                                                recoverItem=QuestItemName.BoxOfWritingSupplies, recoverChance=1.0, recoverRequired=3),
                3: VisitObjective(npc=(7300, 7303)),
                4: DefeatCogObjective(npc=7303, cogCount=15, cogLocation=ToontownGlobals.YeOlde),
                5: VisitObjective(npc=(7303, 7003)),
                6: DefeatCogObjective(npc=7003, cogType='whunter', taskManagerBoss=True, cogLocation=ToontownGlobals.YeOlde),
            },
        ),
        
        # Daffodil Gardens
        31: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.DaisyGardens, 1),
            steps={
                1: VisitObjective(npc=5404),
                2: SwimObjective(npc=5404),
                3: DefeatCogObjective(npc=5404, cogType='foreman'),
                4: RecoverFromCogObjective(npc=5404,
                                           recoverItem=QuestItemName.TarotCard, recoverChance=1.0, recoverRequired=22),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.DaisyGardens),
            },
        ),
        32: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DaisyGardens, 1), GumballMachineBoosterReward(ToontownGlobals.DaisyGardens)),
            steps={
                1: VisitObjective(npc=5314),
                2: VisitObjective(npc=(5314, 5309)),
                3: VisitObjective(npc=(5309, 5114)),
                4: RecoverFromCogObjective(npc=5114, cogType='bc',
                                           recoverItem=QuestItemName.Fertilizer, recoverChance=0.8, recoverRequired=3),
                5: VisitObjective(npc=(5114, 5214)),
                6: RecoverFromCogObjective(npc=5214, cogType='ac',
                                           recoverItem=QuestItemName.Ointment, recoverChance=0.5),
                7: DeliverObjective(npc=(5214, 5314), recoverItem=QuestItemName.BoxOfAnts),
            },
        ),
        33: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Kudos_DG), InventoryReward(BackgroundItemType.Kudos_DG)),
            steps={
                1: VisitObjective(npc=5406),
                # TODO: Change to "Visit Paint Room" objective.
                2: CollectBarrelObjective(npc=5406, zoneId=SpecialQuestZones.SellbotFactory),
                3: DefeatCogObjective(npc=5406, cogCount=10, cogLocation=ToontownGlobals.SunflowerStreet),
            },
        ),
        34: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Elegance), PlaygroundHealBoostReward(ToontownGlobals.DaisyGardens, 6)),
            steps={
                1: VisitObjective(npc=5205),
                2: RecoverFromCogObjective(npc=5205, cogType='ad',
                                           recoverItem=QuestItemName.FineCollar, recoverChance=0.95),
                3: RecoverFromCogObjective(npc=5205, cogType='nd',
                                           recoverItem=QuestItemName.Bell, recoverChance=0.5),
                4: QuestFishObjective(npc=5205, fishType=QuestItemName.GlassOfWater),
                5: RecoverFromCogObjective(npc=5205, cogType='bellring',
                                           recoverItem=QuestItemName.FineBell, recoverChance=1.0,
                                           taskManagerBoss=True, cogLocation=ToontownGlobals.DaisyGardens),
            },
        ),
        35: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DaisyGardens, 2), GumballMachineBoosterReward(ToontownGlobals.DaisyGardens)),
            steps={
                1: VisitObjective(npc=5403),
                2: RecoverFromCogObjective(npc=5403, cogType='dt',
                                           recoverItem=QuestItemName.Flower, recoverChance=0.85, recoverRequired=1),
                3: RecoverFromCogObjective(npc=5403, cogType='dt',
                                           recoverItem=QuestItemName.Flower, recoverChance=0.9, recoverRequired=5),
                4: DefeatCogObjective(npc=5403, cogType='tf', cogLocation=ToontownGlobals.SellbotHQ),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.DaisyGardens),
            },
        ),
        36: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.DaisyGardens, 2),
            steps={
                1: VisitObjective(npc=5219),
                2: MultiObjective(
                    DefeatCogObjective(npc=5219, cogType='tf', npcReturnable=False),
                    DefeatCogObjective(npc=5219, cogType='mb', npcReturnable=False),
                    DefeatCogObjective(npc=5219, cogType='sd', npcReturnable=False),
                    DefeatCogObjective(npc=5219, cogType='hh', npcReturnable=False),
                    DefeatCogObjective(npc=5219, cogType='shw', npcReturnable=False),
                ),
                3: VisitObjective(npc=5219)
            },
        ),
        37: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Calligraphy), PlaygroundHealBoostReward(ToontownGlobals.DaisyGardens, 6)),
            steps={
                1: VisitObjective(npc=5306),
                2: DefeatCogObjective(npc=5306, cogType='ms'),
                3: DefeatFacilityObjective(npc=5306, facilityId=10000),
                4: VisitObjective(npc=(5306, 5414)),
                5: DefeatBossObjective(npc=5414, cogTrack='s'),
                6: VisitObjective(npc=(5414, 5306)),
            },
        ),
        38: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DaisyGardens, 3), GumballMachineBoosterReward(ToontownGlobals.DaisyGardens)),
            steps={
                1: VisitObjective(npc=5306),
                2: VisitObjective(npc=(5306, 5122)),
                3: VisitObjective(npc=(5122, 5219)),
                4: DefeatCogObjective(npc=5219, cogCount=10, cogLevelMin=5),
                5: VisitObjective(npc=(5219, 5220)),
                6: RecoverFromCogObjective(npc=5220, cogLocation=ToontownGlobals.DaisyDrive,
                                           recoverItem=QuestItemName.Package, recoverChance=0.7, recoverRequired=2),
                7: QuestFishObjective(npc=5220, fishType=QuestItemName.Package, fishChance=0.8, fishCount=3),
                8: VisitObjective(npc=(5220, 5203)),
            },
        ),
        39: QuestChain(
            rewards=LaffReward(1),
            steps={
                1: VisitObjective(npc=5316),
                2: RecoverFromCogObjective(npc=5316, cogType='foreman',
                                           recoverItem=QuestItemName.Memo, recoverChance=1.0),
                3: RecoverFromCogObjective(npc=5316, cogType='gh',
                                           recoverItem=QuestItemName.Memo, recoverChance=0.8),
                4: RecoverFromCogObjective(npc=5316, cogType='mslacker',
                                           recoverItem=QuestItemName.CouchBlueprints, recoverChance=1.0,
                                           taskManagerBoss=True, cogLocation=ToontownGlobals.SellbotHQ)
            },
        ),
        
        # Mezzo Melodyland
        41: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.MinniesMelodyland, 1),
            steps={
                1: VisitObjective(npc=4329),
                2: DefeatCogObjective(npc=4329, cogType='shw'),
                3: RecoverFromCogObjective(npc=4329, cogType='shw',
                                           recoverItem=QuestItemName.Photograph, recoverChance=0.95),
                4: VisitObjective(npc=(4329, 4411)),
                5: BuildingObjective(npc=4411, floorMinimum=4),
                6: FishingObjective(npc=4411, rarity=1, fishReq=1),
                7: VisitHQOfficerObjective(npcZone=ToontownGlobals.MinniesMelodyland),
            },
        ),
        42: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.MinniesMelodyland, 1), GumballMachineBoosterReward(ToontownGlobals.MinniesMelodyland)),
            steps={
                1: VisitObjective(npc=4325),
                2: RecoverFromCogObjective(npc=4325, cogTrack='l', cogLocation=ToontownGlobals.TenorTerrace,
                                           recoverItem=QuestItemName.StackOfPaper, recoverChance=0.85, recoverRequired=5),
                3: VisitObjective(npc=(4325, 4108)),
                4: BuildingObjective(npc=4108, buildingCount=2, floorMinimum=4),
                5: VisitObjective(npc=(4108, 4325)),
                6: VisitObjective(npc=(4325, 2002)),
                7: VisitObjective(npc=(2002, 4325)),
            },
        ),
        43: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Kudos_MML), InventoryReward(BackgroundItemType.Kudos_MML)),
            steps={
                1: VisitObjective(npc=4130),
                2: VisitHQOfficerObjective(npcZone=ToontownGlobals.MinniesMelodyland),
                3: VisitObjective(npc=4114),
                4: DefeatCogObjective(npc=(4114, 4130), cogCount=10, cogLocation=ToontownGlobals.AltoAvenue),
                5: BuildingObjective(npc=4130, cogTrack='c', floorMinimum=4),
            },
        ),
        44: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.PickUpThePhone), PlaygroundHealBoostReward(ToontownGlobals.MinniesMelodyland, 6)),
            steps={
                1: VisitObjective(npc=4324),
                2: VisitObjective(npc=(4324, 4309)),
                3: RecoverFromCogObjective(npc=4309, cogType='nc',
                                           recoverItem=QuestItemName.PancakeMix, recoverChance=0.8),
                4: VisitObjective(npc=(4309, 4324)),
                5: VisitObjective(npc=(4324, 4327)),
                6: RecoverFromCogObjective(npc=(4327, 4324), cogType='mi',
                                           recoverItem=QuestItemName.Flower, recoverChance=0.9),
                7: RecoverFromCogObjective(npc=4324, cogType='mouthp',
                                           recoverItem=QuestItemName.CookieRecipe, recoverChance=1.0,
                                           taskManagerBoss=True, cogLocation=ToontownGlobals.MinniesMelodyland),
            },
        ),
        45: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.MinniesMelodyland, 2), GumballMachineBoosterReward(ToontownGlobals.MinniesMelodyland)),
            steps={
                1: VisitObjective(npc=4422),
                2: RecoverFromCogObjective(npc=4422, cogType='pp',
                                           recoverItem=QuestItemName.SaxBrassButNotReally, recoverChance=0.75, recoverRequired=10),
                3: QuestFishObjective(npc=4422, fishType=QuestItemName.ZincVitamins, fishChance=0.6, fishCount=5),
                4: VisitHQOfficerObjective(npcZone=ToontownGlobals.MinniesMelodyland),
            },
        ),
        46: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.MinniesMelodyland, 2),
            steps={
                1: VisitObjective(npc=4312),
                2: DefeatCogObjective(npc=4312, cogCount=10, cogLevelMin=8, cogLocation=ToontownGlobals.MinniesMelodyland),
                3: BuildingObjective(npc=4312, buildingCount=3, floorMinimum=4),
            },
        ),
        47: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Playful), PlaygroundHealBoostReward(ToontownGlobals.MinniesMelodyland, 6)),
            steps={
                1: VisitObjective(npc=4219),
                2: RecoverFromCogObjective(npc=4219, cogTrack='l',
                                           recoverItem=QuestItemName.InsurancePermit, recoverChance=0.35),
                3: RecoverFromBuildingObjective(npc=4219, cogTrack='l', floorMinimum=5,
                                                recoverItem=QuestItemName.FraudulentPaperwork, recoverChance=1.0),
                4: VisitHQOfficerObjective(npcZone=ToontownGlobals.MinniesMelodyland),
            },
        ),
        48: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.MinniesMelodyland, 3), GumballMachineBoosterReward(ToontownGlobals.MinniesMelodyland)),
            steps={
                1: VisitObjective(npc=4328),
                2: VisitObjective(npc=(4328, 2211)),
                3: DefeatCogObjective(npc=2211, cogCount=10, cogType='cc'),
                4: DefeatCogObjective(npc=2211, cogCount=1, cogType='cc'),
                5: VisitObjective(npc=(2211, 4328)),
            },
        ),
        49: QuestChain(
            rewards=LaffReward(1),
            steps={
                1: VisitObjective(npc=4101),
                2: UseDrumObjective(npc=4101, useCount=16, npcReturnable=False),
                3: VisitObjective(npc=4101),
                4: DefeatCogObjective(npc=4101, cogType='mplayer', npcReturnable=False, taskManagerBoss=True, cogLocation=ToontownGlobals.MajorPlayerLobby),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.MinniesMelodyland),
            },
        ),
        
        # The Brrrgh
        51: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.TheBrrrgh, 1),
            steps={
                1: VisitObjective(npc=3124),
                2: DefeatCogObjective(npc=3124, cogCount=15),
                3: DefeatCogObjective(npc=3124, cogCount=10, cogLevelMin=10),
                4: BuildingObjective(npc=3124, buildingCount=2),
                5: BuildingObjective(npc=3124, floorMinimum=5),
            },
        ),
        52: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.TheBrrrgh, 1), GumballMachineBoosterReward(ToontownGlobals.TheBrrrgh)),
            steps={
                1: VisitObjective(npc=3222),
                2: RecoverFromCogObjective(npc=3222, cogLocation=ToontownGlobals.TheBrrrgh,
                                           recoverItem=QuestItemName.RoadSalt, recoverChance=0.85, recoverRequired=10),
                3: RecoverFromCogObjective(npc=3222, cogLocation=ToontownGlobals.TheBrrrgh,
                                           recoverItem=QuestItemName.RoadSalt, recoverChance=0.7, recoverRequired=10),
                4: RacingObjective(npc=3222, trackId=RaceGlobals.RT_Urban_2, npcReturnable=False),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.TheBrrrgh),
            },
        ),
        53: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Kudos_TB), InventoryReward(BackgroundItemType.Kudos_TB)),
            steps={
                1: VisitObjective(npc=3306),
                2: MultiObjective(
                    RecoverFromCogObjective(npc=3306, npcReturnable=False, cogType='bf',
                                            recoverItem=QuestItemName.Honey, recoverChance=0.95),
                    RecoverFromBuildingObjective(npc=3306, npcReturnable=False,
                                                 recoverItem=QuestItemName.NeatThing, recoverChance=1.0, recoverRequired=3),
                ),
                3: VisitObjective(npc=1320),
                4: VisitObjective(npc=(1320, 3306)),
                5: DefeatCogObjective(npc=3306, cogLocation=ToontownGlobals.PolarPlace),
                6: VisitObjective(npc=(3306, 2009)),
                7: VisitObjective(npc=(2009, 3306)),
            },
        ),
        54: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.FireHands), PlaygroundHealBoostReward(ToontownGlobals.TheBrrrgh, 6)),
            steps={
                1: VisitObjective(npc=3105),
                2: RecoverFromCogObjective(npc=3105, cogType='sh',
                                           recoverItem=QuestItemName.Ice, recoverChance=0.85),
                3: VisitObjective(npc=(3105, 3135)),
                4: VisitObjective(npc=(3135, 3105)),
                5: VisitObjective(npc=(3105, 3229)),
                6: DefeatCogObjective(npc=3229, cogCount=20, cogLevelMin=6, cogLocation=ToontownGlobals.SleetStreet),
                7: VisitObjective(npc=(3229, 3135)),
                8: DefeatCogObjective(npc=3135, npcReturnable=False, cogType='fires',
                                      taskManagerBoss=True, cogLocation=ToontownGlobals.TheBrrrgh),
                9: VisitHQOfficerObjective(npcZone=ToontownGlobals.TheBrrrgh),
            },
        ),
        55: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.TheBrrrgh, 2), GumballMachineBoosterReward(ToontownGlobals.TheBrrrgh)),
            steps={
                1: VisitObjective(npc=3202),
                2: RecoverFromBuildingObjective(npc=3202, floorMinimum=4, buildingLocation=ToontownGlobals.TheBrrrgh,
                                                recoverItem=QuestItemName.IndustrialGlass, recoverChance=1.0),
                3: VisitObjective(npc=(3202, 3327)),
                4: DefeatCogObjective(npc=3327, cogCount=15, cogLocation=ToontownGlobals.TheBrrrgh),
                5: VisitObjective(npc=(3327, 3202)),
                6: QuestFishObjective(npc=3202, fishType=QuestItemName.Wood, fishChance=0.8, fishCount=3, fishLocation=ToontownGlobals.OutdoorZone),
                7: SnowballObjective(npc=3202),
                8: VisitHQOfficerObjective(npcZone=ToontownGlobals.TheBrrrgh),
            },
        ),
        56: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.TheBrrrgh, 2),
            steps={
                1: VisitObjective(npc=3403),
                2: VisitObjective(npc=(3403, 2001)),
                3: DeliverObjective(npc=(2001, 3403), recoverItem=QuestItemName.Artwork),
                4: DefeatBossObjective(npc=3403, cogCount=2, cogTrack='l'),
            },
        ),
        57: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Comical), PlaygroundHealBoostReward(ToontownGlobals.TheBrrrgh, 6)),
            steps={
                1: VisitObjective(npc=3201),
                2: GoSadObjective(npc=3201),
                3: BuildingLaffObjective(npc=3201, laffRatio=0.33, floorMinimum=3),
                4: VisitHQOfficerObjective(npcZone=ToontownGlobals.TheBrrrgh),
            },
        ),
        58: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.TheBrrrgh, 3), GumballMachineBoosterReward(ToontownGlobals.TheBrrrgh)),
            steps={
                1: VisitObjective(npc=3124),
                2: VisitObjective(npc=(3124, 3122)),
                3: RecoverFromBuildingObjective(npc=3122, floorMinimum=5, buildingLocation=ToontownGlobals.TheBrrrgh,
                                                recoverItem=QuestItemName.IcicleBicycle, recoverChance=1.0),
                4: VisitObjective(npc=(3122, 3124)),
                5: TreasureObjective(npc=(3124, 3122), treasureCount=10, treasureType=ZoneId2TreasureType[ToontownGlobals.TheBrrrgh]),
                6: DeliverObjective(npc=(3122, 3124), recoverItem=QuestItemName.IcicleBicycle),
                7: RecoverFromCogObjective(npc=3124, cogType='cv',
                                           recoverItem=QuestItemName.MechanicalBelt, recoverChance=1.0, recoverRequired=2),
                8: VisitHQOfficerObjective(npcZone=ToontownGlobals.TheBrrrgh),
            },
        ),
        59: QuestChain(
            rewards=LaffReward(1),
            steps={
                1: VisitObjective(npc=3406),
                2: DefeatCogObjective(npc=3406, cogCount=15, cogLocation=ToontownGlobals.ArcticAvenue),
                3: VisitObjective(npc=(3406, 3328)),
                4: VisitHQOfficerObjective(npcZone=ToontownGlobals.TheBrrrgh),
                5: InvestigateObjective(npcReturnable=False, zoneId=ToontownGlobals.Pizzeria),
                6: VisitHQOfficerObjective(npcZone=ToontownGlobals.TheBrrrgh),
                7: DefeatCogObjective(npcReturnable=False, cogType='pcrat',
                                      taskManagerBoss=True, cogLocation=ToontownGlobals.Pizzeria),
                8: VisitHQOfficerObjective(npcZone=ToontownGlobals.TheBrrrgh),
            },
        ),
        
        # Acorn Acres
        61: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.OutdoorZone, 1),
            steps={
                1: VisitObjective(npc=6307),
                2: DefeatCogObjective(npc=6307, cogCount=10, cogType='bc'),
                # Go to each tunnel in Acorn Acres streets
                3: MultiObjective(
                    InvestigateObjective(npcReturnable=False, zoneId=ToontownGlobals.AlmondAvenue + 1),
                    InvestigateObjective(npcReturnable=False, zoneId=ToontownGlobals.PeanutPlace + 1),
                    InvestigateObjective(npcReturnable=False, zoneId=ToontownGlobals.WalnutWay + 1),
                    InvestigateObjective(npcReturnable=False, zoneId=ToontownGlobals.LegumeLane + 1),
                ),
                4: VisitObjective(npc=6307),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.OutdoorZone),
            },
        ),
        62: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.OutdoorZone, 1), GumballMachineBoosterReward(ToontownGlobals.OutdoorZone)),
            steps={
                1: VisitObjective(npc=6304),
                2: RecoverFromCogObjective(npc=6304, cogTrack='c', cogLocation=ToontownGlobals.BossbotHQ,
                                           recoverItem=QuestItemName.Sapling, recoverChance=0.65),
                3: RecoverFromCogObjective(npc=6304, cogType='clubpres',
                                           recoverItem=QuestItemName.Sapling, recoverChance=1.0),
            },
        ),
        63: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Kudos_AA), InventoryReward(BackgroundItemType.Kudos_AA)),
            steps={
                1: VisitObjective(npc=6101),
                2: RecoverFromBuildingObjective(npc=6101,
                                                recoverItem=QuestItemName.BoxOfPartyPoppers, recoverChance=1.0, recoverRequired=2),
                3: RecoverFromCogObjective(npc=6101, cogType='mg',
                                           recoverItem=QuestItemName.PunchBowl, recoverChance=0.9, recoverRequired=3),
                4: SwimObjective(npc=6101),
                5: DefeatCogObjective(npc=6101, cogCount=10, cogLocation=ToontownGlobals.AlmondAvenue),
                6: VisitHQOfficerObjective(npcZone=ToontownGlobals.OutdoorZone),
            },
        ),
        64: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Rolled), PlaygroundHealBoostReward(ToontownGlobals.OutdoorZone, 6)),
            steps={
                1: VisitObjective(npc=6420),
                2: RecoverFromCogObjective(npc=6420, cogLocation=ToontownGlobals.OutdoorZone,
                                           recoverItem=QuestItemName.Note, recoverChance=0.7, recoverRequired=10),
                3: DefeatCogObjective(npc=6420, cogType='treek', taskManagerBoss=True, cogLocation=ToontownGlobals.OutdoorZone),
                4: VisitHQOfficerObjective(npcZone=ToontownGlobals.OutdoorZone),
            },
        ),
        65: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.OutdoorZone, 2), GumballMachineBoosterReward(ToontownGlobals.OutdoorZone)),
            steps={
                1: VisitObjective(npc=6211),
                2: DefeatCogObjective(npc=6211, cogCount=10, cogType='dl'),
                3: BuildingObjective(npc=6211, floorMinimum=5, buildingLocation=ToontownGlobals.PeanutPlace),
            },
        ),
        66: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.OutdoorZone, 2),
            steps={
                1: VisitObjective(npc=6107),
                2: BuildingObjective(npc=6107, floorMinimum=5),
                3: QuestFishObjective(npc=6107, fishType=QuestItemName.SoakedLeaves, fishLocation=ToontownGlobals.OutdoorZone),
                4: RecoverFromBuildingObjective(npc=6107, floorMinimum=6, cogTrack='c',
                                                recoverItem=QuestItemName.TreePuppies, recoverChance=1.0),
            },
        ),
        67: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Arrogant), PlaygroundHealBoostReward(ToontownGlobals.OutdoorZone, 6)),
            steps={
                1: VisitObjective(npc=6317),
                2: RecoverFromCogObjective(npc=6317, cogLocation=ToontownGlobals.PeanutPlace,
                                           recoverItem=QuestItemName.Nut, recoverChance=0.95, recoverRequired=15),
                3: RecoverFromCogObjective(npc=6317, cogLocation=ToontownGlobals.WalnutWay,
                                           recoverItem=QuestItemName.Nut, recoverChance=0.95, recoverRequired=15),
                4: RecoverFromCogObjective(npc=6317, cogLocation=ToontownGlobals.AlmondAvenue,
                                           recoverItem=QuestItemName.Nut, recoverChance=0.95, recoverRequired=15),
                5: RecoverFromCogObjective(npc=6317, cogLocation=ToontownGlobals.LegumeLane,
                                           recoverItem=QuestItemName.Nut, recoverChance=0.95, recoverRequired=15),
                6: VisitHQOfficerObjective(npcZone=ToontownGlobals.OutdoorZone),
            },
        ),
        68: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.OutdoorZone, 3), GumballMachineBoosterReward(ToontownGlobals.OutdoorZone)),
            steps={
                1: VisitObjective(npc=6302),
                2: VisitObjective(npc=(6302, 6314)),
                3: RecoverFromBuildingObjective(npc=(6314, 6302), floorMinimum=4, buildingLocation=ToontownGlobals.OutdoorZone,
                                                recoverItem=QuestItemName.TissueBox, recoverChance=1.0, recoverRequired=5),
                4: VisitHQOfficerObjective(npcZone=ToontownGlobals.OutdoorZone),
            },
        ),
        69: QuestChain(
            rewards=LaffReward(1),
            steps={
                1: VisitObjective(npc=2010),
                2: FeedDinerObjective(npc=2010, cogAmount=5),
                3: VisitObjective(npc=(2010, 6203)),
                4: BuildingObjective(npc=6203, buildingCount=1, floorMinimum=6, cogTrack='c'),
                5: DefeatCogObjective(npc=(6203, 2010), cogType='chainsaw',
                                      taskManagerBoss=True, cogLocation=ToontownGlobals.ChainsawLogging),
            },
        ),
        
        # Donald's Dreamland
        71: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.DonaldsDreamland, 1),
            steps={
                1: VisitObjective(npc=9823),
                2: QuestFishObjective(npc=9823, fishLocation=ToontownGlobals.DonaldsDreamland,
                                      fishType=QuestItemName.EarPlug, fishChance=0.5, fishCount=2),
                3: BuildingObjective(npc=9823, buildingCount=2, buildingLocation=ToontownGlobals.TwilightTerrace),
                4: DefeatCogObjective(npc=9823, cogCount=15, cogLevelMin=12, cogLocation=ToontownGlobals.TwilightTerrace),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.DonaldsDreamland),
            },
        ),
        72: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DonaldsDreamland, 1), GumballMachineBoosterReward(ToontownGlobals.DonaldsDreamland)),
            steps={
                1: VisitObjective(npc=9228),
                2: QuestFishObjective(npc=9228, fishLocation=ToontownGlobals.DonaldsDreamland,
                                      fishType=QuestItemName.GlassOfWater, fishChance=0.75),
                3: BuildingObjective(npc=9228, buildingLocation=ToontownGlobals.PajamaPlace),
                4: DefeatCogObjective(npc=9228, cogCount=20, cogLocation=ToontownGlobals.DonaldsDreamland),
                5: RecoverFromCogObjective(npc=9228, cogType='mh',
                                           recoverItem=QuestItemName.Microphone, recoverChance=0.7),
                6: QuestFishObjective(npc=9228, fishLocation=ToontownGlobals.DonaldsDreamland,
                                      fishType=QuestItemName.Megaphone, fishChance=0.7),
                7: VisitHQOfficerObjective(npcZone=ToontownGlobals.DonaldsDreamland),
            },
        ),
        73: QuestChain(
            rewards=(InventoryReward(NameplateItemType.Kudos_DDL), InventoryReward(BackgroundItemType.Kudos_DDL)),
            steps={
                1: VisitObjective(npc=9807),
                2: DefeatCogObjective(npc=9807, cogCount=15, cogLocation=ToontownGlobals.DonaldsDreamland),
                3: DefeatCogObjective(npc=9807, cogCount=5, cogType='mi'),
                4: DefeatCogObjective(npc=9807, cogCount=5, cogType='tbc'),
                5: TreasureObjective(npc=9807, treasureCount=10, treasureType=ZoneId2TreasureType[ToontownGlobals.DonaldsDreamland]),
                6: VisitHQOfficerObjective(npcZone=ToontownGlobals.DonaldsDreamland),
            },
        ),
        74: QuestChain(
            rewards=(InventoryReward(ProfilePoseItemType.Naptime), PlaygroundHealBoostReward(ToontownGlobals.DonaldsDreamland, 6)),
            steps={
                1: VisitObjective(npc=9123),
                2: VisitObjective(npc=(9123, 9804)),
                3: DefeatCogObjective(npc=(9804, 9123), cogType='fbed', taskManagerBoss=True, cogLocation=ToontownGlobals.DonaldsDreamland),
                4: VisitHQOfficerObjective(npcZone=ToontownGlobals.DonaldsDreamland),
            },
        ),
        75: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DonaldsDreamland, 2), GumballMachineBoosterReward(ToontownGlobals.DonaldsDreamland)),
            steps={
                1: VisitObjective(npc=9117),
                2: RecoverFromCogObjective(npc=9117, cogType='clerk',
                                           recoverItem=QuestItemName.Calendar, recoverChance=1.0),
                3: DefeatCogObjective(npc=9117, cogCount=52, cogLevelMin=7),
                # TODO: Implement and change to Collect Jellybeans objective.
                4: DeliverJellybeanObjective(npc=9117, jellybeans=365),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.DonaldsDreamland),
            },
        ),
        76: QuestChain(
            rewards=PlaygroundGagMultiplierReward(ToontownGlobals.DonaldsDreamland, 2),
            steps={
                1: VisitObjective(npc=9114),
                2: BuildingObjective(npc=9114, floorMinimum=6, cogTrack='s'),
                3: VisitObjective(npc=(9114, 9232)),
                4: RecoverFromCogObjective(npc=9232, cogTrack='s',
                                           recoverItem=QuestItemName.Lipstick, recoverChance=0.75, recoverRequired=25),
                5: VisitObjective(npc=(9232, 9114)),
                6: RecoverFromCogObjective(npc=9114, cogType='ms',
                                           recoverItem=QuestItemName.MoustacheHair, recoverChance=1.0, recoverRequired=15),
                7: VisitHQOfficerObjective(npcZone=ToontownGlobals.DonaldsDreamland),
            },
        ),
        77: QuestChain(
            rewards=(InventoryReward(NametagFontItemType.Cinema), PlaygroundHealBoostReward(ToontownGlobals.DonaldsDreamland, 6)),
            steps={
                1: VisitObjective(npc=9814),
                2: RecoverFromCogObjective(npc=9814, cogTrack='g',
                                           recoverItem=QuestItemName.FilmReel, recoverChance=0.75, recoverRequired=4),
                3: RecoverFromBuildingObjective(npc=9814, floorMinimum=6, cogTrack='g',
                                                recoverItem=QuestItemName.MachineParts, recoverChance=1.0),
                4: QuestFishObjective(npc=9814,
                                      fishType=QuestItemName.Bubble, fishChance=0.5, fishCount=3),
                5: VisitHQOfficerObjective(npcZone=ToontownGlobals.DonaldsDreamland),
            },
        ),
        78: QuestChain(
            rewards=(PlaygroundGagDiscountReward(ToontownGlobals.DonaldsDreamland, 3), GumballMachineBoosterReward(ToontownGlobals.DonaldsDreamland)),
            steps={
                1: VisitObjective(npc=9815),
                2: RecoverFromCogObjective(npc=9815, cogType='ds',
                                           recoverItem=QuestItemName.ShrinkMeter, recoverChance=0.85, recoverRequired=5),
                3: RecoverFromCogObjective(npc=9815, cogType='sd',
                                           recoverItem=QuestItemName.Gyroscope, recoverChance=0.8, recoverRequired=4),
                4: RecoverFromCogObjective(npc=9815, cogType='le',
                                           recoverItem=QuestItemName.VisualCalibrator, recoverChance=0.9, recoverRequired=3),
                5: RecoverFromCogObjective(npc=9815, cogType='mh',
                                           recoverItem=QuestItemName.Toothpaste, recoverChance=0.9, recoverRequired=2),
                6: RecoverFromCogObjective(npc=9815, cogType='f',
                                           recoverItem=QuestItemName.GlassLens, recoverChance=1.0),
                7: VisitHQOfficerObjective(npcZone=ToontownGlobals.DonaldsDreamland),
            },
        ),
        79: QuestChain(
            rewards=LaffReward(1),
            steps={
                1: VisitObjective(npc=9105),
                2: DefeatCogObjective(npc=9105, cogType='psetter', taskManagerBoss=True, cogLocation=ToontownGlobals.AllStarSuites),
                3: QuestCollectableObjective(npc=9105, collectable=QuestCollectable.AllStarShower),
            },
        ),
    }
)

# Map each safezone to its respective tier.
KudosSafezoneIdToTier = {
    ToontownGlobals.ToontownCentral: 1,
    ToontownGlobals.DonaldsDock: 2,
    ToontownGlobals.YeOlde: 3,
    ToontownGlobals.DaisyGardens: 4,
    ToontownGlobals.MinniesMelodyland: 5,
    ToontownGlobals.TheBrrrgh: 6,
    ToontownGlobals.OutdoorZone: 7,
    ToontownGlobals.DonaldsDreamland: 8,
}

# Map each kudos tier to the average amount of beans & exp
# earned by a main quest in the respective playground.
# These values will be 
KudosTierToBeanRewards = {
    1: 15,
    2: 35,
    3: 55,
    4: 85,
    5: 125,
    6: 160,
    7: 190,
    8: 220,
}

# Map each kudos tier to the mainline quest required to
# begin the kudos quests.
KudosTierToQuest = {
    1: (12, 1),
    2: (22, 1),
    3: (32, 1),
    4: (42, 1),
    5: (49, 1),
    6: (57, 1),
    7: (67, 1),
    8: (75, 1),
}
