from toontown.toon.accessories.ToonParticleAccessory import ToonParticleAccessory
from toontown.toon.accessories.hats.HatFreezeHead import HatFreezeHead
from direct.interval.IntervalGlobal import *


class StormCloudHat(HatFreezeHead, ToonParticleAccessory):
    """
    depression :(
    """

    ParticleName = 'wideliquidate'
    stopBlink       = False
    stopStareAt     = False
    stopLookAround  = False
    stopHeadPose    = False
    overwriteEyes   = True
    overwriteMuzzle = False

    bobDist = 0.06
    bobSpeed = 1.7

    def load(self):
        super().load()

    @classmethod
    def modifyPreview(cls, geom):
        """
        Fixes (some) weird rendering issues with the cloud while previewing in book.
        """
        geom.setTwoSided(1)

    def _positionAccessory(self):
        self.accessoryGeom.setPosHpr(
            0.0643, 0.0478, 0.82, 25.4497, 0.0, 342.6479
        )
        self.accessoryGeom.setScale(2.016)

    def _attachAccessory(self):
        baseNode = self.toon.attachNewNode('accessoryBaseNode')
        baseNode.setZ(self.toon.getHeight())

        # Add bobbing
        bobNode = baseNode.attachNewNode('bobNode')
        Sequence(
            LerpPosInterval(
                bobNode, self.bobSpeed,
                startPos=(0, 0, 0), pos=(0, 0, self.bobDist),
                blendType='easeOut',
            ),
            LerpPosInterval(
                bobNode, self.bobSpeed,
                startPos=(0, 0, self.bobDist), pos=(0, 0, 0),
                blendType='easeIn',
            ),
            LerpPosInterval(
                bobNode, self.bobSpeed,
                startPos=(0, 0, 0), pos=(0, 0, -self.bobDist),
                blendType='easeOut',
            ),
            LerpPosInterval(
                bobNode, self.bobSpeed,
                startPos=(0, 0, -self.bobDist), pos=(0, 0, 0),
                blendType='easeIn',
            ),
        ).loop()

        # Setup nodes and geom
        self.accessoryNodes.append(bobNode)
        self.accessoryGeom.reparentTo(bobNode)

    def unload(self):
        super().unload()
