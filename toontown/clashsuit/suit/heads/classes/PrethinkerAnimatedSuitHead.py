from direct.interval.IntervalGlobal import *
from toontown.suit.heads.AnimatedSuitHead import *
from toontown.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from panda3d.core import Point3, LVecBase4f


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='prethink')
class PrethinkerAnimatedSuitHead(AnimatedSuitHead):
    durationA = 0.8
    durationB = 0.3
    scaleTop = 1.00
    scaleLow = 0.96

    scaleShrink = 0.14
    durationShrink = 4.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.brain = self.find('**/brain')
        self.brainSeq = None
        self.setBrainPulseSpeed()

    def cleanup(self):
        self.cleanupBrainSeq()
        self.brain = None
        super().cleanup()

    def cleanupBrainSeq(self):
        if self.brainSeq:
            self.brainSeq.finish()
            self.brainSeq = None

    """
    Sequence funnies
    """

    def setBrainPulseSpeed(self, speed=1.0):
        self.cleanupBrainSeq()
        self.brainSeq = Sequence(
            LerpScaleInterval(self.brain, self.durationB * (1 / speed), startScale=self.scaleTop, scale=self.scaleLow, blendType='easeOut'),
            LerpScaleInterval(self.brain, self.durationB * (1 / speed), startScale=self.scaleTop, scale=self.scaleLow, blendType='easeOut'),
            Wait(self.durationA * (1 / speed))
        )
        self.brainSeq.loop()

    def makeBrainRedTrack(self):
        return LerpColorScaleInterval(self.brain, 1.0, LVecBase4f(1.0, 0.5, 0.5, 1.0))

    def makeShrink(self):
        brainScale = self.brain.getScale()
        self.cleanupBrainSeq()
        self.brainSeq = LerpScaleInterval(self.brain, self.durationShrink, startScale=brainScale, scale=self.scaleShrink, blendType='easeInOut')
        self.brainSeq.start()

    def doBrainBlast(self):
        self.cleanupBrainSeq()
        brainDisappearTrack = Sequence(LerpScaleInterval(self.brain, 0.6, scale=0.01, blendType='easeInOut'), Func(self.brain.detachNode))
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        deathSoundTrack = Sequence(SoundInterval(deathSound, volume=1.0, node=self))
        explosion = loader.loadModel('phase_3.5/models/props/explosion.bam')
        explosion.setBillboardPointEye()
        explosion.setDepthWrite(False)
        explosionPoint = Point3(0, 2, 2.7)
        explosion.setPos(explosionPoint)
        explosion.reparentTo(self)
        explosionTrack = Sequence(Func(explosion.setScale, 2.0), Wait(0.6), Func(explosion.removeNode))
        colorScaleTrack = Sequence(
            Wait(0.3), Func(self.setColorScale, .36, .36, .301, 1.0)
        )
        self.brainSeq = Parallel(brainDisappearTrack, deathSoundTrack, explosionTrack, colorScaleTrack)
        self.brainSeq.start()
