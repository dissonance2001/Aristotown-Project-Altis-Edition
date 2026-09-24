from datetime import datetime

import prisma.models
from prisma import Json
from prisma.models import Club, ClubToon as ClubToonPrismaModel
from toontown.booster.BoosterBase import BoosterBase

from toontown.club.ClubContainerBase import ClubContainerBase
from toontown.club.ClubClasses import ClubSettings, ClubIcon, ClubToon, ClubTask, ClubLog, ClubInfraction

from typing import List, Optional
from typing import TYPE_CHECKING

from toontown.time.ToontownTimeZone import ToontownTimeZone

if TYPE_CHECKING:
    from toontown.uberdog.ToontownUberRepository import ToontownUberRepository


class ClubContainerUD(ClubContainerBase):
    """
    The UD interface for the Club Container.
    """

    @classmethod
    def makeContainerFromModel(cls, air, club: Club) -> 'ClubContainerUD':
        """
        Creates a ClubContainerUD from the Prisma model.

        :param air: The AI repository.
        :type air: ToontownUberRepository
        :param club: The club model.
        """
        # Return the full structure.
        return cls(
            id=club.id,
            name=club.name,
            requestedName=club.requestedName,
            nameStatus=club.nameStatus,
            settings=cls.convertClubSettings(club.clubSettings),
            clubIcon=cls.convertClubIcon(club.clubIcon),
            motd=club.motd or '',
            capacity=club.capacity,
            clubXp=club.clubXp,
            clubCoins=club.clubCoins,
            jellybeans=club.jellybeans,
            boosters=cls.convertClubBoosters(club.boosters),
            maxBoosters=club.maxBoosters,
            toons=cls.convertClubToons(air, club.id, club.toons),
            itemsOwned=club.ownedItems,
            clubTasks=cls.convertClubTasks(club.clubTasks),
            logCount=len([log for log in club.logs if ClubLog.isTypeVisible(log.logType, log)]) if club.logs else 0,
            infractions=cls.convertClubInfracts(club.infractions),
        )

    @staticmethod
    def convertClubSettings(clubSettings: Json) -> ClubSettings:
        return ClubSettings.fromDict(clubSettings)

    @staticmethod
    def convertClubIcon(clubIcon: Json) -> ClubIcon:
        return ClubIcon.fromDict(clubIcon)

    @staticmethod
    def convertClubBoosters(boosters: List[Json]):
        return [BoosterBase.fromDict(boosterJson) for boosterJson in boosters]

    @staticmethod
    def convertClubToons(air, clubId: int, toons: Optional[List[ClubToonPrismaModel]]) -> List[ClubToon]:
        """:type air: ToontownUberRepository
        :param clubId: The club ID.
        :param toons: All Toon models in the Club."""
        if not toons:
            return []
        toonList = []
        cacheRequest = []
        for toonModel in toons:
            if toonModel.deletedAt:
                continue
            avId = toonModel.avId
            toonStats = air.toonTracker.getToonStats(avId, includeOffline=True)
            if not toonStats:
                cacheRequest.append(avId)
                continue
            toonList.append(ClubToon.fromModel(
                toonModel=toonModel,
                toonName=toonStats.getName(),
                laff=toonStats.getHp(),
                level=toonStats.getLevel(),
                online=air.toonTracker.isAvIdOnline(avId),
            ))
        if cacheRequest:
            air.clubsManager.handleAvIdCache(clubId, cacheRequest)
        return toonList

    @staticmethod
    def convertClubTasks(tasks: List[Json]):
        return [ClubTask.fromDict(taskJson) for taskJson in tasks]

    @staticmethod
    def convertClubInfracts(infracts: List[prisma.models.ClubInfraction]):
        activeInfs = []
        tz = ToontownTimeZone()
        now = datetime.now(tz=tz)
        for inf in infracts:
            if inf.repealedAt is not None:
                continue
            if inf.expiresAt is None or inf.expiresAt >= now:
                activeInfs.append(inf)
        return [ClubInfraction(infModel.infractionType) for infModel in activeInfs]

    def update(self, air):
        """
        Locally updates this ClubContainer.
        Call this before sending it out of UD.
        :type air: ToontownUberRepository
        """
        # Update the online status of the Club Toons.
        for toon in self.getClubToons():
            toon.setOnlineState(air.toonTracker.isAvIdOnline(toon.getAvId()))
