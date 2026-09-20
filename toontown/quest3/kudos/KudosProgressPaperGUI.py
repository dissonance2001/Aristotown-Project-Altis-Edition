if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    base.initCR()  # defines base.cr
    # base.startHeadlessShow()
    # base.initTalkAssistant()
    from toontown.toon.DistributedToon import DistributedToon
    base.localAvatar = DistributedToon(cr=base.cr)
    base.localAvatar.doId = 0

from toontown.ai import HolidayGlobals
from toontown.club.ClubIconGUI import ClubIconGUI
from toontown.quest3.kudos.KudosProgressBarGUI import KudosProgressBarGUI
from toontown.quest3.kudos import KudosConstants
from toontown.gui.TTGui import kwargsToOptionDefs, getPopInSequence
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.hood import ZoneUtil
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class KudosProgressPaperGUI(EasyManagedItem):
    """
    Has a paper for the progress of Kudos in a given playground.
    """

    @InjectorTarget
    def __init__(self, zoneId: int, parent, **kw):
        # GUI boilerplate.
        boardModel = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board_gui')
        optiondefs = kwargsToOptionDefs(
            relief=None,
            pos=(0.0, 0.0, 0.035),
            image=boardModel.find('**/LongPaper'),
            image_scale=(5.15294, 1.0, 1.0),
        )
        boardModel.removeNode()
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(KudosProgressPaperGUI)

        self.zoneId = zoneId

        # Define objects of this GUI.
        self.label_icon = None
        self.text_description = None
        self.text_reward = None
        self.progressBar = None

        # Load elements of this GUI.
        self.load()
        self.setKudos()

        self.accept('kudosUpdated', self.setKudos)
        self.accept('questsChanged', self.setKudos)
        self.accept('questHistoryChanged', self.setKudos)
        # Also listen to this message so that the page can adjust the gumball reward label
        self.accept(HolidayGlobals.GumballHolidayStatusMessage, self.setKudos)

    """
    Loading methods
    """

    def load(self):
        self.label_icon = DirectLabel(
            parent=self, relief=None,
            pos=(-2.024, 0.0, 0.0103),
            scale=0.721,
            image=ClubIconGUI.getImageOfPlayground(self.zoneId),
        )
        self.text_description = DirectLabel(
            parent=self, relief=None,
            pos=(-0.89896, 0.0, 0.053),
            scale=0.186,
            text='Toontown Central\nRank 1',
        )
        self.progressBar = KudosProgressBarGUI(
            parent=self,
            zoneId=self.zoneId,
            pos=(1.149, 0.0, 0.07679),
            scale=1.864,
        )
        self.text_reward = DirectLabel(
            parent=self.progressBar, relief=None,
            pos=(-0.00176, 0.0, -0.11468),
            scale=0.06842,
            text='for: 15% Playground Discount',
        )

    def destroy(self):
        super().destroy()

    def setKudos(self, _=None):
        # Get some useful constants.
        if not base.localAvatar:
            return
        kudos = base.localAvatar.getKudos()
        totalXp = kudos.get(self.zoneId, 0)
        currentXp, maxXp = KudosConstants.getCurrentKudosXp(totalXp)
        rank = KudosConstants.getKudosRank(base.localAvatar, self.zoneId)

        # Update the description.
        pgName = ZoneUtil.zoneIdToName(self.zoneId)[0]
        self.text_description.setText(f'{pgName}\nRank {rank}')

        # Update the reward.
        self.text_reward.setText(f'for: {TTLocalizer.getKudosRewardFromRank(rank=rank + 1, zoneId=self.zoneId)}')

        # Update the progress bar.
        self.progressBar.setXPValues(currentXp, maxXp)


if __name__ == "__main__":
    gui = KudosProgressPaperGUI(
        zoneId=ToontownGlobals.DonaldsDock,
        parent=aspect2d,
        pos=(0, 0, -0.2),
        scale=0.5,
    )
    base.localAvatar.setKudos({
        1000: 120
    })
    GUITemplateSliders(
        guiAffected=gui.progressBar,
        guiKeys=('pos', 'scale'),
    )
    base.run()
