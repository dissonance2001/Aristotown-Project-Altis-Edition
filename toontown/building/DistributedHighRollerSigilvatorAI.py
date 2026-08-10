from toontown.building.DistributedSigilvatorAI import DistributedSigilvatorAI


class DistributedHighRollerSigilvatorAI(DistributedSigilvatorAI):

    def __init__(self, air, bldg, zone, entranceId=0, antiShuffle=0, minLaff=0):
        DistributedSigilvatorAI.__init__(
            self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=minLaff)
        self.entranceId = int(entranceId)

    def getEntranceId(self):
        return self.entranceId

    def getInstanceId(self):
        from toontown.building import MajorPlayerInstanceGlobals
        if self.entranceId == 1:
            return MajorPlayerInstanceGlobals.VIDEOGRAPHER
        return MajorPlayerInstanceGlobals.HIGH_ROLLER

    @property
    def closeTime(self):
        return 6.0
