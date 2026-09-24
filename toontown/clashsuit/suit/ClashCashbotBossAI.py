import math
import random
from typing import Optional

from panda3d.core import *
from direct.fsm import FSM

from toontown.clashsuit.suit import BossCogGlobals
from otp.ai.AIBaseGlobal import simbase
from toontown.building import ClashSuitBuildingGlobals
from toontown.coghq import (DistributedCashbotBossCraneAI,
                                      DistributedCashbotBossCraneFastAI,
                                      DistributedCashbotBossSafeAI,
                                      DistributedCashbotBossTreasureAI)
from toontown.coghq.DistributedCashbotBossObjectAI import \
    DistributedCashbotBossObjectAI
#from toontown.groups.GroupEnums import GroupType, Options
from toontown.instances import DistributedCutsceneSkipButtonAI
from toontown.inventory.enums.ItemEnums import BackgroundItemType, BoosterItemType, MaterialItemType
from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from toontown.quest3.context.CogBossContext import CashbotBossContext
from toontown.quest3.context.StompGoonContext import StompGoonContext
from toontown.clashsuit.suit import ClashBossCogAI, ClashCashbotBossGoonAI
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toon.gui.ToonTipGlobals import TTE


@DirectNotifyCategory()
class ClashCashbotBossAI(ClashBossCogAI.ClashBossCogAI, FSM.FSM):
    
    maxGoons = 8

   # groupType = GroupType.CFO

    def __init__(self, air):
        ClashBossCogAI.ClashBossCogAI.__init__(self, air, 'm')
        FSM.FSM.__init__(self, 'ClashCashbotBossAI')
        self.cranes = None
        self.safes = None
        self.goons = None
        self.treasures = {}
        self.battleOnePlanner = ClashSuitBuildingGlobals.SPE.CFO_HARD
        self.battleTwoPlanner = ClashSuitBuildingGlobals.SPE.CFO_SKELECOGS_HARD
        self.goonMinStrength = 7
        self.goonMaxStrength = 30
        self.healAmount = 0
        self.scene = NodePath('scene')
        self.reparentTo(self.scene)
        cn = CollisionNode('walls')
        cs = CollisionSphere(0, 0, 0, 13)
        cn.addSolid(cs)
        cs = CollisionInvSphere(0, 0, 0, 42)
        cn.addSolid(cs)
        self.attachNewNode(cn)
        self.heldObject = None
        self.waitingForHelmet = 0
        self.avatarHelmets = {}
        self.bossMaxDamage = BossCogGlobals.CashbotBossMaxDamage[0]
        self.knockoutDamage = BossCogGlobals.CashbotBossKnockoutDamage
        self.toonDamagesDict = {}
        self.toonSafeDamagesDict = {}
        self.toonGoonDamagesDict = {}
        self.toonUnstunnedGoonDamagesDict = {}
        self.toonStunsDict = {}
        self.toonGoonStompsDict = {}
        self.numStuns = 0
        self.maxTreasures = 35
        self.numCounterfeits = 1

    def generate(self):
        """
        Called when the DistributedObject is reintroduced to the world, either for the first time or from the cache.
        """
        ClashBossCogAI.ClashBossCogAI.generate(self)
        if __dev__:
            self.scene.reparentTo(self.getRender())

    def getContentSync(self) -> Optional[ContentSyncType]:
        return ContentSyncType.CBHQ

    def getHoodId(self):
        return ToontownGlobals.CashbotHQ

    def makeBattleOneBattles(self):
        self.postBattleState = 'RollToBattleTwo'
        self.initializeBattles(1, BossCogGlobals.CashbotBossBattleOnePosHpr)

    def generateSuits(self, battleNumber):
        if battleNumber == 1:
            return self.invokeSuitPlanner(self.battleOnePlanner, 0)
        else:
            return self.invokeSuitPlanner(self.battleTwoPlanner, 1)

    def removeToon(self, avId):
        if self.cranes is not None:
            for crane in self.cranes:
                crane.removeToon(avId)

        if self.safes is not None:
            for safe in self.safes:
                safe.removeToon(avId)

        if self.goons is not None:
            for goon in self.goons:
                goon.removeToon(avId)

        ClashBossCogAI.ClashBossCogAI.removeToon(self, avId)

    def __makeBattleThreeObjects(self):
        if self.cranes is None:
            self.cranes = []
            for index in range(len(BossCogGlobals.CashbotBossCranePosHprs)):
                if index <= 3:
                    crane = DistributedCashbotBossCraneAI.DistributedCashbotBossCraneAI(self.air, self, index)
                else:
                    crane = DistributedCashbotBossCraneFastAI.DistributedCashbotBossCraneFastAI(self.air, self, index)
                crane.generateWithRequired(self.zoneId)
                self.cranes.append(crane)

        if self.safes is None:
            self.safes = []
            for index in range(len(BossCogGlobals.CashbotBossSafePosHprs)):
                safe = DistributedCashbotBossSafeAI.DistributedCashbotBossSafeAI(self.air, self, index)
                safe.generateWithRequired(self.zoneId)
                self.safes.append(safe)

        if self.goons is None:
            self.goons = []

    def __resetBattleThreeObjects(self):
        if self.cranes is not None:
            for crane in self.cranes:
                crane.request('Free')

        if self.safes is not None:
            for safe in self.safes:
                safe.request('Initial')

    def __deleteBattleThreeObjects(self):
        if self.cranes is not None:
            for crane in self.cranes:
                crane.request('Off')
                crane.requestDelete()

            self.cranes = None
        if self.safes is not None:
            for safe in self.safes:
                safe.request('Off')
                safe.requestDelete()

            self.safes = None
        if self.goons is not None:
            for goon in self.goons:
                goon.request('Off')
                goon.requestDelete()

            self.goons = None

    def doNextAttack(self, task):
        self.__doDirectedAttack()
        if self.heldObject is None and not self.waitingForHelmet:
            self.waitForNextHelmet()

    def __doDirectedAttack(self):
        if self.toonsToAttack:
            toonId = self.toonsToAttack.pop(0)
            while toonId not in self.involvedToons:
                if not self.toonsToAttack:
                    self.b_setAttackCode(BossCogGlobals.BossCogNoAttack)
                    return
                toonId = self.toonsToAttack.pop(0)

            self.toonsToAttack.append(toonId)
            self.b_setAttackCode(BossCogGlobals.BossCogSlowCoinDirectedAttack, toonId)

    def reprieveToon(self, avId):
        if avId in self.toonsToAttack:
            i = self.toonsToAttack.index(avId)
            del self.toonsToAttack[i]
            self.toonsToAttack.append(avId)

    def makeTreasure(self, goon):
        if self.state != 'BattleThree':
            return
        if len(self.treasures) >= self.maxTreasures:
            return
        avId = self.air.getAvatarIdFromSender()
        pos = goon.getPos(self)
        v = Vec3(pos[0], pos[1], 0.0)
        if not v.normalize():
            v = Vec3(1, 0, 0)
        v = v * 27
        angle = random.uniform(0.0, 2.0 * math.pi)
        radius = 10
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        fpos = self.scene.getRelativePoint(self, Point3(v[0] + dx, v[1] + dy, 0))
        if goon.strength <= 10:
            style = random.choice([ToontownGlobals.ToontownCentral, ToontownGlobals.DonaldsDock, ToontownGlobals.YeOlde, ToontownGlobals.GoofySpeedway, ToontownGlobals.GolfZone, ToontownGlobals.DaisyGardens])
            healAmount = 4
        elif goon.strength <= 15:
            style = random.choice([ToontownGlobals.YeOlde, ToontownGlobals.GoofySpeedway, ToontownGlobals.GolfZone, ToontownGlobals.DaisyGardens, ToontownGlobals.MinniesMelodyland])
            healAmount = 8
        else:
            style = random.choice([ToontownGlobals.TheBrrrgh, ToontownGlobals.OutdoorZone, ToontownGlobals.DonaldsDreamland])
            healAmount = 12
        treasure = DistributedCashbotBossTreasureAI.DistributedCashbotBossTreasureAI(self.air, self, goon, style, fpos[0], fpos[1], 0)
        treasure.generateWithRequired(self.zoneId)
        treasure.healAmount = healAmount
        self.treasures[treasure.doId] = treasure

    def grabAttempt(self, avId, treasureId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        treasure = self.treasures.get(treasureId)
        if treasure:
            if treasure.validAvatar(av):
                treasure.d_setGrab(avId)
                taskMgr.doMethodLater(5, self.__deleteTreasure, treasure.uniqueName('deleteTreasure'), extraArgs=[treasure])
            else:
                treasure.d_setReject()

    def __deleteTreasure(self, treasure):
        if treasure.doId in self.treasures:
            del self.treasures[treasure.doId]
            treasure.requestDelete()

    def deleteAllTreasures(self):
        for treasure in list(self.treasures.values()):
            treasure.requestDelete()

        self.treasures = {}

    def getMaxGoons(self):
        t = self.getBattleThreeTime()
        if t <= 1.0:
            return self.maxGoons
        elif t <= 1.1:
            return self.maxGoons + 1
        elif t <= 1.2:
            return self.maxGoons + 2
        elif t <= 1.3:
            return self.maxGoons + 3
        elif t <= 1.4:
            return self.maxGoons + 4
        else:
            return self.maxGoons + 8

    def makeGoon(self, side = None):
        if side is None:
            side = random.choice(['EmergeA', 'EmergeB'])
        goon = self.__chooseOldGoon()
        if goon is None:
            if len(self.goons) >= self.getMaxGoons():
                return
            goon = ClashCashbotBossGoonAI.ClashCashbotBossGoonAI(self.air, self)
            goon.generateWithRequired(self.zoneId)
            self.goons.append(goon)
        if self.getBattleThreeTime() > 1.0:
            goon.STUN_TIME = 4
            goon.b_setupGoon(velocity=8, hFov=90, attackRadius=20, strength=self.goonMaxStrength, scale=2.0)
        else:
            goon.STUN_TIME = self.progressValue(30, 8)
            goon.b_setupGoon(velocity=self.progressRandomValue(3, 7), hFov=self.progressRandomValue(70, 80), attackRadius=self.progressRandomValue(6, 15), strength=int(self.progressRandomValue(self.goonMinStrength, self.goonMaxStrength)), scale=self.progressRandomValue(self.goonMinScale, self.goonMaxScale))
        goon.request(side)

    def __chooseOldGoon(self):
        for goon in self.goons:
            if goon.state == 'Off':
                return goon

    def waitForNextGoon(self, delayTime):
        currState = self.getCurrentOrNextState()
        if currState == 'BattleThree':
            taskName = self.uniqueName('NextGoon')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.doNextGoon, taskName)

    def stopGoons(self):
        taskName = self.uniqueName('NextGoon')
        taskMgr.remove(taskName)

    def doNextGoon(self, task):
        if self.attackCode != BossCogGlobals.BossCogDizzy:
            self.makeGoon()
        delayTime = self.progressValue(10, 2)
        self.waitForNextGoon(delayTime)

    def waitForNextHelmet(self):
        currState = self.getCurrentOrNextState()
        if currState == 'BattleThree':
            taskName = self.uniqueName('NextHelmet')
            taskMgr.remove(taskName)
            delayTime = self.progressValue(45, 15)
            taskMgr.doMethodLater(delayTime, self.__donHelmet, taskName)
            self.waitingForHelmet = 1

    def __donHelmet(self, task):
        self.waitingForHelmet = 0
        if self.heldObject is None:
            safe = self.safes[0]
            safe.request('Grabbed', self.doId, self.doId)
            self.heldObject = safe

    def stopHelmets(self):
        self.waitingForHelmet = 0
        taskName = self.uniqueName('NextHelmet')
        taskMgr.remove(taskName)

    def acceptHelmetFrom(self, avId):
        now = globalClock.getFrameTime()
        then = self.avatarHelmets.get(avId, None)
        if then is None or now - then > 300:
            self.avatarHelmets[avId] = now
            return 1
        return 0

    def magicWordHit(self, damage, avId):
        if self.heldObject:
            self.heldObject.demand('Dropped', avId, self.doId)
            self.heldObject.avoidHelmet = 1
            self.heldObject = None
            self.waitForNextHelmet()
        else:
            self.recordHit(int(damage), impact=None, craneId=None, magic=1)

    def magicWordReset(self):
        if self.state == 'BattleThree':
            self.__resetBattleThreeObjects()

    def magicWordResetGoons(self):
        if self.state == 'BattleThree':
            if self.goons is not None:
                for goon in self.goons:
                    goon.request('Off')
                    goon.requestDelete()

                self.goons = None
            self.__makeBattleThreeObjects()

    def recordHit(self, damage, impact, craneId, obj: DistributedCashbotBossObjectAI=None, magic=0):
        avId = self.air.getAvatarIdFromSender()
        crane = simbase.air.doId2do.get(craneId)
        if not self.validate(avId, avId in self.involvedToons, 'recordHit from unknown avatar'):
            return
        if self.state != 'BattleThree':
            return
        self.b_setBossDamage(self.bossDamage + damage)

        if isinstance(obj, DistributedCashbotBossSafeAI.DistributedCashbotBossSafeAI):
            self.toonSafeDamagesDict.setdefault(avId, 0)
            self.toonSafeDamagesDict[avId] += damage
        elif isinstance(obj, ClashCashbotBossGoonAI.ClashCashbotBossGoonAI):
            damageDict = self.toonUnstunnedGoonDamagesDict if not obj.stunGrabbed else self.toonGoonDamagesDict
            damageDict.setdefault(avId, 0)
            damageDict[avId] += damage

        if avId in self.toonDamagesDict:
            self.toonDamagesDict[avId] += damage
            toon = self.cr.doId2do.get(avId)
            if toon:
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
                toon.addDepartmentExp(math.ceil(1.5 * damage * mult), ToontownGlobals.DEPARTMENT_CASHBOT)
        else:
            self.toonDamagesDict[avId] = damage
            toon = self.cr.doId2do.get(avId)
            if toon:
                mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
                toon.addDepartmentExp(math.ceil(1.5 * damage * mult), ToontownGlobals.DEPARTMENT_CASHBOT)
        self.d_updateDamageDealt(avId, damage)
        if damage > self.bossMaxDamage / 3:
            self.chatOnHit()
        if self.bossDamage >= self.bossMaxDamage:
            self.b_setState('Victory')
        elif self.attackCode != BossCogGlobals.BossCogDizzy and not magic:
            if crane is not None:
                if damage >= self.knockoutDamage:
                    self.b_setAttackCode(BossCogGlobals.BossCogDizzy)
                    self.d_updateStunCount(avId)
                    self.numStuns += 1
                    if avId in self.toonStunsDict:
                        self.toonStunsDict[avId] += 1
                        stuns = self.toonStunsDict[avId]
                        toon = self.cr.doId2do.get(avId)
                        if toon:
                            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
                            toon.addDepartmentExp(math.ceil((250 + 400/(stuns+1)) * mult), ToontownGlobals.DEPARTMENT_CASHBOT)
                    else:
                        self.toonStunsDict[avId] = 1
                        stuns = self.toonStunsDict[avId]
                        toon = self.cr.doId2do.get(avId)
                        if toon:
                            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
                            toon.addDepartmentExp(math.ceil((250 + 400/(stuns+1)) * mult), ToontownGlobals.DEPARTMENT_CASHBOT)
                    for toonId in self.involvedToons:
                        toon = self.cr.doId2do.get(toonId)
                        mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
                        diminished_exp = math.ceil((1500/(self.numStuns+4)) * mult)
                        toon.addDepartmentExp(math.ceil(diminished_exp), ToontownGlobals.DEPARTMENT_CASHBOT)
                        # CFO is Stunned Tip
                        toon.showToonTip(TTE.TIP_CFO_STUNNED)
                    self.stopHelmets()
                elif crane.getIndex() > 3 and (impact > 0.8 or damage >= self.knockoutDamage):
                    self.b_setAttackCode(BossCogGlobals.BossCogDizzy)
                    self.d_updateStunCount(avId)
                    self.numStuns += 1
                    if avId in self.toonStunsDict:
                        self.toonStunsDict[avId] += 2
                        stuns = self.toonStunsDict[avId]
                        if toon:
                            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
                            toon.addDepartmentExp(math.ceil(2*(250 + 400/(stuns+1)) * mult), ToontownGlobals.DEPARTMENT_CASHBOT)
                    else:
                        self.toonStunsDict[avId] = 2
                        stuns = self.toonStunsDict[avId]
                        if toon:
                            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
                            toon.addDepartmentExp(math.ceil(2*(250 + 400/(stuns+1)) * mult), ToontownGlobals.DEPARTMENT_CASHBOT)
                    for toonId in self.involvedToons:
                        toon = self.cr.doId2do.get(toonId)
                        mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
                        diminished_exp = math.ceil((1500/(self.numStuns+4))*mult)
                        toon.addDepartmentExp(diminished_exp, ToontownGlobals.DEPARTMENT_CASHBOT)
                        # CFO is Stunned Tip
                        toon.showToonTip(TTE.TIP_CFO_STUNNED)
                    self.stopHelmets()
                else:
                    self.b_setAttackCode(BossCogGlobals.BossCogNoAttack)
                    self.stopHelmets()
                    self.waitForNextHelmet()

    def b_setBossDamage(self, bossDamage):
        self.d_setBossDamage(bossDamage)
        self.setBossDamage(bossDamage)

    def setBossDamage(self, bossDamage):
        self.reportToonHealth()
        self.bossDamage = bossDamage

    def d_setBossDamage(self, bossDamage):
        self.sendUpdate('setBossDamage', [bossDamage])

    def d_updateDamageDealt(self, avId, damageDealt):
        self.sendUpdate('updateDamageDealt', [avId, damageDealt])

    def d_updateStunCount(self, avId):
        self.sendUpdate('updateStunCount', [avId])
    
    def d_updateGoonsStomped(self, avId):
        self.sendUpdate('updateGoonsStomped', [avId])

    def enterOff(self):
        ClashBossCogAI.ClashBossCogAI.enterOff(self)

    def exitOff(self):
        ClashBossCogAI.ClashBossCogAI.exitOff(self)

    def enterIntroduction(self):
        self.calcAndSetBattleDifficulty()
        ClashBossCogAI.ClashBossCogAI.enterIntroduction(self)
        self.__makeBattleThreeObjects()
        self.__resetBattleThreeObjects()
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'cfo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)
        typeList = []
        typeList.append({'type': 'cfo'})
        for toon in self.involvedToons:
            simbase.air.cogPageManager.toonEncounteredCogs(toon, typeList)

    def exitIntroduction(self):
        self.removeSkipButton()
        ClashBossCogAI.ClashBossCogAI.exitIntroduction(self)
        self.__deleteBattleThreeObjects()

    def makeBattleTwoBattles(self):
        self.postBattleState = 'PrepareBattleThree'
        self.initializeBattles(2, BossCogGlobals.CashbotBossBattleThreePosHpr)

    def enterPrepareBattleTwo(self):
        self.barrier = self.beginBarrier('PrepareBattleTwo', self.involvedToons, 45, self.__donePrepareBattleTwo)
        self.divideToons()
        self.makeBattleTwoBattles()
        self.__makeBattleThreeObjects()
        self.__resetBattleThreeObjects()
        self.calcAndSetBattleDifficulty()
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'cfo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def __donePrepareBattleTwo(self, avIds):
        self.b_setState('BattleTwo')

    def exitPrepareBattleTwo(self):
        self.removeSkipButton()
        self.ignoreBarrier(self.barrier)
        self.__deleteBattleThreeObjects()

    def enterRollToBattleTwo(self):
        self.barrier = self.beginBarrier('RollToBattleTwo', self.involvedToons, 1, self.__doneRollToBattleTwo)

    def __doneRollToBattleTwo(self, avIds):
        self.b_setState('PrepareBattleTwo')

    def exitRollToBattleTwo(self):
        self.ignoreBarrier(self.barrier)

    def enterBattleTwo(self):
        if self.battleA:
            self.battleA.startBattle(self.toonsA, self.suitsA)
        if self.battleB:
            self.battleB.startBattle(self.toonsB, self.suitsB)

    def exitBattleTwo(self):
        self.resetBattles()

    def enterPrepareBattleThree(self):
        self.resetBattles()
        self.__makeBattleThreeObjects()
        self.__resetBattleThreeObjects()
        self.calcAndSetBattleDifficulty()
        self.barrier = self.beginBarrier('PrepareBattleThree', self.involvedToons, 55, self.__donePrepareBattleThree)
        self.skipButton = DistributedCutsceneSkipButtonAI.DistributedCutsceneSkipButtonAI(self.air, 'cfo', self.involvedToons)
        self.skipButton.generateWithRequired(self.zoneId)

    def __donePrepareBattleThree(self, avIds):
        self.b_setState('BattleThree')

    def exitPrepareBattleThree(self):
        self.removeSkipButton()
        if self.newState != 'BattleThree':
            self.__deleteBattleThreeObjects()
        self.ignoreBarrier(self.barrier)

    def enterBattleThree(self):
        self.setPosHpr(*BossCogGlobals.CashbotBossBattleThreePosHpr)
        self.__makeBattleThreeObjects()
        self.__resetBattleThreeObjects()
        self.reportToonHealth()
        self.toonsToAttack = self.involvedToons[:]
        random.shuffle(self.toonsToAttack)
        self.b_setBossDamage(0)
        self.battleThreeStart = globalClock.getFrameTime()
        self.resetBattles()
        self.waitForNextAttack(15)
        self.waitForNextHelmet()
        self.makeGoon(side='EmergeA')
        self.makeGoon(side='EmergeB')
        taskName = self.uniqueName('NextGoon')
        taskMgr.remove(taskName)
        taskMgr.doMethodLater(2, self.__doInitialGoons, taskName)

    def calcAndSetBattleDifficulty(self):
        self.getToonDifficulty()
        self.universalUnites = 2
        self.numCounterfeits = 16
        self.b_setMaxHp(BossCogGlobals.CashbotBossMaxDamage[2])
        self.goonMinStrength = 8
        self.goonMaxStrength = 38
        self.goonMinScale = 0.8
        self.goonMaxScale = 2.4
        self.knockoutDamage = BossCogGlobals.CashbotBossKnockoutDamage * 2
        self.maxTreasures = 25
        self.battleOnePlanner = ClashSuitBuildingGlobals.SPE.CFO_HARD
        self.battleTwoPlanner = ClashSuitBuildingGlobals.SPE.CFO_SKELECOGS_HARD

    def b_setMaxHp(self, hp):
        self.setMaxHp(hp)
        self.d_setMaxHp(hp)

    def setMaxHp(self, hp):
        self.bossMaxDamage = hp

    def d_setMaxHp(self, hp):
        self.sendUpdate('setMaxHp', [hp])

    def __doInitialGoons(self, task):
        self.makeGoon(side='EmergeA')
        self.makeGoon(side='EmergeB')
        self.waitForNextGoon(10)

    def exitBattleThree(self):
        helmetName = self.uniqueName('helmet')
        taskMgr.remove(helmetName)
        if self.newState != 'Victory':
            self.__deleteBattleThreeObjects()
        self.deleteAllTreasures()
        self.stopAttacks()
        self.stopGoons()
        self.stopHelmets()
        self.heldObject = None

    def enterVictory(self):
        self.resetBattles()
        self.suitsKilled.append({'type': 'cfo',
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

    def __doneVictory(self, avIds):
        self.notify.info("LogStats CashbotBossWasDefeated")

        for toonId in self.involvedToons:
            self.notify.info("LogStats ToonDefeatedCashbotBoss toonid %s" % toonId)
            toon = self.air.doId2do.get(toonId)
            if not toon:
                continue
            # Add dept exp bonus for winning the boss
            mult = toon.getDeptExpMult(ToontownGlobals.DEPARTMENT_CASHBOT)
            toon.addDepartmentExp(1000 * mult, ToontownGlobals.DEPARTMENT_CASHBOT)

            self.handleUniteRewards(toon)
            self.giveCounterfeitReward(toon, toonId)
            toon.b_promote(self.deptIndex)
            if toon.cogTypes[self.deptIndex] == 7 and toon.cogLevels[self.deptIndex] >= 7:
                toon.getHammerspace().addItem(BackgroundItemType.HQ_Cashbot)
            # Promotion + Reward Tips
            toon.showToonTip(TTE.TIP_DISGUISE_PROMOTION)
            toon.showToonTip(TTE.TIP_REWARDS_COUNTERFEITS)
            # Unite tip
            toon.showToonTip(TTE.TIP_REWARDS_UNITE)

            if self.begunToonAmount == 1:
                self.notify.info("LogStats ToonSoloDefeatedCashbotBoss toonid %s" % toonId)
            self.air.achievementsManager.cfo(toonId, numPlayers=self.begunToonAmount)

            # Handle boss specific quests
            simbase.air.quest3Manager.progressObjective(
                toon, 
                CashbotBossContext(
                    "m",
                    self.toonStunsDict.get(toonId, 0),
                    self.toonDamagesDict.get(toonId, 0),
                    self.toonSafeDamagesDict.get(toonId, 0),
                    self.toonGoonDamagesDict.get(toonId, 0),
                    self.toonUnstunnedGoonDamagesDict.get(toonId, 0)
                )
            )
            simbase.air.quest3Manager.progressObjective(
                toon,
                StompGoonContext(
                    self.toonGoonStompsDict.get(toonId, 0), 
                    ToontownGlobals.CashbotLobby
                )
            )
        
        self.prepareReward()
        self.rewardClubCoins()

    def giveCounterfeitReward(self, toon, toonId):
        # Give the toon the needed bonuses depending on dept level, holiday, and daily bonus.
        bonusSlips = 0
        departmentLevel = toon.getDepartmentLevel(ToontownGlobals.DEPARTMENT_CASHBOT)
        if departmentLevel == ToontownGlobals.MaxDepartmentLevel[ToontownGlobals.DEPARTMENT_CASHBOT]:
            bonusSlips += 4
        bonusSlips = toon.applyBoosters([BoosterItemType.Reward_Boss_Global, BoosterItemType.Reward_Boss_Cashbot], bonusSlips)
        # toon.queueScavenge(self.numCounterfeits + bonusSlips, ScavengeType.Counterfeits, [])
        toon.getHammerspace().addItem(MaterialItemType.Counterfeits, self.numCounterfeits + bonusSlips)
        self.d_setNumCounterfeitsEarned(toonId, self.numCounterfeits + bonusSlips)

    def d_setNumCounterfeitsEarned(self, toonId, numCounterfeits):
        # Inform the client of the gained counterfeits for mata's victory dialogue.
        self.sendUpdate('setNumCounterfeitsEarned', [toonId, numCounterfeits])

    def exitVictory(self):
        self.__deleteBattleThreeObjects()

    def enterEpilogue(self):
        ClashBossCogAI.ClashBossCogAI.enterEpilogue(self)
