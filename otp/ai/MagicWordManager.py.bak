from direct.directnotify import DirectNotifyGlobal
from direct.distributed import DistributedObject
from otp.ai.MagicWordGlobal import *
from toontown.toonbase import ToontownGlobals
from toontown.toon.ToonAccessoryPlacementPanel import ToonAccessoryPlacementPanel
from toontown.toon import ClashClientMagicWords

lastClickedNametag = None

class MagicWordManager(DistributedObject.DistributedObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('MagicWordManager')
    neverDisable = 1

    def generate(self):
        DistributedObject.DistributedObject.generate(self)
        self.accept('magicWord', self.handleMagicWord)

    def disable(self):
        self.ignore('magicWord')
        DistributedObject.DistributedObject.disable(self)

    def handleMagicWord(self, magicWord):
        if magicWord.lower() == '~acc':
            localAvatar = getattr(base, 'localAvatar', None)
            if localAvatar is None or getattr(localAvatar, 'controlManager', None) is None:
                print 'Accessory editor: load a Toon before using ~acc.'
                if localAvatar is not None:
                    try:
                        localAvatar.setSystemMessage(
                            0,
                            'Load a Toon before using ~acc.'
                        )
                    except:
                        pass
                return

            if hasattr(base, 'apPanel') and getattr(base, 'apPanel', None):
                try:
                    base.apPanel.destroy()
                except:
                    pass
                base.apPanel = None
            else:
                base.apPanel = ToonAccessoryPlacementPanel()
            return

        if not self.cr.wantMagicWords:
            return

        if magicWord.startswith(ToontownGlobals.MagicWordTargetPrefix):
            if lastClickedNametag == None:
                target = base.localAvatar
            else:
                target = lastClickedNametag
            magicWord = magicWord[2:]
        if magicWord.startswith(ToontownGlobals.MagicWordInvokerPrefix):
            target = base.localAvatar
            magicWord = magicWord[1:]

        targetId = target.doId

        # ClashClientMagicWords registers commands that must execute on the
        # client, such as tp, music, and sfx.  Do not also send a successfully
        # matched client command to the AI: the AI may return another response
        # (including a fuzzy suggestion for short words such as tp), which
        # creates a second Spellbook alert and notification sound.
        if target == base.localAvatar:
            response = spellbook.process(base.localAvatar, target, magicWord)
            if response is not None:
                self.sendMagicWordResponse(response)
                return

        # Commands not registered on the client still run on the AI normally.
        self.sendUpdate('sendMagicWord', [magicWord, targetId])

    def sendMagicWordResponse(self, response):
        self.notify.info(response)
        base.localAvatar.setSystemMessage(0, 'Spellbook: ' + str(response))
