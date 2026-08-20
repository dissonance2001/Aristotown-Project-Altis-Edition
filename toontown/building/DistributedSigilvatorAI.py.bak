from otp.ai.AIBase import *
from direct.directnotify import DirectNotifyGlobal
from toontown.building.ElevatorConstants import *
from toontown.building import DistributedElevatorAI
from toontown.building import DistributedElevatorExtAI


class DistributedSigilvatorAI(
        DistributedElevatorExtAI.DistributedElevatorExtAI):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedSigilvatorAI')
    ExitTime = TOON_EXIT_SIGIL_TIME

    def __init__(self, air, bldg, zone, antiShuffle=0, minLaff=0):
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(
            self, air, bldg, numSeats=4,
            antiShuffle=antiShuffle, minLaff=minLaff)
        self.zone = zone
        self.type = ELEVATOR_SIGIL
        self.countdownTime = ElevatorData[self.type]['countdown']

    def getInstanceId(self):
        return None

    @property
    def closeTime(self):
        return ElevatorData[self.type]['closeTime']

    @property
    def openTime(self):
        return ElevatorData[self.type]['openTime']

    def enterClosing(self):
        DistributedElevatorAI.DistributedElevatorAI.enterClosing(self)
        taskMgr.doMethodLater(
            self.closeTime, self.elevatorClosedTask,
            self.uniqueName('closing-timer'))

    def enterClosed(self):
        DistributedElevatorExtAI.DistributedElevatorExtAI.enterClosed(self)
        self.fsm.request('opening')

    def enterOpening(self):
        DistributedElevatorAI.DistributedElevatorAI.enterOpening(self)
        taskMgr.doMethodLater(
            self.openTime, self.waitEmptyTask,
            self.uniqueName('opening-timer'))

    def elevatorClosed(self):
        if self.countFullSeats() > 0:
            bossZone = self.bldg.createBossOffice(
                self.seats, self.getInstanceId())
            if not bossZone:
                self.notify.warning(
                    'Unable to create the Major Player miniboss destination zone.')
                self.fsm.request('closed')
                return
            for seatIndex in xrange(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    self.sendUpdateToAvatarId(
                        avId, 'setBossOfficeZone', [bossZone])
                    self.clearFullNow(seatIndex)
        else:
            self.notify.warning('The sigilvator left, but was empty.')
        self.fsm.request('closed')

    def sendAvatarsToDestination(self, avIdList):
        if not avIdList:
            return
        bossZone = self.bldg.createBossOffice(
            avIdList, self.getInstanceId())
        if not bossZone:
            return
        for avId in avIdList:
            if avId:
                self.sendUpdateToAvatarId(
                    avId, 'setBossOfficeZoneForce', [bossZone])

    def delete(self):
        taskMgr.remove(self.uniqueName('closing-timer'))
        taskMgr.remove(self.uniqueName('opening-timer'))
        DistributedElevatorExtAI.DistributedElevatorExtAI.delete(self)
