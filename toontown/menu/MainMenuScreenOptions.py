import copy
import math

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel, DGG
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import Parallel, LerpFunc
from panda3d.core import Vec3, Point3, Plane, PlaneNode
from pandac.PandaModules import PGButton, MouseButton

from toontown.menu.MainMenuScreen import MainMenuScreen
from toontown.menu import MainMenuGui, MainMenuGlobals
from toontown.settings import ToontownSettings
from toontown.shtiker import ControlRemapDialog
from toontown.toontowngui import TTDialog

try:
    _wheelUpButton = MouseButton.wheelUp()
    _wheelDownButton = MouseButton.wheelDown()
except AttributeError:
    _wheelUpButton = MouseButton.wheel_up()
    _wheelDownButton = MouseButton.wheel_down()

GUI_WHEEL_UP = PGButton.getPressPrefix() + _wheelUpButton.getName() + '-'
GUI_WHEEL_DOWN = PGButton.getPressPrefix() + _wheelDownButton.getName() + '-'


class MainMenuScreenOptions(MainMenuScreen, FSM):
    def __init__(self):
        self.socialOptions = []
        self.audioOptions = []
        self.displayOptions = []
        self.accessibilityOptions = []
        self.gameplayOptions = []
        self.controlOptions = []
        self.cameraOptions = []
        self.currentOptions = ''
        self.currentRow = 0
        self.totalRows = 1
        self.buttonSeqs = {}
        self.resettingOptions = 0
        self.firstLoad = 1
        self.confirm = None
        self.controlDialog = None
        MainMenuScreen.__init__(self)
        FSM.__init__(self, 'MainMenuOptions')
        self.request('Social')
        self.firstLoad = 0

    def _imageSet(self, gui, names):
        images = []
        for name in names:
            images.append(MainMenuGui._node(gui, name))
        if not images or images[0] is None:
            return None
        for i in xrange(len(images)):
            if images[i] is None:
                images[i] = images[0]
        return tuple(images)

    def _makeTab(self, gui, parent, pos, nodeName, text, stateName):
        image = MainMenuGui._node(gui, nodeName)
        kw = dict(parent=parent, relief=None, pos=pos, command=lambda: self.request(stateName),
                  frameSize=(-.12, .1, 0, .1), sortOrder=0)
        if image is not None:
            kw['image'] = image
            kw['image_scale'] = (0.35, 1, 0.175)
            kw['image_pos'] = (0, 0, 0.02)
        else:
            kw['relief'] = DGG.RAISED
            kw['text'] = text
            kw['text_scale'] = 0.035
            kw['frameSize'] = (-0.115, 0.115, -0.045, 0.045)
            kw['frameColor'] = (0.9, 0.85, 0.65, 1)
        button = DirectButton(**kw)
        button.bind(DGG.ENTER, self.onMouseEnter, [button])
        button.bind(DGG.EXIT, self.onMouseExit, [button])
        self.uiItems.append(button)
        return button

    def createUI(self):
        bookModel = loader.loadModel('phase_3.5/models/gui/stickerbook_gui')
        self.frame = DirectFrame(parent=self, relief=None)
        self.background = DirectFrame(parent=self.frame, relief=None, scale=Vec3(2, 1, 1.5),
                                      image=bookModel.find('**/big_book'))
        self.uiItems.append(self.background)
        self.setPos(0, 0, -.05)
        self.setScale(1.2)

        gui = MainMenuGui.loadOptionsGui()
        backgroundImage = MainMenuGui._node(gui, 'options_bg')
        titleImage = MainMenuGui._node(gui, 'options_title')
        descriptionImage = MainMenuGui._node(gui, 'options_dialoguebox')

        if backgroundImage is not None:
            self.pageBorder = DirectFrame(parent=self, relief=None, image=backgroundImage,
                                          pos=(0.01, 0, -0.13), scale=1.7)
        else:
            self.pageBorder = DirectFrame(parent=self, relief=DGG.FLAT, frameColor=(0.98, 0.94, 0.75, 1),
                                          frameSize=(-0.92, 0.92, -0.48, 0.5), pos=(0.01, 0, -0.13))
        self.uiItems.append(self.pageBorder)

        if titleImage is not None:
            self.title = DirectFrame(parent=self, relief=None, image=titleImage,
                                     pos=(0.025, 0, 0.62), scale=(1.1, 1, 0.275))
        else:
            self.title = DirectLabel(parent=self, relief=None, text='Options', text_scale=0.08,
                                     pos=(0.025, 0, 0.59))
        self.uiItems.append(self.title)

        arrowStatic = MainMenuGui._node(gui, 'arrow_static')
        arrowPress = MainMenuGui._node(gui, 'arrow_press')
        arrowHover = MainMenuGui._node(gui, 'arrow_hover')
        if arrowStatic is not None:
            arrowImages = (arrowStatic, arrowPress or arrowStatic, arrowHover or arrowStatic)
            self.upArrow = DirectButton(parent=self, relief=None, image=arrowImages, scale=0.15,
                                        pos=(0.73, 0, 0.05), command=self.previousRow)
            self.downArrow = DirectButton(parent=self, relief=None, image=arrowImages, scale=(-0.15, 1, 0.15),
                                          pos=(0.73, 0, -0.175), hpr=(0, 0, 180), command=self.nextRow)
        else:
            self.upArrow = DirectButton(parent=self, text='^', text_scale=0.07, scale=0.8,
                                        pos=(0.73, 0, 0.05), command=self.previousRow)
            self.downArrow = DirectButton(parent=self, text='v', text_scale=0.07, scale=0.8,
                                          pos=(0.73, 0, -0.175), command=self.nextRow)
        self.uiItems.extend([self.upArrow, self.downArrow])

        self.rowNumberLabel = DirectLabel(parent=self, relief=None, pos=(0.729, 0, -0.08),
                                          text_scale=0.06, text='1/1')
        self.uiItems.append(self.rowNumberLabel)

        if descriptionImage is not None:
            self.optionDescriptionBox = DirectFrame(parent=self, relief=None, image=descriptionImage,
                                                     pos=(0.035, 0, -0.4), scale=(2.3, 1, 0.2875))
        else:
            self.optionDescriptionBox = DirectFrame(parent=self, relief=DGG.FLAT,
                                                     frameColor=(0.92, 0.86, 0.65, 1),
                                                     frameSize=(-0.77, 0.77, -0.09, 0.09),
                                                     pos=(0.035, 0, -0.4))
        self.uiItems.append(self.optionDescriptionBox)
        self.optionDescriptionLabel = DirectLabel(parent=self.optionDescriptionBox, relief=None,
                                                   text='Hover over an option for a description.',
                                                   text_scale=0.16, text_wordwrap=34,
                                                   pos=(-0.015, 0, 0.12), scale=(0.125, 1, 1))
        self.uiItems.append(self.optionDescriptionLabel)

        tabPos = (-0.80, -0.533, -0.266, 0.000, 0.266, 0.533, 0.800)
        self.tabSocial = self._makeTab(gui, self.frame, (tabPos[0], 0, .7), 'tab_privacy', 'Social', 'Social')
        self.tabAudio = self._makeTab(gui, self.frame, (tabPos[1], 0, .7), 'tab_audio', 'Audio', 'Audio')
        self.tabDisplay = self._makeTab(gui, self.frame, (tabPos[2], 0, .7), 'tab_video', 'Display', 'Display')
        self.tabAccessibility = self._makeTab(gui, self.frame, (tabPos[3], 0, .7), 'tab_accessibility', 'Access', 'Accessibility')
        self.tabGameplay = self._makeTab(gui, self.frame, (tabPos[4], 0, .7), 'tab_gameplay', 'Game', 'Gameplay')
        self.tabControls = self._makeTab(gui, self.frame, (tabPos[5], 0, .7), 'tab_controls', 'Controls', 'Controls')
        self.tabCamera = self._makeTab(gui, self.frame, (tabPos[6], 0, .7), 'tab_camera', 'Camera', 'Camera')

        resetImages = self._imageSet(gui, ('reset_static', 'reset_press', 'reset_hover'))
        resetAllImages = self._imageSet(gui, ('resetall_static', 'resetall_press', 'resetall_hover'))
        if resetImages is not None:
            self.resetButton = DirectButton(parent=self, relief=None, image=resetImages, scale=(0.3, 1, 0.15),
                                            pos=(-0.65, 0, -.6), frameSize=(-0.45, 0.45, -0.45, 0.45), command=lambda: self._showResetConfirm(0))
        else:
            self.resetButton = DirectButton(parent=self, text='Reset Page', text_scale=0.045,
                                            pos=(-0.62, 0, -.6), command=lambda: self._showResetConfirm(0))
        if resetAllImages is not None:
            self.resetAllButton = DirectButton(parent=self, relief=None, image=resetAllImages, scale=(0.6, 1, 0.15),
                                               pos=(-0.25, 0, -.6), frameSize=(-0.35, 0.35, -0.35, 0.35), command=lambda: self._showResetConfirm(1))
        else:
            self.resetAllButton = DirectButton(parent=self, text='Reset All', text_scale=0.045,
                                               pos=(-0.25, 0, -.6), frameSize=(-0.35, 0.35, -0.35, 0.35), command=lambda: self._showResetConfirm(1))
        self.uiItems.extend([self.resetButton, self.resetAllButton])

        exitImages = self._imageSet(gui, ('exit_static', 'exit_press', 'exit_hover'))
        if exitImages is not None:
            self.exitButton = DirectButton(parent=self, relief=None, image=exitImages, scale=(0.425, 1, 0.20),
                                           sortOrder=2, pos=(0.45, 0, -0.62), hpr=(0, 0, -5), command=self._goBack)
        else:
            self.exitButton = DirectButton(parent=self, text='Back', text_scale=0.055,
                                           pos=(0.48, 0, -0.6), command=self._goBack)
        self.uiItems.append(self.exitButton)

        self.background['state'] = DGG.NORMAL
        self.background.bind(GUI_WHEEL_UP, self._wheelPage, [-1])
        self.background.bind(GUI_WHEEL_DOWN, self._wheelPage, [1])

        if gui is not None:
            gui.removeNode()
        bookModel.removeNode()

    def _goBack(self):
        base.cr.mainmenu.request('Play')

    def enableButtons(self):
        for button in (self.tabSocial, self.tabAudio, self.tabDisplay, self.tabAccessibility,
                       self.tabGameplay, self.tabControls, self.tabCamera):
            button['state'] = DGG.NORMAL

    def onMouseEnter(self, button, event=None):
        self.moveTabUp(button)

    def onMouseExit(self, button, event=None):
        if button['state'] == DGG.NORMAL:
            self.moveTabDown(button)

    def moveTabUp(self, button):
        if not button:
            return
        try:
            currentPos = button['image_pos'][2]
            currentSize = button['frameSize'][3]
        except:
            return
        sequence = self.buttonSeqs.get(button)
        if sequence:
            sequence.pause()
        if settings.get('reduce-gui-movement', False):
            self.updateTabSize(.174, button)
            self.updateTabPos(.1, button)
            return
        sequence = Parallel(
            LerpFunc(self.updateTabSize, fromData=currentSize, toData=.174, duration=.25, extraArgs=[button]),
            LerpFunc(self.updateTabPos, fromData=currentPos, toData=.1, duration=.25, extraArgs=[button])
        )
        self.buttonSeqs[button] = sequence
        sequence.start()

    def moveTabDown(self, button):
        if self.resettingOptions or not button:
            return
        try:
            currentPos = button['image_pos'][2]
            currentSize = button['frameSize'][3]
        except:
            return
        sequence = self.buttonSeqs.get(button)
        if sequence:
            sequence.pause()
        if settings.get('reduce-gui-movement', False):
            self.updateTabSize(.1, button)
            self.updateTabPos(.02, button)
            return
        sequence = Parallel(
            LerpFunc(self.updateTabSize, fromData=currentSize, toData=.1, duration=.25, extraArgs=[button]),
            LerpFunc(self.updateTabPos, fromData=currentPos, toData=.02, duration=.25, extraArgs=[button])
        )
        self.buttonSeqs[button] = sequence
        sequence.start()

    def updateTabSize(self, value, button):
        try:
            size = button['frameSize']
            button['frameSize'] = (size[0], size[1], size[2], value)
        except:
            pass

    def updateTabPos(self, value, button):
        try:
            pos = button['image_pos']
            button['image_pos'] = (pos[0], pos[1], value)
        except:
            pass

    def getCurrentOptionList(self):
        return getattr(self, self.currentOptions, []) if self.currentOptions else self.socialOptions

    def _destroyOptions(self, optionList):
        while optionList:
            option = optionList.pop()
            try:
                option.destroy()
            except:
                pass

    def _finishTab(self):
        optionList = self.getCurrentOptionList()
        for option in optionList:
            option.reparentTo(self)
            if hasattr(option, 'optionString'):
                option.bind(DGG.ENTER, self.updateDescription, [option.optionString])
                option.bind(DGG.EXIT, self.clearDescription)
                option.bind(GUI_WHEEL_UP, self._wheelPage, [-1])
                option.bind(GUI_WHEEL_DOWN, self._wheelPage, [1])
                for extra in getattr(option, 'extraElements', []):
                    extra.bind(GUI_WHEEL_UP, self._wheelPage, [-1])
                    extra.bind(GUI_WHEEL_DOWN, self._wheelPage, [1])
        rows = [option.row for option in optionList if hasattr(option, 'row')]
        lowestRow = max(rows) if rows else 0
        self.currentRow = 0
        self.totalRows = int(math.floor(float(lowestRow) / MainMenuGlobals.maxRowsShownAtOnce)) + 1
        self.updatePageVisibility()

    def updatePageVisibility(self):
        optionList = self.getCurrentOptionList()
        for option in optionList:
            if not hasattr(option, 'row'):
                option.show()
                continue
            page = int(option.row) / MainMenuGlobals.maxRowsShownAtOnce
            if page == self.currentRow:
                option.setZ(MainMenuGlobals.rowStartingZ - ((option.row % MainMenuGlobals.maxRowsShownAtOnce) * MainMenuGlobals.rowSeparation))
                option.show()
            else:
                option.hide()
        self.rowNumberLabel['text'] = '%d/%d' % (self.currentRow + 1, self.totalRows)
        self.upArrow['state'] = DGG.DISABLED if self.currentRow <= 0 else DGG.NORMAL
        self.downArrow['state'] = DGG.DISABLED if self.currentRow >= self.totalRows - 1 else DGG.NORMAL

    def previousRow(self):
        if self.currentRow > 0:
            self.currentRow -= 1
            self.updatePageVisibility()

    def nextRow(self):
        if self.currentRow < self.totalRows - 1:
            self.currentRow += 1
            self.updatePageVisibility()

    def _wheelPage(self, direction, event=None):
        if direction < 0:
            self.previousRow()
        else:
            self.nextRow()

    def updateDescription(self, optionString, event=None):
        self.optionDescriptionLabel['text'] = MainMenuGui.OPTION_DESCRIPTIONS.get(optionString, optionString)

    def clearDescription(self, event=None):
        self.optionDescriptionLabel['text'] = 'Hover over an option for a description.'

    def enterSocial(self):
        self.currentOptions = 'socialOptions'
        self.socialOptions = []
        self.enableButtons()
        self.tabSocial['state'] = DGG.DISABLED
        if self.firstLoad:
            self.moveTabUp(self.tabSocial)
        if getattr(self, 'inGameOptions', False) and getattr(base, 'localAvatar', None):
            self.socialOptions.append(MainMenuGui.ToggleOption('acceptingNewFriends', 0, 0))
            self.socialOptions.append(MainMenuGui.ToggleOption('acceptingNonFriendWhispers', 1, 0))
            self.socialOptions.append(MainMenuGui.ToggleOption('tpmsgs', 0, 1))
            self.socialOptions.append(MainMenuGui.ToggleOption('friendstatusmsgs', 1, 1))
            self.resetButton['state'] = DGG.NORMAL
        else:
            label = DirectLabel(parent=aspect2d, relief=None, text_scale=0.07,
                                text='Social options are available in game.')
            label.row = 0
            label.col = 0
            self.socialOptions.append(label)
            self.resetButton['state'] = DGG.DISABLED
        self.resetAllButton['state'] = DGG.NORMAL
        self._finishTab()

    def exitSocial(self):
        self.moveTabDown(self.tabSocial)
        self._destroyOptions(self.socialOptions)

    def enterAudio(self):
        self.currentOptions = 'audioOptions'
        self.audioOptions = []
        self.enableButtons()
        self.tabAudio['state'] = DGG.DISABLED
        self.audioOptions.append(MainMenuGui.SliderOption('musicVol', 0, 0, 0, 1, 100, '%'))
        self.audioOptions.append(MainMenuGui.SliderOption('sfxVol', 1, 0, 0, 1, 100, '%'))
        self.audioOptions.append(MainMenuGui.ToggleOption('toonChatSounds', 0, 1))
        self.resetButton['state'] = DGG.NORMAL
        self.resetAllButton['state'] = DGG.NORMAL
        self._finishTab()

    def exitAudio(self):
        self.moveTabDown(self.tabAudio)
        self._destroyOptions(self.audioOptions)

    def enterDisplay(self):
        self.currentOptions = 'displayOptions'
        self.displayOptions = []
        self.enableButtons()
        self.tabDisplay['state'] = DGG.DISABLED
        self.displayOptions.append(MainMenuGui.DropdownOption('aspect-ratio', 0, 0))
        self.displayOptions.append(MainMenuGui.DropdownOption('display-mode', 1, 0))
        self.displayOptions.append(MainMenuGui.ResolutionPicker('res', 0, 1))
        self.displayOptions.append(MainMenuGui.DropdownOption('anisotropic-filtering', 1, 1))
        self.displayOptions.append(MainMenuGui.ToggleOption('anti-aliasing', 0, 2))
        self.displayOptions.append(MainMenuGui.ToggleOption('vertical-sync', 1, 2))
        self.displayOptions.append(MainMenuGui.ToggleOption('show-fps', 0, 3))
        self.resetButton['state'] = DGG.NORMAL
        self.resetAllButton['state'] = DGG.NORMAL
        self._finishTab()

    def exitDisplay(self):
        self.moveTabDown(self.tabDisplay)
        self._destroyOptions(self.displayOptions)

    def enterAccessibility(self):
        self.currentOptions = 'accessibilityOptions'
        self.accessibilityOptions = []
        self.enableButtons()
        self.tabAccessibility['state'] = DGG.DISABLED
        self.accessibilityOptions.append(MainMenuGui.ToggleOption('reduce-gui-movement', 0, 0))
        self.accessibilityOptions.append(MainMenuGui.ToggleOption('smoothanimations', 1, 0))
        self.resetButton['state'] = DGG.NORMAL
        self.resetAllButton['state'] = DGG.NORMAL
        self._finishTab()

    def exitAccessibility(self):
        self.moveTabDown(self.tabAccessibility)
        self._destroyOptions(self.accessibilityOptions)

    def enterGameplay(self):
        self.currentOptions = 'gameplayOptions'
        self.gameplayOptions = []
        self.enableButtons()
        self.tabGameplay['state'] = DGG.DISABLED
        self.gameplayOptions.append(MainMenuGui.DropdownOption('health-meter-mode', 0, 0))
        self.gameplayOptions.append(MainMenuGui.ToggleOption('toggle-sprint', 1, 0))
        self.resetButton['state'] = DGG.NORMAL
        self.resetAllButton['state'] = DGG.NORMAL
        self._finishTab()

    def exitGameplay(self):
        self.moveTabDown(self.tabGameplay)
        self._destroyOptions(self.gameplayOptions)

    def enterControls(self):
        self.currentOptions = 'controlOptions'
        self.controlOptions = []
        self.enableButtons()
        self.tabControls['state'] = DGG.DISABLED
        guiButton = loader.loadModel('phase_3.5/models/gui/optionspage/options_page')
        changeButton = DirectButton(parent=aspect2d, relief=None,
                                    image=(guiButton.find('**/keybinds_static'),
                                           guiButton.find('**/keybinds_press'),
                                           guiButton.find('**/keybinds_hover')),
                                    image_scale=(1, 1, 0.5), scale=0.35,
                                    pos=(MainMenuGlobals.colGlobals[0], 0, MainMenuGlobals.rowStartingZ),
                                    command=self.openKeyRebinding)
        changeButton.optionString = 'change-bindings'
        changeButton.row = 0
        changeButton.col = 0
        changeButton.extraElements = []
        self.controlOptions.append(changeButton)
        self.controlOptions.append(MainMenuGui.ToggleOption('doorkey', 1, 0))
        self.controlOptions.append(MainMenuGui.ToggleOption('interactkey', 1, 1))
        guiButton.removeNode()
        self.resetButton['state'] = DGG.NORMAL
        self.resetAllButton['state'] = DGG.NORMAL
        self._finishTab()
        changeButton.configure(frameSize=(-0.44, 0.44, -0.18, 0.18))

    def exitControls(self):
        self.moveTabDown(self.tabControls)
        self._destroyOptions(self.controlOptions)

    def enterCamera(self):
        self.currentOptions = 'cameraOptions'
        self.cameraOptions = []
        self.enableButtons()
        self.tabCamera['state'] = DGG.DISABLED
        self.cameraOptions.append(MainMenuGui.SliderOption('camSensitivityX', 0, 0, 0.05, 1.0, 10, ''))
        self.cameraOptions.append(MainMenuGui.SliderOption('camSensitivityY', 1, 0, 0.05, 1.0, 10, ''))
        self.cameraOptions.append(MainMenuGui.SliderOption('fieldofview', 0, 1, 30, 120, 1, ' deg'))
        self.cameraOptions.append(MainMenuGui.ToggleOption('cam-toggle-lock', 1, 1))
        self.cameraOptions.append(MainMenuGui.ToggleOption('cam-recenter-on-release', 0, 2))
        self.cameraOptions.append(MainMenuGui.ToggleOption('cam-recenter-on-movement', 1, 2))
        self.resetButton['state'] = DGG.NORMAL
        self.resetAllButton['state'] = DGG.NORMAL
        self._finishTab()

    def exitCamera(self):
        self.moveTabDown(self.tabCamera)
        self._destroyOptions(self.cameraOptions)

    def openKeyRebinding(self):
        messenger.send('wakeup')
        if not settings.get('want-Custom-Controls', False):
            MainMenuGui.applySetting('want-Custom-Controls', True)
        self.controlDialog = ControlRemapDialog.ControlRemap()

    def _showResetConfirm(self, resetAll):
        if self.confirm is not None:
            return
        message = 'Are you sure you want to reset ALL of your settings?' if resetAll else 'Are you sure you want to reset this page?'
        self.confirm = TTDialog.TTGlobalDialog(doneEvent='altisOptionsResetDone', message=message, style=TTDialog.TwoChoice)
        self.confirm.show()
        self.acceptOnce('altisOptionsResetDone', self._handleResetConfirm, [resetAll])

    def _handleResetConfirm(self, resetAll):
        status = self.confirm.doneStatus
        self.confirm.cleanup()
        self.confirm = None
        if status == 'ok':
            self.setDefaultSettings(resetAll)

    def setDefaultSettings(self, resetAll):
        socialKeys = ('acceptingNewFriends', 'acceptingNonFriendWhispers')
        if resetAll:
            for key, value in ToontownSettings.DefaultSettings.items():
                if key in socialKeys and getattr(base, 'localAvatar', None):
                    MainMenuGui.applySetting(key, True)
                else:
                    settings[key] = copy.deepcopy(value)
        else:
            for option in self.getCurrentOptionList():
                key = getattr(option, 'optionString', None)
                if key in socialKeys and getattr(base, 'localAvatar', None):
                    MainMenuGui.applySetting(key, True)
                elif key in ToontownSettings.DefaultSettings:
                    settings[key] = copy.deepcopy(ToontownSettings.DefaultSettings[key])
        MainMenuGui.applyAllSettings()
        self.refreshCurTab()

    def refreshCurTab(self):
        reloadMap = {
            'socialOptions': (self.exitSocial, self.enterSocial),
            'audioOptions': (self.exitAudio, self.enterAudio),
            'displayOptions': (self.exitDisplay, self.enterDisplay),
            'accessibilityOptions': (self.exitAccessibility, self.enterAccessibility),
            'gameplayOptions': (self.exitGameplay, self.enterGameplay),
            'controlOptions': (self.exitControls, self.enterControls),
            'cameraOptions': (self.exitCamera, self.enterCamera),
        }
        funcs = reloadMap.get(self.currentOptions)
        if funcs:
            self.resettingOptions = 1
            funcs[0]()
            funcs[1]()
            self.resettingOptions = 0

    def destroy(self):
        if self.confirm is not None:
            try:
                self.confirm.cleanup()
            except:
                pass
            self.confirm = None
        for sequence in self.buttonSeqs.values():
            try:
                sequence.pause()
            except:
                pass
        self.buttonSeqs = {}
        self._destroyOptions(self.socialOptions)
        self._destroyOptions(self.audioOptions)
        self._destroyOptions(self.displayOptions)
        self._destroyOptions(self.accessibilityOptions)
        self._destroyOptions(self.gameplayOptions)
        self._destroyOptions(self.controlOptions)
        self._destroyOptions(self.cameraOptions)
        self.ignoreAll()
        FSM.cleanup(self)
        MainMenuScreen.destroy(self)
