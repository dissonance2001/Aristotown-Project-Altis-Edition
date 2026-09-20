from typing import Optional

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()
    # base.initTalkAssistant()

from toontown.quest3.kudos.KudosConstants import getRankUpKudosTask
from toontown.gui.TTGui import kwargsToOptionDefs, getPopInSequence
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.toonbase import ToontownGlobals
from direct.gui.DirectGui import *


@DirectNotifyCategory()
class KudosProgressBarGUI(DirectFrame):
    """
    Shows the progress of Kudos in a given playground.
    """

    imageWidth = 12.89583 / 10

    @InjectorTarget
    def __init__(self, zoneId: int, parent, **kw):
        # GUI boilerplate.
        boardModel = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board_gui')
        optiondefs = kwargsToOptionDefs(
            relief=None,
            image=boardModel.find('**/ProgressBarBack'),
            image_scale=(1.29412, 0.1, 0.10503),
        )
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        # Make image and clip plane.
        self.zoneId = zoneId
        self.progressBar = DirectLabel(
            parent=self, relief=None,
            image=boardModel.find('**/PaperProgressBar'),
            image_scale=(self.imageWidth, 0.1, 0.1),
        )
        self.textLabel = DirectLabel(
            parent=self, relief=None,
            text='0 / 20 XP',
            text_pos=(0.0, -0.03057),
            text_scale=0.1,
        )
        boardModel.removeNode()
        clipper = PlaneNode('clipper')
        clipper.setPlane(Plane(Vec3(-1, 0, 0), Point3(-self.imageWidth / 2, 0, 0)))
        self.clipNP = self.attachNewNode(clipper)
        self.progressBar.setClipPlane(self.clipNP)

        self.setXPValues(20, 20)

    def destroy(self):
        self.clipNP.removeNode()
        super().destroy()

    def setXPValues(self, currentXp: int, maxXp: int, calcRankup: bool = True):
        if calcRankup:
            rankupReady = not (base.localAvatar and not getRankUpKudosTask(base.localAvatar, self.zoneId))
        else:
            rankupReady = currentXp >= maxXp
        if not rankupReady:
            self.textLabel.setText('{0} / {1} XP'.format(currentXp, maxXp))
            self.clipNP.setPos((currentXp / maxXp) * self.imageWidth, 0, 0)
        else:
            # Show the full bar.
            self.clipNP.setPos(self.imageWidth, 0, 0)

            # Show different text if we are on the rankup task.
            if calcRankup:
                rankupTask = getRankUpKudosTask(base.localAvatar, self.zoneId)
                if rankupTask and base.localAvatar.hasQuest(rankupTask):
                    self.textLabel.setText('Working On Rank-Up Task!')
                    return

            # Just do this simple text label.
            self.textLabel.setText('Rank-Up Task Ready!')


if __name__ == "__main__":
    gui = KudosProgressBarGUI(
        zoneId=2000,
        parent=aspect2d,
        pos=(0, 0, -0.2),
        scale=2,
    )
    GUITemplateSliders(
        guiAffected=gui,
        guiKeys=('image_scale', 'image_pos'),
        rounding=5,
    )
    base.run()
