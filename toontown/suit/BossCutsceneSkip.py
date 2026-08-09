from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton
from direct.gui import DirectGuiGlobals as DGG
from direct.interval.IntervalGlobal import Sequence, Func, LerpPosInterval
from pandac.PandaModules import TextNode, Vec4
from toontown.toonbase import TTLocalizer, ToontownGlobals

try:
    from toontown.menu.MainMenuGui import MainMenuButton
except ImportError:
    MainMenuButton = None


class BossCutsceneSkip(object):
    """Clash-styled client-side skip control for boss transition movies.

    The battle synchronization remains the same as the previous patch: the
    local movie interval is finished normally, which executes its original
    callback and existing doneBarrier call.
    """

    # These are copied from Clash's DistributedCutsceneSkipButton.
    onScreenPos = (-0.2, 0, 0.05)
    offScreenPos = (1.0, 0, 0.05)

    def __init__(self, boss):
        self.boss = boss
        self.gui = None
        self.voteLabel = None
        self.voteButton = None
        self.buttonModel = None
        self.moveTrack = None
        self.intervalName = None
        self.skipRequested = False
        self.playerTotal = 1
        self.pendingVoteTotal = 0
        self.pendingPlayerTotal = 1
        self.hasPendingVoteState = False

    def _normalise(self, value):
        if value is None:
            return ''
        return ''.join([char.lower() for char in str(value) if char.isalnum()])

    def _isSkippable(self, intervalName):
        intervalKey = self._normalise(intervalName)
        stateKey = self._normalise(getattr(self.boss, 'state', ''))
        combined = intervalKey + stateKey

        for value in getattr(self.boss, 'cutsceneSkipExtraIntervals', ()):
            if intervalKey == self._normalise(value):
                return True

        blocked = ('victory', 'reward', 'epilogue', 'defeat', 'elevator')
        for word in blocked:
            if word in combined:
                return False

        allowed = ('introduction', 'preparebattle', 'rolltobattle')
        for word in allowed:
            if word in combined:
                return True

        return False

    def _hasLocalToon(self):
        if not self.boss:
            return False
        try:
            return self.boss.hasLocalToon()
        except:
            return False

    def _getPlayerTotal(self):
        try:
            total = len(self.boss.involvedToons)
        except:
            total = 1
        return max(1, total)

    def _getText(self, name, fallback):
        return getattr(TTLocalizer, name, fallback)

    def _getInstructionScale(self):
        scale = getattr(TTLocalizer, 'MRPinstructionsText', 0.05)
        try:
            return float(scale)
        except:
            return 0.05

    def _getSignFont(self):
        try:
            return ToontownGlobals.getSignFont()
        except:
            return None

    def _formatVotes(self, votes):
        template = self._getText('CutsceneSkipButtonVotes', 'Votes to skip: %s/%s')
        try:
            return template % (votes, self.playerTotal)
        except:
            return 'Votes to skip: %s/%s' % (votes, self.playerTotal)

    def _createExactClashButton(self):
        if MainMenuButton is None:
            raise ImportError('MainMenuButton is unavailable')

        # Exact Clash sizing and placement from DistributedCutsceneSkipButton.
        self.voteButton = MainMenuButton(
            parent=self.gui,
            image_scale=(0.6, 0.15, 0.15),
            image1_scale=(0.6, 0.15, 0.15),
            image2_scale=(0.6, 0.15, 0.15),
            text=self._getText('CutsceneSkipButtonSkip', 'Skip'),
            text_scale=0.07,
            pos=(-0.14, 0, 0.13),
            command=self._requestSkip
        )

    def _createModelFallback(self):
        """Rebuild MainMenuButton's appearance from the Clash menu model."""
        self.buttonModel = loader.loadModel('phase_3/models/gui/ttcc_menu_buttons')
        normal = self.buttonModel.find('**/menubtn')
        pressed = self.buttonModel.find('**/menubtn-press')

        if normal.isEmpty() or pressed.isEmpty():
            raise StandardError, 'Missing ttcc_menu_buttons geometry'

        self.voteButton = DirectButton(
            parent=self.gui,
            relief=None,
            image=(normal, pressed, normal, normal),
            image_scale=(0.6, 0.15, 0.15),
            image1_scale=(0.6, 0.15, 0.15),
            image2_scale=(0.6, 0.15, 0.15),
            image3_scale=(0.6, 0.15, 0.15),
            image3_color=(0.75, 0.75, 0.75, 1),
            text=self._getText('CutsceneSkipButtonSkip', 'Skip'),
            text_scale=0.07,
            text_align=TextNode.ACenter,
            text_pos=(0, -0.02),
            text_fg=Vec4(1, 1, 1, 1),
            text_style=3,
            pos=(-0.14, 0, 0.13),
            command=self._requestSkip
        )

    def _createPlainFallback(self):
        # Last-resort protection only. Altis normally has the Clash menu model.
        self.voteButton = DirectButton(
            parent=self.gui,
            relief=DGG.RAISED,
            borderWidth=(0.025, 0.025),
            frameSize=(-0.3, 0.3, -0.075, 0.075),
            frameColor=(0.17, 0.35, 0.55, 1),
            text=self._getText('CutsceneSkipButtonSkip', 'Skip'),
            text_scale=0.07,
            text_fg=(1, 1, 1, 1),
            text_shadow=(0, 0, 0, 1),
            text_pos=(0, -0.02),
            pos=(-0.14, 0, 0.13),
            command=self._requestSkip
        )

    def _createGui(self):
        self.playerTotal = self._getPlayerTotal()
        self.gui = DirectFrame(
            parent=base.a2dBottomRight,
            relief=None,
            pos=self.offScreenPos
        )

        labelArgs = {
            'parent': self.gui,
            'text': self._formatVotes(0),
            'scale': self._getInstructionScale(),
            'text_align': TextNode.ARight,
            'text_fg': (1.0, 1.0, 1.0, 1.0),
            'pos': (0.15, 0, -0.02),
            'relief': None
        }
        signFont = self._getSignFont()
        if signFont:
            labelArgs['text_font'] = signFont
        self.voteLabel = DirectLabel(**labelArgs)

        try:
            self._createExactClashButton()
        except:
            try:
                self._createModelFallback()
            except:
                self._createPlainFallback()

        self._moveInInitial()
        if self.hasPendingVoteState:
            self.setVoteSkips(self.pendingVoteTotal, self.pendingPlayerTotal)

    def _clearMoveTrack(self):
        if self.moveTrack:
            self.moveTrack.finish()
            self.moveTrack = None

    def _moveInInitial(self):
        self._clearMoveTrack()
        self.moveTrack = Sequence(
            Func(self.gui.show),
            LerpPosInterval(
                self.gui,
                1.0,
                self.onScreenPos,
                self.offScreenPos,
                blendType='easeInOut'
            )
        )
        self.moveTrack.start()

    def intervalStored(self, intervalName, interval):
        if not self._isSkippable(intervalName):
            return
        if not self._hasLocalToon():
            return

        self.cleanup()
        self.intervalName = intervalName
        self.skipRequested = False
        self._createGui()

    def _requestSkip(self):
        if self.skipRequested or not self.boss or not self.intervalName:
            return

        interval = self.boss.activeIntervals.get(self.intervalName)
        if not interval:
            self.cleanup()
            return

        self.skipRequested = True
        if self.voteButton:
            self.voteButton['state'] = DGG.DISABLED

        requestVote = getattr(self.boss, 'requestCutsceneSkipVote', None)
        if requestVote:
            requestVote()
            return

        if self.voteLabel:
            self.voteLabel['text'] = self._formatVotes(1)
        interval.finish()

    def setVoteSkips(self, voteTotal, playerTotal):
        try:
            voteTotal = int(voteTotal)
        except:
            voteTotal = 0
        try:
            playerTotal = int(playerTotal)
        except:
            playerTotal = 1
        self.pendingVoteTotal = max(0, voteTotal)
        self.pendingPlayerTotal = max(1, playerTotal)
        self.hasPendingVoteState = True
        self.playerTotal = self.pendingPlayerTotal
        if self.voteLabel:
            self.voteLabel['text'] = self._formatVotes(self.pendingVoteTotal)

    def setCutsceneSkip(self):
        if not self.boss or not self.intervalName:
            return
        interval = self.boss.activeIntervals.get(self.intervalName)
        if not interval:
            return
        self.skipRequested = True
        if self.voteButton:
            self.voteButton['state'] = DGG.DISABLED
        interval.finish()

    def intervalCleared(self, intervalName):
        if intervalName != self.intervalName:
            return

        self.intervalName = None
        if self.skipRequested:
            # Clash also leaves the voted button disabled while waiting for the
            # remaining players. The next boss state cleans this GUI up.
            return
        self.cleanup()

    def intervalsCleaned(self):
        self.cleanup()

    def stateChanged(self, state):
        self.cleanup()
        self.pendingVoteTotal = 0
        self.pendingPlayerTotal = 1
        self.hasPendingVoteState = False

    def cleanup(self):
        self._clearMoveTrack()

        if self.voteLabel:
            self.voteLabel.destroy()
            self.voteLabel = None
        if self.voteButton:
            self.voteButton.destroy()
            self.voteButton = None
        if self.gui:
            self.gui.destroy()
            self.gui = None
        if self.buttonModel:
            self.buttonModel.removeNode()
            self.buttonModel = None

        self.intervalName = None
        self.skipRequested = False
        self.playerTotal = 1

    def delete(self):
        self.cleanup()
        self.boss = None
