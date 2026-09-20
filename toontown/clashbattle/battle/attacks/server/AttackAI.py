import math
import random
from typing import TYPE_CHECKING, List

from otp.ai.AIBaseGlobal import simbase
from toontown.clashbattle.battle import PassiveAttributeDefs
from toontown.clashbattle.battle.BattleEventDefinitionClasses import AttackEventDefinition
from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.BattleGlobals import NO_TRAP
from toontown.clashbattle.battle.BattleListenerObject import BattleListenerObject
from toontown.clashbattle.battle.attacks.base.AttackGlobals import getTauntPool
from toontown.clashbattle.battle.attacks.base.AttackTarget import AttackTarget
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.environmental.server.Environmentals import EnvironmentalBase
from toontown.clashbattle.battle.statuses import StatusEffects, SEE
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.toon.gui.ToonTipGlobals import TTE
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI
from toontown.toon.ClashDistributedToonBaseAI import ClashDistributedToonBaseAI
from toontown.utils.AstronStruct import AstronStruct
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

if TYPE_CHECKING:
    from toontown.clashbattle.battle.BattleListenerAI import BattleListenerAI
    from toontown.clashbattle.battle.distributed.ClashBattleBaseAI import ClashBattleBaseAI


@DirectNotifyCategory()
class AttackAI(AstronStruct, BattleListenerObject):
    """
    AttackAI: The base class for all attack functionality.

    :param attackType: The enum value of the attack.
    :param rounds: The current battle round number.
    :param invoker: The invoker of the attack.
    :param targets: The list of BattleAvatar targets which
    the attack affects.
    :param unlure: A flag which when set to True, will unlure
    the invoker (if it exists).
    :param damageMult: How much to multiply the damage of the
    attack by.
    :param extraArgs: Any extra arguments.
    """

    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'tauntIndex',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    # Toggle for knockback damage.
    WANT_KB_BONUS = False
    # Toggle for combination damage.
    WANT_HP_BONUS = False
    # Toggle for taunt phrase.
    WANT_TAUNT = True

    # The status effect id to apply on all affected targets.
    STATUS_EFFECT = None

    # The visual effect id to apply to all affected targets.
    VISUAL_EFFECT = None

    # The amount of targets required for the attack to begin
    # calculating.
    REQUIRED_TARGETS = 0

    # What to restrict a suit's health to when they heal.
    HEAL_CAP = 1.0
    
    # Are suit heals additive?
    HEAL_ADDITIVE = False

    # Does this attack take additional barrier time to consider?
    ADDITIONAL_BARRIER_LENGTH = 0.0

    def __init__(self, attackType: AttackEnum, rounds: int = 0,
                 invoker: BattleAvatar = None, targets: list= None,
                 unlure: bool = False, damageMult: float = 1.0,
                 extraArgs: list = None, tauntIndex: int = 0) -> None:
        self.attackType = attackType
        self.rounds = rounds
        self.invoker = invoker
        self.targets = targets or []  # type: list[BattleAvatar]
        self.unlure = unlure
        self.damageMult = damageMult
        self.extraArgs = extraArgs or []
        self.tauntIndex = tauntIndex

        # The index at which the attack occurred at.
        # This is set after the round is over, but before
        # the attack gets sent to the client.
        self.attackIndex = -1

        # This is what stores the results of the attack in the form of
        # AttackTarget dataclasses.
        self.results = []  # type: list[AttackTarget]

        # Variables set by the battle.
        self.battle = None  # type: ClashBattleBaseAI
        self.battleListener = None  # type: BattleListenerAI
        self.suits = []  # type: list[BattleAvatar]
        self.toons = []  # type: list[BattleAvatar]
        self.environmentals = []  # type: list[EnvironmentalBase]

        # How many of our same attack type is currently being used?
        # This is currently only used by toon attacks.
        self.attackAmount = 0

        # Whether the attack was inserted.
        self.inserted = False

        # The priority at which the attack will occur.
        self.priority = 0

        # Toon attack specific fields.
        self.level = -1
        self.target = -1

        # Set the taunt index during initialization.
        self.setAttackTauntIndex()
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(attackType={repr(self.attackType)}, rounds={self.rounds}, "\
            f"invoker={self.invoker}, targets={self.targets}, unlure={self.unlure}, damageMult={self.damageMult}, "\
            f"suits={self.suits}, toons={self.toons}, priority={self.priority}, "\
            f"results={self.results})"
    
    def toStruct(self) -> list:
        # Convert the attack targets into structs.
        results = AttackTarget.toStructList(self.results)

        # Replace all distributed objects in the extra args
        # with doIds.
        extraArgs = [getattr(arg, "doId", arg) for arg in self.extraArgs]

        return [
            self.attackIndex, self.attackType, getattr(self.invoker, "doId", 0), results, 
            self.level, self.target, self.taunt, extraArgs
        ]

    def cleanup(self) -> None:
        """Purge all variables attached to this object from memory.
        """
        if self.hasBattleListener():
            self.removeListenerObject(self)
        del self.invoker
        del self.targets
        del self.extraArgs
        del self.results
        del self.battle
        del self.battleListener
        del self.suits
        del self.toons
        del self.environmentals
    
    def calculate(self) -> None:
        raise NotImplementedError(f"Called unimplemented AttackAI.calculate() on {self.__class__.__name__}")
    
    def setTargetList(self) -> None:
        """Set the target list of the attack. This function isn't entirely
        necessary to implement if a target list is already provided upon
        initialization.
        """
        if self.targets:
            return

        raise NotImplementedError(f"Called unimplemented AttackAI.setTargetList() on {self.__class__.__name__}")
    
    def getLanded(self) -> bool:
        raise NotImplementedError(f"Called unimplemented AttackAI.getLanded() on {self.__class__.__name__}")
    
    def getDamage(self, target: BattleAvatar=None) -> int:
        raise NotImplementedError(f"Called unimplemented AttackAI.getDamage() on {self.__class__.__name__}")

    def handleHpBonus(self, hpBonus: int, target: BattleAvatar) -> None:
        damageAmount = hpBonus

        if isinstance(target, ClashSuitBaseAI):
            # If we have it, apply a combo damage effectiveness multiplier
            effectiveness = target.getPassive(PassiveAttributeDefs.COMBO_EFFECTIVENESS)
            if effectiveness:
                damageAmount = damageAmount * effectiveness

        # Apply all combo damage modifiers on the suit.
        for comboEffect in target.getStatusEffectsOfType(StatusEffects.ComboDamageModifierStatusEffect):
            damageAmount = comboEffect.handleAttackDamageTaken(damageAmount, self.attackType)
        
        # Apply all environmental damage modifiers.
        for environmental in self.environmentals:
            damageAmount = environmental.handleComboDamage(self.attackType, damageAmount, target, self)

        # Set combo multiplier.
        if damageAmount > 0:
            # Combo Damage Tip
            self.showToonTipAll(TTE.TIP_COMBO_DAMAGE)

        return damageAmount
    
    def handleKbBonus(self, kbBonus: int, target: BattleAvatar) -> None:
        damageAmount = kbBonus

        # If we have it, apply a knockback damage effectiveness multiplier
        if isinstance(target, ClashSuitBaseAI):
            effectiveness = target.getPassive(PassiveAttributeDefs.KNOCKBACK_EFFECTIVENESS)
            if effectiveness:
                damageAmount = int(math.ceil(damageAmount * effectiveness))

        # Apply knockback multipliers.
        for comboEffect in target.getStatusEffectsOfType(StatusEffects.KnockbackDamageModifierStatusEffect):
            damageAmount = comboEffect.handleAttackDamageTaken(damageAmount, self.attackType)
        
        # Apply all environmental damage modifiers.
        for environmental in self.environmentals:
            damageAmount = environmental.handleKnockbackDamage(self.attackType, damageAmount, target, self)

        if damageAmount > 0:
            # Knockback Damage Tip
            self.showToonTipAll(TTE.TIP_LURE_KNOCKBACK)

        return damageAmount
    
    def apply(self) -> None:
        for result in self.results:
            av = self.findTarget(result.avId)

            damages = [result.hpAdjust]

            if result.hpAdjust < 0:
                if not self.invoker:
                    event = BEG.EVENT_GENERAL_DAMAGE
                elif self.isToon(self.invoker):
                    event = BEG.EVENT_TOON_DAMAGE
                else:
                    event = BEG.EVENT_SUIT_DAMAGE

                eventArgs = [av, self.invoker, result.hpAdjust, self.attackType, self.attackIndex]
                if event == BEG.EVENT_TOON_DAMAGE:
                    eventArgs.append(self.level)

                self.sendEvent(event, eventArgs)

            if result.hpBonus < 0 and self.WANT_HP_BONUS:
                result.hpBonus = self.roundDamageValue(self.handleHpBonus(result.hpBonus, av))
                self.sendEvent(BEG.EVENT_TOON_COMBO_DAMAGE, [
                    av, self.invoker, result.hpBonus, self.attackType])
                damages.append(result.hpBonus)
            else:
                result.hpBonus = self.roundDamageValue(result.hpBonus)

            if result.kbBonus < 0 and self.WANT_KB_BONUS:
                result.kbBonus = self.roundDamageValue(self.handleKbBonus(result.kbBonus, av))
                self.sendEvent(BEG.EVENT_TOON_KNOCKBACK_DAMAGE, [
                    av, self.invoker, result.kbBonus, self.attackType])
                damages.append(result.kbBonus)

            for i, hp in enumerate(damages):
                hp = self.damageAvatar(av, result, hp)
                if i == 0:
                    result.hpAdjust = hp
    
    def damageAvatar(self, av: BattleAvatar, result: AttackTarget, hp: int) -> int:
        if isinstance(av, ClashSuitBaseAI):
            return self.damageSuit(av, result, hp)

        elif isinstance(av, ClashDistributedToonBaseAI):
            self.damageToon(av, result, hp)
            return hp

        raise Exception(f"Invalid target type in damageAvatar: {type(av)}, {repr(self)}")

    def damageSuit(self, av: ClashSuitBaseAI, result: AttackTarget, hp: int) -> int:
        """Updates the HP of a Suit."""
        if hp > 0:
            hp = self.healSuit(av, hp, additive=True, healthCap=self.HEAL_CAP)

            self.sendEvent(BEG.EVENT_HEALED, [av, hp])
            return hp

        if av.getHp() <= 0:
            return hp

        formerHp = av.getHp()
        av.setHp(formerHp + hp)

        if av.getHp() > 0:
            return hp

        preventDeathEffect = av.getStatusEffectOfType(StatusEffects.SuitPreventDeathStatusEffect)
        if preventDeathEffect and preventDeathEffect.canPreventDeath():
            av.setHp(1)
            preventDeathEffect.onDeathPrevented()
            return -(formerHp - 1)

        if av.getSkeleRevives() >= 1:
            av.useSkeleRevive()
            self.addDamageMultToSuit(av, setMultiplier=av.getReviveDamageMultiplier())
            av.addVisualEffect(VisualEffectEnum.SKELECOG)
            result.revived = True
            self.sendEvent(BEG.EVENT_SUIT_REVIVED, [av, av.getSkeleRevives(), self.invoker])

            # V2.0 Cogs Tip
            self.showToonTipAll(TTE.TIP_V2_COG)
            return hp

        result.died = True
        self.sendEvent(BEG.EVENT_SUIT_DIED, [av, self.invoker, self.attackType])

        self.suitLeftBattle(av)
        return hp
    
    def damageToon(self, av: ClashDistributedToonBaseAI, result: AttackTarget, hp: int) -> None:
        """Updates the HP of a Toon."""
        toonHp = av.getHp()

        # Send an event whenever a toon gets healed.
        if hp > 0:
            hpDelta = av.getMaxHp() - toonHp
            hp = min(hpDelta, hp)
            self.sendEvent(BEG.EVENT_HEALED, [av, hp])

        if toonHp + hp <= 0:
            result.died = True
            self.sendEvent(BEG.EVENT_TOON_DIED, [av, self.invoker, self.attackType])

        av.hpAdjustBattle += hp
    
    def findTarget(self, targetId: int) -> BattleAvatar:
        """Finds and returns a target with the indicated doId.
        
        :param targetId: The target's doId.
        """
        targets = [tgt for tgt in self.targets if tgt.doId == targetId]
        if targets:
            return targets[0]
        
    def findResult(self, targetId: int) -> AttackTarget:
        """Finds and returns an AttackTarget object (contains the results of the
        attack on the target specifically).
        
        :param targetId: The target's doId.
        """
        results = [tgt for tgt in self.results if tgt.avId == targetId]
        if results:
            return results[0]
    
    def getDeadTargets(self) -> list:
        return [result for result in self.results if result.died]

    def createAttackTarget(self, avId: int) -> AttackTarget:
        """Creates an AttackTarget object with the given avatar id.
        """
        # Prevent duplicate entries.
        result = [result for result in self.results if result.avId == avId]
        if result:
            return result[0]

        attackTarget = AttackTarget(avId)
        self.results.append(attackTarget)
        return attackTarget

    def setBattleListener(self, battleListener):
        if self.hasBattleListener():
            self.removeListenerObject(self)
        # Assign battle listener, and set self to listen to attack events.
        self.battleListener = battleListener
        self.addListenerObject(self, AttackEventDefinition)

    def getBattleListener(self):
        return self.battleListener
    
    def applyDamageModifiers(self, target: BattleAvatar, attackDamage: int,
                             damaging: bool = True, invokerMods: bool = True,
                             targetMods: bool = True, overrideAttackType: int = None):
        """Runs through every possible damage modifier to base damage per 
        target and applies it.
        """
        if attackDamage < 0:
            if self.isSuit(target) and not self.HEAL_ADDITIVE:
                return -self.getSuitHealAmount(target, -attackDamage, self.HEAL_CAP)
            return attackDamage

        # We may need to override the attack type in some cases, such as with lure/trap
        functionalAttackType = overrideAttackType or self.attackType
        attackDamage = float(attackDamage)

        if invokerMods and self.invoker is not None:
            # If we have any gag effectiveness status effects, then affect the toon's damage here.
            # Sort these by their "priority" value, highest applies first
            effectivenessStatusEffects = sorted(
                self.invoker.getStatusEffectsOfType(StatusEffects.AttackEffectivenessStatusEffect), 
                key=lambda x: x.SortPriority, reverse=True
            )

            for statusEffect in effectivenessStatusEffects:
                if not statusEffect.isDisabled():
                    attackDamage = statusEffect.handleAttackDamage(functionalAttackType, attackDamage, target)

            # Apply all environmental damage modifiers.
            for environmental in self.environmentals:
                attackDamage = environmental.handleBaseDamage(functionalAttackType, attackDamage, target, self)

        # Handle trap slightly differently, as the cog's damage taken modifiers
        # don't matter until it actually goes off
        if damaging and targetMods:
            # If the target has any damage taken modifiers, apply them.
            modifierStatusEffects = target.getStatusEffectsOfType(
                StatusEffects.AvatarTakeModifiedDamageStatusEffect)

            for statusEffect in modifierStatusEffects:
                if not isinstance(statusEffect, StatusEffects.LureStatusEffect):
                    attackDamage = statusEffect.handleAttackDamageTaken(attackDamage, functionalAttackType,
                                                                        self.invoker)
                # Rainmaker Heavy Rain requires damage to be absorbed only when we hit, and it will modify the damage values accordingly
                if type(statusEffect) is StatusEffects.HeavyRainStatusEffect and self.getLanded():
                    damageAbsorbed = statusEffect.handleAbsorbedDamageTaken(attackDamage)
                    attackDamage -= damageAbsorbed

            # Apply all environmental damage modifiers.
            for environmental in self.environmentals:
                attackDamage = environmental.handleDamageTaken(
                    target, self.invoker, attackDamage, functionalAttackType)

        attackDamage = int(math.ceil(round(attackDamage, 4)))

        # If they have the instakill flag set, then do 60,000 damage.
        if damaging and getattr(self.invoker, 'instakill', False):
            attackDamage = 60000

        # Set their damage if necessary
        if damaging and (getattr(self.invoker, 'setdamage', None) is not None):
            attackDamage = getattr(self.invoker, 'setdamage')
        
        # If the target has the immortal flag set, do 1 damage.
        if damaging and getattr(target, "immortalMode", False):
            attackDamage = min(attackDamage, 1)

        return attackDamage
    
    def suitLeftBattle(self, suit: ClashSuitBaseAI) -> None:
        """
        Removes the indicated suit from the battle calculator.
        """
        # Clear their aggro map.
        suit.aggroMap.clear()

        # Clear all of their status effects now that they are dead.
        self.clearAvatarStatusEffects(suit)
        
        self.sendEvent(BEG.EVENT_SUIT_LEFT, [suit])

        # And make sure the battle listener is no longer listening to this suit.
        if not suit.hasCleanedUpBattle:
            self.removeListenerObject(suit)
    
    def showToonTipAll(self, tipId: int) -> None:
        for toon in self.getToons():
            toon.showToonTip(tipId)
        
    def postprocess(self) -> tuple:
        """Handles all calculations that occur upon the end
        of the battle movie.
        """
        deadSuits, needUpdate = [], False
        for target in self.targets:
            if not isinstance(target, ClashSuitBaseAI):
                continue

            result = [r for r in self.results if r.avId == target.doId]
            if result:
                result = result[0]
                hp = result.hpAdjust
                if hp < 0 and self.attackType == AttackEnum.TOON_LURE:
                    target.battleTrap = NO_TRAP
                    needUpdate = True
                if result.died and target not in deadSuits:
                    deadSuits.append(target)
        
        return deadSuits, needUpdate
        
    """
    Utility methods
    """
    
    def avatarHasAnyStatusEffect(self, av: BattleAvatar) -> bool:
        """Does the given avatar have any of the specified status
        effects of the attack?
        """
        return any(bool(av.getStatusEffectOfId(status)) for status in self.STATUS_EFFECT)
    
    def findAllSuitsOfName(self, name: str) -> List[ClashSuitBaseAI]:
        return [suit for suit in self.suits if suit.dna.name == name]
    
    def getToons(self) -> List[ClashDistributedToonBaseAI]:
        """Returns a list of all toon objects."""
        return self.getObjectsFromIds(self.toons)
    
    def getAliveToons(self) -> List[ClashDistributedToonBaseAI]:
        """Returns a list of all alive toons.
        """
        return [toon for toon in self.getToons() if toon.getHp() > 0]
    
    def getAliveSuits(self, suits: list=None) -> List[ClashSuitBaseAI]:
        """Returns a list of all alive suits.
        """
        suits = suits if isinstance(suits, list) else self.suits
        return [suit for suit in suits if suit.getHp() > 0]
    
    def getAliveParticipants(self) -> List[BattleAvatar]:
        """Returns a list of all alive toons and suits.
        """
        return self.getAliveToons() + self.getAliveSuits()
    
    def getOtherSuits(self) -> List[ClashSuitBaseAI]:
        """Returns a list of alive suits which are not this
        attack's invoker.
        """
        return self.getAliveSuits([suit for suit in self.suits if suit != self.invoker])
    
    """
    Static methods
    """

    @staticmethod
    def clearAvatarStatusEffects(av: BattleAvatar) -> None:
        # Prevent fail fast iteration and other wonky stuff
        av.clearStatusEffects()

    @staticmethod
    def getObjectsFromIds(doIdList: list):
        retlist = []
        for doId in doIdList:
            do = simbase.air.doId2do.get(doId)
            if do:
                retlist.append(do)
        return retlist
    
    @staticmethod
    def getSuitLureResistance(suit: ClashSuitBaseAI, baseRounds: int) -> int:
        newRounds = baseRounds
        lureResistEffects = suit.getStatusEffectsOfType(StatusEffects.LureResistanceStatusEffect)
        for effect in lureResistEffects:
            newRounds = effect.handleLureResistance(suit, newRounds)

        return newRounds
    
    @staticmethod
    def addDamageMultToSuit(suit: ClashSuitBaseAI, setMultiplier=None, damageCap=None):
        if setMultiplier == 1.0:
            # why bother
            return
        newEffect = SEG.createStatusEffect(suit, SEE.EFFECT_SUIT_DAMAGE_BOOST)
        if setMultiplier:
            newEffect.setMultiplier(setMultiplier)
        suit.addStatusEffect(SEE.EFFECT_SUIT_DAMAGE_BOOST, newEffect)

        # See if we have a set damage cap.
        if suit.dna.name == 'count':
            damageCap = 7.77  # nice

        # Try capping the damage multiplier, if that's defined.
        if damageCap is not None:
            damageEffect = suit.getStatusEffectsOfId(SEE.EFFECT_SUIT_DAMAGE_BOOST)
            if damageEffect and type(damageEffect) is list and \
                len(damageEffect) and damageEffect[0].getMultiplier() > damageCap:
                currentMult = damageEffect[0].getMultiplier()
                damageEffect[0].setMultiplier(damageCap)
                return damageCap / currentMult  # the damage increase ratio

    @staticmethod
    def unlureSuit(suit: ClashSuitBaseAI, instant: bool=False) -> None:
        """Unlures a suit given it is actually lured and it hasn't been already unlured.
        """
        lureEffect = suit.getStatusEffectOfType(StatusEffects.LureStatusEffect)

        if lureEffect:
            if instant:
                lureEffect.delete()
            else:
                lureEffect.setUsed(1)
    
    @staticmethod
    def healSuit(suit: ClashSuitBaseAI, amount: int, additive: int=0, 
                 healthCap: float=1.0) -> int:
        """
        This function is used to heal a suit in battle.
        - Amount can be either a float multiplication or additive. (i.e. 0.75 vs 500)
        - This is determined via the additive flag.
        - healthCap determines the max HP Cap (as a multiple of their current health). (i.e. 1.5)
        """
        if suit.getHp() <= 0:
            return amount

        currentHP = suit.getHp()
        maxHp = suit.getMaxHp()

        healHP = amount if additive else math.ceil(maxHp * amount)
        allowOverheal = 1 if healthCap > 1.0 else 0

        adjustedHP = math.ceil(maxHp * healthCap)
        if currentHP + healHP >= adjustedHP:
            healHP = adjustedHP - currentHP

        suit.healSuit(healHP, allowOverheal)
        
        return healHP
    
    @staticmethod
    def getSuitHealAmount(suit: ClashSuitBaseAI, amount: float, healthCap: float) -> int:
        if suit.getHp() <= 0 or healthCap <= suit.getHealthPercentage():
            return 0

        currentHP = suit.getHp()
        maxHp = suit.getMaxHp()

        healHP = math.ceil(maxHp * amount)

        if currentHP + healHP >= maxHp * healthCap:
            healHP = maxHp * healthCap - currentHP

        return healHP
    
    @staticmethod
    def isSuit(avatar: BattleAvatar) -> bool:
        return isinstance(avatar, ClashSuitBaseAI)
    
    @staticmethod
    def isToon(avatar: BattleAvatar) -> bool:
        return isinstance(avatar, ClashDistributedToonBaseAI)
    
    """
    Taunt functions
    """
    
    def getTauntPool(self):
        return getTauntPool(self.invoker, self.attackType, self.rounds, self.tauntIndex)

    def setAttackTauntIndex(self):
        # Only set the taunt if enabled.
        if self.WANT_TAUNT:
            # Grab our proper taunt pool.
            taunts = self.getTauntPool()
            if taunts:
                self.taunt = [random.choice(list(range(len(taunts)))), self.tauntIndex]
                return

        self.taunt = [0, self.tauntIndex]
    
    """
    Static methods
    """
    
    @staticmethod
    def roundDamageValue(damage: int) -> int:
        return round(damage)
