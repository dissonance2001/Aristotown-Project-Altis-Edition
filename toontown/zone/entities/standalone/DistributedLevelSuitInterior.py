from toontown.building.DistributedSuitInterior import DistributedSuitInterior
from toontown.level import LevelConstants
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedLevelSuitInterior(DistributedSuitInterior):
    def __init__(self, cr):
        super().__init__(cr)
        self.extLevelZone = 0

    def setExtLevelZone(self, extLevelZone: int):
        self.extLevelZone = extLevelZone

    def getRewardRequestDict(self):
        request = super().getRewardRequestDict()
        request['levelZone'] = self.extLevelZone
        # Let the persistent level know to ignore the loading screen
        bboard.post(LevelConstants.Bulletin_IgnoreLoad, True)
        return request
