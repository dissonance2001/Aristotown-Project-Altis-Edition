from __future__ import absolute_import
from toontown.toonbase.ToonBaseGlobal import *
from pandac.PandaModules import *
from toontown.building.DistributedToonInterior import DistributedToonInterior
from toontown.building import ToonInteriorColors
from toontown.building import MajorPlayerInstanceGlobals
from toontown.dna.DNAParser import DNADoor
from toontown.hood import ZoneUtil
import random


class DistributedMajorPlayerInterior(DistributedToonInterior):

    def __init__(self, cr):
        DistributedToonInterior.__init__(self, cr)
        self.majorPlayerMusic = None
        self.majorPlayerMusicFile = None
        self.majorPlayerMusicTaskName = 'majorPlayerLobbyMusic-%s' % id(self)
        self.sigilvatorOrigin = None
        self.sigilvatorOrigin2 = None
        self.sigilvatorOrigins = {}

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
        DNADoor.setupDoor(doorNP, visualDoorRoot, visualDoorOrigin,
                          self.dnaStore, str(self.block), color)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(visualDoorRoot)
        doorFrame.setColor(color)

        elevatorOrigin = self.interior.find('**/elevator_origin')
        elevator = loader.loadModel('phase_11/models/lawbotHQ/lawbotElevator.bam')
        elevator.reparentTo(elevatorOrigin)

        self.sigilvatorOrigin = elevatorOrigin.attachNewNode(
            'major_player_sigilvator_origin')
        self.sigilvatorOrigin.setPos(0, -70.75, -15.97)
        self.sigilvatorOrigin.setHpr(0, 0, 0)
        self.sigilvatorOrigins[0] = self.sigilvatorOrigin

        self.sigilvatorOrigin2 = elevatorOrigin.attachNewNode(
            'major_player_sigilvator_origin_1')
        self.sigilvatorOrigin2.setPos(self.interior, 30.118, 12.678, 0.025)
        self.sigilvatorOrigin2.setHpr(self.interior, -91.42, 0, 0)
        self.sigilvatorOrigins[1] = self.sigilvatorOrigin2

        del self.colors
        del self.dnaStore
        del self.randomGenerator

        spawnDoorOrigin = self.interior.attachNewNode('door_origin')
        spawnDoorOrigin.setTransform(self.interior, originalDoorTransform)
        spawnDoorOrigin.setH(spawnDoorOrigin, 180)
        spawnDoorOrigin.setY(spawnDoorOrigin, 0.5)

        taskMgr.doMethodLater(0.1, self.__startMajorPlayerMusic,
                              self.majorPlayerMusicTaskName)

    def __startMajorPlayerMusic(self, task):
        base.musicManager.stopAllSounds()
        self.majorPlayerMusicFile = loader.loadMusic(
            'phase_12/audio/bgm/merc/instance_majorplayer_lobby.ogg')
        self.majorPlayerMusic = base.playMusic(
            self.majorPlayerMusicFile, looping=1)
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
        self.sigilvatorOrigin = None
        self.sigilvatorOrigin2 = None
        self.sigilvatorOrigins = {}
        self.enterOff()
        DistributedToonInterior.disable(self)

    def delete(self):
        self.__stopMajorPlayerMusic()
        DistributedToonInterior.delete(self)
