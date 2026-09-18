from toontown.toon.accessories.ToonActorAccessory import ToonActorAccessory
from direct.interval.IntervalGlobal import *
import random

OPEN = 0
CLOSE = 1

NEUTRAL = 0
SMILE = 1
SPOOKY = 2


class GhostTophat(ToonActorAccessory):
    def __init__(self, *args):
        super().__init__(*args)
        self.taskName = self.uniqueName('gibus-anim')
        self.blinkTaskName = self.uniqueName('gibus-blink')
        self.unblinkTaskName = self.uniqueName('gibus-unblink')
        self.timeBetweenAnims = (10, 25)
        self.timeBetweenBlinks = (3, 5)
        self.blinkDuration = 0.1
        self.track = None
        self.forceAnim = None  # debug; also sets time between anims to 1 when set.

    def getAnimNames(self) -> tuple:
        return 'loop', 'idle1', 'idle2', 'idle3'

    def complete(self):
        self.setMouth(NEUTRAL)
        self.setEyes(OPEN)
        self.createAnimTask()
        self.createBlinkTask()

    def finish(self):
        if self.track is not None:
            self.track.finish()
            self.track = None
        taskMgr.remove(self.taskName)
        taskMgr.remove(self.blinkTaskName)
        taskMgr.remove(self.unblinkTaskName)

    def createBlinkTask(self):
        a, b = self.timeBetweenBlinks
        t = random.randint(a, b)
        taskMgr.doMethodLater(t, self.blink, self.blinkTaskName)

    def blink(self, task):
        if self.track is not None:
            self.setEyes(CLOSE)
        taskMgr.doMethodLater(self.blinkDuration, self.unblink, self.unblinkTaskName)
        self.createBlinkTask()

    def unblink(self, task):
        if self.track is not None:
            self.setEyes(OPEN)
            self.setMouth(NEUTRAL)
            if random.random() < 0.25:
                self.setMouth(SPOOKY)

    def createAnimTask(self):
        a, b = self.timeBetweenAnims
        t = random.randint(a, b)
        if self.forceAnim:
            t = 1
        self.loop(self.getAnimNames()[0])
        taskMgr.doMethodLater(t, self.playAnim, self.taskName)

    def playAnim(self, task):
        """
        Plays a random ghost anim.
        """
        animChoices = self.getAnimNames()[1:]
        anim = random.choice(animChoices)
        if self.forceAnim is not None:
            anim = self.forceAnim
        self.track = Parallel(ActorInterval(self, anim))
        if anim == 'idle1':    # peek-a-boo, jumpscare
            self.track.append(
                Sequence(
                    Wait(0.6),
                    Func(self.setEyes, CLOSE),
                    Func(self.setMouth, NEUTRAL),
                    Wait(1.1),
                    Func(self.setEyes, OPEN),
                    Func(self.setMouth, SPOOKY),
                )
            )
        elif anim == 'idle2':  # wave wave wave
            self.track.append(
                Sequence(
                    Func(self.setEyes, CLOSE),
                    Func(self.setMouth, SMILE),
                )
            )
        elif anim == 'idle3':  # duck, and come back up
            self.track.append(
                Sequence(
                    Func(self.setEyes, CLOSE),
                    Func(self.setMouth, NEUTRAL),
                    Wait(0.6),
                    Func(self.setEyes, OPEN),
                    Func(self.setMouth, SPOOKY),
                )
            )
        self.track.append(Sequence(
            Wait(self.getDuration(anim) + 0.1),
            Func(self.setEyes, OPEN),
            Func(self.setMouth, NEUTRAL),
            Func(self.createAnimTask),
        ))
        self.track.start()

    def setEyes(self, mode):
        # Takes OPEN or CLOSE.
        leftOpen, rightOpen, leftClosed, rightClosed = self._getEyeNodes()
        if leftOpen and rightOpen and leftClosed and rightClosed:
            leftOpen.hide()
            rightOpen.hide()
            leftClosed.hide()
            rightClosed.hide()
            if mode == OPEN:
                leftOpen.show()
                rightOpen.show()
            elif mode == CLOSE:
                leftClosed.show()
                rightClosed.show()

    def _getEyeNodes(self) -> tuple:
        return self.find('**/eyeLeft'), self.find('**/eyeRight'), self.find('**/eyeLeft.001'), self.find('**/eyeRight.001'),

    def setMouth(self, mode):
        # Takes NEUTRAL, SMILE, or SPOOKY.
        neutral, smile, spooky = self._getMouthNodes()
        if neutral and smile and spooky:
            neutral.hide()
            smile.hide()
            spooky.hide()
            if mode == NEUTRAL:
                neutral.show()
            elif mode == SMILE:
                smile.show()
            elif mode == SPOOKY:
                spooky.show()

    def _getMouthNodes(self) -> tuple:
        return self.find('**/neutral.001'), self.find('**/smile'), self.find('**/spooky')

    @classmethod
    def modifyPreview(cls, geom):
        # Gibus Hat - Hide unnecessary facial features
        removeNodes = (
            geom.find('**/eyeLeft'),
            geom.find('**/eyeRight'),
            geom.find('**/eyeLeft.001'),
            geom.find('**/eyeRight.001'),
            geom.find('**/neutral.001'),
            geom.find('**/smile'),
            geom.find('**/spooky'),
            geom.find('**/ghostBody'),
        )
        for node in removeNodes:
            if node and not node.isEmpty():
                node.removeNode()
