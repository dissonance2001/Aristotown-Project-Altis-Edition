"""Contains the global :class:`.EventManager` instance."""

from __future__ import absolute_import
__all__ = ['eventMgr']

from . import EventManager

#: The global event manager.
eventMgr = EventManager.EventManager()
