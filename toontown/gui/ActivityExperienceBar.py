from direct.gui.DirectGui import DirectFrame, DirectWaitBar, DirectLabel, DGG
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownIntervals
from toontown.toon import ToonExperience
from direct.interval.IntervalGlobal import *


class ActivityExperienceBar(DirectFrame):
    gLabelPos = (0.0, 0.0, 0.125)
    gLabelUpPos = (0.0, 0.0, 0.175)
    gLabelScale = (0.075, 1, 0.075)

    def __init__(self, exp, level, activity, avdna):
        DirectFrame.__init__(self, relief=None, sortOrder=50)
        self.av = None
        self.style = avdna

        self.exp = exp
        self.level = level
        self.activity = activity
        self.maxExp = ToonExperience.ToonExperience().getLevelMaxExp(self.level)
        self.activityExpBar = None
        self.__obscured = 0
        self.bgBar = None
        self.levelLabel = None
        self.gainedLabel = None
        self.visToggle = None
        self.levelUpSfx = loader.loadSfx('phase_3.5/audio/sfx/AV_levelup.ogg')
        self.expSeq = None
        self.currentGained = 0
        self.load()

    def load(self):
        self.barGeom = loader.loadModel('phase_3.5/models/gui/exp_bar')
        self.color = self.style.getHeadColor()
        self.bgBar = DirectFrame(relief=None, geom=self.barGeom, pos=(0.0, 0, -.95), geom_scale=(0.3, 0.25, 0.1),
                                 geom_color=self.color, sortOrder=500)
        self.activityExpBar = DirectWaitBar(parent=self.bgBar, guiId='activityExpBar', pos=(0.0, 0, 0),
                                            relief=DGG.SUNKEN, frameSize=(-2.0, 2.0, -0.1, 0.1),
                                            borderWidth=(0.01, 0.01), scale=0.25, range=self.maxExp, sortOrder=501,
                                            frameColor=(0.5, 0.5, 0.5, 0.5), barColor=(0.0, 1.0, 0.0, 0.5), text='',
                                            text_scale=0.2, text_fg=(1, 1, 1, 1), text_align=TextNode.ACenter,
                                            text_pos=(0, -0.05))
        self.activityExpBar['value'] = self.exp
        self.bgBar.hide()

        self.activityExpBar['text'] = str(self.exp) + '/' + str(self.maxExp)
        if self.level == ToontownGlobals.MaxActivityLevel[self.activity]:
            self.activityExpBar['range'] = 1
            self.activityExpBar['value'] = 1
            self.activityExpBar['text'] = TTLocalizer.ExpBarMax
        self.levelLabel = OnscreenText(parent=self.bgBar,
                                       text=TTLocalizer.ActivityExpBarLevel[self.activity] + str(self.level + 1),
                                       pos=(0.0, 0.05), scale=0.05, font=ToontownGlobals.getBuildingNametagFont(),
                                       fg=(1, 1, 1, 1))
        self.levelLabel.hide()
        self.gainedLabel = DirectLabel(parent=self.bgBar, relief=None, text='+0', pos=self.gLabelPos,
                                       scale=self.gLabelScale, text_font=ToontownGlobals.getInterfaceFont(),
                                       text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1), sortOrder=1)
        self.gainedLabel.setTransparency(1)
        self.gainedLabel.hide()
        if not settings.get('experienceBarMode'):
            self.hide()

    def destroy(self):
        if self.av:
            self.ignore(self.av.uniqueName('activityExpChange'))
            self.ignore('boostsUpdated')

        del self.av
        del self.exp
        del self.maxExp
        del self.currentGained

        if self.expSeq:
            self.expSeq.pause()
            self.expSeq = None

        if self.bgBar:
            self.bgBar.destroy()
            del self.bgBar

        if self.activityExpBar:
            self.activityExpBar.destroy()

        if self.levelLabel:
            self.levelLabel.destroy()

        if self.gainedLabel:
            self.gainedLabel.destroy()

        DirectFrame.destroy(self)

    def updateBar(self, exp=[0], level=[0]):
        exp = exp[self.activity]
        level = level[self.activity]

        experienceInstance = ToonExperience.ToonExperience()

        currExp = self.exp
        if exp:
            self.exp = exp

        currLevel = self.level
        if level:
            self.level = level

        self.maxExp = experienceInstance.getLevelMaxExp(self.level)
        currMaxExp = experienceInstance.getLevelMaxExp(currLevel)

        expDiff = 0
        if self.level != currLevel:
            expDiff += (currMaxExp - currExp)
            expDiff += self.exp
            if self.level - currLevel > 1:
                for lvl in range(currLevel + 1, self.level):
                    expDiff += experienceInstance.getLevelMaxExp(lvl)
        else:
            expDiff = self.exp - currExp

        if not self.currentGained:
            self.currentGained = expDiff
        else:
            self.currentGained += expDiff
            self.gainedLabel.setText('+' + str(self.currentGained))
            return

        animation = 1
        if self.level >= ToontownGlobals.MaxActivityLevel[self.activity] and self.level == currLevel:
            animation = 0

        if (self.currentGained <= 0 or not animation) and not (self.expSeq and self.expSeq.isPlaying()):
            self.updateBarValues(animation=0)
            return

        self.expSeq = Sequence(
            Func(self.gainedLabel.setText, '+' + str(expDiff)),
            Func(self.gainedLabel.setPos, self.gLabelPos),
            Func(self.gainedLabel.setScale, self.gLabelScale),
            Func(self.gainedLabel.show),
            LerpColorScaleInterval(self.gainedLabel, 0.5, (1, 1, 1, 1), (1, 1, 1, 0)),
            Wait(1.5),
            LerpPosInterval(self.gainedLabel, 0.2, self.gLabelUpPos, blendType='easeInOut'),
            ParallelEndTogether(
                LerpPosInterval(self.gainedLabel, 0.75, (0, 0, 0), blendType='easeIn'),
                LerpScaleInterval(self.gainedLabel, 0.75, 0.01, blendType='easeIn'),
                Func(self.updateBarValues)
            ),
            Func(self.gainedLabel.hide),
            Func(self.setCurrentGained, 0)
        )
        if currLevel != self.level and (((self.level + 1) % 10) == 0):
            self.expSeq.append(SoundInterval(self.levelUpSfx))
        self.expSeq.start()

    def updateBarValues(self, animation=1):
        self.levelLabel['text'] = TTLocalizer.ActivityExpBarLevel[self.activity] + str(self.level + 1)

        name = self.av.uniqueName('activityLevelBarBoing') + '-' + str(self.this)

        if self.level >= ToontownGlobals.MaxActivityLevel[self.activity]:
            self.activityExpBar['range'] = 1
            self.activityExpBar['value'] = 1
            self.activityExpBar['text'] = TTLocalizer.ExpBarMax
        else:
            self.activityExpBar['range'] = self.maxExp
            self.activityExpBar['value'] = self.exp

            if boostPercent:
                self.activityExpBar['text'] = str(self.exp) + '/' + str(
                    self.maxExp) + TTLocalizer.ActivituesdayPostfix % int(boostPercent * 100)
            else:
                self.activityExpBar['text'] = str(self.exp) + '/' + str(self.maxExp)
        if animation:
            ToontownIntervals.start(ToontownIntervals.getPulseLargerIval(self.bgBar, name))

    def setCurrentGained(self, num):
        self.currentGained = num

    def start(self):
        self.show()

        if self.visToggle:
            self.visToggle.show()

        if self.av:
            self.accept(self.av.uniqueName('activityExpChange'), self.updateBar)
            # self.accept('boostsUpdated', self.updateBar)

    def stop(self):
        if self.bgBar:
            self.bgBar.hide()
        if self.levelLabel:
            self.levelLabel.hide()
        if self.visToggle:
            self.visToggle.hide()
        if self.av:
            self.ignore(self.av.uniqueName('activityExpChange'))
            # self.ignore('boostsUpdated')

    def setAvatar(self, av):
        if self.av:
            self.ignore(self.av.uniqueName('activityExpChange'))
            # self.ignore('boostsUpdated')

        self.av = av

    def toggleVis(self):
        if self.__obscured:
            self.show()
        else:
            self.hide()

    def hide(self):
        if self.levelLabel:
            self.levelLabel.hide()

        if self.bgBar:
            self.bgBar.hide()

        self.__obscured = 1

    def show(self, forceShow=False):
        if self.level >= ToontownGlobals.MaxActivityLevel[self.activity] and not forceShow:
            self.hide()
            return

        if self.bgBar:
            self.bgBar.show()

        if self.levelLabel:
            self.levelLabel.show()

        self.__obscured = 0
