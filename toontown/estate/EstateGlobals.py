from enum import IntEnum, unique

from toontown.inventory.enums.ItemAttribute import ItemAttribute


@unique
class EstateType(IntEnum):
    """
    The 'type' of Estate generated.
    Associated with different player access and separate databases.
    """
    USER = 0
    CLUB = 1


@unique
class EstateItemType(IntEnum):
    """
    The item type of an Estate item.
    Defined on an item's ItemDefinition.
    Determines the kind of DO AI class generated for it.
    """
    GENERIC = 0  # no functionality
    DOORWAY = 1  # connects subzones
    HOUSE = 2  # houses are doorways
    PIER = 3
    ACTOR_INTERACTABLE = 4
    GENERIC_PLANE = 5  # Dealing with flat planes for swapping textures
    SKYBOX = 6
    GENERIC_ACTOR = 7  # UNUSED
    TUNNEL = 8  # for subzones
    WINDOW_VIEW = 9

    # Items with specific modifiable attributes
    PROP_FIREPLACE = 100
    LAVA_LAMP = 101
    PROP_CLOCK = 102
    PROP_TV = 103
    PROP_SIGN = 104
    PROP_GARDEN_FLOWER = 105
    PROP_PUMPKIN = 106
    PROP_LIGHTSWITCH = 107
    PROP_TIMER = 108
    PROP_DISPLAY = 109
    PROP_STATUE_TOON = 110
    PROP_MERRY_GO_ROUND = 111
    PROP_LIGHT_NEON = 112

    # Physically interactable
    PROP_INTERACTIVE_CANNON = 1000
    PROP_INTERACTIVE_TRAMPOLINE = 1001
    PROP_INTERACTIVE_JUKEBOX = 1002
    PROP_INTERACTIVE_DANCEFLOOR = 1003

    PROP_TABLE_BOARDGAMES = 1005
    PROP_TABLE_PICNIC = 1006
    PROP_INTERACTIVE_HYDRANT = 1007
    PROP_INTERACTIVE_TRASHCAN = 1008
    PROP_INTERACTIVE_MAILBOX = 1009
    PROP_INTERACTIVE_FISHBUCKET = 1010
    PROP_INTERACTIVE_KART = 1011
    PROP_INTERACTIVE_BALL = 1012
    PROP_INTERACTIVE_DUMMY = 1013  # Reacts to a throwable hitting it

    PROP_VENDOR_THROWABLE = 1200
    PROP_GENERATOR_TREASURES = 1201
    PROP_GENERATOR_BUTTERFLY = 1202
    PROP_VENDOR_FIREWORKS = 1203
    PROP_VENDOR_DISPENSER_TANK = 1204  # gag tank
    PROP_GENERATOR_PARTICLES = 1205
    PROP_GENERATOR_FOG = 1206
    PROP_GENERATOR_CLOUDS = 1207 # for cannon
    PROP_GENERATOR_WEATHER = 1208
    PROP_GENERATOR_FIREWORKS = 1209

    # Zaptronics-ish
    PROP_INTERACTIVE_BUTTON = 1004

    PROP_BELL = 2000
    PROP_WARDROBE = 2001
    PROP_TRUNK = 2002
    PROP_CHAIR = 2003

    # 9000: Debug
    DEBUG_OUCH = 9000
    DEBUG_TAG = 9001
    DEBUG_ROPE = 9002
    DEBUG_OCCLUDER = 9003
    DEBUG_PRIMITIVE = 9004


@unique
class EstateKitType(IntEnum):
    """
    The type of estate kit this is.
    Defined on an item's StyleDefinition.
    """
    STANDARD = 0  # No special behavior on this kit
    INTERIOR = 1
    EXTERIOR = 2

@unique
class EstateItemPlacementFlags(IntEnum):
    """
    The placement flags for estate items.
    Defined on an item's ItemDefinition.
    Determines the type of placement this has (standard/wall/rug/on_table).
    """
    STANDARD = 1
    WALL = 2
    RUG = 3
    WALL_STUCK_TO_FLOOR = 4
    WINDOW = 5


# How close to an object does the camera need to be to allow it to be editable
MOVABLE_OBJECT_EDIT_DIST = 40.0

MAX_ESTATE_SUBZONES = 10

ESTATE_DOORWAY_ATTRIBUTE_TAG = ItemAttribute.ESTATE_ENTRANCE

ESTATE_SUBZONE_GENERATED_BBOARD = 'DistributedEstateSubzone-BBoard-Generated'
ESTATE_SUBZONE_DELETED_MESSAGE = 'DistributedEstateSubzone-Deleted'

ESTATE_ITEM_GENERATED_MESSAGE = 'DistributedEstateItem-Generated'
ESTATE_ITEM_PLACEMENT_UPDATED = 'DistributedEstateItem-PlacementUpdated'

ESTATE_GUI_OPEN_EDIT_MENU = 'EstateGUIManager-OpenItemEditMenu'

ESTATE_ROUTER_OWNER_NAME_BBOARD = 'EstateRouterGlobal-OwnerName'
