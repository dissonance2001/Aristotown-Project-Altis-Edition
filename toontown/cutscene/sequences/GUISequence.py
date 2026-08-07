import random
import math
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.PythonUtil import lerp
from direct.gui import DirectGuiGlobals as DGG
from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.editor.CSEditorEnums import SubEventArgumentType as SEAT
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence
from direct.interval.IntervalGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownTimer import ToontownTimer

@cutsceneSequence(name='Screen: Fade Color', enum=EDE.doScreenFade)
def seq_fadeColor(delay=0, color=(0, 0, 0), fadeInDuration=1.0, fadeInBlendType='noBlend', holdDuration=1.0, fadeOutDuration=1.0, fadeOutBlendType='noBlend', cutsceneDict=None):
    screenGui = DirectFrame(parent=render2d, relief=DGG.FLAT, frameSize=(-1, 1, -1, 1), frameColor=(0, 0, 0, 0))
    r, g, b = color

    def lerpScreenColor(t):
        if screenGui:
            screenGui['frameColor'] = (r, g, b, t)

    def cleanup():
        if screenGui:
            screenGui.destroy()
    return Sequence(Wait(delay), LerpFunctionInterval(function=lerpScreenColor, duration=fadeInDuration, fromData=0, toData=1, blendType=fadeInBlendType), Func(lerpScreenColor, 1.0), Wait(holdDuration), LerpFunctionInterval(function=lerpScreenColor, duration=fadeOutDuration, fromData=1, toData=0, blendType=fadeOutBlendType), Func(cleanup))

@cutsceneSequence(name='Node: Basic Label', enum=EDE.basicLabel)
def seq_basicLabel(nodeIndex=0, useRender2d=False, messageIndex=0, delay=0.0, duration=1.2, pos=(0, 0, 0), hpr=(0, 0, 0), scale=1.0, cutsceneDict=None, **kwargs):
    node = cutsceneDict['nodes'][nodeIndex]
    if node in (hidden, camera):
        return Sequence()
    message = cutsceneDict['messages'][messageIndex]
    parent = render2d if useRender2d else node
    label = DirectFrame(
        parent=parent,
        relief=DGG.FLAT,
        frameColor=(0.05, 0.05, 0.05, 0.88),
        borderWidth=(0.02, 0.02),
        pos=tuple(pos),
        hpr=tuple(hpr),
        scale=scale,
        text=message,
        text_fg=(1, 1, 1, 1),
        text_wordwrap=20,
        text_scale=0.08,
        text_pos=(0, -0.025),
        frameSize=(-0.65, 0.65, -0.12, 0.12),
    )
    label.hide()
    label.setBin('fixed', 5000)

    def doShow():
        if label:
            label.show()

    def cleanup():
        if label:
            label.destroy()

    return Sequence(Wait(delay), Func(doShow), Wait(duration), Func(cleanup))


@cutsceneSequence(name='Timescale: Show Change', enum=EDE.showTimescaleChange)
def seq_timescaleChange(enterDuration=1.0, holdDuration=1.0, exitDuration=1.0, timerScale=1.0, cutsceneDict=None):
    startScale, endScale = cutsceneDict['arguments'][:2]
    timer = ToontownTimer()
    timer.setScale(timerScale)
    timer.hide()
    OnscreenText(
        parent=timer,
        text='Battle Speed',
        scale=0.27,
        pos=(0, -0.55),
        fg=(1, 1, 1, 1),
        font=ToontownGlobals.getSignFont(),
    )

    def setTime(value):
        if timer:
            timer.setTimeStr('x%.2f' % value, scale=0.145)

    setTime(startScale)

    def lerpTimerText(t):
        setTime(lerp(startScale, endScale, t))

    return Sequence(
        Func(timer.show),
        LerpPosInterval(
            timer, enterDuration,
            pos=(0, 0, 0), startPos=(0, 0, 2.0),
            blendType='easeOut'),
        LerpFunctionInterval(
            lerpTimerText, duration=holdDuration, blendType='easeInOut'),
        LerpPosInterval(
            timer, exitDuration,
            pos=(0, 0, -2.0), startPos=(0, 0, 0),
            blendType='easeIn'),
        Func(timer.destroy),
    )
