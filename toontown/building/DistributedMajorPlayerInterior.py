from toontown.toonbase.ToonBaseGlobal import *
from panda3d.core import *
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from toontown.toonbase import ToontownGlobals
from DistributedToonInterior import DistributedToonInterior
import ToonInteriorColors
import random
from toontown.hood import ZoneUtil
from toontown.battle import BattleParticles
from toontown.dna.DNAParser import DNADoor

class DistributedMajorPlayerInterior(DistributedToonInterior):

    def __init__(self, cr):
        DistributedToonInterior.__init__(self, cr)
        self.majorPlayerMusic = None
        self.majorPlayerMusicFile = None
        self.majorPlayerMusicTaskName = 'majorPlayerLobbyMusic-%s' % id(self)
        self.sigilSpinIntervals = {}
        self.sigilReturnIntervals = {}
        self.sigilIdleGlowIntervals = {}
        self.sigilBases = {}
        self.sigilTriggerNodes = []
        self.sigilIdleEffects = {}
        self.trackTextureInterval = None
        self.boardingTriggerNode = None
        self.boardingTriggerName = None
        self.localBoardingRequested = False
        self.localBoardedSlot = None
        self.boardedAvIds = {}
        self.boardingToonTracks = {}
        self.boardingState = 'open'
        self.boardingCountdownTaskName = 'majorPlayerBoardingCountdown-%s' % id(self)
        self.boardingCountdownNode = None
        self.boardingCountdownText = None
        self.localToonOnBoard = 0
        self.elevatorFSM = None
        self.antiShuffle = 0

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)

        interior = self.randomDNAItem('TI_dave', self.dnaStore.findNode)
        self.interior = interior.copyTo(render)

        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)

        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'

        door = self.dnaStore.findNode(doorModelName)

        originalDoorOrigin = self.interior.find('**/door_origin;+s')
        originalDoorTransform = originalDoorOrigin.getTransform(self.interior)
        originalDoorOrigin.setName('original_door_origin')

        visualDoorRoot = self.interior.attachNewNode('major_player_visual_door_root')
        visualDoorRoot.setPos(self.interior, -1.2, 0.152, 0.02)
        visualDoorRoot.setHpr(self.interior, 180, 0, 0)
        visualDoorRoot.setScale(0.8, 0.8, 0.8)

        visualDoorOrigin = visualDoorRoot.attachNewNode('major_player_visual_door_origin')
        doorNP = door.copyTo(visualDoorOrigin)

        color = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(
            doorNP,
            visualDoorRoot,
            visualDoorOrigin,
            self.dnaStore,
            str(self.block),
            color
        )

        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(visualDoorRoot)
        doorFrame.setColor(color)

        elevator = loader.loadModel('phase_11/models/lawbotHQ/lawbotElevator.bam')
        elevatorOrigin = self.interior.find('**/elevator_origin')
        elevator.reparentTo(elevatorOrigin)

        self.sigils = []
        self.sigilRoot = loader.loadModel('phase_4/models/modules/ttcc_gen_sigil.bam')
        self.sigilRoot.reparentTo(elevatorOrigin)
        self.sigilRoot.setName('major_player_sigils')
        self.sigilRoot.setPos(1.5, -70.75, -15.97)
        self.sigilRoot.setHpr(0, 0, 0)
        self.sigils.append(self.sigilRoot)

        track = self.sigilRoot.find('**/Track')
        if not track.isEmpty():
            for texture in track.findAllTextures():
                texture.setWrapU(Texture.WMRepeat)
                texture.setWrapV(Texture.WMRepeat)

            self.trackTextureInterval = LerpTexOffsetInterval(
                track,
                0.5,
                Vec2(0.0, 1.0),
                startTexOffset=Vec2(0.0, 0.0),
                textureStage=TextureStage.getDefault()
            )
            self.trackTextureInterval.loop()

        for index in range(1, 5):
            sigilBase = self.sigilRoot.find('**/SigilBase%s' % index)

            if sigilBase.isEmpty():
                continue

            self.sigilBases[index] = sigilBase
            self.__startIdleGlow(index)

        self.boardingTriggerName = self.uniqueName('majorPlayerBoardingTrigger')
        boardingCollisionNode = CollisionNode(self.boardingTriggerName)
        boardingCollisionSphere = CollisionSphere(0, 0, 0.8, 6.5)
        boardingCollisionSphere.setTangible(False)
        boardingCollisionNode.addSolid(boardingCollisionSphere)
        boardingCollisionNode.setFromCollideMask(BitMask32.allOff())
        boardingCollisionNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.boardingTriggerNode = self.sigilRoot.attachNewNode(boardingCollisionNode)

        self.accept(
            'enter' + self.boardingTriggerName,
            self.__enterBoardingArea
        )
        self.accept(
            'exit' + self.boardingTriggerName,
            self.__exitBoardingArea
        )
        self.accept('elevatorExitButton', self.__handleElevatorExitButton)

        del self.colors
        del self.dnaStore
        del self.randomGenerator

        spawnDoorOrigin = self.interior.attachNewNode('door_origin')
        spawnDoorOrigin.setTransform(self.interior, originalDoorTransform)
        spawnDoorOrigin.setH(spawnDoorOrigin, 180)
        spawnDoorOrigin.setY(spawnDoorOrigin, 0.5)

        taskMgr.doMethodLater(
            0.1,
            self.__startMajorPlayerMusic,
            self.majorPlayerMusicTaskName
        )

    def __enterBoardingArea(self, collisionEntry):
        if self.localBoardingRequested or self.localBoardedSlot is not None:
            return

        if not base.localAvatar or base.localAvatar.getHp() <= 0:
            return

        place = base.cr.playGame.getPlace()
        if place:
            place.detectedElevatorCollision(self)

        self.localBoardingRequested = True
        self.sendUpdate('requestBoard', [])

    def __handleElevatorExitButton(self):
        if self.localBoardedSlot is None:
            return

        self.sendUpdate('requestExit', [])

    def __exitBoardingArea(self, collisionEntry):
        if self.localBoardedSlot is not None:
            return

        if self.localBoardingRequested:
            self.localBoardingRequested = False
            self.sendUpdate('requestExit', [])

    def setBoardingState(self, state, timestamp=0):
        self.boardingState = state

        if state == 'countdown':
            self.__startBoardingCountdown(5.0)
        elif state == 'ready':
            self.__startBoardingCountdown(5.0)
        elif state == 'open':
            self.__stopBoardingCountdown()

    def __startBoardingCountdown(self, duration):
        self.__stopBoardingCountdown()

        self.boardingCountdownText = TextNode('majorPlayerBoardingCountdown')
        self.boardingCountdownText.setFont(ToontownGlobals.getSignFont())
        self.boardingCountdownText.setAlign(TextNode.ACenter)
        self.boardingCountdownText.setTextColor(1.0, 1.0, 1.0, 1.0)
        self.boardingCountdownText.setText(str(int(duration)))

        self.boardingCountdownNode = self.sigilRoot.attachNewNode(
            self.boardingCountdownText
        )
        self.boardingCountdownNode.setPos(0, 0, 8.0)
        self.boardingCountdownNode.setScale(1.5)
        self.boardingCountdownNode.setBillboardPointEye()

        task = taskMgr.add(
            self.__boardingCountdownTask,
            self.boardingCountdownTaskName
        )
        task.duration = duration

    def __boardingCountdownTask(self, task):
        remaining = int(max(0, task.duration - task.time) + 0.999)

        if self.boardingCountdownText:
            self.boardingCountdownText.setText(str(remaining))

        if task.time >= task.duration:
            self.__finishBoardingCountdown()
            return Task.done

        return Task.cont

    def __finishBoardingCountdown(self):
        self.__stopBoardingCountdown()
        self.__beginMajorPlayerTeleport()

    def __stopBoardingCountdown(self):
        taskMgr.remove(self.boardingCountdownTaskName)

        if self.boardingCountdownNode:
            self.boardingCountdownNode.removeNode()
            self.boardingCountdownNode = None

        self.boardingCountdownText = None

    def __beginMajorPlayerTeleport(self):
        pass

    def rejectBoard(self, avId, reason=0):
        if avId == base.localAvatar.doId:
            self.localBoardingRequested = False
            self.localBoardedSlot = None
            self.localToonOnBoard = 0
            elevator = self.getPlaceElevator()
            if elevator:
                elevator.signalDone({'where': 'reject'})
    
    def fillSlot0(self, avId, wantBoardingShow=0):
        self.__fillBoardingSlot(0, avId)

    def fillSlot1(self, avId, wantBoardingShow=0):
        self.__fillBoardingSlot(1, avId)

    def fillSlot2(self, avId, wantBoardingShow=0):
        self.__fillBoardingSlot(2, avId)

    def fillSlot3(self, avId, wantBoardingShow=0):
        self.__fillBoardingSlot(3, avId)

    def emptySlot0(self, avId, bailFlag=0, timestamp=0, timeSent=0):
        self.__emptyBoardingSlot(0, avId)

    def emptySlot1(self, avId, bailFlag=0, timestamp=0, timeSent=0):
        self.__emptyBoardingSlot(1, avId)

    def emptySlot2(self, avId, bailFlag=0, timestamp=0, timeSent=0):
        self.__emptyBoardingSlot(2, avId)

    def emptySlot3(self, avId, bailFlag=0, timestamp=0, timeSent=0):
        self.__emptyBoardingSlot(3, avId)

    def __fillBoardingSlot(self, slotIndex, avId):
        if avId == 0:
            self.__emptyBoardingSlot(slotIndex, 0)
            return

        toon = self.cr.doId2do.get(avId)
        sigilBase = self.sigilBases.get(slotIndex + 1)

        if not toon or not sigilBase:
            return

        oldAvId = self.boardedAvIds.get(slotIndex)
        if oldAvId and oldAvId != avId:
            self.__emptyBoardingSlot(slotIndex, oldAvId)

        self.boardedAvIds[slotIndex] = avId

        if avId == base.localAvatar.doId:
            self.localBoardingRequested = False
            self.localBoardedSlot = slotIndex
            self.localToonOnBoard = 1
            place = base.cr.playGame.getPlace()
            if place:
                place.detectedElevatorCollision(self)
            try:
                base.localAvatar.disableAvatarControls()
            except:
                pass

        oldTrack = self.boardingToonTracks.pop(avId, None)
        if oldTrack:
            oldTrack.pause()

        toon.stopSmooth()
        targetPos = sigilBase.getPos(self.sigilRoot)
        targetHpr = toon.getHpr(self.sigilRoot)

        track = Sequence(
            Func(toon.setAnimState, 'run', 1.0),
            LerpPosInterval(
                toon,
                0.75,
                targetPos,
                other=self.sigilRoot,
                blendType='easeInOut'
            ),
            LerpHprInterval(
                toon,
                0.25,
                targetHpr,
                other=self.sigilRoot,
                blendType='easeInOut'
            ),
            Func(toon.setAnimState, 'neutral', 1.0)
        )
        if avId == base.localAvatar.doId:
            elevator = self.getPlaceElevator()
            if elevator:
                cameraTrack = Sequence(
                    Func(
                        elevator.fsm.request,
                        'boarding',
                        [self.getElevatorModel()]
                    ),
                    Func(elevator.fsm.request, 'boarded')
                )
                track = Parallel(track, cameraTrack)

        self.boardingToonTracks[avId] = track
        track.start()

        self.__enterSigil(slotIndex + 1, sigilBase, None)

    def __emptyBoardingSlot(self, slotIndex, avId):
        currentAvId = self.boardedAvIds.get(slotIndex)

        if avId == 0:
            avId = currentAvId

        if currentAvId is not None:
            del self.boardedAvIds[slotIndex]

        if avId is None:
            return

        oldTrack = self.boardingToonTracks.pop(avId, None)
        if oldTrack:
            oldTrack.pause()

        toon = self.cr.doId2do.get(avId)

        if avId == base.localAvatar.doId:
            self.localBoardingRequested = False
            self.localBoardedSlot = None
            self.localToonOnBoard = 0

            sigilBase = self.sigilBases.get(slotIndex + 1)
            if toon and sigilBase:
                startPos = toon.getPos(self.sigilRoot)
                exitPos = Point3(
                    startPos.getX(),
                    startPos.getY() - 2.5,
                    startPos.getZ()
                )

                exitTrack = Sequence(
                    Func(toon.setAnimState, 'run', 1.0),
                    LerpPosInterval(
                        toon,
                        0.75,
                        exitPos,
                        other=self.sigilRoot,
                        blendType='easeInOut'
                    ),
                    Func(toon.setAnimState, 'neutral', 1.0),
                    Func(self.__finishLocalHopOff)
                )
                self.boardingToonTracks[avId] = exitTrack
                exitTrack.start()
            else:
                self.__finishLocalHopOff()
        elif toon:
            toon.startSmooth()

        self.__exitSigil(slotIndex + 1, None)

    def __finishLocalHopOff(self):
        avId = base.localAvatar.doId
        oldTrack = self.boardingToonTracks.pop(avId, None)
        if oldTrack:
            oldTrack.pause()

        try:
            base.localAvatar.setAnimState('neutral', 1.0)
        except:
            pass

        try:
            camera.wrtReparentTo(render)
        except:
            pass

        try:
            base.localAvatar.attachCamera()
        except:
            pass

        try:
            base.localAvatar.startUpdateSmartCamera()
        except:
            pass

        elevator = self.getPlaceElevator()
        if elevator:
            try:
                elevator.fsm.request('exiting')
            except:
                pass
            elevator.signalDone({'where': 'exit'})

        place = base.cr.playGame.getPlace()
        if place and place.fsm.getCurrentState().getName() != 'walk':
            try:
                place.fsm.request('walk')
            except:
                pass

        try:
            base.localAvatar.enableAvatarControls()
        except:
            pass

        try:
            base.localAvatar.setAnimState('neutral', 1.0)
        except:
            pass

    def getElevatorModel(self):
        return self.sigilRoot

    def getPlaceElevator(self):
        place = base.cr.playGame.getPlace()
        if place and hasattr(place, 'elevator'):
            return place.elevator
        return None

    def getDestName(self):
        return None

    def getElevatorTripId(self):
        return 0

    def getAntiShuffle(self):
        return 0

    def getMinLaff(self):
        return 0

    def __enterSigil(self, index, sigilBase, collisionEntry):
        returnInterval = self.sigilReturnIntervals.pop(index, None)
        if returnInterval:
            returnInterval.pause()

        if index in self.sigilSpinIntervals:
            return

        self.__stopIdleGlow(index)

        sigilBase.setColorScale(0.47, 0.49, 0.50, 1.0)

        belt = self.sigilRoot.find('**/Belt%s' % index)
        if belt.isEmpty():
            belt = self.sigilRoot.find('**/Ring%s' % index)
        targetNode = belt if not belt.isEmpty() else sigilBase

        startHpr = targetNode.getHpr()
        spinInterval = targetNode.hprInterval(
            3.0,
            VBase3(startHpr.getX() - 360, startHpr.getY(), startHpr.getZ()),
            startHpr=startHpr
        )
        spinInterval.loop()
        self.sigilSpinIntervals[index] = spinInterval

    def __exitSigil(self, index, collisionEntry):
        spinInterval = self.sigilSpinIntervals.pop(index, None)
        sigilBase = self.sigilBases.get(index)

        if spinInterval:
            spinInterval.pause()

        if sigilBase:
            currentH = sigilBase.getH()
            targetH = currentH - (currentH % 360.0)

            if targetH >= currentH:
                targetH -= 360.0

            returnInterval = sigilBase.hprInterval(
                0.75,
                VBase3(targetH, 0, 0),
                startHpr=VBase3(currentH, 0, 0),
                blendType='easeInOut'
            )
            returnInterval.setDoneEvent(self.uniqueName('sigilReturnDone%s' % index))
            self.acceptOnce(
                self.uniqueName('sigilReturnDone%s' % index),
                self.__finishSigilReturn,
                [index, sigilBase]
            )
            self.sigilReturnIntervals[index] = returnInterval
            returnInterval.start()

    def __finishSigilReturn(self, index, sigilBase):
        self.sigilReturnIntervals.pop(index, None)
        sigilBase.setH(0)
        self.__startIdleGlow(index)

    def __startIdleGlow(self, index):
        if index in self.sigilIdleGlowIntervals:
            return

        sigilBase = self.sigilBases.get(index)
        if not sigilBase:
            return

        brightColor = Vec4(0.294, 0.416, 0.431, 1.0)
        dimColor = Vec4(0.15, 0.22, 0.23, 1.0)

        sigilBase.setColorScale(dimColor)

        if index not in self.sigilIdleEffects:
            light = self.sigilRoot.find('**/Light%s' % index)
            if not light.isEmpty():
                effect = BattleParticles.createParticleEffect(file='uniteCooldown')
                particles = effect.getParticlesNamed('particles-1')
                particles.factory.setLifespanBase(1.8)
                particles.factory.setLifespanSpread(0.35)
                particles.renderer.setCenterColor(Vec4(1.0, 1.0, 1.0, 1.0))
                particles.renderer.setEdgeColor(Vec4(0.92, 0.94, 1.0, 1.0))
                effect.reparentTo(light)
                floorPos = light.getRelativePoint(sigilBase, Point3(0, 0, -0.95))
                effect.setPos(floorPos)
                effect.setHpr(0, 180, 0)
                effect.setScale(0.85, 0.85, 2.0)
                effect.start()
                self.sigilIdleEffects[index] = effect

        glowInterval = Sequence(
            LerpColorScaleInterval(
                sigilBase,
                1.5,
                brightColor,
                startColorScale=dimColor,
                blendType='easeInOut'
            ),
            LerpColorScaleInterval(
                sigilBase,
                1.5,
                dimColor,
                startColorScale=brightColor,
                blendType='easeInOut'
            )
        )
        glowInterval.loop()
        self.sigilIdleGlowIntervals[index] = glowInterval

    def __stopIdleGlow(self, index):
        glowInterval = self.sigilIdleGlowIntervals.pop(index, None)
        if glowInterval:
            glowInterval.finish()

        effect = self.sigilIdleEffects.pop(index, None)
        if effect:
            try:
                effect.softStop()
            except:
                pass
            try:
                effect.cleanup()
            except:
                pass

    def __startMajorPlayerMusic(self, task):
        base.musicManager.stopAllSounds()
        self.majorPlayerMusicFile = loader.loadMusic(
            'phase_12/audio/bgm/merc/instance_majorplayer_lobby.ogg'
        )
        self.majorPlayerMusic = base.playMusic(
            self.majorPlayerMusicFile,
            looping=1
        )
        return task.done

    def __stopMajorPlayerMusic(self):
        taskMgr.remove(self.majorPlayerMusicTaskName)
        base.musicManager.stopAllSounds()

        if self.majorPlayerMusic:
            try:
                self.majorPlayerMusic.stop()
            except:
                pass
            self.majorPlayerMusic = None

        if self.majorPlayerMusicFile:
            try:
                self.majorPlayerMusicFile.stop()
            except:
                pass
            self.majorPlayerMusicFile = None

    def disable(self):
        self.__stopMajorPlayerMusic()
        self.__stopBoardingCountdown()

        if self.trackTextureInterval:
            self.trackTextureInterval.finish()
            self.trackTextureInterval = None

        for index, spinInterval in self.sigilSpinIntervals.items():
            if spinInterval:
                spinInterval.finish()
        self.sigilSpinIntervals = {}

        for index, returnInterval in self.sigilReturnIntervals.items():
            if returnInterval:
                returnInterval.finish()
        self.sigilReturnIntervals = {}

        for index, glowInterval in self.sigilIdleGlowIntervals.items():
            if glowInterval:
                glowInterval.finish()
        self.sigilIdleGlowIntervals = {}

        for effect in self.sigilIdleEffects.values():
            if effect:
                try:
                    effect.softStop()
                except:
                    pass
                try:
                    effect.cleanup()
                except:
                    pass
        self.sigilIdleEffects = {}

        for avId, track in self.boardingToonTracks.items():
            if track:
                track.pause()
        self.boardingToonTracks = {}
        self.boardedAvIds = {}
        self.localBoardingRequested = False
        self.localBoardedSlot = None
        self.localToonOnBoard = 0

        try:
            base.localAvatar.enableAvatarControls()
        except:
            pass

        self.ignore('elevatorExitButton')

        if self.boardingTriggerName:
            self.ignore('enter' + self.boardingTriggerName)
            self.ignore('exit' + self.boardingTriggerName)

        if self.boardingTriggerNode and not self.boardingTriggerNode.isEmpty():
            self.boardingTriggerNode.removeNode()
        self.boardingTriggerNode = None
        self.boardingTriggerName = None

        self.sigilBases = {}

        for triggerNode in self.sigilTriggerNodes:
            if triggerNode and not triggerNode.isEmpty():
                self.ignore('enter' + triggerNode.node().getName())
                self.ignore('exit' + triggerNode.node().getName())
                triggerNode.removeNode()
        self.sigilTriggerNodes = []

        if hasattr(self, 'sigils'):
            for sigil in self.sigils:
                if sigil and not sigil.isEmpty():
                    sigil.removeNode()
            self.sigils = []

        self.enterOff()
        DistributedToonInterior.disable(self)

    def delete(self):
        self.__stopMajorPlayerMusic()
        DistributedToonInterior.delete(self)
