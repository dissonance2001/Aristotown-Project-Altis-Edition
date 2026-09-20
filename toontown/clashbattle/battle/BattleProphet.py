"""
A module for pseudo-religious predictions of battle sets, based on Toon stats.
"""
import math
import random
from typing import Dict, List, Tuple, Optional

from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum

"""
Pre-calculation data for prophetizing
"""

# A dictionary which maps HPs to a list of (level, specialization) tuples.
__prophetData: Dict[int, List[Tuple[int, int, int]]] = {}

# A dictionary for potential cog types given level minimums in each specialization.
__potentialCogs: Dict[int, Dict[int, List[str]]] = {
    SuitBattleGlobals.NORMAL: {
        1: ['cc', 'sc', 'bf', 'f', 'bgh'],
        2: ['tm', 'pp', 'b', 'p', 'pph'],
        3: ['nd', 'tw', 'pf', 'ym', 'ins'],
        4: ['gh', 'bc', 'dt', 'mm', 'cbr'],
        5: ['ms', 'nc', 'nn', 'ds', 'dl'],
        6: ['tf', 'mb', 'ac', 'hh', 'shw'],
        7: ['mi', 'ls', 'cv', 'cr', 'mg'],
        8: ['mh', 'rb', 'bs', 'tbc', 'hho'],
    },
    SuitBattleGlobals.DEFENSE: {
        2: ['pf'],
        4: ['cv'],
        5: ['ad'],
    },
    SuitBattleGlobals.ATTACK: {
        3: ['nn'],
        6: ['sh'],
        7: ['br'],
    },
}


# Prophet data calculation
__specializationOrder = [SuitBattleGlobals.NORMAL, SuitBattleGlobals.DEFENSE, SuitBattleGlobals.ATTACK]
for level in range(1, 31):
    specializationToHP = {
        spec: SuitBattleGlobals.calculateHp(data={'specialization': spec}, level=level)
        for spec in __specializationOrder
    }
    for spec, hp in specializationToHP.items():
        if spec == SuitBattleGlobals.ATTACK and level < 3:
            continue
        if spec == SuitBattleGlobals.DEFENSE and level < 2:
            continue

        __prophetData.setdefault(hp, [])
        __prophetData[hp].append((level, spec, False))

        eliteHp = int(hp * 1.5)
        __prophetData.setdefault(eliteHp, [])
        __prophetData[eliteHp].append((level, spec, True))


"""
Methods for prophetizing
"""


def __produceToonDamage(toonCount: int, requireTrack: Optional[int]) -> List[int]:
    """
    Given a count of active Toons in battle, create a list of
    damage values that they are able to accomplish with pure level 8s.

    Can be adjusted in the future to support other cases.
    """
    # Figure out the number of Cogs this set should consist of.
    __potentialCogCounts = {
        1: 0.05,
        2: 0.05,
        3: 0.20,
        4: 0.70,
    }
    cogCount = random.choices(
        population=list(__potentialCogCounts.keys()),
        weights=list(__potentialCogCounts.values()),
    )[0]
    cogCount = min(cogCount, toonCount)

    # We STILL don't have a way to run through battle calculations
    # without duplicating battle logic ... so that's what I'm gonna do here too.
    cogHps = [0] * cogCount
    trappedCogs = [0] * cogCount
    luredCogs = [0] * cogCount
    soakedCogs = [0] * cogCount
    kbCogs = [0] * cogCount

    # Calculate cog stuff now.
    for toon in range(toonCount):
        # Figure out the tracks that this Toon can use.
        potentialTracks = []

        # Some constants based on the current tracks used.
        cogsFreeToTrap = sum([int(trapStatus == 0 and lureStatus != 0 and kbStatus == 0)
                              for trapStatus, lureStatus, kbStatus in zip(trappedCogs, luredCogs, kbCogs)])
        cogsLured = cogCount - luredCogs.count(0)
        cogsUnlured = luredCogs.count(0)
        luredCogRatio = cogsLured / cogCount
        soakedCogRatio = soakedCogs.count(0) / cogCount

        # Can we use Trap?
        if cogsFreeToTrap and toonCount >= 2:
            potentialTracks.append(AttackEnum.TOON_TRAP)

        # Can we use lure?
        if cogsLured:
            potentialTracks.append(AttackEnum.TOON_LURE)

        # Sound is always viable at a chance relative to cogs lured.
        if random.random() < 0.40:
            if random.random() > math.sqrt(luredCogRatio):
                potentialTracks.append(AttackEnum.TOON_SOUND)

        # Squirt is viable depending on how many cogs are soaked.
        if random.random() < soakedCogRatio and toonCount > 2:
            potentialTracks.append(AttackEnum.TOON_SQUIRT)

        # Zap is also viable, but depending on how many cogs are not soaked.
        if random.random() < (1 - soakedCogRatio):
            potentialTracks.append(AttackEnum.TOON_ZAP)

        # Throw is viable if there are lured cogs.
        if cogsLured:
            potentialTracks.append(AttackEnum.TOON_THROW)

        # Drop is viable if there are unlured cogs.
        if cogsUnlured:
            potentialTracks.append(AttackEnum.TOON_DROP)

        # OK, pick a track to use and go with it.
        if not potentialTracks:
            continue

        # Force open with this track if it is chosen to be used (and can be used).
        if requireTrack is not None and requireTrack in potentialTracks:
            potentialTracks = [requireTrack]
            requireTrack = None

        useTrack = random.choice(potentialTracks)
        if useTrack == AttackEnum.TOON_TRAP:
            # Pick a TNT on a cog with trap status 0 and lure status != 0 and not kbd.
            potentialTargetIndices = []
            for i in range(cogCount):
                if trappedCogs[i] == 0 and luredCogs[i] != 0 and kbCogs[i] == 0:
                    potentialTargetIndices.append(i)
            if potentialTargetIndices:
                targetIndex = random.choice(potentialTargetIndices)
                trappedCogs[targetIndex] = 1
                luredCogs[targetIndex] = 0
                cogHps[targetIndex] += 280

        elif useTrack == AttackEnum.TOON_LURE:
            # Get all cogs with trap status 0 and lure status == 0 and kbStatus == 0.
            potentialTargetIndices = []
            for i in range(cogCount):
                if trappedCogs[i] == 0 and luredCogs[i] == 0 and kbCogs[i] == 0:
                    potentialTargetIndices.append(i)

            if potentialTargetIndices:
                # If there is only one Cog, go single target.
                # Otherwise, 30% for single target.
                singleTarget = len(potentialTargetIndices) == 1 or random.random() < 0.30
                if singleTarget:
                    # Lure with $100
                    targetIndex = potentialTargetIndices[0]
                    luredCogs[targetIndex] = 100
                else:
                    # Lure with presentation
                    for targetIndex in potentialTargetIndices:
                        luredCogs[targetIndex] = 75

        elif useTrack == AttackEnum.TOON_SOUND:
            # Use opera
            for targetIndex in range(cogCount):
                luredCogs[targetIndex] = 0
                cogHps[targetIndex] += 90
                kbCogs[targetIndex] = 1

        elif useTrack == AttackEnum.TOON_SQUIRT:
            # Pick random cog to squirt
            targetIndex = random.choice(list(range(cogCount)))

            # Geyser on it
            cogHps[targetIndex] += 115
            cogHps[targetIndex] += luredCogs[targetIndex]
            kbCogs[targetIndex] = 1
            soakedCogs[targetIndex] = 1

            # Splash damage
            if targetIndex != 0:
                cogHps[targetIndex - 1] += 15
                soakedCogs[targetIndex - 1] = 1
            if targetIndex != (cogCount - 1):
                cogHps[targetIndex + 1] += 15
                soakedCogs[targetIndex + 1] = 1

        elif useTrack == AttackEnum.TOON_ZAP:
            # Pick a random soaked cog.
            potentialTargetIndices = []
            for i in range(cogCount):
                if soakedCogs[i] != 0:
                    potentialTargetIndices.append(i)

            if potentialTargetIndices:
                targetIndex = random.choice(potentialTargetIndices)

                # Zip zap zap
                cogHps[targetIndex] += 240
                if targetIndex != 0 and soakedCogs[targetIndex - 1]:
                    # Go left and zap this guy too!
                    targetIndex -= 1
                    cogHps[targetIndex] += 120

                    if targetIndex != 0 and soakedCogs[targetIndex - 1]:
                        # Go left again and zap this guy too!
                        targetIndex -= 1

                    cogHps[targetIndex] += 120

                elif targetIndex != (cogCount - 1) and soakedCogs[targetIndex + 1]:
                    # Go right and zap this guy too!
                    targetIndex += 1
                    cogHps[targetIndex] += 120

                    if targetIndex != (cogCount - 1) and soakedCogs[targetIndex + 1]:
                        # Go right again and zap this guy too!
                        targetIndex += 1

                    cogHps[targetIndex] += 120

        elif useTrack == AttackEnum.TOON_THROW:
            # Pick a wedding on a cog with trap status 0 and lure status != 0.
            potentialTargetIndices = []
            for i in range(cogCount):
                if trappedCogs[i] == 0 and luredCogs[i] != 0:
                    potentialTargetIndices.append(i)

            if potentialTargetIndices:
                targetIndex = random.choice(potentialTargetIndices)
                cogHps[targetIndex] += 170
                cogHps[targetIndex] += luredCogs[targetIndex]
                kbCogs[targetIndex] = 1

        elif useTrack == AttackEnum.TOON_DROP:
            # Pick a piano on a cog with trap status 0 and lure status == 0 and kbstatus.
            potentialTargetIndices = []
            for i in range(cogCount):
                if trappedCogs[i] == 0 and luredCogs[i] == 0 and kbCogs[i] != 0:
                    potentialTargetIndices.append(i)

            if potentialTargetIndices:
                targetIndex = random.choice(potentialTargetIndices)
                cogHps[targetIndex] += 240

    # Taper off cog HPs a bit.
    cogHps = list(map(lambda x: round(x ** 0.95), cogHps))

    # Return the cog HPs dealt.
    return cogHps


def produceCogLevels(toonCount: int, requireTrack: Optional[int]) -> List[dict]:
    """
    Given a list of active Toons in battle, produce a list of
    possible cog stats for it to be going up against.

    The dict is formatted as such:
    {
        'level': int,
        'type': str,
        'elite': bool,
    }
    """
    damageDealt: List[int] = [0]
    retlist = []

    # Calculate damage dealt.
    for attempt in range(25):
        damageDealt: List[int] = __produceToonDamage(toonCount, requireTrack=requireTrack)
        if sum(damageDealt) != 0:
            # Valid damage is produced.
            break
    else:
        # No valid damage was produced.
        return retlist

    # Roll chance for a specialist. (May be weighted weirdly.)
    specializationChance = 0.15

    # Go over each value of damage dealt.
    cogHps = list(__prophetData.keys())
    hppairs = zip(cogHps, cogHps[1:])
    minDamage, maxDamage = cogHps[0], cogHps[-1]

    for damage in damageDealt:
        # If the damage is outside of cog HP bounds, ignore it.
        if not (minDamage <= damage <= maxDamage):
            continue

        # Go over each pair of damage.
        complete = False
        for lower, higher in hppairs:
            if complete:
                break

            if lower <= damage <= higher:
                # The cog is dealing damage within this HP pair.
                # Pick the lower one for ref.
                levelSpecTuples: List[Tuple[int, int, int]] = __prophetData.get(lower, [])[:]
                random.shuffle(levelSpecTuples)

                # Go through them and pick a valid one.
                for level, spec, elite in levelSpecTuples:
                    # If this cog is a specialist, chance to skip it.
                    if spec != SuitBattleGlobals.NORMAL and random.random() > specializationChance:
                        continue

                    # Figure out the suit type for this level.
                    potentialSuitTypes = []
                    levelSpecDict = __potentialCogs.get(spec, {})
                    for minLevel, suitTypes in levelSpecDict.items():
                        if level >= minLevel:
                            potentialSuitTypes.extend(suitTypes)

                    # Define the spec.
                    retlist.append({
                        'level': level,
                        'type': random.choice(potentialSuitTypes),
                        'elite': elite,
                    })

                    # All good, define this cog.
                    complete = True
                    break

    # Return the dicts of cog data.
    return retlist
