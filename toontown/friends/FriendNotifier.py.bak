from direct.directnotify import DirectNotifyGlobal

from toontown.notifications.NotificationManager import getNotificationManager
from toontown.notifications.notificationData.AddFriendNotification import AddFriendNotification


class FriendNotifier(object):
    """Displays successful friendships through Clash's alert ribbon."""

    notify = DirectNotifyGlobal.directNotify.newCategory('FriendNotifier')

    def __init__(self, avId, avName, avDNA, context, **kw):
        self.avId = avId
        self.avName = avName
        self.avDNA = avDNA
        self.context = context
        self.notification = AddFriendNotification(
            avId=self.avId, name=self.avName, dna=self.avDNA)
        getNotificationManager().addNotification(self.notification)

    def cleanup(self):
        self.context = None
