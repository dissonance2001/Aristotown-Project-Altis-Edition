import datetime
from panda3d.core import TextNode, Vec3, Vec4, PlaneNode, Plane, Point3
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DirectScrolledList, DGG
from direct.gui import DirectGuiGlobals

from toontown.restoration import RestorationGlobals
from toontown.toon.gui import GuiBinGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.ai.NewsManager import NewsManager
from functools import cmp_to_key

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


def myStrftime(myTime):
    result = ''
    result = myTime.strftime('%I')
    if result[0] == '0':
        result = result[1:]
    result += myTime.strftime(':%M %p')
    return result


@DirectNotifyCategory()
class CalendarGuiDay(DirectFrame):
    ScrollListTextSize = 0.03

    def __init__(self, parent, myDate, startDate, dayClickCallback=None, onlyFutureDaysClickable=False):
        self.origParent = parent
        self.startDate = startDate
        self.myDate = myDate
        self.dayClickCallback = dayClickCallback
        self.onlyFutureDaysClickable = onlyFutureDaysClickable
        DirectFrame.__init__(self, parent=parent)
        self.timedEvents = []
        self.partiesInvitedToToday = []
        self.hostedPartiesToday = []
        self.yearlyHolidaysToday = []
        self.showMarkers = ConfigVariableBool('show-calendar-markers', 0).getValue()
        self.filter = ToontownGlobals.CalendarFilterShowAll
        self.load()
        self.createGuiObjects()
        self.update()

    def createDummyLocators(self):
        self.dayButtonLocator = self.attachNewNode('dayButtonLocator')
        self.dayButtonLocator.setX(0.1)
        self.dayButtonLocator.setZ(-0.05)
        self.numberLocator = self.attachNewNode('numberLocator')
        self.numberLocator.setX(0.09)
        self.scrollLocator = self.attachNewNode('scrollLocator')
        self.selectedLocator = self.attachNewNode('selectedLocator')
        self.selectedLocator.setX(0.11)
        self.selectedLocator.setZ(-0.06)

    def load(self):
        dayAsset = loader.loadModel('phase_4/models/parties/tt_m_gui_sbk_calendar_box')
        dayAsset.reparentTo(self)
        self.dayButtonLocator = self.find('**/loc_origin')
        self.numberLocator = self.find('**/loc_number')
        self.scrollLocator = self.find('**/loc_topLeftList')
        self.selectedLocator = self.find('**/loc_origin')
        self.todayBox = self.find('**/boxToday')
        self.todayBox.hide()
        self.selectedFrame = self.find('**/boxHover')
        self.selectedFrame.hide()
        self.defaultBox = self.find('**/boxBlank')
        self.scrollBottomRightLocator = self.find('**/loc_bottomRightList')
        self.scrollDownLocator = self.find('**/loc_scrollDown')
        self.attachMarker(self.scrollDownLocator)
        self.scrollUpLocator = self.find('**/loc_scrollUp')
        self.attachMarker(self.scrollUpLocator)

    def attachMarker(self, parent, scale=0.005, color=(1, 0, 0)):
        if self.showMarkers:
            marker = loader.loadModel('phase_3/models/misc/sphere')
            marker.reparentTo(parent)
            marker.setScale(scale)
            marker.setColor(*color)

    def createGuiObjects(self):
        self.dayButton = DirectButton(parent=self.dayButtonLocator, image=self.selectedFrame, relief=None,
                                      command=self.__clickedOnDay, pressEffect=1, rolloverSound=None, clickSound=None)
        self.numberWidget = DirectLabel(parent=self.numberLocator, relief=None, text=str(self.myDate.day),
                                        text_scale=0.04, text_align=TextNode.ACenter,
                                        text_font=ToontownGlobals.getInterfaceFont(),
                                        text_fg=Vec4(110 / 255.0, 126 / 255.0, 255 / 255.0, 1))
        self.attachMarker(self.numberLocator)
        self.listXorigin = 0
        self.listFrameSizeX = self.scrollBottomRightLocator.getX() - self.scrollLocator.getX()
        self.scrollHeight = self.scrollLocator.getZ() - self.scrollBottomRightLocator.getZ()
        self.listZorigin = self.scrollBottomRightLocator.getZ()
        self.listFrameSizeZ = self.scrollLocator.getZ() - self.scrollBottomRightLocator.getZ()
        self.arrowButtonXScale = 1
        self.arrowButtonZScale = 1
        self.itemFrameXorigin = 0
        self.itemFrameZorigin = 0
        self.buttonXstart = self.itemFrameXorigin + 0.21
        self.gui = loader.loadModel('phase_3.5/models/gui/friendslist_gui')
        buttonOffSet = -0.01
        incButtonPos = (0.0, 0, 0)
        decButtonPos = (0.0, 0, 0)
        itemFrameMinZ = self.listZorigin
        itemFrameMaxZ = self.listZorigin + self.listFrameSizeZ
        arrowUp = self.find('**/downScroll_up')
        arrowDown = self.find('**/downScroll_down')
        arrowHover = self.find('**/downScroll_hover')
        self.scrollList = DirectScrolledList(parent=self.scrollLocator, relief=None, pos=(0, 0, 0),
                                             incButton_image=(arrowUp,
                                                              arrowDown,
                                                              arrowHover,
                                                              arrowUp), incButton_relief=None,
                                             incButton_scale=(self.arrowButtonXScale, 1, self.arrowButtonZScale),
                                             incButton_pos=incButtonPos, incButton_image3_color=Vec4(1, 1, 1, 0.2),
                                             decButton_image=(arrowUp,
                                                              arrowDown,
                                                              arrowHover,
                                                              arrowUp), decButton_relief=None,
                                             decButton_scale=(self.arrowButtonXScale, 1, -self.arrowButtonZScale),
                                             decButton_pos=decButtonPos, decButton_image3_color=Vec4(1, 1, 1, 0.2),
                                             itemFrame_pos=(self.itemFrameXorigin, 0, -0.03), numItemsVisible=4,
                                             incButtonCallback=self.scrollButtonPressed,
                                             decButtonCallback=self.scrollButtonPressed)
        itemFrameParent = self.scrollList.itemFrame.getParent()
        self.scrollList.incButton.reparentTo(self.scrollDownLocator)
        self.scrollList.decButton.reparentTo(self.scrollUpLocator)
        arrowUp.removeNode()
        arrowDown.removeNode()
        arrowHover.removeNode()
        clipper = PlaneNode('clipper')
        clipper.setPlane(Plane(Vec3(-1, 0, 0), Point3(0.23, 0, 0)))
        clipNP = self.scrollList.component('itemFrame').attachNewNode(clipper)
        self.scrollList.component('itemFrame').setClipPlane(clipNP)

    def scrollButtonPressed(self):
        self.__clickedOnDay()

    def adjustForMonth(self):
        curServerDate = base.cr.toontownTimeManager.getCurServerDateTime()
        if self.onlyFutureDaysClickable:
            if self.myDate.year < curServerDate.year or self.myDate.year == curServerDate.year and self.myDate.month < curServerDate.month or self.myDate.year == curServerDate.year and self.myDate.month == curServerDate.month and self.myDate.day < curServerDate.day:
                self.numberWidget.setColorScale(0.5, 0.5, 0.5, 0.5)
                self.numberWidget['state'] = DirectGuiGlobals.DISABLED
            else:
                self.numberWidget.setColorScale(1, 1, 1, 1)
        if self.myDate.month != self.startDate.month:
            self.setColorScale(0.75, 0.75, 0.75, 1.0)
            if self.dayClickCallback is not None:
                self.numberWidget['state'] = DirectGuiGlobals.DISABLED
        else:
            self.setColorScale(1, 1, 1, 1)
        if self.myDate.date() == curServerDate.date():
            self.defaultBox.hide()
            self.todayBox.show()
        else:
            self.defaultBox.show()
            self.todayBox.hide()

    def destroy(self):
        if self.dayClickCallback is not None:
            self.numberWidget.destroy()
        self.dayClickCallback = None
        self.notify.debug('desroying %s' % self.myDate)
        try:
            for item in self.scrollList['items']:
                if hasattr(item, 'description') and item.description and hasattr(item.description, 'destroy'):
                    self.notify.debug('desroying description of item %s' % item)
                    item.unbind(DGG.ENTER)
                    item.unbind(DGG.EXIT)
                    item.description.destroy()

        except e:
            self.notify.debug('pass %s' % self.myDate)

        self.scrollList.removeAndDestroyAllItems()
        self.scrollList.destroy()
        self.dayButton.destroy()
        DirectFrame.destroy(self)

    def addWeeklyHolidays(self):
        if not self.filter == ToontownGlobals.CalendarFilterShowAll and not self.filter == ToontownGlobals.CalendarFilterShowOnlyHolidays:
            return
        if base.cr.newsManager:
            holidays = base.cr.newsManager.getHolidaysForWeekday(self.myDate.weekday())
            holidayName = ''
            holidayDesc = ''
            for holidayId in holidays:
                if holidayId in TTLocalizer.HolidayNamesInCalendar:
                    holidayName = TTLocalizer.HolidayNamesInCalendar[holidayId][0]
                    holidayDesc = TTLocalizer.HolidayNamesInCalendar[holidayId][1]
                else:
                    holidayName = TTLocalizer.UnknownHoliday % holidayId
                self.addTitleAndDescToScrollList(holidayName, holidayDesc)

            self.scrollList.refresh()
        if ConfigVariableBool('calendar-test-items', False).getValue():
            if self.myDate.date() + datetime.timedelta(
                days=-1) == base.cr.toontownTimeManager.getCurServerDateTime().date():
                testItems = ('1:00 AM Party', '2:00 AM CEO', '11:15 AM Party', '5:30 PM CJ', '11:00 PM Party',
                             'Really Really Long String')
                for text in testItems:
                    newItem = DirectLabel(relief=None, text=text, text_scale=self.ScrollListTextSize,
                                          text_align=TextNode.ALeft)
                    self.scrollList.addItem(newItem)

            if self.myDate.date() + datetime.timedelta(
                days=-2) == base.cr.toontownTimeManager.getCurServerDateTime().date():
                testItems = ('1:00 AM Party', '3:00 AM CFO', '11:00 AM Party')
                textSize = self.ScrollListTextSize
                for text in testItems:
                    newItem = DirectLabel(relief=None, text=text, text_scale=textSize, text_align=TextNode.ALeft)
                    self.scrollList.addItem(newItem)

    def addDynamicEvents(self):
        """
        Adds dynamic events to the Calendar day.
        """
        if not self.filter == ToontownGlobals.CalendarFilterShowAll and not self.filter == ToontownGlobals.CalendarFilterShowOnlyHolidays:
            return
        if not base.cr.newsManager:
            return

        # When can we redraw and rename again?
        self.addImmediateHolidayToScrollList(
            holidayId=1001, holidayTime=base.localAvatar.lastRedrawTimestamp + RestorationGlobals.RedrawCooldown
        )
        self.addImmediateHolidayToScrollList(
            holidayId=1002, holidayTime=base.localAvatar.lastRenameTimestamp + RestorationGlobals.RenameCooldown
        )

    def updateArrowButtons(self):
        numItems = 0
        try:
            numItems = len(self.scrollList['items'])
        except e:
            numItems = 0

        if numItems <= self.scrollList._DirectScrolledList__numItemsVisible:
            self.scrollList.incButton.hide()
            self.scrollList.decButton.hide()
        else:
            self.scrollList.incButton.show()
            self.scrollList.decButton.show()

    def collectTimedEvents(self):
        self.timedEvents = []

        if base.cr.newsManager and (
            self.filter == ToontownGlobals.CalendarFilterShowAll or self.filter == ToontownGlobals.CalendarFilterShowOnlyHolidays):
            yearlyHolidays = base.cr.newsManager.getYearlyHolidaysForDate(self.myDate)
            for holiday in yearlyHolidays:
                holidayId = holiday[1]
                holidayStart = holiday[2]
                holidayEnd = holiday[3]
                holidayType = holiday[0]
                if holidayStart[0] == self.myDate.month and holidayStart[1] == self.myDate.day:
                    myTime = datetime.time(holidayStart[2], holidayStart[3], tzinfo=self.myDate.tzinfo)
                elif holidayEnd[0] == self.myDate.month and holidayEnd[1] == self.myDate.day:
                    myTime = datetime.time(holidayEnd[2], holidayEnd[3], tzinfo=self.myDate.tzinfo)
                else:
                    self.notify.error('holiday is not today %s' % holiday)
                self.timedEvents.append((myTime, holiday))

            oncelyHolidays = base.cr.newsManager.getOncelyHolidaysForDate(self.myDate)
            for holiday in oncelyHolidays:
                holidayId = holiday[1]
                holidayStart = holiday[2]
                holidayEnd = holiday[3]
                holidayType = holiday[0]
                if holidayStart[0] == self.myDate.year and holidayStart[1] == self.myDate.month and holidayStart[
                    2] == self.myDate.day:
                    myTime = datetime.time(holidayStart[3], holidayStart[4], tzinfo=self.myDate.tzinfo)
                elif holidayEnd[0] == self.myDate.year and holidayEnd[1] == self.myDate.month and holidayEnd[
                    2] == self.myDate.day:
                    myTime = datetime.time(holidayEnd[3], holidayEnd[4], tzinfo=self.myDate.tzinfo)
                else:
                    self.notify.error('holiday is not today %s' % holiday)
                self.timedEvents.append((myTime, holiday))

            multipleStartHolidays = base.cr.newsManager.getMultipleStartHolidaysForDate(self.myDate)
            for holiday in multipleStartHolidays:
                holidayId = holiday[1]
                holidayStart = holiday[2]
                holidayEnd = holiday[3]
                holidayType = holiday[0]
                if holidayStart[0] == self.myDate.year and holidayStart[1] == self.myDate.month and holidayStart[
                    2] == self.myDate.day:
                    myTime = datetime.time(holidayStart[3], holidayStart[4], tzinfo=self.myDate.tzinfo)
                elif holidayEnd[0] == self.myDate.year and holidayEnd[1] == self.myDate.month and holidayEnd[
                    2] == self.myDate.day:
                    myTime = datetime.time(holidayEnd[3], holidayEnd[4], tzinfo=self.myDate.tzinfo)
                else:
                    self.notify.error('holiday is not today %s' % holiday)
                self.timedEvents.append((myTime, holiday))

            relativelyHolidays = base.cr.newsManager.getRelativelyHolidaysForDate(self.myDate)
            for holiday in relativelyHolidays:
                holidayId = holiday[1]
                holidayStart = holiday[2]
                holidayEnd = holiday[3]
                holidayType = holiday[0]
                if holidayStart[0] == self.myDate.month and holidayStart[1] == self.myDate.day:
                    myTime = datetime.time(holidayStart[2], holidayStart[3], tzinfo=self.myDate.tzinfo)
                elif holidayEnd[0] == self.myDate.month and holidayEnd[1] == self.myDate.day:
                    myTime = datetime.time(holidayEnd[2], holidayEnd[3], tzinfo=self.myDate.tzinfo)
                else:
                    self.notify.error('holiday is not today %s' % holiday)
                self.timedEvents.append((myTime, holiday))

        def timedEventCompare(te1, te2):
            if te1[0] < te2[0]:
                return -1
            elif te1[0] == te2[0]:
                return 0
            else:
                return 1

        self.timedEvents.sort(key=cmp_to_key(timedEventCompare))
        for timedEvent in self.timedEvents:
            # Don't display holidays we don't want to in the calendar.
            if isinstance(timedEvent[1], tuple) and timedEvent[1][1] in ToontownGlobals.DONT_DISPLAY_HOLIDAY:
                continue
            if isinstance(timedEvent[1], tuple) and timedEvent[1][0] == NewsManager.YearlyHolidayType:
                self.addYearlyHolidayToScrollList(timedEvent[1])
            elif isinstance(timedEvent[1], tuple) and timedEvent[1][0] == NewsManager.OncelyHolidayType:
                self.addOncelyHolidayToScrollList(timedEvent[1])
            elif isinstance(timedEvent[1], tuple) and timedEvent[1][0] == NewsManager.OncelyMultipleStartHolidayType:
                self.addOncelyMultipleStartHolidayToScrollList(timedEvent[1])
            elif isinstance(timedEvent[1], tuple) and timedEvent[1][0] == NewsManager.RelativelyHolidayType:
                self.addRelativelyHolidayToScrollList(timedEvent[1])

    def addYearlyHolidayToScrollList(self, holiday):
        holidayId = holiday[1]
        holidayStart = holiday[2]
        holidayEnd = holiday[3]
        holidayType = holiday[0]
        holidayText = ''
        startTime = datetime.time(holidayStart[2], holidayStart[3], tzinfo=self.myDate.tzinfo)
        endTime = datetime.time(holidayEnd[2], holidayEnd[3], tzinfo=self.myDate.tzinfo)
        startDate = datetime.date(self.myDate.year, holidayStart[0], holidayStart[1])
        endDate = datetime.date(self.myDate.year, holidayEnd[0], holidayEnd[1])
        if endDate < startDate:
            endDate = datetime.date(endDate.year + 1, endDate.month, endDate.day)
        if holidayId in TTLocalizer.HolidayNamesInCalendar:
            holidayName = TTLocalizer.HolidayNamesInCalendar[holidayId][0]
            holidayDesc = TTLocalizer.HolidayNamesInCalendar[holidayId][1]
        else:
            holidayName = TTLocalizer.UnknownHoliday % holidayId
            holidayDesc = TTLocalizer.UnknownHoliday % holidayId
        if holidayStart[0] == holidayEnd[0] and holidayStart[1] == holidayEnd[1]:
            holidayText = myStrftime(startTime)
            holidayText += ' ' + holidayName
            holidayDesc += ' ' + TTLocalizer.CalendarEndsAt + myStrftime(endTime)
        elif self.myDate.month == holidayStart[0] and self.myDate.day == holidayStart[1]:
            holidayText = myStrftime(startTime)
            holidayText += ' ' + holidayName
            holidayDesc = holidayName + '. ' + holidayDesc
            holidayDesc += ' ' + TTLocalizer.CalendarEndsAt + endDate.strftime(TTLocalizer.HolidayFormat) + myStrftime(
                endTime)
        elif self.myDate.month == holidayEnd[0] and self.myDate.day == holidayEnd[1]:
            holidayText = myStrftime(endTime)
            holidayText += ' ' + TTLocalizer.CalendarEndDash + holidayName
            holidayDesc = TTLocalizer.CalendarEndOf + holidayName
            holidayDesc += '. ' + TTLocalizer.CalendarStartedOn + startDate.strftime(
                TTLocalizer.HolidayFormat) + myStrftime(startTime)
        else:
            self.notify.error('unhandled case')
        self.addTitleAndDescToScrollList(holidayText, holidayDesc)

    def addOncelyHolidayToScrollList(self, holiday):
        holidayId = holiday[1]
        holidayStart = holiday[2]
        holidayEnd = holiday[3]
        holidayType = holiday[0]
        holidayText = ''
        startTime = datetime.time(holidayStart[3], holidayStart[4], tzinfo=self.myDate.tzinfo)
        endTime = datetime.time(holidayEnd[3], holidayEnd[4], tzinfo=self.myDate.tzinfo)
        startDate = datetime.date(holidayStart[0], holidayStart[1], holidayStart[2])
        endDate = datetime.date(holidayStart[0], holidayEnd[1], holidayEnd[2])
        if endDate < startDate:
            endDate = datetime.date(endDate.year + 1, endDate.month, endDate.day)
        if holidayId in TTLocalizer.HolidayNamesInCalendar:
            holidayName = TTLocalizer.HolidayNamesInCalendar[holidayId][0]
            holidayDesc = TTLocalizer.HolidayNamesInCalendar[holidayId][1]
        else:
            holidayName = TTLocalizer.UnknownHoliday % holidayId
            holidayDesc = ''
        if holidayStart[1] == holidayEnd[1] and holidayStart[2] == holidayEnd[2]:
            holidayText = myStrftime(startTime)
            holidayText += ' ' + holidayName
            holidayDesc = holidayName + '. ' + holidayDesc
            holidayDesc += ' ' + TTLocalizer.CalendarEndsAt + myStrftime(endTime)
        elif self.myDate.year == holidayStart[0] and self.myDate.month == holidayStart[1] and self.myDate.day == \
            holidayStart[2]:
            holidayText = myStrftime(startTime)
            holidayText += ' ' + holidayName
            holidayDesc = holidayName + '. ' + holidayDesc
            holidayDesc += ' ' + TTLocalizer.CalendarEndsAt + endDate.strftime(TTLocalizer.HolidayFormat) + myStrftime(
                endTime)
        elif self.myDate.year == holidayEnd[0] and self.myDate.month == holidayEnd[1] and self.myDate.day == holidayEnd[
            2]:
            holidayText = myStrftime(endTime)
            holidayText += ' ' + TTLocalizer.CalendarEndDash + holidayName
            holidayDesc = TTLocalizer.CalendarEndOf + holidayName
            holidayDesc += '. ' + TTLocalizer.CalendarStartedOn + startDate.strftime(
                TTLocalizer.HolidayFormat) + myStrftime(startTime)
        else:
            self.notify.error('unhandled case')
        self.addTitleAndDescToScrollList(holidayText, holidayDesc)

    def addImmediateHolidayToScrollList(self, holidayId: int, holidayTime: float, **kwargs):
        """
        Adds a single-event holiday to the calendar.

        :param holidayId: The ID of the holiday.
        :param holidayTime: The time of the holiday. Akin to time.time().
        :param kwargs: Kwargs to parse with the holiday name or description.
        :return: None.
        """
        # Verify it's time for this event.
        holidayDateTime = datetime.datetime.fromtimestamp(holidayTime, tz=self.myDate.tzinfo)   # use the same tzinfo as our date (which should be set to ToontownTimeZone()
        if self.myDate.date() != holidayDateTime.date():
            return

        # Build the name and description of the event.
        if holidayId in TTLocalizer.HolidayNamesInCalendar:
            holidayName = TTLocalizer.HolidayNamesInCalendar[holidayId][0]
            holidayDesc = TTLocalizer.HolidayNamesInCalendar[holidayId][1]
            if 'name' in kwargs:
                holidayName = holidayName % kwargs['name']
            if 'desc' in kwargs:
                holidayDesc = holidayDesc % kwargs['desc']
        else:
            holidayName = TTLocalizer.UnknownHoliday % holidayId
            holidayDesc = ''

        # Format the name and description, add it in.
        holidayText = f"{myStrftime(holidayDateTime)} {holidayName}"
        holidayDesc = f"{holidayName}. {holidayDesc}"
        self.addTitleAndDescToScrollList(holidayText, holidayDesc)

    def addOncelyMultipleStartHolidayToScrollList(self, holiday):
        self.addOncelyHolidayToScrollList(holiday)

    def addRelativelyHolidayToScrollList(self, holiday):
        holidayId = holiday[1]
        holidayStart = holiday[2]
        holidayEnd = holiday[3]
        holidayType = holiday[0]
        holidayText = ''
        startTime = datetime.time(holidayStart[2], holidayStart[3], tzinfo=self.myDate.tzinfo)
        endTime = datetime.time(holidayEnd[2], holidayEnd[3], tzinfo=self.myDate.tzinfo)
        startDate = datetime.date(self.myDate.year, holidayStart[0], holidayStart[1])
        endDate = datetime.date(self.myDate.year, holidayEnd[0], holidayEnd[1])
        if endDate < startDate:
            endDate.year += 1
        if holidayId in TTLocalizer.HolidayNamesInCalendar:
            holidayName = TTLocalizer.HolidayNamesInCalendar[holidayId][0]
            holidayDesc = TTLocalizer.HolidayNamesInCalendar[holidayId][1]
        else:
            holidayName = TTLocalizer.UnknownHoliday % holidayId
            holidayDesc = ''
        if holidayStart[0] == holidayEnd[0] and holidayStart[1] == holidayEnd[1]:
            holidayText = myStrftime(startTime)
            holidayText += ' ' + holidayName
            holidayDesc += ' ' + TTLocalizer.CalendarEndsAt + myStrftime(endTime)
        elif self.myDate.month == holidayStart[0] and self.myDate.day == holidayStart[1]:
            holidayText = myStrftime(startTime)
            holidayText += ' ' + holidayName
            holidayDesc = holidayName + '. ' + holidayDesc
            holidayDesc += ' ' + TTLocalizer.CalendarEndsAt + endDate.strftime(TTLocalizer.HolidayFormat) + myStrftime(
                endTime)
        elif self.myDate.month == holidayEnd[0] and self.myDate.day == holidayEnd[1]:
            holidayText = myStrftime(endTime)
            holidayText += ' ' + TTLocalizer.CalendarEndDash + holidayName
            holidayDesc = TTLocalizer.CalendarEndOf + holidayName
            holidayDesc += '. ' + TTLocalizer.CalendarStartedOn + startDate.strftime(
                TTLocalizer.HolidayFormat) + myStrftime(startTime)
        else:
            self.notify.error('unhandled case')
        self.addTitleAndDescToScrollList(holidayText, holidayDesc)

    def addTitleAndDescToScrollList(self, title, desc):
        textSize = self.ScrollListTextSize
        descTextSize = 0.05
        newItem = DirectButton(relief=None, text=title, text_scale=textSize, text_align=TextNode.ALeft,
                               rolloverSound=None, clickSound=None, pressEffect=0, command=self.__clickedOnScrollItem)
        scrollItemHeight = newItem.getHeight()
        descUnderItemZAdjust = scrollItemHeight * descTextSize / textSize
        descUnderItemZAdjust = max(0.0534, descUnderItemZAdjust)
        descUnderItemZAdjust = -descUnderItemZAdjust
        descZAdjust = descUnderItemZAdjust
        newItem.description = DirectLabel(parent=newItem, pos=(0.115, 0, descZAdjust), text='', text_wordwrap=15,
                                          pad=(0.02, 0.02), text_scale=descTextSize, text_align=TextNode.ACenter,
                                          textMayChange=0)
        newItem.description.checkedHeight = False
        newItem.description.setBin('sorted-gui-popup', GuiBinGlobals.HoverTextBin)
        newItem.description.hide()
        newItem.bind(DGG.ENTER, self.enteredTextItem, extraArgs=[newItem, desc, descUnderItemZAdjust])
        newItem.bind(DGG.EXIT, self.exitedTextItem, extraArgs=[newItem])
        self.scrollList.addItem(newItem)
        return

    def exitedTextItem(self, newItem, mousepos):
        newItem.description.hide()

    def enteredTextItem(self, newItem, descText, descUnderItemZAdjust, mousePos):
        if not newItem.description.checkedHeight:
            newItem.description.checkedHeight = True
            newItem.description['text'] = descText
            bounds = newItem.description.getBounds()
            descHeight = newItem.description.getHeight()
            scrollItemHeight = newItem.getHeight()
            descOverItemZAdjust = descHeight - scrollItemHeight / 2.0
            descZPos = self.getPos(aspect2d)[2] + descUnderItemZAdjust - descHeight
            if descZPos < -1.0:
                newItem.description.setZ(descOverItemZAdjust)
            descWidth = newItem.description.getWidth()
            brightFrame = loader.loadModel('phase_4/models/parties/tt_m_gui_sbk_calendar_popUp_bg')
            newItem.description['geom'] = brightFrame
            newItem.description['geom_scale'] = (descWidth, 1, descHeight)
            descGeomZ = (bounds[2] - bounds[3]) / 2.0
            descGeomZ += bounds[3]
            newItem.description['geom_pos'] = (0, 0, descGeomZ)
        newItem.description.show()

    def __clickedOnScrollItem(self):
        self.__clickedOnDay()

    def __clickedOnDay(self):
        acceptClick = True
        if self.onlyFutureDaysClickable:
            curServerDate = base.cr.toontownTimeManager.getCurServerDateTime()
            if self.myDate.date() < curServerDate.date():
                acceptClick = False
        if not acceptClick:
            return
        if self.dayClickCallback:
            self.dayClickCallback(self)
        self.notify.debug('we got clicked on %s' % self.myDate.date())
        messenger.send('clickedOnDay', [self.myDate.date()])

    def updateSelected(self, selected):
        multiplier = 1.1
        if selected:
            self.selectedFrame.show()
            self.setScale(multiplier)
            self.setPos(-0.01, 0, 0.01)
            grandParent = self.origParent.getParent()
            self.origParent.reparentTo(grandParent)
        else:
            self.selectedFrame.hide()
            self.setScale(1.0)
            self.setPos(0, 0, 0)

    def changeDate(self, startDate, myDate):
        self.startDate = startDate
        self.myDate = myDate
        self.scrollList.removeAndDestroyAllItems()
        self.update()

    def update(self):
        self.numberWidget['text'] = str(self.myDate.day)
        self.adjustForMonth()
        self.addWeeklyHolidays()
        self.addDynamicEvents()
        self.collectTimedEvents()
        self.updateArrowButtons()

    def changeFilter(self, filter):
        oldFilter = self.filter
        self.filter = filter
        if self.filter != oldFilter:
            self.scrollList.removeAndDestroyAllItems()
            self.update()
