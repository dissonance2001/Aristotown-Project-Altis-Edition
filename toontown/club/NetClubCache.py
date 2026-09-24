from toontown.club.ClubContainerUD import ClubContainerUD
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from typing import TYPE_CHECKING, Dict, Set, Optional, Union

if TYPE_CHECKING:
    from toontown.utils.BuiltinHelper import *
    from toontown.distributed.ToontownInternalRepository import ToontownInternalRepository


class NoClub(int):
    pass


@DirectNotifyCategory()
class NetClubCache:
    """
    Uses the NetMessenger to cache clubs.
    """
    # TODO - Have ClubManagerUD send up cleanup calls when all toons go offline.

    def __init__(self, air, netHook: bool = True):
        self.air = air  # type: ToontownInternalRepository

        # Cache
        self._clubs        = {}  # type: Dict[int, ClubContainerUD]
        self._avId2Club    = {}  # type: Dict[int, Union[ClubContainerUD, NoClub]]
        self._clubId2AvIds = {}  # type: Dict[int, Set]

        # Listen to hooks.
        if netHook:
            self.air.netMessenger.accept("clubContainerUpdateUD", self, self.onClubUpdate)

    """
    Updaters
    """

    def onClubUpdate(self, clubId: int, status: int, clubContainer: Optional[ClubContainerUD]):
        """
        Receives a club container update.
        """
        # First, clean up our current references for the avs.
        if clubId in self._clubId2AvIds:
            for avId in self._clubId2AvIds[clubId]:
                if avId in self._avId2Club:
                    del self._avId2Club[avId]
            del self._clubId2AvIds[clubId]

        if status:
            # This is a fresh group update, populate cache.
            if isinstance(clubContainer, list):
                clubContainer = ClubContainerUD.fromStruct(clubContainer)
            self._clubs[clubId] = clubContainer

            # Then set new ones.
            avIds = clubContainer.getAvIds()[:]
            for avId in avIds:
                self._avId2Club[avId] = clubContainer
            self._clubId2AvIds[clubId] = avIds

        elif clubId in self._clubs:
            # The club has disbanded.
            del self._clubs[clubId]

    def onNoClubUpdate(self, avId: int):
        """
        Marks an avId as being not in a Club.
        """
        self._avId2Club[avId] = NoClub(1)

    """
    Getters
    """

    def hasCachedData(self, clubId: Optional[int] = None, avId: Optional[int] = None) -> bool:
        """
        Determines if there is anything in the cache for the arguments.
        """
        if clubId:
            return bool(self._clubs.get(clubId, False))
        elif avId:
            return bool(self._avId2Club.get(avId, False))
        else:
            return False

    def getClub(self, clubId: Optional[int] = None, avId: Optional[int] = None) -> Optional[ClubContainerUD]:
        """
        Gets a club from arguments.
        """
        if clubId:
            club = self._clubs.get(clubId)
        elif avId:
            club = self._avId2Club.get(avId)
        else:
            return None
        if isinstance(club, NoClub):
            return None
        return club
