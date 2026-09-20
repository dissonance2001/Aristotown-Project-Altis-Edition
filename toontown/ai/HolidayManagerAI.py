import math
import time

from toontown.toonbase import ToontownGlobals, RealmGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from datetime import datetime
from .HolidayGlobals import *
from toontown.suit.SuitInvasionGlobals import *
from direct.showbase.DirectObject import DirectObject
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository

from ..hood import ZoneUtil
from ..toon import DistributedToonAI

HolidaySuit = 'count'
HolidaySuitSpawnTime = 30
HolidaySuitSpawns = (
    3100, 4100, 5100, 6100, 7100, 9100,
    3200, 4200, 5200, 6200, 7200, 9200,
    4300, 5300, 6300, 7300, 9300,
    4400, 5400, 6400,
)  # deliberately remove arctic avenue, too volatile..

MaxPlaygroundDelay = 3

DifficultyMap = {
    3: 3,  # tb
    4: 2,  # mml
    5: 1,  # dg
    6: 4,  # aa
    7: 0,  # yott
    9: 5,  # ddl
}


@DirectNotifyCategory()
class HolidayManagerAI(DirectObject):
    def __init__(self, air):
        """
        :type air: ToontownAIRepository
        """
        DirectObject.__init__(self)
        self.air = air  # type: ToontownAIRepository
        # List of holidays in progress
        self.currentHolidays = []

        self.xpMultiplier = 1
        self.forceZoneSpawn = None
        self.pgsPicked = []
        taskMgr.add(self.checkForHoliday, 'checkForHoliday')
        self.setup()

    def setup(self):
        self.notify.debug(str(self.currentHolidays))

    def isHolidayRunning(self, holidayId):
        if type(holidayId) is list:
            for hid in holidayId:
                if hid in self.currentHolidays:
                    return True
            return False
        if holidayId in self.currentHolidays:
            return True
        else:
            return False

    def isMoreXpHolidayRunning(self):
        return False

    def getXpMultiplier(self):
        return self.xpMultiplier

    def addHoliday(self, holidayId):
        if holidayId not in self.currentHolidays:
            self.currentHolidays.append(holidayId)
        simbase.air.newsManager.d_setHolidayIdList([self.currentHolidays])

    def startHoliday(self, holidayId):
        if holidayId == ToontownGlobals.MORE_XP_HOLIDAY:
            self.air.newsManager.setMoreXpHolidayStart()
        elif holidayId == ToontownGlobals.TROLLEY_HOLIDAY:
            simbase.air.trolleyHolidayMgr.start()
        elif holidayId == ToontownGlobals.IDES_OF_MARCH:
            messenger.send('startIdes')
        elif holidayId == ToontownGlobals.HALLOWEEN:
            self.air.wantHalloween = True
            #taskMgr.doMethodLater(self.getTimeUntilSuitSpawn(), self.prepareHolidaySuit, 'holiday-suit-spawn')
        elif holidayId == ToontownGlobals.CHRISTMAS:
            self.air.wantChristmas = True
        elif holidayId == ToontownGlobals.APRIL_FOOLS:
            self.air.wantAprilFools = True
        elif holidayId == ToontownGlobals.SKELECOG_INVASION:
            self.air.suitInvasionManager.startInvasion(
                suitDept='l', suitName ='b', flags=IFSkelecog, invasionType=InvasionType.MEGA
            )
        elif holidayId == ToontownGlobals.BLACK_FRIDAY:
            self.air.suitInvasionManager.startInvasion(
                suitDept='s', suitName=None, flags=0, invasionType=InvasionType.MEGA
            )
        elif holidayId == ToontownGlobals.SILLY_SATURDAY:
            try:
                self.air.sillySaturdayManager.startSillySaturday()
            except:
                pass

    def removeHoliday(self, holidayId):
        if holidayId in self.currentHolidays:
            self.currentHolidays.remove(holidayId)
        if holidayId == ToontownGlobals.IDES_OF_MARCH:
            messenger.send('endIdes')
        if holidayId == ToontownGlobals.SKELECOG_INVASION or holidayId == ToontownGlobals.BLACK_FRIDAY:
            self.air.suitInvasionManager.stopInvasion()
        if holidayId == ToontownGlobals.SILLY_SATURDAY:
            self.air.sillySaturdayManager.stopSillySaturday()
        simbase.air.newsManager.d_setHolidayIdList([self.currentHolidays])

    def endHoliday(self, holidayId):
        if holidayId == ToontownGlobals.MORE_XP_HOLIDAY:
            self.xpMultiplier = 1  # for the rest of alpha if 5x isnt enabled
            self.air.newsManager.setMoreXpHolidayEnd()
        if holidayId == ToontownGlobals.TROLLEY_HOLIDAY:
            simbase.air.trolleyHolidayMgr.stop()
        if holidayId == ToontownGlobals.SKELECOG_INVASION:
            self.air.suitInvasionManager.stopInvasion()

    def checkForHoliday(self, task):
        now = datetime.now(tz=ToontownTimeZone())
        task.delayTime = 60
        self.notify.info(
            f"REALM={RealmGlobals.getCurrentRealm()} isPrivate={RealmGlobals.getCurrentRealm().isPrivateRealm()} DEV_HOLIDAYS={DEV_HOLIDAYS} current={self.currentHolidays}")
        for holiday in WEEKLY_HOLIDAYS:
            holidayId = holiday[0]
            day = holiday[1]
            if now.weekday() == day and holidayId not in self.currentHolidays:
                self.addHoliday(holidayId)
                self.startHoliday(holidayId)
            elif now.weekday() != day and holidayId in self.currentHolidays:
                self.removeHoliday(holidayId)
                self.endHoliday(holidayId)
        if RealmGlobals.getCurrentRealm().isPrivateRealm() and DEV_HOLIDAYS:
            # handle dev and QA holidays
            for holidayId in DEV_HOLIDAYS:
                if holidayId not in self.currentHolidays:
                    self.addHoliday(holidayId)
                    self.startHoliday(holidayId)
            return task.again
        for holiday in YEARLY_HOLIDAYS + ONCELY_HOLIDAYS:
            holidayId = holiday[0]
            # Note(YEARLY_HOLIDAYS): start/endDatetime properties and the getXDatetime() function calls
            # should automagically calculate the years for you
            start = holiday[1].startDatetime
            end = holiday[1].endDatetime
            if start < now < end and holidayId not in self.currentHolidays:
                if self.air.safeDistrict and holidayId in NON_SAFE_DISTRICT_HOLIDAYS:
                    # Skip holidays that are not meant to show up in safe districts
                    continue
                self.addHoliday(holidayId)
                self.startHoliday(holidayId)
            elif end < now and holidayId in self.currentHolidays:
                self.removeHoliday(holidayId)
                self.endHoliday(holidayId)
        return task.again

    def getCurPhase(self, holidayId):
        """
        TODO: Get Phase for Actual Holiday.

        :return: 1
        """
        return 1

    ### it's about sending a message ###

    def getPlayersInDistrict(self):
        """
        :return: a list of all the players doIds in the district
        """
        players = []
        for doId in self.air.doId2do:  # Loop through every object in the AI
            av = self.air.doId2do.get(doId)  # Let's make them an object
            if isinstance(av, DistributedToonAI.DistributedToonAI):  # Are they a real toon?
                players.append(doId)
        return players

    def messageDistrict(self, message):
        """
        Messages the entire district with the passed in message
        :type message: str
        """
        self.air.chatManager.sendSystemMessageShard(message, senderName=TTLocalizer.lToonHQ)

    ### holiday suit spawning ###

    def getTimeUntilSuitSpawn(self):
        """
        :returns: the amount of seconds until the next game should start.
            E.g. if minutes_between_game = 30
            The game will run at 12:00, 12:30, 13:00 etc
            if minutes_between_game = 7
            The game will run at 12:07, 12:14, 12:21 etc
        """
        return (HolidaySuitSpawnTime * 60) - (time.time() % (HolidaySuitSpawnTime * 60))

    def prepareHolidaySuit(self, task):
        # look into spawning the holiday suit
        self.messageDistrict(TTLocalizer.CountBulletinOne)

        taskMgr.remove('holiday-suit-spawn')
        taskMgr.remove('holiday-suit-regen')
        taskMgr.doMethodLater(4.0, self.spawnHolidaySuit, 'holiday-suit-regen')

    def spawnHolidaySuit(self, task):
        # get location and message
        zoneId = self.getHolidaySuitSpawnLocation()
        self.notify.info(f'Spawning a holiday suit in zone {zoneId}')
        streetName = ZoneUtil.getStreetName(zoneId)
        self.messageDistrict(TTLocalizer.CountBulletinTwo % streetName)
        # spawn the silly little suit
        sp = simbase.air.suitPlanners.get(zoneId - (zoneId % 100))
        pointmap = sp.streetPointList[:]
        countSuit = sp.createNewSuit(
            [], pointmap, suitName = HolidaySuit, suitLevel = 10, revives = True, exe = False, summoned = True
        )
        difficulty = zoneId // 1000
        self.applyHolidaySuitZoneDifficulty(countSuit, difficulty)
        # restart check
        if self.air.wantHalloween:
            taskMgr.doMethodLater(self.getTimeUntilSuitSpawn(), self.prepareHolidaySuit, 'holiday-suit-spawn')

    def getHolidaySuitSpawnLocation(self):
        # spawn suits in random locations
        if self.forceZoneSpawn:
            if self.forceZoneSpawn in HolidaySuitSpawns:
                spawnLoc = self.forceZoneSpawn
                self.forceZoneSpawn = None
                return spawnLoc
        bufferTime = HolidaySuitSpawnTime * 60 / 2  # adding a buffer time to make sure AIs are in sync
        currTime = time.time()
        # we do a little rng
        rngSeed = math.floor((currTime + bufferTime) // (HolidaySuitSpawnTime * 60))  # grows by 1 every 30 minutes
        state = random.getstate()
        random.seed(rngSeed)
        suitSpawn = random.choice(self._feasibleSuitSpawns())
        self._addSuitSpawnLocation(suitSpawn)
        random.setstate(state)
        return suitSpawn

    def _addSuitSpawnLocation(self, spawn):
        """Adds a pg where a suit was spawned."""
        self.pgsPicked.append((spawn // 1000) * 1000)
        if len(self.pgsPicked) > MaxPlaygroundDelay:
            self.pgsPicked.pop(0)

    def _feasibleSuitSpawns(self) -> list:
        """:returns: a feasible suit spawn location."""
        feasibleSpawns = []
        for spawn in HolidaySuitSpawns:
            if ((spawn // 1000) * 1000) not in self.pgsPicked:
                feasibleSpawns.append(spawn)
        if not feasibleSpawns:
            self.notify.warning("HolidayManagerAI somehow had no feasible spawns...?!")
            return list(HolidaySuitSpawns)
        return feasibleSpawns

    @staticmethod
    def applyHolidaySuitZoneDifficulty(suit, difficulty):
        mappedDiff = DifficultyMap[difficulty]
        if suit:
            suit.setLevel(10 + (mappedDiff * 2), hpMultIndex = 1)
