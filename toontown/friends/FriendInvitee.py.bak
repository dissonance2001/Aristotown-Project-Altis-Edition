from direct.showbase import DirectObject
from direct.directnotify import DirectNotifyGlobal

from toontown.toonbase.ToontownGlobals import MaxFriends
from toontown.notifications.NotificationManager import getNotificationManager
from toontown.notifications.notificationData.FriendRequestNotification import FriendRequestNotification
from toontown.notifications.notificationData.GenericTextNotification import GenericTextNotification
from otp.otpbase import OTPLocalizer


class FriendInvitee(DirectObject.DirectObject):
    """Altis friend-request backend displayed through Clash's alert ribbon."""

    notify = DirectNotifyGlobal.directNotify.newCategory('FriendInvitee')

    def __init__(self, avId, avName, avDNA, context, **kw):
        DirectObject.DirectObject.__init__(self)
        self.avId = avId
        self.avDNA = avDNA
        self.context = context
        self.avName = avName
        self.notification = None
        self.responded = False

        self.accept('cancelFriendInvitation', self.__handleCancelFromAbove)

        if len(base.localAvatar.friendsList) >= MaxFriends:
            self.__sendTooManyResponse()
            self.notification = GenericTextNotification(
                title='Friend Request',
                subtitle=OTPLocalizer.FriendInviteeTooManyFriends % self.avName,
                dna=self.avDNA,
                onDismiss=self.cleanup,
                dedupeKey=('friend-request', self.avId))
        else:
            self.notification = FriendRequestNotification(
                avId=self.avId,
                name=self.avName,
                dna=self.avDNA,
                onYes=self.__accept,
                onNo=self.__reject,
                onDismiss=self.__reject)

        getNotificationManager().addNotification(self.notification)

    def __sendTooManyResponse(self):
        responseContext = self.context
        self.context = None
        self.responded = True
        if responseContext is not None:
            base.cr.friendManager.up_inviteeFriendResponse(3, responseContext)
        else:
            avatarFriendsManager = getattr(base.cr, 'avatarFriendsManager', None)
            if avatarFriendsManager is not None:
                avatarFriendsManager.sendRequestRemove(self.avId)

    def __respond(self, accepted):
        if self.responded:
            self.cleanup()
            return

        self.responded = True
        responseContext = self.context
        self.context = None

        if responseContext is not None:
            response = 1 if accepted else 0
            base.cr.friendManager.up_inviteeFriendResponse(response, responseContext)
        else:
            avatarFriendsManager = getattr(base.cr, 'avatarFriendsManager', None)
            if avatarFriendsManager is not None:
                if accepted:
                    avatarFriendsManager.sendRequestInvite(self.avId)
                else:
                    avatarFriendsManager.sendRequestRemove(self.avId)

        self.cleanup()

    def __accept(self):
        self.__respond(True)

    def __reject(self):
        self.__respond(False)

    def cleanup(self):
        self.ignoreAll()
        self.context = None
        friendManager = getattr(base.cr, 'friendManager', None)
        if getattr(base, 'friendMode', 0) == 1 and friendManager is not None and \
                hasattr(friendManager, 'executeGameSpecificFunction'):
            friendManager.executeGameSpecificFunction()

    def __handleCancelFromAbove(self, context=None):
        if context is not None and context != self.context:
            return
        self.context = None
        self.responded = True
        manager = getNotificationManager()
        if self.notification is not None:
            manager.removeNotification(self.notification, invokeDismiss=False)
        self.cleanup()
