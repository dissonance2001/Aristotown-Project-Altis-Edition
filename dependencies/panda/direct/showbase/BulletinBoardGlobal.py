"""Instantiates the global :class:`~.BulletinBoard.BulletinBoard` object."""

from __future__ import absolute_import
__all__ = ['bulletinBoard']

from . import BulletinBoard

#: The global :class:`~.BulletinBoard.BulletinBoard` object.
bulletinBoard = BulletinBoard.BulletinBoard()
