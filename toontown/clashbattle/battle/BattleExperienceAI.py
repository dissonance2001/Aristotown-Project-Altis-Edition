from copy import deepcopy
import math

from panda3d.core import ConfigVariableBool

from toontown.clashbattle.battle import BattleGlobals, SuitBattleGlobals
from toontown.crafting import CraftingGlobals
from toontown.inventory.enums.ItemEnums import MaterialItemType, ItemType
from toontown.quest3.context.GagExperienceContext import GagExperienceContext
from toontown.toon.DistributedNPCToonBaseAI import DistributedNPCToonBaseAI
from toontown.toon.ToonStatsGlobals import ToonStats
from toontown.toonbase import ToontownGlobals
from toontown.toon.gui.ToonTipGlobals import TTE
from toontown.quest3.context.DefeatCogContext import DefeatCogContext
import random, time

from toontown.utils.DirectNotifyCategory import getNotify

'''
This file contains a collection of functions to manage battle
experience and generation of reward movies on the AI side.

These functions used to be methods on DistributedBattleBaseAI,
BattleCalculatorAI, and Movie, but they have been pulled out here to
collect them together and generalize them for final battles, which
might have as many as 8 Toons.
'''

notify = getNotify('BattleExperienceAI')


def getMultiplier():
    mult = 1
    if simbase.air.wantRecoveryXp:
        start = simbase.air.recoveryXpStart
        ctime = time.time()
        if ctime < start + 10800:
            mult = 3
        elif ctime < start + 172800:
            mult = 2

    return mult


def getSkillGained(toonSkillPtsGained, toonId, track):
    """
    ////////////////////////////////////////////////////////////////////
    // Function:    Get the skill points obtained so far in this battle
    //              for a toon position and a specific attack track
    // Parameters:  skill pts earned, which toon to get the skill points for
    //              track, the attack track to get the skill pts for
    // Changes:
    // Returns:     Skill points received so far in this battle
    ////////////////////////////////////////////////////////////////////
    """
    exp = 0
    expList = []
    if toonSkillPtsGained.get(toonId, None) is not None:
        expList = toonSkillPtsGained.get(toonId, None)
        exp = expList[track] * getMultiplier()
    else:
        expList = [0, 0, 0, 0, 0, 0, 0, 0]
        exp = expList[track]
    return (int(exp))


def getBattleExperience(numToons, activeToons, toonExp,
                        toonSkillPtsGained, toonOrigQuests,
                        toonOrigMerits, toonMerits, toonParts):
    p = []

    toonBattleExps = []

    for k in range(numToons):
        toon = None

        if k < len(activeToons):
            toonId = activeToons[k]
            toon = simbase.air.doId2do.get(toonId)

        # Don't give experience to NPC Toons!
        if isinstance(toon, DistributedNPCToonBaseAI):
            continue

        if toon is None:
            toonBattleExp = [
                -1,
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [],
                [],
                [0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0]
            ]
        else:
            origExp = toonExp[toonId]
            earnedExp = []
            for i, _ in enumerate(BattleGlobals.Tracks):
                earnedExp.append(getSkillGained(toonSkillPtsGained, toonId, i))

            origQuests = toonOrigQuests.get(toonId, [])
            origMerits = toonOrigMerits.get(toonId, [])
            merits = toonMerits.get(toonId, [0, 0, 0, 0, 0])
            parts = toonParts.get(toonId, [0, 0, 0, 0, 0])

            toonBattleExp = [
                toonId,
                origExp,
                earnedExp,
                deepcopy(origQuests),
                origMerits,
                merits,
                parts
            ]

        toonBattleExps.append(toonBattleExp)

    p.append(toonBattleExps)

    # Create a lookup table of the indices of the active toons
    toonIndices = {}

    for i in range(len(activeToons)):
        # Map toonID -> toon's battle index
        toonIndices[activeToons[i]] = i

    # Blank field for updated quests.
    p.append([])

    return p


def assignRewards(activeToons, toonSkillPtsGained, suitsKilled, zoneId, helpfulToons=None, helpfulToons2Rounds=None):
    helpfulToons = helpfulToons or []

    # Build a list of all active toons in the battle
    activeToonList = []
    for t in activeToons:
        toon = simbase.air.doId2do.get(t)
        # Don't give rewards to NPC Toons!
        if isinstance(toon, DistributedNPCToonBaseAI):
            continue
        if toon is not None:
            activeToonList.append(toon)

    updatedQuests = []

    # Now walk through the list and add the gained experience to
    # each toon.
    for toon in activeToonList:
        toonExp = 0
        extraToonExp = 0  # Any EXP that should go past the standard battle cap
        expArray = []
        numElites = 0
        bountiesRedeemed = []
        totalGagXp = 0
        for i in range(len(BattleGlobals.Tracks)):
            exp = getSkillGained(toonSkillPtsGained, toon.doId, i)
            expArray.append(exp)
            totalExp = exp + toon.experience[i]

            if totalExp >= BattleGlobals.regMaxSkill:
                # This is the first time the Toon has reached this experience level.
                # Give them an achievement!
                simbase.air.achievementsManager.maxGag(toon.doId, i)
            if exp > 0:
                newGagList = toon.experience.getNewGagIndexList(i, exp)
                toon.experience.addExp(i, amount=exp)
                toon.inventory.addItemWithList(i, newGagList)
            simbase.air.quest3Manager.progressObjective(quester=toon, context=GagExperienceContext(
                track=i,
                experience=exp
            ))

        # Handle jellybean rewards
        beansEarned = 0

        gumballsEarned = 0

        # Also handle batcoin rewards
        batcoinsEarned = 0
        batcoinMult = 1.0

        timesLootChecked = {}  # Dict[suitName, checkedAmount]
        # Step through each suit killed in battle
        for suit in suitsKilled:
            level = suit['level']
            if level is None:
                continue

            # If it's an executive cog, the jellybean reward is 5x their level
            # Otherwise, it is 2.5x
            if suit['isElite']:
                mult = 5
                if random.random() <= .5:
                    beansEarned += level * 5
                numElites += 1
            else:
                mult = 2.5
                if random.random() <= .1:
                    beansEarned += level * 2

            # Handle Toon XP.
            # Toon XP gets same multipliers as bean rewards
            if toonExp >= BattleGlobals.ExperienceCap:
                toonExp = BattleGlobals.ExperienceCap
            else:
                toonExp += int(level * mult)

            # Gumball/bean/toon exp bounties per specific cogs killed
            bountiesToCheck = [suit['type']]
            # Check if this cog is part of a bounty group.
            # If it is, we need to reward them for every cog in this set, regardless of if they actually
            # killed them or not.
            if suit['type'] in SuitBattleGlobals.COG_BOUNTIES and 'group' in SuitBattleGlobals.COG_BOUNTIES[suit['type']]:
                groupType = SuitBattleGlobals.COG_BOUNTIES[suit['type']]['group']
                otherMembers = SuitBattleGlobals.COG_BOUNTY_GROUPS[groupType][:]
                if suit['type'] in otherMembers:
                    otherMembers.remove(suit['type'])
                bountiesToCheck.extend(otherMembers)

            # Run through all bounties we need to check
            for suitName in bountiesToCheck:
                if suitName in SuitBattleGlobals.COG_BOUNTIES and suitName not in bountiesRedeemed and toon.cogBountiesRemainingToday() > 0:
                    # Make sure said bounty is actually available for this toon
                    if toon.cogBountyAvailable(suitName):
                        bountyDict = SuitBattleGlobals.COG_BOUNTIES[suitName]
                        # Go ahead and add each of the bounties
                        for bountyType in bountyDict.keys():
                            if bountyType == ToontownGlobals.CogBountyTypes.Gumballs:
                                gumballsEarned += bountyDict[bountyType]
                            elif bountyType == ToontownGlobals.CogBountyTypes.Jellybeans:
                                beansEarned += bountyDict[bountyType]
                            elif bountyType == ToontownGlobals.CogBountyTypes.Experience:
                                extraToonExp += bountyDict[bountyType]
                            elif bountyType == ToontownGlobals.CogBountyTypes.Merits:
                                pass  # TODO: Add merits whenever we need them
                        bountiesRedeemed.append(suitName)

            # Handle loot for all suits that were killed.
            # First, check if this suit has any loot associated with it.
            if suit['type'] in SuitBattleGlobals.SUIT_LOOT:
                lootTables = SuitBattleGlobals.SUIT_LOOT[suit['type']]
                # Roll each of the suit's loot tables for the current Toon.
                for lootTable in lootTables:
                    # Pass through other Cogs that have already been checked for loot
                    # We do this in cases where cogs may have been defeated multiple times in one battle
                    # This ensures that loot can add those cogs from the battle previously if they need to.
                    lootTable.rollTable(toon, extraArgs=[timesLootChecked.get(suit['type'], 0)])
                # Mark them as being checked over for loot previously
                timesLootChecked.setdefault(suit['type'], 0)
                timesLootChecked[suit['type']] = timesLootChecked[suit['type']] + 1

            # all things batcoin I suppose
            if suit['isBoss']:
                batcoinsEarned += ToontownGlobals.BatcoinBattlePointsBoss
            elif suit['type'] in ToontownGlobals.BatcoinBattlePointsEX:
                batcoinsEarned += ToontownGlobals.BatcoinBattlePointsEX[suit['type']]
            else:
                if suit['level'] < 15:
                    batcoinsEarned += ToontownGlobals.BatcoinBattlePointsCogs[0]
                else:
                    batcoinsEarned += ToontownGlobals.BatcoinBattlePointsCogs[1]
                if random.random() < 0.25:
                    batcoinsEarned += 1

        # Handle field updates for both beans and XP
        currToonExp = toon.getToonExp()
        toon.b_setToonExp(currToonExp + toonExp + extraToonExp)
        toon.b_setExperience(list(toon.experience))
        if beansEarned > 0:
            toon.sendEarnMoneyAnimation(beansEarned)  # Send an update to the client to display the jar animation for beans earned
            toon.addMoney(beansEarned)
        if gumballsEarned > 0:
            # See how many remaining gumballs we have for the week
            remainingBountyGumballs = toon.remainingWeeklyGumballs()
            # Cap the number of gumballs earned to the # of weekly gumballs remaining
            fixedGumballNum = min(gumballsEarned, remainingBountyGumballs)
            # If we have gumballs remaining after the cappage, send them over, show the toon,
            # and record them for their weekly gumball progress.
            if fixedGumballNum > 0:
                toon.addMoney(fixedGumballNum, doAnim=True, currencyType=MaterialItemType.Gumballs)
                toon.addWeeklyBountyGumballs(fixedGumballNum)
                if toon.getWeeklyBountyGumballsAmount() >= ToontownGlobals.CogBountyWeeklyGumballLimit:
                    # If our gumballs got capped, send them a tip telling them why.
                    toon.showToonTip(TTE.TIP_GUMBALL_LIMIT)

        toon.giveBatcoins(batcoinsEarned, mult=batcoinMult)
        toon.d_setInventory(toon.inventory.makeNetString())
        # Mark any cog bounties we have redeemed by killing them
        if len(bountiesRedeemed) > 0:
            toon.addCogBountyCooldowns(bountiesRedeemed)
            # Cog Bounty toon tip
            toon.showToonTip(TTE.TIP_SWEETENERS)

        # Tell the quest manager about the cogs this toon killed
        # so it can update the quest progress
        if ConfigVariableBool('battle-passing-no-credit', True).getValue():
            # Check if the toon was a helpful toon. Unhelpful toons will not
            # receive quest credit.
            if helpfulToons and toon.doId in helpfulToons:
                if toon in activeToonList:
                    simbase.air.quest3Manager.progressObjective(quester=toon, context=DefeatCogContext(
                        suitsKilled=suitsKilled,
                        zoneId=zoneId
                    ))
                simbase.air.cogPageManager.toonKilledCogs(toon.doId, suitsKilled, zoneId)
                simbase.air.statsLeaderboardManager.updateLeaderboardCogs(toon, suitsKilled)

                # Handle stats for the Toons in battle
                toon.addStat(ToonStats.COGS, len(suitsKilled))
                toon.addStat(ToonStats.ELITES, numElites)
                simbase.air.achievementsManager.cogs(toon.doId)
            # Looks like the toon wasnt too helpful...
            else:
                notify.debug('toon=%d unhelpful not getting killed cog quest credit' % toon.doId)
        else:
            if toon in activeToonList:
                simbase.air.quest3Manager.progressObjective(quester=toon, context=DefeatCogContext(
                    suitsKilled=suitsKilled,
                    zoneId=zoneId,
                ))
            simbase.air.cogPageManager.toonKilledCogs(toon.doId, suitsKilled, zoneId)
            simbase.air.statsLeaderboardManager.updateLeaderboardCogs(toon, suitsKilled)

        updatedQuests.append((toon.doId, [ref.toStruct() for ref in toon.getVisibleQuests()]))

    # Let's handle rewarding the helpful toons with club coins.
    # Get a list of avatars (that actually exist)
    toons = [simbase.air.doId2do.get(avId) for avId in helpfulToons]
    toons = [av for av in toons if av]

    # Calculate the amount of club coins to give.
    clubCoins = sum([0.03 if suit["level"] is not None and suit["level"] >= 15 else 0.02 for suit in suitsKilled])

    # Reward the club coins.
    simbase.air.clubMgr.addClubCoinsForAvatars(toons, clubCoins)

    return updatedQuests


def getNumMatDrop(difficulty):
    return (difficulty + 1) * 4 + random.randint(difficulty+1, (
            difficulty + 1) * 3)  # Has a 1/15 chance to double materials, at best
