from __future__ import annotations
from direct.distributed.DistributedObjectAI import DistributedObjectAI

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from .HolidayGlobals import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


@DirectNotifyCategory()
class NewsManagerAI(DistributedObjectAI):
    def __init__(self, air):
        """
        :type air: ToontownAIRepository
        """
        DistributedObjectAI.__init__(self, air)
        self.air = air  # type: ToontownAIRepository
        self.weeklyHolidays = WEEKLY_HOLIDAYS
        # decided to handle this a bit different, because we want to send tuple start and end times over the network
        # but I also wanted to make the logic in HolidayMangerAI cleaner too
        self.yearlyHolidays = tuple([holidayId, x.startTuple, x.endTuple] for holidayId, x in YEARLY_HOLIDAYS)
        self.oncelyHolidays = tuple([holidayId, x.startTuple, x.endTuple] for holidayId, x in ONCELY_HOLIDAYS)

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedObjectAI.announceGenerate(self)

        self.accept('avatarEntered', self.__handleAvatarEntered)

    def __handleAvatarEntered(self, avatar):
        if hasattr(simbase.air, 'suitInvasionManager'):
            if simbase.air.suitInvasionManager.getInvading():
                # Let this poor avatar who just came in the game know that there is a Cog Invasion taking place
                simbase.air.suitInvasionManager.notifyInvasionBulletin(avatar.getDoId())
        if not hasattr(simbase.air, 'holidayManager'):
            return
        if simbase.air.holidayManager.isHolidayRunning(MORE_XP_HOLIDAY):
            self.sendUpdateToAvatarId(avatar.getDoId(), 'setMoreXpHolidayOngoing', [])
        for holiday in self.weeklyHolidays:
            if simbase.air.holidayManager.isHolidayRunning(holiday[0]):
                # let them know about all holidays actually...
                self.sendUpdateToAvatarId(avatar.getDoId(), 'holidayNotify', [])
        if simbase.air.holidayManager.isHolidayRunning(HYDRANT_ZERO_HOLIDAY):
            self.sendUpdateToAvatarId(avatar.getDoId(), 'startHoliday', [HYDRANT_ZERO_HOLIDAY])

    def setPopulation(self, todo0):
        pass

    def setBingoWin(self, avatar, zoneId):
        self.sendUpdateToAvatarId(avatar.getDoId(), 'setBingoWin', [zoneId])

    def setBingoStart(self):
        self.sendUpdate('setBingoStart', [])

    def setBingoOngoing(self):
        self.sendUpdate('setBingoOngoing', [])

    def setBingoEnd(self):
        self.sendUpdate('setBingoEnd', [])

    def setCircuitRaceStart(self):
        self.sendUpdate('setCircuitRaceStart', [])

    def setCircuitRaceOngoing(self):
        self.sendUpdate('setCircuitRaceOngoing', [])

    def setCircuitRaceEnd(self):
        self.sendUpdate('setCircuitRaceEnd', [])

    def setTrolleyHolidayStart(self):
        self.sendUpdate('setTrolleyHolidayStart', [])

    def setTrolleyHolidayOngoing(self):
        self.sendUpdate('setTrolleyHolidayOngoing', [])

    def setTrolleyHolidayEnd(self):
        self.sendUpdate('setTrolleyHolidayEnd', [])

    def setTrolleyWeekendStart(self):
        self.sendUpdate('setTrolleyWeekendStart', [])

    def setTrolleyWeekendOngoing(self):
        self.sendUpdate('setTrolleyWeekendOngoing', [])

    def setTrolleyWeekendEnd(self):
        self.sendUpdate('setTrolleyWeekendEnd', [])

    def setSellbotNerfHolidayStart(self):
        self.sendUpdate('setSellbotNerfHolidayStart', [])

    def setSellbotNerfHolidayEnd(self):
        self.sendUpdate('setSellbotNerfHolidayEnd', [])

    def setMoreXpHolidayStart(self):
        self.sendUpdate('setMoreXpHolidayStart', [])

    def setMoreXpHolidayOngoing(self):
        self.sendUpdate('setMoreXpHolidayOngoing', [])

    def setMoreXpHolidayEnd(self):
        self.sendUpdate('setMoreXpHolidayEnd', [])

    def setInvasionStatus(self, msgType, cogType, numRemaining, skeleton):
        self.sendUpdate('setInvasionStatus', args = [msgType, cogType, numRemaining, skeleton])

    def d_setHolidayIdList(self, holidays):
        self.sendUpdate('setHolidayIdList', holidays)

    def holidayNotify(self):
        self.sendUpdate('holidayNotify', [])

    def d_setWeeklyCalendarHolidays(self, weeklyHolidays):
        self.sendUpdate('setWeeklyCalendarHolidays', [weeklyHolidays])

    def getWeeklyCalendarHolidays(self):
        return self.weeklyHolidays

    def d_setYearlyCalendarHolidays(self, yearlyHolidays):
        self.sendUpdate('setYearlyCalendarHolidays', [yearlyHolidays])

    def getYearlyCalendarHolidays(self):
        return self.yearlyHolidays

    def setOncelyCalendarHolidays(self, oncelyHolidays):
        self.sendUpdate('setOncelyCalendarHolidays', [oncelyHolidays])

    def getOncelyCalendarHolidays(self):
        return self.oncelyHolidays

    def setRelativelyCalendarHolidays(self, relatHolidays):
        self.sendUpdate('setRelativelyCalendarHolidays', [relatHolidays])

    def getRelativelyCalendarHolidays(self):
        return []

    def setMultipleStartHolidays(self, multiHolidays):
        self.sendUpdate('setMultipleStartHolidays', [multiHolidays])

    def getMultipleStartHolidays(self):
        return []

    def sendMilestoneMessage(self, message: str, senderName: str | None):
        """
        Send a milestone message to all clients in the server.
        String transferred through Astron to prevent data mining.
        """
        self.sendUpdate('announceMilestone', [message, senderName])
