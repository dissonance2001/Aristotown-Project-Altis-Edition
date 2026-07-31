from pandac.PandaModules import *
from toontown.toonbase.ToontownGlobals import *
from direct.showbase import DirectObject
from direct.directnotify import DirectNotifyGlobal
from toontown.toontowngui import TTDialog
from otp.otpbase import OTPLocalizer
from toontown.toontowngui import ToonHeadDialog
from direct.gui.DirectGui import DGG
from otp.otpbase import OTPGlobals


class FriendInvitee(ToonHeadDialog.ToonHeadDialog):
    notify = DirectNotifyGlobal.directNotify.newCategory('FriendInvitee')

    def __init__(self, avId, avName, avDNA, context, **kw):
        self.avId = avId
        self.avDNA = avDNA
        self.context = context
        self.avName = avName

        if len(base.localAvatar.friendsList) >= MaxFriends:
            # Clear the context before sending a response.  The local friends
            # manager can synchronously emit UI/friend events while handling
            # this call; leaving the context set allowed cleanup() to send a
            # second response (2 / "unable to answer") before the real reply.
            responseContext = self.context
            self.context = None
            if responseContext is not None:
                base.cr.friendManager.up_inviteeFriendResponse(3, responseContext)
            else:
                avatarFriendsManager = getattr(base.cr, 'avatarFriendsManager', None)
                if avatarFriendsManager is not None:
                    avatarFriendsManager.sendRequestRemove(self.avId)
            text = OTPLocalizer.FriendInviteeTooManyFriends % self.avName
            style = TTDialog.Acknowledge
            buttonTextList = [OTPLocalizer.FriendInviteeOK]
            command = self.__handleOhWell
        else:
            text = OTPLocalizer.FriendInviteeInvitation % self.avName
            style = TTDialog.TwoChoice
            buttonTextList = [OTPLocalizer.FriendInviteeOK, OTPLocalizer.FriendInviteeNo]
            command = self.__handleButton

        optiondefs = (('dialogName', 'FriendInvitee', None),
         ('text', text, None),
         ('style', style, None),
         ('buttonTextList', buttonTextList, None),
         ('command', command, None),
         ('image_color', (1.0, 0.89, 0.77, 1.0), None),
         ('geom_scale', 0.2, None),
         ('geom_pos', (-0.1, 0, -0.025), None),
         ('pad', (0.075, 0.075), None),
         ('topPad', 0, None),
         ('midPad', 0, None),
         ('pos', (0.45, 0, 0.75), None),
         ('scale', 0.75, None))
        self.defineoptions(kw, optiondefs)
        ToonHeadDialog.ToonHeadDialog.__init__(self, self.avDNA)
        self.accept('cancelFriendInvitation', self.__handleCancelFromAbove)
        self.initialiseoptions(FriendInvitee)
        self.show()
        return

    def cleanup(self):
        # Take ownership of the pending context immediately.  This makes
        # cleanup re-entry harmless and guarantees that only one response is
        # ever sent for a legacy FriendManager request.
        responseContext = self.context
        self.context = None

        ToonHeadDialog.ToonHeadDialog.cleanup(self)
        self.ignore('cancelFriendInvitation')

        if responseContext is not None:
            base.cr.friendManager.up_inviteeFriendResponse(2, responseContext)

        if base.friendMode == 1 and hasattr(base.cr.friendManager, 'executeGameSpecificFunction'):
            base.cr.friendManager.executeGameSpecificFunction()
        return

    def __handleButton(self, value):
        # Clear the context before calling either backend.  Friend-list events
        # can be emitted during the call on a local server, and those events
        # may clean up this dialog.  Previously that cleanup sent response 2
        # first, which made the inviter display "was unable to answer."
        responseContext = self.context
        self.context = None

        if responseContext is not None:
            if value == DGG.DIALOG_OK:
                response = 1
            else:
                response = 0
            base.cr.friendManager.up_inviteeFriendResponse(response, responseContext)
        else:
            avatarFriendsManager = getattr(base.cr, 'avatarFriendsManager', None)
            if avatarFriendsManager is not None:
                if value == DGG.DIALOG_OK:
                    avatarFriendsManager.sendRequestInvite(self.avId)
                else:
                    avatarFriendsManager.sendRequestRemove(self.avId)

        self.cleanup()
        return

    def __handleOhWell(self, value):
        self.cleanup()

    def __handleCancelFromAbove(self, context=None):
        if context is None or context == self.context:
            self.context = None
            self.cleanup()
        return
