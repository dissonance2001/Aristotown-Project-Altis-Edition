from toontown.toonbase import ToontownGlobals

# State Indexes
OFF = 0
MOVING = 1

StepTime = 5.0 # seconds

# Minimum hunger value for all targets.
# Must be in range [0.0->1.0]. Higher values are more hungry.
# Let's try making them always hungry
MinimumHunger = 1.0

NUM_TARGETS_INDEX = 0
POS_START_INDEX = 1
POS_END_INDEX = 4
RADIUS_INDEX = 4
WATER_LEVEL_INDEX = 5

__targetInfoDict = {
    # zone : (num, x, y, z, radius, waterlevel)

    # Toontown Central #
    ToontownGlobals.ToontownCentral: (2, -81, 31, -4.8, 14, -1.4),
    ToontownGlobals.SillyStreet: (2, 20, -664, -1.4, 14, -1.4 - 0.438),
    ToontownGlobals.LoopyLane: (2, -234, 175, -1.4, 14, -1.4 - 0.462),
    ToontownGlobals.PunchlinePlace: (2, 529, -70, -1.4, 13, -1.4 - 0.486),
    ToontownGlobals.WackyWay: (2, -229, 340, -1.4, 14, -1.4 - 0.486),

    # Barnacle Boatyard #
    ToontownGlobals.DonaldsDock: (2, -17, 130, 1.73, 15, 1.73 - 3.615),
    ToontownGlobals.BarnacleBoulevard: (2, 381, -350, -2, 14, -2 - 0.482),
    ToontownGlobals.SeaweedStreet: (2, -395, -226, -2, 14, -2 - 0.482),
    ToontownGlobals.LighthouseLane: (2, 350, 100, -2, 14, -2 - 0.482),
    ToontownGlobals.AhoyAvenue: (4, 50, -90, -2, 14, -2 - 0.482),

    # Daffodil Gardens #
    ToontownGlobals.DaisyGardens: (4, 75, 62, -1.48, 15.6, -1.48 - 0.345),
    ToontownGlobals.ElmStreet: (2, 149, 44, -1.43, 13, -1.43 - 0.618),
    ToontownGlobals.MapleStreet: (2, 176, 100, -1.43, 13, -1.43 - 0.618),
    ToontownGlobals.OakStreet: (2, 134, -70.5, -1.5, 13, -1.5 - 0.377),
    ToontownGlobals.RoseValley: (2, 259, -217, -1.5, 13, -1.43 - 0.618),

    # Mezzo Melodyland #
    ToontownGlobals.MinniesMelodyland: (2, -0.2, -20.2, -14.65, 14, -14.65 - -12.2),
    ToontownGlobals.AltoAvenue: (2, -580, -90, -0.87, 14, -0.87 - 1.844),
    ToontownGlobals.BaritoneBoulevard: (2, -214, 250, -0.87, 14, -0.87 - 1.844),
    ToontownGlobals.TenorTerrace: (2, 715, -15, -0.87, 14, -0.87 - 1.844),
    ToontownGlobals.SopranoStreet: (2, 280, 95, 4.15, 14, -0.87 - 1.844),

    # Acorn Acres #
    ToontownGlobals.OutdoorZone: (4, 13.253, 126.574, 7.815, 14, -0.5),

    # Ye Olde Toontowne #
    ToontownGlobals.YeOlde: (6, -124.875, -10.615, -11.57, 16, -2.25),

    # The Brrrgh #
    ToontownGlobals.TheBrrrgh: (2, -58, -26, 1.7, 10, -0.8),
    ToontownGlobals.WalrusWay: (2, 460, 29, -2, 13, -2 - 0.4),
    ToontownGlobals.SleetStreet: (2, 340, 480, -2, 13, -2 - 0.4),
    ToontownGlobals.PolarPlace: (2, 45.5, 90.86, -2, 13, -2 - 0.4),
    ToontownGlobals.ArcticAvenue: (2, -60, 340, -2, 13, -1.0),

    # Drowsy Dreamland #
    ToontownGlobals.DonaldsDreamland: (2, -7.2, 167, -1.05, 14, -1.05),
    ToontownGlobals.LullabyLane: (2, 118, -185, -2.1, 14, -2.1 - 0.378),
    ToontownGlobals.PajamaPlace: (2, 241, -348, -2.1, 14, -2.1 - 0.378),
    ToontownGlobals.TwilightTerrace: (2, 89.759, -103.341, -1.9, 14, -1.1),
}


def getNumTargets(zone):
    """
    Returns number of targets (fish shadows) that pond is suppose to have.
    Minimum amount is 2.

    :param zone: zoneId
    :return: info[NUM_TARGETS_INDEX] | 2
    """
    info = __targetInfoDict.get(zone)
    if info:
        return info[NUM_TARGETS_INDEX]
    else:
        return 2


def getTargetCenter(zone):
    """
    :param zone: zoneId
    :return: info[POS_START_INDEX:POS_END_INDEX] | (0, 0, 0)
    """
    info = __targetInfoDict.get(zone)
    if info:
        return info[POS_START_INDEX:POS_END_INDEX]
    else:
        return (0, 0, 0)


def getTargetRadius(zone):
    """
    :param zone: zoneId
    :return: info[RADIUS_INDEX] | 10
    """
    info = __targetInfoDict.get(zone)
    if info:
        return info[RADIUS_INDEX]
    else:
        return 10


def getWaterLevel(zone):
    """
    :param zone: zoneId
    :return: info[WATER_LEVEL_INDEX] | 0
    """
    info = __targetInfoDict.get(zone)
    if info:
        return info[WATER_LEVEL_INDEX]
    else:
        return 0
