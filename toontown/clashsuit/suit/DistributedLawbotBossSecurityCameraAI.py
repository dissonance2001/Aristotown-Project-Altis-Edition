import random
from toontown.ai.AIBase import *
from direct.distributed import DistributedNodeAI


class DistributedLawbotBossSecurityCameraAI(DistributedNodeAI.DistributedNodeAI, NodePath):

    def __init__(self, air, boss, posList, damage, tracking=0):
        node = hidden.attachNewNode('DistributedLawbotBossSecurityCameraAI')
        DistributedNodeAI.DistributedNodeAI.__init__(self, air)
        NodePath.__init__(self, node)
        self.boss = boss
        self.bossId = boss.doId
        self.positions = posList
        self.currentPos = None
        self.damPow = damage
        self.velocity = 0
        self.acceleration = 0
        self.tracking = tracking
        self.trackingDoId = None

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        DistributedNodeAI.DistributedNodeAI.generate(self)

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedNodeAI.DistributedNodeAI.announceGenerate(self)
        pos = self.positions.pop(0)
        self.d_setPosHpr(pos[0], pos[1], pos[2], 0, 0, 0)
        if not self.tracking:
            self.waitForNextMove(3)

    def waitForNextMove(self, delayTime):
        taskName = self.uniqueName('NextMove')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.doNextMove, taskName)

    def doNextMove(self, task):
        if self.currentPos:
            self.currentPos = random.choice(self.positions)
        else:
            self.currentPos = self.positions[0]
        self.updatePosition(self.currentPos)
        self.waitForNextMove(1 + random.random()*4.0)
        return

    def updatePosition(self, pos):
        self.sendUpdate('newPosition', [pos[0], pos[1]])

    def delete(self):
        taskMgr.remove(self.uniqueName('NextMove'))
        self.ignoreAll()
        self.positions = None
        self.boss = None
        DistributedNodeAI.DistributedNodeAI.delete(self)

    def destroy(self):
        DistributedNodeAI.DistributedNodeAI.destroy(self)

    def trapFire(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.boss.involvedToons:
            return
        toon = self.air.doId2do.get(avId)
        if toon:
            if self.tracking:
                damage = math.floor(self.boss.progressValue(10, 20) * self.boss.damageMult)
            else:
                damage = math.floor(self.damPow * self.boss.damageMult)
            toon.takeDamage(damage)

    def b_setVelocity(self, velocity):
        self.d_setVelocity(velocity)
        self.setVelocity(velocity)

    def d_setVelocity(self, velocity):
        self.sendUpdate('setVelocity', [velocity])

    def setVelocity(self, velocity):
        self.velocity = velocity

    def b_setAcceleration(self, acceleration):
        self.d_setAcceleration(acceleration)
        self.setAcceleration(acceleration)

    def d_setAcceleration(self, acceleration):
        self.sendUpdate('setAcceleration', [acceleration])

    def setAcceleration(self, acceleration):
        self.acceleration = acceleration

    def b_setTrackingDoId(self, doId):
        self.d_setTrackingDoId(doId)
        self.setTrackingDoId(doId)

    def d_setTrackingDoId(self, doId):
        self.sendUpdate('setTrackingDo', [doId])

    def setTrackingDoId(self, doId):
        self.trackingDoId = doId
