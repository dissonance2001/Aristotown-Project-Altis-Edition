import math
import random
from typing import Optional

from panda3d.core import ConfigVariableBool, ConfigVariableInt

from toontown.inventory.base.Inventory import Inventory
from toontown.inventory.base.InventoryItem import InventoryItem
from toontown.inventory.enums.ItemEnums import BackgroundItemType, BoosterItemType, MaterialItemType
from toontown.clashsuit.suit import BossCogGlobals
from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.distributed.ClockDelta import globalClockDelta
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *
from direct.showbase.PythonUtil import fitDestAngle2Src, reduceAngle

from toontown.clashbattle.battle import BattleExperienceAI
from toontown.clashbattle.battle.distributed import DistributedBattleDinersAI
from toontown.clashbattle.battle.distributed import DistributedBattleWaitersAI
from toontown.building import ClashSuitBuildingGlobals
from toontown.coghq.bossbothq.DistributedBanquetTableAI import DistributedBanquetTableAI
from toontown.coghq.bossbothq import DistributedFoodBeltAI
from toontown.coghq.bossbothq import DistributedGolfSpotAI
from toontown.groups.GroupEnums import GroupType, Options
from toontown.instances import DistributedCutsceneSkipButtonAI
from toontown.quest3.context.CogBossContext import BossbotBossContext
from toontown.clashsuit.suit.DistributedSuitAI import DistributedSuitAI
from toontown.clashsuit.suit import SuitDNA
from toontown.clashsuit.suit.DistributedBossCogAI import DistributedBossCogAI
from toontown.toonbase import ToontownGlobals
from toontown.toon.gui.ToonTipGlobals import TTE
# from toontown.toonbase import BattleGlobals


@DirectNotifyCategory()
class DistributedBossbotBossAI(DistributedBossCogAI, FSM):
    maxToonLevels = 77
    toonUpLevels = [3, 6, 9, 12]

    groupType = GroupType.CEO

    def __init__(self, air):
        DistributedBossCogAI.__init__(self, air, 'c')
        FSM.__init__(self, 'DistributedBossbotBossAI')
        self.scene = NodePath("scene")
        self.reparentTo(self.scene)
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
        self.bossMaxDamage = BossCogGlobals.BossbotBossMaxDamage[0]
        self.threatDict = {}
        self.toonStunsDict = {}
        self.keyStates.append('BattleFour')
        self.battleFourStart = 0
        self.movingToTable = False
        self.tableDest = -1
        self.curTable = -1
        self.speedDamage = 0
        self.maxSpeedDamage = BossCogGlobals.BossbotMaxSpeedDamage
        self.speedRecoverRate = BossCogGlobals.BossbotSpeedRecoverRate
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
        self.desperationState = -1
        self.overtimeOneTime = ConfigVariableInt('overtime-one-time', 1200).getValue()
        self.battleFourDuration = ConfigVariableInt('battle-four-duration', 1800).getValue()
        self.overtimeOneStart = float(self.overtimeOneTime) / self.battleFourDuration

        self.moveAttackAllowed = True

        self.toonDamagesDict = {}
        self.toonSpeedDamagesDict = {}
        self.toonDinersFedDict = {}
        self.toonExeDinersFedDict = {}
        self.toonGolfBallsDict = {}
        self.numStuns = 0

        self.moveTrack = None

        # Collision traverser stuff
        self.cTrav = None
        self.traverseTask = "collisionTraverse"

        self.decaySpeedDamageTask = "decaySpeedDamage"

        self.targetedToon = None

        self.golfAreaAttacks = 0

    def announceGenerate(self):
        """Handle all required fields having been filled in."""
        DistributedBossCogAI.announceGenerate(self)

        # Put a small bubble around the CEO that triggers when he hits a table
        closeBubble = CollisionSphere(0, 0, 0, 10)
        closeBubble.setTangible(0)
        closeBubbleNode = CollisionNode('CloseBoss')
        closeBubbleNode.setIntoCollideMask(BitMask32(0))
        closeBubbleNode.setFromCollideMask(ToontownGlobals.BanquetTableBitmask)
        closeBubbleNode.addSolid(closeBubble)
        self.closeBubbleNode = closeBubbleNode
        self.closeHandler = CollisionHandlerEvent()
        self.closeHandler.addInPattern(self.uniqueName("closeEnter"))
        self.closeHandler.addOutPattern(self.uniqueName("closeExit"))
        self.closeBubbleNodePath = self.attachNewNode(closeBubbleNode)
        self.cTrav = CollisionTraverser(self.uniqueName("DistributedBossbotBossAI"))
        self.cTrav.addCollider(self.closeBubbleNodePath, self.closeHandler)

        self.traverseTask = self.uniqueName("collisionTraverse")

    def delete(self):
        self.notify.debug('DistributedBossbotBossAI.delete')
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('NextAttack'))
        self.deleteBanquetTables()
        self.deleteFoodBelts()
        self.deleteGolfSpots()
        self.stopMove()
        self.deleteTraverser()
        return DistributedBossCogAI.delete(self)

    def getContentSync(self) -> Optional[ContentSyncType]:
        return ContentSyncType.BBHQ

    def enterElevator(self):
        DistributedBossCogAI.enterElevator(self)
        self.calcAndSetBattleDifficulty()
        self.makeBattleOneBattles()

    def enterIntroduction(self):
        self.arenaSide = None
        self.makeBattleOneBattles()
        self.barrier = self.beginBarrier('Introduction', self.involvedToons, 45, self.doneIntroduction)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'ceo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)
        return

    def exitIntroduction(self):
        self.removeSkipButton()
        DistributedBossCogAI.exitIntroduction(self)

    def makeBattleOneBattles(self):
        if not self.battleOneBattlesMade:
            self.postBattleState = 'PrepareBattleTwo'
            self.initializeBattles(1, BossCogGlobals.BossbotBossBattleOnePosHpr)
            self.battleOneBattlesMade = True

    def getHoodId(self):
        return ToontownGlobals.BossbotHQ

    def generateSuits(self, battleNumber):
        if battleNumber == 1:
            retval = self.invokeSuitPlanner(self.getSuitPlanner(), 0)
            return retval
        else:
            suits = self.generateDinerSuits()
            return suits
    
    def getSuitPlanner(self):
        return ClashSuitBuildingGlobals.SPE.CEO_HARD

    def invokeSuitPlanner(self, buildingCode, skelecog):
        suits = DistributedBossCogAI.invokeSuitPlanner(self, buildingCode, skelecog)
        activeSuits = suits['activeSuits'][:]
        reserveSuits = suits['reserveSuits'][:]
        if len(activeSuits) + len(reserveSuits) >= 4:
            while len(activeSuits) < 4:
                activeSuits.append(reserveSuits.pop()[0])

        retval = {'activeSuits': activeSuits,
         'reserveSuits': reserveSuits}
        return retval

    def makeBattle(self, bossCogPosHpr, battlePosHpr, roundCallback, finishCallback, battleNumber, battleSide):
        if battleNumber == 1:
            battle = DistributedBattleWaitersAI.DistributedBattleWaitersAI(self.air, self, roundCallback, finishCallback, battleSide)
        else:
            battle = DistributedBattleDinersAI.DistributedBattleDinersAI(self.air, self, roundCallback, finishCallback, battleSide)
        self.setBattlePos(battle, bossCogPosHpr, battlePosHpr)
        battle.suitsKilled = self.suitsKilled
        battle.battleCalc.toonSkillPtsGained = self.toonSkillPtsGained
        battle.toonExp = self.toonExp
        battle.toonOrigQuests = self.toonOrigQuests
        battle.toonOrigMerits = self.toonOrigMerits
        battle.toonMerits = self.toonMerits
        battle.toonParts = self.toonParts
        battle.helpfulToons = self.helpfulToons

        activeSuits = self.activeSuitsA
        if battleSide:
            activeSuits = self.activeSuitsB
        for suit in activeSuits:
            battle.addSuit(suit)

        battle.generateWithRequired(self.zoneId)
        return battle

    def initializeBattles(self, battleNumber, bossCogPosHpr):
        self.resetBattles()
        if not self.involvedToons:
            self.notify.warning('initializeBattles: no toons!')
            return
        self.battleNumber = battleNumber
        suitHandles = self.generateSuits(battleNumber)
        self.suitsA = suitHandles['activeSuits']
        self.activeSuitsA = self.suitsA[:]
        self.reserveSuits = suitHandles['reserveSuits']
        if battleNumber == 2:
            if self.toonsB:
                movedSuit = self.suitsA.pop()
                self.suitsB = [movedSuit]
                self.activeSuitsB = [movedSuit]
                self.activeSuitsA.remove(movedSuit)
            else:
                self.suitsB = []
                self.activeSuitsB = []
        else:
            suitHandles = self.generateSuits(battleNumber)
            self.suitsB = suitHandles['activeSuits']
            self.activeSuitsB = self.suitsB[:]
            self.reserveSuits += suitHandles['reserveSuits']
        if self.toonsA:
            if battleNumber == 1:
                self.battleA = self.makeBattle(bossCogPosHpr, BossCogGlobals.WaiterBattleAPosHpr, self.handleRoundADone, self.handleBattleADone, battleNumber, 0)
                self.battleAId = self.battleA.doId
            else:
                self.battleA = self.makeBattle(bossCogPosHpr, BossCogGlobals.DinerBattleAPosHpr, self.handleRoundADone, self.handleBattleADone, battleNumber, 0)
                self.battleAId = self.battleA.doId
        else:
            self.moveSuits(self.activeSuitsA)
            self.suitsA = []
            self.activeSuitsA = []
            if self.arenaSide is None:
                self.b_setArenaSide(0)
        if self.toonsB:
            if battleNumber == 1:
                self.battleB = self.makeBattle(bossCogPosHpr, BossCogGlobals.WaiterBattleBPosHpr, self.handleRoundBDone, self.handleBattleBDone, battleNumber, 1)
                self.battleBId = self.battleB.doId
            else:
                self.battleB = self.makeBattle(bossCogPosHpr, BossCogGlobals.DinerBattleBPosHpr, self.handleRoundBDone, self.handleBattleBDone, battleNumber, 1)
                self.battleBId = self.battleB.doId
        else:
            self.moveSuits(self.activeSuitsB)
            self.suitsB = []
            self.activeSuitsB = []
            if self.arenaSide is None:
                self.b_setArenaSide(1)
        self.sendBattleIds()
        return

    def enterPrepareBattleTwo(self):
        self.barrier = self.beginBarrier('PrepareBattleTwo', self.involvedToons, 45, self.__donePrepareBattleTwo)
        self.createFoodBelts()
        self.createBanquetTables()
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'ceo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)
        typeList = []
        typeList.append({'type': 'ceo'})
        for toon in self.involvedToons:
            simbase.air.cogPageManager.toonEncounteredCogs(toon, typeList)

    def __donePrepareBattleTwo(self, avIds):
        self.b_setState('BattleTwo')

    def exitPrepareBattleTwo(self):
        self.removeSkipButton()
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
        self.calcAndSetBattleDifficulty()
        diffInfo = BossCogGlobals.BossbotBossDifficultySettings
        self.diffInfo = diffInfo
        self.numTables = diffInfo[0]
        self.numDinersPerTable = diffInfo[1]
        suitPlanner = ClashSuitBuildingGlobals.getSuitBuildingInfo(self.getSuitPlanner())
        dinerLevel = suitPlanner.suitBossLevels[0]
        # Create a range of levels which the diners can spawn at.
        if dinerLevel == 19:
            # Level range 11-17
            dinerLevels = list(range(11, 17 + 1))
        elif dinerLevel == 18:
            # Level range 12-16
            dinerLevels = list(range(12, 16 + 1))
        else:
            # Level range 11-15
            dinerLevels = list(range(11, 15 + 1))
        for i in range(self.numTables):
            newTable = DistributedBanquetTableAI(self.air, self, i, self.numDinersPerTable, dinerLevels)
            self.tables.append(newTable)
            newTable.generateWithRequired(self.zoneId)

    def deleteBanquetTables(self):
        for table in self.tables:
            table.requestDelete()

        self.tables = []

    def enterBattleTwo(self):
        self.resetBattles()
        self.createFoodBelts()
        self.createBanquetTables()
        for belt in self.foodBelts:
            belt.turnOn()

        for table in self.tables:
            table.turnOn()

        # Feeding the Cogs Tip
        for avId in self.involvedToons:
            toon = simbase.air.doId2do.get(avId)
            if toon:
                toon.showToonTip(TTE.TIP_CEO_FEED_COGS)

        self.barrier = self.beginBarrier('BattleTwo', self.involvedToons, BossCogGlobals.BossbotBossServingDuration + 1, self.__doneBattleTwo)

    def exitBattleTwo(self):
        self.ignoreBarrier(self.barrier)
        for table in self.tables:
            table.finishDiners()
            table.goInactive()

        for belt in self.foodBelts:
            belt.goInactive()

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
            elif self.toonFoodStatus[avId] is None:
                grantRequest = True
        if grantRequest:
            self.toonFoodStatus[avId] = (beltIndex, foodNum)
            self.sendUpdate('toonGotFood', [avId,
             beltIndex,
             foodIndex,
             foodNum])
        return

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
            self.toonDinersFedDict.setdefault(avId, 0)
            self.toonDinersFedDict[avId] += 1

            if table.diners[chairIndex].getElite():
                self.toonExeDinersFedDict.setdefault(avId, 0)
                self.toonExeDinersFedDict[avId] += 1

            self.toonFoodStatus[avId] = None
            table.foodServed(chairIndex)
            self.sendUpdate('toonServeFood', [avId, tableIndex, chairIndex])
        return

    def enterPrepareBattleThree(self):
        self.barrier = self.beginBarrier('PrepareBattleThree', self.involvedToons, BossCogGlobals.BossbotBossServingDuration + 1, self.__donePrepareBattleThree)
        self.divideToons()
        self.makeBattleThreeBattles()
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'ceo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def exitPrepareBattleThree(self):
        self.removeSkipButton()
        self.ignoreBarrier(self.barrier)

    def __donePrepareBattleThree(self, avIds):
        self.b_setState('BattleThree')

    def makeBattleThreeBattles(self):
        if not self.battleThreeBattlesMade:
            if not self.tables:
                self.createBanquetTables()
                for table in self.tables:
                    table.turnOn()
                    table.goInactive()

            aliveSuits = []
            for table in self.tables:
                tableInfo = table.aliveSuits
                aliveSuits += tableInfo

            self.aliveSuits = aliveSuits
            self.postBattleState = 'PrepareBattleFour'
            self.initializeBattles(2, BossCogGlobals.BossbotBossBattleThreePosHpr)
            self.battleThreeBattlesMade = True

    def generateDinerSuits(self):
        diners = []
        for suit in self.aliveSuits:
            diners.append((suit, 100))
        
        # Shuffle the order in which the diners will fly in.
        random.shuffle(diners)

        active = []
        for _ in range(2):
            suitType = 8
            suitLevel = 19
            deptType = 'c'
            suit = self.genSuitObject(self.zoneId, suitType, deptType, suitLevel, 0, 1)
            active.append(suit)

        return {'activeSuits': active,
                'reserveSuits': diners}

    def genSuitObject(self, suitZone, suitType, bldgTrack, suitLevel, revives = 0, executive = 0):
        newSuit = DistributedSuitAI(simbase.air, None)
        skel = self.__setupSuitInfo(newSuit, bldgTrack, suitLevel, suitType)
        if skel:
            newSuit.setSkelecog(1)
        newSuit.setSkeleRevives(revives)
        newSuit.setElite(executive)
        newSuit.generateWithRequired(suitZone)
        newSuit.node().setName('suit-%s' % newSuit.doId)
        return newSuit

    def __setupSuitInfo(self, suit, bldgTrack, suitLevel, suitType):
        dna = SuitDNA.SuitDNA()
        dna.newSuitRandom(suitType, bldgTrack)
        suit.dna = dna
        self.notify.debug('Creating suit type ' + suit.dna.name + ' of level ' + str(suitLevel) + ' from type ' + str(suitType) + ' and track ' + str(bldgTrack))
        suit.setLevel(suitLevel)
        return False

    def enterBattleThree(self):
        self.makeBattleThreeBattles()
        self.notify.debug('self.battleA = %s' % self.battleA)
        if self.battleA:
            self.battleA.startBattle(self.toonsA, self.suitsA)
        if self.battleB:
            self.battleB.startBattle(self.toonsB, self.suitsB)

    def exitBattleThree(self):
        self.resetBattles()

    def enterPrepareBattleFour(self):
        self.resetBattles()
        self.calcAndSetBattleDifficulty()
        self.setupBattleFourObjects()
        self.barrier = self.beginBarrier('PrepareBattleFour', self.involvedToons, 49, self.__donePrepareBattleFour)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'ceo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def __donePrepareBattleFour(self, avIds):
        self.b_setState('BattleFour')

    def exitPrepareBattleFour(self):
        self.removeSkipButton()
        self.ignoreBarrier(self.barrier)

    def enterBattleFour(self):
        self.setPosHpr(*BossCogGlobals.BossbotBossBattleOnePosHpr)
        self.battleFourTimeStarted = globalClock.getFrameTime()
        self.numToonsAtStart = len(self.involvedToons)
        self.resetBattles()
        self.setupBattleFourObjects()
        self.battleFourStart = globalClock.getFrameTime()
        self.waitForNextAttack(5)

        self.startTraverse()

        # Fighting the CEO Tip
        for avId in self.involvedToons:
            toon = simbase.air.doId2do.get(avId)
            if toon:
                toon.showToonTip(TTE.TIP_CEO_FIGHT_TUTORIAL)

    def exitBattleFour(self):
        self.recordCeoInfo()
        self.stopAttacks()
        self.b_stopMove()
        self.stopTraverse()

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
                toonHps.append(toon.getHp())

        self.air.writeServerEvent('ceoInfo', self.doId, '%d|%.2f|%d|%d|%d|%d|%d|%s|%s|%.1f|%d|%d|%d|%d|%d}%d|%s|' % (
         didTheyWin,
         self.battleFourTimeInMin,
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
        av = self.air.doId2do.get(avId)
        if not self.validate(avId, avId in self.involvedToons, 'hitBoss from unknown avatar'):
            return

        # Verify we are in BattleFour
        currState = self.getCurrentOrNextState()
        if currState != 'BattleFour':
            self.air.writeServerEvent('suspicious', avId, 'Bossbot: Toon sent an attack when boss state was not BattleFour!')
            return

        # Verify we are not sending negative or zero damage hits
        if bossDamage < 1:
            # Shouldn't EVER be less than 3. Dmg is sent in as 1-3 then processed
            self.air.writeServerEvent('suspicious', avId, 'Bossbot: Toon sent an attack less than 3 damage!')
            return

        # Stun logic
        if bossDamage == 3:
            if random.random() <= min(BossCogGlobals.BossbotMaxStunChance, self.speedDamage / self.maxSpeedDamage):
                self.b_setAttackCode(BossCogGlobals.BossCogDizzyNow)

                self.toonStunsDict.setdefault(avId, 0)
                self.toonStunsDict[avId] += 1

                # Remove speed damage upon being stunned.
                self.recoverSpeedDamage(BossCogGlobals.BossbotStunSpeedRecover)

                self.numStuns += 1
                if av:
                    mult = av.getDeptExpMult(ToontownGlobals.DEPARTMENT_BOSSBOT)
                    self.addDepartmentExp(av, math.ceil(10 + (650 * mult / (self.numStuns + 10))))

                for toonId in self.involvedToons:
                    toon = self.air.doId2do.get(toonId)
                    if toon:
                        mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_BOSSBOT)
                        self.addDepartmentExp(toon, math.ceil(10 + (975 * mult / (self.numStuns + 10))))
                        # CEO is Stunned Tip
                        toon.showToonTip(TTE.TIP_CEO_STUNNED)
                self.d_updateStunCount(avId)

        # Double damage if the CEO is currently stunned
        if self.attackCode == BossCogGlobals.BossCogDizzyNow:
            bossDamage *= 2

        bossDamage *= 6
        self.d_updateDamageDealt(avId, bossDamage)

        if avId in self.toonDamagesDict:
            self.toonDamagesDict[avId] += bossDamage
        else:
            self.toonDamagesDict[avId] = bossDamage

        toon = self.air.doId2do.get(avId)
        if toon:
            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_BOSSBOT)
            self.addDepartmentExp(toon, math.ceil(bossDamage * 5 * mult))

        bossDamage = min(self.getBossDamage() + bossDamage, self.bossMaxDamage)
        self.b_setBossDamage(bossDamage, 0, 0)
        if self.bossDamage >= self.bossMaxDamage:
            self.b_setState('Victory')
        else:
            self.__recordHit(bossDamage)

    def __recordHit(self, bossDamage):
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

    def d_updateDamageDealt(self, avId, damageDealt):
        self.sendUpdate('updateDamageDealt', [avId, damageDealt])

    def d_updateSpeedDamageDealt(self, avId, speedDamageDealt):
        self.sendUpdate('updateSpeedDamageDealt', [avId, speedDamageDealt])

    def d_updateStunCount(self, avId):
        self.sendUpdate('updateStunCount', [avId])

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
        if speedDamage > self.maxSpeedDamage:
            speedDamage = self.maxSpeedDamage
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
        # av = self.air.doId2do.get(avId)
        if not self.validate(avId, avId in self.involvedToons, 'hitBoss from unknown avatar'):
            return
        if not 2 <= speedDamage <= 6:
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BattleFour':
            return
        self.d_updateSpeedDamageDealt(avId, speedDamage)
        if avId in self.toonSpeedDamagesDict:
            self.toonSpeedDamagesDict[avId] += speedDamage
        else:
            self.toonSpeedDamagesDict[avId] = speedDamage
        
        self.toonGolfBallsDict.setdefault(avId, 0)
        self.toonGolfBallsDict[avId] += 1

        toon = self.air.doId2do.get(avId)
        if toon:
            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_BOSSBOT)
            self.addDepartmentExp(toon, math.ceil(speedDamage * 16 * mult))

        now = globalClock.getFrameTime()
        newDamage = self.getSpeedDamage() + speedDamage
        self.notify.debug('newDamage = %s' % newDamage)
        speedDamage = min(self.getFloatSpeedDamage() + speedDamage, self.maxSpeedDamage)
        self.speedRecoverRate = int(max(
            BossCogGlobals.BossbotSpeedRecoverRate * (1 - (speedDamage / self.maxSpeedDamage), 1)))
        self.b_setSpeedDamage(speedDamage, self.speedRecoverRate, now)
        self.__recordHit(speedDamage)

    def addDepartmentExp(self, toon, exp):
        toon.addDepartmentExp(exp, ToontownGlobals.DEPARTMENT_BOSSBOT)

    def startDecaySpeedDamage(self) -> None:
        delay = max(5 - (self.bossDamage // 250), 1)
        taskMgr.doMethodLater(delay, self.decaySpeedDamage, self.decaySpeedDamageTask)

    def stopDecaySpeedDamage(self) -> None:
        taskMgr.remove(self.decaySpeedDamageTask)

    def decaySpeedDamage(self, task) -> None:
        self.recoverSpeedDamage(1)
        self.startDecaySpeedDamage()

    def recoverSpeedDamage(self, recoverDamage: int) -> None:
        now = globalClock.getFrameTime()
        newDamage = self.getSpeedDamage() - recoverDamage
        self.notify.debug('newDamage = %s' % newDamage)
        speedDamage = min(self.getFloatSpeedDamage() - recoverDamage, self.maxSpeedDamage)
        if speedDamage < 0:
            speedDamage = 0
        self.speedRecoverRate = int(max(
            BossCogGlobals.BossbotSpeedRecoverRate * (1 - (speedDamage / self.maxSpeedDamage), 1)))
        self.b_setSpeedDamage(speedDamage, self.speedRecoverRate, now)
        if self.speedDamage > self.maxSpeedDamage:
            self.speedDamage = self.maxSpeedDamage

    def enterVictory(self):
        self.resetBattles()
        for table in self.tables:
            table.turnOff()

        for golfSpot in self.golfSpots:
            golfSpot.turnOff()

        for belt in self.foodBelts:
            belt.turnOff()

        self.suitsKilled.append({'type': 'ceo',
         'level': None,
         'track': self.dna.dept,
         'isSkelecog': 0,
         'isForeman': 0,
         'isBoss': 1,
         'isSupervisor': 0,
         'isVirtual': 0,
         'hasRevives': 0,
         'isElite': 0,
         'activeToons': self.involvedToons[:]})
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 30, self.__doneVictory)
        return

    def __doneVictory(self, avIds):
        self.notify.info("LogStats BossbotBossWasDefeated")
        for toonId in self.involvedToons:
            self.notify.info("LogStats ToonDefeatedBossbotBoss toonid %s" % toonId)
            toon = self.air.doId2do.get(toonId)
            if toon:

                # Add dept exp bonus for winning the boss
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_BOSSBOT)
                toon.addDepartmentExp(1000 * mult, ToontownGlobals.DEPARTMENT_BOSSBOT)

                self.givePinkSlipReward(toon, toonId)
                toon.b_promote(self.deptIndex)
                if toon.cogTypes[self.deptIndex] == 7 and toon.cogLevels[self.deptIndex] >= 7:
                    toon.getHammerspace().addItem(BackgroundItemType.HQ_Bossbot)
                # Promotion + Reward Tips
                toon.showToonTip(TTE.TIP_DISGUISE_PROMOTION)
                toon.showToonTip(TTE.TIP_REWARDS_PINK_SKIP)
                # Unite tip
                toon.showToonTip(TTE.TIP_REWARDS_UNITE)

                # Handle toon unite rewards
                self.handleUniteRewards(toon)

            if self.begunToonAmount == 1:
                self.notify.info("LogStats ToonSoloDefeatedBossbotBoss toonid %s" % toonId)
            self.air.achievementsManager.ceo(toonId, numPlayers=self.begunToonAmount)

            # Handle boss specific quests
            simbase.air.quest3Manager.progressObjective(
                toon, 
                BossbotBossContext(
                    "c",
                    self.toonStunsDict.get(toonId, 0),
                    self.toonDamagesDict.get(toonId, 0),
                    self.toonDinersFedDict.get(toonId, 0),
                    self.toonExeDinersFedDict.get(toonId, 0),
                    self.toonGolfBallsDict.get(toonId, 0),
                )
            )
        
        self.prepareReward()
        self.rewardClubCoins()

    def givePinkSlipReward(self, toon, toonId):
        bonusSlips = 0
        departmentLevel = toon.getDepartmentLevel(ToontownGlobals.DEPARTMENT_BOSSBOT)
        if departmentLevel == ToontownGlobals.MaxDepartmentLevel[ToontownGlobals.DEPARTMENT_BOSSBOT]:
            bonusSlips += 2
        bonusSlips = toon.applyBoosters([BoosterItemType.Reward_Boss_Global, BoosterItemType.Reward_Boss_Bossbot], bonusSlips)
        slipsAmt = 9
        # toon.queueScavenge(slipsAmt + bonusSlips, ScavengeType.Fires, [])
        toon.getHammerspace().addItem(MaterialItemType.PinkSlips, slipsAmt + bonusSlips)
        self.d_setNumPinkSlipsEarned(toonId, slipsAmt + bonusSlips)

    def d_setNumPinkSlipsEarned(self, toonId, slips):
        self.sendUpdateToAvatarId(toonId, "setNumPinkSlipsEarned", [slips])

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

    def setDesperationState(self, desperationState: int) -> None:
        if self.desperationState < desperationState:
            self.desperationState = desperationState

            # Remove speed damage upon reorg/downsize.
            self.recoverSpeedDamage(BossCogGlobals.BossbotDesperationSpeedRecover)

    def doNextAttack(self, task):
        attackCode = -1
        optionalParam = 0

        if self.attackCode == BossCogGlobals.BossCogDizzyNow:
            attackCode = BossCogGlobals.BossCogGolfAreaAttack

        if self.movingToTable:
            self.waitForNextAttack(5)
        elif self.bossDamage >= self.bossMaxDamage * 0.5 and self.desperationState < 0:
            attackCode = BossCogGlobals.BossCogOvertimeAttack
            self.setDesperationState(0)
            optionalParam = self.desperationState
        elif self.bossDamage >= self.bossMaxDamage * 0.75 and self.desperationState < 1:
            attackCode = BossCogGlobals.BossCogOvertimeAttack
            self.setDesperationState(1)
            optionalParam = self.desperationState
        else:
            if self.golfAreaAttacks < 2:
                attackChoices = [BossCogGlobals.BossCogGolfAreaAttack,
                                 BossCogGlobals.BossCogDirectedAttack]
                attackCode = random.choices(attackChoices, weights=[1, 4])[0]
            else:
                attackCode = BossCogGlobals.BossCogDirectedAttack

        if attackCode != BossCogGlobals.BossCogGolfAreaAttack:
            # Reset the amount of golf area attacks in succession.
            self.golfAreaAttacks = 0

        if attackCode == BossCogGlobals.BossCogAreaAttack:
            self.__doAreaAttack()
        if attackCode == BossCogGlobals.BossCogGolfAreaAttack:
            self.__doGolfAreaAttack()
        elif attackCode == BossCogGlobals.BossCogDirectedAttack:
            self.__doDirectedAttack()
        elif attackCode >= 0:
            self.b_setAttackCode(attackCode, optionalParam)

    def b_setAttackCode(self, attackCode, avId=0):
        if attackCode == BossCogGlobals.BossCogDizzyNow:
            if self.movingToTable:
                self.b_stopMove()

        DistributedBossCogAI.b_setAttackCode(self, attackCode, avId)

    def __doDirectedAttack(self):
        toonId = self.getMaxThreatToon()
        self.notify.debug('toonToAttack=%s' % toonId)

        unflattenedToons = self.getUnflattenedToons()

        attackTotallyRandomToon = random.random() < 0.1
        if unflattenedToons and (attackTotallyRandomToon or toonId == 0):
            toonId = random.choice(unflattenedToons)

        if toonId == 0 or (not self.tableToons and random.random() <= 0.5):
            uprightTables = self.getUprightTables()
            if uprightTables:
                tableToMoveTo = random.choice(uprightTables)
                self.doMoveAttack(tableToMoveTo)
            else:
                self.waitForNextAttack(4)
            return

        self.targetedToon = toonId

        toonThreat = self.getThreat(toonId)
        toonThreat *= 0.25
        threatToSubtract = max(toonThreat, 10)
        self.subtractThreat(toonId, threatToSubtract)

        if self.isToonOnTable(toonId):
            doesMoveAttack = ConfigVariableBool('ceo-does-move-attack', True).getValue()
            if doesMoveAttack:
                chanceToShoot = 0.25
            else:
                chanceToShoot = 1.0
            if not self.moveAttackAllowed:
                self.notify.debug('moveAttack is not allowed, doing gearDirectedAttack')
                chanceToShoot = 1.0
            if random.random() < chanceToShoot:
                self.b_setAttackCode(BossCogGlobals.BossCogGearDirectedAttack, toonId)
                self.numGearAttacks += 1
            else:
                tableIndex = self.getToonTableIndex(toonId)
                self.doMoveAttack(tableIndex)
        else:
            self.b_setAttackCode(BossCogGlobals.BossCogGolfAttack, toonId)
            self.numGolfAttacks += 1

    def doMoveAttack(self, tableIndex):
        if self.attackCode == BossCogGlobals.BossCogDizzyNow:
            self.b_setAttackCode(BossCogGlobals.BossCogRecoverDizzyAttack)

        self.numMoveAttacks += 1
        self.movingToTable = True
        self.tableDest = tableIndex
        self.b_setAttackCode(BossCogGlobals.BossCogMoveAttack, tableIndex)

        table = self.tables[tableIndex]
        curr_pos = self.getPos()
        table_pos = table.getPos()

        foo = NodePath('foo')
        foo.setPos(self.getPos())
        foo.setHpr(self.getHpr())
        foo.lookAt(table_pos)

        to_hpr = foo.getHpr()

        foo.removeNode()

        curr_h = self.getH()

        table_h = reduceAngle(to_hpr.getX() - 180)
        table_h = fitDestAngle2Src(curr_h, table_h)

        turn_speed = self.currentTurnSpeed
        roll_speed = self.currentRollSpeed

        distance = Vec3(table_pos - curr_pos).length()

        turn_time = abs(table_h - curr_h) / turn_speed
        roll_time = distance / roll_speed

        self.departureTime = globalClock.getFrameTime()
        self.arrivalTime = self.departureTime + turn_time + roll_time

        self.moveTrack = Sequence(
            self.hprInterval(turn_time, VBase3(table_h, 0, 0), self.getHpr()),
            self.posInterval(roll_time, table_pos, curr_pos),
            Func(self.reachedTable, self.tableDest)
        )
        self.moveTrack.start()

        self.sendUpdate("doMoveAttack", [self.tableDest, table_pos[0], table_pos[1],
                        globalClockDelta.localToNetworkTime(self.arrivalTime)])

    def b_stopMove(self) -> None:
        self.d_stopMove()
        self.stopMove()

    def d_stopMove(self) -> None:
        self.sendUpdate("stopMove")
        self.d_setPos(*self.getPos())

    def stopMove(self) -> None:
        if not self.movingToTable:
            return
        if self.moveTrack:
            self.moveTrack.pause()
            self.moveTrack = None
        self.movingToTable = False

    @property
    def currentTurnSpeed(self) -> float:
        min_speed = BossCogGlobals.BossbotTurnSpeedMin
        max_speed = BossCogGlobals.BossbotTurnSpeedMax * self.tierSpeedMult
        result = (max_speed - (max_speed - min_speed) * self.fractionalSpeedDamage) * self.overtimeSpeedMult
        return result

    @property
    def currentRollSpeed(self) -> float:
        min_speed = BossCogGlobals.BossbotRollSpeedMin
        max_speed = BossCogGlobals.BossbotRollSpeedMax * self.tierSpeedMult
        result = (max_speed - (max_speed - min_speed) * self.fractionalSpeedDamage) * self.overtimeSpeedMult
        return result

    @property
    def fractionalSpeedDamage(self) -> float:
        result = self.getSpeedDamage() / self.maxSpeedDamage
        return result

    @property
    def overtimeSpeedMult(self) -> float:
        if self.desperationState == 1:
            return 1.5
        elif self.desperationState == 0:
            return 1.2
        return 1.0

    @property
    def tierSpeedMult(self) -> float:
        return 1.0

    @property
    def tableToons(self):
        return [table.avId for table in self.tables if table.avId]

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

    def calcAndSetBattleDifficulty(self):
        self.getToonDifficulty()
        self.b_setMaxHp(BossCogGlobals.BossbotBossMaxDamage[1])
        self.universalUnites = 4

    def b_setMaxHp(self, hp):
        self.setMaxHp(hp)
        self.d_setMaxHp(hp)

    def setMaxHp(self, hp):
        self.bossMaxDamage = hp

    def d_setMaxHp(self, hp):
        self.sendUpdate('setMaxHp', [hp])

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

    def closeEnter(self, colEntry):
        tableStr = colEntry.getIntoNodePath().getNetTag('tableIndex')
        if tableStr:
            tableIndex = int(tableStr)
            self.hitTable(tableIndex)

    def closeExit(self, colEntry):
        tableStr = colEntry.getIntoNodePath().getNetTag('tableIndex')
        if tableStr:
            tableIndex = int(tableStr)
            if self.tableDest != tableIndex:
                self.awayFromTable(tableIndex)

    def reachedTable(self, tableIndex) -> None:
        if self.movingToTable and self.tableDest == tableIndex:
            self.stopMove()
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
        """This function is called whenever a diner is killed.
        """
        self.numDinersExploded += 1
        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_BOSSBOT)
                self.addDepartmentExp(toon, math.ceil(20 * mult))

        # If there are no diners remaining, there's no real point in
        # just waiting, so let's end the round.
        if not any([table.aliveSuits for table in self.tables]):
            self.__doneBattleTwo(self.involvedToons)

    def magicWordHit(self, damage, avId):
        self.hitBoss(damage)

    def __doAreaAttack(self):
        self.b_setAttackCode(BossCogGlobals.BossCogAreaAttack)

    def __doGolfAreaAttack(self):
        self.numGolfAreaAttacks += 1

        # Unlike the one above, this one keeps track
        # of the amount of golf area attacks
        # used in succession.
        self.golfAreaAttacks += 1

        self.b_setAttackCode(BossCogGlobals.BossCogGolfAreaAttack)

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

    def zapToon(self, x, y, z, h, p, r, bpx, bpy, attackCode, timestamp):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'zapToon from unknown avatar'):
            return
        toon = simbase.air.doId2do.get(avId)
        if not toon:
            return

        self.d_showZapToon(avId, x, y, z, h, p, r, attackCode, timestamp)
        damage = BossCogGlobals.BossCogDamageLevels.get(attackCode)

        if damage is None:
            self.notify.warning('No damage listed for attack code %s' % attackCode)
            damage = 5

        damage *= self.getDamageMultiplier()

        # If this toon isn't the one the CEO is targeting, have it deal 25% damage.
        if avId != self.targetedToon and attackCode in (BossCogGlobals.BossCogGolfAttack,
                                                        BossCogGlobals.BossCogGearDirectedAttack):
            damage *= 0.25

        damage = math.floor(damage)
        self.damageToon(toon, damage)
        currState = self.getCurrentOrNextState()
        if attackCode == BossCogGlobals.BossCogElectricFence and (currState in ('RollToBattleTwo', 'BattleThree')):
            if self.attackCode in (BossCogGlobals.BossCogAreaAttack, BossCogGlobals.BossCogDizzyNow):
                return
            if bpy < 0 and abs(bpx / bpy) > 0.5:
                if bpx < 0:
                    self.b_setAttackCode(BossCogGlobals.BossCogSwatRight)
                else:
                    self.b_setAttackCode(BossCogGlobals.BossCogSwatLeft)

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
                self.b_stopMove()
                self.waitForNextAttack(0)

    def getBattleFourTime(self):
        if self.state != 'BattleFour':
            t1 = 0
        else:
            elapsed = globalClock.getFrameTime() - self.battleFourStart
            t1 = elapsed / float(self.battleFourDuration)
        return t1

    def getDamageMultiplier(self):
        mult = 1.6
        if self.desperationState == 1:
            mult *= 2
        elif self.desperationState == 0:
            mult *= 1.25
        return mult

    def toggleMove(self):
        self.moveAttackAllowed = not self.moveAttackAllowed
        return self.moveAttackAllowed

    def startTraverse(self) -> None:
        self.accept(self.uniqueName("closeEnter"), self.closeEnter)
        self.accept(self.uniqueName("closeExit"), self.closeExit)
        taskMgr.add(self._traverseTask, self.traverseTask)

    def stopTraverse(self) -> None:
        taskMgr.remove(self.traverseTask)
        self.ignore(self.uniqueName("closeEnter"))
        self.ignore(self.uniqueName("closeExit"))

    def _traverseTask(self, task) -> None:
        # run the collision traversal if we have a
        # CollisionTraverser set.
        if self.cTrav:
            self.cTrav.traverse(self.scene)
        return task.cont

    def deleteTraverser(self) -> None:
        if self.cTrav:
            self.cTrav.removeCollider(self.closeBubbleNodePath)
            self.cTrav = None
    
    def killDiners(self) -> None:
        """Kills every diner from every table."""
        for table in self.tables:
            table.killDiners()

    @property
    def shouldShowSurrenderDialogue(self):
        if self.getCurrentOrNextState() == 'BattleOne':
            return False

        return True
