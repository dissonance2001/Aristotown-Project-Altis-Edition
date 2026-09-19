"""
BossCogGlobals: defines constants that are global across boss cogs, and
may have meaning to several classes.
"""

from panda3d.core import *

# region Attacks

# Boss Cog movement constants
BossCogRollSpeed      = 7.5
BossCogTurnSpeed      = 20
BossCogTreadSpeed     = 3.5

# Boss Cog attack codes:
BossCogDizzy                  = 0
BossCogElectricFence          = 1
BossCogSwatLeft               = 2
BossCogSwatRight              = 3
BossCogAreaAttack             = 4
BossCogFrontAttack            = 5
BossCogRecoverDizzyAttack     = 6
BossCogDirectedAttack         = 7
BossCogStrafeAttack           = 8
BossCogNoAttack               = 9
BossCogGoonZap                = 10
BossCogSlowDirectedAttack     = 11
BossCogDizzyNow               = 12
BossCogGavelStomp             = 13
BossCogGavelHandle            = 14
BossCogLawyerAttack           = 15
BossCogMoveAttack             = 16
BossCogGolfAttack             = 17
BossCogGolfAreaAttack         = 18
BossCogGearDirectedAttack     = 19
BossCogOvertimeAttack         = 20

# Boss cog codes specific to the Lawbot boss:
BossCogFourWayTornadoAreaAttack   = 21
BossCogBookDirectedAttack         = 22
BossCogPaperFrontAttack           = 23
BossCogEightWayTornadoAreaAttack  = 24
BossCogSpiralTornadoAreaAttack    = 25
BossCogDocketAoeAttack            = 26
BossCogSpreadBookDirectedAttack   = 27

BossCogSlowCoinDirectedAttack     = 28

# The amount of time it takes to play each attack.
BossCogAttackTimes = {
    BossCogElectricFence: 0,
    BossCogSwatLeft: 5.5,
    BossCogSwatRight: 5.5,
    BossCogAreaAttack: 4.21,
    BossCogFrontAttack: 2.65,
    BossCogRecoverDizzyAttack: 5.1,
    BossCogDirectedAttack: 4.84,
    BossCogNoAttack: 6,
    BossCogSlowDirectedAttack: 7.84,
    BossCogMoveAttack: 3,
    BossCogGolfAttack: 6,
    BossCogGolfAreaAttack: 7,
    BossCogGearDirectedAttack: 4.84,
    BossCogOvertimeAttack: 5,
    BossCogFourWayTornadoAreaAttack: 3,
    BossCogEightWayTornadoAreaAttack: 3,
    BossCogSpiralTornadoAreaAttack: 3,
    BossCogBookDirectedAttack: 4.84,
    BossCogPaperFrontAttack: 2.65,
    BossCogSpreadBookDirectedAttack: 4.84,
    BossCogSlowCoinDirectedAttack: 7.84,
}

# The damage that each attack applies to a Toon.
BossCogDamageLevels = {
    BossCogElectricFence: 2,
    BossCogSwatLeft: 8,
    BossCogSwatRight: 8,
    BossCogAreaAttack: 13,
    BossCogFrontAttack: 5,
    BossCogRecoverDizzyAttack: 5,
    BossCogDirectedAttack: 5,
    BossCogStrafeAttack: 3,
    BossCogGoonZap: 8,
    BossCogSlowDirectedAttack: 15,
    BossCogGavelStomp: 38,
    BossCogGavelHandle: 3,
    BossCogLawyerAttack: 11,
    BossCogMoveAttack: 20,
    BossCogGolfAttack: 15,
    BossCogGolfAreaAttack: 15,
    BossCogGearDirectedAttack: 15,
    BossCogOvertimeAttack: 10,
    BossCogFourWayTornadoAreaAttack: 18,
    BossCogEightWayTornadoAreaAttack: 18,
    BossCogSpiralTornadoAreaAttack: 18,
    BossCogBookDirectedAttack: 11,
    BossCogPaperFrontAttack: 11,
    BossCogDocketAoeAttack: 25,
    BossCogSpreadBookDirectedAttack: 14,
    BossCogSlowCoinDirectedAttack: 15,
}

BossCogDizzyStates = [
    BossCogDizzy,
    BossCogDizzyNow,
]

NonBossCogAttacks = [
    BossCogGoonZap,
    BossCogGavelStomp,
    BossCogGavelHandle,
    BossCogLawyerAttack,
    BossCogElectricFence,
    BossCogFourWayTornadoAreaAttack,
    BossCogEightWayTornadoAreaAttack,
    BossCogSpiralTornadoAreaAttack,
    BossCogDocketAoeAttack,
]

# endregion

# Where are the Boss Cog's battles relative to them?
BossCogBattleAPosHpr = (0, -25, 0, 0, 0, 0)
BossCogBattleBPosHpr = (0, 25, 0, 180, 0, 0)

# region SellbotBoss

# How many pie hits does it take to kill the Sellbot VP?
SellbotBossMaxDamage = 1000

# How much damage should a pie do to the Sellbot VP?
SellbotBossPieDamage = 10

# Where is the Sellbot Boss sitting in the three stages of the VP sequence?
SellbotBossBattleOnePosHpr = (0, -35, 0, -90, 0, 0)
SellbotBossBattleTwoPosHpr = (0, 60, 18, -90, 0, 0)
SellbotBossBattleThreeHpr = (180, 0, 0)
SellbotBossBottomPos = (0, -110, -6.5)
SellbotBossDeathPos = (0, -175, -6.5)

# Where do the VP's doobers walk to?
SellbotBossDooberTurnPosA = (-20, -50, 0)
SellbotBossDooberTurnPosB = (20, -50, 0)
SellbotBossDooberTurnPosDown = (0, -50, 0)
SellbotBossDooberFlyPos = (0, -135, -6.5)

# How does the VP roll up the ramp?
SellbotBossTopRampPosA = (-80, -35, 18)
SellbotBossTopRampTurnPosA = (-80, 10, 18)
SellbotBossP3PosA = (-50, 40, 18)
SellbotBossTopRampPosB = (80, -35, 18)
SellbotBossTopRampTurnPosB = (80, 10, 18)
SellbotBossP3PosB = (50, 60, 18)

# endregion
# region CashbotBoss

# How many points does it take to kill the Cashbot CFO?
CashbotBossMaxDamage = [500, 1000, 1500]

# Where is the Cashbot Boss sitting in the CFO sequence?
CashbotBossOffstagePosHpr = (120, -190, 0, 0, 0, 0)
CashbotBossBattleOnePosHpr = (120, -230, 0, 90, 0, 0)
CashbotBossBattleTwoPosHpr = (120, -315, 0, 180, 0, 0)
CashbotRTBattleOneStartPosHpr = (94, -220, 0, 110, 0, 0)
CashbotRTBattleTwoStartPosHpr = (120, -260, 0.025, 0, 0, 0)
CashbotRTBattleTwoEndPosHpr = (120, -290, 0.025, 0, 0, 0)
CashbotBossBattleThreePosHpr = (120, -315, 0, 180, 0, 0)
CashbotBossBattleFleePosHpr = (120, -315, 0, 0, 0, 0)

# Where are the starting points for the toons in battle 3?
CashbotToonsBattleThreeStartPosHpr = [
    (105, -285, 0, 208, 0, 0),
    (136, -342, 0, 398, 0, 0),
    (105, -342, 0, 333, 0, 0),
    (135, -292, 0, 146, 0, 0),
    (93, -303, 0, 242, 0, 0),
    (144, -327, 0, 64, 0, 0),
    (145, -302, 0, 117, 0, 0),
    (93, -327, 0, -65, 0, 0),
]

# How many safes in the final battle sequence, and where are they?
CashbotBossSafePosHprs = [
    (120, -315, 30, 0, 0, 0),  # safe 0 is special; it drops on from above.
    (77.2, -329.3, 0, -90, 0, 0),
    (77.1, -302.7, 0, -90, 0, 0),
    (165.7, -326.4, 0, 90, 0, 0),
    (165.5, -302.4, 0, 90, 0, 0),
    (107.8, -359.1, 0, 0, 0, 0),
    (133.9, -359.1, 0, 0, 0, 0),
    (107.0, -274.7, 0, 180, 0, 0),
    (134.2, -274.7, 0, 180, 0, 0),
]

# How many cranes, and where are they?
CashbotBossCranePosHprs = [
    (97.4, -337.6, 0, -45, 0, 0),
    (97.4, -292.4, 0, -135, 0, 0),
    (142.6, -292.4, 0, 135, 0, 0),
    (142.6, -337.6, 0, 45, 0, 0),
    # Side cranes
    (81, -315, 0, -90, 0, 0),
    (160, -315, 0, 90, 0, 0),
]

# Differentiates normal and side cranes.
CashbotBossCraneTypeNormal = 0
CashbotBossCraneTypeFast = 1

# How long does it take an object to fly from the ground to the magnet?
CashbotBossToMagnetTime = 0.2

# And how long to straighten out when dropped?
CashbotBossFromMagnetTime = 1

# How much impact does it take to hit the Cashbot boss with an object?
CashbotBossSafeKnockImpact = 0.3
CashbotBossSafeNewImpact = 0.0
CashbotBossGoonImpact = 0.1
CashbotBossKnockoutDamage = 12

# How long in-between can an object deal damage to the CFO?
CashbotBossObjectDebounce = 0.5

# endregion
# region LawbotBoss + HardmodeLawbotBoss

# How many points does it take to kill the Lawbot Boss?
LawbotBossMaxDamage = [1000, 1250, 1500]

# How high of a damage multiplier does the Lawbot boss have?
LawbotBossDamageMultipliers = (1.0, 1.15, 1.3)

# How much knockback does sound deal?
# This is based on the amount of toons present
LawbotBossSoundKnockback = {1: 4.0, 2: 3.5, 3: 3.25, 4: 3.0, 5: 3.0, 6: 2.75, 7: 2.75, 8: 2.5}

# This is the amount of damage sound gags deal in the lawbot boss.
LawbotBossSoundDamage = {2: 15, 3: 20, 4: 25, 5: 35, 6: 50}

# How fast does the Lawbot Boss move?
LawbotBossRollSpeedMax = 18
LawbotBossRollSpeedMin = 7.5
LawbotBossTurnSpeedMax = 50
LawbotBossTurnSpeedMin = 20

# How much evidence do you need for each sound tier?
LawbotBossSoundEvidenceRequirement = {'bugle': 0, 'aoogah': 40, 'trunk': 75, 'fog': 110, 'max': 120}
# For hardmode?
HardmodeLawbotBossSoundEvidenceRequirement = {'bugle': 0, 'aoogah': 50, 'trunk': 90, 'fog': 140, 'max': 160}

# Where is the Lawbot Boss sitting in the four stages of the CLO sequence?
LawbotBossBattleOnePosHpr = (0, 385, -71.601, 0, 0, 0)
LawbotBossBattleTablePosHpr = (0, 291, -71.601, 0, 0, 0)
LawbotBossBattleBackFromTablePosHpr = (0, 306, -71.601, 0, 0, 0)
LawbotBossBattleFallPosHpr = (0, 220, -71.601, 0, 0, 0)
LawbotBossBattleFallMiddlePos = Vec3(0, 183.25, -71.601)
LawbotBossBattleFallFinalPos = Vec3(0, 146.5, -71.601)

LawbotBossBattleFallXMin = -100
LawbotBossBattleFallXMax = 100
LawbotBossBattleFallYMin = 140
LawbotBossBattleFallYMax = 280

# Where are the executive doobers on the table sitting?
LawbotBossExecutivePositions = (
    (-15.0082, 173.199, -67.576, -90, 0, 0),
    (9.1846, 216.485, -67.826, 90, 0, 0),
    (-12.1846, 194.485, -67.326, -90, 0, 0),
    (-8.3096, 238.485, -67.326, -90, 0, 0),
    (-9.6846, 216.735, -67.326, -90, 0, 0),
    (8.9346, 238.485, -67.326, 90, 0, 0),
    (12.9346, 194.485, -67.826, 90, 0, 0),
    (12.9346, 173.235, -67.826, 90, 0, 0),
)

# Where is the Litigation Team sitting during the HM CLO Cutscene?
HardmodeLawbotBossLitigationPositions = (
    (-8.3096, 238.485, -68.326, -90, 0, 0),
    (-9.1846, 216.735, -68.326, -90, 0, 0),
    (8.3096, 238.485, -68.326, 90, 0, 0),
    (9.1846, 216.485, -68.326, 90, 0, 0),
)
HardmodeLawbotBossScapegoatZOffset = 0.6

# What levels are the Litigation Team members?
HardmodeLawbotBossLitigationLevels = {
    'stenog': 35,
    'sgoat': 30,
    'lgator': 40,
    'caseman': 35
}

# What's the odds that we actually use our docket?
HardmodeLawbotBossDocketChance = 0.25

HardmodeLawbotBossAttackCogSpeed = 9.6

# How long in seconds between we try to docket the player?
HardmodeLawbotBossAttackCogDocketCooldown = 9

# How many seconds before the docket damages toons in its radius?
HardmodeLawbotBossDocketDelay = 1

# How often (in seconds) should an Executive cog spawn during the sound round?
HardmodeLawbotBossExecutiveSpawnCooldown = 30

# Where are the Lawbot Boss battles located?
LawyerBattleAPosHpr = (-60, -85, 0, 90, 0, 0)
LawyerBattleBPosHpr = (60, -85, 0, -90, 0, 0)
HMLawyerBattleAPosHpr = (-60, -70, 0, 90, 0, 0)
HMLawyerBattleBPosHpr = (60, -70, 0, -90, 0, 0)
LawyerVirtualBattleAPosHpr = (20, -163.5, 0, 180, 0, 0)
LawyerVirtualBattleBPosHpr = (-20, -163.5, 0, 180, 0, 0)
LawyerVirtualBattleSpotlightPos = ((0, 35.25), (0, 35.25))
LawbotBossBattleTwoPosHpr = (0, 220, -71.601, 0, 0, 0)

LawbotBossPaintingOpenPositions = (
    (0, -8, 50),
    (0, -8, 50),
    (8, 0, 50),
    (-8, 0, 50),
    (8, 0, 50),
    (-8, 0, 50),
    (8, 0, 50),
    (-8, 0, 50),
    (0, 8, 50),
    (0, 8, 50),
)

# Position constants for the CLO
LawbotBossBattleThreePosHpr = LawbotBossBattleTwoPosHpr
LawbotBossDeathPos = (0, 295, -71.601)

# Where are Bumpy and Lauren during the introduction cutscene?
LawbotBossWitnessToonPosHpr = (25, 50, 0, 135, 0, 0)
LawbotBossLawyerToonPosHpr = (-25, 50, 0, -135, 0, 0)
HardmodeLawbotBossWitnessToonPosHpr = (4, 20, 0, 160, 0, 0)
HardmodeLawbotBossLawyerToonPosHpr = (-4, 20, 0, -160, 0, 0)

# Where are the Spotlights and Virtual Skelecogs during the HM CLO Intro?
# Note: Spotlight & Virtual 0 is the one that Lauren steps into.
HardmodeIntroductionSpotlightPos = (
    (-18, 20, -71.601),
    (-18, 30, -71.601),
    (18, 30, -71.601),
    (18, 20, -71.601),
    (18, 10, -71.601),
    (-18, 10, -71.601)
)
# Position, H
HardmodeIntroductionVirtualPos = (
    ((-18, 20, -66.601), -90),
    ((-18, 30, -66.601), -90),
    ((18, 30, -66.601), 90),
    ((18, 20, -66.601), 90),
    ((18, 10, -66.601), 90),
    ((-18, 10, -66.601), -90)
)

# What path do the Toons exit the elevator on in the HM CLO Intro?
HardmodeIntroductionToonsAPath = (
    (4, 8, -71.601),
    (4, 16, -71.601),
    (4, 24, -71.601),
    (4, 32, -71.601)
)
HardmodeIntroductionToonsBPath = (
    (-4, 8, -71.601),
    (-4, 16, -71.601),
    (-4, 24, -71.601),
    (-4, 32, -71.601)
)

# Where should the Toons drop the cannons?
LawbotBossCannonPosHprs = (
    (-20, 115, -71.601, 0, 0, 0),
    (20, 115, -71.601, 0, 0, 0),
    (-100, 200, -71.601, -90, 0, 0),
    (100, 200, -71.601, 90, 0, 0),
    (-100, 240, -71.601, -90, 0, 0),
    (100, 240, -71.601, 90, 0, 0),
    (-20, 325, -71.601, 180, 0, 0),
    (20, 325, -71.601, 180, 0, 0),
)

# Where are the gavels located?
LawbotBossGavelPosHprs = (
    (-80, 135, -71.601, -45, 0, 0),
    (80, 135, -71.601, 45, 0, 0),
    (-80, 305, -71.601, -135, 0, 0),
    (80, 305, -71.601, 135, 0, 0),
)

# Where is the evidence box located?
LawbotBossEvidenceBoxPosHpr = (0, 69.5, 0, 180, 0, 0)
LawbotBossEvidenceBoxPos = (0, 69.5, 0)

# Where do the flying cogs spawn?
LawbotBossLawyerPosHprs = {
    -2: (65, 80, 5, 0, 0, 0),  # Bottom right virtual
    -1: (-65, 80, 5, 0, 0, 0),  # Bottom left virtual
    0: (65, 80, 5, 0, 0, 0),  # Bottom right
    1: (-65, 80, 5, 0, 0, 0),  # Bottom left
    2: (135, 120, 5, 90, 0, 0),  # Bottom right
    3: (-135, 120, 5, -90, 0, 0),  # Bottom left
    4: (135, 223, 5, 90, 0, 0),  # Middle right skelecog
    5: (-135, 223, 5, -90, 0, 0),  # Middle left skelecog
    6: (135, 323, 5, 90, 0, 0),  # Top far right
    7: (-135, 323, 5, -90, 0, 0),  # Top far left
    8: (65, 360, 5, 180, 0, 0),  # Top right
    9: (-65, 360, 5, 180, 0, 0),  # Top left
}

# Where do the defense specialists spawn? (Hardmode)
LawbotBossDefenseSpawnDistance = 8
LawbotBossDefenseSpecialistPos = (
    (LawbotBossDefenseSpawnDistance, LawbotBossDefenseSpawnDistance, 0, -45, 0, 0),
    (-LawbotBossDefenseSpawnDistance, LawbotBossDefenseSpawnDistance, 0, 45, 0, 0),
    (-LawbotBossDefenseSpawnDistance, -LawbotBossDefenseSpawnDistance, 0, 135, 0, 0),
    (LawbotBossDefenseSpawnDistance, -LawbotBossDefenseSpawnDistance, 0, -135, 0, 0)
)

# Defense Specialists will spawn once for each health threshold crossed.
# First threshold is always 1.0 purely for logic purposes, doesn't trigger the defense spawning
# Special exception for the last threshold, where they will always spawn below that threshold
LawbotBossDefenseThresholds = (1.0, 0.9, 0.75, 0.6, 0.45, 0.3, 0.2)

# Health values for the Defense Specialists in Overclocked CLO's Sound Round
# Base (4 Toons), Scaling Per Toon past 4
LawbotBossDefenseHealth = {
    'pf': (250, 20),
    'cv': (425, 30),
    'ad': (600, 40)
}
LawbotBossHardDefenseHealth = {
    'pf': (450, 25),
    'cv': (675, 40),
    'ad': (900, 50)
}

# How much to scale Defense Specialist health by when they get hit by a Prestige Trapdoor
# Scaling: 1.0 (unpres quicksand) -> 1.25 (pres trapdoor)
LawbotBossDefenseHealthScaling = 1.25

# The flying cogs will fly to these positions first.
LawbotBossLawyerFirstPos = {
    -2: (20, 92, -58),  # Bottom right virtual
    -1: (-20, 92, -58),  # Bottom left virtual
    0: (65, 105, -45),  # Bottom right
    1: (-65, 105, -45),  # Bottom left
    2: (105, 120, -45),  # Bottom right
    3: (-105, 120, -45),  # Bottom left
    4: (105, 223, -45),  # Middle right skelecog
    5: (-105, 223, -45),  # Middle left skelecog
    6: (105, 323, -45),  # Top far right
    7: (-105, 323, -45),  # Top far left
    8: (65, 330, -45),  # Top right
    9: (-65, 330, -45),  # Top left
}

# Position bounds for treasures dropped by flying cogs.
LawbotBossTreasureBounds = ((-110, 110), (105, 335))

# Position bounds for toons in cannons.
LawbotBossCannonBounds = ((-105, 105), (100, 340))

# How long does the evidence round last?
LawbotBossEvidenceRoundTime = 120

# What height do the flying cogs fly at?
LawbotBossLawyerNormalZPos = -53
LawbotBossLawyerVirtualZPos = -58

# How soon should the flying cogs start moving randomly after doing their initial move?
LawbotBossLawyerInitialDelay = 2
LawbotBossLawyerVirtualInitialDelay = 0.1

# These values are used by DistributedWinterMinigameSuit.
LawbotBossLawyerToPanTime = 2.5
LawbotBossLawyerChanceToAttack = 50
LawbotBossLawyerHeal = 2

# Where does Mr. Bumpy start at?
LawbotBossBumpyPosHpr = (0, 120, -71.601, 0, 0, 0)

# These are the positions Mr. Bumpy will go to when he places the traps.
LawbotBossBumpyTrapsPos = (
    # Trapdoor
    (0, 120, -71.601),
    # Quicksand
    (60, 130, -71.601),  # Bottom right corner
    (-60, 130, -71.601),  # Bottom left corner
    (80, 290, -71.601),  # Top right corner
    (-80, 290, -71.601),  # Top left corner
    (-70, 223, -71.601),  # Middle left
    (70, 223, -71.601),  # Middle Right
    (0, 182.5, -71.601),  # Bottom middle (middle trapdoor)
    (0, 257.5, -71.601),  # Top middle (middle trapdoor)
)

LawbotBossTrapdoorsList = (0,)

# This is where Mr. Bumpy chills out when he doesn't have any work to do.
LawbotBossBumpyIdlePosHpr = (5, 82.5, -71.601, 0, 0, 0)

# This is where Ms. Lauren chills out when she doesn't have any work to do.
LawbotBossLaurenIdlePosHpr = (-5, 82.5, -71.601, 0, 0, 0)

# The traps will be placed at these positions with these rotations.
LawbotBossTrapsPosHpr = (
    # Trapdoor
    (0, 100, -71.601, 180, 0, 0),  # By Evidence Box
    # Quicksand
    (80, 130, -71.601, 315, 0, 0),  # Bottom right corner
    (-80, 130, -71.601, 225, 0, 0),  # Bottom left corner
    (80, 310, -71.601, 45, 0, 0),  # Top right corner
    (-80, 310, -71.601, 135, 0, 0),  # Top left corner
    (-90, 223, -71.601, 90, 0, 0),  # Middle left
    (90, 223, -71.601, -90, 0, 0),  # Middle Right
    (0, 167.5, -71.601, 180, 0, 0),  # Bottom middle (middle trapdoor)
    (0, 272.5, -71.601, 0, 0, 0)  # Top middle (middle trapdoor)
)

# This is how big the traps are.
LawbotBossTrapScale = (13, 13, 1)

# This is the amount of damage that the traps deal.
LawbotBossTrapsDamage = {4: 115, 5: 160}

# This is the amount of damage a prestiged trap deals.
LawbotBossPrestigedTrapsDamage = {4: 150, 5: 210}

# These are the delays for traps.
LawbotBossTrapEnableT = 2.5
LawbotBossTrapActivateT = 3.2
LawbotBossTrapBreakT = 8
LawbotBossTrapRepairT = 10
LawbotBossTrapInterruptBreakT = 2
LawbotBossTrapLandBrokenT = 1.25
LawbotBossTrapPrestigeT = 10

# These are the values for the tornaga attack.
LawbotBossTornadoPosTravel = 80
LawbotBossTornadoTravelDistance = 113
LawbotBossTornadoPosZ = -5
LawbotBossTornadoWobble = (0, 16, 0)
LawbotBossTornadoIndex2PosTravel = {
    0: (LawbotBossTornadoPosTravel, LawbotBossTornadoPosTravel, LawbotBossTornadoPosZ),
    1: (-LawbotBossTornadoPosTravel, LawbotBossTornadoPosTravel, LawbotBossTornadoPosZ),
    2: (LawbotBossTornadoPosTravel, -LawbotBossTornadoPosTravel, LawbotBossTornadoPosZ),
    3: (-LawbotBossTornadoPosTravel, -LawbotBossTornadoPosTravel, LawbotBossTornadoPosZ),
}

# These are the values for the eight way tornaga attack
LawbotBossEightWayTornadoIndex2PosTravel = {
    0: (LawbotBossTornadoPosTravel, LawbotBossTornadoPosTravel, LawbotBossTornadoPosZ),
    1: (-LawbotBossTornadoPosTravel, LawbotBossTornadoPosTravel, LawbotBossTornadoPosZ),
    2: (LawbotBossTornadoPosTravel, -LawbotBossTornadoPosTravel, LawbotBossTornadoPosZ),
    3: (-LawbotBossTornadoPosTravel, -LawbotBossTornadoPosTravel, LawbotBossTornadoPosZ),
    4: (-LawbotBossTornadoTravelDistance, 0, LawbotBossTornadoPosZ),
    5: (LawbotBossTornadoTravelDistance, 0, LawbotBossTornadoPosZ),
    6: (0, -LawbotBossTornadoTravelDistance, LawbotBossTornadoPosZ),
    7: (0, LawbotBossTornadoTravelDistance, LawbotBossTornadoPosZ),
}

# These are the values for the spiral tornaga attack
LawbotBossSpiralTornadoIndex2PosTravel = {
    0: (-LawbotBossTornadoTravelDistance / 1.5, 0, LawbotBossTornadoPosZ),
    1: (LawbotBossTornadoTravelDistance / 1.5, 0, LawbotBossTornadoPosZ),
    2: (0, -LawbotBossTornadoTravelDistance / 1.5, LawbotBossTornadoPosZ),
    3: (0, LawbotBossTornadoTravelDistance / 1.5, LawbotBossTornadoPosZ),
}

# First tuple is the total position, every tuple after is relative spotlight movement positions
LawbotBossSpotlightPosList = [
    [
        (-110, 95, -71.5),
        (70, 70),
        (80, 15),
        (0, 100),
        (35, 35),
        (35, 0),
        (0, 35),
        (70, 35),
        (35, 70),
        (40, 55),
    ],
    [
        (110, 95, -71.5),
        (-70, 70),
        (-80, 15),
        (0, 100),
        (-35, 35),
        (-35, 0),
        (0, 35),
        (-70, 35),
        (-35, 70),
        (-40, 55),
    ],
    [
        (-110, 345, -71.5),
        (70, -70),
        (80, -15),
        (0, -100),
        (35, -35),
        (35, 0),
        (0, -35),
        (70, -35),
        (35, -70),
        (40, -55),
    ],
    [
        (110, 345, -71.5),
        (-70, -70),
        (-80, -15),
        (0, -100),
        (-35, -35),
        (-35, 0),
        (0, -35),
        (-70, -35),
        (-35, -70),
        (-40, -55),
    ],
]

# Positions for the spotlights that track the virtual cogs.
LawbotBossTrackingSpotlightPosList = [[(20, 92, -71.5)], [(-20, 92, -71.5)]]

# Virtual cog spotlight specs.
LawbotBossSpotlightVelocity = (7, 8.5, 10)
LawbotBossSpotlightAccel = (1.75, 2.0, 2.25)
LawbotBossSpotlightDamage = 10

# This is where Bumpy will spawn where he sends you off.
LawbotBossWitnessEpiloguePosHpr = (-2.798, 223, -71.601, 0, 0, 0)

# Hardmode specific Lawbot Boss constants.

HardmodeLawyerVirtualBattleAPosHpr = (35, -261, 0, -90, 0, 0)
HardmodeLawyerVirtualBattleBPosHpr = (-35, -261, 0, 90, 0, 0)
HardmodeLawyerVirtualBattleSpotlightPos = ((-10, 0), (-10, 0))
HardmodeLawyerVirtualBattleCameraPos = [[(41, 34, -71.601)], [(-41, 34, -71.601)]]

# Enums for different types of lawbot boss suits in HM
LawbotBossSuitNormal  = 0
LawbotBossSuitAttack  = 1
LawbotBossSuitDefense = 2

# endregion
# region BossbotBoss

# CEO Battle stuff
BossbotRTIntroStartPosHpr = (0, -64, 0, 180, 0, 0)
BossbotRTPreTwoPosHpr = (0, -20, 0, 180, 0, 0)
BossbotRTEpiloguePosHpr = (0, 90, 0, 180, 0, 0)
BossbotBossBattleOnePosHpr = (0, 355, 0, 0, 0, 0)
BossbotBossPreTwoPosHpr = (0, 20, 0, 0, 0, 0)
BossbotElevCamPosHpr = (0, -100.544, 7.18258, 0, 0, 0)
BossbotFoodModelScale = 0.75  # do we scale up or down from the cog food model
BossbotNumFoodToExplode = 2
BossbotBossServingDuration = 200
BossbotPrepareBattleThreeDuration = 20

# relative to bosscog coordinates for waiter battles
WaiterBattleAPosHpr = (20, -400, 0, 0, 0, 0)
WaiterBattleBPosHpr = (-20, -400, 0, 0, 0, 0)
BossbotBossBattleThreePosHpr = (0, 355, 0, 0, 0, 0)
DinerBattleAPosHpr = (20, -240, 0, 0, 0, 0)
DinerBattleBPosHpr = (-20, -240, 0, 0, 0, 0)
BossbotBossMaxDamage = [1800, 2400, 3000]
BossbotMaxSpeedDamage = 360
BossbotSpeedRecoverRate = 80  # in speed damage recovered per MINUTE
BossbotMaxStunChance = 0.85
BossbotStunSpeedRecover = 32
BossbotDesperationSpeedRecover = 100

# Num tables, Diners per table, Level of diners, Table unflatten time, Hungry duration, Eating duration
BossbotBossDifficultySettings = [13, 5, 14, 9, 22, 29]
BossbotRollSpeedMax  = 22
BossbotRollSpeedMin  = 7.5
BossbotTurnSpeedMax  = 60
BossbotTurnSpeedMin  = 20
BossbotTreadSpeedMax = 10.5
BossbotTreadSpeedMin = 3.5

# List of positions of the banquet tables in the CEO
# NOTE: these were grabbed from the CEO geometry
# model and aren't actually used to position them. (on the client)
BossbotTablePositions = {
    0: (-55.4409, 155.393, 0),
    1: (-0.973121, 155.403, 0),
    2: (57.0671, 155.399, 0),
    3: (-29.5998, 197.85, 0),
    4: (28.0149, 197.85, 0),
    5: (-56.6304, 238.538, 0),
    6: (-0.973121, 238.55, 0),
    7: (57.1147, 238.55, 0),
    8: (-31.2734, 281.368, 0),
    9: (26.4148, 281.383, 0),
    10: (-56.0499, 323.902, 0),
    11: (-0.970739, 323.902, 0),
    12: (56.4156, 323.902, 0),
}

# How likely is a table to contain executive cogs?
# Maps the table index to the chance.
BossbotTableEXEChances = {
    0: 0,
    1: 0,
    2: 0,
    3: 0.25,
    4: 0.25,
    5: 0.5,
    6: 0.5,
    7: 0.5,
    8: 0.75,
    9: 0.75,
    10: 1,
    11: 1,
    12: 1,
}

# endregion
