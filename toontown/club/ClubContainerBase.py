import math
import random

from toontown.booster.BoosterBase import BoosterBase
from toontown.booster.BoosterHandler import BoosterHandler
from toontown.club import ClubGlobals, ClubTaskPricing
from toontown.club.ClubClasses import (
    ClubTask, ClubIcon, ClubLog, ClubToon, ClubSettings, ClubInfraction, ClubModerationLog
)
from toontown.club.ClubEnums import ClubRank
from toontown.club.ClubGlobals import (
    DefaultMOTD, ClubMinSize, ClubItem, ClubTaskDuration, calculateClubLevel
)
from toontown.club.ClubTaskPricing import calculateRerollCost
from toontown.quest3.QuestEnums import QuestSource
from toontown.quest3.base.QuestHistory import QuestHistory
from toontown.quest3.base.QuestReference import QuestId, QuestReference
from toontown.quest3.base.Quester import Quester
from toontown.utils.AstronStruct import AstronStruct

from prisma.enums import ClubNameStatus, ClubInfractionType
from typing import List, Optional


class ClubContainerBase(AstronStruct, BoosterHandler, Quester):
    """
    A struct class which stores all information about a Club.

    This is the base class, which other classes may choose to inherit from.
    """

    def __init__(self,
                 id: int = 0,
                 name: str = 'No Name', requestedName: str = '', nameStatus: ClubNameStatus = ClubNameStatus.NAME_APPROVED,
                 settings: Optional[ClubSettings] = None, clubIcon: Optional[ClubIcon] = None,
                 motd: str = DefaultMOTD, capacity: int = ClubMinSize,
                 clubXp: float = 0.0, clubCoins: float = 0.0, jellybeans: int = 0,
                 boosters: Optional[list] = None, maxBoosters: int = 1,
                 toons: Optional[list] = None, itemsOwned: Optional[list] = None,
                 clubTasks: List[ClubTask] = None, logCount: int = 0, infractions: Optional[list] = None):
        if clubIcon is None:
            clubIcon = ClubIcon()
        if settings is None:
            settings = ClubSettings()
        if clubTasks is None:
            clubTasks = [ClubTask(chainId=83_000_000 + i) for i in range(ClubGlobals.ClubTaskCount)]
        if toons is None:
            toons = []
        if boosters is None:
            boosters = []
        if itemsOwned is None:
            itemsOwned = []
        if infractions is None:
            infractions = []
        self.id = id
        self.name = name
        self.requestedName = requestedName
        self.nameStatus = nameStatus
        self.settings = settings
        self.clubIcon = clubIcon
        self.motd = motd
        self.capacity = capacity
        self.clubXp = clubXp
        self.clubCoins = clubCoins
        self.jellybeans = jellybeans
        self.boosters = boosters
        self.maxBoosters = maxBoosters
        self.toons = toons
        self.itemsOwned = itemsOwned
        self.clubTasks = clubTasks
        self.logCount = logCount
        self.infractions = infractions  # type: List[ClubInfraction]

        # Init BoosterHandler.
        BoosterHandler.__init__(self, boosters=boosters)
        self._boosterInstancesToRaw()

    def toStruct(self) -> list:
        def doRound(val):
            return math.floor(val)
        struct = [
            self.id, self.name, self.requestedName, self.nameStatus,
            self.settings.toStruct(), self.clubIcon.toStruct(), self.motd, self.capacity,
            doRound(self.clubXp), doRound(self.clubCoins), self.jellybeans,
            self.getRawBoosters(), self.maxBoosters,
            ClubToon.toStructList(self.getClubToons()), ClubItem.toStructList(self.itemsOwned),
            ClubTask.toStructList(self.clubTasks), self.logCount, ClubInfraction.toStructList(self.infractions),
        ]
        return struct

    @classmethod
    def fromStruct(cls, struct: list):
        if type(struct) is tuple:
            struct = list(struct)
        indexToType = {
            4: ClubSettings,
            5: ClubIcon,
        }
        indexToListType = {
            11: BoosterBase,
            13: ClubToon,
            14: ClubItem,
            15: ClubTask,
            17: ClubInfraction,
        }
        for i, clubClass in indexToType.items():
            struct[i] = clubClass.fromStruct(struct[i])
        for i, clubClass in indexToListType.items():
            struct[i] = clubClass.fromStructList(struct[i])
        # Return container.
        return cls(*struct)

    """
    Getter methods
    """

    def getAvIds(self) -> list:
        """Gets a list of all AvIds in the club."""
        return [toon.avId for toon in self.getClubToons()]

    def getMemberCount(self) -> int:
        """Returns the club's member count."""
        return len(self.getAvIds())

    def getClubToon(self, avId):
        """Returns the ClubToon from an avId."""
        for toon in self.getClubToons():
            if avId == toon.avId:
                return toon
        return None

    def getClubToons(self):
        return self.toons

    def getClubToonsByRank(self, rank: int):
        return [toon for toon in self.getClubToons() if toon.getRankId() == rank]

    def getClubOwner(self):
        leaderList = self.getClubToonsByRank(ClubRank.Leader)
        if leaderList:
            return leaderList[0]
        else:
            return None

    def getBestLeader(self) -> ClubToon:
        """
        Gets the best suited for 'leader' status,
        excluding the leader themselves.
        """
        for rankId in (ClubRank.Deputy, ClubRank.Officer, ClubRank.Member):
            eldestToon = self.getMostElderOfRank(rankId)
            if eldestToon:
                return eldestToon
        return None

    def getMostElderOfRank(self, rankId: int):
        clubToons = self.getClubToonsByRank(rankId)
        if not clubToons:
            return None
        return sorted(clubToons, key=lambda clubToon: clubToon.getJoinTimestamp())[0]

    def getCapacity(self):
        return self.capacity

    def getRankAndOption(self, rankId, optionId):
        return self.settings.getOptionsFromRank(rankId).getOptionFromId(optionId)

    def avIdHasPermission(self, avId, optionId):
        """Checks if an avId has permissions to do an action."""
        toon = self.getClubToon(avId)
        if not toon:
            return False
        return self.getRankAndOption(toon.getRankId(), optionId)

    def localAvHasPermission(self, optionId):
        """Checks if our local avatar has permissions to do an action."""
        return self.avIdHasPermission(base.localAvatar.getDoId(), optionId)

    def getAvRole(self, avId):
        toon = self.getClubToon(avId)
        if not toon:
            return False
        return toon.getRankId()

    def getLocalAvRole(self):
        return self.getAvRole(base.localAvatar.getDoId())

    def getLocalToon(self):
        return self.getClubToon(base.localAvatar.getDoId())

    def isAvIdOwner(self, avId):
        return self.getAvRole(avId) == ClubRank.Leader

    def localAvIsOwner(self):
        return self.isAvIdOwner(base.localAvatar.getDoId())

    def getClubLevel(self):
        level, currentXp, maxXp = calculateClubLevel(self.clubXp)
        return level

    def getClubIcon(self) -> ClubIcon:
        return self.clubIcon

    def getClubId(self) -> int:
        return self.id

    def getClubName(self) -> str:
        return self.name

    def isClubFull(self) -> bool:
        return len(self.getClubToons()) >= self.capacity

    def getMaxBoosters(self) -> int:
        return self.maxBoosters

    def getJellybeans(self) -> int:
        return self.jellybeans

    def getClubCoins(self) -> int:
        return int(self.clubCoins)

    def getActualClubCoins(self) -> float:
        return self.clubCoins

    def getClubTasks(self) -> List[ClubTask]:
        return self.clubTasks

    def getClubTaskIndex(self, index: int) -> ClubTask:
        return self.clubTasks[index]

    def getClubTask(self, expiredOk: bool = False):
        return None

        if not self.clubTask:
            return None
        if self.clubTask.getTimeLeft() < 0 and not expiredOk:
            return None
        if self.clubTask.isNull:
            return None
        return self.clubTask

    def getOfferedClubTasks(self):
        return []

        return self.offeredClubTasks

    def getOfferedClubTaskIndex(self, i):
        return None

        return self.offeredClubTasks[i]

    def getRerollCost(self, taskIndex) -> int:
        # Club Reroll Cost -- base it off of the lowest chain ID, but have it scale up a tad
        return ClubTaskPricing.calculateRerollCost(self.getClubTaskIndex(taskIndex).getChainId())

    def getLogCount(self):
        return self.logCount

    def hasInfraction(self, infractionType: ClubInfractionType) -> bool:
        return any(inf for inf in self.infractions if inf.getInfractionType() == infractionType)

    """
    Checker Methods
    """

    def avIdInClub(self, avId) -> bool:
        """Checks if an avId is in this club container."""
        return avId in self.getAvIds()

    """
    Club Task Methods
    """

    def addQuest(self, questId: QuestId) -> bool:
        # Not supported, due to club task nuance.
        raise AttributeError

    def addQuestHistory(self, questHistory: QuestHistory) -> None:
        # We do not do anything for this.
        pass

    def getQuestHistory(self):
        # Doesn't exist for ClubContainers.
        pass

    def getQuestReferences(self):
        return [clubTask.getQuestReference() for clubTask in self.getClubTasks()]

    def updateQuestProgress(self):
        # Implemented on the AI side.
        pass
