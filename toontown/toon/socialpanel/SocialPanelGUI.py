from pandac.PandaModules import TextNode
from direct.gui.DirectGui import DirectFrame, DirectButton, DirectLabel
from direct.gui import DirectGuiGlobals as DGG
from direct.interval.IntervalGlobal import Sequence, LerpScaleInterval
from toontown.toonbase import ToontownGlobals
from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui


class SelectorButton(DirectFrame):
    BUTTON_ACTIVE = (0.906, 0.843, 0.125, 1.0)
    BUTTON_INACTIVE = (0.184, 0.192, 0.212, 1.0)

    def __init__(self, parent, pos, width=0.6, height=0.07, title='', callback=None, disabled=False, scale=0.6, **kwargs):
        self.width = width
        self.height = height
        self.callback = callback
        self.lightCol = kwargs.pop('lightCol', (1, 1, 1, 1))
        self.darkCol = kwargs.pop('darkCol', (0.361, 0.361, 0.361, 1.0))
        DirectFrame.__init__(self, parent=parent, relief=None, pos=pos, scale=scale,
                             text_pos=(0, -0.014), text_scale=0.05,
                             text_fg=(0, 0, 0, 1), text='Test choice',
                             geom=sp_gui.find('**/SmoothTextBox'),
                             geom_color=self.darkCol, **kwargs)
        self.initialiseoptions(SelectorButton)
        self.setWidth(width)
        self.titleText = DirectLabel(
            parent=self, relief=None, text_fg=(1, 1, 1, 1), text_shadow=(0, 0, 0, 1),
            text_pos=(0, 0.085), text_scale=0.065, text='')
        if title:
            self.setTitleText(title)
        self.button_left = DirectButton(
            self, pos=(-(width / 2.0) - 0.04, 0, 0), relief=None,
            command=self.changeOption, extraArgs=[-1],
            image=(sp_gui.find('**/Arrow_N'), sp_gui.find('**/Arrow_P'),
                   sp_gui.find('**/Arrow_H'), sp_gui.find('**/Arrow_D')),
            image_scale=(-(30.0 / 42.0), 1, 1), scale=0.08)
        self.button_right = DirectButton(
            self, pos=((width / 2.0) + 0.04, 0, 0), relief=None,
            command=self.changeOption, extraArgs=[1],
            image=(sp_gui.find('**/Arrow_N'), sp_gui.find('**/Arrow_P'),
                   sp_gui.find('**/Arrow_H'), sp_gui.find('**/Arrow_D')),
            image_scale=((30.0 / 42.0), 1, 1), scale=0.08)
        self.button_left.hide()
        self.button_right.hide()
        self.options = []
        self.option2Text = {None: ''}
        self.wraparound = False
        self.currentIndex = 0
        self.disabled = disabled
        self.setDisabled()

    def setDisabled(self):
        if self.disabled:
            self.button_left.show()
            self.button_right.show()
            self.setButtonState(False)
            self.setText('')
            self['geom_color'] = self.darkCol
        else:
            self.setButtonState(True)
            self['geom_color'] = self.lightCol

    def setWidth(self, width):
        self['geom_scale'] = ((0.18333 * width) * (327.0 / 62.0), 1, 0.11)

    def setTitleText(self, text):
        self.titleText.setText(text)

    def enterDisable(self):
        self.disabled = True
        self.setDisabled()

    def exitDisable(self):
        self.disabled = False
        self.setDisabled()

    def setButtonState(self, state):
        guiState = DGG.NORMAL if state else DGG.DISABLED
        self.button_left['state'] = guiState
        self.button_right['state'] = guiState

    def setOptions(self, values=None, texts=None, wraparound=False, setIndex=-1, canDisable=True):
        if canDisable and not (values or texts):
            self.enterDisable()
        else:
            self.exitDisable()
        if not values:
            values = [None]
        if not texts:
            texts = ['']
        self.options = list(values)
        self.option2Text = dict(list(zip(self.options, list(texts))))
        self.wraparound = wraparound
        self.currentIndex = setIndex if setIndex != -1 else len(self.options) - 1
        if self.currentIndex < 0:
            self.currentIndex = 0
        if self.currentIndex >= len(self.options):
            self.currentIndex = len(self.options) - 1
        self.updateButtons()

    def getChoice(self):
        if not self.options:
            return None
        return self.options[self.currentIndex]

    def changeOption(self, direction):
        if not self.options:
            return
        self.currentIndex += direction
        if self.currentIndex < 0:
            self.currentIndex = len(self.options) - 1
        elif self.currentIndex >= len(self.options):
            self.currentIndex = 0
        if self.callback is not None:
            self.callback(self.getChoice())
        self.updateButtons()

    def updateButtons(self):
        choice = self.getChoice()
        self.setText(str(self.option2Text.get(choice, '')))
        if len(self.options) <= 1:
            self.button_left.hide()
            self.button_right.hide()
            return
        self.button_left.show()
        self.button_right.show()
        if not self.wraparound:
            self.button_left['state'] = DGG.NORMAL if self.currentIndex != 0 else DGG.DISABLED
            self.button_right['state'] = DGG.NORMAL if self.currentIndex != len(self.options) - 1 else DGG.DISABLED
        else:
            self.setButtonState(True)


class SocialPanelContextDropdown(DirectFrame):
    """Python 2 compatible version of Clash's social-panel context menu."""

    contextScale = 0.1

    def __init__(self, parent=None, labelText='Label', survive=False):
        self.buttons = []
        self.survive = bool(survive)
        self.hoverInterval = None
        self._mousePos = self._getMousePosition()

        DirectFrame.__init__(
            self,
            parent=aspect2d,
            relief=None,
            state=DGG.NORMAL,
            image=sp_gui.find('**/POPUPBAR'),
            geom=sp_gui.find('**/POPUPBAR_TITLEAREA'),
            scale=self.contextScale,
        )
        self.initialiseoptions(SocialPanelContextDropdown)
        self.setPos(self._mousePos[0], 0, self._mousePos[1])
        self.setBin('gui-popup', 250)

        self.label = DirectLabel(
            parent=self,
            relief=None,
            text=labelText,
            text_align=TextNode.ACenter,
            text_scale=0.32,
            text_pos=(-0.03, -0.67),
            text_fg=(0, 0, 0, 1),
            text_font=ToontownGlobals.getInterfaceFont(),
        )

        self._reposition()
        self.accept('mouse1-up', self._onMouseUp)

        try:
            reduceMovement = bool(settings.get('reduce-gui-movement', False))
        except:
            reduceMovement = False
        if not reduceMovement:
            self.hoverInterval = Sequence(
                LerpScaleInterval(self, 0.1, self.contextScale * 1.1,
                                  blendType='easeInOut', startScale=0.01),
                LerpScaleInterval(self, 0.1, self.contextScale,
                                  blendType='easeInOut'),
            )
            self.hoverInterval.start()

    def _getMousePosition(self):
        if not base.mouseWatcherNode.hasMouse():
            return (0, 0)
        ratio = base.getAspectRatio()
        x = base.mouseWatcherNode.getMouseX() * max(ratio, 1.0)
        z = base.mouseWatcherNode.getMouseY() / min(max(0.001, ratio), 1.0)
        return (x, z)

    def _onMouseUp(self):
        if self.survive:
            self.survive = False
            return
        self.destroy()

    def getButtonCount(self):
        return len(self.buttons)

    def addButton(self, text, callback, red=False, extraArgs=None):
        if extraArgs is None:
            extraArgs = []
        geomName = 'RedButton' if red else 'OrangeButton'
        button = DirectButton(
            parent=self,
            relief=None,
            frameSize=(-1.4, 1.4, -0.45, 0.45),
            command=callback,
            extraArgs=extraArgs,
            geom=(sp_gui.find('**/%s_N' % geomName),
                  sp_gui.find('**/%s_P' % geomName),
                  sp_gui.find('**/%s_H' % geomName)),
            geom_scale=(2.72, 1, 0.9),
            text=text,
            text_align=TextNode.ACenter,
            text_scale=0.37,
            text_pos=(-0.05, -0.1),
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_font=ToontownGlobals.getInterfaceFont(),
        )
        buttonIndex = len(self.buttons)
        button.setPos(0, 0, -1.4 + (buttonIndex * -0.9))
        self.buttons.append(button)
        self._reposition()
        return button

    def _reposition(self):
        self['geom_scale'] = (165.0 / 39.0 * 0.63, 1, 0.76)
        self['geom_pos'] = (0, 0, -0.5)

        buttonCount = len(self.buttons)
        zpos = 1.88 + (0.9 * max(0, buttonCount - 1))
        self['image_scale'] = ((170.0 / 304.0) * 5.0, 1, zpos)
        self['image_pos'] = (0, 0, -zpos / 2.0)
        self['frameSize'] = (-1.45, 1.45, -zpos, 0)

        ratio = base.getAspectRatio()
        x = self._mousePos[0]
        z = self._mousePos[1]
        horizontalMargin = 1.45 * self.contextScale + 0.02
        lowerMargin = zpos * self.contextScale + 0.02
        x = max(-ratio + horizontalMargin, min(x, ratio - horizontalMargin))
        z = max(-1.0 + lowerMargin, min(z, 0.98))
        self.setPos(x, 0, z)

    def destroy(self):
        self.ignoreAll()
        if self.hoverInterval is not None:
            try:
                self.hoverInterval.finish()
            except:
                pass
            self.hoverInterval = None
        for button in self.buttons:
            try:
                button.destroy()
            except:
                pass
        self.buttons = []
        if getattr(self, 'label', None) is not None:
            try:
                self.label.destroy()
            except:
                pass
            self.label = None
        DirectFrame.destroy(self)
