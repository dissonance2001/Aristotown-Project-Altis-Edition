from direct.directnotify import DirectNotifyGlobal
from direct.fsm import FSM
from otp.avatar import DistributedAvatarAI

from toontown.battle import BattleExperienceAI
from toontown.battle import DistributedBattleChainsawAI
from toontown.battle import SuitBattleGlobals
from toontown.suit import DistributedMinibossAI
from toontown.suit import DistributedSuitAI
from toontown.suit import BossCutsceneSkipAI
from toontown.suit import SuitDNA
from toontown.toonbase import ToontownGlobals

import random


class DistributedChainsawBossAI(
        DistributedMinibossAI.DistributedMinibossAI, FSM.FSM):
    notify = DirectNotifyGlobal.directNotify.newCategory(
        'DistributedChainsawBossAI')

    BATTLE_CAP = 5
    PHASE_TWO_HP = 8500
    PHASE_THREE_HP = 4750
    MIN_RPM = 10
    MAX_RPM_PHASE_12 = 20
    MAX_RPM_PHASE_3 = 30

    def __init__(self, air):
        # Chainsaw is a normal Suit miniboss controlled by this lightweight
        # instance object.  Do not run the legacy BossCog constructor.
        DistributedAvatarAI.DistributedAvatarAI.__init__(self, air)
        FSM.FSM.__init__(self, 'DistributedChainsawBossAI')

        self.dna = SuitDNA.SuitDNA()
        self.dna.newSuit('chainsaw')
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

        # Fields referenced by the inherited miniboss helpers.
        self.bossDamage = 0
        self.battleThreeStart = 0
        self.battleThreeDuration = 1800
        self.attackCode = None
        self.attackAvId = 0
        self.hitCount = 0
        self.nerfed = False
        self.numRentalDiguises = 0
        self.numNormalDiguises = 0

        self.chainsawSuitId = 0
        self.chainsawRPM = self.MIN_RPM
        self.chainsawPhase = 1
        self.chainsawPreviousAttack = None
        self.chainsawPreviousLogicAttack = None
        self.chainsawHitlessRounds = -1
        self.chainsawChainLinked = False
        self.chainsawKickbackRounds = 0
        self.chainsawKickbackMultiplier = 1.0
        self.chainsawPendingKickback = False
        self.chainsawPendingKickbackMultiplier = 1.0
        self.chainsawKickbackVisualPending = False
        self.chainsawKickbackActivatedThisRound = False
        self.chainsawPendingPromotedSuitId = 0
        self.chainsawSparkPlug = {}
        self.chainsawCutSlackTargets = {}
        self.chainsawUsedThrottle = False
        self.chainsawRound = 0
        self.chainsawRewardsGranted = False
        self.postBattleState = 'Reward'
        self.chainsawPreviousSupportCount = 0
        self.chainsawChainStartSupportIds = []
        self.chainsawFiredLinks = 0
        self.chainsawDeadwoodTriggered = False
        self.chainsawPhaseTwoFirstTurn = False
        self.chainsawAbilityBanRounds = 0
        self.chainsawCoreV3 = True
        self.cutsceneSkipVoters = []
        self.cutsceneSkipTriggered = False
        self._chainsawDoneSent = False

    def getHoodId(self):
        return ToontownGlobals.OutdoorZone

    def formatReward(self):
        return 'chainsaw'

    # ------------------------------------------------------------------
    # Distributed state used by the client battle presentation / RPM GUI.
    # ------------------------------------------------------------------

    def d_setChainsawSuitId(self, suitId):
        self.chainsawSuitId = suitId
        self.sendUpdate('setChainsawSuitId', [suitId])

    def b_setChainsawRPM(self, rpm):
        rpm = int(max(self.MIN_RPM, rpm))
        maximum = (self.MAX_RPM_PHASE_3 if self.chainsawPhase == 3
                   else self.MAX_RPM_PHASE_12)
        rpm = min(maximum, rpm)
        self.chainsawRPM = rpm
        self.sendUpdate('setChainsawRPM', [rpm])

    def b_setChainsawPhase(self, phase):
        phase = max(1, min(3, int(phase)))
        if self.chainsawPhase == phase:
            return
        self.chainsawPhase = phase
        self.sendUpdate('setChainsawPhase', [phase])

    def requestSkip(self):
        BossCutsceneSkipAI.requestSkip(self)

    # ------------------------------------------------------------------
    # Suit construction.
    # ------------------------------------------------------------------

    def __makeSuit(self, name, actualLevel, executive=0):
        suit = DistributedSuitAI.DistributedSuitAI(self.air, None)
        dna = SuitDNA.SuitDNA()
        dna.newSuit(name)
        suit.dna = dna
        suit.setLevel(actualLevel, forceLevel=True)
        suit.setExecutive(executive)
        suit.generateWithRequired(self.zoneId)
        return suit

    def __makeChainsawSuit(self):
        suit = self.__makeSuit('chainsaw', 50, 0)
        # The current Clash definition is a 12,000 HP level-50 manager.
        suit.b_setMaxHP(12000)
        suit.b_setHP(12000)
        try:
            suit.b_setManager(1)
        except:
            try:
                suit.setManager(1)
            except:
                pass
        suit.setDamageMultiplier(1.0)
        return suit

    def __chooseBossbotGrunt(self, actualLevel):
        choices = []
        for name in SuitDNA.getSuitsInDept('c', includeManagers=False):
            try:
                if (SuitBattleGlobals.getSuitMinLevel(name) <= actualLevel <=
                        SuitBattleGlobals.getSuitMaxLevel(name)):
                    choices.append(name)
            except:
                pass
        if not choices:
            return SuitDNA.getRandomSuitByDept('c')
        return random.choice(choices)

    def __makeGrunt(self):
        level = random.randint(10, 15)
        name = self.__chooseBossbotGrunt(level)
        executive = 1 if random.random() < 0.25 else 0
        return self.__makeSuit(name, level, executive)

    def __makeInitialSuits(self):
        # Clash starts Chainsaw with zero support Cogs.  The manager occupies
        # the front battle slot by himself for the complete first turn; the
        # four support slots are filled through the left office door only
        # after that round finishes.
        return [self.__makeChainsawSuit()]

    def __findChainsawSuit(self):
        for suit in self.activeSuits + self.suits:
            try:
                if suit.dna.name == 'chainsaw':
                    return suit
            except:
                pass
        return None

    def makeBattle(self, bossCogPosHpr, battlePosHpr, roundCallback,
                   finishCallback, battleNumber, battleSide):
        battle = DistributedBattleChainsawAI.DistributedBattleChainsawAI(
            self.air, self, roundCallback, finishCallback, battleSide)
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
        battle.battleCalc.setSkillCreditMultiplier(1)
        battle.generateWithRequired(self.zoneId)
        return battle

    def divideToons(self):
        toons = self.involvedToons[:]
        numToons = min(len(toons), 8)
        self.toons = toons[:numToons]
        self.looseToons += toons[numToons:]
        self.sendToonIds()

    def initializeChainsawBattle(self):
        self.resetBattles()
        if not self.involvedToons:
            self.notify.warning('initializeChainsawBattle: no toons!')
            return

        self.chainsawRPM = self.MIN_RPM
        self.chainsawPhase = 1
        self.chainsawPreviousAttack = None
        self.chainsawPreviousLogicAttack = None
        self.chainsawHitlessRounds = -1
        self.chainsawChainLinked = False
        self.chainsawKickbackRounds = 0
        self.chainsawKickbackMultiplier = 1.0
        self.chainsawPendingKickback = False
        self.chainsawPendingKickbackMultiplier = 1.0
        self.chainsawKickbackVisualPending = False
        self.chainsawKickbackActivatedThisRound = False
        self.chainsawPendingPromotedSuitId = 0
        self.chainsawSparkPlug = {}
        self.chainsawCutSlackTargets = {}
        self.chainsawUsedThrottle = False
        self.chainsawRound = 0
        self.chainsawPreviousSupportCount = 0
        self.chainsawChainStartSupportIds = []
        self.chainsawFiredLinks = 0
        self.chainsawDeadwoodTriggered = False
        self.chainsawPhaseTwoFirstTurn = False
        self.chainsawAbilityBanRounds = 0

        self.battleNumber = 1
        self.suits = self.__makeInitialSuits()
        self.activeSuits = self.suits[:]
        self.reserveSuits = []

        # This matches the battle node authored into the Chainsaw room.
        self.battle = self.makeBattle(
            (0, 10, 0, 180, 0, 0),
            (0, 0, 0, 0, 0, 0),
            self.handleRoundADone,
            self.handleBattleADone,
            1,
            0)
        self.battleId = self.battle.doId
        self.sendBattleIds()

        boss = self.__findChainsawSuit()
        self.d_setChainsawSuitId(boss.doId if boss else 0)
        self.sendUpdate('setChainsawRPM', [self.chainsawRPM])
        self.sendUpdate('setChainsawPhase', [self.chainsawPhase])

    # ------------------------------------------------------------------
    # State flow.
    # ------------------------------------------------------------------

    def enterWaitForToons(self):
        self.acceptNewToons()
        self.barrier = self.beginBarrier(
            'WaitForToons', self.involvedToons, 120,
            self.__doneWaitForToons)

    def __doneWaitForToons(self, avIds):
        self.b_setState('Introduction')

    def exitWaitForToons(self):
        if self.barrier:
            self.ignoreBarrier(self.barrier)
            self.barrier = None

    def enterIntroduction(self):
        # Create the real distributed battle/Suits before the CTSC, but the
        # client keeps the real Chainsaw hidden until the local scene actor is
        # retired at the end of the intro.
        self.cutsceneSkipVoters = []
        self.cutsceneSkipTriggered = False
        self.initializeChainsawBattle()
        self.barrier = self.beginBarrier(
            'Introduction', self.involvedToons, 140,
            self.__doneIntroduction)

    def __doneIntroduction(self, avIds):
        self.b_setState('BattleOne')

    def exitIntroduction(self):
        if self.barrier:
            self.ignoreBarrier(self.barrier)
            self.barrier = None

    def enterBattleOne(self):
        BossCutsceneSkipAI.reset(self)
        if self.battle:
            self.battle.startBattle(self.toons, self.suits)

    def exitBattleOne(self):
        pass

    # ------------------------------------------------------------------
    # Round lifecycle / reserves.
    # ------------------------------------------------------------------

    def __removeDeadFromController(self, deadSuits):
        for suit in deadSuits:
            if suit in self.activeSuits:
                self.activeSuits.remove(suit)

    def __finishRemainingSupports(self):
        # Modern Clash ends this encounter when the manager dies.  Remove the
        # remaining grunts from the battle bookkeeping rather than requiring a
        # post-boss cleanup round.
        if not self.battle:
            return
        for suit in self.activeSuits[:]:
            try:
                if suit.dna.name == 'chainsaw':
                    continue
            except:
                pass
            try:
                suit.b_setHP(0)
            except:
                pass
            try:
                self.battle._DistributedBattleBaseAI__removeSuit(suit)
            except:
                pass
            try:
                self.activeSuits.remove(suit)
            except:
                pass
            try:
                suit.requestDelete()
            except:
                pass
        try:
            self.battle.d_setMembers()
        except:
            pass

    def __spawnReserves(self):
        # Clash suppresses normal reserve refills while Chain Linked is active,
        # but the activation round itself is allowed to fill empty slots and
        # those arriving Cogs become part of the chain.
        if (self.chainsawChainLinked and
                self.chainsawPreviousAttack != 'ChainLinked'):
            return []
        alive = []
        for suit in self.activeSuits:
            try:
                if suit.getHP() > 0:
                    alive.append(suit)
            except:
                pass
        amount = max(0, self.BATTLE_CAP - len(alive))
        reserves = []
        for i in xrange(amount):
            suit = self.__makeGrunt()
            if self.chainsawPreviousAttack == 'Scabbard':
                newMax = int(round(suit.getMaxHP() * 1.5))
                suit.b_setMaxHP(newMax)
                suit.b_setHP(newMax)
                suit.chainsawOvercharged = True
                try:
                    suit.setDamageMultiplier(suit.getDamageMultiplier() * 1.5)
                except:
                    pass
            self.suits.append(suit)
            self.activeSuits.append(suit)
            if self.chainsawChainLinked:
                self.chainsawChainStartSupportIds.append(suit.doId)
            reserves.append(suit)
        return reserves

    def _livingLinkedSupportIds(self):
        chainIds = set(self.chainsawChainStartSupportIds)
        living = []
        seen = set()
        for collection in (self.activeSuits, self.suits):
            for suit in collection:
                if suit is None:
                    continue
                suitId = getattr(suit, 'doId', 0)
                if not suitId or suitId not in chainIds or suitId in seen:
                    continue
                seen.add(suitId)
                try:
                    if suit.getHP() > 0:
                        living.append(suitId)
                except:
                    pass
        return living

    def handleRoundADone(self, toonIds, totalHp, deadSuits):
        if not self.battle:
            return

        self.chainsawRound += 1

        if self.chainsawAbilityBanRounds > 0:
            self.chainsawAbilityBanRounds -= 1

        # Existing Kickback applies for the current two complete rounds.  New
        # Kickback is installed after this decrement below.
        if self.chainsawKickbackRounds > 0:
            self.chainsawKickbackRounds -= 1
            if self.chainsawKickbackRounds <= 0:
                self.chainsawKickbackMultiplier = 1.0

        # Track Cut The Slack targets and grant current Clash-style Kickback
        # when a highly promoted one is defeated by the Toons.
        for suit in deadSuits:
            suitId = getattr(suit, 'doId', 0)
            rounds = self.chainsawCutSlackTargets.pop(suitId, None)
            isCutSlackTarget = rounds is not None or bool(
                getattr(suit, 'chainsawCutSlackTarget', False))
            if isCutSlackTarget:
                try:
                    level = suit.getActualLevel()
                except:
                    level = 0
                if level >= 20:
                    multiplier = 1.10 + ((level - 20) * 0.02)
                    self.chainsawPendingKickback = True
                    self.chainsawPendingKickbackMultiplier = max(
                        self.chainsawPendingKickbackMultiplier, multiplier)

        for suitId in self.chainsawCutSlackTargets.keys():
            self.chainsawCutSlackTargets[suitId] += 1

        self.__removeDeadFromController(deadSuits)

        # Chain Link ends when every Cog that was linked at activation has
        # disappeared.  Current Clash grants two rounds of Kick Back; each Cog
        # removed by a Fire during the chain reduces the 30% bonus by 5%.
        if self.chainsawChainLinked and self.chainsawChainStartSupportIds:
            livingIds = self._livingLinkedSupportIds()
            if not livingIds:
                self.chainsawChainLinked = False
                self.chainsawChainStartSupportIds = []
                firedLinks = max(0, int(self.chainsawFiredLinks))
                self.chainsawPendingKickback = True
                self.chainsawPendingKickbackMultiplier = max(
                    1.0, 1.30 - (0.05 * firedLinks))
                self.chainsawFiredLinks = 0

        boss = self.__findChainsawSuit()
        if not boss or boss.getHP() <= 0:
            self.postBattleState = 'Reward'
            self.__finishRemainingSupports()
            self.battle.resume([])
            return

        # Deadwood is a loss/ejection, not an ordinary battle round.  The
        # calculator has already reduced the Toons to 1 Laff for the movie;
        # after it finishes, retire the battle and let the client return them
        # to the foot of the office/lobby.
        if self.chainsawDeadwoodTriggered:
            for toonId in toonIds:
                toon = self.air.doId2do.get(toonId)
                if toon:
                    try:
                        toon.hpOwnedByBattle = 0
                    except:
                        pass
                    try:
                        toon.hpAdjustBattle = 0
                    except:
                        pass
                    try:
                        toon.b_setHp(1)
                    except:
                        try:
                            toon.setHp(1)
                        except:
                            pass
            self.chainsawDeadwoodTriggered = False
            battle = self.battle
            self.battle = None
            self.battleId = 0
            self.sendBattleIds()
            if battle:
                try:
                    battle.requestDelete()
                except:
                    pass
            self.b_setState('Deadwood')
            return

        if self.chainsawPendingKickback:
            self.chainsawKickbackRounds = 2
            self.chainsawAbilityBanRounds = 2
            self.chainsawKickbackMultiplier = self.chainsawPendingKickbackMultiplier
            self.chainsawKickbackVisualPending = True
            self.chainsawPendingKickback = False
            self.chainsawPendingKickbackMultiplier = 1.0

        if self.chainsawPreviousAttack == 'Scabbard':
            for suit in self.activeSuits:
                try:
                    if suit.dna.name == 'chainsaw' or suit.getHP() <= 0:
                        continue
                    suit.d_setMaxHP(suit.getMaxHP())
                    suit.d_setHP(suit.getHP())
                except:
                    pass

        self.chainsawPendingPromotedSuitId = 0

        reserves = self.__spawnReserves()

        # The calculator needs to know how many support Cogs existed at the
        # start of the next round so a full wipe can award its +1,000 RPM.
        # Reserves are created after calculation, so record the post-refill
        # population here rather than leaving the first reserve wave at zero.
        supportCount = 0
        for suit in self.activeSuits:
            try:
                if suit.dna.name != 'chainsaw' and suit.getHP() > 0:
                    supportCount += 1
            except:
                pass
        self.chainsawPreviousSupportCount = supportCount

        self.battle.resume(reserves)

    # ------------------------------------------------------------------
    # Rewards / completion.
    # ------------------------------------------------------------------

    def __grantChainsawRewards(self):
        if self.chainsawRewardsGranted:
            return
        self.chainsawRewardsGranted = True
        self.d_setBattleExperience()
        BattleExperienceAI.assignRewards(
            self.involvedToons,
            self.toonSkillPtsGained,
            self.suitsKilled,
            ToontownGlobals.dept2cogHQ(self.dept),
            self.helpfulToons)
        for toonId in self.involvedToons:
            toon = self.air.doId2do.get(toonId)
            if toon:
                simbase.air.questManager.toonDefeatedBoss(
                    toon,
                    ToontownGlobals.dept2cogHQ(self.dept),
                    self.dna.dept,
                    self.involvedToons)


    def enterDeadwood(self):
        self.resetBattles()
        self.d_setChainsawSuitId(0)
        self.barrier = self.beginBarrier(
            'Deadwood', self.involvedToons, 12, self.__doneDeadwood)

    def __doneDeadwood(self, avIds):
        self.b_setState('Off')

    def exitDeadwood(self):
        if self.barrier:
            self.ignoreBarrier(self.barrier)
            self.barrier = None

    def enterReward(self):
        self.__grantChainsawRewards()
        self.resetBattles()
        self.d_setChainsawSuitId(0)
        DistributedMinibossAI.DistributedMinibossAI.enterReward(self)

    def enterEpilogue(self):
        BossCutsceneSkipAI.reset(self)
        self.barrier = self.beginBarrier(
            'Epilogue', self.involvedToons, 75,
            self.__doneEpilogue)

    def __doneEpilogue(self, avIds):
        self.b_setState('Off')

    def exitEpilogue(self):
        if self.barrier:
            self.ignoreBarrier(self.barrier)
            self.barrier = None

    def removeToon(self, avId):
        DistributedMinibossAI.DistributedMinibossAI.removeToon(self, avId)
        if self.hasToons() or self.state != 'Off' or self._chainsawDoneSent:
            return
        taskMgr.remove(self.uniqueName('BossDone'))
        self._chainsawDoneSent = True
        if self.air:
            self.air.writeServerEvent('bossBattleDone', self.doId, '%s' % self.dept)
        messenger.send(self.uniqueName('BossDone'))
        self.ignoreAll()

    def enterOff(self):
        self.resetBattles()

    def exitOff(self):
        pass

    def delete(self):
        taskMgr.remove(self.uniqueName('BossDone'))
        try:
            if self.barrier:
                self.ignoreBarrier(self.barrier)
        except:
            pass
        DistributedMinibossAI.DistributedMinibossAI.delete(self)
