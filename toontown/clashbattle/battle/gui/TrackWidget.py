if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()

from typing import Optional

from toontown.clashbattle.battle import BattleGlobals
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.GUINode import GUINode
from toontown.gui import UiHelpers
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.gui.EasyManagedButton import EasyManagedButton
from toontown.gui.EasyScrolledFrame import EasyScrolledFrame
from toontown.toon.socialpanel import SocialPanelGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class TrackWidget(EasyManagedItem):
    """
    Shows track info as a single widget box.
    """

    image_trackCardImage     = SocialPanelGlobals.tooltipGUI.find('**/toontip_toon_holder_max')
    image_prestigeStarFilled = SocialPanelGlobals.gagSelectGui.find('**/prestige_star')
    image_prestigeStarEmpty  = SocialPanelGlobals.gagSelectGui.find('**/prestige_star_empty')

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = kwargsToOptionDefs(
            pos = (0, 0, 0),
            scale = 1.0,
            relief = None,
            image = self.image_trackCardImage,

            easyWidth=0.57,
            easyHeight=-0.835,

            track = [0, self.setGagTrack],
            level = [-1, self.setGagLevel],
            prestige = [False, self.setPrestige],
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)

        # Create various elements of the GUI.
        self.prestigeStarSlot = DirectFrame(
            parent=self,
            relief=None,
            image=self.image_prestigeStarEmpty,
            pos=(0, 0, -0.325),
            scale=0.17
        )

        self.prestigeStar = DirectFrame(
            parent=self.prestigeStarSlot,
            relief=None,
            image=self.image_prestigeStarFilled,
            pos=(0.001, 0, 0),
            scale=1.05882,
        )

        # Initialize options now.
        self.initialiseoptions(TrackWidget)

    def destroy(self):
        del self.prestigeStarSlot
        del self.prestigeStar
        super().destroy()

    def bindToScroll(self, easyScrolledFrame):
        easyScrolledFrame.bindToScroll(self.prestigeStarSlot)
        easyScrolledFrame.bindToScroll(self.prestigeStar)
        super().bindToScroll(easyScrolledFrame)

    """
    GUI updaters
    """

    def setGagTrack(self, track: Optional[AttackEnum] = None):
        """
        Sets the rendered Gag Track.
        """
        if track is not None:
            self['track'] = track
            return
        assert 0 <= int(self['track']) < 8

        # Update our icon.
        self._rerender()

    def setGagLevel(self, level: Optional[int] = None):
        """
        Sets the rendered Gag Level.
        """
        if level is not None:
            self['level'] = level
            return
        assert -1 <= int(self['level']) < 8

        # Update our icon.
        self._rerender()

    def setPrestige(self, prestige: Optional[bool] = None):
        """
        Sets the rendered prestige icon.
        """
        if prestige is not None:
            self['prestige'] = prestige
            return
        assert self['prestige'] in (True, False)

        # Update our icon.
        self._rerender()

    def setNoAccess(self):
        """
        Disables the current track from being accessed.
        """
        self['level'] = -1

    """
    GUI rendering
    """

    def _rerender(self):
        # Set the base track values.
        r, g, b = BattleGlobals.TrackColors[self['track']]
        self['image_color'] = Vec4(r, g, b, 1.0)

        # If we do not have access, darken the track.
        if self['level'] == -1:
            # The track color must be darker.
            r, g, b, _ = tuple(map(lambda x: x * 0.3, self['image_color']))
            self['image_color'] = Vec4(r, g, b, 0.3)

            # Add a darkened gag icon.
            self['geom'] = SocialPanelGlobals.invModels[self['track']][0]
            self['geom_color'] = (0, 0, 0, 1)
            self['geom_scale'] = 3.2
            self['geom_pos'] = (0, 0, 0.09)

            # Update the prestige overlays.
            self.prestigeStar.hide()
            self.prestigeStarSlot['image_color'] = (0.3, 0.3, 0.3, 1.0)

        # If we do, we need to match the widget to the gag.
        else:
            # Add the gag icon.
            track = self['track']
            level = self['level']
            self['geom'] = SocialPanelGlobals.invModels[track][level]
            self['geom_scale'] = 3.2
            self['geom_pos'] = (0, 0, 0.09)

            # Update the prestige overlays.
            self.prestigeStar.hide()
            if self['prestige']:
                self.prestigeStar.show()
            self.prestigeStarSlot['image_color'] = (1.0, 1.0, 1.0, 1.0)


if __name__ == "__main__":
    guis = []
    for i in range(8):
        gui = TrackWidget(
            parent=aspect2d,
            scale=0.30,
            track=i,
            level=i - 1,
            prestige=bool(i % 2),
        )
        guis.append(gui)
    UiHelpers.fillGridWithElements(
        initialGuiList=guis,
        horizontalCount=4, verticalCount=2,
        startPos=(0, 0, 0),
        centering=True,
        scale=0.30,
    )

    GUITemplateSliders(
        guis[0],
        'pos', 'scale'
    )
    base.run()
