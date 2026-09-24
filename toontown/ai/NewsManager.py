from toontown.chat.ChatGlobals import WTSystem   # top of the file
import calendar
from copy import deepcopy
from panda3d.core import *
from direct.distributed import DistributedObject
from toontown.chat.WhisperPopup import WhisperPopup

from toontown.ai import HolidayGlobals
from toontown.quest3.base import QuestGlobals

from toontown.chat.enums.ChatSystemMessagePreset import ChatSystemMessagePreset
from toontown.toonbase import ToontownGlobals
# from toontown.toonbase import BattleGlobals
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.toonbase import TTLocalizer
from direct.interval.IntervalGlobal import *
from toontown.clashsuit.suit import SuitDNA
from typing import TYPE_CHECKING

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

if TYPE_CHECKING:
    from toontown.distributed.ToontownClientRepository import ToontownClientRepository

decorationHolidays = (
    ToontownGlobals.CHRISTMAS,
    ToontownGlobals.HALLOWEEN,
)

"""
These holidays cause the 'promotional' speedchat menu to show up; only one of these should be active at a time!

If we want to support multiple simultaneously, we'll have to figure out a different way of putting the menus 
into the SpeedChat menu.

Currently there's a hidden menu that's always in the SpeedChat, waiting for one of these holidays to come along,
at which point it populates itself with phrases and becomes visible.
We *could* add a menu for every possible holiday, but that seems inefficient.
We could also dynamically insert the menus, but we don't have a robust method of inserting menus and items
into the SpeedChat beyond inserting at a specific index.
"""
promotionalSpeedChatHolidays = []


@DirectNotifyCategory()
class NewsManager(DistributedObject.DistributedObject):
    neverDisable = 1
    YearlyHolidayType = 1
    OncelyHolidayType = 2
    RelativelyHolidayType = 3
    OncelyMultipleStartHolidayType = 4

    def __init__(self, cr):
        """
        :param ToontownClientRepository cr: The client repository which maintains all client-side distributed objects.
        """
        DistributedObject.DistributedObject.__init__(self, cr)
        self.population = 0
        self.invading = 0


        # This is the current holiday Id just for decorations
        # Only one decoration holiday is active at a time
        self.decorationHolidayId = None

        # This dictionary keeps track of all active holidays
        # Multiple holidays may be active (i.e. decorations and fireworks)
        self.holidayIdList = []

        # Attach myself to the cr so others can access
        base.cr.newsManager = self

        self.weeklyCalendarHolidays = []

    def delete(self):
        self.cr.newsManager = None
        DistributedObject.DistributedObject.delete(self)

    def setPopulation(self, population):
        self.population = population
        messenger.send('newPopulation', [population])

    def getPopulation(self):
        return self.population

    def setInvasionStatus(self, msgType, suitType, remaining, flags):
        """
        Let the player know the status of any cog invasion taking place
        """
        deptInvasion = suitType in SuitDNA.suitDepts
        if deptInvasion:
            suitName = SuitDNA.getDeptFullname(suitType)
            suitNamePlural = SuitDNA.getDeptFullnameP(suitType)
        else:
            suitName = SuitBattleGlobals.SuitAttributes[suitType]['name']
            suitNamePlural = SuitBattleGlobals.SuitAttributes[suitType]['pluralname']

        messages = []

        if msgType == ToontownGlobals.SuitInvasionBegin:
            if deptInvasion:
                messages.append(TTLocalizer.SuitDepartmentInvasionBegin1)
                messages.append(TTLocalizer.SuitDepartmentInvasionBegin2.format(departmentNameP=suitNamePlural))
            else:
                messages.append(TTLocalizer.SuitInvasionBegin1)
                messages.append(TTLocalizer.SuitInvasionBegin2 % suitNamePlural)
            # Now are invading
            self.invading = 1
        elif msgType == ToontownGlobals.SuitInvasionEnd:
            messages.append(TTLocalizer.SuitInvasionEnd1 % suitName)
            messages.append(TTLocalizer.SuitInvasionEnd2)
            # No longer invading
            self.invading = 0
        elif msgType == ToontownGlobals.SuitInvasionUpdate:
            messages.append(TTLocalizer.SuitInvasionUpdate1)
            messages.append(TTLocalizer.SuitInvasionUpdate2)
            # Still invading
            self.invading = 1
        elif msgType == ToontownGlobals.SuitInvasionBulletin:
            if deptInvasion:
                messages.append(TTLocalizer.SuitDepartmentInvasionBulletin1)
                messages.append(TTLocalizer.SuitDepartmentInvasionBulletin2.format(departmentNameP=suitNamePlural))
            else:
                messages.append(TTLocalizer.SuitInvasionBulletin1)
                messages.append(TTLocalizer.SuitInvasionBulletin2 % suitNamePlural)
            self.invading = 1
        elif msgType == ToontownGlobals.SkelecogInvasionBegin:
            messages.append(TTLocalizer.SkelecogInvasionBegin1)
            messages.append(TTLocalizer.SkelecogInvasionBegin2)
            messages.append(TTLocalizer.SkelecogInvasionBegin3)
            self.invading = 1
        elif msgType == ToontownGlobals.SkelecogInvasionEnd:
            messages.append(TTLocalizer.SkelecogInvasionEnd1)
            messages.append(TTLocalizer.SkelecogInvasionEnd2)
            self.invading = 0
        elif msgType == ToontownGlobals.SkelecogInvasionBulletin:
            messages.append(TTLocalizer.SkelecogInvasionBulletin1)
            messages.append(TTLocalizer.SkelecogInvasionBulletin2)
            messages.append(TTLocalizer.SkelecogInvasionBulletin3)
            self.invading = 1
        elif msgType == ToontownGlobals.WaiterInvasionBegin:
            messages.append(TTLocalizer.WaiterInvasionBegin1)
            messages.append(TTLocalizer.WaiterInvasionBegin2)
            self.invading = 1
        elif msgType == ToontownGlobals.WaiterInvasionEnd:
            messages.append(TTLocalizer.WaiterInvasionEnd1)
            messages.append(TTLocalizer.WaiterInvasionEnd2)
            self.invading = 0
        elif msgType == ToontownGlobals.WaiterInvasionBulletin:
            messages.append(TTLocalizer.WaiterInvasionBulletin1)
            messages.append(TTLocalizer.WaiterInvasionBulletin2)
            messages.append(TTLocalizer.WaiterInvasionBulletin3)
            self.invading = 1
        elif msgType == ToontownGlobals.V2InvasionBegin:
            messages.append(TTLocalizer.V2InvasionBegin1)
            messages.append(TTLocalizer.V2InvasionBegin2)
            messages.append(TTLocalizer.V2InvasionBegin3)
            self.invading = 1
        elif msgType == ToontownGlobals.V2InvasionEnd:
            messages.append(TTLocalizer.V2InvasionEnd1)
            messages.append(TTLocalizer.V2InvasionEnd2)
            self.invading = 0
        elif msgType == ToontownGlobals.V2InvasionBulletin:
            messages.append(TTLocalizer.V2InvasionBulletin1)
            messages.append(TTLocalizer.V2InvasionBulletin2)
            messages.append(TTLocalizer.V2InvasionBulletin3)
            self.invading = 1
        elif msgType == ToontownGlobals.SuitMegaInvasionBegin:
            messages.append(TTLocalizer.SuitMegaInvasionBegin1)
            messages.append(TTLocalizer.SuitMegaInvasionBegin2 % suitNamePlural)
            self.invading = 1
        elif msgType == ToontownGlobals.SuitMegaInvasionEnd:
            messages.append(TTLocalizer.SuitMegaInvasionEnd1 % suitName)
            messages.append(TTLocalizer.SuitMegaInvasionEnd2)
            self.invading = 0
        elif msgType == ToontownGlobals.SuitMegaInvasionUpdate:
            messages.append(TTLocalizer.SuitMegaInvasionUpdate1)
            messages.append(TTLocalizer.SuitMegaInvasionUpdate2)
            self.invading = 1
        elif msgType == ToontownGlobals.ExeInvasionBegin:
            messages.append(TTLocalizer.ExeInvasionBegin1)
            messages.append(TTLocalizer.ExeInvasionBegin2 % suitNamePlural)
            self.invading = 1
        elif msgType == ToontownGlobals.ExeInvasionEnd:
            messages.append(TTLocalizer.ExeInvasionEnd1 % suitName)
            messages.append(TTLocalizer.ExeInvasionEnd2)
            self.invading = 0
        elif msgType == ToontownGlobals.ExeInvasionUpdate:
            messages.append(TTLocalizer.ExeInvasionUpdate1)
            messages.append(TTLocalizer.ExeInvasionUpdate2)
            self.invading = 1
        elif msgType == ToontownGlobals.ExeInvasionBulletin:
            messages.append(TTLocalizer.ExeInvasionBulletin1)
            messages.append(TTLocalizer.ExeInvasionBulletin2 % suitNamePlural)
            self.invading = 1
        else:
            self.notify.warning('setInvasionStatus: invalid msgType: %s' % msgType)
            return

        # Refresh gag xp display to fit invasion status
        base.localAvatar.inventory.setLiveCreditMult()

        track = Sequence(name = 'newsManagerWait', autoPause = 1)
        for i, message in enumerate(messages):
            if i == 0:
                track.append(Wait(1))
            else:
                track.append(Wait(5))
            track.append(Func(
                lambda msg=message: base.localAvatar.setSystemMessage(
                    0, '%s: %s' % (TTLocalizer.lToonHQ, msg), WTSystem)))

        track.start()

    def getInvading(self):
        return self.invading

    @staticmethod
    def speedChatExists():
        """
        Returns if SpeedChat exists.
        @return: True if it's safe to interact with SpeedChat, False if not.
        """
        return hasattr(base, 'localAvatar') and hasattr(base.localAvatar, 'chatContainer') and hasattr(base.localAvatar.chatContainer, 'speedChatMenu')

    def announceMessage(self, message: str, senderName=TTLocalizer.lToonHQ):
        av = getattr(base, 'localAvatar', None)
        if av:
            av.setSystemMessage(0, '%s: %s' % (senderName, message) if senderName else message, WTSystem)

    def startHoliday(self, holidayId):
        if holidayId not in self.holidayIdList:
            self.notify.info('setHolidayId: Starting Holiday %s' % holidayId)
            self.holidayIdList.append(holidayId)
            if holidayId in decorationHolidays:
                if self.decorationHolidayId is None:
                    self.decorationHolidayId = holidayId
                else:
                    self.notify.error(f"Attempted to run two decor holidays at the same time: curr:{self.decorationHolidayId} attempted:{holidayId}")

            if holidayId == ToontownGlobals.HALLOWEEN:
                base.wantHalloween = True
                self.announceMessage(TTLocalizer.HalloweenPropsHolidayStart)
                if self.speedChatExists():
                    base.localAvatar.chatContainer.speedChatMenu.addHalloweenMenu()

            elif holidayId == ToontownGlobals.CHRISTMAS:
                base.wantChristmas = True
                self.announceMessage(TTLocalizer.WinterDecorationsStart)
                if self.speedChatExists():
                    base.localAvatar.chatContainer.speedChatMenu.addWinterMenu()
                    base.localAvatar.chatContainer.speedChatMenu.addCarolMenu()

            elif holidayId == ToontownGlobals.MORE_XP_HOLIDAY:
                self.announceMessage(TTLocalizer.MoreXpHolidayStart)

            elif holidayId == ToontownGlobals.TROLLEY_HOLIDAY:
                self.announceMessage(TTLocalizer.TrolleyHolidayStart)

            elif holidayId == ToontownGlobals.DEPARTMENT_EXPERIENCE_HOLIDAY:
                self.announceMessage(TTLocalizer.DepartmentHolidayStart)

            elif holidayId == ToontownGlobals.ACTIVITY_EXPERIENCE_HOLIDAY:
                self.announceMessage(TTLocalizer.ActivityHolidayStart)

            elif holidayId == ToontownGlobals.WEALTHY_WEDNESDAY:
                self.announceMessage(TTLocalizer.WealthyWednesdayStart)

            # If gag friday, notify and refresh gag xp display
            elif holidayId == ToontownGlobals.GAG_EXPERIENCE_HOLIDAY:
                self.announceMessage(TTLocalizer.GagExperienceHolidayStart)
                base.localAvatar.inventory.setLiveCreditMult()

            # If gag friday, notify and refresh gag xp display
            elif holidayId == ToontownGlobals.GAG_EXPERIENCE_HOLIDAY_LTO:
                self.announceMessage(TTLocalizer.GagExperienceLTOHolidayStart)
                base.localAvatar.inventory.setLiveCreditMult()

            elif holidayId == ToontownGlobals.MERIT_HOLIDAY:
                self.announceMessage(TTLocalizer.MeritHolidayStart)

            elif holidayId == ToontownGlobals.SILLY_SATURDAY:
                self.announceMessage(TTLocalizer.SillySaturdayHolidayStart)

        #    elif holidayId in ToontownGlobals.SILLY_SATURDAY_ROTATION:
         #       self.announceMessage(TTLocalizer.SillySaturdayEvents[holidayId])

        #    elif holidayId == ToontownGlobals.BOSS_REWARD_HOLIDAY:
         #       self.announceMessage(TTLocalizer.BossRewardHolidayStart)

          #  elif holidayId == ToontownGlobals.HYDRANT_ZERO_HOLIDAY:
           #     self.setHydrantZeroHolidayStart()

            elif holidayId == ToontownGlobals.APRIL_FOOLS and self.speedChatExists():
                base.wantAprilFools = True
                base.localAvatar.chatContainer.speedChatMenu.addAprilToonsMenu()

            elif holidayId == ToontownGlobals.VALENTINES_DAY:
                messenger.send('ValentinesDayStart')
                self.announceMessage(TTLocalizer.ValentinesDayStart)

            elif holidayId == ToontownGlobals.BLACK_CAT_DAY:
                self.announceMessage(TTLocalizer.BlackCatHolidayStart)

            elif holidayId == ToontownGlobals.SPOOKY_BLACK_CAT:
                self.announceMessage(TTLocalizer.SpookyBlackCatHolidayStart)
                for currToon in list(base.cr.toons.values()):
                    currToon.setDNA(currToon.style.clone())

            elif holidayId == ToontownGlobals.IDES_OF_MARCH and self.speedChatExists():
                self.announceMessage(TTLocalizer.IdesOfMarchStart)
                base.localAvatar.chatContainer.speedChatMenu.addIdesOfMarchMenu()

            elif holidayId == ToontownGlobals.THANKSGIVING:
                self.announceMessage(TTLocalizer.ThanksgivingHolidayStart)

            elif holidayId == ToontownGlobals.BLACK_FRIDAY:
                self.announceMessage(TTLocalizer.BlackFridayStart)

            elif holidayId == ToontownGlobals.SPOOKY_BATCOIN_BOOST:
                self.announceMessage(TTLocalizer.BatcoinBoostStart)

            elif holidayId == ToontownGlobals.SPOOKY_BATCOIN_BOOST_FINAL:
                self.announceMessage(TTLocalizer.BatcoinBoostEnd)

            elif holidayId == ToontownGlobals.HALLOWEEN_MIX_WINTER_HOLIDAY:
                self.announceMessage(TTLocalizer.SpookyWinterHolidayStart)

            elif holidayId == ToontownGlobals.NATIONAL_BINGO_DAY_HOLIDAY:
                self.announceMessage(TTLocalizer.NationalBingoDayHolidayStart)

            elif holidayId == ToontownGlobals.CLASH_BIRTHDAY_DOUBLE_GUMBALLS:
                messenger.send(HolidayGlobals.GumballHolidayStatusMessage)
                self.announceMessage(TTLocalizer.ClashBirthdayDoubleGumballsStart)

            elif holidayId == ToontownGlobals.PIE_IN_THE_FACE_HOLIDAY:
                self.announceMessage(TTLocalizer.PieInTheFaceHolidayStart)

            elif holidayId == ToontownGlobals.BOARDBOT_MARKETING:
                self.announceMessage(TTLocalizer.BoardbotMarketingHolidayStart)

            elif holidayId == ToontownGlobals.BOARDBOT_MARKETING_FINALE:
                self.announceMessage(TTLocalizer.BoardbotMarketingFinaleHolidayStart)

    def endHoliday(self, holidayId):
        if holidayId in self.holidayIdList:
            self.notify.info('setHolidayId: Ending Holiday %s' % holidayId)
            self.holidayIdList.remove(holidayId)
            if holidayId in decorationHolidays: self.decorationHolidayId = None

            if holidayId in promotionalSpeedChatHolidays:
                if hasattr(base, 'TTSCPromotionalMenu'):
                    base.TTSCPromotionalMenu.endHoliday(holidayId)
            elif holidayId == ToontownGlobals.MORE_XP_HOLIDAY:
                self.announceMessage(TTLocalizer.MoreXpHolidayEnd)

            elif holidayId == ToontownGlobals.TROLLEY_HOLIDAY:
                self.announceMessage(TTLocalizer.TrolleyHolidayEnd)

            elif holidayId == ToontownGlobals.DEPARTMENT_EXPERIENCE_HOLIDAY:
                self.announceMessage(TTLocalizer.DepartmentHolidayEnd)

            elif holidayId == ToontownGlobals.ACTIVITY_EXPERIENCE_HOLIDAY:
                self.announceMessage(TTLocalizer.ActivityHolidayEnd)

            elif holidayId == ToontownGlobals.WEALTHY_WEDNESDAY:
                self.announceMessage(TTLocalizer.WealthyWednesdayEnd)

            elif holidayId == ToontownGlobals.GAG_EXPERIENCE_HOLIDAY:
                self.announceMessage(TTLocalizer.GagExperienceHolidayEnd)
                base.localAvatar.inventory.setLiveCreditMult()

            elif holidayId == ToontownGlobals.GAG_EXPERIENCE_HOLIDAY_LTO:
                self.announceMessage(TTLocalizer.GagExperienceLTOHolidayEnd)
                base.localAvatar.inventory.setLiveCreditMult()

            elif holidayId == ToontownGlobals.MERIT_HOLIDAY:
                self.announceMessage(TTLocalizer.MeritHolidayEnd)

            elif holidayId == ToontownGlobals.SILLY_SATURDAY:
                self.announceMessage(TTLocalizer.SillySaturdayHolidayEnd)

            elif holidayId == ToontownGlobals.BOSS_REWARD_HOLIDAY:
                self.announceMessage(TTLocalizer.BossRewardHolidayEnd)

            elif holidayId == ToontownGlobals.APRIL_FOOLS and self.speedChatExists():
                base.localAvatar.chatContainer.speedChatMenu.removeAprilToonsMenu()

            elif holidayId == ToontownGlobals.VALENTINES_DAY:
                messenger.send('ValentinesDayStop')
                self.announceMessage(TTLocalizer.ValentinesDayEnd)

            elif holidayId == ToontownGlobals.BLACK_CAT_DAY:
               self.announceMessage(TTLocalizer.BlackCatHolidayEnd)

            elif holidayId == ToontownGlobals.SPOOKY_BLACK_CAT:
                for currToon in list(base.cr.toons.values()):
                    currToon.setDNA(currToon.style.clone())

            elif holidayId == ToontownGlobals.IDES_OF_MARCH and self.speedChatExists():
                base.localAvatar.chatContainer.speedChatMenu.removeIdesOfMarchMenu()

            elif holidayId == ToontownGlobals.THANKSGIVING:
                self.announceMessage(TTLocalizer.ThanksgivingHolidayEnd)

            elif holidayId == ToontownGlobals.BLACK_FRIDAY:
                self.announceMessage(TTLocalizer.BlackFridayEnd)

            elif holidayId == ToontownGlobals.SPOOKY_BATCOIN_BOOST:
                self.announceMessage(TTLocalizer.BatcoinBoostEnd)

            elif holidayId == ToontownGlobals.HALLOWEEN_MIX_WINTER_HOLIDAY:
                self.announceMessage(TTLocalizer.SpookyWinterHolidayEnd)
                if self.speedChatExists():
                    base.localAvatar.chatContainer.speedChatMenu.removeCarolMenu()
                    base.localAvatar.chatContainer.speedChatMenu.removeWinterMenu()

            elif holidayId == ToontownGlobals.NATIONAL_BINGO_DAY_HOLIDAY:
                self.announceMessage(TTLocalizer.NationalBingoDayHolidayEnd)

            elif holidayId == ToontownGlobals.CLASH_BIRTHDAY_DOUBLE_GUMBALLS:
                messenger.send(HolidayGlobals.GumballHolidayStatusMessage)
                self.announceMessage(TTLocalizer.ClashBirthdayDoubleGumballsEnd)

            elif holidayId == ToontownGlobals.PIE_IN_THE_FACE_HOLIDAY:
                self.announceMessage(TTLocalizer.PieInTheFaceHolidayEnd)

    def setHolidayIdList(self, holidayIdList):
        def isEnding(id):
            return id not in holidayIdList

        def isStarting(id):
            return id not in self.holidayIdList

        # Which holidays are ending?
        toEnd = list(filter(isEnding, self.holidayIdList))
        for endingHolidayId in toEnd:
            self.endHoliday(endingHolidayId)

        # Which holidays are starting?
        toStart = list(filter(isStarting, holidayIdList))
        for startingHolidayId in toStart:
            self.startHoliday(startingHolidayId)

        messenger.send('setHolidayIdList', [holidayIdList])

    def getDecorationHolidayId(self):
        return self.decorationHolidayId

    def getHolidayIdList(self):
        return self.holidayIdList

    def setBingoWin(self, zoneId):
        self.announceMessage('Bingo congrats!')

    def setBingoStart(self):
        self.announceMessage(TTLocalizer.FishBingoStart)

    def setBingoOngoing(self):
        self.announceMessage(TTLocalizer.FishBingoOngoing)

    def setBingoEnd(self):
        self.announceMessage(TTLocalizer.FishBingoEnd)

    def setCircuitRaceStart(self):
        self.announceMessage(TTLocalizer.CircuitRaceStart)

    def setCircuitRaceOngoing(self):
        self.announceMessage(TTLocalizer.CircuitRaceOngoing)

    def setCircuitRaceEnd(self):
        self.announceMessage(TTLocalizer.CircuitRaceEnd)

    def setTrolleyHolidayStart(self):
        self.announceMessage(TTLocalizer.TrolleyHolidayStart)

    def setTrolleyHolidayOngoing(self):
        self.announceMessage(TTLocalizer.TrolleyHolidayOngoing)

    def setTrolleyHolidayEnd(self):
        self.announceMessage(TTLocalizer.TrolleyHolidayEnd)

    def setTrolleyWeekendStart(self):
        self.announceMessage(TTLocalizer.TrolleyWeekendStart)

    def setTrolleyWeekendOngoing(self):
        pass

    def setTrolleyWeekendEnd(self):
        self.announceMessage(TTLocalizer.TrolleyWeekendEnd)

    def setMoreXpHolidayStart(self):
        self.announceMessage(TTLocalizer.MoreXpHolidayStart)

    def setMoreXpHolidayOngoing(self):
        self.announceMessage(TTLocalizer.MoreXpHolidayOngoing)

    def setMoreXpHolidayEnd(self):
        self.announceMessage(TTLocalizer.MoreXpHolidayEnd)

    def setSellbotNerfHolidayStart(self):
        self.announceMessage(TTLocalizer.SellbotNerfHolidayStart)

    def setSellbotNerfHolidayEnd(self):
        self.announceMessage(TTLocalizer.SellbotNerfHolidayEnd)

    def holidayNotify(self):
        """
        Used to notify players just logging in of which weekday event is going on
        """
        for id in self.holidayIdList:
            if id == 19:
                self.setBingoOngoing()
            elif id == 20:
                self.setCircuitRaceOngoing()
            elif id == 21:
                self.setTrolleyHolidayOngoing()

    def setWeeklyCalendarHolidays(self, weeklyCalendarHolidays):
        """Handle the AI server telling us which weekly holidays to display."""
        self.weeklyCalendarHolidays = weeklyCalendarHolidays

    def getHolidaysForWeekday(self, day):
        """:return: a list of weekly holiday ids that match the given day of the week."""
        result = []
        for item in self.weeklyCalendarHolidays:
            if item[1] == day:
                result.append(item[0])
        return result

    def setYearlyCalendarHolidays(self, yearlyCalendarHolidays):
        """Handle the AI server telling us which yearly holidays to display."""
        self.yearlyCalendarHolidays = yearlyCalendarHolidays

    def getYearlyHolidaysForDate(self, theDate):
        """Return the yearly holidays which start or stop on the given date."""
        result = []
        for item in self.yearlyCalendarHolidays:
            if item[1][0] == theDate.month and item[1][1] == theDate.day:
                # holiday starts on this date
                newItem = [self.YearlyHolidayType] + list(item)
                result.append(tuple(newItem))
                continue
            if item[2][0] == theDate.month and item[2][1] == theDate.day:
                # holiday ends on this date
                newItem = [self.YearlyHolidayType] + list(item)
                result.append(tuple(newItem))

        return result

    def setMultipleStartHolidays(self, multipleStartHolidays):
        """Handle the AI server telling us which oncely holidays to display."""
        #  oncely differs from yearly holidays in that they have a fixed year
        self.multipleStartHolidays = multipleStartHolidays

    def getMultipleStartHolidaysForDate(self, theDate):
        """:return: the multiple start holidays which start or stop on the given date."""
        result = []
        for theHoliday in self.multipleStartHolidays:
            times = theHoliday[1:]
            # weird why it's we'd have to do this, investigate dc definition when we have time
            tempTimes = times[0]
            for startAndStopTimes in tempTimes:
                startTime = startAndStopTimes[0]
                endTime = startAndStopTimes[1]
                if startTime[0] == theDate.year and startTime[1] == theDate.month and startTime[2] == theDate.day:
                    # holiday starts on this date
                    # We fake the calendarGuiDay and say this is a oncely holiday
                    fakeOncelyHoliday = [theHoliday[0], startTime, endTime]
                    newItem = [self.OncelyMultipleStartHolidayType] + fakeOncelyHoliday
                    result.append(tuple(newItem))
                    continue
                if endTime[0] == theDate.year and endTime[1] == theDate.month and endTime[2] == theDate.day:
                    # holiday ends on this date
                    fakeOncelyHoliday = [theHoliday[0], startTime, endTime]
                    newItem = [self.OncelyMultipleStartHolidayType] + fakeOncelyHoliday
                    result.append(tuple(newItem))

        return result

    def setOncelyCalendarHolidays(self, oncelyCalendarHolidays):
        """Handle the AI server telling us which oncely holidays to display."""
        # oncely differs from yearly holidays in that they have a fixed year
        self.oncelyCalendarHolidays = oncelyCalendarHolidays

    def getOncelyHolidaysForDate(self, theDate):
        """:return: the oncely holidays which start or stop on the given date."""
        result = []
        for item in self.oncelyCalendarHolidays:
            if item[1][0] == theDate.year and item[1][1] == theDate.month and item[1][2] == theDate.day:
                # holiday starts on this date
                newItem = [self.OncelyHolidayType] + list(item)
                result.append(tuple(newItem))
                continue
            if item[2][0] == theDate.year and item[2][1] == theDate.month and item[2][2] == theDate.day:
                # holiday ends on this date
                newItem = [self.OncelyHolidayType] + list(item)
                result.append(tuple(newItem))

        return result

    def setRelativelyCalendarHolidays(self, relativelyCalendarHolidays):
        """Handle the AI server telling us which relatively holidays to display."""
        self.relativelyCalendarHolidays = relativelyCalendarHolidays

    def getRelativelyHolidaysForDate(self, theDate):
        """:return: the relatively holidays which start or stop on the given date."""
        result = []

        # A matrix of the number of times a weekday repeats in a month
        self.weekDaysInMonth = []

        # A matrix of the number of weekdays that repeat one extra time based on the number of days in the month.
        # For instance in a month with 31 days, the first two week days occur one more time than the other days.
        self.numDaysCorMatrix = [(28, 0), (29, 1), (30, 2), (31, 3)]

        # The minimum number of times a day repeats in a month
        for i in range(7):
            self.weekDaysInMonth.append((i, 4))

        for holidayItem in self.relativelyCalendarHolidays:
            item = deepcopy(holidayItem)

            newItem = []
            newItem.append(item[0])

            i = 1
            while i < len(item):
                sRepNum = item[i][1]
                sWeekday = item[i][2]
                eWeekday = item[i + 1][2]

                while True:
                    eRepNum = item[i + 1][1]

                    self.initRepMatrix(theDate.year, item[i][0])
                    while self.weekDaysInMonth[sWeekday][1] < sRepNum:
                        sRepNum -= 1

                    sDay = self.dayForWeekday(theDate.year, item[i][0], sWeekday, sRepNum)

                    self.initRepMatrix(theDate.year, item[i + 1][0])
                    while self.weekDaysInMonth[eWeekday][1] < eRepNum:
                        eRepNum -= 1

                    nDay = self.dayForWeekday(theDate.year, item[i + 1][0], eWeekday, eRepNum)

                    if ((nDay > sDay and
                     item[i+1][0] == item[i][0] and
                     (item[i+1][1] - item[i][1]) <= (nDay - sDay + abs(eWeekday - sWeekday))/7) or
                     item[i+1][0] != item[i][0]):
                        break

                    # Handles the case when the end weekday is less than the start
                    if self.weekDaysInMonth[eWeekday][1] > eRepNum:
                        eRepNum += 1
                    else:
                        item[i + 1][0] += 1
                        item[i + 1][1] = 1

                newItem.append([item[i][0], sDay, item[i][3], item[i][4], item[i][5]])

                newItem.append([item[i + 1][0], nDay, item[i + 1][3], item[i + 1][4], item[i + 1][5]])

                i += 2

            if item[1][0] == theDate.month and newItem[1][1] == theDate.day:
                # holiday starts on this date
                nItem = [self.RelativelyHolidayType] + list(newItem)
                result.append(tuple(nItem))
                continue

            if item[2][0] == theDate.month and newItem[2][1] == theDate.day:
                # holiday ends on this date
                nItem = [self.RelativelyHolidayType] + list(newItem)
                result.append(tuple(nItem))

        return result

    def dayForWeekday(self, year, month, weekday, repNum):
        """
        :returns: the day for a given weekday that has repeated repNum times for that month
        """
        monthDays = calendar.monthcalendar(year, month)
        if monthDays[0][weekday] == 0:
            repNum += 1
        return monthDays[repNum - 1][weekday]

    def initRepMatrix(self, year, month):
        """
        Initialize the number of times weekdays get repeated in a month.
        """
        for i in range(7):
            self.weekDaysInMonth[i] = (i, 4)

        startingWeekDay, numDays = calendar.monthrange(year, month)
        if startingWeekDay > 6:
            import pdb
            pdb.set_trace()
        for i in range(4):
            if numDays == self.numDaysCorMatrix[i][0]:
                break

        for j in range(self.numDaysCorMatrix[i][1]):
            self.weekDaysInMonth[startingWeekDay] = (
                self.weekDaysInMonth[startingWeekDay][0], self.weekDaysInMonth[startingWeekDay][1] + 1)
            startingWeekDay = (startingWeekDay + 1) % 7

    def isHolidayRunning(self, holidayId):
        """:return: True if a holiday is currently running."""
        # WARNING this will not properly handle holidays with delayed ends, like april fools and vampire mickey
        if type(holidayId) is list:
            for hid in holidayId:
                if hid in self.holidayIdList:
                    return True
            return False
        if holidayId in self.holidayIdList:
            return True
        else:
            return False

    def announceMilestone(self, message: str, senderName: str) -> None:
        """
        Display a received milestone message as a ToonHQ whisper.
        """
        self.announceMessage(message, senderName)
