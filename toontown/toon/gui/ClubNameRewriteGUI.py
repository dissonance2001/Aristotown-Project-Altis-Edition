from toontown.club import ClubLocalizer
from toontown.toon.gui.ClubCreationGUI import ClubCreationGUI
from toontown.toonbase import TTLocalizer

from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class ClubNameRewriteGUI(ClubCreationGUI):
    """
    The GUI used for rewriting your Club Name.

    We subclass the ClubCreationGUI to disable Club Icon changing,
    making sure that only the club name entry is enabled.
    """

    def load(self):
        super().load()
        self._updateClubIcon()

        self.clubThemeSelection.disable()
        self.bar_clubIconGeom.disable()
        self.bar_clubIconBg.disable()
        self.bar_clubIconBgColor.disable()

    def destroy(self, clubMade=False, timeout=False):
        if self.seq:
            self.seq.finish()
        base.cr.playGame.getPlace().setState('Walk')
        base.localAvatar.unlockControlsForEntry()
        base.transitions.noTransitions()
        super().destroy()
        messenger.send(self.msg_onExit, [clubMade, True, timeout])

    def _updateClubIcon(self):
        # Update the ClubIconGUI.
        clubContainer = base.cr.clubMgr.getLocalClub()
        if clubContainer:
            self.clubIconGUI.setIcon(clubContainer.clubIcon)

            # Hide the "CUSTOMIZE YOUR ICON!" asset.
            self.label_clubIconOverlay.hide()

        # Update confirm validity.
        self.updateConfirmValidity()

    def updateConfirmValidity(self):
        """
        Figures out if we can validly choose a club icon.
        """
        def disableMake():
            self.button_make['state'] = DGG.DISABLED
            self.button_make['image_color'] = (0.7, 0.7, 0.7, 1.0)

        # We've set a name right?
        if self.entry_club_name.get() in (ClubLocalizer.ClubInitialFillName, ClubLocalizer.ClubGUIBlockedNameDialog):
            # We should probably Do That.
            return disableMake()

        # Looks like it's safe!
        self.button_make['state'] = DGG.NORMAL
        self.button_make['image_color'] = (1.0, 1.0, 1.0, 1.0)

    def createClub(self):
        """Asks the DistributedClubManager to make our club!"""
        base.cr.clubMgr.requestUpdateClubName(self.entry_club_name.get())
