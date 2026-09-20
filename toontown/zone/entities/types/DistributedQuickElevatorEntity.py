from toontown.level import DistributedEntity
from toontown.level import BasicEntities
from toontown.building.ElevatorUtils import *
from toontown.building import DistributedElevatorFSM
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.task import Task
from direct.showbase import PythonUtil
from direct.fsm.FSM import FSM


@DirectNotifyCategory()
class DistributedQuickElevatorEntity(BasicEntities.DistributedNodePathEntity, DistributedElevatorFSM.DistributedElevatorFSM):
    elevatorType2ModelPath = {ELEVATOR_NORMAL: 'phase_4/models/modules/elevator',
                              ELEVATOR_MINT: 'phase_10/models/cogHQ/mintElevator',
                              ELEVATOR_OFFICE: 'phase_11/models/lawbotHQ/lawbotElevator',
                              ELEVATOR_STAGE: 'phase_11/models/lawbotHQ/LB_ElevatorScaled',
                              ELEVATOR_DERRICK_MAN: 'phase_5/models/cogdominium/tt_m_ara_csa_elevatorB',
                              ELEVATOR_VP: 'phase_9/models/cogHQ/cogHQ_elevator'}
    defaultTransitions = {'Off': ['Opening', 'Closed'],
                          'Opening': ['WaitEmpty',
                                      'WaitCountdown',
                                      'Opening',
                                      'Closing'],
                          'WaitEmpty': ['WaitCountdown', 'Closing', 'Opening'],
                          'WaitCountdown': ['WaitEmpty',
                                            'AllAboard',
                                            'Closing',
                                            'WaitCountdown'],
                          'AllAboard': ['WaitEmpty', 'Closing'],
                          'Closing': ['Closed',
                                      'WaitEmpty',
                                      'Closing',
                                      'Opening'],
                          'Closed': ['Opening']}

    def __init__(self, cr):
        BasicEntities.DistributedNodePathEntity.__init__(self, cr)
        DistributedElevatorFSM.DistributedElevatorFSM.__init__(self, cr)
        self.elevatorType = ELEVATOR_NORMAL
        self.countdownTime = ElevatorData[self.elevatorType]['countdown']
        self.isEntering = 0
        self.doorOpeningFlag = 0
        self.doorsNeedToClose = 0
        self.wantState = 0
        self.elevatorModel = None

    def generateInit(self):
        self.notify.debug('generateInit')
        BasicEntities.DistributedNodePathEntity.generateInit(self)

    def generate(self):
        self.notify.debug('generate')
        BasicEntities.DistributedNodePathEntity.generate(self)

    def announceGenerate(self):
        self.notify.debug('announceGenerate')
        BasicEntities.DistributedNodePathEntity.announceGenerate(self)
        self.setupElevator()

    def disable(self):
        self.notify.debug('disable')
        self.ignoreAll()
        DistributedEntity.DistributedEntity.disable(self)

    def delete(self):
        self.notify.debug('delete')
        self.elevatorModel.removeNode()
        del self.elevatorModel
        BasicEntities.DistributedNodePathEntity.delete(self)

    def setElevatorType(self, type):
        self.elevatorType = type
        self.countdownTime = ElevatorData[type]['countdown']
        self.setupElevator()

    def setupElevator(self):
        if self.elevatorModel:
            self.elevatorSphereNodePath.removeNode()
            self.elevatorModel.removeNode()
            self.elevatorModel = None
        self.elevatorModel = loader.loadModel(self.elevatorType2ModelPath[self.elevatorType])
        self.elevatorModel.reparentTo(self)
        self.leftDoor = self.elevatorModel.find('**/left-door')
        if self.leftDoor.isEmpty():
            self.leftDoor = self.elevatorModel.find('**/left_door')
        self.rightDoor = self.elevatorModel.find('**/right-door')
        if self.rightDoor.isEmpty():
            self.rightDoor = self.elevatorModel.find('**/right_door')
        collisionRadius = ElevatorData[self.elevatorType]['collRadius']
        self.elevatorSphere = CollisionSphere(0, 5, 0, collisionRadius)
        self.elevatorSphere.setTangible(0)
        self.elevatorSphereNode = CollisionNode(self.uniqueName('elevatorSphere'))
        self.elevatorSphereNode.setIntoCollideMask(ToontownGlobals.WallBitmask)
        self.elevatorSphereNode.addSolid(self.elevatorSphere)
        self.elevatorSphereNodePath = self.getElevatorModel().attachNewNode(self.elevatorSphereNode)
        self.elevatorSphereNodePath.hide()
        self.elevatorSphereNodePath.reparentTo(self.getElevatorModel())
        self.elevatorSphereNodePath.stash()
        self.boardedAvIds = {}
        self.openDoors = getOpenInterval(self, self.leftDoor, self.rightDoor, self.openSfx, self.finalOpenSfx,
                                         self.elevatorType)
        self.closeDoors = getCloseInterval(self, self.leftDoor, self.rightDoor, self.closeSfx, self.finalCloseSfx,
                                           self.elevatorType)
        self.openDoors = Sequence(self.openDoors, Func(self.onDoorOpenFinish))
        self.closeDoors = Sequence(self.closeDoors, Func(self.onDoorCloseFinish))
        if __debug__:
            self.accept('f12', self.forceClose)
        self.finishSetup()
        self.elevatorSphereNodePath.setY(-1.42)

    def handleEnterSphere(self, collEntry):
        self.cr.playGame.getPlace().detectedElevatorCollision(self)

    def handleEnterElevator(self):
        if base.localAvatar.getHp() > 0:
            self.sendUpdate('requestBoard', [])
        else:
            self.notify.warning('Tried to board elevator with hp: %d' % base.localAvatar.getHp())

    def getElevatorModel(self):
        return self.elevatorModel

    def enterWaitEmpty(self, ts):
        self.lastState = self.state
        self.elevatorSphereNodePath.unstash()
        self.forceDoorsOpen()
        self.accept(self.uniqueName('enterelevatorSphere'), self.handleEnterSphere)
        self.accept(self.uniqueName('enterElevatorOK'), self.handleEnterElevator)
        DistributedElevatorFSM.DistributedElevatorFSM.enterWaitEmpty(self, ts)

    def exitWaitEmpty(self):
        self.lastState = self.state
        self.elevatorSphereNodePath.stash()
        self.ignore(self.uniqueName('enterelevatorSphere'))
        self.ignore(self.uniqueName('enterElevatorOK'))
        DistributedElevatorFSM.DistributedElevatorFSM.exitWaitEmpty(self)

    def enterWaitCountdown(self, ts):
        self.lastState = self.state
        DistributedElevatorFSM.DistributedElevatorFSM.enterWaitCountdown(self, ts)
        self.forceDoorsOpen()
        self.accept(self.uniqueName('enterElevatorOK'), self.handleEnterElevator)
        self.startCountdownClock(self.countdownTime, ts)

    def exitWaitCountdown(self):
        self.lastState = self.state
        self.ignore(self.uniqueName('enterElevatorOK'))
        DistributedElevatorFSM.DistributedElevatorFSM.exitWaitCountdown(self)

    def enterClosing(self, ts):
        self.lastState = self.state
        taskMgr.doMethodLater(1.0, self._delayIris, 'delayedIris')
        DistributedElevatorFSM.DistributedElevatorFSM.enterClosing(self, ts)

    def fillSlot(self, index, avId, transfer=0):
        self.notify.debug('%s.fillSlot(%s, %s, ...)' % (self.doId, index, avId))
        request = self.toonRequests.get(index)
        if request:
            self.cr.relatedObjectMgr.abortRequest(request)
            del self.toonRequests[index]
        if avId == 0:
            pass
        elif avId not in self.cr.doId2do:
            func = PythonUtil.Functor(self.gotToon, index, avId)
            self.toonRequests[index] = self.cr.relatedObjectMgr.requestObjects([avId], allCallback=func)
        elif not self.isSetup:
            self.deferredSlots.append((index, avId))
        else:
            if avId == base.localAvatar.getDoId():
                self.localToonOnBoard = 1
                if not transfer:
                    elevator = self.getPlaceElevator()
                    elevator.fsm.request('boarding', [self.getElevatorModel(), self])
                    elevator.fsm.request('boarded')
            toon = self.cr.doId2do[avId]
            toon.stopSmooth()
            if transfer:
                posPoints = Point3(*self.getScaledPoint(index))
                toon.setPos(self.getElevatorModel(), posPoints)
                toon.setHpr(self.getElevatorModel(), (180, 0, 0))
                toon.setShadowHeight(0)
                if toon.isDisguised:
                    toon.suit.loop('neutral')
                else:
                    toon.setAnimState('Neutral', 1.0)
                self.notify.debug('skipping board animation, since this was a transfer.')
                self.boardedAvIds[avId] = index
                return
            toon.setZ(self.getElevatorModel(), self.getScaledPoint(index)[2])
            toon.setShadowHeight(0)
            if toon.isDisguised:
                toon.suit.loop('walk')
                animFunc = Func(toon.suit.loop, 'neutral')
            else:
                toon.setAnimState('Run', 1.0)
                animFunc = Func(toon.setAnimState, 'Neutral', 1.0)
            toon.headsUp(self.getElevatorModel(), Point3(*self.getScaledPoint(index)))
            track = Sequence(LerpPosInterval(toon, TOON_BOARD_ELEVATOR_TIME * 0.75, Point3(*self.getScaledPoint(index)), other=self.getElevatorModel()), LerpHprInterval(toon, TOON_BOARD_ELEVATOR_TIME * 0.25, Point3(180, 0, 0), other=self.getElevatorModel()), animFunc, name=toon.uniqueName('fillElevator'), autoPause=1)
            track.start()
            self.boardedAvIds[avId] = index

    def _delayIris(self, tskfooler=0):
        if base.localAvatar.getDoId() in list(self.boardedAvIds.keys()):
            base.transitions.fadeOut(1.0)
            base.localAvatar.pauseGlitchKiller()
        return Task.done

    def exitClosing(self):
        self.lastState = self.state
        DistributedElevatorFSM.DistributedElevatorFSM.exitClosing(self)

    def enterClosed(self, ts):
        self.lastState = self.state
        self.forceDoorsClosed()
        self.__doorsClosed(self.getZoneId())

    def exitClosed(self):
        self.lastState = self.state
        DistributedElevatorFSM.DistributedElevatorFSM.exitClosed(self)

    def enterOff(self):
        self.lastState = self.state
        if self.wantState == 'closed':
            self.demand('Closing')
        elif self.wantState == 'waitEmpty':
            self.demand('WaitEmpty')
        DistributedElevatorFSM.DistributedElevatorFSM.enterOff(self)

    def exitOff(self):
        self.lastState = self.state
        DistributedElevatorFSM.DistributedElevatorFSM.exitOff(self)

    def enterOpening(self, ts):
        self.lastState = self.state
        DistributedElevatorFSM.DistributedElevatorFSM.enterOpening(self, ts)

    def exitOpening(self):
        DistributedElevatorFSM.DistributedElevatorFSM.exitOpening(self)

    def getZoneId(self):
        return 0

    def setBldgDoId(self, bldgDoId):
        self.bldg = None
        self.setupElevator()

    def __doorsClosed(self, zoneId):
        pass

    def onDoorCloseFinish(self):
        pass

    def setIsLocked(self, locked):
        self.isLocked = locked

    def getIsLocked(self):
        return self.isLocked

    def setEntering(self, entering):
        self.isEntering = entering

    def getEntering(self):
        return self.isEntering

    def forceDoorsOpen(self):
        openDoors(self.leftDoor, self.rightDoor)

    def forceDoorsClosed(self):
        if self.openDoors.isPlaying():
            self.doorsNeedToClose = 1
        else:
            self.closeDoors.finish()
            closeDoors(self.leftDoor, self.rightDoor)

    def emptySlot0(self, avId, bailFlag, transfer, timestamp):
        self.emptySlot(0, avId, bailFlag, transfer, timestamp)

    def emptySlot1(self, avId, bailFlag, transfer, timestamp):
        self.emptySlot(1, avId, bailFlag, transfer, timestamp)

    def emptySlot2(self, avId, bailFlag, transfer, timestamp):
        self.emptySlot(2, avId, bailFlag, transfer, timestamp)

    def emptySlot3(self, avId, bailFlag, transfer, timestamp):
        self.emptySlot(3, avId, bailFlag, transfer, timestamp)

    def emptySlot4(self, avId, bailFlag, transfer, timestamp):
        self.emptySlot(4, avId, bailFlag, transfer, timestamp)

    def emptySlot5(self, avId, bailFlag, transfer, timestamp):
        self.emptySlot(5, avId, bailFlag, transfer, timestamp)

    def emptySlot6(self, avId, bailFlag, transfer, timestamp):
        self.emptySlot(6, avId, bailFlag, transfer, timestamp)

    def emptySlot7(self, avId, bailFlag, transfer, timestamp):
        self.emptySlot(7, avId, bailFlag, transfer, timestamp)

    def emptySlot(self, index, avId, bailFlag, transfer, timestamp):
        self.notify.debug('Emptying slot: %d for %d' % (index, avId))

        if avId == 0:
            pass
        elif not self.isSetup:
            newSlots = []
            for slot in self.deferredSlots:
                if slot[0] != index:
                    newSlots.append(slot)

            self.deferredSlots = newSlots
        elif avId in self.cr.doId2do:
            if bailFlag == 1 and hasattr(self, 'clockNode'):
                if timestamp < self.countdownTime and timestamp >= 0:
                    self.countdown(self.countdownTime - timestamp)
                else:
                    self.countdown(self.countdownTime)
            toon = self.cr.doId2do[avId]
            toon.stopSmooth()
            if toon.isDisguised:
                toon.suit.loop('walk')
                animFunc = Func(toon.suit.loop, 'neutral')
            else:
                toon.setAnimState('Run', 1.0)
                animFunc = Func(toon.setAnimState, 'Neutral', 1.0)
            if self.offTrack[index]:
                if self.offTrack[index].isPlaying():
                    self.offTrack[index].finish()
                    self.offTrack[index] = None
            self.offTrack[index] = Sequence(LerpPosInterval(toon, TOON_EXIT_ELEVATOR_TIME, Point3(*JumpOutOffsets[index]), startPos=Point3(*self.getScaledPoint(index)), other=self.getElevatorModel()), animFunc, Func(self.notifyToonOffElevator, toon), name=toon.uniqueName('emptyElevator'), autoPause=1)
            if avId == base.localAvatar.getDoId() and transfer:
                nodePath = self.getElevatorModel()
                base.camera.wrtReparentTo(nodePath)
                base.camera.setPosHpr(0, -16, 5.5, 0, 0, 0)
                base.transitions.fadeIn(1.0)
                messenger.send('exitElevator')
                scale = base.localAvatar.getScale()
                self.offTrack[index].append(Func(base.camera.setScale, scale))
            self.offTrack[index].start()
            if avId in self.boardedAvIds:
                del self.boardedAvIds[avId]
        else:
            self.notify.warning('toon: ' + str(avId) + " doesn't exist, and" + ' cannot exit the elevator!')

    def forceRemoveToon(self, avId, index, exitElevator):
        self.notify.debug(f'server asked us to forcefully remove avId {avId} index {index} from boarded.')
        if avId in self.boardedAvIds:
            if self.boardedAvIds[avId] == index:
                del self.boardedAvIds[avId]
            if avId == base.localAvatar.doId:
                self.localToonOnBoard = 0
                zoneId = self.level.getEntityZoneEntId(exitElevator)
                self.newZoneInterest(zoneId)
                taskMgr.doMethodLater(ElevatorData[self.type]['openTime'] * 1.5 + 0.1,
                                      DistributedQuickElevatorEntity.checkLocalToonLocation,
                                      name='QuickElevatorCheckToonLocation',
                                      extraArgs=[exitElevator, self.level])

    def newZoneInterest(self, zoneNum):
        zoneNode = self.level.getZoneNode(zoneNum)
        if zoneNode is None:
            return
        self.level.enterZone(zoneNum)
        self.level.camEnterZone(zoneNum)
        messenger.send('elevatorZoneInterest', [self.level, zoneNum])

    @staticmethod
    def checkLocalToonLocation(exitElevator, level):
        otherElevator = level.getEntity(exitElevator)
        otherElevator.notify.debug('checking local toon location')
        relativePos = localAvatar.getPos(otherElevator)
        if relativePos.length() > 25:
            otherElevator.notify.warning(f'local toon was seen as out of bounds, putting them in the correct place. distance: {relativePos.length()}')
            localAvatar.setPos(otherElevator, *JumpOutOffsets[0])
            localAvatar.setHpr(otherElevator.getElevatorModel(), 180, 0, 0)
            base.transitions.fadeIn()
            base.cr.playGame.getPlace().setState('Walk')
