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

            targetsBoss = False
            if track in (TRAP, LURE, THROW, SQUIRT, ZAP, SOUND, DROP):
                targetsBoss = targetId == boss.doId
                try:
                    if attackAffectsGroup(track, attack[TOON_LVL_COL]):
                        targetsBoss = True
                except:
                    pass
                if targetsBoss and toonId not in bossTargetingToons:
                    bossTargetingToons.append(toonId)

            if (track not in (HEAL, PETSOS) and bossIndex >= 0 and
                    bossIndex < len(hpList)):
                damage = hpList[bossIndex]
                if damage > 0 and track != LURE:
                    hits += 1
                    if track == TRAP:
                        hits += 1
                    if toonId not in attackingToons:
                        attackingToons.append(toonId)

            if track == LURE and targetsBoss:
                try:
                    lureHit = (not attack[TOON_ACCBONUS_COL] or
                               boss.doId in self.calculator.successfulLures)
                except:
                    lureHit = True
                if lureHit:
                    hits += 1

            if track not in (HEAL, PETSOS):
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
                controller.chainsawChainLinked):
            return 0
        if controller.chainsawPhase == 3:
            amount *= 2
        old = controller.chainsawRPM
        self._setRPM(controller, old + amount)
        return controller.chainsawRPM - old

    def _projectRPMGain(self, controller, amount):
        if amount <= 0:
            return controller.chainsawRPM
        if (controller.chainsawPhase == 2 and
                controller.chainsawChainLinked):
            return controller.chainsawRPM
        if controller.chainsawPhase == 3:
            amount *= 2
        maximum = 30 if controller.chainsawPhase == 3 else 20
        return min(maximum, controller.chainsawRPM + amount)

    def _chooseHighestLevel(self, suits):
        if not suits:
            return None
        return sorted(
            suits,
            key=lambda suit: (suit.getActualLevel(),
                              self.battle.activeSuits.index(suit)),
            reverse=True)[0]

    def _isCutSlackTarget(self, suit, controller):
        if getattr(suit, 'chainsawCutSlackTarget', False):
            return True
        try:
            return suit.doId in controller.chainsawCutSlackTargets
        except:
            return False

    def _canAggrandize(self, suit, controller):
        try:
            level = suit.getActualLevel()
        except:
            level = 0
        if self._isCutSlackTarget(suit, controller):
            return level < 33
        return level < 25

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

        managerValue = 1 if cts else 0
        try:
            suit.b_setManager(managerValue)
        except:
            try:
                suit.setManager(managerValue)
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
        else:
            effects.append(StatusEffects.LureResistance(2))

        suit.chainsawManagerBeneficiary = True
        suit.chainsawPromotionLocked = True
        controller = self._getController()
        if controller:
            controller.chainsawPendingPromotedSuitId = suit.doId
        if cts:
            suit.chainsawCutSlackTarget = True
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
        if getattr(support, 'chainsawCutSlackTarget', False):
            support.chainsawCutSlackKickbackHandled = True
            support.chainsawCutSlackTarget = False
            try:
                controller.chainsawCutSlackTargets.pop(support.doId, None)
            except:
                pass
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
        existingCts = [s for s in supports
                       if self._isCutSlackTarget(s, controller)]
        if len(existingCts) >= 2:
            return self._doOffboarding(
                boss, controller, supports, [],
                targetSupport=self._chooseHighestLevel(existingCts))

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

        sacrificePool = [s for s in ordered if s is not target]
        sacrifices = sacrificePool[:3]
        sacrificeLevels = 0
        for support in sacrifices:
            try:
                sacrificeLevels += support.getActualLevel()
            except:
                pass
        try:
            newLevel = min(30, target.getActualLevel() + int(math.ceil(
                sacrificeLevels / 2.0)))
        except:
            newLevel = 30
        if newLevel <= target.getActualLevel():
            newLevel = min(30, target.getActualLevel() + 3)
        if newLevel <= target.getActualLevel():
            return False

        self._spendRPM(controller, 3)
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
            boss, 'ChainsawCoreCutTheSlack%dL%dS%s' % (targetIndex, newLevel, suffix),
            'summon-cog', 0, SuitBattleGlobals.ATK_TGT_SINGLE)
        controller.chainsawPreviousAttack = 'CutTheSlack'
        controller.chainsawPreviousLogicAttack = 'CutTheSlack'
        return True

    def _doAggrandize(self, boss, controller, supports, supportDamage,
                      suedSupports=None, preferredTarget=None):
        suedSupports = suedSupports or []
        candidates = [support for support in supports
                      if self._canAggrandize(support, controller)]
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

        cap = 33 if self._isCutSlackTarget(target, controller) else 25
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
        controller.chainsawSparkPlug[target] = 1
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
        damages = [0 for t in living]
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

    def _triggerCutSlackKickback(self, boss, controller):
        multiplier = 1.0
        for support in self.battle.activeSuits:
            if support is boss:
                continue
            try:
                if support.getHP() > 0:
                    continue
            except:
                continue
            if getattr(support, 'chainsawCutSlackKickbackHandled', False):
                continue
            if not self._isCutSlackTarget(support, controller):
                continue
            support.chainsawCutSlackKickbackHandled = True
            support.chainsawCutSlackTarget = False
            try:
                controller.chainsawCutSlackTargets.pop(support.doId, None)
            except:
                pass
            try:
                level = support.getActualLevel()
            except:
                level = 0
            if level >= 20:
                multiplier = max(
                    multiplier, 1.10 + ((level - 20) * 0.02))

        if multiplier <= 1.0:
            return False

        currentMultiplier = 1.0
        if getattr(controller, 'chainsawKickbackRounds', 0) > 0:
            currentMultiplier = getattr(
                controller, 'chainsawKickbackMultiplier', 1.0)
        controller.chainsawKickbackRounds = max(
            getattr(controller, 'chainsawKickbackRounds', 0), 3)
        controller.chainsawAbilityBanRounds = max(
            getattr(controller, 'chainsawAbilityBanRounds', 0), 3)
        controller.chainsawKickbackMultiplier = max(
            currentMultiplier, multiplier)
        controller.chainsawPendingKickback = False
        controller.chainsawPendingKickbackMultiplier = 1.0
        controller.chainsawKickbackVisualPending = True
        return True

    def _linkedSupportCandidates(self, boss, controller):
        chainIds = set(getattr(
            controller, 'chainsawChainStartSupportIds', []))
        result = []
        seen = set()
        for collection in (getattr(self.battle, 'activeSuits', ()),
                           getattr(self.battle, 'suits', ())):
            for suit in collection:
                if suit is None or suit is boss:
                    continue
                suitId = getattr(suit, 'doId', 0)
                if not suitId or suitId not in chainIds or suitId in seen:
                    continue
                seen.add(suitId)
                result.append(suit)
        return result

    def calculateAfterToonTrack(self, track):
        boss = self._findChainsaw()
        controller = self._getController()
        if not boss or not controller:
            return False

        if (controller.chainsawPhase == 1 and
                boss.getHP() <= self.PHASE_TWO_HP):
            try:
                boss.setDamageMultiplier(1.0)
            except:
                pass

        if not getattr(controller, 'chainsawChainLinked', False):
            return False

        chainIds = list(getattr(
            controller, 'chainsawChainStartSupportIds', []))
        if not chainIds:
            return False

        for suit in self._linkedSupportCandidates(boss, controller):
            try:
                if suit.getHP() > 0:
                    return False
            except:
                pass

        firedIds = []
        for toonId in self.battle.activeToons:
            attack = self.battle.toonAttacks.get(toonId)
            if not attack or attack[TOON_TRACK_COL] != FIRE:
                continue
            targetId = attack[TOON_TGT_COL]
            if targetId not in chainIds or targetId in firedIds:
                continue
            support = None
            for suit in self.battle.activeSuits:
                if suit is not boss and getattr(suit, 'doId', 0) == targetId:
                    support = suit
                    break
            if support is None:
                continue
            isManager = False
            try:
                isManager = bool(support.getManager())
            except:
                pass
            if getattr(support, 'chainsawManagerBeneficiary', False):
                isManager = True
            if not isManager:
                firedIds.append(targetId)

        firedLinks = max(0, int(getattr(
            controller, 'chainsawFiredLinks', 0))) + len(firedIds)
        controller.chainsawChainLinked = False
        controller.chainsawChainStartSupportIds = []
        controller.chainsawKickbackRounds = 3
        controller.chainsawAbilityBanRounds = 3
        controller.chainsawKickbackMultiplier = max(
            1.0, 1.30 - (0.05 * firedLinks))
        controller.chainsawPendingKickback = False
        controller.chainsawPendingKickbackMultiplier = 1.0
        controller.chainsawKickbackVisualPending = True
        controller.chainsawKickbackActivatedThisRound = True
        controller.chainsawFiredLinks = 0

        bossCondition = controller.chainsawKickbackMultiplier
        try:
            self.calculator.setSuitCondition(
                boss.doId, 'vulnerablevideographer', bossCondition,
                -1, 'setBoth')
        except:
            pass
        return True

    def _triggerProjectedChainKickback(self, boss, controller,
                                       supportDamage, firedSupports):
        if not controller.chainsawChainLinked:
            return False
        linkedSupports = self._linkedSupportCandidates(boss, controller)
        if not linkedSupports and not controller.chainsawChainStartSupportIds:
            return False
        for suit in linkedSupports:
            try:
                projectedHP = suit.getHP() - max(0, supportDamage.get(suit, 0))
                if projectedHP > 0 and suit not in firedSupports:
                    return False
            except:
                pass
        controller.chainsawChainLinked = False
        controller.chainsawChainStartSupportIds = []
        firedLinks = max(0, int(getattr(controller, 'chainsawFiredLinks', 0)))
        controller.chainsawKickbackRounds = 3
        controller.chainsawAbilityBanRounds = 3
        controller.chainsawKickbackMultiplier = max(1.0, 1.30 - (0.05 * firedLinks))
        controller.chainsawPendingKickback = False
        controller.chainsawPendingKickbackMultiplier = 1.0
        controller.chainsawKickbackVisualPending = True
        controller.chainsawKickbackActivatedThisRound = True
        controller.chainsawFiredLinks = 0
        return True

    def _chooseAbility(self, boss, controller, hits, attackingToons,
                       bossTargetingToons, supportDamage, firedSupports,
                       suedSupports, supportTracks, iouToons,
                       projectedRPM=None, preAbilityGain=0):
        phase = controller.chainsawPhase
        rpm = controller.chainsawRPM if projectedRPM is None else projectedRPM
        allSupports = []
        predictedDead = []
        supports = []
        for support in self.battle.activeSuits:
            if support is boss:
                continue
            allSupports.append(support)
            try:
                projectedHP = support.getHP() - max(0, supportDamage.get(support, 0))
                alive = projectedHP > 0
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
                                  if self._canAggrandize(s, controller)]
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
                                support.doId, -1) >= 4:
                            matureCts.append(support)

                    survivedAoe = []
                    for support in supports:
                        tracks = supportTracks.get(support, ())
                        if any([track in tracks for track in (SQUIRT, ZAP, SOUND)]):
                            survivedAoe.append(support)

                    if (matureCts or controller.chainsawHitlessRounds >= 1 or
                            firedSupports or survivedAoe):
                        targetSupport = None
                        retaliateToon = None
                        if matureCts:
                            targetSupport = self._chooseHighestLevel(matureCts)
                        elif firedSupports:
                            for toonId in self.battle.activeToons:
                                attack = self.battle.toonAttacks.get(toonId)
                                if attack and attack[TOON_TRACK_COL] == FIRE:
                                    retaliateToon = toonId
                                    break
                        elif survivedAoe:
                            targetSupport = self._chooseHighestLevel(survivedAoe)
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
                        existingCts = [s for s in supports
                                       if self._isCutSlackTarget(s, controller)]
                        if len(existingCts) >= 2:
                            chosen = ('Offboarding',
                                      (self._chooseHighestLevel(existingCts), None))
                        else:
                            preferred = random.choice(suedEligible) if suedEligible else None
                            chosen = ('CutTheSlack', preferred)

        # Extreme attacks are the fallback for phase 1/3. Marked Wood is
        # evaluated after the normal RPM-spending abilities so those abilities
        # keep their existing priority for the special Trap + Lure case.
        if phase != 2 and rpm >= 20:
            if phase == 1:
                chosen = ('Deadwood', None)
            elif supports:
                chosen = ('Layoffs', None)
        elif phase == 2 and rpm <= 10:
            chosen = ('Throttle', None)

        bossTracks = []
        for toonId in bossTargetingToons:
            attack = self.battle.toonAttacks.get(toonId)
            if attack:
                bossTracks.append(attack[TOON_TRACK_COL])
        trapAndLureOnBoss = TRAP in bossTracks and LURE in bossTracks

        if (phase != 2 and rpm >= 17 and
                controller.chainsawPreviousLogicAttack != 'MarkedWood' and
                not (trapAndLureOnBoss and chosen and chosen[0] == 'CutTheSlack')):
            markedTarget = None
            if iouToons:
                iouTargets = [toonId for toonId in iouToons if toonId in livingToons]
                if iouTargets:
                    markedTarget = sorted(
                        iouTargets, key=self._toonCurrentHP, reverse=True)[0]
            if markedTarget is None and len(attackingToons) == 1:
                markedTarget = attackingToons[0]
            if markedTarget is None and livingToons and len(attackingToons) == len(livingToons):
                markedTarget = sorted(
                    attackingToons, key=self._toonCurrentHP, reverse=True)[0]
            if markedTarget is not None:
                chosen = ('MarkedWood', markedTarget)

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
            return (False, False)

        name, data = chosen
        if name == 'Whipsaw':
            controller.chainsawPreviousLogicAttack = 'Whipsaw'
            return (False, False)

        gainApplied = False

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

        # Revving Up is an end-of-turn gain.  Cheat selection uses the RPM
        # Chainsaw had before this turn's attacks; once the cheat has spent its
        # RPM, apply the turn's gain and append the Revving Up movie afterward.
        if preAbilityGain > 0:
            gained = self._applyRPMGain(controller, preAbilityGain)
            if gained > 0:
                self._makeVisualAttack(
                    boss, 'ChainsawCoreRevvingUp%d' % gained,
                    'roll-o-dex', 0, SuitBattleGlobals.ATK_TGT_SINGLE)
            gainApplied = True
        return (result, gainApplied)

    def calculateChainsawAttacks(self):
        boss = self._findChainsaw()
        controller = self._getController()
        if not boss or not controller or boss.getHP() <= 0:
            return

        self.syncRevvingEffect(boss, controller)

        (hits, attackingToons, bossTargetingToons, supportDamage,
         firedSupports, suedSupports, supportTracks, iouToons) = self._bossHitData(boss)

        self._triggerCutSlackKickback(boss, controller)
        chainKickback = bool(getattr(
            controller, 'chainsawKickbackActivatedThisRound', False))
        if not chainKickback:
            chainKickback = self._triggerProjectedChainKickback(
                boss, controller, supportDamage, firedSupports)
        self._doKickbackVisual(boss, controller)
        controller.chainsawKickbackActivatedThisRound = False

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

        if bossTargetingToons:
            controller.chainsawHitlessRounds = -1

        usedAbility = bool(chainKickback)
        gainAppliedBeforeAbility = False
        if not phaseChanged and not chainKickback:
            projectedRPM = self._projectRPMGain(controller, hits)
            usedAbility, gainAppliedBeforeAbility = self._chooseAbility(
                boss, controller, hits, attackingToons,
                bossTargetingToons, supportDamage, firedSupports,
                suedSupports, supportTracks, iouToons,
                projectedRPM=projectedRPM, preAbilityGain=0)

        rpmGain = 0 if gainAppliedBeforeAbility else hits
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

        # Spark Plug damage is an end-of-turn effect and must play after the
        # selected cheat/Revving Up movie in Phase 2 as well.
        self._doSparkPlugDamage(boss, controller)

        if (not usedAbility and not phaseChanged and not bonus and
                controller.chainsawPreviousLogicAttack is None):
            controller.chainsawPreviousAttack = None

        if not bossTargetingToons:
            controller.chainsawHitlessRounds += 1

        controller.chainsawPreviousSupportCount = len(supports)
