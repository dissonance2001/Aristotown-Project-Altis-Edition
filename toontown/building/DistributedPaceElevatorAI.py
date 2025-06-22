from toontown.building.ElevatorConstants import *
from toontown.building import DistributedBossElevatorAI

class DistributedPaceElevatorAI(DistributedBossElevatorAI.DistributedBossElevatorAI):

    def __init__(self, air, bldg, zone, antiShuffle = 0, minLaff = 0):
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=0)
        self.type = ELEVATOR_PACE
        self.countdownTime = ElevatorData[self.type]['countdown']