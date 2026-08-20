from __future__ import absolute_import
import random

from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from toontown.building import DistributedToonInterior
from toontown.building import ToonInteriorColors
from toontown.dna.DNAParser import DNADoor
from toontown.hood import ZoneUtil


class DistributedChainsawInterior(DistributedToonInterior.DistributedToonInterior):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedChainsawInterior')

    def __init__(self, cr):
        DistributedToonInterior.DistributedToonInterior.__init__(self, cr)
        self.chainsawBossDoor = None

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)

        self.interior = loader.loadModel(
            'phase_6/models/areas/ttcc_int_cc_lobby.bam')
        self.interior.reparentTo(render)

        bossDoorOrigin = self.interior.find('**/boss_door_origin')
        if bossDoorOrigin.isEmpty():
            bossDoorOrigin = render.find('**/boss_door_origin')
        if not bossDoorOrigin.isEmpty():
            self.chainsawBossDoor = loader.loadModel(
                'phase_12/models/modules/bossbot_door.bam')
            self.chainsawBossDoor.reparentTo(bossDoorOrigin)
            self.chainsawBossDoor.setPosHpr(0, 0, 0, 0, 0, 0)
        else:
            self.notify.warning(
                'Chainsaw lobby is missing boss_door_origin.')

        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)

        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'

        door = self.dnaStore.findNode(doorModelName)
        doorOrigin = self.interior.find('**/door_origin;+s')
        if doorOrigin.isEmpty():
            doorOrigin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(doorOrigin)
        doorOrigin.setScale(0.8, 0.8, 0.8)
        doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
        color = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(
            doorNP, self.interior, doorOrigin, self.dnaStore,
            str(self.block), color)
        doorFrame = doorNP.find('door_*_flat')
        if not doorFrame.isEmpty():
            doorFrame.wrtReparentTo(self.interior)
            doorFrame.setColor(color)

        del self.colors
        del self.dnaStore
        del self.randomGenerator

    def disable(self):
        if (self.chainsawBossDoor is not None and
                not self.chainsawBossDoor.isEmpty()):
            self.chainsawBossDoor.removeNode()
        self.chainsawBossDoor = None
        DistributedToonInterior.DistributedToonInterior.disable(self)

    def delete(self):
        DistributedToonInterior.DistributedToonInterior.delete(self)
