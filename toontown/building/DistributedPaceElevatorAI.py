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

        self.fsm.request('closed')

        taskMgr.remove(self.uniqueName('pace-ride'))
        taskMgr.doMethodLater(
            self.RideDuration,
            self.finishPaceRide,
            self.uniqueName('pace-ride')
        )

    def enterClosed(self):
        DistributedElevatorExtAI.DistributedElevatorExtAI.enterClosed(self)

    def finishPaceRide(self, task):
        try:
            bossZone = self.bldg.createBossOffice(self.seats)
        except Exception as error:
            self.notify.warning(
                'Pace ride could not create boss destination: %s' % error
            )
            self.fsm.request('opening')
            return Task.done

        if not bossZone:
            self.notify.warning(
                'Pace boss manager returned an invalid zone.'
            )
            self.fsm.request('opening')
            return Task.done

        for seatIndex in xrange(len(self.seats)):
            avId = self.seats[seatIndex]

            if avId:
                self.sendUpdateToAvatarId(
                    avId,
                    'setBossOfficeZoneForce',
                    [bossZone]
                )

                self.clearFullNow(seatIndex)

        self.fsm.request('opening')
        return Task.done

    def delete(self):
        taskMgr.remove(self.uniqueName('pace-ride'))
        DistributedBossElevatorAI.DistributedBossElevatorAI.delete(self)
