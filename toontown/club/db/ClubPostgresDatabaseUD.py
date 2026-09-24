from datetime import datetime, timedelta
from typing import Optional, List

from prisma import Prisma, Json
from prisma.client import TransactionManager
from prisma.enums import ClubLogType, ClubNameStatus, ClubInfractionType
from prisma.models import Club, ClubToon, ClubLog, ClubInfraction
from prisma.types import ClubToonWhereInput, ClubInclude, ClubWhereInput, ClubInfractionWhereInput, ClubUpdateInput
from toontown.booster import BoosterGlobals
from toontown.booster.BoosterBase import BoosterBase
from toontown.club import ClubGlobals

from toontown.club.ClubClasses import ClubIcon, ClubTask, ClubSettings
from toontown.club.ClubEnums import ClubRank
from toontown.inventory.enums.ItemEnums import BoosterItemType
from toontown.time.ToontownTimeZone import ToontownTimeZone

CLUB_INCLUDES: ClubInclude = {
    'toons': True, 'infractions': True
}


class ClubPostgresDatabaseUD:
    def __init__(self):
        # todo: DIC
        self._prisma = Prisma()
        self._prisma.connect()

    def getTransaction(self) -> TransactionManager:
        """
        Provides a Transaction context for transactions.
        """
        return self._prisma.tx()

    # region Club Info Getters
    def getClubById(self, clubId: int, includeDeleted: bool = False, _db: Optional[Prisma] = None) -> Optional[Club]:
        db = self._getDb(_db)
        whereQuery: ClubWhereInput = {
            'id': clubId,
        }

        if not includeDeleted:
            whereQuery['deletedAt'] = None

        return db.club.find_first(
            where=whereQuery,
            include=ClubInclude(toons=True, logs=True, infractions=True, moderationLogs=True),
        )

    def getClubByNameRequestId(self, nameRequestId: int, includeDeleted: bool = False, _db: Optional[Prisma] = None) -> Optional[Club]:
        db = self._getDb(_db)
        whereQuery: ClubWhereInput = {
            'nameRequestId': nameRequestId,
        }

        if not includeDeleted:
            whereQuery['deletedAt'] = None

        return db.club.find_first(
            where=whereQuery,
            include=ClubInclude(toons=True, logs=True, infractions=True, moderationLogs=True),
        )
    # endregion

    # region Club Membership
    # region Club Membership Getters
    def findClubJoinByMemberAvId(self, avId: int, includeDeleted: bool = False, _db: Optional[Prisma] = None) -> Optional[ClubToon]:
        db = self._getDb(_db)

        if not includeDeleted:
            return db.clubtoon.find_first(
                where={
                    'avId': avId,
                    'deletedAt': None,
                },
            )
        else:
            return db.clubtoon.find_first(
                where={
                    'avId': avId,
                },
            )

    def findAllClubToonsByClubId(self, clubId: int, includeDeleted: bool = False, _db: Optional[Prisma] = None) -> List[ClubToon]:
        db = self._getDb(_db)

        if not includeDeleted:
            return db.clubtoon.find_many(
                where={
                    'clubId': clubId,
                    'deletedAt': None,
                },
            )
        else:
            return db.clubtoon.find_many(
                where={
                    'clubId': clubId,
                },
            )

    def findAllClubToonsByClubIdAndRank(self, clubId: int, ranks: List[ClubRank], includeDeleted: bool = False, _db: Optional[Prisma] = None) -> List[ClubToon]:
        db = self._getDb(_db)

        if not includeDeleted:
            return db.clubtoon.find_many(
                where={
                    'clubId': clubId,
                    'rankId': {
                        'in': ranks
                    },
                    'deletedAt': None,
                },
            )
        else:
            return db.clubtoon.find_many(
                where={
                    'clubId': clubId,
                    'rankId': {
                        'in': ranks
                    },
                },
            )

    def findClubJoinByClubIdAndMemberAvId(self, avId: int, clubId: int, includeDeleted: bool = False, _db: Optional[Prisma] = None) -> Optional[ClubToon]:
        db = self._getDb(_db)

        if not includeDeleted:
            return db.clubtoon.find_first(
                where=ClubToonWhereInput(
                    avId=avId,
                    clubId=clubId,
                    deletedAt=None,
                )
            )
        else:
            return db.clubtoon.find_first(
                where=ClubToonWhereInput(
                    avId=avId,
                    clubId=clubId,
                )
            )

    def getClubToonsCount(self, clubId: int, includePending: bool = False, _db: Optional[Prisma] = None) -> int:
        db = self._getDb(_db)

        clubToonWhere: ClubToonWhereInput = {
            'clubId': clubId,
            'deletedAt': None,
        }

        if not includePending:
            clubToonWhere['joinedAt'] = {
                'not': {
                    'equals': None
                }
            }

        return db.clubtoon.count(
            where=clubToonWhere
        )

    # endregion

    # region Club Membership Setters
    def createClubToon(
        self,
        clubId: int,
        avId: int,
        rankId: int,
        invitedBy: int,
        instantJoin: bool = False,
        _db: Optional[Prisma] = None
    ) -> ClubToon:
        db = self._getDb(_db)
        now = self._getNow()

        return db.clubtoon.create(
            data={
                'avId': avId,
                'club': {
                    'connect': { 'id': clubId, },
                },
                'requestedAt': now,
                'joinedAt': now,
                'rankId': rankId,
                'invitedBy': invitedBy,
            }
        )

    def deleteClubToon(self, clubToonId: int, purge: bool = False, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        if not purge:
            # Set the deleted flag.
            db.clubtoon.update(
                data={
                    'deletedAt': now,
                },
                where={
                    'id': clubToonId,

                }
            )
        else:
            # Remove from the DB entirely.
            db.clubtoon.delete(
                where={
                    'id': clubToonId
                }
            )

    def reinstateClubToonById(self, clubToonId: int, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)

        db.clubtoon.update(
            data={
                'deletedAt': None,
            },
            where={
                'id': clubToonId,
            }
        )

    def deleteAllClubToonByClubId(self, clubId: int, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        db.clubtoon.update_many(
            data={
                'deletedAt': now,
            },
            where={
                'clubId': clubId,
            }
        )

    def updateClubToonJoinedAt(self, clubToonId: int, joinedAt: Optional[datetime] = None, _db: Optional[Prisma] = None):
        db = self._getDb(_db)
        now = self._getNow()
        joinedAt = joinedAt if joinedAt else now

        db.clubtoon.update(
            data={
                'joinedAt': joinedAt,
                'updatedAt': now,

            },
            where={
                'id': clubToonId
            }
        )

    def updateClubToonRank(self, clubToonId: int, rankId: ClubRank, _db: Optional[Prisma] = None):
        db = self._getDb(_db)
        now = self._getNow()

        db.clubtoon.update(
            data={
                'rankId': rankId,
                'updatedAt': now,

            },
            where={
                'id': clubToonId
            }
        )

    # endregion
    # endregion

    # region Club creating, editing and deleting
    def createClub(
        self,
        name: str,
        requestedName: str,
        ownerAccountId: int,
        ownerAvId: int,
        clubIcon: ClubIcon,
        clubTasks: List[ClubTask],
        capacity: int,
        dailyCoins: int,
        clubXp: int,
        clubCoins: int,
        jellybeans: int,
        _db: Optional[Prisma] = None
    ) -> Club:
        db = self._getDb(_db)

        now = self._getNow()
        return db.club.create(
            data={
                'name': name,
                'requestedName': requestedName,
                'ownerAccountId': int(ownerAccountId),
                'ownerAvId': ownerAvId,
                'capacity': capacity,
                'level': 1,
                'dailyCoins': dailyCoins,
                'clubXp': clubXp,
                'clubCoins': clubCoins,
                'jellybeans': jellybeans,
                'createdAt': now,
                'updatedAt': now,
                'motd': ClubGlobals.DefaultMOTD,
                'clubIcon': Json(clubIcon.toDict()),
                'clubTasks': [Json(task.toDict()) for task in clubTasks],
                'ownedItems': [] + clubIcon.getItemIDs(),
                'toons': {
                    'create': {
                        'avId': ownerAvId,
                        'invitedBy': ownerAvId,
                        'requestedAt': now,
                        'joinedAt': now,
                        'rankId': ClubRank.Leader,
                    }
                },
                'clubSettings': Json(ClubSettings().toDict()),
                'logs': {
                    'create': [
                        {
                            'logType': ClubLogType.CLUB_CREATED,
                            'data': Json({
                                'avId': ownerAvId,
                                'bgCol': clubIcon.bgCol,
                                'iconId': clubIcon.iconId,
                                'clubCol': clubIcon.clubCol,
                                'backgroundId': clubIcon.backgroundId,
                            })
                        },
                        {
                            'logType': ClubLogType.JOINED_CLUB,
                            'data': Json({
                                'avId': ownerAvId,
                                'inviterAvId': ownerAvId,
                            })
                        },
                    ]
                }
            },
            include=ClubInclude(
                toons=True,
                logs=True,
            )
        )

    def disbandClub(self, clubId: int, _db: Optional[Prisma] = None) -> None:
        """
        Disbands a club.
        """
        db = self._getDb(_db)
        now = self._getNow()

        return db.club.update(
            data={
                'deletedAt': now,
            },
            where={
                'id': clubId
            },
        )

    def reinstateClub(self, clubId, _db: Optional[Prisma] = None) -> None:
        """
        Reinstates a club.
        """
        db = self._getDb(_db)

        return db.club.update(
            data={
                'deletedAt': None,
            },
            where={
                'id': clubId
            },
        )

    def setClubOwner(self, clubId: int, ownerAvId: int, ownerAccountId: int, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        return db.club.update(
            data={
                'ownerAvId': ownerAvId,
                'ownerAccountId': ownerAccountId,
                'updatedAt': now
            },
            where={
                'id': clubId
            },
        )

    def setClubCapacity(self, clubId: int, capacity: int, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        return db.club.update(
            data={
                'capacity': capacity,
                'updatedAt': now
            },
            where={
                'id': clubId
            },
        )

    def giveClubBooster(self, clubId: int, boosterType: BoosterItemType, endTimestamp: int, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        # Get the current club boosters.
        # Cull any expired ones, and add the new ones.
        club = self.getClubById(clubId, _db=db)
        clubBoosters = [BoosterBase.fromDict(j) for j in club.boosters]
        clubBoosters = [booster for booster in clubBoosters if not booster.isExpired()]
        clubBoosters.append(BoosterBase(boosterType, endTimestamp))

        return db.club.update(
            data={
                'boosters': [Json(booster.toDict()) for booster in clubBoosters],
                'updatedAt': now
            },
            where={
                'id': clubId
            },
        )

    def setClubMaxBoosters(self, clubId: int, maxBoosters: int, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        return db.club.update(
            data={
                'maxBoosters': maxBoosters,
                'updatedAt': now
            },
            where={
                'id': clubId
            },
        )

    def setClubSettings(self, clubId: int, clubSettings: dict, _db: Optional[Prisma] = None):
        db = self._getDb(_db)
        now = self._getNow()

        return db.club.update(
            data={
                'clubSettings': Json(clubSettings),
                'updatedAt': now
            },
            where={
                'id': clubId
            },
        )
    # endregion

    # region Club Items
    def addOwnedClubItem(self, clubId: int, clubItemId: int, _db: Optional[Prisma] = None):
        db = self._getDb(_db)
        now = self._getNow()

        return db.club.update(
            data={
                'ownedItems': {
                    'push': clubItemId,
                },
                'updatedAt': now
            },
            where={
                'id': clubId
            },
        )

    def setClubIcon(self, clubId: int, clubIcon: ClubIcon, _db: Optional[Prisma] = None):
        db = self._getDb(_db)
        now = self._getNow()

        return db.club.update(
            data={
                'clubIcon': Json(clubIcon.toDict()),
                'updatedAt': now
            },
            where={
                'id': clubId
            },
        )

    def setClubMotd(self, clubId: int, motd: str, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        return db.club.update(
            data={
                'motd': motd,
                'updatedAt': now
            },
            where={
                'id': clubId
            },
        )

    # endregion

    # region Club Currencies
    def addClubCoins(self, clubId: int, clubCoins: float, _db: Optional[Prisma] = None):
        db = self._getDb(_db)

        db.club.update(
            data={
                'clubCoins': {
                    'increment': clubCoins
                }
            },
            where={
                'id': clubId
            }
        )

    def addJellybeans(self, clubId: int, jellybeans: int, _db: Optional[Prisma] = None):
        db = self._getDb(_db)

        db.club.update(
            data={
                'jellybeans': {
                    'increment': jellybeans
                }
            },
            where={
                'id': clubId
            }
        )

    def addClubXp(self, clubId: int, clubXp: int, _db: Optional[Prisma] = None):
        db = self._getDb(_db)

        db.club.update(
            data={
                'clubXp': {
                    'increment': clubXp
                }
            },
            where={
                'id': clubId
            }
        )

    def addClubCoinsAndClubXp(self, clubId: int, clubCoins: float, clubXp: int, _db: Optional[Prisma] = None):
        db = self._getDb(_db)

        db.club.update(
            data={
                'clubCoins': {
                    'increment': clubCoins
                },
                'clubXp': {
                    'increment': clubXp
                }
            },
            where={
                'id': clubId
            }
        )

    # endregion

    # region Club Names
    def setClubNameAndStatus(self, clubId: int, name: str, nameStatus: ClubNameStatus, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)

        db.club.update(
            data={
                'name': name,
                'nameStatus': nameStatus
            },
            where={
                'id': clubId
            },
        )

    def setClubNameStatus(self, clubId: int, nameStatus: ClubNameStatus, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)

        db.club.update(
            data={
                'nameStatus': nameStatus
            },
            where={
                'id': clubId
            },
        )

    def setClubNameRequestId(self, clubId: int, requestId: int, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        db.club.update(
            data={
                'nameStatus': ClubNameStatus.NAME_REQUESTED,
                'nameRequestId': requestId,
                'updatedAt': now,
            },
            where={
                'id': clubId
            },
        )

    def setClubRequestedName(self, clubId: int, requestedName: str, _db: Optional[Prisma] = None) -> None:
        db = self._getDb(_db)
        now = self._getNow()

        db.club.update(
            data={
                'requestedName': requestedName,
                'updatedAt': now,
            },
            where={
                'id': clubId
            },
        )

    # endregion

    # region Club Logs
    def getClubLogs(self, clubId: int):
        return self._prisma.clublog.find_many(
            take=ClubGlobals.ClubMaxLogs,
            where={
                'clubId': clubId,
            },
            order={
                'createdAt': 'desc',
            },
        )

    def getClubLogsByType(self, clubId: int, types: Optional[List[ClubLogType]] = None,
                          createdAfter: Optional[float] = None, _db: Optional[Prisma] = None):
        db = self._getDb(_db)
        now = self._getNow()
        where = {'clubId': clubId}

        if types:
            where['logType'] = {'in': types}

        if createdAfter is not None:
            where['createdAt'] = {'gte': now - timedelta(seconds=createdAfter)}

        return db.clublog.find_many(
            take=ClubGlobals.ClubMaxLogs,
            where=where,
            order={'createdAt': 'desc'},
        )

    def createClubLog(self, clubId: int, logType: ClubLogType, data: Optional[dict] = None, _db: Optional[Prisma] = None) -> ClubLog:
        if data is None:
            data = {}
        db = self._getDb(_db)

        return db.clublog.create(
            data={
                'clubId': clubId,
                'logType': logType,
                'data': Json(data),
            }
        )
    # endregion

    # region Club Tasks
    def setClubTasks(self, clubId: int, clubTasks: List[ClubTask], _db: Optional[Prisma] = None):
        db = self._getDb(_db)
        now = self._getNow()

        db.club.update(
            data=ClubUpdateInput(
                clubTasks=[Json(task.toDict()) for task in clubTasks],
                updatedAt=now,
            ),
            where={
                'id': clubId,
            }
        )
    # endregion

    # region Club Moderation
    def getInfractionFromId(self, infractionId: int, _db: Optional[Prisma] = None) -> ClubInfraction:
        db = self._getDb(_db)
        return db.clubinfraction.find_first(
            where={
                'id': infractionId
            }
        )

    def getActiveInfractions(self, clubId: int, infractionType: Optional[ClubInfractionType] = None) -> List[ClubInfraction]:
        now = self._getNow()

        queryWhere: ClubInfractionWhereInput = {
            'OR': [
                {
                    'expiresAt': None
                },
                {
                    'expiresAt': {
                        'gt': now
                    }
                }
            ],
            'AND': {
                'clubId': clubId,
                'repealedAt': None,
            }
        }

        if infractionType:
            queryWhere['infractionType'] = infractionType

        return self._prisma.clubinfraction.find_many(where=queryWhere)
    # endregion

    def _getDb(self, db: Optional[Prisma] = None) -> Prisma:
        return db if db else self._prisma

    @staticmethod
    def _getNow() -> datetime:
        return datetime.now(tz=ToontownTimeZone())
