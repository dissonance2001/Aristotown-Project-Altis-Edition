from enum import IntEnum

from toontown.notifications.NotificationEnums import NotificationType
from toontown.notifications.notificationData.NotificationData import NotificationData


class GenericTextId(IntEnum):
    # A field to use for the textId field.
    # (Since notifs could be DB'd, probably don't use auto?)
    ClubStatus = 0
    MailboxDelivery = 1
    BoardingInfo = 2
    DeniedBattle = 3
    BattleFullGroupDisbanded = 4
    RefundFailed = 5
    GroupDeniedPrivacyChange = 6
    GroupDeniedInvite = 7
    YouShouldntBeHere = 8
    ReportReviewed = 9
    DistrictMaintenanceCantCreateGroup = 10
    DistrictFullCantCreateGroup = 11
    DerrickmanGroupFinalExplanation = 12
    Mod_SuccessfullyDisbandedGroup = 13
    InventoryActionRateLimit = 14


class GenericTextNotification(NotificationData):
    """
    Simple, generic text.

    Only one notif with the same textId can be present at the same time.
    """
    notificationType = NotificationType.GenericText

    def __init__(self, textId: GenericTextId = 0, title: str = '', subtitle: str = ''):
        intArgs = [textId]
        strArgs = [title, subtitle]
        super().__init__(intArgs, strArgs)

    def getTextId(self):
        return self.intArgs[0]

    def getTitle(self):
        return self.strArgs[0]

    def getSubtitle(self):
        return self.strArgs[1]

    def shouldBeRemoved(self, otherNotif: 'GenericTextNotification'):
        if self.getNotificationType() == otherNotif.getNotificationType():
            if self.getTextId() == otherNotif.getTextId():
                return True
        return False
