from panda3d.core import Vec3, BillboardEffect, Point3

from toontown.toon.accessories.glasses.GlassesHideEyes import GlassesHideEyes


class PirateGhostMask(GlassesHideEyes):
    """
    Ghost Pirate mask.
    Pupils are billboarded and need to be adjusted in render2d to look proper. Also hides the eyes.
    """

    def load(self):
        super().load()

    @classmethod
    def modifyPreview(cls, geom):
        pupilBillboard = BillboardEffect.make(
            up_vector = Vec3(0, 0, 1),
            eye_relative = True,
            axial_rotate = False,
            offset = 0.0,
            look_at = base.cam2d,
            look_at_point = Point3(0, 0, 0)
        )
        for pupilNode in (geom.find("**/pupil_left"), geom.find("**/pupil_right")):
            pupilNode.setEffect(pupilBillboard)
