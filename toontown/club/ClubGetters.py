from direct.showbase.DirectObject import DirectObject

from toontown.club.DistributedClubManager import DistributedClubManager
from toontown.club.ClubContainerClient import ClubContainerClient


class ClubGetters(DirectObject):
    """
    A class that implements club getters for the local avatar.
    Intended to be inherited.
    """

    # Update messages

    def __init__(self):
        self.accept('clubUpdate', self.onClubUpdate)
        self.accept('enterClub', self.onClubEnter)
        self.accept('exitClub', self.onClubExit)

    def onClubUpdate(self):
        pass

    def onClubEnter(self):
        pass

    def onClubExit(self):
        pass

    # Getters

    @staticmethod
    def getClubMgr() -> DistributedClubManager:
        return base.cr.clubMgr

    def getClubContainer(self) -> ClubContainerClient:
        return self.getClubMgr().getLocalClub()

    def isLocalAvOwner(self):
        return self.getClubContainer().localAvIsOwner()

    def isInClub(self) -> bool:
        return self.getClubMgr().isInClub()
