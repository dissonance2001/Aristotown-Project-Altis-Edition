from __future__ import absolute_import
from direct.distributed.DistributedObjectGlobalAI import DistributedObjectGlobalAI
from direct.directnotify.DirectNotifyGlobal import directNotify


class DistributedGroupManagerAI(DistributedObjectGlobalAI):
    notify = directNotify.newCategory('DistributedGroupManagerAI')

    def announceGenerate(self):
        DistributedObjectGlobalAI.announceGenerate(self)
