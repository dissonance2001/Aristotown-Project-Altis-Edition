from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from otp.ai.AIBase import *


class MotoroomInstanceSessionAI(DirectObject):
    def __init__(self, air):
        DirectObject.__init__(self)
        self.air = air
        self.zoneId = 0
        self.avIds = []
        self.seenAvIds = set()
        self.emptySince = None
        self.createdTime = globalClock.getRealTime()
        self.deleted = False
        self.sakamoreo = None
        self.taskName = 'motoroom-instance-session-%s' % id(self)

    def uniqueName(self, name):
        return '%s-%s' % (name, id(self))

    def generateWithRequired(self, zoneId):
        self.zoneId = zoneId

    def addToon(self, avId):
        if avId and avId not in self.avIds:
            self.avIds.append(avId)

    def b_setState(self, state):
        taskMgr.remove(self.taskName)
        taskMgr.add(self._checkOccupancy, self.taskName)

    def _checkOccupancy(self, task):
        if self.deleted:
            return Task.done

        inside = []
        for avId in self.avIds:
            av = self.air.doId2do.get(avId)
            if av and getattr(av, 'zoneId', None) == self.zoneId:
                inside.append(avId)
                self.seenAvIds.add(avId)

        if inside:
            self.emptySince = None
            return Task.cont

        if not self.seenAvIds:
            if globalClock.getRealTime() - self.createdTime >= 60.0:
                messenger.send(self.uniqueName('BossDone'))
                return Task.done
            return Task.cont

        now = globalClock.getRealTime()
        if self.emptySince is None:
            self.emptySince = now
            return Task.cont

        if now - self.emptySince >= 5.0:
            messenger.send(self.uniqueName('BossDone'))
            return Task.done

        return Task.cont

    def requestDelete(self):
        if self.deleted:
            return
        self.deleted = True
        taskMgr.remove(self.taskName)
        if self.sakamoreo:
            try:
                self.sakamoreo.requestDelete()
            except Exception:
                pass
            self.sakamoreo = None
        self.ignoreAll()
        self.avIds = []
        self.seenAvIds = set()
        self.air = None
