from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.zone.entities.standalone.DistributedLevelDoorAI import DistributedLevelDoorAI


@DirectNotifyCategory()
class DistributedInteriorLevelDoorAI(DistributedLevelDoorAI):
    """
    An unfortunate class that needs to exist so that doors know
    how to send us back to level zones properly.
    """

    def requestEnter(self):
        avatarID = self.air.getAvatarIdFromSender()
        if self.getAllowed(avId=avatarID):
            self.sendReject(avatarID, self.isLockedDoor())
        else:
            self.enqueueAvatarIdEnter(avatarID)
            self.sendUpdateToAvatarId(
                avatarID, 'setOtherZoneIdAndDoIdAndLevelZone',
                [self.level.zoneId, self.otherDoor.getDoId(), self.level.getEntityZoneEntId(self.buildingEntId)])
