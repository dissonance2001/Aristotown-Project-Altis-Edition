from toontown.building.DistributedToonInteriorAI import *
from toontown.toonbase import ToontownGlobals

class DistributedPizzeriaInteriorAI(DistributedToonInteriorAI):

    def __init__(self, block, air, zoneId, building):
        DistributedToonInteriorAI.__init__(self, block, air, zoneId, building)

    def delete(self):
        DistributedToonInteriorAI.delete(self)