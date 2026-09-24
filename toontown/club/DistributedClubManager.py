from typing import TYPE_CHECKING, Optional

from prisma.enums import ClubLogType

from direct.distributed.DistributedObjectGlobal import DistributedObjectGlobal
from direct.showbase.MessengerGlobal import messenger

from toontown.club import ClubLocalizer
from toontown.club.ClubClasses import *
from toontown.club.ClubContainerClient import ClubContainerClient
from toontown.club.ClubEnums import ClubNotification
from toontown.notifications.notificationData.GenericTextNotification import GenericTextNotification, GenericTextId
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.quest3.questlines.ClubsQuestLine import *  # required import

if TYPE_CHECKING:
    from toontown.utils.BuiltinHelper import *


CLIENT_UPDATE_TIME = 5


@DirectNotifyCategory()
class DistributedClubManager(DistributedObjectGlobal):
    """
    The DistributedClubManager is a client-sided representation
    of the Client and the club that they are a part of.
    """
    notification = 'ReceiveClubNotification'

    def __init__(self, cr):
        DistributedObjectGlobal.__init__(self, cr)
        self.cr = cr

        # club data
        self.inClub = False
        self.clubContainer: Optional[ClubContainerClient] = None

        # other club values
        self.onlinePlayersInClub = 0

        # handle calls
        self.accept(self.notification, self.onClubNotification)
        self.accept('inviteAvIdToClub', self.inviteAvIdToClub)
        self.accept('respondToClubInvite', self.respondToClubInvite)
        self.accept('clientLogout', self.cleanupClubState)

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedObjectGlobal.announceGenerate(self)

    def delete(self):
        DistributedObjectGlobal.delete(self)
        self.cr.clubMgr = None
        self.ignoreAll()

    def disable(self):
        self.notify.debug("Disabling ClubManager.")
        DistributedObjectGlobal.disable(self)

    def generate(self):
        self.notify.debug("Generated ClubManager.")
        DistributedObjectGlobal.generate(self)

    def cleanupClubState(self):
        self.inClub = False
        self.clubContainer = None

    """
    Club Updates
    """

    def toontownClubUpdate(self, astronClub):
        """Receive a club update from UD."""
        if not hasattr(base, 'localAvatar'):
            # Dude, we haven't loaded in-game yet --- chill out!!
            return

        # Make our temp club container for use.
        receivedClubContainer: ClubContainerClient = ClubContainerClient.fromStruct(astronClub)

        # Make sure that we are actually in this club.
        if not receivedClubContainer.avIdInClub(self.localAvId):
            # We're not in this club. Check for transition.
            self.exitClub()
            return

        # We are definitely in this club!
        self.clubContainer = receivedClubContainer
        self.enterClub()
        messenger.send('clubUpdate')

    def dropLocalClub(self):
        """
        Leave our club.
        Sent from UD.
        """
        self.exitClub()

    """
    Client Requests
    """

    def setMotd(self, motd: str):
        """Ask to update our MOTD."""
        if len(motd) > MaxMOTDLength:
            motd = motd[:MaxMOTDLength]
        self.sendUpdate('setMotd', [motd])

        # Set it locally as well (assume success).
        self.clubContainer.motd = motd

    def requestCreateClub(self, name: str, icon: ClubIcon):
        """
        Requests to create a club.
        :param name: The name of the club.
        :param icon: The club's icon.
        """
        self.sendUpdate(
            'requestCreateClubCL', [name, icon.toStruct()]
        )

    def requestUpdateClubName(self, name: str):
        """
        Requests to update our Club name.
        :param name: The new name of the Club.
        """
        self.sendUpdate(
            'requestUpdateClubName', [name]
        )

    def requestPurchaseClubItem(self, clubItem: ClubItem):
        """
        Requests to purchase a Club Item.
        :param clubItem: The item to purchase.
        """
        self.sendUpdate(
            'requestPurchaseClubItem', [clubItem.toStruct()]
        )

    def requestOptionSet(self, roleId: int, permId: int, value: int):
        self.sendUpdate('requestOptionSet', [roleId, permId, value])

    def requestRerollTasks(self, clubId: int, taskIndex: int):
        self.sendUpdate('requestRerollTasks', [clubId, taskIndex])

    def requestNewMotd(self, clubId: int, motd: str):
        self.sendUpdate('requestNewMotd', [clubId, base.localAvatar.getStyle().getType(), motd])

    def requestKickToon(self, clubId: int, avId: int):
        self.sendUpdate('requestKickToon', [clubId, avId])

    def requestRankChange(self, clubId: int, avId: int, newRank: int):
        self.sendUpdate('requestRankChange', [clubId, avId, newRank])

    def requestAddJellybeans(self, clubId: int, jellybeans: int):
        self.sendUpdate('requestAddJellybeansCL', [clubId, jellybeans])

    def requestSelfLeaveClub(self, clubId: int):
        """Requests to leave a club."""
        self.sendUpdate('requestSelfLeaveClub', [clubId])

    """
    Club Invites
    """

    def inviteAvIdToClub(self, avId: int):
        """
        Initiates the request to invite an avId to the Club.

        :param avId:   The avId to invite.
        :param clubId: The ID of the Club.
        """
        if not self.clubContainer:
            return
        clubId = self.clubContainer.getClubId()
        self.sendUpdate(
            "inviteAvIdToClubCL", [avId, clubId]
        )

    def respondToClubInvite(self, avId: int, clubId: int, result: int):
        """
        Responds to an invite to join a club.

        :param avId:   The avId who we are responding to.
        :param clubId: The clubId we're interested in joining.
        :param result: The result of our invite (1 yes, 0 no)
        """
        self.sendUpdate(
            "respondToClubInviteCL", [avId, clubId, result]
        )

    """
    Club Logs
    """

    def requestClubLogs(self, clubId: int, page: int):
        """Requests some gamer club logs. Pages start at 0, just like in real life."""
        self.sendUpdate('requestClubLogs', [clubId, page])

    def receiveClubLogs(self, logs):
        """Receives some AWESOME club logs."""
        messenger.send('receiveClubLogs', [ClubLog.fromStructList(logs)])

    """
    Handle Informs
    """

    def clubNotification(self, context: int, args: list):
        """Called from the server about a club change the client should know about."""
        context = ClubNotification(context)
        messenger.send(self.notification, [context, args])

    def onClubNotification(self, context: ClubNotification, args: list):
        # Process club notification data.
        if context in (ClubNotification.UserLeftClub,
                       ClubNotification.UserKickedFromClub):
            if self.exitClub():
                if context == ClubNotification.UserLeftClub:
                    base.localAvatar.addNotification(GenericTextNotification(
                        textId=GenericTextId.ClubStatus,
                        title='Left Club',
                        subtitle=ClubLocalizer.ClubLeaveReasons['left'],
                    ))
                elif context == ClubNotification.UserKickedFromClub:
                    base.localAvatar.addNotification(GenericTextNotification(
                        textId=GenericTextId.ClubStatus,
                        title='Left Club',
                        subtitle=ClubLocalizer.ClubLeaveReasons['kicked'],
                    ))

    """
    Club Transitions
    """

    def enterClub(self):
        """Sent when we just join a club.
        Currently also calls on client load."""
        if self.inClub is True:
            return False
        self.inClub = True
        messenger.send("enterClub")
        return True

    def exitClub(self):
        """Sent when we just exit a club."""
        if self.inClub is False:
            return False
        self.inClub = False
        self.clubContainer = None
        messenger.send("exitClub")
        return True

    """
    Getters
    """

    def isInClub(self):
        return self.inClub

    def getLocalClub(self):
        return self.clubContainer

    """
    Properties
    """

    @property
    def localAvId(self):
        """Gets the localAvId."""
        return base.localAvatar.getDoId()

    def queryClub(self, avId: int, clubDataEvent: str = 'clubData'):
        self.sendUpdate('UD_queryClub', [avId, clubDataEvent])

    def queryClubResp(self, clubStruct, clubDataEvent: str = 'clubData'):
        if clubStruct:
            clubContainer = ClubContainerClient.fromStruct(clubStruct[0])
            messenger.send(clubDataEvent, [clubContainer])
        else:
            messenger.send(clubDataEvent, [None])
