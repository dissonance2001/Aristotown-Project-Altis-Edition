import math
import random

from direct.directnotify import DirectNotifyGlobal
from panda3d.core import *

from toontown.coghq import DistributedCashbotBossTreasureAI
from toontown.duckhuntbossbattle import DistributedFourBossGoonAI
from toontown.duckhuntbossbattle.DistributedRebornBossCogAI import DistributedRebornBossCogAI
from toontown.toonbase import ToontownGlobals


class DistributedCEOBossAI(DistributedRebornBossCogAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCEOBossAI')

    def __init__(self, air, parent=None):
        DistributedRebornBossCogAI.__init__(self, air, 'c', parent)

        # CEO's max health.
        self.bossMaxDamage = 2652

        # Set up the scene.
        self.scene = NodePath('scene')
        self.reparentTo(self.scene)

        # Boundaries the Goons can walk in.
        frontBackWallsNode = CollisionNode('frontBackWalls')
        backWall = CollisionSphere(0, 6700, 0, 155)
        frontBackWallsNode.addSolid(backWall)
        frontWall = CollisionSphere(0, -7700, 0, 155)
        frontBackWallsNode.addSolid(frontWall)
        sideWallsNode = CollisionNode('sideWalls')
        leftWall = CollisionSphere(0, 13500, 0, 135)
        sideWallsNode.addSolid(leftWall)
        rightWall = CollisionSphere(0, -13500, 0, 135)
        sideWallsNode.addSolid(rightWall)

        # Misc. Boundaries.
        podiumNode = CollisionNode('podiums')
        vpPodium = CollisionSphere(-52, 39, 0, 17)
        podiumNode.addSolid(vpPodium)
        cfoPodium = CollisionSphere(46, 39, 0, 17)
        podiumNode.addSolid(cfoPodium)
        vpPapers = CollisionSphere(-52, 59, 0, 12)
        podiumNode.addSolid(vpPapers)

        # Attach to CEO.
        frontBackWallsMake = self.attachNewNode(frontBackWallsNode)
        frontBackWallsMake.setScale(1, 0.01, 1)
        sideWallsMake = self.attachNewNode(sideWallsNode)
        sideWallsMake.setScale(1, 0.01, 1)
        sideWallsMake.setH(90)
        self.attachNewNode(podiumNode)

        # Goon Information.
        self.maxGoons = 30
        self.goons = []

        # Treasures.
        self.treasures = {}
        self.grabbingTreasures = {}
        self.recycledTreasures = []

        # Attack Information.
        self.movingToChandelier = False
        self.chandelierDest = -1
        self.curChandelier = -1
        self.doAttacks = False
        self.inLargeAttack = False

    def disable(self):
        DistributedRebornBossCogAI.disable(self)
        self.stopGoons()
        self.deleteAllTreasures()
        self.deleteGoons()
        self.removeAllTasks()
        self.ignoreAll()
        self.scene.removeNode()
        self.scene = None

    def getMaxGoons(self):
        t = self.getBattleTwoTime()
        if t <= 1.0:
            return self.maxGoons
        elif t <= 1.1:
            return self.maxGoons + 2
        elif t <= 1.2:
            return self.maxGoons + 3
        elif t <= 1.3:
            return self.maxGoons + 4
        elif t <= 1.4:
            return self.maxGoons + 5
        else:
            return self.maxGoons + 6

    def makeGoon(self, side=None, ignoreMax=False):
        if not self.air:
            return
        if not self._parent.air:
            return
        if self.inLargeAttack:
            return
        if self.getIsDead():
            return
        if self._parent.getCurrentOrNextState() != 'BattleTwo':
            return
        if side is None:
            side = random.choice(['EmergeC', 'EmergeD'])
        goon = self.__chooseOldGoon()
        if goon is None:
            if len(self.goons) >= self.getMaxGoons() and not ignoreMax:
                return
            goon = DistributedFourBossGoonAI.DistributedFourBossGoonAI(self.air, self)
            goon.generateWithRequired(self.zoneId)
            self.goons.append(goon)
        if self.getBattleTwoTime() >= 2.5:
            goon.STUN_TIME = 4
            goon.b_setupGoon(velocity=12, hFov=90, attackRadius=15, strength=40, scale=2)
        else:
            goon.STUN_TIME = self.progressValue(15, 8)
            goon.b_setupGoon(velocity=self.progressRandomValue(3, 9), hFov=self.progressRandomValue(80, 90),
                             attackRadius=self.progressRandomValue(8, 14),
                             strength=int(self.progressRandomValue(12, 35)), scale=self.progressRandomValue(1.2, 2))
        goon.request(side)
        return

    def __chooseOldGoon(self):
        for goon in self.goons:
            if goon.state == 'Off':
                return goon

    def waitForNextGoon(self, delayTime):
        currState = self._parent.getCurrentOrNextState()
        if currState == 'BattleTwo':
            taskName = self.uniqueName('NextGoon')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.doNextGoon, taskName)

    def stopGoons(self):
        taskName = self.uniqueName('NextGoon')
        taskMgr.remove(taskName)

    def doNextGoon(self, task):
        if self.getIsDead():
            return task.done
        if self.attackCode != ToontownGlobals.BossCogDizzy:
            self.makeGoon()
        delayTime = self.progressValue(26, 10)  # 26. Spooky.
        self.waitForNextGoon(delayTime)

    def progressValue(self, fromValue, toValue):
        t0 = float(self.bossDamage) / float(self.bossMaxDamage)
        elapsed = globalClock.getFrameTime() - self.battleTwoStart
        t1 = elapsed / float(self.battleTwoDuration)
        t = max(t0, t1)
        return fromValue + (toValue - fromValue) * min(t, 1)

    def progressRandomValue(self, fromValue, toValue, radius=0.2):
        t = self.progressValue(0, 1)
        radius = radius * (1.0 - abs(t - 0.5) * 2.0)
        t += radius * random.uniform(-1, 1)
        t = max(min(t, 1.0), 0.0)
        return fromValue + (toValue - fromValue) * t

    def doInitialGoons(self, task):
        self.makeGoon(side='EmergeC')
        self.makeGoon(side='EmergeD')
        self.waitForNextGoon(10)
        return task.done

    def makeTreasure(self, goon):
        if self._parent.getCurrentOrNextState() != 'BattleTwo':
            return
        pos = goon.getPos(self)
        v = Vec3(pos[0], pos[1], 0.0)
        if not v.normalize():
            v = Vec3(1, 0, 0)
        v = v * 27
        angle = random.uniform(0.0, 2.0 * math.pi)
        radius = 10
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        fpos = self.scene.getRelativePoint(self, Point3(v[0] + dx, v[1] + dy, 0))
        style = random.choice([ToontownGlobals.MyEstate, ToontownGlobals.ToontownCentral])
        if style == ToontownGlobals.MyEstate:
            healAmount = 2
        else:
            healAmount = 3
        if self.recycledTreasures:
            treasure = self.recycledTreasures.pop(0)
            treasure.d_setGrab(0)
            treasure.b_setGoonId(goon.doId)
            treasure.b_setStyle(style)
            treasure.b_setPosition(pos[0], pos[1], 0)
            treasure.b_setFinalPosition(fpos[0], fpos[1], 0)
        else:
            treasure = DistributedCashbotBossTreasureAI.DistributedCashbotBossTreasureAI(self.air, self, goon, style,
                                                                                         fpos[0], fpos[1], 0)
            treasure.generateWithRequired(self.zoneId)
        treasure.healAmount = healAmount
        self.treasures[treasure.doId] = treasure

    def grabAttempt(self, avId, treasureId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        treasure = self.treasures.get(treasureId)
        if treasure:
            if treasure.validAvatar(av):
                del self.treasures[treasureId]
                treasure.d_setGrab(avId)
                self.grabbingTreasures[treasureId] = treasure
                taskMgr.doMethodLater(5, self.__recycleTreasure, treasure.uniqueName('recycleTreasure'),
                                      extraArgs=[treasure])
            else:
                treasure.d_setReject()

    def __recycleTreasure(self, treasure):
        if treasure.doId in self.grabbingTreasures:
            del self.grabbingTreasures[treasure.doId]
            self.recycledTreasures.append(treasure)

    def deleteAllTreasures(self):
        for treasure in list(self.treasures.values()):
            treasure.requestDelete()

        self.treasures = {}
        for treasure in list(self.grabbingTreasures.values()):
            taskMgr.remove(treasure.uniqueName('recycleTreasure'))
            treasure.requestDelete()

        self.grabbingTreasures = {}
        for treasure in self.recycledTreasures:
            treasure.requestDelete()

        self.recycledTreasures = []

    def addRetaliationPoints(self, points):
        if self._parent.cfoBoss:
            self._parent.cfoBoss.addRetaliationPoints(points)

    def doNextAttack(self, task):
        if self.getIsDead():
            return task.done

        currState = self._parent.getCurrentOrNextState()

        if currState == 'BattleTwo':
            if self._parent.assignedLargeAttack == self:
                if self._parent.getAliveBosses() == [self]:
                    return
                self.doLargeAttack()
            self.waitForNextAttack(5)
        elif currState == 'BattleThree':
            attackCode = -1
            if self.movingToChandelier:
                self.waitForNextAttack(5)
            else:
                attackCode = random.choice([
                    ToontownGlobals.BossCogGolfAreaAttack,
                    ToontownGlobals.BossCogAreaAttack,
                    ToontownGlobals.BossCogDirectedAttack,
                    ToontownGlobals.BossCogDirectedAttack,
                    ToontownGlobals.BossCogDirectedAttack,
                    ToontownGlobals.BossCogDirectedAttack,
                    ToontownGlobals.BossCogDirectedAttack,
                    ToontownGlobals.BossCogDirectedAttack,
                    ToontownGlobals.BossCogDirectedAttack,
                    ToontownGlobals.BossCogDirectedAttack])
            if attackCode == ToontownGlobals.BossCogDirectedAttack:
                self.__doDirectedAttack()
            elif attackCode >= 0:
                self.b_setAttackCode(attackCode)
        return

    def doLargeAttack(self):
        self.inLargeAttack = True
        self.b_setAttackCode(ToontownGlobals.BossCogGearWaveAttack)
        taskMgr.doMethodLater(4.21, self.__destroyGoons, self.uniqueName('destroyGoons'))
        taskMgr.doMethodLater(13.21, self.__resetInLargeAttack, self.uniqueName('resetInLargeAttack'))
        self._parent.assignedLargeAttack = None
        self._parent.waitForNextLargeAttack(20)

    def getToon(self):
        returnedToonId = 0
        maxToons = []
        for toonId in self._parent.involvedToons:
            maxToons.append(toonId)

        if maxToons:
            returnedToonId = random.choice(maxToons)
        return returnedToonId

    def getUprightChandeliers(self):
        chandelierList = []
        for chandelier in self._parent.chandeliers:
            if not chandelier.flattened:
                chandelierList.append(chandelier.index)

        return chandelierList

    def getToonChandelierIndex(self, toonId):
        chandelierIndex = -1
        for chandelier in self._parent.chandeliers:
            if chandelier.avId == toonId:
                chandelierIndex = chandelier.index
                break

        return chandelierIndex

    def isToonOnChandelier(self, toonId):
        result = self.getToonChandelierIndex(toonId) != -1
        return result

    def isToonRoaming(self, toonId):
        result = not self.isToonOnChandelier(toonId)
        return result

    def reachedChandelier(self, chandelierIndex):
        if self.movingToChandelier and self.chandelierDest == chandelierIndex:
            self.movingToChandelier = False
            self.curChandelier = self.chandelierDest
            self.chandelierDest = -1

    def hitChandelier(self, chandelierIndex):
        self.notify.debug('hitChandelier chandelierIndex=%d' % chandelierIndex)
        if chandelierIndex < len(self._parent.chandeliers):
            chandelier = self._parent.chandeliers[chandelierIndex]
            if not chandelier.flattened:
                chandelier.setFlattened(True)

    def awayFromChandelier(self, chandelierIndex):
        self.notify.debug('awayFromChandelier chandelierIndex=%d' % chandelierIndex)
        if chandelierIndex < len(self._parent.chandeliers):
            taskName = 'Unflatten-%d' % chandelierIndex
            taskMgr.doMethodLater(9.0, self.unflattenChandelier, taskName, extraArgs=[chandelierIndex])

    def unflattenChandelier(self, chandelierIndex):
        if chandelierIndex < len(self._parent.chandeliers):
            chandelier = self._parent.chandeliers[chandelierIndex]
            if chandelier.flattened:
                chandelier.setFlattened(False)

    def hitByChandelier(self, chandelierIndex):
        self.notify.debug('hitChandelier chandelierIndex=%d' % chandelierIndex)
        if chandelierIndex < len(self._parent.chandeliers):
            chandelier = self._parent.chandeliers[chandelierIndex]
            if not chandelier.gracePeriod:
                damage = random.randint(25, 75)
                chandelier.runGracePeriod()
                self.recordHit(damage)

    def recordHit(self, damage):
        currState = self._parent.getCurrentOrNextState()
        if currState != 'BattleThree':
            return
        self.b_setBossDamage(self.bossDamage + damage)
        if self.bossDamage >= self.bossMaxDamage:
            self._parent.b_setState('Victory')
        elif self.attackCode != ToontownGlobals.BossCogDizzyRecover:
            self.b_setAttackCode(ToontownGlobals.BossCogDizzyRecover)

    def b_setBossDamage(self, bossDamage):
        self.d_setBossDamage(bossDamage)
        self.setBossDamage(bossDamage)

    def setBossDamage(self, bossDamage):
        self.bossDamage = bossDamage

    def d_setBossDamage(self, bossDamage):
        self.sendUpdate('setBossDamage', [bossDamage])

    def __doDirectedAttack(self):
        toonId = self.getToon()
        self.notify.debug('toonToAttack=%s' % toonId)
        if toonId:
            if self.isToonRoaming(toonId):
                self.b_setAttackCode(ToontownGlobals.BossCogGolfAttack, toonId)
            elif self.isToonOnChandelier(toonId):
                chandelierIndex = self.getToonChandelierIndex(toonId)
                self.doMoveAttack(chandelierIndex)
            else:
                self.b_setAttackCode(ToontownGlobals.BossCogGolfAttack, toonId)
        else:
            chandeliersWithToons = []
            if self._parent.involvedToons:
                for toonId in self._parent.involvedToons:
                    chandelierIndex = self.getToonChandelierIndex(toonId)
                    if chandelierIndex > -1 and self._parent.chandeliers[chandelierIndex].state == 'Controlled':
                        chandeliersWithToons.append(chandelierIndex)
            uprightChandeliers = self.getUprightChandeliers()
            chandelierToMoveTo = None
            if chandeliersWithToons:
                chandelierToMoveTo = random.choice(chandeliersWithToons)
                if chandelierToMoveTo == self.curChandelier:
                    remainingChandeliers = self._parent.chandeliers[:]
                    remainingChandeliers.remove(self._parent.chandeliers[chandelierToMoveTo])
                    chandelierToMoveTo = (random.choice(remainingChandeliers)).index
            elif uprightChandeliers:
                chandelierToMoveTo = random.choice(uprightChandeliers)

            if chandelierToMoveTo:
                self.doMoveAttack(chandelierToMoveTo)
            else:
                self.waitForNextAttack(4)

    def doMoveAttack(self, chandelierIndex):
        self.movingToChandelier = True
        self.chandelierDest = chandelierIndex
        self.b_setAttackCode(ToontownGlobals.BossCogMoveAttack, chandelierIndex)

    def __destroyGoons(self, task):
        for goon in self.goons:
            damage = random.randint(20, 100)
            goon.b_damageGoon(damage)

        return task.done

    def __resetInLargeAttack(self, task):
        self.inLargeAttack = False
        return task.done

    def beginFinalBattle(self):
        self.waitForNextAttack(5)

    def d_beginFinalBattle(self):
        self.sendUpdate('beginFinalBattle', [])

    def b_beginFinalBattle(self):
        self.beginFinalBattle()
        self.d_beginFinalBattle()

    def deleteGoons(self):
        if self.goons:
            for goon in self.goons:
                goon.requestDelete()

        self.goons = []
