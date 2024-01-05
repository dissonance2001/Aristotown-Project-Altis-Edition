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
        OnscreenText.OnscreenText.__init__(self, mayChange=1, pos=(0.0, 0.75), scale=TTLocalizer.PBPTonscreenText, fg=(1, 0, 0, 1), font=getSignFont(), wordwrap=13)

    def getShowInterval(self, text, duration):
        return Sequence(Func(self.hide), Func(self.setFg, (1., 0., 0., 1.0)),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, 0.42)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.2, 1.2)),
                                 self.posInterval(0.25, (0, 0, -0.075))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(2),
                        Parallel(self.scaleInterval(0.25, (1.3, 1.3, 1.3)),
                                 self.posInterval(0.25, (0, 0, -0.075))),
                        Parallel(self.scaleInterval(0.25, (0, 0, 0)),
                                 self.posInterval(0.25, (0, 0, 0))))

    def getShowIntervalCheat(self, text, duration):
        return Sequence(Func(self.hide), Func(self.setFg, (0.466, 0.474, 1.0, 1.0)), Wait(duration * 0.1),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, 0.42)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.2, 1.2)),
                                 self.posInterval(0.25, (0, 0, -0.075))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(2),
                        Parallel(self.scaleInterval(0.25, (1.3, 1.3, 1.3)),
                                 self.posInterval(0.25, (0, 0, -0.075))),
                        Parallel(self.scaleInterval(0.25, (0, 0, 0)),
                                 self.posInterval(0.25, (0, 0, 0))))

    def getShowIntervalDesc(self, text, duration):
        return Sequence(Func(self.hide), Func(self.setWordwrap, None), Func(self.setPos, 0.0, 0.65),
                        Func(self.setScale, 0.1), Func(self.setFg, (0.847, 0.784, 0.992, 1.0)), Wait(duration * 0.1),
                        Func(self.setText, text),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, 0.42)), Func(self.setText, text),
                        Func(self.show),
                        Wait(0.5),
                        Parallel(self.scaleInterval(0.25, (1.2, 1.2, 1.2)),
                                 self.posInterval(0.25, (0, 0, -0.075))),
                        Parallel(self.scaleInterval(0.25, (1.1, 1.1, 1.1)),
                                 self.posInterval(0.25, (0, 0, -0.040))),
                        Wait(2),
                        Parallel(self.scaleInterval(0.25, (1.3, 1.3, 1.3)),
                                 self.posInterval(0.25, (0, 0, -0.075))),
                        Parallel(self.scaleInterval(0.25, (0, 0, 0)),
                                 self.posInterval(0.25, (0, 0, 0))))

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