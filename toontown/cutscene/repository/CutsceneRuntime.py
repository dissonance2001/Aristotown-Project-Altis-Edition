"""Runtime loader for Corporate Clash .ctsc files on Project Altis/Python 2."""

import json
import os

from direct.interval.IntervalGlobal import Parallel, Sequence, Wait
from panda3d.core import Filename, VirtualFileSystem

from toontown.cutscene.CutsceneSequenceBase import cutsceneMethodDefs

# Only load the event modules used by highroller_intro.ctsc.  Keeping this
# focused avoids importing unrelated Clash encounter systems into Altis.
_EVENT_MODULES = (
    'AudioSequence',
    'CameraSequence',
    'EnvironmentSequence',
    'GUISequence',
    'GeneralSequence',
    'SuitSequence',
    'ToonSequence',
)
_eventsLoaded = False


def _loadEventModules():
    global _eventsLoaded
    if _eventsLoaded:
        return
    for moduleName in _EVENT_MODULES:
        __import__('toontown.cutscene.sequences.%s' % moduleName)
    _eventsLoaded = True


def getRegisteredEventNames():
    _loadEventModules()
    return sorted(cutsceneMethodDefs.keys())


def _readCutsceneData(resourcePath):
    virtualPath = Filename(resourcePath)
    vfs = VirtualFileSystem.getGlobalPtr()
    if vfs.exists(virtualPath):
        return json.loads(vfs.readFile(virtualPath, True))

    relativePath = resourcePath.lstrip('/\\')
    candidates = (
        os.path.join(os.getcwd(), 'resources', *relativePath.split('/')),
        os.path.join(os.getcwd(), '..', 'resources', *relativePath.split('/')),
    )
    for diskPath in candidates:
        if os.path.isfile(diskPath):
            cutsceneFile = open(diskPath, 'r')
            try:
                return json.load(cutsceneFile)
            finally:
                cutsceneFile.close()
    raise IOError('Could not locate cutscene file: %s' % resourcePath)


def _orderedSubevents(subEvents):
    def sortKey(item):
        try:
            return int(item[0])
        except (TypeError, ValueError):
            return item[0]
    return [value for key, value in sorted(subEvents.items(), key=sortKey)]


def _makeSubeventInterval(subeventData, cutsceneDict, resourcePath,
                          timelineName, timelineTime, subeventIndex):
    eventName = subeventData['eventDefEnum']
    definition = cutsceneMethodDefs.get(eventName)
    if definition is None:
        raise KeyError(
            '[CTSC] %s | %.3fs | %s | subevent %s: no handler for %s' %
            (resourcePath, timelineTime, timelineName, subeventIndex, eventName))

    kwargs = subeventData.get('kwargs', {})
    if not isinstance(kwargs, dict):
        kwargs = json.loads(kwargs)
    kwargs['cutsceneDict'] = cutsceneDict
    try:
        return definition['method'](**kwargs)
    except Exception as error:
        displayKwargs = dict(kwargs)
        displayKwargs.pop('cutsceneDict', None)
        raise RuntimeError(
            '[CTSC] %s | %.3fs | %s | subevent %s | %s | kwargs=%r | %s' %
            (resourcePath, timelineTime, timelineName, subeventIndex,
             eventName, displayKwargs, error))


def buildCutscene(resourcePath, cutsceneDict):
    """Build and return a Panda3D interval from a Clash .ctsc resource."""
    _loadEventModules()
    eventData = _readCutsceneData(resourcePath)
    track = Parallel()

    for event in eventData:
        mode = event.get('sequenceMode', 'Parallel')
        group = Sequence() if mode == 'Sequence' else Parallel()
        timelineName = event.get('name', '<unnamed>')
        timelineTime = float(event.get('time', 0.0))
        ordered = _orderedSubevents(event.get('subEvents', {}))
        for subeventIndex, subevent in enumerate(ordered):
            group.append(_makeSubeventInterval(
                subevent, cutsceneDict, resourcePath,
                timelineName, timelineTime, subeventIndex))
        track.append(Sequence(Wait(timelineTime), group))

    return track
