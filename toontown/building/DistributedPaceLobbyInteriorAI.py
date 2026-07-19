from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedPaceElevatorAI import DistributedPaceElevatorAI
from toontown.toonbase import ToontownGlobals


class DistributedPaceLobbyInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedPaceLobbyInteriorAI'
    )

    def __init__(self, blockNumber, air, zoneId, building):
        DistributedToonInteriorAI.__init__(
            self,
            blockNumber,
            air,
            zoneId,
            building
        )
        self.paceElevator = None

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createPaceElevator()

    def createPaceElevator(self):
        if self.paceElevator:
            return

        self.paceElevator = DistributedPaceElevatorAI(
            self.air,
            self,
            ToontownGlobals.PacesetterLobby
        )
        self.paceElevator.generateWithRequired(self.zoneId)

    def createBossOffice(self, avIdList):
        return self.building.createBossOffice(avIdList)

    def delete(self):
        if self.paceElevator:
            self.paceElevator.requestDelete()
            self.paceElevator = None

        DistributedToonInteriorAI.delete(self)
