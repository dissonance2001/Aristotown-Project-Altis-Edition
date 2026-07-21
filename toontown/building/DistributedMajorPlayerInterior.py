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

            triggerName = self.uniqueName('majorPlayerSigilTrigger%s' % index)
            collisionNode = CollisionNode(triggerName)
            collisionSphere = CollisionSphere(0, 0, 0.6, 1.15)
            collisionSphere.setTangible(False)
            collisionNode.addSolid(collisionSphere)
            collisionNode.setFromCollideMask(BitMask32.allOff())
            collisionNode.setIntoCollideMask(ToontownGlobals.WallBitmask)

            triggerNode = sigilBase.attachNewNode(collisionNode)
            self.sigilTriggerNodes.append(triggerNode)

            self.accept(
                'enter' + triggerName,
                self.__enterSigil,
                [index, sigilBase]
            )
            self.accept(
                'exit' + triggerName,
                self.__exitSigil,
                [index]
            )

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

        if self.trackSpinInterval:
            self.trackSpinInterval.finish()
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
