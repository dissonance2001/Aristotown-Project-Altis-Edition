#Embedded file name: toontown.suit.DistributedBossbotBossAI
from functools import cmp_to_key
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm import FSM
from direct.interval.IntervalGlobal import LerpPosInterval
import math
from pandac.PandaModules import Point3
import random
from otp.ai.MagicWordGlobal import *
from toontown.battle import BattleExperienceAI
from toontown.battle import DistributedBattleDinersAI
from toontown.battle import DistributedBattleMinibossAI
from toontown.battle import DistributedBattleWaitersAI
from toontown.building import SuitBuildingGlobals
from toontown.coghq import DistributedBanquetTableAI
from toontown.coghq import DistributedFoodBeltAI
from toontown.coghq import DistributedGolfSpotAI
from toontown.suit import DistributedBossCogAI
from toontown.suit import DistributedMinibossAI
from toontown.suit import DistributedSuitAI
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownBattleGlobals
from toontown.toonbase import ToontownGlobals

class DistributedDirectorsAI(DistributedMinibossAI.DistributedMinibossAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedDirectorsAI')
    maxToonLevels = 77
    toonUpLevels = [15,
     20,
     25,
     30]

    def __init__(self, air):
        DistributedMinibossAI.DistributedMinibossAI.__init__(self, air, 'c')
        FSM.FSM.__init__(self, 'DistributedDirectorsAI')
        self.battleOneBattlesMade = False
        self.battleThreeBattlesMade = False
        self.battleFourSetup = False
        self.foodBelts = []
        self.numTables = 1
        self.numDinersPerTable = 3
        self.tables = []
        self.numGolfSpots = 4
        self.golfSpots = []
        self.toonFoodStatus = {}
        self.bossMaxDamage = 2400
        self.threatDict = {}
        self.keyStates.append('BattleFour')
        self.battleFourStart = 0
        self.battleDifficulty = 0
        self.movingToTable = False
        self.tableDest = -1
        self.curTable = -1
        self.speedDamage = 0
        self.maxSpeedDamage = ToontownGlobals.BossbotMaxSpeedDamage
        self.speedRecoverRate = ToontownGlobals.BossbotSpeedRecoverRate
        self.speedRecoverStartTime = 0
        self.battleFourTimeStarted = 0
        self.numDinersExploded = 0
        self.numMoveAttacks = 0
        self.numGolfAttacks = 0
        self.numGearAttacks = 0
        self.numGolfAreaAttacks = 0
        self.numToonupGranted = 0
        self.totalLaffHealed = 0
        self.toonupsGranted = []
        self.doneOvertimeOneAttack = False
        self.doneOvertimeTwoAttack = False
        self.overtimeOneTime = simbase.air.config.GetInt('overtime-one-time', 1200)
        self.battleFourDuration = simbase.air.config.GetInt('battle-four-duration', 1800)
        self.overtimeOneStart = float(self.overtimeOneTime) / self.battleFourDuration
        self.moveAttackAllowed = True

    def delete(self):
        self.notify.debug('DistributedBossbotBossAI.delete')
        self.deleteBanquetTables()
        self.deleteFoodBelts()
        self.deleteGolfSpots()
        return DistributedMinibossAI.DistributedMinibossAI.delete(self)

    def enterElevator(self):
        DistributedMinibossAI.DistributedMinibossAI.enterElevator(self)
        self.makeBattleOneBattles()

    def enterIntroduction(self):
        self.arenaSide = None
        self.makeBattleOneBattles()
        self.barrier = self.beginBarrier('Introduction', self.involvedToons, 300, self.doneIntroduction)
        self.createFoodBelts()
        self.createBanquetTables()

    def makeBattleOneBattles(self):
        self.postBattleState = 'PrepareBattleTwo'
        self.initializeBattles(1, ToontownGlobals.BossbotBossBattleOnePosHpr)
        self.battleOneBattlesMade = True

    def getHoodId(self):
        return ToontownGlobals.LawbotHQ

    def generateSuits(self, battleNumber):
        if battleNumber == 1:
            cogs = self.invokeEmptyPlanner(11, random.choice(('blitpair1', 'blitpair2', 'blitpair3', 'blitpair4', 'blitpair5', 'blitpair6')))
            activeSuits = cogs['activeSuits']
            reserveSuits = cogs['reserveSuits']
            random.shuffle(activeSuits)
            while len(activeSuits) >= 6:
                suit = activeSuits.pop()
                reserveSuits.append((suit, 100))

            def compareJoinChance(a, b):
                return cmp(a[1], b[1])

            reserveSuits.sort(key=cmp_to_key(compareJoinChance))
            return {'activeSuits': activeSuits,
                    'reserveSuits': reserveSuits}
        if battleNumber == 2:
            cogs = self.invokeEmptyPlanner(11, 'crf2')
            activeSuits = cogs['activeSuits']
            reserveSuits = cogs['reserveSuits']
            random.shuffle(activeSuits)
            while len(activeSuits) >= 6:
                suit = activeSuits.pop()
                reserveSuits.append((suit, 100))

            def compareJoinChance(a, b):
                return cmp(a[1], b[1])

            reserveSuits.sort(key=cmp_to_key(compareJoinChance))
            return {'activeSuits': activeSuits,
                    'reserveSuits': reserveSuits}

    def generateNewReserves(self, battleNumber, specialCode):
        if battleNumber == 1:
            cogs = self.invokeReservesPlanner(11, specialCode)
            reserveSuits = cogs['reserveSuits']
            return {'reserveSuits': reserveSuits}
        elif battleNumber == 2:
            cogs = self.invokeReservesPlanner(11, specialCode)
            reserveSuits = cogs['reserveSuits']
            return {'reserveSuits': reserveSuits}

    def invokeSuitPlanner(self, buildingCode, skelecog):
        suits = DistributedMinibossAI.DistributedMinibossAI.invokeSuitPlanner(self, buildingCode, skelecog)
        activeSuits = suits['activeSuits'][:]
        reserveSuits = suits['reserveSuits'][:]
        if len(activeSuits) + len(reserveSuits) >= 6:
            while len(activeSuits) < 6:
                activeSuits.append(reserveSuits.pop()[0])

        retval = {'activeSuits': activeSuits,
                  'reserveSuits': reserveSuits}
        return retval

    def makeBattle(self, bossCogPosHpr, battlePosHpr, roundCallback, finishCallback, battleNumber, battleSide):
        battle = DistributedBattleMinibossAI.DistributedBattleMinibossAI(self.air, self, roundCallback, finishCallback,
                                                                         battleSide)
        self.setBattlePos(battle, bossCogPosHpr, battlePosHpr)
        battle.suitsKilled = self.suitsKilled
        battle.battleCalc.toonSkillPtsGained = self.toonSkillPtsGained
        battle.toonExp = self.toonExp
        battle.toonOrigQuests = self.toonOrigQuests
        battle.toonItems = self.toonItems
        battle.toonOrigMerits = self.toonOrigMerits
        battle.toonMerits = self.toonMerits
        battle.toonParts = self.toonParts
        battle.helpfulToons = self.helpfulToons
        mult = ToontownBattleGlobals.getBossBattleCreditMultiplier(battleNumber)
        battle.battleCalc.setSkillCreditMultiplier(mult)
        battle.generateWithRequired(self.zoneId)
        return battle

    def initializeBattles(self, battleNumber, bossCogPosHpr):
        self.resetBattles()
        if not self.involvedToons:
            self.notify.warning('initializeBattles: no toons!')
            return
        self.battleNumber = battleNumber
        suitHandles = self.generateSuits(battleNumber)
        self.suits = suitHandles['activeSuits']
        self.activeSuits = self.suits[:]
        self.reserveSuits = suitHandles['reserveSuits']
        suitHandles = self.generateSuits(battleNumber)
        if self.toons:
            self.battle = self.makeBattle(bossCogPosHpr, ToontownGlobals.DinerBattleAPosHpr, self.handleRoundADone,
                                          self.handleBattleADone, battleNumber, 0)
            self.battleId = self.battle.doId
        else:
            self.moveSuits(self.activeSuits)
            self.suits = []
            self.activeSuits = []
            if self.arenaSide == None:
                self.b_setArenaSide(0)
        self.sendBattleIds()
        return

    def enterPrepareBattleTwo(self):
        self.barrier = self.beginBarrier('PrepareBattleTwo', self.involvedToons, 120, self.__donePrepareBattleTwo)
        self.createFoodBelts()
        self.createBanquetTables()

    def __donePrepareBattleTwo(self, avIds):
        self.b_setState('BattleTwo')

    def exitPrepareBattleTwo(self):
        self.ignoreBarrier(self.barrier)

    def createFoodBelts(self):
        if self.foodBelts:
            return
        for i in range(2):
            newBelt = DistributedFoodBeltAI.DistributedFoodBeltAI(self.air, self, i)
            self.foodBelts.append(newBelt)
            newBelt.generateWithRequired(self.zoneId)

    def deleteFoodBelts(self):
        for belt in self.foodBelts:
            belt.requestDelete()

        self.foodBelts = []

    def createBanquetTables(self):
        if self.tables:
            return
        for i in range(15):
            newTable = DistributedBanquetTableAI.DistributedBanquetTableAI(self.air, self, i, 0, 1)
            self.tables.append(newTable)
            newTable.generateWithRequired(self.zoneId)

    def deleteBanquetTables(self):
        for table in self.tables:
            table.requestDelete()

        self.tables = []

    def enterBattleTwo(self):
        self.resetBattles()
        self.barrier = self.beginBarrier('BattleTwo', self.involvedToons, ToontownGlobals.BossbotBossServingDuration + 1, self.__doneBattleTwo)

    def exitBattleTwo(self):
        self.ignoreBarrier(self.barrier)

    def __doneBattleTwo(self, avIds):
        self.b_setState('PrepareBattleThree')

    def requestGetFood(self, beltIndex, foodIndex, foodNum):
        grantRequest = False
        avId = self.air.getAvatarIdFromSender()
        if self.state != 'BattleTwo':
            grantRequest = False
        elif (beltIndex, foodNum) not in list(self.toonFoodStatus.values()):
            if avId not in self.toonFoodStatus:
                grantRequest = True
            elif self.toonFoodStatus[avId] == None:
                grantRequest = True
        if grantRequest:
            self.toonFoodStatus[avId] = (beltIndex, foodNum)
            self.sendUpdate('toonGotFood', [avId,
             beltIndex,
             foodIndex,
             foodNum])

    def requestServeFood(self, tableIndex, chairIndex):
        grantRequest = False
        avId = self.air.getAvatarIdFromSender()
        if self.state != 'BattleTwo':
            grantRequest = False
        elif tableIndex < len(self.tables):
            table = self.tables[tableIndex]
            dinerStatus = table.getDinerStatus(chairIndex)
            if dinerStatus in (table.HUNGRY, table.ANGRY):
                if self.toonFoodStatus[avId]:
                    grantRequest = True
        if grantRequest:
            self.toonFoodStatus[avId] = None
            table.foodServed(chairIndex)
            self.sendUpdate('toonServeFood', [avId, tableIndex, chairIndex])

    def enterPrepareBattleThree(self):
        self.barrier = self.beginBarrier('PrepareBattleThree', self.involvedToons, ToontownGlobals.BossbotBossServingDuration + 1, self.__donePrepareBattleThree)
        self.divideToons()
        self.makeBattleThreeBattles()

    def exitPrepareBattleThree(self):
        self.ignoreBarrier(self.barrier)

    def __donePrepareBattleThree(self, avIds):
        self.b_setState('BattleThree')

    def makeBattleThreeBattles(self):
        self.postBattleState = 'PrepareBattleTwo'
        self.initializeBattles(2, ToontownGlobals.BossbotBossBattleOnePosHpr)
        self.battleThreeBattlesMade = True

    def generateDinerSuits(self):
        diners = []
        for i in range(len(self.notDeadList)):
            if simbase.config.GetBool('bossbot-boss-cheat', 0):
                suit = self.__genSuitObject(self.zoneId, 2, 'c', 2, 0)
            else:
                info = self.notDeadList[i]
                suitType = info[2] - 4
                suitLevel = random.randint(info[2] - 1, info[2] + 3)
                suit = self.__genSuitObject(self.zoneId, suitType, None, suitLevel, 0)
                if random.randint(0, 100) <= ToontownBattleGlobals.EXECUTIVE_BASE_CHANCE:
                    suit.b_setExecutive(1)
                if random.randint(0, 100) <= ToontownBattleGlobals.GOVERNAUGHT_BASE_CHANCE and not suit.getExecutive():
                    suit.b_setGovernaught(1)
            diners.append((suit, 100))

        active = []
        for i in range(2):
            if simbase.config.GetBool('bossbot-boss-cheat', 0):
                suit = self.__genSuitObject(self.zoneId, 2, 'c', 2, 0)
            else:
                suitType = 8
                suitLevel = self.diffInfo[2] + 5
                suit = self.__genSuitObject(self.zoneId, suitType, 'c', suitLevel, 0)
            active.append(suit)

        return {'activeSuits': active,
         'reserveSuits': diners}

    def __genSuitObject(self, suitZone, suitType, bldgTrack, suitLevel, revives = 0):
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, None)
        skel = self.__setupSuitInfo(newSuit, bldgTrack, suitLevel, suitType)
        if skel:
            newSuit.setSkelecog(1)
        newSuit.setSkeleRevives(revives)
        newSuit.generateWithRequired(suitZone)
        newSuit.node().setName('suit-%s' % newSuit.doId)
        return newSuit

    def __setupSuitInfo(self, suit, bldgTrack, suitLevel, suitType):
        dna = SuitDNA.SuitDNA()
        dept = random.choice(['s', 'm', 'l', 'c', 'g', 't'])
        dna.newSuitRandom(level=suitType, dept=dept)
        suit.dna = dna
        self.notify.debug('Creating suit type ' + suit.dna.name + ' of level ' + str(suitLevel) + ' from type ' + str(suitType) + ' and track ' + str(bldgTrack))
        suit.setLevel(suitLevel)
        return False

    def enterBattleThree(self):
        self.makeBattleThreeBattles()
        if self.battle:
            self.battle.startBattle(self.toons, self.suits)

    def exitBattleThree(self):
        self.resetBattles()

    def enterPrepareBattleFour(self):
        self.resetBattles()
        self.setupBattleFourObjects()
        self.barrier = self.beginBarrier('PrepareBattleFour', self.involvedToons, 49, self.__donePrepareBattleFour)

    def __donePrepareBattleFour(self, avIds):
        self.b_setState('BattleFour')

    def exitPrepareBattleFour(self):
        self.ignoreBarrier(self.barrier)

    def enterBattleFour(self):
        self.battleFourTimeStarted = globalClock.getFrameTime()
        self.numToonsAtStart = len(self.involvedToons)
        self.resetBattles()
        self.setupBattleFourObjects()
        self.battleFourStart = globalClock.getFrameTime()
        self.waitForNextAttack(5)

    def exitBattleFour(self):
        self.recordCeoInfo()
        for belt in self.foodBelts:
            belt.goInactive()

    def recordCeoInfo(self):
        didTheyWin = 0
        if self.bossDamage == self.bossMaxDamage:
            didTheyWin = 1
        self.battleFourTimeInMin = globalClock.getFrameTime() - self.battleFourTimeStarted
        self.battleFourTimeInMin /= 60.0
        self.numToonsAtEnd = 0
        toonHps = []
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                self.numToonsAtEnd += 1
                toonHps.append(toon.hp)

        self.air.writeServerEvent('ceoInfo', self.doId, '%d|%.2f|%d|%d|%d|%d|%d|%d|%s|%s|%.1f|%d|%d|%d|%d|%d}%d|%s|' % (didTheyWin,
         self.battleFourTimeInMin,
         self.battleDifficulty,
         self.numToonsAtStart,
         self.numToonsAtEnd,
         self.numTables,
         self.numTables * self.numDinersPerTable,
         self.numDinersExploded,
         toonHps,
         self.involvedToons,
         self.speedDamage,
         self.numMoveAttacks,
         self.numGolfAttacks,
         self.numGearAttacks,
         self.numGolfAreaAttacks,
         self.numToonupGranted,
         self.totalLaffHealed,
         'ceoBugfixes'))

    def setupBattleFourObjects(self):
        if self.battleFourSetup:
            return
        if not self.tables:
            self.createBanquetTables()
        for table in self.tables:
            table.goFree()

        if not self.golfSpots:
            self.createGolfSpots()
        self.createFoodBelts()
        for belt in self.foodBelts:
            belt.goToonup()

        self.battleFourSetup = True

    def hitBoss(self, bossDamage):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'hitBoss from unknown avatar'):
            return
        if self.attackCode == ToontownGlobals.BossCogDizzyNow:
            bossDamage *= 2
        if bossDamage >= 3 and self.attackCode != ToontownGlobals.BossCogDizzyNow:
            if random.random() <= 0.3:
                self.b_setAttackCode(ToontownGlobals.BossCogDizzyNow)
        if bossDamage < 1:
            self.air.writeServerEvent('suspicious', avId, 'Bossbot: Toon sent an attack less than 1 damage!')
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BattleFour':
            return
        bossDamage *= 2
        bossDamage = min(self.getBossDamage() + bossDamage, self.bossMaxDamage)
        self.b_setBossDamage(bossDamage, 0, 0)
        healthDisp = int(self.bossMaxDamage - self.bossDamage)
        if healthDisp < 0:
            healthDisp = 0
        #self.setHealthTag(str(healthDisp) + '/' + str(int(self.bossMaxDamage)))
        if self.bossDamage >= self.bossMaxDamage:
            self.b_setState('Victory')
        else:
            self.__recordHit(bossDamage)

    def __recordHit(self, bossDamage):
        now = globalClock.getFrameTime()
        self.hitCount += 1
        avId = self.air.getAvatarIdFromSender()
        self.addThreat(avId, bossDamage)

    def getBossDamage(self):
        return self.bossDamage

    def b_setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        self.d_setBossDamage(bossDamage, recoverRate, recoverStartTime)
        self.setBossDamage(bossDamage, recoverRate, recoverStartTime)

    def setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        self.bossDamage = bossDamage
        self.recoverRate = recoverRate
        self.recoverStartTime = recoverStartTime

    def d_setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        timestamp = globalClockDelta.localToNetworkTime(recoverStartTime)
        self.sendUpdate('setBossDamage', [bossDamage, recoverRate, timestamp])

    def getSpeedDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.speedRecoverStartTime
        self.notify.debug('elapsed=%s' % elapsed)
        floatSpeedDamage = max(self.speedDamage - self.speedRecoverRate * elapsed / 60.0, 0)
        self.notify.debug('floatSpeedDamage = %s' % floatSpeedDamage)
        return int(max(self.speedDamage - self.speedRecoverRate * elapsed / 60.0, 0))

    def getFloatSpeedDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.speedRecoverStartTime
        floatSpeedDamage = max(self.speedDamage - self.speedRecoverRate * elapsed / 60.0, 0)
        self.notify.debug('floatSpeedDamage = %s' % floatSpeedDamage)
        return max(self.speedDamage - self.speedRecoverRate * elapsed / 60.0, 0)

    def b_setSpeedDamage(self, speedDamage, recoverRate, recoverStartTime):
        self.d_setSpeedDamage(speedDamage, recoverRate, recoverStartTime)
        self.setSpeedDamage(speedDamage, recoverRate, recoverStartTime)

    def setSpeedDamage(self, speedDamage, recoverRate, recoverStartTime):
        self.speedDamage = speedDamage
        self.speedRecoverRate = recoverRate
        self.speedRecoverStartTime = recoverStartTime

    def d_setSpeedDamage(self, speedDamage, recoverRate, recoverStartTime):
        timestamp = globalClockDelta.localToNetworkTime(recoverStartTime)
        self.sendUpdate('setSpeedDamage', [speedDamage, recoverRate, timestamp])

    def createGolfSpots(self):
        if self.golfSpots:
            return
        for i in range(self.numGolfSpots):
            newGolfSpot = DistributedGolfSpotAI.DistributedGolfSpotAI(self.air, self, i)
            self.golfSpots.append(newGolfSpot)
            newGolfSpot.generateWithRequired(self.zoneId)
            newGolfSpot.forceFree()

    def deleteGolfSpots(self):
        for spot in self.golfSpots:
            spot.requestDelete()

        self.golfSpots = []

    def ballHitBoss(self, speedDamage):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'hitBoss from unknown avatar'):
            return
        if speedDamage < 1:
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BattleFour':
            return
        now = globalClock.getFrameTime()
        newDamage = self.getSpeedDamage() + speedDamage
        self.notify.debug('newDamage = %s' % newDamage)
        speedDamage = min(self.getFloatSpeedDamage() + speedDamage, self.maxSpeedDamage)
        self.b_setSpeedDamage(speedDamage, self.speedRecoverRate, now)
        self.addThreat(avId, 0.1)

    def enterVictory(self):
        self.resetBattles()
        for table in self.tables:
            table.turnOff()

        for golfSpot in self.golfSpots:
            golfSpot.turnOff()

        self.suitsKilled.append({'type': None,
         'level': None,
         'track': self.dna.dept,
         'isSkelecog': 0,
         'isForeman': 0,
         'isBoss': 1,
         'isSupervisor': 0,
         'isVirtual': 0,
         'isElite': 0,
         'activeToons': self.involvedToons[:]})
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 30, self.__doneVictory)

    def __doneVictory(self, avIds):
        self.d_setBattleExperience()
        self.b_setState('Reward')
        BattleExperienceAI.assignRewards(self.involvedToons, self.toonSkillPtsGained, self.suitsKilled, ToontownGlobals.dept2cogHQ(self.dept), self.helpfulToons)
        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                self.givePinkSlipReward(toon)
                toon.b_promote(self.deptIndex)
                toon.addStat(ToontownGlobals.STATS_CEO)

    def givePinkSlipReward(self, toon):
        toon.addPinkSlips(self.battleDifficulty + 1)

    def getThreat(self, toonId):
        if toonId in self.threatDict:
            return self.threatDict[toonId]
        else:
            return 0

    def addThreat(self, toonId, threat):
        if toonId in self.threatDict:
            self.threatDict[toonId] += threat
        else:
            self.threatDict[toonId] = threat

    def subtractThreat(self, toonId, threat):
        if toonId in self.threatDict:
            self.threatDict[toonId] -= threat
        else:
            self.threatDict[toonId] = 0
        if self.threatDict[toonId] < 0:
            self.threatDict[toonId] = 0

    def waitForNextAttack(self, delayTime):
        currState = self.getCurrentOrNextState()
        if currState == 'BattleFour':
            taskName = self.uniqueName('NextAttack')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.doNextAttack, taskName)

    def doNextAttack(self, task):
        attackCode = -1
        optionalParam = 0
        if self.attackCode == ToontownGlobals.BossCogDizzyNow:
            attackCode = ToontownGlobals.BossCogRecoverDizzyAttack
        if self.movingToTable:
            self.waitForNextAttack(5)
        elif self.bossDamage >= self.bossMaxDamage * 0.5 and not self.doneOvertimeOneAttack:
            attackCode = ToontownGlobals.BossCogOvertimeAttack
            self.doneOvertimeOneAttack = True
            optionalParam = 0
        elif self.bossDamage >= self.bossMaxDamage * 0.75 and not self.doneOvertimeTwoAttack:
            attackCode = ToontownGlobals.BossCogOvertimeAttack
            self.doneOvertimeTwoAttack = True
            optionalParam = 1
        else:
            attackCode = random.choice([ToontownGlobals.BossCogGolfAreaAttack,
                                        ToontownGlobals.BossCogFrontAttack,
                                        ToontownGlobals.BossCogAreaAttack,
                                        ToontownGlobals.BossCogChaseAttack,
                                        ToontownGlobals.BossCogGolfAttack,
                                        ToontownGlobals.BossCogDirectedAttack])
        if attackCode == ToontownGlobals.BossCogAreaAttack:
            self.__doAreaAttack()
        if attackCode == ToontownGlobals.BossCogGolfAreaAttack:
            self.__doGolfAreaAttack()
        if attackCode == ToontownGlobals.BossCogGolfAttack:
            self.__doDirectedAttack2()
        elif attackCode == ToontownGlobals.BossCogDirectedAttack:
            self.__doDirectedAttack()
        elif attackCode >= 0:
            self.b_setAttackCode(attackCode, optionalParam)

    def __doDirectedAttack(self):
        toonId = self.getMaxThreatToon()
        self.notify.debug('toonToAttack=%s' % toonId)
        unflattenedToons = self.getUnflattenedToons()
        attackTotallyRandomToon = random.random() < 0.1
        if unflattenedToons and (attackTotallyRandomToon or toonId == 0):
            toonId = random.choice(unflattenedToons)
        if toonId:
            toonThreat = self.getThreat(toonId)
            toonThreat *= 0.25
            threatToSubtract = max(toonThreat, 10)
            self.subtractThreat(toonId, threatToSubtract)
            if self.isToonRoaming(toonId):
                #self.b_setAttackCode(ToontownGlobals.BossCogGolfAttack, toonId)
                self.b_setAttackCode(ToontownGlobals.BossCogChaseAttack, toonId)
                self.numGolfAttacks += 1
            elif self.isToonOnTable(toonId):
                doesMoveAttack = simbase.air.config.GetBool('ceo-does-move-attack', 1)
                if doesMoveAttack:
                    chanceToShoot = 0.25
                else:
                    chanceToShoot = 1.0
                if not self.moveAttackAllowed:
                    self.notify.debug('moveAttack is not allowed, doing gearDirectedAttack')
                    chanceToShoot = 1.0
                if random.random() < chanceToShoot:
                    self.b_setAttackCode(ToontownGlobals.BossCogGearDirectedAttack, toonId)
                    self.numGearAttacks += 1
                else:
                    tableIndex = self.getToonTableIndex(toonId)
                    self.doMoveAttack(tableIndex)
            else:
                self.b_setAttackCode(ToontownGlobals.BossCogGolfAttack, toonId)
        else:
            uprightTables = self.getUprightTables()
            if uprightTables:
                tableToMoveTo = random.choice(uprightTables)
                self.doMoveAttack(tableToMoveTo)
            else:
                self.waitForNextAttack(4)

    def __doDirectedAttack2(self):
        toonId = self.getMaxThreatToon()
        self.notify.debug('toonToAttack=%s' % toonId)
        unflattenedToons = self.getUnflattenedToons()
        attackTotallyRandomToon = random.random() < 0.1
        if unflattenedToons and (attackTotallyRandomToon or toonId == 0):
            toonId = random.choice(unflattenedToons)
        if toonId:
            toonThreat = self.getThreat(toonId)
            toonThreat *= 0.25
            threatToSubtract = max(toonThreat, 10)
            self.subtractThreat(toonId, threatToSubtract)
            self.b_setAttackCode(ToontownGlobals.BossCogGolfAttack, toonId)
            self.numGolfAttacks += 1
        else:
            uprightTables = self.getUprightTables()
            if uprightTables:
                tableToMoveTo = random.choice(uprightTables)
                self.doMoveAttack(tableToMoveTo)
            else:
                self.waitForNextAttack(4)

    def doMoveAttack(self, tableIndex):
        if self.attackCode == ToontownGlobals.BossCogDizzyNow:
            self.b_setAttackCode(ToontownGlobals.BossCogRecoverDizzyAttack)
        self.numMoveAttacks += 1
        self.movingToTable = True
        self.tableDest = tableIndex
        self.b_setAttackCode(ToontownGlobals.BossCogMoveAttack, tableIndex)

    def getUnflattenedToons(self):
        result = []
        uprightTables = self.getUprightTables()
        for toonId in self.involvedToons:
            toonTable = self.getToonTableIndex(toonId)
            if toonTable >= 0 and toonTable not in uprightTables:
                pass
            else:
                result.append(toonId)

        return result

    def getMaxThreatToon(self):
        returnedToonId = 0
        maxThreat = 0
        maxToons = []
        for toonId in self.threatDict:
            curThreat = self.threatDict[toonId]
            tableIndex = self.getToonTableIndex(toonId)
            if tableIndex > -1 and self.tables[tableIndex].state == 'Flat':
                pass
            elif curThreat > maxThreat:
                maxToons = [toonId]
                maxThreat = curThreat
            elif curThreat == maxThreat:
                maxToons.append(toonId)

        if maxToons:
            returnedToonId = random.choice(maxToons)
        return returnedToonId

    def getToonDifficulty(self):
        totalCogSuitTier = 0
        totalToons = 0
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                totalToons += 1
                totalCogSuitTier += toon.cogTypes[0]

        averageTier = 1
        return int(averageTier)

    def calcAndSetBattleDifficulty(self):
        self.toonLevels = self.getToonDifficulty()
        battleDifficulty = int(math.floor(self.toonLevels / 2))
        self.b_setBattleDifficulty(battleDifficulty)

    def b_setBattleDifficulty(self, batDiff):
        self.setBattleDifficulty(batDiff)
        self.d_setBattleDifficulty(batDiff)

    def setBattleDifficulty(self, batDiff):
        self.battleDifficulty = batDiff

    def d_setBattleDifficulty(self, batDiff):
        self.sendUpdate('setBattleDifficulty', [batDiff])

    def getUprightTables(self):
        tableList = []
        for table in self.tables:
            if table.state != 'Flat':
                tableList.append(table.index)

        return tableList

    def getToonTableIndex(self, toonId):
        tableIndex = -1
        for table in self.tables:
            if table.avId == toonId:
                tableIndex = table.index
                break

        return tableIndex

    def getToonGolfSpotIndex(self, toonId):
        golfSpotIndex = -1
        for golfSpot in self.golfSpots:
            if golfSpot.avId == toonId:
                golfSpotIndex = golfSpot.index
                break

        return golfSpotIndex

    def isToonOnTable(self, toonId):
        result = self.getToonTableIndex(toonId) != -1
        return result

    def isToonOnGolfSpot(self, toonId):
        result = self.getToonGolfSpotIndex(toonId) != -1
        return result

    def isToonRoaming(self, toonId):
        result = not self.isToonOnTable(toonId) and not self.isToonOnGolfSpot(toonId)
        return result

    def reachedTable(self, tableIndex):
        if self.movingToTable and self.tableDest == tableIndex:
            self.movingToTable = False
            self.curTable = self.tableDest
            self.tableDest = -1

    def hitTable(self, tableIndex):
        self.notify.debug('hitTable tableIndex=%d' % tableIndex)
        if tableIndex < len(self.tables):
            table = self.tables[tableIndex]
            if table.state != 'Flat':
                table.goFlat()

    def awayFromTable(self, tableIndex):
        self.notify.debug('awayFromTable tableIndex=%d' % tableIndex)
        if tableIndex < len(self.tables):
            taskName = 'Unflatten-%d' % tableIndex
            unflattenTime = self.diffInfo[3]
            taskMgr.doMethodLater(unflattenTime, self.unflattenTable, taskName, extraArgs=[tableIndex])

    def unflattenTable(self, tableIndex):
        if tableIndex < len(self.tables):
            table = self.tables[tableIndex]
            if table.state == 'Flat':
                if table.avId and table.avId in self.involvedToons:
                    table.forceControl(table.avId)
                else:
                    table.goFree()

    def incrementDinersExploded(self):
        self.numDinersExploded += 1

    def magicWordHit(self, damage, avId):
        self.hitBoss(damage)

    def __doAreaAttack(self):
        if self.attackCode == ToontownGlobals.BossCogDizzyNow:
            pass
        self.b_setAttackCode(ToontownGlobals.BossCogAreaAttack)
        self.waitForNextAttack(5)

    def __doGolfAreaAttack(self):
        if self.attackCode == ToontownGlobals.BossCogDizzyNow:
            pass
        self.numGolfAreaAttacks += 1
        self.b_setAttackCode(ToontownGlobals.BossCogGolfAreaAttack)
        self.waitForNextAttack(10)

    def hitToon(self, toonId):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId != toonId, 'hitToon on self'):
            return
        if avId not in self.involvedToons or toonId not in self.involvedToons:
            return
        toon = self.air.doId2do.get(toonId)
        if toon:
            self.healToon(toon, 1)
            self.sendUpdate('toonGotHealed', [toonId])

    def requestGetToonup(self, beltIndex, toonupIndex, toonupNum):
        grantRequest = False
        avId = self.air.getAvatarIdFromSender()
        if self.state != 'BattleFour':
            grantRequest = False
        elif (beltIndex, toonupNum) not in self.toonupsGranted:
            toon = simbase.air.doId2do.get(avId)
            if toon:
                grantRequest = True
        if grantRequest:
            self.toonupsGranted.insert(0, (beltIndex, toonupNum))
            if len(self.toonupsGranted) > 8:
                self.toonupsGranted = self.toonupsGranted[0:8]
            self.sendUpdate('toonGotToonup', [avId,
             beltIndex,
             toonupIndex,
             toonupNum])
            if toonupIndex < len(self.toonUpLevels):
                self.healToon(toon, self.toonUpLevels[toonupIndex])
                self.numToonupGranted += 1
                self.totalLaffHealed += self.toonUpLevels[toonupIndex]
            else:
                self.notify.warning('requestGetToonup this should not happen')
                self.healToon(toon, 1)

    def toonLeftTable(self, tableIndex):
        if self.movingToTable and self.tableDest == tableIndex:
            if random.random() < 0.5:
                self.movingToTable = False
                self.waitForNextAttack(0)

    def getBattleFourTime(self):
        if self.state != 'BattleFour':
            t1 = 0
        else:
            elapsed = globalClock.getFrameTime() - self.battleFourStart
            t1 = elapsed / float(self.battleFourDuration)
        return t1

    def getDamageMultiplier(self):
        mult = ToontownGlobals.BossbotBossDamageMultipliers[self.battleDifficulty]
        if self.doneOvertimeOneAttack and not self.doneOvertimeTwoAttack:
            mult *= 1.25
        elif self.doneOvertimeOneAttack and self.doneOvertimeTwoAttack:
            mult *= 2
        return mult

    def toggleMove(self):
        self.moveAttackAllowed = not self.moveAttackAllowed
        return self.moveAttackAllowed


@magicWord(category=CATEGORY_ADMINISTRATOR)
def skipDirectors():
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedDirectorsAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break

    if not boss:
        return "You aren't in a CEO!"
    if boss.state in ('PrepareBattleThree', 'BattleThree'):
        return "You can't skip this round."
    boss.exitIntroduction()
    boss.b_setState('PrepareBattleThree')

@magicWord(category=CATEGORY_ADMINISTRATOR)
def skipDirectorsCutscene():
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedDirectorsAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break

    if not boss:
        return "You aren't in a CEO!"
    if boss.state in ('PrepareBattleTwo', 'BattleTwo'):
        return "You can't skip this round."
    boss.exitIntroduction()
    boss.b_setState('PrepareBattleTwo')

@magicWord(category=CATEGORY_ADMINISTRATOR)
def skipDirectorsFirst():
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedDirectorsAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break

    if not boss:
        return "You aren't in a CEO!"
    if boss.state in ('PrepareBattleTwo', 'BattleTwo'):
        return "You can't skip this round."
    boss.exitIntroduction()
    boss.b_setState('PrepareBattleTwo')


@magicWord(category=CATEGORY_ADMINISTRATOR)
def skipDirectorsFinal():
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedDirectorsAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break

    if not boss:
        return "You aren't in a CEO!"
    if boss.state in ('PrepareBattleFour', 'BattleFour'):
        return "You can't skip this round."
    boss.exitIntroduction()
    boss.b_setState('PrepareBattleFour')

@magicWord(category=CATEGORY_ADMINISTRATOR)
def skipexecutscene():
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedDirectorsAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break

    if not boss:
        return "You aren't in a CEO!"
    if boss.state in ('PrepareBattleFour', 'BattleFour'):
        return "You can't skip this round."
    boss.exitIntroduction()
    boss.b_setState('BattleOne')
    return 'Skipping Executive Board cutscene...'


@magicWord(category=CATEGORY_ADMINISTRATOR)
def killDirectors():
    invoker = spellbook.getInvoker()
    boss = None
    for do in list(simbase.air.doId2do.values()):
        if isinstance(do, DistributedDirectorsAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break

    if not boss:
        return "You aren't in a CEO!"
    boss.b_setState('Victory')
    return 'Killed CEO.'
