from direct.gui.DirectGui import DirectFrame
from direct.interval.IntervalGlobal import LerpPosInterval


class ChainsawMeterGUI(DirectFrame):
    """Python-2-compatible port of Clash's Chainsaw RPM meter."""

    def __init__(self, parent=None):
        if parent is None:
            parent = base.a2dRightCenter

        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            pos=(-0.12933, 0, 0),
            scale=0.32981)

        self.currentPhase = 1
        self.rpm = 10
        self.secondaryArrows = []
        self.primaryMove = None
        self.gui = loader.loadModel('phase_6/models/gui/chainsaw_meter_gui')

        self.baseFrame = DirectFrame(
            parent=self,
            relief=None,
            image=self.gui.find('**/meter_base'),
            image_scale=(1.0, 1.0, 4.0))
        self.shadowFrame = DirectFrame(
            parent=self,
            relief=None,
            image=self.gui.find('**/meter_shadow'),
            image_scale=(1.0, 1.0, 4.0))
        self.markerFrame = DirectFrame(
            parent=self,
            relief=None,
            image=self.gui.find('**/meter_markers'),
            image_scale=(1.0, 1.0, 4.0))

        self.primaryArrow = DirectFrame(
            parent=self,
            relief=None,
            image=self.gui.find('**/arrow_primary'),
            pos=(-0.22929, 0, self.getMarkerZPos(0)),
            scale=0.41799)

        self._buildPhaseMarkers()
        self.setRPM(10, instant=True)

    @staticmethod
    def getMarkerZPos(index):
        if index > 10:
            return 1.837
        index = max(0, index)
        return -1.59349 + ((1.60494 - -1.59349) * (float(index) / 10.0))

    def _clearPhaseMarkers(self):
        for arrow in self.secondaryArrows:
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
            arrow = DirectFrame(
                parent=self,
                relief=None,
                image=self.gui.find('**/arrow_secondary'),
                pos=(0.25867, 0, self.getMarkerZPos(index)),
                scale=0.27102)
            self.secondaryArrows.append(arrow)

    def setPhase(self, phase):
        phase = max(1, min(3, int(phase)))
        if self.currentPhase == phase:
            return
        self.currentPhase = phase
        self._buildPhaseMarkers()

    def setRPM(self, rpm, instant=False):
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
            self.primaryArrow.setPos(*target)
            return

        self.primaryMove = LerpPosInterval(
            self.primaryArrow,
            0.15,
            target,
            blendType='easeOut')
        self.primaryMove.start()

    def destroy(self):
        if self.primaryMove:
            try:
                self.primaryMove.pause()
            except:
                pass
            self.primaryMove = None
        self._clearPhaseMarkers()
        if self.gui and not self.gui.isEmpty():
            self.gui.removeNode()
        self.gui = None
        DirectFrame.destroy(self)
