"""
All AstronStruct definitions for clubs.
If you are interested in the UD-representation
of a club, check ToontownClub.py.
"""

from prisma.enums import ClubModerationLogType, ClubInfractionType, ClubLogType
from toontown.club import ClubEnums
from toontown.club.ClubGlobals import *
from toontown.club.ClubEnums import ClubRank
from toontown.club.ClubTaskPricing import calculateTaskReward, calculateTaskCost
from toontown.quest3.QuestEnums import QuestSource
from toontown.quest3.base.QuestLine import QuestLine
from toontown.quest3.base.QuestReference import QuestReference, QuestId
from toontown.utils.AstronDict import AstronDict
from toontown.utils.AstronStruct import AstronStruct
import time


class ClubMemberOptions(AstronStruct):
    """
    A container class for configuring perms of the Club Member rank.
    """

    def __init__(self,
                 purchaseClubTasks: bool = False,
                 purchaseClubShopItems: bool = False,
                 canMakeAnnouncements: bool = False,
                 canUseClubShouts: bool = False,
                 canUseClubChat: bool = True,
                 canInviteToons: bool = False,
                 canKickToons: bool = False,
                 canUpdateMotd: bool = False):
        self.purchaseClubTasks = purchaseClubTasks
        self.purchaseClubShopItems = purchaseClubShopItems
        self.canMakeAnnouncements = canMakeAnnouncements
        self.canUseClubShouts = canUseClubShouts
        self.canUseClubChat = canUseClubChat
        self.canInviteToons = canInviteToons
        self.canKickToons = canKickToons
        self.canUpdateMotd = canUpdateMotd

    def toStruct(self) -> list:
        return [
            int(self.purchaseClubTasks), int(self.purchaseClubShopItems),
            int(self.canMakeAnnouncements), int(self.canUseClubShouts),
            int(self.canUseClubChat), int(self.canInviteToons),
            int(self.canKickToons), int(self.canUpdateMotd),
        ]

    def getOptionFromId(self, optionId):
        """Returns the value of an option given an ID."""
        return {
            ClubEnums.REROLL_CLUB_TASKS: self.purchaseClubTasks,
            ClubEnums.PURCHASE_CLUB_SHOP_ITEMS: self.purchaseClubShopItems,
            ClubEnums.CAN_MAKE_ANNOUNCEMENTS: self.canMakeAnnouncements,
            ClubEnums.CAN_USE_CLUB_SHOUTS: self.canUseClubShouts,
            ClubEnums.CAN_USE_CLUB_CHAT: self.canUseClubChat,
            ClubEnums.CAN_INVITE_TOONS: self.canInviteToons,
            ClubEnums.CAN_KICK_TOONS: self.canKickToons,
            ClubEnums.CAN_UPDATE_MOTD: self.canUpdateMotd,
        }.get(optionId)

    def setOptionValue(self, optionId, value):
        if optionId == ClubEnums.REROLL_CLUB_TASKS:
            self.purchaseClubTasks = value
        elif optionId == ClubEnums.PURCHASE_CLUB_SHOP_ITEMS:
            self.purchaseClubShopItems = value
        elif optionId == ClubEnums.CAN_MAKE_ANNOUNCEMENTS:
            self.canMakeAnnouncements = value
        elif optionId == ClubEnums.CAN_USE_CLUB_SHOUTS:
            self.canUseClubShouts = value
        elif optionId == ClubEnums.CAN_USE_CLUB_CHAT:
            self.canUseClubChat = value
        elif optionId == ClubEnums.CAN_INVITE_TOONS:
            self.canInviteToons = value
        elif optionId == ClubEnums.CAN_KICK_TOONS:
            self.canKickToons = value
        elif optionId == ClubEnums.CAN_UPDATE_MOTD:
            self.canUpdateMotd = value


class ClubOfficerOptions(ClubMemberOptions):
    """
    A container class for configuring perms of the Club Officer rank.
    """

    def __init__(self,
                 purchaseClubTasks: bool = False,
                 purchaseClubShopItems: bool = False,
                 canMakeAnnouncements: bool = False,
                 canUseClubShouts: bool = True,
                 canUseClubChat: bool = True,
                 canInviteToons: bool = True,
                 canKickToons: bool = False,
                 canUpdateMotd: bool = False):
        super().__init__(purchaseClubTasks, purchaseClubShopItems,
                         canMakeAnnouncements, canUseClubShouts,
                         canUseClubChat, canInviteToons,
                         canKickToons, canUpdateMotd)


class ClubDeputyOptions(ClubMemberOptions):
    """
    A container class for configuring perms of the Club Deputy rank.
    """

    def __init__(self,
                 purchaseClubTasks: bool = True,
                 purchaseClubShopItems: bool = True,
                 canMakeAnnouncements: bool = False,
                 canUseClubShouts: bool = True,
                 canUseClubChat: bool = True,
                 canInviteToons: bool = True,
                 canKickToons: bool = True,
                 canUpdateMotd: bool = False):
        super().__init__(purchaseClubTasks, purchaseClubShopItems,
                         canMakeAnnouncements, canUseClubShouts,
                         canUseClubChat, canInviteToons,
                         canKickToons, canUpdateMotd)


class ClubOwnerOptions(ClubMemberOptions):
    """
    A container class for configuring perms of the club's owner.
    Not adjustable nor kept up with, as the owner has all perms.
    """

    def __init__(self,
                 purchaseClubTasks: bool = True,
                 purchaseClubShopItems: bool = True,
                 canMakeAnnouncements: bool = True,
                 canUseClubShouts: bool = True,
                 canUseClubChat: bool = True,
                 canInviteToons: bool = True,
                 canKickToons: bool = True,
                 canUpdateMotd: bool = True):
        super().__init__(purchaseClubTasks, purchaseClubShopItems,
                         canMakeAnnouncements, canUseClubShouts,
                         canUseClubChat, canInviteToons,
                         canKickToons, canUpdateMotd)


class ClubTask(AstronStruct):
    """
    A representation of a club task.
    """
    __slots__ = 'chainId', 'taskProgress', 'endTime'

    def __init__(self,
                 chainId: int = 0,
                 taskProgress: list = None,
                 endTime: int = 0):
        if taskProgress is None:
            if chainId == 0:
                taskProgress = []
            else:
                taskProgress = [0] * QuestLine.dereferenceQuestReference(
                    QuestReference(
                        questId=QuestId(
                            questSource=QuestSource.ClubQuest,
                            chainId=chainId,
                            objectiveId=1,
                        )
                    )
                ).getObjectiveCount()
        self.chainId = chainId
        self.taskProgress = taskProgress
        self.endTime = endTime

    def toStruct(self) -> list:
        return [self.chainId, self.taskProgress, self.endTime]

    @property
    def isNull(self):
        return self.chainId == 0

    def getTimeLeft(self):
        return self.endTime - time.time()

    def getChainId(self):
        return self.chainId

    def getTaskProgress(self):
        return self.taskProgress

    def getEndTime(self):
        return self.endTime

    def isComplete(self, clubContainer):
        questReference = self.getQuestReference()
        multiObjective = QuestLine.dereferenceQuestReference(questReference=questReference, quester=clubContainer)
        return multiObjective.isComplete(questReference=questReference, context=None, quester=clubContainer)

    def getQuestReference(self) -> QuestReference:
        return QuestReference(
            questId=QuestId(
                questSource=QuestSource.ClubQuest,
                chainId=self.getChainId(),
                objectiveId=1,
            ),
            progress=self.getTaskProgress()
        )

    def getClubCoinCost(self) -> int:
        return calculateTaskCost(self.getChainId(), coins=True)

    def getJellybeanCost(self) -> int:
        # Just an amount times the club coin cost
        return calculateTaskCost(self.getChainId(), beans=True)

    def getClubCoinReward(self):
        # An amount times the cost
        return calculateTaskReward(self.getChainId())

    @staticmethod
    def fromDict(values):
        return ClubTask(
            values['chainId'],
            values['taskProgress'],
            values['endTime']
        )


class ClubIcon(AstronStruct):
    """
    A representation of the data to draw a Club Icon.
    """
    __slots__ = 'iconId', 'backgroundId', 'clubCol', 'bgCol'

    def __init__(self,
                 iconId: int = 0,
                 backgroundId: int = 0,
                 clubCol: int = BTID,
                 bgCol: int = BBID):
        self.iconId = iconId
        self.backgroundId = backgroundId
        self.clubCol = clubCol
        self.bgCol = bgCol

    def toStruct(self) -> list:
        return [self.iconId, self.backgroundId,
                self.clubCol, self.bgCol]

    def getClubColorId(self) -> int:
        return self.clubCol

    def getClubColor(self) -> ClubColor:
        clubItem: ClubItem = ClubItemIndex.getItem(self.clubCol)
        return clubItem.getValue()

    def getBackgroundCol(self) -> ClubColor:
        clubItem: ClubItem = ClubItemIndex.getItem(self.bgCol)
        return clubItem.getValue()

    def getItemIDs(self):
        return [self.iconId, self.backgroundId, self.clubCol, self.bgCol]

    def toDict(self) -> dict:
        return {
            'iconId': self.iconId,
            'backgroundId': self.backgroundId,
            'clubCol': self.clubCol,
            'bgCol': self.bgCol
        }

    @staticmethod
    def fromDict(values: Dict[str, int]):
        return ClubIcon(
            values['iconId'],
            values['backgroundId'],
            values['clubCol'],
            values['bgCol']
        )


class ClubLog(AstronStruct):
    """
    Representation of a log from a Club.
    """

    # Which club log types does the client get?
    VisibleClubLogs = {
        ClubLogType.CLUB_CREATED,
        ClubLogType.LEFT_CLUB,
        ClubLogType.INVITED_TO_CLUB,
        ClubLogType.KICKED_FROM_CLUB,
        ClubLogType.USER_RANK_CHANGED,
        ClubLogType.CLUB_PROMOTED,
        ClubLogType.BOUGHT_ITEM,
        ClubLogType.CLUB_NAME_APPROVED,
        ClubLogType.CLUB_NAME_REJECTED,
        ClubLogType.CLUB_TASK_COMPLETE,
        ClubLogType.CLUB_TASK_REROLLED,
        ClubLogType.EARNED_JELLYBEANS
    }

    def __init__(self,
                 logType: ClubLogType,
                 logTimestamp: int,
                 data: AstronDict):
        self.logType: ClubLogType = logType
        self.timestamp: int = logTimestamp
        self.data: AstronDict = data

    def toStruct(self) -> list:
        return [self.logType, self.timestamp, self.data.toStruct()]

    @classmethod
    def fromStruct(cls, struct):
        logType, timestamp, data = struct
        logType = ClubLogType(logType)
        data = AstronDict.fromStruct(data)
        return cls(logType, timestamp, data)

    @classmethod
    def fromModelList(cls, models):
        from prisma.models import ClubLog
        models: List[ClubLog]
        return [
            cls(
                logType=model.logType,
                logTimestamp=int(model.createdAt.timestamp()),
                data=AstronDict.fromDict(model.data),
            ) for model in models if model.data
        ]

    def getType(self) -> ClubLogType:
        return self.logType

    def getTimestamp(self):
        return self.timestamp

    def getData(self) -> dict:
        return dict(self.data)

    @staticmethod
    def isTypeVisible(clubLogType: ClubLogType, clubLog) -> bool:
        if clubLogType == ClubLogType.INVITED_TO_CLUB:
            pass
        return clubLogType in ClubLog.VisibleClubLogs


class ClubToon(AstronStruct):
    """
    Information which represents a given Toon in a club.
    """

    def __init__(self,
                 avId: int = 0,
                 toonName: str = '',
                 rankId: int = 0,
                 joinTimestamp: int = 0,
                 laff: int = 0,
                 level: int = 0,
                 online: int = 0):
        self.avId = avId
        self.toonName = toonName
        self.rankId = rankId
        self.joinTimestamp = joinTimestamp
        self.laff = laff
        self.level = level
        self.online = online

    def toStruct(self) -> list:
        return [self.avId, self.toonName, self.rankId,
                self.joinTimestamp, self.laff, self.level,
                self.online]

    def getAvId(self):
        return self.avId

    def getToonName(self):
        return self.toonName

    def getRankId(self):
        return self.rankId

    def getJoinTimestamp(self):
        return self.joinTimestamp

    def getToonLevel(self):
        return self.level

    def isOnline(self):
        return self.online

    def setRankId(self, rankId: int):
        self.rankId = rankId

    def setLaff(self, laff):
        self.laff = laff

    def setLevel(self, level):
        self.level = level

    def setToonName(self, toonName):
        self.toonName = toonName

    def setOnline(self):
        self.online = 1

    def setOffline(self):
        self.online = 0

    def setOnlineState(self, state):
        self.online = state

    @classmethod
    def fromModel(cls, toonModel, toonName, laff, level, online):
        """Made from the prisma model."""
        return cls(
            avId=toonModel.avId,
            toonName=toonName,
            rankId=toonModel.rankId,
            joinTimestamp=toonModel.joinedAt.timestamp(),
            laff=laff,
            level=level,
            online=online,
        )


class ClubLight(AstronStruct):
    """
    A lighter version of a club.
    Keeps in mind the qualities of a different club.
    """

    def __init__(self,
                 clubIcon: ClubIcon = None,
                 clubToons: list = None,
                 clubName: str = 'No Name',
                 clubLevelAverage: int = 0,
                 clubLevelCompletion: float = 0.0):
        if clubIcon is None:
            clubIcon = ClubIcon()
        if clubToons is None:
            clubToons = []
        self.clubIcon = clubIcon
        self.clubToons = clubToons
        self.clubName = clubName
        self.clubLevelAverage = clubLevelAverage
        self.clubLevelCompletion = clubLevelCompletion

    def toStruct(self) -> list:
        return [
            self.clubIcon.toStruct(),
            AstronStruct.toStructList(self.clubToons),
            self.clubName,
            self.clubLevelAverage,
            self.clubLevelCompletion,
        ]

    @classmethod
    def fromStruct(cls, struct: list):
        clubIcon, clubToons, clubName, clubLevelAverage, clubLevelCompletion = struct
        clubIcon = ClubIcon.fromStruct(clubIcon)
        clubToons = ClubToon.fromStructList(clubToons)
        return cls(clubIcon, clubToons, clubName, clubLevelAverage, clubLevelCompletion)


class ClubDuelOffer(AstronStruct):
    """
    Representation for a Club Duel Offer.
    Contains the relevant ClubTask,
    along with a lightweight version of a Club to boot.
    """

    def __init__(self,
                 clubTask: ClubIcon = None,
                 clubLight: ClubLight = None):
        if clubTask is None:
            clubTask = ClubIcon()
        if clubLight is None:
            clubLight = ClubLight()
        self.clubTask = clubTask
        self.clubLight = clubLight

    def toStruct(self) -> list:
        return [
            self.clubTask.toStruct(),
            self.clubLight.toStruct(),
        ]

    @classmethod
    def fromStruct(cls, struct: list):
        clubTask, clubLight = struct
        clubTask = ClubTask.fromStruct(clubTask)
        clubLight = ClubLight.fromStruct(clubLight)
        return cls(clubTask, clubLight)


class ClubClashObjective(AstronStruct):
    """
    Representation for a Club Clash Objective.
    Contains the ID of the objective, along with all args about it.
    """

    def __init__(self,
                 objectiveId: int = 0,
                 objectiveArgs: list = None):
        if objectiveArgs is None:
            objectiveArgs = []
        self.objectiveId = objectiveId
        self.objectiveArgs = objectiveArgs

    def toStruct(self) -> list:
        return [
            self.objectiveId,
            self.objectiveArgs,
        ]


class ClubSettings(AstronStruct):
    """
    The class which contains all of the club settings.
    They are split off into options:
        - Club Options, which are options that affect the whole club
        - Rank Options, which are perms for deputy/officer/member
    """

    def __init__(self,
                 deputySettings: ClubDeputyOptions = None,
                 officerSettings: ClubOfficerOptions = None,
                 memberSettings: ClubMemberOptions = None):
        if deputySettings is None:
            deputySettings = ClubDeputyOptions()
        if officerSettings is None:
            officerSettings = ClubOfficerOptions()
        if memberSettings is None:
            memberSettings = ClubMemberOptions()
        self.deputySettings = deputySettings
        self.officerSettings = officerSettings
        self.memberSettings = memberSettings

    def toStruct(self) -> list:
        return [
            self.deputySettings.toStruct(),
            self.officerSettings.toStruct(),
            self.memberSettings.toStruct(),
        ]

    @classmethod
    def fromStruct(cls, struct: list):
        deputySettings, officerSettings, memberSettings = struct
        deputySettings = ClubDeputyOptions.fromStruct(deputySettings)
        officerSettings = ClubOfficerOptions.fromStruct(officerSettings)
        memberSettings = ClubMemberOptions.fromStruct(memberSettings)
        return cls(deputySettings, officerSettings, memberSettings)

    def getOptionsFromRank(self, rankVal):
        """Gets the options class depending on the rank."""
        return {
            ClubRank.Member: self.memberSettings,
            ClubRank.Officer: self.officerSettings,
            ClubRank.Deputy: self.deputySettings,
            ClubRank.Leader: ClubOwnerOptions(),
        }.get(rankVal)

    def toDict(self) -> dict:
        return {
            ClubRank.Member: self.memberSettings.toStruct(),
            ClubRank.Officer: self.officerSettings.toStruct(),
            ClubRank.Deputy: self.deputySettings.toStruct(),
        }

    @staticmethod
    def fromDict(values: dict) -> 'ClubSettings':
        memberSettings = ClubMemberOptions.fromStruct(values[str(int(ClubRank.Member))])
        officerSettings = ClubOfficerOptions.fromStruct(values[str(int(ClubRank.Officer))])
        deputySettings = ClubDeputyOptions.fromStruct(values[str(int(ClubRank.Deputy))])
        return ClubSettings(deputySettings, officerSettings, memberSettings)


class ClubModerationLog(AstronStruct):
    """
    A model for a ClubModerationLog.
    """

    def __init__(self, _id: int = 0, clubId: int = 0, clubInfractionId: int = 0,
                 createdAt: int = 0, logType: ClubModerationLogType = ClubModerationLogType.INFO,
                 notes: str = ""):
        self._id = _id
        self.clubId = clubId
        self.clubInfractionId = clubInfractionId
        self.createdAt = createdAt
        self.logType = logType
        self.notes = notes

    def toStruct(self):
        return [self._id, self.clubId, self.clubInfractionId, self.createdAt, self.logType, self.notes]


class ClubInfraction(AstronStruct):
    """
    A model for a ClubInfraction.
    """

    def __init__(self, infractionType: ClubInfractionType = ClubInfractionType.WARNING):
        self.infractionType = infractionType

    def toStruct(self) -> list:
        return [self.infractionType]

    @classmethod
    def fromStruct(cls, struct: list):
        return cls(struct[0])

    @classmethod
    def fromDict(cls, json: dict):
        return cls(json['infractionType'])

    def getInfractionType(self) -> ClubInfractionType:
        return self.infractionType

    def isActive(self):
        # The infraction is still active.
        return True
