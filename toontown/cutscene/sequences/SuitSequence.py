from direct.showbase.PythonUtil import lerp
from toontown.battle import BattleProps, MovieUtil
from toontown.battle.BattleProps import globalPropPool
from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.editor.CSEditorEnums import SubEventArgumentType as SEAT
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence, getUniqueCutsceneId
from toontown.cutscene.CutsceneSequenceHelpers import getHprBetweenPoints, NodePathWithState
from panda3d.core import Point3, LVecBase3f, LVecBase4f
from toontown.cutscene.ResolvedActorInterval import (
    ResolvedActorInterval, ResolvedLerpAnimInterval,
    getControlMetadata, resolveControl)
from toontown.cutscene.AltisCutsceneCompat import (
    applySuitVisualEffect, unapplySuitVisualEffect)
from direct.interval.IntervalGlobal import *
from toontown.effects import DustCloud
'\nMethods to help generate positions/etc for sequences.\n'


def _getSuitHeadActor(suit):
    """Return Clash's animated head actor from either source layout."""
    if not suit:
        return None
    head = getattr(suit, 'specialHead', None)
    if head is not None:
        try:
            if not head.isEmpty():
                return head
        except:
            return head
    parts = getattr(suit, 'animatedHeadParts', None) or []
    if parts:
        return parts[0]
    try:
        parts = suit.getAnimatedHeadParts()
        if parts:
            return parts[0]
    except:
        pass
    return None


SUIT_BODY_PART = 'modelRoot'


def _queryActorAnimation(actor, anim):
    control, duration, frames, frameRate = resolveControl(
        actor, anim, SUIT_BODY_PART,
        label='%s animation %r' % (actor.getName(), anim))
    return control, duration, frames


def _getCachedControl(cutsceneDict, cacheName, suitIndex, anim):
    if cutsceneDict is None or suitIndex is None:
        return None
    caches = cutsceneDict.get(cacheName, ())
    if suitIndex < 0 or suitIndex >= len(caches):
        return None
    return caches[suitIndex].get(anim)


def _controlMetadata(control, label):
    duration, frames, frameRate = getControlMetadata(control, label)
    return control, duration, frames


def _loopResolvedControl(control, restart=1, startFrame=None, endFrame=None):
    if startFrame is None:
        control.loop(restart)
    elif endFrame is None:
        control.loop(restart, startFrame, control.getNumFrames() - 1)
    else:
        control.loop(restart, startFrame, endFrame)


def _playResolvedControl(control, startFrame=None, endFrame=None):
    if startFrame is None:
        control.play()
    elif endFrame is None:
        control.play(startFrame, control.getNumFrames() - 1)
    else:
        control.play(startFrame, endFrame)


def _pingpongResolvedControl(control, restart=1, startFrame=0, endFrame=None):
    if endFrame is None:
        endFrame = control.getNumFrames() - 1
    control.pingpong(restart, startFrame, endFrame)


def _stopResolvedControls(controls):
    for control in controls:
        if control is not None:
            control.stop()


# Keep the original Actor-facing helpers for CTSC events outside the High
# Roller intro.  The High Roller handlers below use cached controls directly.
def _loopSuitAnimation(suit, anim):
    suit.loop(anim, 1, SUIT_BODY_PART)


def _playSuitAnimation(suit, anim, startFrame, endFrame):
    suit.play(anim, SUIT_BODY_PART, startFrame, endFrame)


def _pingpongSuitAnimation(suit, anim, restart, startFrame, endFrame):
    suit.pingpong(anim, restart, SUIT_BODY_PART, startFrame, endFrame)


def _stopSuitAnimations(suit):
    suit.stop(None, SUIT_BODY_PART)


def _requireActorAnimation(actor, anim, label, cutsceneDict=None,
                           suitIndex=None, cacheName='suitAnimationControls'):
    if actor is None or not anim:
        return None, None, None

    control = _getCachedControl(
        cutsceneDict, cacheName, suitIndex, anim)
    firstError = None
    if control is not None:
        try:
            return _controlMetadata(control, '%s %r' % (label, anim))
        except Exception as error:
            firstError = error

    try:
        control, duration, frames = _queryActorAnimation(actor, anim)
    except Exception as error:
        control = duration = frames = None
        firstError = error

    if control is None or duration is None or frames is None or frames <= 0:
        # Rebind only the requested body alias from the provider's exact map.
        animPath = None
        if cutsceneDict is not None and suitIndex is not None:
            maps = cutsceneDict.get('suitAnimationMaps', ())
            if suitIndex < len(maps):
                animPath = maps[suitIndex].get(anim)
        if animPath:
            try:
                actor.loadAnims({anim: animPath}, SUIT_BODY_PART)
                control, duration, frames = _queryActorAnimation(actor, anim)
            except Exception as error:
                firstError = error

    if control is None or duration is None or frames is None or frames <= 0:
        raise RuntimeError(
            '%s animation %r is not resolved '
            '(control=%r duration=%r frames=%r error=%r)' %
            (label, anim, control, duration, frames, firstError))
    return control, duration, frames

def _configureSuitNametag(suit, visible=False):
    try:
        suit.hideNametag2d()
    except:
        pass
    try:
        nametag3d = suit.nametag.getNametag3d()
        nametag3d.hideNametag()
        nametag3d.showChat()
        nametag3d.showThought()
        nametag3d.update()
    except:
        pass
    try:
        if visible:
            suit.nametag3d.show()
        else:
            suit.nametag3d.hide()
    except:
        pass


def _attachCutscenePropeller(suit):
    try:
        head = suit.find('**/to_head')
        if head.isEmpty():
            head = suit.find('**/joint_head')
        if suit.prop and not head.isEmpty():
            suit.prop.reparentTo(head)
            suit.prop.setPosHpr(0, 0, 0, 0, 0, 0)
            suit.prop.setScale(1)
            suit.prop.clearColorScale()
            suit.prop.show()
    except:
        pass

def createSuitMoveIval(suit, destPos, duration, gravityMult=0.4):
    """
    Creates a sequence which moves the suit using propeller in a projectile arc.
    """
    dur = suit.getDuration('landing')
    fr = suit.getFrameRate('landing')
    landingDur = dur
    totalDur = duration
    animTimeInAir = totalDur - dur
    flyingDur = animTimeInAir
    moveIval = Sequence(Func(suit.pose, 'landing', 0), ProjectileInterval(suit, duration=flyingDur, endPos=destPos, gravityMult=gravityMult), ActorInterval(suit, 'landing'))
    if suit.prop is None:
        suit.prop = BattleProps.globalPropPool.getProp('propeller')
    if suit.propInSound is None:
        suit.propInSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_in.ogg')
    if suit.propOutSound is None:
        suit.propOutSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_propeller_out.ogg')
    propDur = suit.prop.getDuration('propeller')
    lastSpinFrame = 8
    fr = suit.prop.getFrameRate('propeller')
    spinTime = lastSpinFrame / fr
    openTime = (lastSpinFrame + 1) / fr
    propTrack = Parallel(SoundInterval(suit.propInSound, duration=flyingDur, node=suit), Sequence(ActorInterval(suit.prop, 'propeller', constrainedLoop=1, duration=flyingDur + 1, startTime=0.0, endTime=spinTime), ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime), Func(suit.detachPropeller)))
    result = Parallel(Sequence(Func(_attachCutscenePropeller, suit), ActorInterval(suit.prop, 'propeller', startFrame=lastSpinFrame, endFrame=suit.prop.getNumFrames('propeller'), playRate=-1.6)), Sequence(Wait(0.5), Parallel(moveIval, propTrack)))
    return result

def createSuitMoveIvalErfit(suit, destPos, hole):
    """
    Used in Erfit/Erclaim instance.
    Creates a sequence which moves the suit out of a hole.
    """
    dur = suit.getDuration('landing')
    fr = suit.getFrameRate('landing')
    landingDur = dur
    totalDur = 7.3
    animTimeInAir = totalDur - dur
    flyingDur = animTimeInAir
    moveIval = Sequence(Func(suit.pose, 'landing', 0), ProjectileInterval(suit, duration=flyingDur, endPos=destPos, gravityMult=0.125), ActorInterval(suit, 'landing'))
    if suit.prop is None:
        suit.prop = BattleProps.globalPropPool.getProp('propeller')
    propDur = suit.prop.getDuration('propeller')
    lastSpinFrame = 8
    fr = suit.prop.getFrameRate('propeller')
    spinTime = lastSpinFrame / fr
    openTime = (lastSpinFrame + 1) / fr
    propTrack = Parallel(SoundInterval(suit.propInSound, duration=flyingDur, node=suit), Sequence(ActorInterval(suit.prop, 'propeller', constrainedLoop=1, duration=flyingDur + 1, startTime=0.0, endTime=spinTime), ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime), Func(suit.detachPropeller)))
    hole.setPos(destPos[0], destPos[1], destPos[2])
    smallScale = 0.01
    bigScale = 2.25
    biggerScale = 2.5
    holeTrack = Sequence(Wait(0.25), Func(hole.show), LerpScaleInterval(hole, 0.65, biggerScale, blendType='easeIn'), LerpScaleInterval(hole, 0.15, bigScale, blendType='easeOut'), Wait(1.5), LerpScaleInterval(hole, 0.15, biggerScale, blendType='easeIn'), LerpScaleInterval(hole, 0.65, smallScale, blendType='easeOut'), Func(hole.removeNode))
    hole.hide()
    hole.setScale(0.01)
    result = Parallel(Func(suit.attachPropeller), Sequence(Wait(0.5), Parallel(moveIval, propTrack)), holeTrack)
    return result
'\nAll cutscene sequences\n'

@cutsceneSequence(name='Suit: Show', enum=EDE.showSuit)
def seq_showSuit(suitIndex=0, cutsceneDict=None):
    retParallel = Parallel()
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    retParallel.append(Func(suit.unstash))
    retParallel.append(Func(suit.show))
    if not cutsceneDict.get('suppressSuitNametags', False):
        retParallel.append(Func(suit.showNametag3d))
    else:
        retParallel.append(Func(_configureSuitNametag, suit, True))
    return retParallel

@cutsceneSequence(name='Suit: Hide', enum=EDE.hideSuit)
def seq_hideSuit(suitIndex=0, cutsceneDict=None):
    """Hides a suit."""
    retParallel = Parallel()
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    retParallel.append(Func(suit.stash))
    if cutsceneDict.get('suppressSuitNametags', False):
        retParallel.append(Func(_configureSuitNametag, suit, False))
    else:
        retParallel.append(Func(suit.hideNametag2d))
        retParallel.append(Func(suit.hideNametag3d))
    return retParallel

@cutsceneSequence(name='Suit: Show All', enum=EDE.showSuits)
def seq_showSuits(cutsceneDict=None):
    retParallel = Parallel()
    for suit in cutsceneDict['suits']:
        if not suit:
            continue
        retParallel.append(Func(suit.unstash))
        retParallel.append(Func(suit.show))
        if not cutsceneDict.get('suppressSuitNametags', False):
            retParallel.append(Func(suit.showNametag3d))
        else:
            retParallel.append(Func(_configureSuitNametag, suit, True))
    return retParallel

@cutsceneSequence(name='Suit: Hide All', enum=EDE.hideSuits)
def seq_hideSuits(cutsceneDict=None):
    retParallel = Parallel()
    for suit in cutsceneDict['suits']:
        if not suit:
            continue
        retParallel.append(Func(suit.stash))
        if cutsceneDict.get('suppressSuitNametags', False):
            retParallel.append(Func(_configureSuitNametag, suit, False))
        else:
            retParallel.append(Func(suit.hideNametag2d))
            retParallel.append(Func(suit.hideNametag3d))
    return retParallel

@cutsceneSequence(name='Suit: Animation', enum=EDE.doSuitAnim)
def seq_suitAnim(suitIndex=0, anim='neutral', loop=0, hasDuration=0, duration=0, hasStartTime=0, startTime=0, hasEndTime=0, endTime=0, playRate=1, useEndAnim=0, endAnim='neutral', isInterval=1, oldStyleEndAnim=1, cutsceneDict=None):
    """Makes a suit do an animation using its preflighted AnimControl."""
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    if not hasDuration:
        duration = None
    if not hasStartTime:
        startTime = None
    if not hasEndTime:
        endTime = None
    if not useEndAnim:
        endAnim = None
    playRate = playRate if playRate else 1.0

    control, animDuration, animFrameCount = _requireActorAnimation(
        suit, anim, 'Suit %s' % suitIndex, cutsceneDict, suitIndex)
    endControl = None
    if endAnim:
        endControl, _, _ = _requireActorAnimation(
            suit, endAnim, 'Suit %s end' % suitIndex,
            cutsceneDict, suitIndex)

    startFrame = round(startTime / max(animDuration, 0.01) * animFrameCount) if startTime else 0
    endFrame = round(endTime / max(animDuration, 0.01) * animFrameCount) if endTime else animFrameCount

    if not loop:
        if isInterval:
            ival = ResolvedActorInterval(
                suit, anim, control, loop=loop, duration=duration,
                startTime=startTime, endTime=endTime, playRate=playRate)
        else:
            ival = Func(
                _playResolvedControl, control, startFrame, endFrame)
        if oldStyleEndAnim:
            return Parallel(
                ival,
                Sequence(
                    Wait(duration),
                    ResolvedActorInterval(suit, endAnim, endControl)
                ) if duration and endControl else Sequence())
        if duration:
            return Parallel(
                ival,
                Sequence(
                    Wait(duration),
                    Func(_loopResolvedControl, endControl)
                ) if endControl else Sequence())
        elif endControl:
            return Sequence(ival, Func(_loopResolvedControl, endControl))
        return Sequence(ival)
    return Sequence(Func(_loopResolvedControl, control))

@cutsceneSequence(name='Suit: Blend Animation', enum=EDE.doSuitBlendAnim)
def seq_suitBlendAnim(suitIndex=0, fromAnim='neutral', toAnim='neutral', continueToAnim=True, duration=0, hasFromStartTime=0, fromStartTime=0, hasFromEndTime=0, fromEndTime=0, hasToStartTime=0, toStartTime=0, hasToEndTime=0, toEndTime=0, blendType='easeInOut', cutsceneDict=None):
    av = cutsceneDict['suits'][suitIndex]
    if not av:
        return Sequence()
    if not hasFromStartTime:
        fromStartTime = None
    if not hasFromEndTime:
        fromEndTime = None
    if not hasToStartTime:
        toStartTime = None
    if not hasToEndTime:
        toEndTime = None

    fromControl, _, _ = _requireActorAnimation(
        av, fromAnim, 'Suit %s blend-from' % suitIndex,
        cutsceneDict, suitIndex)
    toControl, _, _ = _requireActorAnimation(
        av, toAnim, 'Suit %s blend-to' % suitIndex,
        cutsceneDict, suitIndex)

    animSeq = Parallel(
        ResolvedActorInterval(
            av, toAnim, toControl, loop=True, duration=duration,
            startTime=toStartTime, endTime=toEndTime),
        ResolvedActorInterval(
            av, fromAnim, fromControl, duration=duration,
            startTime=fromStartTime, endTime=fromEndTime),
        ResolvedLerpAnimInterval(
            duration, fromAnim, [fromControl], toAnim, [toControl],
            blendType=blendType))
    animSeq = Sequence(
        Func(av.setBlend, frameBlend=base.wantSmoothAnims, animBlend=True,
             partName=SUIT_BODY_PART),
        Func(_stopResolvedControls, [fromControl, toControl]),
        animSeq,
        Func(av.setBlend, frameBlend=base.wantSmoothAnims, animBlend=False,
             partName=SUIT_BODY_PART))
    if continueToAnim:
        animSeq.append(ResolvedActorInterval(
            av, toAnim, toControl, startTime=toEndTime))
    return animSeq

@cutsceneSequence(name='Suit: Pingpong', enum=EDE.doSuitPingpong)
def seq_suitPingpong(suitIndex=0, anim='neutral', loop=0, hasDuration=0, duration=0.0, startTime=0, endTime=0, cutsceneDict=None):
    """Makes a suit pingpong an animation."""
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    if not hasDuration:
        duration = None
    animDuration = suit.getDuration(anim, SUIT_BODY_PART)
    animFrameCount = suit.getNumFrames(anim, SUIT_BODY_PART)
    startFrame = round(startTime / max(animDuration, 0.01) * animFrameCount) if startTime else 0
    endFrame = round(endTime / max(animDuration, 0.01) * animFrameCount) if endTime else animFrameCount
    track = Sequence(Func(_pingpongSuitAnimation, suit, anim, loop, startFrame, endFrame))
    if hasDuration:
        track.append(Sequence(Wait(duration), Func(_loopSuitAnimation, suit, 'neutral')))
    return track

@cutsceneSequence(name='Suit: Animate All', enum=EDE.animateAllSuits)
def seq_allSuitsDoAnim(startAnim='neutral', loop=0, hasDuration=0, duration=0, hasStartTime=0, startTime=0, hasEndTime=0, endTime=0, playRate=1.0, useEndAnim=0, endAnim='neutral', isInterval=0, cutsceneDict=None):
    if not hasDuration:
        duration = None
    if not hasStartTime:
        startTime = None
    if not hasEndTime:
        endTime = None
    if not useEndAnim:
        endAnim = None
    retParallel = Parallel()
    for suit in cutsceneDict['suits']:
        if not suit:
            continue
        playRate = playRate if playRate else 1.0
        animDuration = suit.getDuration(startAnim, SUIT_BODY_PART)
        animFrameCount = suit.getNumFrames(startAnim, SUIT_BODY_PART)
        startFrame = round(startTime / max(animDuration, 0.01) * animFrameCount) if startTime else 0
        endFrame = round(endTime / max(animDuration, 0.01) * animFrameCount) if endTime else animFrameCount
        if not loop:
            retParallel.append(Parallel(ActorInterval(suit, startAnim, loop=loop, duration=duration, startTime=startTime, endTime=endTime, playRate=playRate, partName=SUIT_BODY_PART) if isInterval else Func(_playSuitAnimation, suit, startAnim, startFrame, endFrame), Sequence(Wait(duration), ActorInterval(suit, endAnim, partName=SUIT_BODY_PART)) if duration and endAnim else Sequence()))
        else:
            retParallel.append(Sequence(Func(_loopSuitAnimation, suit, startAnim)))
    return retParallel

@cutsceneSequence(name='Suit: Pingpong All', enum=EDE.pingpongAllSuits)
def seq_allSuitPingpong(anim='neutral', loop=0, hasDuration=0, duration=0.0, startTime=0, endTime=0, cutsceneDict=None):
    """Makes all suits pingpong an animation."""
    track = Parallel()
    for i in range(len(cutsceneDict['suits'])):
        suit = cutsceneDict['suits'][i]
        if not suit:
            continue
        track.append(seq_suitPingpong(i, anim, loop, hasDuration, duration, startTime, endTime))
    return track

@cutsceneSequence(name='Suit: Head Animation', enum=EDE.doSuitHeadAnim)
def seq_suitHeadAnim(suitIndex=0, anim='neutral', loop=0, hasDuration=0, duration=0, hasStartTime=0, startTime=0, hasEndTime=0, endTime=0, playRate=1, useEndAnim=0, endAnim='neutral', isInterval=1, cutsceneDict=None):
    """Animate a manager head using one exclusive resolved control.

    Altis starts each animated Cog head's neutral control when the Suit is
    generated.  ResolvedActorInterval poses cached controls directly, so that
    old neutral loop must be stopped before every fusion shot.  Otherwise the
    High Roller's duck joints are driven by two controls at once and visibly
    snap each time the neutral loop wraps.
    """
    suit = cutsceneDict['suits'][suitIndex]
    head = _getSuitHeadActor(suit)
    if not suit or head is None:
        return Sequence()
    if not hasDuration:
        duration = None
    if not hasStartTime:
        startTime = None
    if not hasEndTime:
        endTime = None
    if not useEndAnim:
        endAnim = None
    playRate = playRate if playRate else 1.0

    control, animDuration, animFrameCount = _requireActorAnimation(
        head, anim, 'Suit %s head' % suitIndex,
        cutsceneDict, suitIndex, 'suitHeadAnimationControls')
    endControl = None
    if endAnim:
        endControl, _, _ = _requireActorAnimation(
            head, endAnim, 'Suit %s head end' % suitIndex,
            cutsceneDict, suitIndex, 'suitHeadAnimationControls')

    caches = cutsceneDict.get('suitHeadAnimationControls', ())
    allHeadControls = []
    if suitIndex < len(caches):
        allHeadControls = list(caches[suitIndex].values())

    startFrame = round(startTime / max(animDuration, 0.01) * animFrameCount) if startTime else 0
    endFrame = round(endTime / max(animDuration, 0.01) * animFrameCount) if endTime else animFrameCount
    stopExisting = Func(_stopResolvedControls, allHeadControls)

    if not loop:
        primary = ResolvedActorInterval(
            head, anim, control, loop=loop, duration=duration,
            startTime=startTime, endTime=endTime, playRate=playRate) if isInterval else Func(
                _playResolvedControl, control, startFrame, endFrame)
        animation = Parallel(
            primary,
            Sequence(
                Wait(duration),
                Func(_stopResolvedControls, allHeadControls),
                Func(_loopResolvedControl, endControl)
            ) if duration and endControl else Sequence())
        return Sequence(stopExisting, animation)

    return Sequence(
        stopExisting,
        Func(_loopResolvedControl, control))

@cutsceneSequence(name='Suit: Apply Visual Effect', enum=EDE.suitApplyVisualEffect)
def seq_suitApplyVisualEffect(suitIndex=0, vfxIndex=0, delay=0.0, cutsceneDict=None):
    """Applies a visual effect to a suit."""
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    effect = cutsceneDict['visualEffects'][vfxIndex]
    return Sequence(Wait(delay), Func(applySuitVisualEffect, suit, effect))

@cutsceneSequence(name='Suit: Unapply Visual Effect', enum=EDE.suitUnapplyVisualEffect)
def seq_suitUnapplyVisualEffect(suitIndex=0, vfxIndex=0, delay=0.0, cutsceneDict=None):
    """Unapplies a visual effect from a suit."""
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    effect = cutsceneDict['visualEffects'][vfxIndex]
    return Sequence(Wait(delay), Func(unapplySuitVisualEffect, suit, effect))

@cutsceneSequence(name='Suit: Unchat All', enum=EDE.clearAllSuitChat)
def seq_allSuitsClearChat(cutsceneDict=None):
    retParallel = Parallel()
    for suit in cutsceneDict['suits']:
        if not suit:
            continue
        retParallel.append(Func(suit.clearChat))
    return retParallel
'\nSuit Spawning Sequences\n'

@cutsceneSequence(name='Suit: Lock Propeller', enum=EDE.suitLockPropeller)
def seq_suitLockPropeller(suitIndex=0, locked=0, cutsceneDict=None):
    seq = Sequence()
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    seq.append(Func(suit.setPropellerLocked, locked))
    return seq

@cutsceneSequence(name='Suit: Supa Fly', enum=EDE.suitSupaFly)
def seq_suitFly(suitIndex=0, delay=0, destPos=(0, 0, 0), flyType=0, getPos=0, speed=1.0, cutsceneDict=None):
    retParallel = Sequence()
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    if flyType == 0:
        return Sequence()
    if getPos == 0:
        retParallel.append(Sequence(Wait(delay), suit.beginSupaFlyMove(Point3(*destPos), flyType - 1, None, False, speed=speed)))
        return retParallel
    else:
        retParallel.append(Sequence(Wait(delay), suit.beginSupaFlyMove(Point3(*destPos), flyType - 1, None, False, speed=speed, flyOutBasedOnCurrentPos=True)))
        return retParallel

@cutsceneSequence(name='Suit: Projectile Fly', enum=EDE.suitProjectileFly)
def seq_suitProjectileFly(suitIndex=0, delay=0, flyDuration=4.0, gravityMult=0.4, destPos=(0, 0, 0), cutsceneDict=None):
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    destPos = Point3(*destPos)
    moveIval = createSuitMoveIval(suit, destPos, duration=flyDuration, gravityMult=gravityMult)
    suitTrack = Sequence(Wait(delay), moveIval, Func(_loopSuitAnimation, suit, 'neutral'))
    return suitTrack

@cutsceneSequence(name='Suit: Turn All to Node', enum=EDE.turnSuitsToNode)
def seq_turnSuitsToNode(nodeIndex=None, duration=0, blendType='easeInOut', anim='walk', offset=(0, 0, 0), cutsceneDict=None):
    retseq = Parallel()
    for i, suit in enumerate(cutsceneDict['suits']):
        if not suit:
            continue
        retseq.append(seq_turnSingleSuitToNode(suitIndex=i, nodeIndex=nodeIndex, duration=duration, blendType=blendType, anim=anim, offset=offset, cutsceneDict=cutsceneDict))
    return retseq

@cutsceneSequence(name='Suit: Turn One to Node', enum=EDE.turnSingleSuitToNode)
def seq_turnSingleSuitToNode(suitIndex=0, nodeIndex=None, duration=0.0, blendType='easeInOut', anim='walk', offset=(0, 0, 0), cutsceneDict=None):

    def getNodePos():
        return cutsceneDict['nodes'][nodeIndex].getPos(render) + LVecBase3f(*offset)
    return seq_turnSingleSuitToPoint(suitIndex=suitIndex, point=getNodePos, duration=duration, blendType=blendType, anim=anim, cutsceneDict=cutsceneDict)

@cutsceneSequence(name='Suit: Turn Single to Point', enum=EDE.turnSingleSuitToPoint)
def seq_turnSingleSuitToPoint(suitIndex=0, point=(0, 0, 0), duration=0.0, blendType='easeInOut', anim='walk', cutsceneDict=None):
    retseq = Parallel()
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    turnDict = {'startH': 0, 'endH': 0}

    def setupTurnDict():
        startH = suit.getH(render) % 360
        a = suit.getPos(render)
        if callable(point):
            b = point()
        elif isinstance(point, tuple):
            b = LVecBase3f(*point)
        else:
            b = point
        endH, _, _ = getHprBetweenPoints(a, b)
        endH %= 360
        difference = startH - endH
        if difference > 180:
            startH -= 360
        elif difference < -180:
            endH -= 360
        turnDict['startH'] = startH
        turnDict['endH'] = endH

    def turnCallback(t):
        suit.setH(render, lerp(turnDict['startH'], turnDict['endH'], t))
    if duration is None or duration <= 0:
        return Sequence(Func(setupTurnDict), Func(turnCallback, 1.0))
    walkControl, _, _ = _requireActorAnimation(
        suit, anim, 'Suit %s turn' % suitIndex, cutsceneDict, suitIndex)
    neutralControl, _, _ = _requireActorAnimation(
        suit, 'neutral', 'Suit %s turn end' % suitIndex,
        cutsceneDict, suitIndex)
    retseq.append(Sequence(
        Parallel(
            ResolvedActorInterval(
                suit, anim, walkControl, duration=duration, loop=True),
            Func(setupTurnDict),
            LerpFunc(turnCallback, duration=duration, blendType=blendType)),
        Wait(0.01),
        Func(_loopResolvedControl, neutralControl)))
    return retseq

@cutsceneSequence(name='Suit: Turn All to Point', enum=EDE.turnSuitsToPoint)
def seq_turnSuitsToPoint(point=(0, 0, 0), duration=0.0, blendType='easeInOut', anim='walk', cutsceneDict=None):
    retseq = Parallel()
    for i, suit in enumerate(cutsceneDict['suits']):
        if not suit:
            continue
        retseq.append(seq_turnSingleSuitToPoint(suitIndex=i, point=point, duration=duration, blendType=blendType, anim=anim, cutsceneDict=cutsceneDict))
    return retseq

@cutsceneSequence(name='Suit: Turn Single to HPR', enum=EDE.turnSingleSuitToHpr)
def seq_turnSingleSuitToHpr(suitIndex=0, delay=0, duration=0, hpr=(0, 0, 0), startHpr=(0, 0, 0), useStartHpr=0, blendType='easeInOut', anim='walk', cutsceneDict=None):
    retseq = Parallel()
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()

    targetHpr = LVecBase3f(*hpr)

    # Clash has initialization turns whose duration is exactly zero.
    # An instant turn does not need an animation interval.
    if duration is None or duration <= 0:
        return Sequence(Wait(delay), Func(suit.setHpr, targetHpr))

    if not useStartHpr:
        startHpr = None
    else:
        startHpr = LVecBase3f(*startHpr)

    walkControl, _, _ = _requireActorAnimation(
        suit, anim, 'Suit %s turn' % suitIndex, cutsceneDict, suitIndex)
    neutralControl, _, _ = _requireActorAnimation(
        suit, 'neutral', 'Suit %s turn end' % suitIndex,
        cutsceneDict, suitIndex)
    retseq.append(Sequence(
        Wait(delay),
        Parallel(
            ResolvedActorInterval(
                suit, anim, walkControl, duration=duration, loop=True),
            LerpHprInterval(
                suit, duration, targetHpr,
                startHpr=startHpr, blendType=blendType)),
        Wait(0.01),
        Func(_loopResolvedControl, neutralControl)))
    return retseq

@cutsceneSequence(name='Suit: Turn All to HPR', enum=EDE.turnSuitsToHpr)
def seq_turnSuitsToHpr(delay=0, duration=0, hpr=(0, 0, 0), startHpr=(0, 0, 0), useStartHpr=0, blendType='easeInOut', anim='walk', cutsceneDict=None):
    retseq = Parallel()
    for i, suit in enumerate(cutsceneDict['suits']):
        if not suit:
            continue
        retseq.append(seq_turnSingleSuitToHpr(suitIndex=i, delay=delay, duration=duration, hpr=hpr, startHpr=startHpr, useStartHpr=useStartHpr, blendType=blendType, anim=anim, cutsceneDict=cutsceneDict))
    return retseq

@cutsceneSequence(name='Chainsaw: Set Head Glitch State', enum=EDE.chainsawSetHeadGlitch, hidden=True)
def seq_setChainsawHeadGlitchState(suitIndex=0, delay=0, glitch=0, cutsceneDict=None):
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    specialHead = getattr(suit, 'specialHead', None)
    if not specialHead:
        return Sequence()
    methodName = 'enterGlitch' if glitch else 'exitGlitch'
    glitchFunc = getattr(specialHead, methodName, None)
    if not glitchFunc:
        return Sequence()
    return Sequence(Wait(delay), Func(glitchFunc))

@cutsceneSequence(name='Prethinker: Do Brain Blast', enum=EDE.prethinkerDoBrainBlast, hidden=True)
def seq_setPrethinkerBrainBlastState(suitIndex=0, delay=0, cutsceneDict=None):
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    specialHead = getattr(suit, 'specialHead', None)
    brainBlast = getattr(specialHead, 'doBrainBlast', None) if specialHead else None
    if not brainBlast:
        return Sequence()
    return Sequence(Wait(delay), Func(brainBlast))

@cutsceneSequence(name='Suit: Fire From Cannon', enum=EDE.suitFireFromCannon)
def seq_suitFireFromCannon(suitIndex=0, delay=0, resetDelay=0, cogCannon=False, aimAtPoint=False, aimAtNode=False, point=(0, 0, 0), nodeIndex=0, fireDelay=2.5, unemployment=True, cutsceneDict=None):
    suit = cutsceneDict['suits'][suitIndex]
    pointNode = cutsceneDict['nodes'][nodeIndex]
    if not suit:
        return Sequence()
    if cogCannon:
        cannon = loader.loadModel('phase_5/models/props/cannon_cog')
    else:
        cannon = loader.loadModel('phase_4/models/minigames/toon_cannon')
    barrel = cannon.find('**/cannon')
    barrel = NodePathWithState(barrel)
    referenceNode = render.attachNewNode('referenceNode-Cannon')
    referenceNode.hide()
    cannonHolder = NodePathWithState('CannonHolder')
    cannonHolder.reparentTo(referenceNode)
    cannon.reparentTo(cannonHolder)
    cannonAttachPoint = barrel.attachNewNode('CannonAttach')
    kapowAttachPoint = barrel.attachNewNode('kapowAttach')
    scaleFactor = 1.6
    iScale = 1 / scaleFactor
    barrel.setScale(scaleFactor, 1, scaleFactor)
    suitLevel = suit.getActualLevel()
    if suitLevel > 12:
        suitLevel = 12
    deep = 2.5 + suitLevel * 0.2
    import math
    suitScale = 0.9 - math.sqrt(suitLevel) * 0.1
    kapow = globalPropPool.getProp('kapow')
    kapow.reparentTo(kapowAttachPoint)
    kapow.hide()
    kapow.setScale(0.25)
    kapow.setBillboardPointEye()
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.reparentTo(cannonAttachPoint)
    smoke.setScale(0.5)
    smoke.hide()
    smoke.setBillboardPointEye()
    soundBomb = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_fire_alt.ogg')
    playSoundBomb = SoundInterval(soundBomb, node=cannonHolder)
    soundFly = base.loader.loadSfx('phase_4/audio/sfx/firework_whistle_01.ogg')
    playSoundFly = SoundInterval(soundFly, node=cannonHolder)
    soundCannonAdjust = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_adjust.ogg')
    playSoundCannonAdjust = SoundInterval(soundCannonAdjust, duration=0.6, node=cannonHolder)
    soundCogPanic = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogafssm.ogg')
    playSoundCogPanic = SoundInterval(soundCogPanic, node=cannonHolder)

    def getDustCloudIval():
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(1.0)
        dustCloud.createTrack()
        if not suit:
            return Sequence()
        return Sequence(Func(dustCloud.reparentTo, suit), dustCloud.track, Func(dustCloud.destroy), name='dustCloudIval')

    def makeSuitUnemployed():
        suit.makeUnemployed()
        suit.fired = True
        nameInfo = suit.createNameInfo(wantDept=False)
        suit.setDisplayName(nameInfo)

    def setupCannonAndCog():
        cannon.setPos(0, 0, -8.6)
        cannonHolder.setH(0)
        barrel.setHpr(0, 90, 0)
        referenceNode.setPos(suit.getPos(render))
        referenceNode.setHpr(suit.getHpr(render))
        cannonAttachPoint.setScale(iScale, 1, iScale)
        cannonAttachPoint.setPos(0, 6.7, 0)
        kapowAttachPoint.setPos(0, -0.5, 1.9)
        suit.reparentTo(cannonAttachPoint)
        suit.setPos(0, 0, 0)
        suit.setHpr(0, -90, 0)
    eventId = getUniqueCutsceneId()

    def updateHpr(t):
        a = referenceNode.getPos(render)
        if aimAtNode:
            pos = pointNode.getPos(render)
            pos.setZ(pos.getZ() + 2)
            b = LVecBase3f(*pos)
        else:
            b = LVecBase3f(*point)
        endH, endP, _ = getHprBetweenPoints(a, b)
        endH -= referenceNode.getH()
        h1 = getattr(cannonHolder, 'turnToPoint-%s' % eventId, cannonHolder.getH())
        p1 = getattr(barrel, 'turnToPoint-%s' % eventId, barrel.getP())
        goalH = (endH - h1) * t + h1
        goalP = (endP - p1) * t + p1
        cannonHolder.setH(goalH)
        barrel.setP(goalP)

    def updateStartHpr():
        setattr(cannonHolder, 'turnToPoint-%s' % eventId, cannonHolder.getH())
        setattr(barrel, 'turnToPoint-%s' % eventId, barrel.getP())
    if aimAtPoint or aimAtNode:
        rotateToPointTrack = Sequence(Func(updateStartHpr), LerpFunctionInterval(function=updateHpr, duration=0.6, blendType='easeIn'))
    else:
        rotateToPointTrack = LerpHprInterval(barrel, 0.6, Point3(0, 45, 0), blendType='easeIn')
    reactIval = Parallel(Func(setupCannonAndCog), Func(referenceNode.show), Sequence(LerpPosInterval(cannonHolder, 2.0, Point3(0, 0, 7), blendType='easeInOut'), Parallel(rotateToPointTrack, playSoundCannonAdjust), Wait(fireDelay - 0.5 + resetDelay), Parallel(LerpHprInterval(barrel, 0.6, Point3(0, 90, 0), blendType='easeIn'), playSoundCannonAdjust), LerpPosInterval(cannonHolder, 1.0, Point3(0, 0, 0), blendType='easeInOut')), Sequence(Wait(0.0), Parallel(Sequence(ActorInterval(suit, 'flail', duration=1.4, playRate=1.2), ActorInterval(suit, 'pie-small-react', startTime=1.3, duration=0.6), Func(suit.pose, 'neutral', 0)), Parallel(getDustCloudIval(), Func(makeSuitUnemployed)) if unemployment else Sequence(), suit.scaleInterval(1.0, suitScale), LerpPosInterval(suit, 0.25, Point3(0, -1.0, 0.0)), Sequence(Wait(0.25), Parallel(playSoundCogPanic, LerpPosInterval(suit, 1.5, Point3(0, -deep, 0.0), blendType='easeIn')))), Wait(fireDelay), Parallel(playSoundBomb, playSoundFly, Sequence(Func(smoke.show), Parallel(LerpScaleInterval(smoke, 0.5, 3), LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.hide)), Sequence(Func(kapow.show), ActorInterval(kapow, 'kapow'), Func(kapow.hide)), LerpPosInterval(suit, 3.0, Point3(0, 150.0, 0.0)), suit.scaleInterval(3.0, 0.01)), Func(suit.hide), Func(suit.reparentTo, render), Func(suit.setScale, 1.0)))
    removeThese = (referenceNode, cannonHolder, smoke, kapow, cannon, barrel, cannonAttachPoint, kapowAttachPoint)

    def cleanup():
        from direct.actor.Actor import Actor
        from panda3d.core import NodePath
        for node in removeThese:
            if isinstance(node, Actor):
                node.cleanup()
            elif isinstance(node, NodePath):
                node.removeNode()
    if cutsceneDict.get('isEditor', False):
        sival = Sequence(reactIval, Func(referenceNode.hide))
        cutsceneDict['editorCleanup'].append(cleanup)
    else:
        sival = Sequence(reactIval, Func(cleanup))
    return Sequence(Wait(delay), sival)

@cutsceneSequence(name='LAA: Trapdoor All', enum=EDE.laaTrapdoor, hidden=True)
def seq_laaTrapdoor(cutsceneDict=None):
    retParallel = Parallel()
    for suit in cutsceneDict['suits']:
        if not suit:
            continue
        retParallel.append(Sequence(Sequence(ActorInterval(suit, 'flail', startTime=0, endTime=0.65), Wait(1)), Sequence(ActorInterval(suit, 'flail', startTime=0.65, endTime=0), Func(_loopSuitAnimation, suit, 'neutral'))))
    return retParallel

@cutsceneSequence(name='Suit: Color Scale', enum=EDE.suitColorScale)
def seq_suitColorScale(suitIndex=0, delay=0, duration=0.0,
                       colorScale=(1, 1, 1, 1),
                       startColorScale=(1, 1, 1, 1),
                       useStartColorScale=0,
                       blendType='easeInOut', cutsceneDict=None, **kwargs):
    """Lerp a single suit's color scale (enum retained but absent upstream)."""
    suit = cutsceneDict['suits'][suitIndex]
    if not suit:
        return Sequence()
    if not useStartColorScale:
        startColorScale = None
    else:
        startColorScale = LVecBase4f(*startColorScale)
    return Sequence(
        Wait(delay),
        LerpColorScaleInterval(
            suit, duration,
            colorScale=LVecBase4f(*colorScale),
            startColorScale=startColorScale,
            blendType=blendType))
