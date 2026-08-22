from toontown.groups.GroupEnums import GroupType
from toontown.instances.elevators.mercs.DistributedInstanceMercSigilvatorAI import DistributedInstanceMercSigilvatorAI
from toontown.building import ElevatorConstants


class DistributedPrethinkerSigilvatorAI(DistributedInstanceMercSigilvatorAI):
    base_elevator_time = ElevatorConstants.ElevatorData[ElevatorConstants.ELEVATOR_INSTANCE_MERC_SIGIL]['countdown']
    groupType = GroupType.Prethinker

    @property
    def closeTime(self):
        return 6.0
