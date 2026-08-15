import math

# Python 2.7 compatible Altis Club constants.

CLUB_CREATION_COST = 20000
CLUB_MAX_JELLYBEANS = 1000000000
CLUB_MAX_MEMBERS = 15
CLUB_NAME_MIN = 3
CLUB_NAME_MAX = 24
CLUB_MOTD_MAX = 120
CLUB_CHAT_MAX = 100

RANK_MEMBER = 0
RANK_OFFICER = 1
RANK_DEPUTY = 2
RANK_LEADER = 3

RANK_NAMES = {
    RANK_MEMBER: 'Member',
    RANK_OFFICER: 'Officer',
    RANK_DEPUTY: 'Deputy',
    RANK_LEADER: 'Leader',
}

# Permissions follow the Corporate Clash rank defaults.
PERMISSION_PURCHASE_TASKS = 'purchaseTasks'
PERMISSION_PURCHASE_ITEMS = 'purchaseItems'
PERMISSION_ANNOUNCE = 'announce'
PERMISSION_SHOUT = 'shout'
PERMISSION_CHAT = 'chat'
PERMISSION_INVITE = 'invite'
PERMISSION_KICK = 'kick'
PERMISSION_MOTD = 'motd'
PERMISSION_RANK = 'rank'
PERMISSION_CUSTOMIZE = 'customize'


# Editable permission IDs used by the Club Settings page and DC interface.
PERMISSION_ID_REROLL_TASKS = 0
PERMISSION_ID_PURCHASE_ITEMS = 1
PERMISSION_ID_SHOUT = 2
PERMISSION_ID_CHAT = 3
PERMISSION_ID_INVITE = 4
PERMISSION_ID_KICK = 5
PERMISSION_ID_DESCRIPTION = 6

EDITABLE_PERMISSION_KEYS = (
    PERMISSION_PURCHASE_TASKS,
    PERMISSION_PURCHASE_ITEMS,
    PERMISSION_SHOUT,
    PERMISSION_CHAT,
    PERMISSION_INVITE,
    PERMISSION_KICK,
    PERMISSION_MOTD,
)

PERMISSION_ID_TO_KEY = {
    PERMISSION_ID_REROLL_TASKS: PERMISSION_PURCHASE_TASKS,
    PERMISSION_ID_PURCHASE_ITEMS: PERMISSION_PURCHASE_ITEMS,
    PERMISSION_ID_SHOUT: PERMISSION_SHOUT,
    PERMISSION_ID_CHAT: PERMISSION_CHAT,
    PERMISSION_ID_INVITE: PERMISSION_INVITE,
    PERMISSION_ID_KICK: PERMISSION_KICK,
    PERMISSION_ID_DESCRIPTION: PERMISSION_MOTD,
}

PERMISSION_KEY_TO_ID = dict((value, key) for key, value in PERMISSION_ID_TO_KEY.items())

PERMISSION_LABELS = {
    PERMISSION_PURCHASE_TASKS: 'Reroll Club Tasks',
    PERMISSION_PURCHASE_ITEMS: 'Purchase Club Shop Items',
    PERMISSION_SHOUT: 'Use Club Shouts',
    PERMISSION_CHAT: 'Use Club Chat',
    PERMISSION_INVITE: 'Invite Toons To Club',
    PERMISSION_KICK: 'Kick Toons From Club',
    PERMISSION_MOTD: 'Update Club Description',
}

# Clash display names for the editable ranks.
SETTINGS_RANK_NAMES = {
    RANK_DEPUTY: 'Captains',
    RANK_OFFICER: 'Scouts',
    RANK_MEMBER: 'Members',
}

# Personal settings are saved locally per Toon. They do not alter Club data.
SETTING_SHOW_NAMETAG = 'want-club-nametag'
SETTING_MESSAGE_POPUPS = 'chat-club-message-popups'
SETTING_UPDATE_POPUPS = 'chat-club-update-popups'
SETTING_COIN_NOTIFICATIONS = 'show-clubcoin-reward'

PERSONAL_SETTING_KEYS = (
    SETTING_SHOW_NAMETAG,
    SETTING_MESSAGE_POPUPS,
    SETTING_UPDATE_POPUPS,
    SETTING_COIN_NOTIFICATIONS,
)

PERSONAL_SETTING_DEFAULTS = {
    SETTING_SHOW_NAMETAG: True,
    SETTING_MESSAGE_POPUPS: True,
    SETTING_UPDATE_POPUPS: True,
    SETTING_COIN_NOTIFICATIONS: True,
}

PERSONAL_SETTING_LABELS = {
    SETTING_SHOW_NAMETAG: 'Show Club Nametag',
    SETTING_MESSAGE_POPUPS: 'Pop-Up Club Messages',
    SETTING_UPDATE_POPUPS: 'Pop-Up Club Updates',
    SETTING_COIN_NOTIFICATIONS: 'Show Club Coin Notifications',
}

RANK_PERMISSIONS = {
    RANK_MEMBER: set((PERMISSION_CHAT,)),
    RANK_OFFICER: set((PERMISSION_CHAT, PERMISSION_SHOUT, PERMISSION_INVITE)),
    RANK_DEPUTY: set((PERMISSION_CHAT, PERMISSION_SHOUT, PERMISSION_INVITE,
                      PERMISSION_KICK, PERMISSION_PURCHASE_TASKS,
                      PERMISSION_PURCHASE_ITEMS, PERMISSION_CUSTOMIZE)),
    RANK_LEADER: set((PERMISSION_CHAT, PERMISSION_SHOUT, PERMISSION_INVITE,
                      PERMISSION_KICK, PERMISSION_PURCHASE_TASKS,
                      PERMISSION_PURCHASE_ITEMS, PERMISSION_ANNOUNCE,
                      PERMISSION_MOTD, PERMISSION_RANK,
                      PERMISSION_CUSTOMIZE)),
}

NOTIFY_INFO = 0
NOTIFY_ERROR = 1
NOTIFY_SUCCESS = 2
NOTIFY_INVITE_SENT = 3
NOTIFY_MEMBER_JOINED = 4
NOTIFY_MEMBER_LEFT = 5
NOTIFY_MEMBER_KICKED = 6
NOTIFY_RANK_CHANGED = 7
NOTIFY_TASK_COMPLETE = 8
NOTIFY_ITEM_PURCHASED = 9
NOTIFY_BOOSTER_STARTED = 10
NOTIFY_COIN_EARNED = 11
NOTIFY_DONATION_RESULT = 12

# Donation requests use the existing requestUpdateIcon DC field for Altis
# compatibility. The value cannot collide with real Club Shop icon IDs.
DONATION_REQUEST_MAGIC = 65535

# Full Corporate Clash Club Shop catalogue.
from toontown.club.ClubShopCatalog import (
    SHOP_ITEMS,
    SHOP_COLORS,
    CURRENCY_CLUB_COINS,
    CURRENCY_JELLYBEANS,
    COLOR_PAYLOAD_OFFSET,
)


CLUB_LEGACY_BOOSTER_GUMBALL_TYPES = {
    'gag': 12,
    'activity': 11,
    'merit': 16,
    'department': 9,
    'reward': 13,
    'universal': 60,
}

CLUB_BOOSTER_GUMBALL_TYPES = {
    2000: 50,
    2001: 51,
    2002: 12,
    2003: 20,
    2004: 21,
    2005: 22,
    2006: 23,
    2007: 11,
    2008: 14,
    2009: 3,
    2010: 4,
    2011: 5,
    2012: 6,
    2014: 16,
    2015: 40,
    2016: 41,
    2017: 42,
    2018: 43,
    2020: 13,
    2021: 30,
    2022: 31,
    2023: 32,
    2024: 33,
    2026: 9,
    2027: 60,
}


def normalizeClubBoosterItemId(itemId):
    itemId = int(itemId)
    if 2100 <= itemId < 2200:
        itemId -= 100
    return itemId


def getClubBoosterType(itemId):
    try:
        itemId = normalizeClubBoosterItemId(itemId)
    except:
        return CLUB_LEGACY_BOOSTER_GUMBALL_TYPES.get(str(itemId))
    return CLUB_BOOSTER_GUMBALL_TYPES.get(itemId)


def unpackShopItem(item):
    """Return a normalized seven-field Club Shop tuple.

    Older five-field entries remain accepted for compatibility with saved
    development builds.
    """
    if len(item) >= 7:
        return item[:7]
    name, category, cost, requiredLevel, payload = item
    return (
        name,
        category,
        int(cost),
        int(requiredLevel),
        payload,
        CURRENCY_CLUB_COINS,
        '',
    )


# Current Clash-style Club Task settings. Tasks are generated automatically,
# shared by every member, and replaced immediately when completed.
MAX_ACTIVE_TASKS = 3
CLUB_TASK_DIFFICULTY_COEFFICIENT = 1.15

# Kept only for compatibility with old callers. Club Tasks are no longer
# selected from or purchased through a fixed definition table.
TASK_DEFINITIONS = {}
TASK_PURCHASE_COST = 0
TASK_REROLL_COST = 0


def getTaskRerollCost(task):
    try:
        from toontown.club import ClubTaskPricing
        return ClubTaskPricing.calculateRerollCost(
            int(task.get('chainId', task.get('taskId', 0))))
    except:
        return 1


def getDefaultClubPermissions():
    permissions = {}
    for rank in (RANK_MEMBER, RANK_OFFICER, RANK_DEPUTY):
        rankPermissions = {}
        for permission in EDITABLE_PERMISSION_KEYS:
            rankPermissions[permission] = bool(permission in RANK_PERMISSIONS.get(rank, set()))
        permissions[str(rank)] = rankPermissions
    return permissions


def getPermissionKey(permissionId):
    return PERMISSION_ID_TO_KEY.get(int(permissionId))


# Corporate Clash's current Club XP curve. Level 1 needs 10 XP, and
# every following level needs ceil(previous requirement * 1.03).
CLUB_STARTING_LEVEL_XP = 10
CLUB_LEVEL_XP_GROWTH = 1.03

# Activity callers use the legacy Altis reward units:
# fishing reports 1 unit per fish and trolley reports 10 units per game.
# Convert each unit into 10 current Club Coins and 1 Club XP.
CLUB_ACTIVITY_COIN_MULTIPLIER = 10
CLUB_ACTIVITY_XP_MULTIPLIER = 1

# Club Coins were redenominated by x100 in Clash, but Club XP was not.
# This divisor remains for saved-data compatibility with earlier Club builds.
CLUB_COIN_XP_DIVISOR = 100
CLUB_XP_DENOMINATION_VERSION = 2


def getExperienceRequiredForLevel(level):
    """Return the XP required to advance from ``level`` to ``level + 1``."""
    level = max(1, int(level))
    required = CLUB_STARTING_LEVEL_XP
    for unused in xrange(1, level):
        required = int(math.ceil(required * CLUB_LEVEL_XP_GROWTH))
    return required


def getExperienceForLevel(level):
    """Return the total XP at the beginning of an exact Club level."""
    level = max(1, int(level))
    experience = 0
    for currentLevel in xrange(1, level):
        experience += getExperienceRequiredForLevel(currentLevel)
    return experience


def calculateClubLevel(experience):
    """Return ``(level, progress, required)`` for a total Club XP value."""
    remaining = max(0, int(experience))
    level = 1
    required = CLUB_STARTING_LEVEL_XP

    # Clash currently has no known maximum Club level, so continue applying
    # the same growth formula for as much XP as the Club has earned.
    while remaining >= required:
        remaining -= required
        level += 1
        required = int(math.ceil(required * CLUB_LEVEL_XP_GROWTH))

    return level, remaining, required


def getLevelForExperience(experience):
    return calculateClubLevel(experience)[0]


def hasPermission(rank, permission):
    return permission in RANK_PERMISSIONS.get(int(rank), set())
