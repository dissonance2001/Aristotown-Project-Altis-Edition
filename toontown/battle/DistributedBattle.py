import random
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
from toontown.battle.BattleBase import *
from toontown.battle import DistributedBattleBase
from toontown.battle import SuitBattleGlobals
from otp.avatar import Emote
from toontown.chat.ChatGlobals import *
from toontown.distributed import DelayDelete
from toontown.nametag import NametagGlobals
from toontown.toonbase import ToontownBattleGlobals

class DistributedBattle(DistributedBattleBase.DistributedBattleBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBattle')
    camFOFov = ToontownBattleGlobals.BattleCamFaceOffFov
    camFOPos = ToontownBattleGlobals.BattleCamFaceOffPos
    PlayGameSetPlaceEvent = 'playGameSetPlace'

    def __init__(self, cr):
        townBattle = cr.playGame.hood.loader.townBattle
        DistributedBattleBase.DistributedBattleBase.__init__(self, cr, townBattle)
        self.setupCollisions(self.uniqueBattleName('battle-collide'))

    def generate(self):
        DistributedBattleBase.DistributedBattleBase.generate(self)

    def announceGenerate(self):
        DistributedBattleBase.DistributedBattleBase.generate(self)

    def disable(self):
        DistributedBattleBase.DistributedBattleBase.disable(self)
        self.ignore(self.PlayGameSetPlaceEvent)

    def delete(self):
        DistributedBattleBase.DistributedBattleBase.delete(self)
        self.ignore(self.PlayGameSetPlaceEvent)
        self.removeCollisionData()

    def setInteractivePropTrackBonus(self, trackBonus):
        DistributedBattleBase.DistributedBattleBase.setInteractivePropTrackBonus(self, trackBonus)
        if self.interactivePropTrackBonus >= 0:
            if base.cr.playGame.hood:
                self.calcInteractiveProp()
            else:
                self.acceptOnce(self.PlayGameSetPlaceEvent, self.calcInteractiveProp)

    def calcInteractiveProp(self):
        if base.config.GetBool('want-anim-props', True):
            if base.cr.playGame.hood:
                loader = base.cr.playGame.hood.loader
                if hasattr(loader, 'getInteractiveProp'):
                    self.interactiveProp = loader.getInteractiveProp(self.zoneId)
                    self.notify.debug('self.interactiveProp = %s' % self.interactiveProp)
                else:
                    self.notify.warning('No loader.getInteractiveProp for battle! self.interactiveProp is None')
            else:
                self.notify.warning('No hood? self.interactiveProp is None')

    def setMembers(self, suits, suitsJoining, suitsPending, suitsActive, suitsLured, suitTraps, toons, toonsJoining, toonsPending, toonsActive, toonsRunning, immuneSuits, enragedSuits, absorbingSuits, soakedSuits, timestamp):
        if self.battleCleanedUp():
            return
        oldtoons = DistributedBattleBase.DistributedBattleBase.setMembers(self, suits, suitsJoining, suitsPending, suitsActive, suitsLured, suitTraps, toons, toonsJoining, toonsPending, toonsActive, toonsRunning, immuneSuits, enragedSuits, absorbingSuits, soakedSuits, timestamp)
        if len(self.toons) == 4 and len(oldtoons) < 4:
            self.notify.debug('setMembers() - battle is now full of toons')
            self.closeBattleCollision()
        elif len(self.toons) < 4 and len(oldtoons) == 4:
            self.openBattleCollision()

    def __faceOff(self, ts, name, callback):
        if len(self.suits) == 0:
            self.notify.warning('__faceOff(): no suits.')
            return
        if len(self.toons) == 0:
            self.notify.warning('__faceOff(): no toons.')
            return

        # Pick only the first suit for the faceoff, if there happen to
        # be more than one.
        suit = self.suits[0]
        point = self.suitPoints[0][0]
        suitPos = point[0]
        suitHpr = VBase3(point[1], 0.0, 0.0)

        # And ditto for the first toon.
        toon = self.toons[0]
        toon.getGeomNode().setH(0.0)
        point = self.toonPoints[0][0]
        toonPos = point[0]
        toonHpr = VBase3(point[1], 0.0, 0.0)

        p = toon.getPos(self)
        toon.setPos(self, p[0], p[1], 0.0)
        toon.setShadowHeight(0)
        toon.loop('neutral')
        toon.headsUp(suit)

        suit.setState('Battle')
        suit.loop('neutral')
        suit.headsUp(toon)

        suitTrack: Sequence = Sequence()
        toonTrack: Sequence = Sequence()

        # Make suit and toon face each other (and exchange taunts)
        taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)

        suitTrack.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

        suitHeight = suit.getHeight()
        suitOffsetPnt = Point3(0.0, 0.0, suitHeight)

        # Determine the battle positions based on initial angle
        # between the suit and the battle center (we want the suit to walk
        # as short a distance as possible)
        faceoffTime = self.calcFaceoffTime(self.getPos(), self.initialSuitPos)
        # Make sure the faceoff time is non-zero
        faceoffTime = max(faceoffTime, BATTLE_SMALL_VALUE)
        camSeqLength: float = 0.3
        delay: float = FACEOFF_TAUNT_T + camSeqLength

        if self.hasLocalToon():
            # Empirical hack to pick a mid-height view, left in to sortof match the old view
            MidTauntCamHeight = suitHeight * 0.66
            MidTauntCamHeightLim = suitHeight - 1.8
            if MidTauntCamHeight < MidTauntCamHeightLim:
                MidTauntCamHeight = MidTauntCamHeightLim

            TauntCamY: float = 16.0
            TauntCamX: float = random.choice((-5.0, 5.0))
            TauntCamHeight = random.choice((MidTauntCamHeight, 1.0, 11.0))

            camPos = suit.attachNewNode('camPos')
            camPos.setPos(TauntCamX, TauntCamY, TauntCamHeight)
            camPos.lookAt(suit, suitOffsetPnt)
            pos, hpr = camPos.getPos(camera.getParent()), camPos.getHpr(camera.getParent())

            camTrack = Sequence(
                Func(base.camLens.setMinFov, self.camFOFov/(4./3.)),
                Func(camera.setPos, pos),
                Func(camera.lookAt, suit, suitOffsetPnt),
                Wait(delay)
            )
            camTrack.append(Func(base.camLens.setMinFov, self.camFov/(4./3.)))
            camTrack.append(Func(camera.wrtReparentTo, self))
            camTrack.append(Func(camera.setPos, self.camFOPos))
            camTrack.append(Func(camera.lookAt, suit.getPos(self)))
            camTrack.append(Wait(min(faceoffTime, self.FLY_IN_CUTOFF_DUR)))
            if self.interactiveProp:
                camTrack.append(Func(camera.lookAt, self.interactiveProp.node.getPos(self)))
                camTrack.append(Wait(FACEOFF_LOOK_AT_PROP_T))
        
        suitTrack.append(Wait(delay))
        toonTrack.append(Wait(delay))

        # Make suit and toon face their destination spots in battle
        suitTrack.append(Func(suit.headsUp, self, suitPos))
        suitTrack.append(Func(suit.clearChat))
        suitTrack.append(Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))
        toonTrack.append(Func(toon.headsUp, self, toonPos))

        # Make suit and toon walk to their battle spots
        if faceoffTime > self.FLY_IN_CUTOFF_DUR:
            dummy = suit.attachNewNode('dummy')
            dummy.setPos(self, suitPos)
            dummyPos = dummy.getPos(render)
            dummy.detachNode()

            suit.attachPropeller()
            suit.prop.hide()

            # Incoming copypaste stuff from DistributedBattleDiners
            landingDur = suit.getDuration('landing')
            fr = suit.getFrameRate('landing')

            # length of time in animation spent in the air
            flyingDur = 4.0 - landingDur

            lastSpinFrame: int = 8
            fr = suit.prop.getFrameRate('propeller')
            # Time from beginning of anim at which propeller plays its spin
            spinTime = lastSpinFrame / fr
            # Time from beginning of anim at which propeller starts to close
            openTime = (lastSpinFrame + 1) / fr

            suitTrack.append(Parallel(
                Sequence(
                    Func(suit.pose, 'landing', 0),
                    ProjectileInterval(suit, endPos=dummyPos, duration=3.0, gravityMult=0.25),
                    ActorInterval(suit, 'landing')
                ),
                Sequence(
                    Func(suit.prop.show),
                    Parallel(
                        SoundInterval(suit.propInSound, duration=flyingDur + 1.0, node=suit),
                        Sequence(
                            ActorInterval(suit.prop, 'propeller', constrainedLoop=1, duration=flyingDur + 2.0, startTime=0.0, endTime=spinTime),
                            Func(suit.detachPropeller)
                        )
                    )
                )
            ))
        else:
            suitTrack.append(Func(suit.loop, 'walk'))
            suitTrack.append(Func(suit.enableRaycast, 1))
            suitTrack.append(LerpPosInterval(suit, faceoffTime, suitPos, other=self))
            suitTrack.append(Func(suit.enableRaycast, 0))

        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTrack.append(Func(suit.setHpr, self, suitHpr))
        suitTrack.append(Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))

        soundTrack = Wait(delay + min(faceoffTime, self.FLY_IN_CUTOFF_DUR))

        if faceoffTime > self.FLY_IN_CUTOFF_DUR:
            toonTrack.append(toon.getTeleportOutTrack())
            toonTrack.append(Func(toon.setPosHpr, self, toonPos, toonHpr))
            toonTrack.append(toon.getTeleportInTrack())
            toonTrack.append(Func(toon.loop, 'neutral'))
        else:
            toonTrack.append(Func(toon.loop, 'run'))
            toonTrack.append(LerpPosInterval(toon, faceoffTime, toonPos, other=self))
            toonTrack.append(Func(toon.loop, 'neutral'))
            toonTrack.append(Func(toon.setHpr, self, toonHpr))

            if toon.isLocal():
                soundTrack = Sequence(
                    Wait(delay),
                    SoundInterval(base.localAvatar.soundRun, loop=1, duration=faceoffTime, node=base.localAvatar)
                )

        mtrack: Parallel = Parallel(suitTrack, toonTrack, soundTrack)

        if self.hasLocalToon():
            NametagGlobals.setWant2dNametags(False)
            mtrack = Parallel(mtrack, camTrack)

        done = Func(callback)
        track: Sequence = Sequence(mtrack, done, name=name)
        track.delayDeletes = [DelayDelete.DelayDelete(toon, '__faceOff'), DelayDelete.DelayDelete(suit, '__faceOff')]
        track.start(ts)
        self.storeInterval(track, name)

    def enterFaceOff(self, ts):
        self.notify.debug('enterFaceOff()')
        self.delayDeleteMembers()
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            Emote.globalEmote.disableAll(self.toons[0], 'dbattle, enterFaceOff')
        self.__faceOff(ts, self.faceOffName, self.__handleFaceOffDone)
        if self.interactiveProp:
            self.interactiveProp.gotoFaceoff()

    def __handleFaceOffDone(self):
        self.notify.debug('FaceOff done')
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            self.d_faceOffDone(base.localAvatar.doId)

    def exitFaceOff(self):
        self.notify.debug('exitFaceOff()')
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            Emote.globalEmote.releaseAll(self.toons[0], 'dbattle exitFaceOff')
        self.finishInterval(self.faceOffName)
        self.clearInterval(self.faceOffName)
        self._removeMembersKeep()

    def enterReward(self, ts):
        self.notify.debug('enterReward()')
        self.disableCollision()
        self.delayDeleteMembers()
        Emote.globalEmote.disableAll(base.localAvatar, 'dbattle, enterReward')
        if self.hasLocalToon():
            NametagGlobals.setWant2dNametags(False)
            if self.localToonActive() == 0:
                self.removeInactiveLocalToon(base.localAvatar)
        for toon in self.toons:
            toon.startSmooth()

        self.accept('resumeAfterReward', self.handleResumeAfterReward)
        if self.interactiveProp:
            self.interactiveProp.gotoVictory()
        
        self.playReward(ts)

    def playReward(self, ts):
        self.movie.playReward(ts, self.uniqueName('reward'), self.handleRewardDone)

    def handleRewardDone(self):
        self.notify.debug('Reward done')
        if self.hasLocalToon():
            self.d_rewardDone(base.localAvatar.doId)
        
        self.movie.resetReward()
        messenger.send('resumeAfterReward')

    def handleResumeAfterReward(self):
        self.fsm.request('Resume')

    def exitReward(self):
        self.notify.debug('exitReward()')
        self.ignore('resumeAfterReward')
        self.movie.resetReward(finish=1)
        self._removeMembersKeep()
        NametagGlobals.setWant2dNametags(True)
        Emote.globalEmote.releaseAll(base.localAvatar, 'dbattle, exitReward')

    def enterResume(self, ts = 0):
        self.notify.debug('enterResume()')
        if self.hasLocalToon():
            self.removeLocalToon()
        
        if self.interactiveProp:
            self.interactiveProp.requestIdleOrSad()

    def exitResume(self):
        pass

    def enterNoLocalToon(self):
        self.notify.debug('enterNoLocalToon()')
        self.enableCollision()

    def exitNoLocalToon(self):
        self.disableCollision()

    def enterWaitForServer(self):
        self.notify.debug('enterWaitForServer()')

    def exitWaitForServer(self):
        pass
