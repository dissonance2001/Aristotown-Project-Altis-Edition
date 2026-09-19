import random

from direct.showbase.PythonUtil import lerp

from toontown.ai.AIBaseGlobal import simbase
from toontown.battle.BattleAvatar import BattleAvatar
from toontown.battle.attacks.server.AttackAI import AttackAI
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.statuses import StatusEffects
from toontown.battle.statuses.StatusEffectEnums import StatusEffectEnum


class SuitSingleAttackAI(AttackAI):
    """SuitSingleAttackAI: Extends AttackAI with functionality
    for single target suit attacks.
    """

    __slots__ = (
        # General parameters
        'attackType', 'rounds', 'invoker', 'targets', 'unlure', 'damageMult', 'extraArgs',
        'attackIndex', 'results', 'battleListener', 'suits', 'toons', 'attackAmount',
        'inserted', 'priority', 'battle', 'damage', 'accuracy', 'tauntIndex',
        
        # Toon specific parameters
        'level', 'target',

        # Suit specific parameters
        'taunt',
    )

    REQUIRED_TARGETS = 1
    DAMAGE_RANGE = None  # Potential random damage range. i.e. (0.8, 1.2)

    def __init__(self, attackType: AttackEnum, rounds: int=0, 
                 invoker: BattleAvatar=None, targets: list=None, 
                 unlure: bool=False, damageMult: float=1.0, 
                 extraArgs: list=None, tauntIndex: int=0) -> None:
        super().__init__(attackType, rounds, invoker, targets, unlure, damageMult, extraArgs, tauntIndex)

        # The damage that this attack will deal.
        self.damage = self.invoker.getAttackDamage(attackType)

        # The accuracy of this attack.
        self.accuracy = self.invoker.getAttackAccuracy(attackType)

    def calculate(self) -> None:
        # Whether the attack hit is calculated for each target individually,
        # instead of calculating once for all targets.
        for toon in self.targets:
            attackHit = self.getLanded()

            result = self.getDamage(toon)
            # Apply any damage modifiers here.
            result = self.applyDamageModifiers(toon, result)
            # Apply a random damage range if we have one.
            if self.DAMAGE_RANGE:
                modifier = lerp(self.DAMAGE_RANGE[0], self.DAMAGE_RANGE[1], random.random())
                result = int(result * modifier)

            attackTarget = self.createAttackTarget(toon.doId)

            if attackHit:
                attackTarget.landed = attackHit
                attackTarget.hpAdjust = -result
    
    def setTargetList(self) -> None:
        # The target list was already set.
        if self.targets:
            return

        # Find any overwrite target lists.
        ghostwriter = self.invoker.getStatusEffectsOfId(StatusEffectEnum.TARGET_LIST_GHOSTWRITER)
        for effect in ghostwriter:
            targetList = effect.determineNewTargets(self)
            if targetList is not None:
                self.targets = targetList
                return

        # Add the random toons to the target list.
        self.targets = self.chooseRandomToon()

    def chooseRandomToon(self, amount: int=1, biased: bool=True, chooseAlive: bool=True) -> list:
        # Unbiased picking is very simple.
        if not biased:
            # Grab all of the alive Toons.
            toons = self.getAliveToons()
            # Shuffle them.
            random.shuffle(toons)
            # Return the desired amount of toons.
            return toons[:min(amount, len(toons))]

        # First, get all of the toons that have hit this suit.
        toons = self.invoker.aggroMap

        toonDict = {}

        # Iterate through all active toons.
        for toon in (self.getAliveToons() if chooseAlive else self.getToons()):
            toonId = toon.doId
            # Exclude untouchable toons.
            if toon.getStatusEffectOfType(StatusEffects.UntouchableStatusEffect):
                continue
            # If the toon exists in their aggro, use that value.
            if toonId in toons:
                toonDict[toon] = toons[toonId]
            # Otherwise, use a default value of 1, so that they're
            # still included in the calculation.
            else:
                toonDict[toon] = 1

        for toon in toonDict:
            # If the target has any aggro modifiers, apply them.
            modifierStatusEffects = toon.getStatusEffectsOfType(StatusEffects.AggroModifierStatusEffect)
            for statusEffect in modifierStatusEffects:
                toonDict[toon] = statusEffect.handleAggroModifier(toonDict)

        chosenToons = []

        # If the dictionary of toons is empty, return.
        if not toonDict:
            return chosenToons

        for _ in range(amount):
            if not toonDict:
                break

            # Choose a random toon from the toons dictionary.
            toon = random.choices(list(toonDict), weights=list(toonDict.values()))[0]
            chosenToons.append(toon)

            # Remove the chosen toon from the toonDict.
            del toonDict[toon]

        return chosenToons
    
    def getLanded(self) -> bool:
        randChoice = random.randint(1, 100)

        finalAcc = self.accuracy

        # If we have any accuracy status effects, apply them here.
        accuracyStatusEffects = self.invoker.getStatusEffectsOfType(StatusEffects.AttackAccuracyStatusEffect)
        for statusEffect in accuracyStatusEffects:
            # If override, force the accuracy.
            finalAcc, override = statusEffect.handleAttackAccuracy(self, finalAcc)
            if override != -1:
                finalAcc = override

        return randChoice <= finalAcc
    
    def getDamage(self, target: BattleAvatar=None) -> int:
        return int(self.damage * self.invoker.getDamageMultiplier() * self.damageMult)
