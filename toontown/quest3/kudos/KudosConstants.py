# Every x hours, the kudos quests provided by the
# HQ officers will be reset.
from typing import Optional, Union, List

from toontown.quest3.QuestEnums import QuestSource
from toontown.quest3.base.QuestReference import QuestId
from toontown.toonbase import ToontownGlobals

KUDOS_RESET_INTERVAL = 3

KUDOS_ZONES = [
    ToontownGlobals.ToontownCentral,
    ToontownGlobals.DonaldsDock,
    ToontownGlobals.YeOlde,
    ToontownGlobals.DaisyGardens,
    ToontownGlobals.MinniesMelodyland,
    ToontownGlobals.TheBrrrgh,
    ToontownGlobals.OutdoorZone,
    ToontownGlobals.DonaldsDreamland,
]

# A mapping of each Kudo NPC to their playground.
KUDOS_NPC_MAP = {
    # TTC
    2007: ToontownGlobals.ToontownCentral,
    2008: ToontownGlobals.ToontownCentral,
    2009: ToontownGlobals.ToontownCentral,
    2010: ToontownGlobals.ToontownCentral,
    # BB
    1003: ToontownGlobals.DonaldsDock,
    1004: ToontownGlobals.DonaldsDock,
    1005: ToontownGlobals.DonaldsDock,
    1006: ToontownGlobals.DonaldsDock,
    # YOTT
    7002: ToontownGlobals.YeOlde,
    7003: ToontownGlobals.YeOlde,
    7004: ToontownGlobals.YeOlde,
    7011: ToontownGlobals.YeOlde,
    # DG
    5001: ToontownGlobals.DaisyGardens,
    5002: ToontownGlobals.DaisyGardens,
    5003: ToontownGlobals.DaisyGardens,
    5004: ToontownGlobals.DaisyGardens,
    # MML
    4002: ToontownGlobals.MinniesMelodyland,
    4003: ToontownGlobals.MinniesMelodyland,
    4004: ToontownGlobals.MinniesMelodyland,
    4005: ToontownGlobals.MinniesMelodyland,
    # TB
    3002: ToontownGlobals.TheBrrrgh,
    3003: ToontownGlobals.TheBrrrgh,
    3004: ToontownGlobals.TheBrrrgh,
    3005: ToontownGlobals.TheBrrrgh,
    # AA
    6004: ToontownGlobals.OutdoorZone,
    6005: ToontownGlobals.OutdoorZone,
    6006: ToontownGlobals.OutdoorZone,
    6007: ToontownGlobals.OutdoorZone,
    # DDL
    9004: ToontownGlobals.DonaldsDreamland,
    9005: ToontownGlobals.DonaldsDreamland,
    9006: ToontownGlobals.DonaldsDreamland,
    9007: ToontownGlobals.DonaldsDreamland,
}
KUDOS_NPC_IDS = list(KUDOS_NPC_MAP.keys())
KUDOS_PG_NPCS = {}
for npcId, pg in KUDOS_NPC_MAP.items():
    if pg not in KUDOS_PG_NPCS:
        KUDOS_PG_NPCS[pg] = []
    KUDOS_PG_NPCS[pg].append(npcId)


def getKudosNPCId(index: Optional[int] = None,
                  hoodId: Optional[int] = None,
                  ) -> Union[int, List[int]]:
    # General method for getting Kudos NPC ids.
    if index is not None:
        return KUDOS_NPC_IDS[index]
    elif hoodId is not None:
        return KUDOS_PG_NPCS.get(hoodId)
    raise AttributeError("Argument for getKudosNPCId not specified.")


def getKudosNPCHood(npcId: int) -> int:
    return KUDOS_NPC_MAP.get(npcId, None)


PG_DISCOUNT_AMOUNTS = {
    0: 1,
    1: 0.85,
    2: 0.70,
    3: 0.50,
}


def getPlaygroundDiscountAmount(index):
    return PG_DISCOUNT_AMOUNTS.get(index, 1.0)


# How many kudos does it require
# to rank up? (at our current rank)
RANK_REQUIREMENTS = {
    1: 8,
    2: 9,
    3: 10,
    4: 12,
    5: 14,
    6: 15,
    7: 16,
    8: 18,
    9: 20,
}

# Playground tier to post-rank 10 kudos gumball reward
PG_TIER_TO_GUMBALLS = {
    1: 20,
    2: 25,
    3: 30,
    4: 35,
    5: 40,
    6: 50,
    7: 60,
    8: 70,
}

# Playground Tier to XP total
PG_TIER_TO_EXP_TOTAL = {
    1: 10806,
    2: 18911,
    3: 32419,
    4: 48629,
    5: 64839,
    6: 86452,
    7: 116170,
    8: 162097,
}
# The XP share split between regular tasks and rank-up tasks
KUDOS_TASK_XP = 0.5
KUDOS_RANKUP_TASK_XP = 0.5

# The % XP shares split for each rankup task
KUDOS_RANKUP_XP_SHARES = [
    5, 6, 7, 8, 9, 12.5, 15, 17.5, 20
]

# How many kudos can be accumulated
# at rank 10 before being rewarded & reset?
LOOPING_KUDOS = 20
# What amount of kudos do we reset to when
# hitting the maximum amount?
MAXIMUM_KUDOS = sum(RANK_REQUIREMENTS.values())

# How many quests per NPC?
KUDOS_QUESTS_PER_NPC = 3

# Playground Discount levels
PG_DISCOUNT_VALUES = [1.00, 0.85, 0.70, 0.50]

PG_HEAL_BOOSTS = {0: 0, 5: 6, 8: 12}


def calculateChainIdForRankupTask(playgroundTier: int, taskRank: int) -> int:
    """Calculates the Kudos chain ID from the kudos playground tier and the task rank."""
    return ((playgroundTier - 1) * 10) + taskRank


def calculatePgAndTaskIndexFromRankupChainId(chainId: int) -> tuple:
    """Calculates a PG tier and rank-up task index from a chain id."""
    return (chainId // 10) + 1, (chainId % 10) - 1


def getKudosRankupGumballAmount(zoneId: int) -> int:
    from toontown.quest3.questlines.KudosQuestLine import KudosSafezoneIdToTier
    playgroundTier = KudosSafezoneIdToTier.get(zoneId, None)
    return PG_TIER_TO_GUMBALLS.get(playgroundTier, 3)


def getKudosRank(av, zoneId: int) -> int:
    """Based on the amount of kudos we currently have,
    what rank should we be at?
    """
    from toontown.quest3.questlines.KudosQuestLine import KudosSafezoneIdToTier
    playgroundTier = KudosSafezoneIdToTier.get(zoneId)
    if playgroundTier is None:
        return 1

    # Figure out what rank-up quests the av has done.
    for taskRank in RANK_REQUIREMENTS.keys():
        # What chain ID is associated with this rank?
        chainId = calculateChainIdForRankupTask(playgroundTier, taskRank)

        # Have they completed the rank-up task?
        if not av.hasCompletedQuest(QuestSource.KudosQuest, chainId):
            # If not, then they are still at this rank.
            return taskRank

    # They've done all of the rank-up tasks.
    return 10


def getCurrentKudosXp(kudos: int) -> tuple:
    """Get the current and max XP."""
    for rank, req in RANK_REQUIREMENTS.items():
        if req > kudos:
            return kudos, req
        kudos -= req
    return kudos, LOOPING_KUDOS


def getExpectedRankAndXPAndAlsoMaxXP(kudos: int, doRankup: bool = False) -> tuple:
    """Get the expected rank, XP, and max Xp for the kudos specified."""
    rank = 1
    maxXp = 0
    for rank, maxXp in RANK_REQUIREMENTS.items():
        if doRankup:
            if maxXp >= kudos:
                break
        else:
            if maxXp > kudos:
                break
        rank += 1
        kudos -= maxXp
    else:
        return getMaxRank(), kudos, LOOPING_KUDOS
    return rank, kudos, maxXp


def getMaxRank() -> int:
    return max(list(RANK_REQUIREMENTS.keys())) + 1


def getRankUpKudosTask(av, zoneId: int, includeAtlevel: bool = True) -> Optional[QuestId]:
    """
    Can the avatar receive a kudos rank up quest?

    :return: The chain id of the kudos rank up quest
    that they are able to receive. If they cannot
    receive one, it is 0.
    """
    # Safely retrieve the kudos for this zoneId.
    totalXp = av.getKudos().get(zoneId, 0)

    # Get their kudos rank.
    currentRank = getKudosRank(av, zoneId)
    # If they're rank 10, they're all done with
    # their rank up quests.
    if currentRank == 10:
        return None

    # What is our quest tier?
    from toontown.quest3.questlines.KudosQuestLine import KudosSafezoneIdToTier
    playgroundTier = KudosSafezoneIdToTier.get(zoneId)
    if not playgroundTier:
        return None

    # Go through all of the rank requirements to figure out which quest we have not done.
    for taskRank, rankXp in RANK_REQUIREMENTS.items():
        # Are we at the XP required to get this level's task?
        totalXp -= rankXp
        if includeAtlevel:
            if totalXp < 0:
                # No, we do not have enough XP, and we won't have enough.
                # If we were going to find a quest, we would have by now.
                return None
        else:
            if totalXp <= 0:
                return None

        # At this point, we are eligable to get the rank-up task.
        # What chain ID is associated with this rank?
        chainId = calculateChainIdForRankupTask(playgroundTier, taskRank)

        # Have they completed the rank-up task?
        if not av.hasCompletedQuest(QuestSource.KudosQuest, chainId):
            # If not, then they need to do this task.
            return QuestId(questSource=QuestSource.KudosQuest, chainId=chainId, objectiveId=1)

    # We've gone through all of the rank requirements now, and didn't find a task.
    # This means that we have enough XP for rank 10 and have done all of the tasks.
    # So, there is no quest to return.
    return None


def getKudosXPForQuest(questId: QuestId, quester) -> int:
    from toontown.quest3.base.QuestLine import QuestLine
    from toontown.quest3.rewards import KudosReward
    questChain = QuestLine.getQuestChainFromQuestId(questId, quester)
    rewards = questChain.getQuestRewards()
    highestKudosXp = -1
    # Iterate over each reward, checking for highest kudos amount
    for reward in rewards:
        if isinstance(reward, KudosReward):
            highestKudosXp = max(highestKudosXp, reward.getKudos())

    return highestKudosXp


def isKudosQuestRankUp(questId: QuestId, quester) -> bool:
    return getKudosXPForQuest(questId, quester) == -1


'''
The two functions below are used across the codebase to convert the kudos
representation between a list and a dictionary. The database stores the kudos
as a list of pair objects rather than a dictionary, hence the necessity of these functions.
'''


def kudosDictToList(kudosDict):
    return [(zoneId, kudos) for zoneId, kudos in kudosDict.items()]
