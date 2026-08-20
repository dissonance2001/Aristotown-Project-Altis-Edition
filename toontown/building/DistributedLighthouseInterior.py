from __future__ import absolute_import
from toontown.toonbase.ToonBaseGlobal import *
from panda3d.core import *
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from direct.distributed.ClockDelta import *
from toontown.toonbase import ToontownGlobals
from . import ToonInterior
from .DistributedToonInterior import DistributedToonInterior
from . import ToonInteriorColors
import random
from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
import random
from toontown.hood import ZoneUtil
from toontown.char import Char
from toontown.quest import QuestParser
from toontown.dna.DNAParser import DNADoor
from toontown.hood import ZoneUtil
from six.moves import range

class DistributedLighthouseInterior(DistributedToonInterior):

    def __init__(self, cr):
        DistributedToonInterior.__init__(self, cr)

    def setup(self):
        self.dnaStore = base.cr.playGame.dnaStore
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        interior = self.randomDNAItem('TI_lighthouse', self.dnaStore.findNode)
        self.interior = interior.copyTo(render)
        hoodId = ZoneUtil.getCanonicalHoodId(self.zoneId)
        self.colors = ToonInteriorColors.colors[hoodId]
        self.replaceRandomInModel(self.interior)
        self.setupDoors()
        del self.colors
        del self.dnaStore
        del self.randomGenerator
        self.interior.flattenMedium()
        locators = interior.find("**/locators")

        self.windowView = loader.loadModel("phase_5.5/models/estate/tropicView")
        windowViewOrigin = locators.find("**/windowView_origin")
        self.windowView.reparentTo(windowViewOrigin)
        self.windowView.wrtReparentTo(render)
        del windowViewOrigin

        self.boatBed = loader.loadModel("phase_5.5/models/estate/UWBoatBed")
        boatBedOrigin = locators.find("**/boatBed_origin")
        self.boatBed.reparentTo(boatBedOrigin)
        self.boatBed.wrtReparentTo(render)
        del boatBedOrigin

        self.wallShark = loader.loadModel("phase_5.5/models/estate/UWhammerhead")
        wallSharkOrigin = locators.find("**/wallShark_origin")
        self.wallShark.reparentTo(wallSharkOrigin)
        self.wallShark.wrtReparentTo(render)
        del wallSharkOrigin

        self.wallFish = loader.loadModel("phase_5.5/models/estate/UWswordFish")
        wallFishOrigin = locators.find("**/wallFish_origin")
        self.wallFish.reparentTo(wallFishOrigin)
        self.wallFish.wrtReparentTo(render)
        del wallFishOrigin


        self.shellVace1 = loader.loadModel("phase_5.5/models/estate/UWshellVase")
        self.shellVace2 = loader.loadModel("phase_5.5/models/estate/UWshellVase")
        shellVaceOrigin1 = locators.find("**/shellVase_origin_1")
        shellVaceOrigin2 = locators.find("**/shellVase_origin_2")
        self.shellVace1.reparentTo(shellVaceOrigin1)
        self.shellVace2.reparentTo(shellVaceOrigin2)
        self.shellVace1.wrtReparentTo(render)
        self.shellVace2.wrtReparentTo(render)
        del shellVaceOrigin1
        del shellVaceOrigin2


        self.coralPot = loader.loadModel("phase_5.5/models/estate/UWcoralVase")
        coralPotOrigin = locators.find("**/coralPot_origin")
        self.coralPot.reparentTo(coralPotOrigin)
        self.coralPot.wrtReparentTo(render)
        del coralPotOrigin

        self.clothRack = loader.loadModel("phase_5.5/models/estate/UWcoralClothRack")
        clothRackOrigin = locators.find("**/clothRack_origin")
        self.clothRack.reparentTo(clothRackOrigin)
        self.clothRack.wrtReparentTo(render)
        del clothRackOrigin

        del locators

    def chooseDoor(self):
        doorModelName = 'door_double_round_ul'
        if doorModelName[-1:] == 'r':
            doorModelName = doorModelName[:-1] + 'l'
        else:
            doorModelName = doorModelName[:-1] + 'r'
        door = self.dnaStore.findNode(doorModelName)
        return door

    def setupDoors(self):
        self.randomGenerator = random.Random()
        self.randomGenerator.seed(self.zoneId)
        self.colors = ToonInteriorColors.colors[ToontownGlobals.ToontownCentral]
        door = self.chooseDoor()
        doorOrigins = render.findAllMatches('**/door_origin*')
        numDoorOrigins = doorOrigins.getNumPaths()
        for npIndex in range(numDoorOrigins):
            doorOrigin = doorOrigins[npIndex]
            doorOriginNPName = doorOrigin.getName()
            doorOriginIndexStr = doorOriginNPName[len('door_origin_'):]
            newNode = ModelNode('door_' + doorOriginIndexStr)
            newNodePath = NodePath(newNode)
            newNodePath.reparentTo(self.interior)
            doorNP = door.copyTo(newNodePath)
            doorOrigin.setScale(0.8, 0.8, 0.8)
            doorOrigin.setPos(doorOrigin, 0, -0.025, 0)
            doorColor = self.randomGenerator.choice(self.colors['TI_door'])
            triggerId = str(self.block) + '_' + doorOriginIndexStr
            DNADoor.setupDoor(doorNP, newNodePath, doorOrigin, self.dnaStore, triggerId, doorColor)
            doorFrame = doorNP.find('door_*_flat')
            doorFrame.setColor(doorColor)

    def disable(self):
        self.enterOff()
        DistributedToonInterior.disable(self)

    def delete(self):
        self.windowView.removeNode()
        del self.windowView

        self.boatBed.removeNode()
        del self.boatBed

        self.wallShark.removeNode()
        del self.wallShark

        self.wallFish.removeNode()
        del self.wallFish

        self.shellVace1.removeNode()
        del self.shellVace1
        self.shellVace2.removeNode()
        del self.shellVace2

        self.coralPot.removeNode()
        del self.coralPot

        self.clothRack.removeNode()
        del self.clothRack

        DistributedToonInterior.delete(self)
    
