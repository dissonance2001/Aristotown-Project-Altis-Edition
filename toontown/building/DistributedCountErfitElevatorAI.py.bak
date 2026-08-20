from toontown.building.ElevatorConstants import *
from toontown.building import DistributedElevatorExtAI
from toontown.instances import InstanceGlobals

class DistributedCountErfitElevatorAI(DistributedElevatorExtAI.DistributedElevatorExtAI):

    def __init__(self, air, zone, antiShuffle=0, minLaff=0):
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(
            self,
            air,
            self,
            numSeats=4,
            antiShuffle=antiShuffle,
            minLaff=minLaff
        )
        self.zone = zone
        self.bldgDoId = 0
        self.type = ELEVATOR_ERFIT
        self.countdownTime = ElevatorData[self.type]['countdown']

    def getDoId(self):
        return 0

    def _createInterior(self):
        manager = getattr(self.air, 'instanceZoneManager', None)
        if manager is None:
            self.notify.warning('Count Erfit InstanceZoneManagerAI is unavailable.')
            return

        bossZone = manager.createInstance(self.seats, InstanceGlobals.COUNT_ERFIT)
        if not bossZone:
            self.notify.warning('Count Erfit instance manager returned an invalid zone.')
            return

        for avId in self.seats:
            if avId:
                self.sendUpdateToAvatarId(avId, 'setBossOfficeZoneForce', [bossZone])
