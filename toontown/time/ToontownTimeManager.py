import time
from datetime import datetime, timedelta
from direct.distributed import DistributedObject
from toontown.time.ToontownTimeZone import ToontownTimeZone, UTC
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class ToontownTimeManager(DistributedObject.DistributedObject):
    """
    A class to keep track of toontown time. Toontown time is essentially the
    server time, and matches the time zone and daylight savings changes.
    """
    ClockFormat = '%I:%M:%S %p'
    formatStr = '%Y-%m-%d %H:%M:%S'

    def __init__(self, serverTimeAtLogin=0, clientTimeAtLogin=0,
                 realTimeAtLogin=0):
        """Construct ourself. Default values are at 1970"""
        # TODO: Perhaps the AI and UD should have their own version of this class? SG-SLWP
        self.serverTimeZone = ToontownTimeZone()
        self.updateLoginTimes(serverTimeAtLogin, clientTimeAtLogin,
                              realTimeAtLogin)

    def updateLoginTimes(self, serverTimeAtLogin, clientTimeAtLogin,
                         realTimeAtLogin):
        """Update our fields to the new data"""
        self.serverTimeAtLogin = serverTimeAtLogin
        self.clientTimeAtLogin = clientTimeAtLogin
        self.realTimeAtLogin = realTimeAtLogin

        self.serverDateTime = datetime.fromtimestamp(
            self.serverTimeAtLogin, self.serverTimeZone)

    def getCurServerDateTime(self):
        """Return the current datetime object of the server."""
        secondsPassed = globalClock.getRealTime() - self.realTimeAtLogin
        dt = self.serverDateTime + timedelta(seconds=secondsPassed)
        return dt.astimezone(self.serverTimeZone)

    def convertStrToToontownTime(self, dateStr):
        """Converts a date string and returns a last logged in time, any errors returns current server time."""

        try:
            timeStruct = time.strptime(dateStr, self.formatStr)
            return datetime.fromtimestamp(time.mktime(timeStruct), self.serverTimeZone)
        except Exception as ex:
            self.notify.warning('error parsing date string: "%s": %s' % (dateStr, ex))

    def convertUtcStrToToontownTime(self, dateStr):
        """Converts a utc date string and returns toontown time, any errors returns current server time."""
        try:
            timeStruct = time.strptime(dateStr, self.formatStr)
            dtUtc = datetime(timeStruct[:6], UTC)
            return dtUtc.astimezone(self.serverTimeZone)
        except Exception as ex:
            self.notify.warning('error parsing date string: "%s": %s' % (dateStr, ex))
