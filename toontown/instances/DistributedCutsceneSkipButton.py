from __future__ import absolute_import
from direct.distributed.DistributedObject import DistributedObject
from direct.gui.DirectGui import DirectFrame, DirectLabel, DirectButton, DGG
from direct.interval.IntervalGlobal import Sequence, Func, LerpPosInterval, Wait
from panda3d.core import TextNode, Vec4

from toontown.toonbase import ToontownGlobals


class DistributedCutsceneSkipButton(DistributedObject):
    """Altis/Python-2 compatible cutscene skip vote control."""

    onScreenPos = (-0.23, 0, 0.06)
    offScreenPos = (1.0, 0, 0.06)

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.moveTrack = None
        self.buttonGui = loader.loadModel('phase_3/models/gui/dialog_box_buttons_gui')

        self.gui = DirectFrame(
            parent=base.a2dBottomRight,
            relief=None,
            pos=self.offScreenPos)

        self.voteLabel = DirectLabel(
            parent=self.gui,
            relief=None,
            text='Votes to skip: 0/0',
            text_align=TextNode.ARight,
            text_font=ToontownGlobals.getSignFont(),
            text_fg=(1.0, 1.0, 1.0, 1.0),
            text_scale=0.055,
            pos=(0.10, 0, -0.015))

        buttonImages = self._getButtonImages()
        buttonKw = dict(
            parent=self.gui,
            text='Skip Cutscene',
            text_font=ToontownGlobals.getSignFont(),
            text_scale=0.050,
            text_pos=(0, -0.012),
            text3_fg=(0.5, 0.5, 0.5, 0.75),
            pos=(-0.16, 0, 0.105),
            command=self.addSkipVote)

        if buttonImages is not None:
            buttonKw.update(
                relief=None,
                image=buttonImages,
                image_scale=(0.92, 1.0, 0.72))
        else:
            # Never hand DirectGui an empty NodePath.  Some Altis resource
            # revisions do not contain the same named button nodes.
            buttonKw.update(
                relief=DGG.RAISED,
                frameSize=(-0.58, 0.58, -0.13, 0.13),
                frameColor=(0.82, 0.72, 0.50, 1.0),
                borderWidth=(0.008, 0.008))

        self.voteButton = DirectButton(**buttonKw)

    def _getButtonImages(self):
        if not self.buttonGui or self.buttonGui.isEmpty():
            return None

        # ChtBx_OKBtn is present in Altis's own PickAToon/Estate UI and is a
        # safer first choice than Clash's/other revisions' QuitBtn nodes.
        nodeSets = (
            ('ChtBx_OKBtn_UP', 'ChtBx_OKBtn_DN', 'ChtBx_OKBtn_Rllvr'),
            ('QuitBtn_UP', 'QuitBtn_DN', 'QuitBtn_RLVR'),
            ('CloseBtn_UP', 'CloseBtn_DN', 'CloseBtn_Rllvr'),
        )
        for names in nodeSets:
            nodes = tuple(self.buttonGui.find('**/%s' % name) for name in names)
            if all(not node.isEmpty() for node in nodes):
                return nodes
        return None

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.moveInInitial()

    def disable(self):
        self.ignoreAll()
        self.clearMoveTrack()
        DistributedObject.disable(self)

    def delete(self):
        self.ignoreAll()
        self.clearMoveTrack()
        if self.voteButton:
            self.voteButton.destroy()
            self.voteButton = None
        if self.voteLabel:
            self.voteLabel.destroy()
            self.voteLabel = None
        if self.gui:
            self.gui.destroy()
            self.gui = None
        if self.buttonGui:
            self.buttonGui.removeNode()
            self.buttonGui = None
        DistributedObject.delete(self)

    def moveInInitial(self):
        self.clearMoveTrack()
        self.moveTrack = Sequence(
            Func(self.gui.show),
            LerpPosInterval(self.gui, 0.45, self.onScreenPos,
                            startPos=self.offScreenPos, blendType='easeInOut'))
        self.moveTrack.start()

    def moveOutEnd(self):
        self.clearMoveTrack()
        self.moveTrack = Sequence(
            LerpPosInterval(self.gui, 0.35, self.offScreenPos,
                            startPos=self.gui.getPos(), blendType='easeInOut'),
            Func(self.gui.hide))
        self.moveTrack.start()

    def clearMoveTrack(self):
        if self.moveTrack:
            try:
                self.moveTrack.finish()
            except:
                pass
            self.moveTrack = None

    def setCutsceneSkip(self):
        messenger.send('skipCutscene')
        self.disableButton()
        self.moveOutEnd()

    def addSkipVote(self):
        self.disableButton()
        self.sendUpdate('requestSkip', [])

    def disableButton(self):
        if self.voteButton:
            self.voteButton['state'] = DGG.DISABLED

    def enableButton(self):
        if self.voteButton:
            self.voteButton['state'] = DGG.NORMAL

    def setVoteSkips(self, voteTotal, playerTotal):
        if voteTotal < 0:
            self.disableButton()
            self.voteButton['text'] = 'Cannot Skip'
            self.voteButton['image_color'] = Vec4(0.3, 0.3, 0.3, 1)
            self.voteLabel['text'] = 'Cutscene cannot be skipped'
            Sequence(Wait(5), Func(self.moveOutEnd)).start()
            return

        self.voteLabel['text'] = 'Votes to skip: %s/%s' % (voteTotal, playerTotal)
        if self.voteButton['state'] != DGG.DISABLED:
            self.enableButton()
