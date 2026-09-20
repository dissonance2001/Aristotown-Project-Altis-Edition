from direct.interval.IntervalGlobal import *
from toontown.clashbattle.battle.BattleBase import *
from toontown.clashbattle.battle.BuildingBattleCamera import BuildingBattleCamera
from toontown.clashbattle.battle.distributed.DistributedBattleBase import DistributedBattleBase
from toontown.clashbattle.battle import SuitBattleGlobals
from otp import *
from toontown.clashsuit.suit import SuitDNA
from toontown.toon import TTEmote
from toontown.toonbase import TTLocalizer
from toontown.distributed import DelayDelete
from toontown.chat.constants.ChatGlobals import CFSpeech, CFTimeout
from toontown.nametag import NametagGlobals


class DistributedBattleBldg(DistributedBattleBase):
    CAMERA_CLASS = BuildingBattleCamera
    camFOFov = 30.0
    camFOPos = Point3(0, -10, 4)

    # Add a new reward state to the battle FSM
    defaultTransitions = DistributedBattleBase.defaultTransitions.copy()
    defaultTransitions.update({
        "BuildingReward": ["Resume"],
    })
    for state in ("Off", "PlayMovie"):
        defaultTransitions[state].append("BuildingReward")

    def __init__(self, cr):
        townBattle = base.cr.playGame.getPlace().townBattle
        DistributedBattleBase.__init__(self, cr, townBattle)

        self.streetBattle = 0

    def generate(self):
        DistributedBattleBase.generate(self)

    def setBossBattle(self, value):
        self.bossBattle = value

    def getBossBattleTaunt(self):
        return TTLocalizer.BattleBldgBossTaunt

    def buildJoinPointList(self, avPos, destPos, toon = 0):
        """ buildJoinPointList(avPos, destPos, toon)
        This function is called when suits or toons ask to join the
        battle and need to figure out how to walk to their selected
        pending point (destPos).  It builds a list of points the
        avatar should walk through in order to get there.  If the list
        is empty, the avatar will walk straight there.
        """
        # For building battles, suits and toons are already set up to
        # walk pretty much straight to their join spot.  Always return
        # an empty list here.
        return []
        
    # Each state will have an enter function, an exit function,
    # and a datagram handler, which will be set during each enter function.

    # Specific State functions

    ##### Off state #####

    ##### FaceOff state #####

    def moveSuitToActivePos(self, suit, ts):
        """Custom adjust interval for suits in a building."""
        trackName = self.taskName('to-pending-suit-%d' % suit.doId)
        destPos, destHpr = self.getActorPosHpr(suit, self.suits)

        adjustTimeMod = 0.5 if not self.activeSuits else 1
        playRate = 1.25 if not self.activeSuits else 1
        basePlayRate = suit.getPlayRate('walk')

        checkpoint = suit.getPos(self)
        checkpoint.setY(checkpoint.getY() - 10)

        adjustTime = self.calcSuitMoveTime(destPos, checkpoint) * adjustTimeMod

        track = Sequence(
            Func(suit.setPlayRate, basePlayRate * playRate, 'walk'),
            Func(suit.loop, 'walk'),
            LerpPosInterval(suit, 1.5, checkpoint),
            Func(suit.headsUp, self, destPos),
            LerpPosInterval(suit, adjustTime, destPos, other=self),
            Func(suit.setHpr, self, destHpr),
            Func(suit.setPlayRate, basePlayRate, 'walk'),
            Func(suit.neutralAvatar),
            Func(self._handleSuitJoinDone, suit, ts, False),
            name=trackName
        )
        playRate = self.timescale
        track.start(ts, playRate=playRate)

        track.delayDelete = DelayDelete.DelayDelete(suit, 'moveSuitToActivePos')

        self.storeInterval(track, trackName)

    def __faceOff(self, ts, name, callback):
        if len(self.suits) == 0:
            self.notify.warning('__faceOff(): no suits.')
            return
        if len(self.toons) == 0:
            self.notify.warning('__faceOff(): no toons.')
            return
            
        # Do the suits faceoff
        # TODO: get the actual position of the elevator door
        elevatorPos = self.toons[0].getPos()
        if len(self.suits) == 1:
            leaderIndex = 0
        elif self.bossBattle == 1:
            leaderIndex = 1 # __genSuitInfos ensures that multi-suit boss battles will have boss in index 1 (a middle position)
        else:
            # otherwise __genSuitInfos ensures nothing, so pick the suit with the highest type to be the leader
            maxTypeNum = -1
            for suit in self.suits:
                suitTypeNum = SuitDNA.getSuitType(suit.dna.name)
                if maxTypeNum < suitTypeNum:
                    maxTypeNum = suitTypeNum
                    leaderIndex = self.suits.index(suit)

        camSeqLength = 0.3
        delay = FACEOFF_TAUNT_T + camSeqLength
        suitTrack = Parallel()
        suitLeader = None
        for suit in self.suits:
            suit.setState('Battle')
            # Suits stop what they're doing and look at the toons
            suit.loop('neutral')
            suit.headsUp(elevatorPos)
            suitIsLeader = 0
            oneSuitTrack = Sequence()
            
            # Only the suit leader taunts the toons
            if self.suits.index(suit) == leaderIndex:
                suitLeader = suit
                suitIsLeader = 1
                
                # TODO: have an inside of building taunt here
                if self.bossBattle == 1:
                    taunt = self.getBossBattleTaunt()
                else:
                    taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)

                oneSuitTrack.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

            # Move all suits into position after taunt delay
            destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            oneSuitTrack.append(Wait(delay))
            if suitIsLeader == 1:
                oneSuitTrack.append(Func(suit.clearChat))
            oneSuitTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
            suitTrack.append(oneSuitTrack)

        # Do the toons faceoff 
        toonTrack = Parallel()
        for toon in self.toons:
            oneToonTrack = Sequence()
            destPos, destHpr = self.getActorPosHpr(toon, self.toons)
            oneToonTrack.append(Wait(delay))
            oneToonTrack.append(self.createAdjustInterval(toon, destPos, destHpr, toon=1, run=1))
            toonTrack.append(oneToonTrack)

        def setCamFov(fov):
            base.camLens.setMinFov(fov/(4./3.))

        suitHeight = suitLeader.getHeight()
        suitOffsetPnt = Point3(0, 0, suitHeight)
        
        # Empirical hack to pick a mid-height view, left in to sortof match the old view
        MidTauntCamHeight = suitHeight * 0.66
        MidTauntCamHeightLim = suitHeight - 1.8
        if MidTauntCamHeight < MidTauntCamHeightLim:
            MidTauntCamHeight = MidTauntCamHeightLim

        TauntCamY = 18
        TauntCamX = 0
        TauntCamHeight = random.choice((MidTauntCamHeight, 1, 11))

        camPos = suitLeader.attachNewNode("camPos")
        camPos.setPos(TauntCamX, TauntCamY, TauntCamHeight)
        camPos.lookAt(suitLeader, suitOffsetPnt)
        pos, hpr = camPos.getPos(camera.getParent()), camPos.getHpr(camera.getParent())
        camPos.detachNode()

        if base.settings["reduce-battle-effects"]:
            camTrack = Sequence(
                Func(base.camLens.setMinFov, self.camFOFov/(4./3.)),
                Func(camera.setPos, pos),
                Func(camera.lookAt, suitLeader, suitOffsetPnt),
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

        camPos = Point3(0, -6, 4)
        camHpr = Vec3(0, 0, 0)
        camTrack.append(Func(camera.wrtReparentTo, base.localAvatar))
        camTrack.append(Func(setCamFov, settings['fieldofview']))
        camTrack.append(Func(camera.setPosHpr, camPos, camHpr))

        mtrack = Parallel(suitTrack, toonTrack, camTrack)
        done = Func(callback)
        track = Sequence(mtrack, done, name=name)
        track.start(ts)
        self.storeInterval(track, name)

    def enterFaceOff(self, ts):
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            TTEmote.globalEmote.disableAll(self.toons[0], 'dbattlebldg, enterFaceOff')
        self.delayDeleteMembers()
        self.__faceOff(ts, self.faceOffName, self.__handleFaceOffDone)

    def __handleFaceOffDone(self):
        self.notify.debug('FaceOff done')
        # Only the toon that initiated the battle needs to reply
        self.d_faceOffDone(base.localAvatar.doId)

    def exitFaceOff(self):
        self.notify.debug('exitFaceOff()')
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            TTEmote.globalEmote.releaseAll(self.toons[0], 'dbattlebldg exitFaceOff')
        self.clearInterval(self.faceOffName)
        self._removeMembersKeep()
        camera.wrtReparentTo(self)
        base.camLens.setMinFov(self.camFov/(4./3.))

    ##### WaitForInput state #####

    ##### PlayMovie state #####

    ##### Reward state #####

    def __playReward(self, ts, callback):
        toonTracks = Parallel()
        for toon in self.toons:
            toonTracks.append(Sequence(Func(toon.loop, 'victory'), Wait(FLOOR_REWARD_TIMEOUT), Func(toon.loop, 'neutral')))

        name = self.uniqueName('floorReward')
        track = Sequence(toonTracks, Func(callback), name=name)
        camera.posHprInterval(1, Point3(0, 0, 1), Point3(180, 10, 0), blendType = 'easeInOut').start()
        self.storeInterval(track, name)
        track.start(ts)

    def enterReward(self, ts):
        self.notify.debug('enterReward()')
        self.delayDeleteMembers()
        if self.hasLocalToon():
            base.cr.gameGui.expBar.show()
        self.__playReward(ts, self.__handleFloorRewardDone)

    def __handleFloorRewardDone(self):
        pass

    def exitReward(self):
        self.notify.debug('exitReward()')
        self.clearInterval(self.uniqueName('floorReward'))
        self._removeMembersKeep()
        NametagGlobals.setMasterArrowsOn(1)
        for toon in self.toons:
            toon.startSmooth()
            
    ##### BuildingReward state #####

    def enterBuildingReward(self, ts):
        self.delayDeleteMembers()
        if self.hasLocalToon():
            NametagGlobals.setMasterArrowsOn(0)
            base.cr.gameGui.expBar.show()
        self.movie.playReward(ts, self.uniqueName('building-reward'), self.__handleBuildingRewardDone, noSkip=True)

    def __handleBuildingRewardDone(self):
        if self.hasLocalToon():
            self.d_rewardDone(base.localAvatar.doId)
        self.movie.resetReward()
        
        # Now request our local battle object enter the Resume state,
        # which frees us from the battle.  The distributed object may
        # not enter the Resume state yet (it has to wait until all the
        # toons involved have reported back up), but there's no reason
        # we have to wait around for that.
        if not self.isInTransition():
            self.request('Resume')

    def exitBuildingReward(self):
        # In case we're observing and the server cuts us off
        # this guarantees all final animations get started and things
        # get cleaned up
        self.movie.resetReward(finish=1)
        self._removeMembersKeep()
        NametagGlobals.setMasterArrowsOn(1)
        
    ##### Resume state #####

    def enterResume(self, ts=0):
        if self.hasLocalToon():
            self.removeLocalToon()

    def exitResume(self):
        pass
