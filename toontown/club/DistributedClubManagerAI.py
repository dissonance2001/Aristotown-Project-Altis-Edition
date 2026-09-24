from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from toontown.club import ClubLocalizer
from toontown.club.ClubClasses import *
from toontown.club.ClubContainerAI import ClubContainerAI

from typing import Optional
from typing import TYPE_CHECKING

from toontown.club.ClubEnums import ClubNotification, CAN_INVITE_TOONS
from toontown.notifications.notificationData.ClubJellybeansNotification import ClubJellybeansNotification
from toontown.notifications.notificationData.ClubInviteNotification import ClubInviteNotification
from toontown.quest3.QuestEnums import QuesterType
from toontown.quest3.base.QuestContext import QuestContext
from toontown.quest3.base.Quester import Quester
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.quest3.questlines.ClubsQuestLine import *  # required import

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


@DirectNotifyCategory()
class DistributedClubManagerAI(DistributedObjectGlobalAI):
    def __init__(self, air):
        DistributedObjectGlobalAI.__init__(self, air)
        self.air = air  # type: ToontownAIRepository
        self.allowList = self.air.allowList
        self.blockList = self.air.blockList

        # We keep up with a dict of all club containers.
        # Dict goes from (clubId: clubContainer).
        # (Technically this won't clean up clubs that get disbanded,
        # but this should never be an issue)
        self.clubContainers = dict()

        # Dual dict linking avIds to Clubs and vice versa.
        self.avIdToClubIds = dict()  # type: Dict[int, set]
        self.clubIdToAvIds = dict()  # type: Dict[int, set]

        # For some club IDs, we need to update the avs in them when we next update.
        self.clubIdsToUpdateAvs = set()

        # Accept some calls.
        self.accept('progressObjective', self.onProgressObjective)

    def delete(self):
        super().delete()
        self.ignoreAll()

    """
    Avatar keepup
    """

    def requestAvatarSync(self, avId):
        av = self.air.doId2do.get(avId)
        if av:
            self.updateClubAvatarAI(av)

    def updateClubAvatarAI(self, av: DistributedToonAI):
        # Set them to a club.
        clubIds = self.avIdToClubIds.get(av.getDoId(), None)
        if clubIds is None:
            return av.setToClub()
        for clubId in clubIds:
            clubContainer = self.clubContainers.get(clubId, None)  # type: ClubContainerAI
            if clubContainer is None:
                continue
            av.setToClub(clubContainer)
            return
        av.setToClub()

    def setClubAvatarsOfClub(self, clubId: int):
        """
        Performs setToClub of all avs within a Club.
        Used to update nametag colors, generally.

        :param clubId: The clubId.
        """
        self.clubIdsToUpdateAvs.add(clubId)

    def sendClubCoinReport(self, clubId: int, clubCoins: int):
        """
        Sends the club coin report to all avs.

        :param clubId: The ID of the club to report to.
        :param clubCoins: The amount of coins earned.
        """
        for avId in self.clubIdToAvIds.get(clubId, set()):
            av = self.air.doId2do.get(avId)  # type: DistributedToonAI
            if not av:
                continue
            if not av.getSettings().getSetting('show-clubcoin-reward'):
                return

            # Send them a scavenge for being a good boy
            # av.queueScavenge(
            #     amount=clubCoins,
            #     scavengeType=ScavengeType.ClubCoins,
            #     extraArgs=[ClubCoinAnnouncementPeriod],
            # )

    """
    Club updates/getters
    """

    def toontownClubUpdate(self, astronClub):
        """Receive a club update from UD."""
        # Make our temp club container for use.
        receivedClubContainer: ClubContainerAI = ClubContainerAI.fromStruct(astronClub)
        clubId = receivedClubContainer.id
        self.clubContainers[clubId] = receivedClubContainer

        # This may be slow ... but we need to keep up with avIds to Clubs as well.
        newClubAvIds = set(receivedClubContainer.getAvIds())
        oldClubAvIds = self.clubIdToAvIds.get(clubId, set())
        addedAvIds = set()
        removedAvIds = set()

        # For each avId in the old set, if it is not in the new one,
        # then we need to purge the club from its avIdToClubIds reference.
        for avId in oldClubAvIds:
            if avId not in newClubAvIds:
                # This avId was removed from the club container.
                clubSet = self.avIdToClubIds.get(avId, set())
                clubSet.discard(clubId)
                self.avIdToClubIds[avId] = clubSet
                removedAvIds.add(avId)

        # For each avId in the new set, if it is not in the old one,
        # then we need to add the club into its avIdToClubIds reference.
        for avId in newClubAvIds:
            if avId not in oldClubAvIds:
                # This avId was added to the club container.
                clubSet = self.avIdToClubIds.get(avId, set())
                clubSet.add(clubId)
                self.avIdToClubIds[avId] = clubSet
                addedAvIds.add(avId)

        # Now set the clubIdToAvids.
        self.clubIdToAvIds[clubId] = newClubAvIds

        # Update avs now.
        for avId in receivedClubContainer.getAvIds():
            av = self.air.doId2do.get(avId)
            if not av:
                continue
            av.setToClub(receivedClubContainer)

    def getAvIdClubIds(self, avId: int) -> set:
        return self.avIdToClubIds.get(avId, set())

    def getClub(self, clubId: int) -> ClubContainerAI:
        return self.clubContainers.get(clubId)

    def AI_onClubDisband(self, clubId: int):
        """When a club disbands, we need to clear out our cache of avIds."""
        # If the AI knows this club ID whatsoever ...
        if clubId in self.clubIdToAvIds:

            # Check out every avId still stored in this club.
            for avId in self.clubIdToAvIds[clubId]:

                # If this avId exists in our cache,
                if avId in self.avIdToClubIds:

                    # remove the club ID from its set, and clean up if necessary
                    self.avIdToClubIds[avId].discard(clubId)
                    if not self.avIdToClubIds[avId]:
                        del self.avIdToClubIds[avId]
            del self.clubIdToAvIds[clubId]

    def AI_dropClubAvatars(self, avIds: list):
        # Check out all of the avIds we have received.
        for avId in avIds:
            # Do we have it cached?
            if avId in self.avIdToClubIds:

                # Start clearing it out -- check all of its club ids
                for clubId in self.avIdToClubIds[avId]:
                    # If this avId is associated with the club, remove it, and cleanup the club if necessary
                    self.clubIdToAvIds[clubId].discard(avId)
                    if not self.clubIdToAvIds[clubId]:
                        del self.clubIdToAvIds[clubId]

                # Now make sure it is not in the set anymore.
                del self.avIdToClubIds[avId]

    """
    Client requests
    """

    def requestCreateClubCL(self, name: str, clubIconStruct: list, forceAvid: int = None):
        """
        Creates a club with the given parameters.

        :param name: The name of the club.
        :param clubIconStruct: Struct information for a clubIcon.
        :param forceAvid: Force creates a club for this avId. Used for commands.
        """
        avId = forceAvid or self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId,
                                      "Toon ID was called to create a club, but toon isn't in an active district.")
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_GeneralError, []]
            )

        # Sanity checks on the club icon.
        clubIcon = ClubIcon.fromStruct(clubIconStruct)
        if ClubItemIndex.getItem(clubIcon.clubCol) not in DefaultClubThemeCols:
            self.air.writeServerEvent(
                'suspicious', avId,
                "Toon ID tried to make a club with a non-default theme color.")
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_GeneralError, []]
            )

        if ClubItemIndex.getItem(clubIcon.bgCol) not in DefaultClubIconBgCols:
            self.air.writeServerEvent(
                'suspicious', avId,
                "Toon ID tried to make a club with a non-default BG color.")
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_GeneralError, []]
            )

        if ClubItemIndex.getItem(clubIcon.iconId) not in DefaultClubIconGeoms:
            self.air.writeServerEvent(
                'suspicious', avId,
                "Toon ID tried to make a club with an unavailable geom ID.")
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_GeneralError, []]
            )

        if ClubItemIndex.getItem(clubIcon.backgroundId) not in DefaultClubIconBgs:
            self.air.writeServerEvent(
                'suspicious', avId,
                "Toon ID tried to make a club with an unavailable bg ID.")
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_GeneralError, []]
            )

        # Sanity checks on the user.
        if av.isClubBanned():
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_ClubBanned, []]
            )

        # Is this toon in a club?
        if av.clubIds:
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_AlreadyInClub, []]
            )

        # Is this club name BL'd?
        if self.blockList.is_message_blocked(name):
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_NameBlocked, []]
            )

        # Is this club name AL'd?
        for word in name.split(' '):
            if not self.allowList.is_word_allowed(word):
                return self.sendUpdateToAvatarId(
                    avId, 'clubNotification', [ClubNotification.ClubCreation_NameBlocked, []]
                )

        # Our validation is good -- let's move on.
        if av.getTotalMoney() >= ClubCreationCost:
            defaultName = ClubLocalizer.ClubDefaultName % (av.getName().split(' ')[-1])
            self.sendUpdate('requestCreateClubAI', [avId, name, defaultName, clubIconStruct])
        else:
            return self.sendUpdateToAvatarId(
                avId, 'clubNotification', [ClubNotification.ClubCreation_TooPoor, []]
            )

    def UD_finalizeCreation(self, avId):
        """Takes money from an av after they create a club successfully."""
        av = self.air.doId2do.get(avId)
        if not av:
            return
        av.takeMoney(ClubCreationCost)

    def leaveClub(self, avId: int):
        """
        Inquires an avatar to leave a club.

        :param avId: The avId attempting to leave their club.
        """
        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId, "Toon ID called to leave club, but isn't in district.")
            return

        self.sendUpdate('requestLeaveClub', [avId, av.getName()])

    """
    Club Currency setters
    """

    def addClubCoins(self, avId: int, clubId: int, clubCoins: float) -> None:
        """
        Increments the club coins of our club.

        :param avId: The toon requesting to add club coins.
        :param clubId: The club ID
        :param clubCoins: The amount of club coins to add.
        """
        av = self.air.doId2do.get(avId)
        if not av:
            self.air.writeServerEvent('suspicious', avId, "Toon ID attempted to add club coins, but isn't in district.")
            return

        if not 0 <= clubCoins <= ClubMaxCoins:
            self.air.writeServerEvent('suspicious', avId, f"Toon ID attempted to add an invalid amount of coins. {clubCoins}")
            return

        self.sendUpdate('requestAddClubCoins', [avId, clubId, clubCoins])

    def addClubCoinsForAvatars(self, avatars, clubCoins, overrideAv=None) -> None:
        """Handles giving club coins to avatars based on
        the club that each is in. If two or more are in the same club,
        each of those avatars will contribute the given amount of club coins
        to their club.

        :param avatars: The list of avatars. (i.e the avatars in an instance)
        :param clubCoins: The amount of club coins to give to each eligible avatar,
        either as a float or a dictionary of each avId and the club coins that they'll
        contribute.
        :param overrideAv: In cases where rewards are given individually, we want to
        be able to give each reward separately while checking if they're eligible for
        doing so.
        """
        # Create a dict of every club id and the members of said club.
        activeClubs = {}
        for avatar in avatars:
            # Random sanity check just to be sure
            if not avatar:
                continue

            # If the avatar is in a club, add them and their club to the dict.
            for clubId in self.getAvIdClubIds(avatar.doId):
                if clubId not in activeClubs:
                    activeClubs[clubId] = []
                activeClubs[clubId].append(avatar)

        # Iterate a list of avatars from clubs which have more than
        # two members currently present.
        for clubId, avatarList in activeClubs.items():
            if len(avatarList) < 2:
                continue

            # The club coins can be either a dict or a float, make sure we're grabbing
            # the correct value.
            coins: float = clubCoins.get(avatar.doId) if isinstance(clubCoins, dict) else clubCoins

            # Allow for (just) the override avatar to contribute, and sanity check the
            # coins just in case.
            if overrideAv in (None, avatar) and coins is not None:
                self.addClubCoins(avatar.doId, clubId, coins * NaturalClubCoinMultiplier)

    def requestAddJellybeansCL(self, clubId: int, jellybeans: int) -> None:
        """
        Takes jellybeans from a toon and gives it to the club.

        :param clubId:     The club ID to put jellybeans in from.
        :param jellybeans: The amount of jellybeans to add.
        """
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)  # type: DistributedToonAI
        if not av:
            self.air.writeServerEvent('suspicious', avId, "Toon ID attempted to add jellybeans, but isn't in district.")
            return

        if av.getTotalMoney() < jellybeans:
            self.air.writeServerEvent('suspicious', avId, "Toon ID attempted to add more jellybeans than they owned.")
            return

        # OK, seems good. Take their money and move on.
        if av.takeMoney(deltaMoney=jellybeans):
            self.sendUpdate('requestAddJellybeansAI', [avId, clubId, jellybeans])
            av.addNotification(ClubJellybeansNotification(
                state=ClubJellybeansNotification.state_success,
                clubId=clubId,
                beans=jellybeans,
            ))

    """
    Club Invite management
    """

    def inviteAvIdToClubCL(self, targetAvId: int, clubId: int):
        """
        Initiated request from an av to invite an avId to the Club.

        :param targetAvId:   The avId to invite.
        :param clubId: The ID of the Club.
        """
        inviterAvId = self.air.getAvatarIdFromSender()

        # Don't invite yourself.
        if targetAvId == inviterAvId:
            return

        # Make sure the avs are real.
        inviter = self.air.doId2do.get(inviterAvId)  # type: DistributedToonAI
        target = self.air.doId2do.get(targetAvId)    # type: DistributedToonAI

        if not inviter:
            self.air.writeServerEvent(
                'suspicious', inviter, "Toon ID attempted to invite into club, but was not in district.")
            return

        if not target:
            # Tell them the target must be local.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_notnearby,
                sendToInviter=True,
            )
            return

        # OK, we need to obtain their clubs.
        invitersClubs = self.getAvIdClubIds(inviterAvId)
        targetsClubs = self.getAvIdClubIds(targetAvId)

        # Make sure these make sense!
        if clubId not in invitersClubs:
            # They tried to invite to a club they weren't in??
            self.air.writeServerEvent('suspicious', inviter, "Toon ID attempted to invite in a club they weren't in.")
            return

        if clubId in targetsClubs:
            # OK, they are already in this club.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_they_in_our_club,
                sendToInviter=True,
            )
            return

        if len(targetsClubs) >= MaxClubsPerToon:
            # This target is already in a club.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_they_in_some_club,
                sendToInviter=True,
            )
            return

        # Club IDs look good... now we need the actual club structs.
        clubContainer: ClubContainerAI = self.getClub(clubId)

        if not clubContainer:
            # This club literally does not exist. Maybe desync?
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_tryagain_later,
                sendToInviter=True,
            )
            return

        if not clubContainer.avIdHasPermission(inviterAvId, CAN_INVITE_TOONS):
            # The avId does not have invite perms.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_no_perms,
                sendToInviter=True,
            )
            return

        # Ensure that they are friends.
        if not inviter.isFriendsWith(targetAvId):
            # Nah, they'll have to be friends first!
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_not_friends,
                sendToInviter=True,
            )
            return

        # Ensure they aren't club banned.
        if target.isClubBanned():
            # Yikes, they're banned. Let's... deny for them.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_denied,
                sendToInviter=True,
            )
            return

        # Make sure that they want club invites.
        if not target.getSettings().getSetting('acceptingClubInvites'):
            # OK, tell the inviter that they are unaccepting of new invites.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_unaccepting,
                sendToInviter=True,
            )
            return

        # The club isn't full, right?
        if clubContainer.isClubFull():
            # Club full.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_club_full,
                sendToInviter=True,
            )
            return

        # I believe we have checked everything at this point.
        # Go ahead and forward the notifs to the users.
        self.sendInviteNotification(
            inviterId=inviterAvId, targetId=targetAvId,
            inviteState=ClubInviteNotification.state_sent,
            clubContainer=clubContainer,
            sendToInviter=True,
        )
        self.sendInviteNotification(
            inviterId=inviterAvId, targetId=targetAvId,
            inviteState=ClubInviteNotification.state_received,
            clubContainer=clubContainer,
            sendToTarget=True,
        )

    def respondToClubInviteCL(self, inviterAvId: int, clubId: int, result: int):
        """
        Response to an invite to join a club.

        :param inviterAvId:   The avId who we are responding to.
        :param clubId: The clubId we're interested in joining.
        :param result: The result of our invite (1 yes, 0 no)
        """
        targetAvId = self.air.getAvatarIdFromSender()

        # Don't invite yourself.
        if targetAvId == inviterAvId:
            return

        # Make sure the avs are real.
        inviter = self.air.doId2do.get(inviterAvId)  # type: DistributedToonAI
        target = self.air.doId2do.get(targetAvId)  # type: DistributedToonAI

        if not inviter and (result and target):
            # The inviter is gone, so we tell the target that the invite has expired.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_expired,
                sendToTarget=True,
            )
            return

        if not target and inviter:
            # The target is gone, so we tell the inviter that the invite has expired.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_expired,
                sendToInviter=True,
            )
            return

        if not (target and inviter):
            # Yeah, they're not real. Bye!
            return

        if not result:
            # The request was denied.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_denied,
                sendToInviter=True,
            )
            return

        # Ensure they aren't club banned again.
        if target.isClubBanned():
            # Yikes, they're banned. Let's... deny for them.
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_denied,
                sendToInviter=True,
            )
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                inviteState=ClubInviteNotification.state_expired,
                sendToTarget=True,
            )
            return

        # We can skip a lot of validation this time... for now.
        # We're going to rely on the UD to do the final club-related validations for us.
        self.sendUpdate(
            "inviteAvIdToClubAI",
            [inviterAvId, targetAvId, clubId]
        )

    def respondToClubInviteUD(self, inviterAvId: int, targetAvId: int, clubId: int, result: int):
        """
        The UD tells us if the response to an invite was successful or not.
        This call is sent to all districts, so make sure we can find the inviter and target.

        :param inviterAvId: The inviter's avId.
        :param targetAvId:  The target's avId.
        :param clubId: The ID of the club.
        :param result: The result of the invite.
        """
        # Make sure the avs are real.
        inviter = self.air.doId2do.get(inviterAvId)  # type: DistributedToonAI
        target = self.air.doId2do.get(targetAvId)  # type: DistributedToonAI
        clubContainer: ClubContainerAI = self.getClub(clubId)

        if not clubContainer:
            # Uh, this is awkward. We really do need this!
            # It's OK if the inviter and target exist though,
            # they just won't get the confirmation callback
            # (this is likely to happen as a result of a desync)
            return

        if inviter:
            inviteState = {
                1: ClubInviteNotification.state_accepted,
                2: ClubInviteNotification.state_we_joinlocked,
            }.get(result, ClubInviteNotification.state_tryagain_later)
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                clubContainer=clubContainer,
                inviteState=inviteState,
                sendToInviter=True,
            )

        if target:
            inviteState = {
                1: ClubInviteNotification.state_welcome,
                2: ClubInviteNotification.state_they_joinlocked,
            }.get(result, ClubInviteNotification.state_expired)
            self.sendInviteNotification(
                inviterId=inviterAvId, targetId=targetAvId,
                clubContainer=clubContainer,
                inviteState=inviteState,
                sendToTarget=True,
            )

    def sendInviteNotification(self, inviterId: int, targetId: int,
                               inviteState: int, clubContainer: ClubContainerAI = None,
                               sendToInviter: bool = False, sendToTarget: bool = False):
        """
        Sends an invite notification to a toon.

        :param inviterId: The inviter's id.
        :param targetId:  The target's id.
        :param inviteState:   The state of the notification.
        :param clubContainer: The associated club container.
        :param sendToInviter: Are we sending this notif to the inviter?
        :param sendToTarget:  Are we sending this notif to the target?
        :return:
        """
        # Get avatars
        inviter: DistributedToonAI = self.air.doId2do.get(inviterId)
        target: DistributedToonAI = self.air.doId2do.get(targetId)

        # Scrape club data.
        if clubContainer:
            clubIcon = clubContainer.getClubIcon()
            clubId = clubContainer.getClubId()
            clubName = clubContainer.getClubName()
            clubLevel = clubContainer.getClubLevel()
            iconId, backgroundId, clubCol, bgCol = clubIcon.toStruct()
        else:
            clubId = 0
            clubName = ''
            clubLevel = 1
            iconId, backgroundId, clubCol, bgCol = (0, 0, 0, 0)

        if (not inviter and sendToInviter) or (not target and sendToTarget):
            DistributedClubManagerAI.notify.warning(
                f'sendInviteNotification: invalid notification: inviter {inviter} target {target}')
            return

        # Send notif.
        if sendToInviter:
            targetName = target.getName() if target else ''
            inviter.addNotification(ClubInviteNotification(
                clubId=clubId,
                clubLevel=clubLevel,
                iconId=iconId,
                backgroundId=backgroundId,
                clubCol=clubCol,
                bgCol=bgCol,
                avId=targetId,
                toonName=targetName,
                clubName=clubName,
                inviteState=inviteState,
            ))
        if sendToTarget:
            inviterName = inviter.getName() if inviter else ''
            target.addNotification(ClubInviteNotification(
                clubId=clubId,
                clubLevel=clubLevel,
                iconId=iconId,
                backgroundId=backgroundId,
                clubCol=clubCol,
                bgCol=bgCol,
                avId=inviterId,
                toonName=inviterName,
                clubName=clubName,
                inviteState=inviteState,
            ))

    """
    Club Task Management
    """

    def onProgressObjective(self, quester: Quester, context: QuestContext):
        """
        Called whenever any objective gets progressed.
        """
        if quester.questerType == QuesterType.Toon:
            # We'll progress the same Club on a club container -- that is, if it exists!
            quester: DistributedToonAI
            clubIds = self.getAvIdClubIds(quester.getDoId())

            # Iterate over all clubIds and progress their task.
            for clubId in clubIds:
                clubContainer = self.getClub(clubId)

                # I hope the club container exists!
                if not clubContainer:
                    continue

                # The club container exists, so we can progress this task on them.
                self.air.quest3Manager.progressObjective(quester=clubContainer, context=context)

    def updateQuestProgressAI(self, clubId: int, chainIds: list, progress: list):
        """Updates quest progress for a club."""
        self.sendUpdate('updateQuestProgress', [clubId, chainIds, progress])

    # def broadcastClubScavenge(self, clubId: int, scavengeType: ScavengeType, extraArgs: list):
    #     """
    #     Gives everyone in the Club a scavenge notification.
    #
    #     :param clubId:       The club ID to send a scavenge update to.
    #     :param scavengeType: The type of scavenge to update.
    #     :param extraArgs:    Any additional arguments.
    #     """
    #     clubContainer: ClubContainerAI = self.getClub(clubId)
    #     if not clubContainer:
    #         return
    #
    #     for avId in clubContainer.getAvIds():
    #         av: Optional[DistributedToonAI] = self.air.doId2do.get(avId)
    #         if not av:
    #             continue
    #
    #         # Queue their scavenge.
    #         av.queueScavenge(
    #             amount=1,
    #             scavengeType=scavengeType,
    #             extraArgs=extraArgs,
    #         )
