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

    def calculatePreToonAttacks(self):
        controller = self._controller()
        if not controller:
            return
        if controller.plutocratPhase == 1:
            controller.investorRound += 1
            charon = self._find('charon')
            if charon:
                chance = controller.charonAbsorbChance.get(charon.doId, 0.25) + 0.25
                if random.random() < chance:
                    controller.charonAbsorbChance[charon.doId] = 0.0
                    self.setSuitCondition(charon.doId, 'directorDamageReduction', 0.6, 1, 'setBoth')
                    self._visual(charon, 'PlutocratCoreStandupGuy', True)
                else:
                    controller.charonAbsorbChance[charon.doId] = chance
            nix = self._find('nix')
            if nix and self.battle.activeToons:
                toonId = random.choice(self.battle.activeToons)
                cooldown = self.toonHasCondition(toonId, 'plutocratRewardCooldown')
                if cooldown:
                    self.setToonCondition(toonId, 'plutocratVulnerable', 1.2, 2, 'setBoth')
                    mode = 1
                else:
                    for condition in ('noSOS', 'noFires', 'noSues', 'noUnites', 'noForges', 'plutocratRewardCooldown'):
                        self.setToonCondition(toonId, condition, 1, 2, 'setBoth')
                    mode = 0
                self._visual(nix, 'PlutocratCoreShakedown_%s_%s' % (toonId, mode), True)
        elif controller.plutocratPhase == 2:
            controller.plutocratRound += 1
            if controller.plutocratRound % 3 == 1:
                pcrat = self._find('pcrat')
                performers = [s for s in self._aliveSuits() if getattr(getattr(s, 'dna', None), 'name', '') in self.Investors]
                performer = performers[0] if performers else pcrat
                for suit in self._aliveSuits():
                    if suit is performer:
                        continue
                    self.setSuitCondition(suit.doId, 'directorDamageReduction', 0.6, 1, 'setBoth')
                self._visual(performer, 'PlutocratCoreSlushFund', True, SuitBattleGlobals.ATK_TGT_GROUP)
                controller.snowSquallActive = not controller.snowSquallActive
                self._visual(pcrat, 'PlutocratCoreSnowSquall_%s' % (1 if controller.snowSquallActive else 0), False, SuitBattleGlobals.ATK_TGT_GROUP)

    def _doHydra(self, controller):
        hydra = self._find('hydra')
        if not hydra:
            return
        choices = []
        for suit in self._aliveSuits():
            if suit is hydra:
                continue
            try:
                if suit.getSkeleton() or suit.dna.name in self.Investors:
                    choices.append(suit)
            except:
                pass
        target = random.choice(choices) if choices else hydra
        current = controller.investorKickUpMultipliers.get(target.doId, 1.0) * 1.1
        controller.investorKickUpMultipliers[target.doId] = current
        ghost = {0: 1.0, 1: 1.3, 2: 1.6}.get(min(2, controller.investorDeaths), 1.6)
        try:
            target.setDamageMultiplier(current * ghost)
        except:
            pass
        self._visual(hydra, 'PlutocratCoreKickUp_%s' % target.doId)

    def _doKerberos(self, controller):
        if controller.investorRound % 2 != 1:
            return
        kerberos = self._find('kerberos')
        if not kerberos:
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
        candidates.sort(key=lambda s: s.getHP())
        investorCandidates = [s for s in candidates if getattr(s.dna, 'name', '') in self.Investors]
        target = investorCandidates[0] if investorCandidates else candidates[0]
        isInvestor = getattr(target.dna, 'name', '') in self.Investors
        damage = int(math.ceil(kerberos.getHP() * (0.10 if isInvestor else 0.05)))
        damage = min(damage, max(0, kerberos.getHP() - 1))
        if damage <= 0:
            return
        kerberos.b_setHP(kerberos.getHP() - damage)
        heal = damage * 2 if isInvestor else int(math.ceil(target.getMaxHP() * 0.5))
        cap = int(target.getMaxHP() * (1.25 if isInvestor else 1.5))
        target.b_setHP(min(cap, target.getHP() + heal))
        self._visual(kerberos, 'PlutocratCoreTribute_%s_%s_%s' % (target.doId, damage, heal))

    def _fireGates(self, controller, pcrat):
        if not pcrat or pcrat.getMaxHP() <= 0:
            return
        hpPct = float(pcrat.getHP()) / float(pcrat.getMaxHP())
        for gate in (0.8, 0.4):
            if hpPct <= gate and gate not in controller.deepFreezeGates:
                controller.deepFreezeGates.add(gate)
                for toonId in self.battle.activeToons:
                    self.setToonCondition(toonId, 'plutocratDeepFreeze', 0.8, 2, 'setBoth')
                    self.setToonCondition(toonId, 'noUnites', 1, 2, 'setBoth')
                self._visual(pcrat, 'PlutocratCoreDeepFreeze_2', False, SuitBattleGlobals.ATK_TGT_GROUP)
                controller.queueRemainingInvestor()

    def calculateBeforeSuitAttacks(self):
        controller = self._controller()
        if not controller:
            return
        self._refreshInvestorDamage(controller)
        if controller.plutocratPhase == 1:
            self._doHydra(controller)
            self._doKerberos(controller)
        else:
            pcrat = self._find('pcrat')
            if pcrat:
                hits = self._marketBubbleHits(pcrat)
                if hits:
                    controller.marketBubbleStacks += hits
                pcrat.setDamageMultiplier(1.0 + (controller.marketBubbleStacks * 0.03))
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
            damage = int(math.ceil(min(waiter.getMaxHP() / 3.0, waiter.getHP())))
            if damage > 0:
                waiter.b_setHP(max(0, waiter.getHP() - damage))
                styx.b_setHP(min(int(styx.getMaxHP() * 1.25), styx.getHP() + damage))
                self._visual(styx, 'PlutocratCoreUsuryWaiter_%s_%s' % (waiter.doId, damage))
            return
        if controller.investorRound % 4 != 1:
            return
        if len(self._aliveSuits()) < self.battle.maxSuits:
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

    def _removeDefeatedInvestorAttacks(self):
        kept = []
        for attack in self.battle.suitAttacks:
            attackInfo = attack[SUIT_ATK_COL]
            if not attackInfo:
                kept.append(attack)
                continue
            suitName = attackInfo.get('suitName', '')
            if suitName not in self.Investors:
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
        if controller.plutocratPhase == 1:
            self._doStyx(controller)
        else:
            pcrat = self._find('pcrat')
            if controller.snowSquallActive and pcrat:
                toonIds = []
                damages = []
                for toonId in self.battle.activeToons:
                    toon = self.battle.getToon(toonId)
                    if toon and toon.getHp() > 0:
                        toonIds.append(toonId)
                        damages.append(min(15, toon.getHp()))
                self._targeted(pcrat, 'PlutocratCoreSnowSquallDamage', toonIds, damages)
            if pcrat and controller.plutocratRound % 2 == 1:
                controller.queueNaturalReserves(2)
        self._removeDefeatedInvestorAttacks()
