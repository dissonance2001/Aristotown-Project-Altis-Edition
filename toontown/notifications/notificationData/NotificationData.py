class NotificationData(object):
    """Local Python 2 notification data used by Altis's Clash GUI port."""

    _nextId = 1

    def __init__(self, title='', subtitle='', dna=None, onYes=None, onNo=None,
                 onDismiss=None, notificationType='generic', sfx=None,
                 dedupeKey=None):
        self.id = NotificationData._nextId
        NotificationData._nextId += 1
        self.title = title
        self.subtitle = subtitle
        self.dna = dna
        self.onYes = onYes
        self.onNo = onNo
        self.onDismiss = onDismiss
        self.notificationType = notificationType
        self.sfx = sfx
        self.dedupeKey = dedupeKey

    def getId(self):
        return self.id

    def getTitle(self):
        return self.title

    def getSubtitle(self):
        return self.subtitle

    def getDna(self):
        return self.dna

    def getNotificationType(self):
        return self.notificationType

    def hasChoices(self):
        return self.onYes is not None or self.onNo is not None

    def invokeYes(self):
        if self.onYes is not None:
            self.onYes()

    def invokeNo(self):
        if self.onNo is not None:
            self.onNo()

    def invokeDismiss(self):
        if self.onDismiss is not None:
            self.onDismiss()
