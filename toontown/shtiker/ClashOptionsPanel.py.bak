from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel, DGG
from direct.interval.IntervalGlobal import Parallel, LerpFunc
from panda3d.core import Vec3

from toontown.menu import MainMenuScreenOptions, MainMenuGui


class ClashOptionsPanel(MainMenuScreenOptions.MainMenuScreenOptions):
    PanelScale = 0.97

    def __init__(self, bookPage):
        self.bookPage = bookPage
        self.inGameOptions = True
        MainMenuScreenOptions.MainMenuScreenOptions.__init__(self)
        self.hide()

    def createUI(self):
        bookModel = loader.loadModel('phase_3.5/models/gui/cc_m_txc_gui_options_bg')
        self.frame = DirectFrame(parent=self, relief=None)
        self.background = DirectFrame(
            parent=self.frame,
            relief=None,
            scale=Vec3(1.775, 1, 1.8),
            sortOrder=1,
            pos=(0, 0, 0.041),
            image=bookModel.find('**/options_bg')
        )
        self.uiItems.append(self.background)

        self.background['state'] = DGG.NORMAL
        self.background.bind(MainMenuScreenOptions.GUI_WHEEL_UP, self._wheelPage, [-1])
        self.background.bind(MainMenuScreenOptions.GUI_WHEEL_DOWN, self._wheelPage, [1])

        self._createClashCommonUI()
        for passiveItem in (self.pageBorder, self.title, self.optionDescriptionBox, self.optionDescriptionLabel):
            try:
                passiveItem.guiItem.setActive(False)
            except:
                pass

        self.setPos(0, 0, -0.05)
        self.setScale(self.PanelScale)

        gui = MainMenuGui.loadOptionsGui()
        exitImages = self._imageSet(gui, ('exit_static', 'exit_press', 'exit_hover'))
        self.exitButton = DirectButton(
            parent=self,
            relief=None,
            image=exitImages,
            scale=(0.425, 1, 0.20),
            sortOrder=2,
            pos=(0.45, 0, -0.62),
            hpr=(0, 0, -5),
            command=self._goBack
        )
        self.uiItems.append(self.exitButton)

        moveTabs = [
            self.tabSocial,
            self.tabAudio,
            self.tabDisplay,
            self.tabAccessibility,
            self.tabGameplay,
            self.tabControls,
            self.tabCamera,
        ]
        startPos = -0.98
        endPos = 0.75
        posMove = (abs(startPos) + endPos) / len(moveTabs)
        for i, tab in enumerate(moveTabs):
            tab.reparentTo(self.frame)
            tab.setPos(startPos + (posMove * (i + 1)), 0, 0.730)
            imagePos = tab['image_pos']
            tab['image_pos'] = (imagePos[0], imagePos[1], 0.005)

        if gui is not None:
            gui.removeNode()
        bookModel.removeNode()

        self.setBin('sorted-gui-popup', 2400)
        for tab in moveTabs:
            tab.setBin('sorted-gui-popup', 2399)

        self._tabHitButtons = []
        hitData = (
            (self.tabSocial, 'Social'),
            (self.tabAudio, 'Audio'),
            (self.tabDisplay, 'Display'),
            (self.tabAccessibility, 'Accessibility'),
            (self.tabGameplay, 'Gameplay'),
            (self.tabControls, 'Controls'),
            (self.tabCamera, 'Camera'),
        )
        for tab, stateName in hitData:
            x, y, z = tab.getPos(self.frame)
            hitButton = DirectButton(
                parent=self.frame,
                relief=DGG.FLAT,
                frameColor=(0, 0, 0, 0),
                frameSize=(-0.12, 0.12, 0.0, 0.18),
                pos=(x, 0, z),
                pressEffect=0,
                command=self.request,
                extraArgs=[stateName]
            )
            hitButton.setBin('sorted-gui-popup', 2401)
            hitButton.bind(DGG.ENTER, self.onMouseEnter, [tab])
            hitButton.bind(DGG.EXIT, self.onMouseExit, [tab])
            self._tabHitButtons.append(hitButton)
            self.uiItems.append(hitButton)


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
            self.updateTabPos(.005, button)
            return
        sequence = Parallel(
            LerpFunc(self.updateTabSize, fromData=currentSize, toData=.1, duration=.25, extraArgs=[button]),
            LerpFunc(self.updateTabPos, fromData=currentPos, toData=.005, duration=.25, extraArgs=[button])
        )
        self.buttonSeqs[button] = sequence
        sequence.start()

    def _finishTab(self):
        MainMenuScreenOptions.MainMenuScreenOptions._finishTab(self)
        optionList = self.getCurrentOptionList()
        for option in optionList:
            if not hasattr(option, 'optionString'):
                continue
            extras = getattr(option, 'extraElements', [])
            if extras:
                try:
                    option.guiItem.setActive(False)
                except:
                    pass
            for extra in extras:
                try:
                    extra.bind(DGG.ENTER, self.updateDescription, [option.optionString])
                    extra.bind(DGG.EXIT, self.clearDescription)
                    extra.bind(MainMenuScreenOptions.GUI_WHEEL_UP, self._wheelPage, [-1])
                    extra.bind(MainMenuScreenOptions.GUI_WHEEL_DOWN, self._wheelPage, [1])
                except:
                    pass

    def _createClashCommonUI(self):
        gui = MainMenuGui.loadOptionsGui()

        self.pageBorder = DirectFrame(
            parent=self,
            relief=None,
            image=MainMenuGui._node(gui, 'options_bg'),
            pos=(0.01, 0, -0.13),
            scale=1.7
        )
        self.uiItems.append(self.pageBorder)

        self.title = DirectFrame(
            parent=self,
            relief=None,
            image=MainMenuGui._node(gui, 'options_title'),
            pos=(0.025, 0, 0.62),
            scale=(1.1, 1, 0.275)
        )
        self.uiItems.append(self.title)

        arrowImages = self._imageSet(gui, ('arrow_static', 'arrow_press', 'arrow_hover'))
        self.upArrow = DirectButton(
            parent=self,
            relief=None,
            image=arrowImages,
            scale=0.15,
            pos=(0.73, 0, 0.05),
            command=self.previousRow
        )
        self.downArrow = DirectButton(
            parent=self,
            relief=None,
            image=arrowImages,
            scale=(-0.15, 1, 0.15),
            pos=(0.73, 0, -0.175),
            hpr=(0, 0, 180),
            command=self.nextRow
        )
        self.uiItems.extend([self.upArrow, self.downArrow])

        self.rowNumberLabel = DirectLabel(
            parent=self,
            relief=None,
            pos=(0.729, 0, -0.08),
            text_scale=0.06,
            text='1/1'
        )
        self.uiItems.append(self.rowNumberLabel)

        self.optionDescriptionBox = DirectFrame(
            parent=self,
            relief=None,
            image=MainMenuGui._node(gui, 'options_dialoguebox'),
            pos=(0.035, 0, -0.4),
            scale=(2.3, 1, 0.2875)
        )
        self.uiItems.append(self.optionDescriptionBox)
        self.optionDescriptionLabel = DirectLabel(
            parent=self.optionDescriptionBox,
            relief=None,
            text='Hover over an option for a description.',
            text_scale=0.16,
            text_wordwrap=34,
            pos=(-0.015, 0, 0.12),
            scale=(0.125, 1, 1)
        )
        self.uiItems.append(self.optionDescriptionLabel)

        tabPos = (-0.80, -0.533, -0.266, 0.000, 0.266, 0.533, 0.800)
        self.tabSocial = self._makeTab(gui, self, (tabPos[0], 0, .7), 'tab_privacy', 'Social', 'Social')
        self.tabAudio = self._makeTab(gui, self, (tabPos[1], 0, .7), 'tab_audio', 'Audio', 'Audio')
        self.tabDisplay = self._makeTab(gui, self, (tabPos[2], 0, .7), 'tab_video', 'Display', 'Display')
        self.tabAccessibility = self._makeTab(gui, self, (tabPos[3], 0, .7), 'tab_accessibility', 'Access', 'Accessibility')
        self.tabGameplay = self._makeTab(gui, self, (tabPos[4], 0, .7), 'tab_gameplay', 'Game', 'Gameplay')
        self.tabControls = self._makeTab(gui, self, (tabPos[5], 0, .7), 'tab_controls', 'Controls', 'Controls')
        self.tabCamera = self._makeTab(gui, self, (tabPos[6], 0, .7), 'tab_camera', 'Camera', 'Camera')

        resetImages = self._imageSet(gui, ('reset_static', 'reset_press', 'reset_hover'))
        resetAllImages = self._imageSet(gui, ('resetall_static', 'resetall_press', 'resetall_hover'))
        self.resetButton = DirectButton(
            parent=self,
            relief=None,
            image=resetImages,
            scale=(0.3, 1, 0.15),
            pos=(-0.65, 0, -.6),
            frameSize=(-0.45, 0.45, -0.45, 0.45),
            command=lambda: self._showResetConfirm(0)
        )
        self.resetAllButton = DirectButton(
            parent=self,
            relief=None,
            image=resetAllImages,
            scale=(0.6, 1, 0.15),
            pos=(-0.25, 0, -.6),
            frameSize=(-0.35, 0.35, -0.35, 0.35),
            command=lambda: self._showResetConfirm(1)
        )
        self.uiItems.extend([self.resetButton, self.resetAllButton])

        for option in (self.pageBorder, self.title, self.optionDescriptionBox, self.optionDescriptionLabel):
            option['state'] = DGG.NORMAL
            option.bind(MainMenuScreenOptions.GUI_WHEEL_UP, self._wheelPage, [-1])
            option.bind(MainMenuScreenOptions.GUI_WHEEL_DOWN, self._wheelPage, [1])

        if gui is not None:
            gui.removeNode()

    def _goBack(self):
        if self.bookPage and self.bookPage.book:
            self.bookPage.book.closeBook()

    def _setBookLayer(self, active):
        book = getattr(self.bookPage, 'book', None)
        if not book:
            return
        if active:
            book.setBin('sorted-gui-popup', 2400)
        else:
            book.clearBin()

    def enter(self):
        book = getattr(self.bookPage, 'book', None)
        if book:
            book.show()
            try:
                bookPos = book.getPos(aspect2d)
                self.setPos(bookPos[0], 0, bookPos[2])
            except:
                self.setPos(0, 0, 0.1)

            self._setBookLayer(True)
            self.background.hide()
            try:
                self._bookFrameSize = tuple(book['frameSize'])
                book['frameSize'] = (0, 0, 0, 0)
            except:
                self._bookFrameSize = None

            if getattr(self.bookPage, 'title', None):
                self.bookPage.title.hide()
            if getattr(self.bookPage, 'optionsTab', None):
                self.bookPage.optionsTab.hide()

            if not getattr(book, 'safeMode', 0):
                if getattr(book, 'pageTabFrame', None):
                    book.pageTabFrame.show()
                    book.pageTabFrame.setBin('sorted-gui-popup', 2402)
                if getattr(book, 'pageTabFrame2', None):
                    book.pageTabFrame2.show()
                    book.pageTabFrame2.setBin('sorted-gui-popup', 2402)

            if getattr(book, 'bookCloseButton', None) and getattr(book, 'entered', 0):
                book.bookCloseButton.show()

        self.setBin('sorted-gui-popup', 2401)
        for tab in (self.tabSocial, self.tabAudio, self.tabDisplay, self.tabAccessibility,
                    self.tabGameplay, self.tabControls, self.tabCamera):
            tab.setBin('sorted-gui-popup', 2399)
        for hitButton in getattr(self, '_tabHitButtons', []):
            hitButton.setBin('sorted-gui-popup', 2403)

        self.accept(MainMenuScreenOptions.GUI_WHEEL_UP, self._wheelPage, [-1])
        self.accept(MainMenuScreenOptions.GUI_WHEEL_DOWN, self._wheelPage, [1])
        self.show()

    def exit(self):
        book = getattr(self.bookPage, 'book', None)
        if book:
            self._setBookLayer(False)
            if getattr(self, '_bookFrameSize', None) is not None:
                try:
                    book['frameSize'] = self._bookFrameSize
                except:
                    pass
                self._bookFrameSize = None
            if getattr(self.bookPage, 'title', None):
                self.bookPage.title.show()
            if getattr(self.bookPage, 'optionsTab', None):
                self.bookPage.optionsTab.show()
            if getattr(book, 'pageTabFrame', None):
                book.pageTabFrame.clearBin()
            if getattr(book, 'pageTabFrame2', None):
                book.pageTabFrame2.clearBin()

        self.ignore(MainMenuScreenOptions.GUI_WHEEL_UP)
        self.ignore(MainMenuScreenOptions.GUI_WHEEL_DOWN)
        self.background.show()
        self.clearBin()
        for tab in (self.tabSocial, self.tabAudio, self.tabDisplay, self.tabAccessibility,
                    self.tabGameplay, self.tabControls, self.tabCamera):
            tab.clearBin()
        for hitButton in getattr(self, '_tabHitButtons', []):
            hitButton.clearBin()
        self.hide()

    def unload(self):
        self.destroy()
