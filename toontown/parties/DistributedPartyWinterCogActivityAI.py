from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.parties.DistributedPartyCogActivityAI import DistributedPartyCogActivityAI

class DistributedPartyWinterCogActivityAI(DistributedPartyCogActivityAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedPartyWinterCogActivityAI")

