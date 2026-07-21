from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import globalClockDelta
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI

class DistributedMajorPlayerInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedMajorPlayerInteriorAI')

    def __init__(self, air, block, zoneId, building):
        DistributedToonInteriorAI.__init__(self, air, block, zoneId, building)
        self.boardingSlots = [None, None, None, None]
        self.boardingLocked = False

    def delete(self):
        self.boardingSlots = [None, None, None, None]
        self.ignoreAll()
        DistributedToonInteriorAI.delete(self)

    def __findAvatarSlot(self, avId):
        for index in xrange(len(self.boardingSlots)):
            if self.boardingSlots[index] == avId:
                return index
        return None

    def __findOpenSlot(self):
        for index in xrange(len(self.boardingSlots)):
            if self.boardingSlots[index] is None:
                return index
        return None

    def __sendFillSlot(self, slotIndex, avId):
        self.sendUpdate('fillSlot%s' % slotIndex, [avId, 0])

    def __sendEmptySlot(self, slotIndex, avId):
        self.sendUpdate(
            'emptySlot%s' % slotIndex,
            [
                avId,
                0,
                globalClockDelta.getRealNetworkTime(),
                0
            ]
        )

    def requestBoard(self):
        avId = self.air.getAvatarIdFromSender()

        if not avId:
            return

        if self.boardingLocked:
            self.sendUpdateToAvatarId(avId, 'rejectBoard', [avId, 0])
            return

        currentSlot = self.__findAvatarSlot(avId)
        if currentSlot is not None:
            return

        av = self.air.doId2do.get(avId)
        if not av or av.getHp() <= 0:
            self.sendUpdateToAvatarId(avId, 'rejectBoard', [avId, 0])
            return

        slotIndex = self.__findOpenSlot()
        if slotIndex is None:
            self.sendUpdateToAvatarId(avId, 'rejectBoard', [avId, 3])
            return

        wasEmpty = all(slot is None for slot in self.boardingSlots)

        self.boardingSlots[slotIndex] = avId
        self.acceptOnce(
            self.air.getAvatarExitEvent(avId),
            self.__handleAvatarExit,
            [avId]
        )
        self.__sendFillSlot(slotIndex, avId)

        if wasEmpty:
            self.sendUpdate(
                'setBoardingState',
                [
                    'countdown',
                    globalClockDelta.getRealNetworkTime()
                ]
            )

    def requestExit(self):
        avId = self.air.getAvatarIdFromSender()

        if not avId:
            return

        slotIndex = self.__findAvatarSlot(avId)
        if slotIndex is None:
            return

        if self.boardingLocked:
            return

        self.__clearSlot(slotIndex, avId)

    def __handleAvatarExit(self, avId):
        slotIndex = self.__findAvatarSlot(avId)
        if slotIndex is not None:
            self.__clearSlot(slotIndex, avId)

    def __clearSlot(self, slotIndex, avId):
        if slotIndex < 0 or slotIndex >= len(self.boardingSlots):
            return

        if self.boardingSlots[slotIndex] != avId:
            return

        self.boardingSlots[slotIndex] = None
        self.ignore(self.air.getAvatarExitEvent(avId))
        self.__sendEmptySlot(slotIndex, avId)

    def __allSlotsFilled(self):
        self.boardingLocked = True
        self.sendUpdate(
            'setBoardingState',
            [
                'ready',
                globalClockDelta.getRealNetworkTime()
            ]
        )

    def resetBoarding(self):
        for slotIndex in xrange(len(self.boardingSlots)):
            avId = self.boardingSlots[slotIndex]
            if avId is not None:
                self.__sendEmptySlot(slotIndex, avId)
                self.ignore(self.air.getAvatarExitEvent(avId))

        self.boardingSlots = [None, None, None, None]
        self.boardingLocked = False
        self.sendUpdate(
            'setBoardingState',
            [
                'open',
                globalClockDelta.getRealNetworkTime()
            ]
        )

    def getBoardingSlots(self):
        result = []
        for avId in self.boardingSlots:
            if avId is None:
                result.append(0)
            else:
                result.append(avId)
        return result
