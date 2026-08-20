from __future__ import absolute_import
from direct.interval.IntervalGlobal import Func, Sequence, Wait
from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.building import CountErfitInstanceGlobals

class DistributedCountErfitElevator(DistributedBossElevator.DistributedBossElevator):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCountErfitElevator')

    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_ERFIT
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.elevatorPoints = ElevatorPoints
        self.irisTrack = None

    def announceGenerate(self):
        DistributedBossElevator.DistributedBossElevator.announceGenerate(self)
        if not hasattr(self, 'elevatorModel') or self.elevatorModel is None:
            self.setupElevator()
        self.elevatorModel.show()

    def setupElevator(self):
        self.elevatorModel = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_csa_elevatorB')
        self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right_door')
        geom = base.cr.playGame.hood.loader.geom
        locator = geom.find('**/count_door_origin')
        if locator.isEmpty():
            self.elevatorModel.reparentTo(render)
            self.elevatorModel.setPosHpr(135.0, 19.9901, 9.0, -180.0, 0, 0)
        else:
            self.elevatorModel.reparentTo(locator)
            self.elevatorModel.setPosHpr(0, 0, 0, 0, 0, 0)
        self.elevatorModel.setScale(1)
        DistributedElevator.DistributedElevator.setupElevator(self)
        self.elevatorSphereNodePath.setY(-1.42)

    def enterClosing(self, ts):
        DistributedBossElevator.DistributedBossElevator.enterClosing(self, ts)
        if self.localToonOnBoard:
            if self.irisTrack:
                self.irisTrack.pause()
            self.irisTrack = Sequence(Wait(1.0), Func(base.transitions.fadeOut, 0.8))
            self.irisTrack.start()

    def _goToCountErfitInstance(self, zoneId):
        playGame = self.cr.playGame
        if not playGame:
            return
        hood = getattr(playGame, 'hood', None)
        townLoader = getattr(hood, 'loader', None)
        if (hood is None or
                getattr(hood, 'hoodId', None) != ToontownGlobals.TheBrrrgh or
                townLoader is None or
                not hasattr(townLoader, 'fsm')):
            return
        requestStatus = {
            'loader': CountErfitInstanceGlobals.INSTANCE_LOADER,
            'where': CountErfitInstanceGlobals.BOSS_BATTLE_STATE,
            'how': 'teleportIn',
            'hoodId': ToontownGlobals.TheBrrrgh,
            'zoneId': zoneId,
            'shardId': None,
            'avId': -1,
            'countErfitInstance': 1
        }
        townLoader.fsm.request('quietZone', [requestStatus])

    def setBossOfficeZone(self, zoneId):
        if self.localToonOnBoard:
            self._goToCountErfitInstance(zoneId)

    def setBossOfficeZoneForce(self, zoneId):
        self._goToCountErfitInstance(zoneId)

    def getDestName(self):
        return TTLocalizer.CountErfitBattle

    def setBldgDoId(self, bldgDoId):
        self.bldgDoId = bldgDoId
        self.bldg = None

    def gotBldg(self, buildingList):
        self.bldg = None
