from toontown.club.ClubClasses import ClubIcon
from toontown.club.ClubGlobals import BTID, BBID
from toontown.notifications.NotificationEnums import NotificationType
from toontown.notifications.notificationData.NotificationData import NotificationData


class ClubInviteNotification(NotificationData):
    """
    Contains data for a Club Invite.
    """
    notificationType = NotificationType.ClubInvite
    state_sent = 0
    state_received = 1
    state_accepted = 2
    state_denied = 3
    state_unaccepting = 4
    state_expired = 5
    state_they_in_some_club = 6
    state_they_in_our_club = 7
    state_club_full = 8
    state_club_banned = 9
    state_no_perms = 10
    state_not_friends = 11
    state_tryagain_later = 12
    state_welcome = 13
    state_notnearby = 14
    state_they_joinlocked = 15
    state_we_joinlocked = 16

    def __init__(self, clubId: int = 0, clubLevel: int = 0, iconId: int = 0, backgroundId: int = 0,
                 clubCol: int = BTID, bgCol: int = BBID, avId: int = 0,
                 toonName: str = '', clubName: str = '', inviteState: int = 0):
        """Creates a FriendRequestNotification dataclass."""
        intArgs = [clubId, iconId, backgroundId, clubCol, bgCol, avId, inviteState, clubLevel]
        strArgs = [toonName, clubName]
        blobArgs = []
        super().__init__(intArgs, strArgs, blobArgs)

    """
    Getters
    """

    def getClubId(self):
        return self.intArgs[0]

    def getClubIcon(self) -> ClubIcon:
        return ClubIcon(
            iconId=self.intArgs[1],
            backgroundId=self.intArgs[2],
            clubCol=self.intArgs[3],
            bgCol=self.intArgs[4],
        )

    def getAvId(self):
        return self.intArgs[5]

    def getState(self):
        return self.intArgs[6]

    def getToonName(self):
        return self.strArgs[0]

    def getClubName(self):
        return self.strArgs[1]

    def getClubLevel(self):
        return self.intArgs[7]

    def shouldBeRemoved(self, otherNotif: 'ClubInviteNotification'):
        # Remove if we're the same notif type and are referencing the same avId.
        if self.getNotificationType() == otherNotif.getNotificationType():
            if self.getAvId() == otherNotif.getAvId():
                return True
        return False
