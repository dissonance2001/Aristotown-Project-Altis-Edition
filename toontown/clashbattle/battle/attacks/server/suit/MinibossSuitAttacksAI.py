import random

from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.BattleAvatar import BattleAvatar
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.attacks.server.AttackAI import AttackAI
from toontown.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.battle.attacks.server.suit.BasicAttacksAI import (
    ApplyStatusEffectAttackAI, 
    ApplyStatusEffectToSelfAttackAI, 
    DamageInflictStatusAttackAI, 
    GenericDamageAttackAI, 
    SuitHealAttackAI, 
    SuitUnlureAttackAI
)
from toontown.battle.statuses.StatusEffectEnums import SEE
from toontown.battle.statuses import StatusEffectGlobals as SEG
from toontown.battle.statuses.StatusEffects import FlagEmpower, UnitesDisabledStatusEffect


@AttackClassAI(attackType=AttackEnum.DISRUPTIVE_ADVERTISEMENT)
class DisruptiveAdvertisementAI(ApplyStatusEffectToSelfAttackAI):
    STATUS_EFFECT = SEE.EFFECT_DISRUPTIVE_ADVERTISEMENT

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        effect = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        # This happens after its normal decrement event has been called, so we start with 1 actual round
        # going into the next.
        effect.setRounds(1, adjust=False)
        target.addStatusEffect(self.STATUS_EFFECT, effect)


@AttackClassAI(attackType=AttackEnum.EXTRA_TIP)
class ExtraTipAI(SuitHealAttackAI, SuitUnlureAttackAI):
    """
    This is the attack object used for Extra Tip.
    This is used by the Club President to unlure his autocaddies.
    """
    REQUIRED_TARGETS = 1

    def calculate(self) -> None:
        SuitHealAttackAI.calculate(self)
        SuitUnlureAttackAI.calculate(self)
    
    def setTargetList(self) -> None:
        autocaddies = self.battle.battleCalc.allSuitsExceptMe(exceptSuit=self.invoker)
        choiceList = [
            autocaddie for autocaddie in autocaddies
            if autocaddie.getStatusEffectOfId(SEE.EFFECT_SUIT_LURED) and autocaddie.getHp() > 0
        ]
        if choiceList:
            self.targets = [random.choice(choiceList)]


@AttackClassAI(attackType=AttackEnum.INK_DRAIN)
class InkDrainAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_INK_DRAIN

    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=AttackEnum.INK_DRAIN_DIRECTORS)
class InkDrainDirectorsAI(InkDrainAI):
    def handleStatusEffect(self, target, extraArgs=None):
        super().handleStatusEffect(target, extraArgs=[0.6])


@AttackClassAI(attackType=AttackEnum.LIFE_INSURANCE)
class LifeInsuranceAI(DamageInflictStatusAttackAI):
    """
    This is the attack object used for Life Insurance.
    This is used by the supervisor at the beginning of the first round.
    """
    STATUS_EFFECT = SEE.EFFECT_SUIT_ADDITIVE_DAMAGE_BOOST

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        damageBoostAmount = 5
        self.extraArgs = [damageBoostAmount]
        return super().handleStatusEffect(target, [damageBoostAmount])

    def getDamage(self, target: BattleAvatar = None) -> int:
        return -1.0

    def setTargetList(self) -> None:
        self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.MULTI_LEVEL_MARKETING)
class MultiLevelMarketingAI(ApplyStatusEffectToSelfAttackAI):
    STATUS_EFFECT = SEE.EFFECT_MULTI_LEVEL_MARKETING


@AttackClassAI(attackType=AttackEnum.OBJECTION_SUSTAINED)
class ObjectionSustainedAI(GenericDamageAttackAI):
    """
    This is the attack object used for Head Attorney.
    This is used when his attack is granted and he heals.
    """
    HEAL_ADDITIVE = True

    def calculate(self, ignoreModifiers: bool = False) -> None:
        return super().calculate(ignoreModifiers=True)

    def getDamage(self, target: BattleAvatar = None) -> int:
        if target == self.invoker:
            return self.extraArgs[0]
        return -int(self.extraArgs[0] / 3)

    def setTargetList(self) -> None:
        self.targets = [self.invoker, *self.getToons()]


@AttackClassAI(attackType=AttackEnum.OVERWHELMING_AUTHORITY)
class OverwhelmingAuthorityAI(ApplyStatusEffectAttackAI):
    STATUS_EFFECT = SEE.EFFECT_OVERWHELMING_AUTHORITY

    def __init__(self, *args, **kwargs) -> None:
        # Choose a random manager to taunt the toons.
        super().__init__(*args, tauntIndex=random.randint(0, 2), **kwargs)

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        # Remove all current unite disabled status effects from the toons.
        unitesDisabled = target.getStatusEffectsOfType(UnitesDisabledStatusEffect)
        if unitesDisabled:
            for effect in unitesDisabled:
                effect.delete()

        # Add overwhelming authority status effect to all toons (permanent unites disabled)
        return super().handleStatusEffect(target, extraArgs)
    
    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=AttackEnum.REFINEMENT)
class RefinementAI(DamageInflictStatusAttackAI):
    """
    This is the attack object for Refinement.
    Mr. Derrickman uses this.
    """
    STATUS_EFFECT = SEE.EFFECT_CANT_ATTACK
    HEAL_ADDITIVE = False
    HEAL_CAP = 1.1

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list=None) -> None:
        if target is not self.invoker:
            return

        super().handleStatusEffect(target=target, extraArgs=extraArgs)

    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return -0.4 # negative indicates a heal


@AttackClassAI(attackType=AttackEnum.REFINEMENT_DIRECTORS)
class RefinementDirectorsAI(GenericDamageAttackAI):
    """
    This is the attack object for Refinement Director's version.
    Mr. Derrickhand uses this.
    """
    HEAL_ADDITIVE = True
    HEAL_CAP = 1.25

    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()

    def getDamage(self, target: BattleAvatar = None) -> int:
        return -275 # negative indicates a heal


@AttackClassAI(attackType=AttackEnum.WORKERS_COMP)
class WorkersCompAI(AttackAI):
    REQUIRED_TARGETS = 1
    HEAL_ADDITIVE = True
    
    def calculate(self) -> None:
        suitsKilled, intent = self.getSuitKills()

        # Set base values for attack.
        healAmount = 65
        damageMult = 1.15
        self.HEAL_CAP = 1.25

        # If the "empower" flag is on ourselves, then this attack will be upgraded.
        if self.invoker.getStatusEffectOfType(FlagEmpower):
            healAmount = 160
            damageMult = 1.28
            self.HEAL_CAP = 3

            # If this is Compensation: Compensation, nerf the heal amount.
            if intent == 2:
                healAmount = 80

            # If this is Compensation: Rebalance, nerf the heal amount.
            if intent == 3:
                healAmount = 7

        # Multislacker general foreman compensation
        if intent == 9:
            self.HEAL_CAP = 2.0
            healAmount = 100
        # Multislacker union bust compensation
        if intent == 10:
            self.HEAL_CAP = 2.0
            healAmount = 200
            damageMult = 1.15
        # FTF Foreman general compensation
        if intent == 11:
            self.HEAL_CAP = 10.0
            healAmount = 225
            damageMult = 1.2

        result = self.createAttackTarget(self.invoker.doId)

        for _ in range(suitsKilled):
            result.hpAdjust += healAmount
            # Add a status effect to the foreman with a damage boost.
            effect = SEG.createStatusEffect(self.invoker, SEE.EFFECT_SUIT_DAMAGE_BOOST)
            effect.setMultiplier(damageMult)
            self.invoker.addStatusEffect(SEE.EFFECT_SUIT_DAMAGE_BOOST, effect)

        # Put the actual useful information at the front.
        self.extraArgs = [suitsKilled, damageMult * 100] + self.extraArgs
    
    def getSuitKills(self):
        suitsKilled = self.eventsSentThisRound(BEG.EVENT_SUIT_DIED)

        # If this attack was passed with arguments, up the suits killed by the arguments passed in.
        intent = None
        if self.extraArgs:
            # Add an additional amount of kills now.
            extraKills, *extra = self.extraArgs
            if extraKills != -1:
                suitsKilled = extraKills

            # Check for intent.
            if extra:
                intent, *_ = extra
        
        return suitsKilled, intent
    
    def setTargetList(self) -> None:
        if self.getSuitKills()[0]:
            self.targets = [self.invoker]


@AttackClassAI(attackType=AttackEnum.LIGHTS_ON)
class LightsOnInitiativeAI(AttackAI):
    '''
    This is the cheat Desk Jockey uses to summon more dummies during the toontorial.
    '''
    def calculate(self) -> None:
        from toontown.instances.battle.mercs.DistributedBattlePrethinkerAI import DistributedBattlePrethinkerAI
        from toontown.toontorial.DistributedTutorialBattleAI import DistributedTutorialBattleAI
        if isinstance(self.invoker.battle, DistributedBattlePrethinkerAI):
            # Prethinker Functionality
            self.invoker.battle.instance.generateReserveSuits(count=self.extraArgs[0], overflow=self.extraArgs[1])
        elif isinstance(self.invoker.battle, DistributedTutorialBattleAI):
            # Toontorial Functionality
            self.invoker.battle.summonDummies(amount=self.extraArgs[0], level=self.extraArgs[1])

    def setTargetList(self) -> None:
        self.targets = [self.invoker]
