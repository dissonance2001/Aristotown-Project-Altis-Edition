from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from toontown.toonbase import TTLocalizer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.distributed.ToontownClientRepository import ToontownClientRepository

class DistributedCLOElevator(DistributedBossElevator.DistributedBossElevator):

    def __init__(self, cr):
        """
        :param ToontownClientRepository cr: The client repository which maintains all client-side distributed objects.
        """
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_CLO
        self.countdownTime = ElevatorData[self.type]['countdown']

    def setupElevator(self):
        """
        Called when the building doId is set at construction time, this method sets up the elevator for business.
        """
        self.elevatorModel = loader.loadModel('phase_11/models/lawbotHQ/LB_Elevator')

        self.leftDoor = self.elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right_door')

        geom = base.cr.playGame.hood.loader.geom
        try:
            locator = geom.find('**/elevator_locator')
            self.elevatorModel.reparentTo(locator)
        except:
            self.elevatorModel.reparentTo(render)

        DistributedElevator.DistributedElevator.setupElevator(self)

    def getDestName(self):
        """
        :return: 'Lawbot Executive Lawfice'
        """
        return TTLocalizer.ElevatorLawBotBoss
