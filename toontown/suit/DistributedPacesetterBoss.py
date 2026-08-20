from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from direct.fsm import FSM
from direct.interval.IntervalGlobal import *
from direct.task import Task
from pandac.PandaModules import *

from toontown.battle import BattleBase
from toontown.battle import BattleExperience
from toontown.battle import MovieToonVictory
from toontown.battle import RewardPanel
from toontown.building import ElevatorConstants
from toontown.building import ElevatorUtils
from toontown.distributed import DelayDelete
from toontown.hood import ZoneUtil
from toontown.friends import FriendsListManager
from toontown.suit import BossCutsceneSkip
from toontown.nametag import NametagGlobals
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals
from six.moves import range


# This is an instance/controller object only.  The visible Pacesetter is the
# normal DistributedSuit generated for Battle One by DistributedPacesetterBossAI.
OnePacesetterController = None


class DistributedPacesetterBoss(DistributedObject.DistributedObject, FSM.FSM):
    """Standalone Pacesetter instance controller.

    Despite the historical class/file name, this object is deliberately NOT a
    BossCog, BossCog model, DistributedAvatar, or Suit.  It owns only the room,
    elevator/cutscene sequencing, Toon barriers, and battle/reward handoff.
    The actual Pacesetter character is a normal DistributedSuit (``psetter``)
    and is shared by the CTSC and Battle One.
    """

    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPacesetterBoss')

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        FSM.FSM.__init__(self, 'DistributedPacesetterBoss')

        self.gotAllToons = 0
        self.toons = []
        self.involvedToons = []
        self.toonRequest = None

        self.battleNumber = 0
        self.battleId = 0
        self.battle = None
        self.battleRequest = None
        self.arenaSide = 0

        self.activeIntervals = {}
        # Reuse the exact same client-side cutscene skip helper as Altis's
        # existing Cog bosses.  This controller is not a BossCog; the helper
        # only needs the controller's state, involvedToons and activeIntervals.
        self.cutsceneSkip = BossCutsceneSkip.BossCutsceneSkip(self)
        self.elevatorType = ElevatorConstants.ELEVATOR_PACE

        self.pacesetterSuitId = 0
        self.pacesetterSuit = None
        self.pacesetterSuitRequest = None
        self._pacesetterIntroSetup = None
        self._introductionDoneSent = 0

        self.toonRewardDicts = []
        self.toonRewardIds = []
        self.deathList = []
        self.uberList = []
        self.helpfulToons = []
        self.rewardPanel = None

        self.geom = None
        self.battleNode = None
        self.paceNodeIntro = None
        self.paceNodeDeath = None
        self.elevatorEntrance = None
        self.elevatorModel = None
        self.leftDoor = None
        self.rightDoor = None

        self.elevatorMusic = None
        self.battleOneMusic = None
        self.phaseTwoMusic = None
        self.rewardMusic = None
        self.setPhase1MusicRate = 1.0
        self._pacesetterUsingPhaseTwoMusic = False
        self._pacesetterMusicPlaying = False
        self._pacesetterDefeated = False

    # ------------------------------------------------------------------
    # Distributed lifecycle / network state
    # ------------------------------------------------------------------

    def announceGenerate(self):
        global OnePacesetterController
        DistributedObject.DistributedObject.announceGenerate(self)
        self.loadEnvironment()
        if OnePacesetterController is not None and OnePacesetterController is not self:
            self.notify.warning('Multiple Pacesetter instance controllers are visible.')
        OnePacesetterController = self

    def disable(self):
        global OnePacesetterController

        taskMgr.remove(self.uniqueName('pacesetterInstanceReady'))
        taskMgr.remove(self.uniqueName('pacesetterIntroReady'))
        taskMgr.remove(self.uniqueName('returnFromPacesetter'))

        if self.toonRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
            self.toonRequest = None
        if self.battleRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.battleRequest)
            self.battleRequest = None
        if self.pacesetterSuitRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.pacesetterSuitRequest)
            self.pacesetterSuitRequest = None

        setup = self._pacesetterIntroSetup
        if setup:
            try:
                setup.cleanup()
            except:
                pass
        self._pacesetterIntroSetup = None

        self.cutsceneSkip.cleanup()
        self.cleanupIntervals()
        self.cleanupBattles()
        self.unloadEnvironment()
        self.ignoreAll()

        self.pacesetterSuit = None
        self.pacesetterSuitId = 0

        if OnePacesetterController is self:
            OnePacesetterController = None

        DistributedObject.DistributedObject.disable(self)

    def delete(self):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.delete()
            self.cutsceneSkip = None
        DistributedObject.DistributedObject.delete(self)

    def setState(self, state):
        self.cutsceneSkip.stateChanged(state)
        self.request(state)

    def requestCutsceneSkipVote(self):
        self.sendUpdate('requestSkip', [])

    def setVoteSkips(self, voteTotal, playerTotal):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.setVoteSkips(voteTotal, playerTotal)

    def setCutsceneSkip(self):
        if getattr(self, 'cutsceneSkip', None):
            self.cutsceneSkip.setCutsceneSkip()

    def setToonIds(self, involvedToons, toons, unused):
        self.involvedToons = involvedToons
        self.toons = toons

        if self.toonRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.toonRequest)
        self.gotAllToons = 0

        if not self.involvedToons:
            self.toonRequest = None
            self.gotAllToons = 1
            messenger.send('gotAllToons')
            return

        self.toonRequest = self.cr.relatedObjectMgr.requestObjects(
            self.involvedToons,
            allCallback=self.__gotAllToons,
            eachCallback=self.gotToon)

    def gotToon(self, toon):
        if self.state == 'Elevator':
            self.placeToonInElevator(toon)

    def __gotAllToons(self, toons):
        self.toonRequest = None
        self.gotAllToons = 1
        messenger.send('gotAllToons')

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

    def setPacesetterSuitId(self, suitId):
        self.pacesetterSuitId = suitId

        if self.pacesetterSuitRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.pacesetterSuitRequest)
            self.pacesetterSuitRequest = None

        self.pacesetterSuit = None
        if not suitId:
            return

        suit = self.cr.doId2do.get(suitId)
        if suit:
            self.__setPacesetterSuit(suit)
            return

        self.pacesetterSuitRequest = self.cr.relatedObjectMgr.requestObjects(
            [suitId], allCallback=self.__gotPacesetterSuit)

    def __gotPacesetterSuit(self, suits):
        self.pacesetterSuitRequest = None
        if suits:
            self.__setPacesetterSuit(suits[0])

    def __setPacesetterSuit(self, suit):
        self.pacesetterSuit = suit
        # Battle One is created on the AI before the Introduction state is
        # broadcast.  Hide the real Suit until the CTSC itself reveals him at
        # the authored first-dialogue cue.
        if self.state in ('Off', 'WaitForToons', 'Elevator', 'Introduction'):
            try:
                suit.hide()
            except:
                pass

    def getPacesetterSuit(self):
        return self.pacesetterSuit

    def setBattleExperience(self, *args):
        # The DC field contains eight identical nine-value Toon reward groups,
        # followed by deathList, uberList and helpfulToons.
        if len(args) < 75:
            self.notify.warning('Invalid Pacesetter battle experience payload: %s' % (len(args),))
            return

        entries = []
        for index in range(8):
            start = index * 9
            entries.append(tuple(args[start:start + 9]))

        self.deathList = args[72]
        self.uberList = args[73]
        self.helpfulToons = args[74]
        self.toonRewardDicts = BattleExperience.genRewardDicts(tuple(entries))
        self.toonRewardIds = [entry[0] for entry in entries]

    def d_avatarEnter(self):
        self.sendUpdate('avatarEnter', [])

    def d_avatarExit(self):
        if self.cr:
            self.sendUpdate('avatarExit', [])

    def toonDied(self, avId):
        if avId == localAvatar.doId:
            self.localToonDied()

    # ------------------------------------------------------------------
    # Room / elevator
    # ------------------------------------------------------------------

    def loadEnvironment(self):
        self.geom = loader.loadModel('phase_8/models/areas/ttcc_psetter_bossRoom')
        self.geom.setPos(0, 0, 0)
        self.geom.setScale(1.1)

        self.battleNode = self.geom.attachNewNode('battleA')
        self.battleNode.setPosHpr(0, 50, 0, 0, 0, 0)
        self.paceNodeIntro = self.geom.attachNewNode('paceNodeIntro')
        self.paceNodeIntro.setPosHpr(-37.3, 41.4, 0, 0, 0, 0)
        self.paceNodeDeath = self.geom.attachNewNode('paceNodeDeath')
        self.paceNodeDeath.setPosHpr(-37.3, 41.4, 0, 0, 0, 0)

        self.elevatorEntrance = self.geom.find('**/elevator_origin')
        self.elevatorEntrance.setH(180)
        self.elevatorEntrance.getChildren().detach()
        self.elevatorEntrance.setScale(1)

        self.elevatorModel = loader.loadModel(
            'phase_8/models/modules/ttcc_psetter_elevator.bam')
        self.elevatorModel.reparentTo(self.elevatorEntrance)
        self.setupElevator(self.elevatorModel)

        # Preserve the working v8.4 door nodes/sounds exactly.
        self.leftDoor = self.elevatorModel.find('**/left_door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left-door')
        self.rightDoor = self.elevatorModel.find('**/right_door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right-door')

        self.openSfx = base.loader.loadSfx('phase_5/audio/sfx/elevator_door_open.ogg')
        self.finalOpenSfx = None
        self.closeSfx = base.loader.loadSfx('phase_5/audio/sfx/elevator_door_close.ogg')
        self.finalCloseSfx = None
        self.openDoors = ElevatorUtils.getOpenInterval(
            self, self.leftDoor, self.rightDoor,
            self.openSfx, self.finalOpenSfx, self.elevatorType)
        self.closeDoors = ElevatorUtils.getCloseInterval(
            self, self.leftDoor, self.rightDoor,
            self.closeSfx, self.finalCloseSfx, self.elevatorType)
        self.closeDoors.start()
        self.closeDoors.finish()

        self.elevatorMusic = base.loader.loadMusic(
            'phase_9/audio/bgm/merc/instance_pacesetter_elevator.ogg')
        self.battleOneMusic = base.loader.loadMusic(
            'phase_9/audio/bgm/merc/instance_pacesetter_battle.ogg')
        self.phaseTwoMusic = base.loader.loadMusic(
            'phase_9/audio/bgm/merc/OVERCLOCKED.ogg')
        self.rewardMusic = base.loader.loadMusic(
            'phase_9/audio/bgm/merc/instance_pacesetter_victory.ogg')

        self.geom.reparentTo(render)

    def unloadEnvironment(self):
        if self.elevatorMusic:
            self.elevatorMusic.stop()
        if self.battleOneMusic:
            self.battleOneMusic.stop()
        if self.phaseTwoMusic:
            self.phaseTwoMusic.stop()
        if self.rewardMusic:
            self.rewardMusic.stop()
        if self.geom:
            self.geom.removeNode()
            self.geom = None
        self.battleNode = None
        self.paceNodeIntro = None
        self.paceNodeDeath = None
        self.elevatorEntrance = None
        self.elevatorModel = None

    def setupElevator(self, elevatorModel):
        self.elevatorModel = elevatorModel
        self.leftDoor = elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = elevatorModel.find('**/left_door')
        self.rightDoor = elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = elevatorModel.find('**/right_door')

    def placeToonInElevator(self, toon):
        # Pacesetter uses normal Toons, never VP/CJ Cog disguises.
        if getattr(toon, 'isDisguised', 0):
            toon.takeOffSuit()
        try:
            toon.getGeomNode().show()
        except:
            pass
        toonIndex = self.involvedToons.index(toon.doId)
        toon.reparentTo(self.elevatorModel)
        toon.setPos(*ElevatorConstants.ElevatorPoints[toonIndex])
        toon.setHpr(180, 0, 0)
        toon.loop('neutral')

    # ------------------------------------------------------------------
    # Generic controller helpers (copied from the useful, non-model parts of
    # Altis's miniboss flow; there is no BossCog object behind these methods).
    # ------------------------------------------------------------------

    def storeInterval(self, interval, name):
        if name in self.activeIntervals:
            self.clearInterval(name, finish=1)
        self.activeIntervals[name] = interval
        self.cutsceneSkip.intervalStored(name, interval)

    def cleanupIntervals(self):
        self.cutsceneSkip.intervalsCleaned()
        for interval in self.activeIntervals.values():
            try:
                interval.finish()
            except:
                pass
            DelayDelete.cleanupDelayDeletes(interval)
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
        DelayDelete.cleanupDelayDeletes(interval)
        if name in self.activeIntervals:
            del self.activeIntervals[name]
        self.cutsceneSkip.intervalCleared(name)

    def cleanupBattles(self):
        if self.battle:
            try:
                self.battle.cleanupBattle()
            except:
                pass

    def hasLocalToon(self):
        return localAvatar.doId in self.involvedToons

    def makeEndOfBattleMovie(self, hasLocalToon):
        return Sequence()

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
            if self.battle and hasattr(self.battle, 'toons') and toon in self.battle.toons:
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
        if not toonIds:
            return
        points = BattleBase.BattleBase.toonPoints[len(toonIds) - 1]
        for index in range(len(toonIds)):
            toon = base.cr.doId2do.get(toonIds[index])
            if toon:
                pos, h = points[index]
                toon.reparentTo(render)
                toon.setPosHpr(battleNode, pos[0], pos[1], pos[2], h, 0, 0)

    def localToonDied(self):
        targetZone = ZoneUtil.getSafeZoneId(localAvatar.defaultZone)
        place = self.cr.playGame.getPlace()
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

    # ------------------------------------------------------------------
    # FSM states: standalone elevator -> original CTSC -> one Suit battle.
    # ------------------------------------------------------------------

    def enterOff(self):
        self.cleanupIntervals()

    def exitOff(self):
        pass

    def enterWaitForToons(self):
        # Preserve v7/v8.4's readiness gate.  The place must already be in
        # walk before Elevator requests movie mode, otherwise Altis re-enables
        # movement after teleportIn finishes.
        taskMgr.remove(self.uniqueName('pacesetterInstanceReady'))
        taskMgr.add(
            self.__waitForPacesetterInstanceReady,
            self.uniqueName('pacesetterInstanceReady'))
        if self.geom:
            self.geom.hide()

    def __waitForPacesetterInstanceReady(self, task):
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
        taskMgr.remove(self.uniqueName('pacesetterInstanceReady'))
        if self.geom:
            self.geom.show()

    def enterElevator(self):
        self.cleanupIntervals()

        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                toon.stopLookAround()
                toon.stopSmooth()
                self.placeToonInElevator(toon)

        self.toMovieMode()
        camera.reparentTo(self.elevatorModel)
        camera.setPosHpr(0, 30, 8, 180, 0, 0)
        base.camLens.setMinFov(30)
        base.playMusic(self.elevatorMusic, looping=1, volume=1.0)
        base.transitions.fadeIn(0.8)

        intervalName = 'ElevatorMovie'
        rideTrack = Sequence(
            ElevatorUtils.getRideElevatorInterval(self.elevatorType),
            ElevatorUtils.getRideElevatorInterval(self.elevatorType),
            self.openDoors,
            Func(camera.wrtReparentTo, render),
            Func(self.__donePacesetterElevator),
            name=intervalName)
        rideTrack.start()
        self.storeInterval(rideTrack, intervalName)

    def __donePacesetterElevator(self):
        self.doneBarrier('Elevator')

    def exitElevator(self):
        self.clearInterval('ElevatorMovie', finish=0)
        if self.elevatorMusic:
            self.elevatorMusic.stop()
        camera.wrtReparentTo(render)

    def enterIntroduction(self):
        self.controlToons()
        self._introductionDoneSent = 0
        taskMgr.remove(self.uniqueName('pacesetterIntroReady'))
        taskMgr.add(self.__waitForIntroductionActors,
                    self.uniqueName('pacesetterIntroReady'))

    def __waitForIntroductionActors(self, task):
        if not self.gotAllToons or not self.pacesetterSuit:
            return Task.cont

        delayDeletes = []
        intervalName = 'IntroductionMovie'
        seq = Sequence(
            self.makeIntroductionMovie(delayDeletes),
            Func(self.__doneIntroduction),
            name=intervalName)
        seq.delayDeletes = delayDeletes
        seq.start()
        self.storeInterval(seq, intervalName)
        return Task.done

    def makeIntroductionMovie(self, delayDeletes):
        from toontown.cutscene.PacesetterIntroCutscene import makePacesetterIntroduction
        return makePacesetterIntroduction(self, delayDeletes)

    def __doneIntroduction(self):
        if self._introductionDoneSent:
            return
        self._introductionDoneSent = 1
        self.doneBarrier('Introduction')

    def exitIntroduction(self):
        taskMgr.remove(self.uniqueName('pacesetterIntroReady'))
        setup = self._pacesetterIntroSetup
        if setup:
            setup.cleanup()
        self.clearInterval('IntroductionMovie', finish=0)
        self.releaseToons()
        try:
            ElevatorUtils.closeDoors(
                self.leftDoor, self.rightDoor, self.elevatorType)
        except:
            pass
        base.camera.wrtReparentTo(render)
        base.camLens.setMinFov(52)

    def stopPhaseOneMusic(self):
        if self.battleOneMusic:
            self.battleOneMusic.stop()
        self._pacesetterMusicPlaying = False

    def startPhaseTwoMusic(self):
        self._pacesetterUsingPhaseTwoMusic = True
        if self.phaseTwoMusic:
            self.phaseTwoMusic.setPlayRate(1.0)
            self.phaseTwoMusic.setLoop(True)
            self.phaseTwoMusic.play()
            self._pacesetterMusicPlaying = True

    def getActivePacesetterBattleMusic(self):
        if self._pacesetterUsingPhaseTwoMusic:
            return self.phaseTwoMusic
        return self.battleOneMusic

    def getActivePacesetterMusicRate(self):
        music = self.getActivePacesetterBattleMusic()
        if music:
            try:
                return float(music.getPlayRate())
            except:
                pass
        if self._pacesetterUsingPhaseTwoMusic:
            return 1.0
        return float(self.setPhase1MusicRate)

    def setActivePacesetterMusicRate(self, rate):
        music = self.getActivePacesetterBattleMusic()
        if music:
            try:
                music.setPlayRate(rate)
            except:
                pass

    def stopPacesetterBattleMusic(self):
        if self.battleOneMusic:
            self.battleOneMusic.stop()
        if self.phaseTwoMusic:
            self.phaseTwoMusic.stop()
        self._pacesetterMusicPlaying = False

    def restartPacesetterBattleMusic(self):
        if self._pacesetterDefeated or self._pacesetterMusicPlaying:
            return
        music = self.getActivePacesetterBattleMusic()
        if not music:
            return
        try:
            if self._pacesetterUsingPhaseTwoMusic:
                music.setPlayRate(1.0)
            else:
                music.setPlayRate(self.setPhase1MusicRate)
            music.setLoop(True)
            music.play()
            self._pacesetterMusicPlaying = True
        except:
            pass

    def beginPacesetterDefeat(self):
        self._pacesetterDefeated = True

    def isPacesetterBattleMusicPlaying(self):
        return bool(self._pacesetterMusicPlaying)

    def setBattleMusicSpeed(self):
        # Pacesetter's Come On attack increases the phase-one music speed.
        # This is encounter music state only; it does not depend on BossCog.
        self.setPhase1MusicRate += 0.025
        if self.battleOneMusic:
            self.battleOneMusic.setPlayRate(self.setPhase1MusicRate)

    def __clickedNameTag(self, avatar):
        if self.cr:
            place = self.cr.playGame.getPlace()
            if place and hasattr(place, 'fsm'):
                FriendsListManager.FriendsListManager._FriendsListManager__handleClickedNametag(place, avatar)

    def enterBattleOne(self):
        self.cleanupIntervals()
        mult = ToontownBattleGlobals.getBossBattleCreditMultiplier(1)
        localAvatar.inventory.setBattleCreditMultiplier(mult)
        self.toonsToBattlePosition(self.toons, self.battleNode)
        self.releaseToons()

        if self.pacesetterSuit:
            try:
                self.pacesetterSuit.show()
            except:
                pass

        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setFriendsListButtonActive(1)
        self.accept('clickedNametag', self.__clickedNameTag)
        self.setPhase1MusicRate = 1.0
        self._pacesetterUsingPhaseTwoMusic = False
        self._pacesetterDefeated = False
        if self.battleOneMusic:
            self.battleOneMusic.setPlayRate(self.setPhase1MusicRate)
        if self.phaseTwoMusic:
            self.phaseTwoMusic.stop()
        base.playMusic(self.battleOneMusic, looping=1, volume=0.9)
        self._pacesetterMusicPlaying = True

    def exitBattleOne(self):
        self.ignore('clickedNametag')
        self.stopPacesetterBattleMusic()
        self.cleanupBattles()
        localAvatar.inventory.setBattleCreditMultiplier(1)

    def enterVictory(self):
        # Compatibility only for administrator-forced legacy state changes.
        self.controlToons()
        self.doneBarrier('Victory')

    def exitVictory(self):
        pass

    def enterReward(self):
        self.cleanupIntervals()
        self.controlToons()
        self.stopPacesetterBattleMusic()
        if self.rewardMusic:
            self.rewardMusic.stop()
            self.rewardMusic.setPlayRate(1.0)
            base.playMusic(self.rewardMusic, looping=0, volume=1.0)

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
                    DelayDelete.DelayDelete(toon, 'Pacesetter.enterReward'))
        ival.delayDeletes = delayDeletes
        ival.start()
        self.storeInterval(ival, intervalName)

    def __doneReward(self):
        self.doneBarrier('Reward')

    def exitReward(self):
        self.clearInterval('RewardMovie', finish=0)
        if self.rewardMusic:
            self.rewardMusic.stop()
        if self.rewardPanel:
            self.rewardPanel.destroy()
            self.rewardPanel = None

    def enterEpilogue(self):
        # Return directly to Donald's Dreamland playground.  There is no
        # CJ/Cog-HQ epilogue or BossCog final round anymore.
        self.cleanupIntervals()
        self.controlToons()
        taskMgr.remove(self.uniqueName('returnFromPacesetter'))
        taskMgr.doMethodLater(
            0.1, self.__returnFromPacesetter,
            self.uniqueName('returnFromPacesetter'))

    def __returnFromPacesetter(self, task):
        if not self.hasLocalToon():
            return Task.done

        targetZone = ToontownGlobals.DonaldsDreamland
        place = self.cr.playGame.getPlace()
        if place and hasattr(place, 'fsm'):
            place.fsm.request('teleportOut', [{
                'loader': ZoneUtil.getLoaderName(targetZone),
                'where': ZoneUtil.getWhereName(targetZone, 1),
                'how': 'teleportIn',
                'hoodId': ToontownGlobals.DonaldsDreamland,
                'zoneId': targetZone,
                'shardId': None,
                'avId': -1,
                'battle': 1,
            }])
        return Task.done

    def exitEpilogue(self):
        taskMgr.remove(self.uniqueName('returnFromPacesetter'))

    def enterFrolic(self):
        self.releaseToons()

    def exitFrolic(self):
        pass
