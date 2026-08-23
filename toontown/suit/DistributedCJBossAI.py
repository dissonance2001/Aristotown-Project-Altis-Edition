import random

from direct.distributed.ClockDelta import *
from direct.interval.IntervalGlobal import *
from panda3d.core import *

from otp.ai.MagicWordGlobal import *
from toontown.duckhuntbossbattle.DistributedRebornBossCogAI import DistributedRebornBossCogAI
from toontown.toonbase import ToontownGlobals


class DistributedCJBossAI(DistributedRebornBossCogAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCJBossAI')

    def __init__(self, air, parent=None):
        DistributedRebornBossCogAI.__init__(self, air, 'l', parent)
        self.recoverRate = 0
        self.recoverStartTime = 0
        self.bossMaxDamage = 3000
        self.deathTime = 14.543
        self.isDizzy = False
        self.dontDoLargeAttack = False
        self.roamAttackSeq = None
        self.targetSeq = None

    def disable(self):
        DistributedRebornBossCogAI.disable(self)
        if self.roamAttackSeq:
            self.roamAttackSeq.finish()
        self.roamAttackSeq = None
        if self.targetSeq:
            self.targetSeq.finish()
        self.targetSeq = None
        self.removeAllTasks()
        self.ignoreAll()

    def doNextAttack(self, task):
        if self.getIsDead() or self.getIsDizzy():
            return task.done

        if self._parent.cfoBoss.deathReady:
            self._parent.cfoBoss.deathReady = False
            self.b_setAttackCode(ToontownGlobals.BossCogRoamAttack)
        elif self._parent.assignedLargeAttack == self:
            if not self.dontDoLargeAttack:
                self.doLargeAttack()
            else:
                self._parent.assignedLargeAttack = None
                self._parent.waitForNextLargeAttack(20)
                self.roamAttackSeq = Sequence(self.doRoamAttack())
                self.roamAttackSeq.start()
        else:
            self.roamAttackSeq = Sequence(self.doRoamAttack())
            self.roamAttackSeq.start()

    def findTarget(self):
        involvedToons = self._parent.involvedToons[:]
        if not involvedToons:
            return

        toonToDistance = {}
        for toonId in involvedToons:
            toon = self.air.doId2do.get(toonId)
            if not toon:
                continue

            distance = self.getPos(toon).length()
            toonToDistance[toonId] = distance

        if not toonToDistance:
            return

        targetId = None
        sortedDistances = sorted(toonToDistance.values())
        if len(sortedDistances) >= 2:
            targetDistance = random.choice([sortedDistances[0], sortedDistances[1]])
        else:
            targetDistance = sortedDistances[0]

        for toonId, distance in toonToDistance.items():
            if distance == targetDistance:
                targetId = toonId
                break

        if not targetId:
            return

        self.targetSeq = Sequence(Func(self.b_setAttackCode, ToontownGlobals.BossCogRoamAttack, targetId))
        self.targetSeq.start()

    def doRoamAttack(self):
        return Func(self.findTarget)

    def doLargeAttack(self):
        for bookshelf in self._parent.bookshelves:
            bookshelf.chooseRandomTarget()
            bookshelf.b_setState('TargetPlayer')

        self.b_setAttackCode(ToontownGlobals.BossCogLargeAttack)
        self.waitForNextAttack(20)
        self._parent.assignedLargeAttack = None
        self._parent.waitForNextLargeAttack(20)

    def b_setBossDamage(self, bossDamage):
        self.d_setBossDamage(bossDamage)
        self.setBossDamage(bossDamage)

    def setBossDamage(self, bossDamage):
        self.bossDamage = bossDamage

    def getBossDamage(self):
        return self.bossDamage

    def d_setBossDamage(self, bossDamage):
        self.sendUpdate('setBossDamage', [bossDamage])

    def b_setIsDizzy(self, isDizzy, bossDamage=5):
        if isDizzy:
            self.d_setIsDizzy(bossDamage)
        self.setIsDizzy(isDizzy, bossDamage)

    def setIsDizzy(self, isDizzy, bossDamage):
        self.isDizzy = isDizzy
        if self.isDizzy:
            if bossDamage <= 50:
                time = 14.5
            else:
                time = 10
            self.waitForNextAttack(time)

    def getIsDizzy(self):
        return self.isDizzy

    def d_setIsDizzy(self, bossDamage):
        self.sendUpdate('setIsDizzy', [bossDamage])

    def hitBoss(self, bossDamage, x, y, z, h, p, r):
        initBossDamage = bossDamage
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self._parent.involvedToons, 'hitBoss from unknown avatar'):
            return
        self.validate(avId, bossDamage <= 300, 'invalid bossDamage %s' % bossDamage)
        if bossDamage < 1:
            return
        currState = self._parent.getCurrentOrNextState()
        if currState != 'BattleTwo':
            return
        bossDamage = min(self.getBossDamage() + bossDamage, self.bossMaxDamage)
        self.b_setBossDamage(bossDamage)
        if self.bossDamage >= self.bossMaxDamage:
            self.deathTime = self.calculateDeathAnimDuration(x, y, z, h, p, r)
            self.b_setIsDead(True)
            return
        self.b_setIsDizzy(True, initBossDamage)
        taskName = self.uniqueName('setIsDizzy')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(9.5, self.b_setIsDizzy, taskName, extraArgs=[False])

    def calculateDeathAnimDuration(self, x, y, z, h, p, r):
        self.setPosHpr(x, y, z, h, p, r)
        node = NodePath('bounceBackNode')
        node.reparentTo(self)
        node.setPos(0.0, 10.0, 0.0)
        node.detachNode()
        returnNode = NodePath('returnNode')
        returnNode.setPos(self.getX(), 0, 0.025)
        time = self.getDistance(returnNode) / 20
        leaveHprTime = 1
        if self.getX() >= 160 or -10 <= self.getY() <= 10:
            centerTrack = Sequence()
            leaveHprTime = None
        else:
            centerTrack = Wait(1 + time)
        leaveSeq = Sequence()
        leaveTrack = Wait(leaveHprTime + 10)
        leaveSeq.append(
            Sequence(
                leaveTrack,
                Wait(2.0),
                Func(node.removeNode),
                Func(returnNode.removeNode)
            )
        )
        ival = Sequence(
            Wait(5.5),
            centerTrack,
            Parallel(
                leaveSeq,
                Wait(2.0)
            )
        )
        return ival.getDuration()

    def __handleDeath(self, task=None):
        self.requestDelete()
        self._parent.cjBoss = None
        if task:
            return task.done


@magicWord(category=CATEGORY_DEBUG)
def toggleBooks():
    """
    Toggle The CJ's large attack. (Bookselves)
    """

    invoker = spellbook.getInvoker()
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedCJBossAI):
            if invoker.doId in do._parent.involvedToons:
                do.dontDoLargeAttack = not do.dontDoLargeAttack
                if do.dontDoLargeAttack:
                    return 'Bookselves disabled for this boss session.'
                else:
                    return 'Bookselves has been re-enabled for this boss session.'
    return 'You are not currently in a four boss battle!'
