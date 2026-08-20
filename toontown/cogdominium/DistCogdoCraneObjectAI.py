from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistCogdoCraneObjectAI(DistributedObjectAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistCogdoCraneObjectAI")