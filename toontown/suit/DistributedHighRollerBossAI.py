from pandac.PandaModules import *
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import ToontownGlobals
from toontown.battle import DistributedBattleMinibossAI
from toontown.suit import DistributedMinibossAI
from toontown.building import SuitPlannerInteriorAI
from toontown.battle import BattleExperienceAI
from direct.fsm import FSM
from toontown.suit import DistributedBossCogAI
from otp.avatar import DistributedAvatarAI
from toontown.suit import SuitDNA
import random
from otp.ai.MagicWordGlobal import *
from toontown.building import SuitBuildingGlobals
import math

class DistributedHighRollerBossAI(DistributedMinibossAI.DistributedMinibossAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedHighRollerBossAI')
    maxGoons = 8

    def __init__(self, air):
        DistributedMinibossAI.DistributedMinibossAI.__init__(self, air, 'm')
        FSM.FSM.__init__(self, 'DistributedHighRollerBossAI')
        self.cranes = []
        self.safes = []
        self.goons = []
        self.treasures = {}
        self.grabbingTreasures = {}
        self.recycledTreasures = []
        self.battleDifficulty = 0
        self.goonMinStrength = 7
        self.goonMaxStrength = 30
        self.healAmount = 0
        self.rewardId = 0
        self.rewardedToons = []
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
        self.bossMaxDamage = ToontownGlobals.CashbotBossMaxDamage
        self.maxHP = self.bossMaxDamage
        self.knockoutDamage = ToontownGlobals.CashbotBossKnockoutDamage
        # The custom High Roller instance ends after the High Roller Cog battle.
        # These guards keep the normal reward bookkeeping from running twice
        # if an administrator still forces the legacy Victory state.
        self.highRollerBossKillRecorded = False
        self.highRollerRewardsGranted = False

    def enterWaitForToons(self):
        # The Major Player sigils already provide the boarding/teleport movie,
        # so there is no CFO Elevator state here.  Give slower clients enough
        # time to finish quietZone and teleportIn before beginning the intro.
        self.acceptNewToons()
        if len(self.involvedToons) == 1:
            self.begunSolo = True
        self.barrier = self.beginBarrier(
            'WaitForToons', self.involvedToons, 120,
            self.__doneHighRollerWaitForToons)

    def __doneHighRollerWaitForToons(self, avIds):
        self.b_setState('Introduction')

    def generate(self):
        DistributedMinibossAI.DistributedMinibossAI.generate(self)
        if __dev__:
            self.scene.reparentTo(self.getRender())

    def getHoodId(self):
        # This is a temporary Major Player room hosted under MML, not a Cog HQ.
        return ToontownGlobals.MinniesMelodyland

    def __chooseResistanceRewardId(self):
        # Retained only for DC/API compatibility.  High Roller grants no Unite.
        return 0

    def formatReward(self):
        return str(self.rewardId)

    def getBattleAPosHpr(self):
        return ToontownGlobals.HighRollerBossCogBattleAPosHpr

    def getBattleBPosHpr(self):
        return ToontownGlobals.HighRollerBossCogBattleBPosHpr

    def makeBattleOneBattles(self):
        # The High Roller Cog battle is the only battle in this instance.
        # Skip the old crf2 placeholder Flunky battle and continue directly
        # into the normal reward sequence when BattleOne finishes.
        self.postBattleState = 'Reward'
        self.initializeBattles(1, ToontownGlobals.HighRollerBossBattleOnePosHpr)

    def generateSuits(self, battleNumber):
        if battleNumber == 1:
            cogs = self.invokeEmptyPlanner(11, 'crf1')
            activeSuits = cogs['activeSuits']
            reserveSuits = cogs['reserveSuits']
            while len(activeSuits) >= 6:
                suit = activeSuits.pop()
                reserveSuits.append((suit, 100))

            def compareJoinChance(a, b):
                return cmp(a[1], b[1])

            reserveSuits.sort(compareJoinChance)
            return {'activeSuits': activeSuits,
                    'reserveSuits': reserveSuits}
        if battleNumber == 2:
            cogs = self.invokeEmptyPlanner(11, 'crf2')
            activeSuits = cogs['activeSuits']
            reserveSuits = cogs['reserveSuits']
            while len(activeSuits) >= 6:
                suit = activeSuits.pop()
                reserveSuits.append((suit, 100))

            def compareJoinChance(a, b):
                return cmp(a[1], b[1])

            reserveSuits.sort(compareJoinChance)
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

    def removeToon(self, avId):
        if self.cranes != None:
            for crane in self.cranes:
                crane.removeToon(avId)

        if self.safes != None:
            for safe in self.safes:
                safe.removeToon(avId)

        if self.goons != None:
            for goon in self.goons:
                goon.removeToon(avId)

        DistributedMinibossAI.DistributedMinibossAI.removeToon(self, avId)

    def __makeBattleThreeObjects(self):
        # The standalone High Roller instance has no CFO crane-round objects.
        self.cranes = []
        self.safes = []
        self.goons = []

    def __resetBattleThreeObjects(self):
        self.cranes = []
        self.safes = []
        self.goons = []

    def __deleteBattleThreeObjects(self):
        # Delete any stale objects received from a mixed server, then keep the
        # collections empty for the lifetime of this miniboss.
        for objects in (self.cranes, self.safes, self.goons):
            for obj in objects or []:
                try:
                    obj.request('Off')
                except:
                    pass
                try:
                    obj.requestDelete()
                except:
                    pass
        self.cranes = []
        self.safes = []
        self.goons = []

    def doNextAttack(self, task):
        if self.attackCode == ToontownGlobals.BossCogDizzyNow:
            attackCode = ToontownGlobals.BossCogRecoverDizzyAttack
        else:
            attackCode = random.choice([ToontownGlobals.BossCogAreaAttack,
                                        ToontownGlobals.BossCogFrontAttack,
                                        ToontownGlobals.BossCogSlowDirectedAttack])
        if attackCode == ToontownGlobals.BossCogAreaAttack:
            self.__doAreaAttack()
            self.waitForNextAttack(10)
        elif attackCode == ToontownGlobals.BossCogSlowDirectedAttack:
            self.__doDirectedAttack()
            self.waitForNextAttack(10)
        elif attackCode == ToontownGlobals.BossCogRecoverDizzyAttack:
            self.b_setAttackCode(ToontownGlobals.BossCogRecoverDizzyAttack)
            self.waitForNextAttack(10)
        elif attackCode == ToontownGlobals.BossCogFrontAttack:
            self.b_setAttackCode(ToontownGlobals.BossCogFrontAttack)
            self.waitForNextAttack(10)
        elif attackCode == ToontownGlobals.BossCogGolfAreaAttack:
            self.__doGolfAreaAttack()
            self.waitForNextAttack(10)
        else:
            self.b_setAttackCode(attackCode)

    def __doAreaAttack(self):
        self.b_setAttackCode(ToontownGlobals.BossCogAreaAttack)

    def __doDirectedAttack(self):
        if self.toonsToAttack:
            toonId = self.toonsToAttack.pop(0)
            while toonId not in self.involvedToons:
                if not self.toonsToAttack:
                    self.b_setAttackCode(ToontownGlobals.BossCogNoAttack)
                    return
                toonId = self.toonsToAttack.pop(0)

            self.toonsToAttack.append(toonId)
            self.b_setAttackCode(ToontownGlobals.BossCogSlowDirectedAttack, toonId)

    def reprieveToon(self, avId):
        if avId in self.toonsToAttack:
            i = self.toonsToAttack.index(avId)
            del self.toonsToAttack[i]
            self.toonsToAttack.append(avId)

    def makeTreasure(self, goon):
        # No CFO goons or crane-round treasures exist in this instance.
        return

    def grabAttempt(self, avId, treasureId):
        av = self.air.doId2do.get(avId)
        if not av:
            return
        treasure = self.treasures.get(treasureId)
        if treasure:
            if treasure.validAvatar(av):
                del self.treasures[treasureId]
                treasure.d_setGrab(avId)
                self.grabbingTreasures[treasureId] = treasure
                taskMgr.doMethodLater(5, self.__recycleTreasure, treasure.uniqueName('recycleTreasure'), extraArgs=[treasure])
            else:
                treasure.d_setReject()

    def __recycleTreasure(self, treasure):
        if treasure.doId in self.grabbingTreasures:
            del self.grabbingTreasures[treasure.doId]
            self.recycledTreasures.append(treasure)

    def deleteAllTreasures(self):
        for treasure in self.treasures.values():
            treasure.requestDelete()

        self.treasures = {}
        for treasure in self.grabbingTreasures.values():
            taskMgr.remove(treasure.uniqueName('recycleTreasure'))
            treasure.requestDelete()

        self.grabbingTreasures = {}
        for treasure in self.recycledTreasures:
            treasure.requestDelete()

        self.recycledTreasures = []

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

    def makeGoon(self, side=None):
        # No distributed CFO goons may be generated for High Roller.
        return None

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
        if self.attackCode != ToontownGlobals.BossCogDizzy:
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
        if self.heldObject == None:
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
        if then == None or now - then > 300:
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
            self.recordHit(damage)

    def magicWordReset(self):
        if self.state == 'BattleThree':
            self.__resetBattleThreeObjects()

    def magicWordResetGoons(self):
        if self.state == 'BattleThree':
            if self.goons != None:
                for goon in self.goons:
                    goon.request('Off')
                    goon.requestDelete()

                self.goons = None
            self.__makeBattleThreeObjects()

    def recordHit(self, damage):
        avId = self.air.getAvatarIdFromSender()
        if not self.validate(avId, avId in self.involvedToons, 'recordHit from unknown avatar'):
            return
        if self.state != 'BattleThree':
            return
        self.b_setBossDamage(self.bossDamage + damage)
        healthDisp = int(self.bossMaxDamage - self.bossDamage)
        if healthDisp < 0:
           healthDisp = 0
        #self.setHealthTag(str(healthDisp) + '/' + str(int(self.bossMaxDamage)))
        if self.bossDamage >= self.bossMaxDamage:
            self.b_setState('Victory')
        elif self.attackCode != ToontownGlobals.BossCogDizzy:
            if damage >= self.knockoutDamage:
                self.b_setAttackCode(ToontownGlobals.BossCogDizzy)
                self.stopHelmets()
            else:
                self.b_setAttackCode(ToontownGlobals.BossCogNoAttack)
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

    def d_setRewardId(self, rewardId):
        self.sendUpdate('setRewardId', [rewardId])

    def applyReward(self):
        # No ResistanceChat effect, promotion unite, or CFO staff event belongs
        # to the High Roller miniboss.  Acknowledge once for old clients only.
        avId = self.air.getAvatarIdFromSender()
        if avId in self.involvedToons and avId not in self.rewardedToons:
            self.rewardedToons.append(avId)

    def enterOff(self):
        DistributedMinibossAI.DistributedMinibossAI.enterOff(self)
        self.rewardedToons = []
        self.highRollerBossKillRecorded = False
        self.highRollerRewardsGranted = False

    def exitOff(self):
        DistributedMinibossAI.DistributedMinibossAI.exitOff(self)

    def enterIntroduction(self):
        DistributedMinibossAI.DistributedMinibossAI.enterIntroduction(self)
        self.calcAndSetBattleDifficulty()

    def exitIntroduction(self):
        DistributedMinibossAI.DistributedMinibossAI.exitIntroduction(self)

    def makeBattleTwoBattles(self):
        # This instance is battle-only.  Finishing the second Cog battle goes
        # straight to Reward instead of spawning the legacy CFO crane round.
        self.postBattleState = 'Reward'
        self.initializeBattles(2, ToontownGlobals.HighRollerBossBattleOnePosHpr)
        
    def enterPrepareBattleTwo(self):
        self.barrier = self.beginBarrier('PrepareBattleTwo', self.involvedToons, 350, self.__donePrepareBattleTwo)
        self.divideToons()
        self.makeBattleTwoBattles()
        self.calcAndSetBattleDifficulty()
        
    def __donePrepareBattleTwo(self, avIds):
        self.b_setState('BattleTwo')

    def exitPrepareBattleTwo(self):
        self.ignoreBarrier(self.barrier)
        self.__deleteBattleThreeObjects()
		
    def enterRollToBattleTwo(self):
        self.barrier = self.beginBarrier('RollToBattleTwo', self.involvedToons, 1, self.__doneRollToBattleTwo)
        
    def __doneRollToBattleTwo(self, avIds):
        self.b_setState('PrepareBattleTwo')

    def exitRollToBattleTwo(self):
        self.ignoreBarrier(self.barrier)
        
    def enterBattleTwo(self):
        if self.battle:
            self.battle.startBattle(self.toons, self.suits)

    def exitBattleTwo(self):
        self.resetBattles()

    def enterPrepareBattleThree(self):
        # Redirect any stale/forced crane-round request to the normal reward.
        self.resetBattles()
        taskMgr.remove(self.uniqueName('removedHighRollerCraneRound'))
        taskMgr.doMethodLater(
            0.0, self.__redirectRemovedBattleThree,
            self.uniqueName('removedHighRollerCraneRound'))

    def __donePrepareBattleThree(self, avIds):
        self.b_setState('BattleThree')

    def exitPrepareBattleThree(self):
        taskMgr.remove(self.uniqueName('removedHighRollerCraneRound'))

    def enterBattleThree(self):
        # This state is retained in the DC/FSM contract only.  It creates no
        # cranes, safes, helmets, goons or attacks and immediately redirects.
        self.resetBattles()
        self.__deleteBattleThreeObjects()
        taskMgr.remove(self.uniqueName('removedHighRollerCraneRound'))
        taskMgr.doMethodLater(
            0.0, self.__redirectRemovedBattleThree,
            self.uniqueName('removedHighRollerCraneRound'))

    def __redirectRemovedBattleThree(self, task):
        if self.state in ('PrepareBattleThree', 'BattleThree'):
            self.b_setState('Reward')
        return task.done

    def getToonDifficulty(self):
        totalCogSuitTier = 0
        totalToons = 0

        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                totalToons += 1
                totalCogSuitTier += toon.cogTypes[2]

        averageTier = math.floor(totalCogSuitTier / totalToons) + 1
        return int(averageTier)
		
    def b_setBonusUnites(self, unites):
        self.setBonusUnites(unites)
        self.d_setBonusUnites(unites)

    def setBonusUnites(self, unites):
        self.bonusUnites = unites

    def d_setBonusUnites(self, unites):
        self.sendUpdate('setBonusUnites', [unites])

    def calcAndSetBattleDifficulty(self):
        self.toonLevels = self.getToonDifficulty()
        battleDifficulty = int(self.toonLevels)
        self.b_setBattleDifficulty(battleDifficulty)
        self.recalcDifficulty()
		
    def recalcDifficulty(self):
        self.b_setMaxHp(ToontownGlobals.CashbotBossMaxDamage)
        self.goonMinStrength = 12
        self.goonMaxStrength = 43
        self.goonMinScale = 1.0
        self.goonMaxScale = 2.6
        self.knockoutDamage = ToontownGlobals.CashbotBossKnockoutDamage
        self.b_setBonusUnites(0)

    def b_setBattleDifficulty(self, batDiff):
        self.setBattleDifficulty(batDiff)
        self.d_setBattleDifficulty(batDiff)

    def setBattleDifficulty(self, batDiff):
        self.battleDifficulty = batDiff

    def d_setBattleDifficulty(self, batDiff):
        self.sendUpdate('setBattleDifficulty', [batDiff])

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
        taskMgr.remove(self.uniqueName('removedHighRollerCraneRound'))
        self.__deleteBattleThreeObjects()
        self.deleteAllTreasures()
        self.stopAttacks()
        self.stopGoons()
        self.stopHelmets()
        self.heldObject = None

    def __recordHighRollerBossKill(self):
        if self.highRollerBossKillRecorded:
            return
        self.highRollerBossKillRecorded = True
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

    def __grantHighRollerRewards(self):
        if self.highRollerRewardsGranted:
            return
        self.highRollerRewardsGranted = True
        self.__recordHighRollerBossKill()
        self.d_setBattleExperience()
        BattleExperienceAI.assignRewards(self.involvedToons, self.toonSkillPtsGained, self.suitsKilled, ToontownGlobals.dept2cogHQ(self.dept), self.helpfulToons)
        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                # High Roller is not a CFO battle.  Preserve battle XP,
                # promotion, statistics, and quest credit, but do not award
                # Resistance Unites or bonus unite messages.
                toon.b_promote(self.deptIndex)
                simbase.air.questManager.toonDefeatedBoss(toon, ToontownGlobals.dept2cogHQ(self.dept), self.dna.dept, self.involvedToons)

    def enterReward(self):
        # Normal High Roller completion arrives here directly from BattleOne.
        # Grant the standard battle bookkeeping, then show only the ordinary
        # reward movie.  High Roller does not award Resistance Unites.
        self.resetBattles()
        self.__grantHighRollerRewards()
        DistributedMinibossAI.DistributedMinibossAI.enterReward(self)

    def enterVictory(self):
        # Retained for administrator magic words and old clients, but normal
        # gameplay no longer enters this crane-round state.
        self.resetBattles()
        self.__recordHighRollerBossKill()
        self.barrier = self.beginBarrier('Victory', self.involvedToons, 30, self.__doneVictory)

    def __doneVictory(self, avIds):
        self.__grantHighRollerRewards()
        self.b_setState('Reward')

    def exitVictory(self):
        self.__deleteBattleThreeObjects()

    def enterEpilogue(self):
        # The client uses this state only as a direct return-to-MML transition.
        # There is no Mata Hairy dialogue or Resistance Unite sequence.
        DistributedMinibossAI.DistributedMinibossAI.enterEpilogue(self)


@magicWord(category=CATEGORY_ADMINISTRATOR)
def restartHighRollerRound():
    """
    Restarts the final round in the High Roller fight.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in simbase.air.doId2do.values():
        if isinstance(do, DistributedHighRollerBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in the High Roller fight!"
    boss.b_setState('Reward')
    return 'The High Roller has no crane round; moving to rewards.'


@magicWord(category=CATEGORY_ADMINISTRATOR)
def skipHighRoller():
    """
    Skips to the reward state of the High Roller fight.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in simbase.air.doId2do.values():
        if isinstance(do, DistributedHighRollerBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in the High Roller fight!"
    boss.b_setState('Reward')
    return 'Skipping to High Roller rewards...'

@magicWord(category=CATEGORY_PROGRAMMER)
def highRoller2():
    """
    Skips to the next round of the High Roller fight.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in simbase.air.doId2do.values():
        if isinstance(do, DistributedHighRollerBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in the High Roller fight!"
    boss.exitIntroduction()
    boss.b_setState('PrepareBattleTwo')
    return 'Skipping the first round...'

@magicWord(category=CATEGORY_PROGRAMMER)
def highRollerCutscene1():
    """
    Skips to the next round of the High Roller fight.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in simbase.air.doId2do.values():
        if isinstance(do, DistributedHighRollerBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in the High Roller fight!"
    boss.exitIntroduction()
    boss.b_setState('BattleOne')
    return 'Skipping first cutscene...'

@magicWord(category=CATEGORY_PROGRAMMER)
def killHighRoller():
    """
    Finishes the High Roller fight.
    """
    invoker = spellbook.getInvoker()
    boss = None
    for do in simbase.air.doId2do.values():
        if isinstance(do, DistributedHighRollerBossAI):
            if invoker.doId in do.involvedToons:
                boss = do
                break
    if not boss:
        return "You aren't in the High Roller fight!"
    boss.b_setState('Victory')
    return 'Killed High Roller.'
