from direct.showbase.DirectObject import DirectObject

from toontown.modifiers.Modifier import Modifier
from toontown.modifiers.ModifierClasses import ContentSyncModifiers
from toontown.modifiers.contentsync.ContentSyncDefinitions import ContentSyncDefinitions
from toontown.modifiers.contentsync.ContentSyncEnums import ContentSyncType
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.toon.DistributedToonAI import DistributedToonAI
from toontown.toon.gui.ToonTipGlobals import TTE


@DirectNotifyCategory()
class ContentSyncManagerAI(DirectObject):

    def __init__(self, air):
        self.air = air
        self.accept('avatarEntered', self.onAvatarEntered)

    def applyContentSync(self, syncType, toons,
                         listenForZone=True, listenForDeath=True,
                         forceOldZone=None, ignoreThisZone=None, isLogical=False):
        if not toons:
            return

        if not isinstance(toons, (list, tuple, set)):
            toons = [toons]

        toons = [toon for toon in toons if not toon.hasModifier(*ContentSyncModifiers)]
        if not toons:
            self.notify.info('Attempted to apply ContentSync onto Toons, but they all had sync already.')
            return

        self.notify.info('Applying ContentSync [%s] onto Toons: %s' % (syncType, toons))

        self.removeContentSync(toons, update=False)

        for toon in toons:
            modifiers = ContentSyncDefinitions.getModifiersOfSyncType(syncType)
            for modifier in modifiers:
                finalModifier = modifier is modifiers[-1]
                toon.addModifier(modifier=modifier, update=finalModifier)

            if listenForZone:
                self.listenForZone(toon, forceOldZone=forceOldZone,
                                   ignoreThisZone=ignoreThisZone, isLogical=isLogical)
            if listenForDeath:
                self.listenForDeath(toon)

            toon.showToonTip(TTE.TIP_CONTENT_SYNC)

    def removeContentSync(self, toons, update=True):
        if not toons:
            return

        if not isinstance(toons, (list, tuple, set)):
            toons = [toons]

        toons = [toon for toon in toons if toon.hasModifier(*ContentSyncModifiers)]
        if not toons:
            if update:
                self.notify.info('Attempted to remove ContentSync from Toons, but they did not have any.')
            return

        if update:
            self.notify.info('Removing ContentSync from Toons: %s' % toons)

        for toon in toons:
            toon.removeModifierOfType(*ContentSyncModifiers, update=update)
            self.clearEventsForToon(toon)

    def onAvatarEntered(self, toon):
        self.clearEventsForToon(toon)

    def clearEventsForToon(self, toon):
        self.ignore(toon.getZoneChangeEvent())
        self.ignore(toon.getLogicalZoneChangeEvent())
        self.ignore(toon.getGoneSadMessage())

    def listenForZone(self, toon, forceOldZone=None, ignoreThisZone=None, isLogical=False):
        def onZoneChange(newZone, oldZone):
            if forceOldZone is not None and forceOldZone != oldZone:
                self.notify.info('Detected zone change from %s. However, it was not the right oldZone.' % toon)
                return
            if ignoreThisZone is not None and newZone == ignoreThisZone:
                self.notify.info('Detected zone change from %s. However, the new zone was the ignore zone.' % toon)
                return
            self.notify.info('Detected zone change from %s. Removing content sync...' % toon)
            self.removeContentSync(toon)

        zoneEvent = toon.getLogicalZoneChangeEvent() if isLogical else toon.getZoneChangeEvent()
        self.accept(zoneEvent, onZoneChange)

    def listenForDeath(self, toon):
        def onDeath():
            self.notify.info('Detected DEATH from %s. Removing content sync...' % toon)
            self.removeContentSync(toon)

        self.acceptOnce(toon.getGoneSadMessage(), onDeath)