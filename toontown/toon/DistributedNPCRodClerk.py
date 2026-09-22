"""
DistributedNPCRodClerk -- rewritten to use Clash's generic NPC item-shop
system (toontown/shop/, toontown/toon/npc/shop/) instead of the old
RodBuyGUI/setMovie-based buying flow. Sells items from
RodShopGlobals.RodShopItems.

Pattern adapted directly from DistributedNPCTailor.py. RodBuyGUI.py is no
longer used by this class (left in place, unused, in case anything else
still references it) -- NPCToonShopGUI replaces it.
"""
from panda3d.core import Vec3

from toontown.toon.DistributedNPCToonBase import *
from toontown.toonbase.CooldownManager import CooldownManager
from toontown.toonbase import TTLocalizer
from toontown.toon.npc.shop.gui.NPCToonShopGUI import NPCToonShopGUI


class DistributedNPCRodClerk(DistributedNPCToonBase):
    # Constant codes to use for decrypting chat phrases upon certain interactions
    START_INTERACT_CODE = 1
    EXIT_INTERACT_CODE = 2

    CLIENT_SIDE_CONTEXTS = (
        START_INTERACT_CODE,
        EXIT_INTERACT_CODE
    )

    def __init__(self, cr):
        DistributedNPCToonBase.__init__(self, cr)
        self.npcType = 'Rod Salesman'
        self.storeGui = None
        self.interactCooldown = CooldownManager(2)
        self.responseCooldown = CooldownManager(3)

    def disable(self):
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('__popupStoreGUI'))
        taskMgr.remove(self.uniqueName('lerpCamera'))
        if self.storeGui:
            self.storeGui.destroy()
            self.storeGui = None
        DistributedNPCToonBase.disable(self)

    def announceGenerate(self):
        DistributedNPCToonBase.announceGenerate(self)
        self.setHat(18, 0, 0)

    def handleCollisionSphereEnter(self, collEntry):
        if not self.interactCooldown.check(base.localAvatar.doId).outcome:
            return

        # Freeze the toon and make them look at us
        base.cr.playGame.getPlace().setState('Stopped')
        self.lookAt(base.localAvatar)

        TRANSITION_LENGTH = 1.0
        # Do a pretty camera pan into opening the GUI
        camera.posQuatInterval(TRANSITION_LENGTH, Vec3(-5, 9, self.getHeight() - 0.5), Vec3(-150, -2, 0), other=self,
                               blendType='easeOut', name=self.uniqueName('lerpCamera')).start()

        taskMgr.doMethodLater(TRANSITION_LENGTH, self.__popupStoreGUI, self.uniqueName('__popupStoreGUI'))

        # Tell server we interacted with a ctx code of 1
        self.sendUpdate('toonInteracted', [self.START_INTERACT_CODE])

    def __popupStoreGUI(self, _=None):
        self.storeGui = NPCToonShopGUI(aspect2d, npc=self)

    def doExit(self):
        # Tell the server we exited
        self.sendUpdate('toonInteracted', [self.EXIT_INTERACT_CODE])

    def handleBuyResponse(self, code):
        if self.storeGui:
            self.setChatAbsolute(TTLocalizer.NPCStoreResponses[code], CFSpeech | CFTimeout)
            self.cr.chatManager.sendSystemMessageLocally(TTLocalizer.NPCStoreResponses[code], senderName=self.getName())
            self.storeGui.updatePage()

    # Called from AI, given avId that triggered this interaction, in which context, and which phrase
    def handleInteraction(self, ctxCode, phraseId):
        phraseChoices = TTLocalizer.NPCStoreEnterExitResponses[ctxCode]
        phrase = phraseChoices[phraseId]
        phrase = phrase.replace('_avName_', base.localAvatar.getName())
        self.setChatAbsolute(phrase, CFSpeech | CFTimeout)
