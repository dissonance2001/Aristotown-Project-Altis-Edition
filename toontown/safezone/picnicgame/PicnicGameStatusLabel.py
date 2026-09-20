from direct.gui.DirectLabel import DirectLabel
from direct.interval.FunctionInterval import Wait
from direct.interval.LerpInterval import LerpColorScaleInterval
from direct.interval.MetaInterval import Sequence


class PicnicGameStatusLabel(DirectLabel):

    def __init__(self, avId: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.initialiseoptions(PicnicGameStatusLabel)

        self.__seq: Sequence | None = None

        self.accept(f"AnimateStatusLabel-{avId}", self.animate)

    def destroy(self) -> None:
        self.ignoreAll()
        self.finish()
        super().destroy()

    def finish(self) -> None:
        if self.__seq is not None:
            self.__seq.finish()
            self.__seq = None

    def animate(self, text: str) -> None:
        self.finish()

        self["text"] = text

        self.__seq = Sequence(
            LerpColorScaleInterval(self, 0.1, (1, 1, 1, 1)),
            Wait(3.5),
            LerpColorScaleInterval(self, 1.0, (1, 1, 1, 0)),
        )
        self.__seq.start()
