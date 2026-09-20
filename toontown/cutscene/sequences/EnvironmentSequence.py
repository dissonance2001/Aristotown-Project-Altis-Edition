from direct.showbase import PythonUtil

from toontown.cutscene.editor.CSEditorEnums import EventDefinitionEnum as EDE
from toontown.cutscene.editor.CSEditorEnums import SubEventArgumentType as SEAT
from toontown.cutscene.CutsceneSequenceBase import cutsceneSequence

from direct.interval.IntervalGlobal import *
from panda3d.core import Point3, LVecBase3f, LVecBase4f
from panda3d.core import Fog


fogdefmap = {
    'Exponential':        Fog.MExponential,
    'ExponentialSquared': Fog.MExponentialSquared,
    'Linear':             Fog.MLinear,
}
fogmap = {}


@cutsceneSequence(name='Fog: Create', enum=EDE.createFog)
def seq_createFog(nodeIndex:            SEAT.dropdown_node = 0,
                  fogType:              SEAT.dropdown_fogType = 'Exponential',
                  expDensity:           SEAT.slider_min_zero = 0.5,
                  fogColor:             SEAT.slider_rgb = (1, 1, 1),
                  cutsceneDict:         dict = None) -> Sequence:
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError("Fog node is bad")
    if fogType == 'Linear':
        raise AttributeError("Linear Fog is not yet supported")

    def makeFog():
        fog = Fog('cutsceneFog')
        fog.setExpDensity(expDensity)
        fog.setColor(*fogColor)
        node.setFog(fog)
        fogmap[node] = fog

    return Sequence(
        Func(node.clearFog),
        Func(makeFog),
    )


@cutsceneSequence(name='Fog: Destroy', enum=EDE.destroyFog)
def seq_destroyFog(nodeIndex:            SEAT.dropdown_node = 0,
                   cutsceneDict:         dict = None) -> Sequence:
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError("Fog node is bad")
    def clearFog():
        if node in fogmap:
            node.clearFog()
            del fogmap[node]
    return Sequence(Func(clearFog))


@cutsceneSequence(name='Fog: Lerp Color', enum=EDE.setFogColor)
def seq_lerpFogColor(nodeIndex:      SEAT.dropdown_node = 0,
                       delay:        SEAT.slider_min_zero = 0.0,
                       duration:     SEAT.slider_min_zero = 1.0,
                       startColor:   SEAT.slider_rgb = (1, 1, 1),
                       endColor:     SEAT.slider_rgb = (0, 0, 0),
                       blendType:    SEAT.dropdown_blendType = 'noBlend',
                       cutsceneDict: dict = None) -> Sequence:
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError("Fog node is bad")
    def setColor(t):
        fog = fogmap.get(node)
        if fog is None:
            return
        r1, g1, b1 = startColor
        r2, g2, b2 = endColor
        fog.setColor(
            PythonUtil.lerp(r1, r2, t),
            PythonUtil.lerp(g1, g2, t),
            PythonUtil.lerp(b1, b2, t),
        )
    return Sequence(
        Wait(delay),
        LerpFunctionInterval(
            setColor, duration, blendType=blendType,
        )
    )


@cutsceneSequence(name='Fog: Lerp Density', enum=EDE.setFogDensity)
def seq_lerpFogDensity(nodeIndex:    SEAT.dropdown_node = 0,
                       delay:        SEAT.slider_min_zero = 0.0,
                       duration:     SEAT.slider_min_zero = 1.0,
                       startDensity: SEAT.slider_min_zero = 0.0,
                       endDensity:   SEAT.slider_min_zero = 0.5,
                       blendType:    SEAT.dropdown_blendType = 'noBlend',
                       cutsceneDict: dict = None) -> Sequence:
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError("Fog node is bad")
    def setDensity(t):
        fog = fogmap.get(node)
        if fog is None:
            return
        fog.setExpDensity(PythonUtil.lerp(startDensity, endDensity, t))
    return Sequence(
        Wait(delay),
        LerpFunctionInterval(
            setDensity, duration, blendType=blendType,
        )
    )


"""
Event onesies
"""


@cutsceneSequence(name='Fog: Lerp Density', enum=EDE.setFogDensity)
def seq_lerpFogDensity(nodeIndex:    SEAT.dropdown_node = 0,
                       delay:        SEAT.slider_min_zero = 0.0,
                       duration:     SEAT.slider_min_zero = 1.0,
                       startDensity: SEAT.slider_min_zero = 0.0,
                       endDensity:   SEAT.slider_min_zero = 0.5,
                       blendType:    SEAT.dropdown_blendType = 'noBlend',
                       cutsceneDict: dict = None) -> Sequence:
    node = cutsceneDict['nodes'][nodeIndex]
    if node is None:
        raise AttributeError("Fog node is bad")
    def setDensity(t):
        fog = fogmap.get(node)
        if fog is None:
            return
        fog.setExpDensity(PythonUtil.lerp(startDensity, endDensity, t))
    return Sequence(
        Wait(delay),
        LerpFunctionInterval(
            setDensity, duration, blendType=blendType,
        )
    )


@cutsceneSequence(name='HR: Spawn Television', enum=EDE.highRollerDropTelevisionSet)
def seq_hrTelevision(doSpawn: SEAT.boolean = True,
                     doDespawn: SEAT.boolean = False,
                     dropDuration: SEAT.slider_min_zero = 1.0,
                     holdDuration: SEAT.slider_min_zero = 1.0,
                     backDuration: SEAT.slider_min_zero = 1.0,
                     spawnDistance: SEAT.slider_min_zero = 30.0,
                     despawnDistance: SEAT.slider_min_zero = 30.0,
                     overrideString: SEAT.dropdown_messages = 0,
                     useOverrideString: SEAT.boolean = False,
                     showGraphic: SEAT.boolean = False,
                     hideAnyways: SEAT.boolean = False,
                     cutsceneDict: dict = None):
    """
    Arg[0]: instance
    Arg[1]: question index (if exists and is an integer, otherwise no spawn)
    """
    arguments = cutsceneDict['arguments']
    if not arguments:
        return Sequence()
    overrideStr = cutsceneDict['messages'][overrideString]

    from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
    instance: DistributedInstanceHighroller = arguments[0]
    questionIndex = None
    if len(arguments) >= 2 and type(arguments[1]) is int:
        questionIndex = arguments[1]

    return instance.getEnvironment().getTV().makeTVSequence(
        questionIndex=questionIndex,
        doSpawn=doSpawn,
        doDespawn=doDespawn,
        dropDuration=dropDuration,
        holdDuration=holdDuration,
        backDuration=backDuration,
        spawnDistance=spawnDistance,
        despawnDistance=despawnDistance,
        overrideString=overrideStr if useOverrideString else None,
        showGraphic=showGraphic,
        hideAnyways=hideAnyways
    )

@cutsceneSequence(name='HR: Set Dice', enum=EDE.highRollerSetTelevisionDice)
def seq_hrTelevisionSetDice(argumentIndex: SEAT.dropdown_arguments = 1,
                            pulseAmt: SEAT.slider_min_zero = 1.1,
                            pulseDuration: SEAT.slider_min_zero = 0.05,
                            cutsceneDict: dict = None):
    arguments = cutsceneDict['arguments']
    dice = arguments[argumentIndex]
    if not arguments or not isinstance(dice, tuple):
        return Sequence()
    from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
    instance: DistributedInstanceHighroller = arguments[0]
    tv = instance.getEnvironment().getTV()
    return Parallel(Func(tv.setDice, dice), tv.pulseDice(pulseAmt, pulseDuration, dice))

@cutsceneSequence(name='HR: Wheel Animation', enum=EDE.highRollerSpawnWheel)
def seq_hrWheel(performSpawn: SEAT.boolean = False,
                performHurt: SEAT.boolean = False,
                spinDuration: SEAT.slider_min_zero = 3.0,
                spinCount: SEAT.slider_min_zero = 3,
                cutsceneDict: dict = None):
    arguments = cutsceneDict['arguments']
    if not arguments and not (performSpawn or performHurt):
        return Sequence()
    from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
    instance: DistributedInstanceHighroller = arguments[0]
    wheel = instance.getEnvironment().getWheel()

    if performSpawn:
        return wheel.getSpawnWheelSequence()
    elif performHurt:
        return wheel.getHurtWheelSequence()
    else:
        # Spin the wheel!
        wheelDest = arguments[1]

        from toontown.instances.mercs.HighRollerEnvironment import HighRollerWheel
        if type(wheelDest) not in (HighRollerWheel.WheelDestination, int):
            raise AttributeError(f"wheelDest must be HighRollerWheel.WheelDestination or int, was {wheelDest} (type {type(wheelDest)})")
        return wheel.getSpinSequence(
            destination=wheelDest,
            duration=spinDuration,
            spinCount=round(spinCount)
        )


@cutsceneSequence(name='HR: Spawn Podiums', enum=EDE.highRollerSpawnPodiums)
def seq_hrPodiumSpawn(performSpawn: SEAT.boolean = False,
                      performDespawn: SEAT.boolean = False,
                      commercialPodium: SEAT.boolean = False,
                      cutsceneDict: dict = None):
    arguments = cutsceneDict['arguments']
    if not arguments:
        return Sequence()

    from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
    instance: DistributedInstanceHighroller = arguments[0]
    if commercialPodium:
        hrollerPodium = instance.getEnvironment().getHrollerPodiumRow()
        if performSpawn:
            return hrollerPodium.makeSpawnAnimation()
        elif performDespawn:
            return hrollerPodium.makeDespawnAnimation()
        else:
            return Sequence()

    toonPodium = instance.getEnvironment().getToonPodiumRow()
    suitPodium = instance.getEnvironment().getSuitPodiumRow()

    if performSpawn:
        return Parallel(toonPodium.makeSpawnAnimation(), suitPodium.makeSpawnAnimation())
    elif performDespawn:
        return Parallel(toonPodium.makeDespawnAnimation(), suitPodium.makeDespawnAnimation())
    else:
        return Sequence()
