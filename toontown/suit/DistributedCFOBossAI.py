import random

from direct.distributed.ClockDelta import *

from toontown.duckhuntbossbattle import FourBossBattleGlobals
from toontown.duckhuntbossbattle.DistributedRebornBossCogAI import DistributedRebornBossCogAI
from toontown.toonbase import ToontownGlobals


class DistributedCFOBossAI(DistributedRebornBossCogAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCFOBossAI')

    def __init__(self, air, parent=None):
        DistributedRebornBossCogAI.__init__(self, air, 'm', parent)
        self.bossDamage = 0
        self.bossMaxDamage = 24
        self.deathTime = 16.193
        self.deathReady = True
        self.assignedRetaliationAttack = False
        self.retaliationPoints = 0
        self.toonsWithWood = []
        self.woodBeingCarried = []
        self.placedWood = []
        self.lastToon = 0

    def disable(self):
        DistributedRebornBossCogAI.disable(self)
        self.removeAllTasks()
        self.ignoreAll()

    def doNextAttack(self, task):
        isDead = self.getIsDead()[0]
        if isDead:
            return task.done

        if self._parent.assignedLargeAttack == self:
            self.doLargeAttack()
        elif self.assignedRetaliationAttack:
            self.b_setAttackCode(ToontownGlobals.BossCogGoonRetaliationAttack)
            taskMgr.doMethodLater(4.21, self.__stunGoons, self.uniqueName('stunGoons'))
            self.assignedRetaliationAttack = False
        else:
            self.b_setAttackCode(ToontownGlobals.BossCogMoneyTornadoAttack, 0, random.randint(0, 4),
                                 random.randint(0, 4), self.progressValue(1, 3))

    def addRetaliationPoints(self, points):
        self.retaliationPoints += points
        if self.retaliationPoints >= 75:
            self.retaliationPoints = 0
            self.assignedRetaliationAttack = True

    def __stunGoons(self, task):
        for goon in self._parent.ceoBoss.goons:
            goon.immidiateStun(10)
        return task.done

    def doLargeAttack(self):
        delay = 0
        for x in range(4):
            if len(self._parent.ceoBoss.goons) >= self._parent.ceoBoss.maxGoons:
                break
            taskMgr.doMethodLater(delay, self._parent.ceoBoss.makeGoon, self.uniqueName('cfoSpawnGoonsC'),
                                  extraArgs=['EmergeC', True])
            if len(self._parent.ceoBoss.goons) >= self._parent.ceoBoss.maxGoons:
                break
            taskMgr.doMethodLater(delay, self._parent.ceoBoss.makeGoon, self.uniqueName('cfoSpawnGoonsD'),
                                  extraArgs=['EmergeD', True])
            delay += 4

        self.b_setAttackCode(ToontownGlobals.BossCogLargeAttack)
        self._parent.assignedLargeAttack = None
        self._parent.waitForNextLargeAttack(20)

    def requestGrabWood(self, index):
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            return

        if avId in self.toonsWithWood:
            return

        if index in self.woodBeingCarried:
            return

        if avId not in self._parent.involvedToons:
            return

        if index not in range(len(FourBossBattleGlobals.WoodPilePosHprs)):
            return

        currState = self._parent.getCurrentOrNextState()
        if currState != 'BattleTwo':
            return

        self.toonsWithWood.append(avId)
        self.woodBeingCarried.append(index)
        self.sendUpdate('grabWood', [avId, index])

    def requestPlaceWood(self, index):
        avId = self.air.getAvatarIdFromSender()
        if not avId:
            return

        if avId not in self.toonsWithWood:
            return

        if index in self.placedWood:
            return

        if index not in self.woodBeingCarried:
            return

        if avId not in self._parent.involvedToons:
            return

        if index not in range(len(FourBossBattleGlobals.WoodPilePosHprs)):
            return

        currState = self._parent.getCurrentOrNextState()
        if currState != 'BattleTwo':
            return

        self.toonsWithWood.remove(avId)
        self.woodBeingCarried.remove(index)
        self.placedWood.append(index)
        self.sendUpdate('placeWood', [avId, index])

        self.bossDamage += 1

        if currState != 'BattleTwo':
            return
        isDead = self.getIsDead()[0]
        if not isDead and not self.bossDamage >= self.bossMaxDamage:
            return

        if self.bossDamage == self.bossMaxDamage:
            self.sendUpdate('displayFinalHit', [])
            return

    def finalHit(self):
        self.bossDamage += 1

        if self.bossDamage != self.bossMaxDamage + 1:
            return

        avId = self.air.getAvatarIdFromSender()
        if not avId:
            return

        if not self._parent.cjBoss.isDead:
            self.deathReady = True
            taskMgr.doMethodLater(5.0, self.b_setIsDead, self.uniqueName('setIsDead'), extraArgs=[True, avId])
            return

        self.b_setIsDead(True, avId)

    def requestDropWood(self, index):
        avId = self.air.getAvatarIdFromSender()

        if not avId:
            return

        if avId not in self.toonsWithWood:
            return

        if index in self.placedWood:
            return

        if index not in self.woodBeingCarried:
            return

        if avId not in self._parent.involvedToons:
            return

        if index not in range(len(FourBossBattleGlobals.WoodPilePosHprs)):
            return

        currState = self._parent.getCurrentOrNextState()
        if currState != 'BattleTwo':
            return

        self.toonsWithWood.remove(avId)
        self.woodBeingCarried.remove(index)
        self.sendUpdate('dropWood', [avId, index])

    def progressValue(self, fromValue, toValue):
        t0 = float(self.bossDamage) / float(self.bossMaxDamage)
        elapsed = globalClock.getFrameTime() - self.battleTwoStart
        t1 = elapsed / float(self.battleTwoDuration)
        t = max(t0, t1)
        return fromValue + (toValue - fromValue) * min(t, 1)

    def b_setAttackCode(self, attackCode, avId=0, pathNum=None, spawnNum=None, tornadoNum=1):
        self.d_setAttackCode(attackCode, avId, pathNum, spawnNum, tornadoNum)
        self.setAttackCode(attackCode, avId)

    def d_setAttackCode(self, attackCode, avId=0, pathNum=None, spawnNum=None, tornadoNum=1):
        if pathNum == None:
            pathNum = 5
            spawnNum = 5
        self.sendUpdate('setAttackCode', [attackCode, avId, pathNum, spawnNum, tornadoNum])

    def d_setIsDead(self, isDead, toon):
        dingDing = False
        if isDead:
            # Now we determine either to do the
            # trolley easter egg or not... Most likely not. :'(
            if random.randint(0, 20) == 20:
                dingDing = True
        self.sendUpdate('setIsDead', [isDead, dingDing, toon])

    def b_setIsDead(self, isDead, toon):
        self.setIsDead(isDead)
        self.d_setIsDead(isDead, toon)

    def getIsDead(self):
        return self.isDead, False, 0

    def __handleDeath(self, task=None):
        self.requestDelete()
        self._parent.cfoBoss = None
        if task:
            return task.done
