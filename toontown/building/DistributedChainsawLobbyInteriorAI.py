from direct.directnotify import DirectNotifyGlobal
from toontown.building.DistributedToonInteriorAI import DistributedToonInteriorAI


class DistributedChainsawLobbyInteriorAI(DistributedToonInteriorAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedChainsawLobbyInteriorAI')

    def __init__(self, blockNumber, air, zoneId, building):
        DistributedToonInteriorAI.__init__(self, blockNumber, air, zoneId, building)
