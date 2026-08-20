from __future__ import absolute_import
from toontown.building.ElevatorConstants import *
from toontown.building import DistributedBossElevatorAI

class DistributedMultislackerElevatorAI(DistributedBossElevatorAI.DistributedBossElevatorAI):

    def __init__(self, air, bldg, zone, antiShuffle = 0, minLaff = 0):
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=minLaff)
        self.type = ELEVATOR_VP
        self.countdownTime = ElevatorData[self.type]['countdown']