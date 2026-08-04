from toontown.building.DistributedSigilvatorAI import DistributedSigilvatorAI


class DistributedHighRollerSigilvatorAI(DistributedSigilvatorAI):

    def getInstanceId(self):
        from toontown.building import MajorPlayerInstanceGlobals
        return MajorPlayerInstanceGlobals.HIGH_ROLLER

    @property
    def closeTime(self):
        return 6.0
