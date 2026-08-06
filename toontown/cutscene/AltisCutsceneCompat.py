"""Reusable Corporate Clash cutscene compatibility helpers for Project Altis.

This module is intentionally conservative.  It contains only helpers that were
validated while porting the High Roller introduction to Altis's Python 2 / old
Panda3D Actor runtime.  Boss-specific actors, resources, positions, dialogue,
and cleanup remain in each cutscene provider.
"""

import os

from panda3d.core import Filename, VirtualFileSystem

from toontown.cutscene.ResolvedActorInterval import resolveControl


DEFAULT_LOG_PREFIX = '[Altis CTSC]'


def _prefix(logPrefix):
    return logPrefix or DEFAULT_LOG_PREFIX


def resourceExists(path):
    """Return whether a BAM resource exists through VFS or common disk roots."""
    filename = path if path.endswith('.bam') else path + '.bam'
    vfs = VirtualFileSystem.getGlobalPtr()
    if vfs.exists(Filename(filename)):
        return True

    relative = filename.lstrip('/\\')
    candidates = (
        os.path.join(os.getcwd(), relative),
        os.path.join(os.getcwd(), 'resources', *relative.split('/')),
        os.path.join(os.getcwd(), '..', 'resources', *relative.split('/')),
    )
    for candidate in candidates:
        if os.path.isfile(candidate):
            return True
    return False


def getAnimatedHead(suit, label, logPrefix=None):
    """Return the first valid animated head Actor owned by a Suit."""
    prefix = _prefix(logPrefix)
    parts = getattr(suit, 'animatedHeadParts', None) or []
    if not parts:
        try:
            parts = suit.getAnimatedHeadParts()
        except:
            parts = []
    if not parts:
        raise RuntimeError('%s %s has no animated head Actor.' %
                           (prefix, label))

    head = parts[0]
    if head is None:
        raise RuntimeError('%s %s animated head Actor is None.' %
                           (prefix, label))
    try:
        if head.isEmpty():
            raise RuntimeError('%s %s animated head Actor is empty.' %
                               (prefix, label))
    except AttributeError:
        pass
    return head


def querySinglePartAnimation(actor, animName, partName='modelRoot'):
    """Resolve one animation from an old single-part Panda Actor.

    Altis can return a valid control from getAnimControl while the no-part
    getDuration/getNumFrames calls inspect a different/default part.  Always
    query the same explicit part for all three values.
    """
    try:
        actor.bindAnim(animName, partName)
    except:
        pass
    control = actor.getAnimControl(animName, partName)
    duration = actor.getDuration(animName, partName)
    frames = actor.getNumFrames(animName, partName)
    return control, duration, frames


def validateExistingSuitAnimations(actor, animNames, label,
                                    logPrefix=None,
                                    partName='modelRoot'):
    """Validate aliases already registered by Altis without unloading them."""
    prefix = _prefix(logPrefix)
    try:
        generatedMap = actor.generateAnimDict()
    except:
        generatedMap = {}

    failures = []
    validated = []
    for animName in animNames:
        try:
            control, duration, frames = querySinglePartAnimation(
                actor, animName, partName)
        except Exception as error:
            control = duration = frames = None
            firstError = error
        else:
            firstError = None

        if (control is None or duration is None or frames is None or
                duration <= 0 or frames <= 0):
            # Lazy binding can be absent even when Altis generated a valid map.
            # Reload only that actor's existing mapping; never unload aliases.
            animPath = generatedMap.get(animName)
            if animPath:
                try:
                    actor.loadAnims({animName: animPath}, partName)
                    control, duration, frames = querySinglePartAnimation(
                        actor, animName, partName)
                except Exception as error:
                    firstError = error

        if (control is None or duration is None or frames is None or
                duration <= 0 or frames <= 0):
            failures.append(
                '%s -> %s (control=%r duration=%r frames=%r error=%r)' %
                (animName, generatedMap.get(animName), control, duration,
                 frames, firstError))
        else:
            validated.append(animName)

    if failures:
        raise RuntimeError(
            '%s %s existing animation validation failed:\n  %s' %
            (prefix, label, '\n  '.join(failures)))

    print('%s Preserved Altis %s: %s' %
          (prefix, label, ', '.join(sorted(validated))))


def loadAndValidateAdditionalAnimations(actor, animMap, label,
                                        logPrefix=None,
                                        partName='modelRoot'):
    """Add Clash-only aliases without disturbing existing Altis controls."""
    prefix = _prefix(logPrefix)
    missingFiles = []
    for animName, animPath in sorted(animMap.items()):
        if not resourceExists(animPath):
            missingFiles.append('%s -> %s.bam' % (animName, animPath))
    if missingFiles:
        raise RuntimeError(
            '%s Missing %s animation resources:\n  %s' %
            (prefix, label, '\n  '.join(missingFiles)))

    # Never call unloadAnims here.  Existing distributed Suit actors may share
    # bundles and already own valid walk/neutral controls.
    actor.loadAnims(animMap, partName)

    failures = []
    for animName, animPath in sorted(animMap.items()):
        try:
            control, duration, frames = querySinglePartAnimation(
                actor, animName, partName)
        except Exception as error:
            failures.append('%s -> %s (%s)' %
                            (animName, animPath, error))
            continue
        if (control is None or duration is None or frames is None or
                duration <= 0 or frames <= 0):
            failures.append(
                '%s -> %s (control=%r duration=%r frames=%r)' %
                (animName, animPath, control, duration, frames))

    if failures:
        raise RuntimeError(
            '%s %s animation binding failed:\n  %s' %
            (prefix, label, '\n  '.join(failures)))

    print('%s Added Clash %s: %s' %
          (prefix, label, ', '.join(sorted(animMap.keys()))))


def cacheResolvedControls(actor, animNames, label,
                          logPrefix=None,
                          partName='modelRoot'):
    """Cache exact controls that passed preflight before CTSC construction."""
    prefix = _prefix(logPrefix)
    controls = {}
    failures = []
    for animName in sorted(animNames):
        try:
            control, duration, frames, frameRate = resolveControl(
                actor, animName, partName,
                label='%s %s %s' % (prefix, label, animName))
            controls[animName] = control
        except Exception as error:
            failures.append('%s (%s)' % (animName, error))
    if failures:
        raise RuntimeError(
            '%s Could not cache exact %s controls:\n  %s' %
            (prefix, label, '\n  '.join(failures)))

    print('%s Cached exact %s controls: %s' %
          (prefix, label, ', '.join(sorted(controls.keys()))))
    return controls


def getMultipartToonAnimControls(toon, animName,
                                 partNames=('legs', 'torso'),
                                 lodNames=('1000', '500', '250')):
    """Bind and return all available controls for an Altis multipart Toon."""
    controls = []
    for partName in partNames:
        for lodName in lodNames:
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


def validateExistingMultipartAnimations(actor, animNames, label,
                                         logPrefix=None,
                                         partNames=('legs', 'torso'),
                                         lodNames=('1000', '500', '250')):
    """Validate body animations on every usable Toon part/LOD."""
    prefix = _prefix(logPrefix)
    failures = []
    validated = []
    for animName in animNames:
        try:
            controls = getMultipartToonAnimControls(
                actor, animName, partNames, lodNames)
            duration = actor.getDuration(animName)
            frames = actor.getNumFrames(animName)
        except Exception as error:
            failures.append('%s (%s)' % (animName, error))
            continue
        if (not controls or duration is None or frames is None or
                duration <= 0 or frames <= 0):
            failures.append('%s (controls=%s duration=%r frames=%r)' %
                            (animName, len(controls), duration, frames))
        else:
            validated.append('%s[%s]' % (animName, len(controls)))

    if failures:
        raise RuntimeError(
            '%s %s is missing required existing animations:\n  %s' %
            (prefix, label, '\n  '.join(failures)))

    print('%s Validated multipart %s: %s' %
          (prefix, label, ', '.join(validated)))


def configureSuitNametag(suit, visible=False):
    """Hide a Cog's name while keeping its chat/thought components usable."""
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


def installAnimationLoopGuard(actor, control, animName='neutral'):
    """Prevent a plain Actor.loop call from rewinding a playing control.

    Returns the original actor.loop method.  Pass that value to
    removeAnimationLoopGuard during cleanup.
    """
    if actor is None or control is None:
        return None

    originalLoop = actor.loop

    def guardedLoop(requestedAnim, *args, **kwargs):
        # Preserve explicit ranged or part-specific calls.  Only the plain
        # loop('neutral') style reset is intercepted.
        if requestedAnim == animName and not args and not kwargs:
            try:
                if control.isPlaying():
                    return None
            except:
                pass
            try:
                # restart=0 resumes the current phase instead of frame zero.
                return control.loop(0)
            except:
                pass
        return originalLoop(requestedAnim, *args, **kwargs)

    try:
        actor.loop = guardedLoop
        return originalLoop
    except:
        return None


def removeAnimationLoopGuard(actor, originalLoop):
    """Restore an Actor.loop method returned by installAnimationLoopGuard."""
    if actor is None or originalLoop is None:
        return
    try:
        actor.loop = originalLoop
    except:
        pass
