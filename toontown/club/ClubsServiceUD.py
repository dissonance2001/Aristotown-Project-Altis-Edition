import math
import random
import time
from copy import deepcopy
from typing import Optional, List, Tuple

from prisma import Json
from prisma.client import Prisma
from prisma.enums import ClubNameStatus, ClubLogType
from prisma.models import Club, ClubInfraction, ClubToon

from toontown.ai.exceptions.EntityNotFoundException import EntityNotFoundException
from toontown.ai.exceptions.InvalidStateException import InvalidStateException
from toontown.club import ClubGlobals, ClubLocalizer
from toontown.club.ClubClasses import ClubTask, ClubIcon, ClubSettings
from toontown.club import ClubClasses
from toontown.club.ClubContainerUD import ClubContainerUD
from toontown.club.ClubEnums import ClubRank
from toontown.club.ClubGlobals import ClubItem, ClubItemType, ClubBoosterHours, DefaultClubName
from toontown.club.NetClubCache import NetClubCache
from toontown.club.db.ClubPostgresDatabaseUD import ClubPostgresDatabaseUD

from typing import TYPE_CHECKING

from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.questlines.ClubsQuestLine import ClubsQuestLine  # required for club task functionality
from toontown.uberdog.ToonTrackerUD import ToonTrackerUD

if TYPE_CHECKING:
    from toontown.uberdog.ToontownUberRepository import ToontownUberRepository
    from toontown.club.ClubCoinServiceUD import ClubCoinServiceUD

ONE_DAY = 60 * 60 * 24


class ClubsServiceUD:
    def __init__(self, air: 'ToontownUberRepository', db: ClubPostgresDatabaseUD):
        self.air = air
        self.db = db

        # We cache avIds to clubIds for club existence checks.
        self._clubCache = NetClubCache(air, netHook=False)

    """
    Cache management
    """

    def requestCacheUpdate(self, clubId: int, status: Optional[int] = 1):
        """
        Requests the cache to be updated for a Club.
        """
        if status == 0:
            # Force clear the cache for this Club.
            return self._clubCache.onClubUpdate(clubId, 0, None)

        # Get the updated club container and cache it.
        clubContainer = self._getUpdatedClubContainer(clubId=clubId)
        if clubContainer:
            self._clubCache.onClubUpdate(clubId, status, clubContainer)
        else:
            self._clubCache.onClubUpdate(clubId, 0, None)

    def getCachedClub(self, clubId: Optional[int] = None, avId: Optional[int] = None) -> Optional[ClubContainerUD]:
        if not self._clubCache.hasCachedData(clubId=clubId, avId=avId):
            # We need to get cached data for this input.
            clubContainer = self._getUpdatedClubContainer(clubId=clubId, avId=avId)
            if clubContainer:
                # Slot in the cached data for this group.
                self._clubCache.onClubUpdate(
                    clubId=clubContainer.getClubId(),
                    status=1,
                    clubContainer=clubContainer,
                )
            elif avId:
                # There is no club data here.
                self._clubCache.onNoClubUpdate(avId)

        return self._clubCache.getClub(clubId=clubId, avId=avId)

    def _getUpdatedClubContainer(self, clubId: Optional[int] = None, avId: Optional[int] = None) -> Optional[ClubContainerUD]:
        """
        Given a club id, gets its club container.
        """
        if avId:
            clubId = self.findClubIdByMemberAvId(avId)
            if clubId is None:
                return None
        if clubId:
            try:
                club = self.internal_getClubById(clubId)
            except EntityNotFoundException:
                return None
        else:
            return None

        # Create a ClubContainer with the given model.
        return ClubContainerUD.makeContainerFromModel(air=self.air, club=club)

    """
    Properties
    """

    @property
    def mgr(self):
        """:rtype DistributedClubManagerUD"""
        return self.air.clubsManager

    @property
    def tt(self):
        """:rtype: ToonTrackerUD"""
        return self.air.toonTracker

    @property
    def clubCoinService(self):
        """:rtype: ClubCoinServiceUD"""
        return self.air.clubCoinService

    # region Club Info Getters
    def internal_getClubById(self, clubId: int, includeDeleted: bool = False) -> Club:
        result = self.db.getClubById(clubId, includeDeleted)
        if not result:
            raise EntityNotFoundException

        return result

    def getClubByNameRequestId(self, nameRequestId: int, includeDeleted: bool = False) -> Club:
        result = self.db.getClubByNameRequestId(nameRequestId, includeDeleted)
        if not result:
            raise EntityNotFoundException

        return result
    # endregion

    # region Club Membership
    # region Club Membership Getters
    def getClubMembersByClubId(self, clubId: int) -> List[ClubClasses.ClubToon]:
        clubContainer = self.getCachedClub(clubId=clubId)
        if clubContainer is None:
            return []
        return clubContainer.getClubToons()

    def getClubLeadership(self, clubId: int) -> List[ClubClasses.ClubToon]:
        toons = self.getClubMembersByClubId(clubId)
        return [toon for toon in toons if toon.rankId in [ClubRank.Leader, ClubRank.Deputy]]

    def getClubOwner(self, clubId: int, includeDeleted: bool=False) -> ClubToon:
        clubToons = self.db.findAllClubToonsByClubIdAndRank(clubId, [ClubRank.Leader], includeDeleted=includeDeleted)
        if len(clubToons) != 1:
            raise InvalidStateException(f"Club {clubId} has not enough / too many owners: {str(clubToons)}")

        return clubToons[0]

    def findClubIdByMemberAvId(self, avId: int) -> Optional[int]:
        clubToon = self.db.findClubJoinByMemberAvId(avId)
        if not clubToon:
            return None
        if clubToon.deletedAt:
            return None
        return clubToon.clubId
    # endregion Club Membership Getters

    # region Club Membership Setters
    def inviteAvToClub(self, clubId: int, targetAvId: int, inviterAvId: int, rank: ClubRank):
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            club = self.db.getClubById(clubId, _db=db)
            existingToon = self.db.findClubJoinByClubIdAndMemberAvId(targetAvId, clubId, includeDeleted=True, _db=db)
            if existingToon:
                self.db.deleteClubToon(existingToon.id, purge=True, _db=db)
            self.db.createClubToon(club.id, targetAvId, rank.value, inviterAvId, _db=db)
            self.db.createClubLog(
                club.id,
                ClubLogType.INVITED_TO_CLUB,
                {'avId': targetAvId, 'invitedBy': inviterAvId},
                _db=db
            )
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.broadcastClubUpdate(clubId)

    def leaveClub(self, clubId: int, avId: int):
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            club = self.db.getClubById(clubId, _db=db)
            clubToon = self.db.findClubJoinByClubIdAndMemberAvId(avId, club.id, _db=db)
            self.db.deleteClubToon(clubToon.id, _db=db)
            self.db.createClubLog(club.id, ClubLogType.LEFT_CLUB, {'avId': avId}, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.broadcastClubUpdate(
                clubId,
                chatMessage=ClubLocalizer.Update_MemberLeft % self.tt.getToonName(avId)
            )
            # Tell them the update too. This lets them know they are No Longer Present
            self.flushClubState([avId], clubId=clubId)

    def kickFromClub(self, clubId: int, avId: int, requestedBy: int):
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            club = self.db.getClubById(clubId, _db=db)
            clubToon = self.db.findClubJoinByClubIdAndMemberAvId(avId, club.id, _db=db)
            self.db.deleteClubToon(clubToon.id, _db=db)
            self.db.createClubLog(club.id, ClubLogType.KICKED_FROM_CLUB, {'avId': avId, 'requestedBy': requestedBy}, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.broadcastClubUpdate(
                clubId,
                chatMessage=ClubLocalizer.Update_MemberKicked % self.tt.getToonName(avId)
            )
            # Tell them the update too. This lets them know they are No Longer Present
            self.flushClubState([avId], clubId=clubId)

    def updateAvRank(self, clubId: int, invokerAvId: int, targetAvId: int, rankId: ClubRank):
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            invokerClubToon = self.db.findClubJoinByClubIdAndMemberAvId(invokerAvId, clubId, _db=db)
            targetClubToon = self.db.findClubJoinByClubIdAndMemberAvId(targetAvId, clubId, _db=db)
            oldRank = targetClubToon.rankId

            self.db.updateClubToonRank(targetClubToon.id, rankId, _db=db)
            self.db.createClubLog(
                clubId,
                ClubLogType.USER_RANK_CHANGED,
                data={
                    'changedBy': invokerClubToon.avId,
                    'targetAvId': targetAvId,
                    'oldRank': oldRank,
                    'newRank': rankId,
                },
                _db=db
            )
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.broadcastClubUpdate(
                clubId,
                chatMessage=ClubLocalizer.Update_RoleChange.format(
                    user=self.tt.getToonName(targetAvId),
                    gaming='promoted' if rankId > oldRank else 'demoted',
                    role=ClubLocalizer.ClubRoleNames.get(rankId, ''),
                )
            )

    def transferLeader(self, clubId: int, invokerAvId: int, targetAvId: int, targetAccountId: int):
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            invokerClubToon = self.db.findClubJoinByClubIdAndMemberAvId(invokerAvId, clubId, _db=db)
            targetClubToon = self.db.findClubJoinByClubIdAndMemberAvId(targetAvId, clubId, _db=db)

            self.db.updateClubToonRank(targetClubToon.id, ClubRank.Leader, _db=db)
            self.db.updateClubToonRank(invokerClubToon.id, ClubRank.Member, _db=db)
            self.db.setClubOwner(clubId, targetAvId, targetAccountId, _db=db)
            self.db.createClubLog(
                clubId,
                ClubLogType.LEADER_TRANSFERRED,
                data={
                    'changedBy': invokerClubToon.avId,
                    'targetAvId': targetAvId,
                },
                _db=db
            )
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.broadcastClubUpdate(
                clubId,
                chatMessage=ClubLocalizer.Update_RoleChange.format(
                    user=self.tt.getToonName(targetAvId),
                    gaming='promoted',
                    role=ClubLocalizer.ClubRoleNames.get(ClubRank.Leader),
                )
            )
    # endregion Club Membership Setters
    # endregion Club Membership

    # region Club creating, editing and deleting
    def createClub(self, name: str, defaultName: str, ownerAccountId: int, ownerAvId: int, clubIcon: ClubIcon):
        # Generate an initial list of tasks, one task for each ClubTaskDuration value (easy, medium, hard)
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            existingToon = self.db.findClubJoinByMemberAvId(ownerAvId, includeDeleted=True, _db=db)
            if existingToon:
                self.db.deleteClubToon(existingToon.id, purge=True, _db=db)
            club = self.db.createClub(
                name=defaultName,
                requestedName=name,
                ownerAccountId=ownerAccountId,
                ownerAvId=ownerAvId,
                clubIcon=clubIcon,
                clubTasks=self._makeClubTasks(avIds=[ownerAvId]),
                capacity=ClubGlobals.ClubMinSize,
                dailyCoins=0,
                clubXp=0,
                clubCoins=0,
                jellybeans=0,
                _db=db
            )
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.requestCacheUpdate(club.id)
            return club

    def disbandClub(self,
                    clubId: int,
                    initiatedBy: Optional[int] = None,
                    avIds: List[int] = None,
                    isForceDisband: bool = False,
                    infractionId: Optional[int] = None,
                    chatMessage: Optional[str] = None
                    ) -> None:
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            self.db.deleteAllClubToonByClubId(clubId, _db=db)
            self.db.disbandClub(clubId, _db=db)
            if isForceDisband:
                self.db.createClubLog(clubId, ClubLogType.CLUB_FORCE_DISBANDED, {
                    "initiatedBy": initiatedBy,
                    "infractionId": infractionId,
                    "remainingAvids": avIds
                }, _db=db)
            else:
                self.db.createClubLog(clubId, ClubLogType.CLUB_DISBANDED, {
                    "initiatedBy": initiatedBy,
                    "remainingAvids": avIds
                }, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            # Tell them the update too. This lets them know they are No Longer Present
            self.flushClubState(avIds, chatMessage=chatMessage, clubId=clubId, dropClub=True)

    def reinstateClub(self, clubId: int) -> None:
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            self.db.reinstateClub(clubId, _db=db)
            clubToons = self.db.findAllClubToonsByClubId(clubId, includeDeleted=True, _db=db)
            for clubToon in clubToons:
                # Check if Toon has already joined another Club
                existingClubJoin = self.db.findClubJoinByMemberAvId(clubToon.avId, _db=db)
                if not existingClubJoin:
                    self.db.reinstateClubToonById(clubToon.id, _db=db)
            self.db.createClubLog(clubId, ClubLogType.CLUB_REINSTATED, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            club = self.getCachedClub(clubId=clubId)
            # Tell them the update too. This lets them know they are Once Again Present
            self.flushClubState(club.getAvIds(), chatMessage="Your Club has been reinstated by the Corporate Clash Crew. You may need to close the game and log back in to see the reinstated Club.", clubId=clubId)

    def setClubMotd(self, clubId: int, motd: str, chatMessage: str, _db: Optional[Prisma] = None) -> None:
        if not self.getCachedClub(clubId=clubId):
            return
        self.db.setClubMotd(clubId, motd)
        self.broadcastClubUpdate(clubId, chatMessage=chatMessage)
    # endregion

    # region Club Items
    def purchaseClubItem(self, clubId: int, purchaserAvId: int, clubItem: ClubItem, clubContainer: ClubContainerUD):
        tx = self.db.getTransaction()

        try:
            db = tx.start()

            # We already know we have enough money ... So take it
            itemCost = clubItem.getCost(clubContainer)
            if clubItem.usesJellybeans(clubContainer):
                self.db.addJellybeans(clubId, -itemCost, _db=db)
            else:
                self.db.addClubCoins(clubId, -itemCost, _db=db)

            # Money has been taken. So cool!! Let's give them the item.
            if clubItem.storesId():
                self.db.addOwnedClubItem(clubId, clubItem.itemID, _db=db)

            # Log that the item has been bought.
            self.db.createClubLog(
                clubId,
                ClubLogType.BOUGHT_ITEM,
                data={
                    'itemId': clubItem.itemID,
                    'purchaserAvId': purchaserAvId
                },
                _db=db
            )
            
            if clubItem.type in [ClubItemType.CLUB_ICON, ClubItemType.CLUB_BACKGROUND, ClubItemType.CLUB_THEME_COL, ClubItemType.CLUB_BG_COL]:
                self.updateClubIcon(clubContainer.getClubId(), clubContainer.clubIcon, clubItem, avId=purchaserAvId, notify=False, _db=db)

            elif clubItem.type == ClubItemType.CLUB_NAME_CHANGE:
                self.db.setClubNameStatus(clubContainer.getClubId(), ClubNameStatus.NAME_CHANGING, _db=db)

            elif clubItem.type == ClubItemType.CLUB_MEMBER_SLOTS:
                _, newMembers = ClubGlobals.calculateClubCapacityUpgrade(clubContainer.getCapacity(), True)
                self.db.setClubCapacity(clubContainer.getClubId(), newMembers, _db=db)

            elif clubItem.type == ClubItemType.CLUB_BOOSTER_SLOTS:
                self.db.setClubMaxBoosters(clubContainer.getClubId(), clubContainer.getMaxBoosters() + 1, _db=db)

            elif clubItem.type == ClubItemType.CLUB_BOOSTERS:
                # Add the booster to be active on the club. Yippee!!
                endTimestamp = int(time.time()) + (ClubBoosterHours * 60 * 60)
                self.db.giveClubBooster(clubContainer.getClubId(), clubItem.getValue(), endTimestamp, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            # Format update message.
            itemTypeName, prefix, suffix, superPrefix, superSuffix = ClubGlobals.ClubItemTypeToName.get(clubItem.getType())
            extension = ''
            if clubItem.getType() in (ClubItemType.CLUB_ICON, ClubItemType.CLUB_BACKGROUND, ClubItemType.CLUB_THEME_COL,
                                      ClubItemType.CLUB_BG_COL, ClubItemType.CLUB_BOOSTERS):
                extension = f': {clubItem.getName()}'
            self.broadcastClubUpdate(
                clubId,
                chatMessage=ClubLocalizer.Update_ItemPurchase.format(
                    user=self.tt.getToonName(purchaserAvId),
                    item= f'{superPrefix}{prefix}{itemTypeName}{extension}'
                )
            )

    def updateClubIcon(self, clubId: int, clubIcon: ClubIcon, clubItem: ClubItem, avId: int = 0, notify: bool = True, _db: Optional[Prisma] = None):
        itemID = clubItem.getItemID()

        if clubItem.getType() == ClubItemType.CLUB_ICON:
            clubIcon.iconId = itemID
        elif clubItem.getType() == ClubItemType.CLUB_BACKGROUND:
            clubIcon.backgroundId = itemID
        elif clubItem.getType() == ClubItemType.CLUB_THEME_COL:
            clubIcon.clubCol = itemID
        elif clubItem.getType() == ClubItemType.CLUB_BG_COL:
            clubIcon.bgCol = itemID
        else:
            # This item cannot be equipped... ignore
            return

        self.db.setClubIcon(clubId, clubIcon, _db)
        self.broadcastClubUpdate(
            clubId,
            chatMessage=(ClubLocalizer.Update_ClubIcon.format(user=self.tt.getToonName(avId))) if notify else None
        )

    # endregion

    # region Club Roles
    def updateClubPermissionOption(self, clubId: int, roleId: int, permId: int, value: int):
        """
        Updates the club's permission option.

        NB: THIS OPERATION IS NOT ATOMIC!
        """
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            club = self.db.getClubById(clubId, _db=db)
            oldSettings = ClubSettings.fromDict(club.clubSettings)

            newSettings = deepcopy(oldSettings)
            if roleId == ClubRank.Deputy:
                newSettings.deputySettings.setOptionValue(permId, value)
            elif roleId == ClubRank.Officer:
                newSettings.officerSettings.setOptionValue(permId, value)
            elif roleId == ClubRank.Member:
                newSettings.memberSettings.setOptionValue(permId, value)

            self.db.setClubSettings(clubId, newSettings.toDict(), _db=db)
            self.db.createClubLog(
                clubId,
                ClubLogType.SETTINGS_UPDATED,
                data={
                    'oldSettings': Json(oldSettings.toDict()),
                    'newSettings': Json(newSettings.toDict())
                },
                _db=db
            )
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.broadcastClubUpdate(clubId, debounce=0.05)
    # endregion

    # region Club Currencies
    def addClubCoins(self, clubId: int, clubCoins: float, avId: Optional[int] = None, viaShortcut = False):
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            club = self.db.getClubById(clubId, _db=db)
            self.db.addClubCoins(clubId, clubCoins, _db=db)
            self.db.createClubLog(
                clubId,
                ClubLogType.EARNED_CLUB_XP,
                data={
                    'avId': avId,
                    'amount': clubCoins,
                    'viaShortcut': viaShortcut
                },
                _db=db
            )
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.clubCoinService.fileTaxes(clubId=club.id, startCoin=club.clubCoins, earnings=clubCoins)
            self.broadcastClubUpdate(clubId, debounce=0.30)

    def addJellybeans(self, clubId: int, jellybeans: int, avId: Optional[int] = None, viaShortcut = False):
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            self.db.addJellybeans(clubId, jellybeans, _db=db)
            self.db.createClubLog(
                clubId,
                ClubLogType.EARNED_JELLYBEANS,
                data={
                    'avId': avId,
                    'amount': jellybeans,
                    'viaShortcut': viaShortcut
                },
                _db=db
            )
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.broadcastClubUpdate(clubId, debounce=0.30)

    def addClubXp(self, clubId: int, clubXp: int):
        club = self.getCachedClub(clubId)

        oldXp = club.clubXp
        newXp = oldXp + clubXp
        self.db.addClubXp(clubId, clubXp)
        self._broadcastLevelUp(clubId, club.name, oldXp, newXp)

    def addClubCoinsAndXp(self, clubId: int, clubCoins: float) -> None:
        club = self.getCachedClub(clubId)

        # Current we have a 1:1 relationship between club coins and XP.
        oldXp = club.clubXp
        earnedXp = math.ceil(clubCoins)
        newXp = oldXp + earnedXp
        self.db.addClubCoinsAndClubXp(clubId, clubCoins, earnedXp)
        self.clubCoinService.fileTaxes(clubId=clubId, startCoin=club.clubCoins, earnings=clubCoins)
        self._broadcastLevelUp(clubId, club.name, oldXp, newXp)

    def _broadcastLevelUp(self, clubId: int, clubName: str, oldXp: float, newXp: float) -> None:
        """
        Handles the club update broadcasting for XP gains.
        """
        oldLevel, newLevel = self._checkLevelUp(oldXp, newXp)
        if newLevel is None:
            self.broadcastClubUpdate(clubId, debounce=0.30)
            return

        self.db.createClubLog(
            clubId,
            ClubLogType.CLUB_PROMOTED,
            data={
                'oldLevel': oldLevel,
                'newLevel': newLevel
            },
        )
        self.broadcastClubUpdate(
            clubId,
            chatMessage=ClubLocalizer.Update_LevelUp.format(
                name=clubName,
                level=newLevel,
            )
        )

    @staticmethod
    def _checkLevelUp(oldXp: float, newXp: float) -> Tuple[int, Optional[int]]:
        """
        Checks for a club level up between two XP ranges.
        If no level up, returns None. Otherwise returns the new level.
        """
        oldLevel, *_ = ClubGlobals.calculateClubLevel(oldXp)
        newLevel, *_ = ClubGlobals.calculateClubLevel(newXp)
        return oldLevel, (newLevel if oldLevel != newLevel else None)

    # endregion

    # region Club Names
    def approveClubName(self, clubId: int) -> None:
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            # In case the club got disbanded while a decision is being made
            club = self.db.getClubById(clubId, includeDeleted=True, _db=db)
            self.db.setClubNameAndStatus(clubId, club.requestedName, ClubNameStatus.NAME_APPROVED, _db=db)
            self.db.createClubLog(clubId, ClubLogType.CLUB_NAME_APPROVED, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            if club.deletedAt is None:
                self.broadcastClubUpdate(
                    clubId,
                    chatMessage=ClubLocalizer.Update_NameApproval.format(
                        name=club.requestedName,
                    )
                )

    def rejectClubName(self, clubId: int, denyReason: str) -> None:
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            # In case the club got disbanded while a decision is being made
            club = self.db.getClubById(clubId, includeDeleted=True, _db=db)
            self.db.setClubNameAndStatus(clubId, club.name if club.name else DefaultClubName, ClubNameStatus.NAME_DENIED, _db=db)
            self.db.createClubLog(clubId, ClubLogType.CLUB_NAME_REJECTED, {'denyReason': denyReason}, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            if club.deletedAt is None:
                self.broadcastClubUpdate(
                    clubId,
                    chatMessage=ClubLocalizer.Update_NameDenied.format(
                        name=club.name,
                    )
                )

    def failClubName(self, clubId: int) -> None:
        self.db.setClubNameStatus(clubId, ClubNameStatus.NAME_FAILED)
        self.broadcastClubUpdate(clubId)

    def setRequestedName(self, clubId: int, requestedName: str) -> None:
        self.db.setClubRequestedName(clubId, requestedName)

    def setClubNameRequestId(self, clubId: int, requestId: int) -> None:
        self.db.setClubNameRequestId(clubId, requestId)
        self.broadcastClubUpdate(clubId)
    # endregion

    # region Club Tasks
    def completeClubTaskIndex(self, clubId: int, completeIndices: List[int]):
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            club = self.db.getClubById(clubId, _db=db)
            initialCoins = club.clubCoins
            totalRewards = 0
            for taskIndex in completeIndices:
                clubTask = ClubTask.fromDict(club.clubTasks[taskIndex])
                coinReward = clubTask.getClubCoinReward()
                totalRewards += coinReward

                self.db.createClubLog(club.id, ClubLogType.CLUB_TASK_COMPLETE, {
                    'chainId': clubTask.chainId,
                    'reward': coinReward
                }, _db=db)

            self.db.addClubCoinsAndClubXp(clubId, totalRewards, totalRewards, _db=db)
            newTasks = self._makeClubTasks(club, rerollIndices=completeIndices)
            self.db.setClubTasks(clubId, newTasks, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.clubCoinService.fileTaxes(clubId=clubId, startCoin=initialCoins, earnings=totalRewards)
            self.broadcastClubUpdate(clubId, chatMessage=ClubLocalizer.Update_TaskCompleted)

    def rerollOfferedClubTasks(self, clubId: int, rerollIndex: int, rerollCost: int, avId: int) -> None:
        tx = self.db.getTransaction()

        try:
            db = tx.start()
            club = self.db.getClubById(clubId, _db=db)
            self.db.addJellybeans(clubId, -rerollCost, _db=db)
            self.db.createClubLog(club.id, ClubLogType.CLUB_TASK_REROLLED, {
                'rerollCost': rerollCost,
                'avId': avId
            }, _db=db)
            clubTasks = self._makeClubTasks(club=club, rerollIndices=[rerollIndex])
            self.db.setClubTasks(club.id, clubTasks, _db=db)
        except Exception as e:
            tx.rollback()
            raise e
        else:
            tx.commit()
            self.broadcastClubUpdate(clubId, chatMessage=ClubLocalizer.Update_TaskRerolled)

    def setClubTasks(self, clubId: int, clubTasks: List[ClubTask]):
        self.db.setClubTasks(clubId, clubTasks)

        if not self.attemptCompleteClubTasks(clubId):
            self.broadcastClubUpdate(clubId)

    def attemptCompleteClubTasks(self, clubId) -> bool:
        """Attempts to complete any active club tasks.
        Returns True if successful, otherwise False."""
        clubContainer = self.getCachedClub(clubId=clubId)
        if not clubContainer:
            return False
        clubTasks = clubContainer.getClubTasks()[:]
        completeIndices = []
        for taskIndex, task in enumerate(clubTasks):
            if task.isComplete(None):
                completeIndices.append(taskIndex)
        if completeIndices:
            self.completeClubTaskIndex(clubId, completeIndices)
            return True
        return False

    def _makeClubTasks(self,
                       club: Optional[Club] = None,
                       rerollIndices: Optional[List[int]] = None,
                       avIds: Optional[List[int]] = None) -> List[ClubTask]:
        """
        Given a club, make a list of club tasks to use.
        """
        if club is None:
            # We are populating with a base list of ClubTasks.
            tasks = [None] * ClubGlobals.ClubTaskCount
        else:
            # Use the tasks from this Club.
            tasks = [ClubTask.fromDict(json) for json in club.clubTasks]

        # Reroll the listed indices.
        ignoreObjectiveTypes = []
        if rerollIndices:
            for rerollIndex in rerollIndices:
                # We want to try and make sure our rerolled task isn't the same type as the one it just was.
                if tasks[rerollIndex] is not None:
                    clubTask = tasks[rerollIndex]  # type: ClubTask
                    questObjective = ClubsQuestLine.dereferenceQuestReference(clubTask.getQuestReference()).getInitialObjective()
                    ignoreObjectiveTypes.append(type(questObjective))
                tasks[rerollIndex] = None

        # Calculate the constants for the club tasks.
        if avIds is None:
            avIds = [toonModel.avId for toonModel in club.toons if not toonModel.deletedAt]

            # Let's get all the toons that left or were kicked recently.
            logs = self.db.getClubLogsByType(
                club.id, types=[ClubLogType.LEFT_CLUB, ClubLogType.KICKED_FROM_CLUB],
                createdAfter=ClubGlobals.ClubTaskAntiCheeseDuration
            )

            avIds.extend([log.data["avId"] for log in logs])
            avIds = set(avIds)

        # The minimum scaling is 1/4 of the club's level, but this cannot go above the highest
        # capacity a club can have.
        minToonCount = ClubGlobals.ClubMinSize
        if club:
            minToonCount = max(1, min(math.ceil(club.level / 4), ClubGlobals.ClubMaxSize))
        toonCount = max(minToonCount, len(avIds))
        toonStats = [self.tt.getToonStats(avId) for avId in avIds if self.tt.getToonStats(avId)]
        averageLevel = (sum(toonStat.getLevel() for toonStat in toonStats) / max(len(toonStats), 1)) + 1

        # Start making the task.
        for taskIndex in range(len(tasks)):
            task = tasks[taskIndex]
            if task is None:
                # We need to generate a task for this given index.
                otherTasks = [task for index, task in enumerate(tasks) if index != taskIndex and task]
                tasks[taskIndex] = self._generateClubTask(otherTasks, toonCount, averageLevel, ignoreObjectiveTypes)

        # Return the tasks.
        return tasks

    def _generateClubTask(self,
                          otherTasks: List[ClubTask],
                          toonCount: int,
                          averageLevel: float,
                          ignoreObjectiveTypes: Optional[list] = None) -> ClubTask:
        """Returns a relevant club task for the Club."""
        ignoreObjectiveTypes = ignoreObjectiveTypes or []
        existingObjectiveTypes = [
            type(QuestLine.dereferenceQuestReference(clubTask.getQuestReference()).getInitialObjective())
            for clubTask in otherTasks
        ]
        difficulty = round((math.ceil(toonCount * ClubGlobals.ClubTaskDifficultyCoeff) + 1) ** 1.06)
        clubTask = None
        for attempt in range(16):
            # We need to roll for a good looking task :-)
            seed = int(999_999 * random.random())
            chainId = (difficulty * 1_000_000) + seed
            clubTask = ClubTask(chainId=chainId)

            # Learn more about this cool and awesome quest
            questObjective = QuestLine.dereferenceQuestReference(clubTask.getQuestReference()).getInitialObjective()

            # Validate this club task.
            if attempt < 8:
                # In earlier attempts, try to avoid duplicate objectives.
                if type(questObjective) in existingObjectiveTypes + ignoreObjectiveTypes:
                    continue

            # Make sure this isn't STUPID to offer early.
            lowestToonLevel = questObjective.getLowestToonLevel()
            if lowestToonLevel and averageLevel < lowestToonLevel:
                continue

            # OK this club task works :)
            break

        # Build the ClubTask off this chainId.
        return clubTask
    # endregion

    # region Club Logs
    def getClubLogs(self, clubId: int):
        return self.db.getClubLogs(clubId)
    # endregion

    # region Club Moderation
    def getInfractionFromId(self, infractionId: int) -> ClubInfraction:
        return self.db.getInfractionFromId(infractionId)

    # endregion

    # region Server Updating
    def broadcastClubUpdate(self, clubId: int, avIdRequested: Optional[List[int]] = None,
                            debounce: Optional[float] = None, chatMessage: Optional[str] = None):
        """
        Broadcasts a club update to all players.

        :param clubId: The ID of the club.
        :param avIdRequested: This request going to certain avIds?
        :param debounce: Should a debounce time be associated?
        :param chatMessage: Send an announcement to the club simultaneously.
        """
        self.requestCacheUpdate(clubId)
        self.mgr.updateMembersOfClub(clubId=clubId, avIdRequested=avIdRequested, debounce=debounce, chatMessage=chatMessage)

    def flushClubState(self, avIds: List[int], clubId: int, chatMessage: Optional[str] = None, dropClub: bool = False):
        self._clubCache.onClubUpdate(clubId, 0, None)
        self.mgr.flushClubState(avIds=avIds, chatMessage=chatMessage, clubId=clubId, dropClub=dropClub)
    # endregion
