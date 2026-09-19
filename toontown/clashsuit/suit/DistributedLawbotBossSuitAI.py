import math
import random

from panda3d.core import Vec2, Vec3, Point3

from toontown.suit import BossCogGlobals
from toontown.ai.AIBaseGlobal import *
from toontown.suit import DistributedSuitBaseAI
from toontown.toonbase import ToontownGlobals
from toontown.toon.gui.ToonTipGlobals import TTE


class DistributedLawbotBossSuitAI(DistributedSuitBaseAI.DistributedSuitBaseAI):

    def __init__(self, lawbotBoss, air, suitPlanner, painting):
        DistributedSuitBaseAI.DistributedSuitBaseAI.__init__(self, air, suitPlanner)
        self.boss = lawbotBoss
        self.currState = self.boss.getCurrentOrNextState()
        self.newPosition = None
        self.nearToons = []
        self.suitDamage = 0
        self.suitMaxDamage = 1
        self.isVirtual = 0
        self.isSkelecog = 0
        self.normalZPos = BossCogGlobals.LawbotBossLawyerNormalZPos
        self.virtualZPos = BossCogGlobals.LawbotBossLawyerVirtualZPos
        self.painting = painting
        self.speed = ToontownGlobals.SuitWalkSpeed
        self.spotlight = None
        self.initialMove = True
        self.distance = None
        self.bossStunAllowed = False
        self.targetToon = None
        self.trapIndex = -1
        self.movementQueue = []
        self.cannonBossState = 'BattleTwo'
        self.maxEvidence = BossCogGlobals.LawbotBossSoundEvidenceRequirement['max']
        self.destroyed = False

    def delete(self):
        self.ignoreAll()
        self.boss = None
        self.currState = None
        self.newPosition = None
        self.nearToons = None
        self.suitDamage = None
        self.suitMaxDamage = None
        self.isVirtual = None
        self.isSkelecog = None
        self.normalZPos = None
        self.virtualZPos = None
        self.speed = None
        self.painting = None
        self.initialMove = None
        self.distance = None
        self.bossStunAllowed = None
        self.targetToon = None
        self.trapIndex = None
        self.movementQueue = None
        taskMgr.remove(self.uniqueName('NextAttack'))
        taskMgr.remove(self.uniqueName('Remove'))
        taskMgr.remove(self.uniqueName('Return'))
        taskMgr.remove(self.uniqueName('TrapBreak'))
        DistributedSuitBaseAI.DistributedSuitBaseAI.delete(self)

    def getPos(self):
        return (self.getX(), self.getY(), self.getZ())

    def getPosHpr(self):
        return (
            self.getX(),
            self.getY(),
            self.getZ(),
            self.getH(),
            self.getP(),
            self.getR()
        )

    def waitToRemove(self, delayTime):
        taskName = self.uniqueName('Remove')
        taskMgr.remove(taskName)

        if self.currState == "BattleFour":
            taskMgr.doMethodLater(delayTime, self.boss.removeLawyer, taskName, extraArgs=[self, self.painting])
        else:
            taskMgr.doMethodLater(delayTime, self.removeLawyer, taskName, extraArgs=[])

    def waitForNextMove(self, delayTime):
        taskName = self.uniqueName('NextAttack')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.doNextMove, taskName)

    def doNextMove(self, taskName):
        if self.currState == 'BattleFour':
            lowEnd = 0.08 + (len(self.boss.involvedToons) * 0.01)
            highEnd = 0.21 + (len(self.boss.involvedToons) * 0.02)
            if self.getElite() and not self.isVirtual and random.random() <= self.boss.progressValue(lowEnd, highEnd) and not self.initialMove:
                if self.boss.traps is None:
                    return
                trapDict = {}
                # Create a dictionary containing each trap index and how far from the boss it is.
                for trap in self.boss.traps:
                    trapDict[self.boss.traps.index(trap)] = Vec3(self.boss.getPos() - trap.getPos()).length()
                # Sort it in ascending order.
                sortedTraps = sorted(trapDict.items(), key=lambda x: x[1], reverse=False)
                trapIndex = None
                # Run through the sorted traps, and continually attempt to find the closest one.
                for trapPair in sortedTraps:
                    tIndex = trapPair[0]
                    trap = self.boss.traps[tIndex]
                    if trap.getStatus() != 1 or trap.getSuitId() or trap.getDuringActivation():
                        continue
                    trapIndex = tIndex
                    break
                if not trapIndex:
                    self.doFlying()
                    return
                trap = self.boss.traps[trapIndex]
                self.b_setTrapIndex(trapIndex)
                trap.setSuitId(self.doId)
                trapPos = trap.getPos()
                self.doSwoop(trapPos[0], trapPos[1], trapPos[2])
                # Skelecog Tip
                for avId in self.boss.involvedToons:
                    toon = self.air.doId2do.get(avId)
                    if toon:
                        toon.showToonTip(TTE.TIP_CLO_EXE_DISABLING_TRAP)
            elif self.nearToons or self.targetToon:
                if self.targetToon:
                    toonId = self.targetToon
                    self.targetToon = None
                elif self.nearToons:
                    toonId = random.choice(self.nearToons)
                toon = self.air.doId2do.get(toonId)
                if not toon:
                    self.doFlying()
                    return
                toonPos = toon.getPos()
                toonPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ())
                self.doSwoop(toonPos[0], toonPos[1], toonPos[2])
            else:
                self.doFlying()
        else:
            self.doFlying()

        if self.initialMove:
            self.initialMove = False

    def doSwoop(self, x, y, z):
        # Distance to destination
        distance = Vec3(Point3(x, y, z) - self.getPos()).length()
        self.setPos(Point3(x, y, z))
        if self.getVirtual():
            time = min(4, max(2, distance / (self.speed * self.boss.progressValue(4.5, 6))))
        elif self.trapIndex != -1:
            time = 3
        else:
            time = min(4, max(2, distance / (self.speed * self.boss.progressValue(4.5, 6))))
        self.d_doTravel(time, x, y, z)
        if self.trapIndex != -1:
            self.waitForTrapBreak(time)
        else:
            self.waitToReturn(time + self.boss.progressValue(1.75, 1.5))

    def doManeuver(self, startPos, endPos):
        # Decide whether or not the Lawyer does a special maneuver
        if random.random() < (0.3 + 0.05 * self.getActualLevel()):
            maneuverToDo = random.choice([self.doZigZagVertical, self.doZigZagHorizontal, self.doLoop])
            maneuverToDo(startPos, endPos)
        else:
            self.__addSlowdownMovements(startPos, endPos)

    def doZigZagVertical(self, startPos, endPos):
        waypointOne = self.__lerpPoint3(startPos, endPos, 0.25)
        waypointOne.setZ(waypointOne.getZ() + 20)

        self.__addSlowdownMovements(startPos, waypointOne)

        waypointTwo = self.__lerpPoint3(startPos, endPos, 0.75)
        waypointTwo.setZ(waypointTwo.getZ() - 20)

        self.__addSlowdownMovements(waypointOne, waypointTwo)
        self.__addSlowdownMovements(waypointTwo, endPos)

    def doZigZagHorizontal(self, startPos, endPos):
        midpoint = self.__lerpPoint3(startPos, endPos, 0.5)
        distance = Vec2(midpoint.getXy() - startPos.getXy()).length()
        deltaX = midpoint.getX() - startPos.getX()
        deltaY = midpoint.getY() - startPos.getY()
        angle = math.atan2(deltaY, deltaX) + math.pi / 4
        newDeltaX = distance * math.cos(angle)
        newDeltaY = distance * math.sin(angle)
        waypointOne = Point3(startPos)

        newX = waypointOne.getX() + newDeltaX
        if newX < -100:
            newX = -100
        elif newX > 100:
            newX = 100

        newY = waypointOne.getY() + newDeltaY
        if newY < 120:
            newY = 120
        elif newY > 340:
            newY = 340

        waypointOne.setX(newX)
        waypointOne.setY(newY)
        self.__addSlowdownMovements(startPos, waypointOne)

        distance = Vec2(endPos.getXy() - midpoint.getXy()).length()
        deltaX = endPos.getX() - midpoint.getX()
        deltaY = endPos.getY() - midpoint.getY()
        angle = math.atan2(deltaY, deltaX) - math.pi / 4
        newDeltaX = distance * math.cos(angle)
        newDeltaY = distance * math.sin(angle)
        waypointTwo = Point3(midpoint)

        newXTwo = waypointTwo.getX() + newDeltaX
        if newXTwo < -100:
            newXTwo = -100
        elif newXTwo > 100:
            newXTwo = 100

        newYTwo = waypointTwo.getY() + newDeltaY
        if newYTwo < 120:
            newYTwo = 120
        elif newYTwo > 340:
            newYTwo = 340

        waypointTwo.setX(newXTwo)
        waypointTwo.setY(newYTwo)
        self.__addSlowdownMovements(waypointOne, waypointTwo)

        self.__addSlowdownMovements(waypointTwo, endPos)

    def doLoop(self, startPos, endPos):
        midpoint = self.__lerpPoint3(startPos, endPos, 0.5)
        self.__addSlowdownMovements(startPos, midpoint)

        waypointOne = self.__lerpPoint3(startPos, endPos, 0.75)
        waypointOne.setZ(waypointOne.getZ() + 10)
        self.__addSlowdownMovements(midpoint, waypointOne)

        # Top of Loop
        waypointTwo = Point3(midpoint)
        waypointTwo.setZ(waypointTwo.getZ() + 20)
        self.__addSlowdownMovements(waypointOne, waypointTwo)

        waypointThree = self.__lerpPoint3(startPos, endPos, 0.25)
        waypointThree.setZ(waypointThree.getZ() + 10)
        self.__addSlowdownMovements(waypointTwo, waypointThree)
        self.__addSlowdownMovements(waypointThree, midpoint)
        self.__addSlowdownMovements(midpoint, endPos)

    def __lerpPoint3(self, startPos, endPos, lerpAmount):
        '''
        Returns a Point3 linearly interpolated from 0 to 1
        For lerpAmount, 0 = startPos and 1 = endPos. 0.5 would be the midpoint.
        '''
        lerpedX = startPos.getX() - lerpAmount * (startPos.getX() - endPos.getX())
        lerpedY = startPos.getY() - lerpAmount * (startPos.getY() - endPos.getY())
        lerpedZ = startPos.getZ() - lerpAmount * (startPos.getZ() - endPos.getZ())
        return Point3(lerpedX, lerpedY, lerpedZ)

    def __addSlowdownMovements(self, startPos, endPos):
        distanceToSlowDownFor = 2.5
        distance = Vec3(endPos - startPos).length()
        if distance > 2 * distanceToSlowDownFor:
            # Add slowdown to start of movement
            self.movementQueue.append([self.__lerpPoint3(startPos, endPos, distanceToSlowDownFor/distance), True])
            # Add slowdown to end of movement
            self.movementQueue.append([self.__lerpPoint3(startPos, endPos, 1 - distanceToSlowDownFor/distance), False])
        self.movementQueue.append([endPos, True])

    def waitForTrapBreak(self, delayTime):
        taskName = self.uniqueName('TrapBreak')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.doTrapBreak, taskName)

    def doTrapBreak(self, taskName):
        if self.trapIndex != -1:
            if self.boss.traps is None:
                return
            trap = self.boss.traps[self.trapIndex]
            if trap.getStatus() == 1:
                trap.startBreak()
                delayTime = BossCogGlobals.LawbotBossTrapBreakT
            else:
                delayTime = 0
        else:
            delayTime = 0

        self.waitToReturn(delayTime)

    def waitToReturn(self, delayTime):
        taskName = self.uniqueName('Return')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.doFlying, taskName)

    def doFlying(self, taskName=None):
        if not hasattr(self.boss, 'lawyerPositions'):
            return

        self.b_setTrapIndex(-1)
        oldPosition = self.newPosition
        slowdownMovement = False
        if self.initialMove:
            x, y, z = BossCogGlobals.LawbotBossLawyerFirstPos[self.painting]
            if self.currState == self.cannonBossState:
                z = -20
            self.newPosition = Point3(x, y, z)
            self.boss.lawyerPositions[self] = self.newPosition
            self.distance = Vec3(self.newPosition - self.getPos()).length()
        else:
            while True:
                if self.currState == "BattleFour":
                    if self.getVirtual():
                        x = random.randint(-10, 10)
                        y = random.randint(105, 125)
                        z = self.virtualZPos
                    else:
                        x = random.choice([random.randint(-100, -10), random.randint(10, 100)])
                        y = random.choice([random.randint(105, 120), random.randint(125, 340)])
                        z = self.normalZPos
                    self.newPosition = Point3(x, y, z)
                else:
                    # Get new position to go to if no movements queued.
                    if len(self.movementQueue) == 0:
                        x = random.randint(-100, 100)
                        y = random.randint(120, 340)
                        z = random.randint(-45, 0)
                        self.doManeuver(oldPosition, Point3(x, y, z))
                    # Check for existing movement queue or for new one from doManeuver.
                    if len(self.movementQueue) > 0:
                        nextMovement = self.movementQueue.pop(0)
                        self.newPosition = nextMovement[0]
                        slowdownMovement = nextMovement[1]
                        x = self.newPosition.getX()
                        y = self.newPosition.getY()
                        z = self.newPosition.getZ()
                self.distance = Vec3(self.newPosition - self.getPos()).length()
                if self.newPosition not in list(self.boss.lawyerPositions.values()):
                    self.boss.lawyerPositions[self] = self.newPosition
                    break
        self.setPos(self.newPosition)
        if self.currState == "BattleFour":
            time = self.distance / (self.speed * self.boss.progressValue(1.5, 2.75))
        else:
            time = self.distance / (self.speed * (2 + 0.12 * self.getActualLevel()))
            if slowdownMovement:
                time *= 2.5
            if self.isElite:
                time *= 0.75
        self.d_doTravel(time, x, y, z)
        self.waitForNextMove(time)

    def d_doTravel(self, time, x, y, z):
        self.sendUpdate('doTravel', [str(time), x, y, z])

    def bossNear(self, trapIndex):
        if self.trapIndex == trapIndex:
            if self.boss.traps is None:
                return
            trap = self.boss.traps[self.trapIndex]
            trap.startInterruptBreak()
            self.b_setTrapIndex(-1)
            self.doFlying()

    def avatarNearEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.nearToons:
            self.nearToons.append(avId)

    def avatarNearExit(self):
        try:
            avId = self.air.getAvatarIdFromSender()
            self.nearToons.remove(avId)
        except:
            pass

    def hitSuit(self, taunt=0):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av or avId not in self.boss.involvedToons:
            return
        if self.currState == self.cannonBossState:
            self.b_setSuitDamage(self.suitMaxDamage)
            self.waitToRemove(6)
            taskMgr.remove(self.uniqueName('NextAttack'))
            if self.getActualLevel() > 10:
                evidenceAmt = 6
            elif self.getActualLevel() > 5:
                evidenceAmt = 4
            else:
                evidenceAmt = 3
            # Give extra evidence to all players if we're executive or they have max evidence.
            if (
                self.isElite
                or self.boss.evidence.get(avId, 0) >= self.maxEvidence
            ):
                for toonID in self.boss.involvedToons:
                    evidenceMult = 1.2 if avId == toonID else 0.2
                    evidence = math.ceil(evidenceAmt * evidenceMult)
                    extraMult = 5.0 if avId == toonID else 1.0
                    self.boss.giveEvidence(toonID, evidence, extraMult=extraMult)
                return
            self.boss.giveEvidence(avId, evidenceAmt)
            messenger.send(self.boss.taskName("cannon_destroyedSuit"), sentArgs=[self, avId])
            return
        if not self.getVirtual() and not taunt:
            soundType = av.soundType
            suitDamage = self.boss.getSoundDamage(soundType)
            if suitDamage != self.boss.getSoundDamage(self.boss.soundTypes[avId]):
                self.notify.warning('avId %s tried to damage suit with incorrect damage value (%s)' % (avId, suitDamage))
                return
            suitDamage = min(self.getSuitDamage() + suitDamage, self.suitMaxDamage)
            self.b_setSuitDamage(suitDamage)
            if self.suitDamage >= self.suitMaxDamage and not self.destroyed:
                self.destroyed = True
                taskMgr.remove(self.uniqueName('NextAttack'))
                taskMgr.remove(self.uniqueName('TrapBreak'))
                self.waitToRemove(self.boss.progressValue(8, 4))
                self.boss.suitHitBoss(self.getDoId())
                mult = 1.0
                if self.trapIndex != -1:
                    if self.boss.traps is not None:
                        trap = self.boss.traps[self.trapIndex]
                        trap.startInterruptBreak()
                        # Give players an extra bonus for destroying skelecogs breaking traps.
                        mult = 5.0
                self.boss.makeTreasure(self, av)
                self.boss.incrementSuitsDefeated(self, avId, extraMult=mult)

        elif taunt and self.trapIndex == -1 and not self.getVirtual():
            self.targetToon = avId
            self.waitForNextMove(0)

    def b_setSuitDamage(self, suitDamage):
        self.d_setSuitDamage(suitDamage)
        self.setSuitDamage(suitDamage)

    def d_setSuitDamage(self, suitDamage):
        self.sendUpdate('setSuitDamage', [suitDamage])

    def setSuitDamage(self, suitDamage):
        self.suitDamage = suitDamage

    def b_setSuitMaxDamage(self, suitMaxDamage):
        self.d_setSuitMaxDamage(suitMaxDamage)
        self.setSuitMaxDamage(suitMaxDamage)

    def d_setSuitMaxDamage(self, suitMaxDamage):
        self.sendUpdate('setSuitMaxDamage', [suitMaxDamage])

    def setSuitMaxDamage(self, suitMaxDamage):
        self.suitMaxDamage = suitMaxDamage

    def getSuitDamage(self):
        return self.suitDamage

    def getSuitMaxDamage(self):
        return self.suitMaxDamage

    def setVirtual(self, virtual):
        self.isVirtual = virtual

    def getVirtual(self):
        return self.isVirtual

    def setSkelecog(self, skelecog):
        self.isSkelecog = skelecog

    def getSkelecog(self):
        return self.isSkelecog

    def b_setTrapIndex(self, trapIndex=-1):
        self.d_setTrapIndex(trapIndex)
        self.setTrapIndex(trapIndex)

    def d_setTrapIndex(self, trapIndex=-1):
        self.sendUpdate("setTrapIndex", [trapIndex])

    def setTrapIndex(self, trapIndex=-1):
        self.trapIndex = trapIndex

    def removeLawyer(self):
        if self in self.boss.lawyers:
            self.boss.lawyers.remove(self)

        if self in self.boss.lawyerPositions:
            del self.boss.lawyerPositions[self]

        self.requestDelete()
