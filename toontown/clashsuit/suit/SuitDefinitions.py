from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.inventory.enums.ItemEnums import ChatStickersItemType, BackgroundItemType, NameplateItemType,\
    ClothingTopItemType, ClothingBottomItemType, HatItemType, BackpackItemType, NeckItemType, GlassesItemType, ShoeItemType, \
    MaterialItemType
from toontown.suit.SuitDefinitionsBase import *
from toontown.battle.statuses import SEE
from toontown.battle.BattleBase import *
from toontown.battle.PassiveAttributeDefs import *
from toontown.toonbase.ToontownGlobals import CogBountyTypes, HALLOWEEN_MIX_WINTER_HOLIDAY, HALLOWEEN, APRIL_FOOLS
from toontown.loot.LootTable import *
from toontown.loot.lootTypes import *
from toontown.instances.mercs.InstanceMercGlobals import MercLootBaseChance, MercLootPity, MercLootLegendaryChance, \
    MercLootLegendaryPity, MercLootCommonChance, MercLootCommonPity
from toontown.utils import ColorHelper

# from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

"""
A file to entirely define a Suit's characteristics.
This contains all suit's localization,
battle globals,
random characteristics,
etc etc. Everything suit-related is defined here.

Define a suit as below.
You can view the SuitDefinition class for all things that can be set.

To make sure your suit definition won't crash,
call the test() method on it after setting everything.
"""

# Figure out what Holiday IDs we want for the kudos manager's material drops
materialHolidayIds = [ToontownGlobals.HALLOWEEN, ToontownGlobals.HALLOWEEN_MIX_WINTER_HOLIDAY]
if ConfigVariableString('current-seasonal-holiday', 'None').getValue() == 'april-fools' and ConfigVariableBool('want-halloween-with-april-fools').getValue():
    materialHolidayIds.append(ToontownGlobals.APRIL_FOOLS)


# region test cog definition
__TEST_COG = SuitDefinition('test', BOARDBOT, 5.41, hideDepartment=True)
__TEST_COG.defineLevelRange(1, 9)
__TEST_COG.defineParts(4.0, VBase4(0.95, 0.95, 0.95, 1), ['phase_3.5/models/schoolhouse/dummy/ttcc_ene_dummy-zero'], [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BOW,
                       bodyTex='phase_3.5/maps/schoolhouse/dummy/ttcc_ene_suittex_djockey.png',
                       textureOverride='phase_3.5/maps/schoolhouse/dummy/ttcc_ene_djockey.png')
__TEST_COG.describeAttack(AttackEnum.POWER_TRIP, attack=1, accuracy=80, frequency=100)
__TEST_COG.setStreetAttributes(joinChanceOverride=100, battleCogCap=6)
__TEST_COG.setHpPerLevel({k: 30000 for k in range(11)})
__TEST_COG.test()
# endregion

### SELLBOTS ###
# region
__COLD_CALLER = SuitDefinition('cc', SELLBOT, 4.63, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=1)
__COLD_CALLER.defineLevelRange(1, 5)
__COLD_CALLER.defineParts(3.5, VBase4(0.075, 0.227, 0.871, 1.0), ['phase_9/models/char/suits/ttcc_ene_coldcaller'], [SKELE_HEAD_C], suitType=SUIT_C,
                          tieType=TIE_SKINNY, bodyTex=TEX_SALES)
__COLD_CALLER.describeAttack(AttackEnum.FREEZE_ASSETS, attack=(3, 4, 6, 8, 10), accuracy=50, frequency=(5, 25))
__COLD_CALLER.describeAttack(AttackEnum.POUND_KEY, attack=(2, 2, 3, 4, 5), accuracy=(75, 95), frequency=25)
__COLD_CALLER.describeAttack(AttackEnum.MUMBO_JUMBO, attack=(2, 3, 4, 6, 8), accuracy=(50, 70), frequency=25)
__COLD_CALLER.describeAttack(AttackEnum.HOT_AIR, attack=1, accuracy=90, frequency=(45, 25))
__COLD_CALLER.test()

__TELEMARKETER = SuitDefinition('tm', SELLBOT, 5.24, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=2)
__TELEMARKETER.defineLevelRange(2, 6)
__TELEMARKETER.defineParts(3.75, VBase4(0.92549, 0.803922, 0.756863, 1), ['phase_9/models/char/suits/ttcc_ene_telemarketer'], [SKELE_HEAD_B],
                           suitType=SUIT_B, tieType=TIE_SKINNY, bodyTex=TEX_SALES)
__TELEMARKETER.describeAttack(AttackEnum.CLIPON_TIE, attack=(2, 4), accuracy=75, frequency=15)
__TELEMARKETER.describeAttack(AttackEnum.PICK_POCKET, attack=1, accuracy=75, frequency=15)
__TELEMARKETER.describeAttack(AttackEnum.ROLODEX, attack=(4, 6, 7, 9, 12), accuracy=50, frequency=20)
__TELEMARKETER.describeAttack(AttackEnum.FINGER_WAG, attack=(4, 5, 7, 9, 10), accuracy=(60, 80), frequency=15)
__TELEMARKETER.describeAttack(AttackEnum.POUND_KEY, attack=(3, 7), accuracy=(55, 65, 70, 75, 80), frequency=20)
__TELEMARKETER.describeAttack(AttackEnum.MUMBO_JUMBO, attack=(4, 6, 7, 9, 12), accuracy=(75, 95), frequency=15)
__TELEMARKETER.test()

__NAME_DROPPER = SuitDefinition('nd', SELLBOT, 5.98, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=3)
__NAME_DROPPER.defineLevelRange(3, 7)
__NAME_DROPPER.defineParts(4.35, VBase4(0.756863, 0.686275, 0.803922, 1), ['phase_9/models/char/suits/ttcc_ene_namedropper'], [SKELE_HEAD_A],
                           suitType=SUIT_A, tieType=TIE_SKINNY, bodyTex=TEX_SALES)
__NAME_DROPPER.describeAttack(AttackEnum.RAZZLE_DAZZLE, attack=(4, 5, 6, 9, 12), accuracy=(75, 95), frequency=30)
__NAME_DROPPER.describeAttack(AttackEnum.ROLODEX, attack=(5, 6, 7, 10, 14), accuracy=95, frequency=40)
__NAME_DROPPER.describeAttack(AttackEnum.SYNERGY, attack=(3, 4, 6, 9, 12), accuracy=50, frequency=15)
__NAME_DROPPER.describeAttack(AttackEnum.PICK_POCKET, attack=2, accuracy=95, frequency=15)
__NAME_DROPPER.test()

__GLAD_HANDER = SuitDefinition('gh', SELLBOT, 6.4, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=4)
__GLAD_HANDER.defineLevelRange(4, 8)
__GLAD_HANDER.defineParts(4.75, VBase4(0.823529, 0.839216, 0.835294, 1), ['phase_9/models/char/suits/ttcc_ene_gladhander'], [SKELE_HEAD_C],
                          suitType=SUIT_C, tieType=TIE_SKINNY, bodyTex=TEX_SALES)
__GLAD_HANDER.describeAttack(AttackEnum.RUBBER_STAMP, attack=(4, 3, 3, 2, 1), accuracy=(90, 10), frequency=(40, 30, 20, 10, 5))
__GLAD_HANDER.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=(3, 3, 2, 1, 1), accuracy=(70, 30), frequency=(40, 30, 20, 10, 5))
__GLAD_HANDER.describeAttack(AttackEnum.FILIBUSTER, attack=(4, 6, 9, 12, 15), accuracy=(30, 70), frequency=(10, 20, 30, 40, 45))
__GLAD_HANDER.describeAttack(AttackEnum.SCHMOOZE, attack=(5, 7, 11, 15, 20), accuracy=(55, 95), frequency=(10, 20, 30, 40, 45))
__GLAD_HANDER.test()

__MOVER_AND_SHAKER = SuitDefinition('ms', SELLBOT, 6.7, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=5)
__MOVER_AND_SHAKER.defineLevelRange(5, 10)
__MOVER_AND_SHAKER.defineParts(4.75, VBase4(0.92549, 0.803922, 0.756863, 1), ['phase_9/models/char/suits/ttcc_ene_moverandshaker'], [SKELE_HEAD_B],
                               suitType=SUIT_B, tieType=TIE_SKINNY, bodyTex=TEX_SALES)
__MOVER_AND_SHAKER.describeAttack(AttackEnum.BRAIN_STORM, attack=(5, 6, 8, 10, 12, 14), accuracy=(60, 75, 80, 85, 90, 95), frequency=15)
__MOVER_AND_SHAKER.describeAttack(AttackEnum.HALF_WINDSOR, attack=(6, 9, 11, 13, 16, 19), accuracy=(50, 65, 70, 75, 80, 85), frequency=20)
__MOVER_AND_SHAKER.describeAttack(AttackEnum.QUAKE, attack=(9, 23), accuracy=(60, 65, 75, 80, 85, 90), frequency=20)
__MOVER_AND_SHAKER.describeAttack(AttackEnum.SHAKE, attack=(6, 16), accuracy=(70, 90), frequency=25)
__MOVER_AND_SHAKER.describeAttack(AttackEnum.TREMOR, attack=(5, 6, 7, 8, 9, 10), accuracy=50, frequency=20)
__MOVER_AND_SHAKER.test()

__TWO_FACE = SuitDefinition('tf', SELLBOT, 6.95, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=6)
__TWO_FACE.defineLevelRange(6, 12)
__TWO_FACE.defineParts(5.25, VBase4(0.92549, 0.803922, 0.756863, 1), ['phase_9/models/char/suits/ttcc_ene_twoface'], [SKELE_HEAD_A], suitType=SUIT_A,
                       tieType=TIE_SKINNY, bodyTex=TEX_SALES)
__TWO_FACE.describeAttack(AttackEnum.EVIL_EYE, attack=(10, 22), accuracy=(60, 75, 80, 85, 90), frequency=25)
__TWO_FACE.describeAttack(AttackEnum.HANG_UP, attack=(7, 8, 10, 12, 13, 15, 17), accuracy=(50, 60, 70, 80, 90), frequency=15)
__TWO_FACE.describeAttack(AttackEnum.RAZZLE_DAZZLE, attack=(8, 20), accuracy=(60, 65, 70, 75, 80, 85, 90), frequency=25)
__TWO_FACE.describeAttack(AttackEnum.RE_ORG, attack=(5, 8, 11, 13, 15, 17, 19), accuracy=(65, 75, 80, 85, 90, 95), frequency=15)
__TWO_FACE.describeAttack(AttackEnum.RED_TAPE, attack=(6, 12), accuracy=(60, 65, 75, 85, 90, 95), frequency=20)
__TWO_FACE.test()

__MINGLER = SuitDefinition('mi', SELLBOT, 7.61, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=7)
__MINGLER.defineLevelRange(7, 15)
__MINGLER.defineParts(5.75, VBase4(0.95, 0.75, 0.95, 1), ['phase_9/models/char/suits/ttcc_ene_mingler'], [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_SKINNY, bodyTex=TEX_SALES)
__MINGLER.describeAttack(AttackEnum.BUZZ_WORD, attack=(10, 11, 13, 15, 16, 18, 20, 22, 24), accuracy=(60, 75, 80, 85, 90), frequency=20)
__MINGLER.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=(10, 13, 14, 15, 18, 20, 22, 24, 26), accuracy=(60, 70, 75, 80, 90), frequency=25)
__MINGLER.describeAttack(AttackEnum.MUMBO_JUMBO, attack=(12, 15, 18, 21, 24, 26, 28, 30, 32), accuracy=(60, 65, 70, 75, 80, 85, 90, 95), frequency=15)
__MINGLER.describeAttack(AttackEnum.SCHMOOZE, attack=(7, 8, 12, 15, 16, 17, 18, 19, 20), accuracy=(55, 65, 75, 85, 95), frequency=30)
__MINGLER.describeAttack(AttackEnum.TEE_OFF, attack=(8, 9, 10, 11, 12, 13, 14, 15, 16), accuracy=(70, 75, 80, 85, 95), frequency=10)
__MINGLER.test()

__MR_HOLLYWOOD = SuitDefinition('mh', SELLBOT, 8.95, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=8)
__MR_HOLLYWOOD.defineLevelRange(8, 50)
__MR_HOLLYWOOD.defineParts(7.0, VBase4(0.823529, 0.839216, 0.835294, 1), ['phase_9/models/char/suits/ttcc_ene_mrhollywood'], [SKELE_HEAD_A],
                           suitType=SUIT_A, tieType=TIE_SKINNY, bodyTex=TEX_SALES)
__MR_HOLLYWOOD.describeAttack(AttackEnum.TEE_OFF,
                              attack=(10, 12, 15, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58),
                              accuracy=(70, 75, 80, 85, 90, 95),
                              frequency=25)
__MR_HOLLYWOOD.describeAttack(AttackEnum.SONG_AND_DANCE,
                              attack=(14, 16, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
                              accuracy=(45, 50, 55, 60, 65, 75, 80, 85, 90, 95),
                              frequency=25)
__MR_HOLLYWOOD.describeAttack(AttackEnum.SCHMOOZE,
                              attack=(16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58),
                              accuracy=(55, 65, 70, 75, 80, 85, 90, 95),
                              frequency=25)
__MR_HOLLYWOOD.describeAttack(AttackEnum.RAZZLE_DAZZLE,
                              attack=(8, 11, 14, 17, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58),
                              accuracy=(70, 75, 80, 85, 90, 95),
                              frequency=25)
__MR_HOLLYWOOD.test()

__FACTORY_FOREMAN = SuitDefinition('foreman', SELLBOT, 9.25, miniboss=True)
__FACTORY_FOREMAN.defineLevelRange(11)
__FACTORY_FOREMAN.defineParts(7.35, VBase4(0.95, 0.75, 0.95, 1), [SKELE_HEAD_A], [SKELE_HEAD_A], suitType=SUIT_A,
                              tieType=TIE_SKINNY, bodyTex=TEX_SALES, custom=True)
__FACTORY_FOREMAN.describeAttack(AttackEnum.FIRED, attack=20, accuracy=90, frequency=20)
__FACTORY_FOREMAN.describeAttack(AttackEnum.RE_ORG, attack=16, accuracy=80, frequency=10)
__FACTORY_FOREMAN.describeAttack(AttackEnum.HOT_AIR, attack=24, accuracy=95, frequency=20)
__FACTORY_FOREMAN.describeAttack(AttackEnum.CLIPON_TIE, attack=14, accuracy=75, frequency=10)
__FACTORY_FOREMAN.describeAttack(AttackEnum.DEMOTION, attack=18, accuracy=85, frequency=20)
__FACTORY_FOREMAN.describeAttack(AttackEnum.POWER_TRIP, attack=16, accuracy=85, frequency=20)
__FACTORY_FOREMAN.describeAttack(AttackEnum.WORKERS_COMP)
__FACTORY_FOREMAN.setHpPerLevel({11: 240})
__FACTORY_FOREMAN.makeAlwaysSkelecog()
# Forgive me for this...
__FACTORY_FOREMAN.describeAttack(AttackEnum.BAYOU_BASH)
__FACTORY_FOREMAN.describeAttack(AttackEnum.BAYOU_BELLOW)
__FACTORY_FOREMAN.describeAttack(AttackEnum.SACRIFICE)
__FACTORY_FOREMAN.test()
# endregion

### CASHBOTS ###
# region
__SHORT_CHANGE = SuitDefinition('sc', CASHBOT, 3.25, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=1)
__SHORT_CHANGE.defineLevelRange(1, 5)
__SHORT_CHANGE.defineParts(2.5, VBase4(0.294, 0.651, 0.871, 1), ['phase_10/models/char/suits/ttcc_ene_shortchange'], [SKELE_HEAD_C], suitType=SUIT_C,
                           tieType=TIE_BROAD, bodyTex=TEX_MONEY)
__SHORT_CHANGE.describeAttack(AttackEnum.WATERCOOLER, attack=(2, 2, 3, 4, 6), accuracy=50, frequency=20)
__SHORT_CHANGE.describeAttack(AttackEnum.BOUNCE_CHECK, attack=(3, 11), accuracy=(75, 95), frequency=15)
__SHORT_CHANGE.describeAttack(AttackEnum.CLIPON_TIE, attack=(1, 3), accuracy=50, frequency=25)
__SHORT_CHANGE.describeAttack(AttackEnum.PICK_POCKET, attack=(2, 2, 3, 4, 6), accuracy=95, frequency=40)
__SHORT_CHANGE.test()

__PENNY_PINCHER = SuitDefinition('pp', CASHBOT, 5.26, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=2)
__PENNY_PINCHER.defineLevelRange(2, 6)
__PENNY_PINCHER.defineParts(3.55, VBase4(0.796, 0.322, 0.286, 1.0), ['phase_10/models/char/suits/ttcc_ene_pennypincher'], [SKELE_HEAD_A], suitType=SUIT_A,
                            tieType=TIE_BROAD, bodyTex=TEX_MONEY)
__PENNY_PINCHER.describeAttack(AttackEnum.BOUNCE_CHECK, attack=(3, 4, 5, 7, 10), accuracy=80, frequency=25)
__PENNY_PINCHER.describeAttack(AttackEnum.FREEZE_ASSETS, attack=(2, 3, 4, 6, 9), accuracy=75, frequency=20)
__PENNY_PINCHER.describeAttack(AttackEnum.FINGER_WAG, attack=(1, 2, 3, 4, 6), accuracy=50, frequency=25)
__PENNY_PINCHER.describeAttack(AttackEnum.PENNY_PINCH, attack=(4, 5, 6, 8, 12), accuracy=75, frequency=30)
__PENNY_PINCHER.test()

__TIGHTWAD = SuitDefinition('tw', CASHBOT, 5.41, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=3)
__TIGHTWAD.defineLevelRange(3, 7)
__TIGHTWAD.defineParts(4.5, VBase4(0.65, 0.95, 0.85, 1), ['phase_10/models/char/suits/ttcc_ene_tightwad'], [SKELE_HEAD_C], suitType=SUIT_C,
                       tieType=TIE_BROAD, bodyTex=TEX_MONEY)
__TIGHTWAD.describeAttack(AttackEnum.FIRED, attack=(3, 4, 5, 5, 6), accuracy=75, frequency=(75, 5, 5, 5, 5))
__TIGHTWAD.describeAttack(AttackEnum.GLOWER_POWER, attack=(3, 4, 6, 9, 12), accuracy=95, frequency=(10, 15, 20, 25, 30))
__TIGHTWAD.describeAttack(AttackEnum.FINGER_WAG, attack=(3, 3, 4, 4, 5), accuracy=75, frequency=(5, 70, 5, 5, 5))
__TIGHTWAD.describeAttack(AttackEnum.FREEZE_ASSETS, attack=(3, 4, 6, 9, 12), accuracy=75, frequency=(5, 5, 65, 5, 30))
__TIGHTWAD.describeAttack(AttackEnum.BOUNCE_CHECK, attack=(5, 6, 9, 13, 18), accuracy=75, frequency=(5, 5, 5, 60, 30))
__TIGHTWAD.test()

__BEAN_COUNTER = SuitDefinition('bc', CASHBOT, 5.95, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=4)
__BEAN_COUNTER.defineLevelRange(4, 8)
__BEAN_COUNTER.defineParts(4.4, VBase4(0.643, 0.698, 0.659, 1), ['phase_10/models/char/suits/ttcc_ene_beancounter'], [SKELE_HEAD_B], suitType=SUIT_B,
                           tieType=TIE_BROAD, bodyTex=TEX_MONEY)
__BEAN_COUNTER.describeAttack(AttackEnum.AUDIT, attack=(4, 6, 9, 12, 15), accuracy=95, frequency=20)
__BEAN_COUNTER.describeAttack(AttackEnum.CALCULATE, attack=(4, 6, 9, 12, 15), accuracy=75, frequency=25)
__BEAN_COUNTER.describeAttack(AttackEnum.TABULATE, attack=(4, 6, 9, 12, 15), accuracy=75, frequency=25)
__BEAN_COUNTER.describeAttack(AttackEnum.WRITE_OFF, attack=(4, 6, 9, 12, 15), accuracy=95, frequency=30)
__BEAN_COUNTER.test()

__NUMBER_CRUNCHER = SuitDefinition('nc', CASHBOT, 7.22, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=5)
__NUMBER_CRUNCHER.defineLevelRange(5, 10)
__NUMBER_CRUNCHER.defineParts(5.25, VBase4(0.65, 0.95, 0.85, 1), ['phase_10/models/char/suits/ttcc_ene_numbercruncher'], [SKELE_HEAD_A], suitType=SUIT_A,
                              tieType=TIE_BROAD, bodyTex=TEX_MONEY)
__NUMBER_CRUNCHER.describeAttack(AttackEnum.AUDIT, attack=(5, 6, 8, 10, 12, 14), accuracy=(60, 75, 80, 85, 90, 95), frequency=15)
__NUMBER_CRUNCHER.describeAttack(AttackEnum.CALCULATE, attack=(6, 7, 9, 11, 13, 15), accuracy=(60, 75, 80, 85, 90, 95), frequency=30)
__NUMBER_CRUNCHER.describeAttack(AttackEnum.CRUNCH, attack=(9, 23), accuracy=(60, 65, 75, 80, 85, 90), frequency=35)
__NUMBER_CRUNCHER.describeAttack(AttackEnum.TABULATE, attack=(8, 14), accuracy=90, frequency=20)
__NUMBER_CRUNCHER.test()

__MONEY_BAGS = SuitDefinition('mb', CASHBOT, 6.97, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=6)
__MONEY_BAGS.defineLevelRange(6, 12)
__MONEY_BAGS.defineParts(5.3, VBase4(0.671, 0.761, 0.737, 1), ['phase_10/models/char/suits/ttcc_ene_moneybags'], [SKELE_HEAD_C], suitType=SUIT_C,
                         tieType=TIE_BROAD, bodyTex=TEX_MONEY)
__MONEY_BAGS.describeAttack(AttackEnum.LIQUIDATE, attack=(10, 22), accuracy=(60, 75, 80, 85, 90, 95), frequency=30)
__MONEY_BAGS.describeAttack(AttackEnum.MARKET_CRASH, attack=(8, 20), accuracy=(60, 65, 70, 75, 80, 85, 90), frequency=45)
__MONEY_BAGS.describeAttack(AttackEnum.POWER_TIE, attack=(6, 12), accuracy=(60, 65, 75, 85, 90, 95), frequency=25)
__MONEY_BAGS.test()

__LOAN_SHARK = SuitDefinition('ls', CASHBOT, 8.58, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=7)
__LOAN_SHARK.defineLevelRange(7, 15)
__LOAN_SHARK.defineParts(6.5, VBase4(0.671, 0.761, 0.737, 1), ['phase_10/models/char/suits/ttcc_ene_loanshark'], [SKELE_HEAD_B], suitType=SUIT_B,
                         tieType=TIE_BROAD, bodyTex=TEX_MONEY)
__LOAN_SHARK.describeAttack(AttackEnum.BITE, attack=(10, 11, 13, 15, 16, 18, 20, 22, 24), accuracy=(60, 75, 80, 85, 90, 95), frequency=30)
__LOAN_SHARK.describeAttack(AttackEnum.CHOMP, attack=(12, 15, 18, 21, 24, 26, 28, 30, 32), accuracy=(60, 70, 75, 80, 90, 95), frequency=35)
__LOAN_SHARK.describeAttack(AttackEnum.PLAY_HARDBALL, attack=(9, 25), accuracy=(80, 80, 85, 85, 90, 90, 90, 90, 95), frequency=20)
__LOAN_SHARK.describeAttack(AttackEnum.WRITE_OFF, attack=(6, 22), accuracy=(70, 75, 80, 85, 95), frequency=15)
__LOAN_SHARK.test()

__ROBBER_BARON = SuitDefinition('rb', CASHBOT, 8.95, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=8)
__ROBBER_BARON.defineLevelRange(8, 50)
__ROBBER_BARON.defineParts(7.0, VBase4(0.737, 0.788, 0.769, 1), ['phase_10/models/char/suits/ttcc_ene_robberbaron'], [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BROAD, bodyTex=TEX_MONEY)
__ROBBER_BARON.describeAttack(AttackEnum.SYNERGY,
                              attack=(11, 14, 16, 18, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59),
                              accuracy=(60, 65, 70, 75, 80, 85, 90, 90, 90, 90, 90, 90, 90, 95),
                              frequency=25)
__ROBBER_BARON.describeAttack(AttackEnum.CIGAR_SMOKE,
                              attack=(14, 15, 17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58),
                              accuracy=(60, 65, 70, 75, 80, 85, 90),
                              frequency=25)
__ROBBER_BARON.describeAttack(AttackEnum.PICK_POCKET,
                              attack=(8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50),
                              accuracy=(55, 65, 70, 75, 80, 85, 90),
                              frequency=25)
__ROBBER_BARON.describeAttack(AttackEnum.TEE_OFF,
                              attack=(10, 12, 14, 16, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56),
                              accuracy=(60, 65, 75, 85, 90),
                              frequency=25)
__ROBBER_BARON.test()

__MINT_SUPERVISOR = SuitDefinition('supervis', CASHBOT, 10.25, miniboss=True)
__MINT_SUPERVISOR.defineLevelRange(13, 13)
__MINT_SUPERVISOR.defineParts(7.35, VBase4(0.65, 0.95, 0.85, 1), [SKELE_HEAD_C], [SKELE_HEAD_C], suitType=SUIT_C,
                              tieType=TIE_BROAD, bodyTex=TEX_MONEY, custom=True)
__MINT_SUPERVISOR.describeAttack(AttackEnum.FIRED, attack=25, accuracy=90, frequency=20)
__MINT_SUPERVISOR.describeAttack(AttackEnum.LIQUIDATE, attack=24, accuracy=80, frequency=10)
__MINT_SUPERVISOR.describeAttack(AttackEnum.AUDIT, attack=20, accuracy=95, frequency=20)
__MINT_SUPERVISOR.describeAttack(AttackEnum.TABULATE, attack=26, accuracy=75, frequency=10)
__MINT_SUPERVISOR.describeAttack(AttackEnum.DEMOTION, attack=24, accuracy=85, frequency=20)
__MINT_SUPERVISOR.describeAttack(AttackEnum.SYNERGY, attack=18, accuracy=85, frequency=20)
__MINT_SUPERVISOR.describeAttack(AttackEnum.LIFE_INSURANCE, attack=0, accuracy=0, frequency=0)
__MINT_SUPERVISOR.setPassives(STATUS_EFFECTS=SEE.EFFECT_SUPERVISOR_INSURED)
__MINT_SUPERVISOR.setHpPerLevel({13: 320})
__MINT_SUPERVISOR.makeAlwaysSkelecog()
__MINT_SUPERVISOR.test()
# endregion

### LAWBOTS ###
# region
__BOTTOM_FEEDER = SuitDefinition('bf', LAWBOT, 4.81, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=1)
__BOTTOM_FEEDER.defineLevelRange(1, 5)
__BOTTOM_FEEDER.defineParts(4.0, VBase4(0.75, 0.75, 0.95, 1), ['phase_11/models/char/suits/ttcc_ene_bottom_feeder-zero'],
                            [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__BOTTOM_FEEDER.describeAttack(AttackEnum.RUBBER_STAMP, attack=(2, 6), accuracy=(75, 95), frequency=20)
__BOTTOM_FEEDER.describeAttack(AttackEnum.SHRED, attack=(2, 10), accuracy=(50, 70), frequency=20)
__BOTTOM_FEEDER.describeAttack(AttackEnum.WATERCOOLER, attack=(3, 7), accuracy=95, frequency=10)
__BOTTOM_FEEDER.describeAttack(AttackEnum.PICK_POCKET, attack=(1, 3), accuracy=(25, 45), frequency=50)
__BOTTOM_FEEDER.test()

__BLOODSUCKER = SuitDefinition('b', LAWBOT, 6.17, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=2)
__BLOODSUCKER.defineLevelRange(2, 6)
__BLOODSUCKER.defineParts(4.375, VBase4(0.95, 0.95, 1, 1), ['phase_11/models/char/suits/ttcc_ene_bloodsucker-zero'],
                          [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__BLOODSUCKER.describeAttack(AttackEnum.EVICTION_NOTICE, attack=(1, 2, 3, 3, 4), accuracy=75, frequency=20)
__BLOODSUCKER.describeAttack(AttackEnum.RED_TAPE, attack=(2, 3, 4, 6, 9), accuracy=75, frequency=20)
__BLOODSUCKER.describeAttack(AttackEnum.WITHDRAWAL, attack=(4, 12), accuracy=95, frequency=10)
__BLOODSUCKER.describeAttack(AttackEnum.BITE, attack=(5, 6, 7, 8, 10), accuracy=(60, 75, 80, 85, 90), frequency=10)
__BLOODSUCKER.describeAttack(AttackEnum.LIQUIDATE, attack=(2, 3, 4, 6, 9), accuracy=(50, 90), frequency=40)
__BLOODSUCKER.test()

__TTO_BLOODSUCKER = SuitDefinition('btto', LAWBOT, 6.17)
__TTO_BLOODSUCKER.defineLevelRange(2, 6)
__TTO_BLOODSUCKER.defineParts(4.375, VBase4(0.95, 0.95, 1, 1), ['phase_11/models/char/suits/ttcc_ene_bloodsucker_legacy'],
                              suitType=SUIT_B, custom=True)
__TTO_BLOODSUCKER.describeAttack(AttackEnum.EVICTION_NOTICE, attack=(1, 2, 3, 3, 4), accuracy=75, frequency=20)
__TTO_BLOODSUCKER.describeAttack(AttackEnum.RED_TAPE, attack=(2, 3, 4, 6, 9), accuracy=75, frequency=20)
__TTO_BLOODSUCKER.describeAttack(AttackEnum.WITHDRAWAL, attack=(4, 12), accuracy=95, frequency=10)
__TTO_BLOODSUCKER.describeAttack(AttackEnum.BITE, attack=(5, 6, 7, 8, 10), accuracy=(60, 75, 80, 85, 90), frequency=10)
__TTO_BLOODSUCKER.describeAttack(AttackEnum.LIQUIDATE, attack=(2, 3, 4, 6, 9), accuracy=(50, 90), frequency=40)
__TTO_BLOODSUCKER.test()

__PETTIFOGGER = SuitDefinition('pf', LAWBOT, 6.17, specialization=DEFENSE, onRadar=True, spawnsInInvasion=True, cogTier=2)
__PETTIFOGGER.defineLevelRange(2, 7)
__PETTIFOGGER.defineParts(4.35, VBase4(0.75, 0.75, 0.95, 1), ['phase_11/models/char/suits/ttcc_ene_pettifogger-zero'],
                          [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__PETTIFOGGER.describeAttack(AttackEnum.FILIBUSTER, attack=(1, 2, 2, 3, 3, 4), accuracy=75, frequency=20)
__PETTIFOGGER.describeAttack(AttackEnum.RED_TAPE, attack=(2, 7), accuracy=75, frequency=20)
__PETTIFOGGER.describeAttack(AttackEnum.WRITE_OFF, attack=(3, 4, 5, 6, 8, 10), accuracy=75, frequency=20)
__PETTIFOGGER.describeAttack(AttackEnum.FINGER_WAG, attack=(1, 2, 3, 5, 6, 7), accuracy=(60, 70, 80, 80, 90, 90), frequency=40)
__PETTIFOGGER.test()

__DOUBLETALKER = SuitDefinition('dt', LAWBOT, 5.63, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=3)
__DOUBLETALKER.defineLevelRange(3, 7)
__DOUBLETALKER.defineParts(4.25, VBase4(0.75, 0.75, 0.95, 1), ['phase_11/models/char/suits/ttcc_ene_doubletalker-zero'],
                           [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__DOUBLETALKER.describeAttack(AttackEnum.RUBBER_STAMP, attack=1, accuracy=(50, 90), frequency=5)
__DOUBLETALKER.describeAttack(AttackEnum.BOUNCE_CHECK, attack=1, accuracy=(50, 90), frequency=5)
__DOUBLETALKER.describeAttack(AttackEnum.BUZZ_WORD, attack=(1, 2, 3, 5, 6), accuracy=(50, 90), frequency=20)
__DOUBLETALKER.describeAttack(AttackEnum.DOUBLE_TALK, attack=(6, 6, 9, 13, 18), accuracy=(50, 90), frequency=25)
__DOUBLETALKER.describeAttack(AttackEnum.JARGON, attack=(3, 4, 6, 9, 12), accuracy=(50, 90), frequency=25)
__DOUBLETALKER.describeAttack(AttackEnum.MUMBO_JUMBO, attack=(3, 4, 6, 9, 12), accuracy=(50, 90), frequency=20)
__DOUBLETALKER.test()

__NEEDLENOSE = SuitDefinition('nn', LAWBOT, 5.41, specialization=ATTACK, onRadar=True, isFemale=True,
                              spawnsInInvasion=True, cogTier=3)
__NEEDLENOSE.defineLevelRange(3, 10)
__NEEDLENOSE.defineParts(4.5, VBase4(0.38, 0.455, 0.714, 1), ['phase_11/models/char/suits/ttcc_ene_needlenose-zero'],
                         [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__NEEDLENOSE.describeAttack(AttackEnum.RUBBER_STAMP, attack=(3, 5, 8, 12, 16, 20, 24, 28), accuracy=75, frequency=20)
__NEEDLENOSE.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=(7, 9, 12, 14, 16, 18, 20, 22), accuracy=(60, 70, 80, 90, 95), frequency=30)
__NEEDLENOSE.describeAttack(AttackEnum.BUZZ_WORD, attack=(4, 6, 9, 12, 15, 18, 21, 24, 27), accuracy=75, frequency=20)
__NEEDLENOSE.describeAttack(AttackEnum.POUND_KEY, attack=(5, 9, 13, 17, 21, 25, 28, 31), accuracy=(60, 70, 80, 90, 95), frequency=30)
__NEEDLENOSE.test()

__AMBULANCE_CHASER = SuitDefinition('ac', LAWBOT, 6.39, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=4)
__AMBULANCE_CHASER.defineLevelRange(4, 8)
__AMBULANCE_CHASER.defineParts(4.35, VBase4(0.75, 0.75, 0.95, 1),
                               ['phase_11/models/char/suits/ttcc_ene_ambulance_chaser-zero'], [SKELE_HEAD_B], suitType=SUIT_B,
                               tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__AMBULANCE_CHASER.describeAttack(AttackEnum.SHAKE, attack=(4, 6, 9, 12, 15), accuracy=75, frequency=15)
__AMBULANCE_CHASER.describeAttack(AttackEnum.RED_TAPE, attack=(6, 8, 12, 15, 19), accuracy=75, frequency=30)
__AMBULANCE_CHASER.describeAttack(AttackEnum.ROLODEX, attack=(3, 4, 5, 6, 7), accuracy=75, frequency=20)
__AMBULANCE_CHASER.describeAttack(AttackEnum.HANG_UP, attack=(2, 3, 4, 5, 6), accuracy=75, frequency=35)
__AMBULANCE_CHASER.test()

__CONVEYANCER = SuitDefinition('cv', LAWBOT, 6.71, specialization=DEFENSE, onRadar=True, spawnsInInvasion=True, cogTier=4)
__CONVEYANCER.defineLevelRange(4, 8)
__CONVEYANCER.defineParts(4.5, VBase4(0.427, 0.443, 0.561, 1),
                          ['phase_11/models/char/suits/ttcc_ene_conveyancer-zero', 'phase_11/models/char/suits/ttcc_ene_conveyancer_belt'], [SKELE_HEAD_A],
                          suitType=SUIT_A, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__CONVEYANCER.describeAttack(AttackEnum.LEGALESE, attack=(3, 5, 7, 10, 12), accuracy=(75, 85), frequency=20)
__CONVEYANCER.describeAttack(AttackEnum.EVICTION_NOTICE, attack=(4, 6, 9, 12, 15), accuracy=(75, 85), frequency=30)
__CONVEYANCER.describeAttack(AttackEnum.ROLODEX, attack=(2, 6), accuracy=(75, 85), frequency=20)
__CONVEYANCER.describeAttack(AttackEnum.JARGON, attack=(2, 3, 3, 4, 4), accuracy=(75, 85), frequency=30)
__CONVEYANCER.test()

__BACKSTABBER = SuitDefinition('bs', LAWBOT, 6.95, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=5)
__BACKSTABBER.defineLevelRange(5, 10)
__BACKSTABBER.defineParts(5.05, VBase4(0.561, 0.518, 0.737, 1), ['phase_11/models/char/suits/ttcc_ene_backstabber-zero'],
                          [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__BACKSTABBER.describeAttack(AttackEnum.GUILT_TRIP, attack=(8, 11, 13, 15, 18, 21), accuracy=(60, 75, 80, 85, 90, 95), frequency=35)
__BACKSTABBER.describeAttack(AttackEnum.RESTRAINING_ORDER, attack=(6, 7, 9, 11, 13, 15), accuracy=(50, 65, 70, 75, 90, 95), frequency=25)
__BACKSTABBER.describeAttack(AttackEnum.PICK_POCKET, attack=(10, 12, 15, 18, 20, 22), accuracy=(55, 65, 75, 85, 95, 95), frequency=15)
__BACKSTABBER.describeAttack(AttackEnum.FINGER_WAG, attack=(5, 6, 7, 8, 9, 10), accuracy=(50, 55, 65, 75, 80, 85), frequency=25)
__BACKSTABBER.test()

__ADVOCATE = SuitDefinition('ad', LAWBOT, 6.56, specialization=DEFENSE, onRadar=True, spawnsInInvasion=True, cogTier=5)
__ADVOCATE.defineLevelRange(5, 15)
__ADVOCATE.defineParts(5.25, VBase4(0.1, 0.1, 0.15, 1), ['phase_11/models/char/suits/ttcc_ene_advocate-zero'],
                       [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__ADVOCATE.describeAttack(AttackEnum.POWER_TRIP, attack=(5, 15), accuracy=(60, 75, 80, 85, 90, 95), frequency=35)
__ADVOCATE.describeAttack(AttackEnum.SHRED, attack=(4, 6, 8, 10, 12, 13, 14, 14, 15, 15, 16), accuracy=(50, 65, 70, 75, 90, 95), frequency=25)
__ADVOCATE.describeAttack(AttackEnum.GLOWER_POWER, attack=(6, 8, 10, 12, 14, 15, 16, 17, 18, 19, 20), accuracy=(55, 95), frequency=15)
__ADVOCATE.describeAttack(AttackEnum.WATERCOOLER, attack=(4, 5, 5, 6, 7, 8, 9, 10, 11, 12, 13), accuracy=(50, 55, 65, 75, 80, 85, 90, 95), frequency=25)
__ADVOCATE.test()

__SPIN_DOCTOR = SuitDefinition('sd', LAWBOT, 7.9, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=6)
__SPIN_DOCTOR.defineLevelRange(6, 12)
__SPIN_DOCTOR.defineParts(5.65, VBase4(0.573, 0.831, 0.718, 1), ['phase_11/models/char/suits/ttcc_ene_spin_doctor-zero'],
                          [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__SPIN_DOCTOR.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=(9, 10, 13, 16, 17, 18, 20), accuracy=(60, 75, 80, 85, 90, 95), frequency=30)
__SPIN_DOCTOR.describeAttack(AttackEnum.QUAKE, attack=(8, 10, 12, 14, 16, 18, 20), accuracy=(60, 65, 70, 75, 80, 85, 90), frequency=20)
__SPIN_DOCTOR.describeAttack(AttackEnum.SPIN, attack=(10, 12, 15, 18, 20, 22, 24), accuracy=(70, 75, 80, 85, 90, 95), frequency=20)
__SPIN_DOCTOR.describeAttack(AttackEnum.RE_ORG, attack=(5, 8, 11, 13, 15, 17, 19), accuracy=(65, 75, 80, 85, 90, 95), frequency=15)
__SPIN_DOCTOR.describeAttack(AttackEnum.WRITE_OFF, attack=(6, 12), accuracy=(60, 65, 75, 85, 90, 95), frequency=15)
__SPIN_DOCTOR.test()

__SHYSTER = SuitDefinition('sh', LAWBOT, 6.95, specialization=ATTACK, onRadar=True, isFemale=True,
                           spawnsInInvasion=True, cogTier=6)
__SHYSTER.defineLevelRange(6, 12)
__SHYSTER.defineParts(5.65, VBase4(0.75, 0.75, 0.95, 1), ['phase_11/models/char/suits/ttcc_ene_shyster-zero'], [SKELE_HEAD_B],
                      suitType=SUIT_B, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__SHYSTER.describeAttack(AttackEnum.GUILT_TRIP, attack=(12, 14, 17, 19, 21, 23, 25), accuracy=(85, 85, 85, 85, 90), frequency=40)
__SHYSTER.describeAttack(AttackEnum.LIQUIDATE, attack=(17, 20, 23, 26, 28, 30, 32), accuracy=(75, 75, 80, 80, 85, 85, 90), frequency=25)
__SHYSTER.describeAttack(AttackEnum.RESTRAINING_ORDER, attack=(13, 15, 17, 20, 22, 24, 26), accuracy=(65, 75, 80, 85, 90, 95), frequency=20)
__SHYSTER.describeAttack(AttackEnum.BUZZ_WORD, attack=(10, 11, 12, 14, 16, 18, 20), accuracy=(60, 65, 75, 85, 90, 95), frequency=15)
__SHYSTER.test()

__LEGAL_EAGLE = SuitDefinition('le', LAWBOT, 7.45, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=7)
__LEGAL_EAGLE.defineLevelRange(7, 15)
__LEGAL_EAGLE.defineParts(6.5, VBase4(0.705882, 0.690196, 0.854902, 1),
                          ['phase_11/models/char/suits/ttcc_ene_legal_eagle-zero'], [SKELE_HEAD_A], suitType=SUIT_A,
                          tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__LEGAL_EAGLE.describeAttack(AttackEnum.EVIL_EYE, attack=(10, 11, 13, 15, 16, 18, 20, 22, 24), accuracy=(60, 75, 80, 85, 90, 95), frequency=20)
__LEGAL_EAGLE.describeAttack(AttackEnum.JARGON, attack=(7, 9, 11, 13, 15, 17, 19, 21, 22), accuracy=(60, 70, 75, 80, 90, 95), frequency=15)
__LEGAL_EAGLE.describeAttack(AttackEnum.LEGALESE, attack=(11, 12, 13, 15, 17, 19, 21, 23, 25), accuracy=(55, 65, 75, 85, 95), frequency=30)
__LEGAL_EAGLE.describeAttack(AttackEnum.PECKING_ORDER, attack=(12, 15, 18, 20, 22, 24, 27, 29, 32), accuracy=(70, 75, 80, 85, 95), frequency=35)
__LEGAL_EAGLE.test()

__BARRISTER = SuitDefinition('br', LAWBOT, 7.75, specialization=ATTACK, onRadar=True, spawnsInInvasion=True, cogTier=7)
__BARRISTER.defineLevelRange(7, 15)
__BARRISTER.defineParts(6.75, VBase4(0.95, 0.95, 1, 1), ['phase_11/models/char/suits/ttcc_ene_barrister-zero'],
                        [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__BARRISTER.describeAttack(AttackEnum.THROW_BOOK, attack=(18, 21, 24, 27, 30, 32, 34, 36, 38), accuracy=(75, 80, 80, 80, 80, 85), frequency=40)
__BARRISTER.describeAttack(AttackEnum.EVIL_EYE, attack=(11, 13, 15, 17, 19, 21, 22, 23, 24), accuracy=(90, 90, 90, 90, 90, 90, 95), frequency=15)
__BARRISTER.describeAttack(AttackEnum.PLAY_HARDBALL, attack=(12, 15, 18, 20, 22, 23, 24, 25, 26), accuracy=(85, 85, 85, 90), frequency=15)
__BARRISTER.describeAttack(AttackEnum.QUAKE, attack=(14, 17, 20, 22, 24, 26, 28, 30, 32), accuracy=(70, 70, 75, 75, 80, 80, 85), frequency=30)
__BARRISTER.test()

__BIG_WIG = SuitDefinition('bw', LAWBOT, 8.69, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=8)
__BIG_WIG.defineLevelRange(8, 50)
__BIG_WIG.defineParts(7.0, VBase4(0.75, 0.75, 0.95, 1), ['phase_11/models/char/suits/ttcc_ene_bigwig-zero'], [SKELE_HEAD_A],
                      suitType=SUIT_A, tieType=TIE_BOW, bodyTex=TEX_LEGAL)
__BIG_WIG.describeAttack(AttackEnum.GUILT_TRIP,
                         attack=(11, 14, 16, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59),
                         accuracy=(70, 75, 80, 85, 90, 95),
                         frequency=25)
__BIG_WIG.describeAttack(AttackEnum.THROW_BOOK,
                         attack=(14, 16, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
                         accuracy=(70, 75, 80, 85, 90, 95),
                         frequency=25)
__BIG_WIG.describeAttack(AttackEnum.CIGAR_SMOKE,
                         attack=(10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52),
                         accuracy=(70, 75, 80, 85, 90, 95),
                         frequency=25)
__BIG_WIG.describeAttack(AttackEnum.FINGER_WAG,
                         attack=(13, 15, 17, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59),
                         accuracy=(80, 85, 85, 85, 90, 90, 90, 95),
                         frequency=25)
__BIG_WIG.test()

__HEAD_ATTORNEY = SuitDefinition('clerk', LAWBOT, 8.75, miniboss=True)
__HEAD_ATTORNEY.defineLevelRange(16)
__HEAD_ATTORNEY.defineParts(7.25, VBase4(0.75, 0.75, 0.95, 1), [SKELE_HEAD_B], [SKELE_HEAD_B], suitType=SUIT_B,
                            tieType=TIE_BOW, bodyTex=TEX_LEGAL, custom=True)
__HEAD_ATTORNEY.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=24, accuracy=90, frequency=20)
__HEAD_ATTORNEY.describeAttack(AttackEnum.QUAKE, attack=29, accuracy=60, frequency=20)
__HEAD_ATTORNEY.describeAttack(AttackEnum.EVICTION_NOTICE, attack=28, accuracy=95, frequency=20)
__HEAD_ATTORNEY.describeAttack(AttackEnum.SPIN, attack=27, accuracy=75, frequency=15)
__HEAD_ATTORNEY.describeAttack(AttackEnum.RED_TAPE, attack=23, accuracy=85, frequency=25)
__HEAD_ATTORNEY.describeAttack(AttackEnum.OBJECTION)
__HEAD_ATTORNEY.describeAttack(AttackEnum.OBJECTION_SUSTAINED, attack=20, accuracy=100)
__HEAD_ATTORNEY.describeAttack(AttackEnum.OBJECTION_OVERRULED)
__HEAD_ATTORNEY.setHpPerLevel({16: 465})
__HEAD_ATTORNEY.makeAlwaysSkelecog()
__HEAD_ATTORNEY.test()
# endregion

### BOSSBOTS ###
# region
__FLUNKY = SuitDefinition('f', BOSSBOT, 4.88, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=1)
__FLUNKY.defineLevelRange(1, 5)
__FLUNKY.defineParts(4.0, corpPolyColor, ['phase_12/models/char/suits/ttcc_ene_flunky'], [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BROAD,
                     bodyTex=TEX_CORP)
__FLUNKY.describeAttack(AttackEnum.POUND_KEY,  attack=(2, 2, 3, 4, 6), accuracy=(75, 90), frequency=(30, 50))
__FLUNKY.describeAttack(AttackEnum.SHRED,      attack=(3, 7),          accuracy=(50, 70), frequency=(10, 30))
__FLUNKY.describeAttack(AttackEnum.CLIPON_TIE, attack=(1, 3),          accuracy=(75, 95), frequency=(60, 20))
__FLUNKY.test()

__PENCIL_PUSHER = SuitDefinition('p', BOSSBOT, 5.0, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=2)
__PENCIL_PUSHER.defineLevelRange(2, 6)
__PENCIL_PUSHER.defineParts(3.35, VBase4(0.573, 0.463, 0.443, 1), ['phase_12/models/char/suits/ttcc_ene_pencilpusher'], [SKELE_HEAD_B], suitType=SUIT_B,
                            tieType=TIE_BROAD, bodyTex=TEX_CORP)
__PENCIL_PUSHER.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=(2, 3, 4, 6, 9), accuracy=75, frequency=20)
__PENCIL_PUSHER.describeAttack(AttackEnum.RUB_OUT, attack=(4, 5, 6, 8, 12), accuracy=75, frequency=20)
__PENCIL_PUSHER.describeAttack(AttackEnum.FINGER_WAG, attack=(1, 2, 2, 3, 4), accuracy=75, frequency=15)
__PENCIL_PUSHER.describeAttack(AttackEnum.WRITE_OFF, attack=(4, 12), accuracy=75, frequency=25)
__PENCIL_PUSHER.describeAttack(AttackEnum.FILL_WITH_LEAD, attack=(3, 7), accuracy=75, frequency=20)
__PENCIL_PUSHER.test()

__YESMAN = SuitDefinition('ym', BOSSBOT, 5.28, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=3)
__YESMAN.defineLevelRange(3, 7)
__YESMAN.defineParts(4.125, VBase4(0.823529, 0.839216, 0.835294, 1), ['phase_12/models/char/suits/ttcc_ene_yesman'], [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BROAD, bodyTex=TEX_CORP)
__YESMAN.describeAttack(AttackEnum.RUBBER_STAMP, attack=(2, 10), accuracy=75, frequency=35)
__YESMAN.describeAttack(AttackEnum.RAZZLE_DAZZLE, attack=(7, 15), accuracy=50, frequency=(25, 5))
__YESMAN.describeAttack(AttackEnum.SYNERGY, attack=(4, 12), accuracy=(50, 90), frequency=(5, 25))
__YESMAN.describeAttack(AttackEnum.TEE_OFF, attack=(5, 13), accuracy=(50, 90), frequency=35)
__YESMAN.test()

__MICROMANAGER = SuitDefinition('mm', BOSSBOT, 1.625, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=4)
__MICROMANAGER.defineLevelRange(4, 8)
__MICROMANAGER.defineParts(1.25, VBase4(0.95, 0.75, 0.75, 1), ['phase_12/models/char/suits/ttcc_ene_micromanager'], [SKELE_HEAD_C], suitType=SUIT_C,
                           tieType=TIE_BROAD, bodyTex=TEX_CORP)
__MICROMANAGER.describeAttack(AttackEnum.DEMOTION, attack=(6, 8, 12, 15, 18), accuracy=(50, 90), frequency=30)
__MICROMANAGER.describeAttack(AttackEnum.FINGER_WAG, attack=(4, 6, 9, 12, 15), accuracy=(50, 90), frequency=10)
__MICROMANAGER.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=(3, 4, 6, 8, 10), accuracy=(50, 90), frequency=15)
__MICROMANAGER.describeAttack(AttackEnum.BRAIN_STORM, attack=(4, 6, 9, 12, 15), accuracy=(50, 55, 65, 75, 85), frequency=25)
__MICROMANAGER.describeAttack(AttackEnum.BUZZ_WORD, attack=(4, 6, 9, 12, 15), accuracy=(50, 90), frequency=20)
__MICROMANAGER.test()

__DOWNSIZER = SuitDefinition('ds', BOSSBOT, 6.08, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=5)
__DOWNSIZER.defineLevelRange(5, 10)
__DOWNSIZER.defineParts(4.5, VBase4(0.643, 0.698, 0.659, 1), ['phase_12/models/char/suits/ttcc_ene_downsizer'], [SKELE_HEAD_B], suitType=SUIT_B,
                        tieType=TIE_BROAD, bodyTex=TEX_CORP)
__DOWNSIZER.describeAttack(AttackEnum.CANNED, attack=(6, 8, 9, 11, 13, 15), accuracy=(60, 75, 80, 85, 90, 95), frequency=25)
__DOWNSIZER.describeAttack(AttackEnum.DOWNSIZE, attack=(10, 13, 15, 18, 20, 22), accuracy=(50, 90), frequency=35)
__DOWNSIZER.describeAttack(AttackEnum.PINK_SLIP, attack=(9, 15), accuracy=(40, 55, 65, 75, 90, 95), frequency=25)
__DOWNSIZER.describeAttack(AttackEnum.SACKED, attack=(5, 7, 9, 12, 14, 16), accuracy=(50, 75), frequency=15)
__DOWNSIZER.test()

__HEAD_HUNTER = SuitDefinition('hh', BOSSBOT, 7.45, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=6)
__HEAD_HUNTER.defineLevelRange(6, 12)
__HEAD_HUNTER.defineParts(6.5, VBase4(0.95, 0.75, 0.75, 1), ['phase_12/models/char/suits/ttcc_ene_headhunter'], [SKELE_HEAD_A], suitType=SUIT_A,
                          tieType=TIE_BROAD, bodyTex=TEX_CORP)
__HEAD_HUNTER.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=(5, 6, 8, 10, 12, 14, 16), accuracy=(60, 75, 80, 85, 90, 95, 95), frequency=15)
__HEAD_HUNTER.describeAttack(AttackEnum.GLOWER_POWER, attack=(7, 8, 10, 12, 14, 16, 18), accuracy=(50, 60, 70, 80, 90, 95, 95), frequency=20)
__HEAD_HUNTER.describeAttack(AttackEnum.HALF_WINDSOR, attack=(8, 20), accuracy=(60, 90), frequency=20)
__HEAD_HUNTER.describeAttack(AttackEnum.HEAD_SHRINK, attack=(10, 12, 15, 18, 21, 22, 24), accuracy=(65, 75, 80, 85, 95, 95, 95), frequency=20)
__HEAD_HUNTER.describeAttack(AttackEnum.RE_ORG, attack=(5, 8, 11, 13, 15, 17, 19), accuracy=(65, 75, 80, 85, 90, 95, 95), frequency=15)
__HEAD_HUNTER.describeAttack(AttackEnum.ROLODEX, attack=(6, 12), accuracy=(60, 90), frequency=10)
__HEAD_HUNTER.test()

__CORPORATE_RAIDER = SuitDefinition('cr', BOSSBOT, 8.23, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=7)
__CORPORATE_RAIDER.defineLevelRange(7, 15)
__CORPORATE_RAIDER.defineParts(6.75, VBase4(0.792, 0.675, 0.624, 1), ['phase_12/models/char/suits/ttcc_ene_corporateraider'], [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BROAD, bodyTex=TEX_CORP)
__CORPORATE_RAIDER.describeAttack(AttackEnum.CANNED, attack=(8, 16), accuracy=(80, 80, 85, 85, 90, 90, 95, 95, 95), frequency=15)
__CORPORATE_RAIDER.describeAttack(AttackEnum.EVIL_EYE, attack=(12, 15, 18, 21, 24, 26, 28, 30, 32), accuracy=(60, 70, 75, 80, 90, 95, 95, 95, 95), frequency=25)
__CORPORATE_RAIDER.describeAttack(AttackEnum.PICK_POCKET, attack=(9, 12, 13, 14, 15, 17, 18, 20, 22), accuracy=(55, 65, 75, 85, 95, 95, 95, 95, 95), frequency=20)
__CORPORATE_RAIDER.describeAttack(AttackEnum.PLAY_HARDBALL, attack=(7, 8, 12, 15, 16, 18, 20, 22, 24), accuracy=(60, 65, 70, 75, 80, 85, 90, 95, 95), frequency=20)
__CORPORATE_RAIDER.describeAttack(AttackEnum.POWER_TIE,
                                  attack=(10, 26),
                                  accuracy=(65, 75, 80, 85, 95, 95, 95, 95, 95),
                                  frequency=20)
__CORPORATE_RAIDER.test()

__BIG_CHEESE = SuitDefinition('tbc', BOSSBOT, 9.34, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=8)
__BIG_CHEESE.defineLevelRange(8, 50)
__BIG_CHEESE.defineParts(7.0, VBase4(0.631, 0.8, 0.416, 1), ['phase_12/models/char/suits/ttcc_ene_bigcheese'], [SKELE_HEAD_A], suitType=SUIT_A,
                         tieType=TIE_BROAD, bodyTex=TEX_CORP)
__BIG_CHEESE.describeAttack(AttackEnum.CIGAR_SMOKE,
                            attack=(10, 12, 15, 18, 20, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61),
                            accuracy=(55, 65, 70, 75, 80, 85, 90),
                            frequency=25)
__BIG_CHEESE.describeAttack(AttackEnum.POWER_TRIP,
                            attack=(14, 15, 17, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59),
                            accuracy=(60, 65, 70, 75, 80, 85, 90),
                            frequency=25)
__BIG_CHEESE.describeAttack(AttackEnum.GLOWER_POWER,
                            attack=(10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 50, 51, 52, 53, 54, 55, 56),
                            accuracy=(55, 65, 70, 75, 80, 85, 90),
                            frequency=20)
__BIG_CHEESE.describeAttack(AttackEnum.TEE_OFF,
                            attack=(8, 11, 14, 17, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58),
                            accuracy=(55, 65, 70, 75, 80, 85, 90),
                            frequency=30)
__BIG_CHEESE.test()

__CLUB_PRESIDENT = SuitDefinition('clubpres', BOSSBOT, 9.25, miniboss=True)
__CLUB_PRESIDENT.defineLevelRange(18)
__CLUB_PRESIDENT.defineParts(7.35, VBase4(133/255, 112/255, 86/255, 1), ['phase_12/models/char/suits/ttcc_ene_clubpresident-zero'],
                             ['phase_12/models/char/suits/ttcc_ene_clubpresident-zero'], suitType=SUIT_A,
                             tieType=TIE_BROAD, bodyTex=TEX_CORP, custom=True)
__CLUB_PRESIDENT.describeAttack(AttackEnum.CIGAR_SMOKE, attack=38, accuracy=90, frequency=13)
__CLUB_PRESIDENT.describeAttack(AttackEnum.SONG_AND_DANCE, attack=32, accuracy=90, frequency=12)
__CLUB_PRESIDENT.describeAttack(AttackEnum.GLOWER_POWER, attack=34, accuracy=90, frequency=13)
__CLUB_PRESIDENT.describeAttack(AttackEnum.POWER_TRIP, attack=32, accuracy=90, frequency=12)
__CLUB_PRESIDENT.describeAttack(AttackEnum.TEE_OFF, attack=35, accuracy=90, frequency=50)
__CLUB_PRESIDENT.describeAttack(AttackEnum.EXTRA_TIP)
__CLUB_PRESIDENT.setHpPerLevel({18: 600})
__CLUB_PRESIDENT.test()

__AUTOCADDIE = SuitDefinition('autocad', BOSSBOT, 5.45)
__AUTOCADDIE.defineLevelRange(14, 15)
__AUTOCADDIE.defineParts(4.34, VBase4(0.95, 0.75, 0.75, 1), ['phase_12/models/char/suits/ttcc_ene_autocaddie-zero'],
                         ['phase_12/models/char/suits/ttcc_ene_autocaddie-zero'], suitType=SUIT_A, tieType=TIE_BROAD,
                         bodyTex=TEX_CORP, custom=True)
__AUTOCADDIE.describeAttack(AttackEnum.CIGAR_SMOKE, attack=(22, 24), accuracy=(85, 90), frequency=20)
__AUTOCADDIE.describeAttack(AttackEnum.SONG_AND_DANCE, attack=(24, 25), accuracy=(70, 75), frequency=15)
__AUTOCADDIE.describeAttack(AttackEnum.GLOWER_POWER, attack=(24, 25), accuracy=90, frequency=15)
__AUTOCADDIE.describeAttack(AttackEnum.POWER_TRIP, attack=(25, 26), accuracy=(65, 70), frequency=15)
__AUTOCADDIE.describeAttack(AttackEnum.TEE_OFF, attack=(26, 28), accuracy=(70, 75), frequency=35)
__AUTOCADDIE.setHpPerLevel({14: 375, 15: 425})
__AUTOCADDIE.makeAlwaysExecutive()
__AUTOCADDIE.makeAlwaysSkelecog()
__AUTOCADDIE.test()
# endregion

### BOARDBOTS ###
# region
__BAG_HOLDER = SuitDefinition('bgh', BOARDBOT, 5.45, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=1)
__BAG_HOLDER.defineLevelRange(1, 5)
__BAG_HOLDER.defineParts(4.0, ColorHelper.hexToPCol('74a1a6'), ['phase_14/models/char/suits/cc_a_ene_bagholder-zero'],
                         [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BROAD, bodyTex=TEX_BOARD)
__BAG_HOLDER.describeAttack(AttackEnum.SHORT_SQUEEZE, attack=(2, 3, 5, 6, 11), accuracy=(75, 90), frequency=25)
__BAG_HOLDER.describeAttack(AttackEnum.SACKED, attack=(2, 10), accuracy=90, frequency=25)
__BAG_HOLDER.describeAttack(AttackEnum.PICK_POCKET, attack=(2, 3, 5, 7, 9), accuracy=(50, 70), frequency=25)
__BAG_HOLDER.describeAttack(AttackEnum.RUBBER_STAMP, attack=(1, 3, 5, 6, 8), accuracy=(55, 75), frequency=25)
__BAG_HOLDER.test()

__PAPER_HANDS = SuitDefinition('pph', BOARDBOT, 5.24, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=2)
__PAPER_HANDS.defineLevelRange(2, 6)
__PAPER_HANDS.defineParts(3.75, ColorHelper.hexToPCol('e1e7ed'), ['phase_14/models/char/suits/cc_a_ene_paperhands-zero'],
                          [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_BROAD, bodyTex=TEX_BOARD)
__PAPER_HANDS.describeAttack(AttackEnum.SHORT_SQUEEZE, attack=(5, 7, 9, 11, 13), accuracy=75, frequency=20)
__PAPER_HANDS.describeAttack(AttackEnum.ROLODEX, attack=(3, 6, 7, 10, 12), accuracy=80, frequency=20)
__PAPER_HANDS.describeAttack(AttackEnum.MARKET_CRASH, attack=(3, 11), accuracy=80, frequency=20)
__PAPER_HANDS.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=(2, 5, 7, 9, 10), accuracy=(70, 90), frequency=20)
__PAPER_HANDS.describeAttack(AttackEnum.WRITE_OFF, attack=(4, 6, 7, 9, 12), accuracy=(70, 85), frequency=20)
__PAPER_HANDS.test()

__INSIDER = SuitDefinition('ins', BOARDBOT, 5.8, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=3)
__INSIDER.defineLevelRange(3, 7)
__INSIDER.defineParts(4.34, VBase4(0.063, 0.067, 0.094, 1.0), ['phase_14/models/char/suits/cc_a_ene_insider-zero'],
                      [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_NONE,
                      bodyTex='phase_3.5/maps/ttcc_ene_suittex_highcollar_g.png', bodyModelType=BodyModelType.HighCollar)
__INSIDER.describeAttack(AttackEnum.BLUE_CHIP, attack=(6, 7, 9, 13, 15), accuracy=75, frequency=25)
__INSIDER.describeAttack(AttackEnum.PICK_POCKET, attack=(2, 4, 7, 10, 11), accuracy=(75, 95), frequency=25)
__INSIDER.describeAttack(AttackEnum.POWER_TRIP, attack=(3, 5, 7, 8, 9), accuracy=(60, 80), frequency=25)
__INSIDER.describeAttack(AttackEnum.HANG_UP, attack=(3, 6, 7, 11, 13), accuracy=95, frequency=25)
__INSIDER.test()

__CIRCUIT_BREAKER = SuitDefinition('cbr', BOARDBOT, 7.3, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=4)
__CIRCUIT_BREAKER.defineLevelRange(4, 8)
__CIRCUIT_BREAKER.defineParts(5.0, ColorHelper.hexToPCol('616b6a'), ['phase_14/models/char/suits/cc_a_ene_circuitbreaker-zero'],
                              [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BROAD, bodyTex=TEX_BOARD)
__CIRCUIT_BREAKER.describeAttack(AttackEnum.FALLING_KNIFE, attack=(8, 18), accuracy=(60, 75), frequency=25)
__CIRCUIT_BREAKER.describeAttack(AttackEnum.QUAKE, attack=(7, 9, 10, 12, 13), accuracy=(60, 90), frequency=25)
__CIRCUIT_BREAKER.describeAttack(AttackEnum.POWER_TRIP, attack=(6, 7, 9, 10, 11), accuracy=(55, 80), frequency=25)
__CIRCUIT_BREAKER.describeAttack(AttackEnum.BRAIN_STORM, attack=(7, 9, 11, 13, 15), accuracy=(60, 80), frequency=25)
__CIRCUIT_BREAKER.test()

__DEAD_LOCK = SuitDefinition('dl', BOARDBOT, 7.2, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=5)
__DEAD_LOCK.defineLevelRange(5, 10)
__DEAD_LOCK.defineParts(5.25, ColorHelper.hexToPCol('98a9ac'), ['phase_14/models/char/suits/cc_a_ene_deadlock-zero'],
                        [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BROAD, bodyTex=TEX_BOARD)
__DEAD_LOCK.describeAttack(AttackEnum.SHORT_SQUEEZE, attack=(10, 22), accuracy=(70, 85), frequency=20)
__DEAD_LOCK.describeAttack(AttackEnum.RED_TAPE, attack=(7, 18), accuracy=(80, 95), frequency=20)
__DEAD_LOCK.describeAttack(AttackEnum.EVIL_EYE, attack=(8, 17), accuracy=(75, 90), frequency=20)
__DEAD_LOCK.describeAttack(AttackEnum.GUILT_TRIP, attack=(6, 15), accuracy=(60, 85), frequency=20)
__DEAD_LOCK.describeAttack(AttackEnum.GLOWER_POWER, attack=(8, 19), accuracy=(70, 85), frequency=20)
__DEAD_LOCK.test()

__SHARK_WATCHER = SuitDefinition('shw', BOARDBOT, 8.25, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=7)
__SHARK_WATCHER.defineLevelRange(6, 12)
__SHARK_WATCHER.defineParts(5.6, ColorHelper.hexToPCol('547B80'), ['phase_14/models/char/suits/cc_a_ene_sharkwatcher-zero'],
                            [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BROAD, bodyTex=TEX_BOARD)
__SHARK_WATCHER.describeAttack(AttackEnum.FALLING_KNIFE, attack=(12, 27), accuracy=(75, 85), frequency=20)
__SHARK_WATCHER.describeAttack(AttackEnum.LIQUIDATE, attack=(8, 22), accuracy=(80, 95), frequency=20)
__SHARK_WATCHER.describeAttack(AttackEnum.BITE, attack=(10, 25), accuracy=(70, 90), frequency=20)
__SHARK_WATCHER.describeAttack(AttackEnum.WATERCOOLER_GROUP, attack=(8, 19), accuracy=(65, 85), frequency=20)
__SHARK_WATCHER.describeAttack(AttackEnum.GLOWER_POWER, attack=(10, 22), accuracy=90, frequency=20)
__SHARK_WATCHER.test()

__MAGNATE = SuitDefinition('mg', BOARDBOT, 8.5, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=6)
__MAGNATE.defineLevelRange(7, 15)
__MAGNATE.defineParts(6.8, VBase4(0.188, 0.188, 0.188, 1), ['phase_14/models/char/suits/cc_a_ene_magnate-zero'],
                      [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BROAD, bodyTex=TEX_BOARD)
__MAGNATE.describeAttack(AttackEnum.BLUE_CHIP, attack=(14, 33), accuracy=85, frequency=25)
__MAGNATE.describeAttack(AttackEnum.PECKING_ORDER, attack=(11, 28), accuracy=(70, 90), frequency=20)
__MAGNATE.describeAttack(AttackEnum.TEE_OFF, attack=(9, 25), accuracy=90, frequency=15)
__MAGNATE.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=(9, 24), accuracy=(65, 85), frequency=20)
__MAGNATE.describeAttack(AttackEnum.FIRED, attack=(10, 27), accuracy=(80, 95), frequency=20)
__MAGNATE.test()

__HEAD_HONCHO = SuitDefinition('hho', BOARDBOT, 10.1, isMainline=True, onRadar=True, spawnsInInvasion=True, cogTier=8)
__HEAD_HONCHO.defineLevelRange(8, 50)
__HEAD_HONCHO.defineParts(7.0, VBase4(0.329, 0.329, 0.329, 1.0), ['phase_14/models/char/suits/cc_a_ene_headhoncho-zero'],
                          [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BROAD, bodyTex=TEX_BOARD)
__HEAD_HONCHO.describeAttack(AttackEnum.FALLING_KNIFE,
                             attack=(17, 20, 23, 25, 27, 29, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68),
                             accuracy=80,
                             frequency=20)
__HEAD_HONCHO.describeAttack(AttackEnum.BLUE_CHIP,
                             attack=(15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68),
                             accuracy=85,
                             frequency=20)
__HEAD_HONCHO.describeAttack(AttackEnum.CIGAR_SMOKE_HEAD_HONCHO,
                             attack=(12, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
                             accuracy=(85, 90),
                             frequency=20)
__HEAD_HONCHO.describeAttack(AttackEnum.FIRED,
                             attack=(10, 13, 16, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58),
                             accuracy=(80, 90),
                             frequency=20)
__HEAD_HONCHO.describeAttack(AttackEnum.POWER_TRIP,
                             attack=(11, 14, 17, 19, 20, 22, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60),
                             accuracy=80,
                             frequency=20)
__HEAD_HONCHO.test()

__CHAIRMAN = SuitDefinition('chairman', BOARDBOT, 3.25)
__CHAIRMAN.defineLevelRange(50)
__CHAIRMAN.defineParts(2.5, VBase4(84/255, 78/255, 69/255, 1), ['phase_14/models/char/suits/ttcc_ene_chairman-zero'],
                       [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BROAD, bodyTex=TEX_BOARD, custom=True)
__CHAIRMAN.describeAttack(AttackEnum.FIRED, attack=20, accuracy=90, frequency=20)
__CHAIRMAN.describeAttack(AttackEnum.RE_ORG, attack=16, accuracy=80, frequency=10)
__CHAIRMAN.describeAttack(AttackEnum.HOT_AIR, attack=24, accuracy=95, frequency=20)
__CHAIRMAN.describeAttack(AttackEnum.CLIPON_TIE, attack=14, accuracy=75, frequency=10)
__CHAIRMAN.describeAttack(AttackEnum.DEMOTION, attack=18, accuracy=85, frequency=20)
__CHAIRMAN.describeAttack(AttackEnum.POWER_TRIP, attack=16, accuracy=85, frequency=20)
__CHAIRMAN.test()

__OTTOMAN = SuitDefinition('ottoman', BOARDBOT, 5.95)
__OTTOMAN.defineLevelRange(50, 50)
__OTTOMAN.defineParts(4.4, VBase4(0.212, 0.173, 0.145, 1.0), ['phase_14/models/char/suits/ttcc_ene_ottoman-zero'],
                      [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_BROAD, bodyTex=TEX_BOARD, custom=True)
__OTTOMAN.describeAttack(AttackEnum.FIRED, attack=20, accuracy=90, frequency=20)
__OTTOMAN.describeAttack(AttackEnum.RE_ORG, attack=16, accuracy=80, frequency=10)
__OTTOMAN.describeAttack(AttackEnum.HOT_AIR, attack=24, accuracy=95, frequency=20)
__OTTOMAN.describeAttack(AttackEnum.CLIPON_TIE, attack=14, accuracy=75, frequency=10)
__OTTOMAN.describeAttack(AttackEnum.DEMOTION, attack=18, accuracy=85, frequency=20)
__OTTOMAN.describeAttack(AttackEnum.POWER_TRIP, attack=16, accuracy=85, frequency=20)
__OTTOMAN.makeHidden()
__OTTOMAN.test()
# endregion

### TOONTORIAL ###
# region
__DESK_JOCKEY = SuitDefinition('djockey', BOSSBOT, 7.1, hideDepartment=True)
__DESK_JOCKEY.defineLevelRange(1, 9)
__DESK_JOCKEY.defineParts(4.0, VBase4(0.95, 0.95, 0.95, 1), ['phase_3.5/models/schoolhouse/dummy/ttcc_ene_dummy-zero'], [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BOW,
                     bodyTex='phase_3.5/maps/schoolhouse/dummy/ttcc_ene_suittex_djockey.png',
                     textureOverride='phase_3.5/maps/schoolhouse/dummy/ttcc_ene_djockey.png')
__DESK_JOCKEY.describeAttack(AttackEnum.POUND_KEY,  attack=6, accuracy=75, frequency=30)
__DESK_JOCKEY.describeAttack(AttackEnum.SHRED,      attack=6, accuracy=50, frequency=10)
__DESK_JOCKEY.describeAttack(AttackEnum.CLIPON_TIE, attack=6, accuracy=75, frequency=60)
__DESK_JOCKEY.describeAttack(AttackEnum.LIGHTS_ON)
__DESK_JOCKEY.setHpPerLevel({
    1: 6,
    2: 12,
    9: 110
})
__DESK_JOCKEY.setAttackBehavior(SEE.EFFECT_MANAGER_DESK_JOCKEY)
__DESK_JOCKEY.makeHidden()
__DESK_JOCKEY.test()
# endregion

### TASKLINE MINIBOSSES ###
# region
__DERRICK_MAN = SuitDefinition('derrman', BOSSBOT, 6.7, miniboss=True)
__DERRICK_MAN.defineLevelRange(5)
__DERRICK_MAN.defineParts(4.75, VBase4(175/255, 118/255, 63/255, 1), ['phase_12/models/char/suits/ttcc_ene_derrickman-zero'], [SKELE_HEAD_A], suitType=SUIT_A,
                          tieType=TIE_BROAD, bodyTex=TEX_CORP, custom=True)
__DERRICK_MAN.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=10, accuracy=75, frequency=20)
__DERRICK_MAN.describeAttack(AttackEnum.LIQUIDATE, attack=6, accuracy=95, frequency=10)
__DERRICK_MAN.describeAttack(AttackEnum.WITHDRAWAL, attack=10, accuracy=80, frequency=20)
__DERRICK_MAN.describeAttack(AttackEnum.QUAKE, attack=5, accuracy=75, frequency=30)
__DERRICK_MAN.describeAttack(AttackEnum.FREEZE_ASSETS, attack=4, accuracy=85, frequency=20)
__DERRICK_MAN.describeAttack(AttackEnum.REFINEMENT, attack=0, accuracy=0, frequency=0)
__DERRICK_MAN.setHpPerLevel({5: 100})
__DERRICK_MAN.setBounty({CogBountyTypes.Gumballs: 5, CogBountyTypes.Jellybeans: 40, CogBountyTypes.Experience: 100})
__DERRICK_MAN.setMovieAttributes(overrideDeaths=True, extendMovieTime=90)
__DERRICK_MAN.makeHidden()
__DERRICK_MAN.test()

__DLAO = SuitDefinition('dlao', BOARDBOT, 9.9, miniboss=True)
__DLAO.defineLevelRange(7)
__DLAO.defineParts(6.75, VBase4(144/255, 129/255, 118/255, 1), ['phase_14/models/char/suits/ttcc_ene_dola-zero'],
                   [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_BROAD, bodyTex=TEX_BOARD, custom=True)
__DLAO.describeAttack(AttackEnum.RE_ORG, attack=12, accuracy=75, frequency=20)
__DLAO.describeAttack(AttackEnum.BRAIN_STORM, attack=10, accuracy=95, frequency=10)
__DLAO.describeAttack(AttackEnum.EVICTION_NOTICE, attack=14, accuracy=80, frequency=20)
__DLAO.describeAttack(AttackEnum.QUAKE, attack=10, accuracy=75, frequency=30)
__DLAO.describeAttack(AttackEnum.TREMOR, attack=8, accuracy=85, frequency=20)
__DLAO.describeAttack(AttackEnum.INK_DRAIN, attack=0, accuracy=0, frequency=0)
__DLAO.setHpPerLevel({7: 275})
__DLAO.setBounty({CogBountyTypes.Gumballs: 8, CogBountyTypes.Jellybeans: 125, CogBountyTypes.Experience: 800})
__DLAO.setMovieAttributes(overrideDeaths=True, extendMovieTime=30)
__DLAO.makeHidden()
__DLAO.test()

__DOPR = SuitDefinition('dopr', SELLBOT, 8.25, miniboss=True)
__DOPR.defineLevelRange(10)
__DOPR.defineParts(6.25, VBase4(0.95, 0.75, 0.95, 1), ['phase_9/models/char/suits/ttcc_ene_dopr-zero'],
                   ['phase_9/models/char/suits/ttcc_ene_dopr-zero'], suitType=SUIT_C, tieType=TIE_SKINNY,
                   bodyTex=TEX_SALES, custom=True)
__DOPR.describeAttack(AttackEnum.SCHMOOZE, attack=20, accuracy=75, frequency=25)
__DOPR.describeAttack(AttackEnum.BRAIN_STORM, attack=16, accuracy=95, frequency=25)
__DOPR.describeAttack(AttackEnum.GUILT_TRIP, attack=18, accuracy=80, frequency=25)
__DOPR.describeAttack(AttackEnum.SYNERGY, attack=14, accuracy=85, frequency=25)
__DOPR.describeAttack(AttackEnum.GLOWER_POWER, attack=11, accuracy=65)
__DOPR.setPassives(STATUS_EFFECTS=SEE.EFFECT_AMBUSH_MARKETING)
__DOPR.setHpPerLevel({10: 1200})
__DOPR.setBounty({CogBountyTypes.Gumballs: 10, CogBountyTypes.Jellybeans: 200, CogBountyTypes.Experience: 1000})
__DOPR.makeAlwaysSkelecog()
__DOPR.setMovieAttributes(overrideDeaths=True, extendMovieTime=40)
__DOPR.makeHidden()
__DOPR.test()

__DERRICK_HAND = SuitDefinition('derrhand', BOSSBOT, 8.85, miniboss=True)
__DERRICK_HAND.defineLevelRange(25)
__DERRICK_HAND.defineParts(7.0, VBase4(90/255, 85/255, 82/255, 1), ['phase_12/models/char/suits/ttcc_ene_derrickhand-zero'],
                           ['phase_12/models/char/suits/ttcc_ene_derrickhand_skele-zero'], suitType=SUIT_A,
                           custom=True, tieType=TIE_BROAD, bodyTex=TEX_CORP)
__DERRICK_HAND.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=25, accuracy=75, frequency=20)
__DERRICK_HAND.describeAttack(AttackEnum.LIQUIDATE, attack=24, accuracy=95, frequency=10)
__DERRICK_HAND.describeAttack(AttackEnum.WITHDRAWAL, attack=27, accuracy=80, frequency=20)
__DERRICK_HAND.describeAttack(AttackEnum.QUAKE, attack=23, accuracy=75, frequency=30)
__DERRICK_HAND.describeAttack(AttackEnum.FREEZE_ASSETS, attack=30, accuracy=85, frequency=20)
__DERRICK_HAND.describeAttack(AttackEnum.REFINEMENT_DIRECTORS)
__DERRICK_HAND.setHpPerLevel({25: 1100})
# Directors bounties are split between DOPA, DoLD, and Derrickhand for a total of:
# 16 Gumballs, 800 beans, and 1500 experience.
__DERRICK_HAND.setBounty({CogBountyTypes.Gumballs: 10, CogBountyTypes.Jellybeans: 275, CogBountyTypes.Experience: 500})
__DERRICK_HAND.makeHidden()
__DERRICK_HAND.test()

__DOLD = SuitDefinition('dold', BOARDBOT, 9.9, miniboss=True)
__DOLD.defineLevelRange(25)
__DOLD.defineParts(7.5, VBase4(231/255, 94/255, 16/255, 1), ['phase_14/models/char/suits/ttcc_ene_dold-zero'], [SKELE_HEAD_A], suitType=SUIT_A,
                   tieType=TIE_BROAD, bodyTex=TEX_BOARD, custom=True)
__DOLD.describeAttack(AttackEnum.RE_ORG, attack=32, accuracy=75, frequency=20)
__DOLD.describeAttack(AttackEnum.RED_TAPE, attack=30, accuracy=95, frequency=10)
__DOLD.describeAttack(AttackEnum.EVICTION_NOTICE, attack=31, accuracy=80, frequency=20)
__DOLD.describeAttack(AttackEnum.QUAKE, attack=24, accuracy=75, frequency=30)
__DOLD.describeAttack(AttackEnum.AFTERSHOCK, attack=22, accuracy=85, frequency=20)
__DOLD.describeAttack(AttackEnum.INK_DRAIN_DIRECTORS)
__DOLD.setHpPerLevel({25: 1250})
# Directors bounties are split between DOPA, DoLD, and Derrickhand for a total of:
# 16 Gumballs, 800 beans, and 1500 experience.
__DOLD.setBounty({CogBountyTypes.Gumballs: 10, CogBountyTypes.Jellybeans: 275, CogBountyTypes.Experience: 500})
__DOLD.makeHidden()
__DOLD.test()

__DOPA = SuitDefinition('dopa', SELLBOT, 10.5, miniboss=True)
__DOPA.defineLevelRange(30)
__DOPA.defineParts(7.25, VBase4(0.95, 0.75, 0.95, 1), ['phase_9/models/char/suits/ttcc_ene_dopa-zero'],
                   ['phase_9/models/char/suits/ttcc_ene_dopa-zero'], suitType=SUIT_C, tieType=TIE_SKINNY,
                   bodyTex=TEX_SALES, custom=True)
__DOPA.describeAttack(AttackEnum.SCHMOOZE, attack=34, accuracy=75, frequency=25)
__DOPA.describeAttack(AttackEnum.BRAIN_STORM, attack=31, accuracy=95, frequency=25)
__DOPA.describeAttack(AttackEnum.GUILT_TRIP, attack=23, accuracy=80, frequency=25)
__DOPA.describeAttack(AttackEnum.SYNERGY, attack=25, accuracy=75, frequency=25)
__DOPA.describeAttack(AttackEnum.OVERWHELMING_AUTHORITY)
__DOPA.describeAttack(AttackEnum.GLOWER_POWER, attack=22, accuracy=70)
__DOPA.describeAttack(AttackEnum.DISRUPTIVE_ADVERTISEMENT)
__DOPA.describeAttack(AttackEnum.MULTI_LEVEL_MARKETING)
__DOPA.setHpPerLevel({30: 1500})
# Directors bounties are split between DOPA, DoLD, and Derrickhand for a total of:
# 16 Gumballs, 800 beans, and 1500 experience.
__DOPA.setBounty({CogBountyTypes.Gumballs: 10, CogBountyTypes.Jellybeans: 275, CogBountyTypes.Experience: 500})
__DOPA.makeAlwaysSkelecog()
__DOPA.makeHidden()
__DOPA.test()
# endregion

### EVENT MINIBOSSES ###
# region
__COUNT_ERCLAIM = SuitDefinition('count', LAWBOT, 8.0, miniboss=True)
__COUNT_ERCLAIM.defineLevelRange(10, 20)
__COUNT_ERCLAIM.defineParts(6.075, VBase4(0.95, 0.95, 1, 1),
                            ['phase_11/models/char/suits/ttcc_ene_counterclaim-zero'], [SKELE_HEAD_B],
                            suitType=SUIT_B, tieType=TIE_BOW,
                            bodyTex='phase_11/maps/ttcc_ene_suittex_count.png', custom=True)
__COUNT_ERCLAIM.describeAttack(AttackEnum.EVICTION_NOTICE,
                               attack=(12, 12, 18, 12, 24, 12, 30, 12, 36, 12, 42),
                               accuracy=75,
                               frequency=25)
__COUNT_ERCLAIM.describeAttack(AttackEnum.BRAIN_STORM,
                               attack=(10, 10, 16, 10, 22, 10, 28, 10, 34, 10, 40),
                               accuracy=75,
                               frequency=25)
__COUNT_ERCLAIM.describeAttack(AttackEnum.WITHDRAWAL,
                               attack=(16, 16, 24, 16, 32, 16, 40, 16, 48, 16, 54),
                               accuracy=95,
                               frequency=10)
__COUNT_ERCLAIM.describeAttack(AttackEnum.BITE,
                               attack=(14, 14, 21, 14, 28, 14, 35, 14, 42, 14, 49),
                               accuracy=(60, 75, 75, 80, 80, 85, 85, 90, 90, 95, 95),
                               frequency=15)
__COUNT_ERCLAIM.describeAttack(AttackEnum.LIQUIDATE,
                               attack=(16, 11, 24, 11, 32, 11, 40, 11, 48, 11, 56),
                               accuracy=(65, 50, 65, 50, 75, 50, 75, 50, 85, 50, 85),
                               frequency=25)
__COUNT_ERCLAIM.describeAttack(AttackEnum.QUAKE,
                               attack=(12, 12, 16, 12, 20, 12, 24, 12, 29, 12, 34),
                               accuracy=80)
__COUNT_ERCLAIM.describeAttack(AttackEnum.LAFF_STEAL)
__COUNT_ERCLAIM.describeAttack(AttackEnum.RISE_FROM_THE_SCRAP)
__COUNT_ERCLAIM.describeAttack(AttackEnum.SACRIFICE)
__COUNT_ERCLAIM.describeAttack(AttackEnum.SCOPE_CREEP)
__COUNT_ERCLAIM.setAttackBehavior(SEE.EFFECT_COUNT_ERCLAIM)
__COUNT_ERCLAIM.setPassives(HP_MULT=(2.12988, 2.12988 * 1.8), DEFENSE_BOOST=5)
__COUNT_ERCLAIM.setStreetAttributes(joinChanceOverride=80, isStubborn=True, maxCogOnStreet=1)
__COUNT_ERCLAIM.setReviveAttributes(hpMult=0.6, dmgMult=1.4)
__COUNT_ERCLAIM.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__COUNT_ERCLAIM.makeHidden()
__COUNT_ERCLAIM.test()

__COUNT_ERFIT = SuitDefinition('erfit', CASHBOT, 10.25, miniboss=True, nerfDamageForExe=True)
__COUNT_ERFIT.defineLevelRange(10, 20)
__COUNT_ERFIT.defineParts(7.35, VBase4(0.95, 1.0, 0.95, 1.0),
                          ['phase_11/models/char/suits/ttcc_ene_counterclaim-zero'], [SKELE_HEAD_A],
                          suitType=SUIT_A, tieType=TIE_BROAD,
                          bodyTex='phase_11/maps/ttcc_ene_suittex_count.png',
                          textureOverride='phase_10/maps/ttcc_ene_counterfit.png', custom=True)
__COUNT_ERFIT.describeAttack(AttackEnum.BOUNCE_CHECK, attack=(12, 41), accuracy=(80, 90), frequency=15)
__COUNT_ERFIT.describeAttack(AttackEnum.FREEZE_ASSETS, attack=(8, 36), accuracy=(75, 95), frequency=20)
__COUNT_ERFIT.describeAttack(AttackEnum.FINGER_WAG, attack=(12, 44), accuracy=(78, 93), frequency=50)
__COUNT_ERFIT.describeAttack(AttackEnum.SYNERGY, attack=(10, 39), accuracy=(70, 90), frequency=15)
__COUNT_ERFIT.describeAttack(AttackEnum.HYDRATION_CHECK, attack=(10, 35), accuracy=95)
__COUNT_ERFIT.describeAttack(AttackEnum.QUAKE, attack=25, accuracy=90)
__COUNT_ERFIT.describeAttack(AttackEnum.PROTOON_SHAKE)
__COUNT_ERFIT.describeAttack(AttackEnum.PERSONAL_TRAINER)
__COUNT_ERFIT.describeAttack(AttackEnum.GAINS_FROM_THE_SCRAP)
__COUNT_ERFIT.setAttackBehavior(SEE.EFFECT_COUNT_ERFIT)
__COUNT_ERFIT.setReviveAttributes(hpMult=2.0286743, dmgMult=1.4)
__COUNT_ERFIT.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__COUNT_ERFIT.setStreetAttributes(joinChanceOverride=100)  # useful for debug because I am in pain.
__COUNT_ERFIT.setHpPerLevel({
    10: 777, 12: 1477, 14: 2177,
    16: 3777, 18: 5777, 20: 7777,
})
__COUNT_ERFIT.makeHidden()
__COUNT_ERFIT.test()

__REDD = SuitDefinition('redd', LAWBOT, 6.17, miniboss=True)
__REDD.defineLevelRange(10, 20)
__REDD.defineParts(4.375, VBase4(0.95, 0.95, 1, 1), ['phase_11/models/char/suits/ttcc_ene_redd-zero'], [SKELE_HEAD_B], suitType=SUIT_B,
                   tieType=TIE_BOW, bodyTex=TEX_LEGAL, custom=True)
__REDD.describeAttack(AttackEnum.SHAKE,
                      attack=(8, 8, 13, 8, 18, 8, 23, 8, 28, 8, 33),
                      accuracy=(65, 65, 70, 65, 75, 65, 80, 65, 85, 65, 90),
                      frequency=15)
__REDD.describeAttack(AttackEnum.GUILT_TRIP,
                      attack=(12, 12, 16, 12, 20, 12, 24, 12, 28, 12, 32),
                      accuracy=(60, 60, 68, 60, 74, 60, 80, 60, 88, 60, 95),
                      frequency=20)
__REDD.describeAttack(AttackEnum.WRITE_OFF,
                      attack=(8, 8, 14, 8, 20, 8, 26, 8, 32, 8, 38),
                      accuracy=(80, 80, 83, 80, 86, 80, 89, 80, 92, 80, 95),
                      frequency=25)
__REDD.describeAttack(AttackEnum.DOUBLE_TALK,
                      attack=(9, 9, 16, 9, 23, 9, 30, 9, 37, 9, 44),
                      accuracy=(75, 75, 78, 75, 81, 75, 84, 75, 87, 75, 90),
                      frequency=25)
__REDD.describeAttack(AttackEnum.LIQUIDATE,
                      attack=(8, 8, 16, 8, 24, 8, 32, 8, 40, 8, 48),
                      accuracy=(80, 80, 83, 80, 86, 80, 89, 80, 92, 80, 95),
                      frequency=15)
__REDD.setPassives(LURE_RESISTANCE=0, COMBO_EFFECTIVENESS=0.5, KNOCKBACK_EFFECTIVENESS=0.5)
__REDD.test()

# __WITNESS_STANDIN = SuitDefinition('standin', LAWBOT, 8.69, miniboss=True)
# __WITNESS_STANDIN.defineLevelRange(50)
# __WITNESS_STANDIN.defineParts(7.0, VBase4(0.75, 0.75, 0.95, 1), ['skelecog'], suitType=SUIT_A, custom=True)
# __WITNESS_STANDIN.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=24, accuracy=90, frequency=20)
# __WITNESS_STANDIN.describeAttack(AttackEnum.QUAKE, attack=29, accuracy=60, frequency=20)
# __WITNESS_STANDIN.describeAttack(AttackEnum.EVICTION_NOTICE, attack=28, accuracy=95, frequency=20)
# __WITNESS_STANDIN.describeAttack(AttackEnum.SPIN, attack=27, accuracy=75, frequency=15)
# __WITNESS_STANDIN.describeAttack(AttackEnum.RED_TAPE, attack=23, accuracy=85, frequency=25)
# __WITNESS_STANDIN.describeAttack(AttackEnum.OBJECTION)
# __WITNESS_STANDIN.describeAttack(AttackEnum.OBJECTION_SUSTAINED, attack=20, accuracy=100)
# __WITNESS_STANDIN.describeAttack(AttackEnum.OBJECTION_OVERRULED)
# __WITNESS_STANDIN.test()

__JUDY = SuitDefinition('judy', LAWBOT, 5.41, isFemale=True)
__JUDY.defineLevelRange(20)
__JUDY.defineParts(4.5, VBase4(0.424, 0.494, 0.749, 1.0), ['phase_11/models/char/suits/ttcc_ene_judy-zero'], [SKELE_HEAD_C],
                   suitType=SUIT_C, tieType=TIE_BOW, bodyTex=TEX_LEGAL, custom=True)
__JUDY.describeAttack(AttackEnum.WITHDRAWAL, attack=1, accuracy=95, frequency=40)
__JUDY.describeAttack(AttackEnum.GUILT_TRIP, attack=1, accuracy=95, frequency=30)
__JUDY.describeAttack(AttackEnum.LIQUIDATE, attack=1, accuracy=95, frequency=30)
__JUDY.test()
# endregion

LitigationLootChance = 0.02
LitigationLootPity = 0.001

### OVERCLOCKED MINIBOSSES ###
# region
__LITIGATOR = SuitDefinition('lgator', LAWBOT, 9.25, miniboss=True)
__LITIGATOR.defineLevelRange(40)
__LITIGATOR.defineParts(7.25, VBase4(0.388, 0.443, 0.639, 1.0), ['phase_11/models/char/suits/ttcc_ene_litigator-zero'],
                        [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BOW, bodyTex=TEX_LEGAL, custom=True)
__LITIGATOR.describeAttack(AttackEnum.POWER_TRIP, attack=32, accuracy=75, frequency=20)
__LITIGATOR.describeAttack(AttackEnum.CHOMP, attack=36, accuracy=85, frequency=40)
__LITIGATOR.describeAttack(AttackEnum.FIRED, attack=40, accuracy=75, frequency=15)
__LITIGATOR.describeAttack(AttackEnum.EVIL_EYE, attack=30, accuracy=95, frequency=10)
__LITIGATOR.describeAttack(AttackEnum.THROW_BOOK, attack=34, accuracy=90, frequency=15)
__LITIGATOR.describeAttack(AttackEnum.BAYOU_BASH)
__LITIGATOR.describeAttack(AttackEnum.BAYOU_BELLOW)
__LITIGATOR.describeAttack(AttackEnum.SNAP, attack=25, accuracy=100)
__LITIGATOR.describeAttack(AttackEnum.SNAP_RETALIATE, attack=30, accuracy=100)
__LITIGATOR.setPassives(FORCED_DEFENSE=70, LURE_RESISTANCE=2)
__LITIGATOR.setAttackBehavior(SEE.EFFECT_LITIGATOR_MANAGER)
__LITIGATOR.setHpPerLevel({40: 4600})
__LITIGATOR.setBounty({CogBountyTypes.Gumballs: 15, CogBountyTypes.Jellybeans: 150, CogBountyTypes.Experience: 500, 'group': CogBountyGroups.LitigationTeam})
__LITIGATOR.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Litigator), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__LITIGATOR.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(ClothingTopItemType.LawbotSuitTop), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__LITIGATOR.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(ClothingBottomItemType.Shorts_Suit_Lawbot), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__LITIGATOR.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(2), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__LITIGATOR.makeHidden()
__LITIGATOR.test()

__STENOGRAPHER = SuitDefinition('stenog', LAWBOT, 10, miniboss=True, isFemale=True)
__STENOGRAPHER.defineLevelRange(35)
__STENOGRAPHER.defineParts(7.0, VBase4(0.357, 0.408, 0.573, 1.0), ['phase_11/models/char/suits/ttcc_ene_stenographer-zero'],
                           [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BOW, bodyTex=TEX_LEGAL, custom=True)
__STENOGRAPHER.describeAttack(AttackEnum.MUMBO_JUMBO, attack=29, accuracy=95, frequency=30)
__STENOGRAPHER.describeAttack(AttackEnum.FILIBUSTER, attack=32, accuracy=90, frequency=25)
__STENOGRAPHER.describeAttack(AttackEnum.BUZZ_WORD, attack=30, accuracy=90, frequency=20)
__STENOGRAPHER.describeAttack(AttackEnum.POUND_KEY, attack=38, accuracy=85, frequency=15)
__STENOGRAPHER.describeAttack(AttackEnum.JARGON, attack=25, accuracy=95, frequency=10)
__STENOGRAPHER.describeAttack(AttackEnum.COURT_SANCTION, attack=25, accuracy=100)
__STENOGRAPHER.describeAttack(AttackEnum.COURT_SANCTION_RETALIATE, attack=25, accuracy=100)
__STENOGRAPHER.describeAttack(AttackEnum.COURT_RECORD)
__STENOGRAPHER.describeAttack(AttackEnum.COURT_COSTS, accuracy=100)
__STENOGRAPHER.setPassives(FORCED_DEFENSE=70, LURE_RESISTANCE=2)
__STENOGRAPHER.setAttackBehavior(SEE.EFFECT_STENOGRAPHER_MANAGER)
__STENOGRAPHER.setHpPerLevel({35: 4500})
__STENOGRAPHER.setBounty({CogBountyTypes.Gumballs: 15, CogBountyTypes.Jellybeans: 150, CogBountyTypes.Experience: 500, 'group': CogBountyGroups.LitigationTeam})
__STENOGRAPHER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Stenographer), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__STENOGRAPHER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hairbow_Diploma), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__STENOGRAPHER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_Gavel), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__STENOGRAPHER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(2), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__STENOGRAPHER.makeHidden()
__STENOGRAPHER.test()

__CASE_MANAGER = SuitDefinition('caseman', LAWBOT, 8.25, miniboss=True)
__CASE_MANAGER.defineLevelRange(35)
__CASE_MANAGER.defineParts(6.75, VBase4(0.4705, 0.334, 0.275, 1), ['phase_11/models/char/suits/ttcc_ene_casemanager-zero'],
                           [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_BOW, bodyTex=TEX_LEGAL, custom=True)
__CASE_MANAGER.describeAttack(AttackEnum.GUILT_TRIP, attack=26, accuracy=90, frequency=30)
__CASE_MANAGER.describeAttack(AttackEnum.FOUNTAIN_PEN, attack=28, accuracy=90, frequency=35)
__CASE_MANAGER.describeAttack(AttackEnum.EVICTION_NOTICE, attack=32, accuracy=85, frequency=15)
__CASE_MANAGER.describeAttack(AttackEnum.RESTRAINING_ORDER, attack=33, accuracy=90, frequency=10)
__CASE_MANAGER.describeAttack(AttackEnum.ROLODEX, attack=30, accuracy=95, frequency=10)
__CASE_MANAGER.describeAttack(AttackEnum.INSURANCE_PLAN)
__CASE_MANAGER.describeAttack(AttackEnum.LEGAL_BINDINGS)
__CASE_MANAGER.setPassives(FORCED_DEFENSE=70, LURE_RESISTANCE=2)
__CASE_MANAGER.setAttackBehavior(SEE.EFFECT_CASE_MANAGER_MANAGER)
__CASE_MANAGER.setHpPerLevel({35: 4250})
__CASE_MANAGER.setBounty({CogBountyTypes.Gumballs: 15, CogBountyTypes.Jellybeans: 150, CogBountyTypes.Experience: 500, 'group': CogBountyGroups.LitigationTeam})
__CASE_MANAGER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.CaseManager), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__CASE_MANAGER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_Lawbook), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__CASE_MANAGER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(NeckItemType.CjTie), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__CASE_MANAGER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(2), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__CASE_MANAGER.makeHidden()
__CASE_MANAGER.test()

__SCAPEGOAT = SuitDefinition('sgoat', LAWBOT, 7.5, miniboss=True)
__SCAPEGOAT.defineLevelRange(30, 30)
__SCAPEGOAT.defineParts(5.325, VBase4(0.3, 0.3, 0.45, 1), ['phase_11/models/char/suits/ttcc_ene_scapegoat-zero'],
                        [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_BOW, bodyTex=TEX_LEGAL, custom=True)
__SCAPEGOAT.describeAttack(AttackEnum.TREMOR, attack=25, accuracy=95, frequency=15)
__SCAPEGOAT.describeAttack(AttackEnum.GUILT_TRIP, attack=28, accuracy=80, frequency=15)
__SCAPEGOAT.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=26, accuracy=90, frequency=10)
__SCAPEGOAT.describeAttack(AttackEnum.BITE, attack=32, accuracy=90, frequency=30)
__SCAPEGOAT.describeAttack(AttackEnum.FINGER_WAG, attack=30, accuracy=95, frequency=30)
__SCAPEGOAT.describeAttack(AttackEnum.SCAPEGOAT_ENRAGED)
__SCAPEGOAT.describeAttack(AttackEnum.SCAPEGOAT_DEFENSE)
__SCAPEGOAT.setPassives(FORCED_DEFENSE=75, STATUS_EFFECTS=SEE.EFFECT_SCAPEGOAT_RAGE, LURE_RESISTANCE=2)
__SCAPEGOAT.setAttackBehavior(SEE.EFFECT_SCAPEGOAT_MANAGER)
__SCAPEGOAT.setHpPerLevel({30: 4800})
__SCAPEGOAT.setBounty({CogBountyTypes.Gumballs: 15, CogBountyTypes.Jellybeans: 150, CogBountyTypes.Experience: 500, 'group': CogBountyGroups.LitigationTeam})
__SCAPEGOAT.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Scapegoat), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__SCAPEGOAT.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_Backstabber), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__SCAPEGOAT.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(NeckItemType.LawBowtie), chance=LitigationLootChance, chancePerPity=LitigationLootPity, enemyName=__SCAPEGOAT.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(2), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__SCAPEGOAT.makeHidden()
__SCAPEGOAT.test()
# endregion

### STREET MERCS ###
# region
__DUCK_SHUFFLER = SuitDefinition('duckshfl', CASHBOT, 6.6, miniboss=True, isMerc=True, nerfDamageForExe=True)
__DUCK_SHUFFLER.defineLevelRange(5)
__DUCK_SHUFFLER.defineParts(4.75, VBase4(0.714, 0.118, 0.055, 1.0),
                            ['phase_10/models/char/suits/ttcc_ene_duckshuffler-zero'], [SKELE_HEAD_B], suitType=SUIT_B,
                            tieType=TIE_SKINNY, bodyTex='phase_10/maps/ttcc_ene_suittex_duckshfl.png')
__DUCK_SHUFFLER.describeAttack(AttackEnum.SPIN,          attack=5, accuracy=90,  frequency=100)
__DUCK_SHUFFLER.describeAttack(AttackEnum.WAGER_DUCKS,   attack=4, accuracy=100, frequency=0)
__DUCK_SHUFFLER.describeAttack(AttackEnum.WAGER_SEVENS,  attack=0, accuracy=100, frequency=0)
__DUCK_SHUFFLER.describeAttack(AttackEnum.WAGER_BEANS,   attack=0, accuracy=100, frequency=0)
__DUCK_SHUFFLER.describeAttack(AttackEnum.WAGER_BAR,     attack=3, accuracy=100, frequency=0)
__DUCK_SHUFFLER.describeAttack(AttackEnum.WAGER_BUST,    attack=0, accuracy=100, frequency=0)
__DUCK_SHUFFLER.setPassives(LURE_RESISTANCE=1, FORCED_DEFENSE=10)
__DUCK_SHUFFLER.setAttackBehavior(SEE.EFFECT_MANAGER_DUCK_SHUFFLER)
__DUCK_SHUFFLER.setHpPerLevel({5: 200})
__DUCK_SHUFFLER.setBounty({CogBountyTypes.Gumballs: 10, CogBountyTypes.Jellybeans: 100, CogBountyTypes.Experience: 150})
__DUCK_SHUFFLER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.DuckShuffler), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__DUCK_SHUFFLER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_MoneyBag), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__DUCK_SHUFFLER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(2), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__DUCK_SHUFFLER.setStreetAttributes(joinChanceOverride=25, isStubborn=True, maxCogOnStreet=1, canJoinBattles=False)
__DUCK_SHUFFLER.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__DUCK_SHUFFLER.test()

__DEEP_DIVER = SuitDefinition('ddiver', BOARDBOT, 8.8, miniboss=True, isMerc=True, nerfDamageForExe=True)
__DEEP_DIVER.defineLevelRange(7)
__DEEP_DIVER.defineParts(7.0, VBase4(0.635, 0.615, 0.651, 1), ['phase_14/models/char/suits/ttcc_ene_deepdiver-zero'],
                         [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_NONE, bodyTex='phase_14/maps/ttcc_ene_suittex_ddiver.png')
__DEEP_DIVER.describeAttack(AttackEnum.WATERCOOLER_DOUBLE, attack=7, accuracy=75, frequency=100)
__DEEP_DIVER.describeAttack(AttackEnum.DIVE)
__DEEP_DIVER.describeAttack(AttackEnum.SINK_OR_SWIM,       attack=8, accuracy=80, frequency=0)
__DEEP_DIVER.setPassives(LURE_RESISTANCE=1, FORCED_DEFENSE=20)
__DEEP_DIVER.setAttackBehavior(SEE.EFFECT_MANAGER_DEEP_DIVER)
__DEEP_DIVER.setStreetAttributes(joinChanceOverride=60, isStubborn=True, maxCogOnStreet=1, canJoinBattles=False)
__DEEP_DIVER.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__DEEP_DIVER.setHpPerLevel({7: 400})
__DEEP_DIVER.setBounty({CogBountyTypes.Gumballs: 12, CogBountyTypes.Jellybeans: 200, CogBountyTypes.Experience: 500})
__DEEP_DIVER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.DeepDiver), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__DEEP_DIVER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(ShoeItemType.DiverBoots), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__DEEP_DIVER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(2), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__DEEP_DIVER.test()

__GATEKEEPER = SuitDefinition('gatekeep', BOARDBOT, 6.7, miniboss=True, isMerc=True, nerfDamageForExe=True)
__GATEKEEPER.defineLevelRange(10)
__GATEKEEPER.defineParts(5.0, VBase4(0.345, 0.345, 0.345, 1), ['phase_14/models/char/suits/ttcc_ene_gatekeeper-zero'], [SKELE_HEAD_A],
                         suitType=SUIT_A, tieType=TIE_NONE, bodyTex='phase_14/maps/ttcc_ene_suittex_gatekeep.png')
__GATEKEEPER.describeAttack(AttackEnum.CANNED,     attack=12, accuracy=95, frequency=20)
__GATEKEEPER.describeAttack(AttackEnum.FIRED,      attack=15, accuracy=85, frequency=30)
__GATEKEEPER.describeAttack(AttackEnum.QUAKE,      attack=11, accuracy=85, frequency=15)
__GATEKEEPER.describeAttack(AttackEnum.RED_TAPE,   attack=13, accuracy=90, frequency=35)
__GATEKEEPER.setPassives(LURE_RESISTANCE=1, FORCED_DEFENSE=30)
__GATEKEEPER.setAttackBehavior(SEE.EFFECT_MANAGER_GATEKEEPER)
__GATEKEEPER.setStreetAttributes(joinChanceOverride=80, isStubborn=True, maxCogOnStreet=1, canJoinBattles=False)
__GATEKEEPER.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__GATEKEEPER.setHpPerLevel({10: 1200})
__GATEKEEPER.setBounty({CogBountyTypes.Gumballs: 14, CogBountyTypes.Jellybeans: 350, CogBountyTypes.Experience: 1000})
__GATEKEEPER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Gatekeeper), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__GATEKEEPER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_Shield), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__GATEKEEPER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=LootContainer([
                InventoryLoot(ClothingTopItemType.ArmoredChestplate),
                InventoryLoot(ClothingBottomItemType.Shorts_Armor),
                InventoryLoot(ClothingBottomItemType.Skirt_Armor),
            ], friendlyName='Armored Outfit'), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__GATEKEEPER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(ShoeItemType.ArmoredGreaves), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__GATEKEEPER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(3), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__GATEKEEPER.test()

__BELLRINGER = SuitDefinition('bellring', SELLBOT, 6.7, miniboss=True, isMerc=True, nerfDamageForExe=True)
__BELLRINGER.defineLevelRange(13)
__BELLRINGER.defineParts(4.75, VBase4(168/255, 127/255, 63/255, 1), ['phase_9/models/char/suits/ttcc_ene_bellringer-zero'], [SKELE_HEAD_B],
                         suitType=SUIT_B, tieType=TIE_NONE, bodyTex='phase_9/maps/ttcc_ene_suittex_bellring.png',
                         bodyModelType=BodyModelType.HighCollar)
__BELLRINGER.describeAttack(AttackEnum.HANG_UP,    attack=15, accuracy=70, frequency=20)
__BELLRINGER.describeAttack(AttackEnum.POUND_KEY,  attack=13, accuracy=90, frequency=30)
__BELLRINGER.describeAttack(AttackEnum.QUAKE,      attack=10, accuracy=75, frequency=20)
__BELLRINGER.describeAttack(AttackEnum.ROLODEX,    attack=14, accuracy=80, frequency=30)
__BELLRINGER.describeAttack(AttackEnum.HEALING_BELL)
__BELLRINGER.setPassives(LURE_RESISTANCE=1, FORCED_DEFENSE=40)
__BELLRINGER.setAttackBehavior(SEE.EFFECT_MANAGER_BELLRINGER)
__BELLRINGER.setStreetAttributes(joinChanceOverride=80, isStubborn=True, maxCogOnStreet=1, canJoinBattles=False)
__BELLRINGER.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__BELLRINGER.setHpPerLevel({13: 1800})
__BELLRINGER.setBounty({CogBountyTypes.Gumballs: 17, CogBountyTypes.Jellybeans: 500, CogBountyTypes.Experience: 1250})
__BELLRINGER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Bellringer), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__BELLRINGER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(NeckItemType.NeckCowbell), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__BELLRINGER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(3), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__BELLRINGER.test()

__MOUTHPIECE = SuitDefinition('mouthp', LAWBOT, 6.7, miniboss=True, isMerc=True, nerfDamageForExe=True)
__MOUTHPIECE.defineLevelRange(16)
__MOUTHPIECE.defineParts(4.77, VBase4(0.349, 0.416, 0.51, 1),
                         ['phase_11/models/char/suits/ttcc_ene_mouthpiece-zero'], [SKELE_HEAD_B], suitType=SUIT_B,
                         tieType=TIE_BOW, bodyTex='phase_11/maps/ttcc_ene_suittex_mouthp.png')
__MOUTHPIECE.describeAttack(AttackEnum.HANG_UP,        attack=16, accuracy=90, frequency=30)
__MOUTHPIECE.describeAttack(AttackEnum.POUND_KEY,      attack=20, accuracy=80, frequency=35)
__MOUTHPIECE.describeAttack(AttackEnum.ROLODEX,        attack=15, accuracy=90, frequency=00)
__MOUTHPIECE.describeAttack(AttackEnum.FINGER_WAG,     attack=18, accuracy=85, frequency=35)
__MOUTHPIECE.describeAttack(AttackEnum.RED_THREAD)
__MOUTHPIECE.setPassives(STATUS_EFFECT=[SEE.EFFECT_MOUTHPIECE_EXTRA_ATTACK], FORCED_DEFENSE=50)
__MOUTHPIECE.setAttackBehavior(SEE.EFFECT_MANAGER_MOUTHPIECE)
__MOUTHPIECE.setStreetAttributes(joinChanceOverride=80, isStubborn=True, maxCogOnStreet=1, battleCogCap=5, canJoinBattles=False)
__MOUTHPIECE.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__MOUTHPIECE.setHpPerLevel({16: 2200})
__MOUTHPIECE.setBounty({CogBountyTypes.Gumballs: 20, CogBountyTypes.Jellybeans: 650, CogBountyTypes.Experience: 1500})
__MOUTHPIECE.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Mouthpiece), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__MOUTHPIECE.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(GlassesItemType.Glasses_Mouthpiece), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__MOUTHPIECE.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(4), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__MOUTHPIECE.test()

__FIRESTARTER = SuitDefinition('fires', BOSSBOT, 8.7, miniboss=True, isMerc=True, nerfDamageForExe=True)
__FIRESTARTER.defineLevelRange(20)
__FIRESTARTER.defineParts(6.5, VBase4(0.769, 0.196, 0.055, 1.0),
                          ['phase_12/models/char/suits/ttcc_ene_firestarter-zero'], [SKELE_HEAD_A], suitType=SUIT_A,
                          tieType=TIE_BROAD, bodyTex='phase_12/maps/ttcc_ene_suittex_fires.png')
__FIRESTARTER.describeAttack(AttackEnum.HOT_AIR,                 attack=13, accuracy=85, frequency=30)
__FIRESTARTER.describeAttack(AttackEnum.FIRED,                   attack=15, accuracy=90, frequency=30)
__FIRESTARTER.describeAttack(AttackEnum.POWER_TRIP,              attack=13, accuracy=80, frequency=25)
__FIRESTARTER.describeAttack(AttackEnum.CIGAR_SMOKE_FIRESTARTER, attack=12, accuracy=85, frequency=15)
__FIRESTARTER.describeAttack(AttackEnum.BACKBURNER)
__FIRESTARTER.setPassives(LURE_RESISTANCE=1, FORCED_DEFENSE=60)
__FIRESTARTER.setStreetAttributes(joinChanceOverride=80, isStubborn=True, maxCogOnStreet=1, canJoinBattles=False)
__FIRESTARTER.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__FIRESTARTER.setHpPerLevel({20: 3350})
__FIRESTARTER.setAttackBehavior(SEE.EFFECT_MANAGER_FIRESTARTER)
__FIRESTARTER.setBounty({CogBountyTypes.Gumballs: 24, CogBountyTypes.Jellybeans: 825, CogBountyTypes.Experience: 1750})
__FIRESTARTER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Firestarter), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__FIRESTARTER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_Firestarter), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__FIRESTARTER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_Firestoker), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__FIRESTARTER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(4), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__FIRESTARTER.test()

__TREEKILLER = SuitDefinition('treek', CASHBOT, 6.7, miniboss=True, isMerc=True, nerfDamageForExe=True)
__TREEKILLER.defineLevelRange(24)
__TREEKILLER.defineParts(5.3, VBase4(160/255, 195/255, 155/255, 1), ['phase_10/models/char/suits/ttcc_ene_treekiller-zero'], [SKELE_HEAD_C], suitType=SUIT_C,
                         tieType=TIE_BROAD, bodyTex='phase_10/maps/ttcc_ene_suittex_treek.png')
__TREEKILLER.describeAttack(AttackEnum.MARKET_CRASH,     attack=29, accuracy=90, frequency=15)
__TREEKILLER.describeAttack(AttackEnum.SHRED,            attack=32, accuracy=90, frequency=35)
__TREEKILLER.describeAttack(AttackEnum.GUILT_TRIP,       attack=24, accuracy=80, frequency=25)
__TREEKILLER.describeAttack(AttackEnum.FIRED,            attack=31, accuracy=80, frequency=25)
__TREEKILLER.describeAttack(AttackEnum.PEELING_THE_BARK, attack=8,  accuracy=100)
__TREEKILLER.describeAttack(AttackEnum.WOODCHIPPER)
__TREEKILLER.setPassives(LURE_RESISTANCE=1, FORCED_DEFENSE=70)
__TREEKILLER.setStreetAttributes(joinChanceOverride=80, isStubborn=True, maxCogOnStreet=1, canJoinBattles=False)
__TREEKILLER.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__TREEKILLER.setHpPerLevel({24: 3500})
__TREEKILLER.setBounty({CogBountyTypes.Gumballs: 26, CogBountyTypes.Jellybeans: 1000, CogBountyTypes.Experience: 2000})
__TREEKILLER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Treekiller), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__TREEKILLER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_Treekiller), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__TREEKILLER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(5), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__TREEKILLER.test()

__FEATHERBEDDER = SuitDefinition('fbed', BOSSBOT, 6.7, miniboss=True, isMerc=True, nerfDamageForExe=True)
__FEATHERBEDDER.defineLevelRange(30)
__FEATHERBEDDER.defineParts(5.5, VBase4(0.321, 0.212, 0.216, 1), ['phase_12/models/char/suits/ttcc_ene_featherbedder-zero'], [SKELE_HEAD_C], suitType=SUIT_C,
                            tieType=TIE_BROAD, bodyTex='phase_12/maps/ttcc_ene_suittex_fbed.png')
__FEATHERBEDDER.describeAttack(AttackEnum.LIQUIDATE,       attack=29, accuracy=85, frequency=10)
__FEATHERBEDDER.describeAttack(AttackEnum.PECKING_ORDER,   attack=31, accuracy=90, frequency=35)
__FEATHERBEDDER.describeAttack(AttackEnum.GUILT_TRIP,      attack=25, accuracy=90, frequency=30)
__FEATHERBEDDER.describeAttack(AttackEnum.SACKED,          attack=25, accuracy=85, frequency=25)
__FEATHERBEDDER.setPassives(LURE_RESISTANCE=2, FORCED_DEFENSE=75, STATUS_EFFECTS=SEE.EFFECT_PEACEFUL_SLUMBER)
__FEATHERBEDDER.setAttackBehavior(SEE.EFFECT_MANAGER_FEATHERBEDDER)
__FEATHERBEDDER.setStreetAttributes(joinChanceOverride=50, isStubborn=True, maxCogOnStreet=1,
                                    battleCogCap=5, canJoinBattles=False)
__FEATHERBEDDER.setMovieAttributes(overrideDeaths=True, extendMovieTime=20)
__FEATHERBEDDER.setHpPerLevel({30: 3800})
__FEATHERBEDDER.setBounty({CogBountyTypes.Gumballs: 30, CogBountyTypes.Jellybeans: 1350, CogBountyTypes.Experience: 2250})
__FEATHERBEDDER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Featherbedder), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__FEATHERBEDDER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_Featherbedder), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__FEATHERBEDDER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(5), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__FEATHERBEDDER.test()
# endregion

### INSTANCE MERCS ###
# region
__PRETHINKER = SuitDefinition('prethink', SELLBOT, 5.2, miniboss=True, isMerc=True, nerfDamageForExe=True)
__PRETHINKER.defineLevelRange(12)
__PRETHINKER.defineParts(3.75, VBase4(127/255, 112/255, 142/255, 1),
                         ['phase_9/models/char/suits/ttcc_ene_prethinker-zero'], [SKELE_HEAD_B], suitType=SUIT_B,
                         tieType=TIE_SKINNY, bodyTex='phase_9/maps/ttcc_ene_suittex_prethink.png')
__PRETHINKER.describeAttack(AttackEnum.BRAIN_STORM, attack=17, accuracy=85, frequency=20)
__PRETHINKER.describeAttack(AttackEnum.RE_ORG, attack=19, accuracy=70, frequency=25)
__PRETHINKER.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=14, accuracy=70, frequency=20)
__PRETHINKER.describeAttack(AttackEnum.BUZZ_WORD, attack=18, accuracy=75, frequency=35)
__PRETHINKER.describeAttack(AttackEnum.BRAIN_WAVE, attack=10, accuracy=100)
__PRETHINKER.describeAttack(AttackEnum.CASTLING)
__PRETHINKER.describeAttack(AttackEnum.FORWARD_THINKING)
__PRETHINKER.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, FORCED_DEFENSE=30, LURE_RESISTANCE=2)
__PRETHINKER.setMovieAttributes(overrideDeaths=True, extendMovieTime=50)
__PRETHINKER.setAttackBehavior(SEE.EFFECT_MANAGER_PRETHINKER)
__PRETHINKER.setHpPerLevel({12: 1000})
__PRETHINKER.setBounty({CogBountyTypes.Gumballs: 20, CogBountyTypes.Jellybeans: 80, CogBountyTypes.Experience: 125})
__PRETHINKER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Prethinker), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__PRETHINKER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_SmartCap), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__PRETHINKER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(3), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__PRETHINKER.makeHidden()
__PRETHINKER.test()

__PRETHINKER_JOCKEY = SuitDefinition('ptjockey', BOSSBOT, 7.1, departmentOverride='Brianbot')
__PRETHINKER_JOCKEY.defineLevelRange(1, 10)
__PRETHINKER_JOCKEY.defineParts(4.0, VBase4(0.95, 0.95, 0.95, 1), ['phase_3.5/models/schoolhouse/dummy/ttcc_ene_dummy-zero'], [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_BOW,
                     bodyTex='phase_3.5/maps/schoolhouse/dummy/ttcc_ene_suittex_ptjockey.png',
                     textureOverride='phase_3.5/maps/schoolhouse/dummy/ttcc_ene_djockey.png')
__PRETHINKER_JOCKEY.describeAttack(AttackEnum.POUND_KEY,  attack=7, accuracy=75, frequency=30)
__PRETHINKER_JOCKEY.describeAttack(AttackEnum.SHRED,      attack=7, accuracy=50, frequency=10)
__PRETHINKER_JOCKEY.describeAttack(AttackEnum.CLIPON_TIE, attack=7, accuracy=75, frequency=60)
__PRETHINKER_JOCKEY.describeAttack(AttackEnum.LIGHTS_ON)
__PRETHINKER_JOCKEY.makeHidden()
__PRETHINKER_JOCKEY.test()

__RAINMAKER = SuitDefinition('rainmake', LAWBOT, 6.7, miniboss=True, isMerc=True, nerfDamageForExe=True, isFemale=True)
__RAINMAKER.defineLevelRange(16)
__RAINMAKER.defineParts(5.0, ColorHelper.hexToPCol('a1a5b1'), ['phase_11/models/char/suits/ttcc_ene_rainmaker-zero'],
                        [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_NONE,
                        bodyTex="phase_11/maps/ttcc_ene_suittex_rainmake.png", custom=True,
                        bodyModelType=BodyModelType.LongCoat)
__RAINMAKER.describeAttack(AttackEnum.BRAIN_STORM,   attack=10, accuracy=80, frequency=30)
__RAINMAKER.describeAttack(AttackEnum.LIQUIDATE,     attack=12, accuracy=65, frequency=25)
__RAINMAKER.describeAttack(AttackEnum.POWER_TRIP,    attack=9, accuracy=70, frequency=20)
__RAINMAKER.describeAttack(AttackEnum.FREEZE_ASSETS, attack=11, accuracy=75, frequency=25)
__RAINMAKER.describeAttack(AttackEnum.WEATHER_MONSOON)
__RAINMAKER.describeAttack(AttackEnum.WEATHER_OIL_RAIN)
__RAINMAKER.describeAttack(AttackEnum.WEATHER_FOG)
__RAINMAKER.describeAttack(AttackEnum.WEATHER_HEAVY_RAIN)
__RAINMAKER.describeAttack(AttackEnum.WEATHER_STORM_CELL)
__RAINMAKER.describeAttack(AttackEnum.WEATHER_INVERSION)
__RAINMAKER.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, FORCED_DEFENSE=35, LURE_RESISTANCE=1, STATUS_EFFECTS=SEE.EFFECT_GENERIC_EXTRA_ATTACKS)
__RAINMAKER.setMovieAttributes(overrideDeaths=True, extendMovieTime=60)
__RAINMAKER.setAttackBehavior(SEE.EFFECT_MANAGER_RAINMAKER)
__RAINMAKER.setHpPerLevel({16: 2700})
__RAINMAKER.setBounty({CogBountyTypes.Gumballs: 24, CogBountyTypes.Jellybeans: 125, CogBountyTypes.Experience: 750})
__RAINMAKER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Rainmaker), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__RAINMAKER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Top_Raincloud), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__RAINMAKER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(3), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__RAINMAKER.makeHidden()
__RAINMAKER.test()

__WITCH_HUNTER = SuitDefinition('whunter', LAWBOT, 8.0, miniboss=True, isMerc=True, nerfDamageForExe=True)
__WITCH_HUNTER.defineLevelRange(20)
__WITCH_HUNTER.defineParts(6.2, VBase4(0.705882, 0.690196, 0.854902, 1),
                           ['phase_11/models/char/suits/ttcc_ene_witchhunter-zero'], [SKELE_HEAD_A], suitType=SUIT_A,
                           tieType=TIE_BOW, bodyTex="phase_11/maps/ttcc_ene_suittex_whunter.png", custom=True)
__WITCH_HUNTER.describeAttack(AttackEnum.SACKED, attack=19, accuracy=95, frequency=25)
__WITCH_HUNTER.describeAttack(AttackEnum.HOT_AIR, attack=20, accuracy=85, frequency=25)
__WITCH_HUNTER.describeAttack(AttackEnum.GUILT_TRIP, attack=16, accuracy=80, frequency=20)
__WITCH_HUNTER.describeAttack(AttackEnum.THROW_BOOK, attack=21, accuracy=80, frequency=30)
__WITCH_HUNTER.describeAttack(AttackEnum.TRIAL_BY_FIRE)
__WITCH_HUNTER.describeAttack(AttackEnum.MOB_MENTALITY)
__WITCH_HUNTER.describeAttack(AttackEnum.BOILERPLATE, accuracy=95)
__WITCH_HUNTER.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, FORCED_DEFENSE=45, LURE_RESISTANCE=1, STATUS_EFFECTS=SEE.EFFECT_WILL_OF_THE_PEOPLE)
__WITCH_HUNTER.setMovieAttributes(overrideDeaths=True, extendMovieTime=65)
__WITCH_HUNTER.setAttackBehavior(SEE.EFFECT_MANAGER_WITCH_HUNTER)
__WITCH_HUNTER.setHpPerLevel({20: 3450})
__WITCH_HUNTER.setBounty({CogBountyTypes.Gumballs: 28, CogBountyTypes.Jellybeans: 200, CogBountyTypes.Experience: 1500})
__WITCH_HUNTER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.WitchHunter), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__WITCH_HUNTER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_PitchFork), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__WITCH_HUNTER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_Witchhunter), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__WITCH_HUNTER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(4), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__WITCH_HUNTER.makeHidden()
__WITCH_HUNTER.test()

__MULTISLACKER = SuitDefinition('mslacker', SELLBOT, 6.7, miniboss=True, isMerc=True, nerfDamageForExe=True)
__MULTISLACKER.defineLevelRange(24)
__MULTISLACKER.defineParts(4.4, VBase4(0.45, 0.45, 0.45, 1), ['phase_9/models/char/suits/ttcc_ene_multislacker-zero'],
                           [SKELE_HEAD_C], suitType=SUIT_C, tieType=TIE_SKINNY,
                           bodyTex='phase_9/maps/ttcc_ene_suittex_mslacker.png', custom=True)
__MULTISLACKER.describeAttack(AttackEnum.CLIPON_TIE, attack=19, accuracy=90, frequency=25)
__MULTISLACKER.describeAttack(AttackEnum.HALF_WINDSOR, attack=22, accuracy=80, frequency=20)
__MULTISLACKER.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=17, accuracy=85, frequency=25)
__MULTISLACKER.describeAttack(AttackEnum.POWER_TIE, attack=20, accuracy=85, frequency=30)
__MULTISLACKER.describeAttack(AttackEnum.WASTEFUL_MGMT)
__MULTISLACKER.describeAttack(AttackEnum.HYPER_TASK)
__MULTISLACKER.describeAttack(AttackEnum.ZERO_TASK)
__MULTISLACKER.describeAttack(AttackEnum.MANDATORY_LUNCH)
__MULTISLACKER.describeAttack(AttackEnum.MS_POWER_TIE, attack=25, accuracy=85)
__MULTISLACKER.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, FORCED_DEFENSE=50, LURE_RESISTANCE=1)
__MULTISLACKER.setMovieAttributes(overrideDeaths=True, extendMovieTime=40)
__MULTISLACKER.setAttackBehavior(SEE.EFFECT_MANAGER_MULTISLACKER)
__MULTISLACKER.setHpPerLevel({24: 3200})
__MULTISLACKER.setBounty({CogBountyTypes.Gumballs: 32, CogBountyTypes.Jellybeans: 300, CogBountyTypes.Experience: 1900})
__MULTISLACKER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Multislacker), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__MULTISLACKER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_Multislacker), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__MULTISLACKER.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(4), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__MULTISLACKER.makeHidden()
__MULTISLACKER.test()

__MULTISLACKER_FOREMAN = SuitDefinition('msfore', SELLBOT, 9.25, miniboss=True)
__MULTISLACKER_FOREMAN.defineLevelRange(19, 21)
__MULTISLACKER_FOREMAN.defineParts(7.35, VBase4(0.95, 0.75, 0.95, 1), [SKELE_HEAD_A], [SKELE_HEAD_A], suitType=SUIT_A,
                                   tieType=TIE_SKINNY, bodyTex=TEX_SALES, custom=True)
__MULTISLACKER_FOREMAN.describeAttack(AttackEnum.FIRED, attack=19, accuracy=90, frequency=20)
__MULTISLACKER_FOREMAN.describeAttack(AttackEnum.RE_ORG, attack=17, accuracy=90, frequency=10)
__MULTISLACKER_FOREMAN.describeAttack(AttackEnum.HOT_AIR, attack=20, accuracy=95, frequency=20)
__MULTISLACKER_FOREMAN.describeAttack(AttackEnum.CLIPON_TIE, attack=16, accuracy=95, frequency=10)
__MULTISLACKER_FOREMAN.describeAttack(AttackEnum.DEMOTION, attack=18, accuracy=85, frequency=20)
__MULTISLACKER_FOREMAN.describeAttack(AttackEnum.POWER_TRIP, attack=15, accuracy=85, frequency=20)
__MULTISLACKER_FOREMAN.describeAttack(AttackEnum.WORKERS_COMP)
__MULTISLACKER_FOREMAN.describeAttack(AttackEnum.UNION_BUST)
__MULTISLACKER_FOREMAN.setPassives(HP_MULT=1.0, FORCED_DEFENSE=55)
__MULTISLACKER_FOREMAN.setHpPerLevel({19: 725, 20: 825, 21: 925})
__MULTISLACKER_FOREMAN.makeAlwaysSkelecog()
__MULTISLACKER_FOREMAN.makeHidden()
__MULTISLACKER_FOREMAN.test()

__MAJOR_PLAYER = SuitDefinition('mplayer', BOSSBOT, 10.0, miniboss=True, isMerc=True, nerfDamageForExe=True)
__MAJOR_PLAYER.defineLevelRange(28)
__MAJOR_PLAYER.defineParts(7.1, VBase4(1.0, 1.0, 1.0, 1), ['phase_12/models/char/suits/ttcc_ene_majorplayer-zero'], [SKELE_HEAD_A], suitType=SUIT_A,
                           tieType=TIE_BROAD, bodyTex='phase_12/maps/ttcc_ene_suittex_mplayer.png')
__MAJOR_PLAYER.describeAttack(AttackEnum.HOT_AIR, attack=16, accuracy=90, frequency=30)
__MAJOR_PLAYER.describeAttack(AttackEnum.QUAKE, attack=15, accuracy=75, frequency=20)
__MAJOR_PLAYER.describeAttack(AttackEnum.SONG_AND_DANCE, attack=15, accuracy=85, frequency=20)
__MAJOR_PLAYER.describeAttack(AttackEnum.RE_ARRANGE, attack=18, accuracy=85, frequency=30)
__MAJOR_PLAYER.describeAttack(AttackEnum.STAR_OF_THE_SHOW)
__MAJOR_PLAYER.describeAttack(AttackEnum.DANCE_PARTNERS)
__MAJOR_PLAYER.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, FORCED_DEFENSE=65, LURE_RESISTANCE=1)
__MAJOR_PLAYER.setMovieAttributes(overrideDeaths=True, extendMovieTime=120)
__MAJOR_PLAYER.setAttackBehavior(SEE.EFFECT_MANAGER_MAJOR_PLAYER)
__MAJOR_PLAYER.setHpPerLevel({28: 4444})
__MAJOR_PLAYER.setBounty({CogBountyTypes.Gumballs: 38, CogBountyTypes.Jellybeans: 425, CogBountyTypes.Experience: 2300})
__MAJOR_PLAYER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.MajorPlayer), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__MAJOR_PLAYER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_Saxophone), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__MAJOR_PLAYER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_MuzzleRose), chance=MercLootLegendaryChance, chancePerPity=MercLootLegendaryPity, enemyName=__MAJOR_PLAYER.name, rarity=LootRarity.Legendary),
            HolidayLootEntry(loot=HalloweenMaterialLoot(5), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__MAJOR_PLAYER.makeHidden()
__MAJOR_PLAYER.test()

__PLUTOCRAT = SuitDefinition('pcrat', CASHBOT, 4.5, miniboss=True, isMerc=True, nerfDamageForExe=True)
__PLUTOCRAT.defineLevelRange(38)
__PLUTOCRAT.defineParts(3.2, VBase4(0.667, 0.639, 0.6, 1.0), ['phase_10/models/char/suits/ttcc_ene_plutocrat-zero'], [SKELE_HEAD_C], suitType=SUIT_C,
                        tieType=TIE_BROAD, bodyTex='phase_10/maps/ttcc_ene_suittex_pcrat.png')
__PLUTOCRAT.describeAttack(AttackEnum.FREEZE_ASSETS,         attack=34, accuracy=95, frequency=30)
__PLUTOCRAT.describeAttack(AttackEnum.PICK_POCKET,           attack=29, accuracy=80, frequency=15)
__PLUTOCRAT.describeAttack(AttackEnum.SYNERGY,               attack=27, accuracy=95, frequency=20)
__PLUTOCRAT.describeAttack(AttackEnum.MARKET_CRASH,          attack=32, accuracy=90, frequency=20)
__PLUTOCRAT.describeAttack(AttackEnum.CIGAR_SMOKE_PLUTOCRAT, attack=35, accuracy=75, frequency=15)
__PLUTOCRAT.describeAttack(AttackEnum.SLUSH_FUND)
__PLUTOCRAT.describeAttack(AttackEnum.DEEP_FREEZE)
__PLUTOCRAT.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, LURE_RESISTANCE=1)
__PLUTOCRAT.setMovieAttributes(overrideDeaths=True, extendMovieTime=30)
__PLUTOCRAT.setAttackBehavior(SEE.EFFECT_MANAGER_PLUTOCRAT)
__PLUTOCRAT.setHpPerLevel({38: 6000})
__PLUTOCRAT.setBounty({CogBountyTypes.Gumballs: 44, CogBountyTypes.Jellybeans: 525, CogBountyTypes.Experience: 2700})
__PLUTOCRAT.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Plutocrat), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__PLUTOCRAT.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Overhead_Icecube), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__PLUTOCRAT.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(6), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__PLUTOCRAT.makeHidden()
__PLUTOCRAT.test()

__CHARON = SuitDefinition('charon', CASHBOT, 6.7, miniboss=True, isMerc=True, nerfDamageForExe=True)
__CHARON.defineLevelRange(25)
__CHARON.defineParts(5.7, VBase4(0.294, 0.651, 0.871, 1), [SKELE_HEAD_A], [SKELE_HEAD_A], suitType=SUIT_A,
                     tieType=TIE_SKINNY, bodyTex=TEX_MONEY, skeleBodyTex='**/skel_body_cash_gen',
                     skeleTextureOverride='**/skel_body_cash_gen', bodyTint=(0.529, 0.506, 0.475, 1.0))
__CHARON.describeAttack(AttackEnum.DEMOTION,        attack=35, accuracy=90, frequency=30)
__CHARON.describeAttack(AttackEnum.RED_TAPE,        attack=34, accuracy=85, frequency=20)
__CHARON.describeAttack(AttackEnum.PECKING_ORDER,   attack=36, accuracy=90, frequency=25)
__CHARON.describeAttack(AttackEnum.POWER_TRIP,      attack=32, accuracy=85, frequency=25)
__CHARON.setHpPerLevel({25: 2000})
__CHARON.setPassives(FORCED_DEFENSE=70, LURE_RESISTANCE=3)
__CHARON.setAttackBehavior(SEE.EFFECT_MANAGER_CHARON)
__CHARON.makeAlwaysSkelecog()
__CHARON.makeHidden()
__CHARON.test()

__NIX = SuitDefinition('nix', CASHBOT, 6.8, miniboss=True, isMerc=True, nerfDamageForExe=True)
__NIX.defineLevelRange(21)
__NIX.defineParts(5.8, VBase4(0.294, 0.651, 0.871, 1), [SKELE_HEAD_B], [SKELE_HEAD_B], suitType=SUIT_B,
                  tieType=TIE_BROAD, bodyTex=TEX_MONEY, skeleBodyTex='**/skel_body_cash_gen',
                  skeleTextureOverride='**/skel_body_cash_gen', bodyTint=(0.565, 0.588, 0.627, 1.0))
__NIX.describeAttack(AttackEnum.PLAY_HARDBALL,   attack=32, accuracy=90, frequency=30)
__NIX.describeAttack(AttackEnum.RUB_OUT,         attack=28, accuracy=85, frequency=15)
__NIX.describeAttack(AttackEnum.CANNED,          attack=30, accuracy=90, frequency=25)
__NIX.describeAttack(AttackEnum.POWER_TRIP,      attack=26, accuracy=85, frequency=30)
__NIX.describeAttack(AttackEnum.SHAKEDOWN)
__NIX.setHpPerLevel({21: 1625})
__NIX.setPassives(FORCED_DEFENSE=80, LURE_RESISTANCE=3)
__NIX.setAttackBehavior(SEE.EFFECT_MANAGER_NIX)
__NIX.makeAlwaysSkelecog()
__NIX.makeHidden()
__NIX.test()

__HYDRA = SuitDefinition('hydra', CASHBOT, 8.0, miniboss=True, isMerc=True, nerfDamageForExe=True)
__HYDRA.defineLevelRange(22)
__HYDRA.defineParts(6.3, VBase4(0.294, 0.651, 0.871, 1), [SKELE_HEAD_C], [SKELE_HEAD_C], suitType=SUIT_C,
                    tieType=TIE_BOW, bodyTex=TEX_MONEY, skeleBodyTex='**/skel_body_cash_gen',
                    skeleTextureOverride='**/skel_body_cash_gen', bodyTint=(0.612, 0.71, 0.729, 1.0))
__HYDRA.describeAttack(AttackEnum.CHOMP,    attack=29, accuracy=90, frequency=30)
__HYDRA.describeAttack(AttackEnum.BITE,     attack=26, accuracy=85, frequency=25)
__HYDRA.describeAttack(AttackEnum.CRUNCH,   attack=28, accuracy=90, frequency=25)
__HYDRA.describeAttack(AttackEnum.SYNERGY,  attack=25, accuracy=85, frequency=20)
__HYDRA.describeAttack(AttackEnum.KICK_UP)
__HYDRA.setHpPerLevel({22: 1700})
__HYDRA.setPassives(FORCED_DEFENSE=80, LURE_RESISTANCE=3)
__HYDRA.setAttackBehavior(SEE.EFFECT_MANAGER_HYDRA)
__HYDRA.makeAlwaysSkelecog()
__HYDRA.makeHidden()
__HYDRA.test()

__STYX = SuitDefinition('styx', CASHBOT, 6.8, miniboss=True, isMerc=True, nerfDamageForExe=True)
__STYX.defineLevelRange(20)
__STYX.defineParts(5.4, VBase4(0.294, 0.651, 0.871, 1), [SKELE_HEAD_C], [SKELE_HEAD_C], suitType=SUIT_C,
                   tieType=TIE_BROAD, bodyTex=TEX_MONEY, skeleBodyTex='**/skel_body_cash_gen',
                   skeleTextureOverride='**/skel_body_cash_gen', bodyTint=(0.749, 0.749, 0.749, 1.0))
__STYX.describeAttack(AttackEnum.WATERCOOLER,       attack=34, accuracy=90, frequency=30)
__STYX.describeAttack(AttackEnum.LIQUIDATE,         attack=32, accuracy=85, frequency=20)
__STYX.describeAttack(AttackEnum.FREEZE_ASSETS,     attack=33, accuracy=90, frequency=30)
__STYX.describeAttack(AttackEnum.SYNERGY,           attack=30, accuracy=85, frequency=20)
__STYX.describeAttack(AttackEnum.SITDOWN)
__STYX.describeAttack(AttackEnum.USURY)
__STYX.setHpPerLevel({20: 1500})
__STYX.setPassives(FORCED_DEFENSE=80, LURE_RESISTANCE=3)
__STYX.setAttackBehavior(SEE.EFFECT_MANAGER_STYX)
__STYX.makeAlwaysSkelecog()
__STYX.makeHidden()
__STYX.test()

__KERBEROS = SuitDefinition('kerberos', CASHBOT, 8.5, miniboss=True, isMerc=True, nerfDamageForExe=True)
__KERBEROS.defineLevelRange(23)
__KERBEROS.defineParts(6.9, VBase4(0.294, 0.651, 0.871, 1), [SKELE_HEAD_A], [SKELE_HEAD_A], suitType=SUIT_A,
                       tieType=TIE_BROAD, bodyTex=TEX_MONEY, skeleBodyTex='**/skel_body_cash_gen',
                       skeleTextureOverride='**/skel_body_cash_gen', bodyTint=(0.649, 0.749, 0.649, 1.0))
__KERBEROS.describeAttack(AttackEnum.WITHDRAWAL,     attack=30, accuracy=90, frequency=30)
__KERBEROS.describeAttack(AttackEnum.BOUNCE_CHECK,   attack=27, accuracy=85, frequency=30)
__KERBEROS.describeAttack(AttackEnum.PICK_POCKET,    attack=29, accuracy=90, frequency=25)
__KERBEROS.describeAttack(AttackEnum.SYNERGY,        attack=26, accuracy=85, frequency=15)
__KERBEROS.describeAttack(AttackEnum.TRIBUTE)
__KERBEROS.setHpPerLevel({23: 1800})
__KERBEROS.setPassives(FORCED_DEFENSE=75, LURE_RESISTANCE=3)
__KERBEROS.setAttackBehavior(SEE.EFFECT_MANAGER_KERBEROS)
__KERBEROS.makeAlwaysSkelecog()
__KERBEROS.makeHidden()
__KERBEROS.test()

__CHAINSAW_CONSULTANT = SuitDefinition('chainsaw', BOSSBOT, 10.2, miniboss=True, isMerc=True, nerfDamageForExe=True)
__CHAINSAW_CONSULTANT.defineLevelRange(50)
__CHAINSAW_CONSULTANT.defineParts(7.0, VBase4(0.294, 0.29, 0.298, 1.0),
                                  ['phase_12/models/char/suits/ttcc_ene_chainsaw-zero'], ['phase_12/models/char/suits/ttcc_ene_chainsaw-zero'],
                                  suitType=SUIT_A, tieType=TIE_BROAD,
                                  bodyTex='phase_12/maps/ttcc_ene_suittex_chainsaw.png')
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.GLOWER_POWER, attack=30, accuracy=95, frequency=35)
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.ROLODEX, attack=28, accuracy=85, frequency=25)
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.QUAKE, attack=24, accuracy=80, frequency=15)
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.CANNED, attack=26, accuracy=90, frequency=25)
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.OFFBOARDING)
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.REVVING_UP)
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.LAYOFFS)
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.CUT_THE_SLACK)
__CHAINSAW_CONSULTANT.describeAttack(AttackEnum.MARKED_WOOD, attack=30)
__CHAINSAW_CONSULTANT.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, LURE_RESISTANCE=1, FORCED_DEFENSE=70)
__CHAINSAW_CONSULTANT.setMovieAttributes(overrideDeaths=True, extendMovieTime=60)
__CHAINSAW_CONSULTANT.setAttackBehavior(SEE.EFFECT_MANAGER_CHAINSAW_CONSULTANT)
__CHAINSAW_CONSULTANT.setHpPerLevel({50: 12000})
__CHAINSAW_CONSULTANT.setBounty({CogBountyTypes.Gumballs: 50, CogBountyTypes.Jellybeans: 625, CogBountyTypes.Experience: 3100})
__CHAINSAW_CONSULTANT.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.ChainsawConsultant), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__CHAINSAW_CONSULTANT.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_Chainsaw), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__CHAINSAW_CONSULTANT.name, rarity=LootRarity.VeryRare),
            HolidayLootEntry(loot=HalloweenMaterialLoot(7), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__CHAINSAW_CONSULTANT.makeHidden()
__CHAINSAW_CONSULTANT.test()

__PACESETTER = SuitDefinition('psetter', SELLBOT, 7.1, miniboss=True, isMerc=True, nerfDamageForExe=True)
__PACESETTER.defineLevelRange(66)
__PACESETTER.defineParts(5.65, VBase4(0.369, 0.365, 0.365, 1), ['phase_9/models/char/suits/ttcc_ene_pacesetter-zero'],
                         [SKELE_HEAD_B], suitType=SUIT_B, tieType=TIE_NONE,
                         bodyTex='phase_9/maps/ttcc_ene_suittex_pacesetter.png', bodyModelType=BodyModelType.OpenShirt)
__PACESETTER.describeAttack(AttackEnum.RAZZLE_DAZZLE,  attack=44, accuracy=95, frequency=30)
__PACESETTER.describeAttack(AttackEnum.SCHMOOZE,       attack=40, accuracy=90, frequency=25)
__PACESETTER.describeAttack(AttackEnum.QUAKE,          attack=34, accuracy=85, frequency=20)
__PACESETTER.describeAttack(AttackEnum.WITHDRAWAL,     attack=38, accuracy=95, frequency=25)
__PACESETTER.describeAttack(AttackEnum.PICK_UP_THE_PACE)
__PACESETTER.describeAttack(AttackEnum.OVERCLOCKED)
__PACESETTER.describeAttack(AttackEnum.RUSH_JOB)
__PACESETTER.describeAttack(AttackEnum.CONTENT_SYNC)
__PACESETTER.describeAttack(AttackEnum.MOVING_GOALPOSTS)
__PACESETTER.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__PACESETTER.describeAttack(AttackEnum.HURRY_SICKNESS_MG, attack=35, accuracy=100)
__PACESETTER.setPassives(HP_MULT=1.0, FORCED_DEFENSE=65, LURE_RESISTANCE=1)
__PACESETTER.setMovieAttributes(overrideDeaths=True, extendMovieTime=50)
__PACESETTER.setAttackBehavior(SEE.EFFECT_MANAGER_PACESETTER)
__PACESETTER.setHpPerLevel({66: 12500})
__PACESETTER.setBounty({CogBountyTypes.Gumballs: 50, CogBountyTypes.Jellybeans: 750, CogBountyTypes.Experience: 3500})
__PACESETTER.setLoot([
    LootTable(
        [
            DefeatPityLootEntry(loot=InventoryLoot(ChatStickersItemType.Pacesetter), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__PACESETTER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(GlassesItemType.Glasses_Pacesetter), chance=MercLootBaseChance, chancePerPity=MercLootPity, enemyName=__PACESETTER.name, rarity=LootRarity.VeryRare),
            DefeatPityLootEntry(loot=InventoryLoot(BackpackItemType.Backpack_Guitar_Pacesetter), chance=MercLootLegendaryChance, chancePerPity=MercLootLegendaryPity, enemyName=__PACESETTER.name, rarity=LootRarity.Legendary),
            HolidayLootEntry(loot=HalloweenMaterialLoot(7), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),
        ]
    )
])
__PACESETTER.makeHidden()
__PACESETTER.test()

__HIGH_ROLLER = SuitDefinition('hroller', CASHBOT, 10.0, miniboss=True, isMerc=True, nerfDamageForExe=True)
__HIGH_ROLLER.defineLevelRange(100)
__HIGH_ROLLER.defineParts(7.1, VBase4(1.0, 1.0, 1.0, 1), ['phase_12/models/char/suits/cc_m_chr_ene_highroller-zero'],
                          [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_NONE,
                          bodyTex='phase_12/maps/cc_t_ene_highroller_suit.png', extraPadding=1.5,
                          bodyModelType=BodyModelType.HighRoller)
__HIGH_ROLLER.describeAttack(AttackEnum.FREE_CRUISE, attack=198, accuracy=85, frequency=25)
__HIGH_ROLLER.describeAttack(AttackEnum.ROLLED, attack=150, accuracy=100, frequency=25)
__HIGH_ROLLER.describeAttack(AttackEnum.CON_DUCK_TION, attack=225, accuracy=85, frequency=25)
__HIGH_ROLLER.describeAttack(AttackEnum.DICE_ROULETTE, frequency=25)
__HIGH_ROLLER.describeAttack(AttackEnum.ACE_IN_THE_HOLE, attack=333, accuracy=100)
__HIGH_ROLLER.describeAttack(AttackEnum.RANDOM_GAME)
__HIGH_ROLLER.describeAttack(AttackEnum.RANDOM_GAME_FINISH)
__HIGH_ROLLER.describeAttack(AttackEnum.RANDOM_GAME_PUNISH)
__HIGH_ROLLER.describeAttack(AttackEnum.HIGHROLLER_HOLLYWOOD)
__HIGH_ROLLER.describeAttack(AttackEnum.TRICK_OF_THE_LIGHT)
__HIGH_ROLLER.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, FORCED_DEFENSE=65, LURE_RESISTANCE=1)
__HIGH_ROLLER.setMovieAttributes(overrideDeaths=True, extendMovieTime=90)
__HIGH_ROLLER.setAttackBehavior(SEE.EFFECT_MANAGER_HIGH_ROLLER)
__HIGH_ROLLER.setHpPerLevel({100: 999})
__HIGH_ROLLER.setBounty({CogBountyTypes.Gumballs: 30, CogBountyTypes.Jellybeans: 4444, CogBountyTypes.Experience: 300, CogBountyTypes.HolidayList: [ToontownGlobals.APRIL_FOOLS]})
__HIGH_ROLLER.setLoot([
    LootTable(
        [
            LootEntry(loot=InventoryLoot(MaterialItemType.Gumballs, quantity=40), chance=1.0, rarity=LootRarity.Guaranteed),
            HolidayLootEntry(loot=HalloweenMaterialLoot(5), chance=1.00, rarity=LootRarity.Guaranteed, holidayIds=materialHolidayIds),

            DefeatAmountLootEntry(loot=InventoryLoot(ChatStickersItemType.HighRoller), enemyAmount=1, enemyName=__HIGH_ROLLER.name),  # High Roller sticker
            DefeatAmountLootEntry(loot=InventoryLoot(HatItemType.Hat_LowBaller), enemyAmount=2, enemyName=__HIGH_ROLLER.name),  # Low Baller hat
            DefeatAmountLootEntry(loot=InventoryLoot(GlassesItemType.Glasses_LowBaller), enemyAmount=3, enemyName=__HIGH_ROLLER.name),  # Low Baller glasses
            DefeatAmountLootEntry(loot=InventoryLoot(ChatStickersItemType.DiceRoll), enemyAmount=5, enemyName=__HIGH_ROLLER.name),  # Dice sticker
            DefeatAmountLootEntry(loot=LootContainer([
                InventoryLoot(ClothingTopItemType.HighRollersSuit),
                InventoryLoot(ClothingBottomItemType.HighRollersSuitShorts),
            ], friendlyName='High Roller\'s Suit'), enemyAmount=7, enemyName=__HIGH_ROLLER.name),  # High Roller outfit
            DefeatAmountLootEntry(loot=InventoryLoot(HatItemType.Hat_HighRoller), enemyAmount=10, enemyName=__HIGH_ROLLER.name),  # High Roller hat
            DefeatAmountLootEntry(loot=LootContainer([
                InventoryLoot(ClothingTopItemType.HighRollersProdigalSuit),
                InventoryLoot(ClothingBottomItemType.HighRollersProdigalSuitShorts),
            ], friendlyName='High Roller\'s Prodigal Suit'), enemyAmount=15, enemyName=__HIGH_ROLLER.name),  # High Roller black outfit
        ]
    )
])
__HIGH_ROLLER.makeHidden()
__HIGH_ROLLER.test()

__HIGH_ROLLER_CLONE = SuitDefinition('hrollerc', CASHBOT, 10.0, miniboss=True)
__HIGH_ROLLER_CLONE.defineLevelRange(25)
__HIGH_ROLLER_CLONE.defineParts(7.1, VBase4(1.0, 1.0, 1.0, 1), ['phase_12/models/char/suits/cc_m_chr_ene_highroller-zero'],
                          [SKELE_HEAD_A], suitType=SUIT_A, tieType=TIE_NONE,
                          bodyTex='phase_12/maps/cc_t_ene_highroller_suit.png', extraPadding=1.5,
                          bodyModelType=BodyModelType.HighRoller)
__HIGH_ROLLER_CLONE.describeAttack(AttackEnum.POWER_TRIP, attack=50, accuracy=85, frequency=100)
__HIGH_ROLLER_CLONE.describeAttack(AttackEnum.HIGHROLLER_CLONE_TRAP)
__HIGH_ROLLER_CLONE.describeAttack(AttackEnum.HIGHROLLER_CLONE_SQUIRT)
__HIGH_ROLLER_CLONE.setPassives(HP_MULT=1.0, DEFENSE_BOOST=0, FORCED_DEFENSE=65)
__HIGH_ROLLER_CLONE.setMovieAttributes(overrideDeaths=True, extendMovieTime=120)
__HIGH_ROLLER_CLONE.setHpPerLevel({25: 8000})
__HIGH_ROLLER_CLONE.makeHidden()
__HIGH_ROLLER_CLONE.test()

# region Face the Family managers
__FTF_FOREMAN = SuitDefinition('ftf_s', SELLBOT, 9.25, miniboss=True)
__FTF_FOREMAN.defineLevelRange(20, 40)
__FTF_FOREMAN.defineParts(7.35, VBase4(0.95, 0.75, 0.95, 1), [SKELE_HEAD_A], [SKELE_HEAD_A], suitType=SUIT_A,
                          tieType=TIE_SKINNY, bodyTex=TEX_SALES, custom=True)
__FTF_FOREMAN.describeAttack(AttackEnum.FIRED, attack=30, accuracy=90, frequency=20)
__FTF_FOREMAN.describeAttack(AttackEnum.RE_ORG, attack=26, accuracy=80, frequency=10)
__FTF_FOREMAN.describeAttack(AttackEnum.HOT_AIR, attack=32, accuracy=95, frequency=20)
__FTF_FOREMAN.describeAttack(AttackEnum.CLIPON_TIE, attack=28, accuracy=75, frequency=10)
__FTF_FOREMAN.describeAttack(AttackEnum.DEMOTION, attack=26, accuracy=85, frequency=20)
__FTF_FOREMAN.describeAttack(AttackEnum.POWER_TRIP, attack=25, accuracy=85, frequency=20)
__FTF_FOREMAN.describeAttack(AttackEnum.WORKERS_COMP)
__FTF_FOREMAN.describeAttack(AttackEnum.FTF_FOREMAN_SNIPE)
__FTF_FOREMAN.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__FTF_FOREMAN.setPassives(FORCED_DEFENSE=65)
__FTF_FOREMAN.makeAlwaysSkelecog()
__FTF_FOREMAN.test()

__FTF_SUPERVISOR = SuitDefinition('ftf_m', CASHBOT, 10.25, miniboss=True)
__FTF_SUPERVISOR.defineLevelRange(20, 40)
__FTF_SUPERVISOR.defineParts(7.35, VBase4(0.65, 0.95, 0.85, 1), [SKELE_HEAD_C], [SKELE_HEAD_C], suitType=SUIT_C,
                             tieType=TIE_BROAD, bodyTex=TEX_MONEY, custom=True)
__FTF_SUPERVISOR.describeAttack(AttackEnum.FIRED, attack=32, accuracy=90, frequency=20)
__FTF_SUPERVISOR.describeAttack(AttackEnum.LIQUIDATE, attack=30, accuracy=80, frequency=10)
__FTF_SUPERVISOR.describeAttack(AttackEnum.AUDIT, attack=27, accuracy=95, frequency=20)
__FTF_SUPERVISOR.describeAttack(AttackEnum.TABULATE, attack=31, accuracy=75, frequency=10)
__FTF_SUPERVISOR.describeAttack(AttackEnum.DEMOTION, attack=30, accuracy=85, frequency=20)
__FTF_SUPERVISOR.describeAttack(AttackEnum.SYNERGY, attack=24, accuracy=85, frequency=20)
__FTF_SUPERVISOR.describeAttack(AttackEnum.FTF_SUPERVISOR_LIFE_INSURANCE, attack=0, accuracy=0, frequency=0)
__FTF_SUPERVISOR.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__FTF_SUPERVISOR.describeAttack(AttackEnum.FTF_SUPERVISOR_ABACUS_SYNERGY, attack=38, accuracy=100, frequency=0)
__FTF_SUPERVISOR.setPassives(STATUS_EFFECTS=SEE.EFFECT_FTF_SUPERVISOR_INSURED, FORCED_DEFENSE=65)
__FTF_SUPERVISOR.makeAlwaysSkelecog()
__FTF_SUPERVISOR.test()

__FTF_ATTORNEY = SuitDefinition('ftf_l', LAWBOT, 8.75, miniboss=True)
__FTF_ATTORNEY.defineLevelRange(20, 40)
__FTF_ATTORNEY.defineParts(7.25, VBase4(0.75, 0.75, 0.95, 1), [SKELE_HEAD_B], [SKELE_HEAD_B], suitType=SUIT_B,
                           tieType=TIE_BOW, bodyTex=TEX_LEGAL, custom=True)
__FTF_ATTORNEY.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=29, accuracy=90, frequency=10)
__FTF_ATTORNEY.describeAttack(AttackEnum.QUAKE, attack=32, accuracy=60, frequency=10)
__FTF_ATTORNEY.describeAttack(AttackEnum.EVICTION_NOTICE, attack=31, accuracy=95, frequency=30)
__FTF_ATTORNEY.describeAttack(AttackEnum.SPIN, attack=29, accuracy=75, frequency=25)
__FTF_ATTORNEY.describeAttack(AttackEnum.RED_TAPE, attack=28, accuracy=85, frequency=25)
__FTF_ATTORNEY.describeAttack(AttackEnum.OBJECTION)
__FTF_ATTORNEY.describeAttack(AttackEnum.OBJECTION_SUSTAINED, attack=20, accuracy=100)
__FTF_ATTORNEY.describeAttack(AttackEnum.OBJECTION_OVERRULED)
__FTF_ATTORNEY.describeAttack(AttackEnum.CASTLING)
__FTF_ATTORNEY.describeAttack(AttackEnum.FTF_ATTORNEY_PICK_UP_THE_PACE)
__FTF_ATTORNEY.describeAttack(AttackEnum.RUSH_JOB)
__FTF_ATTORNEY.describeAttack(AttackEnum.FTF_ATTORNEY_COURT_MANDATE_MONOLITH)
__FTF_ATTORNEY.describeAttack(AttackEnum.FTF_ATTORNEY_COURT_MANDATE_OMNIPOTENT)
__FTF_ATTORNEY.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__FTF_ATTORNEY.setPassives(FORCED_DEFENSE=65)
__FTF_ATTORNEY.makeAlwaysSkelecog()
__FTF_ATTORNEY.test()

__FTF_PRESIDENT = SuitDefinition('ftf_c', BOSSBOT, 9.25, miniboss=True)
__FTF_PRESIDENT.defineLevelRange(20, 40)
__FTF_PRESIDENT.defineParts(7.35, VBase4(133/255, 112/255, 86/255, 1), ['phase_12/models/char/suits/ttcc_ene_autocaddie-zero'],
                            ['phase_12/models/char/suits/ttcc_ene_autocaddie-zero'], suitType=SUIT_A,
                            tieType=TIE_BROAD, bodyTex=TEX_CORP, custom=True)
__FTF_PRESIDENT.describeAttack(AttackEnum.CIGAR_SMOKE, attack=34, accuracy=80, frequency=19)
__FTF_PRESIDENT.describeAttack(AttackEnum.SONG_AND_DANCE, attack=33, accuracy=80, frequency=6)
__FTF_PRESIDENT.describeAttack(AttackEnum.GLOWER_POWER, attack=31, accuracy=75, frequency=19)
__FTF_PRESIDENT.describeAttack(AttackEnum.POWER_TRIP, attack=31, accuracy=90, frequency=6)
__FTF_PRESIDENT.describeAttack(AttackEnum.TEE_OFF, attack=30, accuracy=90, frequency=50)
__FTF_PRESIDENT.describeAttack(AttackEnum.FTF_PRESIDENT_EXTRA_TIP)
__FTF_PRESIDENT.describeAttack(AttackEnum.FTF_PRESIDENT_MULLIGAN, attack=30, accuracy=80, frequency=0)
__FTF_PRESIDENT.describeAttack(AttackEnum.FTF_PRESIDENT_SNAP, attack=29, accuracy=100, frequency=0)
__FTF_PRESIDENT.describeAttack(AttackEnum.FTF_PRESIDENT_SNIPE, attack=30, accuracy=100, frequency=0)
__FTF_PRESIDENT.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__FTF_PRESIDENT.setPassives(FORCED_DEFENSE=65)
__FTF_PRESIDENT.makeAlwaysSkelecog()
__FTF_PRESIDENT.test()

__FTF_FOREMAN_REDTAPE = SuitDefinition('ftf_s_rt', SELLBOT, 9.25, miniboss=True)
__FTF_FOREMAN_REDTAPE.defineLevelRange(20, 40)
__FTF_FOREMAN_REDTAPE.defineParts(7.35, VBase4(0.95, 0.75, 0.95, 1), [SKELE_HEAD_A], [SKELE_HEAD_A], suitType=SUIT_A,
                          tieType=TIE_SKINNY, bodyTex=TEX_SALES, custom=True)
__FTF_FOREMAN_REDTAPE.describeAttack(AttackEnum.FTF_FOREMAN_REDTAPE, attack=25, accuracy=85, frequency=100)
__FTF_FOREMAN_REDTAPE.describeAttack(AttackEnum.WORKERS_COMP)
__FTF_FOREMAN_REDTAPE.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__FTF_FOREMAN_REDTAPE.setPassives(FORCED_DEFENSE=65)
__FTF_FOREMAN_REDTAPE.makeAlwaysSkelecog()
__FTF_FOREMAN_REDTAPE.test()

__FTF_FOREMAN_BURNING = SuitDefinition('ftf_s_br', SELLBOT, 9.25, miniboss=True)
__FTF_FOREMAN_BURNING.defineLevelRange(20, 40)
__FTF_FOREMAN_BURNING.defineParts(7.35, VBase4(0.95, 0.75, 0.95, 1), [SKELE_HEAD_A], [SKELE_HEAD_A], suitType=SUIT_A,
                                  tieType=TIE_SKINNY, bodyTex=TEX_SALES, custom=True)
__FTF_FOREMAN_BURNING.describeAttack(AttackEnum.FTF_FOREMAN_CIGAR_SMOKE, attack=16, accuracy=85, frequency=100)
__FTF_FOREMAN_BURNING.describeAttack(AttackEnum.WORKERS_COMP)
__FTF_FOREMAN_BURNING.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__FTF_FOREMAN_BURNING.setPassives(FORCED_DEFENSE=65)
__FTF_FOREMAN_BURNING.makeAlwaysSkelecog()
__FTF_FOREMAN_BURNING.test()

__FTF_PRESIDENT_ANCIENT = SuitDefinition('ftf_c_ac', BOSSBOT, 9.25, miniboss=True)
__FTF_PRESIDENT_ANCIENT.defineLevelRange(20, 40)
__FTF_PRESIDENT_ANCIENT.defineParts(7.35, VBase4(133/255, 112/255, 86/255, 1), ['phase_12/models/char/suits/ttcc_ene_autocaddie-zero'],
                            ['phase_12/models/char/suits/ttcc_ene_autocaddie-zero'], suitType=SUIT_A,
                            tieType=TIE_BROAD, bodyTex=TEX_CORP, custom=True)
__FTF_PRESIDENT_ANCIENT.describeAttack(AttackEnum.FTF_PRESIDENT_EXTRA_TIP)
__FTF_PRESIDENT_ANCIENT.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__FTF_PRESIDENT_ANCIENT.describeAttack(AttackEnum.FTF_PRESIDENT_DRIVER, attack=29, accuracy=90, frequency=100)
__FTF_PRESIDENT_ANCIENT.setPassives(FORCED_DEFENSE=65)
__FTF_PRESIDENT_ANCIENT.makeAlwaysSkelecog()
__FTF_PRESIDENT_ANCIENT.test()

__FTF_SUPERVISOR_CONFUSED = SuitDefinition('ftf_m_cf', CASHBOT, 8.75, miniboss=True)
__FTF_SUPERVISOR_CONFUSED.defineLevelRange(20, 40)
__FTF_SUPERVISOR_CONFUSED.defineParts(7.25, VBase4(0.75, 0.75, 0.95, 1), [SKELE_HEAD_B], [SKELE_HEAD_B], suitType=SUIT_B,
                                      tieType=TIE_BOW, bodyTex=TEX_MONEY, custom=True)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.PARADIGM_SHIFT, attack=29, accuracy=90, frequency=10)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.QUAKE, attack=32, accuracy=60, frequency=10)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.EVICTION_NOTICE, attack=31, accuracy=95, frequency=30)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.SPIN, attack=29, accuracy=75, frequency=25)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.RED_TAPE, attack=28, accuracy=85, frequency=25)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.OBJECTION)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.OBJECTION_SUSTAINED, attack=20, accuracy=100)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.OBJECTION_OVERRULED)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.CASTLING)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.FTF_ATTORNEY_PICK_UP_THE_PACE)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.RUSH_JOB)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.CORPORATE_RESTRUCTURING)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.HURRY_SICKNESS, attack=35, accuracy=100)
__FTF_SUPERVISOR_CONFUSED.describeAttack(AttackEnum.FTF_SUPERVISOR_LIFE_INSURANCE, attack=0, accuracy=0, frequency=0)
__FTF_SUPERVISOR_CONFUSED.setPassives(STATUS_EFFECTS=SEE.EFFECT_FTF_SUPERVISOR_INSURED, FORCED_DEFENSE=65)
__FTF_SUPERVISOR_CONFUSED.makeAlwaysSkelecog()
__FTF_SUPERVISOR_CONFUSED.test()

# This is a junk Cog that exists solely to track loot
__FTF_NUCLEAR = SuitDefinition('ftf_nuclear', BOSSBOT, 9.25)
__FTF_NUCLEAR.defineLevelRange(1)
__FTF_NUCLEAR.defineParts(7.35, VBase4(133/255, 112/255, 86/255, 1), ['phase_12/models/char/suits/ttcc_ene_autocaddie-zero'],
                          ['phase_12/models/char/suits/ttcc_ene_autocaddie-zero'], suitType=SUIT_A,
                          tieType=TIE_BROAD, bodyTex=TEX_CORP, custom=True)
__FTF_NUCLEAR.describeAttack(AttackEnum.CIGAR_SMOKE, attack=1, accuracy=95, frequency=100)
__FTF_NUCLEAR.setLoot([
    LootTable(
        [
            # Guaranteed Gumballs
            LootEntry(loot=InventoryLoot(MaterialItemType.Gumballs, quantity=5), chance=1.0, rarity=LootRarity.Guaranteed),
            # Goon Hats
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_GoonPatrol_Yellow), chance=0.04, chancePerPity=0.002, enemyName=__FTF_NUCLEAR.name, rarity=LootRarity.Uncommon),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_GoonPatrol_Orange), chance=0.04, chancePerPity=0.002, enemyName=__FTF_NUCLEAR.name, rarity=LootRarity.Uncommon),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_GoonPatrol_Red), chance=0.04, chancePerPity=0.002, enemyName=__FTF_NUCLEAR.name, rarity=LootRarity.Uncommon),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_GoonPatrol_Purple), chance=0.04, chancePerPity=0.002, enemyName=__FTF_NUCLEAR.name, rarity=LootRarity.Uncommon),
            DefeatPityLootEntry(loot=InventoryLoot(HatItemType.Hat_GoonSecurity), chance=0.04, chancePerPity=0.002, enemyName=__FTF_NUCLEAR.name, rarity=LootRarity.Uncommon),
            # X Defeat Drops
            DefeatAmountLootEntry(loot=InventoryLoot(BackgroundItemType.Special_PaintMixer), enemyAmount=5, enemyName=__FTF_NUCLEAR.name),
            DefeatAmountLootEntry(loot=InventoryLoot(NameplateItemType.Special_SellbotPaint), enemyAmount=10, enemyName=__FTF_NUCLEAR.name),
            DefeatAmountLootEntry(loot=LootContainer(
                [InventoryLoot(ChatStickersItemType.SellbotEmblem),
                 InventoryLoot(ChatStickersItemType.CashbotEmblem),
                 InventoryLoot(ChatStickersItemType.LawbotEmblem),
                 InventoryLoot(ChatStickersItemType.BossbotEmblem),
                 InventoryLoot(ChatStickersItemType.BoardbotEmblem)],
                friendlyName='Cog Emblem Sticker Set'), enemyAmount=20, enemyName=__FTF_NUCLEAR.name),
            DefeatAmountLootEntry(loot=InventoryLoot(BackpackItemType.FactoryGear), enemyAmount=35, enemyName=__FTF_NUCLEAR.name),
            DefeatAmountLootEntry(loot=InventoryLoot(HatItemType.Hat_CogBucket), enemyAmount=50, enemyName=__FTF_NUCLEAR.name),
            DefeatAmountLootEntry(loot=InventoryLoot(HatItemType.Hat_Skelecog_Purple), enemyAmount=65, enemyName=__FTF_NUCLEAR.name),
            DefeatAmountLootEntry(loot=InventoryLoot(ChatStickersItemType.FrustratedForeman), enemyAmount=80, enemyName=__FTF_NUCLEAR.name),
        ]
    )
], shiftSwap=True)
__FTF_NUCLEAR.makeHidden()
__FTF_NUCLEAR.test()
# endregion
# endregion
