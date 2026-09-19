import json
import random

from direct.showbase.PythonUtil import lerp

from toontown.suit import BossCogGlobals
from toontown.battle.BattleGlobals import BattleOrderPriority
from toontown.battle.distributed import DistributedBattleLitigatorsAI
from toontown.coghq.lawbothq import DistributedHardmodeLawbotCannonAI
from toontown.inventory.enums.ItemEnums import BackgroundItemType, BoosterItemType, MaterialItemType
from toontown.suit import (DistributedHardmodeLawbotBossSuitAI,
                           DistributedHardmodeLawbotBossSuitAttackAI,
                           DistributedSuitAI)
from toontown.suit.DistributedLawbotBossAI import *
from toontown.toon.npc.NPCToonClassesAI import DistributedNPCLaurenAI
from toontown.toon.gui.ToonTipGlobals import TTE

tornadoAttacks = [BossCogGlobals.BossCogSpiralTornadoAreaAttack,
                  BossCogGlobals.BossCogEightWayTornadoAreaAttack,
                  BossCogGlobals.BossCogFourWayTornadoAreaAttack]


@DirectNotifyCategory()
class DistributedHardmodeLawbotBossAI(DistributedLawbotBossAI):
    groupType = GroupType.OCLO
    WANT_TOONO = True

    def __init__(self, air):
        DistributedLawbotBossAI.__init__(self, air)
        FSM.FSM.__init__(self, 'DistributedHardmodeLawbotBossAI')
        self.litigationOrder = ['stenog', 'sgoat', 'lgator', 'caseman']
        # Keep track of summoned cogs separately in litigation team round.
        # We don't want the litigator spawning cogs and them going to the other side.
        self.reserveSuitsA = []
        self.reserveSuitsB = []
        self.laurenNPC = None
        self.forcedAttackCode = None
        self.attackCogsSpawned = 0
        self.onExecutiveSpawnCooldown = False
        self.lastTornadoType = None
        self.tornadoesSinceOtherAttacks = 0
        self.randomGen = random.Random()

    def getContentSync(self) -> Optional[ContentSyncType]:
        return ContentSyncType.OCLO

    def d_createBossTrapMovie(self):
        if self.attackCode != BossCogGlobals.BossCogDizzyNow:
            return
        trap = self.traps[self.trapIndex]
        # Once again, ensure skelecogs fly away from the trap if they are targeting it
        # while the CLO falls through it.
        if trap.getSuitId():
            suit = simbase.air.doId2do.get(trap.suitId)
            if suit:
                suit.bossNear(self.trapIndex)
        # Inform both the trap itself and Bumpy that the CLO is falling through this trap.
        if trap.getStatus() != 1:
            if trap.getStatus() == -1:
                trap.startLandBroken()
                self.bumpyNPC.bossLandBroken()
            self.b_setAttackCode(BossCogGlobals.BossCogRecoverDizzyAttack)
            return
        trap.setDuringActivation(1)
        # Lauren should stop trying to prestige the trap if the CLO is falling through it.
        if trap is self.laurenNPC.trap:
            self.laurenNPC.bossLand()
        trap.startActivate()
        avIdDict = {}
        # Create a percentage of knockback dealt for each toon that dealt some.
        if self.toonsSoundDamageDealt:
            totalKnockBackDealt = sum(self.toonsSoundDamageDealt.values())
            for avId, knockBackDealt in self.toonsSoundDamageDealt.items():
                avIdDict[avId] = knockBackDealt / totalKnockBackDealt
        else:
            # If no toons dealt damage (she was already in damage position when she was stunned),
            # Then evenly split the credit amongst all toons.
            knockBackDealt = 1.0 / len(self.involvedToons)
            for avId in self.involvedToons:
                avIdDict[avId] = knockBackDealt

        # Get trap damage to check if CLO will die
        if trap.getPrestiged():
            # 135 if quicksand, 210 if trapdoor.
            trapDamage = BossCogGlobals.LawbotBossPrestigedTrapsDamage[trap.trapLevel]
        else:
            # 90 if quicksand, 140 if trapdoor.
            trapDamage = BossCogGlobals.LawbotBossTrapsDamage[trap.trapLevel]

        # Don't do forced area attack or spawn defense cogs if trap will kill
        healthLeft = self.bossMaxDamage - self.bossDamage - trapDamage
        if self.checkIfTrapKills(healthLeft):
            self.sendUpdate("setRandomFallPosition", [0, 220, 0])
            self.sendUpdate("createBossTrapMovie", [self.trapIndex, False, False])
            self.laurenNPC.d_sayAdvice()
        else:
            # Conditional for making defense specialists, also doesn't spawn if this trap would kill CLO
            self.setRandomFallPosHpr()
            self.makeDefenseSpecialists(healthLeft, trapDamage, self.shouldSpawnEmpoweredDefense(healthLeft))
            self.sendUpdate("createBossTrapMovie", [self.trapIndex, True, True])
        taskMgr.doMethodLater(3.5, self.trapHitBoss, self.uniqueName('trapHitBossDelay'), extraArgs=[avIdDict])

    def getPrestigedBossTraps(self):
        # Return all prestiged, active boss traps.
        if self.traps is not None:
            return [trap for trap in self.traps if trap.getPrestiged() and trap.getStatus() == 1]
        else:
            return []

    def setAttackCode(self, attackCode, avId = 0):
        self.attackCode = attackCode
        self.chatOnAttack(attackCode, avId)
        self.attackAvId = avId
        if attackCode == BossCogGlobals.BossCogDizzyNow:
            # If the CLO is dizzy, we want a variable stun time from 16 seconds to 10 seconds.
            delayTime = self.progressValue(16, 10)
        else:
            delayTime = BossCogGlobals.BossCogAttackTimes.get(attackCode)
            if attackCode == BossCogGlobals.BossCogFrontAttack:
                delayTime += 0.8
            if delayTime is None:
                return
        if attackCode == BossCogGlobals.BossCogRecoverDizzyAttack:
            # If she stops being stunned, clear out some values relevant to the stunned state.
            self.toonsSoundDamageDealt = {}
            self.stunnedHits = 0
            self.maxStunnedHits = 0
            self.trapIndex = -1
            # Next attack will be a tornaga.
            self.forcedAttackCode = BossCogGlobals.BossCogFourWayTornadoAreaAttack
        elif attackCode in tornadoAttacks:
            self.tornadoesSinceOtherAttacks += 1
        else:
            self.tornadoesSinceOtherAttacks = 0
        self.waitForNextAttack(delayTime)

    def doNextAttack(self, task):
        if self.movingToToon:
            self.waitForNextAttack(3)
            return
        self.b_stopMoveTask()
        if self.attackCode == BossCogGlobals.BossCogDizzyNow:
            attackCode = BossCogGlobals.BossCogRecoverDizzyAttack
        elif self.forcedAttackCode is not None:
            attackCode = self.forcedAttackCode
            self.forcedAttackCode = None
        else:
            attackChoices = [
                BossCogGlobals.BossCogAreaAttack,
                BossCogGlobals.BossCogSpreadBookDirectedAttack,
                BossCogGlobals.BossCogFrontAttack,
                BossCogGlobals.BossCogFourWayTornadoAreaAttack
            ]
            # Area attack (chance to be tornado): 1/8
            # Spread book: 4/8
            # Front paper attack: 1/8
            # Tornado attack: 2/8
            attackCode = self.randomGen.choices(attackChoices, weights=[1, 4, 1, 2])[0]
            # Some forced attack code to ensure no spamming of the same attacks
            if attackCode == BossCogGlobals.BossCogFrontAttack:
                self.forcedAttackCode = BossCogGlobals.BossCogSpreadBookDirectedAttack
        if attackCode == BossCogGlobals.BossCogAreaAttack:
            self.__decideAreaAttack()
        elif attackCode == BossCogGlobals.BossCogSpreadBookDirectedAttack:
            self.__doDirectedAttack()
        elif attackCode == BossCogGlobals.BossCogFourWayTornadoAreaAttack:
            self.doTornadoAreaAttack()
        else:
            self.b_setAttackCode(attackCode)

    def __decideAreaAttack(self):
        # If criteria is met, do a tornado area attack instead of a normal jump area attack.
        if self.randomGen.randint(3, 10) > self.progressValue(9, 4):
            self.doTornadoAreaAttack()
        else:
            self.doAreaAttack()

    def doTornadoAreaAttack(self):
        # Choose a random tornaga for now.
        tornadoList = tornadoAttacks[:]
        # Make sure not to do the last tornado type we did.
        if self.lastTornadoType is not None and self.lastTornadoType in tornadoList:
            tornadoList.remove(self.lastTornadoType)
        attackCode = self.randomGen.choice(tornadoList)
        self.b_setAttackCode(attackCode)
        self.lastTornadoType = attackCode
        # Don't do 2 tornadoes in a row, do a book instead.
        if self.tornadoesSinceOtherAttacks >= 2:
            self.forcedAttackCode = BossCogGlobals.BossCogSpreadBookDirectedAttack

    def doAreaAttack(self):
        self.b_setAttackCode(BossCogGlobals.BossCogAreaAttack)

    def __doDirectedAttack(self):
        if self.nearToons:
            toonId = self.randomGen.choice(self.nearToons)
            # 70% chance, never move towards the same toon 2x in a row
            if self.randomGen.random() >= 0.3 and self.currToon != toonId:
                self.currToon = toonId
                self.doMoveAttack(toonId)
            else:
                # Reset current toon value
                self.currToon = -1
                self.b_setAttackCode(BossCogGlobals.BossCogSpreadBookDirectedAttack, toonId)
        else:
            # 40% chance to do move attack, 60% chance to do one of 2 area attacks.
            if self.randomGen.random() >= 0.6 and len(self.involvedToons) > 0:
                self.doMoveAttack(self.randomGen.choice(self.involvedToons))
            else:
                self.__decideAreaAttack()

    def doMoveAttack(self, toonId):
        toon = self.air.doId2do.get(toonId)
        if toon:
            currPos = self.getPos()
            currH = self.getH()

            # Set up a placeholder node used to determine HPR and distances.
            foo = NodePath("foo")
            foo.setPos(currPos)
            foo.setHpr(self.getHpr())

            toPos = LPoint3f(toon.getX(), toon.getY(), -71.601)

            # If the toon targeted is outside of the CLO's move bounds, go to the "home" position (middle of room)
            if not (-105 <= toPos[0] <= 110 and 120 <= toPos[1] <= 320):
                toPos = LPoint3f(0, 220, -71.601)

            foo.lookAt(toPos)

            toHpr = foo.getHpr()
            toHpr.setX(toHpr.getX() - 180)
            foo.removeNode()

            # If the CLO is trying to move to a position she is already at, do an area attack instead.
            if toPos == currPos:
                self.__decideAreaAttack()
                return

            self.numMoveAttacks += 1
            self.movingToToon = True
            self.toonDest = toonId

            # Figure out the H rotation required.
            trapH = round(PythonUtil.fitDestAngle2Src(currH, toHpr[0]))

            # Figure out some speed values required for her movement.
            turnSpeed = self.getCurTurnSpeed()
            rollSpeed = self.getCurRollSpeed()

            distance = Vec3(toPos - currPos).length()
            rollTime = distance / rollSpeed

            turnTime = abs(trapH - currH) / turnSpeed

            # Create a serverside version of the movement movie for timing purposes.
            self.moveTrack = Sequence(
                self.hprInterval(turnTime, VBase3(trapH, 0, 0), self.getHpr()),
                self.posInterval(rollTime, toPos, currPos),
                Func(self.reachToon, toonId)
            )
            self.moveTrack.start()

            self.setAttackCode(BossCogGlobals.BossCogMoveAttack, toonId)
            self.sendUpdate("doMoveAttack", [toonId, turnTime, rollTime, toPos[0], toPos[1], trapH])
        else:
            self.b_setAttackCode(BossCogGlobals.BossCogNoAttack)

    def setBossDamage(self, bossDamage):
        self.bossDamage = bossDamage
        # If the CLO reaches certain health thresholds, change her desperation state and increase spotlight values.
        if self.bossDamage >= self.bossMaxDamage * 0.75:
            self.desperationState = 1
            self.setSpotlightVelocityAccel(BossCogGlobals.LawbotBossSpotlightVelocity[1], BossCogGlobals.LawbotBossSpotlightAccel[1])
        elif self.bossDamage >= self.bossMaxDamage * 0.5:
            self.desperationState = 0
            self.setSpotlightVelocityAccel(BossCogGlobals.LawbotBossSpotlightVelocity[2], BossCogGlobals.LawbotBossSpotlightAccel[2])
        else:
            self.desperationState = -1

    def formatReward(self):
        return str(self.numSues) + ' c&ds'

    def makeBattleOneBattles(self):
        self.postBattleState = 'PrepareBattleTwo'
        self.initializeBattles(1, BossCogGlobals.LawbotBossBattleBackFromTablePosHpr)

    def generateSuits(self, battleNumber):
        if battleNumber == 1:
            return self.invokeSuitPlanner(self.battleOnePlanner, 1, virtual=True)
        else:
            return self.invokeSuitPlannerBosses()

    def resetBattles(self):
        sendReset = 0
        if self.battleA:
            self.battleA.requestDelete()
            del self.battleA
            self.battleA = None
            self.battleAId = 0
            sendReset = 1
        if self.battleB:
            self.battleB.requestDelete()
            del self.battleB
            self.battleB = None
            self.battleBId = 0
            sendReset = 1
        for suit in self.suitsA + self.suitsB:
            suit.requestDelete()

        for suit, joinChance in self.reserveSuits + self.reserveSuitsA + self.reserveSuitsB:
            suit.requestDelete()

        self.suitsA = []
        self.activeSuitsA = []
        self.suitsB = []
        self.activeSuitsB = []
        self.reserveSuits = []
        self.reserveSuitsA = []
        self.reserveSuitsB = []
        self.battleNumber = 0
        if sendReset:
            self.sendBattleIds()

    def invokeSuitPlannerBosses(self):
        activeSuitsA = []
        activeSuitsB = []
        activeSuitsA.append(self.genBossSuit(self.litigationOrder[0], BattleOrderPriority.BEGINNING))
        activeSuitsA.append(self.genBossSuit(self.litigationOrder[1], BattleOrderPriority.END))
        activeSuitsB.append(self.genBossSuit(self.litigationOrder[2], BattleOrderPriority.BEGINNING))
        activeSuitsB.append(self.genBossSuit(self.litigationOrder[3], BattleOrderPriority.END))
        reserveSuits = []
        reserveSuitsA = []
        reserveSuitsB = []

        retval = {'activeSuitsA': activeSuitsA,
                  'activeSuitsB': activeSuitsB,
                  'reserveSuits': reserveSuits,
                  'reserveSuitsA': reserveSuitsA,
                  'reserveSuitsB': reserveSuitsB}

        return retval

    def genBossSuit(self, suitName, battlePriority):
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, None)
        dna = SuitDNA.SuitDNA()
        dna.newSuit(suitName)
        newSuit.dna = dna
        suitLevels = BossCogGlobals.HardmodeLawbotBossLitigationLevels
        newSuit.setLevel(suitLevels[suitName])
        newSuit.setElite(1)
        newSuit.generateWithRequired(self.zoneId)
        newSuit.setBattleOrderPriority(battlePriority)
        newSuit.node().setName('suit-%s' % newSuit.doId)
        return newSuit

    def initializeBattles(self, battleNumber, bossCogPosHpr):
        self.resetBattles()
        if not self.involvedToons:
            self.notify.warning('initializeBattles: no toons!')
            return
        self.battleNumber = battleNumber
        if battleNumber == 1:
            suitHandles = self.generateSuits(battleNumber)
            self.suitsA = suitHandles['activeSuits']
            self.activeSuitsA = self.suitsA[:]
            self.reserveSuits = suitHandles['reserveSuits']
            suitHandles = self.generateSuits(battleNumber)
            self.suitsB = suitHandles['activeSuits']
            self.activeSuitsB = self.suitsB[:]
            self.reserveSuits += suitHandles['reserveSuits']
        else:
            suitHandles = self.generateSuits(battleNumber)
            self.suitsA = suitHandles['activeSuitsA']
            self.activeSuitsA = self.suitsA[:]
            self.reserveSuits = suitHandles['reserveSuits']
            suitHandles = self.generateSuits(battleNumber)
            self.suitsB = suitHandles['activeSuitsB']
            self.activeSuitsB = self.suitsB[:]
            self.reserveSuits += suitHandles['reserveSuits']
        if self.toonsA:
            if battleNumber == 1:
                self.battleA = self.makeBattle(BossCogGlobals.LawbotBossBattleTablePosHpr,
                                               BossCogGlobals.HardmodeLawyerVirtualBattleAPosHpr, self.handleRoundADone, self.handleBattleADone, battleNumber, 0)
            else:
                self.battleA = self.makeBattle(bossCogPosHpr, BossCogGlobals.LawyerBattleAPosHpr, self.handleBossRoundADone, self.handleBattleADone, battleNumber, 0)
            self.battleAId = self.battleA.doId
        else:
            self.moveSuits(self.activeSuitsA)
            self.suitsA = []
            self.activeSuitsA = []
            if self.arenaSide is None:
                self.b_setArenaSide(0)
        if self.toonsB:
            if battleNumber == 1:
                self.battleB = self.makeBattle(BossCogGlobals.LawbotBossBattleTablePosHpr,
                                               BossCogGlobals.HardmodeLawyerVirtualBattleBPosHpr, self.handleRoundBDone, self.handleBattleBDone, battleNumber, 1)
            else:
                self.battleB = self.makeBattle(bossCogPosHpr, BossCogGlobals.LawyerBattleBPosHpr, self.handleBossRoundBDone, self.handleBattleBDone, battleNumber, 1)
            self.battleBId = self.battleB.doId
        else:
            self.moveSuits(self.activeSuitsB)
            self.suitsB = []
            self.activeSuitsB = []
            if self.arenaSide is None:
                self.b_setArenaSide(1)
        self.sendBattleIds()

    # The following three functions are used to ensure that there are only 2 minibosses present at a time
    # in any battle. This is especially prevalent for instances where there is only one battle, instead of 2.
    def handleBossRoundADone(self, toonIds, totalHp, deadSuits):
        if self.battleA:
            self.handleBossRoundDone(self.battleA, self.suitsA, self.activeSuitsA, toonIds, totalHp, deadSuits)

    def handleBossRoundBDone(self, toonIds, totalHp, deadSuits):
        if self.battleB:
            self.handleBossRoundDone(self.battleB, self.suitsB, self.activeSuitsB, toonIds, totalHp, deadSuits)

    def handleBossRoundDone(self, battle, suits, activeSuits, toonIds, totalHp, deadSuits):
        totalMaxHp = 0
        for suit in suits:
            totalMaxHp += suit.getMaxHp()

        for suit in deadSuits:
            if suit in activeSuits:
                activeSuits.remove(suit)

        minibossList = []

        def getMinibossList():
            return [suit for suit in activeSuits if suit.isMiniboss()]

        joinedReserves = []
        minibossList = getMinibossList()
        if len(self.reserveSuits) > 0 and len(activeSuits) < battle.maxSuits:
            for info in self.reserveSuits:
                if len(activeSuits) < battle.maxSuits and len(minibossList) < 2:
                    suits.append(info[0])
                    activeSuits.append(info[0])
                    joinedReserves.append(info)
                    minibossList = getMinibossList()

            for info in joinedReserves:
                self.reserveSuits.remove(info)

        joinedReservesA = []
        if len(self.reserveSuitsA) > 0 and battle is self.battleA and len(activeSuits) < battle.maxSuits:
            for info in self.reserveSuitsA:
                if len(activeSuits) < battle.maxSuits:
                    suits.append(info[0])
                    activeSuits.append(info[0])
                    joinedReservesA.append(info)

            for info in joinedReservesA:
                self.reserveSuitsA.remove(info)

            # Clear these out as we don't want any possible extra pesky cogs lying around.
            self.reserveSuitsA = []

        joinedReservesB = []
        if len(self.reserveSuitsB) > 0 and battle is self.battleB and len(activeSuits) < battle.maxSuits:
            for info in self.reserveSuitsB:
                if len(activeSuits) < battle.maxSuits:
                    suits.append(info[0])
                    activeSuits.append(info[0])
                    joinedReservesB.append(info)

            for info in joinedReservesB:
                self.reserveSuitsB.remove(info)

            # Clear these out as we don't want any possible extra pesky cogs lying around.
            self.reserveSuitsB = []

        battle.resume(joinedReserves + joinedReservesA + joinedReservesB)

    def makeBattle(self, bossCogPosHpr, battlePosHpr, roundCallback, finishCallback, battleNumber, battleSide):
        if battleNumber == 1:
            battle = DistributedBattleVirtualAI.DistributedBattleVirtualAI(
                self.air, self, roundCallback, finishCallback, battleSide)
        else:
            battle = DistributedBattleLitigatorsAI.DistributedBattleLitigatorsAI(
                self.air, self, roundCallback, finishCallback, battleSide)
        self.setBattlePos(battle, bossCogPosHpr, battlePosHpr)
        battle.suitsKilled = self.suitsKilled
        battle.battleCalc.toonSkillPtsGained = self.toonSkillPtsGained
        battle.toonExp = self.toonExp
        battle.toonOrigQuests = self.toonOrigQuests
        battle.toonOrigMerits = self.toonOrigMerits
        battle.toonMerits = self.toonMerits
        battle.toonParts = self.toonParts
        battle.helpfulToons = self.helpfulToons

        battle.generateWithRequired(self.zoneId)
        if battleNumber != 1:
            self.accept(battle.uniqueName("battleFinalFinished"), self.forceExitChairs)
        return battle

    # Random suit spawning
    def genRandSuit(self, battle):
        newSuit = DistributedSuitAI.DistributedSuitAI(simbase.air, None)
        dna = SuitDNA.SuitDNA()
        newSuit.dna = dna

        # Do some funky stuff that gives a guaranteed wide range of levels.
        # Make a differentiation here so that we can store the level boosts for both battles.
        if not hasattr(self, 'levelBoostA'):
            self.levelBoostA = 0
        if not hasattr(self, 'levelBoostB'):
            self.levelBoostB = 0

        maxLevel = 18
        minLevel = 10

        if battle is self.battleA:
            generatedLevel = self.randomGen.randint(minLevel + self.levelBoostA, maxLevel)
            self.levelBoostA = maxLevel - generatedLevel
        else:
            generatedLevel = self.randomGen.randint(minLevel + self.levelBoostB, maxLevel)
            self.levelBoostB = maxLevel - generatedLevel

        randNum = self.randomGen.random()
        # 10% chance to +1 the given level
        if randNum <= 0.1:
            generatedLevel += 1
            # 1% chance to +2 the given level
            if randNum <= 0.01:
                generatedLevel += 1

        suitType = SuitDNA.getRandomSuitType(generatedLevel)
        newSuit.dna.newSuitRandom(suitType, 'l')
        newSuit.setLevel(generatedLevel)
        if self.randomGen.random() <= 0.25:
            newSuit.setElite(1)
        newSuit.generateWithRequired(self.zoneId)
        newSuit.node().setName('suit-%s' % newSuit.doId)
        return newSuit

    def enterIntroduction(self):
        self.calcAndSetBattleDifficulty()
        self.resetBattles()
        self.arenaSide = None
        self.makeBattleOneBattles()
        self.barrier = self.beginBarrier('Introduction', self.involvedToons, 90, self.doneIntroduction)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'clo_hm', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)
        # Add the CLO to each toon's encountered cogs for the cog gallery.
        typeList = []
        typeList.append({'type': 'clo_hm'})
        for toon in self.involvedToons:
            simbase.air.cogPageManager.toonEncounteredCogs(toon, typeList)

    def enterPrepareBattleTwo(self):
        self.barrier = self.beginBarrier('PrepareBattleTwo', self.involvedToons, 100, self.__donePrepareBattleTwo)
        self.divideToons()
        self.b_setLitigationOrder()
        self.makeBattleTwoBattles()
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'clo_hm', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def b_setLitigationOrder(self):
        self.shuffleLitigationOrder()
        self.d_setLitigationOrder()

    def shuffleLitigationOrder(self):
        # Check if we need an av's forced litigation order from commands before continuing.
        for avId in self.involvedToons:
            av = self.air.doId2do.get(avId)
            if not av:
                continue

            if hasattr(av, 'forceLitigationOrder') and av.forceLitigationOrder:
                self.litigationOrder = av.forceLitigationOrder
                del av.forceLitigationOrder
                return

        self.randomGen.shuffle(self.litigationOrder)

    def d_setLitigationOrder(self):
        self.sendUpdate('setLitigationOrder', [self.litigationOrder])

    def d_updateLitigationMemberPosition(self, name, battleSide):
        self.sendUpdate('updateLitigationMemberPosition', [name, battleSide])

    def makeBattleTwoBattles(self):
        self.postBattleState = "PrepareBattleThree"
        self.initializeBattles(2, BossCogGlobals.LawbotBossBattleBackFromTablePosHpr)

    def __donePrepareBattleTwo(self, avIds):
        self.b_setState("BattleTwo")

    def enterBattleTwo(self):
        self.setupChairs()
        self.makeBattleTwoBattles()
        if self.battleA:
            self.battleA.startBattle(self.toonsA, self.suitsA)
        if self.battleB:
            self.battleB.startBattle(self.toonsB, self.suitsB)

    def exitBattleTwo(self):
        self.deleteChairs()
        self.resetBattles()

    def enterPrepareBattleThree(self):
        self.calcAndSetBattleDifficulty()
        self.__makeBattleThreeObjects()
        self.barrier = self.beginBarrier('PrepareBattleThree', self.involvedToons, 45, self.__donePrepareBattleThree)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'clo_hm', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def __donePrepareBattleThree(self, avIds):
        self.b_setState('BattleThree')

    def __makeBattleThreeObjects(self):
        self.makeCannons()
        self.makeGavels()

    def makeCannons(self):
        if self.cannons is None:
            self.cannons = []
            for index in range(len(BossCogGlobals.LawbotBossCannonPosHprs)):
                cannon = DistributedHardmodeLawbotCannonAI.DistributedHardmodeLawbotCannonAI(
                    self.air, self, index, *BossCogGlobals.LawbotBossCannonPosHprs[index]
                )
                cannon.generateWithRequired(self.zoneId)
                self.cannons.append(cannon)

    def __deleteBattleThreeObjects(self):
        self.deleteCannons()
        self.deleteGavels()
        self.resetLawyers()

    def enterBattleThree(self):
        self.startBattleTime()
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        self.setZ(0)
        self.makeInitialLawyers()
        self.enableGavels()
        self.barrier = self.beginBarrier("BattleThree", self.involvedToons, BossCogGlobals.LawbotBossEvidenceRoundTime + 1, self.__doneBattleThree)

    def exitBattleThree(self):
        self.ignoreBarrier(self.barrier)
        self.stopBattleTime()
        self.resetBattles()
        self.stopAttacks()
        self.__deleteBattleThreeObjects()

    def __doneBattleThree(self, avIds):
        self.b_setState('PrepareBattleFour')

    def enterPrepareBattleFour(self):
        self.calcAndSetBattleDifficulty()
        self.barrier = self.beginBarrier('PrepareBattleFour', self.involvedToons, 60, self.__donePrepareBattleFour)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'clo_hm', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def __donePrepareBattleFour(self, avIds):
        self.b_setState('BattleFour')

    def enterBattleFour(self):
        self.setPosHpr(*BossCogGlobals.LawbotBossBattleTwoPosHpr)
        self.startBattleTime()
        self.battleFourTimeStarted = globalClock.getFrameTime()
        self.calcAndSetBattleDifficulty()
        self.air.writeServerEvent('lawbotBossSettings', self.doId, '%s|%s' % (
            self.dept,
            self.toonupValue
        ))
        self.__makeBattleFourObjects()
        self.resetBattles()
        self.battleThreeStart = globalClock.getFrameTime()
        self.calculateEvidenceType()
        self.waitForNextAttack(5)
        self.numToonsAtStart = len(self.involvedToons)
        # Getting Sound Evidence Tip
        for avId in self.involvedToons:
            toon = simbase.air.doId2do.get(avId)
            if toon:
                toon.showToonTip(TTE.TIP_CLO_GET_EVIDENCE)

    def calculateEvidenceType(self):
        # Bugle at 0, Aoogah at 30, Trunk at 65, Fog at 100.
        for toonId in self.involvedToons:
            if toonId in self.evidence:
                evidenceAmt = self.evidence[toonId]

                if evidenceAmt >= BossCogGlobals.HardmodeLawbotBossSoundEvidenceRequirement['fog']:
                    self.soundTypes[toonId] = 6
                elif evidenceAmt >= BossCogGlobals.HardmodeLawbotBossSoundEvidenceRequirement['trunk']:
                    self.soundTypes[toonId] = 5
                elif evidenceAmt >= BossCogGlobals.HardmodeLawbotBossSoundEvidenceRequirement['aoogah']:
                    self.soundTypes[toonId] = 4
                else:
                    self.soundTypes[toonId] = 3
            else:
                self.soundTypes[toonId] = 3

    def __makeBattleFourObjects(self):
        self.makeBossTrackingSpotlights()
        self.makeInitialLawyers()
        self.makeBumpyNPC()
        self.makeLaurenNPC()
        self.makeBossTraps()
        self.makeBossSpotlights()

    def __deleteBattleFourObjects(self):
        self.resetLawyers()
        self.deleteBossTrackingSpotlights()
        self.deleteBossSpotlights()
        self.removeBumpyNPC()
        self.removeLaurenNPC()
        self.deleteBossTraps()

    def doBattleFourInfo(self):
        didTheyWin = 0
        if self.bossDamage == BossCogGlobals.LawbotBossMaxDamage:
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

        self.air.writeServerEvent('b3Info', self.doId, '%d|%.2f|%d|%d|%d|%d|%s' % (
            didTheyWin,
            self.battleFourTimeInMin,
            self.numToonsAtStart,
            self.numToonsAtEnd,
            self.toonupValue,
            self.numAreaAttacks,
            toonHps
        ))

    def exitBattleFour(self):
        taskMgr.remove(self.uniqueName('NextLawyer'))
        taskMgr.remove(self.uniqueName('executive-cooldown'))
        self.stopBattleTime()
        self.doBattleFourInfo()
        self.stopAttacks()
        self.__deleteBattleFourObjects()
        self.deleteTreasures()

    def enterVictory(self):
        self.resetBattles()
        self.suitsKilled.append({
            'type': 'clo_hm',
            'level': None,
            'track': self.dna.dept,
            'isSkelecog': 0,
            'isForeman': 0,
            'isBoss': 1,
            'isSupervisor': 0,
            'isVirtual': 0,
            'hasRevives': 0,
            'isElite': 0,
            'activeToons': self.involvedToons[:]
        })
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 60, self.__doneVictory)

    def __doneVictory(self, avIds):
        self.notify.info("LogStats HardmodeLawbotBossWasDefeated")

        for toonId in self.involvedToons:
            self.notify.info("LogStats ToonDefeatedHardmodeLawbotBoss toonid %s" % toonId)
            toon = self.air.doId2do.get(toonId)
            if not toon:
                continue

            # Add dept exp bonus for winning the boss
            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_LAWBOT)
            toon.addDepartmentExp(1000 * mult, ToontownGlobals.DEPARTMENT_LAWBOT)

            # Give the toon the needed bonuses depending on dept level, holiday, and daily bonus.
            bonuses = 0
            departmentLevel = toon.getDepartmentLevel(ToontownGlobals.DEPARTMENT_LAWBOT)
            if departmentLevel == ToontownGlobals.MaxDepartmentLevel[ToontownGlobals.DEPARTMENT_LAWBOT]:
                bonuses += 1
            bonuses = toon.applyBoosters([BoosterItemType.Reward_Boss_Global, BoosterItemType.Reward_Boss_Lawbot], bonuses)

            # Give toons their rewards
            self.giveCeaseDesistReward(toon, toonId, bonuses)
            self.handleUniteRewards(toon)

            toon.b_promote(self.deptIndex, hardFlag=1)
            if toon.cogTypes[self.deptIndex] == 7 and toon.cogLevels[self.deptIndex] >= 7:
                toon.getHammerspace().addItem(BackgroundItemType.HQ_Lawbot)
            # Promotion + Reward Tips
            toon.showToonTip(TTE.TIP_DISGUISE_PROMOTION)
            toon.showToonTip(TTE.TIP_REWARDS_CEASE_AND_DESIST)
            # Unite tip
            toon.showToonTip(TTE.TIP_REWARDS_UNITE)

            if self.begunToonAmount == 1:
                self.notify.info("LogStats ToonSoloDefeatedHardmodeLawbotBoss toonid %s" % toonId)
            self.air.achievementsManager.overclockedCLO(toonId, numPlayers=self.begunToonAmount)

            # Handle boss specific quests
            simbase.air.quest3Manager.progressObjective(
                toon, 
                LawbotBossContext(
                    "l",
                    self.toonStunsDict.get(toonId, 0),
                    self.toonDamagesDict.get(toonId, 0),
                    self.evidence.get(toonId, 0),
                    (
                        self.toonsNumSuitsDestroyed.get(toonId, 0),
                        self.toonsNumSuitsDefeated.get(toonId, 0),
                    ),
                    (
                        self.toonsNumExeSuitsDestroyed.get(toonId, 0),
                        self.toonsNumExeSuitsDefeated.get(toonId, 0),
                    ),
                )
            )
        
        self.prepareReward()
        self.rewardClubCoins()

        # First OCLO clear
        # self.air.netMessenger.send(
        #     'clearCheck', [
        #         json.dumps({
        #             'type': 'oclo',
        #             'avatarIds': self.involvedToons,
        #             'avatarNames': [self.air.doId2do.get(toonId).getName() for toonId in self.involvedToons]
        #         })
        #     ]
        # )

    def giveCeaseDesistReward(self, toon, toonId, bonuses=0):
        toon.getHammerspace().addItem(MaterialItemType.CeaseAndDesists, self.numSues + (bonuses*2))
        self.d_setNumSuesEarned(toonId, self.numSues + (bonuses*2))
        toon.queueScavenge(self.numSues + (bonuses*2), ScavengeType.Ceases, [])

    def exitVictory(self):
        self.deleteBossTraps()
        self.takeAwaySound()

    def makeBossTraps(self):
        if self.traps is None:
            self.traps = []
            for index in range(len(BossCogGlobals.LawbotBossTrapsPosHpr)):
                # If the trap is index 0, make it a trapdoor. Else, it should be a quicksand.
                trapLevel = 5 if index in BossCogGlobals.LawbotBossTrapdoorsList else 4
                trap = DistributedLawbotBossTrapAI.DistributedLawbotBossTrapAI(self.air, self, index, trapLevel)
                trap.generateWithRequired(self.zoneId)
                trap.setPosHpr(*BossCogGlobals.LawbotBossTrapsPosHpr[index])
                self.traps.append(trap)

    def makeBossSpotlights(self):
        if self.spotlights is None:
            self.spotlights = []
            for index in range(len(BossCogGlobals.LawbotBossSpotlightPosList)):
                spotlight = DistributedLawbotBossSecurityCameraAI.DistributedLawbotBossSecurityCameraAI(
                    self.air, self, BossCogGlobals.LawbotBossSpotlightPosList[index][:],
                    BossCogGlobals.LawbotBossSpotlightDamage
                )
                spotlight.generateWithRequired(self.zoneId)
                self.spotlights.append(spotlight)

    def makeBossTrackingSpotlights(self):
        if self.trackingSpotlights is None:
            self.trackingSpotlights = []
            for index in range(len(BossCogGlobals.LawbotBossTrackingSpotlightPosList)):
                spotlight = DistributedLawbotBossSecurityCameraAI.DistributedLawbotBossSecurityCameraAI(
                    self.air, self, BossCogGlobals.LawbotBossTrackingSpotlightPosList[index][:],
                    BossCogGlobals.LawbotBossSpotlightDamage, tracking=1
                )
                spotlight.generateWithRequired(self.zoneId)
                self.trackingSpotlights.append(spotlight)

    def makeBumpyNPC(self):
        npcId = 2009
        self.bumpyNPC = DistributedNPCBumpyAI(self.air, self, npcId)
        self.bumpyNPC.setPosHpr(*BossCogGlobals.LawbotBossBumpyPosHpr)
        npcToon = NPCToons.NPCToonDict.get(npcId)
        npcToon.zoneId = self.zoneId
        npcToon.createNPC(self.bumpyNPC, 0)
        self.bumpyNPC.initializeTimers()

    def makeLaurenNPC(self):
        npcId = 12050
        self.laurenNPC = DistributedNPCLaurenAI(self.air, self, npcId)
        self.laurenNPC.setPosHpr(*BossCogGlobals.LawbotBossBumpyPosHpr)
        npcToon = NPCToons.NPCToonDict.get(npcId)
        npcToon.zoneId = self.zoneId
        npcToon.createNPC(self.laurenNPC, 0)
        self.laurenNPC.initializeTimers()

    def removeLaurenNPC(self):
        if self.laurenNPC:
            self.laurenNPC.requestDelete()
            self.laurenNPC = None

    def getLawyerSpawnRate(self):
        toonsAmount = len(self.involvedToons)
        if toonsAmount >= 7:
            return 8
        elif toonsAmount >= 5:
            return 10
        else:
            return 12

    def makeInitialLawyers(self):
        self.resetLawyers()

        currState = self.getCurrentOrNextState()
        if currState == "BattleThree":
            for i in range(10):
                self.makeLawyer(i)

            self.waitForNextLawyers(self.getLawyerSpawnRate())
        elif currState == "BattleFour":
            # Cogs below num 0 are considered virtuals.
            for i in range(-2, 10):
                self.makeLawyer(i, virtual=i < 0)

            self.waitForNextLawyers()

    def waitForNextLawyers(self, delayTime=12):
        currState = self.getCurrentOrNextState()
        if currState in ("BattleThree", "BattleFour"):
            taskName = self.uniqueName('NextLawyer')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.makeLawyers, taskName)

    def makeLawyers(self, taskName):
        currState = self.getCurrentOrNextState()
        if currState == "BattleThree":
            availablePaintings = list(range(10))
            self.randomGen.shuffle(availablePaintings)
            for i in availablePaintings:
                if len(self.lawyers) >= self.maxLawyersBattleTwo:
                    break
                # Chance to spawn Executive
                elite = self.randomGen.random() <= 0.12
                self.makeLawyer(i, elite=elite)

            self.waitForNextLawyers(self.getLawyerSpawnRate())
        elif currState == "BattleFour":
            sortedLawyersPerPainting = {p: l for p, l in sorted(self.lawyersPerPainting.items(), key=itemgetter(1))}
            for i in sortedLawyersPerPainting:
                if len(self.lawyers) >= self.maxLawyersBattleFour:
                    break

                self.makeLawyer(i)

            self.waitForNextLawyers()

    def makeLawyer(self, painting, virtual=False, elite=False):
        currState = self.getCurrentOrNextState()
        if currState == "BattleThree":
            level = self.randomGen.randint(6, 18)
        else:
            level = int(math.ceil(self.progressValue(2, self.lawyerMaxLevel)))
        spotlight = None

        attackCogsWanted = sum([
            self.bossDamage >= self.bossMaxDamage * 0.05,
            self.bossDamage >= self.bossMaxDamage * 0.05,
            self.bossDamage >= self.bossMaxDamage * 0.4,
        ])  # True evals to 1, False evals to 0, sum the entirety of it.

        if self.attackCogsSpawned < attackCogsWanted:
            # Spawn attack cogs
            suit = DistributedHardmodeLawbotBossSuitAttackAI.DistributedHardmodeLawbotBossSuitAttackAI(self, self.air,
                                                                                                       None, painting)
            self.attackCogsSpawned += 1
        else:
            suit = DistributedHardmodeLawbotBossSuitAI.DistributedHardmodeLawbotBossSuitAI(self, self.air, None,
                                                                                           painting)
            suit.dna = SuitDNA.SuitDNA()
        if suit.type == BossCogGlobals.LawbotBossSuitAttack:
            suitInfo = self.randomGen.choice([['sh', 6, 12], ['br', 7, 15], ['nn', 3, 10]])
            suit.dna.newSuit(suitInfo[0])
            suit.setLevel(min(max(level, suitInfo[1]), suitInfo[2]))
            suit.setElite(1)
            self.lawyersPerPainting[painting] = self.lawyersPerPainting.get(painting, 0) + 1
        elif virtual:
            spotlight = painting + 2
            spotlight = self.trackingSpotlights[spotlight]
            # Force the virtuals to be level 15 legal eagles.
            suit.dna.newSuitRandom(7, suitDept, wantAlts=0)
            suit.setLevel(15)
            suit.setVirtual(1)
        else:
            suitType = SuitDNA.getRandomSuitType(level)
            # Don't randomly spawn alternates in the Hardmode Sound Round
            suit.dna.newSuitRandom(suitType, suitDept, wantAlts=False if currState == "BattleFour" else True)
            suit.setLevel(level)
            self.lawyersPerPainting[painting] = self.lawyersPerPainting.get(painting, 0) + 1
        if currState == "BattleFour":
            # If a painting is in the middle, spawn a guaranteed executive.
            # Else, there is a 15% chance for the cog to become an executive as long as the cooldown is not active.
            if painting in (4, 5) or (self.randomGen.random() <= 0.15 and not virtual and not self.onExecutiveSpawnCooldown):
                elite = True
                self.onExecutiveSpawnCooldown = True
                taskMgr.doMethodLater(BossCogGlobals.HardmodeLawbotBossExecutiveSpawnCooldown,
                                      self.removeExecutiveSpawnCooldown, self.uniqueName('executive-cooldown'))
        if elite:
            suit.setElite(1)
        suit.setPosHpr(*BossCogGlobals.LawbotBossLawyerPosHprs[painting])
        suit.generateWithRequired(self.zoneId)
        # Grab the cog's specialization for health purposes.
        specialization = SuitBattleGlobals.SuitAttributes[suit.dna.name].get('specialization', SuitBattleGlobals.NORMAL)
        health = SuitBattleGlobals.calculateHp({'specialization': specialization}, level, dnaName=suit.dna.name)
        # If the cog is elite, increase it's max HP by 1.5x
        if suit.isElite:
            health *= 1.5
        suit.b_setSuitMaxDamage(int(health))
        if spotlight is not None:
            # For virtuals, they need a spotlight attached to them for tracking.
            spotlight.b_setTrackingDoId(suit.doId)
            suit.waitForNextMove(BossCogGlobals.LawbotBossLawyerVirtualInitialDelay)
        else:
            delay = BossCogGlobals.LawbotBossLawyerInitialDelay
            if currState == "BattleFour":
                self.d_createPaintingMovie(painting)
                delay *= 2
            suit.waitForNextMove(delay)
        self.lawyers.append(suit)
        self.lawyerPositions[suit] = suit.getPos()
        self.sendLawyerId(suit)

    def removeExecutiveSpawnCooldown(self, _=None):
        self.onExecutiveSpawnCooldown = False

    def makeDefenseSpecialists(self, healthLeft, trapDamage, empoweredSpawn):
        healthPercent = healthLeft / self.bossMaxDamage
        levelList = []
        if empoweredSpawn:
            levelList.append(15)
            # At 40% health, replace a Conveyancer with Advocate
            if healthPercent <= 0.4:
                levelList.append(15)
            else:
                levelList.append(8)
            # At 60% health, replace Pettifogger with Advocate
            if healthPercent <= 0.6:
                levelList.append(15)
            else:
                levelList.append(7)
            # At 20% health, replace a Conveyancer with Advocate
            if healthPercent <= 0.2:
                levelList.append(15)
            else:
                levelList.append(8)
        else:
            # All Conveyancers under 50%, otherwise Pettifoggers
            if healthPercent <= 0.5:
                levelList = [8, 8, 8, 8]
            else:
                levelList = [7, 7, 7, 7]
        for i in range(len(levelList)):
            suit = DistributedLawbotBossDefenseSpecialistAI(self, self.air, None)

            level = levelList[i]
            if level <= 7:
                # Levels 2 - 7: Pettifogger
                suitName = 'pf'
            elif level == 8:
                # Level 8: Conveyancer
                suitName = 'cv'
            else:
                # Level 9 - 15: Advocate
                suitName = 'ad'

            actualSuitName = suitName

            # Make DNA for the chosen specialist
            suit.dna = SuitDNA.SuitDNA()
            suit.dna.newSuit(actualSuitName)
            suit.setLevel(level)
            suit.setElite(1)
            suit.setPosHpr(*BossCogGlobals.LawbotBossDefenseSpecialistPos[i])
            suit.generateWithRequired(self.zoneId)

            # Get base health and scale it for each toon beyond 4
            health = BossCogGlobals.LawbotBossHardDefenseHealth[suitName][0]
            health = health + BossCogGlobals.LawbotBossHardDefenseHealth[suitName][1] * max(0, len(self.involvedToons) - 4)
            # Scale health further based on trap damage
            damageRange = BossCogGlobals.LawbotBossPrestigedTrapsDamage[5] - BossCogGlobals.LawbotBossTrapsDamage[4]
            adjustedTrapDamage = trapDamage - BossCogGlobals.LawbotBossTrapsDamage[4]
            healthScale = lerp(1, BossCogGlobals.LawbotBossDefenseHealthScaling, adjustedTrapDamage / damageRange)
            health = health * healthScale
            suit.b_setSuitMaxDamage(int(health))
            self.defenseSpecialists.append(suit)
            self.sendDefenseSpecialistId(suit)

    def calcAndSetBattleDifficulty(self):
        # Max flying cogs in the cannon/evidence round
        self.maxLawyersBattleTwo = 16 + math.ceil(len(self.involvedToons) * 1.5)
        # Max flying cogs in the sound round
        self.maxLawyersBattleFour = 18
        # Grab the sound damage toons should deal from Globals.
        self.soundDamage = BossCogGlobals.LawbotBossSoundKnockback.get(len(self.involvedToons), 1)
        self.getToonDifficulty()
        # Sets CLO HP, cog levels, # of sound, # of c&ds gained, and max flying cog level in sound round
        self.b_setMaxHp(2000)
        self.battleOnePlanner = SuitBuildingGlobals.SPE.HARDMODE_CLO
        self.numSound = 30
        self.numSues = 30
        self.lawyerMaxLevel = 12
        self.damageMult = 1.5
        self.universalUnites = 7

    def giveEvidence(self, toonID, evidenceAmt, extraMult=1.0):
        currEvidence = self.evidence.get(toonID, 0)
        self.evidence[toonID] = currEvidence + evidenceAmt
        self.d_updateEvidence(toonID, evidenceAmt)

        # Give dept exp for gaining evidence and check for nameplate
        toon = self.air.doId2do.get(toonID)
        if toon:
            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_LAWBOT)
            xp = 4 * evidenceAmt * mult * extraMult
            toon.addDepartmentExp(math.ceil(xp), ToontownGlobals.DEPARTMENT_LAWBOT)

            # Nameplate Reward for Max Evidence
            if self.evidence[toonID] >= BossCogGlobals.HardmodeLawbotBossSoundEvidenceRequirement['max']:
                toon.addItem(NameplateItemType.Special_UpToEleven)

    def makeTreasure(self, lawyer, av):
        if self.state != 'BattleFour':
            return
        # Don't spawn treasures from defense specialists
        if lawyer.type == BossCogGlobals.LawbotBossSuitDefense:
            return
        # If the max amount of treasures has been reached, dont
        if len(self.treasures) >= self.maxTreasures:
            return
        # If the lawyer is by the CLO, there is a 65% (scales down based on number of players) chance for it to dont
        if lawyer.doId in self.nearbyLawyers:
            if self.randomGen.random() > 0.35 + 0.04 * len(self.involvedToons):
                return

        lawyerPos = lawyer.getPos()
        avPos = av.getPos()
        v = Vec3(avPos[0], avPos[1], 0.0)

        angle = self.randomGen.uniform(0.0, 2.0 * math.pi)
        radius = 6
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        fpos = Point3(v[0] + dx, v[1] + dy, 0)
        bounds = BossCogGlobals.LawbotBossTreasureBounds
        # Ensure the treasure's positions is within the bounds of the room
        fpos = Point3(min(max(fpos[0], bounds[0][0]), bounds[0][1]), min(max(fpos[1], bounds[1][0]), bounds[1][1]), 0)
        lawyerLevel = lawyer.getActualLevel()
        # Determine the playground style for this treasure
        if lawyerLevel <= 5:
            styleList = [ToontownGlobals.ToontownCentral,
                         ToontownGlobals.DonaldsDock,
                         ToontownGlobals.OldeToontown,
                         ToontownGlobals.GolfZone,
                         ToontownGlobals.GoofySpeedway,
                         ToontownGlobals.DaisyGardens]
        elif lawyerLevel <= 7:
            styleList = [ToontownGlobals.DonaldsDock,
                         ToontownGlobals.OldeToontown,
                         ToontownGlobals.GolfZone,
                         ToontownGlobals.GoofySpeedway,
                         ToontownGlobals.DaisyGardens,
                         ToontownGlobals.MinniesMelodyland]
        elif lawyerLevel <= 9:
            styleList = [ToontownGlobals.MinniesMelodyland,
                         ToontownGlobals.TheBrrrgh,
                         ToontownGlobals.OutdoorZone,
                         ToontownGlobals.DonaldsDreamland]
        else:
            styleList = [ToontownGlobals.OutdoorZone,
                         ToontownGlobals.DonaldsDreamland]
        style = random.choice(styleList)
        healAmount = math.ceil(lawyerLevel * 1.2)
        treasure = DistributedLawbotBossTreasureAI.DistributedLawbotBossTreasureAI(self.air, self, lawyer, style, lawyerPos[0], lawyerPos[1], lawyerPos[2], fpos[0], fpos[1], -71.601)
        treasure.generateWithRequired(self.zoneId)
        treasure.healAmount = healAmount
        self.treasures[treasure.doId] = treasure

    def zapToon(self, x, y, z, h, p, r, bpx, bpy, attackCode, timestamp):
        currState = self.getCurrentOrNextState()
        # You shouldn't take damage during the Cannon Round
        if currState == "BattleThree":
            return
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'zapToon from unknown avatar'):
            return
        toon = simbase.air.doId2do.get(avId)
        if toon:
            self.d_showZapToon(avId, x, y, z, h, p, r, attackCode, timestamp)
            damage = BossCogGlobals.BossCogDamageLevels.get(attackCode)
            if damage is None:
                self.notify.warning('No damage listed for attack code %s' % attackCode)
                damage = 5
            damage *= self.getDamageMultiplier()
            # If the CLO is stunned, being rammed/bumped deals 4 damage.
            # Else, it is multiplied by her normal damage multiplier.
            if attackCode == BossCogGlobals.BossCogElectricFence:
                damage = 5
                if self.attackCode != BossCogGlobals.BossCogDizzyNow:
                    damage *= self.getDamageMultiplier()
            elif attackCode == BossCogGlobals.BossCogDocketAoeAttack:
                # Don't scale the damage for this attack, or players will have a bad time.
                damage = BossCogGlobals.BossCogDamageLevels.get(attackCode)

            damage = math.floor(damage)
            self.damageToon(toon, damage)

    def healBoss(self, bossHeal):
        bossDamage = -bossHeal
        currState = self.getCurrentOrNextState()
        if currState != 'BattleFour':
            return
        bossDamage = min(self.getBossDamage() + bossDamage, self.bossMaxDamage)
        bossDamage = max(bossDamage, 0)
        self.b_setBossDamage(bossDamage)

    @property
    def shouldShowSurrenderDialogue(self):
        if self.getCurrentOrNextState() == 'BattleOne':
            return False

        return True
