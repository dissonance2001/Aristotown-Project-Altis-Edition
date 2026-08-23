from panda3d.core import Vec3, Vec4, Point3, Plane, PlaneNode, WindowProperties, loadPrcFileData
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectSlider, DirectLabel, OnscreenText, OnscreenImage, DGG
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func, LerpPosInterval, LerpColorScaleInterval
from toontown.menu.MainMenuGlobals import colGlobals, rowStartingZ, rowSeparation, colCondensedGlobals, rowCondensedGlobals
from toontown.settings import ToontownSettings


descriptionFrameSize = (-0.275, 0.275, -0.125, 0.125)

OPTION_LABELS = {
    'acceptingNewFriends': 'Accepting Friend Requests',
    'acceptingNonFriendWhispers': 'Accepting Non-Friend Whispers',
    'tpmsgs': 'Teleport Messages',
    'friendstatusmsgs': 'Friend Status Messages',
    'musicVol': 'Music Volume',
    'sfxVol': 'SFX Volume',
    'toonChatSounds': 'Toon Chat Sounds',
    'aspect-ratio': 'Aspect Ratio',
    'display-mode': 'Display Mode',
    'res': 'Resolution',
    'anisotropic-filtering': 'Anisotropic Filtering',
    'anti-aliasing': 'Anti-Aliasing',
    'vertical-sync': 'Vertical Sync*',
    'show-fps': 'Show FPS Meter',
    'reduce-gui-movement': 'Reduce GUI Movement',
    'smoothanimations': 'Smooth Animations',
    'health-meter-mode': 'Overhead Laff Display',
    'toggle-sprint': 'Toggle Sprint',
    'want-Custom-Controls': 'Custom Keymapping',
    'change-bindings': 'Change Key Bindings',
    'doorkey': 'Door Interaction Key',
    'interactkey': 'NPC Interaction Key',
    'camSensitivityX': 'Horizontal Camera Sensitivity',
    'camSensitivityY': 'Vertical Camera Sensitivity',
    'cam-toggle-lock': 'Right Click Toggles Mouse Control',
    'fieldofview': 'Field Of View',
    'cam-recenter-on-release': 'Recenter on Control Release',
    'cam-recenter-on-movement': 'Recenter on Movement',
}

OPTION_DESCRIPTIONS = {
    'acceptingNewFriends': 'Allows other Toons to send you friend requests.',
    'acceptingNonFriendWhispers': 'Allows Toons who are not on your friends list to whisper to you.',
    'tpmsgs': 'Shows teleport-related messages from other Toons.',
    'friendstatusmsgs': 'Shows messages when friends come online or go offline.',
    'musicVol': 'Adjusts the volume of the music.',
    'sfxVol': 'Adjusts the volume of the sound effects.',
    'toonChatSounds': 'Enables or disables Toon voice sounds when Toons speak.',
    'aspect-ratio': 'Changes the aspect ratio used by the game.',
    'display-mode': 'Changes between windowed, borderless, and fullscreen display modes.',
    'res': 'Changes the game window resolution.',
    'anisotropic-filtering': 'Changes anisotropic filtering to make angled textures less blurry.',
    'anti-aliasing': 'Enables or disables anti-aliasing. A restart may be required for the framebuffer change.',
    'vertical-sync': 'Enables or disables vertical sync. Requires a restart, as in Corporate Clash.',
    'show-fps': 'Shows or hides the FPS meter in the upper-right corner.',
    'reduce-gui-movement': 'Reduces animated movement in supported user interface elements.',
    'smoothanimations': 'Enables or disables Altis smooth animation interpolation. Requires a restart, matching the original Altis behavior.',
    'health-meter-mode': 'Changes when Laff meters are displayed above Toon heads.',
    'toggle-sprint': 'When enabled, press Sprint once to stay sprinting; when disabled, hold Sprint to sprint.',
    'want-Custom-Controls': 'Enables Altis custom keymapping.',
    'change-bindings': 'Opens the key binding editor.',
    'doorkey': 'Requires the interaction key when entering supported doors.',
    'interactkey': 'Requires the interaction key when talking to supported NPCs.',
    'camSensitivityX': 'Adjusts how fast the orbit camera moves left and right.',
    'camSensitivityY': 'Adjusts how fast the orbit camera moves up and down.',
    'cam-toggle-lock': 'Makes right click toggle orbit-camera control instead of requiring it to be held.',
    'fieldofview': 'Adjusts the camera field of view.',
    'cam-recenter-on-release': 'Recenters the orbit camera when camera control is released.',
    'cam-recenter-on-movement': 'Recenters the orbit camera when the Toon starts moving.',
}

DROPDOWN_OPTIONS = {
    'aspect-ratio': ['Adaptive', '4:3', '5:4', '16:9', '21:9'],
    'display-mode': ['Windowed', 'Borderless', 'Fullscreen'],
    'anisotropic-filtering': ['Off', '2x', '4x', '8x', '16x'],
    'health-meter-mode': ['Always Off', 'Always On', 'Default'],
}


def loadOptionsGui():
    try:
        return loader.loadModel('phase_3.5/models/gui/optionspage/options_page')
    except:
        return None


def _node(gui, name):
    if gui is None:
        return None
    try:
        node = gui.find('**/' + name)
        if node.isEmpty():
            return None
        return node
    except:
        return None


def _restoreMousePatterns():
    try:
        base.disableShowbaseMouse()
        base.mouseWatcherNode.setEnterPattern('mouse-enter-%r')
        base.mouseWatcherNode.setLeavePattern('mouse-leave-%r')
        base.mouseWatcherNode.setButtonDownPattern('button-down-%r')
        base.mouseWatcherNode.setButtonUpPattern('button-up-%r')
    except:
        pass


def _requestWindowProperties():
    if not getattr(base, 'win', None):
        return

    mode = int(settings.get('display-mode', 0))
    if mode < 0 or mode > 2:
        mode = 0
        settings['display-mode'] = 0

    res = settings.get('res', [1280, 720])
    try:
        width = max(320, int(res[0]))
        height = max(240, int(res[1]))
    except:
        width = 1280
        height = 720
        settings['res'] = [width, height]

    props = WindowProperties()
    props.setSize(width, height)
    props.setParentWindow(0)

    if mode == 2:
        props.setFullscreen(True)
        props.setUndecorated(False)
        settings['fullscreen'] = True
    elif mode == 1:
        props.setFullscreen(False)
        props.setUndecorated(True)
        settings['fullscreen'] = False
    else:
        props.setFullscreen(False)
        props.setUndecorated(False)
        settings['fullscreen'] = False

    try:
        sort = base.win.getSort()
    except:
        sort = None

    try:
        gsg = base.win.getGsg()
    except:
        gsg = None

    try:
        opened = base.openMainWindow(props=props, gsg=gsg, keepCamera=True)
        if opened is False:
            return
        base.graphicsEngine.openWindows()
        _restoreMousePatterns()
        if sort is not None and getattr(base, 'win', None):
            base.win.setSort(sort)
        base.graphicsEngine.renderFrame()
        base.graphicsEngine.renderFrame()
    except:
        try:
            base.win.requestProperties(props)
            base.graphicsEngine.renderFrame()
        except:
            pass


def _refreshHealthMeters():
    cr = getattr(base, 'cr', None)
    if not cr:
        return
    try:
        avatars = list(cr.doId2do.values())
    except:
        return
    for avatar in avatars:
        update = getattr(avatar, '_DistributedToon__considerUpdateMeter', None)
        if update:
            try:
                update()
            except:
                pass


def applySetting(optionString, value):
    try:
        messenger.send('wakeup')
    except:
        pass

    if optionString in ('acceptingNewFriends', 'acceptingNonFriendWhispers'):
        avatar = getattr(base, 'localAvatar', None)
        if avatar:
            current = settings.get(optionString, {})
            if not isinstance(current, dict):
                current = {}
            current[str(avatar.doId)] = bool(value)
            settings[optionString] = current
            setattr(avatar, optionString, bool(value))
        try:
            messenger.send('option-update-' + optionString, [bool(value)])
        except:
            pass
        return

    settings[optionString] = value
    try:
        messenger.send('option-update-' + optionString, [value])
    except:
        pass

    if optionString == 'musicVol':
        try:
            base.musicManager.setVolume(float(value))
            base.musicActive = float(value) > 0.0
        except:
            pass
    elif optionString == 'sfxVol':
        try:
            for manager in base.sfxManagerList:
                manager.setVolume(float(value))
            base.sfxActive = float(value) > 0.0
        except:
            pass
    elif optionString == 'toonChatSounds':
        base.toonChatSounds = bool(value)
    elif optionString in ('tpmsgs', 'friendstatusmsgs'):
        if hasattr(base, 'toggleTpMsgs'):
            base.toggleTpMsgs()
        else:
            base.wantTpMessages = bool(settings.get('tpmsgs', True))
            base.wantFriendStatusMessagse = bool(settings.get('friendstatusmsgs', True))
    elif optionString == 'aspect-ratio':
        base.Widescreen = int(value)
        if hasattr(base, 'updateAspectRatio'):
            base.updateAspectRatio()
    elif optionString in ('display-mode', 'res'):
        _requestWindowProperties()
    elif optionString == 'anisotropic-filtering':
        if hasattr(base, 'updateAnisotrophicFiltering'):
            base.updateAnisotrophicFiltering()
    elif optionString == 'anti-aliasing':
        if hasattr(base, 'updateAntiAliasing'):
            base.updateAntiAliasing()
    elif optionString == 'vertical-sync':
        loadPrcFileData('', 'sync-video %s' % bool(value))
    elif optionString == 'show-fps':
        enabled = bool(value)
        if hasattr(base, 'setCustomFPSVisible'):
            try:
                base.setCustomFPSVisible(enabled)
            except:
                pass
        fpsFrame = getattr(base, 'fpsFrame', None)
        if fpsFrame is not None:
            try:
                if enabled:
                    fpsFrame.show()
                else:
                    fpsFrame.hide()
            except:
                pass
    elif optionString == 'fieldofview':
        try:
            base.camLens.setMinFov(float(value) / (4.0 / 3.0))
        except:
            pass
    elif optionString in ('doorkey', 'interactkey'):
        if hasattr(base, 'toggleDoorKey'):
            base.toggleDoorKey()
    elif optionString == 'want-Custom-Controls':
        base.wantCustomControls = bool(value)
        if hasattr(base, 'reloadControls'):
            base.reloadControls()
        avatar = getattr(base, 'localAvatar', None)
        if avatar:
            try:
                avatar.controlManager.reload()
            except:
                pass
            try:
                avatar.chatMgr.reloadWASD()
            except:
                pass
    elif optionString == 'toggle-sprint':
        avatar = getattr(base, 'localAvatar', None)
        if avatar and hasattr(avatar, 'reloadMovementHotkeys'):
            avatar.reloadMovementHotkeys()
    elif optionString == 'smoothanimations':
        base.wantSmoothAnims = bool(value)
    elif optionString == 'health-meter-mode':
        base.meterMode = int(value)
        _refreshHealthMeters()


def applyAllSettings():
    keys = (
        'musicVol', 'sfxVol', 'toonChatSounds', 'tpmsgs', 'friendstatusmsgs',
        'aspect-ratio', 'anisotropic-filtering', 'anti-aliasing', 'vertical-sync',
        'show-fps', 'fieldofview', 'doorkey', 'interactkey', 'toggle-sprint', 'want-Custom-Controls',
        'smoothanimations', 'health-meter-mode', 'reduce-gui-movement', 'camSensitivityX',
        'camSensitivityY', 'cam-toggle-lock', 'cam-recenter-on-release', 'cam-recenter-on-movement'
    )
    for key in keys:
        if key in settings:
            try:
                applySetting(key, settings[key])
            except:
                pass
    try:
        _requestWindowProperties()
    except:
        pass


class MainMenuButton(DirectButton):
    def __init__(self, parent=aspect2d, **kw):
        gui = loader.loadModel('phase_3/models/gui/ttcc_menu_buttons')
        optiondefs = (
            ('relief', None, None),
            ('image', (
                gui.find('**/menubtn'),
                gui.find('**/menubtn-press'),
                gui.find('**/menubtn'),
                gui.find('**/menubtn-press'),
            ), None),
            ('image_scale', (.3, .15, .15), None),
            ('image1_scale', (.3, .15, .15), None),
            ('image2_scale', (.3, .15, .15), None),
            ('text_fg', (1, 1, 1, 1), None),
            ('text_shadow', (0, 0, 0, 1), None),
            ('text_scale', 0.05, None),
            ('text_pos', (0, -0.02), None),
            ('hoverScale', 1.1, None),
        )
        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(MainMenuButton)
        scale = self['scale'] or 1.0
        if type(scale) in (int, float):
            hoverScale = scale * self['hoverScale']
        else:
            hoverScale = Vec3(*scale) * self['hoverScale']
        self.bind(DGG.ENTER, hoverButton, [self, hoverScale])
        self.bind(DGG.EXIT, hoverButton, [self, self['scale']])
        gui.removeNode()


class GoodMainMenuButton(MainMenuButton):
    def __init__(self, parent=aspect2d, **kw):
        if 'image_color' not in kw:
            kw['image_color'] = Vec4(0.299805, 0.614258, 1, 1)
        MainMenuButton.__init__(self, parent, **kw)


class BaseOption(DirectButton):
    def __init__(self, optionString, col=0, row=0):
        DirectButton.__init__(self, parent=aspect2d, relief=None, frameSize=descriptionFrameSize)
        self.optionString = optionString
        self.col = col
        self.row = row
        self.extraElements = []
        self.setPos(colGlobals[col], 0, rowStartingZ - (row * rowSeparation))

    def destroy(self):
        self.extraElements = []
        DirectButton.destroy(self)


class ToggleOption(BaseOption):
    def __init__(self, optionString, col=0, row=0):
        BaseOption.__init__(self, optionString, col, row)
        self.gui = loadOptionsGui()
        if optionString in ('acceptingNewFriends', 'acceptingNonFriendWhispers') and getattr(base, 'localAvatar', None):
            current = settings.get(optionString, {})
            if isinstance(current, dict):
                self.isToggledOn = bool(current.get(str(base.localAvatar.doId), getattr(base.localAvatar, optionString, True)))
            else:
                self.isToggledOn = bool(getattr(base.localAvatar, optionString, True))
        else:
            self.isToggledOn = bool(settings.get(optionString, ToontownSettings.DefaultSettings.get(optionString, False)))
        self.label = OnscreenText(parent=self, pos=(0, -0.1), scale=0.05,
                                  text=OPTION_LABELS.get(optionString, optionString), wordwrap=13)
        onImage = _node(self.gui, 'options_on')
        offImage = _node(self.gui, 'options_off')
        hoverImage = _node(self.gui, 'options_hover')
        if onImage is not None and offImage is not None:
            self.onImage = (onImage, hoverImage or onImage, onImage)
            self.offImage = (offImage, hoverImage or offImage, offImage)
            image = self.onImage if self.isToggledOn else self.offImage
            self.checkButton = DirectButton(
                parent=self,
                relief=None,
                image=image,
                image_scale=.125,
                frameSize=(-0.14, 0.14, -0.14, 0.14),
                command=self.toggle
            )
        else:
            self.onImage = None
            self.offImage = None
            self.checkButton = DirectButton(
                parent=self,
                relief=None,
                text='ON' if self.isToggledOn else 'OFF',
                text_scale=0.05,
                frameSize=(-0.12, 0.12, -0.05, 0.05),
                frameColor=(0.75, 0.9, 0.75, 1) if self.isToggledOn else (0.9, 0.75, 0.75, 1),
                command=self.toggle
            )
        self.extraElements = [self.checkButton]

    def _refreshImage(self):
        if self.onImage is not None and self.offImage is not None:
            self.checkButton['image'] = self.onImage if self.isToggledOn else self.offImage
        else:
            self.checkButton['text'] = 'ON' if self.isToggledOn else 'OFF'
            self.checkButton['frameColor'] = (0.75, 0.9, 0.75, 1) if self.isToggledOn else (0.9, 0.75, 0.75, 1)

    def toggle(self):
        self.isToggledOn = not self.isToggledOn
        self._refreshImage()
        applySetting(self.optionString, self.isToggledOn)

    def destroy(self):
        if self.gui is not None:
            self.gui.removeNode()
            self.gui = None
        BaseOption.destroy(self)


class SliderOption(BaseOption):
    def __init__(self, optionString, col=0, row=0, min=0.0, max=1.0, mult=1.0, unit=''):
        BaseOption.__init__(self, optionString, col, row)
        self.actualMin = float(min)
        self.actualMax = float(max)
        self.mult = float(mult)
        self.unit = unit
        self.gui = loadOptionsGui()
        value = float(settings.get(optionString, ToontownSettings.DefaultSettings.get(optionString, min)))
        if value < self.actualMin:
            value = self.actualMin
        elif value > self.actualMax:
            value = self.actualMax
        self.frame = DirectFrame(parent=self, relief=None, scale=0.8)
        sliderBox = _node(self.gui, 'slider_box')
        fillBox = _node(self.gui, 'slider_box_filling')
        pencil = _node(self.gui, 'pencil')
        self.background = None
        self.fillIn = None
        self.clippingPlane = None
        if sliderBox is not None and fillBox is not None:
            self.background = OnscreenImage(parent=self.frame, image=sliderBox, scale=(1, 1, .125))
            self.fillIn = OnscreenImage(parent=self.frame, image=fillBox, scale=(1, 1, .125))
            self.clippingPlane = PlaneNode('clipper')
            self.clippingPlane.setPlane(Plane(Vec3(-1, 0, 0), Point3(-0.308, 0, 0)))
            clipNP = self.fillIn.attachNewNode(self.clippingPlane)
            self.fillIn.setClipPlane(clipNP)
        span = self.actualMax - self.actualMin
        if span < 0.0001:
            span = 0.0001
        normalized = (value - self.actualMin) / span
        sliderKw = {
            'parent': self.frame,
            'value': normalized,
            'range': (0.0, 1.0),
            'pageSize': .05,
            'orientation': DGG.HORIZONTAL,
            'scale': 0.25,
            'frameSize': (-1.32, 1.61, -0.08, 0.08),
            'command': self.onChange,
        }
        if pencil is not None:
            sliderKw['thumb_relief'] = None
            sliderKw['thumb_geom'] = pencil
            sliderKw['thumb_geom_scale'] = (0.5, 1, 0.5)
            sliderKw['frameColor'] = (0, 0, 0, 0)
        self.slider = DirectSlider(**sliderKw)
        self.label = OnscreenText(parent=self, pos=(0, -0.1), scale=0.05, wordwrap=13)
        self._updateLabel(value)
        self.onChange()
        self.extraElements = [self.frame, self.slider]

    def _value(self):
        return self.actualMin + float(self.slider['value']) * (self.actualMax - self.actualMin)

    def _updateLabel(self, value):
        shown = value * self.mult
        if self.mult == 100.0 or self.optionString == 'fieldofview':
            valueText = '%d%s' % (int(round(shown)), self.unit)
        else:
            valueText = '%.2f%s' % (shown, self.unit)
        self.label['text'] = '%s (%s)' % (OPTION_LABELS.get(self.optionString, self.optionString), valueText)

    def onChange(self):
        value = self._value()
        if self.clippingPlane is not None:
            x = -0.308 + (0.612 * float(self.slider['value']))
            self.clippingPlane.setPlane(Plane(Vec3(-1, 0, 0), Point3(x, 0, 0)))
        self._updateLabel(value)
        applySetting(self.optionString, value)

    def destroy(self):
        if self.gui is not None:
            self.gui.removeNode()
            self.gui = None
        BaseOption.destroy(self)


class DropdownOption(BaseOption):
    def __init__(self, optionString, col=0, row=0, options=None):
        BaseOption.__init__(self, optionString, col, row)
        self.gui = loadOptionsGui()
        self.options = options or DROPDOWN_OPTIONS.get(optionString, [])
        self.currentOption = int(settings.get(optionString, ToontownSettings.DefaultSettings.get(optionString, 0)))
        if self.currentOption < 0 or self.currentOption >= len(self.options):
            self.currentOption = 0
        text = self.options[self.currentOption] if self.options else 'Unknown'
        thing = _node(self.gui, 'thing_static')
        press = _node(self.gui, 'dropdown_press')
        hover = _node(self.gui, 'dropdown_hover')
        self.dropdownButton = DirectButton(
            parent=self,
            relief=None,
            text=str(text),
            command=self.openDropdown,
            text_scale=.05,
            text_pos=(0, -0.02),
            image_pos=(0.035, 0, 0.005),
            image_scale=(0.5, 1, 0.25),
            image=(thing, press or thing, hover or thing) if thing is not None else None,
            frameSize=(-0.16, 0.23, -0.055, 0.05)
        )
        self.label = OnscreenText(parent=self, pos=(0, -.1), scale=0.05,
                                  text=OPTION_LABELS.get(optionString, optionString), wordwrap=12)
        self.dropdownButton.bind(DGG.ENTER, hoverButton, [self.dropdownButton, 1.1])
        self.dropdownButton.bind(DGG.EXIT, hoverButton, [self.dropdownButton, 1])
        self.extraElements = [self.dropdownButton]
        self.popup = None
        self.dropdownButtons = []

    def openDropdown(self):
        if self.popup is not None:
            return
        try:
            base.transitions.fadeScreen(0.5)
        except:
            pass
        self.popup = DirectFrame(parent=aspect2d, relief=None, scale=1.2)
        self.popup.setBin('sorted-gui-popup', 3000)
        try:
            self.popup.setPos(self.dropdownButton, 0, 0, 0)
        except:
            self.popup.setPos(0, 0, 0)
        self.createButtons()

    def createButtons(self):
        gui = loadOptionsGui()
        paperTop = _node(gui, 'paper_top')
        paperMiddle = _node(gui, 'paper_middle')
        paperBottom = _node(gui, 'paper_bottom')
        self.dropdownButtons = []
        backBtn = DirectButton(
            parent=self.popup,
            relief=None,
            text='Back',
            command=self.back,
            text_scale=.05,
            text_pos=(0, -0.02),
            image_scale=0.46,
            image=(paperTop, paperTop, paperTop) if paperTop is not None else None,
            image1_color=Vec4(0.8, 0.8, 1, 1),
            image2_color=Vec4(0.8, 0.8, 1, 1),
            image3_color=Vec4(0.5, 0.5, 0.5, 0.5),
            frameSize=(-0.16, 0.16, -0.04, 0.04),
            pos=(0, 0, -0.1)
        )
        self.dropdownButtons.append(backBtn)
        for item in range(len(self.options)):
            isLast = item == len(self.options) - 1
            paper = paperBottom if isLast else paperMiddle
            btn = DirectButton(
                parent=self.popup,
                relief=None,
                text=str(self.options[item]),
                command=self.onChange,
                extraArgs=[item],
                text_scale=.05,
                text_pos=(0, -0.02),
                image_scale=0.46,
                image=(paper, paper, paper) if paper is not None else None,
                image1_color=Vec4(0.8, 0.8, 1, 1),
                image2_color=Vec4(0.8, 0.8, 1, 1),
                image3_color=Vec4(0.5, 0.5, 0.5, 0.5),
                frameSize=(-0.16, 0.16, -0.04, 0.04),
                pos=(0, 0, -0.175 - (0.075 * item))
            )
            self.dropdownButtons.append(btn)
        self.accept('stickerBookExited', self.back)
        staggeredFadeUp(self.dropdownButtons)
        if gui is not None:
            gui.removeNode()

    def onChange(self, value):
        self.currentOption = int(value)
        self.dropdownButton['text'] = str(self.options[self.currentOption])
        applySetting(self.optionString, self.currentOption)
        self.back()

    def back(self):
        self.ignore('stickerBookExited')
        if self.popup is not None:
            self.popup.destroy()
            self.popup = None
        self.dropdownButtons = []
        try:
            base.transitions.noFade()
        except:
            pass

    def destroy(self):
        self.back()
        if self.gui is not None:
            self.gui.removeNode()
            self.gui = None
        BaseOption.destroy(self)


class ResolutionPicker(BaseOption):
    def __init__(self, optionString='res', col=0, row=0):
        BaseOption.__init__(self, optionString, col, row)
        self.gui = loadOptionsGui()
        self.resolutions = []
        for item in getattr(base, 'resList', []):
            try:
                resolution = (int(item[0]), int(item[1]))
            except:
                continue
            if resolution[0] >= 800 and resolution[1] >= 600 and resolution not in self.resolutions:
                self.resolutions.append(resolution)
        current = settings.get('res', [1280, 720])
        try:
            currentTuple = (int(current[0]), int(current[1]))
        except:
            currentTuple = (1280, 720)
        if currentTuple not in self.resolutions:
            self.resolutions.append(currentTuple)
        self.resolutions.sort()
        thing = _node(self.gui, 'thing_static')
        press = _node(self.gui, 'dropdown_press')
        hover = _node(self.gui, 'dropdown_hover')
        self.dropdownButton = DirectButton(
            parent=self,
            relief=None,
            text='%dx%d' % currentTuple,
            command=self.openDropdown,
            text_scale=.05,
            text_pos=(0, -0.02),
            image_pos=(0.035, 0, 0.005),
            image_scale=(0.5, 1, 0.25),
            image=(thing, press or thing, hover or thing) if thing is not None else None,
            frameSize=(-0.16, 0.23, -0.055, 0.05)
        )
        self.label = OnscreenText(parent=self, pos=(0, -.1), scale=0.05, text='Resolution', wordwrap=12)
        self.dropdownButton.bind(DGG.ENTER, hoverButton, [self.dropdownButton, 1.1])
        self.dropdownButton.bind(DGG.EXIT, hoverButton, [self.dropdownButton, 1])
        self.extraElements = [self.dropdownButton]
        self.dialog = None
        self.dropdownButtons = []

    def openDropdown(self):
        if self.dialog is not None:
            return
        try:
            base.transitions.fadeScreen(0.5)
        except:
            pass
        self.dialog = DirectFrame(parent=aspect2d, relief=None, scale=1.2)
        self.dialog.setBin('sorted-gui-popup', 3000)
        try:
            self.dialog.setPos(self.dropdownButton, 0, 0, 0)
        except:
            self.dialog.setPos(0, 0, 0)
        self.createButtons()

    def createButtons(self):
        gui = loadOptionsGui()
        paperTop = _node(gui, 'paper_top')
        paperMiddle = _node(gui, 'paper_middle')
        paperBottom = _node(gui, 'paper_bottom')
        self.dropdownButtons = []
        backBtn = DirectButton(
            parent=self.dialog,
            relief=None,
            text='Back',
            command=self.back,
            text_scale=.05,
            text_pos=(0, -0.02),
            image_scale=0.46,
            image=(paperTop, paperTop, paperTop) if paperTop is not None else None,
            image1_color=Vec4(0.8, 0.8, 1, 1),
            image2_color=Vec4(0.8, 0.8, 1, 1),
            image3_color=Vec4(0.5, 0.5, 0.5, 0.5),
            frameSize=(-0.16, 0.16, -0.04, 0.04),
            pos=(0, 0, -0.1)
        )
        self.dropdownButtons.append(backBtn)
        for item in range(len(self.resolutions)):
            isLast = item == len(self.resolutions) - 1
            paper = paperBottom if isLast else paperMiddle
            resolution = self.resolutions[item]
            btn = DirectButton(
                parent=self.dialog,
                relief=None,
                text='%dx%d' % resolution,
                command=self.onChange,
                extraArgs=[resolution[0], resolution[1]],
                text_scale=.05,
                text_pos=(0, -0.02),
                image_scale=0.46,
                image=(paper, paper, paper) if paper is not None else None,
                image1_color=Vec4(0.8, 0.8, 1, 1),
                image2_color=Vec4(0.8, 0.8, 1, 1),
                image3_color=Vec4(0.5, 0.5, 0.5, 0.5),
                frameSize=(-0.16, 0.16, -0.04, 0.04),
                pos=(0, 0, -0.175 - (0.075 * item))
            )
            self.dropdownButtons.append(btn)
        self.accept('stickerBookExited', self.back)
        staggeredFadeUp(self.dropdownButtons)
        if gui is not None:
            gui.removeNode()

    def onChange(self, x, y):
        self.dropdownButton['text'] = '%dx%d' % (x, y)
        applySetting('res', [int(x), int(y)])
        self.back()

    def back(self):
        self.ignore('stickerBookExited')
        if self.dialog is not None:
            self.dialog.destroy()
            self.dialog = None
        self.dropdownButtons = []
        try:
            base.transitions.noFade()
        except:
            pass

    def destroy(self):
        self.back()
        if self.gui is not None:
            self.gui.removeNode()
            self.gui = None
        BaseOption.destroy(self)


def hoverButton(button, scale, event=None):
    if scale is None:
        scale = 1.0
    if settings.get('reduce-gui-movement', False):
        button.setScale(Vec3(scale))
        return
    Sequence(
        button.scaleInterval(.1, Vec3(scale) * 1.1, blendType='easeInOut'),
        button.scaleInterval(.1, Vec3(scale), blendType='easeInOut')
    ).start()


def staggeredFadeUp(items):
    if settings.get('reduce-gui-movement', False):
        for item in items:
            if item:
                item.setColorScale(1, 1, 1, 1)
        return
    seq = Sequence()
    for item in items:
        if item:
            item.setTransparency(1)
            finalPos = item.getPos()
            startPos = Point3(finalPos) - Point3(0, 0, .2)
            item.setColorScale(1, 1, 1, 0)
            par = Parallel(
                LerpPosInterval(item, .2, finalPos, startPos, blendType='easeInOut'),
                LerpColorScaleInterval(item, .2, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0), blendType='easeInOut')
            )
            seq.append(Func(par.start))
            seq.append(Wait(.05))
    seq.start()


def staggeredFadePopin(items, scales=None):
    if settings.get('reduce-gui-movement', False):
        for i in range(len(items)):
            item = items[i]
            if item:
                scale = scales[i] if scales else item.getScale()
                item.setScale(scale)
                item.setColorScale(1, 1, 1, 1)
        return
    seq = Sequence()
    for i in range(len(items)):
        item = items[i]
        if item:
            scale = scales[i] if scales else item.getScale()
            item.setTransparency(1)
            item.setScale(0.01)
            item.setColorScale(1, 1, 1, 0)
            par = Parallel(
                Sequence(
                    item.scaleInterval(.2, Vec3(scale * 1.1), blendType='easeInOut'),
                    item.scaleInterval(.1, Vec3(scale), blendType='easeInOut')
                ),
                LerpColorScaleInterval(item, .2, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0), blendType='easeInOut')
            )
            seq.append(Func(par.start))
            seq.append(Wait(.05))
    seq.start()
