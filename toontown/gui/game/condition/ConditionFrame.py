from __future__ import annotations

import math

from toontown.gui.UiLerper import UILerper


from typing import Any

from toontown.gui.game.condition.ConditionGlobals import *

from toontown.gui.game.condition.subframes.ConditionSubframeBase import ConditionSubframeBase
from toontown.gui.game.GameGUIGlobals import UI_SCALED_SHADOW_ALPHA
from toontown.gui import TTGui
from toontown.gui.CornerAnchor import CornerAnchor
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.gui.TilingScaledFrame import TilingScaledFrame
from toontown.gui.hover.HoverFrameTypes import HoverFrameTypes
from toontown.toon.gui import GuiBinGlobals

from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *
from panda3d.core import Vec4, TextNode
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget


@DirectNotifyCategory()
class ConditionFrame(EasyManagedItem):
    Z_SPEED = 0.25
    INDEX_LAG = 0.12
    SLIDE_IN_SPEED = 0.27
    SLIDE_OUT_SPEED = 0.27

    ConditionScaledTexture = 'phase_3/maps/gui/ttcc_gui_tiledFrame_generic_border.png'
    ConditionScaledColor = Vec4(48 / 255, 181 / 255, 105 / 255, 1.0)
    ConditionPatternTexture = 'core/gui/maps/cc_t_gui_sframe_pat_testblue.png'
    ConditionPatternColor = Vec4(1, 1, 1, UI_SCALED_SHADOW_ALPHA)
    ConditionPatternSpeed = (0.02, -0.02)
    ConditionPatternScale = 0.14

    HoverFrameType = None

    @InjectorTarget
    def __init__(self, parent, **kw):
        optiondefs = TTGui.kwargsToOptionDefs(
            pos=(0, 0, 0),
            scale=1.0,
            relief=None,
            frameSize=(0.0, 0.74721, -0.20635, 0.0),
            obj=None,
            conditionState=ConditionState.GLOBAL,
            conditionStateArgs=ConditionStateArgs(),
            side=ConditionSide.LEFT,
            index=0,
            dismissable=False,
            subframeStart=0.03,
            iconDist=0.14,
            iconScale=0.2,
            easyPadUp=0.0,
            height=0.20635,
            heightPadMult=1.15,
            shadowBorder=0.02662,
            shadowPadding=-0.01358,
            shadowOffscreen=-0.09412,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(ConditionFrame)
        self.setBin('sorted-gui-popup', GuiBinGlobals.ConditionFrame)

        self.conditionArgs = None
        self.subframes = []
        self.queuedIconTypes = []
        self.iconSeq = None
        self.hasSetZ = False
        self.zSeq = None
        self.goalZ = -128937123.0
        self.slideSeq = None
        self.hasSlidIn = False

        self.frame = TilingScaledFrame(
            parent=self,
            borderScale=0.024,
            frameBin=GuiBinGlobals.ConditionFrame,
            scaledTexture=self.getConditionScaledTexture(),
            scaledColor=self.getConditionScaledColor(),
            patternTexture=self.getConditionPatternTexture(),
            patternSpeed=self.getConditionPatternSpeed(),
            patternScale=self.getConditionPatternScale(),
        )
        self.frame.patternNode.setColorScale(self.getConditionPatternColor())
        self.anchor = CornerAnchor(parent=self, corner=SideCorners.get(self['side']))
        self.flipAnchor = CornerAnchor(parent=self.frame, corner=SideReverseCorners.get(self['side']))

        self.accept(AskIconMsg, self.askIconMessage)

        if self['dismissable']:
            self.frame.bind(DGG.WITHIN, self.mouseWithinBounds)
            self.frame.bind(DGG.WITHOUT, self.mouseWithoutBounds)
            self.frame['state'] = DGG.NORMAL
            self.accept('mouse1-up', self.__attemptDismiss)

        self.hide()

    def destroy(self):
        if hasattr(self, 'isDestroying'):
            return
        self.isDestroying = 1
        self.ignoreAll()

        def finishDestroy():
            self.cleanupLerpSeqs()
            self.queuedIconTypes = []
            if self.iconSeq:
                self.iconSeq.finish()
                self.iconSeq = None
            self.conditionArgs = None
            self.subframes = []
            self.anchor = None
            self.queuedIconTypes = []
            self.frame = None
            EasyManagedItem.destroy(self)

        self.slideOut(finishDestroy)

    def getConditionScaledTexture(self):
        return self.ConditionScaledTexture

    def getConditionScaledColor(self):
        return self.ConditionScaledColor

    def getConditionPatternTexture(self):
        return self.ConditionPatternTexture

    def getConditionPatternSpeed(self):
        return self.ConditionPatternSpeed

    def getConditionPatternScale(self):
        return self.ConditionPatternScale

    def getConditionPatternColor(self):
        return self.ConditionPatternColor

    def determineSubframeClasses(self) -> list[type[ConditionSubframeBase]]:
        return []

    def makeConditionArgs(self) -> ConditionArgs:
        return ConditionArgs()

    def canObjectOwnUs(self, obj: Any) -> bool:
        return False

    def getFrameScale(self) -> float:
        if self['index'] == 0:
            return StandardFrameScale
        return SmallFrameScale

    def place(self):
        z = 0
        furthestDist = 0
        subframeX = self['subframeStart'] * (-1 if self.side == ConditionSide.RIGHT else 1)
        for frame in self.subframes:
            z -= frame.getEasyPadUp()
            frame.setPos(subframeX, 0, z)
            frame.place()
            l, r, *__ = frame['frameSize']
            if self.side == ConditionSide.LEFT:
                furthestDist = max(furthestDist, r + frame.extraDist)
            elif self.side == ConditionSide.RIGHT:
                furthestDist = min(furthestDist, l - frame.extraDist)
            else:
                raise KeyError
            z += frame.getEasyHeight()
            z += frame.getEasyPadDown()

        frameHeight = min(-self['height'], z)
        self['frameSize'] = {
            ConditionSide.LEFT: (0, 1, frameHeight, 0),
            ConditionSide.RIGHT: (-1, 0, frameHeight, 0),
        }.get(self.side)
        left, right, down, up = self.getDefinedBounds()
        width = right - left
        height = up - down
        self['easyWidth'] = width
        self['easyHeight'] = height * self['heightPadMult']

        self.frame['borderScale'] = self['shadowBorder']
        UILerper.lerpOption(
            gui=self.frame,
            option='frameSize',
            duration=self.SLIDE_IN_SPEED,
            end={
                ConditionSide.LEFT: (
                    left - self['shadowPadding'] + self['shadowOffscreen'],
                    subframeX + furthestDist + self['shadowPadding'],
                    down - self['shadowPadding'],
                    up + self['shadowPadding'],
                ),
                ConditionSide.RIGHT: (
                    subframeX + furthestDist - self['shadowPadding'],
                    right + self['shadowPadding'] - self['shadowOffscreen'],
                    down - self['shadowPadding'],
                    up + self['shadowPadding'],
                ),
            }.get(self.side),
            instant=self.frame['frameSize'] is None,
        )

        for frame in self.subframes:
            frame.setZ(frame.getZ() + (frameHeight / 2) - (z / 2))

        self.anchor.place()
        self.flipAnchor.place()

        if not self.hasSlidIn:
            self.hasSlidIn = True
            self.slideIn()

    def buildSubframes(self) -> None:
        self.conditionArgs = self.makeConditionArgs()
        subframeClasses = [cls for cls in self.determineSubframeClasses() if cls.validateArgs(self.conditionArgs)]
        subframeClassSet = set(subframeClasses)

        for activeSubframe in self.subframes[:]:
            if type(activeSubframe) not in subframeClassSet:
                self.subframes.remove(activeSubframe)
                activeSubframe.destroy()

        activeSubframeTypes = set(type(subframe) for subframe in self.subframes)
        for subframeClass in subframeClasses:
            if subframeClass not in activeSubframeTypes:
                newFrame = subframeClass(parent=self.frame, side=self.side)
                self.frame.clipWithinFrame(newFrame)
                self.subframes.append(newFrame)

        orderedSubframes = []
        for subframeClass in subframeClasses:
            for subframe in self.subframes:
                if type(subframe) is subframeClass:
                    orderedSubframes.append(subframe)
                    break
        self.subframes = orderedSubframes

        for subframe in self.subframes:
            if subframe.conditionArgs != self.conditionArgs:
                subframe['conditionArgs'] = self.conditionArgs
            if subframe.side != self.side:
                subframe['side'] = self.side
            subframe.place()

        self.place()

    def mouseWithinBounds(self, _=None):
        if not self.HoverFrameType:
            raise NotImplementedError(f'Unimplemented hover frame type for {self.__class__.__name__}')
        if getattr(base, 'hoverMgr', None):
            base.hoverMgr.hoverObject(self.frame, item=self.obj, itemType=self.HoverFrameType, frameDir='right')

    def mouseWithoutBounds(self, _=None):
        if getattr(base, 'hoverMgr', None):
            base.hoverMgr.unhoverObject()

    def __attemptDismiss(self):
        if not self.frame.isMouseWithinBounds():
            return
        manager = None
        try:
            manager = base.cr.gameGui.getConditionUIManager()
        except Exception:
            manager = getattr(base.cr, 'scavengeConditionUIManager', None)
        if manager:
            manager.removeTimedReleaseFrame(self.obj)

    def getTimedReleaseDuration(self) -> float:
        try:
            manager = base.cr.gameGui.getConditionUIManager()
        except Exception:
            manager = getattr(base.cr, 'scavengeConditionUIManager', None)
        if not manager:
            return 10.0
        return manager.timedReleaseObjects.get(self.obj, 10.0)

    def askIconMessage(self, obj: Any, conditionIconType):
        if obj is not self.obj:
            return
        self.queuedIconTypes.append(conditionIconType)
        if not self.iconSeq:
            self._checkIconQueue()

    def _checkIconQueue(self):
        if not self.queuedIconTypes:
            self.iconSeq = None
            return
        conditionIconType = self.queuedIconTypes.pop(0)
        from toontown.gui.game.condition.ConditionIcon import ConditionIcon
        iconGui = ConditionIcon(
            parent=self.flipAnchor,
            conditionIconType=conditionIconType,
            pos=(self['iconDist'] * (1 if self.side == ConditionSide.LEFT else -1), 0, 0),
            scale=self['iconScale'],
        )
        self.iconSeq = iconGui.makeSequence(self._checkIconQueue)
        self.iconSeq.start()

    def cleanupLerpSeqs(self):
        if self.zSeq:
            self.zSeq.pause()
            self.zSeq = None

    def setZGoal(self, z: float):
        if not self.hasSetZ:
            self.hasSetZ = True
            self.setZ(z)
            return
        if z == self.goalZ:
            return
        self.goalZ = z
        if self.zSeq:
            self.zSeq.pause()
            self.zSeq = None
        startZ = self.getZ()
        def ival(t: float):
            self.setZ(lerp(startZ, z, t))
        self.zSeq = Sequence(LerpFunctionInterval(ival, duration=self.Z_SPEED, blendType='easeOut'))
        self.zSeq.start()

    def slideIn(self):
        left, right, *_ = self.frame.getDefinedBounds()
        width = abs(right - left) * 1.1
        if self.side == ConditionSide.LEFT:
            width = -width
        def ival(t=0):
            self.setX(lerp(width, 0, t))
        self.slideSeq = Sequence(
            Func(ival),
            Wait(self.INDEX_LAG * self['index']),
            Func(self.show),
            LerpFunctionInterval(ival, duration=self.SLIDE_IN_SPEED, blendType='easeOut'),
        )
        self.slideSeq.start()

    def slideOut(self, callback=None):
        if self.slideSeq:
            self.slideSeq.pause()
            self.slideSeq = None
        left, right, *_ = self.frame.getDefinedBounds()
        width = abs(right - left) * 1.1
        if self.side == ConditionSide.LEFT:
            width = -width
        def ival(t=0):
            self.setX(lerp(0, width, t))
        self.slideSeq = Sequence(
            Func(ival),
            Wait(self.INDEX_LAG * self['index']),
            LerpFunctionInterval(ival, duration=self.SLIDE_OUT_SPEED, blendType='easeIn'),
            Func(callback) if callback else Wait(0.0),
        )
        self.slideSeq.start()

    @property
    def obj(self) -> Any:
        return self['obj']

    @property
    def conditionState(self) -> ConditionState:
        return self['conditionState']

    @property
    def conditionStateArgs(self) -> ConditionStateArgs:
        return self['conditionStateArgs']

    @property
    def side(self) -> ConditionSide:
        return self['side']
