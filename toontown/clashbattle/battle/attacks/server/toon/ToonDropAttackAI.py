from toontown.clashbattle.battle.BattleGlobals import DropHpBonus, DropPrestigeAmt, DropPrestigeStartAmt, DropPrestigeBlacklist
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.statuses.StatusEffectDefinitions import DEBUFF, getEffectIdsOfQuality, StatusEffectDefinitions
from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI


@AttackClassAI(attackType=AttackEnum.TOON_DROP)
class ToonDropAttackAI(ToonAttackAI):
    WANT_HP_BONUS = True
    
    def calculate(self) -> None:
        attackHit = self.getLanded()
        attackDamage = self.getDamage()
        if not attackHit:
            self.giveMissEffect()

        for target in self.targets:
            target: ClashSuitBaseAI
            targetId = target.getDoId()

            if not target.canBeAttacked():
                continue

            # Apply any damage modifiers here.
            finalAttackDamage = self.applyDamageModifiers(target, attackDamage)
            # Also apply a damage boost if any debuffs are present on the target.
            if self.hasTrackBonus:
                effectIdSet = {effect.getEffectId()
                               for effect in target.getStatusEffects()
                               if effect.getEffectId() not in DropPrestigeBlacklist
                               and StatusEffectDefinitions.get(effect.getEffectId()).quality == DEBUFF}
                debuffCount = len(effectIdSet)
                bonus = (DropPrestigeStartAmt + (DropPrestigeAmt * debuffCount)) if debuffCount else 1.0
                finalAttackDamage = round(finalAttackDamage * bonus)

            attackTarget = self.createAttackTarget(targetId)

            # Move onto the next target if it's already lured.
            if target.getStatusEffectOfType(StatusEffects.LureStatusEffect):
                continue
            attackTarget.kbBonus = -1

            attackTarget.landed = attackHit

            if not attackHit:
                continue

            target.addAggro(self.invoker.doId, finalAttackDamage)

            attackTarget.hpAdjust = -finalAttackDamage

            # 30% combo damage for Drop.
            attackTarget.hpBonus = DropHpBonus

        return super().calculate()
