from toontown.notifications.NotificationEnums import NotificationType
from toontown.notifications.notificationData.NotificationData import NotificationData


class LeaveClubNotification(NotificationData):
    notificationType = NotificationType.LeaveClub

    def __init__(self, clubId: int = 0):
        super().__init__(intArgs=[clubId])

    def getClubId(self):
        return self.intArgs[0]

    def shouldBeRemoved(self, otherNotif):
        return otherNotif.getNotificationType() == self.getNotificationType()
