from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from direct.fsm import FSM
from otp.avatar import DistributedAvatarAI
from toontown.battle import DistributedBattlePlutocratAI
from toontown.battle import SuitBattleGlobals
from toontown.battle import StatusEffects
from toontown.suit import DistributedMinibossAI
from toontown.suit import DistributedSuitAI
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownGlobals
from toontown.building import PlutocratInstanceGlobals
import random
from six.moves import range


class DistributedPlutocratBossAI(DistributedMinibossAI.DistributedMinibossAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedPlutocratBossAI')
    InvestorInfo = {
        'charon': (25, 2000),
        'nix': (21, 1675),
        'hydra': (22, 1800),
        'styx': (20, 1625),
        'kerberos': (23, 1850),
    }

    def __init__(self, air):
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        FSM.FSM.__init__(self, 'DistributedPlutocratBossAI')
        self.dna = SuitDNA.SuitDNA()
        self.dna.newSuit('pcrat')
        self.dept = self.dna.dept
        self.deptIndex = SuitDNA.suitDepts.index(self.dept)
        self.resetBattleCounters()
        self.looseToons = []
        self.involvedToons = []
        self.toons = []
        self.nearToons = []
        self.suits = []
        self.activeSuits = []
        self.reserveSuits = []
        self.barrier = None
        self.keyStates = ['BattleOne', 'Reward']
        self.bossDamage = 0
        self.battleThreeStart = 0
        self.battleThreeDuration = 1800
        self.attackCode = None
        self.attackAvId = 0
        self.hitCount = 0
        self.nerfed = False
        self.numRentalDiguises = 0
        self.numNormalDiguises = 0
        self.bossSuit = None
        self.investorOrder = []
        self.remainingInvestors = []
        self.plutocratPhase = 1
        self.postBattleState = 'Reward'
        self.cutsceneSkipVoters = []
        self.cutsceneSkipTriggered = False
        self.investorDeaths = 0
        self.investorRound = 0
        self.plutocratRound = 0
        self.deepFreezeGates = set()
        self.snowSquallActive = False
        self.marketBubbleStacks = 0
        self.charonAbsorbChance = {}
        self.ghostPayrollVisualDeaths = 0
        self.investorKickUpMultipliers = {}
        self.investorTurnCounts = {}
        self.charonStandupSuitId = 0
        self.charonAbsorbedDamage = 0
        self.snowSquallDamageRounds = 0
        self.slushFundNextRound = 0
        self.pendingDeepFreezeCount = 0

    def getHoodId(self):
        return ToontownGlobals.TheBrrrgh

    def formatReward(self):
        return 'plutocrat'

    def d_setPlutocratPhase(self, phase):
        self.plutocratPhase = int(phase)
        self.sendUpdate('setPlutocratPhase', [self.plutocratPhase])

    def __makeSuit(self, name, actualLevel, maxHp, skelecog):
        suit = DistributedSuitAI.DistributedSuitAI(self.air, None)
        dna = SuitDNA.SuitDNA()
        dna.newSuit(name)
        suit.dna = dna
        suit.setLevel(actualLevel, forceLevel=True)
        suit.setManager(1)
        if skelecog:
            suit.setSkelecog(1)
        suit.generateWithRequired(self.zoneId)
        suit.b_setMaxHP(maxHp)
        suit.b_setHP(maxHp)
        return suit

    def __makeInvestor(self, name):
        level, hp = self.InvestorInfo[name]
        return self.__makeSuit(name, level, hp, 1)

    def __makePlutocrat(self):
        return self.__makeSuit('pcrat', 38, 6000, 0)

    def queueRemainingInvestor(self):
        if not self.remainingInvestors:
            return None
        name = self.remainingInvestors.pop(0)
        suit = self.__makeInvestor(name)
        self.reserveSuits.append(suit)
        if self.battle:
            self.battle.maxSuits += 1
        return suit

    def queueNaturalReserves(self, count=2):
        if not self.battle:
            return []
        result = []
        living = [suit for suit in self.activeSuits if suit.getHP() > 0]
        for unused in range(count):
            if len(living) + len(self.reserveSuits) >= self.battle.maxSuits:
                break
            actualLevel = random.randint(12, 15)
            candidates = []
            for name in SuitDNA.suitDeptCogs.get('m', ()):
                try:
                    if (SuitBattleGlobals.getSuitMinLevel(name) <= actualLevel <=
                            SuitBattleGlobals.getSuitMaxLevel(name)):
                        candidates.append(name)
                except:
                    pass
            if not candidates:
                continue
            name = random.choice(candidates)
            suit = DistributedSuitAI.DistributedSuitAI(self.air, None)
            dna = SuitDNA.SuitDNA()
            dna.newSuit(name)
            suit.dna = dna
            suit.setLevel(actualLevel, forceLevel=True)
            if random.random() <= 0.25:
                suit.setExecutive(1)
            suit.generateWithRequired(self.zoneId)
            self.reserveSuits.append(suit)
            result.append(suit)
        return result

    def queueStyxWaiter(self):
        if not self.battle:
            return None
        for suit in self.suits + self.reserveSuits:
            try:
                if suit.getWaiter() and suit.getHP() > 0:
                    return suit
            except:
                if getattr(suit, 'isWaiter', 0) and suit.getHP() > 0:
                    return suit
        candidates = []
        for dept in SuitDNA.suitDepts:
            for name in SuitDNA.suitDeptCogs.get(dept, ()):
                try:
                    if (SuitBattleGlobals.getSuitMinLevel(name) <= 15 <=
                            SuitBattleGlobals.getSuitMaxLevel(name)):
                        candidates.append(name)
                except:
                    pass
        waiter = DistributedSuitAI.DistributedSuitAI(self.air, None)
        dna = SuitDNA.SuitDNA()
        dna.newSuit(random.choice(candidates) if candidates else 'tf')
        waiter.dna = dna
        waiter.setLevel(15, forceLevel=True)
        waiter.setExecutive(1)
        waiter.plutocratWaiterLureResistance = 2
        try:
            waiter.setWaiter(1)
        except:
            waiter.isWaiter = 1
        waiter.generateWithRequired(self.zoneId)
        self.reserveSuits.append(waiter)
        return waiter

    def resetBattles(self):
        sendReset = 0
        if self.battle:
            self.battle.requestDelete()
            self.battle = None
            self.battleId = 0
            sendReset = 1
        cleaned = []
        for suit in self.suits + self.reserveSuits:
            if suit not in cleaned:
                cleaned.append(suit)
        if self.bossSuit and self.bossSuit not in cleaned:
            cleaned.append(self.bossSuit)
        for suit in cleaned:
            try:
                suit.requestDelete()
            except:
                pass
        self.suits = []
        self.activeSuits = []
        self.reserveSuits = []
        self.bossSuit = None
        self.battleNumber = 0
        if sendReset:
            self.sendBattleIds()

    def makeBattle(self):
        battle = DistributedBattlePlutocratAI.DistributedBattlePlutocratAI(
            self.air, self, self.handleRoundADone, self.handleBattleADone, 0)
        self.setBattlePos(battle, PlutocratInstanceGlobals.BATTLE_NODE_POS_HPR, (0, 0, 0, 0, 0, 0))
        battle.maxSuits = 4
        battle.suitsKilled = self.suitsKilled
        battle.battleCalc.toonSkillPtsGained = self.toonSkillPtsGained
        battle.toonExp = self.toonExp
        battle.toonOrigQuests = self.toonOrigQuests
        battle.toonItems = self.toonItems
        battle.toonOrigMerits = self.toonOrigMerits
        battle.toonMerits = self.toonMerits
        battle.toonParts = self.toonParts
        battle.helpfulToons = self.helpfulToons
        battle.battleCalc.setSkillCreditMultiplier(1)
        battle.generateWithRequired(self.zoneId)
        return battle

    def initializePlutocratBattle(self):
        self.resetBattles()
        if not self.involvedToons:
            self.notify.warning('initializePlutocratBattle: no toons!')
            return
        self.battleNumber = 1
        self.plutocratPhase = 1
        self.investorOrder = list(self.InvestorInfo.keys())
        random.shuffle(self.investorOrder)
        initialNames = self.investorOrder[:3]
        self.remainingInvestors = self.investorOrder[3:]
        self.bossSuit = self.__makePlutocrat()
        self.suits = [self.__makeInvestor(name) for name in initialNames]
        self.activeSuits = self.suits[:]
        self.reserveSuits = []
        self.investorDeaths = 0
        self.investorRound = 0
        self.plutocratRound = 0
        self.deepFreezeGates = set()
        self.snowSquallActive = False
        self.marketBubbleStacks = 0
        self.charonAbsorbChance = {}
        self.ghostPayrollVisualDeaths = 0
        self.investorKickUpMultipliers = {}
        self.investorTurnCounts = {}
        self.charonStandupSuitId = 0
        self.charonAbsorbedDamage = 0
        self.snowSquallDamageRounds = 0
        self.slushFundNextRound = 0
        self.pendingDeepFreezeCount = 0
        self.battle = self.makeBattle()
        self.battleId = self.battle.doId
        self.sendBattleIds()
        self.sendUpdate('setPlutocratPhase', [1])

    def enterWaitForToons(self):
        self.acceptNewToons()
        self.barrier = self.beginBarrier('WaitForToons', self.involvedToons, 120, self.__doneWaitForToons)

    def __doneWaitForToons(self, avIds):
        self.b_setState('Introduction')

    def exitWaitForToons(self):
        if self.barrier:
            self.ignoreBarrier(self.barrier)
            self.barrier = None

    def enterIntroduction(self):
        self.initializePlutocratBattle()
        self.barrier = self.beginBarrier('Introduction', self.involvedToons, 45, self.__doneIntroduction)

    def __doneIntroduction(self, avIds):
        self.b_setState('BattleOne')

    def exitIntroduction(self):
        if self.barrier:
            self.ignoreBarrier(self.barrier)
            self.barrier = None

    def enterBattleOne(self):
        if self.battle:
            self.battle.startBattle(self.toons, self.suits)

    def exitBattleOne(self):
        pass

    def handleRoundADone(self, toonIds, totalHp, deadSuits):
        if not self.battle:
            return
        for suit in deadSuits:
            if suit in self.activeSuits:
                self.activeSuits.remove(suit)
            try:
                if self.plutocratPhase == 1 and suit.dna.name in self.InvestorInfo:
                    self.investorDeaths = min(2, self.investorDeaths + 1)
            except:
                pass
        if self.plutocratPhase == 1 and not self.activeSuits:
            self.d_setPlutocratPhase(2)
            for toonId in toonIds:
                toon = self.air.doId2do.get(toonId)
                if toon and hasattr(toon, 'clearStatusEffects'):
                    try:
                        toon.clearStatusEffects()
                    except:
                        pass
            if self.bossSuit:
                self.suits.append(self.bossSuit)
                self.activeSuits.append(self.bossSuit)
                self.battle.resume([self.bossSuit])
                return
        joined = []
        while self.reserveSuits and len(self.activeSuits) < self.battle.maxSuits:
            reserve = self.reserveSuits.pop(0)
            if reserve not in self.suits:
                self.suits.append(reserve)
            self.activeSuits.append(reserve)
            joined.append(reserve)
        self.battle.resume(joined)
        for reserve in joined:
            if getattr(reserve, 'plutocratWaiterLureResistance', 0):
                effects = self.battle.battleCalc.suitStatusConditionsNew.setdefault(reserve.doId, [])
                effects.append(StatusEffects.LureResistance(2))

    def enterReward(self):
        self.barrier = self.beginBarrier('Reward', self.involvedToons, 35, self.__doneReward)

    def __doneReward(self, avIds):
        self.resetBattles()
        self.b_setState('Epilogue')

    def exitReward(self):
        if self.barrier:
            self.ignoreBarrier(self.barrier)
            self.barrier = None

    def enterEpilogue(self):
        self.barrier = self.beginBarrier('Epilogue', self.involvedToons, 10, self.__doneEpilogue)

    def __doneEpilogue(self, avIds):
        self.b_setState('Off')

    def exitEpilogue(self):
        if self.barrier:
            self.ignoreBarrier(self.barrier)
            self.barrier = None

    def enterOff(self):
        self.resetBattles()

    def exitOff(self):
        pass

    def delete(self):
        try:
            if self.barrier:
                self.ignoreBarrier(self.barrier)
        except:
            pass
        self.resetBattles()
        DistributedMinibossAI.DistributedMinibossAI.delete(self)
