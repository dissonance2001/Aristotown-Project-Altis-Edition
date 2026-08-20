"""Instantiates the global :class:`~.Messenger.Messenger` object."""

from __future__ import absolute_import
__all__ = ['messenger']

from . import Messenger

#: Contains the global :class:`~.Messenger.Messenger` instance.
messenger = Messenger.Messenger()
