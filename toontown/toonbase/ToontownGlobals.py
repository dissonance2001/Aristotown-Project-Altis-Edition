import TTLocalizer
from otp.otpbase.OTPGlobals import *
from toontown.toonbase.ToonPythonUtil import Enum, invertDict
from pandac.PandaModules import BitMask32, Vec4
from toontown.toonbase.ContentPackCompatibility import ContentPackCompatibility
MapHotkeyOn = 'alt'
MapHotkeyOff = 'alt-up'
MapHotkey = 'alt'
AccountDatabaseChannelId = 4008
ToonDatabaseChannelId = 4021
DoodleDatabaseChannelId = 4023
DefaultDatabaseChannelId = AccountDatabaseChannelId
DatabaseIdFromClassName = {'Account': AccountDatabaseChannelId}
CogHQCameraFov = 60.0
BossBattleCameraFov = 72.0
MakeAToonCameraFov = 48.0
VPElevatorFov = 53.0
CFOElevatorFov = 43.0
CJElevatorFov = 59.0
CEOElevatorFov = 59.0
CBElevatorFov = 42.0
CogdoFov = 45.0
WantPromotion = 0
PendingPromotion = 1
CeilingBitmask = BitMask32(256)
FloorEventBitmask = BitMask32(16)
PieBitmask = BitMask32(256)
PetBitmask = BitMask32(8)
CatchGameBitmask = BitMask32(16)
CashbotBossObjectBitmask = BitMask32(16)
FurnitureSideBitmask = BitMask32(32)
FurnitureTopBitmask = BitMask32(64)
FurnitureDragBitmask = BitMask32(128)
PetLookatPetBitmask = BitMask32(256)
PetLookatNonPetBitmask = BitMask32(512)
BanquetTableBitmask = BitMask32(1024)
FullPies = 65535
CogHQCameraFar = 900.0
CogHQCameraNear = 1.0
CashbotHQCameraFar = 2000.0
CashbotHQCameraNear = 1.0
LawbotHQCameraFar = 3000.0
LawbotHQCameraNear = 1.0
BossbotHQCameraFar = 3000.0
BossbotHQCameraNear = 1.0
SpeedwayCameraFar = 8000.0
SpeedwayCameraNear = 1.0
MaxMailboxContents = 30
MaxHouseItems = 100
MaxAccessories = 50
ExtraDeletedItems = 5
DeletedItemLifetime = 7 * 24 * 60
CatalogNumWeeksPerSeries = 13
CatalogNumWeeks = 78
PetFloorCollPriority = 5
PetPanelProximityPriority = 6
P_NoTrunk = -28
P_AlreadyOwnBiggerCloset = -27
P_ItemAlreadyRented = -26
P_OnAwardOrderListFull = -25
P_AwardMailboxFull = -24
P_ItemInPetTricks = -23
P_ItemInMyPhrases = -22
P_ItemOnAwardOrder = -21
P_ItemInAwardMailbox = -20
P_ItemAlreadyWorn = -19
P_ItemInCloset = -18
P_ItemOnGiftOrder = -17
P_ItemOnOrder = -16
P_ItemInMailbox = -15
P_PartyNotFound = 14
P_WillNotFit = -13
P_NotAGift = -12
P_OnOrderListFull = -11
P_MailboxFull = -10
P_NoPurchaseMethod = -9
P_ReachedPurchaseLimit = -8
P_NoRoomForItem = -7
P_NotShopping = -6
P_NotAtMailbox = -5
P_NotInCatalog = -4
P_NotEnoughMoney = -3
P_InvalidIndex = -2
P_UserCancelled = -1
P_ItemAvailable = 1
P_ItemOnOrder = 2
P_ItemUnneeded = 3
GIFT_user = 0
GIFT_admin = 1
GIFT_RAT = 2
GIFT_mobile = 3
GIFT_cogs = 4
GIFT_partyrefund = 5
FM_InvalidItem = -7
FM_NondeletableItem = -6
FM_InvalidIndex = -5
FM_NotOwner = -4
FM_NotDirector = -3
FM_RoomFull = -2
FM_HouseFull = -1
FM_MovedItem = 1
FM_SwappedItem = 2
FM_DeletedItem = 3
FM_RecoveredItem = 4
SPDonaldsBoat = 3
SPMinniesPiano = 4
CEVirtual = 14
MaxHpLimit = 200
ExpMoneyCarryReward = 500
ExpTrainingPointReward = 1
ExpGagCarryReward = 10
MaxCarryLimit = 120
MaxQuestCarryLimit = 4
GravityValue = 32.174
MaxCogSuitLevel = 50 - 1
MaxToonLevel = 70 - 1
CogSuitHPLevels = (15 - 1,
 20 - 1,
 30 - 1,
 40 - 1,
 50 - 1)
CogReviveSuitHPLevels = (25 - 1,
 50 - 1)
ExperienceTrainingPointLevels = (4 - 1,
8 - 1,
12 - 1,
16 - 1,
20 - 1,
28 - 1,
38 - 1,
48 - 1,
58 - 1,
68 - 1)
ExperienceGagLevels = (10 - 1,
20 - 1,
30 - 1,
40 - 1,
50 - 1,
60 - 1,
70 - 1,
80 - 1)
ExperienceMoneyLevels = (5 - 1,
10 - 1,
15 - 1,
20 - 1,
25 - 1,
30 - 1,
35 - 1,
40 - 1,
45 - 1,
50 - 1,
55 - 1,
60 - 1,
65 - 1,
70 - 1)
FishingRodCosts = [0, 750, 2500, 5000, 10000]
BucketCosts = {20: 0,
 30: 1000,
 40: 2000,
 50: 3000,
 60: 4000,
 70: 5000,
 80: 6000,
 90: 7000,
 100: 8000}
TTLocalizer.InterfaceFont = ContentPackCompatibility.resolveFontPath(
    TTLocalizer.InterfaceFont
)
TTLocalizer.ToonFont = ContentPackCompatibility.resolveFontPath(
    TTLocalizer.ToonFont
)
TTLocalizer.MinnieFont = ContentPackCompatibility.resolveFontPath(
    TTLocalizer.MinnieFont
)

setInterfaceFont(TTLocalizer.InterfaceFont)
setSignFont(TTLocalizer.SignFont)
from toontown.toontowngui import TTDialog
setDialogClasses(TTDialog.TTDialog, TTDialog.TTGlobalDialog)
ToonFont = None
BuildingNametagFont = None
MinnieFont = None
SuitFont = None

def getToonFont():
    global ToonFont
    if ToonFont == None:
        ToonFont = loader.loadFont(TTLocalizer.ToonFont, lineHeight = 1.0)
    return ToonFont


def getBuildingNametagFont():
    global BuildingNametagFont
    if BuildingNametagFont == None:
        BuildingNametagFont = loader.loadFont(TTLocalizer.BuildingNametagFont)
    return BuildingNametagFont


def getMinnieFont():
    global MinnieFont
    if MinnieFont == None:
        MinnieFont = loader.loadFont(TTLocalizer.MinnieFont)
    return MinnieFont


def getSuitFont():
    global SuitFont
    if SuitFont == None:
        SuitFont = loader.loadFont(TTLocalizer.SuitFont, pixelsPerUnit = 40, spaceAdvance = 0.25, lineHeight = 1.0)
    return SuitFont


DonaldsDock = 1000
ToontownCentral = 2000
TheBrrrgh = 3000
MinniesMelodyland = 4000
DaisyGardens = 5000
OutdoorZone = 6000
AcornAvenue = 6100
PeanutPlace = 6200
WalnutWay = 6300
LegumeLane = 6400
FunnyFarm = 500000
GoofySpeedway = 8000
YeOlde = 7000
Toonseltown = 18000 
SkyClan = 22000
KnightKnoll = 7100
NobleNook = 7200
WizardWay=7300
DonaldsDreamland = 9000
BarnacleBoulevard = 1100
SeaweedStreet = 1200
LighthouseLane = 1300
AhoyAvenue = 1400
SillyStreet = 2100
LoopyLane = 2200
PunchlinePlace = 2300
WackyWay = 2400
WalrusWay = 3100
SleetStreet = 3200
PolarPlace = 3300
ArcticAvenue = 3400
AltoAvenue = 4100
BaritoneBoulevard = 4200
TenorTerrace = 4300
SopranoStreet = 4400
ElmStreet = 5100
MapleStreet = 5200
OakStreet = 5300
RoseValley = 5400
LullabyLane = 9100
PajamaPlace = 9200
TwilightTerrace = 9300
ToonHall = 2513
PacesetterLobby = 9613
DerrickmanInterior = 2921
PizzariaInterior = 3740
ToontownCentralOld = 20000
SchoolHouse = 2516
OTGagShop = 7502
Dungeon = 7507
CountErfitLobby = 25200
CountErfitBattle = 25201
HoodHierarchy = {ToontownCentral: (SillyStreet, LoopyLane, PunchlinePlace, WackyWay),
 DonaldsDock: (BarnacleBoulevard, SeaweedStreet, LighthouseLane, AhoyAvenue),
 TheBrrrgh: (WalrusWay, SleetStreet, PolarPlace, ArcticAvenue),
 YeOlde: (KnightKnoll, NobleNook, WizardWay),
 MinniesMelodyland: (AltoAvenue, BaritoneBoulevard, TenorTerrace, SopranoStreet),
 DaisyGardens: (ElmStreet, MapleStreet, OakStreet, RoseValley),
 OutdoorZone: (AcornAvenue, PeanutPlace, WalnutWay, LegumeLane),
 DonaldsDreamland: (LullabyLane, PajamaPlace, TwilightTerrace),
 GoofySpeedway: (),
 Toonseltown: (),
 SkyClan: (),              
 ToontownCentralOld: ()}
WelcomeValleyToken = 0

# Street Manager Spawns
streetMgrs = ["duckshfl", "ddiver", "gatekeep", "bellring", 'mouthp', "fires", "treek", "fbed"]
streetMgrs2Zones = {"duckshfl": [SillyStreet, LoopyLane, PunchlinePlace, WackyWay],
                    "ddiver": [BarnacleBoulevard, SeaweedStreet, LighthouseLane, AhoyAvenue],
                    "gatekeep": [KnightKnoll, NobleNook, WizardWay],
                    "bellring": [ElmStreet, MapleStreet, OakStreet, RoseValley],
                    'mouthp': [AltoAvenue, BaritoneBoulevard, TenorTerrace, SopranoStreet],
                    "fires": [WalrusWay, SleetStreet, PolarPlace, ArcticAvenue],
                    "treek": [AcornAvenue, PeanutPlace, WalnutWay, LegumeLane],
                    "fbed": [LullabyLane, PajamaPlace, TwilightTerrace]}
streetMgrs2Levels = {"duckshfl": 5,
                     "ddiver": 7,
                     "gatekeep": 10,
                     "bellring": 13,
                     'mouthp': 16,
                     "fires": 20,
                     "treek": 24,
                     "fbed": 30}

# Manager Music
animSuitHeadsPosedNeutral = ('ddiver', 'chairman', 'cbr', 'shw', 'mg', 'phouse', 'racket', 'bookkeep', 'chairman2')
noCustomMusicManagers = ["bdirector", "ghd", "sya", "radiog", "ubuster", "racket", "safesupervis", "redd", "wsi", "erfit", "ambass", "wtapper", "bkeeper", "phouse", "arbit", "videog"]
managerMusic = {"djockey": "phase_3.5/audio/bgm/TC_SZ_SH_encntr.ogg",
                "ptjockey": "phase_3.5/audio/bgm/TC_SZ_SH_encntr.ogg",
                "derrman": "phase_4/audio/bgm/derrick/encntr_derrick.ogg",
                "derrhand": "phase_12/audio/bgm/directors_encntr.ogg",
                "dopa": "phase_12/audio/bgm/directors_encntr.ogg",
                "duckshfl": "phase_10/audio/bgm/merc/street_duckshuffler.ogg",
                "bellring": "phase_9/audio/bgm/merc/street_bellringer.ogg",
                "treek": "phase_10/audio/bgm/merc/street_treekiller.ogg",
                "fbed": "phase_12/audio/bgm/merc/street_featherbedder.ogg",
                "prethink": "phase_9/audio/bgm/merc/instance_prethinker_battle.ogg",
                "mslacker": "phase_9/audio/bgm/merc/instance_multislacker_battle.ogg",
                "mplayer": "phase_12/audio/bgm/merc/instance_majorplayer_battle_2.ogg",
                "mplayer2": "phase_12/audio/bgm/merc/instance_majorplayer_battle_2.ogg",
                "pcrat": "phase_10/audio/bgm/merc/instance_plutocrat_battle.ogg",
                "psetter": "phase_9/audio/bgm/merc/instance_pacesetter_battle.ogg",
                "chainsaw": "phase_12/audio/bgm/merc/instance_chainsaw_battle_2.ogg",
                "chainsaw2": "phase_12/audio/bgm/merc/instance_chainsaw_battle_3.ogg",
                "rainmake": "phase_11/audio/bgm/merc/instance_rainmaker_battle_empty.ogg",
                "ddiver": "phase_14/audio/bgm/merc/street_deepdiver.ogg",
                "fires": "phase_12/audio/bgm/merc/street_firestarter.ogg",
                "dola": "phase_6/audio/bgm/dola_encntr.ogg",
                "gatekeep": "phase_14/audio/bgm/merc/street_gatekeeper.ogg",
                "whunter": "phase_11/audio/bgm/merc/instance_witchhunter_battle.ogg",
                "dopr": "phase_7/audio/bgm/dopr_encntr.ogg",
                "mouthp": "phase_11/audio/bgm/merc/street_mouthpiece.ogg",
                "dold": "phase_12/audio/bgm/directors_encntr.ogg",
                "erclaim": "phase_13/audio/bgm/halloween/encntr_countErclaim.ogg",
                "lgator": "phase_11/audio/bgm/LB_litigation_litigator.ogg",
                "caseman": "phase_11/audio/bgm/LB_litigation_casemgr.ogg",
                "stenog": "phase_11/audio/bgm/LB_litigation_stenograph.ogg",
                "sgoat": "phase_11/audio/bgm/LB_litigation_scapegoat.ogg",
                "hroller": "phase_13/audio/bgm/april_toons/highroller/cc_s_bgm_ara_hroller_int_battle_2.ogg",
                "hrollers": "phase_13/audio/bgm/april_toons/highroller/BONUSROUND.ogg",
                "hroller2": "phase_13/audio/bgm/april_toons/highroller/BONUSROUND.ogg",
                "judy": "phase_11/audio/bgm/LB_courtyard_encntr.ogg",
                "charon": "phase_10/audio/bgm/merc/instance_plutocrat_investors.ogg",
                "nix": "phase_10/audio/bgm/merc/instance_plutocrat_investors.ogg",
                "hydra": "phase_10/audio/bgm/merc/instance_plutocrat_investors.ogg",
                "styx": "phase_10/audio/bgm/merc/instance_plutocrat_investors.ogg",
                "kerberos": "phase_10/audio/bgm/merc/instance_plutocrat_investors.ogg",
                "ottoman": "phase_7/audio/bgm/building/boardbot/building_g_final.ogg",
                "chairman": "phase_7/audio/bgm/building/boardbot/building_g_final.ogg",
                "crystal": "phase_7/audio/bgm/building/boardbot/building_g_final.ogg",
                "dvking": "phase_7/audio/bgm/building/boardbot/building_g_final.ogg",
                "foreman": "phase_9/audio/bgm/SB_factory_boss.ogg",
                "supervis": "phase_10/audio/bgm/CB_mint_encntr_boss.ogg",
                "clerk": "phase_11/audio/bgm/LB_office_encntr_boss.ogg",
                "clubpres": "phase_12/audio/bgm/BB_club_encntr_boss.ogg"}


# Colors for Loading Screens / Title Text
DEFAULTCOLOR = (1.0, 0.0, 0.0, 1.0)
TTCOLOR = (1.0, 0.5, 0.4, 1.0)
DDCOLOR = (0.8, 0.6, 0.5, 1.0)
BRCOLOR = (0.3, 0.6, 1.0, 1.0)
MMCOLOR = (1.0, 0.5, 0.5, 1.0)
DGCOLOR = (0.8, 0.6, 1.0, 1.0)
DLCOLOR = (1.0, 0.9, 0.5, 1.0)
OZCOLOR = (1.0, 0.5, 0.4, 1.0)
GSCOLOR = (1.0, 0.5, 0.4, 1.0)

BossbotHQ = 10000
BossbotLobby = 10100
BossbotCountryClubIntA = 10500
BossbotCountryClubIntB = 10600
BossbotCountryClubIntC = 10700
SellbotHQ = 11000
SellbotLobby = 11100
SellbotMultislackerLobby = 11300
SellbotFactoryExt = 11200
SellbotFactoryInt = 11500
CashbotHQ = 12000
CashbotLobby = 12100
CashbotMintIntA = 12500
CashbotMintIntB = 12600
CashbotMintIntC = 12700
LawbotHQ = 13000
LawbotLobby = 13100
LawbotLounge = 13700  # OCLO Lobby
LawbotOfficeExt = 13200
LawbotOfficeInt = 13300
LawbotStageIntA = 13300
LawbotStageIntB = 13400
LawbotStageIntC = 13500
LawbotStageIntD = 13600
ZoneIdrDefault      = 0
ZoneIdrDerrickMan   = 1
ZoneIdrDOLA         = 2
ZoneIdrDungeon      = 3
ZoneIdrVP           = 4
ZoneIdrCFO          = 5
ZoneIdrCLO          = 6
ZoneIdrCEO          = 7
ZoneIdrDirectors    = 8
ZoneIdrChairman     = 9
ZoneIdrCount        = 10
ZoneIdrFactory      = 11
ZoneIdrCoin         = 12
ZoneIdrDollar       = 13
ZoneIdrBullion      = 14
ZoneIdrAOffice      = 15
ZoneIdrBOffice      = 16
ZoneIdrCOffice      = 17
ZoneIdrDOffice      = 18
ZoneIdrFront        = 19
ZoneIdrMiddle       = 20
ZoneIdrBack         = 21
ZoneIdrBDA          = 22
ZoneIdrBDB          = 23
ZoneIdrBDC          = 24
ZoneIdrEstate       = 25
ZoneIdrRestoration  = 26
ZoneIdrErfit        = 27
ZoneIdrTutorial     = 28
ZoneIdrLastNum      = 29  # make this the last one ALWAYS

BoardbotHQ = 19000
BoardbotLobby = 19100
BoardbotOfficeLobby = 19200
BoardOfficeIntA = 19500
BoardOfficeIntB = 19600
BoardOfficeIntC = 19700

TechbotHQ = 21000
TechbotLobby = 21100

# Dedicated client hood used only by the dynamically allocated High Roller
# instance.  It deliberately does not share CashbotHQ's loader or title.
HighRollerHQ = 14000

Tutorial = 15000
MyEstate = 16000
GolfZone = 17000
PartyHood = 24000
HoodsAlwaysVisited = [17000, 18000]
WelcomeValleyBegin = 26000
WelcomeValleyEnd = 61000
DynamicZonesBegin = 61000
DynamicZonesEnd = 1 << 20
cogDept2index = {'c': 0,
 'l': 1,
 'm': 2,
 's': 3,
 'g': 4,
 't': 5,}
cogIndex2dept = invertDict(cogDept2index)
HQToSafezone = {SellbotHQ: DaisyGardens,
 CashbotHQ: MinniesMelodyland,
 LawbotHQ: TheBrrrgh,
 BossbotHQ: OutdoorZone,
 BoardbotHQ: DonaldsDreamland,
 TechbotHQ: DonaldsDreamland,
 HighRollerHQ: MinniesMelodyland
 }
CogDeptNames = [TTLocalizer.Bossbot,
 TTLocalizer.Lawbot,
 TTLocalizer.Cashbot,
 TTLocalizer.Sellbot,
 TTLocalizer.Boardbot,
 TTLocalizer.Techbot]

def cogHQZoneId2deptIndex(zone):
    if zone >= 21000 and zone <= 21999:
        return 5
    elif zone >= 19000 and zone <= 19999:
        return 4
    elif zone >= 13000 and zone <= 13999:
        return 1
    elif zone >= 12000:
        return 2
    elif zone >= 11000:
        return 3
    else:
        return 0


def cogHQZoneId2dept(zone):
    return cogIndex2dept[cogHQZoneId2deptIndex(zone)]


def dept2cogHQ(dept):
    dept2hq = {'c': BossbotHQ,
     'l': LawbotHQ,
     'm': CashbotHQ,
     's': SellbotHQ,
     'g': BoardbotHQ,
    't': TechbotHQ}
    return dept2hq[dept]


MockupFactoryId = 0
MintNumFloors = {CashbotMintIntA: 20,
 CashbotMintIntB: 20,
 CashbotMintIntC: 20}
CashbotMintCogLevel = 20
CashbotMintSkelecogLevel = 25
CashbotMintBossLevel = 28
MintNumBattles = {CashbotMintIntA: 4,
 CashbotMintIntB: 6,
 CashbotMintIntC: 8}
MintCogBuckRewards = {CashbotMintIntA: 8,
 CashbotMintIntB: 14,
 CashbotMintIntC: 20}
MintNumRooms = {CashbotMintIntA: 2 * (6,) + 5 * (7,) + 5 * (8,) + 5 * (9,) + 3 * (10,),
 CashbotMintIntB: 3 * (8,) + 6 * (9,) + 6 * (10,) + 5 * (11,),
 CashbotMintIntC: 4 * (10,) + 10 * (11,) + 6 * (12,)}
 
BoardOfficeNumFloors = {BoardOfficeIntA: 20,
 BoardOfficeIntB: 20,
 BoardOfficeIntC: 20}
BoardOfficeCogLevel = 14
BoardOfficeSkelecogLevel = 15
BoardOfficeBossLevel = 28
BoardOfficeNumBattles = {BoardOfficeIntA: 4,
 BoardOfficeIntB: 6,
 BoardOfficeIntC: 8}
BoardOfficeCogBuckRewards = {BoardOfficeIntA: 8,
 BoardOfficeIntB: 14,
 BoardOfficeIntC: 20}
BoardOfficeNumRooms = {BoardOfficeIntA: 2 * (6,) + 5 * (7,) + 5 * (8,) + 5 * (9,) + 3 * (10,),
 BoardOfficeIntB: 3 * (8,) + 6 * (9,) + 6 * (10,) + 5 * (11,),
 BoardOfficeIntC: 4 * (10,) + 10 * (11,) + 6 * (12,)}
 
BossbotCountryClubCogLevel = 15
BossbotCountryClubSkelecogLevel = 16
BossbotCountryClubBossLevel = 16
CountryClubNumRooms = {BossbotCountryClubIntA: (4,),
 BossbotCountryClubIntB: 3 * (8,) + 6 * (9,) + 6 * (10,) + 5 * (11,),
 BossbotCountryClubIntC: 4 * (10,) + 10 * (11,) + 6 * (12,)}
CountryClubNumBattles = {BossbotCountryClubIntA: 3,
 BossbotCountryClubIntB: 2,
 BossbotCountryClubIntC: 3}
CountryClubCogBuckRewards = {BossbotCountryClubIntA: 8,
 BossbotCountryClubIntB: 14,
 BossbotCountryClubIntC: 20}
LawbotStageCogLevel = 18
LawbotStageSkelecogLevel = 20
LawbotStageBossLevel = 28
StageNumBattles = {LawbotStageIntA: 0,
 LawbotStageIntB: 0,
 LawbotStageIntC: 0,
 LawbotStageIntD: 0}
StageNoticeRewards = {LawbotStageIntA: 75,
 LawbotStageIntB: 150,
 LawbotStageIntC: 225,
 LawbotStageIntD: 300}
StageNumRooms = {LawbotStageIntA: 2 * (6,) + 5 * (7,) + 5 * (8,) + 5 * (9,) + 3 * (10,),
 LawbotStageIntB: 3 * (8,) + 6 * (9,) + 6 * (10,) + 5 * (11,),
 LawbotStageIntC: 4 * (10,) + 10 * (11,) + 6 * (12,),
 LawbotStageIntD: 4 * (10,) + 10 * (11,) + 6 * (12,)}
FT_FullSuit = 'fullSuit'
FT_Leg = 'leg'
FT_Arm = 'arm'
FT_Torso = 'torso'
factoryId2factoryType = {MockupFactoryId: FT_FullSuit,
 SellbotFactoryInt: FT_FullSuit,
 LawbotOfficeInt: FT_FullSuit}
StreetNames = TTLocalizer.GlobalStreetNames
StreetBranchZones = StreetNames.keys()
Hoods = (DonaldsDock,
 ToontownCentral,
 TheBrrrgh,
 MinniesMelodyland,
 DaisyGardens,
 OutdoorZone,
 FunnyFarm,
 GoofySpeedway,
 YeOlde,
 Toonseltown,
 SkyClan,
 DonaldsDreamland,
 BossbotHQ,
 SellbotHQ,
 CashbotHQ,
 LawbotHQ,
 BoardbotHQ,
 TechbotHQ,
 GolfZone)
HoodsForTeleportAll = (DonaldsDock,
 ToontownCentral,
 TheBrrrgh,
 MinniesMelodyland,
 DaisyGardens,
 OutdoorZone,
 GoofySpeedway,
 YeOlde,
 Toonseltown,
 SkyClan,
 DonaldsDreamland,
 BossbotHQ,
 SellbotHQ,
 CashbotHQ,
 LawbotHQ,
 BoardbotHQ,
 GolfZone)
BingoCardNames = {'normal': 0,
'corners': 1,
'diagonal': 2,
'threeway': 3,
'blockout': 4}
NoPreviousGameId = 0
RaceGameId = 1
CannonGameId = 2
TagGameId = 3
PatternGameId = 4
RingGameId = 5
MazeGameId = 6
TugOfWarGameId = 7
CatchGameId = 8
DivingGameId = 9
TargetGameId = 10
PairingGameId = 11
VineGameId = 12
IceGameId = 13
CogThiefGameId = 14
TwoDGameId = 15
PhotoGameId = 16
TravelGameId = 100
MinigameNames = {'race': RaceGameId,
 'cannon': CannonGameId,
 'tag': TagGameId,
 'pattern': PatternGameId,
 'minnie': PatternGameId,
 'match': PatternGameId,
 'matching': PatternGameId,
 'ring': RingGameId,
 'maze': MazeGameId,
 'tug': TugOfWarGameId,
 'catch': CatchGameId,
 'diving': DivingGameId,
 'target': TargetGameId,
 'pairing': PairingGameId,
 'vine': VineGameId,
 'ice': IceGameId,
 'thief': CogThiefGameId,
 '2d': TwoDGameId,
 'photo': PhotoGameId,
 'travel': TravelGameId}
MinigameTemplateId = -1
MinigameIDs = (RaceGameId,
 CannonGameId,
 TagGameId,
 PatternGameId,
 RingGameId,
 MazeGameId,
 TugOfWarGameId,
 CatchGameId,
 DivingGameId,
 TargetGameId,
 PairingGameId,
 VineGameId,
 IceGameId,
 CogThiefGameId,
 TwoDGameId,
 PhotoGameId,
 TravelGameId)
MinigamePlayerMatrix = {
    1: (CannonGameId, MazeGameId, TugOfWarGameId, RingGameId, VineGameId, CogThiefGameId, TwoDGameId, DivingGameId, PairingGameId, CatchGameId, TargetGameId, PhotoGameId),
    2: (CannonGameId, MazeGameId, TugOfWarGameId, PatternGameId, TagGameId, RingGameId, VineGameId, IceGameId, CogThiefGameId, TwoDGameId, DivingGameId, PairingGameId, CatchGameId, TargetGameId, PhotoGameId),
    3: (CannonGameId, MazeGameId, TugOfWarGameId, PatternGameId, RaceGameId, TagGameId, VineGameId, RingGameId, IceGameId, CogThiefGameId, TwoDGameId, DivingGameId, PairingGameId, CatchGameId, TargetGameId, PhotoGameId),
    4: (CannonGameId, MazeGameId, TugOfWarGameId, PatternGameId, RaceGameId, TagGameId, VineGameId, RingGameId, IceGameId, CogThiefGameId, TwoDGameId, DivingGameId, PairingGameId, CatchGameId, TargetGameId, PhotoGameId),
}
MinigameReleaseDates = {IceGameId: (2008, 8, 5),
 PhotoGameId: (2008, 8, 13),
 TwoDGameId: (2008, 8, 20),
 CogThiefGameId: (2008, 8, 27)}
KeyboardTimeout = 300
phaseMap = {Tutorial: 4,
 ToontownCentral: 4,
 ToontownCentralOld: 4,
 MyEstate: 5.5,
 DonaldsDock: 6,
 MinniesMelodyland: 6,
 GoofySpeedway: 6,
 YeOlde: 7,
 TheBrrrgh: 8,
 DaisyGardens: 8,
 FunnyFarm: 8,
 DonaldsDreamland: 8,
 OutdoorZone: 6,
 Toonseltown: 13,
 SkyClan: 13, 
 BossbotHQ: 12,
 SellbotHQ: 9,
 CashbotHQ: 10,
 LawbotHQ: 11,
 BoardbotHQ: 14,
 TechbotHQ: 11,
 HighRollerHQ: 13,
 GolfZone: 6,
 PartyHood: 13}
streetPhaseMap = {
 ToontownCentral: 5,
 ToontownCentralOld: 5,
 DonaldsDock: 6,
 MinniesMelodyland: 6,
 GoofySpeedway: 6,
 YeOlde: 7,
 Toonseltown: 13,
 SkyClan: 13,
 TheBrrrgh: 8,
 DaisyGardens: 8,
 FunnyFarm: 8,
 DonaldsDreamland: 8,
 OutdoorZone: 6,
 BossbotHQ: 12,
 SellbotHQ: 9,
 CashbotHQ: 10,
 LawbotHQ: 11,
 BoardbotHQ: 14,
 TechbotHQ: 11,
 HighRollerHQ: 13,
 PartyHood: 13}
dnaMap = {Tutorial: 'toontown_central',
 ToontownCentral: 'toontown_central',
 ToontownCentralOld: 'toontown_central_old',
 DonaldsDock: 'donalds_dock',
 MinniesMelodyland: 'minnies_melody_land',
 GoofySpeedway: 'goofy_speedway',
 TheBrrrgh: 'the_burrrgh',
 DaisyGardens: 'daisys_garden',
 DonaldsDreamland: 'donalds_dreamland',
 YeOlde: 'olde_toontown',
 OutdoorZone: 'outdoor_zone',
 BossbotHQ: 'cog_hq_bossbot',
 SellbotHQ: 'cog_hq_sellbot',
 CashbotHQ: 'cog_hq_cashbot',
 LawbotHQ: 'cog_hq_lawbot',
 BoardbotHQ: 'cog_hq_boardbot',
 TechbotHQ: 'cog_hq_boardbot',
 HighRollerHQ: 'cog_hq_cashbot',
 GolfZone: 'golf_zone',
 Toonseltown: 'toonseltown',
 SkyClan: 'skyclan'} 
hoodNameMap = {DonaldsDock: TTLocalizer.DonaldsDock,
 ToontownCentral: TTLocalizer.ToontownCentral,
 ToontownCentralOld: TTLocalizer.ToontownCentralOld,
 TheBrrrgh: TTLocalizer.TheBrrrgh,
 MinniesMelodyland: TTLocalizer.MinniesMelodyland,
 DaisyGardens: TTLocalizer.DaisyGardens,
 OutdoorZone: TTLocalizer.OutdoorZone,
 FunnyFarm: TTLocalizer.FunnyFarm,
 GoofySpeedway: TTLocalizer.GoofySpeedway,
 YeOlde: TTLocalizer.YeOlde,
 Toonseltown: TTLocalizer.Toonseltown,
 SkyClan: TTLocalizer.SkyClan,  
 DonaldsDreamland: TTLocalizer.DonaldsDreamland,
 BossbotHQ: TTLocalizer.BossbotHQ,
 SellbotHQ: TTLocalizer.SellbotHQ,
 CashbotHQ: TTLocalizer.CashbotHQ,
 LawbotHQ: TTLocalizer.LawbotHQ,
 BoardbotHQ: TTLocalizer.BoardbotHQ,
 TechbotHQ: TTLocalizer.TechbotHQ,
 HighRollerHQ: ('The High Roller', 'The High Roller'),
 Tutorial: TTLocalizer.Tutorial,
 MyEstate: TTLocalizer.MyEstate,
 GolfZone: TTLocalizer.GolfZone,
 PartyHood: TTLocalizer.PartyHood}
safeZones = [ToontownCentral,
 OutdoorZone,
 DonaldsDock,
 DaisyGardens,
 YeOlde,
 Toonseltown,
 SkyClan,
 MinniesMelodyland,
 TheBrrrgh,
 DonaldsDreamland]
safeZoneCountMap = {MyEstate: 8,
 Tutorial: 6,
 ToontownCentral: 6,
 ToontownCentralOld: 6,
 DonaldsDock: 10,
 MinniesMelodyland: 5,
 GoofySpeedway: 500,
 YeOlde: 500,
 Toonseltown: 500,
#HQ: 2,
 SkyClan: 500,
 TheBrrrgh: 8,
 DaisyGardens: 9,
 FunnyFarm: 500,
 DonaldsDreamland: 5,
 OutdoorZone: 500,
 GolfZone: 500,
 PartyHood: 500}
townCountMap = {MyEstate: 8,
 Tutorial: 40,
 ToontownCentral: 37,
 ToontownCentralOld: 37,
 DonaldsDock: 40,
 MinniesMelodyland: 40,
 GoofySpeedway: 40,
 TheBrrrgh: 40,
 DaisyGardens: 40,
 YeOlde: 40,
 Toonseltown: 40,
 SkyClan: 40,
 FunnyFarm: 40,
 DonaldsDreamland: 40,
 OutdoorZone: 40,
 PartyHood: 20}
hoodCountMap = {MyEstate: 2,
 Tutorial: 2,
 ToontownCentral: 2,
 ToontownCentralOld: 2,
 DonaldsDock: 2,
 MinniesMelodyland: 2,
 GoofySpeedway: 2,
 TheBrrrgh: 2,
 DaisyGardens: 2,
 FunnyFarm: 2,
 YeOlde: 2,
 Toonseltown: 2,
 SkyClan: 2, 
 DonaldsDreamland: 2,
 OutdoorZone: 2,
 BossbotHQ: 2,
 SellbotHQ: 43,
 CashbotHQ: 2,
 LawbotHQ: 2,
 BoardbotHQ: 2,
 TechbotHQ: 1,
 HighRollerHQ: 2,
 GolfZone: 2,
 PartyHood: 2}
TrophyStarLevels = (10,
 20,
 30,
 50,
 75,
 100)
TrophyStarColors = (Vec4(0.9, 0.6, 0.2, 1),
 Vec4(0.9, 0.6, 0.2, 1),
 Vec4(0.8, 0.8, 0.8, 1),
 Vec4(0.8, 0.8, 0.8, 1),
 Vec4(1, 1, 0, 1),
 Vec4(1, 1, 0, 1))
MickeySpeed = 5.0
VampireMickeySpeed = 1.15
MinnieSpeed = 3.2
WitchMinnieSpeed = 1.8
Dungeon = 7507
ChainsawLobby = 6837
OZGagShop = 6505
OTGagShop = 7502
OZPetShop = 6506
OTPetShop = 7503
SchoolHouse = 2516
SchoolHouseWelcomeValley = 32516
DerrickLobby = 2921
DerrickLobbyWelcomeValley = 32921
Lighthouse = 1836
MajorPlayerLobby = 4874
ChainsawExterior = 6319
DonaldSpeed = 3.68
FrankenDonaldSpeed = 0.9
DaisySpeed = 2.3
GoofySpeed = 5.2
SuperGoofySpeed = 1.6
PlutoSpeed = 5.5
WesternPlutoSpeed = 3.2
ChipSpeed = 3
DaleSpeed = 3.5
DaleOrbitDistance = 3
SuitWalkSpeed = 4.8
PieThrowArc = 0
PieThrowLinear = 1
PieCodeBossCog = 1
PieCodeNotBossCog = 2
PieCodeToon = 3
PieCodeBossInsides = 4
PieCodeDefensePan = 5
PieCodeProsecutionPan = 6
PieCodeLawyer = 7
PieCodeInvasionSuit = 8
PieCodeWinterMinigame = 9
PieCodeColors = {PieCodeBossCog: None,
 PieCodeNotBossCog: (0.8,
                     0.8,
                     0.8,
                     1),
 PieCodeToon: None}

TsMinigamePresentSpawns = [
    (-0.639, 11.667, 8.145), (-66.881, 23.699, 7.440), (-95.831, -31.366, 7.671),
    (-35.684, -64.850, 7.582), (1.296, -22.138, 8.145), (51.839, -23.528, 20.716),
    (51.213, -65.294, 20.716), (7.909, -115.745, 20.716), (-74.028, -115.942, 20.716),
    (-133.813, -102.684, 20.716), (-146.668, -65.000, 20.716), (-157.555, -11.622, 20.716),
    (-132.259, 32.709, 20.716), (-116.528, 78.990, 20.716), (-63.659, 85.099, 20.716),
    (-13.441, 83.446, 20.716), (29.180, 55.438, 20.716), (47.878, 2.846, 20.716),
    (51.661, -60.085, 20.716), (15.599, -103.597, 20.716), (-48.597, -123.973, 20.716),
    (-249.845, 129.939, 51.086), (-273.014, 154.750, 51.134), (-296.712, 125.948, 51.081),
    (-262.148, 62.950, 46.743), (-254.333, 20.114, 39.840), (-217.679, 13.684, 31.292),
    (-192.200, -13.930, 23.151), (-48.062, 104.606, 20.963), (-25.120, 127.918, 20.938),
    (-35.774, 153.803, 21.707), (-25.983, 184.331, 23.630), (-43.548, 233.900, 34.732),
    (35.760, 270.560, 34.732), (17.127, 315.700, 34.732), (-4.353, 284.361, 32.701),
    (14.474, 294.335, 32.647), (-33.623, 337.604, 34.732), (-50.226, 332.328, 34.732),
    (-70.316, 295.469, 34.732), (-59.562, 266.507, 34.732), (-50.931, 245.158, 34.732),
    (81.882, -12.866, 21.524), (110.483, -30.150, 24.876), (126.150, -7.622, 26.561),
    (152.386, -40.638, 29.128), (177.747, -32.575, 29.159), (166.898, -4.914, 29.208),
    (150.295, -7.477, 29.175), (45.143, -88.056, 20.716), (-42.810, -118.545, 20.716),
    (-120.567, -93.444, 19.893), (-158.023, -48.409, 20.716), (-178.568, 4.474, 21.867),
    (-195.343, -11.763, 23.676), (-214.766, 9.433, 29.858), (-239.553, -0.212, 34.549),
    (-259.293, 28.252, 41.397), (-247.402, 43.815, 42.139), (-277.375, 67.989, 48.064),
    (-271.164, 101.637, 50.714), (-286.607, 114.011, 50.906), (-283.147, 163.911, 51.147),
    (26.743, 68.824, 20.716), (53.532, 37.172, 20.716), (50.984, -24.003, 20.716),
    (-8.534, -108.613, 20.716), (-185.917, -11.728, 22.335), (-219.607, 13.368, 31.743),
    (-44.812, 179.386, 22.548), (-22.842, 206.859, 31.150), (-27.625, 232.616, 34.732),
    (-47.542, 257.962, 34.732), (-33.562, 290.682, 34.732), (-48.688, 311.422, 34.732),
    (-58.844, 306.565, 34.732), (-65.224, 302.114, 34.732), (-57.864, 296.647, 34.732),
    (-30.880, 304.356, 34.732), (-23.311, 78.128, 20.759), (57.881, 19.239, 20.715),
    (90.868, -15.580, 22.506), (159.160, -1.299, 29.201), (160.468, -28.515, 29.175),
    (175.419, -24.105, 29.192), (105.420, -20.148, 24.099), (35.992, -78.673, 20.716),
    (-18.636, -118.073, 20.716), (-77.200, -118.963, 20.716), (-140.362, -62.899, 20.716),
    (-205.366, -7.805, 25.244), (-238.077, 25.061, 38.521), (-269.102, 88.958, 49.808),
    (-284.785, 135.608, 51.098), (-260.995, 145.983, 51.117), (-174.492, -3.015, 21.020),
    (-122.790, 53.800, 20.716), (-45.218, 107.358, 20.994), (-26.464, 180.690, 22.711),
    (-33.439, 230.229, 34.732), (-8.846, 232.249, 34.732), (2.444, 271.078, 32.717),
    (-29.203, 33.203, 8.145), (-3.149, -9.868, 7.834), (-12.918, -53.830, 7.355),
    (-42.109, -68.439, 8.075), (-96.664, -26.770, 7.668), (-63.129, 97.462, 20.776),
    (79.353, -11.984, 21.209), (94.071, -26.324, 22.781), (153.482, -14.129, 29.209),
    (169.220, -4.847, 29.209), (178.441, -20.216, 29.207), (168.280, -48.539, 29.097),
    (-252.176, 116.704, 50.896), (-258.176, 143.983, 51.113), (-279.369, 157.876, 51.141),
    (-287.238, 130.925, 51.089), (-269.983, 105.350, 50.759), (-262.575, 139.275, 51.102),
    (-258.177, 154.207, 51.134), (-140.901, 27.706, 20.716), (-36.943, 145.355, 21.417),
    (-29.597, 236.949, 34.732), (-29.540, 254.928, 34.732), (-42.010, 268.824, 34.732),
    (-47.346, 313.345, 34.732), (-54.695, 308.816, 34.732), (-28.431, 323.097, 34.732),
    (-21.843, 329.391, 34.732), (-23.476, 320.564, 34.732), (-38.720, 331.502, 34.732),
    (-30.117, 338.448, 34.732), (-49.841, 324.785, 34.732), (-46.708, 340.842, 34.732),
    (-10.413, 290.011, 33.007), (-0.028, 265.157, 32.989), (19.883, 295.819, 32.993),
    (126.590, -18.653, 26.642), (118.702, -1.181, 25.763), (108.781, -28.779, 24.551),
    (91.112, -25.668, 22.440), (-255.088, 109.196, 50.795), (-260.328, 132.630, 51.088),
    (-287.945, 149.923, 51.129), (-276.383, 168.952, 51.151), (-256.179, 138.204, 51.101),
    (-263.716, 91.342, 49.756), (-157.723, 24.239, 20.716), (-30.264, 182.393, 22.748),
    (33.807, -24.490, 15.033), (-130.642, -15.844, 12.507), (-114.576, 16.783, 10.905),
    (-92.145, 51.463, 11.126), (1.677, 52.711, 15.135), (95.396, -11.820, 23.103),
    (6.672, -80.469, 8.145), (-180.244, -58.345, 20.791),
]

TsMinigameSuitLocations = [
    (-71.436, -49.617, 3.463, -35.379, 0, 0), (-58.114, -55.124, 4.586, -12.433, 0, 0),
    (-44.066, -55.109, 4.208, 10.778, 0, 0), (-29.455, -48.750, 3.135, 35.873, 0, 0),
    (-21.165, -40.093, 3.092, 56.643, 0, 0), (-14.703, -20.125, 3.910, 89.813, 0, 0),
    (-17.177, -6.147, 3.731, 112.744, 0, 0), (-25.971, 6.988, 2.760, 139.732, 0, 0),
    (-47.446, 16.882, 4.981, 176.286, 0, 0), (-67.259, 13.303, 4.798, -154.578, 0, 0),
    (-78.685, 4.470, 3.844, -126.653, 0, 0), (-87.106, -13.614, 5.423, -97.180, 0, 0),
    (-85.053, -32.656, 4.982, -68.988, 0, 0), (-77.788, -44.200, 3.162, -46.974, 0, 0),
    (-68.807, -51.224, 3.814, -29.853, 0, 0), (-51.948, -55.791, 4.349, -2.757, 0, 0),
    (-34.944, -52.008, 3.528, 26.391, 0, 0), (-23.368, -42.962, 2.530, 48.421, 0, 0),
    (-16.390, -30.351, 3.798, 74.174, 0, 0), (-14.717, -18.086, 4.079, 93.262, 0, 0),
    (-18.045, -4.104, 3.606, 118.379, 0, 0), (-23.269, 4.113, 2.664, 132.633, 0, 0),
    (-32.788, 12.115, 3.978, 154.029, 0, 0), (-44.578, 16.475, 5.040, 171.079, 0, 0),
    (-57.486, 16.509, 5.191, -168.445, 0, 0), (-69.399, 12.157, 4.627, -150.396, 0, 0),
    (-79.379, 3.643, 4.036, -127.622, 0, 0), (-87.194, -14.189, 5.413, -97.570, 0, 0),
    (-86.135, -29.466, 5.247, -77.101, 0, 0), (-78.648, -43.244, 3.321, -50.979, 0, 0),
]

TsMinigameTreePresentLocations = [
    (-45.238, 3.594, 0.025), (-25.092, -22.666, 0.025), (-43.514, -40.960, 0.025),
    (-58.137, -7.841, 0.025), (-40.769, -7.378, 0.025), (-51.141, -35.721, 0.025),
    (-53.945, -31.115, 0.025), (-55.960, -15.995, 0.025),
]

TsMinigamePresentPoints = 2
TsMinigameCogPoints = 1
TsMinigameDeductCogPoints = 1

suitIndex = {
'f' : 0,
'p' : 1,
'ym' : 2,
'mm' : 3,
'ds' : 4,
'hh' : 5,
'cr' : 6,
'tbc' : 7,
'bf' : 8,
'b' : 9,
'dt' : 10,
'ac' : 11,
'bs' : 12,
'sd' : 13,
'le' : 14,
'bw' : 15,
'sc' : 16,
'pp' : 17,
'tw' : 18,
'bc' : 19,
'nc' : 20,
'mb' : 21,
'ls' : 22,
'rb' : 23,
'cc' : 24,
'tm' : 25,
'nd' : 26,
'gh' : 27,
'ms' : 28,
'tf' : 29,
'm' : 30,
'mh' : 31,
'ca' : 32,
'cn' : 33,
'sw' : 34,
'mdm' : 35,
'txm' : 36,
'mg' : 37,
'bfh' : 38,
'hho' : 39
}
BossCogRollSpeed = 7.5
BossCogTurnSpeed = 20
BossCogTreadSpeed = 3.5
BossCogDizzy = 0
BossCogElectricFence = 1
BossCogSwatLeft = 2
BossCogSwatRight = 3
BossCogAreaAttack = 4
BossCogFrontAttack = 5
BossCogRecoverDizzyAttack = 6
BossCogDirectedAttack = 7
BossCogStrafeAttack = 8
BossCogNoAttack = 9
BossCogGoonZap = 10
BossCogSlowDirectedAttack = 11
BossCogDizzyNow = 12
BossCogGavelStomp = 13
BossCogGavelHandle = 14
BossCogLawyerAttack = 15
BossCogMoveAttack = 16
BossCogGolfAttack = 17
BossCogGolfAreaAttack = 18
BossCogGearDirectedAttack = 19
BossCogOvertimeAttack = 20
BossCogChaseAttack = 21
BossCogAttackTimes = {BossCogElectricFence: 0,
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
                      BossCogChaseAttack: 7.1}
BossCogDamageLevels = {BossCogElectricFence: 1,
 BossCogSwatLeft: 5,
 BossCogSwatRight: 5,
 BossCogAreaAttack: 10,
 BossCogFrontAttack: 3,
 BossCogRecoverDizzyAttack: 3,
 BossCogDirectedAttack: 3,
 BossCogStrafeAttack: 2,
 BossCogGoonZap: 5,
 BossCogSlowDirectedAttack: 10,
 BossCogGavelStomp: 20,
 BossCogGavelHandle: 2,
 BossCogLawyerAttack: 5,
 BossCogMoveAttack: 20,
 BossCogGolfAttack: 15,
 BossCogGolfAreaAttack: 15,
 BossCogGearDirectedAttack: 15,
 BossCogOvertimeAttack: 10}
BossCogNerfedDamageLevels = {BossCogElectricFence: 1,
 BossCogSwatLeft: 2,
 BossCogSwatRight: 2,
 BossCogAreaAttack: 5,
 BossCogFrontAttack: 3,
 BossCogRecoverDizzyAttack: 3,
 BossCogDirectedAttack: 3,
 BossCogStrafeAttack: 2,
 BossCogGoonZap: 2,
 BossCogSlowDirectedAttack: 5,
 BossCogGavelStomp: 10,
 BossCogGavelHandle: 2,
 BossCogLawyerAttack: 2,
 BossCogMoveAttack: 8,
 BossCogGolfAttack: 8,
 BossCogGolfAreaAttack: 8,
 BossCogGearDirectedAttack: 8,
 BossCogOvertimeAttack: 10}
CountErclaimBattleAPosHpr = (0, 55, 0, 180, 0, 0)
PacesetterBattleAPosHpr = (0, 110, 0, 180, 0, 0)
DirectorsBattleAPosHpr = (0, 150, 0, 180, 0, 0)
# Shared boss-battle offsets used by the existing custom boss fights.
# Keep these at their pre-CFO-split values so custom encounters retain their
# original positioning.
FourBossesBossBattleOnePosHpr = (0,
 0,
 0,
 0,
 0,
 0)
FourBossesBossBattleFourPosHpr = (0,
 0,
 0,
 0,
 0,
 0)
FourBossCogBattleAPosHpr = (0,
 100,
 21.869,
 -180,
 0,
 0)
FourBossCogBattleBPosHpr = (15,
 40,
 21.869,
 -46.5,
 0,
 0)
FourBossRankedBattleAPosHpr = (-112,
 -23,
 0.025,
 90,
 0,
 0)
FourBossRankedBattleBPosHpr = (-112,
 23,
 0.025,
 90,
 0,
 0)
FourBossRankedBattleCPosHpr = (-112,
 0.0,
 0.025,
 90,
 0,
 0)
BossCogBattleAPosHpr = (0,
 60,
 0,
 180,
 0,
 0)
BossCogBattleBPosHpr = (0,
 60,
 0,
 0,
 0,
 0)

# The regular CFO uses stock-style left/right battle offsets.  These are
# intentionally CFO-only and must not replace BossCogBattleA/B globally.
CashbotBossCogBattleAPosHpr = (0,
 -25,
 0,
 0,
 0,
 0)
CashbotBossCogBattleBPosHpr = (0,
 25,
 0,
 180,
 0,
 0)

# The standalone High Roller arena uses its own battle offsets.  Keep them
# separate so changing the High Roller instance cannot move the VP/CFO/CJ/CEO.
HighRollerBossCogBattleAPosHpr = (0,
 60,
 0,
 180,
 0,
 0)
HighRollerBossCogBattleBPosHpr = (0,
 60,
 0,
 0,
 0,
 0)
VideographerBossCogBattleAPosHpr = (0,
 120,
 0,
 0,
 0,
 0)
VideographerBossCogBattleBPosHpr = (0,
 120,
 0,
 0,
 0,
 0)
SellbotBossMaxDamage = 100
SellbotBossMaxDamageNerfed = 100
SellbotBossBattleOnePosHpr = (0,
 - 20,
 0,
 0,
 0,
 0)
SellbotBossBattleThreePosHpr = (0,
 - 20,
 18,
 0,
 0,
 0)
SellbotBossBattleTwoPosHpr = (0,
 -50,
 -6.5,
 180,
 0,
 0)

SellbotBossBattleTwoPosHpr2 = (0,
 60,
 18,
 0,
 0,
 0)
SellbotBossBattleThreeHpr = (180, 0, 0)
SellbotBossBottomPos = (0, -110, -6.5)
SellbotBossDeathPos = (0, -175, -6.5)
SellbotBossDooberTurnPosA = (-80, -35, 18)
SellbotBossDooberTurnPosB = (80, -35, 18)
SellbotBossDooberTurnPosDown = (0, -35, 0)
SellbotBossDooberFlyPos = (0, -135, -6.5)
SellbotBossTopRampPosA = (-80, -35, 18)
SellbotBossTopRampTurnPosA = (-80, 10, 18)
SellbotBossP3PosA = (-50, 40, 18)
SellbotBossTopRampPosB = (80, -35, 18)
SellbotBossTopRampTurnPosB = (80, 10, 18)
SellbotBossP3PosB = (50, 60, 18)
CashbotBossMaxDamage = 1500
CashbotBossOffstagePosHpr = (120,
 -195,
 0,
 0,
 0,
 0)
CashbotBossBattleOnePosHpr = (120,
 -230,
 0,
 90,
 0,
 0)
CashbotBossBattleTwoPosHpr = (120,
 -315,
 0,
 180,
 0,
 0)
CashbotRTBattleOneStartPosHpr = (94,
 -220,
 0,
 110,
 0,
 0)
CashbotRTBattleTwoStartPosHpr = (120,
 -260,
 0.025,
 0,
 0,
 0)
CashbotRTBattleTwoEndPosHpr = (120,
 -290,
 0.025,
 0,
 0,
 0)
CashbotBossBattleThreePosHpr = (120,
 -315,
 0,
 180,
 0,
 0)
CashbotToonsBattleThreeStartPosHpr = [(105,
  -285,
  0,
  208,
  0,
  0),
 (136,
  -342,
  0,
  398,
  0,
  0),
 (105,
  -342,
  0,
  333,
  0,
  0),
 (135,
  -292,
  0,
  146,
  0,
  0),
 (93,
  -303,
  0,
  242,
  0,
  0),
 (144,
  -327,
  0,
  64,
  0,
  0),
 (145,
  -302,
  0,
  117,
  0,
  0),
 (93,
  -327,
  0,
  -65,
  0,
  0)]
CashbotBossSafePosHprs = [(120, -315, 30, 0, 0, 0),
 (77.2, -329.3, 0, -90, 0, 0),
 (77.1, -302.7, 0, -90, 0, 0),
 (165.7, -326.4, 0, 90, 0, 0),
 (165.5, -302.4, 0, 90, 0, 0),
 (107.8, -359.1, 0, 0, 0, 0),
 (133.9, -359.1, 0, 0, 0, 0),
 (107.0, -274.7, 0, 180, 0, 0),
 (134.2, -274.7, 0, 180, 0, 0)]
CashbotBossCranePosHprs = [(97.4, -337.6, 0, -45, 0, 0),
 (97.4, -292.4, 0, -135, 0, 0),
 (142.6, -292.4, 0, 135, 0, 0),
 (142.6, -337.6, 0, 45, 0, 0),
 (81, -315, 0, -90, 0, 0),
 (160, -315, 0, 90, 0, 0)]

# Standalone High Roller coordinates preserved from the working custom fight.
# The High Roller classes use only these names; regular CFO code uses the
# CashbotBoss... values above.
HighRollerBossOffstagePosHpr = (120, -195, 0, 0, 0, 0)
HighRollerBossBattleOnePosHpr = (0, -130, 0, 180, 0, 0)
VideographerBossBattleOnePosHpr = (0, -170, 1.25, 0, 0, 0)
HighRollerBossBattleTwoPosHpr = (120, -285, 0, 180, 0, 0)
HighRollerRTBattleOneStartPosHpr = (94, -220, 0, 110, 0, 0)
HighRollerRTBattleTwoStartPosHpr = (94, -220, 0, 110, 0, 0)
HighRollerRTBattleTwoEndPosHpr = (120, -290, 0.025, 0, 0, 0)
HighRollerBossBattleThreePosHpr = (120, -315, 0, 180, 0, 0)
HighRollerToonsBattleThreeStartPosHpr = CashbotToonsBattleThreeStartPosHpr[:]
HighRollerBossSafePosHprs = [(120, -315, 30, 0, 0, 0),
 (77.1, -302.7, 0, -90, 0, 0),
 (165.7, -326.4, 0, 90, 0, 0),
 (134.2, -274.7, 0, 180, 0, 0),
 (107.8, -359.1, 0, 0, 0, 0),
 (107.0, -274.7, 0, 180, 0, 0),
 (133.9, -359.1, 0, 0, 0, 0),
 (165.5, -302.4, 0, 90, 0, 0),
 (77.2, -329.3, 0, -90, 0, 0)]
HighRollerBossCranePosHprs = CashbotBossCranePosHprs[:]
CashbotBossToMagnetTime = 0.2
CashbotBossFromMagnetTime = 1
CashbotBossSafeKnockImpact = 0.5
CashbotBossSafeNewImpact = 0.0
CashbotBossGoonImpact = 0.25
CashbotBossKnockoutDamage = 25
TTWakeWaterHeight = -4.79
DDWakeWaterHeight = 1.669
EstateWakeWaterHeight = -.3
OZWakeWaterHeight = 4.3
WakeRunDelta = 0.1
WakeWalkDelta = 0.2
NoItems = 0
NewItems = 1
OldItems = 2
SuitInvasionBegin = 0
SuitInvasionEnd = 1
SuitInvasionUpdate = 2
SuitInvasionBulletin = 3
SkelecogInvasionBegin = 4
SkelecogInvasionEnd = 5
SkelecogInvasionBulletin = 6
WaiterInvasionBegin = 7
WaiterInvasionEnd = 8
WaiterInvasionBulletin = 9
V2InvasionBegin = 10
V2InvasionEnd = 11
V2InvasionBulletin = 12
SuitMegaInvasionBegin = 13
SuitMegaInvasionEnd = 14
SuitMegaInvasionUpdate = 15
SuitMegaInvasionBulletin = 16
NO_HOLIDAY = 0
JULY4_FIREWORKS = 1
NEWYEARS_FIREWORKS = 2
HALLOWEEN = 3
WINTER_DECORATIONS = 4
SKELECOG_INVASION = 5
MR_HOLLYWOOD_INVASION = 6
FISH_BINGO_NIGHT = 7
BLACK_CAT_DAY = 9
RESISTANCE_EVENT = 10
KART_RECORD_DAILY_RESET = 11
KART_RECORD_WEEKLY_RESET = 12
TRICK_OR_TREAT = 13
CIRCUIT_RACING = 14
POLAR_PLACE_EVENT = 15
CIRCUIT_RACING_EVENT = 16
TROLLEY_HOLIDAY = 17
TROLLEY_WEEKEND = 18
SILLY_SATURDAY_BINGO = 19
SILLY_SATURDAY_CIRCUIT = 20
SILLY_SATURDAY_TROLLEY = 21
ROAMING_TRIALER_WEEKEND = 22
BOSSCOG_INVASION = 23
MARCH_INVASION = 24
MORE_XP_HOLIDAY = 25
HALLOWEEN_PROPS = 26
HALLOWEEN_COSTUMES = 27
DECEMBER_INVASION = 28
APRIL_FOOLS_COSTUMES = 29
CRASHED_LEADERBOARD = 30
OCTOBER31_FIREWORKS = 31
NOVEMBER19_FIREWORKS = 32
SELLBOT_SURPRISE_1 = 33
SELLBOT_SURPRISE_2 = 34
SELLBOT_SURPRISE_3 = 35
SELLBOT_SURPRISE_4 = 36
CASHBOT_CONUNDRUM_1 = 37
CASHBOT_CONUNDRUM_2 = 38
CASHBOT_CONUNDRUM_3 = 39
CASHBOT_CONUNDRUM_4 = 40
LAWBOT_GAMBIT_1 = 41
LAWBOT_GAMBIT_2 = 42
LAWBOT_GAMBIT_3 = 43
LAWBOT_GAMBIT_4 = 44
TROUBLE_BOSSBOTS_1 = 45
TROUBLE_BOSSBOTS_2 = 46
TROUBLE_BOSSBOTS_3 = 47
TROUBLE_BOSSBOTS_4 = 48
JELLYBEAN_DAY = 49
FEBRUARY14_FIREWORKS = 51
JULY14_FIREWORKS = 52
JUNE22_FIREWORKS = 53
BIGWIG_INVASION = 54
COLD_CALLER_INVASION = 53
BEAN_COUNTER_INVASION = 54
DOUBLE_TALKER_INVASION = 55
DOWNSIZER_INVASION = 56
WINTER_CAROLING = 57
HYDRANT_ZERO_HOLIDAY = 58
VALENTINES_DAY = 59
SILLYMETER_HOLIDAY = 60
MAILBOX_ZERO_HOLIDAY = 61
TRASHCAN_ZERO_HOLIDAY = 62
SILLY_SURGE_HOLIDAY = 63
HYDRANTS_BUFF_BATTLES = 64
MAILBOXES_BUFF_BATTLES = 65
TRASHCANS_BUFF_BATTLES = 66
SILLY_CHATTER_ONE = 67
SILLY_CHATTER_TWO = 68
SILLY_CHATTER_THREE = 69
SILLY_CHATTER_FOUR = 70
SILLY_TEST = 71
YES_MAN_INVASION = 72
TIGHTWAD_INVASION = 73
TELEMARKETER_INVASION = 74
HEADHUNTER_INVASION = 75
SPINDOCTOR_INVASION = 76
MONEYBAGS_INVASION = 77
TWOFACES_INVASION = 78
MINGLER_INVASION = 79
LOANSHARK_INVASION = 80
CORPORATE_RAIDER_INVASION = 81
ROBBER_BARON_INVASION = 82
LEGAL_EAGLE_INVASION = 83
BIG_WIG_INVASION = 84
BIG_CHEESE_INVASION = 85
DOWN_SIZER_INVASION = 86
MOVER_AND_SHAKER_INVASION = 87
DOUBLETALKER_INVASION = 88
PENNY_PINCHER_INVASION = 89
NAME_DROPPER_INVASION = 90
AMBULANCE_CHASER_INVASION = 91
MICROMANAGER_INVASION = 92
NUMBER_CRUNCHER_INVASION = 93
SILLY_CHATTER_FIVE = 94
VICTORY_PARTY_HOLIDAY = 95
SELLBOT_NERF_HOLIDAY = 96
JELLYBEAN_TROLLEY_HOLIDAY = 97
JELLYBEAN_FISHING_HOLIDAY = 98
JELLYBEAN_PARTIES_HOLIDAY = 99
BANK_UPGRADE_HOLIDAY = 100
TOP_TOONS_MARATHON = 101
SELLBOT_INVASION = 102
SELLBOT_FIELD_OFFICE = 103
SELLBOT_INVASION_MOVER_AND_SHAKER = 104
IDES_OF_MARCH = 105
EXPANDED_CLOSETS = 106
TAX_DAY_INVASION = 107
KARTING_TICKETS_HOLIDAY = 109
PRE_JULY_4_DOWNSIZER_INVASION = 110
PRE_JULY_4_BIGWIG_INVASION = 111
COMBO_FIREWORKS = 112
JELLYBEAN_TROLLEY_HOLIDAY_MONTH = 113
JELLYBEAN_FISHING_HOLIDAY_MONTH = 114
JELLYBEAN_PARTIES_HOLIDAY_MONTH = 115
SILLYMETER_EXT_HOLIDAY = 116
SPOOKY_BLACK_CAT = 117
SPOOKY_TRICK_OR_TREAT = 118
SPOOKY_PROPS = 119
SPOOKY_COSTUMES = 120
WACKY_WINTER_DECORATIONS = 121
WACKY_WINTER_CAROLING = 122
SILLY_METER_GENERAL_PHASE_ZERO = 123
SILLY_METER_GENERAL_PHASE_ONE = 124
SILLY_METER_GENERAL_PHASE_TWO = 125
SILLY_METER_GENERAL_PHASE_THREE = 126
SILLY_METER_GENERAL_PHASE_FOUR = 127
SILLY_METER_GENERAL_PHASE_FIVE = 128
SILLY_METER_GENERAL_PHASE_SIX = 129
SILLY_METER_GENERAL_PHASE_SEVEN = 130
SILLY_METER_GENERAL_PHASE_EIGHT = 131
SILLY_METER_GENERAL_PHASE_NINE = 132
SILLY_METER_GENERAL_PHASE_TEN = 133
SILLY_METER_GENERAL_PHASE_ELEVEN = 134
SILLY_METER_GENERAL_PHASE_TWELVE = 135
SILLY_METER_GENERAL_PHASE_THRITEEN = 136
SILLY_METER_GENERAL_PHASE_FOURTEEN = 137
TOT_REWARD_JELLYBEAN_AMOUNT = 100
TOT_REWARD_END_OFFSET_AMOUNT = 0
LawbotBossMaxDamage = 2700
LawbotBossWinningTilt = 40
LawbotBossInitialDamage = 1350
LawbotBossBattleOnePosHpr = (-2.798,
 220,
 0,
 0,
 0,
 0)
LawbotBossBattleFourPosHpr = (-2.798,
 -60,
 0,
 90,
 0,
 0)
LawbotBossBattleTwoPosHpr = (-2.798,
 220,
 0,
 0,
 0,
 0)
LawbotBossBattleLitigationPosHpr = (-2.798,
 135,
 0,
 90,
 0,
 0)
LawbotBossBattleLitigationBPosHpr = (-52.798,
 120,
 0,
 0,
 0,
 20)
LawbotBossTopRampPosA = (-80, -35, 18)
LawbotBossTopRampTurnPosA = (-80, 10, 18)
LawbotBossP3PosA = (55, -9, 0)
LawbotBossTopRampPosB = (80, -35, 18)
LawbotBossTopRampTurnPosB = (80, 10, 18)
LawbotBossP3PosB = (55, -9, 0)
LawbotBossBattleThreePosHpr = (-2.798,
 220,
 0,
 0,
 0,
 0)
LawbotBossBottomPos = (50, 300, 0)
LawbotBossDeathPos = (50, 300, 0)
LawbotBossGavelPosHprs = [(-45,
  175,
  0,
  - 135,
  0,
  0),
(-55,
  220,
  0,
  - 135,
  0,
  0),
(55,
  220,
  0,
  135,
  0,
  0),
(-55,
  50,
  0,
  - 135,
  0,
  0),
(55,
  50,
  0,
  135,
  0,
  0),
(0,
  20,
  0,
  0,
  0,
  0),
 (45,
  175,
  0,
  135,
  0,
  0),
 (50,
 120,
  0,
  45,
  0,
  0),
 (-50,
  120,
  0,
  - 45,
  0,
  0),
 (-40,
  70,
  0,
  0,
  0,
  0),
 (40,
  70,
  0,
  - 180,
  0,
  0),
 (30,
  170,
  0,
  45,
  0,
  0),
 (-30,
  170,
  0,
  135,
  0,
  0)]
LawbotBossGavelTimes = [(0.2, 0.9, 0.6),
 (0.25, 1, 0.5),
 (1.0, 6, 0.5),
 (0.3, 3, 1),
 (0.1, 0.9, 0.45),
 (0.24, 1.1, 0.65),
 (0.27, 1.2, 0.45),
                        (1.25, 1, 0.5),
                        (1.0, 6, 0.5),
                        (1.3, 3, 1),
                        (0.26, 0.9, 0.45),
                        (0.1, 1.1, 0.65),
                        (0.27, 1.2, 0.45),
 (1.0, 0.95, 0.5)]
LawbotBossGavelHeadings = [(0,
  115,
  4,
  - 70 - 45,
  5,
  45),
 (0,
  145,
  - 4,
  - 35,
  - 45,
  - 16,
  32),
 (0,
  128,
  19,
  - 7,
  5,
  23),
 (0,
  134,
  8,
  - 16,
  32,
  - 45,
  7,
  7,
  - 30,
  19,
  - 13,
  25),
 (0,
  145,
  - 90,
  45,
  90),
 (0,
  145,
  - 90,
  45,
  90),
 (0, -45, 45),
                           (0, -45, 45),
                           (0, -45, 45),
                           (0, -45, 45),
                           (0, -45, 45),
(0, -45, 45),
                           (0, -45, 45),
                           (0, -45, 45),
 (0, -45, 45)]
LawbotBossCogRelBattleAPosHpr = (-25,
 0,
 0,
 0,
 0,
 0)
LawbotBossCogRelBattleBPosHpr = (-25,
 0,
 0,
 0,
 0,
 0)
LawbotBossCogAbsBattleAPosHpr = (-5,
 0,
 0,
 0,
 0,
 0)
LawbotBossCogAbsBattleBPosHpr = (-5,
 0,
 0,
 0,
 0,
 0)
LawbotBossWitnessStandPosHpr = (54,
 100,
 0,
 0,
 0,
 0)
LawbotBossInjusticePosHpr = (-3,
 125,
 0,
 0,
 0,
 0)
LawbotBossInjusticeScale = (2.5, 2.5, 1.5)
LawbotBossDefensePanDamage = 25
LawbotBossLawyerPosHprs = [(-57,
  76,
  0,
  - 90,
  0,
  0),
 (-57,
  88,
  0,
  - 90,
  0,
  0),
 (-57,
  100,
  0,
  - 90,
  0,
  0),
 (-57,
  112,
  0,
  - 90,
  0,
  0),
 (-57,
  124,
  0,
  - 90,
  0,
  0),
 (-57,
  136,
  0,
  - 90,
  0,
  0),
 (-57,
  148,
  0,
  - 90,
  0,
  0),
 (-57,
  160,
  0,
  - 90,
  0,
  0),
 (-3,
  50,
  0,
  0,
  0,
  0),
 (-3,
  200,
  0,
  - 180,
  0,
  0),
                           (57,
                            76,
                            0,
                            - 90,
                            0,
                            0),
                           (57,
                            88,
                            0,
                            - 90,
                            0,
                            0),
                           (57,
                            100,
                            0,
                            - 90,
                            0,
                            0),
                           (57,
                            112,
                            0,
                            - 90,
                            0,
                            0),
                           (57,
                            124,
                            0,
                            - 90,
                            0,
                            0),
                           (57,
                            136,
                            0,
                            - 90,
                            0,
                            0),
                           (57,
                            148,
                            0,
                            - 90,
                            0,
                            0),
                           (57,
                            160,
                            0,
                            - 90,
                            0,
                            0)
                      ]
LawbotBossLawyerCycleTime = 6
LawbotBossLawyerToPanTime = 2.5
LawbotBossLawyerChanceToAttack = 25
LawbotBossLawyerHeal = 2
LawbotBossLawyerStunTime = 10
LawbotBossDifficultySettings = [(38,
  4,
  18,
  1,
  0,
  0),
 (36,
  5,
  18,
  1,
  0,
  0),
(36,
  5,
  18,
  1,
  0,
  0),
(36,
  5,
  18,
  1,
  0,
  0),
(36,
  5,
  18,
  1,
  0,
  0),
 (34,
  5,
  18,
  1,
  0,
  0),
 (32,
  6,
  18,
  2,
  0,
  0),
 (30,
  6,
  18,
  2,
  0,
  0),
 (28,
  7,
  18,
  3,
  0,
  0),
 (26,
  7,
  18,
  3,
  1,
  1),
 (24,
  8,
  18,
  4,
  1,
  1),
 (22,
  8,
  18,
  4,
  1,
  0)]
LawbotBossCannonPosHprs = [(-40,
  - 12,
  0,
  - 90,
  0,
  0),
 (-40,
  0,
  0,
  - 90,
  0,
  0),
 (-40,
  12,
  0,
  - 90,
  0,
  0),
 (-40,
  24,
  0,
  - 90,
  0,
  0),
 (-40,
  36,
  0,
  - 90,
  0,
  0),
 (-40,
  48,
  0,
  - 90,
  0,
  0),
 (-40,
  60,
  0,
  - 90,
  0,
  0),
 (-40,
  72,
  0,
  - 90,
  0,
  0)]
LawbotBossCannonPosA = (-80, -51.48, 0)
LawbotBossCannonPosB = (-80, 70.73, 0)
LawbotBossChairPosHprs = [(60,
  72,
  0,
  - 90,
  0,
  0),
 (60,
  62,
  0,
  - 90,
  0,
  0),
 (60,
  52,
  0,
  - 90,
  0,
  0),
 (60,
  42,
  0,
  - 90,
  0,
  0),
 (60,
  32,
  0,
  - 90,
  0,
  0),
 (60,
  22,
  0,
  - 90,
  0,
  0),
 (70,
  72,
  5,
  - 90,
  0,
  0),
 (70,
  62,
  5,
  - 90,
  0,
  0),
 (70,
  52,
  5,
  - 90,
  0,
  0),
 (70,
  42,
  5,
  - 90,
  0,
  0),
 (70,
  32,
  5,
  - 90,
  0,
  0),
 (70,
  22,
  5,
  - 90,
  0,
  0)]
LawbotBossChairRow1PosB = (59.3, 48, 14.05)
LawbotBossChairRow1PosA = (59.3, -18.2, 14.05)
LawbotBossChairRow2PosB = (75.1, 48, 28.2)
LawbotBossChairRow2PosA = (75.1, -18.2, 28.2)
LawbotBossCannonBallMax = 12
LawbotBossJuryBoxStartPos = (394, -8, 5)
LawbotBossJuryBoxRelativeEndPos = (30, 0, 12.645)
LawbotBossJuryBoxMoveTime = 1
LawbotBossJurorsForBalancedScale = 8
LawbotBossDamagePerJuror = 68
LawbotBossCogJurorFlightTime = 10
LawbotBossCogJurorDistance = 75
LawbotBossBaseJurorNpcId = 2001
LawbotBossWitnessEpiloguePosHpr = (43,
 0,
 0,
 180,
 0,
 0)
LawbotBossChanceForTaunt = 25
LawbotBossBonusWaitTime = 60
LawbotBossBonusDuration = 20
LawbotBossBonusToonup = 10
LawbotBossBonusWeightMultiplier = 2
LawbotBossChanceToDoAreaAttack = 11
LOW_POP_JP = 0
MID_POP_JP = 100
HIGH_POP_JP = 200
LOW_POP_INTL = 399
MID_POP_INTL = 499
HIGH_POP_INTL = -1
LOW_POP = 100
MID_POP = 200
HIGH_POP = -1
PinballCannonBumper = 0
PinballCloudBumperLow = 1
PinballCloudBumperMed = 2
PinballCloudBumperHigh = 3
PinballTarget = 4
PinballRoof = 5
PinballHouse = 6
PinballFence = 7
PinballBridge = 8
PinballStatuary = 9
PinballScoring = [(100, 1),
 (150, 1),
 (200, 1),
 (250, 1),
 (350, 1),
 (100, 1),
 (50, 1),
 (25, 1),
 (100, 1),
 (10, 1)]
PinballCannonBumperInitialPos = (0, -20, 40)
RentalCop = 0
RentalCannon = 1
RentalGameTable = 2
GlitchKillerZones = [13300,
 13400,
 13500,
 13600]
ColorPlayer = (0.3,
 0.7,
 0.3,
 1)
ColorAvatar = (0.3,
 0.3,
 0.7,
 1)
ColorPet = (0.6,
 0.4,
 0.2,
 1)
ColorFreeChat = (0.3,
 0.3,
 0.8,
 1)
ColorSpeedChat = (0.2,
 0.6,
 0.4,
 1)
ColorNoChat = (0.8,
 0.5,
 0.1,
 1)
FactoryLaffMinimums = [(0, 0),
 (0, 0, 0),
 (0,
  0,
  0,
  0),
 (0, 0, 0)]
PICNIC_COUNTDOWN_TIME = 60
BossbotRTIntroStartPosHpr = (0,
 - 64,
 0,
 180,
 0,
 0)
BossbotRTPreTwoPosHpr = (0,
 - 20,
 0,
 180,
 0,
 0)
BossbotRTEpiloguePosHpr = (0,
 90,
 0,
 180,
 0,
 0)
BossbotBossBattleOnePosHpr = (0,
 390,
 0,
 0,
 0,
 0)
BossbotBossBattleOnePosHpr2 = (0,
 390,
 0,
 0,
 0,
 0)
BossbotBossPreTwoPosHpr = (0,
 20,
 0,
 0,
 0,
 0)
BossbotElevCamPosHpr = (0,
 - 100.544,
 7.18258,
 0,
 0,
 0)
BossbotFoodModelScale = 0.75
BossbotOilDamage = 5
BossbotNumFoodToExplode = 2
BossbotBossServingDuration = 5
BossbotPrepareBattleThreeDuration = 20
WaiterBattleAPosHpr = (20,
 - 400,
 0,
 0,
 0,
 0)
WaiterBattleBPosHpr = (-20,
 - 400,
 0,
 0,
 0,
 0)
BossbotBossBattleThreePosHpr = (0,
 355,
 0,
 0,
 0,
 0)
DinerBattleAPosHpr = (0,
                      -100,
 0,
 0,
 0,
 0)
DinerBattleBPosHpr = (0,
 -100,
 0,
 0,
 0,
 0)
BossbotBossMaxDamage = 2400
BossbotMaxSpeedDamage = 90
BossbotSpeedRecoverRate = 20
BossbotBossDifficultySettings = [
  # number of tables, number of diners per table, diner level, unflatten time, hungry duration, eat duration
  (14,8,10,3,30,25),
  (14,8,11,6,28,26),
  (14,8,12,7,26,27),
  (14,8,13,8,24,28),
  (14,8,14,9,22,29)
 ]
BossbotBossDamageMultipliers = [1, 1.1, 1.25, 1.4, 1.6]
BossbotRollSpeedMax = 50
BossbotRollSpeedMin = 20
BossbotTurnSpeedMax = 80
BossbotTurnSpeedMin = 40
BossbotTreadSpeedMax = 20.5
BossbotTreadSpeedMin = 6.5
CalendarFilterShowAll = 0
CalendarFilterShowOnlyHolidays = 1
CalendarFilterShowOnlyParties = 2
TTC = 1
DD = 2
MM = 3
GS = 4
DG = 5
BR = 6
OZ = 7
DL = 8
DefaultWantNewsPageSetting = 0
gmMagicWordList = ['restock',
 'restockUber',
 'autoRestock',
 'resistanceRestock',
 'restockSummons',
 'uberDrop',
 'rich',
 'maxBankMoney',
 'toonUp',
 'rod',
 'cogPageFull',
 'pinkSlips',
 'Tickets',
 'newSummons',
 'who',
 'who all']
NewsPageScaleAdjust = 0.85
AnimPropTypes = Enum(('Unknown',
 'Hydrant',
 'Mailbox',
 'Trashcan'), start = -1)
EmblemTypes = Enum(('Silver', 'Gold'))
NumEmblemTypes = 2
DefaultMaxBankMoney = 150000
DefaultBankItemId = 1350
ToonAnimStates = set(['off',
 'neutral',
 'victory',
 'Happy',
 'Sad',
 'Catching',
 'CatchEating',
 'Sleep',
 'walk',
 'jumpSquat',
 'jump',
 'jumpAirborne',
 'jumpLand',
 'run',
 'swim',
 'swimhold',
 'dive',
 'cringe',
 'OpenBook',
 'ReadBook',
 'CloseBook',
 'TeleportOut',
 'Died',
 'TeleportedOut',
 'TeleportIn',
 'Emote',
 'SitStart',
 'Sit',
 'Push',
 'Squish',
 'FallDown',
 'GolfPuttLoop',
 'GolfRotateLeft',
 'GolfRotateRight',
 'GolfPuttSwing',
 'GolfGoodPutt',
 'GolfBadPutt',
 'Flattened',
 'CogThiefRunning',
 'ScientistJealous',
 'ScientistEmcee',
 'ScientistWork',
 'ScientistLessWork',
 'ScientistPlay'])
AV_FLAG_REASON_TOUCH = 1
AV_FLAG_HISTORY_LEN = 500
AV_TOUCH_CHECK_DELAY_AI = 3.0
AV_TOUCH_CHECK_DELAY_CL = 1.0
AV_TOUCH_CHECK_DIST = 2.0
AV_TOUCH_CHECK_DIST_Z = 5.0
AV_TOUCH_CHECK_TIMELIMIT_CL = 0.002
AV_TOUCH_COUNT_LIMIT = 5
AV_TOUCH_COUNT_TIME = 300
hood2Id = [
    ('TTC', (ToontownCentral,)),
    ('DD', (DonaldsDock,)),
    ('MML', (MinniesMelodyland,)),
    ('DG', (DaisyGardens,)),
    ('TB', (TheBrrrgh,)),
    ('DDL', (DonaldsDreamland,)),
    ('TS', (Toonseltown,)),
    ('SC', (SkyClan,)),
    ('GZ', (GolfZone,)),
    ('GSW', (GoofySpeedway,)),
    ('GS', (GoofySpeedway,)),
    ('AA', (OutdoorZone,)),
    ('OT', (YeOlde,)),
    ('YEOLDE', (YeOlde,)),
    ('YOTT', (YeOlde,)),
    ('CEO', (BossbotHQ,)),
    ('CJ', (LawbotHQ,)),
    ('CFO', (CashbotHQ,)),
    ('VP', (SellbotHQ,)),
    ('BBHQ', (BossbotHQ,)),
    ('LBHQ', (LawbotHQ,)),
    ('CBHQ', (CashbotHQ,)),
    ('SBHQ', (SellbotHQ,)),
    ('FACTORY', (SellbotHQ, SellbotFactoryExt)),
    ('FRONTENTRY', (SellbotHQ, SellbotFactoryExt)),
    ('SIDEENTRY', (SellbotHQ, SellbotFactoryExt)),
    ('BULLION', (CashbotHQ,)),
    ('DOLLAR', (CashbotHQ,)),
    ('COIN', (CashbotHQ,)),
    ('OFFICEA', (LawbotHQ, LawbotOfficeExt)),
    ('OFFICEB', (LawbotHQ, LawbotOfficeExt)),
    ('OFFICEC', (LawbotHQ, LawbotOfficeExt)),
    ('OFFICED', (LawbotHQ, LawbotOfficeExt)),
    ('BACK', (BossbotHQ,)),
    ('MIDDLE', (BossbotHQ,)),
    ('FRONT', (BossbotHQ,))]
SuitLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]


# Buffs...

BMovementSpeed = 0
BMovementSpeedMultiplier = 2.3

BGagAccuracy = 1
BGagAccuracyMultiplier = 1.3

# Toon Stats
TOTAL_STATS = 28

STATS_COGS = 0
STATS_BLDGS = 1
STATS_ELITES = 2
STATS_FRIENDS = 3
STATS_CURR_FRIENDS = 4
STATS_TASKS = 5
STATS_VP = 6
STATS_CFO = 7
STATS_CJ = 8
STATS_CEO = 9
STATS_CM = 10
STATS_SAD = 11
STATS_CATALOG = 12
STATS_FISH = 13
STATS_TROLLEY = 14
STATS_GAGS = 15
STATS_TREASURES = 16
STATS_JB_SPENT = 17
STATS_JB_EARNED = 18
STATS_SOS = 19
STATS_UNITES = 20
STATS_SUMMONS = 21
STATS_FIRES = 22
STATS_FACTORIES = 23
STATS_MINTS = 24
STATS_STAGES = 25
STATS_CLUBS = 26
STATS_BOARD_OFFICES = 27

RegenLaffDict = {ToontownCentral: 1,
 OutdoorZone: 2,
 DonaldsDock: 3,
 DaisyGardens: 4,
 MinniesMelodyland: 5,
 TheBrrrgh: 6,
 DonaldsDreamland: 7}

                            # 1-default # 2 # 3 # 4
HouseInteriorLayoutPrices = [4000, 5000, 6000, 7000]
CODE_SUCCESS = 0
CODE_INVALID = 1
CODE_EXPIRED = 2
CODE_INELIGIBLE = 3
CODE_REWARD_ERROR = 4
CODE_TOO_MANY_ATTEMPTS = 5
CODE_UNAVAILABLE = 6

MagicWordInvokerPrefix = '~'
MagicWordTargetPrefix = '~~'
