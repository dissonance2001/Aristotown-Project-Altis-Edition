from __future__ import absolute_import
from toontown.notifications.notificationData.NotificationData import NotificationData


class CatalogNotification(NotificationData):
    """Catalog/mail notification shown in Clash's standard alert frame."""

    def __init__(self, message=''):
        NotificationData.__init__(
            self,
            title='Cattlelog Alert',
            subtitle=message,
            notificationType='catalog',
            sfx='phase_3.5/audio/sfx/UI_notif_general.ogg',
            dedupeKey='catalog-alert')
