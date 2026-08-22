from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from toontown.toon.DistributedToonAI import DistributedToonAI


class ContentSyncApplierAI:
    """
    An AI-sided base class to help apply Content Sync onto Toons for various instances.
    self.air must be defined for this to be functional.
    """

    contentSync_listenForZone = True
    contentSync_listenForDeath = True

    def getContentSync(self):
        """
        Figures out the ideal content sync to apply.
        Override this method to set the content sync.
        """
        return None

    def contentSync_getForceOldZone(self):
        return None

    def contentSync_getIgnoreThisZone(self):
        return None

    def contentSync_getZoneChangeIsLogical(self):
        return False

    def applyContentSync(self, *toons):
        assert hasattr(self, 'air') and self.air, "self.air must be defined for ContentSync."

        contentSync = self.getContentSync()
        if contentSync is None:
            return

        self.air.contentSyncManager.applyContentSync(
            syncType=contentSync,
            toons=toons,
            listenForZone=self.contentSync_listenForZone,
            listenForDeath=self.contentSync_listenForDeath,
            forceOldZone=self.contentSync_getForceOldZone(),
            ignoreThisZone=self.contentSync_getIgnoreThisZone(),
            isLogical=self.contentSync_getZoneChangeIsLogical(),
        )

    def removeContentSync(self, *toons):
        assert hasattr(self, 'air') and self.air, "self.air must be defined for ContentSync."

        if self.getContentSync() is None:
            return

        for toon in toons:
            self.air.contentSyncManager.removeContentSync(toon)

    def avIdsToAvs(self, avIds):
        retlist = []
        for toonId in avIds:
            toon = self.air.doId2do.get(toonId)
            if toon:
                retlist.append(toon)
        return retlist