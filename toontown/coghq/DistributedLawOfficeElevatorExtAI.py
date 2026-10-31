from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.task import Task
from otp.ai.AIBase import *
from toontown.building import DistributedElevatorExtAI
from toontown.building.ElevatorConstants import *
from toontown.toonbase import ToontownGlobals
from toontown.instances import InstanceGlobals

class DistributedLawOfficeElevatorExtAI(DistributedElevatorExtAI.DistributedElevatorExtAI):
    def __init__(self, air, bldg, lawOfficeId, entranceId, antiShuffle = 0, minLaff = 0):
        DistributedElevatorExtAI.DistributedElevatorExtAI.__init__(self, air, bldg, antiShuffle = antiShuffle, minLaff = minLaff)
        self.lawOfficeId = lawOfficeId
        self.entranceId = entranceId

    def getEntranceId(self):
        return self.entranceId

    def checkBoard(self, av):
        if self.entranceId == 4:
            manager = getattr(self.air, 'instanceZoneManager', None)
            if manager is None or not manager.hasInstanceType(InstanceGlobals.SADS):
                return REJECT_NOT_YET_AVAILABLE
        return DistributedElevatorExtAI.DistributedElevatorExtAI.checkBoard(self, av)

    def _createSadsInstance(self, avIdList):
        manager = getattr(self.air, 'instanceZoneManager', None)
        if manager is None:
            self.notify.warning('Sads InstanceZoneManagerAI is unavailable.')
            return 0
        return manager.createInstance(avIdList, InstanceGlobals.SADS)

    def elevatorClosed(self):
        numPlayers = self.countFullSeats()
        if numPlayers > 0:
            if self.entranceId == 4:
                sadsZone = self._createSadsInstance(self.seats)
                if not sadsZone:
                    self.notify.warning('Could not create Sads instance for the fifth Lawfice elevator.')
                    self.fsm.request('opening')
                    return
                for seatIndex, avId in enumerate(self.seats):
                    if avId:
                        self.sendUpdateToAvatarId(avId, 'setLawOfficeInteriorZone', [sadsZone])
                        self.clearFullNow(seatIndex)
            else:
                players = []
                for i in self.seats:
                    if i not in [None, 0]:
                        players.append(i)
                lawOfficeZone = self.bldg.createLawOffice(self.lawOfficeId, self.entranceId, players)
                for seatIndex in range(len(self.seats)):
                    avId = self.seats[seatIndex]
                    if avId:
                        self.sendUpdateToAvatarId(avId, 'setLawOfficeInteriorZone', [lawOfficeZone])
                        self.clearFullNow(seatIndex)
        else:
            self.notify.warning('The elevator left, but was empty.')
        self.fsm.request('closed')

    def enterClosed(self):
        DistributedElevatorExtAI.DistributedElevatorExtAI.enterClosed(self)
        self.fsm.request('opening')

    def sendAvatarsToDestination(self, avIdList):
        if len(avIdList) > 0:
            if self.entranceId == 4:
                officeZone = self._createSadsInstance(avIdList)
            else:
                officeZone = self.bldg.createLawOffice(self.lawOfficeId, self.entranceId, avIdList)
            if not officeZone:
                return
            for avId in avIdList:
                if avId:
                    self.sendUpdateToAvatarId(avId, 'setLawOfficeInteriorZoneForce', [officeZone])
