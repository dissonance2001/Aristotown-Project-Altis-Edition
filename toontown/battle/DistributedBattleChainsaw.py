from panda3d.core import Point3, VBase3
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import Func, LerpHprInterval, LerpPosInterval, Parallel, Sequence, Track, Wait

from toontown.battle import DistributedBattleMiniboss
from toontown.suit import Suit
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals


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
        self.chainsawChainVisualActive = False
        self._chainsawIdleTasks = set()
        points = list(self.suitPoints)
        points[1] = ((Point3(0, 4.5, 0), 180),
                     (Point3(5, 5.8, 0), 170))
        self.suitPoints = tuple(points)

    def getActorPosHpr(self, actor, actorList=[]):
        try:
            if isinstance(actor, Suit.Suit):
                if actorList == []:
                    actorList = self.activeSuits
                if actor in actorList:
                    boss = None
                    supports = []
                    for suit in actorList:
                        try:
                            if suit.style.name == 'chainsaw':
                                boss = suit
                            else:
                                supports.append(suit)
                        except:
                            supports.append(suit)
                    formations = {
                        1: ((Point3(0, 4.5, 0), 180),),
                        2: ((Point3(10, 4.5, 0), 155),
                            (Point3(-10, 4.5, 0), 205)),
                        3: ((Point3(10, 4.5, 0), 155),
                            (Point3(0, 7, 0), 179),
                            (Point3(-10, 4.5, 0), 205)),
                        4: ((Point3(10, 4.5, 0), 155),
                            (Point3(5, 5.8, 0), 170),
                            (Point3(-5, 5.8, 0), 190),
                            (Point3(-10, 4.5, 0), 205)),
                        5: ((Point3(10, 4.5, 0), 155),
                            (Point3(5, 5.8, 0), 170),
                            (Point3(0, 7, 0), 179),
                            (Point3(-5, 5.8, 0), 190),
                            (Point3(-10, 4.5, 0), 205))}
                    formation = formations.get(len(actorList))
                    if formation:
                        if actor is boss:
                            index = 0
                        else:
                            regularSupports = []
                            promotedSupports = []
                            for support in actorList:
                                if support is boss:
                                    continue
                                if getattr(support, 'chainsawManagerBeneficiary', False):
                                    promotedSupports.append(support)
                                else:
                                    regularSupports.append(support)
                            orderedSupports = regularSupports + list(reversed(promotedSupports))
                            index = orderedSupports.index(actor) + 1
                        point = formation[index]
                        return (Point3(point[0]), VBase3(point[1], 0.0, 0.0))
        except:
            pass
        return DistributedBattleMiniboss.DistributedBattleMiniboss.getActorPosHpr(
            self, actor, actorList)

    def getSurrenderExitStatus(self):
        return {
            'loader': 'townLoader',
            'where': 'toonInterior',
            'how': 'teleportIn',
            'hoodId': ToontownGlobals.OutdoorZone,
            'zoneId': ToontownGlobals.ChainsawLobby,
            'shardId': None,
            'avId': -1,
            'battle': 1,
            'quick': 1,
        }

    def delete(self):
        for taskName in list(self._chainsawIdleTasks):
            taskMgr.remove(taskName)
        self._chainsawIdleTasks.clear()
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

    def setChainsawChainVisualActive(self, active):
        self.chainsawChainVisualActive = bool(active)
        self._refreshChainsawChainVisuals()

    def _refreshChainsawChainVisuals(self):
        boss = None
        supports = []
        for suit in self.activeSuits:
            if not suit:
                continue
            try:
                if suit.getHP() <= 0:
                    continue
            except:
                pass
            try:
                if suit.style.name == 'chainsaw':
                    boss = suit
                else:
                    supports.append(suit)
            except:
                supports.append(suit)

        for suit in list(getattr(self, 'suits', ())) + list(self.activeSuits):
            if not suit:
                continue
            try:
                suit.clearSuitStatusEffect('chainsawChainLinked')
            except:
                pass

        if not self.chainsawChainVisualActive or not boss or not supports:
            return

        incoming = [0.0, 0.25, 0.5, 0.75, 1.0]
        linkedIncoming = incoming[-(len(supports) + 1):]
        bossMultiplier = linkedIncoming[0]
        try:
            boss.setSuitStatusEffect(
                'chainsawChainLinked',
                int(round((1.0 - bossMultiplier) * 100.0)),
                None, 'setBoth')
        except:
            pass

        multipliers = linkedIncoming[1:]
        for index in xrange(len(supports)):
            suit = supports[index]
            defense = int(round((1.0 - multipliers[index]) * 100.0))
            try:
                suit.setSuitStatusEffect(
                    'chainsawChainLinked', defense, None, 'setBoth')
            except:
                pass

    def _pruneStaleLuredSuits(self):
        self.luredSuits = [suit for suit in self.luredSuits
                           if suit in self.activeSuits]

    def _applyChainsawPhaseThreeIdle(self, suit):
        if not getattr(suit, '_chainsawPhaseThreeIdle', False):
            return
        try:
            if suit.getDizzy() or suit.getDizzy3():
                return
        except:
            pass
        try:
            if suit.hasSuitStatusEffect('sleepy'):
                return
        except:
            pass
        try:
            control = suit.getAnimControl(
                'neutral-override-glitched', partName='modelRoot')
        except:
            control = None
        if control is None:
            return
        try:
            suit.setPlayRate(
                1 + (suit.battleSpeed * .1),
                'neutral-override-glitched', partName='modelRoot')
        except:
            pass
        try:
            suit.loop('neutral-override-glitched', partName='modelRoot')
        except:
            try:
                suit.loop('neutral-override-glitched')
            except:
                pass

    def _queueChainsawPhaseThreeIdle(self, suit, delay=0.2):
        taskName = self.uniqueName(
            'chainsawPhaseThreeIdle-%s' % getattr(suit, 'doId', id(suit)))
        taskMgr.remove(taskName)
        self._chainsawIdleTasks.add(taskName)

        def applyIdle(task):
            self._chainsawIdleTasks.discard(taskName)
            try:
                if suit not in self.activeSuits or suit.getHP() <= 0:
                    return task.done
            except:
                return task.done
            self._applyChainsawPhaseThreeIdle(suit)
            return task.done

        taskMgr.doMethodLater(delay, applyIdle, taskName)

    def _installChainsawNeutralRecovery(self, suit):
        if getattr(suit, '_chainsawNeutralRecoveryInstalled', False):
            return
        suit._chainsawNeutralRecoveryInstalled = True
        suit._chainsawPhaseThreeIdle = False
        methodNames = (
            'setNeutralAnimation',
            'setNeutralAnimationDrop',
            'setNeutralAnimationTrap',
            'setNeutralAnimationAttack',
        )
        for methodName in methodNames:
            original = getattr(suit, methodName, None)
            if original is None:
                continue

            def recoveredNeutral(original=original, suit=suit, battle=self):
                result = original()
                battle._applyChainsawPhaseThreeIdle(suit)
                battle._queueChainsawPhaseThreeIdle(suit)
                return result

            setattr(suit, methodName, recoveredNeutral)

    def _syncChainsawNeutralRecovery(self):
        controller = getattr(self, 'bossCog', None)
        phase = getattr(controller, 'chainsawPhase', 1) if controller else 1
        for suit in self.activeSuits:
            try:
                if suit.style.name != 'chainsaw':
                    continue
            except:
                continue
            self._installChainsawNeutralRecovery(suit)
            suit._chainsawPhaseThreeIdle = phase == 3
            if suit._chainsawPhaseThreeIdle:
                self._applyChainsawPhaseThreeIdle(suit)
                self._queueChainsawPhaseThreeIdle(suit)

    def enterWaitForInput(self, ts):
        self._pruneStaleLuredSuits()
        result = DistributedBattleMiniboss.DistributedBattleMiniboss.enterWaitForInput(
            self, ts)
        self._syncChainsawNeutralRecovery()
        return result

    def setMembers(self, suits, suitsJoining, suitsPending, suitsActive,
                   suitsLured, suitTraps, toons, toonsJoining, toonsPending,
                   toonsActive, toonsRunning, immuneSuits, enragedSuits,
                   absorbingSuits, soakedSuits, timestamp):
        result = DistributedBattleMiniboss.DistributedBattleMiniboss.setMembers(
            self, suits, suitsJoining, suitsPending, suitsActive, suitsLured,
            suitTraps, toons, toonsJoining, toonsPending, toonsActive,
            toonsRunning, immuneSuits, enragedSuits, absorbingSuits,
            soakedSuits, timestamp)
        self._pruneStaleLuredSuits()
        if self.chainsawChainVisualActive:
            self._refreshChainsawChainVisuals()
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
