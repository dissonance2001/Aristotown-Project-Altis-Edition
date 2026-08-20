from direct.showbase import PythonUtil
from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.editor.CSEditorEnums import SubEventArgumentType as SEAT
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence
from direct.interval.IntervalGlobal import *
from panda3d.core import Point3, LVecBase3f, LVecBase4f
from panda3d.core import Fog
fogdefmap = {'Exponential': Fog.MExponential, 'ExponentialSquared': Fog.MExponentialSquared, 'Linear': Fog.MLinear}
fogmap = {}

@cutsceneSequence(name='Fog: Create', enum=EDE.createFog)
def seq_createFog(nodeIndex=0, fogType='Exponential', expDensity=0.5, fogColor=(1, 1, 1), cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError('Fog node is bad')
    if fogType == 'Linear':
        raise AttributeError('Linear Fog is not yet supported')

    def makeFog():
        fog = Fog('cutsceneFog')
        fog.setExpDensity(expDensity)
        fog.setColor(*fogColor)
        node.setFog(fog)
        fogmap[node] = fog
    return Sequence(Func(node.clearFog), Func(makeFog))

@cutsceneSequence(name='Fog: Destroy', enum=EDE.destroyFog)
def seq_destroyFog(nodeIndex=0, cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError('Fog node is bad')

    def clearFog():
        if node in fogmap:
            node.clearFog()
            del fogmap[node]
    return Sequence(Func(clearFog))

@cutsceneSequence(name='Fog: Lerp Color', enum=EDE.setFogColor)
def seq_lerpFogColor(nodeIndex=0, delay=0.0, duration=1.0, startColor=(1, 1, 1), endColor=(0, 0, 0), blendType='noBlend', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError('Fog node is bad')

    def setColor(t):
        fog = fogmap.get(node)
        if fog is None:
            return
        r1, g1, b1 = startColor
        r2, g2, b2 = endColor
        fog.setColor(PythonUtil.lerp(r1, r2, t), PythonUtil.lerp(g1, g2, t), PythonUtil.lerp(b1, b2, t))
    return Sequence(Wait(delay), LerpFunctionInterval(setColor, duration, blendType=blendType))

@cutsceneSequence(name='Fog: Lerp Density', enum=EDE.setFogDensity)
def seq_lerpFogDensity(nodeIndex=0, delay=0.0, duration=1.0, startDensity=0.0, endDensity=0.5, blendType='noBlend', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError('Fog node is bad')

    def setDensity(t):
        fog = fogmap.get(node)
        if fog is None:
            return
        fog.setExpDensity(PythonUtil.lerp(startDensity, endDensity, t))
    return Sequence(Wait(delay), LerpFunctionInterval(setDensity, duration, blendType=blendType))
'\nEvent onesies\n'

@cutsceneSequence(name='Fog: Lerp Density', enum=EDE.setFogDensity)
def seq_lerpFogDensity(nodeIndex=0, delay=0.0, duration=1.0, startDensity=0.0, endDensity=0.5, blendType='noBlend', cutsceneDict=None):
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError('Fog node is bad')

    def setDensity(t):
        fog = fogmap.get(node)
        if fog is None:
            return
        fog.setExpDensity(PythonUtil.lerp(startDensity, endDensity, t))
    return Sequence(Wait(delay), LerpFunctionInterval(setDensity, duration, blendType=blendType))

@cutsceneSequence(name='HR: Spawn Television', enum=EDE.highRollerDropTelevisionSet)
def seq_hrTelevision(doSpawn=True, doDespawn=False, dropDuration=1.0, holdDuration=1.0, backDuration=1.0, spawnDistance=30.0, despawnDistance=30.0, overrideString=0, useOverrideString=False, showGraphic=False, hideAnyways=False, cutsceneDict=None):
    arguments = cutsceneDict.get('arguments', [])
    if not arguments:
        return Sequence()
    instance = arguments[0]
    environment = instance.getEnvironment() if hasattr(instance, 'getEnvironment') else instance
    television = environment.getTV() if hasattr(environment, 'getTV') else None
    if television is None:
        return Sequence()
    overrideStr = cutsceneDict['messages'][overrideString] if useOverrideString else None
    questionIndex = None
    if len(arguments) >= 2 and isinstance(arguments[1], int):
        questionIndex = arguments[1]
    return television.makeTVSequence(
        questionIndex=questionIndex,
        doSpawn=doSpawn,
        doDespawn=doDespawn,
        dropDuration=dropDuration,
        holdDuration=holdDuration,
        backDuration=backDuration,
        spawnDistance=spawnDistance,
        despawnDistance=despawnDistance,
        overrideString=overrideStr,
        showGraphic=showGraphic,
        hideAnyways=hideAnyways)


@cutsceneSequence(name='HR: Set Dice', enum=EDE.highRollerSetTelevisionDice)
def seq_hrTelevisionSetDice(argumentIndex=1, pulseAmt=1.1, pulseDuration=0.05, cutsceneDict=None):
    arguments = cutsceneDict.get('arguments', [])
    if not arguments or argumentIndex >= len(arguments):
        return Sequence()
    dice = arguments[argumentIndex]
    if not isinstance(dice, tuple):
        return Sequence()
    instance = arguments[0]
    environment = instance.getEnvironment() if hasattr(instance, 'getEnvironment') else instance
    television = environment.getTV() if hasattr(environment, 'getTV') else None
    if television is None or not hasattr(television, 'setDice'):
        return Sequence()
    pulse = television.pulseDice(pulseAmt, pulseDuration, dice) if hasattr(television, 'pulseDice') else Sequence()
    return Parallel(Func(television.setDice, dice), pulse)


@cutsceneSequence(name='HR: Wheel Animation', enum=EDE.highRollerSpawnWheel)
def seq_hrWheel(performSpawn=False, performHurt=False, spinDuration=3.0, spinCount=3, cutsceneDict=None):
    arguments = cutsceneDict.get('arguments', [])
    if not arguments:
        return Sequence()
    instance = arguments[0]
    environment = instance.getEnvironment() if hasattr(instance, 'getEnvironment') else instance
    wheel = environment.getWheel() if hasattr(environment, 'getWheel') else None
    if wheel is None:
        return Sequence()
    if performSpawn:
        return wheel.getSpawnWheelSequence()
    if performHurt:
        return wheel.getHurtWheelSequence()
    destination = arguments[1] if len(arguments) > 1 else None
    return wheel.getSpinSequence(destination=destination, duration=spinDuration, spinCount=int(round(spinCount)))


@cutsceneSequence(name='HR: Spawn Podiums', enum=EDE.highRollerSpawnPodiums)
def seq_hrPodiumSpawn(performSpawn=False, performDespawn=False, commercialPodium=False, cutsceneDict=None):
    arguments = cutsceneDict.get('arguments', [])
    if not arguments:
        return Sequence()
    instance = arguments[0]
    environment = instance.getEnvironment() if hasattr(instance, 'getEnvironment') else instance
    if commercialPodium:
        podium = environment.getHrollerPodiumRow() if hasattr(environment, 'getHrollerPodiumRow') else None
        if podium is None:
            return Sequence()
        if performSpawn:
            return podium.makeSpawnAnimation()
        if performDespawn:
            return podium.makeDespawnAnimation()
        return Sequence()
    toonPodium = environment.getToonPodiumRow() if hasattr(environment, 'getToonPodiumRow') else None
    suitPodium = environment.getSuitPodiumRow() if hasattr(environment, 'getSuitPodiumRow') else None
    if toonPodium is None or suitPodium is None:
        return Sequence()
    if performSpawn:
        return Parallel(toonPodium.makeSpawnAnimation(), suitPodium.makeSpawnAnimation())
    if performDespawn:
        return Parallel(toonPodium.makeDespawnAnimation(), suitPodium.makeDespawnAnimation())
    return Sequence()
