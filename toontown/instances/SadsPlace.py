from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM, State
from direct.interval.IntervalGlobal import Func, LerpPosHprInterval, LerpPosInterval, Parallel, Sequence, SoundInterval, Wait
from pandac.PandaModules import Point3
from otp.otpbase import OTPGlobals
from toontown.battle import BattlePlace
from toontown.chat.ChatGlobals import WTSystem
from toontown.chat.WhisperPopup import WhisperPopup
from toontown.building import ElevatorConstants, ElevatorUtils
from toontown.nametag import NametagGlobals
from toontown.toon import Toon
from toontown.toonbase import ToontownGlobals


class SadsPlace(BattlePlace.BattlePlace):
    notify = DirectNotifyGlobal.directNotify.newCategory('SadsPlace')
    CorridorModel = 'phase_13/models/events/halloween/sads_corridor'
    CorridorTextures = (
        'phase_13/maps/events/halloween/corridor_deco.png',
        'phase_13/maps/events/halloween/corridor_deco_2.png',
        'phase_13/maps/events/halloween/corridor_wall.png'
    )
    OpeningRoomModel = 'phase_13/models/events/halloween/candleGame_arena'
    OpeningMusic = 'phase_13/audio/bgm/halloween/FF_too_much.ogg'
    ElevatorMusic = 'phase_13/audio/bgm/april_toons/erfit/elevator_countErfit_1.ogg'
    CorridorElevatorMusic = 'phase_13/audio/bgm/april_toons/erfit/elevator_countErfit_2.ogg'
    ElevatorModel = 'phase_5/models/cogdominium/tt_m_ara_csa_elevatorB'
    CorridorElevatorPos = (0.0, -36.5155982971191, 0.00000594914990870166)

    def __init__(self, loader, parentFSM, doneEvent):
        BattlePlace.BattlePlace.__init__(self, loader, doneEvent)
        self.parentFSM = parentFSM
        self.zoneId = None
        self.corridor = None
        self.corridorTextures = []
        self.corridorElevator = None
        self.corridorElevatorMusic = None
        self.corridorLeftDoor = None
        self.corridorRightDoor = None
        self.openingRoom = None
        self.elevatorOrigin = None
        self.exitElevatorOrigin = None
        self.cutsceneElevator = None
        self.runElevator = None
        self.runLeftDoor = None
        self.runRightDoor = None
        self.cutsceneLeftDoor = None
        self.cutsceneRightDoor = None
        self.openingMusic = None
        self.elevatorMusic = None
        self.openSfx = None
        self.finalOpenSfx = None
        self.closeSfx = None
        self.finalCloseSfx = None
        self.dingSfx = None
        self.notificationSfx = None
        self.cutsceneTrack = None
        self.elevatorTrack = None
        self.toonsInElevator = []
        self.previousFov = None
        self._corridorEntry = None
        self._corridorSpawn = None
        self.fsm = ClassicFSM.ClassicFSM('SadsPlace', [
            State.State('start', self.enterStart, self.exitStart, ['openingScene']),
            State.State('openingScene', self.enterOpeningScene,
                        self.exitOpeningScene, ['elevatorToCorridor']),
            State.State('elevatorToCorridor', self.enterElevatorToCorridor,
                        self.exitElevatorToCorridor, ['goldenCorridor']),
            State.State('goldenCorridor', self.enterGoldenCorridor,
                        self.exitGoldenCorridor, ['walk']),
            State.State('walk', self.enterWalk, self.exitWalk,
                        ['stickerBook', 'sit', 'teleportOut', 'final']),
            State.State('stickerBook', self.enterStickerBook, self.exitStickerBook,
                        ['walk', 'teleportOut', 'final']),
            State.State('sit', self.enterSit, self.exitSit,
                        ['walk', 'teleportOut', 'final']),
            State.State('teleportOut', self.enterTeleportOut,
                        self.exitTeleportOut, ['walk', 'final']),
            State.State('final', self.enterFinal, self.exitFinal, ['start'])
        ], 'start', 'final')

    def uniqueName(self, name):
        return 'SadsPlace-%s' % name

    def load(self):
        BattlePlace.BattlePlace.load(self)
        self.parentFSM.getStateNamed('sads').addChild(self.fsm)
        self.townBattle = self.loader.townBattle

        self.corridor = loader.loadModel(self.CorridorModel)
        if self.corridor.isEmpty():
            self.notify.error('Could not load Golden Corridor model: %s.bam' % self.CorridorModel)
        self.corridor.reparentTo(render)
        self.corridor.stash()

        for texturePath in self.CorridorTextures:
            try:
                texture = loader.loadTexture(texturePath)
                if texture:
                    self.corridorTextures.append(texture)
            except Exception:
                self.notify.warning('Could not preload Sads corridor texture: %s' % texturePath)

        self._corridorEntry = self._findNode((
            '**/elevator_origin',
            '**/elevator_origin_0',
            '**/elevatorOrigin'
        ))
        self._corridorSpawn = self._findNode((
            '**/elevator_exit',
            '**/toon_spawn',
            '**/corridor_spawn',
            '**/spawn_point',
            '**/spawn'
        ))

        self.openingMusic = loader.loadMusic(self.OpeningMusic)
        self.elevatorMusic = loader.loadMusic(self.ElevatorMusic)
        self.corridorElevatorMusic = loader.loadMusic(self.CorridorElevatorMusic)
        self.openSfx = loader.loadSfx('phase_5/audio/sfx/elevator_door_open.ogg')
        self.finalOpenSfx = None
        self.closeSfx = loader.loadSfx('phase_5/audio/sfx/elevator_door_close.ogg')
        self.finalCloseSfx = None
        self.dingSfx = base.loader.loadSfx('phase_5/audio/sfx/elevator_door_close.ogg')
        self.notificationSfx = base.loader.loadSfx('phase_3/audio/sfx/clock03.ogg')

    def unload(self):
        self._stopTracks()
        self._detachToonsAndCamera()
        self._removeCutsceneElevator()
        self._removeCorridorElevator()
        if self.corridor and not self.corridor.isEmpty():
            self.corridor.removeNode()
        self.corridor = None
        self.corridorTextures = []
        self.parentFSM.getStateNamed('sads').removeChild(self.fsm)
        del self.parentFSM
        del self.fsm
        self.ignoreAll()
        BattlePlace.BattlePlace.unload(self)

    def enter(self, requestStatus):
        self.zoneId = requestStatus['zoneId']
        self.previousFov = base.camLens.getMinFov()
        self.fsm.enterInitialState()
        try:
            base.transitions.fadeOut(0.0)
        except Exception:
            pass
        NametagGlobals.setWant2dNametags(False)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setTeleportAvailable(0)
        self._loadCutsceneElevator()
        self._loadCorridorElevator()
        self._stageToonsForOpeningScene()
        self.fsm.request('openingScene', [requestStatus])

    def exit(self):
        self._stopTracks()
        self._detachToonsAndCamera()
        self.fsm.requestFinalState()
        self.ignoreAll()
        NametagGlobals.setWant2dNametags(False)
        if self.previousFov is not None:
            base.camLens.setMinFov(self.previousFov)
            self.previousFov = None

    def _findNode(self, patterns):
        if not self.corridor:
            return None
        for pattern in patterns:
            node = self.corridor.find(pattern)
            if not node.isEmpty():
                return node
        return None

    def _findElevatorDoors(self, elevator):
        leftDoor = elevator.find('**/left_door')
        rightDoor = elevator.find('**/right_door')
        if leftDoor.isEmpty() or rightDoor.isEmpty():
            self.notify.error('Sads elevator model is missing left_door/right_door.')
        return leftDoor, rightDoor

    def _findOpeningElevatorDoors(self, elevator):
        leftDoor = elevator.find('**/left_door')
        rightDoor = elevator.find('**/right_door')
        if leftDoor.isEmpty() or rightDoor.isEmpty():
            self.notify.error('Sads opening elevator is missing left_door/right_door nodes.')
        return leftDoor, rightDoor

    def _loadCutsceneElevator(self):
        if self.cutsceneElevator and not self.cutsceneElevator.isEmpty():
            return

        self.openingRoom = loader.loadModel(self.OpeningRoomModel)
        if self.openingRoom.isEmpty():
            self.notify.error('Could not load Sads opening room: %s.bam' % self.OpeningRoomModel)
        self.openingRoom.setPos(0, 0, 0)
        self.openingRoom.reparentTo(render)
        self.openingRoom.stash()

        self.elevatorOrigin = self.openingRoom.find('**/entry-elevator_origin')
        if self.elevatorOrigin.isEmpty():
            self.notify.error('Sads opening room is missing entry-elevator_origin.')
        self.exitElevatorOrigin = self.openingRoom.find('**/exit-elevator_origin')
        if self.exitElevatorOrigin.isEmpty():
            self.notify.error('Sads opening room is missing exit-elevator_origin.')

        self.elevatorOrigin.setH(180)
        self.elevatorOrigin.getChildren().detach()
        self.elevatorOrigin.setScale(1)
        self.exitElevatorOrigin.getChildren().detach()
        self.exitElevatorOrigin.setScale(1)

        self.cutsceneElevator = loader.loadModel(self.ElevatorModel)
        if self.cutsceneElevator.isEmpty():
            self.notify.error('Could not load Sads entry elevator: %s' % self.ElevatorModel)
        self.cutsceneElevator.reparentTo(self.elevatorOrigin)
        self.cutsceneElevator.setScale(1)
        self.cutsceneElevator.setColorScaleOff()
        self.cutsceneLeftDoor, self.cutsceneRightDoor = self._findOpeningElevatorDoors(self.cutsceneElevator)
        ElevatorUtils.closeDoors(
            self.cutsceneLeftDoor,
            self.cutsceneRightDoor,
            ElevatorConstants.ELEVATOR_NORMAL
        )

        self.runElevator = loader.loadModel(self.ElevatorModel)
        if self.runElevator.isEmpty():
            self.notify.error('Could not load Sads exit elevator: %s' % self.ElevatorModel)
        self.runElevator.reparentTo(self.exitElevatorOrigin)
        self.runElevator.setScale(1)
        self.runElevator.setColorScaleOff()
        self.runLeftDoor, self.runRightDoor = self._findOpeningElevatorDoors(self.runElevator)
        ElevatorUtils.closeDoors(
            self.runLeftDoor,
            self.runRightDoor,
            ElevatorConstants.ELEVATOR_NORMAL
        )

    def _loadCorridorElevator(self):
        if self.corridorElevator and not self.corridorElevator.isEmpty():
            return

        self.corridorElevator = loader.loadModel(self.ElevatorModel)
        if self.corridorElevator.isEmpty():
            self.notify.error('Could not load Golden Corridor elevator: %s' % self.ElevatorModel)

        if self._corridorEntry:
            self._corridorEntry.getChildren().detach()
            self._corridorEntry.setScale(1)
            self.corridorElevator.reparentTo(self._corridorEntry)
            self.corridorElevator.setPosHpr(0, 0, 0, 180, 0, 0)
            self.corridorElevator.setScale(1)
        else:
            self.corridorElevator.reparentTo(self.corridor)
            self.corridorElevator.setPosHpr(*self.CorridorElevatorPos, 180, 0, 0)
            self.corridorElevator.setScale(1)
            self.notify.warning('Sads corridor has no elevator_origin locator; using the authored elevator_origin transform.')
        self.corridorLeftDoor, self.corridorRightDoor = self._findElevatorDoors(self.corridorElevator)
        ElevatorUtils.closeDoors(
            self.corridorLeftDoor,
            self.corridorRightDoor,
            ElevatorConstants.ELEVATOR_NORMAL
        )

    def _getPartyToons(self):
        toons = []
        localToon = base.localAvatar
        for obj in list(base.cr.doId2do.values()):
            if isinstance(obj, Toon.Toon):
                if obj is localToon or getattr(obj, 'zoneId', None) == self.zoneId:
                    toons.append(obj)
        if localToon not in toons:
            toons.insert(0, localToon)
        toons.sort(key=lambda toon: toon.doId)
        return toons

    def _stageToonsForOpeningScene(self):
        self.toonsInElevator = self._getPartyToons()
        for index, toon in enumerate(self.toonsInElevator):
            try:
                toon.stopLookAround()
                toon.stopSmooth()
            except Exception:
                pass
            try:
                toon.setCogIndex(-1)
            except Exception:
                pass
            toon.wrtReparentTo(self.cutsceneElevator)
            point = ElevatorConstants.ElevatorPoints[index % len(ElevatorConstants.ElevatorPoints)]
            toon.setPos(*point)
            toon.setHpr(180, 0, 0)
            try:
                toon.loop('neutral')
            except Exception:
                pass

        camera.reparentTo(self.cutsceneElevator)
        camera.setPosHpr(0, 14, 4, 180, 0, 0)
        base.camLens.setMinFov(ToontownGlobals.CBElevatorFov / (4.0 / 3.0))

    def _stageToonsForRunToElevator(self):
        room = self.openingRoom

        for toon in self.toonsInElevator:
            if toon.isEmpty():
                continue
            toon.wrtReparentTo(room)
            try:
                toon.loop('neutral')
            except Exception:
                pass

    def _makeToonRunTrack(self):
        track = Parallel()
        room = self.openingRoom
        destination = self.exitElevatorOrigin
        center = (len(self.toonsInElevator) - 1) * 0.5

        for index, toon in enumerate(self.toonsInElevator):
            if toon.isEmpty():
                continue
            startPos = toon.getPos(room)
            endPos = room.getRelativePoint(
                destination,
                Point3((index - center) * 2.4, 0.0, 0.1))
            toonTrack = Sequence(
                Wait(index * 1.0),
                Parallel(
                    Func(toon.loop, 'run'),
                    LerpPosInterval(
                        toon,
                        5.0,
                        endPos,
                        other=room,
                        startPos=startPos)),
                Func(toon.loop, 'neutral'))
            track.append(toonTrack)

        return track

    def _makeCutsceneCameraTrack(self):
        return Sequence(
            Func(camera.wrtReparentTo, render),
            Func(
                base.camLens.setMinFov,
                ToontownGlobals.CBElevatorFov / (4.0 / 3.0)),
            LerpPosHprInterval(
                camera,
                3.0,
                Point3(0, 0, 70),
                Point3(0, -90, -90),
                blendType='easeInOut'))

    def _boardToonsInRunElevator(self):
        for index, toon in enumerate(self.toonsInElevator):
            if toon.isEmpty():
                continue
            toon.wrtReparentTo(self.runElevator)
            point = ElevatorConstants.ElevatorPoints[index % len(ElevatorConstants.ElevatorPoints)]
            toon.setPos(*point)
            toon.setHpr(180, 0, 0)
            try:
                toon.loop('neutral')
            except Exception:
                pass

    def _movePartyToElevator(self, elevator):
        for index, toon in enumerate(self.toonsInElevator):
            if toon.isEmpty():
                continue
            toon.wrtReparentTo(elevator)
            point = ElevatorConstants.ElevatorPoints[index % len(ElevatorConstants.ElevatorPoints)]
            toon.setPos(*point)
            toon.setHpr(180, 0, 0)
            try:
                toon.loop('neutral')
            except Exception:
                pass
        camera.wrtReparentTo(elevator)
        camera.setPosHpr(0, 14, 4, 180, 0, 0)

    def _stopTracks(self):
        for attr in ('cutsceneTrack', 'elevatorTrack'):
            track = getattr(self, attr, None)
            if track:
                try:
                    track.pause()
                except Exception:
                    pass
                setattr(self, attr, None)
        if self.openingMusic:
            try:
                self.openingMusic.stop()
            except Exception:
                pass
        for music in (self.elevatorMusic, self.corridorElevatorMusic):
            if music:
                try:
                    music.stop()
                except Exception:
                    pass

    def _startElevatorMusic(self):
        if self.elevatorMusic:
            base.playMusic(self.elevatorMusic, looping=1, volume=1.0)

    def _stopElevatorMusic(self):
        if self.elevatorMusic:
            self.elevatorMusic.stop()

    def _stopOpeningMusic(self):
        if self.openingMusic:
            self.openingMusic.stop()

    def _playElevatorDing(self):
        if self.dingSfx:
            base.playSfx(self.dingSfx)
        else:
            self.notify.warning('Elevator ding sound could not be loaded.')

    def _makeRunToElevatorTransitionTrack(self):
        soundDuration = self.dingSfx.length() if self.dingSfx else 0.5
        irisDuration = soundDuration / 1.5
        return Parallel(
            Sequence(
                Func(base.transitions.irisOut, irisDuration),
                Wait(irisDuration)),
            SoundInterval(self.dingSfx, render))

    def _showButNobodyCame(self):
        popup = WhisperPopup(
            'But nobody came.',
            OTPGlobals.getInterfaceFont(),
            WTSystem,
            timeout=7.0)
        popup.manage(base.marginManager)
        notificationSfx = getattr(base.localAvatar, 'soundSystemMessage', None)
        if notificationSfx is None:
            notificationSfx = self.notificationSfx
        if notificationSfx:
            base.playSfx(notificationSfx)
        else:
            self.notify.warning('System notification sound could not be loaded.')

    def _startOpeningMusic(self):
        if self.openingMusic:
            base.playMusic(self.openingMusic, looping=1, volume=0.9)
        else:
            self.notify.warning('Opening music FF_too_much.ogg could not be loaded.')

    def enterOpeningScene(self, requestStatus=None):
        if self.corridor:
            self.corridor.stash()
        if self.openingRoom:
            self.openingRoom.setColorScale(0.12, 0.12, 0.12, 1.0)
            self.openingRoom.unstash()
            self.openingRoom.show()
        if self.cutsceneElevator:
            self.cutsceneElevator.show()
        if self.runElevator:
            self.runElevator.show()

        self.cutsceneTrack = Sequence(
            Func(self._startElevatorMusic),
            Func(base.transitions.fadeIn, 0.8),
            ElevatorUtils.getRideElevatorInterval(ElevatorConstants.ELEVATOR_NORMAL),
            ElevatorUtils.getRideElevatorInterval(ElevatorConstants.ELEVATOR_NORMAL),
            Wait(2.0),
            Parallel(
                Func(self._stopElevatorMusic),
                Func(self._startOpeningMusic),
                ElevatorUtils.getOpenInterval(
                    self,
                    self.cutsceneLeftDoor,
                    self.cutsceneRightDoor,
                    self.openSfx,
                    self.finalOpenSfx,
                    ElevatorConstants.ELEVATOR_NORMAL)),
            Func(camera.wrtReparentTo, render),
            Wait(1.0),
            Func(self._showButNobodyCame),
            Wait(7.0),
            Func(self._stageToonsForRunToElevator),
            self._makeCutsceneCameraTrack(),
            self._makeToonRunTrack(),
            self._makeRunToElevatorTransitionTrack(),
            Func(self._stopOpeningMusic),
            Func(self.fsm.request, 'elevatorToCorridor'))
        self.cutsceneTrack.start()

    def exitOpeningScene(self):
        if self.cutsceneTrack:
            self.cutsceneTrack.pause()
            self.cutsceneTrack = None
        self._stopOpeningMusic()
        for toon in self.toonsInElevator:
            try:
                if toon.getParent() == self.cutsceneElevator or toon.getParent() == self.runElevator or toon.getParent() == self.openingRoom:
                    toon.wrtReparentTo(render)
            except Exception:
                pass
        if camera.getParent() == self.cutsceneElevator or camera.getParent() == self.runElevator or camera.getParent() == self.openingRoom:
            camera.wrtReparentTo(render)
        self._removeCutsceneElevator()

    def enterElevatorToCorridor(self):
        if self.openingRoom:
            self.openingRoom.stash()
        if self.corridor:
            self.corridor.unstash()
            self.corridor.show()
        self._movePartyToElevator(self.corridorElevator)
        if self.corridorElevatorMusic:
            base.playMusic(self.corridorElevatorMusic, looping=1, volume=1.0)

        ride = Sequence(
            Func(base.transitions.fadeIn, 0.8),
            ElevatorUtils.getRideElevatorInterval(ElevatorConstants.ELEVATOR_NORMAL),
            ElevatorUtils.getRideElevatorInterval(ElevatorConstants.ELEVATOR_NORMAL),
            ElevatorUtils.getOpenInterval(
                self,
                self.corridorLeftDoor,
                self.corridorRightDoor,
                self.openSfx,
                self.finalOpenSfx,
                ElevatorConstants.ELEVATOR_NORMAL
            ),
            Wait(0.75),
            Func(self.fsm.request, 'goldenCorridor')
        )
        self.elevatorTrack = ride
        ride.start()

    def exitElevatorToCorridor(self):
        if self.elevatorTrack:
            self.elevatorTrack.pause()
            self.elevatorTrack = None
        if self.corridorElevatorMusic:
            self.corridorElevatorMusic.stop()

    def enterGoldenCorridor(self):
        if self.corridor:
            self.corridor.unstash()
            self.corridor.show()

        spawn = self._corridorSpawn
        for index, toon in enumerate(self.toonsInElevator):
            if toon.isEmpty():
                continue
            x = ((index % 4) - 1.5) * 1.0
            y = 0.0
            z = 0.1
            toon.wrtReparentTo(render)
            if spawn:
                toon.setPos(spawn, x, y, z)
                toon.setHpr(spawn, 180, 0, 0)
            else:
                toon.setPos(self.corridorElevator, x, -8.0, z)
                toon.setHpr(self.corridorElevator, 180, 0, 0)
            try:
                toon.b_setAnimState('neutral', 1)
            except Exception:
                pass

        camera.wrtReparentTo(render)
        if self.previousFov is not None:
            base.camLens.setMinFov(self.previousFov)
            self.previousFov = None
        self.toonsInElevator = []
        NametagGlobals.setWant2dNametags(True)
        NametagGlobals.setWantActiveNametags(True)
        base.localAvatar.setTeleportAvailable(1)
        try:
            base.transitions.fadeIn(0.5)
        except Exception:
            pass
        self.fsm.request('walk')

    def exitGoldenCorridor(self):
        pass

    def _detachToonsAndCamera(self):
        for toon in self.toonsInElevator:
            try:
                if toon.getParent() == self.cutsceneElevator or toon.getParent() == self.runElevator or toon.getParent() == self.corridorElevator or toon.getParent() == self.openingRoom:
                    toon.wrtReparentTo(render)
            except Exception:
                pass
        if camera.getParent() == self.cutsceneElevator or camera.getParent() == self.runElevator or camera.getParent() == self.corridorElevator or camera.getParent() == self.openingRoom:
            camera.wrtReparentTo(render)
        self.toonsInElevator = []

    def _removeCutsceneElevator(self):
        if self.cutsceneElevator and not self.cutsceneElevator.isEmpty():
            self.cutsceneElevator.removeNode()
        if self.runElevator and not self.runElevator.isEmpty():
            self.runElevator.removeNode()
        if self.openingRoom and not self.openingRoom.isEmpty():
            self.openingRoom.removeNode()
        self.cutsceneElevator = None
        self.runElevator = None
        self.runLeftDoor = None
        self.runRightDoor = None
        self.cutsceneLeftDoor = None
        self.cutsceneRightDoor = None
        self.openingRoom = None
        self.elevatorOrigin = None
        self.exitElevatorOrigin = None

    def _removeCorridorElevator(self):
        if self.corridorElevator and not self.corridorElevator.isEmpty():
            self.corridorElevator.removeNode()
        self.corridorElevator = None
        self.corridorElevatorMusic = None
        self.corridorLeftDoor = None
        self.corridorRightDoor = None

    def enterWalk(self, teleportIn=0):
        BattlePlace.BattlePlace.enterWalk(self, teleportIn)
        base.localAvatar.setTeleportAvailable(1)

    def enterTeleportOut(self, requestStatus):
        BattlePlace.BattlePlace.enterTeleportOut(self, requestStatus, self._teleportOutDone)

    def _teleportOutDone(self, requestStatus):
        self.doneStatus = requestStatus
        messenger.send(self.doneEvent)

    def exitTeleportOut(self):
        BattlePlace.BattlePlace.exitTeleportOut(self)
