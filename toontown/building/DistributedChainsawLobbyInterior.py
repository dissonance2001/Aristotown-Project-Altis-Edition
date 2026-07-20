import random
from toontown.toonbase.ToonBaseGlobal import *
from pandac.PandaModules import *
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.building import ToonInteriorColors
from toontown.building import DistributedToonInterior
from toontown.dna.DNAParser import DNADoor
from toontown.hood import ZoneUtil
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase


class DistributedChainsawLobbyInterior(DistributedToonInterior.DistributedToonInterior):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedChainsawLobbyInterior')

    def __init__(self, cr):
        DistributedToonInterior.DistributedToonInterior.__init__(self, cr)
        self.dnaStore = cr.playGame.dnaStore

    def generate(self):
        DistributedToonInterior.DistributedToonInterior.generate(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.setup()
        taskMgr.doMethodLater(0.1, self.startChainsawMusic, 'chainsawLobbyMusic-%s' % id(self))

    def startChainsawMusic(self, task):
        base.musicManager.stopAllSounds()
        self.music = loader.loadMusic('phase_12/audio/bgm/merc/instance_chainsaw_lobby.ogg')
        if self.music:
            self.music.setLoop(True)
            self.music.setVolume(0.8)
            self.music.play()
        return task.done

    def setZoneIdAndBlock(self, zoneId, block):
        self.zoneId = zoneId
        self.block = block

    def chooseDoor(self):
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        return self.dnaStore.findNode(doorModelName)

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.interior = loader.loadModel('phase_6/models/areas/ttcc_int_cc_lobby.bam')
        self.interior.reparentTo(render)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        door = self.chooseDoor()
        doorOrigin = self.interior.find('**/door_origin;+s')
        if doorOrigin.isEmpty():
            doorOrigin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(doorOrigin)
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        doorColor = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, doorOrigin, self.dnaStore, str(self.block), doorColor)
        doorFrame = doorNP.find('door_*_flat')
        if not doorFrame.isEmpty():
            doorFrame.wrtReparentTo(self.interior)
        del self.colors
        del self.dnaStore
        del self.randomGenerator
        for npcToon in self.cr.doFindAllInstances(DistributedNPCToonBase):
            npcToon.initToonState()

    def disable(self):
        taskMgr.remove('chainsawLobbyMusic-%s' % id(self))
        if hasattr(self, 'music') and self.music:
            self.music.stop()
            self.music = None
        DistributedToonInterior.DistributedToonInterior.disable(self)

    def delete(self):
        taskMgr.remove('chainsawLobbyMusic-%s' % id(self))
        if hasattr(self, 'music') and self.music:
            self.music.stop()
            self.music = None
        DistributedToonInterior.DistributedToonInterior.delete(self)
