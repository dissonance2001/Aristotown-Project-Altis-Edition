import math
import random
from typing import Optional
from collections import Counter

from toontown.inventory.registry import UniteRegistry
from toontown.clashsuit.suit import BossCogGlobals
from toontown.modifiers.contentsync.ContentSyncApplierAI import ContentSyncApplierAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.distributed.MsgTypes import CLIENTAGENT_EJECT
from direct.distributed.PyDatagram import PyDatagram
from panda3d.core import ConfigVariableBool, NodePath
from direct.showbase.MessengerGlobal import messenger
from direct.task.TaskManagerGlobal import taskMgr

from otp.avatarimport DistributedAvatarAI
from toontown.clashbattle.battle import BattleBase
from toontown.clashbattle.battle import BattleExperienceAI
from toontown.clashbattle.battle.distributed import ClashBattleFinalAI
from toontown.building import SuitPlannerInteriorAI
from toontown.groups.GroupClasses import GroupAI
from toontown.groups.GroupEnums import Options
from toontown.hood import ZoneUtil
from toontown.clashsuit.suit import SuitDNA
from toontown.toonbase import TTLocalizer, RealmGlobals
from toontown.clashbattle.battle import BattleGlobals
from toontown.toonbase import ToontownGlobals

AllBossCogs = []


@DirectNotifyCategory()
class ClashBossCogAI(DistributedAvatarAI.DistributedAvatarAI, ContentSyncApplierAI):
    groupType = None

    def __init__(self, air, dept):
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        self.dept = dept
        self.dna = SuitDNA.SuitDNA()
        self.dna.newBossCog(self.dept)
        self.deptIndex = SuitDNA.suitDepts.index(self.dept)
        self.resetBattleCounters()
        self.looseToons = []
        self.involvedToons = []
        self.begunToonAmount = -1
        self.punishedToons = []
        self.toonsA = []
        self.toonsB = []
        self.nearToons = []
        self.suitsA = []
        self.activeSuitsA = []
        self.suitsB = []
        self.activeSuitsB = []
        self.reserveSuits = []
        self.barrier = None
        self.keyStates = ['BattleOne', 'BattleTwo', 'BattleThree', 'Victory']
        self.bossDamage = 0
        self.battleThreeStart = 0
        self.battleThreeDuration = 1800
        self.attackCode = None
        self.attackAvId = 0
        self.hitCount = 0
        self.toonLevels = 0
        self.surrenderRequests = {}
        self.surrendered = False
        self.TYPE_HURT = 0
        self.TYPE_ATTACK = 1
        self.uniteRewardId = [random.choice(UniteRegistry.getTypes()) for _ in range(20)]
        self.uniteRewardedToons = []
        self.bonusUnitesDict = {}
        self.universalUnites = 0
        self.saidSurrenderDialogue = False
        AllBossCogs.append(self)

    def delete(self):
        self.ignoreAll()

        taskMgr.remove(self.uniqueName('BossDone'))
        taskMgr.remove(self.uniqueName('NextAttack'))

        del self.dna

        if self in AllBossCogs:
            i = AllBossCogs.index(self)
            del AllBossCogs[i]

        return DistributedAvatarAI.DistributedAvatarAI.delete(self)

    def contentSync_getIgnoreThisZone(self) -> Optional[int]:
        return self.zoneId

    def contentSync_getZoneChangeIsLogical(self) -> bool:
        return True

    def getDNAString(self):
        return self.dna.makeNetString()

    def avatarEnter(self):
        avId = self.air.getAvatarIdFromSender()
        self.addToon(avId)

    def avatarExit(self):
        avId = self.air.getAvatarIdFromSender()
        self.removeToon(avId)

    def avatarNearEnter(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.nearToons:
            self.nearToons.append(avId)

    def avatarNearExit(self):
        avId = self.air.getAvatarIdFromSender()
        try:
            self.nearToons.remove(avId)
        except Exception:
            pass

    def setHealthTag(self, tag):
        self.sendUpdate('setHealthTag', [tag])

    def __handleUnexpectedExit(self, avId):
        self.removeToon(avId)

    def addToon(self, avId):
        if avId not in self.looseToons and avId not in self.involvedToons:
            self.looseToons.append(avId)
            event = self.air.getAvatarExitEvent(avId)
            self.acceptOnce(event, self.__handleUnexpectedExit, extraArgs=[avId])

    def removeToon(self, avId):
        av = self.air.doId2do.get(avId)
        if av is not None:
            self.removeContentSync(av)
            if av.getHp() <= 0:
                if avId not in self.punishedToons:
                    #self.air.cogSuitMgr.removeParts(av, self.deptIndex)
                    self.punishedToons.append(avId)

        if avId in self.looseToons:
            self.looseToons.remove(avId)

        if avId in self.involvedToons:
            self.involvedToons.remove(avId)

        if avId in self.toonsA:
            self.toonsA.remove(avId)

        if avId in self.toonsB:
            self.toonsB.remove(avId)

        if avId in self.nearToons:
            self.nearToons.remove(avId)

        if self.battleA:
            self.battleA.adjustSurrendered()

        if self.battleB:
            self.battleB.adjustSurrendered()

        event = self.air.getAvatarExitEvent(avId)
        self.ignore(event)
        if not self.hasToons():
            taskMgr.doMethodLater(10, self.__bossDone, self.uniqueName('BossDone'))
        else:
            self.sendUpdate('toonRemoved', [avId])

    def __bossDone(self, task):
        self.notify.info("LogStats BossDone")
        self.b_setState('Off')
        messenger.send(self.uniqueName('BossDone'))
        self.ignoreAll()

    def hasToons(self):
        return self.looseToons or self.involvedToons

    def hasToonsAlive(self):
        alive = 0
        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                hp = toon.getHp()
                if hp > 0:
                    alive = 1

        return alive

    def getBossChatIndex(self, type, attackCode=0):
        if type == self.TYPE_HURT:
            choices = TTLocalizer.BossCogHurtPhrases.get(self.dna.dept, None)
        elif type == self.TYPE_ATTACK:
            choices = TTLocalizer.BossCogTauntPhrases.get(self.dna.dept, None)
            if choices is not None:
                choices = choices.get(attackCode, None)
        if choices is not None:
            choice = random.choice(choices)
            indexOfChoice = choices.index(choice)
        else:
            indexOfChoice = None
        return indexOfChoice

    def chatOnHit(self):
        stringIndex = self.getBossChatIndex(self.TYPE_HURT)
        if stringIndex is not None:
            self.sendUpdate('setBossChatFromIndex', [stringIndex, self.TYPE_HURT, 0, 0])

    def chatOnAttack(self, attackCode, avId=0):
        stringIndex = self.getBossChatIndex(self.TYPE_ATTACK, attackCode)
        if stringIndex is not None:
            self.sendUpdate('setBossChatFromIndex', [stringIndex, self.TYPE_ATTACK, attackCode, avId])

    def sendBattleIds(self):
        self.sendUpdate('setBattleIds', [self.battleNumber, self.battleAId, self.battleBId])

    def sendToonIds(self):
        self.sendUpdate('setToonIds', [self.involvedToons, self.toonsA, self.toonsB])

    def damageToon(self, toon, deduction):
        toon.takeDamage(deduction)
        if toon.getHp() <= 0:
            self.sendUpdate('toonDied', [toon.doId])
            # TODO: Zero out inventory? Or maybe scrap this feature with pouches.
            self.removeToon(toon.doId)
            if self.getState() in ["Elevator", "Introduction"]:
                # This is anti-cheese because people were abusing a bug to get cog suits in safezones.
                toon.b_setLastHood(ZoneUtil.getSafeZoneId(toon.defaultZone))
                datagram = PyDatagram()
                datagram.addServerHeader(
                    toon.GetPuppetConnectionChannel(toon.doId),
                    self.air.ourChannel, CLIENTAGENT_EJECT
                )
                datagram.addUint16(155)
                datagram.addString('You have been kicked due to suspicious activity detected on your account.')
                self.air.send(datagram)

    def healToon(self, toon, increment):
        self.notify.info("LogStats healToonHealed amount %s" % increment)
        toon.toonUp(increment)

    def d_setBattleExperience(self, battleExperience):
        self.notify.debug('network:setBattleExperience()')
        self.sendUpdate('setBattleExperience', battleExperience)
    
    def prepareReward(self, rewardState: str="Reward") -> None:
        exp = self.getBattleExperience()
        exp[-1] = self.assignRewards()
        self.d_setBattleExperience(exp)
        self.b_setState(rewardState)
    
    def assignRewards(self):
        return BattleExperienceAI.assignRewards(
            self.involvedToons, 
            self.toonSkillPtsGained, 
            self.suitsKilled, 
            ToontownGlobals.dept2cogHQ(self.dept), 
            self.helpfulToons
        )

    def getBattleExperience(self):
        return BattleExperienceAI.getBattleExperience(
            8,
            self.involvedToons,
            self.toonExp,
            self.toonSkillPtsGained,
            self.toonOrigQuests,
            self.toonOrigMerits,
            self.toonMerits,
            self.toonParts,
        )

    def b_setArenaSide(self, arenaSide):
        self.setArenaSide(arenaSide)
        self.d_setArenaSide(arenaSide)

    def setArenaSide(self, arenaSide):
        self.arenaSide = arenaSide

    def d_setArenaSide(self, arenaSide):
        self.sendUpdate('setArenaSide', [arenaSide])

    def b_setState(self, state):
        self.setState(state)
        self.d_setState(state)

    def d_setState(self, state):
        self.sendUpdate('setState', [state])

    def setState(self, state):
        self.demand(state)
        if self.air:
            if state in self.keyStates:
                self.air.writeServerEvent('bossBattle', self.doId, '%s|%s|%s|%s' % (self.dept,
                 state,
                 self.involvedToons,
                 self.formatReward()))

    def getState(self):
        return self.state

    def formatReward(self):
        return 'unspecified'

    def enterOff(self):
        self.resetBattles()
        self.resetToons()
        self.resetBattleCounters()

    def exitOff(self):
        pass

    def enterWaitForToons(self):
        self.acceptNewToons()
        self.barrier = self.beginBarrier('WaitForToons', self.involvedToons, 5, self.__doneWaitForToons)
        self.begunToonAmount = len(self.involvedToons)

    def __doneWaitForToons(self, toons):
        self.b_setState('Elevator')

    def exitWaitForToons(self):
        self.ignoreBarrier(self.barrier)
        self.applyContentSync(*self.avIdsToAvs(self.involvedToons))

    def enterElevator(self):
        if self.notify.getDebug():
            for toonId in self.involvedToons:
                toon = simbase.air.doId2do.get(toonId)
                if toon:
                    self.notify.debug('%s. involved toon %s, %s/%s' % (self.doId,
                     toonId,
                     toon.getHp(),
                     toon.getMaxHp()))

        self.resetBattles()
        self.barrier = self.beginBarrier('Elevator', self.involvedToons, 30, self.__doneElevator)

    def __doneElevator(self, avIds):
        self.b_setState('Introduction')

    def exitElevator(self):
        self.ignoreBarrier(self.barrier)

    def enterIntroduction(self):
        self.resetBattles()
        self.arenaSide = None
        self.makeBattleOneBattles()
        self.barrier = self.beginBarrier('Introduction', self.involvedToons, 45, self.doneIntroduction)

    def doneIntroduction(self, avIds):
        self.b_setState('BattleOne')

    def exitIntroduction(self):
        self.ignoreBarrier(self.barrier)
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if toon:
                toon.b_setCogIndex(-1)

    def enterBattleOne(self):
        if self.battleA:
            self.battleA.startBattle(self.toonsA, self.suitsA)
        if self.battleB:
            self.battleB.startBattle(self.toonsB, self.suitsB)

    def exitBattleOne(self):
        self.resetBattles()

    def enterReward(self):
        self.resetBattles()
        # for toonId in self.involvedToons:
        #     toon = simbase.air.doId2do.get(toonId)
        self.barrier = self.beginBarrier('Reward', self.involvedToons, BattleBase.BUILDING_REWARD_TIMEOUT, self.__doneReward)

    def __doneReward(self, avIds):
        self.b_setState('Epilogue')

    def exitReward(self):
        pass

    def enterEpilogue(self):
        pass

    def exitEpilogue(self):
        pass

    def enterFrolic(self):
        self.resetBattles()

    def exitFrolic(self):
        pass

    def resetBattleCounters(self):
        self.battleNumber = 0
        self.battleA = None
        self.battleAId = 0
        self.battleB = None
        self.battleBId = 0
        self.arenaSide = None
        self.toonSkillPtsGained = {}
        self.toonExp = {}
        self.toonOrigQuests = {}
        self.toonOrigMerits = {}
        self.toonMerits = {}
        self.toonParts = {}
        self.suitsKilled = []
        self.helpfulToons = []

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

        for suit, joinChance in self.reserveSuits:
            suit.requestDelete()

        self.suitsA = []
        self.activeSuitsA = []
        self.suitsB = []
        self.activeSuitsB = []
        self.reserveSuits = []
        self.battleNumber = 0
        if sendReset:
            self.sendBattleIds()

    def resetToons(self):
        if self.toonsA or self.toonsB:
            self.looseToons = self.looseToons + self.involvedToons
            self.involvedToons = []
            self.toonsA = []
            self.toonsB = []
            self.sendToonIds()

    def divideToons(self):
        # figure out our sort mode
        toonLevels = self._getToonLevels()
        if toonLevels and ((min(toonLevels) / max(toonLevels)) < 0.7):
            # toon level range is too drastic, divide toons by levels
            toons = self._divideToonsWithLevels()
        else:
            toons = self._divideToonsWithFriends()
        numToons = min(len(toons), 8)
        if ConfigVariableBool('force-divide-boss-toons', False).getValue():
            numToonsB = (numToons + random.choice([0, 1])) // 2
        else:
            numToonsB = 0 if numToons <= 4 else (numToons + random.choice([0, 1])) // 2
        self.toonsA = toons[numToonsB:numToons]
        self.toonsB = toons[:numToonsB]
        self.looseToons += toons[numToons:]
        self.sendToonIds()

    def _divideToonsWithFriends(self) -> list:
        """algorithm to prioritize toons siding with friends"""
        # set up toon list
        toons = self.involvedToons[:]
        random.shuffle(toons)

        # start filling the list we have
        retlist = []
        for avId in toons:
            if avId in retlist:
                continue
            retlist.append(avId)

            # let's grab the friend of this toon
            toon = simbase.air.doId2do.get(avId, None)
            if toon is None:
                # hopefully never happens, but best to make sure
                continue

            # iterate over all of their friends, see if they're here
            toonFriends = [friendTuple[0] for friendTuple in toon.friendsList]
            for toonFriend in toonFriends:
                if toonFriend in toons and toonFriend not in retlist:
                    retlist.append(toonFriend)

        # we are done here i think
        return retlist

    def _divideToonsWithLevels(self) -> list:
        """algorithm to prioritize toons siding with friends"""
        # randomize toons
        useToons = self.involvedToons[:]
        random.shuffle(useToons)

        # set up level dictionary
        levelDict = {}
        for avId in useToons:
            # let's grab the friend of this toon
            toon = simbase.air.doId2do.get(avId, None)
            if toon is None:
                # hopefully never happens, but best to make sure
                levelDict[avId] = 1
                continue
            # set their level in the dict
            levelDict[avId] = toon.toonLevel

        # sort by toon levels, in order
        retlist = [levelTuple[0] for levelTuple in sorted(levelDict.items(), key=lambda x: x[1], reverse=True)]

        # put even indices at end, odd indices in front
        retlist = retlist[::2] + retlist[1::2]

        # we are done here i think
        return retlist

    def _getToonLevels(self) -> list:
        """returns a list of all toon levels from involvedToons"""
        retlist = []
        for avId in self.involvedToons:
            toon = simbase.air.doId2do.get(avId, None)
            if toon is None:
                continue
            if hasattr(toon, 'toonLevel'):
                retlist.append(toon.toonLevel + 1)
        return retlist

    def acceptNewToons(self):
        sourceToons = self.looseToons
        self.looseToons = []
        for toonId in sourceToons:
            toon = self.air.doId2do.get(toonId)
            if toon and not toon.ghostMode:
                self.involvedToons.append(toonId)
            else:
                self.looseToons.append(toonId)

        for avId in self.involvedToons:
            toon = self.air.doId2do.get(avId)
            if toon:
                p = []
                for t, _ in enumerate(BattleGlobals.Tracks):
                    p.append(0)

                self.toonExp[avId] = p
                self.toonOrigMerits[avId] = toon.cogMerits[:]

        self.getToonDifficulty()
        self.divideToons()

    def getToonDifficulty(self):
        if self.toonLevels != 0:
            return

        # Get our baseline params.
        totalCogSuitTier = 0
        totalToons = 0

        # Go over all the toons.
        for toonId in self.involvedToons:
            toon = simbase.air.doId2do.get(toonId)
            if not toon:
                continue

            # Calculate their boss fidelity.
            totalToons += 1
            if toon.cogReviveLevels[self.deptIndex] >= 0:
                totalCogSuitTier += 7
            else:
                totalCogSuitTier += toon.cogTypes[self.deptIndex]

        # Calculate level based on suit averages.
        averageTier = math.floor(totalCogSuitTier / max(1, totalToons)) + 1
        self.toonLevels = int(averageTier)

    def getBossTier(self) -> Options:
        """Returns the current boss tier."""
        return Options.TIER_ONE

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
        suitHandles = self.generateSuits(battleNumber)
        self.suitsB = suitHandles['activeSuits']
        self.activeSuitsB = self.suitsB[:]
        self.reserveSuits += suitHandles['reserveSuits']
        if self.toonsA:
            self.battleA = self.makeBattle(bossCogPosHpr, BossCogGlobals.BossCogBattleAPosHpr, self.handleRoundADone, self.handleBattleADone, battleNumber, 0)
            self.battleAId = self.battleA.doId
        else:
            self.moveSuits(self.activeSuitsA)
            self.suitsA = []
            self.activeSuitsA = []
            if self.arenaSide is None:
                self.b_setArenaSide(0)
        if self.toonsB:
            self.battleB = self.makeBattle(bossCogPosHpr, BossCogGlobals.BossCogBattleBPosHpr, self.handleRoundBDone, self.handleBattleBDone, battleNumber, 1)
            self.battleBId = self.battleB.doId
        else:
            self.moveSuits(self.activeSuitsB)
            self.suitsB = []
            self.activeSuitsB = []
            if self.arenaSide is None:
                self.b_setArenaSide(1)
        self.sendBattleIds()

    def makeBattle(self, bossCogPosHpr, battlePosHpr, roundCallback, finishCallback, battleNumber, battleSide):
        battle = ClashBattleFinalAI.ClashBattleFinalAI(self.air, self, roundCallback, finishCallback, battleSide)
        self.setBattlePos(battle, bossCogPosHpr, battlePosHpr)
        battle.suitsKilled = self.suitsKilled
        battle.battleCalc.toonSkillPtsGained = self.toonSkillPtsGained
        battle.toonExp = self.toonExp
        battle.toonOrigQuests = self.toonOrigQuests
        battle.toonOrigMerits = self.toonOrigMerits
        battle.toonMerits = self.toonMerits
        battle.toonParts = self.toonParts
        battle.helpfulToons = self.helpfulToons
        # mult = BattleGlobals.getBossBattleCreditMultiplier(battleNumber)
        # if self.air.holidayManager.isHolidayRunning(ToontownGlobals.GAG_EXPERIENCE_HOLIDAY) or self.air.holidayManager.isHolidayRunning(ToontownGlobals.SILLY_GAG) or self.air.holidayManager.isHolidayRunning(ToontownGlobals.GAG_EXPERIENCE_HOLIDAY_LTO):
        #     mult += 1

        #calculate experience for every round
        # battle.battleCalc.calculateSkillCreditMultiplier(bossBattleNumber = battleNumber)
        battle.generateWithRequired(self.zoneId)
        return battle

    def setBattlePos(self, battle, cogPosHpr, battlePosHpr):
        bossNode = NodePath('bossNode')
        bossNode.setPosHpr(*cogPosHpr)
        battleNode = bossNode.attachNewNode('battleNode')
        battleNode.setPosHpr(*battlePosHpr)
        suitNode = battleNode.attachNewNode('suitNode')
        suitNode.setPos(0, 1, 0)
        battle.pos = battleNode.getPos(NodePath())
        battle.initialSuitPos = suitNode.getPos(NodePath())

    def moveSuits(self, active):
        for suit in active:
            self.reserveSuits.append((suit, 0))

    def handleRoundADone(self, toonIds, totalHp, deadSuits):
        if self.battleA:
            self.handleRoundDone(self.battleA, self.suitsA, self.activeSuitsA, toonIds, totalHp, deadSuits)

    def handleRoundBDone(self, toonIds, totalHp, deadSuits):
        if self.battleB:
            self.handleRoundDone(self.battleB, self.suitsB, self.activeSuitsB, toonIds, totalHp, deadSuits)

    def handleBattleADone(self, zoneId, toonIds):
        if self.battleA:
            self.battleA.requestDelete()
            self.battleA = None
            self.battleAId = 0
            self.sendBattleIds()
        if self.arenaSide is None:
            self.b_setArenaSide(0)
        if not self.battleB and self.hasToons() and self.hasToonsAlive():
            if not self.surrendered:
                self.b_setState(self.postBattleState)

    def handleBattleBDone(self, zoneId, toonIds):
        if self.battleB:
            self.battleB.requestDelete()
            self.battleB = None
            self.battleBId = 0
            self.sendBattleIds()
        if self.arenaSide is None:
            self.b_setArenaSide(1)
        if not self.battleA and self.hasToons() and self.hasToonsAlive():
            if not self.surrendered:
                self.b_setState(self.postBattleState)

    def invokeSuitPlanner(self, buildingCode, skelecog, skelecogRandom=0, dept=None, virtual=False):
        if dept is None:
            dept = self.dna.dept
        planner = SuitPlannerInteriorAI.SuitPlannerInteriorAI(1, buildingCode, dept, self.zoneId, virtual=virtual, departmentBoss=True)
        planner.respectInvasions = 0
        suits = planner.genFloorSuits(0)

        if skelecog:
            for suit in suits['activeSuits']:
                wantSkelecog = 1
                if skelecogRandom:
                    wantSkelecog = random.randint(0, 1)
                suit.b_setSkelecog(wantSkelecog)

            for reserve in suits['reserveSuits']:
                wantSkelecog = 1
                if skelecogRandom:
                    wantSkelecog = random.randint(0, 1)
                suit = reserve[0]
                suit.b_setSkelecog(wantSkelecog)
        if virtual:
            for suit in suits['activeSuits']:
                suit.setVirtual(virtual)
            for reserve in suits['reserveSuits']:
                suit = reserve[0]
                suit.setVirtual(virtual)

        return suits

    def generateSuits(self, battleNumber):
        raise Exception('generateSuits unimplemented')

    def handleRoundDone(self, battle, suits, activeSuits, toonIds, totalHp, deadSuits):
        totalMaxHp = 0
        for suit in suits:
            totalMaxHp += suit.getMaxHp()

        for suit in deadSuits:
            if suit in activeSuits:
                activeSuits.remove(suit)

        joinedReserves = []
        if len(self.reserveSuits) > 0 and len(activeSuits) < 4:
            hpPercent = 100 - totalHp // totalMaxHp * 100.0
            for info in self.reserveSuits:
                if info[1] <= hpPercent and len(activeSuits) < 4:
                    suits.append(info[0])
                    activeSuits.append(info[0])
                    joinedReserves.append(info)

            for info in joinedReserves:
                self.reserveSuits.remove(info)

        battle.resume(joinedReserves)

    def getBattleThreeTime(self):
        elapsed = globalClock.getFrameTime() - self.battleThreeStart
        t1 = elapsed / float(self.battleThreeDuration)
        return t1

    def progressValue(self, fromValue, toValue):
        t0 = float(self.bossDamage) / float(self.bossMaxDamage)
        elapsed = globalClock.getFrameTime() - self.battleThreeStart
        t1 = elapsed / float(self.battleThreeDuration)
        t = max(t0, t1)
        return fromValue + (toValue - fromValue) * min(t, 1)

    def progressRandomValue(self, fromValue, toValue, radius = 0.2):
        t = self.progressValue(0, 1)
        radius = radius * (1.0 - abs(t - 0.5) * 2.0)
        t += radius * random.uniform(-1, 1)
        t = max(min(t, 1.0), 0.0)
        return fromValue + (toValue - fromValue) * t

    def reportToonHealth(self):
        if self.notify.getDebug():
            str = ''
            for toonId in self.involvedToons:
                toon = self.air.doId2do.get(toonId)
                if toon:
                    str += ', %s (%s/%s)' % (toonId, toon.getHp(), toon.getMaxHp())

            self.notify.debug('%s.toons = %s' % (self.doId, str[2:]))

    def getDamageMultiplier(self):
        # Based on HP, go from 1x damage multiplier to 1.675x damage multiplier.
        mult = self.progressValue(1.0, 1.675)
        return mult

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

            # Is the boss currently stunned?
            bossIsStunned = self.attackCode == BossCogGlobals.BossCogDizzy
            # If the attack this toon is going to get hit by is a collision with the boss, and the boss is stunned,
            # Do not update the attack code to a swat, effectively unstunning
            if bossIsStunned and attackCode == BossCogGlobals.BossCogElectricFence:
                return

            if attackCode == BossCogGlobals.BossCogElectricFence and (currState in ('RollToBattleTwo', 'BattleThree')):
                if self.attackCode in (BossCogGlobals.BossCogAreaAttack, BossCogGlobals.BossCogDizzyNow):
                    return
                if bpy < 0 and abs(bpx / bpy) > 0.5:
                    if bpx < 0:
                        self.b_setAttackCode(BossCogGlobals.BossCogSwatRight)
                    else:
                        self.b_setAttackCode(BossCogGlobals.BossCogSwatLeft)

    def d_showZapToon(self, avId, x, y, z, h, p, r, attackCode, timestamp):
        self.sendUpdate('showZapToon', [avId,
         x,
         y,
         z,
         h,
         p,
         r,
         attackCode,
         timestamp])

    def b_setAttackCode(self, attackCode, avId = 0):
        self.d_setAttackCode(attackCode, avId)
        self.setAttackCode(attackCode, avId)

    def setAttackCode(self, attackCode, avId = 0):
        self.attackCode = attackCode
        self.chatOnAttack(attackCode)
        self.attackAvId = avId
        if attackCode == BossCogGlobals.BossCogDizzy or attackCode == BossCogGlobals.BossCogDizzyNow:
            delayTime = self.progressValue(20, 5)
            self.hitCount = 0
        elif attackCode in (BossCogGlobals.BossCogSlowDirectedAttack, BossCogGlobals.BossCogSlowCoinDirectedAttack):
            delayTime = BossCogGlobals.BossCogAttackTimes.get(attackCode)
            delayTime += self.progressValue(10, 0)
        else:
            delayTime = BossCogGlobals.BossCogAttackTimes.get(attackCode)
            if delayTime is None:
                return
        self.waitForNextAttack(delayTime)

    def d_setAttackCode(self, attackCode, avId = 0):
        self.sendUpdate('setAttackCode', [attackCode, avId])

    def waitForNextAttack(self, delayTime):
        currState = self.getCurrentOrNextState()
        if currState == 'BattleThree':
            taskName = self.uniqueName('NextAttack')
            taskMgr.remove(taskName)
            taskMgr.doMethodLater(delayTime, self.doNextAttack, taskName)

    def stopAttacks(self):
        taskName = self.uniqueName('NextAttack')
        taskMgr.remove(taskName)

    def doNextAttack(self, task):
        self.b_setAttackCode(BossCogGlobals.BossCogNoAttack)

    def removeSkipButton(self):
        if hasattr(self, 'skipButton'):
            self.skipButton.requestDelete()
            del self.skipButton
    
    def rewardClubCoins(self) -> None:
        # Let's handle rewarding the survivors with club coins.
        
        # Get a list of avatars (that actually exist)
        toons = [simbase.air.doId2do.get(avId) for avId in self.involvedToons]
        toons = [av for av in toons if av]

        # Calculate the amount of club coins to give.
        clubCoins = 0.1

        # Reward the club coins.
        simbase.air.clubMgr.addClubCoinsForAvatars(toons, clubCoins)

    def b_setBonusUnites(self, toonId, unites):
        indivUnite = unites
        self.setBonusUnites(toonId, indivUnite)
        self.d_setBonusUnites(toonId, indivUnite)

    def setBonusUnites(self, toonId, unites):
        self.bonusUnitesDict[toonId] = unites

    def d_setBonusUnites(self, toonId, unites):
        self.sendUpdate('setBonusUnites', [toonId, unites])

    def d_setUniteRewardId(self, uniteRewardId):
        self.sendUpdate('setUniteRewardId', [uniteRewardId])

    def applyUniteReward(self):
        avId = self.air.getAvatarIdFromSender()
        currState = self.getCurrentOrNextState()
        if currState != 'Epilogue':
            self.air.writeServerEvent('suspicious', avId, "avId tried to apply unite reward, but boss cog was not in epilogue state.")
            return
        if avId in self.involvedToons and avId not in self.uniteRewardedToons:
            self.uniteRewardedToons.append(avId)
            toon = self.air.doId2do.get(avId)
            if toon:
                toon.doUniteEffect(self.uniteRewardId[0])

    def getTrueUniteAmount(self):
        uniteAmt = self.universalUnites
        uniteBoostHolidays = (ToontownGlobals.BOSS_REWARD_HOLIDAY, ToontownGlobals.SILLY_REWARD)
        # We get +1 unite from each boss if it's sunday
        if any(self.air.holidayManager.isHolidayRunning(holiday) for holiday in uniteBoostHolidays):
            uniteAmt += 1

        return uniteAmt

    def handleUniteRewards(self, toon):
        uniteAmt = self.getTrueUniteAmount()
        # Keeping around "Bonus unites" for compatability's sake.
        self.b_setBonusUnites(toon.doId, uniteAmt)
        # Hand out unites equivalent to the amount of universal unites set by this boss.
        for i in range(uniteAmt):
            toon.getHammerspace().addItem(self.uniteRewardId[i])

        uniteAmt = self.getTrueUniteAmount()

        # We send the "real" unites over, then we gotta convert to their actual IDs on AI
        self.d_setUniteRewardId(self.uniteRewardId)

    def setSurrender(self, surrender):
        self.surrendered = surrender
        if self.surrendered and self.shouldShowSurrenderDialogue and not self.saidSurrenderDialogue:
            self.saidSurrenderDialogue = True
            for battle in (self.battleA, self.battleB):
                if not battle:
                    continue

                if len(battle.toons):
                    battle.sendUpdateGameover(battle.toons[0], run=False, suitIndex=self.doId, suitContext=self.getBossNameFromDept(), forceUber=False, surrender=True)
                    break

    def adjustSurrendered(self):
        numSurrendered = 0
        numToons = len(self.involvedToons)
        requiredSurrenderVotes = BattleGlobals.getSurrenderVotes(numToons)

        for toonId in self.involvedToons:
            if toonId in self.surrenderRequests:
                # Get the value of their surrender request, it would be 0/False if they toggled off
                numSurrendered += int(self.surrenderRequests[toonId])

        for battle in (self.battleA, self.battleB):
            if not battle:
                continue

            battle.b_setNumSurrendered(numSurrendered, requiredSurrenderVotes, [toonId for toonId, value in self.surrenderRequests.items() if value])

            # Check if the number of surrender votes meets requirements.
            if numSurrendered >= requiredSurrenderVotes:
                battle.finishSurrender()

    def clearSurrenderRequests(self):
        for battle in (self.battleA, self.battleB):
            if not battle:
                continue

            self.surrenderRequests = {}
            battle.b_setNumSurrendered(0, len(self.involvedToons), [])

    @property
    def shouldShowSurrenderDialogue(self):
        return True

    def getBossNameFromDept(self) -> str:
        return {'s': 'vp', 'm': 'cfo', 'l': 'clo', 'c': 'ceo'}.get(self.dna.dept)
