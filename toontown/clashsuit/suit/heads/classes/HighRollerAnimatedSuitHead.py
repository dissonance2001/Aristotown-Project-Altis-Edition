if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()


from toontown.clashsuit.suit.heads.AnimatedSuitHead import *
from toontown.clashsuit.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from direct.interval.IntervalGlobal import *
from typing import Optional


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName=('hroller', 'hrollerc'))
class HighRollerAnimatedSuitHead(AnimatedSuitHead):
    """
    High Roller has a bug with his neutral animation loop because of
    animation blending. So, we disable it for the first frame only.
    """

    def __init__(self, *args, **kwargs):
        self.fakeNeutral: Optional[Parallel] = None
        super().__init__(*args, **kwargs)

    def cleanup(self):
        self.stopFakeNeutral()
        super().cleanup()

    def play(self, animName, partName=None, fromFrame=None, toFrame=None):
        self.stopFakeNeutral()
        super().play(animName, partName, fromFrame, toFrame)

    def loop(self, animName, restart=1, partName=None, fromFrame=None, toFrame=None):
        self.stopFakeNeutral()
        if animName in ('neutral', 'neutral-hurt', 'neutral-lured'):
            self.startFakeNeutral(animName)
        else:
            super().loop(animName, restart, partName, fromFrame, toFrame)

    def startFakeNeutral(self, animName='neutral'):
        self.stopFakeNeutral()
        self.fakeNeutral = Parallel(
            self.actorInterval(animName),
            Sequence(
                Func(self.setBlend, frameBlend=base.wantSmoothAnims),
                Wait(((self.getDuration(animName) * 24) - 1) / 24),
                Func(self.setBlend, frameBlend=False)
            ),
        )
        self.fakeNeutral.loop()

    def stopFakeNeutral(self):
        if self.fakeNeutral:
            self.fakeNeutral.pause()
            self.fakeNeutral = None


if __name__ == "__main__":
    from toontown.clashsuit.suit import Suit, SuitDNA
    suit = Suit.Suit()
    suitDNA = SuitDNA.SuitDNA()
    suitDNA.newSuit('hroller')
    suit.setDNA(suitDNA)
    suit.loop('neutral')
    suit.reparentTo(render)

    base.setBackgroundColor(1, 1, 1, 1)
    suit.setPos(0.3813, 5.0, -8.3617)
    suit.setHpr(74.51, -9.1503, 9.1504)
    suit.setScale(1, 1, 1)

    from toontown.chat.ui.speedchat.ColorSpace import hsv2rgb

    def awsome(t):
        col = list(hsv2rgb(t * 360, 0.3, 0.9)) + [1.0]
        base.setBackgroundColor(*col)

    Sequence(
        LerpFunctionInterval(
            awsome, duration=10.0,
        )
    ).loop()

    def asdf(*_):
        suit.specialHead.stop()
        suit.specialHead.play('neutral')

    suit.accept('a', asdf)

    # from toontown.utils.InjectorHelper import setNodeAdjuster
    # setNodeAdjuster(suit)
    base.run()
