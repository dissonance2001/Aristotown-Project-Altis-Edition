from datetime import datetime

from toontown.time.ToontownTimeZone import ToontownTimeZone
from toontown.toonbase.ToontownGlobals import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.inventory.enums.ItemEnums import *


@DirectNotifyCategory()
class HolidayDateRange(object):
    def __init__(self, startYear=None, startMonth=None, startDay=None, startHour=None, startMinute=None,
                 endYear=None, endMonth=None, endDay=None, endHour=None, endMinute=None, active=False):
        # start date+time stuff
        # this line is to shut Pycharm up about its "you didn't init this in __init__" warning
        self._startYear = self._startMonth = self._startDay = self._startHour = self._startMinute = None
        # then we call these setter calls to validate the args passed in
        self.startYear = startYear
        self.startMonth = startMonth
        self.startDay = startDay
        self.startHour = startHour
        self.startMinute = startMinute
        # end date+time stuff
        # see above for reasoning
        self._endYear = self._endMonth = self._endDay = self._endHour = self._endMinute = None
        # also see above
        self.endYear = endYear
        self.endMonth = endMonth
        self.endDay = endDay
        self.endHour = endHour
        self.endMinute = endMinute
        # going to assume this one will be a constant, and will also just forcibly make this a bool (even if someone
        #  sends an evil int instead)
        self.__active = True if active else False

    # helper functions

    def getStartDatetime(self):
        """
        Returns the start datetime object for the start of a holiday, uses current datetime values for year if None,
        and uses 0 for hour and minute if either are None

        :return: datetime object for the start date time stuff passed into this object
        """
        # we get default values for these 3 because datetime requires them to *not* be None (for some reason
        #  both month and day can be None)
        tz = ToontownTimeZone()
        now = datetime.now(tz=tz)
        year = now.year if self.startYear is None else self.startYear
        hour = 0 if self.startHour is None else self.startHour
        minute = 0 if self.startMinute is None else self.startMinute
        # attempt to automatically decrement year if startYear isn't set, startMonth is > endMonth *and* our current month < startMonth
        #  (I don't check to see if now.month == endMonth just on the offchance we somehow have a holiday that starts in december and
        #    ends in february)
        self.notify.debug(f'{self.startMonth}, {self.endMonth}, {now.month}, {self.startMonth > self.endMonth >= now.month}, {now <= datetime(now.year, self.endMonth, self.endDay, self.endHour, self.endMinute, tzinfo=tz)}')
        if self.startYear is None and self.startMonth > self.endMonth >= now.month and now <= datetime(now.year, self.endMonth, self.endDay, self.endHour, self.endMinute, tzinfo=tz):
            year -= 1
        return datetime(year=year, month=self.startMonth, day=self.startDay, hour=hour, minute=minute, tzinfo=tz)

    def getEndDatetime(self):
        """
        Returns the end datetime object for the end of a holiday, uses current datetime values for year if None,
        and uses 0 for hour and minute if either are None

        :return: datetime object for the end date time stuff passed into this object
        """
        # we get default values for these 3 because datetime requires them to *not* be None (for some reason
        #  both month and day can be None)
        tz = ToontownTimeZone()
        now = datetime.now(tz=tz)
        year = now.year if self.endYear is None else self.endYear
        # attempt to automatically increment year if endYear isn't set, startMonth is > endMonth *and* our current month < startMonth
        #  (I don't check to see if now.month == endMonth just on the offchance we somehow have a holiday that starts in december and
        #    ends in february)
        self.notify.debug(f'{self.startMonth}, {self.endMonth}, {now.month}, {self.startMonth > self.endMonth}, {now > datetime(now.year, self.endMonth, self.endDay, self.endHour, self.endMinute, tzinfo=tz)}')
        if self.endYear is None and self.startMonth > self.endMonth and now > datetime(now.year, self.endMonth, self.endDay, self.endHour, self.endMinute, tzinfo=tz):
            year += 1
        hour = 0 if self.endHour is None else self.endHour
        minute = 0 if self.endMinute is None else self.endMinute
        return datetime(year=year, month=self.endMonth, day=self.endDay, hour=hour, minute=minute, tzinfo=tz)

    def getNowDatetime(self):
        """
        Returns the current date and time as a datetime object, with the ToontownTimeZone timezone (important for holiday
        comparisons)

        :return: datetime object for the current date and time
        """
        return datetime.now(tz=ToontownTimeZone())

    # properties

    @property
    def startYear(self):
        return self._startYear

    @startYear.setter
    def startYear(self, year):
        if year is not None:
            if not isinstance(year, int):
                self.notify.error(f"startYear must be of type int/None, not '{type(year)}'!", exception=TypeError)
            elif year < 0:
                self.notify.error("startYear must be greater than or equal to 0!", exception=ValueError)
        self._startYear = year

    @property
    def startMonth(self):
        return self._startMonth

    @startMonth.setter
    def startMonth(self, month):
        if month is not None:
            if not isinstance(month, int):
                self.notify.error(f"startMonth must be of type int/None, not '{type(month)}'!", exception=TypeError)
            elif month not in range(1, 13):
                self.notify.error("startMonth must be in range 1-12!", exception=ValueError)
        self._startMonth = month

    @property
    def startDay(self):
        return self._startDay

    @startDay.setter
    def startDay(self, day):
        if day is not None:
            if not isinstance(day, int):
                self.notify.error(f"startDay must be of type int/None, not '{type(day)}'!", exception=TypeError)
            elif day not in range(1, 32):
                # not gonna do an extreme check for range for each month here
                self.notify.error("startDay must be in range 1-31!", exception=ValueError)
        self._startDay = day

    @property
    def startHour(self):
        return self._startHour

    @startHour.setter
    def startHour(self, hour):
        if hour is not None:
            if not isinstance(hour, int):
                self.notify.error(f"startHour must be of type int/None, not '{type(hour)}'!", exception=TypeError)
            elif hour not in range(24):
                self.notify.error("startHour must be in range 0-23!", exception=ValueError)
        self._startHour = hour

    @property
    def startMinute(self):
        return self._startMinute

    @startMinute.setter
    def startMinute(self, minute):
        if minute is not None:
            if not isinstance(minute, int):
                self.notify.error(f"startMinute must be of type int/None, not '{type(minute)}'!", exception=TypeError)
            elif minute not in range(60):
                self.notify.error("startMinute must be in range 0-59!", exception=ValueError)
        self._startMinute = minute

    @property
    def endYear(self):
        return self._endYear

    @endYear.setter
    def endYear(self, year):
        if year is not None:
            if not isinstance(year, int):
                self.notify.error(f"endYear must be of type int/None, not '{type(year)}'!", exception=TypeError)
            elif year < 0:
                self.notify.error("endYear must be greater than or equal to 0!", exception=ValueError)
        self._endYear = year

    @property
    def endMonth(self):
        return self._endMonth

    @endMonth.setter
    def endMonth(self, month):
        if month is not None:
            if not isinstance(month, int):
                self.notify.error(f"endMonth must be of type int/None, not '{type(month)}'!", exception=TypeError)
            elif month not in range(1, 13):
                self.notify.error("endMonth must be in range 1-12!", exception=ValueError)
        self._endMonth = month

    @property
    def endDay(self):
        return self._endDay

    @endDay.setter
    def endDay(self, day):
        if day is not None:
            if not isinstance(day, int):
                self.notify.error(f"endDay must be of type int/None, not '{type(day)}'!", exception=TypeError)
            elif day not in range(1, 32):
                # not gonna do an extreme check for range for each month here
                self.notify.error("endDay must be in range 1-31!", exception=ValueError)
        self._endDay = day

    @property
    def endHour(self):
        return self._endHour

    @endHour.setter
    def endHour(self, hour):
        if hour is not None:
            if not isinstance(hour, int):
                self.notify.error(f"endHour must be of type int/None, not '{type(hour)}'!", exception=TypeError)
            elif hour not in range(24):
                self.notify.error("endHour must be in range 0-23!", exception=ValueError)
        self._endHour = hour

    @property
    def endMinute(self):
        return self._endMinute

    @endMinute.setter
    def endMinute(self, minute):
        if minute is not None:
            if not isinstance(minute, int):
                self.notify.error(f"endMinute must be of type int/None, not '{type(minute)}'!", exception=TypeError)
            elif minute not in range(60):
                self.notify.error("endMinute must be in range 0-59!", exception=ValueError)
        self._endMinute = minute

    @property
    def startDatetime(self):
        return self.getStartDatetime()

    @property
    def endDatetime(self):
        return self.getEndDatetime()

    @property
    def nowDatetime(self):
        # This one seems a bit more useful to get the current datetime, with the correct timezone for comparisons
        return self.getNowDatetime()

    @property
    def timezone(self):
        # I dunno why anyone would need a timezone object, but here you go ig
        return ToontownTimeZone()

    @property
    def active(self):
        return self.__active


@DirectNotifyCategory()
class YearlyHolidayDateRange(HolidayDateRange):
    """
    'date range' object for yearly holidays (this doesn't define start/end years, and is calculated when needed)
    """

    def __init__(self, startMonth=None, startDay=None, startHour=None, startMinute=None,
                 endMonth=None, endDay=None, endHour=None, endMinute=None, active=False):
        # we will let the start/getEndDatetime() calls calculate the year for us
        super().__init__(startMonth=startMonth, startDay=startDay, startHour=startHour, startMinute=startMinute,
                         endMonth=endMonth, endDay=endDay, endHour=endHour, endMinute=endMinute, active=active)

    # helper funcs

    def getStartTuple(self):
        return self.startMonth, self.startDay, self.startHour, self.startMinute

    def getEndTuple(self):
        return self.endMonth, self.endDay, self.endHour, self.endMinute

    # properties

    @property
    def _thisYearAndMonth(self):
        tz = ToontownTimeZone()
        now = datetime.now(tz=tz)
        return now.year, now.month

    @property
    def startYear(self):
        currentYear, currentMonth = self._thisYearAndMonth

        if self.startMonth > self.endMonth:
            # This event wraps all the way around the year!
            # So, if we are in the next year, then
            # the start year will have to have been last year.
            if currentMonth < self.startMonth:
                return currentYear - 1

        # Otherwise, it is sufficient to say that we
        # are currently in the right year.
        return currentYear

    @startYear.setter
    def startYear(self, year):
        if year is not None:
            if not isinstance(year, int):
                self.notify.error(f"startYear must be of type int/None, not '{type(year)}'!", exception=TypeError)
            elif year < 0:
                self.notify.error("startYear must be greater than or equal to 0!", exception=ValueError)
        self._startYear = year

    @property
    def endYear(self):
        currentYear, currentMonth = self._thisYearAndMonth

        if self.startMonth > self.endMonth:
            # This event wraps all the way around the year!
            # So, if we are in the next year, then
            # the end year will have to be this year.
            if currentMonth < self.startMonth:
                return currentYear

            # If this is not the case, then we will say that
            # this event wlil have to end next year.
            else:
                return currentYear + 1

        # Otherwise, it is sufficient to say that we
        # are currently in the right year.
        return currentYear

    @endYear.setter
    def endYear(self, year):
        if year is not None:
            if not isinstance(year, int):
                self.notify.error(f"endYear must be of type int/None, not '{type(year)}'!", exception=TypeError)
            elif year < 0:
                self.notify.error("endYear must be greater than or equal to 0!", exception=ValueError)
        self._endYear = year

    @property
    def startTuple(self):
        return self.getStartTuple()

    @property
    def endTuple(self):
        return self.getEndTuple()


@DirectNotifyCategory()
class OncelyHolidayDateRange(HolidayDateRange):
    """
    'date range' object for oncely holidays (this is essentially the same as HolidayDateRange, but with a 'specific' name attached to the class)
    """
    # helper funcs

    def getStartTuple(self):
        return self.startYear, self.startMonth, self.startDay, self.startHour, self.startMinute

    def getEndTuple(self):
        return self.endYear, self.endMonth, self.endDay, self.endHour, self.endMinute

    # properties

    @property
    def startTuple(self):
        return self.getStartTuple()

    @property
    def endTuple(self):
        return self.getEndTuple()


# NOTE: this is getting defined because Quests+NPCs needs this to always be defined, RIP
# I will end up setting YEARLY_HOLIDAYS and ONCELY_HOLIDAYS with some of this data so that Holiday/NewsManagerAI doesn't
# need extra rewriting, and to allow devs to control what is shown in the book, and what is actually run
# NOTE 2: append `active=True` to any of these that you want running in the future for certain (at the time of writing
#  this only appears to be valentines day (and by technicality the gag experience holiday that already passed)
HOLIDAY2RANGE = {
    # yearly holidays
    # HolidayID: YearlyHolidayDateRange(begin<Month, Day, Hour, Minute>, end<Month, Day, Hour, Minute>)
    NEWYEARS_FIREWORKS: YearlyHolidayDateRange(12, 29, 0, 0, 1, 4, 0, 0),
    VALENTINES_DAY: YearlyHolidayDateRange(2, 12, 0, 0, 2, 22, 0, 0, active=True),
    IDES_OF_MARCH: YearlyHolidayDateRange(3, 14, 12, 0, 3, 20, 0, 0),
    APRIL_FOOLS: YearlyHolidayDateRange(4, 28, 0, 0, 6, 11, 23, 59),
    JULY4_FIREWORKS: YearlyHolidayDateRange(7, 4, 0, 0, 7, 4, 23, 59),
    NATIONAL_BINGO_DAY_HOLIDAY: YearlyHolidayDateRange(6, 27, 0, 0, 6, 27, 23, 59, active=True),
    CLASH_BIRTHDAY_DOUBLE_GUMBALLS: YearlyHolidayDateRange(7, 2, 0, 0, 7, 3, 23, 59, active=True),
    PIE_IN_THE_FACE_HOLIDAY: YearlyHolidayDateRange(11, 27, 0, 0, 11, 27, 23, 59, active=True),
    HALLOWEEN: YearlyHolidayDateRange(10, 20, 0, 0, 11, 24, 0, 0),
    # SKELECOG_INVASION: YearlyHolidayDateRange(10, 23, 0, 0, 11, 1, 0, 0),
    CHRISTMAS: YearlyHolidayDateRange(12, 15, 0, 0, 1, 14, 0, 0),
    THANKSGIVING: YearlyHolidayDateRange(11, 23, 0, 0, 12, 5, 0, 0),
    # BLACK_FRIDAY: YearlyHolidayDateRange(11, 26, 0, 0, 11, 27, 0, 0),
    # SPOOKY_BATCOIN_BOOST: YearlyHolidayDateRange(10, 30, 0, 0, 11, 2, 0, 0),
    # SPOOKY_BATCOIN_BOOST_FINAL: YearlyHolidayDateRange(11, 10, 0, 0, 11, 8, 0, 0),
    # oncely holidays
    # HolidayID: OncelyHolidayDateRange(begin<Year, Month, Day, Hour, Minute>, end<Year, Month, Day, Hour, Minute>)
    # GAG_EXPERIENCE_HOLIDAY_LTO: OncelyHolidayDateRange(2022, 4, 1, 0, 0, 2022, 4, 15, 0, 0, active=True),
    HALLOWEEN_MIX_WINTER_HOLIDAY: OncelyHolidayDateRange(2022, 12, 18, 0, 0, 2023, 1, 9, 0, 0),
}


# (Holiday, Weekday)
WEEKLY_HOLIDAYS = (
    (MERIT_HOLIDAY, 0),  # Monday
    (ACTIVITY_EXPERIENCE_HOLIDAY, 1),  # Tuesday
    (WEALTHY_WEDNESDAY, 2),  # Wednesday
    (DEPARTMENT_EXPERIENCE_HOLIDAY, 3),  # Thursday
    (GAG_EXPERIENCE_HOLIDAY, 4),  # Friday
    (SILLY_SATURDAY, 5),  # Saturday
    (BOSS_REWARD_HOLIDAY, 6),  # Sunday
)

# Generate a tuple of yearly holidays whose class is YearlyHolidayDateRange *and* is manually marked to be 'active'
# format: (HolidayId, HOLIDAY2RANGE[HolidayId])
YEARLY_HOLIDAYS = tuple((holidayId, holidayRange) for holidayId, holidayRange in HOLIDAY2RANGE.items() if isinstance(holidayRange, YearlyHolidayDateRange) and holidayRange.active)
# make holidayId lookup easier for some places, while keeping current logic requiring a list/tuple intact
YEARLY_HOLIDAYS_DICT = {holidayId: dateRange for holidayId, dateRange in YEARLY_HOLIDAYS}


# Associate certain Holiday's with catalog redemption items on login.
HOLIDAY_LOGIN_REDEMPTION = {
    VALENTINES_DAY: (BackpackItemType.CupidBow, BackpackItemType.CupidBowQuiver),
}

# Holidays that will not start in safe districts
NON_SAFE_DISTRICT_HOLIDAYS = (
    BOARDBOT_MARKETING,
    BOARDBOT_MARKETING_FINALE,
)


# List of Holidays to be automatically enabled
# on development or QA servers.
DEV_HOLIDAYS = (
    # CLASH_BIRTHDAY_DOUBLE_GUMBALLS,
    # HALLOWEEN_MIX_WINTER_HOLIDAY,
    # APRIL_FOOLS,
    # HALLOWEEN,
    # CHRISTMAS,
)

# Generate a tuple of oncely holidays whose class is OncelyHolidayDateRange *and* is manually marked to be 'active'
# format: (HolidayId, HOLIDAY2RANGE[HolidayId])
ONCELY_HOLIDAYS = tuple((holidayId, holidayRange) for holidayId, holidayRange in HOLIDAY2RANGE.items() if isinstance(holidayRange, OncelyHolidayDateRange) and holidayRange.active)
# make holidayId lookup easier for some places, while keeping current logic requiring a list/tuple intact
ONCELY_HOLIDAYS_DICT = {holidayId: dateRange for holidayId, dateRange in ONCELY_HOLIDAYS}

# Let certain text know to adjust itself when a holiday has become active/inactive
GumballHolidayStatusMessage = 'HolidayManager-GumballHolidayChanged'
