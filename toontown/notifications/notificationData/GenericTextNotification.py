from __future__ import absolute_import
from toontown.notifications.notificationData.NotificationData import NotificationData


class GenericTextNotification(NotificationData):
    def __init__(self, title='', subtitle='', dna=None, onDismiss=None,
                 sfx=None, dedupeKey=None):
        NotificationData.__init__(
            self, title=title, subtitle=subtitle, dna=dna,
            onDismiss=onDismiss, notificationType='generic-text', sfx=sfx,
            dedupeKey=dedupeKey)
