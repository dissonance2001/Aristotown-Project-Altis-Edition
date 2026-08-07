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

        # Major Player Place can host multiple custom/Kudos minibosses.
        # The global InstanceZoneManagerAI owns their temporary zones; this
        # interior only owns the entrance objects that route players to them.
        self.sigilvators = {}
        self.sigilvator = None  # compatibility alias for High Roller
        self.majorPlayerLobbyManager = getattr(
            self.air, 'instanceZoneManager', None)

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createSigilvators()

    def createSigilvators(self):
        self._createSigilvator(
            MajorPlayerInstanceGlobals.HIGH_ROLLER,
            DistributedHighRollerSigilvatorAI)
        self.sigilvator = self.sigilvators.get(
            MajorPlayerInstanceGlobals.HIGH_ROLLER)

    def _createSigilvator(self, instanceId, sigilvatorClass):
        if instanceId in self.sigilvators:
            return self.sigilvators[instanceId]

        sigilvator = sigilvatorClass(
            self.air, self, ToontownGlobals.MajorPlayerLobby)
        sigilvator.generateWithRequired(self.zoneId)
        self.sigilvators[instanceId] = sigilvator
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
