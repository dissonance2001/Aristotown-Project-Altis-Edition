from pandac.PandaModules import *
from toontown.toonbase import ToontownGlobals
from direct.directnotify import DirectNotifyGlobal
from toontown.safezone import Walk


class PublicWalk(Walk.Walk):
    notify = DirectNotifyGlobal.directNotify.newCategory('PublicWalk')

    def __init__(self, parentFSM, doneEvent):
        Walk.Walk.__init__(self, doneEvent)
        self.parentFSM = parentFSM
        self._boundActionHotkeys = []

    def load(self):
        Walk.Walk.load(self)

    def unload(self):
        Walk.Walk.unload(self)
        del self.parentFSM

    def _acceptActionKeys(self):
        for eventName in self._boundActionHotkeys:
            self.ignore(eventName)
        self._boundActionHotkeys = []
        bindings = (
            (ToontownGlobals.StickerBookHotkey, self.__handleStickerBookEntry),
            (ToontownGlobals.OptionsPageHotkey, self.__handleOptionsEntry)
        )
        for eventName, method in bindings:
            if eventName and eventName not in self._boundActionHotkeys:
                self.accept(eventName, method)
                self._boundActionHotkeys.append(eventName)
        self.accept('enterStickerBook', self.__handleStickerBookEntry)
        self.accept('reloadActionKeys', self._reloadActionKeys)

    def _ignoreActionKeys(self):
        for eventName in self._boundActionHotkeys:
            self.ignore(eventName)
        self._boundActionHotkeys = []
        self.ignore('enterStickerBook')
        self.ignore('reloadActionKeys')

    def _reloadActionKeys(self):
        self._acceptActionKeys()

    def enter(self, slowWalk=0):
        Walk.Walk.enter(self, slowWalk)
        if hasattr(base.localAvatar, 'book') and base.localAvatar.book is not None:
            base.localAvatar.book.showButton()
        self._acceptActionKeys()
        if hasattr(base.localAvatar, 'laffMeter') and base.localAvatar.laffMeter is not None:
            base.localAvatar.laffMeter.start()
        base.localAvatar.beginAllowPies()

    def exit(self):
        Walk.Walk.exit(self)
        if hasattr(base.localAvatar, 'book') and base.localAvatar.book is not None:
            base.localAvatar.book.hideButton()
        self._ignoreActionKeys()
        if hasattr(base.localAvatar, 'laffMeter') and base.localAvatar.laffMeter is not None:
            base.localAvatar.laffMeter.stop()
        base.localAvatar.endAllowPies()

    def __handleStickerBookEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if currentState == 'jumpAirborne':
            return
        if base.localAvatar.book.isObscured():
            return
        doneStatus = {}
        doneStatus['mode'] = 'StickerBook'
        messenger.send(self.doneEvent, [doneStatus])

    def __handleOptionsEntry(self):
        currentState = base.localAvatar.animFSM.getCurrentState().getName()
        if currentState == 'jumpAirborne':
            return
        if base.localAvatar.book.isObscured():
            return
        doneStatus = {}
        doneStatus['mode'] = 'Options'
        messenger.send(self.doneEvent, [doneStatus])
