from toontown.ai import HolidayBaseAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class BingoWeekendMgrAI(HolidayBaseAI.HolidayBaseAI):
    """
    BingoWeekendMgrAI(HolidayBaseAI)
    """

    PostName = 'BingoWeekend'
    StartStopMsg = 'BingoWeekendStartStop'

    def start(self):
        HolidayBaseAI.HolidayBaseAI.start(self)

        bboard.post(BingoWeekendMgrAI.PostName, True)
        simbase.air.newsManager.setBingoStart()
        messenger.send(BingoWeekendMgrAI.StartStopMsg)

    def stop(self):
        HolidayBaseAI.HolidayBaseAI.stop(self)

        bboard.remove(BingoWeekendMgrAI.PostName)
        simbase.air.newsManager.setBingoEnd()
        messenger.send(BingoWeekendMgrAI.StartStopMsg)
