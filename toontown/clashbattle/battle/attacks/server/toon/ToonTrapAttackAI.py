import math

from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import SEE, StatusEffects
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.toon.gui.ToonTipGlobals import TTE
from toontown.clashbattle.battle import BattleGlobals
from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI


@AttackClassAI(attackType=AttackEnum.TOON_TRAP)
class ToonTrapAttackAI(ToonAttackAI):

    def calculate(self) -> None:
        # Trap Tip
        self.showToonTipAll(TTE.TIP_TRAP)

        for target in self.targets:
            target: ClashSuitBaseAI

            if target.getHp() <= 0:
                continue

            # Check for if this suit could be lured.
            lureEffect = target.getStatusEffectOfType(StatusEffects.LureStatusEffect)

            if lureEffect:
                # We need to. Not use this trap.
                self.attackIndex = -1
                continue

            attackTarget = self.createAttackTarget(target.getDoId())
            attackTarget.landed = True

            # Keep track of our own version of the damage per suit in cases of possible group traps
            finalAttackDamage = self.getFinalDamage(target)
            trapEffect = target.getStatusEffectOfType(StatusEffects.TrappedStatusEffect)

            # If there is no trap in front of the suit, it's fine to add the trap.
            if not trapEffect:
                self.sendEvent(BEG.EVENT_PLACED_TRAP, [target, self.invoker, finalAttackDamage, self.level, self.attackIndex])
                # Store the entire attack so that we can reference it when doing target damage modifiers later.
                newTrapEffect = SEG.createStatusEffect(target, SEE.EFFECT_SUIT_TRAPPED)
                newTrapEffect.setTrapLevel(self.level)
                newTrapEffect.setTrapDamage(finalAttackDamage)
                newTrapEffect.setInvoker(self.invoker)
                target.addStatusEffect(SEE.EFFECT_SUIT_TRAPPED, newTrapEffect)

        return super().calculate()

    def getFinalDamage(self, target: ClashSuitBaseAI) -> int:
        """
        Apply any damage modifiers to this Trap and return the final damage to deal to <target>
        """
        finalAttackDamage = self.getDamage()

        # Trap gags deal 30% more damage to executive Cogs. (NOT managers)
        if target.isElite and not target.isMiniboss():
            finalAttackDamage *= BattleGlobals.TrapEliteBonus

        finalAttackDamage = math.ceil(finalAttackDamage)

        # Apply any damage modifiers here.
        finalAttackDamage = self.applyDamageModifiers(target, finalAttackDamage, targetMods=False)

        return finalAttackDamage
