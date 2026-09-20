from operator import itemgetter
import random
from typing import Dict

from toontown.clashbattle.battle.BattleEventGlobals import BEG
from toontown.clashbattle.battle.BattleAvatar import BattleAvatar
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.attacks.server.AttackAI import AttackAI
from toontown.clashbattle.battle.attacks.server.AttackRepositoryAI import AttackClassAI
from toontown.clashbattle.battle.attacks.server.suit.BasicAttacksAI import ApplyStatusEffectAttackAI, \
    ApplyVisualEffectToSelfAttackAI, DamageInflictStatusAttackAI, RemoveVisualEffectFromSelfAttackAI
from toontown.clashbattle.battle.attacks.server.suit.SuitGroupAttackAI import SuitGroupAttackAI
from toontown.clashbattle.battle.attacks.server.suit.SuitSingleAttackAI import SuitSingleAttackAI
from toontown.clashbattle.battle.statuses import StatusEffectGlobals as SEG
from toontown.clashbattle.battle.statuses.StatusEffectEnums import SEE, SUIT_STATUS_EFFECTS_TO_REMOVE
from toontown.clashbattle.battle.statuses.StatusEffects import LureStatusEffect, UseGagLevelSenderStatusEffect
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashsuit.suit.ClashSuitBaseAI import ClashSuitBaseAI
from toontown.toon.ClashDistributedToonBaseAI import ClashDistributedToonBaseAI


@AttackClassAI(attackType=AttackEnum.BAYOU_BASH)
class BayouBashAI(AttackAI):
    """
    Used for Litigator's Bayou Bash attack.
    Summons more cogs.

    This attack also has the opportunity to become bayou bellow if bayou bash has already either happened,
    or the battle does not have space for more cogs.
    """
    def calculate(self) -> None:
        # Try to add the bayou bash attack.

        # In the following circumstances, add the bayou bellow attack instead:
        # There are already 6 cogs in the battle, or:
        # Bayou bash has already been used this turn.
        if len(self.targets) >= 6 or self.hasEventBeenSent(BEG.EVENT_LT_LGATOR_BAYOU_BASH):
            luredSuits = []
            for suit in self.targets:
                suit: ClashSuitBaseAI
                for effectType in SUIT_STATUS_EFFECTS_TO_REMOVE:
                    effectsOfType = suit.getStatusEffectsOfId(effectType)
                    for effect in effectsOfType:
                        if effectType == SEE.EFFECT_SUIT_LURED and suit not in luredSuits:
                            luredSuits.append(suit)
                        effect.delete()

            # Add a new suit attack for every suit that was lured before.
            for suit in luredSuits:
                self.sendEvent(BEG.EVENT_CREATE_INSERT_ATTACK, [
                    suit.getRandomAttack(), {"invoker": suit, "unlure": True},
                    {"respectPreviousAdditions": True}
                ])

            # Let our status effect manager know that this attack has happened.
            self.sendEvent(BEG.EVENT_LT_LGATOR_BAYOU_BELLOW)
            self.attackType = AttackEnum.BAYOU_BELLOW
        # Just do normal ol' bayou bash.
        else:
            # Spawn some new suits to fill up the battle
            # Increase cap to 5 or 6 depending on how many times summoned cogs already.
            managerEffect = self.invoker.getStatusEffectOfId(SEE.EFFECT_LITIGATOR_MANAGER)
            timesSummoned = managerEffect.getTimesSummoned()
            if timesSummoned > 1:
                self.invoker.battle.maxSuits = 6
            elif timesSummoned > 0:
                self.invoker.battle.maxSuits = 5
            else:
                self.invoker.battle.maxSuits = 4

            suitsToGen = self.invoker.battle.maxSuits - len(self.targets)
            for _ in range(suitsToGen):
                managerEffect.addCogToBattle()

            # Let our status effect manager know that this attack has happened.
            managerEffect.increaseTimesSummoned()
            self.sendEvent(BEG.EVENT_LT_LGATOR_BAYOU_BASH)
    
    def setTargetList(self) -> None:
        self.targets = self.getAliveSuits()


@AttackClassAI(attackType=AttackEnum.COURT_COSTS)
class CourtCostsAI(SuitGroupAttackAI):
    """
    This is the attack object for Court Costs.
    Stenographer uses this to deal damage every 3 rounds, and the damage increases by 2 every time its used.
    """

    def getDamage(self, target: BattleAvatar = None) -> int:
        return self.extraArgs[0]


@AttackClassAI(attackType=AttackEnum.COURT_RECORD)
class CourtRecordAI(AttackAI):
    """
    This is the attack object for Court Record.
    Stenographer uses this to disable a level of gag for the next turn.
    If they use that level of gag, they take damage as a punishment
    """

    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'gagLevel', 'gagLevel2',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.gagLevel = self.extraArgs[0]
        self.gagLevel2 = self.extraArgs[1]
    
    def calculate(self) -> None:
        # If the toon already has a gag level status effect, set the level on that.
        # Else, make a new status effect and give it to them.
        for toon in self.targets:
            gagEffects = toon.getStatusEffectsOfType(UseGagLevelSenderStatusEffect)
            if gagEffects:
                gagEffects[0].setGagLevel(self.gagLevel)
                gagEffects[0].setGagLevel2(self.gagLevel2)
            else:
                # Create a new court record effect with the given gag level and
                newGagEffect = SEG.createStatusEffect(toon, SEE.EFFECT_COURT_RECORD)
                newGagEffect.setGagLevel(self.gagLevel)
                newGagEffect.setGagLevel2(self.gagLevel2)
                toon.addStatusEffect(SEE.EFFECT_COURT_RECORD, newGagEffect)

        self.sendEvent(BEG.EVENT_LT_STENOG_USE_COURT_RECORD)
    
    def setTargetList(self) -> None:
        self.targets = self.getToons()


@AttackClassAI(attackType=(AttackEnum.COURT_SANCTION, AttackEnum.COURT_SANCTION_RETALIATE))
class CourtSanctionAI(DamageInflictStatusAttackAI):
    """
    This is the attack object for Court Sanction.
    Stenographer uses this to deal damage to a toon and apply a gag effectiveness down status effect to them.
    """
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'toonsDamageDealt', 'sanctionMult', 'weakened',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    REQUIRED_TARGETS = 1
    STATUS_EFFECT = SEE.EFFECT_SANCTIONED

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toonsDamageDealt: Dict[ClashDistributedToonBaseAI, int] = self.extraArgs[0]
        self.sanctionMult = self.extraArgs[1]
        self.weakened = self.extraArgs[2]
        self.extraArgs = self.extraArgs[1:]
    
    def cleanup(self) -> None:
        del self.toonsDamageDealt
        super().cleanup()

    def calculate(self) -> None:
        super().calculate()

        # Send event if a normal court sanction was used
        if not self.weakened:
            self.sendEvent(BEG.EVENT_LT_STENOG_NORMAL_SANCTION)
    
    def setTargetList(self) -> None:
        # A predefined target was given.
        if self.targets:
            return

        # Grab the toon that has dealt the least damage.
        # Keep in mind that the damage numbers are negative.
        self.toonsDamageDealt = {
            toon: dmg for toon, dmg in self.toonsDamageDealt.items() if toon.getHp() > 0 and toon.doId in self.battle.activeToons
        } if self.toonsDamageDealt else {}

        if self.toonsDamageDealt:
            self.targets = [sorted(self.toonsDamageDealt.items(), key=itemgetter(1), reverse=True)[0][0]]
        else:
            # Grab a random toon
            aliveToons = self.getAliveToons()
            if aliveToons:
                self.targets = [random.choice(aliveToons)]

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        sanctionEffect = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        sanctionEffect.setMultiplier(self.sanctionMult)
        target.addStatusEffect(self.STATUS_EFFECT, sanctionEffect)
        target.addVisualEffect(VisualEffectEnum.GAG_DOWN)
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return self.invoker.getAttackDamage(self.attackType)


@AttackClassAI(attackType=AttackEnum.INSURANCE_PLAN)
class InsurancePlanAI(ApplyStatusEffectAttackAI):
    REQUIRED_TARGETS = 1
    STATUS_EFFECT = SEE.EFFECT_CASE_MANAGER_HOT

    def setTargetList(self) -> None:
        # Only add insurance plan attack if there are hurt suits in the battle that aren't our suit.
        aliveSuits = self.getOtherSuits()
        self.targets = [self.invoker]

        # Find all IDs of suits without Insurance
        suitsWithoutEffect = []
        for suit in aliveSuits:
            if not suit.getStatusEffectsOfId(SEE.EFFECT_CASE_MANAGER_HOT):
                suitsWithoutEffect.append(suit)

        # Find all IDs of lured suits without insurance that would benefit from the lure resistance
        luredSuitsWithoutEffect = []
        for suit in aliveSuits:
            if suit not in suitsWithoutEffect:
                continue
            luredEffect = suit.getStatusEffectOfType(LureStatusEffect)
            if luredEffect and luredEffect.getRounds() > 1:
                luredSuitsWithoutEffect.append(suit)

        # Find all IDs of hurt suits without insurance
        hurtSuitsWithoutEffect = [
            suit for suit in aliveSuits
            if suit.getMaxHp() > suit.getHp() and suit in suitsWithoutEffect
        ]

        def cleanList(listOfSuits):
            return [s for s in listOfSuits if s not in self.targets]

        for _ in range(2):
            if suitsWithoutEffect:
                # Pick a suit without Insurance
                # Prioritizes Lured Suits, then Hurt Suits, then any Suit without the effect.
                # If there's no suits without the effect, just target a random suit!!
                listToUse = cleanList(luredSuitsWithoutEffect) or cleanList(hurtSuitsWithoutEffect) or \
                            cleanList(suitsWithoutEffect) or cleanList(aliveSuits)
                if listToUse:
                    self.targets.append(random.choice(listToUse))

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        # Give Case Manager 1 stack of Insurance, given that he is not the main target.
        if target is self.invoker and len(self.targets) > 1:
            # Create a new Insurance status effect and set its rounds to 1
            singleStackInsurance = SEG.createStatusEffect(target, self.STATUS_EFFECT)
            singleStackInsurance.setRounds(1)
            # Add it directly to the profile so it can combine as needed
            target.addStatusEffect(self.STATUS_EFFECT, singleStackInsurance)
        # Otherwise, target gets the standard amount of stacks.
        else:
            target.addStatusEffect(self.STATUS_EFFECT)

        # Add visual effect.
        target.addVisualEffect(VisualEffectEnum.INSURANCE)


@AttackClassAI(attackType=AttackEnum.LEGAL_BINDINGS)
class LegalBindingsAI(ApplyStatusEffectAttackAI):
    REQUIRED_TARGETS = 1
    STATUS_EFFECT = SEE.EFFECT_CASE_MANAGER_DOT

    def setTargetList(self) -> None:
        # Pick a random toon from the battle to apply damage over time.
        # Prefer to select toons who do not currently have the effect.
        # If everyone already has it, pick a random toon.
        aliveToons = self.getAliveToons()
        if not aliveToons:
            return

        toonsWithoutEffect = []
        for toon in aliveToons:
            if not toon.getStatusEffectsOfId(SEE.EFFECT_CASE_MANAGER_DOT):
                toonsWithoutEffect.append(toon)

        self.targets = [random.choice(toonsWithoutEffect if toonsWithoutEffect else aliveToons)]

    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        super().handleStatusEffect(target, extraArgs)
        target.addVisualEffect(VisualEffectEnum.LEGALLY_BOUND)


@AttackClassAI(attackType=AttackEnum.SCAPEGOAT_DEFENSE)
class ScapegoatDefenseAI(RemoveVisualEffectFromSelfAttackAI):
    VISUAL_EFFECT = VisualEffectEnum.SCAPEGOAT_ENRAGED


@AttackClassAI(attackType=AttackEnum.SCAPEGOAT_ENRAGED)
class ScapegoatEnragedAI(ApplyVisualEffectToSelfAttackAI):
    VISUAL_EFFECT = VisualEffectEnum.SCAPEGOAT_ENRAGED


@AttackClassAI(attackType=(AttackEnum.SNAP, AttackEnum.SNAP_RETALIATE, AttackEnum.FTF_PRESIDENT_SNAP))
class SnapAI(DamageInflictStatusAttackAI, SuitSingleAttackAI):
    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'toonsDamageDealt', 'vulnerableMult', 'weakened', 'damage',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    REQUIRED_TARGETS = 1
    STATUS_EFFECT = SEE.EFFECT_VULNERABLE

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.toonsDamageDealt: Dict[ClashDistributedToonBaseAI, int] = self.extraArgs[0]
        self.vulnerableMult = self.extraArgs[1]
        self.weakened = self.extraArgs[2]
        self.extraArgs = self.extraArgs[1:]
        self.damage = self.invoker.getAttackDamage(self.attackType)
    
    def cleanup(self) -> None:
        del self.toonsDamageDealt
        super().cleanup()
    
    def setTargetList(self) -> None:
        # A predefined target was given.
        if self.targets:
            return

        # Grab the toon that has dealt the most damage.
        # Keep in mind that the damage numbers are negative.
        self.toonsDamageDealt = {
            toon: dmg for toon, dmg in self.toonsDamageDealt.items() if toon.getHp() > 0 and toon.doId in self.battle.activeToons
        } if self.toonsDamageDealt else {}

        if self.toonsDamageDealt:
            self.targets = [sorted(self.toonsDamageDealt.items(), key=itemgetter(1))[0][0]]
        else:
            # Grab a random toon
            aliveToons = self.getAliveToons()
            if aliveToons:
                self.targets = [random.choice(aliveToons)]
    
    def handleStatusEffect(self, target: BattleAvatar, extraArgs: list = None) -> None:
        vulnEffect = SEG.createStatusEffect(target, self.STATUS_EFFECT)
        vulnEffect.setMultiplier(self.vulnerableMult)
        target.addStatusEffect(self.STATUS_EFFECT, vulnEffect)
    
    def getDamage(self, target: BattleAvatar = None) -> int:
        return SuitSingleAttackAI.getDamage(self, target)
