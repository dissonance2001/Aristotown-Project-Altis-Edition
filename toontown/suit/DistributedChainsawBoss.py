from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.fsm import FSM
from direct.interval.IntervalGlobal import Func, LerpFunctionInterval, Parallel, Sequence
from pandac.PandaModules import *
from direct.task import Task

from toontown.battle import BattleBase
from toontown.battle import BattleExperience
from toontown.battle import MovieToonVictory
from toontown.battle import RewardPanel
from toontown.battle.ChainsawMeterGUI import ChainsawMeterGUI
from toontown.distributed import DelayDelete
from toontown.hood import ZoneUtil
from toontown.nametag import NametagGlobals
from toontown.suit import Suit
from toontown.suit import SuitDNA
from toontown.suit import BossCutsceneSkip
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals


OneChainsawController = None


class DistributedChainsawBoss(DistributedObject.DistributedObject, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedChainsawBoss')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedChainsawBoss')
        self.gotAllToons = 0
        self.toons = []
        self.involvedToons = []
        self.toonRequest = None

        self.battleNumber = 0
        self.battleId = 0
        self.battle = None
        self.battleRequest = None
        self.arenaSide = 0

        self.chainsawSuitId = 0
        self.chainsawSuit = None
        self.chainsawSuitRequest = None
        self.chainsawRPM = 10
        self.chainsawPhase = 1

        self.toonRewardDicts = []
        self.toonRewardIds = []
        self.deathList = []
        self.uberList = []
        self.helpfulToons = []
        self.rewardPanel = None

        self.chainsawMeter = None
        self.phaseOneMusic = None
        self.phaseTwoMusic = None
        self.phaseThreeMusic = None
        self.victoryMusic = None

        self.geom = None
        self.battleNode = None
        self.sceneSuit = None
        self.doorEntrance_1 = None
        self.doorEntrance_2 = None
        self.cogEntrance_1_1 = None
        self.cogEntrance_1_2 = None
        self.cogEntrance_2_1 = None
        self.cogEntrance_2_2 = None
        self.doorList = []
        self._introductionTrack = None
        self._introductionDoneSent = 0
        self._chainsawIntroSetup = None
        self._chainsawSpecialHead = None
        self.activeIntervals = {}
        self.cutsceneSkip = BossCutsceneSkip.BossCutsceneSkip(self)

    def announceGenerate(self):
        global OneChainsawController
        DistributedObject.DistributedObject.announceGenerate(self)
        self.loadEnvironment()
        if (OneChainsawController is not None and
                OneChainsawController is not self):
            self.notify.warning(
                'Multiple Chainsaw instance controllers are visible.')
        OneChainsawController = self

    def disable(self):
        global OneChainsawController
        taskMgr.remove(self.uniqueName('chainsawInstanceReady'))
        taskMgr.remove(self.uniqueName('chainsawIntroReady'))
        taskMgr.remove(self.uniqueName('chainsawFoundationReturn'))
        self.__clearIntroductionTrack()
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.cleanup()
        self.cleanupIntervals()
        if self.toonRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
            self.toonRequest = None
        if self.battleRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
            self.battleRequest = None
        if self.chainsawSuitRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.chainsawSuitRequest)
            self.chainsawSuitRequest = None
        self.__destroyChainsawMeter()
        self.__stopBattleMusic()
        self.cleanupBattles()
        self.unloadEnvironment()
        self.ignoreAll()
        if OneChainsawController is self:
            OneChainsawController = None
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
        self.toonRequest = self.cr.relatedObjectMgr.requestObjects(
            self.involvedToons, allCallback=self.__gotAllToons)

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

        self.battleRequest = self.cr.relatedObjectMgr.requestObjects(
            [battleId], allCallback=self.__gotBattle)

    def __gotBattle(self, battles):
        self.battleRequest = None
        if not battles:
            self.battle = None
            return
        if self.battle and self.battle is not battles[0]:
            try:
                self.battle.cleanupBattle()
            except:
                pass
        self.battle = battles[0]

    def setArenaSide(self, arenaSide):
        self.arenaSide = arenaSide

    def setChainsawSuitId(self, suitId):
        self.chainsawSuitId = suitId
        if self.chainsawSuitRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.chainsawSuitRequest)
            self.chainsawSuitRequest = None
        self.chainsawSuit = None
        if not suitId:
            return
        suit = self.cr.doId2do.get(suitId)
        if suit:
            self.__setChainsawSuit(suit)
            return
        self.chainsawSuitRequest = self.cr.relatedObjectMgr.requestObjects(
            [suitId], allCallback=self.__gotChainsawSuit)

    def __gotChainsawSuit(self, suits):
        self.chainsawSuitRequest = None
        if suits:
            self.__setChainsawSuit(suits[0])

    def __setChainsawSuit(self, suit):
        self.chainsawSuit = suit
        if self.state in ('Off', 'WaitForToons', 'Introduction'):
            try:
                suit.hide()
            except:
                pass
        self.__applyChainsawPhaseVisual()

    def getChainsawSuit(self):
        return self.chainsawSuit

    def setChainsawRPM(self, rpm):
        self.chainsawRPM = max(10, min(30, int(rpm)))
        # During BattleOne the server sends the new RPM before the cheat movie
        # starts.  Clash keeps the meter on the old value until the authored
        # point in the movie (Revving Up is 1.0s in).  MovieChainsawCore / the
        # CTSC adapter performs the visible, smooth meter update.
        if self.chainsawMeter and self.state != 'BattleOne':
            self.chainsawMeter.setRPM(self.chainsawRPM)

    def setChainsawPhase(self, phase):
        self.chainsawPhase = max(1, min(3, int(phase)))
        # Phase fields also arrive before their transition CTSC has reached the
        # visual handoff.  Store the authoritative state immediately, but let
        # the battle movie update the live meter/head at the authored moment.
        if self.chainsawMeter and self.state != 'BattleOne':
            self.chainsawMeter.setPhase(self.chainsawPhase)
            self.chainsawMeter.setRPM(self.chainsawRPM)
        # The dedicated Clash phase-transition CTSC controls the exact
        # music handoff timing.  Do not switch tracks as soon as the network
        # phase field arrives.

    def playChainsawBattleMusic(self):
        if self.state == 'BattleOne':
            self.__playBattleMusic()

    def __applyChainsawPhaseVisual(self):
        suit = self.chainsawSuit
        if not suit:
            return
        try:
            from toontown.cutscene.ChainsawIntroCutscene import installChainsawBattleHead
            installChainsawBattleHead(suit, self.chainsawPhase)
        except Exception as error:
            self.notify.warning(
                'Could not install Chainsaw battle head: %s' % error)

    def setBattleExperience(self, *args):
        if len(args) < 75:
            self.notify.warning(
                'Invalid Chainsaw battle experience payload: %s' % len(args))
            return
        entries = []
        for index in xrange(8):
            start = index * 9
            entries.append(tuple(args[start:start + 9]))
        self.deathList = args[72]
        self.uberList = args[73]
        self.helpfulToons = args[74]
        self.toonRewardDicts = BattleExperience.genRewardDicts(tuple(entries))
        self.toonRewardIds = [entry[0] for entry in entries]

    def toonDied(self, avId):
        if avId == localAvatar.doId:
            self.localToonDied()

    def d_avatarEnter(self):
        self.sendUpdate('avatarEnter', [])

    def d_avatarExit(self):
        self.sendUpdate('avatarExit', [])

    def loadEnvironment(self):
        self.geom = loader.loadModel('phase_6/models/areas/ttcc_int_cc_boss')
        self.battleNode = self.geom.attachNewNode('battleA')
        self.battleNode.setPosHpr(0, 10, 0, 180, 0, 0)
        self.geom.reparentTo(render)
        self.setupDoors()

        # Clash removes these development-only pieces after it has copied the
        # real door geometry from their locators.
        for node in self.geom.findAllMatches('**/NORENDER_*'):
            node.removeNode()
        self.geom.hide()

        self.phaseOneMusic = loader.loadMusic(
            'phase_12/audio/bgm/merc/instance_chainsaw_battle.ogg')
        self.phaseTwoMusic = loader.loadMusic(
            'phase_12/audio/bgm/merc/instance_chainsaw_battle_2.ogg')
        self.phaseThreeMusic = loader.loadMusic(
            'phase_12/audio/bgm/merc/instance_chainsaw_battle_3.ogg')
        self.victoryMusic = loader.loadMusic(
            'phase_12/audio/bgm/merc/instance_chainsaw_victory.ogg')

        dna = SuitDNA.SuitDNA()
        dna.newSuit('chainsaw')
        suit = Suit.Suit()
        suit.setDNA(dna)
        suit.dna = dna
        suit.doId = -2551
        suit.loop('neutral')
        try:
            suit.setDisplayName('Chainsaw Consultant')
        except:
            pass
        locator = self.geom.find('**/cog_origin_0')
        if locator.isEmpty():
            suit.reparentTo(render)
            suit.setPosHpr(0, 8, 0, 180, 0, 0)
        else:
            suit.reparentTo(locator)
            suit.setPosHpr(0, 0, 0, 0, 0, 0)
        suit.hide()
        self.sceneSuit = suit

    def setupDoors(self):
        doorModel = loader.loadModel('phase_12/models/modules/bossbot_door')
        entranceOrigin = self.geom.find('**/door_origin_0')
        cogOrigin1 = self.geom.find('**/door_origin_1')
        cogOrigin2 = self.geom.find('**/door_origin_2')
        if (entranceOrigin.isEmpty() or cogOrigin1.isEmpty() or
                cogOrigin2.isEmpty()):
            doorModel.removeNode()
            raise RuntimeError(
                '[Chainsaw] Boss room is missing one or more door origins')

        doorEntrance = doorModel.copyTo(entranceOrigin)
        cogEntrance1 = doorModel.copyTo(cogOrigin1)
        cogEntrance2 = doorModel.copyTo(cogOrigin2)
        self.doorEntrance_1 = doorEntrance.find('**/door_0')
        self.doorEntrance_2 = doorEntrance.find('**/door_1')
        self.cogEntrance_1_1 = cogEntrance1.find('**/door_0')
        self.cogEntrance_1_2 = cogEntrance1.find('**/door_1')
        self.cogEntrance_2_1 = cogEntrance2.find('**/door_0')
        self.cogEntrance_2_2 = cogEntrance2.find('**/door_1')
        self.doorList = [
            self.doorEntrance_1,
            self.doorEntrance_2,
            self.cogEntrance_1_1,
            self.cogEntrance_1_2,
            self.cogEntrance_2_1,
            self.cogEntrance_2_2,
        ]
        doorModel.removeNode()

    def unloadEnvironment(self):
        setup = self._chainsawIntroSetup
        if setup:
            try:
                setup.stopMusic()
            except:
                pass
        head = self._chainsawSpecialHead
        if head:
            try:
                head.stopIntroEffects()
            except:
                pass
        self._chainsawIntroSetup = None
        self._chainsawSpecialHead = None
        self.__destroyChainsawMeter()
        self.__stopBattleMusic()
        self.phaseOneMusic = None
        self.phaseTwoMusic = None
        self.phaseThreeMusic = None
        self.victoryMusic = None

        if self.sceneSuit:
            try:
                self.sceneSuit.cleanup()
            except:
                try:
                    self.sceneSuit.removeNode()
                except:
                    pass
            self.sceneSuit = None
        if self.geom and not self.geom.isEmpty():
            self.geom.removeNode()
        self.geom = None
        self.battleNode = None
        self.doorEntrance_1 = None
        self.doorEntrance_2 = None
        self.cogEntrance_1_1 = None
        self.cogEntrance_1_2 = None
        self.cogEntrance_2_1 = None
        self.cogEntrance_2_2 = None
        self.doorList = []

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.intervalStored(name, interval)

    def cleanupIntervals(self):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.intervalsCleaned()
        for interval in self.activeIntervals.values():
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

    def cleanupBattles(self):
        if self.battle:
            try:
                self.battle.cleanupBattle()
            except:
                pass

    def __destroyChainsawMeter(self):
        if self.chainsawMeter:
            try:
                self.chainsawMeter.destroy()
            except:
                pass
            self.chainsawMeter = None

    def __stopBattleMusic(self):
        for music in (self.phaseOneMusic, self.phaseTwoMusic,
                      self.phaseThreeMusic, self.victoryMusic):
            if music:
                try:
                    music.stop()
                except:
                    pass

    def __setChainsawMusicVolume(self, value, music):
        if music:
            try:
                music.setVolume(value)
            except:
                pass

    def __startChainsawMusicQuiet(self, music):
        if not music:
            return
        try:
            music.setLoop(True)
            music.setVolume(0.0)
            music.play()
        except:
            pass

    def __stopChainsawMusicTrack(self, music):
        if music:
            try:
                music.stop()
            except:
                pass

    def makeChainsawPhaseTwoMusicHandoff(self):
        # The phase field arrives before the authored dialogue cue. Keep the
        # audible transition separate and start it from the phase-two CTSC.
        oldMusic = self.phaseOneMusic
        newMusic = self.phaseTwoMusic
        return Sequence(
            Func(self.__startChainsawMusicQuiet, newMusic),
            Parallel(
                LerpFunctionInterval(
                    self.__setChainsawMusicVolume,
                    fromData=0.9, toData=0.0, duration=6.0,
                    extraArgs=[oldMusic]),
                LerpFunctionInterval(
                    self.__setChainsawMusicVolume,
                    fromData=0.0, toData=0.9, duration=6.0,
                    extraArgs=[newMusic])),
            Func(self.__stopChainsawMusicTrack, oldMusic))

    def __playBattleMusic(self):
        for music in (self.phaseOneMusic, self.phaseTwoMusic, self.phaseThreeMusic):
            if music:
                try:
                    music.stop()
                    music.setVolume(0.9)
                except:
                    pass
        if self.chainsawPhase == 1:
            music = self.phaseOneMusic
        elif self.chainsawPhase == 2:
            music = self.phaseTwoMusic
        else:
            music = self.phaseThreeMusic
        if music:
            try:
                base.playMusic(music, looping=1, volume=0.9)
            except:
                try:
                    music.setLoop(True)
                    music.setVolume(0.9)
                    music.play()
                except:
                    pass

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

    def toonsToBattlePosition(self, toonIds, battleNode):
        if not toonIds or not battleNode:
            return
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for index in xrange(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[index])
            if toon:
                pos, h = points[index]
                toon.reparentTo(render)
                toon.setPosHpr(
                    battleNode, pos[0], pos[1], pos[2], h, 0, 0)

    def localToonDied(self):
        targetZone = ZoneUtil.getSafeZoneId(localAvatar.defaultZone)
        place = self.cr.playGame.getPlace()
        if place and hasattr(place, 'fsm'):
            place.fsm.request('died', [{
                'loader': ZoneUtil.getLoaderName(targetZone),
                'where': ZoneUtil.getWhereName(targetZone, 1),
                'how': 'teleportIn',
                'hoodId': targetZone,
                'zoneId': targetZone,
                'shardId': None,
                'avId': -1,
                'battle': 1,
            }])

    def enterOff(self):
        taskMgr.remove(self.uniqueName('chainsawFoundationReturn'))
        self.__clearIntroductionTrack()

    def exitOff(self):
        pass

    def enterWaitForToons(self):
        taskMgr.remove(self.uniqueName('chainsawInstanceReady'))
        taskMgr.add(
            self.__waitForInstanceReady,
            self.uniqueName('chainsawInstanceReady'))

    def __waitForInstanceReady(self, task):
        if not self.gotAllToons:
            return Task.cont
        place = None
        try:
            place = base.cr.playGame.getPlace()
        except:
            pass
        if not place or not hasattr(place, 'fsm'):
            return Task.cont
        state = place.fsm.getCurrentState()
        if not state or state.getName() != 'walk':
            return Task.cont
        self.doneBarrier('WaitForToons')
        return Task.done

    def exitWaitForToons(self):
        taskMgr.remove(self.uniqueName('chainsawInstanceReady'))

    def enterIntroduction(self):
        self.controlToons()
        self._introductionDoneSent = 0
        if self.geom:
            self.geom.show()
        if self.sceneSuit:
            self.sceneSuit.show()
            self.sceneSuit.unstash()

        try:
            localAvatar.hideLaffMeters(True)
        except:
            pass
        try:
            base.transitions.fadeIn(0.8)
        except:
            pass

        taskMgr.remove(self.uniqueName('chainsawIntroReady'))
        taskMgr.add(
            self.__waitForIntroductionActors,
            self.uniqueName('chainsawIntroReady'))

    def __waitForIntroductionActors(self, task):
        if not self.gotAllToons or not self.sceneSuit:
            return Task.cont
        if not self.battleNode or len(self.doorList) != 6:
            return Task.cont

        delayDeletes = []
        intervalName = 'IntroductionMovie'
        try:
            track = Sequence(
                self.makeIntroductionMovie(delayDeletes),
                Func(self.__doneIntroduction),
                name=intervalName)
            track.delayDeletes = delayDeletes
            self._introductionTrack = track
            track.start()
            self.storeInterval(track, intervalName)
        except:
            for delayDelete in delayDeletes:
                try:
                    delayDelete.destroy()
                except:
                    pass
            raise
        return Task.done

    def makeIntroductionMovie(self, delayDeletes):
        from toontown.cutscene.ChainsawIntroCutscene import makeChainsawIntroduction
        return makeChainsawIntroduction(self, delayDeletes)

    def __doneIntroduction(self):
        if self._introductionDoneSent:
            return
        self._introductionDoneSent = 1
        self.doneBarrier('Introduction')

    def __clearIntroductionTrack(self):
        track = self._introductionTrack
        if track:
            try:
                track.pause()
            except:
                pass
            try:
                DelayDelete.cleanupDelayDeletes(track)
            except:
                pass
        self._introductionTrack = None
        if 'IntroductionMovie' in self.activeIntervals:
            try:
                del self.activeIntervals['IntroductionMovie']
            except:
                pass
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.intervalCleared('IntroductionMovie')

    def exitIntroduction(self):
        taskMgr.remove(self.uniqueName('chainsawIntroReady'))
        self.__clearIntroductionTrack()
        setup = self._chainsawIntroSetup
        if setup:
            try:
                setup.cleanup(removeHead=False)
            except:
                pass
        try:
            localAvatar.hideLaffMeters(False)
        except:
            pass
        self.clearInterval('IntroductionMovie', finish=0)
        self._introductionTrack = None
        try:
            camera.wrtReparentTo(render)
        except:
            pass
        try:
            base.camLens.setMinFov(52)
        except:
            pass
        # releaseToons() enters the Place walk state. Walk.enter() owns the
        # normal Altis/OrbitalCamera handoff.
        self.releaseToons()

    def enterBattleOne(self):
        self.cleanupIntervals()
        if self.geom:
            self.geom.show()
        if self.sceneSuit:
            try:
                self.sceneSuit.hide()
            except:
                pass

        try:
            mult = ToontownBattleGlobals.getBossBattleCreditMultiplier(1)
            localAvatar.inventory.setBattleCreditMultiplier(mult)
        except:
            pass

        self.toonsToBattlePosition(self.toons, self.battleNode)
        self.releaseToons()

        if self.chainsawSuit:
            try:
                self.chainsawSuit.show()
                self.chainsawSuit.unstash()
            except:
                pass
            self.__applyChainsawPhaseVisual()

        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        try:
            base.localAvatar.setFriendsListButtonActive(1)
        except:
            pass

        if self.chainsawMeter is None:
            try:
                self.chainsawMeter = ChainsawMeterGUI()
            except Exception as error:
                self.notify.warning(
                    'Could not create Chainsaw RPM meter: %s' % error)
                self.chainsawMeter = None
        if self.chainsawMeter:
            self.chainsawMeter.setPhase(self.chainsawPhase)
            self.chainsawMeter.setRPM(self.chainsawRPM, instant=True)

        self.__playBattleMusic()

    def exitBattleOne(self):
        self.__stopBattleMusic()
        self.__destroyChainsawMeter()
        self.cleanupBattles()
        try:
            localAvatar.inventory.setBattleCreditMultiplier(1)
        except:
            pass

    def enterDeadwood(self):
        self.cleanupIntervals()
        self.controlToons()
        self.__stopBattleMusic()
        self.__destroyChainsawMeter()
        self.cleanupBattles()
        taskMgr.remove(self.uniqueName('returnFromChainsawDeadwood'))
        taskMgr.doMethodLater(
            0.1, self.__returnFromChainsawDeadwood,
            self.uniqueName('returnFromChainsawDeadwood'))

    def __returnFromChainsawDeadwood(self, task):
        self.doneBarrier('Deadwood')
        if self.hasLocalToon():
            self.__teleportToChainsawLobby()
        return Task.done

    def exitDeadwood(self):
        taskMgr.remove(self.uniqueName('returnFromChainsawDeadwood'))

    def enterReward(self):
        self.cleanupIntervals()
        self.controlToons()
        self.__stopBattleMusic()
        self.__destroyChainsawMeter()

        if self.victoryMusic:
            try:
                self.victoryMusic.stop()
                self.victoryMusic.setPlayRate(1.0)
                base.playMusic(self.victoryMusic, looping=0, volume=1.0)
            except:
                pass

        panelName = self.uniqueName('reward')
        self.rewardPanel = RewardPanel.RewardPanel(panelName)
        victory, camVictory, skipper = MovieToonVictory.doToonVictory(
            1,
            self.involvedToons,
            self.toonRewardIds,
            self.toonRewardDicts,
            self.deathList,
            self.rewardPanel,
            allowGroupShot=0,
            uberList=self.uberList,
            noSkip=True)

        intervalName = 'RewardMovie'
        ival = Sequence(
            Parallel(victory, camVictory),
            Func(self.__doneReward),
            name=intervalName)

        delayDeletes = []
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                delayDeletes.append(
                    DelayDelete.DelayDelete(toon, 'Chainsaw.enterReward'))
        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)

    def __doneReward(self):
        self.doneBarrier('Reward')

    def exitReward(self):
        self.clearInterval('RewardMovie', finish=0)
        if self.victoryMusic:
            try:
                self.victoryMusic.stop()
            except:
                pass
        if self.rewardPanel:
            self.rewardPanel.destroy()
            self.rewardPanel = None

    def enterEpilogue(self):
        # The exact Clash ending CTSC is deliberately left for the next layer.
        # Keep the completed battle path deterministic and return to the lobby.
        self.cleanupIntervals()
        self.controlToons()
        taskMgr.remove(self.uniqueName('returnFromChainsaw'))
        taskMgr.doMethodLater(
            0.1, self.__returnFromChainsaw,
            self.uniqueName('returnFromChainsaw'))

    def __returnFromChainsaw(self, task):
        self.doneBarrier('Epilogue')
        if self.hasLocalToon():
            self.__teleportToChainsawLobby()
        return Task.done

    def __teleportToChainsawLobby(self):
        place = self.cr.playGame.getPlace()
        if place and hasattr(place, 'fsm'):
            place.fsm.request('teleportOut', [{
                'loader': ZoneUtil.getLoaderName(ToontownGlobals.OutdoorZone),
                'where': 'toonInterior',
                'how': 'teleportIn',
                'hoodId': ToontownGlobals.OutdoorZone,
                'zoneId': ToontownGlobals.ChainsawLobby,
                'shardId': None,
                'avId': -1,
                'battle': 1,
                'quick': 1,
            }])

    def exitEpilogue(self):
        taskMgr.remove(self.uniqueName('returnFromChainsaw'))

    def enterFrolic(self):
        self.releaseToons()

    def exitFrolic(self):
        pass
