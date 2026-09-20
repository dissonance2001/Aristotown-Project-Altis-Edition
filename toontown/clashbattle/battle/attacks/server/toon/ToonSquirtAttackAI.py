from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleGlobals import NumRoundsSoaked, SplashDamageAmt
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.base.AttackTarget import AttackTarget
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffects, SEE
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.toon.gui.ToonTipGlobals import TTE
from toontown.clashsuit.suit.DistributedSuitBaseAI import DistributedSuitBaseAI


@AttackClassAI(attackType=AttackEnum.TOON_SQUIRT)
class ToonSquirtAttackAI(ToonAttackAI):
    WANT_HP_BONUS = True
    WANT_KB_BONUS = True

    def calculate(self) -> None:
        attackHit = self.getLanded()
        attackDamage = self.getDamage()
        if not attackHit:
            self.giveMissEffect()

        for target in self.targets.copy():
            target: DistributedSuitBaseAI
            targetIndex = self.suits.index(target)
            targetId = target.getDoId()

            if not target.canBeAttacked():
                continue

            # Apply any damage modifiers here.
            finalAttackDamage = self.applyDamageModifiers(target, attackDamage)

            attackTarget = self.createAttackTarget(targetId)
            attackTarget.landed = attackHit

            unlured = self.attemptUnlureSuit(target)

            if not attackHit:
                continue

            # Soaked Cog Tip
            self.showToonTipAll(TTE.TIP_ZAP_NEEDS_SOAKED)

            # Soak the target that the squirt hit.
            self.attemptAddSoakTarget(target, attackTarget)

            # Soak the nearby suits.
            # First, attempt to soak the target to the right.
            if targetIndex > 0:
                rightSuit = self.suits[targetIndex - 1]
                self.attemptAddSoakTarget(rightSuit, self.attemptSplashTarget(rightSuit, finalAttackDamage))

            # Then attempt to soak the target to the left.
            if targetIndex < len(self.suits) - 1:
                leftSuit = self.suits[targetIndex + 1]
                self.attemptAddSoakTarget(leftSuit, self.attemptSplashTarget(leftSuit, finalAttackDamage))
            
            target.addAggro(self.invoker.doId, finalAttackDamage)
            
            attackTarget.hpAdjust = -finalAttackDamage
            attackTarget.hpBonus = .20

            if unlured:
                attackTarget.kbBonus = 1

        return super().calculate()
    
    def attemptSplashTarget(self, suit: DistributedSuitBaseAI, totalDamage: int) -> None:
        if not suit.canBeAttacked():
            return

        splashTarget = self.createAttackTarget(suit.doId)
        self.targets.append(suit)
        splashDamage = self.applyDamageModifiers(
            suit, totalDamage * SplashDamageAmt[self.hasTrackBonus], invokerMods=False)
        splashTarget.hpAdjust = -splashDamage
        splashTarget.landed = True

        suit.addAggro(self.invoker.doId, splashDamage)

        return splashTarget
    
    def attemptAddSoakTarget(self, suit: DistributedSuitBaseAI, attackTarget: AttackTarget=None):
        """
        Attempts to soak the indicated target.
        If it is already soaked, the soak rounds will be refreshed.
        """
        # Return if the Cog can't be attacked, or is already drenched.
        if not suit.canBeAttacked() or suit.getStatusEffectOfId(SEE.EFFECT_SUIT_DRENCHED) or attackTarget is None:
            return

        roundsSoaked = NumRoundsSoaked[self.level]

        # Soak the suit if it isn't already.
        # Apply any effects that modify the soak rounds here.
        roundModifierEffects = self.invoker.getStatusEffectsOfType(StatusEffects.SoakRoundsModifierStatusEffect)
        for effect in roundModifierEffects:
            roundsSoaked = effect.handleSoakRounds(roundsSoaked)

        effect = SEE.EFFECT_SUIT_SOAKED

        # Create a new soak status effect
        newSoakEffect = SEG.createStatusEffect(suit, effect)

        # Set our rounds
        newSoakEffect.setRounds(roundsSoaked, adjust=False)

        # Update attack target's extra args to show the client how long they were soaked
        attackTarget.extraArgs.append(roundsSoaked)

        # Removed the "just dodged soak" effect if they got hit by another soak
        suit.removeStatusEffectOfId(SEE.EFFECT_SUIT_JUST_DODGED_SOAK)

        # Insert them into the battle avatar, let it handle the combine logic.
        soakEffect, combined = suit.addStatusEffect(effect, newSoakEffect)

        # Send events that the suit got soaked
        eventToSend = BEG.EVENT_RESOAKED_SUIT if combined else BEG.EVENT_SOAKED_SUIT
        self.sendEvent(eventToSend, [suit, self.invoker, roundsSoaked, soakEffect, self])

    def giveMissEffect(self):
        # In addition to the usual miss effect, we'll want to add a hidden
        # "just dodged soak" effect to any suits that would've gotten soaked.

        def addJustDodgedSoak(suit):  # This is just here so we're not adding the effect to cogs that are already soaked.
            if not suit.getStatusEffectOfId(SEE.EFFECT_SUIT_SOAKED):
                suit.addStatusEffect(effectId=SEE.EFFECT_SUIT_JUST_DODGED_SOAK)

        for target in self.targets.copy():
            # Add it to our target first
            targetIndex = self.suits.index(target)
            addJustDodgedSoak(target)

            # Then the two adjacent suits
            if targetIndex > 0:
                addJustDodgedSoak(self.suits[targetIndex - 1])
            if targetIndex < len(self.suits) - 1:
                addJustDodgedSoak(self.suits[targetIndex + 1])

        # Then we can do the normal miss effect
        super().giveMissEffect()
