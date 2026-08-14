from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer

class DistributedCountErfitElevator(DistributedBossElevator.DistributedBossElevator):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCountErfitElevator')
    
    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_ERFIT
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.elevatorPoints = ElevatorPoints

    def announceGenerate(self):
        DistributedBossElevator.DistributedBossElevator.announceGenerate(self)

        if not hasattr(self, 'elevatorModel') or self.elevatorModel is None:
            self.setupElevator()

        self.elevatorModel.show()
        print 'COUNT ERFIT ELEVATOR POS:', self.elevatorModel.getPos(render)

    def setupElevator(self):
        self.elevatorModel = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB')
        # icon = self.elevatorModel.find('**/elevator_frame/')
        # icon.hide()
        self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right_door')
        geom = base.cr.playGame.hood.loader.geom
        # locator = geom.find('**/elevator_locator')
        locator = geom.find('**/count_door_origin')
        if locator.isEmpty():
            self.elevatorModel.reparentTo(render)
            self.elevatorModel.setPosHpr(135.0, 19.9901, 9.0, -180.0, 0, 0)
        else:
            self.elevatorModel.reparentTo(locator)
            self.elevatorModel.setPosHpr(0, 0, 0, 0, 0, 0)
        #self.elevatorModel.setH(180)
        self.elevatorModel.setScale(1)
        DistributedElevator.DistributedElevator.setupElevator(self)
        self.elevatorSphereNodePath.setY(-1.42)

    def getDestName(self):
        return TTLocalizer.CountErfitBattle
    
    def setBldgDoId(self, bldgDoId):
        self.bldgDoId = bldgDoId
        self.bldg = None
        return
    
    def gotBldg(self, buildingList):
        self.bldg = None
        return