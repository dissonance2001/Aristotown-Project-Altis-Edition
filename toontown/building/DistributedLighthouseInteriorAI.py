from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI

class DistributedLighthouseInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedLighthouseInteriorAI")

