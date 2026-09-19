import math
from operator import attrgetter
import random
from typing import List

from direct.showbase import PythonUtil
from toontown.battle import SuitBattleGlobals, BattleGlobals

from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.BattleAvatar import BattleAvatar
from toontown.battle.BattleGlobals import ATTACK_TRACKS
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.server.AttackAI import AttackAI
from toontown.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.battle.attacks.server.suit.BasicAttacksAI import (
    ApplyStatusEffectAttackAI,
    ApplyStatusEffectToSelfAttackAI,
    ApplyVisualEffectToSelfAttackAI,
    CreateAttackAttackAI,
    DamageAttackAI,
    DamageInflictStatusAttackAI,
    DoNothingAI,
    EndBattleAttackAI,
    GenericDamageAttackAI,
    HitAllParticipantsAttackAI,
    RemoveStatusEffectAttackAI,
    RemoveStatusEffectFromSelfAttackAI,
    RemoveVisualEffectFromSelfAttackAI,
    SuitHealAttackAI, InstakillAttackAI,
    SuitUnlureAttackAI, DamageRemoveStatusAttackAI, SuitUnlureCreateAttackAttackAI,
)
from toontown.battle.attacks.server.suit.SuitGroupAttackAI import SuitGroupAttackAI
from toontown.battle.attacks.server.suit.SuitSingleAttackAI import SuitSingleAttackAI
from toontown.battle.environmental.base.EnvironmentalEnum import PlutocratWeather, EnvironmentalEnum
from toontown.battle.statuses import StatusEffects
from toontown.battle.statuses.StatusEffectDefinitions import DEBUFF
from toontown.battle.statuses.StatusEffectEnums import SEE, SUIT_STATUS_EFFECTS_TO_REMOVE
from toontown.battle.statuses import StatusEffectGlobals as SEG
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.suit.DistributedSuitBaseAI import DistributedSuitBaseAI
from toontown.suit.SuitDNA import SuitDNA
from toontown.toon import ToonDNA
from toontown.toon.DistributedToonBaseAI import DistributedToonBaseAI
from toontown.toonbase import TTLocalizer


@AttackClassAI(attackType=AttackEnum.BACKBURNER)
class BackburnerAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_BACKBURNER

    healthMultiplier = 3.0

    def calculate(self) -> None:
        # Check to see if our targets don't have the Barnburner effect.
        noEffectTargets = [target for target in self.targets if not target.getStatusEffectOfId(SEE.EFFECT_BACKBURNER)]

        # Apply the status effect to all targets.
        super().calculate()

        # Raise the max hp + hp of targets newly getting the status effect + adjust their status effect rounds..
        # Also, send info to the client so they can update the HP during the movie.
        for result in self.results:
            if result.landed:
                target = self.findTarget(result.avId)
                if target in noEffectTargets:
                    # Adjust their health.
                    newMaxHp = int(target.getMaxHp() * self.healthMultiplier)
                    newHp = int(target.getHp() * self.healthMultiplier)
                    target.setMaxHp(newMaxHp)
                    target.setHp(newHp)
                    result.extraArgs = [newMaxHp, newHp]

                    # Adjust the rounds of their negative effects.
                    effect = target.getStatusEffectOfId(SEE.EFFECT_BACKBURNER)
                    if effect:
                        effect.incrementStacks(1)
                        effect.reduceEffects()

    def setTargetList(self) -> None:
        self.targets = self.getOtherSuits()

        # Ensure that the condition is fulfilled before calculating the attack.
        if not self.targets:
            self.REQUIRED_TARGETS = 1


@AttackClassAI(attackType=AttackEnum.BARNBURNER)
class BarnBurnerAI(HitAllParticipantsAttackAI, RemoveStatusEffectAttackAI):
    STATUS_EFFECT = SUIT_STATUS_EFFECTS_TO_REMOVE

    def calculate(self, ignoreModifiers: bool = False) -> None:
        HitAllParticipantsAttackAI.calculate(self, ignoreModifiers)

        for result in self.results:
            if result.landed:
                target = self.findTarget(result.avId)
                self.handleStatusEffect(target)

    def getDamage(self, target: BattleAvatar=None) -> int:
        # The attack does 5% more damage for each target.
        return self.extraArgs[0] * (1.0 + (0.05 * len(self.targets)))


@AttackClassAI(attackType=AttackEnum.TRIAL_BY_FIRE)
class TrialByFireAI(DamageInflictStatusAttackAI):
    STATUS_EFFECT = SEE.EFFECT_TRIAL_BY_FIRE
    REQUIRED_TARGETS = 1

    @property
    def damagePercent(self):
        return self.extraArgs[0]

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        target.addStatusEffect(self.STATUS_EFFECT, extraArgs=self.extraArgs.copy())

    def setTargetList(self) -> None:
        aliveToons = self.getAliveToons()
        random.shuffle(aliveToons)
        self.targets = aliveToons[:min(self.extraArgs[1], len(aliveToons))]

    def getDamage(self, target: BattleAvatar = None) -> int:
        hp = target.getHp()
        # Floor the damage to be consistent with all other suit damage calcs, but also
        # don't do absolutely zero damage either. (this can happen with 1 laff ubers)
        return max(min(math.floor(hp * self.damagePercent), hp), 1)


@AttackClassAI(attackType=AttackEnum.BOILERPLATE)
class BoilerplateAI(TrialByFireAI):
    """Effectively the same as Trial by Fire except it hits all
    toons and has a chance to miss.
    """
    REQUIRED_TARGETS = 1

    def setTargetList(self) -> None:
        self.targets = self.getToons()

    def getLanded(self) -> bool:
        return random.random() <= self.invoker.getAttackAccuracy(self.attackType)


@AttackClassAI(attackType=AttackEnum.DEEP_FREEZE)
class DeepFreezeAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_DEEP_FREEZE

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        deepFreezeRounds = self.extraArgs[0]
        status = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        status.setRounds(deepFreezeRounds)
        target.addStatusEffect(self.STATUS_EFFECT, status)

    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=AttackEnum.DIVE)
class DiveAI(ApplyStatusEffectToSelfAttackAI):
    STATUS_EFFECT = SEE.EFFECT_DIVING

    @property
    def hasSavior(self):
        return self.extraArgs[0]

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        status = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        status.setHasSavior(self.hasSavior)
        target.addStatusEffect(self.STATUS_EFFECT, status)
        # Also clear out debuff effects
        target.clearStatusEffectsOfQuality(quality=DEBUFF, exceptions=SEE.EFFECT_SUIT_TRAPPED)


@AttackClassAI(attackType=AttackEnum.SINK_OR_SWIM)
class SinkOrSwimAI(GenericDamageAttackAI):
    STATUS_EFFECT = SEE.EFFECT_DIVING

    def calculate(self) -> None:
        super().calculate()

        # Remove the diving effect from the deep diver.
        self.invoker.removeStatusEffectOfId(self.STATUS_EFFECT)
        self.invoker.noRegularAttackRounds = 0

    def setTargetList(self) -> None:
        self.targets = self.getToons()
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return self.invoker.getAttackDamage(self.attackType)


@AttackClassAI(attackType=AttackEnum.DEEP_DIVER_PROMOTE_FODDER)
class DeepDiverPromoteFodderAI(AttackAI):
    REQUIRED_TARGETS = 1

    @property
    def specialBoyId(self):
        return self.extraArgs[0]

    def calculate(self) -> None:
        coolSpecialBoy = self.battle.findSuit(self.specialBoyId)
        # Special boy's new level
        newLevel = 7

        # Set their new level without distributing it.
        attributes = SuitBattleGlobals.SuitAttributes[coolSpecialBoy.dna.name]
        coolSpecialBoy.level = newLevel - attributes['level'] - 1

        # Also make them an executive.
        coolSpecialBoy.isElite = True

        # And recalculate their HP.
        hp = coolSpecialBoy.calculateHp()
        coolSpecialBoy.maxHp = hp
        coolSpecialBoy.hp = hp

        # Send their doId as an extra argument.
        self.extraArgs = [coolSpecialBoy.doId, coolSpecialBoy.level]


@AttackClassAI(attackType=AttackEnum.HEALING_BELL)
class HealingBellAI(RemoveStatusEffectAttackAI):
    """
    Used for Bellringer's Healing Bell attack.
    3 different conditions:

    - If there are any Suits in battle with negative status conditions, 
    those status conditions are healed
    - If there are other Suits in battle but they don't have negative status effects, 
    they're healed by 33% of their max HP instead (up to 33% overheal)
    - If the user is alone, the user will heal themselves by 20% of their max HP and 
    remove their negative status effects.
    """
    REQUIRED_TARGETS = 1

    STATUS_EFFECT = SUIT_STATUS_EFFECTS_TO_REMOVE

    healMultipliers = (1.0, 1.25, 1.5, 2.0)

    def calculate(self) -> None:
        # Track the suits that we have helped to track conditions.
        helpedSuits = []
        # Track the suits we have unlured to give them extra attacks.
        luredSuits = []

        # Health Cap is 2x
        self.HEAL_CAP = 2.0

        # The more toons in the fight, the more we heal.
        healMultiplierIndex = max(0, min(len(self.getAliveToons()) - 1, 3))
        healMultiplier = self.healMultipliers[healMultiplierIndex]

        # If the manager effect says we have weakened healing (from an explosion),
        # Healing is half as effective this time around
        managerEffect = self.invoker.getStatusEffectOfId(SEE.EFFECT_MANAGER_BELLRINGER)
        if managerEffect and managerEffect.isHealingWeakened:
            healMultiplier *= 0.5

        # We delete all negative status effects from each suit except for the user
        for suit in self.targets:
            suit: DistributedSuitBaseAI
            if suit == self.invoker:
                continue
            for effectType in self.STATUS_EFFECT:
                effectsOfType = suit.getStatusEffectsOfId(effectType)
                for effect in effectsOfType:
                    if effectType == SEE.EFFECT_SUIT_LURED and suit not in luredSuits:
                        luredSuits.append(suit)
                    if suit not in helpedSuits:
                        helpedSuits.append(suit)
                    # Remove the status effect
                    effect.delete()
            if suit in helpedSuits:
                # Heal them a small amount if an effect was removed
                healAmount = -self.applyDamageModifiers(suit, (-0.5) * healMultiplier)
                result = self.createAttackTarget(suit.doId)
                result.hpAdjust = healAmount
            else:
                # Heal them a larger amount if an effect was not removed
                healAmount = -self.applyDamageModifiers(suit, (-0.75) * healMultiplier)
                if healAmount == 0:
                    continue
                helpedSuits.append(suit)
                result = self.createAttackTarget(suit.doId)
                result.hpAdjust = healAmount

        # And just like our dear cousin Bayou Bellow, a new suit attack for every suit that was lured before.
        for suit in luredSuits:
            self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                suit.getRandomAttack(), {"invoker": suit, "unlure": True},
                {"respectPreviousAdditions": True}
            ])

        # If we helped other suits, give ourselves a small heal.
        # If we didn't, clear our debuffs and give ourselves a larger heal.
        if helpedSuits:
            # Heal the user
            result = self.createAttackTarget(self.invoker.doId)
            result.hpAdjust = -self.applyDamageModifiers(self.invoker, (-1 / 20) * healMultiplier)
        else:
            # We delete all the user's negative status effects
            self.handleStatusEffect(self.invoker)

            # Heal the user
            result = self.createAttackTarget(self.invoker.doId)
            result.hpAdjust = -self.applyDamageModifiers(self.invoker, (-1 / 8) * healMultiplier)

    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()


@AttackClassAI(attackType=AttackEnum.MS_POWER_TIE)
class MultislackerPowerTieAI(SuitSingleAttackAI):
    DAMAGE_MULTS = [1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1]
    
    def setTargetList(self) -> None:
        self.targets = self.extraArgs[0]
        self.extraArgs = []

    def getDamage(self, target: BattleAvatar = None) -> int:
        return int(self.damage * self.invoker.getDamageMultiplier() * self.DAMAGE_MULTS[self.targets.index(target)])


@AttackClassAI(attackType=AttackEnum.MANDATORY_LUNCH)
class MandatoryLunchAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_LUNCH_BREAK_MSLACKER

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list=None) -> None:
        target.addStatusEffect(self.STATUS_EFFECT)
    
    def setTargetList(self) -> None:
        self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.UNION_BUST)
class UnionBustAI(GenericDamageAttackAI):
    BannedSuits = ['mslacker', 'msfore']

    def calculate(self, ignoreModifiers: bool = True):
        super().calculate(ignoreModifiers=True)
        # Manually insert another workers comp for union bust
        self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
            AttackEnum.WORKERS_COMP, {"invoker": self.invoker, "extraArgs": [len(self.targets), 10], "unlure": True},
            {"mode": "end"},
        ])

    def setTargetList(self) -> None:
        self.targets = [suit for suit in self.invoker.battle.activeSuits if suit.getHp() > 0 and suit.dna.name not in self.BannedSuits]

    def getDamage(self, target: BattleAvatar = None) -> int:
        return target.getHp()


@AttackClassAI(attackType=AttackEnum.MOB_MENTALITY)
class MobMentalityAI(CreateAttackAttackAI):
    INSERTION_ARGS = {"respectPreviousAdditions": True}
    # Mult Value will scale the damage multiplier down based on number of Cogs that get extra attacks.
    # 1 Cog: 90% damage  (total damage: 90%)
    # 2 Cogs: 75% damage (total damage: 150%)
    # 3 Cogs: 60% damage (total damage: 180%)
    # 4 Cogs: 50% damage (total damage: 200%)
    MULT_VALUES = {
        1: 0.9,
        2: 0.75,
        3: 0.6,
        4: 0.5
    }

    def calculate(self) -> None:
        super().calculate()

        instance = getattr(self.invoker.battle, "instance", None)
        if not instance:
            return

        # Increase the strength of the user's Will of the People effect
        willEffect = self.invoker.getStatusEffectOfId(SEE.EFFECT_WILL_OF_THE_PEOPLE)
        if willEffect:
            willEffect.handleMobMentality()

        # Figure out the current mob situation
        mobMembersPerFill = self.extraArgs.pop(2)
        maxMobMembers = self.extraArgs.pop(1)
        currentReserves = len(instance.reserveSuits)
        self.extraArgs += [currentReserves]

        # Give the targets hivemind if
        # there are 13 or more suits in the mob.
        if currentReserves >= 13:
            for target in self.targets:
                hivemindEffect = SEG.createStatusEffect(target, SEE.EFFECT_HIVEMIND)
                target.addStatusEffect(SEE.EFFECT_HIVEMIND, hivemindEffect)
        # Give the targets lure resistance when 
        # there are 6 or more suits in the mob.
        elif currentReserves >= 6:
            for target in self.targets:
                lureEffect = SEG.createStatusEffect(target, SEE.EFFECT_LURE_RESISTANCE)
                lureEffect.setAmount(2)
                target.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE, lureEffect)

        # Check if they have Hivemind
        # If they do, adjust their attack targets
        for target in self.targets:
            hivemindEffect = target.getStatusEffectOfId(SEE.EFFECT_HIVEMIND)
            if hivemindEffect:
                hivemindEffect.retargetSuitAttacks()

        if currentReserves >= maxMobMembers:
            return

        suits = instance.generateMobMentalitySuits(min(currentReserves + mobMembersPerFill, maxMobMembers) - currentReserves)
        self.extraArgs += [s.doId for s in suits]

        if currentReserves + len(suits) >= 8:
            # Increase the battle cap to 5 upon reaching 8 mob members.
            self.invoker.battle.maxSuits = 5
    
    def setTargetList(self) -> None:
        # Create a list of suits sorted by level.
        otherSuits = sorted(self.getOtherSuits(), key=lambda x: x.getActualLevel())
        # Grab the amount desired to be targeted.
        self.targets = otherSuits[:min(self.extraArgs[0], len(otherSuits))]

    def getAttackArgs(self, index: int) -> dict:
        return {"damageMult": self.MULT_VALUES.get(len(self.targets), 0.5)}


@AttackClassAI(attackType=AttackEnum.PEELING_THE_BARK)
class PeelingTheBarkAI(DamageInflictStatusAttackAI):
    STATUS_EFFECT = SEE.EFFECT_PEELING_THE_BARK

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        if target.isSuit():
            if not target.getStatusEffectOfId(SEE.EFFECT_PEELING_THE_BARK_SUIT):
                target.addStatusEffect(SEE.EFFECT_PEELING_THE_BARK_SUIT)
            return

        target.addStatusEffect(SEE.EFFECT_PEELING_THE_BARK)

    def setTargetList(self) -> None:
        self.targets = self.getToons() + self.getOtherSuits()
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return self.invoker.getAttackDamage(self.attackType)


@AttackClassAI(attackType=AttackEnum.POWER_NAP_HEAL)
class PowerNapHealAI(SuitHealAttackAI):
    EffectsToRemove = [
        SEE.EFFECT_SUIT_LURED, SEE.EFFECT_SUIT_SUED, SEE.EFFECT_SUIT_DAZED, SEE.EFFECT_SUIT_SOAKED,
        SEE.EFFECT_SUIT_DRENCHED, SEE.EFFECT_COGS_DAMAGE_DOWN
    ]

    def calculate(self, ignoreModifiers: bool = False):
        super().calculate(ignoreModifiers=False)
        for target in self.targets:
            targetWasLured = target.getStatusEffectOfId(SEE.EFFECT_SUIT_LURED)
            # Remove all the indicated effects
            for effectId in self.EffectsToRemove:
                target.removeStatusEffectOfId(effectId)
            # Give them an extra attack if they were lured previously.
            if targetWasLured:
                self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                    target.getRandomAttack(), {"invoker": target, "unlure": True},
                    {"respectPreviousAdditions": True}
                ])


@AttackClassAI(attackType=AttackEnum.POWER_NAP_KILL_DAMAGE_UP)
class PowerNapKillDamageUpAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_POWER_NAP_KILL_DMG_BOOST

    def calculate(self) -> None:
        # Apply the status effect to each target.
        for target in self.targets:
            result = self.createAttackTarget(target.doId)

            if self.getLanded():
                result.landed = True
                self.handleStatusEffect(target, extraArgs=self.extraArgs[:])

    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=AttackEnum.GATEKEEPER_FODDER_KILL_PIERCE)
class GatekeeperFodderKillPierceAI(PowerNapKillDamageUpAI):
    STATUS_EFFECT = SEE.EFFECT_GATEKEEPER_TOON_PIERCE


@AttackClassAI(attackType=AttackEnum.GATEKEEPER_JUMP_UNLURE_FODDER)
class GatekeeperJumpUnlureFodderAI(AttackAI):
    REQUIRED_TARGETS = 1

    def setTargetList(self) -> None:
        luredSuits = [suit for suit in self.getAliveSuits() if suit is not self.invoker and suit.getStatusEffectOfId(SEE.EFFECT_SUIT_LURED)]
        if luredSuits:
            self.targets = [random.choice(luredSuits)]

    def calculate(self):
        for target in self.targets:
            luredEffect = target.getStatusEffectOfId(SEE.EFFECT_SUIT_LURED)
            # Give them an extra attack if they were lured previously.
            if luredEffect:
                self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                    target.getRandomAttack(), {"invoker": target, "unlure": True},
                    {"respectPreviousAdditions": True}
                ])
                attackTarget = self.createAttackTarget(target.doId)

                attackTarget.landed = True
                attackTarget.hpAdjust = 0


@AttackClassAI(attackType=(AttackEnum.PICK_UP_THE_PACE, AttackEnum.OVERCLOCKED, AttackEnum.FTF_ATTORNEY_PICK_UP_THE_PACE))
class PickUpThePaceAI(DoNothingAI):
    """
    This is the speedup attack class for Pacesetter.
    The speed type and timescale are sent to the client.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.extraArgs[0] *= 100
        if len(self.extraArgs) > 1:
            self.extraArgs[1] *= 100


@AttackClassAI(attackType=AttackEnum.SLUSH_FUND)
class SlushFundAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_SLUSH_FUND
    REQUIRED_TARGETS = 1

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        status = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        status.setRounds(1)
        target.addStatusEffect(self.STATUS_EFFECT, status)

    def setTargetList(self) -> None:
        self.targets = self.getOtherSuits()


class WagerBaseAI(AttackAI):

    def calculate(self) -> None:
        pass
    
    def getTauntPool(self):
        return TTLocalizer.DuckShufflerRollStart


@AttackClassAI(attackType=AttackEnum.WAGER_BAR)
class WagerBarAI(RemoveStatusEffectAttackAI, GenericDamageAttackAI, WagerBaseAI):
    """Hits every target for differing damage values,
    while attempting to remove lure effects.
    """
    STATUS_EFFECT = SEE.EFFECT_SUIT_LURED

    def calculate(self) -> None:
        RemoveStatusEffectAttackAI.calculate(self)
        GenericDamageAttackAI.calculate(self)
    
    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        if self.isSuit(target):
            self.unlureSuit(target, instant=True)

    def setTargetList(self) -> None:
        self.targets = [*self.getAliveSuits(), *self.getToons()]

    def getDamage(self, target: BattleAvatar = None) -> int:
        if isinstance(target, DistributedSuitBaseAI):
            return 8
        return self.invoker.getAttackDamage(self.attackType)


@AttackClassAI(attackType=AttackEnum.WAGER_BEANS)
class WagerBeansAI(WagerBaseAI):
    
    def calculate(self) -> None:
        for target in self.targets:
            target: DistributedToonBaseAI

            # Give them silly little beans :)
            target.addMoney(20)
    
    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=AttackEnum.WAGER_BUST)
class WagerBustAI(DoNothingAI, WagerBaseAI):
    """
    This is the attack object used for Wager Bust.
    Nothing Happens! but it must inherit from WagerBaseAI
    """
    pass


@AttackClassAI(attackType=AttackEnum.WAGER_DUCKS)
class WagerDucksAI(GenericDamageAttackAI, WagerBaseAI):
    """
    This is the attack object used for Wager Ducks
    This is used when the shuffler rolls ducks
    Damages and turns people into ducks
    """

    def calculate(self) -> None:
        super().calculate()

        for target in self.targets:
            if not target.getVisualEffectOfId(VisualEffectEnum.TOON_BECOME_DUCK) and hasattr(target, 'dna'):
                newSpeciesType = ToonDNA.toonSpeciesTypes.index('f')
                oldSpeciesType = ToonDNA.toonSpeciesTypes.index(target.dna.head[0])
                target.addVisualEffect(VisualEffectEnum.TOON_BECOME_DUCK, [newSpeciesType, oldSpeciesType])
    
    def setTargetList(self) -> None:
        self.targets = self.getToons()
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return self.invoker.getAttackDamage(self.attackType)


@AttackClassAI(attackType=AttackEnum.WAGER_SEVENS)
class WagerSevensAI(GenericDamageAttackAI, WagerBaseAI):
    HEAL_CAP = 1.5
    HEAL_ADDITIVE = True

    def setTargetList(self) -> None:
        self.targets = [*self.getAliveSuits(), *self.getToons()]
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return -7  # negative for a heal


@AttackClassAI(attackType=AttackEnum.WOODCHIPPER)
class WoodchipperAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_WOODCHIPPER
    REQUIRED_TARGETS = 1

    def setTargetList(self) -> None:
        # Simply apply Woodchipper to a random Toon
        activeToons = self.getToons() # type: list[DistributedToonBaseAI]
        toonsWithoutEffect = []
        for toon in activeToons:
            if not toon.getStatusEffectsOfId(self.STATUS_EFFECT):
                toonsWithoutEffect.append(toon)

        chosenToon = random.choice(toonsWithoutEffect if toonsWithoutEffect else activeToons)
        if chosenToon:
            self.targets = [chosenToon]


@AttackClassAI(attackType=AttackEnum.ZERO_TASK)
class ZeroTaskAI(GenericDamageAttackAI):
    HEAL_CAP = 2.0
    HEAL_ADDITIVE = True
    REQUIRED_TARGETS = 1

    def calculate(self) -> None:
        # RNG response to the heal.
        self.extraArgs = [random.randint(0, 99) for _ in self.targets]

        GenericDamageAttackAI.calculate(self)
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return -40  # negative for a heal
    
    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()
        if len(self.targets) > 1:
            self.targets = [suit for suit in self.getOtherSuits()]


@AttackClassAI(attackType=AttackEnum.CASTLING)
class CastlingAI(DoNothingAI):
    REQUIRED_TARGETS = 1

    def calculate(self) -> None:
        # Make sure invoker is in suit list.
        if self.invoker not in self.suits:
            return
        # Find invoker's index in the suit list.
        invokerIndex = self.suits.index(self.invoker)

        # Find a good suit to swap with.
        # Make lists of suits with good properties.
        untrappedSuits = [suit for suit in self.targets if not suit.getStatusEffectOfType(StatusEffects.TrappedStatusEffect)]
        drySuits = [suit for suit in self.targets if not suit.getStatusEffectOfType(StatusEffects.SoakStatusEffect)]
        listToUse = PythonUtil.union(untrappedSuits, drySuits) or untrappedSuits or drySuits or self.targets

        # Get a random suit out of the ones with the best properties.
        otherSuit = random.choice(listToUse)
        # Find target's index in the suit list.
        otherIndex = self.suits.index(otherSuit)
        # Remove invoker from the list.
        self.suits.remove(self.invoker)
        # Reinsert at the other suit's index
        self.suits.insert(otherIndex, self.invoker)
        # Same idea for the other suit
        self.suits.remove(otherSuit)
        self.suits.insert(invokerIndex, otherSuit)

        # Exchange traps so that the traps stay in their positions.
        invokerTrapEffect = self.invoker.getStatusEffectOfType(StatusEffects.TrappedStatusEffect)
        invokerBattleTrap = self.invoker.battleTrap
        otherTrapEffect = otherSuit.getStatusEffectOfType(StatusEffects.TrappedStatusEffect)
        otherBattleTrap = otherSuit.battleTrap

        # Swap info between the two
        otherSuit.battleTrap = invokerBattleTrap
        self.invoker.battleTrap = otherBattleTrap

        if invokerTrapEffect:
            self.invoker.statusEffects.remove(invokerTrapEffect)
        if otherTrapEffect:
            otherSuit.statusEffects.remove(otherTrapEffect)
        if invokerTrapEffect:
            invokerTrapEffect.avProfile = otherSuit
            otherSuit.addStatusEffect(SEE.EFFECT_SUIT_TRAPPED, invokerTrapEffect)
        if otherTrapEffect:
            otherTrapEffect.avProfile = self.invoker
            self.invoker.addStatusEffect(SEE.EFFECT_SUIT_TRAPPED, otherTrapEffect)

        # Now that we're done messing with the suit order, send an event to change Toon attack targets.
        # We want Toon attacks to continue targeting their original positions, essentially.
        self.sendEvent(BEG.EVENT_TOON_TARGETING_OVERRIDE, [{
            self.invoker.doId: otherSuit.doId,
            otherSuit.doId: self.invoker.doId
        }])

        # Create attack target so client gets sent the suit to swap with.
        self.createAttackTarget(otherSuit.doId)

        # Finally, unlure the target.
        self.unlureSuit(otherSuit, instant=True)

    def setTargetList(self) -> None:
        self.targets = self.getOtherSuits()


@AttackClassAI(attackType=AttackEnum.BRAIN_WAVE)
class BrainWaveAI(SuitGroupAttackAI):
    def calculate(self) -> None:
        super().calculate()

        # Remove lure from all the extra cogs
        for suitId in self.extraArgs:
            suit = simbase.air.doId2do.get(suitId)
            if suit:
                suit.removeStatusEffectOfId(SEE.EFFECT_SUIT_LURED)
    
    def setTargetList(self) -> None:
        pass # Targets are predefined.


@AttackClassAI(attackType=AttackEnum.PT_BLOCK_SOUND_ENTER)
class PrethinkerBlockSoundEnterAI(ApplyStatusEffectToSelfAttackAI):
    STATUS_EFFECT = SEE.EFFECT_PRETHINKER_DODGE_SOUND

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list=None) -> None:
        # If our chosen cog is alive, dodge sound completely.
        # Otherwise, take half damage from sound.
        effectId = SEE.EFFECT_PRETHINKER_DODGE_SOUND if self.cogStandingBehind.getHp() > 0 else SEE.EFFECT_PRETHINKER_DAMAGE_TAKEN_DOWN
        target.addStatusEffect(effectId)

    @property
    def cogStandingBehind(self):
        return self.invoker.battle.activeSuits[self.extraArgs[0]]


@AttackClassAI(attackType=AttackEnum.PT_BLOCK_SOUND_EXIT)
class PrethinkerBlockSoundExitAI(RemoveStatusEffectFromSelfAttackAI):
    STATUS_EFFECT = [SEE.EFFECT_PRETHINKER_DODGE_SOUND, SEE.EFFECT_PRETHINKER_DAMAGE_TAKEN_DOWN]


class WeatherBaseAI(DoNothingAI):
    pass


@AttackClassAI(attackType=AttackEnum.WEATHER_FOG)
class FogAI(WeatherBaseAI):
    pass


@AttackClassAI(attackType=AttackEnum.WEATHER_HEAVY_RAIN)
class HeavyRainAI(WeatherBaseAI):
    pass


@AttackClassAI(attackType=AttackEnum.WEATHER_INVERSION)
class InversionAI(ApplyStatusEffectToSelfAttackAI, WeatherBaseAI):
    STATUS_EFFECT = SEE.EFFECT_GENERIC_EXTRA_ATTACKS

    def calculate(self, ignoreModifiers: bool = False) -> None:
        ApplyStatusEffectToSelfAttackAI.calculate(self)
        # WeatherBaseAI.calculate(self)


@AttackClassAI(attackType=AttackEnum.WEATHER_MONSOON)
class MonsoonAI(WeatherBaseAI):
    pass


@AttackClassAI(attackType=AttackEnum.WEATHER_OIL_RAIN)
class OilRainAI(WeatherBaseAI):
    pass


@AttackClassAI(attackType=AttackEnum.WEATHER_STORM_CELL)
class StormCellAI(WeatherBaseAI):
    pass


@AttackClassAI(attackType=AttackEnum.HEAVY_RAIN_ZAP)
class HeavyRainZapAI(HitAllParticipantsAttackAI, RemoveStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_HEAVY_RAIN

    def calculate(self, ignoreModifiers: bool = False) -> None:
        HitAllParticipantsAttackAI.calculate(self, ignoreModifiers=True)

        for result in self.results:
            if result.landed:
                target = self.findTarget(result.avId)
                self.handleStatusEffect(target)

    def getDamage(self, target: BattleAvatar = None) -> int:
        statusEffect = target.getStatusEffectOfId(SEE.EFFECT_HEAVY_RAIN)
        if statusEffect:
            return statusEffect.getDamageAbsorbed()
        return 0


@AttackClassAI(attackType=AttackEnum.STORM_CELL_ZAP)
class StormCellZapAI(DamageAttackAI):

    def calculate(self, ignoreModifiers: bool = False) -> None:
        for target in self.targets:
            result = self.getDamage(target)
            attackTarget = self.createAttackTarget(target.doId)
            attackTarget.landed = 1
            if isinstance(target, DistributedToonBaseAI):
                attackTarget.hpAdjust = result
            # else:
            #     attackTarget.hpAdjust = (round(target.getMaxHp() * 1.5) - target.getHp())

    def getLanded(self) -> bool:
        return True

    def setTargetList(self) -> None:
        self.targets = self.getAliveToons()  #  + self.getAliveSuits()


@AttackClassAI(attackType=AttackEnum.RAINMAKER_ENDING_0)
class RainmakerEnding0AI(WeatherBaseAI):
    pass


@AttackClassAI(attackType=(
    AttackEnum.RAINMAKER_ENDING_1, AttackEnum.RAINMAKER_ENDING_2,
    AttackEnum.RAINMAKER_ENDING_3, AttackEnum.RAINMAKER_ENDING_4,
))
class RainmakerEndingAI(DoNothingAI):
    ADDITIONAL_BARRIER_LENGTH = 40


@AttackClassAI(attackType=AttackEnum.RAINMAKER_ENDING_4)
class RainmakerFinalEndingAI(InstakillAttackAI):
    ADDITIONAL_BARRIER_LENGTH = 40


@AttackClassAI(attackType=AttackEnum.STANDUP_GUY)
class StandupGuyAI(ApplyStatusEffectToSelfAttackAI):
    STATUS_EFFECT = SEE.EFFECT_STANDUP_GUY

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        newEffect, _ = target.addStatusEffect(self.STATUS_EFFECT)
        if newEffect:
            newEffect.setMultiplier(self.extraArgs[1])


@AttackClassAI(attackType=AttackEnum.SHAKEDOWN)
class ShakedownAI(ApplyStatusEffectAttackAI, SuitSingleAttackAI):
    STATUS_EFFECT = [SEE.EFFECT_REWARD_COOLDOWN, SEE.EFFECT_DAMAGE_TAKEN_UP]

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        """Decide whether to give the target a unite cooldown or vulnerability
        status effect.
        """
        rounds = self.extraArgs[0]
        damageTaken = self.extraArgs[1]

        # The target already has a unite cooldown, give them vulnerability
        # instead.
        if target.getStatusEffectOfType(StatusEffects.RewardCooldownStatusEffect):
            effect = SEG.createStatusEffect(target, self.STATUS_EFFECT[1])
            effect.setMultiplier(damageTaken)
            target.addStatusEffect(self.STATUS_EFFECT[1], effect)

            # Used for the attack name description.
            self.extraArgs = [1]
            return

        # They don't have a unite cooldown. Let's fix that.
        effect = SEG.createStatusEffect(target, self.STATUS_EFFECT[0])
        effect.setRounds(rounds)
        target.addStatusEffect(self.STATUS_EFFECT[0], effect)

        # Used for the attack name description.
        self.extraArgs = [0]

    def setTargetList(self) -> None:
        # Pick a random target using the suit single attack logic.
        return SuitSingleAttackAI.setTargetList(self)


@AttackClassAI(attackType=AttackEnum.KICK_UP)
class KickUpAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_SUIT_DAMAGE_BOOST
    REQUIRED_TARGETS = 1

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        effect = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        effect.setMultiplier(self.extraArgs[0])
        target.addStatusEffect(self.STATUS_EFFECT, effect)

    def setTargetList(self) -> None:
        # Choose a random investor to boost.
        suits = [suit for suit in self.getOtherSuits() if suit.isSkelecog]
        if suits:
            self.targets = [random.choice(suits)]
        else:
            self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.SITDOWN)
class SitdownAI(DoNothingAI):
    """Styx simply generates a new waiter to join the battle.
    """

    def calculate(self) -> None:
        waiterLevel, instance = self.extraArgs

        # Generate a executive waiter at the specified level.
        waiter = instance.generateRandomReserve(waiterLevel, True, True)
        if waiter:
            waiter.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE, extraArgs=[2])


@AttackClassAI(attackType=AttackEnum.USURY)
class UsuryAI(GenericDamageAttackAI):
    REQUIRED_TARGETS = 2
    HEAL_CAP = 1.25
    HEAL_ADDITIVE = True

    def setTargetList(self) -> None:
        # Is this a waiter case, or fodder case?
        self.waiterUsury = self.extraArgs[0]

        # Add the invoker to the target list first.
        self.targets.append(self.invoker)

        # Get the other alive suits.
        suits = self.getOtherSuits()

        if self.waiterUsury:
            waiter = [suit for suit in suits if suit.isWaiter]
            if waiter:
                self.targets.append(waiter[0])
        else:
            regularSuits = [suit for suit in suits if not suit.isMiniboss()]
            if regularSuits:
                self.targets.extend(regularSuits)
                self.HEAL_CAP = 1.5

    
    def getDamage(self, target: BattleAvatar = None) -> int:
        # We get a third of a waiter's health, or three quarters of the fodders' health.
        portion = 1 / 3 if self.waiterUsury else 3 / 4

        # We'll have to calculate each of the damaged cogs' health to determine styx's heal.
        if target is self.invoker:
            damage = 0
            # Get a portion of each suit's health.
            for i in range(1, len(self.targets)):
                damage += math.ceil(min(self.targets[i].getMaxHp() * portion, self.targets[i].getHp()))
            # The invoker gets healed with the damage.
            return -damage
        else:
            damage = math.ceil(min(target.getMaxHp() * portion, target.getHp()))
            # The target gets the damage taken from them.
            return damage

    def applyDamageModifiers(self, target: BattleAvatar, attackDamage: int,
                             damaging: bool=True, invokerMods: bool=False, 
                             targetMods: bool=True):
        """Overriden to set the default value for invokerMods to False."""
        return super().applyDamageModifiers(target, attackDamage, damaging, invokerMods, targetMods)


@AttackClassAI(attackType=AttackEnum.TRIBUTE)
class TributeAI(GenericDamageAttackAI):
    REQUIRED_TARGETS = 2
    HEAL_CAP = 1.25
    HEAL_ADDITIVE = True

    def setTargetList(self) -> None:
        # Get a sorted list of all the suits in battle that are in need of health.
        suits = sorted([
            suit for suit in self.getOtherSuits()
            if suit.dna.name != "pcrat"
        ], key=attrgetter("hp"))

        # Alter the health conditions if there are no
        # satellite investors present.
        if all([not suit.isSkelecog for suit in suits]):
            self.HEAL_ADDITIVE = False
            self.HEAL_CAP = 1.5

        # Now we can check if any of the suits are below the health cap.
        suits = [suit for suit in suits if suit.getHealthPercentage() < self.HEAL_CAP]

        # Finally, further sort to prioritize the investors.
        suits = sorted(suits, key=lambda s: s.isSkelecog, reverse=True)
        if suits:
            self.targets = [self.invoker, suits[0]]
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        # Get 10% of the invoker's current hp.
        damage = math.ceil(self.invoker.getHp() * (0.1 if target.isSkelecog else 0.05))

        # Apply that damage to the invoker.
        if target is self.invoker:
            return damage

        # If the target is not an investor,
        # heal it into overcharge.
        if not target.isSkelecog:
            return -1.5

        # Otherwise heal twice the amount.
        return -(damage * 2)
    
    def applyDamageModifiers(self, target: BattleAvatar, attackDamage: int,
                             damaging: bool=True, invokerMods: bool=False, 
                             targetMods: bool=True):
        """Overriden to set the default value for invokerMods to False."""
        return super().applyDamageModifiers(target, attackDamage, damaging, invokerMods, targetMods)


@AttackClassAI(attackType=AttackEnum.RUSH_JOB)
class RushJobAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_RUSH_JOB
    REQUIRED_TARGETS = 1

    RUSHJOB_ACCUP = -10

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        return super().handleStatusEffect(target, [self.RUSHJOB_ACCUP, self.extraArgs[0], self.extraArgs[1]])
    
    def setTargetList(self) -> None:
        # Go over all targets. Remove the rush job visual effect.
        for suit in self.getAliveSuits():
            suit.removeVisualEffectOfId(VisualEffectEnum.RUSH_JOB)

        # Choose a random target without rush job.
        potentialTargets = [suit for suit in self.getAliveSuits()
                            if suit and not suit.getStatusEffectOfId(SEE.EFFECT_RUSH_JOB)]
        if not potentialTargets:
            return

        target = random.choice(potentialTargets)

        # Get the manager effect. Under certain conditions, we will force
        # the invoker (Pacesetter) to be the target himself.
        mgrEffect = self.invoker.getStatusEffectOfType(StatusEffects.PacesetterStatusEffectBase) if self.invoker else None
        if self.invoker in potentialTargets and mgrEffect and (mgrEffect.isMaxed() and not mgrEffect.isInChallengeMode()):
            target = self.invoker

        fromAttorney = self.extraArgs[0]

        # Do some funnies from here.
        if isinstance(target, DistributedToonBaseAI):
            self.extraArgs = [AttackEnum.TOON_HEAL]
        elif isinstance(target, DistributedSuitBaseAI):
            choices = [t for t in ATTACK_TRACKS if t != AttackEnum.TOON_HEAL]

            # Remove trap & lure from being used on lured cogs.
            if target.getStatusEffectOfType(StatusEffects.LureStatusEffect):
                choices.remove(AttackEnum.TOON_TRAP)
                choices.remove(AttackEnum.TOON_LURE)
            # Remove trap from being used on trapped cogs.
            elif target.getStatusEffectOfType(StatusEffects.TrappedStatusEffect):
                choices.remove(AttackEnum.TOON_TRAP)

            self.extraArgs = [random.choice(choices)]
        else:
            return

        self.extraArgs.append(fromAttorney)
        self.targets = [target]

        # Clear debuffs too
        target.clearStatusEffectsOfQuality(quality=DEBUFF, exceptions=[SEE.EFFECT_SUIT_TRAPPED])


@AttackClassAI(attackType=AttackEnum.HURRY_SICKNESS)
class HurrySicknessAI(DamageInflictStatusAttackAI):
    STATUS_EFFECT = SEE.EFFECT_HURRY_SICKNESS

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        return super().handleStatusEffect(target, [self.extraArgs[0], .75, self.extraArgs[1], self.extraArgs[3]])

    def setTargetList(self) -> None:
        self.targets = self.getToons()

    def getDamage(self, target: BattleAvatar = None) -> int:
        # Deals 10 more damage for each mistake the players have made.
        return 35 + (self.extraArgs[2] * 10)


@AttackClassAI(attackType=AttackEnum.HURRY_SICKNESS_MG)
class HurrySicknessMGAI(HurrySicknessAI):
    def setTargetList(self) -> None:
        return


@AttackClassAI(attackType=AttackEnum.CORPORATE_RESTRUCTURING)
class CorporateRestructuringAI(DoNothingAI):
    REQUIRED_TARGETS = 2

    def calculate(self) -> None:
        # Get a shallow of the old suits to hash.
        oldsuits = self.suits.copy()
        # Shuffle the suits.
        random.shuffle(self.suits)
        # If there was literally no change, just reverse
        # the list.
        if self.suits == oldsuits:
            self.suits.reverse()

        for suit in self.targets:
            index = self.suits.index(suit)
            attackTarget = self.createAttackTarget(suit.doId)
            attackTarget.extraArgs = [index]

        self.extraArgs = [suit.doId for suit in self.suits]
    
    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()


@AttackClassAI(attackType=AttackEnum.CONTENT_SYNC)
class ContentSyncAI(AttackAI):

    def calculate(self) -> None:
        self.sendEvent(BEG.EVENT_PACESETTER_RANDOMIZE_GAG_ORDER)
        for toon in self.targets:
            self.createAttackTarget(toon.doId)

    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=AttackEnum.MOVING_GOALPOSTS)
class MovingGoalpostsAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_MOVING_GOALPOSTS

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        status = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        for track in range(len(BattleGlobals.Tracks)):
            status.setGagLevel(track, random.choice([4, 5, 6, 7]))
        target.addStatusEffect(self.STATUS_EFFECT, status)

    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=AttackEnum.ROCKING_IN_RHYTHM)
class RockingInRhythmAI(GenericDamageAttackAI):
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'tauntIndex', 'damageDict',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damageDict = self.extraArgs[0]
        self.extraArgs = []
    
    def setTargetList(self) -> None:
        self.targets = self.getObjectsFromIds(list(self.damageDict))
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return self.damageDict.get(target.doId, 0)
    
    def applyDamageModifiers(self, target: BattleAvatar, attackDamage: int, 
                             damaging: bool = True, invokerMods: bool = True, 
                             targetMods: bool = True):
        if isinstance(target, DistributedSuitBaseAI):
            return attackDamage
        return super().applyDamageModifiers(target, attackDamage, damaging, invokerMods, targetMods)


@AttackClassAI(attackType=AttackEnum.STAR_OF_THE_SHOW)
class StarOfTheShowAI(AttackAI):
    """
    Every 3 rounds, starting on round 2, the Major Player will select
    an audience member as a willing volunteer to join the show!
    """

    def calculate(self) -> None:
        # Let's add a new cog to the battle.
        instance = self.battle.instance
        suitIndex, newSuit = instance.createAudienceSuit()
        if not newSuit:
            # No suits :(
            self.extraArgs = [-1]
            self.targets = []
        else:
            # Add an audience member to the reserves.
            instance.reserveSuits.append(newSuit)
            self.extraArgs = [suitIndex]
            startingDamage = 20 if self.battle.hasRevived else 30
            newSuit.addStartingStatusEffect(SEE.EFFECT_STAR_OF_THE_SHOW, extraArgs=[startingDamage, 0])
            self.targets = self.getAliveSuits()

    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()


@AttackClassAI(attackType=AttackEnum.GUEST_VERSE_START)
class GuestVerseStartAI(ApplyStatusEffectAttackAI, CreateAttackAttackAI):
    """
    Crazy Piano Guy tells weird sidekick to show off their amazing moves
    """
    STATUS_EFFECT = SEE.EFFECT_GUEST_VERSE

    def calculate(self) -> None:
        # The cutscene will need to know if our target is a star so it knows how to manipulate the stagelight.
        self.extraArgs.append(self.targets[0].hasStatusEffectOfId(SEE.EFFECT_STAR_OF_THE_SHOW))
        ApplyStatusEffectAttackAI.calculate(self)
        self.unlureSuit(self.targets[0], instant=True)
        CreateAttackAttackAI.calculate(self)

    def setTargetList(self) -> None:
        self.targets = [random.choice(self.getOtherSuits())]


@AttackClassAI(attackType=AttackEnum.DANCE_PARTNERS)
class DancePartnersAI(AttackAI):
    """
    Summons Dance Partners!! WE LOVE FRIENDS!!!!
    """

    def calculate(self) -> None:
        # So first, we are going to spawn up to ONE new suit per Toon.
        # It also depends on if there is room to spawn them, too!
        suitsToSpawn = len(self.getAliveToons())
        maxSpawnsForPartners = 5  # max suits, but with one less tbh
        openSpots = maxSpawnsForPartners - len(self.getAliveSuits())
        suitsToSpawn = min(suitsToSpawn, openSpots)

        # Figure out how many Toons are ready for partners.
        partnerableToons = [toon for toon in self.getAliveToons()
                            if not toon.getStatusEffectsOfId(SEE.EFFECT_DANCE_PARTNER)]

        # Only spawn a suit per available Toon.
        suitsToSpawn = min(suitsToSpawn, len(partnerableToons))

        # Go ahead and spawn the suits.
        if suitsToSpawn > 0:
            # Suit time !! Add them to reserves NOW.
            newSoots = self.battle.instance.generateReserveSuits(suitsToSpawn, False)
            self.battle.instance.oopsAllBuffs(
                newSoots,
                reviveOverride=False,
                isActive=False
            )
            self.extraArgs = [min(len(partnerableToons), len(newSoots))]

            # Figure out which indices are OK.
            # This logic is the same in Environmentals.py for the major player revive.
            validEffectIndices = list(range(8))  # just obligatory number idk lol
            for toon in self.getAliveToons():
                existingPartnerEffect = toon.getStatusEffectOfId(SEE.EFFECT_DANCE_PARTNER)
                if existingPartnerEffect:
                    effectIndex = existingPartnerEffect.getEffectIndex()
                    if effectIndex in validEffectIndices:
                        validEffectIndices.remove(effectIndex)

            # Assign soulmates.
            toonList = partnerableToons[:]
            sootList = newSoots[:]
            random.shuffle(toonList)
            random.shuffle(sootList)
            for silyLilCritter, genericAntagonist in zip(toonList, sootList):
                effectIndex = validEffectIndices.pop(0)
                avId_A = silyLilCritter.getDoId()
                avId_B = genericAntagonist.getDoId()
                silyLilCritter.addStatusEffect(
                    effectId=SEE.EFFECT_DANCE_PARTNER,
                    extraArgs=[effectIndex, avId_A, avId_B],
                )
                genericAntagonist.addStartingStatusEffect(
                    effectId=SEE.EFFECT_DANCE_PARTNER,
                    extraArgs=[effectIndex, avId_A, avId_B],
                )
                self.extraArgs.append(avId_A)
                self.extraArgs.append(avId_B)
        else:
            # NO NEW SUITS. CRINGE!!!!!!
            self.extraArgs = [0]

    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()


@AttackClassAI(attackType=AttackEnum.TOON_STAR_BONUS_TEXT)
class ToonStarBonusTextAI(PowerNapKillDamageUpAI):
    STATUS_EFFECT = SEE.EFFECT_STAR_OF_THE_SHOW_TOON


@AttackClassAI(attackType=AttackEnum.BELLRINGER_FODDER_EXPLOSION)
class BellringerFodderExplosionAI(HitAllParticipantsAttackAI):
    WANT_TAUNT = True

    def calculate(self, ignoreModifiers: bool = False) -> None:
        if self.getLanded():
            # Let this cog know to stop preventing death because we need to Kill Them Now
            self.sendEvent(BEG.EVENT_BELLRING_FODDER_IGNORE_PREVENT_DEATH, [self.invoker])

        super().calculate(ignoreModifiers=ignoreModifiers)

    def getDamage(self, target: BattleAvatar = None) -> int:
        if target is self.invoker:
            return 50000
        elif target.isToon():
            return 20
        elif target.dna.name == 'bellring':
            return 400
        else:
            return 40


@AttackClassAI(attackType=AttackEnum.RED_THREAD)
class RedThreadAI(AttackAI):
    """
    Used by the Mouthpiece at the end of every turn.
    """

    def getLanded(self) -> bool:
        return True

    def setTargetList(self) -> None:
        self.targets = self.getAliveToons() + self.getOtherSuits()

    def calculate(self) -> None:
        # try and pair up toons with cogs,  excess toons get paired with each other
        toons = self.getAliveToons()
        suits = self.getOtherSuits()

        # Ensure that our toons & suits don't have the red thread effect, as we're giving them all a new one.
        for av in toons + suits:
            av.removeStatusEffectOfId(SEE.EFFECT_RED_THREAD)
            av.removeVisualEffectsOfId(VisualEffectEnum.RED_THREAD)

        leftoverToons = len(toons) - len(suits)
        for toon, suit in zip(toons, suits):
            toon.addStatusEffect(effectId=SEE.EFFECT_RED_THREAD, extraArgs=[suit.doId])
            suit.addStatusEffect(effectId=SEE.EFFECT_RED_THREAD, extraArgs=[toon.doId])
            toon.addVisualEffect(VisualEffectEnum.RED_THREAD, extraArgs=[suit.doId])
            self.extraArgs.extend((toon.doId, suit.doId))
        if leftoverToons >= 2:
            # Naughty toons are bound together.
            naughtyToons = toons[-leftoverToons:] # rightmost toons i think
            assert len(naughtyToons) == leftoverToons
            for toon in naughtyToons:
                toon.addStatusEffect(effectId=SEE.EFFECT_RED_THREAD_TANGLED)
            for first, second in zip(naughtyToons, naughtyToons[1:]):
                first.addVisualEffect(VisualEffectEnum.RED_THREAD, extraArgs=[second.doId])
                self.extraArgs.extend((first.doId, second.doId))
        # bookkeeping
        for target in self.targets:
            attackTarget = self.createAttackTarget(target.doId)
            attackTarget.landed = True
            attackTarget.hpAdjust = 0


@AttackClassAI(attackType=AttackEnum.SNOW_SQUALL)
class SnowSquallAI(DoNothingAI):
    """Used by the Plutocrat to toggle the weather."""
    __slots__ = "toggleEffect",

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.toggleEffect = self.extraArgs[1]

    def calculate(self) -> None:
        self.sendEvent(BEG.EVENT_PCRAT_WEATHER, [
            PlutocratWeather.SNOW_SQUALL if self.toggleEffect else PlutocratWeather.NORMAL])


@AttackClassAI(attackType=AttackEnum.SNOW_SQUALL_DAMAGE)
class SnowSquallDamageAI(DamageAttackAI):

    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=AttackEnum.SHATTER_DAMAGE)
class ShatterDamageAI(GenericDamageAttackAI):
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'tauntIndex', 'suit',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    REQUIRED_TARGETS = 1
    DamagePercent = 0.5

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.suit: DistributedSuitBaseAI = self.extraArgs[0]
    
    def cleanup(self) -> None:
        del self.suit
        return super().cleanup()

    def calculate(self, ignoreModifiers: bool = True) -> None:
        super().calculate(ignoreModifiers)

    def setTargetList(self) -> None:
        if self.suit not in self.suits:
            return

        # Target the nearby suits if possible.
        index = self.suits.index(self.suit)
        if index > 0:
            suit: DistributedSuitBaseAI = self.suits[index - 1]
            if suit.canBeAttacked():
                self.targets.append(suit)

        if index < len(self.suits) - 1:
            suit: DistributedSuitBaseAI = self.suits[index + 1]
            if suit.canBeAttacked():
                self.targets.append(suit)

    def getDamage(self, target: BattleAvatar = None) -> int:
        # Shatter deals 40% of the killed suit's max health.
        damage = math.ceil(self.suit.getMaxHp() * self.DamagePercent)

        # The Plutocrat specifically has a case where he can
        # modify damage taken from shatter.
        effect = target.getStatusEffectOfId(SEE.EFFECT_MANAGER_PLUTOCRAT)
        if effect:
            damage = effect.handleAttackDamageTaken(damage, self.attackType, None)
        
        return damage


@AttackClassAI(attackType=AttackEnum.BEWITCHMENT)
class BewitchmentAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_BEWITCHMENT

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        return super().handleStatusEffect(target, [1.75, True, True, 1.3, self.extraArgs[0]])


@AttackClassAI(attackType=AttackEnum.PYROMANIAC)
class PyromaniacAI(DoNothingAI):
    REQUIRED_TARGETS = 1

    def setTargetList(self) -> None:
        managerEffect = self.invoker.getStatusEffectOfId(SEE.EFFECT_MANAGER_FIRESTARTER)
        if not managerEffect:
            return

        # If Firestarter is alone, or if 2 or more of his backburned ads
        # were killed, give him +5 damage and +8% damage reduction.
        aliveSuits = self.getAliveSuits()
        conditional_firesAlone = len(aliveSuits) == 1
        conditional_deadFodders = len(managerEffect.deadSuits) >= 2

        if conditional_firesAlone or conditional_deadFodders:
            self.targets = [self.invoker]
            self.extraArgs = [TTLocalizer.HP_TEXT_PYROMANIAC, int(conditional_firesAlone)]
            managerEffect.handlePyromaniac()


"""
Chainsaw Consultant
"""
# region Chainsaw Consultant


@AttackClassAI(attackType=AttackEnum.SCABBARD)
class ScabbardAI(SuitHealAttackAI):

    def setTargetList(self) -> None:
        self.targets = self.getOtherSuits()


@AttackClassAI(attackType=AttackEnum.CHAIN_LINKED)
class ChainLinkedAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_CHAIN_LINKED

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        index = 4 - self.getAliveSuits().index(target)
        return super().handleStatusEffect(target, [index])
    
    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()


@AttackClassAI(attackType=AttackEnum.KICKBACK)
class KickBackAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_KICKBACK

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        super().handleStatusEffect(target, [self.extraArgs[0]])
        kickbackEffect = target.getStatusEffectOfId(self.STATUS_EFFECT)
        if kickbackEffect:
            kickbackEffect.setRounds(self.extraArgs[1])


@AttackClassAI(attackType=AttackEnum.AGGRANDIZE)
class AggrandizeAI(RemoveStatusEffectAttackAI):
    STATUS_EFFECT = SUIT_STATUS_EFFECTS_TO_REMOVE
    REQUIRED_TARGETS = 1

    def calculate(self) -> None:
        super().calculate()

        target = self.targets[0]  # type: DistributedSuitBaseAI

        overcharge = target.getStatusEffectOfId(SEE.EFFECT_OVERCHARGED)
        isOvercharged = overcharge and overcharge.active

        # If they aren't executive, make them one.
        if not target.isElite:
            target.isElite = True

            # And raise their level by 2.
            target.level += 2

        # Otherwise, just give them a level boost.
        else:
            target.level = min(target.level + 4, 25)

        # Recalculate their HP.
        hp = target.calculateHp()
        target.maxHp = hp
        target.hp = hp

        # Preserve overcharged.
        if isOvercharged:
            target.setMaxHp(math.ceil(target.maxHp * 1.5))

        # Give them the 'Aggrandize' effect to easily keep
        # track of the fact that they have indeed been Aggrandized.
        target.addStatusEffect(SEE.EFFECT_AGGRANDIZE)

        # Also give them manager benefits.
        target.addStatusEffect(SEE.EFFECT_MINIBOSS)

        self.extraArgs = [target.level]

    def setTargetList(self) -> None:
        if self.targets:
            return

        otherSuits = self.getOtherSuits()
        if not otherSuits:
            return
        
        # Prioritize picking suits that aren't exe, 
        # then sued suits, then everyone else who can be promoted.
        suitChoices = {}
        for suit in otherSuits:
            if suit.getStatusEffectOfId(SEE.EFFECT_SUIT_SUED):
                suitChoices[suit] = 10
            elif not suit.isElite:
                suitChoices[suit] = 6
            elif suit.level < 25:
                suitChoices[suit] = 1

        if suitChoices:
            self.targets = [random.choices(list(suitChoices), list(suitChoices.values()))[0]]


@AttackClassAI(attackType=AttackEnum.OFFBOARDING)
class OffboardingAI(SuitSingleAttackAI):
    REQUIRED_TARGETS = 2
    DAMAGE_MULT = 3

    def setTargetList(self) -> None:
        otherSuits = self.getOtherSuits()
        highestLevelSuit = sorted(otherSuits, key=lambda s: s.getActualLevel(), reverse=True)[0]
        retaliateTarget = self.extraArgs[0]
        # If no targets provided, pick the highest level cog
        if not self.targets and otherSuits:
            self.targets = [highestLevelSuit]
        # If not retaliating to a toon using a pink slip, pick a random toon
        if not retaliateTarget and self.getAliveToons():
            self.targets.extend(self.chooseRandomToon())
        # Otherwise insert the highest level cog to be used as ammo
        elif retaliateTarget:
            self.targets.insert(0, highestLevelSuit)

    def getDamage(self, target: BattleAvatar = None) -> int:
        if target.isSuit():
            return target.getHp()

        # The damage multiplier scales to the health percentage.
        return self.getTargetDamage(self.targets[0])

    def getTargetDamage(self, tgt: DistributedSuitBaseAI) -> int:
        # Clamp the health percentage between 10% and 120%.
        healthPercentage = min(max(tgt.getHealthPercentage(), 0.1), 1.2)
        return math.ceil(tgt.getActualLevel() * healthPercentage * self.DAMAGE_MULT)

    def applyDamageModifiers(self, target: BattleAvatar, attackDamage: int,
                             damaging: bool = True, invokerMods: bool = False,
                             targetMods: bool = True):
        """Overriden to set the default value for invokerMods to False."""
        return super().applyDamageModifiers(target, attackDamage, damaging, invokerMods, targetMods)

    def getLanded(self) -> bool:
        return True


@AttackClassAI(attackType=AttackEnum.LAYOFFS)
class LayoffsAI(OffboardingAI):
    DAMAGE_MULT = 4

    def setTargetList(self) -> None:
        aliveSuits = self.getOtherSuits()
        toons = self.getToons()
        if not toons or not aliveSuits:
            return

        # Choose the smallest number.
        targets = min(len(aliveSuits), len(toons))
        self.targets = toons[:targets] + aliveSuits[:targets]

    def getDamage(self, target: BattleAvatar = None) -> int:
        if target.isSuit():
            return target.getHp()

        # Get the associated target.
        tgt: DistributedSuitBaseAI = self.targets[self.targets.index(target) + len(self.targets) // 2]

        # The damage multiplier scales to the health percentage.
        return self.getTargetDamage(tgt)


@AttackClassAI(attackType=AttackEnum.CUT_THE_SLACK)
class CutTheSlackAI(GenericDamageAttackAI):
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'tauntIndex', 'coolSpecialBoy',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    # How high can a Suit be promoted to?
    MAX_LEVEL = 30

    STATUS_EFFECT = SUIT_STATUS_EFFECTS_TO_REMOVE

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.coolSpecialBoy: DistributedSuitBaseAI = None

    def cleanup(self) -> None:
        del self.coolSpecialBoy
        return super().cleanup()

    def calculate(self) -> None:
        if not self.targets:
            newLevel = min(self.coolSpecialBoy.getActualLevel() + 3, self.MAX_LEVEL)
        else:
            # Add all of the target's levels onto the cool special boy.
            addLevels = sum([suit.getActualLevel() for suit in self.targets])
            newLevel = min(self.coolSpecialBoy.getLevel() + addLevels, self.MAX_LEVEL)

        overcharge = self.coolSpecialBoy.getStatusEffectOfId(SEE.EFFECT_OVERCHARGED)
        isOvercharged = overcharge and overcharge.active

        # Set their new level without distributing it.
        attributes = SuitBattleGlobals.SuitAttributes[self.coolSpecialBoy.dna.name]
        self.coolSpecialBoy.level = newLevel - attributes['level'] - 1

        # Also make them an executive.
        self.coolSpecialBoy.isElite = True

        # And recalculate their HP.
        hp = self.coolSpecialBoy.calculateHp()
        self.coolSpecialBoy.maxHp = hp
        self.coolSpecialBoy.hp = hp
        
        # Give them manager benefits.
        self.coolSpecialBoy.addStatusEffect(SEE.EFFECT_MINIBOSS)

        # Also give them lure resistance.
        self.coolSpecialBoy.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE)

        # Remove any baddy effects.
        for effect in self.STATUS_EFFECT:
            self.coolSpecialBoy.removeStatusEffectOfId(effect)

        # Preserve overcharged.
        if isOvercharged:
            self.coolSpecialBoy.setMaxHp(math.ceil(self.coolSpecialBoy.maxHp * 1.5))

        # Send their doId as an extra argument.
        self.extraArgs = [self.coolSpecialBoy.doId, self.coolSpecialBoy.level]

        super().calculate()

        # Save the cool special boy on the manager effect.
        chainsawEffect = self.invoker.getStatusEffectOfId(SEE.EFFECT_MANAGER_CHAINSAW_CONSULTANT)
        if chainsawEffect and self.coolSpecialBoy not in chainsawEffect.cutTheSlack_targets:
            chainsawEffect.cutTheSlack_targets[self.coolSpecialBoy] = 0
    
    def setTargetList(self) -> None:
        aliveSuits = [
            suit for suit in self.getOtherSuits() 
            if suit.getActualLevel() < self.MAX_LEVEL
        ]

        if self.targets and aliveSuits:
            self.coolSpecialBoy = self.targets[0]
            self.targets = [suit for suit in aliveSuits if suit is not self.coolSpecialBoy]
        elif len(aliveSuits) > 1:
            self.targets = sorted(aliveSuits, key=lambda s: s.getActualLevel())
            self.coolSpecialBoy = self.targets.pop()
        elif aliveSuits:
            self.coolSpecialBoy = aliveSuits[0]
        
        # Don't process the attack if for some reason our cool special boy
        # is NOT present.
        if not self.coolSpecialBoy:
            self.REQUIRED_TARGETS = 1
            self.targets = []

    def getDamage(self, target: BattleAvatar = None) -> int:
        return target.getHp()


@AttackClassAI(attackType=AttackEnum.MARKED_WOOD)
class MarkedWoodAI(DamageInflictStatusAttackAI):
    STATUS_EFFECT = SEE.EFFECT_MARKED_WOOD
    REQUIRED_TARGETS = 1

    def calculate(self, ignoreModifiers: bool = True) -> None:
        super().calculate(ignoreModifiers)
    
    def getDamage(self, target: BattleAvatar=None) -> int:
        # Drop the target to up to 33% of their max health, doing at minimum 40 damage.
        return max(math.ceil(target.getHp() - (target.getMaxHp() * 0.33)), 40)


@AttackClassAI(attackType=AttackEnum.DEADWOOD)
class DeadwoodAI(EndBattleAttackAI):

    def calculate(self, ignoreModifiers: bool = True) -> None:
        super().calculate(ignoreModifiers)

        for target in self.targets:
            target.deadwood = True

    def getDamage(self, target: BattleAvatar = None) -> int:
        return target.getHp() - 1


@AttackClassAI(attackType=AttackEnum.THROTTLE)
class ThrottleAI(DamageInflictStatusAttackAI):
    STATUS_EFFECT = SEE.EFFECT_DAMAGE_TAKEN_UP

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        return super().handleStatusEffect(target, [1.25])

    def setTargetList(self) -> None:
        self.targets = self.getToons()

    def getDamage(self, target: BattleAvatar = None) -> int:
        targetHp = target.getMaxHp() if self.extraArgs[0] else target.getHp()
        return math.ceil(targetHp * 0.5)


@AttackClassAI(attackType=AttackEnum.SPARK_PLUG)
class SparkPlugAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_SPARK_PLUG
    REQUIRED_TARGETS = 1
    
    def setTargetList(self) -> None:
        toons = sorted(self.getToons(), key=lambda toon: toon.getHp())
        if toons:
            self.targets = [toons[-1]]


@AttackClassAI(attackType=AttackEnum.CHAINSAW_ENTER_DORMANT)
class ChainsawEnterDormantAI(RemoveVisualEffectFromSelfAttackAI):
    # Enter phase 2 cutscene attack
    VISUAL_EFFECT = VisualEffectEnum.CHAINSAW_OVERRIDE
    NEW_VISUAL_EFFECT = VisualEffectEnum.CHAINSAW_OVERRIDE_GLITCHED

    def handleVisualEffect(self, target: BattleAvatar, extraArgs: list=None) -> None:
        visuals = self.VISUAL_EFFECT
        if not isinstance(visuals, (list, tuple)):
            visuals = [visuals]

        newVisuals = self.NEW_VISUAL_EFFECT
        if not isinstance(newVisuals, (list, tuple)):
            newVisuals = [newVisuals]

        for visual in visuals:
            result = target.removeVisualEffectOfId(visual)
            if not result:
                self.notify.debug(f"Could not remove {visual} effect from {repr(target)}!")

        for newVisual in newVisuals:
            result = target.addVisualEffect(newVisual, extraArgs=extraArgs)
            if not result:
                self.notify.debug(f"Could not add {newVisual} effect to {repr(target)}!")


@AttackClassAI(attackType=AttackEnum.CHAINSAW_EXIT_DORMANT)
class ChainsawExitDormantAI(ChainsawEnterDormantAI):
    # Enter phase 3 cutscene attack
    VISUAL_EFFECT = VisualEffectEnum.CHAINSAW_OVERRIDE_GLITCHED
    NEW_VISUAL_EFFECT = VisualEffectEnum.CHAINSAW_OVERRIDE

# endregion
