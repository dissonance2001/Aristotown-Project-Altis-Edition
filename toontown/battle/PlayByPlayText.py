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
from typing import Union

class PlayByPlayText(OnscreenText.OnscreenText):
    notify = DirectNotifyGlobal.directNotify.newCategory('PlayByPlayText')
    wordwrapBase = 16

    def __init__(self) -> None:
        OnscreenText.OnscreenText.__init__(
            self, mayChange=True,
            pos=(0.0, 0.75), scale=TTLocalizer.PBPTonscreenText,
            fg=(1.0, 0.0, 0.0, 1.0), font=getSignFont(),
            wordwrap=self.wordwrapBase)
        self.currentSequence = Sequence()
        self.color = (1.0, 0.0, 0.0, 1.0)
        self.colorFunc = None
        self.subText = OnscreenText.OnscreenText(mayChange=True,
                                                 pos=(0.0, 0.65),
                                                 scale=0.1,
                                                 fg=(1.0, 0.5, 0.0, 1.0),
                                                 font=getSignFont(),
                                                 wordwrap=self.wordwrapBase * 2)
        self.subTextColor = None
        self.deadToonsText = OnscreenText.OnscreenText(mayChange=True,
                                                       pos=(0.0, 0.75),
                                                       scale=TTLocalizer.PBPTonscreenText,
                                                       fg=(1.0, 0.0, 0.0, 1.0),
                                                       font=getSignFont(),
                                                       wordwrap=self.wordwrapBase)
        self.deadToonsText.setColorScale(1.0, 1.0, 1.0, 0.0)
        self.deadToonsText.hide()

    def getShowInterval(self, text, duration, colorOverride = lambda: (1.0, 0.0, 0.0, 1.0), posOverride = lambda: (0.0, 0.75),
                        pbpDelay: float = 0.0, pbpSubtextDelay: float = 0.0, wantFadeIn: bool = True, wantFadeOut: bool = True,
                        wordwrapMult: float = 1.0, fadeInMult: float = 0.1, subtextFadeInMult: float = 0.2,
                        fadeOutMult: float = 0.7) -> Union[Track, Sequence]:
        self.colorFunc = colorOverride
        self.color = colorOverride()

        fadeInDur: float = duration * fadeInMult if wantFadeIn else 0.0

        def updateWordwrap() -> None:
            self.setWordwrap(self.wordwrapBase * wordwrapMult)
            self.subText.setWordwrap(self.wordwrapBase * wordwrapMult * 2)
            self.deadToonsText.setWordwrap(self.wordwrapBase * wordwrapMult)

        normalTextScaleSeq: Sequence
        if wantFadeIn:
            normalTextScaleSeq = Sequence(
                LerpFunc(self.setTextScale, fromData=0.025, toData=TTLocalizer.PBPTonscreenText * 1.1, duration=0.3, blendType='easeInOut'),
                LerpFunc(self.setTextScale, fromData=TTLocalizer.PBPTonscreenText * 1.1, toData=TTLocalizer.PBPTonscreenText, duration=0.08, blendType='easeInOut')
            )
        else:
            normalTextScaleSeq = Sequence(
                Func(self.setTextScale, TTLocalizer.PBPTonscreenText)
            )

        if isinstance(text, tuple):
            self.subTextColor = (1.0, 0.5, 0.0, 1.0) if self.color == (1.0, 0.0, 0.0, 1.0) else (0.85, 0.78, 1.0, 1.0)
            subTextScale: float = TTLocalizer.PBPTonscreenText * TTLocalizer.PBPTsubTextModifier

            subTextScaleSeq: Sequence = Sequence(
                LerpFunc(self.subText.setTextScale, fromData=0.025, toData=subTextScale * 1.1, duration=0.3, blendType='easeInOut'),
                LerpFunc(self.subText.setTextScale, fromData=subTextScale * 1.1, toData=subTextScale, duration=0.08, blendType='easeInOut')
            )

            self.currentSequence = Track(
                (0.0 + pbpDelay, Sequence(
                    Func(updateWordwrap),
                    Func(self.setColorScale, (1.0, 1.0, 1.0, 1.0)),
                    Func(self.subText.setColorScale, (1.0, 1.0, 1.0, 1.0)),
                    Func(self.setTextColor, colorOverride),
                    Func(self.setSubTextColor, lambda: self.subTextColor),
                    Func(self.setTextPos, posOverride),
                    Func(self.hide),
                    Func(self.setTextScale, 0.01),
                    Func(self.subText.hide),
                    Func(self.subText.setTextScale, 0.01),
                    Wait(fadeInDur),
                    Func(self.setText, text[0]),
                    Func(self.subText.setText, text[1]),
                    Func(self.show),
                    Func(normalTextScaleSeq.start)
                )),
                ((duration * subtextFadeInMult) + pbpSubtextDelay, Parallel(
                    Func(self.subText.show),
                    Func(subTextScaleSeq.start)
                )),
                (duration * fadeOutMult, Sequence(
                    Func(normalTextScaleSeq.finish),
                    Func(subTextScaleSeq.finish),
                    LerpFunc(self.fadeOutText, fromData=1.0, toData=0.0, duration=duration * 0.1, extraArgs=[self.colorFunc, True], blendType='easeInOut'),
                    Func(self.hide),
                    Func(self.subText.hide)
                )) if wantFadeOut else (duration * 1.0, Sequence(
                    Func(normalTextScaleSeq.finish),
                    Func(subTextScaleSeq.finish),
                    LerpFunc(self.fadeOutText, fromData=0.0, toData=0.0, duration=0.0, extraArgs=[self.colorFunc, True], blendType='easeInOut'),
                    Func(self.hide),
                    Func(self.subText.hide)
                ))
            )
        else:
            self.currentSequence = Sequence(
                Func(updateWordwrap),
                Func(self.setColorScale, (1.0, 1.0, 1.0, 1.0)),
                Func(self.setTextColor, colorOverride),
                Func(self.setTextPos, posOverride),
                Func(self.hide),
                Func(self.setTextScale, 0.01),
                Func(self.subText.hide),
                Func(self.subText.setTextScale, 0.01),
                Wait(fadeInDur),
                Func(self.setText, text),
                Func(self.show),
                Func(normalTextScaleSeq.start),
                Wait(duration * 0.8),
                Func(normalTextScaleSeq.finish),
                LerpFunc(self.fadeOutText, fromData=1.0, toData=0.0, duration=duration * 0.1, extraArgs=[self.colorFunc, True], blendType='easeInOut'),
                Func(self.hide)
            )
        return self.currentSequence

    def getShowIntervalOvercharged(self, text, duration):
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(0.988, 0., 1.0, 1.0)), Func(self.hide), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
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

    def getShowIntervalOverhealed(self, text, duration):
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(0, 0.949, 1, 1.0)), Func(self.hide), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
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
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(0.466, 0.474, 1.0, 1.0)), Func(self.hide), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
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

    def getShowIntervalCheatOverhealed(self, text, duration):
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(0, 0.949, 1, 1.0)), Func(self.hide), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
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
        return Sequence(LerpColorScaleInterval(self, 0, Vec4(0.988, 0., 1.0, 1.0)), Func(self.hide), Func(self.setPos, 0.0, 0.75), Func(self.setScale, 0.16),
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
        return Sequence(Wait(0.5), LerpColorScaleInterval(self, 0, Vec4(0.847, 0.784, 0.992, 1.0)), Func(self.hide), Func(self.setWordwrap, 30), Func(self.setPos, 0.0, 0.6625),
                        Func(self.setScale, 0.09),
                        Func(self.setText, text),
                        LerpScaleInterval(self, duration=0, scale=(0, 0, 0)),
                        self.posInterval(0, (0, 0, 0.6625)),
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

    def showToonsDied(self, toons) -> None:
        toonNames = []

        def createToonText(toon) -> None:
            toonName = toon.getName()
            saved = toon.getHp() > 0
            toonNames.append((toonName, saved))

        for toon in toons:
            createToonText(toon)

        stringBase = 'defeated!'
        allSaved: bool = all([text[1] for text in toonNames])
        if allSaved:
            stringBase = 'saved by a Unite!'

        finalToonNames = ()
        if allSaved:
            for toonName in toonNames:
                finalToonNames += (toonName[0],)
        else:
            for toonName in toonNames:
                if not toonName[1]:
                    finalToonNames += (toonName[0],)

        # TODO: Change to encompass more Toons and be more flexible.
        stringFormats = {
            1: '{0} was ',
            2: '{0} and {1} were ',
            3: '{0}, {1}, and {2} were ',
            4: '{0}, {1}, {2}, and {3} were '
        }

        beginning = stringFormats[len(finalToonNames)].format(*finalToonNames)
        deathString = beginning + stringBase

        textColor = (0.0, 1.0, 0.0, 1.0) if allSaved else (1.0, 0.0, 0.0, 1.0)
        textFunc = lambda: textColor

        normalTextScaleSeq: Sequence = Sequence(
            Parallel(
                LerpColorScaleInterval(self, 0.2, (1.0, 1.0, 1.0, 0.0)),
                LerpColorScaleInterval(self.subText, 0.2, (1.0, 1.0, 1.0, 0.0))
            ),
            Func(self.setDeadTextColor, textFunc),
            Func(self.deadToonsText.setTextPos, (0.0, 0.75)),
            Func(self.deadToonsText.setText, deathString),
            Func(self.deadToonsText.show),
            LerpColorScaleInterval(self.deadToonsText, 0.2, (1.0, 1.0, 1.0, 1.0)),
            Wait(3.8),
            LerpColorScaleInterval(self.deadToonsText, 0.2, (1.0, 1.0, 1.0, 0.0))
        )

        if self.currentSequence:
            self.currentSequence.pause()
            self.currentSequence = None

        def tryHide() -> None:
            normalTextScaleSeq.finish()
            if self and hasattr(self, 'hide'):
                self.hide()

        def tryShow() -> None:
            normalTextScaleSeq.start()
            if self and hasattr(self, 'show'):
                if getattr(self, 'subText', None):
                    self.subText.hide()
                self.show()

        if not self:
            return

        if not hasattr(self, 'hide'):
            return

        self.currentSequence = Sequence(
            Func(tryHide),
            Wait(0.5),
            Func(tryShow),
            Wait(4.0),
            Func(tryHide)
        )
        self.currentSequence.start()

    def setTextColor(self, color = lambda: (1.0, 0.0, 0.0, 1.0)) -> None:
        self['fg'] = color()

    def setSubTextColor(self, color = lambda: (1.0, 0.5, 0.0, 1.0)) -> None:
        self.subText['fg'] = color()

    def setDeadTextColor(self, color = lambda: (1.0, 0.0, 0.0, 1.0)) -> None:
        self.deadToonsText['fg'] = color()

    def fadeOutText(self, alpha: float, color, usingColorScale: bool = False):
        # This looks really terrible but its basically grabbing the first 3 parts of the color func
        # thats passed through, and then adding an alpha and THEN repacking it into a lambda because that is
        # what setTextColor expects.
        if usingColorScale:
            self.setColorScale(1.0, 1.0, 1.0, alpha)
            if self.subTextColor:
                self.subText.setColorScale(1.0, 1.0, 1.0, alpha)
        else:
            self.setTextColor(lambda: (*color()[:3], alpha))
            if self.subTextColor:
                self.setSubTextColor(lambda: (self.subTextColor[0], self.subTextColor[1], self.subTextColor[2], alpha))

    def setTextPos(self, pos = lambda: (0.0, 0.75)):
        textPos = pos()
        OnscreenText.OnscreenText.setTextPos(self, textPos)
        if self.subText:
            subTextPos = (textPos[0], textPos[1] - 0.1)
            self.subText.setTextPos(subTextPos)

    def cleanup(self):
        self.currentSequence.finish()
        del self.currentSequence
        OnscreenText.OnscreenText.cleanup(self)
        self.colorFunc = None
        if self.subText:
            self.subText.cleanup()
            self.subText = None
        if self.deadToonsText:
            self.deadToonsText.cleanup()
            self.deadToonsText = None
