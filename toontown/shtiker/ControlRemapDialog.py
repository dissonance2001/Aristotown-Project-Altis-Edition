from panda3d.core import Vec3, TextNode
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DirectDialog, DirectScrolledFrame, DGG
from direct.interval.IntervalGlobal import Sequence, LerpScaleInterval


ELEMENT_SPACING = -0.485
CONTROLS_TO_SAVE = {}

CONTROL_KEYS = (
    'MOVE_UP',
    'MOVE_LEFT',
    'MOVE_DOWN',
    'MOVE_RIGHT',
    'JUMP',
    'ACTION_BUTTON',
    'SECONDARY_KEY',
    'SPRINT_KEY',
    'INTERACT',
    'INVENTORY_KEY',
    'QUESTS_KEY',
    'CHAT_HOTKEY',
    'CHAT_CLOSE_HOTKEY',
    'NEXT_CAMERA_POS',
    'MAP_PAGE_HOTKEY',
    'OPTIONS_PAGE_HOTKEY',
    'SCREENSHOT_KEY',
    'STREET_MAP_KEY',
    'COMMAND_HOTKEY',
    'CHANNEL_MAIN',
    'CHANNEL_WHISPERS',
    'CHANNEL_ALERTS',
    'CHANNEL_NPC',
    'CHANNEL_CLUBS',
)

CONTROL_LABELS = (
    'Move Forwards:',
    'Move Left:',
    'Move Backwards:',
    'Move Right:',
    'Jump:',
    'Primary Action:',
    'Secondary Action:',
    'Sprint:',
    'Interact Key:',
    'Gags Key:',
    'Tasks Key:',
    'Chatbox Hotkey:',
    'Toggle Chat:',
    'Camera Position:',
    'Open Shticker Book:',
    'Open Options:',
    'Screenshot Key:',
    'Street Map Toggle:',
    'Command Hotkey:',
    'Main Channel:',
    'Whisper Channel:',
    'Alerts Channel:',
    'NPC Channel:',
    'Clubs Channel:',
)

CONTROL_DESCRIPTIONS = {
    5: 'Used for Altis primary actions and the 0% pie/action-button interaction.',
    6: 'Used for secondary actions such as minimum-power pies; CLO Taunt can use this later.',
    7: 'Sprint key. Whether it is a hold or toggle input is controlled by the Sprint setting.',
    8: 'If interaction keys are enabled, this interacts with supported doors, NPCs and objects.',
    9: 'Shows your Gag inventory outside the Shticker Book.',
    10: 'Shows your Tasks outside the Shtiker Book.',
    11: 'Opens the chatbox and focuses the text entry.',
    12: 'Opens or closes the Clash-style chat panel.',
    13: 'Cycles through the available camera positions.',
    14: 'Opens or closes the Shticker Book.',
    15: 'Opens the Shticker Book directly to Options.',
    16: 'Takes a screenshot of the current game view.',
    17: 'Shows or hides the street and quest map.',
    18: 'Opens the chatbox with a slash command ready to type.',
    19: 'Opens the Main chat channel.',
    20: 'Opens the Whispers chat channel.',
    21: 'Opens the Alerts chat channel.',
    22: 'Opens the NPC chat channel.',
    23: 'Opens the Clubs chat channel when available.',
}

MOVEMENT_END = 4
ACTIONS_END = 6


def _cleanText(text):
    if text is None:
        return 'Unbound'
    text = str(text).replace('_', ' ')
    if not text:
        return 'Unbound'
    return text[0].upper() + text[1:]


def _getDefault(key):
    defaults = getattr(base, '_controlDefaults', {})
    if key in defaults:
        return defaults[key]
    return getattr(base, key, '')


class RebindPopup(DirectFrame):
    def __init__(self, parent, controlNum):
        DirectFrame.__init__(self, parent=parent, relief=None)
        self.controlNum = controlNum
        gui = loader.loadModel('phase_3.5/models/gui/optionspage/keybinds_gui.bam')
        key = CONTROL_KEYS[controlNum]
        current = CONTROLS_TO_SAVE.get(controlNum, getattr(base, key, _getDefault(key)))
        self.dialogBox = DirectDialog(
            parent=self,
            dialogName='altisKeybindPopup',
            image=gui.find('**/base'),
            scale=(6, 3, 3),
            relief=None,
            suppressMouse=True,
            suppressKeys=True
        )
        self.exitButton = DirectButton(
            parent=self.dialogBox,
            relief=None,
            pos=(0.075, 1, 0.05),
            scale=(0.025, 1, 0.05),
            image=(gui.find('**/button_neutral'), gui.find('**/button_click'), gui.find('**/button_highlight')),
            command=self.cancel
        )
        self.rebindLabel = DirectLabel(
            parent=self.dialogBox,
            relief=None,
            pos=(0, 0, 0),
            text='Current bind for %s' % CONTROL_LABELS[controlNum].rstrip(':'),
            text_wordwrap=15,
            scale=(0.01, 0.04, 0.02)
        )
        self.keyLabel = DirectLabel(
            parent=self.dialogBox,
            relief=None,
            pos=(-0.005, 0, -0.115),
            text=_cleanText(current),
            scale=(0.014, 0.04, 0.028)
        )
        gui.removeNode()
        Sequence(
            LerpScaleInterval(self, 0.2, Vec3(1.1), Vec3(0.01), blendType='easeInOut'),
            LerpScaleInterval(self, 0.09, Vec3(1), blendType='easeInOut')
        ).start()

    def cancel(self):
        messenger.send('altis-keybind-popup-closed', [-1])
        self.destroy()

    def finish(self):
        messenger.send('altis-keybind-popup-closed', [self.controlNum])
        self.destroy()

    def destroy(self):
        self.ignoreAll()
        try:
            self.dialogBox.cleanup()
        except:
            pass
        DirectFrame.destroy(self)


class KeyBindInfo(object):
    def __init__(self, controlNum, parent, z):
        self.button = None
        self.label = None
        description = CONTROL_DESCRIPTIONS.get(controlNum)
        if not description:
            return
        gui = loader.loadModel('phase_3.5/models/gui/optionspage/keybind_info.bam')
        size = 0.55 / 7.0
        panelHeight = 1.25
        infoScale = Vec3(2.4, 1, 0.34 * panelHeight) * 7
        self.button = DirectButton(
            parent=parent,
            pos=(-0.406, 0, z + 0.09),
            relief=None,
            scale=(size / 1.8, size, size / 0.2),
            image=gui.find('**/info_button')
        )
        self.label = DirectLabel(
            parent=self.button,
            pos=(8.3, 0, 0.18),
            relief=None,
            scale=infoScale,
            image=gui.find('**/info_backing'),
            text_scale=(0.039, 0.224, 0.448),
            text=description,
            text_align=TextNode.ACenter,
            text_pos=(-0.02, -0.07),
            text_wordwrap=25
        )
        self.label.hide()
        self.button.bind(DGG.ENTER, self.show)
        self.button.bind(DGG.EXIT, self.hide)
        gui.removeNode()

    def show(self, event=None):
        if self.label:
            self.label.show()

    def hide(self, event=None):
        if self.label:
            self.label.hide()

    def setState(self, state):
        if self.button:
            self.button['state'] = state

    def destroy(self):
        if self.button:
            self.button.destroy()
            self.button = None
        self.label = None


class KeyBindEntry(object):
    def __init__(self, controlNum, parent, spacing):
        self.controlNum = controlNum
        self.parent = parent
        self.spacing = spacing
        gui = loader.loadModel('phase_3.5/models/gui/optionspage/keybinds_gui.bam')
        key = CONTROL_KEYS[controlNum]
        current = CONTROLS_TO_SAVE.get(controlNum, getattr(base, key, _getDefault(key)))
        zLabel = -0.7 + ELEMENT_SPACING * spacing
        zButton = -0.6 + ELEMENT_SPACING * spacing
        self.label = DirectLabel(
            parent=parent,
            pos=(-0.37, 0, zLabel),
            text=CONTROL_LABELS[controlNum],
            scale=(0.03, 0.03, 0.3),
            relief=None,
            text_align=TextNode.ALeft
        )
        self.sketch = DirectButton(
            parent=parent,
            pos=(0.25, 0, zButton),
            relief=None,
            image=gui.find('**/sketch_box'),
            scale=(0.275, 1, 1),
            frameSize=(-0.25, 0.22, -0.125, 0.175),
            command=messenger.send,
            extraArgs=['altis-keybind-wait', [self]],
            text=_cleanText(current),
            text_pos=(-0.0125, -0.05),
            text_scale=(0.085, 0.2, 0.4)
        )
        self.eraser = DirectButton(
            parent=parent,
            pos=(0.4, 0, zButton),
            image=gui.find('**/eraser'),
            scale=(0.275, 1, 1.3),
            relief=None,
            frameSize=(-0.085, 0.1, -0.175, 0.175),
            command=messenger.send,
            extraArgs=['altis-keybind-reset-one', [controlNum]]
        )
        self.info = KeyBindInfo(controlNum, parent, zLabel)
        gui.removeNode()

    def setText(self, value):
        self.sketch['text'] = _cleanText(value)

    def setState(self, state):
        self.sketch['state'] = state
        self.eraser['state'] = state
        self.info.setState(state)

    def destroy(self):
        self.info.destroy()
        self.sketch.destroy()
        self.eraser.destroy()
        self.label.destroy()


class ControlRemap(DirectFrame):
    def __init__(self):
        DirectFrame.__init__(self, parent=aspect2d, relief=None)
        self.unloaded = False
        self.popupDialog = None
        self.resetDialog = None
        self.entries = []
        self._suppressedOrbitalCamera = None
        self._orbitalWheelWasEnabled = False
        self.accept('altis-keybind-reset-one', self.resetOne)
        self.accept('altis-keybind-wait', self.enterWaitForKey)
        self.accept('altis-keybind-popup-closed', self.exitWaitForKey)
        self._suppressOrbitalWheel()
        self._load()
        self.setBin('sorted-gui-popup', 5000)
        base.transitions.fadeScreen(0.75)
        Sequence(
            LerpScaleInterval(self.frame, 0.2, Vec3(1.1), Vec3(0.01), blendType='easeInOut'),
            LerpScaleInterval(self.frame, 0.09, Vec3(1), blendType='easeInOut')
        ).start()
        messenger.send('disable-hotkeys')
        try:
            base.cr.chatLog.removeFocus()
        except:
            pass


    def _getOrbitalCamera(self):
        try:
            avatar = getattr(base, 'localAvatar', None)
            return getattr(avatar, 'orbitalCamera', None)
        except:
            return None

    def _suppressOrbitalWheel(self):
        orbitalCamera = self._getOrbitalCamera()
        if orbitalCamera is None:
            return
        try:
            active = orbitalCamera.isActive()
        except:
            active = True
        try:
            accepting = orbitalCamera.isAccepting('wheel_up')
        except:
            accepting = active
        if not accepting:
            return
        try:
            orbitalCamera.ignore('wheel_up')
            orbitalCamera.ignore('wheel_down')
            self._suppressedOrbitalCamera = orbitalCamera
            self._orbitalWheelWasEnabled = True
        except:
            self._suppressedOrbitalCamera = None
            self._orbitalWheelWasEnabled = False

    def _restoreOrbitalWheel(self):
        orbitalCamera = self._suppressedOrbitalCamera
        self._suppressedOrbitalCamera = None
        if orbitalCamera is not None and self._orbitalWheelWasEnabled:
            try:
                if orbitalCamera.isActive():
                    orbitalCamera.accept('wheel_up', orbitalCamera._handleWheelUp)
                    orbitalCamera.accept('wheel_down', orbitalCamera._handleWheelDown)
            except:
                pass
        self._orbitalWheelWasEnabled = False

    def _load(self):
        gui = loader.loadModel('phase_3.5/models/gui/optionspage/keybinds_gui.bam')
        self.frame = DirectFrame(parent=self, relief=None)
        canvasYSize = 0.11 * len(CONTROL_KEYS) + 0.9
        self.dialog = DirectScrolledFrame(
            parent=self.frame,
            image=gui.find('**/clipboard_base'),
            relief=None,
            state=DGG.NORMAL,
            image_scale=(2, 1, 2),
            canvasSize=(-0.5, 0.5, -canvasYSize, 0),
            frameSize=(-0.8, 0.875, -0.776, 0.535),
            verticalScroll_thumb_image=gui.find('**/grip_slider'),
            verticalScroll_resizeThumb=False,
            verticalScroll_relief=None,
            verticalScroll_pos=(0, 0, -0.08),
            verticalScroll_scale=(1, 1, 0.85),
            verticalScroll_thumb_frameSize=(-0.125, 0.125, -0.1, 0.1),
            verticalScroll_thumb_image_scale=(0.25, 1, 0.2),
            verticalScroll_incButton_relief=None,
            verticalScroll_decButton_relief=None
        )
        canvas = self.dialog.getCanvas()
        self.movement = DirectFrame(
            image=gui.find('**/movement'), parent=canvas, relief=None,
            scale=(1.8, 1, 0.2), pos=(0.285, 0, -0.07)
        )
        self.actions = DirectFrame(
            image=gui.find('**/actions'), parent=canvas, relief=None,
            scale=(1.8, 1, 0.2), pos=(0.285, 0, -0.78)
        )
        self.hotkeys = DirectFrame(
            image=gui.find('**/hotkeys'), parent=canvas, relief=None,
            scale=(1.8, 1, 0.2), pos=(0.285, 0, -1.15), image_pos=(-0.03, 0, 0)
        )
        for controlNum in xrange(len(CONTROL_KEYS)):
            if controlNum <= MOVEMENT_END:
                parent = self.movement
                spacing = controlNum
            elif controlNum <= ACTIONS_END:
                parent = self.actions
                spacing = controlNum - MOVEMENT_END - 0.6
            else:
                parent = self.hotkeys
                spacing = controlNum - ACTIONS_END - 0.625
            entry = KeyBindEntry(controlNum, parent, spacing)
            self.entries.append(entry)
            self._bindToScroll(entry.sketch)
            self._bindToScroll(entry.eraser)
            if entry.info.button:
                self._bindToScroll(entry.info.button)
        self._bindToScroll(self.dialog)
        self._bindToScroll(self.dialog.verticalScroll)
        self._bindToScroll(self.dialog.verticalScroll.thumb)
        self._bindToScroll(self.dialog.verticalScroll.incButton)
        self._bindToScroll(self.dialog.verticalScroll.decButton)
        self.resetButton = DirectButton(
            parent=self.dialog, pos=(-0.6, 0, -0.875), scale=(0.5, 1, 0.25), relief=None,
            frameSize=(-0.45, 0.45, -0.325, 0.325), image=gui.find('**/reset'),
            command=self.resetAll
        )
        self.cancelButton = DirectButton(
            parent=self.dialog, pos=(0, 0, -0.85), scale=(0.5, 1, 0.25), relief=None,
            frameSize=(-0.475, 0.45, -0.35, 0.25), image=gui.find('**/cancel'),
            command=self.cancel
        )
        self.okButton = DirectButton(
            parent=self.dialog, pos=(0.55, 0, -0.875), scale=(0.46, 1, 0.23), relief=None,
            frameSize=(-0.425, 0.425, -0.35, 0.35), image=gui.find('**/ok'),
            command=self.save
        )
        self._bindToScroll(self.resetButton)
        self._bindToScroll(self.cancelButton)
        self._bindToScroll(self.okButton)
        gui.removeNode()

    def _bindToScroll(self, gui):
        gui.bind(DGG.WHEELUP, self._wheel, extraArgs=[-1])
        gui.bind(DGG.WHEELDOWN, self._wheel, extraArgs=[1])

    def _wheel(self, direction, event=None):
        try:
            canvasSize = self.dialog['canvasSize']
            canvasHeight = abs(float(canvasSize[2]) - float(canvasSize[3]))
            if canvasHeight <= 0.0:
                return
            value = float(self.dialog['verticalScroll_value']) + (0.2 / canvasHeight) * direction
            self.dialog['verticalScroll_value'] = max(0.0, min(1.0, value))
        except:
            pass

    def enterWaitForKey(self, entry):
        controlNum = entry.controlNum
        self.popupDialog = RebindPopup(self.dialog, controlNum)
        self._setButtons(DGG.DISABLED)
        base.buttonThrowers[0].node().setButtonDownEvent('buttonPress-' + str(controlNum))
        self.popupDialog.acceptOnce('buttonPress-' + str(controlNum), self.registerKey, [controlNum])

    def registerKey(self, controlNum, keyName):
        CONTROLS_TO_SAVE[controlNum] = keyName
        if self.popupDialog:
            self.popupDialog.finish()
            self.popupDialog = None

    def exitWaitForKey(self, controlNum=-1):
        self._setButtons(DGG.NORMAL)
        if controlNum in CONTROLS_TO_SAVE:
            self.entries[controlNum].setText(CONTROLS_TO_SAVE[controlNum])
        self.popupDialog = None

    def resetOne(self, controlNum):
        key = CONTROL_KEYS[controlNum]
        value = _getDefault(key)
        CONTROLS_TO_SAVE[controlNum] = value
        self.entries[controlNum].setText(value)

    def resetAll(self):
        if self.resetDialog:
            return
        self._setButtons(DGG.DISABLED)
        gui = loader.loadModel('phase_3.5/models/gui/optionspage/keybinds_gui.bam')
        self.resetDialog = DirectDialog(
            parent=self.dialog,
            dialogName='altisResetKeybinds',
            image=gui.find('**/base'),
            scale=(6, 3, 3),
            relief=None
        )
        self.resetExit = DirectButton(
            parent=self.resetDialog, relief=None, pos=(0.075, 1, 0.05), scale=(0.025, 1, 0.05),
            image=(gui.find('**/button_neutral'), gui.find('**/button_click'), gui.find('**/button_highlight')),
            command=self.closeResetDialog
        )
        self.resetLabel = DirectLabel(
            parent=self.resetDialog, relief=None, pos=(0, 0, 0),
            text='Reset all keybinds to their defaults?', scale=(0.01, 0.04, 0.02)
        )
        self.resetConfirm = DirectButton(
            parent=self.resetDialog, relief=None, pos=(-0.005, 0, -0.115),
            text='RESET ALL', scale=(0.014, 0.04, 0.028), command=self.confirmResetAll
        )
        gui.removeNode()

    def confirmResetAll(self):
        for controlNum, key in enumerate(CONTROL_KEYS):
            value = _getDefault(key)
            CONTROLS_TO_SAVE[controlNum] = value
            self.entries[controlNum].setText(value)
        self.closeResetDialog()

    def closeResetDialog(self):
        if self.resetDialog:
            try:
                self.resetDialog.cleanup()
            except:
                pass
            self.resetDialog = None
        self._setButtons(DGG.NORMAL)

    def _setButtons(self, state):
        for entry in self.entries:
            entry.setState(state)
        self.resetButton['state'] = state
        self.cancelButton['state'] = state
        self.okButton['state'] = state

    def save(self):
        keymap = settings.get('keymap', {})
        for controlNum, key in enumerate(CONTROL_KEYS):
            keymap[key] = CONTROLS_TO_SAVE.get(controlNum, getattr(base, key, _getDefault(key)))
        settings['keymap'] = keymap
        settings['want-Custom-Controls'] = True
        base.wantCustomControls = True
        base.reloadControls()
        try:
            base.localAvatar.controlManager.reload()
        except:
            pass
        try:
            base.localAvatar.chatMgr.reloadWASD()
        except:
            pass
        messenger.send('reloadActionKeys')
        self.unload()

    def cancel(self):
        self.unload()

    def unload(self):
        if self.unloaded:
            return
        self.unloaded = True
        base.transitions.noFade()
        CONTROLS_TO_SAVE.clear()
        self.ignoreAll()
        if self.popupDialog:
            try:
                self.popupDialog.destroy()
            except:
                pass
            self.popupDialog = None
        if self.resetDialog:
            try:
                self.resetDialog.cleanup()
            except:
                pass
            self.resetDialog = None
        for entry in self.entries:
            entry.destroy()
        self.entries = []
        try:
            self.dialog.destroy()
        except:
            pass
        try:
            self.frame.destroy()
        except:
            pass
        self._restoreOrbitalWheel()
        messenger.send('enable-hotkeys')
        DirectFrame.destroy(self)
