import random

from otp.ai.AIBaseGlobal import *
from toontown.clashsuit.suit.SuitDNA import SuitDNA
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.clashsuit.suit import DistributedSuitBaseAI
from toontown.clashsuit.suit import SuitDialog


@DirectNotifyCategory()
class DistributedFactorySuitAI(DistributedSuitBaseAI.DistributedSuitBaseAI):
    def __init__(self, air, suitPlanner):
        DistributedSuitBaseAI.DistributedSuitBaseAI.__init__(self, air, suitPlanner)
        self.blocker = None
        self.battleCellIndex = None
        self.factoryGone = 0
        self.leader = False

    def factoryIsGoingDown(self):
        self.factoryGone = 1

    def delete(self):
        if not self.factoryGone:
            self.setBattleCellIndex(None)
        del self.blocker
        self.ignoreAll()
        DistributedSuitBaseAI.DistributedSuitBaseAI.delete(self)

    def setLevelDoId(self, levelDoId):
        self.levelDoId = levelDoId

    def getLevelDoId(self):
        return self.levelDoId

    def setCogId(self, cogId):
        self.cogId = cogId

    def getCogId(self):
        return self.cogId

    def setReserve(self, reserve):
        self.reserve = reserve

    def getReserve(self):
        return self.reserve

    def requestBattle(self, x, y, z, h, p, r):
        toonId = self.air.getAvatarIdFromSender()
        if self.notify.getDebug():
            self.notify.debug(str(self.getDoId()) + str(self.zoneId) + ': request battle with toon: %d' % toonId)
        self.confrontPos = Point3(x, y, z)
        self.confrontHpr = Vec3(h, p, r)
        if self.sp.requestBattle(self, toonId):
            if self.notify.getDebug():
                self.notify.debug('Suit %d requesting battle in zone %d with toon %d' % (self.getDoId(), self.zoneId, toonId))
        else:
            if self.notify.getDebug():
                self.notify.debug('requestBattle from suit %d, toon %d- denied by battle manager' % (toonId, self.getDoId()))
            # self.b_setBrushOff(SuitDialog.getBrushOffIndex(self.getStyleName()))
            self.d_denyBattle(toonId)

    def getConfrontPosHpr(self):
        return (self.confrontPos, self.confrontHpr)

    def setBattleCellIndex(self, battleCellIndex):
        self.sp.suitBattleCellChange(self, oldCell=self.battleCellIndex, newCell=battleCellIndex)
        self.battleCellIndex = battleCellIndex
        self.attachBattleBlocker()
        self.accept(self.sp.getBattleBlockerEvent(self.battleCellIndex), self.attachBattleBlocker)

    def getBattleCellIndex(self):
        return self.battleCellIndex

    def attachBattleBlocker(self):
        blocker = self.sp.battleMgr.battleBlockers.get(self.battleCellIndex)
        self.blocker = blocker

    def resume(self):
        self.notify.debug('Suit %s resume' % self.doId)
        if self.hp <= 0:
            messenger.send(self.getDeathEvent())
            self.notify.debug('Suit %s dead after resume' % self.doId)
            self.requestRemoval()
        return None

    def isForeman(self):
        return self.boss or hasattr(self, 'forceForemanFlag')

    def getLeader(self):
        return self.leader
    
    def d_setLeader(self):
        self.sendUpdate("setLeader", [True])

    def b_setDNAString(self, dnaString):
        self.dna = SuitDNA()
        self.dna.makeFromNetString(dnaString)
        self.sendUpdate('setDNAString', [dnaString])
