from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedChipAI import DistributedChipAI

class DistributedPoliceChipAI(DistributedChipAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPoliceChipAI")

