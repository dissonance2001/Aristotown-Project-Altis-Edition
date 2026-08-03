import weakref
import json
import os

# Custom decorative NPC definitions for Project Altis.
#
# Toon Hall entries use the default area. Outdoor TTC entries set
# area='ttc'. The AI creates each group in the correct zone while the client
# uses the same data for placement, appearance and interaction phrases.

POSITION_MATCH_TOLERANCE = 0.75

BODY_COLOR_SAKAMOREO = (0.298039, 0.298039, 0.349020, 1.0)
BODY_COLOR_BAMPIRE = (0.400000, 0.615686, 0.278431, 1.0)
BODY_COLOR_BOOTS = (1.000000, 0.639216, 0.262745, 1.0)
BODY_COLOR_LARS = (0.000000, 1.000000, 0.498039, 1.0)
BODY_COLOR_CHOMPY = (0.098039, 0.223529, 0.764706, 1.0)
HEAD_COLOR_DETERMINATION = (0.639216, 0.356863, 0.270588, 1.0)
BODY_COLOR_DETERMINATION = (0.980392, 0.945098, 0.588235, 1.0)
BODY_COLOR_FINESSE = (0.349020, 0.305882, 0.494118, 1.0)
LEG_COLOR_FINESSE = (0.298039, 0.298039, 0.349020, 1.0)
BODY_COLOR_SILLY_PEBBLE = (0.949020, 0.592157, 0.674510, 1.0)
BODY_COLOR_NED = (0.266667, 0.309804, 0.678431, 1.0)
BODY_COLOR_MOOSE = (0.513725, 0.203922, 0.560784, 1.0)
BODY_COLOR_NIBBLES_CORAL = (0.832031, 0.500000, 0.296875, 1.0)
BODY_COLOR_SPARKY = (0.560784, 0.454902, 0.392157, 1.0)
BODY_COLOR_DUKE = (0.752941, 0.066667, 0.203922, 1.0)
BODY_COLOR_SPICY_COOKIE = (0.831373, 0.090196, 0.109804, 1.0)
BODY_COLOR_ICONIC = (0.196078, 0.643137, 0.078431, 1.0)
BODY_COLOR_GILBERT = (0.627451, 0.345098, 0.262745, 1.0)
BODY_COLOR_BLINKY = (0.933333, 0.262745, 0.278431, 1.0)
BODY_COLOR_BLUE_DRAGON_MAMORU = (0.090196, 0.619608, 0.949020, 1.0)
BODY_COLOR_INTO_THE_DARKNESS = (0.462745, 0.435294, 0.439216, 1.0)
BODY_COLOR_ERIA = (0.619608, 0.360784, 0.505882, 1.0)
LEG_COLOR_KURO = (0.458824, 0.141176, 0.274510, 1.0)
RYAN_ACCENT_COLOR = (0.250980, 0.203922, 0.454902, 1.0)
LEG_COLOR_SPARKY = (0.949020, 0.760784, 0.823529, 1.0)
HEAD_COLOR_LADY_MARIGOLD = (0.541176, 0.113725, 0.184314, 1.0)
WHITE = (1.0, 1.0, 1.0, 1.0)

_NED_STRIPE_TEXTURE_CACHE = {}
_BLACK_BOTTOM_TEXTURE_CACHE = {}
_NPC_DIALOGUE_SOUND_CACHE = {}


def _findAccessoryPlacementsPath():
    relativePath = os.path.join(
        'resources',
        'phase_14',
        'accessories',
        'accessory_placements.json'
    )
    roots = []

    try:
        currentDirectory = os.path.abspath(os.getcwd())
        while True:
            if currentDirectory not in roots:
                roots.append(currentDirectory)
            parentDirectory = os.path.dirname(currentDirectory)
            if parentDirectory == currentDirectory:
                break
            currentDirectory = parentDirectory
    except:
        pass

    try:
        currentDirectory = os.path.dirname(os.path.abspath(__file__))
        while True:
            if currentDirectory not in roots:
                roots.append(currentDirectory)
            parentDirectory = os.path.dirname(currentDirectory)
            if parentDirectory == currentDirectory:
                break
            currentDirectory = parentDirectory
    except:
        pass

    for root in roots:
        candidate = os.path.join(root, relativePath)
        if os.path.isfile(candidate):
            return candidate

    return None


def _findAccessoryRegistryPath():
    placementPath = _findAccessoryPlacementsPath()
    if not placementPath:
        return None
    return os.path.join(
        os.path.dirname(placementPath),
        'accessories_registry.json'
    )


def _loadCustomAccessoryId(accessoryType, accessoryName, fallbackId=None):
    registryPath = _findAccessoryRegistryPath()
    if not registryPath or not os.path.isfile(registryPath):
        return fallbackId

    try:
        registryFile = open(registryPath, 'r')
        try:
            registry = json.load(registryFile)
        finally:
            registryFile.close()
    except:
        return fallbackId

    wantedName = (accessoryName or '').lower()

    for registryKey, accessoryData in registry.get('accessories', {}).items():
        if not isinstance(accessoryData, dict):
            continue
        if accessoryData.get('type') != accessoryType:
            continue

        candidateNames = [
            accessoryData.get('name'),
            os.path.splitext(os.path.basename(registryKey))[0],
            os.path.basename(accessoryData.get('model', ''))
        ]

        matched = False
        for candidateName in candidateNames:
            if (isinstance(candidateName, basestring) and
                    candidateName.lower() == wantedName):
                matched = True
                break

        if not matched:
            continue

        accessoryId = accessoryData.get('id')
        if not isinstance(accessoryId, int):
            accessoryId = accessoryData.get('native_id')
        if isinstance(accessoryId, int):
            return accessoryId

    return fallbackId


def _loadSavedAccessoryPlacementByName(accessoryType, accessoryName,
                                        placementKeys):
    placementPath = _findAccessoryPlacementsPath()
    if not placementPath:
        return None

    try:
        placementFile = open(placementPath, 'r')
        try:
            placementData = json.load(placementFile)
        finally:
            placementFile.close()
    except:
        return None

    typeData = placementData.get(accessoryType, {})
    if not isinstance(typeData, dict):
        return None

    if isinstance(placementKeys, basestring):
        placementKeys = (placementKeys,)

    # Older editor builds could move the same BAM to a new native ID every
    # time the list refreshed. Search the highest ID first so an already-saved
    # latest placement remains usable after installing the ID-stability fix.
    accessoryIds = list(typeData.keys())
    accessoryIds.sort(
        key=lambda value: int(value) if str(value).isdigit() else -1,
        reverse=True
    )

    wantedName = (accessoryName or '').lower()

    for accessoryId in accessoryIds:
        accessoryData = typeData.get(accessoryId)
        if not isinstance(accessoryData, dict):
            continue

        for placementKey in placementKeys or ():
            entry = accessoryData.get(placementKey)
            if not isinstance(entry, dict):
                continue

            entryName = entry.get('name')
            if (isinstance(entryName, basestring) and
                    entryName.lower() != wantedName):
                continue

            pos = entry.get('pos')
            hpr = entry.get('hpr')
            scale = entry.get('scale')
            if pos is None or hpr is None or scale is None:
                continue

            return (tuple(pos), tuple(hpr), tuple(scale))

    return None


def _loadSavedAccessoryPlacement(accessoryType, accessoryId, placementKeys):
    placementPath = _findAccessoryPlacementsPath()
    if not placementPath:
        return None

    try:
        placementFile = open(placementPath, 'r')
        try:
            placementData = json.load(placementFile)
        finally:
            placementFile.close()
    except:
        return None

    accessoryData = placementData.get(accessoryType, {}).get(
        str(accessoryId),
        {}
    )
    if not isinstance(accessoryData, dict):
        return None

    if isinstance(placementKeys, basestring):
        placementKeys = (placementKeys,)

    for placementKey in placementKeys or ():
        entry = accessoryData.get(placementKey)
        if not isinstance(entry, dict):
            continue

        pos = entry.get('pos')
        hpr = entry.get('hpr')
        scale = entry.get('scale')
        if pos is None or hpr is None or scale is None:
            continue

        return (tuple(pos), tuple(hpr), tuple(scale))

    return None


def _hasAccessoryNodes(npc, attributeName):
    nodes = getattr(npc, attributeName, None)
    if not nodes:
        return False

    for node in nodes:
        try:
            if node and not node.isEmpty():
                return True
        except:
            pass

    return False


# All decorative Toon Hall NPCs share one lightweight distance manager.
# Bodies are never hidden, which avoids visible popping when walking around
# the room. Only expensive animation, look-around and collision work is
# reduced as the local Toon moves away. Nametags stay visible at all ranges.
NPC_OPTIMIZATION_INTERVAL = 0.5
NPC_FULL_DETAIL_DISTANCE = 16.0
NPC_NAMETAG_DISTANCE = 32.0
NPC_LOD_ANIMATION_NEAR_DISTANCE = 12.0
NPC_LOD_ANIMATION_FAR_DISTANCE = 36.0
NPC_LOD_ANIMATION_DELAY = 0.25
NPC_OPTIMIZATION_TASK_NAME = 'toonHallCustomNPCOptimization'

_OPTIMIZED_NPC_REFS = []
_OPTIMIZATION_TASK_RUNNING = False


CUSTOM_NPCS = (
    {
        'slot': 1,
        'npcId': 93001,
        'name': 'Sakamoreo',
        'gender': 'f',
        'dna': (
            'css',
            'md',
            'm',
            'f',
            BODY_COLOR_SAKAMOREO,
            WHITE,
            WHITE,
            BODY_COLOR_SAKAMOREO,
            0,
            0,
            0,
            0,
            72,
            0
        ),
        'pos': (-29.882, -11.826, 0.025),
        'hpr': (-63.952, 0.0, 0.0),
        'backpack': (111, 0, 0),
        'hat': (136, 0, 0),
        'glasses': (50, 0, 0),
        'phrase': 'Ka-pow.',
    },
    {
        'slot': 2,
        'npcId': 93002,
        'name': 'Bampire',
        'gender': 'f',
        'dna': (
            'tss',
            'md',
            's',
            'f',
            BODY_COLOR_BAMPIRE,
            WHITE,
            BODY_COLOR_BAMPIRE,
            BODY_COLOR_BAMPIRE,
            161,
            0,
            152,
            0,
            74,
            0
        ),
        'pos': (-25.713, -17.069, 0.025),
        'hpr': (-53.649, 0.0, 0.0),
        'glasses': (37, 14, 0),
        'hat': (120, 102, 0),
        'backpack': (31, 38, 0),
        'shoes': (3, 57, 0),
        'hideArms': True,
        'hideSleeves': True,
        'hideGloves': True,
        'phrase': 'Happy birthday bestie hope its a great one!! :3',
    },
    {
        'slot': 3,
        'npcId': 93003,
        'name': 'Boots',
        'gender': 'm',
        'dna': (
            'jls',
            'ms',
            'l',
            'm',
            BODY_COLOR_BOOTS,
            WHITE,
            BODY_COLOR_BOOTS,
            BODY_COLOR_BOOTS,
            49,
            27,
            38,
            27,
            7,
            14
        ),
        'pos': (-20.553, -22.204, 0.025),
        'hpr': (-43.098, 0.0, 0.0),
        'hat': (135, 0, 0),
        'backpack': (51, 0, 0),
        'shoes': (3, 30, 0),
        'phrase': 'True, true.',
    },
    {
        'slot': 4,
        'npcId': 93004,
        'name': 'Lars',
        'gender': 'f',
        'dna': (
            'jls',
            'md',
            'l',
            'f',
            BODY_COLOR_LARS,
            WHITE,
            BODY_COLOR_LARS,
            BODY_COLOR_LARS,
            162,
            0,
            153,
            0,
            8,
            8
        ),
        'pos': (-16.098, -26.246, 0.025),
        'hpr': (-31.972, 0.0, 0.0),
        'hat': (10, 0, 0),
        'backpack': (1, 0, 0),
        'glasses': (5, 0, 0),
        'phrase': 'a deer ingame but a goat in and out, happy birthday diss :3',
    },
    {
        'slot': 5,
        'npcId': 93005,
        'name': 'Chompy',
        'gender': 'm',
        'dna': (
            'dls',
            'ls',
            'l',
            'm',
            BODY_COLOR_CHOMPY,
            WHITE,
            BODY_COLOR_CHOMPY,
            BODY_COLOR_CHOMPY,
            163,
            0,
            154,
            0,
            70,
            0
        ),
        'pos': (-11.295, -28.631, 0.025),
        'hpr': (-22.588, 0.0, 0.0),
        'hat': (118, 0, 0),
        'backpack': (85, 0, 0),
        'glasses': (43, 0, 0),
        'shoes': (3, 30, 0),
        'irisColor': (76, 242, 100),
        'phrase': 'happy birthday to thee diss and i wish for ye have a wonderful 1. your stuff is wonderful seeing mate!',
    },
    {
        'slot': 6,
        'npcId': 93006,
        'name': 'Determination',
        'gender': 'm',
        'dna': (
            'cll',
            'ms',
            'm',
            'm',
            BODY_COLOR_DETERMINATION,
            WHITE,
            BODY_COLOR_DETERMINATION,
            HEAD_COLOR_DETERMINATION,
            4,
            4,
            4,
            4,
            0,
            14
        ),
        'pos': (-6.390, -30.627, 0.025),
        'hpr': (-12.362, 0.0, 0.0),
        'hat': (7, 0, 0),
        'backpack': (55, 11, 0),
        'shoes': (3, 30, 0),
        'irisColor': (190, 54, 57),
        'phrase': 'Never give up who you are, if not for yourself, for the people that love you.',
    },
    {
        'slot': 7,
        'npcId': 93007,
        'name': 'Finesse',
        'gender': 'm',
        'dna': (
            'xss',
            'ms',
            'm',
            'm',
            BODY_COLOR_FINESSE,
            WHITE,
            LEG_COLOR_FINESSE,
            BODY_COLOR_FINESSE,
            164,
            0,
            155,
            0,
            72,
            0
        ),
        'pos': (1.731, -29.774, 0.025),
        'hpr': (6.920, 0.0, 0.0),
        'hat': (136, 0, 0),
        'backpack': (73, 0, 0),
        'glasses': (5, 0, 0),
        'irisColor': (196, 41, 73),
        'phrase': "I'm just monkeying with you.",
    },
    {
        'slot': 8,
        'npcId': 93008,
        'name': 'Silly Pebbles',
        'gender': 'f',
        'dna': (
            'kss',
            'ms',
            'm',
            'f',
            BODY_COLOR_SILLY_PEBBLE,
            WHITE,
            BODY_COLOR_SILLY_PEBBLE,
            BODY_COLOR_SILLY_PEBBLE,
            166,
            0,
            157,
            0,
            73,
            0
        ),
        'pos': (7.695, -27.959, 0.025),
        'hpr': (19.320, 0.0, 0.0),
        'hat': (140, 0, 0),
        'backpack': (111, 0, 0),
        'glasses': (53, 0, 0),
        'glassesPlacementKey': 'cs',
        'shoes': (3, 74, 0),
        'boyShorts': (73, 0),
        'hideGloves': True,
        'forceEyelashes': True,
        'speechFontName': 'Comical',
        'speechFontPaths': (
            'phase_3/models/fonts/Comic.ttf',
            'phase_3/fonts/Comic.ttf',
            'phase_3/models/fonts/comic.ttf',
            'phase_3/fonts/comic.ttf',
        ),
        'typewriterSpeech': True,
        'typewriterDelay': 0.5,
        'phrase': 'beep',
    },
    {
        'slot': 9,
        'npcId': 93009,
        'name': 'Ned',
        'gender': 'm',
        'dna': (
            'bss',
            'ms',
            'm',
            'm',
            BODY_COLOR_NED,
            WHITE,
            BODY_COLOR_NED,
            BODY_COLOR_NED,
            4,
            34,
            4,
            34,
            49,
            0
        ),
        'pos': (13.199, -25.583, 0.025),
        'hpr': (32.162, 0.0, 0.0),
        'hat': (10, 0, 0),
        'glasses': (5, 0, 0),
        'shoes': (2, 69, 0),
        'nedStripedShirt': True,
        'phrase': "You've been drafted.",
    },
    {
        'slot': 10,
        'npcId': 93010,
        'name': 'Lady Marigold',
        'gender': 'f',
        'dna': (
            'vss',
            'md',
            'm',
            'f',
            BODY_COLOR_SAKAMOREO,
            WHITE,
            BODY_COLOR_SAKAMOREO,
            HEAD_COLOR_LADY_MARIGOLD,
            167,
            0,
            0,
            0,
            71,
            0
        ),
        'pos': (26.560, -13.474, 0.025),
        'hpr': (72.659, 0.0, 0.0),
        'hat': (39, 25, 0),
        'backpack': (2, 0, 0),
        'glasses': (23, 20, 0),
        'hideArms': True,
        'hideSleeves': True,
        'hideGloves': True,
        'earColor': BODY_COLOR_SAKAMOREO,
        'phrase': "MI OW, happy bday diss, glad to be friends! youre one of the pals thats helped me get to the point im at and i couldnt be thankful enough <33",
    },
    {
        'slot': 11,
        'npcId': 93011,
        'name': 'Moose',
        'gender': 'm',
        'dna': (
            'hsl',
            'ms',
            'm',
            'm',
            BODY_COLOR_MOOSE,
            WHITE,
            BODY_COLOR_MOOSE,
            BODY_COLOR_MOOSE,
            168,
            0,
            159,
            0,
            49,
            0
        ),
        'pos': (27.584, -6.968, 0.025),
        'hpr': (73.956, 0.0, 0.0),
        'hat': (39, 109, 0),
        'backpack': (73, 81, 0),
        'glasses': (40, 0, 0),
        'forceClientGlasses': True,
        'phrase': 'Happy birthday Diss!',
    },
    {
        'slot': 12,
        'npcId': 93012,
        'name': 'Nibbles',
        'gender': 'f',
        'dna': (
            'rss',
            'md',
            's',
            'f',
            BODY_COLOR_NIBBLES_CORAL,
            WHITE,
            BODY_COLOR_NIBBLES_CORAL,
            BODY_COLOR_NIBBLES_CORAL,
            169,
            0,
            160,
            0,
            0,
            15
        ),
        'pos': (27.850, -0.250, 0.025),
        'hpr': (90.000, 0.0, 0.0),
        'hat': (107, 0, 0),
        'bottomColorRGB': (83, 162, 56),
        'phrase': "Happy birthday, Diss! Life isn't what we expected but we're doin' it!",
    },
    {
        'slot': 13,
        'npcId': 93013,
        'name': 'Sparky',
        'gender': 'f',
        'dna': (
            'vss',
            'md',
            's',
            'f',
            BODY_COLOR_SPARKY,
            WHITE,
            LEG_COLOR_SPARKY,
            BODY_COLOR_SPARKY,
            171,
            0,
            162,
            0,
            79,
            0
        ),
        'pos': (27.584, 6.468, 0.025),
        'hpr': (106.044, 0.0, 0.0),
        'hat': (158, 0, 0),
        'backpack': (67, 0, 0),
        # This placement was authored under the editor's cs head key. Apply
        # the saved transform directly so Sparky's fox head does not fall back
        # to the default vs placement.
        'hatPlacement': (
            (0.08832800388336182, -0.09262120723724365, 0.5527229309082031),
            (180.0, 343.3007507324219, 22.014087677001953),
            (0.6499999761581421, 0.6499999761581421, 0.6499999761581421)
        ),
        'earColor': WHITE,
        'irisColor': (255, 0, 255),
        'phrase': 'Happy Birthday Dissonance!',
    },
    {
        'slot': 14,
        'npcId': 93014,
        'name': 'Stellaluna',
        'gender': 'f',
        'dna': (
            'nss',
            'md',
            'm',
            'f',
            BODY_COLOR_SAKAMOREO,
            WHITE,
            BODY_COLOR_SAKAMOREO,
            BODY_COLOR_SAKAMOREO,
            172,
            0,
            163,
            0,
            7,
            31
        ),
        'pos': (27.017, 12.336, 0.025),
        'hpr': (110.811, 0.0, 0.0),
        # Dedicated Halloween bat bow. Model 3 is the classic ribbon bow.
        'hat': (3, 1, 0),
        'forceClientHat': True,
        'backpack': (56, 0, 0),
        'glasses': (19, 0, 0),
        'forceClientGlasses': True,
        # The editor saved gsr1 under cs. Install that exact transform under
        # Stellaluna's real nss head key (ns) before regenerating the glasses.
        'glassesModelName': 'gsr1',
        'glassesPlacementTargetKey': 'ns',
        'glassesPlacement': (
            (0.0, 0.2225337028503418, -0.04465538263320923),
            (180.0, 356.5360107421875, 0.0),
            (0.3540000021457672, 0.2930000126361847, 0.3330000042915344)
        ),
        # Keep skirt texture 7; ClothesColors index 31 supplies the black tint.
        'shoes': (2, 8, 0),
        'phrase': 'HAPPY BIRTHDAY! Thank you for teaching me to OCLO all of those years ago <3',
    },
    {
        'slot': 15,
        'npcId': 93015,
        'name': 'Duke',
        'gender': 'm',
        'dna': (
            'jss',
            'ss',
            's',
            'm',
            BODY_COLOR_DUKE,
            WHITE,
            BODY_COLOR_SAKAMOREO,
            BODY_COLOR_DUKE,
            173,
            0,
            164,
            0,
            73,
            0
        ),
        'pos': (24.682, 17.318, 0.025),
        'hpr': (124.565, 0.0, 0.0),
        'hat': (140, 0, 0),
        'glasses': (56, 0, 0),
        'backpack': (51, 0, 0),
        # swt1 / Wingtips in ToonDNA.
        'shoes': (1, 4, 0),
        'phrase': "Happy Birthday, Diss!! You're the best <3",
    },
    {
        'slot': 16,
        'npcId': 93016,
        'name': 'Spicy Cookie',
        'gender': 'f',
        'dna': (
            'gss',
            'md',
            's',
            'f',
            BODY_COLOR_SPICY_COOKIE,
            WHITE,
            BODY_COLOR_SPICY_COOKIE,
            BODY_COLOR_SPICY_COOKIE,
            156,
            0,
            147,
            0,
            69,
            0
        ),
        'pos': (21.988, 22.042, 0.025),
        'hpr': (134.342, 0.0, 0.0),
        'hat': (120, 113, 0),
        'glasses': (41, 38, 0),
        'backpack': (94, 99, 0),
        'shoes': (2, 70, 0),
        'phrase': "Happy Birthday Diss! You're sweeter than a jellybean!",
    },
    {
        'slot': 17,
        'npcId': 93017,
        'name': 'Iconic',
        'gender': 'm',
        'dna': (
            'css',
            # Use the skirt torso while retaining Iconic's male gender.
            'md',
            'm',
            'm',
            BODY_COLOR_ICONIC,
            WHITE,
            HEAD_COLOR_LADY_MARIGOLD,
            BODY_COLOR_ICONIC,
            158,
            0,
            148,
            0,
            71,
            0
        ),
        'pos': (16.098, 26.246, 0.025),
        'hpr': (148.028, 0.0, 0.0),
        'hat': (156, 0, 0),
        # Force a GirlBottoms skirt texture on this male Toon. Without this,
        # Toon.generateToonClothes uses BoyShorts because Iconic is male.
        'girlSkirt': (71, 0),
        'backpack': (40, 39, 0),
        'glasses': (53, 0, 0),
        'glassesPlacementKey': 'cs',
        'phrase': 'I love you! <3',
    },
    {
        'slot': 18,
        'npcId': 93018,
        'name': 'Gilbert',
        'gender': 'm',
        'dna': (
            'dss',
            'ms',
            'm',
            'm',
            BODY_COLOR_GILBERT,
            WHITE,
            BODY_COLOR_GILBERT,
            BODY_COLOR_GILBERT,
            # Plain shirt. Its actual light-gray colour is applied
            # directly below instead of relying on a palette index.
            0,
            0,
            0,
            0,
            248,
            0
        ),
        'shirtColorRGB': (192, 192, 192),
        'pos': (11.295, 28.631, 0.025),
        'hpr': (157.412, 0.0, 0.0),
        'hat': (93, 221, 0),
        # This hat can arrive before the dog head's attachment nodes exist.
        # Rebuild it client-side after the complete Toon model is available.
        'forceClientHat': True,
        # Reuse Sparky's scarf accessory.
        'backpack': (67, 0, 0),
        'phrase': 'Happy birthday Diss!',
    },
    {
        'slot': 19,
        'npcId': 93019,
        'name': 'Blinky',
        'gender': 'm',
        'dna': (
            'sss',
            'ms',
            's',
            'm',
            BODY_COLOR_BLINKY,
            WHITE,
            BODY_COLOR_BLINKY,
            BODY_COLOR_BLINKY,
            529,
            0,
            505,
            0,
            298,
            0
        ),
        'pos': (5.174, 29.786, 0.025),
        'hpr': (175.140, 0.0, 0.0),
        'hat': (200, 0, 0),
        # The Press Painter hat is loaded directly after the pig head nodes
        # exist. This avoids setHat()/generateHat deleting the only instance
        # during early NPC construction. The editor's canonical custom entry
        # saves under cs on the user's current Toon, so prefer that live value
        # and fall back to an ss value if one is authored later.
        'directCustomHat': True,
        'directCustomHatModel': (
            'phase_14/accessories/cc_m_acc_hat_press_painter'
        ),
        # Resolve the current stable registry ID by BAM name instead of
        # assuming that an older broken editor left it at exactly 200.
        'directCustomHatRegistryName': 'cc_m_acc_hat_press_painter',
        'directCustomHatPlacementKeys': ('cs', 'ss'),
        'directCustomHatPlacementTargetKey': 'ss',
        # Same chair glasses used by Moose. Install the normal pig placement
        # explicitly before generating them because ID 40 only has a custom
        # kangaroo entry in the saved placement table.
        'glasses': (40, 0, 0),
        'forceClientGlasses': True,
        'glassesUseBasePlacement': True,
        'glassesPlacementTargetKey': 'ss',
        'shoes': (1, 71, 0),
        'phrase': 'Happy birthday to you Diss!',
    },
    {
        'slot': 20,
        'npcId': 93020,
        'name': 'Blue Dragon Mamoru',
        'gender': 'm',
        'dna': (
            # Deer head using the long antler set.
            'xls',
            # Tall male torso with shorts.
            'ls',
            'm',
            'm',
            BODY_COLOR_BLUE_DRAGON_MAMORU,
            WHITE,
            BODY_COLOR_BLUE_DRAGON_MAMORU,
            BODY_COLOR_BLUE_DRAGON_MAMORU,
            70,
            0,
            59,
            0,
            159,
            0
        ),
        'pos': (-1.731, 29.774, 0.025),
        'hpr': (-173.080, 0.0, 0.0),
        'hat': (14, 0, 0),
        'backpack': (10, 0, 0),
        'shoes': (3, 44, 0),
        'irisColor': (23, 158, 242),
        'phrase': 'The Jirus will come and drag you into High Roller Bootcamp.',
        # Pass this loaded dialogue directly to setChatAbsolute. A non-None
        # dialogue sound suppresses the normal Toon gibberish voice while the
        # custom phrase still appears in the speech bubble.
        'dialogueSfx': (
            'phase_5/audio/sfx/'
            'cc_s_dlg_ene_hroller_good_morning_clash_general.ogg'
        ),
    },
    {
        'slot': 21,
        'npcId': 93021,
        'name': 'Into The Darkness',
        'gender': 'm',
        'dna': (
            # Normal Koala head. The face/head uses Sakamoreo's body colour;
            # the ears are recoloured separately below.
            'ess',
            'ms',
            'm',
            'm',
            BODY_COLOR_SAKAMOREO,
            WHITE,
            BODY_COLOR_SAKAMOREO,
            BODY_COLOR_INTO_THE_DARKNESS,
            533,
            0,
            509,
            0,
            # Same male shorts texture used by Silly Pebbles.
            73,
            0
        ),
        'pos': (-7.695, 27.959, 0.025),
        'hpr': (-160.680, 0.0, 0.0),
        'hat': (154, 0, 0),
        'backpack': (84, 0, 0),
        'glasses': (40, 0, 0),
        # Use the same client-side glasses generation path as Moose.
        'forceClientGlasses': True,
        # Koala ears use the requested grey while the rest of the head keeps
        # Sakamoreo's body colour.
        'earColor': BODY_COLOR_INTO_THE_DARKNESS,
        'phrase': 'but its wafer thin',
    },
    {
        'slot': 22,
        'npcId': 93022,
        'name': 'Kuro',
        'gender': 'm',
        'dna': (
            # Normal male cat head, medium torso and medium legs.
            'css',
            'ms',
            'm',
            'm',
            # Head and torso/arms use Sakamoreo's body colour.
            BODY_COLOR_SAKAMOREO,
            WHITE,
            # Legs use Kuro's requested dark rose colour.
            LEG_COLOR_KURO,
            BODY_COLOR_SAKAMOREO,
            # Plain shirt and sleeves. Their exact RGB tint is applied below.
            0,
            0,
            0,
            0,
            # Same male shorts used by Silly Pebbles.
            73,
            0
        ),
        'shirtColorRGB': (117, 36, 70),
        'pos': (-13.199, 25.583, 0.025),
        'hpr': (-147.838, 0.0, 0.0),
        # Same backpack as Sakamoreo.
        'backpack': (111, 0, 0),
        # Same Solemn Rose glasses and custom cat placement as Silly Pebbles.
        'glasses': (53, 0, 0),
        'glassesPlacementKey': 'cs',
        'irisColor': (117, 36, 70),
        'phrase': 'My legs hurt from all this business I been standing on.',
    },
    {
        # First decorative NPC placed outdoors in the TTC playground.
        'area': 'ttc',
        'slot': 1,
        'npcId': 93101,
        'name': 'Eria',
        'gender': 'f',
        'dna': (
            'css',
            'md',
            'm',
            'f',
            BODY_COLOR_ERIA,
            WHITE,
            # Same white leg colour used by Sakamoreo.
            WHITE,
            BODY_COLOR_ERIA,
            540,
            0,
            516,
            0,
            63,
            0
        ),
        'pos': (-115.085, -52.020, 0.525),
        'hpr': (-70.042, 0.0, 0.0),
        # Pebbles' Solemn Rose is the primary pair. The cs transform is the
        # exact placement already used by Pebbles and matches Eria's cat head.
        'glasses': (53, 0, 0),
        'forceClientGlasses': True,
        'glassesPlacementKey': 'cs',
        # Duke's glasses are attached as a second independent pair so the
        # primary Rose model is not cleared by Toon.generateGlasses().
        'extraGlasses': ((56, 0, 0),),
        'backpack': (47, 0, 0),
        # Play the Toon wave animation exactly when the player interacts.
        'interactionAnimation': 'wave',
        'phrase': (
            'Happy birthday Diss! Come on get inside, everyone is waiting '
            'for you.'
        ),
    },
    {
        # Second decorative NPC placed outdoors in the TTC playground.
        'area': 'ttc',
        'slot': 2,
        'npcId': 93102,
        'name': 'Ryan',
        'gender': 'm',
        'dna': (
            # Normal cat head, medium male torso and short legs.
            'css',
            'ms',
            's',
            'm',
            # Head and torso/arms use Sakamoreo's body colour.
            BODY_COLOR_SAKAMOREO,
            WHITE,
            # Legs use the requested purple accent.
            RYAN_ACCENT_COLOR,
            BODY_COLOR_SAKAMOREO,
            # Flippy's striped shirt and sleeves. Keep the DNA tint valid
            # and apply extended Toon colour 53 directly below.
            3,
            0,
            3,
            0,
            104,
            0
        ),
        # Extended colour ID 53 from ToonDNA.allColorsList is the requested
        # purple: (0.5764, 0.4392, 0.8588) -> RGB (147, 112, 219).
        # Applying it directly preserves the dark stripe detail in texture 3.
        'shirtColorRGB': (147, 112, 219),
        'pos': (-107.362, -64.419, 0.525),
        'hpr': (-2.811, 0.0, 0.0),
        # Recolour only the cat ears; the rest of the head stays in
        # Sakamoreo's body colour.
        'earColor': RYAN_ACCENT_COLOR,
        'irisColor': (97, 95, 109),
        # Same glasses as Lars.
        'glasses': (5, 0, 0),
        'backpack': (73, 72, 0),
        # Use the full crying emote when the player interacts with Ryan.
        'interactionAnimation': 'cry',
        'phrase': (
            "I'm lazy as fuck and didn't provide a proper screenshot and "
            "a phrase within 3 days so I wasn't invited inside..."
        ),
    },
)


def _createNPCsForArea(air, zoneId, area):
    # Imported lazily to avoid a client-side circular import.
    from toontown.toon import NPCToons

    createdNPCs = []

    for data in CUSTOM_NPCS:
        if data.get('area', 'toonhall') != area:
            continue

        desc = (
            -1,
            data['name'],
            data['dna'],
            data['gender'],
            0,
            NPCToons.NPC_REGULAR
        )

        npc = NPCToons.createNPC(
            air,
            data['npcId'],
            desc,
            zoneId
        )

        backpack = data.get('backpack')
        if backpack:
            npc.b_setBackpack(*backpack)

        hat = data.get('hat')
        if hat:
            npc.b_setHat(*hat)

        glasses = data.get('glasses')
        if glasses:
            npc.b_setGlasses(*glasses)

        shoes = data.get('shoes')
        if shoes:
            npc.b_setShoes(*shoes)

        # Do not send a distributed position update here. NPCToons.createNPC
        # has already generated the object, and a late d_setPosHpr update would
        # overwrite the client-side Toon Hall-relative placement.
        createdNPCs.append(npc)

    return createdNPCs


def createNPCs(air, zoneId):
    # Existing Toon Hall entry point retained for compatibility.
    return _createNPCsForArea(air, zoneId, 'toonhall')


def createTTCNPCs(air, zoneId):
    return _createNPCsForArea(air, zoneId, 'ttc')


def deleteNPCs(npcs):
    for npc in tuple(npcs or ()):
        if npc:
            npc.requestDelete()


def _getClientNPCId(npc):
    # doId is the Astron distributed-object ID, not the NPC definition ID.
    # The previous hotfix checked doId first, so it could never recognise
    # Sakamoreo's custom npcId (93001).
    getter = getattr(npc, 'getNpcId', None)
    if getter:
        try:
            npcId = getter()
            if npcId is not None:
                return npcId
        except:
            pass

    for attribute in ('npcId', 'npc_id'):
        npcId = getattr(npc, attribute, None)
        if npcId is not None:
            return npcId

    return None


def _matchesClientNPC(npc, data):
    npcId = _getClientNPCId(npc)
    if npcId == data['npcId']:
        return True

    # During generation, initToonState can run before setNpcId reaches the
    # client. Fall back to name + matching loaded Toon Hall zone so the Pace
    # Lobby Sakamoreo is never mistaken for this Toon Hall copy.
    try:
        if npc.getName() != data['name']:
            return False

        if data.get('area', 'toonhall') == 'ttc':
            return getattr(npc, 'zoneId', None) == 2000

        return _findLoadedToonHallInterior(npc) is not None
    except:
        return False


def getDataForNPC(npc):
    for data in CUSTOM_NPCS:
        if _matchesClientNPC(npc, data):
            return data
    return None


def isCustomNPC(npc):
    return getDataForNPC(npc) is not None


def playInteractionAnimation(npc):
    data = getDataForNPC(npc)
    if not data:
        return False

    animation = data.get('interactionAnimation')
    if not animation:
        return False

    # Finish an earlier interaction animation cleanly before starting a new
    # one. This prevents stacked wave intervals after repeated clicks.
    previousTrack = getattr(npc, '_customNPCInteractionTrack', None)
    if previousTrack is not None:
        try:
            previousTrack.finish()
        except:
            pass

    try:
        from direct.interval.IntervalGlobal import (
            ActorInterval, Func, Parallel, Sequence
        )

        if animation == 'cry':
            # Match the game's full upset/cry emote: sad face, the reversible
            # bad-putt animation, and the very-sad voice sound.
            crySfx = base.loader.loadSfx(
                'phase_4/audio/sfx/avatar_emotion_very_sad.ogg'
            )

            def playCrySfx():
                base.playSfx(crySfx, node=npc)

            cryAnimation = Sequence(
                ActorInterval(
                    npc,
                    'bad-putt',
                    startFrame=29,
                    endFrame=59,
                    playRate=-0.75
                ),
                ActorInterval(
                    npc,
                    'bad-putt',
                    startFrame=29,
                    endFrame=59,
                    playRate=0.75
                )
            )
            track = Sequence(
                Func(npc.sadEyes),
                Func(npc.blinkEyes),
                Func(npc.showSadMuzzle),
                Parallel(cryAnimation, Func(playCrySfx)),
                Func(npc.hideSadMuzzle),
                Func(npc.normalEyes),
                Func(npc.loop, 'neutral')
            )
        else:
            track = Sequence(
                ActorInterval(npc, animation),
                Func(npc.loop, 'neutral')
            )

        npc._customNPCInteractionTrack = track
        track.start()
        return True
    except:
        # Older Panda builds may fail to construct an ActorInterval while the
        # model is still settling. Keep a visible crying fallback rather than
        # attempting to play a nonexistent animation literally named cry.
        try:
            if animation == 'cry':
                npc.sadEyes()
                npc.blinkEyes()
                npc.showSadMuzzle()
                npc.play('bad-putt')
            else:
                npc.play(animation)
            return True
        except:
            return False


def getPhraseForNPC(npc):
    data = getDataForNPC(npc)
    if data:
        # Apply this immediately before setChatAbsolute is called. This avoids
        # NPC generation or nametag setup replacing the custom speech font.
        _applySpeechFont(npc, data)
        return data.get('phrase')
    return None



def _applyEarColor(npc, data):
    color = data.get('earColor')
    if not color:
        return True

    try:
        red, green, blue, alpha = color
    except:
        return False

    applied = False

    try:
        # Toon head models keep their ears in separate nodes such as
        # ears-short and ears-long. Match the same ear geometry pattern used
        # by the Toon head renderer so the face and muzzle remain unchanged.
        for lodName in npc.getLODNames():
            head = npc.getPart('head', lodName)
            ears = head.findAllMatches('**/ear?*')

            for index in range(ears.getNumPaths()):
                ear = ears.getPath(index)
                if ear.isEmpty():
                    continue

                ear.clearColorScale()
                ear.setColor(red, green, blue, alpha)
                applied = True
    except:
        return False

    return applied


def _applyIrisColor(npc, data):
    color = data.get('irisColor')
    if not color:
        return False

    red = float(color[0]) / 255.0
    green = float(color[1]) / 255.0
    blue = float(color[2]) / 255.0

    patterns = (
        '**/joint_pupilL*',
        '**/joint_pupilR*',
        '**/def_left_pupil*',
        '**/def_right_pupil*'
    )

    applied = False

    for pattern in patterns:
        pupils = npc.findAllMatches(pattern)

        for index in range(pupils.getNumPaths()):
            pupil = pupils.getPath(index)

            if not pupil.isEmpty():
                pupil.setColor(red, green, blue, 1.0)
                applied = True

    return applied


def _applyBoyShorts(npc, data):
    boyShorts = data.get('boyShorts')
    if not boyShorts:
        return False

    try:
        from toontown.toon import ToonDNA
        from panda3d.core import Texture
    except:
        return False

    shortsId = boyShorts[0]
    colorId = boyShorts[1]

    try:
        torsoCode = data['dna'][1]
    except:
        torsoCode = 'ms'

    try:
        if npc.style.torso != torsoCode:
            npc.swapToonTorso(torsoCode, genClothes=0)
    except:
        pass

    try:
        shirtId = data['dna'][8]
        shirtColorId = data['dna'][9]
        sleeveId = data['dna'][10]
        sleeveColorId = data['dna'][11]

        shirtTex = loader.loadTexture(
            ToonDNA.Shirts[shirtId],
            okMissing=True
        )
        sleeveTex = loader.loadTexture(
            ToonDNA.Sleeves[sleeveId],
            okMissing=True
        )
        bottomTex = loader.loadTexture(
            ToonDNA.BoyShorts[shortsId],
            okMissing=True
        )

        if shirtTex:
            shirtTex.setMinfilter(Texture.FTLinearMipmapLinear)
            shirtTex.setMagfilter(Texture.FTLinear)

        if sleeveTex:
            sleeveTex.setMinfilter(Texture.FTLinearMipmapLinear)
            sleeveTex.setMagfilter(Texture.FTLinear)

        if bottomTex:
            bottomTex.setMinfilter(Texture.FTLinearMipmapLinear)
            bottomTex.setMagfilter(Texture.FTLinear)

        shirtColor = ToonDNA.ClothesColors[shirtColorId]
        sleeveColor = ToonDNA.ClothesColors[sleeveColorId]
        bottomColor = ToonDNA.ClothesColors[colorId]

        darkBottomColor = bottomColor * 0.5
        darkBottomColor.setW(1.0)

        for lodName in npc.getLODNames():
            torso = npc.getPart('torso', lodName)

            top = torso.find('**/torso-top')
            if not top.isEmpty() and shirtTex:
                top.setTexture(shirtTex, 1)
                top.setColor(shirtColor)

            sleeves = torso.find('**/sleeves')
            if not sleeves.isEmpty() and sleeveTex:
                sleeves.setTexture(sleeveTex, 1)
                sleeves.setColor(sleeveColor)

            bottoms = torso.findAllMatches('**/torso-bot')
            for index in range(bottoms.getNumPaths()):
                bottom = bottoms.getPath(index)
                if bottomTex:
                    bottom.setTexture(bottomTex, 1)
                bottom.setColor(bottomColor)

            caps = torso.findAllMatches('**/torso-bot-cap')
            caps.setColor(darkBottomColor)

        return True
    except:
        return False




def _applyGirlSkirt(npc, data):
    girlSkirt = data.get('girlSkirt')
    if not girlSkirt:
        return False

    try:
        from toontown.toon import ToonDNA
        from panda3d.core import Texture
    except:
        return False

    skirtId = girlSkirt[0]
    colorId = girlSkirt[1]

    try:
        torsoCode = data['dna'][1]
    except:
        torsoCode = 'md'

    # A male Toon normally loads BoyShorts regardless of the torso mesh.
    # Keep Iconic male while explicitly using the medium skirt torso/model.
    try:
        if npc.style.torso != torsoCode:
            npc.swapToonTorso(torsoCode, genClothes=0)
    except:
        pass

    try:
        shirtId = data['dna'][8]
        shirtColorId = data['dna'][9]
        sleeveId = data['dna'][10]
        sleeveColorId = data['dna'][11]

        shirtTex = loader.loadTexture(
            ToonDNA.Shirts[shirtId],
            okMissing=True
        )
        sleeveTex = loader.loadTexture(
            ToonDNA.Sleeves[sleeveId],
            okMissing=True
        )
        skirtTex = loader.loadTexture(
            ToonDNA.GirlBottoms[skirtId][0],
            okMissing=True
        )

        if shirtTex:
            shirtTex.setMinfilter(Texture.FTLinearMipmapLinear)
            shirtTex.setMagfilter(Texture.FTLinear)

        if sleeveTex:
            sleeveTex.setMinfilter(Texture.FTLinearMipmapLinear)
            sleeveTex.setMagfilter(Texture.FTLinear)

        if skirtTex:
            skirtTex.setMinfilter(Texture.FTLinearMipmapLinear)
            skirtTex.setMagfilter(Texture.FTLinear)

        shirtColor = ToonDNA.ClothesColors[shirtColorId]
        sleeveColor = ToonDNA.ClothesColors[sleeveColorId]
        skirtColor = ToonDNA.ClothesColors[colorId]

        darkSkirtColor = skirtColor * 0.5
        darkSkirtColor.setW(1.0)

        for lodName in npc.getLODNames():
            torso = npc.getPart('torso', lodName)

            top = torso.find('**/torso-top')
            if not top.isEmpty() and shirtTex:
                top.setTexture(shirtTex, 1)
                top.setColor(shirtColor)

            sleeves = torso.find('**/sleeves')
            if not sleeves.isEmpty() and sleeveTex:
                sleeves.setTexture(sleeveTex, 1)
                sleeves.setColor(sleeveColor)

            bottoms = torso.findAllMatches('**/torso-bot')
            for index in range(bottoms.getNumPaths()):
                bottom = bottoms.getPath(index)
                if skirtTex:
                    bottom.setTexture(skirtTex, 1)
                bottom.setColor(skirtColor)

            caps = torso.findAllMatches('**/torso-bot-cap')
            for index in range(caps.getNumPaths()):
                caps.getPath(index).setColor(darkSkirtColor)

        return True
    except:
        return False


def _applyCustomShirtColor(npc, data):
    color = data.get('shirtColorRGB')
    if not color:
        return True

    try:
        red = float(color[0]) / 255.0
        green = float(color[1]) / 255.0
        blue = float(color[2]) / 255.0

        applied = False
        for lodName in npc.getLODNames():
            torso = npc.getPart('torso', lodName)

            top = torso.find('**/torso-top')
            if not top.isEmpty():
                top.clearColorScale()
                top.setColor(red, green, blue, 1.0)
                applied = True

            sleeves = torso.find('**/sleeves')
            if not sleeves.isEmpty():
                sleeves.clearColorScale()
                sleeves.setColor(red, green, blue, 1.0)
                applied = True

        return applied
    except:
        return False


def _applyCustomBottomColor(npc, data):
    color = data.get('bottomColorRGB')
    if not color:
        return True

    try:
        red = float(color[0]) / 255.0
        green = float(color[1]) / 255.0
        blue = float(color[2]) / 255.0

        applied = False
        for lodName in npc.getLODNames():
            torso = npc.getPart('torso', lodName)
            bottoms = torso.findAllMatches('**/torso-bot')

            for index in range(bottoms.getNumPaths()):
                bottom = bottoms.getPath(index)
                bottom.clearColorScale()
                bottom.setColor(red, green, blue, 1.0)
                applied = True

        return applied
    except:
        return False



def _makeBlackBottomTexture(texturePath):
    cached = _BLACK_BOTTOM_TEXTURE_CACHE.get(texturePath)
    if cached:
        return cached

    try:
        from panda3d.core import Filename, PNMImage, Texture
        sourceTexture = loader.loadTexture(texturePath, okMissing=True)
    except:
        return None

    if not sourceTexture:
        return None

    sourceImage = PNMImage()
    stored = False
    try:
        stored = sourceTexture.store(sourceImage)
    except:
        pass
    if not stored:
        try:
            stored = sourceImage.read(Filename(texturePath))
        except:
            stored = False
    if not stored:
        return None

    width = sourceImage.getXSize()
    height = sourceImage.getYSize()
    hasAlpha = sourceImage.hasAlpha()
    output = PNMImage(width, height, 4 if hasAlpha else 3)

    # Keep the original skirt pattern and its highlights, but remap all colour
    # into a narrow black/charcoal range. This reads as black in game without
    # multiplying every texel to zero and destroying the visible pattern.
    for y in range(height):
        for x in range(width):
            red = sourceImage.getRed(x, y)
            green = sourceImage.getGreen(x, y)
            blue = sourceImage.getBlue(x, y)
            luminance = red * 0.299 + green * 0.587 + blue * 0.114
            value = 0.015 + luminance * 0.18
            if value > 0.20:
                value = 0.20
            output.setXel(x, y, value, value, value)
            if hasAlpha:
                output.setAlpha(x, y, sourceImage.getAlpha(x, y))

    texture = Texture(
        'toonHall-black-bottom-%s' % len(_BLACK_BOTTOM_TEXTURE_CACHE)
    )
    try:
        if not texture.load(output):
            return None
    except:
        return None

    texture.setMinfilter(Texture.FTLinearMipmapLinear)
    texture.setMagfilter(Texture.FTLinear)
    _BLACK_BOTTOM_TEXTURE_CACHE[texturePath] = texture
    return texture


def _applyBlackBottomPattern(npc, data):
    if not data.get('blackBottomPattern'):
        return True

    try:
        from toontown.toon import ToonDNA
        textureId = data['dna'][12]
        texture = _makeBlackBottomTexture(ToonDNA.GirlBottoms[textureId])
    except:
        return False

    if not texture:
        return False

    applied = False
    try:
        for lodName in npc.getLODNames():
            torso = npc.getPart('torso', lodName)
            bottoms = torso.findAllMatches('**/torso-bot')

            for index in range(bottoms.getNumPaths()):
                bottom = bottoms.getPath(index)
                bottom.setTexture(texture, 1)
                bottom.clearColorScale()
                bottom.setColor(1.0, 1.0, 1.0, 1.0)
                applied = True

            caps = torso.findAllMatches('**/torso-bot-cap')
            for index in range(caps.getNumPaths()):
                cap = caps.getPath(index)
                cap.clearColorScale()
                cap.setColor(0.025, 0.025, 0.025, 1.0)
    except:
        return False

    return applied


def _makeNedStripeTexture(texturePath):
    cached = _NED_STRIPE_TEXTURE_CACHE.get(texturePath)
    if cached:
        return cached

    try:
        from panda3d.core import Filename, PNMImage, Texture
        sourceTexture = loader.loadTexture(texturePath, okMissing=True)
    except:
        return None

    if not sourceTexture:
        return None

    sourceImage = PNMImage()
    stored = False
    try:
        stored = sourceTexture.store(sourceImage)
    except:
        pass
    if not stored:
        try:
            stored = sourceImage.read(Filename(texturePath))
        except:
            stored = False
    if not stored:
        return None

    width = sourceImage.getXSize()
    height = sourceImage.getYSize()
    hasAlpha = sourceImage.hasAlpha()
    output = PNMImage(width, height, 4 if hasAlpha else 3)

    # Shirt 4's source texture uses cyan and yellow horizontal stripes.
    # Keep that exact pattern and UV layout, changing only the two colours:
    # cyan -> Ned red, yellow -> Ned mauve.
    mauve = (107.0 / 255.0, 61.0 / 255.0, 84.0 / 255.0)
    red = (250.0 / 255.0, 59.0 / 255.0, 41.0 / 255.0)

    for y in range(height):
        for x in range(width):
            sourceRed = sourceImage.getRed(x, y)
            sourceBlue = sourceImage.getBlue(x, y)

            # Strong source colours become exact requested colours. Only the
            # anti-aliased boundary is softly blended to preserve clean edges.
            blend = 0.5 + (sourceBlue - sourceRed) * 4.0
            if blend < 0.0:
                blend = 0.0
            elif blend > 1.0:
                blend = 1.0

            outRed = mauve[0] + (red[0] - mauve[0]) * blend
            outGreen = mauve[1] + (red[1] - mauve[1]) * blend
            outBlue = mauve[2] + (red[2] - mauve[2]) * blend
            output.setXel(x, y, outRed, outGreen, outBlue)
            if hasAlpha:
                output.setAlpha(x, y, sourceImage.getAlpha(x, y))

    texture = Texture('toonHall-ned-stripes-%s' % len(_NED_STRIPE_TEXTURE_CACHE))
    try:
        if not texture.load(output):
            return None
    except:
        return None

    texture.setMinfilter(Texture.FTLinearMipmapLinear)
    texture.setMagfilter(Texture.FTLinear)
    _NED_STRIPE_TEXTURE_CACHE[texturePath] = texture
    return texture


def _applyNedStripedShirt(npc, data):
    if not data.get('nedStripedShirt'):
        return True

    try:
        from toontown.toon import ToonDNA
        shirtTexture = _makeNedStripeTexture(ToonDNA.Shirts[4])
        sleeveTexture = _makeNedStripeTexture(ToonDNA.Sleeves[4])
    except:
        return False

    if not shirtTexture or not sleeveTexture:
        return False

    applied = False
    try:
        for lodName in npc.getLODNames():
            torso = npc.getPart('torso', lodName)
            top = torso.find('**/torso-top')
            sleeves = torso.find('**/sleeves')

            if not top.isEmpty():
                top.setTexture(shirtTexture, 1)
                top.clearColorScale()
                top.setColor(1.0, 1.0, 1.0, 1.0)
                applied = True

            if not sleeves.isEmpty():
                sleeves.setTexture(sleeveTexture, 1)
                sleeves.clearColorScale()
                sleeves.setColor(1.0, 1.0, 1.0, 1.0)
                applied = True
    except:
        return False

    return applied


def _applyVisibleEyelashes(npc, data, rebuild=False):
    if not data.get('forceEyelashes'):
        return True

    try:
        if rebuild:
            style = getattr(npc, 'style', None)

            if style:
                originalHead = style.head

                try:
                    # ToonHead.setupEyelashes selects the long eyelash model
                    # whenever the second head-code character is "l".
                    # Temporarily use kls for the eyelash rebuild, then restore
                    # Silly Pebbles' real kss head so her head shape is unchanged.
                    style.head = (
                        originalHead[0] +
                        'l' +
                        originalHead[2:]
                    )
                    npc.setupEyelashes(style)
                finally:
                    style.head = originalHead

        npc.showEyelashes()
        return True
    except:
        return False


def _getDirectCustomHatAccessoryId(data):
    hat = data.get('hat')
    fallbackId = hat[0] if hat else None
    registryName = data.get('directCustomHatRegistryName')

    if registryName:
        return _loadCustomAccessoryId('hat', registryName, fallbackId)

    return fallbackId


def _getDirectCustomHatPlacement(npc, data):
    hat = data.get('hat')
    if not hat:
        return None

    placementKeys = data.get('directCustomHatPlacementKeys')
    if not placementKeys:
        placementKeys = ('cs', 'ss')

    accessoryId = _getDirectCustomHatAccessoryId(data)
    if accessoryId is not None:
        placement = _loadSavedAccessoryPlacement(
            'hat',
            accessoryId,
            placementKeys
        )
        if placement:
            return placement

    # Preserve a placement saved under ID 200 before the registry bug moved
    # the BAM, then search old shifted IDs by accessory name as a final bridge.
    if accessoryId != hat[0]:
        placement = _loadSavedAccessoryPlacement(
            'hat',
            hat[0],
            placementKeys
        )
        if placement:
            return placement

    registryName = data.get('directCustomHatRegistryName')
    if registryName:
        placement = _loadSavedAccessoryPlacementByName(
            'hat',
            registryName,
            placementKeys
        )
        if placement:
            return placement

    targetKey = data.get('directCustomHatPlacementTargetKey')
    if not targetKey:
        try:
            targetKey = npc.style.head[:2]
        except:
            targetKey = None

    if targetKey:
        try:
            from toontown.toon import AccessoryGlobals
            return AccessoryGlobals.HatTransTable.get(targetKey)
        except:
            pass

    return None


def _loadDirectCustomHatModel(modelPath):
    if not modelPath:
        return None

    candidates = [modelPath]
    normalized = modelPath.replace('\\', '/')

    if normalized.startswith('resources/'):
        normalized = normalized[len('resources/'):]
    else:
        candidates.append('resources/' + normalized)

    relativeResourcePath = os.path.join('resources', normalized)
    roots = []

    try:
        currentDirectory = os.path.abspath(os.getcwd())
        while True:
            if currentDirectory not in roots:
                roots.append(currentDirectory)
            parentDirectory = os.path.dirname(currentDirectory)
            if parentDirectory == currentDirectory:
                break
            currentDirectory = parentDirectory
    except:
        pass

    try:
        currentDirectory = os.path.dirname(os.path.abspath(__file__))
        while True:
            if currentDirectory not in roots:
                roots.append(currentDirectory)
            parentDirectory = os.path.dirname(currentDirectory)
            if parentDirectory == currentDirectory:
                break
            currentDirectory = parentDirectory
    except:
        pass

    for root in roots:
        candidate = os.path.join(root, relativeResourcePath)
        if candidate not in candidates:
            candidates.append(candidate)

    for candidate in candidates:
        try:
            geom = loader.loadModel(candidate, okMissing=True)
        except:
            geom = None

        try:
            if geom and not geom.isEmpty():
                return geom
        except:
            pass

    return None


def _isDirectCustomHatNode(node):
    try:
        return (
            node and
            not node.isEmpty() and
            node.getName() == 'toonHallDirectCustomHatNode'
        )
    except:
        return False


def _applyDirectCustomHatPlacement(npc, data):
    placement = _getDirectCustomHatPlacement(npc, data)
    if not placement:
        return False

    hatNodes = getattr(npc, 'hatNodes', None)
    if not hatNodes:
        return False

    applied = False

    for hatNode in hatNodes:
        if not _isDirectCustomHatNode(hatNode):
            continue

        try:
            children = hatNode.getChildren()
            for child in children:
                child.setPos(*placement[0])
                child.setHpr(*placement[1])
                child.setScale(*placement[2])
                applied = True
        except:
            pass

    return applied


def _installDirectCustomHat(npc, data):
    if not data.get('directCustomHat'):
        return False

    hat = data.get('hat')
    modelPath = data.get('directCustomHatModel')
    placement = _getDirectCustomHatPlacement(npc, data)

    if not hat or not modelPath or not placement:
        return False

    try:
        headNodes = npc.findAllMatches('**/__Actor_head')
        if not headNodes or headNodes.getNumPaths() == 0:
            return False
    except:
        return False

    # Keep a correctly installed direct model and only refresh its transform.
    # If a later distributed accessory update replaced it, rebuild one clean
    # tracked set instead of stacking another instance on top.
    existingNodes = getattr(npc, 'hatNodes', None) or []
    for existingNode in existingNodes:
        if _isDirectCustomHatNode(existingNode):
            return _applyDirectCustomHatPlacement(npc, data)

    for existingNode in existingNodes:
        try:
            if existingNode and not existingNode.isEmpty():
                existingNode.removeNode()
        except:
            pass

    npc.hatNodes = []

    geom = _loadDirectCustomHatModel(modelPath)
    if geom is None:
        return False

    try:
        geom.unstash()
        geom.show()
        for child in geom.findAllMatches('**'):
            child.unstash()
            child.show()
    except:
        pass

    try:
        geom.setPos(*placement[0])
        geom.setHpr(*placement[1])
        geom.setScale(*placement[2])
    except:
        return False

    try:
        accessoryId = _getDirectCustomHatAccessoryId(data)
        if accessoryId is None:
            accessoryId = hat[0]
        npc.hat = (accessoryId, hat[1], hat[2])
    except:
        pass

    installed = False

    try:
        for index in range(headNodes.getNumPaths()):
            headNode = headNodes.getPath(index)
            accessoryNode = headNode.attachNewNode(
                'toonHallDirectCustomHatNode'
            )
            geom.instanceTo(accessoryNode)
            npc.hatNodes.append(accessoryNode)
            installed = True
    except:
        return False

    return installed


def _applyConfiguredHat(npc, data):
    if data.get('directCustomHat'):
        return _installDirectCustomHat(npc, data)

    if not data.get('forceClientHat'):
        return True

    hat = data.get('hat')
    if not hat:
        return True

    placement = data.get('hatPlacement')
    targetKey = data.get('hatPlacementTargetKey')

    if not targetKey:
        try:
            targetKey = npc.style.head[:2]
        except:
            targetKey = None

    if data.get('hatPlacementFromFile'):
        sourceKeys = data.get('hatPlacementSourceKeys')
        if not sourceKeys:
            sourceKeys = (targetKey,)
        savedPlacement = _loadSavedAccessoryPlacement(
            'hat',
            hat[0],
            sourceKeys
        )
        if savedPlacement:
            placement = savedPlacement

    if placement and targetKey:
        try:
            from toontown.toon import AccessoryGlobals
            accessoryId = hat[0]
            table = AccessoryGlobals.ExtendedHatTransTable
            if accessoryId not in table:
                table[accessoryId] = {}
            table[accessoryId][targetKey] = placement
        except:
            pass

    # setHat already performs one complete regeneration. Calling generateHat
    # again here creates another custom model instance in this Altis loader.
    try:
        npc.setHat(hat[0], hat[1], hat[2])
    except:
        try:
            npc.hat = hat
            npc.generateHat()
        except:
            return False

    return _hasAccessoryNodes(npc, 'hatNodes')

def _applyConfiguredGlasses(npc, data):
    if not data.get('forceClientGlasses'):
        return True

    glasses = data.get('glasses')
    if not glasses:
        return True

    placement = data.get('glassesPlacement')
    targetKey = data.get('glassesPlacementTargetKey')

    if not targetKey:
        try:
            targetKey = npc.style.head[:2]
        except:
            targetKey = None

    if data.get('glassesUseBasePlacement') and targetKey:
        try:
            from toontown.toon import AccessoryGlobals
            placement = AccessoryGlobals.GlassesTransTable.get(targetKey)
        except:
            placement = None

    if placement and targetKey:
        try:
            from toontown.toon import AccessoryGlobals
            accessoryId = glasses[0]
            table = AccessoryGlobals.ExtendedGlassesTransTable
            if accessoryId not in table:
                table[accessoryId] = {}
            table[accessoryId][targetKey] = placement
        except:
            pass

    # setGlasses already regenerates the accessory. Do not call
    # generateGlasses a second time.
    try:
        npc.setGlasses(glasses[0], glasses[1], glasses[2])
    except:
        try:
            npc.glasses = glasses
            npc.generateGlasses()
        except:
            return False

    return _hasAccessoryNodes(npc, 'glassesNodes')

def _applyHatPlacement(npc, data):
    placement = data.get('hatPlacement')
    hat = data.get('hat')

    if not placement or not hat:
        return True

    hatNodes = getattr(npc, 'hatNodes', None)
    if not hatNodes:
        return False

    applied = False

    for hatNode in hatNodes:
        try:
            children = hatNode.getChildren()

            for child in children:
                child.setPos(
                    placement[0][0],
                    placement[0][1],
                    placement[0][2]
                )
                child.setHpr(
                    placement[1][0],
                    placement[1][1],
                    placement[1][2]
                )
                child.setScale(
                    placement[2][0],
                    placement[2][1],
                    placement[2][2]
                )
                applied = True
        except:
            pass

    # Some custom accessory loaders wrap or instance the BAM beneath another
    # node. Apply the same saved transform to its named model root as a fallback.
    modelName = data.get('hatModelName')
    if modelName:
        try:
            modelNodes = npc.findAllMatches('**/%s*' % modelName)
            for index in range(modelNodes.getNumPaths()):
                modelNode = modelNodes.getPath(index)
                modelNode.setPos(*placement[0])
                modelNode.setHpr(*placement[1])
                modelNode.setScale(*placement[2])
                applied = True
        except:
            pass

    return applied


def _retryHatPlacement(npc, data, task):
    retries = getattr(task, 'npcHatPlacementRetries', 0) + 1
    task.npcHatPlacementRetries = retries

    if data.get('directCustomHat'):
        # Continue briefly through the distributed loading window. Installing
        # is idempotent: it keeps one tracked hat and only reapplies the latest
        # editor placement unless another update replaced the node.
        _installDirectCustomHat(npc, data)
        _applyDirectCustomHatPlacement(npc, data)

        if retries >= 20:
            return task.done
        return task.again

    # Regenerate only while no live hat node exists. Repeated generation of a
    # custom hat can leave duplicate model instances behind.
    if (data.get('forceClientHat') and
            not _hasAccessoryNodes(npc, 'hatNodes')):
        _applyConfiguredHat(npc, data)

    if data.get('hatPlacement'):
        _applyHatPlacement(npc, data)

    if _hasAccessoryNodes(npc, 'hatNodes') or retries >= 12:
        return task.done

    return task.again


def _applyGlassesPlacement(npc, data):
    placement = data.get('glassesPlacement')
    placementKey = data.get('glassesPlacementKey')
    glasses = data.get('glasses')

    if not glasses:
        return True

    # NPC-specific direct placements take priority. This supports placements
    # authored on a different preview head key in the accessory editor.
    if not placement and placementKey:
        try:
            from toontown.toon import AccessoryGlobals
            accessoryId = glasses[0]
            placement = AccessoryGlobals.ExtendedGlassesTransTable.get(
                accessoryId,
                {}
            ).get(placementKey)
        except:
            placement = None

    if not placement:
        return not placementKey and not data.get('glassesPlacement')

    glassesNodes = getattr(npc, 'glassesNodes', None)
    if not glassesNodes:
        return False

    applied = False

    for glassesNode in glassesNodes:
        try:
            children = glassesNode.getChildren()

            for child in children:
                child.setPos(
                    placement[0][0],
                    placement[0][1],
                    placement[0][2]
                )
                child.setHpr(
                    placement[1][0],
                    placement[1][1],
                    placement[1][2]
                )
                child.setScale(
                    placement[2][0],
                    placement[2][1],
                    placement[2][2]
                )
                applied = True
        except:
            pass

    # gsr1 is the model name stored by the placement editor. Apply the same
    # transform to a named model root too, in case this Altis build wraps the
    # accessory beneath an extra attachment node.
    modelName = data.get('glassesModelName')
    if modelName:
        try:
            modelNodes = npc.findAllMatches('**/%s*' % modelName)
            for index in range(modelNodes.getNumPaths()):
                modelNode = modelNodes.getPath(index)
                modelNode.setPos(*placement[0])
                modelNode.setHpr(*placement[1])
                modelNode.setScale(*placement[2])
                applied = True
        except:
            pass

    return applied


def _retryGlassesPlacement(npc, data, task):
    # If the distributed glasses update arrived before the head attachment
    # nodes existed, regenerate only while the NPC still has no glasses nodes.
    if (data.get('forceClientGlasses') and
            not _hasAccessoryNodes(npc, 'glassesNodes')):
        _applyConfiguredGlasses(npc, data)

    _applyGlassesPlacement(npc, data)
    _applyExtraGlasses(npc, data)
    _applyVisibleEyelashes(npc, data)

    retries = getattr(task, 'npcPlacementRetries', 0) + 1
    task.npcPlacementRetries = retries

    # Accessory generation can finish a few frames after initToonState. Keep
    # reapplying briefly so a late gsr1 rebuild cannot restore default ns.
    if retries >= 12:
        return task.done

    return task.again



def _hasLiveNodeList(nodes):
    if not nodes:
        return False

    for node in nodes:
        try:
            if node and not node.isEmpty():
                return True
        except:
            pass

    return False


def _clearExtraGlasses(npc):
    nodes = getattr(npc, '_toonHallExtraGlassesNodes', None)
    if nodes:
        for node in nodes:
            try:
                if node and not node.isEmpty():
                    node.removeNode()
            except:
                pass

    npc._toonHallExtraGlassesNodes = []
    npc._toonHallExtraGlassesSignature = None


def _getExtraGlassesPlacement(npc, accessoryId, placementKey=None):
    try:
        headKey = npc.style.head[:2]
    except:
        return None

    keys = []
    if placementKey:
        keys.append(placementKey)
    if headKey not in keys:
        keys.append(headKey)

    # Prefer a placement saved by the editor, then the extended/static tables.
    placement = _loadSavedAccessoryPlacement(
        'glasses',
        accessoryId,
        tuple(keys)
    )
    if placement:
        return placement

    try:
        from toontown.toon import AccessoryGlobals

        extended = AccessoryGlobals.ExtendedGlassesTransTable.get(
            accessoryId,
            {}
        )
        for key in keys:
            placement = extended.get(key)
            if placement:
                return placement

        return AccessoryGlobals.GlassesTransTable.get(headKey)
    except:
        return None


def _applyExtraGlasses(npc, data):
    extraGlasses = data.get('extraGlasses')
    if not extraGlasses:
        return True

    try:
        signature = tuple(tuple(item[:3]) for item in extraGlasses)
    except:
        return False

    existingNodes = getattr(npc, '_toonHallExtraGlassesNodes', None)
    if (getattr(npc, '_toonHallExtraGlassesSignature', None) == signature and
            _hasLiveNodeList(existingNodes)):
        return True

    try:
        from toontown.toon import ToonDNA
        from panda3d.core import Texture
    except:
        return False

    headNodes = npc.findAllMatches('**/__Actor_head')
    if headNodes.getNumPaths() == 0:
        return False

    _clearExtraGlasses(npc)
    createdNodes = []

    placementKeys = data.get('extraGlassesPlacementKeys', ())

    for index in range(len(extraGlasses)):
        glasses = extraGlasses[index]
        try:
            accessoryId = int(glasses[0])
            textureId = int(glasses[1])
            colorId = int(glasses[2])
        except:
            continue

        if (accessoryId <= 0 or
                accessoryId >= len(ToonDNA.GlassesModels)):
            continue

        modelPath = ToonDNA.GlassesModels[accessoryId]
        if not modelPath:
            continue

        glassesGeom = loader.loadModel(modelPath, okMissing=True)
        if not glassesGeom:
            continue

        if textureId != 0:
            try:
                texturePath = ToonDNA.GlassesTextures[textureId]
                texture = loader.loadTexture(texturePath, okMissing=True)
                if texture:
                    texture.setMinfilter(Texture.FTLinearMipmapLinear)
                    texture.setMagfilter(Texture.FTLinear)
                    glassesGeom.setTexture(texture, 1)
            except:
                pass

        placementKey = None
        try:
            placementKey = placementKeys[index]
        except:
            pass

        placement = _getExtraGlassesPlacement(
            npc,
            accessoryId,
            placementKey
        )
        if not placement:
            continue

        glassesGeom.setPos(*placement[0])
        glassesGeom.setHpr(*placement[1])
        glassesGeom.setScale(*placement[2])

        for headIndex in range(headNodes.getNumPaths()):
            headNode = headNodes.getPath(headIndex)
            extraNode = headNode.attachNewNode('extraGlassesNode')
            glassesGeom.instanceTo(extraNode)
            createdNodes.append(extraNode)

    if not createdNodes:
        return False

    npc._toonHallExtraGlassesNodes = createdNodes
    npc._toonHallExtraGlassesSignature = signature
    return True

def _applyHiddenGloves(npc, data):
    hideArms = data.get('hideArms')
    hideSleeves = data.get('hideSleeves')
    hideGloves = data.get('hideGloves')

    if not (hideArms or hideSleeves or hideGloves):
        return True

    hidden = False

    try:
        for lodName in npc.getLODNames():
            torso = npc.getPart('torso', lodName)

            if hideArms:
                arms = torso.find('**/arms')
                if not arms.isEmpty():
                    arms.hide()
                    hidden = True

            if hideSleeves:
                sleeves = torso.find('**/sleeves')
                if not sleeves.isEmpty():
                    sleeves.hide()
                    hidden = True

            if hideGloves:
                hands = torso.find('**/hands')
                if not hands.isEmpty():
                    hands.hide()
                    hidden = True
    except:
        pass

    return hidden


def _loadSpeechFont(data):
    cachedFont = data.get('_loadedSpeechFont')
    if cachedFont:
        return cachedFont

    requestedName = data.get('speechFontName')
    if not requestedName:
        return None

    requestedNameLower = requestedName.lower()
    font = None
    loadedFrom = None

    # First use the localized registered font list by its visible name. The
    # item enum number is not guaranteed to match this list's index.
    try:
        from toontown.toonbase import TTLocalizer

        fontNames = getattr(TTLocalizer, 'NametagFontNames', ())
        fontPaths = getattr(TTLocalizer, 'NametagFonts', ())

        for index in range(min(len(fontNames), len(fontPaths))):
            fontName = str(fontNames[index]).lower()

            if (fontName == requestedNameLower or
                    requestedNameLower in fontName or
                    'comic' in fontName):
                fontPath = fontPaths[index]
                font = loader.loadFont(fontPath, lineHeight=1.0)
                loadedFrom = fontPath
                break
    except:
        font = None

    # Also inspect fonts already registered in ToontownGlobals. This supports
    # installations where Comical was added without a matching localizer name.
    if not font:
        try:
            from toontown.toonbase import ToontownGlobals

            registeredPaths = getattr(
                ToontownGlobals,
                'NametagFontPaths',
                {}
            )

            for index, fontPath in registeredPaths.items():
                fontPathText = str(fontPath).lower()

                if 'comic' in fontPathText:
                    font = ToontownGlobals.getNametagFont(index)
                    loadedFrom = fontPath
                    break
        except:
            font = None

    # Finally try the expected Comic.ttf resource locations directly.
    if not font:
        try:
            from panda3d.core import Filename, VirtualFileSystem

            vfs = VirtualFileSystem.getGlobalPtr()

            for fontPath in data.get('speechFontPaths', ()):
                filename = Filename(fontPath)
                rootedFilename = Filename('/' + fontPath)

                if not (vfs.exists(filename) or
                        vfs.exists(rootedFilename)):
                    continue

                font = loader.loadFont(fontPath, lineHeight=1.0)
                loadedFrom = fontPath
                break
        except:
            font = None

    if font:
        data['_loadedSpeechFont'] = font
        data['_loadedSpeechFontPath'] = loadedFrom

    return font


def _setFontOnTarget(target, font):
    if target is None:
        return False

    applied = False

    # The original OTP nametag stack calls this setSpeechFont, while the
    # newer Python nametag stack calls it setChatFont.
    for methodName in ('setSpeechFont', 'setChatFont'):
        method = getattr(target, methodName, None)

        if method:
            try:
                method(font)
                applied = True
            except:
                pass

    return applied


def _applySpeechFont(npc, data):
    if not data.get('speechFontName'):
        return True

    font = _loadSpeechFont(data)
    if not font:
        if not getattr(npc, '_speechFontMissingLogged', False):
            print (
                '[Toon Hall NPC] Could not find Comical font for %s. '
                'Checked registered fonts and Comic.ttf paths.'
                % data.get('name', 'unknown NPC')
            )
            npc._speechFontMissingLogged = True
        return False

    applied = _setFontOnTarget(npc, font)

    nametag = getattr(npc, 'nametag', None)
    if nametag is not None:
        if _setFontOnTarget(nametag, font):
            applied = True

        for getterName in ('getNametag2d', 'getNametag3d'):
            getter = getattr(nametag, getterName, None)

            if getter:
                try:
                    if _setFontOnTarget(getter(), font):
                        applied = True
                except:
                    pass

    if applied and not getattr(npc, '_speechFontAppliedLogged', False):
        print (
            '[Toon Hall NPC] Applied %s speech font to %s from %s'
            % (
                data.get('speechFontName', 'custom'),
                data.get('name', 'unknown NPC'),
                data.get('_loadedSpeechFontPath', 'registered font')
            )
        )
        npc._speechFontAppliedLogged = True

    return applied


def _advanceTypewriterSpeech(npc, data, originalMethod, state, task):
    text = state.get('text', '')
    index = state.get('index', 1)

    if not text or index >= len(text):
        return task.done

    index += 1
    state['index'] = index

    try:
        _applySpeechFont(npc, data)
        originalMethod(
            text[:index],
            state['flags'],
            *state.get('args', ()),
            **state.get('kwargs', {})
        )
    except:
        return task.done

    if index >= len(text):
        return task.done

    return task.again


def _installTypewriterSpeech(npc, data):
    if not data.get('typewriterSpeech'):
        return True

    if getattr(npc, '_toonHallTypewriterSpeechInstalled', False):
        return True

    originalMethod = getattr(npc, 'setChatAbsolute', None)
    phrase = data.get('phrase')

    if not originalMethod or not phrase:
        return False

    try:
        delay = max(0.03, float(data.get('typewriterDelay', 0.5)))
    except:
        delay = 0.5

    taskName = 'toonHallTypewriterSpeech-%s' % getattr(
        npc,
        'doId',
        id(npc)
    )

    def typewriterSetChatAbsolute(chatString, chatFlags, *args, **kwargs):
        # Leave every other speech line and system bubble untouched.
        if chatString != phrase:
            return originalMethod(
                chatString,
                chatFlags,
                *args,
                **kwargs
            )

        taskMgr.remove(taskName)
        _applySpeechFont(npc, data)

        state = {
            'text': chatString,
            'flags': chatFlags,
            'args': args,
            'kwargs': kwargs,
            'index': 1,
        }

        # Show the first character immediately.
        originalMethod(
            chatString[:1],
            chatFlags,
            *args,
            **kwargs
        )

        if len(chatString) > 1:
            taskMgr.doMethodLater(
                delay,
                _advanceTypewriterSpeech,
                taskName,
                extraArgs=[npc, data, originalMethod, state],
                appendTask=True
            )

        return None

    npc._toonHallOriginalSetChatAbsolute = originalMethod
    npc.setChatAbsolute = typewriterSetChatAbsolute
    npc._toonHallTypewriterSpeechInstalled = True
    return True


def _loadNPCDialogueSound(data):
    soundPath = data.get('dialogueSfx')
    if not soundPath:
        return None

    if soundPath in _NPC_DIALOGUE_SOUND_CACHE:
        return _NPC_DIALOGUE_SOUND_CACHE[soundPath]

    candidates = [soundPath]
    normalizedPath = soundPath.replace('\\', '/')

    if normalizedPath.startswith('resources/'):
        candidates.append(normalizedPath[len('resources/'):])
    else:
        candidates.append('resources/' + normalizedPath)

    sound = None

    for candidate in candidates:
        try:
            sound = loader.loadSfx(candidate)
        except:
            sound = None

        if sound:
            break

    # Cache failures too so walking into the NPC repeatedly does not keep
    # attempting disk loads when the resource is genuinely missing.
    _NPC_DIALOGUE_SOUND_CACHE[soundPath] = sound

    if not sound:
        print (
            '[Toon Hall NPC] Could not load dialogue sound for %s: %s'
            % (data.get('name', 'unknown NPC'), soundPath)
        )

    return sound


def _installCustomDialogueSpeech(npc, data):
    if not data.get('dialogueSfx'):
        return True

    if getattr(npc, '_toonHallCustomDialogueInstalled', False):
        return True

    originalMethod = getattr(npc, 'setChatAbsolute', None)
    phrase = data.get('phrase')

    if not originalMethod or not phrase:
        return False

    def customDialogueSetChatAbsolute(chatString, chatFlags,
                                      dialogue=None, *args, **kwargs):
        # Only replace the voice for this NPC's configured interaction line.
        # Other system bubbles and dialogue calls retain their original sound.
        if chatString == phrase and dialogue is None:
            customDialogue = _loadNPCDialogueSound(data)

            if customDialogue is not None:
                dialogue = customDialogue
            else:
                # Keep the text bubble but do not fall back to normal Toon
                # gibberish when the requested High Roller audio is missing.
                mutedMethod = getattr(npc, 'setChatMuted', None)
                if mutedMethod:
                    try:
                        return mutedMethod(
                            chatString,
                            chatFlags,
                            None,
                            *(args or ()),
                            **kwargs
                        )
                    except:
                        pass

        return originalMethod(
            chatString,
            chatFlags,
            dialogue,
            *args,
            **kwargs
        )

    npc._toonHallOriginalCustomDialogueSetChatAbsolute = originalMethod
    npc.setChatAbsolute = customDialogueSetChatAbsolute
    npc._toonHallCustomDialogueInstalled = True
    return True

def _findLoadedToonHallInterior(npc):
    try:
        from toontown.building.DistributedToonHallInterior import (
            DistributedToonHallInterior
        )

        interiors = npc.cr.doFindAllInstances(
            DistributedToonHallInterior
        )

        npcZoneId = getattr(npc, 'zoneId', None)
        fallback = None

        for toonHall in interiors:
            interior = getattr(toonHall, 'interior', None)
            if not interior or interior.isEmpty():
                continue

            if fallback is None:
                fallback = interior

            if getattr(toonHall, 'zoneId', None) == npcZoneId:
                return interior

        return fallback
    except:
        return None



def _disableCustomNPCQuestWork(npc):
    """Custom display NPCs never offer quests, so skip the costly scan."""
    if getattr(npc, '_toonHallQuestWorkDisabled', False):
        return

    try:
        npc.setQuestNotify(None)
    except:
        pass

    checkQuestStatus = getattr(npc, 'checkQuestStatus', None)
    if checkQuestStatus:
        npc._toonHallOriginalCheckQuestStatus = checkQuestStatus
        npc.checkQuestStatus = lambda: None

    npc._toonHallQuestWorkDisabled = True


def _setCustomNPCCollisionEnabled(npc, enabled):
    current = getattr(npc, '_toonHallCollisionEnabled', None)
    if current == enabled:
        return

    try:
        from panda3d.core import BitMask32
        from toontown.toonbase import ToontownGlobals

        if enabled:
            npc.cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)
            npc.detectAvatars()
        else:
            # Remove an interaction prompt that may have been left on-screen.
            try:
                npc.handleCollisionSphereExit(None)
            except:
                pass
            npc.ignoreAvatars()
            npc.cSphereNode.setCollideMask(BitMask32.allOff())

        npc._toonHallCollisionEnabled = enabled
    except:
        pass


def _setCustomNPCNametagEnabled(npc, enabled):
    current = getattr(npc, '_toonHallNametagEnabled', None)
    if current == enabled:
        return

    methodName = 'showNametag3d' if enabled else 'hideNametag3d'
    method = getattr(npc, methodName, None)

    try:
        if method:
            method()
        else:
            nametag3d = getattr(npc, 'nametag3d', None)
            if nametag3d:
                if enabled:
                    nametag3d.show()
                else:
                    nametag3d.hide()
        npc._toonHallNametagEnabled = enabled
    except:
        pass


def _setCustomNPCNearState(npc):
    previousState = getattr(npc, '_toonHallOptimizationState', None)
    if previousState == 'near':
        return

    # Ensure the normal idle animation is active when returning to full detail.
    if previousState in ('medium', 'far'):
        try:
            npc.setAnimState('neutral', 0.9, None, None)
        except:
            pass

        try:
            npc.startLookAround()
        except:
            pass

    _setCustomNPCNametagEnabled(npc, True)
    _setCustomNPCCollisionEnabled(npc, True)
    npc._toonHallOptimizationState = 'near'


def _setCustomNPCMediumState(npc):
    if getattr(npc, '_toonHallOptimizationState', None) == 'medium':
        return

    try:
        npc.stopLookAround()
    except:
        pass

    # Holding the current neutral pose removes continuous skeletal updates.
    # The NPC remains fully rendered and immediately resumes when approached.
    try:
        npc.stop()
    except:
        pass

    _setCustomNPCNametagEnabled(npc, True)
    _setCustomNPCCollisionEnabled(npc, False)
    npc._toonHallOptimizationState = 'medium'


def _setCustomNPCFarState(npc):
    if getattr(npc, '_toonHallOptimizationState', None) == 'far':
        return

    try:
        npc.stopLookAround()
    except:
        pass

    try:
        npc.stop()
    except:
        pass

    # Keep every custom NPC's nametag visible, even at maximum distance.
    _setCustomNPCNametagEnabled(npc, True)
    _setCustomNPCCollisionEnabled(npc, False)
    npc._toonHallOptimizationState = 'far'


def _customNPCNeedsFullDetail(npc):
    try:
        if npc.isBusyWithLocalToon():
            return True
    except:
        pass

    if getattr(npc, 'curQuestMovie', None):
        return True
    if getattr(npc, 'clubGui', None):
        return True
    return False


def _getCustomNPCDistance(npc):
    try:
        localAvatar = getattr(base, 'localAvatar', None)
        if localAvatar is None:
            return 0.0
        return localAvatar.getDistance(npc)
    except:
        return 0.0


def _updateCustomNPCOptimization(npc):
    if _customNPCNeedsFullDetail(npc):
        _setCustomNPCNearState(npc)
        return

    distance = _getCustomNPCDistance(npc)

    if distance <= NPC_FULL_DETAIL_DISTANCE:
        _setCustomNPCNearState(npc)
    elif distance <= NPC_NAMETAG_DISTANCE:
        _setCustomNPCMediumState(npc)
    else:
        _setCustomNPCFarState(npc)


def _customNPCOptimizationTask(task):
    global _OPTIMIZED_NPC_REFS
    global _OPTIMIZATION_TASK_RUNNING

    aliveRefs = []

    for npcRef in _OPTIMIZED_NPC_REFS:
        npc = npcRef()
        if npc is None:
            continue

        try:
            if npc.isEmpty():
                continue
        except:
            continue

        aliveRefs.append(npcRef)
        _updateCustomNPCOptimization(npc)

    _OPTIMIZED_NPC_REFS = aliveRefs

    if not aliveRefs:
        _OPTIMIZATION_TASK_RUNNING = False
        return task.done

    task.delayTime = NPC_OPTIMIZATION_INTERVAL
    return task.again


def _registerCustomNPCOptimization(npc):
    global _OPTIMIZATION_TASK_RUNNING

    if getattr(npc, '_toonHallOptimizationRegistered', False):
        _updateCustomNPCOptimization(npc)
        return

    npc._toonHallOptimizationRegistered = True

    try:
        npcRef = weakref.ref(npc)
    except TypeError:
        # Some older Panda3D extension wrappers do not expose weakrefs.
        # Keep a direct callable reference; isEmpty() still removes it later.
        npcRef = lambda: npc

    _OPTIMIZED_NPC_REFS.append(npcRef)

    # DistributedNPCToonBase.generate already enables both of these. Mark
    # their initial state so a nearby NPC is not registered twice.
    npc._toonHallCollisionEnabled = True
    npc._toonHallNametagEnabled = True

    # Panda3D's built-in LOD animation throttling updates distant skeletons
    # less often even before the shared manager freezes medium/far NPCs.
    try:
        npc.setLODAnimation(
            NPC_LOD_ANIMATION_FAR_DISTANCE,
            NPC_LOD_ANIMATION_NEAR_DISTANCE,
            NPC_LOD_ANIMATION_DELAY
        )
    except:
        pass

    _disableCustomNPCQuestWork(npc)
    _updateCustomNPCOptimization(npc)

    if not _OPTIMIZATION_TASK_RUNNING:
        taskMgr.remove(NPC_OPTIMIZATION_TASK_NAME)
        taskMgr.doMethodLater(
            NPC_OPTIMIZATION_INTERVAL,
            _customNPCOptimizationTask,
            NPC_OPTIMIZATION_TASK_NAME
        )
        _OPTIMIZATION_TASK_RUNNING = True

def positionClientNPC(npc):
    data = getDataForNPC(npc)
    if not data:
        return False

    pos = data['pos']
    hpr = data['hpr']
    area = data.get('area', 'toonhall')

    npc.reparentTo(render)

    if area == 'ttc':
        # TTC printer coordinates are already in render/world space.
        npc.setPos(render, pos[0], pos[1], pos[2])
        npc.setHpr(render, hpr[0], hpr[1], hpr[2])
        positionReference = render
    else:
        interior = _findLoadedToonHallInterior(npc)
        if not interior:
            return False

        # Toon Hall coordinates are relative to the loaded interior model.
        npc.setPos(interior, pos[0], pos[1], pos[2])
        npc.setHpr(interior, hpr[0], hpr[1], hpr[2])
        positionReference = interior
    _applyIrisColor(npc, data)
    _applyEarColor(npc, data)
    _applyBoyShorts(npc, data)
    _applyGirlSkirt(npc, data)
    _applyNedStripedShirt(npc, data)
    _applyCustomShirtColor(npc, data)
    _applyCustomBottomColor(npc, data)
    _applyBlackBottomPattern(npc, data)
    _applyHiddenGloves(npc, data)
    _applySpeechFont(npc, data)
    _installTypewriterSpeech(npc, data)
    _installCustomDialogueSpeech(npc, data)
    _registerCustomNPCOptimization(npc)

    hatGenerated = _applyConfiguredHat(npc, data)
    hatPlaced = _applyHatPlacement(npc, data)
    glassesGenerated = _applyConfiguredGlasses(npc, data)
    glassesPlaced = _applyGlassesPlacement(npc, data)
    extraGlassesApplied = _applyExtraGlasses(npc, data)
    _applyVisibleEyelashes(npc, data, rebuild=True)

    if (data.get('directCustomHat') or
            (data.get('forceClientHat') and not hatGenerated) or
            data.get('hatPlacement') or not hatPlaced):
        taskName = 'toonHallHatPlacement-%s' % getattr(
            npc,
            'doId',
            id(npc)
        )
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(
            0.1,
            _retryHatPlacement,
            taskName,
            extraArgs=[npc, data],
            appendTask=True
        )

    if ((data.get('forceClientGlasses') and not glassesGenerated) or
            data.get('glassesPlacement') or not glassesPlaced or
            (data.get('extraGlasses') and not extraGlassesApplied)):
        taskName = 'toonHallGlassesPlacement-%s' % getattr(
            npc,
            'doId',
            id(npc)
        )
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(
            0.1,
            _retryGlassesPlacement,
            taskName,
            extraArgs=[npc, data],
            appendTask=True
        )

    actual = npc.getPos(positionReference)
    actualHpr = npc.getHpr(positionReference)

    if not getattr(npc, '_toonHallPositionLogged', False):
        print (
            '[Custom NPC] Positioned %s at '
            'X=%.3f Y=%.3f Z=%.3f H=%.3f'
            % (
                data['name'],
                actual[0],
                actual[1],
                actual[2],
                actualHpr[0]
            )
        )
        npc._toonHallPositionLogged = True

    return True
