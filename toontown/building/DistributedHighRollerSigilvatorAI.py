from toontown.building.DistributedSigilvatorAI import DistributedSigilvatorAI


class DistributedHighRollerSigilvatorAI(DistributedSigilvatorAI):

    @property
    def closeTime(self):
        return 6.0
