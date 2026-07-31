import random

from direct.gui.DirectGui import DirectButton, DirectEntry, DirectFrame, DirectLabel
from direct.gui import DirectGuiGlobals as DGG
from pandac.PandaModules import NodePath, TextNode, TransparencyAttrib

from toontown.club.ClubClasses import ClubIcon
from toontown.club.ClubIconGUI import ClubIconGUI
from toontown.club import ClubGlobals
from toontown.toonbase import ToontownGlobals


def _normalizedNodeName(name):
    return ''.join([character.lower() for character in str(name) if character.isalnum()])


def _findGuiPart(model, names):
    """Find a GUI part even when an older BAM uses a minor name variation."""
    for name in names:
        node = model.find('**/' + name)
        if not node.isEmpty():
            return node

    wanted = [_normalizedNodeName(name) for name in names]
    matches = model.findAllMatches('**/*')
    for index in range(matches.getNumPaths()):
        node = matches.getPath(index)
        nodeName = _normalizedNodeName(node.getName())
        for candidate in wanted:
            if nodeName == candidate or candidate in nodeName:
                return node
    return NodePath()


def _attachGuiPart(parent, model, names, pos, scale, sort):
    """Copy the actual BAM subgraph instead of passing it through OnscreenImage.

    Project Altis's older DirectGUI can fail to display compound BAM nodes when
    they are supplied through the ``image`` option.  Copying the real NodePath
    preserves its texture and child geometry.
    """
    source = _findGuiPart(model, names)
    if source.isEmpty():
        return None

    artwork = source.copyTo(parent)
    try:
        artwork.clearTransform()
    except:
        artwork.setPos(0, 0, 0)
        artwork.setHpr(0, 0, 0)
        artwork.setScale(1)
    artwork.setPos(pos)
    artwork.setScale(scale)
    artwork.setTransparency(TransparencyAttrib.MAlpha)
    artwork.setDepthTest(False)
    artwork.setDepthWrite(False)
    artwork.setBin('gui-popup', sort)
    return artwork


class _SelectionIndicator(DirectFrame):
    def __init__(self, parent, shopGui, scale=(0.16, 1, 0.28), pos=(0, 0, 0.003)):
        # Copy the real Clash scribble geometry directly from club_shop.bam.
        # Passing this compound node through DirectGUI's image/geom option does
        # not render reliably in Altis's older Panda3D build.
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            frameSize=(0, 0, 0, 0),
        )
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.setDepthTest(False)
        self.setDepthWrite(False)
        self.setBin('gui-popup', 506)

        node = shopGui.find('**/CategorySelectIndicator')
        self.artwork = None
        if not node.isEmpty():
            self.artwork = node.copyTo(self)
            try:
                self.artwork.clearTransform()
            except:
                self.artwork.setPos(0, 0, 0)
                self.artwork.setHpr(0, 0, 0)
                self.artwork.setScale(1)
            self.artwork.setPos(pos)
            self.artwork.setScale(scale)
            self.artwork.setColorScale(1, 1, 1, 0.85)
            self.artwork.setTransparency(TransparencyAttrib.MAlpha)
            self.artwork.setDepthTest(False)
            self.artwork.setDepthWrite(False)
            self.artwork.setBin('gui-popup', 506)
        else:
            self.fallback = DirectFrame(
                parent=self,
                relief=DGG.RIDGE,
                frameSize=(-0.07, 0.07, -0.07, 0.07),
                frameColor=(1, 1, 1, 0.55),
                borderWidth=(0.008, 0.008),
            )
            self.fallback.setBin('gui-popup', 506)
        self.hide()


class _WoodenTitle(DirectFrame):
    def __init__(self, parent, gui, text, pos=(0, 0, 0), scale=1.0):
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            pos=pos,
            scale=scale,
        )
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.setDepthTest(False)
        self.setDepthWrite(False)
        self.setBin('gui-popup', 503)

        self.artwork = _attachGuiPart(
            self,
            gui,
            ('Title_Board', 'TitleBoard', 'title_board', 'titleBoard'),
            (0, 0, 0),
            (0.8, 1, 0.125),
            503,
        )
        if self.artwork is None:
            # Exact-size fallback only when the installed BAM truly lacks the node.
            self.fallback = DirectFrame(
                parent=self,
                relief=DGG.RIDGE,
                frameSize=(-0.16, 0.16, -0.038, 0.038),
                frameColor=(0.48, 0.27, 0.16, 1.0),
                borderWidth=(0.006, 0.006),
            )
            self.fallback.setBin('gui-popup', 503)

        self.label = DirectLabel(
            parent=self,
            relief=None,
            text=text,
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.052,
            text_pos=(-0.006, -0.012),
            text_fg=(1.0, 0.902, 0.741, 1.0),
            text_shadow=(0.267, 0.18, 0.137, 1.0),
        )
        self.label.setBin('gui-popup', 504)


class _ThemeSelection(DirectFrame):
    def __init__(self, parent, owner):
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            frameSize=(-0.5, 0.5, -0.125, 0.125),
            pos=(-0.3, 0, -0.145),
        )
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.setDepthTest(False)
        self.setDepthWrite(False)
        self.setBin('gui-popup', 502)

        self.rowArtwork = _attachGuiPart(
            self,
            owner.gui,
            ('Board_Row', 'BoardRow', 'board_row', 'boardRow'),
            (0.102, 0, -0.08),
            (0.5, 1, 0.125),
            502,
        )
        if self.rowArtwork is None:
            self.rowFallback = DirectFrame(
                parent=self,
                relief=DGG.FLAT,
                frameSize=(-0.105, 0.285, -0.111, -0.014),
                frameColor=(0.025, 0.16, 0.13, 0.72),
            )
            self.rowFallback.setBin('gui-popup', 502)

        self.owner = owner
        self.buttons = []
        self.title = _WoodenTitle(self, owner.gui, 'CLUB THEME', pos=(0, 0, -0.011), scale=0.5)
        self.indicator = _SelectionIndicator(self, owner.shopGui, scale=(0.30, 1, 0.50), pos=(0, 0, 0.01))

        for index, color in enumerate(ClubIconGUI.COLORS):
            button = DirectButton(
                parent=self,
                relief=DGG.RAISED,
                frameSize=(-0.1, 0.1, -0.1, 0.1),
                frameColor=color,
                borderWidth=(0.03, 0.03),
                command=self._select,
                extraArgs=[index],
                pressEffect=0,
            )
            x = (index // 2) * 0.0466 - 0.060
            z = (index % 2) * -0.048 - 0.055
            button.setPos(x, 0, z)
            button.setScale(0.2)
            self.buttons.append(button)

    def _select(self, index):
        self.owner.themeId = int(index)
        self.indicator.reparentTo(self.buttons[index])
        self.indicator.setPos(0, 0, 0)
        self.indicator.show()
        self.owner._refreshIcon()


class _ChoiceBar(DirectFrame):
    MODE_ICON = 'icon'
    MODE_BACKGROUND = 'background'
    MODE_COLOR = 'color'

    def __init__(self, parent, owner, label, mode, pos):
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            frameSize=(-0.5, 0.5, -0.125, 0.125),
            scale=0.48,
            pos=pos,
        )
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.setDepthTest(False)
        self.setDepthWrite(False)
        self.setBin('gui-popup', 502)

        self.rowArtwork = _attachGuiPart(
            self,
            owner.gui,
            ('Board_Row', 'BoardRow', 'board_row', 'boardRow'),
            (0, 0, 0),
            (1, 1, 0.20),
            502,
        )
        if self.rowArtwork is None:
            self.rowFallback = DirectFrame(
                parent=self,
                relief=DGG.FLAT,
                frameSize=(-0.385, 0.385, -0.083, 0.083),
                frameColor=(0.025, 0.16, 0.13, 0.72),
            )
            self.rowFallback.setBin('gui-popup', 502)

        self.owner = owner
        self.mode = mode
        self.index = 0
        self.buttons = []
        self.visibleCount = 4 if mode == self.MODE_COLOR else 5
        self.values = list(range(16)) if mode == self.MODE_COLOR else list(range(1, 9))

        self.title = _WoodenTitle(self, owner.gui, label, pos=(-0.26, 0, 0.10))
        self.left = self._makeArrow(-0.45, -1, False)
        self.right = self._makeArrow(0.45, 1, True)
        self.indicator = _SelectionIndicator(self, owner.shopGui)

        self._buildButtons()
        self._reposition()
        self._updateArrows()

    def _makeArrow(self, x, direction, flip):
        button = DirectButton(
            parent=self,
            relief=None,
            geom=(
                self.owner.gui.find('**/Arrow_Neutral'),
                self.owner.gui.find('**/Arrow_Press'),
                self.owner.gui.find('**/Arrow_Hover'),
                self.owner.gui.find('**/Arrow_Neutral'),
            ),
            geom_scale=(-1, 1, 1) if flip else (1, 1, 1),
            frameSize=(-0.45, 0.45, -0.45, 0.50),
            scale=0.13,
            pos=(x, 0, 0),
            command=self._scroll,
            extraArgs=[direction],
            pressEffect=0,
        )
        button.setTransparency(TransparencyAttrib.MAlpha)
        return button

    def _buildButtons(self):
        for listIndex, value in enumerate(self.values):
            if self.mode == self.MODE_ICON:
                node = ClubIconGUI.icons.find('**/icon_%s' % value)
                button = DirectButton(
                    parent=self,
                    relief=None,
                    image=node,
                    image_scale=0.15,
                    frameSize=(-0.07, 0.057, -0.07, 0.07),
                    command=self._select,
                    extraArgs=[listIndex, value],
                    pressEffect=0,
                )
            elif self.mode == self.MODE_BACKGROUND:
                node = ClubIconGUI.backgrounds.find('**/bg_%s' % value)
                button = DirectButton(
                    parent=self,
                    relief=None,
                    geom=node,
                    geom_scale=0.14,
                    geom_color=(0.20, 0.20, 0.20, 1),
                    frameSize=(-0.07, 0.057, -0.07, 0.07),
                    command=self._select,
                    extraArgs=[listIndex, value],
                    pressEffect=0,
                )
            else:
                color = ClubIconGUI.COLORS[value]
                button = DirectButton(
                    parent=self,
                    relief=None,
                    image=self.owner.gui.find('**/PaintCan_Base'),
                    image_scale=0.16,
                    geom=self.owner.gui.find('**/PaintCan_Color'),
                    geom_scale=0.16,
                    geom_color=color,
                    frameSize=(-0.07, 0.057, -0.07, 0.07),
                    command=self._select,
                    extraArgs=[listIndex, value],
                    pressEffect=0,
                )
            button.setTransparency(TransparencyAttrib.MAlpha)
            self.buttons.append(button)

    def _select(self, listIndex, value):
        if self.mode == self.MODE_ICON:
            self.owner.iconId = int(value)
        elif self.mode == self.MODE_BACKGROUND:
            self.owner.backgroundId = int(value)
        else:
            self.owner.backgroundColorId = int(value)

        self.indicator.reparentTo(self.buttons[listIndex])
        self.indicator.setPos(0, 0, 0)
        self.indicator.show()
        self.owner._refreshIcon()

    def _scroll(self, amount):
        maximum = max(0, len(self.buttons) - self.visibleCount)
        self.index = max(0, min(maximum, self.index + int(amount)))
        self._reposition()
        self._updateArrows()

    def _reposition(self):
        for button in self.buttons:
            button.hide()

        shown = self.buttons[self.index:self.index + self.visibleCount]
        if self.mode == self.MODE_COLOR:
            startX, endX = -0.258, 0.265
        else:
            startX, endX = -0.300, 0.305
        distance = (endX - startX) / float(max(1, self.visibleCount - 1))
        for offset, button in enumerate(shown):
            button.setPos(startX + offset * distance, 0, 0)
            button.show()

    def _updateArrows(self):
        maximum = max(0, len(self.buttons) - self.visibleCount)
        self.left['state'] = DGG.NORMAL if self.index > 0 else DGG.DISABLED
        self.right['state'] = DGG.NORMAL if self.index < maximum else DGG.DISABLED
        self.left['geom_color'] = (1, 1, 1, 1) if self.index > 0 else (0.64, 0.64, 0.64, 1)
        self.right['geom_color'] = (1, 1, 1, 1) if self.index < maximum else (0.64, 0.64, 0.64, 1)


class ClubCreationGUI(DirectFrame):
    doneEvent = 'club-creation-gui-done'
    SCREEN_SCALE = 2.25
    PLACEHOLDER = 'Enter club\nname here.'

    def __init__(self, npc=None):
        self.gui = loader.loadModel('phase_3.5/models/gui/clubs/club_creation')
        self.shopGui = loader.loadModel('phase_3.5/models/gui/clubs/club_shop')
        boardRowNode = _findGuiPart(self.gui, ('Board_Row', 'BoardRow', 'board_row', 'boardRow'))
        titleBoardNode = _findGuiPart(self.gui, ('Title_Board', 'TitleBoard', 'title_board', 'titleBoard'))
        import sys
        background = self.gui.find('**/ClubCreation_Base')

        DirectFrame.__init__(
            self,
            parent=aspect2d,
            relief=None,
            image=background,
            scale=self.SCREEN_SCALE,
        )
        self.initialiseoptions(ClubCreationGUI)
        self.setBin('gui-popup', 500)
        self.setTransparency(TransparencyAttrib.MAlpha)
        self.gui.setTransparency(TransparencyAttrib.MAlpha)
        self.shopGui.setTransparency(TransparencyAttrib.MAlpha)

        self.npc = npc
        self.iconId = 0
        self.backgroundId = 0
        self.themeId = -1
        self.backgroundColorId = -1
        self._destroyed = False
        self._usingPlaceholder = True

        self.title = DirectLabel(
            parent=self,
            relief=None,
            text='Club-O-Matic',
            text_font=ToontownGlobals.getMinnieFont(),
            text_scale=0.040,
            text_pos=(0, 0),
            text_fg=(1.0, 0.878, 0.639, 1.0),
            text_shadow=(0.239, 0.118, 0.071, 1.0),
            pos=(0.0035, 0, 0.306),
        )

        self.exitButton = DirectButton(
            parent=self,
            relief=None,
            image=(
                self.gui.find('**/Cancel_Neutral'),
                self.gui.find('**/Cancel_Press'),
                self.gui.find('**/Cancel_Hover'),
                self.gui.find('**/Cancel_Neutral'),
            ),
            frameSize=(-0.4, 0.4, -0.4, 0.4),
            scale=0.12,
            pos=(0.443, 0, 0.28),
            command=self.destroy,
            pressEffect=0,
        )
        self.exitButton.setTransparency(TransparencyAttrib.MAlpha)

        self.nameEntry = DirectEntry(
            parent=self,
            relief=None,
            text_fg=(0.12, 0.08, 0.04, 1),
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.030,
            width=5.8,
            numLines=2,
            pos=(-0.303, 0, 0.187),
            initialText=self.PLACEHOLDER,
            focus=0,
            cursorKeys=1,
            overflow=1,
            focusInCommand=self._focusName,
            focusOutCommand=self._blurName,
            command=self._nameAccepted,
        )
        try:
            self.nameEntry.guiItem.setMaxChars(ClubGlobals.CLUB_NAME_MAX)
        except:
            try:
                self.nameEntry['maxChars'] = ClubGlobals.CLUB_NAME_MAX
            except:
                pass

        self.randomNameButton = None
        try:
            clothingGui = loader.loadModel('phase_3.5/models/gui/clothingpage/clothing_page')
            refreshN = clothingGui.find('**/Refresh_N')
            refreshP = clothingGui.find('**/Refresh_P')
            refreshH = clothingGui.find('**/Refresh_H')
            if not refreshN.isEmpty():
                self.randomNameButton = DirectButton(
                    parent=self,
                    relief=None,
                    image=(refreshN, refreshP, refreshH, refreshN),
                    image_scale=(1.7 * (45.0 / 1018.0), 1.0, 1.4 * (46.0 / 917.0)),
                    pos=(-0.11, 0, 0.13),
                    scale=0.5,
                    command=self._randomizeName,
                    pressEffect=0,
                )
                self.randomNameButton.setTransparency(TransparencyAttrib.MAlpha)
        except:
            pass

        self.preview = ClubIconGUI(parent=self, scale=0.18, pos=(-0.23, 0, 0.0))
        self.preview.setTransparency(TransparencyAttrib.MAlpha)
        self.customizeLabel = DirectLabel(
            parent=self,
            relief=None,
            image=self.gui.find('**/Customize'),
            image_scale=1.2,
            scale=0.18,
            pos=(-0.23, 0, 0.0),
        )
        self.customizeLabel.setTransparency(TransparencyAttrib.MAlpha)

        self.themeSelector = _ThemeSelection(self, self)
        self.iconBar = _ChoiceBar(self, self, 'IMAGE', _ChoiceBar.MODE_ICON, (0.16, 0, 0.178))
        self.backgroundBar = _ChoiceBar(self, self, 'DETAIL', _ChoiceBar.MODE_BACKGROUND, (0.16, 0, 0.050))
        self.colorBar = _ChoiceBar(self, self, 'COLOR', _ChoiceBar.MODE_COLOR, (0.16, 0, -0.078))

        # The complete price text is already painted into this asset.
        self.costSign = DirectLabel(
            parent=self,
            relief=None,
            image=self.gui.find('**/Jellybean_Sign'),
            image_scale=(0.5, 1, 0.25),
            pos=(0.08, 0, -0.22),
            scale=0.5,
        )
        self.costSign.setTransparency(TransparencyAttrib.MAlpha)

        self.jarModel = loader.loadModel('phase_3.5/models/gui/jar_gui')
        jarNode = self.jarModel.find('**/Jar')
        self.jellybeanBank = DirectLabel(
            parent=self,
            relief=None,
            image=jarNode if not jarNode.isEmpty() else None,
            pos=(0.224, 0, -0.21),
            scale=0.3,
            text='0',
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.18,
            text_pos=(0, -0.10),
            text_fg=(0.95, 0.95, 0, 1),
            text_shadow=(0, 0, 0, 1),
        )
        self.jellybeanBank.setTransparency(TransparencyAttrib.MAlpha)

        self.status = DirectLabel(
            parent=self,
            relief=None,
            text='',
            text_font=ToontownGlobals.getToonFont(),
            text_scale=0.017,
            text_wordwrap=24,
            pos=(0.08, 0, -0.282),
            text_fg=(1, 0.35, 0.25, 1),
            text_shadow=(0, 0, 0, 1),
        )

        self.createButton = DirectButton(
            parent=self,
            relief=None,
            image=(
                self.gui.find('**/Confirm_Neutral'),
                self.gui.find('**/Confirm_Press'),
                self.gui.find('**/Confirm_Hover'),
                self.gui.find('**/Confirm_Press'),
            ),
            frameSize=(-0.4, 0.4, -0.4, 0.4),
            scale=0.11,
            pos=(0.35, 0, -0.22),
            command=self.createClub,
            pressEffect=0,
        )
        self.createButton.setTransparency(TransparencyAttrib.MAlpha)

        self.accept('club-state-updated', self._stateUpdated)
        self.accept('club-notification', self._notification)
        self.acceptOnce('escape', self.destroy)
        mapHotkey = getattr(base, 'MAP_PAGE_HOTKEY', None)
        if mapHotkey and mapHotkey != 'escape':
            self.acceptOnce(mapHotkey, self.destroy)

        try:
            self.accept(base.localAvatar.uniqueName('moneyChange'), self._moneyChanged)
        except:
            pass

        self._updateMoney()
        self._refreshIcon()
        self._updateConfirmValidity()

        try:
            base.localAvatar.disableControls()
        except:
            pass

    def _focusName(self, *args):
        if self._usingPlaceholder:
            self.nameEntry.set('')
            self._usingPlaceholder = False
        self._updateConfirmValidity()

    def _blurName(self, *args):
        if not self.nameEntry.get().strip():
            self.nameEntry.set(self.PLACEHOLDER)
            self._usingPlaceholder = True
        self._updateConfirmValidity()

    def _nameAccepted(self, *args):
        self._updateConfirmValidity()

    def _randomizeName(self):
        first = ('Happy', 'Silly', 'Toony', 'Jolly', 'Wacky', 'Dizzy', 'Lucky', 'Bouncy')
        second = ('Toons', 'Pals', 'Friends', 'Stars', 'Heroes', 'Crew', 'Club', 'Squad')
        self.nameEntry.set('%s %s' % (random.choice(first), random.choice(second)))
        self._usingPlaceholder = False
        self._updateConfirmValidity()

    def _moneyChanged(self, *args):
        self._updateMoney()
        self._updateConfirmValidity()

    def _updateMoney(self):
        total = 0
        try:
            total = int(base.localAvatar.getTotalMoney())
        except:
            try:
                total = int(base.localAvatar.getMoney())
            except:
                pass
        self.jellybeanBank['text'] = str(total)
        if total < ClubGlobals.CLUB_CREATION_COST:
            self.jellybeanBank['text_fg'] = (1, 0, 0, 1)
            self.jellybeanBank['text_shadow'] = (0, 0, 0, 0)
        else:
            self.jellybeanBank['text_fg'] = (0.95, 0.95, 0, 1)
            self.jellybeanBank['text_shadow'] = (0, 0, 0, 1)

    def _refreshIcon(self):
        icon = ClubIcon(
            self.iconId,
            self.backgroundId,
            max(0, self.themeId),
            max(0, self.backgroundColorId),
        )
        self.preview.setIcon(icon)
        if self.iconId and self.backgroundId and self.themeId >= 0 and self.backgroundColorId >= 0:
            self.customizeLabel.hide()
        else:
            self.customizeLabel.show()
        self._updateConfirmValidity()

    def _getEnteredName(self):
        if self._usingPlaceholder:
            return ''
        return self.nameEntry.get().replace('\n', ' ').strip()

    def _updateConfirmValidity(self):
        if not hasattr(self, 'createButton'):
            return
        name = self._getEnteredName()
        enoughMoney = False
        try:
            enoughMoney = base.localAvatar.getTotalMoney() >= ClubGlobals.CLUB_CREATION_COST
        except:
            pass
        selected = bool(self.iconId and self.backgroundId and self.themeId >= 0 and self.backgroundColorId >= 0)
        validName = ClubGlobals.CLUB_NAME_MIN <= len(name) <= ClubGlobals.CLUB_NAME_MAX
        enabled = enoughMoney and selected and validName
        self.createButton['state'] = DGG.NORMAL if enabled else DGG.DISABLED
        self.createButton['image_color'] = (1, 1, 1, 1) if enabled else (0.7, 0.7, 0.7, 1)

    def createClub(self):
        name = self._getEnteredName()
        if len(name) < ClubGlobals.CLUB_NAME_MIN:
            self.status['text'] = 'The Club name must be at least %s characters.' % ClubGlobals.CLUB_NAME_MIN
            return
        if len(name) > ClubGlobals.CLUB_NAME_MAX:
            self.status['text'] = 'The Club name cannot exceed %s characters.' % ClubGlobals.CLUB_NAME_MAX
            return
        if not (self.iconId and self.backgroundId and self.themeId >= 0 and self.backgroundColorId >= 0):
            self.status['text'] = 'Choose an image, detail, color, and Club theme.'
            return
        try:
            if base.localAvatar.getTotalMoney() < ClubGlobals.CLUB_CREATION_COST:
                self.status['text'] = 'You need 20,000 jellybeans to create a Club.'
                return
        except:
            pass

        self.status['text'] = 'Creating Club...'
        self.createButton['state'] = DGG.DISABLED
        self.createButton['image_color'] = (0.6, 0.6, 0.6, 1)
        icon = ClubIcon(self.iconId, self.backgroundId, self.themeId, self.backgroundColorId)
        base.cr.clubMgr.requestCreateClub(name, icon)

    def _stateUpdated(self, club):
        if club:
            self.destroy(clubMade=True)

    def _notification(self, notifyType, message):
        self.status['text'] = message
        if notifyType == ClubGlobals.NOTIFY_ERROR:
            self._updateConfirmValidity()

    def destroy(self, clubMade=False):
        if self._destroyed:
            return
        self._destroyed = True
        self.ignoreAll()
        try:
            base.localAvatar.enableControls()
        except:
            pass
        try:
            self.gui.removeNode()
        except:
            pass
        try:
            self.shopGui.removeNode()
        except:
            pass
        try:
            self.jarModel.removeNode()
        except:
            pass
        DirectFrame.destroy(self)
        messenger.send(self.doneEvent, [clubMade])
