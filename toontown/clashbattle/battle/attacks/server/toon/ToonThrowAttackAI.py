from toontown.battle import BattleGlobals
from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.BattleGlobals import ThrowPresHealPercent
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.base.AttackTarget import AttackTarget
from toontown.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.battle.statuses import StatusEffects, SEE
from toontown.battle.statuses import StatusEffectGlobals as SEG
from toontown.suit.DistributedSuitBaseAI import DistributedSuitBaseAI
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
            target: DistributedSuitBaseAI
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

    def attemptAddMarkTarget(self, suit: DistributedSuitBaseAI):
        """
        Attempts to mark the indicated target.
        """
        # Return if the Cog can't be attacked, or is already marked.
        if not suit.canBeAttacked() or suit.getStatusEffectOfId(SEE.EFFECT_MARKED_FOR_LAUGH):
            return

        # Mark!! Add the level extra arguments too.
        suit.addStatusEffect(SEE.EFFECT_MARKED_FOR_LAUGH, extraArgs=[BattleGlobals.ThrowMarkPercent, self.level])
