from direct.directnotify import DirectNotifyGlobal
from panda3d.core import *
from toontown.building import FADoorCodes, DoorTypes
from toontown.building.DistributedDoorAI import DistributedDoorAI
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedChainsawInteriorAI import DistributedChainsawInteriorAI
from toontown.building.DistributedDungeonInteriorAI import DistributedDungeonInteriorAI
from toontown.building.DistributedGagshopInteriorAI import DistributedGagshopInteriorAI
from toontown.building.DistributedPetshopInteriorAI import DistributedPetshopInteriorAI
from toontown.building.DistributedLighthouseInteriorAI import DistributedLighthouseInteriorAI
from toontown.building.DistributedDerrickmanInteriorAI import DistributedDerrickmanInteriorAI
from toontown.building.DistributedPizzeriaInteriorAI import DistributedPizzeriaInteriorAI
from toontown.building.DistributedMajorPlayerInteriorAI import DistributedMajorPlayerInteriorAI
from toontown.building.DistributedPaceLobbyInteriorAI import DistributedPaceLobbyInteriorAI
from toontown.hood import ZoneUtil
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals
if __debug__:
    import pdb

class UncapturableBuildingAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('UncapturableBuildingAI')

    def __init__(self, air, exteriorZone, interiorZone, blockNumber):
        self.air = air
        self.exteriorZone = exteriorZone
        self.interiorZone = interiorZone
        self.savedBy = []
        self.setup(blockNumber)

    def cleanup(self):
        self.outsideDoor0.requestDelete()
        self.insideDoor0.requestDelete()
        del self.outsideDoor0
        del self.insideDoor0
        if self.interiorZone == ToontownGlobals.Lighthouse:
            self.outsideDoor1.requestDelete()
            self.insideDoor1.requestDelete()
            del self.outsideDoor1
            del self.insideDoor1
        self.interior.requestDelete()
        del self.interior

    def setup(self, blockNumber):
        if self.interiorZone == ToontownGlobals.ChainsawLobby:
            self.interior = DistributedChainsawInteriorAI(blockNumber, self.air, self.interiorZone, self)
        elif self.interiorZone == ToontownGlobals.Dungeon:
            self.interior = DistributedDungeonInteriorAI(blockNumber, self.air, self.interiorZone, self)
        elif self.interiorZone == ToontownGlobals.OTGagShop or self.interiorZone == ToontownGlobals.OZGagShop:
            self.interior = DistributedGagshopInteriorAI(blockNumber, self.air, self.interiorZone)
        elif self.interiorZone == ToontownGlobals.OTPetShop or self.interiorZone == ToontownGlobals.OZPetShop:
            self.interior = DistributedPetshopInteriorAI(blockNumber, self.air, self.interiorZone)
        elif self.interiorZone == ToontownGlobals.Lighthouse:
            self.interior = DistributedLighthouseInteriorAI(blockNumber, self.air, self.interiorZone, self)
        elif self.interiorZone == ToontownGlobals.DerrickLobby or self.interiorZone == ToontownGlobals.DerrickLobbyWelcomeValley:
            self.interior = DistributedDerrickmanInteriorAI(blockNumber, self.air, self.interiorZone, self)
        elif self.interiorZone == ToontownGlobals.PizzariaInterior:
            self.interior = DistributedPizzeriaInteriorAI(blockNumber, self.air, self.interiorZone, self)
        elif self.interiorZone == ToontownGlobals.MajorPlayerLobby:
            self.interior = DistributedMajorPlayerInteriorAI(blockNumber, self.air, self.interiorZone, self)
        elif self.interiorZone == ToontownGlobals.PacesetterLobby:
            self.interior = DistributedPaceLobbyInteriorAI(blockNumber, self.air, self.interiorZone, self)
        else:
            self.interior = DistributedToonInteriorAI(blockNumber, self.air, self.interiorZone, self)
        self.interior.generateWithRequired(self.interiorZone)
        if self.interiorZone in [ToontownGlobals.SchoolHouse, ToontownGlobals.DerrickLobby, ToontownGlobals.DerrickLobbyWelcomeValley, ToontownGlobals.PizzariaInterior, ToontownGlobals.MajorPlayerLobby, ToontownGlobals.PacesetterLobby]:
            self.outsideDoor0 = DistributedDoorAI(self.air, blockNumber, DoorTypes.EXT_STANDARD, doorIndex=0)
            self.insideDoor0 = DistributedDoorAI(self.air, blockNumber, DoorTypes.INT_STANDARD, doorIndex=0)
        else:
            self.outsideDoor0 = DistributedDoorAI(self.air, blockNumber, DoorTypes.EXT_UNCAP, doorIndex=0)
            if self.interiorZone == ToontownGlobals.Lighthouse:
                self.insideDoor0 = DistributedDoorAI(self.air, blockNumber, DoorTypes.INT_HQ, doorIndex=0)
            else:
                self.insideDoor0 = DistributedDoorAI(self.air, blockNumber, DoorTypes.INT_STANDARD, doorIndex=0)
        self.outsideDoor0.zoneId = self.exteriorZone
        self.insideDoor0.zoneId = self.interiorZone
        self.outsideDoor0.generateWithRequired(self.exteriorZone)
        self.insideDoor0.generateWithRequired(self.interiorZone)
        self.outsideDoor0.sendUpdate('setDoorIndex', [self.outsideDoor0.getDoorIndex()])
        self.insideDoor0.sendUpdate('setDoorIndex', [self.insideDoor0.getDoorIndex()])
        self.outsideDoor0.setOtherDoor(self.insideDoor0)
        self.insideDoor0.setOtherDoor(self.outsideDoor0)
        if self.interiorZone == ToontownGlobals.Lighthouse:
            self.outsideDoor1 = DistributedDoorAI(self.air, blockNumber, DoorTypes.EXT_UNCAP, doorIndex=1)
            self.insideDoor1 = DistributedDoorAI(self.air, blockNumber, DoorTypes.INT_HQ, doorIndex=1)
            self.outsideDoor1.zoneId = self.exteriorZone
            self.insideDoor1.zoneId = self.interiorZone
            self.outsideDoor1.generateWithRequired(self.exteriorZone)
            self.insideDoor1.generateWithRequired(self.interiorZone)
            self.outsideDoor1.sendUpdate('setDoorIndex', [self.outsideDoor1.getDoorIndex()])
            self.insideDoor1.sendUpdate('setDoorIndex', [self.insideDoor1.getDoorIndex()])
            self.outsideDoor1.setOtherDoor(self.insideDoor1)
            self.insideDoor1.setOtherDoor(self.outsideDoor1)

    def isSuitBlock(self):
        return 0

    def isSuitBuilding(self):
        return 0

    def isCogdo(self):
        return 0

    def isEstablishedSuitBlock(self):
        return 0