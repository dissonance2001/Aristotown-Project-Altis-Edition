from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal

from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI
from toontown.instances.elevators.mercs.DistributedPlutocratSigilvatorAI import DistributedPlutocratSigilvatorAI
from toontown.instances import InstanceGlobals
from toontown.toonbase import ToontownGlobals


class DistributedPizzeriaInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedPizzeriaInteriorAI')
    ElevatorClass = DistributedPlutocratSigilvatorAI

    def __init__(self, blockNumber, air, zoneId, building):
        DistributedToonInteriorAI.__init__(
            self, blockNumber, air, zoneId, building)
        self.plutocratSigilvator = None

    def generate(self):
        DistributedToonInteriorAI.generate(self)
        self.createPlutocratSigilvator()

    def createPlutocratSigilvator(self):
        if self.plutocratSigilvator:
            return self.plutocratSigilvator
        self.plutocratSigilvator = self.ElevatorClass(
            self.air, self, ToontownGlobals.PizzariaInterior)
        self.plutocratSigilvator.generateWithRequired(self.zoneId)
        return self.plutocratSigilvator

    def createBossOffice(self, avIdList, instanceId=None):
        manager = getattr(self.air, 'instanceZoneManager', None)
        if manager is None:
            self.notify.warning(
                'Cannot create Plutocrat instance: InstanceZoneManagerAI is unavailable.')
            return 0
        if not manager.hasInstanceType(InstanceGlobals.PLUTOCRAT):
            self.notify.warning(
                'Plutocrat battle controller is not registered yet.')
            return 0
        return manager.createInstance(avIdList, InstanceGlobals.PLUTOCRAT)

    def delete(self):
        if self.plutocratSigilvator:
            self.plutocratSigilvator.requestDelete()
            self.plutocratSigilvator = None
        DistributedToonInteriorAI.delete(self)
