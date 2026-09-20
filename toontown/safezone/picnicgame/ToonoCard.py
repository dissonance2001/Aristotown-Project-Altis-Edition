from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *


class ToonoCard(DirectButton):

    def __init__(self, cardType: int, cardNumber: int, index: int, geom) -> None:
        DirectButton.__init__(
            self, parent = aspect2d, relief = None, geom = geom,
            geom_pos = (0, 0, 0), pos = (-0.5, 0.0, 0.0), geom_scale = (.4, .4, .6),
            command = self.handleCardClick, frameSize = (-.2, .2, -1, .2),
            state = DGG.DISABLED, sortOrder = 5
        )
        self.initialiseoptions(ToonoCard)
        self.hide()

        self.cardType = cardType
        self.cardNumber = cardNumber
        self.index = index

        self.hoverEnabled: bool = False

        self._seq: LerpColorScaleInterval = None
        self._hoverSeq: LerpPosInterval = None
        self._flashSeq: Sequence = None

        self.enabledColor = Vec4(1, 1, 1, 1)
        self.disabledColor = Vec4(0.6, 0.6, 0.6, 1.0)
        self.flashColor = Vec4(0.5, 0.5, 0.5, 1)

        self.enterHoverZ: int = 0
        self.exitHoverZ: int = 0

    def destroy(self) -> None:
        self.finishHoverSeq()
        self.finishSeq()
        self.stopFlash()

        DirectButton.destroy(self)

    def handleCardClick(self) -> None:
        # Don't do anything if the card is disabled.
        if hasattr(self, "disabled") and self.disabled:
            return

        messenger.send("toonoCardClicked", [self.index])

    def disableButton(self) -> None:
        self["state"] = DGG.DISABLED

    def enableHover(self) -> None:
        if self.hoverEnabled:
            return

        self.enterHoverZ = self.getZ() + 0.2
        self.exitHoverZ = self.getZ()

        self.hoverEnabled = True
        self.bind(DGG.ENTER, self.enterHover)
        self.bind(DGG.EXIT, self.exitHover)

    def enterHover(self, event) -> None:
        self.pauseHoverSeq()

        self._hoverSeq = LerpPosInterval(self, 0.2, Vec3(self.getX(), self.getY(), self.enterHoverZ), self.getPos())
        self._hoverSeq.start()

    def exitHover(self, event) -> None:
        self.pauseHoverSeq()

        self._hoverSeq = LerpPosInterval(self, 0.2, Vec3(self.getX(), self.getY(), self.exitHoverZ), self.getPos())
        self._hoverSeq.start()

    def pauseHoverSeq(self) -> None:
        if self._hoverSeq is not None:
            self._hoverSeq.pause()

    def finishHoverSeq(self) -> None:
        if self._hoverSeq is not None:
            self._hoverSeq.finish()
            self._hoverSeq = None

    def enableCard(self, animate: bool) -> None:
        """Animate the button being enabled.
        """
        if hasattr(self, "disabled") and not self.disabled:
            return
        elif not hasattr(self, "disabled"):
            # This is the first time we're enabling the card, set the state to
            # normal.
            # We're letting the card's state be normal from now on, even when
            # disabled to allow for the hovering to work. This is fine, since
            # the button function won't trigger if the button is disabled
            # anyway.
            self["state"] = DGG.NORMAL

        self.disabled = False

        self.finishSeq()

        if animate:
            self._seq = LerpColorScaleInterval(self, 0.2, self.enabledColor, self.disabledColor)
            self._seq.start()

    def disableCard(self) -> None:
        """Animate the card being disabled.
        """
        if hasattr(self, "disabled") and self.disabled:
            return
        elif not hasattr(self, "disabled"):
            # This is the first time we're disabling the card, set the state to
            # normal.
            # We're letting the card's state be normal from now on, regardless
            # of the state to allow for the hovering to work. This is fine
            # since the button function won't trigger if the button is disabled
            # anyway.
            self["state"] = DGG.NORMAL

        self.disabled = True

        self.finishSeq()

        self._seq = LerpColorScaleInterval(self, 0.2, self.disabledColor)
        self._seq.start()

    def finishSeq(self) -> None:
        if self._seq is not None:
            self._seq.finish()
            self._seq = None

    def startFlash(self) -> None:
        self.stopFlash()

        self._flashSeq = Sequence(
            LerpColorScaleInterval(self, 1, self.enabledColor, blendType = "easeInOut"),
            LerpColorScaleInterval(self, 1, self.flashColor, blendType = "easeInOut"),
        )
        self._flashSeq.loop()

    def stopFlash(self) -> None:
        if self._flashSeq is not None:
            self._flashSeq.finish()
            self._flashSeq = None

    def untintCard(self) -> None:
        if hasattr(self, "disabled"):
            if self.disabled:
                self.setColorScale(self.disabledColor)
            else:
                self.setColorScale(self.enabledColor)
