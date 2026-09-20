from direct.interval.IntervalGlobal import *
from otp.nametag import NametagGlobals
from toontown.chat.constants.ChatGlobals import CFSpeech, CFTimeout
from toontown.battle.distributed import DistributedBattle
from toontown.battle import SuitBattleGlobals
from toontown.battle.BattleBase import *
from otp import *
from toontown.suit import SuitDNA
from toontown.battle import BattleMusicListener
from toontown.toon import TTEmote
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.distributed.ToontownClientRepository import ToontownClientRepository


@DirectNotifyCategory()
class DistributedPersistentLevelBattle(DistributedBattle.DistributedBattle):
    """
    DistributedPersistentLevelBattle(DistributedBattle)
    """

    def __init__(self, cr):
        """
        :param ToontownClientRepository cr: The client repository which maintains all client-side distributed objects.
        """
        self.notify.debug("init")
        DistributedBattle.DistributedBattle.__init__(self, cr)
        self.levelRequest = None
        self.levelBattle = 1
        self.battleMusicListener = BattleMusicListener.BattleMusicListener()

    def setLevelDoId(self, levelDoId):
        self.levelDoId = levelDoId

    def setBattleCellId(self, battleCellId):
        self.battleCellId = battleCellId

        def doPlacement(levelList, self = self):
            self.levelRequest = None
            self.level = levelList[0]
            battleCell = self.level.getEntity(self.battleCellId)
            self.level.requestReparent(self, battleCell.parentEntId)
            self.setPos(battleCell.pos)
            self.notify.debug('h = %s' % battleCell.getH())
            self.wrtReparentTo(render)
            return

        level = base.cr.doId2do.get(self.levelDoId)
        if level is None:
            self.notify.warning(
                'level %s not in doId2do yet, battle %s will be mispositioned.' % self.levelDoId, self.doId
            )
            self.levelRequest = self.cr.relatedObjectMgr.requestObjects([self.levelDoId], doPlacement)
        else:
            doPlacement([level])
        return

    def setPosition(self, *args):
        pass

    def setInitialSuitPos(self, x, y, z):
        """
        generates a Point3 vector given x y z components

        :type x: float
        :type y: float
        :type z: float
        """
        self.initialSuitPos = Point3(x, y, z)

    def disable(self):
        """
        Called when the DistributedObject is removed from active duty and stored in a cache.
        """
        if self.hasLocalToon():
            self.unlockLevelViz()
        if self.levelRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.levelRequest)
            self.levelRequest = None
        DistributedBattle.DistributedBattle.disable(self)
        return

    def delete(self):
        self.ignoreAll()
        DistributedBattle.DistributedBattle.delete(self)

    def handleBattleBlockerCollision(self):
        messenger.send(self.getCollisionName(), [None])
        return

    def lockLevelViz(self):
        level = base.cr.doId2do.get(self.levelDoId)
        if level:
            level.lockVisibility(zoneId = self.zoneId)
        else:
            self.notify.warning("lockLevelViz: couldn't find level %s" % self.levelDoId)

    def unlockLevelViz(self):
        level = base.cr.doId2do.get(self.levelDoId)
        if level:
            level.unlockVisibility()
        else:
            self.notify.warning("unlockLevelViz: couldn't find level %s" % self.levelDoId)

    def onWaitingForJoin(self):
        self.lockLevelViz()
        if self.hasLocalToon() and not self.battleMusicListener.storedMusic:
            self.battleMusicListener.playMusic(self.suits, zone=[base.cr.playGame.getPlace().getZoneId()])

    def __faceOff(self, ts, name, callback):
        if len(self.suits) == 0:
            self.notify.warning('__faceOff(): no suits.')
            return
        if len(self.toons) == 0:
            self.notify.warning('__faceOff(): no toons.')
            return
        toon = self.toons[0]
        point = self.toonPoints[0][0]
        toonPos = point[0]
        toonHpr = VBase3(point[1], 0.0, 0.0)
        p = toon.getPos(self)
        toon.setPos(self, p[0], p[1], 0.0)
        toon.setShadowHeight(0)
        leaderIndex = self.suits[0]

        camSeqLength = 0.3
        delay = FACEOFF_TAUNT_T + camSeqLength
        suitTrack = Parallel()
        suitLeader = None

        for suit in self.suits:
            suit.setState('Battle')
            suit.loop('neutral')
            suit.headsUp(toonPos)
            suitIsLeader = 0
            oneSuitTrack = Sequence()

            if suit == leaderIndex:
                suitLeader = suit
                suitIsLeader = 1
                taunt = SuitBattleGlobals.getFaceoffTaunt(suit.getStyleName(), suit.doId)
                oneSuitTrack.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
            destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            if suitIsLeader == 1:
                oneSuitTrack.append(Wait(delay))
                oneSuitTrack.append(Func(suit.clearChat))
            oneSuitTrack.append(self.createAdjustInterval(suit, destPos, destHpr))
            suitTrack.append(oneSuitTrack)

        suitHeight = suitLeader.getHeight()
        suitOffsetPnt = Point3(0, 0, suitHeight)
        toonTrack = Parallel()
        for toon in self.toons:
            oneToonTrack = Sequence()
            destPos, destHpr = self.getActorPosHpr(toon, self.toons)
            oneToonTrack.append(Wait(delay))
            oneToonTrack.append(self.createAdjustInterval(toon, destPos, destHpr, toon = 1, run = 1))
            toonTrack.append(oneToonTrack)

        if self.hasLocalToon():
            # kill the local toon sprint sequence
            base.localAvatar.stopSprintFovSeq()

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

            camTrack.append(Func(base.camLens.setMinFov, self.camFov / (4. / 3.)))
            camTrack.append(Func(camera.wrtReparentTo, self))
            camTrack.append(Func(camera.setPos, self.camFOPos))
            camTrack.append(Func(camera.lookAt, suit))

        mtrack = Parallel(suitTrack, toonTrack)

        if self.hasLocalToon():
            NametagGlobals.setMasterArrowsOn(0)
            mtrack = Parallel(mtrack, camTrack)

        done = Func(callback)
        track = Sequence(mtrack, done, name = name)
        track.start(ts)
        self.storeInterval(track, name)
        return

    def enterFaceOff(self, ts):
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            TTEmote.globalEmote.disableAll(self.toons[0], 'dbattlebldg, enterFaceOff')
        self.delayDeleteMembers()
        self.__faceOff(ts, self.faceOffName, self.__handleFaceOffDone)
        if self.hasLocalToon() and not self.battleMusicListener.storedMusic:
            self.battleMusicListener.playMusic(self.suits, zone=[base.cr.playGame.getPlace().getZoneId()])

    def __handleFaceOffDone(self):
        self.notify.debug('FaceOff done')
        self.d_faceOffDone(base.localAvatar.doId)

    def exitFaceOff(self):
        self.notify.debug('exitFaceOff()')
        if len(self.toons) > 0 and base.localAvatar == self.toons[0]:
            TTEmote.globalEmote.releaseAll(self.toons[0], 'dbattlebldg exitFaceOff')
        self.clearInterval(self.faceOffName)
        self._removeMembersKeep()

    def __playReward(self, ts, callback):
        toonTracks = Parallel()
        for toon in self.toons:
            toonTracks.append(
                Sequence(
                    Func(toon.loop, 'victory'),
                    Wait(FLOOR_REWARD_TIMEOUT),
                    Func(toon.loop, 'neutral')
                )
            )

        name = self.uniqueName('floorReward')
        track = Sequence(toonTracks, Func(callback), name = name)
        camera.setPos(0, 0, 1)
        camera.setHpr(180, 10, 0)
        self.storeInterval(track, name)
        track.start(ts)

    def enterReward(self, ts):
        # Make sure toon is participating in the battle
        if self.hasLocalToon():
            self.notify.info('enterReward()')
            self.disableCollision()
            self.delayDeleteMembers()
            self.__playReward(ts, self.__handleFloorRewardDone)

    def __handleFloorRewardDone(self):
        pass

    def exitReward(self):
        self.notify.info('exitReward()')
        self.clearInterval(self.uniqueName('floorReward'))
        self._removeMembersKeep()
        if self.hasLocalToon():
            NametagGlobals.setMasterArrowsOn(1)
        for toon in self.toons:
            toon.startSmooth()
        if self.hasLocalToon():
            self.battleMusicListener.stopMusic()
