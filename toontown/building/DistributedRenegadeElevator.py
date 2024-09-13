import DistributedElevator
import DistributedBossElevator
from ElevatorConstants import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer

class DistributedRenegadeElevator(DistributedBossElevator.DistributedBossElevator):

    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_BB
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.elevatorPoints = BossbotElevatorPoints

    def setupElevator(self):
        geom = base.cr.playGame.hood.loader.geom
        self.elevatorModel = loader.loadModel('phase_12/models/bossbotHQ/BB_Elevator')
        self.leftDoor = self.elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right_door')
        self.elevatorModel.reparentTo(geom)
        self.elevatorModel.setPos(30.556, 268.603, -1.726)
        self.elevatorModel.setHpr(270, 0, 0)
        DistributedElevator.DistributedElevator.setupElevator(self)

    def getDestName(self):
        return TTLocalizer.ElevatorRenegade
