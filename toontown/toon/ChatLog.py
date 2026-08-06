import re

from toontown.pgui.DirectGui import *
from toontown.pgui import DirectGuiGlobals as DGG
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Sequence, Parallel, LerpPosInterval, LerpScaleInterval
from pandac.PandaModules import TextNode, Vec4, Point3, CullBinManager, KeyboardButton
from toontown.toonbase import ToontownGlobals
from toontown.stickers import StickerMenu
from toontown.toon.AltisCommandShortcuts import getCommandShortcuts


class ChatLog(DirectFrame, DirectObject):
    """Aristotown-style chat display backed by Aristotown's existing chat network."""

    TAB_MAIN = 'main'
    TAB_WHISPERS = 'whispers'
    TAB_ALERTS = 'alerts'
    TAB_NPC = 'npc'
    TAB_CLUBS = 'clubs'
    MAX_MESSAGE_LENGTH = 100

    def __init__(self):
        # Build the complete chat interface beneath ``hidden``.  LocalToon can
        # create ChatLog while ToontownLoader is still drawing a loading frame;
        # constructing it directly below a2dTopLeft makes the four quick-menu
        # buttons briefly appear over that loading screen.
        self._interfaceParent = base.a2dTopLeft
        self._bulkLoading = bool(getattr(loader, 'inBulkBlock', None))
        DirectFrame.__init__(self, parent=hidden, relief=None, sortOrder=500)
        DirectObject.__init__(self)

        # Corporate Clash draws the tab images one layer behind the main panel,
        # while keeping their text above it.  Ensure Aristotown has the same fixed
        # GUI bin available before assigning those layers.
        cbm = CullBinManager.getGlobalPtr()
        if cbm.findBin('sorted-gui-popup') < 0:
            cbm.addBin('sorted-gui-popup', CullBinManager.BTFixed, 70)
        self.setBin('sorted-gui-popup', 1000)

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
        self.stickerMenu = StickerMenu.StickerMenu(self, self.assets)
        self._addTutorialMessages()
        self._selectTab(self.TAB_MAIN, playSound=False)
        self._closeDisplay(playSound=False, instant=True)

        self.accept(base.CHAT_HOTKEY, self.focusChat)
        self.accept('c', self.chatHotkey)
        self.accept('mouse1', self._handleMouseClickFocus)
        self.accept('chat-panel-open', self.open)
        self.accept('chat-panel-close', self.close)
        self.accept('club-state-updated', self._clubStateUpdated)
        self.accept('altis-bulk-load-begin', self._handleBulkLoadBegin)
        self.accept('altis-bulk-load-end', self._handleBulkLoadEnd)

        base.cr.chatLog = self
        print('[ChatSystem] Aristotown chat interface loaded.')
        try:
            if base.localAvatar.chatMgr.fsm.getCurrentState().getName() == 'off':
                self.disableInterface()
        except:
            pass
        self._refreshInterfaceVisibility()

    def _handleBulkLoadBegin(self):
        self._bulkLoading = True
        self.removeFocus()
        if getattr(self, 'stickerMenu', None):
            self.stickerMenu.hideMenu()
        try:
            chatMgr = base.localAvatar.chatMgr
            if hasattr(chatMgr, 'closePanelMenus'):
                chatMgr.closePanelMenus()
        except:
            pass
        self.reparentTo(hidden)

    def _handleBulkLoadEnd(self):
        # ToontownLoader emits this after ToontownLoadingScreen.end() has hidden
        # the loading GUI, so the normal chat HUD can safely return now.
        self._bulkLoading = False
        self._refreshInterfaceVisibility()

    def _refreshInterfaceVisibility(self):
        if not self.interfaceEnabled or self._bulkLoading:
            self.reparentTo(hidden)
            return

        self.reparentTo(self._interfaceParent)
        self.quickFrame.show()
        self.displayFrame.show()
        if self.isHidden:
            self.displayFrame.setPos(-0.55, 0, -0.275)
            self.quickFrame.setPos(0.25, 0, -0.077)
        else:
            self.displayFrame.setPos(0.51, 0, -0.275)
            self.quickFrame.setPos(0.25, 0, 0.08)

    def _images(self, prefix, normal='Normal', pressed='Pressed', hover='Hover'):
        return (
            self.assets.find('**/%s%s' % (prefix, normal)),
            self.assets.find('**/%s%s' % (prefix, pressed)),
            self.assets.find('**/%s%s' % (prefix, hover)),
            self.assets.find('**/%s%s' % (prefix, normal)),
        )

    def _clubStateUpdated(self, club):
        self.setClubAvailable(bool(club))

    def setClubAvailable(self, available):
        try:
            button = self.tabButtons.get(self.TAB_CLUBS)
        except:
            button = None
        if button is not None:
            button['state'] = DGG.NORMAL if available else DGG.DISABLED
            alpha = 1.0 if available else 0.65
            button['text_fg'] = (1, 1, 1, alpha)
            button['text_shadow'] = (0, 0, 0, alpha)
        if not available and self.currentTab == self.TAB_CLUBS:
            self._selectTab(self.TAB_MAIN, playSound=False)
        self._updateEntryState()

    def _makeQuickMenu(self):
        self.quickFrame = DirectFrame(
            parent=self,
            relief=None,
            pos=(0.25, 0, -0.077),
            scale=0.5,
        )

        # Match Corporate Clash's exact four-button quick-menu layout.
        quickButtonScale = 0.247875
        quickButtonZ = -0.025
        quickButtonPositions = (-0.325, -0.0583333333, 0.2083333333, 0.475)

        self.quickSpeedChatButton = DirectButton(
            parent=self.quickFrame,
            relief=None,
            pos=(quickButtonPositions[0], 0, quickButtonZ),
            scale=quickButtonScale,
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

        self.quickStickerButton = DirectButton(
            parent=self.quickFrame,
            relief=None,
            pos=(quickButtonPositions[1], 0, quickButtonZ),
            scale=quickButtonScale,
            image=self._images('Circle_Star_', 'N', 'P', 'H'),
            image_scale=(1, 1, 62.0 / 61.0),
            text=('', 'Stickers', 'Stickers', ''),
            text_pos=(0, -0.93),
            text_scale=0.55,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.openStickers,
            pressEffect=0,
        )

        self.quickUniteButton = DirectButton(
            parent=self.quickFrame,
            relief=None,
            pos=(quickButtonPositions[2], 0, quickButtonZ),
            scale=quickButtonScale,
            image=self._images('Circle_Fist_', 'N', 'P', 'H'),
            image_scale=(1, 1, 62.0 / 61.0),
            text=('', 'Unites', 'Unites', ''),
            text_pos=(0, -0.93),
            text_scale=0.55,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            command=self.openUnites,
            pressEffect=0,
        )

        self.quickChatButton = DirectButton(
            parent=self.quickFrame,
            relief=None,
            pos=(quickButtonPositions[3], 0, quickButtonZ),
            scale=quickButtonScale,
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
        self._makeCommandShortcuts()
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
            # The graphic stays behind the main panel, exactly like Clash.
            # Its label remains above the panel so every tab name is readable.
            button.setBin('sorted-gui-popup', 999)
            for stateIndex in range(4):
                try:
                    button.component('text%s' % stateIndex).setBin('sorted-gui-popup', 1001)
                except:
                    pass

            notification = DirectFrame(
                parent=button,
                relief=None,
                pos=(0.39, 0, 0),
                scale=0.001,
                image=self.assets.find('**/Chat-Panel-Notification'),
                image_scale=(0.06, 1, (66.0 / 26.0) * 0.06),
            )
            notification.setBin('sorted-gui-popup', 1002)
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

    def _makeCommandShortcuts(self):
        self.commandShortcuts = getCommandShortcuts(getattr(base, 'localAvatar', None))
        self._commandLookup = {}
        for command in self.commandShortcuts:
            for invokeWord in (command['name'],) + tuple(command.get('aliases', ())):
                self._commandLookup[invokeWord.lower()] = command

        self._commandMode = 'hidden'
        self._commandMatches = []
        self._commandSelectionIndex = -1
        self._commandVisibleStart = 0
        self._commandSelectionKind = 'command'
        self._commandInvokeWord = ''
        self._commandTargetBase = ''
        self._commandPrefix = '/'
        self._commandExact = None

        self.commandFrame = DirectFrame(
            parent=self.displayFrame,
            relief=None,
            pos=(0.118, 0, -0.37),
            scale=0.76,
        )
        self.commandFrame.setBin('sorted-gui-popup', 1004)

        self.commandTint = DirectFrame(
            parent=self.commandFrame,
            relief=None,
            pos=(-0.032, 0, 0),
            scale=(0.905, 1, 0.57),
            image=self.assets.find('**/Chat-Panel-Tint-Rounded'),
            image_scale=(1, 1, 339.0 / 849.0),
        )

        shortcutImage = self.assets.find('**/Shortcut_Gray')
        if shortcutImage.isEmpty():
            shortcutImage = self.assets.find('**/Chat-Panel-Tint-Rounded')
        self.commandBackground = DirectFrame(
            parent=self.commandFrame,
            relief=None,
            image=shortcutImage,
            image_scale=(1, 1, 188.0 / 709.0),
        )

        self.commandScrollBar = DirectFrame(
            parent=self.commandFrame,
            relief=None,
            pos=(0.456, 0, 0),
            scale=(0.024, 1, 0.23),
            image=self.assets.find('**/Scrollbar'),
        )
        self.commandScrollThumb = DirectFrame(
            parent=self.commandFrame,
            relief=None,
            pos=(0.456, 0, 0.07),
            scale=(0.052, 1, 0.062),
            image=self.assets.find('**/Scrollblock'),
        )

        self.commandSelectionFrame = DirectFrame(parent=self.commandFrame, relief=None)
        self.commandRows = []
        for visibleIndex, zPos in enumerate((0.058, -0.058)):
            row = DirectButton(
                parent=self.commandSelectionFrame,
                relief=None,
                pos=(-0.032, 0, zPos),
                scale=0.45,
                frameSize=(-0.99, 0.98, -0.12, 0.12),
                frameColor=(0.203, 0.501, 0.921, 0.4),
                command=self._chooseVisibleCommand,
                extraArgs=[visibleIndex],
                pressEffect=0,
            )
            title = DirectLabel(
                parent=row,
                relief=None,
                scale=0.1,
                pos=(-0.95, 0, 0.01),
                text='',
                text_align=TextNode.ALeft,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                textMayChange=1,
            )
            description = DirectLabel(
                parent=row,
                relief=None,
                scale=0.05,
                pos=(0.95, 0, -0.08),
                text='',
                text_align=TextNode.ARight,
                text_fg=(1, 1, 1, 1),
                text_shadow=(0, 0, 0, 1),
                text_wordwrap=19,
                textMayChange=1,
            )
            autofill = DirectLabel(
                parent=row,
                relief=None,
                scale=0.05,
                pos=(-0.95, 0, -0.08),
                text='Press "TAB" to select',
                text_align=TextNode.ALeft,
                text_fg=(0.843, 0.855, 0.404, 1),
                text_shadow=(0, 0, 0, 1),
            )
            row.bind(DGG.WITHIN, self._hoverVisibleCommand, [visibleIndex])
            row._commandTitle = title
            row._commandDescription = description
            row._commandAutofill = autofill
            row._commandValue = None
            self.commandRows.append(row)

        self.commandInformationFrame = DirectFrame(parent=self.commandFrame, relief=None)
        self.commandInvokeText = DirectLabel(
            parent=self.commandInformationFrame,
            relief=None,
            pos=(-0.46, 0, 0.046),
            scale=0.05,
            text='',
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            textMayChange=1,
        )
        self.commandDescriptionText = DirectLabel(
            parent=self.commandInformationFrame,
            relief=None,
            pos=(0.39, 0, 0.07),
            scale=0.025,
            text='',
            text_align=TextNode.ARight,
            text_wordwrap=18,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            textMayChange=1,
        )
        self.commandParametersText = DirectLabel(
            parent=self.commandInformationFrame,
            relief=None,
            pos=(-0.46, 0, 0),
            scale=0.03,
            text='',
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            textMayChange=1,
        )
        self.commandAliasesText = DirectLabel(
            parent=self.commandInformationFrame,
            relief=None,
            pos=(-0.46, 0, -0.04),
            scale=0.03,
            text='',
            text_align=TextNode.ALeft,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            textMayChange=1,
        )
        self.commandHintText = DirectLabel(
            parent=self.commandInformationFrame,
            relief=None,
            pos=(0.39, 0, -0.08),
            scale=0.025,
            text='',
            text_align=TextNode.ARight,
            text_wordwrap=18,
            text_fg=(1, 1, 1, 0.6),
            text_shadow=(0, 0, 0, 1),
            textMayChange=1,
        )

        self.commandSelectionFrame.hide()
        self.commandInformationFrame.hide()
        self.commandScrollBar.hide()
        self.commandScrollThumb.hide()
        self.commandFrame.hide()

    def _updateCommandPanelColour(self, colourName, scrollColour):
        if not hasattr(self, 'commandBackground'):
            return
        image = self.assets.find('**/Shortcut_%s' % colourName)
        if image.isEmpty():
            image = self.assets.find('**/Shortcut_Gray')
        if not image.isEmpty():
            self.commandBackground['image'] = image
        self.commandScrollBar['image_color'] = scrollColour
        self.commandScrollThumb['image_color'] = scrollColour

    def _getNearbyCommandTargets(self):
        targets = []
        seen = set()
        try:
            from toontown.toon.DistributedToon import DistributedToon
            try:
                objects = base.cr.getObjectsOfExactClass(DistributedToon)
                try:
                    iterator = objects.itervalues()
                except:
                    iterator = objects.values()
            except:
                try:
                    iterator = base.cr.doId2do.itervalues()
                except:
                    iterator = base.cr.doId2do.values()

            for toon in iterator:
                if toon is None or toon is getattr(base, 'localAvatar', None):
                    continue
                if toon.__class__ is not DistributedToon:
                    continue
                try:
                    doId = toon.getDoId()
                except:
                    doId = getattr(toon, 'doId', 0)
                if not doId or doId in seen:
                    continue
                try:
                    name = toon.getName().strip()
                except:
                    name = ''
                if not name:
                    continue
                seen.add(doId)
                targets.append({
                    'kind': 'target',
                    'name': name,
                    'nameLower': name.lower(),
                    'description': 'Target this nearby Toon.  Toon ID: %s' % doId,
                    'doId': doId,
                    'toon': toon,
                    'searchTerms': (name.lower(), str(doId)),
                })
        except:
            pass

        targets.sort(key=lambda item: item['nameLower'])
        return targets

    def _formatCommandTargetName(self, name):
        return name

    def _extractCompletedCommandTarget(self, argumentText, targets):
        text = argumentText.lstrip()
        if not text:
            return (None, text)

        lowered = text.lower()
        orderedTargets = sorted(targets, key=lambda item: len(item['name']), reverse=True)
        for target in orderedTargets:
            name = target['name']
            loweredName = target['nameLower']
            if lowered == loweredName:
                return (target, '')
            if lowered.startswith(loweredName) and len(text) > len(name) and text[len(name)].isspace():
                return (target, text[len(name):].lstrip())
        return (None, text)

    def _filterCommandTargets(self, targets, enteredText):
        query = enteredText.strip().lower()
        strong = []
        weak = []
        for target in targets:
            terms = target.get('searchTerms', (target['nameLower'],))
            if not query or any(term.startswith(query) for term in terms):
                strong.append(target)
            elif any(query in term for term in terms):
                weak.append(target)
        return strong + weak

    def _getCommandMatchRank(self, command, query):
        name = command.get('name', '').lower()
        aliases = tuple(alias.lower() for alias in command.get('aliases', ()) or ())
        if not query:
            return (0, len(name), name)
        if name.startswith(query):
            return (0, len(name) - len(query), len(name), name)
        aliasPrefixes = [alias for alias in aliases if alias.startswith(query)]
        if aliasPrefixes:
            shortestAlias = min(aliasPrefixes, key=len)
            return (1, len(shortestAlias) - len(query), len(shortestAlias), name)
        namePosition = name.find(query)
        if namePosition >= 0:
            return (2, namePosition, len(name), name)
        aliasPositions = []
        for alias in aliases:
            position = alias.find(query)
            if position >= 0:
                aliasPositions.append((position, len(alias)))
        if aliasPositions:
            position, aliasLength = min(aliasPositions)
            return (3, position, aliasLength, name)
        return None

    def _getCommandPrefix(self, text):
        if not text:
            return None
        oldPrefix = getattr(ToontownGlobals, 'MagicWordInvokerPrefix', '~')
        if text.startswith('/'):
            return '/'
        if oldPrefix and text.startswith(oldPrefix):
            return oldPrefix
        return None

    def _updateCommandShortcuts(self, text):
        commandPrefix = self._getCommandPrefix(text)
        if (not self._entryFocused or commandPrefix is None or
                self.currentTab in (self.TAB_ALERTS, self.TAB_NPC)):
            self._hideCommandShortcuts()
            return

        self._commandPrefix = commandPrefix
        self.commandFrame.show()
        if text.startswith(commandPrefix + commandPrefix):
            self._showEmptyCommandInformation(text,
                'Use %scommand ToonName instead of %s%scommand.' %
                (commandPrefix, commandPrefix, commandPrefix))
            return

        entered = text[len(commandPrefix):]
        commandMatch = re.match(r'^\s*(\S+)', entered)
        commandWord = commandMatch.group(1).lower() if commandMatch else ''
        exact = self._commandLookup.get(commandWord)

        if exact is not None:
            self._commandExact = exact
            self._commandSelectionKind = 'command'
            self._commandTargetBase = ''
            self._commandInvokeWord = commandMatch.group(1)
            remainder = entered[commandMatch.end():]
            targetMode = exact.get('targetMode', 'optional')
            targets = self._getNearbyCommandTargets() if targetMode != 'none' else []

            if remainder and targetMode != 'none':
                argumentText = remainder.lstrip()
                completedTarget, remainingArguments = self._extractCompletedCommandTarget(argumentText, targets)
                if completedTarget is not None:
                    self._showCommandInformation(exact, completedTarget)
                    return

                targetMatches = self._filterCommandTargets(targets, argumentText)
                if targetMatches:
                    self._commandMode = 'selection'
                    self._commandSelectionKind = 'target'
                    self._commandTargetBase = self._commandPrefix + self._commandInvokeWord + ' '
                    self._commandMatches = targetMatches
                    self._commandSelectionIndex = 0
                    self._commandVisibleStart = 0
                    self.commandInformationFrame.hide()
                    self.commandSelectionFrame.show()
                    self._refreshCommandRows()
                    return

            self._showCommandInformation(exact)
            return

        self._commandExact = None
        self._commandMode = 'selection'
        self._commandSelectionKind = 'command'
        self._commandInvokeWord = ''
        self._commandTargetBase = ''
        query = commandWord
        rankedMatches = []
        for command in self.commandShortcuts:
            rank = self._getCommandMatchRank(command, query)
            if rank is not None:
                rankedMatches.append((rank, command))
        rankedMatches.sort(key=lambda item: item[0])
        self._commandMatches = [item[1] for item in rankedMatches]
        self._commandSelectionIndex = 0 if self._commandMatches else -1
        self._commandVisibleStart = 0

        if not self._commandMatches:
            self._showEmptyCommandInformation(text)
            return

        self.commandInformationFrame.hide()
        self.commandSelectionFrame.show()
        self._refreshCommandRows()

    def _hideCommandShortcuts(self):
        if not hasattr(self, 'commandFrame'):
            return
        self._commandMode = 'hidden'
        self._commandSelectionKind = 'command'
        self._commandMatches = []
        self._commandSelectionIndex = -1
        self._commandExact = None
        self._commandInvokeWord = ''
        self._commandTargetBase = ''
        self.commandFrame.hide()

    def _showCommandInformation(self, command, target=None):
        self._commandMode = 'information'
        self._commandExact = command
        self._commandMatches = []
        self._commandSelectionIndex = -1
        self.commandSelectionFrame.hide()
        self.commandScrollBar.hide()
        self.commandScrollThumb.hide()
        self.commandInformationFrame.show()

        invokeWord = self._commandInvokeWord or command['name']
        syntax = self._commandPrefix + invokeWord
        targetMode = command.get('targetMode', 'optional')
        if target is not None:
            syntax += ' ' + self._formatCommandTargetName(target['name'])
        elif targetMode == 'required':
            syntax += ' <nearby Toon name>'
        elif targetMode == 'optional':
            syntax += ' [nearby Toon name]'
        if command.get('usage'):
            syntax += ' ' + command['usage']
        self.commandInvokeText['text'] = syntax
        self.commandDescriptionText['text'] = command.get('description') or 'No description is available for this command.'
        self.commandParametersText['text'] = ('Parameters: %s' % command['usage']) if command.get('usage') else ''
        aliases = command.get('aliases', ())
        self.commandAliasesText['text'] = ('Aliases: %s' % ', '.join(aliases)) if aliases else ''
        if target is not None:
            self.commandHintText['text'] = 'Target: %s. Press ENTER to run it.' % target['name']
        elif targetMode == 'required':
            self.commandHintText['text'] = 'Type a nearby Toon name and press TAB.'
        elif targetMode == 'optional':
            self.commandHintText['text'] = 'Optional: type a nearby Toon name and press TAB. Without a matched name, the command runs on yourself.'
        else:
            self.commandHintText['text'] = 'This command runs on your client or your own Toon.'

    def _showEmptyCommandInformation(self, text, hint=None):
        self._commandMode = 'empty'
        self.commandSelectionFrame.hide()
        self.commandScrollBar.hide()
        self.commandScrollThumb.hide()
        self.commandInformationFrame.show()
        self.commandInvokeText['text'] = text
        self.commandDescriptionText['text'] = 'No matching commands were found.'
        self.commandParametersText['text'] = ''
        self.commandAliasesText['text'] = ''
        self.commandHintText['text'] = hint or 'Keep typing or erase part of the command.'

    def _refreshCommandRows(self):
        if self._commandMode != 'selection':
            return

        if self._commandSelectionIndex < self._commandVisibleStart:
            self._commandVisibleStart = self._commandSelectionIndex
        elif self._commandSelectionIndex >= self._commandVisibleStart + len(self.commandRows):
            self._commandVisibleStart = self._commandSelectionIndex - len(self.commandRows) + 1

        maximumStart = max(0, len(self._commandMatches) - len(self.commandRows))
        self._commandVisibleStart = max(0, min(self._commandVisibleStart, maximumStart))

        for visibleIndex, row in enumerate(self.commandRows):
            absoluteIndex = self._commandVisibleStart + visibleIndex
            if absoluteIndex >= len(self._commandMatches):
                row._commandValue = None
                row.hide()
                continue

            item = self._commandMatches[absoluteIndex]
            row._commandValue = item
            row._commandTitle['text'] = item['name']
            row._commandDescription['text'] = item.get('description', '')
            if absoluteIndex == self._commandSelectionIndex:
                row['relief'] = DGG.FLAT
                row._commandAutofill.show()
            else:
                row['relief'] = None
                row._commandAutofill.hide()
            row.show()

        if len(self._commandMatches) > len(self.commandRows):
            self.commandScrollBar.show()
            self.commandScrollThumb.show()
            denominator = float(max(1, len(self._commandMatches) - 1))
            ratio = self._commandSelectionIndex / denominator
            self.commandScrollThumb.setZ(0.075 - (ratio * 0.15))
        else:
            self.commandScrollBar.hide()
            self.commandScrollThumb.hide()

    def _hoverVisibleCommand(self, visibleIndex, unused=None):
        if self._commandMode != 'selection':
            return
        absoluteIndex = self._commandVisibleStart + visibleIndex
        if absoluteIndex < len(self._commandMatches):
            self._commandSelectionIndex = absoluteIndex
            self._refreshCommandRows()

    def _chooseVisibleCommand(self, visibleIndex):
        if self._commandMode != 'selection':
            return
        absoluteIndex = self._commandVisibleStart + visibleIndex
        if absoluteIndex >= len(self._commandMatches):
            return
        self._commandSelectionIndex = absoluteIndex
        self._completeSelectedCommand()

    def _completeSelectedCommand(self):
        item = None
        if self._commandMode == 'selection':
            if 0 <= self._commandSelectionIndex < len(self._commandMatches):
                item = self._commandMatches[self._commandSelectionIndex]
        elif self._commandMode == 'information':
            try:
                currentText = self.entry.get(plain=True)
            except:
                currentText = self.entry.get()
            commandPrefix = self._getCommandPrefix(currentText) or self._commandPrefix
            entered = currentText[len(commandPrefix):]
            if re.search(r'\s', entered):
                return
            item = self._commandExact

        if item is None:
            return

        if self._commandSelectionKind == 'target' or item.get('kind') == 'target':
            newText = self._commandTargetBase + self._formatCommandTargetName(item['name']) + ' '
        else:
            newText = self._commandPrefix + item['name'] + ' '
        self.entry.set(newText)
        self.entry.setCursorPosition(len(newText))
        self._entryChanged(None)

    def _commandSelectionUp(self):
        if self._commandMode != 'selection' or not self._commandMatches:
            return
        self._commandSelectionIndex = max(0, self._commandSelectionIndex - 1)
        self._refreshCommandRows()

    def _commandSelectionDown(self):
        if self._commandMode != 'selection' or not self._commandMatches:
            return
        self._commandSelectionIndex = min(len(self._commandMatches) - 1, self._commandSelectionIndex + 1)
        self._refreshCommandRows()

    def _entryUp(self, unused=None):
        try:
            text = self.entry.get(plain=True)
        except:
            text = self.entry.get()
        if self._getCommandPrefix(text) is not None:
            self._commandSelectionUp()
        else:
            self._historyUp()

    def _entryDown(self, unused=None):
        try:
            text = self.entry.get(plain=True)
        except:
            text = self.entry.get()
        if self._getCommandPrefix(text) is not None:
            self._commandSelectionDown()
        else:
            self._historyDown()

    def _entryTab(self, unused=None):
        try:
            text = self.entry.get(plain=True)
        except:
            text = self.entry.get()
        if self._getCommandPrefix(text) is not None:
            self._completeSelectedCommand()

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
            command=self.openStickers,
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

    def disableUniteButtons(self):
        self.uniteButton['state'] = DGG.DISABLED
        self.quickUniteButton['state'] = DGG.DISABLED

        disabledColor = VBase4(0.3, 0.3, 0.3, 1)
        self.uniteButton['image_color'] = disabledColor
        self.quickUniteButton['image_color'] = disabledColor

    def updateUniteButtons(self):
        disabled = (
            self.obscuredSpeedChat or
            base.localAvatar.hasToonStatusEffect('cooldown') or
            'noUnites' in base.localAvatar.battleConditions
        )

        state = DGG.DISABLED if disabled else DGG.NORMAL
        color = VBase4(0.3, 0.3, 0.3, 1) if disabled else Vec4(1, 1, 1, 1)

        self.uniteButton['state'] = state
        self.quickUniteButton['state'] = state
        self.uniteButton['image_color'] = color
        self.quickUniteButton['image_color'] = color

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
        if getattr(self, 'stickerMenu', None):
            self.stickerMenu.hideMenu()
        self._closeDisplay(playSound=not self.isHidden)

    def toggle(self):
        if self.isHidden:
            self.open()
        else:
            self.close()

    def chatHotkey(self):
        # Let the player type "c" normally in the text box.
        if self._entryFocused:
            return

        if self.isHidden:
            self.open()
        else:
            self.close()

    def closeChatHotkey(self):
        # Let DirectEntry keep the letter C while the player is typing.
        if self._entryFocused:
            return
        if not self.isHidden:
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
        self._hideCommandShortcuts()
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
            # Each unselected tab image remains tucked behind the main frame.
            # The selected tab image is hidden so the matching coloured panel's
            # complete integrated tab shape is shown in front, as in Clash.
            button['image_pos'] = (0, 0, 10) if tabName == tab else (0, 0, 0)

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
        self._updateCommandPanelColour(panelName.split('_')[-1], scrollColour)
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
        self._updateCommandShortcuts(text)

    def _focusIn(self):
        self._entryFocused = True
        self.updateUniteButtons()
        self.entry.accept('escape', self.removeFocus)
        self.entry.accept(self.entry.guiItem.getPressEvent(KeyboardButton.up()), self._entryUp)
        self.entry.accept(self.entry.guiItem.getRepeatEvent(KeyboardButton.up()), self._entryUp)
        self.entry.accept(self.entry.guiItem.getPressEvent(KeyboardButton.down()), self._entryDown)
        self.entry.accept(self.entry.guiItem.getRepeatEvent(KeyboardButton.down()), self._entryDown)
        self.entry.accept(self.entry.guiItem.getPressEvent(KeyboardButton.tab()), self._entryTab)
        self.ignore(getattr(base, 'CHAT_CLOSE_HOTKEY', 'c'))
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
        self.updateUniteButtons()
        self.entry.ignore('escape')
        self.entry.ignore(self.entry.guiItem.getPressEvent(KeyboardButton.up()))
        self.entry.ignore(self.entry.guiItem.getRepeatEvent(KeyboardButton.up()))
        self.entry.ignore(self.entry.guiItem.getPressEvent(KeyboardButton.down()))
        self.entry.ignore(self.entry.guiItem.getRepeatEvent(KeyboardButton.down()))
        self.entry.ignore(self.entry.guiItem.getPressEvent(KeyboardButton.tab()))
        self.accept('c', self.chatHotkey)
        try:
            if base.wantCustomControls:
                base.localAvatar.controlManager.enableWASD()
            else:
                base.localAvatar.enableControls()
        except:
            pass
        self._entryChanged(None)

    def _handleMouseClickFocus(self):
        # Clicking anywhere outside the actual text-entry bar removes focus,
        # but leaves the Clash chat panel and any unsent message open.
        self.updateUniteButtons()
        if not self._entryFocused:
            return
        try:
            if not base.mouseWatcherNode.hasMouse():
                self.removeFocus()
                return
            mouse = base.mouseWatcherNode.getMouse()
            point = self.entryScroll.getRelativePoint(
                render2d, Point3(mouse.getX(), 0, mouse.getY()))
            clipLeft, clipRight, clipBottom, clipTop = (0, 13.4, -1, 1)
            insideEntry = (clipLeft <= point.getX() <= clipRight and
                           clipBottom <= point.getZ() <= clipTop)

            insideCommands = False
            if hasattr(self, 'commandFrame') and not self.commandFrame.isHidden():
                commandPoint = self.commandFrame.getRelativePoint(
                    render2d, Point3(mouse.getX(), 0, mouse.getY()))
                insideCommands = (-0.53 <= commandPoint.getX() <= 0.53 and
                                  -0.16 <= commandPoint.getZ() <= 0.16)
        except:
            insideEntry = False
            insideCommands = False
        if not insideEntry and not insideCommands:
            self.removeFocus()

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
        if getattr(self, 'stickerMenu', None):
            self.stickerMenu.hideMenu()
        chatMgr = getattr(base.localAvatar, 'chatMgr', None)
        if chatMgr and hasattr(chatMgr, 'openPanelSpeedChat'):
            chatMgr.openPanelSpeedChat()

    def openUnites(self):
        self.updateUniteButtons()
        if self.obscuredSpeedChat or base.localAvatar.hasToonStatusEffect('cooldown') or 'noUnites' in base.localAvatar.battleConditions:
            return
        if getattr(self, 'stickerMenu', None):
            self.stickerMenu.hideMenu()
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

    def addToLog(self, msg, avId=0, category=None, showNotification=True):
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

        if showNotification:
            if tab == self.TAB_ALERTS:
                try:
                    self._showClashAlert(msg)
                except Exception as error:
                    print('[ChatLog] Could not show Clash alert: %s' % error)
                    if self.isHidden or self.currentTab != self.TAB_MAIN:
                        self._showNotification(self.TAB_MAIN)
                    if self.isHidden or self.currentTab != self.TAB_ALERTS:
                        self._showNotification(self.TAB_ALERTS)
            else:
                if self.isHidden or self.currentTab != self.TAB_MAIN:
                    self._showNotification(self.TAB_MAIN)
                if tab != self.TAB_MAIN and (self.isHidden or self.currentTab != tab):
                    self._showNotification(tab)

    def _showClashAlert(self, message):
        from toontown.notifications.NotificationManager import getNotificationManager
        from toontown.notifications.notificationData.GenericTextNotification import GenericTextNotification

        text = self._stripTextProperties(str(message)).strip()
        title = 'System Alert'
        prefixes = (
            'System Message:',
            'Game Message:',
            'Toon HQ:',
        )
        for prefix in prefixes:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()
                title = prefix[:-1]
                break

        getNotificationManager().addNotification(GenericTextNotification(
            title=title,
            subtitle=text))

    def _stripTextProperties(self, text):
        try:
            text = re.sub('\x01[^\x01]*\x01', '', text)
            return text.replace('\x02', '')
        except:
            return text

    def _wrapLongDisplayWords(self, text, maxRun=50):
        """Break long unspaced runs so the scrolled frame cannot clip them."""
        if not text:
            return text

        result = []
        visibleRun = 0
        propertyOpen = False
        index = 0
        textLength = len(text)
        while index < textLength:
            character = text[index]

            # Panda text properties use \1PROPERTY\1 ... \2.  Copy the
            # property markers without counting them as visible characters.
            if character == '\x01':
                propertyEnd = text.find('\x01', index + 1)
                if propertyEnd != -1:
                    result.append(text[index:propertyEnd + 1])
                    propertyOpen = True
                    index = propertyEnd + 1
                    continue
            elif character == '\x02':
                result.append(character)
                propertyOpen = False
                index += 1
                continue

            if character in (' ', '\t', '\n'):
                visibleRun = 0
            else:
                if visibleRun >= maxRun:
                    result.append('\n')
                    visibleRun = 0
                visibleRun += 1

            result.append(character)
            index += 1

        return ''.join(result)

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
        displayMsg = self._wrapLongDisplayWords(msg)
        options = {
            'parent': self.lists[tab].getCanvas(),
            'relief': None,
            'frameColor': (0, 0, 0, 0),
            'frameSize': (-0.85, 0.85, -0.05, 0.05),
            'text': displayMsg,
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
        item._chatHeight = 0.069 * self._estimateLineCount(displayMsg)
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
            self.TAB_MAIN: "World messages are shown here. Messages from the\nWhispers, Alerts, NPC and Clubs tabs are also shown here.\nMain combines every supported Aristotown chat channel.",
            self.TAB_WHISPERS: 'Whispers sent to and received from other Toons are shown here.',
            self.TAB_ALERTS: 'System alerts and announcements are shown here.',
            self.TAB_NPC: 'Cog and NPC dialogue is shown here.',
            self.TAB_CLUBS: 'Club messages are shown here when club chat is available.',
        }
        for tab, text in tutorials.items():
            self._addMessageItem(tab, text, textColor=tutorialColour, tutorial=True)

    def _scrollCurrent(self, amount):
        if getattr(self, 'stickerMenu', None) and self.stickerMenu.isOpen:
            return
        if self.isHidden or self.currentTab not in self.lists:
            return
        try:
            self.lists[self.currentTab].verticalScroll.scrollStep(amount)
            messenger.send('wakeup')
        except:
            pass

    def openStickers(self):
        if self.obscuredSpeedChat or not self.interfaceEnabled:
            return
        chatMgr = getattr(base.localAvatar, 'chatMgr', None)
        if chatMgr and hasattr(chatMgr, 'closePanelMenus'):
            chatMgr.closePanelMenus()
        if getattr(self, 'stickerMenu', None):
            self.stickerMenu.toggleMenu()

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
        if self.obscuredSpeedChat and getattr(self, 'stickerMenu', None):
            self.stickerMenu.hideMenu()
        self.quickSpeedChatButton['state'] = DGG.DISABLED if self.obscuredSpeedChat else DGG.NORMAL
        self.quickStickerButton['state'] = DGG.DISABLED if self.obscuredSpeedChat else DGG.NORMAL
        self.updateUniteButtons()
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
        if getattr(self, 'stickerMenu', None):
            self.stickerMenu.hideMenu()
        self.quickFrame.hide()
        self.displayFrame.hide()
        self.reparentTo(hidden)

    def enableInterface(self):
        self.interfaceEnabled = True
        self._refreshInterfaceVisibility()

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
        if getattr(self, 'stickerMenu', None):
            self.stickerMenu.destroy()
            self.stickerMenu = None
        self._displaySequence.pause()
        self._notificationSequence.pause()
        self.removeFocus()
        if getattr(base.cr, 'chatLog', None) is self:
            base.cr.chatLog = None
        notificationManager = getattr(base, 'altisNotificationManager', None)
        if notificationManager is not None:
            notificationManager.destroy()
            base.altisNotificationManager = None
        try:
            self.assets.removeNode()
        except:
            pass
        self.destroy()
