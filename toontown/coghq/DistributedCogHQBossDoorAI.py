"""
Alias/Wrapper class for DistributedCogHQDoorAI to promote distinguishability
"""

from __future__ import absolute_import
from .DistributedCogHQDoorAI import *
from direct.directnotify import DirectNotifyGlobal


class DistributedCogHQBossDoorAI(DistributedCogHQDoorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCogHQBossDoorAI')
    """
    DistributedCogHQBossDoorAI(DistributedCogHQDoorAI)
    """
    pass
