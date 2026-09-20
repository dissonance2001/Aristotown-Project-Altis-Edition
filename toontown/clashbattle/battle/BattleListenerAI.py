from toontown.clashbattle.battle.BattleEventDefinitionClasses import *
from toontown.clashbattle.battle import BattleEventDefinitionList


@DirectNotifyCategory()
class BattleListenerAI:
    """
    Original created on 8/13/2020 by Sketched.
    Object-oriented rewrite created on 3/27/2022 by Main.

    BattleListenerAI

    The BattleListenerAI class listens for events that are passed through to it
    via external means. When an event that was being listened to is triggered,
    the corresponding action that it was given will take place.

    This class should not need to be inherited, as it contains all of the required
    features for quick and simple 'modifications' to the battle calculator.

    @author: Sketched
    @coauthor: Main
    """

    class ObjectListener:
        """
        A listener object for the BattleListener.
        Takes an object and stores its event definitions.
        """

        def __init__(self, object):
            self.object = object
            self.eventDefs = []

        def cleanup(self):
            del self.object
            del self.eventDefs

        def addObjectEvents(self, objectEvents):
            self.eventDefs.extend(objectEvents)

    def __init__(self, battleCalc):
        self.notify.debug(f"New BattleListenerAI {id(self)} instance active.")
        self.openEvents = {}
        self.eventHistory = {}
        self.eventDefs = BattleEventDefinitionList.EventDefs
        self.battleCalc = battleCalc
        self.cleanedUp = False
        self.addListenerObject(battleCalc, BattleCalculatorEventDefinition)

    def cleanup(self):
        if self.cleanedUp:
            return
        self.cleanedUp = True

        for objectListener in self.openEvents.values():
            objectListener.cleanup()
        del self.openEvents
        del self.eventDefs
        self.notify.debug(f"BattleListenerAI {id(self)} has cleaned up.")

    def addListenerObject(self, object, objectDefinitionClass):
        """
        Adds an object to the BattleListener.
        :param object: The object to be added.
        :param objectDefinitionClass: The definition class associated with this object.
        """
        # Sanity check, just to be sure.
        assert issubclass(objectDefinitionClass, ObjectDefinitionType)

        # Find all event definitions attached to this object.
        objectEvents = self.eventDefs.findObjectEvents(object, objectDefinitionClass)

        # If we have not started listening to this object, open an entry.
        if object not in self.openEvents:
            self.notify.debug(f"Adding a new ObjectListener for {object}.")
            self.openEvents[object] = self.ObjectListener(object)

        # Start listening to all events for this object.
        self.notify.debug(f"Adding new object events for {object}.")
        self.openEvents[object].addObjectEvents(objectEvents)

    def removeListenerObject(self, object):
        """
        Removes an object from the BattleListener.
        :param object: The object to stop listening to.
        """
        if object in getattr(self, "openEvents", {}):
            self.notify.debug(f"Cleaning up a new ObjectListener for {object}.")
            del self.openEvents[object]
        else:
            self.notify.debug(f"Attempt to clean an ObjectListener for {object} failed, as it does not exist.")

    def sendEvent(self, eventId, eventArgs=None):
        """
        Tell the Battle Listener that an event has happened.
        The Battle Listener will activate all event definitions as necessary.
        """
        if self.cleanedUp:
            return

        if eventId == BEG.EVENT_BEGIN_ROUND:
            # Debug to notify that this is the beginning of a round.
            self.notify.debug(f"-=- ROUND START -=-")

        eventArgs = eventArgs if eventArgs else []
        self.addEventNameToHistory(eventId)

        # Iterate over all events we have open.
        sentEvent = False
        for object, objectListener in list(self.openEvents.items()):
            # We want to ensure that, for each event definition, the event name
            # that we received corresponds to the event definition.
            # If this is the case, we will activate the event!
            for battleEvent in objectListener.eventDefs:
                if eventId in battleEvent.listensTo:
                    # This event def can and will be activated.
                    sentEvent = True
                    self.notify.debug(f"ACTIVATE EVENT {eventId.name} - OBJECT {object.__class__.__name__}")
                    battleEvent.activateEvent(self.getBattleListenerDict(object), eventArgs)
                    self.notify.debug(f"EVENT {eventId.name} END - OBJECT {object.__class__.__name__}")

        # If we didn't send an event, do a notify with more info.
        if not sentEvent:
            self.notify.debug(f"Event {eventId.name} sent, has no callbacks.")

        if eventId == BEG.EVENT_END_ROUND:
            # Debug to notify that this is the end of the round.
            self.notify.debug(f"-=- ROUND END -=-")

    def getBattleListenerDict(self, object):
        """
        Gets the battle listener dict.
        This is used for replacements for battle event activation.
        """
        return {
            'self': object,
            'battleCalculator': self.battleCalc,
            'battleListener': self,
        }

    def addEventNameToHistory(self, eventName):
        """
        Adds an event name to the current event history.
        """
        currentRound = self.getCurrentRound()
        self.eventHistory.setdefault(currentRound, [])
        self.eventHistory[currentRound].append(eventName)

    def getEventsSentThisRound(self):
        """
        Returns a list of all events sent this round.
        """
        return self.eventHistory.get(self.getCurrentRound(), [])

    def getCurrentRound(self):
        return self.battleCalc.getCurrentRound()
