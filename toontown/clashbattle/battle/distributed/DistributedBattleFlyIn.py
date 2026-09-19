import random
from panda3d.core import VBase3, Point3
from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, Track
from toontown.battle.distributed import DistributedBattleFinal
from toontown.suit import SuitTimings
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedBattleFlyIn(DistributedBattleFinal.DistributedBattleFinal):
    def __init__(self, cr):
        DistributedBattleFinal.DistributedBattleFinal.__init__(self, cr)
        self.initialReservesJoiningDone = False

    def showSuitsJoining(self, suits, ts, name, callback):
        if len(suits) == 0 and not self.initialReservesJoiningDone:
            self.initialReservesJoiningDone = True
            self.doInitialSuitsJoining(ts, name, callback)
            return
        self.showSuitsFalling(suits, ts, name, callback)

    def doInitialSuitsJoining(self, ts, name, callback):
        done = Func(callback)
        track = Sequence(Wait(0.5), done, name=name)
        track = Parallel(track, self.getCamTrack(override=True))
        track.start(ts)
        self.storeInterval(track, name)

    def showSuitsFalling(self, suits, ts, name, callback):
        if self.bossCog is None:
            return
        suitTrack = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            startPos = destPos + Point3(0, 0, SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suit.reparentTo(self)
            suit.setPos(startPos)
            suit.setHpr(destHpr)
            flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
            suitTrack.append(Track((delay, Sequence(flyIval, Func(suit.loop, 'neutral')))))
            delay += 1
        
        suitTrack.append(self.updateActiveSuitPositions())

        done = Func(callback)
        track = Sequence(suitTrack, done, name=name)
        track = Parallel(track, self.getCamTrack())
        track.start(ts)
        self.storeInterval(track, name)
        return

    def enterWaitForInput(self, ts = 0):
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput(self, ts)
        if self.hasLocalToon():
            camera.reparentTo(self)
