from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedPlutoAI import DistributedPlutoAI

class DistributedWesternPlutoAI(DistributedPlutoAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedWesternPlutoAI")

