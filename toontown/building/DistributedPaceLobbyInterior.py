import random
from toontown.toonbase.ToonBaseGlobal import *
from pandac.PandaModules import *
from toontown.toonbase.ToontownGlobals import *
from direct.distributed import DistributedObject
from direct.directnotify import DirectNotifyGlobal
from toontown.building import ToonInteriorColors
from toontown.building import DistributedToonInterior
from toontown.dna.DNAParser import DNADoor
from toontown.hood import ZoneUtil
from toontown.toon.DistributedNPCToonBase import DistributedNPCToonBase


class DistributedPaceLobbyInterior(DistributedToonInterior.DistributedToonInterior):

    def __init__(self, cr):
        DistributedToonInterior.DistributedToonInterior.__init__(self, cr)
        self.dnaStore = cr.playGame.dnaStore
        self.bellSound = None
        self.bellInside = False
        self.bellPosition = Point3(-29.851, 26.147, 4.043)
        self.bellEnterRadius = 2.0
        self.bellExitRadius = 2.75
        self.bellTaskName = 'paceLobbyBellTask-%s' % id(self)
        self.showerSound = None
        self.showerInside = False
        self.showerTaskName = 'paceLobbyShowerTask-%s' % id(self)

    def generate(self):
        DistributedToonInterior.DistributedToonInterior.generate(self)

    def announceGenerate(self):
        DistributedObject.DistributedObject.announceGenerate(self)
        self.setup()
        taskMgr.doMethodLater(0.1, self.doMusic, 'pacelobbyMusic')
        taskMgr.add(self.checkBell, self.bellTaskName)
        taskMgr.add(self.checkShower, self.showerTaskName)

    def doMusic(self, task):
        base.musicManager.stopAllSounds()
        self.pacelobbyMusicFile = loader.loadMusic('phase_9/audio/bgm/merc/instance_pacesetter_lobby.ogg')
        self.pacelobbyMusic = base.playMusic(self.pacelobbyMusicFile, looping=1)
        return task.done

    def checkBell(self, task):
        if not hasattr(base, 'localAvatar') or not base.localAvatar:
            return task.cont

        toonPos = base.localAvatar.getPos(render)
        distanceSquared = (toonPos - self.bellPosition).lengthSquared()
        enterDistanceSquared = self.bellEnterRadius * self.bellEnterRadius
        exitDistanceSquared = self.bellExitRadius * self.bellExitRadius

        if self.bellInside:
            if distanceSquared >= exitDistanceSquared:
                self.bellInside = False
        elif distanceSquared <= enterDistanceSquared:
            self.bellInside = True
            if self.bellSound:
                self.bellSound.stop()
                self.bellSound.play()

        return task.cont

    def checkShower(self, task):
        if not hasattr(base, 'localAvatar') or not base.localAvatar:
            return task.cont

        pos = base.localAvatar.getPos(render)

        inside = (-6.5 <= pos.getX() <= 6.3 and
                  57.8 <= pos.getY() <= 60.2)

        if self.showerInside:
            if not inside:
                self.showerInside = False
        elif inside:
            self.showerInside = True
            if self.showerSound:
                self.showerSound.stop()
                self.showerSound.play()

        return task.cont

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
        self.interior = loader.loadModel('phase_8/models/areas/ttcc_int_psetter_lobby.bam')
        self.interior.reparentTo(render)
        self.bellSound = loader.loadSfx('phase_5/audio/sfx/ttcc_int_psetter_bell.ogg')
        self.showerSound = loader.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_bonus.ogg')
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

    def stopPaceLobbyMusic(self):
        base.musicManager.stopAllSounds()

        if hasattr(self, 'pacelobbyMusic') and self.pacelobbyMusic:
            try:
                self.pacelobbyMusic.stop()
            except:
                pass
            self.pacelobbyMusic = None

        if hasattr(self, 'pacelobbyMusicFile') and self.pacelobbyMusicFile:
            try:
                self.pacelobbyMusicFile.stop()
            except:
                pass
            self.pacelobbyMusicFile = None

    def disable(self):
        taskMgr.remove(self.bellTaskName)
        taskMgr.remove(self.showerTaskName)
        taskMgr.remove('pacelobbyMusic')
        self.bellInside = False
        self.stopPaceLobbyMusic()

        if self.bellSound:
            self.bellSound.stop()
            self.bellSound = None
        if self.showerSound:
            self.showerSound.stop()
            self.showerSound = None

        DistributedToonInterior.DistributedToonInterior.disable(self)

    def delete(self):
        taskMgr.remove(self.bellTaskName)
        taskMgr.remove(self.showerTaskName)
        taskMgr.remove('pacelobbyMusic')
        self.stopPaceLobbyMusic()
        DistributedToonInterior.DistributedToonInterior.delete(self)
