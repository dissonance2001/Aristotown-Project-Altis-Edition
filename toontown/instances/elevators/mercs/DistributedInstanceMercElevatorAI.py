from toontown.building.ElevatorConstants import *
from toontown.instances.elevators import DistributedInstanceElevatorAI
from toontown.instances.InstanceGlobals import *
from toontown.instances.mercs.InstanceMercGlobals import MercDefinition, mercZoneIdToMercDefinition, \
    mercDefinitionToEnum, \
    MERC_PRETHINKER, MERC_RAINMAKER, MERC_WITCHHUNTER, MERC_MULTISLACKER, MERC_MAJORPLAYER, MERC_PLUTOCRAT, \
    MERC_CHAINSAW, MERC_PACESETTER, MERC_HIGHROLLER
from ....groups.GroupEnums import GroupType
#from ....quest3.base.QuestReference import QuestId


MercEnum2GroupType = {
    MERC_PRETHINKER: GroupType.Prethinker,
    MERC_RAINMAKER: GroupType.Rainmaker,
    MERC_WITCHHUNTER: GroupType.Witchhunter,
    MERC_MULTISLACKER: GroupType.Multislacker,
    MERC_MAJORPLAYER: GroupType.Majorplayer,
    MERC_PLUTOCRAT: GroupType.Plutocrat,
    MERC_CHAINSAW: GroupType.Chainsaw,
    MERC_PACESETTER: GroupType.Pacesetter,
    MERC_HIGHROLLER: GroupType.Highroller,
}


class DistributedInstanceMercElevatorAI(DistributedInstanceElevatorAI.DistributedInstanceElevatorAI):
    base_elevator_time = ElevatorData[ELEVATOR_INSTANCE_MERC]['countdown']
    groupType = [GroupType.Highroller, GroupType.Pacesetter, GroupType.Majorplayer]

    def __init__(self, air, bldg, zone, antiShuffle=0, minLaff=0, mercDef=None):
        DistributedInstanceElevatorAI.DistributedInstanceElevatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=minLaff)
        self.type = ELEVATOR_INSTANCE_MERC
        self.bossType = INSTANCE_MERC
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.mercDef = mercDef
        if mercDef is None:
            self.mercDef = mercZoneIdToMercDefinition(zone)
        self.mercDefEnum = None
        self.setMercDefEnum(mercDefinitionToEnum(self.mercDef))
       # self.questRequired = self.mercDef.requiredTaskID

    def setMercDefEnum(self, enum):
        self.mercDefEnum = enum

    def getMercDefEnum(self):
        return self.mercDefEnum

    def getSpecificGroupType(self):
        return MercEnum2GroupType[self.mercDefEnum]

    def elevatorClosed(self):
        numPlayers = self.countFullSeats()
        if numPlayers > 0:
            bossZone = self.bldg.createBossOffice(self.seats, self.bossType, self.mercDef)

            # temporary debug remove later
            self.notify.warning(
                "DEBUG createBossOffice: returned=%s  bldg=%s  bossType=%s  mercDef=%s"
                % (bossZone, self.bldg.__class__.__name__, self.bossType, self.mercDef)
            )

            for seatIndex in range(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setBossOfficeZone', [bossZone])
                    self.clearFullNow(seatIndex)
        else:
            self.notify.warning('The elevator left, but was empty.')
        self.fsm.request('closed')