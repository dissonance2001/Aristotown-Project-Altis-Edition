import math
import random

from toontown.clashbattle.battle.BattleGlobals import ToonupMissAmt, ToonupSelfHealAmt
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.toon.DistributedToonBaseAI import DistributedToonBaseAI


@AttackClassAI(attackType=AttackEnum.TOON_HEAL)
class ToonHealAttackAI(ToonAttackAI):

    def calculate(self) -> None:
        # Insert a random joke index for megaphone gags
        if self.level == 1:
            self.extraArgs.append(random.randint(0, 10000))

        attackHit = self.getLanded()
        attackDamage = self.getDamage()
        addExp = False

        # Divide the attack damage by 5 if the attack missed.
        if not attackHit:
            attackDamage *= ToonupMissAmt
            self.giveMissEffect()

        # Apply any damage modifiers here.
        finalAttackDamage = self.applyDamageModifiers(None, attackDamage, damaging=False)

        # Provide a self heal to the invoker.
        selfHealAmount = math.ceil(finalAttackDamage * ToonupSelfHealAmt[self.hasTrackBonus])

        # Get all targets besides the invoker. (if applicable)
        otherTargets = [target for target in self.targets if target is not self.invoker]

        # Divide the attack damage by the amount of targets.
        finalAttackDamage = math.ceil(finalAttackDamage / max(len(otherTargets), 1))

        for target in self.targets:
            target: DistributedToonBaseAI
            if not target.canBeAttacked():
                continue

            hpDelta = target.getMaxHp() - target.getHp()

            attackTarget = self.createAttackTarget(target.doId)
            attackTarget.landed = attackHit
            if target is self.invoker:
                attackTarget.hpAdjust = min(hpDelta, selfHealAmount)
                if attackTarget.hpAdjust:
                    addExp = True
            else:
                attackTarget.hpAdjust = min(hpDelta, finalAttackDamage)
                if attackTarget.hpAdjust:
                    addExp = True

                # Add the cheer effect to the target if the gag hit.
                if attackHit:
                    cheerEffect = SEG.createStatusEffect(target, SEE.EFFECT_CHEER)

                    # The cheer effect lasts for 2 rounds when prestiged.
                    if self.hasTrackBonus:
                        cheerEffect.setRounds(2, adjust=False)

                    target.addStatusEffect(SEE.EFFECT_CHEER, cheerEffect)

        self.sendEvent(BEG.EVENT_TOON_USED_GAG, [self])
        if addExp:
            self.addAttackExp(self.attackType, self.level, override=self.creditOverride)
    
    def setTargetList(self) -> None:
        if self.targets:
            return

        if self.isGroup:
            # Group toonups used by a toon affect all besides the attacker toon.
            self.targets = self.getToons()
        else:
            # Single toonups have a single target, as well as the self heal target.
            self.targets = self.getObjectsFromIds([self.target]) + [self.invoker]
