from panda3d.core import Point3, VBase3
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import Func, LerpHprInterval, LerpPosInterval, Parallel, Sequence, Track, Wait

from toontown.battle import DistributedBattleMiniboss


class DistributedBattleChainsaw(
        DistributedBattleMiniboss.DistributedBattleMiniboss):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedBattleChainsaw')

    def __init__(self, cr):
        DistributedBattleMiniboss.DistributedBattleMiniboss.__init__(self, cr)
        self.doorOpenSfx = loader.loadSfx(
            'phase_9/audio/sfx/CHQ_door_open.ogg')
        self.doorCloseSfx = loader.loadSfx(
            'phase_9/audio/sfx/CHQ_door_close.ogg')

    def delete(self):
        if self.doorOpenSfx:
            try:
                self.doorOpenSfx.stop()
            except:
                pass
        if self.doorCloseSfx:
            try:
                self.doorCloseSfx.stop()
            except:
                pass
        self.doorOpenSfx = None
        self.doorCloseSfx = None
        DistributedBattleMiniboss.DistributedBattleMiniboss.delete(self)

    def _pruneStaleLuredSuits(self):
        self.luredSuits = [suit for suit in self.luredSuits
                           if suit in self.activeSuits]

    def enterWaitForInput(self, ts):
        self._pruneStaleLuredSuits()
        return DistributedBattleMiniboss.DistributedBattleMiniboss.enterWaitForInput(
            self, ts)

    def setMembers(self, suits, suitsJoining, suitsPending, suitsActive,
                   suitsLured, suitTraps, toons, toonsJoining, toonsPending,
                   toonsActive, toonsRunning, immuneSuits, enragedSuits,
                   absorbingSuits, soakedSuits, timestamp):
        result = DistributedBattleMiniboss.DistributedBattleMiniboss.setMembers(
            self, suits, suitsJoining, suitsPending, suitsActive, suitsLured,
            suitTraps, toons, toonsJoining, toonsPending, toonsActive,
            toonsRunning, immuneSuits, enragedSuits, absorbingSuits,
            soakedSuits, timestamp)

        # TownBattle builds its Cog cards from activeSuits. Chainsaw cheat
        # deaths/sacrifices can briefly leave a zero-HP support in that list
        # after its death movie, so prune it locally and request a GUI rebuild.
        removed = False
        active = []
        for suit in self.activeSuits:
            keep = True
            try:
                isChainsaw = (getattr(getattr(suit, 'dna', None), 'name', None)
                              == 'chainsaw')
                if not isChainsaw and suit.getHP() <= 0:
                    keep = False
            except:
                pass
            if keep:
                active.append(suit)
            else:
                removed = True
        if removed:
            self.activeSuits = active
            self._pruneStaleLuredSuits()
            self.needAdjustTownBattle = 1
            try:
                self._DistributedBattleBase__requestAdjustTownBattle()
            except:
                pass
        else:
            self._pruneStaleLuredSuits()
        return result

    def makeSuitJoin(self, suit, ts):
        # Reserve Cogs are generated as distributed objects before the door
        # movie begins.  Hide them at the first battle-membership callback so
        # they cannot flash at a default/canonical battle point for a frame.
        try:
            if getattr(getattr(suit, 'dna', None), 'name', None) != 'chainsaw':
                suit.hide()
        except:
            pass
        return DistributedBattleMiniboss.DistributedBattleMiniboss.makeSuitJoin(
            self, suit, ts)

    def doInitialSuitsJoining(self, ts, name, callback):
        # The only initial Suit is Chainsaw himself.  Place him directly on
        # the canonical front manager point; do not use an office-door join.
        ordered = self._getCanonicalSuitOrder(self.suits)
        for suit in ordered:
            try:
                suit.reparentTo(self)
                destPos, destHpr = self.getActorPosHpr(suit, ordered)
                suit.setPos(destPos)
                suit.setHpr(destHpr)
                suit.show()
                suit.unstash()
                suit.loop('neutral')
            except:
                pass

        done = Func(callback)
        if self.hasLocalToon():
            camera.reparentTo(self)
            camera.setPosHpr(23, -11, 7, 60, 0, 0)
        track = Sequence(Wait(0.15), done, name=name)
        track.start(ts)
        self.storeInterval(track, name)

    def showSuitsFalling(self, suits, ts, name, callback):
        # Corporate Clash sends replacement grunts through the left office
        # door.  Keep this isolated to the Chainsaw battle instead of changing
        # DistributedBattleMiniboss globally.
        controller = getattr(self, 'bossCog', None)
        left = getattr(controller, 'cogEntrance_1_1', None) if controller else None
        right = getattr(controller, 'cogEntrance_1_2', None) if controller else None
        if (left is None or right is None or
                left.isEmpty() or right.isEmpty()):
            return DistributedBattleMiniboss.DistributedBattleMiniboss.showSuitsFalling(
                self, suits, ts, name, callback)

        suitTracks = Parallel()
        delay = 0.0
        for suit in suits:
            # A freshly generated distributed Suit can render for one frame at
            # its canonical battle point before the joining interval starts.
            # Hide it immediately so there is never a ghost/placeholder Cog in
            # front of the Toons.
            try:
                suit.hide()
            except:
                pass
            suit.setState('Battle')
            if suit in self.joiningSuits:
                i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)

            startPos = Point3(-36.88455, 4.53885, 0)
            endWalkPos = Point3(-12.34567, 4.5389, 0)

            def fixHeading(s=suit):
                if s.getH() < 0:
                    s.setH(s.getH() + 360)

            move = Sequence(
                Func(suit.reparentTo, self),
                Func(suit.setPos, startPos),
                Func(suit.headsUp, destPos),
                Func(suit.show),
                Func(suit.unstash),
                Func(suit.loop, 'walk'),
                LerpPosInterval(
                    suit,
                    self.calcSuitMoveTime(endWalkPos, startPos) * 0.67,
                    endWalkPos),
                Func(suit.headsUp, destPos),
                LerpPosInterval(
                    suit,
                    self.calcSuitMoveTime(destPos, endWalkPos) * 0.67,
                    destPos),
                Func(fixHeading),
                LerpHprInterval(suit, 0.9, destHpr),
                Func(suit.loop, 'neutral'))
            suitTracks.append(Track((delay, move)))
            delay += 1.0

        doorSeq = Sequence(
            Parallel(
                Func(base.playSfx, self.doorOpenSfx, node=left),
                LerpHprInterval(left, 0.6, (-127.45104, 0, 0), blendType='easeIn'),
                LerpHprInterval(right, 0.6, (127.45104, 0, 0), blendType='easeIn')),
            Parallel(
                LerpHprInterval(left, 0.3, (-118, 0, 0), blendType='easeOut'),
                LerpHprInterval(right, 0.3, (118, 0, 0), blendType='easeOut')),
            Wait((1.0 * len(suits)) + 1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(base.playSfx, self.doorCloseSfx, node=left)),
                LerpHprInterval(left, 0.8, (0, 0, 0), blendType='easeIn'),
                LerpHprInterval(right, 0.8, (0, 0, 0), blendType='easeIn')))

        if self.hasLocalToon():
            camera.reparentTo(self)
            camera.setPosHpr(4, -15, 7, 20, 0, 0)

        track = Sequence(
            Parallel(suitTracks, doorSeq),
            Func(callback),
            name=name)
        track.start(ts)
        self.storeInterval(track, name)
