from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
from toontown.battle import StatusEffects
from toontown.battle import PlutocratBalanceGlobals
import math
import random


class PlutocratCalculatorAI:
    Investors = ('charon', 'nix', 'hydra', 'styx', 'kerberos')

    def __init__(self, calculator):
        self.calculator = calculator
        self.battle = calculator.battle
        self._deferredToonCalls = []
        self._replayingDeferredToons = False
        self._installCompatibilityHooks()

    def __getattr__(self, name):
        return getattr(self.calculator, name)

    def _installCompatibilityHooks(self):
        calculator = self.calculator
        if getattr(calculator, '_plutocratParityHooksInstalled', False):
            return
        calculator._plutocratParityHooksInstalled = True

        baseDamageMultipliers = calculator.applyToonGagDamageMultipliers
        def applyToonGagDamageMultipliers(damage, toonId, suitId, atkTrack, atkLevel, organicBonus=False):
            damage = baseDamageMultipliers(damage, toonId, suitId, atkTrack, atkLevel, organicBonus)
            controller = self._controller()
            if not controller or damage <= 0:
                return damage
            suit = self.battle.findSuit(suitId)
            if not suit:
                return damage
            name = getattr(getattr(suit, 'dna', None), 'name', '')
            if self._isFrozen(controller, suit):
                damage *= 0.9
                if atkTrack == ZAP:
                    damage *= 0.5
            if controller.plutocratPhase == 2 and name == 'charon':
                damage *= 0.8
            if self.suitHasCondition(suitId, 'plutocratSlushFund'):
                damage *= 0.8
            if name == 'pcrat' and controller.marketBubbleStacks < 0:
                damage *= 1.25
            return damage
        calculator.applyToonGagDamageMultipliers = applyToonGagDamageMultipliers

        targetDefenseName = '_BattleCalculatorAI__targetDefense'
        baseTargetDefense = getattr(calculator, targetDefenseName, None)
        if baseTargetDefense:
            def targetDefense(suit, atkTrack):
                defense = baseTargetDefense(suit, atkTrack)
                controller = self._controller()
                if controller and suit and self._isFrozen(controller, suit):
                    defense += 25
                return defense
            setattr(calculator, targetDefenseName, targetDefense)

        createZapName = '_BattleCalculatorAI__createZapTargetList'
        validZapName = '_BattleCalculatorAI__isValidZapChainTarget'
        baseCreateZap = getattr(calculator, createZapName, None)
        baseValidZap = getattr(calculator, validZapName, None)
        if baseCreateZap and baseValidZap:
            def createZapTargetList(attackIndex):
                controller = self._controller()
                if not controller:
                    return baseCreateZap(attackIndex)
                attack = self.battle.toonAttacks.get(attackIndex)
                if not attack:
                    return baseCreateZap(attackIndex)
                mainTarget = self.battle.findSuit(attack[TOON_TGT_COL])
                if not mainTarget or mainTarget not in self.battle.activeSuits:
                    return []
                if self._isFrozen(controller, mainTarget):
                    return [mainTarget]
                if not baseValidZap(mainTarget):
                    return []
                activeSuits = self.battle.activeSuits
                mainIndex = activeSuits.index(mainTarget)
                targets = [mainTarget]
                index = mainIndex - 1
                while index >= 0 and len(targets) < 4:
                    suit = activeSuits[index]
                    if self._isFrozen(controller, suit):
                        break
                    if baseValidZap(suit):
                        targets.append(suit)
                    index -= 1
                index = mainIndex + 1
                while index < len(activeSuits) and len(targets) < 4:
                    suit = activeSuits[index]
                    if self._isFrozen(controller, suit):
                        break
                    if baseValidZap(suit):
                        targets.append(suit)
                    index += 1
                return targets
            setattr(calculator, createZapName, createZapTargetList)

        calcTracksName = '_BattleCalculatorAI__calculateToonAttacksForTracks'
        baseCalcTracks = getattr(calculator, calcTracksName, None)
        baseSetSuitCondition = calculator.setSuitCondition
        def setSuitCondition(suitId, condition, modifier, turns=-1, mode='none'):
            suit = self.battle.findSuit(suitId)
            investor = bool(suit and getattr(getattr(suit, 'dna', None), 'name', '') in self.Investors)
            if investor and condition in ('soaked', 'drenched', 'sued') and turns > 1 and mode != 'none':
                turns -= 1
            return baseSetSuitCondition(suitId, condition, modifier, turns, mode)
        calculator.setSuitCondition = setSuitCondition
        if baseCalcTracks:
            def calculateToonAttacksForTracks(allowedTracks, finalizeBonuses=True):
                if self._shouldDeferToonMoves():
                    self._deferredToonCalls.append((
                        calculateToonAttacksForTracks,
                        (list(allowedTracks), finalizeBonuses)))
                    return None
                controller = self._controller()
                if not controller or ZAP not in allowedTracks:
                    return baseCalcTracks(allowedTracks, finalizeBonuses)
                temporarySoak = []
                for suit in self._aliveSuits():
                    if not self._isFrozen(controller, suit):
                        continue
                    if (self.suitHasCondition(suit.doId, 'soaked') or
                            self.suitHasCondition(suit.doId, 'drenched') or
                            self.suitHasCondition(suit.doId, 'missedSoak')):
                        continue
                    baseSetSuitCondition(suit.doId, 'soaked', 1, 1, 'setBoth')
                    temporarySoak.append(suit.doId)
                try:
                    return baseCalcTracks(allowedTracks, finalizeBonuses)
                finally:
                    for suitId in temporarySoak:
                        baseSetSuitCondition(suitId, 'soaked', 0, 0, 'setBoth')
            setattr(calculator, calcTracksName, calculateToonAttacksForTracks)

        postProcessName = '_BattleCalculatorAI__postProcessToonAttacksForTracks'
        basePostProcess = getattr(calculator, postProcessName, None)
        if basePostProcess:
            def postProcessToonAttacksForTracks(allowedTracks):
                if self._shouldDeferToonMoves():
                    self._deferredToonCalls.append((
                        postProcessToonAttacksForTracks,
                        (list(allowedTracks),)))
                    return None
                return basePostProcess(allowedTracks)
            setattr(calculator, postProcessName, postProcessToonAttacksForTracks)

        trackPhaseName = '_BattleCalculatorAI__calculateToonTrackPhase'
        baseTrackPhase = getattr(calculator, trackPhaseName, None)
        if baseTrackPhase:
            def calculateToonTrackPhase(track):
                if self._shouldDeferToonMoves():
                    self._deferredToonCalls.append((
                        calculateToonTrackPhase, (track,)))
                    return None
                return baseTrackPhase(track)
            setattr(calculator, trackPhaseName, calculateToonTrackPhase)

        lureTimeoutName = '_BattleCalculatorAI__updateLureTimeouts'
        baseLureTimeout = getattr(calculator, lureTimeoutName, None)
        if baseLureTimeout:
            def updateLureTimeouts():
                if self._shouldDeferToonMoves():
                    self._deferredToonCalls.append((updateLureTimeouts, ()))
                    return None
                return baseLureTimeout()
            setattr(calculator, lureTimeoutName, updateLureTimeouts)

        baseInterceptor = calculator.applyCogDamageInterceptors
        def applyCogDamageInterceptors(attackDamage, toonId, suit, targetId, atkTrack):
            attackDamage = baseInterceptor(attackDamage, toonId, suit, targetId, atkTrack)
            controller = self._controller()
            if not controller or attackDamage <= 0 or atkTrack in (HEAL, SUE, FIRE):
                return attackDamage
            charonId = getattr(controller, 'charonStandupSuitId', 0)
            if not charonId or targetId == charonId:
                return attackDamage
            charon = self.battle.findSuit(charonId)
            if not charon or charon.getHP() <= 0:
                return attackDamage
            absorbed = int(math.ceil(attackDamage * 0.4))
            controller.charonAbsorbedDamage += absorbed
            return max(0, attackDamage - absorbed)
        calculator.applyCogDamageInterceptors = applyCogDamageInterceptors

        addLuredName = '_BattleCalculatorAI__addLuredSuitInfo'
        baseAddLured = getattr(calculator, addLuredName, None)
        if baseAddLured:
            def addLuredSuitInfo(suitId, currRounds, maxRounds, wakeChance, lurer, lureLvl, lureId=-1, npc=0):
                suit = self.battle.findSuit(suitId)
                investor = bool(suit and getattr(getattr(suit, 'dna', None), 'name', '') in self.Investors)
                if investor and maxRounds > 0:
                    maxRounds = 2
                result = baseAddLured(suitId, currRounds, maxRounds, wakeChance, lurer, lureLvl, lureId, npc)
                if investor:
                    info = getattr(calculator, 'currentlyLuredSuits', {}).get(suitId)
                    if info and info[1] > 2:
                        info[1] = 2
                return result
            setattr(calculator, addLuredName, addLuredSuitInfo)

        applySuitName = '_BattleCalculatorAI__applySuitAttackDamages'
        baseApplySuit = getattr(calculator, applySuitName, None)
        if baseApplySuit:
            def applySuitAttackDamages(attack, theSuit):
                disabled = []
                attackName = ''
                try:
                    attackName = attack[SUIT_ATK_COL].get('name', '')
                except:
                    pass
                controller = self._controller()
                if controller and theSuit and getattr(getattr(theSuit, 'dna', None), 'name', '') == 'pcrat' and not attackName.startswith('PlutocratCore'):
                    bonus = max(0, controller.marketBubbleStacks) * 3
                    if bonus:
                        for toonId in self.battle.activeToons:
                            pos = self.battle.activeToons.index(toonId)
                            if attack[SUIT_HP_COL][pos] > 0:
                                attack[SUIT_HP_COL][pos] += bonus
                for toonId in self.battle.activeToons:
                    if not self.toonHasCondition(toonId, 'plutocratDeepFreeze'):
                        continue
                    pos = self.battle.activeToons.index(toonId)
                    status = getattr(calculator, 'toonStatusConditions', {}).get(toonId, {}).get('plutocratDeepFreeze')
                    if status:
                        disabled.append((status, status.get('modifier', 0.8)))
                        status['modifier'] = 1.0
                    if attack[SUIT_HP_COL][pos] > 0 and attackName != 'PlutocratCoreSnowSquallDamage':
                        attack[SUIT_HP_COL][pos] = int(math.floor(attack[SUIT_HP_COL][pos] * 0.8))
                try:
                    return baseApplySuit(attack, theSuit)
                finally:
                    for status, modifier in disabled:
                        status['modifier'] = modifier
            setattr(calculator, applySuitName, applySuitAttackDamages)

    def _shouldDeferToonMoves(self):
        if self._replayingDeferredToons:
            return False
        controller = self._controller()
        return bool(controller and getattr(
            controller, 'deepFreezeRoundActive', False))

    def _replayDeferredToonMoves(self):
        if not self._deferredToonCalls:
            return
        calls = self._deferredToonCalls
        self._deferredToonCalls = []
        self._replayingDeferredToons = True
        try:
            for function, args in calls:
                function(*args)
        finally:
            self._replayingDeferredToons = False

    def _clearKerberosDebuffs(self, suit):
        if not suit:
            return
        self._unlure(suit)
        keep = set(('plutocratFrozen', 'dead'))
        negative = set((
            'soaked', 'drenched', 'dazed', 'dazed2', 'sleepy', 'marked',
            'markedThrow', 'vulnerable', 'damageReduction', 'monsoon',
            'trapRushJob', 'lureRushJob', 'throwRushJob', 'squirtRushJob',
            'zapRushJob', 'soundRushJob', 'dropRushJob', 'unlureSuit',
        ))
        legacy = getattr(self.calculator, 'suitStatusConditions', {}).get(suit.doId, {})
        for condition in list(legacy.keys()):
            if condition in negative and condition not in keep:
                self.setSuitCondition(suit.doId, condition, 0, 0, 'setBoth')
        effects = getattr(self.calculator, 'suitStatusConditionsNew', {}).get(suit.doId)
        if effects is not None:
            kept = []
            for effect in effects:
                if isinstance(effect, StatusEffects.Trapped):
                    kept.append(effect)
                elif getattr(effect, 'good', False):
                    kept.append(effect)
            effects[:] = kept

    def _applyStandupAbsorption(self, controller):
        charonId = getattr(controller, 'charonStandupSuitId', 0)
        if not charonId:
            return
        charon = self.battle.findSuit(charonId)
        if not charon or charon.getHP() <= 0:
            return
        fireAbsorb = 0
        for toonId in self.battle.activeToons:
            attack = self.battle.toonAttacks.get(toonId)
            if not attack:
                continue
            try:
                if attack[TOON_TRACK_COL] != FIRE or attack[TOON_TGT_COL] == charonId:
                    continue
                for value in attack[TOON_HP_COL]:
                    if value > 0:
                        fireAbsorb += int(math.ceil(value * 0.4))
            except:
                pass
        controller.charonAbsorbedDamage += fireAbsorb
        damage = min(charon.getHP(), int(controller.charonAbsorbedDamage))
        if damage <= 0:
            return
        charon.b_setHP(charon.getHP() - damage)
        controller.charonAbsorbedDamage = 0
        if charon.getHP() <= 0:
            if not self.suitHasCondition(charon.doId, 'dead'):
                self.setSuitCondition(charon.doId, 'dead', 1, 2, 'setBoth')
                self.calculator.deadSuits += 1
            self.suitLeftBattle(charon.doId)

    def _controller(self):
        controller = getattr(self.battle, 'bossCog', None)
        if controller is None or not hasattr(controller, 'plutocratPhase'):
            return None
        return controller

    def _aliveSuits(self):
        result = []
        for suit in self.battle.activeSuits:
            try:
                if suit.getHP() > 0:
                    result.append(suit)
            except:
                pass
        return result

    def _find(self, name):
        for suit in self._aliveSuits():
            try:
                if suit.dna.name == name:
                    return suit
            except:
                pass
        return None

    def _visual(self, suit, name, beforeToons=False, group=SuitBattleGlobals.ATK_TGT_SINGLE):
        if not suit:
            return None
        attack = self.calculator.getCheatAttack(suit.doId, {
            'suitName': suit.dna.name,
            'name': name,
            'animName': 'nothing',
            'hp': 0,
            'acc': 100,
            'freq': 0,
            'group': group,
        })
        if attack[SUIT_ATK_COL]:
            attack[SUIT_BEFORE_TOONS_COL] = 1 if beforeToons else 0
            self.battle.suitAttacks.append(attack)
            return attack
        return None

    def _targeted(self, suit, name, toonIds, damages):
        if not suit or not toonIds:
            return None
        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = suit.doId
        attack[SUIT_ATK_COL] = {
            'suitName': suit.dna.name,
            'name': name,
            'animName': 'nothing',
            'hp': 0,
            'acc': 100,
            'freq': 0,
            'group': SuitBattleGlobals.ATK_TGT_GROUP if len(toonIds) > 1 else SuitBattleGlobals.ATK_TGT_SINGLE,
        }
        attack[SUIT_TGT_COL] = []
        attack[SUIT_HP_COL] = [-1 for i in xrange(len(self.battle.activeToons))]
        attack[TOON_DIED_COL] = 0
        attack[SUIT_BEFORE_TOONS_COL] = 0
        attack[SUIT_TAUNT_COL] = 0
        for toonId, damage in zip(toonIds, damages):
            if toonId not in self.battle.activeToons:
                continue
            index = self.battle.activeToons.index(toonId)
            attack[SUIT_TGT_COL].append(index)
            attack[SUIT_HP_COL][index] = max(0, int(math.ceil(damage)))
        if not attack[SUIT_TGT_COL]:
            return None
        self.calculator._BattleCalculatorAI__applySuitAttackDamages(attack, suit)
        self.battle.suitAttacks.append(attack)
        return attack

    def _refreshInvestorDamage(self, controller):
        ghost = {0: 1.0, 1: 1.3, 2: 1.6}.get(min(2, controller.investorDeaths), 1.6)
        for suit in self._aliveSuits():
            try:
                if suit.dna.name in self.Investors:
                    kickup = controller.investorKickUpMultipliers.get(suit.doId, 1.0)
                    suit.setDamageMultiplier((ghost * kickup) if controller.plutocratPhase == 1 else kickup)
            except:
                pass
        if (controller.plutocratPhase == 1 and
                controller.investorDeaths > controller.ghostPayrollVisualDeaths):
            for suit in self._aliveSuits():
                try:
                    if suit.dna.name in self.Investors:
                        self._visual(suit, 'PlutocratCoreGhostPayroll')
                except:
                    pass
            controller.ghostPayrollVisualDeaths = controller.investorDeaths

    def _marketBubbleHits(self, pcrat):
        if not pcrat:
            return 0
        try:
            index = self.battle.activeSuits.index(pcrat)
        except:
            return 0
        hits = 0
        for toonId in self.battle.activeToons:
            attack = self.battle.toonAttacks.get(toonId)
            if not attack:
                continue
            try:
                hp = attack[TOON_HP_COL]
                if index < len(hp) and hp[index] > 0:
                    hits += 1
            except:
                pass
        return hits

    def _advanceInvestorTurns(self, controller):
        if not hasattr(controller, 'investorTurnCounts'):
            controller.investorTurnCounts = {}
        aliveIds = set()
        for suit in self._aliveSuits():
            try:
                if suit.dna.name in self.Investors:
                    aliveIds.add(suit.doId)
                    controller.investorTurnCounts[suit.doId] = (
                        controller.investorTurnCounts.get(suit.doId, 0) + 1)
            except:
                pass
        for suitId in list(controller.investorTurnCounts.keys()):
            if suitId not in aliveIds and self.battle.findSuit(suitId) is None:
                del controller.investorTurnCounts[suitId]

    def _investorTurn(self, controller, suit):
        if not suit:
            return 0
        return getattr(controller, 'investorTurnCounts', {}).get(suit.doId, 0)

    def _currentRound(self, controller):
        return int(controller.investorRound + controller.plutocratRound)

    def _unlure(self, suit):
        if not suit:
            return
        try:
            self.calculator.removeLured(suit.doId)
        except:
            pass

    def _deepFreezeActive(self):
        for toonId in self.battle.activeToons:
            if self.toonHasCondition(toonId, 'plutocratDeepFreeze'):
                return True
        return False

    def _convertSoakToFrozen(self, controller):
        if controller.plutocratPhase != 2:
            return
        for suit in list(self.battle.activeSuits):
            if not suit:
                continue
            rounds = 0
            for condition in ('drenched', 'soaked'):
                if self.suitHasCondition(suit.doId, condition):
                    rounds = max(rounds, self.getSuitConditionTurns(suit.doId, condition))
                    self.setSuitCondition(suit.doId, condition, 0, 0, 'setBoth')
            if rounds:
                if rounds < 0:
                    rounds = 1
                self.setSuitCondition(suit.doId, 'plutocratFrozen', 1, rounds, 'setBoth')
                self._visual(
                    suit,
                    'PlutocratCoreFreezeSuit_%s_%s' % (suit.doId, rounds),
                    False,
                    SuitBattleGlobals.ATK_TGT_GROUP)

    def _isFrozen(self, controller, suit):
        return bool(
            controller.snowSquallActive or
            self.suitHasCondition(suit.doId, 'plutocratFrozen'))

    def _cancelPreparedReward(self, toonId):
        attack = self.battle.toonAttacks.get(toonId)
        if not attack:
            return
        try:
            if attack[TOON_TRACK_COL] in (FIRE, SUE, SOS, NPCSOS):
                self.battle.toonAttacks[toonId] = getToonAttack(toonId)
        except:
            pass

    def _shortenInvestorDamageDowns(self):
        source = getattr(self.calculator, 'suitStatusConditionsNew', {})
        for suit in self._aliveSuits():
            try:
                if suit.dna.name not in self.Investors:
                    continue
            except:
                continue
            for effect in source.get(suit.doId, []):
                if not isinstance(effect, StatusEffects.DamageModifier):
                    continue
                if getattr(effect, 'good', True):
                    continue
                if getattr(effect, '_plutocratInvestorShortened', False):
                    continue
                if getattr(effect, 'roundsLeft', -1) > 1:
                    effect.roundsLeft -= 1
                effect._plutocratInvestorShortened = True

    def calculatePreToonAttacks(self):
        controller = self._controller()
        if not controller:
            return
        controller.deepFreezeTriggeredThisRound = False
        controller.pendingDeepFreezeCount = 0
        controller.deepFreezeRoundActive = self._deepFreezeActive()
        self._deferredToonCalls = []
        controller.charonStandupSuitId = 0
        controller.charonAbsorbedDamage = 0
        if not hasattr(controller, 'snowSquallDamageRounds'):
            controller.snowSquallDamageRounds = 0
        if controller.plutocratPhase == 1:
            controller.investorRound += 1
        else:
            controller.plutocratRound += 1
        self._advanceInvestorTurns(controller)

        charon = self._find('charon')
        if charon:
            chance = controller.charonAbsorbChance.get(charon.doId, 0.0) + 0.25
            if random.random() < chance:
                controller.charonAbsorbChance[charon.doId] = 0.0
                controller.charonStandupSuitId = charon.doId
                self._unlure(charon)
                self._visual(charon, 'PlutocratCoreStandupGuy', True)
            else:
                controller.charonAbsorbChance[charon.doId] = chance

        nix = self._find('nix')
        if nix and self.battle.activeToons:
            self._unlure(nix)
            toonId = random.choice(self.battle.activeToons)
            self._cancelPreparedReward(toonId)
            cooldown = self.toonHasCondition(toonId, 'plutocratRewardCooldown')
            vulnerable = self.toonHasCondition(toonId, 'plutocratVulnerable')
            if cooldown or vulnerable:
                for condition in ('noSOS', 'noFires', 'noSues', 'noUnites', 'noForges', 'plutocratRewardCooldown'):
                    self.setToonCondition(toonId, condition, 0, 0, 'setBoth')
                self.setToonCondition(toonId, 'plutocratVulnerable', 1.2, 3, 'setBoth')
                mode = 1
            else:
                self.setToonCondition(toonId, 'plutocratVulnerable', 0, 0, 'setBoth')
                for condition in ('noSOS', 'noFires', 'noSues', 'noUnites', 'noForges', 'plutocratRewardCooldown'):
                    self.setToonCondition(toonId, condition, 1, 3, 'setBoth')
                mode = 0
            self._visual(nix, 'PlutocratCoreShakedown_%s_%s' % (toonId, mode), True)

        self._doHydra(controller)
        self._doKerberos(controller)
        self._doStyx(controller)

        if controller.plutocratPhase == 2:
            currentRound = self._currentRound(controller)
            if not getattr(controller, 'slushFundNextRound', 0):
                firstRound = max(7, currentRound)
                controller.slushFundNextRound = firstRound + ((1 - firstRound) % 3)
            if currentRound >= controller.slushFundNextRound:
                pcrat = self._find('pcrat')
                performers = [suit for suit in self._aliveSuits()
                              if getattr(getattr(suit, 'dna', None), 'name', '') in self.Investors]
                performer = random.choice(performers) if performers else pcrat
                targets = [suit for suit in self._aliveSuits() if suit is not performer]
                if performer and targets:
                    self._unlure(performer)
                    for suit in targets:
                        self.setSuitCondition(suit.doId, 'plutocratSlushFund', 0.8, 2, 'setBoth')
                    self._visual(performer, 'PlutocratCoreSlushFund', True, SuitBattleGlobals.ATK_TGT_GROUP)
                    controller.slushFundNextRound += 3

    def _doHydra(self, controller):
        hydra = self._find('hydra')
        if not hydra:
            return
        self._unlure(hydra)
        investors = []
        grunts = []
        for suit in self._aliveSuits():
            if suit is hydra:
                continue
            try:
                if suit.dna.name == 'pcrat':
                    continue
                if suit.dna.name in self.Investors:
                    investors.append(suit)
                elif not suit.getManager():
                    grunts.append(suit)
            except:
                pass
        targets = []
        if investors:
            targets = [random.choice(investors)]
        elif controller.plutocratPhase == 2 and grunts:
            count = min(2, len(grunts))
            targets = random.sample(grunts, count)
        else:
            targets = [hydra]
        for target in targets:
            isInvestor = False
            try:
                isInvestor = target.dna.name in self.Investors
            except:
                pass
            boost = 1.1 if isInvestor or target is hydra else 1.2
            current = (
                controller.investorKickUpMultipliers.get(target.doId, 1.0) *
                boost)
            controller.investorKickUpMultipliers[target.doId] = current
            ghost = {0: 1.0, 1: 1.3, 2: 1.6}.get(
                min(2, controller.investorDeaths), 1.6)
            try:
                target.setDamageMultiplier(
                    current * ghost if isInvestor else current)
            except:
                pass
            self._visual(hydra, 'PlutocratCoreKickUp_%s' % target.doId, True)

    def _doKerberos(self, controller):
        kerberos = self._find('kerberos')
        if not kerberos or self._investorTurn(controller, kerberos) % 2 != 1:
            return

        candidates = []
        for suit in self._aliveSuits():
            if suit is kerberos:
                continue
            try:
                if suit.dna.name != 'pcrat':
                    candidates.append(suit)
            except:
                pass

        def levelKey(suit):
            try:
                return suit.getActualLevel()
            except:
                try:
                    return suit.getLevel()
                except:
                    return 0

        target = None
        if candidates:
            if controller.plutocratPhase == 2:
                highest = max([levelKey(suit) for suit in candidates])
                choices = [suit for suit in candidates if levelKey(suit) == highest]
                target = random.choice(choices)
            else:
                lowest = min([levelKey(suit) for suit in candidates])
                choices = [suit for suit in candidates if levelKey(suit) == lowest]
                target = random.choice(choices)

        self._unlure(kerberos)
        if target:
            self._unlure(target)

        damage = int(math.ceil(kerberos.getHP() * 0.10))
        damage = min(damage, kerberos.getHP())
        if damage <= 0:
            return
        kerberos.b_setHP(kerberos.getHP() - damage)
        self.setSuitCondition(kerberos.doId, 'cantAttack', 1, 1, 'setBoth')

        heal = 0
        if target:
            heal = int(math.ceil(damage * 2.5))
            isInvestor = getattr(getattr(target, 'dna', None), 'name', '') in self.Investors
            if controller.plutocratPhase == 2:
                cap = int(target.getMaxHP() * 2.0)
            elif isInvestor:
                cap = int(target.getMaxHP() * 1.25)
            else:
                cap = int(target.getMaxHP() * 1.5)
            oldHp = target.getHP()
            target.b_setHP(min(cap, oldHp + heal))
            heal = max(0, target.getHP() - oldHp)
            self._clearKerberosDebuffs(target)

        targetId = target.doId if target else 0
        self._visual(kerberos, 'PlutocratCoreTribute_%s_%s_%s' % (targetId, damage, heal), True)
        if kerberos.getHP() <= 0:
            if not self.suitHasCondition(kerberos.doId, 'dead'):
                self.setSuitCondition(kerberos.doId, 'dead', 1, 2, 'setBoth')
                self.calculator.deadSuits += 1
            self.suitLeftBattle(kerberos.doId)

    def _fireGates(self, controller, pcrat):
        if not pcrat or pcrat.getMaxHP() <= 0:
            return
        hpPct = float(pcrat.getHP()) / float(pcrat.getMaxHP())
        for gate in (0.8, 0.4):
            if hpPct <= gate and gate not in controller.deepFreezeGates:
                controller.deepFreezeGates.add(gate)
                controller.deepFreezeTriggeredThisRound = True
                controller.pendingDeepFreezeCount = getattr(
                    controller, 'pendingDeepFreezeCount', 0) + 1

    def _applyPendingDeepFreeze(self, controller):
        count = getattr(controller, 'pendingDeepFreezeCount', 0)
        if count <= 0:
            return
        pcrat = self._find('pcrat')
        if not pcrat:
            controller.pendingDeepFreezeCount = 0
            return
        for unused in xrange(count):
            self._unlure(pcrat)
            for toonId in self.battle.activeToons:
                self.setToonCondition(
                    toonId, 'plutocratDeepFreeze', 0.8, 2, 'setBoth')
                self.setToonCondition(
                    toonId, 'noUnites', 1, 2, 'setBoth')
            self._visual(
                pcrat, 'PlutocratCoreDeepFreeze_2', False,
                SuitBattleGlobals.ATK_TGT_GROUP)
            controller.queueRemainingInvestor()
        controller.pendingDeepFreezeCount = 0

    def _toonKillingTrack(self, suitIndex):
        killingTrack = None
        for toonId in self.battle.activeToons:
            attack = self.battle.toonAttacks.get(toonId)
            if not attack:
                continue
            try:
                died = attack[SUIT_DIED_COL] & (1 << suitIndex)
                if died:
                    killingTrack = attack[TOON_TRACK_COL]
            except:
                pass
        return killingTrack

    def _markShatterDeath(self, suit):
        if not suit or suit.getHP() > 0:
            return
        if not self.suitHasCondition(suit.doId, 'dead'):
            self.setSuitCondition(suit.doId, 'dead', 1, 2, 'setBoth')
            self.calculator.deadSuits += 1
        self.suitLeftBattle(suit.doId)

    def _queueShatters(self, controller):
        suits = list(self.battle.activeSuits)
        pending = []
        processed = set()
        for index, suit in enumerate(suits):
            killingTrack = self._toonKillingTrack(index)
            if (killingTrack is not None and killingTrack != FIRE and
                    self._isFrozen(controller, suit)):
                pending.append(suit)
        while pending:
            shattered = pending.pop(0)
            if shattered.doId in processed:
                continue
            processed.add(shattered.doId)
            try:
                index = suits.index(shattered)
            except:
                continue
            targets = []
            if index > 0:
                targets.append(suits[index - 1])
            if index < len(suits) - 1:
                targets.append(suits[index + 1])
            encoded = []
            baseDamage = int(math.ceil(shattered.getMaxHP() * 0.50))
            for target in targets:
                try:
                    if target.getHP() <= 0:
                        continue
                except:
                    continue
                damage = baseDamage
                burst = 0
                try:
                    if (controller.plutocratPhase == 2 and
                            target.dna.name == 'charon'):
                        damage = int(math.ceil(shattered.getMaxHP() * 3.0))
                    if target.dna.name == 'pcrat':
                        stacks = controller.marketBubbleStacks
                        if stacks > 0:
                            damage = int(math.ceil(
                                damage * (1.0 + min(0.05 * stacks, 1.0))))
                            controller.marketBubbleStacks = -2
                            self.setSuitCondition(
                                target.doId, 'plutocratSlushFund',
                                0, 0, 'setBoth')
                            burst = 1
                        elif stacks == 0:
                            controller.marketBubbleStacks = 1
                        elif stacks < 0:
                            damage = int(math.ceil(damage * 1.25))
                except:
                    pass
                damage = min(damage, target.getHP())
                if damage <= 0:
                    continue
                target.b_setHP(max(0, target.getHP() - damage))
                died = 1 if target.getHP() <= 0 else 0
                if died:
                    wasFrozen = self._isFrozen(controller, target)
                    if target.doId not in processed and wasFrozen:
                        pending.append(target)
                    self._markShatterDeath(target)
                encoded.extend((
                    str(target.doId), str(damage),
                    str(burst), str(died)))
            if encoded:
                self._visual(
                    shattered,
                    'PlutocratCoreShatter_%s_%s' % (
                        shattered.doId, '_'.join(encoded)),
                    False,
                    SuitBattleGlobals.ATK_TGT_GROUP)

    def calculateBeforeSuitAttacks(self):
        controller = self._controller()
        if not controller:
            return
        self._shortenInvestorDamageDowns()
        if getattr(controller, 'deepFreezeRoundActive', False):
            self._refreshInvestorDamage(controller)
            return
        self._applyStandupAbsorption(controller)
        self._refreshInvestorDamage(controller)
        self._convertSoakToFrozen(controller)
        self._queueShatters(controller)
        if controller.plutocratPhase == 2:
            pcrat = self._find('pcrat')
            if pcrat:
                hits = self._marketBubbleHits(pcrat)
                if hits and controller.marketBubbleStacks >= 0:
                    controller.marketBubbleStacks += hits
                pcrat.setDamageMultiplier(1.0)
                self._fireGates(controller, pcrat)

    def _findWaiter(self):
        for suit in self._aliveSuits():
            try:
                if suit.getWaiter():
                    return suit
            except:
                if getattr(suit, 'isWaiter', 0):
                    return suit
        return None

    def _doStyx(self, controller):
        styx = self._find('styx')
        if not styx:
            return
        waiter = self._findWaiter()
        if waiter:
            self._unlure(styx)
            damage = int(math.ceil(min(waiter.getMaxHP() / 3.0, waiter.getHP())))
            if damage > 0:
                waiter.b_setHP(max(0, waiter.getHP() - damage))
                styx.b_setHP(min(int(styx.getMaxHP() * 1.25), styx.getHP() + damage))
                self._visual(styx, 'PlutocratCoreUsuryWaiter_%s_%s' % (waiter.doId, damage), True)
                if waiter.getHP() <= 0 and not self.suitHasCondition(waiter.doId, 'dead'):
                    self.setSuitCondition(waiter.doId, 'dead', 1, 2, 'setBoth')
                    self.calculator.deadSuits += 1
                    self.suitLeftBattle(waiter.doId)
            return
        if self._currentRound(controller) % 4 != 1:
            return
        if self._deepFreezeActive():
            return
        if controller.plutocratPhase == 1 or len(self._aliveSuits()) < self.battle.maxSuits:
            self._unlure(styx)
            controller.queueStyxWaiter()
            self._visual(styx, 'PlutocratCoreSitdown', True)
            return
        if controller.plutocratPhase != 2:
            return
        fodders = []
        for suit in self._aliveSuits():
            if suit is styx:
                continue
            try:
                if not suit.getManager():
                    fodders.append(suit)
            except:
                pass
        if not fodders:
            return
        self._unlure(styx)
        total = 0
        ids = []
        for target in fodders:
            damage = int(math.ceil(min(target.getMaxHP() * 0.75, target.getHP())))
            if damage <= 0:
                continue
            target.b_setHP(max(0, target.getHP() - damage))
            total += damage
            ids.append(str(target.doId))
            if target.getHP() <= 0 and not self.suitHasCondition(target.doId, 'dead'):
                self.setSuitCondition(target.doId, 'dead', 1, 2, 'setBoth')
                self.calculator.deadSuits += 1
                self.suitLeftBattle(target.doId)
        if total:
            styx.b_setHP(min(int(styx.getMaxHP() * 1.5), styx.getHP() + total))
            self._visual(styx, 'PlutocratCoreUsuryFodder_%s' % '_'.join(ids), True)

    def _removeDefeatedSuitAttacks(self):
        kept = []
        for attack in self.battle.suitAttacks:
            attackInfo = attack[SUIT_ATK_COL]
            if not attackInfo:
                kept.append(attack)
                continue
            attackName = attackInfo.get('name', '')
            if attackName.startswith('PlutocratCore'):
                kept.append(attack)
                continue
            suitId = attack[SUIT_ID_COL]
            suit = self.battle.findSuit(suitId)
            defeated = suit is None
            if suit is not None:
                try:
                    defeated = suit.getHP() <= 0 or self.suitHasCondition(suitId, 'dead')
                except:
                    defeated = True
            if not defeated:
                kept.append(attack)
        self.battle.suitAttacks[:] = kept

    def calculatePostSuitAttacks(self):
        controller = self._controller()
        if not controller:
            return
        deepFreezeRound = bool(getattr(
            controller, 'deepFreezeRoundActive', False))
        if deepFreezeRound:
            self._replayDeferredToonMoves()
            self._shortenInvestorDamageDowns()
            self._applyStandupAbsorption(controller)
            self._convertSoakToFrozen(controller)
            self._queueShatters(controller)
            if controller.plutocratPhase == 2:
                pcrat = self._find('pcrat')
                if pcrat:
                    hits = self._marketBubbleHits(pcrat)
                    if hits and controller.marketBubbleStacks >= 0:
                        controller.marketBubbleStacks += hits
                    pcrat.setDamageMultiplier(1.0)
                    self._fireGates(controller, pcrat)
        self._applyPendingDeepFreeze(controller)
        if controller.plutocratPhase == 2:
            pcrat = self._find('pcrat')
            if controller.snowSquallActive and pcrat and controller.snowSquallDamageRounds > 0:
                if not controller.deepFreezeTriggeredThisRound:
                    toonIds = []
                    damages = []
                    damageAmount = 12 if self._deepFreezeActive() else 15
                    for toonId in self.battle.activeToons:
                        toon = self.battle.getToon(toonId)
                        if toon and toon.getHp() > 0:
                            toonIds.append(toonId)
                            damages.append(min(damageAmount, toon.getHp()))
                    self._targeted(pcrat, 'PlutocratCoreSnowSquallDamage', toonIds, damages)
                controller.snowSquallDamageRounds -= 1

            currentRound = self._currentRound(controller)
            if pcrat and currentRound >= 9 and currentRound % 2 == 1:
                controller.queueNaturalReserves(2)
            if pcrat and currentRound >= 7 and currentRound % 3 == 1:
                nextSnowState = not controller.snowSquallActive
                self._unlure(pcrat)
                self._visual(pcrat, 'PlutocratCoreSnowSquall_%s' % (1 if nextSnowState else 0), False, SuitBattleGlobals.ATK_TGT_GROUP)
                controller.snowSquallActive = nextSnowState
                controller.snowSquallDamageRounds = 2 if nextSnowState else 0
            if controller.marketBubbleStacks < 0:
                controller.marketBubbleStacks += 1
        if not deepFreezeRound:
            self._removeDefeatedSuitAttacks()
        controller.deepFreezeRoundActive = False

