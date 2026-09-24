from toontown.notifications.NotificationEnums import NotificationType
from toontown.notifications.notificationData.NotificationData import NotificationData


class AddClubmateNotification(NotificationData):
    """
    Contains logic for handling adding clubmates.
    """
    notificationType = NotificationType.AddClubmate

    def shouldBeRemoved(self, otherNotif: 'AddClubmateNotification'):
        # Remove if we're either:
        # - the same notif type
        # - a Friend Request notif, with an outbound state
        notifType = self.getNotificationType()
        if otherNotif.getNotificationType() == notifType:
            return True
        return False
