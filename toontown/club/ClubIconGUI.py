"""
The ClubIcon GUI class.
Can be created and set anywhere with a ClubIcon passed in.
"""
from toontown.club.ClubClasses import ClubIcon
from toontown.club.ClubGlobals import ClubItemIndex
from toontown.hood import ZoneUtil
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class ClubIconGUI(DirectFrame):
    """
    Visualizes a ClubIcon.
    Use ClubIconGUI.setIcon(ClubIcon) to set the visual property of the icon.
    """
    clubBackgrounds = loader.loadModel('phase_3.5/models/gui/clubs/club_backgrounds')
    clubIcons = loader.loadModel('phase_3.5/models/gui/clubs/club_icons')

    @InjectorTarget
    def __init__(self, parent, **kw):
        # GUI boilerplate.
        optiondefs = ()
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # Define objects of this GUI.
        self.frame_background = None
        self.frame_icon = None
        self.clubIcon = ClubIcon()

        # Load elements of this GUI.
        self.load()

    def setIcon(self, clubIcon: ClubIcon):
        """Sets the icon appearance of this ClubIcon."""
        self.clubIcon = clubIcon
        self.notify.info(f"Updated clubIcon - {clubIcon}")
        self.refresh()

    """
    Loading methods
    """

    def load(self):
        # Load in the background and icon assets.
        statusEffectImages = base.loader.loadModel('phase_3.5/models/gui/battlegui/status_effects')
        bgImage = statusEffectImages.find('**/default_background')
        self.frame_background = DirectFrame(
            parent=self,
            relief=None,
            image=bgImage,
        )
        self.frame_icon = DirectFrame(
            parent=self,
            relief=None,
            geom=None,
            geom_scale=0.86,
        )
        statusEffectImages.removeNode()

        # Now use the default clubIcon appearance.
        self.refresh()

    def destroy(self):
        super().destroy()
        self.ignoreAll()
        self.clubIcon = None

    """
    Model accessors
    """

    def _getBaseNode(self):
        return self.clubBackgrounds.find('**/base')

    def _getBackground(self, clubIcon: ClubIcon):
        if clubIcon.backgroundId in (0, None):
            return None
        clubItem = ClubItemIndex.getItem(clubIcon.backgroundId)
        return self.clubBackgrounds.find(f'**/bg_{clubItem.getValue()}')

    def _getIconGeom(self, clubIcon: ClubIcon):
        if clubIcon.iconId in (0, None):
            return None
        clubItem = ClubItemIndex.getItem(clubIcon.iconId)
        return self.clubIcons.find(f'**/icon_{clubItem.getValue()}')

    """
    Refresh methods
    """

    def refresh(self):
        """Updates the appearance of the GUI to match our set clubIcon."""
        self.notify.info("Refreshing clubIcon.")

        # Set model data.
        self.frame_background['image'] = self._getBaseNode()
        self.frame_background['geom'] = self._getBackground(self.clubIcon)
        self.frame_icon['geom'] = self._getIconGeom(self.clubIcon)
        self.frame_icon['geom_scale'] = 0.9

        # Set color data.
        clubColor = self.clubIcon.getClubColor()
        bgColor = self.clubIcon.getBackgroundCol()
        self.setThemeColor(clubColor.getColor())
        self.setBackgroundColor(bgColor.getColor())

        # Listen for color changes.
        self.ignoreAll()
        self.accept(clubColor.getUpdateName(), self.setThemeColor)
        self.accept(bgColor.getUpdateName(), self.setBackgroundColor)

    def setThemeColor(self, col):
        self.frame_background['image_color'] = col

    def setBackgroundColor(self, col):
        self.frame_background['geom_color'] = col

    """
    Static methods
    """

    @staticmethod
    def getImageOfPlayground(zoneId: int):
        """Returns the icon image of a given zone id."""
        index = {
            ToontownGlobals.ToontownCentral: 12,
            ToontownGlobals.DonaldsDock: 13,
            ToontownGlobals.YeOlde: 14,
            ToontownGlobals.DaisyGardens: 15,
            ToontownGlobals.MinniesMelodyland: 16,
            ToontownGlobals.TheBrrrgh: 17,
            ToontownGlobals.OutdoorZone: 18,
            ToontownGlobals.DonaldsDreamland: 19,
            ToontownGlobals.SellbotHQ: 26,
            ToontownGlobals.CashbotHQ: 27,
            ToontownGlobals.LawbotHQ: 28,
            ToontownGlobals.BossbotHQ: 29,
            ToontownGlobals.BoardbotHQ: 30,
        }.get(ZoneUtil.getHoodId(zoneId))
        return ClubIconGUI.clubIcons.find(f'**/icon_{index}')

    @staticmethod
    def getThatSillyArrow():
        """Gets that silly arrow"""
        return ClubIconGUI.clubBackgrounds.find(f'**/bg_30')
