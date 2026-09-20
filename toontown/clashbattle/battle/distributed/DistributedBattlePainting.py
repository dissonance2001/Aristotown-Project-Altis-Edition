from panda3d.core import Point3, Vec3
from direct.interval.IntervalGlobal import *
from toontown.clashbattle.battle.distributed import DistributedBattleFinal
from toontown.clashbattle.battle import BattleProps
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedBattlePainting(DistributedBattleFinal.DistributedBattleFinal):
    def __init__(self, cr):
        DistributedBattleFinal.DistributedBattleFinal.__init__(self, cr)
        self.initialReservesJoiningDone = False

    def showSuitsJoining(self, suits, ts, name, callback):
        suitTrack = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            if self.battleSide:
                startPos = Point3(6, 95, 80)
            else:
                startPos = Point3(-6, 95, 80)
            self.notify.debug('startPos for %s = %s' % (suit, startPos))
            suit.reparentTo(self)
            suit.setPos(startPos)
            suit.headsUp(self)
            flyTrack = self.createFlyIval(suit, startPos, destPos, destHpr)
            suitTrack.append(Track((delay, Sequence(flyTrack, Func(suit.loop, 'neutral')))))
            delay += 1
        
        suitTrack.append(self.updateActiveSuitPositions())

        if self.hasLocalToon():
            camera.reparentTo(self)
            base.camLens.setMinFov(self.camFov/(4/3))
            camTrack = LerpPosHprInterval(camera, 1, Point3(0, -16, 0.25), Vec3(0, 30, 0), blendType='easeOut')
            returnTrack = LerpPosHprInterval(camera, 1, Point3(0, -16, 3), Vec3(0, 0, 0), blendType='easeOut')
        else:
            camTrack = Sequence(Wait(1))
            returnTrack = Sequence(Wait(1))
        done = Func(callback)
        if self.battleSide:
            openPainting = Func(self.bossCog.openPainting, 4)
            closePainting = Func(self.bossCog.closePainting, 4)
        else:
            openPainting = Func(self.bossCog.openPainting, 5)
            closePainting = Func(self.bossCog.closePainting, 5)
        track = Sequence(Parallel(openPainting, camTrack), Wait(1.5), suitTrack, Parallel(returnTrack, closePainting, done), name=name)
        track.start(ts)
        self.storeInterval(track, name)
        return
        
    def createFlyIval(self, suit, startPos, destPos, destHpr):
        dur = suit.getDuration('landing')
        landingDur = dur
        totalDur = 7.3
        animTimeInAir = totalDur - dur

        def fixSuitHpr(suit):
            if suit.getH() < 0:
                suit.setH(suit.getH() + 360)

        moveIval = Sequence(
            Func(suit.headsUp, self), 
            Func(suit.pose, 'landing', 0), 
            ParallelEndTogether(
                ProjectileInterval(suit, duration=animTimeInAir, startPos=startPos, endPos=destPos, gravityMult=0.25), 
                Sequence(
                    Func(fixSuitHpr, suit),
                    LerpHprInterval(suit, 1.5, destHpr, blendType='easeIn')
                )
            ),
            ActorInterval(suit, 'landing')
        )
        if suit.prop is None:
            suit.prop = BattleProps.globalPropPool.getProp('propeller')
        lastSpinFrame = 8
        fr = suit.prop.getFrameRate('propeller')
        spinTime = lastSpinFrame / fr
        openTime = (lastSpinFrame + 1) / fr
        suit.attachPropeller()
        propTrack = Parallel(
            SoundInterval(suit.propInSound, duration=animTimeInAir, node=suit), 
            Sequence(
                ActorInterval(
                    suit.prop, 'propeller', constrainedLoop=1, duration=animTimeInAir + 1, 
                    startTime=0.0, endTime=spinTime
                ), 
                ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime), 
                Func(suit.detachPropeller)
            )
        )
        result = Parallel(moveIval, propTrack)
        return result

    def enterWaitForInput(self, ts = 0):
        DistributedBattleFinal.DistributedBattleFinal.enterWaitForInput(self, ts)
