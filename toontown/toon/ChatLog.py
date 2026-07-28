import re

from toontown.pgui.DirectGui import *
from toontown.pgui import DirectGuiGlobals as DGG
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Sequence, Parallel, LerpPosInterval, LerpScaleInterval
from pandac.PandaModules import TextNode, Vec4, Point3
from toontown.toonbase import ToontownGlobals


class ChatLog(DirectFrame, DirectObject):
    """Clash-style chat display backed by Altis's existing chat network."""

    TAB_MAIN = 'main'
    TAB_WHISPERS = 'whispers'
    TAB_ALERTS = 'alerts'
    TAB_NPC = 'npc'
    TAB_CLUBS = 'clubs'
    MAX_MESSAGE_LENGTH = 100

    def __init__(self):
        DirectFrame.__init__(self, parent=base.a2dTopLeft, relief=None, sortOrder=500)
        DirectObject.__init__(self)

        self.assets = loader.loadModel('phase_3.5/models/gui/chat/chat_panel')
        self.openSfx = loader.loadSfx('phase_3.5/audio/sfx/UI_chat_button_open.ogg')
        self.closeSfx = loader.loadSfx('phase_3.5/audio/sfx/UI_chat_button_close.ogg')
        self.tabSfx = loader.loadSfx('phase_3.5/audio/sfx/UI_chat_button_tab.ogg')
        self.openSfx.setVolume(0.6)
        self.closeSfx.setVolume(0.6)
        self.tabSfx.setVolume(0.6)

        self.isHidden = True
        self.interfaceEnabled = True
        self.currentTab = self.TAB_MAIN
        self.whisperTargetName = None
        self.whisperTargetId = 0
        self.whisperTargetPlayerId = 0
        self.notifications = {
            self.TAB_MAIN: False,
            self.TAB_WHISPERS: False,
            self.TAB_ALERTS: False,
            self.TAB_NPC: False,
            self.TAB_CLUBS: False,
        }
        self.obscuredNormal = False
        self.obscuredSpeedChat = False
        self.obscuredLog = False
        self._displaySequence = Sequence()
        self._notificationSequence = Sequence()
        self._entryFocused = False

        self._makeQuickMenu()
        self._makeDisplay()
        self._addTutorialMessages()
        self._selectTab(self.TAB_MAIN, playSound=False)
        self._closeDisplay(playSound=False, instant=True)

        self.accept(base.CHAT_HOTKEY, self.focusChat)
        self.accept('chat-panel-open', self.open)
        self.accept('chat-panel-close', self.close)

        base.cr.chatLog = self
        print('[ChatSystem] Clash-style chat interface loaded.')
        try:
            if base.localAvatar.chatMgr.fsm.getCurrentState().getName() == 'off':
                self.disableInterface()
        except:
            pass

    def _images(self, prefix, normal='Normal', pressed='Pressed', hover='Hover'):
        return (
            self.assets.find('**/%s%s' % (prefix, normal)),
            self.assets.find('**/%s%s' % (prefix, pressed)),
            self.assets.find('**/%s%s' % (prefix, hover)),
            self.assets.find('**/%s%s' % (prefix, normal)),
        )

    def _makeQuickMenu(self):
        self.quickFrame = DirectFrame(
            parent=self,
            relief=None,
            pos=(0.25, 0, -0.077),
            scale=0.5,
        )

        self.quickSpeedChatButton = DirectButton(
            parent=self.quickFrame,
            relief=None,
            pos=(-0.075, 0, -0.025),
            scale=0.247875,
            image=self._images('Circle_Lightning_', 'N', 'P', 'H'),
            image_scale=(1, 1, 62.0 / 61.0),
            text=('', 'SpeedChat', 'SpeedChat', ''),
            text_pos=(0.7, -0.93),
            text_scale=0.55,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.openSpeedChat,
            pressEffect=0,
        )

        self.quickChatButton = DirectButton(
            parent=self.quickFrame,
            relief=None,
            pos=(0.325, 0, -0.025),
            scale=0.247875,
            image=self._images('Circle_Chat_', 'N', 'P', 'H'),
            image_scale=(1, 1, 62.0 / 61.0),
            text=('', 'Open Chat', 'Open Chat', ''),
            text_pos=(0, -0.93),
            text_scale=0.55,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.open,
            pressEffect=0,
        )

        self.quickNotification = DirectFrame(
            parent=self.quickChatButton,
            relief=None,
            pos=(0.38, 0, -0.17),
            hpr=(0, 0, 5),
            scale=0.001,
            image=self.assets.find('**/Chat-Panel-Notification'),
            image_scale=(0.26644, 1, (66.0 / 26.0) * 0.26644),
        )

    def _makeDisplay(self):
        self.displayFrame = DirectFrame(
            parent=self,
            relief=None,
            pos=(-0.55, 0, -0.275),
        )

        self.backgroundUpper = DirectFrame(
            parent=self.displayFrame,
            relief=None,
            pos=(-0.025, 0, 0.011),
            scale=(0.924, 0.937, 0.937),
            image=self.assets.find('**/Chat-Panel-Tint-Rounded'),
            image_scale=(1, 1, 339.0 / 849.0),
        )
        self.backgroundLower = DirectFrame(
            parent=self.displayFrame,
            relief=None,
            pos=(0.08, 0, -0.219),
            scale=(0.673, 1, 0.181),
            image=self.assets.find('**/Chat-Panel-Tint-Rounded'),
            image_pos=(-0.11836, 0, -0.01301),
            image_scale=(1.47343, 1, 0.52936),
        )
        self.colourPanel = DirectFrame(
            parent=self.displayFrame,
            relief=None,
            frameSize=(-0.499, 0.499, -0.27, 0.21),
            image=self.assets.find('**/Panel_Green'),
            image_scale=(1, 1, 499.0 / 916.0),
        )

        self._makeTabs()
        self._makeLists()
        self._makeWhisperTarget()
        self._makeEntry()
        self._makeDisplayButtons()

    def _makeTabs(self):
        self.tabButtons = {}
        tabData = (
            (self.TAB_MAIN, 'Main', 'Green', -0.40641),
            (self.TAB_WHISPERS, 'Whispers', 'Blue', -0.22214),
            (self.TAB_ALERTS, 'Alerts', 'Red', -0.03787),
            (self.TAB_NPC, 'NPC', 'Yellow', 0.14640),
            (self.TAB_CLUBS, 'Clubs', 'Cyan', 0.33067),
        )
        for tab, label, colour, xPos in tabData:
            button = DirectButton(
                parent=self.displayFrame,
                relief=None,
                pos=(xPos, 0, 0.23299),
                scale=0.18424,
                image=self.assets.find('**/Tab_%s' % colour),
                image_scale=(1, 1, 72.0 / 169.0),
                text=label,
                text_pos=(0, -0.01524),
                text_scale=0.2,
                text_align=TextNode.ACenter,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                command=self._selectTab,
                extraArgs=[tab],
                pressEffect=0,
            )
            notification = DirectFrame(
                parent=button,
                relief=None,
                pos=(0.39, 0, 0),
                scale=0.001,
                image=self.assets.find('**/Chat-Panel-Notification'),
                image_scale=(0.06, 1, (66.0 / 26.0) * 0.06),
            )
            button.notification = notification
            if tab == self.TAB_CLUBS and not getattr(base.localAvatar, 'guildId', 0):
                button['state'] = DGG.DISABLED
                button['text_fg'] = (1, 1, 1, 0.65)
                button['text_shadow'] = (0, 0, 0, 0.65)
            self.tabButtons[tab] = button

    def _makeLists(self):
        self.lists = {}
        self.listItems = {}
        for tab in (self.TAB_MAIN, self.TAB_WHISPERS, self.TAB_ALERTS, self.TAB_NPC, self.TAB_CLUBS):
            chatFrame = DirectScrolledFrame(
                parent=self.displayFrame,
                relief=None,
                autoHideScrollBars=0,
                manageScrollBars=0,
                pos=(-0.025, 0, 0.01),
                scale=0.5,
                frameSize=(-0.91, 0.91, -0.36, 0.36),
                canvasSize=(-0.85, 0.85, -0.36, 0.36),
                verticalScroll_pos=(0.98, 0, 0),
                verticalScroll_scale=(1, 1, 1),
                verticalScroll_frameSize=(-0.05, 0.05, -0.34528, 0.362),
                verticalScroll_relief=None,
                verticalScroll_geom=self.assets.find('**/Scrollbar'),
                verticalScroll_geom_scale=(0.04, 1, 0.74),
                verticalScroll_geom_pos=(-0.00757, 0, 0.00811),
                verticalScroll_resizeThumb=0,
                verticalScroll_scrollSize=0.075,
                verticalScroll_pageSize=0.65,
                verticalScroll_thumb_relief=None,
                verticalScroll_thumb_image=self.assets.find('**/Scrollblock'),
                verticalScroll_thumb_image_scale=(0.10496, 1, 0.156),
                verticalScroll_thumb_image_pos=(-0.00723, 0, 0),
                verticalScroll_thumb_image_color=(1, 1, 1, 1),
            )
            chatFrame.horizontalScroll.hide()
            chatFrame.verticalScroll.incButton.hide()
            chatFrame.verticalScroll.decButton.hide()
            chatFrame.verticalScroll.setValue(1)
            chatFrame.verticalScroll.thumb.hide()
            chatFrame.hide()
            self.lists[tab] = chatFrame
            self.listItems[tab] = []

    def _makeWhisperTarget(self):
        self.whisperTargetFrame = DirectFrame(
            parent=self.displayFrame,
            relief=None,
            pos=(-0.18, 0, -0.177),
            scale=0.6,
            image=self.assets.find('**/Chat-Panel-Whisper'),
            image_scale=(0.52, 1, 0.11),
            text='',
            text_pos=(-0.18, -0.012),
            text_scale=0.055,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            textMayChange=1,
        )
        self.whisperCloseButton = DirectButton(
            parent=self.whisperTargetFrame,
            relief=None,
            pos=(0.39, 0, 0),
            scale=0.11,
            image=self._images('Chat-Panel-WhisperClose-'),
            image_scale=(1, 1, 1),
            command=self.clearWhisperTarget,
            pressEffect=0,
        )
        self.whisperTargetFrame.hide()

    def _makeEntry(self):
        self.entryFrame = DirectFrame(
            parent=self.displayFrame,
            relief=None,
            pos=(-0.28166, 0, -0.23178),
        )
        self.entry = DirectEntry(
            parent=self.entryFrame,
            relief=None,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0),
            width=500,
            numLines=1,
            cursorKeys=1,
            focus=0,
            suppressKeys=1,
            suppressMouse=1,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_scale=0.8,
            entryFont=ToontownGlobals.getInterfaceFont(),
            command=self.sendCurrentMessage,
            focusInCommand=self._focusIn,
            focusOutCommand=self._focusOut,
        )
        self.entryScroll = DirectEntryScroll(
            self.entry,
            parent=self.entryFrame,
            relief=None,
            clipSize=(0, 13.4, -1, 1),
            scale=0.04425,
        )
        self.entry.bind(DGG.TYPE, self._entryChanged)
        self.entry.bind(DGG.ERASE, self._entryChanged)
        try:
            keyName = base.CHAT_HOTKEY.upper()
        except:
            keyName = 'T'
        self.entryHint = DirectLabel(
            parent=self.entryFrame,
            relief=None,
            pos=(0, 0, 0),
            scale=0.0354,
            text="Press '%s' to chat" % keyName,
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 0.42),
            text_shadow=(0, 0, 0, 0.5),
            textMayChange=1,
        )
        self.characterCounter = DirectLabel(
            parent=self.displayFrame,
            relief=None,
            pos=(0.39834, 0, -0.23178),
            text='0/%s' % self.MAX_MESSAGE_LENGTH,
            text_align=TextNode.ARight,
            text_scale=0.022,
            text_fg=(0.7, 0.7, 0.7, 0.65),
            text_shadow=(0, 0, 0, 1),
            textMayChange=1,
        )
        self.history = []
        self.historyIndex = -1
        self.unsentHistoryText = ''

    def _makeDisplayButtons(self):
        xBase = -0.4485
        xIncrement = 0.06146
        self.displaySpeedChatButton = DirectButton(
            parent=self.displayFrame,
            relief=None,
            pos=(xBase, 0, -0.221),
            scale=0.06346,
            image=self._images('Bubble_'),
            image_scale=(1, 1, 62.5 / 61.0),
            text=('', 'SpeedChat', 'SpeedChat', ''),
            text_pos=(1, -1.3),
            text_scale=0.65,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.openSpeedChat,
            pressEffect=0,
        )
        self.stickerButton = DirectButton(
            parent=self.displayFrame,
            relief=None,
            pos=(xBase + xIncrement, 0, -0.221),
            scale=0.06346,
            image=self._images('Star_'),
            image_scale=(1, 1, 62.5 / 61.0),
            text=('', 'Stickers', 'Stickers', ''),
            text_pos=(0, -1.3),
            text_scale=0.65,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self._showStickerUnavailable,
            pressEffect=0,
        )
        self.uniteButton = DirectButton(
            parent=self.displayFrame,
            relief=None,
            pos=(xBase + (xIncrement * 2), 0, -0.221),
            scale=0.06346,
            image=self._images('Fist_'),
            image_scale=(1, 1, 62.5 / 61.0),
            text=('', 'Unites', 'Unites', ''),
            text_pos=(0, -1.3),
            text_scale=0.65,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.openUnites,
            pressEffect=0,
        )
        self.sendButton = DirectButton(
            parent=self.displayFrame,
            relief=None,
            pos=(0.44818, 0, -0.221),
            scale=0.06346,
            image=self._images('Chat_'),
            image_scale=(1, 1, 62.5 / 61.0),
            text=('', 'Send', 'Send', ''),
            text_pos=(0, -1.3),
            text_scale=0.65,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.sendCurrentMessage,
            pressEffect=0,
        )
        self.closeButton = DirectButton(
            parent=self.displayFrame,
            relief=None,
            pos=(0.46172, 0, 0.23731),
            scale=0.05409,
            image=self._images('Exit_'),
            image_scale=(1, 1, 0.97842),
            text=('', 'Close', 'Close', ''),
            text_pos=(2.5, -0.22),
            text_scale=0.8,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.close,
            pressEffect=0,
        )

    def _playSfx(self, sound):
        try:
            base.playSfx(sound)
        except:
            try:
                sound.play()
            except:
                pass

    def open(self, focus=False):
        if not self.interfaceEnabled or self.obscuredLog:
            return
        self._openDisplay(playSound=self.isHidden)
        if focus:
            self.entry['focus'] = 1

    def close(self):
        self._closeDisplay(playSound=not self.isHidden)

    def toggle(self):
        if self.isHidden:
            self.open()
        else:
            self.close()

    def focusChat(self):
        if self.obscuredNormal:
            return
        if self.currentTab in (self.TAB_ALERTS, self.TAB_NPC):
            self._selectTab(self.TAB_MAIN)
        elif self.currentTab == self.TAB_CLUBS and not getattr(base.localAvatar, 'guildId', 0):
            self._selectTab(self.TAB_MAIN)
        self.open(focus=True)

    def _openDisplay(self, playSound=True, instant=False):
        self.isHidden = False
        self.displayFrame.show()
        self.quickFrame.show()
        self.accept('wheel_up', self._scrollCurrent, [-1])
        self.accept('wheel_down', self._scrollCurrent, [1])
        self._displaySequence.pause()
        if instant:
            self.displayFrame.setPos(0.51, 0, -0.275)
            self.quickFrame.setPos(0.25, 0, 0.08)
        else:
            self._displaySequence = Parallel(
                LerpPosInterval(self.displayFrame, 0.28, Point3(0.51, 0, -0.275), blendType='easeInOut'),
                LerpPosInterval(self.quickFrame, 0.28, Point3(0.25, 0, 0.08), blendType='easeInOut'),
            )
            self._displaySequence.start()
        if playSound:
            self._playSfx(self.openSfx)
        self._clearNotification(self.currentTab)

    def _closeDisplay(self, playSound=True, instant=False):
        self.isHidden = True
        self.ignore('wheel_up')
        self.ignore('wheel_down')
        self.removeFocus()
        try:
            chatMgr = base.localAvatar.chatMgr
            if hasattr(chatMgr, 'closePanelMenus'):
                chatMgr.closePanelMenus()
        except:
            pass
        self._displaySequence.pause()
        if instant:
            self.displayFrame.setPos(-0.55, 0, -0.275)
            self.quickFrame.setPos(0.25, 0, -0.077)
        else:
            self._displaySequence = Parallel(
                LerpPosInterval(self.displayFrame, 0.28, Point3(-0.55, 0, -0.275), blendType='easeInOut'),
                LerpPosInterval(self.quickFrame, 0.28, Point3(0.25, 0, -0.077), blendType='easeInOut'),
            )
            self._displaySequence.start()
        if playSound:
            self._playSfx(self.closeSfx)

    def _selectTab(self, tab, playSound=True):
        if tab not in self.lists:
            return
        self.currentTab = tab
        for tabName, chatList in self.lists.items():
            if tabName == tab:
                chatList.show()
            else:
                chatList.hide()
        for tabName, button in self.tabButtons.items():
            button['image_color'] = (1, 1, 1, 1) if tabName == tab else (0.74, 0.74, 0.74, 1)

        panelName = {
            self.TAB_MAIN: 'Panel_Green',
            self.TAB_WHISPERS: 'Panel_Blue',
            self.TAB_ALERTS: 'Panel_Red',
            self.TAB_NPC: 'Panel_Yellow',
            self.TAB_CLUBS: 'Panel_Cyan',
        }[tab]
        scrollColour = {
            self.TAB_MAIN: (0.325, 0.784, 0.278, 1),
            self.TAB_WHISPERS: (0.314, 0.392, 0.749, 1),
            self.TAB_ALERTS: (0.769, 0.353, 0.294, 1),
            self.TAB_NPC: (0.616, 0.588, 0.137, 1),
            self.TAB_CLUBS: (0.278, 0.702, 0.784, 1),
        }[tab]
        self.colourPanel['image'] = self.assets.find('**/%s' % panelName)
        self.lists[tab].verticalScroll['geom_color'] = scrollColour
        self._clearNotification(tab)
        self._updateEntryState()
        if playSound:
            self._playSfx(self.tabSfx)

    def _updateEntryState(self):
        canSend = True
        try:
            keyName = base.CHAT_HOTKEY.upper()
        except:
            keyName = 'T'
        hint = "Press '%s' to chat" % keyName
        if self.currentTab == self.TAB_ALERTS:
            canSend = False
            hint = 'Alerts cannot be replied to.'
        elif self.currentTab == self.TAB_NPC:
            canSend = False
            hint = 'NPC messages cannot be replied to.'
        elif self.currentTab == self.TAB_CLUBS:
            if getattr(base.localAvatar, 'guildId', 0):
                hint = 'Chat with your Club...'
            else:
                canSend = False
                hint = 'You are not in a Club.'
        elif self.currentTab == self.TAB_WHISPERS and not self.whisperTargetId and not self.whisperTargetPlayerId:
            canSend = False
            hint = 'Select a Toon to whisper to.'
        elif self.currentTab == self.TAB_WHISPERS and self.whisperTargetName:
            hint = 'Whisper to %s...' % self.whisperTargetName

        self.entryHint['text'] = hint
        self.entry['state'] = DGG.NORMAL if canSend and not self.obscuredNormal else DGG.DISABLED
        self.sendButton['state'] = DGG.NORMAL if canSend and not self.obscuredNormal else DGG.DISABLED
        self._entryChanged(None)

    def _entryChanged(self, unused):
        try:
            text = self.entry.get(plain=True)
        except:
            text = self.entry.get()
        if len(text) > self.MAX_MESSAGE_LENGTH:
            text = text[:self.MAX_MESSAGE_LENGTH]
            self.entry.set(text)
            self.entry.setCursorPosition(len(text))
        textLength = len(text)
        self.characterCounter['text'] = '%s/%s' % (textLength, self.MAX_MESSAGE_LENGTH)
        if textLength >= int(self.MAX_MESSAGE_LENGTH * 0.9):
            self.characterCounter['text_fg'] = (1, 0, 0, 0.8)
        elif textLength >= int(self.MAX_MESSAGE_LENGTH * 0.7):
            self.characterCounter['text_fg'] = (1, 0.92, 0, 0.7)
        else:
            self.characterCounter['text_fg'] = (0.7, 0.7, 0.7, 0.65)
        if text or self._entryFocused:
            self.entryHint.hide()
        else:
            self.entryHint.show()

    def _focusIn(self):
        self._entryFocused = True
        self.entry.accept('escape', self.removeFocus)
        self.entry.accept('arrow_up', self._historyUp)
        self.entry.accept('arrow_down', self._historyDown)
        try:
            if base.wantCustomControls:
                base.localAvatar.controlManager.disableWASD()
            else:
                base.localAvatar.disableControls()
        except:
            pass
        self._entryChanged(None)

    def _focusOut(self):
        self._entryFocused = False
        self.entry.ignore('escape')
        self.entry.ignore('arrow_up')
        self.entry.ignore('arrow_down')
        try:
            if base.wantCustomControls:
                base.localAvatar.controlManager.enableWASD()
            else:
                base.localAvatar.enableControls()
        except:
            pass
        self._entryChanged(None)

    def removeFocus(self):
        try:
            self.entry['focus'] = 0
        except:
            pass

    def sendCurrentMessage(self, unused=None):
        if self.currentTab in (self.TAB_ALERTS, self.TAB_NPC):
            return
        try:
            text = self.entry.get(plain=True).strip()
        except:
            text = self.entry.get().strip()
        if not text:
            return
        text = text[:self.MAX_MESSAGE_LENGTH]

        chatMgr = getattr(base.localAvatar, 'chatMgr', None)
        if not chatMgr or not hasattr(chatMgr, 'sendPanelMessage'):
            return
        if chatMgr.sendPanelMessage(text):
            self.history.insert(0, text)
            self.history = self.history[:20]
            self.historyIndex = -1
            self.unsentHistoryText = ''
            self.entry.set('')
            self._entryChanged(None)

    def _historyUp(self):
        if not self.history:
            return
        if self.historyIndex == -1:
            try:
                self.unsentHistoryText = self.entry.get(plain=True)
            except:
                self.unsentHistoryText = self.entry.get()
        self.historyIndex = min(self.historyIndex + 1, len(self.history) - 1)
        self.entry.set(self.history[self.historyIndex])
        self.entry.setCursorPosition(len(self.history[self.historyIndex]))
        self._entryChanged(None)

    def _historyDown(self):
        if self.historyIndex == -1:
            return
        self.historyIndex -= 1
        text = self.unsentHistoryText if self.historyIndex == -1 else self.history[self.historyIndex]
        self.entry.set(text)
        self.entry.setCursorPosition(len(text))
        self._entryChanged(None)

    def openSpeedChat(self):
        if self.obscuredSpeedChat:
            return
        chatMgr = getattr(base.localAvatar, 'chatMgr', None)
        if chatMgr and hasattr(chatMgr, 'openPanelSpeedChat'):
            chatMgr.openPanelSpeedChat()

    def openUnites(self):
        if self.obscuredSpeedChat:
            return
        chatMgr = getattr(base.localAvatar, 'chatMgr', None)
        if chatMgr and hasattr(chatMgr, 'openPanelUnites'):
            chatMgr.openPanelUnites()

    def setWhisperTarget(self, avatarName, avatarId, playerId=0):
        self.whisperTargetName = avatarName
        self.whisperTargetId = avatarId or 0
        self.whisperTargetPlayerId = playerId or 0
        self.whisperTargetFrame['text'] = avatarName or 'Whisper'
        self.whisperTargetFrame.show()
        self._selectTab(self.TAB_WHISPERS, playSound=False)
        self.open(focus=True)

    def clearWhisperTarget(self):
        self.whisperTargetName = None
        self.whisperTargetId = 0
        self.whisperTargetPlayerId = 0
        self.whisperTargetFrame.hide()
        self._updateEntryState()
        try:
            chatMgr = base.localAvatar.chatMgr
            stateName = chatMgr.fsm.getCurrentState().getName()
            if stateName in ('whisperSpeedChat', 'whisperSpeedChatPlayer'):
                chatMgr.fsm.request('mainMenu')
        except:
            pass

    def getWhisperTarget(self):
        return (self.whisperTargetName, self.whisperTargetId, self.whisperTargetPlayerId)

    def _classifyMessage(self, msg):
        lower = msg.lower()
        if 'coggray' in lower or 'npc message' in lower:
            return self.TAB_NPC
        if 'system message' in lower or 'game message' in lower or 'toon hq:' in lower or 'orangetext' in lower:
            return self.TAB_ALERTS
        if ' whispers' in lower or 'whispers:' in lower:
            return self.TAB_WHISPERS
        return self.TAB_MAIN

    def addToLog(self, msg, avId=0, category=None):
        if not msg:
            return
        msg = msg.replace('\r', ' ')
        tab = category or self._classifyMessage(msg)
        if tab not in self.lists:
            tab = self.TAB_MAIN

        targetTabs = [self.TAB_MAIN]
        if tab != self.TAB_MAIN:
            targetTabs.append(tab)

        for targetTab in targetTabs:
            self._addMessageItem(targetTab, msg, avId)

        if self.isHidden or self.currentTab != self.TAB_MAIN:
            self._showNotification(self.TAB_MAIN)
        if tab != self.TAB_MAIN and (self.isHidden or self.currentTab != tab):
            self._showNotification(tab)

    def _stripTextProperties(self, text):
        try:
            text = re.sub('\x01[^\x01]*\x01', '', text)
            return text.replace('\x02', '')
        except:
            return text

    def _estimateLineCount(self, text):
        text = self._stripTextProperties(text)
        totalLines = 0
        for paragraph in text.split('\n'):
            words = paragraph.split(' ')
            if not words:
                totalLines += 1
                continue
            currentLength = 0
            paragraphLines = 1
            for word in words:
                wordLength = len(word)
                if currentLength and currentLength + 1 + wordLength > 57:
                    paragraphLines += 1
                    currentLength = wordLength
                else:
                    currentLength += wordLength + (1 if currentLength else 0)
            totalLines += paragraphLines
        return max(1, totalLines)

    def _addMessageItem(self, tab, msg, avId=0, textColor=None, tutorial=False):
        if tab not in self.lists:
            return
        options = {
            'parent': self.lists[tab].getCanvas(),
            'relief': None,
            'frameColor': (0, 0, 0, 0),
            'frameSize': (-0.85, 0.85, -0.05, 0.05),
            'text': msg,
            'text_scale': 0.064,
            'text_pos': (-0.84, 0),
            'text_style': 3,
            'text_align': TextNode.ALeft,
            'text_wordwrap': 26.5,
            'text_shadow': (0, 0, 0, 1),
            'textMayChange': 0,
        }
        if textColor is not None:
            options['text_fg'] = textColor
        if avId:
            options['command'] = self.buttonizeIt
            options['extraArgs'] = [avId]
        item = DirectButton(**options)
        item._chatHeight = 0.069 * self._estimateLineCount(msg)
        item._chatTutorial = bool(tutorial)
        self.listItems[tab].append(item)

        while len(self.listItems[tab]) > 60:
            removeIndex = None
            for index, oldItem in enumerate(self.listItems[tab]):
                if not getattr(oldItem, '_chatTutorial', False):
                    removeIndex = index
                    break
            if removeIndex is None:
                break
            oldItem = self.listItems[tab].pop(removeIndex)
            try:
                oldItem.destroy()
            except:
                pass

        self._layoutMessages(tab, scrollToBottom=True)

    def _layoutMessages(self, tab, scrollToBottom=False):
        chatFrame = self.lists[tab]
        currentPosition = 0.305
        for item in self.listItems[tab]:
            item.setPos(0, 0, currentPosition)
            currentPosition -= getattr(item, '_chatHeight', 0.069)

        lowerBound = min(currentPosition + 0.025, -0.36)
        chatFrame['canvasSize'] = (-0.85, 0.85, lowerBound, 0.36)
        chatFrame.setCanvasSize()
        if lowerBound == -0.36:
            chatFrame.verticalScroll.thumb.hide()
        else:
            chatFrame.verticalScroll.thumb.show()
        if scrollToBottom:
            chatFrame.verticalScroll.setValue(1)

    def _addTutorialMessages(self):
        tutorialColour = (0.72, 0.72, 0.72, 0.95)
        tutorials = {
            self.TAB_MAIN: "World messages are shown here. Messages from the\nWhispers, Alerts, NPC and Clubs tabs are also shown here.\nMain combines every supported Altis chat channel.",
            self.TAB_WHISPERS: 'Whispers sent to and received from other Toons are shown here.',
            self.TAB_ALERTS: 'System alerts and announcements are shown here.',
            self.TAB_NPC: 'Cog and NPC dialogue is shown here.',
            self.TAB_CLUBS: 'Club messages are shown here when club chat is available.',
        }
        for tab, text in tutorials.items():
            self._addMessageItem(tab, text, textColor=tutorialColour, tutorial=True)

    def _scrollCurrent(self, amount):
        if self.isHidden or self.currentTab not in self.lists:
            return
        try:
            self.lists[self.currentTab].verticalScroll.scrollStep(amount)
            messenger.send('wakeup')
        except:
            pass

    def _showStickerUnavailable(self):
        if getattr(self, '_stickerNoticeShown', False):
            return
        self._stickerNoticeShown = True
        self.addToLog(
            '\1orangeText\1System Message: Stickers are not enabled in this Altis build.\2',
            category=self.TAB_ALERTS,
        )

    def _showNotification(self, tab):
        self.notifications[tab] = True
        if tab in self.tabButtons:
            self.tabButtons[tab].notification.setScale(0.06)
        self._refreshQuickNotification()

    def _clearNotification(self, tab):
        self.notifications[tab] = False
        if tab in self.tabButtons:
            self.tabButtons[tab].notification.setScale(0.001)
        self._refreshQuickNotification()

    def _refreshQuickNotification(self):
        wantNotification = any(self.notifications.values())
        self._notificationSequence.pause()
        targetScale = 1.0 if wantNotification else 0.001
        self._notificationSequence = Sequence(
            LerpScaleInterval(self.quickNotification, 0.18, targetScale, blendType='easeInOut')
        )
        self._notificationSequence.start()

    def setObscured(self, normal, speedChat, chatLog=False):
        self.obscuredNormal = bool(normal)
        self.obscuredSpeedChat = bool(speedChat)
        self.obscuredLog = bool(chatLog)
        self.quickSpeedChatButton['state'] = DGG.DISABLED if self.obscuredSpeedChat else DGG.NORMAL
        self.quickChatButton['state'] = DGG.DISABLED if self.obscuredLog else DGG.NORMAL
        self.displaySpeedChatButton['state'] = DGG.DISABLED if self.obscuredSpeedChat else DGG.NORMAL
        self._updateEntryState()
        if self.obscuredNormal and self.obscuredSpeedChat and self.obscuredLog:
            self.disableInterface()
        else:
            self.enableInterface()

    def disableInterface(self):
        self.interfaceEnabled = False
        self.removeFocus()
        self.quickFrame.hide()
        self.displayFrame.hide()

    def enableInterface(self):
        self.interfaceEnabled = True
        self.quickFrame.show()
        self.displayFrame.show()
        if self.isHidden:
            self.displayFrame.setPos(-0.55, 0, -0.275)
            self.quickFrame.setPos(0.25, 0, -0.077)
        else:
            self.displayFrame.setPos(0.51, 0, -0.275)
            self.quickFrame.setPos(0.25, 0, 0.08)

    def updateTransparency(self, transparency):
        alpha = max(0.0, min(1.0, transparency))
        self.backgroundUpper['image_color'] = (1, 1, 1, alpha)
        self.backgroundLower['image_color'] = (1, 1, 1, alpha)
        self.colourPanel['image_color'] = (1, 1, 1, alpha)

    def buttonizeIt(self, avId):
        if not avId:
            return
        av = base.cr.doId2do.get(avId)
        if av:
            try:
                av.clickedNametag()
            except:
                pass

    def stop(self):
        self.ignoreAll()
        self._displaySequence.pause()
        self._notificationSequence.pause()
        self.removeFocus()
        if getattr(base.cr, 'chatLog', None) is self:
            base.cr.chatLog = None
        try:
            self.assets.removeNode()
        except:
            pass
        self.destroy()
