"""Contains various types of attack classes which to inherit functionality from."""
from abc import ABC

from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.BattleAvatar import BattleAvatar
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.server.AttackAI import AttackAI
from toontown.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.battle.statuses import StatusEffectGlobals as SEG
from toontown.battle.statuses.StatusEffectEnums import SEE
from toontown.toon.DistributedToonBaseAI import DistributedToonBaseAI


"""
Exceptions
"""


class StatusEffectNotDefinedError(Exception):
    pass


class VisualEffectNotDefinedError(Exception):
    pass


"""
Basic attack classes
"""


class ApplyStatusEffectAttackAI(AttackAI):
    """This attack's sole purpose is to inflict a status effect
    to its targets.
    """

    def calculate(self) -> None:
        # We should always have a status effect defined.
        if not self.STATUS_EFFECT:
            raise StatusEffectNotDefinedError(
                f"{self.__class__.__name__}, which subclasses ApplyStatusEffectAttackAI, "\
                "has no status effect defined!")
        
        # Apply the status effect to each target.
        for target in self.targets:
            result = self.createAttackTarget(target.doId)

            if self.getLanded():
                result.landed = True
                self.handleStatusEffect(target)
    
    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list=None) -> None:
        extraArgs = extraArgs or []

        statuses = self.STATUS_EFFECT
        if not isinstance(statuses, (list, tuple)):
            statuses = [statuses]

        for status in statuses:
            target.addStatusEffect(status, extraArgs=extraArgs)

    def getLanded(self) -> bool:
        return True


class RemoveStatusEffectAttackAI(ApplyStatusEffectAttackAI):
    """This attack's sole purpose is to remove a status effect
    from its targets.
    """

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list=None) -> None:
        statuses = self.STATUS_EFFECT
        if not isinstance(statuses, (list, tuple)):
            statuses = [statuses]

        for status in statuses:
            if status == SEE.EFFECT_SUIT_LURED:
                self.unlureSuit(target, instant=True)
                continue
            target.removeStatusEffectOfId(status)


class ApplyVisualEffectAttackAI(AttackAI):
    """This attack's sole purpose is to inflict a visual effect
    to its targets.
    """

    def calculate(self) -> None:
        # Replace visual effect enum with extra args list if we have it
        if self.extraArgs:
            self.VISUAL_EFFECT = self.extraArgs[:]
        # We should always have a status effect defined.
        if not self.VISUAL_EFFECT:
            raise VisualEffectNotDefinedError(
                f"{self.__class__.__name__}, which subclasses ApplyVisualEffectAttackAI, "\
                "has no visual effect defined!")
        
        # Apply the status effect to each target.
        for target in self.targets:
            result = self.createAttackTarget(target.doId)

            if self.getLanded():
                result.landed = True
                self.handleVisualEffect(target)
    
    def handleVisualEffect(self, target: BattleAvatar, extraArgs: list=None) -> None:
        extraArgs = extraArgs or []

        visuals = self.VISUAL_EFFECT
        if not isinstance(visuals, (list, tuple)):
            visuals = [visuals]

        for visual in visuals:
            target.addVisualEffect(visual, extraArgs=extraArgs)

    def getLanded(self) -> bool:
        return True


@AttackClassAI(attackType=AttackEnum.REMOVE_VISUAL_EFFECT)
class RemoveVisualEffectAttackAI(ApplyVisualEffectAttackAI):
    """This attack's sole purpose is to remove a visual effect
    from its targets.
    """

    def handleVisualEffect(self, target: BattleAvatar, extraArgs: list=None) -> None:
        visuals = self.VISUAL_EFFECT
        if not isinstance(visuals, (list, tuple)):
            visuals = [visuals]

        for visual in visuals:
            result = target.removeVisualEffectOfId(visual)
            if not result:
                self.notify.debug(f"Could not remove {visual} effect from {repr(target)}!")


class ApplyStatusEffectToSelfAttackAI(ApplyStatusEffectAttackAI):
    """Effectively the same as ApplyStatusEffectAttackAI, except the only
    target is the invoker itself.
    """

    def setTargetList(self) -> None:
        self.targets = [self.invoker]


class RemoveStatusEffectFromSelfAttackAI(RemoveStatusEffectAttackAI):
    """Effectively the same as RemoveStatusEffectAttackAI, except the only
    target is the invoker itself.
    """

    def setTargetList(self) -> None:
        self.targets = [self.invoker]


class ApplyVisualEffectToSelfAttackAI(ApplyVisualEffectAttackAI):
    """Effectively the same as ApplyVisualEffectAttackAI, except the only
    target is the invoker itself.
    """

    def setTargetList(self) -> None:
        self.targets = [self.invoker]


class RemoveVisualEffectFromSelfAttackAI(RemoveVisualEffectAttackAI):
    """Effectively the same as RemoveVisualEffectAttackAI, except the only
    target is the invoker itself.
    """

    def setTargetList(self) -> None:
        self.targets = [self.invoker]


class GenericDamageAttackAI(AttackAI):
    """A generic attack which deals damage to all of
    its specified targets.

    NOTE: "damage" is just a way to reference a change
    in HP; this change can be either positive or negative.
    """
    WANT_TAUNT = False

    def calculate(self, ignoreModifiers: bool = False) -> None:
        for target in self.targets:
            attackHit = self.getLanded()
            result = self.getDamage(target)
            if not ignoreModifiers:
                # Apply any damage modifiers here.
                result = self.applyDamageModifiers(target, result)

            attackTarget = self.createAttackTarget(target.doId)

            if attackHit:
                attackTarget.landed = attackHit
                attackTarget.hpAdjust = -result
                # This is a heal on a toon, we need to cap it
                if isinstance(target, DistributedToonBaseAI) and attackTarget.hpAdjust > 0:
                    hpDelta = target.getMaxHp() - target.getHp()
                    attackTarget.hpAdjust = min(hpDelta, attackTarget.hpAdjust)
    
    def getLanded(self) -> bool:
        return True


class DamageInflictStatusAttackAI(GenericDamageAttackAI, ApplyStatusEffectAttackAI):
    """A generic attack, except a status will be inflicted on targets
    which the attack successfully hits.
    """
    
    def calculate(self, ignoreModifiers: bool = False) -> None:
        for target in self.targets:
            attackHit = self.getLanded()
            result = self.getDamage(target)
            if not ignoreModifiers:
                # Apply any damage modifiers here.
                result = self.applyDamageModifiers(target, result)

            attackTarget = self.createAttackTarget(target.doId)

            if attackHit:
                self.handleStatusEffect(target)

                attackTarget.landed = attackHit
                attackTarget.hpAdjust = -result


class DamageRemoveStatusAttackAI(GenericDamageAttackAI, RemoveStatusEffectAttackAI):
    """A generic attack, except a status will be removed from targets
    which the attack successfully hits.
    """

    def calculate(self, ignoreModifiers: bool = False) -> None:
        for target in self.targets:
            attackHit = self.getLanded()
            result = self.getDamage(target)
            if not ignoreModifiers:
                # Apply any damage modifiers here.
                result = self.applyDamageModifiers(target, result)

            attackTarget = self.createAttackTarget(target.doId)

            if attackHit:
                self.handleStatusEffect(target)

                attackTarget.landed = attackHit
                attackTarget.hpAdjust = -result


class HitAllParticipantsAttackAI(GenericDamageAttackAI):

    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits() + self.getToons()


class CreateAttackAttackAI(AttackAI):
    """Creates a number of new random attacks for each
    attack target.
    """
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'amount',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )
    
    ATTACK_ARGS = {}
    INSERTION_ARGS = {}  # index=None, respectPreviousAdditions=False, adjust=True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.amount = 1

    def calculate(self) -> None:
        for target in self.targets:
            self.createAttackTarget(target.doId)
            for i in range(self.amount):
                attackArgs = {"invoker": target, "unlure": True}
                attackArgs.update(self.getAttackArgs(i))

                self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                    self.getNewAttackEnum(target), attackArgs,
                    self.INSERTION_ARGS.copy()
                ])
    
    def getAttackArgs(self, index: int) -> dict:
        return self.ATTACK_ARGS.copy()
    
    def getNewAttackEnum(self, target: BattleAvatar) -> AttackEnum:
        return target.getRandomAttack()


@AttackClassAI(attackType=AttackEnum.SUIT_HEAL)
class SuitHealAttackAI(GenericDamageAttackAI):
    """Mirrors the functionality of the old style SuitHealAttackAI
    in regards to the use of extraArgs.
    """

    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'amount',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.amount = self.extraArgs[0]
        self.HEAL_ADDITIVE = self.extraArgs[1]
        self.HEAL_CAP = self.extraArgs[2]
    
    def getDamage(self, target: BattleAvatar=None) -> int:
        return -self.amount


@AttackClassAI(attackType=AttackEnum.SUIT_LURE)
class SuitLureAttackAI(ApplyStatusEffectAttackAI):
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'lureRounds'
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    STATUS_EFFECT = SEE.EFFECT_SUIT_LURED

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.lureRounds = self.extraArgs[0]
    
    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        if target.getStatusEffectOfId(self.STATUS_EFFECT):
            return

        newLureEffect = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        newLureEffect.setRounds(self.lureRounds, adjust=False)
        lureEffect, combined = target.addStatusEffect(SEE.EFFECT_SUIT_LURED, newLureEffect)
        lureEffect.setUniqueId(self.rounds)
        lureEffect.setFresh(False)
        self.sendEvent(BEG.EVENT_LURED_SUIT, [target, None, self.lureRounds, None, self.attackIndex, -1])


@AttackClassAI(attackType=AttackEnum.SUIT_UNLURE)
class SuitUnlureAttackAI(RemoveStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_SUIT_LURED
    
    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        self.unlureSuit(target, instant=True)


@AttackClassAI(attackType=(
    AttackEnum.SUIT_DAMAGE, AttackEnum.TOON_DAMAGE, AttackEnum.HYDRATION_COMEBACK,
    AttackEnum.SUIT_MARKED_DAMAGE, AttackEnum.COURT_RECORD_DAMAGE, AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE,
    AttackEnum.LEGAL_BINDINGS_DAMAGE, AttackEnum.WOODCHIPPER_DAMAGE,
    AttackEnum.DEEP_DIVER_DIVING_DOT, AttackEnum.OIL_RAIN_DOT, AttackEnum.SPARK_PLUG_DAMAGE,
    AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE_INSTANT, AttackEnum.HIGHROLLER_LEVEL_DAMAGE, AttackEnum.RED_THREAD_DAMAGE,
    AttackEnum.HEARTBROKEN
))
class DamageAttackAI(GenericDamageAttackAI):
    """Damage any toon or suit."""

    def getDamage(self, target: BattleAvatar = None) -> int:
        return -self.extraArgs[0]


@AttackClassAI(attackType=AttackEnum.DAMAGE_ABSORB_SUIT_DAMAGE_WITH_UNLURE)
class DamageUnlureAttackAI(DamageAttackAI):
    """Damages and unlures a suit."""

    def calculate(self, ignoreModifiers: bool = False) -> None:
        super().calculate(ignoreModifiers=ignoreModifiers)

        if self.getLanded():
            for target in self.targets:
                target.deleteStatusEffectOfId(SEE.EFFECT_SUIT_LURED)


@AttackClassAI(attackType=(AttackEnum.AVATAR_INSTAKILL, AttackEnum.COGS_FLY_AWAY))
class InstakillAttackAI(GenericDamageAttackAI):
    """Kill all avatars that are passed in."""

    def calculate(self, ignoreModifiers: bool = True) -> None:
        super().calculate(ignoreModifiers=True)

    def getDamage(self, target: BattleAvatar = None):
        # Prevent any unite struggling.
        if target.isToon():
            return 9999
        return target.hp


@AttackClassAI(attackType=(
    AttackEnum.SHOW_HP_TEXT, AttackEnum.SHOW_PIP_TEXT, AttackEnum.WASTEFUL_MGMT,
    AttackEnum.OBJECTION, AttackEnum.OBJECTION_OVERRULED,
    AttackEnum.FORWARD_THINKING, AttackEnum.REVVING_UP,
    AttackEnum.PCRAT_INVESTOR_DEATH_PHRASE,
    AttackEnum.GHOST_PAYROLL_HEAL, AttackEnum.INSOMNIA,
    AttackEnum.SPENDING_REV, AttackEnum.HYPER_TASK,
    AttackEnum.STAR_OF_THE_SHOW_END, AttackEnum.PACESETTER_CHALLENGE,
    AttackEnum.PACESETTER_CHALLENGE_CANCELLED, AttackEnum.AVATAR_SAY_PHRASE,
    AttackEnum.AVATAR_SAY_PHRASE_ON_TARGET, AttackEnum.SUITS_ADJUST_POSITION,
    AttackEnum.FTF_ATTORNEY_COURT_MANDATE_OMNIPOTENT, AttackEnum.FTF_ATTORNEY_COURT_MANDATE_MONOLITH,
    AttackEnum.HR_TOON_LAFF_UP, AttackEnum.APPLY_VISUAL_EFFECT_MOVIE, AttackEnum.GUEST_VERSE_END,
    AttackEnum.STENOG_CALCULATING_COSTS,
))
class DoNothingAI(AttackAI):
    """For all of your doing nothing needs."""
    
    def calculate(self) -> None:
        # Send all of the targets to the client.
        # (this list can be empty if no targets were provided)
        [self.createAttackTarget(target.doId) for target in self.targets]

    def setTargetList(self) -> None:
        pass


class EndBattleAttackAI(DamageInflictStatusAttackAI):
    """Upon calculating this attack, the battle calculator will immediately
    stop the round and force the battle to end. This attack also inflicts
    a 'dead' effect to the Toons, forcing them out of the battle.
    """
    STATUS_EFFECT = SEE.EFFECT_DEAD

    def setTargetList(self) -> None:
        self.targets = self.getToons()


class SuitUnlureCreateAttackAttackAI(SuitUnlureAttackAI, CreateAttackAttackAI):

    def calculate(self) -> None:
        SuitUnlureAttackAI.calculate(self)
        CreateAttackAttackAI.calculate(self)
