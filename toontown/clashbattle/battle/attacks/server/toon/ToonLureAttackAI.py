import math

from otp.ai.AIBaseGlobal import simbase
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.BattleGlobals import NumRoundsLured, getAvPropDamage, LureTrappedSuitBonus
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.base.AttackTarget import AttackTarget
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffects, SEE
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.toon.gui.ToonTipGlobals import TTE
from toontown.clashsuit.suit.DistributedSuitBaseAI import DistributedSuitBaseAI


@AttackClassAI(attackType=AttackEnum.TOON_LURE)
class ToonLureAttackAI(ToonAttackAI):

    def __init__(self, attackType: AttackEnum, rounds: int = 0,
                 invoker: BattleAvatar = None, targets: list = None,
                 extraArgs: list = None, level: int = -1, target: int = -1,
                 propBonus: int = -1, expGained: dict = None, creditMult: int = 1,
                 creditLevel: int = 0, levelBonus: int = 0,
                 targetHitsTrack: dict = None, targetAttacks: dict = None):
        super().__init__(attackType, rounds, invoker, targets, extraArgs, level, target, propBonus, expGained,
                         creditMult, creditLevel, levelBonus, targetHitsTrack, targetAttacks)
        self.trappedTarget = False

    def calculate(self) -> None:
        attackHit = self.getLanded()
        baseRoundsLured = self.getDamage()
        if not attackHit:
            for target in self.targets:
                if not target.getStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE) and not target.getStatusEffectOfId(SEE.EFFECT_SUIT_LURED):
                    # If the suit dodges lure, isn't lured, and doesn't have lure resistance,
                    # give them a -25% damage debuff for the turn
                    target.addStatusEffect(SEE.EFFECT_SUIT_JUST_DODGED_LURE)
            self.giveMissEffect()
        else:
            # Lure hit, remove "just dodged" effect from all targets
            for target in self.targets:
                if target.getStatusEffectOfId(SEE.EFFECT_SUIT_JUST_DODGED_LURE):
                    target.removeStatusEffectOfId(SEE.EFFECT_SUIT_JUST_DODGED_LURE)

        for target in self.targets:
            target: DistributedSuitBaseAI
            targetId = target.getDoId()

            if not target.canBeAttacked():
                continue

            # If the suit was just lured, or if the effect is set to expire after
            # the lures are finished, ignore this target.
            oldLureEffect = target.getStatusEffectOfType(StatusEffects.LureStatusEffect)
            if oldLureEffect and (not oldLureEffect.getFresh() or oldLureEffect.getUsed()):
                continue

            # See if the suit has a trap on it.
            # If a previous lure from this chain has already triggered the trap, ignore this target.
            trapEffect = target.getStatusEffectOfType(StatusEffects.TrappedStatusEffect)
            if trapEffect:
                if trapEffect.getUsed():
                    continue
                self.trappedTarget = True

            # Set our knockback modifier
            knockback = getAvPropDamage(
                self.attackType, self.level,
                self.invoker.getExperience()[AttackEnum.TOON_LURE], self.hasTrackBonus,
            )

            attackTarget = self.createAttackTarget(targetId)
            attackTarget.landed = attackHit

            if not attackHit:
                continue

            roundsLured = self.getSuitLureResistance(target, baseRoundsLured)
            # This cog has lure immunity, don't lure them at all.
            if roundsLured == -1:
                attackTarget.kbBonus = -1
                continue

            if trapEffect:
                trapId = trapEffect.getInvokerId()
                trapDmg = trapEffect.getTrapDamage()
                trapLvl = trapEffect.getTrapLevel()
                # Apply any damage modifiers here.
                trapDmg = self.applyDamageModifiers(target, trapDmg, invokerMods=False, overrideAttackType=AttackEnum.TOON_TRAP)
                self.addAttackExp(AttackEnum.TOON_TRAP, trapLvl, toonId=trapId)
                attackTarget.hpAdjust -= trapDmg
                # We do this so that we are either sending the toon object.
                toon = simbase.air.doId2do.get(trapId)
                self.sendEvent(BEG.EVENT_TRIGGERED_TRAP, [target, toon, trapDmg, trapLvl])
                # Queue the trap effect to be cleared at the end of the chain.
                trapEffect.setUsed(1)

                target.addAggro(trapId, trapDmg)

                attackTarget.kbBonus = -3

                # Since the cog has been trapped, we don't want them to be lured again.
                if oldLureEffect:
                    oldLureEffect.setUsed(1)

                # Inflict the dazed debuff on the cog.
                target.addStatusEffect(SEE.EFFECT_SUIT_DAZED)
            else:
                # Lured Cog Tip
                self.showToonTipAll(TTE.TIP_LURE_COG_STUN)

                self.creditOverride = True

                # Tell the battle that we've successfully lured this Suit.

                newLureEffect = SEG.createStatusEffect(target, SEE.EFFECT_SUIT_LURED)
                newLureEffect.setRounds(roundsLured, adjust=False)
                newLureEffect.setUniqueId(self.rounds)
                newLureEffect.addInvoker(self.invoker, self)
                newLureEffect.setPrestige(self.hasTrackBonus)
                
                # Adjust the knockback for any status effects if they exist.
                kbEffects = self.invoker.getStatusEffectsOfType(StatusEffects.LureKnockbackModifierStatusEffect)
                for kbEffect in kbEffects:
                    knockback = kbEffect.handleLureKb(knockback)

                # Lure KB is affected by various effects.
                # This method will also do the rounding for us.
                knockback = self.applyDamageModifiers(target, knockback)

                newLureEffect.setKnockback(knockback)

                lureEffect, combined = target.addStatusEffect(SEE.EFFECT_SUIT_LURED, newLureEffect)

                if not oldLureEffect:
                    attackTarget.kbBonus = roundsLured
                    self.sendEvent(BEG.EVENT_LURED_SUIT, [target, self.invoker, roundsLured, lureEffect, self.attackIndex, self.level])
                else:
                    # Clear out kbbonus for all old lures on this suit.
                    for lureAttack in list(lureEffect.invokers.values()):
                        for result in lureAttack.results:
                            result: AttackTarget
                            if result.avId == targetId:
                                result.kbBonus = -1

                    # Set the new attack with the knockback bonus
                    attackTarget.kbBonus = roundsLured
                    self.sendEvent(BEG.EVENT_RELURED_SUIT, [target, self.invoker, roundsLured, lureEffect, self.attackIndex, self.level])

                    lureEffect.addInvoker(self.invoker, self)

        # Don't send to the client if none of our targets were processed.
        if not self.results:
            self.attackIndex = -1

        return super().calculate()

    def getRawAccuracyOrOverride(self):
        rawAcc, override = super().getRawAccuracyOrOverride()
        # If no accuracy override, trap existing is added as a +20% accuracy bonus
        if override == -1 and any([target.hasStatusEffectOfId(SEE.EFFECT_SUIT_TRAPPED) for target in self.targets]):
            rawAcc += LureTrappedSuitBonus
        return rawAcc, override

    def getDamage(self, target: BattleAvatar = None) -> int:
        return NumRoundsLured[self.level]
