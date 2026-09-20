import os
from typing import Optional

from toontown.toon.gui import GuiBinGlobals
from toontown.utils.DGGEventIgnorer import ignore_event

if __name__ == "__main__":
    from tools.headless.headlessbase import HeadlessStart
    from tools.headless.headlessbase.HeadlessBase import HeadlessBase
    base = HeadlessBase(wantHotkeys=False)
    if __debug__:
        from toontown.utils.DeveloperInjector import startInjector
        startInjector()
    from toontown.quest3.objectives import *
    DefeatCogObjective()
    # base.initCR()  # defines base.cr
    # base.startHeadlessShow()
    # base.initTalkAssistant()

import time

from toontown.quest3.questlines.KudosQuestLine import KudosQuestLine
from toontown.quest3.kudos.KudosConstants import KUDOS_RESET_INTERVAL, KUDOS_QUESTS_PER_NPC, getRankUpKudosTask
from toontown.quest3.kudos.KudosProgressPaperGUI import KudosProgressPaperGUI
from toontown.quest3.base.QuestReference import QuestReference, QuestId
from toontown.quest3.base.QuestHistory import QuestHistory
from toontown.quest3.gui.Quest3Poster import QuestPoster
from toontown.quest3.QuestEnums import QuestSource
from toontown.toon.npc import NPCToons
from toontown.toon.npc.NPCToonConstants import NPCToonEnum
from toontown.gui.TTGui import kwargsToOptionDefs, getPopInSequence
from toontown.gui.GUITemplateSliders import GUITemplateSliders
from toontown.gui.UiHelpers import generateButtonImages
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.utils.InjectorTarget import InjectorTarget
from toontown.toonbase import ToontownGlobals
from toontown.time import TimeUtil
from direct.showbase.PythonUtil import lerp
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *


PosterScale = 0.34


@DirectNotifyCategory()
class ExteriorKudosBoardGUI(DirectFrame):
    """
    The exterior Kudos Board GUI, which gets opened per playground.
    """

    boardScale = 1.92
    posterCount = 12

    timerTaskName = 'ExteriorKudosBoardGUI-Timer'

    @InjectorTarget
    def __init__(self, board, zoneId: int, parent=aspect2d, **kw):
        # GUI boilerplate.
        boardModel = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board.bam')
        optiondefs = kwargsToOptionDefs(
            relief=None,
            pos=(0.0, 0.0, 0.00899),
            image=boardModel.find('**/kudos_board'),
            image_scale=(1.265, 1.0, 1.034),
        )
        boardModel.removeNode()
        self.defineoptions(kw, optiondefs)
        super().__init__(parent, **kw)
        self.initialiseoptions(self.__class__)

        self.board = board
        self.zoneId = zoneId

        self.postersLastUpdated = 0

        # Define objects of this GUI.
        self.button_info = None
        self.button_cancel = None
        self.label_reset = None
        self.progressPaper = None
        self.questPosters = []
        self.qpTransitionNodes = []

        # Load elements of this GUI.
        self.load()
        self.accept('questsChanged', self.updateQuestPosters)
        self.accept('questHistoryChanged', self.updateQuestPosters)

        # Do the pop-in sequence.
        self.popSequence = None
        self.hoverSeqs = {}

        # Track hovered posters
        self.canHover = False
        self.hoveredPosters = []

        # Begin reset timer update.
        self.updateTimer()
        taskMgr.add(self.updateTimer, self.timerTaskName)

    """
    Loading methods
    """

    def load(self):
        # Get the posters.
        for i in range(self.posterCount):
            node = self.attachNewNode(f'poster-{i}')
            poster = QuestPoster(parent=node)
            poster.hoverFrame = DirectFrame(parent=poster, frameSize=(-0.4, 0.4, -0.28, 0.28), relief=None,
                                            sortOrder=5)
            poster.hoverFrame.bind(DGG.WITHIN, self.hoverPoster, [poster, i, True])
            poster.hoverFrame.bind(DGG.WITHOUT, self.hoverPoster, [poster, i, False])
            poster.hoverFrame['state'] = DGG.NORMAL
            self.qpTransitionNodes.append(node)
            self.questPosters.append(poster)
        self.placeQuestPosters()
        self.updateQuestPosters()

        boardModel = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board_gui.bam')
        self.button_info = DirectButton(
            parent=self, relief=None,
            pos=(0.51606, 0.0, 0.31206 + 0.015),
            scale=0.09806,
            image=generateButtonImages(boardModel, prefix='Kudos_Question_', normal='N', pressed='P', hover='H'),
            image_scale = (87/86, 1.0, 1.0),
            command=self.onInfo,
        )
        self.button_info.hide()  # Add later if we want people to be smart
        self.button_cancel = DirectButton(
            parent=self, relief=None,
            pos=(0.61306, 0.0, 0.31206 + 0.015),
            scale=0.09806,
            image=generateButtonImages(boardModel, prefix='Kudos_Exit_', normal='N', pressed='P', hover='H'),
            image_scale=(87 / 86, 1.0, 1.0),
            command=self.onCancel,
        )
        self.progressPaper = KudosProgressPaperGUI(
            zoneId=self.zoneId, parent=self,
            pos=(0.004, 0.0, -0.38021 + 0.015),
            scale=0.18,
        )
        self.label_reset = DirectLabel(
            parent=self, relief=None,
            pos=(0.0, 0.0, -0.496),
            scale=0.30041,
            text='Resets in: 3:49:20',
            text_scale=0.13,
            text_fg=(0, 0, 0, 1),
        )
        kudosPoster = loader.loadModel('phase_3.5/models/gui/kudos/kudos_board_gui')
        self.kudosHQPaper = DirectFrame(
            parent=self, relief=None,
            pos=(0, 0, 0),
            image=kudosPoster.find('**/Paper1'),
            image_scale=Vec3(0.8, 1.0, 0.58) * 0.5,
            text='',
            text_pos=(0, 0.022),
            text_fg=(0, 0, 0, 1),
            text_scale=(0.037),
            text_align=TextNode.ACenter,
            text_wordwrap=15,
        )
        self.kudosHQPaper.hide()
        kudosPoster.removeNode()
        boardModel.removeNode()

    def destroy(self):
        if self.popSequence:
            self.popSequence.finish()
            self.popSequence = None
        for hoverSeq in self.hoverSeqs.values():
            hoverSeq.finish()
        self.hoverSeqs = {}
        self.hoveredPosters = []
        taskMgr.remove(self.timerTaskName)
        self.ignoreAll()
        super().destroy()

    def show(self):
        super().show()
        self.updateQuestPosters(forceSet=True)

    """
    Visual update methods
    """

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

        # Update posters.
        self.updateQuestPosters()

        # Run the task again.
        if task is not None:
            task.delayTime = 1.0
            return task.again

    def setDisclaimer(self, msg: Optional[str] = None):
        """
        Sets the disclaimer on the kudos board.
        """
        if msg is None:
            self.kudosHQPaper.hide()
        else:
            self.kudosHQPaper.show()
            self.kudosHQPaper['text'] = msg

    """
    Quest Poster methods
    """

    def placeQuestPosters(self,
                          xstart: float = -0.42,
                          xend: float = 0.42,
                          zstart: float = 0.19,
                          zend: float = -0.19,
                          scale: float = PosterScale,
                          rows: int = 4,
                          cols: int = 3,):
        for i, poster in enumerate(self.questPosters):
            xindex = i // cols
            zindex = i % cols
            xpos = lerp(xstart, xend, xindex / (rows - 1))
            zpos = lerp(zstart, zend, zindex / (cols - 1))
            poster.setPos(xpos, 0, zpos)
            if scale is not None:
                poster.setScale(scale)

    def updateQuestPosters(self, forceSet: bool = False):
        # Should we update the poster refs?
        nextInterval = TimeUtil.getNextTimestampOfInterval(KUDOS_RESET_INTERVAL)
        if self.postersLastUpdated == nextInterval and not forceSet:
            self.updatePosterVisibility()
            return
        self.postersLastUpdated = nextInterval

        # Get relevant HQ officers.
        questIds = KudosQuestLine.getAvailableKudosQuests(self.zoneId)
        if not questIds:
            # We may not be loaded yet, if this is the case
            return

        # Get the posters.
        for questPoster, questId in zip(self.questPosters, questIds):
            questPoster.setQuestId(questId)
            questPoster.show()

        if forceSet:
            self.updatePosterVisibility()

    def updatePosterVisibility(self):
        # Can we get a new quest?
        rankUpTask = getRankUpKudosTask(base.localAvatar, self.zoneId) if base.localAvatar else None
        canAddQuest = base.localAvatar.canAddQuest() if base.localAvatar else False

        if rankUpTask is not None:
            # We're going to show the rank-up task.
            # Hide all the posters.
            for poster in self.questPosters:
                poster.hide()

            # Otherwise, we tell people to go the Toon HQ.
            self.kudosHQPaper.show()

            # If we have the rank-up task... we're done here.
            if base.localAvatar.hasQuest(rankUpTask, history=True):
                self.setDisclaimer('Complete your\nRank-Up Task to get\nmore Kudos Tasks!')
            else:
                self.setDisclaimer('Visit an HQ Officer\nto receive your\nRank-Up Task!')
        else:
            # We're going to show all of the randomly-generated tasks.
            # Update the posters.
            self.placeQuestPosters(scale=None)

            # Hide the rank-up disclaimer
            postersVisible = False
            self.kudosHQPaper.hide()

            for poster in self.questPosters:
                # Get its questref if it exists.
                questRef = poster.questReference  # type: QuestReference
                if questRef is None:
                    continue

                # Hide or show the poster.
                poster.show()
                if base.localAvatar and base.localAvatar.hasQuest(questRef.getQuestId(), history=True):
                    poster.hide()
                else:
                    postersVisible = True
                    poster.show()

                # Set the choice button, if we can add a quest.
                poster.setChoiceButton()
                if canAddQuest:
                    poster.setChoiceButton(self.chooseKudosQuest)

            # Show or hide the disclaimer depending.
            if postersVisible:
                # Hide the disclaimer -- there are tasks to be claimed.
                self.setDisclaimer()
            else:
                self.setDisclaimer('All Tasks Cleared!\nCome back for the\nnext reset!')

    def chooseKudosQuest(self, questId):
        self.board.chooseKudosQuest(questId)

    @ignore_event
    def hoverPoster(self, poster, index, inside=True):
        if not self.canHover:
            return

        def startSeq(i, seq):
            hoverSeq = self.hoverSeqs.get(i)
            if hoverSeq:
                hoverSeq.pause()
            seq.start()
            self.hoverSeqs[i] = seq

        def startUpSeq(i):
            poster = self.questPosters[i]
            newSeq = Sequence(
                Func(poster.setBin, 'sorted-gui-popup', GuiBinGlobals.KudosQuestPopupBin),
                LerpScaleInterval(poster, 0.15, PosterScale*1.3, blendType='easeInOut')
            )
            startSeq(i, newSeq)

        def startDownSeq(i):
            poster = self.questPosters[i]
            newSeq = Sequence(
                Func(poster.clearBin),
                LerpScaleInterval(poster, 0.15, PosterScale, blendType='easeInOut')
            )
            startSeq(i, newSeq)

        if inside:
            if index in self.hoveredPosters:
                return
            self.hoveredPosters.append(index)
            if len(self.hoveredPosters) == 1:
                startUpSeq(index)
        else:
            if index not in self.hoveredPosters:
                return
            self.hoveredPosters.remove(index)
            startDownSeq(index)
            for otherIndex in self.hoveredPosters:
                startUpSeq(otherIndex)

    def setCanHover(self, canHover):
        self.canHover = canHover

    """
    Button methods
    """

    def onInfo(self):
        pass

    def onCancel(self):
        if self.board:
            self.board.closeGui()

    """
    Sequences
    """

    posterPopTime = 0.25
    posterPopDelay = 0.04
    posterPopBetween = 0.08
    posterPopList = (
        (2,),
        (1, 5),
        (0, 4, 8),
        (3, 7, 11),
        (6, 10),
        (9,),
    )

    def hide(self):
        if self.popSequence:
            self.popSequence.finish()
            self.popSequence = None
        for hoverSeq in self.hoverSeqs.values():
            hoverSeq.finish()
        self.hoverSeqs = {}
        for poster in self.questPosters:
            poster.setScale(PosterScale)
        super().hide()

    def performInitSequence(self):
        self.progressPaper.setKudos()
        self.popSequence = Parallel(
            getPopInSequence(self, self.boardScale),
            self.makeTaskAppearSequence()
        )
        self.popSequence.start()
        if settings['reduce-gui-movement']:
            self.popSequence.finish()
            self.popSequence = None

    def makeTaskAppearSequence(self):
        posterScale = self.questPosters[0].getScale()
        for node, poster in zip(self.qpTransitionNodes, self.questPosters):
            poster.setScale(0.05)
            node.hide()
        retTrack = Parallel()
        for index, popList in enumerate(self.posterPopList):
            for posterIndex in popList:
                poster = self.questPosters[posterIndex]
                node = self.qpTransitionNodes[posterIndex]
                delay = self.posterPopDelay + (self.posterPopBetween * index)
                retTrack.append(Sequence(
                    Wait(delay),
                    Func(node.show),
                    getPopInSequence(poster, posterScale, duration=self.posterPopTime)
                ))
        return Sequence(retTrack, Func(self.setCanHover, True))


if __name__ == "__main__":
    os.environ['REALM'] = 'dev'
    gui = ExteriorKudosBoardGUI(
        board=None,
        zoneId=ToontownGlobals.ToontownCentral,
        parent=aspect2d,
        pos=(0, 0, 0),
        scale=ExteriorKudosBoardGUI.boardScale,
    )
    GUITemplateSliders(
        guiAffected=gui.label_reset,
        guiKeys=('pos', 'scale'),
    )
    base.run()
