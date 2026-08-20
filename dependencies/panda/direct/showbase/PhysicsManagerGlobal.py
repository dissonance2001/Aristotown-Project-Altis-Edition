"""Instantiates the global :class:`~panda3d.physics.PhysicsManager` object."""

from __future__ import absolute_import
__all__ = ['physicsMgr']

from panda3d.physics import PhysicsManager

#: Contains the global :class:`~panda3d.physics.PhysicsManager` instance.
physicsMgr = PhysicsManager()
