import time

from toontown.quest3.kudos.KudosConstants import KUDOS_RESET_INTERVAL
from toontown.time import TimeUtil

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()

from toontown.quest3.kudos.KudosProgressPaperGUI import KudosProgressPaperGUI
from toontown.quest3.kudos.KudosDetailProgressPaperGUI import KudosDetailProgressPaperGUI
from toontown.gui.EasyScrolledFrame import EasyScrolledFrame
from toontown.gui.EasyManagedItem import EasyManagedItem
from toontown.gui.TTGui import kwargsToOptionDefs
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.SequenceQueue import SequenceQueue
from toontown.utils.DGGEventIgnorer import ignore_event
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.toonbase import ToontownGlobals
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.interval.IntervalGlobal import *
from direct.gui import DirectGuiGlobals as DGG
from panda3d.core import *


@DirectNotifyCategory()
class KudosPage(DirectFrame):

    sequenceDebounce = 0.05

    enterDuration = 0.2
    enterEase = 'easeOut'
    exitDuration = 0.15
    exitEase = 'easeIn'
    itemMoveDist = -1.5

    itemScale = 0.19877
    itemSpacing = -0.2
    itemPosOffset = (0.53877, 0.0, -0.1084)

    @InjectorTarget
    def __init__(self, parent=None, **kw):
        # GUI boilerplate.
        boardModel = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board.bam')
        optiondefs = kwargsToOptionDefs(
            relief=None,

            # Adjust these to place on the page.
            scale=1.3,
            pos=(0, 0, 0.05),

            # The board image itself.
            image=boardModel.find('**/kudos_board'),
            image_scale=(1.265, 1.0, 1.034),
        )
        boardModel.removeNode()
        self.defineoptions(kw, optiondefs)
        super().__init__(parent=parent, **kw)
        self.initialiseoptions(KudosPage)

        # References
        self.scrolledFrame = None  # type: EasyScrolledFrame
        self.papers = {}
        self.infoPapers = {}
        self.openMotions = {}
        self.cleanedUp = False
        self.label_reset = None

        self.sequenceQueue = SequenceQueue(maxSize=3, autoSkip=True)

        self.load()
        if base.localAvatar:
            self.setKudos(base.localAvatar.getKudos())
        self.accept('kudosUpdated', self.setKudos)

        self.updateTimer()
        taskMgr.add(self.updateTimer, 'kudosPage-updateTimer')

    def load(self):
        boardModel = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board_gui')
        self.scrolledFrame = EasyScrolledFrame(
            parent=self, relief=None,
            pos=(0, 0, 0.011),
            scale=1.0,

            verticalScroll_relief=None,
            verticalScroll_image=boardModel.find('**/Kudos_Scrollbar'),
            verticalScroll_image_scale=(0.10315, 1.0, 0.77136),
            verticalScroll_image_pos=(-0.00247, 0.0, -0.09225),

            verticalScroll_thumb_relief=None,
            verticalScroll_thumb_image=boardModel.find('**/Kudos_Scroll'),
            verticalScroll_thumb_image_scale=(0.05994, 1.0, 0.10222),
            verticalScroll_thumb_image_pos=(-0.00089, 0.0, 0.01531),

            frameSize=(-0.58469, 0.58469, -0.45486, 0.27798),
            scrollBarPosOffset=(-0.01569, 0.0, -0.00362),
            scrollBarScale=0.9679,
            thumbHeight=0.06592,
        )
        boardModel.removeNode()

        for hoodId in ToontownGlobals.MainTaskingHoods:
            paper = KudosProgressPaperGUI(
                zoneId=hoodId, parent=None, scale=self.itemScale,
                posOffset=self.itemPosOffset,
                easyHeight=self.itemSpacing,
                easyScrolledFrame=self.scrolledFrame,
            )
            paper['state'] = DGG.NORMAL
            paper.bind(event=DGG.WITHIN,  command=self.prepareShowHoodRewards, extraArgs=[hoodId])
            paper.bind(event=DGG.WITHOUT, command=self.prepareHideHoodRewards, extraArgs=[hoodId])
            self.papers[hoodId] = paper

        self.scrolledFrame.updateItemPositions()

        self.label_reset = DirectLabel(
            parent=self, relief=None,
            pos=(0.0, 0.0, -0.496),
            scale=0.30041,
            text='Resets in: 3:49:20',
            text_scale=0.13,
            text_fg=(0, 0, 0, 1),
        )

    def destroy(self):
        self.cleanedUp = True
        self.ignoreAll()

        taskMgr.remove('kudosPage-updateTimer')

        # Kill queue first.
        self.sequenceQueue.finish()
        del self.sequenceQueue

        # Delete refs.
        del self.scrolledFrame
        del self.papers
        del self.infoPapers
        del self.openMotions

        # Complete destruction
        super().destroy()

    """
    GUI changes
    """

    def setKudos(self, kudos: dict):
        # Disable all papers.
        for paper in self.papers.values():
            paper.hide()
            paper.setActivePositioning(False)

        # Engage all papers, according to kudos.
        for zoneId in kudos.keys():
            paper = self.papers.get(zoneId)
            if paper:
                paper.show()
                paper.setActivePositioning(True)

        # Set the scrollframe height.
        activeHoods = len(kudos.keys())
        self.scrolledFrame['forcedHeight'] = self.itemSpacing * (activeHoods + 1)

        # Update item positions now.
        self.scrolledFrame.updateItemPositions()

    """
    Browsing rewards
    """

    @ignore_event
    def prepareShowHoodRewards(self, hoodId: int):
        if hoodId in self.openMotions:
            # We have a task that was about to perform a motion -- debounce it
            taskName = self.openMotions.get(hoodId)
            taskMgr.remove(taskName)
            self.openMotions.pop(hoodId)
            return
        taskName = f'prepareShow-{hoodId}'
        self.openMotions[hoodId] = taskName
        taskMgr.doMethodLater(self.sequenceDebounce, self.showHoodRewards, taskName, extraArgs=[hoodId])

    @ignore_event
    def prepareHideHoodRewards(self, hoodId: int):
        if hoodId in self.openMotions:
            # We have a task that was about to perform a motion -- debounce it
            taskName = self.openMotions.get(hoodId)
            taskMgr.remove(taskName)
            self.openMotions.pop(hoodId)
            return
        taskName = f'prepareHide-{hoodId}'
        self.openMotions[hoodId] = taskName
        taskMgr.doMethodLater(self.sequenceDebounce, self.hideHoodRewards, taskName, extraArgs=[hoodId])

    def showHoodRewards(self, hoodId: int):
        if hoodId in self.openMotions:
            self.openMotions.pop(hoodId)

        # Cleanup all active info papers.
        for hoodId in list(self.infoPapers.keys()):
            self.hideHoodRewards(hoodId)

        # Create an info paper first.
        paper = KudosDetailProgressPaperGUI(
            zoneId=hoodId, parent=None, scale=self.itemScale,
        )
        paper.hide()
        self.infoPapers[hoodId] = paper

        # What index are we adding in?
        def getPositionIndex():
            relatedPaper = self.papers.get(hoodId)
            return self.scrolledFrame.canvasItems.index(relatedPaper) + 1

        # Perform a sequence to add it.
        sequence = Sequence(
            # Start managing the item.
            Func(self.scrolledFrame.addItem, paper, getPositionIndex),
            Func(paper.show),
            Parallel(
                # Setting the item's position offset.
                LerpFunctionInterval(
                    function=self.setPaperX, duration=self.enterDuration,
                    fromData=self.itemMoveDist, toData=0.0, blendType=self.enterEase,
                    extraArgs=[paper],
                ),
                # Setting the item's height.
                LerpFunctionInterval(
                    function=self.setPaperHeight, duration=self.enterDuration,
                    fromData=0.0, toData=self.itemSpacing, blendType=self.enterEase,
                    extraArgs=[paper],
                ),
                # Making sure the items are positioned.
                LerpFunctionInterval(
                    function=lambda _: self.scrolledFrame.updateItemPositions(),
                    duration=self.enterDuration + 0.01,
                ),
            )
        )
        self.sequenceQueue.append(sequence)

    def hideHoodRewards(self, hoodId: int):
        if hoodId in self.openMotions:
            self.openMotions.pop(hoodId)

        if not self.infoPapers.get(hoodId):
            return
        paper = self.infoPapers.pop(hoodId)

        # Perform a sequence to nuke it.
        sequence = Sequence(
            Parallel(
                # Setting the item's position offset.
                LerpFunctionInterval(
                    function=self.setPaperX, duration=self.exitDuration,
                    fromData=0.0, toData=self.itemMoveDist, blendType=self.exitEase,
                    extraArgs=[paper],
                ),
                # Setting the item's height.
                LerpFunctionInterval(
                    function=self.setPaperHeight, duration=self.exitDuration,
                    fromData=self.itemSpacing, toData=0.0, blendType=self.exitEase,
                    extraArgs=[paper],
                ),
                # Making sure the items are positioned.
                LerpFunctionInterval(
                    function=lambda _: self.scrolledFrame.updateItemPositions(),
                    duration=self.exitDuration + 0.01,
                ),
            ),
            # Destroy the paper.
            Func(self.removePaper, paper)
        )
        self.sequenceQueue.append(sequence)

    """
    Static methods for positioning GUI
    """

    @staticmethod
    def setPaperX(xoff: float, paper: EasyManagedItem):
        x, y, z = KudosPage.itemPosOffset
        if paper:
            paper['posOffset'] = (x + xoff, y, z)

    @staticmethod
    def setPaperHeight(height: float, paper: EasyManagedItem):
        if paper:
            paper['easyHeight'] = height

    def removePaper(self, paper):
        if self.cleanedUp:
            return
        self.scrolledFrame.removeItem(paper)
        paper.destroy()

    def updateTimer(self, task=None):
        # Update the timer.
        secondsLeft = int(TimeUtil.getNextTimestampOfInterval(KUDOS_RESET_INTERVAL) - time.time())
        m, s = divmod(secondsLeft, 60)
        h, m = divmod(m, 60)
        s = max(s, 0)

        if h > 0:
            self.label_reset.setText(f'Resets in: {h:d}:{m:02d}:{s:02d}')
        elif m > 0:
            self.label_reset.setText(f'Resets in: {m:02d}:{s:02d}')
        else:
            self.label_reset.setText(f'Resets in: {s} second{"s" if s != 1 else ""}')

        # Run the task again.
        if task is not None:
            task.delayTime = 1.0
            return task.again


if __name__ == "__main__":
    gui = KudosPage()
    # gui.load()
    # gui.enter()
    GUITemplateSliders(
        guiAffected=gui.scrolledFrame,
        guiKeys=(
            'pos',
        ),
        # scale=0.25,
    )
    base.run()
