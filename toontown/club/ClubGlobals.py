"""
Global definitions for Clubs.
"""
import math
import random
from bisect import bisect_right
from enum import IntEnum, auto, Enum

from toontown.club.ClubColor import ClubColor, ClubColorPulser
from toontown.club.ClubEnums import ClubRank, CAN_MAKE_ANNOUNCEMENTS, CAN_KICK_TOONS, PURCHASE_CLUB_SHOP_ITEMS, \
    ClubShopCategory, ClubNameStatus
from toontown.inventory.enums.ItemEnums import BoosterItemType
from toontown.time.TimeUtil import checkIsDay
from toontown.toonbase import TTLocalizer, ProcessGlobals
from toontown.toonbase.TTLocalizerEnglish import BattleGlobalAvPropStrings
from toontown.utils.AstronStruct import AstronStruct
from typing import List, Dict

ClubCreationCost = 20000  # 20,000 beans to create a club

# Club coin globals.
ClubMaxCoins = 10_000_000
ClubMaxJellybeans = 1_000_000_000
ClubMaxXp = 10_000_000
NaturalClubCoinMultiplier = 2  # club coins earned from natural means

# The number of seconds between each announcement of club coin gains.
ClubCoinAnnouncementPeriod = 15 * 60


class ClubCapacityCostType(Enum):
    CC = auto()
    JBS = auto()


# The cost of each capacity upgrade.
ClubCapacityUpgrades = {
    15: {"cost": 25, "level": 5, "type": ClubCapacityCostType.CC},
    20: {"cost": 100, "level": 15, "type": ClubCapacityCostType.CC},
    25: {"cost": 200, "level": 25, "type": ClubCapacityCostType.CC},
    30: {"cost": 300, "level": 35, "type": ClubCapacityCostType.CC},
    35: {"cost": 600, "level": 50, "type": ClubCapacityCostType.CC},
    40: {"cost": 800, "level": 65, "type": ClubCapacityCostType.CC},
    45: {"cost": 1_250, "level": 80, "type": ClubCapacityCostType.CC},
    50: {"cost": 1_000_000, "level": 100, "type": ClubCapacityCostType.JBS},
    55: {"cost": 5_000, "level": 110, "type": ClubCapacityCostType.CC},
    60: {"cost": 2_500_000, "level": 120, "type": ClubCapacityCostType.JBS},
    65: {"cost": 15_000, "level": 130, "type": ClubCapacityCostType.CC},
    70: {"cost": 5_000_000, "level": 140, "type": ClubCapacityCostType.JBS},
    75: {"cost": 25_000, "level": 150, "type": ClubCapacityCostType.CC},
    # TODO: uncomment these later for more upgrades
    # 80: {"cost": 40_000_000, "level": 160, "type": ClubCapacityCostType.JBS},
    # 85: {"cost": 55_000, "level": 170, "type": ClubCapacityCostType.CC},
    # 90: {"cost": 70_000_000, "level": 180, "type": ClubCapacityCostType.JBS},
    # 95: {"cost": 85_000, "level": 190, "type": ClubCapacityCostType.CC},
    # 100: {"cost": 100_000_000, "level": 200, "type": ClubCapacityCostType.JBS},
}

# Club size range.
ClubMinSize = 10
ClubMaxSize = list(ClubCapacityUpgrades)[-1]

# Several club defaults.
DefaultClubName = "Colorful Club"
DefaultMOTD = "Welcome to the club!"
MaxMOTDLength = 80

# XP Globals.
ClubStartXP = 10
ClubXPRampup = 1.03
ClubMaxLevel = 999
ClubMaxXP = sum([math.ceil(ClubStartXP * (level ** ClubXPRampup)) for level in range(0, ClubMaxLevel)]) - 1

# Rate limiter
CLUB_UD_RATELIMITER_MAX_HITS = 5
CLUB_UD_RATELIMITER_PERIOD = 1

CLUB_UD_SAVE_TIME = 30

# Name globals.
ClubMaxNameLength = 30

# Booster globals
ClubMaxBoosters = 3
ClubBoosterHours = 48

# Log  g  g
ClubMaxLogs = 100000
ClubLogsPerPage = 40

#       tasq
ClubTaskCount = 3
ClubTaskDifficultyCoeff = 1.15  # difficulty scaling with toon level
ClubTaskAntiCheeseDuration = 60 * 60 * 72  # 72 hours

# This doesn't really mean too much currently,
# since a lot of backend will still have to adjust for making this >1.
MaxClubsPerToon = 1

# Task Duration.
ClubTaskDuration = (
    60 * 60 * 24 * 7,  # easy, 1 week
    60 * 60 * 24 * 5,  # medium, 5 days
    60 * 60 * 24 * 4,  # hard, 4 days
)

# What perms are skipped per roles?
# (These are invisible in the settings.)
ClubPermsSkipped = {
    ClubRank.Officer: (
        CAN_MAKE_ANNOUNCEMENTS,
    ),
    ClubRank.Deputy: (
        CAN_MAKE_ANNOUNCEMENTS,
    ),
    ClubRank.Member: (
        CAN_KICK_TOONS,
        CAN_MAKE_ANNOUNCEMENTS,
    )
}


"""
Club Math Methods
"""


def calculateClubLevel(clubXp: float):
    """
    Calculates the club level given an amount of clubCoins.
    :return: level, currentXp, maxXp

    :todo no while loop please
    """
    # set values for calculation
    currentXp = math.floor(clubXp)
    maxXp = ClubStartXP
    level = 1

    # run loop to do club level math
    while currentXp >= maxXp:
        currentXp = round(currentXp - maxXp)
        maxXp = math.ceil(maxXp * ClubXPRampup)
        level += 1

    # return our values
    return level, int(currentXp), int(maxXp)


"""
Global definitions for purchasable items from the Club Shop.
"""


class ClubItemType(IntEnum):
    CLUB_ICON = auto()
    CLUB_BACKGROUND = auto()
    CLUB_THEME_COL = auto()
    CLUB_BG_COL = auto()
    CLUB_NAME_CHANGE = auto()
    CLUB_MEMBER_SLOTS = auto()
    CLUB_BOOSTERS = auto()
    CLUB_BOOSTER_SLOTS = auto()


ClubItemTypeToName = {
    ClubItemType.CLUB_ICON:          ('Icon Image',    'new ',        ' Purchased', 'a ',   ''),
    ClubItemType.CLUB_BACKGROUND:    ('Icon Detail',   'new ',        ' Purchased', 'a ',   ''),
    ClubItemType.CLUB_THEME_COL:     ('Theme Color',   'new ',        ' Purchased', 'a ',   ''),
    ClubItemType.CLUB_BG_COL:        ('Detail Color',  'new ',        ' Purchased', 'a ',   ''),
    ClubItemType.CLUB_NAME_CHANGE:   ('Name Change',   'Club ',       ' Purchased', 'a ',   ''),
    ClubItemType.CLUB_MEMBER_SLOTS:  ('Member Slots',  'additional ', ' Purchased', '',     ''),
    ClubItemType.CLUB_BOOSTERS:      ('Booster',       'Club ',       ' Purchased', 'a ',   ' Active'),
    ClubItemType.CLUB_BOOSTER_SLOTS: ('Booster Slots', 'additional ', ' Purchased', '',     ''),
}


class ClubItem(AstronStruct):
    """
    Essentially a dataclass detailing
    club item description, pricing and etc.
    """

    def __init__(self, type: ClubItemType, name: str = '', cost: int = 0,
                 description: str = '', value=None, useJellybeans: bool = False,
                 levelRequired: int = 0, lockWeekday: int = None,
                 copyId: int = None):
        """
        :param type:          The type of item the ClubItem is.
        :param name:          The name of the ClubItem.
        :param cost:          The cost of the ClubItem.
        :param description:   The description of the ClubItem.
        :param value:         The value of the ClubItem (in Club Coins)
        :param useJellybeans:    Does the ClubItem cost Jellybeans and not Club Coins?
        :param levelRequired: Is this item level-locked?
        :param lockWeekday:   Can this item only be bought on a weekday?
        :param copyId:        Copy the values of another Club Item.
        """
        self.type = type
        self.name = name
        self.cost = cost
        self.description = description
        self.value = value
        self.itemID = None
        self.useJellybeans = useJellybeans
        self.levelRequired = levelRequired
        self.lockWeekday = lockWeekday
        self.copyId = copyId

    """Struct momence"""

    def toStruct(self) -> int:
        return self.itemID

    @staticmethod
    def toStructList(astronStructs):
        return astronStructs

    @classmethod
    def fromStruct(cls, struct: int):
        return ClubItemIndex.getItem(struct)

    """Processing"""

    def postProcess(self, clubItemIndex: 'ClubItemIndex'):
        # Handle copy-to.
        if self.copyId is not None:
            otherItem = clubItemIndex.getItem(self.copyId)
            self.copyTo(otherItem)

    def copyTo(self, item: 'ClubItem'):
        """Copies properties to match another item."""
        self.name = item.name
        self.cost = item.cost
        self.description = item.description
        self.value = item.value
        self.useJellybeans = item.useJellybeans
        self.levelRequired = item.levelRequired
        self.lockWeekday = item.lockWeekday
        self.copyId = item.copyId

    """Simple getters"""

    def getType(self) -> ClubItemType:
        return self.type

    def getValue(self):
        return self.value

    def getItemID(self):
        return self.itemID

    def getCost(self, clubContainer):
        return self.cost

    def getName(self):
        return self.name

    def getDescription(self, clubContainer):
        levelRequired = self.getLevelRequired(clubContainer)
        if levelRequired > clubContainer.getClubLevel():
            return TTLocalizer.ClubShopInsufficientLevel % levelRequired
        return self.description

    def getLevelRequired(self, clubContainer):
        return self.levelRequired

    def storesId(self):
        # Is the item ID stored on the club container upon purchase? (For permanent purchases.)
        return True

    @staticmethod
    def hasPermission(clubContainer, avId):
        return clubContainer.avIdHasPermission(avId, PURCHASE_CLUB_SHOP_ITEMS)

    """Complex getters"""

    def aboveLevelMinimum(self, club):
        level, currentXp, maxXp = calculateClubLevel(club.clubXp)
        return level >= self.getLevelRequired(club)

    def canPurchase(self, club, avId):
        return self.aboveLevelMinimum(club) \
               and self.isRightWeekday() \
               and (self.canAfford(club) or self.hasBought(club)) \
               and self.hasPermission(club, avId)

    def canAfford(self, clubContainer):
        if not self.usesJellybeans(clubContainer):
            return clubContainer.getClubCoins() >= self.getCost(clubContainer)
        else:
            return clubContainer.getJellybeans() >= self.getCost(clubContainer)

    def usesJellybeans(self, clubContainer):
        return self.useJellybeans

    def hasBought(self, clubContainer):
        return self in clubContainer.itemsOwned

    def isType(self, clubItemType: ClubItemType) -> bool:
        return self.getType() == clubItemType

    def isRightWeekday(self) -> bool:
        if self.lockWeekday is None:
            return True
        return checkIsDay(weekday=self.lockWeekday)

    """Index setter"""

    def setItemID(self, itemID: int):
        self.itemID = itemID


class ClubItemBooster(ClubItem):

    def getName(self):
        from toontown.inventory.registry.ItemTypeRegistry import getItemDefinition
        return getItemDefinition(self.getValue()).getName()

    def canPurchase(self, club, avId):
        """We cannot purchase the item if we have too many boosters."""
        return super().canPurchase(club, avId) and \
               len(club.getAllBoosters()) < club.getMaxBoosters() and \
               not self.clubHasBooster(club)

    def clubHasBooster(self, clubContainer):
        """Returns True if the clubContainer has a booster of this item's type."""
        boosterType = self.getValue()  # type: BoosterItemType
        return bool(clubContainer.getBoosterOfType(boosterType))

    def storesId(self):
        return False


class ClubItemClubIcon(ClubItem):

    def canPurchase(self, club, avId):
        """We cannot purchase the item if we currently have it equipped on our icon."""
        return super().canPurchase(club, avId) and \
               self.getItemID() not in club.clubIcon.getItemIDs()


class ClubItemClubIconThreatening(ClubItemClubIcon):

    # Sketched made me add this -Main

    def getDescription(self, clubContainer):
        levelRequired = self.getLevelRequired(clubContainer)
        if levelRequired > clubContainer.getClubLevel():
            return TTLocalizer.ClubShopInsufficientLevel % levelRequired
        if random.random() > 0.002:
            return super().getDescription(clubContainer)
        return super().getDescription(clubContainer) + ' Or else.'


class ClubItemMemberSlots(ClubItem):
    """Functionally identical to ClubItem, but cost calculated dynamically"""

    def storesId(self):
        return False

    def getDescription(self, clubContainer):
        levelRequired = self.getLevelRequired(clubContainer)
        if levelRequired > clubContainer.getClubLevel():
            return TTLocalizer.ClubShopInsufficientLevel % levelRequired
        oldMembers = clubContainer.capacity
        if oldMembers == ClubMaxSize:
            return self.description[1]
        cost, newMembers = calculateClubCapacityUpgrade(oldMembers, True)
        return self.description[0] % (oldMembers, newMembers)

    def getCost(self, clubContainer):
        return math.ceil(calculateClubCapacityUpgrade(clubContainer.capacity, False))

    def getLevelRequired(self, clubContainer) -> int:
        upgrade = ClubCapacityUpgrades.get(clubContainer.capacity + 5)
        if upgrade is None:
            return 0
        return upgrade["level"]

    def hasBought(self, clubContainer):
        return clubContainer.capacity == ClubMaxSize

    def canPurchase(self, club, avId):
        return club.capacity != ClubMaxSize \
               and super().canPurchase(club, avId)

    def usesJellybeans(self, clubContainer) -> bool:
        upgrade = ClubCapacityUpgrades.get(clubContainer.capacity + 5)
        if upgrade is None:
            return False
        return upgrade["type"] == ClubCapacityCostType.JBS


class ClubItemBoosterSlots(ClubItem):
    """Functionally identical to ClubItem, but cost calculated dynamically"""

    def storesId(self):
        return False

    def getLevelRequired(self, clubContainer):
        return {
            1: 50,
            2: 100,
            3: 100,
        }.get(clubContainer.getMaxBoosters(), 0)

    def getDescription(self, clubContainer):
        levelRequired = self.getLevelRequired(clubContainer)
        if levelRequired > clubContainer.getClubLevel():
            return TTLocalizer.ClubShopInsufficientLevel % levelRequired
        currentBoosters = clubContainer.getMaxBoosters()
        if currentBoosters == ClubMaxBoosters:
            return self.description[1]
        return self.description[0] % (currentBoosters, currentBoosters + 1)

    def getCost(self, clubContainer):
        return {
            1: 100,
            2: 500,
            3: 1000,
        }.get(clubContainer.getMaxBoosters(), 1000)

    def hasBought(self, clubContainer):
        return clubContainer.getMaxBoosters() == ClubMaxBoosters

    def canPurchase(self, club, avId):
        return club.getMaxBoosters() != ClubMaxBoosters \
               and super().canPurchase(club, avId)


class ClubItemNameChanger(ClubItem):
    """Functionally identical to ClubItem, but purchase calculated dynamically"""

    def storesId(self):
        return False

    @staticmethod
    def hasPermission(clubContainer, avId):
        return clubContainer.isAvIdOwner(avId)

    def canPurchase(self, club, avId):
        return club.nameStatus == ClubNameStatus.NAME_APPROVED \
               and super().canPurchase(club, avId)


class __ClubItemIndex:
    """A container class for all club items."""

    # Default item IDs for club icons.
    ICON_DEFAULTS = [
        # icon imgs
        1, 2, 3, 4, 5, 6, 7, 8,
        # bg imgs
        500, 501, 502, 503, 504, 505, 506, 507,
        # theme cols
        1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007,
        1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017,
        # bg cols
        1500, 1501, 1502, 1503, 1504, 1505, 1506, 1507,
        1510, 1511, 1512, 1513, 1514, 1515, 1516, 1517,
    ]

    def __init__(self, itemDict):
        self.itemDict = itemDict  # type: Dict[int, ClubItem]

        # Add a task hook for all pulsing colors if we're client-sided.
        self.colorPulsers = [idx for idx in self.itemDict if isinstance(self.itemDict[idx].value, ClubColorPulser)]
        if ProcessGlobals.getCurrentProcess() == ProcessGlobals.Process.Client:
            taskMgr.add(self.doColorUpdates, "ClubColorPulsers-update")

        # Populate the item dict.
        for itemID, clubItem in self.itemDict.items():
            clubItem.setItemID(itemID)

        # Post-process.
        for clubItem in self.itemDict.values():
            clubItem.postProcess(self)

    def doColorUpdates(self, task):
        for idx in self.colorPulsers:
            self.itemDict[idx].value.doColorUpdate()
        task.delayTime = 0.05
        return task.again

    """
    Various getters
    """

    def getItem(self, index: int) -> ClubItem:
        """
        Gets an item given an item ID.
        :param index: The item ID to get.
        :return:      A ClubItem dataclass.
        :rtype:       ClubItem
        """
        return self.itemDict.get(index)

    def getItems(self):
        """
        Gets a list of all of the ClubItems.
        :return:      A list of ClubItem dataclasses.
        :rtype:       List[ClubItem]
        """
        return list(self.itemDict.values())

    def getItemsOfIndices(self, indices: list):
        """
        Gets a list of indexed ClubItems.
        :param indices: A list of integers.
        :type  indices: List[int]
        :return:        A list of ClubItem dataclasses.
        :rtype:         List[ClubItem]
        """
        return [self.getItem(index) for index in indices]

    def getItemsOfType(self, type: ClubItemType):
        """
        Gets a list of all items under a certain type.
        :param type: A ClubItemType enum.
        :type  type: ClubItemType
        :return:     A list of ClubItem dataclasses.
        :rtype:      List[ClubItem]
        """
        return [item for item in self.getItems() if item.isType(type)]

    def getItemsOfTypes(self, types: list):
        """
        Gets a list of all items under types.
        :param types: A list of ClubItemTypes.
        :type  types: List[ClubItemType]
        :return:      A list of CLubItem dataclasses.
        :rtype:       List[ClubItem]
        """
        retList = []
        for type in types:
            retList.extend(self.getItemsOfType(type))
        return retList

    def getFilteredItemsOfType(self, type: ClubItemType, indices: list):
        """
        Gets a list of ClubItems under a list of existing indices.
        :param type:    A ClubItemType enum.
        :type  type:    ClubItemType
        :param indices: A list of integers.
        :type  indices: List[int]
        :return:        A list of ClubItem dataclasses.
        :rtype:         List[ClubItem]
        """
        return [item for item in self.getItemsOfIndices(indices) if item.isType(type)]

    def getDefaultsOfType(self, type: ClubItemType):
        """
        Gets a list of all 'default' items under a certain type.
        :param type: A ClubItemType enum.
        :type  type: ClubItemType
        :return:     A list of ClubItem dataclasses.
        :rtype:      List[ClubItem]
        """
        return self.getFilteredItemsOfType(type=type, indices=self.ICON_DEFAULTS)


BTID = 1110  # blank theme col ID
BBIDMATCH = 1115  # the blank them col ID that the BBID matches to
BBID = 1615  # blank bg col ID
ClubNameChangeCost = 300

__IconCoinCost = 1
__IconBeanCost = 1
__ThemeCoinCost = 1
__ThemeBeanCost = 1
__BackgroundCost = 5
__BoosterCoinMult = 1
__BoosterBeanMult = 1000

ClubItemIndex = __ClubItemIndex(itemDict={
    1:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=1,   name='Butterfly',  cost=__IconBeanCost * 500, useJellybeans=True, description='A gentle butterfly.'),
    2:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=2,   name='Doodle',     cost=__IconBeanCost * 500, useJellybeans=True, description='A silly Doodle.'),
    3:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=3,   name='Jellybeans', cost=__IconBeanCost * 500, useJellybeans=True, description='Sweet, sweet Jellybeans.'),
    4:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=4,   name='Popsicle',   cost=__IconBeanCost * 500, useJellybeans=True, description='A sweet popsicle.'),
    5:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=5,   name='Pointer',    cost=__IconBeanCost * 500, useJellybeans=True, description='A glove, pointing up.'),
    6:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=6,   name='Paw Print',  cost=__IconBeanCost * 500, useJellybeans=True, description='A paw print.'),
    7:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=7,   name='Clouds',     cost=__IconBeanCost * 500, useJellybeans=True, description='For when you\'re lost in thought.'),
    8:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=8,   name='Palette',    cost=__IconBeanCost * 500, useJellybeans=True, description='Time to get creative!'),

    9:  ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=12,  name='Ice Cream',   levelRequired=5,  cost=__IconBeanCost * 5000, useJellybeans=True, description='A sweet treat from Toontown Central.'),
    10: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=13,  name='Starfish',    levelRequired=10, cost=__IconBeanCost * 5000, useJellybeans=True, description='A lovely star from Barnacle Boatyard.'),
    11: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=14,  name='Crown',       levelRequired=15, cost=__IconBeanCost * 5000, useJellybeans=True, description='An heirloom from Ye Olde Toontowne.'),
    12: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=15,  name='Flower',      levelRequired=20, cost=__IconBeanCost * 5000, useJellybeans=True, description='A lazy daisy from Daffodil Gardens.'),
    13: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=16,  name='Music Notes', levelRequired=25, cost=__IconBeanCost * 5000, useJellybeans=True, description='A rigid rhythm from Mezzo Melodyland.'),
    14: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=17,  name='Snowflake',   levelRequired=30, cost=__IconBeanCost * 5000, useJellybeans=True, description='A chilling insignia from The Brrrgh.'),
    15: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=18,  name='Acorn',       levelRequired=35, cost=__IconBeanCost * 5000, useJellybeans=True, description='The titular fruit of Acorn Acres.'),
    16: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=19,  name='ZZZ',         levelRequired=40, cost=__IconBeanCost * 5000, useJellybeans=True, description='The sleepy Z\'s of Drowsy Dreamland.'),

    17: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=20,  name='Sun',            levelRequired=25, cost=__IconCoinCost * 75, description='Daytime.'),
    18: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=9,   name='Party Hat',      levelRequired=10, cost=__IconCoinCost * 25, description='Party time!'),
    19: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=10,  name='Trap & Lure',    levelRequired=15, cost=__IconCoinCost * 75, description='A strong combo.'),
    20: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=11,  name='Throw & Squirt', levelRequired=15, cost=__IconCoinCost * 75, description='A classic duo.'),
    21: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=21,  name='Moon',           levelRequired=25, cost=__IconCoinCost * 75, description='Nighttime.'),
    22: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=22,  name='Rabbit',         levelRequired=20, cost=__IconCoinCost * 50, description='Go as fast as you can!'),
    23: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=23,  name='Snail',          levelRequired=20, cost=__IconCoinCost * 50, description='Take it slow.'),
    24: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=24,  name='Turtle',         levelRequired=20, cost=__IconCoinCost * 50, description='Take it REAL slow.'),

    25: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=26,  name='Sellbot Emblem',  levelRequired=50,  cost=__IconCoinCost * 500,     description='You\'re gonna go nuts and bolts for this offer!'),
    26: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=27,  name='Cashbot Emblem',  levelRequired=50,  cost=__IconCoinCost * 500,     description='Crashed by cash... unbelievable.'),
    27: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=28,  name='Lawbot Emblem',   levelRequired=50,  cost=__IconCoinCost * 500,     description='There\'s a storm of legal trouble coming your way.'),
    28: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=29,  name='Bossbot Emblem',  levelRequired=50,  cost=__IconCoinCost * 500,     description='Caddie, I\'ll need my driver!'),
    29: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=30,  name='Boardbot Emblem', levelRequired=50,  cost=__IconCoinCost * 500,     description='You\'re fired.'),
    30: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=25,  name='Toon Resistance', levelRequired=100, cost=__IconBeanCost * 10000000, useJellybeans=True, description='Toons of the World, Unite!'),
    31: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=35,  name='Laff Meter',      levelRequired=15,  cost=__IconBeanCost * 25000,    useJellybeans=True, description='Keep on smilin\'.'),
    32: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=36,  name='Treasure Chest',  levelRequired=30,  cost=__IconBeanCost * 30000,    useJellybeans=True, description='A trove of goodies awaits.'),

    33: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=31,  name='Trolley',       levelRequired=75, cost=__IconCoinCost * 600, description='Let\'s go ride the Trolley!'),
    34: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=32,  name='Fishing',       levelRequired=75, cost=__IconCoinCost * 600, description='One cast away from a Devil Ray.'),
    35: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=33,  name='Golfing',       levelRequired=75, cost=__IconCoinCost * 600, description='I\'ll take a mulligan...'),
    36: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=34,  name='Racing',        levelRequired=75, cost=__IconCoinCost * 600, description='Wow! You are FAST!'),
    37: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=37,  name='Shooting Star', levelRequired=30, cost=__IconCoinCost * 400, description='Wish upon a star.'),
    38: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=41,  name='Autumn Leaves', levelRequired=30, cost=__IconCoinCost * 400, description='The seasons are changing...'),
    39: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=42,  name='Hearts',        levelRequired=30, cost=__IconCoinCost * 400, description='For a lovely club.'),
    40: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=38,  name='Lucky Clover',  levelRequired=30, cost=__IconCoinCost * 400, description='For a lucky club.'),

    100: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=46,  name=BattleGlobalAvPropStrings[0][0], levelRequired=20,  cost=__IconCoinCost * 50,    description='For tickling your funnybone.'),
    101: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=47,  name=BattleGlobalAvPropStrings[0][1], levelRequired=40,  cost=__IconCoinCost * 175,   description='Everyone\'s a comedian!'),
    102: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=48,  name=BattleGlobalAvPropStrings[0][2], levelRequired=60,  cost=__IconCoinCost * 400,   description='Pucker up!'),
    103: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=49,  name=BattleGlobalAvPropStrings[0][3], levelRequired=80,  cost=__IconCoinCost * 1000,  description='Hope you brought tap shoes!'),
    104: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=50,  name=BattleGlobalAvPropStrings[0][4], levelRequired=100, cost=__IconCoinCost * 2000,  description='Caution: Does NOT allow you to fly.'),
    105: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=51,  name=BattleGlobalAvPropStrings[0][5], levelRequired=120, cost=__IconCoinCost * 4000,  description='It\'s more difficult than it looks.'),
    106: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=52,  name=BattleGlobalAvPropStrings[0][6], levelRequired=135, cost=__IconCoinCost * 6000,  description='Get ready to PAR-TAY!'),
    107: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=53,  name=BattleGlobalAvPropStrings[0][7], levelRequired=150, cost=__IconCoinCost * 10000, description='Also useful for repairing roofs.'),
    108: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=54,  name=BattleGlobalAvPropStrings[1][0], levelRequired=20,  cost=__IconCoinCost * 50,    description='It\'ll make a monkey outta anyone!'),
    109: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=55,  name=BattleGlobalAvPropStrings[1][1], levelRequired=40,  cost=__IconCoinCost * 175,   description='Goes great with autumn leaves.'),
    110: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=56,  name=BattleGlobalAvPropStrings[1][2], levelRequired=60,  cost=__IconCoinCost * 400,   description='BOING!'),
    111: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=57,  name=BattleGlobalAvPropStrings[1][3], levelRequired=80,  cost=__IconCoinCost * 1000,  description='Don\'t lose them!'),
    112: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=58,  name=BattleGlobalAvPropStrings[1][4], levelRequired=100, cost=__IconCoinCost * 2000,  description='Get it before it\'s gone!'),
    113: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=59,  name=BattleGlobalAvPropStrings[1][5], levelRequired=120, cost=__IconCoinCost * 4000,  description='Looks pretty a-DOOR-able to me!'),
    114: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=60,  name=BattleGlobalAvPropStrings[1][6], levelRequired=135, cost=__IconCoinCost * 6000,  description='Become a one-Toon demolition master!'),
    115: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=61,  name=BattleGlobalAvPropStrings[1][7], levelRequired=150, cost=__IconCoinCost * 10000, description='Also great for gold mining!'),
    116: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=62,  name=BattleGlobalAvPropStrings[2][0], levelRequired=20,  cost=__IconCoinCost * 50,    description='Times are hard.'),
    117: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=63,  name=BattleGlobalAvPropStrings[2][1], levelRequired=40,  cost=__IconCoinCost * 175,   description='Maybe you can pick up some coins under the couch!'),
    118: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=64,  name=BattleGlobalAvPropStrings[2][2], levelRequired=60,  cost=__IconCoinCost * 400,   description='Hey, it\'s a step up!'),
    119: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=65,  name=BattleGlobalAvPropStrings[2][3], levelRequired=80,  cost=__IconCoinCost * 1000,  description='Now you\'re a real metal attractor!'),
    120: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=66,  name=BattleGlobalAvPropStrings[2][4], levelRequired=100, cost=__IconCoinCost * 2000,  description='Moving up in the world!'),
    121: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=67,  name=BattleGlobalAvPropStrings[2][5], levelRequired=120, cost=__IconCoinCost * 4000,  description='You are getting veeeery sleepy...'),
    122: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=68,  name=BattleGlobalAvPropStrings[2][6], levelRequired=135, cost=__IconCoinCost * 6000,  description='Top of the leagues!'),
    123: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=69,  name=BattleGlobalAvPropStrings[2][7], levelRequired=150, cost=__IconCoinCost * 10000, description='It\'ll make anyone fall asleep.'),
    124: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=70,  name=BattleGlobalAvPropStrings[3][0], levelRequired=20,  cost=__IconCoinCost * 50,    description='Great for song covers!'),
    125: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=72,  name=BattleGlobalAvPropStrings[3][1], levelRequired=40,  cost=__IconCoinCost * 175,   description='Honk honk!'),
    126: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=71,  name=BattleGlobalAvPropStrings[3][2], levelRequired=60,  cost=__IconCoinCost * 400,   description='It\'ll rattle your eardrums!'),
    127: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=73,  name=BattleGlobalAvPropStrings[3][3], levelRequired=80,  cost=__IconCoinCost * 1000,  description='It\'s military grade!'),
    128: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=74,  name=BattleGlobalAvPropStrings[3][4], levelRequired=100, cost=__IconCoinCost * 2000,  description='Pretty old-fashioned.'),
    129: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=75,  name=BattleGlobalAvPropStrings[3][5], levelRequired=120, cost=__IconCoinCost * 4000,  description='It\'ll never forget!'),
    130: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=76,  name=BattleGlobalAvPropStrings[3][6], levelRequired=135, cost=__IconCoinCost * 6000,  description='For calling all your favorite ships.'),
    131: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=77,  name=BattleGlobalAvPropStrings[3][7], levelRequired=150, cost=__IconCoinCost * 10000, description='A classic!'),
    132: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=78,  name=BattleGlobalAvPropStrings[4][0], levelRequired=20,  cost=__IconCoinCost * 50,    description='Sofie will be pleased.'),
    133: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=79,  name=BattleGlobalAvPropStrings[4][1], levelRequired=40,  cost=__IconCoinCost * 175,   description='Hydration check!'),
    134: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=80,  name=BattleGlobalAvPropStrings[4][2], levelRequired=60,  cost=__IconCoinCost * 400,   description='Reach for the sky!'),
    135: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=81,  name=BattleGlobalAvPropStrings[4][3], levelRequired=80,  cost=__IconCoinCost * 1000,  description='A staple of summertime fun!'),
    136: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=82,  name=BattleGlobalAvPropStrings[4][4], levelRequired=100, cost=__IconCoinCost * 2000,  description='Care for a drink?'),
    137: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=83,  name=BattleGlobalAvPropStrings[4][5], levelRequired=120, cost=__IconCoinCost * 4000,  description='Fight fire with... firehose!'),
    138: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=84,  name=BattleGlobalAvPropStrings[4][6], levelRequired=135, cost=__IconCoinCost * 6000,  description='Hope you brought an umbrella!'),
    139: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=85,  name=BattleGlobalAvPropStrings[4][7], levelRequired=150, cost=__IconCoinCost * 10000, description='They call it Ol\' Faithful.'),
    140: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=86,  name=BattleGlobalAvPropStrings[5][0], levelRequired=20,  cost=__IconCoinCost * 50,    description='Shake my hand!'),
    141: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=87,  name=BattleGlobalAvPropStrings[5][1], levelRequired=40,  cost=__IconCoinCost * 175,   description='I\'ve got a bright idea!'),
    142: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=88,  name=BattleGlobalAvPropStrings[5][2], levelRequired=60,  cost=__IconCoinCost * 400,   description='Play those tunes!'),
    143: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=89,  name=BattleGlobalAvPropStrings[5][3], levelRequired=80,  cost=__IconCoinCost * 1000,  description='Someone\'s kart won\'t be running today...'),
    144: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=90,  name=BattleGlobalAvPropStrings[5][4], levelRequired=100, cost=__IconCoinCost * 2000,  description='Take a glance at the electricity channel!'),
    145: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=91,  name=BattleGlobalAvPropStrings[5][5], levelRequired=120, cost=__IconCoinCost * 4000,  description='Lights! Camera! Action!'),
    146: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=92,  name=BattleGlobalAvPropStrings[5][6], levelRequired=135, cost=__IconCoinCost * 6000,  description='It\'s like making your own lightning!'),
    147: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=93,  name=BattleGlobalAvPropStrings[5][7], levelRequired=150, cost=__IconCoinCost * 10000, description='The king of the skies.'),
    148: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=94,  name=BattleGlobalAvPropStrings[6][0], levelRequired=20,  cost=__IconCoinCost * 50,    description='Yum, pink!'),
    149: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=95,  name=BattleGlobalAvPropStrings[6][1], levelRequired=40,  cost=__IconCoinCost * 175,   description='Now with extra snozzberry!'),
    150: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=96,  name=BattleGlobalAvPropStrings[6][2], levelRequired=60,  cost=__IconCoinCost * 400,   description='Hope you like frosting.'),
    151: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=97,  name=BattleGlobalAvPropStrings[6][3], levelRequired=80,  cost=__IconCoinCost * 1000,  description='Blow out the candle and make a wish!'),
    152: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=98,  name=BattleGlobalAvPropStrings[6][4], levelRequired=100, cost=__IconCoinCost * 2000,  description='It\'s technically healthy. Right?'),
    153: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=99,  name=BattleGlobalAvPropStrings[6][5], levelRequired=120, cost=__IconCoinCost * 4000,  description='Splat!'),
    154: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=100, name=BattleGlobalAvPropStrings[6][6], levelRequired=135, cost=__IconCoinCost * 6000,  description='Happy birthday to you!'),
    155: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=101, name=BattleGlobalAvPropStrings[6][7], levelRequired=150, cost=__IconCoinCost * 10000, description='It\'s gotta be perfect!'),
    156: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=102, name=BattleGlobalAvPropStrings[7][0], levelRequired=20,  cost=__IconCoinCost * 50,    description='That poor little flower.'),
    157: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=103, name=BattleGlobalAvPropStrings[7][1], levelRequired=40,  cost=__IconCoinCost * 175,   description='Quicker than quicksand!'),
    158: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=104, name=BattleGlobalAvPropStrings[7][2], levelRequired=60,  cost=__IconCoinCost * 400,   description='Strike!'),
    159: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=105, name=BattleGlobalAvPropStrings[7][3], levelRequired=80,  cost=__IconCoinCost * 1000,  description='A favorite of blacksmiths.'),
    160: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=106, name=BattleGlobalAvPropStrings[7][4], levelRequired=100, cost=__IconCoinCost * 2000,  description='But how much does it weigh?'),
    161: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=107, name=BattleGlobalAvPropStrings[7][5], levelRequired=120, cost=__IconCoinCost * 4000,  description='Safe-ty first!'),
    162: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=108, name=BattleGlobalAvPropStrings[7][6], levelRequired=135, cost=__IconCoinCost * 6000,  description='It\'ll make you a little BOLDER!'),
    163: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=109, name=BattleGlobalAvPropStrings[7][7], levelRequired=150, cost=__IconCoinCost * 10000, description='Well, it\'s no Mozart...'),

    200: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=39,  name='Pumpkin',       levelRequired=75, useJellybeans=True, cost=__IconBeanCost * 50000, description='For a spooky club.'),
    201: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=42,  name='Hearts',        levelRequired=60, useJellybeans=True, cost=__IconBeanCost * 50000, description='For a lovely club.'),
    202: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=43,  name='Fireworks',     levelRequired=60, useJellybeans=True, cost=__IconBeanCost * 50000, description='For a combustible club.'),
    203: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=40,  name='Toonsmas Tree', levelRequired=75, useJellybeans=True, cost=__IconBeanCost * 50000, description='For a festive club.'),
    204: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=44,  name='Easter Egg',    levelRequired=50, useJellybeans=True, cost=__IconBeanCost * 50000, description='A decorative egg.'),
    205: ClubItemClubIcon(type=ClubItemType.CLUB_ICON, value=45,  name='Easter Basket', levelRequired=50, useJellybeans=True, cost=__IconBeanCost * 50000, description='Several decorative eggs.'),

    ##############################

    500: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=1,  name='Horizontal Stripes',   description='Some simple stripes for your Club Icon.', cost=250, useJellybeans=True,),
    501: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=2,  name='Vertical Stripes',     description='Some simple stripes for your Club Icon.', cost=250, useJellybeans=True,),
    502: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=3,  name='Diagonal Stripes A',   description='Some simple stripes for your Club Icon.', cost=250, useJellybeans=True,),
    503: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=4,  name='Diagonal Stripes B',   description='Some simple stripes for your Club Icon.', cost=250, useJellybeans=True,),
    504: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=5,  name='Horizontal Stroke',    description='Some simple stripes for your Club Icon.', cost=250, useJellybeans=True,),
    505: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=6,  name='Vertical Stroke',      description='Some simple stripes for your Club Icon.', cost=250, useJellybeans=True,),
    506: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=7,  name='Diagonal Stroke A',    description='Some simple stripes for your Club Icon.', cost=250, useJellybeans=True,),
    507: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=8,  name='Diagonal Stroke B',    description='Some simple stripes for your Club Icon.', cost=250, useJellybeans=True,),

    510: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=9,  name='Polka-Dots',       description='Some polka-dots to speckle on your Club Icon.',                cost=6000, useJellybeans=True, levelRequired=5),
    511: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=10, name='Faded Polka-Dots', description='Some polka-dots to speckle on your Club Icon.',                cost=6000, useJellybeans=True, levelRequired=5),
    512: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=15, name='Horizontal Fade',  description='A subtle color gradient for your Club Icon.',                  cost=10000, useJellybeans=True, levelRequired=15),
    513: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=14, name='Vertical Fade',    description='A subtle color gradient for your Club Icon.',                  cost=10000, useJellybeans=True, levelRequired=15),
    514: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=11, name='Circle Ring',      description='A ring of circles to line your Club Icon.',                    cost=7500, useJellybeans=True, levelRequired=10),
    515: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=12, name='Line Ring',        description='A ring of lines to line your Club Icon.',                      cost=7500, useJellybeans=True, levelRequired=10),
    516: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=13, name='X Ring',           description='A ring of X\'s to line your Club Icon.',                       cost=7500, useJellybeans=True, levelRequired=10),
    517: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=37, name='Embroidered',      description='A fancy, embroidered ring of X\'s to line your Club Icon.',    cost=14000, useJellybeans=True, levelRequired=10),

    520: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=17, name='Horizontal Semicircle',    description='A perfect semicircle to divide your Club Icon.',       cost=50000, useJellybeans=True, levelRequired=30),
    521: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=16, name='Vertical Semicircle',      description='A perfect semicircle to divide your Club Icon.',       cost=50000, useJellybeans=True, levelRequired=30),
    522: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=18, name='Rings',                    description='Some rings to apply onto your Club Icon.',             cost=175000, useJellybeans=True, levelRequired=40),
    523: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=19, name='Inverted Rings',           description='A unique ring pattern for your Club Icon.',            cost=250000, useJellybeans=True, levelRequired=50),
    524: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=20, name='Horizontal Zig-Zag',       description='A horizontal, zig-zag pattern for your Club Icon.',    cost=40000,  useJellybeans=True, levelRequired=35),
    525: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=21, name='Vertical Zig-Zag',         description='A vertical, zig-zag pattern for your Club Icon.',      cost=40000,  useJellybeans=True, levelRequired=35),
    526: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=22, name='Horizontal Serpentine',    description='A horizontal, serpentine pattern for your Club Icon.', cost=30000,  useJellybeans=True, levelRequired=30),
    527: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=23, name='Vertical Serpentine',      description='A vertical, serpentine pattern for your Club Icon.',   cost=30000,  useJellybeans=True, levelRequired=30),

    530: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=25, name='Heart Stencil',        description='A stencil pattern for your Club Icon.', cost=10, levelRequired=15),
    531: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=26, name='Spade Stencil',        description='A stencil pattern for your Club Icon.', cost=10, levelRequired=15),
    532: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=27, name='Club Stencil',         description='A stencil pattern for your Club Icon.', cost=10, levelRequired=15),
    533: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=28, name='Diamond Stencil',      description='A stencil pattern for your Club Icon.', cost=10, levelRequired=15),
    534: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=29, name='Circle Stencil',       description='A stencil pattern for your Club Icon.', cost=10, levelRequired=15),
    535: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=30, name='Triangle Stencil',     description='A stencil pattern for your Club Icon.', cost=10, levelRequired=15),
    536: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=31, name='Star Stencil',         description='A stencil pattern for your Club Icon.', cost=10, levelRequired=15),
    537: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=32, name='Soft Star Stencil',    description='A stencil pattern for your Club Icon.', cost=10, levelRequired=15),

    540: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=24, name='Gear Stencil',     description='A stencil pattern for your Club Icon.',     cost=30, levelRequired=35),
    541: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=33, name='X Stencil',        description='A stencil pattern for your Club Icon.',     cost=30, levelRequired=35),
    542: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=34, name='Square Stencil',   description='A stencil pattern for your Club Icon.',     cost=30, levelRequired=35),
    543: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=38, name='Explosion',        description='An explosion pattern for your Club Icon!',  cost=35, levelRequired=35),
    544: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=35, name='Checkerboard',     description='A checkerboard background pattern.',        cost=3500000, useJellybeans=True, levelRequired=50),
    545: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=36, name='Mosaic',           description='A mosaic background pattern.',              cost=3500000, useJellybeans=True, levelRequired=50),
    546: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=39, name='Spikes',           description='A pattern consisting of interior spikes.',  cost=4000000, useJellybeans=True, levelRequired=55),
    547: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=40, name='Spiral',           description='A spiral pattern.',                         cost=4000000, useJellybeans=True, levelRequired=55),

    550: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=41, name='Strong Ring',  description='A bold ring for your Club Icon.',              cost=5000000, useJellybeans=True, levelRequired=60),
    551: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=42, name='Clouds',       description='Overcast weather for your Club Icon.',         cost=5000000, useJellybeans=True, levelRequired=60),
    552: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=44, name='Linked',       description='A linked pattern for your Club Icon.',         cost=10000000, useJellybeans=True, levelRequired=70),
    553: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=45, name='Jigsaw',       description='Puzzle pieces for your Club Icon.',            cost=10000000, useJellybeans=True, levelRequired=70),
    554: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=46, name='Shrubbery',    description='Some tidy shubbery lining your Club Icon.',    cost=15000000, useJellybeans=True, levelRequired=80),
    555: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=43, name='Chevron',      description='A unique chevron for your Club Icon.',         cost=15000000, useJellybeans=True, levelRequired=80),
    556: ClubItemClubIcon(type=ClubItemType.CLUB_BACKGROUND, value=47, name='Diamonds',     description='Fancy diamonds for your Club Icon.',           cost=15000000, useJellybeans=True, levelRequired=80),

    ##############################

    1000: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cc2d2d'), name='Basic Red',           cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1001: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cd682d'), name='Basic Orange',        cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1002: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cda52d'), name='Basic Orange-Yellow', cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1003: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('bacd2d'), name='Basic Yellow',        cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1004: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('7dcd2d'), name='Basic Yellow-Green',  cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1005: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('42cd2d'), name='Basic Green',         cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1006: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('2dcd55'), name='Basic Blue-Green',    cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1007: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('2dcd90'), name='Basic Bluer-Green',   cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),

    1010: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('2dcdcd'), name='Basic Blue',          cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1011: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('2d92cd'), name='Basic Sky Blue',      cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1012: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('2d55cd'), name='Basic Violet-Blue',   cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1013: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('402dcd'), name='Basic Indigo',        cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1014: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('7d2dcd'), name='Basic Purple',        cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1015: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('b82dcd'), name='Basic Magenta',       cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1016: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cd2da5'), name='Basic Pink',          cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),
    1017: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cd2d6a'), name='Basic Rose Red',      cost=__ThemeCoinCost * 5, description='A basic color for your Club.'),

    1020: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('f4cccc'), name='Light Red', cost=__ThemeCoinCost * 20, description='A lovely shade of red for your Club.'),
    1021: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('ea9999'), name='Salmon', cost=__ThemeCoinCost * 20, description='A lovely shade of red for your Club.'),
    1022: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('e06666'), name='Candy', cost=__ThemeCoinCost * 20, description='A lovely shade of red for your Club.'),
    1023: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cc3d3d'), name='Jasper', cost=__ThemeCoinCost * 20, description='A lovely shade of red for your Club.'),
    1024: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('ab2222'), name='Firebrick', cost=__ThemeCoinCost * 20, description='A lovely shade of red for your Club.'),
    1025: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('7d0e0e'), name='Maroon', cost=__ThemeCoinCost * 20, description='A lovely shade of red for your Club.'),
    1026: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('590606'), name='Rosewood', cost=__ThemeCoinCost * 20, description='A lovely shade of red for your Club.'),
    1027: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('330202'), name='Dark Chocolate', cost=__ThemeCoinCost * 20, description='A lovely shade of red for your Club.'),

    1030: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('f4e0cd'), name='Almond', cost=__ThemeCoinCost * 20, description='A lovely shade of orange for your Club.'),
    1031: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('eac299'), name='Khaki', cost=__ThemeCoinCost * 20, description='A lovely shade of orange for your Club.'),
    1032: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('e0a467'), name='Fawn', cost=__ThemeCoinCost * 20, description='A lovely shade of orange for your Club.'),
    1033: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cc853e'), name='Oak', cost=__ThemeCoinCost * 20, description='A lovely shade of orange for your Club.'),
    1034: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('aa6622'), name='Light Brown', cost=__ThemeCoinCost * 20, description='A lovely shade of orange for your Club.'),
    1035: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('7c450e'), name='Sepia', cost=__ThemeCoinCost * 20, description='A lovely shade of orange for your Club.'),
    1036: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('5b3106'), name='Chocolate', cost=__ThemeCoinCost * 20, description='A lovely shade of orange for your Club.'),
    1037: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('311a02'), name='Brown', cost=__ThemeCoinCost * 20, description='A lovely shade of orange for your Club.'),

    1040: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('f4efcd'), name='Beige', cost=__ThemeCoinCost * 20, description='A lovely shade of yellow for your Club.'),
    1041: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('eadf99'), name='Blond', cost=__ThemeCoinCost * 20, description='A lovely shade of yellow for your Club.'),
    1042: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('e0d067'), name='Flax', cost=__ThemeCoinCost * 20, description='A lovely shade of yellow for your Club.'),
    1043: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('ccb93e'), name='Sandstorm', cost=__ThemeCoinCost * 20, description='A lovely shade of yellow for your Club.'),
    1044: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('aa9822'), name='Gold', cost=__ThemeCoinCost * 20, description='A lovely shade of yellow for your Club.'),
    1045: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('7c6d0e'), name='Brass', cost=__ThemeCoinCost * 20, description='A lovely shade of yellow for your Club.'),
    1046: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('5b5006'), name='Bronze', cost=__ThemeCoinCost * 20, description='A lovely shade of yellow for your Club.'),
    1047: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('312b02'), name='Olive', cost=__ThemeCoinCost * 20, description='A lovely shade of yellow for your Club.'),

    1050: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cdf4cd'), name='Mint', cost=__ThemeCoinCost * 20, description='A lovely shade of green for your Club.'),
    1051: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('99ea99'), name='Tea', cost=__ThemeCoinCost * 20, description='A lovely shade of green for your Club.'),
    1052: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('67e067'), name='Lime', cost=__ThemeCoinCost * 20, description='A lovely shade of green for your Club.'),
    1053: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('3ecc3e'), name='Emerald', cost=__ThemeCoinCost * 20, description='A lovely shade of green for your Club.'),
    1054: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('22aa22'), name='Cactus', cost=__ThemeCoinCost * 20, description='A lovely shade of green for your Club.'),
    1055: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('0e7c0e'), name='Forest', cost=__ThemeCoinCost * 20, description='A lovely shade of green for your Club.'),
    1056: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('065b06'), name='Royal Green', cost=__ThemeCoinCost * 20, description='A lovely shade of green for your Club.'),
    1057: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('023102'), name='Dark Green', cost=__ThemeCoinCost * 20, description='A lovely shade of green for your Club.'),

    1060: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cdf4e7'), name='Ice Blue', cost=__ThemeCoinCost * 20, description='A lovely shade of cyan for your Club.'),
    1061: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('99eacf'), name='Sea Foam', cost=__ThemeCoinCost * 20, description='A lovely shade of cyan for your Club.'),
    1062: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('67e0b8'), name='Aquamarine', cost=__ThemeCoinCost * 20, description='A lovely shade of cyan for your Club.'),
    1063: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('3ecc9c'), name='Turquoise', cost=__ThemeCoinCost * 20, description='A lovely shade of cyan for your Club.'),
    1064: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('22aa7d'), name='Eucalyptus', cost=__ThemeCoinCost * 20, description='A lovely shade of cyan for your Club.'),
    1065: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('0e7c57'), name='Viridian', cost=__ThemeCoinCost * 20, description='A lovely shade of cyan for your Club.'),
    1066: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('065b3f'), name='Malachite', cost=__ThemeCoinCost * 20, description='A lovely shade of cyan for your Club.'),
    1067: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('023121'), name='Deep Cyan', cost=__ThemeCoinCost * 20, description='A lovely shade of cyan for your Club.'),

    1070: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cde7f4'), name='Chrome', cost=__ThemeCoinCost * 20, description='A lovely shade of blue for your Club.'),
    1071: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('99cfea'), name='Cornflower', cost=__ThemeCoinCost * 20, description='A lovely shade of blue for your Club.'),
    1072: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('67b8e0'), name='Cyan', cost=__ThemeCoinCost * 20, description='A lovely shade of blue for your Club.'),
    1073: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('3e9ccc'), name='Electric Blue', cost=__ThemeCoinCost * 20, description='A lovely shade of blue for your Club.'),
    1074: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('227daa'), name='Blue Steel', cost=__ThemeCoinCost * 20, description='A lovely shade of blue for your Club.'),
    1075: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('0e577c'), name='Glacier', cost=__ThemeCoinCost * 20, description='A lovely shade of blue for your Club.'),
    1076: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('063f5b'), name='Blue Silk', cost=__ThemeCoinCost * 20, description='A lovely shade of blue for your Club.'),
    1077: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('022131'), name='Deep Blue', cost=__ThemeCoinCost * 20, description='A lovely shade of blue for your Club.'),

    1080: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cdcdf4'), name='Periwinkle', cost=__ThemeCoinCost * 20, description='A lovely shade of indigo for your Club.'),
    1081: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('9999ea'), name='Light Blue', cost=__ThemeCoinCost * 20, description='A lovely shade of indigo for your Club.'),
    1082: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('6767e0'), name='Royal Blue', cost=__ThemeCoinCost * 20, description='A lovely shade of indigo for your Club.'),
    1083: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('3e3ecc'), name='Breeze', cost=__ThemeCoinCost * 20, description='A lovely shade of indigo for your Club.'),
    1084: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('2222aa'), name='Sapphire', cost=__ThemeCoinCost * 20, description='A lovely shade of indigo for your Club.'),
    1085: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('0e0e7c'), name='Cobalt', cost=__ThemeCoinCost * 20, description='A lovely shade of indigo for your Club.'),
    1086: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('06065b'), name='Navy', cost=__ThemeCoinCost * 20, description='A lovely shade of indigo for your Club.'),
    1087: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('020231'), name='Deep Ocean', cost=__ThemeCoinCost * 20, description='A lovely shade of indigo for your Club.'),

    1090: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('e7cdf4'), name='Lavender', cost=__ThemeCoinCost * 20, description='A lovely shade of violet for your Club.'),
    1091: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cf99ea'), name='Lilac', cost=__ThemeCoinCost * 20, description='A lovely shade of violet for your Club.'),
    1092: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('b767e0'), name='Amethyst', cost=__ThemeCoinCost * 20, description='A lovely shade of violet for your Club.'),
    1093: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('9d3ecc'), name='Purple', cost=__ThemeCoinCost * 20, description='A lovely shade of violet for your Club.'),
    1094: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('7d22aa'), name='Grape', cost=__ThemeCoinCost * 20, description='A lovely shade of violet for your Club.'),
    1095: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('570e7c'), name='Midnight ', cost=__ThemeCoinCost * 20, description='A lovely shade of violet for your Club.'),
    1096: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('3f065b'), name='Clairvoyant', cost=__ThemeCoinCost * 20, description='A lovely shade of violet for your Club.'),
    1097: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('210231'), name='New Moon', cost=__ThemeCoinCost * 20, description='A lovely shade of violet for your Club.'),

    1100: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('f4cde7'), name='Orchid', cost=__ThemeCoinCost * 20, description='A lovely shade of pink for your Club.'),
    1101: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('ea99cf'), name='Pink', cost=__ThemeCoinCost * 20, description='A lovely shade of pink for your Club.'),
    1102: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('e067b7'), name='Bubble Gum', cost=__ThemeCoinCost * 20, description='A lovely shade of pink for your Club.'),
    1103: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('cc3e9c'), name='Fuchsia', cost=__ThemeCoinCost * 20, description='A lovely shade of pink for your Club.'),
    1104: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('aa227d'), name='Violet', cost=__ThemeCoinCost * 20, description='A lovely shade of pink for your Club.'),
    1105: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('7c0e57'), name='Plum', cost=__ThemeCoinCost * 20, description='A lovely shade of pink for your Club.'),
    1106: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('5b063f'), name='Velvet', cost=__ThemeCoinCost * 20, description='A lovely shade of pink for your Club.'),
    1107: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('310221'), name='Blackberry', cost=__ThemeCoinCost * 20, description='A lovely shade of pink for your Club.'),

    BTID: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('ffffff'), name='Snow', cost=__ThemeCoinCost * 30, description='As white as snow.'),
    1111: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('dddddd'), name='Aluminum', cost=__ThemeCoinCost * 30, description='A metallic gray.'),
    1112: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('bbbbbb'), name='Silver', cost=__ThemeCoinCost * 30, description='A metallic gray.'),
    1113: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('999999'), name='Gray', cost=__ThemeCoinCost * 30, description='A nice gray color.'),
    1114: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('777777'), name='Nickel', cost=__ThemeCoinCost * 30, description='A metallic gray.'),
    1115: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('555555'), name='Dark Gray', cost=__ThemeCoinCost * 30, description='A darker gray color.'),
    1116: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('333333'), name='Charcoal', cost=__ThemeCoinCost * 30, description='A very dark gray color.'),
    1117: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('111111'), name='Black', cost=__ThemeCoinCost * 30, description='Dark as the night.'),

    1120: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('d294ff'), name='Toon-Up', cost=__ThemeCoinCost * 50, description='The Toon-Up Gag Track color!'),
    1121: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('ff5050'), name='Trap', cost=__ThemeCoinCost * 50, description='The Trap Gag Track color!'),
    1122: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('50be4c'), name='Lure', cost=__ThemeCoinCost * 50, description='The Lure Gag Track color!'),
    1123: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('5d6cef'), name='Sound', cost=__ThemeCoinCost * 50, description='The Sound Gag Track color!'),
    1124: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('ff41c6'), name='Squirt', cost=__ThemeCoinCost * 50, description='The Squirt Gag Track color!'),
    1125: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('f9ff5d'), name='Zap', cost=__ThemeCoinCost * 50, description='The Zap Gag Track color!'),
    1126: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('ff9142'), name='Throw', cost=__ThemeCoinCost * 50, description='The Throw Gag Track color!'),
    1127: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColor('43f2ff'), name='Drop', cost=__ThemeCoinCost * 50, description='The Drop Gag Track color!'),

    1130: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('eb4d4d', 3.0), ('eb8f4d', 3.0))), name='Flames',    levelRequired=50, cost=__ThemeCoinCost * 200, description='A flaming color blend.'),
    1131: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('eb8f4d', 3.0), ('ebdb4d', 3.0))), name='Sunrise',   levelRequired=50, cost=__ThemeCoinCost * 200, description='A color blend for a sunrise.'),
    1132: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('ebdb4d', 3.0), ('6deb4d', 3.0))), name='Knowledge', levelRequired=50, cost=__ThemeCoinCost * 200, description='A blend of knowledge.'),
    1133: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('6deb4d', 3.0), ('4debe3', 3.0))), name='Nature',    levelRequired=50, cost=__ThemeCoinCost * 200, description='Nature, condensed into a color blend.'),
    1134: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('4debe3', 3.0), ('4d72eb', 3.0))), name='Ocean',     levelRequired=50, cost=__ThemeCoinCost * 200, description='A color blend of the ocean.'),
    1135: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('4d72eb', 3.0), ('a74deb', 3.0))), name='Twilight',  levelRequired=50, cost=__ThemeCoinCost * 200, description='Twilight\'s blend of colors.'),
    1136: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('a74deb', 3.0), ('eb4d4d', 3.0))), name='Bloom',     levelRequired=50, cost=__ThemeCoinCost * 200, description='A blooming blend of colors.'),
    1137: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('bbbbbb', 3.0), ('555555', 3.0))), name='Mid-Range', levelRequired=50, cost=__ThemeCoinCost * 200, description='A blend for a midrange of grays.'),

    1140: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('f28888', 3.0), ('f2b488', 3.0))), name='Bright Flames',    levelRequired=50, cost=__ThemeCoinCost * 200, description='A bright, flaming color blend.'),
    1141: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('f2b488', 3.0), ('f2e788', 3.0))), name='Bright Sunrise',   levelRequired=50, cost=__ThemeCoinCost * 200, description='A color blend for a bright sunrise.'),
    1142: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('f2e788', 3.0), ('9df288', 3.0))), name='Bright Knowledge', levelRequired=50, cost=__ThemeCoinCost * 200, description='A blend of bright knowledge.'),
    1143: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('9df288', 3.0), ('88f2ec', 3.0))), name='Bright Nature',    levelRequired=50, cost=__ThemeCoinCost * 200, description='Nature, condensed into a bright color blend.'),
    1144: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('88f2ec', 3.0), ('88a0f2', 3.0))), name='Bright Ocean',     levelRequired=50, cost=__ThemeCoinCost * 200, description='A bright color blend of the ocean.'),
    1145: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('88a0f2', 3.0), ('c488f2', 3.0))), name='Bright Twilight',  levelRequired=50, cost=__ThemeCoinCost * 200, description='Twilight\'s bright blend of colors.'),
    1146: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('c488f2', 3.0), ('f28888', 3.0))), name='Bright Bloom',     levelRequired=50, cost=__ThemeCoinCost * 200, description='A blooming blend of bright colors.'),
    1147: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('ffffff', 6.0), ('999999', 6.0))), name='Light Grays',      levelRequired=50, cost=__ThemeCoinCost * 200, description='A blend for a midrange of light grays.'),

    1150: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('730d0d', 3.0), ('73370d', 3.0))), name='Deep Flames',    levelRequired=50, cost=__ThemeCoinCost * 200, description='A deep, flaming color blend.'),
    1151: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('73370d', 3.0), ('73690d', 3.0))), name='Deep Sunrise',   levelRequired=50, cost=__ThemeCoinCost * 200, description='A color blend for a (paradoxically dim) sunrise.'),
    1152: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('73690d', 3.0), ('21730d', 3.0))), name='Deep Knowledge', levelRequired=50, cost=__ThemeCoinCost * 200, description='A blend of deep knowledge.'),
    1153: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('21730d', 3.0), ('0d736e', 3.0))), name='Deep Nature',    levelRequired=50, cost=__ThemeCoinCost * 200, description='Nature, condensed into a deep color blend.'),
    1154: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('0d736e', 3.0), ('0d2573', 3.0))), name='Deep Ocean',     levelRequired=50, cost=__ThemeCoinCost * 200, description='A deep color blend of the ocean.'),
    1155: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('0d2573', 3.0), ('470d73', 3.0))), name='Deep Twilight',  levelRequired=50, cost=__ThemeCoinCost * 200, description='Twilight\'s dark blend of colors.'),
    1156: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('470d73', 3.0), ('730d0d', 3.0))), name='Deep Bloom',     levelRequired=50, cost=__ThemeCoinCost * 200, description='A blooming blend of deep colors.'),
    1157: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('777777', 6.0), ('111111', 6.0))), name='Dark Grays',     levelRequired=50, cost=__ThemeCoinCost * 200, description='A blend for a midrange of dark grays.'),

    1160: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('fe0000', 3.0), ('fd8c00', 3.0))), name='True Flames',    levelRequired=65, cost=__ThemeCoinCost * 300, description='A true, flaming color blend.'),
    1161: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('fd8c00', 3.0), ('ffe500', 3.0))), name='True Sunrise',   levelRequired=65, cost=__ThemeCoinCost * 300, description='A color blend for a true sunrise.'),
    1162: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('ffe500', 3.0), ('15e80c', 3.0))), name='True Knowledge', levelRequired=65, cost=__ThemeCoinCost * 300, description='A blend of true knowledge.'),
    1163: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('15e80c', 3.0), ('00d2f7', 3.0))), name='True Nature',    levelRequired=65, cost=__ThemeCoinCost * 300, description='Nature, condensed into a true color blend.'),
    1164: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('00d2f7', 3.0), ('5610e3', 3.0))), name='True Ocean',     levelRequired=65, cost=__ThemeCoinCost * 300, description='A true  color blend of the ocean.'),
    1165: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('5610e3', 3.0), ('bf0dde', 3.0))), name='True Twilight',  levelRequired=65, cost=__ThemeCoinCost * 300, description='Twilight\'s true blend of colors.'),
    1166: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('bf0dde', 3.0), ('fe0000', 3.0))), name='True Bloom',     levelRequired=65, cost=__ThemeCoinCost * 300, description='A blooming blend of true colors.'),
    1167: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('ffffff', 12.0), ('000000', 12.0))), name='Black & White',  levelRequired=65, cost=__ThemeCoinCost * 300, description='A blend between black and white.'),

    1170: ClubItemClubIconThreatening(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('eb4d4d', 2.0), ('eb8f4d', 2.0), ('ebdb4d', 2.0), ('6deb4d', 2.0), ('4debe3', 2.0), ('4d72eb', 2.0), ('a74deb', 2.0))), name='Rainbow',        useJellybeans=True, levelRequired=75,  cost=__ThemeBeanCost * 100000, description='Enjoy all of the colors.'),
    1171: ClubItemClubIconThreatening(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('f28888', 2.0), ('f2b488', 2.0), ('f2e788', 2.0), ('9df288', 2.0), ('88f2ec', 2.0), ('88a0f2', 2.0), ('c488f2', 2.0))), name='Bright Rainbow', useJellybeans=True, levelRequired=75,  cost=__ThemeBeanCost * 100000, description='Enjoy all of the colors.'),
    1172: ClubItemClubIconThreatening(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('730d0d', 2.0), ('73370d', 2.0), ('73690d', 2.0), ('21730d', 2.0), ('0d736e', 2.0), ('0d2573', 2.0), ('470d73', 2.0))), name='Deep Rainbow',   useJellybeans=True, levelRequired=75,  cost=__ThemeBeanCost * 100000, description='Enjoy all of the colors.'),
    1173: ClubItemClubIconThreatening(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('fe0000', 2.0), ('fd8c00', 2.0), ('ffe500', 2.0), ('15e80c', 2.0), ('00d2f7', 2.0), ('5610e3', 2.0), ('bf0dde', 2.0))), name='True Rainbow',   useJellybeans=True, levelRequired=100, cost=__ThemeBeanCost * 150000, description='Enjoy all of the colors, in their oversaturated glory.'),
    1174: ClubItemClubIcon(type=ClubItemType.CLUB_THEME_COL, value=ClubColorPulser((('d294ff', 2.0), ('ff5050', 2.0), ('50be4c', 2.0), ('ff9142', 2.0), ('ff41c6', 2.0), ('f9ff5d', 2.0), ('5d6cef', 2.0), ('43f2ff', 3.0))), name='8-Track', levelRequired=100, cost=__ThemeCoinCost * 500, description='Fades between all of the Gag Track colors.'),

    ##############################

    1500: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1000),
    1501: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1001),
    1502: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1002),
    1503: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1003),
    1504: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1004),
    1505: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1005),
    1506: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1006),
    1507: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1007),
    1510: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1010),
    1511: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1011),
    1512: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1012),
    1513: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1013),
    1514: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1014),
    1515: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1015),
    1516: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1016),
    1517: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1017),
    1520: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1020),
    1521: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1021),
    1522: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1022),
    1523: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1023),
    1524: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1024),
    1525: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1025),
    1526: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1026),
    1527: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1027),
    1530: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1030),
    1531: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1031),
    1532: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1032),
    1533: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1033),
    1534: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1034),
    1535: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1035),
    1536: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1036),
    1537: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1037),
    1540: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1040),
    1541: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1041),
    1542: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1042),
    1543: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1043),
    1544: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1044),
    1545: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1045),
    1546: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1046),
    1547: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1047),
    1550: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1050),
    1551: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1051),
    1552: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1052),
    1553: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1053),
    1554: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1054),
    1555: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1055),
    1556: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1056),
    1557: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1057),
    1560: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1060),
    1561: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1061),
    1562: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1062),
    1563: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1063),
    1564: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1064),
    1565: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1065),
    1566: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1066),
    1567: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1067),
    1570: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1070),
    1571: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1071),
    1572: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1072),
    1573: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1073),
    1574: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1074),
    1575: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1075),
    1576: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1076),
    1577: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1077),
    1580: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1080),
    1581: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1081),
    1582: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1082),
    1583: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1083),
    1584: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1084),
    1585: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1085),
    1586: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1086),
    1587: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1087),
    1590: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1090),
    1591: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1091),
    1592: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1092),
    1593: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1093),
    1594: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1094),
    1595: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1095),
    1596: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1096),
    1597: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1097),
    1600: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1100),
    1601: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1101),
    1602: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1102),
    1603: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1103),
    1604: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1104),
    1605: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1105),
    1606: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1106),
    1607: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1107),
    1610: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1110),
    1611: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1111),
    1612: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1112),
    1613: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1113),
    1614: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1114),
    BBID: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=BBIDMATCH),
    1616: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1116),
    1617: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1117),
    1620: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1120),
    1621: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1121),
    1622: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1122),
    1623: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1123),
    1624: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1124),
    1625: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1125),
    1626: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1126),
    1627: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1127),
    1630: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1130),
    1631: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1131),
    1632: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1132),
    1633: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1133),
    1634: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1134),
    1635: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1135),
    1636: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1136),
    1637: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1137),
    1640: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1140),
    1641: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1141),
    1642: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1142),
    1643: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1143),
    1644: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1144),
    1645: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1145),
    1646: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1146),
    1647: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1147),
    1650: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1150),
    1651: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1151),
    1652: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1152),
    1653: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1153),
    1654: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1154),
    1655: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1155),
    1656: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1156),
    1657: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1157),
    1660: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1160),
    1661: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1161),
    1662: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1162),
    1663: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1163),
    1664: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1164),
    1665: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1165),
    1666: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1166),
    1667: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1167),
    1670: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1170),
    1671: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1171),
    1672: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1172),
    1673: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1173),
    1674: ClubItemClubIcon(type=ClubItemType.CLUB_BG_COL, copyId=1174),

    ##############################

    2000: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Gags_Support,     levelRequired=10,  useJellybeans=False, cost=__BoosterCoinMult * 60,  description='All members in your Club will earn additional Squirt, Sound, Toon-Up, and Lure Gag Experience for %s hours.' % ClubBoosterHours),
    2001: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Gags_Power,       levelRequired=10,  useJellybeans=False, cost=__BoosterCoinMult * 60,  description='All members in your Club will earn additional Trap, Zap, Throw, and Drop Gag Experience for %s hours.' % ClubBoosterHours),
    2002: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Gags_Global,      levelRequired=40,  useJellybeans=False, cost=__BoosterCoinMult * 225, description='All members in your Club will earn extra Gag Experience for %s hours.' % ClubBoosterHours),
    2003: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Racing,  levelRequired=15,  useJellybeans=False, cost=__BoosterCoinMult * 30,  description='All members in your Club will earn extra Racing Experience for %s hours.' % ClubBoosterHours),
    2004: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Trolley, levelRequired=15,  useJellybeans=False, cost=__BoosterCoinMult * 30,  description='All members in your Club will earn extra Trolley Experience for %s hours.' % ClubBoosterHours),
    2005: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Golf,    levelRequired=15,  useJellybeans=False, cost=__BoosterCoinMult * 30,  description='All members in your Club will earn extra Golf Experience for %s hours.' % ClubBoosterHours),
    2006: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Fishing, levelRequired=15,  useJellybeans=False, cost=__BoosterCoinMult * 30,  description='All members in your Club will earn extra Fishing Experience for %s hours.' % ClubBoosterHours),
    2007: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Global,  levelRequired=40,  useJellybeans=False, cost=__BoosterCoinMult * 150, description='All members in your Club will earn extra Activity Experience for %s hours.' % ClubBoosterHours),
    2008: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Jellybeans_Bingo,     levelRequired=25,  useJellybeans=False, cost=__BoosterCoinMult * 75,  description='All members in your Club will earn additional Jellybeans from all sources for %s hours.' % ClubBoosterHours),
    2009: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Sellbot,        levelRequired=25,  useJellybeans=False, cost=__BoosterCoinMult * 80,  description='All members in your Club will earn extra Invoices for %s hours.' % ClubBoosterHours),
    2010: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Cashbot,        levelRequired=25,  useJellybeans=False, cost=__BoosterCoinMult * 80,  description='All members in your Club will earn extra Cogbucks for %s hours.' % ClubBoosterHours),
    2011: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Lawbot,         levelRequired=25,  useJellybeans=False, cost=__BoosterCoinMult * 80,  description='All members in your Club will earn extra Patents for %s hours.' % ClubBoosterHours),
    2012: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Bossbot,        levelRequired=25,  useJellybeans=False, cost=__BoosterCoinMult * 80,  description='All members in your Club will earn extra Stock Options for %s hours.' % ClubBoosterHours),
    2014: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Global,         levelRequired=50,  useJellybeans=False, cost=__BoosterCoinMult * 150, description='All members in your Club will earn extra Merits from all sources for %s hours.' % ClubBoosterHours),
    2015: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Sellbot,  levelRequired=35,  useJellybeans=False, cost=__BoosterCoinMult * 140, description='All members in your Club will earn additional I.O.U.s from the V.P. for %s hours.' % ClubBoosterHours),
    2016: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Cashbot,  levelRequired=35,  useJellybeans=False, cost=__BoosterCoinMult * 140, description='All members in your Club will earn additional Counterfeits from the C.F.O. for %s hours.' % ClubBoosterHours),
    2017: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Lawbot,   levelRequired=35,  useJellybeans=False, cost=__BoosterCoinMult * 90,  description='All members in your Club will earn additional Cease and Desists from the C.L.O. for %s hours.' % ClubBoosterHours),
    2018: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Bossbot,  levelRequired=35,  useJellybeans=False, cost=__BoosterCoinMult * 90,  description='All members in your Club will earn additional Pink Slips from the C.E.O. for %s hours.' % ClubBoosterHours),
    2020: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Global,   levelRequired=60,  useJellybeans=False, cost=__BoosterCoinMult * 300, description='All members in your Club will have increased Boss Rewards (Excluding Unites) for %s hours.' % ClubBoosterHours),
    2021: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Sellbot,  levelRequired=30,  useJellybeans=False, cost=__BoosterCoinMult * 60,  description='All members in your Club will earn extra Sellbot Department Experience for %s hours.' % ClubBoosterHours),
    2022: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Cashbot,  levelRequired=30,  useJellybeans=False, cost=__BoosterCoinMult * 60,  description='All members in your Club will earn extra Cashbot Department Experience for %s hours.' % ClubBoosterHours),
    2023: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Lawbot,   levelRequired=30,  useJellybeans=False, cost=__BoosterCoinMult * 60,  description='All members in your Club will earn extra Lawbot Department Experience for %s hours.' % ClubBoosterHours),
    2024: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Bossbot,  levelRequired=30,  useJellybeans=False, cost=__BoosterCoinMult * 60,  description='All members in your Club will earn extra Bossbot Department Experience for %s hours.' % ClubBoosterHours),
    2026: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Global,   levelRequired=40,  useJellybeans=False, cost=__BoosterCoinMult * 100, description='All members in your Club will earn extra Department Experience from all departments for %s hours.' % ClubBoosterHours),
    2027: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.AllStar,              levelRequired=100, useJellybeans=False, cost=__BoosterCoinMult * 500, description='All members in your Club will have increased Gag Experience, Activity Experience, Jellybeans, Merits, and Boss Rewards for %s hours.' % ClubBoosterHours),

    2100: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Gags_Support,     levelRequired=10,  useJellybeans=True, cost=__BoosterBeanMult * 60, description='All members in your Club will earn additional Squirt, Sound, Toon-Up, and Lure Gag Experience for %s hours.' % ClubBoosterHours),
    2101: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Gags_Power,       levelRequired=10,  useJellybeans=True, cost=__BoosterBeanMult * 60, description='All members in your Club will earn additional Trap, Zap, Throw, and Drop Gag Experience for %s hours.' % ClubBoosterHours),
    2102: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Gags_Global,      levelRequired=40,  useJellybeans=True, cost=__BoosterBeanMult * 225, description='All members in your Club will earn extra Gag Experience for %s hours.' % ClubBoosterHours),
    2103: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Racing,  levelRequired=15,  useJellybeans=True, cost=__BoosterBeanMult * 30, description='All members in your Club will earn extra Racing Experience for %s hours.' % ClubBoosterHours),
    2104: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Trolley, levelRequired=15,  useJellybeans=True, cost=__BoosterBeanMult * 30, description='All members in your Club will earn extra Trolley Experience for %s hours.' % ClubBoosterHours),
    2105: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Golf,    levelRequired=15,  useJellybeans=True, cost=__BoosterBeanMult * 30, description='All members in your Club will earn extra Golf Experience for %s hours.' % ClubBoosterHours),
    2106: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Fishing, levelRequired=15,  useJellybeans=True, cost=__BoosterBeanMult * 30, description='All members in your Club will earn extra Fishing Experience for %s hours.' % ClubBoosterHours),
    2107: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Exp_Activity_Global,  levelRequired=40,  useJellybeans=True, cost=__BoosterBeanMult * 150, description='All members in your Club will earn extra Activity Experience for %s hours.' % ClubBoosterHours),
    2108: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Jellybeans_Bingo,     levelRequired=25,  useJellybeans=True, cost=__BoosterBeanMult * 75, description='All members in your Club will earn additional Jellybeans from all sources for %s hours.' % ClubBoosterHours),
    2109: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Sellbot,        levelRequired=25,  useJellybeans=True, cost=__BoosterBeanMult * 80, description='All members in your Club will earn extra Invoices for %s hours.' % ClubBoosterHours),
    2110: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Cashbot,        levelRequired=25,  useJellybeans=True, cost=__BoosterBeanMult * 80, description='All members in your Club will earn extra Cogbucks for %s hours.' % ClubBoosterHours),
    2111: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Lawbot,         levelRequired=25,  useJellybeans=True, cost=__BoosterBeanMult * 80, description='All members in your Club will earn extra Patents for %s hours.' % ClubBoosterHours),
    2112: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Bossbot,        levelRequired=25,  useJellybeans=True, cost=__BoosterBeanMult * 80, description='All members in your Club will earn extra Stock Options for %s hours.' % ClubBoosterHours),
    2114: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Merit_Global,         levelRequired=50,  useJellybeans=True, cost=__BoosterBeanMult * 150, description='All members in your Club will earn extra Merits from all sources for %s hours.' % ClubBoosterHours),
    2115: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Sellbot,  levelRequired=35,  useJellybeans=True, cost=__BoosterBeanMult * 140, description='All members in your Club will earn additional I.O.U.s from the V.P. for %s hours.' % ClubBoosterHours),
    2116: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Cashbot,  levelRequired=35,  useJellybeans=True, cost=__BoosterBeanMult * 140, description='All members in your Club will earn additional Counterfeits from the C.F.O. for %s hours.' % ClubBoosterHours),
    2117: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Lawbot,   levelRequired=35,  useJellybeans=True, cost=__BoosterBeanMult * 90, description='All members in your Club will earn additional Cease and Desists from the C.L.O. for %s hours.' % ClubBoosterHours),
    2118: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Bossbot,  levelRequired=35,  useJellybeans=True, cost=__BoosterBeanMult * 90, description='All members in your Club will earn additional Pink Slips from the C.E.O. for %s hours.' % ClubBoosterHours),
    2120: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Global,   levelRequired=60,  useJellybeans=True, cost=__BoosterBeanMult * 300, description='All members in your Club will have increased Boss Rewards (Excluding Unites) for %s hours.' % ClubBoosterHours),
    2121: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Sellbot,  levelRequired=30,  useJellybeans=True, cost=__BoosterBeanMult * 60, description='All members in your Club will earn extra Sellbot Department Experience for %s hours.' % ClubBoosterHours),
    2122: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Cashbot,  levelRequired=30,  useJellybeans=True, cost=__BoosterBeanMult * 60, description='All members in your Club will earn extra Cashbot Department Experience for %s hours.' % ClubBoosterHours),
    2123: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Lawbot,   levelRequired=30,  useJellybeans=True, cost=__BoosterBeanMult * 60, description='All members in your Club will earn extra Lawbot Department Experience for %s hours.' % ClubBoosterHours),
    2124: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Bossbot,  levelRequired=30,  useJellybeans=True, cost=__BoosterBeanMult * 60, description='All members in your Club will earn extra Bossbot Department Experience for %s hours.' % ClubBoosterHours),
    2126: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.Reward_Boss_Global,   levelRequired=40,  useJellybeans=True, cost=__BoosterBeanMult * 100, description='All members in your Club will earn extra Department Experience from all departments for %s hours.' % ClubBoosterHours),
    2127: ClubItemBooster(type=ClubItemType.CLUB_BOOSTERS, value=BoosterItemType.AllStar,              levelRequired=100, useJellybeans=True, cost=__BoosterBeanMult * 500, description='All members in your Club will have increased Gag Experience, Activity Experience, Jellybeans, Merits, and Boss Rewards for %s hours.' % ClubBoosterHours),

    ##############################

    2500: ClubItemMemberSlots(type=ClubItemType.CLUB_MEMBER_SLOTS, name='+5 Member Capacity',   cost=0,                     description=('Increases the capacity of Toons in your Club from %s to %s! The more, the merrier.', 'Your Club has reached the max capacity.')),
    2501: ClubItemNameChanger(type=ClubItemType.CLUB_NAME_CHANGE,  name='Club Name Change',     cost=ClubNameChangeCost,    description='Allows you to change your Club\'s name once. Talk to Doe Vinci after to get it finalized. Can only be purchased by the owner of the Club.', levelRequired=25),
    2502: ClubItemBoosterSlots(type=ClubItemType.CLUB_BOOSTER_SLOTS, name='+1 Booster Slot',    cost=0,                     description=('Increases the amount of Boosters your Club can have active at once from %s to %s!', 'Your Club has reached the maximum amount of active Boosters.')),
})

DefaultClubThemeCols  = ClubItemIndex.getDefaultsOfType(ClubItemType.CLUB_THEME_COL)
DefaultClubIconBgCols = ClubItemIndex.getDefaultsOfType(ClubItemType.CLUB_BG_COL)
DefaultClubIconGeoms  = ClubItemIndex.getDefaultsOfType(ClubItemType.CLUB_ICON)
DefaultClubIconBgs    = ClubItemIndex.getDefaultsOfType(ClubItemType.CLUB_BACKGROUND)

ClubCategoryNames = {
    ClubShopCategory.IMAGES: 'Icon Images',
    ClubShopCategory.BACKGROUNDS: 'Icon Detail',
    ClubShopCategory.THEME_COLORS: 'Theme Colors',
    ClubShopCategory.BACKGROUND_COLORS: 'Detail Colors',
    ClubShopCategory.GAGS: 'Gags',
    ClubShopCategory.ACTIVITIES: 'Activities',
    ClubShopCategory.MERITS: 'Merits',
    ClubShopCategory.REWARDS: 'Boss Rewards',
    ClubShopCategory.UNIVERSAL: 'Universal',
    ClubShopCategory.DEPARTMENTXP: 'Department Exp.',
}


class ClubItemCurrencyType(IntEnum):
    CLUB_COINS = auto()
    JELLYBEANS = auto()


# Club member slot upgrades
def calculateClubCapacityUpgrade(currentMembers: int, includeNewMembers: bool):
    """
    Calculates the costs and result of a club member shop upgrade.
    :param currentMembers:    How many members the club currently has.
    :param includeNewMembers: Include the new members in the result.
    :return: None if the purchase cannot occur.
             Otherwise returns the new members and the cost of operation.
    """
    memberIncrement = 5

    # How many members would this club have now?
    newMembers = currentMembers + memberIncrement

    if newMembers > ClubMaxSize:
        # Nope, too many.
        if includeNewMembers:
            return 0, currentMembers
        return 0

    # How much would this cost?
    cost = ClubCapacityUpgrades[newMembers]["cost"]

    # Return our result.
    if includeNewMembers:
        return cost, newMembers
    return cost


"""
Club Shop Functions
"""


def getShopItems(category, subCategory):
    if category == ClubShopCategory.ITEMS_AND_UPGRADES:
        return ClubItemIndex.getItemsOfTypes([ClubItemType.CLUB_MEMBER_SLOTS,
                                              ClubItemType.CLUB_BOOSTER_SLOTS,
                                              ClubItemType.CLUB_NAME_CHANGE,])

    elif category == ClubShopCategory.CLUB_BOOSTERS:
        boosterShopItems = ClubItemIndex.getItemsOfType(ClubItemType.CLUB_BOOSTERS)
        validBoosterTypes = {
            ClubShopCategory.GAGS:          [
                BoosterItemType.Exp_Gags_Support,
                BoosterItemType.Exp_Gags_Power,
            ],
            ClubShopCategory.ACTIVITIES:    [
                BoosterItemType.Exp_Activity_Racing,
                BoosterItemType.Exp_Activity_Trolley,
                BoosterItemType.Exp_Activity_Golf,
                BoosterItemType.Exp_Activity_Fishing,
            ],
            ClubShopCategory.MERITS:        [
                BoosterItemType.Merit_Sellbot,
                BoosterItemType.Merit_Cashbot,
                BoosterItemType.Merit_Lawbot,
                BoosterItemType.Merit_Bossbot,
                BoosterItemType.Merit_Boardbot,
            ],
            ClubShopCategory.DEPARTMENTXP:  [
                BoosterItemType.Exp_Dept_Sellbot,
                BoosterItemType.Exp_Dept_Cashbot,
                BoosterItemType.Exp_Dept_Lawbot,
                BoosterItemType.Exp_Dept_Bossbot,
                BoosterItemType.Exp_Dept_Boardbot,
            ],
            ClubShopCategory.REWARDS:       [
                BoosterItemType.Reward_Boss_Sellbot,
                BoosterItemType.Reward_Boss_Cashbot,
                BoosterItemType.Reward_Boss_Lawbot,
                BoosterItemType.Reward_Boss_Bossbot,
                BoosterItemType.Reward_Boss_Boardbot,
            ],
            ClubShopCategory.UNIVERSAL: [
                BoosterItemType.Exp_Gags_Global,
                BoosterItemType.Exp_Activity_Global,
                BoosterItemType.Jellybeans_Global,
                BoosterItemType.AllStar,
                BoosterItemType.Merit_Global,
                BoosterItemType.Exp_Dept_Global,
                BoosterItemType.Reward_Boss_Global,
            ],
        }.get(subCategory)

        # Get the filtered booster types.
        boosterItems = [shopItem for shopItem in boosterShopItems
                        if shopItem.getValue() in validBoosterTypes and shopItem.isRightWeekday()]

        # So the Club Coin items are at the front, and the Jellybean items are at the end.
        # We go ahead and take the second half of the items and merge them into the initial ones.
        halfwayPoint = len(boosterItems) // 2
        filteredItems = []
        for itemPair in zip(boosterItems[:halfwayPoint], boosterItems[halfwayPoint:]):
            filteredItems.extend(itemPair)

        # We gaming
        return filteredItems

    elif category == ClubShopCategory.CUSTOMIZATION:
        return ClubItemIndex.getItemsOfType({
            ClubShopCategory.IMAGES: ClubItemType.CLUB_ICON,
            ClubShopCategory.BACKGROUNDS: ClubItemType.CLUB_BACKGROUND,
            ClubShopCategory.THEME_COLORS: ClubItemType.CLUB_THEME_COL,
            ClubShopCategory.BACKGROUND_COLORS: ClubItemType.CLUB_BG_COL,
        }.get(subCategory))
