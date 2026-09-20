import time
from datetime import datetime, timedelta, tzinfo

from panda3d.core import ConfigVariableString

# In the U.S., DST starts at 2AM (standard time) on the first Sunday in April:
DST_START = datetime(1, 3, 10, 2)

# ...and it ends at 2AM (DST time; 1AM standard time) on the last Sunday in
# October, which is the first Sunday on or after October 25th:
DST_END = datetime(1, 11, 3, 1)


def forwardToSunday(dt):
    daysLeft = 6 - dt.weekday()
    if daysLeft:
        dt += timedelta(daysLeft)
    return dt


class UTC(tzinfo):

    def tzname(self, dt):
        return 'UTC'

    def utcoffset(self, dt):
        return timedelta(0)

    def dst(self, dt):
        return timedelta(0)


class ToontownTimeZone(tzinfo):

    def __init__(self):
        timeZoneInfo = ConfigVariableString('server-timezone', 'EST/EDT/-5').getValue()
        self.stdName, self.dstName, self.stdOffset = timeZoneInfo.split('/')
        self.stdOffset = int(self.stdOffset)

    def tzname(self, dt):
        if self.dst(dt):
            return self.dstName
        else:
            return self.stdName

    def utcoffset(self, dt):
        return timedelta(hours=self.stdOffset) + self.dst(dt)

    def dst(self, dt):
        # Find the first Sunday in April, and the last in October:
        start = forwardToSunday(DST_START.replace(year=dt.year))
        end = forwardToSunday(DST_END.replace(year=dt.year))

        if start <= dt.replace(tzinfo=None) < end:
            return timedelta(hours=1)
        else:
            return timedelta(0)
    
    def __repr__(self) -> str:
        return "TTCCTimeZone"


# Day Zero
EPOCH = datetime.fromtimestamp(0)


def getServerEpochTime() -> float:
    """
    Returns a relative epoch time to ToontownTimeZone.
    You can think of this like doing time.time(), but getting
    the server-side time from it.
    :return: Time in seconds.
    """
    #now = datetime.now(tz=ToontownTimeZone())
    #return time.mktime((datetime.now(tz=ToontownTimeZone()) + now.dst()).timetuple())
    # for now, just assume time.time is always unix
    return time.time()


def getServerTimeOffset() -> float:
    """
    Returns the offset of the time.time() result for client for
    discreprencies for non EST peoples.
    """
    #return getServerEpochTime() - time.time()
    # also just assume time.time() is in unix, along with the client
    # I have a couple of ideas to patch this otherwise, but I need to hunt down *every*
    # place where timestamps are inconsistent
    return getServerEpochTime()
