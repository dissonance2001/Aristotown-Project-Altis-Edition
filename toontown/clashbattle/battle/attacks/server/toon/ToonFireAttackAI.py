import math

from otp.ai.AIBaseGlobal import simbase
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleGlobals import FireCostPercent
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.statuses.StatusEffectEnums import StatusEffectEnum
from toontown.inventory.enums.ItemEnums import MaterialItemType
from toontown.modifiers import ModifierEnums
from toontown.clashsuit.suit.DistributedSuitBaseAI import DistributedSuitBaseAI
from toontown.toon.ToonStatsGlobals import ToonStats


@AttackClassAI(attackType=AttackEnum.TOON_FIRE)
class ToonFireAttackAI(ToonAttackAI):

    def calculate(self) -> None:
        for suit in self.targets:
            suit: DistributedSuitBaseAI
            suitId = suit.getDoId()

            if suit.getHp() <= 0:
                continue

            attackTarget = self.createAttackTarget(suitId)

            # Fail to fire the Suit if it doesn't exist
            # or if the Suit is a miniboss (.mgr)
            # or if they have been given the same resistances as a miniboss
            if suit.isMiniboss():
                continue

            # Do they have immunity?
            immunityEffects = suit.getStatusEffectsOfType(StatusEffects.MinibossResistancesStatusEffect)
            if any([immunityEffect.minibossImmunitiesActive for immunityEffect in immunityEffects]):
                continue
            if suit.getStatusEffectOfType(StatusEffects.PinkSlipImmunity):
                continue

            result = self.useToonFires(suit)
            if not result:
                return

            suit.b_setSkeleRevives(0)

            attackTarget.landed = True
            attackTarget.hpAdjust = -suit.getHp()

            self.sendEvent(BEG.EVENT_FIRED_SUIT, [suit, self.invoker])

    def useToonFires(self, suit: DistributedSuitBaseAI) -> bool:
        """
        This module handles subtracting the correct amount of fires from a toon after usage.
        """

        # It costs 1/2 of the Suit's level (rounded up) to fire said suit.
        costToFire = math.ceil(suit.getActualLevel() * FireCostPercent)
        toonFires = self.invoker.getPinkSlips()

        if toonFires < 0:
            return False

        # Fires cannot be used on reward cooldown
        if self.invoker.getStatusEffectOfType(StatusEffects.RewardCooldownStatusEffect):
            return False

        # No fires when prevented in sync.
        for rewardModifier in self.invoker.getModifiersOfType(*ModifierEnums.REWARD_MODIFIERS):
            if not rewardModifier.canUseSlips():
                return False

        # It's pretty sus when a Toon tries to fire
        # with more fires than they actually have...
        if costToFire > toonFires:
            simbase.air.writeServerEvent('suspicious', avId=self.invoker.doId,
                                         issue=f'Toon attempting to fire a {costToFire} cost cog with {toonFires} fires')
            self.notify.warning(
                f'Toon {self.invoker.doId} attempting to fire a {costToFire} cost cog with {toonFires} pink slips')
            return False

        self.invoker.getHammerspace().removeItemQuantity(MaterialItemType.PinkSlips, costToFire)
        self.invoker.addStat(ToonStats.FIRES, amount=costToFire)
        effect, _ = self.invoker.addStatusEffect(StatusEffectEnum.EFFECT_REWARD_COOLDOWN)
        effect.setRounds(1)
        return True
