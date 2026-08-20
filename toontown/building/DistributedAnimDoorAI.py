from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedDoorAI import DistributedDoorAI

class DistributedAnimDoorAI(DistributedDoorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedAnimDoorAI")

