from __future__ import absolute_import
import random
import time
from six.moves import range

MAX_GUMBALLS = 9999
MAX_BOOSTER_DURATION = 7 * 24 * 60 * 60
BOOSTER_HOURS = 2
RANDOM_BOOSTER_HOURS = 8
DAILY_BOOSTER_HOURS = 8

JELLYBEANS_GLOBAL = 14
JELLYBEANS_BINGO = 24
GUMBALLS_GLOBAL = 17
EXP_GAGS_GLOBAL = 12
EXP_GAGS_SUPPORT = 50
EXP_GAGS_POWER = 51
EXP_ACTIVITY_GLOBAL = 11
EXP_ACTIVITY_RACING = 20
EXP_ACTIVITY_TROLLEY = 21
EXP_ACTIVITY_GOLF = 22
EXP_ACTIVITY_FISHING = 23
FISH_RARITY = 8
MERIT_GLOBAL = 16
MERIT_SELLBOT = 3
MERIT_CASHBOT = 4
MERIT_LAWBOT = 5
MERIT_BOSSBOT = 6
MERIT_BOARDBOT = 7
EXP_DEPT_GLOBAL = 9
EXP_DEPT_SELLBOT = 30
EXP_DEPT_CASHBOT = 31
EXP_DEPT_LAWBOT = 32
EXP_DEPT_BOSSBOT = 33
EXP_DEPT_BOARDBOT = 34
REWARD_BOSS_GLOBAL = 13
REWARD_BOSS_SELLBOT = 40
REWARD_BOSS_CASHBOT = 41
REWARD_BOSS_LAWBOT = 42
REWARD_BOSS_BOSSBOT = 43
REWARD_BOSS_BOARDBOT = 44
ALL_STAR = 60
RANDOM = 70
REWARD_BOSS_SELLBOT_DOUBLE = 80

ADDITIVE = 1
ADDITIVE_MULTIPLICATIVE_PERC = 2
ADDITIVE_MULT = 3
MULTIPLICATIVE = 4
GLOBAL_BOSS_REWARDS = 5
ALL_STAR_MODE = 6
RANDOM_MODE = 7

ALL_STAR_BOOSTS = [EXP_GAGS_POWER, JELLYBEANS_GLOBAL, MERIT_GLOBAL, REWARD_BOSS_GLOBAL, EXP_DEPT_GLOBAL]
BOSS_REWARD_BOOSTS = [REWARD_BOSS_SELLBOT, REWARD_BOSS_CASHBOT, REWARD_BOSS_LAWBOT, REWARD_BOSS_BOSSBOT, REWARD_BOSS_BOARDBOT]
SUPPORT_GAG_TRACKS = [0, 2, 4, 6]
POWER_GAG_TRACKS = [1, 3, 5, 7]

BOOSTERS = {
    JELLYBEANS_GLOBAL: ('Jellybean Booster', '+25% Jellybeans', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 1.0),
    JELLYBEANS_BINGO: ('Fish Bingo Booster', 'x2 Jellybeans from Fish Bingo', 2, MULTIPLICATIVE, 0.0),
    GUMBALLS_GLOBAL: ('Gumball Booster', 'x2 Gumballs', 2, MULTIPLICATIVE, 0.0),
    EXP_GAGS_GLOBAL: ('Universal Gag Booster', '+1x Gag Experience', 1, ADDITIVE_MULT, 0.5),
    EXP_GAGS_SUPPORT: ('Support Gag Booster', '+1x Squirt, Sound, Toon-Up and Lure Experience', 1, ADDITIVE_MULT, 1.0),
    EXP_GAGS_POWER: ('Power Gag Booster', '+1x Trap, Zap, Throw and Drop Experience', 1, ADDITIVE_MULT, 1.0),
    EXP_ACTIVITY_GLOBAL: ('Activity XP Booster', '+25% Activity Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    EXP_ACTIVITY_RACING: ('Racing XP Booster', '+25% Racing Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 1.0),
    EXP_ACTIVITY_TROLLEY: ('Trolley XP Booster', '+25% Trolley Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 1.0),
    EXP_ACTIVITY_GOLF: ('Golf XP Booster', '+25% Golf Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 1.0),
    EXP_ACTIVITY_FISHING: ('Fishing XP Booster', '+25% Fishing Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 1.0),
    FISH_RARITY: ('Fish Rarity Booster', '+0.5 Fish Rarity', 0.5, ADDITIVE, 0.0),
    MERIT_GLOBAL: ('Universal Merit Booster', '+25% to all Merits', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    MERIT_SELLBOT: ('Invoice Booster', '+25% Invoices', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    MERIT_CASHBOT: ('Cogbuck Booster', '+25% Cogbucks', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    MERIT_LAWBOT: ('Patent Booster', '+25% Patents', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    MERIT_BOSSBOT: ('Stock Option Booster', '+25% Stock Options', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    MERIT_BOARDBOT: ('Boardbot Merit Booster', '+25% Boardbot Merits', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    EXP_DEPT_GLOBAL: ('Department XP Booster', '+25% Department Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    EXP_DEPT_SELLBOT: ('Sellbot XP Booster', '+25% Sellbot Department Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    EXP_DEPT_CASHBOT: ('Cashbot XP Booster', '+25% Cashbot Department Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    EXP_DEPT_LAWBOT: ('Lawbot XP Booster', '+25% Lawbot Department Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    EXP_DEPT_BOSSBOT: ('Bossbot XP Booster', '+25% Bossbot Department Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    EXP_DEPT_BOARDBOT: ('Boardbot XP Booster', '+25% Boardbot Department Experience', 0.25, ADDITIVE_MULTIPLICATIVE_PERC, 0.5),
    REWARD_BOSS_GLOBAL: ('Boss Reward Booster', '+1 Boss Reward', 1, GLOBAL_BOSS_REWARDS, 0.5),
    REWARD_BOSS_SELLBOT: ('V.P. Reward Booster', '+1 V.P. Reward', 1, ADDITIVE, 1.0),
    REWARD_BOSS_CASHBOT: ('C.F.O. Reward Booster', '+1 C.F.O. Reward', 1, ADDITIVE, 1.0),
    REWARD_BOSS_LAWBOT: ('C.L.O. Reward Booster', '+1 C.L.O. Reward', 1, ADDITIVE, 1.0),
    REWARD_BOSS_BOSSBOT: ('C.E.O. Reward Booster', '+1 C.E.O. Reward', 1, ADDITIVE, 1.0),
    REWARD_BOSS_BOARDBOT: ('Boardbot Reward Booster', '+1 Boardbot Reward', 1, ADDITIVE, 1.0),
    REWARD_BOSS_SELLBOT_DOUBLE: ('V.P. Reward Booster', 'x2 V.P. Rewards', 2, MULTIPLICATIVE, 0.0),
    ALL_STAR: ('All-Star Booster', 'Boosts multiple reward types', 1, ALL_STAR_MODE, 0.4),
    RANDOM: ('Random Booster', 'A random useful Booster', 1, RANDOM_MODE, 0.4),
}

NORMAL_OFFER_DATA = {
    MERIT_SELLBOT: (125, 0.6),
    MERIT_CASHBOT: (125, 0.6),
    MERIT_LAWBOT: (125, 0.6),
    MERIT_BOSSBOT: (125, 0.6),
    EXP_ACTIVITY_RACING: (100, 1.15),
    EXP_ACTIVITY_TROLLEY: (100, 1.15),
    EXP_ACTIVITY_GOLF: (100, 1.15),
    EXP_ACTIVITY_FISHING: (100, 1.15),
    EXP_DEPT_SELLBOT: (125, 0.35),
    EXP_DEPT_CASHBOT: (125, 0.35),
    EXP_DEPT_LAWBOT: (125, 0.35),
    EXP_DEPT_BOSSBOT: (125, 0.35),
    REWARD_BOSS_SELLBOT: (150, 0.6),
    REWARD_BOSS_CASHBOT: (150, 0.6),
    REWARD_BOSS_LAWBOT: (125, 0.5),
    REWARD_BOSS_BOSSBOT: (125, 0.5),
    JELLYBEANS_GLOBAL: (75, 3.0),
    EXP_GAGS_POWER: (100, 1.8),
    EXP_GAGS_SUPPORT: (100, 1.8),
}

DAILY_OFFERS = {
    0: (MERIT_GLOBAL, 600, DAILY_BOOSTER_HOURS),
    1: (EXP_ACTIVITY_GLOBAL, 450, DAILY_BOOSTER_HOURS),
    2: (JELLYBEANS_GLOBAL, 300, DAILY_BOOSTER_HOURS),
    3: (EXP_DEPT_GLOBAL, 450, DAILY_BOOSTER_HOURS),
    4: (EXP_GAGS_GLOBAL, 700, DAILY_BOOSTER_HOURS),
    5: (ALL_STAR, 1000, DAILY_BOOSTER_HOURS),
    6: (REWARD_BOSS_GLOBAL, 800, DAILY_BOOSTER_HOURS),
}

COG_BOUNTY_WEEKLY_LIMIT = 1000
GUMBALL_BOUNTIES = {
    'derrman': 5,
    'dopr': 10,
    'derrhand': 10,
    'dold': 10,
    'dopa': 10,
    'lgator': 15,
    'stenog': 15,
    'caseman': 15,
    'sgoat': 15,
    'duckshfl': 10,
    'ddiver': 12,
    'gatekeep': 14,
    'bellring': 17,
    'mouthp': 20,
    'fires': 24,
    'treek': 26,
    'fbed': 30,
    'prethink': 20,
    'rainmake': 24,
    'whunter': 28,
    'mslacker': 32,
    'mplayer': 38,
    'pcrat': 44,
    'chainsaw': 50,
    'psetter': 50,
    'hroller': 30,
}
GUMBALL_BOUNTY_GROUPS = {
    'lgator': ['lgator', 'stenog', 'caseman', 'sgoat'],
    'stenog': ['lgator', 'stenog', 'caseman', 'sgoat'],
    'caseman': ['lgator', 'stenog', 'caseman', 'sgoat'],
    'sgoat': ['lgator', 'stenog', 'caseman', 'sgoat'],
}

ALTIS_FUNCTIONAL_TYPES = set([
    JELLYBEANS_GLOBAL,
    GUMBALLS_GLOBAL,
    EXP_GAGS_GLOBAL,
    EXP_GAGS_SUPPORT,
    EXP_GAGS_POWER,
    MERIT_GLOBAL,
    MERIT_SELLBOT,
    MERIT_CASHBOT,
    MERIT_LAWBOT,
    MERIT_BOSSBOT,
    REWARD_BOSS_GLOBAL,
    REWARD_BOSS_SELLBOT,
    REWARD_BOSS_CASHBOT,
    REWARD_BOSS_LAWBOT,
    REWARD_BOSS_BOSSBOT,
    ALL_STAR,
])

def getBoosterName(boosterType):
    return BOOSTERS.get(int(boosterType), ('Unknown Booster', '', 0, ADDITIVE, 0))[0]

def getBoosterDescription(boosterType):
    return BOOSTERS.get(int(boosterType), ('Unknown Booster', '', 0, ADDITIVE, 0))[1]

def getBoosterDefinition(boosterType):
    return BOOSTERS.get(int(boosterType))

def _weightedPick(rng, pairs):
    total = sum([x[1] for x in pairs])
    if total <= 0:
        return pairs[0][0]
    value = rng.random() * total
    for item, weight in pairs:
        value -= weight
        if value <= 0:
            return item
    return pairs[-1][0]

def _nextMidnight():
    now = time.localtime()
    return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday + 1, 0, 0, 0, -1, -1, -1)))

def getNextBountyTimestamp():
    return _nextMidnight()

def getNextWeeklyBountyReset():
    now = time.localtime()
    days = (6 - now.tm_wday) % 7
    if days == 0:
        days = 7
    return int(time.mktime((now.tm_year, now.tm_mon, now.tm_mday + days, 0, 0, 0, -1, -1, -1)))

def getOffers(zoneId=0):
    rng = random.Random(_nextMidnight() + (int(zoneId) * 20))
    pool = dict([(boosterType, data) for boosterType, data in NORMAL_OFFER_DATA.items() if boosterType in ALTIS_FUNCTIONAL_TYPES])
    offers = []
    daily = DAILY_OFFERS.get(time.localtime().tm_wday)
    hasDaily = daily and daily[0] in ALTIS_FUNCTIONAL_TYPES
    count = min(4 if hasDaily else 5, len(pool))
    for index in range(count):
        pairs = [(boosterType, pool[boosterType][1]) for boosterType in sorted(pool.keys())]
        boosterType = _weightedPick(rng, pairs)
        cost = pool[boosterType][0]
        del pool[boosterType]
        offers.append((1000 + boosterType, boosterType, cost, BOOSTER_HOURS, 0))
    offers.append((3000 + RANDOM, RANDOM, 350, RANDOM_BOOSTER_HOURS, 2))
    if hasDaily:
        boosterType, cost, hours = daily
        offers.append((2000 + boosterType, boosterType, cost, hours, 1))
    return offers

def getOffer(offerId, zoneId=0):
    for offer in getOffers(zoneId):
        if offer[0] == int(offerId):
            return offer
    return None

def getRandomUsefulBooster(seed=None):
    choices = []
    for boosterType in sorted(ALTIS_FUNCTIONAL_TYPES):
        if boosterType in (GUMBALLS_GLOBAL, RANDOM):
            continue
        definition = BOOSTERS.get(boosterType)
        if not definition or definition[4] <= 0:
            continue
        choices.append((boosterType, definition[4]))
    rng = random.Random(seed)
    return _weightedPick(rng, choices)

def _activeTypes(rawBoosters, now=None):
    if now is None:
        now = time.time()
    active = []
    for data in rawBoosters or []:
        try:
            boosterType, endTimestamp, startTimestamp = data
            if float(endTimestamp) > now:
                active.append(int(boosterType))
        except:
            pass
    return active

def cleanupBoosters(rawBoosters, now=None):
    if now is None:
        now = time.time()
    clean = []
    for data in rawBoosters or []:
        try:
            boosterType, endTimestamp, startTimestamp = data
            if float(endTimestamp) > now:
                clean.append([int(boosterType), int(endTimestamp), int(startTimestamp)])
        except:
            pass
    return clean

def addBooster(rawBoosters, boosterType, seconds, now=None):
    if now is None:
        now = int(time.time())
    boosterType = int(boosterType)
    seconds = max(0, int(seconds))
    clean = cleanupBoosters(rawBoosters, now)
    for data in clean:
        if data[0] == boosterType:
            maxEnd = int(now) + MAX_BOOSTER_DURATION
            data[1] = min(maxEnd, data[1] + seconds)
            return clean, data[1]
    endTimestamp = min(int(now) + MAX_BOOSTER_DURATION, int(now) + seconds)
    clean.append([boosterType, endTimestamp, int(now)])
    return clean, endTimestamp

def hasBooster(rawBoosters, boosterType):
    return int(boosterType) in _activeTypes(rawBoosters)

def getGagExperienceMultiplier(rawBoosters, track):
    active = _activeTypes(rawBoosters)
    multiplier = active.count(EXP_GAGS_GLOBAL) * BOOSTERS[EXP_GAGS_GLOBAL][2]
    if int(track) in SUPPORT_GAG_TRACKS:
        multiplier += active.count(EXP_GAGS_SUPPORT) * BOOSTERS[EXP_GAGS_SUPPORT][2]
    elif int(track) in POWER_GAG_TRACKS:
        multiplier += active.count(EXP_GAGS_POWER) * BOOSTERS[EXP_GAGS_POWER][2]
    multiplier += active.count(ALL_STAR) * BOOSTERS[EXP_GAGS_POWER][2]
    return multiplier

def applyBoosters(rawBoosters, boosterTypes, value, applyRound=False):
    if type(boosterTypes) not in (list, tuple):
        boosterTypes = [boosterTypes]
    boosterTypes = [int(x) for x in boosterTypes]
    active = _activeTypes(rawBoosters)
    applying = []
    for boosterType in boosterTypes:
        applying.extend([boosterType] * active.count(boosterType))
    gagTypes = [EXP_GAGS_GLOBAL, EXP_GAGS_SUPPORT, EXP_GAGS_POWER]
    meritTypes = [MERIT_GLOBAL, MERIT_SELLBOT, MERIT_CASHBOT, MERIT_LAWBOT, MERIT_BOSSBOT, MERIT_BOARDBOT]
    deptTypes = [EXP_DEPT_GLOBAL, EXP_DEPT_SELLBOT, EXP_DEPT_CASHBOT, EXP_DEPT_LAWBOT, EXP_DEPT_BOSSBOT, EXP_DEPT_BOARDBOT]
    for unused in range(active.count(ALL_STAR)):
        if any([x in boosterTypes for x in gagTypes]):
            applying.append(EXP_GAGS_POWER)
        if JELLYBEANS_GLOBAL in boosterTypes:
            applying.append(JELLYBEANS_GLOBAL)
        if any([x in boosterTypes for x in meritTypes]):
            applying.append(MERIT_GLOBAL)
        if any([x in boosterTypes for x in BOSS_REWARD_BOOSTS + [REWARD_BOSS_GLOBAL]]):
            applying.append(REWARD_BOSS_GLOBAL)
        if any([x in boosterTypes for x in deptTypes]):
            applying.append(EXP_DEPT_GLOBAL)
    if any([x in boosterTypes for x in BOSS_REWARD_BOOSTS]):
        applying.extend([REWARD_BOSS_GLOBAL] * active.count(REWARD_BOSS_GLOBAL))
    boostedValue = value
    multBoost = 1.0
    for boosterType in applying:
        definition = BOOSTERS.get(boosterType)
        if not definition:
            continue
        amount = definition[2]
        mode = definition[3]
        if mode in (ADDITIVE, ADDITIVE_MULT, GLOBAL_BOSS_REWARDS):
            boostedValue += amount
        elif mode == ADDITIVE_MULTIPLICATIVE_PERC:
            multBoost += amount
    for boosterType in applying:
        definition = BOOSTERS.get(boosterType)
        if definition and definition[3] == MULTIPLICATIVE:
            boostedValue *= definition[2]
    boostedValue *= multBoost
    if applyRound:
        return int(round(boostedValue))
    return boostedValue
