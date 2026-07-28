from direct.gui.DirectGui import DirectFrame, DirectButton
from toontown.toon.socialpanel.SocialPanelGlobals import *


class SocialPanelTabs(DirectFrame):
    tab_ratio = 123.0 / 84.0
    tab_scale = 0.09

    def __init__(self, parent):
        DirectFrame.__init__(self, parent=parent, relief=None)
        self.initialiseoptions(SocialPanelTabs)
        self.panel = parent
        self.button_friendsTab = None
        self.button_groupsTab = None
        self.button_mailTab = None
        self.button_clubsTab = None
        self.button_closePanel = None
        self.load()

    def load(self):
        imageScale = (self.tab_ratio, 1, 1)
        textOptions = {
            'text_fg': (1, 1, 1, 1),
            'text_bg': (0, 0, 0, 0),
            'text_shadow': (0, 0, 0, 1),
            'text_pos': (-0.024, -1.1),
            'text_scale': 0.6,
        }

        self.button_friendsTab = DirectButton(
            parent=self,
            relief=None,
            image_scale=imageScale,
            image=(sp_gui.find('**/HeartButton_N'),
                   sp_gui.find('**/HeartButton_P'),
                   sp_gui.find('**/HeartButton_H')),
            command=self.panel.showFriendsTab,
            text=('', 'Friends', 'Friends', ''),
            **textOptions
        )

        self.button_groupsTab = DirectButton(
            parent=self,
            relief=None,
            image_scale=imageScale,
            image=(sp_gui.find('**/ToonButton_N'),
                   sp_gui.find('**/ToonButton_P'),
                   sp_gui.find('**/ToonButton_H')),
            command=self.panel.unavailableTab,
            extraArgs=[TAB_GROUPS],
            text=('', 'Groups', 'Groups', ''),
            **textOptions
        )

        self.button_clubsTab = DirectButton(
            parent=self,
            relief=None,
            image_scale=imageScale,
            image=(sp_gui.find('**/ClubButton_N'),
                   sp_gui.find('**/ClubButton_P'),
                   sp_gui.find('**/ClubButton_H')),
            command=self.panel.unavailableTab,
            extraArgs=[TAB_CLUBS],
            text=('', 'Clubs', 'Clubs', ''),
            **textOptions
        )

        self.button_closePanel = DirectButton(
            parent=self,
            relief=None,
            image_scale=imageScale,
            image=(sp_gui.find('**/Close_N'),
                   sp_gui.find('**/Close_P'),
                   sp_gui.find('**/Close_H')),
            command=self.panel.exit,
            text=('', 'Close', 'Close', ''),
            **textOptions
        )

        self.setButtonDistances(-0.433, -0.084, -0.889, 0.08)

    def setButtonDistances(self, start, end, zpos, scale):
        buttons = [self.button_friendsTab,
                   self.button_groupsTab,
                   self.button_clubsTab,
                   self.button_closePanel]
        count = len(buttons)
        for index in xrange(count):
            if count > 1:
                amount = float(index) / float(count - 1)
            else:
                amount = 0.0
            xpos = start + ((end - start) * amount)
            buttons[index].setPos(xpos, 0, zpos)
            buttons[index].setScale(scale)

    def destroy(self):
        self.panel = None
        DirectFrame.destroy(self)
