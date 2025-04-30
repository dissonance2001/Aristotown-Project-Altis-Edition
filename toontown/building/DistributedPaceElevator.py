# -*- coding: utf-8 -*-
from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer

class DistributedPaceElevator(DistributedBossElevator.DistributedBossElevator):

    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)
        self.type = ELEVATOR_PACE
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.elevatorPoints = BossbotElevatorPoints

    def announceGenerate(self):
        DistributedBossElevator.DistributedBossElevator.announceGenerate(self)
        self.setupElevator()

    def setupElevator(self):
        self.elevatorModel = loader.loadModel('phase_8/models/modules/ttcc_psetter_elevator.bam')
        self.leftDoor = self.elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right_door')
        locator = geom.find('**/elevator_origin')
        if locator.isEmpty():
            print '[DistributedPaceElevator] Warning: Could not find elevator_origin - parenting to render instead.'
            self.elevatorModel.reparentTo(render)
            self.elevatorModel.setHpr(180, 0, 0)  # Adjust position
        else:
            self.elevatorModel.reparentTo(locator)
            self.elevatorModel.setHpr(180, 0, 0)

        DistributedElevator.DistributedElevator.setupElevator(self)

    def getDestName(self):
        return TTLocalizer.ElevatorBossBotBoss
