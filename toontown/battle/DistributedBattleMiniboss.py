import random
from panda3d.core import VBase3, Point3
from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, Track
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import DistributedBattleFinal
from toontown.effects import DustCloud
from toontown.suit import SuitTimings
from toontown.toonbase import ToontownGlobals
from toontown.chat import ResistanceChat
from toontown.chat.ChatGlobals import *
from toontown.battle import BattleProps
from toontown.battle import MovieUtil
from toontown.battle import SuitBattleGlobals
from direct.showutil import Effects
from direct.directnotify import DirectNotifyGlobal
from toontown.suit.DistributedDirectors import DistributedDirectors
from toontown.suit.DistributedLawbotBoss import DistributedLawbotBoss
from toontown.suit.DistributedCashbotBoss import DistributedCashbotBoss
from toontown.suit.DistributedSellbotBossMini import DistributedSellbotBossMini
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
        orderedSuits = self._getCanonicalSuitOrder(self.suits)
        for suit in orderedSuits:
            suit.reparentTo(self)
            destPos, destHpr = self.getActorPosHpr(suit, orderedSuits)
            suit.setPos(destPos)
            suit.setHpr(destHpr)

    def showSuitsFalling(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        for suit in suits:
            if suit.dna.name == 'ambass':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedDirectors):
                        obj.hideAmbassador()
            if suit.dna.name == 'wtapper':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedDirectors):
                        obj.hideWiretapper()
            if suit.dna.name == 'phouse':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedDirectors):
                        obj.hidePowerhouse()
            if suit.dna.name == 'bkeeper':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedDirectors):
                        obj.hideVaultmaster()
            if suit.dna.name == 'lgator':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedLawbotBoss):
                        obj.hideLitigator()
            if suit.dna.name == 'stenog':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedLawbotBoss):
                        obj.hideStenographer()
            if suit.dna.name == 'caseman':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedLawbotBoss):
                        obj.hideCaseManager()
            if suit.dna.name == 'sgoat':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedLawbotBoss):
                        obj.hideScapegoat()
            if suit.dna.name == 'safesupervis':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedSellbotBossMini):
                        obj.hidePressurizer()
            if suit.dna.name == 'ubuster':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedSellbotBossMini):
                        obj.hideUnionBuster()
            if suit.dna.name == 'racket':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedSellbotBossMini):
                        obj.hideRacketeer()
            if suit.dna.name == 'radiog':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedSellbotBossMini):
                        obj.hideRadiographer()
            if suit.dna.name == 'hroller':
                suit.setPos(0, 0, 50)
                return self.showSuitsFallingHighRoller(suit, ts, name, callback)
            if suit.dna.name == 'cbutcher':
                suit.setState('Battle')
                suitTrack = Sequence()
                oldPos, oldHpr = self.getActorPosHpr(suit, self.suits)

                def getDustCloudIval(oldPos=oldPos):
                    dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
                    dustCloud.setBillboardAxis(2.0)
                    dustCloud.setZ(3)
                    dustCloud.setScale(Point3(5.0, 1.0, 1.0))
                    dustCloud.createTrack()
                    dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
                    return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, self, oldPos + (0, 0, suit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                                    name='dustCloadIval')

                if suit in self.joiningSuits:
                    i = self._getPendingPreviewIndex(suit)
                    destPos, h = self.suitPendingPointsSilhouettes[i]
                    destHpr = VBase3(h, 0, 0)
                else:
                    destPos, destHpr = self.getActorPosHpr(suit, self.suits)
                startPos = destPos + Point3(0, 0, 0)
                startPos2 = destPos + Point3(0, 0, 0)
                self.notify.debug('startPos for %s = %s' % (suit, startPos))
                suitTrack.append(Func(suit.reparentTo, self))
                suitTrack.append(Func(suit.headsUp, self))
                suitTrack.append(LerpPosInterval(suit, 0, startPos))
                suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
                suitTrack.append(Func(getDustCloudIval().start))
                suitTrack.append(Sequence(ActorInterval(suit, 'mob-mentality', startTime=1)))
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(LerpPosInterval(suit, 0, startPos2))
                suitTracks.append(suitTrack)
                # flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
                suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
                delay += 0
                if self.hasLocalToon():
                    camera.reparentTo(self)
                    if random.choice([0, 1]):
                        camera.setPosHpr(0, -10, 7, 0, 0, 0)
                    else:
                        camera.setPosHpr(0, -10, 7, 0, 0, 0)
            elif suit.dna.name == 'hrollers' or suit.dna.name == 'bcaster':
                suit.setState('Battle')
                suitTrack = Sequence()
                if suit in self.joiningSuits:
                    i = self._getPendingPreviewIndex(suit)
                    destPos, h = self.suitPendingPointsSilhouettes[i]
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
                # flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
                suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
                delay += 0

                if self.hasLocalToon():
                    camera.reparentTo(self)
                    if random.choice([0, 1]):
                        camera.setPosHpr(0, -10, 7, 0, 0, 0)
                    else:
                        camera.setPosHpr(0, -10, 7, 0, 0, 0)
            elif suit.dna.name == 'mh2' or suit.dna.name == 'std2' or suit.dna.name == 'videog' or suit.dna.name == 'choreo' or suit.dna.name == 'fmaker' or suit.dna.name == 'cinema' or suit.dna.name == 'director':
                suit.setState('Battle')
                suitTrack = Sequence()
                oldPos, oldHpr = self.getActorPosHpr(suit, self.suits)

                def getDustCloudIval(oldPos=oldPos):
                    dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
                    dustCloud.setBillboardAxis(2.0)
                    dustCloud.setZ(3)
                    dustCloud.setScale(Point3(5.0, 1.0, 1.0))
                    dustCloud.createTrack()
                    dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
                    return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, self, oldPos + (0, 0, suit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                                    name='dustCloadIval')

                if suit in self.joiningSuits:
                    i = self._getPendingPreviewIndex(suit)
                    destPos, h = self.suitPendingPointsSilhouettes[i]
                    destHpr = VBase3(h, 0, 0)
                else:
                    destPos, destHpr = self.getActorPosHpr(suit, self.suits)
                startPos = destPos + Point3(0, 0, 0)
                startPos2 = destPos + Point3(0, 0, 0)
                self.notify.debug('startPos for %s = %s' % (suit, startPos))
                suitTrack.append(Func(suit.reparentTo, self))
                suitTrack.append(Func(suit.headsUp, self))
                suitTrack.append(Func(suit.hide))
                suitTrack.append(Wait(delay))
                suitTrack.append(Func(suit.show))
                suitTrack.append(LerpPosInterval(suit, 0, startPos))
                suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
                suitTrack.append(Func(getDustCloudIval().start))
                suitTrack.append(random.choice((ActorInterval(suit, 'mob-mentality', startTime=suit.getDuration('mob-mentality') - 1),
                                                ActorInterval(suit, 'slip-forward', startTime=suit.getDuration('slip-forward') - 1),
                                                ActorInterval(suit, 'glower', startTime=suit.getDuration('glower') - 1),
                                                ActorInterval(suit, 'speak', startTime=suit.getDuration('speak') - 1),
                                                ActorInterval(suit, 'finger-wag', startTime=suit.getDuration('finger-wag') - 1))))
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(LerpPosInterval(suit, 0, startPos2))
                suitTracks.append(suitTrack)
                # flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
                suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
                delay += .1
                if self.hasLocalToon():
                    camera.reparentTo(self)
                    if random.choice([0, 1]):
                        camera.setPosHpr(0, -10, 7, 0, 0, 0)
                    else:
                        camera.setPosHpr(0, -10, 7, 0, 0, 0)
            else:
                suitTrack = Sequence()
                if suit.dna.name == 'hroller2':
                    suit.hide()
                suit.setState('Battle')
                if suit.dna.dept == 'l':
                    suit.reparentTo(self.bossCog)
                    suit.setPos(0, 0, 0)
                if suit in self.joiningSuits:
                    i = self._getPendingPreviewIndex(suit)
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
                taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
                if not suit.dna.name == 'hroller2':
                    suitTrack.append(Track((delay, Sequence(Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), flyIval), Func(suit.loop, 'neutral')))))
                else:
                    suitTrack.append(Track((delay, Sequence(Parallel(flyIval), Func(suit.loop, 'neutral')))))
                suitTracks.append(suitTrack)
                delay += 1

                if self.hasLocalToon():
                    camera.reparentTo(self)
                    if random.choice([0, 1]):
                        camera.setPosHpr(20, -4, 7, 60, 0, 0)
                    else:
                        camera.setPosHpr(-20, -4, 7, -60, 0, 0)
        done = Func(callback)
        track = Sequence(suitTracks, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def showSuitsFallingPhantomEntry(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            suitTrack = Sequence()
            oldPos, oldHpr = self.getActorPosHpr(suit, self.suits)

            def getDustCloudIval(oldPos=oldPos):
                dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
                dustCloud.setBillboardAxis(2.0)
                dustCloud.setZ(3)
                dustCloud.setScale(Point3(5.0, 1.0, 1.0))
                dustCloud.createTrack()
                dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
                return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, self, oldPos + (0, 0, suit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                                name='dustCloadIval')

            if suit in self.joiningSuits:
                i = self._getPendingPreviewIndex(suit)
                destPos, h = self.suitPendingPointsSilhouettes[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            startPos = destPos + Point3(0, 0, 0)
            startPos2 = destPos + Point3(0, 0, 0)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suitTrack.append(Func(suit.reparentTo, self))
            suitTrack.append(Func(suit.headsUp, self))
            suitTrack.append(LerpPosInterval(suit, 0, startPos))
            suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
            suitTrack.append(Func(getDustCloudIval().start))
            suitTrack.append(Sequence(ActorInterval(suit, 'slip-forward')))
            suitTrack.append(LerpPosInterval(suit, 0, startPos2))
            suitTracks.append(suitTrack)
            # flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
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

    def showSuitsFallingSilhouette(self, suits, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            suitTrack = Sequence()
            if suit in self.joiningSuits:
                i = self._getPendingPreviewIndex(suit)
                destPos, h = self.suitPendingPointsSilhouettes[i]
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
            # flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
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

    def showSuitsFallingHighRoller(self, suit, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        suit.setState('Battle')
        suitTrack = Sequence()
        if suit in self.joiningSuits:
            i = self._getPendingPreviewIndex(suit)
            destPos, h = self.suitPendingPointsSilhouettes[i]
            destHpr = VBase3(h, 0, 0)
        else:
            destPos, destHpr = self.getActorPosHpr(suit, self.suits)
        startPos = destPos + Point3(0, 0, 0)
        startPos2 = destPos + Point3(0, 0, 0)
        self.notify.debug('startPos for %s = %s' % (suit, startPos))
        suitTrack.append(Func(suit.reparentTo, self))
        suitTrack.append(Func(suit.headsUp, self))
        suitTrack.append(LerpPosInterval(suit, 0, startPos))
        suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
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

    def showSuitsFallingVideographer(self, suit, ts, name, callback):
        if self.bossCog == None:
            return
        suitTracks = Parallel()
        delay = 0
        suit.setState('Battle')
        suitTrack = Sequence()
        if suit in self.joiningSuits:
            i = self._getPendingPreviewIndex(suit)
            destPos, h = self.suitPendingPointsSilhouettes[i]
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
                i = self._getPendingPreviewIndex(suit)
                destPos, h = self.suitPendingPointsSilhouettes[i]
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

    def showSuitsFallingHighRoller2(self, suit, ts, name, callback):
        if self.bossCog == None:
            return
        suitTrack = Parallel()
        delay = 0
        suit.setState('Battle')
        if suit.dna.dept == 'l':
            suit.reparentTo(self.bossCog)
            suit.setPos(0, 0, 0)
        if suit in self.joiningSuits:
            i = self._getPendingPreviewIndex(suit)
            destPos, h = self.suitPendingPointsSilhouettes[i]
            destHpr = VBase3(h, 0, 0)
        else:
            destPos, destHpr = self.getActorPosHpr(suit, self.suits)
        startPos = destPos + Point3(0, 0, SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)
        self.notify.debug('startPos for %s = %s' % (suit, startPos))
        suit.reparentTo(self)
        suit.setPos(destPos)
        suit.headsUp(self)
        suit.hide()
        flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
        taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
        delay += 1

        if self.hasLocalToon():
            camera.reparentTo(self)
            if random.choice([0, 1]):
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
            else:
                camera.setPosHpr(0, -10, 7, 0, 0, 0)
        done = Func(callback)
        track = Sequence(suitTrack, name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def createManagerMoveIval(self, suit):
        dur = suit.getDuration('landing')
        fr = suit.getFrameRate('landing')
        landingDur = dur
        totalDur = 7.3
        animTimeInAir = totalDur - dur
        flyingDur = animTimeInAir
        impactLength = dur - animTimeInAir
        if suit in self.joiningSuits:
            i = self._getPendingPreviewIndex(suit)
            destPos, h = self.suitPendingPointsSilhouettes[i]
            destHpr = VBase3(h, 0, 0)
        else:
            destPos, destHpr = self.getActorPosHpr(suit, self.suits)
        suit.reparentTo(render)
        if suit.dna.name == 'ambass':
            suit.setPos(15, 352.25, 2.5)
            taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
            moveIval = Sequence(Func(suit.headsUp, self), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Func(suit.pose, 'landing', 0),
                                ProjectileInterval(suit, duration=flyingDur, startPos=(15, 355, 4.25), endPos=destPos, gravityMult=0.25), ActorInterval(suit, 'landing'))
        elif suit.dna.name == 'wtapper':
            suit.setPos(-15, 352.25, 2.5)
            taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
            moveIval = Sequence(Func(suit.headsUp, self), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Func(suit.pose, 'landing', 0),
                                ProjectileInterval(suit, duration=flyingDur, startPos=(-15, 355, 4.25), endPos=destPos, gravityMult=0.25), ActorInterval(suit, 'landing'))
        elif suit.dna.name == 'phouse':
            suit.setPos(30, 352.25, 2.5)
            taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
            moveIval = Sequence(Func(suit.headsUp, self), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Func(suit.pose, 'landing', 0),
                                ProjectileInterval(suit, duration=flyingDur, startPos=(30, 355, 4.25), endPos=destPos, gravityMult=0.25), ActorInterval(suit, 'landing'))
        elif suit.dna.name == 'bkeeper':
            suit.setPos(-30, 352.25, 2.5)
            taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
            moveIval = Sequence(Func(suit.headsUp, self), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Func(suit.pose, 'landing', 0),
                                ProjectileInterval(suit, duration=flyingDur, startPos=(-30, 355, 4.25), endPos=destPos, gravityMult=0.25), ActorInterval(suit, 'landing'))
        else:
            suit.setPos(0, 0, 0)
            taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
            moveIval = Sequence(Func(suit.headsUp, self), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Func(suit.pose, 'landing', 0),
                                ProjectileInterval(suit, duration=flyingDur, startPos=(-30, 355, 4.25), endPos=destPos, gravityMult=0.25), ActorInterval(suit, 'landing'))
        suit.setHpr(180, 0, 0)
        if suit.prop == None:
            suit.prop = BattleProps.globalPropPool.getProp('propeller')
        lastSpinFrame = 8
        fr = suit.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame + 1) / fr
        suit.attachPropeller()
        propTrack = Parallel(SoundInterval(suit.propInSound, duration=flyingDur, node=suit), Sequence(ActorInterval(suit.prop, 'propeller', constrainedLoop=1, duration=flyingDur + 1, startTime=0.0, endTime=spinTime), ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime), Func(suit.detachPropeller)))
        result = Parallel(moveIval, propTrack)
        return result

    def enterWaitForInput(self, ts = 0):
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput(self, ts)
        if self.hasLocalToon():
            camera.reparentTo(self)
