from direct.directnotify import DirectNotifyGlobal
from direct.task.TaskManagerGlobal import taskMgr

from toontown.suit import SuitTimings
from toontown.suit.DistributedSuitBaseAI import DistributedSuitBaseAI


class DistributedWinterMinigameSuitAI(DistributedSuitBaseAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedWinterMinigameSuitAI')

    def __init__(self, air, suitPlanner):
        DistributedSuitBaseAI.__init__(self, air, suitPlanner)
        self.hit = False
        self.canGrab = False
        self.posHpr = (0, 0, 0, 0, 0, 0)

    def setPosHpr(self, x, y, z, h, p, r):
        self.posHpr = (x, y, z, h, p, r)

    def getPosHpr(self):
        return self.posHpr

    def flyIn(self, x, y, z):
        self.sendUpdate('flyIn', [x, y, z])
        taskMgr.doMethodLater(SuitTimings.fromSky, self.flyInStop, 'ts-stop-flyin-cog-%s' % self.doId)

    def flyInStop(self, task=None):
        self.canGrab = True

    def hitByToon(self):
        if self.hit:
            return
        self.sendUpdate('explode', [])
        self.hit = True
        self.canGrab = False
        taskMgr.remove('ts-stop-flyin-cog-%s' % self.doId)
        taskMgr.doMethodLater(SuitTimings.suitDeath, self.requestDelete, 'ts-del-cog-%s' % self.doId, extraArgs=[])
