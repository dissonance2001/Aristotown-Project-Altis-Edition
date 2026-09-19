from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleProps import *

from direct.distributed import ClockDelta
from . import DistributedGoon
from .GoonGlobals import *

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.suit import DistributedGoon


@DirectNotifyCategory()
class DistributedGridGoon(DistributedGoon.DistributedGoon):

    def __init__(self, cr):
        try:
            self.DistributedGridGoon_initialized
        except:
            self.DistributedGridGoon_initialized = 1
            DistributedGoon.DistributedGoon.__init__(self, cr)

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedGoon.DistributedGoon.generate(self)

        # turn off wall collisions, and let the AI figure it out
        self.ignore(self.uniqueName('wallHit'))

        self.mazeWalkTrack = None
        self.mazeTurnTrack = None

    def delete(self):
        if self.mazeWalkTrack:
            self.mazeWalkTrack.pause()
            del self.mazeWalkTrack
        if self.mazeTurnTrack:
            self.mazeTurnTrack.pause()
            del self.mazeTurnTrack

        DistributedGoon.DistributedGoon.delete(self)

    def setH(self, h):
        self.h = h

    def setPath(self):
        return

    def setPathPts(self, xi, yi, zi, xf, yf, zf):
        self.notify.debug('setPathPts')

        # Start walking when we receive path points for the first time
        if self.getCurrentOrNextState() != 'Walk':
            self.request('Walk')

        if self.mazeWalkTrack:
            self.mazeWalkTrack.pause()
            del self.mazeWalkTrack
            self.mazeWalkTrack = None
        if self.mazeTurnTrack:
            self.mazeTurnTrack.pause()
            del self.mazeTurnTrack
            self.mazeTurnTrack = None

        curPos = Point3(xi, yi, zi)
        nextPos = Point3(xf, yf, zf)

        # Calculate the amount of time we should spend walking
        distance = Vec3(curPos - nextPos).length()
        duration = distance / self.velocity

        # Naming this reference 'self.walkTrack' was causing the resume()
        # call in DistributedGoon.enterWalk to blow up down in the
        # IntervalManager.
        self.mazeWalkTrack = Sequence(Func(self.headsUp,
                                           nextPos[0], nextPos[1], nextPos[2]),  # face next point
                                      LerpPosInterval(self,
                                                      duration=duration,
                                                      pos=nextPos,
                                                      startPos=curPos),  # go to next point
                                      name=self.uniqueName("mazeWalkTrack"))
        self.mazeWalkTrack.start()

    def turnGoon(self, timesTurned):
        if self.mazeTurnTrack:
            self.mazeTurnTrack.finish()
            del self.mazeTurnTrack
            self.mazeTurnTrack = None

        turnAmount = timesTurned * 90 + self.getH()
        turnTime = timesTurned * GRID_SECONDS_PER_ROTATION
        self.mazeTurnTrack = Sequence(LerpHprInterval(self, turnTime, (turnAmount, 0, 0)))
        self.mazeTurnTrack.start()

    def enterWalk(self, avId=None, ts=0):
        self.notify.debug('enterWalk, ts = %s' % ts)
        self.startToonDetect()
        self.loop('walk', 0)
        self.isStunned = 0

    def exitWalk(self):
        self.notify.debug('exitWalk')
        self.stopToonDetect()
        if self.mazeWalkTrack and not self.paused:
            self.pauseTime = self.mazeWalkTrack.pause()
            self.paused = 1
        self.stop()

    def handleToonDetect(self, collEntry = None):
        if base.localAvatar.isStunned:
            return
        if self.state == 'Off':
            return
        self.stopToonDetect()
        self.request('Battle', base.localAvatar.doId)
        if self.mazeWalkTrack:
            self.pauseTime = self.mazeWalkTrack.pause()
            self.paused = 1
        if self.mazeTurnTrack:
            self.mazeTurnTrack.finish()
            self.mazeTurnTrack = None
        if self.dclass and hasattr(self, 'dclass'):
            self.sendUpdate('requestBattle', [self.pauseTime])
        else:
            self.notify.info('Grid Goon deleted and still trying to call handleToonDetect()')

    def __handleStun(self, collEntry):
        toon = base.localAvatar
        if toon:
            toonDistance = self.getPos(toon).length()
            if toonDistance > self.attackRadius:
                self.notify.warning('Stunned a grid goon, but outside of attack radius')
                return
            else:
                self.request('Stunned')
        if self.mazeWalkTrack:
            self.pauseTime = self.mazeWalkTrack.pause()
            self.paused = 1
        if self.mazeTurnTrack:
            self.mazeTurnTrack.finish()
            self.mazeTurnTrack = None
        self.sendUpdate('requestStunned', [self.pauseTime])

    def setMovie(self, mode, avId, pauseTime, timestamp):
        if self.isDead:
            return
        ts = ClockDelta.globalClockDelta.localElapsedTime(timestamp)
        self.notify.debug('%s: setMovie(%s,%s,%s,%s)' % (self.doId,
         mode,
         avId,
         pauseTime,
         ts))
        if mode == GOON_MOVIE_BATTLE:
            if self.state != 'Battle':
                self.request('Battle', avId, ts)
        elif mode == GOON_MOVIE_STUNNED:
            if self.state != 'Stunned':
                toon = base.cr.doId2do.get(avId)
                if toon:
                    toonDistance = self.getPos(toon).length()
                    if toonDistance > self.attackRadius:
                        self.notify.warning('Stunned a goon, but outside of attack radius')
                        return
                    else:
                        self.request('Stunned', ts)
        elif mode == GOON_MOVIE_RECOVERY:
            if self.state != 'Recovery':
                self.request('Recovery', ts, pauseTime)
        elif mode == GOON_MOVIE_SYNC:
            if self.mazeWalkTrack:
                self.mazeWalkTrack.pause()
                self.paused = 1
            if self.state == 'Off' or self.state == 'Walk':
                self.request('Walk', avId, pauseTime + ts)
        else:
            if self.mazeWalkTrack:
                self.mazeWalkTrack.pause()
                self.mazeWalkTrack = None
            if self.mazeTurnTrack:
                self.mazeTurnTrack.finish()
                self.mazeTurnTrack = None
            self.request('Walk', avId, pauseTime + ts)
