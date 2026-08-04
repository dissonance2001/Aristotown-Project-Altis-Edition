import random

from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import VBase3

from toontown.battle import DistributedBattleFinal


class DistributedCashbotBattleFinal(DistributedBattleFinal.DistributedBattleFinal):
    """Dedicated normal C.F.O. battle hatch animation.

    Cogs begin small inside the C.F.O. hatch, then walk toward their battle
    positions while growing smoothly to normal size at the same time.

    The shared DistributedBattleFinal class remains untouched, so High Roller
    and all other custom boss battles keep their existing behavior.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedCashbotBattleFinal')

    def showSuitsJoining(self, suits, ts, name, callback):
        if self.bossCog is None:
            return

        if self.battleSide:
            openDoor = Func(self.bossCog.doorB.request, 'open')
            closeDoor = Func(self.bossCog.doorB.request, 'close')
        else:
            openDoor = Func(self.bossCog.doorA.request, 'open')
            closeDoor = Func(self.bossCog.doorA.request, 'close')

        suitTrack = Parallel()
        delay = 0.0

        for suit in suits:
            suit.setState('Battle')

            # Match the normal boss hatch effect: start small at the boss
            # origin, then move and grow concurrently.
            suit.setPos(self.bossCog, 0, 0, 0)
            suit.headsUp(self)
            suit.setScale(3.8 / suit.height)

            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)

            # Start both intervals at the same moment. This prevents the Cog
            # from standing still while small before beginning to grow.
            suitTrack.append(Track(
                (delay, Parallel(
                    self.createAdjustInterval(suit, destPos, destHpr),
                    suit.scaleInterval(1.5, 1)))))
            delay += 1.0

        if self.hasLocalToon() and hasattr(base, 'camera') and base.camera is not None:
            base.camera.reparentTo(self)
            if random.choice([0, 1]):
                base.camera.setPosHpr(20, -4, 7, 60, 0, 0)
            else:
                base.camera.setPosHpr(-20, -4, 7, -60, 0, 0)

        done = Func(callback)
        track = Sequence(openDoor, suitTrack, closeDoor, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
