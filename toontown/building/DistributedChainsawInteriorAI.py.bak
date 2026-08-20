from direct.directnotify import DirectNotifyGlobal

from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.building.DistributedChainsawSigilvatorAI import DistributedChainsawSigilvatorAI
from toontown.instances import InstanceGlobals
from toontown.toonbase import ToontownGlobals


class DistributedChainsawInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedChainsawInteriorAI')

    def __init__(self, blockNumber, air, zoneId, building):
        DistributedToonInteriorAI.__init__(
            self, blockNumber, air, zoneId, building)
        self.chainsawSigilvator = None

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createChainsawSigilvator()

    def createChainsawSigilvator(self):
        if self.chainsawSigilvator:
            return self.chainsawSigilvator
        self.chainsawSigilvator = DistributedChainsawSigilvatorAI(
            self.air, self, ToontownGlobals.ChainsawLobby)
        self.chainsawSigilvator.generateWithRequired(self.zoneId)
        return self.chainsawSigilvator

    def createBossOffice(self, avIdList, instanceId=None):
        manager = getattr(self.air, 'instanceZoneManager', None)
        if manager is None:
            self.notify.warning(
                'Cannot create Chainsaw instance: InstanceZoneManagerAI '
                'is unavailable.')
            return 0
        return manager.createInstance(avIdList, InstanceGlobals.CHAINSAW)

    def delete(self):
        if self.chainsawSigilvator:
            self.chainsawSigilvator.requestDelete()
            self.chainsawSigilvator = None
        DistributedToonInteriorAI.delete(self)
