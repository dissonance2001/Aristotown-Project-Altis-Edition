from direct.task import Task
from toontown.building.ElevatorConstants import *
from toontown.building import DistributedBossElevatorAI
from toontown.building import DistributedElevatorExtAI


class DistributedPaceElevatorAI(
        DistributedBossElevatorAI.DistributedBossElevatorAI):

    RideDuration = 8.0

    def __init__(self, air, bldg, zone, antiShuffle=0, minLaff=0):
        DistributedBossElevatorAI.DistributedBossElevatorAI.__init__(
            self,
            air,
            bldg,
            zone,
            antiShuffle=antiShuffle,
            minLaff=minLaff
        )

        self.type = ELEVATOR_PACE
        self.countdownTime = ElevatorData[self.type]['countdown']

    def elevatorClosed(self):
        if self.countFullSeats() <= 0:
            self.fsm.request('opening')
            return

        try:
            bossZone = self.bldg.createBossOffice(self.seats)
        except Exception as error:
            self.notify.warning(
                'Pacesetter elevator could not create boss destination: %s' %
                error)
            self.fsm.request('opening')
            return

        if not bossZone:
            self.notify.warning(
                'Pacesetter boss manager returned an invalid zone.')
            self.fsm.request('opening')
            return

        for seatIndex in xrange(len(self.seats)):
            avId = self.seats[seatIndex]
            if avId:
                self.sendUpdateToAvatarId(
                    avId,
                    'setBossOfficeZoneForce',
                    [bossZone]
                )
                self.clearFullNow(seatIndex)

        self.fsm.request('closed')

    def enterClosed(self):
        DistributedElevatorExtAI.DistributedElevatorExtAI.enterClosed(self)
        self.fsm.request('opening')

    def delete(self):
        taskMgr.remove(self.uniqueName('pace-ride'))
        DistributedBossElevatorAI.DistributedBossElevatorAI.delete(self)
