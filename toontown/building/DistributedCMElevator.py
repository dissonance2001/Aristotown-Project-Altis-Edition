from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer

class DistributedCMElevator(DistributedBossElevator.DistributedBossElevator):

    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_CM
        self.countdownTime = ElevatorData[self.type]['countdown']

    def setupElevator(self):
        geom = base.cr.playGame.hood.loader.geom
        self.elevatorModel = loader.loadModel('phase_12/models/bossbotHQ/BB_Elevator')
        self.leftDoor = self.elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right_door')
        locator = geom.find('**/elevator_locator')
        self.elevatorModel.reparentTo(locator)  # reparent to locator when putting it back
       # self.elevatorModel.setPos(0, -85, 0)  # Temporary
        DistributedElevator.DistributedElevator.setupElevator(self)

    def getDestName(self):
        return TTLocalizer.ElevatorLawBotBoss