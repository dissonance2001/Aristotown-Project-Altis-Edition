from direct.gui.DirectGui import DirectFrame, DirectWaitBar, DirectLabel, DGG
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

from toontown.inventory.enums.ItemEnums import BoosterItemType
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownIntervals
from toontown.toon import ToonExperience
from direct.interval.IntervalGlobal import *

from toontown.toonbase.ToontownGlobals import DepartmentToBooster


class DepartmentExperienceBar(DirectFrame):
    gLabelPos = (0.0, 0.0, 0.125)
    gLabelUpPos = (0.0, 0.0, 0.175)
    gLabelScale = (0.075, 1, 0.075)

    def __init__(self, exp, level, department, avdna):
        DirectFrame.__init__(self, relief=None, sortOrder=50)
        self.av = None
        self.style = avdna
        if self.style.type == 't':
            self.isToon = 1
        else:
            self.isToon = 0

        self.exp = exp
        self.level = level
        self.department = department
        self.maxExp = ToonExperience.ToonExperience().getLevelMaxExp(self.level)
        self.departmentExpBar = None
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
        if self.isToon:
            self.barGeom = loader.loadModel('phase_3.5/models/gui/exp_bar')
            self.color = self.style.getHeadColor()
            self.bgBar = DirectFrame(relief=None, geom=self.barGeom, pos=(0.0, 0, -.95), geom_scale=(0.3, 0.25, 0.1),
                                     geom_color=self.color, sortOrder=500)
            self.departmentExpBar = DirectWaitBar(parent=self.bgBar, guiId='departmentExpBar', pos=(0.0, 0, 0),
                                                  relief=DGG.SUNKEN, frameSize=(-2.0, 2.0, -0.1, 0.1),
                                                  borderWidth=(0.01, 0.01), scale=0.25, range=self.maxExp,
                                                  sortOrder=501, frameColor=(0.5, 0.5, 0.5, 0.5),
                                                  barColor=(0.0, 1.0, 0.0, 0.5), text='', text_scale=0.2,
                                                  text_fg=(1, 1, 1, 1), text_align=TextNode.ACenter,
                                                  text_pos=(0, -0.05))
            self.departmentExpBar['value'] = self.exp
            self.bgBar.hide()

            relevantBooster = DepartmentToBooster[self.department]
            boostPercent = base.localAvatar.applyBoosters([BoosterItemType.Exp_Dept_Global, relevantBooster], 0)

            if boostPercent:
                self.departmentExpBar['text'] = str(self.exp) + '/' + str(
                    self.maxExp) + TTLocalizer.DepartmentBoost % int(boostPercent * 100)
            else:
                self.departmentExpBar['text'] = str(self.exp) + '/' + str(self.maxExp)
            if self.level == ToontownGlobals.MaxDepartmentLevel[self.department]:
                self.departmentExpBar['range'] = 1
                self.departmentExpBar['value'] = 1
                self.departmentExpBar['text'] = TTLocalizer.ExpBarMax
            self.levelLabel = OnscreenText(parent=self.bgBar,
                                           text=TTLocalizer.DepartmentExpBarLevel[self.department] + str(
                                               self.level + 1), pos=(0.0, 0.05), scale=0.05,
                                           font=ToontownGlobals.getBuildingNametagFont(), fg=(1, 1, 1, 1))
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
            self.ignore(self.av.uniqueName('departmentExpChange'))

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

        if self.departmentExpBar:
            self.departmentExpBar.destroy()

        if self.levelLabel:
            self.levelLabel.destroy()

        if self.gainedLabel:
            self.gainedLabel.destroy()

        DirectFrame.destroy(self)

    def updateBar(self, exp=[0], level=[0]):
        exp = exp[self.department]
        level = level[self.department]

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
        if self.level >= ToontownGlobals.MaxDepartmentLevel[self.department] and self.level == currLevel:
            animation = 0

        if (expDiff <= 0 or not animation) and not (self.expSeq and self.expSeq.isPlaying()):
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
        self.levelLabel['text'] = TTLocalizer.DepartmentExpBarLevel[self.department] + str(self.level + 1)

        name = self.av.uniqueName('departmentLevelBarBoing') + '-' + str(self.this)

        if self.level >= ToontownGlobals.MaxDepartmentLevel[self.department]:
            self.departmentExpBar['range'] = 1
            self.departmentExpBar['value'] = 1
            self.departmentExpBar['text'] = TTLocalizer.ExpBarMax
        else:
            self.departmentExpBar['range'] = self.maxExp
            self.departmentExpBar['value'] = self.exp

            relevantBooster = DepartmentToBooster[self.department]
            boostPercent = base.localAvatar.applyBoosters([BoosterItemType.Exp_Dept_Global, relevantBooster], 0)

            if boostPercent:
                self.departmentExpBar['text'] = str(self.exp) + '/' + str(
                    self.maxExp) + TTLocalizer.DepartmentBoost % int(boostPercent * 100)
            else:
                self.departmentExpBar['text'] = str(self.exp) + '/' + str(self.maxExp)
        if animation:
            ToontownIntervals.start(ToontownIntervals.getPulseLargerIval(self.bgBar, name))

    def setCurrentGained(self, num):
        self.currentGained = num

    def start(self):
        if self.isToon:
            self.show()

            if self.visToggle:
                self.visToggle.show()

            if self.av:
                self.accept(self.av.uniqueName('departmentExpChange'), self.updateBar)

    def stop(self):
        if self.isToon:
            if self.bgBar:
                self.bgBar.hide()
            if self.levelLabel:
                self.levelLabel.hide()
            if self.visToggle:
                self.visToggle.hide()
            if self.av:
                self.ignore(self.av.uniqueName('departmentExpChange'))

    def setAvatar(self, av):
        if self.av:
            self.ignore(self.av.uniqueName('departmentExpChange'))

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
        if self.level >= ToontownGlobals.MaxDepartmentLevel[self.department] and not forceShow:
            self.hide()
            return

        if self.bgBar:
            self.bgBar.show()

        if self.levelLabel:
            self.levelLabel.show()

        self.__obscured = 0
