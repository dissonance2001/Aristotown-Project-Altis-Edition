from otp.ai.AIBaseGlobal import *
import random
from otp.avatar import DistributedAvatarAI
from toontown.suit import SuitPlannerBase
from toontown.suit import SuitBase
from toontown.suit import SuitDNA
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import SuitBattleGlobals
from toontown.toonbase import ToontownBattleGlobals

class DistributedSuitBaseAI(DistributedAvatarAI.DistributedAvatarAI, SuitBase.SuitBase):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedSuitBaseAI')

    def __init__(self, air, suitPlanner):
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        SuitBase.SuitBase.__init__(self)
        self.sp = suitPlanner
        self.maxHP = 10
        self.currHP = 10
        self.immune = 0
        self.enraged = 0
        self.absorbing = 0
        self.soaked = 0
        self.zoneId = 0
        self.dna = SuitDNA.SuitDNA()
        self.virtual = 0
        self.waiter = 0
        self.isElite = 0
        self.executive = 0
        self.cog = 0
        self.isSkeleton = 0
        self.manager = 0
        self.isVirtual = 0
        self.governaught = 0
        self.dmgMult = 1.0
        self.vulnerabilityMult = 1.0
        self.skeleRevives = 0
        self.maxSkeleRevives = 0
        self.reviveFlag = 0
        self.buildingHeight = None

    def generate(self):
        DistributedAvatarAI.DistributedAvatarAI.generate(self)

    def delete(self):
        self.sp = None
        del self.dna

        DistributedAvatarAI.DistributedAvatarAI.delete(self)
        SuitBase.SuitBase.delete(self)

    def requestRemoval(self):
        if self.sp != None:
            self.sp.removeSuit(self)
        else:
            self.requestDelete()
        return

    def setLevel(self, lvl = None):
        attributes = SuitBattleGlobals.SuitAttributes[self.dna.name]
        if attributes['level'] < 100:  # IF NORMAL COG
            if lvl:
                self.level = lvl - attributes['level'] - 1
            else:
                self.level = SuitBattleGlobals.pickFromFreqList(attributes['freq'])
            if lvl > attributes['level'] + len(attributes['hp']):
                self.level = len(attributes['hp']) - 1
            self.notify.debug('Assigning level ' + str(lvl))
            if hasattr(self, 'doId'):
                self.d_setLevelDist(self.level)
            hp = attributes['hp'][self.level]
            self.maxHP = hp
            self.currHP = hp
        else:
            if self.dna.name == 'mes' or 'mad':
                self.level = lvl
            else:
                self.level = attributes['level']  # don't subtract 1, assume the level is as-is from battleglobals
            self.notify.debug('Assigning level to non-normal cog ' + str(self.level))
            if hasattr(self, 'doId'):
                self.d_setLevelDist(self.level)
            if self.dna.name == 'mes' or 'mad':
                if self.level > 99:
                    hp = hp = attributes['hp'][49]
                else:
                    hp = attributes['hp'][self.level]
            else:
                hp = attributes['hp'][0]
            self.maxHP = hp
            self.currHP = hp

    def getLevelDist(self):
        return self.getLevel()

    def d_setLevelDist(self, level):
        self.sendUpdate('setLevelDist', [level])
		
    def b_setElite(self, flag):
        self.setElite(flag)
        self.d_setElite(flag)

    def d_setElite(self, flag):
        self.sendUpdate('setElite', [flag])

    def setElite(self, flag):
        self.isElite = flag
        if flag:
            self.maxHP = int(self.maxHP * 1.0)
            self.currHP = int(self.currHP * 1.0)

    def getElite(self):
        return self.isElite

    def setupSuitDNA(self, level, type, track):
        dna = SuitDNA.SuitDNA()
        dna.newSuitRandom(type, track)
        self.dna = dna
        self.track = track
        self.setLevel(level)

    def getDNAString(self):
        if self.dna:
            return self.dna.makeNetString()
        else:
            self.notify.debug('No dna has been created for suit %d!' % self.getDoId())
            return ''

    def b_setImmuneStatus(self, num):
        if num == None:
            num = 0
        self.setImmuneStatus(num)
        self.d_setImmuneStatus(self.getImmuneStatus())
        return

    def d_setImmuneStatus(self, num):
        self.sendUpdate('setImmuneStatus', [num])

    def getImmuneStatus(self):
        return self.immune

    def setImmuneStatus(self, num):
        if num == None:
            num = 0
        self.immune = num
        return

    def b_setEnragedStatus(self, num):
        if num == None:
            num = 0
        self.setEnragedStatus(num)
        self.d_setEnragedStatus(self.getEnragedStatus())
        return

    def d_setEnragedStatus(self, num):
        self.sendUpdate('setEnragedStatus', [num])

    def getEnragedStatus(self):
        return self.enraged

    def setEnragedStatus(self, num):
        if num == None:
            num = 0
        self.enraged = num
        return

    def b_setAbsorbingStatus(self, num):
        if num == None:
            num = 0
        self.setAbsorbingStatus(num)
        self.d_setAbsorbingStatus(self.getAbsorbingStatus())
        return

    def d_setAbsorbingStatus(self, num):
        self.sendUpdate('setAbsorbingStatus', [num])

    def getAbsorbinigStatus(self):
        return self.absorbing

    def setAbsorbingStatus(self, num):
        if num == None:
            num = 0
        self.absorbing = num
        return

    def b_setSoakedStatus(self, num):
        if num == None:
            num = 0
        self.setSoakedStatus(num)
        self.d_setSoakedStatus(self.getSoakedStatus())
        return

    def d_setSoakedStatus(self, num):
        self.sendUpdate('setSoakedStatus', [num])

    def getSoakedStatus(self):
        return self.soaked

    def setSoakedStatus(self, num):
        if num == None:
            num = 0
        self.soaked = num
        return

    def b_setBrushOff(self, index):
        self.setBrushOff(index)
        self.d_setBrushOff(index)

    def d_setBrushOff(self, index):
        self.sendUpdate('setBrushOff', [index])

    def setBrushOff(self, index):
        pass

    def d_denyBattle(self, toonId):
        self.sendUpdateToAvatarId(toonId, 'denyBattle', [])

    def b_setExecutive(self, executive):
        if executive == None:
            executive = 0
        self.setExecutive(executive)
        self.d_setExecutive(self.getExecutive())

    def d_setExecutive(self, executive):
        self.sendUpdate('setExecutive', [executive])

    def getExecutive(self):
        return self.executive

    def setExecutive(self, executive):
        if executive == None:
            executive = 0
        self.executive = executive
        if self.dna.name == 'mh2':
            self.maxHP = random.randint(200, 900)
            self.currHP = self.maxHP
        if self.dna.name == 'std2':
            self.maxHP = random.randint(100, 700)
            self.currHP = self.maxHP
        if self.dna.name == 'autocad' or self.dna.name == 'watchm' \
                or self.dna.name == 'ant':
            self.maxHP = int((self.maxHP * random.uniform(.75, 1.25)) * ToontownBattleGlobals.EXECUTIVE_HP_MULT)
            self.currHP = self.maxHP
        if self.executive and not self.dna.name == 'mh2' and not self.dna.name == 'std2' and not self.dna.name == 'autocad' and not self.dna.name == 'watchm'  \
                and not self.dna.name == 'ant':
            self.maxHP = int(self.maxHP * ToontownBattleGlobals.EXECUTIVE_HP_MULT)
            self.currHP = self.maxHP

    def b_setCog(self, cog):
        if cog == None:
            cog = 0
        self.setCog(cog)
        self.d_setCog(self.getCog())

    def d_setCog(self, cog):
        self.sendUpdate('setExecutive', [cog])

    def getCog(self):
        return self.cog

    def setCog(self, cog):
        if cog == None:
            cog = 0
        self.cog = cog
        if self.cog:
            self.maxHP = self.maxHP
            self.currHP = self.maxHP

    def b_setGovernaught(self, governaught):
        if governaught == None:
            governaught = 0
        self.setGovernaught(governaught)
        self.d_setGovernaught(self.getGovernaught())

    def d_setGovernaught(self, governaught):
        self.sendUpdate('setGovernaught', [governaught])

    def getGovernaught(self):
        return self.governaught

    def setGovernaught(self, governaught):
        if governaught == None:
            governaught = 0
        self.governaught = governaught
        if self.governaught:
            self.maxHP = int(self.maxHP * ToontownBattleGlobals.GOVERNAUGHT_HP_MULT)
            self.currHP = self.maxHP

    def b_setManager(self, manager):
        if manager == None:
            manager = 0
        self.setManager(manager)
        self.d_setManager(self.getManager())

    def d_setManager(self, manager):
        self.sendUpdate('setManager', [manager])

    def getManager(self):
        return self.manager

    def setManager(self, manager):
        if manager == None:
            manager = 0
        self.manager = manager

    def b_setSkeleRevives(self, num):
        if num == None:
            num = 0
        self.setSkeleRevives(num)
        self.d_setSkeleRevives(self.getSkeleRevives())

    def d_setSkeleRevives(self, num):
        self.sendUpdate('setSkeleRevives', [num])

    def getSkeleRevives(self):
        return self.skeleRevives

    def setSkeleRevives(self, num):
        if num == None:
            num = 0
        self.skeleRevives = num
        if num > self.maxSkeleRevives:
            self.maxSkeleRevives = num

    def getMaxSkeleRevives(self):
        return self.maxSkeleRevives

    def useSkeleRevive(self):
        self.skeleRevives -= 1
        if self.getSkeleton() > 0:
            self.setVirtual(1)
        else:
            self.setSkeleton(1)
        self.currHP = self.maxHP
        self.reviveFlag = 1
        self.setDamageMultiplier(self.getDamageMultiplier() * 1.5)
        self.setMaxHP(int(self.maxHP * .5))

    def reviveCheckAndClear(self):
        returnValue = 0
        if self.reviveFlag == 1:
            returnValue = 1
            self.reviveFlag = 0
        return returnValue

    def getHP(self):
        return self.currHP

    def setHP(self, hp):
        if hp > self.maxHP * self.hardMaxHP and not self.dna.name == 'foreman' and not self.dna.name == 'clubpres' and not self.dna.name == 'clerk' and not self.dna.name == 'supervis':
            self.currHP = self.maxHP * self.hardMaxHP
        else:
            self.currHP = hp
        return None

    def b_setHP(self, hp):
        self.setHP(hp)
        self.d_setHP(hp)

    def d_setHP(self, hp):
        self.sendUpdate('setHP', [hp])
		
    def setMaxHP(self, hp):
        self.maxHP = hp
        self.currHP = hp

    def d_setMaxHP(self, hp):
        self.sendUpdate('setMaxHP', [hp])
		
    def b_setMaxHP(self, hp):
        self.d_setMaxHP(hp)
        self.setMaxHP(hp)
		
    def getMaxHP(self):
        return self.maxHP
		
    def setDamageMultiplier(self, mult):
        self.dmgMult = mult
		
    def getDamageMultiplier(self):
        return self.dmgMult

    def setVulnerabilityMultiplier(self, vulnerability):
        self.vulnerabilityMult = vulnerability

    def getVulnerabilityMultiplier(self):
        return self.vulnerabilityMult

    def releaseControl(self):
        pass

    def getDeathEvent(self):
        return 'cogDead-%s' % self.doId

    def resume(self):
        self.notify.debug('resume, hp=%s' % self.currHP)
        if self.currHP <= 0:
            messenger.send(self.getDeathEvent())
            self.requestRemoval()

    def prepareToJoinBattle(self):
        pass

    def b_setSkelecog(self, flag):
        if flag == None:
            flag = 0
        self.isSkeleton(flag)
        self.setSkelecog(flag)
        self.d_setSkelecog(flag)

    def setSkelecog(self, flag):
        if flag == None:
            flag = 0
        self.isSkeleton = flag
        SuitBase.SuitBase.setSkelecog(self, flag)
        if self.isSkeleton:
            self.maxHP = int(self.maxHP * random.uniform(.75, 1.25))
            self.currHP = self.maxHP

    def b_setSkeleton(self, isSkeleton):
        if isSkeleton == None:
            isSkeleton = 0
        self.isSkeleton(isSkeleton)
        self.d_setSkeleton(self.getSkeleton())

    def d_setSkeleton(self, isSkeleton):
        self.sendUpdate('setisSkeleton', [isSkeleton])

    def getSkeleton(self):
        return self.isSkeleton

    def setSkeleton(self, isSkeleton):
        if isSkeleton == None:
            isSkeleton = 0
        self.isSkeleton = isSkeleton

    def d_setSkelecog(self, flag):
        self.sendUpdate('setSkelecog', [flag])

    def isForeman(self):
        return 0

    def isSupervisor(self):
        return 0

    def setVirtual(self, flag):
        if flag == None:
            flag = 0
        self.isVirtual = flag
        SuitBase.SuitBase.setVirtual(self, flag)

    def getVirtual(self):
        return self.isVirtual

    def setWaiter(self, flag):
        SuitBase.SuitBase.setWaiter(self, flag)

    def d_setWaiter(self, flag):
        self.sendUpdate('setWaiter', [flag])

    def b_setWaiter(self, flag):
        self.setWaiter(flag)
        self.d_setWaiter(flag)

    def getWaiter(self):
        return self.waiter