from __future__ import absolute_import
__all__ = ['jobMgr']

from . import JobManager

#: Contains the global :class:`~.JobManager.JobManager` object.
jobMgr = JobManager.JobManager()
