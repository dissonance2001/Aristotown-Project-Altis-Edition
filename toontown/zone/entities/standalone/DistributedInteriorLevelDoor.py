from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.zone.entities.standalone.DistributedLevelDoor import DistributedLevelDoor
from toontown.level import LevelConstants
from toontown.building.DistributedDoor import DistributedDoor
from toontown.hood import ZoneUtil


@DirectNotifyCategory()
class DistributedInteriorLevelDoor(DistributedLevelDoor):
    """
    An unfortunate class that needs to exist for the sake
    of properly sending us back to level areas.
    """

    def announceGenerate(self):
        # Re-re-override the announceGenerate to use the standard door one
        DistributedDoor.announceGenerate(self)

    def setOtherZoneIdAndDoIdAndLevelZone(self, zoneId, distributedObjectID, levelZone):
        # Alternate function for use when going to level zones
        self.otherZoneId = zoneId
        self.otherDoId = distributedObjectID
        self.levelZone = levelZone

    def getRequestStatus(self):
        zoneId = self.otherZoneId
        # We must set allowRedirect to 0 because we expect to meet our other door on the other side.
        request = {
            'loader': ZoneUtil.getBranchLoaderName(zoneId),
            'where': ZoneUtil.getToonWhereName(zoneId),
            'how': 'DoorIn',
            'hoodId': ZoneUtil.getHoodId(zoneId),
            'zoneId': zoneId,
            'shardId': None,
            'avId': -1,
            'allowRedirect': 0,
            'doorDoId': self.otherDoId,
            'levelZone': self.levelZone,
        }
        # Let the persistent level know to ignore the loading screen and title text
        bboard.post(LevelConstants.Bulletin_IgnoreLoad, True)
        bboard.post(LevelConstants.Bulletin_IgnoreTitleText, True)
        return request
