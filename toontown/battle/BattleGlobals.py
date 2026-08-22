from enum import IntEnum

class BattleStateEnum(IntEnum):
 INACTIVE = 1
 JOINING = 2
 JOINING_NOT_PENDING = 3
 PENDING = 4
 ACTIVE = 5
 RUNNING = 6

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
NumRoundsLured = [1,
 1,
 2,
 2,
 3,
 3,
 4,
    4]
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