import math

from otp.ai.AIBaseGlobal import simbase
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.BattleGlobals import ZapTargetsWanted, getZapJumpDamage
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.clashsuit.suit.DistributedSuitBaseAI import DistributedSuitBaseAI


@AttackClassAI(attackType=AttackEnum.TOON_ZAP)
class ToonZapAttackAI(ToonAttackAI):
    LEFT = 1
    RIGHT = -1

    def calculate(self) -> None:
        attackHit = self.getLanded()
        self.extraArgs.append(1)  # This'll determine whether the movie should play at all

        if not attackHit:
            self.targets = self.targets[:1]
            if self.targets:
                if self.targets[0].hasStatusEffectOfId(SEE.EFFECT_SUIT_JUST_DODGED_SOAK):
                    self.extraArgs[-1] = 0  # Turn off the movie
            self.giveMissEffect()

        attackDamage = self.getDamage()
        totalJumpDamage = getZapJumpDamage(attackDamage, self.hasTrackBonus)

        # Get the number of jump damage per cog based on # hit
        jumpDamagePerCog = 0 if len(self.targets) <= 1 else \
            int(math.ceil(totalJumpDamage / (len(self.targets) - 1)))

        zapTargetsHit = 0
        perHitAttackDamage = attackDamage

        for target in self.targets:
            target: DistributedSuitBaseAI
            targetId = target.getDoId()

            if not target.canBeAttacked():
                continue

            # Create a new AttackTarget.
            attackTarget = self.createAttackTarget(targetId)
            attackTarget.landed = attackHit

            # Unlure the suit regardless of the outcome.
            self.attemptUnlureSuit(target)

            # Zap doesn't do anything when it misses.
            if not attackHit:
                break

            soakEffect = target.getStatusEffectOfType(StatusEffects.ZapDealsBoostedDamage)
            if not soakEffect:
                continue

            if soakEffect.getRounds() > 1:
                # Decrement the drenched rounds by 1.
                if isinstance(soakEffect, StatusEffects.DrenchStatusEffect):
                    decremented = soakEffect.decrement(1, isZap=True)
                    if decremented:
                        attackTarget.extraArgs.append(0)
                # Set the rounds on the soak effect that's on this suit to 1.
                # This will make it insta-perish as soon as the round is over.
                else:
                    soakEffect.setRounds(1, adjust=False)

            if zapTargetsHit > 0:
                perHitAttackDamage = jumpDamagePerCog
            zapTargetsHit += 1

            # Apply any damage modifiers here.
            finalAttackDamage = self.applyDamageModifiers(target, perHitAttackDamage)

            attackTarget.hpAdjust = -finalAttackDamage

            # Register the amount of harm dealt to the poor suit.
            target.addAggro(self.invoker.doId, finalAttackDamage)
        
        # Call the superclass function for shared functionality.
        super().calculate()
    
    def getLanded(self) -> bool:
        suit: DistributedSuitBaseAI = simbase.air.doId2do.get(self.target)
        if suit:
            return bool(suit.getStatusEffectOfType(StatusEffects.ZapWillHit))
        return False
    
    def setTargetList(self) -> None:
        target = [suit for suit in self.suits if suit.doId == self.target]
        if not target:
            return

        target = target[0]
        # Set some standards for the loop.
        targetIndex = self.suits.index(target)
        self.targets = [target]

        # First, we need to determine the direction we need to go.
        # Firstly, assume that we're going left.
        direction = self.LEFT

        # However, if there's no suit to the left of us,
        # then obviously we'll need to go right.
        if targetIndex >= len(self.suits) - 1:
            direction = self.RIGHT

        # Suppose there is a suit to the left of us.
        # Well, what if it's not soaked? Then we'll go right.
        else:
            leftTargetIndex = targetIndex + self.LEFT
            leftTarget = self.suits[leftTargetIndex]
            soakEffect = leftTarget.getStatusEffectOfType(StatusEffects.ZapCanJump)
            untouchableEffect = leftTarget.getStatusEffectOfType(StatusEffects.UntouchableStatusEffect)
            if not soakEffect or untouchableEffect:
                direction = self.RIGHT

        # Now, we're going to go over a set amount of suits.
        for _ in range(ZapTargetsWanted):

            # Get information about the cog we're on.
            target = self.suits[targetIndex]

            # If this cog is not soaked, then there's no more suits to check.
            soakEffect = target.getStatusEffectOfType(StatusEffects.ZapCanJump)
            untouchableEffect = target.getStatusEffectOfType(StatusEffects.UntouchableStatusEffect)
            if not soakEffect or untouchableEffect:
                break

            # Now that we know that the cog is soaked,
            # we're safe to apply the damage to it.
            if target not in self.targets:
                self.targets.append(target)

            # Now, we'll go ahead and move our targetIndex
            # by the expected direction. And if it's OOB,
            # then we're safe to break from the loop.
            targetIndex += direction
            if not (0 <= targetIndex < len(self.suits)):
                break
