from typing import Optional, List

from prisma.enums import ClubNameStatus, ClubInfractionType

from direct.distributed.DistributedObjectGlobalUD import DistributedObjectGlobalUD
from requests import Response

from toontown.ai.exceptions.EntityNotFoundException import EntityNotFoundException
from toontown.chat.constants import ChatGlobals
from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.club import ClubEnums, ClubGlobals, ClubLocalizer, ClubTaskPricing
from toontown.club.ClubClasses import ClubIcon, ClubTask, ClubLog
from toontown.club.ClubContainerUD import ClubContainerUD
from toontown.club.ClubEnums import ClubNotification, ClubRank, ChangableClubNameStates
from toontown.club.ClubGlobals import ClubMaxCoins, ClubMaxJellybeans, ClubItemIndex, ClubLogsPerPage
from toontown.club.ClubsServiceUD import ClubsServiceUD
from toontown.toonbase import TTLocalizer
from toontown.uberdog.CachedToonStats import CachedToonStats
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.RateLimiter import RateLimiter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.uberdog.ToontownUberRepository import ToontownUberRepository


@DirectNotifyCategory()
class DistributedClubManagerUD(DistributedObjectGlobalUD):
    """
    The DistributedClubManagerUD is responsible for handling
    most (if not all) backend actions for managing Clubs.
    """

    def __init__(self, air: 'ToontownUberRepository') -> None:
        """
        Initialize the DistributedClubManagerUD.

        :param air: The AI repository to be attached to.
        """
        super().__init__(air)
        self.air = air

        # Load base stuff
        self.notify.info("Initializing...")
        self.avIdRateLimiter = {}

        # Create Club Service
        self._clubsService: Optional[ClubsServiceUD] = None

        # Accept calls
        self.accept('UD_ToonJoined', self.toonOnline)
        self.accept('UD_ToonLeft',   self.toonOffline)

       # self.air.netMessenger.accept("onAvatarDeleted", self, self.toonDeleted) We'll comment this out as ToontownInteralRepository does not have netmessages

    def announceGenerate(self):
        super().announceGenerate()
        self._clubsService = self.air.clubsService

    """
    Disband Club
    """

    def disbandClub(self,
                    clubId: int,
                    avId: Optional[int] = None,
                    isForceDisband: bool = False,
                    infractionId: Optional[int] = None,
                    chatMessage: Optional[str] = None
                    ) -> None:
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer:
            self.notify.warning(f"Tried to disband club ID {clubId} but it doesn't exist!")
            return

        if avId is None:
            avIds = clubContainer.getAvIds()
        else:
            avIds = [avId]
        self._clubsService.disbandClub(clubId, avId, avIds, isForceDisband, infractionId, chatMessage=chatMessage)

    def reinstateClub(self, clubId):
        club = self._clubsService.internal_getClubById(clubId, True)
        if not club.deletedAt:
            self.notify.warning(f"Tried to reinstate club ID {clubId} but it exists!")
            return

        ownerClubToon = self._clubsService.getClubOwner(clubId, includeDeleted=True)
        ownerOtherClubToons = self._clubsService.findClubIdByMemberAvId(ownerClubToon.avId)
        if ownerOtherClubToons:
            self.notify.warning(f"Tried to reinstate club ID {clubId} but owner {ownerClubToon.avId} has already joined another Club!")
            return

        self._clubsService.reinstateClub(clubId)

    def toonOnline(self, avId: int):
        clubContainer = self._clubsService.getCachedClub(avId=avId)
        if not clubContainer:
            return

        # Update everyone in the club.
        self.updateMembersOfClub(clubId=clubContainer.getClubId())

    def toonOffline(self, avId: int):
        clubContainer = self._clubsService.getCachedClub(avId=avId)
        if not clubContainer:
            return

        # Update everyone in the club. about the change.
        self.updateMembersOfClub(clubId=clubContainer.getClubId())

    def toonDeleted(self, avId: int):
        """When a toon is deleted, we need to remove them from their club."""
        clubContainer = self._clubsService.getCachedClub(avId=avId)
        if not clubContainer:
            return

        # Were they the owner?
        if clubContainer.isAvIdOwner(avId):
            # They were the owner, kill
            self.disbandClub(clubContainer.getClubId(), avId, chatMessage='The owner of your Club has deleted their Toon, disbanding the Club.')
        else:
            # They were not the owner, regular remove them
            self.requestLeaveClub(avId)

    """
    Creating Clubs
    """

    def requestCreateClubAI(self, avId: int, clubName: str, defaultName: str, clubIcon) -> None:
        """
        Sent from the AI.
        Requests to create a new Club given the avId, along
        with some set defaults for the paramters of the Club.

        :param avId: The avId attempting to create a club.
        :param clubName: The name of the club being made. Already validated on the AI.
        :param defaultName: The default name of the club.
        :param clubIcon: Information to create the clubIcon.
        :return: None.
        """
        if self.rateLimited(avId):
            # Ignore ratelimit checks from this call!
            # Very high-priority.
            return

        if self._clubsService.getCachedClub(avId=avId):
            # While theoretically we should be able to support multiple toons in one club,
            # we're taking a step back to ensure only one toon per club.
            self.air.writeServerEvent('suspicious', avId, "Toon tried to create a club even though they're already in one!")
            return

        self.notify.info(f"Got a request to make a club for avId {avId}")

        account = self.air.mongodb.astron.objects.find_one({
            "dclass": "Account",
            "fields.ACCOUNT_AV_SET": {"$elemMatch": {"$eq": avId}}
        })
        if not account or not account.get("fields") or not account["fields"].get("WEBSITE_USER_ID"):
            # Account doesn't exist?
            self.air.writeServerEvent('suspicious', avId, "Toon tried to create a club but no account ID?")
            return

        club = self._clubsService.createClub(
            name=clubName,
            defaultName=defaultName,
            ownerAccountId=account["fields"]["WEBSITE_USER_ID"],
            ownerAvId=avId,
            clubIcon=ClubIcon.fromStruct(clubIcon),
        )

        self.requestAvatarSync(avId)

        self.notify.info("Completed creating new club.")
        self.sendUpdateToAvatarId(
            avId, 'clubNotification', [ClubNotification.ClubCreation_Success, []]
        )
        self.updateMembersOfClub(club.id)

        # Send name approval call.
        clubContainer = self._clubsService.getCachedClub(clubId=club.id)
        self.sendNameApproval(avId, clubContainer, clubName, creating=True)

        # Go ahead and finalize creation.
        self.sendUpdate('UD_finalizeCreation', [avId])

    """
    Club Name Approval
    """

    def sendNameApproval(self, avId: int, clubContainer: ClubContainerUD, name: str, creating: bool=False):
        """
        Sends a POST to the rpcClient for club name approval.

        :param avId: The doId of the toon that requested the name.
        :param clubContainer: The club's club container.
        :param name: The name of the club.
        :param creating: True if we're creating the Club for the first time, False if just changing name of existing Club.
        """
        # Prevent duplicate name requests from coming through
        # If we want to allow this, we need a new API endpoint.
        if clubContainer.nameStatus == ClubNameStatus.NAME_REQUESTED and not creating:
            return

        # Send the request to the API
        clubId = clubContainer.getClubId()
        self.notify.debug(f"Name Request: Sending request for club {clubId}")
        self._clubsService.setRequestedName(clubId, name)
        response: Optional[Response] = self.air.rpcClient.call('gs/names/club/+', json={
            "avid": avId,
            "name": name
        })

        # If we can't contact the API, set the name to deny.
        if response is None or response.status_code != 200:
            self.notify.warning(f"Name Request ({clubId}): Failed to contact API!")
            self._clubsService.failClubName(clubId)
            return

        # Parse the JSON response from the server.
        responseData = response.json()
        if not responseData.get("status"):
            self.notify.warning(f"Name Request ({clubId}): Failed to send request - {responseData.get('reason')}")
            self._clubsService.failClubName(clubId)
            return

        self._clubsService.setClubNameRequestId(clubId, int(responseData.get("requestid")))

    def handleClubNameApproved(self, nameRequestId: int):
        try:
            club = self._clubsService.getClubByNameRequestId(nameRequestId, includeDeleted=True)
        except EntityNotFoundException:
            self.notify.warning(f"Got club name approved for nameRequestId {nameRequestId} but can't find the Club.")
            return

        # We still handle cases where the Club is deleted but the name got approved, just in case we need to undo
        # the delete.
        self._clubsService.approveClubName(club.id)
        if club.deletedAt is None:
            self.requestClubAvatarSync(club.id)

    def handleClubNameRejected(self, nameRequestId: int, denyReason: str):
        try:
            club = self._clubsService.getClubByNameRequestId(nameRequestId, includeDeleted=True)
        except EntityNotFoundException:
            self.notify.warning(f"Got club name rejected for nameRequestId {nameRequestId} but can't find the Club.")
            return

        # We still handle cases where the Club is deleted but the name got approved, just in case we need to undo
        # the delete.
        self._clubsService.rejectClubName(club.id, denyReason=denyReason)

    def requestUpdateClubName(self, name: str) -> None:
        """
        Sent from the Client.
        Requests a brand new club name.

        :param name: The name of the club to try to rewrite to.
        """
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            return

        if self.rateLimited(avId):
            # Ignore ratelimit checks from this call!
            # Very high-priority.
            pass

        clubContainer = self._clubsService.getCachedClub(avId=avId)
        if not clubContainer:
            # This toon kind of needs to be in a club.
            self.air.writeServerEvent('suspicious', avId, "Toon tried rewrite a Club name for a club they're not in!")
            return

        # Is this Toon the owner?
        if not clubContainer.isAvIdOwner(avId):
            # This toon tried to change their club name for a club they don't own!
            self.air.writeServerEvent('suspicious', avId, "Toon tried rewrite a Club name for a club they don't own!")
            return

        # Is this club in a state that demands changing name?
        if clubContainer.nameStatus not in ChangableClubNameStates:
            # That shouldn't happen either.
            self.air.writeServerEvent('suspicious', avId, "Toon tried rewrite a Club name for a club in an"
                                                          "invalid nameStatus!")
            return

        # Sanity checks passed, attempt to update their club name.
        self.notify.info(f"Requesting a new name for {avId}'s club.")
        self.sendUpdateToAvatarId(
            avId, 'clubNotification', [ClubNotification.ClubCreation_Success, []]
        )
        self.sendNameApproval(avId, clubContainer, name, creating=False)

    """
    Leaving Clubs
    """

    def requestLeaveClub(self, avId: int, reason=ClubNotification.UserLeftClub) -> None:
        """
        Requests an avId to leave their club.

        :param avId: The avId to remove.
        :param reason: The reason to remove them.
        :return: None.
        """
        clubContainer = self._clubsService.getCachedClub(avId=avId)
        if not clubContainer:
            self.notify.warning(f"User {avId} tried to leave their club but it doesn't exist!")
            return

        self._clubsService.leaveClub(clubContainer.getClubId(), avId)
        self.sendUpdateToAvatarId(avId, "clubNotification", [reason, []])

        # Force club update.
        self.requestAvatarSync(avId)

    """
    Club Invite
    """

    def inviteAvIdToClubAI(self, inviterAvId: int, targetAvId: int, clubId: int):
        """
        The AI has confirmed that this invite was approved.
        We validate it directly on the UD end for club-related affairs just in case.
        """
        # First thing's first, get the club.
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)

        if not clubContainer:
            # Club doesn't exist -- either clubId is fake or club disbanded.
            self.sendUpdate("respondToClubInviteUD", [inviterAvId, targetAvId, clubId, 0])
            return

        # The target has the permission to do this, yes?
        # This also confirms that the inviter is in the club.
        if not clubContainer.avIdHasPermission(inviterAvId, ClubEnums.CAN_INVITE_TOONS):
            # Nope, they don't have the right to do this.
            self.sendUpdate("respondToClubInviteUD", [inviterAvId, targetAvId, clubId, 0])
            return

        # The club's not full, right?
        if clubContainer.isClubFull():
            # Yikes, club is full already.
            self.sendUpdate("respondToClubInviteUD", [inviterAvId, targetAvId, clubId, 0])
            return

        # Inviter isn't in a club as well, right?
        existingClub = self._clubsService.getCachedClub(avId=targetAvId)

        if existingClub:
            # targetAvId is NOT supposed to be in a club. Kinda cringe.
            self.sendUpdate("respondToClubInviteUD", [inviterAvId, targetAvId, clubId, 0])
            return

        # Is this club join locked?
        if clubContainer.hasInfraction(ClubInfractionType.JOIN_LOCK):
            # The club is join locked.
            self.sendUpdate("respondToClubInviteUD", [inviterAvId, targetAvId, clubId, 2])
            return

        # Well, the inviter has permission, the club is real, and the target isn't in a club.
        # Given that they have to have confirmed the invite at this point, and that AI
        # has done validation on the approval and that the target isn't banned,
        # we can go ahead and add them to this club now!
        self._clubsService.inviteAvToClub(clubId, targetAvId, inviterAvId, ClubRank.Member)
        self.requestAvatarSync(targetAvId)

        # In addition, let's make sure we go ahead and tell the AIs about the good news.
        self.sendUpdate("respondToClubInviteUD", [inviterAvId, targetAvId, clubId, 1])

    """
    Update club settings (permissions, management)
    """

    def requestOptionSet(self, roleId: int, permId: int, value: int) -> None:
        """Sets an individual option to update the club permissions."""
        avId = self.air.getAvatarIdFromSender()

        # Get their club.
        clubContainer = self._clubsService.getCachedClub(avId=avId)
        if not clubContainer:
            self.air.writeServerEvent('suspicious', avId,
                                      "Toon tried to update club settings.. but they're NOT IN A CLUB!!")
            return

        # They better be an owner.
        if not clubContainer.isAvIdOwner(avId):
            self.air.writeServerEvent('suspicious', avId,
                                      "Non-leader attempted to update club settings... What a fool.")
            return

        # Set the club's permissions now.
        self._clubsService.updateClubPermissionOption(clubContainer.getClubId(), roleId, permId, value)

    def requestKickToon(self, clubId: int, targetAvId: int):
        """A toon has requested to kick this toon."""
        # Find the club.
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer:
            return
        assailantId = self.air.getAvatarIdFromSender()
        assailant = clubContainer.getClubToon(assailantId)
        if assailantId not in clubContainer.getAvIds():
            return
        kickedToon = clubContainer.getClubToon(targetAvId)
        if targetAvId not in clubContainer.getAvIds():
            return

        # Make sure they have permission to kick.
        if not clubContainer.avIdHasPermission(assailantId, ClubGlobals.CAN_KICK_TOONS):
            return

        # The assailant must have a higher role than the target.
        if kickedToon.rankId >= assailant.rankId:
            return

        self._clubsService.kickFromClub(clubContainer.getClubId(), targetAvId, assailantId)

    def requestRankChange(self, clubId: int, targetAvId: int, newRank: int):
        """The client has requested a rank change."""
        clubOwnerId = self.air.getAvatarIdFromSender()
        if self.rateLimited(clubOwnerId):
            return

        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer.isAvIdOwner(clubOwnerId):
            return

        targetClubToon = clubContainer.getClubToon(targetAvId)
        if not targetClubToon:
            return

        invokerClubToon = clubContainer.getClubToon(clubOwnerId)
        if not invokerClubToon:
            return

        targetAccount = self.air.mongodb.astron.objects.find_one({
            "dclass": "Account",
            "fields.ACCOUNT_AV_SET": {"$elemMatch": {"$eq": targetAvId}}
        })
        if not targetAccount or not targetAccount.get("fields") or not targetAccount["fields"].get("WEBSITE_USER_ID"):
            # Account doesn't exist?
            self.air.writeServerEvent(
                'suspicious',
                clubId,
                f"Toon {clubOwnerId} tried to transfer a club's ownership but target {targetAvId} has no account ID?"
            )
            return

        newRank = ClubRank(newRank)
        # Set the new rank.
        if newRank != ClubRank.Leader:
            self._clubsService.updateAvRank(clubContainer.getClubId(), clubOwnerId, targetClubToon.avId, newRank)

        else:
            # Looks like the role of Owner is being passed around!
            self._clubsService.transferLeader(
                clubContainer.getClubId(),
                clubOwnerId,
                targetClubToon.avId,
                targetAccount["fields"]["WEBSITE_USER_ID"]
            )

    def requestSelfLeaveClub(self, clubId: int):
        """The client has requested to leave the club."""
        avId = self.air.getAvatarIdFromSender()
        if self.rateLimited(avId):
            return

        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if clubContainer is None:
            return

        if avId not in clubContainer.getAvIds():
            self.air.writeServerEvent('suspicious', avId, f"av {avId} tried to leave a club {clubId} they're not in.")
            return

        if clubContainer.isAvIdOwner(avId):
            if len(clubContainer.getAvIds()) == 1 and clubContainer.getAvIds()[0] == avId:
                # Club only has one member (the av); perform disband
                self.disbandClub(clubId, avId)
            else:
                # We don't allow Club Leaders to leave without either first transferring ownership or
                # kicking all members in the Club first.
                # todo: tell the owner off
                self.notify.info(f"Club owner {avId} of club {clubId} tried to leave club but avIds is {clubContainer.getAvIds()}, failing.")
                return

        # Bye
        self.requestLeaveClub(avId, ClubNotification.UserLeftClub)

    """
    Club currency methods
    """

    def requestAddClubCoins(self, avId: int, clubId: int, clubCoins: float) -> None:
        """
        Receives a request from an avId to add club coins.
        """
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer:
            return

        if avId not in clubContainer.getAvIds():
            return

        if clubContainer.getClubCoins() >= ClubMaxCoins:
            return

        self._clubsService.addClubCoinsAndXp(clubContainer.getClubId(), clubCoins)

    def requestAddJellybeansAI(self, avId: int, clubId: int, jellybeans: int) -> None:
        """
        Receives a request from an avId to add jellybeans.

        :param avId:       The requester avId.
        :param clubId:     The clubID to add into.
        :param jellybeans: The jellybeans to add.
        """
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer:
            return

        if avId not in clubContainer.getAvIds():
            self.air.writeServerEvent('suspicious', avId, "Toon tried to add jellybeans.. but they're NOT IN A CLUB!!")
            return

        if clubContainer.getJellybeans() >= ClubMaxJellybeans:
            return

        self._clubsService.addJellybeans(clubId, jellybeans, avId)

    def requestPurchaseClubItem(self, clubItemId: int) -> None:
        """
        Receives a request from an avId to purchase a club item.
        """

        avId = self.air.getAvatarIdFromSender()
        if not avId:
            return
        # Don't send too many requests
        if self.rateLimited(avId):
            return

        def notifyFailure():
            self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubShop_Failure, []]
            )

        # Find the club.
        clubContainer = self._clubsService.getCachedClub(avId=avId)
        if not clubContainer:
            # OK ... mysterious. This is a fail.
            return notifyFailure()

        clubItem = ClubItemIndex.getItem(clubItemId)
        if not clubItem:
            return notifyFailure()

        if clubItem.getItemID() in clubContainer.itemsOwned:
            # Currently we only allow re-equipping Club Icon items.
            return self._clubsService.updateClubIcon(
                clubContainer.getClubId(), clubContainer.getClubIcon(), clubItem, avId=avId
            )

        # This one pretty much covers all the checks:
        if not clubItem.canPurchase(clubContainer, avId):
            return notifyFailure()

        # Pog. Go ahead and buy the item!!
        itemCost = clubItem.getCost(clubContainer)
        if clubItem.usesJellybeans(clubContainer):
            if clubContainer.getJellybeans() < itemCost:
                # We didn't have enough beans. Rolled
                return notifyFailure()
        else:
            if clubContainer.getClubCoins() < itemCost:
                # We didn't have enough coins. Rolled
                return notifyFailure()

        self._clubsService.purchaseClubItem(clubContainer.getClubId(), avId, clubItem, clubContainer)

        # Return success.
        self.sendUpdateToAvatarId(
            avId, 'clubNotification', [ClubNotification.ClubShop_Success, []]
        )

    """
    Avatar upkeeping
    """

    def setClubAvatarsOfClub(self, clubId: int):
        self.sendUpdate('setClubAvatarsOfClub', [clubId])

    def requestClubAvatarSync(self, clubId: int):
        """Requests all avatars in a club to sync."""
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if clubContainer:
            for avId in clubContainer.getAvIds():
                self.requestAvatarSync(avId)

    def requestAvatarSync(self, avId: int):
        """Requests an avatar sync, to maintain the av's
        local recognization of their club status."""
        self.sendUpdate('requestAvatarSync', [avId])

    # def broadcastClubScavenge(self, clubId: int, scavengeType: ScavengeType, extraArgs: Optional[list] = None):
    #     """
    #     Sends out a scavenge report to a Club.
    #     """
    #     if extraArgs is None:
    #         extraArgs = []
    #     self.sendUpdate('broadcastClubScavenge', [clubId, scavengeType, extraArgs])

    def sendClubCoinReport(self, clubId: int, coins: int):
        if not self._clubsService.getCachedClub(clubId=clubId):
            return
        self.sendUpdate('sendClubCoinReport', [clubId, coins])

    """
    Club task methods
    """

    def requestRerollTasks(self, clubId: int, taskIndex: int):
        """
        The client asks for tasks to be rerolled.

        :param clubId: ID of the club
        :param taskIndex: The task index to be rerolled.
        """
        # Ensure perms and things are lookin' good
        avId = self.air.getAvatarIdFromSender()
        if self.rateLimited(avId):
            # Shut up
            return

        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer:
            return

        if not clubContainer.avIdHasPermission(avId, ClubEnums.REROLL_CLUB_TASKS):
            # This avId does not have rights
            return

        if not (0 <= taskIndex < ClubGlobals.ClubTaskCount):
            # i hate you
            return

        clubTask = clubContainer.getClubTaskIndex(taskIndex)
        rerollCost = ClubTaskPricing.calculateRerollCost(clubTask.getChainId())
        if rerollCost > clubContainer.getJellybeans():
            return

        # OK, we can reroll tasks
        self.sendUpdateToAvatarId(
            avId, 'clubNotification', [ClubNotification.ClubTasks_Rerolled, [rerollCost]]
        )
        self._clubsService.rerollOfferedClubTasks(clubContainer.getClubId(), taskIndex, rerollCost, avId)

    def updateQuestProgress(self, clubId: int, chainIds: list, progress: list):
        """
        Updates quest progress for the club task

        :param clubId: The ID of the club to update
        :param chainIds: All the chainIds at each index.
        :param progress: List of integers to update progress onto
        """
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer:
            return

        # (applies progress cutely)
        clubTasks = clubContainer.getClubTasks()
        for index, data in enumerate(zip(clubTasks, progress)):
            clubTask, taskProgress = data
            if clubTask.getChainId() == chainIds[index]:
                clubTask.taskProgress[0] += taskProgress

        # Update club tasks.
        self._clubsService.setClubTasks(clubId, clubTasks)

    def sendClubTaskUpdate(self, clubId: int, context: int, clubTask: ClubTask):
        pass
        # self.broadcastClubScavenge(
        #     clubId=clubId,
        #     scavengeType=ScavengeType.ClubTask,
        #     extraArgs=[
        #         context,  # context
        #         clubTask.getChainId(),  # chain ID,
        #         clubTask.getClubCoinReward(),  # coin reward
        #     ]
        # )

    """
    Club log methods
    """

    def requestClubLogs(self, clubId: int, page: int):
        """
        An av's requests for club logs.

        :param clubId: The ID of the club to get logs from.
        :param page: What page of logs are requested.
        """
        # Is avId ratelimited?
        avId = self.air.getAvatarIdFromSender()
        if self.rateLimited(avId):
            # Shut up
            return

        # Get the club.
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer:
            return

        # The av is in this club, yeah?
        if avId not in clubContainer.getAvIds():
            # Somehow, they aren't. They do not get no logs !!!
            return

        # Get the logs on the right page.
        logs = self._clubsService.getClubLogs(clubContainer.getClubId()) or []
        logs = [log for log in logs if ClubLog.isTypeVisible(log.logType, log) and log.data] \
               [(page * ClubLogsPerPage):((page + 1) * ClubLogsPerPage)]

        # Send these logs to the client.
        self.sendUpdateToAvatarId(avId, 'receiveClubLogs', [ClubLog.toStructList(ClubLog.fromModelList(logs))])

    """
    Client requests
    """

    def requestNewMotd(self, clubId: int, animalType: str, motd: str):
        """Updates a club's MOTD."""
        avId = self.air.getAvatarIdFromSender()
        if self.rateLimited(avId):
            return

        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if not clubContainer:
            return
        if avId not in clubContainer.getAvIds():
            return
        if not clubContainer.avIdHasPermission(avId, ClubEnums.CAN_UPDATE_MOTD):
            return
        if clubContainer.hasInfraction(ClubInfractionType.MOTD_EDIT_LOCK):
            return

        # Scrub the message now.
        if animalType not in TTLocalizer.AnimalSounds:
            # They sent us a bad animal type, yikes
            return
        scrubbedMotdSmr = self.air.chatFilter.scrub_message(
            message=motd,
            scrubbed_word_prefix="\x01WLDisplay\x01",
            scrubbed_word_suffix="\x02",
            garbler_choices=TTLocalizer.AnimalSounds.get(animalType)
        )

        if scrubbedMotdSmr.is_blocklist_hit:
            # This message is inappropriate, do not set.
            return

        scrubbedMotd = scrubbedMotdSmr.scrubbed_message

        # Set the MOTD to this.
        if len(scrubbedMotd) > ClubGlobals.MaxMOTDLength:
            scrubbedMotd = scrubbedMotd[:ClubGlobals.MaxMOTDLength]

        # Get the chat message.
        toonStats = self.air.toonTracker.getToonStats(avId)
        chatMessage = ClubLocalizer.Update_SetMOTD.format(
            user=toonStats.getName() if toonStats else 'User',
            motd=scrubbedMotd,
        )

        self._clubsService.setClubMotd(clubContainer.getClubId(), scrubbedMotd, chatMessage)

    """
    Misc methods
    """

    def rateLimited(self, avId):
        if avId not in self.avIdRateLimiter:
            self.avIdRateLimiter[avId] = RateLimiter(max_hits=ClubGlobals.CLUB_UD_RATELIMITER_MAX_HITS, period=ClubGlobals.CLUB_UD_RATELIMITER_PERIOD)
        rateLimiter = self.avIdRateLimiter[avId]
        return rateLimiter.tryRequest()

    """
    Client/Server Upkeep
    """

    def flushClubState(self, avIds: Optional[List[int]] = None, chatMessage: Optional[str] = None, clubId: Optional[int] = None, dropClub: bool = False):
        """Flushes the club state for all avids."""
        if avIds:
            for avId in avIds:
                self.sendUpdateToAvatarId(avId, 'dropLocalClub', [])
            if chatMessage is not None:
                self.air.chatRouter.sendMessageToToons(
                    avIds, 0, 'Server',
                    ChatChannel.Clubs, ChatGlobals.Club_Update,
                    ChatContentType.Text, chatMessage,
                )
        if clubId is not None:
            if dropClub:
                # Disband the club entirely on the AI.
                self.air.netMessenger.send('clubContainerUpdateUD', [clubId, 0, 0])
                self.sendUpdate('AI_onClubDisband', [clubId])
            elif avIds:
                # Only clean out these avatars on the AI.
                self.sendUpdate('AI_dropClubAvatars', [avIds])

    def updateMembersOfClub(self,
                            clubId: int,
                            avIdRequested: Optional[List[int]] = None,
                            debounce: Optional[float] = None,
                            chatMessage: Optional[str] = None):
        """
        Update everybody in the Club about the current state of the Club.

        :param clubId: The ID of the club.
        :param avIdRequested: Is this request only going to certain avIds?
        :param debounce: A debounce time for the request.
        :param chatMessage: Send out this message to all members in the Club.
        """
        # Remove debounce tasks.
        # This is a terrifying panda3d way of debouncing (thank you rdb)
        avIdRequested = sorted(avIdRequested) if avIdRequested else None
        taskName = f"updateMembersOfClub-{clubId}-{avIdRequested}"
        self.removeTask(taskName)
        if debounce is not None:
            # Debounce this request.
            self.doMethodLater(
                delayTime=debounce,
                funcOrTask=self.updateMembersOfClub,
                name=taskName,
                extraArgs=[clubId, avIdRequested, None, chatMessage],
            )
            return

        # Create a ClubContainer with the given model.
        clubContainer = self._clubsService.getCachedClub(clubId=clubId)
        if clubContainer is None:
            return
        clubContainer.update(self.air)
        ccStruct = clubContainer.toStruct()

        # Figure out who we are sending this to.
        if avIdRequested is None:
            # Let's go with everyone in the club, along with the districts itself.
            avIds = clubContainer.getAvIds()

            # Figure out which districts the avIds are in, and update them.
            # for districtId in self.air.toonTracker.getDistrictIdsOfAvIds(*avIds):
            #     self.sendUpdateToAvatarId(districtId, 'toontownClubUpdate', [ccStruct])
            # TODO - make this actually target districts (above code doesnt work . . .)
            self.sendUpdate('toontownClubUpdate', [ccStruct])

            # Send to everyone in the club.
            for avId in avIds:
                self.sendUpdateToAvatarId(avId, 'toontownClubUpdate', [ccStruct])

            self.air.netMessenger.send('clubContainerUpdateUD', [clubId, 1, ccStruct])

            # Send a chat message out to them as well.
            if chatMessage:
                self.air.chatRouter.sendMessageToToons(
                    avIds, 0, 'Server',
                    ChatChannel.Clubs, ChatGlobals.Club_Update,
                    ChatContentType.Text, chatMessage,
                )
        else:
            # Just the folks in the requested list.
            for avId in avIdRequested:
                self.sendUpdateToAvatarId(avId, 'toontownClubUpdate', [ccStruct])

            # Send a chat message out to them as well.
            if chatMessage:
                self.air.chatRouter.sendMessageToToons(
                    avIdRequested, 0, clubContainer.getClubName(),
                    ChatChannel.Clubs, ChatGlobals.Club_Update,
                    ChatContentType.Text, chatMessage,
                )

    """
    Toon Stat Gathering
    """

    def handleAvIdCache(self, clubId: int, avIds: List[int]):
        """
        When a ClubContainerUD gets generated, it may be missing certain
        ToonStat information from the ToonTrackerUD because the Toons were offline.
        If that is the case, then we need to ask the ToonTrackerUD to get them for us.
        """
        self.air.toonTracker.askCache(*avIds, callback=lambda: self.updateMembersOfClub(clubId))

    def UD_queryClub(self, avId: int, clubDataEvent: str = 'clubData'):
        clientavId = self.air.getAvatarIdFromSender()
        if self.rateLimited(clientavId):
            return

        # Verify the clubDataEvent isnt stupid
        if clubDataEvent not in ('clubData', 'clubDataForAvatarPanel',):
            return

        def verifyStats(stats: CachedToonStats):
            # Called to verify if toon settings are appropriate for sending query response.
            if not (stats and stats.getSettings().getSetting('can-query-club')):
                self.sendUpdateToAvatarId(clientavId, 'queryClubResp', [[], clubDataEvent])
                return

            clubContainer = self._clubsService.getCachedClub(avId=avId)
            if not clubContainer:
                self.sendUpdateToAvatarId(clientavId, 'queryClubResp', [[], clubDataEvent])
                return

            self.sendUpdateToAvatarId(clientavId, 'queryClubResp', [[clubContainer.toStruct()], clubDataEvent])

        # We will need up to date info about the client's settings.
        self.air.toonTracker.getFreshToonStats(avId, callback=verifyStats)
