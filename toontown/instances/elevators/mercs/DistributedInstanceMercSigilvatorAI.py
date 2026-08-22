from toontown.building.ElevatorConstants import *
from toontown.instances.elevators.mercs.DistributedInstanceMercElevatorAI import MercEnum2GroupType
from toontown.building.DistributedSigilvatorAI import DistributedSigilvatorAI
from toontown.instances.InstanceGlobals import *
from toontown.instances.mercs.InstanceMercGlobals import MercDefinition, mercZoneIdToMercDefinition, mercDefinitionToEnum
#from toontown.quest3.base.QuestReference import QuestId


class DistributedInstanceMercSigilvatorAI(DistributedSigilvatorAI):
    # By default, these sigilvators have an inaccessible quest.
    #questRequired = True

    def __init__(self, air, bldg, zone, antiShuffle=0, minLaff=0, mercDef=None):
        DistributedSigilvatorAI.__init__(self, air, bldg, zone, antiShuffle=antiShuffle, minLaff=minLaff)
        self.type = ELEVATOR_INSTANCE_MERC_SIGIL
        self.bossType = INSTANCE_MERC
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.mercDef = mercDef
       # if mercDef is None:
        #    self.mercDef = mercZoneIdToMercDefinition(zone)
       # self.mercDefEnum = None
       # self.setMercDefEnum(mercDefinitionToEnum(self.mercDef))
        #self.questRequired = self.mercDef.requiredTaskID

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
            for seatIndex in xrange(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setBossOfficeZone', [bossZone])
                    self.clearFullNow(seatIndex)

        else:
            self.notify.warning('The elevator left, but was empty.')
        self.fsm.request('closed')
