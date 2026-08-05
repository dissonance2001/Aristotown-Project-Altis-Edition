from toontown.notifications.notificationData.NotificationData import NotificationData


class AddFriendNotification(NotificationData):
    def __init__(self, avId=0, name='', dna=None):
        self.avId = avId
        self.name = name
        NotificationData.__init__(
            self,
            title='New Friend',
            subtitle='You are now friends with %s!' % name,
            dna=dna,
            notificationType='add-friend',
            dedupeKey=('add-friend', avId))
