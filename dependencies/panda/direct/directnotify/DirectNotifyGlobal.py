"""Instantiates global DirectNotify used in Direct."""

from __future__ import absolute_import
__all__ = ['directNotify', 'giveNotify']

from . import DirectNotify

#: The global :class:`~.DirectNotify.DirectNotify` object.
directNotify = DirectNotify.DirectNotify()

#: Shorthand function for adding a DirectNotify category to a given class
#: object.  Alias of `.DirectNotify.DirectNotify.giveNotify`.
giveNotify = directNotify.giveNotify
