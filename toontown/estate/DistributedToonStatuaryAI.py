from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.estate.DistributedStatuaryAI import DistributedStatuaryAI

class DistributedToonStatuaryAI(DistributedStatuaryAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedToonStatuaryAI")

    def setOptional(self, todo0):
        pass