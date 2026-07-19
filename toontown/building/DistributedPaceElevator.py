# -*- coding: utf-8 -*-
from direct.interval.IntervalGlobal import Func, Sequence, SoundInterval
from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from toontown.building.ElevatorUtils import getCloseInterval
from toontown.toonbase import TTLocalizer


class DistributedPaceElevator(DistributedBossElevator.DistributedBossElevator):

    def __init__(self, cr):
        DistributedBossElevator.DistributedBossElevator.__init__(self, cr)

        self.type = ELEVATOR_PACE
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.elevatorPoints = ElevatorPoints

        self.openSfx = base.loader.loadSfx(
            'phase_5/audio/sfx/elevator_door_open.ogg'
        )
        self.closeSfx = base.loader.loadSfx(
            'phase_5/audio/sfx/elevator_door_close.ogg'
        )
        self.dingSfx = base.loader.loadSfx(
            'phase_5/audio/sfx/elevator_ding.ogg'
        )
        self.clunkSfx = base.loader.loadSfx(
            'phase_5/audio/sfx/cogbldg_door_close.ogg'
        )

        self.finalOpenSfx = None
        self.finalCloseSfx = None

    def setupElevator(self):
        self.elevatorModel = loader.loadModel(
            'phase_8/models/modules/ttcc_psetter_elevator.bam'
        )

        self.leftDoor = self.elevatorModel.find('**/left_door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left-door')

        self.rightDoor = self.elevatorModel.find('**/right_door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right-door')

        if self.leftDoor.isEmpty() or self.rightDoor.isEmpty():
            self.notify.error(
                'Could not find the Pacesetter elevator door nodes.'
            )

        locator = render.find('**/elevator_origin')
        if locator.isEmpty():
            locator = render.find('**/elevator_locator')

        if locator.isEmpty():
            self.notify.warning(
                'Could not find elevator_origin or elevator_locator; '
                'parenting the elevator to render.'
            )
            self.elevatorModel.reparentTo(render)
        else:
            self.elevatorModel.reparentTo(locator)

        self.elevatorModel.setPos(0, 0, 0)
        self.elevatorModel.setHpr(180, 0, 0)
        self.elevatorModel.setScale(1)

        DistributedElevator.DistributedElevator.setupElevator(self)

        self.closeDoors.pause()
        self.closeDoors = Sequence(
            getCloseInterval(
                self,
                self.leftDoor,
                self.rightDoor,
                self.closeSfx,
                None,
                self.type
            ),
            SoundInterval(
                self.dingSfx,
                volume=ElevatorData[self.type]['sfxVolume'],
                node=self.leftDoor
            ),
            SoundInterval(
                self.clunkSfx,
                volume=ElevatorData[self.type]['sfxVolume'],
                node=self.leftDoor
            ),
            Func(self.onDoorCloseFinish)
        )

    def getElevatorModel(self):
        return self.elevatorModel

    def getDestName(self):
        if hasattr(TTLocalizer, 'ElevatorPacesetter'):
            return TTLocalizer.ElevatorPacesetter
        if hasattr(TTLocalizer, 'ElevatorBossBotBoss'):
            return TTLocalizer.ElevatorBossBotBoss
        return 'The Pacesetter'
