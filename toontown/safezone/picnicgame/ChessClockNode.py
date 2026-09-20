from direct.gui.DirectLabel import DirectLabel
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.LerpInterval import LerpColorScaleInterval, LerpScaleInterval
from direct.interval.MetaInterval import Sequence, Parallel
from panda3d.core import Vec4, TextNode

from toontown.safezone.picnicgame.BoardGameGlobals import PLAYER_TIME, getToonPanels
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownTimer import ToontownTimer


class ChessClockNode(ToontownTimer):

    def __init__(self, avId: int) -> None:
        super().__init__()
        self.initialiseoptions(ChessClockNode)

        self.avId = avId

        self.clockTrack: Sequence | None = None
        self.timeLeft: float = 0.0

        for panel in getToonPanels():
            if panel.obj.doId == avId:
                self.reparentTo(panel.flipAnchor)
                break

        self.setPos(0.14, 0, 0)
        self.setScale(0.3)
        self.setTime(PLAYER_TIME)

    def destroy(self) -> None:
        self.finishClockTrack()
        super().destroy()

    def setTimeLeft(self, timeLeft: float, animated: bool = False) -> None:
        self.timeLeft = timeLeft
        self.startClock(animated)

    def startClock(self, animated: bool = False) -> None:
        self.stop()

        timeLeft = self.timeLeft - globalClock.getFrameTime()

        oldTime = self.currentTime
        task = self.countdown(timeLeft, lambda: self.stop())
        task.avId = self.avId

        timedAdded = int(timeLeft - oldTime)

        if not animated or timedAdded <= 0:
            return

        self.finishClockTrack()

        # Create a local label that will be destroyed upon finishing
        # the clock sequence.
        label = DirectLabel(
            parent=self, relief=None,
            text=f"+{timedAdded}", text_scale=0.4,
            text_fg=(1, 1, 1, 1), text_font=ToontownGlobals.getSignFont(),
            text_shadow=(0, 0, 0, 1), text_align=TextNode.ACenter,
            pos=(0.7, 0, -0.15),
        )

        clockScale = self.getScale()

        self.clockTrack = Parallel(
            # Pop effect for the timer to indicate time being added.
            Sequence(
                LerpScaleInterval(self, 0.1, clockScale * 1.2, clockScale, blendType="easeInOut"),
                LerpScaleInterval(self, 0.1, clockScale, clockScale * 1.2, blendType="easeInOut"),
            ),
            # Pop text above the timer displaying the amount of time added.
            Sequence(
                Func(label.show),
                Wait(1.85),
                LerpColorScaleInterval(label, 0.1, Vec4(1, 1, 1, 0)),
                Func(label.destroy)
            )
        )
        self.clockTrack.start()

    def finishClockTrack(self) -> None:
        if self.clockTrack is not None:
            self.clockTrack.finish()
            self.clockTrack = None
