from toontown.building.DistributedDoorWithSpecialSound import DistributedDoorWithSpecialSound
from direct.distributed.ClockDelta import *
from toontown.hood import ZoneUtil

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.distributed.DistributedObject import DistributedObject


@DirectNotifyCategory()
class DistributedLevelDoor(DistributedDoorWithSpecialSound):
    def __init__(self, cr):
        super().__init__(cr)
        self.buildingEntId = 0
        self.levelDoId = 0
        self.level = None
        self.levelRequest = None
        self.__needStateTransition = None
        self.__needExitStateTransition = None
        self.__donePostAnnounceGenerate = False

    def announceGenerate(self):
        # Take over this announce generate so that we can
        # Wait to do postAnnounceGenerate til we have our level
        DistributedObject.announceGenerate(self)

        def onLevelGenerate(levelList, self=self):
            self.level = levelList[0]

            def onEntityReady(self=self):
                self.notify.debug('building ready, setup door')
                self.building = self.level.getEntity(self.buildingEntId)

                self.levelRequest = None

                self.doPostAnnounceGenerate()
                return

            self.level.setEntityCreateCallback(self.buildingEntId, onEntityReady)

        self.levelRequest = self.cr.relatedObjectMgr.requestObjects([self.levelDoId], onLevelGenerate)

    def doPostAnnounceGenerate(self):
        super().doPostAnnounceGenerate()
        self.__donePostAnnounceGenerate = True
        if self.__needStateTransition:
            self.setState(self.__needStateTransition[0], self.__needStateTransition[1])
            self.__needStateTransition = None
        if self.__needExitStateTransition:
            self.setExitDoorState(self.__needExitStateTransition[0], self.__needExitStateTransition[1])
            self.__needExitStateTransition = None

    def disable(self):
        super().disable()
        if self.levelRequest is not None:
            self.cr.relatedObjectMgr.abortRequest(self.levelRequest)
            self.levelRequest = None

    def setBuildingEntId(self, buildingEntId):
        self.buildingEntId = buildingEntId

    def getBuildingEntId(self):
        return self.buildingEntId

    def setLevelDoId(self, levelDoId):
        self.levelDoId = levelDoId

    def getLevelDoId(self):
        return self.levelDoId

    def setState(self, state, timestamp):
        if self.__donePostAnnounceGenerate:
            self.fsm.request(state, [globalClockDelta.localElapsedTime(timestamp)])
        else:
            self.__needStateTransition = (state, timestamp)

    def setExitDoorState(self, state, timestamp):
        if self.__donePostAnnounceGenerate:
            self.exitDoorFSM.request(state, [globalClockDelta.localElapsedTime(timestamp)])
        else:
            self.__needExitStateTransition = (state, timestamp)
