from toontown.battle.BattleBase import *
from toontown.battle.BattleGlobals import *
from toontown.battle import SuitBattleGlobals
from toontown.battle import StatusEffects
from toontown.toonbase import ToontownBattleGlobals

import math
import random


class ChainsawCalculatorAI:
    """Project Altis adapter for the modern three-phase Chainsaw fight.

    The source of truth for the ordering/thresholds is Corporate Clash's
    ChainsawConsultantStatusEffectBase.  This adapter keeps that logic local to
    Chainsaw instead of importing Clash's whole modern status/event framework.
    """

    PHASE_TWO_HP = 8500
    PHASE_THREE_HP = 4750

    def __init__(self, calculator):
        self.calculator = calculator
        self.battle = calculator.battle

    def __getattr__(self, name):
        return getattr(self.calculator, name)

    def _getController(self):
        controller = getattr(self.battle, 'bossCog', None)
        if controller is None:
            return None
        if not hasattr(controller, 'chainsawRPM'):
            return None
        return controller

    def _findChainsaw(self):
        for suit in self.battle.activeSuits:
            try:
                if suit.dna.name == 'chainsaw':
                    return suit
            except:
                pass
        return None

    def syncRevvingEffect(self, boss=None, controller=None):
        if boss is None:
            boss = self._findChainsaw()
        if controller is None:
            controller = self._getController()
        if not boss or not controller:
            return None

        effects = self.calculator.suitStatusConditionsNew.setdefault(
            boss.doId, [])
        effect = None
        for candidate in effects:
            if isinstance(candidate, StatusEffects.RevvingUp):
                effect = candidate
                break

        if effect is None:
            effect = StatusEffects.RevvingUp()
            effects.append(effect)

        effect.rpm = int(controller.chainsawRPM)
        effect.reforesting = int(controller.chainsawPhase) == 2
        effect.updateEffect()
        return effect

    def _aliveSupports(self, boss):
        result = []
        for suit in self.battle.activeSuits:
            if suit is boss:
                continue
            try:
                if suit.getHP() > 0:
                    result.append(suit)
            except:
                pass
        return result

    def _toonCurrentHP(self, toonId):
        toon = self.battle.getToon(toonId)
        if not toon:
            return 0
        hp = toon.getHp()
        try:
            hp += self.calculator.toonHPAdjusts.get(toonId, 0)
        except:
            pass
        return max(0, hp)

    def _makeVisualAttack(self, boss, name, animName='nothing', hp=0,
                          group=SuitBattleGlobals.ATK_TGT_SINGLE):
        attack = self.calculator.getCheatAttack(
            boss.doId,
            {
                'suitName': 'chainsaw',
                'name': name,
                'animName': animName,
                'hp': hp,
                'acc': 100,
                'freq': 0,
                'group': group,
            })
        if attack[SUIT_ATK_COL]:
            self.battle.suitAttacks.append(attack)
            return attack
        return None

    def _makeTargetedAttack(self, boss, name, toonIds, damages,
                            animName='nothing'):
        if not toonIds:
            return None

        attack = getDefaultSuitAttack()
        attack[SUIT_ID_COL] = boss.doId
        attack[SUIT_ATK_COL] = {
            'suitName': 'chainsaw',
            'name': name,
            'animName': animName,
            'hp': 0,
            'acc': 100,
            'freq': 0,
            'group': (SuitBattleGlobals.ATK_TGT_GROUP
                      if len(toonIds) > 1 else SuitBattleGlobals.ATK_TGT_SINGLE),
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

        try:
            self.calculator._BattleCalculatorAI__applySuitAttackDamages(
                attack, boss)
        except:
            # Keep the movie intact if an older BattleCalculator layout is in
            # use; ordinary getCheatAttack attacks remain the fallback path.
            return None

        self.battle.suitAttacks.append(attack)
        return attack

    def _bossHitData(self, boss):
        bossIndex = -1
        try:
            bossIndex = self.battle.activeSuits.index(boss)
        except:
            pass

        hits = 0
        attackingToons = []
        bossTargetingToons = []
        supportDamage = {}
        firedSupports = []
        suedSupports = []
        supportTracks = {}
        iouToons = []

        for toonId in self.battle.activeToons:
            attack = self.battle.toonAttacks.get(toonId)
            if not attack:
                continue
            track = attack[TOON_TRACK_COL]
            hpList = attack[TOON_HP_COL]
            targetId = attack[TOON_TGT_COL]

            # Clash tracks IOU usage separately for Marked Wood.  Altis uses
            # NPCSOS for these battle rewards, so preserve the Toon as an IOU
            # aggressor even when the reward does not have a normal damage row.
            if track == NPCSOS:
                iouToons.append(toonId)

            if track in (FIRE, SUE):
                for suit in self.battle.activeSuits:
                    if suit is boss or suit.doId != targetId:
                        continue
                    # Promoted Chainsaw beneficiaries have standard Manager
                    # protections.  Failed Fire/Sue attempts must not count as
                    # Offboarding triggers.
                    isManager = False
                    try:
                        isManager = bool(suit.getManager())
                    except:
                        pass
                    if getattr(suit, 'chainsawManagerBeneficiary', False):
                        isManager = True
                    if not isManager:
                        if track == FIRE:
                            firedSupports.append(suit)
                            controller = self._getController()
                            if (controller and controller.chainsawChainLinked and
                                    suit.doId in controller.chainsawChainStartSupportIds):
                                controller.chainsawFiredLinks += 1
                        else:
                            suedSupports.append(suit)
                    break

            if bossIndex >= 0 and bossIndex < len(hpList):
                damage = hpList[bossIndex]
                if damage > 0 and track != LURE:
                    hits += 1
                    if track == TRAP:
                        hits += 1
                    if toonId not in attackingToons:
                        attackingToons.append(toonId)
                    if toonId not in bossTargetingToons:
                        bossTargetingToons.append(toonId)

            # Chain Link counts Lure as targeting Chainsaw. Marked Wood does
            # not, so track targeting independently from actual damage hits.
            if track == LURE:
                targetsBoss = targetId == boss.doId
                try:
                    if attackAffectsGroup(LURE, attack[TOON_LVL_COL]):
                        targetsBoss = True
                except:
                    pass
                if targetsBoss and toonId not in bossTargetingToons:
                    bossTargetingToons.append(toonId)

            for index in xrange(min(len(hpList), len(self.battle.activeSuits))):
                suit = self.battle.activeSuits[index]
                if suit is boss:
                    continue
                damage = hpList[index]
                if damage > 0:
                    supportDamage[suit] = supportDamage.get(suit, 0) + damage
                    supportTracks.setdefault(suit, []).append(track)

        return (hits, attackingToons, bossTargetingToons, supportDamage,
                firedSupports, suedSupports, supportTracks, iouToons)

    def _setRPM(self, controller, value):
        controller.b_setChainsawRPM(value)
        self.syncRevvingEffect(controller=controller)

    def _spendRPM(self, controller, stacks):
        self._setRPM(controller, controller.chainsawRPM - stacks)

    def _applyRPMGain(self, controller, amount):
        if amount <= 0:
            return 0
        if (controller.chainsawPhase == 2 and
                (controller.chainsawChainLinked or
                 controller.chainsawPreviousAttack == 'ChainLinked')):
            return 0
        if controller.chainsawPhase == 3:
            amount *= 2
        old = controller.chainsawRPM
        self._setRPM(controller, old + amount)
        return controller.chainsawRPM - old

    def _chooseHighestLevel(self, suits):
        if not suits:
            return None
        return sorted(
            suits,
            key=lambda suit: (suit.getActualLevel(),
                              self.battle.activeSuits.index(suit)),
            reverse=True)[0]

    def _promoteSuit(self, suit, newLevel, cts=False, distribute=True):
        if not suit:
            return
        newLevel = max(1, int(newLevel))
        wasOvercharged = bool(getattr(suit, 'chainsawOvercharged', False))

        if distribute:
            suit.setLevel(newLevel, forceLevel=True)
            try:
                suit.b_setExecutive(1)
            except:
                suit.setExecutive(1)
            if wasOvercharged:
                newMax = int(math.ceil(suit.getMaxHP() * 1.5))
                try:
                    suit.b_setMaxHP(newMax)
                except:
                    suit.setMaxHP(newMax)
            try:
                suit.b_setHP(suit.getMaxHP())
            except:
                pass
        else:
            try:
                relativeLevel = SuitBattleGlobals.getRelativeFromActualLevel(
                    suit.dna.name, newLevel)
                suit.level = relativeLevel
                vitals = SuitBattleGlobals.getSuitVitals(
                    suit.dna.name, relativeLevel)
                maxHp = int(math.ceil(
                    vitals['hp'] * ToontownBattleGlobals.EXECUTIVE_HP_MULT))
                if wasOvercharged:
                    maxHp = int(math.ceil(maxHp * 1.5))
                suit.maxHP = maxHp
                suit.currHP = maxHp
            except:
                suit.setLevel(newLevel, forceLevel=True)
            try:
                suit.executive = 1
            except:
                suit.setExecutive(1)

        try:
            suit.b_setManager(1)
        except:
            try:
                suit.setManager(1)
            except:
                pass

        try:
            self.calculator.removeLured(suit.doId)
        except:
            pass
        self.calculator.suitStatusConditions[suit.doId] = {}
        effects = self.calculator.suitStatusConditionsNew.setdefault(suit.doId, [])
        effects[:] = [effect for effect in effects
                      if isinstance(effect, StatusEffects.Overcharged)]
        effects.append(StatusEffects.ManagerBeneficiary(-1))
        if cts:
            effects.append(StatusEffects.LureResistance(1))

        suit.chainsawManagerBeneficiary = True
        suit.chainsawPromotionLocked = True
        controller = self._getController()
        if controller:
            controller.chainsawPendingPromotedSuitId = suit.doId
        if cts:
            if controller:
                controller.chainsawCutSlackTargets[suit.doId] = 0
        else:
            suit.chainsawAggrandized = True

    def _fireSupport(self, support):
        if not support:
            return
        try:
            support.b_setHP(0)
        except:
            support.setHP(0)

    def _doOffboarding(self, boss, controller, supports, firedSupports,
                       targetSupport=None, retaliationToon=None):
        support = targetSupport if targetSupport in supports else self._chooseHighestLevel(supports)
        if not support:
            return False
        self._spendRPM(controller, 2)
        hpRatio = float(max(0, support.getHP())) / max(1.0, float(support.getMaxHP()))
        hpRatio = min(max(hpRatio, 0.1), 1.2)
        damage = math.ceil(support.getActualLevel() * 3 * hpRatio)
        damage = max(1, int(damage))
        supportIndex = self.battle.activeSuits.index(support)
        name = 'ChainsawCoreOffboarding%d' % max(1, supportIndex)
        self._fireSupport(support)
        if retaliationToon in self.battle.activeToons:
            self._makeTargetedAttack(
                boss, name, [retaliationToon], [damage], 'throw-paper')
        else:
            self._makeVisualAttack(
                boss, name, 'throw-paper', damage,
                SuitBattleGlobals.ATK_TGT_SINGLE)
        controller.chainsawPreviousAttack = 'Offboarding'
        controller.chainsawPreviousLogicAttack = 'Offboarding'
        return True

    def _doMarkedWood(self, boss, controller, targetToonId=None):
        living = [toonId for toonId in self.battle.activeToons
                  if self._toonCurrentHP(toonId) > 0]
        if not living:
            return False
        if targetToonId not in living:
            targetToonId = sorted(
                living, key=self._toonCurrentHP, reverse=True)[0]
        target = targetToonId
        toon = self.battle.getToon(target)
        maxHp = toon.getMaxHp() if toon else self._toonCurrentHP(target)
        damage = max(
            40,
            int(math.ceil(self._toonCurrentHP(target) - (maxHp * 0.33))))
        self._spendRPM(controller, 7)
        self._makeTargetedAttack(
            boss, 'ChainsawCoreMarkedWood', [target], [damage], 'throw-paper')
        try:
            self.setToonCondition(target, 'markedwood', 1.75, 2, 'setBoth')
        except:
            pass
        controller.chainsawPreviousAttack = 'MarkedWood'
        controller.chainsawPreviousLogicAttack = 'MarkedWood'
        return True

    def _doCutTheSlack(self, boss, controller, supports, preferredTarget=None):
        if not supports:
            return False

        # A Cog that has already received a Chainsaw promotion is a Manager
        # Beneficiary and can never be promoted by Cut the Slack a second time.
        eligible = []
        for support in supports:
            if getattr(support, 'chainsawPromotionLocked', False):
                continue
            if support.doId in controller.chainsawCutSlackTargets:
                continue
            try:
                if support.getActualLevel() >= 30:
                    continue
            except:
                pass
            eligible.append(support)
        if not eligible:
            return False

        ordered = sorted(
            eligible,
            key=lambda suit: (suit.getActualLevel(),
                              self.battle.activeSuits.index(suit)))
        if preferredTarget in eligible:
            target = preferredTarget
        else:
            target = ordered[-1]

        # Current Clash balance only sacrifices up to two lower-level Cogs.
        sacrificePool = [s for s in ordered if s is not target]
        sacrifices = sacrificePool[:2]
        newLevel = 30

        # Current wiki/update behavior uses a 4,000 RPM cost.
        self._spendRPM(controller, 4)
        for support in sacrifices:
            self._fireSupport(support)
        self._promoteSuit(target, newLevel, cts=True, distribute=False)
        targetIndex = self.battle.activeSuits.index(target)
        sacrificeIndices = []
        for support in sacrifices:
            try:
                sacrificeIndices.append(self.battle.activeSuits.index(support))
            except:
                pass
        suffix = ''.join([str(index) for index in sacrificeIndices])
        self._makeVisualAttack(
            boss, 'ChainsawCoreCutTheSlack%dS%s' % (targetIndex, suffix),
            'summon-cog', 0, SuitBattleGlobals.ATK_TGT_SINGLE)
        controller.chainsawPreviousAttack = 'CutTheSlack'
        controller.chainsawPreviousLogicAttack = 'CutTheSlack'
        return True

    def _doAggrandize(self, boss, controller, supports, supportDamage,
                      suedSupports=None, preferredTarget=None):
        suedSupports = suedSupports or []
        candidates = []
        for support in supports:
            # User-facing Manager rule: once a Cog has been promoted into a
            # beneficiary, no Chainsaw promotion may select it again.
            if getattr(support, 'chainsawPromotionLocked', False):
                continue
            try:
                if (not support.getExecutive()) or support.getActualLevel() < 25:
                    candidates.append(support)
            except:
                candidates.append(support)
        if not candidates:
            return False

        damaged = [s for s in candidates if supportDamage.get(s, 0) > 0]
        sued = [s for s in candidates if s in suedSupports]
        if preferredTarget in candidates:
            target = preferredTarget
        elif damaged:
            target = sorted(damaged, key=lambda s: s.getHP())[-1]
        elif sued:
            target = sorted(sued, key=lambda s: s.getHP())[-1]
        else:
            # Match Clash's preference for a non-Executive employee before an
            # already-Executive but still promotable employee.
            nonExe = []
            for suit in candidates:
                try:
                    if not suit.getExecutive():
                        nonExe.append(suit)
                except:
                    pass
            target = nonExe[0] if nonExe else candidates[0]

        cap = 25
        try:
            add = 4 if target.getExecutive() else 2
        except:
            add = 2
        self._spendRPM(controller, 3)
        newLevel = min(cap, target.getActualLevel() + add)
        self._promoteSuit(target, newLevel, distribute=False)
        targetIndex = self.battle.activeSuits.index(target)
        self._makeVisualAttack(
            boss, 'ChainsawCoreAggrandize%dL%d' % (targetIndex, newLevel),
            'summon-cog', 0, SuitBattleGlobals.ATK_TGT_SINGLE)
        controller.chainsawPreviousAttack = 'Aggrandize'
        controller.chainsawPreviousLogicAttack = 'Aggrandize'
        return True

    def _doChainLinked(self, boss, controller):
        self._spendRPM(controller, 2)
        controller.chainsawChainLinked = True
        controller.chainsawChainStartSupportIds = [
            s.doId for s in self._aliveSupports(boss)]
        controller.chainsawFiredLinks = 0
        self._makeVisualAttack(
            boss, 'ChainsawCoreChainLinked', 'sticker', 0,
            SuitBattleGlobals.ATK_TGT_GROUP)
        controller.chainsawPreviousAttack = 'ChainLinked'
        return True

    def _doScabbard(self, boss, controller, supports):
        self._spendRPM(controller, 7)
        states = []
        for support in supports:
            current = support.getHP()
            maximum = support.getMaxHP()
            overcharged = bool(getattr(support, 'chainsawOvercharged', False))
            if current >= maximum and not overcharged:
                newMax = int(math.ceil(maximum * 1.5))
                support.setMaxHP(newMax)
                support.setHP(newMax)
                support.chainsawOvercharged = True
                effects = self.calculator.suitStatusConditionsNew.setdefault(
                    support.doId, [])
                if not any([isinstance(effect, StatusEffects.Overcharged)
                            for effect in effects]):
                    effects.append(StatusEffects.Overcharged())
                try:
                    support.setDamageMultiplier(
                        support.getDamageMultiplier() * 1.5)
                except:
                    pass
                finalHP = newMax
                finalMax = newMax
                overcharged = True
            else:
                finalMax = maximum
                finalHP = min(
                    finalMax, current + int(math.ceil(finalMax * 0.5)))
                support.setHP(finalHP)
            try:
                index = self.battle.activeSuits.index(support)
                states.extend((index, int(finalHP), int(finalMax),
                               1 if overcharged else 0))
            except:
                pass
        name = 'ChainsawCoreScabbard'
        if states:
            name += '_' + '_'.join([str(value) for value in states])
        self._makeVisualAttack(
            boss, name, 'sticker', 0, SuitBattleGlobals.ATK_TGT_GROUP)
        controller.chainsawPreviousAttack = 'Scabbard'
        return True

    def _doSparkPlug(self, boss, controller):
        living = [toonId for toonId in self.battle.activeToons
                  if self._toonCurrentHP(toonId) > 0]
        if not living:
            return False
        target = sorted(living, key=self._toonCurrentHP, reverse=True)[0]
        self._spendRPM(controller, 2)
        controller.chainsawSparkPlug[target] = 2
        self._makeTargetedAttack(
            boss, 'ChainsawCoreSparkPlug', [target], [0], 'finger-wag')
        controller.chainsawPreviousAttack = 'SparkPlug'
        return True

    def _doSparkPlugDamage(self, boss, controller):
        targets = []
        damage = []
        for toonId in controller.chainsawSparkPlug.keys():
            if controller.chainsawSparkPlug[toonId] > 0 and self._toonCurrentHP(toonId) > 0:
                targets.append(toonId)
                damage.append(20)
                controller.chainsawSparkPlug[toonId] -= 1
        for toonId in controller.chainsawSparkPlug.keys():
            if controller.chainsawSparkPlug[toonId] <= 0:
                del controller.chainsawSparkPlug[toonId]
        if targets:
            self._makeTargetedAttack(
                boss, 'ChainsawCoreSparkPlugDamage', targets, damage, 'effort')

    def _doThrottle(self, boss, controller):
        living = [toonId for toonId in self.battle.activeToons
                  if self._toonCurrentHP(toonId) > 0]
        if not living:
            return False
        damages = []
        for toonId in living:
            toon = self.battle.getToon(toonId)
            if controller.chainsawUsedThrottle:
                damage = int(math.ceil(toon.getMaxHp() * 0.5))
            else:
                damage = int(math.ceil(self._toonCurrentHP(toonId) * 0.5))
            damages.append(max(1, damage))
        throttleName = ('ChainsawCoreThrottleTwo'
                        if controller.chainsawUsedThrottle
                        else 'ChainsawCoreThrottle')
        controller.chainsawUsedThrottle = True
        self._makeTargetedAttack(
            boss, throttleName, living, damages, 'glower')
        for toonId in living:
            try:
                self.setToonCondition(toonId, 'vulnerable', 1.25, 2, 'setBoth')
            except:
                pass
        controller.chainsawPreviousAttack = 'Throttle'
        return True

    def _doLayoffs(self, boss, controller, supports):
        if not supports:
            return False
        toons = [toonId for toonId in self.battle.activeToons
                 if self._toonCurrentHP(toonId) > 0]
        if not toons:
            return False

        orderedSupports = sorted(
            list(supports), key=lambda s: self.battle.activeSuits.index(s))
        targetCount = min(len(orderedSupports), len(toons))
        targetToons = list(toons[:targetCount])
        damages = []
        for index in xrange(targetCount):
            support = orderedSupports[index]
            hpRatio = float(max(0, support.getHP())) / max(1.0, float(support.getMaxHP()))
            hpRatio = min(max(hpRatio, 0.1), 1.2)
            damage = math.ceil(support.getActualLevel() * 4 * hpRatio)
            damages.append(max(1, damage))

        cost = min(10, 6 + len(orderedSupports))
        self._spendRPM(controller, cost)
        for support in orderedSupports:
            self._fireSupport(support)
        firedIndices = ''.join([
            str(self.battle.activeSuits.index(support))
            for support in orderedSupports])
        self._makeTargetedAttack(
            boss, 'ChainsawCoreLayoffs%s' % firedIndices,
            targetToons, damages, 'glower')
        controller.chainsawPreviousAttack = 'Layoffs'
        return True

    def _doDeadwood(self, boss, controller):
        living = [toonId for toonId in self.battle.activeToons
                  if self._toonCurrentHP(toonId) > 0]
        if not living:
            return False
        damages = [max(0, self._toonCurrentHP(t) - 1) for t in living]
        self._makeTargetedAttack(
            boss, 'ChainsawCoreDeadwood', living, damages, 'glower')
        controller.chainsawDeadwoodTriggered = True
        controller.chainsawPreviousAttack = 'Deadwood'
        return True

    def _doKickbackVisual(self, boss, controller):
        if not getattr(controller, 'chainsawKickbackVisualPending', False):
            return False
        multiplier = controller.chainsawKickbackMultiplier
        if getattr(controller, 'chainsawPendingKickback', False):
            multiplier = controller.chainsawPendingKickbackMultiplier
        percent = int(round(max(0.0, (float(multiplier) - 1.0) * 100.0)))
        self._makeVisualAttack(
            boss, 'ChainsawCoreKickback%d' % percent,
            'pie-small-react', 0, SuitBattleGlobals.ATK_TGT_SINGLE)
        controller.chainsawKickbackVisualPending = False
        return True

    def _triggerProjectedChainKickback(self, boss, controller,
                                       supportDamage, firedSupports):
        if not controller.chainsawChainLinked:
            return False
        foundLinked = False
        for suit in self.battle.activeSuits:
            try:
                if (suit is boss or
                        suit.doId not in controller.chainsawChainStartSupportIds):
                    continue
                foundLinked = True
                if suit.getHP() > 0 and suit not in firedSupports:
                    return False
            except:
                pass
        if not foundLinked and not controller.chainsawChainStartSupportIds:
            return False
        controller.chainsawChainLinked = False
        controller.chainsawChainStartSupportIds = []
        controller.chainsawKickbackRounds = 3
        controller.chainsawAbilityBanRounds = 3
        controller.chainsawKickbackMultiplier = 1.30
        controller.chainsawPendingKickback = False
        controller.chainsawPendingKickbackMultiplier = 1.0
        controller.chainsawKickbackVisualPending = True
        controller.chainsawFiredLinks = 0
        return True

    def _chooseAbility(self, boss, controller, hits, attackingToons,
                       bossTargetingToons, supportDamage, firedSupports,
                       suedSupports, supportTracks, iouToons):
        phase = controller.chainsawPhase
        rpm = controller.chainsawRPM
        allSupports = []
        predictedDead = []
        supports = []
        for support in self.battle.activeSuits:
            if support is boss:
                continue
            allSupports.append(support)
            try:
                alive = support.getHP() > 0
            except:
                alive = True
            if support in firedSupports or not alive:
                predictedDead.append(support)
            else:
                supports.append(support)
        livingToons = [toonId for toonId in self.battle.activeToons
                       if self._toonCurrentHP(toonId) > 0]

        fullBattle = len(supports) == 4
        allToonsHitBoss = (len(livingToons) > 0 and
                           len(attackingToons) == len(livingToons))
        allToonsTargetedBoss = (len(livingToons) > 0 and
                                len(bossTargetingToons) == len(livingToons))
        exactlyOneHitBoss = len(attackingToons) == 1
        totalLevel = 0
        for suit in supports:
            try:
                totalLevel += suit.getActualLevel()
            except:
                pass

        # Kick Back temporarily bans RPM-spending abilities.  Clash permits
        # them again at 17,000+ RPM even while the ban is active.
        abilityBan = int(getattr(controller, 'chainsawAbilityBanRounds', 0))
        canSpend = abilityBan <= 0 or rpm >= 17
        chosen = None

        if canSpend:
            if phase == 2:
                # Build the Phase 2 pool in ascending threshold order.  A later
                # qualifying ability replaces an earlier one, matching Clash's
                # "highest RPM requirement wins" rule.
                if rpm >= 13:
                    candidates = [s for s in supports
                                  if not getattr(s, 'chainsawPromotionLocked', False)]
                    damaged = [s for s in candidates if supportDamage.get(s, 0) > 0]
                    sued = [s for s in candidates if s in suedSupports]
                    if len(candidates) == 1 or damaged or sued:
                        target = None
                        if damaged:
                            target = sorted(damaged, key=lambda x: x.getHP())[-1]
                        elif sued:
                            target = sorted(sued, key=lambda x: x.getHP())[-1]
                        chosen = ('Aggrandize', target)

                if (rpm >= 15 and
                        not controller.chainsawChainLinked and
                        (not supports or allToonsTargetedBoss)):
                    chosen = ('ChainLinked', None)

                if rpm >= 17:
                    if fullBattle or len([s for s in suedSupports if s in supports]) >= 2:
                        chosen = ('Scabbard', None)

            else:
                wantCts = True

                if rpm >= 12 and supports:
                    matureCts = []
                    for support in supports:
                        if controller.chainsawCutSlackTargets.get(
                                support.doId, -1) >= 3:
                            matureCts.append(support)

                    survivedAoe = False
                    for support in supports:
                        tracks = supportTracks.get(support, ())
                        if any([track in tracks for track in (SQUIRT, ZAP, SOUND)]):
                            survivedAoe = True
                            break

                    if (matureCts or controller.chainsawHitlessRounds >= 2 or
                            firedSupports or survivedAoe):
                        targetSupport = None
                        retaliateToon = None
                        if matureCts:
                            targetSupport = random.choice(matureCts)
                        elif firedSupports:
                            # Altis records the Toon who selected Fire in the
                            # raw attack list.  Retaliate against the first one
                            # that actually fired a support Cog.
                            for toonId in self.battle.activeToons:
                                attack = self.battle.toonAttacks.get(toonId)
                                if attack and attack[TOON_TRACK_COL] == FIRE:
                                    retaliateToon = toonId
                                    break
                        chosen = ('Offboarding', (targetSupport, retaliateToon))

                if wantCts and rpm >= 14 and supports:
                    ctsCandidates = []
                    for support in supports:
                        if getattr(support, 'chainsawPromotionLocked', False):
                            continue
                        if support.doId in controller.chainsawCutSlackTargets:
                            continue
                        try:
                            if support.getActualLevel() >= 30:
                                continue
                        except:
                            pass
                        ctsCandidates.append(support)

                    suedEligible = [s for s in suedSupports if s in ctsCandidates]
                    if ctsCandidates and (fullBattle or len(predictedDead) >= 2 or suedEligible):
                        preferred = random.choice(suedEligible) if suedEligible else None
                        chosen = ('CutTheSlack', preferred)

                if (rpm >= 17 and
                        controller.chainsawPreviousLogicAttack != 'MarkedWood'):
                    if exactlyOneHitBoss or allToonsHitBoss or iouToons:
                        targetToon = None
                        if iouToons:
                            livingIous = [toonId for toonId in iouToons
                                         if toonId in livingToons]
                            if livingIous:
                                targetToon = sorted(
                                    livingIous,
                                    key=self._toonCurrentHP)[-1]
                        elif exactlyOneHitBoss:
                            targetToon = attackingToons[0]
                        elif livingToons:
                            targetToon = sorted(
                                livingToons,
                                key=self._toonCurrentHP)[-1]
                        chosen = ('MarkedWood', targetToon)

        # Extreme attacks override the normal pool exactly like Clash.
        if phase != 2 and rpm >= 20:
            if phase == 1:
                chosen = ('Deadwood', None)
            elif supports:
                chosen = ('Layoffs', None)
        elif phase == 2 and rpm <= 10:
            chosen = ('Throttle', None)

        # Fallback attacks.  Spark Plug cannot repeat; when it would repeat,
        # Clash forces Scabbard or Aggrandize if the RPM/field permits it.
        if chosen is None and canSpend:
            if phase != 2:
                if controller.chainsawPreviousAttack != 'Whipsaw':
                    chosen = ('Whipsaw', None)
            elif rpm >= 11:
                if controller.chainsawPreviousAttack != 'SparkPlug':
                    chosen = ('SparkPlug', None)
                elif supports:
                    if rpm >= 17:
                        chosen = ('Scabbard', None)
                    elif rpm >= 13:
                        chosen = ('Aggrandize', None)

        if chosen is None:
            controller.chainsawPreviousLogicAttack = None
            return False

        name, data = chosen
        if name == 'Whipsaw':
            controller.chainsawPreviousLogicAttack = 'Whipsaw'
            return False
        if name == 'Deadwood':
            result = self._doDeadwood(boss, controller)
        elif name == 'Layoffs':
            result = self._doLayoffs(boss, controller, supports)
        elif name == 'Throttle':
            result = self._doThrottle(boss, controller)
        elif name == 'SparkPlug':
            result = self._doSparkPlug(boss, controller)
        elif name == 'Scabbard':
            result = self._doScabbard(boss, controller, supports)
        elif name == 'ChainLinked':
            result = self._doChainLinked(boss, controller)
        elif name == 'Aggrandize':
            result = self._doAggrandize(
                boss, controller, supports, supportDamage,
                suedSupports=suedSupports, preferredTarget=data)
        elif name == 'Offboarding':
            targetSupport, retaliateToon = data
            result = self._doOffboarding(
                boss, controller, supports, firedSupports,
                targetSupport=targetSupport, retaliationToon=retaliateToon)
        elif name == 'CutTheSlack':
            result = self._doCutTheSlack(
                boss, controller, supports, preferredTarget=data)
        elif name == 'MarkedWood':
            result = self._doMarkedWood(
                boss, controller, targetToonId=data)
        else:
            result = False

        if result:
            controller.chainsawPreviousLogicAttack = name
        return result

    def calculateChainsawAttacks(self):
        boss = self._findChainsaw()
        controller = self._getController()
        if not boss or not controller or boss.getHP() <= 0:
            return

        self.syncRevvingEffect(boss, controller)

        (hits, attackingToons, bossTargetingToons, supportDamage,
         firedSupports, suedSupports, supportTracks, iouToons) = self._bossHitData(boss)

        self._doSparkPlugDamage(boss, controller)
        chainKickback = self._triggerProjectedChainKickback(
            boss, controller, supportDamage, firedSupports)
        self._doKickbackVisual(boss, controller)

        phaseChanged = False
        if controller.chainsawPhase == 1 and boss.getHP() <= self.PHASE_TWO_HP:
            controller.b_setChainsawPhase(2)
            self._setRPM(controller, 10)
            controller.chainsawChainLinked = False
            controller.chainsawPreviousAttack = 'PhaseTwo'
            controller.chainsawUsedThrottle = False
            controller.chainsawPhaseTwoFirstTurn = True
            self._makeVisualAttack(
                boss, 'ChainsawCorePhaseTwo', 'rake-react', 0,
                SuitBattleGlobals.ATK_TGT_GROUP)
            self._doThrottle(boss, controller)
            controller.chainsawPreviousAttack = 'PhaseTwo'
            phaseChanged = True
        elif controller.chainsawPhase == 2 and boss.getHP() <= self.PHASE_THREE_HP:
            controller.b_setChainsawPhase(3)
            self.syncRevvingEffect(boss, controller)
            controller.chainsawChainLinked = False
            controller.chainsawPreviousAttack = 'PhaseThree'
            self._makeVisualAttack(
                boss, 'ChainsawCorePhaseThree', 'rake-react', 0,
                SuitBattleGlobals.ATK_TGT_GROUP)
            phaseChanged = True

        if hits:
            controller.chainsawHitlessRounds = -1

        usedAbility = bool(chainKickback)
        if not phaseChanged and not chainKickback:
            usedAbility = self._chooseAbility(
                boss, controller, hits, attackingToons,
                bossTargetingToons, supportDamage, firedSupports,
                suedSupports, supportTracks, iouToons)

        # Current Clash revving rules: every damaging non-Lure gag that lands
        # on Chainsaw is +1 stack; wiping every support after turn one is +1.
        rpmGain = 0 if chainKickback else hits
        supports = self._aliveSupports(boss)
        if (not chainKickback and controller.chainsawRound > 0 and
                not supports and controller.chainsawPreviousSupportCount > 0):
            rpmGain += 1

        # Whipsaw is the phase 1/3 fallback and grants +2 stacks.  It may not
        # happen two rounds in a row.  Phase 3 doubles this gain as well.
        bonus = 0
        if (not usedAbility and not phaseChanged and
                controller.chainsawPhase in (1, 3) and
                controller.chainsawPreviousLogicAttack == 'Whipsaw' and
                controller.chainsawPreviousAttack != 'Whipsaw'):
            bonus = 2
            controller.chainsawPreviousAttack = 'Whipsaw'

        gained = self._applyRPMGain(controller, rpmGain + bonus)
        if gained > 0:
            if bonus:
                multiplier = 2 if controller.chainsawPhase == 3 else 1
                normalRequested = rpmGain * multiplier
                normalGained = min(gained, normalRequested)
                bonusGained = max(0, gained - normalGained)
                name = 'ChainsawCoreWhipsaw%d_%d' % (gained, bonusGained)
            else:
                name = 'ChainsawCoreRevvingUp%d' % gained
            # RPM is synchronized through the controller/meter; this movie is
            # visual-only and must never deal the stack count as Toon damage.
            self._makeVisualAttack(
                boss, name, 'roll-o-dex', 0,
                SuitBattleGlobals.ATK_TGT_SINGLE)

        if (not usedAbility and not phaseChanged and not bonus and
                controller.chainsawPreviousLogicAttack is None):
            controller.chainsawPreviousAttack = None

        if not hits:
            controller.chainsawHitlessRounds += 1

        controller.chainsawPreviousSupportCount = len(supports)
