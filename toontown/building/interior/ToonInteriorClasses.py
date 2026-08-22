import random
import time

from direct.actor.Actor import Actor
from panda3d.core import Mat4, Point3, CollisionTraverser, CollisionHandlerQueue, CollisionNode, BitMask32, CollisionRay, \
    CollisionSphere, DecalEffect, TextNode, ModelNode, CollisionTube

from direct.interval.IntervalGlobal import *
from toontown.building import ToonInteriorColors, ToonInteriorTextures
from toontown.building.interior.props.LavaLamp import LavaLamp
from toontown.hood import ZoneUtil
from toontown.shader import FogGlobals
from toontown.shader.ShaderEnums import ShaderType
from toontown.shader.ToontownFog import ToontownFog
from toontown.toon.OneTimeCutsceneGlobals import OneTimeCutscenes
from toontown.toonbase.ToonBase import *
from toontown.dna.DNAParser import DNADoor
from toontown.building.DistributedToonInterior import DistributedToonInterior
from toontown.toonbase.ToontownGlobals import WallBitmask
from toontown.utils.PandaNodeHelper import *

BASIC_SOUND_PATH = 'standard'

CustomToonInteriors = {}


def ToonInteriorCls(cls):
    zoneIds = cls.ZONE_ID
    if type(zoneIds) not in (tuple, list):
        zoneIds = [zoneIds]

    for zoneId in zoneIds:
        if zoneId is None:
            continue
        if zoneId <= 0:
            raise AttributeError('%s has an invalid Zone ID! (%s)' % (cls.__name__, zoneId))
        if zoneId in CustomToonInteriors:
            raise AttributeError('%s tried to define Zone ID %s twice in CustomToonInteriors!' % (cls.__name__, zoneId))
        CustomToonInteriors[zoneId] = cls

    return cls


class DistributedCustomInteriorBase(DistributedToonInterior):
    MODEL_PATH = None
    SOUND_PATH = None
    ZONE_ID = 0
    BASIC_DOOR = True
    COPY_DOOR_NODE = True
    FLATTEN_INTERIOR = True
    DoorOriginOffset = Point3(0, -0.025, 0)
    DoorOriginScale = Point3(0.8, 0.8, 0.8)

    def __init__(self, cr):
        DistributedToonInterior.__init__(self, cr)
        self.doorNP = None
        testAttribs = ('MODEL_PATH', 'ZONE_ID')
        for attribName, interiorAttrib in [(testAttrib, getattr(self, testAttrib, None)) for testAttrib in testAttribs]:
            if not interiorAttrib:
                raise AttributeError("%s has no %s!" % (self.__class__.__name__, attribName))

    def setDnaStore(self):
        self.dnaStore = base.cr.playGame.dnaStore

    def setupInteriorModel(self):
        if __debug__:
            self.interior = loader.loadModel(self.MODEL_PATH, noCache=True)
        else:
            self.interior = loader.loadModel(self.MODEL_PATH)
        self.interior.reparentTo(render)
        if self.BASIC_DOOR:
            self.setupDoor()

    def setup(self):
        self.setDnaStore()
        self.setupInteriorModel()
        if self.FLATTEN_INTERIOR:
            self.interior.flattenMedium()
        self.doMusic()

    def getDoorColor(self):
        return Vec4(0.8, 0.5, 0.3, 1.0)

    def chooseDoor(self):
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        return door

    def handleDoorFrame(self):
        doorFrame = self.doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        doorFrame.setColor(self.doorColor)

    def setupDoor(self):
        door = self.chooseDoor()
        if door.isEmpty():
            self.notify.warning("Door is empty, not placing a door.")
            return

        doorOrigin = render.find('**/door_origin;+s')
        if doorOrigin.isEmpty():
            self.notify.warning("Couldn't find door_origin DCS node!!")
            doorOrigin = NodePath(render)
            doorOrigin.setPos(0, 0, 0)

        self.doorColor = self.getDoorColor()
        if self.COPY_DOOR_NODE:
            self.doorNP = door.copyTo(doorOrigin)
        else:
            self.doorNP = door
            self.doorNP.reparentTo(doorOrigin)
        doorOrigin.setScale(self.DoorOriginScale)
        doorOrigin.setPos(doorOrigin, self.DoorOriginOffset)
        DNADoor.setupDoor(self.doorNP, self.interior, doorOrigin, self.dnaStore, str(self.block), self.doorColor)
        self.handleDoorFrame()

    def getProperSoundPath(self):
        if self.SOUND_PATH == BASIC_SOUND_PATH:
            return base.cr.playGame.hood.loader.activityMusic
        elif type(self.SOUND_PATH) is dict:
            return self.SOUND_PATH.get(self.zoneId, 'None')
        else:
            return self.SOUND_PATH

    def doMusic(self):
        base.musicMgr.playMusic(self.getProperSoundPath(), looping=1)

    def disable(self):
        self.doorNP = None
        DistributedToonInterior.disable(self)


@ToonInteriorCls
class DistributedPacesetterLobby(DistributedCustomInteriorBase):
    MODEL_PATH = 'phase_8/models/areas/ttcc_int_psetter_lobby'
    SOUND_PATH = 'pacesetter_lobby'
    FLATTEN_INTERIOR = False
    ZONE_ID = 9613
    BellCollisionName = 'Pacesetter-BellCollision'
    BellCollisionCooldown = 1.0

    def __init__(self, cr):
        DistributedCustomInteriorBase.__init__(self, cr)
        self.lavaLamps = []
        self.waterfallNsm = None
        self.waterNsm = None
        self.streetSimNode = render.attachNewNode("streetSimNode")
        self.soundNode = None
        self.hitBellSfx = loader.loadSfx('phase_8/audio/sfx/ttcc_int_psetter_bell.ogg')
        self.lastBellHitTime = 0
        self.fogBG = ToontownFog(FogGlobals.zoneId2FogAttrs[9000], "PacesetterLobby_BGFog")
        base.cr.playGame.hood.startSky()

    def delete(self):
        if self.waterfallNsm:
            self.waterfallNsm.cleanup()
        if self.waterNsm:
            self.waterNsm.cleanup()
        if self.streetSimNode:
            self.streetSimNode.removeNode()
        if getattr(base.cr.playGame, 'hood', None) and getattr(base.cr.playGame.hood, 'sky', None):
            base.cr.playGame.hood.stopSky()
        for lamp in self.lavaLamps:
            lamp.cleanup()
        del self.lavaLamps
        if self.hitBellSfx:
            self.hitBellSfx.stop()
            del self.hitBellSfx
        del self.soundNode
        if self.fogBG:
            self.fogBG.removeFog()
            self.fogBG = None
        base.localAvatar.wakeOverride = False
        DistributedCustomInteriorBase.delete(self)

    def setupInteriorModel(self):
        DistributedCustomInteriorBase.setupInteriorModel(self)

        self.interior.find("**/upper_floor_geom").node().setEffect(DecalEffect.make())
        self.interior.find("**/lower_floor_geom").node().setEffect(DecalEffect.make())

        for i in range(5):
            lamp = LavaLamp(colorIndex=i)
            lamp.reparentTo(self.interior.find('**/lavalamp_%s' % i))
            self.lavaLamps.append(lamp)

        streetNodes = base.cr.playGame.hood.loader.nodeList
        wantedGroups = ("9108", "9109", "9110", "9111", "9112")
        for node in streetNodes:
            if node.getName() in wantedGroups:
                node.copyTo(self.streetSimNode)

        self.streetSimNode.setPos(-120, 190, -5.0)
        self.streetSimNode.setH(90)
        self.streetSimNode.setScale(2)

        sb17 = self.streetSimNode.find('**/sb16:_landmark__DNARoot')
        if (not sb17.isEmpty()) and (not sb17.isHidden()):
            elevator = loader.loadModel('phase_4/models/modules/elevator')
            elevator.reparentTo(self.streetSimNode)
            elevator.setH(60)
            elevator.setPos(-171.5, -68.5, 0)
            elevator.setScale(0.8, 1, 1)
            npc = elevator.findAllMatches('**/floor_light_?;+s')
            for light in npc:
                light.hide()

        sb9 = self.streetSimNode.find('**/sb9:_landmark__DNARoot')
        if (not sb9.isEmpty()) and (not sb9.isHidden()):
            elevator = loader.loadModel('phase_4/models/modules/elevator')
            elevator.reparentTo(self.streetSimNode)
            elevator.setPos(-98, -2.5, 0)
            npc = elevator.findAllMatches('**/floor_light_?;+s')
            for light in npc:
                light.hide()

        sign = self.streetSimNode.find("**/neighborhood_sign_DL_DNARoot")
        if not sign.isEmpty():
            sign.removeNode()
        tb13 = self.streetSimNode.find("**/tb13:toon_landmark_psetter_DNARoot")
        if not tb13.isEmpty():
            tb13.removeNode()

        for node in self.streetSimNode.findAllMatches('**/*EXTERIOR_ONLY'):
            node.removeNode()
        for node in self.streetSimNode.findAllMatches('**/+CollisionNode'):
            node.removeNode()

        self.waterfallNsm = NodeShaderManager(node=self.interior.find('**/waterfall'))
        self.waterfallNsm.addShader(NodeShader(shaderType=ShaderType.Waterfall))
        self.waterNsm = NodeShaderManager(node=self.interior.find('**/water'))
        self.waterNsm.addShader(NodeShader(shaderType=ShaderType.Ripple))

        self.waterTrigger = self.interior.find('**/water_trigger')
        self.accept('enter' + self.waterTrigger.getName(), self.__inEnter)
        self.accept('exit' + self.waterTrigger.getName(), self.__inExit)

        self.setupBell()

        self.fogBG.attachFog([self.streetSimNode, base.cr.playGame.hood.sky])
        self.interior.find("**/front_glass_geom").setBin('transparent', 0)

    def __inEnter(self, *args):
        base.localAvatar.wakeOverride = True

    def __inExit(self, *args):
        base.localAvatar.wakeOverride = False

    def setupBell(self):
        ct = CollisionTube(0, 0, 0, 0, 0, 10, 1)
        ct.setTangible(0)
        cn = CollisionNode(self.BellCollisionName)
        cn.addSolid(ct)
        cn.setCollideMask(ToontownGlobals.WallBitmask)
        self.soundNode = self.interior.attachNewNode(cn)
        self.soundNode.setPos(-29, 26, 0)
        self.accept('enter%s' % self.BellCollisionName, self.__handleEnterBell)

    def __handleEnterBell(self, _=None):
        if time.time() - self.lastBellHitTime < self.BellCollisionCooldown:
            return
        self.lastBellHitTime = time.time()
        self.doBellSound()
        self.sendUpdate('doBellSound')

    def doBellSound(self):
        base.playSfx(self.hitBellSfx, volume=0.8, node=self.soundNode)