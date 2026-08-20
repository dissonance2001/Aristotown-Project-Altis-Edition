"""Contains the global :class:`~.Task.TaskManager` object."""

from __future__ import absolute_import
__all__ = ['taskMgr']

from . import Task

#: The global task manager.
taskMgr = Task.TaskManager()
