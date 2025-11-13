import string
from pandac.PandaModules import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.toonbase.ToontownGlobals import *
from toontown.battle.SuitBattleGlobals import *
from direct.interval.IntervalGlobal import *
from direct.directnotify import DirectNotifyGlobal
from direct.gui import OnscreenText
from toontown.battle import BattleBase

class PlayByPlayText(OnscreenText.OnscreenText):
    notify = DirectNotifyGlobal.directNotify.newCategory('PlayByPlayText')

    def __init__(self):
        OnscreenText.OnscreenText.__init__(self, mayChange=1, pos=(0.0, 0.75), scale=TTLocalizer.PBPTonscreenText, fg=(1, 1, 1, 1), font=getSignFont(), wordwrap=None)

    def getShowInterval(self, text, duration):
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(1, 0, 0, 1.0)), Func(self.hide), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, .75)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(duration),
                        LerpColorScaleInterval(self, .25, Vec4(0, 0, 0, 0)), Func(self.hide))

    def getShowIntervalOvercharged(self, text, duration):
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(0.988, 0., 1.0, 1.0)), Func(self.hide), Wait(duration * 0.1), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, .75)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(duration),
                        LerpColorScaleInterval(self, .25, Vec4(0, 0, 0, 0)), Func(self.hide))

    def getShowIntervalCheat(self, text, duration):
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(0.466, 0.474, 1.0, 1.0)), Func(self.hide), Wait(duration * 0.1), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, .75)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(duration),
                        LerpColorScaleInterval(self, .25, Vec4(0, 0, 0, 0)), Func(self.hide))

    def getShowIntervalCheatRed(self, text, duration):
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(1, 0, 0, 1.0)), Func(self.hide), Wait(duration * 0.1), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, .75)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(duration),
                        LerpColorScaleInterval(self, .25, Vec4(0, 0, 0, 0)), Func(self.hide))

    def getShowIntervalCheatOvercharged(self, text, duration):
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(0.988, 0., 1.0, 1.0)), Func(self.hide), Wait(duration * 0.1), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, .75)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(duration),
                        LerpColorScaleInterval(self, .25, Vec4(0, 0, 0, 0)), Func(self.hide))

    def getShowIntervalDesc(self, text, duration):
        return Sequence(Wait(0.5), LerpColorScaleInterval(self, 0, Vec4(0.847, 0.784, 0.992, 1.0)), Func(self.hide), Func(self.setWordwrap, None), Func(self.setPos, 0.0, 0.6625),
                        Func(self.setScale, 0.09), Wait(duration * 0.1),
                        Func(self.setText, text),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, 0.6625)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(duration - .5),
                        LerpColorScaleInterval(self, .25, Vec4(0, 0, 0, 0)), Func(self.hide))

    def getToonsDiedInterval(self, textList, duration):
        track = Sequence(Func(self.hide), Wait(duration * 0.3))
        waitGap = 0.6 / len(textList) * duration
        for text in textList:
            newList = [Func(self.setText, text),
             Func(self.show),
             Wait(waitGap),
             Func(self.hide)]
            track += newList

        track.append(Wait(duration * 0.1))
        return track