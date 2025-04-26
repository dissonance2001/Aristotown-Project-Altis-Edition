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
        self.cSphereNodePath.show()

    def __init__(self, cr):
        DistributedObject.DistributedObject.__init__(self, cr)
        self.dnaStore = cr.playGame.dnaStore

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

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.interior = loader.loadModel('phase_8/models/areas/ttcc_int_pcrat_lobby.bam')
        self.interior.reparentTo(render)
        self.setupFreezer()
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
        self.interior.flattenMedium()
        for npcToon in self.cr.doFindAllInstances(DistributedNPCToonBase):
            npcToon.initToonState()

    def disable(self):
        self.interior.removeNode()
        del self.interior
        DistributedObject.DistributedObject.disable(self)