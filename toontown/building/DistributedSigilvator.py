import random
import time

from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.task.Task import Task
from direct.directnotify import DirectNotifyGlobal
from toontown.building import DistributedElevator
from toontown.building import DistributedElevatorExt
from toontown.building.ElevatorConstants import *
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.battle import BattleParticles


class DistributedSigilvator(DistributedElevatorExt.DistributedElevatorExt):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSigilvator')
    JumpOutOffsets = SigilJumpOutOffsets
    JumpOutAnim = 'walk'
    ExitTime = TOON_EXIT_SIGIL_TIME
    BoardH = 0
    BaseTrackSpin = 0.9
    TrackSpinPerToon = 0.9
    ToonsEnteringTrackSpin = 6.7
    TrackSpinTaskName = 'sigilvator-track-spin-task'
    OriginName = 'major_player_sigilvator_origin'

    def __init__(self, cr):
        DistributedElevatorExt.DistributedElevatorExt.__init__(self, cr)
        self.type = ELEVATOR_SIGIL
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.elevatorPoints = SigilvatorPoints
        self.elevatorModel = loader.loadModel(
            'phase_4/models/modules/ttcc_gen_sigil.bam')
        self.leftDoor = None
        self.rightDoor = None
        self.irisTrack = None
        self.occupiedSigils = []
        self.sigils = []
        self.lights = []
        self.lightSeqs = []
        self.sigilGlowSeqs = []
        self.sigilRotationSeqs = []
        self.sigilParticles = []
        self.track = self.elevatorModel.find('**/Track')
        self.trackSpinIntensity = self.BaseTrackSpin
        self.trackCurrUv = 0.0
        self.lastSpinTime = time.time()
        self.updateSpinIntensitySeq = None
        self._setupVisuals()

    def _configureSurfaceNode(self, node, sortOrder):
        if node is None or node.isEmpty():
            return

        # Altis renders the lobby floor after Clash's custom ``ground`` bin.
        # That made every flat sigil surface disappear beneath the wood even
        # though the lights and particles were still visible.  Put the flat
        # surfaces in Panda's normal transparent bin so the floor is drawn
        # first, while keeping depth testing against walls and Toons.
        node.show()
        node.setTwoSided(1)
        node.setTransparency(TransparencyAttrib.MAlpha)
        node.setBin('transparent', sortOrder)
        node.setDepthTest(1)
        node.setDepthWrite(0)
        try:
            node.setDepthOffset(1)
        except:
            pass

    def _setupVisuals(self):
        BattleParticles.loadParticles()

        # Do not use Clash's custom ``ground`` bin in Altis.  In this older
        # renderer that bin is sorted underneath the Toon Hall wooden floor,
        # which leaves only the light columns and particles visible.
        self._configureSurfaceNode(self.track, 10)
        if not self.track.isEmpty():
            for texture in self.track.findAllTextures():
                texture.setWrapU(Texture.WMRepeat)
                texture.setWrapV(Texture.WMRepeat)

        shadowBase = self.elevatorModel.find('**/DropShadow')
        if not shadowBase.isEmpty():
            shadowBase.show()
            shadowBase.setBin('shadow', -5)
            shadowBase.setDepthWrite(0)

        for i in range(4):
            sigil = self.elevatorModel.find('**/SigilBase%s' % (i + 1))
            sigilTop = self.elevatorModel.find('**/SigilTop%s' % (i + 1))
            light = self.elevatorModel.find('**/Light%s' % (i + 1))

            self._configureSurfaceNode(sigil, 20 + i)
            self._configureSurfaceNode(sigilTop, 30 + i)

            if not sigil.isEmpty() and not shadowBase.isEmpty():
                shadowCopy = shadowBase.copyTo(sigil)
                shadowCopy.setBin('shadow', -5)
                shadowCopy.setDepthWrite(0)

            self.sigils.append(sigil)
            self.lights.append(light)
            self.lightSeqs.append(None)
            self.sigilRotationSeqs.append(None)

            particles = None
            if not sigil.isEmpty():
                try:
                    particles = BattleParticles.createParticleEffect(
                        file='sigilSparkle')
                    particles.start(parent=sigil, renderParent=render)
                except Exception as error:
                    self.notify.warning(
                        'Unable to start sigilSparkle particles: %s' % error)
            self.sigilParticles.append(particles)

            sigilSeq = self.getSigilSeq(sigil)
            if sigilSeq:
                sigilSeq.loop()
                sigilSeq.setT(random.random() * sigilSeq.getDuration())
            self.sigilGlowSeqs.append(sigilSeq)

        if not shadowBase.isEmpty():
            shadowBase.removeNode()

    def announceGenerate(self):
        DistributedElevatorExt.DistributedElevatorExt.announceGenerate(self)
        self.lastSpinTime = time.time()
        taskMgr.add(self.updateTrackUv,
                    self.uniqueName(self.TrackSpinTaskName))

    def gotBldg(self, buildingList):
        # This object is attached to a Toon interior, not a suit building.
        # Bypass DistributedElevatorExt.gotBldg(), which expects suit-door
        # and floor-indicator methods that Major Player interiors do not have.
        return DistributedElevator.DistributedElevator.gotBldg(
            self, buildingList)

    def setupElevator(self, task=None):
        origin = render.find('**/%s' % self.OriginName)
        if origin.isEmpty():
            taskMgr.remove(self.uniqueName('setupSigilvatorDelay'))
            taskMgr.doMethodLater(0.1, self.setupElevator,
                                  self.uniqueName('setupSigilvatorDelay'))
            return Task.done

        taskMgr.remove(self.uniqueName('setupSigilvatorDelay'))
        self.elevatorModel.reparentTo(origin)
        # Keep Clash's original local placement.  Surface render ordering is
        # handled in _configureSurfaceNode without lifting boarded Toons.
        self.elevatorModel.setPos(0, 0, 0)
        self.elevatorModel.setHpr(0, 0, 0)

        collisionRadius = ElevatorData[self.type]['collRadius']
        self.elevatorSphere = CollisionTube(
            4, 0, 0, -4, 0, 0, collisionRadius)
        self.elevatorSphere.setTangible(0)
        self.elevatorSphereNode = CollisionNode(
            self.uniqueName('elevatorSphere'))
        self.elevatorSphereNode.setIntoCollideMask(
            ToontownGlobals.WallBitmask)
        self.elevatorSphereNode.addSolid(self.elevatorSphere)
        self.elevatorSphereNodePath = self.elevatorModel.attachNewNode(
            self.elevatorSphereNode)
        self.elevatorSphereNodePath.stash()

        self.boardedAvIds = {}
        self.openDoors = Sequence()
        self.closeDoors = Sequence(
            self.getPortInterval(), Func(self.onDoorCloseFinish))
        self.finishSetup()
        return Task.done

    @staticmethod
    def getSigilSeq(sigil):
        if sigil.isEmpty():
            return None
        return Sequence(
            LerpColorScaleInterval(
                sigil, 1.5, (0.6, 0.88, 1.0, 1.0),
                blendType='easeIn'),
            LerpColorScaleInterval(
                sigil, 1.5, (1.0, 1.0, 1.0, 1.0),
                blendType='easeOut'))

    def updateTrackUv(self, task):
        if self.track is None or self.track.isEmpty():
            return Task.cont
        now = time.time()
        timeDiff = now - self.lastSpinTime
        self.trackCurrUv += self.trackSpinIntensity * timeDiff
        self.trackCurrUv %= 1.0
        self.track.setTexOffset(
            TextureStage.getDefault(), 0, self.trackCurrUv)
        self.lastSpinTime = now
        return Task.cont

    def setSpinIntensity(self, value):
        self.trackSpinIntensity = value

    def calculateNewSpinIntensity(self):
        return self.BaseTrackSpin + (
            self.TrackSpinPerToon * self.countFullSeats())

    def _updateTrackIntensity(self, target, duration=2.0):
        if self.updateSpinIntensitySeq:
            self.updateSpinIntensitySeq.pause()
        self.updateSpinIntensitySeq = LerpFunctionInterval(
            self.setSpinIntensity, duration=duration,
            fromData=self.trackSpinIntensity, toData=target,
            blendType='easeIn')
        self.updateSpinIntensitySeq.start()

    def setSigilOccupied(self, index):
        if index < 0 or index >= len(self.sigils):
            self.notify.warning('Got improper sigil index: %s.' % index)
            return
        if index not in self.occupiedSigils:
            self.occupiedSigils.append(index)
        self._updateTrackIntensity(self.calculateNewSpinIntensity())

        light = self.lights[index]
        if not light.isEmpty():
            if self.lightSeqs[index]:
                self.lightSeqs[index].pause()
            seq = LerpColorScaleInterval(
                light, 1.0, (1.0, 1.0, 1.0, 0.0),
                blendType='easeIn')
            seq.start()
            self.lightSeqs[index] = seq

        sigil = self.sigils[index]
        if sigil.isEmpty():
            return
        if self.sigilRotationSeqs[index]:
            self.sigilRotationSeqs[index].pause()

        def startSigilLoop(sigilIndex=index):
            if self.sigilRotationSeqs[sigilIndex]:
                self.sigilRotationSeqs[sigilIndex].pause()
            self.sigils[sigilIndex].setH(0)
            rotateLoop = Sequence(
                LerpHprInterval(
                    self.sigils[sigilIndex], 2.5, (-360, 0, 0)),
                Func(self.sigils[sigilIndex].setH, 0))
            rotateLoop.loop()
            self.sigilRotationSeqs[sigilIndex] = rotateLoop

        seq = Sequence(
            LerpHprInterval(
                sigil, 4.0, (-360, 0, 0), blendType='easeIn'),
            Func(startSigilLoop, index))
        seq.start()
        self.sigilRotationSeqs[index] = seq

        if self.sigilGlowSeqs[index]:
            self.sigilGlowSeqs[index].pause()
        glowStop = LerpColorScaleInterval(
            sigil, 1.0, (1, 1, 1, 1), blendType='easeIn')
        glowStop.start()
        self.sigilGlowSeqs[index] = glowStop

        particles = self.sigilParticles[index]
        if particles:
            try:
                particles.softStop()
            except:
                pass

    def setSigilUnoccupied(self, index):
        if index < 0 or index >= len(self.sigils):
            self.notify.warning('Got improper sigil index: %s.' % index)
            return
        if index in self.occupiedSigils:
            self.occupiedSigils.remove(index)
        self._updateTrackIntensity(self.calculateNewSpinIntensity())

        light = self.lights[index]
        if not light.isEmpty():
            if self.lightSeqs[index]:
                self.lightSeqs[index].pause()
            seq = LerpColorScaleInterval(
                light, 1.0, (1.0, 1.0, 1.0, 1.0),
                blendType='easeIn')
            seq.start()
            self.lightSeqs[index] = seq

        sigil = self.sigils[index]
        if sigil.isEmpty():
            return
        if self.sigilRotationSeqs[index]:
            self.sigilRotationSeqs[index].pause()
        if sigil.getH() <= -180:
            sigil.setH(sigil.getH() + 360)
        returnSeq = Sequence(
            LerpHprInterval(
                sigil, 1.0, (0, 0, 0), blendType='easeIn'))
        returnSeq.start()
        self.sigilRotationSeqs[index] = returnSeq

        if self.sigilGlowSeqs[index]:
            self.sigilGlowSeqs[index].pause()
        glowSeq = self.getSigilSeq(sigil)
        if glowSeq:
            glowSeq.loop()
        self.sigilGlowSeqs[index] = glowSeq

        particles = self.sigilParticles[index]
        if particles:
            try:
                particles.softStart()
            except:
                pass

    def addToonToSlot(self, avId, index):
        self.boardedAvIds[avId] = index
        self.setSigilOccupied(index)

    def clearToonFromSlot(self, avId, index):
        if avId in self.boardedAvIds:
            del self.boardedAvIds[avId]
        self.setSigilUnoccupied(index)

    def getIndexToAvIdDict(self):
        result = {}
        for avId, index in list(self.boardedAvIds.items()):
            result[index] = avId
        return result

    def getPortInterval(self):
        teleportTrack = Parallel()
        for avId in list(self.boardedAvIds.keys()):
            toon = base.cr.doId2do.get(avId)
            if toon:
                teleportTrack.append(toon.getTeleportOutTrack(False))
        return teleportTrack

    def onDoorCloseFinish(self):
        for avId in list(self.boardedAvIds.keys()):
            av = self.cr.doId2do.get(avId)
            if av is not None and av.getParent().compareTo(
                    self.elevatorModel) == 0:
                av.detachNode()
        self.boardedAvIds = {}
        for index in self.occupiedSigils[:]:
            self.setSigilUnoccupied(index)
        self._updateTrackIntensity(self.BaseTrackSpin, 1.5)

    def forceDoorsOpen(self):
        pass

    def forceDoorsClosed(self):
        if hasattr(self, 'closeDoors'):
            self.closeDoors.finish()

    def enterClosing(self, ts):
        if self.localToonOnBoard:
            elevator = self.getPlaceElevator()
            if elevator:
                elevator.fsm.request('elevatorClosing')
            if self.irisTrack:
                self.irisTrack.pause()
            self.irisTrack = Sequence(
                Wait(max(0.0, self.closeTime - 1.0)),
                Func(base.transitions.fadeOut, 0.8))
            self.irisTrack.start()

        self.closeDoors = Parallel(
            Sequence(self.getPortInterval(),
                     Func(self.onDoorCloseFinish)),
            LerpFunctionInterval(
                self.setSpinIntensity, duration=1.0,
                fromData=self.trackSpinIntensity,
                toData=self.ToonsEnteringTrackSpin))
        self.closeDoors.start(ts)

    def allowedToEnter(self, zoneId=None):
        return True

    def getElevatorModel(self):
        return self.elevatorModel

    def getZoneId(self):
        return self.zoneId

    def getInstanceId(self):
        """Return the Major Player miniboss identifier for this sigil set."""
        return None

    def getDestinationWhere(self):
        from toontown.building import MajorPlayerInstanceGlobals
        return MajorPlayerInstanceGlobals.BOSS_BATTLE_STATE

    def _restoreFailedInstanceTransition(self):
        try:
            base.transitions.fadeIn(0.5)
        except:
            pass
        if hasattr(self, 'restoreTeleportTargets'):
            self.restoreTeleportTargets()

    def __goToBossOffice(self, zoneId):
        from toontown.building import MajorPlayerInstanceGlobals

        playGame = self.cr.playGame
        if not playGame:
            self.notify.warning(
                'Cannot enter Major Player instance %s: PlayGame unavailable.' %
                zoneId)
            self._restoreFailedInstanceTransition()
            return

        instanceId = self.getInstanceId()
        if not instanceId:
            self.notify.warning(
                'Cannot enter Major Player instance %s: no miniboss id.' %
                zoneId)
            self._restoreFailedInstanceTransition()
            return

        # A Major Player fight is a temporary room attached to the currently
        # loaded MML town loader.  It is not a hood and it is not a Cog HQ.
        # Using the town loader's quiet-zone state keeps the MML hood, DNA
        # store, sky, and cached resources alive while the dynamic zone syncs.
        hood = getattr(playGame, 'hood', None)
        townLoader = getattr(hood, 'loader', None)
        if (hood is None or
                getattr(hood, 'hoodId', None) !=
                ToontownGlobals.MinniesMelodyland or
                townLoader is None or
                not hasattr(townLoader, 'fsm')):
            self.notify.warning(
                'Cannot enter Major Player miniboss %s outside the MML '
                'town loader.' % instanceId)
            self._restoreFailedInstanceTransition()
            return

        requestStatus = {
            'loader': MajorPlayerInstanceGlobals.INSTANCE_LOADER,
            'where': self.getDestinationWhere(),
            'how': 'teleportIn',
            'hoodId': ToontownGlobals.MinniesMelodyland,
            'zoneId': zoneId,
            'shardId': None,
            'avId': -1,
            'minibossId': instanceId,
            'majorPlayerInstance': 1,
        }
        if not townLoader.fsm.request('quietZone', [requestStatus]):
            self.notify.warning(
                'MML town loader rejected Major Player miniboss %s.' %
                instanceId)
            self._restoreFailedInstanceTransition()

    def setBossOfficeZone(self, zoneId):
        if self.localToonOnBoard:
            self.__goToBossOffice(zoneId)

    def setBossOfficeZoneForce(self, zoneId):
        self.__goToBossOffice(zoneId)

    def getDestName(self):
        return getattr(TTLocalizer, 'ElevatorMajorPlayer', 'High Roller')

    @property
    def closeTime(self):
        return ElevatorData[self.type]['closeTime']

    def _cleanupVisuals(self):
        taskMgr.remove(self.uniqueName(self.TrackSpinTaskName))
        taskMgr.remove(self.uniqueName('setupSigilvatorDelay'))
        if self.irisTrack:
            self.irisTrack.pause()
            self.irisTrack = None
        if self.updateSpinIntensitySeq:
            self.updateSpinIntensitySeq.pause()
            self.updateSpinIntensitySeq = None
        for seq in self.sigilGlowSeqs:
            if seq:
                seq.pause()
        for seq in self.lightSeqs:
            if seq:
                seq.pause()
        for seq in self.sigilRotationSeqs:
            if seq:
                seq.pause()
        for particles in self.sigilParticles:
            if particles:
                try:
                    particles.cleanup()
                except:
                    pass
        self.sigilParticles = []

    def disable(self):
        if (hasattr(self, 'closeDoors') and self.closeDoors and
                self.closeDoors.isPlaying()):
            self.closeDoors.finish()
        self._cleanupVisuals()
        DistributedElevatorExt.DistributedElevatorExt.disable(self)

    def delete(self):
        self._cleanupVisuals()
        DistributedElevatorExt.DistributedElevatorExt.delete(self)
        if self.elevatorModel and not self.elevatorModel.isEmpty():
            self.elevatorModel.removeNode()
        self.elevatorModel = None
