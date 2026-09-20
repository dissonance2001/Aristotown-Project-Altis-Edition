from panda3d.core import *
from direct.interval.IntervalGlobal import *
import math

from toontown.clashsuit.suit import BossCogGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.distributed import DistributedNode
from direct.task import Task
from toontown.toonbase import ToontownGlobals
from math import *

def circleX(angle, radius, centerX, centerY):
    x = radius * cos(angle) + centerX
    return x


def circleY(angle, radius, centerX, centerY):
    y = radius * sin(angle) + centerY
    return y


def getCirclePoints(segCount, centerX, centerY, radius, wideX = 1.0, wideY = 1.0):
    returnShape = []
    for seg in range(0, int(segCount)):
        coordX = wideX * circleX(pi * 2.0 * float(float(seg) / float(segCount)), radius, centerX, centerY)
        coordY = wideY * circleY(pi * 2.0 * float(float(seg) / float(segCount)), radius, centerX, centerY)
        returnShape.append((coordX, coordY, 1))

    coordX = wideX * circleX(pi * 2.0 * float(0 / segCount), radius, centerX, centerY)
    coordY = wideY * circleY(pi * 2.0 * float(0 / segCount), radius, centerX, centerY)
    returnShape.append((coordX, coordY, 1))
    return returnShape



@DirectNotifyCategory()
class DistributedLawbotBossSecurityCamera(DistributedNode.DistributedNode):
    
    stomperModel = 'phase_9/models/cogHQ/square_stomper'

    def __init__(self, cr, silent=False):
        DistributedNode.DistributedNode.__init__(self, cr)
        self.silent = silent
        node = hidden.attachNewNode('DistributedNodePathEntity')
        self.trackBeamGN = None
        self.trackFloorGN = None
        self.trackX = 0.0
        self.trackY = 0.0
        self.radius = 11.5
        self.trackShape = []
        self.trackShape = getCirclePoints(7, 0.0, 0.0, self.radius)
        self.trackShapeFloor = []
        self.trackShapeFloor = getCirclePoints(16, 0.0, 0.0, self.radius)
        self.zFloat = 0.05
        self.projector = Point3(0, 0, 40)
        self.isToonIn = 0
        self.toonX = 0
        self.toonY = 0
        self.canDamage = 1
        self.accel = BossCogGlobals.LawbotBossSpotlightAccel[0]
        self.maxVel = BossCogGlobals.LawbotBossSpotlightVelocity[0]
        self.vX = 0.0
        self.vY = 0.0
        self.targetX = self.trackX
        self.targetY = self.trackY
        self.targetDoId = None
        self.targetDo = None
        self.targetPos = (0, 0)
        self.lastTime = 0.0
        self.currentTime = 0.0
        self.delta = 0.0
        self.isCogRound = 0
        self.wideX = 1.0
        self.wideY = 1.0
        self.Norm = {}
        self.Norm['Red'] = 0.2
        self.Norm['Green'] = 0.2
        self.Norm['Blue'] = 0.2
        self.Norm['Alpha'] = 1.0
        self.Alert = {}
        self.Alert['Red'] = 1.0
        self.Alert['Green'] = 0.0
        self.Alert['Blue'] = 0.0
        self.Alert['Alpha'] = 1.0
        self.attackSound = loader.loadSfx('phase_9/audio/sfx/CHQ_GOON_tractor_beam_alarmed.ogg')
        self.onSound = loader.loadSfx('phase_11/audio/sfx/LB_camera_shutter_2.ogg')
        self.attackTrack = Parallel(SoundInterval(self.attackSound, node=self, volume=0.8), SoundInterval(self.onSound, node=self, volume=0.8))
        self.moveStartSound = loader.loadSfx('phase_11/audio/sfx/LB_laser_beam_on_2.ogg')
        self.moveStartTrack = Parallel(SoundInterval(self.moveStartSound, node=self, volume=0.4))
        self.moveLoopSound = loader.loadSfx('phase_11/audio/sfx/LB_laser_beam_hum_2.ogg')
        self.moveLoopSound.setLoop()
        self.moveLoopTrack = Parallel(SoundInterval(self.moveLoopSound, node=self, volume=0.4))
        self.moveStopSound = loader.loadSfx('phase_11/audio/sfx/LB_laser_beam_off_2.ogg')
        self.moveStopTrack = Parallel(SoundInterval(self.moveStopSound, node=self, volume=0.4))
        self.taskName = None
        return

    def generateInit(self):
        self.notify.debug('generateInit')
        DistributedNode.DistributedNode.generateInit(self)

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        self.notify.debug('generate')
        DistributedNode.DistributedNode.generate(self)

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        self.notify.debug('announceGenerate')
        DistributedNode.DistributedNode.announceGenerate(self)
        self.trackBeamNode = self.attachNewNode('tracking Beam Node')
        self.trackBeamGN = GeomNode('tracking Beam')
        self.trackBeamNode.attachNewNode(self.trackBeamGN)
        self.trackBeamNode.setTransparency(TransparencyAttrib.MAlpha)
        self.trackBeamNode.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        self.trackBeamNode.setTwoSided(False)
        self.trackBeamNode.setDepthWrite(False)
        self.trackFloorNode = self.attachNewNode('tracking floor Node')
        self.trackFloorGN = GeomNode('tracking Floor')
        self.trackFloorNode.attachNewNode(self.trackFloorGN)
        self.trackFloorNode.setTransparency(TransparencyAttrib.MAlpha)
        self.trackFloorNode.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        self.trackFloorNode.setTwoSided(False)
        self.trackFloorNode.setDepthWrite(False)
        self.loadModel()
        return

    def disable(self):
        self.notify.debug('disable')

        self.moveLoopTrack.finish()
        del self.moveLoopTrack

        self.attackTrack.finish()
        del self.attackTrack

        self.moveStartTrack.finish()
        del self.moveStartTrack

        self.moveStopTrack.finish()
        del self.moveStopTrack

        self.ignoreAll()
        DistributedNode.DistributedNode.disable(self)

    def delete(self):
        self.notify.debug('delete')
        self.unloadModel()
        if self.taskName:
            taskMgr.remove(self.taskName)
        DistributedNode.DistributedNode.delete(self)

    def loadModel(self):
        self.reparentTo(render)
        self.rotateNode = self.attachNewNode('rotate')
        self.model = loader.loadModel(self.stomperModel)
        self.model.reparentTo(self.rotateNode)
        self.model.setPos(0, 1, 0)
        self.taskName = 'securityCameraupdate %s' % self.doId
        taskMgr.add(self.__updateTrack, self.taskName, priority=25)

    def unloadModel(self):
        if self.model:
            self.model.removeNode()
            del self.model
            self.model = None
        return

    def newPosition(self, posX, posY):
        self.targetPos = Point3(posX, posY, 0)

    def __updateTrack(self, task):
        if self.targetDo:
            self.targetX = self.targetDo.getX(self)
            self.targetY = self.targetDo.getY(self)
        else:
            self.targetX = self.targetPos[0]
            self.targetY = self.targetPos[1]
        self.rotateNode.setPos(self.projector)
        self.rotateNode.lookAt(Point3(self.trackX, self.trackY, 0.0))
        dt = globalClock.getDt()
        deccel = 1.0 - 1.0 * (dt * 7.0)
        if deccel < 0:
            deccel = 0.0
        dirX = 0.0
        dirY = 0.0
        distX = self.targetX - self.trackX
        distY = self.targetY - self.trackY
        trigDist = math.sqrt(distX * distX + distY * distY)
        totalDist = abs(distX) + abs(distY)
        propX = abs(distX) / (totalDist + 0.01)
        propY = abs(distY) / (totalDist + 0.01)
        if self.targetX != self.trackX:
            dirX = distX / abs(distX)
        if self.targetY != self.trackY:
            dirY = distY / abs(distY)
        if trigDist < self.radius * 0.5 + 1.0:
            self.vX = self.vX * deccel
            self.vY = self.vY * deccel
            if not self.silent:
                self.moveStopTrack.start()
                self.moveLoopTrack.finish()
        else:
            if not self.moveLoopTrack.isPlaying() and not self.silent:
                self.moveLoopTrack.start()
                self.moveStartTrack.start()
            self.vX += dirX * self.accel * propX
            self.vY += dirY * self.accel * propY
        if self.vX > self.maxVel:
            self.vX = self.maxVel
        if self.vX < -self.maxVel:
            self.vX = -self.maxVel
        if self.vY > self.maxVel:
            self.vY = self.maxVel
        if self.vY < -self.maxVel:
            self.vY = -self.maxVel
        self.trackX += self.vX * dt
        self.trackY += self.vY * dt
        self.genTrack()
        dist = self.getDist(base.localAvatar)
        if dist < self.radius and self.canDamage:
            if not base.localAvatar.isStunned and not self.isCogRound:
                self.canDamage = 0
                self.sendUpdate('trapFire', [])
                base.localAvatar.stunToon()
                base.localAvatar.playDialogueForString('!')
                if not self.silent:
                    self.attackTrack.start()
                taskMgr.doMethodLater(2.0, self._resetDam, 'reset Damage')
        return Task.cont

    def _resetDam(self, task = None):
        self.canDamage = 1
        if hasattr(self, 'attackTrack') and self.attackTrack.isPlaying():
            self.attackTrack.finish()

    def getDist(self, thing):
        dx = thing.getPos(self)[0] - self.trackX
        dy = thing.getPos(self)[1] - self.trackY
        return sqrt(dx * dx + dy * dy)

    def genTrack(self):
        dist = self.getDist(base.localAvatar)
        draw = 1.0 / (0.01 + float(pow(dist, 0.4)))
        self.trackShape = []
        self.trackShape = getCirclePoints(5 + draw * 12.0, 0.0, 0.0, self.radius, self.wideX, self.wideY)
        self.trackShapeFloor = []
        self.trackShapeFloor = getCirclePoints(5 + draw * 50.0, 0.0, 0.0, self.radius, self.wideX, self.wideY)
        if self.trackBeamGN:
            self.trackBeamGN.removeAllGeoms()
        if self.trackFloorGN:
            self.trackFloorGN.removeAllGeoms()
        beamRed = 0.0
        beamGreen = 0.0
        beamBlue = 0.0
        beamAlpha = 1.0
        if self.canDamage:
            origin = self.Norm
        else:
            origin = self.Alert
        self.gFormat = GeomVertexFormat.getV3cp()
        self.trackBeamVertexData = GeomVertexData('holds my vertices', self.gFormat, Geom.UHDynamic)
        self.trackBeamVertexWriter = GeomVertexWriter(self.trackBeamVertexData, 'vertex')
        self.trackBeamColorWriter = GeomVertexWriter(self.trackBeamVertexData, 'color')
        self.trackFloorVertexData = GeomVertexData('holds my vertices', self.gFormat, Geom.UHDynamic)
        self.trackFloorVertexWriter = GeomVertexWriter(self.trackFloorVertexData, 'vertex')
        self.trackFloorColorWriter = GeomVertexWriter(self.trackFloorVertexData, 'color')
        self.trackBeamVertexWriter.addData3f(self.projector[0], self.projector[1], self.projector[2])
        self.trackBeamColorWriter.addData4f(origin['Red'], origin['Green'], origin['Blue'], origin['Alpha'])
        self.trackFloorVertexWriter.addData3f(self.trackX, self.trackY, self.zFloat)
        self.trackFloorColorWriter.addData4f(origin['Red'], origin['Green'], origin['Blue'], origin['Alpha'])
        for vertex in self.trackShape:
            self.trackBeamVertexWriter.addData3f(self.trackX + vertex[0], self.trackY + vertex[1], self.zFloat)
            self.trackBeamColorWriter.addData4f(beamRed, beamGreen, beamBlue, beamAlpha)

        for vertex in self.trackShapeFloor:
            self.trackFloorVertexWriter.addData3f(self.trackX + vertex[0], self.trackY + vertex[1], self.zFloat)
            self.trackFloorColorWriter.addData4f(origin['Red'], origin['Green'], origin['Blue'], origin['Alpha'])

        self.trackBeamTris = GeomTrifans(Geom.UHStatic)
        self.trackFloorTris = GeomTrifans(Geom.UHStatic)
        sizeTrack = len(self.trackShape)
        self.trackBeamTris.addVertex(0)
        for countVertex in range(1, sizeTrack + 1):
            self.trackBeamTris.addVertex(countVertex)

        self.trackBeamTris.addVertex(1)
        self.trackBeamTris.closePrimitive()
        self.trackBeamGeom = Geom(self.trackBeamVertexData)
        self.trackBeamGeom.addPrimitive(self.trackBeamTris)
        self.trackBeamGN.addGeom(self.trackBeamGeom)
        sizeTrack = len(self.trackShapeFloor)
        self.trackFloorTris.addVertex(0)
        for countVertex in range(1, sizeTrack + 1):
            self.trackFloorTris.addVertex(countVertex)

        self.trackFloorTris.addVertex(1)
        self.trackFloorTris.closePrimitive()
        self.trackFloorGeom = Geom(self.trackFloorVertexData)
        self.trackFloorGeom.addPrimitive(self.trackFloorTris)
        self.trackFloorGN.addGeom(self.trackFloorGeom)

    def setProjector(self, projPoint):
        self.projector = Point3(projPoint[0], projPoint[1], projPoint[2])
        self.rotateNode.setPos(self.projector)
        if self.trackBeamGN and self.trackFloorGN:
            self.genTrack()

    def setVelocity(self, velocity):
        self.maxVel = velocity

    def setAcceleration(self, acceleration):
        self.accel = acceleration

    def setTrackingDo(self, doId):
        self.targetDoId = doId
        self.targetDo = self.cr.doId2do.get(self.targetDoId)
        self.radius = 8.0
        self.maxVel = 25.0
        self.accel = 15.0
        self.setProjector((0, 0, 115))
        self.updateColors()

    def updateColors(self, type=0):
        if type == 0:
            self.Norm['Red'] = 0.0
            self.Norm['Green'] = 1.0
            self.Norm['Blue'] = 0.0
            self.Norm['Alpha'] = 1.0
            self.Alert['Red'] = 1.0
            self.Alert['Green'] = 0.5
            self.Alert['Blue'] = 0.0
            self.Alert['Alpha'] = 1.0
        elif type == 1:
            self.Norm['Red'] = 1.0
            self.Norm['Green'] = 1.0
            self.Norm['Blue'] = 1.0
            self.Norm['Alpha'] = 1.0
            self.Alert['Red'] = 1.0
            self.Alert['Green'] = 0.0
            self.Alert['Blue'] = 0.0
            self.Alert['Alpha'] = 1.0

    def setHideModel(self, flag):
        if flag:
            self.model.stash()
        else:
            self.model.unstash()

    def setWideX(self, num):
        self.wideX = num

    def setWideY(self, num):
        self.wideY = num
