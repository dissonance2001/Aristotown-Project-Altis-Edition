import random

from panda3d.core import VBase3, Point3
from direct.interval.IntervalGlobal import Sequence, Wait, Func, Parallel, Track, ProjectileInterval, SoundInterval, \
    ActorInterval, ParallelEndTogether, LerpHprInterval
from toontown.battle.distributed import DistributedBattleFinal
from toontown.suit import SuitTimings
from toontown.toonbase import ToontownGlobals
from toontown.battle import BattleProps

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedBattleDiners(DistributedBattleFinal.DistributedBattleFinal):
    def __init__(self, cr):
        # Create the diners table
        DistributedBattleFinal.DistributedBattleFinal.__init__(self, cr)
        self.initialReservesJoiningDone = False

    def announceGenerate(self):
        DistributedBattleFinal.DistributedBattleFinal.announceGenerate(self)
        self.moveSuitsToInitialPos()

    def showSuitsJoining(self, suits, ts, name, callback):
        # Show the diners joining the battle, handle initial join as well.
        if len(suits) == 0 and not self.initialReservesJoiningDone:
            self.initialReservesJoiningDone = True
            self.doInitialSuitsJoining(ts, name, callback)
            return
        self.showSuitsFalling(suits, ts, name, callback)

    def doInitialSuitsJoining(self, ts, name, callback):
        done = Func(callback)
        track = Sequence(Wait(0.5), done, name=name)
        track = Parallel(track, self.getCamTrack(override=True))
        track.start(ts)
        self.storeInterval(track, name)

    def moveSuitsToInitialPos(self):
        # Force the initial suits to be in the right spot.
        # Tubby's note: To any clash devs, I bet you can tell which ones were written by interns
        # and which ones were written by actual developers
        for i in range(len(self.suits)):
            suit = self.suits[i]
            suit.reparentTo(self)
            destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            suit.setPos(destPos)
            suit.setHpr(destHpr)

    def showSuitsFalling(self, suits, ts, name, callback):
        if self.bossCog is None:
            # Hmm, no boss cog?  Maybe not generated yet.
            # Tubby's note: Hmm, no full time job? Maybe not generated yet.
            return
        suitTrack = Parallel()
        delay = 0
        for suit in suits:
            suit.setState('Battle')
            if suit.dna.dept == 'l':
                suit.reparentTo(self.bossCog)
                suit.setPos(0, 0, 0)

            if self.bossCog.dna.dept == 'c':
                suit.setActiveShadow(1) # Enable drop shadow calculations
                suit.showShadow()       # And then show
                suit.addActive()        # Manage the nametag

            # Move all suits into position.
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
            moveIval = Sequence()
            chairInfo = self.bossCog.claimOneChair(suit)
            if chairInfo:
                moveIval = self.createDinerMoveIval(suit, destPos, destHpr, chairInfo)
            suitTrack.append(Track((delay, Sequence(moveIval, Func(suit.loop, 'neutral')))))
            delay += 1

        if self.battleSide == 0:
            self.CAM_SUIT_JOINING_POS = (4, -15, 7, 20, 0, 0)
        else:
            self.CAM_SUIT_JOINING_POS = (-4, -15, 7, -20, 0, 0)

        suitTrack.append(self.updateActiveSuitPositions())

        done = Func(callback)
        track = Sequence(suitTrack, done, name=name)
        track = Parallel(track, self.getCamTrack())

        track.start(ts)
        self.storeInterval(track, name)
        return

    def createDinerMoveIval(self, suit, destPos, destHpr, chairInfo):
        """Return an interval of a diner moving to his destPos."""
        # Adapted from  suit.beginSupaFlyMovie

        # Calculate some times used to manipulate the suit's landing
        # animation
        dur = suit.getDuration('landing')
        fr = suit.getFrameRate('landing')

        landingDur = dur

        totalDur = 7.3
        # length of time in animation spent in the air
        animTimeInAir = totalDur - dur
        flyingDur = animTimeInAir

        # Length of time in animation spent impacting and reacting to
        # the ground
        impactLength = dur - animTimeInAir

        tableIndex = chairInfo[0]
        chairIndex = chairInfo[1]
        table = self.bossCog.tables[tableIndex]
        chairLocator = table.chairLocators[chairIndex]
        chairPos = chairLocator.getPos(self)
        chairHpr = chairLocator.getHpr(self)
        suit.setPos(chairPos)
        suit.setHpr(chairHpr)
        wayPoint = (chairPos + destPos) / 2.0
        wayPoint.setZ(wayPoint.getZ() + 20)

        def fixSuitHpr(suit):
            if suit.getH() < 0:
                suit.setH(suit.getH() + 360)

        moveIval = Sequence(
            Func(suit.headsUp, self),
            Func(suit.pose, 'landing', 0),
            ParallelEndTogether(
                ProjectileInterval(suit, duration=flyingDur, startPos=chairPos, endPos=destPos, gravityMult=0.25),
                Sequence(
                    Func(fixSuitHpr, suit),
                    LerpHprInterval(suit, 1.5, destHpr, blendType='easeIn')
                )
            ),
            ActorInterval(suit, 'landing')
        )

        # Now create info for the propeller's animation
        if suit.prop is None:
            suit.prop = BattleProps.globalPropPool.getProp('propeller')
        propDur = suit.prop.getDuration('propeller')
        lastSpinFrame = 8
        fr = suit.prop.getFrameRate('propeller')
        # Time from beginning of anim at which propeller plays its spin
        spinTime = lastSpinFrame / fr
        # Time from beginning of anim at which propeller starts to close
        openTime = (lastSpinFrame + 1) / fr

        # Now create the propeller animation intervals that will go in
        # the third and final track
        suit.attachPropeller()
        propTrack = Parallel(
            SoundInterval(suit.propInSound, duration=flyingDur, node=suit),
            Sequence(
                ActorInterval(suit.prop, 'propeller', constrainedLoop=1, duration=flyingDur + 1, startTime=0.0, endTime=spinTime),
                ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime),
                Func(suit.detachPropeller)
            )
        )
        result = Parallel(moveIval, propTrack)
        return result
