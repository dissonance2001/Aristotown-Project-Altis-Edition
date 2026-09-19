"""
This module represents all base classes to build Battle Event Definitions.

The general heirarchy is as follows:
- BattleEventDefinitions
    - A container holding a dict between ObjectDefinitionTypes : BattleEvents.
    - Accessed by the BattleListener to appropriately find event definitions.
    - Contains:
        - ObjectDefinitionTypes
            - These reflect the type of object that a definition is being applied to.
            - For example, SuitEventDefinition represents a suit in battle that the
              events are being directly attached to.
        - BattleEvents
            - Expressed as either a single BattleEvent, or a tuple containing several BattleEvents.
            - A BattleEvent contains:
                - A name as a string (optional)
                - An event, or tuple of events, to listen to.
                - A EventCallbackType on conditional success
                    - Expressed as either a single EventCallbackType, or a tuple containing several EventCallbackTypes.
                    - References a callback that is to be executed upon the event being fired.
                - A EventCallbackType on conditional failure
                    - Same as above.
                - An EventConditional or EventConditionalGroup
                    - An EventConditionalGroup contains conditionals. The type of ConditionalGroup reflects
                      the condition on which the ConditionalGroup may return True.
                    - An EventConditional runs a callback with arguments, which are specified on
                      the initialization of an EventConditional instance.
                - Either a tuple or dict representing callbackArguments.
                    - As a tuple:
                        - Represents the arguments in order that are used with the callback.
                        - EVENT_X consts are replaced with actual information from
                          the respective events that are sent.
                    - As a dict:
                        - Represents the keyword arguments that are used with the callback.
                        - EVENT_X consts are replaced with actual information from
                          the respective events that are sent.
"""
from toontown.toonbase import RealmGlobals

from direct.directnotify import DirectNotifyGlobal
from copy import copy, deepcopy
from enum import Enum
from typing import TYPE_CHECKING

import os


### Enums ###
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


class EventArg(Enum):
    SELF = -1
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7


### Exceptions ###


class BattleEventException(BaseException):
    """
    An exception raised by BattleEvent-related classes, to strongly specify the kind of exception that occurred.
    """
    pass


### Base Classes ###

def parseArgument(value, battleListenerDict, eventArgs):
    if isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            value[i] = parseArgument(v, battleListenerDict, eventArgs)
    elif isinstance(value, dict):
        for k, v in value.items():
            value[k] = parseArgument(v, battleListenerDict, eventArgs)
    else:
        # 1. Replace eventArgs as necessary.
        # 2. If callbacks are present, run those.
        # 3. Pass everything else through cleanly.
        if value == EventArg.SELF:
            # This value is a SELF sentinel, so set it to the self object.
            return battleListenerDict['self']
        elif isinstance(value, EventArg):
            # This value is an event arg -- so replace it from one in the list.
            return eventArgs[value.value]
        elif isinstance(value, CallbackType):
            # This value is a callback type. So, run the callback accordingly.
            return value.runCallback(battleListenerDict, eventArgs)
        else:
            # This value has nothing special, so pass it through.
            return value
    return value


@DirectNotifyCategory(debug=RealmGlobals.getCurrentRealm().isPrivateRealm())
class ConditionalBase:
    """
    Declares a base class for a Conditional.

    A Conditional is a callback wrapper for BattleEvents.

    With a specified callback type (which points to which object a callback lies upon)
        and function name (the name of the function on this object), a Conditional
        will use this callback type and return either True or False from a test method.

    By specifying args and kwargs on initiation, a Conditional will use these
        args and kwargs for the callback upon testing.

    To use a Conditional, you MUST use a subclass of ConditionalBase in BattleEventDefinitionClasses.
        1) Use CustomConditional if you want to specify the callback type, function name, and arg/kwargs directly.
        2) Use a different Conditional subclass if you want ease in defining specific conditionals.
           If the conditional that you're looking for is common, perhaps it is already defined.
    """
    callbackType = None
    funcName = ''

    def __init__(self, *args, **kwargs):
        """
        Let subclasses be more specific with how these are defined.
        """
        self.args = args
        self.kwargs = kwargs

    def test(self, battleListenerDict, eventArgs) -> bool:
        """
        Tests the conditional.
        """
        args, kwargs = self._cleanseArgs(battleListenerDict, eventArgs, list(self.args), self.kwargs)
        self.notify.debug(f"Testing conditional.\n\tfunction name: {self.funcName}\n\t"
                          f"args: {args}\n\tkwargs: {kwargs}")
        return bool(
            self.callbackType(self.funcName).runCallback(
                battleListenerDict, eventArgs, *args, **kwargs
            )
        )
    
    @staticmethod
    def _cleanseArgs(battleListenerDict, eventArgs: list, args, kwargs):
        return parseArgument(args, battleListenerDict, eventArgs), \
            parseArgument(kwargs, battleListenerDict, eventArgs)


class ConditionalGroup(ConditionalBase):
    """
    Refers to a collection of EventConditionals.
    All conditionals inside the ConditionalGroup are tested.

    Subclasses of ConditionalGroup can be used to more finely determine the
        success conditions of the conditionals within a group, such as if
        the group is successful on any conditional testing True, or if
        ALL conditionals must test True.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conditionals = self.args

        if __dev__:
            # Sanity checking for developers
            if not self.args:
                raise BattleEventException(f"Arguments were not defined for ConditionalGroup.")

            if any(not isinstance(conditional, ConditionalBase) for conditional in self.conditionals):
                raise BattleEventException(f"ConditionalGroup was defined with a non-Conditional object.")

            if self.kwargs:
                raise BattleEventException(f"ConditionalGroup forbids keyword arguments.")

    def test(self, battleListenerDict, eventArgs) -> bool:
        return any(conditional.test(battleListenerDict, eventArgs) for conditional in self.conditionals)


@DirectNotifyCategory(debug=RealmGlobals.getCurrentRealm().isPrivateRealm())
class CallbackType:
    """
    A Callback wrapper, where subclasses are able to point
    specifically to which object the Callback belongs to.

    funcName references the name of the method attached to an object.

    kwargs are the base keyword arguments for the function to use.
        A conditional that uses this callback, or callbackArguments,
        will have their kwargs override the ones set on the callback type.

    You MUST never initiate this class directly; only the base classes.
    """
    def __init__(self, funcName: str, *args, **kwargs):
        self.funcName = funcName
        self.args = args
        self.kwargs = kwargs

    def getObject(self, battleListenerDict):
        """
        Hmm...
        This is a bit tricky, as the object that CallbackType is aware of
        is strictly dependent on the context of the ObjectDefinitionType.

        As such, battleListenerDict is a dict that is generated by the BattleListener,
        and getObject will pick and return the right object from that dict.

        Hacky? Perhaps. Call me if you come up with a better solution.
            1-800-LOL-MAIN
        """
        raise NotImplementedError

    def runCallback(self, battleListenerDict, eventArgs, *args, **temp_kwargs):
        """
        Runs the callback as declared by the CallbackType.
        Contains several try/excepts to give pointed debugs during development.
        """
        # Get kwargs of the callback.
        # Use our defined kwargs, but we will prioritize bonus kwargs that are passed in.
        args = list(self.args) + list(args)
        kwargs = copy(self.kwargs)
        kwargs.update(temp_kwargs)

        # Cleanse our args/kwargs of any EventArg.SELFs.
        self._cleanseArgs(battleListenerDict, eventArgs, args, kwargs)

        # Ok, callback o' clock.
        if RealmGlobals.getCurrentRealm().isPrivateRealm():
            # Do sanity checking if we're a Toontown Developer.
            self.notify.debug(f"33% - Running callback of function name '{self.funcName}'...")
            try:
                obj = self.getObject(battleListenerDict)
            except Exception as e:
                self.notify.debug(f"Critical failure while attempting to get callback target of {self}")
                raise e
            self.notify.debug(f"67% - Object found: {obj.__class__.__name__}")
            callback = getattr(obj, self.funcName)
            if callback:
                try:
                    result = callback(*args, **kwargs)
                except Exception as e:
                    print(f"Critical failure while attempting to run "
                          f"callback {self.funcName} on object {obj.__class__.__name__}")
                    raise e
                self.notify.debug(f"100% - Callback complete!")
                return result
            else:
                raise BattleEventException(f"Object {obj.__class__.__name__} missing function {self.funcName}")
        else:
            # Since we're on live, try except with sentry
            try:
                return getattr(self.getObject(battleListenerDict), self.funcName)(*args, **kwargs)
            except Exception as e:
                # Something cringe happened, print it
                import traceback
                traceback.print_exc()
                if TYPE_CHECKING:
                    from toontown.rpc import ServerEnvAI
                    if ServerEnvAI.report_errors:
                        # Sentry: logging for callback exceptions
                        import sentry_sdk
                        with sentry_sdk.push_scope() as scope:
                            scope.set_level('error')
                            sentry_sdk.capture_exception(e)

    @staticmethod
    def _cleanseArgs(battleListenerDict, eventArgs: list, args, kwargs):
        return parseArgument(args, battleListenerDict, eventArgs), \
            parseArgument(kwargs, battleListenerDict, eventArgs)


@DirectNotifyCategory(debug=RealmGlobals.getCurrentRealm().isPrivateRealm())
class BattleEvent:
    """
    The base class for a BattleEvent.

    A BattleEvent is a full-on declaration of a callback to be ran upon certain
    events being called by any AI-related battle class. In addition, an optional
    name can be specified for the event, along with whatever event IDs that it
    will listen to in order to run the callback.

    In addition, you can declare a conditional, or a group of them with a ConditionalGroup.
    These are special objects that declare OTHER callbacks to be called. If these callbacks
    return False, then the BattleEvent's callback will not be ran. In the case that a
    failureCallback is defined, then that failureCallback will be ran instead.

    In addition, you can specify callbackArguments in the form of either some constant,
    list, or dictionary. A list will act as a list of args, and a dict will act as kwargs
    for the callback. There are special sentinel values you can use in callbackArguments.

        If you specify EventArg.SELF, then that value will be replaced with the object
            of the actual object with a listener attached.
        If you specify EventArg.ZERO, EventArg.ONE etc, then that value will be replaced
            with the args that are sent with the event. See BattleEventGlobals.py.
        If you specify some CallbackType, then the CallbackType will be calculated
            and used as the value for the callback argument.
    """
    def __init__(self, name: str = None, listensTo = None, conditional = None,
                 callback = None, failureCallback = None):
        """
        Creates a BattleEvent Instance.
        :param name: The name of the BattleEvent. Optional.
        :param listensTo: What event(s) this BattleEvent listens to.
        :param conditional: An EventConditional or EventConditionalGroup. Optional.
        :param callback: An EventCallbackType (or tuple of them) ran as a callback on conditional success.
        :param failureCallback: An EventCallbackType (or tuple of them) ran as a callback on conditional failure.
        """
        assert listensTo and (callback or failureCallback), f"A BattleEvent was defined incorrectly.\n" \
                                                            f"Kwargs:\n\tname: {name}\n\t" \
                                                            f"listensTo (required): {listensTo}\n\t" \
                                                            f"conditional: {conditional}\n\tcallback(s): {callback}\n\t" \
                                                            f"failureCallback: {failureCallback}\n\t" \
                                                            f"\t(Either callback or failureCallback required.)"
        self.name = name
        self.listensTo = listensTo if isinstance(listensTo, (list, tuple)) else (listensTo,)
        # Wrap Conditional in a ConditionalGroup if we deem necessary.
        if isinstance(conditional, (list, tuple)):
            conditional = ConditionalGroup(*conditional)
        self.conditional = conditional

        if callback is None:
            callback = []
        elif not isinstance(callback, (tuple, list)):
            callback = [callback]
        self.callback = callback

        if failureCallback is None:
            failureCallback = []
        elif not isinstance(failureCallback, (tuple, list)):
            failureCallback = [failureCallback]
        self.failureCallback = failureCallback

    def activateEvent(self, battleListenerDict, eventArgs: list):
        # This event has been activated, so we will perform it accordingly.
        # If there are any conditionals, we must test them.
        if not self.conditional:
            self.notify.debug("Event has no conditionals, so it will run callbacks.")
            success = True
        else:
            self.notify.debug("Event has conditionals, so we will test them.")
            success = self.conditional.test(battleListenerDict, eventArgs)
            self.notify.debug(f"Conditionals for event {'passed' if success else 'failed'}.")

        # Now, depending on if we were successful or not, we will perform
        # either the success callback or failure callback.
        if success:
            # The event was successful, so we may do our success callback.
            if self.callback:
                for i, callback in enumerate(self.callback):
                    self.notify.debug(f"Running callback #{i + 1}...")
                    callback.runCallback(battleListenerDict, eventArgs)
        else:
            # The event was unsuccessful, so we may do our failure callback.
            if self.failureCallback:
                self.notify.debug("Running failure callback...")
                for callback in self.failureCallback:
                    callback.runCallback(battleListenerDict, eventArgs)


class ObjectDefinitionType:
    """
    A subclass that allows classes that interface with the BattleListener
    to more reliably attach event definitions to objects.
    """

    def __init__(self, reference):
        self.reference = reference

    def connectsTo(self, obj) -> bool:
        """
        Checks if this object is connected to our reference.
        If it is, then return True. Otherwise return False.
        :param obj: The object that is being passed in.
        :return: True if the reference matches with the object, otherwise False.
        """
        raise NotImplementedError

    @classmethod
    def getDefault(cls):
        """Returns the default event definition, if no other definitions are defined."""
        return []


@DirectNotifyCategory(debug=RealmGlobals.getCurrentRealm().isPrivateRealm())
class BattleEventDefinitions:
    """
    The container class containing pairs of ObjectDefinitionTypes : BattleEvents.
    """
    def __init__(self, definitionDict):
        self.definitionDict = definitionDict

    def findObjectEvents(self, object, objectDefinitionClass):
        """
        Finds all object events of a given class tied to an object.
        :return: A list of all events.
        """
        objectEvents = []

        # Find all object events associated with this definition.
        for objectDefinition, battleEvent in self.definitionDict.items():  # type: ObjectDefinitionType, BattleEvent
            if not isinstance(objectDefinition, objectDefinitionClass):
                # This object definition does not match the class we're looking for.
                continue

            # Does this object definition match this object?
            if objectDefinition.connectsTo(object):
                # It does, so add the events.
                acceptedEvents = []
                for acceptedEvent in (battleEvent if isinstance(battleEvent, (tuple, list)) else [battleEvent]):
                    acceptedEvents.append(deepcopy(acceptedEvent))
                objectEvents.extend(acceptedEvents)

        # Return the events that we have found.
        # If none were found, use the definition class's defined default.
        return objectEvents or objectDefinitionClass.getDefault()
