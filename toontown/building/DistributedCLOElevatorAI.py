from toontown.building.ElevatorConstants import *
from toontown.building import DistributedBossElevatorAI, ElevatorConstants
from typing import TYPE_CHECKING

#from toontown.groups.GroupEnums import GroupType

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


class DistributedCLOElevatorAI(DistributedBossElevatorAI.DistributedBossElevatorAI):
    base_elevator_time = ElevatorConstants.ElevatorData[ElevatorConstants.ELEVATOR_CLO]['countdown']
   # groupType = GroupType.CLO

    def __init__(self, air, bldg, zone, antiShuffle = 0, minLaff = 0):
        """
        :type air: ToontownAIRepository
        """
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(
            self, air, bldg, zone, antiShuffle = antiShuffle, minLaff = minLaff
        )
        self.type = ELEVATOR_CLO
        self.countdownTime = ElevatorData[self.type]['countdown']
