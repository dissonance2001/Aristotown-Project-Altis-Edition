import random
import math
from direct.showbase.PythonUtil import lerp
from toontown.battle.BattleProps import globalPropPool
from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.editor.CSEditorEnums import SubEventArgumentType as SEAT
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence, getUniqueCutsceneId
from panda3d.core import Point3, LVecBase3f, LVecBase4f, NodePath
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import BattleBase
from toontown.cutscene.editor.CSEditorClasses import EventArgument, CSEditorException
from toontown.cutscene.editor.CSEditorEnums import ToonBlockShape, ToonSubEventTargetGroup
from toontown.building.ElevatorConstants import ElevatorPoints, BigElevatorPoints
from toontown.cutscene.CutsceneSequenceHelpers import NodePathWithState, getHprBetweenPoints
from toontown.toonbase import TTLocalizer
from otp.otpbase import OTPLocalizer
from toontown.effects import DustCloud
try:
    from toontown.suit.SuitDNA import allSuitNames
except ImportError:
    from toontown.suit import SuitDNA
    allSuitNames = []
    for _deptList in SuitDNA.suitDeptCogs.values() + SuitDNA.suitDeptManagers.values():
        allSuitNames.extend(_deptList)

def loopToonOrDisguise(toon, animName):
    toon.suit.loop(animName) if toon.isDisguised else toon.loop(animName)


def _toonAnimTarget(toon):
    if getattr(toon, 'isDisguised', False):
        return toon.suit
    return toon


def _getMultipartToonAnimControls(toon, animName):
    """Return the exact body controls used by an Altis multipart Toon.

    Altis Toons keep the same animation on the legs and torso parts for each
    LOD.  The Actor-level getNumFrames()/play()/loop() helpers can inspect an
    arbitrary part and occasionally return None or leave the visible LOD in
    neutral.  Driving the six real controls directly avoids both problems.
    """
    if not toon or not animName:
        return []
    if getattr(toon, 'isDisguised', False):
        target = toon.suit
        try:
            target.bindAnim(animName, 'modelRoot')
        except:
            pass
        try:
            control = target.getAnimControl(animName, 'modelRoot')
        except:
            control = None
        return [control] if control is not None else []

    controls = []
    for partName in ('legs', 'torso'):
        for lodName in ('1000', '500', '250'):
            try:
                toon.bindAnim(animName, partName, lodName)
            except:
                pass
            try:
                control = toon.getAnimControl(animName, partName, lodName)
            except:
                control = None
            if control is not None:
                controls.append(control)
    return controls


def _getMultipartToonAnimMetrics(toon, animName):
    controls = _getMultipartToonAnimControls(toon, animName)
    if not controls:
        return None, None
    control = controls[0]
    try:
        frames = control.getNumFrames()
    except:
        frames = None
    try:
        frameRate = control.getFrameRate()
    except:
        frameRate = None
    if frames is None or frameRate is None or frameRate <= 0:
        return None, frames
    return float(frames) / float(frameRate), frames


def _prepareManualToonAnimation(toon):
    """Stop Altis's speed-driven Happy state before a CTSC animation.

    The High Roller intro moves the shared toonPosNode rather than each Toon,
    so Altis continues to measure each Toon at zero speed and repeatedly poses
    neutral.  Switching the multipart Toon FSM to ``off`` prevents that speed
    task from overriding the CTSC's walk/run/slip animations.
    """
    if not toon or getattr(toon, 'isDisguised', False):
        return
    try:
        toon.wakeUp()
    except:
        pass
    try:
        toon.animFSM.request('off')
    except:
        try:
            toon.stop()
        except:
            pass


def _directLoopToon(toon, animName, playRate=1.0):
    if not toon or not animName:
        return
    _prepareManualToonAnimation(toon)
    controls = _getMultipartToonAnimControls(toon, animName)
    for control in controls:
        try:
            control.setPlayRate(playRate)
            control.loop(True)
        except:
            pass


def _directPlayToon(toon, animName, playRate=1.0,
                    startFrame=None, endFrame=None):
    if not toon or not animName:
        return
    _prepareManualToonAnimation(toon)
    controls = _getMultipartToonAnimControls(toon, animName)
    for control in controls:
        try:
            control.setPlayRate(playRate)
            if startFrame is None:
                control.play()
            else:
                lastFrame = control.getNumFrames() - 1
                finalFrame = lastFrame if endFrame is None else min(endFrame, lastFrame)
                control.play(max(startFrame, 0), max(finalFrame, 0))
        except:
            pass


def _directNeutralToon(toon):
    _directLoopToon(toon, 'neutral', 1.0)


def _loopToonForDuration(toon, animName, duration, playRate=1.0):
    return Sequence(
        Func(_directLoopToon, toon, animName, playRate),
        Wait(max(float(duration), 0.0)),
    )

@cutsceneSequence(name='Toon: Move Sequence', enum=EDE.moveSingleToon)
def seq_moveSingleToon(toonIndex=0, pos=(0, 0, 0), duration=0, delay=0, hasAnim=True, anim='walk', cutsceneDict=None):
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    destination = LVecBase3f(*pos)
    if duration <= 0:
        return Sequence(Wait(delay), Func(toon.setPos, destination))
    animation = _loopToonForDuration(toon, anim, duration) if hasAnim else Wait(duration)
    return Sequence(
        Wait(delay),
        Parallel(animation, LerpPosInterval(toon, pos=destination, duration=duration)),
        Wait(0.01),
        Func(_directNeutralToon, toon) if hasAnim else Wait(0.0),
    )

@cutsceneSequence(name='Toon: Relative Turn&Move Sequence', enum=EDE.turnAndMoveToon)
def seq_moveAndTurnToon(toonIndex=0, goalPos=(0, 0, 0), goalHpr=(0, 0, 0), moveDuration=3.0, turnDuration=3.0, delay=0, walkAnim='walk', runAnim='run', cutsceneDict=None):
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    seq = Sequence(Wait(delay))
    if turnDuration != 0.0:
        seq.append(Parallel(
            _loopToonForDuration(toon, walkAnim, turnDuration),
            LerpHprInterval(toon, turnDuration, LVecBase3f(*goalHpr))))
    if moveDuration != 0.0:
        seq.append(Parallel(
            _loopToonForDuration(toon, runAnim, moveDuration),
            LerpPosInterval(toon, moveDuration, LVecBase3f(*goalPos))))
    seq.append(Wait(0.01))
    seq.append(Func(_directNeutralToon, toon))
    return seq

@cutsceneSequence(name='Toon: Move Block Sequence', enum=EDE.moveToonsInBlock)
def seq_moveToonsInBlock(target='All', pos=(0, 0, 0), duration=0, delay=0, hasAnim=True, anim='walk', shape='Elevator', radius=1.5, h=0.0, cutsceneDict=None):
    retseq = Parallel()
    targetGroup = ToonSubEventTargetGroup[target]
    blockShape = ToonBlockShape[shape]
    targetRange = _getTargetRange(targetGroup, cutsceneDict['toons'], cutsceneDict['maxPlayers'])
    blockPoints = _toonBlockPositions(pos, shape=blockShape, radius=radius, h=h, toons=cutsceneDict['toons'][(targetRange[0] if targetRange else 0):((targetRange[-1] + 1) if targetRange else 0)])
    for i in targetRange:
        retseq.append(seq_moveSingleToon(toonIndex=i, pos=blockPoints[i], duration=duration, delay=delay, anim=anim, hasAnim=hasAnim, cutsceneDict=cutsceneDict))
    return retseq

@cutsceneSequence(name='Toon: Turn All to Node', enum=EDE.turnToonsToNode)
def seq_turnToonsToNode(target='All', nodeIndex=None, duration=0, blendType='easeInOut', hasAnim=True, anim='walk', offset=(0, 0, 0), cutsceneDict=None):
    retseq = Parallel()
    targetGroup = ToonSubEventTargetGroup[target]
    for i in _getTargetRange(targetGroup, cutsceneDict['toons'], cutsceneDict['maxPlayers']):
        retseq.append(seq_turnSingleToonToNode(toonIndex=i, nodeIndex=nodeIndex, duration=duration, blendType=blendType, anim=anim, hasAnim=hasAnim, offset=offset, cutsceneDict=cutsceneDict))
    return retseq

@cutsceneSequence(name='Toon: Turn One to Node', enum=EDE.turnSingleToonToNode)
def seq_turnSingleToonToNode(toonIndex=0, nodeIndex=None, duration=0.0, blendType='easeInOut', hasAnim=True, anim='walk', offset=(0, 0, 0), cutsceneDict=None):

    def getNodePos():
        return cutsceneDict['nodes'][nodeIndex].getPos(render) + LVecBase3f(*offset)
    return seq_turnSingleToonToPoint(toonIndex=toonIndex, point=getNodePos, duration=duration, blendType=blendType, anim=anim, hasAnim=hasAnim, cutsceneDict=cutsceneDict)

@cutsceneSequence(name='Toon: Turn Single to Point', enum=EDE.turnSingleToonToPoint)
def seq_turnSingleToonToPoint(toonIndex=0, point=(0, 0, 0), duration=0.0, blendType='easeInOut', hasAnim=True, anim='walk', cutsceneDict=None):
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    turnDict = {'startH': 0, 'endH': 0}

    def setupTurnDict():
        startH = toon.getH(render) % 360
        a = toon.getPos(render)
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
        toon.setH(render, lerp(turnDict['startH'], turnDict['endH'], t))

    if duration <= 0:
        return Sequence(Func(setupTurnDict), Func(turnCallback, 1.0))
    animation = _loopToonForDuration(toon, anim, duration) if hasAnim else Wait(duration)
    return Sequence(
        Func(setupTurnDict),
        Parallel(animation, LerpFunc(turnCallback, duration=duration, blendType=blendType)),
        Wait(0.01),
        Func(_directNeutralToon, toon) if hasAnim else Wait(0.0),
    )

@cutsceneSequence(name='Toon: Turn All to Point', enum=EDE.turnToonsToPoint)
def seq_turnToonsToPoint(target='All', point=(0, 0, 0), duration=0.0, blendType='easeInOut', hasAnim=True, anim='walk', cutsceneDict=None):
    retseq = Parallel()
    targetGroup = ToonSubEventTargetGroup[target]
    for i in _getTargetRange(targetGroup, cutsceneDict['toons'], cutsceneDict['maxPlayers']):
        retseq.append(seq_turnSingleToonToPoint(toonIndex=i, point=point, duration=duration, blendType=blendType, anim=anim, hasAnim=hasAnim, cutsceneDict=cutsceneDict))
    return retseq

@cutsceneSequence(name='Toon: Turn Single to HPR', enum=EDE.turnSingleToonToHpr)
def seq_turnSingleToonToHpr(toonIndex=0, delay=0, duration=0, hpr=(0, 0, 0), startHpr=(0, 0, 0), useStartHpr=0, blendType='easeInOut', hasAnim=True, anim='walk', cutsceneDict=None):
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    destination = LVecBase3f(*hpr)
    if duration <= 0:
        return Sequence(Wait(delay), Func(toon.setHpr, destination))
    start = LVecBase3f(*startHpr) if useStartHpr else None
    animation = _loopToonForDuration(toon, anim, duration) if hasAnim else Wait(duration)
    # Pacesetter's first tackle deliberately continues slip-backward in the
    # next CTSC sub-event from startTime=1.0.  Do not insert Altis's normal
    # one-frame neutral between those two authored animation segments.
    continueSameSlip = bool(hasAnim and anim == 'slip-backward')
    return Sequence(
        Wait(delay),
        Parallel(animation, LerpHprInterval(
            toon, duration, destination, startHpr=start,
            blendType=blendType)),
        Wait(0.0 if continueSameSlip else 0.01),
        Wait(0.0) if continueSameSlip else
        (Func(_directNeutralToon, toon) if hasAnim else Wait(0.0)),
    )

@cutsceneSequence(name='Toon: Turn All to HPR', enum=EDE.turnToonsToHpr)
def seq_turnToonsToHpr(delay=0, duration=0, hpr=(0, 0, 0), startHpr=(0, 0, 0), useStartHpr=0, blendType='easeInOut', hasAnim=True, anim='walk', cutsceneDict=None):
    retseq = Parallel()
    for i, toon in enumerate(cutsceneDict['toons']):
        if not toon:
            continue
        retseq.append(seq_turnSingleToonToHpr(toonIndex=i, delay=delay, duration=duration, hpr=hpr, startHpr=startHpr, useStartHpr=useStartHpr, blendType=blendType, hasAnim=hasAnim, anim=anim, cutsceneDict=cutsceneDict))
    return retseq

@cutsceneSequence(name='Toon: Teleport to Elevator', enum=EDE.tpToonsToElevator)
def seq_moveToonsToElevator(target='Players', elevatorModelIndex=0, isBig=0, cutsceneDict=None):
    retParallel = Parallel()
    posList = BigElevatorPoints if isBig else ElevatorPoints
    targetGroup = ToonSubEventTargetGroup[target]
    if elevatorModelIndex is not None:
        for i in _getTargetRange(targetGroup, cutsceneDict['toons'], cutsceneDict['maxPlayers']):
            toon = cutsceneDict['toons'][i]
            if not toon:
                continue
            toonSeq = Sequence()
            toonSeq.append(Func(toon.reparentTo, cutsceneDict['elevators'][elevatorModelIndex]))
            toonSeq.append(Func(toon.setPos, *posList[i]))
            toonSeq.append(Func(toon.setH, 180))
            toonSeq.append(Func(toon.wrtReparentTo, render))
            retParallel.append(toonSeq)
    return retParallel

@cutsceneSequence(name='Toon: Move to Battle Positions', enum=EDE.moveToonsToBattlePos)
def seq_moveToonsToBattlePositions(duration=5.0, hasAnim=True, anim='walk', delay=0, battleNodeIndex=0, flipY=0, xyzOffset=(0, 0, 0), cutsceneDict=None):
    retseq = Parallel()
    toons = [toon for toon in cutsceneDict['toons'] if toon]
    toonPoints = BattleBase.toonPoints[len(toons) - 1]
    battlePos = cutsceneDict['nodes'][battleNodeIndex].getPos()
    for i, toon in enumerate(toons):
        goalPos, goalH = toonPoints[i]
        goalPos = goalPos + battlePos
        goalHpr = Point3(goalH, 0, 0)
        if flipY:
            x, y, z = goalPos
            goalPos = LVecBase3f(x, -y, z)
            goalHpr = Point3(-goalH + 180, 0, 0)
        xoff, yoff, zoff = xyzOffset
        x, y, z = goalPos
        goalPos = LVecBase3f(x + xoff, y + yoff, z + zoff)
        animation = _loopToonForDuration(toon, anim, duration) if hasAnim else Wait(duration)
        retseq.append(Sequence(
            Wait(delay),
            Parallel(animation, LerpPosHprInterval(
                toon, duration, pos=goalPos, hpr=goalHpr)),
            Wait(0.01),
            Func(_directNeutralToon, toon) if hasAnim else Wait(0.0)))
    return retseq

@cutsceneSequence(name='Toon: Animate', enum=EDE.animateSingleToon)
def seq_singleToonDoAnim(toonIndex=0, startAnim='neutral', loop=0, hasDuration=0, duration=0, hasStartTime=0, startTime=0, hasEndTime=0, endTime=0, playRate=1, useEndAnim=0, endAnim='neutral', isInterval=0, cutsceneDict=None):
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Parallel()
    duration = duration if hasDuration else None
    startTime = startTime if hasStartTime else None
    endTime = endTime if hasEndTime else None
    endAnim = endAnim if useEndAnim else None
    playRate = playRate if playRate else 1.0
    # Do not query Actor-level metrics unless the CTSC actually requests a
    # frame range.  On Altis multipart Toons those helpers can return None even
    # though all six body controls are valid, which previously crashed the
    # unchanged CTSC at the 113.5s ``Toons Shocked`` event.
    startFrame = None
    endFrame = None
    if hasStartTime or hasEndTime:
        animDuration, animFrameCount = _getMultipartToonAnimMetrics(
            toon, startAnim)
        if animDuration is None or animFrameCount is None:
            raise RuntimeError(
                'Toon %s animation %r has no multipart timing data.' %
                (toonIndex, startAnim))
        if hasStartTime:
            startFrame = int(round(
                float(startTime) / max(animDuration, 0.01) * animFrameCount))
        else:
            startFrame = 0
        if hasEndTime:
            endFrame = int(round(
                float(endTime) / max(animDuration, 0.01) * animFrameCount))
            endFrame = min(max(endFrame, 0), max(animFrameCount - 1, 0))
    if loop:
        return Sequence(Func(_directLoopToon, toon, startAnim, playRate))
    primary = Func(_directPlayToon, toon, startAnim, playRate, startFrame, endFrame)
    if duration is not None:
        track = Parallel(primary, Wait(duration))
        if endAnim:
            return Sequence(track, Func(_directLoopToon, toon, endAnim, 1.0))
        return track

    # Clash's ``isInterval`` path uses ActorInterval, which does not finish
    # until the requested animation segment has actually played.  Altis must
    # drive multipart Toon controls manually, but it still has to preserve the
    # same interval duration.  Without this wait, a following CTSC sub-event
    # (usually ``neutral``) runs on the same frame and cancels slip-backward.
    # Pacesetter's intro contains two such slip events.
    if isInterval:
        animDuration, animFrameCount = _getMultipartToonAnimMetrics(
            toon, startAnim)
        if animDuration is not None:
            segmentStart = float(startTime) if startTime is not None else 0.0
            segmentEnd = float(endTime) if endTime is not None else float(animDuration)
            segmentDuration = max(segmentEnd - segmentStart, 0.0)
            segmentDuration /= max(abs(float(playRate)), 0.0001)
            return Sequence(primary, Wait(segmentDuration))

    if endAnim:
        return Sequence(primary, Func(_directLoopToon, toon, endAnim, 1.0))
    return Sequence(primary)

@cutsceneSequence(name='Toon: Animate All Toons', enum=EDE.animateAllToons)
def seq_allToonsDoAnim(startAnim='neutral', loop=0, hasDuration=0, duration=0, hasStartTime=0, startTime=0, hasEndTime=0, endTime=0, playRate=1, useEndAnim=0, endAnim='neutral', isInterval=0, cutsceneDict=None):
    retParallel = Parallel()
    for i, toon in enumerate(cutsceneDict['toons']):
        if not toon:
            continue
        retParallel.append(seq_singleToonDoAnim(
            toonIndex=i, startAnim=startAnim, loop=loop,
            hasDuration=hasDuration, duration=duration,
            hasStartTime=hasStartTime, startTime=startTime,
            hasEndTime=hasEndTime, endTime=endTime,
            playRate=playRate, useEndAnim=useEndAnim,
            endAnim=endAnim, isInterval=isInterval,
            cutsceneDict=cutsceneDict))
    return retParallel

@cutsceneSequence(name='Toon: Pingpong', enum=EDE.pingpongSingleToon)
def seq_toonPingpong(toonIndex=0, anim='neutral', loop=0, hasDuration=0, duration=0.0, startTime=0, endTime=0, cutsceneDict=None):
    """Makes a toon pingpong an animation."""
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    if not hasDuration:
        duration = None
    animDuration = toon.getDuration(anim)
    animFrameCount = toon.getNumFrames(anim)
    startFrame = round(startTime / max(animDuration, 0.01) * animFrameCount) if startTime else 0
    endFrame = round(endTime / max(animDuration, 0.01) * animFrameCount) if endTime else animFrameCount
    track = Sequence(Func(toon.pingpong, anim, loop, None, startFrame, endFrame))
    if hasDuration:
        track.append(Sequence(Wait(duration), Func(loopToonOrDisguise(toon, 'neutral'))))
    return track

@cutsceneSequence(name='Toon: Pingpong All', enum=EDE.pingpongAllToons)
def seq_allToonsPingpong(anim='neutral', loop=0, hasDuration=0, duration=0.0, startTime=0, endTime=0, cutsceneDict=None):
    """Makes all toons pingpong an animation."""
    track = Parallel()
    for i in range(len(cutsceneDict['toons'])):
        track.append(seq_toonPingpong(i, anim, loop, hasDuration, duration, startTime, endTime, cutsceneDict))
    return track

@cutsceneSequence(name='Toon: Disguise All Toons (FOR TESTING ONLY!)', enum=EDE.disguiseAllToons)
def seq_disguiseAllToons(delay=0, cutsceneDict=None):
    retParallel = Parallel()
    for toon in cutsceneDict['toons']:
        if not toon:
            continue
        retParallel.append(Func(toon.putOnSuit, random.choice(allSuitNames)))
    return Sequence(Wait(delay), retParallel)

@cutsceneSequence(name='Toon: Undisguise All Toons', enum=EDE.undisguiseAllToons)
def seq_undisguiseAllToons(delay=0, cutsceneDict=None):
    retParallel = Parallel()
    for toon in cutsceneDict['toons']:
        if not toon:
            continue
        if not hasattr(toon, 'dustCloud') or toon.dustCloud is None:
            toon.dustCloud = DustCloud.DustCloud()
            toon.dustCloud.setPos(0, 2, 3)
            toon.dustCloud.setScale(0.5)
            toon.dustCloud.setDepthWrite(0)
            toon.dustCloud.setBin('fixed', 0)
            toon.dustCloud.createTrack()
        retParallel.append(Sequence(Func(toon.dustCloud.reparentTo, toon), Func(toon.dustCloud.show), Parallel(toon.dustCloud.track, Sequence(Wait(0.3), Func(toon.takeOffSuit), Func(toon.sadEyes), Func(toon.blinkEyes), Func(toon.play, 'slip-backward'), Wait(0.7))), Func(toon.dustCloud.hide), Func(toon.normalEyes)))
    snd = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_propellerBreaks.ogg')
    return Sequence(Wait(delay), Func(snd.play), retParallel)

@cutsceneSequence(name='Toon: Set One Anim State', enum=EDE.setOneAnimState)
def seq_setOneToonAnimState(toonIndex=0, delay=0, animState='Neutral', cutsceneDict=None):
    retParallel = Parallel()
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    extraArgs = []
    if animState == 'Squish':
        extraArgs = [1.0 / len(cutsceneDict['toons'])]
    retParallel.append(Func(toon.setAnimState, animState, 1.0, None, None, None, extraArgs))
    return Sequence(Wait(delay), retParallel)

@cutsceneSequence(name='Toon: Set All Anim State', enum=EDE.setAllAnimStates)
def seq_setToonAnimState(delay=0, animState='Neutral', cutsceneDict=None):
    retParallel = Parallel()
    for toon in cutsceneDict['toons']:
        if not toon:
            continue
        extraArgs = []
        if animState == 'Squish':
            extraArgs = [1.0 / len(cutsceneDict['toons'])]
        retParallel.append(Func(toon.setAnimState, animState, 1.0, None, None, None, extraArgs))
    return Sequence(Wait(delay), retParallel)


def _playCutsceneEmote(toon, emoteIndex, emoteName=None):
    _prepareManualToonAnimation(toon)
    if emoteName == 'Taunt':
        try:
            toon.play('taunt')
        except:
            pass
        try:
            sfx = loader.loadSfx('phase_4/audio/sfx/avatar_emotion_taunt.ogg')
            base.playSfx(sfx, node=toon)
        except:
            pass
        return
    try:
        toon.doEmote(emoteIndex, 1.0, 0, None, [])
    except:
        pass

@cutsceneSequence(name='Toon: Emote One', enum=EDE.setOneEmote)
def seq_setOneToonEmote(toonIndex=0, delay=0, emoteIndex=0, cutsceneDict=None):
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    emoteName = emoteIndex
    emoteIndex = OTPLocalizer.EmoteFuncDict[emoteIndex]
    return Sequence(
        Wait(delay),
        Func(_playCutsceneEmote, toon, emoteIndex, emoteName))

@cutsceneSequence(name='Toon: Emote All', enum=EDE.setAllEmote)
def seq_setToonEmote(delay=0, emoteIndex=0, cutsceneDict=None):
    retParallel = Parallel()
    for i in range(len(cutsceneDict['toons'])):
        retParallel.append(seq_setOneToonEmote(i, 0, emoteIndex, cutsceneDict))
    return Sequence(Wait(delay), retParallel)

@cutsceneSequence(name='Toon: Show', enum=EDE.showToon)
def seq_showToon(toonIndex=0, cutsceneDict=None):
    retParallel = Parallel()
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    retParallel.append(Func(toon.show))
    retParallel.append(Func(toon.showNametag3d))
    return retParallel

@cutsceneSequence(name='Toon: Hide', enum=EDE.hideToon)
def seq_hideToon(toonIndex=0, cutsceneDict=None):
    retParallel = Parallel()
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    retParallel.append(Func(toon.hide))
    retParallel.append(Func(toon.hideNametag2d))
    retParallel.append(Func(toon.hideNametag3d))
    return retParallel

@cutsceneSequence(name='Toon: Show All', enum=EDE.showToons)
def seq_showToons(cutsceneDict=None):
    retParallel = Parallel()
    for toon in cutsceneDict['toons']:
        if not toon:
            continue
        retParallel.append(Func(toon.show))
        retParallel.append(Func(toon.showNametag3d))
    return retParallel

@cutsceneSequence(name='Toon: Hide All', enum=EDE.hideToons)
def seq_hideToons(cutsceneDict=None):
    retParallel = Parallel()
    for toon in cutsceneDict['toons']:
        if not toon:
            continue
        retParallel.append(Func(toon.hide))
        retParallel.append(Func(toon.hideNametag2d))
        retParallel.append(Func(toon.hideNametag3d))
    return retParallel

@cutsceneSequence(name='Toon: Fire From Cannon', enum=EDE.toonFireFromCannon)
def seq_toonFireFromCannon(toonIndex=0, toonFlyDist=150, toonFlyDur=3.0, delay=0, resetDelay=0, cogCannon=False, aimAtPoint=False, nodeIndex=0, startHpr=(0, 0, 0), hideAvatar=True, cutsceneDict=None):
    suit = cutsceneDict['toons'][toonIndex]
    point = cutsceneDict['nodes'][nodeIndex]
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
    deep = 2.7
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
        b = LVecBase3f(*point.getPos())
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
    if aimAtPoint:
        rotateToPointTrack = Sequence(Func(updateStartHpr), LerpFunctionInterval(function=updateHpr, duration=0.6, blendType='easeIn'))
    else:
        rotateToPointTrack = LerpHprInterval(barrel, 0.6, Point3(0, 45, 0), blendType='easeIn')
    reactIval = Parallel(Func(setupCannonAndCog), Func(referenceNode.show), Sequence(LerpPosHprInterval(cannonHolder, 2.0, Point3(0, 0, 7), Vec3(*startHpr), blendType='easeInOut'), Parallel(rotateToPointTrack, playSoundCannonAdjust), Wait(2.0 + resetDelay), Parallel(LerpHprInterval(barrel, 0.6, Point3(0, 90, 0), blendType='easeIn'), playSoundCannonAdjust), LerpPosInterval(cannonHolder, 1.0, Point3(0, 0, 0), blendType='easeInOut')), Sequence(Wait(0.0), Parallel(ActorInterval(suit, 'cringe'), suit.scaleInterval(1.0, 0.8), LerpPosInterval(suit, 0.25, Point3(0, -1.0, 0.0)), Sequence(Wait(0.25), Parallel(playSoundCogPanic, LerpPosInterval(suit, 1.5, Point3(0, -deep, 0.0), blendType='easeIn')))), Wait(2.5), Parallel(playSoundBomb, playSoundFly, Sequence(Func(smoke.show), Parallel(LerpScaleInterval(smoke, 0.5, 3), LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.hide)), Sequence(Func(kapow.show), ActorInterval(kapow, 'kapow'), Func(kapow.hide)), LerpPosInterval(suit, toonFlyDur, Point3(0, toonFlyDist, 0.0)), suit.scaleInterval(toonFlyDur, 0.01) if hideAvatar else suit.scaleInterval(0.01, 1.0), Sequence(Wait(toonFlyDur), Sequence(Func(suit.hide), Func(suit.reparentTo, render), Func(suit.setScale, 1.0)) if hideAvatar else Sequence(Func(suit.wrtReparentTo, render), Func(suit.setScale, 1.0))))))
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

@cutsceneSequence(name='Toon: Squish', enum=EDE.squishToon)
def seq_squishToon(toonIndex=0, cutsceneDict=None):
    toon = cutsceneDict['toons'][toonIndex]
    if not toon:
        return Sequence()
    return Sequence(Func(toon.setAnimState, 'Squish'), Func(toon.playDialogueForString, '!'), Wait(2.7), Func(toon.setAnimState, 'Neutral'))

def _toonBlockPositions(midPos, shape, radius, h=0.0, toons=[]):
    """
    Creates the positions for a Toon Block.

    :param midPos: The middle position of the block.
    :param shape: The shape of the block to be generated.
    :param radius: The radius of the block (distance between Toons; exact interpretation depends on block shape).
    :param toons: The toons being moved.
    """
    retBlock = []
    x, y, z = midPos
    if shape is ToonBlockShape.Elevator:
        retBlock.append(Point3(x + radius, y - radius, z))
        retBlock.append(Point3(x - radius, y - radius, z))
        retBlock.append(Point3(x + radius, y + radius, z))
        retBlock.append(Point3(x - radius, y + radius, z))
        retBlock.append(Point3(x + radius * 3, y - radius, z))
        retBlock.append(Point3(x - radius * 3, y - radius, z))
        retBlock.append(Point3(x + radius * 3, y + radius, z))
        retBlock.append(Point3(x - radius * 3, y + radius, z))
    elif shape is ToonBlockShape.BigElevator:
        retBlock.append(Point3(x + radius, y - radius, z))
        retBlock.append(Point3(x - radius, y - radius, z))
        retBlock.append(Point3(x + radius * 3, y - radius, z))
        retBlock.append(Point3(x - radius * 3, y - radius, z))
        retBlock.append(Point3(x + radius, y + radius, z))
        retBlock.append(Point3(x - radius, y + radius, z))
        retBlock.append(Point3(x + radius * 3, y + radius, z))
        retBlock.append(Point3(x - radius * 3, y + radius, z))
    elif shape is ToonBlockShape.SingleFile:
        for i in range(8):
            retBlock.append(Point3(x, y - radius * i * 2, z))
    elif shape is ToonBlockShape.DoubleFile:
        for i in range(4):
            retBlock.append(Point3(x - radius, y - radius * i * 2, z))
            retBlock.append(Point3(x + radius, y - radius * i * 2, z))
    elif shape is ToonBlockShape.FourWide:
        for i in range(-3, 4, 2):
            retBlock.append(Point3(x + radius * i, y + radius, z))
            retBlock.append(Point3(x + radius * i, y - radius, z))
    elif shape is ToonBlockShape.EightWide:
        for i in range(-7, 8, 2):
            retBlock.append(Point3(x + radius * i, y, z))
    elif shape is ToonBlockShape.Line:
        numOfToons = len(toons) - toons.count(None)
        distanceMulti = -0.5 * (numOfToons - 1)
        for toon in toons:
            if toon is None:
                retBlock.append(None)
                continue
            distance = distanceMulti * radius
            if distance == 0:
                retBlock.append(Point3(x, y, z))
            else:
                retBlock.append(Point3(x + distance * math.cos(math.radians(h)), y + distance * math.sin(math.radians(h)), z))
            distanceMulti += 1
    elif shape is ToonBlockShape.Circle:
        numOfToons = len(toons) - toons.count(None)
        i = 0
        for toon in toons:
            if toon is None:
                retBlock.append(None)
                continue
            if numOfToons == 1:
                retBlock.append(Point3(x, y, z))
            else:
                degrees = h + i * (360.0 / numOfToons)
                retBlock.append(Point3(x + radius * math.cos(math.radians(degrees)), y + radius * math.sin(math.radians(degrees)), z))
            i += 1
    return retBlock

def _getTargetRange(targetGroup, toons, maxPlayers):
    """
    Returns a range of Toons in the Toons list which are to be the target of the SubEvent.

    NPCs are placed into the Toons list at the first index
    which cannot be a player, e.g. in a 4-player miniboss
    cutscene, players occupy toons[0:4], and NPCs occupy
    toons[4:]. If fewer than max players are present,
    unoccupied spots in the Toons list are `None`, which
    isn't our problem to deal with here uwu

    :param targetGroup: The ToonSubEventTargetGroup that specifies which Toons should be affected (e.g. only NPCs).
    :param toons: Should be cutsceneDict['toons'].
    """
    if targetGroup is ToonSubEventTargetGroup.All:
        return range(len(toons))
    elif targetGroup is ToonSubEventTargetGroup.NPCs:
        return range(maxPlayers, len(toons))
    elif targetGroup is ToonSubEventTargetGroup.Players:
        return range(0, maxPlayers)
    raise CSEditorException('Got invalid ToonSubEventTargetGroup, or some other issue, while getting targetRange')
