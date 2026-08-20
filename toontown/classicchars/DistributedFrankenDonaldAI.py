from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.classicchars.DistributedDonaldAI import DistributedDonaldAI

class DistributedFrankenDonaldAI(DistributedDonaldAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedFrankenDonaldAI")

