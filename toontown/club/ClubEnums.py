"""
Enum definitions for clubs.
"""
from enum import IntEnum, auto

from strenum import StrEnum

from prisma.enums import ClubNameStatus


### CLUB NOTIFICATION ENUMS ###


class ClubNotification(IntEnum):
    """
    A type of Notification from the server to the client.
    Contains various callback data.
    Cannot be auto, some fields are DB'd
    """
    UserLeftClub = 0
    UserKickedFromClub = 1

    # Callback types when a user is attempting to create a club.
    ClubCreation_GeneralError = 2
    ClubCreation_ClubBanned = 3
    ClubCreation_AlreadyInClub = 4
    ClubCreation_NameBlocked = 5
    ClubCreation_TooPoor = 6
    ClubCreation_Success = 7

    # Club Shop callbacks
    ClubShop_Success = 8
    ClubShop_Failure = 9
    ClubShop_Equip = 10

    ClubTasks_Rerolled = 20
    ClubTasks_TaskStarted = 21
    ClubTasks_TaskComplete = 22
    ClubTasks_TaskFailed = 23



# In what states can the Club Name be changed in?
ChangableClubNameStates = [ClubNameStatus.NAME_DENIED, ClubNameStatus.NAME_CHANGING, ClubNameStatus.NAME_FAILED]


class ClubRank(IntEnum):
    # The rank of a member within a club.
    Member = 0
    Officer = 1
    Deputy = 2
    Leader = 3


### CLUB OPTIONS ID ###
REROLL_CLUB_TASKS = 0
PURCHASE_CLUB_SHOP_ITEMS = 1
CAN_MAKE_ANNOUNCEMENTS = 2
CAN_USE_CLUB_SHOUTS = 3
CAN_USE_CLUB_CHAT = 4
CAN_INVITE_TOONS = 5
CAN_KICK_TOONS = 6
CAN_UPDATE_MOTD = 7


### CLUB SHOP CATEGORIES ###
class ClubShopCategory(IntEnum):
    # main categories
    ITEMS_AND_UPGRADES = auto()
    CLUB_BOOSTERS = auto()
    CUSTOMIZATION = auto()

    # image subcategories
    IMAGES = auto()
    BACKGROUNDS = auto()
    THEME_COLORS = auto()
    BACKGROUND_COLORS = auto()

    # booster subcategories
    GAGS = auto()
    ACTIVITIES = auto()
    MERITS = auto()
    DEPARTMENTXP = auto()
    REWARDS = auto()
    UNIVERSAL = auto()
