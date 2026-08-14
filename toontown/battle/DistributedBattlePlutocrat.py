from direct.interval.IntervalGlobal import *
from pandac.PandaModules import NodePath, Point3, VBase3

from toontown.battle import DistributedBattleMiniboss
from toontown.cutscene import PlutocratCutscenes


class DistributedBattlePlutocrat(DistributedBattleMiniboss.DistributedBattleMiniboss):
    def setPosition(self, x, y, z):
        DistributedBattleMiniboss.DistributedBattleMiniboss.setPosition(
            self, x, y, z)
        self.setH(-90)

    def setMovie(self, movieHasBeenMade, avIds, suitIds, toonAttacks,
                 toonTrackOrder, suitAttacks):
        result = DistributedBattleMiniboss.DistributedBattleMiniboss.setMovie(
            self, movieHasBeenMade, avIds, suitIds, toonAttacks,
            toonTrackOrder, suitAttacks)
        if int(movieHasBeenMade) != 1:
            return result
        boss = self.bossCog
        if boss and getattr(boss, 'deepFreezeRoundsLeft', 0) > 0:
            for attack in getattr(self.movie, 'suitAttackDicts', ()):
                attack['phase'] = 'preToon'
        frozenIds = set()
        for attack in getattr(self.movie, 'suitAttackDicts', ()):
            name = attack.get('name', '')
            if name.startswith('PlutocratCoreFreezeSuit_'):
                parts = name.split('_')
                if len(parts) >= 3:
                    try:
                        frozenIds.add(int(parts[-2]))
                    except:
                        pass
            elif name.startswith('PlutocratCoreShatter_'):
                parts = name.split('_')
                if len(parts) >= 2:
                    try:
                        frozenIds.add(int(parts[1]))
                    except:
                        pass
        for suit in getattr(self, 'suits', ()):
            if getattr(suit, 'doId', None) in frozenIds:
                try:
                    suit.movieFrozen = True
                except:
                    pass
        return result

    def showSuitsJoining(self, suits, ts, name, callback):
        if not self.initialReservesJoiningDone:
            investors = []
            for suit in self.suits:
                try:
                    if suit.dna.name in ('charon', 'nix', 'hydra', 'styx', 'kerberos'):
                        investors.append(suit)
                except:
                    pass
            if investors:
                self.initialReservesJoiningDone = True
                self.doInitialSuitsJoining(ts, name, callback)
                return
        DistributedBattleMiniboss.DistributedBattleMiniboss.showSuitsJoining(
            self, suits, ts, name, callback)

    def doInitialSuitsJoining(self, ts, name, callback):
        ordered = self._getCanonicalSuitOrder(self.suits)
        tracks = Parallel()
        for suit in ordered:
            try:
                if suit.dna.name not in ('charon', 'nix', 'hydra', 'styx', 'kerberos'):
                    continue
                suit.setState('Battle')
                suit.show()
                suit.unstash()
                suit.wrtReparentTo(self)
                destPos, destHpr = self.getActorPosHpr(suit, ordered)
                tracks.append(self.createAdjustInterval(
                    suit, destPos, destHpr, toon=0, run=0))
            except:
                pass
        if self.hasLocalToon():
            camera.reparentTo(self)
            camera.setPosHpr(0, -18, 12, 0, -12, 0)
        track = Sequence(tracks, Func(callback), name=name)
        track.start(ts)
        self.storeInterval(track, name)

    def enterWaitForInput(self, ts=0):
        result = DistributedBattleMiniboss.DistributedBattleMiniboss.enterWaitForInput(
            self, ts)
        boss = self.bossCog
        if boss:
            boss.advanceDeepFreezeVisuals()
            boss.advanceFrozenSuitVisuals()
            taskMgr.doMethodLater(
                0.05,
                lambda task: (boss.restoreBattlePresentation(resetCamera=0), task.done)[1],
                self.uniqueName('plutocratPresentationRefresh'))
        return result

    def exitWaitForInput(self):
        taskMgr.remove(self.uniqueName('plutocratPresentationRefresh'))
        return DistributedBattleMiniboss.DistributedBattleMiniboss.exitWaitForInput(self)


    def _restorePostPlutocratJoinCamera(self):
        if not self.hasLocalToon():
            return
        try:
            camera.reparentTo(self)
            camera.setPosHpr(0, -14.92, 9.56, 0, -18.5, 0)
        except:
            pass

    def showSuitsFalling(self, suits, ts, name, callback):
        boss = self.bossCog
        if boss is None:
            return DistributedBattleMiniboss.DistributedBattleMiniboss.showSuitsFalling(
                self, suits, ts, name, callback)
        pcratTrack = Sequence()
        investorTracks = Parallel()
        hatch = Sequence()
        investorDelay = 0.0
        wantHatch = False
        for suit in suits:
            suit.setState('Battle')
            if suit in self.joiningSuits:
                try:
                    i = self._getPendingPreviewIndex(suit)
                except:
                    i = len(self.pendingSuits) + self.joiningSuits.index(suit)
                destPos, h = self.suitPendingPoints[i]
                destHpr = VBase3(h, 0, 0)
            else:
                destPos, destHpr = self.getActorPosHpr(suit, self.suits)
            dest = NodePath('plutocratDestNode-%s' % suit.doId)
            dest.reparentTo(self)
            dest.setPos(destPos)
            dest.setHpr(destHpr)
            if suit.dna.name == 'pcrat':
                toons = []
                for toonId in self.activeToons:
                    toon = self.cr.doId2do.get(toonId)
                    if toon:
                        toons.append(toon)
                fly = PlutocratCutscenes.makeJoinPcrat(boss, suit, dest, toons)
                if self.hasLocalToon():
                    music = Sequence(
                        Func(boss.playJoinMusic),
                        Wait(14.9),
                        Func(boss.playPlutocratMusic))
                    cam = Track(
                        (0.0, Func(camera.reparentTo, self)),
                        (0.0, Func(camera.setPosHpr, 0, 10.5, 8, 0, 7.5, 0)),
                        (12.35, Func(camera.setPosHpr, -5.325, 10.5, 9.08, -163.5, -21.8, 0)),
                        (14.9, Func(camera.setPosHpr, 0, 10.5, 8, 0, 7.5, 0)),
                        (17.5, LerpPosHprInterval(camera, 3.0, (0, -14.92, 9.56), (0, -18.5, 0), blendType='easeInOut')))
                else:
                    music = Sequence()
                    cam = Sequence()
                pcratTrack = Sequence(
                    Func(PlutocratCutscenes.cleanupCutscenePlutocrat, boss),
                    Parallel(fly, music, cam),
                    Func(self._restorePostPlutocratJoinCamera),
                    Func(dest.removeNode))
            else:
                suit.hide()
                fly = PlutocratCutscenes.makeJoinGeneric(boss, suit, dest)
                investorTracks.append(Sequence(
                    Wait(investorDelay), Func(suit.show), fly, Func(dest.removeNode)))
                investorDelay += 1.0
                wantHatch = True
        if wantHatch:
            if self.hasLocalToon():
                hatch.append(Func(camera.reparentTo, self))
                hatch.append(Func(camera.setPosHpr, 0, -9, 8, 0, 0, 0))
            hatch.append(PlutocratCutscenes.makeHatch(boss, True))
            hatch.append(investorTracks)
            hatch.append(PlutocratCutscenes.makeHatch(boss, False))
            hatch.append(Func(boss.restoreBattlePresentation))
        done = Func(callback)
        track = Sequence(
            pcratTrack,
            hatch if wantHatch else investorTracks,
            Func(boss.refreshFrozenSuitVisuals),
            done,
            name=name)
        track.start(ts)
        self.storeInterval(track, name)
