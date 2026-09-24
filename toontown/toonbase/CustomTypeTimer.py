from .ToontownTimer import *
from toontown.toonbase import ToontownGlobals

TIMER_TYPE_DEFAULT = -1
TIMER_TYPE_UNITE = 0
TIMER_TYPE_OVERCLOCKED = 1

# For textScale and textPos:
# index 0 is 1 char time remaining, index 1 is 2 char, index 2 is 3 char. Example: 150s uses index 2.
TimerData = {
    TIMER_TYPE_DEFAULT: {'imagePath': None,
                         'imagePos': (0, 0, 0),
                         'imageScale': 1.0,
                         'textScale': [0.34, 0.27, 0.2],
                         'textPos': [(-0.025, -0.125), (-0.025, -0.1), (-0.01, -0.08)],
                         'fontColor': (0, 0, 0, 1),
                         'font': ToontownGlobals.getInterfaceFont(),
                         'textShadow': (0, 0, 0, 0),
                         'runningOutColor': Vec4(1, 0, 0, 1),
                         'marginDist': 0.0,
                         'extendsVertical': 0,
                         'screenIndex': 0,
                         },
    TIMER_TYPE_UNITE: {'imagePath': 'phase_3.5/maps/battlegui/unite_timer.png',
                       'imagePos': (-0.01, 0, 0.025),
                       'imageScale': 0.4,
                       'textScale': [0.32, 0.25, 0.18],
                       'textPos': [(-0.015, -0.11), (-0.015, -0.09), (-0.01, -0.0675)],
                       'marginDist': 0.13,
                       'extendsVertical': 1,
                       'screenIndex': 10,
                       },
    TIMER_TYPE_OVERCLOCKED: {'imagePath': ['phase_3.5/models/gui/directives_gui', '**/overclocked'],
                             'imagePos': (-0.01, 0, 0.1),
                             'textPos': [(-0.025, -0.115), (-0.025, -0.09), (-0.01, -0.07)],
                             'fontColor': (1, 1, 1, 1),
                             'font': ToontownGlobals.getSuitFont(),
                             'textShadow': (0, 0, 0, 1),
                             'runningOutColor': Vec4(0.65, 0, 0, 1)},
}


class CustomTypeTimer(ToontownTimer):
    def __init__(self, needDialog=None, useImage=True, highlightNearEnd=True, timerType=TIMER_TYPE_DEFAULT):
        self.timerType = timerType
        self.timerInfo = TimerData[timerType]
        ToontownTimer.__init__(self, needDialog, useImage, highlightNearEnd)
        self.initialiseoptions(CustomTypeTimer)
        self['image_pos'] = self.getInfo('imagePos')
        self['image_scale'] = self.getInfo('imageScale')
        self.setFontColor(self.getInfo('fontColor'))
        self['text_font'] = self.getInfo('font')
        self['text_shadow'] = self.getInfo('textShadow')
        self.setTransparency(1)
        self.popTimer = None
        self.textScaleData = self.getInfo('textScale')
        self.textPosData = self.getInfo('textPos')
        self.runningOutColor = self.getInfo('runningOutColor')

    def getImage(self):
        customPath = self.getInfo('imagePath')
        if customPath:
            if type(customPath) in (list, tuple):
                model = loader.loadModel(customPath[0])
                image = model.find(customPath[1])
                model.removeNode()
            else:
                image = loader.loadTexture(customPath)
            return image

        if ToontownTimer.ClockImage is None:
            model = loader.loadModel('phase_3.5/models/gui/clock_gui')
            ToontownTimer.ClockImage = model.find('**/alarm_clock')
            model.removeNode()

        return CustomTypeTimer.ClockImage

    def setTime(self, time):
        time = bound(time, 0, 999)
        if time == self.currentTime:
            return
        self.currentTime = time
        timeStr = str(time)
        timeStrLen = len(timeStr)
        if timeStrLen == 1:
            if time <= 5 and self.highlightNearEnd:
                self.setTimeStr(timeStr, self.textScaleData[0], self.textPosData[0], self.runningOutColor)
            else:
                self.setTimeStr(timeStr, self.textScaleData[0], self.textPosData[0])
        elif timeStrLen == 2:
            self.setTimeStr(timeStr, self.textScaleData[1], self.textPosData[1])
        elif timeStrLen == 3:
            self.setTimeStr(timeStr, self.textScaleData[2], self.textPosData[2])

    def getInfo(self, keyword):
        return self.timerInfo.get(keyword, TimerData[TIMER_TYPE_DEFAULT][keyword])

    def posInTopLeftCorner(self):
        self.setScreenCorner(ScreenCorner.TOP_LEFT)
        self.managedPosOffset = (0, 0, -self.getInfo('marginDist'))
        self.startPositionManagement()
        self.setPos(self.managedPosOffset)

    def getScreenIndex(self):
        return self.getInfo('screenIndex')

    def extendsVertical(self):
        return self.getInfo('extendsVertical')
