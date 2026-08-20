from __future__ import absolute_import
import random
from toontown.toonbase.ToonBaseGlobal import *
from pandac.PandaModules import *
from toontown.toonbase.ToontownGlobals import *
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.building import ToonInteriorColors
from toontown.dna.DNAParser import DNADoor
from toontown.building import DistributedToonInterior
from toontown.hood import ZoneUtil
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase


class DistributedPizzeriaInterior(DistributedObject.DistributedObject):

    def setupFreezer(self):
        # DistributedSwitch.DistributedSwitch.setupSwitch(self)
        radius = 45.0
        cSphere = CollisionSphere(85.113,  49.793,  0.025, radius)
        cSphere.setTangible(0)
        cSphereNode = CollisionNode('FreezerTransition')
        cSphereNode.addSolid(cSphere)
        self.cSphereNodePath = self.interior.attachNewNode(cSphereNode)
        cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)

    def setupFreezerMusic(self):
        self.coldTriggerIn = self.interior.find('**/mid_cold_transition_IN')
        self.coldTriggerOut = self.interior.find('**/mid_cold_transition_OUT')
        if not self.coldTriggerIn.isEmpty():
            self.accept('enter' + self.coldTriggerIn.getName(), self.__enterColdRoom)
        if not self.coldTriggerOut.isEmpty():
            self.accept('enter' + self.coldTriggerOut.getName(), self.__leaveColdRoom)

    def __enterColdRoom(self, *args):
        if self.inColdRoom:
            return
        self.inColdRoom = True
        place = base.cr.playGame.getPlace()
        if place and hasattr(place, 'PizzeriaFreezerMusic'):
            place.PizzeriaFreezerMusic(None)

    def __leaveColdRoom(self, *args):
        if not self.inColdRoom:
            return
        self.inColdRoom = False
        place = base.cr.playGame.getPlace()
        if place and hasattr(place, 'PizzeriaMusic'):
            place.PizzeriaMusic(None)

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.dnaStore = cr.playGame.dnaStore
        self.PizzaRoomNP = None
        self.MidRoomNP = None
        self.ColdRoomNP = None
        self.bossDoor_left = None
        self.bossDoor_right = None
        self.tableList = []
        self.inColdRoom = False
        self.coldTriggerIn = None
        self.coldTriggerOut = None

    def generate(self):
        DistributedObject.DistributedObject.generate(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.setup()
        #taskMgr.doMethodLater(0.0, self.doMusic, 'pacelobbyMusic')  # gotta delay it a bit

   # def doMusic(self, task):
    #    base.musicManager.stopAllSounds()
     #   self.pizzerialobbyMusicFile = loader.loadMusic("phase_10/audio/bgm/merc/instance_plutocrat_lobby_standard.ogg")
      #  self.pizzerialobbyMusic = base.playMusic(self.pizzerialobbyMusicFile, looping=1)
       # return task.done

    def setZoneIdAndBlock(self, zoneId, block):
        self.zoneId = zoneId
        self.block = block

    def chooseDoor(self):
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        return door

    def applyDecalEffect(self, nodePath):
        if nodePath.isEmpty():
            return
        effect = DecalEffect.make()
        if isinstance(nodePath.node(), GeomNode):
            nodePath.node().setEffect(effect)
        for geom in nodePath.findAllMatches('**/+GeomNode'):
            geom.node().setEffect(effect)

    def setupRoomProps(self):
        self.PizzaRoomNP = self.interior.find('**/pizzaroom')
        self.MidRoomNP = self.interior.find('**/midroom')
        self.ColdRoomNP = self.interior.find('**/coldroom')

        sigilOrigin = self.interior.find('**/sigilvator_origin')
        if not sigilOrigin.isEmpty():
            sigilOrigin.setH(180)

        pizzaTable = loader.loadModel('phase_8/models/props/ttcc_prp_pc_table')
        tableIndex = 0
        if not self.PizzaRoomNP.isEmpty():
            for node in self.PizzaRoomNP.findAllMatches('**/table_origin_*'):
                tableIndex += 1
                table = pizzaTable.copyTo(node)
                tableCollision = table.find('**/pizza_table_coll_top')
                if not tableCollision.isEmpty():
                    tableCollision.setName('coll_tableTop_%s' % tableIndex)
            for node in self.PizzaRoomNP.findAllMatches('**/booths_table_top_coll_*'):
                tableIndex += 1
                node.setName('coll_tableTop_%s' % tableIndex)
        self.tableList = [0] * tableIndex

        ceilingLight = loader.loadModel('phase_8/models/props/ttcc_prp_pc_lampCeiling')
        if not self.PizzaRoomNP.isEmpty():
            for node in self.PizzaRoomNP.findAllMatches('**/ceiling_light_origin_*'):
                ceilingLight.instanceTo(node)

        wallLight = loader.loadModel('phase_8/models/props/ttcc_prp_pc_lampWall')
        if not self.PizzaRoomNP.isEmpty():
            for node in self.PizzaRoomNP.findAllMatches('**/wall_light_origin_**'):
                wallLight.instanceTo(node)

        if not self.PizzaRoomNP.isEmpty():
            floor = self.PizzaRoomNP.find('**/floor_pizza_main_geom')
            self.applyDecalEffect(floor)
            counterFloor = self.PizzaRoomNP.find('**/countertiles_floor_geom')
            self.applyDecalEffect(counterFloor)

        if not self.ColdRoomNP.isEmpty():
            coldFloor = self.ColdRoomNP.find('**/coldroom_floor_geom')
            self.applyDecalEffect(coldFloor)
            self.bossDoor_left = self.ColdRoomNP.find('**/freezerdoor_L')
            self.bossDoor_right = self.ColdRoomNP.find('**/freezerdoor_R')

        pizzaPositions = (
            (-19.513, 37.228, 3.531, -55.737, 0.000, 0.000),
            (31.779, 48.006, 2.525, -58.124, 0.000, 0.000),
            (22.289, 67.669, 6.531, 165.832, 0.000, 0.000),
            (3.774, 103.713, 6.525, 30.149, 0.000, 0.000),
            (-3.369, 104.111, 6.525, 36.193, 0.000, 0.000),
            (-19.243, 88.888, 5.013, 67.591, 0.000, 0.000),
            (37.464, 80.827, 6.531, -129.871, 0.000, 0.000),
            (57.268, 80.060, 6.531, -130.540, 0.000, 0.000),
            (58.091, 106.492, 6.525, 161.242, 0.000, 0.000),
            (-1.134, 98.849, 6.525, 26.388, 0.000, 0.000),
            (-22.885, 63.734, 5.013, 91.273, 0.000, 0.000),
            (29.527, 105.869, 6.525, 110.790, 0.000, 0.000),
            (64.049, 103.551, 6.525, 113.320, 0.000, 0.000),
        )
        pizzaModel = loader.loadModel('phase_8/models/props/pizza.bam')
        for x, y, z, h, p, r in pizzaPositions:
            pizza = pizzaModel.copyTo(self.interior)
            pizza.setPosHpr(render, x, y, z, h, p, r)
            pizza.setScale(5.0)
        pizzaModel.removeNode()

        for snowCollision in self.interior.findAllMatches('**/snowpile_coll_*'):
            snowCollision.setTag('giveSnowballs', 'snowballs')
            snowCollision.setTag('surface', 'snow')

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.interior = loader.loadModel('phase_8/models/areas/ttcc_int_pcrat_lobby.bam')
        self.interior.reparentTo(render)
        self.setupRoomProps()
        self.setupFreezer()
        self.setupFreezerMusic()
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        door = self.chooseDoor()
        doorOrigin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(doorOrigin)
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        doorColor = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, doorOrigin, self.dnaStore, str(self.block), doorColor)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        del self.colors
        del self.dnaStore
        del self.randomGenerator
        if self.ColdRoomNP and not self.ColdRoomNP.isEmpty():
            storageGroup = self.ColdRoomNP.find('**/cr_prop_storage_group')
            if not storageGroup.isEmpty():
                storageGroup.flattenStrong()
        if self.PizzaRoomNP and not self.PizzaRoomNP.isEmpty():
            self.PizzaRoomNP.flattenMedium()
        if self.MidRoomNP and not self.MidRoomNP.isEmpty():
            self.MidRoomNP.flattenMedium()
        for npcToon in self.cr.doFindAllInstances(DistributedNPCToonBase):
            npcToon.initToonState()

    def disable(self):
        if self.coldTriggerIn is not None and not self.coldTriggerIn.isEmpty():
            self.ignore('enter' + self.coldTriggerIn.getName())
        if self.coldTriggerOut is not None and not self.coldTriggerOut.isEmpty():
            self.ignore('enter' + self.coldTriggerOut.getName())
        self.coldTriggerIn = None
        self.coldTriggerOut = None
        self.inColdRoom = False
        self.interior.removeNode()
        del self.interior
        DistributedObject.DistributedObject.disable(self)
