from toontown.clashbattle.battle.BattleGlobals import SoundAtkBonus
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import SEE, StatusEffects
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.clashsuit.suit.DistributedSuitBaseAI import DistributedSuitBaseAI


@AttackClassAI(attackType=AttackEnum.TOON_SOUND)
class ToonSoundAttackAI(ToonAttackAI):

    def calculate(self) -> None:
        attackHit = self.getLanded()
        attackDamage = self.getDamage()
        if not attackHit:
            self.giveMissEffect()

        attackHitSomeone = False

        for target in self.targets:
            target: DistributedSuitBaseAI
            targetId = target.getDoId()

            if not target.canBeAttacked():
                continue

            # Apply any damage modifiers here.
            finalAttackDamage = self.applyDamageModifiers(target, attackDamage)

            attackTarget = self.createAttackTarget(targetId)

            unlured = self.attemptUnlureSuit(target)

            if not attackHit:
                continue

            attackHitSomeone = True

            target.addAggro(self.invoker.doId, finalAttackDamage)

            attackTarget.landed = attackHit
            attackTarget.hpAdjust = -finalAttackDamage

            if unlured:
                attackTarget.kbBonus = 1

        if attackHitSomeone:
            windedEffect = self.invoker.getStatusEffectOfId(SEE.EFFECT_WINDED)
            encoreEffect = self.invoker.getStatusEffectOfId(SEE.EFFECT_ENCORE)

            # If they are Winded, do nothing.
            if windedEffect:
                pass
            # Give them the Encore effect if it doesn't exist.
            elif not encoreEffect:
                soundEffect = SEG.createStatusEffect(self.invoker, SEE.EFFECT_ENCORE)
                soundEffect.setRounds(1)
                soundEffect.setMultiplier(SoundAtkBonus[self.hasTrackBonus])

                self.invoker.addStatusEffect(SEE.EFFECT_ENCORE, soundEffect)
            # Otherwise, remove the Encore effect and give them the Winded effect.
            else:
                if not encoreEffect.isDisabled():
                    encoreEffect.delete()
                    self.invoker.addStatusEffect(SEE.EFFECT_WINDED)

        return super().calculate()

    def handleLureAccuracy(self, attackAcc, accBonus, randomAcc):
        # For Sound, we only want to use Lure's 100% accuracy if all of our targets are lured.
        allTargetsLured = all([bool(target.getStatusEffectOfType(StatusEffects.LureStatusEffect)) for target in self.targets])
        if allTargetsLured and len(self.targets):
            # All targets are lured, return the lure's result
            lureResult = self.targets[0].getStatusEffectOfType(StatusEffects.LureStatusEffect).handleAttackAccuracy(attackAcc, accBonus, randomAcc)
            return lureResult, True
        # Some targets unlured, we aren't using the result from lure
        return None, False
