# You'd put this chunk on the top of the file, preferably before all the other imports.
if __name__ == "__main__":
    # VVVV Uncomment me VVVV

    # You can either run HeadlessBase or ToonBase. Either one will work! (Preferably HeadlessBase, though.)
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase

    # Very important that you set base to this within the module.
    base = HeadlessBase()

    # Injector if needed
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()

    # We can call some extra methods if we need them for our instance:
    base.initCR()  # Initialize Client Repository (defines base.cr)
    base.startHeadlessShow()

from toontown.suit.heads.AnimatedSuitHead import *
from toontown.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.interval.IntervalGlobal import *
from panda3d.core import TextureStage


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='duckshfl')
class DuckShufflerAnimatedSuitHead(AnimatedSuitHead):

    SLOT_A = 'slotL'
    SLOT_B = 'slotMid'
    SLOT_C = 'slotR'

    # UV pos
    # Seven, Ducks, Bar, Cherry
    UV_POS = [0.0, 0.27, 0.528, 0.762]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slotNodes = [self.suit.specialHead.find(f'**/{slot}') for slot in [self.SLOT_A, self.SLOT_B, self.SLOT_C]]
        self.eyePositions = [0] * 3

    def cleanup(self):
        super().cleanup()
        self.slotNodes = {}

    def setEyePos(self, t):
        for slot in self.slotNodes:
            slot.setTexOffset(TextureStage.getDefault(), 0, t)

    def __animateSlot(self, t, eyeIndex):
        if not self.slotNodes:
            return
        self.slotNodes[eyeIndex].setTexOffset(TextureStage.getDefault(), 0, t)
        self.eyePositions[eyeIndex] = t

    def rollEyeSlot(self, eyeIndex, eyePosIndex, rollDuration=3.0, endDuration=0.1, stopDistance=0.04, rollCount=11, asInterval: bool = False):
        eyePos = self.UV_POS[eyePosIndex]
        seq = Sequence(
            LerpFunctionInterval(
                self.__animateSlot, duration=rollDuration,
                fromData=self.eyePositions[eyeIndex], toData=rollCount + eyePos + stopDistance,
                extraArgs=[eyeIndex],
            ),
            LerpFunctionInterval(
                self.__animateSlot, duration=endDuration,
                fromData=rollCount + eyePos + stopDistance, toData=rollCount + eyePos,
                extraArgs=[eyeIndex], blendType='easeOut'
            ),
            Func(self.__animateSlot, eyePos, eyeIndex)
        )
        if not asInterval:
            seq.start()
        else:
            return seq


# You'd put this chunk on the bottom of the file, outside any class/function scope.
if __name__ == "__main__":
    # Put whatever you wanna call here (preferably related to the module you're putting this into)
    # Ex: toontown/suit/Suit.py

    from toontown.suit import Suit
    s = Suit.Suit()
    from toontown.suit import SuitDNA
    d = SuitDNA.SuitDNA()
    d.newSuit('duckshfl')
    s.setDNA(d)
    s.loop('neutral')
    s.reparentTo(render)
    s.setPos(0, 0, 0)
    s.setH(180)
    base.oobe()

    # Lastly, we need to call this for anything to pop up.
    base.run()
