import random
from typing import Optional

from direct.distributed.ClockDelta import *
from direct.fsm import FSM

from toontown.suit import BossCogGlobals
from toontown.ai.AIBaseGlobal import *
from toontown.building import SuitBuildingGlobals
from toontown.groups.GroupEnums import GroupType
from toontown.instances import DistributedCutsceneSkipButtonAI
from toontown.inventory.enums.ItemEnums import BackgroundItemType, BoosterItemType, IOUItemType
from toontown.inventory.registry.IOURegistry import IOURegistry
from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from toontown.quest3.context.CogBossContext import CogBossContext
from toontown.quest3.context.TossPieContext import TossPieContext
from toontown.quest3.SpecialQuestZones import SpecialQuestZones
from toontown.suit import DistributedBossCogAI, DistributedSuitAI, SuitDNA
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toon.gui.ToonTipGlobals import TTE


@DirectNotifyCategory()
class DistributedSellbotBossAI(DistributedBossCogAI.DistributedBossCogAI, FSM.FSM):

    limitHitCount = 6
    hitCountDamage = 350
    numPies = 50

    groupType = GroupType.VP

    def __init__(self, air):
        DistributedBossCogAI.DistributedBossCogAI.__init__(self, air, 's')
        FSM.FSM.__init__(self, 'DistributedSellbotBossAI')
        self.doobers = []
        self.cagedToonNpcId = 90001
        self.bossMaxDamage = BossCogGlobals.SellbotBossMaxDamage
        self.battleOnePlanner = SuitBuildingGlobals.SPE.VP
        self.battleTwoPlanner = SuitBuildingGlobals.SPE.VP_SKELECOGS
        self.recoverRate = 0
        self.recoverStartTime = 0
        self.numIOUs = 2
        self.pieHealAmt = 1
        self.toonDamagesDict = {}
        self.toonStunsDict = {}
        self.toonPiesThrownDict = {}
        self.toonRewards = {}
        self.toonHealDict = {}
        self.toonPieGrabDict = {}
        self.numStuns = 0
        self.noSwipeAttackCodes = [BossCogGlobals.BossCogAreaAttack,
                                   BossCogGlobals.BossCogDizzyNow,
                                   BossCogGlobals.BossCogFrontAttack,
                                   BossCogGlobals.BossCogRecoverDizzyAttack]
        self.__openedDoorThree = False
        iouChoices = [iou for iou in IOURegistry if iou != IOUItemType.AllBoost]  # No rain!!!
        self.giveRewards = [random.choice(iouChoices) for _ in range(20)]

    def announceGenerate(self):
        super().announceGenerate()
        self.accept("toonTossedPie", self.logToonPieThrow)

    def delete(self):
        del self.toonRewards
        return super().delete()

    def getContentSync(self) -> Optional[ContentSyncType]:
        return ContentSyncType.SBHQ

    def getHoodId(self):
        return ToontownGlobals.SellbotHQ

    def getCagedToonNpcId(self):
        return self.cagedToonNpcId

    def logToonPieThrow(self, avId: int, pieType: int) -> None:
        if avId not in self.involvedToons or pieType != 4:
            return
        self.toonPiesThrownDict.setdefault(avId, 0)
        self.toonPiesThrownDict[avId] += 1

    def hitBoss(self, bossDamage):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'hitBoss from unknown avatar'):
            return
        self.validate(avId, bossDamage == BossCogGlobals.SellbotBossPieDamage, 'invalid bossDamage %s' % bossDamage)
        if bossDamage > BossCogGlobals.SellbotBossPieDamage:
            simbase.air.writeServerEvent('suspicious', avId, 'Toon sent an attack over 10 damage!')
            simbase.air.banManager.ban(0, avId, '10-y', 'Your account has been flagged for suspicious activity. Contact support for further information.')
            return
        if bossDamage < BossCogGlobals.SellbotBossPieDamage:
            simbase.air.writeServerEvent('suspicious', avId, 'Toon sent an attack less than 10 damage!')
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BattleThree':
            return
        if self.attackCode != BossCogGlobals.BossCogDizzyNow:
            toon = simbase.air.doId2do.get(avId)
            if toon:
                # How to Stun VP Tip
                toon.showToonTip(TTE.TIP_STUN_VP_TUTORIAL)
            return
        bossDamage = min(self.getBossDamage() + bossDamage, self.bossMaxDamage)
        self.b_setBossDamage(bossDamage, 0, 0)
        self.d_updateDamageDealt(avId)
        if avId in self.toonDamagesDict:
            self.toonDamagesDict[avId] += BossCogGlobals.SellbotBossPieDamage
            toon = self.air.doId2do.get(avId)
            if toon:
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_SELLBOT)
                toon.addDepartmentExp(math.ceil(70 * mult), ToontownGlobals.DEPARTMENT_SELLBOT)
        else:
            self.toonDamagesDict[avId] = BossCogGlobals.SellbotBossPieDamage
            toon = self.air.doId2do.get(avId)
            if toon:
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_SELLBOT)
                toon.addDepartmentExp(math.ceil(70 * mult), ToontownGlobals.DEPARTMENT_SELLBOT)
        if self.bossDamage >= self.bossMaxDamage:
            self.setState('NearVictory')
        else:
            self.__recordHit()

    def hitBossInsides(self):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'hitBossInsides from unknown avatar'):
            return
        currState = self.getCurrentOrNextState()
        if currState != 'BattleThree':
            return
        if not self.__openedDoorThree:
            return
        self.b_setAttackCode(BossCogGlobals.BossCogDizzyNow)
        self.d_updateStunCount(avId)
        self.numStuns += 1
        if avId in self.toonStunsDict:
            self.toonStunsDict[avId] += 1
            toon = self.air.doId2do.get(avId)
            if toon:
                stuns = self.toonStunsDict[avId]
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_SELLBOT)
                toon.addDepartmentExp(math.ceil((75 + 130/(stuns+1)) * mult), ToontownGlobals.DEPARTMENT_SELLBOT)
        else:
            self.toonStunsDict[avId] = 1
            toon = self.air.doId2do.get(avId)
            if toon:
                stuns = self.toonStunsDict[avId]
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_SELLBOT)
                toon.addDepartmentExp(math.ceil((75 + 130/(stuns+1)) * mult), ToontownGlobals.DEPARTMENT_SELLBOT)
        for toonId in self.involvedToons:
            toon = self.cr.doId2do.get(toonId)
            if toon:
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_SELLBOT)
                diminished_exp = math.ceil(10*(60/(self.numStuns+4))*mult)
                toon.addDepartmentExp(diminished_exp, ToontownGlobals.DEPARTMENT_SELLBOT)
                # VP is Stunned Tip
                toon.showToonTip(TTE.TIP_VP_STUNNED)
        self.b_setBossDamage(self.getBossDamage(), 0, 0)

    def d_updateDamageDealt(self, avId):
        self.sendUpdate('updateDamageDealt', [avId])

    def d_updateStunCount(self, avId):
        self.sendUpdate('updateStunCount', [avId])

    def hitToon(self, toonId):
        avId = self.air.getAvatarIdFromSender()
        if avId == toonId:
            simbase.air.writeServerEvent('suspicious', avId, 'Toon tried to heal their self!')
            simbase.air.banManager.ban(0, avId, '10-y', 'Your account has been flagged for suspicious activity. Contact support for further information.')
        if not self.validate(avId, avId != toonId, 'hitToon on self'):
            return
        if avId not in self.involvedToons or toonId not in self.involvedToons:
            return
        toon = self.air.doId2do.get(toonId)
        if toon:
            now = globalClock.getFrameTime()
            if toonId not in self.toonHealDict:  # Toon hasn't been logged for a heal yet, log them
                self.toonHealDict[toonId] = now
                self.healToon(toon, self.pieHealAmt)
            else:  # Check that 0.5 seconds has elapsed at least between heals
                lastHealTime = self.toonHealDict.get(toonId)
                if (now - lastHealTime) >= 0.5:
                    self.toonHealDict[toonId] = now
                    self.healToon(toon, self.pieHealAmt)

    def touchCage(self):
        avId = self.air.getAvatarIdFromSender()
        currState = self.getCurrentOrNextState()
        if currState != 'BattleThree' and currState != 'NearVictory':
            return
        if not self.validate(avId, avId in self.involvedToons, 'touchCage from unknown avatar'):
            return
        toon = simbase.air.doId2do.get(avId)

        def __givePies(toon):
            toon.b_setNumPies(self.numPies)
            toon.__touchedCage = 1
            self.__goodJump(avId)
            # Throwing Pies Tip
            toon.showToonTip(TTE.TIP_VP_THROW_PIES)

        now = globalClock.getFrameTime()
        if toon:
            if avId not in self.toonPieGrabDict:
                self.toonPieGrabDict[avId] = now
                __givePies(toon)
            else:
                lastGrab = self.toonPieGrabDict.get(avId)
                if (now - lastGrab) >= 5:
                    self.toonPieGrabDict[avId] = now
                    __givePies(toon)

    def finalPieSplat(self):
        if self.state != 'NearVictory':
            return
        self.b_setState('Victory')

    def doNextAttack(self, task):
        if self.attackCode == BossCogGlobals.BossCogDizzyNow:
            attackCode = BossCogGlobals.BossCogRecoverDizzyAttack
        else:
            attackCode = random.choice([BossCogGlobals.BossCogAreaAttack,
                                        BossCogGlobals.BossCogFrontAttack,
                                        BossCogGlobals.BossCogDirectedAttack,
                                        BossCogGlobals.BossCogDirectedAttack,
                                        BossCogGlobals.BossCogDirectedAttack,
                                        BossCogGlobals.BossCogDirectedAttack])
        if attackCode == BossCogGlobals.BossCogAreaAttack:
            self.__doAreaAttack()
        elif attackCode == BossCogGlobals.BossCogDirectedAttack:
            self.__doDirectedAttack()
        else:
            self.b_setAttackCode(attackCode)

    def __doAreaAttack(self):
        self.b_setAttackCode(BossCogGlobals.BossCogAreaAttack)
        now = globalClock.getFrameTime()
        self.b_setBossDamage(self.getBossDamage(), 0, now)

    def __doDirectedAttack(self):
        if self.nearToons:
            toonId = random.choice(self.nearToons)
            self.b_setAttackCode(BossCogGlobals.BossCogDirectedAttack, toonId)
        else:
            self.__doAreaAttack()

    def b_setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        self.d_setBossDamage(bossDamage, recoverRate, recoverStartTime)
        self.setBossDamage(bossDamage, recoverRate, recoverStartTime)

    def setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        self.bossDamage = bossDamage
        self.recoverRate = recoverRate
        self.recoverStartTime = recoverStartTime

    def getBossDamage(self):
        now = globalClock.getFrameTime()
        elapsed = now - self.recoverStartTime
        return int(max(self.bossDamage - self.recoverRate * elapsed / 60.0, 0))

    def d_setBossDamage(self, bossDamage, recoverRate, recoverStartTime):
        timestamp = globalClockDelta.localToNetworkTime(recoverStartTime)
        self.sendUpdate('setBossDamage', [bossDamage, recoverRate, timestamp])

    def waitForNextStrafe(self, delayTime):
        currState = self.getCurrentOrNextState()
        if currState == 'BattleThree':
            taskName = self.uniqueName('NextStrafe')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.doNextStrafe, taskName)

    def stopStrafes(self):
        taskName = self.uniqueName('NextStrafe')
        taskMgr.remove(taskName)

    def doNextStrafe(self, task):
        self.__openedDoorThree = True
        if self.attackCode != BossCogGlobals.BossCogDizzyNow:
            # If at the ledge, we only want the VP to open the front door.
            side = self.decideSideOpen()
            direction = random.choice([0, 1])
            self.sendUpdate('doStrafe', [side, direction])
        delayTime = 9
        self.waitForNextStrafe(delayTime)

    def decideSideOpen(self):
        if 160 <= self.bossDamage <= 360:
            return 1  # Open back on first hill.

        if 470 <= self.bossDamage <= 510:
            return 0  # Open front when approaching the 2nd ramp.

        if 520 <= self.bossDamage <= 720:
            return 1  # Open back on second hill.

        if 950 <= self.bossDamage <= 1000:
            return 0  # Open front at the ledge.

        # Not in any region, open random
        return random.choice([0, 1])

    def __sendDooberIds(self):
        dooberIds = []
        for suit in self.doobers:
            dooberIds.append(suit.doId)

        self.sendUpdate('setDooberIds', [dooberIds])

    def d_cagedToonBattleThree(self, index, avId):
        self.sendUpdate('cagedToonBattleThree', [index, avId])

    def formatReward(self):
        return str(self.cagedToonNpcId)

    def makeBattleOneBattles(self):
        self.postBattleState = 'RollToBattleTwo'
        self.initializeBattles(1, BossCogGlobals.SellbotBossBattleOnePosHpr)

    def generateSuits(self, battleNumber):
        if battleNumber == 1:
            return self.invokeSuitPlanner(self.battleOnePlanner, 0)
        else:
            return self.invokeSuitPlanner(self.battleTwoPlanner, 1)

    def removeToon(self, avId):
        toon = simbase.air.doId2do.get(avId)
        if toon:
            toon.b_setNumPies(0)
        DistributedBossCogAI.DistributedBossCogAI.removeToon(self, avId)

    def enterOff(self):
        DistributedBossCogAI.DistributedBossCogAI.enterOff(self)
        self.__resetDoobers()

    def enterElevator(self):
        DistributedBossCogAI.DistributedBossCogAI.enterElevator(self)
        self.b_setBossDamage(0, 0, 0)

    def enterIntroduction(self):
        self.calcAndSetBattleDifficulty()
        DistributedBossCogAI.DistributedBossCogAI.enterIntroduction(self)
        self.__makeDoobers()
        self.b_setBossDamage(0, 0, 0)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'vp', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)
        typeList = []
        typeList.append({'type': 'vp'})
        for toon in self.involvedToons:
            simbase.air.cogPageManager.toonEncounteredCogs(toon, typeList)

    def exitIntroduction(self):
        self.removeSkipButton()
        DistributedBossCogAI.DistributedBossCogAI.exitIntroduction(self)
        self.__resetDoobers()

    def enterRollToBattleTwo(self):
        self.divideToons()
        self.barrier = self.beginBarrier('RollToBattleTwo', self.involvedToons, 45, self.__doneRollToBattleTwo)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'vp', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def __doneRollToBattleTwo(self, avIds):
        self.b_setState('PrepareBattleTwo')

    def exitRollToBattleTwo(self):
        self.removeSkipButton()
        self.ignoreBarrier(self.barrier)

    def enterPrepareBattleTwo(self):
        self.barrier = self.beginBarrier('PrepareBattleTwo', self.involvedToons, 30, self.__donePrepareBattleTwo)
        self.calcAndSetBattleDifficulty()
        self.makeBattleTwoBattles()

    def __donePrepareBattleTwo(self, avIds):
        self.b_setState('BattleTwo')

    def exitPrepareBattleTwo(self):
        self.ignoreBarrier(self.barrier)

    def makeBattleTwoBattles(self):
        self.postBattleState = 'PrepareBattleThree'
        self.initializeBattles(2, BossCogGlobals.SellbotBossBattleTwoPosHpr)

    def enterBattleTwo(self):
        if self.battleA:
            self.battleA.startBattle(self.toonsA, self.suitsA)
        if self.battleB:
            self.battleB.startBattle(self.toonsB, self.suitsB)

    def exitBattleTwo(self):
        self.resetBattles()

    def enterPrepareBattleThree(self):
        self.barrier = self.beginBarrier('PrepareBattleThree', self.involvedToons, 30, self.__donePrepareBattleThree)
        self.calcAndSetBattleDifficulty()

    def __donePrepareBattleThree(self, avIds):
        self.b_setState('BattleThree')

    def exitPrepareBattleThree(self):
        self.ignoreBarrier(self.barrier)

    def enterBattleThree(self):
        self.resetBattles()
        self.takeAwayPies()  # It's possible to take in pies from vinny
        self.setPieType()
        self.b_setBossDamage(0, 0, 0)
        self.battleThreeStart = globalClock.getFrameTime()
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.__touchedCage = 0
                # Getting Pies Tip
                toon.showToonTip(TTE.TIP_VP_GET_PIES)

        self.waitForNextAttack(5)
        self.waitForNextStrafe(9)
        self.cagedToonDialogIndex = 100
        self.__saySomethingLater()

    def __saySomething(self, task = None):
        index = None
        avId = 0
        if len(self.involvedToons) == 0:
            return
        avId = random.choice(self.involvedToons)
        toon = simbase.air.doId2do.get(avId)
        if toon.__touchedCage:
            if self.cagedToonDialogIndex <= TTLocalizer.CagedToonBattleThreeMaxAdvice:
                index = self.cagedToonDialogIndex
                self.cagedToonDialogIndex += 1
            elif random.random() < 0.2:
                index = random.randrange(100, TTLocalizer.CagedToonBattleThreeMaxAdvice + 1)
        else:
            index = random.randrange(20, TTLocalizer.CagedToonBattleThreeMaxTouchCage + 1)
        if index:
            self.d_cagedToonBattleThree(index, avId)
        self.__saySomethingLater()

    def __saySomethingLater(self, delayTime = 15):
        taskName = self.uniqueName('CagedToonSaySomething')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(delayTime, self.__saySomething, taskName)

    def __goodJump(self, avId):
        currState = self.getCurrentOrNextState()
        if currState != 'BattleThree':
            return
        index = random.randrange(10, TTLocalizer.CagedToonBattleThreeMaxGivePies + 1)
        self.d_cagedToonBattleThree(index, avId)
        self.__saySomethingLater()

    def exitBattleThree(self):
        self.stopAttacks()
        self.stopStrafes()
        taskName = self.uniqueName('CagedToonSaySomething')
        taskMgr.remove(taskName)

    def zapToon(self, x, y, z, h, p, r, bpx, bpy, attackCode, timestamp):
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
            damage = math.floor(damage)
            self.damageToon(toon, damage)
            currState = self.getCurrentOrNextState()
            if attackCode == BossCogGlobals.BossCogElectricFence and (currState == 'RollToBattleTwo' or currState == 'BattleThree'):
                if bpy < 0 and abs(bpx / bpy) > 0.5:
                    if bpx < 0:
                        if self.attackCode in self.noSwipeAttackCodes:
                            return
                        self.b_setAttackCode(BossCogGlobals.BossCogSwatRight)
                    else:
                        if self.attackCode in self.noSwipeAttackCodes:
                            return
                        self.b_setAttackCode(BossCogGlobals.BossCogSwatLeft)

    def enterNearVictory(self):
        self.resetBattles()

    def exitNearVictory(self):
        pass

    def enterVictory(self):
        self.resetBattles()
        self.suitsKilled.append({'type': 'vp',
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
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 10, self.__doneVictory)

    def __doneVictory(self, avIds):
        self.notify.info("LogStats SellbotBossWasDefeated")
        for toonId in self.involvedToons:
            self.notify.info("LogStats ToonDefeatedSellbotBoss toonid %s" % toonId)
            toon = self.air.doId2do.get(toonId)
            if not toon:
                continue
            numReward = self.numIOUs
            # Add dept exp bonus for winning the boss
            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_SELLBOT)
            toon.addDepartmentExp(1000 * mult, ToontownGlobals.DEPARTMENT_SELLBOT)

            departmentLevel = toon.getDepartmentLevel(ToontownGlobals.DEPARTMENT_SELLBOT)
            if departmentLevel == ToontownGlobals.MaxDepartmentLevel[ToontownGlobals.DEPARTMENT_SELLBOT]:
                numReward += 1
            numReward = toon.applyBoosters([BoosterItemType.Reward_Boss_Global, BoosterItemType.Reward_Boss_Sellbot,
                                            BoosterItemType.Reward_Boss_Sellbot_Double], numReward)
            # Every boss always rewards 1 singular Rain
            rewards = [IOUItemType.AllBoost] + self.giveRewards[:numReward]
            self.toonRewards[toonId] = rewards

            # send the toon their specific rewards for the epilogue
            self.sendUpdateToAvatarId(toonId, 'setRewards', [rewards])

            # Handle toon unite rewards
            self.handleUniteRewards(toon)

            for reward in rewards:
                if not toon.getHammerspace().addItem(reward):
                    self.notify.info(
                        '%s.unable to add NPCFriend %s to %s.' % (self.doId, self.cagedToonNpcId, toonId)
                    )
            toon.b_promote(self.deptIndex)
            if toon.cogTypes[self.deptIndex] == 7 and toon.cogLevels[self.deptIndex] >= 7:
                toon.getHammerspace().addItem(BackgroundItemType.HQ_Sellbot)
            # Promotion + Reward Tips
            toon.showToonTip(TTE.TIP_DISGUISE_PROMOTION)
            toon.showToonTip(TTE.TIP_REWARDS_IOU)
            # Unite tip
            toon.showToonTip(TTE.TIP_REWARDS_UNITE)

            if self.begunToonAmount == 1:
                self.notify.info("LogStats ToonSoloDefeatedSellbotBoss toonid %s" % toonId)
            self.air.achievementsManager.vp(toonId, numPlayers=self.begunToonAmount)

            # Handle boss specific quests
            simbase.air.quest3Manager.progressObjective(
                toon,
                CogBossContext(
                    "s",
                    self.toonStunsDict.get(toonId, 0),
                    self.toonDamagesDict.get(toonId, 0),
                )
            )
            simbase.air.quest3Manager.progressObjective(
                toon,
                TossPieContext(
                    self.toonPiesThrownDict.get(toonId, 0),
                    4,
                    SpecialQuestZones.SellbotBoss,
                ),
            )

        self.prepareReward()
        self.rewardClubCoins()

    def exitVictory(self):
        self.takeAwayPies()

    def enterFrolic(self):
        DistributedBossCogAI.DistributedBossCogAI.enterFrolic(self)
        self.b_setBossDamage(0, 0, 0)

    def __resetDoobers(self):
        for suit in self.doobers:
            suit.requestDelete()

        self.doobers = []

    def __makeDoobers(self):
        self.__resetDoobers()
        for i in range(8):
            suit = DistributedSuitAI.DistributedSuitAI(self.air, None)
            level = random.randrange(len(SuitDNA.suitsPerLevel))
            suit.dna = SuitDNA.SuitDNA()
            suit.dna.newSuitRandom(level=level, dept=self.dna.dept)
            suit.setLevel(level)
            suit.generateWithRequired(self.zoneId)
            self.doobers.append(suit)

        self.__sendDooberIds()

    def setPieType(self):
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.d_setPieType(4)

    def takeAwayPies(self):
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.b_setNumPies(0)

    def __recordHit(self):
        now = globalClock.getFrameTime()
        self.hitCount += 1
        self.chatOnHit()
        if self.hitCount < self.limitHitCount or self.bossDamage < self.hitCountDamage:
            return
        self.b_setAttackCode(BossCogGlobals.BossCogRecoverDizzyAttack)

    def enterEpilogue(self):
        super().enterEpilogue()

        for toonId, rewards in self.toonRewards.items():
            toon: DistributedToonAI = simbase.air.getDo(toonId)
            if not toon:
                continue

    def calcAndSetBattleDifficulty(self):
        self.getToonDifficulty()
        self.universalUnites = 2
        self.numPies = 30
        self.pieHealAmt = 3
        self.battleOnePlanner = SuitBuildingGlobals.SPE.VP
        self.battleTwoPlanner = SuitBuildingGlobals.SPE.VP_SKELECOGS
        self.numIOUs = 3
