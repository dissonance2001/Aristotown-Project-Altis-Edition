from __future__ import absolute_import
from toontown.notifications.notificationData.NotificationData import NotificationData


class FriendRequestNotification(NotificationData):
    def __init__(self, avId=0, name='', dna=None, onYes=None, onNo=None,
                 onDismiss=None):
        self.avId = avId
        self.name = name
        NotificationData.__init__(
            self,
            title='Friend Request',
            subtitle='%s wants to be your friend.' % name,
            dna=dna,
            onYes=onYes,
            onNo=onNo,
            onDismiss=onDismiss,
            notificationType='friend-request',
            dedupeKey=('friend-request', avId))

    def getAvId(self):
        return self.avId

    def getToonName(self):
        return self.name
