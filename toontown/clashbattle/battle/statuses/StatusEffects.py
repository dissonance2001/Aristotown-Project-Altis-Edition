from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.clashbattle.battle.BattleAvatar import BattleAvatar

import math
import random
from enum import IntEnum
from typing import List, Optional

from direct.showbase.PythonUtil import clampScalar

from toontown.clashbattle.battle import PassiveAttributeDefs
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle import BattleGlobals
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.visuals.VisualEffectEnums import *
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from ..BattleGlobals import BattleOrderPriority
from ..BattleListenerObject import BattleListenerObject
from ..environmental.base.EnvironmentalEnum import RainmakerWeather, ENV_ENUM, EnvironmentalEnum
from toontown.instances import HighRollerGlobals
from toontown.instances.HighRollerGlobals import HighRollerGameEnum
from toontown.toon.GagInventoryBase import GagInventoryBase
from toontown.clashbattle.battle.statuses.StatusEffectsBase import *

from toontown.utils.AstronStruct import AstronStruct
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE, SUIT_STATUS_EFFECTS_TO_REMOVE, SUIT_STATUS_EFFECTS_TO_REDUCE

NORMAL = 0
OVERCLOCKED = 1

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# Helper Classes (not status effects) #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# Most of these classes are paired with event definitions that are intended to be inherited
# region

# Class to keep track of rounds.


class RoundTimer:
    def __init__(self):
        self.roundTimerCount = 0
        self.roundsPastSinceLastCycleCheck = []
        self.timerCallback = None

    def setTimerCallback(self, callback):
        """
        Whenever the round increments (on round start),
        run a callback.
        """
        self.timerCallback = callback

    def runTimerCallback(self):
        """
        Attempts to run a set callback.
        """
        if self.timerCallback:
            self.timerCallback()

    def incrementRoundTimer(self, amount):
        self.roundTimerCount = self.roundTimerCount + amount
        self.roundsPastSinceLastCycleCheck.append(self.roundTimerCount)
        self.runTimerCallback()

    def doRoundCycleCheck(self, divisor, remainders):
        for round in self.roundsPastSinceLastCycleCheck:
            if isinstance(remainders, tuple) or isinstance(remainders, list):
                matchFound = round % divisor in remainders
            else:
                matchFound = round % divisor == remainders
            if matchFound:
                return True
        return False

    def resetRoundsList(self):
        self.roundsPastSinceLastCycleCheck = []

    def resetTimer(self):
        self.roundTimerCount = 0
        self.roundsPastSinceLastCycleCheck = []

    def setRoundCount(self, roundCount):
        self.roundTimerCount = roundCount

    def getRoundCount(self):
        return self.roundTimerCount


# Class that contains multiple RoundTimer objects.
# Useful for keeping track of multiple, changing cooldowns, for example.
class MultiTimer:
    def __init__(self, numberOfTimers):
        self.roundTimers = []
        self.indexCallbacks = {}
        for i in range(numberOfTimers):
            self.roundTimers.append(RoundTimer())

    def setTimerCallbacks(self, callbackDict):
        """
        Sets a callback on the timer for a given index.
        Whenever the round timer increments (at the start of the round),
        the callback will be ran.
        :param callbackDict: {index: callback} dictionary.
        """
        for index, callback in callbackDict.items():
            self.roundTimers[index].setTimerCallback(callback)

    def incrementRoundTimer(self, index, amount):
        self.roundTimers[index].incrementRoundTimer(amount)

    def incrementRoundTimers(self, amount):
        for timer in self.roundTimers:
            timer.incrementRoundTimer(amount)

    def doRoundCycleCheck(self, index, divisor, remainders):
        return self.roundTimers[index].doRoundCycleCheck(divisor, remainders)

    def resetRounds(self):
        for timer in self.roundTimers:
            timer.resetRoundsList()

    def resetRoundsList(self, index):
        self.roundTimers[index].resetRoundsList()

    def resetTimer(self, index):
        self.roundTimers[index].resetTimer()

    def setRoundCount(self, index, roundCount):
        self.roundTimers[index].setRoundCount(roundCount)

    def getRoundCount(self, index):
        return self.roundTimers[index].roundTimerCount


# Class that listens to all damage dealt in a battle turn.
class DamageListener:
    """
    A DamageListener is a StatusEffect helper class that,
    when it inherits the DAMAGE_LISTENER definition,
    listens to all damage that is applied in battle to
    all avatars (suits and toons).
    """

    def __init__(self):
        self.damageDict = {}

    def getBattle(self):
        """
        Ideally, this method is overwritten by StatusEffectBase.
        """
        raise NotImplementedError

    def getBattleCalc(self):
        raise NotImplementedError

    def getSuitDamageTotal(self):
        """
        Gets the total damage that Suits have taken so far.
        """
        retValue = 0
        for s in self.getBattleCalc().suits:
            # activeSuits is a list of suit avs
            avId = s.getDoId()
            if avId in self.damageDict:
                retValue += self.damageDict[avId]
        return retValue

    def getToonDamageTotal(self):
        """
        Gets the total damage that Toons have taken so far.
        """
        retValue = 0
        for avId in self.getBattleCalc().toons:
            # activeToons is a list of toon avIds
            if avId in self.damageDict:
                retValue += self.damageDict[avId]
        return retValue

    def addDamage(self, av, damage):
        """
        Adds damage directly to an avatar.
        """
        avId = av.getDoId()
        if avId not in self.damageDict:
            self.damageDict[avId] = damage
        else:
            self.damageDict[avId] += damage

    def resetDamage(self):
        self.damageDict = {}


# Astron representation of a status effect.

class StatusEffectStruct(AstronStruct):

    def __init__(self, effectId, rounds, disabledRounds, extraArgs):
        self.effectId = effectId
        self.rounds = rounds
        self.disabledRounds = disabledRounds
        self.extraArgs = extraArgs

    def toStruct(self):
        return [self.effectId, self.rounds, self.disabledRounds, self.extraArgs]

# endregion

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# General Status Effect Classes #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# region

# General attack effectiveness effect
class AttackEffectivenessStatusEffect(StatusEffectBase):
    # Higher will apply first
    SortPriority = 0

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.multiplier = extraArgs[0]
        self.fields = ['multiplier']

    def combine(self, otherEffect):
        # When combining, take the highest rounds
        otherMult = otherEffect.getMultiplier()
        otherRounds = otherEffect.getRounds()

        # If we're a buff, take the highest multiplier.
        # If we're a debuff, take the lowest multiplier.
        effectType = SEG.StatusEffectId2Type.get(self.effectId, SEG.BUFF)
        if effectType == SEG.BUFF and otherMult > self.getMultiplier():
            self.setMultiplier(otherMult)
        elif effectType == SEG.DEBUFF and otherMult < self.getMultiplier():
            self.setMultiplier(otherMult)

        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        # Handle custom requisites for changing attack damage here in subclasses.
        if not self.isDisabled():
            attackDamage *= self.getMultiplier()
        return attackDamage

    def setMultiplier(self, mult):
        self.multiplier = mult

    def getMultiplier(self):
        return self.multiplier


# Used for toons accuracy up
class AttackAccuracyStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.accuracyChange = extraArgs[0]
        # Override is -1 for no override, a number for any other forced accuracy amount. 0-100
        self.override = extraArgs[1]
        self.fields = ['accuracyChange', 'override']

    def handleAttackAccuracy(self, attackTrack: int, attackAccuracy):
        # Handle custom requisites for changing attack accuracy here in subclasses.
        # Override is used for Toons accuracy up

        if self.isDisabled():
            return attackAccuracy, -1

        # Add it if its an int
        # Else, multiply it (float)
        if isinstance(self.accuracyChange, int):
            attackAccuracy += self.accuracyChange
        else:
            attackAccuracy *= self.accuracyChange
        return attackAccuracy, self.override

    def combine(self, otherEffect):
        # Handle combinations with other effects
        otherRounds = otherEffect.getRounds()
        otherAccuracyChange = otherEffect.getAccuracyChange()

        if otherRounds > self.rounds or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)

        # Update our accuracy change if the other one is a higher accuracy change than us.
        # (More effective on negative side)
        if otherAccuracyChange > self.accuracyChange:
            self.setAccuracyChange(otherAccuracyChange)

    def getAccuracyChange(self):
        return self.accuracyChange

    def setAccuracyChange(self, accuracyChange):
        self.accuracyChange = accuracyChange

    def getOverride(self):
        return self.override


class HiddenAttackAccuracyStatusEffect(AttackAccuracyStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False


# If this flag is on an effect, attacks against the target
# will break the accuracy cap.
class IncomingAttacksBreakAccuracyCap:
    def canBreakCap(self, attack) -> bool:
        attackFilter = self.accCap_getAttackFilter()
        if attackFilter is None:
            return True
        return attack.attackType in attackFilter

    def accCap_getAttackFilter(self) -> Optional[List[AttackEnum]]:
        # Get a list of attacks that are acceptable to break the cap.
        return None


# Likewise, this affects the accuracy of outgoing attacks.
class OutgoingAttacksBreakAccuracyCap:
    def canBreakCap(self, attack) -> bool:
        attackFilter = self.accCap_getAttackFilter()
        if attackFilter is None:
            return True
        return attack.attackType in attackFilter

    def accCap_getAttackFilter(self) -> Optional[List[AttackEnum]]:
        # Get a list of attacks that are acceptable to break the cap.
        return None


class ToonJustMissedStatusEffect(AttackAccuracyStatusEffect, OutgoingAttacksBreakAccuracyCap):
    """
    When a Toon just misses, they get a special recovery effect.
    """
    pass


class SuitJustDodgedSoakStatusEffect(StatusEffectBase):
    """
    When a Suit dodges a Soak status effect (dodges or is adjacent to a suit that dodges a Squirt),
    we set a flag that tells Zap gags not to be consumed.
    """
    pass


# Additive damage boost.
class AdditiveDamageBoostStatusEffect(AttackEffectivenessStatusEffect):
    def combine(self, otherEffect):
        """When combining, combine multipliers."""
        # Combine multiplier.
        self.setMultiplier(self.getMultiplier() + otherEffect.getMultiplier())

        # When combining, take the highest rounds.
        otherRounds = otherEffect.getRounds()
        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        return attackDamage + self.getMultiplier()


class AdditiveDamageBoostNoToonup(AdditiveDamageBoostStatusEffect):
    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        if attackTrack == AttackEnum.TOON_HEAL:
            return attackDamage
        return super().handleAttackDamage(attackTrack=attackTrack, attackDamage=attackDamage, target=target)


# When damage boosts are combined with this, it will add them on to the existing value in a multiplicative fashion.
class MultiplicativeDamageBoostStatusEffect(AttackEffectivenessStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.rounding = extraArgs[1]
        self.fields += ['rounding']

    def combine(self, otherEffect):
        # When combining, take the highest rounds.
        otherMult = otherEffect.getMultiplier()
        otherRounds = otherEffect.getRounds()

        # Multiply the damage multipliers together.
        self.setMultiplier(round(otherMult * self.getMultiplier(), self.rounding))

        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)


class HealthBonusEffect(StatusEffectBase):
    """
    Adds a health bonus to the given cog.
    This currently has no support for a limited number of rounds. Cry about it.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.boostAmount = self.extraArgs[0]
        from toontown.clashsuit.suit.SuitBase import SuitBase
        if self.isAi() and isinstance(self.av, SuitBase):
            self.av.b_setMaxHp(self.av.getMaxHp() + self.boostAmount)


# Gives the suit the given amount of lure resistance for a limited time
class LureResistanceStatusEffect(StatusEffectBase):
    VisualSortOrder = 45

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.amount = extraArgs[0]
        self.fields = ['amount']
        self.adjustCurrentLureRounds(self.getAmount())

    def setAmount(self, amount):
        self.amount = amount

    def getAmount(self):
        return self.amount

    def handleLureResistance(self, suit, lureResistance):
        # Override in subclasses if needed.
        return min(lureResistance, self.getAmount())

    def adjustCurrentLureRounds(self, amount, adjust=False):
        # AI Only
        if self.avProfile.battleListener:
            luredEffect = self.avProfile.getStatusEffectOfType(LureStatusEffect)
            if luredEffect is not None and luredEffect.getRounds() > amount:
                if amount == -1:
                    # We have -1, which means full lure immunity, so we can just delete the lure effect
                    luredEffect.delete()
                else:
                    luredEffect.setRounds(amount, adjust)


class PinkSlipImmunity:
    """
    Complete immunity to just fires, without a flag to enable/disable it.
    """
    pass


class CeaseDesistImmunity:
    """
    Complete immunity to just sues, without a flag to enable/disable it.
    """
    pass


class ToonRewardImmunityStatusEffect(StatusEffectBase, PinkSlipImmunity, CeaseDesistImmunity):
    pass


class AttackTargetGhostwriter:
    """
    This subclass helps to create status effects that overwrite various attack targets
    for certain attack classes. In particular, this helps to create various "agro"
    status effects.
    """

    def determineNewTargets(self, attack) -> Optional[list]:
        """
        Determines the new targets of this attack.
        If there are no overrides, returns None.
        Otherwise, return a list of valid battle avatars.
        """
        return None


# Gives the suit immunity to fires and sues
class MinibossResistancesStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.minibossImmunitiesActive = True
        self.fields.extend(['minibossImmunitiesActive'])


# Currently used for Disruptive Advertisement by DOPA
class HitAvatarStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.avatarHit = False
        self.extraAttackType = extraArgs[0]
        self.fields = ['extraAttackType']

    def roundsRanOut(self):
        if not self.hasAvatarBeenHit():
            self.getBattleCalc().createAndInsertAttack(
                self.extraAttackType,
                {"invoker": self.getAv(), "unlure": True},
                {"mode": "end"}
            )
        super().roundsRanOut()

    def setAvatarHit(self, flag):
        self.avatarHit = flag
        if self.avatarHit:
            self.handleAvatarHasBeenHit()

    def handleAvatarHasBeenHit(self):
        return

    def hasAvatarBeenHit(self):
        return self.avatarHit


class DisruptiveAdvertisementEffect(HitAvatarStatusEffect):
    def handleAvatarHasBeenHit(self):
        self.createGeneralAttack(
            AttackEnum.REMOVE_VISUAL_EFFECT,
            [VisualEffectEnum.DISRUPTIVE_ADVERTISEMENT.value],
            [self.getAv()]
        )


# Currently used for Multi Level Marketing by DOPA, and DOPR
class ExtraSuitAttacksStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.numExtraAttacks = extraArgs[0]
        self.extraAttackType = extraArgs[1]
        self.unlure = extraArgs[2]
        self.fields = ['numExtraAttacks', 'extraAttackType', 'unlure']
        self.attacksCompletedThisTurn = 0
        self.inheritedEventDefinitions.append(SEE.EFFECT_GENERIC_EXTRA_ATTACKS)

    def getExtraAttacks(self):
        return self.numExtraAttacks

    def setExtraAttacks(self, num):
        self.numExtraAttacks = num

    def setAttacksCompleted(self, num):
        self.attacksCompletedThisTurn = num

    def setUnlure(self, unlure):
        self.unlure = unlure

    def combine(self, otherEffect):
        self.setExtraAttacks(self.getExtraAttacks() + 1)

    def addAllExtraAttacks(self):
        for _ in range(self.getExtraAttacks() - self.attacksCompletedThisTurn):
            if self.extraAttackType != -1:
                self.getBattleCalc().createAndInsertAttack(
                    self.extraAttackType,
                    {"unlure": self.unlure, "invoker": self.getAv()},
                )
                self.attacksCompletedThisTurn += 1
            else:
                suitEffect = self.av.getStatusEffectOfType(CogStatusEffect)
                if suitEffect:
                    suitEffect.generateRandomSuitAttack(unlure=self.unlure)


# Status effect for making the avatar entirely immune to targeting.
# Currently only works for suit on toon attacks.
class UntouchableStatusEffect(StatusEffectBase):
    @staticmethod
    def canBeTrapped():
        """
        Determines whether a suit with this status effect should be able to be affected by trap.
        Overwrite this method in an inherited effect to allow it to be trapped.
        """
        return False


# This status effect doesn't really have a function, it just exists to let the battle know that the toon has
# their unites disabled, and for GUI display.
class UnitesDisabledStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = False
        self.hasDisabledUnites = True
        self.visualEffectEnums = [VisualEffectEnum.UNITE_COOLDOWN]

    def roundsRanOut(self):
        # Since this status effect decrements its natural timer at an odd time,
        # (Visual Effects look at the start of the movie to clean up,
        # but this status effect doesn't decrement until after the movie ends),
        # we'll have to ensure that the unite cooldown visual effect
        # gets cleaned up at the correct time.
        self.getAv().removeVisualEffectOfId(VisualEffectEnum.UNITE_COOLDOWN)

        # Ok, we can clean up casually now.
        super().roundsRanOut()


class RewardCooldownStatusEffect(UnitesDisabledStatusEffect):
    pass


# Used for Lure, prestige lure, sue, etc.
class CantAttackStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True

    def combine(self, otherEffect):
        otherRounds = otherEffect.getRounds()
        if otherRounds > self.rounds or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)


class SueStatusEffect(CantAttackStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE]
        self.visualEffectEnums = [VisualEffectEnum.SUED]

    def incrementRounds(self):
        self.setRounds(min(self.getRounds() + 1, BattleGlobals.NumRoundsCeaseDesistCap))


# Causes the avatar to take a modified amount of damage when attacked.
class AvatarTakeModifiedDamageStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.multiplier = extraArgs[0]
        self.fields = ['multiplier']

    def combine(self, otherEffect):
        # When combining, take the highest multiplier and highest rounds
        otherMult = otherEffect.getMultiplier()
        otherRounds = otherEffect.getRounds()
        if otherMult > self.getMultiplier():
            self.setMultiplier(otherMult)
        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Handle custom requisites for changing attack damage here in subclasses.
        attackDamage *= self.getMultiplier()
        return attackDamage

    def setMultiplier(self, mult):
        self.multiplier = mult

    def getMultiplier(self):
        return self.multiplier

    def incMultiplier(self, inc):
        self.setMultiplier(self.getMultiplier() + inc)


class AvatarTakeFlattenedDamageStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    """
    Status effect for modifying the damage an avatar takes by a flat value. Can't go below 0.
    """
    def combine(self, otherEffect):
        """When combining, combine multipliers."""
        # Combine multiplier.
        self.setMultiplier(self.getMultiplier() + otherEffect.getMultiplier())

        # When combining, take the highest rounds.
        otherRounds = otherEffect.getRounds()
        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def handleAttackDamageTaken(self, attackDamage: int, attackTrack: int, invoker):
        attackDamage += self.getMultiplier()
        return max(0, attackDamage)


# Used for Lure, prestige lure.
class LureStatusEffect(CantAttackStatusEffect, AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.prestige = extraArgs[0]
        self.knockback = extraArgs[1]
        self.accuracy = extraArgs[2]
        self.fields = ['prestige', 'knockback', 'accuracy']
        self.used = False
        self.fresh = True
        self.invokers = {}
        self.uniqueId = -1
        self.visualEffectEnums = [VisualEffectEnum.LURED]

    def handleAttackAccuracy(self, attackAccuracy, accuracyBonus, randomAccuracy):
        if BattleGlobals.WantLureDecay:
            ourAccuracy = self.getAccuracy()
            if ourAccuracy >= 100:  # Return true since attack is supposed to be guaranteed to hit.
                return True
            # Take the maximum between the base accuracy and the lure decay.
            else:
                # Lure decay should never disadvantage players over attacking unlured Cogs.
                lureDecay = max(attackAccuracy, ourAccuracy)
                # This allows you to stun for the lure decay accuracy
                # (i.e. if dry zap accuracy with one stun would normally be 50,
                # but lure decay accuracy is at 70, you would be able to stun for the 70 accuracy and
                # end with 90 accuracy using one stun).
                if lureDecay < BattleGlobals.MaxToonAcc and accuracyBonus > 0:
                    lureDecay += accuracyBonus
                    lureDecay = min(lureDecay, BattleGlobals.MaxToonAcc)

                return randomAccuracy <= lureDecay
        else:
            return True

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        if attackTrack in (AttackEnum.TOON_THROW, AttackEnum.TOON_SQUIRT):
            attackDamage += self.getKnockback()
        return attackDamage

    def decrement(self, amount):
        for _ in range(amount):
            self.setAccuracy(self.getAccuracy() - 5)
        super().decrement(amount)

    def delete(self):
        if self.cleanedUp:
            return
        del self.invokers
        super().delete()

    def getPrestige(self):
        return self.prestige

    def setPrestige(self, prestige):
        self.prestige = prestige
        self.setAccuracy(BattleGlobals.LureAccuracy)

    def combine(self, otherEffect):
        # Lure can only reach this point if its the round of it being created
        otherRounds = otherEffect.getRounds()
        # If the other effect's rounds are higher, replace ours with them
        # Or if the other effect has infinite rounds, make our rounds infinite.
        if otherRounds > self.getRounds() or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)

        # If we're not prestige and the other effect is, then set us to prestige.
        if not self.prestige and otherEffect.prestige:
            self.setPrestige(otherEffect.prestige)

        if otherEffect.getKnockback() > self.getKnockback():
            self.setKnockback(otherEffect.getKnockback())

    def getKnockback(self):
        return self.knockback

    def setKnockback(self, knockback):
        self.knockback = knockback

    def getAccuracy(self):
        return self.accuracy

    def setAccuracy(self, accuracy):
        self.accuracy = accuracy

    def getUsed(self):
        return self.used

    def setUsed(self, used):
        self.used = used

    def getFresh(self) -> bool:
        return self.fresh

    def setFresh(self, fresh: bool) -> None:
        self.fresh = fresh

    def getUniqueId(self) -> int:
        return self.uniqueId

    def setUniqueId(self, uniqueId: int) -> None:
        self.uniqueId = uniqueId

    def addInvoker(self, toon, attack) -> None:
        self.invokers[toon.doId] = attack

    def removeInvoker(self, toon) -> None:
        toonId = toon.doId
        if toonId in self.invokers:
            del self.invokers[toonId]


# Used for Lure, prestige lure.
class LureKnockbackModifierStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.lureKbBonus = extraArgs[0]
        self.fields = ['lureKbBonus']

    def setlureKbBonus(self, lureKbBonus):
        self.lureKbBonus = lureKbBonus

    def getlureKbBonus(self):
        return self.lureKbBonus

    def handleLureKb(self, knockback):
        # Handle overrides here if needed.
        knockback *= self.lureKbBonus
        return knockback


class SuitCannotDodgeStatusEffect(StatusEffectBase):
    def isDodgeDisabled(self, attack) -> bool:
        return True


# Causes the avatar to be more or less likely to dodge attacks.
class SuitDefenseModifierStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.amount = extraArgs[0]
        self.fields = ['amount']

    def getAmount(self):
        return self.amount

    def setAmount(self, amount):
        self.amount = amount

    def combine(self, otherEffect):
        # When combining, take the highest rounds
        otherAmount = otherEffect.getAmount()
        otherRounds = otherEffect.getRounds()

        # Take the highest amount.
        if otherAmount > self.getAmount():
            self.setAmount(otherAmount)

        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def handleSuitDefense(self, suit, suitDefense, attack):
        # Override in subclasses if needed.
        return suitDefense + self.amount


# Modifies the aggro value placed on the given avatar.
class AggroModifierStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.amount = extraArgs[0]
        self.multiplicative = extraArgs[1]
        self.relative = extraArgs[2]
        self.fields = ['amount', 'multiplicative', 'relative']

    def getAmount(self):
        return self.amount

    def handleAggroModifier(self, aggroDict: dict):
        # Override in subclasses if needed.

        # If we want a relative value, use the highest (or lowest) aggro value as a basis
        # to ensure the desired effect.
        if self.relative:
            aggro = (max if self.amount > 0 else min)(aggroDict.values())
        else:
            aggro = aggroDict.get(self.getAv().doId, 1)

        return aggro * self.amount if self.multiplicative else aggro + self.amount


# Marker for a Status Effect allowing Zap to always hit.
class ZapWillHit:
    pass


# Marker for a Status Effect allowing a Zap to jump onto or off a Suit.
class ZapCanJump:
    pass


# Marker for Zap to deal bonus damage to a Suit.
class ZapDealsBoostedDamage:
    pass


# Used for Soak.
class SoakStatusEffect(SuitDefenseModifierStatusEffect, ZapCanJump, ZapDealsBoostedDamage, ZapWillHit):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.visualEffectEnums = [VisualEffectEnum.SOAKED]
        self.combines = True

    def combine(self, otherEffect):
        otherRounds = otherEffect.getRounds()
        # If the other effect's rounds are higher, replace ours with them
        # Or if the other effect's rounds are infinite, make ours infinite
        if otherRounds > self.getRounds() or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)


# Drenched, the prestige version of Soaked.
class DrenchStatusEffect(SoakStatusEffect, MultiplicativeDamageBoostStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.multiplier = extraArgs[1]
        self.rounding = extraArgs[2]
        self.visualEffectEnums = [VisualEffectEnum.DRENCHED]
        self.fields += ['multiplier', 'rounding']
        self.targetedByZap = False

    def decrement(self, amount, isZap: bool=False) -> bool:
        # Disallow zap from decrementing it more than once.
        if isZap and self.targetedByZap:
            return False

        self.targetedByZap = isZap
        super().decrement(amount)
        return True


# Multiplicative damage modifier on incoming combo damage.
class ComboDamageModifierStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.comboMultiplier = extraArgs[0]
        self.fields += ['comboMultiplier']

    def combine(self, otherEffect):
        # When combining, combine the multipliers.
        self.setComboMultiplier(self.getComboMultiplier() * otherEffect.getComboMultiplier())

        # Take the higher rounds.
        otherRounds = otherEffect.getRounds()
        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Handle custom requisites for changing attack damage here in subclasses.
        attackDamage *= self.getComboMultiplier()
        return attackDamage

    def setComboMultiplier(self, mult):
        self.comboMultiplier = mult

    def getComboMultiplier(self):
        return self.comboMultiplier

    def incMultiplier(self, inc):
        self.setComboMultiplier(self.getComboMultiplier() + inc)


# Multiplicative damage modifier on incoming knockback damage.
class KnockbackDamageModifierStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.kbMultiplier = extraArgs[0]
        self.fields += ['kbMultiplier']

    def combine(self, otherEffect):
        # When combining, combine the multipliers.
        self.setKbMultiplier(self.getKbMultiplier() * otherEffect.getKbMultiplier())

        # Take the higher rounds.
        otherRounds = otherEffect.getRounds()
        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Handle custom requisites for changing attack damage here in subclasses.
        attackDamage *= self.getKbMultiplier()
        return attackDamage

    def setKbMultiplier(self, mult):
        self.comboMultiplier = mult

    def getKbMultiplier(self):
        return self.comboMultiplier

    def incMultiplier(self, inc):
        self.setKbMultiplier(self.getKbMultiplier() + inc)


# Used for Frozen, a sidegrade to Soak in cold environments. Zap does not jump on or to it.
class FrozenStatusEffect(SuitDefenseModifierStatusEffect, ZapDealsBoostedDamage, ZapWillHit, AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        SuitDefenseModifierStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        # This is only necessary on the AI.
        if self.isAi():
            self.rounds = extraArgs[1]
        self.visualEffectEnums = [VisualEffectEnum.FROZEN]

    def combine(self, otherEffect):
        otherRounds = otherEffect.getRounds()
        if otherRounds > self.getRounds() or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        if attackTrack == AttackEnum.TOON_ZAP:
            attackDamage *= 2/3  # Zap deals 2/3rds the damage.
        attackDamage *= 0.9  # The avatar also takes 10% reduced damage.
        return attackDamage


# Used for Throw.
class MarkedForLaughStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE]
        self.multiplier = extraArgs[0]
        self.level = extraArgs[1]
        self.fields = ['multiplier', 'level']

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Only modify damage for non-Throw gags.
        if attackTrack != AttackEnum.TOON_THROW:
            attackDamage *= self.getMultiplier()
        return attackDamage


# Used to display that a Suit is trapped by a trap gag.
class TrappedStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = False
        self.trapLevel = extraArgs[0]
        self.trapDamage = extraArgs[1]
        self.fields = ['trapLevel', 'trapDamage']

        self.invokerId = 0
        self.used = 0

    def setTrapLevel(self, level):
        self.trapLevel = level

    def getTrapLevel(self):
        return self.trapLevel

    def setTrapDamage(self, damage):
        self.trapDamage = damage

    def getTrapDamage(self):
        return self.trapDamage

    def setInvoker(self, toon) -> None:
        self.invokerId = toon.doId

    def getInvoker(self):
        return simbase.air.getDo(self.invokerId)

    def setInvokerId(self, toonId: int) -> None:
        self.invokerId = toonId

    def getInvokerId(self) -> int:
        return self.invokerId

    def setUsed(self, used: int) -> None:
        self.used = used

    def getUsed(self) -> int:
        return self.used


# Status effect to modify applied soak rounds.
class SoakRoundsModifierStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.amount = extraArgs[0]
        self.fields = ['amount']

    def setAmount(self, amount):
        self.amount = amount

    def getAmount(self):
        return self.amount

    def combine(self, otherEffect):
        # When combining, take the highest rounds
        otherAmount = otherEffect.getAmount()
        otherRounds = otherEffect.getRounds()

        # Take the highest amount.
        if otherAmount > self.getAmount():
            self.setAmount(otherAmount)

        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def handleSoakRounds(self, rounds):
        rounds += self.amount
        return rounds


# General toon damage up status effect.
class ToonDamageBoostStatusEffect(LureKnockbackModifierStatusEffect, AttackEffectivenessStatusEffect):
    SortPriority = 100

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        AttackEffectivenessStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.gagTrack = extraArgs[1]
        self.uses = extraArgs[2]
        # Tracks if an effect higher than us did something this turn
        self.higherEffectActivated = False
        self.maxUses = self.uses
        self.fields += ['gagTrack', 'uses']
        self.inheritedEventDefinitions += [SEE.EFFECT_BASE]
        self.visualEffectEnums = [VisualEffectEnum.TOON_BOOST]

    def setGagTrack(self, gagTrack):
        self.gagTrack = gagTrack

    def getGagTrack(self):
        return self.gagTrack

    def setUses(self, uses: int) -> None:
        self.uses = uses
        self.maxUses = max(uses, self.uses)

    def getUses(self) -> int:
        return self.uses

    @property
    def otherEffects(self):
        otherBoostEffects = self.av.getStatusEffectsOfId(self.effectId)
        if self in otherBoostEffects:
            otherBoostEffects.remove(self)

        return otherBoostEffects

    @property
    def otherWeakerEffects(self):
        return [effect for effect in self.otherEffects if effect.getGagTrack() == self.getGagTrack() and effect.getMultiplier() < self.getMultiplier()]

    def isAnotherEffectBetterThanUs(self):
        for effect in self.otherEffects:
            # Oh no, this effect is our track and its better than us. Sadge. :(
            if effect.getGagTrack() == self.getGagTrack() and effect.getMultiplier() > self.getMultiplier():
                return True

        return False

    def isVisible(self):
        return not self.isAnotherEffectBetterThanUs()

    def combine(self, otherEffect):
        otherUses = otherEffect.getUses()

        # Take the highest uses capped to initial uses.
        if otherUses > self.getUses():
            self.setUses(otherUses)

    # Only combine if we have the same gag track and multiplier.
    def wantCombine(self, otherEffect):
        return self.getGagTrack() == otherEffect.getGagTrack() and self.getMultiplier() == otherEffect.getMultiplier()

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        # Another boost of this track is better than us, we should do nothing here
        if self.isAnotherEffectBetterThanUs() or self.isDisabled():
            self.higherEffectActivated = True
            return attackDamage

        # Handle lure differently, as it gets boosted knockback damage.
        if self.gagTrack in (attackTrack, -1) and attackTrack != AttackEnum.TOON_LURE:
            attackDamage += self.getMultiplier()
        return attackDamage

    def handleLureKb(self, knockback):
        # Another boost of this track is better than us, we should do nothing here
        if self.isAnotherEffectBetterThanUs() or self.isDisabled():
            self.higherEffectActivated = True
            return knockback

        # Add the multiplier to lure knockback.
        if self.gagTrack in (AttackEnum.TOON_LURE, -1):
            knockback += self.getMultiplier()
        return knockback

    def checkSendEvent(self, attack) -> None:
        from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
        attack: ToonAttackAI = attack  # woes of a shared functionality file
        # Ignore attacks not from our avatar and attacks which don't match
        # our gag track.
        if attack.invoker != self.getAv() or (self.getGagTrack() != -1 and attack.attackType != self.getGagTrack()):
            return

        # Another boost of this track is better than us, which means we did nothing.
        # We should not decrement.

        if self.isAnotherEffectBetterThanUs() or self.isDisabled() or self.higherEffectActivated:
            self.higherEffectActivated = False
            return

        # Excluding toonup, ignore attacks that didn't actually hit, since they
        # didn't actually get the bonus.
        if attack.attackType != AttackEnum.TOON_HEAL and not attack.landed:
            return

        # Otherwise, it's an attack of the type we want from the matching invoker.
        # Decrement the uses.
        self.uses -= 1

        # Delete the status effect if we're out of uses.
        if self.uses == 0:
            self.roundsRanOut()


class MultiplicativeToonDamageBoostStatusEffect(ToonDamageBoostStatusEffect):
    SortPriority = 10

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        # Handle lure differently, as it gets boosted knockback damage.
        if self.gagTrack in (attackTrack, -1) and attackTrack != AttackEnum.TOON_LURE and not self.isDisabled():
            attackDamage *= self.getMultiplier()
        return attackDamage

    def handleLureKb(self, knockback):
        # Add the multiplier to lure knockback.
        if self.gagTrack in (AttackEnum.TOON_LURE, -1) and not self.isDisabled():
            knockback *= self.getMultiplier()
        return knockback


# Sound Damage Boost passive.
class EncoreStatusEffect(MultiplicativeToonDamageBoostStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.combines = False

    def checkSendEvent(self, attack) -> None:
        return  # encore is round based


# Sound spam debuff.
class WindedStatusEffect(AttackEffectivenessStatusEffect):
    SortPriority = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.combines = False

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        # Winded only affects sound.
        if attackTrack != AttackEnum.TOON_SOUND:
            return attackDamage
        return super().handleAttackDamage(attackTrack, attackDamage, target)


# Forces targeting one toon, unlures self at end of round.
class HivemindEffect(StatusEffectBase):
    def retargetSuitAttacks(self) -> None:
        # Get a list of valid toons.
        toons = self.getBattleCalc().getAliveToons()

        # Get the toons who are bewitched.
        bewitchedToons = [toon for toon in toons if toon.getStatusEffectOfId(SEE.EFFECT_BEWITCHMENT)]

        # Preset the target list if marked wood was previously used.
        targets = None
        if bewitchedToons:
            targets = [bewitchedToons[0]]
        elif toons:
            targets = [toons[0]]

        # Apply the override for the suit's random attack.
        if targets:
            for attack in self.getBattleCalc().attackOrder.getAttacksOfInvoker(self.av):
                # Only adjust targets if the attack hasn't calculated yet
                if attack.attackIndex == -1:
                    attack.targets = targets
                    attack.unlure = True


# The Witch Hunter takes less damage, increasing with Mob Mentalities and decreasing with Cog destruction.
class WillOfThePeopleStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.decreaseAmount = 0.05
        self.increaseAmount = 0.10

    def handleSuitDied(self):
        self.multiplier = min(1.0, self.multiplier + self.decreaseAmount)
        # Hide the effect if it's not reducing any damage.
        if self.multiplier == 1.0:
            self.wantShow = False

    def handleMobMentality(self):
        self.multiplier = max(0, self.multiplier - self.increaseAmount)
        self.wantShow = True


# Causes all gags besides toonup to miss.
class LunchBreakStatusEffect(AttackAccuracyStatusEffect):
    def handleAttackAccuracy(self, attackTrack: int, attackAccuracy):
        # Handle custom requisites for changing attack accuracy here in subclasses.
        # Override is used for Toons accuracy up

        # Override accuracy to be 0 for non-heal tracks.
        if attackTrack != AttackEnum.TOON_HEAL:
            return attackAccuracy, self.override

        return attackAccuracy, -1


class LunchBreakMslackerEffect(CantAttackStatusEffect, UntouchableStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = True

    def isVisible(self):
        # The client will still receive this status effect,
        # it just won't show on the status effect panel.
        return False


# Suit takes less damage from the first gag track that hits them each round.
class FocusedDefenseStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.damageTakenThisRound = False
        self.reduceDamage = True

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        if not self.reduceDamage:
            return attackDamage
        return super().handleAttackDamageTaken(attackDamage, attackTrack, invoker)

    def handleBeginRound(self):
        # Reset the tracking properties to default.
        self.damageTakenThisRound = False
        self.reduceDamage = True

    def checkForDamageDealt(self, suit):
        # If damage is dealt to us, make note of that.
        if suit == self.getAv():
            self.damageTakenThisRound = True

    def handleTrackOver(self):
        # When a track ends, if we've taken damage this round, then stop reducing damage for the rest of the round.
        if self.damageTakenThisRound:
            self.reduceDamage = False


class WorkerManagementStatusEffect(StatusEffectBase):
    EFFECTS_TO_REMOVE = SUIT_STATUS_EFFECTS_TO_REMOVE

    def cleanseNearbySuits(self):
        """Cleanses suits next to this one of certain effects at the end of the round."""
        for suit in self.getBattleCalc().findNearbySuits(self.getAv()):
            lureEffect = bool(suit.getStatusEffectOfId(SEE.EFFECT_SUIT_LURED))
            for effectId in self.EFFECTS_TO_REMOVE:
                suit.removeStatusEffectOfId(effectId)

            # Give the lured suits an attack.
            if lureEffect:
                from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import createAttack
                attack = createAttack(suit.getRandomAttack(), invoker=suit)

                self.getBattleCalc().insertAttack(attack, respectPreviousAdditions=True)


class UnionBustStatusEffect(StatusEffectBase):
    BannedSuits = ['msfore', 'mslacker']

    def roundsRanOut(self):
        self.prepareUnionBust()
        super().roundsRanOut()

    @property
    def otherSuits(self):
        return [suit for suit in self.battleCalc.getAliveCogs() if suit.dna.name not in self.BannedSuits]

    def prepareUnionBust(self):
        if len(self.otherSuits) > 0:
            self.createAttack(AttackEnum.UNION_BUST, insertMethod='end', unlure=True)


class EndBattleOnDeathEffect(StatusEffectBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = False

    def attemptEndFight(self):
        # Remove pending suits from battle
        from toontown.clashbattle.battle.BattleGlobals import BattleStateEnum
        battle = self.getBattle()
        suitsToRemove = battle.pendingSuits + battle.joiningSuits + battle.joiningNotPendingSuits
        for suit in suitsToRemove:
            suit.setBattleState(BattleStateEnum.INACTIVE)
        # Instakill all alive suits
        aliveSuits = [suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]
        self.createGeneralAttack(
            AttackEnum.AVATAR_INSTAKILL,
            targetList=aliveSuits,
            insertKwargs={"respectPreviousAdditions": False}
        )

        # If we're part of an instance, clear the reserve suits.
        if hasattr(battle, 'instance'):
            for suit in battle.instance.reserveSuits:
                if isinstance(suit, tuple):
                    suit[0].requestDelete()
                else:
                    suit.requestDelete()
            battle.instance.reserveSuits = []


class SuitPreventDeathStatusEffect(StatusEffectBase):

    def canPreventDeath(self):
        return True

    def onDeathPrevented(self):
        pass


# A combined class for Attack Effectiveness and Avatar Take Modified Damage effects.
class AttackIOModificationStatusEffect(AttackEffectivenessStatusEffect, AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.attackMultiplier = extraArgs[0]
        self.defenseMultiplier = extraArgs[1]
        self.fields = ['attackMultiplier', 'defenseMultiplier']

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        # Handle custom requisites for changing attack damage here in subclasses.
        attackDamage *= self.attackMultiplier
        return attackDamage

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Handle custom requisites for changing attack damage here in subclasses.
        attackDamage *= self.defenseMultiplier
        return attackDamage

    def setMultiplier(self, mult):
        # ideally, we shouldn't be calling this particular function
        return True

    def getMultiplier(self):
        # ideally, we shouldn't be calling this particular function
        return 1.0

    def incMultiplier(self, inc):
        self.setMultiplier(self.getMultiplier() + inc)


# A status effect which just obscures the target's HP.
class ObscureHPStatusEffect(StatusEffectBase):
    pass


# A status effect which obscures all battle information.
class ObscureInformationStatusEffect(StatusEffectBase):
    pass


# A status effect that makes Zap Gags deal only one damage.
class PlasticSuitStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        AvatarTakeModifiedDamageStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        if attackTrack == AttackEnum.TOON_ZAP:
            attackDamage = 1
            self.wantShow = True
        return attackDamage


class OverrideAddedStatusEffect(StatusEffectBase):
    """
    This Status Effect hooks into the BattleAvatar's addStatusEffect class.
    Whenever a StatusEffect is attempted to be added to the class,
    it will replace it with a different class. Works for VisualEffects too.

    This can be particularly useful for when you want to have
    a Suit affect the environment more directly (e.g. replacing Soak with Frozen).

    To avoid issues, StatusEffect overrides only ever happens on the AI.
    This check happens in the addStatusEffect method of BattleAvatar.
    """

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = True    # If you intend on showing the Client any visual effect remaps,
                                # they MUST have it communicated to the client.
                                # You can have the effect's visibility disabled in
                                # StatusEffectDefinitions if you want to avoid that tho.

        # Status Effect remapping.
        self.statusEffectIdMapping = {}
        self.newStatusEffectIdArgs = {}

        # Visual Effect remapping.
        self.visualEffectIdMapping = {}
        self.newVisualEffectIdArgs = {}

    """
    All Status Effect Remap methods
    """

    def addNewStatusEffectMap(self, beforeId: int, afterId: int, newEffectArgs=None) -> None:
        """
        Adds a new mapping a StatusEffectID.

        :param beforeId: Some old StatusEffectID to replace.
        :param afterId: A new StatusEffectID to replace it with.
        :param newEffectArgs: Accepts the following:
            1) A list. Copied and used as new arguments for the StatusEffect.
            2) A function that returns a list. Gets called to use as args upon replacement.
               This function gets passed in the status effect.
            3) None. Uses the default args of the effect.
        :return: None.
        """
        # Set the ID in our map.
        self.statusEffectIdMapping[beforeId] = afterId

        # Copy the effectArgs.
        if type(newEffectArgs) is list:
            newEffectArgs = newEffectArgs[:]

        # Use them as our argument mapping.
        self.newStatusEffectIdArgs[afterId] = newEffectArgs

    def removeStatusEffectMap(self, beforeId: int) -> None:
        """
        Removes a mapping.

        :param beforeId: The beforeId to remove.
        :return: None.
        """
        afterId = self.statusEffectIdMapping[beforeId]
        del self.newStatusEffectIdArgs[afterId]
        del self.statusEffectIdMapping[beforeId]

    def clearStatusEffectMap(self) -> None:
        """
        Clears all StatusEffect maps.

        :return: None.
        """
        self.newStatusEffectIdArgs = {}
        self.statusEffectIdMapping = {}

    def checkStatusEffectForReplacementMap(self, beforeId: int, statusEffect):
        """
        Called from a BattleAvatar. Checks this status effect to
        determine if there should be a new StatusEffectID to use.

        :param beforeId: The ID to check for.
        :return: If there is a defined mapping, it will return both the
                 new StatusEffectID and the arguments for it.
                 If not, then it will return None, None.
        """
        if beforeId not in self.statusEffectIdMapping:
            return None, None

        # There is a mapping defined.
        afterId = self.statusEffectIdMapping[beforeId]

        # Get the args.
        afterArgs = self.newStatusEffectIdArgs[afterId]

        # If this is a function, run it.
        if callable(afterArgs):
            afterArgs = self.newStatusEffectIdArgs[afterId](statusEffect)

        return afterId, afterArgs

    """
    All Visual Effect Remap methods
    """

    def addNewVisualEffectMap(self, beforeEnum: VisualEffectEnum, afterEnum: VisualEffectEnum, newEffectArgs=None) -> None:
        """
        Adds a new mapping a VisualEffectID.

        :param beforeEnum: Some old VisualEffectID to replace.
        :param afterEnum: A new VisualEffectID to replace it with.
        :param newEffectArgs: Accepts the following:
            1) A list. Copied and used as new arguments for the VisualEffect.
            2) A function that returns a list. Gets called with args, to use as args.
            3) None. Uses the default args of the effect.
        :return: None.
        """
        # Set the ID in our map.
        self.visualEffectIdMapping[beforeEnum] = afterEnum

        # Copy the effectArgs.
        if type(newEffectArgs) is list:
            newEffectArgs = newEffectArgs[:]

        # Use them as our argument mapping.
        self.newVisualEffectIdArgs[afterEnum] = newEffectArgs

    def removeVisualEffectMap(self, beforeEnum: VisualEffectEnum) -> None:
        """
        Removes a mapping.

        :param beforeEnum: The beforeEnum to remove.
        :return: None.
        """
        afterId = self.visualEffectIdMapping[beforeEnum]
        del self.newVisualEffectIdArgs[afterId]
        del self.visualEffectIdMapping[beforeEnum]

    def clearVisualEffectMap(self) -> None:
        """
        Clears all StatusEffect maps.

        :return: None.
        """
        self.newVisualEffectIdArgs = {}
        self.visualEffectIdMapping = {}

    def checkVisualEffectForReplacementMap(self, beforeEnum: VisualEffectEnum, visualEffectExtraArgs):
        """
        Called from a BattleAvatar. Checks this status effect to
        determine if there should be a new StatusEffectID to use.

        :param beforeEnum: The ID to check for.
        :return: If there is a defined mapping, it will return both the
                 new StatusEffectID and the arguments for it.
                 If not, then it will return None, None.
        """
        if beforeEnum not in self.visualEffectIdMapping:
            return None, None

        # There is a mapping defined.
        afterId = self.visualEffectIdMapping[beforeEnum]

        # Get the args.
        afterArgs = self.newVisualEffectIdArgs[afterId]

        # If this is a function, run it.
        if callable(afterArgs):
            afterArgs = self.newVisualEffectIdArgs[afterId](visualEffectExtraArgs)

        return afterId, afterArgs


class DeepFreezeStatusEffect(AvatarTakeModifiedDamageStatusEffect, UnitesDisabledStatusEffect, AttackAccuracyStatusEffect):
    """
    This is a unique status effect which moves all
    Toon Attacks after all Cog Attacks.
    """

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.multiplier = 0.8
        self.inheritedEventDefinitions += [SEE.EFFECT_UNITE_COOLDOWN]
        self.accuracyChange = 0
        self.override = 100
        self.hasShiftedToonMoves = False
        self.hasDisabledUnites = False

    def reset(self):
        """
        Called at the start of a turn.
        """
        self.hasShiftedToonMoves = False

    def onMovieDone(self):
        # When the battle movie is done, set unites to disabled.
        self.hasDisabledUnites = True

    def handleAttackAccuracy(self, attackTrack: int, attackAccuracy):
        if attackTrack == AttackEnum.TOON_HEAL:
            return 100, 100
        return attackAccuracy, -1

    def shiftAllToonMoves(self, attackOrder):
        """
        Shifts all Toon Moves from the start of
        the turn to after the Cogs have moved.
        """
        if self.hasShiftedToonMoves:
            return

        # Prevent any other Deep Freeze status effect from functioning.
        self.setShiftOnAllDeepFreezeEffects()

        # Sort the attack order based on if the attack is a toon attack.
        from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import ToonAttackAI
        attackOrder.sort(key=lambda atk: isinstance(atk, ToonAttackAI))

    def setShiftOnAllDeepFreezeEffects(self):
        """
        To make sure the logic on this attack doesn't
        mess the hell up, we need to make sure that only
        one Deep Freeze status effect engages.
        """
        allStatusEffects = self.getBattleCalc().getAllToonStatusEffects()
        for effect in allStatusEffects:
            if isinstance(effect, self.__class__):
                effect.hasShiftedToonMoves = True


"""
HP Gates.
An HP gate is a special type of callback for
a StatusEffect which an HPGatekeeper handles.
The callback gets fired whenever its avatar
hits a specific HP level.
"""


class HPGate:
    """
    A definition for an HPGate callback.
    """

    def __init__(self, hpRatio: float, callback=None,
                 maxUses=1, unlimited=False, canFireFunction=None,
                 isRatio: bool=True):
        """
        :param hpRatio: The hpRatio to check HP from (0.0 -> 1.0).
        :param callback: A callback to fire upon HPGate succession.
        :param maxUses: How many times the HPGate can fire.
        :param unlimited: Whether or not the HPGate can fire an unlimited amount of times.
        :param canFireFunction: A callable that must return a bool. If it returns True, the
                                gate is allowed to fire. If it returns False, then it won't.
        :param isRatio: Whether or not the hpRatio value is indeed representative of a percentage.
                        When False, it will run under the assumption of it being a static integer.
        """
        self.hpRatio = hpRatio
        self.isRatio = isRatio
        self.callback = callback
        self.maxUses = maxUses
        self.unlimited = unlimited
        self.canFireFunction = canFireFunction
        self.timesFired = 0

    def canFire(self, statusEffect=None) -> bool:
        """
        Can be inherited by other HPGates to provide
        a unique check for whether or not the HPGate can fire.

        :param statusEffect: The status effect associated with the HPGate.
        :return: True if the gate can fire, False otherwise.
        """
        return True

    def checkGate(self, battleAvatar, statusEffect=None):
        from toontown.clashbattle.battle import BattleAvatar
        """
        Checks if a gate has been met.
        If it has, return the callback to fire.

        :param battleAvatar: The battleAvatar to check HP off of.
        :param statusEffect: The statusEffect this HPGate is attached to.
        """
        if (self.timesFired >= self.maxUses) and not self.unlimited:
            # We've already fired this HPGate too many times.
            return None

        if not self.canFire(statusEffect):
            # A subclass decided this gate can't fire for whatever reason.
            return None

        if self.canFireFunction is not None:
            if not self.canFireFunction():
                # A defined canFireFunction decided this gate cannot fire.
                return None

        if self.testGate(battleAvatar):
            # This gate is able to be fired. Fire and return the callback.
            self.timesFired += 1
            return self.callback

    def testGate(self, battleAvatar):
        """
        Determines if this gate can be fired or not.

        :param battleAvatar: The battleAvatar to check HP off of.
        """
        if not self.isRatio:
            return battleAvatar.getHp() <= self.hpRatio
        return battleAvatar.getHealthPercentage() <= self.hpRatio


class HPGatekeeper(StatusEffectBase):
    """
    An HPGatekeeper class.
    Manages HP Gates.
    """

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.inheritedEventDefinitions += [SEE.DEFINITION_HP_GATEKEEPER]
        self.hpGates = []  # List[HPGate]

    def cleanup(self):
        if self.cleanedUp:
            return

        del self.hpGates
        return super().cleanup()

    def _setManualHPGates(self):
        """If this is called, then we trust the StatusEffect to manually call the fireGates method."""
        if SEE.DEFINITION_HP_GATEKEEPER in self.inheritedEventDefinitions:
            self.inheritedEventDefinitions.remove(SEE.DEFINITION_HP_GATEKEEPER)

    def addHPGate(self, hpRatio: float, callback=None,
                  maxUses=1, unlimited=False, canFireFunction=None,
                  isRatio: bool=True):
        """
        :param hpRatio: The hpRatio to check HP from (0.0 -> 1.0).
        :param callback: A callback to fire upon HPGate succession.
        :param maxUses: How many times the HPGate can fire.
        :param unlimited: Whether or not the HPGate can fire an unlimited amount of times.
        :param canFireFunction: A callable that must return a bool. If it returns True, the
                                gate is allowed to fire. If it returns False, then it won't.
        :param isRatio: Whether or not the hpRatio value is indeed representative of a percentage.
                        When False, it will run under the assumption of it being a static integer.
        """
        self.hpGates.append(
            HPGate(hpRatio=hpRatio, callback=callback, maxUses=maxUses,
                   unlimited=unlimited, canFireFunction=canFireFunction,
                   isRatio=isRatio)
        )

    def resetHPGates(self):
        self.hpGates = []

    def fireGates(self):
        """
        Check and fire all of the HPGates.
        """
        for gate in self.hpGates:
            callback = gate.checkGate(self.getAv(), statusEffect=self)
            if callback is not None:
                callback()


class CogStatusEffect(HPGatekeeper):
    """CogStatusEffect: Contains the basic behavior functionality
    of any generic Cog. All status effects which extend and/or
    change this basic behavior should inherit from this class.
    """

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.inheritedEventDefinitions += [SEE.EFFECT_SUIT]
        self.canGenerateAttack = True
        # Used to handle damage that is taken in the same track after a suit revives
        self.trackAfterReviveDamage = False

    def generateAttack(self):
        if not self.canGenerateAttack:
            return

        from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI
        suit: ClashSuitBaseAI = self.getAv()
        if suit.noRegularAttackRounds > 0:
            suit.noRegularAttackRounds -= 1
            return
        elif suit.noRegularAttackRounds == -1:
            return

        self.generateRandomSuitAttack()

    def generateRandomSuitAttack(self, *args, **kwargs):
        """
        Picks and returns a random attack type for the indicated Suit.
        """
        if not self.canGenerateAttack:
            return

        from toontown.clashbattle.battle.attacks.server.AttackAI import AttackAI
        from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI

        suit: ClashSuitBaseAI = self.getAv()
        choice = suit.getRandomAttack()

        from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import createAttack
        attack: AttackAI = createAttack(choice, *args, **kwargs, invoker=suit)

        if suit.getPassive(PassiveAttributeDefs.ATTACKS_FIRST, False):
            insertMode = "beginning"
        else:
            insertMode = "end"

        self.getBattleCalc().insertAttack(attack, insertMode, respectPreviousAdditions=True, overrideInserted=False)

    def enableAttackGeneration(self):
        self.canGenerateAttack = True

    def disableAttackGeneration(self):
        self.canGenerateAttack = False

    ### Revive stuff

    def handleSuitRevived(self, suit):
        if suit is not self.av:
            return

        self.trackAfterReviveDamage = True

    def handleReviveDamageInfo(self):
        # Set a field on the client to keep track of how much damage was taken after a revive was complete
        if self.trackAfterReviveDamage:
            self.av.d_setAfterReviveDamage([self.av.getHp(), self.av.getMaxHp()])

        self.trackAfterReviveDamage = False

    def getAvatarBattleState(self):
        return self.getAv().getBattleState()


class StatusEffectRoundsModifierEffect(StatusEffectBase):
    EFFECTS_TO_MODIFY = []

    def __init__(self, *args):
        super().__init__(*args)
        self.wantShow = False
        # How many rounds should the given effectIds be modified by
        self.roundModifier = self.extraArgs[0]
        self.relativeModifier = self.extraArgs[1]
        self.fields = ['roundModifier', 'relativeModifier']
        self.inheritedEventDefinitions = [SEE.DEFINITION_ROUNDS_MODIFIER]

    def handleEffectRounds(self, effect, avatar):
        """
        Called whenever an effect is created or combined.
        Will adjust the effect's rounds based on the modifier on this effect.
        """

        # Only care about our avatar, not anyone elses
        if avatar is not self.av:
            return

        # Only care about effects in our modify list
        if effect.effectId not in self.EFFECTS_TO_MODIFY:
            return

        # Update the rounds of the effect based on our modifier
        if self.relativeModifier:
            effect.setRounds(max(effect.getRounds() + self.roundModifier, 1), adjust=False)
            return

        effect.setRounds(min(effect.getRounds(), self.roundModifier), adjust=False)

    def handleSuitLured(self, target, lureEffect):
        if target is not self.av:
            return

        # Make sure we update the knockback value to display correctly for lure
        for lureAttack in list(lureEffect.invokers.values()):
            for result in lureAttack.results:
                if result.avId != self.av.doId:
                    continue

                if (self.roundModifier > 0 and result.kbBonus < lureEffect.getRounds()) or (self.roundModifier < 0 and result.kbBonus > lureEffect.getRounds()):
                    result.kbBonus = lureEffect.getRounds()

    def handleSuitSoaked(self, target, soakEffect, squirtAttack):
        if target is not self.av:
            return

        # Make sure we update the soak rounds value to show correctly on the client
        for result in squirtAttack.results:
            if result.avId != self.av.doId:
                continue

            if (self.roundModifier > 0 and result.extraArgs[0] < soakEffect.getRounds()) or (self.roundModifier < 0 and result.extraArgs[0] > soakEffect.getRounds()):
                result.extraArgs[0] = soakEffect.getRounds()


# Currently not used :blush:
class HPRandomizerStatusEffect(StatusEffectBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.wantShow = False
        # Minimum range of randomized HP
        self.minRange = self.extraArgs[0]
        # Maximum range of randomized HP
        self.maxRange = self.extraArgs[1]
        # The chosen random hp percentage
        self.chosenPercent = self.extraArgs[2]
        self.fields = ['minRange', 'maxRange', 'chosenPercent']
        # Handle the randomized HP on the server
        if self.isAi():
            self.handleHP()

    def handleHP(self):
        # This would be way too dangerous to allow to ever go on Toons,
        # so double check this just in case.
        from toontown.clashsuit.suit.SuitBase import SuitBase
        if not isinstance(self.av, SuitBase):
            simbase.air.writeServerEvent('suspicious', self.av.doId, "Toon somehow got an HP randomizer status effect. Bad.")
            return

        # Get a random HP percent from our range
        self.chosenPercent = round(lerp(self.minRange, self.maxRange, random.random()), 2)
        # Apply the random HP percent
        self.av.b_setMaxHp(int(self.av.getMaxHp() * self.chosenPercent))


class SkelecogStatusEffect(StatusEffectRoundsModifierEffect):
    EFFECTS_TO_MODIFY = SUIT_STATUS_EFFECTS_TO_REDUCE

    def __init__(self, *args):
        super().__init__(*args)
        self.wantShow = True
        self.chosenPercent = self.extraArgs[2]
        self.fields.extend(['chosenPercent'])

    def setChosenPercent(self, chosenPercent):
        self.chosenPercent = chosenPercent

    def getChosenPercent(self):
        return self.chosenPercent


# Generic damage absorption status effect
class DamageAbsorbStatusEffect(StatusEffectBase):
    AVATAR_TYPE_SUIT = 0
    AVATAR_TYPE_TOON = 1
    # Determines whether or not absorbs placed on multiple cogs will split damage.
    SplitMultipleTargetDamage = True
    # Ignore absorb mechanics if no avs have damage downs
    IgnoreWhenNoDamageDowns = True
    # Only apply damage downs if there are cogs existing to absorb stuff
    ApplyDamageDownOnlyWithAbsorbs = True
    # The attack type for when a Toon absorbs damage
    ToonDamageAbsorbAttack = AttackEnum.DAMAGE_ABSORB_TOON_DAMAGE
    # The attack type for when a Suit absorbs damage
    SuitDamageAsborbAttack = AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE

    def __init__(self, *args):
        super().__init__(*args)
        # Absorb multiplier is sort of the opposite of what you would expect it to be.
        # A 0.7 absorb multiplier will mean that this cog will absorb 30% of damage dealt.
        self.absorbMultiplier = self.extraArgs[0]
        # Is it a toon or a suit that is doing the absorption?
        self.avatarType = self.extraArgs[1]
        self.fields = ['absorbMultiplier', 'avatarType']
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE, SEE.DEFINITION_DAMAGE_ABSORB]
        self.activeDamageDowns = {}
        self.damageDealtThisTrack = 0
        # Do an initial "round begin" to get the damage down on the other avatars,
        # Since this could happen anytime after the beginning of a turn
        # but before the end of it
        if self.isAi():
            self.handleBeginRound()

    def setMultiplier(self, multiplier):
        self.absorbMultiplier = multiplier

    def handleBeginRound(self):
        # Delete and re-instantiate all damage downs
        self.deleteOthersDamageDown()
        self.damageDealtThisTrack = 0

        absorbCogs = self.getAbsorbTargetList()
        if self.ApplyDamageDownOnlyWithAbsorbs and len(absorbCogs) <= 0:
            return

        avatars = self.getDamageTakenDownAvatars()
        self.addDamageDownToAvatars(avatars)

    def getDamageTakenDownAvatars(self):
        if self.avatarType == self.AVATAR_TYPE_SUIT:
            avatars = [avatar for avatar in self.getBattleCalc().getAliveCogs()]
        elif self.avatarType == self.AVATAR_TYPE_TOON:
            getProfile = self.getBattleCalc().getToon
            avatars = [getProfile(toonID) for toonID in self.getBattleCalc().toons]
            avatars = [av for av in avatars if av and av.getHp() > 0]
        else:
            raise AttributeError(f"self.avatarType is incorrectly defined for effect {self.__class__.__name__}. Expected: (0, 1). Got: {self.avatarType}.")

        # Remove ourselves from the list if we're in it
        if self.getAv() in avatars:
            avatars.remove(self.getAv())

        return avatars

    def addDamageDownToAvatars(self, avatars):
        # Run through all avatars and see if we need to add a hidden damage down effect to them
        for avatar in avatars:
            if avatar and avatar not in self.activeDamageDowns:
                newEffect, _ = avatar.addStatusEffect(SEE.EFFECT_DAMAGE_ABSORB_DAMAGE_DOWN)
                newEffect.setMultiplier(self.absorbMultiplier)
                self.activeDamageDowns[avatar] = newEffect

    def shouldTrackDamage(self, suit):
        return suit not in self.getAbsorbTargetList()

    # Called when any suit takes damage
    def incrementSuitDamageDealt(self, amount, suit, track):
        # Ignore this if our absorbing avatar is a Toon
        if self.avatarType == self.AVATAR_TYPE_TOON:
            return
        # Only add damage dealt this track to absorb if this is not us that was hurt
        if not self.shouldTrackDamage(suit):
            return

        # Do some math to figure out how much damage was prevented and deal that to us
        self.damageDealtThisTrack += int(amount * (1 - self.absorbMultiplier) / self.absorbMultiplier)

    def getAbsorbTargetList(self):
        return [self.getAv()]

    def handleTrackOver(self):
        # This is a suit-absorbing-damage specific function.
        if self.avatarType == self.AVATAR_TYPE_TOON:
            return

        targetList = self.getAbsorbTargetList()

        if self.damageDealtThisTrack and (len(self.activeDamageDowns) > 0 or not self.IgnoreWhenNoDamageDowns):
            # Take some damage here as "damage absorption"
            damageTaken = self.damageDealtThisTrack
            # Only absorb if there are cogs that actually can absorb.
            if len(targetList) > 0:
                # If greater than one targets absorbing, split damage.
                if len(targetList) > 1 and self.SplitMultipleTargetDamage:
                    damageTaken = int(math.ceil(damageTaken / len(targetList)))

                self.createGeneralAttack(self.SuitDamageAsborbAttack, extraArgs=[damageTaken], targetList=targetList)

        self.damageDealtThisTrack = 0
        # If we have no absorbers left, delete the damage downs.
        if len(targetList) <= 0:
            self.deleteOthersDamageDown()

    # Called when any Toon takes damage
    def incrementToonDamageDealt(self, amount, toon):
        # Ignore this if our absorbing avatar is a Suit
        if self.avatarType == self.AVATAR_TYPE_SUIT:
            return
        if toon is self.getAv():
            return

        # Do some math to figure out how much damage was prevented and deal that to us
        damageTaken = int(amount * (1 - self.absorbMultiplier) / self.absorbMultiplier)
        self.createGeneralAttack(self.ToonDamageAbsorbAttack, extraArgs=[damageTaken])

    def delete(self):
        if self.cleanedUp:
            return
        # This effect is gone, remove all active damage downs on other avatars
        self.deleteOthersDamageDown()
        super().delete()

    def deleteOthersDamageDown(self):
        # Remove all current damage modifier status effects on other avatars
        for effect in self.activeDamageDowns.values():
            effect.delete()
        self.activeDamageDowns = {}


class DamageAbsorbDamageDownStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, *args):
        super().__init__(*args)
        self.wantShow = False
        self.combines = False


# Status effect that is placed on other cogs when damage absorption is active
class DamageAbsorbInstantStatusEffect(DamageAbsorbStatusEffect):
    SuitDamageAsborbAttack = AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE_INSTANT


class NervousPacingStatusEffect(StatusEffectBase):
    """
    A hidden status effect that will cause a Cog's "position" priority in battle
    to change over time given various conditions. On default, it will happen
    on round end, if they are alone in the battle.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = False
        self.initAttributes()

    def initAttributes(self):
        self._currentPacingIndex = -1
        self.inheritedEventDefinitions.append(SEE.EFFECT_NERVOUS_PACING)

    def _rotateAvatarPacing(self):
        self._currentPacingIndex += 1
        if self._currentPacingIndex >= len(self.pacing_getPriorityOrder()):
            self._currentPacingIndex = 0
        self.av.setBattleOrderPriority(self.pacing_getPriority())

    def pacing_onRoundEnd(self):
        """Default behavior. On round end, determine if we should change pace, and do it."""
        if self.pacing_shouldPace():
            self._rotateAvatarPacing()

    def pacing_shouldPace(self) -> bool:
        """Determines if the Suit's nervous pacing should apply."""
        return True

    def pacing_getPriorityOrder(self) -> List[BattleOrderPriority]:
        """Determines the priority order of the pacing."""
        return [
            BattleOrderPriority.BEGINNING,
            BattleOrderPriority.MIDDLE,
            BattleOrderPriority.END,
            BattleOrderPriority.MIDDLE,
        ]

    def pacing_getPriority(self):
        return self.pacing_getPriorityOrder()[self._currentPacingIndex]

# endregion


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
# 'Environmental' Status Effects #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-= #
# region

class SoakToFrozenStatusEffect(OverrideAddedStatusEffect):
    """
    A target with this status effect will replace any
    Soak status effect it receives with a Frozen one.
    """

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)

        # Bind Soak to Frozen.
        self.addNewStatusEffectMap(beforeId=SEE.EFFECT_SUIT_SOAKED, afterId=SEE.EFFECT_SUIT_FROZEN, newEffectArgs=self.carryRoundsOver)

        # Bind Drenched to Frozen.
        self.addNewStatusEffectMap(beforeId=SEE.EFFECT_SUIT_DRENCHED, afterId=SEE.EFFECT_SUIT_FROZEN, newEffectArgs=self.carryRoundsOver)

        self.addNewVisualEffectMap(beforeEnum=VisualEffectEnum.SOAKED, afterEnum=VisualEffectEnum.FROZEN)

    @staticmethod
    def carryRoundsOver(soakedStatusEffect):
        """
        This method gets called upon the Soak status effect, and
        carries the rounds over to use as the new effect.

        :param soakedStatusEffect: The Soaked status effect.
        :return: A list of the new args to use.
        """
        return [BattleGlobals.FrozenDefBonusAmt, soakedStatusEffect.rounds]

# endregion

# -=-=-=-=-=-=-=-=-=-=-=-=- #
# Litigation Status Effects #
# -=-=-=-=-=-=-=-=-=-=-=-=- #
# region


# Base class used for all litigation team managers
class LitigationTeamManagerStatusEffectBase(CogStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = False
        self.inheritedEventDefinitions += [SEE.DEFINITION_LITIGATION_TEAM_MANAGER]
        self.wantShow = False
        self.litigationMembers = ['stenog', 'sgoat', 'lgator', 'caseman']
        self.hasMembers = {}
        self.resistingLure = False
        # Do initial population of our dict of litigation members.
        self.updateLitigationMembers(ignoreHp=True)
        self.attackId2Type = {}
        if self.isAi() and not self.battleCalc.getEnvironmentalOfType(ENV_ENUM.OVERCHARGE_ALL):
            self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])

    def cleanup(self):
        if self.cleanedUp:
            return

        del self.attackId2Type
        del self.hasMembers
        del self.litigationMembers

        super().cleanup()

    def updateLitigationMembers(self, ignoreHp=False):
        # We don't need to care about this if we're dead.
        if self.getAv().getHp() <= 0 and not ignoreHp:
            return

        # Update our list of the cogs we have with us.
        for member in self.litigationMembers:
            suit = self.getBattleCalc().findCogInBattle(member)
            self.hasMembers[member] = True if suit and suit.getHp() > 0 else False

    def checkSpawnNaturalCogs(self):
        # If we have the litigator in our battle, we don't need natural cog spawns.
        if self.hasMembers['lgator']:
            return

        # If natural cogs have already been spawned this turn, don't do anything.
        if self.getBattleCalc().hasEventBeenSent(BEG.EVENT_LT_SPAWN_NATURAL_COGS):
            return

        # Try to spawn 2 cogs into the battle
        # If any cogs spawn at all, we can send the event below
        result = any([self.addCogToBattle(), self.addCogToBattle()])
        # Only send this event if a cog was successfully added to battle.
        if result:
            self.getBattleCalc().sendEvent(BEG.EVENT_LT_SPAWN_NATURAL_COGS)

    def addCogToBattle(self):
        battle = self.getBattle()
        # Don't follow through if this battle does not have less suits than max.
        if not battle.lessSuitsThanMax():
            return False

        boss = simbase.air.doId2do.get(battle.bossCogId)
        # Grab the correct battle from the boss that we are in
        if battle is boss.battleA:
            reserveSuits = boss.reserveSuitsA
        else:
            reserveSuits = boss.reserveSuitsB

        # Append a randomly generated suit from the boss.
        reserveSuits.append((boss.genRandSuit(battle), 0))
        return True

    def isScapegoatInRage(self):
        # Make sure that we actually have scapegoat here
        if not self.hasMembers['sgoat']:
            return False

        # Once more, make sure we actually have scapegoat here
        scapegoat = self.getBattleCalc().findCogInBattle('sgoat')
        if not scapegoat:
            return False

        # Make sure we have the rage status effect
        rageEffects = scapegoat.getStatusEffectsOfType(ScapegoatRageStatusEffect)
        if not rageEffects:
            return False

        # Return whether or not the rage effect is saying scapegoat is in rage
        return bool(rageEffects[0].getInRage())

    def checkApplyLureResistance(self):
        # Figure out if we need to apply extra lure resistance or not.
        battle = self.getBattle()
        boss = simbase.air.doId2do.get(battle.bossCogId)
        if not self.resistingLure and sum(list(self.hasMembers.values())) == 1 and len(boss.reserveSuits) == 0:
            self.applyDesperationLureResistance()

    def applyDesperationLureResistance(self):
        self.resistingLure = True
        self.lureResistanceEffect.setAmount(1)
        self.createGeneralAttack(AttackEnum.SHOW_HP_TEXT, [TTLocalizer.HP_TEXT_DESPERATION], [self.getAv()])
        self.av.addStatusEffect(SEE.EFFECT_SUIT_DAMAGE_BOOST, extraArgs=[1.4, 2])


# Used for the Litigator (from Litigation team), manages many aspects of his special abilities for him.
class LitigatorManagerStatusEffect(LitigationTeamManagerStatusEffectBase, MultiTimer):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        LitigationTeamManagerStatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        # Timer 0: Snap timer
        # Timer 1: Bayou Bash timer
        MultiTimer.__init__(self, numberOfTimers=2)
        self.inheritedEventDefinitions += [SEE.DEFINITION_MULTI_TIMER]
        self.timesSummoned = 0
        self.toonsDamageDealt = {}
        self.damageTaken = 0
        self.damageThreshold = 500
        self.attackId2Type = {AttackEnum.BAYOU_BASH: self.createBayouBashAttack,
                              AttackEnum.SNAP: self.createSnapAttack,
                              AttackEnum.SNAP_RETALIATE: self.createSnapAttack}

    def cleanup(self):
        if self.cleanedUp:
            return

        del self.toonsDamageDealt
        super().cleanup()

    def increaseTimesSummoned(self):
        self.timesSummoned += 1

    def getTimesSummoned(self):
        return self.timesSummoned

    def createBayouBashAttack(self):
        # If Bayou Bellow has already been used this turn, then just return
        if self.getBattleCalc().hasEventBeenSent(BEG.EVENT_LT_LGATOR_BAYOU_BELLOW):
            return

        # BayouBashAI handles all decisions between doing bash, bellow, or nothing
        self.createAttack(AttackEnum.BAYOU_BASH)

    def createSnapAttack(self, weak=False, chosenToon=None):
        # Increase the multiplier if we have stenographer in the battle.
        # Force the multiplier to 10% if we have the weak flag.
        multiplier = 1.1 if weak else (1.4 if self.hasMembers['stenog'] else 1.2)
        attackType = AttackEnum.SNAP_RETALIATE if weak else AttackEnum.SNAP
        targets = [chosenToon] if chosenToon else []
        self.createAttack(
            attackType, insertMethod='index' if weak else None, targets=targets,
            extraArgs=[self.toonsDamageDealt.copy(), multiplier, weak],
            passedArgs=[weak, chosenToon]
        )
        # Clear damage dealt after creating the attack
        if not weak:
            self.toonsDamageDealt = {}

    def increaseToonsDamageDealt(self, toon, amount):
        currAmount = self.toonsDamageDealt.get(toon, 0)
        self.toonsDamageDealt[toon] = currAmount + amount

    def increaseDamageTaken(self, amount: int) -> None:
        # Damage numbers are negative, so we need to make the amount
        # positive for this purpose.
        self.damageTaken = self.damageTaken + abs(amount)
        # If we've taken enough damage, shorten the cooldown of Bayou Bash
        while self.damageTaken >= self.damageThreshold:
            self.incrementRoundTimer(1, 1)
            self.damageTaken = self.damageTaken - self.damageThreshold

    def addCogToBattle(self):
        battle = self.getBattle()
        # Don't follow through if this battle does not have less suits than max.
        if not len([suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]) < battle.maxSuits:
            return False

        boss = simbase.air.doId2do.get(battle.bossCogId)
        # Grab the correct battle from the boss that we are in
        if battle is boss.battleA:
            reserveSuits = boss.reserveSuitsA
        else:
            reserveSuits = boss.reserveSuitsB

        # Append a randomly generated suit from the boss.
        suit = boss.genRandSuit(battle)
        # Add a starting status effect to the suit for insurance if case manager exists.
        if self.hasMembers['caseman']:
            suit.addStartingStatusEffect(SEE.EFFECT_CASE_MANAGER_HOT, rounds=1)
            suit.addStartingVisualEffect(VisualEffectEnum.INSURANCE)
        reserveSuits.append((suit, 0))
        return True


# Used for the Stenographer (from Litigation team), manages many aspects of her special abilities for her.
class StenographerManagerStatusEffect(LitigationTeamManagerStatusEffectBase, RoundTimer):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        LitigationTeamManagerStatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        RoundTimer.__init__(self)
        self.inheritedEventDefinitions += [SEE.DEFINITION_ROUND_TIMER]
        self.toonsDamageDealt = {}
        self.lastUsedGagLevel = 5
        self.lastUsedGagLevel2 = -1
        self.timesCourtCostsUsed = 0
        self.attackId2Type = {AttackEnum.COURT_SANCTION: self.createCourtSanctionAttack,
                              AttackEnum.COURT_SANCTION_RETALIATE: self.createCourtSanctionAttack,
                              AttackEnum.COURT_RECORD: self.createCourtRecordAttack,
                              AttackEnum.COURT_COSTS: self.createCourtCostsAttack}

    def cleanup(self):
        if self.cleanedUp:
            return

        del self.toonsDamageDealt
        super().cleanup()

    def createCourtSanctionAttack(self, weak=False, chosenToon=None):
        # Increase the multiplier if we have litigator in the battle,
        # Force the multiplier to 25% if we have the weak flag.
        multiplier = 0.75 if weak else (0.25 if self.hasMembers['lgator'] else 0.5)
        attackType = AttackEnum.COURT_SANCTION_RETALIATE if weak else AttackEnum.COURT_SANCTION
        targets = [chosenToon] if chosenToon else []
        self.createAttack(
            attackType, insertMethod='index' if weak else None, targets=targets,
            extraArgs=[self.toonsDamageDealt.copy(), multiplier, weak],
            passedArgs=[weak]
        )
        # Clear damage dealt after creating the attack
        if not weak:
            self.toonsDamageDealt = {}

    def increaseToonsDamageDealt(self, toon, amount):
        currAmount = self.toonsDamageDealt.get(toon, 0)
        self.toonsDamageDealt[toon] = currAmount + amount

    def createCourtRecordAttack(self):
        # Don't create the attack if its already happened this turn.
        if self.getBattleCalc().hasEventBeenSent(BEG.EVENT_LT_STENOG_USE_COURT_RECORD):
            return

        # Pick a random gag level from 5 to 7 (effectively 6 to 8) to disable for the next turn.
        # Additionally, remove our last used gag level to prevent repeats from happening.
        levelChoices = [5, 6, 7]
        levelChoices.remove(self.lastUsedGagLevel)

        # Choose our first gag level to disable.
        gagChoice1 = random.choice(levelChoices)
        choiceList = [gagChoice1]
        levelChoices.remove(gagChoice1)

        # If scapegoat is in rage, choose a second to disable.
        gagChoice2 = -1
        if self.isScapegoatInRage():
            gagChoice2 = random.choice(levelChoices)
        choiceList.append(gagChoice2)

        # Create the court record attack with the given levels
        self.createAttack(AttackEnum.COURT_RECORD, extraArgs=choiceList)
        # Keep track of our last used levels
        self.lastUsedGagLevel = gagChoice1
        self.lastUsedGagLevel2 = gagChoice2

    def triggeredCourtRecordDamage(self, attack):
        self.createGeneralAttack(
            AttackEnum.COURT_RECORD_DAMAGE,
            extraArgs=[-50],
            targetList=[attack.invoker]
        )

    def createCourtCostsAttack(self, damageToDeal=None):
        # Increases from 24 damage to a max of 155, increases by +4 every time its used.
        if not damageToDeal:
            damageToDeal = self.getCourtCostsDamage()
            self.timesCourtCostsUsed += 1

        self.createAttack(AttackEnum.COURT_COSTS, extraArgs=[damageToDeal], passedArgs=[damageToDeal])

    def getCourtCostsDamage(self) -> int:
        return min(24 + (4 * self.timesCourtCostsUsed), ToontownGlobals.MaxHpLimit)

    def createCalculatingCostsAttack(self):
        # Shows a telegraph of the incoming court costs attack
        self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
            AttackEnum.STENOG_CALCULATING_COSTS,
            {"targets": [self.av], "extraArgs": [self.getCourtCostsDamage()]},
            {"mode": 'end'},
        ])

    def addAttackToLureQueue(self, attackId, passedArgs):
        # We have to have this extra in here, as stenographer is the only one who has an ability that will
        # trigger every turn and should not overlap.
        if attackId == AttackEnum.COURT_RECORD:
            return

        self.lureAbilityQueue.append([attackId, passedArgs])
        self.createGeneralAttack(AttackEnum.SHOW_HP_TEXT, extraArgs=[TTLocalizer.HP_TEXT_ABILITY_QUEUE])


# Used for the Case Manager (from Litigation team), manages many aspects of his special abilities for him.
class CaseManagerManagerStatusEffect(LitigationTeamManagerStatusEffectBase, RoundTimer):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        LitigationTeamManagerStatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        RoundTimer.__init__(self)
        self.inheritedEventDefinitions += [SEE.DEFINITION_ROUND_TIMER]
        self.attackId2Type = {AttackEnum.INSURANCE_PLAN: self.createInsurancePlanAttack,
                              AttackEnum.LEGAL_BINDINGS: self.createLegalBindingsAttack}

    def createInsurancePlanAttack(self):
        self.createAttack(AttackEnum.INSURANCE_PLAN)

    def createLegalBindingsAttack(self):
        self.createAttack(AttackEnum.LEGAL_BINDINGS)


# Used for the Scapegoat (from Litigation team), manages many aspects of his special abilities for him.
class ScapegoatManagerStatusEffect(LitigationTeamManagerStatusEffectBase, RoundTimer):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        LitigationTeamManagerStatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        RoundTimer.__init__(self)
        self.inheritedEventDefinitions += [SEE.DEFINITION_ROUND_TIMER]

    def updateLureResistanceForRage(self, entering=True):
        if entering:
            self.lureResistanceEffect.setAmount(-1 if self.resistingLure else 1)
        else:
            self.lureResistanceEffect.setAmount(1 if self.resistingLure else 2)

    def applyDesperationLureResistance(self):
        self.resistingLure = True
        rageEffect = self.getAv().getStatusEffectOfType(ScapegoatRageStatusEffect)
        if rageEffect:
            self.lureResistanceEffect.setAmount(-1 if rageEffect.getInRage() else 1)
            if rageEffect.getInRage():
                rageEffect.rageAndDesperation = 1
        self.createGeneralAttack(AttackEnum.SHOW_HP_TEXT, [TTLocalizer.HP_TEXT_DESPERATION], [self.getAv()])
        self.av.addStatusEffect(SEE.EFFECT_SUIT_DAMAGE_BOOST, extraArgs=[1.4, 2])


# Used for healing suits over time, creates a general attack to display it
class SuitHealOverTimeStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = False
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE, SEE.DEFINITION_SUIT_HEAL_OVER_TIME]
        self.amount = extraArgs[0]
        self.additive = extraArgs[1]
        self.healthCap = extraArgs[2]
        self.fields = ['amount', 'additive', 'healthCap']

    def setAmount(self, amount):
        self.amount = amount

    def getAmount(self):
        return self.amount

    def setAdditive(self, additive):
        self.additive = additive

    def setHealthCap(self, healthCap):
        self.healthCap = healthCap

    def applyHeal(self):
        suit = self.getAv()
        # If the suit is already at max HP (including overheal), we don't need a heal.
        healthPercentage = suit.getHp() / suit.getMaxHp()
        if healthPercentage >= self.healthCap:
            return
        # Make sure the suit isn't dead either
        if suit.getHp() <= 0:
            return
        self.createGeneralAttack(
            AttackEnum.SUIT_HEAL,
            extraArgs=[self.amount, self.additive, self.healthCap],
            targetList=[self.getAv()]
        )


# A variation of suit heal over time, used by the case manager and has special healing parameters
class InsuranceStatusEffect(LureResistanceStatusEffect, SuitHealOverTimeStatusEffect, MinibossResistancesStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        SuitHealOverTimeStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.lureResistanceAmount = 2
        self.adjustCurrentLureRounds(self.lureResistanceAmount, adjust=False)
        self.minibossImmunitiesActive = True
        # AI Only
        if self.avProfile.battleListener:
            # They have a sue effect, delete it.
            sueEffect = self.avProfile.getStatusEffectOfType(SueStatusEffect)
            if sueEffect:
                sueEffect.delete()

    def handleLureResistance(self, suit, lureResistance):
        return min(lureResistance, self.lureResistanceAmount)

    def combine(self, otherEffect):
        # Get rounds from other effect, -1 to compensate for the adjust
        otherRounds = otherEffect.getRounds() - 1
        # Max of 5 rounds/stacks at any given time
        self.setRounds(clampScalar(self.rounds + otherRounds, self.rounds, 5), adjust=False)

    def applyHeal(self):
        suit = self.getAv()
        # If the suit is already at max HP (including overheal), we don't need a heal.
        healthPercentage = suit.getHp() / suit.getMaxHp()
        if healthPercentage >= self.healthCap:
            return
        # Make sure the suit isn't dead either
        if suit.getHp() <= 0:
            return

        self.createGeneralAttack(
            AttackEnum.SUIT_HEAL,
            extraArgs=[self.amount, True, self.healthCap],
            targetList=[self.getAv()]
        )


# Self explanatory, deals damage to a toon over multiple rounds.
class ToonDamageOverTimeStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE]
        self.amount = extraArgs[0]
        self.fields = ['amount']

    def combine(self, otherEffect):
        otherRounds = otherEffect.getRounds()
        # Max of 5 stacks at any time
        self.setRounds(min(self.rounds + otherRounds, 5), adjust=False)

    def setAmount(self, amount):
        self.amount = amount

    def getAmount(self):
        return self.amount

    def applyDamage(self):
        self.createGeneralAttack(
            AttackEnum.TOON_DAMAGE,
            extraArgs=[-self.amount],
            targetList=[self.getAv()]
        )


# Deals damage to a toon over multiple rounds. (Legal bindings specific)
class LegalBindingsStatusEffect(ToonDamageOverTimeStatusEffect):
    def applyDamage(self):
        self.createGeneralAttack(
            AttackEnum.LEGAL_BINDINGS_DAMAGE,
            extraArgs=[-self.amount],
            targetList=[self.getAv()]
        )
        # Send event that legal bindings expired (can't use the normal status effect expired event, since that would
        # result in steno trying to add weak sanction after all attacks have been calculated. Thus, it would
        # go into the void and never trigger)
        if self.getRounds() <= 1:
            self.getBattleCalc().sendEvent(BEG.EVENT_LT_CASEMAN_BINDINGS_EXPIRED, [self.getAv()])


# Sends an event when the avatar uses the gag level set.
class UseGagLevelSenderStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE]
        self.gagLevel = extraArgs[0]
        self.gagLevel2 = extraArgs[1]
        self.eventToSend = extraArgs[2]
        self.fields = ['gagLevel', 'gagLevel2', 'eventToSend']

    def combine(self, otherEffect):
        # When combining, take the new effects gag level and if needed the new effects rounds.
        self.setGagLevel(otherEffect.getGagLevel())

        otherRounds = otherEffect.getRounds()
        if otherRounds > self.rounds or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)

    def checkSendEvent(self, attack):
        # Make sure the toon that did this is actually our toon!!!!!
        if ((self.gagLevel != -1 and self.gagLevel == attack.level) or
            (self.gagLevel2 != -1 and self.gagLevel2 == attack.level)) \
                and self.getAv() is attack.invoker:
            self.getBattleCalc().sendEvent(self.eventToSend, [attack])

    def setGagLevel(self, gagLevel):
        self.gagLevel = gagLevel

    def getGagLevel(self):
        return self.gagLevel

    def setGagLevel2(self, gagLevel):
        self.gagLevel2 = gagLevel

    def getGagLevel2(self):
        return self.gagLevel2

    def setEventToSend(self, eventToSend):
        self.eventToSend = eventToSend

    def getEventToSend(self):
        return self.eventToSend


class UseGagLevelsWithTrackSenderStatusEffect(UseGagLevelSenderStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = []
        # Fill in fields with all gag levels
        self.gagLevels = []
        for track in range(len(BattleGlobals.Tracks)):
            setattr(self, self.getAttrName(track), self.extraArgs[track])
            self.gagLevels.append(getattr(self, self.getAttrName(track), -1))
            self.fields.append(self.getAttrName(track))
        self.eventToSend = self.extraArgs[len(BattleGlobals.Tracks)]
        self.fields.append('eventToSend')

    def checkSendEvent(self, attack):
        # Make sure the attack passed is valid for Punishment
        if self.checkAttackValidForPunishment(attack):
            self.getBattleCalc().sendEvent(self.eventToSend, [attack])

    def checkAttackValidForPunishment(self, attack):
        gagLevel = self.getGagLevel(attack.track)
        return self.getAv() is attack.invoker and gagLevel != -1 and attack.level == gagLevel

    @staticmethod
    def getAttrName(track):
        return f'gagLevel{track}'

    def combine(self, otherEffect):
        # When combining, take the new effects gag levels and if needed the new effects rounds.
        for track in range(len(BattleGlobals.Tracks)):
            self.setGagLevel(track, getattr(otherEffect, self.getAttrName(track), -1))

        otherRounds = otherEffect.getRounds()
        if otherRounds > self.rounds or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)

    def setGagLevel(self, track, level):
        setattr(self, self.getAttrName(track), level)

    def getGagLevel(self, track):
        return getattr(self, self.getAttrName(track), -1)


class ScapegoatRageStatusEffect(AvatarTakeModifiedDamageStatusEffect, AttackEffectivenessStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = False
        self.rageAmount = extraArgs[0]
        self.inRage = extraArgs[1]
        self.rageAndDesperation = extraArgs[2]
        self.fields = ['rageAmount', 'inRage', 'rageAndDesperation']
        self.damageDealtThisTrack = 0
        self.cogsAlive = 0
        self.takenDirectDamageThisRound = False
        self.roundsSinceTakenDirectDamage = 0

    def getInRage(self):
        return self.inRage

    def setInRage(self, inRage):
        self.inRage = inRage

        suits = [suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]
        if self.getAv() in suits:
            suits.remove(self.getAv())

        if inRage:
            # Reset this counter when we go into rage
            self.roundsSinceTakenDirectDamage = 0
            # Remove all current scapegoat damage modifier status effects on other cogs
            for suit in suits:
                damageModifiers = suit.getStatusEffectsOfType(ScapegoatDamageTakenDownStatusEffect)
                if damageModifiers:
                    for effect in damageModifiers:
                        effect.delete()
        else:
            # Add scapegoat damage modifier status effect to all other cogs
            self.addStatusEffectToAllSuits(SEE.EFFECT_SCAPEGOAT_DAMAGE_TAKEN_DOWN, suits=suits)

    def getRageAmount(self):
        return self.rageAmount

    def setRageAmount(self, rageAmount):
        self.rageAmount = rageAmount

    def handleRoundOver(self):
        if self.inRage:
            self.inRage -= 1
            if self.inRage <= 0:
                # Update lure resistance for exiting rage
                managerEffect = self.getAv().getStatusEffectOfType(ScapegoatManagerStatusEffect)
                if managerEffect is not None:
                    managerEffect.updateLureResistanceForRage(entering=False)
                # Insert suit attack to show cooling down here
                self.getBattleCalc().createAndInsertAttack(
                    AttackEnum.SCAPEGOAT_DEFENSE,
                    {"unlure": True, "invoker": self.getAv()},
                    {"respectPreviousAdditions": True},
                )
                self.setRageAmount(0)
                self.rageAndDesperation = 0
                self.getBattleCalc().sendEvent(BEG.EVENT_LT_SGOAT_RAGE_EXIT)
            return

        if self.takenDirectDamageThisRound:
            self.roundsSinceTakenDirectDamage = 0
        else:
            self.roundsSinceTakenDirectDamage += 1
        # 10 rage increase per round + 5 rage for each round Scapegoat has been "ignored"
        self.incrementRageAmount(10 + 5 * self.roundsSinceTakenDirectDamage)
        if self.rageAmount >= 100:
            self.setInRage(2)
            self.setRageAmount(max(self.rageAmount, 0))
            # Insert suit attack to show becoming enraged and unlure
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.SCAPEGOAT_ENRAGED,
                {"unlure": True, "invoker": self.getAv()},
                {"respectPreviousAdditions": True}
            )
            # Update lure resistance for entering rage
            managerEffect = self.getAv().getStatusEffectOfType(ScapegoatManagerStatusEffect)
            if managerEffect is not None:
                managerEffect.updateLureResistanceForRage(entering=True)
                if managerEffect.resistingLure:
                    self.rageAndDesperation = 1
            self.getBattleCalc().sendEvent(BEG.EVENT_LT_SGOAT_RAGE_ENTER)

    def handleTrackOver(self):
        if not self.inRage and self.damageDealtThisTrack:
            # Take some damage here as "damage absorption"
            damageTaken = self.damageDealtThisTrack

            self.createGeneralAttack(AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE, extraArgs=[damageTaken])

        self.damageDealtThisTrack = 0
        # Update how many cogs are alive at the end of every track
        self.cogsAlive = len([suit for suit in self.getBattleCalc().suits if suit.getHp() > 0])

    def handleBeginRound(self):
        # Reset this flag at beginning of round
        self.takenDirectDamageThisRound = False

        # Do not give 50% damage down if in rage mode.
        if self.inRage:
            return

        suits = [suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]
        # Update how many cogs are alive at the beginning of every round
        self.cogsAlive = len(suits)
        if self.getAv() in suits:
            suits.remove(self.getAv())

        # For each suit in the battle that isnt scapegoat, check if we need to add a damage down effect to them.
        for suit in suits:
            scapegoatDamageDownEffects = suit.getStatusEffectsOfType(ScapegoatDamageTakenDownStatusEffect)
            if not scapegoatDamageDownEffects:
                suit.addStatusEffect(SEE.EFFECT_SCAPEGOAT_DAMAGE_TAKEN_DOWN)

    def receiveGeneralAttackDamage(self, amount):
        self.incrementRageAmount(abs(amount) // 10)

    # Called when any suit is dealt damage by a Toon
    def incrementDamageDealt(self, amount, suit, track):
        # Only add damage dealt this track to absorb if this is not us that was hurt
        if suit is not self.getAv():
            # If its a fire, straight up add +20 rage
            if track == AttackEnum.TOON_FIRE:
                if not self.inRage:
                    self.incrementRageAmount(20)
                return
            # Do some math to figure out how much damage was prevented and deal that to Scapegoat
            percentOfTotalDamage = SEG.StatusEffectAttributes[SEE.EFFECT_SCAPEGOAT_DAMAGE_TAKEN_DOWN]['extraArgs'][0]
            self.damageDealtThisTrack += int(amount * (1 - percentOfTotalDamage) / percentOfTotalDamage)
        # If we are scapegoat, set flag and increase our rage counter by the damage dealt divided by 10
        elif not self.inRage:
            self.takenDirectDamageThisRound = True
            self.incrementRageAmount(abs(amount) // 10)

    def gotLured(self):
        if not self.inRage:
            self.incrementRageAmount(15)

    def gotSoaked(self):
        if not self.inRage:
            self.incrementRageAmount(15)

    def gotSued(self):
        if not self.inRage:
            self.incrementRageAmount(15)

    def incrementRageAmount(self, amount):
        self.rageAmount += amount
        if self.rageAmount > 100:
            self.rageAmount = 100

    # Increase damage of outgoing attacks by 1.3x while in rage.
    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        if self.inRage:
            attackDamage *= 1.3
        return attackDamage

    # Decrease damage of incoming attacks by 30% while in rage.
    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Don't decrease damage taken if he is in desperation mode.
        managerEffect = self.getAv().getStatusEffectOfType(ScapegoatManagerStatusEffect)
        if managerEffect is not None:
            if self.inRage and not managerEffect.resistingLure:
                attackDamage *= 0.7
        return attackDamage

    def getRageAndDesperation(self):
        return self.rageAndDesperation


# Causes the avatar to take a modified amount of damage when attacked (modified for no-show property).
class ScapegoatDamageTakenDownStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False


# endregion

# -=-=-=-=-=-=-=-=-=-=-=-=- #
# Toontorial Status Effects #
# -=-=-=-=-=-=-=-=-=-=-=-=- #
# region
# Desk Jockey's manager
# Makes it so the Desk Jockey only its given target and doesn't attack by default.
class DeskJockeyEffect(CogStatusEffect):
    def __init__(self, *args):
        super().__init__(*args)
        self.wantShow = False
        self.getAv().noRegularAttackRounds = -1
        self.targetId = None

    def setTargetId(self, targetId):
        self.targetId = targetId

    def generateRandomSuitAttack(self, *args, **kwargs):
        # If we don't have a target or if we can't find our target, don't attack.
        if not self.targetId or self.targetId not in self.getBattleCalc().toons:
            return
        toon = simbase.air.doId2do.get(self.targetId)
        if toon:
            kwargs["targets"] = [toon]
            return super().generateRandomSuitAttack(*args, **kwargs)
        return
# endregion

# -=-=-=-=-=-=-=-=-=-=-=- #
# Taskline Status Effects #
# -=-=-=-=-=-=-=-=-=-=-=- #
# region


# Used for the supervisor, keeps him healed every round.
class SupervisorInsuredStatusEffect(SuitHealOverTimeStatusEffect):
    HealAttackType = AttackEnum.LIFE_INSURANCE

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = True

    def applyHeal(self):
        suit = self.getAv()
        # Make sure we're not the only one in the battle.
        # If we're the only one left, kill the status effect.
        if len([suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]) <= 1:
            self.createGeneralAttack(
                AttackEnum.SHOW_HP_TEXT,
                extraArgs=[TTLocalizer.HP_TEXT_POLICY_TERMINATED],
                targetList=[self.getAv()]
            )
            self.delete()
            return

        # If the suit is already at max HP, we don't need a heal.
        healthPercentage = suit.getHp() / suit.getMaxHp()
        if healthPercentage >= self.healthCap:
            return
        # Make sure the suit isn't dead either
        if suit.getHp() <= 0:
            return

        self.getBattleCalc().createAndInsertAttack(
            self.HealAttackType,
            {"unlure": True, "invoker": suit},
            {"respectPreviousAdditions": True},
        )


# An effect that gives full immunity to combo and knockback damage.
class ComboKbImmunityStatusEffect(ComboDamageModifierStatusEffect, KnockbackDamageModifierStatusEffect):

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.combines = True
        self.comboMultiplier, self.kbMultiplier = (0, 0)
        self.fields = ['comboMultiplier', 'kbMultiplier']

# endregion

# -=-=-=-=-=-=-=-=-=-= #
# Event Status Effects #
# -=-=-=-=-=-=-=-=-=-= #
# region


# Status effects regarding the Halloween suits.
class CountErclaimStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.hasLaffSteal = None
        self.wantShow = False
        self.healthCap = 2.0
        self.hpCheck = None

        self.sacrificeHealthCondition = 0.25
        self.sacrificeDamageCondition = 700
        self.sacrificeCooldown = 0
        self.roundsSinceSacrifice = 0
        self.maxRoundsForSomethingToHappen = 5

        self.reviveCooldown = 0
        self.roundsSinceRevive = 0

        self.usedReviveThisTurn = False
        self.usedSacrificeThisTurn = False
        self.becameSkelecogThisTurn = False
        self.usedFire = False

        self.isStreet = False
        if self.isAi():
            if not hasattr(self, 'timesSuitsRevived'):
                # changes based on if this is the street count
                self.isStreet = True
                self.sacrificeDamageCondition = 300
                self.maxRoundsForSomethingToHappen = 3

        self.createLureResistanceStatusEffect()

    def createLaffStealAttack(self, damage, suit):
        if not self.getAv() or suit != self.getAv():
            return
        if not self.hasLaffSteal:
            count = self.getAv()
            # make sure count qualifies for the move
            healthPercentage = suit.getHp() / suit.getMaxHp()
            if healthPercentage >= self.healthCap or suit.getHp() <= 0:
                return
            self.hasLaffSteal = self.addCountAttack(AttackEnum.LAFF_STEAL)
            self.hasLaffSteal.increaseDamageDealt(-damage)
        else:
            self.hasLaffSteal.increaseDamageDealt(-damage)

    def checkForSacrifice(self):
        # Checks to see if we qualify for a sacrifice.
        count = self.getAv()
        if not count:
            return
        # set necessary variables
        self.roundsSinceSacrifice += 1
        if self.sacrificeCooldown > 0:
            self.sacrificeCooldown -= 1
            return
        willSacrifice = False
        # check several things
        newHP = count.getHp()
        maxHp = count.getMaxHp()
        if (newHP / maxHp) < self.sacrificeHealthCondition or \
            (self.hpCheck - newHP) > self.sacrificeDamageCondition or \
            (self.becameSkelecogThisTurn and self.hpCheck + (maxHp - newHP) > self.sacrificeDamageCondition) or \
                self.roundsSinceSacrifice >= self.maxRoundsForSomethingToHappen:
            willSacrifice = True
        # set checks
        self.hpCheck = newHP
        if willSacrifice:
            self.roundsSinceSacrifice = 0
            self.sacrificeCooldown = 2
            minSuits = 3
            if self.isStreet:
                minSuits = 2
                self.sacrificeCooldown = 0
            if self.usedSacrificeThisTurn:
                self.addCountAttack(AttackEnum.QUAKE, index='end')
            elif len([suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]) >= minSuits:
                self.addCountAttack(AttackEnum.SACRIFICE, index='end')
            else:
                self.addCountAttack(AttackEnum.QUAKE, index='end')
            self.usedSacrificeThisTurn = True

    def checkForRevive(self):
        # Checks to see if we qualify for a revive
        count = self.getAv()
        if not count:
            return
        # check several things
        willRevive = False
        aliveSuits = [suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]
        if (self.usedFire or self.roundsSinceRevive >= self.maxRoundsForSomethingToHappen) and not self.usedReviveThisTurn:
            if len(aliveSuits) < 4:
                willRevive = True
        # use da revive
        if willRevive and not self.isStreet:
            self.usedReviveThisTurn = True
            self.roundsSinceRevive = 0
            self.reviveCooldown = 2
            self.addCountAttack(AttackEnum.RISE_FROM_THE_SCRAP, index='end')

    def addCountAttack(self, attackType, index=None):
        # Adds a count attack.
        count = self.getAv()
        if not count:
            return
        from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import createAttack
        attack = createAttack(attackType, unlure=True, invoker=count)
        if not index:
            self.getBattleCalc().insertAttack(attack, respectPreviousAdditions=True, adjust=True)
        elif index == 'end':
            self.getBattleCalc().insertAttack(attack, "end")
        return attack

    def enterRevive(self, suit):
        # Set variables regarding what to do once Erclaim revives.
        if not self.getAv() or suit != self.getAv():
            return
        self.becameSkelecogThisTurn = True
        self.attemptScopeCreep()
        self.sacrificeCooldown = 0
        self.reviveCooldown = 0

    def attemptScopeCreep(self):
        # Attempts to add a scope creep.
        if not self.isStreet:
            return
        calc = self.getBattleCalc()
        creepEffect = calc.getSuitEffectOfType(self.getAv(), CountCreepStatusEffect)
        if creepEffect:
            if creepEffect.getMultiplier() == creepEffect.multiplierStep[1]:
                return
        self.addCountAttack(AttackEnum.SCOPE_CREEP, index='end')

    def beginRound(self):
        # Set variables based on when the round starts.
        count = self.getAv()
        self.hpCheck = count.getMaxHp()
        self.becameSkelecogThisTurn = False
        self.usedFire = False
        self.usedReviveThisTurn = False
        self.usedSacrificeThisTurn = False
        self.hasLaffSteal = None

    def forceRevive(self):
        # Called when a toon uses fire.
        self.usedFire = True


class CountCreepStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        if not extraArgs:
            extraArgs = [0]
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True
        self.timesCalled = 0
        self.multiplierStep = (
            0.90,  # start
            0.60,  # max
            -0.05  # increment
        )

    def combine(self, otherEffect):
        pass

    def updateMultiplier(self, creepCount):
        # Update the multiplier.
        self.timesCalled = min(creepCount, 100)
        self.multiplier = self.multiplierStep[0]
        didNotPass = True
        for _ in range(self.timesCalled):
            self.incMultiplier(self.multiplierStep[2])
        if self.getMultiplier() < self.multiplierStep[1]:
            if abs(self.getMultiplier() - self.multiplierStep[1]) > abs(self.multiplierStep[2] / 2):
                didNotPass = False
            self.setMultiplier(self.multiplierStep[1])
        return didNotPass


class CountErfitStatusEffect(StatusEffectBase, MultiTimer, DamageListener):

    tier2ReviveDamage = {
        1: 7,
        2: 15,
        3: 20,
        4: 25,
        5: 30,
        6: 34,
        7: 39,
        8: 44,
        9: 49,
        10: 54,
        11: 59,
    }
    damageCap = 1000  # damage required to incite an extra gains from the scrap

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False  # ensures the client doesn't get communicated this effect
        self.personalTrainerRoundCount = 0
        self.hasRevived = False

        # Add multi-timer
        MultiTimer.__init__(self, numberOfTimers=2)
        self.inheritedEventDefinitions += [SEE.DEFINITION_MULTI_TIMER]
        self.setRoundCount(0, 4)

        # Add damage listener
        DamageListener.__init__(self)
        self.inheritedEventDefinitions += [SEE.DEFINITION_DAMAGE_LISTENER]

        # Erfit Attacks
        self.proToonShakeAttack = None

        # Have a little lure resistance as a treat
        self.createLureResistanceStatusEffect()

    def hasRevivedThisTurn(self):
        """
        Determines if Erfit has revived specifically this turn.
        """
        return self.getBattleCalc().eventsSentThisRound(BEG.EVENT_SUIT_REVIVED) > 0

    def getTier(self):
        """
        Gets the tier of the Erfit battle.
        """
        count = self.getAv()
        if not count:
            return None

        return (count.level // 2) + 1

    def doSpecialRevive(self):
        """
        Do a silly special revive move!
        """
        count = self.getAv()
        if not count:
            return
        if self.hasRevived:
            # probably will never happen, but better safe than sorry?
            return
        if count.getHp() <= 0:
            # he's dead jim
            return
        # Below originally used getBattleCalc().createSuitAttackOfType(), but that isn't implemented for the client
        # Possibly work on own implementation?
        self.createGeneralAttack(
            AttackEnum.ERFIT_REVIVE,
            extraArgs=[self.tier2ReviveDamage[self.getTier()]]
        )
        # Originally used getBattleCalc().insertAttack() here, but it was not needed here
        self.hasRevived = True
        count.addVisualEffect(VisualEffectEnum.ERFIT_REVIVE)

        # no suits in this battle will be able to attack for the rest of the turn
        self.addStatusEffectToAllSuits(SEE.EFFECT_CANT_ATTACK)

        # erfit will take 5x damage for the rest of battle
        count.addStatusEffect(SEE.EFFECT_ERFIT_GODMODE)

    def doCheats(self):
        """
        Event: EVENT_NORMAL_ATTACKS_OVER
        """
        self.attemptGains()
        self.attemptPersonalTrainer()

    def attemptGains(self):
        # Trigger 1: Deal an obscene amount of damage to cogs this turn.
        if self.getSuitDamageTotal() >= self.damageCap and self.getRoundCount(0) > 3:
            # Run gains.
            self.addErfitAttack(AttackEnum.GAINS_FROM_THE_SCRAP)
            # Reset this round timer.
            self.setRoundCount(0, 0)

        # Trigger 2: Runs every four turns.
        if self.doRoundCycleCheck(1, 4, 0):
            self.addErfitAttack(AttackEnum.GAINS_FROM_THE_SCRAP)

    def attemptPersonalTrainer(self):
        """
        Attempts to use Personal Trainer.
        Only can be used when three turns pass with <4 cogs in battle.
        """
        self.personalTrainerRoundCount += 1
        if self.personalTrainerRoundCount >= 3:
            # It's been 3 rounds with <4 cogs in the battle. Time to summon.
            self.addErfitAttack(AttackEnum.PERSONAL_TRAINER, index='end')
            self.personalTrainerRoundCount = 0

    def addErfitAttack(self, attackType, extraArgs=None, index=None, adjust=True, respectPrevious=True):
        # Adds a count attack.
        if not self.getAv():
            return
        if self.getAv().getHp() <= 0:
            return
        extraArgs = extraArgs or []

        # Since we are adding a new attack, we want to enable the ability
        # for a Pro-Toon Shake to happen again, in case it happened
        # earlier in the turn.
        self.proToonShakeAttack = None

        # Now we'll go ahead and do some magic to create the attack.
        count = self.getAv()
        if not count:
            return
        from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import createAttack
        attack = createAttack(attackType, invoker=count, extraArgs=extraArgs, unlure=True)
        if not index:
            self.getBattleCalc().insertAttack(attack,
            respectPreviousAdditions=respectPrevious, adjust=adjust)
        elif index == 'start':
            self.getBattleCalc().insertAttack(attack,
            respectPreviousAdditions=respectPrevious, adjust=False)
        elif index == 'end':
            self.getBattleCalc().insertAttack(attack, "end")
        return attack

    def createHydrationCheckAttack(self):
        # Pick a random toon from the battle to apply the Hydrated effect.
        # Prefer to select toons who do not currently have the effect.
        # If everyone already has it, pick a random toon.
        count = self.getAv()
        if not count:
            return
        if count.getHp() <= 0:
            return
        activeToons = self.getBattleCalc().getAliveToons()
        if not activeToons:
            return
        self.addErfitAttack(AttackEnum.HYDRATION_CHECK,
                            extraArgs=[random.choice(activeToons)], adjust=False)
        # attack = self.getBattleCalc().createSuitAttackOfType(count, AttackEnum.HYDRATION_CHECK,
        #                                                      [random.choice(activeToons).doId], unlure=True)
        # attackOrder.insert(0, attack)

    def createProToonShake(self, damage, suit):
        """
        Whenever Erfit deals damage to a Toon, create a Pro-Toon Shake attack.
        """
        if not self.getAv() or suit != self.getAv():
            # Erfit is not around, or this suit is not Erfit.
            return
        if self.getAv().getHp() <= 0:
            return

        if not self.proToonShakeAttack:
            # Create the attack.
            self.proToonShakeAttack = self.addErfitAttack(AttackEnum.PROTOON_SHAKE, respectPrevious=True)

        # Increment the damage on the attack.
        self.proToonShakeAttack.increaseDamageDealt(-damage)

    def beginRound(self):
        # Set variables based on when the round starts.
        self.proToonShakeAttack = None

        # If there are 4+ cogs in the battle, reset PT round count.
        if len(self.getBattleCalc().suits) >= 4:
            self.personalTrainerRoundCount = 0


# Overcharged! Applies to a Suit that can receive the Overcharge perk.
class OverchargeStatusEffect(LureResistanceStatusEffect,
                             MultiplicativeDamageBoostStatusEffect,
                             MinibossResistancesStatusEffect):

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        LureResistanceStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.amount = extraArgs[0]
        self.multiplier = extraArgs[1]
        self.rounding = extraArgs[2]
        self.hpRequired = extraArgs[3]
        self.minibossImmunitiesActive = False
        self.fields = ['amount', 'multiplier', 'rounding', 'hpRequired', 'minibossImmunitiesActive']

        # properties of the effect itself
        self.wantShow = True
        self.active = False
        self.rounds = SEG.NO_ROUNDS
        self.damageMult = self.multiplier

        # AI Only
        if self.avProfile.battleListener:
            # Set the multiplier to Bad
            self.updateMultiplier()
            # They have a sue effect, delete it.
            sueEffect = self.avProfile.getStatusEffectOfType(SueStatusEffect)
            if sueEffect:
                sueEffect.delete()

    def isVisible(self):
        self.checkAvHp()
        return self.active

    def checkAvHp(self):
        """
        Checks the Suit's HP.
        If it's above the threshold, update the lure resistance
        and update the suit's damage multiplier.
        """
        suit = self.getAv()
        if not suit or suit.getHp() <= 0:
            return
        healthPercentage = suit.getHealthPercentage() * 1.001  # lil extra in case of rounding
        self.active = healthPercentage >= self.hpRequired
        self.minibossImmunitiesActive = self.active
        if self.avProfile.battleListener:
            self.updateMultiplier()
        if self.active:
            # Kill sues, and lower lure.
            if self.avProfile.battleListener:
                # They have a sue effect, delete it.
                sueEffect = self.avProfile.getStatusEffectOfType(SueStatusEffect)
                if sueEffect:
                    sueEffect.delete()

                # If they have lure, lower its rounds.
                lureEffect = self.avProfile.getStatusEffectOfType(LureStatusEffect)
                if lureEffect:
                    if lureEffect.getRounds() > 2:
                        lureEffect.setRounds(2, adjust=False)

    def updateMultiplier(self):
        """
        Updates the Suit's damage multiplier.
        """
        if self.active:
            self.setMultiplier(self.damageMult)
        else:
            self.setMultiplier(1.0)

    def handleLureResistance(self, suit, lureResistance):
        if not self.active:
            return lureResistance
        return min(lureResistance, self.amount)


# The manager effect for the Overclocked Foreman.
class OverclockedForemanStatusEffect(StatusEffectBase, MultiTimer):
    """
    Enum values for what type of Foreman this is.
    """
    BELLOW = 0
    ANTERGY = 1
    STEADFAST = 2
    COMPENSATION = 3
    DESTRUCTION = 4
    PRETHINKING = 5
    REBALANCE = 6
    SACRIFICE = 7
    PRISMATIC = 8

    PRISMATIC_HP = 999
    PRISMATIC_MOVES_BLOCKED = 3

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.visualEffectEnums = [VisualEffectEnum.OC_FOREMAN]

        # Add a multi-timer effect.
        MultiTimer.__init__(self, numberOfTimers=4)
        self.inheritedEventDefinitions += [SEE.DEFINITION_MULTI_TIMER]

        # Set the type parameters of the Foreman.
        self.type = None if not extraArgs else extraArgs[0]
        self.fields = ['type']
        self.callback = None
        self.activated = False  # field for various compensations
        self.prismaticBlocklist = []

        # Decide the type of the Overclocked Foreman.
        if self.isAi() and self.type is None:
            self.type = self.decideType()

            # If we're prismatic, up our health.
            if self.getType() == self.PRISMATIC:
                self.getAv().b_setMaxHp(self.PRISMATIC_HP)

        # Set the callback to be called.
        self.declareCallbacks()

    def getType(self):
        return self.type

    def setCallback(self, callback):
        self.callback = callback

    """
    Active listeners
    """

    def onRoundStart(self):
        """
        Called at the start of each round.
        Prismatic Foreman will calculate its blocklist.
        """
        if self.getType() != self.PRISMATIC:
            # Blocklist only calculated on prismatic.
            return

        # Calculate moves to blocklist for prismatic.
        self.prismaticBlocklist = random.sample([self.BELLOW, self.ANTERGY, self.STEADFAST, self.COMPENSATION,
                                                 self.PRETHINKING, self.REBALANCE, self.SACRIFICE],
                                                self.PRISMATIC_MOVES_BLOCKED)

    def onEndToonTrack(self, attackTrack, attackList):
        """
        Called on the end of every Toon Track calculation.
        :param attackTrack: The track that was used.
        :param attackList: A list of each attack in the track.
        """
        if self.getType() == self.DESTRUCTION:
            # Do destruction.
            self.compensationDestruction(attackTrack, attackList)
        if self.getType() == self.REBALANCE or (self.getType() == self.PRISMATIC and self.REBALANCE not in self.prismaticBlocklist):
            # Do rebalance.
            self.compensationRebalance(attackList)
        if attackTrack == AttackEnum.TOON_SOUND:
            # Punish for sound usage.
            self.punishSound()
        if attackTrack == AttackEnum.TOON_SQUIRT and \
                self.getType() == self.BELLOW or (self.getType() == self.PRISMATIC and self.BELLOW not in self.prismaticBlocklist):
            # Punish for soak usage.
            self.compensationBellow(None, force=True, index=True)

    def onAttackOrder(self, attackOrder):
        """
        Called upon the creation of the attack order.
        """
        # If we have a set callback, run it.
        if self.callback:
            self.callback(attackOrder)

    """
    Initiation Methods
    """

    def decideType(self):
        """
        Decides the type of the Foreman.
        """
        # If this foreman is not the boss, pick a random field.
        if not self.getAv().boss:
            return random.choice([self.BELLOW, self.ANTERGY, self.STEADFAST, self.COMPENSATION,
                                  self.DESTRUCTION, self.PRETHINKING, self.REBALANCE, self.SACRIFICE])
        else:
            # If it is the boss, it is prismatic.
            return self.PRISMATIC

    def declareCallbacks(self):
        """
        Declares the callbacks to be ran at the start of each turn.
        """
        callbackDict = {
            self.BELLOW: self.compensationBellow,
            self.ANTERGY: self.compensationAntergy,
            self.STEADFAST: self.compensationSteadfast,
            self.COMPENSATION: self.compensationCompensation,
            # self.DESTRUCTION is not round-based.
            self.PRETHINKING: self.compensationPrethinking,
            # self.REBALANCE is not round-based.
            self.SACRIFICE: self.compensationSacrifice,
            self.PRISMATIC: self.compensationPrismatic,
        }.get(self.type)
        self.setCallback(callbackDict)

    def compensationBellow(self, _, force=False, index=False):
        """
        Runs the Bellow Compensation.
        Does Bayou Bellow once every two turns.
        """
        # Round logic to make sure we don't go too early.
        if not force:
            if self.getRoundCount(0) < 2:
                return
        self.setRoundCount(0, 0)

        # Send a bash in advance, so that when we do BayouBash, it'll automatically be BayouBellow.
        self.getBattleCalc().sendEvent(BEG.EVENT_LT_LGATOR_BAYOU_BASH)

        # Add a bellow to the round order.
        self.createAttack(AttackEnum.BAYOU_BASH, unlure=True)

    def compensationAntergy(self, _):
        """
        Runs the Antergy Compensation.
        At the start of the turn, gives the Suit massive combo/kb resist.
        """
        # Only apply this on round one.
        if self.getAv().getStatusEffectOfId(SEE.EFFECT_COMBO_KB_IMMUNITY):
            return

        # Give the Suit the status effect.
        self.getAv().addStatusEffect(SEE.EFFECT_COMBO_KB_IMMUNITY)

    def compensationSteadfast(self, _):
        """
        Runs the Steadfast Compensation.
        This suit has full lure immunity.
        """
        # Only apply this on round one.
        if self.getAv().getStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE):
            return

        # Give the Suit the status effect.
        lureEffect = SEG.createStatusEffect(self.getAv(), SEE.EFFECT_LURE_RESISTANCE)
        lureEffect.setAmount(-1)
        self.getAv().addStatusEffect(SEE.EFFECT_LURE_RESISTANCE, lureEffect)

    def compensationCompensation(self, _):
        """
        Runs the Compensation Compensation.
        Gives this suit an extra stack of Compensation at the end of every single turn.
        """
        # Add one stack of workers comp with the intent flag of 2.
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.WORKERS_COMP,
            {"invoker": self.getAv(), "unlure": True, "extraArgs": [1, 2]},
            {"mode": "end"}
        )

    def compensationDestruction(self, attackTrack, attackList):
        """
        Runs the Destruction Compensation.
        Doesn't listen to round order, but immediately
        implodes whenever any Toon uses a Gag.
        """
        if not attackList or self.activated:
            return

        # Set variables in advance for loop.
        attack = None
        track = None
        level = None
        damage = None
        canAttack = False

        from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import \
            ToonAttackAI

        # Get the arguments for the attack.
        for attack in attackList:
            attack: ToonAttackAI
            track = attack.attackType
            level = attack.level
            isGroup = attack.isGroup
            damage = 9999

            # Can we create the attack?
            canAttack = False

            if self.getAv() in attack.targets:
                # The suit is being attacked.
                canAttack = True

            if attack.attackType == AttackEnum.TOON_HEAL and isGroup:
                # Group Toon-Up is being used.
                canAttack = True

            if not attack.landed:
                # The attack missed.
                canAttack = False

            if canAttack:
                # We should be ready to attack!
                continue

        if not canAttack:
            # Nope, we're not ready to attack yet.
            return

        # Now create the attack.
        self.activated = True
        if attack:
            from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import createAttack
            attack = createAttack(
                AttackEnum.OVERCLOCKED_FOREMAN_DESTRUCTION,
                extraArgs=[damage, track, level],
                targets=[self.getAv()]
            )
            self.getBattleCalc().insertAttack(attack, adjust=True)

    def compensationPrethinking(self, attackOrder):
        """
        Runs the Prethinking Compensation.
        Dodges Drop.
        """
        # Lure self to dodge a Drop.
        gagCheck = self.__getToonGagUsageIndex(attackOrder, AttackEnum.TOON_DROP)
        if gagCheck is not None:
            self.lureSelf(attackOrder.index(gagCheck))
            self.unlureSelfAfterToonRound(attackOrder)

    def compensationRebalance(self, attackList):
        """
        Runs the Rebalance Compensation.
        Adds a stack of Compensation when the Cog receives MFL.
        """
        if not attackList or self.activated:
            return

        # Set variables in advance for loop.
        attackCount = 0

        from toontown.clashbattle.battle.attacks.server.toon.ToonAttackAI import \
            ToonAttackAI

        # Get the arguments for the attack.
        for attack in attackList:
            attack: ToonAttackAI

            # Can we create the attack?
            if not (self.getAv() in attack.targets):
                # The suit is not being attacked.
                continue

            if attack.attackType != AttackEnum.TOON_THROW:
                # Throw is not being used.
                continue

            if not attack.landed:
                # The attack missed.
                continue

            if attack.hasTrackBonus:
                # The attack was prestiged.
                attackCount += 1

        # Now create the attack.
        if attackCount:
            # Put the worker's comp in right now, with intent 3.
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.WORKERS_COMP,
                {"invoker": self.getAv(), "extraArgs": [attackCount, 3], "unlure": True},
                {"adjust": True}
            )

    def compensationSacrifice(self, _):
        """
        Runs the Sacrifice Compensation.
        Does Sacrifice once every two turns.
        """
        # Round logic to make sure we don't go too early.
        if self.getRoundCount(3) < 2:
            return
        self.setRoundCount(3, 0)

        # Add a sacrifice to the round order.
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.SACRIFICE,
            {"invoker": self.getAv(), "unlure": True, "extraArgs": [1]},
            {"mode": "end"}
        )

    def compensationPrismatic(self, _):
        """
        Prismatic Foreman. The ultimate one.
        Does most compensations immediately!!
        """
        if self.BELLOW not in self.prismaticBlocklist:
            self.compensationBellow(_)

        if self.ANTERGY not in self.prismaticBlocklist:
            self.compensationAntergy(_)
        else:
            # remove combo/kb resist if we have it
            self.getAv().removeStatusEffectOfId(SEE.EFFECT_COMBO_KB_IMMUNITY)

        if self.STEADFAST not in self.prismaticBlocklist:
            self.compensationSteadfast(_)
        else:
            # remove lure immunity if we have it
            self.getAv().removeStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE)

        if self.COMPENSATION not in self.prismaticBlocklist:
            self.compensationCompensation(_)
        if self.PRETHINKING not in self.prismaticBlocklist:
            self.compensationPrethinking(_)
        if self.SACRIFICE not in self.prismaticBlocklist:
            self.compensationSacrifice(_)

    """
    Other Methods
    """

    def punishSound(self):
        """
        Sound users shalt be punished.
        Give em' an extra stack of workers comp. Just for fun!
        """
        # Add one stack of workers comp with the intent flag of 1.
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.WORKERS_COMP,
            {"invoker": self.getAv(), "extraArgs": [1, 1], "unlure": True},
            {"adjust": True}
        ),

    """
    Gag Avoider Methods
    """

    def __getToonGagUsageIndex(self, track, trackId):
        """Returns the gag track index in an attack track."""
        for gagTuple in track:
            if type(gagTuple) != list:
                continue
            if gagTuple[0] == trackId:
                # make sure that we are being targeted by any of these gags
                av = self.getAv()
                for attack in gagTuple[1]:
                    if attack.target == av.doId or av in attack.targets:
                        return gagTuple
        return None

    def lureSelf(self, attackIndex):
        """Lures the suit."""
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.SUIT_LURE,
            {"targets": [self.getAv()], "extraArgs": [2]},
            {"index": attackIndex, "adjust": False},
        )

    def unlureSelf(self, attackIndex):
        """Unlures the suit."""
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.SUIT_UNLURE,
            {"targets": [self.getAv()]},
            {"index": attackIndex},
        )

    def unlureSelfAfterToonRound(self, track):
        """
        Unlures self immediately prior to the Cog attack round.
        Looks for the first usage of a Gag track going backwards from the attack order,
        and then places the unlure immediately after that.
        """
        gagCheck = None
        for gagTuple in track[::-1]:
            if type(gagTuple) == list:
                gagCheck = gagTuple
                break
        if gagCheck is not None:
            self.unlureSelf(track.index(gagCheck))
# endregion

# -=-=-=-=-=-= #
# Flag Classes #
# -=-=-=-=-=-= #
# region

class FlagBase(StatusEffectBase):
    """
    A flag acts as a "dummy" status effect.

    A BattleAvatar can be given them exactly like any
    other status effect, but they won't do anything.

    Their main use is simply that: as flags.
    Certain attacks or moves can look for a BattleAvatar
    with a "flag" to induce separate behavior.
    """

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.combines = False
        self.rounds = SEG.NO_ROUNDS


class FlagEmpower(FlagBase):
    """
    This flag is an "empower" flag.
    Certain attacks/effects/etc. can look to this flag
    in order to be empowered based on some avatar.

    The naming is only convention.
    """
    pass


class HiddenStatusEffect(StatusEffectBase):
    def isVisible(self):
        return False


class GagTracksDisabled(HiddenStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = []
        # Fill in fields with all gag tracks
        self.gagTracks = []
        for track in range(len(BattleGlobals.Tracks)):
            setattr(self, self.getAttrName(track), self.extraArgs[track])
            self.gagTracks.append(getattr(self, self.getAttrName(track), 0))
            self.fields.append(self.getAttrName(track))

    @staticmethod
    def getAttrName(track):
        return f'gagTrack{track}'

    def combine(self, otherEffect):
        # When combining, take the new effects gag levels and if needed the new effects rounds.
        for track in range(len(BattleGlobals.Tracks)):
            self.setGagTrackDisabled(track, getattr(otherEffect, self.getAttrName(track), 0))

        otherRounds = otherEffect.getRounds()
        if otherRounds > self.rounds or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)

    def setGagTrackDisabled(self, track, disabled):
        setattr(self, self.getAttrName(track), disabled)

    def getGagTrackDisabled(self, track):
        return getattr(self, self.getAttrName(track), 0)

    def getAllDisabledTracks(self):
        return [AttackEnum(int(round(gagTrack))) for gagTrack in range(len(BattleGlobals.Tracks)) if self.getGagTrackDisabled(gagTrack)]


class GagLevelsDisabled(HiddenStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = []
        # Fill in fields with all gag levels
        self.gagLevels = []
        for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1):
            setattr(self, self.getAttrName(level), self.extraArgs[level])
            self.gagLevels.append(getattr(self, self.getAttrName(level), 0))
            self.fields.append(self.getAttrName(level))

    @staticmethod
    def getAttrName(track):
        return f'gagLevel{track}'

    def combine(self, otherEffect):
        # When combining, take the new effects gag levels and if needed the new effects rounds.
        for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1):
            self.setGagLevelDisabled(level, getattr(otherEffect, self.getAttrName(level), 0))

        otherRounds = otherEffect.getRounds()
        if otherRounds > self.rounds or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)

    def setGagLevelDisabled(self, level, disabled):
        setattr(self, self.getAttrName(level), disabled)

    def getGagLevelDisabled(self, level):
        return getattr(self, self.getAttrName(level), 0)

    def getAllDisabledLevels(self):
        return [level for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1) if self.getGagLevelDisabled(level)]


class MixedGagTracksLevelsDisabled(HiddenStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = []
        # Fill in fields with all gag tracks AND levels
        self.gagsDisabled = []
        for track in range(len(BattleGlobals.Tracks)):
            for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1):
                setattr(self, self.getAttrName(track, level), self.extraArgs[(track * (BattleGlobals.MAX_LEVEL_INDEX + 1)) + level])
                self.gagsDisabled.append(getattr(self, self.getAttrName(track, level), 0))
                self.fields.append(self.getAttrName(track, level))

    @staticmethod
    def getAttrName(track, level):
        return f'gagTrack{track}_Level{level}'

    def combine(self, otherEffect):
        # When combining, take the new effects gag levels and if needed the new effects rounds.
        for track in range(len(BattleGlobals.Tracks)):
            for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1):
                self.setGagTrackLevelDisabled(track, level, getattr(otherEffect, self.getAttrName(track, level), 0))

        otherRounds = otherEffect.getRounds()
        if otherRounds > self.rounds or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)

    def setGagTrackLevelDisabled(self, track, level, disabled):
        setattr(self, self.getAttrName(track, level), disabled)

    def getGagTrackLevelDisabled(self, track, level):
        return getattr(self, self.getAttrName(track, level), 0)

    def getAllDisabledTracksLevels(self):
        returnList = []
        for track in range(len(BattleGlobals.Tracks)):
            for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1):
                if self.getGagTrackLevelDisabled(track, level):
                    returnList.append((AttackEnum(int(round(track))), level))

        return returnList


class CounterfeitContainer(HiddenStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = []
        self.combines = False
        # Fill in fields with all gag tracks AND levels
        self.gags = []
        for track in range(len(BattleGlobals.Tracks)):
            for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1):
                setattr(self, self.getAttrName(track, level), self.extraArgs[(track * (BattleGlobals.MAX_LEVEL_INDEX + 1)) + level])
                self.gags.append(getattr(self, self.getAttrName(track, level), 0))
                self.fields.append(self.getAttrName(track, level))

    @staticmethod
    def getAttrName(track, level):
        return f'gagTrack{track}_Level{level}'

    def setGagTrackLevel(self, track, level, value):
        setattr(self, self.getAttrName(track, level), value)

    def getGagTrackLevel(self, track, level):
        return getattr(self, self.getAttrName(track, level), 0)

    def getAllGagTrackLevels(self):
        returnDict = {}
        for track in range(len(BattleGlobals.Tracks)):
            for level in range(BattleGlobals.MAX_LEVEL_INDEX + 1):
                if self.getGagTrackLevel(track, level):
                    returnList[(AttackEnum(int(round(track))), level)] = self.getGagTrackLevel(track, level)

        return returnDict


# endregion

# -=-=-=-=-=-=-=-=-=-=-=-=-=- #
# Street Mercs Status Effects #
# -=-=-=-=-=-=-=-=-=-=-=-=-=- #
# region
# Duck shuffler's manager
class DuckShufflerEffect(CogStatusEffect):
    class RollChoices(IntEnum):
        Ducks = auto()
        Sevens = auto()
        Beans = auto()
        Bar = auto()
        Bust = auto()

    # The percentage chance of each roll being gotten.
    RollWeights = {
        RollChoices.Ducks:  0.05,
        RollChoices.Sevens: 0.20,
        RollChoices.Beans:  0.10,
        RollChoices.Bar:    0.35,
        RollChoices.Bust:   0.30,
    }

    # What attacks are generated upon roll success.
    RollToAttack = {
        RollChoices.Ducks:  AttackEnum.WAGER_DUCKS,
        RollChoices.Sevens: AttackEnum.WAGER_SEVENS,
        RollChoices.Beans:  AttackEnum.WAGER_BEANS,
        RollChoices.Bar:    AttackEnum.WAGER_BAR,
        RollChoices.Bust:   AttackEnum.WAGER_BUST,
    }

    # If you want to force a roll choice for testing purposes.
    DebugRollChoice = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = False

    def rollSlots(self):
        # Grab the proper weights for each roll type.
        rollWeights = [self.RollWeights[rollType] for rollType in list(self.RollWeights.keys())]

        # Give us a random roll from the possible options.
        rollChoice = self.DebugRollChoice or random.choices(list(self.RollWeights.keys()), weights=rollWeights)[0]

        # Add this attack to the end of the round.
        self.getBattleCalc().createAndInsertAttack(
            self.RollToAttack[rollChoice],
            {"invoker": self.getAv(), "unlure": True},
            {"mode": "end"}
        )

    def weDied(self):
        # Hey. We died.
        # Remove all of the toon become ducks visual effects from all toons
        for toon in self.getBattleCalc().getAllToons():
            toon.removeVisualEffectOfId(VisualEffectEnum.TOON_BECOME_DUCK)


# Deep Divers's manager
# Handles the Chosen One Cog and other fun stuff
class DeepDiverEffect(CogStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mySavior = None
        self.doveThisTurn = False
        self.needSinkOrSwim = False
        self.checkedSinkOrSwimThisTurn = False
        self.currentlyDiving = False
        self.diveDisabledTurns = -1

    def handleBeginRound(self):
        if self.diveDisabledTurns >= 1:
            self.diveDisabledTurns -= 1
        self.doveThisTurn = False
        self.checkedSinkOrSwimThisTurn = False
        self.currentlyDiving = bool(self.av.getStatusEffectOfId(SEE.EFFECT_DIVING))
        # Need sink or swim if we are diving and we don't have a savior cog
        self.needSinkOrSwim = self.currentlyDiving and self.mySavior is None

    def handleAbilities(self):
        # First check if we have a dive we have queued.
        self.checkDive()
        # Now check if we need to Kill the Toons with a DOT
        self.checkToonDOT()
        # After, check if we need to sink or swim.
        self.checkSinkOrSwim()

    def checkDive(self):
        # Don't dive if we're already diving
        if self.currentlyDiving:
            return
        # After killing a promoted Cog, dive will be disabled for the turn after.
        if self.diveDisabledTurns > 0:
            return

        # Check if we have a special boy to promote
        otherSuits = [suit for suit in self.getBattleCalc().getAliveCogs() if suit is not self.av]
        specialBoy = None
        for suit in otherSuits:
            if suit.getActualLevel() < 7 or not suit.isElite:
                specialBoy = suit
                break

        # Add a dive now
        self.createAttack(attackType=AttackEnum.DIVE, insertMethod='end', unlure=True, extraArgs=[bool(specialBoy)])
        self.doveThisTurn = True

        if specialBoy:
            # We have a special boy, promote him and save him.
            self.mySavior = specialBoy
            self.createGeneralAttack(attackType=AttackEnum.DEEP_DIVER_PROMOTE_FODDER, extraArgs=[specialBoy.doId],
                                     insertKwargs=dict(mode='end'))

    def checkToonDOT(self):
        # Don't do the DOT if we are gonna sink or swim this turn
        if self.needSinkOrSwim:
            return

        # If we're diving, make all of the toons take a small bit of DOT damage
        if self.currentlyDiving or self.doveThisTurn:
            self.createGeneralAttack(attackType=AttackEnum.DEEP_DIVER_DIVING_DOT,
                                     targetList=[self.getBattle().getToon(toonId) for toonId in self.getBattle().activeToons],
                                     extraArgs=[-5], insertKwargs=dict(mode='end'))

    def checkSinkOrSwim(self):
        # We have a flag that we need to do this attack, go ahead and do it
        if self.needSinkOrSwim:
            self.createAttack(attackType=AttackEnum.SINK_OR_SWIM, insertMethod='end', unlure=True)
            self.mySavior = None

        self.checkedSinkOrSwimThisTurn = True

    def handleSuitDied(self, suit):
        # Check if our saviors exists and if the cog is our savior.
        if self.mySavior is None or suit is not self.mySavior:
            return

        # The cog was our savior. THEY're DEAD!
        # Now we need to murder the toons, mark us as so.
        self.needSinkOrSwim = True
        # This will disable their dive for one turn, giving them a fully free turn regardless of
        # who is in the battle.
        self.diveDisabledTurns = 2
        # If she has somehow already checked for sink or swim, check it again!!!!
        if self.checkedSinkOrSwimThisTurn:
            self.checkSinkOrSwim()



# Deep Diver's Diving effect
class DivingStatusEffect(UntouchableStatusEffect, IgnoreVisualEffectMovieUnapplyEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hasSavior = self.extraArgs[0]
        self.fields = ['hasSavior']
        if self.isAi():
            self.av.noRegularAttackRounds = -1

    def setHasSavior(self, hasSavior):
        self.hasSavior = hasSavior

    @staticmethod
    def canBeTrapped():
        return True


# Gatekeeper's Front Line
class GatekeeperManagerStatusEffect(CogStatusEffect, AttackIOModificationStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = True
        self.suitsGivenHealthBoost = []
        self.damageBoostThisRound = 0
        # Do an initial "round begin" to get the damage down on the other avatars,
        # Since this could happen anytime after the beginning of a turn
        # but before the end of it
        if self.isAi():
            self.addEffectToSuits()

    def cleanup(self):
        super().cleanup()
        self.suitsGivenHealthBoost = []

    def addEffectToSuits(self):
        if not self.isAi():
            return

        currentSuits = [suit for suit in self.getBattle().activeSuits if suit.getHp() > 0]
        for suit in currentSuits:
            if suit is self.getAv():
                continue
            if suit.doId not in self.suitsGivenHealthBoost and not suit.getStatusEffectOfId(SEE.EFFECT_GATEKEEPER_FODDER_BONUS):
                suit.addStatusEffect(SEE.EFFECT_GATEKEEPER_FODDER_BONUS)
                # Also give them lure resistance for the funny
                suit.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE,
                                     SEG.createStatusEffect(suit, SEE.EFFECT_LURE_RESISTANCE, extraArgs=[2]))
                self.suitsGivenHealthBoost.append(suit.doId)

    def handleSuitDied(self, suit):
        fodderBonus: AdditiveDamageBoostStatusEffect = suit.getStatusEffectOfId(SEE.EFFECT_GATEKEEPER_FODDER_BONUS)
        if fodderBonus:
            self.damageBoostThisRound += (fodderBonus.getMultiplier() * 2)

    def normalAttacksOver(self):
        # If we have a damage boost we need to give out, go ahead and do that
        if self.damageBoostThisRound:
            self.createGeneralAttack(AttackEnum.GATEKEEPER_FODDER_KILL_PIERCE, extraArgs=[self.damageBoostThisRound])

        self.damageBoostThisRound = 0

        # Now add a "wake up" attack to pick a random lured cog and wake them up
        self.createAttack(AttackEnum.GATEKEEPER_JUMP_UNLURE_FODDER)

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # We ignore the damage down if our invoker has the toon pierce effect
        if not invoker.getStatusEffectOfId(SEE.EFFECT_GATEKEEPER_TOON_PIERCE):
            attackDamage *= self.defenseMultiplier
        return attackDamage


# Effect that fodders in the Gatekeeper fight receive
class GatekeeperFodderBonusEffect(AdditiveDamageBoostStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        AdditiveDamageBoostStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.boostAmount = self.extraArgs[0]
        self.multiplier = self.extraArgs[1]
        self.fields = ['boostAmount', 'multiplier']

        # Was being weird with the health boost effect by itself so I am just doing this here
        from toontown.clashsuit.suit.SuitBase import SuitBase
        if self.isAi() and isinstance(self.av, SuitBase):
            self.av.b_setMaxHp(self.av.getMaxHp() + self.boostAmount)

    def onRoundEnd(self):
        # Boost damage at the end of every round.
        self.multiplier += 3


class GatekeeperToonPierceEffect(AdditiveDamageBoostNoToonup):
    def combine(self, otherEffect):
        # Always take the new multiplier when combining here
        self.setMultiplier(otherEffect.getMultiplier())

        # When combining, take the highest rounds.
        otherRounds = otherEffect.getRounds()
        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)


# Bellringer's manager
# Creates the Overcharge environment on battle start.
class BellringerStatusEffect(CogStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Overcharge to all suits in this fight.
        self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])
        self.suitsGivenExplosionBoost = []
        self.weakenedHealingThisRound = False
        # Do an initial "round begin" to get the explosion effect on the other avatars,
        # Since this could happen anytime after the beginning of a turn
        # but before the end of it
        if self.isAi():
            self.addEffectToSuits()

    def onRoundBegin(self):
        self.weakenedHealingThisRound = False

    @property
    def isHealingWeakened(self):
        return self.weakenedHealingThisRound

    def explosionHappened(self):
        self.weakenedHealingThisRound = True

    def cleanup(self):
        super().cleanup()
        self.suitsGivenExplosionBoost = []

    def addEffectToSuits(self):
        if not self.isAi():
            return

        currentSuits = [suit for suit in self.getBattle().activeSuits if suit.getHp() > 0]
        for suit in currentSuits:
            if suit is self.getAv():
                continue
            if suit.doId not in self.suitsGivenExplosionBoost and not suit.getStatusEffectOfId(
                SEE.EFFECT_BELLRINGER_FODDER_EXPLOSION):
                suit.addStatusEffect(SEE.EFFECT_BELLRINGER_FODDER_EXPLOSION)
                self.suitsGivenExplosionBoost.append(suit.doId)


# Bellringer thing but for fodder
# Makes stuff go boom
class BellringerFodderExplosionEffect(SuitPreventDeathStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = True
        self.overchargedAtBeginning = False
        self.ignorePreventDeath = False

    def setIgnorePreventDeath(self, preventDeath):
        self.ignorePreventDeath = preventDeath

    def isVisible(self):
        return self.isOvercharged

    @property
    def isOvercharged(self):
        overcharge = self.av.getStatusEffectOfId(SEE.EFFECT_OVERCHARGED)
        return overcharge and overcharge.active

    def onRoundBegin(self):
        self.overchargedAtBeginning = self.isOvercharged
        self.ignorePreventDeath = False

    def canPreventDeath(self):
        if self.ignorePreventDeath:
            return False

        return self.overchargedAtBeginning

    def onDeathPrevented(self):
        # They prevented death, we need to blow them up now !!!
        self.createAttack(AttackEnum.BELLRINGER_FODDER_EXPLOSION, unlure=True, insertMethod='index')
        # Let the manager effect know that healing should be weakened this round
        self.getBattleCalc().sendEvent(BEG.EVENT_BELLRING_EXPLOSION_HAPPENED)


# Mouthpiece's manager
class MouthpieceStatusEffect(CogStatusEffect, UntouchableStatusEffect):
    COOKIE_RECIPES = [
        SEE.EFFECT_LURE_RESISTANCE,
        SEE.EFFECT_FLATTENED_DAMAGE_TAKEN,
        SEE.EFFECT_SOAK_RESISTANCE,
        SEE.EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = True
        self.suitsGivenBoost = set()
        self.heartbrokenDamage = 0
        # create overcharge environmental
        # self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])

    def cleanup(self):
        if self.cleanedUp:
            return

        # Since the visual effect isn't tied to the status effect, it will persist on the toon unless we
        # explicitly remove it from the avatar.
        if self.isAi():
            for toon in self.battleCalc.getAllToons():
                toon.removeVisualEffectsOfId(VisualEffectEnum.RED_THREAD)

        super().cleanup()

    def bakeCookies(self, freshSuit):
        # called when a suit joins battle
        if freshSuit.dna.name == 'mouthp' or not self.isAi() or freshSuit in self.suitsGivenBoost:
            return

        cookieType = random.choice(self.COOKIE_RECIPES)
        self.suitsGivenBoost.add(freshSuit)

        # Increase the level by 2.
        freshSuit.level += 2
        # Send our new level to the client.
        freshSuit.d_setLevelDist(freshSuit.getLevel())

        newHp = freshSuit.getHp() + 250
        freshSuit.b_setMaxHp(newHp)
        freshSuit.b_setHp(newHp)

        extraArgs = []
        if cookieType == SEE.EFFECT_FLATTENED_DAMAGE_TAKEN:
            # flat -30 damage to gags
            extraArgs = [-30]
        elif cookieType == SEE.EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST:
            # flat +12 damage increase
            extraArgs = [12]
        elif cookieType == SEE.EFFECT_LURE_RESISTANCE:
            # lure immunity
            extraArgs = [-1]
        freshSuit.addStatusEffect(cookieType, extraArgs=extraArgs)
        freshSuit.addStatusEffect(SEE.EFFECT_MOUTHPIECE_BONUS, extraArgs=[int(cookieType)])
        freshSuit.addVisualEffect(VisualEffectEnum.MOUTHPIECE_BONUS, extraArgs=[random.randint(1, 4)])
        if cookieType != SEE.EFFECT_LURE_RESISTANCE:
            # if not lure-immune, get resistance
            freshSuit.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE, extraArgs=[2])

    def handleSuitDied(self, suit):
        if suit.getStatusEffectOfId(SEE.EFFECT_MOUTHPIECE_BONUS):
            self.heartbrokenDamage -= suit.getMaxHp()
            self.suitsGivenBoost.remove(suit)

    def handleHeartbroken(self):
        if self.heartbrokenDamage < 0:
            self.createGeneralAttack(AttackEnum.HEARTBROKEN, insertKwargs={"mode": "insert"},
                                     extraArgs=[self.heartbrokenDamage])
            self.heartbrokenDamage = 0

    def extraAttacks(self) -> None:
        self.createAttack(AttackEnum.ROLODEX, insertMethod='end', unlure=True)
        otherSuitCount = len(self.getBattle().aliveSuits) - 1
        if otherSuitCount > 0 or len(self.getBattle().activeToons) > 1:
            self.createAttack(AttackEnum.RED_THREAD, insertMethod='end')

    # TODO: cleanup sets method for when an avatar dies? maybe? or perhaps not necessary?


# Mouthpiece's passive bonus applied to Cogs joining from the street
class MouthpieceBonusFlag(FlagBase):
    # A flag for marking a Cog as buffed by Mouthpiece.
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = True
        self.cookieType = SEE(extraArgs[0])
        self.fields = ['cookieType']


class RedThreadStatusEffect(StatusEffectBase):
    """
    Similar to a damage absorb status effect, but it listens to a given list of avatars
    and does not do any hidden damage down.
    """
    connectedSuitMultiplier = 1.00  # when a toon takes X damage, a connected suit takes this % of that
    connectedToonMultiplier = 0.10  # when a suit takes X damage, a connected toon takes this % of that

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.partner = extraArgs[0]
        self.fields = ['partner']
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE]
        self.combines = False

    def heardDamage(self, damageAmount: int, target: BattleAvatar, attackType: AttackEnum):
        if attackType == AttackEnum.RED_THREAD_DAMAGE:
            return  # ignore red thread damage here to not echo endlessly
        if target is None or target.doId != self.partner:
            return  # sanity check
        if self.av.isSuit() and target.isToon():
            self.createGeneralAttack(
                AttackEnum.RED_THREAD_DAMAGE,
                insertKwargs={"mode": "insert"},
                extraArgs=[damageAmount * self.connectedSuitMultiplier],  # TODO: sort out priority?
                targetList=[self.av]
            )
        elif self.av.isToon() and target.isSuit():
            self.createGeneralAttack(
                AttackEnum.RED_THREAD_DAMAGE,
                insertKwargs={"mode": "insert"},
                extraArgs=[damageAmount * self.connectedToonMultiplier],
                targetList=[self.av]
            )
        # TODO: cleanup method for when an avatar dies? maybe? or perhaps not necessary?


class RedThreadTangledStatusEffect(StatusEffectBase):
    """Variant of Red Thread that echoes damage from any other avatar also with this effect"""
    multiplier = 0.5
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.inheritedEventDefinitions = [SEE.EFFECT_RED_THREAD, SEE.EFFECT_BASE]
        self.combines = False

    def heardDamage(self, damageAmount: int, target: BattleAvatar, attackType: AttackEnum):
        if target.getStatusEffectOfId(SEE.EFFECT_RED_THREAD_TANGLED) is None or attackType == AttackEnum.RED_THREAD_DAMAGE:
            return
        self.createGeneralAttack(
            AttackEnum.RED_THREAD_DAMAGE,
            insertKwargs={'mode': 'insert'},
            extraArgs=[damageAmount * self.multiplier],
            targetList=[self.getAv()]
        )


# Treekiller's Peeling the Bark (suit)
class PeelingTheBark(StatusEffectRoundsModifierEffect):
    EFFECTS_TO_MODIFY = SUIT_STATUS_EFFECTS_TO_REDUCE

    def __init__(self, *args):
        super().__init__(*args)
        self.wantShow = True
        self.inheritedEventDefinitions += [SEE.EFFECT_BASE]

        # Adjust all of the currently inflicted effects.
        if self.isAi():
            for effectId in self.EFFECTS_TO_MODIFY:
                for effect in self.getAv().getStatusEffectsOfId(effectId):
                    self.handleEffectRounds(effect, self.getAv())


# Featherbedder's cheese prevention
class PeacefulSlumberEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = True
        self.roundsNoCogs = 0

    def isVisible(self):
        return self.multiplier < 1.0

    def adjustDefense(self):
        # Count dead cogs as well (Based on how many were alive at the beginning of the round)
        if len(self.getBattle().activeSuits) <= 1:
            self.roundsNoCogs = min(self.roundsNoCogs + 1, 2)
        else:
            self.roundsNoCogs = max(self.roundsNoCogs - 1, 0)

        # Adjusts at the very end of the round
        if self.roundsNoCogs >= 2:
            self.multiplier = max(self.multiplier - 0.25, 0.0)
        else:
            self.multiplier = min(self.multiplier + 0.25, 1.0)


# Featherbedder's Overhire
class FeatherbedderStatusEffect(CogStatusEffect, AttackIOModificationStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = True
        self.attackPowers = (1.00, 1.1, 1.2, 1.3, 1.4)
        self.attackReduct = (1.00, 0.85, 0.70, 0.55, 0.40)
        self.suitsGivenPowerNap = []
        self.suitsAddedExtraAttackFor = []
        self.calledInsomnia = False
        self.powerNapCogsKilledThisTrack = 0
        if self.isAi():
            # Apply Overcharge to all suits in this fight.
            self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])
        self.updateReduction()

    def updateReduction(self):
        if not self.isAi():
            return

        self.suitsAddedExtraAttackFor = []
        self.calledInsomnia = False
        # Get the index of the power lists
        currentSuits = [suit for suit in self.getBattle().activeSuits if suit.getHp() > 0]
        suitCount = len(currentSuits) - 1
        suitIndex = max(0, min(suitCount, len(self.attackPowers) - 1))
        self.attackMultiplier = self.attackPowers[suitIndex]
        self.defenseMultiplier = self.attackReduct[suitIndex]

        for suit in currentSuits:
            if suit is self.getAv():
                continue
            if suit.doId not in self.suitsGivenPowerNap and not suit.getStatusEffectOfId(SEE.EFFECT_POWER_NAP):
                suit.addStatusEffect(SEE.EFFECT_POWER_NAP)
                self.suitsGivenPowerNap.append(suit.doId)

    def heyFeatherbedderIReallyHateSoundCanYouMakeThemShutUp(self, suit) -> None:
        # Reject their ridiculous request if sound was used on a non sleepy suit.
        if suit.doId in self.suitsAddedExtraAttackFor or not suit.getStatusEffectOfId(SEE.EFFECT_POWER_NAP):
            return

        self.suitsAddedExtraAttackFor.append(suit.doId)
        if not self.calledInsomnia:
            self.createAttack(AttackEnum.INSOMNIA, insertMethod='end', unlure=True)
        self.calledInsomnia = True
        self.generateRandomSuitAttack()

    def checkSuitDied(self, suit):
        if suit.getStatusEffectOfId(SEE.EFFECT_POWER_NAP):
            self.powerNapCogsKilledThisTrack += 1

    def checkPowerNapBoost(self):
        if self.powerNapCogsKilledThisTrack > 0:
            self.createGeneralAttack(AttackEnum.POWER_NAP_KILL_DAMAGE_UP, extraArgs=[3*self.powerNapCogsKilledThisTrack])
        self.powerNapCogsKilledThisTrack = 0


# Featherbedder's Fodder Status Effect
class PowerNapStatusEffect(AttackIOModificationStatusEffect):
    attackPowers = (0.2, 0.4)
    attackReduct = (0.3, 0.5)

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = False
        self.wakeUpHealAmount = self.extraArgs[2]
        self.turnIndex = 0 if len(extraArgs) < 4 else int(extraArgs[3])
        self.attackMultiplier = self.attackPowers[self.turnIndex]
        self.defenseMultiplier = self.attackReduct[self.turnIndex]
        self.fields += ["wakeUpHealAmount", "turnIndex"]

    def decrement(self, amount):
        if self.turnIndex < 1:
            self.turnIndex += 1
            self.attackMultiplier = self.attackPowers[self.turnIndex]
            self.defenseMultiplier = self.attackReduct[self.turnIndex]
        super().decrement(amount)

    def roundsRanOut(self):
        self.createGeneralAttack(AttackEnum.POWER_NAP_HEAL, targetList=[self.av], extraArgs=[self.wakeUpHealAmount, 1, 3.0])
        super().roundsRanOut()


class FirestarterStatusEffect(CogStatusEffect, AttackIOModificationStatusEffect):
    MAX_ATTACK_MULT = 25
    MAX_DEFENSE_MULT = 0.6

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.deadSuits = []

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        attackDamage += self.attackMultiplier
        return attackDamage

    def handleBackburner(self) -> None:
        self.createAttack(
            AttackEnum.BACKBURNER,
            insertMethod="end",
        )

    def handleSuitDied(self, suit) -> None:
        self.deadSuits.append(suit)

    def handleRequestPyromaniac(self):
        if self.attackMultiplier >= self.MAX_ATTACK_MULT and self.defenseMultiplier <= self.MAX_DEFENSE_MULT:
            return

        # Display pyromaniac stack being earned.
        self.createAttack(AttackEnum.PYROMANIAC, insertMethod='end')

    def handlePyromaniac(self) -> None:
        self.attackMultiplier = min(self.attackMultiplier + 5, self.MAX_ATTACK_MULT)
        self.defenseMultiplier = max(self.defenseMultiplier - 0.08, self.MAX_DEFENSE_MULT)

        # Also make the effect visible.
        self.wantShow = True

        self.deadSuits = []


# Firestarter's Backburner Status
class BackburnerStatusEffect(AttackIOModificationStatusEffect, StatusEffectRoundsModifierEffect):
    EFFECTS_TO_MODIFY = SUIT_STATUS_EFFECTS_TO_REDUCE
    STARTING_ATK = 10
    STARTING_DEF = 1.25
    ATK_GAIN_PER_STACK = 10
    DEF_GAIN_PER_STACK = 0.75

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        AttackIOModificationStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, [extraArgs[0], extraArgs[1]])
        StatusEffectRoundsModifierEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, [extraArgs[2], extraArgs[3]])
        self.wantShow = True
        self.stacks = 1
        self.fields = ['attackMultiplier', 'defenseMultiplier', 'roundModifier', 'relativeModifier', 'percentHpDamage']

        # Adjust all of the currently inflicted effects.
        if self.isAi():
            self.percentHpDamageBase = extraArgs[4]
            self.percentHpDamagePerExtraStack = extraArgs[5]
            self.percentHpDamage = 0
            self.updateReduction()
            self.updateDamage()
        else:
            self.percentHpDamage = extraArgs[4]

    def reduceEffects(self):
        for effectId in self.EFFECTS_TO_MODIFY:
            for effect in self.getAv().getStatusEffectsOfId(effectId):
                self.handleEffectRounds(effect, self.getAv())

    def combine(self, otherEffect):
        # When combining, take the highest rounds
        otherStacks = otherEffect.stacks
        self.incrementStacks(otherStacks)

    def incrementStacks(self, amount):
        self.stacks += amount
        self.updateReduction()
        self.updateDamage()

    def updateReduction(self):
        if not self.isAi():
            return
        self.attackMultiplier = self.STARTING_ATK + ((self.stacks - 1) * self.ATK_GAIN_PER_STACK)
        self.defenseMultiplier = self.STARTING_DEF + ((self.stacks - 1) * self.DEF_GAIN_PER_STACK)
        self.roundModifier = -self.stacks

    def updateDamage(self):
        if not self.isAi():
            return
        self.percentHpDamage = self.percentHpDamageBase + (self.percentHpDamagePerExtraStack * (self.stacks - 1))

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        # The attack damage boost should be additive, not multiplicative
        attackDamage += self.attackMultiplier
        return attackDamage

    def applyDamage(self):
        maxHp, hp = self.getAv().getMaxHp(), self.getAv().getHp()
        damage = max(min(math.ceil(maxHp * self.percentHpDamage), hp), 1)
        self.createGeneralAttack(
            AttackEnum.SUIT_DAMAGE,
            extraArgs=[-damage],
            targetList=[self.getAv()]
        )

# endregion

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# Instance Mercs Status Effects #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# region


# Base Status Effect for the Instance Mercs
class InstanceMercStatusEffectBase(CogStatusEffect):
    """
    The base status effect for an InstanceMerc.
    """
    NORMAL = 0
    OVERCLOCKED = 1

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.difficulty = extraArgs[0]
        self.fields = ['difficulty']

        # Determines the natural spawnrate for cogs,
        # based on whatever this instance suit is.
        self.reserveSpawnCount = 1

        # Determines whether the instance merc kills all other suits along with itself.
        # AKA: Fight ends immediately when merc dies.
        self.endFightOnDeath = False
        self.removeReservesOnDeath = False

        self.inheritedEventDefinitions += [SEE.EFFECT_MANAGER_MERC]

        # Attack definitions to set per merc regarding difficulty.
        self.ATTACK_DEFS = {}

    def cleanup(self):
        if self.cleanedUp:
            return

        del self.ATTACK_DEFS
        return super().cleanup()

    ### BATTLE METHODS ###

    def attemptEndFight(self):
        battle = self.getBattle()

        if self.endFightOnDeath:
            # Remove pending suits from battle
            from toontown.clashbattle.battle.BattleGlobals import BattleStateEnum
            suitsToRemove = battle.pendingSuits + battle.joiningSuits + battle.joiningNotPendingSuits
            for suit in suitsToRemove:
                suit.setBattleState(BattleStateEnum.INACTIVE)
            # Instakill all alive suits
            aliveSuits = [suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]
            self.createGeneralAttack(
                AttackEnum.AVATAR_INSTAKILL,
                targetList=aliveSuits,
                insertKwargs={"respectPreviousAdditions": False}
            )

        if self.endFightOnDeath or self.removeReservesOnDeath:
            # If we're part of an instance, clear the reserve suits.
            if hasattr(battle, 'instance'):
                for suit in battle.instance.reserveSuits:
                    if isinstance(suit, tuple):
                        suit[0].requestDelete()
                    else:
                        suit.requestDelete()
                battle.instance.reserveSuits = []

    ### DIFFICULTY METHODS ###

    def getDifficulty(self):
        """
        Gets the currently defined difficulty for the status effect.
        By default, it will use whatever difficulty argument that
        the Suit generates with.
        """
        return self.difficulty

    """
    All of these methods are simple comparison
    methods, used for various HP gate definitions.
    """

    def modeIsNormal(self):
        return self.difficulty == self.NORMAL

    def modeIsNotNormal(self):
        return self.difficulty != self.NORMAL

    def modeIsOverclocked(self):
        return self.difficulty == self.OVERCLOCKED

    def modeIsNotOverclocked(self):
        return self.difficulty != self.OVERCLOCKED

    def updateDifficulty(self, difficulty):
        """
        This method gets called by DistributedInstanceMercAI, when the merc is created.
        This ensures that the status effect is using the correct logic for the difficulty.
        """
        if self.isAi():
            self.difficulty = difficulty

    def getAttackInfo(self, field):
        """
        self.ATTACK_DEFS represents a dictionary of information regarding
        customizating specific fields of a Suit's ability, based on whatever
        self.difficulty is set to.
        """
        assert field in self.ATTACK_DEFS
        fieldTuple = self.ATTACK_DEFS[field]
        pickIndex = self.difficulty
        if type(fieldTuple) != tuple:
            return fieldTuple
        elif len(fieldTuple) == 1:
            return fieldTuple[0]
        elif len(fieldTuple) == 2:
            return fieldTuple[pickIndex]

    ### INSTANCE METHODS ###

    def getInstance(self):
        """
        Gets the battle instance object that we are located in.
        We can request pending suits through its methods.

        Additionally, this function will return None if no instance exists.
        This is to help keep compatability with handling these enemies
        outside of a given instance.
        """
        if not self.isAi():
            return None
        return getattr(self.getBattle(), 'instance', None)

    def instanceNaturalSpawns(self, spawnCount: int = None):
        """
        Naturally adds a reserve cog.
        """
        self.instanceRequestReserves(spawnCount or self.reserveSpawnCount, overflow=False)

    def instanceRequestReserves(self, addReserve=1, overflow=False):
        """
        Requests the merc instance to add reserve cogs.

        The logic for level generation, suit type, etc. can be modified
        in the suit's respective instance AI (DistributedInstance_____AI).

        addReserve determines how many cogs to put into reserve.
        overflow determines if the reserve should overflow past the active suits.
        """
        instance = self.getInstance()
        if instance is not None:
            instance.generateReserveSuits(addReserve, overflow)

    def getInstanceReserves(self):
        """
        Returns a list of the reserve suits if the instance exists.
        Otherwise, an empty list will be returned.
        """
        instance = self.getInstance()
        if instance is not None:
            return instance.reserveSuits
        return []


# Prethinker's status effect, which is designed to make him very fun to fight against
class PrethinkerStatusEffectBase(InstanceMercStatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.additionalAttacks = extraArgs[1]
        self.fields += ['additionalAttacks']

        self.endFightOnDeath = True
        self.reserveSpawnCount = 2

        # Was Prethinker targeted last round?
        self.targetedLastRound = False
        # How many rounds sound used in a row?
        self.soundRounds = 0
        self.blockingSound = False
        self.blockingSoundTargetIndex = None
        # Castling in reaction to being soaked, lured or trapped at beginning of turn has a cooldown.
        self.setupCastlingCooldown = 0

        self.ATTACK_DEFS = {
            'setup_castling_cooldown': (2, 2)
        }

        self.addHPGate(hpRatio=0.4, callback=self.addNewAttack)

    def generateAttack(self):
        # Extra desperation attacks.
        self.doForwardThinkingAttacks()
        # Standard attack.
        super().generateAttack()

    def doForwardThinkingAttacks(self):
        for _ in range(self.additionalAttacks):
            # Get a number of targets that is the lowest between either the number of toons, or the number of cogs.
            numTargets = min(len(self.getBattleCalc().getAliveCogs()), len(self.getBattle().activeToons))
            activeToons = self.getBattle().activeToons[:]
            random.shuffle(activeToons)
            targetList = activeToons[:numTargets]
            extraArgs = []
            if numTargets > 1:
                possibleCogs = [suit for suit in self.getBattleCalc().getAliveCogs() if suit is not self.av]
                random.shuffle(possibleCogs)
                extraArgs = [suit.doId for suit in possibleCogs[:numTargets-1]]
            self.createAttack(AttackEnum.BRAIN_WAVE, targets=[self.getBattle().getToon(target) for target in targetList], extraArgs=extraArgs, unlure=True)

    def doCheats(self, attackOrder):
        # First, reduce our cooldowns.
        self.setupCastlingCooldown = max(0, self.setupCastlingCooldown - 1)

        self.blockingSound = False
        self.blockingSoundTargetIndex = None

        # Conditional checks for Castling
        # Check to see if we're being targeted this round.
        # If we are, and we were also targeted last round, do Castling to change our position.
        attemptedCastleThisTurn = False
        if self.__isBeingTargeted(attackOrder.getAttacks()):
            if self.targetedLastRound:
                attemptedCastleThisTurn = True
                self.doCastling()
            else:
                self.targetedLastRound = True
        else:
            self.targetedLastRound = False

        # If this conditional isn't on cooldown, check to see if the Toons have setup on us (Soaked, Lured, Trapped).
        if self.setupCastlingCooldown == 0:
            setupTypes = (SoakStatusEffect, LureStatusEffect, TrappedStatusEffect)
            for effectType in setupTypes:
                if self.avProfile.getStatusEffectOfType(effectType) is not None:
                    attemptedCastleThisTurn = True
                    self.doCastling()
                    break

        # Keep track of how many rounds in a row sound has been used.
        if self.getBattleCalc().findToonAttack(AttackEnum.TOON_SOUND):
            self.soundRounds += 1
        else:
            self.soundRounds = 0

        # If they've used sound twice or more in a row, and there are other alive cogs, prethinker will
        # go and stand behind one of the alive cogs to "dodge" the sound.
        # This is technically a form of castling, so ignore it if we have castled this turn.
        if self.soundRounds >= 2 and len(self.getBattleCalc().getAliveCogs()) > 1 and not attemptedCastleThisTurn:
            nextSoundIndex = self.getBattleCalc().attackOrder.getNextIndexOfTrack(AttackEnum.TOON_SOUND)
            if nextSoundIndex is not None:
                self.blockingSound = True
                self.blockingSoundTargetIndex = self.getBattle().activeSuits.index(random.choice([suit for suit in self.getBattle().activeSuits if suit.getHp() > 0 and suit is not self.av]))
                self.createAttack(AttackEnum.PT_BLOCK_SOUND_ENTER, insertMethod='index',
                                  insertArgs={'insertIndex': nextSoundIndex, 'adjust': False},
                                  extraArgs=[self.blockingSoundTargetIndex], unlure=True)

    def checkSoundOver(self, track):
        # If we used sound, create the exit effect which will remove the temp untouchable effect
        if track == AttackEnum.TOON_SOUND and self.blockingSound:
            self.createAttack(AttackEnum.PT_BLOCK_SOUND_EXIT, insertMethod='index',
                              extraArgs=[self.blockingSoundTargetIndex], unlure=True)

            self.blockingSound = False
            self.blockingSoundTargetIndex = None

    def doCastling(self):
        # Only do Castling if there's another suit in the fight.
        if len(self.getBattleCalc().getAliveCogs()) > 1:
            # Put the anti-setup condition on cooldown so we don't do Castling TOO often.
            self.setupCastlingCooldown = self.getAttackInfo('setup_castling_cooldown')
            self.createAttack(AttackEnum.CASTLING, unlure=True, insertMethod='beginning')

    def __isBeingTargeted(self, attacks):
        """Returns if Prethinker is being directly targeted this round by a Toon attack."""
        av = self.getAv()

        from toontown.clashbattle.battle.attacks.server.AttackAI import AttackAI
        for attack in attacks:
            attack: AttackAI
            # Don't check attack types that don't directly target us.
            if attack.attackType not in [AttackEnum.TOON_HEAL, AttackEnum.TOON_SOUND] + BattleGlobals.NON_ATTACKS:
                # make sure that we are being targeted by any of these gags
                if attack.target == av.doId:
                    return True

    def addNewAttack(self):
        self.additionalAttacks += 1
        self.wantShow = True
        self.createAttack(AttackEnum.FORWARD_THINKING, 'end', unlure=True)
        self.av.addVisualEffect(VisualEffectEnum.PRETHINKER_BRAIN_STORM)

    def attemptLightsOn(self):
        # Only works when in an instance.
        instance = self.getInstance()
        if instance is None:
            return
        battleCalc = self.getBattleCalc()

        # If we have an executive prethinker jockey in the battle, make them refill the battle if there's empty slots.
        aliveSuits = battleCalc.getAliveCogs()
        jockey = battleCalc.findCogInBattle('ptjockey', aliveSuits)
        if jockey is None or not jockey.isElite:
            return

        amountToSpawn = instance.getInstanceInfo('battle_cap') - len(aliveSuits)
        if amountToSpawn > 0:
            battleCalc.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                AttackEnum.LIGHTS_ON, {"invoker": jockey, "unlure": True, "extraArgs": [amountToSpawn, True]},
                {"mode": "end"}
            ])

    def weDied(self):
        # Hey. We died.
        # Remove the brain storm visual effect because of it
        self.av.removeVisualEffectOfId(VisualEffectEnum.PRETHINKER_BRAIN_STORM)


# Chainsaw Consultant's attack behavior.
@DirectNotifyCategory()
class ChainsawConsultantStatusEffectBase(InstanceMercStatusEffectBase, AttackIOModificationStatusEffect,
                                         DamageAbsorbStatusEffect):
    MAX_REVVING_STACKS = 10
    DEBUG_FORCE_ATTACK = None  # AttackEnum.DEADWOOD

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)

        self.notify.setDebug(True)

        self.fields = [
            'difficulty', 'attackMultiplier', 'defenseMultiplier', 'revvingUpStacks', 'currentPhase',
            'highestRevStacks', 'absorbMultiplier',
        ]
        self.difficulty = extraArgs[0]
        self.attackMultiplier = extraArgs[1]
        self.defenseMultiplier = extraArgs[2]
        self._revvingUpStacks = extraArgs[3]
        self.currentPhase = extraArgs[4]
        self.highestRevStacks = extraArgs[5]
        self.absorbMultiplier = extraArgs[6]
        self.avatarType = 0

        self.endFightOnDeath = True
        self.wantShow = True
        self.reserveSpawnCount = 5
        self.internalRounds = 0
        self.previousAttack = None

        # What attack (excluding any overrides) did we last use?
        self.previousLogicAttack = None

        # What attack types have been used on each Suit?
        self.suitToAttacksUsed = {}
        # Keep track of the the toons which attacked each Suit.
        self.suitToToonAggressors = {}
        # Keep track of the amount of damage dealt to each Suit.
        self.suitToDamageTaken = {}
        # Keep track of the previous Toon who attacked him.
        self.lastToonAttacked = None
        # Keep track of all of the toons which used an IOU in this round.
        self.toonsWhoNeededToResortToUsingIOUsLmao = []
        # Keep track of the suits that have died this turn.
        self.deadSuits = []
        # Keep track of how many stacks were queued to be
        # added at the end of the turn.
        self.queuedStacks = 0
        self.bonusStacks = 0
        # Has the chainsaw used throttle in the battle yet?
        self.usedThrottle = False

        # Suits which benefited from Cut The Slack.
        self.cutTheSlack_targets = {}

        # Keep track of how long the Chainsaw has gone without
        # being attacked.
        self.hitlessRounds = -1

        # Keep track of all the fired chain linked cogs.
        self.firedLinks = 0

        # If this value is 0 or below, rev spending abilities are allowed.
        self.abilityBanRounds = 0

        # Map all of the attack enums to their functions.
        self.ATTACK_FUNCTIONS = {
            AttackEnum.WHIP_SAW: self.doWhipSaw,
            AttackEnum.OFFBOARDING: self.doOffboarding,
            AttackEnum.CUT_THE_SLACK: self.doCutTheSlack,
            AttackEnum.MARKED_WOOD: self.doMarkedWood,
            AttackEnum.SCABBARD: self.doScabbard,
            AttackEnum.CHAIN_LINKED: self.doChainLinked,
            AttackEnum.AGGRANDIZE: self.doAggrandize,
            AttackEnum.DEADWOOD: self.doDeadwood,
            AttackEnum.THROTTLE: self.doThrottle,
            AttackEnum.SPARK_PLUG: self.doSparkPlug,
            AttackEnum.LAYOFFS: self.doLayoffs,
        }

        # Add the override visual effect when we spawn
        self.av.addVisualEffect(VisualEffectEnum.CHAINSAW_OVERRIDE)

        self.addHPGate(hpRatio=8500, callback=self.startPhaseTwo, isRatio=False)
        self.addHPGate(hpRatio=4750, callback=self.startPhaseThree, isRatio=False)

        # Apply Overcharge to all suits in this fight.
        self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])

        # Absorption stuff
        self.inheritedEventDefinitions += [SEE.DEFINITION_DAMAGE_ABSORB]
        self.activeDamageDowns = {}
        self.damageDealtThisTrack = 0
        # Do an initial "round begin" to get the damage down on the other avatars,
        # Since this could happen anytime after the beginning of a turn
        # but before the end of it
        if self.isAi():
            self.handleBeginRound()
        else:
            from toontown.clashbattle.battle.gui.special.ChainsawMeterGUI import ChainsawMeterGUI
            messenger.send(ChainsawMeterGUI.setRPMEvent(), [self._revvingUpStacks])

    def cleanup(self):
        if self.cleanedUp:
            return

        del self.suitToAttacksUsed
        del self.suitToToonAggressors
        del self.suitToDamageTaken
        del self.lastToonAttacked
        del self.toonsWhoNeededToResortToUsingIOUsLmao

        return super().cleanup()

    def generateRandomSuitAttack(self, *args, **kwargs):
        kwargs["tauntIndex"] = self.currentPhase == 2
        return super().generateRandomSuitAttack(*args, **kwargs)

    def startPhaseTwo(self) -> None:
        self.currentPhase = 2
        self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
            AttackEnum.CHAINSAW_ENTER_DORMANT,
            {"invoker": self.av},
            {"mode": 'end'},
        ])
        # Set stacks to 0 upon entering the second phase.
        self.revvingUpStacks = 0
        # Force the attack multiplier to 1x.
        self.setMultiplier(1)

        self.highestRevStacks = self.revvingUpStacks

    def startPhaseThree(self) -> None:
        self.currentPhase = 3
        self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
            AttackEnum.CHAINSAW_EXIT_DORMANT,
            {"invoker": self.av},
            {"mode": 'end'},
        ])
        # Set stack cap to 20.
        self.MAX_REVVING_STACKS = 20

        self.highestRevStacks = self.revvingUpStacks

        # Remove the chain link effect if present.
        if self.chainLinkActive:
            for suit in self.getBattleCalc().suits:
                suit.removeStatusEffectOfId(SEE.EFFECT_CHAIN_LINKED)

            self.removeChainLink()

    def handleEndRound(self) -> None:
        self.lastToonAttacked = None
        self.deadSuits = []
        self.queuedStacks = 0
        self.bonusStacks = 0
        self.suitToAttacksUsed = {}
        self.suitToToonAggressors = {}
        self.suitToDamageTaken = {}
        self.toonsWhoNeededToResortToUsingIOUsLmao = []

        # Increment the hitless rounds regardless of if he
        # was actually hit or not, as when he does get it,
        # the rounds get set to -1.
        self.hitlessRounds += 1

        # Increment the rounds for each cut the slack target.
        for suit in self.cutTheSlack_targets:
            self.cutTheSlack_targets[suit] += 1

        # Decrement ability ban rounds.
        if self.abilityBanRounds > 0:
            self.abilityBanRounds -= 1

    def handleBeginSuitAttacks(self) -> None:
        # Get a list of valid toons.
        toons = [simbase.air.getDo(toonId) for toonId in self.getBattleCalc().toons]
        toons = [toon for toon in toons if toon]

        # Get the toons who are marked.
        markedToons = [toon for toon in toons if toon.getStatusEffectOfId(SEE.EFFECT_MARKED_WOOD)]

        # Preset the target list if marked wood was previously used.
        targets = None
        if markedToons:
            # Prioritize the toon who last attacked the chainsaw.
            if self.lastToonAttacked:
                targets = [self.lastToonAttacked]
            # Otherwise, target the marked toon.
            elif markedToons:
                targets = [markedToons[0]]

        # Apply the override for the chainsaw's random attack.
        if targets:
            for attack in self.getBattleCalc().attackOrder.getAttacksOfInvoker(self.av):
                attack.targets = targets

    def handleGagLanded(self, suit, toon, attackType: AttackEnum) -> None:
        if attackType != AttackEnum.TOON_LURE:
            if suit is self.getAv():
                # Increment stacks by 1 for each gag landed during the turn.
                self.queuedStacks += 1

                # Increment stacks by 1 if a trap was triggered.
                if attackType == AttackEnum.TOON_TRAP:
                    self.queuedStacks += 1

            self.suitToToonAggressors.setdefault(suit, [])
            self.suitToToonAggressors[suit].append(toon)

        self.suitToAttacksUsed.setdefault(suit, [])
        self.suitToAttacksUsed[suit].append(attackType)

    def handleChainsawUnlured(self):
        # Increment stacks by 1 if a toon unlured the chainsaw.
        self.queuedStacks += 1

    def handleToonUsedGag(self, attack) -> None:
        if attack.attackType != AttackEnum.TOON_NPC:
            return

        self.toonsWhoNeededToResortToUsingIOUsLmao.append(attack.invoker)

    def handleNormalAttacksOver(self) -> None:
        stacks = self.queuedStacks

        # Punish the Toons if they've wiped all of the other Suits in a single turn.
        if self.deadSuits:
            if len(self.deadSuits) == len([suit for suit in self.getBattleCalc().suits if suit is not self.getAv()]):
                stacks += 1

        # Remove a stack if chain link is active.
        if self.chainLinkActive:
            stacks -= 1

        stacks = self.addStacks(stacks)
        bonusStacks = self.addStacks(self.bonusStacks)
        if stacks + bonusStacks > 0:
            visualStacks = stacks or bonusStacks
            diff = self.revvingUpStacks - (stacks + bonusStacks)
            bonus = 0 if not stacks else bonusStacks

            self.createAttack(
                AttackEnum.REVVING_UP, extraArgs=[visualStacks, diff, bonus], unlure=True,
                tauntIndex=self.currentPhase - 1
            )

    def registerToonDamageDealt(self, suit, damageAmount: int, attackType: AttackEnum) -> None:
        self.suitToDamageTaken.setdefault(suit, 0)
        self.suitToDamageTaken[suit] += damageAmount

        if suit is self.getAv():
            # Reset the rounds hitless.
            self.hitlessRounds = -1

        elif attackType == AttackEnum.TOON_FIRE and suit.getStatusEffectOfId(SEE.EFFECT_CHAIN_LINKED):
            self.firedLinks += 1

    def handleChainsawHit(self, toon):
        self.lastToonAttacked = toon

    def suitDied(self, suit, attackType) -> None:
        self.deadSuits.append(suit)

        wasCts = suit in self.cutTheSlack_targets
        if wasCts:
            del self.cutTheSlack_targets[suit]

        # Apply kickback vulnerability to self if a Cut the Slack cog is killed
        # Don't do this if it's part of chain linked though
        if wasCts and not suit.getStatusEffectOfId(SEE.EFFECT_CHAIN_LINKED):
            # Don't do kick back if the suit was fired by Chainsaw
            if attackType in (AttackEnum.OFFBOARDING, AttackEnum.LAYOFFS, AttackEnum.CUT_THE_SLACK):
                return
            level = suit.getActualLevel()
            # Only grant the bonus if they're level 20 or above.
            if level >= 20:
                self.createAttack(
                    AttackEnum.KICKBACK,
                    unlure=True,
                    insertMethod="index",
                    targets=[self.getAv()],
                    extraArgs=[1.10 + ((level - 20) * 0.02), 2],
                )

        chainLinked = suit.getStatusEffectOfId(SEE.EFFECT_CHAIN_LINKED)
        if not chainLinked:
            return

        # If the chain link was broken, give the Chainsaw the
        # kickback effect.
        if self.chainLinkActive:
            return

        self.createAttack(
            AttackEnum.KICKBACK,
            unlure=True,
            insertMethod="index",
            targets=[self.getAv()],
            extraArgs=[1.05 + ((5 - self.firedLinks) * 0.05), 2],
        )

        self.removeChainLink()

        # Ban rev spending abilities next turn.
        self.abilityBanRounds = 2

    def removeChainLink(self) -> None:
        # The chain link was broken, so let's remove their effect.
        self.av.removeStatusEffectOfId(SEE.EFFECT_CHAIN_LINKED)

        # Reset the chain links fired.
        self.firedLinks = 0

    def instanceNaturalSpawns(self, spawnCount: int = None):
        # Ignore spawns when chain link is active.
        if self.previousAttack != AttackEnum.CHAIN_LINKED and self.chainLinkActive:
            return

        # Properly fill the battle if any suits died this round.
        aliveSuits = [suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]
        emptySlots = self.reserveSpawnCount - len(aliveSuits)
        if emptySlots:
            self.instanceRequestReserves(emptySlots, overflow=True)

            # If scabbard was used this turn, ensure that the incoming suits are
            # overcharged.
            if self.previousAttack == AttackEnum.SCABBARD:
                for reserve in self.getInstanceReserves():
                    reserve.overhealed = True
                    reserve.b_setHp(math.ceil(reserve.getHp() * 1.5))

            # If chain linked was used this turn, ensure that the incoming suits
            # are chain linked.
            elif self.previousAttack == AttackEnum.CHAIN_LINKED:
                reserves = self.getInstanceReserves()
                activeSuits = self.getBattleCalc().suits
                for i, reserve in enumerate(reserves):
                    # Give them the appropriate index.
                    reserve.addStartingStatusEffect(SEE.EFFECT_CHAIN_LINKED, extraArgs=[5 - len(activeSuits) - i])

    def handleAbilities(self):
        """Creates the abilities for Chainsaw Consultant."""
        # Store the chosen attack type here.
        # All the attack conditions are sorted based on their
        # cost, so the most expensive attack which passes its
        # conditionals will always happen.
        attackType = None
        kwargs = {}

        self.notify.debug("Called handleAbilities(), building ability pool...")

        # Convenience variables.
        battleCalc = self.getBattleCalc()
        toons = [simbase.air.getDo(toon) for toon in battleCalc.toons]
        toons = [toon for toon in toons if toon]
        suits = battleCalc.suits
        aliveSuits = [suit for suit in suits if suit.getHp() > 0]
        otherAliveSuits = [suit for suit in aliveSuits if suit is not self.av]
        fullBattle = len(aliveSuits) == 5
        suedSuits = [
            suit for suit in aliveSuits
            if suit.getStatusEffectOfId(SEE.EFFECT_SUIT_SUED)
        ]
        firedSuits = [
            suit
            for suit, atks in self.suitToAttacksUsed.items()
            if AttackEnum.TOON_FIRE in atks and suit is not self.getAv()
        ]
        totalLevel = sum([suit.getActualLevel() for suit in otherAliveSuits])

        # Only use rev spending abilities if we are allowed to.
        if self.abilityBanRounds <= 0 or self.revvingUpStacks >= 7:
            # Specific abilities for phase 2.
            if self.currentPhase == 2:
                # Add aggrandize to the choices if he can afford it.
                if self.revvingUpStacks >= 3:
                    # Get the suits which can be aggrandized.
                    aggrandizeTargets = [s for s in otherAliveSuits if (not s.isElite or s.getLevel() < 25)]
                    # Get any of these suits that were damaged.
                    damagedSuits = [s for s in aggrandizeTargets if self.suitToDamageTaken.get(s)]

                    # Conditionals
                    conditional_singleSuit = len(aggrandizeTargets) == 1
                    conditional_aliveDamagedSuits = len(damagedSuits) > 0
                    conditional_suedCogs = len(suedSuits) > 0

                    self.notify.debug(
                        "Ability 'Aggrandize' can be afforded, checking conditionals..."
                        f"\nConditional 'singleSuit': {conditional_singleSuit}"
                        f"\nConditional 'aliveDamagedSuits': {conditional_aliveDamagedSuits}"
                        f"\nConditional 'suedCogs: {conditional_suedCogs}"
                    )

                    # Check if any of the conditionals were met.
                    if any([
                        conditional_singleSuit,
                        conditional_aliveDamagedSuits,
                        conditional_suedCogs,
                    ]):
                        self.notify.debug("Conditionals passed! Choosing 'Aggrandize' as the chosen ability...")
                        attackType = AttackEnum.AGGRANDIZE

                        # Specifically target the damaged suit with the
                        # highest health.
                        if conditional_aliveDamagedSuits:
                            kwargs["aggrandize_targets"] = [sorted(damagedSuits, key=lambda suit: suit.getHp())[-1]]
                            kwargs["aggrandize_taunt"] = 1
                        elif conditional_suedCogs:
                            kwargs["aggrandize_targets"] = [sorted(suedSuits, key=lambda suit: suit.getHp())[-1]]
                        else:
                            kwargs["aggrandize_taunt"] = 0

                # Add Chain Linked to the choices if he has 6 or more stacks.
                # (it actually costs 3 to use)
                if self.revvingUpStacks >= 5:
                    # Conditionals
                    conditional_chainsawAlone = len(aliveSuits) == 1
                    conditional_targetChainsaw = len(self.suitToAttacksUsed.get(self.av, [])) == len(toons)
                    conditional_chainLinkInactive = not self.chainLinkActive

                    self.notify.debug(
                        "Ability 'Chain Linked' can be afforded, checking conditionals..."
                        f"\nConditional 'chainsawAlone': {conditional_chainsawAlone}"
                        f"\nConditional 'targetChainsaw': {conditional_targetChainsaw}"
                        f"\nConditional 'chainLinkInactive': {conditional_chainLinkInactive}"
                    )

                    # Check if any of the conditionals were met.
                    if conditional_chainLinkInactive and any([
                        conditional_chainsawAlone,
                        conditional_targetChainsaw,
                    ]):
                        self.notify.debug("Conditionals passed! Choosing 'Chain Linked' as the chosen ability...")
                        attackType = AttackEnum.CHAIN_LINKED

                        if conditional_chainsawAlone:
                            kwargs["chainlinked_taunt"] = 0
                        else:
                            kwargs["chainlinked_taunt"] = 1

                # Add scabbard to the choices if he can afford it.
                if self.revvingUpStacks >= 7:
                    # Conditionals
                    conditional_fullBattle = fullBattle
                    conditional_suedCogs = len(suedSuits) >= 2

                    self.notify.debug(
                        "Ability 'Scabbard' can be afforded, checking conditionals..."
                        f"\nConditional 'fullBattle': {conditional_fullBattle}"
                        f"\nConditional 'suedCogs': {conditional_suedCogs}"
                    )

                    # Check if any of the conditionals were met.
                    if any([
                        conditional_fullBattle,
                        conditional_suedCogs,
                    ]):
                        self.notify.debug("Conditionals passed! Choosing 'Scabbard' as the chosen ability...")
                        attackType = AttackEnum.SCABBARD

                        if conditional_fullBattle:
                            kwargs["scabbard_taunt"] = 0
                        else:
                            kwargs["scabbard_taunt"] = 1

            # Specific abilities for phases 1 and 3.
            else:
                wantCts = True

                # Add offboarding to the choices if he can afford it.
                if self.revvingUpStacks >= 2 and otherAliveSuits:
                    cutTheSlackTargets = [
                        suit for suit, rounds in self.cutTheSlack_targets.items()
                        if rounds >= 3 and suit.getHp() > 0
                    ]

                    # Conditionals
                    conditional_cutTheSlackTarget = len(cutTheSlackTargets) > 0
                    conditional_hitless = self.hitlessRounds >= 2
                    conditional_firedSuit = len(firedSuits) > 0
                    conditional_suitSurvivedAOE = any([
                        any(track in val for track in (AttackEnum.TOON_SQUIRT, AttackEnum.TOON_ZAP, AttackEnum.TOON_SOUND))
                        for key, val in self.suitToAttacksUsed.items()
                        if key is not self.getAv() and key.getHp() > 0
                    ])
                    conditional_levelPool = totalLevel >= 80

                    self.notify.debug(
                        "Ability 'Offboarding' can be afforded, checking conditionals..."
                        f"\nConditional 'cutTheSlackTarget': {conditional_cutTheSlackTarget}"
                        f"\nConditional 'hitless': {conditional_hitless}"
                        f"\nConditional 'firedSuit': {conditional_firedSuit}"
                        f"\nConditional 'suitSurvivedAOE': {conditional_suitSurvivedAOE}"
                        f"\nConditional 'levelPool: {conditional_levelPool}"
                    )

                    # Check if any of the conditionals were met.
                    if any([
                        conditional_cutTheSlackTarget,
                        conditional_hitless,
                        conditional_firedSuit,
                        conditional_suitSurvivedAOE,
                        conditional_levelPool,
                    ]):
                        self.notify.debug("Conditionals passed! Choosing 'Offboarding' as the chosen ability...")
                        attackType = AttackEnum.OFFBOARDING

                        if conditional_levelPool:
                            kwargs["offboarding_taunt"] = 3 if self.currentPhase == 1 else 7
                            # Fire the highest level cog in the case of the level pool
                            # being 80 or higher.
                            kwargs["offboarding_targets"] = [
                                sorted(otherAliveSuits, key=lambda suit: suit.getActualLevel(), reverse=True)[0]
                            ]
                            # Also override cts to not happen.
                            wantCts = False
                        elif conditional_firedSuit:
                            # Target a toon who used a fire.
                            aggressors = [self.suitToToonAggressors[suit] for suit in firedSuits]
                            kwargs["offboarding_taunt"] = 1 if self.currentPhase == 1 else 5
                            kwargs["retaliate_against"] = random.choice(aggressors)
                        elif conditional_cutTheSlackTarget:
                            # Specifically target the cut the slack target
                            # if the condition was met.
                            kwargs["offboarding_targets"] = [random.choice(cutTheSlackTargets)]
                        elif conditional_hitless:
                            kwargs["offboarding_taunt"] = 2 if self.currentPhase == 1 else 6
                        else:
                            # cog survives AOE
                            kwargs["offboarding_taunt"] = 0 if self.currentPhase == 1 else 4

                # Add cut the slack to the choices if he can afford it.
                if wantCts and self.revvingUpStacks >= 4 and otherAliveSuits:
                    # Get a list of valid CTS targets.
                    ctsSuits = [
                        suit for suit in aliveSuits
                        if suit.getActualLevel() < 30
                    ]
                    # Get a list of all sued suits.
                    suedSuits = [
                        suit for suit in aliveSuits
                        if suit.getStatusEffectOfId(SEE.EFFECT_SUIT_SUED)
                    ]

                    # Conditionals
                    conditional_fullBattle = fullBattle
                    conditional_deadSuits = len(self.deadSuits) >= 2
                    conditional_suedCog = len(suedSuits) > 0
                    conditional_ctsSuits = len(ctsSuits) > 0

                    self.notify.debug(
                        "Ability 'Cut The Slack' can be afforded, checking conditionals..."
                        f"\nConditional 'fullBattle': {conditional_fullBattle}"
                        f"\nConditional 'deadSuits': {conditional_deadSuits}"
                        f"\nConditional 'suedCog': {conditional_suedCog}"
                        f"\nConditional 'ctsSuits': {conditional_ctsSuits}"
                    )

                    # Check if any of the conditionals were met.
                    if conditional_ctsSuits and any([
                        conditional_fullBattle,
                        conditional_deadSuits,
                        conditional_suedCog,
                    ]):
                        self.notify.debug("Conditionals passed! Choosing 'Cut The Slack' as the chosen ability...")
                        attackType = AttackEnum.CUT_THE_SLACK

                        # Specifically target (any) of the sued cogs
                        # if the condition was met.
                        suedUnion = [suit for suit in suedSuits if suit in ctsSuits]
                        if conditional_suedCog and suedUnion:
                            kwargs["cuttheslack_targets"] = [random.choice(suedUnion)]
                            kwargs["cuttheslack_taunt"] = 2 if self.currentPhase == 1 else 5
                        elif conditional_deadSuits:
                            kwargs["cuttheslack_taunt"] = 1 if self.currentPhase == 1 else 4
                        elif conditional_fullBattle:
                            kwargs["cuttheslack_taunt"] = 0 if self.currentPhase == 1 else 3

                # Add marked wood to the choices if he can afford it.
                # Also have the caveat of only happening if the
                # previously chosen logic attack was not marked wood.
                if self.revvingUpStacks >= 7 and self.previousLogicAttack != AttackEnum.MARKED_WOOD:
                    chainsawHits = self.suitToToonAggressors.get(self.getAv(), [])

                    # Conditionals
                    conditional_chainsawSingleHit = len(chainsawHits) == 1
                    conditional_chainsawAllHit = len(chainsawHits) == len(toons)
                    conditional_usedIOU = len(self.toonsWhoNeededToResortToUsingIOUsLmao) > 0

                    self.notify.debug(
                        "Ability 'Marked Wood' can be afforded, checking conditionals..."
                        f"\nConditional 'chainsawSingleHit': {conditional_chainsawSingleHit}"
                        f"\nConditional 'chainsawAllHit': {conditional_chainsawAllHit}"
                        f"\nConditional 'usedIOU': {conditional_usedIOU}"
                    )

                    # Check if any of the conditionals were met.
                    if any([
                        conditional_chainsawSingleHit,
                        conditional_chainsawAllHit,
                        conditional_usedIOU,
                    ]):
                        self.notify.debug("Conditionals passed! Choosing 'Marked Wood' as the chosen ability...")
                        attackType = AttackEnum.MARKED_WOOD

                        # Specifically target the toon that:
                        # - Used an IOU (with the highest HP)
                        if conditional_usedIOU:
                            kwargs["markedwood_targets"] = [
                                sorted(self.toonsWhoNeededToResortToUsingIOUsLmao, key=lambda toon: toon.getHp())[-1]
                            ]
                            kwargs["markedwood_taunt"] = 2 if self.currentPhase == 1 else 5
                        # - Hit the chainsaw (alone)
                        elif conditional_chainsawSingleHit:
                            kwargs["markedwood_targets"] = [chainsawHits[0]]
                            kwargs["markedwood_taunt"] = 0 if self.currentPhase == 1 else 3
                        # - Hit the chainsaw (with the highest HP)
                        else:
                            kwargs["markedwood_targets"] = [sorted(toons, key=lambda toon: toon.getHp())[-1]]
                            kwargs["markedwood_taunt"] = 1 if self.currentPhase == 1 else 4

        # Do a big attack when reaching 10 stacks.
        if self.currentPhase != 2 and self.revvingUpStacks >= 10:
            # During phase 1, use Deadwood.
            if self.currentPhase == 1:
                attackType = AttackEnum.DEADWOOD
            # During phase 3, use Layoffs.
            elif otherAliveSuits:
                attackType = AttackEnum.LAYOFFS

        # Absolutely do Throttle when he reaches 0 stacks.
        elif self.currentPhase == 2 and self.revvingUpStacks == 0:
            attackType = AttackEnum.THROTTLE

        # If not doing an extreme attack...
        elif attackType is None and (self.abilityBanRounds <= 0 or self.revvingUpStacks >= 7):
            # Use whip saw during phases 1/3.
            if self.currentPhase != 2:
                if self.previousAttack != AttackEnum.WHIP_SAW:
                    attackType = AttackEnum.WHIP_SAW
            # Use spark plug during phase 2 if affordable and
            # if there wasn't an ability used in the previous turn.
            elif self.revvingUpStacks >= 1:
                if self.previousAttack != AttackEnum.SPARK_PLUG:
                    attackType = AttackEnum.SPARK_PLUG
                # If he is trying to use spark plug again,
                # force him to use scabbard or aggrandize
                # if he can afford it.
                elif otherAliveSuits:
                    if self.revvingUpStacks >= 7:
                        attackType = AttackEnum.SCABBARD
                    elif self.revvingUpStacks >= 3:
                        attackType = AttackEnum.AGGRANDIZE

            # Save the chosen logic attack.
            self.previousLogicAttack = attackType

        if self.DEBUG_FORCE_ATTACK is not None:
            attackType = self.DEBUG_FORCE_ATTACK

        self.notify.debug(f"Calculation of handleAbilities() completed. Ability chosen: {repr(attackType)}")

        # And create the attack.
        attackFunc = self.ATTACK_FUNCTIONS.get(attackType)
        if attackFunc:
            attackFunc(**kwargs)

        self.internalRounds += 1
        self.previousAttack = attackType

    def doOffboarding(self, **kwargs):
        self.removeStacks(2)

        retaliateTarget = kwargs.get("retaliate_against")
        self.createAttack(
            AttackEnum.OFFBOARDING, insertMethod='end', unlure=True, extraArgs=[bool(retaliateTarget)],
            tauntIndex=kwargs.get("offboarding_taunt", 0),
            targets=retaliateTarget if retaliateTarget else kwargs.get("offboarding_targets"),
        )

    def doLayoffs(self, **kwargs):
        self.removeStacks(10 - len(self.deadSuits))
        self.createAttack(AttackEnum.LAYOFFS, insertMethod='end', unlure=True, extraArgs=[-1])

    def doCutTheSlack(self, **kwargs):
        self.removeStacks(3)
        self.createAttack(
            AttackEnum.CUT_THE_SLACK, unlure=True,
            tauntIndex=kwargs.get("cuttheslack_taunt", 0),
            targets=kwargs.get("cuttheslack_targets"),
        )

    def doMarkedWood(self, **kwargs):
        self.removeStacks(7)
        self.createAttack(
            AttackEnum.MARKED_WOOD, unlure=True, insertMethod="end",
            tauntIndex=kwargs.get("markedwood_taunt", 0),
            targets=kwargs.get("markedwood_targets", [
                random.choice([simbase.air.getDo(toonId) for toonId in self.getBattleCalc().toons])
            ]),
        )

    def doAggrandize(self, **kwargs):
        self.removeStacks(3)
        self.createAttack(
            AttackEnum.AGGRANDIZE, unlure=True, insertMethod="end",
            targets=kwargs.get("aggrandize_targets"),
            tauntIndex=kwargs.get("aggrandize_taunt", 0)
        )

    def doScabbard(self, **kwargs):
        self.removeStacks(7)
        self.createAttack(
            AttackEnum.SCABBARD, unlure=True, extraArgs=[0.75, False, 1.5],
            insertMethod="end",
            tauntIndex=kwargs.get("scabbard_taunt", 0)
        )

    def doChainLinked(self, **kwargs):
        self.removeStacks(2)
        self.createAttack(
            AttackEnum.CHAIN_LINKED, unlure=True, insertMethod="end",
            tauntIndex=kwargs.get("chainlinked_taunt", 0)
        )

    def doDeadwood(self, **kwargs):
        self.createAttack(AttackEnum.DEADWOOD, unlure=True, insertMethod="end")

    def doThrottle(self, **kwargs):
        self.createAttack(AttackEnum.THROTTLE, unlure=True, insertMethod="end", extraArgs=[self.usedThrottle])
        self.usedThrottle = True

    def doSparkPlug(self, **kwargs):
        self.removeStacks(2)
        self.createAttack(AttackEnum.SPARK_PLUG, unlure=True, insertMethod="end")

    def doWhipSaw(self, **kwargs):
        # Queue up 2 stacks (this gets displayed with the revving up attack)
        self.bonusStacks += 2

    def addStacks(self, stacks: int) -> int:
        if self.currentPhase == 2 and (self.chainLinkActive or self.previousAttack == AttackEnum.CHAIN_LINKED):
            return 0

        oldStacks = self.revvingUpStacks
        self.revvingUpStacks += (stacks * self.revvingUpStackGainMulti)
        return self.revvingUpStacks - oldStacks

    def removeStacks(self, stacks: int) -> None:
        self.createGeneralAttack(
            AttackEnum.SPENDING_REV, insertKwargs={"mode": "end"}, extraArgs=[stacks, self.revvingUpStacks]
        )
        self.revvingUpStacks -= stacks

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Apply defense multiplier during phase 2.
        if self.currentPhase == 2:
            attackDamage *= self.defenseMultiplier
        return attackDamage

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        # Apply attack multiplier during phase 1/3.
        if self.currentPhase != 2:
            attackDamage *= self.attackMultiplier
        return attackDamage

    def setMultiplier(self, mult):
        self.attackMultiplier = mult

    def getAbsorbTargetList(self):
        return [
            suit for suit in self.getBattleCalc().getAliveCogs()
            if suit.getStatusEffectOfId(SEE.EFFECT_AGGRANDIZE)
        ]

    def getDamageTakenDownAvatars(self):
        return [self.av]

    def shouldTrackDamage(self, suit):
        return suit in self.getDamageTakenDownAvatars()

    @property
    def revvingUpStacks(self) -> int:
        return self._revvingUpStacks

    @revvingUpStacks.setter
    def revvingUpStacks(self, stacks) -> None:
        self._revvingUpStacks = min(max(stacks, 0), self.MAX_REVVING_STACKS)
        self.highestRevStacks = max(self.highestRevStacks, self._revvingUpStacks)

        # Update the defense multiplier during phase 2.
        if self.currentPhase == 2:
            self.defenseMultiplier = 0.5 + (0.1 * self._revvingUpStacks)
        else:
            # Update the damage multiplier.
            self.setMultiplier(1 + .10 * self._revvingUpStacks)

    @property
    def revvingUpStackGainMulti(self) -> int:
        return 2 if self.currentPhase == 3 else 1

    @property
    def chainLinkActive(self) -> bool:
        return any([
            (suit.getStatusEffectOfId(SEE.EFFECT_CHAIN_LINKED) and suit.getHp() > 0)
            for suit in self.getBattleCalc().suits
            if suit is not self.av
        ])


class MarkedWoodStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        """Overrides the parent function to check if the invoker of the attack
        in question is the Chainsaw Consultant.
        """
        if invoker is None or (not invoker.isSuit()) or invoker.dna.name != "chainsaw":
            return attackDamage
        return super().handleAttackDamageTaken(attackDamage, attackTrack, invoker)


# Chainsaw Consultant's 'Chain Linked' effect
class ChainLinkedStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    DAMAGE_DOWN_MULT = [0, 0.25, 0.5, 0.75, 1]

    def updateMultiplier(self) -> None:
        """Dynamically determine the damage down multiplier based on
        the amount of chain linked suits in the battle.
        """
        if not self.isAi() or self.av.getHp() <= 0:
            return

        suits = [
            suit for suit in self.getBattle().suits
            if suit.getHp() > 0
            and suit.getStatusEffectOfId(SEE.EFFECT_CHAIN_LINKED)
        ]
        self.multiplier = self.DAMAGE_DOWN_MULT[-len(suits) + suits.index(self.av)]


# A blank status effect, solely used to indicate that the associated Suit
# will absorb damage for the Chainsaw Consultant.
class AggrandizeStatusEffect(StatusEffectBase):

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self._absorbMultiplier = extraArgs[0]
        self.fields = ['absorbMultiplier']

    @property
    def absorbMultiplier(self) -> float:
        if not self.isAi():
            return self._absorbMultiplier

        aggrandizeSuits = [
            suit for suit in self.getBattleCalc().suits
            if suit.getStatusEffectOfId(SEE.EFFECT_AGGRANDIZE)
            and suit.getHp() > 0
        ]
        return 1 / len(aggrandizeSuits) * 0.5


# Pacesetter's status effect, which handles various timescale controls
class PacesetterStatusEffectBase(InstanceMercStatusEffectBase):
    secondJobChance = 0.70
    secondJobOverclockedChance = 0.33

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.fields = ['difficulty', 'timescale', 'maxedOut']
        self._setManualHPGates()

        self.reserveSpawnCount = 3
        self.secondJob = False
        self.thirdJob = False
        self.canSync = False
        self.canMoveGoalposts = False
        self.mistakesMade = 0
        self.actualRounds = 0
        self.spawnCycleRounds = 0
        self.passesHappened = 0
        self.allowChallengeMode = True
        self.inChallengeMode = False
        self.challengeModePhraseSelection = random.randint(0, len(
            TTLocalizer.GeneralAttackSayPhrases[TTLocalizer.SAY_PHRASE_PACESETTER_CHALLENGE_ONE][0]) - 1)

        self.difficulty = extraArgs[0]
        self.timescale = extraArgs[1]
        self.maxedOut = extraArgs[2]

        self.ATTACK_DEFS = {
            'speed_inc': (0.25, 0.30),          # Timescale increase per difficulty
            'max_speed': (4.00, 4.00),          # Max timescale
            'overclocked': (6.00, 6.00),        # The Overclocked timescale
            'hurry_sickness_mult': (.6, .2),    # The amount of attack damage reduction for hurry sickness.
        }

        if self.isAi():
            self.addHPGate(hpRatio=0.80, callback=self.enableSync)
            self.addHPGate(hpRatio=0.66, callback=self.callMoveGoalposts)
            self.addHPGate(hpRatio=0.60, callback=self.enterSecondJob)
            self.addHPGate(hpRatio=0.40, callback=self.overclock)
            self.addHPGate(hpRatio=0.25, callback=self.enterThirdJob)
            self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.PACESETTER_GAG_ORDER])

    def setTimescale(self, timescale):
        self.timescale = timescale
        battle = self.getBattle()
        battle.timescale = timescale
        self.wantShow = True

    def getTimescale(self):
        return self.timescale

    def isMaxed(self):
        return self.maxedOut

    def isInChallengeMode(self):
        return self.inChallengeMode

    def overclock(self):
        """Called once we've hit our HP gate."""
        if not self.maxedOut:
            self.maxedOut = True
            self.__callOverclock()

    def earlyOverclock(self):
        self.disableAttackGeneration()  # Make sure this is off (it should be already but You Never Know)
        self.createAttack(  # Make his second taunt attack
            AttackEnum.PACESETTER_CHALLENGE,
            extraArgs=[TTLocalizer.SAY_PHRASE_PACESETTER_CHALLENGE_TWO, self.challengeModePhraseSelection],
            unlure=True, priority=1000)

        # Get some new HP gates now that we're going into challenge mode
        self.resetHPGates()
        self.addHPGate(hpRatio=0.90, callback=self.enterSecondJob)
        self.addHPGate(hpRatio=0.80, callback=self.enableSync)
        self.addHPGate(hpRatio=0.66, callback=self.callMoveGoalposts)
        self.addHPGate(hpRatio=0.40, callback=self.enterThirdJob)

        # And overclock
        self.overclock()
        self.allowChallengeMode = False
        self.inChallengeMode = True

    def enterSecondJob(self):
        self.secondJob = True

    def enterThirdJob(self):
        self.thirdJob = True

    def handleEndRound(self) -> None:
        if self.maxedOut and not self.canGenerateAttack:
            return self.enableAttackGeneration()

    def handleToonAttackOrder(self, toonAttacks) -> None:
        self.actualRounds += 1
        if not self.allowChallengeMode:
            return

        if not toonAttacks:
            self.passesHappened += 1
        if self.passesHappened < self.actualRounds:
            if self.passesHappened == 1:
                # They have heeded their warning.
                self.enableAttackGeneration()
                self.createAttack(attackType=AttackEnum.PACESETTER_CHALLENGE_CANCELLED, insertMethod='beginning')
            self.allowChallengeMode = False

        else:  # Handle challenge mode warnings
            if self.passesHappened == 2:
                # They have been warned.
                self.earlyOverclock()

            elif self.passesHappened == 1:
                # Warn them of their transgressions.
                self.disableAttackGeneration()
                self.createAttack(
                    AttackEnum.PACESETTER_CHALLENGE,
                    extraArgs=[TTLocalizer.SAY_PHRASE_PACESETTER_CHALLENGE_ONE, self.challengeModePhraseSelection],
                    unlure=True, priority=1000
                )

    def handleRushJobFail(self):
        self.createAttack(AttackEnum.HURRY_SICKNESS, extraArgs=[
            self.getAttackInfo("hurry_sickness_mult"), self.getDifficulty(), self.mistakesMade, False
        ], unlure=True)
        self.mistakesMade += 2 if self.inChallengeMode else 1

    def instanceNaturalSpawns(self, spawnCount: int = None):
        if not self.canGenerateAttack:
            return
        self.spawnCycleRounds += 1
        if self.spawnCycleRounds % 2 == 1:
            self.instanceRequestReserves(spawnCount or self.reserveSpawnCount, overflow=False)

    def changeSpeed(self):
        """Called at the end of all normal attacks."""
        # Always call Rush Job.
        self.__callRushJob()

        # Always call Corporate Restructuring.
        self.__callCorporateRestructuring()

        # Check HP gates now.
        self.fireGates()

        # If we're not overclocked, change speeds.
        if not self.maxedOut:
            self.__callPickUpThePace()

    def enableSync(self):
        self.canSync = True

    def callContentSync(self):
        if self.canSync:
            self.createAttack(AttackEnum.CONTENT_SYNC, unlure=True)

    def callMoveGoalposts(self):
        self.canMoveGoalposts = True
        self.createAttack(AttackEnum.MOVING_GOALPOSTS, unlure=True)

    # Gonna randomize the gag levels every turn via moving goalposts
    def randomizeGagLevels(self):
        if not self.canMoveGoalposts:
            return

        for toon in self.activeToons:
            gagLevelEffects = toon.getStatusEffectsOfId(SEE.EFFECT_MOVING_GOALPOSTS)
            for effect in gagLevelEffects:
                for track in range(len(BattleGlobals.Tracks)):
                    effect.setGagLevel(track, random.choice([4, 5, 6, 7]))

    def badGagLevelUsed(self, attack):
        # Uh oh!! Stinky!! A toon used a bad gag level
        self.createAttack(AttackEnum.HURRY_SICKNESS_MG, targets=[attack.invoker], unlure=True,
                          extraArgs=[self.getAttackInfo("hurry_sickness_mult"), self.getDifficulty(), self.mistakesMade, False])
        self.mistakesMade += 2 if self.inChallengeMode else 1

    def __callCorporateRestructuring(self) -> None:
        if not self.canGenerateAttack:
            return

        self.createAttack(AttackEnum.CORPORATE_RESTRUCTURING, unlure=True)

    def __callRushJob(self) -> None:
        if not self.canGenerateAttack:
            return

        self.createAttack(AttackEnum.RUSH_JOB, extraArgs=[False], unlure=True)

        # See if we are able to do a second rush job.
        if self.secondJob:
            # Roll a chance for second job.
            jobChance = self.secondJobChance if not self.thirdJob else self.secondJobOverclockedChance
            if random.random() < jobChance:
                self.createAttack(AttackEnum.RUSH_JOB, extraArgs=[False], unlure=True)

        # Pull a third job if possible.
        if self.thirdJob:
            self.createAttack(AttackEnum.RUSH_JOB, extraArgs=[False], unlure=True)

    def __callPickUpThePace(self):
        """Call for Pick Up The Pace."""

        # No pacing if we can't generate attacks
        if not self.canGenerateAttack:
            return

        # No pacing if we're at max speed.
        if self.getTimescale() == self.getAttackInfo('max_speed'):
            return

        # Figure out how much to increase the speed by.
        currentSpeed = self.getTimescale()
        newSpeed = min(self.getAttackInfo('max_speed'), self.getTimescale() + self.getAttackInfo('speed_inc'))
        self.setTimescale(newSpeed)

        # At this point, call for a speedup.
        self.createAttack(AttackEnum.PICK_UP_THE_PACE, extraArgs=[self.getTimescale(), currentSpeed], unlure=True)

    def weDied(self):
        # We died!
        # Set the timescale back to 1.0
        self.resetTimescale()
        self.av.removeVisualEffect(VisualEffectEnum.AFTERIMAGE)

    def __callOverclock(self):
        """Call for Overclocked."""
        self.createAttack(AttackEnum.OVERCLOCKED, extraArgs=[self.getTimescale()], unlure=True, priority=42069)
        self.av.addVisualEffect(VisualEffectEnum.AFTERIMAGE)

    def resetTimescale(self):
        self.setTimescale(1.0)
        battle = self.getBattle()
        battle.updateTimescale()

    def onMovieEnd(self):
        if self.maxedOut:
            self.setTimescale(self.getAttackInfo('overclocked'))
            battle = self.getBattle()
            battle.updateTimescale()


class RushJobStatusEffect(SuitDefenseModifierStatusEffect, PinkSlipImmunity, IncomingAttacksBreakAccuracyCap,
                          AvatarTakeModifiedDamageStatusEffect, SuitCannotDodgeStatusEffect):

    VisualSortOrder = 100
    DamageMultiplier = 0.60

    def __init__(self, *args, **kwargs):
        SuitDefenseModifierStatusEffect.__init__(self, *args, **kwargs)
        self.attackType = self.extraArgs[1]
        self.fromAttorney = self.extraArgs[2]
        self.fields += ['attackType', 'fromAttorney']
        self.hasBeenHit = False
        self.cannotDodgeTrack = True

    def getTrack(self):
        return self.attackType

    def roundsRanOut(self):
        # Only do this calculation on the server.
        if self.isAi():
            if not self.hasBeenHit:
                # If we have not been hit, send the fail call only once.
                if not self.getBattleCalc().hasEventBeenSent(BEG.EVENT_PACESETTER_FAILED):
                    self.getBattleCalc().sendEvent(BEG.EVENT_PACESETTER_FAILED)
                # And remove the visual effect at the very end.
                self.createGeneralAttack(
                    attackType=AttackEnum.REMOVE_VISUAL_EFFECT,
                    extraArgs=[VisualEffectEnum.RUSH_JOB.value, 1],
                    targetList=[self.getAv()],
                )
        super().roundsRanOut()

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Handle custom requisites for changing attack damage here in subclasses.
        if self.av.dna.name == 'psetter':
            return attackDamage
        if attackTrack == self.getTrack():
            return attackDamage
        return attackDamage * self.DamageMultiplier

    def handleDamageTaken(self, attackIndex: int) -> None:
        self.hasBeenHit = True
        self.createGeneralAttack(
            attackType=AttackEnum.REMOVE_VISUAL_EFFECT,
            extraArgs=[VisualEffectEnum.RUSH_JOB.value, 1],
            targetList=[self.getAv()],
        )

    def handleSuitDefense(self, suit, suitDefense, attack):
        if attack.attackType == self.getTrack():
            return super().handleSuitDefense(suit, suitDefense, attack)
        else:
            return suitDefense

    def isDodgeDisabled(self, attack) -> bool:
        # If we've already guaranteed a hit, return early.
        if not self.cannotDodgeTrack:
            return

        # If we want Trap, make sure Lure hits.
        if self.getTrack() == AttackEnum.TOON_TRAP:
            attackTypeToCheck = AttackEnum.TOON_LURE
        # If we want Zap, make sure Squirt hits.
        elif self.getTrack() == AttackEnum.TOON_ZAP:
            attackTypeToCheck = AttackEnum.TOON_SQUIRT
        # Otherwise, make sure the track we want hits.
        else:
            attackTypeToCheck = self.getTrack()

        # Guarantee getting hit by the attack if the type matches.
        if attack.attackType == attackTypeToCheck:
            self.cannotDodgeTrack = False
            return True
        else:
            return False

    def accCap_getAttackFilter(self) -> Optional[List[AttackEnum]]:
        return [self.getTrack()]


class HurrySicknessStatusEffect(AttackIOModificationStatusEffect):
    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.fields += ["mode", "fromAttorney"]
        self.mode = self.extraArgs[2]
        # For FTF
        self.fromAttorney = self.extraArgs[3]

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Decrease the amount of healing we take.
        if self.mode == OVERCLOCKED and attackTrack == AttackEnum.TOON_HEAL:
            attackDamage *= self.defenseMultiplier
        return attackDamage


# Multislacker's status effect
class MultislackerStatusEffectBase(InstanceMercStatusEffectBase):
    FodderEffects = {
        None: 20,  # overheal
        SEE.EFFECT_LURE_RESISTANCE: 20,
        SEE.EFFECT_SUIT_DAMAGE_BOOST: 20,
        SEE.EFFECT_FLATTENED_DAMAGE_TAKEN: 20,
        SEE.EFFECT_SOAK_RESISTANCE: 20,
    }

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.removeReservesOnDeath = True
        self.avatarHits = []
        self.roundStartHp = 0
        self.lonelyRounds = 100
        self.mandatoryLunchEnabled = False

        self.ATTACK_DEFS = {
            # How much damage do we take during Out For Lunch
            "OFL_damage_reduction": (0.10, 0.05),
            # How many suits to add to the planner
            "fill_suit_planner": (5, 10),
            # How many rounds can we handle being without friends
            "fill_suit_planner_rounds": (3, 2),
            # Each time we take this much damage in a round, summon friends a round earlier
            "speedup_summon_damage_increment": (400, 400)
        }
        # Index 0: Foreman Level
        # Index 1: Status Effect
        self.foremanInfo = (
            (19, SEE.EFFECT_FOCUSED_DEFENSE),
            (20, SEE.EFFECT_WORKER_MANAGEMENT),
            (21, SEE.EFFECT_UNION_BUST),
        )
        self.foremenRecentlyUsed = []

        self.addHPGate(hpRatio=0.6, callback=self.enableMandatoryLunch)

        if self.isAi():
            self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])

    def cleanup(self):
        if self.cleanedUp:
            return

        del self.avatarHits
        return super().cleanup()

    def enableMandatoryLunch(self):
        self.mandatoryLunchEnabled = True

    def incrementAvatarHits(self, toon) -> None:
        self.avatarHits.append(toon)

    def resetAvatarHits(self) -> None:
        self.avatarHits = []

    def resetRoundStartHp(self) -> None:
        self.roundStartHp = self.getAv().getHp()

    def getAliveFriends(self):
        suits = self.getBattleCalc().suits[:]
        suits.remove(self.getAv())
        return [suit for suit in suits if suit.getHp() > 0]

    def checkAvatarHits(self) -> None:
        if not self.getAliveFriends():
            damageTakenThisRound = self.roundStartHp - self.getAv().getHp()
            damageIncrement = self.getAttackInfo("speedup_summon_damage_increment")
            if damageTakenThisRound > damageIncrement:
                self.lonelyRounds += damageTakenThisRound // damageIncrement

        # Gate zero/hyper task behind there being active fodders,
        # even if they're dead.
        if len(self.getBattleCalc().suits) > 1:
            # Multislacker wasn't hit! Help out the homies in retaliation.
            if not self.avatarHits:
                # Only use zero task if there is anyone to heal, otherwise do nothing.
                unhealthySuits = [suit for suit in self.getBattleCalc().suits if 0 < suit.getHp() < suit.getMaxHp() * 1.25]
                if unhealthySuits:

                    # Heal all of the homies.
                    self.createAttack(AttackEnum.ZERO_TASK, unlure=True, extraArgs=unhealthySuits)
            else:
                # Multislacker has been hit! Crush the toons.
                self.createAttack(AttackEnum.HYPER_TASK, unlure=True)
                self.createAttack(AttackEnum.MS_POWER_TIE, extraArgs=[self.avatarHits], unlure=True)

    def checkOutForLunch(self) -> None:
        av = self.getAv()

        # If there are any suits alive (besides the Multislacker),
        # give the Multislacker the out for lunch status effect.
        if self.getAliveFriends():
            self.addOutForLunchEffect(av)
        else:
            # Otherwise, remove the effect if they already have it.
            av.removeStatusEffectOfId(SEE.EFFECT_OUT_FOR_LUNCH)

    def addOutForLunchEffect(self, av) -> None:
        outForLunch = SEG.createStatusEffect(
            av, SEE.EFFECT_OUT_FOR_LUNCH, extraArgs=[
                self.getAttackInfo("OFL_damage_reduction")
            ]
        )
        av.addStatusEffect(SEE.EFFECT_OUT_FOR_LUNCH, outForLunch)

    def attemptSummonFriends(self) -> None:
        # If we're taking our Mandatory Lunch but the Foreman has been destroyed,
        # We are contractually obligated to rejoin the fight.
        aliveFriends = self.getAliveFriends()
        if not aliveFriends or not self.getBattleCalc().findCogInBattle('msfore', aliveFriends):
            self.avProfile.removeStatusEffectOfId(SEE.EFFECT_LUNCH_BREAK_MSLACKER)
            self.checkOutForLunch()

        usedML = False

        # Use mandatory lunch if the battle isn't full.
        if self.mandatoryLunchEnabled and len(self.getAliveFriends()) < 4:
            # The attack doesn't spawn suits because it's easier to just call this method
            # to summon more friends.
            instance = self.getInstance()
            if instance is not None:
                self.createAttack(AttackEnum.MANDATORY_LUNCH, unlure=True)

                foremanInfoList = []
                for _ in range(2):
                    foremanChoices = [info for info in self.foremanInfo if info not in self.foremenRecentlyUsed]
                    foremanInfo = random.choice(foremanChoices)
                    foremanInfoList.append(foremanInfo)
                    # Keep track of the foremen we have summoned so we don't summon them more often than any other.
                    # If we are summoning the last one, then reset the used list with only the most recent.
                    if len(self.foremenRecentlyUsed) == len(self.foremanInfo) - 1:
                        self.foremenRecentlyUsed = [foremanInfo]
                    else:
                        self.foremenRecentlyUsed.append(foremanInfo)
                self.applyBuffsToReserves(
                    instance.generateMandatoryLunchSuits(foremanInfoList=foremanInfoList)
                )
                # Remove Out for Lunch when going into Mandatory Lunch
                self.avProfile.removeStatusEffectOfId(SEE.EFFECT_OUT_FOR_LUNCH)

                usedML = True

            self.mandatoryLunchEnabled = False

        # Attempt to add more cogs to the level pool if we've had no friends for a
        # given amount of rounds.
        if not aliveFriends:
            self.lonelyRounds += 1
            if self.lonelyRounds > self.getAttackInfo("fill_suit_planner_rounds"):
                self.lonelyRounds = 0
                # Use wasteful management if mandatory lunch wasn't used.
                if usedML:
                    return

                # The attack doesn't do anything because it's easier to just call this method
                # to summon more friends.
                instance = self.getInstance()
                if instance is None:
                    return

                self.createAttack(AttackEnum.WASTEFUL_MGMT, unlure=True)

                self.applyBuffsToReserves(
                    instance.generateReserveSuits(self.getAttackInfo("fill_suit_planner"), overflow=True)
                )
        else:
            self.lonelyRounds = 0

    def applyBuffsToReserves(self, suits) -> None:
        # Each suit spawns with a random buff.
        for suit in suits:
            effect = random.choices(
                list(self.FodderEffects),
                list(self.FodderEffects.values()),
            )[0]
            if effect == SEE.EFFECT_LURE_RESISTANCE:
                suit.addStatusEffect(effect, extraArgs=[-1])
            elif effect == SEE.EFFECT_SUIT_DAMAGE_BOOST:
                suit.addStatusEffect(effect, extraArgs=[1.3, 2])
            elif effect == SEE.EFFECT_FLATTENED_DAMAGE_TAKEN:
                suit.addStatusEffect(effect, extraArgs=[-40])
            elif effect == SEE.EFFECT_SOAK_RESISTANCE:
                suit.addStatusEffect(effect, extraArgs=[0.4])
            else:
                suit.overhealed = True
                suit.b_setHp(math.ceil(suit.getMaxHp() * 1.4))

    def resetLoneliness(self) -> None:
        # If the new suit that joined isn't the Multislacker,
        # reset the loneliness.
        self.lonelyRounds = 0
        self.addOutForLunchEffect(self.getAv())


class SoakResistanceStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Applies multiplier to damage, but only if this suit is soaked.
        if self.av.getStatusEffectOfId(SEE.EFFECT_SUIT_SOAKED):
            attackDamage *= self.getMultiplier()
        return attackDamage


# Rainmaker's status effect
class RainmakerStatusEffectBase(InstanceMercStatusEffectBase, NervousPacingStatusEffect, SuitPreventDeathStatusEffect):
    class WeatherControl(BattleListenerObject):
        """Internal class dedicated to keeping track of the current
        weather phase, what weather phase to go to next, and when
        we need to change the weather phase.

        :param callbacks: The weather phase functions to call.
        """
        weatherCycleLength = 2

        def __init__(self,
                     weatherCycle: List[RainmakerWeather],
                     startWeather: List[RainmakerWeather],
                     endWeather: RainmakerWeather,
                     callbackMap: dict,
                     preCallback: callable,
                     battleListener) -> None:
            # These two variables define some of the properties of the cycles.
            self.weatherCycle = weatherCycle
            self.startWeather = startWeather
            self.endWeather = endWeather

            # This determines the current status of the weather, and general internal state
            self.currentWeatherCycle = []
            self.currentWeather = endWeather
            self.rounds = 1
            self.stopped = False

            # Variable used to overwrite what the currentWeather should be.
            self.forcedWeather = None

            # A callback mapping for weather -> callback funcs.
            self.preCallback = preCallback
            self.callbackMap = callbackMap
            self.weatherPhases = len(weatherCycle)
            self.battleListener = battleListener
            self.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.RAINMAKER_WEATHER])

        def delete(self):
            if not hasattr(self, 'battleListener'):
                return
            self.sendEvent(BEG.EVENT_DESTROY_ENVIRONMENTAL, [ENV_ENUM.RAINMAKER_WEATHER])
            del self.battleListener

        def progressWeather(self):
            if self.hasEventBeenSent(BEG.EVENT_RAINMAKE_WEATHER):
                # Do not attempt to increment rounds if we've changed weather this round.
                return
            if self.stopped:
                return

            # First, increment the amount of rounds.
            self.rounds += 1

            # Every other round (or every round if we're in Inversion), change the weather phase.
            if self.rounds % 2 == 0 or self.currentWeather == RainmakerWeather.NORMAL:
                self.rounds = 0
                self.preCallback()

                # Figure out what our new weather should be.
                if self.forcedWeather is None:
                    # Move forward in the cycle.
                    if not self.currentWeatherCycle:
                        # We are at the end of a cycle -- so create a new one and start there.
                        self.currentWeatherCycle = self.makeNewWeatherCycle()

                    # Now move forward in the existing cycle.
                    self.currentWeather = self.currentWeatherCycle.pop(0)
                else:
                    # Swap to the forced weather.
                    self.currentWeather = self.forcedWeather
                    if self.forcedWeather == RainmakerWeather.MONSOON:
                        # After Monsoon, we have a force inversion with a reset weather cycle.
                        self.currentWeatherCycle = self.makeNewWeatherCycle()
                        self.forcedWeather = RainmakerWeather.NORMAL
                    else:
                        # We'll just reset the forced weather here
                        self.forcedWeather = None

                # Figure out the callback we wanna send.
                callback = self.getCurrentCallback()
                if callback is not None:
                    callback()

                # Send an event dictating change.
                self.sendEvent(BEG.EVENT_RAINMAKE_PRE_TRANSITION)
                self.sendEvent(
                    eventId=BEG.EVENT_RAINMAKE_WEATHER,
                    eventArgs=[self.getCurrentWeather()]
                )

        def getBattleListener(self):
            return self.battleListener

        def setWeatherNow(self, weather: RainmakerWeather):
            self.rounds = -1
            self.forcedWeather = weather
            self.progressWeather()

        def enterFinalState(self):
            self.setWeatherNow(RainmakerWeather.FINALE)
            self.stopped = True

        """
        Weather handler
        """

        DEBUG_WEATHER = []  # [RainmakerWeather.STORM_CELL]

        def makeNewWeatherCycle(self) -> List[RainmakerWeather]:
            """Creates a new weather cycle from scratch."""
            if not self.DEBUG_WEATHER:
                weatherList = self.weatherCycle[:]                    # Start with a blank weather cycle.
                random.shuffle(weatherList)                           # Now shuffle it.
                weatherList = weatherList[0:self.weatherCycleLength]  # Don't use all of it.
                weatherList = self.startWeather + weatherList         # Add the intro to the list.
            else:
                weatherList = self.DEBUG_WEATHER[:]                   # Debug weather cycle :)
            weatherList.append(self.endWeather)                       # Add the final weather.
            return weatherList

        """
        Properties
        """

        def getCurrentWeather(self) -> RainmakerWeather:
            return self.currentWeather

        def getCurrentCallback(self):
            return self.callbackMap.get(self.getCurrentWeather())

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        InstanceMercStatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        NervousPacingStatusEffect.initAttributes(self)
        self.reserveSpawnCount = 2
        self.deathPreventable = True
        self.deathPrevented = False
        self.endingPhase = 0
        self.needRewardCooldownOnToons = False

        self.weatherController = self.WeatherControl(
            weatherCycle=[RainmakerWeather.OIL_RAIN,
                          RainmakerWeather.FOG,
                          RainmakerWeather.HEAVY_RAIN,
                          RainmakerWeather.STORM_CELL],
            startWeather=[],
            endWeather=RainmakerWeather.NORMAL,
            callbackMap={
                RainmakerWeather.OIL_RAIN:   self.weather_OilRain,
                RainmakerWeather.FOG:        self.weather_Fog,
                RainmakerWeather.HEAVY_RAIN: self.weather_HeavyRain,
                RainmakerWeather.STORM_CELL: self.weather_StormCell,
                RainmakerWeather.NORMAL:     self.weather_Inversion,
                RainmakerWeather.MONSOON:    self.weather_Monsoon,
            },
            preCallback=self.weather_preChange,
            battleListener=self.avProfile.getBattleListener(),
        )

        # Specific balancing of the status effects is in RainmakerEnvironmental
        self.ATTACK_DEFS = {
            "storm_cell_zap_damage": 15,   # Storm cell zap damage
            "bad_spawn_phases":  [RainmakerWeather.STORM_CELL],
            "fill_spawn_phases": [RainmakerWeather.STORM_CELL],
        }

        self.addHPGate(hpRatio=0.3, callback=self.requestMonsoon, maxUses=1)
        self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])

    def delete(self):
        if self.cleanedUp:
            return
        super().delete()
        self.weatherController.delete()

    def weatherControl(self) -> None:
        # All of the fun stuff is handled in the weather controller;
        # advancing the weather controller is all we need to do.
        self.attemptEndingCutscene()
        self.weatherController.progressWeather()

    def requestMonsoon(self):
        self.weatherController.setWeatherNow(RainmakerWeather.MONSOON)

    def attemptEndingCutscene(self):
        if self.deathPreventable:
            # Nope -- we aren't on the brink of dying yet.
            return
        self.endingPhase += 1
        if self.endingPhase == 1:
            self.createAttack(AttackEnum.RAINMAKER_ENDING_1)
        elif self.endingPhase == 2:
            self.createAttack(AttackEnum.RAINMAKER_ENDING_2)
        elif self.endingPhase == 3:
            self.createAttack(AttackEnum.RAINMAKER_ENDING_3)
        elif self.endingPhase >= 4:
            self.createAttack(AttackEnum.RAINMAKER_ENDING_4, targets=[self.av])

    def instanceNaturalSpawns(self, spawnCount: int = None):
        # If we prevented death, don't spawn.
        if self.deathPrevented:
            # Set this flag super late to make sure we aren't killed earlier in the turn.
            self.deathPreventable = False
            return

        # We don't want to spawn cogs during certain phases, due to their strength.
        if self.weatherController.getCurrentWeather() in self.getAttackInfo('bad_spawn_phases') \
            and self.weatherController.rounds == 1:
            return

        # Otherwise, spawn normally.
        spawnCount = None if self.weatherController.getCurrentWeather() not in self.getAttackInfo('fill_spawn_phases') else 5
        super().instanceNaturalSpawns(spawnCount=spawnCount)

    def canPreventDeath(self):
        return self.deathPreventable

    def onDeathPrevented(self):
        if self.deathPrevented:
            return
        self.deathPrevented = True

        self.battleCalc.sendEvent(BEG.EVENT_RAINMAKE_DEATH_PREVENTED)

        # End weather state.
        self.weatherController.enterFinalState()

        # Make it so other suits can't attack
        self.addStatusEffectToAllSuits(SEE.EFFECT_CANT_ATTACK, suits=[suit for suit in self.battleCalc.getAliveSuits() if suit is not self.av])
        # Remove all of Rainmaker's attacks, and only insert the new ones we actually need.
        self.battleCalc.removeAllAttacksFromInvoker(self.av)

        # Make all other suits fly away
        targets = []
        for suit in self.battle.aliveSuits:
            if suit.dna.name != 'rainmake':
                targets.append(suit)
        if targets:
            self.createAttack(AttackEnum.COGS_FLY_AWAY, unlure=True, targets=targets)

        # Initial transformation attack.
        self.createAttack(AttackEnum.RAINMAKER_ENDING_0, unlure=True, extraArgs=[
            TTLocalizer.SAY_PHRASE_RAINMAKER_DEATH, 1,
        ])

        # Various effect nonsense
        suitEffect = self.av.getStatusEffectOfType(CogStatusEffect)
        if suitEffect:
            suitEffect.disableAttackGeneration()
        attackEffect = self.av.getStatusEffectOfType(ExtraSuitAttacksStatusEffect)
        if attackEffect:
            attackEffect.delete()
        lureEffect = self.av.getStatusEffectOfType(LureResistanceStatusEffect)
        if lureEffect:
            lureEffect.setAmount(-1)
        self.needRewardCooldownOnToons = True

    def checkApplyFinalRewardCooldown(self):
        if self.needRewardCooldownOnToons:
            self.needRewardCooldownOnToons = False
            for avId in self.battleCalc.toons:
                toon = self.battleCalc.getToon(avId)
                if toon:
                    effect, _ = toon.addStatusEffect(SEE.EFFECT_REWARD_COOLDOWN)
                    effect.wantShow = False
                    effect.setRounds(20)

    """
    Weather phases
    """

    def weather_preChange(self):
        if self.deathPrevented:
            # Delete the storm cell effect
            stormCellEffect = self.av.getStatusEffectOfId(SEE.EFFECT_STORM_CELL)
            if stormCellEffect:
                stormCellEffect.delete()
            # Don't create any of these attacks if we're in our "death" state
            return

        if self.weatherController.getCurrentWeather() == RainmakerWeather.HEAVY_RAIN:
            self.createAttack(AttackEnum.HEAVY_RAIN_ZAP, unlure=True)
        elif self.weatherController.getCurrentWeather() == RainmakerWeather.STORM_CELL:
            stormCellEffect = self.av.getStatusEffectOfId(SEE.EFFECT_STORM_CELL)
            if stormCellEffect:
                self.createAttack(AttackEnum.STORM_CELL_ZAP, unlure=True, extraArgs=[stormCellEffect.getRounds()])
                stormCellEffect.delete()

    def weather_OilRain(self) -> None:
        self.createAttack(AttackEnum.WEATHER_OIL_RAIN, unlure=True, extraArgs=[
            TTLocalizer.SAY_PHRASE_WEATHER_OIL_RAIN, 1,
        ])

    def weather_Fog(self) -> None:
        self.createAttack(AttackEnum.WEATHER_FOG, unlure=True, extraArgs=[
            TTLocalizer.SAY_PHRASE_WEATHER_FOG, 1,
        ])

    def weather_HeavyRain(self) -> None:
        self.createAttack(AttackEnum.WEATHER_HEAVY_RAIN, unlure=True, extraArgs=[
            TTLocalizer.SAY_PHRASE_WEATHER_HEAVY_RAIN, 1,
        ])

    def weather_StormCell(self) -> None:
        self.createAttack(AttackEnum.WEATHER_STORM_CELL, unlure=True, extraArgs=[
            TTLocalizer.SAY_PHRASE_WEATHER_STORM_CELL,
        ], targets=[self.getAv()])

    def weather_Inversion(self) -> None:
        self.reserveSpawnCount = 2
        self.createAttack(AttackEnum.WEATHER_INVERSION, unlure=True, extraArgs=[
            TTLocalizer.SAY_PHRASE_WEATHER_INVERSION], targets=[self.getAv()])

    def weather_Monsoon(self):
        self.reserveSpawnCount = 0
        self.createAttack(AttackEnum.WEATHER_MONSOON, unlure=True, extraArgs=[
            TTLocalizer.SAY_PHRASE_WEATHER_MONSOON,
        ])


class OilRainHealStatusEffect(SuitHealOverTimeStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wasDeathPrevented = False
        self.inheritedEventDefinitions.append(SEE.EFFECT_OIL_RAIN_HOT)

    def rainmakerDeathPrevented(self):
        self.wasDeathPrevented = True

    def applyHeal(self):
        if self.cleanedUp:
            return
        if self.wasDeathPrevented:
            # No heals to Suits if her death was prevented.
            return
        suit = self.getAv()
        # If the suit is already at max HP (including overheal), we don't need a heal.
        healthPercentage = suit.getHp() / suit.getMaxHp()
        if healthPercentage >= self.healthCap:
            return
        # Make sure the suit isn't dead either
        if suit.getHp() <= 0:
            return
        self.createGeneralAttack(
            AttackEnum.SUIT_HEAL,
            extraArgs=[self.amount, self.additive, self.healthCap],
            targetList=[self.getAv()]
        )


class OilRainDamageStatusEffect(ToonDamageOverTimeStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wasDeathPrevented = False
        self.inheritedEventDefinitions.append(SEE.EFFECT_OIL_RAIN_DOT)

    def rainmakerDeathPrevented(self):
        self.wasDeathPrevented = True

    def applyDamage(self):
        if self.cleanedUp:
            return
        if self.wasDeathPrevented:
            # No damage to Toons if her death was prevented.
            return
        self.createGeneralAttack(
            AttackEnum.OIL_RAIN_DOT,
            extraArgs=[-self.amount],
            targetList=[self.getAv()]
        )


class HeavyRainStatusEffect(AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damageAbsorbed = 0
        self.fields.append('damageAbsorbed')
        self.buffedDamageIncrease = self.extraArgs[1]

    def getDamageAbsorbed(self) -> int:
        return round(self.damageAbsorbed)

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        # Make sure it is heavy rain currently.
        if self.isAi():
            envEffect = self.battleCalc.getEnvironmentalOfType(EnvironmentalEnum.RAINMAKER_WEATHER)
            if not envEffect:
                return attackDamage
            if envEffect.getWeather() == RainmakerWeather.HEAVY_RAIN and self.battleCalc.hasEventBeenSent(BEG.EVENT_RAINMAKE_PRE_TRANSITION):
                return attackDamage

        # Handle custom requisites for changing attack damage here in subclasses.
        attackDamage *= (self.buffedDamageIncrease / 100)
        return attackDamage

    def handleAbsorbedDamageTaken(self, attackDamage):
        # Run the damage absorption calculation and return the damage we want to absorb (The value from handleAttackDamageTaken)
        damageAbsorbed = math.floor(attackDamage * (1 - self.getMultiplier()))
        self.damageAbsorbed += damageAbsorbed
        return damageAbsorbed


class StormCellStatusEffect(StatusEffectBase):

    DecrementPerGag = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions = [SEE.EFFECT_STORM_CELL]

    def decrement(self, amount):
        super().decrement(self.DecrementPerGag)


class MonsoonStatusEffect(AttackAccuracyStatusEffect, RewardCooldownStatusEffect):

    def __init__(self, *args, **kwargs):
        AttackAccuracyStatusEffect.__init__(self, *args, **kwargs)

    def roundsRanOut(self):
        AttackAccuracyStatusEffect.roundsRanOut(self)


# This status effect will create a specified number of specific
# general attacks upon expiry.
class DelayedAttackStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False
        self.attackAmount = extraArgs[0]
        self.attackType = extraArgs[1]
        self.attackExtraArgs = extraArgs[2]
        self.fields = ["attackAmount", "attackType", "attackExtraArgs"]

    def roundsRanOut(self):
        calculator = self.getBattleCalc()

        for _ in range(self.attackAmount):
            aliveToons = [toon for toon in calculator.getAllToons() if toon.getHp() > 0]
            self.createGeneralAttack(self.attackType, self.attackExtraArgs, targetList=[random.choice(aliveToons)])

        super().roundsRanOut()


# Major Player's status effect
class MajorPlayerStatusEffect(InstanceMercStatusEffectBase):

    dancingDamageDealt = {
        # Dance accuracy to damage dealt.
        -0.01: 40,  # less than zero for math reasonz
        0.60: 32,
        0.70: 24,
        0.80: 16,
        0.90: 8,
        1.00: 0,
    }
    nukeDamageRatio = (0.03, 999)

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        InstanceMercStatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)

        # Some revive attributes.
        self.revive = bool(hasattr(self.av, 'anAbsoluteLegendReally')) or extraArgs[1]
        self.revive_readyForStar = False
        self.wantShow = True
        self.fields += ['revive']

        # End the fight when we die during phase 2.
        self.endFightOnDeath = self.revive

        self.needShowStarBonusValue = 0

        # Queue up the rhythm game to occur.
        if self.isAi():
            if not self.revive:
                self.addHPGate(hpRatio=0.70, callback=self.createRhythmAttack)
                self.addHPGate(hpRatio=0.40, callback=self.createRhythmAttack)

                # Add the environmental.
                self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.MAJOR_PLAYER_REVIVE_HANDLER])
            else:
                self.addHPGate(hpRatio=0.50, callback=self.createRhythmAttack)

                # Add the environmental.
                self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.MAJOR_PLAYER_SHUFFLE_HANDLER])

    def delete(self):
        if self.cleanedUp:
            return

        # Remove all of the the stars of the show on dying in phase 1.
        if not self.revive:
            for suit in self.getBattleCalc().suits:
                effect = suit.getStatusEffectOfId(SEE.EFFECT_STAR_OF_THE_SHOW)
                if effect:
                    effect.delete()

        return super().delete()

    def handleStarOfTheShow(self):
        """
        Every 3 rounds, starting on round 2, the Major Player will select
        an audience member as a willing volunteer to join the show!
        That is, if the battle isn't full.
        """
        if self.hasRevived():
            return
        if self.battleCalc.getCurrentRound() % 5 == 1:
            # Dance partners should happen this turn, so we queue for the next. We cannot overlap.
            return
        if len(self.getBattle().activeSuits) <= 5:
            self.createAttack(attackType=AttackEnum.STAR_OF_THE_SHOW, unlure=True, priority=1015)

    def handleRevivedStarOfTheShow(self):
        """
        He uses Star of the Show at the end of every round when revived.
        Except the first one when he comes home xd
        """
        if not self.hasRevived():
            return
        if not self.revive_readyForStar:
            self.revive_readyForStar = True
            return
        if len(self.getBattle().activeSuits) <= 5:
            self.createAttack(attackType=AttackEnum.STAR_OF_THE_SHOW, unlure=True, priority=1015)

    def handleGuestVerse(self):
        """
        Every other round, starting on round 2, the Major Player will
        choose 1 friend to do an additional attack, applying Viral Sensation
        effect onto a toon.
        """
        if len(self.battleCalc.getAliveCogs()) > 1:
            self.createAttack(
                attackType=AttackEnum.GUEST_VERSE_START,
                unlure=True,
                extraArgs=[self.hasRevived()]
            )

    def handleDancePartners(self):
        """
        Every 3 rounds, starting on round 1, the Major Player will
        completely fill the battle and assign dance partners to each Toon.
        """
        if self.hasRevived():
            return
        self.createAttack(attackType=AttackEnum.DANCE_PARTNERS, unlure=True, priority=1015)

    def applyBuffs(self):
        # In phase 2, we need to apply new versions of our buffs to the cogs.
        if self.hasRevived():
            otherSuits = [suit for suit in self.battleCalc.getAliveCogs() if suit != self.avProfile]

            # Before other buffs are applied, we are going to ensure every suit has a fresh 2 round lure resistance.
            # This is to prevent any weird issues with overlapping resistance/immunity effects
            for suit in otherSuits:
                if suit.hasStatusEffectOfId(SEE.EFFECT_STAR_OF_THE_SHOW):
                    lureResist = suit.getStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE)
                    if lureResist:
                        lureResist.delete()
                    suit.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE, extraArgs=[2])

            self.getInstance().oopsAllBuffs(
                otherSuits,
                reviveOverride=False,
                isActive=True
            )

    def handleBeginRound(self):
        if self.hasRevived():
            # Refresh lure immune present flag at beginning of every round
            self.getInstance().immunePresent = False

    def suitDied(self, suit):
        lureEffect = suit.getStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE)
        if lureEffect and lureEffect.getAmount() == -1:
            self.getBattle().instance.immunePresent = False

    def createRhythmAttack(self) -> None:
        if self.av.getHp() <= 0:
            return
        self.getBattleCalc().sendEvent(BEG.EVENT_MPLAYER_HWA)

    def handleRhythm(self, notesDict: dict, totalNotes: int) -> None:
        if self.av.getHp() <= 0:
            return
        damageDict = {}
        damageRatios = list(self.dancingDamageDealt.keys())
        badRatio, nukeDamage = self.nukeDamageRatio
        for avId, notes in notesDict.items():
            # ratio
            ratio = sum(notes) / totalNotes
            if ratio < badRatio and self.revive:
                damageDict[avId] = nukeDamage
                continue
            for ratioA, ratioB in zip(damageRatios, damageRatios[1:]):
                if ratioA < ratio <= ratioB:
                    damage = self.dancingDamageDealt[ratioB]
                    if damage:
                        damageDict[avId] = damage
                    break

        # Create the RIR attack
        self.createGeneralAttack(
            AttackEnum.ROCKING_IN_RHYTHM,
            extraArgs=[damageDict],
        )

    def addToonStarBonus(self, value):
        self.needShowStarBonusValue += value

    def checkToonStarBonus(self):
        # Check if we need to show a bonus for Toons gaining star of the show bonus
        if self.needShowStarBonusValue:
            self.createGeneralAttack(AttackEnum.TOON_STAR_BONUS_TEXT, extraArgs=[self.needShowStarBonusValue])

        self.needShowStarBonusValue = 0

    """
    Getters
    """

    def hasRevived(self):
        return self.revive

    def isVisible(self):
        return False


# Literally just the cogs damage down effect except it's hidden. :)
# (also will apply the effect before all other damage buffs)
class MajorPlayerPhaseTwoDamageDownStatusEffect(AttackEffectivenessStatusEffect):
    SortPriority = 1000

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = False


class StarOfTheShowStatusEffect(AdditiveDamageBoostStatusEffect, MinibossResistancesStatusEffect):
    """
    The rising damage boost given to audience members.
    Also handles Last Tap.
    """

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        AdditiveDamageBoostStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.minibossImmunitiesActive = True
        self.fields.extend(['mode'])
        self.mode = extraArgs[1]
        self.superstar = extraArgs[1] == 1
        self.lastTap = extraArgs[1] == 2

        # On initial AI application, deliver the COOL BUFFS.
        if self.isAi() and not self.isLastTap():
            hpIncrease = 425 if not self.superstar else 625
            self.av.b_setMaxHp(self.av.getMaxHp() + hpIncrease)
            # Because of fodder buffs, we may already be getting lure immunity, so don't give lure resist yet.
            if not self.hasStartingLure():
                self.createLureResistanceStatusEffect(2)

    def delete(self):
        if self.cleanedUp:
            return

        if self.av.getHp() > 0:
            # Return their health back to normality.
            healthPercentage = self.av.getHealthPercentage()
            self.av.setMaxHp(self.av.calculateHp())
            self.av.setHp(self.av.getHp() * healthPercentage)

            # Display the effect dying.
            self.createGeneralAttack(
                AttackEnum.STAR_OF_THE_SHOW_END,
                targetList=[self.av],
                extraArgs=[self.av.getHp(), self.av.getMaxHp()]
            )

        return super().delete()

    def weDied(self) -> None:
        # Give a +15 damage boost to each toon present when a
        # Star of the Show dies. It will apply at the end of the round.

        self.battleCalc.sendEvent(BEG.EVENT_MPLAYER_ADD_STAR_BONUS, [15])

    def hasStartingLure(self):
        if not self.av.startingStatusEffects:
            return
        for effect in self.av.startingStatusEffects:
            if effect['effectId'] == SEE.EFFECT_LURE_RESISTANCE:
                return True
        return False

    def isSuperstar(self) -> bool:
        """YOURE A SUPERSTAR !!!!"""
        return self.superstar

    def isLastTap(self):
        """last tap? more like last cr"""
        return self.lastTap

    def onRoundEnd(self):
        # Boost damage at the end of every round.
        self.multiplier += 5 if not self.isLastTap() else 1


class GuestVerseStatusEffect(AttackAccuracyStatusEffect):
    """
    When Major Player chooses a Suit to perform a Guest Verse, the Suit will
    get this invisible status effect to watch for when the Suit successfully
    hits a Toon. Then, they will apply the status effect to said Toon.
    """


    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.hitToons = []
        self.attacksAfter = 1

    def handleAttackAccuracy(self, attackTrack, attackAccuracy):
        attack = self.getBattleCalc().attackOrder.getAttacksOfInvoker(self.avProfile)[-1]
        if attack:
            if len(attack.targets) > 1:
                attackAccuracy = 80
            else:
                attackAccuracy = 90
            self.override = attackAccuracy
        return attackAccuracy, self.override

    def suitHit(self, toon, suit):
        if suit == self.av:
            self.hitToons.append(toon)

    def timeForVirus(self):
        # We've gone to the next attack, which doesn't exist yet. BUT it's about to, because we will apply
        # mean status effects to the toons!
        if self.attacksAfter > 0:
            self.attacksAfter -= 1
            return

        isStar = self.av.hasStatusEffectOfId(SEE.EFFECT_STAR_OF_THE_SHOW)

        for toon in self.hitToons:
            toon.addStatusEffect(SEE.EFFECT_VIRAL_SENSATION)

        # This attack will secretly apply Viral Sensation to the toons, and reset our stage light.
        self.createAttack(
            AttackEnum.GUEST_VERSE_END,
            extraArgs=[self.battle.hasRevived, isStar],
            priority=1005
        )

        # This attack will let the toons know about the misery they were just afflicted with.
        if self.hitToons:
            self.createGeneralAttack(
                AttackEnum.SHOW_HP_TEXT,
                targetList=self.hitToons,
                extraArgs=[TTLocalizer.HP_TEXT_VIRAL_SENSATION],
                insertKwargs=dict(priority=1010)
            )

        # This status effect is a bit stubborn about its rounds expiring, so we'll just tell it that it's done.
        self.roundsRanOut()


class ViralSensationStatusEffect(AdditiveDamageBoostNoToonup, AttackAccuracyStatusEffect):
    """
    When a Toon is hit with a Guest Verse attack, they will be given increased damage, but
    lower accuracy on higher level Gags.
    """

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = False
        self.multiplier = extraArgs[0]
        self.accDecrease = self.extraArgs[1]
        self.levelCap = self.extraArgs[2]
        self.fields = ['multiplier', 'accDecrease', 'levelCap']

    def handleAttackAccuracy(self, attackTrack: int, attackAccuracy):
        # So this override function doesn't really let you figure out what level the Gag is, so we'll find it.

        attacks = self.battleCalc.attackOrder.getAttacksOfInvoker(self.av)
        gagAttack = [attack for attack in attacks if attack.track == attackTrack]
        if not gagAttack:
            return 0, -1  # This should never happen but just in case
        gagAttack = gagAttack[0]

        # Remove accDecrease accuracy from the attack per every level the gag is past the levelCap
        attackAccuracy -= (self.accDecrease * max(gagAttack.level - self.levelCap, 0))

        return attackAccuracy, -1


class DancePartnerStatusEffect(AttackEffectivenessStatusEffect, AttackTargetGhostwriter):
    """
    Major Player will assign for a random Toon and Suit to both have this status effect.
    The Toon and Suit will become "conjoined" in this regard, and deal bonus damage
    to each other. They will, however, be weaker to other targets.

    When the owner of this status effect perishes, both effects will clear.
    """

    match_toon_damageMultiplier = 1.50  # How much more damage a Toon will deal when the effects match.
    match_suit_damageMultiplier = 1.25  # How much more damage a Suit will deal when the effects match.
    wrong_toon_damageMultiplier = 0.25  # How much less damage a Toon will deal when the effects don't match.
    wrong_suit_damageMultiplier = 0.75  # How much less damage a Suit will deal when the effects don't match.

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        StatusEffectBase.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.multiplier = 1.00  # init this I GUESS
        self.combines = False

        # Interpret our extra arguments.
        self.effectIndex, self.avId_A, self.avId_B = extraArgs
        self.fields = ['effectIndex', 'avId_A', 'avId_B']

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        # Determine if we are a toon or suit first.
        if target is None:
            return attackDamage
        targetId = target if type(target) is int else target.doId
        match = self.doesAvIdMatch(targetId)
        if self.av.isSuit():
            attackDamage *= self.match_suit_damageMultiplier if match else self.wrong_suit_damageMultiplier
        elif self.av.isToon():
            # Don't do anything if it's toon-up.
            if attackTrack == AttackEnum.TOON_HEAL:
                return attackDamage
            attackDamage *= self.match_toon_damageMultiplier if match else self.wrong_toon_damageMultiplier
        return attackDamage

    def handleAvatarDied(self, av):
        # Called whenever a Toon or Suit is removed from the battle.
        if self.cleanedUp:
            return
        if self.doesAvIdMatch(av.doId):
            # Our partner is gone -- we can cleanup.
            self.delete()

    def determineNewTargets(self, attack) -> Optional[list]:
        """
        Determines the new targets of this attack.
        If there are no overrides, returns None.
        Otherwise, return a list of valid battle avatars.
        """
        av = self.getBattle().getToon(self.getOppositeAvId())
        if av is not None:
            return [av]

    """
    Useful methods
    """

    def getEffectIndex(self) -> int:
        return round(self.effectIndex)

    def doesAvIdMatch(self, avId, includeSelf: bool = False) -> bool:
        """Determines if we are 'matching' with an avId."""
        if not self.av:
            # we literally do not exist
            return False
        if avId == self.av.doId and not includeSelf:
            # We do not match with ourselves
            return False
        return avId == int(self.avId_A) or avId == int(self.avId_B)

    def getOppositeAvId(self) -> int:
        """Returns the opposite matching avId."""
        if self.av.doId == self.avId_A:
            return self.avId_B
        return self.avId_A


class SiphonStatusEffect(AttackEffectivenessStatusEffect):

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.healingMult = extraArgs[1]
        self.healingCap = extraArgs[2]
        self.fields += ['healingMult', 'healingCap']

    def onSuitAttack(self, suit, damageAmount):
        if suit is self.av and damageAmount < 0:
            self.createGeneralAttack(
                AttackEnum.SUIT_HEAL,
                targetList=[self.av],
                extraArgs=[damageAmount * self.healingMult * -1, True, self.healingCap]
            )


# Witch Hunter status effect
class WitchHunterStatusEffect(InstanceMercStatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.endFightOnDeath = True
        self.cheatRounds = 0
        self.wantShow = True

        if len(extraArgs) > 1:
            self.client_currentMobSize = extraArgs[1]
        else:
            self.client_currentMobSize = 0
        self.fields += ["currentMobSize"]

        self.ATTACK_DEFS = {
            "trial_by_fire_rounds": (3, 1),                     # Trial by fire frequency
            "mob_mentality_rounds": (2, 2),                     # Mob Mentality frequency
        }

        # How many members can be in the mob
        self.maxMobMembers = 8

        # How many members add to the mob
        self.mobMembersPerFill = 5

        # The next round that we should increase our fill rate
        self.nextFillIncreaseRound = None

        # Is Rally Cry active? (desperation)
        self.rallyCryActive = False

        # Should we force filling the mob this round?
        self.forceFillMob = False

        # Should our next trial by fire be replaced by boilerplate?
        self.needBoilerplate = False

        # Use boilerplate twice
        self.addHPGate(0.33, self.handleBoilerplate)
        self.addHPGate(0.66, self.handleBoilerplate)

        # Go into Rally Cry at low HP (desperation)
        self.addHPGate(0.7, self.handleRallyCry)

        # Setup functions
        if self.isAi():
            self.determineNextFillIncreaseRound()
            resistEffect = self.av.getStatusEffectOfType(LureResistanceStatusEffect)
            if resistEffect:
                resistEffect.wantShow = False

    def weDied(self) -> None:
        # When we die, clear Trial By Fire from all toons.
        for toon in self.getBattleCalc().getAliveToons():
            toon.removeStatusEffectOfId(SEE.EFFECT_TRIAL_BY_FIRE)

    def handleBoilerplate(self) -> None:
        self.needBoilerplate = True

    def handleRallyCry(self) -> None:
        self.rallyCryActive = True
        self.maxMobMembers = 16

    def determineNextFillIncreaseRound(self):
        if self.mobMembersPerFill == 4:
            roundsPerFillIncrease = self.getAttackInfo("mob_mentality_rounds") * 2
        elif self.mobMembersPerFill == 5:
            roundsPerFillIncrease = self.getAttackInfo("mob_mentality_rounds") * 4
        elif self.mobMembersPerFill >= 6:
            roundsPerFillIncrease = self.getAttackInfo("mob_mentality_rounds") * 6
        self.nextFillIncreaseRound = self.cheatRounds + roundsPerFillIncrease - (self.cheatRounds % self.getAttackInfo("mob_mentality_rounds"))

    def handleCheats(self) -> None:
        self.cheatRounds += 1

        # Increase how many members we're adding every fill on certain rounds (every other mob mentality)
        if self.cheatRounds >= self.nextFillIncreaseRound:
            self.mobMembersPerFill += 1
            self.determineNextFillIncreaseRound()

        if self.cheatRounds % self.getAttackInfo("trial_by_fire_rounds") == 0:
            self.handleTrialByFire()

        # Only use mob mentality if there are actually suits to buff.
        if self.cheatRounds % self.getAttackInfo("mob_mentality_rounds") == 0 or self.forceFillMob:
            if self.forceFillMob and not self.cheatRounds % self.getAttackInfo("mob_mentality_rounds") == 0:
                self.forceFillMob = False
            self.handleMobMentality()

    def handleMobMentality(self):
        # Determine cheat strength by mob size
        if self.currentMobSize >= 13:
            suitsTargeted = 4
        elif self.currentMobSize >= 6:
            suitsTargeted = 3
        else:
            suitsTargeted = 2

        # How many member should we fill the mob with?
        fillAmount = self.mobMembersPerFill + (1 if self.rallyCryActive else 0)

        self.createAttack(AttackEnum.MOB_MENTALITY, extraArgs=[
            suitsTargeted,
            self.maxMobMembers,
            fillAmount
        ], unlure=True)

    def handleTrialByFire(self) -> None:
        if self.needBoilerplate:
            self.createAttack(AttackEnum.BOILERPLATE, extraArgs=[0.1, 0.8], unlure=True)
            self.needBoilerplate = False
        else:
            # Determine cheat strength by mob size
            if self.currentMobSize >= 13:
                dotAmount = 0.15
            elif self.currentMobSize >= 8:
                dotAmount = 0.15
            elif self.currentMobSize >= 6:
                dotAmount = 0.10
            else:
                dotAmount = 0.05

            numTargets = 2 if self.currentMobSize >= 3 else 1
            self.createAttack(AttackEnum.TRIAL_BY_FIRE, extraArgs=[
                dotAmount,
                numTargets,
            ], unlure=True)

    def handleBewitchment(self) -> None:
        """Applies the bewitchment effect to the highest laff toon."""
        toons = self.getBattleCalc().getAliveToons()
        if not toons:
            return

        targetChoices = sorted(toons, key=lambda t: t.getHp(), reverse=True)
        targets = targetChoices[:min(2 if self.currentMobSize >= 6 else 1, len(targetChoices))]

        # Determine cheat strength by mob size
        if self.currentMobSize >= 13:
            vulnerability = 1.3
        elif self.currentMobSize >= 8:
            vulnerability = 1.25
        elif self.currentMobSize >= 6:
            vulnerability = 1.2
        elif self.currentMobSize >= 3:
            vulnerability = 1.15
        else:
            vulnerability = 1.10

        self.createAttack(
            AttackEnum.BEWITCHMENT,
            targets=targets,
            unlure=True,
            extraArgs=[vulnerability],
        )

    @property
    def currentMobSize(self) -> int:
        if not getattr(self.getBattle(), "instance", None):
            return 0
        return len(self.getBattle().instance.reserveSuits)


# Works the same as a ToonDamageOverTimeStatusEffect, except the damage is a % of
# the toon's max health.
class ToonPercentDamageOverTimeStatusEffect(ToonDamageOverTimeStatusEffect):
    DamageAttackType = AttackEnum.TOON_DAMAGE

    def applyDamage(self):
        maxHp, hp = self.getAv().getMaxHp(), self.getAv().getHp()
        # Floor the damage to be consistent with all other suit damage calcs, but also
        # don't do absolutely zero damage either. (this can happen with 1 laff ubers)
        damage = max(min(math.floor(maxHp * self.amount), hp), 1)
        self.createGeneralAttack(
            attackType=self.DamageAttackType,
            extraArgs=[-damage],
            targetList=[self.getAv()]
        )


# Trial by Fire
class TrialByFireStatusEffect(ToonPercentDamageOverTimeStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.cheatRounds = 0
        self.combines = True
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE]
        self.amount = extraArgs[0]  # DOT multi
        self.fields = ['amount']

    def combine(self, otherEffect):
        # If we're combining the effect, let's reset the rounds
        # so we don't take double damage (once from the attack and once from here) this round.
        self.cheatRounds = 0

        otherRounds = otherEffect.getRounds()
        otherAmount = otherEffect.getAmount()

        # Take highest of rounds
        self.setRounds(max(self.rounds, otherRounds), adjust=False)

        if otherAmount > self.getAmount():
            self.setAmount(otherAmount)

    def applyDamage(self):
        # Don't apply damage on the first turn
        self.cheatRounds += 1
        if self.cheatRounds <= 1:
            return
        return super().applyDamage()

    def handleSoaked(self) -> None:
        self.createGeneralAttack(
            AttackEnum.REMOVE_VISUAL_EFFECT,
            extraArgs=[VisualEffectEnum.TRIAL_BY_FIRE.value],
            targetList=[self.getAv()],
        )
        self.delete()


# Bewitchment
class BewitchmentStatusEffect(AggroModifierStatusEffect, AttackIOModificationStatusEffect):

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        AggroModifierStatusEffect.__init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.attackMultiplier = extraArgs[3]
        self.defenseMultiplier = extraArgs[4]
        self.fields += ['attackMultiplier', 'defenseMultiplier']

    # The bewitched toon does extra damage to Witch Hunter.
    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        if target and target.dna.name == "whunter":
            attackDamage *= self.attackMultiplier
        return attackDamage


# Plutocrat status effect
class PlutocratStatusEffect(InstanceMercStatusEffectBase, AdditiveDamageBoostStatusEffect,
                            AvatarTakeModifiedDamageStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = True

        self.reserveSpawnCount = 2
        self.endFightOnDeath = True
        self.toggleSnowSquall = True

        if len(extraArgs) > 1:
            self.marketBubbleStacks = extraArgs[1]
        else:
            self.marketBubbleStacks = 0

        self.fields += ["marketBubbleStacks"]

        self.ATTACK_DEFS = {
            "deep_freeze_rounds": (2, 3),  # How many rounds should deep freeze last for?
            "slush_fund_dr": (0.6, 0.2),  # How much DR should slush fund apply to cogs?
        }

        # The Plutocrat will force the Toons go after the suits
        # for a few rounds at each hp gate.
        self.addHPGate(0.4, self.handleDeepFreeze)
        self.addHPGate(0.8, self.handleDeepFreeze)

        # The Plutocrat will spawn in the remaining two investors one at a time at certain HP gates.
        self.addHPGate(0.4, self.spawnInvestor)
        self.addHPGate(0.8, self.spawnInvestor)

        if self.isAi():
            self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.PLUTOCRAT_WEATHER])
            self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])

    def delete(self):
        if self.cleanedUp:
            return
        if self.isAi():
            self.getBattleCalc().sendEvent(BEG.EVENT_DESTROY_ENVIRONMENTAL, [ENV_ENUM.PLUTOCRAT_WEATHER])
            self.getBattleCalc().sendEvent(BEG.EVENT_DESTROY_ENVIRONMENTAL, [ENV_ENUM.OVERCHARGE_ALL])
        super().delete()

    def spawnInvestor(self) -> None:
        # Only works when in the instance.
        instance = self.getInstance()
        if instance:
            instance.instanceInfo['battle_cap'] += 1
            instance.battle.maxSuits += 1
            instance.reserveSuits.append(instance.genInvestorSuit())

    def handleDeepFreeze(self) -> None:
        # Set a priority so that this goes at the end of the round, but still before snow squall
        self.createAttack(AttackEnum.DEEP_FREEZE, extraArgs=[
            self.getAttackInfo("deep_freeze_rounds"),
        ], insertMethod="end", unlure=True, priority=1000)

    def handleSlushFund(self) -> None:
        battleCalc = self.getBattleCalc()
        investors = [suit for suit in battleCalc.getAliveCogs() if suit.getStatusEffectOfType(SatelliteInvestorStatusEffectBase)]
        # If there are investors in the fight, have one of them perform Slush Fund instead.
        if investors:
            battleCalc.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                AttackEnum.SLUSH_FUND, {"invoker": investors[0], "unlure": True, "extraArgs": [
                    self.getAttackInfo("slush_fund_dr"),
                ]},
                {"mode": "beginning"}
            ])
        else:
            self.createAttack(AttackEnum.SLUSH_FUND, extraArgs=[
                self.getAttackInfo("slush_fund_dr"),
            ], insertMethod="beginning", unlure=True)

    def handleSnowSquall(self) -> None:
        self.createAttack(AttackEnum.SNOW_SQUALL, extraArgs=[
            TTLocalizer.SAY_PHRASE_PCRAT_SNOW_SQUALL_ENTER \
                if self.toggleSnowSquall else TTLocalizer.SAY_PHRASE_PCRAT_SNOW_SQUALL_EXIT,
            self.toggleSnowSquall
        ], unlure=True, priority=2000)  # a very low priority to make sure snow squall is always at the end
        self.toggleSnowSquall = not self.toggleSnowSquall

    def handleReceivedDamage(self, attackType: AttackEnum) -> None:
        if self.marketBubbleStacks > 0 and attackType == AttackEnum.SHATTER_DAMAGE:
            # Set to -2 to prevent it from immediately going away at the
            # end of the turn.
            self.marketBubbleStacks = -2

        elif self.marketBubbleStacks >= 0:
            # Increment the amount of hits taken.
            self.marketBubbleStacks += 1

    def handleRoundEnded(self) -> None:
        if self.marketBubbleStacks <= -1:
            self.marketBubbleStacks += 1

    def getMultiplier(self) -> None:
        if self.marketBubbleStacks <= 0:
            return 0
        return self.marketBubbleStacks * 3

    def getVulnerabilityDamage(self) -> None:
        if self.marketBubbleStacks <= -1:
            return 1.25
        return 1

    def getShatterMultiplier(self) -> None:
        return 1 + min(0.05 * self.marketBubbleStacks, 1)

    def handleAttackDamageTaken(self, attackDamage, attackTrack: int, invoker):
        if self.marketBubbleStacks >= 0 and attackTrack == AttackEnum.SHATTER_DAMAGE:
            return attackDamage * self.getShatterMultiplier()
        return attackDamage * self.getVulnerabilityDamage()


# Base class used for all Satellite Investors
class SatelliteInvestorStatusEffectBase(InstanceMercStatusEffectBase):
    InvestorMembers = ['charon', 'nix', 'hydra', 'styx', 'kerberos']

    def __init__(self, *args):
        super().__init__(*args)
        self.combines = False
        self.inheritedEventDefinitions += [SEE.EFFECT_SATELLITE_INVESTOR_MANAGER]
        self.wantShow = False
        self.hasMembers = {}
        self.resistingLure = False
        # Do initial population of our dict of satellite investors.
        self.updateInvestorMembers(ignoreHp=True)
        self.attackId2Type = {}

    def updateInvestorMembers(self, ignoreHp=False):
        # We don't need to care about this if we're dead.
        if self.getAv().getHp() <= 0 and not ignoreHp:
            return

        # Update our list of the cogs we have with us.
        for member in self.InvestorMembers:
            suit = self.getBattleCalc().findCogInBattle(member)
            self.hasMembers[member] = True if suit and suit.getHp() > 0 else False

    def suitDied(self, suit):
        # Don't give the ghost payroll when the Plutocrat is in the battle.
        if self.getBattleCalc().findCogInBattle("pcrat"):
            return

        # A suit died, check if we need to increase lure resistance
        if all([s.dna.name in self.InvestorMembers for s in (self.getAv(), suit)]):
            # Cool, go ahead and try to create a new lure resistance (ghost payroll) effect
            # Even if we already have one, the combine will handle everything we need
            self.createLureResistanceStatusEffect()
            self.createGeneralAttack(AttackEnum.GHOST_PAYROLL_HEAL)

    def createLureResistanceStatusEffect(self, rounds=2):
        ghostPayroll = SEG.createStatusEffect(self.getAv(), SEE.EFFECT_GHOST_PAYROLL)
        self.getAv().addStatusEffect(SEE.EFFECT_GHOST_PAYROLL, ghostPayroll)


# Charon status effect
class CharonStatusEffect(SatelliteInvestorStatusEffectBase):
    AbsorbChanceIncPerRound = 0.25

    def __init__(self, *args):
        super().__init__(*args)
        self.absorbChance = 0.25

        self.ATTACK_DEFS = {
            "absorb_mult": (0.6, 0.4),  # How much damage Charon absorbs with Standup Guy.
        }

    def handleBeginRound(self):
        self.absorbChance += self.AbsorbChanceIncPerRound
        if random.random() < self.absorbChance:
            # We hit the chance, add the standup guy attack to give him damage absorb for the turn
            self.createAttack(AttackEnum.STANDUP_GUY, "beginning", extraArgs=[
                TTLocalizer.SAY_PHRASE_STANDUP_GUY,
                self.getAttackInfo("absorb_mult"),
            ], unlure=True)
            # Clear out the absorb chance now that we've added the attack
            self.absorbChance = 0


# Nix status effect
class NixStatusEffect(SatelliteInvestorStatusEffectBase):

    def __init__(self, *args):
        super().__init__(*args)
        self.ATTACK_DEFS = {
            "shakedown_rounds": (2, 3),  # How many rounds to put the toon on unite cd?
            "shakedown_dr": (1.2, 1.4),  # How much damage vulnerability do toons receive?
        }

    def handleBeginRound(self) -> None:
        self.createAttack(AttackEnum.SHAKEDOWN, "beginning", extraArgs=[
            self.getAttackInfo("shakedown_rounds"),
            self.getAttackInfo("shakedown_dr"),
        ], unlure=True)


# Hydra status effect
class HydraStatusEffect(SatelliteInvestorStatusEffectBase):

    def __init__(self, *args):
        super().__init__(*args)
        self.ATTACK_DEFS = {
            "kickup_dmg_boost": (1.1, 1.2),  # How much to boost damage by?
        }

    def handleKickUp(self) -> None:
        self.createAttack(AttackEnum.KICK_UP, insertMethod="index", extraArgs=[
            self.getAttackInfo("kickup_dmg_boost")
        ], unlure=True, insertArgs={"adjust": False})


# Styx status effect
class StyxStatusEffect(SatelliteInvestorStatusEffectBase):

    def __init__(self, *args):
        super().__init__(*args)
        self.ATTACK_DEFS = {
            "waiter_level": (15, 15),  # What level is the waiter summon?
        }

    def handleSitdown(self) -> None:
        # Sitdown will only occur if the waiter has a spot to sit down, otherwise usury will occur
        if self.hasWaiter:
            return

        if len(self.battle.activeSuits) >= self.battle.maxSuits:
            self.createAttack(AttackEnum.USURY, unlure=True, extraArgs=[False], priority=3)
            return

        self.createAttack(AttackEnum.SITDOWN, extraArgs=[
            self.getAttackInfo("waiter_level"), self.getInstance()
        ], unlure=True, priority=3)

    def handleUsury(self) -> None:
        if not self.hasWaiter:
            return

        self.createAttack(AttackEnum.USURY, unlure=True, extraArgs=[True])

    @property
    def hasWaiter(self) -> bool:
        for suit in self.getBattleCalc().suits:
            if suit.isWaiter:
                return True
        return False


# Kerberos status effect
class KerberosStatusEffect(SatelliteInvestorStatusEffectBase):

    def handleTribute(self) -> None:
        self.createAttack(AttackEnum.TRIBUTE, unlure=True)


# Gives a damage boost
class GhostPayrollEffect(AttackEffectivenessStatusEffect):
    damageBoosts = {
        1: 1.3,
        2: 1.6,
    }

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        self.howManyDied = extraArgs[0]
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.wantShow = True
        self.combines = True
        self.fields = ['howManyDied']

    def combine(self, otherEffect):
        self.howManyDied += 1

    def getHowManyDied(self):
        return self.howManyDied

    def getMultiplier(self):
        # Pass as an int for the client's sake
        return self.damageBoosts[int(self.howManyDied)]


# Woodchipper status effect
# Deals damage to a toon over multiple rounds.
class WoodchipperStatusEffect(ToonDamageOverTimeStatusEffect):
    def applyDamage(self):
        self.createGeneralAttack(
            AttackEnum.WOODCHIPPER_DAMAGE,
            extraArgs=[-self.amount],
        )


class SparkPlugStatusEffect(ToonDamageOverTimeStatusEffect):
    def applyDamage(self):
        self.createGeneralAttack(
            AttackEnum.SPARK_PLUG_DAMAGE,
            extraArgs=[-self.amount],
            targetList=[self.getAv()]
        )
# endregion


# High Roller's status effect
class HighRollerStatusEffectBase(InstanceMercStatusEffectBase, MinibossResistancesStatusEffect):
    phaseOneAndAHalfHP = 1  # This is how much HP you need to whittle him down to to get him to phase 1.5
    phaseTwoHP = 44444  # This is how much HP he'll have when he goes into phase 2

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.punishedToons = []
        from toontown.instances.HighRollerGlobals import HighRollerGameEnum
        self.games = [
            HighRollerGameEnum.TRIVIA,
            HighRollerGameEnum.SHUFFLE,
            HighRollerGameEnum.PUZZLE,
        ]
        self.previousGame = None
        self.disabledEffectsDuringMinigames = [
            SEE.EFFECT_TOON_DAMAGE_UP,
            SEE.EFFECT_TOON_MULT_DAMAGE_UP,
            SEE.EFFECT_ENCORE,
            SEE.EFFECT_TOONS_ACCURACY_UP,
            SEE.EFFECT_CHEER,
            SEE.EFFECT_DICE_COOLDOWN,
            SEE.EFFECT_PIP_DISCOUNT,
        ]
        self.currentGame = HighRollerGameEnum.BETWEEN
        self.wantShow = False
        self.levelDamage = 0
        self.currentPhase = 1
        self.getAv().noRegularAttackRounds = -1
        self.isAITHTurn = False
        self.randomAttacks = 0
        self.pointInfo = {}
        self.wantPointOSD = True
        self.endFightOnDeath = True

        self.addHPGate(hpRatio=self.phaseOneAndAHalfHP, callback=self.startPhaseOneAndAHalf, isRatio=False)

        if self.isAi():
            self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.ADAPTIVE_LAFF])

    """
    Multi-phase functions
    """

    def addShowHostEffect(self):
        av = self.getAv()
        showHost = SEG.createStatusEffect(
            av, SEE.EFFECT_SHOW_HOST
        )
        av.addStatusEffect(SEE.EFFECT_SHOW_HOST, showHost)

    def handleSuitDied(self, suit, invoker, attackType):
        if self.currentPhase == 1:
            # Adds damage based on cog levels to a total, applied to High Roller after toons attack
            from toontown.instances.HighRollerGlobals import HighRollerGameEnum
            if self.getInstance().currentGame == HighRollerGameEnum.BETWEEN and invoker.isToon():
                self.levelDamage += suit.getActualLevel() * (7 if suit.isElite else 4)
                self.getInstance().commercialSuitsKilled += 1
        elif self.currentPhase == 1.5:
            if len(self.battleCalc.getAliveCogs()) <= 1 and attackType != AttackEnum.FINISH_BETWEEN:
                self.startPhaseTwo()
        elif self.currentPhase == 2:
            self.updateHarmoniousColors(len(self.getBattleCalc().getAliveCogs()) - 1)
            cloneEffect = suit.getStatusEffectOfId(SEE.EFFECT_HIGHROLLER_CLONE)
            if not cloneEffect:
                return
            cloneId = cloneEffect.getType()
            self.avProfile.sendEvent(
                eventId=BEG.EVENT_HROLL_KILL_CLONE,
                eventArgs=[cloneId]
            )
            if len(self.battleCalc.getAliveCogs()) <= 1:
                self.av.removeVisualEffectOfId(VisualEffectEnum.ROLLED)

    """
    Phase transitions
    """

    def wipeStatusesAndPips(self, startingPips: int = 0):
        for toon in self.getBattleCalc().getAliveToons():
            for effect in toon.getStatusEffects()[:]:
                if effect.effectId == SEE.EFFECT_PIP_COUNTER:
                    effect: PipCounterEffect
                    effect.decrementPoints(effect.getPointCount() - startingPips)
                elif SEG.StatusEffectId2Type.get(effect.effectId) == SEG.BUFF:
                    effect.delete()

    def startPhaseOneAndAHalf(self):
        from toontown.instances.HighRollerGlobals import HighRollerGameEnum
        self.currentGame = HighRollerGameEnum.BETWEEN
        self.createAttack(AttackEnum.FINISH_BETWEEN)

        self.createAttack(AttackEnum.HIGHROLLER_HOLLYWOOD, priority=100100)

        # Force Toon laff to 150
        toons = self.getBattleCalc().getAliveToons()
        for toon in toons:
            self.getBattleCalc().sendEvent(BEG.EVENT_ADAPTIVE_LAFF,
                                           eventArgs=[toon, 150, 'set'])
        # Show a cute movie here showing their max laff gain
        laffGain = [150 - toon.getMaxHp() for toon in self.getBattleCalc().getAliveToons()]
        self.createGeneralAttack(
            AttackEnum.HR_TOON_LAFF_UP, targetList=list(self.getBattleCalc().getAliveToons()),
            extraArgs=[0.0 if self.wantPointOSD else 2.0, *laffGain], insertKwargs=dict(priority=110000)
        )
        self.getBattleCalc().sendEvent(BEG.EVENT_HROLL_FORCE_MAX_LAFF_MOVIE)
        self.wipeStatusesAndPips(startingPips=4)
        self.currentPhase = 1.5
        self.getInstance().setCurrentPhase(self.currentPhase)

    def startPhaseTwo(self):
        # Sets current phase on status effect and instance
        self.currentPhase = 2
        self.getInstance().setCurrentPhase(self.currentPhase)

        # Update High Roller max health
        av = self.getAv()
        av.b_setMaxHp(self.phaseTwoHP)
        if not av.getStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE):
            av.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE,
                               SEG.createStatusEffect(av, SEE.EFFECT_LURE_RESISTANCE, extraArgs=[1]))

        # Force Toon laff to 999
        toons = self.getBattleCalc().getAliveToons()
        for toon in toons:
            self.getBattleCalc().sendEvent(BEG.EVENT_ADAPTIVE_LAFF,
                                           eventArgs=[toon, 999, 'set'])
        # Show a cute movie here showing their max laff gain
        laffGain = [999 - toon.getMaxHp() for toon in self.getBattleCalc().getAliveToons()]
        self.createGeneralAttack(
            AttackEnum.HR_TOON_LAFF_UP, targetList=list(self.getBattleCalc().getAliveToons()),
            extraArgs=[0.0 if self.wantPointOSD else 2.0, *laffGain], insertKwargs=dict(priority=110000)
        )
        self.getBattleCalc().sendEvent(BEG.EVENT_HROLL_FORCE_MAX_LAFF_MOVIE)
        self.wipeStatusesAndPips()

        # No more invulnerability, but harmonious colors activates
        av.removeStatusEffectOfId(SEE.EFFECT_SHOW_HOST)
        harmoniousColors = SEG.createStatusEffect(
            av, SEE.EFFECT_HARMONIOUS_COLORS, extraArgs=[1.0, 0.05]
        )
        av.addStatusEffect(SEE.EFFECT_HARMONIOUS_COLORS, harmoniousColors)

        # High Roller stands between his clones
        self.getAv().setBattleOrderPriority(BattleOrderPriority.MIDDLE)

        # Create the clone environmental
        self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.HIGH_ROLLER_CLONE_HANDLER])

        # Create the attack for the transition to phase 2
        self.createAttack(AttackEnum.HIGHROLLER_BEGIN_MADNESS, priority=100100)

        # Kiddie gloves come off, time to attack!
        self.randomAttacks = 2

        # Add an HP gate to do the Ace in the Hole attack
        self.addHPGate(hpRatio=0.65, callback=self.doAceInTheHoleTurn)

    """
    Phase one
    """

    def handleLevelDamage(self):
        # Applies attack based on level damage recorded during toon round
        if self.currentGame == HighRollerGameEnum.BETWEEN and self.levelDamage > 0:
            # Debug pipeline to hollywoods
            # self.levelDamage *= 60
            # High Roller can only take a certain amount of damage before he transitions to phase 1.5.
            cappedDamage = max(min(self.levelDamage, self.getAv().getHp() - self.phaseOneAndAHalfHP), 0)

            self.createGeneralAttack(
                AttackEnum.HIGHROLLER_LEVEL_DAMAGE,
                extraArgs=[-(cappedDamage)],
                targetList=[self.getAv()]
            )
            self.levelDamage = 0

    def handleRandomGame(self):
        """
        High Roller creates an attack which sets up a new random game.
        """
        if self.currentPhase != 1:
            return

        # When the games start, we'll leave the show host ability on until phase 2.
        if not self.getAv().getStatusEffectOfId(SEE.EFFECT_SHOW_HOST):
            self.addShowHostEffect()
        if self.getAv().getStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE):
            self.getAv().removeStatusEffectOfId(SEE.EFFECT_LURE_RESISTANCE)

        if self.getAv().getStatusEffectOfId(SEE.EFFECT_SUIT_LURED):
            self.createAttack(AttackEnum.SUIT_UNLURE, targets=[self.getAv()], unlure=True)

        # Randomly select a game, ignoring the previous game that was selected.
        eligibleGames = self.games.copy()
        if self.previousGame is not None:
            eligibleGames.remove(self.previousGame)
        self.currentGame = random.choice(eligibleGames)
        self.previousGame = self.currentGame

        # Disable all buffs and dice effects.
        for toon in self.getBattleCalc().getAliveToons():
            for effectId in self.disabledEffectsDuringMinigames:
                for effect in toon.getStatusEffectsOfId(effectId):
                    effect.setDisabledRounds(1)
        # Give ourselves a status effect saying that all buffs have been disabled.
        self.getAv().addStatusEffect(SEE.EFFECT_HIGHROLLER_MINIGAME_HOST)

        self.createAttack(AttackEnum.FINISH_BETWEEN, unlure=True)

        self.createAttack(AttackEnum.SPIN_WHEEL, extraArgs=[self.currentGame], priority=100000, unlure=True)

        gameArgs = []
        if self.currentGame in (HighRollerGameEnum.TRIVIA, HighRollerGameEnum.PUZZLE):  # Unused for puzzle, but we need it here
            epicQuestionIndex = random.randint(0, len(TTLocalizer.HighRollerQuestions) - 1)
            gameArgs = [epicQuestionIndex]
        elif self.currentGame == HighRollerGameEnum.SHUFFLE:
            realSlimShady = random.randint(0, 3)
            gameArgs = [realSlimShady]

        self.createAttack(AttackEnum.RANDOM_GAME, extraArgs=[self.currentGame, *gameArgs], priority=100050, unlure=True)
        self.wantPointOSD = False
        self.punishedToons = []

    def handleGameWrong(self, toons):
        self.punishedToons += [toon for toon in toons
                               if toon not in self.punishedToons]

    def handleGameFinish(self):
        if self.currentPhase != 1:
            return

        from toontown.instances.HighRollerGlobals import HighRollerGameEnum, getPipReward
        aliveSuits = [suit for suit in self.getBattleCalc().suits if suit.getHp() > 0]
        leftoverSuitNum = len(aliveSuits) - 1

        # If we're on puzzle game and the punished toons list is already populated,
        # that means the toons didn't use the right gag.
        # In this case, we want to give them 2 fewer pips.
        wantExtraPunishment = self.currentGame == HighRollerGameEnum.PUZZLE and self.punishedToons

        if leftoverSuitNum > 0:
            self.createAttack(AttackEnum.RANDOM_GAME_FINISH, unlure=True)
            if self.currentGame == HighRollerGameEnum.PUZZLE:
                self.punishedToons = self.activeToons

        self.wantPointOSD = False

        for toon in self.getBattleCalc().getAliveToons():
            pointCounter = toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
            if not pointCounter:
                continue
            self.giveToonPoints(toon, getPipReward(self.currentGame, toon not in self.punishedToons, leftoverSuitNum, wantExtraPunishment))

        self.currentGame = HighRollerGameEnum.BETWEEN

        self.createAttack(AttackEnum.RANDOM_GAME_PUNISH,
                          extraArgs=[self.punishedToons, leftoverSuitNum, wantExtraPunishment],
                          priority=100200, unlure=True)

        self.createAttack(AttackEnum.HIGHROLLER_COMMERCIAL, priority=100300, unlure=True)

    """
    Phase two
    """

    def generateAttack(self):
        if self.randomAttacks == 0:
            return

        # Remove untouchable
        if self.av.getVisualEffectOfId(VisualEffectEnum.HR_UNTOUCHABLE):
            self.createAttack(AttackEnum.HR_EXIT_UNTOUCHABLE)

        # Check HP gates before generating attacks.
        self.fireGates()

        # Generate 2 attacks
        attacks = [AttackEnum.ACE_IN_THE_HOLE] if self.isAITHTurn else []
        self.isAITHTurn = False
        while len(attacks) < self.randomAttacks:
            choice = self.av.getRandomAttack()
            if choice not in attacks:
                attacks.append(choice)

        [self.getBattleCalc().sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
            attack, dict(invoker=self.getAv()), dict(priority=99990-i, overrideInserted=False)
        ]) for i, attack in enumerate(attacks)]
        # To debug certain attacks just replace reversed(attacks) with a list of AttackEnums you want him to use each turn.

    def doAceInTheHoleTurn(self):
        self.isAITHTurn = True

    def handlePhaseTwo(self):
        if self.currentPhase != 2:
            return

        # We only want to spawn new clones if we had a round of nonactivity with only the manager in the fight.
        if len(self.getBattleCalc().suits) != 1:
            return

        self.createAttack(AttackEnum.TRICK_OF_THE_LIGHT, priority=100200)

        self.updateHarmoniousColors(4)

    def updateHarmoniousColors(self, numClones):
        harmoniousColors = self.getAv().getStatusEffectOfId(SEE.EFFECT_HARMONIOUS_COLORS)
        if not harmoniousColors:
            return
        harmoniousColors.updateReduct(numClones)

    """
    Point system
    """

    def resetPointInfo(self):
        self.pointInfo = {toon: 0 for toon in self.getBattleCalc().getAliveToons()}
        self.wantPointOSD = True

    def giveToonPoints(self, toon, amount):
        if toon not in self.pointInfo:
            return
        pointCounter = toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
        if pointCounter:
            self.pointInfo[toon] += pointCounter.increment(amount)

    def giveAllToonsPoints(self, amount):
        for toon in self.pointInfo:
            self.giveToonPoints(toon, amount)

    def spendPointsOnGags(self, allAttacks):
        if self.pointInfo == {}:
            self.resetPointInfo()  # Needs to be done at the very beginning of the battle.
        trackDict: dict = {}

        for attack in allAttacks:
            if not getattr(attack, "invoker", None) or getattr(attack, "track", None) not in BattleGlobals.ATTACK_TRACKS:
                continue
            if attack.track not in trackDict:
                trackDict[attack.track] = []
            trackDict[attack.track].append(attack)

        for attackTrack, attackList in trackDict.items():
            targetList = []
            extraArgs = [0.0]
            for attack in attackList:
                pointCounter = attack.invoker.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
                if not pointCounter:
                    continue

                targetList.append(attack.invoker)
                extraArgs.append(-pointCounter.spendPoints(attack))

            idx = self.battleCalc.attackOrder.getAttacks().index(attackList[0])
            self.createGeneralAttack(
                AttackEnum.SHOW_PIP_TEXT, targetList=targetList, extraArgs=extraArgs,
                insertKwargs=dict(index=idx, adjust=False, respectPreviousAdditions=False))

    def roundStartPoints(self):
        from toontown.instances.HighRollerGlobals import HighRollerGameEnum
        laffGain = 0
        if self.currentPhase == 1:
            if self.currentGame == HighRollerGameEnum.PUZZLE:
                numPoints = 8
            else:
                numPoints = 2
            toons = self.getBattleCalc().getAliveToons()
            laffGain = int(numPoints * 1.5)
            for toon in toons:
                self.getBattleCalc().sendEvent(BEG.EVENT_ADAPTIVE_LAFF,
                                               eventArgs=[toon, laffGain, 'addToCap'])
            self.giveAllToonsPoints(numPoints)
        elif self.currentPhase == 1.5:
            self.giveAllToonsPoints(6)
        elif self.currentPhase == 2:
            self.giveAllToonsPoints(8)

        if any(self.pointInfo.values()):
            self.createGeneralAttack(
                AttackEnum.SHOW_PIP_TEXT, targetList=list(self.pointInfo.keys()),
                extraArgs=[2.0 if self.wantPointOSD else 0.0, *list(self.pointInfo.values())],
                insertKwargs=dict(priority=100600))
        if laffGain and not self.getBattleCalc().hasEventBeenSent(BEG.EVENT_HROLL_FORCE_MAX_LAFF_MOVIE):
            self.createGeneralAttack(
                AttackEnum.HR_TOON_LAFF_UP, targetList=list(self.getBattleCalc().getAliveToons()),
                extraArgs=[0.0 if self.wantPointOSD else 2.0, *[laffGain] * 4], insertKwargs=dict(priority=100700)
            )
        self.resetPointInfo()

    def handleToonAdded(self, toon):
        effect, combined = toon.addStatusEffect(effectId=SEE.EFFECT_PIP_COUNTER)
        # Start off with 7 pips so that we can use the golden dice, plus 1 level 1 gag.
        effect.setRounds(7, adjust=False)


class HighRollerShowHostEffect(UntouchableStatusEffect):
    """
    High Roller, being the show host and all, can't be attacked after the first round.
    Well, at the very least, not until he's unleashed his true power in phase 3.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = True

    def isVisible(self):
        # The client will still receive this status effect,
        # it just won't show on the status effect panel.
        return False


class HarmoniousColorsEffect(AttackIOModificationStatusEffect):
    VisualSortOrder = 1000
    attackReduct = (1.0, 0.2, 0.15, 0.1, 0.05)

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = False
        if self.isAi():
            self.defenseMultiplier = self.attackReduct[-1]

    def updateReduct(self, numClones):
        self.defenseMultiplier = self.attackReduct[numClones]

    def isVisible(self):
        return (self.defenseMultiplier < 1.0) or (self.av.hasStatusEffectOfId(SEE.EFFECT_HR_UNTOUCHABLE))


class HighRollerQuestionEffect(SuitCannotDodgeStatusEffect, PinkSlipImmunity, IncomingAttacksBreakAccuracyCap):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.getAv().noRegularAttackRounds = -1
        self.inheritedEventDefinitions.append(SEE.EFFECT_QUESTION)
        if self.isAi():
            self.letterIndex = self.extraArgs[1]
            self.fields = ['letterIndex']
        else:
            self.letterIndex = self.extraArgs[0]

    def checkAnswer(self, toonAttacks):
        pass

    def isDodgeDisabled(self, attack) -> bool:
        return True


class FlunkyTriviaEffect(ObscureHPStatusEffect, HighRollerQuestionEffect, SuitPreventDeathStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.visualEffectEnums = [VisualEffectEnum.HIGHROLLER_TRIVIA]
        self.isCorrect = extraArgs[0]

        if self.isAi():
            self.nameIndex = extraArgs[1]
            self.questionIndex = extraArgs[2]
            self.fields.append('questionIndex')
        else:
            self.nameIndex = extraArgs[0]
            self.questionIndex = extraArgs[1]

    def checkAnswer(self, toonAttacks):
        def getSideTargets(attack):
            if getattr(attack, "track", None) != AttackEnum.TOON_SQUIRT:
                return []
            sideTargets = []
            i = attack.suits.index(attack.targets[0])
            if i > 0:
                sideTargets.append(attack.suits[i - 1])
            if i < len(attack.suits) - 1:
                sideTargets.append(attack.suits[i + 1])
            return sideTargets

        damagedBy = [attack.invoker for attack in toonAttacks if self.getAv() in attack.targets + getSideTargets(attack)]
        # The suit wasn't hit, but it was supposed to be (you missed the correct answer).
        if self.isCorrect:
            self.getBattleCalc().sendEvent(BEG.EVENT_HROLL_QUESTION_WRONG,
                eventArgs=[[toon for toon in self.activeToons if toon not in damagedBy]])
        else:
            self.getBattleCalc().sendEvent(BEG.EVENT_HROLL_QUESTION_WRONG, eventArgs=[damagedBy])

    def isAnswerCorrect(self):
        if self.questionIndex != -1 and self.nameIndex != -1:
            return TTLocalizer.HighRollerQuestions[int(self.questionIndex)][int(self.nameIndex)][1]
        else:
            return False

    def getName(self):
        if self.questionIndex != -1 and self.nameIndex != -1:
            return TTLocalizer.HighRollerQuestions[int(self.questionIndex)][int(self.nameIndex)][0]
        else:
            return "???"


class PuzzleShowEffect(HighRollerQuestionEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        if self.isAi():
            self.track = self.extraArgs[2]
            self.fields += ['track']
        else:
            self.track = self.extraArgs[1]

    def checkAnswer(self, toonAttacks):
        # If our set track wasn't used in attacks...
        if self.track not in [getattr(attack, "track", None) for attack in toonAttacks if hasattr(attack, "track")]:
            # Punish everyone.
            self.getBattleCalc().sendEvent(BEG.EVENT_HROLL_QUESTION_WRONG, eventArgs=[self.activeToons])

    def getTrack(self):
        return self.track


class CogShuffleEffect(ObscureHPStatusEffect, HighRollerQuestionEffect, SuitPreventDeathStatusEffect):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.isCorrect = extraArgs[0]
        self.letterIndex = extraArgs[1]
        self.fields = ['isCorrect', 'letterIndex']
        self.visualEffectEnums = [VisualEffectEnum.HIGHROLLER_TRIVIA]

    def checkAnswer(self, toonAttacks):
        def getSideTargets(attack):
            if getattr(attack, "track", None) != AttackEnum.TOON_SQUIRT:
                return []
            sideTargets = []
            i = attack.suits.index(attack.targets[0])
            if i > 0:
                sideTargets.append(attack.suits[i - 1])
            if i < len(attack.suits) - 1:
                sideTargets.append(attack.suits[i + 1])
            return sideTargets

        damagedBy = [attack.invoker for attack in toonAttacks if self.getAv() in attack.targets + getSideTargets(attack)]
        # The suit wasn't hit, but it was supposed to be (you missed the correct answer).
        if self.isCorrect:
            self.getBattleCalc().sendEvent(BEG.EVENT_HROLL_QUESTION_WRONG,
                eventArgs=[[toon for toon in self.activeToons if toon not in damagedBy]])
        else:
            self.getBattleCalc().sendEvent(BEG.EVENT_HROLL_QUESTION_WRONG, eventArgs=[damagedBy])

    def isAnswerCorrect(self):
        return self.isCorrect


class HollywoodStarStatusEffect(AdditiveDamageBoostStatusEffect):
    """
    The rising damage boost given to High Roller's hollywoods.
    """
    VisualSortOrder = 1000

    def onRoundEnd(self):
        # Boost damage at the end of every round.
        self.multiplier += 5

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        return super().handleAttackDamage(attackTrack, attackDamage, target) - 10


class HighRollerCloneStatusEffect(StatusEffectBase):
    """
    The clones kinda just sit here and be of a certain type while the environmental does all the work.
    """

    VisualSortOrder = 1000

    TOONUP = 0
    TRAP = 1
    LURE = 2
    THROW = 3
    SQUIRT = 4
    ZAP = 5
    SOUND = 6
    DROP = 7

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.visualEffectEnums = [VisualEffectEnum.HIGHROLLER_CLONE]

        # Set the type parameters of the clone.
        self.type = extraArgs[0]
        self.fields = ['type']

    def getType(self):
        return self.type


class RaisingTheAnteEffect(AdditiveDamageBoostStatusEffect):
    VisualSortOrder = 4999

    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        if attackTrack == AttackEnum.TOON_HEAL:
            return (attackDamage * 10)
        # For whatever reason, sometimes this function gets passed an id, so let's convert it over.
        if isinstance(target, int):
            if self.isAi():
                target = simbase.air.getDo(target)
            else:
                target = base.cr.getDo(target)
        if (target and not target.getStatusEffectOfId(
            SEE.EFFECT_HIGHROLLER_SHIELD_SUIT)):
            return (attackDamage * 10)
        # The multiplier here is the damage down for clones.
        # It's easier to handle it on the toon's side than the suit's side.
        return max((attackDamage * 10) + self.getMultiplier(), 0)


class FakeSoakStatusEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.combines = True

    def combine(self, otherEffect):
        otherRounds = otherEffect.getRounds()
        # If the other effect's rounds are higher, replace ours with them
        # Or if the other effect's rounds are infinite, make ours infinite
        if otherRounds > self.getRounds() or otherRounds == SEG.NO_ROUNDS:
            self.setRounds(otherRounds, adjust=False)


class PipCounterEffect(StatusEffectBase):
    VisualSortOrder = 5000

    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)
        self.updateGagList(rounds)

    @property
    def cooldownEffects(self):
        effects = self.av.getStatusEffectsOfId(SEE.EFFECT_DICE_COOLDOWN)
        effects.sort(key=lambda e: int(e.pip))
        return effects

    def increment(self, amount):
        realAmount = min(amount, 99 - self.rounds)
        super().increment(realAmount)
        self.updateGagList(self.rounds)
        return realAmount

    def updateGagList(self, pointLevel: int, lastAttack = None):
        av = self.getAv()
        if not av or not self.isAi():
            return
        inv: GagInventoryBase = av.inventory
        inv.zeroInv()

        discount = 0
        discountEffect = av.getStatusEffectOfId(SEE.EFFECT_PIP_DISCOUNT)
        if discountEffect:
            discount = discountEffect.getActiveDiscount()

        if self.getRounds() > 0 or discount > 0:
            for track in range(len(BattleGlobals.Tracks)):
                for level in range(min(pointLevel + discount, 8)):
                    inv.addItem(track=track, level=level)

        # hack to make sure the player isn't missing a gag
        if lastAttack:
            inv.addItem(track=lastAttack.track, level=lastAttack.level)

        av.d_setInventory(inv.makeNetString())

    def spendPoints(self, attack):
        av = self.getAv()
        if not av or attack.invoker != av:
            return 0  # Returning 0 because we need to return an int

        amount = min(HighRollerGlobals.getPipCost(av, attack.track, attack.level), self.rounds)
        self.rounds -= amount
        self.updateGagList(self.rounds, attack)
        return amount

    def decrement(self, amount):
        pass

    def decrementPoints(self, points: int):
        self.rounds -= points
        if self.rounds < 0:
            self.rounds = 0
        self.updateGagList(self.rounds)

    def getPointCount(self) -> int:
        return self.rounds


class PipDiscountEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)

        self.discount = extraArgs[0]
        self.fields = ['discount']

    def getDiscount(self) -> int:
        # Mainly used for string purposes on the client
        return self.discount

    def getActiveDiscount(self) -> int:
        if self.isDisabled():
            return 0
        return self.getDiscount()


class DiceCooldownEffect(StatusEffectBase):
    def __init__(self, avProfile, effectId, rounds, disabledRounds, extraArgs):
        super().__init__(avProfile, effectId, rounds, disabledRounds, extraArgs)

        self.pip = extraArgs[0]
        self.combines = False
        self.fields += ['pip']

    def setPip(self, pip):
        self.pip = pip

    def getPip(self) -> int:
        return int(self.pip) if not self.isDisabled() else -1


class AceInTheHoleVulnerabilityEffect(AvatarTakeModifiedDamageStatusEffect):
    VisualSortOrder = 4998


class HighRollerToonGagsUnlocked(FlagBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wantShow = True

    def isVisible(self):
        return False


class HighRollerUntouchableStatusEffect(UntouchableStatusEffect):
    @staticmethod
    def canBeTrapped():
        return True

# endregion


# region find the family effects

class FindTheFamilyBaseEffect(StatusEffectBase):
    VisualSortOrder = 500

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions = [SEE.DEFINITION_OC_FAMILY_BASE]

    @property
    def specialContainer(self):
        # Hooked up to the corresponding special container owned by this FTF suit
        return self.av.specialContainer


class FindTheFamilySellbotEffect(FindTheFamilyBaseEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions += [SEE.DEFINITION_OC_FAMILY_S]


class FindTheFamilyCashbotEffect(FindTheFamilyBaseEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions += [SEE.DEFINITION_OC_FAMILY_M]

    def handleObjectionFailure(self, fromSuit):
        # For the sake of the confused supervisor lol
        if fromSuit is not self.av:
            return

        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.OBJECTION_OVERRULED,
            {"unlure": True, "invoker": self.getAv()},
            {"respectPreviousAdditions": True}
        )


class FindTheFamilyLawbotEffect(FindTheFamilyBaseEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions += [SEE.DEFINITION_OC_FAMILY_L]

    def handleObjectionFailure(self, fromSuit):
        if fromSuit is not self.av:
            return

        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.OBJECTION_OVERRULED,
            {"unlure": True, "invoker": self.getAv()},
            {"respectPreviousAdditions": True}
        )


class FindTheFamilyBossbotEffect(FindTheFamilyBaseEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions += [SEE.DEFINITION_OC_FAMILY_C]


class FindTheFamilyNuclear(FindTheFamilyBaseEffect):
    VisualSortOrder = 490

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions = []

    def handleNuclearTransformation(self):
        # This will happen as the very last attack of the round.
        # The client will now insert a movie showing some of this goofy stuff happening
        self.createGeneralAttack(AttackEnum.FTF_NUCLEAR_TRANSFORMATION,
                                 targetList=[self.av], insertKwargs={'mode': 'end', 'priority': 100000})

        # If we haven't added one yet, add an attack to adjust the suits position after the attack is done
        if not self.battleCalc.attackOrder.hasAttackOfType(AttackEnum.SUITS_ADJUST_POSITION):
            self.createGeneralAttack(AttackEnum.SUITS_ADJUST_POSITION, insertKwargs={'mode': 'end', 'priority': 100100})

    def handleMovieDone(self):
        # Now we can go ahead and finalize all of our changes.
        # This will send it all over to the client. Yay!
        self.av.b_setSpecialContainerId(self.av.specialContainerId)

    def isVisible(self):
        # Don't need to show this for dual core cogs
        return not self.av.hasStatusEffectOfId(SEE.EFFECT_FTF_DUALCORE)


class FindTheFamilyFinalDamageBoost(MultiplicativeDamageBoostStatusEffect):
    VisualSortOrder = 495


class FindTheFamilySuitFinalDamageBoost(FindTheFamilyFinalDamageBoost):
    def handleAttackDamage(self, attackTrack: int, attackDamage, target):
        attackDamage = super().handleAttackDamage(attackTrack, attackDamage, target)
        if target and target.isToon():
            attackDamage = attackDamage * lerp(0.95, 1.05, random.random())

        return attackDamage


class FindTheFamilySupervisorLifeInsurance(SupervisorInsuredStatusEffect):
    HealAttackType = AttackEnum.FTF_SUPERVISOR_LIFE_INSURANCE


class FindTheFamilyContractorForeman(FindTheFamilySellbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chosenToonId = None

    def handleNormalAttacksOver(self):
        if self.chosenToonId:
            return
        aliveToons = self.battleCalc.getAliveToons()
        if not len(aliveToons):
            return
        toonsWithoutEffect = [toon for toon in aliveToons if not toon.hasStatusEffectOfId(SEE.EFFECT_FTF_FOREMAN_CONTRACTOR_TANGO)]
        if not len(toonsWithoutEffect):
            return

        # See what "effect indices" we have remaining here
        toonsWithEffect = [toon for toon in aliveToons if toon not in toonsWithoutEffect]
        validEffectIndices = list(range(8))
        for toon in toonsWithEffect:
            tangoEffect = toon.getStatusEffectOfId(SEE.EFFECT_FTF_FOREMAN_CONTRACTOR_TANGO)
            if tangoEffect.effectIndex in validEffectIndices:
                validEffectIndices.remove(tangoEffect.effectIndex)

        chosenToon = random.choice(toonsWithoutEffect)
        self.chosenToonId = chosenToon.doId
        validIndex = random.choice(validEffectIndices)
        chosenToon.addStatusEffect(
            SEE.EFFECT_FTF_FOREMAN_CONTRACTOR_TANGO,
            extraArgs=[validIndex, self.chosenToonId, self.av.doId])
        self.av.addStatusEffect(
            SEE.EFFECT_FTF_FOREMAN_CONTRACTOR_TANGO,
            extraArgs=[validIndex, self.chosenToonId, self.av.doId])
        # Call out for help that u need a strong toon to help u fill out paperwork
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
            {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_FOREMAN_CONTRACTOR_BEGIN, 1], "targets": [self.av]},
            {"priority": 1000}
        )
        # Toon response to callout
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
            {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_FOREMAN_CONTRACTOR_TOON, 1], "targets": [chosenToon]},
            {"priority": 1001}
        )


class FindTheFamilyContractorDancePartnerStatusEffect(DancePartnerStatusEffect):
    """
    Like major player's dance partners except butchered a bit
    """

    VisualSortOrder = 485

    match_toon_damageMultiplier = 1.50  # How much more damage a Toon will deal when the effects match.
    match_suit_damageMultiplier = 1.50  # How much more damage a Suit will deal when the effects match.
    wrong_toon_damageMultiplier = 0.50  # How much less damage a Toon will deal when the effects don't match.
    wrong_suit_damageMultiplier = 0.50  # How much less damage a Suit will deal when the effects don't match.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions.append(SEE.EFFECT_DANCE_PARTNER)


class FindTheFamilyRedTapeForeman(FindTheFamilySellbotEffect):
    pass


class FindTheFamilySniperForeman(FindTheFamilySellbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resetHits()

    def resetHits(self) -> None:
        self.toonsThatNeedSniped = []
        self.toonsSnipeDamage = []

    def applySnipe(self, toon, damage, attackType) -> None:
        # Don't include toons that are already marked for sniping.
        if toon in self.toonsThatNeedSniped:
            return
        # Only add toons with a reward cooldown
        if not toon.hasStatusEffectOfId(SEE.EFFECT_REWARD_COOLDOWN):
            return
        # Ignore damage that comes from other Snipes
        if attackType == AttackEnum.FTF_FOREMAN_SNIPE:
            return

        self.toonsThatNeedSniped.append(toon)
        self.toonsSnipeDamage.append(damage)

    def addSnipeAttack(self):
        if len(self.toonsThatNeedSniped) > 0:
            self.createAttack(AttackEnum.FTF_FOREMAN_SNIPE, insertMethod='index', unlure=True,
                              targets=self.toonsThatNeedSniped, extraArgs=self.toonsSnipeDamage)
        self.toonsThatNeedSniped = []
        self.toonsSnipeDamage = []


class FindTheFamilySleepyForeman(FindTheFamilySellbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.isAi():
            self.av.addStatusEffect(SEE.EFFECT_FTF_FOREMAN_SLEEPY_POWER_NAP)


class FindTheFamilySleepForemanPowerNap(PowerNapStatusEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions.append(SEE.EFFECT_POWER_NAP)


class FindTheFamilyExplosiveForeman(FindTheFamilySellbotEffect):
    def roundsRanOut(self):
        # He is going bye bye
        self.createAttack(AttackEnum.OVERCLOCKED_FOREMAN_DESTRUCTION, unlure=True, priority=-500)
        super().roundsRanOut()


class FindTheFamilyBurningForeman(FindTheFamilySellbotEffect):
    pass


class FindTheFamilyBurningForemanDamageOverTime(ToonPercentDamageOverTimeStatusEffect):
    def combine(self, otherEffect):
        otherRounds = otherEffect.getRounds()
        if otherRounds > self.getRounds():
            self.setRounds(otherRounds, adjust=False)

    def applyDamage(self):
        maxHp, hp = self.getAv().getMaxHp(), self.getAv().getHp()
        # Floor the damage to be consistent with all other suit damage calcs, but also
        # don't do absolutely zero damage either. (this can happen with 1 laff ubers)
        damage = max(math.floor(maxHp * self.amount), 1)
        self.createGeneralAttack(
            attackType=self.DamageAttackType,
            extraArgs=[-damage],
            targetList=[self.getAv()]
        )


class FindTheFamilySpongySupervisor(DamageAbsorbStatusEffect, FindTheFamilyCashbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions = [SEE.EFFECT_BASE, SEE.DEFINITION_DAMAGE_ABSORB, SEE.DEFINITION_OC_FAMILY_M]

    def incrementSuitDamageDealt(self, amount, suit, track):
        # Increase the amount of damage that he *takes*
        super().incrementSuitDamageDealt(amount * (0.5 / (1 - self.absorbMultiplier)), suit=suit, track=track)


class FindTheFamilyFraudSupervisor(FindTheFamilyCashbotEffect):
    def suitDealtDamage(self, suit, damage):
        # Ignore damage that didn't come from us
        if suit is not self.av:
            return

        # Take the damage we just dealt, but times 3 back at ourselves.
        self.createGeneralAttack(AttackEnum.SUIT_DAMAGE, extraArgs=[damage * 3], targetList=[self.getAv()])


class FindTheFamilyAbacusSupervisor(FindTheFamilyCashbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.levelChoice = self.extraArgs[0]
        self.isAbove = self.extraArgs[1]
        self.fields = ['levelChoice', 'isAbove']
        self.levelsUsedThisTurn = 0
        if self.isAi():
            self.chooseNewLevels()

    def handleNormalAttacksOver(self):
        self.checkGagsUsed()
        self.chooseNewLevels()

    def chooseNewLevels(self):
        self.levelChoice = random.randint(10, 20)
        self.isAbove = random.choice([0, 1])
        self.levelsUsedThisTurn = 0

    def handleGagLanded(self, suit, attackLevel):
        if suit is not self.av:
            return

        if attackLevel == -1:
            return

        self.levelsUsedThisTurn += attackLevel + 1

    def checkGagsUsed(self):
        if self.isAbove:
            metConditions = self.levelsUsedThisTurn >= self.levelChoice
        else:
            metConditions = self.levelsUsedThisTurn <= self.levelChoice

        if not metConditions:
            # Call out that they DID Bad
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
                {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_SUPERVISOR_ABACUS_BAD_CONDITIONS, 1], "targets": [self.av]},
            )
            # Now kill them with big attack
            self.createAttack(AttackEnum.FTF_SUPERVISOR_ABACUS_SYNERGY, insertMethod='index', unlure=True)
        else:
            # Call out that they did good!!
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
                {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_SUPERVISOR_ABACUS_GOOD_CONDITIONS, 1], "targets": [self.av]},
            )


class FindTheFamilyConfusedSupervisor(FindTheFamilyCashbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions += [SEE.DEFINITION_OC_FAMILY_L]
        if self.isAi():
            # Create the environmental that tracks randomized gag order if we haven't yet
            # We only need one for the entire battle
            if not getattr(self.battle, 'ftf_createdRandomGagOrderTracker', False):
                setattr(self.battle, 'ftf_createdRandomGagOrderTracker', True)
                self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.FTF_SUPERVISOR_CONFUSED_GAG_ORDER])

    def doCheats(self):
        self.createAttack(AttackEnum.CONTENT_SYNC, unlure=True, priority=1050)


class FindTheFamilyControllingSupervisor(FindTheFamilyBaseEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.isAi():
            self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.FTF_SUPERVISOR_CONTROLLING])

    def delete(self):
        if self.cleanedUp:
            return
        if self.isAi():
            # Send an event to destroy the overseer environmental we created earlier
            self.getBattleCalc().sendEvent(BEG.EVENT_DESTROY_ENVIRONMENTAL, [ENV_ENUM.FTF_SUPERVISOR_CONTROLLING])
        super().delete()


class FindTheFamilyAccountantSupervisor(FindTheFamilyCashbotEffect):
    TargetChoices = [1, 2, 3, 4]
    TargetWeights = [30, 30, 30, 10]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.targetChoice = self.extraArgs[0]
        self.fields = ['targetChoice']
        self.targetsHit = []
        if self.isAi():
            self.chooseNewTargets()

    def handleNormalAttacksOver(self):
        self.checkGagsUsed()
        self.chooseNewTargets()

    def chooseNewTargets(self):
        self.targetsHit = []
        aliveCogs = len(self.battleCalc.getAliveCogs())
        if aliveCogs == 1:
            self.targetChoice = 1
        else:
            targetChoices = self.TargetChoices[:3 - max(0, (4 - aliveCogs))]
            targetWeights = self.TargetWeights[:3 - max(0, (4 - aliveCogs))]
            self.targetChoice = random.choices(targetChoices, weights=targetWeights)[0]

    def handleGagLanded(self, suit):
        if suit.doId not in self.targetsHit:
            self.targetsHit.append(suit.doId)

    def checkGagsUsed(self):
        metConditions = len(self.targetsHit) == self.targetChoice

        if not metConditions:
            # Call out that they DID Bad
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
                {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_SUPERVISOR_ABACUS_BAD_CONDITIONS, 1], "targets": [self.av]},
            )
            # Now kill them with big attack
            self.createAttack(AttackEnum.FTF_SUPERVISOR_ABACUS_SYNERGY, insertMethod='index', unlure=True)
        else:
            # Call out that they did good!!
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
                {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_SUPERVISOR_ABACUS_GOOD_CONDITIONS, 1], "targets": [self.av]},
            )


class FindTheFamilySneakyAttorney(FindTheFamilyLawbotEffect):
    def doCheats(self):
        self.createAttack(AttackEnum.CASTLING, unlure=True, insertMethod='beginning')


# This inherits from the base effect instead of the lawbot effect so that objection doesn't happen
class FindTheFamilyOverseerAttorney(FindTheFamilyBaseEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.isAi():
            self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.FTF_ATTORNEY_OVERSEER])

    def delete(self):
        if self.cleanedUp:
            return
        if self.isAi():
            # Send an event to destroy the overseer environmental we created earlier
            self.getBattleCalc().sendEvent(BEG.EVENT_DESTROY_ENVIRONMENTAL, [ENV_ENUM.FTF_ATTORNEY_OVERSEER])
        super().delete()


class FindTheFamilyChronoAttorney(FindTheFamilyLawbotEffect):
    def getTimescale(self):
        return self.battle.timescale

    def setTimescale(self, timescale):
        battle = self.getBattle()
        battle.timescale = timescale

    def doCheats(self):
        currSpeed = self.getTimescale()
        # No pacing if we're at max speed.
        if currSpeed >= 8.0:
            return

        # Figure out how much to increase the speed by.
        newSpeed = min(8.0, currSpeed + 0.5)
        self.setTimescale(newSpeed)

        # Force unlure them first because it was goofy with the movie
        if self.av.hasStatusEffectOfId(SEE.EFFECT_SUIT_LURED):
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.SUIT_UNLURE,
                {"targets": [self.getAv()]},
            )

        # At this point, call for a speedup.
        self.createAttack(AttackEnum.FTF_ATTORNEY_PICK_UP_THE_PACE, extraArgs=[self.getTimescale(), currSpeed], unlure=True)
        # He is a joggy boy
        if not self.av.getVisualEffectOfId(VisualEffectEnum.FTF_ATTORNEY_JOGGING):
            self.av.addVisualEffect(VisualEffectEnum.FTF_ATTORNEY_JOGGING)


class FindTheFamilyRushJobAttorney(FindTheFamilyLawbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.isAi():
            # Create the environmental that tracks rush job damage if we haven't yet
            # We only need one for the entire battle
            if not getattr(self.battle, 'ftf_createdRushJobTracker', False):
                setattr(self.battle, 'ftf_createdRushJobTracker', True)
                self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.FTF_GENERAL_RUSHJOB_TRACKER])

    def doCheats(self):
        # Force unlure them first because it was goofy with the movie
        if self.av.hasStatusEffectOfId(SEE.EFFECT_SUIT_LURED):
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.SUIT_UNLURE,
                {"targets": [self.getAv()]},
            )

        # Just create a rush job attack
        self.createAttack(AttackEnum.RUSH_JOB, extraArgs=[True], unlure=True)
        # self.createAttack(AttackEnum.RUSH_JOB, extraArgs=[True], unlure=True)


class FindTheFamilyMonolithAttorney(FindTheFamilyLawbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lastTracks = []

    def doCheats(self):
        allTracks = list(range(0, AttackEnum.TOON_DROP + 1))
        for lastTrack in self.lastTracks:
            allTracks.remove(lastTrack)

        random.shuffle(allTracks)
        choiceOne = allTracks.pop()
        random.shuffle(allTracks)
        choiceTwo = allTracks.pop()

        self.createAttack(AttackEnum.FTF_ATTORNEY_COURT_MANDATE_MONOLITH, unlure=True, priority=980, extraArgs=[choiceOne, choiceTwo])
        for toon in self.battleCalc.getAliveToons():
            newDisabledEffect = SEG.createStatusEffect(toon, SEE.EFFECT_DISABLE_GAG_TRACKS)
            newDisabledEffect.setRounds(1, adjust=True)
            newDisabledEffect.setGagTrackDisabled(choiceOne, 1)
            newDisabledEffect.setGagTrackDisabled(choiceTwo, 1)
            toon.addStatusEffect(SEE.EFFECT_DISABLE_GAG_TRACKS, newDisabledEffect)


class FindTheFamilyOmnipotentAttorney(FindTheFamilyLawbotEffect):
    def doCheats(self):
        allLevels = [4, 5, 6, 7]  # Actually 5-8
        random.shuffle(allLevels)
        choiceOne = allLevels.pop()
        random.shuffle(allLevels)
        choiceTwo = allLevels.pop()

        self.createAttack(AttackEnum.FTF_ATTORNEY_COURT_MANDATE_OMNIPOTENT, unlure=True, priority=985, extraArgs=[choiceOne, choiceTwo])
        for toon in self.battleCalc.getAliveToons():
            newDisabledEffect = SEG.createStatusEffect(toon, SEE.EFFECT_DISABLE_GAG_LEVELS)
            newDisabledEffect.setRounds(1, adjust=True)
            newDisabledEffect.setGagLevelDisabled(choiceOne, 1)
            newDisabledEffect.setGagLevelDisabled(choiceTwo, 1)
            toon.addStatusEffect(SEE.EFFECT_DISABLE_GAG_LEVELS, newDisabledEffect)


class FindTheFamilyMulliganClubPresident(FindTheFamilyBossbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extraAttacks = 1

    def doCheats(self):
        for _ in range(self.extraAttacks):
            self.createAttack(AttackEnum.FTF_PRESIDENT_MULLIGAN, unlure=True, priority=500)

        self.extraAttacks += 1


class FindTheFamilyChipFanClubPresident(FindTheFamilyBossbotEffect):
    TimesHitPosTextType = {
        1: TTLocalizer.HP_TEXT_CHIPFAN_RPM_1,
        2: TTLocalizer.HP_TEXT_CHIPFAN_RPM_2,
        3: TTLocalizer.HP_TEXT_CHIPFAN_RPM_3,
        4: TTLocalizer.HP_TEXT_CHIPFAN_RPM_4,
    }
    TimesHitNegTextType = {
        1: TTLocalizer.HP_TEXT_CHIPFAN_RPM_1_N,
        2: TTLocalizer.HP_TEXT_CHIPFAN_RPM_2_N,
        3: TTLocalizer.HP_TEXT_CHIPFAN_RPM_3_N,
        4: TTLocalizer.HP_TEXT_CHIPFAN_RPM_4_N,
    }

    IncreasePerHit = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resetHits()
        self.needHeal = False

    def resetHits(self):
        self.timesHit = 0
        self.shownRpmGainTimes = 0

    def doCheats(self):
        if self.timesHit > 0:
            self.createGeneralAttack(
                AttackEnum.SHOW_HP_TEXT, insertKwargs={"mode": "insert", "priority": -100},
                extraArgs=[self.TimesHitNegTextType[self.timesHit]]
            )

        if self.timesHit == 1:
            # 1,000 RPM: Uses litigator's snap
            self.createAttack(
                AttackEnum.FTF_PRESIDENT_SNAP, insertMethod='index', priority=-100, unlure=True,
                extraArgs=[dict(), 1.25, False],
            )
        elif self.timesHit == 2:
            # 2,000 RPM: His next attack heals him for 10x the damage he deals
            self.needHeal = True
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
                {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_PRESIDENT_INCOMING_HEAL, 1], "targets": [self.av]},
                {"mode": "insert", "priority": -100}
            )
        elif self.timesHit == 3:
            # 3,000 RPM: Uses bayou bellow
            # Send a bash in advance, so that when we do BayouBash, it'll automatically be BayouBellow.
            self.getBattleCalc().sendEvent(BEG.EVENT_LT_LGATOR_BAYOU_BASH)
            # Add a bellow to the round order.
            self.createAttack(AttackEnum.BAYOU_BASH, unlure=True, insertMethod='index', priority=-100)
        elif self.timesHit >= 4:
            # 4,000 RPM: Unlures himself, and then does a nasty snipe
            toonPool = [toon for toon in self.activeToons if toon.getHp() > 0]
            toonTargets = random.sample(toonPool, min(len(toonPool), 2))
            self.createAttack(AttackEnum.FTF_PRESIDENT_SNIPE, insertMethod='index', targets=toonTargets,
                              extraArgs=[-50] * len(toonTargets), unlure=True, priority=-100)

        self.resetHits()

    def handleGagLanded(self, suit, attackType: AttackEnum) -> None:
        if attackType == AttackEnum.TOON_LURE:
            return
        if suit is not self.getAv():
            return

        self.timesHit = min(4, self.timesHit + self.IncreasePerHit)

    def handleTrackOver(self):
        if self.shownRpmGainTimes < self.timesHit:
            self.createGeneralAttack(
                AttackEnum.SHOW_HP_TEXT, insertKwargs={"mode": "insert"},
                extraArgs=[self.TimesHitPosTextType[self.timesHit - self.shownRpmGainTimes]]
            )

        self.shownRpmGainTimes = self.timesHit

    def suitDealtDamage(self, damageAmount):
        if self.needHeal:
            self.createGeneralAttack(AttackEnum.SUIT_HEAL,
                extraArgs=[damageAmount * -10, True, 10.0],
                targetList=[self.getAv()]
            )

        self.needHeal = False


class FindTheFamilyAncientClubPresident(FindTheFamilyBossbotEffect):
    pass


class FindTheFamilyPuzzlingClubPresident(FindTheFamilyBossbotEffect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.isAi():
            if self.battleCalc.rounds == 0:
                # Pick a random Toon to add the confused effect on immediately.
                toonChoice = random.choice([self.battle.getToon(toon) for toon in self.battle.toons])
                toonChoice.addStatusEffect(SEE.EFFECT_FTF_PRESIDENT_PUZZLING_CONFUSED)

    def confuseToon(self):
        # Choose a random toon to mess with their attack order
        aliveToons = self.battleCalc.getAliveToons()
        if not len(aliveToons):
            return
        aliveToonsWithoutEffect = [toon for toon in aliveToons if not toon.hasStatusEffectOfId(SEE.EFFECT_FTF_PRESIDENT_PUZZLING_CONFUSED)]
        # Just re-add the effect to a Toon that already has it if we don't have any toons that dont
        toonChoicePool = aliveToonsWithoutEffect if len(aliveToonsWithoutEffect) else aliveToons

        toonChoice = random.choice(toonChoicePool)
        confusedEffect = SEG.createStatusEffect(toonChoice, SEE.EFFECT_FTF_PRESIDENT_PUZZLING_CONFUSED)
        confusedEffect.setRounds(1)
        toonChoice.addStatusEffect(SEE.EFFECT_FTF_PRESIDENT_PUZZLING_CONFUSED, newStatusEffect=confusedEffect)

        # Insert a call and response from the president to the toon
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
            {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_PRESIDENT_PUZZLING_MIND_MEDDLE, 1], "targets": [self.av]},
            {"priority": 1010}
        )
        # Add the confusion visual effect to the toon
        self.createGeneralAttack(
            AttackEnum.APPLY_VISUAL_EFFECT_MOVIE,
            extraArgs=[VisualEffectEnum.CONFUSION.value],
            targetList=[toonChoice],
            insertKwargs=dict(priority=1011),
        )
        # Toon response to callout
        self.getBattleCalc().createAndInsertAttack(
            AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
            {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_PRESIDENT_PUZZLING_TOON_RESPONSE, 1], "targets": [toonChoice]},
            {"priority": 1012}
        )


class FindTheFamilyPuzzlingClubPresidentConfused(MixedGagTracksLevelsDisabled):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inheritedEventDefinitions += [SEE.EFFECT_BASE]

    def isVisible(self):
        return True

    def getGagTrackLevelDisabled(self, track, level):
        if track == AttackEnum.TOON_SOUND:
            return 1
        elif track in (AttackEnum.TOON_LURE, AttackEnum.TOON_HEAL) and level in (1, 3, 5, 7):
            return 1
        return 0

    def handleRandomization(self, attackOrder):
        toonAttacks = self.battleCalc.attackOrder.getAttacksOfInvoker(self.av)
        if not len(toonAttacks):
            return

        attack = toonAttacks[0]

        if attack.isGroup:
            return

        aliveToons = self.battleCalc.getAliveToons()

        oldTarget = attack.target
        if attack.attackType in (AttackEnum.TOON_HEAL, AttackEnum.TOON_NPC):
            oldTargetObj = self.battle.getToon(oldTarget)
            bannedToonList = [self.av, oldTargetObj]
            newToonList = [toon for toon in aliveToons if toon not in bannedToonList]
            if len(newToonList) <= 0:
                return

            newTarget = random.choice(newToonList)
        else:
            aliveSuits = [suit for suit in self.battle.activeSuits if suit.getHp() > 0]
            if attack.attackType == AttackEnum.TOON_TRAP:
                # Narrow down suit choices to ones that don't have the trapped effect
                aliveSuits = [suit for suit in aliveSuits if not suit.hasStatusEffectOfId(SEE.EFFECT_SUIT_TRAPPED)]
            elif attack.attackType == AttackEnum.TOON_LURE:
                # Narrow down suit choices to ones that don't have the lured effect
                aliveSuits = [suit for suit in aliveSuits if not suit.hasStatusEffectOfId(SEE.EFFECT_SUIT_LURED)]
            if len(aliveSuits) <= 1:
                return
            if attack.target == -1:
                return

            oldTargetObj = self.battle.getSuit(oldTarget)
            newTarget = random.choice([suit for suit in aliveSuits if suit is not oldTargetObj])

        # Change our target.
        attack.target = newTarget.doId
        # Then, if our target list has already been set, clear it and set it again.
        if attack.targets:
            attack.targets = []
            attack.setTargetList()


class FindTheFamilyShiveringClubPresident(FindTheFamilyBossbotEffect):
    def __init__(self, *args, **kwargs):
        FindTheFamilyBossbotEffect.__init__(self, *args, **kwargs)
        self.resetHits()
        if self.isAi():
            # Shatter functionality is handled by the shivering president's environmental
            self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.FTF_PRESIDENT_SHIVERING])

    def delete(self):
        if self.cleanedUp:
            return
        if self.isAi():
            # Send an event to destroy the shivering environmental we created earlier
            self.getBattleCalc().sendEvent(BEG.EVENT_DESTROY_ENVIRONMENTAL, [ENV_ENUM.FTF_PRESIDENT_SHIVERING])
        super().delete()

    def resetHits(self):
        self.timesHit = 0

    def doCheats(self):
        if self.timesHit >= 3:
            # If hit 3 or more times this turn, use deep freeze!!!
            # First, we need to announce what we're doing
            self.getBattleCalc().createAndInsertAttack(
                AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET,
                {"extraArgs": [TTLocalizer.SAY_PHRASE_FTF_PRESIDENT_SHIVERING_DEEP_FREEZE, 1], "targets": [self.av]},
                {"priority": 600}
            )
            self.createAttack(AttackEnum.DEEP_FREEZE, extraArgs=[2], unlure=True, priority=601)

        self.resetHits()

    def handleGagLanded(self, suit, attackType: AttackEnum) -> None:
        if attackType == AttackEnum.TOON_LURE:
            return
        if suit is not self.getAv():
            return

        self.timesHit = min(4, self.timesHit + 1)

    def freezeSuit(self, effect) -> None:
        """When a Suit is applied with either the soaked or drenched effect, remove it
        and replace it with frozen."""
        # Get the rounds which the soak/drench would have lasted for.
        rounds = effect.getRounds()

        # Remove soak/drench.
        effect.delete()

        # Apply frozen
        newEffect = SEG.createStatusEffect(self.av, SEE.EFFECT_SUIT_FROZEN)
        # No adjust so that it does not include the +1 rounds used on the server.
        newEffect.setRounds(rounds, adjust=False)
        self.av.addStatusEffect(SEE.EFFECT_SUIT_FROZEN, newEffect)


class FindTheFamilyHighStakesClubPresident(FindTheFamilyBossbotEffect):
    def __init__(self, *args, **kwargs):
        FindTheFamilyBossbotEffect.__init__(self, *args, **kwargs)
        if self.isAi():
            # Gives random -35% to +35% effectiveness environmental
            self.avProfile.sendEvent(BEG.EVENT_CREATE_ENVIRONMENTAL, [ENV_ENUM.FTF_PRESIDENT_HIGHSTAKES])

    def delete(self):
        if self.cleanedUp:
            return
        if self.isAi():
            # Send an event to destroy the high stakes environmental we created earlier
            self.getBattleCalc().sendEvent(BEG.EVENT_DESTROY_ENVIRONMENTAL, [ENV_ENUM.FTF_PRESIDENT_HIGHSTAKES])
        super().delete()

from . import StatusEffectGlobals as SEG