from toontown.toonbase.ToonBaseGlobal import *
from panda3d.core import *
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from toontown.toonbase import ToontownGlobals
import ToonInterior
from DistributedToonInterior import DistributedToonInterior
import ToonInteriorColors, random
from direct.directnotify import DirectNotifyGlobal
from toontown.dna.DNAParser import DNADoor
from direct.distributed import DistributedObject
import random
from toontown.hood import ZoneUtil
from toontown.char import Char
from toontown.quest import QuestParser
from toontown.hood import ZoneUtil

class DistributedChainsawInterior(DistributedToonInterior):

    def __init__(self, cr):
        DistributedToonInterior.__init__(self, cr)

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        interior = loader.loadModel('phase_6/models/areas/ttcc_int_cc_lobby.bam')
        self.interior = interior.copyTo(render)
        Chainsawdoor = loader.loadModel('phase_12/models/modules/bossbot_door.bam')
        Chainsawdoor_origin = render.find('**/boss_door_origin')
        Chainsawdoor.reparentTo(Chainsawdoor_origin)
        sigilvator = loader.loadModel('phase_4/models/modules/ttcc_gen_sigil.bam')
        sigilvator_origin = render.find('**/sigilvator_origin')
        sigilvator.reparentTo(sigilvator_origin)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        door_origin = render.find('**/door_origin;+s')
        doorNP = door.copyTo(door_origin)
        door_origin.setScale(0.8, 0.8, 0.8)
        door_origin.setPos(door_origin, 0, -0.025, 0)
        color = self.randomGenerator.choice(self.colors['TI_door'])
        DNADoor.setupDoor(doorNP, self.interior, door_origin, self.dnaStore, str(self.block), color)
        doorFrame = doorNP.find('door_*_flat')
        doorFrame.wrtReparentTo(self.interior)
        doorFrame.setColor(color)
        del self.colors
        del self.dnaStore
        del self.randomGenerator
        self.interior.flattenMedium()

    def disable(self):
        self.enterOff()
        DistributedToonInterior.disable(self)

    def delete(self):
        DistributedToonInterior.delete(self)
    
