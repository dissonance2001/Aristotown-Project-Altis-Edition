from __future__ import absolute_import
import random

from direct.gui.DirectGui import DirectFrame
from direct.interval.IntervalGlobal import LerpFunctionInterval, LerpHprInterval, LerpPosInterval, Parallel, Sequence


class ChainsawMeterGUI(DirectFrame):
    BUMP_DURATION = 0.11
    BUMP_COEFF = 0.015

    def __init__(self, parent=None):
        if parent is None:
            parent = base.a2dRightCenter

        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            pos=(-0.12933, 0, 0),
            scale=0.32981)

        self.currentPhase = 0
        self.rpm = 10
        self.secondaryArrows = []
        self.primaryMove = None
        self.primaryPointerMove = None
        self.bumpMove = None
        self.phaseMove = None
        self.topFade = None
        self.bottomFade = None
        self.jiggleTaskName = 'ChainsawMeterJiggle-%s' % id(self)
        self.gui = loader.loadModel('phase_6/models/gui/chainsaw_meter_gui')

        self.bumpRoot = self.attachNewNode('chainsawMeterBump')
        self.jiggleRoot = self.bumpRoot.attachNewNode('chainsawMeterJiggle')
        self.phaseRoot = self.jiggleRoot.attachNewNode('chainsawMeterPhase')

        self.baseFrame = DirectFrame(
            parent=self.phaseRoot,
            relief=None,
            image=self.gui.find('**/meter_base'),
            image_scale=(1.0, 1.0, 4.0))
        self.gradientTop = DirectFrame(
            parent=self.phaseRoot,
            relief=None,
            image=self.gui.find('**/meter_gradient'),
            image_scale=(1.0, 1.0, 4.0),
            image_color=(1, 1, 1, 0),
            pos=(0.0128, 0, 0.85468),
            scale=0.50408)
        self.gradientBottom = DirectFrame(
            parent=self.phaseRoot,
            relief=None,
            image=self.gui.find('**/meter_gradient'),
            image_scale=(1.0, 1.0, 4.0),
            image_color=(1, 1, 1, 0),
            pos=(0.01748, 0, -0.84532),
            hpr=(0, 0, 180),
            scale=0.50408)
        self.shadowFrame = DirectFrame(
            parent=self.phaseRoot,
            relief=None,
            image=self.gui.find('**/meter_shadow'),
            image_scale=(1.0, 1.0, 4.0))
        self.markerFrame = DirectFrame(
            parent=self.phaseRoot,
            relief=None,
            image=self.gui.find('**/meter_markers'),
            image_scale=(1.0, 1.0, 4.0))

        self.primaryArrowRoot = self.phaseRoot.attachNewNode('chainsawMeterPrimaryArrow')
        self.primaryArrowRoot.setPos(-0.22929, 0, self.getMarkerZPos(0))
        self.primaryArrow = DirectFrame(
            parent=self.primaryArrowRoot,
            relief=None,
            image=self.gui.find('**/arrow_primary'),
            scale=0.41799)
        self.primaryPointerMove = Sequence(
            LerpPosInterval(
                self.primaryArrow, 0.62, (0.05, 0, 0),
                startPos=(-0.035, 0, 0), blendType='easeInOut'),
            LerpPosInterval(
                self.primaryArrow, 0.62, (-0.035, 0, 0),
                startPos=(0.05, 0, 0), blendType='easeInOut'))
        self.primaryPointerMove.loop()

        self.setPhase(1, instant=True)
        self.setRPM(10, instant=True)

    @staticmethod
    def getMarkerZPos(index):
        if index > 10:
            return 1.837
        index = max(0, index)
        return -1.59349 + ((1.60494 - -1.59349) * (float(index) / 10.0))

    def _clearPhaseMarkers(self):
        for entry in self.secondaryArrows:
            arrow, hprTrack = entry
            try:
                hprTrack.pause()
            except:
                pass
            try:
                arrow.destroy()
            except:
                pass
        self.secondaryArrows = []

    def _buildPhaseMarkers(self):
        self._clearPhaseMarkers()
        if self.currentPhase == 2:
            indices = (0, 3, 5, 7)
        else:
            indices = (2, 4, 7, 10)

        for index in indices:
            basePos = (0.25867, 0, self.getMarkerZPos(index))
            arrow = DirectFrame(
                parent=self.phaseRoot,
                relief=None,
                image=self.gui.find('**/arrow_secondary'),
                pos=basePos,
                scale=0.27102)
            hprTrack = Sequence(
                LerpHprInterval(
                    arrow, 0.18, (0, 0, 0.4),
                    startHpr=(0, 0, -0.4),
                    blendType='easeInOut'),
                LerpHprInterval(
                    arrow, 0.18, (0, 0, -0.4),
                    startHpr=(0, 0, 0.4),
                    blendType='easeInOut'))
            hprTrack.loop()
            try:
                hprTrack.setT((float(index) / 10.0) * hprTrack.getDuration())
            except:
                pass
            self.secondaryArrows.append((arrow, hprTrack))

    def _setTopAlpha(self, alpha):
        if self.gradientTop:
            self.gradientTop['image_color'] = (1, 1, 1, alpha)

    def _setBottomAlpha(self, alpha):
        if self.gradientBottom:
            self.gradientBottom['image_color'] = (1, 1, 1, alpha)

    def _fadeGradients(self, top, bottom, instant=False):
        for name in ('topFade', 'bottomFade'):
            track = getattr(self, name)
            if track:
                try:
                    track.pause()
                except:
                    pass
                setattr(self, name, None)

        try:
            oldTop = self.gradientTop['image_color'][3]
        except:
            oldTop = 0.0
        try:
            oldBottom = self.gradientBottom['image_color'][3]
        except:
            oldBottom = 0.0

        if instant:
            self._setTopAlpha(top)
            self._setBottomAlpha(bottom)
            return

        self.topFade = LerpFunctionInterval(
            self._setTopAlpha, 2.0,
            fromData=oldTop, toData=top,
            blendType='easeInOut')
        self.bottomFade = LerpFunctionInterval(
            self._setBottomAlpha, 2.0,
            fromData=oldBottom, toData=bottom,
            blendType='easeInOut')
        self.topFade.start()
        self.bottomFade.start()

    def _playPhaseTransition(self):
        if self.phaseMove:
            try:
                self.phaseMove.pause()
            except:
                pass
        self.phaseMove = Sequence(
            LerpPosInterval(
                self.phaseRoot, 0.25, (-0.6, 0, 0),
                blendType='easeOut'),
            LerpPosInterval(
                self.phaseRoot, 0.25, (0, 0, 0),
                blendType='easeIn'))
        self.phaseMove.start()

    def setPhase(self, phase, instant=False):
        phase = max(1, min(3, int(phase)))
        changed = self.currentPhase != phase
        self.currentPhase = phase
        if changed:
            self._buildPhaseMarkers()
            if not instant:
                self._playPhaseTransition()
        if changed or instant:
            if phase == 2:
                self._fadeGradients(0.0, 1.0, instant=instant)
            else:
                self._fadeGradients(1.0, 0.0, instant=instant)
        self._refreshJiggle()

    def _bump(self, delta):
        if not delta:
            return
        if self.bumpMove:
            try:
                self.bumpMove.pause()
            except:
                pass
        self.bumpMove = LerpPosInterval(
            self.bumpRoot,
            self.BUMP_DURATION,
            (0, 0, 0),
            startPos=(0, 0, float(delta) * self.BUMP_COEFF),
            blendType='easeOut')
        self.bumpMove.start()

    def _jiggleSeverity(self):
        index = self.rpm - 10
        if self.currentPhase == 2:
            if index > 2:
                return 0.0
            return min(1.0, float(3 - index) / 3.0)
        if index < 8:
            return 0.0
        return min(1.0, float(index - 7) / 3.0)

    def _jiggleTask(self, task):
        severity = self._jiggleSeverity()
        if severity <= 0.0:
            self.jiggleRoot.setPosHpr(0, 0, 0, 0, 0, 0)
            return task.done
        posDist = 0.002 + (0.004 * severity)
        hprDist = 0.05 + (0.15 * severity)
        self.jiggleRoot.setPos(
            random.uniform(-posDist, posDist),
            0,
            random.uniform(-posDist, posDist))
        self.jiggleRoot.setHpr(
            random.uniform(-hprDist, hprDist),
            random.uniform(-hprDist, hprDist),
            random.uniform(-hprDist, hprDist))
        return task.cont

    def _refreshJiggle(self):
        taskMgr.remove(self.jiggleTaskName)
        self.jiggleRoot.setPosHpr(0, 0, 0, 0, 0, 0)
        if self._jiggleSeverity() > 0.0:
            taskMgr.add(self._jiggleTask, self.jiggleTaskName)

    def setRPM(self, rpm, instant=False):
        oldRPM = self.rpm
        self.rpm = max(10, min(30, int(rpm)))
        index = self.rpm - 10
        target = (-0.22929, 0, self.getMarkerZPos(index))

        if self.primaryMove:
            try:
                self.primaryMove.pause()
            except:
                pass
            self.primaryMove = None

        if instant:
            self.primaryArrowRoot.setPos(*target)
            self._refreshJiggle()
            return

        self.primaryMove = LerpPosInterval(
            self.primaryArrowRoot,
            0.15,
            target,
            blendType='easeOut')
        self.primaryMove.start()
        self._bump(self.rpm - oldRPM)
        self._refreshJiggle()

    def destroy(self):
        taskMgr.remove(self.jiggleTaskName)
        for name in ('primaryMove', 'primaryPointerMove', 'bumpMove', 'phaseMove', 'topFade', 'bottomFade'):
            track = getattr(self, name, None)
            if track:
                try:
                    track.pause()
                except:
                    pass
                setattr(self, name, None)
        self._clearPhaseMarkers()
        if self.gui and not self.gui.isEmpty():
            self.gui.removeNode()
        self.gui = None
        DirectFrame.destroy(self)
