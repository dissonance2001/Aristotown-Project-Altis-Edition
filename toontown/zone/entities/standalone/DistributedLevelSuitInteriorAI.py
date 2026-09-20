from toontown.building.DistributedSuitInteriorAI import DistributedSuitInteriorAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedLevelSuitInteriorAI(DistributedSuitInteriorAI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getExtLevelZone(self) -> int:
        return self.bldg.level.getEntityZoneEntId(self.bldg.entId)
