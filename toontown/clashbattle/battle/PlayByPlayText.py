from toontown.battle.SuitBattleGlobals import *
from toontown.toonbase import ToontownGlobals
from direct.interval.IntervalGlobal import *
from direct.gui import OnscreenText


@DirectNotifyCategory()
class PlayByPlayText(OnscreenText.OnscreenText):
    wordwrapBase = 16

    def __init__(self):
        OnscreenText.OnscreenText.__init__(
            self, mayChange=1,
            pos=(0.0, 0.75), scale=TTLocalizer.PBPTonscreenText,
            fg=(1, 0, 0, 1), font=ToontownGlobals.getSignFont(),
            wordwrap=self.wordwrapBase)
        self.currentSequence = Sequence()
        self.color = (1, 0, 0, 1)
        self.colorFunc = None
        self.subText = OnscreenText.OnscreenText(mayChange=1,
                                                 pos=(0.0, 0.65),
                                                 scale=0.1,
                                                 fg=(1, 0.5, 0, 1),
                                                 font=ToontownGlobals.getSignFont(),
                                                 wordwrap=self.wordwrapBase * 2)
        self.subTextColor = None
        self.deadToonsText = OnscreenText.OnscreenText(mayChange=1,
                                                       pos=(0.0, 0.75),
                                                       scale=TTLocalizer.PBPTonscreenText,
                                                       fg=(1, 0, 0, 1),
                                                       font=ToontownGlobals.getSignFont(),
                                                       wordwrap=self.wordwrapBase)
        self.deadToonsText.setColorScale(1, 1, 1, 0)
        self.deadToonsText.hide()

    def getShowInterval(self, text, duration, colorOverride=lambda: (1, 0, 0, 1), posOverride=lambda: (0.0, 0.75),
                        pbpDelay: float = 0.0, pbpSubtextDelay: float = 0.0, wantFadeIn: bool=True, wantFadeOut: bool=True,
                        wordwrapMult: float = 1.0, fadeInMult: float = 0.1, subtextFadeInMult: float = 0.2,
                        fadeOutMult: float = 0.7):
        self.colorFunc = colorOverride
        self.color = colorOverride()

        fadeInDur = duration * fadeInMult if wantFadeIn else 0

        def updateWordwrap():
            self.setWordwrap(self.wordwrapBase * wordwrapMult)
            self.subText.setWordwrap(self.wordwrapBase * wordwrapMult * 2)
            self.deadToonsText.setWordwrap(self.wordwrapBase * wordwrapMult)

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
            if self.color == (1, 0, 0, 1):
                self.subTextColor = (1, 0.5, 0, 1)
            else:
                self.subTextColor = (0.85, 0.78, 1.0, 1)
            subTextScale = TTLocalizer.PBPTonscreenText * TTLocalizer.PBPTsubTextModifier

            subTextScaleSeq = Sequence(
                LerpFunc(self.subText.setTextScale, fromData=0.025, toData=subTextScale * 1.1, duration=0.3, blendType='easeInOut'),
                LerpFunc(self.subText.setTextScale, fromData=subTextScale * 1.1, toData=subTextScale, duration=0.08, blendType='easeInOut')
            )

            self.currentSequence = Track(
                (0.0 + pbpDelay, Sequence(
                    Parallel(
                        Func(updateWordwrap),
                        Func(self.setColorScale, (1, 1, 1, 1)),
                        Func(self.subText.setColorScale, (1, 1, 1, 1)),
                        Func(self.setTextColor, colorOverride),
                        Func(self.setSubTextColor, lambda: self.subTextColor)
                    ),
                    Func(self.setTextPos, posOverride),
                    Parallel(
                        Func(self.hide),
                        Func(self.setTextScale, 0.01),
                        Func(self.subText.hide),
                        Func(self.subText.setTextScale, 0.01),
                    ),
                    Wait(fadeInDur),
                    Parallel(
                        Func(self.setText, text[0]),
                        Func(self.subText.setText, text[1])
                    ),
                    Parallel(
                        Func(self.show),
                        Func(normalTextScaleSeq.start),
                    ),
                )),
                ((duration * subtextFadeInMult) + pbpSubtextDelay, Parallel(
                    Func(self.subText.show),
                    Func(subTextScaleSeq.start),
                )),
                (duration * fadeOutMult, Sequence(
                    Func(normalTextScaleSeq.finish),
                    Func(subTextScaleSeq.finish),
                    Parallel(
                        LerpFunc(self.fadeOutText, fromData=1, toData=0, duration=duration * 0.1,
                                 extraArgs=[self.colorFunc, True], blendType='easeInOut'),
                    ),
                    Parallel(
                        Func(self.hide),
                        Func(self.subText.hide)
                    )
                )) if wantFadeOut else (
                    duration * 1.0,
                    Sequence(
                        Func(normalTextScaleSeq.finish),
                        Func(subTextScaleSeq.finish),
                        Parallel(
                            LerpFunc(self.fadeOutText, fromData=0, toData=0, duration=0.0,
                                     extraArgs=[self.colorFunc, True], blendType='easeInOut')
                        ),
                        Parallel(
                            Func(self.hide),
                            Func(self.subText.hide)
                        )
                    )
                 )
            )
        else:
            self.currentSequence = Sequence(
                Func(updateWordwrap),
                Func(self.setColorScale, (1, 1, 1, 1)),
                Func(self.setTextColor, colorOverride),
                Func(self.setTextPos, posOverride),
                Parallel(
                    Func(self.hide),
                    Func(self.setTextScale, 0.01),
                    Func(self.subText.hide),
                    Func(self.subText.setTextScale, 0.01),
                ),
                Wait(fadeInDur),
                Func(self.setText, text),
                Parallel(
                    Func(self.show),
                    Func(normalTextScaleSeq.start),
                ),
                Wait(duration * 0.8),
                Func(normalTextScaleSeq.finish),
                LerpFunc(self.fadeOutText, fromData=1, toData=0, duration=duration * 0.1,
                         extraArgs=[self.colorFunc, True], blendType='easeInOut'),
                Func(self.hide)
            )
        return self.currentSequence

    def showToonsDied(self, toons):
        toonNames = []

        def createToonText(toon):
            toonName = toon.getName().upper()
            saved = toon.getHp() > 0
            toonNames.append([toonName, saved])

        for toon in toons:
            createToonText(toon)

        stringBase = TTLocalizer.MovieToonDefeated
        allSaved = all([text[1] for text in toonNames])
        if allSaved:
            stringBase = TTLocalizer.MovieToonSaved

        finalToonNames = []
        if allSaved:
            for toonName in toonNames:
                finalToonNames.append(toonName[0])
        else:
            for toonName in toonNames:
                if not toonName[1]:
                    finalToonNames.append(toonName[0])

        stringFormats = {
            1: '{0} WAS ',
            2: '{0} AND {1} WERE ',
            3: '{0}, {1}, AND {2} WERE ',
            4: '{0}, {1}, {2}, AND {3} WERE ',
        }

        beginning = stringFormats[len(finalToonNames)].format(*finalToonNames)
        deathString = beginning + stringBase

        textColor = (0, 1, 0, 1) if allSaved else (1, 0, 0, 1)
        textFunc = lambda: textColor

        normalTextScaleSeq = Sequence(
            Parallel(
                LerpColorScaleInterval(self, 0.2, (1, 1, 1, 0)),
                LerpColorScaleInterval(self.subText, 0.2, (1, 1, 1, 0))
            ),
            Func(self.setDeadTextColor, textFunc),
            Func(self.deadToonsText.setTextPos, (0.0, 0.75)),
            Func(self.deadToonsText.setText, deathString),
            Func(self.deadToonsText.show),
            LerpColorScaleInterval(self.deadToonsText, 0.2, (1, 1, 1, 1)),
            Wait(3.8),
            LerpColorScaleInterval(self.deadToonsText, 0.2, (1, 1, 1, 0))
        )

        if self.currentSequence:
            self.currentSequence.pause()
            self.currentSequence = None

        def tryHide():
            normalTextScaleSeq.finish()
            if self and hasattr(self, 'hide'):
                self.hide()

        def tryShow():
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
            Func(tryHide),
        )
        self.currentSequence.start()

    def setTextColor(self, color=lambda: (1, 0, 0, 1)):
        self['fg'] = color()

    def setSubTextColor(self, color=lambda: (1, 0.5, 0, 1)):
        self.subText['fg'] = color()

    def setDeadTextColor(self, color=lambda: (1, 0, 0, 1)):
        self.deadToonsText['fg'] = color()

    def fadeOutText(self, alpha, color, usingColorScale=False):
        # This looks really terrible but its basically grabbing the first 3 parts of the color func
        # thats passed through, and then adding an alpha and THEN repacking it into a lambda because that is
        # what setTextColor expects.
        if usingColorScale:
            self.setColorScale(1, 1, 1, alpha)
            if self.subTextColor:
                self.subText.setColorScale(1, 1, 1, alpha)
        else:
            self.setTextColor(lambda: (*color()[:3], alpha))
            if self.subTextColor:
                self.setSubTextColor(lambda: (self.subTextColor[0], self.subTextColor[1], self.subTextColor[2], alpha))

    def setTextPos(self, pos=lambda: (0.0, 0.75)):
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
