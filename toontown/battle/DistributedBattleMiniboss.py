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
from toontown.battle.BattleProps import *
from toontown.battle import BattleProps
from toontown.battle import MovieUtil
from toontown.battle import SuitBattleGlobals
from direct.showutil import Effects
from direct.directnotify import DirectNotifyGlobal
from toontown.suit.DistributedDirectors import DistributedDirectors
from toontown.suit.DistributedBoardbotBoss import DistributedBoardbotBoss
from toontown.suit.DistributedCountErclaimBoss import DistributedCountErclaimBoss
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
            if suit.dna.name == 'cdirector':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedBoardbotBoss):
                        obj.hideContingency()
            if suit.dna.name == 'dking':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedBoardbotBoss):
                        obj.hideDividend()
            if suit.dna.name == 'rkeeper':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedBoardbotBoss):
                        obj.hideRecordkeeper()
            if suit.dna.name == 'liquid':
                for obj in base.cr.doId2do.values():
                    if isinstance(obj, DistributedBoardbotBoss):
                        obj.hideTollmaster()
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
            if suit.dna.name == 'hustle':
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
            boss = next((obj for obj in base.cr.doId2do.values()
            if isinstance(obj, DistributedCountErclaimBoss)), None)
            if boss:
                if suit.isSkeleton:
                    suit.setState('Battle')
                    suitTrack = Sequence()
                    oldPos, oldHpr = self.getActorPosHpr(suit, self.suits)

                    if suit in self.joiningSuits:
                        i = self._getPendingPreviewIndex(suit)
                        destPos, h = self.suitPendingPoints[i]
                        destHpr = VBase3(h, 0, 0)
                    else:
                        destPos, destHpr = self.getActorPosHpr(suit, self.suits)
                    startPos = destPos + Point3(0, 0, 0)
                    startPos2 = destPos + Point3(0, 0, 0)
                    self.notify.debug('startPos for %s = %s' % (suit, startPos))
                    sfx = loader.loadSfx(
                        "phase_5/audio/sfx/SA_zombie_cogs_rising.ogg"
                    )
                    suitTrack.append(Func(suit.reparentTo, self))
                    suitTrack.append(Func(suit.headsUp, self))
                    suitTrack.append(LerpPosInterval(suit, 0, startPos))
                    suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
                    suitTrack.append(Parallel(SoundInterval(sfx, node=suit), ActorInterval(suit, 'reanimated')))
                    suitTrack.append(Func(suit.loop, 'neutral'))
                    suitTrack.append(LerpPosInterval(suit, 0, startPos2))
                    suitTracks.append(suitTrack)
                    # flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
                    suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
                    delay += 0
                    if self.hasLocalToon():
                        camera.reparentTo(self)
                        if random.choice([0, 1]):
                            camera.setPosHpr(0, -15, 7, 0, 0, 0)
                        else:
                            camera.setPosHpr(0, -15, 7, 0, 0, 0)
                else:
                    suit.setState('Battle')
                    if self.hasLocalToon():
                        camera.reparentTo(self)
                        if random.choice([0, 1]):
                            camera.setPosHpr(0, -15, 7, 0, 0, 0)
                        else:
                            camera.setPosHpr(0, -15, 7, 0, 0, 0)
                    if suit in self.joiningSuits:
                        i = self._getPendingPreviewIndex(suit)
                        destPos, h = self.suitPendingPoints[i]
                        destHpr = VBase3(h, 0, 0)
                    else:
                        destPos, destHpr = self.getActorPosHpr(suit, self.suits)
                    trapProp = globalPropPool.getProp('quicksand')
                    trapProp.setColor(Vec4(0.1, 0.1, 1.0, 1))
                    trapProp.setHpr(Point3(300, 0, 0))
                    trapProp.setScale(0.01)
                    trapProp.setPos(destPos)
                    trapProp.reparentTo(self)
                    smallScale = 0.01
                    bigScale = 2.25
                    biggerScale = 2.5
                    trapTrack = Sequence(
                        Wait(0.65),
                        LerpScaleInterval(trapProp, 0.65, biggerScale, blendType='easeIn'),
                        LerpScaleInterval(trapProp, 0.15, bigScale, blendType='easeOut'),
                        Wait(1.0),
                        LerpScaleInterval(trapProp, 0.15, biggerScale, blendType='easeIn'),
                        LerpScaleInterval(trapProp, 0.65, smallScale, blendType='easeOut'),
                        Func(trapProp.removeNode)
                    )

                    def soakSuit():
                        pass

                    def suitNeutral():
                        suit.setNeutralAnimation()

                    def createSuitMoveIval(suit, destPos, hole):
                        dur = suit.getDuration('landing')
                        fr = suit.getFrameRate('landing')
                        landingDur = dur
                        totalDur = 7.3
                        animTimeInAir = totalDur - dur
                        flyingDur = animTimeInAir
                        moveIval = Sequence(
                            Func(suit.pose, 'landing', 0),
                                Parallel(
                                    Sequence(
                                        ProjectileInterval(suit, duration=flyingDur, endPos=destPos, gravityMult=0.125),
                                        ActorInterval(suit, 'landing')
                                    ),
                                    Sequence(
                                        Wait(0.5),
                                    )
                                ),
                                Func(suitNeutral)
                        )
                        if suit.prop is None:
                            suit.prop = globalPropPool.getProp('propeller')
                        propDur = suit.prop.getDuration('propeller')
                        lastSpinFrame = 8
                        fr = suit.prop.getFrameRate('propeller')
                        spinTime = lastSpinFrame / fr
                        openTime = (lastSpinFrame + 1) / fr
                        taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
                        propTrack = Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), 
                            SoundInterval(suit.propInSound, duration=flyingDur, node=suit),
                            Sequence(
                                ActorInterval(suit.prop, 'propeller', constrainedLoop=1, duration=flyingDur + 1, startTime=0.0, endTime=spinTime),
                                ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime),
                                Func(suit.detachPropeller)
                            )
                        )
                        hole.setPos(self, destPos[0], destPos[1], destPos[2])
                        underPos = destPos + Point3(0, 0, (-SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)/2)
                        startPos = destPos + Point3(0, 0, 0)
                        startPos2 = destPos + Point3(0, 0, 0)
                        result = Parallel(
                            Func(suit.attachPropeller),
                            Sequence(
                                Func(suit.setPos, underPos),
                                Parallel(moveIval, propTrack)
                            )
                        )
                        return result
                    #destPos, destHpr = self.getActorPosHpr(suit)
                    suit.wrtReparentTo(self)
                    moveIval = createSuitMoveIval(suit, destPos, trapProp)
                    # suitInbetweenTrack = Sequence(Func(suit.setSkelecog, 1), Func(suit.healthBar.show), Func(soakSuit), Func(suit.setHp, suit.getMaxHp()), Func(suit.wrtReparentTo, battle))
                    suitTrack = Sequence(moveIval)

                   # return Parallel(suitTrack, trapTrack)
                    suitTracks.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
                    suitTracks.append(Parallel(suitTrack, trapTrack))
            elif suit.dna.name == 'cbutcher':
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
                    destPos, h = self.suitPendingPointsSilhouettes2[i]
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
                suitTrack.append(Sequence(ActorInterval(suit, 'mob-mentality', startTime=suit.getDuration('mob-mentality') - 1)))
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(LerpPosInterval(suit, 0, startPos2))
                suitTracks.append(suitTrack)
                # flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
                suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
                delay += 0
                if self.hasLocalToon():
                    camera.reparentTo(self)
                    if random.choice([0, 1]):
                        camera.setPosHpr(0, -15, 7, 0, 0, 0)
                    else:
                        camera.setPosHpr(0, -15, 7, 0, 0, 0)
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
                        camera.setPosHpr(0, -15, 7, 0, 0, 0)
                    else:
                        camera.setPosHpr(0, -15, 7, 0, 0, 0)
                continue
            boss = next((obj for obj in base.cr.doId2do.values()
            if isinstance(obj, DistributedCashbotBoss)), None)
            if boss and not suit.dna.name in ['bcaster', 'hrollers', 'hroller2', 'hroller']:
                suit.setState('Battle')
                suitTrack = Sequence()
                oldPos, oldHpr = self.getActorPosHpr(suit, self.suits)
                stagelight = globalPropPool.getProp('stagelight')
                node = stagelight.node()
                node.setBounds(OmniBoundingVolume())
                node.setFinal(1)
                stagelight.reparentTo(suit)
                stagelight.setPos(0, 0, suit.height + 10)

                if suit in self.joiningSuits:
                    i = self._getPendingPreviewIndex(suit)
                    destPos, h = self.suitPendingPointsSilhouettes2[i]
                    destHpr = VBase3(h, 0, 0)
                else:
                    destPos, destHpr = self.getActorPosHpr(suit, self.suits)
                startPos = destPos + Point3(0, 0, 0)
                startPos2 = destPos + Point3(0, 0, 0)
                self.notify.debug('startPos for %s = %s' % (suit, startPos))
                sfx = loader.loadSfx(
                        "phase_11/audio/sfx/LB_camera_shutter_2.ogg"
                    )
                suitTrack.append(Func(suit.reparentTo, self))
                suitTrack.append(Func(suit.headsUp, self))
                suitTrack.append(Func(suit.hide))
                suitTrack.append(Wait(delay))
                suitTrack.append(Func(suit.show))
                suitTrack.append(LerpPosInterval(suit, 0, startPos))
                suitTrack.append(LerpHprInterval(suit, 0, Vec3(180, 0, 0)))
                suitTrack.append(Parallel(Sequence(Wait(.5), LerpColorScaleInterval(stagelight, .5, VBase4(0, 0, 0, 0))), SoundInterval(sfx, node=suit), random.choice((ActorInterval(suit, 'mob-mentality', startTime=suit.getDuration('mob-mentality') - 1),
                                                ActorInterval(suit, 'small-zap', startTime=suit.getDuration('small-zap') - .75),
                                                ActorInterval(suit, 'slip-backward', startTime=suit.getDuration('slip-backward') - .75),
                                                ActorInterval(suit, 'pie-small-react', startTime=suit.getDuration('pie-small-react') - .75),
                                                ActorInterval(suit, 'rake-react', startTime=suit.getDuration('rake-react') - .75),
                                                ActorInterval(suit, 'finger-wag', startTime=suit.getDuration('finger-wag') - .75)))))
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(Func(stagelight.removeNode))
                suitTrack.append(LerpPosInterval(suit, 0, startPos2))
                suitTracks.append(suitTrack)
                # flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
                suitTrack.append(Track((delay, Sequence(Func(suit.loop, 'neutral')))))
                delay += .15
                if self.hasLocalToon():
                    camera.reparentTo(self)
                    if random.choice([0, 1]):
                        camera.setPosHpr(0, -15, 7, 0, 0, 0)
                    else:
                        camera.setPosHpr(0, -15, 7, 0, 0, 0)
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
                startPos = destPos + Point3(0, 0, 100)
                self.notify.debug('startPos for %s = %s' % (suit, startPos))
                suit.reparentTo(self)
                suit.hide()
                suit.setPos(startPos)
                suit.headsUp(self)
                flyIval = suit.beginSupaFlyMove(destPos, True, 'flyIn')
                taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
                if not suit.dna.name == 'hroller2':
                    suitTrack.append(Track((delay, Sequence(Parallel(Func(suit.show), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), flyIval), Func(suit.loop, 'neutral')))))
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
