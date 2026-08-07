import random
from toontown.battle import MovieUtil
from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.editor.CSEditorEnums import SubEventArgumentType as SEAT
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence
from toontown.building import ElevatorUtils, ElevatorConstants
from direct.interval.IntervalGlobal import *
from panda3d.core import Point2, Point3, LVecBase3f, LVecBase4f, PGButton, TextNode
from toontown.chat.ChatGlobals import CFSpeech, CFTimeout
from toontown.suit.Suit import Suit
from toontown.chat.ChatBalloon import ChatBalloon
from toontown.nametag import NametagGlobals


def _getAnimatedSuitHead(actor):
    head = getattr(actor, 'specialHead', None)
    if head is not None:
        try:
            if not head.isEmpty():
                return head
        except:
            return head
    parts = getattr(actor, 'animatedHeadParts', None) or []
    if parts:
        return parts[0]
    try:
        parts = actor.getAnimatedHeadParts()
        if parts:
            return parts[0]
    except:
        pass
    return None


def _isSuitLike(actor):
    return isinstance(actor, Suit) or (hasattr(actor, 'nametag') and
                                       hasattr(actor, 'hideNametag2d'))


def _configureSuitDialogueNametag(actor):
    if not _isSuitLike(actor):
        return
    try:
        nametag3d = actor.nametag.getNametag3d()
        nametag3d.hideNametag()
        nametag3d.showChat()
        nametag3d.showThought()
        nametag3d.update()
    except:
        pass


def _finishActorDialogue(actor, suppressSuitName=False):
    actor.clearChat()
    if suppressSuitName:
        _configureSuitDialogueNametag(actor)


def _setActorDialogue(actor, message, wantHeadAnim=True, wantSound=True):
    flags = CFTimeout | (CFSpeech if wantSound else 0)
    if _isSuitLike(actor):
        # Project Altis uses the older Suit.setChatAbsolute signature and does
        # not accept Clash's wantHeadAnim/wantSound keyword arguments.
        #
        # Avatar.setChatAbsolute automatically runs a talking head animation,
        # then calls headPart.loop('neutral').  On High Roller that call resets
        # the orbiting ducks to frame zero.  Temporarily hide only his animated
        # head list from Avatar while setting chat; the nametag and voice still
        # work, but no dialogue interval can interrupt or rewind the duck loop.
        preserveDuckLoop = getattr(
            actor, '_preserveHighRollerDuckLoopDuringDialogue', False)
        originalAnimatedHeadParts = None
        if preserveDuckLoop:
            originalAnimatedHeadParts = getattr(actor, 'animatedHeadParts', None)
            if originalAnimatedHeadParts is not None:
                actor.animatedHeadParts = []
        try:
            actor.setChatAbsolute(message, flags)
        finally:
            if originalAnimatedHeadParts is not None:
                actor.animatedHeadParts = originalAnimatedHeadParts

        if not wantHeadAnim and not preserveDuckLoop:
            try:
                for headPart in actor.getHeadParts():
                    headPart.loop('neutral')
            except:
                pass
    else:
        actor.setChatAbsolute(message, flags)


DETACHED_DIALOGUE_MESSAGES = (
    'The Spinning Wheel...',
    "Welcome back to the Tooniverffe'ff favorite ffhow!",
    # Pacesetter: Altis can lose this native Nametag3d bubble after the
    # "Hold on a sec..." camera transition.  Keep the original dialogue and
    # voice, but render the standard Cog balloon through the proven projected
    # compatibility path.
    'FINALLY! Entertainment at last! I was feeling myself rust!',
)

# Per-line screen-space offsets for the two projected CTSC bubbles.
# Positive X moves right; positive Z moves upward.
DETACHED_DIALOGUE_SCREEN_OFFSETS = {
    # Major Player: reference-shot placement.
    'The Spinning Wheel...': (0.55, 0.40),
    # High Roller keeps the previously approved placement.
    "Welcome back to the Tooniverffe'ff favorite ffhow!": (0.82, 0.18),
    # Pacesetter is near the center of this shot; keep the bubble centered over
    # his projected position instead of applying High Roller's large X offset.
    'FINALLY! Entertainment at last! I was feeling myself rust!': (0.42, -0.08),
}

# Per-line size multipliers for projected CTSC bubbles.
# High Roller's bubble remains at the default size.
DETACHED_DIALOGUE_SCREEN_SCALES = {
    'The Spinning Wheel...': 0.75,
    # Pacesetter's long line needs a smaller balloon than the generic projected
    # Cog bubble so it stays clear of his body and the right side of the shot.
    'FINALLY! Entertainment at last! I was feeling myself rust!': 0.70,
}


class _ProjectedDialogueBubble(object):
    """Draw an authored Cog speech bubble independently of Altis nametags.

    The two affected CTSC shots move or bind the normal Nametag3d while Altis
    is also rebuilding it.  That leaves the chat text alive but the rendered
    balloon missing.  Use Toontown's real ChatBalloon model under aspect2d and
    project the authored 3-D attachment point every frame.  This does not touch
    the Cog's head, hat, nameplate, or animation controls.
    """

    def __init__(self, actor, message, source, offset, authoredScale):
        self.actor = actor
        self.source = source
        self.offset = offset
        self.screenXOffset, self.screenZOffset = \
            DETACHED_DIALOGUE_SCREEN_OFFSETS.get(message, (0.82, 0.18))
        self.root = aspect2d.attachNewNode(
            'highRollerProjectedDialogue-%s' % id(self))
        self.root.setDepthTest(False)
        self.root.setDepthWrite(False)
        self.root.setBin('fixed', 200)

        group = actor.nametag
        textNode = TextNode('highRollerProjectedDialogueText')
        textNode.setText(message)
        textNode.setAlign(TextNode.ACenter)
        textNode.setFont(group.getChatFont())
        try:
            textNode.setWordwrap(group.getChatWordWrap())
        except:
            textNode.setWordwrap(10)
        try:
            textNode.setGlyphScale(ChatBalloon.TEXT_GLYPH_SCALE)
            textNode.setGlyphShift(ChatBalloon.TEXT_GLYPH_SHIFT)
        except:
            pass

        chatColors = group.getChatColor()
        foreground, background = chatColors[PGButton.SInactive]
        # Use the normal Cog speech balloon with its pointer/tail.
        # ToonBase assigns chatbox_noarrow.bam to the 2-D model, which is why
        # the projected CTSC bubble previously looked like a plain rectangle.
        model = NametagGlobals.chatBalloon3dModel
        modelWidth = NametagGlobals.chatBalloon3dWidth
        modelHeight = NametagGlobals.chatBalloon3dHeight
        if model is None:
            model = NametagGlobals.chatBalloon2dModel
            modelWidth = NametagGlobals.chatBalloon2dWidth
            modelHeight = NametagGlobals.chatBalloon2dHeight

        self.balloon = ChatBalloon(
            model, modelWidth, modelHeight, textNode,
            foreground=foreground, background=background,
            reversed=False, button=None)
        self.balloon.reparentTo(self.root)
        self.balloon.setDepthTest(False)
        self.balloon.setDepthWrite(False)
        self.balloon.setBin('fixed', 201)

        # Match the normal Nametag2d centering logic so the projected point is
        # the visual centre of the balloon, not its lower-left model origin.
        try:
            left, right, bottom, top = textNode.getFrameActual()
            center = self.root.getRelativePoint(
                self.balloon.textNodePath,
                ((left + right) / 2.0, 0, (bottom + top) / 2.0))
            self.balloon.setPos(self.balloon, -center)
        except:
            pass

        # The original values are world-space Nametag3d scales and cannot be
        # applied directly under aspect2d.  Preserve their relative emphasis
        # while keeping both special bubbles within the screen.
        displayScale = 0.19 + min(max(float(authoredScale), 1.0), 4.0) * 0.0125
        displayScale *= DETACHED_DIALOGUE_SCREEN_SCALES.get(message, 1.0)
        self.root.setScale(displayScale)
        self.update()

    def update(self):
        if self.root is None or self.root.isEmpty():
            return
        projected = Point2()
        try:
            worldPoint = render.getRelativePoint(self.source, self.offset)
            cameraPoint = base.cam.getRelativePoint(render, worldPoint)
            visible = cameraPoint.getY() > 0 and base.camLens.project(
                cameraPoint, projected)
        except:
            visible = False

        if visible:
            aspect = base.getAspectRatio()
            x = projected.getX() * aspect + self.screenXOffset
            z = projected.getY() + self.screenZOffset
            x = max(-aspect + 0.28, min(aspect - 0.28, x))
            z = max(-0.72, min(0.90, z))
            self.root.setPos(x, 0, z)
        else:
            # A camera cut can occur on the same frame as the dialogue event.
            # Keep the balloon visible until the source projects again.
            self.root.setPos(self.screenXOffset, 0,
                             min(0.90, 0.58 + self.screenZOffset))
        self.root.show()

    def cleanup(self):
        if self.balloon is not None:
            try:
                self.balloon.removeNode()
            except:
                pass
            self.balloon = None
        if self.root is not None:
            try:
                self.root.removeNode()
            except:
                pass
            self.root = None


def _hideNativeActorChat(actor):
    # The projected balloon is the visible copy.  Keep setChatAbsolute only for
    # the original Cog voice and talking animation.
    for getter in ('getNametag3d', 'getNametag2d'):
        try:
            nametag = getattr(actor.nametag, getter)()
            nametag.hideChat()
            nametag.hideThought()
            nametag.update()
        except:
            pass


def _startProjectedDialogueBubble(holder, actor, message, source, offset, scale):
    try:
        holder[0] = _ProjectedDialogueBubble(
            actor, message, source, offset, scale)
        print('[HighRoller CTSC] Visible projected speech bubble: %s' % message)
    except Exception as error:
        holder[0] = None
        print('[HighRoller CTSC] Projected speech bubble failed: %s' % error)


def _updateProjectedDialogueBubble(value, holder):
    bubble = holder[0]
    if bubble is not None:
        bubble.update()


def _stopProjectedDialogueBubble(holder):
    bubble = holder[0]
    if bubble is not None:
        bubble.cleanup()
    holder[0] = None

def _syncNametagToHead(value, nametag, head, offset):
    """Follow an animated head without inheriting its model scale."""
    try:
        parent = nametag.getParent()
        nametag.setPos(parent.getRelativePoint(head, offset))
    except:
        pass


def _forceActorDialogueVisible(actor):
    """Show the chat component without restoring the Cog name label.

    Older Altis Suit actors can leave the wrapper NodePath stashed even after
    ``show()`` is called.  Clash dialogue events expect the wrapper and the
    underlying Nametag3d chat component to be active on the following frame.
    Explicitly unstash/show both layers so isolated bubbles cannot disappear.
    """
    try:
        actor.showNametag3d()
    except:
        pass
    try:
        actor.nametag3d.unstash()
    except:
        pass
    try:
        actor.nametag3d.show()
    except:
        pass
    _configureSuitDialogueNametag(actor)
    try:
        actor.nametag3d.unstash()
        actor.nametag3d.show()
    except:
        pass


def _showSuitDialogueNametag(actor):
    _forceActorDialogueVisible(actor)


def _bindNametagToHead(nametag, head, offset, scale):
    """Follow an animated head while keeping a normal world-space bubble size."""
    try:
        nametag.reparentTo(head)
        nametag.setPos(offset)
        nametag.setHpr(0, 0, 0)
        nametag.setScale(render, scale, scale, scale)
    except:
        # Preserve a usable fallback if an older Panda build rejects the
        # other-relative setScale overload.
        try:
            nametag.setScale(scale)
        except:
            pass


def _restoreNametagTransform(nametag, parent, transform):
    try:
        nametag.reparentTo(parent)
        nametag.setTransform(transform)
    except:
        pass

@cutsceneSequence(name='Actor: Dialogue', enum=EDE.actorDialogue)
def seq_actorDialogue(messageIndex=0, actorIndex=0, delay=0.0, duration=3.0, moveNametag=False, xyz=(0, 0, 0), scale=1.0, hideNametag=False, wantHeadAnim=True, wantSound=True, disable=False, bindToHead=False, cutsceneDict=None):
    if disable:
        return Sequence()
    actor = cutsceneDict['actors'][actorIndex]
    if not actor:
        return Sequence()

    message = cutsceneDict['messages'][messageIndex]
    hideSuitNametag = cutsceneDict.get('suppressSuitNametags', False)

    # These two authored shots lose Altis's shared nametag node.  Do not touch
    # the Cog head or its normal talking animation; display a temporary copy of
    # the standard 3D speech balloon instead.
    if _isSuitLike(actor) and message in DETACHED_DIALOGUE_MESSAGES:
        source = _getAnimatedSuitHead(actor) if bindToHead else actor
        if source is None:
            source = actor
        offset = LVecBase3f(*xyz) if moveNametag else actor.nametag3d.getPos(source)
        holder = [None]
        return Sequence(
            Wait(delay),
            Func(_setActorDialogue, actor, message, wantHeadAnim, wantSound),
            Func(_hideNativeActorChat, actor),
            Func(_startProjectedDialogueBubble,
                 holder, actor, message, source, offset, scale),
            Parallel(
                Wait(duration),
                LerpFunc(
                    _updateProjectedDialogueBubble,
                    fromData=0.0,
                    toData=1.0,
                    duration=duration,
                    extraArgs=[holder])),
            Func(_stopProjectedDialogueBubble, holder),
            Func(_finishActorDialogue, actor, hideSuitNametag))

    nametag = actor.nametag3d
    track = Sequence(Wait(delay))
    originalParent = nametag.getParent()
    originalTransform = nametag.getTransform()
    originalScale = nametag.getScale()
    originalPos = nametag.getPos()
    head = _getAnimatedSuitHead(actor)
    followHead = bool(bindToHead and head is not None)

    if followHead:
        # Use the CTSC's authored head-local offset, but normalize the bubble in
        # render space.  This is the Major Player "Spinning Wheel" case: direct
        # inheritance from his animated head makes the bubble effectively zero
        # sized on Project Altis.
        offset = LVecBase3f(*xyz) if moveNametag else nametag.getPos(head)
        track.append(Func(_bindNametagToHead, nametag, head, offset, scale))
    elif moveNametag:
        track.append(Func(nametag.setPos, LVecBase3f(*xyz)))

    chatFunc = Func(
        _setActorDialogue,
        actor,
        message,
        wantHeadAnim,
        wantSound)

    # Reassert visibility over the first few rendered frames.  Altis updates a
    # Suit's Nametag3d after setChatAbsolute(), and that late update previously
    # hid the Major Player and High Roller bubbles again.
    visibilityPulse = Sequence(
        Func(_forceActorDialogueVisible, actor)
        if hideSuitNametag else Func(nametag.show),
        Wait(0.01),
        Func(_forceActorDialogueVisible, actor)
        if hideSuitNametag else Func(nametag.show),
        Wait(0.09),
        Func(_forceActorDialogueVisible, actor)
        if hideSuitNametag else Func(nametag.show))

    track = Sequence(
        track,
        Sequence() if followHead else Func(nametag.setScale, scale),
        Func(nametag.unstash),
        Func(nametag.show),
        chatFunc,
        Parallel(Wait(duration), visibilityPulse),
        Func(_finishActorDialogue, actor, hideSuitNametag))

    if followHead:
        track.append(Func(
            _restoreNametagTransform,
            nametag,
            originalParent,
            originalTransform))
    else:
        track.append(Func(nametag.setScale, originalScale))
        track.append(Func(nametag.setPos, originalPos))
    if hideNametag:
        track.append(Func(nametag.hide))
    return track

@cutsceneSequence(name='Actor: Iterative Dialogue', enum=EDE.actorDialogueIt)
def seq_actorDialogueIt(messageIndex=0, actorIndex=0, delay=0.0, duration=3.0, moveNametag=False, xyz=(0, 0, 0), scale=1.0, hideNametag=False, disable=False, cutsceneDict=None):
    """
    Condenses dialogue related things into one sequence.
    Can define a duration, move the nametag (speech bubble), and hide the nametag afterwards.
    If the nametag is moved, it will move back to the original position after the dialogue duration.
    """
    if disable:
        return Sequence()
    actor = cutsceneDict['actors'][actorIndex]
    nametag = actor.nametag3d
    track = Sequence(Wait(delay))
    originalScale = nametag.getScale()
    if moveNametag:
        originalPos = nametag.getPos()
        track.append(Func(nametag.setPos, LVecBase3f(*xyz)))
    hideSuitNametag = cutsceneDict.get('suppressSuitNametags', False)
    track = Sequence(track, Func(nametag.setScale, scale), Func(nametag.unstash), Func(nametag.show), Func(actor.setChatIterative, cutsceneDict['messages'][messageIndex], CFSpeech | CFTimeout), Func(_forceActorDialogueVisible, actor) if hideSuitNametag else Func(nametag.show), Wait(duration), Func(_finishActorDialogue, actor, hideSuitNametag), Func(nametag.setScale, originalScale))
    if hideNametag:
        track.append(Func(nametag.hide))
    if moveNametag:
        track.append(Func(nametag.setPos, originalPos))
    return track

@cutsceneSequence(name='Actor: Show Nametag', enum=EDE.showNametag)
def seq_actorShowNametag(actorIndex=0, cutsceneDict=None):
    actor = cutsceneDict['actors'][actorIndex]
    if not actor:
        return Sequence()
    if _isSuitLike(actor):
        return Sequence(Func(_forceActorDialogueVisible, actor))
    return Sequence(Func(actor.nametag3d.unstash), Func(actor.nametag3d.show))

@cutsceneSequence(name='Actor: Hide Nametag', enum=EDE.hideNametag)
def seq_actorHideNametag(actorIndex=0, cutsceneDict=None):
    actor = cutsceneDict['actors'][actorIndex]
    if not actor:
        return Sequence()
    return Sequence(Func(actor.nametag3d.hide))

@cutsceneSequence(name='Actor: Chat', enum=EDE.actorChat)
def seq_actorSays(messageIndex=0, actorIndex=0, delay=0.0, disable=False, cutsceneDict=None):
    if disable:
        return Sequence()
    actor = cutsceneDict['actors'][actorIndex]
    if not actor:
        return Sequence()
    return Sequence(
        Wait(delay),
        Func(actor.setChatAbsolute,
             cutsceneDict['messages'][messageIndex], CFSpeech | CFTimeout),
        Func(_forceActorDialogueVisible, actor)
        if _isSuitLike(actor) else Func(actor.nametag3d.show))

@cutsceneSequence(name='Actor: Chat Off', enum=EDE.actorShutUp)
def seq_actorUnsays(actorIndex=0, delay=0.0, cutsceneDict=None):
    return Sequence(Wait(delay), Func(cutsceneDict['actors'][actorIndex].clearChat))

@cutsceneSequence(name='Time Sleep', enum=EDE.timeSleep)
def seq_wait(time=0.0, cutsceneDict=None):
    return Sequence(Wait(time))

@cutsceneSequence(name='Actor: Move Sequence', enum=EDE.moveActor)
def seq_moveActor(actorIndex=0, duration=0.0, delay=0.0, blendType='easeInOut', xyz=(0, 0, 0), useStartPos=0, startPos=(0, 0, 0), cutsceneDict=None):
    if not useStartPos:
        startPos = None
    else:
        startPos = LVecBase3f(*startPos)
    actorDo = cutsceneDict['actors'][actorIndex]
    return Sequence(Wait(delay), LerpPosInterval(nodePath=actorDo, pos=LVecBase3f(*xyz), duration=duration, startPos=startPos, blendType=blendType))

@cutsceneSequence(name='Actor: Turn Sequence', enum=EDE.turnActor)
def seq_turnActor(actorIndex=0, duration=0.0, delay=0.0, blendType='easeInOut', hpr=(0, 0, 0), useStartHpr=0, startHpr=(0, 0, 0), cutsceneDict=None):
    if not useStartHpr:
        startHpr = None
    else:
        startHpr = LVecBase3f(*startHpr)
    actorDo = cutsceneDict['actors'][actorIndex]
    return Sequence(Wait(delay), LerpHprInterval(nodePath=actorDo, hpr=LVecBase3f(*hpr), duration=duration, startHpr=startHpr, blendType=blendType))

@cutsceneSequence(name='Node: Set Pos/HPR/Scale', enum=EDE.nodePosHprScale)
def seq_nodeSetPosHprScale(nodeIndex=0, delay=0, pos=(0, 0, 0), hpr=(0, 0, 0), scale=(1, 1, 1), cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    if node in (render, hidden):
        print('WARNING! Cutscene tried to move render or hidden!')
        return Sequence()
    return Sequence(Wait(delay), Func(node.setPos, LVecBase3f(*pos)), Func(node.setHpr, LVecBase3f(*hpr)), Func(node.setScale, LVecBase3f(*scale)))

@cutsceneSequence(name='Node: Show', enum=EDE.showNode)
def seq_showNode(nodeIndex=0, cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    return Sequence(Func(node.show))

@cutsceneSequence(name='Node: Hide', enum=EDE.hideNode)
def seq_hideNode(nodeIndex=0, cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    return Sequence(Func(node.hide))

@cutsceneSequence(name='Node: Reparent to Node', enum=EDE.reparentNode)
def seq_reparentNode(nodeIndex=0, targetIndex=0, wrt=0, disable=True, cutsceneDict=None):
    if disable:
        return Sequence()
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    if node in (render, hidden):
        print('WARNING! Cutscene tried to reparent render or hidden!')
        return Sequence()
    target = cutsceneDict['nodes'][targetIndex]
    if target is node:
        return Sequence()
    if target is None:
        return Sequence()
    if wrt:
        return Func(node.wrtReparentTo, target)
    else:
        return Func(node.reparentTo, target)

@cutsceneSequence(name='Node: Move Sequence', enum=EDE.moveNode)
def seq_moveNode(nodeIndex=0, delay=0, duration=0.0, pos=(0, 0, 0), startPos=(0, 0, 0), useStartPos=0, hpr=(0, 0, 0), startHpr=(0, 0, 0), useStartHpr=0, blendType='easeInOut', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    if node in (render, hidden):
        print('WARNING! Cutscene tried to move render or hidden!')
        return Sequence()
    if not useStartPos:
        startPos = None
    else:
        startPos = LVecBase3f(*startPos)
    if not useStartHpr:
        startHpr = None
    else:
        startHpr = LVecBase3f(*startHpr)
    return Sequence(Wait(delay), LerpPosHprInterval(node, duration=duration, pos=LVecBase3f(*pos), startPos=startPos, hpr=LVecBase3f(*hpr), startHpr=startHpr, blendType=blendType))

@cutsceneSequence(name='Node: Pos Relative To Other', enum=EDE.posRelativeToOther)
def seq_posRelativeToOtherNode(nodeIndex=0, delay=0, duration=0.0, otherNodeIndex=0, pos=(0, 0, 0), startPos=(0, 0, 0), useStartPos=0, blendType='easeInOut', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    otherNode = cutsceneDict['nodes'][otherNodeIndex]
    if not otherNode:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    if node in (render, hidden):
        print('WARNING! Cutscene tried to move render or hidden!')
        return Sequence()
    if not useStartPos:
        startPos = None
    else:
        startPos = LVecBase3f(*startPos)
    return Sequence(Wait(delay), LerpPosInterval(node, duration=duration, pos=LVecBase3f(*pos), startPos=startPos, other=otherNode, blendType=blendType))

@cutsceneSequence(name='Node: Rotate Sequence', enum=EDE.rotateNode)
def seq_rotateNode(nodeIndex=0, delay=0, duration=0.0, hpr=(0, 0, 0), startHpr=(0, 0, 0), useStartHpr=0, blendType='easeInOut', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    if node in (render, hidden):
        print('WARNING! Cutscene tried to rotate render or hidden!')
        return Sequence()
    if not useStartHpr:
        startHpr = None
    else:
        startHpr = LVecBase3f(*startHpr)
    return Sequence(Wait(delay), LerpHprInterval(node, duration=duration, hpr=LVecBase3f(*hpr), startHpr=startHpr, blendType=blendType))

@cutsceneSequence(name='Node: Scale Sequence', enum=EDE.scaleNode)
def seq_scaleNode(nodeIndex=0, delay=0, duration=0, scale=(1, 1, 1), startScale=(1, 1, 1), useStartScale=0, blendType='easeInOut', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    if node in (render, hidden):
        print('WARNING! Cutscene tried to scale render or hidden!')
        return Sequence()
    if not useStartScale:
        startScale = None
    if scale:
        scale = list(scale)
        scale[0] = max(scale[0], 0.001)
        scale[1] = max(scale[1], 0.001)
        scale[2] = max(scale[2], 0.001)
        scale = tuple(scale)
    if startScale:
        startScale = list(startScale)
        startScale[0] = max(startScale[0], 0.001)
        startScale[1] = max(startScale[1], 0.001)
        startScale[2] = max(startScale[2], 0.001)
        startScale = tuple(startScale)
    return Sequence(Wait(delay), LerpScaleInterval(node, duration=duration, scale=scale, startScale=startScale, blendType=blendType))

@cutsceneSequence(name='Node: Color Scale Sequence', enum=EDE.colorScaleNode)
def seq_colorScaleNode(nodeIndex=0, delay=0, duration=0, colorScale=(1, 1, 1, 1), startColorScale=(1, 1, 1, 1), useStartColorScale=0, blendType='easeInOut', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    if not useStartColorScale:
        startColorScale = None
    if colorScale:
        colorScale = LVecBase4f(*colorScale)
    if startColorScale:
        startColorScale = LVecBase4f(*startColorScale)
    return Sequence(Wait(delay), LerpColorScaleInterval(node, duration=duration, colorScale=colorScale, startColorScale=startColorScale, blendType=blendType))

@cutsceneSequence(name='Node: Alpha Scale Sequence', enum=EDE.alphaScaleNode)
def seq_alphaScaleNode(nodeIndex=0, delay=0, duration=0, alphaScale=1, startAlphaScale=1, blendType='easeInOut', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    return Sequence(Wait(delay), LerpFunctionInterval(node.setAlphaScale, duration=duration, fromData=startAlphaScale, toData=alphaScale, blendType=blendType))

@cutsceneSequence(name='Node: Color Sequence', enum=EDE.colorNode)
def seq_colorNode(nodeIndex=0, delay=0, duration=0, color=(1, 1, 1, 1), startColor=(1, 1, 1, 1), useStartColor=0, blendType='easeInOut', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()
    if not useStartColor:
        startColorScale = None
    if color:
        colorScale = LVecBase4f(*color)
    if startColor:
        startColor = LVecBase4f(*startColor)
    return Sequence(Wait(delay), LerpColorInterval(node, duration=duration, color=color, startColor=startColor, blendType=blendType))

@cutsceneSequence(name='Function: Call', enum=EDE.functionCall)
def seq_functionCall(functionIndex=0, delay=0, disable=True, hasArgument=False, argumentIndex=0, returnsInterval=False, cutsceneDict=None):
    if disable:
        return Sequence()
    function = cutsceneDict['functions'][functionIndex]
    if not function:
        return Sequence()
    if hasArgument:
        arguments = cutsceneDict['arguments'][argumentIndex]
        if not isinstance(arguments, list):
            arguments = [arguments]
    else:
        arguments = []
    track = Sequence(Wait(delay))
    if returnsInterval:
        track.append(function(*arguments))
    else:
        track.append(Func(function, *arguments))
    return track

@cutsceneSequence(name='Function: Lerp', enum=EDE.functionLerp)
def seq_functionLerp(functionIndex=0, delay=0, disable=True, hasExtraArg=False, argumentIndex=0, fromData=0, toData=1, duration=0, blendType='easeInOut', cutsceneDict=None):
    if disable:
        return Sequence()
    function = cutsceneDict['functions'][functionIndex]
    if not function:
        return Sequence()
    if hasExtraArg:
        arguments = cutsceneDict['arguments'][argumentIndex]
        if not isinstance(arguments, list):
            arguments = [arguments]
    else:
        arguments = []
    return Sequence(Wait(delay), LerpFunc(function, duration=duration, fromData=fromData, toData=toData, blendType=blendType, extraArgs=arguments))

@cutsceneSequence(name='Elevator Close', enum=EDE.closeElev)
def seq_closeElev(elevatorModelIndex=0, cutsceneDict=None):
    bem = cutsceneDict['elevators'][elevatorModelIndex]
    retParallel = Parallel(ElevatorUtils.getCloseInterval(None, bem.find('**/left_door'), bem.find('**/right_door'), None, None, ElevatorConstants.ELEVATOR_DERRICK_MAN))
    return retParallel

@cutsceneSequence(name='Elevator Open', enum=EDE.openElev)
def seq_openElev(elevatorModelIndex=0, cutsceneDict=None):
    bem = cutsceneDict['elevators'][elevatorModelIndex]
    retParallel = Parallel(ElevatorUtils.getOpenInterval(None, bem.find('**/left_door'), bem.find('**/right_door'), None, None, ElevatorConstants.ELEVATOR_DERRICK_MAN))
    return retParallel

@cutsceneSequence(name='Node: Set clear Color Scale', enum=EDE.setClearColorScale)
def seq_setClearColorScale(nodeIndex=0, delay=0, setClear=True, cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    if setClear:
        return Sequence(Wait(delay), Func(node.setColorScaleOff, 1))
    else:
        return Sequence(Wait(delay), Func(node.setColorScaleOff, 0))

@cutsceneSequence(name='Create Explosion', enum=EDE.createExplosion)
def seq_createExplosion(nodeIndex=0, scale=1, cutsceneDict=None):
    parent = cutsceneDict['nodes'][nodeIndex]
    if not parent:
        return Sequence()
    toonPlacerNode = NodePath('toonPlacerNode')
    toonPlacerNode.reparentTo(parent)
    toonPlacerNode.setY(-5)
    toonPos = toonPlacerNode.getPos(render)
    toonPlacerNode.removeNode()
    point = Point3(*toonPos)
    point.setZ(point.getZ() + parent.getHeight() + 1)
    return MovieUtil.createKapowExplosionTrack(render, explosionPoint=point, scale=scale)

@cutsceneSequence(name='Node: Jiggle Vicariously', enum=EDE.jiggleNode)
def seq_jigglejiggleji(nodeIndex=0, delay=0.0, duration=1.0, startJig=0.0, endJig=5.0, offset=(0, 0, 0), blendType='easeInOut', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if not node:
        return Sequence()
    if node is camera and (not cutsceneDict['affectsCamera']):
        return Sequence()

    def performJiggle(t):
        x, y, z = offset
        delta = lerp(startJig, endJig, t)
        xx = (random.random() * 2 - 1) * delta
        yy = (random.random() * 2 - 1) * delta
        zz = (random.random() * 2 - 1) * delta
        node.setPos(x + xx, y + yy, z + zz)
    return Sequence(Wait(delay), LerpFunctionInterval(function=performJiggle, duration=duration, blendType=blendType))

@cutsceneSequence(name='Node: Scale List', enum=EDE.scaleNodeList)
def seq_scaleNodeList(nodeIndices=(), delay=0, duration=0.0,
                      scale=(1, 1, 1), startScale=(1, 1, 1),
                      useStartScale=0, blendType='easeInOut',
                      cutsceneDict=None, **kwargs):
    """Scale several nodes in parallel (enum retained but absent upstream)."""
    track = Parallel()
    for nodeIndex in nodeIndices:
        track.append(seq_scaleNode(
            nodeIndex=nodeIndex,
            delay=delay,
            duration=duration,
            scale=scale,
            startScale=startScale,
            useStartScale=useStartScale,
            blendType=blendType,
            cutsceneDict=cutsceneDict))
    return track
