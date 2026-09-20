from toontown.building.DistributedDoorWithSpecialSoundAI import DistributedDoorWithSpecialSoundAI
from toontown.building.DoorTypes import SpecialSoundTypes
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedLevelDoorAI(DistributedDoorWithSpecialSoundAI):
    def __init__(self, air, blockNumber, doorType, buildingEntId, levelDoId, doorIndex=0, lockValue=0, swing=3, soundType=SpecialSoundTypes.Standard):
        super().__init__(air, blockNumber, doorType, doorIndex=doorIndex, lockValue=lockValue, swing=swing, soundType=soundType)
        self.buildingEntId = buildingEntId
        self.levelDoId = levelDoId
        self.level = self.air.getDo(self.levelDoId)

    def delete(self):
        self.level = None
        super().delete()

    def setBuildingEntId(self, buildingEntId):
        self.buildingEntId = buildingEntId

    def getBuildingEntId(self):
        return self.buildingEntId

    def setLevelDoId(self, levelDoId):
        self.levelDoId = levelDoId

    def getLevelDoId(self):
        return self.levelDoId
