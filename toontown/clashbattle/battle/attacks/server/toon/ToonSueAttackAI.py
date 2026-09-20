import math

from otp.ai.AIBaseGlobal import simbase
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleGlobals import SueCostPercent
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffects, SEE
from toontown.clashbattle.battle.statuses.StatusEffectEnums import StatusEffectEnum
from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.modifiers import ModifierEnums
from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI
from toontown.toon.ToonStatsGlobals import ToonStats


@AttackClassAI(attackType=AttackEnum.TOON_SUE)
class ToonSueAttackAI(ToonAttackAI):

    def calculate(self) -> None:
        for suit in self.targets:
            suit: ClashSuitBaseAI
            suitId = suit.getDoId()

            if suit.getHp() <= 0:
                continue

            attackTarget = self.createAttackTarget(suitId)

            # Fail to sue the Suit if it doesn't exist
            # or if the Suit is a miniboss (.mgr)
            # or if they have been given the same resistances as a miniboss
            if suit.isMiniboss():
                continue

            # Do they have immunity?
            immunityEffects = suit.getStatusEffectsOfType(StatusEffects.MinibossResistancesStatusEffect)
            if any([immunityEffect.minibossImmunitiesActive for immunityEffect in immunityEffects]):
                continue
            if suit.getStatusEffectOfType(StatusEffects.CeaseDesistImmunity):
                continue

            result = self.useToonSues(suit)
            if not result:
                return

            attackTarget.landed = True

            suit.addStatusEffect(SEE.EFFECT_SUIT_SUED)
            self.sendEvent(BEG.EVENT_SUED_SUIT, [suit, self.invoker])

    def useToonSues(self, suit: ClashSuitBaseAI) -> bool:
        """
        This module handles subtracting the correct amount of sues from a toon after usage.
        """

        # It costs 1/4 of the Suit's level (rounded up) to sue said suit.
        costToSue = math.ceil(suit.getActualLevel() * SueCostPercent)
        toonSues = self.invoker.getCeaseDesists()

        if toonSues < 0:
            return False

        # Fires cannot be used on reward cooldown
        if self.invoker.getStatusEffectOfType(StatusEffects.RewardCooldownStatusEffect):
            return False

        # No sues when prevented in sync.
        for rewardModifier in self.invoker.getModifiersOfType(*ModifierEnums.REWARD_MODIFIERS):
            if not rewardModifier.canUseCNDs():
                return False

        # It's pretty sus when a Toon tries to sue
        # with more C&Ds than they actually have...
        if costToSue > toonSues:
            simbase.air.writeServerEvent('suspicious', avId=self.invoker.doId,
                                         issue=f'Toon attempting to sue a {costToSue} cost cog with {toonSues} cease desists')
            self.notify.warning(f'Toon attempting to sue a {costToSue} cost cog with {toonSues} cease desists')
            return False

        # Decrement the Toon's sues with the amount required.
        self.invoker.getHammerspace().removeItemQuantity(MaterialItemType.CeaseAndDesists, costToSue)
        self.invoker.addStat(ToonStats.SUES, amount=costToSue)
        effect, _ = self.invoker.addStatusEffect(StatusEffectEnum.EFFECT_REWARD_COOLDOWN)
        effect.setRounds(1)
        return True
