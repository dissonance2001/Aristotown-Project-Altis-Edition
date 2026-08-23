from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.fsm import FSM
from direct.task import Task
from direct.interval.IntervalGlobal import *
from toontown.distributed import DelayDelete
from toontown.cutscene import PlutocratCutscenes
from toontown.suit import BossCutsceneSkip
from pandac.PandaModules import *
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.battle import BattleBase
from toontown.building import PlutocratInstanceGlobals
from toontown.building import PlutocratEnvironment
from toontown.friends import FriendsListManager
from toontown.nametag import NametagGlobals


OnePlutocratController = None


class DistributedPlutocratBoss(DistributedObject.DistributedObject, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPlutocratBoss')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedPlutocratBoss')
        self.gotAllToons = 0
        self.toons = []
        self.involvedToons = []
        self.toonRequest = None
        self.battleNumber = 0
        self.battleId = 0
        self.battle = None
        self.battleRequest = None
        self.arenaSide = 0
        self.plutocratPhase = 1
        self.geom = None
        self.battleNode = None
        self.chuteLeft = None
        self.chuteRight = None
        self.doorLeft = None
        self.doorRight = None
        self.particleRender = None
        self.environment = None
        self.snowSquallActive = False
        self.frozenSuitRounds = {}
        self.deepFreezeRoundsLeft = 0
        self.deepFreezeColor = VBase4(51.0 / 255.0, 1.0, 1.0, 1.0)
        self.fanModel = None
        self.investorMusic = None
        self.plutocratMusic = None
        self.introMusic = None
        self.joinMusic = None
        self.coldMusic = None
        self.victoryMusic = None
        self.currentMusic = None
        self.musicFadeTrack = None
        self.cutscenePlutocrat = None
        self.introTrack = None
        self.deathTrack = None
        self.introDelayDeletes = []
        self.introInvestors = []
        self.deathCutsceneSuits = []
        self.plutocratDeathPlayed = False
        self.activeIntervals = {}
        self.cutsceneSkipExtraIntervals = ('PlutocratDeathMovie',)
        self.cutsceneSkip = BossCutsceneSkip.BossCutsceneSkip(self)

    def announceGenerate(self):
        global OnePlutocratController
        DistributedObject.DistributedObject.announceGenerate(self)
        self.loadEnvironment()
        OnePlutocratController = self
        try:
            place = base.cr.playGame.getPlace()
            if place and hasattr(place, 'bossCog') and place.bossCog is None:
                place.bossCog = self
        except:
            pass

    def disable(self):
        global OnePlutocratController
        for name in ('plutocratInstanceReady', 'plutocratIntroDone', 'plutocratRewardDone', 'plutocratEpilogueDone'):
            taskMgr.remove(self.uniqueName(name))
        if self.toonRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
            self.toonRequest = None
        if self.battleRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
            self.battleRequest = None
        if self.introTrack:
            try: self.introTrack.finish()
            except: pass
            self.introTrack = None
        if self.deathTrack:
            try: self.deathTrack.finish()
            except: pass
            self.deathTrack = None
        PlutocratCutscenes.cleanupCutscenePlutocrat(self)
        PlutocratCutscenes.cleanupDeath(self)
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.cleanup()
        self.cleanupIntervals()
        self.stopMusic()
        self.unloadEnvironment()
        self.ignoreAll()
        if OnePlutocratController is self:
            OnePlutocratController = None
        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.delete()
            self.cutsceneSkip = None
        DistributedObject.DistributedObject.delete(self)

    def setState(self, state):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.stateChanged(state)
        self.request(state)

    def setToonIds(self, involvedToons, toons, unused):
        self.involvedToons = involvedToons
        self.toons = toons
        if self.toonRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
            self.toonRequest = None
        self.gotAllToons = 0
        if not self.involvedToons:
            self.gotAllToons = 1
            return
        self.toonRequest = self.cr.relatedObjectMgr.requestObjects(self.involvedToons, allCallback=self.__gotAllToons)

    def __gotAllToons(self, toons):
        self.toonRequest = None
        self.gotAllToons = 1

    def setBattleIds(self, battleNumber, battleId, unused):
        self.battleNumber = battleNumber
        self.battleId = battleId
        if self.battleRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
            self.battleRequest = None
        if not battleId:
            self.battle = None
            return
        self.battleRequest = self.cr.relatedObjectMgr.requestObjects([battleId], allCallback=self.__gotBattle)

    def __gotBattle(self, battles):
        self.battleRequest = None
        self.battle = battles[0] if battles else None

    def setArenaSide(self, arenaSide):
        self.arenaSide = arenaSide

    def setPlutocratPhase(self, phase):
        self.plutocratPhase = int(phase)
        if self.state == 'BattleOne':
            self.playBattleMusic()

    def requestCutsceneSkipVote(self):
        self.sendUpdate('requestSkip', [])

    def setCutsceneSkip(self):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.setCutsceneSkip()

    def setVoteSkips(self, voteTotal, playerTotal):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.setVoteSkips(voteTotal, playerTotal)

    def toonDied(self, avId):
        if avId == localAvatar.doId:
            self.localToonDied()

    def hasLocalToon(self):
        return localAvatar.doId in self.involvedToons

    def controlToons(self):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.stopLookAround()
                toon.stopSmooth()
        if self.hasLocalToon():
            self.toMovieMode()

    def releaseToons(self, finalBattle=0):
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if not toon:
                continue
            if (self.battle and hasattr(self.battle, 'toons') and
                    toon in self.battle.toons):
                continue
            toon.startLookAround()
            toon.startSmooth()
            toon.wrtReparentTo(render)
            if toon == localAvatar:
                if finalBattle:
                    self.toFinalBattleMode()
                else:
                    self.toWalkMode()

    def toMovieMode(self):
        place = self.cr.playGame.getPlace() if self.cr and self.cr.playGame else None
        if place and hasattr(place, 'fsm'):
            place.setState('movie')

    def toWalkMode(self):
        place = self.cr.playGame.getPlace() if self.cr and self.cr.playGame else None
        if place and hasattr(place, 'fsm'):
            place.setState('walk')

    def toFinalBattleMode(self):
        place = self.cr.playGame.getPlace() if self.cr and self.cr.playGame else None
        if place and hasattr(place, 'fsm'):
            place.setState('finalBattle')

    def _getIntroductionInvestors(self):
        investors = []
        seen = set()

        battle = self.battle
        if battle:
            for suit in getattr(battle, 'suits', ()):
                if suit is None:
                    continue
                try:
                    if suit.dna.name in PlutocratCutscenes.INVESTORS:
                        investors.append(suit)
                        seen.add(suit.doId)
                except:
                    pass

        for obj in list(self.cr.doId2do.values()):
            try:
                if obj.doId in seen:
                    continue
                if getattr(obj, 'zoneId', None) != self.zoneId:
                    continue
                if getattr(getattr(obj, 'dna', None), 'name', '') not in PlutocratCutscenes.INVESTORS:
                    continue
                investors.append(obj)
                seen.add(obj.doId)
            except:
                pass

        return investors[:3]

    def __clickedNameTag(self, avatar):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleClickedNametag(
                    place, avatar)

    def restoreBattlePresentation(self, resetCamera=1):
        if not self.battle:
            return
        if self.hasLocalToon():
            try:
                localAvatar.hideLaffMeters(False)
            except:
                pass
            try:
                localAvatar.laffMeter.show()
                localAvatar.laffMeter.start()
            except:
                pass
            NametagGlobals.setWant2dNametags(False)
            NametagGlobals.setWantActiveNametags(True)
            try:
                base.localAvatar.setFriendsListButtonActive(1)
            except:
                pass
            if resetCamera:
                try:
                    camera.reparentTo(self.battle)
                    camera.setPosHpr(0, -18, 12, 0, -12, 0)
                except:
                    pass
        self.refreshDeepFreezeVisuals()

    def _toonParts(self, toon):
        parts = []
        for methodName in ('getHeadParts', 'getTorsoParts', 'getLegsParts'):
            try:
                for part in getattr(toon, methodName)():
                    if part and part not in parts:
                        parts.append(part)
            except:
                pass
        return parts

    def _laffMeters(self):
        meters = []
        try:
            if localAvatar.laffMeter:
                meters.append(localAvatar.laffMeter)
        except:
            pass
        if self.battle and getattr(self.battle, 'movie', None):
            for meter in getattr(self.battle.movie, 'laffMeters', ()):
                if meter and meter not in meters:
                    meters.append(meter)
        return meters

    def refreshDeepFreezeVisuals(self):
        if self.deepFreezeRoundsLeft <= 0:
            return
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if not toon:
                continue
            for part in self._toonParts(toon):
                try:
                    part.setColorScale(self.deepFreezeColor)
                except:
                    pass
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if not toon:
                continue
            try:
                toon._plutocratLaffMeterColor = VBase4(self.deepFreezeColor)
            except:
                pass
            try:
                messenger.send(
                    toon.uniqueName('set-laff-meter-color'),
                    [self.deepFreezeColor])
            except:
                pass
        for meter in self._laffMeters():
            try:
                meter.clearColorScale()
                meter.show()
            except:
                pass

    def applyDeepFreezeVisuals(self, rounds):
        try:
            rounds = int(rounds)
        except:
            rounds = 2
        self.deepFreezeRoundsLeft = max(
            self.deepFreezeRoundsLeft, max(1, rounds) + 1)
        taskMgr.remove(self.uniqueName('deepFreezeVisualRefresh'))
        taskMgr.doMethodLater(
            0.05, self._refreshDeepFreezeTask,
            self.uniqueName('deepFreezeVisualRefresh'))
        self.refreshDeepFreezeVisuals()

    def _refreshDeepFreezeTask(self, task):
        if self.deepFreezeRoundsLeft <= 0:
            return Task.done
        self.refreshDeepFreezeVisuals()
        return Task.again

    def advanceDeepFreezeVisuals(self):
        if self.deepFreezeRoundsLeft <= 0:
            return
        self.deepFreezeRoundsLeft -= 1
        if self.deepFreezeRoundsLeft <= 0:
            self.clearDeepFreezeVisuals()
        else:
            self.refreshDeepFreezeVisuals()

    def clearDeepFreezeVisuals(self):
        self.deepFreezeRoundsLeft = 0
        taskMgr.remove(self.uniqueName('deepFreezeVisualRefresh'))
        if not self.cr:
            return
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if not toon:
                continue
            for part in self._toonParts(toon):
                try:
                    part.clearColorScale()
                except:
                    pass
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if not toon:
                continue
            try:
                if hasattr(toon, '_plutocratLaffMeterColor'):
                    del toon._plutocratLaffMeterColor
            except:
                pass
            try:
                messenger.send(toon.uniqueName('set-laff-meter-color'))
            except:
                pass
        for meter in self._laffMeters():
            try:
                meter.clearColorScale()
            except:
                pass

    def applyFrozenSuitVisual(self, suit, rounds):
        if not suit:
            return
        try:
            rounds = int(rounds)
        except:
            rounds = 1
        self.frozenSuitRounds[suit.doId] = max(1, rounds) + 1
        try:
            suit.movieFrozen = True
        except:
            pass
        for effectName in ('soaked', 'drenched'):
            try:
                suit.clearSuitStatusEffect(effectName)
            except:
                pass
        self.refreshFrozenSuitVisuals()

    def advanceFrozenSuitVisuals(self):
        expired = []
        for suitId, rounds in list(self.frozenSuitRounds.items()):
            if rounds > 0:
                rounds -= 1
                if rounds <= 0:
                    expired.append(suitId)
                else:
                    self.frozenSuitRounds[suitId] = rounds
        for suitId in expired:
            if suitId in self.frozenSuitRounds:
                del self.frozenSuitRounds[suitId]
        self.refreshFrozenSuitVisuals()

    def clearFrozenSuitVisuals(self):
        self.frozenSuitRounds = {}
        if not self.battle:
            return
        for suit in getattr(self.battle, 'suits', ()):
            if not suit:
                continue
            try:
                suit.movieFrozen = False
                suit.getGeomNode().clearColorScale()
            except:
                pass

    def refreshFrozenSuitVisuals(self):
        if not self.battle:
            return
        for suit in getattr(self.battle, 'suits', ()):
            if not suit:
                continue
            try:
                frozen = bool(
                    self.snowSquallActive or
                    self.frozenSuitRounds.get(suit.doId, 0) > 0)
                suit.movieFrozen = frozen
                if frozen:
                    suit.getGeomNode().setColorScale(0.72, 0.9, 1.0, 1.0)
                else:
                    suit.getGeomNode().clearColorScale()
            except:
                pass

    def setSnowSquallActive(self, active):
        self.snowSquallActive = bool(active)
        if self.environment:
            if self.snowSquallActive:
                self.environment.setSnowSquall()
            else:
                self.environment.setDefault()
        self.refreshFrozenSuitVisuals()
        self.setSnowSquallMusic(self.snowSquallActive)

    def playVictoryMusic(self):
        self._playMusicObject(self.victoryMusic, 1, 1.0)

    def d_avatarEnter(self):
        self.sendUpdate('avatarEnter', [])

    def d_avatarExit(self):
        self.sendUpdate('avatarExit', [])

    def loadEnvironment(self):
        self.geom = loader.loadModel('phase_8/models/areas/ttcc_pcrat_bossRoom')
        self.geom.reparentTo(render)
        safes = self.geom.find('**/safes_2')
        if not safes.isEmpty():
            safes.setTwoSided(1)
        self.fanModel = loader.loadModel('phase_8/models/props/ttcc_prp_pc_fanUnit')
        self.fanModel.setTwoSided(1)
        self.fanModel.setScale(1.4, 1, 1.4)
        for node in self.geom.findAllMatches('**/fan_origin_*'):
            self.fanModel.instanceTo(node)
        self.chuteLeft = self.geom.find('**/chute_door_left')
        self.chuteRight = self.geom.find('**/chute_door_right')
        self.doorLeft = self.geom.find('**/boss_door_L')
        self.doorRight = self.geom.find('**/boss_door_R')
        self.particleRender = render.attachNewNode('particleRender')
        self.particleRender.setDepthWrite(0)
        self.particleRender.setBin('fixed', 1)
        self.environment = PlutocratEnvironment.PlutocratEnvironment(self.geom)
        self.battleNode = self.geom.attachNewNode('battleA')
        self.battleNode.setPosHpr(*PlutocratInstanceGlobals.BATTLE_NODE_POS_HPR)
        self.investorMusic = loader.loadMusic('phase_10/audio/bgm/merc/instance_plutocrat_investors.ogg')
        self.plutocratMusic = loader.loadMusic('phase_10/audio/bgm/merc/instance_plutocrat_battle.ogg')
        self.introMusic = loader.loadMusic('phase_10/audio/bgm/merc/instance_plutocrat_ctscn.ogg')
        self.joinMusic = loader.loadMusic('phase_10/audio/bgm/merc/instance_plutocrat_ctscn_2.ogg')
        self.coldMusic = loader.loadMusic('phase_10/audio/bgm/merc/instance_plutocrat_battle_cold.ogg')
        self.victoryMusic = loader.loadMusic('phase_10/audio/bgm/merc/instance_plutocrat_end.ogg')

    def unloadEnvironment(self):
        self.clearDeepFreezeVisuals()
        self.clearFrozenSuitVisuals()
        if self.environment:
            self.environment.cleanup()
            self.environment = None
        if self.particleRender and not self.particleRender.isEmpty():
            self.particleRender.removeNode()
        self.particleRender = None
        if self.geom and not self.geom.isEmpty():
            self.geom.removeNode()
        self.geom = None
        self.battleNode = None
        if self.fanModel and not self.fanModel.isEmpty():
            self.fanModel.removeNode()
        self.fanModel = None
        self.investorMusic = None
        self.plutocratMusic = None
        self.introMusic = None
        self.joinMusic = None
        self.coldMusic = None
        self.victoryMusic = None
        self.currentMusic = None

    def stopMusic(self):
        if self.musicFadeTrack:
            try:
                self.musicFadeTrack.finish()
            except:
                pass
            self.musicFadeTrack = None
        for music in (self.investorMusic, self.plutocratMusic, self.introMusic, self.joinMusic, self.coldMusic, self.victoryMusic):
            if music:
                try:
                    music.stop()
                except:
                    pass
        self.currentMusic = None

    def playBattleMusic(self):
        target = self.investorMusic if self.plutocratPhase == 1 else self.plutocratMusic
        if target is self.currentMusic:
            return
        self.stopMusic()
        if target:
            try:
                base.playMusic(target, looping=1, volume=0.9)
            except:
                target.setLoop(1)
                target.setVolume(0.9)
                target.play()
            self.currentMusic = target

    def _playMusicObject(self, music, looping=1, volume=0.9):
        self.stopMusic()
        if not music:
            return
        try:
            base.playMusic(music, looping=looping, volume=volume)
        except:
            music.setLoop(looping)
            music.setVolume(volume)
            music.play()
        self.currentMusic = music

    def playIntroMusic(self):
        self._playMusicObject(self.introMusic, 0, 1.0)

    def playJoinMusic(self):
        self._playMusicObject(self.joinMusic, 0, 1.0)

    def playPlutocratMusic(self):
        self._playMusicObject(self.plutocratMusic, 1, 0.9)

    def _setMusicVolume(self, volume, music):
        if music:
            try:
                music.setVolume(volume)
            except:
                pass

    def _finishMusicCrossfade(self, source, target):
        if source and source is not target:
            try:
                source.stop()
            except:
                pass
        self.currentMusic = target
        self.musicFadeTrack = None

    def setSnowSquallMusic(self, active):
        target = self.coldMusic if active else self.plutocratMusic
        source = self.currentMusic
        if not target or target is source:
            return
        if self.musicFadeTrack:
            try:
                self.musicFadeTrack.finish()
            except:
                pass
            self.musicFadeTrack = None
        currentTime = 0.0
        if source:
            try:
                currentTime = source.getTime()
            except:
                currentTime = 0.0
        try:
            target.stop()
        except:
            pass
        try:
            target.setLoop(1)
            target.setVolume(0.0)
            target.setTime(currentTime)
            target.play()
        except:
            try:
                base.playMusic(target, looping=1, volume=0.0)
                target.setTime(currentTime)
            except:
                pass
        self.currentMusic = target
        sourceStart = 0.9
        if source:
            try:
                sourceStart = source.getVolume()
            except:
                pass
        self.musicFadeTrack = Sequence(
            Parallel(
                LerpFunctionInterval(self._setMusicVolume, fromData=sourceStart, toData=0.0, duration=3.0, extraArgs=[source]),
                LerpFunctionInterval(self._setMusicVolume, fromData=0.0, toData=0.9, duration=3.0, extraArgs=[target])),
            Func(self._finishMusicCrossfade, source, target))
        self.musicFadeTrack.start()

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.intervalStored(name, interval)

    def cleanupIntervals(self):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.intervalsCleaned()
        for interval in list(self.activeIntervals.values()):
            try:
                interval.pause()
            except:
                pass
            try:
                DelayDelete.cleanupDelayDeletes(interval)
            except:
                pass
        self.activeIntervals = {}

    def clearInterval(self, name, finish=1):
        if name not in self.activeIntervals:
            return
        interval = self.activeIntervals[name]
        try:
            if finish:
                interval.finish()
            else:
                interval.pause()
        except:
            pass
        try:
            DelayDelete.cleanupDelayDeletes(interval)
        except:
            pass
        if name in self.activeIntervals:
            del self.activeIntervals[name]
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.intervalCleared(name)

    def toonsToBattlePosition(self, toonIds, battleNode):
        if not toonIds or not battleNode:
            return
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for index in range(len(toonIds)):
            toon = self.cr.doId2do.get(toonIds[index])
            if toon:
                pos, h = points[index]
                toon.reparentTo(render)
                toon.setPosHpr(
                    battleNode, pos[0], pos[1], pos[2], h, 0, 0)

    def localToonDied(self):
        targetZone = ZoneUtil.getSafeZoneId(localAvatar.defaultZone)
        place = self.cr.playGame.getPlace()
        if place and hasattr(place, 'fsm'):
            place.fsm.request('died', [{'loader': ZoneUtil.getLoaderName(targetZone), 'where': ZoneUtil.getWhereName(targetZone, 1), 'how': 'teleportIn', 'hoodId': targetZone, 'zoneId': targetZone, 'shardId': None, 'avId': -1, 'battle': 1}])

    def enterOff(self):
        self.stopMusic()

    def exitOff(self):
        pass

    def enterWaitForToons(self):
        taskMgr.remove(self.uniqueName('plutocratInstanceReady'))
        taskMgr.add(self.__waitForInstanceReady, self.uniqueName('plutocratInstanceReady'))

    def __waitForInstanceReady(self, task):
        if not self.gotAllToons:
            return Task.cont
        try:
            place = base.cr.playGame.getPlace()
        except:
            place = None
        if not place or not hasattr(place, 'fsm'):
            return Task.cont
        state = place.fsm.getCurrentState()
        if not state or state.getName() != 'walk':
            return Task.cont
        self.doneBarrier('WaitForToons')
        return Task.done

    def exitWaitForToons(self):
        taskMgr.remove(self.uniqueName('plutocratInstanceReady'))

    def enterIntroduction(self):
        self.controlToons()
        try:
            localAvatar.hideLaffMeters(True)
        except:
            pass
        try:
            base.transitions.fadeIn(0.6)
        except:
            pass
        self.introDelayDeletes = []
        self.introInvestors = []
        taskMgr.remove(self.uniqueName('plutocratIntroDone'))
        taskMgr.add(self.__waitForIntroductionActors, self.uniqueName('plutocratIntroDone'))

    def __waitForIntroductionActors(self, task):
        if not self.gotAllToons:
            return Task.cont

        investors = self._getIntroductionInvestors()
        if len(investors) < 3:
            return Task.cont

        self.introInvestors = investors
        try:
            intervalName = 'IntroductionMovie'
            self.introTrack = Sequence(
                Func(self.playIntroMusic),
                PlutocratCutscenes.makeIntroduction(
                    self, self.introDelayDeletes, self.introInvestors),
                Func(self.__finishIntroductionTrack),
                name=intervalName)
            self.introTrack.delayDeletes = self.introDelayDeletes
            self.introTrack.start()
            self.storeInterval(self.introTrack, intervalName)
            return Task.done
        except Exception as error:
            self.notify.warning('Plutocrat introduction CTSC failed: %s' % error)
            self.__finishIntroductionTrack()
            return Task.done

    def __finishIntroductionTrack(self):
        self.doneBarrier('Introduction')

    def exitIntroduction(self):
        taskMgr.remove(self.uniqueName('plutocratIntroDone'))
        self.clearInterval('IntroductionMovie', finish=0)
        self.introDelayDeletes = []
        self.introInvestors = []
        self.introTrack = None
        try:
            localAvatar.hideLaffMeters(False)
        except:
            pass
        try:
            camera.wrtReparentTo(render)
            base.camLens.setFov(ToontownGlobals.DefaultCameraFov)
        except:
            pass

    def enterBattleOne(self):
        self.cleanupIntervals()
        self.toonsToBattlePosition(self.toons, self.battleNode)
        self.releaseToons()
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        try:
            base.localAvatar.setFriendsListButtonActive(1)
        except:
            pass
        self.accept('clickedNametag', self.__clickedNameTag)
        self.restoreBattlePresentation(resetCamera=0)
        self.playBattleMusic()

    def exitBattleOne(self):
        self.ignore('clickedNametag')
        self.clearDeepFreezeVisuals()
        self.stopMusic()

    def enterReward(self):
        if self.plutocratDeathPlayed:
            taskMgr.doMethodLater(
                0.1,
                self.__finishPlayedDeathReward,
                self.uniqueName('plutocratRewardDone'))
            return
        self.stopMusic()
        taskMgr.add(self.__waitForDeathSuit, self.uniqueName('plutocratRewardDone'))

    def __finishPlayedDeathReward(self, task):
        self.doneBarrier('Reward')
        return Task.done

    def __waitForDeathSuit(self, task):
        plutocrat = None
        for obj in list(self.cr.doId2do.values()):
            try:
                if getattr(getattr(obj, 'dna', None), 'name', '') == 'pcrat':
                    plutocrat = obj
                    break
            except:
                pass
        if not plutocrat:
            if task.time < 5.0:
                return Task.cont
            self.doneBarrier('Reward')
            return Task.done
        try:
            plutocrat.wrtReparentTo(self.battleNode)
            intervalName = 'PlutocratDeathMovie'
            self.deathTrack = Sequence(
                PlutocratCutscenes.makeDeath(self, plutocrat),
                Func(self.doneBarrier, 'Reward'),
                name=intervalName)
            self.deathTrack.start()
            self.storeInterval(self.deathTrack, intervalName)
        except Exception as error:
            self.notify.warning('Plutocrat death CTSC failed: %s' % error)
            self.doneBarrier('Reward')
        return Task.done

    def exitReward(self):
        taskMgr.remove(self.uniqueName('plutocratRewardDone'))
        self.clearInterval('PlutocratDeathMovie', finish=0)
        self.deathTrack = None
        PlutocratCutscenes.cleanupDeath(self)

    def enterEpilogue(self):
        taskMgr.doMethodLater(0.5, self.__finishEpilogue, self.uniqueName('plutocratEpilogueDone'))

    def __finishEpilogue(self, task):
        self.doneBarrier('Epilogue')
        return Task.done

    def exitEpilogue(self):
        taskMgr.remove(self.uniqueName('plutocratEpilogueDone'))
        if localAvatar.doId in self.involvedToons:
            self.__returnToPizzeria()

    def __returnToPizzeria(self):
        place = self.cr.playGame.getPlace()
        if place and hasattr(place, 'fsm'):
            place.fsm.request('teleportOut', [{'loader': ZoneUtil.getLoaderName(ToontownGlobals.TheBrrrgh), 'where': 'toonInterior', 'how': 'teleportIn', 'hoodId': ToontownGlobals.TheBrrrgh, 'zoneId': ToontownGlobals.PizzariaInterior, 'shardId': None, 'avId': -1, 'battle': 1, 'quick': 1}])
