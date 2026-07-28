from pandac.PandaModules import TextNode, Vec3
from direct.gui.DirectGui import DirectButton, DirectFrame
from direct.gui import DirectGuiGlobals as DGG
from toontown.toon.socialpanel.SocialPanelGlobals import friendYOffset, sp_gui, sp_gui_icons

COLOR_DEFAULT = (0.80, 0.88, 0.74, 1.0)
COLOR_FAVORITE = (50.0 / 255.0, 184.0 / 255.0, 213.0 / 255.0, 1.0)
COLOR_SELECTED = (0.84, 0.88, 0.37, 1.0)
COLOR_OFFLINE = (0.42, 0.42, 0.42, 1.0)


class SocialPanelFriend(DirectButton):
    shiftPos = Vec3(0.5, 0, 0)
    configurePos = Vec3(-0.25, 0, -0.2275)

    def __init__(self, scrollFrame, handle, index, friendsTab,
                 configureMode=False, online=True):
        self.handle = handle
        self.index = index
        self.friendsTab = friendsTab
        self.configureMode = configureMode
        self.selected = False
        self.online = online

        leftPos = scrollFrame['canvasSize'][0]
        textFont = None
        try:
            avatar = base.cr.doId2do.get(self.avId)
            if avatar is not None and hasattr(avatar, 'getFont'):
                textFont = avatar.getFont()
            elif hasattr(handle, 'getFont'):
                textFont = handle.getFont()
        except:
            textFont = None

        options = {
            'parent': scrollFrame.getCanvas(),
            'relief': None,
            'command': self.onClick,
            'frameSize': (0, 5.0, -friendYOffset, 0),
            'frameColor': (1, 1, 1, 0),
            'text': self.handle.getName(),
            'text_scale': 0.29,
            'text_align': TextNode.ALeft,
            'text_pos': (0.1, -0.07 - (friendYOffset / 2.0)),
            'text_fg': self.getTextColor(),
            'text_shadow': self.getTextShadow(),
            'geom': (sp_gui.find('**/Box_N'),
                     sp_gui.find('**/Box_P'),
                     sp_gui.find('**/Box_H')),
            'geom_color': COLOR_DEFAULT,
            'geom_scale': (0.5 * (455.0 / 42.0), 1, 0.52),
            'geom_pos': (2.71, 0, -0.24),
        }
        if textFont is not None:
            options['text_font'] = textFont

        DirectButton.__init__(self, **options)
        self.initialiseoptions(SocialPanelFriend)

        self.startPos = Vec3(leftPos, 1, 0 - (index * friendYOffset))
        self.endPos = self.startPos + self.shiftPos
        self.setPos(self.startPos)

        self.checkboxBehind = DirectFrame(
            parent=self,
            relief=None,
            geom=sp_gui.find('**/Box2_N'),
            geom_color=COLOR_DEFAULT,
            pos=(-0.25, 0, -0.24),
            scale=0.52,
        )

        self.checkbox = DirectButton(
            parent=self,
            relief=None,
            image=sp_gui_icons.find('**/CIRCLE1'),
            image_scale=0.5,
            pos=self.configurePos,
            scale=0.45,
            command=self.toggleSelected,
        )

        self.bind(DGG.B3PRESS, self.onRightClick)
        self.setConfigure(configureMode, instant=True)

    def destroy(self):
        self.ignoreAll()
        self.friendsTab = None
        DirectButton.destroy(self)

    def onClick(self):
        if self.configureMode:
            self.toggleSelected()
        else:
            self.friendsTab.friendButtonClicked(self)

    def onRightClick(self, event):
        self.friendsTab.friendRightClicked(self)

    def toggleSelected(self, force=None):
        if force is None:
            self.selected = not self.selected
        else:
            self.selected = bool(force)
        self.updateVisuals()
        self.friendsTab.friendSelectionChanged(self)

    def clearSelection(self, sendEvent=True):
        self.selected = False
        self.updateVisuals()
        if sendEvent:
            self.friendsTab.friendSelectionChanged(self)

    def setConfigure(self, mode, instant=False):
        self.configureMode = bool(mode)
        if self.configureMode:
            self.setPos(self.endPos)
            self.checkbox.show()
            self.checkboxBehind.show()
        else:
            self.setPos(self.startPos)
            self.checkbox.hide()
            self.checkboxBehind.hide()
            self.selected = False
        self.updateVisuals()

    def updateVisuals(self):
        if self.selected and self.configureMode:
            color = COLOR_SELECTED
            image = sp_gui_icons.find('**/CIRCLE3')
        elif self.favorite:
            color = COLOR_FAVORITE
            image = sp_gui_icons.find('**/CIRCLE1')
        else:
            color = COLOR_DEFAULT
            image = sp_gui_icons.find('**/CIRCLE1')
        self['geom_color'] = color
        self['text_fg'] = self.getTextColor()
        textShadow = self.getTextShadow()
        if textShadow is None:
            textShadow = (0, 0, 0, 0)
        self['text_shadow'] = textShadow
        self.checkboxBehind['geom_color'] = color
        self.checkbox['image'] = image

    def getTextColor(self):
        if self.favorite:
            return (1, 1, 1, 1)
        if self.online:
            return (0, 0, 0, 1)
        return COLOR_OFFLINE

    def getTextShadow(self):
        if self.favorite:
            return (0, 0, 0, 1)
        return None

    @property
    def favorite(self):
        if self.friendsTab is None:
            return False
        return self.friendsTab.isFavorite(self.avId)

    @property
    def avId(self):
        if hasattr(self.handle, 'getDoId'):
            return self.handle.getDoId()
        return self.handle.doId
