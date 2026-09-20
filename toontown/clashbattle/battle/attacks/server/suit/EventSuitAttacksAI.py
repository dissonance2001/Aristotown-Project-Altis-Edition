import math, random
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.SuitBattleGlobals import calculateHp
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackAI import AttackAI
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.suit import SuitDoubleAttackAI
from toontown.clashbattle.battle.attacks.server.suit.MercSuitAttacksAI import ShatterDamageAI
from toontown.clashbattle.battle.attacks.server.suit.BasicAttacksAI import GenericDamageAttackAI, DamageInflictStatusAttackAI, \
    SuitHealAttackAI, SuitUnlureAttackAI, ApplyStatusEffectAttackAI, DoNothingAI, HitAllParticipantsAttackAI, \
    RemoveStatusEffectAttackAI
from toontown.clashbattle.battle.attacks.server.suit.SuitSingleAttackAI import SuitSingleAttackAI
from toontown.clashbattle.battle.attacks.server.suit.SuitGroupAttackAI import SuitGroupAttackAI
from toontown.clashbattle.battle.statuses import StatusEffects
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE
from toontown.clashbattle.battle.statuses.StatusEffects import FindTheFamilyBaseEffect
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.events.apriltoons.findthefamily import FindTheFamilyGlobals
from toontown.clashsuit.suit.DistributedSuitBaseAI import DistributedSuitBaseAI

# region Count Erfit / Erclaim

@AttackClassAI(attackType=AttackEnum.ERFIT_REVIVE)
class ErfitReviveAI(GenericDamageAttackAI):

    def setTargetList(self) -> None:
        self.targets = self.getOtherSuits()

    def getDamage(self, target: BattleAvatar = None) -> int:
        return round(self.extraArgs[0] * 8)


@AttackClassAI(attackType=AttackEnum.GAINS_FROM_THE_SCRAP)
class GainsFromTheScrapAI(GenericDamageAttackAI):
    """
    This is the attack object used for Gains From The Scrap.
    This is used by Count Erfit to delete other cogs.
    """
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'chosenSuit',

        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    REQUIRED_TARGETS = 1
    HEAL_ADDITIVE = True
    HEAL_CAP = 1.5

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.chosenSuit = None

    def calculate(self, ignoreModifiers: bool = False) -> None:
        self.chosenSuit = self.targets.pop(0)
        self.extraArgs = [self.suits.index(self.chosenSuit)]

        self.targets = [suit for suit in self.suits if suit != self.chosenSuit]

        super().calculate()

        # Remove that suit.
        result = self.createAttackTarget(self.chosenSuit.doId)
        result.hpAdjust = -self.chosenSuit.getHp()

        self.targets.append(self.chosenSuit)
        del self.chosenSuit

        # Send an event that did this attack in the round.
        self.sendEvent(BEG.EVENT_ERFIT_GAINS_FROM_THE_SCRAP)

        # Make sure erfit is RIPPED!!!!!!!!!!!
        self.invoker.addStatusEffect(SEE.EFFECT_RIPPED)

    def setTargetList(self) -> None:
        # If gains has happened this turn already, do the alt attack.
        if self.hasEventBeenSent(BEG.EVENT_ERFIT_GAINS_FROM_THE_SCRAP):
            return self.doAltAttack()

        # Get a list of all potential suits.
        suitList = self.getOtherSuits()

        # If there are no suits left, do the alternate attack.
        if not suitList:
            return self.doAltAttack()

        # Grab the suit with the lowest amount of HP.
        chosenSuit = sorted(suitList, key=lambda x: x.getHp(), reverse=False)

        if chosenSuit:
            self.targets = [chosenSuit[0]]
        else:
            # No suit somehow? Just do the alt attack.
            return self.doAltAttack()

    def doAltAttack(self):
        # Add a quake instead, as long as Erfit didn't revive.
        if not self.hasEventBeenSent(BEG.EVENT_SUIT_REVIVED):
            self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                AttackEnum.QUAKE, {"invoker": self.invoker},
                {"respectPreviousAdditions": True}
            ])

    def getDamage(self, target: BattleAvatar = None) -> int:
        # Heal all of the suits in the battle by half the suit's health.
        return -(self.chosenSuit.getHp() // 2)


@AttackClassAI(attackType=AttackEnum.HYDRATION_CHECK)
class HydrationCheckAI(SuitSingleAttackAI):

    def calculate(self) -> None:
        attackHit = self.getLanded()

        # Get the attack damage properly.
        toon: BattleAvatar = self.targets[0]
        damage = self.getDamage()
        damage = self.applyDamageModifiers(toon, damage)

        # Immortal toons only take 1 damage.
        # Well, 2, since this attack has its damage split in half.
        if toon.immortalMode:
            damage = 2

        if not attackHit:
            healAmount = 8
            # If the attack missed, then we passed the hydration check.
            # Heal 8 laff!
            missingLaff = toon.getMaxHp() - toon.getHp()
            if missingLaff > healAmount:
                damage = -healAmount
            else:
                damage = -missingLaff

        result = self.createAttackTarget(toon.doId)
        result.hpAdjust = -damage

        # Add the Hydrated status effect.
        toon.addStatusEffect(SEE.EFFECT_HYDRATED)

        # And, if the toon did take damage, send them to the shadow realm.
        # For this turn only, of course.
        if attackHit:
            toon.addStatusEffect(SEE.EFFECT_UNTOUCHABLE)

            # Tweak the damage.
            # Half goes to the hydration check, half goes to the fall.
            damageDealt = result.hpAdjust / 2
            result.hpAdjust = math.floor(damageDealt)
            comebackDamage = math.ceil(damageDealt)

            # The initial hydration will not be fatal, but the fall will be.
            if result.hpAdjust > toon.getHp() > 0:
                result.hpAdjust = toon.getHp() - 1

            # Also, add the HydrationComeback general attack.
            self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                AttackEnum.HYDRATION_COMEBACK,
                {"targets": [toon], "extraArgs": [comebackDamage]},
                {"mode": "end"},
            ])

    def getLanded(self) -> bool:
        # If there is only one toon in the battle, the attack always misses.
        if len(self.toons) <= 1:
            return False
        return super().getLanded()


@AttackClassAI(attackType=AttackEnum.LAFF_STEAL)
class LaffStealAI(GenericDamageAttackAI):
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'damageDealt',

        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    HEAL_ADDITIVE = True
    HEAL_CAP = 2.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damageDealt = 0

    def increaseDamageDealt(self, inc):
        self.damageDealt += inc

    def calculate(self, ignoreModifiers: bool = False) -> None:
        super().calculate()

        suitEffect = self.invoker.getStatusEffectOfType(StatusEffects.CountErclaimStatusEffect)

        if suitEffect:
            suitEffect.hasLaffSteal = None  # make sure count can laff steal again properly

    def getDamage(self, target: BattleAvatar = None) -> int:
        suitEffect = self.invoker.getStatusEffectOfType(StatusEffects.CountErclaimStatusEffect)

        # He has a base life steal of 125%, and it goes up by an additional 125% up to 250% at his lowest health.
        if not hasattr(suitEffect, 'timesSuitsRevived'):
            cap = 175
            baseHeal *= (2 / 3)
            MaxAdditionalHeal *= (2 / 3)
        else:
            baseHeal = 1.25
            MaxAdditionalHeal = 1.25
            cap = 3000

        healAmount = baseHeal + max((MaxAdditionalHeal*(1.0 - self.invoker.getHp() / self.invoker.getMaxHp())), 0)
        return -int(min(healAmount*self.damageDealt, cap))  # negative indicating a heal


@AttackClassAI(attackType=AttackEnum.PERSONAL_TRAINER)
class PersonalTrainerAI(AttackAI):
    """
    This is the attack object for Personal Trainer.
    Count Erfit uses this to revive dead cogs.
    """
    REQUIRED_TARGETS = 1
    selfDamageMult = 2.0

    def calculate(self) -> None:
        # Bump our level range.
        self.invoker.battle.instance.incrementMaxSuitLevel()

        # Generate suits accordingly.
        aliveSuits = self.getAliveSuits()
        suitsToGen = 4 - len(aliveSuits)
        for _ in range(suitsToGen):
            suit = self.invoker.battle.instance.genRandSuit(beSkelecog=1)
            self.invoker.battle.instance.reserveSuits.append((suit, 0))
            suit.addStartingStatusEffect(SEE.EFFECT_OVERCHARGED)
            suit.addStartingVisualEffect(VisualEffectEnum.OVERCHARGED)

        # Hurt Erfit for the health of the cog summoned.
        damageDealt = calculateHp({}, self.invoker.battle.instance.getSuitLevelRange()[1])
        reviveDamageMult = 1.0
        if self.invoker.getVisualEffectOfId(VisualEffectEnum.ERFIT_REVIVE):
            reviveDamageMult = 5.0

        result = self.createAttackTarget(self.invoker.doId)
        result.hpAdjust = -damageDealt * self.selfDamageMult * reviveDamageMult

    def setTargetList(self) -> None:
        # For compatibility, fail this attack if there's no instance
        if not hasattr(self.invoker.battle, 'instance'):
            return
        self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.PROTOON_SHAKE)
class ProToonShakeAI(GenericDamageAttackAI):
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'damageDealt', 'healAmount',

        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    HEAL_CAP = 1.5
    HEAL_ADDITIVE = True
    selfDamageMult = 2.0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damageDealt = 0
        # Extra Args
        self.healAmount = 0

    def increaseDamageDealt(self, inc):
        self.damageDealt += inc

    def setTargetList(self) -> None:
        self.targets = [self.invoker]

    def calculate(self):
        # Figure out how much we're going to heal.
        hpMult = self.invoker.getHealthPercentage() + 1.0
        self.healAmount = round(self.damageDealt * hpMult)

        # Pick a suit to heal.
        # We don't want Erfit himself in the list of possible suits.
        suitList = [suit for suit in self.getOtherSuits() if suit.getHealthPercentage() < 1.50]

        # Pick a suit to heal. If there is no suit, Erfit is healing himself.
        selfHeal = False
        if suitList:
            suitHpDict = {suit.getHp(): suit for suit in suitList}
            targetSuit = suitHpDict[max(suitHpDict.keys())]
            self.targets = [targetSuit]
        else:
            suitList.append(self.invoker)
            targetSuit = self.invoker
            selfHeal = True

        # If no suit, then dip.
        if not targetSuit:
            return

        super().calculate()

        # If we did not self-heal, we want to hurt Erfit.
        if not selfHeal:
            self.targets.append(self.invoker)
            # "heal"
            reviveDamageMult = 1.0
            if self.invoker.getVisualEffectOfId(VisualEffectEnum.ERFIT_REVIVE):
                reviveDamageMult = 5.0
            result = self.createAttackTarget(self.invoker.doId)
            result.hpAdjust = -self.healAmount * self.selfDamageMult * reviveDamageMult

    def getDamage(self, target: BattleAvatar = None) -> int:
        return -self.healAmount


@AttackClassAI(attackType=AttackEnum.RISE_FROM_THE_SCRAP)
class RiseFromTheScrapAI(AttackAI):
    """
    This is the attack object for Rise From The Scrap attack.
    Count Erclaim uses this to revive dead cogs.
    """
    REQUIRED_TARGETS = 1

    def calculate(self) -> None:
        suitEffect = self.invoker.getStatusEffectOfType(StatusEffects.CountErclaimStatusEffect)
        reviveCount = suitEffect.timesSuitsRevived

        aliveSuits = self.getAliveSuits()
        suitsToGen = 4 - len(aliveSuits)
        for _ in range(suitsToGen):
            self.invoker.battle.instance.reserveSuits.append(
                (self.invoker.battle.instance.genRandSuit(levelBonus=reviveCount), 0))

        return super().calculate()

    def setTargetList(self) -> None:
        suitEffect = self.invoker.getStatusEffectOfType(StatusEffects.CountErclaimStatusEffect)

        # Not salvaging old code from standin battle calculator or anything....
        if hasattr(suitEffect, 'timesSuitsRevived'):
            suitEffect.timesSuitsRevived += 1
        else:
            return

        self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.SACRIFICE)
class SacrificeAI(GenericDamageAttackAI):
    """
    This is the attack object used for Sacrifice.
    This is used by Count Erclaim to sacrifice other cogs.
    """
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'chosenSuit',

        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    HEAL_ADDITIVE = True
    HEAL_CAP = 2.0
    REQUIRED_TARGETS = 2

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.chosenSuit = None

    def calculate(self, ignoreModifiers: bool = False) -> None:
        suitEffect = self.invoker.getStatusEffectOfType(StatusEffects.CountErclaimStatusEffect)
        dmgMult = 1.1
        if not hasattr(suitEffect, 'timesSuitsRevived'):
            dmgMult = 1.05

        result = self.addDamageMultToSuit(self.invoker, setMultiplier=dmgMult)
        if result is not None:
            dmgMult = result

        # If we, the user of the Sacrifice, is an OverclockedForeman,
        # give all other alive Cogs in battle a stack of Worker's Compensation.
        if self.invoker.getStatusEffectOfType(StatusEffects.OverclockedForemanStatusEffect):
            for suit in self.getAliveSuits():
                self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                    AttackEnum.WORKERS_COMP, {"invoker": suit, "extraArgs": [1, 4], "unlure": True},
                ])

        self.extraArgs = [dmgMult * 100] + self.extraArgs

        return super().calculate(ignoreModifiers=True)

    def setTargetList(self) -> None:
        # We don't want count himself in the list of possible suits.
        suitList = [suit for suit in self.calculator.suits if suit.getHp() > 0 and \
            suit != self.invoker]

        # We don't want un-ceased cogs if there are other ceased cogs available.
        ceasedSuits = [suit for suit in suitList if suit.getStatusEffectOfType(StatusEffects.SueStatusEffect)]
        if len(ceasedSuits) >= 1:
            suitList = ceasedSuits

        # We also don't want skelecogs if there are other "flesh" cogs available.
        skelecogs = [suit for suit in suitList if suit.isSkelecog]
        if len(skelecogs) != len(suitList):
            for suit in skelecogs:
                suitList.remove(suit)

        # If there is a cog with an OverclockedForeman cheat with the PRISMATIC type, do not kill it.
        godSuits = []
        for suit in suitList:
            ocftfEffect = suit.getStatusEffectOfType(StatusEffects.OverclockedForemanStatusEffect)
            if ocftfEffect and ocftfEffect.getType() == StatusEffects.OverclockedForemanStatusEffect.PRISMATIC:
                godSuits.append(suit)

        # and clean out the godsuits.
        for suit in godSuits:
            if suit in suitList:
                suitList.remove(suit)

        # Grab the suit with the highest amount of HP.
        self.chosenSuit = sorted(suitList, key=lambda x: x.getHp(), reverse=True)
        if self.chosenSuit:
            self.targets = [self.chosenSuit[0]]

        self.targets.append(self.invoker)

    def getDamage(self, target: BattleAvatar = None) -> int:
        if target == self.invoker:
            return -self.chosenSuit.getHp()  # negative indicates a heal

        return self.chosenSuit.getHp()


@AttackClassAI(attackType=AttackEnum.SCOPE_CREEP)
class ScopeCreepAI(AttackAI):
    REQUIRED_TARGETS = 1

    def calculate(self) -> None:
        pass

    def setTargetList(self) -> None:
        suitEffect = self.invoker.getStatusEffectOfType(StatusEffects.CountErclaimStatusEffect)
        if hasattr(suitEffect, 'timesSuitsRevived'):
            return

        creepCount = 0
        creepEffect = self.invoker.getStatusEffectOfType(StatusEffects.CountCreepStatusEffect)
        if creepEffect:
            creepCount = creepEffect.timesCalled + 1
        self.invoker.removeStatusEffectOfId(SEE.EFFECT_COUNT_CREEP)
        effect, _ = self.invoker.addStatusEffect(SEE.EFFECT_COUNT_CREEP)
        somethingHappened = effect.updateMultiplier(creepCount)
        if not somethingHappened:
            return

        self.targets = [self.invoker]

# endregion

# region FTF / OCFTF


@AttackClassAI(attackType=AttackEnum.FTF_SUPERVISOR_LIFE_INSURANCE)
class FTFSupervisorLifeInsuranceAI(DamageInflictStatusAttackAI):
    """
    This is the attack object used for FTF Life Insurance.
    This is used by the supervisor at the beginning of the first round.
    """
    STATUS_EFFECT = SEE.EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST
    HEAL_ADDITIVE = True

    def calculate(self, ignoreModifiers: bool = False) -> None:
        return super().calculate(ignoreModifiers=True)

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        damageBoostAmount = 10 if self.invoker.getStatusEffectOfId(SEE.EFFECT_FTF_SUPERVISOR_FRAUD) else 5
        self.extraArgs = [damageBoostAmount]
        return super().handleStatusEffect(target, [damageBoostAmount])

    def getDamage(self, target: BattleAvatar = None) -> int:
        return -225

    def setTargetList(self) -> None:
        self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.FTF_PRESIDENT_EXTRA_TIP)
class FTFPresidentExtraTipAI(SuitHealAttackAI, SuitUnlureAttackAI):
    """
    This is the attack object used for FTF Extra Tip.
    This is used by the FTF Club President to unlure his Cogs.
    """
    REQUIRED_TARGETS = 1

    def calculate(self, ignoreModifiers: bool = False) -> None:
        SuitHealAttackAI.calculate(self)
        SuitUnlureAttackAI.calculate(self)

    def setTargetList(self) -> None:
        otherCogs = self.battle.battleCalc.allSuitsExceptMe(self.invoker)
        choiceList = [
            otherCog for otherCog in otherCogs
            if otherCog.getStatusEffectOfId(SEE.EFFECT_SUIT_LURED) and otherCog.getHp() > 0
        ]
        if choiceList:
            self.targets = [random.choice(choiceList)]


@AttackClassAI(attackType=AttackEnum.FTF_FOREMAN_REDTAPE)
class FTFForemanRedtapeAI(DamageInflictStatusAttackAI, SuitDoubleAttackAI):
    STATUS_EFFECT = SEE.EFFECT_REWARD_COOLDOWN

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        # The target already has a unite cooldown, give them vulnerability
        # instead.
        cooldownEffect = target.getStatusEffectOfType(StatusEffects.RewardCooldownStatusEffect)
        if cooldownEffect:
            cooldownEffect.setRounds(cooldownEffect.getRounds() + 3, adjust=False)
            return

        # They don't have a unite cooldown. Let's fix that.
        effect = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        effect.setRounds(2)
        target.addStatusEffect(self.STATUS_EFFECT, effect)

    def setTargetList(self) -> None:
        # Pick a random target using the suit double attack logic.
        return SuitDoubleAttackAI.setTargetList(self)


@AttackClassAI(attackType=(AttackEnum.FTF_FOREMAN_SNIPE, AttackEnum.FTF_PRESIDENT_SNIPE))
class FTFForemanSnipeAI(GenericDamageAttackAI):
    def calculate(self, ignoreModifiers: bool = False) -> None:
        return super().calculate(ignoreModifiers=bool(self.invoker.dna.name == 'ftf_s'))

    def getDamage(self, target: BattleAvatar = None) -> int:
        return -self.extraArgs[self.targets.index(target)]


@AttackClassAI(attackType=AttackEnum.FTF_NUCLEAR_TRANSFORMATION)
class FTFNuclearTransformationAI(DoNothingAI):
    def calculate(self) -> None:
        ourSuit = self.targets[0]
        # Find all possible morphable abilities
        possibleOptions = FindTheFamilyGlobals.AllMorphableAbilities[:]
        # Remove our own ID so that we don't morph back into ourself
        possibleOptions.remove(ourSuit.specialContainerId)
        # Remove the ID of other cogs in our battle, if they have the "only one" flag
        otherSuits = [suit for suit in
                      self.battle.battleCalc.allSuitsExceptMe(exceptSuit=ourSuit, suits=self.battle.activeSuits) if
                      suit.getHp() > 0]
        bannedAbilities = [otherSuit.specialContainerId for otherSuit in otherSuits if
                           otherSuit.specialContainer.onlyOne]
        for bannedAbility in bannedAbilities:
            if bannedAbility in possibleOptions:
                possibleOptions.remove(bannedAbility)

        # Now pick a new effect for us to transform into
        newContainerId = random.choice(possibleOptions)
        newContainer = FindTheFamilyGlobals.FamilyRegistry[newContainerId]
        # Save our old HP ratio so that it will be consistent once we transform
        oldHpRatio = (ourSuit.getHp() / ourSuit.getMaxHp())

        # Handle moving all this good stuff over server side
        ourSuit.specialContainerId = newContainerId
        ourSuit.specialContainer = newContainer
        from toontown.clashsuit.suit.SuitDNA import SuitDNA
        from toontown.clashbattle.battle import SuitBattleGlobals
        dna = SuitDNA()
        dna.newSuit(newContainer.suitType)
        ourSuit.dna = dna
        attributes = SuitBattleGlobals.SuitAttributes[ourSuit.dna.name]
        ourSuit.level = newContainer.suitLevel - attributes['level'] - 1
        maxHealth = newContainer.health
        if ourSuit.getStatusEffectOfId(SEE.EFFECT_FTF_DUALCORE) or ourSuit.hasDualCoreEffect:
            maxHealth *= FindTheFamilyGlobals.DualCoreHealthBoost
        if ourSuit.getStatusEffectOfId(SEE.EFFECT_FTF_NUCLEAR) or ourSuit.hasNuclearEffect:
            maxHealth *= FindTheFamilyGlobals.NuclearHealthBoost
        ourSuit.setMaxHp(maxHealth)
        newHealth = int(round(maxHealth * oldHpRatio))
        ourSuit.setHp(newHealth)
        ourSuit.ftf_nuclearStoredHp = newHealth

        # Clear out any lingering effects they have that aren't our nuclear effect
        for statusEffect in ourSuit.getStatusEffects()[:]:
            if (isinstance(statusEffect, FindTheFamilyBaseEffect) and statusEffect.effectId != SEE.EFFECT_FTF_NUCLEAR) \
                    or statusEffect.effectId == SEE.EFFECT_FTF_SUPERVISOR_INSURED:
                statusEffect.delete()
        # Can't seem to find a better place to get rid of this so
        ourSuit.removeVisualEffectOfId(VisualEffectEnum.FTF_ATTORNEY_JOGGING)

        # Add their new effect based on their transformation
        if newContainer.effectId != SEE.EFFECT_BASE:
            ourSuit.addStatusEffect(newContainer.effectId)
        # Check if we need to add back the insurance effect if we're turning into a supervisor
        if ourSuit.dna.name in ('ftf_m', 'ftf_m_cf'):
            ourSuit.addStatusEffect(SEE.EFFECT_FTF_SUPERVISOR_INSURED)

        if newContainerId == FindTheFamilyGlobals.AbilityEnum.President_Shivering:
            # We are now a shivering president, convert soak to frozen
            self.convertEffectToNew(ourSuit, fromEffectId=SEE.EFFECT_SUIT_SOAKED, toEffectId=SEE.EFFECT_SUIT_FROZEN)
        else:
            # We are converting to something that is not a shivering president, replace frozen if we have it
            self.convertEffectToNew(ourSuit, fromEffectId=SEE.EFFECT_SUIT_FROZEN, toEffectId=SEE.EFFECT_SUIT_SOAKED)

        self.extraArgs = [newContainerId, maxHealth, newHealth]

        super().calculate()

    def convertEffectToNew(self, suit, fromEffectId, toEffectId):
        oldEffect = suit.getStatusEffectOfId(fromEffectId)
        if oldEffect:
            rounds = oldEffect.getRounds()

            # Remove old effect
            oldEffect.delete()

            # Apply the new effect
            newEffect = SEG.createStatusEffect(suit, toEffectId)
            # No adjust so that it does not include the +1 rounds used on the server.
            newEffect.setRounds(rounds, adjust=False)
            suit.addStatusEffect(toEffectId, newEffect)


@AttackClassAI(attackType=AttackEnum.FTF_PRESIDENT_DRIVER)
class FTFPresidentDriverAI(DamageInflictStatusAttackAI, SuitDoubleAttackAI):
    STATUS_EFFECT = SEE.EFFECT_DAMAGE_DOWN

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        damageDownEffect = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        damageDownEffect.setMultiplier(0.75)
        damageDownEffect.setRounds(1)
        target.addStatusEffect(SEE.EFFECT_DAMAGE_DOWN, damageDownEffect)

    def setTargetList(self) -> None:
        # Pick a random target using the suit double attack logic.
        return SuitDoubleAttackAI.setTargetList(self)


@AttackClassAI(attackType=AttackEnum.OVERCLOCKED_FOREMAN_DESTRUCTION)
class FTFForemanDestructionAI(HitAllParticipantsAttackAI):
    def calculate(self, ignoreModifiers: bool = False) -> None:
        super().calculate(ignoreModifiers=ignoreModifiers)
        if self.getLanded():
            for target in self.targets:
                if self.invoker is target or target.isToon():
                    continue

                # First remove their lure effect
                target.deleteStatusEffectOfId(SEE.EFFECT_SUIT_LURED)
                # Now give them some permanent lure resistance :)
                lureEffect = SEG.createStatusEffect(target, SEE.EFFECT_LURE_RESISTANCE)
                lureEffect.setAmount(1)
                target.addStatusEffect(SEE.EFFECT_LURE_RESISTANCE, lureEffect)

    def getDamage(self, target: BattleAvatar = None) -> int:
        if target is self.invoker:
            return 50000
        elif target.isToon():
            return 50
        else:
            return 200


@AttackClassAI(attackType=AttackEnum.FTF_PRESIDENT_SHATTER_DAMAGE)
class FTFPresidentShatterDamageAI(ShatterDamageAI):
    DamagePercent = 0.33

    def calculate(self, ignoreModifiers: bool = True) -> None:
        super().calculate(ignoreModifiers=ignoreModifiers)
        if self.getLanded():
            for target in self.targets:
                # Now we can add slush fund to all remaining cogs
                target.addStatusEffect(SEE.EFFECT_SLUSH_FUND)


@AttackClassAI(attackType=AttackEnum.FTF_FOREMAN_CIGAR_SMOKE)
class FTFForemanCigarSmokeAI(DamageInflictStatusAttackAI, SuitDoubleAttackAI):
    STATUS_EFFECT = SEE.EFFECT_FTF_FOREMAN_BURNING_SMOKED

    def setTargetList(self) -> None:
        # Pick a random target using the suit double attack logic.
        return SuitDoubleAttackAI.setTargetList(self)

# endregion

# region High Roller


@AttackClassAI(attackType=AttackEnum.FINISH_BETWEEN)
class FinishBetweenAI(GenericDamageAttackAI):
    def calculate(self, ignoreModifiers: bool = False) -> None:
        # Let's kill EVERYONE. (except game show man)
        super().calculate(ignoreModifiers=True)
        self.invoker.removeStatusEffectOfId(SEE.EFFECT_COMMERCIAL)

    def setTargetList(self) -> None:
        self.targets = self.getOtherSuits()

    def getDamage(self, target: BattleAvatar = None) -> int:
        return target.getHp()


@AttackClassAI(attackType=AttackEnum.SPIN_WHEEL)
class SpinWheelAI(DoNothingAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@AttackClassAI(attackType=AttackEnum.RANDOM_GAME)
class RandomGameAI(DoNothingAI):
    """
    Every 4 rounds, starting on round 2, High Roller will spin
    the wheel and decide on a new game to activate!
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currentGame, *self.extraArgs = self.extraArgs

    def calculate(self) -> None:
        # Let's add new cogs to the battle.
        instance = self.battle.instance
        from toontown.instances.HighRollerGlobals import HighRollerGameEnum
        if self.currentGame == HighRollerGameEnum.TRIVIA:
            instance.makeTriviaSuits(*self.extraArgs)
            self.tauntIndex = 0
        elif self.currentGame == HighRollerGameEnum.PUZZLE:
            instance.makePuzzleSuits(len(self.battle.activeToons))
            self.tauntIndex = 1
        elif self.currentGame == HighRollerGameEnum.SHUFFLE:
            instance.makeShuffleSuits(*self.extraArgs)
            self.tauntIndex = 2
        self.setAttackTauntIndex()


@AttackClassAI(attackType=AttackEnum.RANDOM_GAME_FINISH)
class RandomGameFinishAI(GenericDamageAttackAI):

    def calculate(self, ignoreModifiers: bool = False) -> None:
        # Let's kill EVERYONE. (except game show man)
        for target in self.targets:
            target.clearStatusEffects()
        super().calculate(ignoreModifiers=True)

    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()
        if self.invoker in self.targets:
            self.targets.remove(self.invoker)

    def getDamage(self, target: BattleAvatar = None) -> int:
        return target.getHp()


@AttackClassAI(attackType=AttackEnum.RANDOM_GAME_PUNISH)
class RandomGamePunishAI(GenericDamageAttackAI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.punishedToons, self.leftoverSuits, self.wantExtraPunishment = self.extraArgs[0:3]
        self.extraArgs = []

    def calculate(self, ignoreModifiers: bool = False) -> None:
        from toontown.instances.HighRollerGlobals import getPipReward, HighRollerGameEnum
        super().calculate()
        laffGain = []
        for i, toon in enumerate(self.getAliveToons()):
            pointCounter = toon.getStatusEffectOfId(SEE.EFFECT_PIP_COUNTER)
            if not pointCounter:
                continue
            isPunished = int(toon not in self.punishedToons)
            numPoints = getPipReward(self.battle.instance.currentGame, isPunished, self.leftoverSuits, self.wantExtraPunishment)
            toonLaffGain = int(numPoints * 1.5)
            laffGain.append(toonLaffGain)
            self.battle.battleCalc.sendEvent(BEG.EVENT_ADAPTIVE_LAFF, eventArgs=[toon, toonLaffGain, 'addToCap'])

        if len(laffGain) > 0 and not self.battle.battleCalc.hasEventBeenSent(BEG.EVENT_HROLL_FORCE_MAX_LAFF_MOVIE):
            # Add the extra laff we got from this game to the existing laff up attack
            laffUpAtk = self.battle.battleCalc.attackOrder.getAttackOfType(AttackEnum.HR_TOON_LAFF_UP)
            if laffUpAtk:
                for i in range(len(self.getAliveToons())):
                    laffUpAtk.extraArgs[i+1] = laffUpAtk.extraArgs[i+1] + laffGain[i]
        self.battle.instance.b_setCurrentGame(HighRollerGameEnum.BETWEEN)

    def setTargetList(self) -> None:
        self.targets = self.punishedToons

    def getDamage(self, target: BattleAvatar = None) -> int:
        return target.getMaxHp() * self.battle.instance.toonIsWrong(target)

    def applyDamageModifiers(self, target: BattleAvatar, attackDamage: int,
                             damaging: bool = True, invokerMods: bool = True,
                             targetMods: bool = True, overrideAttackType: int = None):
        if isinstance(target, DistributedSuitBaseAI):
            return attackDamage
        return super().applyDamageModifiers(target, attackDamage, damaging, invokerMods, targetMods)


@AttackClassAI(attackType=AttackEnum.HIGHROLLER_COMMERCIAL)
class HighRollerCommercialAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_COMMERCIAL

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        target.addStatusEffect(self.STATUS_EFFECT)

    def setTargetList(self) -> None:
        self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.HIGHROLLER_HOLLYWOOD)
class HighRollerHollywoodAI(DoNothingAI):
    def calculate(self) -> None:
        # Let's send the big bois into the battle.
        self.battle.instance.genBigHollies()


@AttackClassAI(attackType=AttackEnum.HIGHROLLER_BEGIN_MADNESS)
class HighRollerBeginMadnessAI(DoNothingAI):
    def calculate(self) -> None:
        # Give toons their new status effect
        for toon in self.getAliveToons():
            toon.addStatusEffect(effectId=SEE.EFFECT_RAISING_THE_ANTE)

        # Let's send the first group of clones into the battle.
        self.battle.instance.genCloneSuits()


@AttackClassAI(attackType=AttackEnum.TRICK_OF_THE_LIGHT)
class TrickOfTheLightAI(DoNothingAI):
    def calculate(self) -> None:
        super().calculate()
        # Let's add more clones to the battle.
        self.battle.instance.genCloneSuits()

        # Make High Roller a God
        self.invoker.addStatusEffect(SEE.EFFECT_HR_UNTOUCHABLE)


@AttackClassAI(attackType=AttackEnum.HIGHROLLER_CLONE_TOONUP)
class HighRollerCloneToonupAI(GenericDamageAttackAI):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damageDict = self.extraArgs[0]
        self.extraArgs = []

    def setTargetList(self) -> None:
        self.targets = [toon for toon in list(self.damageDict.keys()) if self.damageDict[toon] != 0]

    def getDamage(self, target: BattleAvatar = None) -> int:
        return self.damageDict.get(target, 0)

    def applyDamageModifiers(self, target: BattleAvatar, attackDamage: int,
                             damaging: bool = True, invokerMods: bool = True,
                             targetMods: bool = True, overrideAttackType: int = None):
        if isinstance(target, DistributedSuitBaseAI):
            return attackDamage
        return super().applyDamageModifiers(target, attackDamage, damaging, invokerMods, targetMods)

@AttackClassAI(attackType=AttackEnum.HIGHROLLER_CLONE_TRAP)
class HighRollerCloneTrapAI(RemoveStatusEffectAttackAI, GenericDamageAttackAI):
    """
    Explodes cogs and toons alike for either 100 or 200 damage,
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
        return 100 * self.damageMult


@AttackClassAI(attackType=AttackEnum.HIGHROLLER_CLONE_SQUIRT)
class HighRollerCloneSquirtAI(GenericDamageAttackAI, ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_FAKE_SOAKED

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.damageDict = self.extraArgs[0]
        self.extraArgs = []

    def calculate(self, ignoreModifiers: bool = False) -> None:
        GenericDamageAttackAI.calculate(self)
        ApplyStatusEffectAttackAI.calculate(self)

    def setTargetList(self) -> None:
        self.targets = [toon for toon in list(self.damageDict.keys()) if self.damageDict[toon] != 0]

    def getDamage(self, target: BattleAvatar = None) -> int:
        return self.damageDict.get(target, 0)

    def applyDamageModifiers(self, target: BattleAvatar, attackDamage: int,
                             damaging: bool=True, invokerMods: bool=True,
                             targetMods: bool=True, overrideAttackType: int = None):
        if isinstance(target, DistributedSuitBaseAI):
            return attackDamage
        return super().applyDamageModifiers(target, attackDamage, damaging, invokerMods, targetMods)


@AttackClassAI(attackType=AttackEnum.DICE_ROULETTE)
class DiceRouletteAI(GenericDamageAttackAI, SuitSingleAttackAI):
    ashleyDamage = [30, 60, 120, 180, 240, 300]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ashley Olsen die for dmg amount
        self.ashleyDie = random.randint(1, 6)
        self.maryKateDie = random.randint(1, 6)
        self.extraArgs += [self.ashleyDie, self.maryKateDie]

    def getDamage(self, target: BattleAvatar=None) -> int:
        return self.ashleyDamage[self.ashleyDie - 1] if self.maryKateDie != 5 else 0

    def setTargetList(self) -> None:
        if self.maryKateDie == 6:
            self.targets = self.getAliveSuits()
        elif self.maryKateDie <= 4:
            self.targets = SuitSingleAttackAI.chooseRandomToon(self, amount=self.maryKateDie)
        else:
            self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.ACE_IN_THE_HOLE)
class AceInTheHoleAI(DamageInflictStatusAttackAI, SuitGroupAttackAI):
    STATUS_EFFECT = SEE.EFFECT_AITH_DAMAGE_TAKEN_UP


@AttackClassAI(attackType=AttackEnum.FREE_CRUISE)
class FreeCruiseAI(SuitGroupAttackAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Essentially, this attack will either hit all toons or miss all toons.
        # We just need to pre-calc the accuracy roll here.
        self.accuracy = 100 if self.getLanded() else 0


@AttackClassAI(attackType=AttackEnum.HR_EXIT_UNTOUCHABLE)
class HRExitUntouchableAI(DoNothingAI):
    def calculate(self) -> None:
        super().calculate()

        # No more God Roller
        self.invoker.removeStatusEffectOfId(SEE.EFFECT_HR_UNTOUCHABLE)
        self.invoker.removeVisualEffectOfId(VisualEffectEnum.HR_UNTOUCHABLE)
        self.invoker.addVisualEffect(VisualEffectEnum.ROLLED)


@AttackClassAI(attackType=AttackEnum.ROLLED)
class RolledAI(SuitGroupAttackAI):
    DAMAGE_RANGE = (0.85, 1.15)

# endregion
