from toontown.notifications.NotificationEnums import NotificationType
from toontown.notifications.notificationData.NotificationData import NotificationData


class ClubJellybeansNotification(NotificationData):
    notificationType = NotificationType.ClubJellybeans
    state_no_beans = 0
    state_has_beans = 1
    state_success = 2

    def __init__(self, state: int = 1, clubId: int = 0, beans: int = 0):
        """Creates a FriendRequestNotification dataclass."""
        intArgs = [state, clubId, beans]
        super().__init__(intArgs=intArgs)

    def getState(self):
        return self.intArgs[0]

    def getClubId(self):
        return self.intArgs[1]

    def getJellybeans(self):
        return self.intArgs[2]

    def setJellybeans(self, amount):
        self.intArgs[2] = amount

    def shouldBeRemoved(self, otherNotif: 'ClubJellybeansNotification'):
        # Remove if we're the same type.
        notifType = self.getNotificationType()
        if otherNotif.getNotificationType() == notifType:
            return True
        return False
