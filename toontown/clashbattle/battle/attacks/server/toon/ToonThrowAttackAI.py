from toontown.clashbattle.battle import BattleGlobals
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleGlobals import ThrowPresHealPercent
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.base.AttackTarget import AttackTarget
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffects, SEE
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI
import math


@AttackClassAI(attackType=AttackEnum.TOON_THROW)
class ToonThrowAttackAI(ToonAttackAI):
    WANT_HP_BONUS = True
    WANT_KB_BONUS = True
    
    def calculate(self) -> None:
        attackHit = self.getLanded()
        attackDamage = self.getDamage()
        if not attackHit:
            self.giveMissEffect()

        for target in self.targets.copy():
            target: ClashSuitBaseAI
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

            target.addAggro(self.invoker.doId, finalAttackDamage)

            attackTarget.hpAdjust = -finalAttackDamage
            attackTarget.hpBonus = .20
            
            if unlured:
                attackTarget.kbBonus = 1

            # Mark the target that the throw hit.
            self.attemptAddMarkTarget(target)

            # If the target was hit with prestige, we need to heal our thrower.
            if self.hasTrackBonus:
                healDamage = math.ceil(finalAttackDamage * ThrowPresHealPercent)
                healTarget = self.createAttackTarget(self.invoker.doId)
                healTarget.landed = attackHit
                healTarget.hpAdjust = min(self.invoker.getMaxHp() - self.invoker.getHp(), healDamage)
                self.targets.append(self.invoker)

        return super().calculate()

    def attemptAddMarkTarget(self, suit: ClashSuitBaseAI):
        """
        Attempts to mark the indicated target.
        """
        # Return if the Cog can't be attacked, or is already marked.
        if not suit.canBeAttacked() or suit.getStatusEffectOfId(SEE.EFFECT_MARKED_FOR_LAUGH):
            return

        # Mark!! Add the level extra arguments too.
        suit.addStatusEffect(SEE.EFFECT_MARKED_FOR_LAUGH, extraArgs=[BattleGlobals.ThrowMarkPercent, self.level])
