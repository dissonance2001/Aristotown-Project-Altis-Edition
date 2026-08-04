from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedHighRollerSigilvatorAI import DistributedHighRollerSigilvatorAI
from toontown.building import MajorPlayerInstanceGlobals
from toontown.coghq.LobbyManagerAI import LobbyManagerAI
from toontown.suit import DistributedHighRollerBossAI
from toontown.toonbase import ToontownGlobals


class DistributedMajorPlayerInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedMajorPlayerInteriorAI')

    def __init__(self, block, air, zoneId, building):
        DistributedToonInteriorAI.__init__(
            self, block, air, zoneId, building)

        # Major Player Place is intended to contain two minibosses.  Keep both
        # the managers and the sigilvators keyed by instance id so the second
        # boss can be registered later without creating another hood or HQ.
        self.sigilvators = {}
        self.sigilvator = None  # compatibility alias for High Roller
        self.createdInstanceManagerIds = []

        managers = getattr(self.air, 'majorPlayerInstanceManagers', None)
        if managers is None:
            managers = {}
            self.air.majorPlayerInstanceManagers = managers
        self.instanceManagers = managers

        self._ensureInstanceManager(
            MajorPlayerInstanceGlobals.HIGH_ROLLER,
            DistributedHighRollerBossAI.DistributedHighRollerBossAI)

        # Compatibility alias retained for existing local debugging code.
        self.majorPlayerLobbyManager = self.instanceManagers.get(
            MajorPlayerInstanceGlobals.HIGH_ROLLER)

    def _ensureInstanceManager(self, instanceId, bossConstructor):
        manager = self.instanceManagers.get(instanceId)
        if manager is not None:
            return manager

        manager = LobbyManagerAI(
            self.air, bossConstructor, ToontownGlobals.MajorPlayerLobby)
        manager.generateWithRequired(ToontownGlobals.MajorPlayerLobby)
        self.instanceManagers[instanceId] = manager
        self.createdInstanceManagerIds.append(instanceId)
        return manager

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

        manager = self.instanceManagers.get(instanceId)
        if manager is None:
            self.notify.warning(
                'createBossOffice: no Major Player manager for %r.' %
                instanceId)
            return 0
        return manager.createBossOffice(avIdList)

    def delete(self):
        for sigilvator in self.sigilvators.values():
            sigilvator.requestDelete()
        self.sigilvators = {}
        self.sigilvator = None

        for instanceId in self.createdInstanceManagerIds:
            manager = self.instanceManagers.get(instanceId)
            if manager is not None:
                manager.requestDelete()
                del self.instanceManagers[instanceId]
        self.createdInstanceManagerIds = []

        if not self.instanceManagers:
            managers = getattr(
                self.air, 'majorPlayerInstanceManagers', None)
            if managers is self.instanceManagers:
                del self.air.majorPlayerInstanceManagers

        self.majorPlayerLobbyManager = None
        DistributedToonInteriorAI.delete(self)
