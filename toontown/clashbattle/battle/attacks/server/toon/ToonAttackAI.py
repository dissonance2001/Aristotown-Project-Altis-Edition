import math
import random
from typing import List

from otp.ai.AIBaseGlobal import simbase
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.BattleGlobals import ATTACK_TRACKS, NUM_GAG_TRACKS, AccuracyBonusIncrement, \
    AvPropAccuracy, ExperienceCap, MaxToonAcc, MaxToonTrackAcc, InherentTrackExpMult, attackAffectsGroup, \
    getAvPropDamage, MaxToonAccBrokeCap
from toontown.clashbattle.battle.attacks.server.AttackAI import AttackAI
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.statuses.StatusEffectEnums import StatusEffectEnum, SEE
from toontown.hood import ZoneUtil
from toontown.clashsuit.suit.DistributedSuitBaseAI import DistributedSuitBaseAI
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.toon.ToonStatsGlobals import ToonStats
from toontown.inventory.enums.ItemEnums import BoosterItemType


class ToonAttackAI(AttackAI):
    """
    ToonAttackAI: Extends AttackAI with toon specific
    functionality.

    :param level: The level of the toon attack.
    :param target: The target of the toon attack.
    :param propBonus: The prop bonus of the current battle.
    :param expGained: Dictionary of skill points for the
    current battle.
    :param creditMult: Gag exp credit multiplier for the
    current battle.
    :param creditLevel: Max level of the suits which
    were alive at the start of the current round.
    :param levelBonus: The maximum level of every gag
    used of the current gag track.
    :param targetHitsTrack: A dictionary of each active
    participant with the amount of times they were hit
    by the current toon track.
    :param targetAttacks: A dictionary containing each avatar
    mapped to a list of attacks which will target it. This
    parameter is useful for calculating certain prestige effects.
    """
    WANT_TAUNT = False

    def __init__(self, attackType: AttackEnum, rounds: int = 0,
                 invoker: BattleAvatar = None, targets: list = None,
                 extraArgs: list = None, level: int = -1, target: int = -1,
                 propBonus: int = -1, expGained: dict = None, creditMult: int = 1,
                 creditLevel: int = 0, levelBonus: int = 0,
                 targetHitsTrack: dict = None, targetAttacks: dict = None) -> None:
        super().__init__(
            attackType, rounds=rounds, invoker=invoker,
            targets=targets, extraArgs=extraArgs
        )
        self.originalLevel = level
        self.level = level
        self.target = target
        self.hasPropBonus = self.attackType == propBonus
        self.trackIndex = self.attackType in ATTACK_TRACKS

        # Does this toon have track bonus?
        if self.trackIndex:
            self.hasTrackBonus = invoker.checkGagBonus(self.attackType, self.level) or self.hasPropBonus
        else:
            self.hasTrackBonus = False

        # Relevant values passed shared with the battle.
        self.expGained = expGained if isinstance(expGained, dict) else {}
        self.creditMult = creditMult
        self.creditLevel = creditLevel
        self.levelBonus = levelBonus
        self.targetHitsTrack = targetHitsTrack if isinstance(targetHitsTrack, dict) else {}
        self.targetAttacks = targetAttacks if isinstance(targetAttacks, dict) else {}

        # Should gag credit be overridden for this attack?
        # Default to False.
        self.creditOverride = False

    def cleanup(self) -> None:
        del self.targetHitsTrack
        del self.targetAttacks
        del self.expGained

        super().cleanup()

    def calculate(self) -> None:
        # Send an event that our toon used a gag.
        if self.attackType not in (AttackEnum.TOON_SUE, AttackEnum.TOON_FIRE):
            self.sendEvent(BEG.EVENT_TOON_USED_GAG, [self])

        # Attempt to add gag experience.
        if self.attackType not in (
            AttackEnum.TOON_SUE, AttackEnum.TOON_FIRE, AttackEnum.TOON_TRAP
        ) and self.landed:
            self.addAttackExp(self.attackType, self.level, override=self.creditOverride)

    def setTargetList(self) -> None:
        """Determine the target list for the attack to use.
        """
        if self.targets:
            return

        if not self.isGroup:
            # Handle single target attacks.
            target = [suit for suit in self.suits if suit.doId == self.target]
            if target:
                self.targets.append(target[0])
        else:
            self.targets = self.suits.copy()

    def attemptTargetingOverride(self, targetOverrideDict):
        # Check to see if our target should change
        if self.target in targetOverrideDict:
            # Change our target.
            self.target = targetOverrideDict[self.target]
            # Then, if our target list has already been set, clear it and set it again.
            if self.targets:
                self.targets = []
                self.setTargetList()

    def getDamage(self, target: BattleAvatar = None) -> int:
        """
        Returns the amount of damage that the attack should deal.
        """
        if self.trackIndex:
            return getAvPropDamage(
                self.attackType, self.level,
                self.invoker.getExperience()[self.attackType],
                self.hasTrackBonus
            )
        raise Exception(f"Called ToonAttackAI.getDamage() on an unsupported track: {repr(self.attackType)}")

    def getLanded(self) -> bool:
        """Calculates and returns if a Toon attack will hit.
        """
        # Check override
        if getattr(self.invoker, 'setaccuracy', None) is not None:
            return random.randint(1, 100) <= getattr(self.invoker, 'setaccuracy')

        # Toonup gags should always hit.
        if self.attackType == AttackEnum.TOON_HEAL:
            return True

        # Drop should never hit if all targets are lured.
        if self.attackType == AttackEnum.TOON_DROP:
            if all(target.getStatusEffectOfType(StatusEffects.LureStatusEffect) for target in self.targets):
                return False

        # Regular calculation
        randomAcc = 100 * random.random()
        rawAcc, accOverride = self.getRawAccuracyOrOverride()
        if accOverride != -1:
            return randomAcc <= accOverride

        # Find and use the highest suit defense.
        maxTargetDef, shouldHitOverride = self.getMaxDefenseOrOverride()
        if shouldHitOverride:
            return True

        # If a previous attack of this track
        # has been used on one of the targets, return that result.
        if self.attackType != AttackEnum.TOON_DROP:
            for tgt, results in self.targetHitsTrack.items():
                if tgt in [t.doId for t in self.targets] and results:
                    return results[0]

        # Based on the previous attacks, determine the accuracy bonus.
        finalAcc = self.getFinalAccuracy(rawAcc, maxTargetDef)

        # Iterate through the target list to find a lured suit.
        if self.attackType not in (AttackEnum.TOON_DROP, AttackEnum.TOON_LURE):
            accBonus = self.maxTargetHits * AccuracyBonusIncrement
            lureResult, useLureResult = self.handleLureAccuracy(finalAcc, accBonus, randomAcc)
            if useLureResult:
                return lureResult

        return randomAcc <= finalAcc

    def getRawAccuracyOrOverride(self):
        baseAcc = AvPropAccuracy[self.attackType][self.level]
        rawAcc = baseAcc + self.levelBonus

        # If we have any attack accuracy status effects, then change the toon's accuracy here.
        accuracyStatusEffects = self.invoker.getStatusEffectsOfType(StatusEffects.AttackAccuracyStatusEffect)
        for statusEffect in accuracyStatusEffects:
            # If override, force to true.
            rawAcc, override = statusEffect.handleAttackAccuracy(self.attackType, rawAcc)
            if override != -1:
                return rawAcc, override

        return rawAcc, -1

    def getMaxDefenseOrOverride(self):
        maxTargetDef = 0
        for suit in self.targets:
            # Get this suit's defense and profile.
            suitDef = suit.getDefense()

            # If this suit is lured, and we're using lure, ignore this suit.
            if self.attackType == AttackEnum.TOON_LURE and \
                suit.getStatusEffectsOfType(StatusEffects.LureStatusEffect):
                continue

            # Apply defense modifier status effects.
            defenseEffects = suit.getStatusEffectsOfType(StatusEffects.SuitDefenseModifierStatusEffect)
            for effect in defenseEffects:
                suitDef = effect.handleSuitDefense(suit, suitDef, self)

            maxTargetDef = max(suitDef, maxTargetDef)

            # Wait, maybe we can just hit?
            cantDodgeEffects = suit.getStatusEffectsOfType(StatusEffects.SuitCannotDodgeStatusEffect)
            for effect in cantDodgeEffects:
                if effect.isDodgeDisabled(self):
                    return maxTargetDef, True

        return maxTargetDef, False

    def getFinalAccuracy(self, rawAcc, maxTargetDef):
        # Determine which target was hit the most amount of times
        # by taking the sum of the list of booleans indicating
        # whether the given attack had landed or not. t == 1, f == 0
        maxTargetHits = self.maxTargetHits

        # The accuracy bonus is the maximum target hits multiplied
        # by the accuracy bonus increment.
        accBonus = maxTargetHits * AccuracyBonusIncrement

        # Attack accuracy is the sum of the base accuracy
        # subtracted by the max target defense and the total accuracy bonus.
        finalAcc = (rawAcc - maxTargetDef) + accBonus

        # If accuracy has surpassed 95% (96% for drop), then we will divide it by tenfold.
        # The new accuracy cap becomes 99%, which can be reached at 135% accuracy.
        accCap = self.getAccuracyCap()
        if finalAcc > accCap:
            finalAcc = accCap + ((finalAcc - accCap) / 10)
            accCap = MaxToonAccBrokeCap

        # Ensure that the attack accuracy doesn't go above the cap.
        finalAcc = min(finalAcc, accCap)

        return finalAcc

    def handleLureAccuracy(self, attackAcc, accBonus, randomAcc):
        useResult = False
        for target in self.targets:
            lureEffect = target.getStatusEffectOfType(StatusEffects.LureStatusEffect)
            if lureEffect:
                useResult = True
                # Grab the result accuracy from the status effect class based on our data.
                result = lureEffect.handleAttackAccuracy(attackAcc, accBonus, randomAcc)
                if not result:  # Attack missed due to lure decay
                    self.showToonTipAll(65)
                return result, useResult
        return None, useResult

    def getAccuracyCap(self):
        for target in self.targets:
            accuracyBreakEffect = target.getStatusEffectOfType(StatusEffects.IncomingAttacksBreakAccuracyCap)
            if accuracyBreakEffect and accuracyBreakEffect.canBreakCap(self):
                return 100
        for accuracyBreakEffect in self.invoker.getStatusEffectsOfType(StatusEffects.OutgoingAttacksBreakAccuracyCap):
            if accuracyBreakEffect and accuracyBreakEffect.canBreakCap(self):
                return 100
        return MaxToonTrackAcc.get(self.attackType, MaxToonAcc)

    def getTrackExp(self, track: int) -> int:
        return self.invoker.getExperience().getExpLevel(track)

    def wasTargetHitWithPrestige(self, targetId: int) -> bool:
        if self.targetHitsTrack:
            return any(atk.hasTrackBonus for atk in self.targetHitsTrack.get(targetId, []))
        return False

    def getAttacksLandedOnTarget(self, targetId: int, considerPrestige: bool=False):
        """Generates a list of every attack which has landed on the targetId thus far.
        This list will be different for each attack in the chain, but this is okay, as only
        the final attack really matters in calculating values such as combo and knockback
        damage.
        """
        if self.targetAttacks:
            attacks = []

            for attack in self.targetAttacks.get(targetId, []):
                attack: ToonAttackAI
                # Filter out attacks of a different type.
                if attack.attackType != self.attackType:
                    continue

                # Filter out unprestiged attacks if desired.
                if considerPrestige and not attack.hasTrackBonus:
                    continue

                result = attack.findResult(targetId)
                if not result or not result.landed:
                    continue

                attacks.append(attack)

            return attacks

        return []

    def addAttackExp(self, track, level, toonId: int = None, override: bool = False) -> None:
        """
        Attempts to give experience to the indicated toon.
        It will fail to do so if it doesn't meet the conditions or if it is overriden.
        """
        if override or level >= self.creditLevel:
            return

        if toonId is not None:
            toon = simbase.air.doId2do.get(toonId)
            if not toon:
                return
        else:
            toon = self.invoker
            toonId = self.invoker.doId

        if not isinstance(toon, DistributedToonAI):
            return

        # Boost the gag experience multiplier by the toon's gag exp boosters.
        boosters = [BoosterItemType.Exp_Gags_Global]
        if track in (AttackEnum.TOON_SQUIRT, AttackEnum.TOON_SOUND,
                     AttackEnum.TOON_HEAL, AttackEnum.TOON_LURE):
            boosters.append(BoosterItemType.Exp_Gags_Support)
        elif track in (AttackEnum.TOON_TRAP, AttackEnum.TOON_ZAP,
                       AttackEnum.TOON_THROW, AttackEnum.TOON_DROP):
            boosters.append(BoosterItemType.Exp_Gags_Power)
        gagExpBoost = toon.applyBoosters(boosters, 0)

        # Apply any playground gag bonuses.
        zoneId = ZoneUtil.getHoodId(toon.zoneId)
        gagExpBoost += toon.getPlaygroundGagMultiplier(zoneId)

        self.expGained.setdefault(toonId, [0 for _ in range(NUM_GAG_TRACKS)])
        if not self.creditMult:
            return
        self.expGained[toonId][track] = int(min(ExperienceCap, self.expGained[toonId][track] + (level + 1)
                                                * (self.creditMult + gagExpBoost) * InherentTrackExpMult.get(track, 1)))

    def attemptUnlureSuit(self, suit: DistributedSuitBaseAI, instant: bool = False) -> bool:
        """
        Attempts to unlure suit and give credit to the invoker of the lure.
        """
        lureEffect = suit.getStatusEffectOfType(StatusEffects.LureStatusEffect)
        if not lureEffect:
            return False

        # only attempt to add EXP if lurers even exist
        for lurerId, lureAttack in list(lureEffect.invokers.items()):
            lureLvl = lureAttack.level
            self.addAttackExp(AttackEnum.TOON_LURE, lureLvl, lurerId)

            # Don't give credit to the lure invoker more than once.
            toon = simbase.air.getDo(lurerId)
            if not toon:
                continue
            self.sendEvent(BEG.EVENT_TOON_UNLURED_SUIT, [toon, lureEffect.getUniqueId(), suit])

        self.unlureSuit(suit, instant=instant)
        return True

    def giveMissEffect(self):
        """When a gag misses, we inflict a hidden miss 'forgiveness' status effect onto the invoker."""
        self.invoker.addStatusEffect(effectId=StatusEffectEnum.EFFECT_TOON_JUST_MISSED)

    def postprocess(self) -> tuple:
        # Take the item from their inventory if possible.
        if (
            self.attackType not in (AttackEnum.TOON_NO_ATTACK, AttackEnum.TOON_FIRE, AttackEnum.TOON_SUE)
            and not (self.attackType == AttackEnum.TOON_ZAP and not (self.extraArgs or [0])[-1])
            and self.attackIndex != -1
            and getattr(self.invoker, "inventory", None)
            and self.targets
        ):
            pipsqueak = self.invoker.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
            counterfeit = self.invoker.getStatusEffectOfId(SEE.EFFECT_COUNTERFEIT_CONTAINER)
            if pipsqueak:
                # Eat
                pass
            elif counterfeit and counterfeit.getGagTrackLevel(self.attackType, self.originalLevel):
                # Decrement our counterfeit for this gag
                counterfeit.setGagTrackLevel(self.attackType, self.originalLevel, 0)
            elif self.invoker.inventory.useItem(self.attackType, self.originalLevel) == -1:
                simbase.air.writeServerEvent(
                    'suspicious',
                    self.invoker.doId,
                    f'Toon generating movie for non-existent gag track {self.attackType} level {self.originalLevel}'
                )
                self.notify.warning(
                    f'generating movie for non-existent gag track {self.attackType} level {self.originalLevel}! '
                    f'avId: {self.invoker.doId}'
                )
            self.invoker.addStat(ToonStats.GAGS)
            self.invoker.d_setInventory(self.invoker.inventory.makeNetString())

        return super().postprocess()

    """
    Properties
    """

    @property
    def track(self) -> int:
        return self.attackType

    @property
    def isGroup(self) -> bool:
        return attackAffectsGroup(self.attackType, self.level)

    @property
    def landed(self) -> bool:
        return any(result.landed for result in self.results)

    @property
    def targetIds(self) -> List[int]:
        return [target.doId for target in self.targets]

    @property
    def maxTargetHits(self) -> int:
        """Using the current attack's target list, determines the most amount of
        hits a target has taken from any of the previously used gag tracks.
        """
        targetIds = self.targetIds

        if self.targetAttacks:
            maxTargetHits = {}
            trappedHitAvatar = []
            for k, v in self.targetAttacks.items():
                for atk in v:
                    atk: ToonAttackAI
                    # Don't use attacks of the same type.
                    if atk.attackType == self.attackType:
                        continue

                    # Our gag isn't targeting this target.
                    if k not in targetIds:
                        continue

                    # Placing Trap doesn't count as a stun.
                    if atk.attackType == AttackEnum.TOON_TRAP:
                        continue

                    maxTargetHits.setdefault(k, 0)
                    result = atk.findResult(k)

                    if not result or not result.landed:
                        continue

                    # Successfully Trapping a Cog counts as 2 stuns
                    if atk.attackType == AttackEnum.TOON_LURE and atk.trappedTarget:
                        # Only count the Trap-stun once
                        if k not in trappedHitAvatar:
                            maxTargetHits[k] += (2 * result.landed)
                            trappedHitAvatar.append(k)
                    else:
                        maxTargetHits[k] += result.landed

            if maxTargetHits:
                return max(maxTargetHits.values())

        return 0

    """
    Static methods
    """

    @staticmethod
    def roundDamageValue(damage: int) -> int:
        """Rounds the given damage value so that the Toon receives the
        most benefit from it.
        - If damage is negative, it's hurting the Cogs, so it rounds down.
        - If damage is positive, it's healing the Toons, so it rounds up.
        """
        return math.floor(damage) if damage < 0 else math.ceil(damage)
