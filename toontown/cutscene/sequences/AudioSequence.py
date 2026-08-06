from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.editor.CSEditorEnums import SubEventArgumentType as SEAT
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence
from direct.interval.IntervalGlobal import *


def _playCutsceneMusic(music, loop=True, volume=1.0, startTime=0.0):
    musicMgr = getattr(base, 'musicMgr', None)
    if musicMgr and hasattr(musicMgr, 'playMusic'):
        try:
            musicMgr.playMusic(music, looping=loop, volume=volume, time=startTime)
            return
        except TypeError:
            musicMgr.playMusic(music, looping=loop, volume=volume)
            return
    if isinstance(music, basestring):
        music = loader.loadMusic(music)
    try:
        base.playMusic(music, looping=loop, volume=volume, time=startTime)
    except TypeError:
        base.playMusic(music, looping=loop, volume=volume)


def _stopCutsceneMusic(music):
    musicMgr = getattr(base, 'musicMgr', None)
    if musicMgr and hasattr(musicMgr, 'stopMusic'):
        try:
            musicMgr.stopMusic(music)
            return
        except TypeError:
            pass
    if hasattr(music, 'stop'):
        music.stop()

@cutsceneSequence(name='Audio: Play SFX', enum=EDE.playSoundEffect)
def seq_playSoundEffect(sfxIndex=0, hasNode=False, nodeIndex=0, loop=False, hasDuration=False, duration=0.0, volume=1.0, startTime=0.0, isInterval=True, cutsceneDict=None):
    sfx = cutsceneDict['sounds'][sfxIndex]
    if not sfx:
        return Sequence()
    if not hasNode:
        node = None
    else:
        node = cutsceneDict['nodes'][nodeIndex]
    if not hasDuration:
        duration = 0.0
    if isInterval:
        track = SoundInterval(sound=sfx, loop=loop, duration=duration, volume=volume, startTime=startTime, node=node)
    else:
        track = Func(base.playSfx, sfx, loop, 1, volume, startTime, node)
        if hasDuration:
            track = Sequence(track, Wait(duration), Func(sfx.stop))
    return track

@cutsceneSequence(name='Audio: Stop SFX', enum=EDE.stopSoundEffect)
def seq_stopSoundEffect(sfxIndex=0, cutsceneDict=None):
    sfx = cutsceneDict['sounds'][sfxIndex]
    return Func(sfx.stop)

@cutsceneSequence(name='Audio: Play Music', enum=EDE.playMusic)
def seq_playMusic(musicIndex=0, loop=True, volume=1.0, startTime=0.0, cutsceneDict=None):
    musicCode = cutsceneDict['music'][musicIndex]
    return Func(_playCutsceneMusic, musicCode, loop, volume, startTime)

@cutsceneSequence(name='Audio: Stop Music', enum=EDE.stopMusic)
def seq_stopMusic(musicIndex=0, cutsceneDict=None):
    musicCode = cutsceneDict['music'][musicIndex]
    return Func(_stopCutsceneMusic, musicCode)
