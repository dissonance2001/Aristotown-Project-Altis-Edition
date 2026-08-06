import random
import math
from direct.gui.DirectFrame import DirectFrame
from direct.showbase.PythonUtil import lerp
from direct.gui import DirectGuiGlobals as DGG
from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.editor.CSEditorEnums import SubEventArgumentType as SEAT
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence
from direct.interval.IntervalGlobal import *

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
