"""
A BattleListenerObject is a object that is related
to the battle system that is able to access the Battle Listener.

Objects that should access the Battle Listener in whatever way
can subclass this object to more easily access it.
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from toontown.clashbattle.battle.BattleListenerAI import BattleListenerAI


class BattleListenerException(AttributeError):
    """
    Raised when a method is called on an object expecting a battle listener,
    but it was not set/defined.
    """
    pass


class BattleListenerObject:

    def getBattleListener(self):
        """:rtype: BattleListenerAI"""
        raise NotImplementedError("Subclass of BattleListenerObject must implement getBattleListener")

    def hasBattleListener(self) -> bool:
        """
        Determines if this object has a set battle listener.
        :return: True if a battle listener is set, False otherwise.
        """
        return self.getBattleListener() is not None

    def addListenerObject(self, object, objectDefinitionClass):
        """
        Adds an object to the BattleListener.
        :param object: The object to be added.
        :param objectDefinitionClass: The definition class associated with this object.
        """
        if not self.hasBattleListener():
            raise BattleListenerException("addObject called without battle listener set!")
        self.getBattleListener().addListenerObject(object, objectDefinitionClass)

    def removeListenerObject(self, object):
        """
        Removes an object from the BattleListener.
        :param object: The object to stop listening to.
        """
        if not self.hasBattleListener():
            raise BattleListenerException("removeListenerObject called without battle listener set!")
        self.getBattleListener().removeListenerObject(object)

    def sendEvent(self, eventId, eventArgs: list = None) -> None:
        """
        Sends an event through the Battle Listener.
        :param eventId: The integer ID of the event to send.
        :param eventArgs: The arguments to pass through for the event.
        :return: None.
        """
        if self.hasBattleListener():
            self.getBattleListener().sendEvent(eventId, eventArgs)

    def hasEventBeenSent(self, eventId, amount: int = 1) -> bool:
        """
        Determines if an event has been sent from the BattleListener.
        :param eventId: The integer ID of the event to check.
        :param amount: How many times has this event been sent minimum?
        :return: True if the event has been sent as many times or more than the amount, False otherwise.
        """
        if not self.hasBattleListener():
            raise BattleListenerException("hasEventBeenSent called without battle listener set!")
        return self.eventsSentThisRound(eventId) >= amount

    def eventsSentThisRound(self, eventId) -> int:
        """
        Returns how many times the specified event has been sent this round.
        :param eventId: The integer ID of the event to check.
        """
        if not self.hasBattleListener():
            raise BattleListenerException("eventsSentThisRound called without battle listener set!")
        return self.getBattleListener().getEventsSentThisRound().count(eventId)
