from toontown.building.DistributedSigilvatorAI import DistributedSigilvatorAI
from toontown.instances import InstanceGlobals


class DistributedChainsawSigilvatorAI(DistributedSigilvatorAI):
    def getInstanceId(self):
        return InstanceGlobals.CHAINSAW

    @property
    def closeTime(self):
        return 4.0
