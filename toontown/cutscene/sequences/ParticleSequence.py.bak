from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence
from direct.interval.IntervalGlobal import Func, LerpPosInterval, Sequence, Wait
from panda3d.core import LVecBase3f


@cutsceneSequence(name='Run Particle System', enum=EDE.particleSystemRun)
def seq_particleSystemRun(particleIndex=0, duration=5.0, delay=0,
                          parentIndex=0, renderParentIndex=0,
                          leaveItGoingForever=False, cutsceneDict=None):
    particles = cutsceneDict.get('particles', ())
    nodes = cutsceneDict.get('nodes', ())
    if particleIndex < 0 or particleIndex >= len(particles):
        return Sequence()
    if parentIndex < 0 or parentIndex >= len(nodes):
        return Sequence()
    if renderParentIndex < 0 or renderParentIndex >= len(nodes):
        return Sequence()
    particleSystem = particles[particleIndex]
    parent = nodes[parentIndex]
    renderParent = nodes[renderParentIndex]
    if particleSystem is None or parent is None or renderParent is None:
        return Sequence()
    track = Sequence(
        Wait(delay),
        Func(particleSystem.start, parent=parent, renderParent=renderParent),
        Func(particleSystem.softStart),
        Wait(duration))
    if not leaveItGoingForever:
        track.append(Func(particleSystem.softStop))
    return track


@cutsceneSequence(name='Move Particle System Pos', enum=EDE.moveParticleSystemPos)
def seq_moveParticleSystemPos(particleIndex=0, duration=0, pos=(0, 0, 0),
                              delay=0, blendType='easeInOut',
                              startPos=(0, 0, 0), useStartPos=0,
                              cutsceneDict=None):
    particles = cutsceneDict.get('particles', ())
    if particleIndex < 0 or particleIndex >= len(particles):
        return Sequence()
    particleSystem = particles[particleIndex]
    if particleSystem is None:
        return Sequence()
    if useStartPos:
        startPos = LVecBase3f(*startPos)
    else:
        startPos = None
    return Sequence(
        Wait(delay),
        LerpPosInterval(
            particleSystem,
            duration=duration,
            blendType=blendType,
            startPos=startPos,
            pos=LVecBase3f(*pos)))
