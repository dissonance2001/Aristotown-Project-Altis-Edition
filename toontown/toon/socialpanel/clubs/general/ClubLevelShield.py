from __future__ import absolute_import
from direct.gui.DirectGui import DirectFrame, DirectLabel
from pandac.PandaModules import TransparencyAttrib

from toontown.toon.socialpanel.SocialPanelGlobals import sp_gui
from toontown.toonbase import ToontownGlobals


class ClubLevelShield(DirectFrame):
    """Python 2 port of Corporate Clash's Club Level shield."""

    def __init__(self, parent, **kw):
        DirectFrame.__init__(
            self,
            parent=parent,
            relief=None,
            image=sp_gui.find('**/Badge_Icon_Orange'),
            image_scale=((62.0 / 67.0) * 0.3, 1, 0.3),
            **kw
        )
        self.initialiseoptions(ClubLevelShield)
        self.setTransparency(TransparencyAttrib.MAlpha)

        self.text_level = DirectLabel(
            parent=self,
            relief=None,
            text='1',
            text_font=ToontownGlobals.getToonFont(),
            text_pos=(-0.005, -0.034),
            text_scale=0.13,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
        )

    def setClubLevel(self, level):
        self.text_level['text'] = str(level)

    def destroy(self):
        DirectFrame.destroy(self)
