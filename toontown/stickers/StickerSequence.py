from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import Sequence, Parallel, Func, Wait
from direct.interval.LerpInterval import LerpScaleInterval, LerpPosInterval, LerpHprInterval
from direct.interval.ActorInterval import ActorInterval
from pandac.PandaModules import NodePath, Vec3, TransparencyAttrib

from toontown.stickers import StickerGlobals


class StickerSequence(DirectObject):
    """Python 2 port of Clash's Toon, Cog-disguise and dice sticker sequences."""

    def __init__(self, toon, stickerId, modifier=0):
        DirectObject.__init__(self)
        self.toon = toon
        self.stickerId = int(stickerId)
        self.modifier = int(modifier or 0)
        self.parentNode = None
        self.stickerNode = None
        self.stickerTrack = None
        self.toonTrack = None
        self.stickerSfx = None
        self.emotesDisabled = False

    def start(self):
        self.stop()
        if not self.toon:
            return False
        try:
            if self.toon.isEmpty():
                return False
        except:
            pass

        nodePath = StickerGlobals.getStickerNode(self.stickerId, self.modifier)
        if not nodePath:
            return False

        model = loader.loadModel('phase_3.5/models/gui/stickers')
        if not model or model.isEmpty():
            return False
        source = model.find(nodePath)
        if source.isEmpty():
            model.removeNode()
            return False

        self.parentNode = NodePath('sticker-parent-%s' % getattr(self.toon, 'doId', 0))
        self.stickerNode = source.copyTo(self.parentNode)
        model.removeNode()

        self.stickerNode.setBillboardPointEye()
        self.stickerNode.setTransparency(TransparencyAttrib.MAlpha)
        self.stickerNode.setDepthWrite(False)
        self.stickerNode.setPos(0, 0, 0)
        self.stickerNode.setScale(0.001)

        if not self._placeStickerForPresentation():
            self.cleanup()
            return False

        soundPath = StickerGlobals.getStickerSfxPath(self.stickerId)
        if soundPath:
            try:
                self.stickerSfx = loader.loadSfx(soundPath)
            except:
                self.stickerSfx = None

        if self.stickerId == StickerGlobals.DICE_ROLL:
            self.stickerTrack = self._makeDiceStickerTrack()
            self.toonTrack = self._makeDiceToonTrack()
        else:
            self.stickerTrack = self._makeDefaultStickerTrack()
            self.toonTrack = self._makeDefaultToonTrack()

        if not self.toonTrack:
            self.cleanup()
            return False
        self.toonTrack.start()
        return True

    def _isDisguised(self):
        try:
            return bool(self.toon.isDisguised and self.toon.suit)
        except:
            return False

    def _getToonRightHand(self):
        hand = getattr(self.toon, 'rightHand', None)
        if hand and not hand.isEmpty():
            return hand
        try:
            hands = self.toon.getRightHands()
            if hands:
                return hands[0]
        except:
            pass
        return NodePath()

    def _getPresentationParent(self):
        if self.stickerId == StickerGlobals.DICE_ROLL:
            return self.toon
        if self._isDisguised():
            try:
                return self.toon.suit.getRightHand()
            except:
                return NodePath()
        return self._getToonRightHand()

    def _getPresentationOffset(self):
        if self.stickerId == StickerGlobals.DICE_ROLL:
            try:
                height = self.toon.getHeight()
            except:
                height = 4.0
            return Vec3(0.0, 2.0, height / 2.0)
        if self._isDisguised():
            return Vec3(-0.07, 0.3, -1.45)
        return Vec3(0.0, 0.2, 1.0)

    def _placeStickerForPresentation(self):
        parent = self._getPresentationParent()
        if not parent or parent.isEmpty():
            return False
        offset = self._getPresentationOffset()

        if self._isDisguised() and self.stickerId != StickerGlobals.DICE_ROLL:
            self.parentNode.reparentTo(render)
            self.parentNode.setPos(render.getRelativePoint(parent, offset))
        else:
            self.parentNode.reparentTo(parent)
            self.parentNode.setPos(offset)
        return True

    def _parentStickerToWorld(self):
        if not self.parentNode:
            return
        parent = self._getPresentationParent()
        offset = self._getPresentationOffset()
        if parent and not parent.isEmpty() and self._isDisguised() and self.stickerId != StickerGlobals.DICE_ROLL:
            self.parentNode.reparentTo(render)
            self.parentNode.setPosHpr(render.getRelativePoint(parent, offset), Vec3(0, 0, 0))
            return
        try:
            worldPos = self.parentNode.getPos(render)
            self.parentNode.reparentTo(render)
            self.parentNode.setPosHpr(worldPos, Vec3(0, 0, 0))
        except:
            pass

    def _getStickerScale(self):
        scale = StickerGlobals.getStickerScale3d(self.stickerId)
        if isinstance(scale, (tuple, list)):
            return Vec3(1.6 * scale[0], 1.6 * scale[1], 1.6 * scale[2])
        return Vec3(1.6 * scale, 1.6 * scale, 1.6 * scale)

    def _makeDefaultStickerTrack(self):
        stickerScale = self._getStickerScale()
        floatDistance = 0.25 * stickerScale.getZ()
        scaleTrack = Sequence(
            LerpScaleInterval(self.stickerNode, 0.2, stickerScale, blendType='easeIn'),
            Func(self._playStickerSfx),
            LerpScaleInterval(self.stickerNode, 0.05, stickerScale, blendType='easeOut'),
            Wait(4.0),
            LerpScaleInterval(self.stickerNode, 0.05, stickerScale, blendType='easeIn'),
            LerpScaleInterval(self.stickerNode, 0.2, 0.001, blendType='easeOut'),
        )
        posTrack = Sequence(
            LerpPosInterval(self.stickerNode, 1.125, (0, 0, floatDistance), blendType='easeInOut'),
            LerpPosInterval(self.stickerNode, 1.125, (0, 0, 0), blendType='easeInOut'),
            LerpPosInterval(self.stickerNode, 1.125, (0, 0, floatDistance), blendType='easeInOut'),
            LerpPosInterval(self.stickerNode, 1.125, (0, 0, 0), blendType='easeInOut'),
        )
        return Sequence(
            Func(self._parentStickerToWorld),
            Parallel(scaleTrack, posTrack),
            Func(self._cleanupStickerOnly),
        )

    def _makeDiceStickerTrack(self):
        stickerScale = self._getStickerScale()
        floatDistance = 0.175 * stickerScale.getZ()
        scaleTrack = Sequence(
            Func(self._playStickerSfx),
            LerpScaleInterval(self.stickerNode, 0.10, stickerScale, blendType='easeIn'),
            LerpScaleInterval(self.stickerNode, 0.4, stickerScale * 1.15, blendType='easeOut'),
            LerpScaleInterval(self.stickerNode, 0.4, stickerScale, blendType='easeIn'),
            Wait(3.3),
            LerpScaleInterval(self.stickerNode, 0.05, stickerScale, blendType='easeIn'),
            LerpScaleInterval(self.stickerNode, 0.2, 0.001, blendType='easeOut'),
        )
        posTrack = Sequence(
            LerpHprInterval(self.stickerNode, 0.10, Vec3(0, 0, 0), startHpr=Vec3(0, 0, -120), blendType='easeOut'),
            LerpPosInterval(self.stickerNode, 1.125, (0, 0, floatDistance), blendType='easeInOut'),
            LerpPosInterval(self.stickerNode, 1.125, (0, 0, 0), blendType='easeInOut'),
            LerpPosInterval(self.stickerNode, 1.125, (0, 0, floatDistance), blendType='easeInOut'),
            LerpPosInterval(self.stickerNode, 1.125, (0, 0, 0), blendType='easeInOut'),
        )
        return Sequence(
            Func(self._parentStickerToWorld),
            Parallel(scaleTrack, posTrack),
            Func(self._cleanupStickerOnly),
        )

    def _duration(self, actor, anim, fromFrame=None, toFrame=None, fallback=0.5):
        try:
            if fromFrame is None and toFrame is None:
                value = actor.getDuration(anim)
            elif fromFrame is None:
                value = actor.getDuration(anim, toFrame=toFrame)
            else:
                value = actor.getDuration(anim, fromFrame=fromFrame, toFrame=toFrame)
            if value:
                return value
        except:
            pass
        return fallback

    def _makeDefaultToonTrack(self):
        if self._isDisguised():
            suit = self.toon.suit
            firstWait = self._duration(self.toon, 'toss', toFrame=20) / 2.6
            secondWait = self._duration(self.toon, 'toss', fromFrame=21, toFrame=30) / 3.0
            return Sequence(
                Func(self._disableEmotes),
                Parallel(
                    Sequence(
                        ActorInterval(suit, 'sticker', playRate=1.2),
                        Func(suit.loop, 'neutral'),
                    ),
                    Sequence(
                        Wait(firstWait),
                        Func(self.stickerTrack.start),
                        Wait(secondWait),
                        Wait(self._duration(self.toon, 'toss', toFrame=30)),
                    ),
                ),
                Func(self._finishToonAnimation),
            )

        firstDuration = self._duration(self.toon, 'toss', toFrame=20) / 3.0
        secondDuration = self._duration(self.toon, 'toss', fromFrame=21, toFrame=30) / 3.0
        return Sequence(
            Func(self._disableEmotes),
            Func(self.toon.setPlayRate, 3.0, 'toss'),
            Func(self.toon.play, 'toss', None, 0, 20),
            Wait(firstDuration),
            Func(self.stickerTrack.start),
            Func(self.toon.play, 'toss', None, 21, 30),
            Wait(secondDuration),
            Func(self.toon.setPlayRate, -1.0, 'toss'),
            Func(self.toon.play, 'toss', None, 0, 30),
            Wait(self._duration(self.toon, 'toss', toFrame=30)),
            Func(self._finishToonAnimation),
        )

    def _makeDiceToonTrack(self):
        if self._isDisguised():
            return self._makeDefaultToonTrack()

        tossSpeed = 1.45
        midSpeed = 1.33
        returnSpeed = 1.0
        try:
            torso = self.toon.style.torso[0]
        except:
            torso = 'm'

        if torso == 'l':
            tossStart, tossEnd = 36, 46
            midStart, midEnd = 60, 60
            returnEnd = 104
        elif torso == 'm':
            tossStart, tossEnd = 37, 46
            midStart, midEnd = 60, 63
            returnEnd = 104
        else:
            tossStart, tossEnd = 31, 44
            midStart, midEnd = 51, 56
            returnEnd = 104

        return Sequence(
            Func(self._disableEmotes),
            Func(self.toon.setPlayRate, tossSpeed, 'toss'),
            Func(self.toon.play, 'toss', None, tossStart, tossEnd),
            Wait(self._duration(self.toon, 'toss', tossStart, tossEnd) / tossSpeed),
            Func(self.toon.setPlayRate, midSpeed, 'toss'),
            Func(self.toon.play, 'toss', None, midStart, midEnd),
            Wait(self._duration(self.toon, 'toss', midStart, midEnd) / midSpeed),
            Func(self.stickerTrack.start),
            Func(self.toon.setPlayRate, returnSpeed, 'toss'),
            Func(self.toon.play, 'toss', None, midEnd, returnEnd),
            Wait(self._duration(self.toon, 'toss', midEnd, returnEnd) / returnSpeed),
            Func(self._finishToonAnimation),
        )

    def _disableEmotes(self):
        if self.emotesDisabled:
            return
        try:
            from toontown.toon import TTEmote
            TTEmote.globalEmote.disableBody(self.toon, 'sticker')
            self.emotesDisabled = True
        except:
            pass

    def _releaseEmotes(self):
        if not self.emotesDisabled:
            return
        try:
            from toontown.toon import TTEmote
            TTEmote.globalEmote.releaseBody(self.toon, 'sticker')
        except:
            pass
        self.emotesDisabled = False

    def _finishToonAnimation(self):
        try:
            if self._isDisguised():
                self.toon.suit.loop('neutral')
            else:
                self.toon.setPlayRate(1.0, 'toss')
                self.toon.loop('neutral')
        except:
            pass
        self._releaseEmotes()
        self.toonTrack = None

    def _playStickerSfx(self):
        if not self.stickerSfx:
            return
        try:
            base.playSfx(self.stickerSfx, looping=0)
        except:
            try:
                self.stickerSfx.play()
            except:
                pass

    def _cleanupStickerOnly(self):
        if self.stickerNode:
            try:
                self.stickerNode.removeNode()
            except:
                pass
            self.stickerNode = None
        if self.parentNode:
            try:
                self.parentNode.removeNode()
            except:
                pass
            self.parentNode = None
        self.stickerTrack = None

    def stop(self):
        if self.toonTrack:
            try:
                self.toonTrack.pause()
            except:
                pass
            self.toonTrack = None
        if self.stickerTrack:
            try:
                self.stickerTrack.pause()
            except:
                pass
            self.stickerTrack = None
        try:
            if self.toon:
                if self._isDisguised():
                    self.toon.suit.loop('neutral')
                else:
                    self.toon.setPlayRate(1.0, 'toss')
                    self.toon.loop('neutral')
        except:
            pass
        self._releaseEmotes()
        self._cleanupStickerOnly()

    def cleanup(self):
        self.stop()
