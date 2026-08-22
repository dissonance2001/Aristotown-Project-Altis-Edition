from toontown.battle import BattleGlobals
from toontown.groups.GroupClasses import GroupCreation
from toontown.groups.GroupEnums import Responses, GroupType, Options
from toontown.groups.GroupGlobals import BoardingGroupInformation
from toontown.groups.GroupLocalizer import GROUP_DISBAND_PIZZERIA_DISTRICT_FULL_MESSAGE
from toontown.modifiers.contentsync.ContentSyncDefinitions import GroupTypeToGTSDef, ContentSyncDefinitions
from toontown.notifications.NotificationEnums import NotificationType
from toontown.notifications.notificationData.NotificationData import NotificationData
from toontown.toonbase import TTLocalizer
from toontown.utils import text


class GroupCallbackNotification(NotificationData):
    """
    Contains logic for retrieving group callback info.
    """
    notificationType = NotificationType.GroupCallback

    def __init__(self,
                 errorCode=None, errorType=0,
                 avId=0, name='', groupType=0, oneGroupOption=0):
        """Creates a GroupCallbackNotification dataclass."""
        if type(errorCode) is Responses:
            intArgs = [errorCode.value, errorType.value, avId, groupType, oneGroupOption]
        else:
            intArgs = [errorCode, errorType, avId, groupType, oneGroupOption]
        strArgs = [name]
        super(GroupCallbackNotification, self).__init__(intArgs, strArgs)

    def getErrorCode(self):
        return Responses(self.intArgs[0])

    def getErrorType(self):
        return Responses(self.intArgs[1])

    def getCodeMessage(self):
        if self.getErrorType() == Responses.CannotJoinGroup:
            if self.getErrorCode() in (Responses.WarningBelowLaffRec, Responses.WarningBelowGagRec):
                groupDef = BoardingGroupInformation[self.getGroupType()]
                return TTLocalizer.GroupJoinFailure[self.getErrorCode()] % (groupDef.minLaffRec if self.getErrorCode() == Responses.WarningBelowLaffRec else groupDef.minGagRec)
            return TTLocalizer.GroupJoinFailure[self.getErrorCode()]
        elif self.getErrorType() == Responses.CannotMakeGroup:
            if self.getErrorCode() in (Responses.WarningBelowLaffRec, Responses.WarningBelowGagRec):
                groupDef = BoardingGroupInformation[self.getGroupType()]
                return TTLocalizer.GroupCreateFailure[self.getErrorCode()] % (groupDef.minLaffRec if self.getErrorCode() == Responses.WarningBelowLaffRec else groupDef.minGagRec)
            return TTLocalizer.GroupCreateFailure[self.getErrorCode()]
        elif self.getErrorType() == Responses.DistrictFullPizzeria:
            return GROUP_DISBAND_PIZZERIA_DISTRICT_FULL_MESSAGE
        elif self.getErrorType() in (Responses.OK, Responses.Info):
            if self.isLocalJoinNotification():
                # Return a unique message, if we are being content sync'd or not.
                syncType = GroupTypeToGTSDef.getSyncType(self.getGroupCreation())
                av = base.localAvatar
                if syncType:
                    csDef = ContentSyncDefinitions.getDefinition(syncType)
                    if csDef.checkSyncActive(av):
                        # Base message
                        msg = 'You have joined the Group.\n'

                        # Laff sync messages
                        if csDef.checkLaffSyncActive(av):
                            msg += '\n\1white\1\5icon_contentSync\5\2 Your Max Laff will be {0}.'.format(csDef.getConstrainedLaff(av))

                        # Gag sync message
                        if csDef.checkGagSyncActive(av):
                            levelRestricted = csDef.getMaxGagLevel() + 1
                            msg += '\n\1white\1\5icon_contentSync\5\2 Up to Level {0} Gags are permitted.'.format(levelRestricted)

                        # Add reward message (we *can* predict these, they aren't inconsistent between boss tiers
                        prohibitedRewards = []
                        if csDef.checkIOUSyncActive(av):
                            prohibitedRewards.append('IOUs')
                        if csDef.checkUniteSyncActive(av):
                            prohibitedRewards.append('Unites')
                        if csDef.checkCNDSyncActive(av):
                            prohibitedRewards.append('C&Ds')
                        if csDef.checkPinkSlipSyncActive(av):
                            prohibitedRewards.append('Pink Slips')

                        # Add the message if we have actually blocked any rewards.
                        if prohibitedRewards:
                            blockedRewardMsg = text.makeCommaSeparatedItems(prohibitedRewards)
                            msg += '\n\1white\1\5icon_contentSync\5\2 {0} will be restricted.'.format(blockedRewardMsg)

                        return msg

                # If we're at this point, content sync is very not active.
                return 'You have joined the Group.'
            else:
                msg = TTLocalizer.GroupKeepupMessages[self.getErrorCode()]
                if self.getToonName():
                    msg = msg % self.getToonName()
            return msg
        else:
            return ''

    def getAvId(self):
        return self.intArgs[2]

    def getToonName(self):
        return self.strArgs[0]

    def isLocalJoinNotification(self):
        return self.getAvId() == base.localAvatar.getDoId() and self.getErrorCode() == Responses.ToonJoined

    def hasContentSyncActive(self):
        if self.getAvId() != base.localAvatar.getDoId():
            return False
        syncType = GroupTypeToGTSDef.getSyncType(self.getGroupCreation())
        if syncType:
            csDef = ContentSyncDefinitions.getDefinition(syncType)
            if csDef.checkSyncActive(av=base.localAvatar):
                return True
        return False

    def getGroupType(self):
        return self.intArgs[3]

    def getGroupCreation(self):
        return GroupCreation(
            groupType=self.intArgs[3],
            groupOptions=[self.intArgs[4]],
            groupSize=123456789,  # doesn't matter, not used
        )

    def shouldBeRemoved(self, otherNotif):
        if otherNotif.getNotificationType() == self.getNotificationType():
            return True
        return False