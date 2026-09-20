import random

from panda3d.core import Point3, Vec3

from toontown.clashsuit.suit import BossCogGlobals
from toontown.clashsuit.suit.DistributedHardmodeLawbotBossSuitAI import DistributedHardmodeLawbotBossSuitAI
from toontown.toonbase import ToontownGlobals


class DistributedHardmodeLawbotBossSuitAttackAI(DistributedHardmodeLawbotBossSuitAI):
    def __init__(self, lawbotBoss, air, suitPlanner, painting):
        super().__init__(lawbotBoss, air, suitPlanner, painting)
        self.type = BossCogGlobals.LawbotBossSuitAttack
        self.speed = BossCogGlobals.HardmodeLawbotBossAttackCogSpeed
        self.chaseToon = None
        self.docketTargetPos = None
        self.performingDocket = False
        self.performedDocket = False

    def delete(self):
        self.chaseToon = None
        self.docketTargetPos = None
        self.performingDocket = None
        del self.chaseToon
        del self.docketTargetPos
        del self.performingDocket
        del self.performedDocket
        taskMgr.removeTasksMatching(self.uniqueName('docket-task'))
        taskMgr.removeTasksMatching(self.uniqueName('end-docket'))
        super().delete()

    def doNextMove(self, taskName):
        if self.performingDocket:
            # No need to try and move if we're using our Docket attack, since we're standing still anyway.
            return

        # We attack with a pattern of Docket -> move -> repeat
        self.performedDocket = not self.performedDocket

        if not self.performedDocket:
            if not self.chaseToon and self.boss.involvedToons:
                toonId = random.choice(self.boss.involvedToons)
                toon = self.air.doId2do.get(toonId)
                if toon:
                    self.chaseToon = toon
        else:
            # This will force them to randomly walk around.
            self.chaseToon = None

        self.doFlying()

        if self.initialMove:
            self.initialMove = False

    def doFlying(self, taskName=None):
        if self.chaseToon:
            # We're preparing to use our docket attack, so let's start chasing the toon.
            toonPos = self.chaseToon.getPos()
            self.docketTargetPos = Point3(toonPos.getX(), toonPos.getY(), self.normalZPos)
            doDocket = True
        else:
            self.chaseToon = None
            self.docketTargetPos = None
            doDocket = False

        if self.initialMove:
            # We've just come out of the portrait. Fly forward a bit to prevent clipping through the wall.
            x, y, z = BossCogGlobals.LawbotBossLawyerFirstPos[self.painting]
            if self.currState == self.cannonBossState:
                z = -20
            self.newPosition = Point3(x, y, z)
            self.boss.lawyerPositions[self] = self.newPosition
            self.distance = Vec3(self.newPosition - self.getPos()).length()
        else:
            while True:
                if not self.chaseToon:
                    # We don't have a target to chase, so just default to a random pos and wander about.
                    x = random.choice([random.randint(-100, -10), random.randint(10, 100)])
                    y = random.choice([random.randint(105, 120), random.randint(125, 340)])
                    z = self.normalZPos
                    self.newPosition = Point3(x, y, z)
                else:
                    break

                self.distance = Vec3(self.newPosition - self.getPos()).length()
                if self.newPosition not in list(self.boss.lawyerPositions.values()):
                    self.boss.lawyerPositions[self] = self.newPosition
                    break

            if self.docketTargetPos:
                # We've got our targets position, let's start flying towards it.
                self.newPosition = self.docketTargetPos
                x, y, z = self.newPosition
                self.distance = Vec3(self.newPosition - self.getPos()).length()
                self.boss.lawyerPositions[self] = self.newPosition
                self.docketTargetPos = None

        self.setPos(self.newPosition)
        speed = self.speed if not self.chaseToon else self.speed * 6
        time = self.distance / (speed * self.boss.progressValue(1.5, 2.75))

        if not self.initialMove and doDocket:
            taskMgr.removeTasksMatching(self.uniqueName('docket-task'))
            taskMgr.doMethodLater(time, self.beginDocket, self.uniqueName('docket-task'))

        self.d_doTravel(time, x, y, z)
        self.waitForNextMove(time)

    def beginDocket(self, _=None):
        # We've reached our target's position. Time to begin the docket after a small delay.
        self.sendUpdate('beginDocket')
        self.performingDocket = True
        taskMgr.doMethodLater(BossCogGlobals.HardmodeLawbotBossDocketDelay * 2, self.endDocket,
                              self.uniqueName('end-docket'))

    def endDocket(self, _=None):
        self.performingDocket = False
        self.chaseToon = None
        self.docketTargetPos = None
        self.waitForNextMove(0)

    def removeLawyer(self):
        self.boss.attackCogsSpawned -= 1
        super().removeLawyer()

    def hitSuit(self, taunt=0):
        # Attack suits are immortal, and can't be taunted or hit.
        return
