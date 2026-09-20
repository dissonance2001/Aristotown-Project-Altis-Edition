from panda3d.core import Point3, Vec3
from direct.interval.IntervalGlobal import *
from toontown.clashbattle.battle.distributed import DistributedBattleFinal
from toontown.clashbattle.battle import BattleProps
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedBattleLitigators(DistributedBattleFinal.DistributedBattleFinal):
    """
    DistributedBattleLitigators is a hybrid DistributedBattlePainting file.
    For litigation team members, they fly in from their spot at the table during the boss.
    For non-litigation team members, they fly in from the painting as usual.
    """

    def __init__(self, cr):
        DistributedBattleFinal.DistributedBattleFinal.__init__(self, cr)
        self.initialReservesJoiningDone = False
        base.dblg = self

    def adjustLitigationTeamMusic(self):
        # Only our local avatar should update the music
        if not self.hasLocalToon():
            return

        # We want to send over all suits in the battle, including pending and joining suits.
        bossSuits = self.joiningSuits + self.pendingSuits + self.activeSuits
        self.bossCog.setLitigationTeamMusic(bossSuits)

    def showSuitsJoining(self, suits, ts, name, callback):
        # Re-adjust the music when suits are joining
        self.adjustLitigationTeamMusic()
        self.showSuitsFalling(suits, ts, name, callback)

    def showSuitsFalling(self, suits, ts, name, callback):
        suitTrack = Parallel()
        delay = 0
        hasLitMember = False
        otherSuits = False
        for suit in suits:
            if suit.style.name in self.bossCog.litigationOrder:
                hasLitMember = True
            else:
                otherSuits = True

        for suit in suits:
            isLitigationMember = suit.style.name in self.bossCog.litigationOrder
            fakeSuit = None
            if isLitigationMember:
                for litMember in self.bossCog.litigationTeam:
                    if litMember.style.name == suit.style.name:
                        fakeSuit = litMember
                        break

            suit.setState('Battle')
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)

            if isLitigationMember:
                startPos = fakeSuit.getPos(self)
            else:
                if self.battleSide:
                    startPos = Point3(6, 95, 80)
                else:
                    startPos = Point3(-6, 95, 80)

            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suit.reparentTo(self)
            suit.setPos(startPos)
            suit.headsUp(self)
            flyTrack = self.createFlyIval(suit, startPos, destPos, litigationMember=isLitigationMember)
            suitTrack.append(Track((delay, Sequence(flyTrack, Func(suit.loop, 'neutral')))))
            if isLitigationMember:
                suitTrack.append(Sequence(Func(fakeSuit.hide)))
            delay += 1
        
        suitTrack.append(self.updateActiveSuitPositions())

        if self.hasLocalToon():
            camera.reparentTo(self)
            if hasLitMember:
                camTrack = Sequence(Func(camera.setPosHpr, 0, -20, 30, 180, -20, 0),
                                    Wait(2.0),
                                    LerpPosHprInterval(camera, 2, (0, -30, 10), (0, 0, 0), blendType='easeOut'))
            else:
                camTrack = LerpPosHprInterval(camera, 1, Point3(0, -16, 0.25), Vec3(0, 30, 0), blendType='easeOut')
            returnTrack = LerpPosHprInterval(camera, 1, Point3(0, -16, 3), Vec3(0, 0, 0), blendType='easeOut')
        else:
            camTrack = Sequence(Wait(1))
            returnTrack = Sequence(Wait(1))

        done = Func(callback)
        litTeamTrack = None
        if hasLitMember:
            litTeamTrack = Parallel(Sequence(suitTrack, done), Sequence(camTrack, returnTrack))

        if otherSuits:
            if self.battleSide:
                openPainting = Func(self.bossCog.openPainting, 4)
                closePainting = Func(self.bossCog.closePainting, 4)
            else:
                openPainting = Func(self.bossCog.openPainting, 5)
                closePainting = Func(self.bossCog.closePainting, 5)
        else:
            openPainting = Sequence()
            closePainting = Sequence()

        if litTeamTrack and otherSuits:
            pTrack = Parallel(openPainting, litTeamTrack)
            track = Sequence(pTrack, closePainting, done, name=name)
        elif litTeamTrack:
            track = Sequence(litTeamTrack, name=name)
        elif otherSuits:
            track = Sequence(Parallel(openPainting, camTrack), Wait(1.5), suitTrack,
                             Parallel(returnTrack, closePainting, done), name=name)
        else:
            track = Sequence(done, name=name)

        track.start(ts)
        self.storeInterval(track, name)
        return

    def createFlyIval(self, suit, startPos, destPos, litigationMember=False):
        dur = suit.getDuration('landing')
        landingDur = dur
        totalDur = 7.3
        animTimeInAir = totalDur - dur
        moveIval = Sequence(Func(suit.headsUp, self), Func(suit.pose, 'landing', 0),
                            ProjectileInterval(suit, duration=animTimeInAir, startPos=startPos, endPos=destPos,
                                               gravityMult=0.25), ActorInterval(suit, 'landing'))
        if suit.prop is None:
            suit.prop = BattleProps.globalPropPool.getProp('propeller')
        lastSpinFrame = 8
        fr = suit.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame + 1) / fr
        suit.attachPropeller()
        propTrack = Parallel(SoundInterval(suit.propInSound, duration=animTimeInAir, node=suit), Sequence(
            ActorInterval(suit.prop, 'propeller', constrainedLoop=1, duration=animTimeInAir + 1, startTime=0.0,
                          endTime=spinTime),
            ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime), Func(suit.detachPropeller)))
        moveTrack = Sequence(moveIval)
        if litigationMember:
            endTrack = Sequence(Func(suit.loop, 'walk'), LerpHprInterval(suit, 2, (180, 0, 0)), Func(suit.loop, 'neutral'))
            moveTrack.append(endTrack)
        result = Parallel(moveTrack, propTrack)
        return result

    def enterPlayMovie(self, ts=0):
        DistributedBattleFinal.DistributedBattleFinal.enterPlayMovie(self, ts)
        # Re-adjust the music when the battle movie is starting.
        self.adjustLitigationTeamMusic()

    def enterWaitForInput(self, ts=0):
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput(self, ts)
        # Re-adjust the music when the player is receiving input.
        self.adjustLitigationTeamMusic()
        if self.hasLocalToon():
            camera.reparentTo(self)
            
    def enterResume(self, ts=0):
        DistributedBattleFinal.DistributedBattleFinal.enterResume(self, ts)
        # Only our local avatar should update the music
        if self.hasLocalToon():
            # Send a message to update the music, but with an empty list. This will effectively only play the base track
            self.bossCog.setLitigationTeamMusic([])
