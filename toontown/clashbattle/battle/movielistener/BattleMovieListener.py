from typing import Dict, List

from direct.showbase.DirectObject import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.clashbattle.battle.movielistener.BattleMovieListenerEnum import BMLE


class BattleMovieEventStore:
    def __init__(self, eventFunc, lastsOnce=False):
        self.eventFunc = eventFunc
        self.lastsOnce = lastsOnce
        self.disabled = False

    def callFunc(self, sequence=None, **eventKwargs):
        if self.disabled:
            return

        self.eventFunc(sequence, **eventKwargs)
        if self.lastsOnce:
            self.disabled = True


@DirectNotifyCategory()
class BattleMovieListener(DirectObject):
    """
    A rudimentary client version of the battle listener used for battle movies.
    """

    def __init__(self, battle):
        super().__init__()
        self.battle = battle
        self.eventHooks: Dict[object, Dict[int, List[BattleMovieEventStore]]] = {}

    def sendEvent(self, eventId: BMLE, sequence=None, **eventKwargs) -> None:
        for eventObject in list(self.eventHooks.keys()):
            for eventStore in list(self.eventHooks[eventObject].get(eventId, [])):
                eventStore.callFunc(sequence, **eventKwargs)
                if eventStore.lastsOnce and eventStore in self.eventHooks[eventObject]:
                    self.eventHooks[eventObject].remove(eventStore)

    def addHook(self, eventObj, eventId, eventFunc, lastsOnce=False):
        # Create the event store and add it to the dict
        self.eventHooks.setdefault(eventObj, {})
        self.eventHooks[eventObj].setdefault(eventId, [])
        eventStore = BattleMovieEventStore(eventFunc, lastsOnce)
        self.eventHooks[eventObj][eventId].append(eventStore)

    def removeHooks(self, eventObj):
        if eventObj in self.eventHooks:
            del self.eventHooks[eventObj]

    def cleanup(self):
        self.battle = None
        self.eventHooks = {}
