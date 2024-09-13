from toontown.suit import SuitDNA
from toontown.suit.SuitLegList import *
from toontown.suit import SuitTimings
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import *
from pandac.PandaModules import *
from pandac.PandaModules import Point3
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import TTLocalizer


TIME_BUFFER_PER_WPT = 0.25
TIME_DIVISOR = 100
DISTRIBUTE_TASK_CREATION = 0

class SuitBase:
    notify = DirectNotifyGlobal.directNotify.newCategory('SuitBase')

    def __init__(self):
        self.dna = None
        self.level = 0
        self.maxHP = 10
        self.currHP = 10
        self.isSkelecog = 0
        self.isElite = 0
        self.isWaiter = 0
        self.isImmune = 0
        self.isSoaked = 0
        self.isEnraged = 0
        self.isAbsorbing = 0

    def delete(self):
        if hasattr(self, 'legList'):
            del self.legList

    def getStyleName(self):
        if hasattr(self, 'dna') and self.dna:
            return self.dna.name
        else:
            return 'unknown'

    def getStyleDept(self):
        if hasattr(self, 'dna') and self.dna:
            return SuitDNA.getDeptFullname(self.dna.dept)
        else:
            return 'unknown'

    def getCurrentHealth(self):
        return self.currHP

    def getMaxHealth(self):
        return self.maxHP

    def getLevel(self):
        return self.level

    def setLevel(self, level):
        self.level = level
        nameWLevel = TTLocalizer.SuitBaseNameWithLevel % {'name': self.name,
         'dept': self.getStyleDept(),
         'level': self.getActualLevel()}
        self.setDisplayName(nameWLevel)
        attributes = SuitBattleGlobals.SuitAttributes[self.dna.name]
        self.maxHP = attributes['hp'][self.level]
        self.currHP = self.maxHP

    def getSkelecog(self):
        return self.isSkelecog

    def setSkelecog(self, flag):
        self.isSkelecog = flag

    def setVirtual(self, flag):
        self.isVirtual = flag

    def setWaiter(self, flag):
        self.isWaiter = flag
		
    def getElite(self):
        return self.isElite

    def setElite(self, flag):
        self.isElite = flag

    def setImmuneStatus(self, num):
        if num == None:
            num = 0
        else:
            self.isImmune = num

    def getImmuneStatus(self):
        return self.isImmune

    def setEnragedStatus(self, num):
        if num == None:
            num = 0
        else:
            self.isEnraged = num

    def getEnragedStatus(self):
        return self.isEnraged

    def setAbsorbingStatus(self, num):
        if num == None:
            num = 0
        else:
            self.isAbsorbing = num

    def getAbsorbingStatus(self):
        return self.isAbsorbing

    def setSoakedStatus(self, num):
        if num == None:
            num = 0
        else:
            self.isSoaked = num

    def getSoakedStatus(self):
        return self.isSoaked

    def getActualLevel(self):
        if hasattr(self, 'dna'):
            return SuitBattleGlobals.getActualFromRelativeLevel(self.getStyleName(), self.level) + 1
        else:
            return 1

    def setPath(self, path):
        self.path = path
        self.pathLength = self.path.getNumPoints()

    def getPath(self):
        return self.path

    def printPath(self):
        print '%d points in path' % self.pathLength
        for currPathPt in xrange(self.pathLength):
            indexVal = self.path.getPointIndex(currPathPt)
            print '\t', self.sp.dnaStore.getSuitPointWithIndex(indexVal)

    def makeLegList(self):
        self.legList = SuitLegList(self.path, self.sp.dnaStore)