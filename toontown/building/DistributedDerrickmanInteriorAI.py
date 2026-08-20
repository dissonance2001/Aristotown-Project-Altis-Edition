from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI

class DistributedDerrickmanInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedDerrickmanInteriorAI")

