import random
from panda3d.core import VBase3, Point3
from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, Track
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import DistributedBattleFinal
from toontown.suit import SuitTimings
from toontown.toonbase import ToontownGlobals
from toontown.chat import ResistanceChat
from toontown.chat.ChatGlobals import *
from toontown.battle import BattleProps
from direct.showutil import Effects
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect

class DistributedBattleMiniboss(DistributedBattleFinal.DistributedBattleFinal):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattleMiniboss')

    def __init__(self, cr):
        DistributedBattleFinal.DistributedBattleFinal.__init__(self, cr)
        base.dbw = self
        self.initialReservesJoiningDone = False

    def announceGenerate(self):
        DistributedBattleFinal.DistributedBattleFinal.announceGenerate(self)
        self.moveSuitsToInitialPos()

    def showSuitsJoining(self, suits, ts, name, callback):
        if len(suits) == 0 and not self.initialReservesJoiningDone:
            self.initialReservesJoiningDone = True
            self.doInitialSuitsJoining(ts, name, callback)
            return
        self.showSuitsFalling(suits, ts, name, callback)

    def doInitialSuitsJoining(self, ts, name, callback):
        done = Func(callback)
        if self.hasLocalToon():
            self.notify.debug('parenting camera to distributed battle waiters')
            camera.reparentTo(self)
            if random.choice([0, 1]):
                camera.setPosHpr(20, -4, 7, 60, 0, 0)
            else:
                camera.setPosHpr(-20, -4, 7, -60, 0, 0)
        track = Sequence(Wait(0.5), done, name=name)
        track.start(ts)
        self.storeInterval(track, name)

    def moveSuitsToInitialPos(self):
        battlePts = self.suitPoints[len(self.suitPendingPoints) - 1]
        for i in xrange(len(self.suits)):
            suit = self.suits[i]
            suit.reparentTo(self)
            destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            suit.setPos(destPos)
            suit.setHpr(destHpr)

    def showSuitsFalling(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTrack = Parallel()
        delay = 0
        for suit in suits:
            if suit.dna.name == 'hrollers':
                suit.setPos(0, 0, 50)
                return self.showSuitsFallingSilhouette(suits, ts, name, callback)
            if suit.dna.name == 'hroller2':
                suit.setPos(0, 0, 50)
                return self.showSuitsFallingHighRoller2(suits, ts, name, callback)
            if suit.dna.name == 'videog':
                suit.setPos(0, 0, 50)
                return self.showSuitsFallingVideographer(suits, ts, name, callback)
            if suit.dna.name == 'bcaster':
                suit.setPos(0, 0, 50)
                return self.showSuitsFallingSilhouette(suits, ts, name, callback)
            if suit.dna.name == 'hroller':
                suit.setPos(0, 0, 50)
                return self.showSuitsFallingHighRoller(suits, ts, name, callback)
            if suit.dna.name == 'director':
                suit.setPos(0, 0, 50)
                return self.showSuitsFallingHighRoller(suits, ts, name, callback)
            if suit.dna.name == 'fmaker':
                suit.setPos(0, 0, 50)
                return self.showSuitsFallingHighRoller(suits, ts, name, callback)
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
            suit.headsUp(self)
            flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
            suitTrack.append(Track((delay, Sequence(flyIval, Func(suit.loop, 'neutral')))))
            delay += 1

        if self.hasLocalToon():
            camera.reparentTo(self)
            if random.choice([0, 1]):
                camera.setPosHpr(20, -4, 7, 60, 0, 0)
            else:
                camera.setPosHpr(-20, -4, 7, -60, 0, 0)
        done = Func(callback)
        track = Sequence(suitTrack, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def showSuitsFallingSilhouette(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            suitTrack = Sequence()
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            startPos = destPos + Point3(0, 0, 0)
            startPos.setY(startPos.getY() + 16.5)
            startPos.setZ(startPos.getZ() - 4.5)
            startPos2 = destPos + Point3(0, 0, 0)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suitTrack.append(Func(suit.reparentTo, self))
            suitTrack.append(Func(suit.headsUp, self))
            suitTrack.append(LerpPosInterval(suit, 0, startPos))
            suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
            suitTrack.append(LerpColorScaleInterval(suit, 0, (0, 0, 0, 0)))
            suitTrack.append(Sequence(ActorInterval(suit, 'shot5', startTime=3, endTime=3), Parallel(Wait(3.0), LerpColorScaleInterval(suit, 3, (1, 1, 1, 1)))))
            suitTrack.append(LerpPosInterval(suit, 0, startPos2))
            suitTracks.append(suitTrack)
            #flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
            suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
            delay += 0

        if self.hasLocalToon():
            camera.reparentTo(self)
            if random.choice([0, 1]):
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
            else:
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
        done = Func(callback)
        track = Sequence(suitTracks, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def showSuitsFallingHighRoller(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            suitTrack = Sequence()
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            startPos = destPos + Point3(0, 0, 0)
            startPos.setY(startPos.getY() + 16.5)
            startPos.setZ(startPos.getZ() - 4.5)
            startPos2 = destPos + Point3(0, 0, 0)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suitTrack.append(Func(suit.reparentTo, self))
            suitTrack.append(Func(suit.headsUp, self))
            suitTrack.append(LerpPosInterval(suit, 0, startPos))
            suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
            suitTrack.append(LerpColorScaleInterval(suit, 0, (0, 0, 0, 0)))
            suitTrack.append(Parallel(ActorInterval(suit, 'shot5'), LerpColorScaleInterval(suit, 0.5, (1, 1, 1, 1))))
            suitTrack.append(Func(suit.setChatAbsolute, "Get ready for the ffho-ho-how of a lifetime, Bobby Dazzler!", CFSpeech | CFTimeout))
            suitTrack.append(LerpPosInterval(suit, 0, startPos2))
            suitTracks.append(suitTrack)
            #flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
            suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
            delay += 0

        if self.hasLocalToon():
            camera.reparentTo(self)
            if random.choice([0, 1]):
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
            else:
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
        done = Func(callback)
        track = Sequence(suitTracks, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def showSuitsFallingVideographer(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            suitTrack = Sequence()
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            startPos = destPos + Point3(0, 0, 0)
            startPos.setY(startPos.getY() + 16.5)
            startPos.setZ(startPos.getZ() - 4.5)
            startPos2 = destPos + Point3(0, 0, 0)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suitTrack.append(Func(suit.reparentTo, self))
            suitTrack.append(Func(suit.headsUp, self))
            suitTrack.append(LerpPosInterval(suit, 0, startPos))
            suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
            suitTrack.append(LerpColorScaleInterval(suit, 0, (0, 0, 0, 0)))
            suitTrack.append(Parallel(ActorInterval(suit, 'shot5'), LerpColorScaleInterval(suit, 0.5, (1, 1, 1, 1))))
            suitTrack.append(LerpPosInterval(suit, 0, startPos2))
            suitTracks.append(suitTrack)
            #flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
            suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
            delay += 0

        if self.hasLocalToon():
            camera.reparentTo(self)
            if random.choice([0, 1]):
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
            else:
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
        done = Func(callback)
        track = Sequence(suitTracks, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def showSuitsFallingHollywoods(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            suitTrack = Sequence()
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            startPos = destPos + Point3(0, 0, 0)
            startPos.setY(startPos.getY() + 16.5)
            startPos.setZ(startPos.getZ() - 4.5)
            startPos2 = destPos + Point3(0, 0, 0)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suitTrack.append(Func(suit.reparentTo, self))
            suitTrack.append(Func(suit.headsUp, self))
            suitTrack.append(LerpPosInterval(suit, 0, startPos))
            suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
            suitTrack.append(LerpColorScaleInterval(suit, 0, (0, 0, 0, 0)))
            suitTrack.append(Parallel(ActorInterval(suit, 'shot5'), LerpColorScaleInterval(suit, 0.5, (1, 1, 1, 1))))
            suitTrack.append(LerpPosInterval(suit, 0, startPos2))
            suitTracks.append(suitTrack)
            #flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
            suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
            delay += 0

        if self.hasLocalToon():
            camera.reparentTo(self)
            if random.choice([0, 1]):
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
            else:
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
        done = Func(callback)
        track = Sequence(suitTracks, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def showSuitsFallingHighRoller2(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            suitTrack = Sequence()
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            startPos = destPos + Point3(0, 0, 0)
            startPos.setY(startPos.getY() + 16.5)
            startPos.setZ(startPos.getZ() - 4.5)
            startPos2 = destPos + Point3(0, 0, 0)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suitTrack.append(Func(suit.reparentTo, self))
            suitTrack.append(Func(suit.headsUp, self))
            suitTrack.append(LerpPosInterval(suit, 0, startPos))
            suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
            suitTrack.append(LerpColorScaleInterval(suit, 0, (0, 0, 0, 0)))
            suitTrack.append(Parallel(ActorInterval(suit, 'shot5'), LerpColorScaleInterval(suit, 0.5, (1, 1, 1, 1))))
            suitTrack.append(LerpPosInterval(suit, 0, startPos2))
            suitTracks.append(suitTrack)
            #flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
            suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
            delay += 0

        if self.hasLocalToon():
            camera.reparentTo(self)
            if random.choice([0, 1]):
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
            else:
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
        done = Func(callback)
        track = Sequence(suitTracks, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def enterWaitForInput(self, ts = 0):
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput(self, ts)
        if self.hasLocalToon():
            camera.reparentTo(self)
