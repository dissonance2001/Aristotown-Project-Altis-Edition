from toontown.toonbase import ToontownBattleGlobals


class IOUDefinition:
    def __init__(self, subtype, gagTrack, uses, boost, npcId, stars, obtainable=1, rewardCooldown=1):
        self.subtype = subtype
        self.gagTrack = gagTrack
        self.uses = uses
        self.boost = boost
        self.npcId = npcId
        self.stars = stars
        self.obtainable = obtainable
        self.rewardCooldown = rewardCooldown

    def getSubtype(self):
        return self.subtype

    def getGagTrack(self):
        return self.gagTrack

    def getUses(self):
        return self.uses

    def getBoost(self):
        return self.boost

    def getNpcId(self):
        return self.npcId

    def getStars(self):
        return self.stars

    def getRewardCooldown(self):
        return self.rewardCooldown


HEAL = ToontownBattleGlobals.HEAL_TRACK
TRAP = ToontownBattleGlobals.TRAP_TRACK
LURE = ToontownBattleGlobals.LURE_TRACK
THROW = ToontownBattleGlobals.THROW_TRACK
SQUIRT = ToontownBattleGlobals.SQUIRT_TRACK
ZAP = ToontownBattleGlobals.ZAP_TRACK
SOUND = ToontownBattleGlobals.SOUND_TRACK
DROP = ToontownBattleGlobals.DROP_TRACK

IOURegistry = {
    1: IOUDefinition(1, HEAL, 3, 25, 2121, 3),
    2: IOUDefinition(2, HEAL, 2, 35, 2132, 4),
    3: IOUDefinition(3, HEAL, 1, 60, 2001, 5),
    11: IOUDefinition(11, TRAP, 3, 65, 1001, 3),
    12: IOUDefinition(12, TRAP, 2, 90, 3007, 4),
    13: IOUDefinition(13, TRAP, 1, 170, 2011, 5),
    21: IOUDefinition(21, LURE, 3, 15, 1323, 3),
    22: IOUDefinition(22, LURE, 2, 18, 2308, 4),
    23: IOUDefinition(23, LURE, 1, 30, 3112, 5),
    31: IOUDefinition(31, THROW, 3, 30, 4108, 3),
    32: IOUDefinition(32, THROW, 2, 40, 2316, 4),
    33: IOUDefinition(33, THROW, 1, 70, 5012, 5),
    34: IOUDefinition(34, THROW, 3, 30, 2314, 3, 0),
    41: IOUDefinition(41, SQUIRT, 3, 25, 1223, 3),
    42: IOUDefinition(42, SQUIRT, 2, 35, 5125, 4),
    43: IOUDefinition(43, SQUIRT, 1, 60, 2217, 5),
    51: IOUDefinition(51, ZAP, 3, 25, 2101, 3),
    52: IOUDefinition(52, ZAP, 2, 35, 1123, 4),
    53: IOUDefinition(53, ZAP, 1, 60, 9203, 5),
    61: IOUDefinition(61, SOUND, 3, 15, 4115, 3),
    62: IOUDefinition(62, SOUND, 2, 20, 4219, 4),
    63: IOUDefinition(63, SOUND, 1, 35, 4119, 5),
    71: IOUDefinition(71, DROP, 3, 35, 4140, 3),
    72: IOUDefinition(72, DROP, 2, 45, 2311, 4),
    73: IOUDefinition(73, DROP, 1, 80, 1116, 5),
    81: IOUDefinition(81, -1, 1, 15, 90001, 3, rewardCooldown=0),
}

NPCIDToIOUSubtype = {}
for subtype, definition in list(IOURegistry.items()):
    NPCIDToIOUSubtype[definition.getNpcId()] = subtype

ObtainableIOUSubtypes = [subtype for subtype, definition in list(IOURegistry.items()) if definition.obtainable]
ObtainableIOUSubtypes.sort()
ObtainableIOUNPCIds = [IOURegistry[subtype].getNpcId() for subtype in ObtainableIOUSubtypes]


def getIOU(subtype):
    return IOURegistry.get(subtype)


def getIOUByNPCId(npcId):
    subtype = NPCIDToIOUSubtype.get(npcId)
    if subtype is None:
        return None
    return IOURegistry.get(subtype)


def getSubtypeByNPCId(npcId):
    return NPCIDToIOUSubtype.get(npcId)


def getConditionName(gagTrack, boost):
    return 'iouBoost_%s_%s' % (gagTrack, boost)


def parseConditionName(condition):
    if not condition.startswith('iouBoost_'):
        return None
    pieces = condition.split('_')
    if len(pieces) != 3:
        return None
    try:
        return int(pieces[1]), int(pieces[2])
    except ValueError:
        return None


def getTrackName(gagTrack):
    if gagTrack == -1:
        return 'ALL GAGS'
    names = ('TOON-UP', 'TRAP', 'LURE', 'THROW', 'SQUIRT', 'ZAP', 'SOUND', 'DROP')
    if 0 <= gagTrack < len(names):
        return names[gagTrack]
    return 'GAGS'


def getBoostTerm(gagTrack):
    if gagTrack == HEAL:
        return 'LAFF'
    if gagTrack == LURE:
        return 'KNOCKBACK DAMAGE'
    return 'DAMAGE'


def getDescription(definition):
    gagTrack = definition.getGagTrack()
    if gagTrack == HEAL:
        term = 'LAFF'
    elif gagTrack == LURE:
        term = 'KNOCKBACK'
    else:
        term = 'DAMAGE'
    return '+%d %s' % (definition.getBoost(), term)
