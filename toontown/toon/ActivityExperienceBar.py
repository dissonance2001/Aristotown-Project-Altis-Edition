from panda3d.core import TextNode
from direct.gui.DirectGui import DirectFrame, DirectWaitBar, DGG
from direct.gui.OnscreenText import OnscreenText
from direct.interval.IntervalGlobal import Sequence, LerpScaleInterval
from toontown.toon import ActivityExperience
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from direct.task.TaskManagerGlobal import taskMgr


class ActivityExperienceBar(DirectFrame):
    def __init__(self, exp, levels, style):
        DirectFrame.__init__(self, relief=None, sortOrder=50)
        self.av = None
        self.expArray = self._fixArray(exp)
        self.levelArray = self._fixArray(levels)
        self.style = style
        self.activity = None
        self.activityActive = False
        self.bgBar = None
        self.expBar = None
        self.levelLabel = None
        self._deltaLabel = None
        self.activityExp = ActivityExperience.ActivityExperience()
        self._pulseScale = None
        self.levelUpSfx = loader.loadSfx('phase_3.5/audio/sfx/AV_levelup.ogg')
        self.load()

    def _fixArray(self, values):
        values = list(values or [])
        while len(values) < ToontownGlobals.TOTAL_ACTIVITIES:
            values.append(0)
        return values[:ToontownGlobals.TOTAL_ACTIVITIES]

    def load(self):
        self.barGeom = loader.loadModel('phase_3.5/models/gui/exp_bar')
        self.color = self.style.getHeadColor() if self.style else (1, 1, 1, 1)
        self.bgBar = DirectFrame(
            relief=None,
            geom=self.barGeom,
            pos=(0.0, 0.0, -0.95),
            geom_scale=(0.3, 0.25, 0.1),
            geom_color=self.color
        )
        self.expBar = DirectWaitBar(
            parent=self.bgBar,
            guiId='activityExpBar',
            pos=(0.0, 0.0, 0.0),
            relief=DGG.SUNKEN,
            frameSize=(-2.0, 2.0, -0.1, 0.1),
            borderWidth=(0.01, 0.01),
            scale=0.25,
            range=1,
            sortOrder=50,
            frameColor=(0.5, 0.5, 0.5, 0.5),
            barColor=(0.0, 1.0, 0.0, 0.5),
            text='0/1',
            text_scale=0.2,
            text_fg=(1, 1, 1, 1),
            text_align=TextNode.ACenter,
            text_pos=(0, -0.05)
        )
        self.levelLabel = OnscreenText(
            parent=self.bgBar,
            text='',
            pos=(0.0, 0.05),
            scale=0.05,
            font=ToontownGlobals.getBuildingNametagFont(),
            fg=(1, 1, 1, 1)
        )
        self._pulseScale = self.bgBar.getScale()
        self.hide()

    def updateBar(self, expArray=None, levelArray=None):
        if expArray is not None:
            self.expArray = self._fixArray(expArray)
        if levelArray is not None:
            self.levelArray = self._fixArray(levelArray)
        if self.activity is None or not self.activityActive:
            return
        activity = self.activity
        level = self.levelArray[activity]
        exp = self.expArray[activity]
        maxLevel = ToontownGlobals.MaxActivityLevel[activity]
        if level >= maxLevel:
            self.hide()
            return
        maxExp = self.activityExp.getLevelMaxExp(level)
        self.expBar['range'] = maxExp
        self.expBar['value'] = min(exp, maxExp)
        self.expBar['text'] = '%d/%d' % (exp, maxExp)
        self.levelLabel['text'] = '%s%d' % (TTLocalizer.ActivityExpBarLevel[activity], level + 1)
        self.show()
        if self._pulseScale is not None:
            Sequence(
                LerpScaleInterval(self.bgBar, 0.1, self._pulseScale * 1.5, blendType='easeOut'),
                LerpScaleInterval(self.bgBar, 0.1, self._pulseScale, blendType='easeIn'),
                name=self.uniqueName('activityXpPulse')
            ).start()

    def setActivity(self, activity, show=True):
        activity = int(activity)
        if activity < 0 or activity >= ToontownGlobals.TOTAL_ACTIVITIES:
            return False
        level = self.levelArray[activity]
        if level >= ToontownGlobals.MaxActivityLevel[activity]:
            self.activity = None
            self.activityActive = False
            self.hide()
            return False
        self.activity = activity
        self.activityActive = bool(show)
        self.updateBar()
        if not show:
            self.hide()
        return True

    def _handleExpChange(self, expArray):
        oldExp = list(self.expArray)
        self.expArray = self._fixArray(expArray)
        if self.activity is None or not self.activityActive:
            return
        self.updateBar()
        if oldExp != self.expArray:
            self._showDelta(oldExp, self.expArray)

    def _handleLevelChange(self, levelArray):
        oldLevels = list(self.levelArray)
        self.levelArray = self._fixArray(levelArray)
        if self.activity is None or not self.activityActive:
            return
        self.updateBar()
        newLevel = self.levelArray[self.activity]
        if newLevel > oldLevels[self.activity] and newLevel in ToontownGlobals.ActivityHPLevels[self.activity]:
            base.playSfx(self.levelUpSfx)

    def _showDelta(self, oldExp, newExp):
        if self.activity is None or not self.activityActive:
            return
        oldValue = oldExp[self.activity]
        newValue = newExp[self.activity]
        delta = newValue - oldValue
        if delta < 0:
            delta = newValue
        if delta <= 0:
            return
        if self._deltaLabel is None:
            self._deltaLabel = OnscreenText(
                parent=self.bgBar,
                text='',
                pos=(0.0, -0.25),
                scale=0.045,
                align=TextNode.ACenter,
                fg=(1, 1, 1, 1)
            )
        self._deltaLabel['text'] = '+%d XP' % delta
        self._deltaLabel.show()
        self._deltaLabel.clearColorScale()

    def start(self):
        if not self.av:
            return
        self.accept(self.av.uniqueName('activityExpChange'), self._handleExpChange)
        self.accept(self.av.uniqueName('activityLevelChange'), self._handleLevelChange)

    def stop(self):
        if self.av:
            self.ignore(self.av.uniqueName('activityExpChange'))
            self.ignore(self.av.uniqueName('activityLevelChange'))
        self.activity = None
        self.activityActive = False
        self.hide()

    def setAvatar(self, av):
        if self.av:
            self.ignore(self.av.uniqueName('activityExpChange'))
            self.ignore(self.av.uniqueName('activityLevelChange'))
        self.av = av
        self.expArray = self._fixArray(getattr(av, 'getActivityExp', lambda: self.expArray)())
        self.levelArray = self._fixArray(getattr(av, 'getActivityLevels', lambda: self.levelArray)())

    def hide(self):
        if self.bgBar:
            self.bgBar.hide()
        if self.levelLabel:
            self.levelLabel.hide()
        if self._deltaLabel is not None:
            self._deltaLabel.hide()

    def show(self):
        if self.activity is None:
            return
        level = self.levelArray[self.activity]
        if level >= ToontownGlobals.MaxActivityLevel[self.activity]:
            self.hide()
            return
        if self.bgBar:
            self.bgBar.show()
        if self.levelLabel:
            self.levelLabel.show()

    def destroy(self):
        if self.av:
            self.ignore(self.av.uniqueName('activityExpChange'))
            self.ignore(self.av.uniqueName('activityLevelChange'))
        if self._deltaLabel is not None:
            self._deltaLabel.destroy()
            self._deltaLabel = None
        if self.expBar:
            self.expBar.destroy()
            self.expBar = None
        if self.levelLabel:
            self.levelLabel.destroy()
            self.levelLabel = None
        if self.bgBar:
            self.bgBar.destroy()
            self.bgBar = None
        DirectFrame.destroy(self)
