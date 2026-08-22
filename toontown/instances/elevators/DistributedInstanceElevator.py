from toontown.building.ElevatorUtils import *
from toontown.building import DistributedElevator
from toontown.building import DistributedElevatorExt
from toontown.toonbase import TTLocalizer, ToontownGlobals


class DistributedInstanceElevator(DistributedElevatorExt.DistributedElevatorExt):
    def __init__(self, cr):
        DistributedElevatorExt.DistributedElevatorExt.__init__(self, cr)
        self.type = ELEVATOR_DERRICK_MAN
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.elevatorModel = loader.loadModel('phase_9/models/cogHQ/cogHQ_elevator')
        self.irisTrack = None

    def disable(self):
        DistributedElevator.DistributedElevator.disable(self)

    def generate(self):
        DistributedElevatorExt.DistributedElevatorExt.generate(self)

    def delete(self):
        if self.irisTrack:
            self.irisTrack.pause()
            self.irisTrack = None
        self.elevatorModel.removeNode()
        del self.elevatorModel
        DistributedElevatorExt.DistributedElevatorExt.delete(self)

    def setupElevator(self):
        icon = self.elevatorModel.find('**/big_frame/')
        icon.hide()
        self.leftDoor = self.elevatorModel.find('**/left-door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        geom = base.cr.playGame.hood.loader.geom
        locator = geom.find('**/elevator_locator')
        self.elevatorModel.reparentTo(locator)
        self.elevatorModel.setH(180)
        DistributedElevator.DistributedElevator.setupElevator(self)

    def setBldgDoId(self, bldgDoId):
        self.bldgDoId = bldgDoId
        self.bldg = None
        self.setupElevator()

    def getElevatorModel(self):
        return self.elevatorModel

    def gotBldg(self, buildingList):
        return DistributedElevator.DistributedElevator.gotBldg(self, buildingList)

    def getZoneId(self):
        """
        :returns: the current zone ID.
        :rtype: int
        """
        return 0

    def __doorsClosed(self, zoneId):
        pass

    def setBossOfficeZone(self, zoneId):
        if self.localToonOnBoard:
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {'loader': 'cogHQLoader',
                          'how': 'Movie',
                          'where': 'instanceBattle',
                          'hoodId': hoodId,
                          'zoneId': zoneId,
                          'shardId': None}
            self.cr.playGame.getPlace().elevator.signalDone(doneStatus)
            base.camLens.setMinFov(ToontownGlobals.CBElevatorFov/(4./3.))

    def setBossOfficeZoneForce(self, zoneId):
        place = self.cr.playGame.getPlace()
        if place:
            place.request('Elevator', self, 1)
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {'loader': 'cogHQLoader',
                          'where': 'instanceBattle',
                          'how': 'Movie',
                          'zoneId': zoneId,
                          'hoodId': hoodId,
                          'shardId': None}
            if hasattr(place, 'elevator') and place.elevator:
                place.elevator.signalDone(doneStatus)
            else:
                self.notify.warning("setBossOfficeZoneForce: Couldn't find playGame.getPlace().elevator, zoneId: %s" % zoneId)
        else:
            self.notify.warning("setBossOfficeZoneForce: Couldn't find playGame.getPlace(), zoneId: %s" % zoneId)

    def getDestName(self):
        return TTLocalizer.ElevatorSellBotBoss

    def enterClosing(self, ts):
        DistributedElevatorExt.DistributedElevatorExt.enterClosing(self, ts)
        if self.localToonOnBoard:
            if self.irisTrack:
                self.irisTrack.pause()
            self.irisTrack = Sequence(
                Wait(1.0),
                Func(base.transitions.fadeOut, 0.8)
            )
            self.irisTrack.start()