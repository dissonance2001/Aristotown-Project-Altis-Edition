from direct.interval.IntervalGlobal import *

from toontown.toon.accessories.ToonAccessory import ToonAccessory


class ClashBirthdayHat(ToonAccessory):
    def __init__(self, *args):
        super().__init__(*args)
        self.sequence = None

    def start(self):
        if self.sequence:
            return

        self.sequence = Sequence(
            Parallel(
                self.accessoryGeom.hprInterval(
                    2,
                    (360, self.accessoryGeom.getHpr()[1], self.accessoryGeom.getHpr()[2])
                ),
                Sequence(
                    self.accessoryGeom.posInterval(
                        1,
                        (self.accessoryGeom.getPos()[0], self.accessoryGeom.getPos()[1],
                         self.accessoryGeom.getPos()[2] - 0.15)
                    ),
                    self.accessoryGeom.posInterval(
                        1,
                        (self.accessoryGeom.getPos()[0], self.accessoryGeom.getPos()[1],
                         self.accessoryGeom.getPos()[2])
                    )
                )
            )
        )
        self.sequence.loop()

    def stop(self):
        if self.sequence:
            self.sequence.finish()
            self.sequence = None
