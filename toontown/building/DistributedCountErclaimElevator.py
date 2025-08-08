from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer

class DistributedCountErclaimElevator(DistributedBossElevator.DistributedBossElevator):

    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_CJ
        self.countdownTime = ElevatorData[self.type]['countdown']

    def setupElevator(self):
        self.elevatorModel = loader.loadModel('phase_4/models/modules/ttcc_gen_sigil')
        # icon = self.elevatorModel.find('**/big_frame/')
        # icon.hide()
        self.leftDoor = self.elevatorModel.find('**/DropShadow')
        self.rightDoor = self.elevatorModel.find('**/Bolts')
        geom = base.cr.playGame.hood.loader.geom
        locator = geom.find('**/elevator_locator')
        self.elevatorModel.reparentTo(locator)
        self.elevatorModel.setY(-10)
        self.elevatorModel.setX(30)
        DistributedElevator.DistributedElevator.setupElevator(self)

    def getDestName(self):
        return TTLocalizer.ElevatorLawBotBoss