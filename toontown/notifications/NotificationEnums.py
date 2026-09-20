"""
Various enums used for notifications.
"""
from enum import IntEnum


class NotificationType(IntEnum):
    """
    The enum representing the type of notification for a Toon.
    These may be DB'd on a toon, don't use auto()
    """
    NoNotifs = 0  # type to notify having no notifications available
    FriendRequest = 2
    AddFriend = 3
    FakeFriendResponse = 4
    GroupCallback = 5
    GroupInvite = 6
    ClubInvite = 7
    ClubTaskReroll = 8
    ClubTaskPurchase = 9
    ClubTaskStatus = 10
    AddClubmate = 11
    GenericText = 12
    ClubJellybeans = 13
    LeaveClub = 14
    GenericYesNo = 15


# Strong Notifications are types of notifications that
# will persist on the Toon, even after disconnecting.
StrongNotificationTypes = (
    # NotificationType.NewCatalog,
)

NonFeebleNotificationTypes = (
    NotificationType.FriendRequest, NotificationType.AddFriend,
    NotificationType.ClubInvite, NotificationType.AddClubmate,
    NotificationType.GroupInvite,
)

# Feeble Notifications are types of notifications that get
# cleared when the ribbon closes for notifications.
FeebleNotificationTypes = tuple(notifType for notifType in NotificationType if notifType not in NonFeebleNotificationTypes)
