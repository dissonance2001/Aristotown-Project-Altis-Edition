"""
This module contains all required classes to build Battle Event Definitions.
The base classes can be found in BattleListenerClasses.py.
"""
import random

from toontown.battle.BattleEventGlobals import BEG
from toontown.battle.BattleListenerClasses import *
from toontown.battle.attacks.base.AttackEnum import AttackEnum


# # # CallbackType Subclasses # # #


class SelfCallback(CallbackType):
    """
    Performs a method callback on the object tied to the event definition.
    """

    def getObject(self, battleListenerDict):
        return battleListenerDict['self']


class DecrementCallback(SelfCallback):

    def __init__(self, amount: int=1):
        super().__init__("decrement", amount=amount)


class AvatarGetterCallback(SelfCallback):

    def __init__(self) -> None:
        super().__init__("getAv")


class BattleCalculatorCallback(CallbackType):
    """
    Performs a method callback on the Battle Calculator.
    """

    def getObject(self, battleListenerDict):
        return battleListenerDict['battleCalculator']


class SuitNameGetterCallback(BattleCalculatorCallback):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__("getSuitName", *args, **kwargs)


class BattleListenerCallback(CallbackType):
    """
    Performs a method callback on the Battle Listener.
    """

    def getObject(self, battleListenerDict):
        return battleListenerDict['battleListener']


# # # BattleEvent Subclasses # # #


class BattleEventCreateAndInsertAttack(BattleEvent):

    def __init__(self, name: str = None, attackType: AttackEnum = AttackEnum.TOON_NO_ATTACK,
                 listensTo: BEG=BEG.EVENT_ATTACK_ORDER, conditional = None, 
                 attackKwargs: dict = None, insertKwargs: dict = None, failureCallback=None):
        """
        :param name: The name of the battle event.
        :param attackType: The attack enum that the avatar should call.
        :param conditional: Conditional or ConditionalGroup
        :param attackExtraArgs: Extra args to be passed along with the attack.
        :param insertKwargs: Extra args for insertion.
        """
        super().__init__(
            name=name,
            listensTo=listensTo,
            callback=BattleCalculatorCallback(
                'createAndInsertAttack',
                attackType=attackType,
                attackKwargs=attackKwargs or {},
                insertKwargs=insertKwargs or {},
            ),
            conditional=conditional,
            failureCallback=failureCallback
        )


class BattleEventDelete(BattleEvent):
    """
    Listens for any avatar deaths, and upon the avatar associated with
    ourself dies, self destruct.
    """

    def __init__(self, name: str=None, failureCallback=None):
        super().__init__(
            name=name, 
            listensTo=(BEG.EVENT_TOON_LEFT, BEG.EVENT_SUIT_DIED, BEG.EVENT_SUIT_LEFT), 
            conditional=ConditionalReferenceEquality(AvatarGetterCallback(), EventArg.ZERO), 
            callback=SelfCallback("delete"),
            failureCallback=failureCallback
        )


class BattleEventBeginRound(BattleEvent):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, listensTo=BEG.EVENT_BEGIN_ROUND)


class BattleEventEndRound(BattleEvent):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, listensTo=BEG.EVENT_END_ROUND)


class BattleEventNormalAttacksOver(BattleEvent):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, listensTo=BEG.EVENT_NORMAL_ATTACKS_OVER)


class BattleEventSuitDied(BattleEvent):
    def __init__(self, name: str=None, suitName: str=None, callback=None, failureCallback=None):
        super().__init__(
            name,
            listensTo=BEG.EVENT_SUIT_DIED,
            callback=callback or SelfCallback("delete"),
            conditional=ConditionalValueEquality(SuitNameGetterCallback(EventArg.ZERO), suitName),
            failureCallback=failureCallback
        )

# # # Conditional Subclasses # # #


class CustomConditional(ConditionalBase):
    """
    Definition for a custom conditional.
    """

    def __init__(self, callbackType, funcName: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.callbackType = callbackType
        self.funcName = funcName


class CustomOverrideConditional(ConditionalBase):

    def test(self, battleListenerDict, eventArgs) -> bool:
        args, kwargs = self._cleanseArgs(battleListenerDict, eventArgs, list(self.args), self.kwargs)
        self.notify.debug(f"Testing conditional.\n\tfunction name: {self.funcName}\n\t"
                          f"args: {args}\n\tkwargs: {kwargs}")
        return self.customTest(args, kwargs, battleListenerDict, eventArgs)
    
    def customTest(self, args, kwargs, battleListenerDict, eventArgs):
        raise NotImplementedError


class ConditionalSomeSuitIsHurt(ConditionalBase):
    callbackType = BattleCalculatorCallback
    funcName = 'areCogsHurt'


class ConditionalRoundCycle(CustomOverrideConditional):
    def __init__(self, cycleLength: int=3, onRound: int=0):
        super().__init__(cycleLength, onRound, BattleCalculatorCallback("getCurrentRound"))
    
    def customTest(self, args, *otherArgs):
        divisor, remainders, currRounds = args
        if isinstance(remainders, (tuple, list)):
            return currRounds % divisor in remainders
        else:
            return currRounds % divisor == remainders


class ConditionalRoundCheck(CustomOverrideConditional):
    def __init__(self, roundNumber: int=1):
        super().__init__(roundNumber, BattleCalculatorCallback("getCurrentRound"))

    def customTest(self, args, *otherArgs):
        roundNumber, currRounds = args
        if isinstance(roundNumber, (tuple, list)):
            return currRounds in roundNumber
        else:
            return currRounds == roundNumber


class ConditionalEventWasSent(ConditionalBase):
    callbackType = BattleCalculatorCallback
    funcName = 'hasEventBeenSent'


class ConditionalReferenceEquality(CustomOverrideConditional):
    """
    Determines if the two given values are pointing to
    the same reference.
    """

    def customTest(self, args, *otherArgs):
        valueA, valueB = args
        return valueA is valueB


class ConditionalReferenceInequality(CustomOverrideConditional):
    """
    Determines if the two given values are not pointing to
    the same reference.
    """

    def customTest(self, args, *otherArgs):
        valueA, valueB = args
        return valueA is not valueB


class ConditionalValueEquality(CustomOverrideConditional):
    """
    Determines if the two given values are of equal value.
    """

    def customTest(self, args, *otherArgs):
        valueA, valueB = args
        return valueA == valueB


class ConditionalValueInequality(CustomOverrideConditional):
    """
    Determines if the two given values are not of equal value.
    """

    def customTest(self, args, *otherArgs):
        valueA, valueB = args
        return valueA != valueB


class ConditionalValueGreaterThan(CustomOverrideConditional):
    """
    Determines if the first value is greater than the second value.
    """

    def customTest(self, args, *otherArgs):
        valueA, valueB = args
        return valueA > valueB
    

class ConditionalMultipleValueEquality(CustomOverrideConditional):
    """
    Determines if value A has an equal value in value B.
    """

    def customTest(self, args, *otherArgs):
        valueA, valueB = args
        return valueA in valueB


class ConditionalSelfIsAlive(ConditionalValueGreaterThan):

    def __init__(self):
        super().__init__(SelfCallback("getHp"), 0)


class ConditionalRandomRoll(CustomOverrideConditional):

    def customTest(self, args, *otherArgs):
        chance = args[0]
        return random.random() <= chance


class ConditionalSuitTypeLured(ConditionalBase):
    callbackType = BattleCalculatorCallback
    funcName = "isASuitLured"


# # # ConditionalGroup Subclasses # # #


class WantAllConditionalGroup(ConditionalGroup):

    def test(self, battleListenerDict, eventArgs) -> bool:
        return all(conditional.test(battleListenerDict, eventArgs) for conditional in self.conditionals)


# # # Constants # # #

BaseStatusEffectEvents = [
    BattleEventEndRound(
        callback=DecrementCallback(),
    )
]

BaseEnvironmentalEvents = BaseStatusEffectEvents.copy() + [
    BattleEvent(
        listensTo=BEG.EVENT_SET_PARTICIPANTS,
        callback=SelfCallback('setParticipants', EventArg.ZERO, EventArg.ONE)
    ),
    BattleEvent(
        listensTo=BEG.EVENT_TOON_ADDED_TO_BATTLE,
        callback=SelfCallback('handleToonAddedToBattle', EventArg.ZERO),
    ),
    BattleEvent(
        listensTo=BEG.EVENT_SUIT_ADDED_TO_BATTLE,
        callback=SelfCallback('handleSuitAddedToBattle', EventArg.ZERO),
    ),
    BattleEvent(
        listensTo=BEG.EVENT_TOON_LEFT,
        callback=SelfCallback('handleToonRemovedFromBattle', EventArg.ZERO),
    ),
    BattleEvent(
        listensTo=BEG.EVENT_SUIT_LEFT,
        callback=SelfCallback('handleSuitRemovedFromBattle', EventArg.ZERO),
    ),
    BattleEvent(
        listensTo=BEG.EVENT_BATTLE_END,
        callback=SelfCallback('handleBattleEnd'),
    ),
]


# # # ObjectDefinitionType Subclasses # # #

class SuitEventDefinition(ObjectDefinitionType):

    def connectsTo(self, obj) -> bool:
        return self.reference == obj.dna.name


class StatusEffectEventDefinition(ObjectDefinitionType):

    def connectsTo(self, obj) -> bool:
        if self.reference == obj.effectId:
            return True
        if self.reference in obj.inheritedEventDefinitions:
            return True
        return False

    @classmethod
    def getDefault(cls):
        return BaseStatusEffectEvents


class GenericEventDefinition(ObjectDefinitionType):

    def connectsTo(self, obj) -> bool:
        return self.reference == obj.__class__.__name__


class BattleCalculatorEventDefinition(GenericEventDefinition):
    pass


class BattleObjectEventDefinition(GenericEventDefinition):
    pass


class DistributedDiceChoiceDefinition(GenericEventDefinition):
    pass


class DebugGagAccuracyEventDefinition(GenericEventDefinition):
    pass


class AttackEventDefinition(ObjectDefinitionType):

    def connectsTo(self, obj) -> bool:
        return self.reference == obj.__class__.__name__ or self.reference in [c.__name__ for c in obj.__class__.__bases__]


class EnvironmentalEventDefinition(ObjectDefinitionType):

    def connectsTo(self, obj) -> bool:
        if self.reference in obj.environmentalType:
            return True
        elif self.reference in obj.inheritedEventDefinitions:
            return True
        return False
