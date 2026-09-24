from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedPaceElevatorAI import DistributedPaceElevatorAI
from toontown.building.DistributedHighRollerSigilvatorAI import DistributedHighRollerSigilvatorAI
from toontown.toonbase import ToontownGlobals
from toontown.instances import InstanceGlobals


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
        self.motoroomSigilvator = None
        self.paceCat = None
        self.paceLobbyManager = getattr(
            self.air, 'instanceZoneManager', None)

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createPaceElevator()
        self.createMotoroomSigilvator()

    def createPaceElevator(self):
        if self.paceElevator:
            return

        self.paceElevator = DistributedPaceElevatorAI(
            self.air,
            self,
            ToontownGlobals.PacesetterLobby
        )

        self.paceElevator.generateWithRequired(self.zoneId)

    def createMotoroomSigilvator(self):
        if self.motoroomSigilvator:
            return

        self.motoroomSigilvator = DistributedHighRollerSigilvatorAI(
            self.air,
            self,
            ToontownGlobals.PacesetterLobby,
            2
        )
        self.motoroomSigilvator.generateWithRequired(self.zoneId)

    def createBossOffice(self, avIdList, instanceId=None):
        manager = getattr(self.air, 'instanceZoneManager', None)
        if manager is None:
            self.notify.warning(
                'createBossOffice: InstanceZoneManagerAI is unavailable.'
            )
            return 0

        if instanceId is None:
            instanceId = InstanceGlobals.PACESETTER

        return manager.createInstance(avIdList, instanceId)

    def delete(self):
        if self.paceCat:
            self.paceCat.requestDelete()
            self.paceCat = None

        if self.motoroomSigilvator:
            self.motoroomSigilvator.requestDelete()
            self.motoroomSigilvator = None

        if self.paceElevator:
            self.paceElevator.requestDelete()
            self.paceElevator = None

        self.paceLobbyManager = None
        DistributedToonInteriorAI.delete(self)
