"""
BattleGlobals: central repository for all battle globals
"""

import math
from enum import IntEnum, auto
from panda3d.core import ConfigVariableDouble, Point3, Vec3
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE

from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownGlobals import *


# defaults for camera
BattleCamFaceOffFov = 30.0
BattleCamFaceOffPos = Point3(0, -10, 4)
BattleCamDefaultPos = Point3(0, -8.6, 16.5)
BattleCamDefaultHpr = Vec3(0, -61, 0)
BattleCamDefaultFov = 80.0
BattleCamMenuFov = 65.0
BattleCamJoinPos = Point3(0, -12, 13)
BattleCamJoinHpr = Vec3(0, -45, 0)

# avatar start hp
BaseHp = 15

# avatar starting training points
BaseTrainingPoints = 4

# avatar track names and numbers
Tracks = TTLocalizer.BattleGlobalTracks

TrackColors = (
    (211 / 255.0, 148 / 255.0, 255 / 255.0),
    (255 / 255.0, 80 / 255.0, 80 / 255.0),
    (79 / 255.0, 190 / 255.0, 76 / 255.0),
    (93 / 255.0, 108 / 255.0, 239 / 255.0),
    (255 / 255.0, 65 / 255.0, 199 / 255.0),
    (249 / 255.0, 255 / 255.0, 93 / 255.0),
    (255 / 255.0, 145 / 255.0, 66 / 255.0),
    (67 / 255.0, 243 / 255.0, 255 / 255.0),
)

HealColor = (0, 0.9, 0)
HurtColor = (0.9, 0, 0)
HurtColor_Orange = (1, 0.5, 0)
HurtColor_Yellow = (1, 1, 0)

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
NO_TRAP         = -1
LURE_SUCCEEDED  = -1
SOAKED          = 1
DRY             = 0

# Defined in BattleGlobals.py
ATTACK_TRACKS = [
    AttackEnum.TOON_HEAL,
    AttackEnum.TOON_TRAP,
    AttackEnum.TOON_LURE,
    AttackEnum.TOON_THROW,
    AttackEnum.TOON_SQUIRT,
    AttackEnum.TOON_ZAP,
    AttackEnum.TOON_SOUND,
    AttackEnum.TOON_DROP,
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
    AttackEnum.TOON_DROP,
]
NON_GAG_TRACK_ORDER = [attackEnum for attackEnum in TRACK_ORDER if attackEnum not in ATTACK_TRACKS]
GAG_TRACK_ORDER = [attackEnum for attackEnum in TRACK_ORDER if attackEnum in ATTACK_TRACKS]

NON_ATTACKS = [AttackEnum.TOON_UN_ATTACK, AttackEnum.TOON_PASS, AttackEnum.TOON_NO_ATTACK]

# Attack times
ATTACK_TIME = 20.0

# Delay between multiple gags in a track being used
TOON_TRAP_DELAY = 0.8

TOON_SOUND_DELAY    = 1.0

TOON_THROW_DELAY        = 0.5
TOON_THROW_SUIT_DELAY   = 1.0

TOON_SQUIRT_DELAY       = 0.5
TOON_SQUIRT_SUIT_DELAY  = 1.0

TOON_ZAP_DELAY      = 0.5
TOON_ZAP_SUIT_DELAY = 2

TOON_DROP_DELAY         = 0.8
TOON_DROP_SUIT_DELAY    = 1.0

TOON_RUN_T          = 3.3
TIMEOUT_PER_USER    = 5

TOON_FIRE_DELAY         = 0.5
TOON_FIRE_SUIT_DELAY    = 1.0

# Reward times, in seconds
REWARD_TIMEOUT          = 120
FLOOR_REWARD_TIMEOUT    = 4
BUILDING_REWARD_TIMEOUT = 300


class BattleStateEnum(IntEnum):
    INACTIVE            = auto()
    JOINING             = auto()
    JOINING_NOT_PENDING = auto()
    PENDING             = auto()
    ACTIVE              = auto()
    RUNNING             = auto()


class BattleOrderPriority(IntEnum):
    NEUTRAL   = auto()
    BEGINNING = auto()
    MIDDLE    = auto()
    END       = auto()


# Alias
BOP = BattleOrderPriority

CLIENT_INPUT_TIMEOUT = ConfigVariableDouble("battle-input-timeout", TTLocalizer.BBbattleInputTimeout).getValue()


def levelAffectsGroup(track, level):
    return attackAffectsGroup(track, level)


def attackAffectsGroup(track, level, attackType=None):
    if track in ATTACK_TRACKS:
        return AvPropTargetCat[AvPropTarget[track]][level]

    return False


# A little pad time added to server time calculations, to allow for
# slow or out-of-sync clients.  In general, the AI server will give
# each client the expected time to complete its movie, plus
# SERVER_BUFFER_TIME, and then will ask all the clients to move on
# with or without the slow one(s).
SERVER_BUFFER_TIME = 2.0

SERVER_INPUT_TIMEOUT = CLIENT_INPUT_TIMEOUT + SERVER_BUFFER_TIME

# The maximum time we expect a suit to take walk to its position in
# battle.
MAX_JOIN_T = TTLocalizer.BBbattleInputTimeout / 4

# The length of time for a faceoff taunt.
FACEOFF_TAUNT_T = 3.5
FACEOFF_LOOK_AT_PROP_T = 6

# The amount of time it takes to open up the elevator doors and walk
# out.
ELEVATOR_T = 4.0

BATTLE_SMALL_VALUE = 1e-07

# This is the furthest we expect to have to walk from the face-off to
# get the battle.  If we are further away than this, we suspect we are
# victims of clock skew.
MAX_EXPECTED_DISTANCE_FROM_BATTLE = 50.0

# Rounds of being afk til an av is given a warning prompt.
AV_AFK_ROUNDS = 2

# which props buffs which track
PropTypeToTrackBonus = {
    AnimPropTypes.Hydrant: AttackEnum.TOON_SQUIRT,
    AnimPropTypes.Mailbox: AttackEnum.TOON_THROW,
    AnimPropTypes.Trashcan: AttackEnum.TOON_HEAL,
}

# avatar skill levels (totalled)
Levels = [
    [0, 20, 100, 500, 2000, 5000, 9000, 14000],  # Toon-Up
    [0, 20, 100, 500, 2000, 5000, 9000, 14000],  # Trap
    [0, 20, 100, 500, 2000, 5000, 9000, 14000],  # Lure
    [0, 20, 100, 500, 2000, 5000, 9000, 14000],  # Sound
    [0, 20, 100, 500, 2000, 5000, 9000, 14000],  # Throw
    [0, 20, 100, 500, 2000, 5000, 9000, 14000],  # Squirt
    [0, 20, 100, 500, 2000, 5000, 9000, 14000],  # Zap
    [0, 20, 100, 500, 2000, 5000, 9000, 14000],  # Drop
]


def getGagLevels(experience: list, trackAccess: list) -> list:
    from toontown.toon.Experience import Experience
    expInfo = Experience(*experience)
    return [
        (expInfo.getExpLevel(i) + 1 if trackAccess[i] else 0)
        for i in range(NUM_GAG_TRACKS)
    ]

regMaxSkill = 20000
UberSkill = 1000
MaxSkill = regMaxSkill

# This is the maximum amount of experience per track that may be earned in one battle (or in one building).
ExperienceCap = 1500

# This accuracy (a percentage) is the highest that can ever be attained.
MaxToonAcc = 95

# If toon accuracy breaks the previous cap, it now caps at 99.
MaxToonAccBrokeCap = 99

# This accuracy (a percentage) is the highest that any given track can ever attain.
MaxToonTrackAcc = {
    AttackEnum.TOON_DROP: 96
}

# These are inherent exp multipliers for certain tracks.
InherentTrackExpMult = {
    AttackEnum.TOON_HEAL: 2,
}

# avatar starting skill level
StartingLevel = 0

CarryLimits = (
    (  # Toon-Up
        (10, 0, 0, 0, 0, 0, 0, 0),
        (10, 5, 0, 0, 0, 0, 0, 0),
        (15, 10, 5, 0, 0, 0, 0, 0),
        (20, 15, 10, 5, 0, 0, 0, 0),
        (25, 20, 15, 10, 3, 0, 0, 0),
        (30, 25, 20, 15, 7, 3, 0, 0),
        (30, 25, 20, 15, 7, 3, 2, 0),
        (30, 25, 20, 15, 7, 3, 2, 1),
    ),
    (  # Trap
        (10, 0, 0, 0, 0, 0, 0, 0),
        (10, 5, 0, 0, 0, 0, 0, 0),
        (15, 10, 5, 0, 0, 0, 0, 0),
        (20, 15, 10, 5, 0, 0, 0, 0),
        (25, 20, 15, 10, 3, 0, 0, 0),
        (30, 25, 20, 15, 7, 3, 0, 0),
        (30, 25, 20, 15, 7, 3, 2, 0),
        (30, 25, 20, 15, 7, 3, 2, 1),
    ),
    (  # Lure
        (10, 0, 0, 0, 0, 0, 0, 0),
        (10, 5, 0, 0, 0, 0, 0, 0),
        (15, 10, 5, 0, 0, 0, 0, 0),
        (20, 15, 10, 5, 0, 0, 0, 0),
        (25, 20, 15, 10, 3, 0, 0, 0),
        (30, 25, 20, 15, 7, 3, 0, 0),
        (30, 25, 20, 15, 7, 3, 2, 0),
        (30, 25, 20, 15, 7, 3, 2, 1),
    ),
    (  # Sound
        (10, 0, 0, 0, 0, 0, 0, 0),
        (10, 5, 0, 0, 0, 0, 0, 0),
        (15, 10, 5, 0, 0, 0, 0, 0),
        (20, 15, 10, 5, 0, 0, 0, 0),
        (25, 20, 15, 10, 3, 0, 0, 0),
        (30, 25, 20, 15, 7, 3, 0, 0),
        (30, 25, 20, 15, 7, 3, 2, 0),
        (30, 25, 20, 15, 7, 3, 2, 1),
    ),
    (  # Throw
        (10, 0, 0, 0, 0, 0, 0, 0),
        (10, 5, 0, 0, 0, 0, 0, 0),
        (15, 10, 5, 0, 0, 0, 0, 0),
        (20, 15, 10, 5, 0, 0, 0, 0),
        (25, 20, 15, 10, 3, 0, 0, 0),
        (30, 25, 20, 15, 7, 3, 0, 0),
        (30, 25, 20, 15, 7, 3, 2, 0),
        (30, 25, 20, 15, 7, 3, 2, 1),
    ),
    (  # Squirt
        (10, 0, 0, 0, 0, 0, 0, 0),
        (10, 5, 0, 0, 0, 0, 0, 0),
        (15, 10, 5, 0, 0, 0, 0, 0),
        (20, 15, 10, 5, 0, 0, 0, 0),
        (25, 20, 15, 10, 3, 0, 0, 0),
        (30, 25, 20, 15, 7, 3, 0, 0),
        (30, 25, 20, 15, 7, 3, 2, 0),
        (30, 25, 20, 15, 7, 3, 2, 1),
    ),
    (  # Zap
        (10, 0, 0, 0, 0, 0, 0, 0),
        (10, 5, 0, 0, 0, 0, 0, 0),
        (15, 10, 5, 0, 0, 0, 0, 0),
        (20, 15, 10, 5, 0, 0, 0, 0),
        (25, 20, 15, 10, 3, 0, 0, 0),
        (30, 25, 20, 15, 7, 3, 0, 0),
        (30, 25, 20, 15, 7, 3, 2, 0),
        (30, 25, 20, 15, 7, 3, 2, 1),
    ),
    (  # Drop
        (10, 0, 0, 0, 0, 0, 0, 0),
        (10, 5, 0, 0, 0, 0, 0, 0),
        (15, 10, 5, 0, 0, 0, 0, 0),
        (20, 15, 10, 5, 0, 0, 0, 0),
        (25, 20, 15, 10, 3, 0, 0, 0),
        (30, 25, 20, 15, 7, 3, 0, 0),
        (30, 25, 20, 15, 7, 3, 2, 0),
        (30, 25, 20, 15, 7, 3, 2, 1),
    ),
)

# avatar prop maxes
MaxProps = ((15, 40), (30, 60), (75, 80))

# Sound gag names (CLO).
# These map to props in BattleProps, but it must be defined here because BattleProps cannot be included on the AI.
soundNames = [
    "kazoo",
    "bikehorn",
    "whistle",
    "bugle",
    "aoogah",
    "elephant",
    "fog_horn",
    "singing",
]
soundPosHpr = [
    (-1.2, -1.3, 0.1, 145, 0, 85),
    (-1.1, -1.4, 0.1, 145, 0, 0),
    (-1.2, -1.3, 0.1, 145, 0, 85),
    (-1.3, -1.4, 0.1, 145, 0, 85),
    (-1.0, -1.5, 0.2, 145, 0, 85),
    (-0.6, -0.9, 0.15, 145, 0, 85),
    (-0.8, -0.9, 0.2, 145, 0, 0),
    (-0.8, -0.9, 0.2, 145, 0, 90),
]
soundScale = [
    (0.2, 0.2, 0.2),
    (0.65, 0.65, 0.65),
    (0.2, 0.2, 0.2),
    (0.4, 0.4, 0.4),
    (0.5, 0.5, 0.5),
    (0.3, 0.4, 0.2),
    (0.3, 0.3, 0.3),
    (1.7, 1.7, 1.7),
]

# Pie names.
# These map to props in BattleProps, but it must be defined here because BattleProps cannot be included on the AI.
pieNames = [
    "cupcake",
    "fruitpie-slice",
    "creampie-slice",
    "birthday-cake-slice",
    "fruitpie",
    "creampie",
    "birthday-cake",
    "wedding-cake",
    "lawbook",
    "pineapple",
    "snowball",
]

# avatar prop icon filenames (unused)
AvProps = (
    ("feather", "bullhorn", "lipstick", "bamboocane", "pixiedust", "baton", "baton"),
    ("banana", "rake", "spring", "marbles", "quicksand", "trapdoor", "xspot", "tnt", "traintrack"),
    ("1dollar", "smmagnet", "5dollar", "bigmagnet", "10dollar", "hypnogogs", "hypnogogs"),
    ("bikehorn", "whistle", "bugle", "aoogah", "elephant", "foghorn", "singing"),
    ("cupcake", "fruitpieslice", "creampieslice", "fruitpie", "creampie", "cake", "cake"),
    ("flower", "waterglass", "waterballoon", "bottle", "firehose", "stormcloud", "stormcloud"),
    ("flower", "waterglass", "waterballoon", "bottle", "firehose", "stormcloud", " stormcloud"),
    ("flowerpot", "sandbag", "anvil", "weight", "safe", "piano", "piano"),
)

# avatar prop icon filenames (new)
AvPropsNew = [[f"prop_{track}_{level}" for level in range(MAX_LEVEL_INDEX + 1)] for track in range(NUM_GAG_TRACKS)]

# prettier on-screen versions of the prop names
AvPropStrings = TTLocalizer.BattleGlobalAvPropStrings

# prettier on-screen versions of the prop names for singular usage
AvPropStringsSingular = TTLocalizer.BattleGlobalAvPropStringsSingular

# prettier on-screen versions of the prop names for plural usage
AvPropStringsPlural = TTLocalizer.BattleGlobalAvPropStringsPlural

# avatar base prop accuracies
AvPropAccuracy = (
    (100, 100, 100, 100, 100, 100, 100, 100),           # Toonup
    (0, 0, 0, 0, 0, 0, 0, 0),                   # Trap
    (80, 75, 80, 75, 85, 80, 85, 85),           # Lure
    (95, 95, 95, 95, 95, 95, 95, 95),           # Sound
    (95, 95, 95, 95, 95, 95, 95, 95),           # Squirt
    (100, 100, 100, 100, 100, 100, 100, 100,),  # Zap
    (75, 75, 75, 75, 75, 75, 75, 75),           # Throw
    (60, 60, 60, 60, 60, 60, 60, 60),           # Drop
)

# avatar prop damages
# each entry represents a toon prop track and is a list of pairs, the first of each pair represents the damage range
# (min to max) which maps to the second pair which represents the toon's track exp.
# So the higher the toon's exp in that prop's track, the more damage that particular prop can do
AvPropDamage = (
    # Toon-Up
    (
        ((8, 12), (Levels[0][0], Levels[0][1])),
        ((18, 24), (Levels[0][1], Levels[0][2])),
        ((25, 30), (Levels[0][2], Levels[0][3])),
        ((39, 45), (Levels[0][3], Levels[0][4])),
        ((50, 60), (Levels[0][4], Levels[0][5])),
        ((69, 84), (Levels[0][5], Levels[0][6])),
        ((85, 90), (Levels[0][6], Levels[0][7])),
        ((105, 135), (Levels[0][7], MaxSkill)),
    ),
    # Trap
    (
        ((12, 14), (Levels[1][0], Levels[1][1])),
        ((21, 28), (Levels[1][1], Levels[1][2])),
        ((35, 45), (Levels[1][2], Levels[1][3])),
        ((55, 75), (Levels[1][3], Levels[1][4])),
        ((85, 115), (Levels[1][4], Levels[1][5])),
        ((130, 160), (Levels[1][5], Levels[1][6])),
        ((180, 220), (Levels[1][6], Levels[1][7])),
        ((240, 280), (Levels[1][7], MaxSkill)),
    ),
    # Lure
    (
        ((2, 5), (Levels[2][0], Levels[2][1])),
        ((6, 10), (Levels[2][1], Levels[2][2])),
        ((10, 25), (Levels[2][2], Levels[2][3])),
        ((15, 30), (Levels[2][3], Levels[2][4])),
        ((35, 65), (Levels[2][4], Levels[2][5])),
        ((35, 50), (Levels[2][5], Levels[2][6])),
        ((75, 100), (Levels[2][6], Levels[2][7])),
        ((55, 75), (Levels[2][7], MaxSkill)),
    ),
    # Sound
    (
        ((4, 5),   (Levels[3][0], Levels[3][1])),
        ((7, 10),  (Levels[3][1], Levels[3][2])),
        ((12, 16), (Levels[3][2], Levels[3][3])),
        ((18, 23), (Levels[3][3], Levels[3][4])),
        ((25, 30), (Levels[3][4], Levels[3][5])),
        ((35, 50), (Levels[3][5], Levels[3][6])),
        ((55, 70), (Levels[3][6], Levels[3][7])),
        ((75, 90), (Levels[3][7], MaxSkill)),
    ),
    # Squirt
    (
        ((3, 4), (Levels[4][0], Levels[4][1])),
        ((6, 8), (Levels[4][1], Levels[4][2])),
        ((10, 12), (Levels[4][2], Levels[4][3])),
        ((18, 21), (Levels[4][3], Levels[4][4])),
        ((27, 30), (Levels[4][4], Levels[4][5])),
        ((45, 60), (Levels[4][5], Levels[4][6])),
        ((65, 90), (Levels[4][6], Levels[4][7])),
        ((95, 120), (Levels[4][7], MaxSkill)),
    ),
    # Zap
    (
        ((6, 12), (Levels[5][0], Levels[5][1])),
        ((14, 20), (Levels[5][1], Levels[5][2])),
        ((24, 36), (Levels[5][2], Levels[5][3])),
        ((40, 60), (Levels[5][3], Levels[5][4])),
        ((70, 90), (Levels[5][4], Levels[5][5])),
        ((100, 140), (Levels[5][5], Levels[5][6])),
        ((150, 190), (Levels[5][6], Levels[5][7])),
        ((200, 240), (Levels[5][7], MaxSkill)),
    ),
    # Throw
    (
        ((5, 8), (Levels[6][0], Levels[6][1])),
        ((10, 13), (Levels[6][1], Levels[6][2])),
        ((15, 20), (Levels[6][2], Levels[6][3])),
        ((30, 35), (Levels[6][3], Levels[6][4])),
        ((48, 56), (Levels[6][4], Levels[6][5])),
        ((60, 90), (Levels[6][5], Levels[6][6])),
        ((95, 130), (Levels[6][6], Levels[6][7])),
        ((140, 170), (Levels[6][7], MaxSkill)),
    ),
    # Drop
    (
        ((10, 12), (Levels[7][0], Levels[7][1])),
        ((15, 20), (Levels[7][1], Levels[7][2])),
        ((30, 35), (Levels[7][2], Levels[7][3])),
        ((45, 56), (Levels[7][3], Levels[7][4])),
        ((75, 90), (Levels[7][4], Levels[7][5])),
        ((105, 140), (Levels[7][5], Levels[7][6])),
        ((165, 200), (Levels[7][6], Levels[7][7])),
        ((220, 250), (Levels[7][7], MaxSkill)),
    ),
)

# avatar prop target type (0 for single target, 1 for group target)
# AvPropTargetCat is a grouping of target types for a single track and AvPropTarget is which target type group from
# AvPropTargetCat each toon attack track uses
ATK_SINGLE_TARGET = 0
ATK_GROUP_TARGET = 1

AvPropTargetCat = (
    (
        ATK_SINGLE_TARGET,
        ATK_GROUP_TARGET,
        ATK_SINGLE_TARGET,
        ATK_GROUP_TARGET,
        ATK_SINGLE_TARGET,
        ATK_GROUP_TARGET,
        ATK_SINGLE_TARGET,
        ATK_GROUP_TARGET,
    ),
    (
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
    ),
    (
        ATK_GROUP_TARGET,
        ATK_GROUP_TARGET,
        ATK_GROUP_TARGET,
        ATK_GROUP_TARGET,
        ATK_GROUP_TARGET,
        ATK_GROUP_TARGET,
        ATK_GROUP_TARGET,
        ATK_GROUP_TARGET,
    ),
    (
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_SINGLE_TARGET,
        ATK_GROUP_TARGET,
    ),
)

AvPropTarget = (0, 1, 0, 2, 1, 1, 1, 1)

# Maximum allowed [suits] in battle. (for gui elements, movie camera shots)
MaxBattleAvatars = 6

# Values that are mainly relevant in the BattleCalculatorAI class.

# Amount of lure rounds per lure gag.
NumRoundsLured = [2, 2, 3, 3, 4, 4, 5, 5]

# Amount of soak rounds per squirt gag.
NumRoundsSoaked = [3, 3, 3, 3, 4, 4, 4, 4]

# Amount of bonus accuracy per gag.
AttackAccPerGagLvl = [0, 10, 20, 30, 40, 50, 60, 70]
# Amount of accuracy bonus given for each valid gag used.
AccuracyBonusIncrement = 20

# Drop prestige adds 15% to its base accuracy when solo.
DropBonusAccAmt = 15

# What % of the Toonup heal amt should the prestiged toonup user receive?
ToonupSelfHealAmt = [0.25, 0.4]
# What % of the Toonup heal amt should remain if it misses?
ToonupMissAmt = 0.4

# Should Lure Decay be enabled? (Diminishing accuracy the longer a lure lasts)
WantLureDecay = False

# Drop has a unique combo damage multiplier.
DropHpBonus = 0.30

DropPrestigeStartAmt = 1.05  # How much drop's prestige dmg boost will start out at, if there's any debuffs
DropPrestigeAmt = 0.05  # How much to boost by per debuff

# Debuffs to ignore when looking to apply prestige bonus.
DropPrestigeBlacklist = (
    SEE.EFFECT_SUIT_TRAPPED,
)

# Drop prestige adds 10% combo damage per prestige drop used.
DropBonusComboAmt = 10

# Soak increases incoming accuracy by 10%.
SoakDefBonusAmt = -10

# Lure gains +20% accuracy if any of its targets are trapped
LureTrappedSuitBonus = 20

# Drench decreases Suit defense by 20%.
DrenchDefBonusAmt = -20

# Frozen decreases Suit defense by 25%.
FrozenDefBonusAmt = -25

# Splash damage from Squirt Gags varies based on prestige.
SplashDamageAmt = [0.25, 0.50]

# The length of the target list needed for Zap.
ZapTargetsWanted = 3

# Amount of inactive rounds required for Suits to unsue.
NumRoundsCeaseDesist = 4
NumRoundsCeaseDesistCap = 5

# % of suit's level required to sue a suit.
SueCostPercent = 0.25
# % of suit's level required to fire a suit.
FireCostPercent = 0.33

# Bonus trap damage against executive cogs
TrapEliteBonus = 1.3
# Prestige trap bonus damage
TrapHealthyBonus = 1.2
# How much health a cog must have to receive the healthy bonus
TrapHealthyBonusHPThreshold = 0.5

# Gag's accuracy base while a suit is Lured.
# Starts at 105 so that gag's have 100% accuracy for the turn after lure is used
LureAccuracy = 105

# Prestige lure multipliers
LurePrestigeSingleBonus = 0.15
LurePrestigeGroupBonus = 0.25

# Throw's MFL status effect definitions and pres's self-heal multiplier
ThrowMarkPercent = 1.10
ThrowPresHealPercent = 0.20

# Sound's Encore damage multiplier for unpres and pres respectively
SoundAtkBonus = (1.08, 1.16)

# Do we want interactive prop buffs? (Street Props offering prestige gags)
WantInteractivePropBuffs = False


def calculateAccuracyString(accuracy, track):
    if track == AttackEnum.TOON_ZAP:
        return TTLocalizer.BattleGlobalAccuracyIfSoaked

    if accuracy >= 100:
        return TTLocalizer.BattleGlobalAccuracyPerfect
    elif accuracy >= 90:
        return TTLocalizer.BattleGlobalAccuracyHigh
    elif accuracy >= 70:
        return TTLocalizer.BattleGlobalAccuracyMedium
    elif accuracy >= 50:
        return TTLocalizer.BattleGlobalAccuracyLow
    elif accuracy > 0:
        return TTLocalizer.BattleGlobalAccuracyAwful
    else:
        return TTLocalizer.BattleGlobalAccuracyNever


def getAvPropDamage(attackTrack, attackLevel, exp, organicBonus=False, propBonus=False, propAndOrganicBonusStack=False, targetList=[], suitId=None, allSuits=None):
    """
    Get the appropriate prop damage based on various attributes of the prop and the toon

    :param attackTrack: the track of the prop
    :param attackLevel: the level of the prop
    :param exp: the toon's exp in the specified track
    """
    # Map a damage value for the prop based on the track exp of the toon.
    # For example, a throw might have 3-6 damage which maps to 0-30 exp.
    # So at 0 to 7.75 exp, the throw will do 3 damage; at 7.75 to 15.5 exp, the throw will do 4 damage;
    # at 15.5 to 23.25, the throw will do 5 damage; at 23.25 to 30 exp, the throw will do 6 damage;
    # at more than 30 exp, the throw will max out at 6 damage
    minD = AvPropDamage[attackTrack][attackLevel][0][0]
    maxD = AvPropDamage[attackTrack][attackLevel][0][1]
    minE = AvPropDamage[attackTrack][attackLevel][1][0]
    maxE = AvPropDamage[attackTrack][attackLevel][1][1]
    expVal = min(exp, maxE)
    expPerHp = float(maxE - minE + 1) / float(maxD - minD + 1)
    damage = math.floor((expVal - minE) / expPerHp) + minD
    if damage <= 0:
        damage = minD
    if propAndOrganicBonusStack:
        originalDamage = damage
        if organicBonus:
            damage += getDamageBonus(originalDamage, attackLevel, attackTrack, targetList, suitId, allSuits)
        if propBonus:
            damage += getDamageBonus(originalDamage, attackLevel, attackTrack, targetList, suitId, allSuits)
    elif organicBonus or propBonus:
        damage += getDamageBonus(damage, attackLevel, attackTrack, targetList, suitId, allSuits)
    return damage


def getZapJumpDamage(damage, prestige: bool=False):
    """Specialized jump damage depending on prestige. 
    (addition is used to avoid floating point imprecision)
    """
    return math.ceil(damage + damage * (0.1 if prestige else -0.1))


def getDamageBonus(normal, level, track=4, targetList=[], suitId=None, allSuits=None):
    if track == AttackEnum.TOON_TRAP:
        bonus = math.ceil(normal * 0.2)
    elif track == AttackEnum.TOON_LURE:
        if attackAffectsGroup(track, level):
            bonus = math.ceil(normal * LurePrestigeGroupBonus)
        else:
            bonus = math.ceil(normal * LurePrestigeSingleBonus)
    else:
        bonus = 0
    return bonus


def isGroup(track, level):
    return AvPropTargetCat[AvPropTarget[track]][level]


def getCreditMultiplier(floorIndex):
    """
    :param int floorIndex: 0 for the first floor, up through 4 for the top floor of a five-story building.
    :returns: the skill credit multiplier appropriate for a particular floor in a building battle.
    """
    # Currently, this is 1 for the first floor (floor 0), 1.5 for the second floor (floor 1), etc.
    return 1 + floorIndex * 0.5


def getBuildingCreditMultiplier(floorCount):
    return 1 + floorCount


def getFactoryCreditMultiplier(factoryId):
    """
    :param int factoryId: The factory-interior zone defined in ToontownGlobals.py.
    :returns: the skill credit multiplier for a particular factory.
    """
    # for now, there's only one factory
    return 4.0


def getFactoryMeritMultiplier(factoryId):
    """
    :returns: the skill merit multiplier for a particular factory.
    :param int factoryId: the factory-interior zone defined in ToontownGlobals.py.
    """
    # Many people complained about how many runs you must make now that
    # we lowered the cog levels so I have upped this by a factor of two.
    return 4.0


def getMintCreditMultiplier(mintId):
    """
    :param int mintId: the mint-interior zone defined in ToontownGlobals.py.
    :returns: the skill credit multiplier for a particular mint.
    """
    return {
        CashbotMintIntA: 4.0,
        CashbotMintIntB: 5.0,
        CashbotMintIntC: 6.0
    }.get(mintId, 2.0)


def getStageCreditMultiplier(stageId):
    """
    :param int stageId: the stage-interior zone defined in ToontownGlobals.py.
    :returns: the skill credit multiplier for a particular mint.
    """
    return {
        LawbotStageIntA: 4.0,
        LawbotStageIntB: 5.0,
        LawbotStageIntC: 6.0
    }.get(stageId, 2.0)


def getCountryClubCreditMultiplier(countryClubId):
    """
    :param int mintId: the mint-interior zone defined in ToontownGlobals.py.
    :returns: the skill credit multiplier for a particular mint.
    """
    return {
        BossbotCountryClubIntA: 4.0,
        BossbotCountryClubIntB: 5.0,
        BossbotCountryClubIntC: 6.0,
    }.get(countryClubId, 2.0)


def getBossBattleCreditMultiplier(battleNumber):
    """
    :param int battleNumber: 1 for the first battle and 2 for the second battle.
    :returns: the skill credit multiplier for the two first battles of the final battle sequence with the Senior V.P.
    """
    return 1


def getInvasionMultiplier():
    """
    This gets multiplied on every street battle and in every interior.
    User must first check to see if there is an invasion.

    :returns: the skill credit multiplier during invasions. (base = 2.0)
    """
    return 2.0


def getMegaMultiplier():
    """
    :return: 3.0
    """
    return 3.0


def getMoreXpHolidayMultiplier():
    """
    This gets multiplied on every street battle and in every interior.
    User must first check to see if there is an invasion.

    :returns: the skill credit multiplier during the more xp holiday. (base = 2.0)
    """
    return 2.0


def getCogHQMultiplier():
    """
    :return: 2.0
    """
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
    foundOne = 0
    while not foundOne:
        if trackList[endList - 1] == 0:
            trackList.pop(endList - 1)
            endList -= 1
        else:
            foundOne = 1
    return trackList


def getUberFlag(flagMask, index):
    decode = decodeUber(flagMask)
    if index >= len(decode):
        return 0
    else:
        return decode[index]


def getUberFlagSafe(flagMask, index):
    if flagMask == "unknown" or flagMask < 0:
        return -1
    else:
        return getUberFlag(flagMask, index)


def getFancyTrackText(track: AttackEnum) -> str:
    return {
        AttackEnum.TOON_HEAL: "\1GagTrack_toon-up\1Toon-Up\2",
        AttackEnum.TOON_TRAP: "\1GagTrack_trap\1Trap\2",
        AttackEnum.TOON_LURE: "\1GagTrack_lure\1Lure\2",
        AttackEnum.TOON_SOUND: "\1GagTrack_sound\1Sound\2",
        AttackEnum.TOON_SQUIRT: "\1GagTrack_squirt\1Squirt\2",
        AttackEnum.TOON_ZAP: "\1GagTrack_zap\1Zap\2",
        AttackEnum.TOON_THROW: "\1GagTrack_throw\1Throw\2",
        AttackEnum.TOON_DROP: "\1GagTrack_drop\1Drop\2",
    }.get(track, "Unknown Track!")


def getCounterfeitCooldownsForMaxLevel(maxLevel: int):
    baseCd = 3 if maxLevel == 7 else 2
    return {maxLevel: baseCd, maxLevel-1: baseCd-1, maxLevel-2: (baseCd-2) if maxLevel == 7 else (baseCd-1)}


def getSurrenderVotes(numToons: int) -> int:
    # If the group has 4 or fewer toons, all must surrender.
    # If the group has 5 or more toons, all except one must surrender.
    return numToons if numToons <= 4 else numToons - 1


# Sent when an avatar is being targeted by a damaging attack
BattleAvatarTargetedMessage = 'Battle-AvatarTargeted'
