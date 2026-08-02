# -*- coding: utf-8 -*-
from pandac.PandaModules import Point3
from direct.interval.IntervalGlobal import Func, Sequence, SoundInterval, Wait, LerpPosInterval
from toontown.building import DistributedElevator
from toontown.building import DistributedBossElevator
from toontown.building.ElevatorConstants import *
from toontown.building.ElevatorUtils import getCloseInterval
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals


class DistributedPaceElevator(DistributedBossElevator.DistributedBossElevator):

    RideDuration = 8.0

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
        self.rideMusic = base.loader.loadMusic(
            'phase_9/audio/bgm/merc/instance_pacesetter_elevator.ogg'
        )

        self.finalOpenSfx = None
        self.finalCloseSfx = None
        self.rideTrack = None
        self.rideHiddenGeom = None
        self.previousMinFov = None
        self.rideElevatorStartPos = None
        self.rideRoot = None
        self.rideOriginalParent = None
        self.rideOriginalMat = None

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

    def onDoorCloseFinish(self):
        return

    def enterClosed(self, ts):
        DistributedBossElevator.DistributedBossElevator.enterClosed(
            self,
            ts
        )

        self.forceDoorsClosed()
        self.startRide(ts)

    def exitClosed(self):
        pass

    def __goToBossOffice(self, zoneId):
        self.stopRide()
        camera.wrtReparentTo(render)

        playGame = self.cr.playGame

        if not playGame:
            self.notify.warning(
                'Cannot enter Pace boss zone %s: PlayGame unavailable.' % zoneId
            )
            return

        requestStatus = {
            'loader': 'cogHQLoader',
            'where': 'cogHQBossBattle',
            'how': 'teleportIn',
            'hoodId': ToontownGlobals.LawbotHQ,
            'zoneId': zoneId,
            'shardId': None,
            'avId': -1
        }

        playGame.fsm.request(
            'quietZone',
            [requestStatus]
        )


    def setBossOfficeZone(self, zoneId):
        if self.localToonOnBoard:
            self.__goToBossOffice(zoneId)


    def setBossOfficeZoneForce(self, zoneId):
        self.__goToBossOffice(zoneId)

    def startRide(self, ts=0):
        self.stopRide()

        base.musicManager.stopAllSounds()

        place = self.cr.playGame.getPlace()
        if place and hasattr(place, 'loader') and hasattr(place.loader, 'geom'):
            self.rideHiddenGeom = place.loader.geom
            self.rideHiddenGeom.hide()

        for seatIndex in xrange(len(self.elevatorPoints)):
            avId = 0
            if seatIndex < len(self.boardedAvIds.keys()):
                avId = self.boardedAvIds.keys()[seatIndex]

            toon = self.cr.doId2do.get(avId)
            if toon:
                toon.reparentTo(self.elevatorModel)
                toon.setPos(apply(Point3, self.elevatorPoints[seatIndex]))
                toon.setHpr(180, 0, 0)
                toon.setAnimState('neutral', 1.0)
                toon.show()
                toon.setShadowHeight(0)

        self.rideRoot = render.attachNewNode(self.uniqueName('paceRideRoot'))
        self.rideOriginalParent = self.elevatorModel.getParent()
        self.rideOriginalMat = self.elevatorModel.getMat(render)

        self.elevatorModel.reparentTo(self.rideRoot)
        self.elevatorModel.setMat(render, self.rideOriginalMat)

        camera.reparentTo(self.elevatorModel)
        camera.setPos(0.0, 12.0, 4.6)
        camera.setHpr(180, -6, 0)

        self.rideElevatorStartPos = self.rideRoot.getPos()

        # self.rideMusic.setLoop(False)
        # self.rideMusic.setVolume(1.0)
        # self.rideMusic.play()

        cameraMid = Point3(0.0, 12.0, 4.6)
        cameraMin = Point3(0.0, 12.0, 4.4)
        cameraMax = Point3(0.0, 12.0, 4.8)

        # self.rideTrack = Sequence(
        #     Wait(0.5),

        #     LerpPosInterval(camera,0.5,cameraMin,startPos=cameraMid,blendType='easeOut'),
        #     LerpPosInterval(camera,0.5,cameraMid,startPos=cameraMin),

        #     Wait(0.75),

        #     LerpPosInterval(camera,0.5,cameraMax,startPos=cameraMid,blendType='easeOut'),
        #     LerpPosInterval(camera,0.75,cameraMid,startPos=cameraMax),

        #     Wait(0.75),

        #     LerpPosInterval(camera,0.45,cameraMin,startPos=cameraMid,blendType='easeOut'),
        #     LerpPosInterval(camera,0.45,cameraMid,startPos=cameraMin),

        #     Wait(0.75),

        #     LerpPosInterval(camera,0.45,cameraMax,startPos=cameraMid,blendType='easeOut'),
        #     LerpPosInterval(camera,0.75,cameraMid,startPos=cameraMax),

        #     Wait(0.9),
        #     Func(self.finishRide)
        # )
        # self.rideTrack.start(ts)

    def finishRide(self):
        if self.rideElevatorStartPos is not None:
            if self.rideRoot:
                self.rideRoot.setPos(self.rideElevatorStartPos)
            self.rideElevatorStartPos = None

        if self.rideHiddenGeom:
            self.rideHiddenGeom.show()
            self.rideHiddenGeom = None

    def stopRide(self):
        if self.rideTrack:
            self.rideTrack.pause()
            self.rideTrack = None

        if self.rideElevatorStartPos is not None:
            if self.rideRoot:
                self.rideRoot.setPos(self.rideElevatorStartPos)
            self.rideElevatorStartPos = None

        self.restoreRideScene()

    def restoreRideScene(self):
        if self.rideRoot:
            for avId in self.boardedAvIds.keys():
                toon = self.cr.doId2do.get(avId)
                if toon:
                    toon.wrtReparentTo(render)

            if self.rideOriginalParent:
                currentMat = self.elevatorModel.getMat(render)
                self.elevatorModel.reparentTo(self.rideOriginalParent)
                self.elevatorModel.setMat(render, currentMat)

            self.rideRoot.removeNode()
            self.rideRoot = None
            self.rideOriginalParent = None
            self.rideOriginalMat = None

        if self.rideHiddenGeom:
            self.rideHiddenGeom.show()
            self.rideHiddenGeom = None


    def enterOpening(self, ts):
        if self.rideTrack:
            self.rideTrack.pause()
            self.rideTrack = None

        if self.rideHiddenGeom:
            self.rideHiddenGeom.show()
            self.rideHiddenGeom = None

        taskMgr.remove(self.uniqueName('paceRideCleanup'))
        taskMgr.doMethodLater(
            ElevatorData[self.type]['openTime'],
            self.__finishRideCleanup,
            self.uniqueName('paceRideCleanup')
        )

        DistributedBossElevator.DistributedBossElevator.enterOpening(self, ts)

    def __stopPaceRideMusic(self, task):
        return task.done

    def __finishRideCleanup(self, task):
        camera.wrtReparentTo(render)
        self.restoreRideScene()
        return task.done

    def disable(self):
        taskMgr.remove(self.uniqueName('paceRideCleanup'))
        taskMgr.remove(self.uniqueName('stopPaceRideMusic'))
        if self.rideMusic:
            self.rideMusic.stop()
        camera.wrtReparentTo(render)
        self.stopRide()
        DistributedBossElevator.DistributedBossElevator.disable(self)

    def delete(self):
        taskMgr.remove(self.uniqueName('paceRideCleanup'))
        taskMgr.remove(self.uniqueName('stopPaceRideMusic'))
        if self.rideMusic:
            self.rideMusic.stop()
        camera.wrtReparentTo(render)
        self.stopRide()
        self.rideMusic = None
        DistributedBossElevator.DistributedBossElevator.delete(self)

    def getElevatorModel(self):
        return self.elevatorModel

    def getDestName(self):
        if hasattr(TTLocalizer, 'ElevatorPacesetter'):
            return TTLocalizer.ElevatorPacesetter
        if hasattr(TTLocalizer, 'ElevatorBossBotBoss'):
            return TTLocalizer.ElevatorBossBotBoss
        return 'The Pacesetter'
