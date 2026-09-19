import random

from direct.showbase import PythonUtil

from toontown.toonbase.MarginManagerCell import ScreenCellFlag

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.GUINode import GUINode
from toontown.gui import UiHelpers
from toontown.toon.gui import GuiBinGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from typing import Optional, Callable
from direct.interval.IntervalGlobal import *
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class ChainsawMeterGUI(DirectFrame):
    """
    On-screen meter for Chainsaw's RPM.
    """

    BUMP_DURATION = 0.11
    BUMP_COEFF = 0.015

    JIGGLE_POS_DIST = 0.002
    JIGGLE_HPR_DIST = 0.05
    JIGGLE_POS_COEFF_DIST = 0.002
    JIGGLE_HPR_COEFF_DIST = 0.05

    @InjectorTarget
    def __init__(self, parent=base.a2dRightCenter, **kw):
        # GUI boilerplate.
        gui = self.getGui()
        optiondefs = kwargsToOptionDefs(
            pos=(-0.12933, 0.0, 0.0),
            scale=0.32981,
            relief = None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # State
        self.currentPhase = 0
        self.index = 0

        # Positional node
        self.posNodeA = GUINode(parent=self, name='meterPosNode')
        self.posNodeB = GUINode(parent=self.posNodeA, name='bumpNode')
        self.posNodeC = GUINode(parent=self.posNodeB, name='jiggleNode')
        self.posNodeD = GUINode(parent=self.posNodeC, name='horrorNode')
        self.posNodeE = GUINode(parent=self.posNodeD, name='revNode')
        self.posNodeZ = GUINode(parent=self.posNodeE, name='rootNode')

        # Define objects of this GUI.
        self.base = DirectFrame(
            parent=self.posNodeZ, relief=None,
            pos=(0, 0, 0), scale=1.0,
            image=gui.find('**/meter_base'),
            image_scale=UiHelpers.calculateImageScale(256, 1024),
        )
        self.gradient_top = ChainsawMeterGradient(
            parent=self.posNodeZ, relief=None,
            pos=(0.0128, 0.0, 0.85468), scale=0.50408,
        )
        self.gradient_bottom = ChainsawMeterGradient(
            parent=self.posNodeZ, relief=None,
            pos=(0.01748, 0.0, -0.84532), scale=0.50408,
            hpr=(0, 0, 180),
        )
        self.dropshadow = DirectFrame(
            parent=self.posNodeZ, relief=None,
            pos=(0, 0, 0), scale=1.0,
            image=gui.find('**/meter_shadow'),
            image_scale=UiHelpers.calculateImageScale(256, 1024),
        )
        self.markers = ChainsawMeterMarkers(
            parent=self.posNodeZ, relief=None,
            pos=(0, 0, 0), scale=1.0,
        )

        # Set bins.
        self.base.setBin('sorted-gui-popup', GuiBinGlobals.ChainsawMeterGUIBin)
        self.gradient_top.setBin('sorted-gui-popup', GuiBinGlobals.ChainsawMeterGUIBin + 1)
        self.gradient_bottom.setBin('sorted-gui-popup', GuiBinGlobals.ChainsawMeterGUIBin + 1)
        self.markers.setBin('sorted-gui-popup', GuiBinGlobals.ChainsawMeterGUIBin + 2)
        self.dropshadow.setBin('sorted-gui-popup', GuiBinGlobals.ChainsawMeterGUIBin - 1)

        gui.removeNode()

        # Sequence stuff
        self.jiggleSeq = None

        # Open up event hooks
        self.acceptOnce(self.getDestroyEvent(), self.destroy)
        self.acceptOnce(self.getPhaseOneEvent(), self.enterPhaseOne)
        self.acceptOnce(self.getPhaseTwoEvent(), self.enterPhaseTwo)
        self.acceptOnce(self.getPhaseThreeEvent(), self.enterPhaseThree)
        self.accept(self.getRPMDeltaEvent(), self.bump)
        self.accept(self.setRPMEvent(), self.setRPM)
        self.accept(self.getShatterEvent(), self.shatter)

        # Set cells
        base.flagScreenCells(ScreenCellFlag.chainsawMeter, base.rightCells)

        # Do enter transition
        self._enter()
        messenger.send(self.getPhaseOneEvent())

    def destroy(self):
        self.ignoreAll()
        self._exit(callback=self._fullDestroy)

    def _fullDestroy(self):
        if self.jiggleSeq:
            self.jiggleSeq.pause()
        self.jiggleSeq = None
        base.unflagScreenCells(ScreenCellFlag.chainsawMeter, base.rightCells)
        super().destroy()

    @staticmethod
    def getGui():
        return loader.loadModel('phase_6/models/gui/chainsaw_meter_gui')

    """
    Event names
    """

    @staticmethod
    def getDestroyEvent() -> str:
        return 'ChainsawMeterGUI-Destroy'

    @staticmethod
    def getPhaseOneEvent() -> str:
        return 'ChainsawMeterGUI-PhaseOne'

    @staticmethod
    def getPhaseTwoEvent() -> str:
        return 'ChainsawMeterGUI-PhaseTwo'

    @staticmethod
    def getPhaseThreeEvent() -> str:
        return 'ChainsawMeterGUI-PhaseThree'

    @staticmethod
    def getRPMDeltaEvent() -> str:
        return 'ChainsawMeterGUI-RPMDelta'

    @staticmethod
    def setRPMEvent() -> str:
        return 'ChainsawMeterGUI-setRPM'

    @staticmethod
    def getShatterEvent() -> str:
        return 'ChainsawMeterGUI-shatter'

    """
    Phase Management
    """

    def enterPhaseOne(self):
        self.currentPhase = 1
        self.gradient_top.enter()

    def enterPhaseTwo(self):
        self.currentPhase = 2
        self.phaseTransition()
        self.gradient_top.exit()
        self.gradient_bottom.enter()
        messenger.send(self.setRPMEvent(), [0])

    def enterPhaseThree(self):
        self.currentPhase = 3
        self.phaseTransition()
        self.gradient_top.enter()
        self.gradient_bottom.exit()
        self.jiggle()

    """
    Transitions
    """

    def phaseTransition(self):
        Parallel(
            Sequence(
                LerpPosInterval(self.posNodeE, 0.25, (-0.6, 0, 0), blendType='easeOut'),
                LerpPosInterval(self.posNodeE, 0.25, (0, 0, 0), blendType='easeIn'),
            ),
            Sequence(
                LerpColorScaleInterval(self, 0.30, (1.0, 1.0, 1.0, 1.0), (1.0, 0.5, 0.5, 1.0), blendType='easeIn'),
            ),
        ).start()

    def shatter(self):
        Sequence(
            Wait(1.4),
            Parallel(
                LerpPosInterval(self.posNodeD, 1.0, (0, 0, -10), blendType='easeIn'),
                LerpHprInterval(self.posNodeD, 1.0, (0, 0, 70), blendType='easeIn'),
            ),
            Func(self._fullDestroy),
        ).start()

    def jiggle(self):
        if settings['reduce-battle-effects']:
            return
        if self.currentPhase != 3:
            return
        if self.jiggleSeq:
            self.jiggleSeq.pause()
            self.jiggleSeq = None
        posDist = self.JIGGLE_POS_DIST + (self.JIGGLE_POS_COEFF_DIST * max(0, self.index - 10))
        hprDist = self.JIGGLE_HPR_DIST + (self.JIGGLE_HPR_COEFF_DIST * max(0, self.index - 10))
        def updatePos(_):
            self.posNodeC.setPos(
                PythonUtil.lerp(-posDist, posDist, random.random()),
                0,
                PythonUtil.lerp(-posDist, posDist, random.random()),
            )
            self.posNodeC.setHpr(
                PythonUtil.lerp(-hprDist, hprDist, random.random()),
                PythonUtil.lerp(-hprDist, hprDist, random.random()),
                PythonUtil.lerp(-hprDist, hprDist, random.random()),
            )
        self.jiggleSeq = Sequence(
            LerpFunctionInterval(updatePos, 1.0)
        )
        self.jiggleSeq.loop()

    def setRPM(self, rpm: int):
        self.bump(rpm - self.index)

    def bump(self, delta: int):
        self.index += delta
        if settings['reduce-battle-effects']:
            return
        self.jiggle()
        Sequence(
            LerpPosInterval(
                self.posNodeB, self.BUMP_DURATION,
                pos=(0, 0, 0), startPos=(0, 0, delta * self.BUMP_COEFF),
                blendType='easeOut',
            ),
        ).start()

    def _enter(self):
        seq = Sequence(
            LerpPosInterval(
                self.posNodeA, 0.25,
                pos=(0, 0, 0), startPos=(1.0, 0, 0),
                blendType='easeOut',
            ),
        )
        seq.start()
        if settings['reduce-battle-effects']:
            seq.finish()

    def _exit(self, callback: Optional[Callable[[], None]] = None):
        seq = Sequence(
            LerpPosInterval(
                self.posNodeA, 0.25,
                pos=(1.0, 0, 0), startPos=(0, 0, 0),
                blendType='easeIn',
            ),
            Func(callback) if callback is not None else Wait(0.0),
        )
        seq.start()
        if settings['reduce-battle-effects']:
            seq.finish()


@DirectNotifyCategory()
class ChainsawMeterMarkers(DirectFrame):
    """
    Handles the various arrow logic for the markers.
    """

    @InjectorTarget
    def __init__(self, parent=base.a2dRightCenter, **kw):
        # GUI boilerplate.
        gui = ChainsawMeterGUI.getGui()
        optiondefs = kwargsToOptionDefs(
            pos = (0, 0, 0),
            scale = 1.0,
            relief = None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # Positional node
        self.posNode = GUINode(parent=self, name='markerPosNode')

        # Define objects of this GUI.
        self.panel_markers = DirectFrame(
            parent=self.posNode, relief=None,
            pos=(0, 0, 0), scale=1.0,
            image=gui.find('**/meter_markers'),
            image_scale=UiHelpers.calculateImageScale(256, 1024),
        )
        gui.removeNode()

        # Add main marker
        ChainsawMeterPrimaryArrow(
            parent=self.posNode,
            pos=(-0.22929, 0, 0),
            scale=0.41799,
        )

        # Open event hooks
        self.acceptOnce(ChainsawMeterGUI.getPhaseOneEvent(), self.enterPhaseOne)
        self.acceptOnce(ChainsawMeterGUI.getPhaseTwoEvent(), self.enterPhaseTwo)
        self.acceptOnce(ChainsawMeterGUI.getPhaseThreeEvent(), self.enterPhaseThree)

    def destroy(self):
        self.ignoreAll()
        super().destroy()

    """
    Phase Transitions
    """

    def enterPhaseOne(self):
        self.createMarkers(2, 4, 7, 10)

    def enterPhaseTwo(self):
        self.createMarkers(0, 3, 5, 7)

    def enterPhaseThree(self):
        self.createMarkers(2, 4, 7, 10, jiggle=True)

    """
    Marker Logic
    """

    def createMarkers(self, *indices, jiggle: bool = False):
        """Creates markers at the given indices."""
        for index in indices:
            ChainsawMeterSecondaryArrow(
                parent=self,
                pos=(0.25867, 0, self.getMarkerZPos(index)),
                scale=0.27102,
                index=index,
                jiggle=jiggle,
            )

    @staticmethod
    def getMarkerZPos(index) -> float:
        if index > 10:
            return 1.837
        index = max(0, index)
        return PythonUtil.lerp(
            -1.59349, 1.60494, (index / 10)
        )


@DirectNotifyCategory()
class ChainsawMeterGradient(DirectFrame):
    """
    The gradient backing for the meter.
    """

    TIME_TRANSITION = 2.0

    @InjectorTarget
    def __init__(self, parent=base.a2dRightCenter, **kw):
        # GUI boilerplate.
        gui = ChainsawMeterGUI.getGui()
        optiondefs = kwargsToOptionDefs(
            pos = (0, 0, 0),
            scale = 1.0,
            relief = None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # Positional node
        self.posNode = GUINode(parent=self, name='markerPosNode')

        # Define objects of this GUI.
        self.gradient = DirectFrame(
            parent=self.posNode, relief=None,
            pos=(0, 0, 0), scale=1.0,
            image=gui.find('**/meter_gradient'),
            image_scale=UiHelpers.calculateImageScale(128, 512),
            image_color=(1, 1, 1, 0),
        )
        gui.removeNode()

    def setGradientAlpha(self, a):
        if not self.gradient:
            return
        self.gradient['image_color'] = (1, 1, 1, a)

    def enter(self):
        LerpFunctionInterval(
            self.setGradientAlpha, self.TIME_TRANSITION,
            fromData=0, toData=1,
            blendType='easeInOut',
        ).start()

    def exit(self):
        LerpFunctionInterval(
            self.setGradientAlpha, self.TIME_TRANSITION,
            fromData=1, toData=0,
            blendType='easeInOut',
        ).start()


@DirectNotifyCategory()
class ChainsawMeterPrimaryArrow(DirectFrame):
    """
    The primary arrow for the chainsaw meter.
    """

    MOVE_DURATION = 0.15
    MOVE_XDIST = -0.25

    @InjectorTarget
    def __init__(self, parent=base.a2dRightCenter, **kw):
        # GUI boilerplate.
        gui = ChainsawMeterGUI.getGui()
        optiondefs = kwargsToOptionDefs(
            pos = (0, 0, 0),
            scale = 1.0,
            relief = None,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # State
        self.index = 0

        # Positional node
        self.posNodeA = GUINode(parent=self, name='slidePosNode')
        self.posNodeB = GUINode(parent=self.posNodeA, name='markerPosNode')
        self.posNodeC = GUINode(parent=self.posNodeB, name='markerHprNode')
        self.posNodeD = GUINode(parent=self.posNodeC, name='mainPosNode')
        self.posNodeE = GUINode(parent=self.posNodeD, name='shatterNode')

        # Define objects of this GUI.
        self.arrow = DirectFrame(
            parent=self.posNodeE, relief=None,
            pos=(0, 0, 0), scale=1.0,
            image=gui.find('**/arrow_primary'),
        )
        gui.removeNode()

        # Set position.
        self.setPositionToIndex(instant=True)

        # Run move sequences.
        yDist = 0.00
        xDist = -0.2
        moveSpd = 0.60
        self.posSeq = Sequence(
            LerpPosInterval(
                self.posNodeB, duration=moveSpd,
                pos=(xDist, 0, yDist), startPos=(0, 0, 0),
                blendType='easeOut',
            ),
            LerpPosInterval(
                self.posNodeB, duration=moveSpd,
                pos=(0.0, 0, 0.0),
                blendType='easeIn',
            ),
            LerpPosInterval(
                self.posNodeB, duration=moveSpd,
                pos=(xDist, 0, -yDist),
                blendType='easeOut',
            ),
            LerpPosInterval(
                self.posNodeB, duration=moveSpd,
                pos=(0.0, 0, 0.0),
                blendType='easeIn',
            ),
        )
        self.posSeq.loop()

        # Open event hooks
        self.accept(ChainsawMeterGUI.getRPMDeltaEvent(), self.changeRPMDelta)
        self.accept(ChainsawMeterGUI.setRPMEvent(), self.setRPM)
        self.accept(ChainsawMeterGUI.getShatterEvent(), self.shatter)

    def destroy(self):
        self.ignoreAll()
        self.posSeq.pause()
        self.posSeq = None
        super().destroy()

    """
    Marker positioning
    """

    def setRPM(self, rpm: int):
        self.index = rpm
        self.setPositionToIndex()

    def changeRPMDelta(self, delta: int):
        self.index += delta
        self.setPositionToIndex()

    def setPositionToIndex(self, instant: bool = False):
        seq = Parallel(
            Sequence(
                LerpPosInterval(
                    self.posNodeC, duration=self.MOVE_DURATION / 2,
                    pos=(self.MOVE_XDIST, 0, 0),
                    blendType='easeOut',
                ),
                LerpPosInterval(
                    self.posNodeC, duration=self.MOVE_DURATION / 2,
                    pos=(0.0, 0, 0),
                    blendType='easeIn',
                ),
            ),
            LerpPosInterval(
                self.posNodeD, duration=self.MOVE_DURATION,
                pos=(0, 0, ChainsawMeterMarkers.getMarkerZPos(self.index) / self['scale']),
                blendType='easeOut',
            )
        )
        seq.start()
        if instant:
            seq.finish()

    """
    Transitions
    """

    def shatter(self):
        Sequence(
            ProjectileInterval(
                self.posNodeE, startPos=(0, 0, 0), endPos=(-0.5, 0, -10),
                duration=0.8,
            )
        ).start()

    def _enter(self):
        Sequence(
            LerpPosInterval(
                self.posNodeA, 0.25,
                pos=(0, 0, 0), startPos=(1.0, 0, 0),
                blendType='easeOut',
            ),
        ).start()


@DirectNotifyCategory()
class ChainsawMeterSecondaryArrow(DirectFrame):
    """
    Handles the various arrow logic for the markers.
    """

    @InjectorTarget
    def __init__(self, parent=base.a2dRightCenter, **kw):
        # GUI boilerplate.
        gui = ChainsawMeterGUI.getGui()
        optiondefs = kwargsToOptionDefs(
            pos = (0, 0, 0),
            scale = 1.0,
            relief = None,
            index = 0,
            jiggle = 0,
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # Positional node
        self.posNodeA = GUINode(parent=self,          name='slidePosNode')
        self.posNodeB = GUINode(parent=self.posNodeA, name='markerPosNode')
        self.posNodeC = GUINode(parent=self.posNodeB, name='markerHprNode')
        self.posNodeZ = GUINode(parent=self.posNodeC, name='shatterNode')
        self.posNodeD = GUINode(parent=self.posNodeZ, name='jiggleNode')

        # Define objects of this GUI.
        self.arrow = DirectFrame(
            parent=self.posNodeD, relief=None,
            pos=(0, 0, 0), scale=1.0,
            image=gui.find('**/arrow_secondary'),
        )
        gui.removeNode()

        # Open event hooks
        self.acceptOnce(ChainsawMeterGUI.getPhaseOneEvent(), self.destroy)
        self.acceptOnce(ChainsawMeterGUI.getPhaseTwoEvent(), self.destroy)
        self.acceptOnce(ChainsawMeterGUI.getPhaseThreeEvent(), self.destroy)
        self.accept(ChainsawMeterGUI.getShatterEvent(), self.shatter)

        # Run move sequences.
        yDist = 0.02
        xDist = 0.03
        moveSpd = 1.60
        turnDist = 0.5
        turnSpd = 4.00
        jiggleDist = 0.015
        self.posSeq = Sequence(
            LerpPosInterval(
                self.posNodeB, duration=moveSpd,
                pos=(xDist, 0, yDist), startPos=(0, 0, 0),
                blendType='easeOut',
            ),
            LerpPosInterval(
                self.posNodeB, duration=moveSpd,
                pos=(0.0, 0, 0.0),
                blendType='easeIn',
            ),
            LerpPosInterval(
                self.posNodeB, duration=moveSpd,
                pos=(xDist, 0, -yDist),
                blendType='easeOut',
            ),
            LerpPosInterval(
                self.posNodeB, duration=moveSpd,
                pos=(0.0, 0, 0.0),
                blendType='easeIn',
            ),
        )
        self.hprSeq = Sequence(
            LerpHprInterval(
                self.posNodeC, duration=turnSpd,
                hpr=(0, 0, turnDist), startHpr=(0, 0, -turnDist),
                blendType='easeInOut',
            ),
            LerpHprInterval(
                self.posNodeC, duration=turnSpd,
                hpr=(0, 0, -turnDist), startHpr=(0, 0, turnDist),
                blendType='easeInOut',
            ),
        )
        self.posSeq.loop()
        self.hprSeq.loop()
        self.posSeq.setT((self['index'] / 10) * self.posSeq.getDuration())
        self.hprSeq.setT((self['index'] / 10) * self.hprSeq.getDuration())

        # Do jiggle if we can.
        self.jiggleSeq = None
        if self['jiggle'] and not settings['reduce-battle-effects']:
            def updatePos(_):
                self.posNodeD.setPos(
                    PythonUtil.lerp(-jiggleDist, jiggleDist, random.random()),
                    0,
                    PythonUtil.lerp(-jiggleDist, jiggleDist, random.random()),
                )
            self.jiggleSeq = Sequence(
                LerpFunctionInterval(updatePos, 1.0)
            )
            self.jiggleSeq.loop()

        # Do enter transition.
        self._enter()

    def destroy(self):
        self.ignoreAll()
        self._exit(callback=self._fullDestroy)

    def _fullDestroy(self):
        self.posSeq.pause()
        self.hprSeq.pause()
        if self.jiggleSeq:
            self.jiggleSeq.pause()
        self.posSeq = None
        self.hprSeq = None
        self.jiggleSeq = None
        super().destroy()

    """
    Transitions
    """

    def shatter(self):
        fallMult = (((self['index'] // 2) % 2) - 0.5) * 2
        Sequence(
            Wait(0.15 * (self['index'] // 2)),
            ProjectileInterval(
                self.posNodeZ, startPos=(0, 0, 0), endPos=(0.9 * fallMult, 0, -27),
                duration=1.2,
            )
        ).start()

    def _enter(self):
        Sequence(
            PosInterval(
                self.posNodeA, (3.0, 0, 0),
            ),
            Wait(0.2),
            LerpPosInterval(
                self.posNodeA, duration=0.2,
                pos=(0, 0, 0), startPos=(3.0, 0, 0),
                blendType='easeOut',
            ),
        ).start()

    def _exit(self, callback: Optional[Callable[[], None]] = None):
        Sequence(
            LerpPosInterval(
                self.posNodeA, duration=0.2,
                pos=(3.0, 0, 0), startPos=(0, 0, 0),
                blendType='easeIn',
            ),
            Func(callback) if callback is not None else Wait(0.0),
        ).start()


if __name__ == "__main__":
    gui = ChainsawMeterGUI(
        # any kwargs go here
    )
    GUITemplateSliders(
        gui,
        'pos', 'scale'
    )
    def move(delta):
        messenger.send(ChainsawMeterGUI.getRPMDeltaEvent(), [delta])
    def shatter():
        messenger.send(ChainsawMeterGUI.getShatterEvent())
    def progress():
        if not base.ChainsawMeterGUI:
            ChainsawMeterGUI()
        else:
            if base.ChainsawMeterGUI.currentPhase == 1:
                messenger.send(ChainsawMeterGUI.getPhaseTwoEvent())
            elif base.ChainsawMeterGUI.currentPhase == 2:
                messenger.send(ChainsawMeterGUI.getPhaseThreeEvent())
            elif base.ChainsawMeterGUI.currentPhase == 3:
                messenger.send(ChainsawMeterGUI.getDestroyEvent())
    base.accept('x', progress)
    base.accept('c', shatter)
    base.accept('q', move, [1])
    base.accept('a', move, [-1])
    base.accept('w', move, [3])
    base.accept('s', move, [-3])
    base.accept('e', move, [8])
    base.accept('d', move, [-8])
    base.run()
