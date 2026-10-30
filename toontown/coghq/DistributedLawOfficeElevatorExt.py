from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from toontown.building.ElevatorConstants import *
from toontown.building.ElevatorUtils import *
from toontown.building import DistributedElevatorExt
from toontown.building import DistributedElevator
from toontown.toonbase import ToontownGlobals
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.gui import DirectGui
from toontown.hood import ZoneUtil
from toontown.toonbase import TTLocalizer

class DistributedLawOfficeElevatorExt(DistributedElevatorExt.DistributedElevatorExt):

    def __init__(self, cr):
        DistributedElevatorExt.DistributedElevatorExt.__init__(self, cr)
        self.type = ELEVATOR_OFFICE
        self.signHead = None

    def generate(self):
        DistributedElevatorExt.DistributedElevatorExt.generate(self)

    def delete(self):
        if self.signHead and not self.signHead.isEmpty():
            self.signHead.removeNode()
            self.signHead = None
        self.elevatorModel.removeNode()
        del self.elevatorModel
        DistributedElevatorExt.DistributedElevatorExt.delete(self)

    def setEntranceId(self, entranceId):
        self.entranceId = entranceId
        if not getattr(self, 'elevatorModel', None):
            self.setupElevator()
        geom = self.cr.playGame.hood.loader.geom
        locator = geom.find('**/elevator_origin_%s' % entranceId)
        if locator:
            self.elevatorModel.setPosHpr(locator, 0, 0, 0, 0, 0, 0)
        else:
            self.notify.error('No origin found for originId: %s' % entranceId)
        entranceId2zoneId = {0: ToontownGlobals.LawbotStageIntA,
         1: ToontownGlobals.LawbotStageIntB,
         2: ToontownGlobals.LawbotStageIntC,
         3: ToontownGlobals.LawbotStageIntD,
         4: ToontownGlobals.LawbotStageIntD}
        self.intZoneId = entranceId2zoneId[entranceId]
        if self.signHead and not self.signHead.isEmpty():
            self.signHead.removeNode()
            self.signHead = None
        if entranceId != 4:
            locator = geom.find('**/elevator_signorigin_%s' % entranceId)
            backgroundGeom = geom.find('**/ElevatorFrameFront_%d' % entranceId)
            signText = DirectGui.OnscreenText(text=TextEncoder.upper(TTLocalizer.GlobalStreetNames[self.intZoneId][-1]), font=ToontownGlobals.getSuitFont(), scale=2, fg=(0.87, 0.87, 0.87, 1), mayChange=False, parent=geom)
            signText.setPosHpr(locator, 0, 0, 0, 0, 0, 0)
            signText.setDepthWrite(0)
        else:
            locator = geom.find('**/elevator_signorigin_4')
            if locator.isEmpty():
                self.notify.error('No sign origin found for entranceId: 4')
            else:
                self.signHead = loader.loadModel('phase_5/models/char/suitC_skeleton_skull-zero')
                self.signHead.reparentTo(locator)
                self.signHead.setPos(0, -0.45, -0.3)
                self.signHead.setHpr(180, 0, 0)
                self.signHead.setScale(4.5)
                self.signHead.setTexture(loader.loadTexture('phase_5/maps/ttcc_ene_skelecog_l.png'), 1)
                self.signHead.setTwoSided(True)

    def setupElevator(self):
        if getattr(self, 'entranceId', None) == 4:
            self.elevatorModel = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB')
            self.elevatorModel.setScale(1)
        else:
            self.elevatorModel = loader.loadModel('phase_11/models/lawbotHQ/LB_ElevatorScaled')
        self.elevatorModel.reparentTo(render)
        self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right_door')
        DistributedElevator.DistributedElevator.setupElevator(self)
        self.elevatorSphereNodePath.setY(-1.42)

    def getElevatorModel(self):
        return self.elevatorModel

    def setBldgDoId(self, bldgDoId):
        self.bldg = None
        if not getattr(self, 'elevatorModel', None) and hasattr(self, 'entranceId'):
            self.setupElevator()
        return

    def getZoneId(self):
        return 0

    def __doorsClosed(self, zoneId):
        pass

    def setLawOfficeInteriorZone(self, zoneId):
        if self.localToonOnBoard:
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {'loader': 'cogHQLoader',
             'where': 'stageInterior',
             'how': 'teleportIn',
             'zoneId': zoneId,
             'hoodId': hoodId,
             'stageId': self.intZoneId}
            self.cr.playGame.getPlace().elevator.signalDone(doneStatus)

    def setLawOfficeInteriorZoneForce(self, zoneId):
        place = self.cr.playGame.getPlace()
        if place:
            place.fsm.request('elevator', [self, 1])
            hoodId = self.cr.playGame.hood.hoodId
            doneStatus = {'loader': 'cogHQLoader',
             'where': 'stageInterior',
             'how': 'teleportIn',
             'zoneId': zoneId,
             'hoodId': hoodId,
             'stageId': self.intZoneId}
            if hasattr(place, 'elevator') and place.elevator:
                place.elevator.signalDone(doneStatus)
            else:
                self.notify.warning("setMintInteriorZoneForce: Couldn't find playGame.getPlace().elevator, zoneId: %s" % zoneId)
        else:
            self.notify.warning("setLawOfficeInteriorZoneForce: Couldn't find playGame.getPlace(), zoneId: %s" % zoneId)

    def getDestName(self):
        if self.intZoneId == ToontownGlobals.LawbotStageIntA:
            return TTLocalizer.ElevatorLawBotCourse0
        elif self.intZoneId == ToontownGlobals.LawbotStageIntB:
            return TTLocalizer.ElevatorLawBotCourse1
        elif self.intZoneId == ToontownGlobals.LawbotStageIntC:
            return TTLocalizer.ElevatorLawBotCourse2
        elif self.intZoneId == ToontownGlobals.LawbotStageIntD:
            return TTLocalizer.ElevatorLawBotCourse3
