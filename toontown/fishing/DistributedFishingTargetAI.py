from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.distributed.ClockDelta import *
from toontown.fishing import FishingTargetGlobals
import random
import math

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedFishingTargetAI(DistributedNodeAI):
    """
    DistributedFishingTargetAI(DistributedNodeAI)
    """

    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        self.pondId = 0
        self.angle = 0
        self.targetRadius = 0
        self.time = 0
        self.centerPoint = [0, 0, 0]

    def generate(self):
        DistributedNodeAI.generate(self)
        self.updateState()
        if not self.pondId:
            self.notify.warning("we don't have a pond ID for some reason?")
            # We don't have a pond ID for some reason...
            return
        
        pond = self.air.doId2do[self.pondId]
        pond.addTarget(self)
        self.centerPoint = FishingTargetGlobals.getTargetCenter(pond.getArea())

    def delete(self):
        taskMgr.remove('updateFishingTarget%d' % self.doId)

        DistributedNodeAI.delete(self)

    def setPondDoId(self, pondId):
        self.pondId = pondId

    def getPondDoId(self):
        return self.pondId

    def setState(self, stateIndex, angle, radius, time, timeStamp):
        self.angle = angle
        self.targetRadius = radius
        self.time = time

    def getState(self):
        return [0, self.angle, self.targetRadius, self.time, globalClockDelta.getRealNetworkTime()]

    def updateState(self):
        if not self.pondId in self.air.doId2do:
            return
        self.b_setPosHpr(self.targetRadius * math.cos(self.angle) + self.centerPoint[0], self.targetRadius * math.sin(self.angle) + self.centerPoint[1], self.centerPoint[2], 0, 0, 0)
        self.angle = random.randrange(359)
        self.targetRadius = random.uniform(FishingTargetGlobals.getTargetRadius(self.air.doId2do[self.pondId].getArea()), 0)
        self.time = random.uniform(10.0, 5.0)
        self.sendUpdate('setState', [0, self.angle, self.targetRadius, self.time, globalClockDelta.getRealNetworkTime()])
        taskMgr.doMethodLater(self.time + random.uniform(5, 2.5), DistributedFishingTargetAI.updateState, 'updateFishingTarget%d' % self.doId, [self])
