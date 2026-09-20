from panda3d.core import ConfigVariableBool, Point3, VBase3
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout
from toontown.nametag import NametagGlobals
from direct.interval.IntervalGlobal import *
from direct.showbase.MessengerGlobal import messenger

from toontown.clashbattle.battle import BattleMusicListener, SuitBattleGlobals
from toontown.clashbattle.battle.BattleBase import *
from toontown.clashbattle.battle.distributed import DistributedBattleBase
from toontown.discord import DiscordPresets
from toontown.distributed import DelayDelete
from toontown.hood import ZoneUtil
from toontown.toon import TTEmote
from toontown.clashbattle.battle import BattleGlobals
from toontown.discord.DiscordPresets import presets as discord_presets


class DistributedBattle(DistributedBattleBase.DistributedBattleBase):
    camFOFov = BattleGlobals.BattleCamFaceOffFov
    camFOPos = BattleGlobals.BattleCamFaceOffPos
    # this event comes from PlayGame.setPlace()
    PlayGameSetPlaceEvent = 'playGameSetPlace'

    def __init__(self, cr):
        townBattle = cr.playGame.hood.loader.townBattle
        DistributedBattleBase.DistributedBattleBase.__init__(self, cr, townBattle)
        self.setupCollisions(self.uniqueBattleName('battle-collide'))
        self.battleMusicListener = BattleMusicListener.BattleMusicListener()
        self.listenerZone = cr.playGame.hood.hoodId

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
        
    ##### Messages From The Server #####

    def setMembers(self, suits, suitTraps, toons, timestamp):
        if self.battleCleanedUp():
            return

        super().setMembers(suits, suitTraps, toons, timestamp)

        if self.hasLocalToon():
            if not self.battleMusicListener.storedMusic:
                self.battleMusicListener.playMusic(self.suits, zone=[
                        self.listenerZone, base.cr.playGame.getPlace().getZoneId()])

            manager_fight = False
            zoneId = ZoneUtil.getBranchZone(base.localAvatar.zoneId)
            for suit in self.suits:
                if suit and suit.dna and suit.dna.name in TTLocalizer.StreetManagers:
                    if zoneId in TTLocalizer.GlobalStreetNames:
                        base.discord.applyPreset(suit.dna.name, hover_fillin=TTLocalizer.GlobalStreetNames[zoneId][2])
                    manager_fight = True
            if not manager_fight:
                if zoneId in DiscordPresets.zones:
                    name_dat = TTLocalizer.GlobalStreetNames[zoneId]
                    base.discord.applyPreset('cog_battle', fillin=(name_dat[1], name_dat[2]))

        # If the battle is full, we need to make the collision sphere
        # tangible so other toons can't walk through the battle
        if len(self.toons) >= 4:
            self.notify.debug('setMembers() - battle is now full of toons')
            self.closeBattleCollision()
        else:
            self.openBattleCollision()

    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    # Specific State functions

    ##### Off state #####

    ##### FaceOff state #####

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
        toon.getGeomNode().setH(0)
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

        suitTrack = Sequence()
        toonTrack = Sequence()

        # Make suit and toon face each other (and exchange taunts)
        taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)

        suitTrack.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

        suitHeight = suit.getHeight()
        suitOffsetPnt = Point3(0, 0, suitHeight)

        # Determine the battle positions based on initial angle
        # between the suit and the battle center (we want the suit to walk
        # as short a distance as possible)
        faceoffTime = self.calcFaceoffTime(self.getPos(), self.initialSuitPos)
        # Make sure the faceoff time is non-zero
        faceoffTime = max(faceoffTime, BATTLE_SMALL_VALUE)
        camSeqLength = 0.3
        delay = FACEOFF_TAUNT_T + camSeqLength

        if self.hasLocalToon():
            # kill the local toon sprint sequence
            base.localAvatar.stopSprintFovSeq()

            # Empirical hack to pick a mid-height view, left in to sortof match the old view
            MidTauntCamHeight = suitHeight * 0.66
            MidTauntCamHeightLim = suitHeight - 1.8
            if MidTauntCamHeight < MidTauntCamHeightLim:
                MidTauntCamHeight = MidTauntCamHeightLim

            TauntCamY = 16
            TauntCamX = random.choice((-5, 5))
            TauntCamHeight = random.choice((MidTauntCamHeight, 1, 11))

            camPos = suit.attachNewNode("camPos")
            camPos.setPos(TauntCamX, TauntCamY, TauntCamHeight)
            camPos.lookAt(suit, suitOffsetPnt)
            pos, hpr = camPos.getPos(camera.getParent()), camPos.getHpr(camera.getParent())
            camPos.detachNode()

            if base.settings["reduce-battle-effects"]:
                camTrack = Sequence(
                    Func(base.camLens.setMinFov, self.camFOFov/(4./3.)),
                    Func(camera.setPos, pos),
                    Func(camera.lookAt, suit, suitOffsetPnt),
                    Wait(delay)
                )
            else:
                camTrack = Sequence(
                    Parallel(
                        LerpPosHprInterval(
                            camera, camSeqLength, 
                            pos, hpr, 
                            startPos=camera.getPos(), startHpr=camera.getHpr(),
                            blendType='easeInOut'
                        ),
                        LerpFunc(
                            base.camLens.setMinFov, 
                            camSeqLength, 
                            base.camLens.getMinFov(), 
                            self.camFOFov / (4/3),
                        ),
                    ),
                    Wait(delay - camSeqLength)
                )
            camTrack.append(Func(base.camLens.setMinFov, self.camFov/(4./3.)))
            camTrack.append(Func(camera.wrtReparentTo, self))
            camTrack.append(Func(camera.setPos, self.camFOPos))
            camTrack.append(Func(camera.lookAt, suit.getPos(self)))
            camTrack.append(Wait(min(faceoffTime, self.FLY_IN_CUTOFF_DUR)))

        suitTrack.append(Wait(delay))
        toonTrack.append(Wait(delay))

        # Make suit and toon face their destination spots in the battle
        suitTrack.append(Func(suit.headsUp, self, suitPos))
        suitTrack.append(Func(suit.clearChat))
        toonTrack.append(Func(toon.headsUp, self, toonPos))

        # Make suit and toon walk to their battle spots
        if faceoffTime > self.FLY_IN_CUTOFF_DUR:
            dummy = suit.attachNewNode("dummy")
            dummy.setPos(self, suitPos)
            dummyPos = dummy.getPos(render)
            dummy.detachNode()

            suit.attachPropeller()
            suit.prop.hide()

            # incoming copypaste stuff from DistributedBattleDiners
            landingDur = suit.getDuration('landing')
            fr = suit.getFrameRate('landing')

            # length of time in animation spent in the air
            flyingDur = 4 - landingDur

            lastSpinFrame = 8
            fr = suit.prop.getFrameRate('propeller')
            # Time from beginning of anim at which propeller plays its spin
            spinTime = lastSpinFrame / fr
            # Time from beginning of anim at which propeller starts to close
            openTime = (lastSpinFrame + 1) / fr

            suitTrack.append(
                Parallel(
                    Sequence(
                        Func(suit.pose, 'landing', 0),
                        ProjectileInterval(suit, endPos=dummyPos, duration=3, gravityMult=0.25),
                        ActorInterval(suit, 'landing')
                    ),
                    Sequence(
                        Func(suit.prop.show),
                        Parallel(
                            SoundInterval(suit.propInSound, duration=flyingDur + 1, node=suit),
                            Sequence(
                                ActorInterval(
                                    suit.prop, 'propeller', constrainedLoop=1, duration=flyingDur + 2,
                                    startTime=0.0, endTime=spinTime
                                ),
                                ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime),
                                Func(suit.detachPropeller)
                            ),
                        )
                    )
                )
            )
        else:
            suitTrack.append(Func(suit.loop, 'walk'))
            suitTrack.append(Func(suit.enableRaycast, 1))
            suitTrack.append(LerpPosInterval(suit, faceoffTime, suitPos, other=self))
            suitTrack.append(Func(suit.enableRaycast, 0))

        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTrack.append(Func(suit.setHpr, self, suitHpr))

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

        mtrack = Parallel(suitTrack, toonTrack, soundTrack)

        if self.hasLocalToon():
            # No arrows - they just get in the way
            NametagGlobals.setMasterArrowsOn(0)
            mtrack = Parallel(mtrack, camTrack)

        done = Func(callback)
        track = Sequence(mtrack, done, name=name)
        track.delayDeletes = [DelayDelete.DelayDelete(toon, '__faceOff'), DelayDelete.DelayDelete(suit, '__faceOff')]
        track.start(ts)
        self.storeInterval(track, name)

    def enterFaceOff(self, ts):
        self.notify.debug('enterFaceOff()')
        self.delayDeleteMembers()
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            TTEmote.globalEmote.disableAll(self.toons[0], 'dbattle, enterFaceOff')
        self.__faceOff(ts, self.faceOffName, self.__handleFaceOffDone)
        if self.hasLocalToon() and not self.battleMusicListener.storedMusic:
            self.battleMusicListener.playMusic(self.suits, zone=[self.listenerZone, base.cr.playGame.getPlace().getZoneId()])

    def __handleFaceOffDone(self):
        self.notify.debug('FaceOff done')
        # Only the toon that initiated the battle needs to reply
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            self.d_faceOffDone(base.localAvatar.doId)

    def exitFaceOff(self):
        self.notify.debug('exitFaceOff()')
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            TTEmote.globalEmote.releaseAll(self.toons[0], 'dbattle exitFaceOff')
        self.finishInterval(self.faceOffName)
        # Remove the delayDelete, so an exited toon doesn't hang around
        self.clearInterval(self.faceOffName)
        self._removeMembersKeep()
        
    ##### WaitForInput state #####

    ##### PlayMovie state #####

    ##### Reward state #####

    def enterReward(self, ts):
        self.notify.debug('enterReward()')
        self.disableCollision()
        self.delayDeleteMembers()
        TTEmote.globalEmote.disableAll(base.localAvatar, 'dbattle, enterReward')

        if self.hasLocalToon():
            NametagGlobals.setMasterArrowsOn(0)
            base.cr.gameGui.expBar.show()
            if self.localToonActive() == 0:
                self.removeInactiveLocalToon(base.localAvatar)
    
        # Some of the toons may finish the movie before we do; be
        # prepared to show them moving around when they do.
        for toon in self.toons:
            toon.startSmooth()

        self.accept('resumeAfterReward', self.handleResumeAfterReward)
        self.playReward(ts)

    def playReward(self, ts):
        self.movie.playReward(ts, self.uniqueName('reward'), self.handleRewardDone)

    def handleRewardDone(self):
        self.notify.debug('Reward done')
        if self.hasLocalToon():
            self.d_rewardDone(base.localAvatar.doId)
            id = ZoneUtil.getBranchZone(base.localAvatar.zoneId)
            if id in DiscordPresets.zones:
                base.discord.setZone(id)


        self.movie.resetReward()
        
        # Now request our local battle object enter the Resume state,
        # which frees us from the battle.  The distributed object may
        # not enter the Resume state yet (it has to wait until all the
        # toons involved have reported back up), but there's no reason
        # we have to wait around for that.

        # We have to send a message, instead of directly asking the
        # ClassicFSM to switch states, since we might call this method when
        # we finish the track in exitReward().
        messenger.send('resumeAfterReward')

    def handleResumeAfterReward(self):
        self.request('Resume')

    def exitReward(self):
        self.notify.debug('exitReward()')
        self.ignore('resumeAfterReward')
        if self.hasLocalToon():
            self.battleMusicListener.stopMusic()
        # In case we're observing and the server cuts us off
        # this guarantees all final animations get started and things
        # get cleaned up
        self.movie.resetReward(finish=1)
        self._removeMembersKeep()
        if self.hasLocalToon():
            NametagGlobals.setMasterArrowsOn(1)
        TTEmote.globalEmote.releaseAll(base.localAvatar, 'dbattle, exitReward')
        
    ##### Resume state #####

    def enterResume(self, ts = 0):
        self.notify.debug('enterResume()')
        if self.hasLocalToon():
            self.removeLocalToon()

    def exitResume(self):
        pass
        
    #########################
    ##### LocalToon ClassicFSM #####
    #########################

    ##### HasLocalToon state #####

    ##### NoLocalToon state #####

    def enterNoLocalToon(self):
        self.notify.debug('enterNoLocalToon()')
        # Enable battle collision sphere
        self.enableCollision()

    def exitNoLocalToon(self):
        # Disable battle collision sphere
        self.disableCollision()
        
    ##### WaitForServer state #####

    def enterWaitForServer(self):
        self.notify.debug('enterWaitForServer()')

    def exitWaitForServer(self):
        pass
