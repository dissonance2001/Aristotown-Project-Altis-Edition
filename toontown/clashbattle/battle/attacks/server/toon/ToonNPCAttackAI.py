from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.battle.statuses import SEE, StatusEffects
from toontown.battle.statuses import StatusEffectGlobals as SEG
from toontown.battle.statuses.StatusEffectEnums import StatusEffectEnum
from toontown.inventory.enums.ItemEnums import IOUItemType
from toontown.inventory.registry.IOURegistry import IOURegistry
from toontown.modifiers import ModifierEnums
from toontown.toon.ToonStatsGlobals import ToonStats


@AttackClassAI(attackType=AttackEnum.TOON_NPC)
class ToonNPCAttackAI(ToonAttackAI):

    def setTargetList(self) -> None:
        iou = IOURegistry[self.level]

        self.targets = self.getObjectsFromIds([self.target])
        # Apply the bonus to oneself as well if used on another toon, and
        # the invoker actually has the gag track.
        if self.invoker not in self.targets and (iou.getGagTrack() == -1 or self.invoker.hasTrackAccess(iou.getGagTrack())):
            self.targets.append(self.invoker)

    def calculate(self) -> None:
        # Apply any gag boosts used in this round.
        iou = IOURegistry[self.level]

        # No SOS when prevented in sync.
        for rewardModifier in self.invoker.getModifiersOfType(*ModifierEnums.REWARD_MODIFIERS):
            if not rewardModifier.canUseIOUs():
                return

        # IOUs cannot be used on reward cooldown
        if self.invoker.getStatusEffectOfType(StatusEffects.RewardCooldownStatusEffect):
            return

        # They must have the IOU.
        if sum(item.getItemSubtype() == self.level for item in self.invoker.getIOUs()) <= 0:
            return

        for target in self.targets:
            self.createAttackTarget(target.doId)
            effectId = SEE.EFFECT_TOON_DAMAGE_UP
            newStatusEffect = SEG.createStatusEffect(target, effectId)
            # Manually set the damage boost and track based on this NPCSOS.
            newStatusEffect.setGagTrack(iou.getGagTrack())
            newStatusEffect.setMultiplier(iou.getBoost())
            newStatusEffect.setUses(iou.getUses())
            target.addStatusEffect(effectId, newStatusEffect)

        effect, _ = self.invoker.addStatusEffect(StatusEffectEnum.EFFECT_REWARD_COOLDOWN)
        effect.setRounds(1)

        self.sendEvent(BEG.EVENT_TOONS_DAMAGE_UP, [self.invoker, iou.getUses()])
        self.sendEvent(BEG.EVENT_TOON_USED_GAG, [self])

    def postprocess(self) -> tuple:
        # Remove the matching item from their inventory.
        self.invoker.getHammerspace().removeItemQuantity(IOUItemType(self.level))
        self.invoker.addStat(ToonStats.IOUS)

        return [], False
