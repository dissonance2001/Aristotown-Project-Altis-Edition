from toontown.ai import HolidayBaseAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BingoHolidayMgrAI(HolidayBaseAI.HolidayBaseAI):
    """
    BingoHolidayMgrAI(HolidayBaseAI)
    """

    PostName = 'BingoHoliday'
    StartStopMsg = 'BingoHolidayStartStop'

    def start(self):
        HolidayBaseAI.HolidayBaseAI.start(self)

        bboard.post(BingoHolidayMgrAI.PostName, True)
        simbase.air.newsManager.setBingoStart()
        messenger.send(BingoHolidayMgrAI.StartStopMsg)

    def stop(self):
        HolidayBaseAI.HolidayBaseAI.stop(self)

        bboard.remove(BingoHolidayMgrAI.PostName)
        simbase.air.newsManager.setBingoEnd()
        messenger.send(BingoHolidayMgrAI.StartStopMsg)
