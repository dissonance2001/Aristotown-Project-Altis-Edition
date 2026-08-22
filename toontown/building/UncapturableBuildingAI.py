from direct.directnotify import DirectNotifyGlobal
from toontown.building import DoorTypes
from toontown.building.DistributedDoorAI import DistributedDoorAI
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.interior.ToonInteriorClassesAI import CustomToonInteriors
from toontown.toonbase import ToontownGlobals


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
        self.interior.requestDelete()
        del self.interior

    def setup(self, blockNumber):
        # Prefer a registered custom interior, otherwise fall back to the generic one
        if self.interiorZone in CustomToonInteriors:
            self.interior = CustomToonInteriors[self.interiorZone](
                blockNumber, self.air, self.interiorZone, self)
        else:
            self.interior = DistributedToonInteriorAI(
                blockNumber, self.air, self.interiorZone, self)

        self.interior.generateWithRequired(self.interiorZone)

        # Door setup
        if self.interiorZone in (
            ToontownGlobals.SchoolHouse,
            ToontownGlobals.DerrickLobby,
            ToontownGlobals.DerrickLobbyWelcomeValley,
            ToontownGlobals.PizzariaInterior,
            ToontownGlobals.MajorPlayerLobby,
            ToontownGlobals.PacesetterLobby,
            9613,                       # Pacesetter safety
        ):
            extType = DoorTypes.EXT_STANDARD
            intType = DoorTypes.INT_STANDARD
        else:
            extType = DoorTypes.EXT_UNCAP
            intType = DoorTypes.INT_STANDARD

        self.outsideDoor0 = DistributedDoorAI(self.air, blockNumber, extType, doorIndex=0)
        self.insideDoor0 = DistributedDoorAI(self.air, blockNumber, intType, doorIndex=0)

        self.outsideDoor0.zoneId = self.exteriorZone
        self.insideDoor0.zoneId = self.interiorZone
        self.outsideDoor0.generateWithRequired(self.exteriorZone)
        self.insideDoor0.generateWithRequired(self.interiorZone)
        self.outsideDoor0.sendUpdate('setDoorIndex', [self.outsideDoor0.getDoorIndex()])
        self.insideDoor0.sendUpdate('setDoorIndex', [self.insideDoor0.getDoorIndex()])
        self.outsideDoor0.setOtherDoor(self.insideDoor0)
        self.insideDoor0.setOtherDoor(self.outsideDoor0)

    def isSuitBlock(self):
        return 0

    def isSuitBuilding(self):
        return 0

    def isCogdo(self):
        return 0

    def isEstablishedSuitBlock(self):
        return 0