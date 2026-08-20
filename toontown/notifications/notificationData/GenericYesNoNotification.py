from __future__ import absolute_import
from toontown.notifications.notificationData.NotificationData import NotificationData


class GenericYesNoNotification(NotificationData):
    def __init__(self, title='', subtitle='', onYes=None, onNo=None,
                 onDismiss=None, dna=None, sfx=None, dedupeKey=None):
        NotificationData.__init__(
            self, title=title, subtitle=subtitle, dna=dna,
            onYes=onYes, onNo=onNo, onDismiss=onDismiss,
            notificationType='generic-yes-no', sfx=sfx,
            dedupeKey=dedupeKey)
