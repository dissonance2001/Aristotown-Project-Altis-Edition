import random

from direct.distributed.ClockDelta import *

from toontown.duckhuntbossbattle import FourBossBattleGlobals
from toontown.duckhuntbossbattle.DistributedRebornBossCogAI import DistributedRebornBossCogAI
from toontown.toonbase import ToontownGlobals


class DistributedVPBossAI(DistributedRebornBossCogAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedVPBossAI')
    limitHitCount = 6
    hitCountDamage = 35

    def __init__(self, air, parent=None):
        DistributedRebornBossCogAI.__init__(self, air, 's', parent)
        self.recoverRate = 0
        self.recoverStartTime = 0
        self.bossMaxDamage = 30
        self.deathTime = 7
        self.wasHitLastStun = False

    def disable(self):
        DistributedRebornBossCogAI.disable(self)
        self.removeAllTasks()
        self.ignoreAll()

    def b_setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        self.d_setBossDamage(bossDamage, recoverRate, recoverStartTime)
        self.setBossDamage(bossDamage, recoverRate, recoverStartTime)

    def setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        self.bossDamage = bossDamage
        self.recoverRate = recoverRate
        self.recoverStartTime = recoverStartTime

    def getBossDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.recoverStartTime
        return int(max(self.bossDamage - self.recoverRate * elapsed / 60.0, 0))

    def d_setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        timestamp = globalClockDelta.localToNetworkTime(recoverStartTime)
        self.sendUpdate('setBossDamage', [bossDamage, recoverRate, timestamp])

    def hitBoss(self, bossDamage):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self._parent.involvedToons, 'hitBoss from unknown avatar'):
            return
        self.validate(avId, bossDamage == 1, 'invalid bossDamage %s' % bossDamage)
        if bossDamage < 1:
            return
        currState = self._parent.getCurrentOrNextState()
        if currState != 'BattleTwo':
            return
        if self.attackCode != ToontownGlobals.BossCogDizzyNow:
            return
        bossDamage = min(self.getBossDamage() + bossDamage, self.bossMaxDamage)
        self.wasHitLastStun = True
        self.b_setBossDamage(bossDamage, 0, 0)
        if self.bossDamage >= self.bossMaxDamage:
            self.b_setIsDead(True)
        else:
            self.__recordHit()

    def hitBossInsides(self):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self._parent.involvedToons, 'hitBossInsides from unknown avatar'):
            return
        currState = self._parent.getCurrentOrNextState()
        if currState != 'BattleTwo':
            return
        self.wasHitLastStun = False
        taskMgr.remove(self.uniqueName("recoverFromStun"))
        self.b_setAttackCode(ToontownGlobals.BossCogDizzyNow)
        self.b_setBossDamage(self.getBossDamage(), 0, 0)

    def __recordHit(self):
        self.hitCount += 1
        if self.hitCount < self.limitHitCount or self.bossDamage < self.hitCountDamage:
            return
        self.b_setAttackCode(ToontownGlobals.BossCogRecoverDizzyAttack)

    def __handleDeath(self, task=None):
        self.requestDelete()
        self._parent.vpBoss = None
        if task:
            return task.done

    def setAttackCode(self, attackCode, avId=0):
        DistributedRebornBossCogAI.setAttackCode(self, attackCode, avId)
        if attackCode == ToontownGlobals.BossCogDizzyNow:
            taskMgr.doMethodLater(self.progressValue(20, 7.5), self.recoverFromStun, self.uniqueName("recoverFromStun"))

    def recoverFromStun(self, task):
        if not self.wasHitLastStun:
            now = globalClock.getFrameTime()
            self.b_setBossDamage(self.getBossDamage(), FourBossBattleGlobals.VPRecoverRate, now)
        return task.done

    def doNextAttack(self, task):
        if self.getIsDead():
            return task.done

        if self._parent.assignedLargeAttack == self:
            self.doLargeAttack()
        else:
            self.__doDirectedAttack()

        return task.done

    def __doDirectedAttack(self):
        cannonToons = []
        for cannon in self._parent.cannons:
            if cannon.avId != 0:
                cannonToons.append(cannon.avId)

        if cannonToons:
            toonId = random.choice(cannonToons)
        else:
            if self._parent.involvedToons:
                toonId = random.choice(self._parent.involvedToons)
            else:
                self.b_setAttackCode(ToontownGlobals.BossCogCanAttack, 0)
                return

        if toonId:
            self.b_setAttackCode(ToontownGlobals.BossCogCanAttack, toonId)
        else:
            self.b_setAttackCode(ToontownGlobals.BossCogCanAttack, 0)

    def doLargeAttack(self):
        self.b_setAttackCode(ToontownGlobals.BossCogLargeAttack)
        self._parent.assignedLargeAttack = None
        self._parent.waitForNextLargeAttack(20)
