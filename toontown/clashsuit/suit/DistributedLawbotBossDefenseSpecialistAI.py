import random

from toontown.suit import BossCogGlobals
from toontown.ai.AIBaseGlobal import *
from toontown.suit import DistributedSuitBaseAI
from toontown.toonbase import ToontownGlobals


class DistributedLawbotBossDefenseSpecialistAI(DistributedSuitBaseAI.DistributedSuitBaseAI):

    def __init__(self, lawbotBoss, air, suitPlanner):
        DistributedSuitBaseAI.DistributedSuitBaseAI.__init__(self, air, suitPlanner)
        self.boss = lawbotBoss
        self.suitDamage = 0
        self.suitMaxDamage = 1
        self.type = BossCogGlobals.LawbotBossSuitDefense

    def delete(self):
        self.ignoreAll()
        self.boss = None
        self.suitDamage = None
        self.suitMaxDamage = None
        taskMgr.remove(self.uniqueName('Remove'))
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
        taskMgr.doMethodLater(delayTime, self.requestDelete, taskName, extraArgs=[])

    def hitSuit(self, taunt=0):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av or avId not in self.boss.involvedToons:
            return
        if not self.getVirtual() and not taunt:
            soundType = av.soundType
            suitDamage = self.boss.getSoundDamage(soundType)
            if suitDamage != self.boss.getSoundDamage(self.boss.soundTypes[avId]):
                self.notify.warning('avId %s tried to damage suit with incorrect damage value (%s)' % (avId, suitDamage))
                return
            suitDamage = min(self.getSuitDamage() + suitDamage, self.suitMaxDamage)
            self.b_setSuitDamage(suitDamage)
            # make sure we're not yet destroyed already, as well.
            if self.suitDamage >= self.suitMaxDamage and self in self.boss.defenseSpecialists:
                self.boss.makeTreasure(self, av)
                self.boss.incrementSuitsDefeated(self, avId, extraMult=1.0)
                # Remove self from the defense specialist list immediately
                if self in self.boss.defenseSpecialists:
                    self.boss.defenseSpecialists.remove(self)
                # Giving time for the client to play the defeated movie before this is deleted.
                self.waitToRemove(3)

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
        self.trapIndex = trapIndex
