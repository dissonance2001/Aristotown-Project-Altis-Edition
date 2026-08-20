"""Instantiates the global :class:`~.InputState.InputState` object."""

from __future__ import absolute_import
__all__ = ['inputState']

# This file had to be separated from MessengerGlobal to resolve a
# circular include dependency with DirectObject.

from direct.controls import InputState

#: The global :class:`~.InputState.InputState` object.
inputState = InputState.InputState()
