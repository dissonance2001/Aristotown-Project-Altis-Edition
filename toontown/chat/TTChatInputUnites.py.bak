from direct.showbase import DirectObject
from toontown.pgui import DirectGuiGlobals as DGG
from otp.speedchat.SpeedChat import SpeedChat
from otp.speedchat.SpeedChatTypes import SCMenu, SCMenuHolder, SCColorScheme
from otp.speedchat import SpeedChatGlobals
from toontown.speedchat.TTSCResistanceTerminal import TTSCResistanceTerminal, TTSCResistanceMsgEvent
from toontown.chat import ResistanceChat
from toontown.shtiker.OptionsPage import speedChatStyles
from toontown.toonbase import TTLocalizer


class TTChatInputUnites(DirectObject.DirectObject):

    def __init__(self, chatMgr):
        DirectObject.DirectObject.__init__(self)
        self.chatMgr = chatMgr
        self.isOpen = False
        self.availableCount = 0
        self.uniteMenu = SpeedChat(
            name='Unites-Menu',
            backgroundModelName='phase_3/models/gui/ChatPanel',
            guiModelName='phase_3.5/models/gui/speedChatGui')
        self.uniteMenu.setScale(TTLocalizer.TTCISCspeedChat)
        self.uniteMenu.setBin('gui-popup', 0)
        self.uniteMenu.setTopLevelOverlap(TTLocalizer.TTCISCtopLevelOverlap)
        self._updateStyle()
        self.accept('resistanceMessagesChanged', self._rebuild)
        self.accept('SpeedChatStyleChange', self._updateStyle)
        self.accept(self.uniteMenu.getEventName(TTSCResistanceMsgEvent), self._handleUnite)
        self._rebuild()
        self.uniteMenu.reparentTo(hidden)

    def delete(self):
        self.hide()
        self.ignoreAll()
        self.uniteMenu.destroy()
        del self.uniteMenu
        del self.chatMgr

    def _updateStyle(self):
        try:
            nameKey, arrowColor, rolloverColor, frameColor = speedChatStyles[base.localAvatar.getSpeedChatStyleIndex()]
            colorScheme = SCColorScheme(
                arrowColor=arrowColor,
                rolloverColor=rolloverColor,
                frameColor=frameColor)
        except:
            colorScheme = SCColorScheme()
        self.uniteMenu.setColorScheme(colorScheme)

    def _rebuild(self):
        self.uniteMenu.clearMenu()
        self.availableCount = 0
        try:
            localAvatar = base.localAvatar
        except:
            return

        for menuIndex in ResistanceChat.resistanceMenu:
            menu = SCMenu()
            for itemIndex in ResistanceChat.getItems(menuIndex):
                textId = ResistanceChat.encodeId(menuIndex, itemIndex)
                charges = localAvatar.getResistanceMessageCharges(textId)
                if charges > 0:
                    menu.append(TTSCResistanceTerminal(textId, charges))
                    self.availableCount += charges

            textId = ResistanceChat.encodeId(menuIndex, 0)
            menuName = ResistanceChat.getMenuName(textId)
            self.uniteMenu.append(SCMenuHolder(menuName, menu))

        self.uniteMenu.finalizeAll()

    def show(self):
        if self.isOpen:
            self.hide()
            return

        self._rebuild()
        if self.availableCount <= 0:
            chatLog = getattr(base.cr, 'chatLog', None)
            if chatLog:
                chatLog.addToLog(
                    '\1playerGreen\1System Message\2: You do not have any Unites available.',
                    category=chatLog.TAB_ALERTS)
            return

        self.isOpen = True
        self.acceptOnce('mouse1', self._handleOutsideClick)
        self.acceptOnce('mouse3', self._handleOutsideClick)
        self.acceptOnce(
            self.uniteMenu.getEventName(SpeedChatGlobals.SCTerminalSelectedEvent),
            self.hide)
        self.uniteMenu.reparentTo(base.a2dpTopLeft, DGG.FOREGROUND_SORT_INDEX)
        # Keep the Unite list vertically aligned with SpeedChat, but shifted
        # slightly to the right so the two shortcut menus have distinct anchors.
        chatLog = getattr(getattr(base, 'cr', None), 'chatLog', None)
        if chatLog is not None and not getattr(chatLog, 'isHidden', True):
            self.uniteMenu.setPos(0.1675, 0, -0.58)
        else:
            self.uniteMenu.setPos(0.275, 0, -0.184)
        self.uniteMenu.show()
        self.uniteMenu.enter()

    def hide(self, unused=None):
        if not self.isOpen:
            return
        self.isOpen = False
        self.ignore('mouse1')
        self.ignore('mouse3')
        self.ignore(self.uniteMenu.getEventName(SpeedChatGlobals.SCTerminalSelectedEvent))
        self.uniteMenu.exit()
        self.uniteMenu.reparentTo(hidden)

    def _handleOutsideClick(self):
        self.hide()

    def _handleUnite(self, textId):
        noUnites = False
        try:
            if 'noUnites' in base.localAvatar.battleConditions:
                noUnites = True
        except:
            pass
        try:
            if base.localAvatar.hasToonStatusEffect('cooldown'):
                noUnites = True
        except:
            pass

        if not noUnites:
            self.chatMgr.sendSCResistanceChatMessage(textId)
        self.hide()
