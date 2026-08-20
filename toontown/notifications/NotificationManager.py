from __future__ import absolute_import
from direct.showbase import DirectObject
from direct.task import Task

from toontown.notifications.NotificationMessages import CL_LOCAL_NOTIFICATION
from toontown.notifications.gui.NotificationContainer import NotificationContainer


class NotificationManager(DirectObject.DirectObject):
    """Local storage adapter for Clash's notification panel on Altis.

    Clash only exposes the panel while the normal social interface is active.
    Altis's catalog fields arrive before ``LocalToon.initInterface`` and while
    the loading screen is still drawing, so creation, visibility, and sound are
    deliberately deferred until the normal game interface is active.
    """

    def __init__(self, owner=None):
        DirectObject.DirectObject.__init__(self)
        self.notifications = []
        if owner is None:
            owner = getattr(base, 'localAvatar', None)
        self.ownerId = getattr(owner, 'doId', None)

        self.container = NotificationContainer(self)
        self.container.hide()

        self.interfaceRequested = False
        self.interfaceVisible = False
        self.pendingAnnouncement = False
        self.loading = bool(getattr(loader, 'inBulkBlock', None))

        self.taskName = 'AltisNotificationManager-ready-%s' % self.ownerId
        self.accept(CL_LOCAL_NOTIFICATION, self.addNotification)
        self.accept('altis-bulk-load-begin', self.__handleLoadBegin)
        self.accept('altis-bulk-load-end', self.__handleLoadEnd)

        taskMgr.remove(self.taskName)
        taskMgr.add(self.__visibilityTask, self.taskName)

    def __handleLoadBegin(self):
        self.loading = True
        self.interfaceVisible = False
        if self.container is not None:
            self.container.hide()

    def __handleLoadEnd(self):
        # The next normal task frame performs the reveal.  This guarantees the
        # panel and notification sound cannot appear inside the loading screen.
        self.loading = False
        self.interfaceVisible = False

    def __worldIsReady(self):
        if self.loading:
            return False
        try:
            if getattr(loader, 'inBulkBlock', None):
                return False
        except Exception:
            pass

        localAvatar = getattr(base, 'localAvatar', None)
        if localAvatar is None:
            return False
        try:
            playGame = base.cr.playGame
            if playGame is None or playGame.getPlace() is None:
                return False
        except Exception:
            return False
        return True

    def __visibilityTask(self, task):
        shouldShow = self.interfaceRequested and self.__worldIsReady()

        if not shouldShow:
            if self.interfaceVisible:
                self.interfaceVisible = False
                if self.container is not None:
                    self.container.hide()
            return Task.cont

        if not self.interfaceVisible:
            self.interfaceVisible = True
            if self.container is not None:
                self.container.show()
                self.container.setNotifications(
                    self.notifications,
                    newNotification=self.pendingAnnouncement,
                    playSound=self.pendingAnnouncement,
                )
            self.pendingAnnouncement = False

        return Task.cont

    def setInterfaceVisible(self, visible):
        """Matches Clash's ``LocalToon.refreshOnscreenButtons`` visibility."""
        self.interfaceRequested = bool(visible)
        if not self.interfaceRequested:
            self.interfaceVisible = False
            if self.container is not None:
                self.container.hide()

    def addNotification(self, data):
        dedupeKey = getattr(data, 'dedupeKey', None)
        if dedupeKey is not None:
            for oldData in self.notifications[:]:
                if getattr(oldData, 'dedupeKey', None) == dedupeKey:
                    self.removeNotification(oldData, invokeDismiss=True,
                                            refresh=False)

        self.notifications.insert(0, data)
        if self.interfaceVisible and self.container is not None:
            self.container.setNotifications(
                self.notifications,
                newNotification=True,
                playSound=True,
            )
        else:
            # Play only when the panel is first revealed in the actual world.
            self.pendingAnnouncement = True
        return data

    def removeNotificationAt(self, index, invokeDismiss=True, refresh=True):
        if index < 0 or index >= len(self.notifications):
            return
        data = self.notifications.pop(index)
        if invokeDismiss:
            data.invokeDismiss()
        if refresh and self.container is not None:
            self.container.setNotifications(self.notifications)

    def removeNotification(self, data, invokeDismiss=False, refresh=True):
        if data not in self.notifications:
            return
        self.removeNotificationAt(
            self.notifications.index(data),
            invokeDismiss=invokeDismiss,
            refresh=refresh,
        )

    def clear(self, invokeDismiss=False):
        oldNotifications = self.notifications[:]
        self.notifications = []
        self.pendingAnnouncement = False
        if invokeDismiss:
            for data in oldNotifications:
                data.invokeDismiss()
        if self.container is not None:
            self.container.setNotifications(self.notifications)

    def destroy(self):
        taskMgr.remove(self.taskName)
        self.ignoreAll()
        if self.container is not None:
            self.container.destroy()
            self.container = None
        self.notifications = []
        self.interfaceRequested = False
        self.interfaceVisible = False
        self.pendingAnnouncement = False


def getNotificationManager(owner=None):
    manager = getattr(base, 'altisNotificationManager', None)
    if owner is None:
        owner = getattr(base, 'localAvatar', None)
    ownerId = getattr(owner, 'doId', None)

    if manager is not None and getattr(manager, 'ownerId', None) != ownerId:
        manager.destroy()
        manager = None
    if manager is None or getattr(manager, 'container', None) is None:
        manager = NotificationManager(owner)
        base.altisNotificationManager = manager
    return manager


def addNotification(data):
    return getNotificationManager().addNotification(data)
