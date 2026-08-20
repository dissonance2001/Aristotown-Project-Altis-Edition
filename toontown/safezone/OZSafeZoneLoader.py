from __future__ import absolute_import
import copy
import random
from direct.actor import Actor
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.interval.IntervalGlobal import *
from pandac.PandaModules import *
from otp.avatar import Avatar
from toontown.chat.ChatGlobals import *
from toontown.nametag.NametagGroup import *
from otp.otpbase import OTPGlobals
from toontown.distributed import DelayDelete
from toontown.effects import Bubbles
from toontown.hood import ZoneUtil
from toontown.safezone.OZPlayground import OZPlayground
from toontown.safezone.SafeZoneLoader import SafeZoneLoader
from toontown.toon import Toon, ToonDNA, NPCToons
from toontown.toonbase import TTLocalizer
from toontown.battle import BattleParticles
from direct.task.Task import Task
from six.moves import map
from six.moves import range

class OZSafeZoneLoader(SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = OZPlayground
        self.musicFile = 'phase_6/audio/bgm/AA_nbrhood.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/AA_SZ_activity.ogg'
        self.dnaFile = 'phase_6/dna/outdoor_zone_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_6/dna/storage_OZ_sz.pdna'
        self.waterInterval = None
        self.splashOne = None
        self.splashOneRender = None
        self.splashTwo = None
        self.splashTwoRender = None
        self.wakeWaterTriangles = []

    def load(self):
        self.done = 0
        SafeZoneLoader.load(self)
        self.birdSound = list(map(base.loader.loadSfx, ['phase_4/audio/sfx/SZ_TC_bird1.ogg', 'phase_4/audio/sfx/SZ_TC_bird2.ogg', 'phase_4/audio/sfx/SZ_TC_bird3.ogg']))
        self.underwaterSound = base.loader.loadSfx('phase_4/audio/sfx/AV_ambient_water.ogg')
        self.swimSound = base.loader.loadSfx('phase_4/audio/sfx/AV_swim_single_stroke.ogg')
        self.submergeSound = base.loader.loadSfx('phase_5.5/audio/sfx/AV_jump_in_water.ogg')

        binMgr = CullBinManager.getGlobalPtr()
        binMgr.addBin('water', CullBinManager.BTFixed, 29)
        waterNodes = self.geom.findAllMatches('**/Water*')
        for i in range(waterNodes.getNumPaths()):
            water = waterNodes.getPath(i)
            water.setTransparency(1)
            water.setBin('water', 51, 1)

        river = self.geom.find('**/river*')
        if not river.isEmpty():
            river.setTransparency(1)
            river.setColor(1, 1, 1, 0.5)

        stream = self.geom.find('**/waterfall*')
        if not stream.isEmpty():
            stream.setTransparency(1)
            stream.setColor(1, 1, 1, 0.5)
            self.waterInterval = self.waterfallInterval(stream)
            self.waterInterval.loop()

        self.splashOne = BattleParticles.loadParticleFile('waterfallSplash.ptf')
        self.splashOne.setPos(-22.6, 17.9, -0.5)
        self.splashOneRender = self.geom.attachNewNode('splashOneRender')
        self.splashOneRender.setDepthWrite(0)
        self.splashOneRender.setBin('fixed', 1)
        self.splashOne.start(self.geom, self.splashOneRender)

        self.splashTwo = BattleParticles.loadParticleFile('waterfallSplashBig.ptf')
        self.splashTwo.setPos(-2.65, 71.4, 7.6)
        self.splashTwoRender = self.geom.attachNewNode('splashTwoRender')
        self.splashTwoRender.setDepthWrite(0)
        self.splashTwoRender.setBin('fixed', 1)
        self.splashTwo.start(self.geom, self.splashTwoRender)
        self._buildWakeWaterTriangles()

    def _buildWakeWaterTriangles(self):
        self.wakeWaterTriangles = []
        waterRoots = self.geom.findAllMatches('**/river*')
        if waterRoots.getNumPaths() == 0:
            waterRoots = self.geom.findAllMatches('**/Water*')
        for rootIndex in range(waterRoots.getNumPaths()):
            waterRoot = waterRoots.getPath(rootIndex)
            geomNodes = waterRoot.findAllMatches('**/+GeomNode')
            if geomNodes.getNumPaths() == 0 and isinstance(waterRoot.node(), GeomNode):
                self._addWakeWaterGeom(waterRoot)
            else:
                for geomIndex in range(geomNodes.getNumPaths()):
                    self._addWakeWaterGeom(geomNodes.getPath(geomIndex))

    def _addWakeWaterGeom(self, geomNodePath):
        geomNode = geomNodePath.node()
        if not isinstance(geomNode, GeomNode):
            return
        for geomIndex in range(geomNode.getNumGeoms()):
            geom = geomNode.getGeom(geomIndex)
            reader = GeomVertexReader(geom.getVertexData(), 'vertex')
            vertices = []
            while not reader.isAtEnd():
                point = reader.getData3f()
                point = self.geom.getRelativePoint(geomNodePath, point)
                vertices.append((point[0], point[1], point[2]))
            for primitiveIndex in range(geom.getNumPrimitives()):
                primitive = geom.getPrimitive(primitiveIndex).decompose()
                for triangleIndex in range(primitive.getNumPrimitives()):
                    start = primitive.getPrimitiveStart(triangleIndex)
                    end = primitive.getPrimitiveEnd(triangleIndex)
                    if end - start != 3:
                        continue
                    i0 = primitive.getVertex(start)
                    i1 = primitive.getVertex(start + 1)
                    i2 = primitive.getVertex(start + 2)
                    if i0 >= len(vertices) or i1 >= len(vertices) or i2 >= len(vertices):
                        continue
                    p0 = vertices[i0]
                    p1 = vertices[i1]
                    p2 = vertices[i2]
                    denom = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
                    if abs(denom) < 0.00001:
                        continue
                    self.wakeWaterTriangles.append((p0, p1, p2, denom, min(p0[0], p1[0], p2[0]), max(p0[0], p1[0], p2[0]), min(p0[1], p1[1], p2[1]), max(p0[1], p1[1], p2[1])))

    def getWakeWaterHeightAt(self, x, y):
        bestHeight = None
        for triangle in self.wakeWaterTriangles:
            p0, p1, p2, denom, minX, maxX, minY, maxY = triangle
            if x < minX or x > maxX or y < minY or y > maxY:
                continue
            a = ((p1[1] - p2[1]) * (x - p2[0]) + (p2[0] - p1[0]) * (y - p2[1])) / denom
            b = ((p2[1] - p0[1]) * (x - p2[0]) + (p0[0] - p2[0]) * (y - p2[1])) / denom
            c = 1.0 - a - b
            if a < -0.001 or b < -0.001 or c < -0.001:
                continue
            height = a * p0[2] + b * p1[2] + c * p2[2]
            if bestHeight is None or height > bestHeight:
                bestHeight = height
        return bestHeight

    def waterfallInterval(self, obj):
        def rollTexMatrix(t, obj=obj):
            obj.setTexOffset(TextureStage.getDefault(), 0, t)
        return LerpFunctionInterval(rollTexMatrix, fromData=0, toData=1, duration=3)

    def exit(self):
        SafeZoneLoader.exit(self)

    def unload(self):
        del self.birdSound
        if self.waterInterval:
            self.waterInterval.finish()
            self.waterInterval = None
        if self.splashOne:
            self.splashOne.cleanup()
            self.splashOne = None
        if self.splashOneRender:
            self.splashOneRender.removeNode()
            self.splashOneRender = None
        if self.splashTwo:
            self.splashTwo.cleanup()
            self.splashTwo = None
        if self.splashTwoRender:
            self.splashTwoRender.removeNode()
            self.splashTwoRender = None
        self.wakeWaterTriangles = []
        SafeZoneLoader.unload(self)
        self.done = 1
