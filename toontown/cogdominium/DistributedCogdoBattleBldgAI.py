from __future__ import absolute_import
from direct.directnotify import DirectNotifyGlobal
from toontown.battle.DistributedBattleBldgAI import DistributedBattleBldgAI

class DistributedCogdoBattleBldgAI(DistributedBattleBldgAI):
    notify = DirectNotifyGlobal.directNotify.newCategory("DistributedCogdoBattleBldgAI")

