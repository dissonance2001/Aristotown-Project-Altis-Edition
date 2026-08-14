from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
import math
import random


class PlutocratCalculatorAI:
    Investors = ('charon', 'nix', 'hydra', 'styx', 'kerberos')

    def __init__(self, calculator):
        self.calculator = calculator
        self.battle = calculator.battle

    def __getattr__(self, name):
        return getattr(self.calculator, name)

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
                track = attack[TOON_TRACK_COL]
                hp = attack[TOON_HP_COL]
                if track != LURE and index < len(hp) and hp[index] > 0:
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

    def calculatePreToonAttacks(self):
        controller = self._controller()
        if not controller:
            return
        controller.deepFreezeTriggeredThisRound = False
        if not hasattr(controller, 'snowSquallDamageRounds'):
            controller.snowSquallDamageRounds = 0
        if controller.plutocratPhase == 1:
            controller.investorRound += 1
        else:
            controller.plutocratRound += 1
        self._advanceInvestorTurns(controller)
        charon = self._find('charon')
        if charon:
            if controller.plutocratPhase == 2:
                self.setSuitCondition(
                    charon.doId, 'directorDamageReduction', 0.8, 1, 'setBoth')
            chance = controller.charonAbsorbChance.get(charon.doId, 0.0) + 0.25
            if random.random() < chance:
                controller.charonAbsorbChance[charon.doId] = 0.0
                self._unlure(charon)
                self.setSuitCondition(charon.doId, 'directorDamageReduction', 0.6, 1, 'setBoth')
                self._visual(charon, 'PlutocratCoreStandupGuy', True)
            else:
                controller.charonAbsorbChance[charon.doId] = chance
        nix = self._find('nix')
        if nix and self.battle.activeToons:
            self._unlure(nix)
            toonId = random.choice(self.battle.activeToons)
            cooldown = self.toonHasCondition(
                toonId, 'plutocratRewardCooldown')
            vulnerable = self.toonHasCondition(
                toonId, 'plutocratVulnerable')
            if cooldown or vulnerable:
                for condition in (
                        'noSOS', 'noFires', 'noSues', 'noUnites',
                        'noForges', 'plutocratRewardCooldown'):
                    self.setToonCondition(
                        toonId, condition, 0, 0, 'setBoth')
                self.setToonCondition(
                    toonId, 'plutocratVulnerable', 1.2, 3, 'setBoth')
                mode = 1
            else:
                self.setToonCondition(
                    toonId, 'plutocratVulnerable', 0, 0, 'setBoth')
                for condition in (
                        'noSOS', 'noFires', 'noSues', 'noUnites',
                        'noForges', 'plutocratRewardCooldown'):
                    self.setToonCondition(
                        toonId, condition, 1, 3, 'setBoth')
                mode = 0
            self._visual(
                nix,
                'PlutocratCoreShakedown_%s_%s' % (toonId, mode),
                True)
        if controller.plutocratPhase == 2:
            if self._currentRound(controller) % 3 == 1:
                pcrat = self._find('pcrat')
                performers = [s for s in self._aliveSuits() if getattr(getattr(s, 'dna', None), 'name', '') in self.Investors]
                performer = performers[0] if performers else pcrat
                self._unlure(performer)
                for suit in self._aliveSuits():
                    if suit is performer:
                        continue
                    self.setSuitCondition(suit.doId, 'directorDamageReduction', 0.8, 2, 'setBoth')
                self._visual(performer, 'PlutocratCoreSlushFund', True, SuitBattleGlobals.ATK_TGT_GROUP)
            pcrat = self._find('pcrat')
            if pcrat:
                if controller.marketBubbleStacks < 0:
                    self.setSuitCondition(
                        pcrat.doId, 'directorDamageReduction', 1.25, 1, 'setBoth')
                elif self.suitHasCondition(pcrat.doId, 'directorDamageReduction'):
                    if abs(self.getSuitConditionModifier(
                            pcrat.doId, 'directorDamageReduction') - 1.25) < 0.001:
                        self.setSuitCondition(
                            pcrat.doId, 'directorDamageReduction', 0, 0, 'setBoth')

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
            self._visual(hydra, 'PlutocratCoreKickUp_%s' % target.doId)

    def _doKerberos(self, controller):
        kerberos = self._find('kerberos')
        if not kerberos or self._currentRound(controller) % 2 != 1:
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
        if not candidates:
            return
        if controller.plutocratPhase == 2:
            def levelKey(suit):
                try:
                    return suit.getActualLevel()
                except:
                    try:
                        return suit.getLevel()
                    except:
                        return 0
            target = max(candidates, key=levelKey)
        else:
            candidates.sort(key=lambda s: s.getHP())
            investorCandidates = [
                s for s in candidates
                if getattr(s.dna, 'name', '') in self.Investors]
            target = investorCandidates[0] if investorCandidates else candidates[0]
        self._unlure(kerberos)
        self._unlure(target)
        isInvestor = getattr(target.dna, 'name', '') in self.Investors
        damage = int(math.ceil(
            kerberos.getHP() * (0.10 if isInvestor else 0.05)))
        damage = min(damage, max(0, kerberos.getHP() - 1))
        if damage <= 0:
            return
        kerberos.b_setHP(kerberos.getHP() - damage)
        heal = (
            int(math.ceil(damage * 2.5)) if isInvestor else
            int(math.ceil(target.getMaxHP() * 0.5)))
        if controller.plutocratPhase == 2:
            cap = int(target.getMaxHP() * 2.0)
        else:
            cap = int(target.getMaxHP() * (1.25 if isInvestor else 1.5))
        target.b_setHP(min(cap, target.getHP() + heal))
        self._visual(kerberos, 'PlutocratCoreTribute_%s_%s_%s' % (
            target.doId, damage, heal))

    def _fireGates(self, controller, pcrat):
        if not pcrat or pcrat.getMaxHP() <= 0:
            return
        hpPct = float(pcrat.getHP()) / float(pcrat.getMaxHP())
        for gate in (0.8, 0.4):
            if hpPct <= gate and gate not in controller.deepFreezeGates:
                controller.deepFreezeGates.add(gate)
                controller.deepFreezeTriggeredThisRound = True
                self._unlure(pcrat)
                for toonId in self.battle.activeToons:
                    self.setToonCondition(toonId, 'plutocratDeepFreeze', 0.8, 2, 'setBoth')
                    self.setToonCondition(toonId, 'noUnites', 1, 2, 'setBoth')
                self._visual(pcrat, 'PlutocratCoreDeepFreeze_2', False, SuitBattleGlobals.ATK_TGT_GROUP)
                controller.queueRemainingInvestor()

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
                        if stacks >= 0:
                            if stacks > 0:
                                damage = int(math.ceil(
                                    damage * (1.0 + min(0.05 * stacks, 1.0))))
                            controller.marketBubbleStacks = -2
                            self.setSuitCondition(
                                target.doId, 'directorDamageReduction',
                                0, 0, 'setBoth')
                            burst = 1
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
        self._refreshInvestorDamage(controller)
        self._convertSoakToFrozen(controller)
        self._queueShatters(controller)
        self._doHydra(controller)
        self._doKerberos(controller)
        if controller.plutocratPhase == 2:
            pcrat = self._find('pcrat')
            if pcrat:
                hits = self._marketBubbleHits(pcrat)
                if hits and controller.marketBubbleStacks >= 0:
                    controller.marketBubbleStacks += hits
                pcrat.setDamageMultiplier(
                    1.0 + (max(0, controller.marketBubbleStacks) * 0.03))
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
                self._visual(styx, 'PlutocratCoreUsuryWaiter_%s_%s' % (waiter.doId, damage))
            return
        if self._currentRound(controller) % 4 != 1:
            return
        if self._deepFreezeActive():
            return
        if len(self._aliveSuits()) < self.battle.maxSuits:
            self._unlure(styx)
            controller.queueStyxWaiter()
            self._visual(styx, 'PlutocratCoreSitdown')
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
        if total:
            styx.b_setHP(min(int(styx.getMaxHP() * 1.5), styx.getHP() + total))
            self._visual(styx, 'PlutocratCoreUsuryFodder_%s' % '_'.join(ids))

    def _removeDefeatedSuitAttacks(self):
        kept = []
        for attack in self.battle.suitAttacks:
            attackInfo = attack[SUIT_ATK_COL]
            if not attackInfo:
                kept.append(attack)
                continue
            attackName = attackInfo.get('name', '')
            if (attackName.startswith('PlutocratCoreShatter_') or
                    attackName.startswith('PlutocratCoreFreezeSuit_')):
                kept.append(attack)
                continue
            suitId = attack[SUIT_ID_COL]
            suit = self.battle.findSuit(suitId)
            defeated = suit is None
            if suit is not None:
                try:
                    defeated = (
                        suit.getHP() <= 0 or
                        self.suitHasCondition(suitId, 'dead'))
                except:
                    defeated = True
            if not defeated:
                kept.append(attack)
        self.battle.suitAttacks[:] = kept

    def calculatePostSuitAttacks(self):
        controller = self._controller()
        if not controller:
            return
        self._doStyx(controller)
        if controller.plutocratPhase == 2:
            pcrat = self._find('pcrat')
            if (controller.snowSquallActive and pcrat and
                    controller.snowSquallDamageRounds > 0 and
                    not controller.deepFreezeTriggeredThisRound):
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
            if pcrat and currentRound % 2 == 1:
                controller.queueNaturalReserves(2)
            if pcrat and currentRound % 3 == 1:
                nextSnowState = not controller.snowSquallActive
                self._unlure(pcrat)
                self._visual(
                    pcrat,
                    'PlutocratCoreSnowSquall_%s' % (1 if nextSnowState else 0),
                    False,
                    SuitBattleGlobals.ATK_TGT_GROUP)
                controller.snowSquallActive = nextSnowState
                controller.snowSquallDamageRounds = 2 if nextSnowState else 0
            if controller.marketBubbleStacks < 0:
                controller.marketBubbleStacks += 1
        self._removeDefeatedSuitAttacks()
