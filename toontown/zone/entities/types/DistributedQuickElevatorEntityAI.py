from toontown.level import DistributedEntityAI
from toontown.level import BasicEntities
from toontown.building import DistributedElevatorFSMAI
from toontown.building.ElevatorConstants import *
from direct.distributed.ClockDelta import *
from toontown.ai.AIBase import *


@DirectNotifyCategory()
class DistributedQuickElevatorEntityAI(DistributedEntityAI.DistributedEntityAI, NodePath, BasicEntities.NodePathAttribs, DistributedElevatorFSMAI.DistributedElevatorFSMAI):
    defaultTransitions = {
        'Off': ['Opening', 'Closed'],
        'Opening': ['WaitEmpty', 'WaitCountdown', 'Opening', 'Closing'],
        'WaitEmpty': ['WaitCountdown', 'Closing', 'WaitEmpty', 'Opening'],
        'WaitCountdown': ['WaitEmpty', 'AllAboard', 'Closing', 'WaitCountdown'],
        'AllAboard': ['WaitEmpty', 'Closing'],
        'Closing': ['Closed', 'WaitEmpty', 'Closing', 'Opening'],
        'Closed': ['Opening']}

    def __init__(self, level, entId):
        DistributedEntityAI.DistributedEntityAI.__init__(self, level, entId)
        DistributedElevatorFSMAI.DistributedElevatorFSMAI.__init__(self, self.air, self.level)
        self.countdownTime = ElevatorData[self.type]['countdown']
        self.anyToonsBailed = 0
        self.avIds = self.level.avIdList
        self.isEntering = 0
        self.wantState = None
        self.zoneId = self.bldg.zoneId
        self.inTransfer = False
        if not hasattr(self, 'exitElevator'):
            self.exitElevator = 0
        if not hasattr(self, 'unlockEvent'):
            self.unlockEvent = 0
        if self.unlockEvent:
            self.setUnlockEvent(self.unlockEvent)
        node = hidden.attachNewNode('DistributedQuickElevatorEntityAI')
        NodePath.__init__(self, node)

    def generate(self):
        DistributedEntityAI.DistributedEntityAI.generate(self)
        self.setPos(self.pos)
        self.setHpr(self.hpr)
        DistributedElevatorFSMAI.DistributedElevatorFSMAI.generate(self)

    def avIsOKToBoard(self, av):
        if av.hp > 0 and self.accepting:
            pass
        return not self.isLocked

    def acceptBoarder(self, avId, seatIndex, transfer=0):
        self.notify.debug('acceptBoarder')
        if self.findAvatar(avId) is not None:
            return None

        # Don't accept boarders if the other elevator has other toons. This is an edge case
        # introduced with latency to prevent having toons in both elevators at the same time
        otherElevator = self.getOtherElevator()
        if otherElevator and not transfer and any(otherElevator.seats):
            self.rejectBoarder(avId, ElevatorResponse.OtherElevatorBusy)
            return
        # Don't allow boarding at all if another elevator doesn't exist
        elif not otherElevator:
            self.rejectBoarder(avId, ElevatorResponse.OtherElevatorBusy)
            return

        self.seats[seatIndex] = avId
        self.timeOfBoarding = globalClock.getRealTime()
        self.sendUpdate('fillSlot', [seatIndex, avId, transfer])
        self.acceptOnce(self.air.getAvatarExitEvent(avId), self.__handleUnexpectedExit,
                        extraArgs=[avId])

        if not transfer:
            if self.state == 'WaitEmpty' and self.countFullSeats() < self.countAvsInZone():
                self.request('WaitCountdown')
            elif self.state in ('WaitCountdown', 'WaitEmpty') and self.countFullSeats() >= self.countAvsInZone():
                self.inTransfer = True
                taskMgr.doMethodLater(TOON_BOARD_ELEVATOR_TIME, self.goAllAboard, self.quickBoardTask)
            otherElevator = self.level.getEntity(self.exitElevator)
            if otherElevator.state not in ('Closing', 'Closed'):
                otherElevator.wantState = 'closed'
                otherElevator.request('Closing')
        else:
            taskMgr.doMethodLater(ElevatorData[self.type]['openTime'], self.acceptExiter, 'forceExitToon', [avId, 1])

    def forceClose(self):
        if not __debug__:
            return

        avId = simbase.air.getAvatarIdFromSender()
        av = simbase.air.doId2do.get(avId)

        if not av:
            return

        if av.getAdminAccess() < 200:
            return

        if avId in self.seats and self.getState() not in ('Closing', 'Closed'):
            self.request('AllAboard')

    def countAvsInZone(self):
        matchingZones = 0
        for avId in self.bldg.avIdList:
            av = self.air.doId2do.get(avId)
            if av:
                if av.zoneId == self.bldg.zoneId:
                    matchingZones += 1
        return matchingZones

    def goAllAboard(self, throwAway = 1):
        self.request('Closing')
        return Task.done

    def clearEmptyNow(self, seatIndex):
        self.sendUpdate('emptySlot', [seatIndex, 0, 0, 0, globalClockDelta.getRealNetworkTime()])

    def clearFullNow(self, seatIndex):
        avId = self.seats[seatIndex]
        if avId is None:
            self.notify.warning('Clearing an empty seat index: ' + str(seatIndex) + ' ... Strange...')
        else:
            self.seats[seatIndex] = None
            self.sendUpdate('fillSlot', [0, 0, 0])
            self.ignore(self.air.getAvatarExitEvent(avId))

    def acceptExiter(self, avId, transfer=0):
        self.notify.debug(f'beginning of acceptExiter. seats: {self.seats}')
        seatIndex = self.findAvatar(avId)
        if seatIndex is None:
            self.notify.warning(f'toon {avId} tried to exit, but they had no seat Index. Oops.')
            return
        if self.inTransfer:
            self.notify.warning(f'ignoring toon {avId} exit request, they were in the middle of transferring.')
            return
        self.clearFullNow(seatIndex)
        bailFlag = 0
        if self.anyToonsBailed == 0 and not transfer:
            bailFlag = 1
            self.resetCountdown()
            self.anyToonsBailed = 1
        if not transfer and self.countFullSeats() == 0:
            self.request('WaitEmpty')
        self.sendUpdate('emptySlot', [seatIndex, avId, bailFlag, transfer, globalClockDelta.getRealNetworkTime()])
        taskMgr.doMethodLater(TOON_EXIT_ELEVATOR_TIME, self.clearEmptyNow, self.uniqueName('clearEmpty-%s' % seatIndex),
                              extraArgs=(seatIndex,))

    def __handleUnexpectedExit(self, avId):
        self.notify.warning('Avatar: ' + str(avId) + ' has exited unexpectedly')
        seatIndex = self.findAvatar(avId)
        if seatIndex is None:
            pass
        else:
            self.clearFullNow(seatIndex)
            self.clearEmptyNow(seatIndex)
            if self.countFullSeats() == 0:
                self.request('WaitEmpty')

    def enterOpening(self, clearSeats=1):
        self.d_setState('Opening')
        DistributedElevatorFSMAI.DistributedElevatorFSMAI.enterOpening(self)
        taskMgr.doMethodLater(ElevatorData[self.type]['openTime'], self.waitEmptyTask,
                              self.uniqueName('opening-timer'))

    def exitOpening(self):
        DistributedElevatorFSMAI.DistributedElevatorFSMAI.exitOpening(self)
        if self.isLocked:
            self.wantState = 'closed'
        if self.wantState == 'closed':
            self.demand('Closing')

    def waitEmptyTask(self, task):
        self.request('WaitEmpty')
        return Task.done

    def enterWaitEmpty(self):
        self.lastState = self.state
        if self.wantState == 'closed':
            self.demand('Closing')
        else:
            self.d_setState('WaitEmpty')
            self.accepting = 1
            # Force the other elevator into opening.
            otherElevator = self.getOtherElevator()
            if otherElevator and otherElevator.getCurrentOrNextState() not in ('WaitEmpty', 'Opening', 'Open', 'WaitCountdown'):
                otherElevator.wantState = 'waitEmpty'
                otherElevator.request('Opening')

    def enterWaitCountdown(self):
        self.lastState = self.state
        DistributedElevatorFSMAI.DistributedElevatorFSMAI.enterWaitCountdown(self)
        taskMgr.doMethodLater(self.countdownTime, self.timeToGoTask, self.uniqueName('countdown-timer'))
        if self.lastState == 'WaitCountdown':
            pass

    def timeToGoTask(self, task):
        if self.countFullSeats() > 0:
            self.request('AllAboard')
        else:
            self.request('WaitEmpty')
        return Task.done

    def resetCountdown(self):
        taskMgr.remove(self.uniqueName('countdown-timer'))
        taskMgr.doMethodLater(self.countdownTime, self.timeToGoTask, self.uniqueName('countdown-timer'))

    def enterAllAboard(self):
        DistributedElevatorFSMAI.DistributedElevatorFSMAI.enterAllAboard(self)
        currentTime = globalClock.getRealTime()
        elapsedTime = currentTime - self.timeOfBoarding
        self.notify.debug('elapsed time: ' + str(elapsedTime))
        waitTime = max(TOON_BOARD_ELEVATOR_TIME - elapsedTime, 0)
        taskMgr.doMethodLater(waitTime, self.closeTask, self.uniqueName('waitForAllAboard'))

    def closeTask(self, task):
        if self.countFullSeats() >= 1:
            self.request('Closing')
        else:
            self.request('WaitEmpty')
        return Task.done

    def enterClosing(self):
        if self.countFullSeats() > 0:
            self.sendUpdate('kickToonsOut')
        DistributedElevatorFSMAI.DistributedElevatorFSMAI.enterClosing(self)
        taskMgr.doMethodLater(ElevatorData[self.type]['closeTime'], self.elevatorClosedTask,
                              self.uniqueName('closing-timer'))
        self.d_setState('Closing')

    def elevatorClosedTask(self, task):
        self.elevatorClosed()
        return Task.done

    def elevatorClosed(self):
        if self.isLocked:
            self.request('Closed')
            return None

        numPlayers = self.countFullSeats()
        if numPlayers > 0:
            players = []
            for i in self.seats:
                if i not in [None, 0]:
                    players.append(i)
                    continue
            sittingAvIds = []
            for seatIndex in range(len(self.seats)):
                avId = self.seats[seatIndex]
                if avId:
                    sittingAvIds.append(avId)
                    continue
            for avId in self.avIds:
                if avId not in sittingAvIds:
                    continue
            self.sendToonsToOtherElevator(sittingAvIds)
        else:
            self.notify.debug('The elevator has closed while the other end is in use.')
        self.wantState = 'closed'
        self.request('Closed', 0)

    def setElevatorType(self, type):
        self.type = type
        self.countdownTime = ElevatorData[type]['countdown']
        if self.isLocked:
            self.wantState = 'closed'
            self.request('Closing')
        else:
            self.wantState = 'waitEmpty'
            self.request('Opening')

    def setIsLocked(self, locked, lockOther=True):
        self.isLocked = locked
        if locked:
            if self.state == 'WaitEmpty':
                self.request('Closing')

            if self.countFullSeats() == 0:
                self.wantState = 'closed'
            else:
                self.wantState = 'opening'
        else:
            self.wantState = 'waitEmpty'
            if self.state == 'Closed':
                self.request('Opening')

        # To avoid infinite recursion, only lock the other if it has the lock other flag
        otherElevator = self.getOtherElevator()
        if otherElevator and lockOther:
            otherElevator.setIsLocked(locked, lockOther=False)

    def getLocked(self):
        return self.isLocked

    def unlock(self):
        if self.isLocked:
            self.setIsLocked(0)

    def lock(self):
        if not self.isLocked:
            self.setIsLocked(1)

    def setUnlockEvent(self, event):
        if self.unlockEvent:
            self.ignore(self.unlockEvent)
        self.unlockEvent = self.getOutputEventName(event)
        if self.unlockEvent:
            self.accept(self.unlockEvent, self.setIsUnlocked)

    def setIsUnlocked(self, isUnlocked):
        if isUnlocked:
            self.unlock()
        else:
            self.lock()

    def start(self):
        self.quickBoardTask = self.uniqueName('quickBoard')
        if self.isLocked:
            self.wantState = 'closed'
            self.request('Closed')
        else:
            self.wantState = 'waitEmpty'
            self.request('Opening')

    def getOtherElevator(self):
        # Make sure the other elevator is generated (or exists in general) before trying to do anything with it.
        otherElevator = self.level.getEntity(self.exitElevator)
        if otherElevator and isinstance(otherElevator, DistributedQuickElevatorEntityAI):
            return otherElevator

        return None

    def beClosed(self):
        pass

    def setEntering(self, entering):
        self.isEntering = entering

    def getEntering(self):
        return self.isEntering

    def enterClosed(self, clearSeats=1):
        DistributedElevatorFSMAI.DistributedElevatorFSMAI.enterClosed(self)
        if self.wantState == 'closed':
            return
        self.demand('Opening', [clearSeats])

    def enterOff(self):
        self.lastState = self.state
        if self.wantState == 'closed':
            self.demand('Closing')
        elif self.wantState == 'waitEmpty':
            self.demand('WaitEmpty')

    def sendToonsToOtherElevator(self, toons):
        otherElevator = self.getOtherElevator()
        if otherElevator:
            otherElevator.transferToons(self.entId, toons)
        self.inTransfer = False

    def transferToons(self, otherElevatorEntId, toons):
        otherElevator = self.level.getEntity(otherElevatorEntId)
        if otherElevator:
            for seatIndex in range(len(otherElevator.seats)):
                avId = otherElevator.seats[seatIndex]
                if avId:
                    otherElevator.clearFullNow(seatIndex)
                    otherElevator.clearEmptyNow(seatIndex)
                    # Forcefully ensure they are no longer in the boarding list for the other elevator.
                    otherElevator.d_forceRemoveToon(avId, seatIndex, self.entId)
        for i, toon in enumerate(toons):
            self.acceptBoarder(toon, i, transfer=1)

        def openFunc(task=None):
            elevatorList = [elevator for elevator in (self, otherElevator) if elevator]
            for elevator in elevatorList:
                elevator.wantState = 'opening'
                elevator.request('Opening')

        taskMgr.doMethodLater(ElevatorData[self.type]['openTime'] / 2, openFunc, 'elevatorTransferOpenDoors')

    def d_forceRemoveToon(self, avId, index, elevatorId):
        self.sendUpdate('forceRemoveToon', [avId, index, elevatorId])

    def delete(self):
        self.ignoreAll()
        for seatIndex in range(len(self.seats)):
            avId = self.seats[seatIndex]
            if avId:
                self.clearFullNow(seatIndex)
                self.clearEmptyNow(seatIndex)

        DistributedEntityAI.DistributedEntityAI.delete(self)

    def destroy(self):
        self.notify.info('destroy entity(quickElevatorEntityAI) %s' % self.entId)
        DistributedEntityAI.DistributedEntityAI.destroy(self)
