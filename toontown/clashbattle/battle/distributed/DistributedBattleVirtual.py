import random
from panda3d.core import VBase3, Point3
from direct.interval.IntervalGlobal import *
from toontown.battle.distributed import DistributedBattleFinal
from toontown.suit import SuitTimings
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedBattleVirtual(DistributedBattleFinal.DistributedBattleFinal):
    def __init__(self, cr):
        DistributedBattleFinal.DistributedBattleFinal.__init__(self, cr)

    def showSuitsJoining(self, suits, ts, name, callback):
        suitTrack = Parallel()
        delay = 0
        for suit in suits:
            suit.makeVirtual(healthColored=True)
            suit.setState('Battle')
            if suit.dna.dept == 'l':
                suit.reparentTo(self.bossCog)
                suit.setPos(0, 0, 0)
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
            flyIval = suit.beginSupaFlyMove(destPos, 2, 'flyInQuick')
            sfx = base.loader.loadSfx('phase_11/audio/sfx/LB_laser_beam_on_2.ogg')
            suit.setScale(0.01, 0.01, 0.01)
            suit.setColorScale(0, 0, 0, 0)
            popIn = Sequence(Parallel(Func(suit.show), SoundInterval(sfx, duration=1.2, startTime=0, volume=1), LerpScaleInterval(suit, 0.25, (1, 1, 1), (0.01, 0.01, 0.01)), LerpColorScaleInterval(suit, 0.25, (1, 1, 1, 1))))
            suitTrack.append(Track((delay, Parallel(popIn, Sequence(flyIval, Func(suit.loop, 'neutral'))))))
            delay += 1
        
        suitTrack.append(self.updateActiveSuitPositions())

        done = Func(callback)
        track = Sequence(Wait(0.8), suitTrack, done, name=name)
        track = Parallel(track, self.getCamTrack(override=not self.initialReservesJoiningDone))
        self.initialReservesJoiningDone = True
        track.start(ts)
        self.storeInterval(track, name)
        return

    def enterWaitForInput(self, ts = 0):
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput(self, ts)
