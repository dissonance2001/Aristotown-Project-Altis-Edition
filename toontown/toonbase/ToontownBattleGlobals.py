from ToontownGlobals import *
import math
import TTLocalizer
MAX_TOON_CAPACITY = 4
MAX_SUIT_CAPACITY = 6
BattleCamFaceOffFov = 40.0
BattleCamFaceOffPos = Point3(0, -10, 4)
BattleCamDefaultPos1 = Point3(0, -8.6, 18.5)
BattleCamDefaultHpr1 = Vec3(0, 0, 0)
BattleCamDefaultPos2 = Point3(0, -9.1, 22)
BattleCamDefaultHpr2 = Vec3(0, -56, 0)
BattleCamDefaultFov = 100
BattleCamMenuFov = 65.0
BattleCamMenuFov2 = 85.0
BattleCamJoinPos = Point3(0, -12, 13)
BattleCamJoinHpr = Vec3(0, -45, 0)
SkipMovie = 0
BaseHp = 15
Tracks = TTLocalizer.BattleGlobalTracks
NPCTracks = TTLocalizer.BattleGlobalNPCTracks
TrackColors = (
(211 / 255.0, 148 / 255.0, 255 / 255.0),
(255 / 255.0, 0 / 255.0, 0 / 255.0),
(79 / 255.0, 190 / 255.0, 76 / 255.0),
(255 / 255.0, 145 / 255.0, 66 / 255.0),
(255 / 255.0, 65 / 255.0, 199 / 255.0),
(254 / 255.0, 255 / 255.0, 0 / 255.0),
(93 / 255.0, 108 / 255.0, 239 / 255.0),
(67 / 255.0, 243 / 255.0, 255 / 255.0))
HEAL_TRACK = 0
TRAP_TRACK = 1
LURE_TRACK = 2
THROW_TRACK = 3
SQUIRT_TRACK = 4
ZAP_TRACK = 5
SOUND_TRACK = 6
DROP_TRACK = 7
NPC_RESTOCK_GAGS = 8
NPC_TOONS_HIT = 9
NPC_COGS_MISS = 10
NPC_DAMAGE_BOOST = 11
MIN_TRACK_INDEX = 0
MAX_TRACK_INDEX = 7
MIN_LEVEL_INDEX = 0
MAX_LEVEL_INDEX = 7
MAX_UNPAID_LEVEL_INDEX = 4
LAST_REGULAR_GAG_LEVEL = 6
UBER_GAG_LEVEL_INDEX = 8
NUM_GAG_TRACKS = 8
PropTypeToTrackBonus = {AnimPropTypes.Hydrant: SQUIRT_TRACK,
 AnimPropTypes.Mailbox: THROW_TRACK,
 AnimPropTypes.Trashcan: HEAL_TRACK}
Levels = [
[0, 20, 200, 800, 2000, 6000, 10000, 15000], # Toon-Up
[0, 20, 100, 800, 2000, 6000, 10000, 15000],  # Trap
[0, 20, 100, 800, 2000, 6000, 10000, 15000],  # Lure
[0, 20, 100, 800, 2000, 6000, 10000, 15000], # Throw
[0, 10, 50, 400, 2000, 6000, 10000, 15000],   # Squirt
[0, 10, 50, 400, 2000, 6000, 10000, 15000],   # Zap
[0, 20, 100, 500, 2000, 6000, 10000, 15000],   # Sound
[0, 20, 100, 500, 2000, 6000, 10000, 15000]]  # Drop
regMaxSkill = 15000
UberSkill = 0
MaxSkill = UberSkill + regMaxSkill
UnpaidMaxSkills = [
Levels[0][1] - 1,
Levels[1][1] - 1,
Levels[2][1] - 1,
Levels[3][1] - 1,
Levels[4][4] - 1,
Levels[5][4] - 1,
Levels[6][1] - 1,
Levels[7][1] - 1]
ExperienceCap = 15000

def gagIsPaidOnly(track, level):
    return Levels[track][level] > UnpaidMaxSkills[track]


def gagIsVelvetRoped(track, level):
    if level > 0:
        if track in [4, 5]:
            if level > 3:
                return True
        else:
            return True
    return False


MaxToonAcc = 95
StartingLevel = 0
CarryLimits = (
(
# Toon-Up
(10, 0, 0, 0, 0, 0, 0, 0),
(10, 5, 0, 0, 0, 0, 0, 0),
(15, 10, 5, 0, 0, 0, 0, 0),
(20, 15, 10, 5, 0, 0, 0, 0),
(25, 20, 15, 10, 3, 0, 0, 0),
(30, 25, 20, 15, 7, 3, 0, 0),
(30, 25, 20, 15, 7, 3, 2, 1),
(30, 25, 20, 15, 7, 3, 2, 1)),
(
# Trap
(10, 0, 0, 0, 0, 0, 0, 0),
(10, 5, 0, 0, 0, 0, 0, 0),
(15, 10, 5, 0, 0, 0, 0, 0),
(20, 15, 10, 5, 0, 0, 0, 0),
(25, 20, 15, 10, 3, 0, 0, 0),
(30, 25, 20, 15, 7, 3, 0, 0),
(30, 25, 20, 15, 7, 3, 2, 1),
(30, 25, 20, 15, 7, 3, 2, 1)),
(
# Lure
(10, 0, 0, 0, 0, 0, 0, 0),
(10, 5, 0, 0, 0, 0, 0, 0),
(15, 10, 5, 0, 0, 0, 0, 0),
(20, 15, 10, 5, 0, 0, 0, 0),
(25, 20, 15, 10, 3, 0, 0, 0),
(30, 25, 20, 15, 7, 3, 0, 0),
(30, 25, 20, 15, 7, 3, 2, 1),
(30, 25, 20, 15, 7, 3, 2, 1)),
(
# Throw
(10, 0, 0, 0, 0, 0, 0, 0),
(10, 5, 0, 0, 0, 0, 0, 0),
(15, 10, 5, 0, 0, 0, 0, 0),
(20, 15, 10, 5, 0, 0, 0, 0),
(25, 20, 15, 10, 3, 0, 0, 0),
(30, 25, 20, 15, 7, 3, 0, 0),
(30, 25, 20, 15, 7, 3, 2, 1),
(30, 25, 20, 15, 7, 3, 2, 1)),
(
# Squirt
(10, 0, 0, 0, 0, 0, 0, 0),
(10, 5, 0, 0, 0, 0, 0, 0),
(15, 10, 5, 0, 0, 0, 0, 0),
(20, 15, 10, 5, 0, 0, 0, 0),
(25, 20, 15, 10, 3, 0, 0, 0),
(30, 25, 20, 15, 7, 3, 0, 0),
(30, 25, 20, 15, 7, 3, 2, 1),
(30, 25, 20, 15, 7, 3, 2, 1)),
(
# Zap
(10, 0, 0, 0, 0, 0, 0, 0),
(10, 5, 0, 0, 0, 0, 0, 0),
(15, 10, 5, 0, 0, 0, 0, 0),
(20, 15, 10, 5, 0, 0, 0, 0),
(25, 20, 15, 10, 3, 0, 0, 0),
(30, 25, 20, 15, 7, 3, 0, 0),
(30, 25, 20, 15, 7, 3, 2, 1),
(30, 25, 20, 15, 7, 3, 2, 1)),
(
# Sound
(10, 0, 0, 0, 0, 0, 0, 0),
(10, 5, 0, 0, 0, 0, 0, 0),
(15, 10, 5, 0, 0, 0, 0, 0),
(20, 15, 10, 5, 0, 0, 0, 0),
(25, 20, 15, 10, 3, 0, 0, 0),
(30, 25, 20, 15, 7, 3, 0, 0),
(30, 25, 20, 15, 7, 3, 2, 1),
(30, 25, 20, 15, 7, 3, 2, 1)),
(
# Drop
(10, 0, 0, 0, 0, 0, 0, 0),
(10, 5, 0, 0, 0, 0, 0, 0),
(15, 10, 5, 0, 0, 0, 0, 0),
(20, 15, 10, 5, 0, 0, 0, 0),
(25, 20, 15, 10, 3, 0, 0, 0),
(30, 25, 20, 15, 7, 3, 0, 0),
(30, 25, 20, 15, 7, 3, 2, 1),
(30, 25, 20, 15, 7, 3, 2, 1)))
MaxProps = ((15, 40), (30, 60), (75, 100))
DLF_SKELECOG = 1
DLF_FOREMAN = 2
DLF_BOSS = 4
DLF_SUPERVISOR = 8
DLF_VIRTUAL = 16
DLF_REVIVES = 32
DLF_ELITE = 64
EXECUTIVE_HP_MULT = 1.5
EXECUTIVE_DMG_MULT = 1.2
EXECUTIVE_BASE_CHANCE = 30
GOVERNAUGHT_HP_MULT = 0.75
GOVERNAUGHT_DMG_MULT = 1.5
GOVERNAUGHT_BASE_CHANCE = 20
V2_BASE_CHANCE = 25
pieNames = ['cupcake', 'fruitpie-slice', 'creampie-slice', 'birthday-cake-slice', 'fruitpie', 'creampie', 'birthday-cake', 'wedding-cake', 'lawbook']
AvProps = (
('feather', 'bullhorn', 'lipstick', 'bamboocane','pixiedust', 'baton', 'pixiedust', 'baton'),
('banana', 'rake', 'marbles', 'spring', 'quicksand', 'trapdoor', 'xspot', 'tnt'),
('1dollar', 'smmagnet', '5dollar', 'bigmagnet', '10dollar', 'hypnogogs', '50dollar', 'hypnogogs'),
('cupcake', 'fruitpieslice', 'creampieslice', 'creampieslice', 'fruitpie', 'creampie', 'cake', 'cake'),
('flower', 'waterglass', 'watergun', 'waterballoon', 'bottle', 'firehose', 'stormcloud', 'stormcloud'),
('flower', 'waterglass', 'waterballoon', 'bottle', 'firehose','stormcloud', 'stormcloud', 'stormcloud'),
('kazoo', 'bikehorn', 'whistle', 'bugle', 'aoogah', 'elephant', 'foghorn', 'singing'),
('flowerpot', 'sandbag', 'bowlingball', 'anvil', 'weight', 'safe', 'boulder', 'piano'))
AvPropsNew = (
('inventory_feather', 'inventory_megaphone', 'inventory_lipstick', 'inventory_bamboo_cane', 'inventory_pixiedust', 'inventory_juggling_cubes', 'inventory_cannon', 'inventory_ladder'),
('inventory_banana_peel', 'inventory_rake', 'inventory_marbles', 'inventory_springboard', 'inventory_quicksand_icon', 'inventory_trapdoor', 'inventory_wreckingball', 'inventory_tnt'),
('inventory_1dollarbill', 'inventory_small_magnet', 'inventory_5dollarbill', 'inventory_big_magnet', 'inventory_10dollarbill', 'inventory_hypno_goggles', 'inventory_50dollarbill', 'inventory_screen'),
('inventory_cup_cake', 'inventory_fruit_pie_slice', 'inventory_cream_pie_slice', 'inventory_cake_slice', 'inventory_fruitpie', 'inventory_creampie', 'inventory_cake', 'inventory_wedding'),
('inventory_squirt_flower', 'inventory_glass_of_water', 'inventory_water_gun', 'inventory_waterballoon', 'inventory_seltzer_bottle', 'inventory_firehose', 'inventory_storm_cloud', 'inventory_geyser'),
('inventory_buzzer', 'inventory_rug', 'inventory_balloon', 'inventory_cart_battery', 'inventory_television', 'inventory_tazer', 'inventory_tesla_coil', 'inventory_lightning'),
('inventory_kazoo', 'inventory_bikehorn', 'inventory_whistle', 'inventory_bugle', 'inventory_aoogah', 'inventory_elephant','inventory_fog_horn', 'inventory_opera_singer'),
('inventory_flower_pot', 'inventory_sandbag', 'inventory_bowlingball', 'inventory_anvil', 'inventory_weight', 'inventory_safe_box', 'inventory_boulder', 'inventory_piano'))
AvPropStrings = TTLocalizer.BattleGlobalAvPropStrings
AvPropStringsSingular = TTLocalizer.BattleGlobalAvPropStringsSingular
AvPropStringsPlural = TTLocalizer.BattleGlobalAvPropStringsPlural
AvPropAccuracy = (
(70, 70, 70, 70, 70, 70, 70, 70),
(0, 0, 0, 0, 0, 0, 0, 0),
(50, 50, 60, 60, 70, 70, 90, 90),
(75, 75, 75, 75, 75, 75, 75, 75),
(95, 95, 95, 95, 95, 95, 95, 95),
(100, 100, 100, 100, 100, 100, 100, 100),
(95, 95, 95, 95, 95, 95, 95, 95),
(80, 80, 80, 80, 80, 80, 80, 80))
AvDropBonusAccuracy = (90, 90, 90, 90, 90, 90, 90, 90)
AvTrackAccStrings = TTLocalizer.BattleGlobalAvTrackAccStrings
AvPropDamage = (
# Toon-Up
(((10, 10), (Levels[0][0], Levels[0][1])),
((12, 12), (Levels[0][1], Levels[0][2])),
((24, 24), (Levels[0][2], Levels[0][3])),
((45, 45), (Levels[0][3], Levels[0][4])),
((60, 60), (Levels[0][4], Levels[0][5])),
((90, 90), (Levels[0][5], Levels[0][6])),
((95, 95), (Levels[0][6], Levels[0][7])),
((135, 135), (Levels[0][7], MaxSkill))),
# Trap
(((16, 16), (Levels[1][0], Levels[1][1])),
((32, 32), (Levels[1][1], Levels[1][2])),
((50, 50), (Levels[1][2], Levels[1][3])),
((80, 80), (Levels[1][3], Levels[1][4])),
((120, 120), (Levels[1][4], Levels[1][5])),
((170, 170), (Levels[1][5], Levels[1][6])),
((230, 230), (Levels[1][6], Levels[1][7])),
((290, 290), (Levels[1][7], MaxSkill))),
# Lure
(((0, 0), (0, 0)),
((0, 0), (0, 0)),
((0, 0), (0, 0)),
((0, 0), (0, 0)),
((0, 0), (0, 0)),
((0, 0), (0, 0)),
((0, 0), (0, 0)),
((0, 0), (0, 0))),
# Throw
(((8, 8), (Levels[3][0], Levels[3][1])),
((13, 13), (Levels[3][1], Levels[3][2])),
((21, 21), (Levels[3][2], Levels[3][3])),
((35, 35), (Levels[3][3], Levels[3][4])),
((56, 56), (Levels[3][4], Levels[3][5])),
((90, 90), (Levels[3][5], Levels[3][6])),
((130, 130), (Levels[3][6], Levels[3][7])),
((170, 170), (Levels[3][7], MaxSkill))),
# Squirt
(((4, 4), (Levels[4][0], Levels[4][1])),
((8, 8), (Levels[4][1], Levels[4][2])),
((16, 16), (Levels[4][2], Levels[4][3])),
((21, 21), (Levels[4][3], Levels[4][4])),
((30, 30), (Levels[4][4], Levels[4][5])),
((60, 60), (Levels[4][5], Levels[4][6])),
((90, 90), (Levels[4][6], Levels[4][7])),
((120, 120), (Levels[4][7], MaxSkill))),
# Zap
(((12, 12), (Levels[5][0], Levels[5][1])),
((20, 20), (Levels[5][1], Levels[5][2])),
((36, 36), (Levels[5][2], Levels[5][3])),
((60, 60), (Levels[5][3], Levels[5][4])),
((90, 90), (Levels[5][4], Levels[5][5])),
((140, 140), (Levels[5][5], Levels[5][6])),
((190, 190), (Levels[5][6], Levels[5][7])),
((240, 240), (Levels[5][7], MaxSkill))),
# Sound
(((5, 5), (Levels[3][0], Levels[3][1])),
((10, 10), (Levels[6][1], Levels[6][2])),
((16, 16), (Levels[6][2], Levels[6][3])),
((23, 23), (Levels[6][3], Levels[6][4])),
((30, 30), (Levels[6][4], Levels[6][5])),
((50, 50), (Levels[6][5], Levels[6][6])),
((70, 70), (Levels[6][6], Levels[6][7])),
((90, 90), (Levels[6][7], MaxSkill))),
# Drop
(((12, 12), (Levels[6][0], Levels[6][1])),
((20, 20), (Levels[6][1], Levels[6][2])),
((35, 35), (Levels[6][2], Levels[6][3])),
((56, 56), (Levels[6][3], Levels[6][4])),
((90, 90), (Levels[6][4], Levels[6][5])),
((140, 140), (Levels[6][5], Levels[6][6])),
((200, 200), (Levels[6][6], Levels[6][7])),
((250, 250), (Levels[6][7], MaxSkill))))
ATK_SINGLE_TARGET = 0
ATK_GROUP_TARGET = 1
AvPropTargetCat = ((ATK_SINGLE_TARGET, ATK_GROUP_TARGET, ATK_SINGLE_TARGET, ATK_GROUP_TARGET, ATK_SINGLE_TARGET, ATK_GROUP_TARGET, ATK_SINGLE_TARGET, ATK_GROUP_TARGET),
(ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET),
(ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET, ATK_SINGLE_TARGET),
(ATK_GROUP_TARGET, ATK_GROUP_TARGET, ATK_GROUP_TARGET, ATK_GROUP_TARGET, ATK_GROUP_TARGET, ATK_GROUP_TARGET, ATK_GROUP_TARGET, ATK_GROUP_TARGET))
LURE_KNOCKBACK_VALUE = 1
AvLureKnockback = (1.3, 1, 1.3, 1, 1.3, 1, 1.7, 1.5)
AvPropTarget = (0, 3, 0, 2, 3, 3, 3, 3, 3)
AvLureRounds = (1, 1, 2, 2, 3, 3, 4, 4)
AvZapJumps = ((3, 2.25, 1.5),
              (3, 2.5, 2),
              (3, 2.75, 2.5))
InstaKillChance = [2, 3, 5, 8, 10, 15, 20, 20]
DropMissChance = [40, 40, 40, 40, 40, 40, 40, 40]
LureMissChance = [5, 10, 5, 10, 5, 10, 5, 10]
AvSoakRounds = (3, 3, 3, 3, 4, 4, 4, 4)
AvMarkRounds = (1, 1, 1, 1, 1, 1, 1, 1)
AvDazeRounds = (2, 2, 2, 2, 2, 2, 2, 2)
AvSelfHealThrow = (4, 6, 8, 10, 14, 28, 36, 44)
AvSoakDefReduction = 15
AvDazeDefReduction = 10
AvMarkBoost = 10
AvZapBoost = 300
TRAP_EXECUTIVE_BONUS = 0.3
TRAP_HEALTHY_BONUS = 0.2


def getTrapDamage(trapLevel, toon, suit = None, executive = None):
    if suit:
        executive = suit.getExecutive() or suit.getGovernaught() or suit.getManager()
    damage = getAvPropDamage(TRAP_TRACK, trapLevel, toon.experience.getExp(TRAP_TRACK))
    organicBonus = toon.checkGagBonus(TRAP_TRACK, trapLevel)
    if executive and organicBonus:
        damage += math.ceil((damage * TRAP_EXECUTIVE_BONUS) + 1)
    elif executive:
        damage += math.ceil(damage * TRAP_EXECUTIVE_BONUS)
    return int(damage)

def getAvPropDamage(attackTrack, attackLevel, exp, organicBonus = False, propBonus = False, propAndOrganicBonusStack = False):
    minD = AvPropDamage[attackTrack][attackLevel][0][0]
    maxD = AvPropDamage[attackTrack][attackLevel][0][1]
    minE = AvPropDamage[attackTrack][attackLevel][1][0]
    maxE = AvPropDamage[attackTrack][attackLevel][1][1]
    expVal = min(exp, maxE)
    expPerHp = float(maxE - minE + 1) / float(maxD - minD + 1)
    damage = math.floor((expVal - minE) / expPerHp) + minD
    if damage <= 0:
        damage = minD
    return damage


def getDamageBonus(normal, track = 4):
    bonus = 0
    return bonus


def isGroup(track, level):
    return AvPropTargetCat[AvPropTarget[track]][level]


def getCreditMultiplier(floorIndex):
    return 1 + floorIndex * 0.5


def getFactoryCreditMultiplier(factoryId):
    return 4.0


def getFactoryMeritMultiplier(factoryId):
    return 4.0


def getMintCreditMultiplier(mintId):
    return {CashbotMintIntA: 4.0,
     CashbotMintIntB: 5.0,
     CashbotMintIntC: 6.0}.get(mintId, 2.0)


def getStageCreditMultiplier(floor):
    return getCreditMultiplier(floor) * 2

def getBoardOfficeCreditMultiplier(boardofficeId):
    return {BoardOfficeIntA: 4.0,
     BoardOfficeIntB: 5.0,
     BoardOfficeIntC: 6.0}.get(boardofficeId, 2.0)


def getCountryClubCreditMultiplier(countryClubId):
    return {BossbotCountryClubIntA: 4.0,
     BossbotCountryClubIntB: 5.0,
     BossbotCountryClubIntC: 6.0}.get(countryClubId, 2.0)


def getBossBattleCreditMultiplier(battleNumber):
    return 1 + battleNumber


def getInvasionMultiplier():
    return 2.0


def getMegaMultiplier():
    return 3.0


def getMoreXpHolidayMultiplier():
    return 2.0


def encodeUber(trackList):
    bitField = 0
    for trackIndex in xrange(len(trackList)):
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
    if flagMask == 'unknown' or flagMask < 0:
        return -1
    else:
        return getUberFlag(flagMask, index)

ValidStatusConditions = (
    # Manager Calculators
    'rageBuilding',
    'powerhouseRotation',
    'groundbreakercalculator',
    'costscalculator',
    'insurancecalculator',
    'snappedcalculator',
    'sanctioncalculator',
    'bindingscalculator',
    'soakedcalculator',
    'soakedcalculator2',
    'damageupcalculator1',
    'damageupcalculator2',
    'markedcalculator',
    'markedcalculator2',
    'bashcalculator',
    'bellowattack',
    'immunecalculator',
    'brokenconnectioncalculator',
    'voicemailcalculator',
    'mulligancalculator',
    'mulligancalculator2',
    'mulligancalculator3',
    'mulligancalculator4',
    'collectcallfeescalculator',
    'collectcallcalculator',
    'collectcallcalculator3',
    'busycalculator',
    'wiretappedcalculator',
    'rotationcalculator',
    'papercutcalculator',
    'explodingcalculator',
    'explodingcalculator2',
    'refinementcalculator',
    'gavelcalculator',
    'bellowcalculator',
    'bellowcalculator2',
    'bookkeepingcalculator',
    'rolledcalculator',
    'diceroulettecalculator',
    'freecruisecalculator',
    'conductioncalculator',
    'vulnerablecalculator',
    'HRdamagereduction',
    'sanctioncalculator2',
    'sanctioncalculator3',
    'sanctioncalculator4',
    'snipecalculator',
    'snipecalculator2',
    'refinementcalculator',
    'refinemanagercalculator',
    'headrollercalculator',
    'headroller2calculator',
    'calculatingcalculator',
    'dropcalculator',
    'zapcalculator',
    'toonupcalculator',
    'trapcalculator',
    'syphoncalculator',
    'wiretappedcalculator',
    'cheercalculator',
    'bindingscalculator2',
    'sanctioncalculator2',
    'gagbansnipe',
    'mulligansnipe',
    'breachvulnerable',
    'breachgagban',
    'gavelcalculator2',
    'collectcallsnipe',
    'vulnerablesnipe',
    'bookkeepersnipe',
    'highpressurecalculator',
    'heatwavecalculator',
    'heatwavecalculationcalculator',
    'promotioncalculator',
    'unionduescalculator',
    'unionduescalculationcalculator',
    'unionbustercalculator',
    'unionbustcalculator',
    'unionwagescalculator',
    'breachcalculator',
    'contractenforcementcalculator',
    'extortioncalculator',
    'extortioncalculator2',
    'profiteeringcalculator',
    'hustlingcalculator',
    'radioinfrequencycalculator',
    'hottakecalculator',
    'overmodulatedcalculator',
    'dancesessioncalculator',
    'filmmakercalculator',
    'directorcalculator',
    'dead',
    'dancesession',
    'directorscutscalculator',
    'trickofthelight',
    'hollywoodcalculator',
    'gameovercalculator',
    'gametimecalculator',
    'electricshockcalculator',
    'target2',
    'silspawn',
    'target3',
    'target4',
    'target5',
    'target6',
    'spawnsteno',
    'deadsteno',
    'deadgator',
    'activesteno',
    'activegator',
    'activecase',
    'activegoat',
    'dotfinished',
    'healfinished',
    'managerspawn',
    'deadgoat',
    'deadsafe',
    'deadracket',
    'deadunion',
    'deadradio',
    'deadamb',
    'deadbook',
    'spawncase',
    'spawngator',
    'spawngoat',
    'spawnwire',
    'spawnamb',
    'spawnpower',
    'spawnbook',
    'spawnsafe',
    'spawnracket',
    'spawnunion',
    'spawnradio',
    'ambtarget2',
    'ambtarget3',
    'ambtarget4',
    'ambtarget5',
    'ambtarget6',
    'ambheadrollertarget',
    'advancementcalculator',
    'headrollertargetcalculator',
    'barcalculator',
    'spawncalculator',
    'deadcase',
    'deadpower',
    'deadunion',
    'cinemacalculator',
    'choreocalculator',
    'HRpowertrip',
    'HRconduction',
    'HRrolled',
    'HRdiceroulette',
    'HRfreecruise',

    # Cog Status Effects
    'zapped',
    'killedbyroller',
    'bookkeeping',
    'bookkeeping2',
    'bantracks',
    'cannotMiss',
    'alwaysMiss',
    'cannotDodge',
    'alwaysDodge',
    'dodgy',
    'enraged',
    'shielding',
    'lureImmune',
    'soakImmune',
    'damageReduction',
    'ban2levels',
    'ban2tracks',
    'bash1',
    'bash2',
    'bash3',
    'bash4',
    'bash5',
    'extraAttack',
    'extraAttack2',
    'extraAttack3',
    'extraAttack4',
    'extraAttack5',
    'extraAttack6',
    'extraAttack7',
    'extraAttack8',
    'extraAttack9',
    'extraAttack10',
    'extraGlower',
    'extraGlower2',
    'extraGlower3',
    'extraGlower4',
    'extraGlower5',
    'extraGlower6',
    'extraGlower7',
    'extraGlower8',
    'extraGlower9',
    'extraGlower10',
    'deadDerrick',
    'deadDOLA',
    'deadDOPR',
    'extraPeckingOrder',
    'absorbingHR',
    'aceInTheHole',
    'zapImmune',
    'deathcheck',
    'kbImmune',
    'phase3',
    'syphon',
    'absorbing',
    'vulnerable',
    'desperation',
    'absorbing2',
    'dazed2',
    'phase2',
    'frozen',
    'soaked',
    'lured',
    'marked',
    'immune',
    'dazed',
    'sued',
    'suemovie',
    'contracted',
    'killedbyvideo',
    'noKB',
    'firsttrick',
    'secondtrick',
    'thirdtrick',
    'fourthtrick',
    'silhouettespawn',
    'vulnerablebroadcaster',
    'vulnerablesilhouette1',
    'vulnerablesilhouette2',
    'vulnerablesilhouette3',
    'brokenconnection',
    'vulnerablevideographer',
    'collectcallcalculator2',
    'desperationcalculator',
    'lureResist',
    'throwbookcalculator',
    'whirlwindcalculator',
    'paperfilingcalculator',

    # Toon Status Effects
    'hidden',
    'burned',
    'noUnites',
    'markToon',
    'raisedAnte',
    'confused',
    'encore2',
    'snappedtarget2',
    'snappedtarget3',
    'snappedtarget4',
    'mulligan',
    'mulligan2',
    'mulligan3',
    'mulligan4',
    'markedforsanction',
    'bound',
    'rushJobCompleted',
    'useToonUp',
    'useTrap',
    'useLure',
    'useThrow',
    'useSquirt',
    'useZap',
    'useSound',
    'useDrop',
    'snappedtarget2',
    'snapped',
    'snappedtarget',
    'allGagBoost',
    'corruptedtarget',
    'noGags',
    'healBoost',
    'insured',
    'noToonUpGags',
    'banned',
    'banned2',
    'banned3',
    'trapBoost',
    'noTrapGags',
    'bookkeepingtoon',
    'lureBoost',
    'nolevel4s',
    'noLureGags',
    'soundBoost',
    'noSoundGags',
    'usedThrow',
    'usedTrap',
    'usedSquirt',
    'usedSound',
    'usedDrop',
    'usedHeal',
    'usedZap',
    'usedLure',
    'throwBoost',
    'noThrowGags',
    'squirtBoost',
    'nolevel7s',
    'soakToon',
    'markToon',
    'nolevel6s',
    'nolevel5s',
    'nolevel8s',
    'noSquirtGags',
    'zapBoost',
    'noZapGags',
    'dropBoost',
    'noDropGags',
    'noFires',
    'noSOS',
    'noSues',
    'encore',
    'winded',
    'cheer',
    'corruption',
    'groupDamageDown',
    'noDamage',
    'busted',
    'collectcalled',
)