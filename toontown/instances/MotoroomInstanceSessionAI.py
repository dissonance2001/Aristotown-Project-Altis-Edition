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
        self._createSakamoreo()

    def _createSakamoreo(self):
        if self.sakamoreo or not self.air or not self.zoneId:
            return

        from toontown.toon import NPCToons

        bodyColor = (0.298039, 0.298039, 0.349020, 1.0)
        white = (1.0, 1.0, 1.0, 1.0)
        dna = (
            'css',
            'md',
            'm',
            'f',
            bodyColor,
            white,
            white,
            bodyColor,
            0,
            0,
            0,
            0,
            72,
            0
        )
        desc = (
            -1,
            'Sakamoreo',
            dna,
            'f',
            0,
            NPCToons.NPC_REGULAR
        )

        self.sakamoreo = NPCToons.createNPC(
            self.air,
            93901,
            desc,
            self.zoneId
        )
        self.sakamoreo.b_setBackpack(111, 0, 0)
        self.sakamoreo.b_setHat(136, 0, 0)
        self.sakamoreo.b_setGlasses(50, 0, 0)
        self.sakamoreo.setPosHpr(
                -16.120, 34.579, -4.02,
                78.787, 0.0, 0.0
            )
        if hasattr(self.sakamoreo, 'd_setPosHpr'):
            self.sakamoreo.d_setPosHpr(
                -16.120, 34.579, -4.02,
                78.787, 0.0, 0.0
            )

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
