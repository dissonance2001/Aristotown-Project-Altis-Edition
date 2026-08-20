from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedHighRollerSigilvatorAI import DistributedHighRollerSigilvatorAI
from toontown.building import MajorPlayerInstanceGlobals
from toontown.toonbase import ToontownGlobals


class DistributedMajorPlayerInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedMajorPlayerInteriorAI')

    def __init__(self, block, air, zoneId, building):
        DistributedToonInteriorAI.__init__(
            self, block, air, zoneId, building)

        self.sigilvators = {}
        self.sigilvator = None
        self.majorPlayerLobbyManager = getattr(
            self.air, 'instanceZoneManager', None)

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createSigilvators()

    def createSigilvators(self):
        self._createSigilvator(
            MajorPlayerInstanceGlobals.HIGH_ROLLER,
            DistributedHighRollerSigilvatorAI, 0)
        self._createSigilvator(
            MajorPlayerInstanceGlobals.VIDEOGRAPHER,
            DistributedHighRollerSigilvatorAI, 1)
        self.sigilvator = self.sigilvators.get(
            (MajorPlayerInstanceGlobals.HIGH_ROLLER, 0))

    def _createSigilvator(self, instanceId, sigilvatorClass, entranceId):
        key = (instanceId, entranceId)
        if key in self.sigilvators:
            return self.sigilvators[key]

        sigilvator = sigilvatorClass(
            self.air, self, ToontownGlobals.MajorPlayerLobby, entranceId)
        sigilvator.generateWithRequired(self.zoneId)
        self.sigilvators[key] = sigilvator
        return sigilvator

    def createBossOffice(self, avIdList, instanceId=None):
        if instanceId is None:
            instanceId = MajorPlayerInstanceGlobals.HIGH_ROLLER

        manager = getattr(self.air, 'instanceZoneManager', None)
        if manager is None:
            self.notify.warning(
                'createBossOffice: InstanceZoneManagerAI is unavailable.')
            return 0

        return manager.createInstance(avIdList, instanceId)

    def delete(self):
        for sigilvator in self.sigilvators.values():
            sigilvator.requestDelete()
        self.sigilvators = {}
        self.sigilvator = None
        self.majorPlayerLobbyManager = None
        DistributedToonInteriorAI.delete(self)
