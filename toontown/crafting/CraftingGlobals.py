from enum import IntEnum

from toontown.toonbase import TTLocalizer

# Currently only uses Halloween materials
TOTAL_CRAFT_MATERIALS = 16


# Halloween Reagents
class HalloweenMaterial(IntEnum):
    CRAFT_MAT_BONE = 0
    CRAFT_MAT_BOLT_HALLOWEEN = 1
    CRAFT_MAT_BAG_OF_STRAW = 2
    CRAFT_MAT_TATTERED_CLOTH = 3
    CRAFT_MAT_POTION = 4
    CRAFT_MAT_EAT_ME_COOKIE = 5
    CRAFT_MAT_LIGHTNING_BOLT = 6
    CRAFT_MAT_CLOWN_NOSE = 7
    CRAFT_MAT_ROCKET = 8
    CRAFT_MAT_BAT = 9
    CRAFT_MAT_SUPERTOON_EMBLEM = 10
    CRAFT_MAT_CREEPY_CRAWLY = 11
    CRAFT_MAT_BROOMSTICK = 12
    CRAFT_MAT_EGG_HALLOWEEN = 13
    CRAFT_MAT_PUMPKIN = 14
    CRAFT_MAT_TREASURE = 15


# This is separate, it is used to denote something that costs some of every material.
CRAFT_MAT_ALL = -1
HALLOWEEN_MAT_START = 0
HALLOWEEN_MAT_END = 15

MaterialIconNames = (
    'material_bone',
    'material_bolt_event',
    'material_bag_of_straw',
    'material_tattered_cloth',
    'material_potion',
    'material_eat_me_cookie',
    'material_lightning',
    'material_clown_nose',
    'material_rocket',
    'material_bat',
    'material_supertoon',
    'material_bugs',
    'material_broomstick',
    'material_egg',
    'material_pumpkin',
    'material_treasure'
)


def getSortedMaterialIndex(rawMatIndex):
    names = TTLocalizer.MaterialNames
    sortedNames = names[:]
    sortedNames.sort()
    searchingName = names[rawMatIndex]
    return sortedNames.index(searchingName)


def getUnsortedMaterialIndex(sortedMatIndex):
    names = TTLocalizer.MaterialNames
    sortedNames = names[:]
    sortedNames.sort()
    searchingName = sortedNames[sortedMatIndex]
    return names.index(searchingName)
