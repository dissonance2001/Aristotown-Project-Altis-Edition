from __future__ import absolute_import
from . import DistributedElevator
from . import DistributedBossElevator
from .ElevatorConstants import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer

class DistributedCBMElevator(DistributedBossElevator.DistributedBossElevator):

    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_CBM
        self.countdownTime = 8

    def setupElevator(self):
        self.elevatorModel = loader.loadModel('phase_10/models/cogHQ/CFOElevator')
        self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right_door')
        geom = base.cr.playGame.hood.loader.geom
        locator = geom.find('**/elevator_locator')
        self.elevatorModel.reparentTo(locator)
        self.elevatorModel.setH(90)
        self.elevatorModel.setY(100)
        self.elevatorModel.setZ(-27.5)
        self.elevatorModel.setX(30)
        DistributedElevator.DistributedElevator.setupElevator(self)

    def getDestName(self):
        return TTLocalizer.ElevatorCashBotBoss
