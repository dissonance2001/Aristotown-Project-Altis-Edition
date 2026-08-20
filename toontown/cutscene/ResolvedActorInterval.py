"""Intervals that play already-resolved Panda3D AnimControl objects.

Project Altis's older Actor implementation can return a valid control from
getAnimControl() while a later getAnimControls() lookup returns no controls.
The stock ActorInterval performs the latter lookup in its constructor.  CTSC
providers preflight and cache the exact controls, so this interval consumes
those controls directly and never performs a second Actor dictionary lookup.
"""

from __future__ import absolute_import
import math

from direct.interval.Interval import Interval
from pandac.PandaModules import CInterval, CLerpAnimEffectInterval


def _waitPending(control):
    try:
        control.waitPending()
    except:
        pass


def getControlMetadata(control, label='animation'):
    if control is None:
        raise RuntimeError('%s has no AnimControl.' % label)
    _waitPending(control)
    try:
        frames = control.getNumFrames()
        frameRate = control.getFrameRate()
    except Exception as error:
        raise RuntimeError('%s control metadata failed: %s' % (label, error))
    if frames is None or frames <= 0:
        raise RuntimeError('%s has invalid frame count %r.' % (label, frames))
    if frameRate is None or frameRate <= 0:
        raise RuntimeError('%s has invalid frame rate %r.' % (label, frameRate))
    duration = float(frames) / float(frameRate)
    return duration, frames, frameRate


def resolveControl(actor, animName, partName='modelRoot', lodName=None,
                   label=None):
    """Synchronously resolve one exact AnimControl from an Actor."""
    if label is None:
        label = '%s animation %r' % (actor, animName)
    try:
        actor.bindAnim(animName, partName, lodName, allowAsyncBind=False)
    except TypeError:
        # Compatibility with Actor variants that do not accept the keyword.
        actor.bindAnim(animName, partName, lodName, False)
    except:
        # getAnimControl below gives the useful failure if binding did not work.
        pass

    try:
        control = actor.getAnimControl(
            animName, partName, lodName, allowAsyncBind=False)
    except TypeError:
        control = actor.getAnimControl(animName, partName, lodName, False)

    duration, frames, frameRate = getControlMetadata(control, label)
    return control, duration, frames, frameRate


class ResolvedActorInterval(Interval):
    """ActorInterval-compatible interval using exact cached controls."""

    animNum = 1

    def __init__(self, actor, animName, controls, loop=0, constrainedLoop=0,
                 duration=None, startTime=None, endTime=None,
                 startFrame=None, endFrame=None, playRate=1.0, name=None,
                 forceUpdate=0):
        intervalId = 'ResolvedActor-%s-%d' % (
            animName, ResolvedActorInterval.animNum)
        ResolvedActorInterval.animNum += 1

        self.actor = actor
        self.animName = animName
        if isinstance(controls, (list, tuple)):
            self.controls = [control for control in controls if control is not None]
        else:
            self.controls = [controls] if controls is not None else []
        if not self.controls:
            raise RuntimeError('ResolvedActorInterval %r has no controls.' % animName)

        self.loopAnim = loop
        self.constrainedLoop = constrainedLoop
        self.forceUpdate = forceUpdate
        self.playRate = playRate
        if name is None:
            name = intervalId

        for control in self.controls:
            _waitPending(control)

        baseFrameRate = self.controls[0].getFrameRate()
        if baseFrameRate is None or baseFrameRate <= 0:
            raise RuntimeError(
                'ResolvedActorInterval %r has invalid frame rate %r.' %
                (animName, baseFrameRate))
        self.frameRate = baseFrameRate * abs(playRate)

        if startFrame is not None:
            self.startFrame = startFrame
        elif startTime is not None:
            self.startFrame = startTime * self.frameRate
        else:
            self.startFrame = 0

        if endFrame is not None:
            self.endFrame = endFrame
        elif endTime is not None:
            self.endFrame = endTime * self.frameRate
        elif duration is not None:
            if startTime is None:
                startTime = float(self.startFrame) / float(self.frameRate)
            self.endFrame = duration * self.frameRate
        else:
            maxFrames = self.controls[0].getNumFrames()
            for control in self.controls[1:]:
                maxFrames = max(maxFrames, control.getNumFrames())
            self.endFrame = maxFrames - 1

        self.reverse = playRate < 0
        if self.endFrame < self.startFrame:
            self.reverse = True
            self.startFrame, self.endFrame = self.endFrame, self.startFrame

        self.numFrames = self.endFrame - self.startFrame + 1
        self.implicitDuration = False
        if duration is None:
            self.implicitDuration = True
            duration = float(self.numFrames) / float(self.frameRate)

        Interval.__init__(self, name, duration)

    def getCurrentFrame(self):
        if self.isStopped():
            return None
        return self.startFrame + self.numFrames * self.currT

    def privStep(self, t):
        frameCount = t * self.frameRate
        if self.constrainedLoop:
            frameCount = frameCount % self.numFrames

        if self.reverse:
            absoluteFrame = self.endFrame - frameCount
        else:
            absoluteFrame = self.startFrame + frameCount

        integerFrame = int(math.floor(absoluteFrame + 0.0001))
        for control in self.controls:
            numFrames = control.getNumFrames()
            if self.loopAnim:
                frame = (integerFrame % numFrames) + (absoluteFrame - integerFrame)
            else:
                frame = max(min(absoluteFrame, numFrames - 1), 0)
            control.pose(frame)

        if self.forceUpdate:
            self.actor.update()
        self.state = CInterval.SStarted
        self.currT = t

    def privFinalize(self):
        if self.implicitDuration and not self.loopAnim:
            finalFrame = self.startFrame if self.reverse else self.endFrame
            for control in self.controls:
                control.pose(finalFrame)
            if self.forceUpdate:
                self.actor.update()
        else:
            self.privStep(self.getDuration())
        self.state = CInterval.SFinal
        self.intervalDone()


class ResolvedLerpAnimInterval(CLerpAnimEffectInterval):
    """Lerp animation effects using exact cached controls."""

    lerpAnimNum = 1

    def __init__(self, duration, startAnim, startControls, endAnim, endControls,
                 startWeight=0.0, endWeight=1.0, blendType='noBlend',
                 name=None):
        if name is None:
            name = 'ResolvedLerpAnimInterval-%d' % ResolvedLerpAnimInterval.lerpAnimNum
            ResolvedLerpAnimInterval.lerpAnimNum += 1
        blendType = self.stringBlendType(blendType)
        if blendType == self.BTInvalid:
            raise ValueError('Invalid animation blend type: %r' % blendType)
        CLerpAnimEffectInterval.__init__(self, name, duration, blendType)

        for control in startControls:
            self.addControl(
                control, startAnim, 1.0 - startWeight, 1.0 - endWeight)
        for control in endControls:
            self.addControl(control, endAnim, startWeight, endWeight)
