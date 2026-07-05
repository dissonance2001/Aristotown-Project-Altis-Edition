"""
Alias/Wrapper class for DistributedCogHQDoorAI to promote distinguishability
"""

from .DistributedCogHQDoorAI import *
from direct.directnotify import DirectNotifyGlobal


class DistributedCogHQBossDoorAI(DistributedCogHQDoorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedCogHQBossDoorAI')
    """
    DistributedCogHQBossDoorAI(DistributedCogHQDoorAI)
    """
    pass
