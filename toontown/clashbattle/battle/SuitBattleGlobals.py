from toontown.toonbase import TTLocalizer
from toontown.clashbattle.battle import PassiveAttributeDefs
from toontown.clashbattle.battle.BattleBase import *
from toontown.clashsuit.suit.SuitDefinitions import suitBuildBattleAttributeDict, suitGetMinibossNamesCode,\
                                          suitGetStreetInfo, suitGetReviveInfo, suitGetMercNamesCode, \
                                          suitGetAlwaysSkelecogNamesCode, suitGetAlwaysExecutiveNamesCode, \
                                          suitGetIterativeChatNamesCode, suitGetBountyNamesCode, suitGroupSuitsByDept, \
                                          suitGetBountyGroupsByType, suitGetLootNamesCode, suitGetOverrideDeaths, \
                                          suitGetExtendMovieTime, suitGetBowtieSuits, suitGetNoTieSuits, \
                                          suitGetDisallowedSpawnsNamesCode
from toontown.clashsuit.suit.SuitDefinitionsBase import SuitDefinitions, suitGetInvasionableSuits
from toontown.toonbase import TTLocalizer
from toontown.utils.DirectNotifyCategory import getNotify

notify = getNotify("SuitBattleGlobals")

COG_MINIBOSSES = suitGetMinibossNamesCode()
SuitAttributes = suitBuildBattleAttributeDict()
JOIN_CHANCE_OVERRIDES, STUBBORN_COGS, STREET_MAX_COG, STREET_BATTLE_COG_CAP, CANT_JOIN_BATTLES = suitGetStreetInfo()
MERCS = suitGetMercNamesCode()
REVIVE_ATTRIBUTES = suitGetReviveInfo()
ALWAYS_SKELECOGS = suitGetAlwaysSkelecogNamesCode()
ALWAYS_EXECUTIVES = suitGetAlwaysExecutiveNamesCode()
ITERATIVE_CHAT = suitGetIterativeChatNamesCode()
COG_BOUNTIES = suitGetBountyNamesCode()
COG_BOUNTY_GROUPS = suitGetBountyGroupsByType()
SUIT_LOOT = suitGetLootNamesCode()
COG_DEPARTMENTS = suitGroupSuitsByDept()
INVASIONABLE_COGS = suitGetInvasionableSuits()
OVERRIDE_SPECIAL_DEATHS = suitGetOverrideDeaths()
DEATH_EXTEND_MOVIE_TIME = suitGetExtendMovieTime()
BOWTIE_SUITS = suitGetBowtieSuits()
NO_TIE_SUITS = suitGetNoTieSuits()
DISALLOWED_SPAWNS = suitGetDisallowedSpawnsNamesCode()


# Randomized hp range for virtuals and skelecogs
SkelecogHpRange = (0.90, 1.10)
VirtualHpRange  = (0.70, 1.10)
SkelecogEffectBlocklist = ('ftf_s', 'ftf_m', 'ftf_l', 'ftf_c', 'ftf_s_rt', 'ftf_s_br', 'ftf_m_cf', 'ftf_c_ac')

# Specialization Enums
NORMAL = 0
DEFENSE = 1
ATTACK = 2

SuitSpecialization2Name = {
    NORMAL: TTLocalizer.SuitAttributeNormal,
    DEFENSE: TTLocalizer.SuitAttributeDefense,
    ATTACK: TTLocalizer.SuitAttributeAttack,
}


HealthRemapping = {
    1488: 1480,
}


def pickFromFreqList(freqList):
    return random.choices(list(range(len(freqList))), weights=freqList)[0]


def calculateHp(data, level, hpMultIndex=0, dnaName=''):
    # HP Boosts and HP related attributes are set in adjustHP function in ClashSuitBaseAI
    if "specialization" in data:
        formula = data["specialization"]
    else:
        formula = NORMAL
    if formula == NORMAL:  # Base formula
        health = (level + 1) * (level + 2)
    elif formula == DEFENSE:  # Defense HP formula
        health = ((level + 2) ** 2) + level
    elif formula == ATTACK:  # Attack HP formula
        health = ((level + 1) ** 2) - level
    else:
        health = (level + 1) * (level + 2)

    # If we have any passive attributes, apply them.
    passives = data.get('passives')
    if passives:
        if passives.get(PassiveAttributeDefs.HP_MULT):
            if type(passives[PassiveAttributeDefs.HP_MULT]) == tuple:
                health = int(math.floor(health * passives[PassiveAttributeDefs.HP_MULT][hpMultIndex]))
            else:
                health = int(math.floor(health * passives[PassiveAttributeDefs.HP_MULT]))
        if passives.get(PassiveAttributeDefs.HP_BOOST):
            health += int(passives[PassiveAttributeDefs.HP_BOOST])

    # Also see if we're forcing HP the based way
    suitDef = SuitDefinitions.get(dnaName, None)
    if suitDef:
        forceHp = suitDef.forceHp
        if forceHp:
            if type(forceHp) is int:
                health = forceHp
            elif type(forceHp) is dict:
                if level in forceHp:
                    health = forceHp[level]

    return health


def calculateDefense(data, level, boost=0):
    if "specialization" in data:
        formula = data["specialization"]
    else:
        formula = NORMAL

    defense = int(level * 5)
    if defense > 65:
        defense = 65
    elif defense <= 0:
        defense = 2
    if formula == DEFENSE:
        boost += 10
    elif formula == ATTACK:
        boost -= 10

    # If we have any passive attributes, apply them.
    passives = data.get('passives')
    forcedDefense = None
    if passives:
        defenseBoost = passives.get(PassiveAttributeDefs.DEFENSE_BOOST, 0)
        forcedDefense = passives.get(PassiveAttributeDefs.FORCED_DEFENSE)
        boost += defenseBoost

    defense += boost
    defense = max(defense, 2)
    if forcedDefense:
        defense = forcedDefense
    return defense


def getFaceoffTaunt(suitName, doId):
    if suitName in SuitFaceoffTaunts:
        taunts = SuitFaceoffTaunts[suitName]
    else:
        taunts = TTLocalizer.SuitFaceoffDefaultTaunts
    return taunts[doId % len(taunts)]


SuitFaceoffTaunts  = TTLocalizer.SuitFaceoffTaunts
SuitGameoverTaunts = TTLocalizer.SuitGameoverTaunts
SuitGameoverTauntIds = TTLocalizer.SuitGameoverTauntIds
SuitSurrenderTauntIds = TTLocalizer.SuitSurrenderTauntIds
