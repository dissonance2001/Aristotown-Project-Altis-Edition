"""
FishGlobals

Codes passed between DistributedFishingSpotAI and DistributedFishingSpot.

Also includes debug functions to test fishing probability.
"""
from toontown.fishing.FishingRodCompat import FishingRodItemType, getRodDefinition as _compatGetRodDefinition  # TODO: swap to toontown.inventory once ported
from toontown.toonbase import TTLocalizer
from math import ceil, pow
import random
from toontown.toonbase import ToontownGlobals
import copy
import collections


# Movie codes
NoMovie = 0
EnterMovie = 1
ExitMovie = 2
CastMovie = 3
PullInMovie = 4

# How long may we stand watching our float bob, without reeling
# anything in?
CastTimeout = 45.0

# These codes indicate the category of item we might have pulled out,
# or the reason we failed to pull anything out.
Nothing = 0
QuestItem = 1
FishItem = 2
JellybeanItem = 3
BootItem = 4
GagItem = 5
BackgroundItem = 6
OverTankLimit = 7
FishItemNewEntry = 8
FishItemNewRecord = 9
CatchFailed = 10
MaterialItem = 11

# Indicates a Boot Genus, Species Pair. Used to differentiate
# a boot catch from a normal fishItem catch in Fish Bingo.
BingoBoot = (BootItem, 99)

ProbabilityDict = {
    94: FishItem,
    95: JellybeanItem,
    100: BootItem,
    2: BackgroundItem,
}
HalloweenProbabilityDict = {
    94: FishItem,
    95: JellybeanItem,
    100: BootItem,
    2: BackgroundItem,
    8: MaterialItem
}
SortedProbabilityCutoffs = list(ProbabilityDict.keys())
SortedProbabilityCutoffs.sort()
SortedHalloweenProbabilityCutoffs = list(HalloweenProbabilityDict.keys())
SortedHalloweenProbabilityCutoffs.sort()

Rod2JellybeanDict = {
    0: 10,
    1: 20,
    2: 30,
    3: 75,
    4: 150,
    5: 250,
    6: 500
}

# JellybeanFishingHolidayScoreMultiplier = 2

# Most rare value
MAX_RARITY = 8

FishingAngleMax = 50.0

# Value modifiers to determine fish values
OVERALL_VALUE_SCALE = 15
RARITY_VALUE_SCALE = 0.2
WEIGHT_VALUE_SCALE = 0.05 / 16.0

# Collection enums
COLLECT_NO_UPDATE = 0
COLLECT_NEW_ENTRY = 1
COLLECT_NEW_RECORD = 2


AllShopRods = [
    FishingRodItemType.Twig,
    FishingRodItemType.Bamboo,
    FishingRodItemType.Hardwood,
    FishingRodItemType.Steel,
    FishingRodItemType.Gold,
    FishingRodItemType.Platinum,
]

# Used in Edgar Allan Pole's Fishing Shop
# We are keeping this price separate til we get a better shop interface.
FishingRodCosts = {
    FishingRodItemType.Cardboard: 0,
    FishingRodItemType.Twig:      500,
    FishingRodItemType.Bamboo:    1250,
    FishingRodItemType.Hardwood:  2500,
    FishingRodItemType.Steel:     5000,
    FishingRodItemType.Gold:      7500,
    FishingRodItemType.Platinum:  10000
}

RarityColors = {
    1: (0.400, 1.000, 0.950, 1),
    2: (0.169, 1.000, 0.376, 1),
    3: (0.180, 0.329, 1.000, 1),
    4: (0.659, 0.180, 1.000, 1),
    5: (1.000, 0.635, 0.000, 1),
    6: (1.000, 0.866, 0.000, 1),
    7: (0.976, 0.541, 1.000, 1),
    8: (1.000, 0.169, 0.169, 1)
}

MaxRodId = 4

FishAudioFileDict = {
    # genus, : (fileName, loop, delay, playRate)
    -1: ('Clownfish.ogg', 1, 1.5, 1.0),
    0: ('BalloonFish.ogg', 1, 0, 1.23),
    2: ('CatFish.ogg', 1, 0, 1.26),
    4: ('Clownfish.ogg', 1, 1.5, 1.0),
    6: ('Frozen_Fish.ogg', 1, 0, 1.0),
    8: ('Starfish.ogg', 0, 0, 1.25),
    10: ('Holy_Mackerel.ogg', 1, 0.9, 1.0),
    12: ('Dog_Fish.ogg', 1, 0, 1.25),
    14: ('AmoreEel.ogg', 1, 0, 1.0),
    16: ('Nurse_Shark.ogg', 0, 0, 1.0),
    18: ('King_Crab.ogg', 0, 0, 1.0),
    20: ('Moon_Fish.ogg', 0, 1.0, 1.0),
    22: ('Seahorse.ogg', 1, 0, 1.26),
    24: ('Pool_Shark.ogg', 1, 2.0, 1.0),
    26: ('Bear_Acuda.ogg', 1, 0, 1.0),
    28: ('CutThroatTrout.ogg', 1, 0, 1.0),
    30: ('Piano_Tuna.ogg', 0, 0, 1.0),
    32: ('PBJ_Fish.ogg', 1, 0, 1.25),
    34: ('DevilRay.ogg', 0, 0, 1.0)
}

FishFileDict = {
    # genus, : (phase, mod file name, intro anim file name, swim anim file name (loops), shtick anim file name, pos, scale, h, p)
    #
    # -1 is default if model is not present
    -1: (4, 'clownFish-zero', 'clownFish-swim', 'clownFish-swim', None, (0.12, 0, -0.15), 0.38, -35, 20),
    0: (4, 'balloonFish-zero', 'balloonFish-swim', 'balloonFish-swim', None, (0.0, 0, 0.0), 1.0, 0, 0),
    2: (4, 'catFish-zero', 'catFish-swim', 'catFish-swim', None, (1.2, -2.0, 0.5), 0.22, -35, 10),
    4: (4, 'clownFish-zero', 'clownFish-swim', 'clownFish-swim', None, (0.12, 0, -0.15), 0.38, -35, 20),
    6: (4, 'frozenFish-zero', 'frozenFish-swim', 'frozenFish-swim', None, (0, 0, 0), 0.5, -35, 20),
    8: (4, 'starFish-zero', 'starFish-swim', 'starFish-swimLOOP', None, (0, 0, -0.38), 0.36, -35, 20),
    10: (4, 'holeyMackerel-zero', 'holeyMackerel-swim', 'holeyMackerel-swim', None, None, 0.4, 0, 0),
    12: (4, 'dogFish-zero', 'dogFish-swim', 'dogFish-swim', None, (0.8, -1.0, 0.275), 0.33, -38, 10),
    14: (4, 'amoreEel-zero', 'amoreEel-swim', 'amoreEel-swim', None, (0.425, 0, 1.15), 0.5, 0, 60),
    16: (4, 'nurseShark-zero', 'nurseShark-swim', 'nurseShark-swim', None, (0, 0, -0.15), 0.3, -40, 10),
    18: (4, 'kingCrab-zero', 'kingCrab-swim', 'kingCrab-swimLOOP', None, None, 0.4, 0, 0),
    20: (4, 'moonFish-zero', 'moonFish-swim', 'moonFish-swimLOOP', None, (-1.2, 14, -2.0), 0.33, 0, -10),
    22: (4, 'seaHorse-zero', 'seaHorse-swim', 'seaHorse-swim', None, (-0.57, 0.0, -2.1), 0.23, 33, -10),
    24: (4, 'poolShark-zero', 'poolShark-swim', 'poolShark-swim', None, (-0.45, 0, -1.8), 0.33, 45, 0),
    26: (4, 'BearAcuda-zero', 'BearAcuda-swim', 'BearAcuda-swim', None, (0.65, 0, -3.3), 0.2, -35, 20),
    28: (4, 'cutThroatTrout-zero', 'cutThroatTrout-swim', 'cutThroatTrout-swim', None, (-0.2, 0, -0.1), 0.5, 35, 20),
    30: (4, 'pianoTuna-zero', 'pianoTuna-swim', 'pianoTuna-swim', None, (0.3, 0, 0.0), 0.6, 40, 30),
    32: (4, 'PBJfish-zero', 'PBJfish-swim', 'PBJfish-swim', None, (0, 0, 0.72), 0.31, -35, 10),
    34: (4, 'devilRay-zero', 'devilRay-swim', 'devilRay-swim', None, (0, 0, 0), 0.4, -35, 20)
}

# How many unique fish we need to get the next fishing bonus
FISH_PER_BONUS = 10

TrophyDict = collections.OrderedDict([
    (0, (TTLocalizer.FishTrophyNameDict[0],)),
    (1, (TTLocalizer.FishTrophyNameDict[1],)),
    (2, (TTLocalizer.FishTrophyNameDict[2],)),
    (3, (TTLocalizer.FishTrophyNameDict[3],)),
    (4, (TTLocalizer.FishTrophyNameDict[4],)),
    (5, (TTLocalizer.FishTrophyNameDict[5],)),
    (6, (TTLocalizer.FishTrophyNameDict[6],))
])

# Indexes into the FishDict data
WEIGHT_MIN_INDEX = 0
WEIGHT_MAX_INDEX = 1
RARITY_INDEX = 2
ZONE_LIST_INDEX = 3

Anywhere = 1

# Rarity Names (for trading cards)
#
# 1-2 Very Common
# 3-4 Common
# 5-6 Rare
# 7-8 Very Rare
# 9 Extremely Rare
# 10 Ultra Rare

# For compactness in the fishDict table, let's make an alias
TTG = ToontownGlobals

# Genus is stored as an even number just to perforate the space for future additions
# FishDict stores a dictionary of fish properties
# GENUS : SPECIES_LIST
# SPECIES_LIST is a list of SPECIES
# Each SPECIES defines properties: (WEIGHT_MIN, WEIGHT_MAX, RARITY, ZONE_LIST)
__fishDict = collections.OrderedDict([
    # Balloon Fish #
    (0, ((1, 3, 1, (Anywhere,)),  # Balloon Fish
         (1, 1, 4, (TTG.ToontownCentral, Anywhere)),  # Hot Air Balloon Fish
         (3, 5, 5, (TTG.PunchlinePlace, TTG.TheBrrrgh)),  # Weather Balloon Fish
         (3, 5, 3, (TTG.SillyStreet, TTG.DaisyGardens)),  # Water Balloon Fish
         (1, 5, 2, (TTG.LoopyLane, TTG.ToontownCentral)))),  # Red Balloon Fish

    # Cat Fish #
    (2, ((2, 6, 1, (TTG.DaisyGardens, Anywhere)),  # Cat Fish
         (2, 6, 8, (TTG.ElmStreet, TTG.DaisyGardens)),  # Siamese Cat Fish
         (5, 11, 4, (TTG.LullabyLane,)),  # Alley Cat Fish
         (2, 6, 3, (TTG.DaisyGardens,)),  # Tabby Cat Fish
         (5, 11, 2, (TTG.DonaldsDreamland,)))),  # Tom Cat Fish

    # Clown Fish #
    (4, ((2, 8, 1, (TTG.ToontownCentral, Anywhere)),  # Clown Fish
         (2, 8, 4, (TTG.ToontownCentral, Anywhere)),  # Sad Clown Fish
         (2, 8, 2, (TTG.ToontownCentral, Anywhere)),  # Party Clown Fish
         (2, 8, 6, (TTG.ToontownCentral, TTG.MinniesMelodyland)))),  # Circus Clown Fish

    # Frozen Fish #
    (6, ((8, 12, 1, (TTG.TheBrrrgh,)),)),  # Frozen Fish

    # Star Fish #
    (8, ((1, 5, 1, (Anywhere,)),  # Star Fish
         (2, 6, 2, (TTG.MinniesMelodyland, Anywhere)),  # Five Star Fish
         (5, 10, 5, (TTG.MinniesMelodyland, Anywhere)),  # Rock Star Fish
         (1, 5, 7, (Anywhere,)),  # Shining Star Fish
         (1, 5, 8, (Anywhere,)))),  # All Star Fish

    # Holey Mackerel #
    (10, ((6, 10, 8, (TTG.OutdoorZone, Anywhere)),)),  # Holey Mackerel

    # Dog Fish #
    (12, ((7, 15, 1, (TTG.DonaldsDock, Anywhere)),  # Dog Fish
          (18, 20, 6, (TTG.DonaldsDock,)),  # Bull Dog Fish
          (1, 5, 5, (TTG.DonaldsDock,)),  # Hot Dog Fish
          (3, 7, 4, (TTG.DonaldsDock,)),  # Dalmation Dog Fish
          (1, 2, 2, (TTG.DonaldsDock, Anywhere)))),  # Puppy Dog Fish

    # Amore Eel #
    (14, ((2, 6, 1, (TTG.DaisyGardens, Anywhere)),  # Amore Eel
          (2, 6, 3, (TTG.DaisyGardens,)))),  # Electric Amore Eel

    # Nurse Shark #
    (16, ((4, 12, 5, (TTG.MinniesMelodyland, Anywhere)),  # Nurse Shark
          (4, 12, 7, (TTG.BaritoneBoulevard, TTG.MinniesMelodyland)),  # Clara Nurse Shark
          (4, 12, 8, (TTG.TenorTerrace, TTG.MinniesMelodyland)))),  # Florence Nurse Shark

    # King Crab #
    (18, ((2, 4, 3, (TTG.DonaldsDock, Anywhere)),  # King Crab
          (5, 8, 7, (TTG.TheBrrrgh,)),  # Alaskan King Crab
          (4, 6, 8, (TTG.YeOlde, TTG.LighthouseLane)))),  # Old King Crab

    # Moon Fish #
    (20, ((4, 6, 1, (TTG.DonaldsDreamland,)),  # Moon Fish
          (14, 18, 8, (TTG.DonaldsDreamland,)),  # Full Moon Fish
          (6, 10, 8, (TTG.LullabyLane,)),  # Half Moon Fish
          (1, 1, 3, (TTG.DonaldsDreamland,)),  # New Moon Fish
          (2, 6, 6, (TTG.LullabyLane,)),  # Crescent Moon Fish
          (10, 14, 4, (TTG.DonaldsDreamland, TTG.DaisyGardens)))),  # Harvest Moon Fish

    # Sea Horse #
    (22, ((12, 16, 2, (TTG.DaisyGardens, Anywhere)),  # Sea Horse
          (14, 18, 3, (TTG.DaisyGardens, Anywhere)),  # Rocking Sea Horse
          (14, 20, 5, (TTG.DaisyGardens,)),  # Clydesdale Sea Horse
          (14, 20, 7, (TTG.DaisyGardens,)))),  # Arabian Sea Horse

    # Pool Shark #
    (24, ((9, 11, 3, (Anywhere,)),  # Pool Shark
          (8, 12, 5, (TTG.DaisyGardens, TTG.DonaldsDock)),  # Kiddie Pool Shark
          (8, 12, 6, (TTG.DaisyGardens, TTG.DonaldsDock)),  # Swimming Pool Shark
          (8, 16, 7, (TTG.DaisyGardens, TTG.DonaldsDock)))),  # Olympic Pool Shark

    # Bear Acuda #
    (26, ((10, 18, 2, (TTG.TheBrrrgh,)),  # Brown Bear Acuda
          (10, 18, 3, (TTG.TheBrrrgh,)),  # Black Bear Acuda
          (10, 18, 4, (TTG.TheBrrrgh,)),  # Koala Bear Acuda
          (10, 18, 5, (TTG.TheBrrrgh,)),  # Honey Bear Acuda
          (12, 20, 6, (TTG.TheBrrrgh,)),  # Polar Bear Acuda
          (14, 20, 7, (TTG.TheBrrrgh,)),  # Panda Bear Acuda
          (14, 20, 8, (TTG.SleetStreet, TTG.TheBrrrgh)),  # Kodiac Bear Acuda
          (16, 20, 8, (TTG.WalrusWay, TTG.TheBrrrgh)))),  # Grizzly Bear Acuda

    # Cutthroat Trout #
    (28, ((2, 10, 2, (TTG.DonaldsDock, Anywhere)),  # Cutthroat Trout
          (4, 10, 6, (TTG.BarnacleBoulevard, TTG.DonaldsDock)),  # Captain Cutthroat Trout
          (4, 10, 7, (TTG.SeaweedStreet, TTG.DonaldsDock)))),  # Scurvy Cutthroat Trout

    # Piano Tuna #
    (30, ((13, 17, 5, (TTG.MinniesMelodyland, Anywhere)),  # Piano Tuna
          (16, 20, 8, (TTG.AltoAvenue, TTG.MinniesMelodyland)),  # Grand Piano Tuna
          (12, 18, 8, (TTG.TenorTerrace, TTG.MinniesMelodyland)),  # Baby Grand Piano Tuna
          (12, 18, 6, (TTG.MinniesMelodyland,)),  # Upright Piano Tuna
          (12, 18, 7, (TTG.MinniesMelodyland,)))),  # Player Piano Tuna

    # PB&J Fish #
    (32, ((1, 5, 2, (TTG.ToontownCentral, Anywhere)),  # PB&J Fish
          (1, 5, 3, (TTG.TheBrrrgh, Anywhere)),  # Grape PB&J Fish
          (1, 5, 4, (TTG.DaisyGardens,)),  # Crunchy PB&J Fish
          (1, 5, 5, (TTG.DonaldsDreamland,)),  # Strawberry PB&J Fish
          (1, 5, 8, (TTG.TheBrrrgh, TTG.DonaldsDreamland)))),  # Concord Grape PB&J Fish

    # Devil Ray #
    (34, ((1, 20, 8, (TTG.DonaldsDreamland, Anywhere)),))  # Devil Ray
])

def getSpecies(genus):
    """
    :param genus:
    :return: the list of species it contains
    """
    return __fishDict[genus]

def getGenera():
    """
    :return: a list of all genera (plural for genus)
    """
    return list(__fishDict.keys())


# Indexes into the FishDict data
ROD_WEIGHT_MIN_INDEX = 0
ROD_WEIGHT_MAX_INDEX = 1
ROD_CAST_COST_INDEX = 2


def getEffectiveRarity(rarity, offset):
    return min(MAX_RARITY, rarity + offset)


def getRodDefinition(rodSubtype):
    return _compatGetRodDefinition(rodSubtype)


def canBeCaughtByRod(genus, species, rodSubtype):
    minFishWeight, maxFishWeight = getWeightRange(genus, species)
    rodDefinition = getRodDefinition(rodSubtype)
    minRodWeight, maxRodWeight = rodDefinition.getWeightRange()
    # See if the weight ranges overlap. If they do at all, we can
    # catch this fish with this rod
    if minRodWeight <= maxFishWeight and maxRodWeight >= minFishWeight:
        return 1
    else:
        return 0


def __rollRarityDice(rodSubtype, rNumGen=None):
    """
    :returns: a rarity level [1-8] with proper percent chance of getting that rarity level
    :rtype: int
    """
    # Now we can take the rodId into consideration. This allows us to have the higher
    # level rods catch more rare fish
    if rNumGen is None:
        diceRoll = random.random()
    else:
        diceRoll = rNumGen.random()

    rodDefinition = getRodDefinition(rodSubtype)
    exp = rodDefinition.getFishRarityFactor()
    rarity = int(ceil(10 * (1 - pow(diceRoll, exp))))
    # If random.random() returns exactly 1.0, the math has an edge condition where
    # rarity will equal exactly 0, which is not a valid value, just return 1 instead
    if rarity <= 0:
        rarity = 1
    # Corporate Clash only allows for rarities 1-8 in our fishing globals, but the formula still rolls 9 and 10
    # This prevents some needless rarity re-rolling and applies rarity 9 to 7 and rarity 10 to 8
    if rarity == 9:
        rarity = 7
    if rarity == 10:
        rarity = 8
    return rarity


def getRandomWeight(genus, species, rodSubtype=None, rNumGen=None):
    """
    Get a weight value for the fish specified, taking the rod we
    are using into account (if specified). This returns weights that
    have a nice bell curve distribution.

    :param genus:
    :param species:
    :param rodSubtype:
    :param rNumGen:
    :return: int
    """
    minFishWeight, maxFishWeight = getWeightRange(genus, species)
    if rodSubtype is None:
        # Use the actual fish values unmodified
        minWeight = minFishWeight
        maxWeight = maxFishWeight
    else:
        # Clamp the effective fish weight by the amount this rod can handle
        rodDefinition = getRodDefinition(rodSubtype)
        minRodWeight, maxRodWeight = rodDefinition.getWeightRange()
        minWeight = max(minFishWeight, minRodWeight)
        maxWeight = min(maxFishWeight, maxRodWeight)

    # Add a few random numbers to give a natural bell curve of probabilities
    if rNumGen is None:
        randNumA = random.random()
        randNumB = random.random()
    else:
        randNumA = rNumGen.random()
        randNumB = rNumGen.random()

    randNum = (randNumA + randNumB) / 2.0
    # Scale the 0-1 values into the effective weight range possible
    randWeight = minWeight + (maxWeight - minWeight) * randNum
    # Convert to ounces and round to integer
    return int(round(randWeight * 16))


def getRandomFishVitals(zoneId, rodSubtype, rNumGen = None):
    """
    Attempts to generate a random fish based on the indicated zoneId and rodId.
    If all 10 possible rarities are rolled without a fish, safely return a
    generic 1 pound BalloonFish.

    :param zoneId:
    :param rodSubtype:
    :param rNumGen:
    :return:
    """
    triedRarities = []
    while True:
        rarity = __rollRarityDice(rodSubtype, rNumGen)

        if rarity not in triedRarities:
            triedRarities.append(rarity)
        else:
            # We have already tried this rarity, keep rolling.
            continue

        rodDict = __pondInfoDict.get(zoneId, __fallbackPondInfo)
        rarityDict = rodDict.get(rodSubtype, {})
        fishList = rarityDict.get(rarity)

        if fishList:
            if rNumGen is None:
                genus, species = random.choice(fishList)
            else:
                genus, species = rNumGen.choice(fishList)
            weight = getRandomWeight(genus, species, rodSubtype, rNumGen)
            return (1, genus, species, weight)

        # If every rarity has been rolled, this pond is dumb, therefore return a
        # generic balloon fish that weighs 1 pound.
        if len(triedRarities) == 10:
            return (0, 0, 0, 16)


def getWeightRange(genus, species):
    """
    :returns: the weight range of this genus, species by looking up the value in the FishDict.
              Weight range is returned as a 2-item list (min, max) in pounds

    :type genus: int
    :type species: int
    """
    fishInfo = __fishDict[genus][species]
    return (fishInfo[WEIGHT_MIN_INDEX], fishInfo[WEIGHT_MAX_INDEX])


def getRarity(genus, species):
    """
    Return the rarity of this genus, species by looking up the value in the FishDict

    :param genus:
    :param species:
    :return:
    """
    return __fishDict[genus][species][RARITY_INDEX]


def getValue(genus, species, weight):
    """
    Returns the monetary value of this fish using a delicately balanced formula
    based on the fish species, rarity, and weight

    :param genus:
    :param species:
    :param weight:
    :return: finalValue (int)
    """
    rarity = getRarity(genus, species)
    rarityValue = pow(RARITY_VALUE_SCALE * rarity, 1.5)
    weightValue = pow(WEIGHT_VALUE_SCALE * weight, 1.1)
    value = OVERALL_VALUE_SCALE * (rarityValue + weightValue)
    # Round up because jellybeans should be integers
    finalValue = int(ceil(value))
    # base = getBase()
    # if hasattr(base, 'cr') and base.cr: Might implement this again in the future /shrug
        # if hasattr(base.cr, 'newsManager') and base.cr.newsManager:
            # holidayIds = base.cr.newsManager.getHolidayIdList()
            # if ToontownGlobals.JELLYBEAN_FISHING_HOLIDAY in holidayIds or ToontownGlobals.JELLYBEAN_FISHING_HOLIDAY_MONTH in holidayIds:
                # finalValue *= JellybeanFishingHolidayScoreMultiplier
    # elif ToontownGlobals.JELLYBEAN_FISHING_HOLIDAY in simbase.air.holidayManager.currentHolidays or ToontownGlobals.JELLYBEAN_FISHING_HOLIDAY_MONTH in simbase.air.holidayManager.currentHolidays:
        # finalValue *= JellybeanFishingHolidayScoreMultiplier
    return finalValue


__totalNumFish = 0

__emptyRodDict = {}
for rodSubtype in FishingRodItemType:
    __emptyRodDict[rodSubtype] = {}

__anywhereDict = copy.deepcopy(__emptyRodDict)

"""
pondInfoDict is a version of the fishDict, with zone as the primary key, rod as the secondary key,
with a list of fish (genus, species) and their effecitve rarities at that pond.
{ zone1 : { rod0 : ((genus, species, effectiveRarity), etc)
            rod1 : ((genus, species, effectiveRarity), etc)
            etc
           }
  zone2 : { rod0 : ((genus, species, effectiveRarity), etc)
            rod1 : ((genus, species, effectiveRarity), etc)
            etc
           }
  etc
  }
"""
__pondInfoDict = {}

# Loop through all the fish
for genus, speciesList in list(__fishDict.items()):
    for species in range(len(speciesList)):
        __totalNumFish += 1
        # Pull off the properties we are interested in
        speciesDesc = speciesList[species]
        rarity = speciesDesc[RARITY_INDEX]
        zoneList = speciesDesc[ZONE_LIST_INDEX]
        # Add entries for all the zones this Fish is found in
        for zoneIndex in range(len(zoneList)):
            # Special case if the fish is found anywhere, store it in a temp
            # holding dict to be added to the pondInfoDict at the end of all this
            zone = zoneList[zoneIndex]
            effectiveRarity = getEffectiveRarity(rarity, zoneIndex)
            if zone == Anywhere:
                # Now go through the rod indexes adding fish to the pond that
                # can be caught by that rod
                for rodSubtype, rarityDict in list(__anywhereDict.items()):
                    if canBeCaughtByRod(genus, species, rodSubtype):
                        fishList = rarityDict.setdefault(effectiveRarity, [])
                        fishList.append((genus, species))

            else:
                # The effective rarity is higher the later the zone is
                # on the list
                # Fetch or create the rod dict
                # Note - we do not use setdefualt here so we do not have to
                # waste a bunch of copy.deepcopy's of the emptyRodDict
                pondZones = [zone]
                subZones = ToontownGlobals.HoodHierarchy.get(zone)
                if subZones:
                    pondZones.extend(subZones)
                for pondZone in pondZones:
                    if pondZone in __pondInfoDict:
                        rodDict = __pondInfoDict[pondZone]
                    else:
                        rodDict = copy.deepcopy(__emptyRodDict)
                        __pondInfoDict[pondZone] = rodDict
                    # Now go through the rod indexes adding fish to the pond that
                    # can be caught by that rod
                    for rodSubtype, rarityDict in list(rodDict.items()):
                        if canBeCaughtByRod(genus, species, rodSubtype):
                            fishList = rarityDict.setdefault(effectiveRarity, [])
                            fishList.append((genus, species))

# Now add the fish in the anywhere dict to the pondInfoDict entries
for zone, rodDict in list(__pondInfoDict.items()):
    for rodSubtype, anywhereRarityDict in list(__anywhereDict.items()):
        for rarity, anywhereFishList in list(anywhereRarityDict.items()):
            rarityDict = rodDict[rodSubtype]
            fishList = rarityDict.setdefault(rarity, [])
            fishList.extend(anywhereFishList)

# Fallback entry for pond zones that aren't in the table above (e.g. Altis
# hoods/legacy zones that don't exist in Corporate Clash's game world, so no
# fish-location data ever mentions them). Such a zone still gets whatever
# fish are catchable "Anywhere" instead of crashing HoodAI's pond startup
# with a KeyError.
__fallbackPondInfo = copy.deepcopy(__emptyRodDict)
for rodSubtype, anywhereRarityDict in list(__anywhereDict.items()):
    for rarity, anywhereFishList in list(anywhereRarityDict.items()):
        rarityDict = __fallbackPondInfo[rodSubtype]
        fishList = rarityDict.setdefault(rarity, [])
        fishList.extend(anywhereFishList)


def getPondDict(zoneId):
    print(__pondInfoDict.get(zoneId, __fallbackPondInfo))


def getTotalNumFish():
    return __totalNumFish

# Testing and debugging functions


def testRarity(rodId = 0, numIter = 100000, rNumGen = None):
    """
    For debugging only: run this to check the percentage chance of finding each rarity level.
    Prints out a dictionary of the values from simulation.

    :param rodId: 0
    :param numIter: 100000
    """
    d = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0}
    for i in range(numIter):
        v = __rollRarityDice(rodId, rNumGen)
        d[v] += 1
    # convert to a percentage
    for rarity, count in list(d.items()):
        percentage = count / float(numIter) * 100
        d[rarity] = percentage
    print(d)


def getRandomFish():
    genus = random.choice(list(__fishDict.keys()))
    species = random.randint(0, len(__fishDict[genus]) - 1)
    return (genus, species)


def getPondInfo():
    # This looks best when pprinted
    # import pprint
    # pprint.pprint(FishGlobals.getPondInfo())
    return __pondInfoDict


def getSimplePondInfo():
    # This looks best when pprinted
    # import pprint
    # pprint.pprint(FishGlobals.getPondInfo())
    info = {}
    for pondId, pondInfo in list(__pondInfoDict.items()):
        pondFishList = []
        for rodId, rodInfo in list(pondInfo.items()):
            for rarity, fishList in list(rodInfo.items()):
                for fish in fishList:
                    if fish not in pondFishList:
                        pondFishList.append(fish)
        pondFishList.sort()
        info[pondId] = pondFishList
    return info


def _getFallbackPondFishList():
    # Same flattening getSimplePondInfo() does, just for the "Anywhere fish
    # only" fallback pond used when a zone isn't in __pondInfoDict at all.
    pondFishList = []
    for rodId, rodInfo in list(__fallbackPondInfo.items()):
        for rarity, fishList in list(rodInfo.items()):
            for fish in fishList:
                if fish not in pondFishList:
                    pondFishList.append(fish)
    pondFishList.sort()
    return pondFishList


def getPondGeneraList(pondId):
    tmpList = []
    generaList = []
    pondInfo = getSimplePondInfo()
    # Zones that don't exist in Corporate Clash's game world (e.g. Altis-only
    # legacy hoods) won't be in pondInfo; fall back to "Anywhere" fish rather
    # than crashing HoodAI's pond startup.
    fishList = pondInfo.get(pondId)
    if fishList is None:
        fishList = _getFallbackPondFishList()
    for fish in fishList:
        if fish[0] not in tmpList:
            tmpList.append(fish[0])
            generaList.append(fish)
    return generaList


def printNumGeneraPerPond():
    pondInfo = getSimplePondInfo()
    for pondId, fishList in list(pondInfo.items()):
        generaList = []
        for fish in fishList:
            if fish[0] not in generaList:
                generaList.append(fish[0])
        print('Pond %s has %s Genera' % (pondId, len(generaList)))


def generateFishingReport(numCasts = 10000, hitRate = 0.8):
    """
    Prints out a report from a full simulation of the fishing
    system, including boots, jellybean bonuses, and the cost of casting.
    Shows profit per rod and per pond.

    hitRate is how often the user hits a fish
    hitRate of 1.0 means you always hit, 0.5 means half the time

    :param numCasts: 10000
    :param hitRate: 0.8
    """
    totalPondMoney = {}
    totalRodMoney = {}
    totalPondBaitCost = {}
    # This function is not updated to use hammerspace logic.
    # Don't expect it to work.
    for pond in __pondInfoDict:
        totalPondMoney[pond] = 0
        totalPondBaitCost[pond] = 0
        for rod in range(MaxRodId + 1):
            totalRodMoney.setdefault(rod, 0)
            baitCost = getCastCost(rod)
            for cast in range(numCasts):
                totalPondBaitCost[pond] += baitCost
                # Figure that you do not always get a hit
                if random.random() > hitRate:
                    # You missed - go to the next cast
                    continue
                # Figure out what you got
                rand = random.random() * 100.0
                for cutoff in SortedProbabilityCutoffs:
                    if rand <= cutoff:
                        itemType = ProbabilityDict[cutoff]
                        break
                if itemType == FishItem:
                    success, genus, species, weight = getRandomFishVitals(pond, rod)
                    if success:
                        value = getValue(genus, species, weight)
                        totalPondMoney[pond] += value
                        totalRodMoney[rod] += value
                    # Else, it is a boot, which we do not care about
                # Fished up some jellybeans
                elif itemType == JellybeanItem:
                    value = Rod2JellybeanDict[rod]
                    totalPondMoney[pond] += value
                    totalRodMoney[rod] += value

    numPonds = len(totalPondMoney)
    for pond, money in list(totalPondMoney.items()):
        baitCost = 0
        for rod in range(MaxRodId + 1):
            baitCost += getCastCost(rod)
        totalCastCost = baitCost * numCasts
        print(('pond: %s  totalMoney: %s profit: %s perCast: %s' %
               (pond, money,
                money - totalCastCost,  # Profit
                (money - totalCastCost) / float(numCasts * (MaxRodId + 1))),  # Profit per cast
               ))
    for rod, money in list(totalRodMoney.items()):
        baitCost = getCastCost(rod)
        totalCastCost = baitCost * (numCasts * numPonds)
        print(('rod: %s totalMoney: %s castCost: %s profit: %s perCast: %s' %
               (rod, money,
                totalCastCost,
                money - totalCastCost,  # Profit
                (money - totalCastCost) / float(numCasts * numPonds)),  # Profit per cast
               ))


# ---------------------------------------------------------------------------
# Legacy compatibility block.
#
# Your project's older dockside "fishing spot" system (toontown/safezone/
# DistributedFishingSpot.py, DistributedFishingSpotAI.py) and a few other
# untouched files (toontown/ai/FishManagerAI.py, toontown/catalog/
# CatalogPoleItem.py, toontown/shtiker/FishPage.py, toontown/shtiker/
# ItemsPage.py, toontown/toon/DistributedNPCFishermanAI.py,
# toontown/toon/DistributedNPCPetclerkAI.py) still import names from this
# module that Corporate Clash's rewritten fishing system no longer defines,
# because Clash replaced rod file/price/rarity lookups with its inventory
# item-registry system (see FishingRodCompat.py). These are restored here,
# verbatim from your original FishGlobals.py, purely so that pre-existing,
# untouched code keeps working. None of the newly-ported pond/bingo code
# reads from this block.
# ---------------------------------------------------------------------------

CertItem = 6

RodFileDict = {0: 'phase_4/models/props/pole_treebranch-mod',
 1: 'phase_4/models/props/pole_bamboo-mod',
 2: 'phase_4/models/props/pole_wood-mod',
 3: 'phase_4/models/props/pole_steel-mod',
 4: 'phase_4/models/props/pole_gold-mod'}
RodPriceDict = {0: 0,
 1: 400,
 2: 800,
 3: 1200,
 4: 2000}
_LegacyGlobalRarityDialBase = 4.3  # matches FishingRodCompat.GlobalRarityDialBase; kept separate to avoid import-order issues
RodRarityFactor = {0: 1.0 / (_LegacyGlobalRarityDialBase * 1),
 1: 1.0 / (_LegacyGlobalRarityDialBase * 0.975),
 2: 1.0 / (_LegacyGlobalRarityDialBase * 0.95),
 3: 1.0 / (_LegacyGlobalRarityDialBase * 0.9),
 4: 1.0 / (_LegacyGlobalRarityDialBase * 0.85)}

__rodDict = {0: (0, 4, 1),
 1: (0, 8, 2),
 2: (0, 12, 3),
 3: (0, 16, 4),
 4: (0, 20, 5)}


def getCastCost(rodId):
    return __rodDict[rodId][ROD_CAST_COST_INDEX]


def getRodWeightRange(rodIndex):
    rodProps = __rodDict[rodIndex]
    return (rodProps[ROD_WEIGHT_MIN_INDEX], rodProps[ROD_WEIGHT_MAX_INDEX])


# Your legacy dockside rod system uses 5 tiers, numbered 0-4 (see RodFileDict
# above). Corporate Clash's rod system (FishingRodItemType, in
# FishingRodCompat.py) uses 7 tiers numbered 1-7, since Clash added two more
# rods (Twig and Platinum) that don't exist in the legacy system. Both
# systems call the same getRandomFishVitals()/getRodDefinition() below, so
# any legacy rod ID has to be translated to its closest new-style equivalent
# first - matched by rod name/material where Clash kept the same tier, and
# by closest progression position for tiers Clash inserted.
_LegacyRodIdToFishingRodItemType = {
    0: FishingRodItemType.Cardboard,   # pole_treebranch-mod
    1: FishingRodItemType.Bamboo,      # pole_bamboo-mod
    2: FishingRodItemType.Hardwood,    # pole_wood-mod (closest match to "Wood")
    3: FishingRodItemType.Steel,       # pole_steel-mod
    4: FishingRodItemType.Gold,        # pole_gold-mod
}


def legacyRodIdToFishingRodItemType(legacyRodId):
    """Translate a legacy (0-4) rod id, as stored on the avatar and used by
    the dockside DistributedFishingSpotAI system, to the corresponding
    FishingRodItemType used by getRandomFishVitals()/getRodDefinition().
    """
    return _LegacyRodIdToFishingRodItemType.get(legacyRodId, FishingRodItemType.Cardboard)
