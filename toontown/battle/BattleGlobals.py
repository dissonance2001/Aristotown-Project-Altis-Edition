'''
BattleGlobals: central repository for all battle globals
'''

import math

from panda3d.core import ConfigVariableDouble, Point3, Vec3
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.statuses.StatusEffectEnums import SEE

from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import *


# defaults for camera
BattleCamFaceOffFov = 30.0
BattleCamFaceOffPos = Point3(0.0, -10.0, 4.0)
BattleCamDefaultPos = Point3(0.0, -8.6, 16.5)
BattleCamDefaultHpr = Vec3(0.0, -61.0, 0.0)
BattleCamDefaultFov = 80.0
BattleCamMenuFov = 65.0
BattleCamJoinPos = Point3(0.0, -12.0, 13.0)
BattleCamJoinHpr = Vec3(0.0, -45.0, 0.0)

# avatar track names and numbers
Tracks = TTLocalizer.BattleGlobalTracks

TrackColors: tuple[tuple[float, float, float], ...] = (
    (211.0 / 255.0, 148.0 / 255.0, 255.0 / 255.0),
    (255.0 / 255.0, 80.0 / 255.0, 80.0 / 255.0),
    (79.0 / 255.0, 190.0 / 255.0, 76.0 / 255.0),
    (93.0 / 255.0, 108.0 / 255.0, 239.0 / 255.0),
    (255.0 / 255.0, 65.0 / 255.0, 199.0 / 255.0),
    (249.0 / 255.0, 255.0 / 255.0, 93.0 / 255.0),
    (255.0 / 255.0, 145.0 / 255.0, 66.0 / 255.0),
    (67.0 / 255.0, 243.0 / 255.0, 255.0 / 255.0)
)

HealColor = (0.0, 0.9, 0.0)
HurtColor = (0.9, 0.0, 0.0)
HurtColor_Orange = (1.0, 0.5, 0.0)
HurtColor_Yellow = (1.0, 1.0, 1.0)

tpm = TextPropertiesManager.getGlobalPtr()
for i, color in enumerate(TrackColors):
    prop = TextProperties()
    prop.setTextColor(*color, 1)
    tpm.setProperties(f'toon_track_{i}', prop)

PassColor = (0.753, 0.322, 0.263)
SOSColor = (0.337, 0.361, 0.522)
SueColor = (0.494, 0.541, 0.690)
FireColor = (0.761, 0.565, 0.643)

MIN_TRACK_INDEX = 0
MAX_TRACK_INDEX = 7

MIN_LEVEL_INDEX = 0
MAX_LEVEL_INDEX = 7

LAST_REGULAR_GAG_LEVEL = 7

UBER_GAG_LEVEL_INDEX = 8

NUM_GAG_TRACKS = 8

# Toon actions and attacks
NO_TRAP = -1
LURE_SUCCEEDED = -1
SOAKED = 1
DRY = 0

# Defined in BattleGlobals.py
ATTACK_TRACKS = [
    AttackEnum.TOON_HEAL,
    AttackEnum.TOON_TRAP,
    AttackEnum.TOON_LURE,
    AttackEnum.TOON_SOUND,
    AttackEnum.TOON_SQUIRT,
    AttackEnum.TOON_ZAP,
    AttackEnum.TOON_THROW,
    AttackEnum.TOON_DROP
]
TRACK_ORDER = [
    # Rewards
    AttackEnum.TOON_FIRE,
    AttackEnum.TOON_SUE,
    AttackEnum.TOON_NPC,

    # Gag Tracks
    AttackEnum.TOON_HEAL,
    AttackEnum.TOON_TRAP,
    AttackEnum.TOON_LURE,
    AttackEnum.TOON_THROW,
    AttackEnum.TOON_SQUIRT,
    AttackEnum.TOON_ZAP,
    AttackEnum.TOON_SOUND,
    AttackEnum.TOON_DROP
]
NON_GAG_TRACK_ORDER = [attackEnum for attackEnum in TRACK_ORDER if attackEnum not in ATTACK_TRACKS]
GAG_TRACK_ORDER = [attackEnum for attackEnum in TRACK_ORDER if attackEnum in ATTACK_TRACKS]

NON_ATTACKS = [AttackEnum.TOON_UN_ATTACK, AttackEnum.TOON_PASS, AttackEnum.TOON_NO_ATTACK]

# Attack times
ATTACK_TIME = 20.0

# Reward times, in seconds
REWARD_TIMEOUT = 120
FLOOR_REWARD_TIMEOUT = 4
BUILDING_REWARD_TIMEOUT = 300

AccuracyBonuses = [0,
 20,
 40,
 60]
DamageBonuses = [0,
 20,
 20,
 20]
DamageBonusesDrop = [0,
 30,
 30,
 30]
AttackExpPerTrack = [0,
 10,
 20,
 30,
 40,
 50,
 60,
                     70]

# Maximum allowed [suits] in battle. (for gui elements, movie camera shots)
MaxBattleAvatars = 7

# Values that are mainly relevant in the BattleCalculatorAI class.

# Amount of lure rounds per lure gag.
NumRoundsLured = [1, 1, 2, 2, 3, 3, 4, 4]
NumRoundsWet = [2, 2, 3, 3, 4, 4, 5, 5]
TRAP_CONFLICT = -2
APPLY_HEALTH_ADJUSTMENTS = 1
TOONS_TAKE_NO_DAMAGE = 0
CAP_HEALS = 1
CLEAR_SUIT_ATTACKERS = 1
SUITS_UNLURED_IMMEDIATELY = 1
CLEAR_MULTIPLE_TRAPS = 0
KBBONUS_LURED_FLAG = 0
KBBONUS_TGT_LURED = 1

def getBossBattleCreditMultiplier(battleNumber: int) -> float:
    '''
    Parameters:
        battleNumber (int): 1 for the first battle and 2 for the second battle.
    
    Returns:
        out (float): the skill credit multiplier for the two first battles of the final battle sequence with the Senior V.P.
    '''
    return 1.0


def getInvasionMultiplier() -> float:
    '''
    This gets multiplied on every street battle and in every interior.
    User must first check to see if there is an invasion.
    
    Returns:
        out (float): the skill credit multiplier during invasions. (base = 2.0)
    '''
    return 2.0


def getMegaMultiplier() -> float:
    '''
    Returns:
        out (float): 3.0
    '''
    return 3.0


def getMoreXpHolidayMultiplier() -> float:
    '''
    This gets multiplied on every street battle and in every interior.
    User must first check to see if there is an invasion.

    Returns:
        out (float): the skill credit multiplier during the more xp holiday. (base = 2.0)
    '''
    return 2.0


def getCogHQMultiplier() -> float:
    '''
    Returns:
        out (float): 2.0
    '''
    return 2.0


def encodeUber(trackList):
    bitField = 0
    for trackIndex in range(len(trackList)):
        if trackList[trackIndex] > 0:
            bitField += pow(2, trackIndex)

    return bitField


def decodeUber(flagMask):
    if flagMask == 0:
        return []
    maxPower = 16
    workNumber = flagMask
    workPower = maxPower
    trackList = []
    while workPower >= 0:
        if workNumber >= pow(2, workPower):
            workNumber -= pow(2, workPower)
            trackList.insert(0, 1)
        else:
            trackList.insert(0, 0)
        workPower -= 1

    endList = len(trackList)
    foundOne: bool = False
    while not foundOne:
        if trackList[endList - 1] == 0:
            trackList.pop(endList - 1)
            endList -= 1
        else:
            foundOne = True

    return trackList


def getUberFlag(flagMask, index):
    decode = decodeUber(flagMask)
    if index >= len(decode):
        return 0
    else:
        return decode[index]


def getUberFlagSafe(flagMask, index):
    if flagMask == 'unknown' or flagMask < 0:
        return -1
    else:
        return getUberFlag(flagMask, index)


def getFancyTrackText(track: AttackEnum) -> str:
    return {
        AttackEnum.TOON_HEAL: '\1GagTrack_toon-up\1Toon-Up\2',
        AttackEnum.TOON_TRAP: '\1GagTrack_trap\1Trap\2',
        AttackEnum.TOON_LURE: '\1GagTrack_lure\1Lure\2',
        AttackEnum.TOON_SOUND: '\1GagTrack_sound\1Sound\2',
        AttackEnum.TOON_SQUIRT: '\1GagTrack_squirt\1Squirt\2',
        AttackEnum.TOON_ZAP: '\1GagTrack_zap\1Zap\2',
        AttackEnum.TOON_THROW: '\1GagTrack_throw\1Throw\2',
        AttackEnum.TOON_DROP: '\1GagTrack_drop\1Drop\2'
    }.get(track, 'Unknown Track!')


def getCounterfeitCooldownsForMaxLevel(maxLevel: int):
    baseCd: int = 3 if maxLevel == 7 else 2
    return {maxLevel: baseCd,
            maxLevel - 1: baseCd - 1,
            maxLevel - 2: (baseCd - 2) if maxLevel == 7 else (baseCd - 1)}


def getSurrenderVotes(numToons: int) -> int:
    # If the group has 4 or fewer toons, all must surrender.
    # If the group has 5 or more toons, all except one must surrender.
    return numToons if numToons <= 4 else numToons - 1


# Sent when an avatar is being targeted by a damaging attack
BattleAvatarTargetedMessage = 'Battle-AvatarTargeted'
