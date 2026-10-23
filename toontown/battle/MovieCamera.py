import random
from panda3d.core import *
from toontown.suit import SuitBase
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.SuitBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleGlobals, MovieUtil
from direct.task.Task import Task
from . import PlayByPlayText
notify = DirectNotifyGlobal.directNotify.newCategory('MovieCamera')

def chooseHealShot(heals, attackDuration):
    openShot = chooseHealOpenShot(heals, attackDuration)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseHealCloseShot(heals, openDuration, openName, attackDuration)
    track = Sequence(openShot, closeShot)
    return track


def chooseHealOpenShot(heals, attackDuration):
    numHeals = len(heals)
    av = None
    duration = 2.8
    shotChoices = [toonGroupShot]
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseHealMidShot(heals, attackDuration):
    numHeals = len(heals)
    av = None
    duration = 2.1
    shotChoices = [toonGroupHighShot]
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseHealCloseShot(heals, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    shotChoices = [toonGroupShot]
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseTrapShot(traps, attackDuration, battle, enterDuration = 0, exitDuration = 0):
    enterShot = chooseNPCEnterShot(traps, enterDuration)
    openShot = chooseTrapOpenShot(traps, attackDuration, battle)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseTrapCloseShot(traps, openDuration, battle, openName, attackDuration)
    exitShot = chooseNPCExitShot(traps, exitDuration)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseTrapOpenShot(traps, attackDuration, battle):
    numTraps = len(traps)
    av = None
    duration = 3.0
    shotChoices = [allGroupLowShot]
    track = random.choice(shotChoices)(*[av, duration, battle])
    return track


def chooseTrapCloseShot(traps, openDuration, battle, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    shotChoices = [allGroupLowShot]
    track = random.choice(shotChoices)(*[av, duration, battle])
    return track


def chooseLureShot(lures, attackDuration, battle, enterDuration = 0.0, exitDuration = 0.0):
    enterShot = chooseNPCEnterShot(lures, enterDuration)
    openShot = chooseLureOpenShot(lures, attackDuration, battle)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseLureCloseShot(lures, openDuration, battle, openName, attackDuration)
    exitShot = chooseNPCExitShot(lures, exitDuration)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseLureOpenShot(lures, attackDuration, battle):
    numLures = len(lures)
    av = None
    duration = 3.0
    shotChoices = [allGroupLowShot]
    track = random.choice(shotChoices)(*[av, duration, battle])
    return track


def chooseLureCloseShot(lures, openDuration, battle, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    hasTrainTrackTrap = False
    battle = lures[0]['battle']
    for suit in battle.suits:
        if hasattr(suit, 'battleTrap') and suit.battleTrap == UBER_GAG_LEVEL_INDEX:
            hasTrainTrackTrap = True

    shotChoices = [allGroupLowShot]
    track = random.choice(shotChoices)(*[av, duration, battle])
    return track

def avatarTrainShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 0, -7, 1 + avatar.getHeight(), 0, 0, 0, duration, 'avatarTrainShot')

def chooseSoundShot(sounds, targets, attackDuration, battle, enterDuration = 0.0, exitDuration = 0.0):
    enterShot = chooseNPCEnterShot(sounds, enterDuration)
    openShot = chooseSoundOpenShot(sounds, targets, attackDuration, battle)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseSoundCloseShot(sounds, targets, openDuration, openName, attackDuration, battle)
    exitShot = chooseNPCExitShot(sounds, exitDuration)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseSoundOpenShot(sounds, targets, attackDuration, battle):
    duration = 3.1
    isUber = 0
    for sound in sounds:
        if sound['level'] == 7:
            isUber = 1
            duration = 5.0

    numSounds = len(sounds)
    av = None
    if numSounds == 1:
        av = sounds[0]['toon']
        shotChoices = [avatarCloseUpThreeQuarterRightShot, allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    elif numSounds >= 2 and numSounds <= 4:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    else:
        notify.error('Bad number of sounds: %s' % numSounds)
    return track

def cameraActorShotInsurance(parent, name = 'cameraActorShot'):
    path = 'phase_3.5/models/misc/camera_actor'
    cameraActor = Actor.Actor(path)
    cameraActor.reparentTo(parent)
    camera = cameraActor
    track = Sequence(
        Func(camera.setPosHpr, 0.0, 5.95944, 9.19824, 180.0, -15.15766, 0.0), Parallel(LerpPosInterval(camera, .7, VBase3(0.0, 8.8096, 7.77317)), LerpHprInterval(camera, .7, VBase3(180.0, 0.0, 0.0))),
        Parallel(LerpPosInterval(camera, .5, VBase3(-0.0, -10.0, 10.10513)),
                 LerpHprInterval(camera, .5, VBase3(0.0, -10.49376, 0.0))),
        Func(cameraActor.cleanup),
        name=name)
    return track

def cameraActorShot(parent, anim, remainTime = 0.0, name = 'cameraActorShot'):
    previousParent = camera.getParent()
    path = 'phase_3.5/models/misc/camera_actor'
    cameraActor = Actor.Actor(path, {anim: path + '-' + anim})
    node = cameraActor.find('**/CameraBone')
    track = Sequence(
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(camera.setPosHpr, 0, -1, 2, 0, 0, 0),
        ActorInterval(cameraActor, anim),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime - cameraActor.getDuration(anim)),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, 0.0, -15.0, 10.0, 0, -20, 0),
        Func(cameraActor.cleanup),
        name=name
    )
    return track


def cameraActorShotHighRoller(parent, anim, remainTime = 0.0, name = 'cameraActorShot'):
    previousParent = camera.getParent()
    path = 'phase_3.5/models/misc/camera_actor'
    cameraActor = Actor.Actor(path, {anim: path + '-' + anim})
    node = cameraActor.find('**/CameraBone')
    track = Sequence(
        Func(cameraActor.reparentTo, parent),
        #Func(camera.reparentTo, node),
        Func(camera.setPosHpr, 0, -1, 2, 0, 0, 0),
        ActorInterval(cameraActor, anim),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime),
        Func(camera.setPosHpr, 0.0, -10.0, 10.0, 0, -20, 0),
        Func(cameraActor.cleanup),
        name=name
    )
    return track

def cameraActorShot2(parent, anim, remainTime = 0.0, name = 'cameraActorShot'):
    numSuits = len(battle.activeSuits)
    previousParent = camera.getParent()
    path = 'phase_3.5/models/misc/camera_actor'
    cameraActor = Actor.Actor(path, {anim: path + '-' + anim})
    node = cameraActor.find('**/CameraBone')
    track = Sequence(
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(cameraActor.reparentTo, parent),
        Func(camera.setPosHpr, 0, -29, -12, 180, 0, 0),
        Func(cameraActor.reparentTo, parent),
        ActorInterval(cameraActor, anim, startTime=0, endTime=1.97),
        Wait(1.49),
        Func(camera.setPosHpr, 0, -34.5, -3.5, 180, 0, 0),
        Func(cameraActor.reparentTo, parent),
        ActorInterval(cameraActor, anim, startTime=3.46, endTime=6.25),
        Func(cameraActor.reparentTo, parent),
        Func(camera.setPosHpr, 0, -22.5, -4, 180, 0, 0),
        Wait(1.0),
        Func(cameraActor.reparentTo, parent),
        ActorInterval(cameraActor, anim, startTime=7.25),
        Func(cameraActor.reparentTo, parent),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, node.getX(), node.getY(), node.getZ(), *node.getHpr()),
        Func(cameraActor.cleanup),
        name=name
    )
    return track

def cameraActorShot3(parent, anim, remainTime = 0.0, name = 'cameraActorShot'):
    battle = parent
    numSuits = len(battle.activeSuits)
    previousParent = camera.getParent()
    path = 'phase_3.5/models/misc/camera_actor'
    cameraActor = Actor.Actor(path, {anim: path + '-' + anim})
    node = cameraActor.find('**/CameraBone')
    track = Sequence(
        Wait(1),
        Func(camera.setPosHpr, 0, -34.5, -3.5, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=3.46, endTime=6.25),
        Func(camera.setPosHpr, 0, -22.5, -4, 0, 0, 0),
        Wait(1.0),
        ActorInterval(cameraActor, anim, startTime=7.25),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, node.getX(), node.getY(), node.getZ(), *node.getHpr()),
        Func(cameraActor.cleanup),
        name=name
    )
    track3 = Sequence(
        Wait(1),
        Func(camera.setPosHpr, 5, -34.5, -3.5, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=3.46, endTime=6.25),
        Func(camera.setPosHpr, 5, -22.5, -4, 0, 0, 0),
        Wait(1.0),
        ActorInterval(cameraActor, anim, startTime=7.25),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, node.getX(), node.getY(), node.getZ(), *node.getHpr()),
        Func(cameraActor.cleanup),
        name=name
    )
    track2 = Sequence(
        Wait(1),
        Func(camera.setPosHpr, 2.5, -34.5, -3.5, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=3.46, endTime=6.25),
        Func(camera.setPosHpr, 2.5, -22.5, -4, 0, 0, 0),
        Wait(1.0),
        ActorInterval(cameraActor, anim, startTime=7.25),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, node.getX(), node.getY(), node.getZ(), *node.getHpr()),
        Func(cameraActor.cleanup),
        name=name
    )
    track4 = Sequence(
        Wait(1),
        Func(camera.setPosHpr, 7.5, -34.5, -3.5, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=3.46, endTime=6.25),
        Func(camera.setPosHpr, 7.5, -22.5, -4, 0, 0, 0),
        Wait(1.0),
        ActorInterval(cameraActor, anim, startTime=7.25),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, node.getX(), node.getY(), node.getZ(), *node.getHpr()),
        Func(cameraActor.cleanup),
        name=name
    )
    track5 = Sequence(
        Wait(1),
        Func(camera.setPosHpr, 10, -34.5, -3.5, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=3.46, endTime=6.25),
        Func(camera.setPosHpr, 10, -25.5, -4, 0, 0, 0),
        Wait(1.0),
        ActorInterval(cameraActor, anim, startTime=7.25),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, node.getX(), node.getY(), node.getZ(), *node.getHpr()),
        Func(cameraActor.cleanup),
        name=name
    )
    track6 = Sequence(
        Wait(1),
        Func(camera.setPosHpr, 12.5, -37, -3.5, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=3.46, endTime=6.25),
        Func(camera.setPosHpr, 12.5, -22.5, -4, 0, 0, 0),
        Wait(1.0),
        ActorInterval(cameraActor, anim, startTime=7.25),
        Func(cameraActor.pose, anim, cameraActor.getNumFrames(anim) - 1),
        Wait(remainTime),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, node.getX(), node.getY(), node.getZ(), *node.getHpr()),
        Func(cameraActor.cleanup),
        name=name
    )
    if numSuits == 1:
        return track
    elif numSuits == 2:
        return track2
    elif numSuits == 3:
        return track3
    elif numSuits == 4:
        return track4
    elif numSuits == 5:
        return track5
    elif numSuits == 6:
        return track6
    else:
        return track2


def chooseSoundCloseShot(sounds, targets, openDuration, openName, attackDuration, battle):
    numSuits = len(targets)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = targets[0]['suit']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot,
         avatarBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    elif numSuits >= 2 and numSuits <= BattleGlobals.MaxBattleAvatars:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    return track


def chooseThrowShot(throws, suitThrowsDict, attackDuration, battle, enterDuration=0, exitDuration=0):
    enterShot = chooseNPCEnterShot(throws, enterDuration)
    openShot = chooseThrowOpenShot(throws, suitThrowsDict, attackDuration, battle)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    exitShot = chooseNPCExitShot(throws, exitDuration)
    closeShot = chooseThrowCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration, battle)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseThrowOpenShot(throws, suitThrowsDict, attackDuration, battle):
    numThrows = len(throws)
    av = None
    duration = 3.0
    if numThrows == 1:
        av = throws[0]['toon']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot,
         avatarBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    elif numThrows >= 2 and numThrows <= 4:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    else:
        notify.error('Bad number of throws: %s' % numThrows)
    return track


def chooseThrowCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration, battle):
    numSuits = len(suitThrowsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[list(suitThrowsDict.keys())[0]]
        shotChoices = [avatarCloseUpThrowShot,
                       allGroupLowShot2, 
         avatarCloseUpThreeQuarterLeftShot,
         suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    elif numSuits >= 2 and numSuits <= BattleGlobals.MaxBattleAvatars or numSuits == 0:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    return track


def chooseSquirtShot(squirts, suitSquirtsDict, attackDuration, battle):
    openShot = chooseSquirtOpenShot(squirts, suitSquirtsDict, attackDuration, battle)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseSquirtCloseShot(squirts, suitSquirtsDict, openDuration, openName, attackDuration, battle)
    track = Sequence(openShot, closeShot)
    return track


def chooseSquirtOpenShot(squirts, suitSquirtsDict, attackDuration, battle):
    numSquirts = len(squirts)
    av = None
    duration = 3.0
    if numSquirts == 1:
        av = squirts[0]['toon']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot,
         avatarBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    elif numSquirts >= 2 and numSquirts <= 4:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    else:
        notify.error('Bad number of squirts: %s' % numSquirts)
    return track


def chooseSquirtCloseShot(squirts, suitSquirtsDict, openDuration, openName, attackDuration, battle):
    numSuits = len(suitSquirtsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[list(suitSquirtsDict.keys())[0]]
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterLeftShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    elif numSuits >= 2 and numSuits <= BattleGlobals.MaxBattleAvatars:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    return track

def chooseZapShot(zaps, attackDuration, enterDuration=0.0, exitDuration=0.0):
    enterShot = chooseNPCEnterShot(zaps, enterDuration)
    exitShot = chooseNPCExitShot(zaps, exitDuration)
    fullShot = allGroupHighShot(None, attackDuration)
    track = Sequence(enterShot, fullShot, exitShot)
    return track


def chooseZapOpenShot(zaps, attackDuration):
    numLures = len(zaps)
    av = None
    duration = 3.0
    shotChoices = [avatarBehindShot]
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseZapCloseShot(zaps, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    hasTrainTrackTrap = False
    battle = zaps[0]['battle']
    shotChoices = [avatarBehindShot]
    track = random.choice(shotChoices)(*[av, duration, battle])
    return track


def chooseDropShot(drops, suitDropsDict, attackDuration, battle, enterDuration=0.0, exitDuration=0.0):
    enterShot = chooseNPCEnterShot(drops, enterDuration)
    exitShot = chooseNPCExitShot(drops, exitDuration)
    if any(drop['level'] > 0 for drop in drops):
        fullShot = allGroupHighShot(None, attackDuration)
        track = Sequence(enterShot, fullShot, exitShot)
    else:
        openShot = chooseDropOpenShot(drops, suitDropsDict, attackDuration, battle)
        openDuration = openShot.getDuration()
        openName = openShot.getName()
        closeShot = chooseDropCloseShot(drops, suitDropsDict, openDuration, openName, attackDuration, battle)
        track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseDropOpenShot(drops, suitDropsDict, attackDuration, battle):
    numDrops = len(drops)
    av = None
    duration = 3.0
    if numDrops == 1:
        av = drops[0]['toon']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         allGroupLowShot2, 
         avatarBehindShot,
         suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    elif numDrops >= 2 and numDrops <= 4 or numDrops == 0:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    else:
        notify.error('Bad number of drops: %s' % numDrops)
    return track


def chooseDropCloseShot(drops, suitDropsDict, openDuration, openName, attackDuration, battle):
    numSuits = len(suitDropsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[list(suitDropsDict.keys())[0]]
        shotChoices = [avatarCloseUpThrowShot,
                       allGroupLowShot2, 
         avatarCloseUpThreeQuarterLeftShot,
         suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    elif numSuits >= 2 and numSuits <= BattleGlobals.MaxBattleAvatars or numSuits == 0:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        track = random.choice(shotChoices)(*[av, duration, battle])
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    return track


def chooseNPCEnterShot(enters, entersDuration):
    av = None
    duration = entersDuration
    shotChoices = [toonGroupShot]
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseNPCExitShot(exits, exitsDuration):
    av = None
    duration = exitsDuration
    shotChoices = [toonGroupShot]
    track = random.choice(shotChoices)(*[av, duration])
    return track

def randomTargetGroupShot(targets, suit, duration, battle):
    totalHeight = 0
    actorCount = 0

    for target in targets:
        if 'toon' in target:
            actor = target['toon']

        elif 'suit' in target:
            actor = target['suit']

        else:
            continue

        totalHeight += actor.getHeight()
        actorCount += 1

    if actorCount <= 0:
        return Sequence(Wait(duration))

    avgHeight = float(totalHeight) / actorCount * 0.75

    suitPos, origHpr = battle.getActorPosHpr(suit)

    x = 1 + random.random() * 3

    if suitPos.getX() > 0:
        x = -x

    if random.random() > 0.5:
        y = 3 + random.random()
        z = avgHeight + random.random() * 6

    else:
        y = 11 + random.random() * 2
        z = 13 + random.random() * 2

    focalPoint = Point3(0, -4, avgHeight)

    return focusShot(x, y, z, duration, focalPoint)

def getAttackTargetActor(target):
    if not target:
        return None

    if 'toon' in target[0]:
        return target[0]['toon']

    if 'suit' in target[0]:
        return target[0]['suit']

    return None

def chooseSuitShot(attack, attackDuration, cheat=0):
    duration = attackDuration
    if duration < 0:
        duration = 1e-06
    diedTrack = None
    groupStatus = attack['group']
    target = attack['target']
    targetDicts = attack['target']
    playRate: float = attack['playRate']
    deadToons = []

    for targetDict in targetDicts:
        died = targetDict.get('died', 0)

        if died != 0 and 'toon' in targetDict:
            deadToons.append(targetDict['toon'])

    if len(deadToons) > 0:
        pbpText = attack['playByPlayText']
        diedTextList = []
        for toon in deadToons:
            pbpText = attack['playByPlayText']
            diedTextList.append(toon.getName() + ' was defeated!')

        diedTrack = pbpText.getToonsDiedInterval(diedTextList, duration)
    suit = attack['suit']
    name = attack['name']
    battle = attack['battle']

    # Chainsaw Consultant's dedicated Corporate Clash CTSCs own the complete
    # camera track.  Do not stack Altis's generic Suit camera on top of them.
    chainsawCtscNames = (
        'ChainsawCoreRevvingUp',
        'ChainsawCoreWhipsaw',
        'ChainsawCorePhaseTwo',
        'ChainsawCorePhaseThree',
        'ChainsawCoreChainLinked',
        'ChainsawCoreScabbard',
        'ChainsawCoreSparkPlug',
        'ChainsawCoreThrottle',
        'ChainsawCoreThrottleTwo',
        'ChainsawCoreDeadwood',
    )
    if (name in chainsawCtscNames or
            name.startswith('ChainsawCoreOffboarding') or
            name.startswith('ChainsawCoreLayoffs')):
        return Sequence(Wait(attackDuration))
    camTrack = Sequence()

    def defaultCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
        if attack['group'] == ATK_TGT_SINGLE:
            targetActor = getAttackTargetActor(target)

            if targetActor is None:
                return Sequence()

            if 'suit' in target[0]:
                defenderString = 'suit'
            else:
                defenderString = 'toon'

            return randomAttackCam(attack['suit'], targetActor, attack['battle'], attackDuration, openShotDuration, 'suit', defenderString)

        return randomGroupAttackCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)

    # def defaultCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
    #     return randomAttackCam(attack['suit'], target[0]['toon'], attack['battle'], attackDuration,
    #                                openShotDuration, 'suit')

    def fromBehindCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
        return fromBehindGroupCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)

    def managerCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
        return randomManagerCheatCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)

    def shake_camera(task):
        camera = base.camera
        shake_intensity = 0.5  # Adjust for desired shake intensity
        x_shake = random.uniform(-shake_intensity, shake_intensity)
        y_shake = random.uniform(-shake_intensity, shake_intensity)
        z_shake = random.uniform(-shake_intensity, shake_intensity)
        camera.setPosHpr(10, 0, 10, 115, -30, 0)
        camera.setPos(camera.getPos() + Vec3(+ x_shake, y_shake, z_shake))
        return task.cont
    
    def shake_camera_sacrifice(task):
        camera = base.camera
        shake_intensity = 0.5  # Adjust for desired shake intensity
        x_shake = random.uniform(-shake_intensity, shake_intensity)
        y_shake = random.uniform(-shake_intensity, shake_intensity)
        z_shake = random.uniform(-shake_intensity, shake_intensity)
        camera.setPosHpr(20, -10, 15, 50, -30, 0)
        camera.setPos(camera.getPos() + Vec3(+ x_shake, y_shake, z_shake))
        return task.cont

    def shake_camera_high_pressure(task):
        camera = base.camera
        shake_intensity = 0.75  # Adjust for desired shake intensity
        x_shake = random.uniform(-shake_intensity, shake_intensity)
        y_shake = random.uniform(-shake_intensity, shake_intensity)
        z_shake = random.uniform(-shake_intensity, shake_intensity)
        camera.setPosHpr(0.0, -20.0, 10.0, 0, -20, 0)
        camera.setPos(camera.getPos() + Vec3(+ x_shake, y_shake, z_shake))
        return task.cont

    def shake_camera_mandatory_toll(task):
        camera = base.camera
        shake_intensity = 0.5  # Adjust for desired shake intensity
        x_shake = random.uniform(-shake_intensity, shake_intensity)
        y_shake = random.uniform(-shake_intensity, shake_intensity)
        z_shake = random.uniform(-shake_intensity, shake_intensity)
        camera.setPosHpr(5, 0, .5, 155, 35, 0)
        camera.setPos(camera.getPos() + Vec3(+ x_shake, y_shake, z_shake))
        return task.cont

    def shake_camera_advancement(task):
        camera = base.camera
        shake_intensity = 0.5  # Adjust for desired shake intensity
        x_shake = random.uniform(-shake_intensity, shake_intensity)
        y_shake = random.uniform(-shake_intensity, shake_intensity)
        z_shake = random.uniform(-shake_intensity, shake_intensity)
        camera.setPosHpr(0.0, -10.0, 10.0, 0, -20, 0)
        camera.setPos(camera.getPos() + Vec3(+ x_shake, y_shake, z_shake))
        return task.cont

    def shake_camera_tremor(task):
        camera = base.camera
        shake_intensity = 0.25  # Adjust for desired shake intensity
        x_shake = random.uniform(-shake_intensity, shake_intensity)
        y_shake = random.uniform(-shake_intensity, shake_intensity)
        z_shake = random.uniform(-shake_intensity, shake_intensity)
        camera.setPosHpr(10, 0, 10, 115, -30, 0)
        camera.setPos(camera.getPos() + Vec3(x_shake, y_shake, z_shake))
        return task.cont

    match name:
        case 'AcidRain':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'Aftershock' | 'Quake':
            quake = 1
            camTrack.append(suitCameraShakeShot(attackDuration, 1.0, quake=quake))
        case 'Audit' | 'Calculate' | 'Tabulate':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'Bash':
            camTrack.append(Sequence(defaultCamera(openShotDuration=1.75, attackDuration=1.75), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(2.0),
                                     Func(taskMgr.remove, 'camera_shake'), Wait(attackDuration - 3.75)))
        case 'Beguile':
            camTrack.append(heldRelativeShot(suit, 5.0, 12.5, 10.0, -210.0, -20.0, 0.0, 2.1))
            camTrack.append(defaultCamera(openShotDuration=0.0, attackDuration=attackDuration - 2.1))
            #camTrack.append(defaultCamera(openShotDuration=2.1))
        case 'Bite':
            camTrack.append(defaultCamera(openShotDuration=2.8 / 1.5))
        case 'BlueChip' | 'CoinToss':
            camTrack.append(defaultCamera(openShotDuration=2.45))
        case 'BounceCheck':
            if groupStatus == ATK_TGT_GROUP:
                camTrack.append(defaultCamera())
            else:
                camTrack.append(randomSplitShot(suit, target[0]['toon'], battle, attackDuration))
        case 'BounceRate':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'BrainStorm' | 'Forecast':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'Breakthrough':
            camTrack.append(defaultCamera(openShotDuration=3.5))
        case 'BuzzWord':
            camTrack.append(defaultCamera(openShotDuration=3.1))
        case 'Canned':
            camTrack.append(defaultCamera(openShotDuration=2.9 / 1.3))
        case 'CashGrab' | 'Embezzle' | 'PennyPinch' | 'PickPocket' | 'StolenScene':
            camTrack.append(allGroupLowShot(suit, attackDuration, battle))
        case 'Chomp':
            camTrack.append(defaultCamera(openShotDuration=2.8 / 1.5))
        case 'CigarSmoke' | 'SmokeAndMirrors':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'ClipOnTie' | 'DoubleWindsor' | 'HalfWindsor' | 'PowerTie':
            if groupStatus == ATK_TGT_GROUP:
                camTrack.append(defaultCamera())
            else:
                camTrack.append(randomSplitShot(suit, target[0]['toon'], battle, attackDuration))
        case 'CloseTheLoop':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'CloudStorage':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'Crunch' | 'MudSling':
            if groupStatus == ATK_TGT_GROUP:
                camTrack.append(defaultCamera())
            else:
                camTrack.append(randomSplitShot(suit, target[0]['toon'], battle, attackDuration))
        case 'DataBreach':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'DataCorruption':
            camTrack.append(defaultCamera(openShotDuration=1.75))
        case 'Demotion':
            camTrack.append(defaultCamera(openShotDuration=1.7))
        case 'DenialOfService':
            camTrack.append(defaultCamera(openShotDuration=0.75))
        case 'Disassemble':
            camTrack.append(defaultCamera(openShotDuration=1.75))
        case 'DiskScratch':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'DoubleTalk':
            camTrack.append(defaultCamera(openShotDuration=3.9 / playRate))
        case 'Downsize':
            camTrack.append(defaultCamera(openShotDuration=1.8))
        case 'ElectrostaticEnergy':
            camTrack.append(defaultCamera(openShotDuration=1.75))
        case 'Encrypt':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'EvictionNotice':
            camTrack.append(defaultCamera(openShotDuration=3.0 / playRate))
        case 'EvilEye':
            camTrack.append(defaultCamera(openShotDuration=2.7 / playRate))
        case 'DoubleCross':
            camTrack.append(defaultCamera(openShotDuration=2.5)) # Double Cross movie's play rate is not flexible.  TODO: Make it flexible.
        case 'FallingKnife':
            camTrack.append(randomOverShoulderShot(suit, target[0]['toon'], battle, attackDuration, focus='suit')) # Merely for the first part of the camera track.  The other part will be handled in the attack method itself.
        case 'Filibuster':
            camTrack.append(defaultCamera(openShotDuration=3.0 / playRate))
        case 'FillWithLead':
            camTrack.append(defaultCamera(openShotDuration=3.3 / playRate))
        case 'FingerWag':
            camTrack.append(defaultCamera(openShotDuration=2.2))
        case 'Fired':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'FiveOClockShadow':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'FloodTheMarket':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'FountainPen':
            camTrack.append(defaultCamera(openShotDuration=1.25))
        case 'FreezeAssets':
            camTrack.append(defaultCamera(openShotDuration=1.7 / playRate))
        case 'GlowerPower':
            camTrack.append(defaultCamera(openShotDuration=1.4))
        case 'GoldDust':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'GoldRush':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'GuiltTrip':
            camTrack.append(defaultCamera(openShotDuration=0.9))
        case 'HangUp':
            camTrack.append(defaultCamera(openShotDuration=(66.0/24.0) / playRate))
        case 'HeadShrink':
            camTrack.append(defaultCamera(openShotDuration=1.3 / playRate))
        case 'HostileTakeover':
            camTrack.append(defaultCamera(openShotDuration=1.0 / playRate))
        case 'HotAir':
            camTrack.append(defaultCamera(openShotDuration=2.0 / playRate))
        case 'Inject':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'Jargon':
            camTrack.append(defaultCamera(openShotDuration=3.5 / playRate))
        case 'Legalese':
            camTrack.append(defaultCamera(openShotDuration=3.0 / playRate))
        case 'Liquidate':
            camTrack.append(randomSplitShot(suit, target[0]['toon'], battle, attackDuration))
        case 'MarketCrash' | 'Newspaper':
            camTrack.append(defaultCamera(openShotDuration=2.7 / playRate))
        case 'MindBlow':
            camTrack.append(defaultCamera(openShotDuration=3.5 / playRate))
        case 'MoneyTalks':
            camTrack.append(defaultCamera(openShotDuration=3.5 / playRate))
        case 'MumboJumbo':
            camTrack.append(defaultCamera(openShotDuration=3.0 / playRate))
        case 'MysteriousDisappearance':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'NickelAndDime':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'Novel' | 'ThrowBook':
            camTrack.append(defaultCamera(openShotDuration=2.9 / playRate))
        case 'Overload':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'ParadigmShift':
            camTrack.append(defaultCamera(openShotDuration=1.01))
        case 'PeckingOrder':
            camTrack.append(defaultCamera(openShotDuration=2.8 / playRate))
        case 'PinkSlip':
            camTrack.append(defaultCamera(openShotDuration=2.8 / playRate))
        case 'PlayHardball':
            camTrack.append(defaultCamera(openShotDuration=(70.0 / 24.0) / playRate))
        case 'PoundKey':
            camTrack.append(defaultCamera(openShotDuration=(46.0 / 24.0) / playRate))
        case 'PowerTrip':
            camTrack.append(defaultCamera(openShotDuration=0.9))
        case 'Quash':
            camTrack.append(defaultCamera(openShotDuration=1.0))
        case 'RazzleDazzle':
            camTrack.append(defaultCamera(openShotDuration=2.2))
        case 'ReArrange' | 'ReOrg':
            camTrack.append(defaultCamera(openShotDuration=1.1))
        case 'RecordBreaker':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'RedTape':
            camTrack.append(defaultCamera(openShotDuration=(70.0 / 24.0) / playRate))
        case 'Reprogram':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'RestrainingOrder':
            camTrack.append(defaultCamera(openShotDuration=2.8 / playRate))
        case 'Rolodex':
            camTrack.append(defaultCamera(openShotDuration=3.5 / playRate))
        case 'RubOut':
            camTrack.append(defaultCamera(openShotDuration=(42.0 / 24.0) / playRate))
        case 'RubberStamp':
            camTrack.append(defaultCamera(openShotDuration=(52.0 / 24.0) / playRate))
        case 'Sacked':
            camTrack.append(defaultCamera(openShotDuration=2.9 / playRate))
        case 'SandTrap':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'Schmooze' | 'TestSchmooze':
            camTrack.append(defaultCamera(openShotDuration=3.0 / playRate))
        case 'Shake':
            camTrack.append(suitCameraShakeShot(attackDuration, 0.5))
        case 'ShortSqueeze':
            camTrack.append(randomSplitShot(suit, target[0]['toon'], battle, attackDuration))
        case 'Shred':
            camTrack.append(defaultCamera(openShotDuration=(80.0 / 24.0) / playRate))
        case 'SongAndDance':
            camTrack.append(defaultCamera(openShotDuration=4.1))
        case 'Spin':
            camTrack.append(defaultCamera(openShotDuration=1.7))
        case 'Stomper':
            camTrack.append(defaultCamera(openShotDuration=1.0))
        case 'StumpSpeech':
            camTrack.append(defaultCamera())
        case 'Synergy':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'TeeOff':
            camTrack.append(defaultCamera(openShotDuration=2.9))
        case 'TickingTimeBomb':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'Tremor':
            camTrack.append(suitCameraShakeShot(attackDuration, 0.25))
        case 'VersionControl':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'VoodooMagic':
            camTrack.append(defaultCamera(openShotDuration=0.75))
        case 'Watercooler':
            camTrack.append(defaultCamera(openShotDuration=3.0))
        case 'Withdrawal':
            camTrack.append(defaultCamera(openShotDuration=1.0))
        case 'WriteOff':
            camTrack.append(defaultCamera(openShotDuration=(65.0 / 24.0) / playRate))
            # redd heir wing cheats
        case 'ReddLiquidationSale':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'ReddPeckingOrder':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'ReddAutoRepair':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, attackDuration))
            # witness stand-in cheats
        case 'WSIJuryNotice':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'WSICeaseAndDesist':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'ArbitratorObjection':
            camTrack.append(randomActorShot(suit, battle, 2.0, 'suit'))
            camTrack.append(heldShot(10.0, 0.0, 10.0, 115.0, -30.0, 0.0, attackDuration - 2.0))
        case 'ArbitratorPaperFiling':
            camTrack.append(Sequence(defaultCamera(openShotDuration=2.5, attackDuration=2.5), Wait(attackDuration - 2.5)))
        case 'ArbitratorWhirlwind':
            camTrack.append(randomActorShot(suit, battle, 0.5, 'suit'))
            camTrack.append(heldShot(10.0, 0.0, 10.0, 120.0, -30.0, 0.0, attackDuration - 0.5))
        case 'ArbitratorThrowBook':
            camTrack.append(heldRelativeShot(suit, 0.0, 8.8096, 7.77317, -180.0, 0.0, 0.0, 1.7))
            camTrack.append(moveShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, 1.0))
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 2.7))
        case 'ArbitratorThrowBook2' | 'ArbitratorThrowBook3' | 'ArbitratorThrowBook4' | 'ArbitratorThrowBook5':
            camTrack.append(heldRelativeShot(suit, 0.0, 8.8096, 7.77317, -180.0, 0.0, 0.0, 1.7))
            camTrack.append(moveShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 3.2))
            # litigator cheats
        case 'LitigatorSnapSoak':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'LitigatorSnapBindings':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'LitigatorSnap':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'LitigatorSnapStenographer':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'LitigatorBayouBash':
            camTrack.append(Sequence(motionShot(.5, 9.0, suit.height - 1, 175, 0, 0.0, 0, suit), moveCameraOnly(-1.0, 9.0, suit.height - 1, 1, suit, h=190, p=0, startH=175, startP=0), Wait(attackDuration - 1)))
        case 'LitigatorBayouBellow':
            camTrack.append(Sequence(cameraActorShot(suit, 'litigator-bellow', attackDuration)))
            # stenographer cheats
        case 'StenographerSanctionBindings':
            if attackDuration > 2:
                camTrack.append(defaultCamera(openShotDuration=0.5))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'StenographerSanctionSuppression':
            if attackDuration > 2:
                camTrack.append(defaultCamera(openShotDuration=0.5))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'StenographerSanction':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'StenographerSanctionLitigator':
            camTrack.append(defaultCamera(openShotDuration=0.5))
            # case manager cheats
        case 'CaseManagerInsurancePlanScapegoat' | 'CaseManagerInsurancePlanScapegoat2' | 'CaseManagerInsurancePlan' | 'CaseManagerInsurancePlan2':
            camTrack.append(heldRelativeShot(suit, 0.0, 8.8096, 7.77317, -180.0, 0.0, 0.0, 2.7))
            camTrack.append(moveShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 4.2))
        case 'CaseManagerInsurance':
            camTrack.append(heldShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, attackDuration))
        case 'CaseManagerInsurance2':
            camTrack2 = heldShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, attackDuration)
            return camTrack2
        case 'CaseManagerLegalBindings':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'CaseManagerLegalBindings2':
            camTrack.append(heldRelativeShot(suit, 0.0, 8.8096, 7.77317, -180.0, 0.0, 0.0, 2.7))
            camTrack.append(moveShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 4.2))
            # scapegoat cheats
        case 'ScapegoatRageBuilding':
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
        case 'ScapegoatShieldsUp':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'ScapegoatEnraged':
            camTrack.append(heldRelativeShot(suit, 0.0, 10.0, 8.0, -180.0, -20.0, 0.0, attackDuration))
        case 'ScapegoatGavel':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'ScapegoatBarnyardBash':
            if attackDuration > 2:
                camTrack.append(randomActorShot(target[0]['toon'], battle, attackDuration, 'toon'))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        # powerhouse cheats
        case 'PowerhouseAbsorb':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'PowerhouseSoakImmune':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'PowerhouseDropImmune':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'PowerhouseZapImmune':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'PowerhouseLureImmune':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'PowerhouseSyphon':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'PowerhouseSyphonDesperation':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, attackDuration))
        case 'PowerhouseGroundbreaker':
            quake = 1
            camTrack.append(suitCameraShakeShot(attackDuration, 1.0, quake=quake))
        case 'PowerhouseGroundbreakerRevert':
            if attackDuration > 2:
                camTrack.append(Parallel(heldShot(0.0, 0.0, 3.5, 180.0, -20.0, 0.0, attackDuration)))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'PowerhouseSnipeVulnerable':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'PowerhouseSnipeGagBan':
            if attackDuration > 2:
                camTrack2 = defaultCamera(openShotDuration=1.75)
                pbpText = attack['playByPlayText']
                pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
                return Parallel(pbpTrack, camTrack2)
            else:
                camTrack2 = defaultCamera(openShotDuration=1.75)
                return camTrack2
        case 'PowerhouseSnipeSoaked':
            camTrack.append(defaultCamera(openShotDuration=1.75))
        case 'PowerhouseToleranceBuilding':
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
        case 'PowerhouseSnipeBookkept':
            if attackDuration > 2:
                camTrack2 = defaultCamera(openShotDuration=1.75)
                pbpText = attack['playByPlayText']
                displayName = TTLocalizer.SuitAttackNames.get(name, '')
                pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=(0.0, 0.775))
                return Parallel(pbpTrack, camTrack2)
            else:
                camTrack2 = defaultCamera(openShotDuration=1.75)
                return camTrack2
        case 'PowerhouseSnipeMulligan':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'PowerhouseSnipeCollectCall':
            camTrack.append(heldRelativeShot(suit, 0.0, 9.0, 10.0, -180.0, -20.0, 0.0, attackDuration))
        case 'PowerhouseGeneration':
            camTrack.append(heldRelativeShot(suit, 0.0, 9.0, 10.0, -180.0, -20.0, 0.0, attackDuration))
        case 'PowerhouseGeneration2':
            camTrack.append(heldRelativeShot(suit, 0.0, 9.0, 10.0, -180.0, -20.0, 0.0, attackDuration))
        # bookkeeper cheats
        case 'BookkeeperPaperCutSoaked':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'BookkeeperPaperCutMarked':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'BookkeeperPaperCut':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'BookkeeperExplodingDocument':
            camTrack.append(heldRelativeShot(suit, 0.0, 10.0, 7.0, -180.0, 0.0, 0.0, 2.7))
            camTrack.append(moveShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 4.2))
        case 'BookkeeperMandatoryFiling':
            camTrack.append(defaultCamera(openShotDuration=0.75))
        case 'BookkeeperCabinetCrackdown':
            camTrack.append(defaultCamera(openShotDuration=0.75))
        case 'BookkeeperBookkeepingRetaliation':
            if attackDuration > 2:
                camTrack2 = defaultCamera(openShotDuration=3.0)
                pbpText = attack['playByPlayText']
                displayName = TTLocalizer.SuitAttackNames.get(name, '')
                pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
                return Parallel(pbpTrack, camTrack2)
            else:
                camTrack2 = defaultCamera(openShotDuration=0.0)
                return camTrack2
        case 'BookkeeperBookkeeping':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        # wiretapper cheats
        case 'WiretapperCollectCall':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'WiretapperCollectCall2':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'WiretapperCollectCallDamage':
            # camTrack.append(randomSplitShot(suit, target[0]['toon'], battle, attackDuration))
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'WiretapperBusySignal':
            camTrack.append(Sequence(randomActorShot(target[0]['toon'], battle, 1.5, 'toon'), randomActorShot(suit, battle, 1.0, 'suit'), randomActorShot(target[0]['toon'], battle, attackDuration - 2.5, 'toon')))
        case 'WiretapperGagBan':
            camTrack2 = heldRelativeShot(suit, 0.0, 9.0, suit.height + 5.0, -180.0, -30.0, 0.0, attackDuration)
            return camTrack2
        case 'WiretapperWiretapped':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'WiretapperVoicemail':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'WiretapperBrokenConnection':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        # ambassador cheats
        case 'AmbassadorHeadRoller' | 'AmbassadorHeadRoller2' | 'AmbassadorHeadRoller3' | 'AmbassadorHeadRoller4' | 'AmbassadorHeadRoller5':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'AmbassadorHeadRollerGroup':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0.0, -20, 0.0, attackDuration))
        case 'AmbassadorAdvancement':
            camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, 0.0),
                                     Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                     Func(taskMgr.remove, 'camera_shake'),
                                     heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
        case 'AmbassadorAdvancement2' | 'AmbassadorAdvancement3':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'AmbassadorAdvancement4' | 'AmbassadorAdvancement5':
            camTrack.append(heldRelativeShot(suit, 0.0, 8.8096, 7.77317, -180.0, 0.0, 0.0, 2.7))
            camTrack.append(moveShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 4.2))
        case 'AmbassadorRefinement' | 'AmbassadorRefinementManager':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, suit.getDuration('snap') + 0.5))
            camTrack.append(cameraActorShot(suit, 'summon-cog', (attackDuration - (suit.getDuration('snap') + 0.5))))
        case 'AmbassadorGhostMentality':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'AmbassadorPhase2':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'AmbassadorDamageUp':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'AmbassadorManagerialProtection' | 'AmbassadorManagerialProtectionImmunity':
            camTrack.append(defaultCamera(openShotDuration=3.0))
        case 'AmbassadorMulligan':
            camTrack.append(defaultCamera(openShotDuration=2.0, attackDuration=2.0))
            camTrack.append(heldShot(0.0, -60.0, 20.0, 0.0, -20.0, 0.0, attackDuration - 2.0))
        # safety supervisor cheats
        case 'SafetyOverpressured':
            target = attack['target']
            targetSuit = target[0]['suit']
            camTrack2 = Sequence(heldRelativeShot(suit, 0.0, 9.0, 6.0, -180.0, 0.0, 0.0, 5.0),
                                 moveShot(0.0, -20.0, 10.0, 0.0, -20.0, 0.0, 1.5),
                                 heldShot(0.0, -20.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 6.5))
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackName.get(name, '')
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(targetSuit.name)), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            return Parallel(pbpTrack, camTrack2)
        case 'SafetyOverpressured2' | 'SafetyOverpressured3' | 'SafetyOverpressured4' | 'SafetyOverpressured5':
            camTrack.append(heldRelativeShot(suit, 0.0, 9.0, 6.0, -180.0, 0.0, 0.0, 5.0))
            camTrack.append(moveShot(0.0, -20.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 6.5))
        case 'SafetyHighPressure':
            camTrack.append(Sequence(defaultCamera(openShotDuration=4, attackDuration=4), moveShot(0.0, -20.0, 10.0, 0, -20, 0, 0),
                                     Func(taskMgr.add, shake_camera_high_pressure, 'camera_shake'), Wait(3.0),
                                     Func(taskMgr.remove, 'camera_shake'),
                                     heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 7)))
        case 'SafetyHeatWave':
            camTrack.append(Sequence(motionShot(4.0, -10.0, suit.height + 5, 30, -30.0, 0.0, 0, suit), moveCameraOnly(-4, -10.0, suit.height + 5, suit.getDuration('magic3-alt'), suit, h=-30, p=-30, startH=30, startP=-30), motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration - suit.getDuration('magic3-alt'))))
        case 'SafetyHeatWaveCalculation':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 5.0, 180, 30.0, 0.0, 0, suit), moveCameraOnly(0.0, 9.0, suit.height + 5, attackDuration - 2, suit, h=180, p=-30), Wait(2)))
        case 'SafetyOverpressureDeath':
            camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'SafetyViolation':
            if attackDuration > 2:
                camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                     defaultCamera(openShotDuration=0, attackDuration=attackDuration-5)))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'SafetyPromotion':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                     moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
        case 'SafetyPromotion2':
            camTrack.append(Sequence(defaultCamera(openShotDuration=2.0)))
        case 'SafetyPromotion3':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                     moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
        case 'SafetyPromotion4':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                     moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
        case 'SafetyPromotion5':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                     moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
        case 'SafetySoakRetaliation':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                     defaultCamera(openShotDuration=0, attackDuration=attackDuration-5)))
            # hustler cheats
        case 'HustlerLimitedTimeOfferApprove':
            if attackDuration > 2:
                camTrack.append(heldShot(10, 0, 10, 115, -30, 0, attackDuration))
            else:
                camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
                return camTrack2
        case 'HustlerLimitedTimeOfferDenied':
            if attackDuration > 2:
                camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
            else:
                camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
                return camTrack2
        case 'HustlerSalesPitch':
            camTrack.append(Sequence(defaultCamera(openShotDuration=3, attackDuration=3), motionShot(2.5, 10, 1, 165, 25, 0, 0, target[0]['toon']), Wait(attackDuration - 3)))
        case 'HustlerClosingTime':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                          heldRelativeShot(suit, 0.0, 7.8096, 9, -180, -10.0, 0.0, attackDuration)))
        case 'HustlerBaitAndSwitch':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'HustlerCustomerRetention':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
            #camTrack.append(Sequence(heldShot(0, 15, 20, -180, -20, 0, attackDuration)))
        case 'HustlerExclusiveOfferRetaliation':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'HustlerExclusiveOffer':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'HustlerHalfWindsor':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        # traffic manager cheats
        case 'TrafficDetour':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'TrafficCongestionPricing':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'TrafficRedLight':
            target = attack['target']
            targetSuit = target[0]['suit']
            tpMgr = TextPropertiesManager.getGlobalPtr()
        
            def addTextColor(name, r, g, b):
                prop = TextProperties()
                prop.setTextColor(r, g, b, 1)
                tpMgr.setProperties(name, prop)
        
            addTextColor('redLight',   1.0, 0.0, 0.0)
            redLight = '\1redLight\1Red Light\2'
            camTrack2 = Sequence(
                # First shot: attacking suit
                heldRelativeShot(suit, 0.0, 8.8096, 7.77317, -180.0, 0.0, 0.0, 1.0),
        
                # Switch to target suit shot.
                Func(camera.setPos, targetSuit, 0.0, 10.0, targetSuit.height - 5),
        
                # Set the orientation for this new shot.
                Func(camera.setHpr, targetSuit, 180, 0, 0),
        
                moveCameraOnly(0.0, 10.0, targetSuit.height, 1, targetSuit, h=180, p=0, startH=180, startP=0),
                # Now ONLY move upward relative to targetSuit.
        
                Wait(attackDuration - 2.0)
            )
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(targetSuit.name, redLight)), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            return Parallel(pbpTrack, camTrack2)
        case 'TrafficTrafficViolation':
            if attackDuration > 2:
                camTrack.append(Sequence(motionShot(2.0, -2.0, suit.height, 0, -20.0, 0.0, 0, suit), Wait(attackDuration - 0)))
            else:
                camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
                return camTrack2
        case 'TrafficRedLightRetaliation':
            if attackDuration > 2:
                camTrack.append(Sequence(motionShot(2.0, -2.0, suit.height, 0, -20.0, 0.0, 0, suit), Wait(attackDuration - 0)))
            else:
                camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
                return camTrack2
        case 'TrafficGreenLight':
            target = attack['target']
            targetSuit = target[0]['suit']
            tpMgr = TextPropertiesManager.getGlobalPtr()
        
            def addTextColor(name, r, g, b):
                prop = TextProperties()
                prop.setTextColor(r, g, b, 1)
                tpMgr.setProperties(name, prop)
        
            addTextColor('greenLight',  0.027, 1, 0)
            greenLight = '\1greenLight\1Green Light\2'
            camTrack2 = Sequence(
                # First shot: attacking suit
                heldRelativeShot(suit, 0.0, 8.8096, 7.77317, -180.0, 0.0, 0.0, 1.0),
        
                # Switch to target suit shot.
                Func(camera.setPos, targetSuit, 0.0, 10.0, targetSuit.height - 5),
        
                # Set the orientation for this new shot.
                Func(camera.setHpr, targetSuit, 180, 0, 0),
        
                moveCameraOnly(0.0, 10.0, targetSuit.height, 1, targetSuit, h=180, p=0, startH=180, startP=0),
                # Now ONLY move upward relative to targetSuit.
        
                Wait(attackDuration - 2.0)
            )
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(targetSuit.name, greenLight)), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            return Parallel(pbpTrack, camTrack2)
        case 'TrafficYellowLight':
            tpMgr = TextPropertiesManager.getGlobalPtr()
        
            def addTextColor(name, r, g, b):
                prop = TextProperties()
                prop.setTextColor(r, g, b, 1)
                tpMgr.setProperties(name, prop)
        
            addTextColor('yellowLight', 0.973, 1, 0)
            yellowLight = '\1yellowLight\1Yellow Light\2'
            camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(yellowLight)), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            return Parallel(pbpTrack, camTrack2)
        case 'TrafficGreenLightRetaliation':
            if attackDuration > 2:
                camTrack.append(Sequence(motionShot(2.0, -2.0, suit.height, 0, -20.0, 0.0, 0, suit), Wait(attackDuration - 0)))
            else:
                camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
                return camTrack2
        case 'TrafficYield':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        # union buster cheats
        case 'UnionBusterCompensationClaims':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'UnionBusterContractEnforcementHealing':
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'UnionBusterUnionDues':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'UnionBusterNoStrikeClause':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'UnionBusterUnionCalculator':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'UnionBusterUnionBust':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'UnionBusterUnionBuster':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'UnionBusterUnionWages':
            camTrack.append(Sequence(motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), moveCameraOnly(-4.0, 9.0, suit.height - 1, attackDuration - 3, suit, h=210, p=0, startH=150, startP=0), Wait(3)))
        case 'UnionBusterUnionWages2' | 'UnionBusterUnionWages3' | 'UnionBusterUnionWages4' | 'UnionBusterUnionWages5':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'UnionBusterBreachOfContract':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'UnionBusterBreachOfContract2':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'UnionBusterBreachOfContract3':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'UnionBusterBreachOfContract4':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'UnionBusterContractEnforcement':
            camTrack.append(defaultCamera(openShotDuration=6.75))
        case 'UnionBusterContractEnforcement2':
            camTrack.append(defaultCamera(openShotDuration=1.5))
            # racketeer
        case 'RacketeerOverextendedLeverage2':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'RacketeerOverextendedLeverage':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'RacketeerProfiteering':
            camTrack.append(Sequence(motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(3.7),
                                     moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 5.2)))
        case 'RacketeerProfiteering2' | 'RacketeerProfiteering3' | 'RacketeerProfiteering4' | 'RacketeerProfiteering5':
            camTrack.append(Parallel(cameraActorShot(suit, 'summon-cog', attackDuration), Wait(attackDuration)))
        case 'RacketeerExtortion':
            camTrack.append(Parallel(cameraActorShot(suit, 'sacrifice-cog', attackDuration), Wait(attackDuration)))
        case 'RacketeerExtortion2':
            camTrack.append(Sequence(heldShot(10, 0, 10, 115, -30, 0, 1.0), Parallel(Wait(attackDuration - 1), cameraActorShot(suit, 'summon-cog', attackDuration - 1))))
        case 'RacketeerCompensation':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'RacketeerHustling':
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        case 'RacketeerRacketeering':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'RacketeerPeckingOrderRetaliation':
            if attackDuration > 2:
                camTrack.append(defaultCamera(openShotDuration=1.5))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'RacketeerPeckingOrderRetaliationSoak':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                     defaultCamera(openShotDuration=0, attackDuration=attackDuration-5)))
            # radiographer
        case 'RadiographerRadioInfrequency':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'RadiographerHotTake':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'RadiographerHotTakeDamage':
            if attackDuration > 2:
                camTrack.append(defaultCamera(openShotDuration=0))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'RadiographerHotTakeRetaliation':
            camTrack.append(defaultCamera(openShotDuration=6.75))
        case 'RadiographerOvermodulated' | 'RadiographerOvermodulated2' | 'RadiographerOvermodulated3' | 'RadiographerOvermodulated4' | 'RadiographerOvermodulated5':
            camTrack.append(randomActorShot(suit, battle, 1.5, 'suit'))
            camTrack.append(moveShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 3.0))
        case 'RadiographerDanceSession': # Target Check
            camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
            #derrick man
        case 'DerrickManRefinement':
            camTrack.append(heldRelativeShot(suit, 0.0, 8.8096, 5.77317, -180.0, 0.0, 0.0, 2.7))
            camTrack.append(moveShot(0.0, -20.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 4.2))
            #dola
        case 'DOLAInkDrain':
            camTrack.append(defaultCamera(openShotDuration=1.0))
            #dopr
        case 'DOPRAmbushMarketing':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
            #dividend king
        case 'DividendZapRetaliation':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'DividendAccountRollover' | 'DividendAccountRollover2' | 'DividendAccountRollover3' | 'DividendAccountRollover4' | 'DividendAccountRollover5':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'DividendLiquidationEvent':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'DividendLiquidationEventDamage':
            if attackDuration > 2:
                camTrack2 = Parallel(heldShot(0.0, 0.0, 3.5, 180, -20, 0, attackDuration))
                return camTrack2
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
            # if attackDuration > 2:
            #     camTrack2 = randomActorShot(target[0]['toon'], battle, attackDuration, 'toon')
            #     pbpText = attack['playByPlayText']
            #     displayName = TTLocalizer.SuitAttackNames.get(name, '')
            #     pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(attack['target'][0]['hp'])), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            #     return Parallel(pbpTrack, camTrack2)
            # else:
            #     camTrack2 = defaultCamera(openShotDuration=0)
            #     return camTrack2
        case 'DividendTotalMarketMeltdown' | 'DividendTotalMarketMeltdown2':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'DividendTotalMarketMeltdownDamage':
            camTrack2 = heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration)
            return camTrack2
        case 'DividendPeckingOrder':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'DividendPeckingOrderZapped':
            camTrack.append(allGroupLowShot(suit, attackDuration, battle))
            # ottoman cheats
        case 'OttomanRevisedDraft':
            camTrack.append(defaultCamera(openShotDuration=0.75))
        case 'OttomanRedPenReview':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'OttomanFootnoteOverload':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'OttomanPerformanceReview':
            camTrack.append(heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration))
        case 'OttomanPerformanceReviewRevert':
            camTrack.append(heldRelativeShot(suit, 0.0, 8.8096, 7.77317, -180.0, 0.0, 0.0, 2.7))
            camTrack.append(moveShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, 1.5))
            camTrack.append(heldShot(0.0, -10.0, 10.0, 0.0, -20.0, 0.0, attackDuration - 4.2))
            # crystalline cheats
        case 'CrystalShatteringClarity':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'CrystalRefractDamage':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'CrystalRefractDamageRetaliation':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'CrystalFracturedLimitsOffensive' | 'CrystalFracturedLimitsDefensive':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'CrystalFracturedLimitsRetaliation':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'CrystalPrismaticDistortion':
            camTrack.append(defaultCamera(openShotDuration=0.5))
            # chairman cheats
        case 'ChairmanTrapRetaliation':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'ChairmanLureRetaliation':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'ChairmanThrowRetaliation':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'ChairmanSquirtRetaliation':
            camTrack.append(Sequence(defaultCamera(openShotDuration=2.0, attackDuration=2.0),
                                     heldShot(5.0, 0.0, 0.5, 155.0, 35.0, 0.0, attackDuration - 2.0)))
        case 'ChairmanZapRetaliation':
            camTrack.append(defaultCamera(openShotDuration=0.75))
        case 'ChairmanSoundRetaliation':
            camTrack.append(heldRelativeShot(suit, 0.0, 15.0, 5.0, -180.0, 0.0, 0.0, 4.0))
            camTrack.append(defaultCamera(openShotDuration=0.0, attackDuration=attackDuration - 4.0))
        case 'ChairmanDropRetaliation':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'ChairmanCage':
            camTrack.append(defaultCamera(openShotDuration=1.0))
        case 'ChairmanPhase2':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'ChairmanOvertime' | 'ChairmanOvertime2' | 'ChairmanOvertime3' | 'ChairmanOvertime4' | 'ChairmanOvertime5':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                     moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
        case 'ChairmanHostileLiquidation' | 'ChairmanHostileLiquidation2' | 'ChairmanHostileLiquidation3' | 'ChairmanHostileLiquidation4' | 'ChairmanHostileLiquidation5':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                     moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
        case 'ChairmanSnipe':
            camTrack.append(defaultCamera(openShotDuration=1.5))
            # liquidator cheats
        case 'LiquidatorOilRain':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, attackDuration)))
        case 'LiquidatorOilRainDamage':
            camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'LiquidatorFreezingRain':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, attackDuration)))
        case 'LiquidatorHeavyRain':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, attackDuration)))
        case 'LiquidatorHeavyRainDamage':
            camTrack2 = heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration)
            return camTrack2
        case 'LiquidatorStormCell':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, attackDuration)))
        case 'LiquidatorStormCellDamage':
            camTrack2 = defaultCamera(openShotDuration=1.0)
            return camTrack2
        case 'LiquidatorInversion':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 10.8096, 8, -180, -10.0, 0.0, attackDuration)))
        case 'LiquidatorMonsoon':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 10.8096, 10, -180, -10.0, 0.0, attackDuration)))
        case 'LiquidatorTornado':
            camTrack.append(Sequence(randomActorShot(suit, battle, 0.5, 'suit'), heldShot(20, 0, 20, 115, -30, 0, attackDuration - .5)))
            # tollmaster
        case 'TollmasterMandatoryToll':
            camTrack.append(Sequence(motionShot(0, -6, suit.height + 2, 0, 0, 0.0, 0, suit), moveCameraOnly(2, -1, suit.height, attackDuration - 2, suit, h=0, p=-10, startH=0, startP=0), Wait(2)))
            #camTrack.append(Sequence(motionShot(0.0, 10.0, 5.0, -180, 30.0, 0.0, 0, suit), motionShot(2.0, -2.0, suit.height, 0, -20.0, 0.0, 2, suit), Wait(attackDuration - 2)))
        case 'TollmasterMandatoryTollFinal':
            camTrack.append(Sequence(randomActorShot(suit, battle, 6.5, 'suit'), 
                                     heldShot(0, 15, 20, -180, -20, 0, attackDuration - 6.5)))
        case 'TollmasterRushHour':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'TollmasterResonanceTax' | 'TollmasterResonanceTax2' | 'TollmasterResonanceTax3' | 'TollmasterResonanceTax4' | 'TollmasterResonanceTax5':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'TollmasterMissedPayment':
            if attackDuration > 2:
                camTrack.append(allGroupLowShot(suit, attackDuration, battle))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'TollmasterLedgerOfSound':
            camTrack.append(Sequence(defaultCamera(openShotDuration=1.5)))
        case 'TollmasterBalanceTheLedger':
            camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 0),
                                     Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                     Func(taskMgr.remove, 'camera_shake'),
                                     heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
        case 'TollmasterBalanceTheLedger2' | 'TollmasterBalanceTheLedger3' | 'TollmasterBalanceTheLedger4' | 'TollmasterBalanceTheLedger5':
            camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 0),
                                     Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                     Func(taskMgr.remove, 'camera_shake'),
                                     heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
            # record keeper
        case 'RecordkeeperMinutesTaken' | 'RecordkeeperMinutesTakenContingency':
            camTrack.append(Sequence(randomActorShot(suit, battle, 2.0, 'suit'), heldShot(0, 15, 20, -180, -20, 0, attackDuration - 2)))
        case 'RecordkeeperMinutesTakenDamage':
            camTrack.append(heldShot(0, 15, 20, -180, -20, 0, attackDuration))
        case 'RecordkeeperPaperTrail':
            camTrack.append(defaultCamera(openShotDuration=6.75))
        case 'RecordkeeperRevisedFiling':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.0, 'suit'), heldShot(0, 15, 20, -180, -20, 0, attackDuration - 1)))
        case 'RecordkeeperRevisedFilingLiquidation':
            camTrack.append(defaultCamera(openShotDuration=6.75))
        case 'RecordkeeperRedlinedClause':
            camTrack.append(defaultCamera(openShotDuration=0.5))
        case 'RecordkeeperRedlinedClauseMissedPayment':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'RecordkeeperAuditCycle':
            camTrack.append(Sequence(motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), Wait(attackDuration)))
        case 'RecordkeeperPhantomEntryDamage':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration)))
        case 'RecordkeeperPhantomEntrySpawn':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 5.0, 180, 30.0, 0.0, 0, suit), moveCameraOnly(0.0, 9.0, suit.height + 5, attackDuration - 2, suit, h=180, p=-30), Wait(2)))
        case 'RecordkeeperPhantomEntrySacrifice':
            camTrack.append(Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)))
            # corporate butcherer
        case 'ButcherOverride':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 10.0, 10.0, -180, -10.0, 0.0, attackDuration)))
        case 'ButcherOverrideRemoval':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 10.0, 10.0, -180, -10.0, 0.0, attackDuration)))
        case 'ButcherRevvingUp':
            camTrack2 = Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 10.0, 10.0, -180, -10.0, 0.0, attackDuration))
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(target[0]['hp'])), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            return Parallel(pbpTrack, camTrack2)
        case 'ButcherRevvingUpWhipsaw':
            camTrack2 = Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     heldRelativeShot(suit, 0.0, 10.0, 10.0, -180, -10.0, 0.0, attackDuration))
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
            pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            return Parallel(pbpTrack, camTrack2)
        case 'ButcherKickback':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'ButcherMarkedWood':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), defaultCamera(openShotDuration=1.5, attackDuration=attackDuration - 2)))
        case 'ButcherOffboarding' | 'ButcherOffboarding2' | 'ButcherOffboarding3' | 'ButcherOffboarding4' | 'ButcherOffboarding5':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), randomActorShot(suit, battle, 1, 'suit'), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3)))
        case 'ButcherAggrandize' | 'ButcherAggrandize2' | 'ButcherAggrandize3' | 'ButcherAggrandize4' | 'ButcherAggrandize5':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
        case 'ButcherSparkPlug':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, 3.0), defaultCamera(openShotDuration=0, attackDuration=attackDuration - 5)))
        case 'ButcherSparkPlugDamage':
            if attackDuration > 2:
                camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
                pbpText = attack['playByPlayText']
                displayName = TTLocalizer.SuitAttackNames.get(name, '')
                pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
                return Parallel(pbpTrack, camTrack2)
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'ButcherScabbard':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'ButcherLayoffs':
            camTrack.append(Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, 3.875), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3.875)))
            # contingency director
        case 'ContingencyOverrideRevert':
            camTrack2 = Sequence(randomActorShot(suit, battle, attackDuration, 'suit'))
            return camTrack2
        case 'ContingencyOverride':
            camTrack2 = Sequence(randomActorShot(suit, battle, attackDuration, 'suit'))
            return camTrack2
        case 'ContingencySelfRepair':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                          heldRelativeShot(suit, 0.0, 7.8096, 9, -180, -10.0, 0.0, attackDuration)))
        case 'ContingencyFailsafeProtocol':
            camTrack.append(allGroupHighShot(suit, attackDuration))
        case 'ContingencyRiskThresholdBreach':
            dmg = attack['target'][0]['hp']
            camTrack2 = Sequence(motionShot(6.0, 7.0, suit.height, 225, -10, 0.0, 0, suit), moveCameraOnly(-6.0, 7.0, suit.height, attackDuration - 2, suit, h=225, p=-10, startH=135, startP=-20), Wait(2))
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(dmg, 'y' if abs(dmg) == 1 else 'ies')), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            return Parallel(pbpTrack, camTrack2)
        case 'ContingencyRiskThresholdBreach75':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'ContingencyMarkLiquidated':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'ContingencyRiskThresholdBreach50':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'ContingencyMarkRevisedFiling':
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        case 'ContingencyRiskThresholdBreach25':
            if attackDuration > 2.0:
                camTrack2 = defaultCamera(openShotDuration=0.75)
                pbpText = attack['playByPlayText']
                displayName = TTLocalizer.SuitAttackNames.get(name, '')
                pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
                return Parallel(pbpTrack, camTrack2)
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'ContingencyContingencyClause':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'ContingencyContingencyClauseRetaliation':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=3), defaultCamera(openShotDuration=1.5, attackDuration=attackDuration-3)))
        case 'ContingencyRedundantAuthority':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'ContingencyOperationalFreeze':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'ContingencyForecastCollapse':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
            #cashbot litigation
        case 'PayrollPayrollProcessing':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 4.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                     moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
        case 'PayrollPerformanceBonus':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 4.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                     moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
        case 'ErclaimLaffSteal':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'ErclaimRiseFromTheScrap' | 'ErclaimScopeCreep':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'ErclaimPhase2':
            camTrack2 = Sequence()
            return camTrack2
        case 'ErclaimSacrifice':
            camTrack.append(Sequence(heldShot(20, -10, 15, 50, -30, 0, 1.5), Func(taskMgr.add, shake_camera_sacrifice, 'camera_shake'), Wait(attackDuration - 2.0),
                                     Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
        case 'ErclaimSacrifice2' | 'ErclaimSacrifice3' | 'ErclaimSacrifice4' | 'ErclaimSacrifice5':
            camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                     Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
        case 'ErfitHydrationCheck':
            if attack['target'][0]['hp'] > 0:
                camTrack.append(Sequence(defaultCamera(openShotDuration=2.0, attackDuration=2), heldShot(0, 15, 20, -180, -20, 0, attackDuration - 2)))
            else:
                camTrack.append(Sequence(defaultCamera(openShotDuration=2.0)))
        case 'ErfitWringOut':
            camTrack.append(randomSplitShot(suit, target[0]['toon'], battle, attackDuration))
        case 'ErfitHydrationCheckRevert':
            if attackDuration > 2:
                camTrack2 = Parallel(heldShot(0.0, 0.0, 3.5, 180, -20, 0, attackDuration))
                return camTrack2
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'ErclaimHemmorage':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'ErfitProToonShake':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'ErclaimHemmorageHealing':
            camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'ErfitGainsFromTheScrap':
            camTrack.append(Parallel(cameraActorShot(suit, 'sacrifice-cog', attackDuration), Wait(attackDuration)))
        case 'ErfitGainsFromTheScrap2' | 'ErfitGainsFromTheScrap3' | 'ErfitGainsFromTheScrap4' | 'ErfitGainsFromTheScrap5':
            camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                     Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
        case 'ErfitPersonalTrainer':
            camTrack.append(Parallel(cameraActorShot(suit, 'summon-cog', attackDuration), Wait(attackDuration)))
        case 'ErfitPhase2':
            camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        #high roller phase 1 cheats
        case 'HighRollerNoAttack':
            camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
            return camTrack2
        case 'HighRollerWheelSpin':
            camTrack.append(Sequence(motionShot(0.0, 5, 8, -180, 0.0, 0.0, 0, suit), Wait(3.5),
                                     motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                     motionShot(0.0, 8, 8, -180, 0.0, 0.0, 0, suit), Wait(attackDuration - 5.75)))
        case 'HighRollerGameOver' | 'HighRollerGameOver2':
            camTrack.append(Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, 4 + suit.getDuration('snap')), motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, .5, suit), Wait(1.0),
                                     defaultCamera(openShotDuration=0, attackDuration=attackDuration - (5.5 + suit.getDuration('snap')))))
        case 'HighRollerPuzzle':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'HighRollerPuzzleBan':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'HighRollerCommercialBreak':
            camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'HighRollerGameTimeSpawn':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                          heldRelativeShot(suit, 0.0, 7.8096, 9, -180, -10.0, 0.0, attackDuration)))
        case 'HighRollerGameTimeCog' | 'HighRollerGameTimeCog2':
            dmg = attack['target'][0]['hp']
            targetSuit = battle.activeSuits[dmg]
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
        
            camTrack2 = Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.0),
                                     motionShot(0.0, 9.0, targetSuit.height + 5, -180, -30.0, 0.0, 0, targetSuit), Wait(3.0), heldShot(0.0, -20.0, 12.0, 0, -10, 0, 7.5), Wait(3.5), 
                                     motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, .5, suit), Wait(.5), motionShot(0.0, 9.0, targetSuit.height + 5, -180, -30.0, 0.0, 0, targetSuit), Wait(attackDuration - 16))
            pbpText = attack['playByPlayText']
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(targetSuit.name)), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            return Parallel(pbpTrack, camTrack2)
        case 'HighRollerGameTimeCog3' | 'HighRollerGameTimeCog4' | 'HighRollerGameTimeCog5' | 'HighRollerGameTimeCog6' | 'HighRollerGameTimeCog7' | 'HighRollerGameTimeCog8' | 'HighRollerGameTimeCog9' | 'HighRollerGameTimeCog10':
            camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
        case 'HighRollerBust':
            if attackDuration > 2:
                camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                     moveShot(0.0, -20.0, 10.0, 0, -20, 0, 0.5),
                                     heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 5.5)))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        # high roller phase 2 cheats
        case 'HighRollerPhase3':
            camTrack2 = Sequence(heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration))
            return camTrack2
        # high roller phase 3 cheats
        case 'HighRollerPhase2':
            camTrack2 = Sequence(motionShot(0.0, 8.8096, 9.77317, -180, 0.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'HighRollerFreeCruise':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.7))
            camTrack.append(moveShot(-21.0, 8.0, 8.0, -120, 0, 0, 0.5))
            camTrack.append(heldShot(-21.0, 8.0, 8.0, -120, 0, 0, attackDuration - 4.2))
        case 'HighRollerConduction':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'HighRollerRolled':
            camTrack.append(defaultCamera(openShotDuration=1.7))
        case 'HighRollerRaisingTheAnte':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.7))
            camTrack.append(moveShot(-21.0, 8.0, 8.0, -120, 0, 0, 0.5))
            camTrack.append(heldShot(-21.0, 8.0, 8.0, -120, 0, 0, attackDuration - 4.2))
        case 'HighRollerDiceRouletteCogs' | 'HighRollerDiceRouletteToons' | 'HighRollerDiceRouletteEveryone' | 'HighRollerDiceRouletteNobody':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.25, 'suit'),
                                     motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                     heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
        case 'HighRollerVulnerable':
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        case 'HighRollerTrickOfTheLight':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'HighRollerAceInTheHole':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0.7, suit), Wait(3.0),
                                     moveShot(0, 15, 20, -180, -20, 0, 1.0),
                                     heldShot(0, 15, 20, -180, -20, 0, attackDuration - 4.7)))
        # high roller silhouette cheats
        case 'HighRollerDonation':
            camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'), heldShot(0.0, -20.0, 10.0, 0, -20, 0, 3.875), randomActorShot(suit, battle, attackDuration - 5.375, 'suit')))
        case 'HighRollerSyphon':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0.5, attackDuration=2.0), randomActorShot(suit, battle, attackDuration - 2, 'suit')))
        case 'HighRollerBar' | 'HighRollerBar2':
            camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
        case 'HighRollerLureResistance' | 'HighRollerLureResistance2':
            camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
        case 'HighRollerSingingBlues':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 15, 5, -180, 0.0, 0.0, 0, suit), Wait(attackDuration)))
        case 'HighRollerDamageReduction':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'HighRollerSplashback':
            if attackDuration > 1:
                camTrack.append(Sequence(defaultCamera(openShotDuration=3, attackDuration=3), motionShot(2.5, 10, 1, 165, 25, 0, 0, target[0]['toon']), Wait(attackDuration - 3)))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'HighRollerCheerRetaliation':
            if attackDuration > 1:
                camTrack.append(defaultCamera(openShotDuration=1.5))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
            #videographer cheats
        case 'VideographerStarOfTheShow':
            target = attack['target']
            targetSuit = target[0]['suit']
            camTrack.append(Sequence(motionShot(0.0, 10.0, 5.0, 180, 30.0, 0.0, 0, suit), moveCameraOnly(0.0, 9.0, suit.height + 5, attackDuration - 2, suit, h=180, p=-30), Wait(2)))
            camTrack2 = Sequence(
                defaultCamera(openShotDuration=0, attackDuration=0),
        
                # First shot: attacking suit
                motionShot(
                    0.0,
                    8.8096,
                    7.77317,
                    -180,
                    0.0,
                    0.0,
                    0,
                    suit
                ),
        
                Wait(1.0),
        
                # Switch to target suit shot.
                Func(
                    camera.setPos,
                    targetSuit,
                    0.0,
                    10.0,
                    targetSuit.height - 5
                ),
        
                # Set the orientation for this new shot.
                Func(
                    camera.setHpr,
                    targetSuit,
                    180,
                    0,
                    0
                ),
        
                moveCameraOnly(0.0, 10.0, targetSuit.height, 1, targetSuit, h=180, p=0, startH=180, startP=0),
                # Now ONLY move upward relative to targetSuit.
        
                Wait(attackDuration - 2.0)
            )
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(targetSuit.name)), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            return Parallel(pbpTrack, camTrack2)
        case 'VideographerHardCut':
            camTrack.append(defaultCamera(openShotDuration=1.0))
        case 'VideographerRisingStars' | 'VideographerRisingStars2':
            camTrack.append(Sequence(motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), moveCameraOnly(-4.0, 9.0, suit.height - 1, attackDuration, suit, h=210, p=0, startH=150, startP=0)))
        case 'VideographerRisingStarsSacrifice':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'VideographerStagelightsCogs':
            for headPart in suit.animatedHeadParts:
                camTrack.append(Sequence(motionShot(0, 9, suit.height - 1, 180, 0, 0.0, 0, suit), moveCameraOnly(0, 3, 1, 1, headPart, h=180, p=0, startH=180, startP=0),
                                         moveCameraOnly(0, 3, 1, 3.5, headPart, h=180, p=0, startH=180, startP=0), 
                                         heldShot(0.0, -15.0, 12.5, 0, -20, 0, attackDuration - 4.5)))
        case 'VideographerStagelightsToons':
            for headPart in suit.animatedHeadParts:
                camTrack.append(Sequence(motionShot(0, 9, suit.height - 1, 180, 0, 0.0, 0, suit), moveCameraOnly(0, 3, 1, 1, headPart, h=180, p=0, startH=180, startP=0),
                                         moveCameraOnly(0, 3, 1, 3.5, headPart, h=180, p=0, startH=180, startP=0), 
                                         heldShot(0.0, -20.0, 12.5, 0, -20, 0, attackDuration - 4.5)))
        case 'VideographerRisingStarsSilhouette':
            camTrack.append(Sequence(motionShot(0.0, 10.8096, 10.77317, -180, 0.0, 0.0, 0, suit), Wait(attackDuration)))
        case 'VideographerVideoStatic':
            camTrack.append(heldShot(0.0, -15.0, 12.5, 0, -20, 0, attackDuration))
        case 'VideographerPhase3':
            camTrack2 = Sequence(motionShot(0, 15, 9, 180, 0, 0.0, 0, suit), Wait(4), 
                                 moveCameraOnly(0, 20, 9, 3 + suit.getDuration('frustrated') + 4, suit, p=0, startP=0, h=180, startH=180),
                                 motionShot(0, 5, 3, 180, 50, 0.0, 0, suit), Wait(4), 
                                 moveCameraOnly(0, 10, 9, 4, suit, h=180, p=0, startP=50, startH=180),
                                 moveCameraOnly(0, 15, 9, .5, suit, h=180, p=0, startP=0, startH=180), Wait(1.5),
                                 motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), 
                                 moveCameraOnly(-4.0, 9.0, suit.height - 1, .5 + 2.5 + (suit.getDuration('throttletwo') - 3) + 4, suit, h=210, p=0, startH=150, startP=0),
                                 motionShot(0, -50.0, suit.height - 1, 0, 0, 0.0, 0, suit), 
                                 moveCameraOnly(0, -15.0, suit.height - 1, suit.getDuration('finger-wag') + (suit.getDuration('rake-react') / 2) + 2 + 2 + suit.getDuration('pie-small-react'), suit, h=0, p=0, startH=0, startP=0),
                                 motionShot(0.0, 10.0, 5.0, 180, 30.0, 0.0, 0, suit), moveCameraOnly(0.0, 9.0, suit.height + 5, suit.getDuration('effort'), suit, h=180, p=-30),
                                 motionShot(0, 15, 9, 180, 0, 0.0, 0, suit),
                                 moveCameraOnly(0, 20, 9, 4, suit, h=180, p=0, startP=0, startH=180),
                                 motionShot(0, 10, 10, 180, 0, -35, 0, suit), Wait(2.0),
                                 motionShot(0, 8, 10, 180, 0, 35, 0, suit), Wait(2.0),
                                  motionShot(0, 6, 10, 180, 0, 0, 0, suit), Wait(4.0),
                                  motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), 
                                 moveCameraOnly(-4.0, 9.0, suit.height - 1, 8, suit, h=210, p=0, startH=150, startP=0),
                                 motionShot(0, 6, 10, 180, 0, 0, 0, suit), Wait(4.0))
            return camTrack2
        case 'VideographerElectricShock':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'VideographerElectricShock2':
            camTrack.append(Sequence(motionShot(0.0, 12.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration)))
        case 'VideographerElectricShock3':
            camTrack.append(Sequence(motionShot(0, -6, suit.height + 2, 0, 0, 0.0, 0, suit), moveCameraOnly(-2, -1, suit.height, attackDuration - 2, suit, h=0, p=-10, startH=0, startP=0), Wait(2)))
        case 'VideographerElectricShock4':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'VideographerDeath':
            camTrack2 = Sequence(motionShot(0, 30, 3, 180, 0, 0.0, 0, suit), Wait(4), 
                                 moveCameraOnly(0, 15, 8, 19, suit, p=0, startP=0, h=180, startH=180),
                                 motionShot(0, -10.0, suit.height - 1, 0, 0, 0.0, 0, suit), 
                                 moveCameraOnly(0, -25.0, suit.height - 1, 28, suit, h=0, p=0, startH=0, startP=0),
                                 motionShot(6.0, 12.0, suit.height - 1, 150, 0, 0.0, 0, suit), 
                                 moveCameraOnly(-6.0, 12.0, suit.height - 1, 12, suit, h=210, p=0, startH=150, startP=0),
                                motionShot(5, -10.0, 3, 180, 0, 0.0, 0, suit), 
                                 moveCameraOnly(-5.0, -10.0, 3, 18, suit, h=0, p=0, startH=0, startP=0), 
                                 motionShot(0, 15.0, 8, 180, 0, 0.0, 0, suit), 
                                 moveCameraOnly(0, 10.0, 8, 18, suit, h=180, p=0, startH=180, startP=0), Wait(20))
            return camTrack2
        case 'VideographerAttackRewind':
            camTrack.append(defaultCamera(openShotDuration=1.0))
        case 'VideographerDirectorCuts':
            camTrack2 = Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, 5), motionShot(6.0, 12.0, suit.height - 1, 150, 0, 0.0, 0, suit), 
                                 moveCameraOnly(-6.0, 12.0, suit.height - 1, suit.getDuration('finger-wag') + suit.getDuration('frustrated') + 4, suit, h=210, p=0, startH=150, startP=0), 
                                 motionShot(0, -50.0, suit.height - 1, 0, 0, 0.0, 0, suit), 
                                 moveCameraOnly(0, -15.0, suit.height - 1, 2 + suit.getDuration('finger-wag') + suit.getDuration('summon') + 4, suit, h=0, p=0, startH=0, startP=0),
                                 motionShot(0, 15.0, suit.height, 180, 0, 0.0, 0, suit), 
                                 moveCameraOnly(0, 10.0, suit.height, attackDuration - (2 + 5 + suit.getDuration('finger-wag') + suit.getDuration('summon') + 4 + suit.getDuration('finger-wag') + suit.getDuration('frustrated') + 4), suit, h=180, p=0, startH=180, startP=0))
            return camTrack2
            # broadcaster cheats
        case 'BroadcasterDonation' | 'BroadcasterDonation2':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'BroadcasterViralSensation':
            camTrack.append(defaultCamera(openShotDuration=1.0))
        #filmmaker cheats
        case 'ChoreoPlacesEveryone':
            camTrack.append(allGroupHighShot(suit, attackDuration))
        case 'ChoreoChoreography':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'FilmmakerInFocus':
            target = attack['target']
            toon = target[0]['toon']
            camTrack.append(Sequence(motionShot(0, -6, suit.height + 3, 0, 0, 0.0, 0, suit), Wait(1), moveCameraOnly(0, 5, 2, 1, toon, h=180, p=0, startH=180, startP=0), Wait(attackDuration - 2)))
        case 'FilmmakerCaughtOnCamera':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'FilmmakerCameraFlash':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'FilmmakerWrappedInTheFilm':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'FilmmakerCameraRewind':
            camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'),
                                     moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
        case 'FilmmakerBudgetCuts':
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        #director cheats
        case 'DirectorActionCog':
            target = attack['target']
            targetSuit = target[0]['suit']
            camTrack2 = Sequence(
                defaultCamera(openShotDuration=0, attackDuration=0),
        
                # First shot: attacking suit
                motionShot(
                    0.0,
                    12.8096,
                    8.77317,
                    -180,
                    0.0,
                    0.0,
                    0,
                    suit
                ),
        
                Wait(1.0),
        
                # Switch to target suit shot.
                Func(
                    camera.setPos,
                    targetSuit,
                    0.0,
                    10.0,
                    targetSuit.height - 5
                ),
        
                # Set the orientation for this new shot.
                Func(
                    camera.setHpr,
                    targetSuit,
                    180,
                    0,
                    0
                ),
        
                moveCameraOnly(0.0, 10.0, targetSuit.height, 1, targetSuit, h=180, p=0, startH=180, startP=0),
                # Now ONLY move upward relative to targetSuit.
        
                Wait(attackDuration - 2.0)
            )
            pbpText = attack['playByPlayText']
            displayName = TTLocalizer.SuitAttackNames.get(name, '')
            pbpTrack = pbpText.getShowInterval((displayName[0], displayName[1].format(targetSuit.name)), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            return Parallel(pbpTrack, camTrack2)
        case 'DirectorActionRetaliation':
            camTrack.append(defaultCamera(openShotDuration=3.55))
        case 'DirectorActionPartner':
            target = attack['target']
            toon = target[0]['toon']
            camTrack.append(Sequence(moveCameraOnly(0, 6, 4, 0, toon, h=180, p=0, startH=180, startP=0), Wait(attackDuration)))
        case 'DirectorCut':
            camTrack.append(defaultCamera(openShotDuration=3.55))
        case 'DirectorAction':
            camTrack.append(Sequence(motionShot(0.0, 12.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration)))
        case 'DirectorActionRetaliation':
            camTrack.append(defaultCamera(openShotDuration=3.55))
        case 'DirectorBackToOnes':
            camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
        case 'DirectorProductionBudget':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'DirectorBudgetExpansion':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        #face the family
        case 'ForemanSnipe':
            if attackDuration > 2:
                camTrack.append(defaultCamera(openShotDuration=1.5))
            else:
                camTrack2 = defaultCamera(openShotDuration=0)
                return camTrack2
        case 'ForemanRedTape':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'ForemanContractor':
            camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(3), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3))
            return camTrack2
        case 'ForemanContributing':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'ForemanUnionized':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'ForemanContractorDeath':
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
        case 'ForemanBurning':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'ForemanExtortion':
            camTrack.append(Parallel(cameraActorShot(suit, 'sacrifice-cog', attackDuration), Wait(attackDuration)))
        case 'ForemanPolish':
            camTrack.append(Sequence(heldShot(0.0, -15.0, 10.0, 0, -20, 0, suit.getDuration('snap') + .5), cameraActorShot(suit, 'summon-cog', (attackDuration - (suit.getDuration('snap') + .5)))))
        case 'ForemanSleepyOvercharge':
            camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'ForemanExplosion':
            camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'ForemanCompensation' | 'ForemanCompensation2' | 'ForemanCompensation3' | 'ForemanCompensation4' | 'ForemanCompensation5':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'MintUsury':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.0),
                                     moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.0),
                                     heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 2)))
        case 'MintLureResistance' | 'MintLureResistance2':
            camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
        case 'MintMovingGoalposts':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'MintAudit':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'MintLedger':
            camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=suit.getDuration('glower')), randomActorShot(suit, battle, attackDuration - suit.getDuration('glower'), 'suit')))
        case 'MintHurrySickness':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'MintLifeInsurance':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration)))
        case 'MintPolicyTerminated':
            camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'MintFraudulentDamage':
            camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'MintCompoundingInterest':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'MintAbacusAbove15' | 'MintAbacusBelow15' | 'MintAccountant1' | 'MintAccountant2' | 'MintAccountant3' | 'MintAccountant4' | 'MintAccountant5':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'MintApprove' | 'MintDisapprove':
            camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'MintSynergy':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'MintScheming':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'WhistleCompensation':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'AttorneyObjection':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'AttorneyDrainingPower':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'AttorneyShakedownVulnerable':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'AttorneyShakedownCooldown':
            camTrack.append(defaultCamera(openShotDuration=2.5))
        case 'AttorneyInkDrain':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'AttorneyDizzy':
            camTrack.append(Sequence(randomActorShot(suit, battle, 0.5, 'suit'), heldShot(20, 0, 20, 115, -30, 0, attackDuration - .5)))
        case 'AttorneyRemand':
            camTrack.append(Sequence(motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(3.7),
                                     moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 5.2)))
        case 'AttorneyOverseer' | 'AttorneyOverseerDrop' | 'AttorneyOverseerSquirt' | 'AttorneyOverseerThrow':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'AttorneyObjectionSustained':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'AttorneyObjectionOverruled':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'AttorneyChrono':
            camTrack.append(Sequence(motionShot(0, 15, suit.height - 2.5, 180, 0, 0.0, 0, suit), 
                                 moveCameraOnly(0, 7.0, suit.height - 2.5, 1.5, suit, h=180, p=0, startH=180, startP=0), Wait(attackDuration - 1.5)))
        case 'PacesetterComeOn':
            camTrack.append(Sequence(motionShot(0, 15, suit.height - 2.5, 180, 0, 0.0, 0, suit), 
                                 moveCameraOnly(0, 7.0, suit.height - 2.5, 1.5, suit, h=180, p=0, startH=180, startP=0), Wait(attackDuration - 1.5)))
        case 'AttorneyRushJob':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                          heldRelativeShot(suit, 0.0, 7.8096, 9, -180, -10.0, 0.0, attackDuration)))
        case 'AttorneyHurrySickness':
            if attackDuration > 2:
                camTrack.append(defaultCamera(openShotDuration=1.5))
            else:
                camTrack2 = Sequence(Wait(attackDuration))
                return camTrack2
        case 'PresidentTargetCheck':
            camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'PresidentLiability2':
            camTrack.append(defaultCamera(openShotDuration=.5))
        case 'PresidentLiability':
            camTrack.append(defaultCamera(openShotDuration=.5))
        case 'PresidentMandatoryFiling':
            camTrack.append(defaultCamera(openShotDuration=0.75))
        case 'PacesetterTurn1' | 'PacesetterTurn2':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'PacesetterEarlyOverclocked':
            # Same as Clash's normal OVERCLOCKED attack: the guitar-solo CTSC
            # owns the camera for the entire transition.
            return Sequence(Wait(attackDuration))
        case 'PacesetterHurrySickness':
            if attackDuration > 2:
                camTrack.append(defaultCamera(openShotDuration=1.5))
            else:
                camTrack2 = Sequence(Wait(attackDuration))
                return camTrack2
        case 'PacesetterHurrySicknessBan':
            if attackDuration > 2:
                camTrack.append(defaultCamera(openShotDuration=1.5))
            else:
                camTrack2 = Sequence(Wait(attackDuration))
                return camTrack2
        case 'PacesetterContentSync':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'PacesetterCorporateRestructuring':
            camTrack.append(allGroupHighShot(suit, attackDuration))
        case 'PacesetterMovingGoalposts':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'PacesetterOverclocked':
            # The original Clash guitar-solo CTSC owns the camera for the whole
            # Overclocked transition.
            return Sequence(Wait(attackDuration))
        case 'RushJobTrap' | 'RushJobLure' | 'RushJobThrow' | 'RushJobSquirt' | 'RushJobZap' | 'RushJobSound' | 'RushJobDrop':
            targets = attack['target']
            targetData = targets[0]
            targetSuit = targetData['suit']
            tpMgr = TextPropertiesManager.getGlobalPtr()
        
            def addTextColor(name, r, g, b):
                prop = TextProperties()
                prop.setTextColor(r, g, b, 1)
                tpMgr.setProperties(name, prop)
        
            addTextColor('trap',   1.0, 0.0, 0.0)
            addTextColor('lure',   0.0, 1.0, 0.047)
            addTextColor('throw',  1.0, 0.639, 0.0)
            addTextColor('squirt', 0.914, 0.0, 1.0)
            addTextColor('zap',    0.973, 1.0, 0.0)
            addTextColor('sound',  0.086, 0.0, 1.0)
            addTextColor('drop',   0.0, 1.0, 0.992)
            trapText = '\1trap\1Trap Track\2'
            lureText = '\1lure\1Lure Track\2'
            throwText = '\1throw\1Throw Track\2'
            squirtText = '\1squirt\1Squirt Track\2'
            zapText = '\1zap\1Zap Track\2'
            soundText = '\1sound\1Sound Track\2'
            dropText = '\1drop\1Drop Track\2'
            banDesc = {
                'RushJobTrap': 'The %s needs you to use the %s on the %s!' % (suit.name, trapText, targetSuit.name),
                'RushJobLure': 'The %s needs you to use the %s on the %s!' % (suit.name, lureText, targetSuit.name),
                'RushJobThrow': 'The %s needs you to use the %s on the %s!' % (suit.name, throwText, targetSuit.name),
                'RushJobSquirt': 'The %s needs you to use the %s on the %s!' % (suit.name, squirtText, targetSuit.name),
                'RushJobZap': 'The %s needs you to use the %s on the %s!' % (suit.name, zapText, targetSuit.name),
                'RushJobSound': 'The %s needs you to use the %s on the %s!' % (suit.name, soundText, targetSuit.name),
                'RushJobDrop': 'The %s needs you to use the %s on the %s!' % (suit.name, dropText, targetSuit.name),
            }
        
            banDescHustler = {
                'RushJobTrap': '%s needs you to use the Trap track on the %s!' % (suit.name, targetSuit.name),
                'RushJobLure': '%s needs you to use the Lure track on the %s!' % (suit.name, targetSuit.name),
                'RushJobThrow': '%s needs you to use the Throw track on the %s!' % (suit.name, targetSuit.name),
                'RushJobSquirt': '%s needs you to use the Squirt track on the %s!' % (suit.name, targetSuit.name),
                'RushJobZap': '%s needs you to use the Zap track on the %s!' % (suit.name, targetSuit.name),
                'RushJobSound': '%s needs you to use the Sound track on the %s!' % (suit.name, targetSuit.name),
                'RushJobDrop': '%s needs you to use the Drop track on the %s!' % (suit.name, targetSuit.name),
            }
        
            if suit.dna.name == 'psetter':
                from toontown.cutscene.PacesetterRushJobCutscene import makePacesetterRushJob
                camTrack2 = makePacesetterRushJob(suit, targetSuit, battle, attackDuration)
            else:
                camTrack2 = Sequence(
                defaultCamera(openShotDuration=0, attackDuration=0),
        
                # First shot: attacking suit
                motionShot(
                    0.0,
                    8.8096,
                    7.77317,
                    -180,
                    0.0,
                    0.0,
                    0,
                    suit
                ),
        
                Wait(1.0),
        
                # Switch to target suit shot.
                Func(
                    camera.setPos,
                    targetSuit,
                    0.0,
                    10.0,
                    targetSuit.height - 5
                ),
        
                # Set the orientation for this new shot.
                Func(
                    camera.setHpr,
                    targetSuit,
                    180,
                    0,
                    0
                ),
        
                moveCameraOnly(0.0, 10.0, targetSuit.height, 1, targetSuit, h=180, p=0, startH=180, startP=0),
                # Now ONLY move upward relative to targetSuit.
        
                Wait(attackDuration - 2.0)
            )
            pbpText = attack['playByPlayText']
            pbpTrack = pbpText.getShowInterval(('Rush Job!', banDesc[name]), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            pbpTrack2 = pbpText.getShowInterval(('Limited Time Offer!', banDesc[name]), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            if suit.dna.name == 'hustle':
                return Parallel(pbpTrack2, camTrack2)
            else:
                return Parallel(pbpTrack, camTrack2)
        
        case 'PresidentExtraTip' | 'PresidentExtraTip2' | 'PresidentExtraTip3' | 'PresidentExtraTip4' | 'PresidentExtraTip5' | 'PresidentExtraTip6':
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                     moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
        case 'PresidentSnap':
            camTrack.append(defaultCamera(openShotDuration=2.0))
        case 'PresidentSensational':
            camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
        case 'PresidentViralSensation':
            camTrack2 = Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
            return camTrack2
        case 'PresidentSyphon':
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        case 'PresidentBayouBellow':
            camTrack.append(Parallel(Wait(attackDuration), Sequence(cameraActorShot(suit, 'litigator-bellow', attackDuration))))
        case 'PresidentSnipe':
            camTrack.append(defaultCamera(openShotDuration=1.0))
        case 'PresidentDeepFreeze':
            camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(3.0), defaultCamera(openShotDuration=1.5, attackDuration=attackDuration - 3)))
        case 'PresidentFrozenDeath':
            camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'PresidentPuzzling':
            camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 2))
            return camTrack2
        case 'PresidentDriver':
            camTrack.append(defaultCamera(openShotDuration=2.25))
        case 'PresidentMulligan':
            camTrack.append(defaultCamera(openShotDuration=2.25))
        case 'PresidentHighStakes':
            camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        case 'HighStakesHeal' | 'HighStakesTrap' | 'HighStakesLure' | 'HighStakesSound' | 'HighStakesThrow' | 'HighStakesSquirt' | 'HighStakesZap' | 'HighStakesDrop':
            camTrack2 = Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
            if attackDuration > 1:
                return camTrack2
            else:
                return Parallel()
        #universal cheats
        case 'Desperation':
            camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'Desperation2':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'KnockbackThrow' | 'KnockbackSquirt':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'ComboThrow' | 'ComboSquirt' | 'ComboDrop':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'AbilityQueued' | 'AbilityQueuedPreToon':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'SynergyFees':
            camTrack.append(defaultCamera(openShotDuration=1.5))
        case 'CalculatingFees':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'DeathCheck':
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
        case 'CogSpawn':
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
        case 'TargetCheck' | 'AmbassadorTargetCheck':
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
        case 'UnstableTransformation':
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'DrenchDecrement':
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'SoakRemoval':
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'OilRemoval':
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'GovernaughtDeath':
            camTrack2 = Sequence(heldShot(10, 0, 10, 115, -30, 0, attackDuration))
            return camTrack2
        case 'MarkRemoval':
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'LureRemovalPreToon' | 'LureRemoval' | 'LureRemovalHeal' | 'LureRemovalTrap' | 'LureRemovalLure' | 'LureRemovalSound' | 'LureRemovalThrow' | 'LureRemovalSquirt' | 'LureRemovalZap' | 'LureRemovalDrop':
            camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
            return camTrack2
        case 'SueApplication':
            camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
            return camTrack2
        case 'SueRemoval':
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
        case 'AbsorbMovie':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'AbsorbMovieLevel':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'AbsorbMovieLure' | 'AbsorbMovieThrow' | 'AbsorbMovieSquirt' | 'AbsorbMovieZap' | 'AbsorbMovieSound' | 'AbsorbMovieDrop':
            camTrack2 = Sequence(
                motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit),
                Wait(attackDuration)
            )
            return camTrack2
        
        case 'AbsorbMovieLevelLure' | 'AbsorbMovieLevelThrow' | 'AbsorbMovieLevelSquirt' | 'AbsorbMovieLevelZap' | 'AbsorbMovieLevelSound' | 'AbsorbMovieLevelDrop':
            camTrack2 = Sequence(
                motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit),
                Wait(attackDuration)
            )
            return camTrack2
        case 'ZapMovie':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'SueDamage':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'SyphonMovie':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'DamageMovie':
            camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
            return camTrack2
        case 'BanLevel4' | 'BanLevel5' | 'BanLevel6' | 'BanLevel7' | 'BanLevel8' | 'BanToonup' | 'BanTrap' | 'BanLure' | 'BanThrow' | 'BanSquirt' | 'BanZap' | 'BanSound' | 'BanDrop':
            banDesc = {
                'BanLevel4': 'Level 4 gags are off-limits!',
                'BanLevel5': 'Level 5 gags are off-limits!',
                'BanLevel6': 'Level 6 gags are off-limits!',
                'BanLevel7': 'Level 7 gags are off-limits!',
                'BanLevel8': 'Level 8 gags are off-limits!',
                'BanToonup': 'Toon-Up gags are off-limits!',
                'BanTrap': 'Trap gags are off-limits!',
                'BanLure': 'Lure gags are off-limits!',
                'BanThrow': 'Throw gags are off-limits!',
                'BanSquirt': 'Squirt gags are off-limits!',
                'BanZap': 'Zap gags are off-limits!',
                'BanSound': 'Sound gags are off-limits!',
                'BanDrop': 'Drop gags are off-limits!'
            }
        
            camTrack2 = defaultCamera(openShotDuration=0.5)
            pbpText = attack['playByPlayText']
            pbpTrack = pbpText.getShowInterval(('Wire Cut!', banDesc[name]), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            if attack['suit'].dna.name == 'wtapper':
                return Parallel(pbpTrack, camTrack2)
            else:
                camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        
        case 'BanLevel45' | 'BanLevel46' | 'BanLevel47' | 'BanLevel48' | 'BanLevel56' | 'BanLevel57' | 'BanLevel58' | 'BanLevel67' | 'BanLevel68' | 'BanLevel78':
            banDesc = {
                'BanLevel45': 'Level 4 and 5 gags are off-limits!',
                'BanLevel46': 'Level 4 and 6 gags are off-limits!',
                'BanLevel47': 'Level 4 and 7 gags are off-limits!',
                'BanLevel48': 'Level 4 and 8 gags are off-limits!',
                'BanLevel56': 'Level 5 and 6 gags are off-limits!',
                'BanLevel57': 'Level 5 and 7 gags are off-limits!',
                'BanLevel58': 'Level 5 and 8 gags are off-limits!',
                'BanLevel67': 'Level 6 and 7 gags are off-limits!',
                'BanLevel68': 'Level 6 and 8 gags are off-limits!',
                'BanLevel78': 'Level 7 and 8 gags are off-limits!'
            }
        
            camTrack2 = Sequence(randomActorShot(suit, battle, 3, 'suit'), defaultCamera(openShotDuration=0, attackDuration=attackDuration -3))
            camTrack3 = defaultCamera(openShotDuration=0.5)
            camTrack4 = defaultCamera(openShotDuration=1.5)
            pbpText = attack['playByPlayText']
            pbpTrack = pbpText.getShowInterval(('Contingency Clause!', banDesc[name]), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            pbpTrack2 = pbpText.getShowInterval(('Wire Cut!', banDesc[name]), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            pbpTrack3 = pbpText.getShowInterval(('Contract Enforcement!', banDesc[name]), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            match attack['suit'].dna.name:
                case 'cdirector':
                    return Parallel(pbpTrack, camTrack2)
                case 'wtapper':
                    return Parallel(pbpTrack2, camTrack3)
                case 'ubuster':
                    return Parallel(pbpTrack3, camTrack4)
                case _:
                    camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'BanToonupTrap' | 'BanToonupLure' | 'BanToonupThrow' | 'BanToonupSquirt' | 'BanToonupZap' | 'BanToonupSound' | 'BanToonupDrop' | 'BanTrapLure' | 'BanTrapThrow' | 'BanTrapSquirt' | 'BanTrapZap' | 'BanTrapSound' | 'BanTrapDrop' | 'BanLureThrow' | 'BanLureSquirt' | 'BanLureZap' | 'BanLureSound' | 'BanLureDrop' | 'BanThrowSquirt' | 'BanThrowZap' | 'BanThrowSound' | 'BanThrowDrop' | 'BanSquirtZap' | 'BanSquirtSound' | 'BanSquirtDrop' | 'BanZapSound' | 'BanZapDrop' | 'BanSoundDrop':
            banDesc = {
                'BanToonupTrap': 'Toon-Up and Trap gags are off-limits!',
                'BanToonupLure': 'Toon-Up and Lure gags are off-limits!',
                'BanToonupThrow': 'Toon-Up and Throw gags are off-limits!',
                'BanToonupSquirt': 'Toon-Up and Squirt gags are off-limits!',
                'BanToonupZap': 'Toon-Up and Zap gags are off-limits!',
                'BanToonupSound': 'Toon-Up and Sound gags are off-limits!',
                'BanToonupDrop': 'Toon-Up and Drop gags are off-limits!',
                'BanTrapLure': 'Trap and Lure gags are off-limits!',
                'BanTrapThrow': 'Trap and Throw gags are off-limits!',
                'BanTrapSquirt': 'Trap and Squirt gags are off-limits!',
                'BanTrapZap': 'Trap and Zap gags are off-limits!',
                'BanTrapSound': 'Trap and Sound gags are off-limits!',
                'BanTrapDrop': 'Trap and Drop gags are off-limits!',
                'BanLureThrow': 'Lure and Throw gags are off-limits!',
                'BanLureSquirt': 'Lure and Squirt gags are off-limits!',
                'BanLureZap': 'Lure and Zap gags are off-limits!',
                'BanLureSound': 'Lure and Sound gags are off-limits!',
                'BanLureDrop': 'Lure and Drop gags are off-limits!',
                'BanThrowSquirt': 'Throw and Squirt gags are off-limits!',
                'BanThrowZap': 'Throw and Zap gags are off-limits!',
                'BanThrowSound': 'Throw and Sound gags are off-limits!',
                'BanThrowDrop': 'Throw and Drop gags are off-limits!',
                'BanSquirtZap': 'Squirt and Zap gags are off-limits!',
                'BanSquirtSound': 'Squirt and Sound gags are off-limits!',
                'BanSquirtDrop': 'Squirt and Drop gags are off-limits!',
                'BanZapSound': 'Zap and Sound gags are off-limits!',
                'BanZapDrop': 'Zap and Drop gags are off-limits!',
                'BanSoundDrop': 'Sound and Drop gags are off-limits!'
            }
        
            camTrack2 = defaultCamera(openShotDuration=2.5)
            camTrack3 = defaultCamera(openShotDuration=0.5)
            pbpText = attack['playByPlayText']
            pbpTrack = pbpText.getShowInterval(('Contingency Clause!', banDesc[name]), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            pbpTrack2 = pbpText.getShowInterval(('Wire Cut!', banDesc[name]), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        
            match attack['suit'].dna.name:
                case 'cdirector':
                    return Parallel(pbpTrack, camTrack2)
                case 'wtapper':
                    return Parallel(pbpTrack2, camTrack3)
                case _:
                    camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'DisableToonupTrap' | 'DisableToonupLure' | 'DisableToonupThrow' | 'DisableToonupSquirt' | 'DisableToonupZap' | 'DisableToonupSound' | 'DisableToonupDrop' | 'DisableTrapLure' | 'DisableTrapThrow' | 'DisableTrapSquirt' | 'DisableTrapZap' | 'DisableTrapSound' | 'DisableTrapDrop' | 'DisableLureThrow' | 'DisableLureSquirt' | 'DisableLureZap' | 'DisableLureSound', 'DisableLureDrop' | 'DisableThrowSquirt' | 'DisableThrowZap' | 'DisableThrowSound' | 'DisableThrowDrop' | 'DisableSquirtZap' | 'DisableSquirtSound' | 'DisableSquirtDrop' | 'DisableZapSound' | 'DisableZapDrop' | 'DisableSoundDrop' | 'DisableLevel45' | 'DisableLevel46' | 'DisableLevel47' | 'DisableLevel48' | 'DisableLevel56' | 'DisableLevel57' | 'DisableLevel58' | 'DisableLevel67' | 'DisableLevel68' | 'DisableLevel78':
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        case 'GagBanRetaliationHeal' | 'GagBanRetaliationTrap' | 'GagBanRetaliationLure' | 'GagBanRetaliationThrow' | 'GagBanRetaliationSquirt' | 'GagBanRetaliationZap' | 'GagBanRetaliationSound' | 'GagBanRetaliationDrop':
            pbpText = attack['playByPlayText']
            pbpTrackUnionBuster = pbpText.getShowInterval(('Breach Of Contract', 'The Union Buster retaliates against Toons who chose banned gags!'), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            pbpTrackContingency = pbpText.getShowInterval(('Contingency Clause!', 'The Contingency Director punishes Toons for using banned gags!'), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            pbpTrackRacketeer = pbpText.getShowInterval(('Corporate Dominion!', 'The Racketeer retaliates against Toons who used banned gags!'), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            pbpTrackWiretapper = pbpText.getShowInterval(('Wire Cut!', 'Due to an overinflated budget this toon takes {!s} damage!'.format(attack['target'][0]['hp'])), attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
            camTrack2 = Parallel(Wait(attackDuration), Sequence(heldRelativeShot(target[0]['toon'], 3, 10, 3, 163, 0, 0, 2.5, "courtRecordDamageHeldShot"), LerpFunctionInterval(camera.setP, 0.5, fromData=0, toData=10)))
            camTrack3 = Parallel(Wait(attackDuration), Sequence(heldRelativeShot(target[0]['toon'], 3, 10, 3, 163, 0, 0, 2.5, "courtRecordDamageHeldShot")))
            camTrackRacketeer = defaultCamera(openShotDuration=1.5)
            camTrackUnionBuster = defaultCamera(openShotDuration=0.75)
            camTrackContingnency = Sequence(defaultCamera(openShotDuration=0, attackDuration=3), defaultCamera(openShotDuration=1.5, attackDuration=attackDuration-3))
            if attackDuration > 2.0:
                match suit.dna.name:
                    case 'wtapper':
                        return Parallel(pbpTrackWiretapper, camTrack3)
                    case 'racket':
                        return Parallel(pbpTrackRacketeer, camTrackRacketeer)
                    case 'cdirector':
                        return Parallel(pbpTrackContingency, camTrackContingnency)
                    case 'ubuster':
                        return Parallel(pbpTrackUnionBuster, camTrackUnionBuster)
            else:
                return camTrack2
        case _:
            camTrack.append(defaultCamera())
    pbpText: PlayByPlayText.PlayByPlayText = attack['playByPlayText']
    displayName = TTLocalizer.SuitAttackNames.get(attack['name'], '')
    currentHp = attack['currentHp']
    maxHp = attack['maxHp']

    hpPercent = float(currentHp) / float(maxHp) if maxHp > 0 else 0.0

    def getTextColor() -> tuple[float, float, float, float]:
        # Cheat logic will have to be handled another way.
        if hpPercent >= 1.5:
            return (1.0, 0.0, 1.0, 1.0)
        elif hpPercent > 1.0:
            return (0.0, 0.949, 1.0, 1.0)
        else:
            return (1.0, 0.0, 0.0, 1.0)

    if attack['name'] in TTLocalizer.SuitCheatNames:
        pbpDc = PlayByPlayText.PlayByPlayText()
        if name in (
            'ForemanRedTape',
            'ForemanBurning',
            'MintCompoundingInterest',
            'ErfitWringOut',
            'PresidentDriver',
            'PowerhouseSnipeSoaked',
        ):
            pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=getTextColor, posOverride=lambda: (0.0, 0.775))
        else:
            pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=lambda: (0.45, 0.45, 1.0, 1.0), posOverride=lambda: (0.0, 0.775))
        return Parallel(camTrack, pbpTrack)
    else:
        pbpTrack = pbpText.getShowInterval(displayName, attackDuration, colorOverride=getTextColor)
    track = Sequence(Parallel(camTrack, pbpTrack))
    return track

def chooseSuitCloseShot(attack, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    if duration < 0:
        duration = 1e-06
    groupStatus = attack['group']
    diedTrack = None
    battle = attack['battle']
    if groupStatus == ATK_TGT_SINGLE:
        av = attack['target'][0]['toon']
        shotChoices = [avatarCloseUpThreeQuarterRightShot, suitGroupThreeQuarterLeftBehindShot]
        died = attack['target'][0]['died']
        if died != 0:
            pbpText = attack['playByPlayText']
            diedText = av.getName() + ' was defeated!'
            diedTextList = [diedText]
            diedTrack = pbpText.getToonsDiedInterval(diedTextList, 3.5)
    else:
        av = None
        shotChoices = [avatarCloseUpThreeQuarterRightShot, suitGroupThreeQuarterLeftBehindShot]
        targetDicts = attack['target']
        deadToons = []

        for targetDict in targetDicts:
            died = targetDict.get('died', 0)

            if died != 0 and 'toon' in targetDict:
                deadToons.append(targetDict['toon'])

        if len(deadToons) > 0:
            pbpText = attack['playByPlayText']
            diedTextList = []
            for toon in deadToons:
                pbpText = attack['playByPlayText']
                diedTextList.append(toon.getName() + ' was defeated!')

            diedTrack = pbpText.getToonsDiedInterval(diedTextList, 3.5)
    track = random.choice(shotChoices)(*[av, duration, battle])
    return track


def makeShot(x, y, z, h, p, r, duration, other = None, name = 'makeShot'):
    if other:
        return heldRelativeShot(other, x, y, z, h, p, r, duration, name)
    else:
        return heldShot(x, y, z, h, p, r, duration, name)


def focusShot(x, y, z, duration, target, other = None, splitFocusPoint = None, name = 'focusShot'):
    track = Sequence()
    if other:
        track.append(Func(camera.setPos, other, Point3(x, y, z)))
    else:
        track.append(Func(camera.setPos, Point3(x, y, z)))
    if splitFocusPoint:
        track.append(Func(focusCameraBetweenPoints, target, splitFocusPoint))
    else:
        def lookAtTarget():
            camera.lookAt(target() if callable(target) else target)

        track.append(Func(lookAtTarget))
    track.append(Wait(duration))
    return track


def moveShot(x, y, z, h, p, r, duration, other = None, name = 'moveShot'):
    return motionShot(x, y, z, h, p, r, duration, other, name)


def focusMoveShot(x, y, z, duration, target, other = None, name = 'focusMoveShot'):
    camera.setPos(Point3(x, y, z))
    camera.lookAt(target)
    hpr = camera.getHpr()
    return motionShot(x, y, z, hpr[0], hpr[1], hpr[2], duration, other, name)


def chooseSOSShot(av, duration):
    shotChoices = [
     avatarBehindShot,
     avatarBehindHighShot]
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseRewardShot(av, duration, allowGroupShot = 1):

    def chooseRewardShotNow(av):
        if av.playingAnim == 'victory' or not allowGroupShot:
            shotChoices = [(0,
              8,
              av.getHeight() * 0.66,
              179,
              15,
              0), (5.2,
              5.45,
              av.getHeight() * 0.66,
              131.5,
              3.6,
              0)]
            shot = random.choice(shotChoices)
            camera.setPosHpr(av, *shot)
        else:
            camera.setPosHpr(10, 0, 10, 115, -30, 0)

    return Sequence(Func(chooseRewardShotNow, av), Wait(duration))


def heldShot(x, y, z, h, p, r, duration, name = 'heldShot'):
    track = Sequence(name=name)
    track.append(Func(camera.setPosHpr, x, y, z, h, p, r))
    track.append(Wait(duration))
    return track


def heldRelativeShot(other, x, y, z, h, p, r, duration, name = 'heldRelativeShot'):
    track = Sequence(name=name)
    track.append(Func(camera.setPosHpr, other, x, y, z, h, p, r))
    track.append(Wait(duration))
    return track

def motionShot(x, y, z, h, p, r, duration, other = None, name = 'motionShot'):
    if other:
        posTrack = LerpPosInterval(camera, duration, pos=Point3(x, y, z), other=other, blendType='easeInOut')
        hprTrack = LerpHprInterval(camera, duration, hpr=Point3(h, p, r), other=other, blendType='easeInOut')
    else:
        posTrack = LerpPosInterval(camera, duration, pos=Point3(x, y, z), blendType='easeInOut')
        hprTrack = LerpHprInterval(camera, duration, hpr=Point3(h, p, r), blendType='easeInOut')
    return Parallel(posTrack, hprTrack)

def moveCameraOnly(x, y, z, duration, other=None,
                   h=None, p=None, r=None, startH=None, startP=None, startR=None,
                   name='moveCameraOnly'):

    if other:
        posTrack = LerpPosInterval(
            camera,
            duration,
            pos=Point3(x, y, z),
            other=other, blendType='easeInOut'
        )
    else:
        posTrack = LerpPosInterval(
            camera,
            duration,
            pos=Point3(x, y, z), blendType='easeInOut'
        )

    currentHpr = camera.getHpr()

    startingH = 180 if startH is None else startH
    startingP = currentHpr[1] if startP is None else startP
    startingR = currentHpr[2] if startR is None else startR

    targetH = currentHpr[0] if h is None else h
    targetP = currentHpr[1] if p is None else p
    targetR = currentHpr[2] if r is None else r

    hprTrack = LerpHprInterval(
        camera,
        duration,
        hpr=Point3(targetH, targetP, targetR),
        startHpr=Point3(startingH, startingP, startingR), other=other, blendType='easeInOut'
    )

    return Parallel(
        posTrack,
        hprTrack,
        name=name
    )


# def motionShot(x, y, z, h, p, r, duration, other=None, name='motionShot'):
#     if other:
#         # Get the camera's current rotation relative to the target.
#         startHpr = camera.getHpr(other)

#         # Normalize heading so Panda takes the shortest path
#         # to the requested heading.
#         while startHpr.getX() - h > 180:
#             startHpr.setX(startHpr.getX() - 360)

#         while startHpr.getX() - h < -180:
#             startHpr.setX(startHpr.getX() + 360)

#         # Do the same for pitch.
#         while startHpr.getY() - p > 180:
#             startHpr.setY(startHpr.getY() - 360)

#         while startHpr.getY() - p < -180:
#             startHpr.setY(startHpr.getY() + 360)

#         # And roll.
#         while startHpr.getZ() - r > 180:
#             startHpr.setZ(startHpr.getZ() - 360)

#         while startHpr.getZ() - r < -180:
#             startHpr.setZ(startHpr.getZ() + 360)

#         posTrack = LerpPosInterval(
#             camera,
#             duration,
#             pos=Point3(x, y, z),
#             other=other,
#             blendType='easeInOut'
#         )

#         hprTrack = LerpHprInterval(
#             camera,
#             duration,
#             hpr=Point3(h, p, r),
#             startHpr=startHpr,
#             other=other,
#             blendType='easeInOut'
#         )

#     else:
#         startHpr = camera.getHpr()

#         while startHpr.getX() - h > 180:
#             startHpr.setX(startHpr.getX() - 360)

#         while startHpr.getX() - h < -180:
#             startHpr.setX(startHpr.getX() + 360)

#         while startHpr.getY() - p > 180:
#             startHpr.setY(startHpr.getY() - 360)

#         while startHpr.getY() - p < -180:
#             startHpr.setY(startHpr.getY() + 360)

#         while startHpr.getZ() - r > 180:
#             startHpr.setZ(startHpr.getZ() - 360)

#         while startHpr.getZ() - r < -180:
#             startHpr.setZ(startHpr.getZ() + 360)

#         posTrack = LerpPosInterval(
#             camera,
#             duration,
#             pos=Point3(x, y, z),
#             blendType='easeInOut'
#         )

#         hprTrack = LerpHprInterval(
#             camera,
#             duration,
#             hpr=Point3(h, p, r),
#             startHpr=startHpr,
#             blendType='easeInOut'
#         )

#     return Parallel(
#         posTrack,
#         hprTrack,
#         name=name
#     )


def allGroupShot(avatar, duration, battle=None):
    return heldShot(10, 0, 10, 89, -30, 0, duration, "allGroupShot")


def allGroupLowShot2(avatar, duration, battle=None):
    return heldShot(15, 0, 3, 89, 0, 0, duration, 'allGroupLowShot')


def allGroupLowShot(avatar, duration, battle=None):

    def getWidth(s):
        if s is None or s.getGeomNode() is None:
            return 0
        width = (
            s.getGeomNode().getScale()[0]
        )
        # Enforce a minimum width.
        return max(width, 4)

    if battle.activeSuits:
        # Get the width of each suit in the actor list.
        width = [getWidth(s) for s in battle.activeSuits]

        # Calculate the total sum of the suit widths.
        widthSum = sum(width)

        # Get the ratio of the maximum suit width allowed to the
        # width sum.
        widthRatio = max(widthSum / 18, 1)

        # If the ratio wasn't capped, it can be applied to the
        # width sum.
        if widthRatio > 1:
            widthSum -= (10 * widthRatio) - 10
        x = max(min(15 * (widthSum / 20), 20), 15)
        y = -len(battle.activeSuits)
        h = 90 - (len(battle.activeSuits) * 3)
        p = max([suit.getHeight() + 1 for suit in battle.activeSuits]) / 2
    else:
        x = 15
        y = 3
        h = 90
        p = 0
    return heldShot(x, y, 3, h, p, 0, duration, "allGroupLowShot")


def allGroupLowDiagonalShot(avatar, duration, battle=None):
    return heldShot(7, 5, 6, 119, -30, 0, duration, 'allGroupLowShot')


def allGroupHighShot(avatar, duration, battle=None):
    return heldShot(0, -15, 8, 0, -10, 0, duration, 'allGroupHighShot')


def toonGroupShot(avatar, duration, battle=None):
    return heldShot(10, 0, 10, 115, -30, 0, duration, 'toonGroupShot')


def toonGroupHighShot(avatar, duration, battle=None):
    return heldShot(5, 0, 1, 115, 45, 0, duration, 'toonGroupHighShot')


def suitGroupShot(avatar, duration, battle=None):
    return heldShot(10, 0, 10, 65, -30, 0, duration, 'suitGroupShot')


def suitGroupLowLeftShot(avatar, duration, battle=None):
    return heldShot(8.4, -3.85, 2.75, 36.3, 3.25, 0, duration, 'suitGroupLowLeftShot')


def suitGroupThreeQuarterLeftBehindShot(avatar, duration, battle=None):
    """Good for toon throws, and some suit magic attacks."""
    if battle.activeSuits:
        suitHeight = max([suit.getHeight() + 1 for suit in battle.activeSuits])
    else:
        suitHeight = 1

    if MovieUtil.shotDirection == "left":
        x = -12.37
        h = -134.61
    else:
        x = 12.37
        h = 134.61

    return heldShot(
        x,
        11.5,
        max(min(suitHeight + 1.5, 15.16), 8.16),
        h,
        -max(min(15 * (suitHeight / 5), 40), 15),
        0,
        duration,
        "suitGroupThreeQuarterLeftBehindShot",
    )


def suitWakeUpShot(avatar, duration, battle=None):
    return heldShot(10, -5, 10, 65, -30, 0, duration, 'suitWakeUpShot')


def suitCameraShakeShot(duration, shakeIntensity: float, quake = 0, extraDelay: float = 0.0):
    track = Sequence(name='suitShakeCameraShot')
    shakeDelay: float
    numShakes: int
    postShakeDelay: float
    if quake == 1:
        shakeDelay = 1.375
        numShakes = 4
        postShakeDelay = 0.75
    else:
        shakeDelay = 0.525
        numShakes = 5
        postShakeDelay = 0.5
    shakeDuration = (duration - shakeDelay - postShakeDelay - extraDelay) / numShakes

    def shakeCameraTrack(shakeIntensity: float, perShakeDuration, numShakes: int = 4, shakeRate: float = 60.0):
        shakeTrack = Sequence(name='miniShakeCameraShot')

        # calculate how quick we move each random shake in each stomp
        playRate = 1.0 / shakeRate
        # determine how many mini-shakes per stomp
        miniShakeAmt = int(perShakeDuration / playRate)

        for shakeNo in range(numShakes):
            # determine each mini-shake in each stomp with shakeDuration / play rate
            # shakeTrack.append(Func(print, f'shakeIntensity={shakeIntensity}, perShakeDuration={perShakeDuration}, numShakes={numShakes}, shakeRate={shakeRate}, miniShakeAmt={miniShakeAmt}'))
            for playIter in range(miniShakeAmt):
                randY = (random.random() * 2.0) - 1.0
                randZ = (random.random() * 2.0) - 1.0
                # set x & z with a displacement that depends on 'how long' we've been shaking the screen for
                displacement = (1 - (playIter / miniShakeAmt)) * shakeIntensity
                # clamp ranges within [-1.0, 1.0) for camera.lookAt()
                randY = min(max(randY * displacement, -1.0), 1.0)
                randZ = min(max(randZ * displacement, -1.0), 1.0)
                # shakeTrack.append(Func(print, f'playIter {playIter}, x={randY}, z={randZ}, displacement={displacement}'))
                shakeTrack.append(Func(camera.lookAt, 0.0, randY, randZ))
                # make sure the camera waits for this mini-shake to finish before going to the next mini-shake
                shakeTrack.append(Wait(playRate))

            # reset to pos(0.0, 0.0, 0.0) after each stomp
            shakeTrack.append(Func(camera.lookAt, 0.0, 0.0, 0.0))

        # return the shake sequence that we have thus calculated with dark magicks
        return shakeTrack

    # Allow a reasonable degree of randomness in the camera's positioning
    x = 13.0 + random.random() * 3.0
    if random.random() > 0.5:
        x = -x
    z = 12.0 + random.random() * 3.0
    # Let the camera display the toons
    track.append(Func(camera.setPos, x, -5.0, z))

    # Point the camera at the center of the battle, to shoot all the actors
    track.append(Func(camera.lookAt, Point3(0.0, 0.0, 0.0)))
    track.append(Wait(shakeDelay + extraDelay))
    track.append(shakeCameraTrack(shakeIntensity, shakeDuration, numShakes=numShakes))
    track.append(Wait(postShakeDelay))
    return track


def avatarCloseUpShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 0, 8, avatar.getHeight() * 0.66, 179, 15, 0, duration, 'avatarCloseUpShot')


def avatarCloseUpThrowShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 3, 8, avatar.getHeight() * 0.66, 159, 3.6, 0, duration, 'avatarCloseUpThrowShot')


def avatarCloseUpThreeQuarterRightShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 5.2, 5.45, avatar.getHeight() * 0.66, 131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterRightShot')


def avatarCloseUpThreeQuarterRightShotWide(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 7.2, 8.45, avatar.getHeight() * 0.66, 131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterRightShot')


def avatarCloseUpThreeQuarterLeftShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, -5.2, 5.45, avatar.getHeight() * 0.66, -131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterLeftShot')


def avatarCloseUpThreeQuarterRightFollowShot(avatar, duration, battle=None):
    track = Sequence(name='avatarCloseUpThreeQuarterRightFollowShot')
    track.append(heldRelativeShot(avatar, 5.2, 5.45, avatar.getHeight() * 0.66, 131.5, 3.6, 0, duration * 0.65))
    track.append(LerpHprInterval(nodePath=camera, other=avatar, duration=duration * 0.2, hpr=Point3(110, 3.6, 0), blendType='easeInOut'))
    track.append(Wait(duration * 0.25))
    return track


def avatarCloseUpZoomShot(avatar, duration, battle=None):
    track = Sequence('avatarCloseUpZoomShot')
    track.append(LerpPosHprInterval(nodePath=camera, other=avatar, duration=duration / 2, startPos=Point3(0, 10, avatar.getHeight()), startHpr=Point3(179, -10, 0), pos=Point3(0, 6, avatar.getHeight()), hpr=Point3(179, -10, 0), blendType='easeInOut'))
    track.append(Wait(duration / 2))
    return track


def avatarBehindShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 5, -7, avatar.getHeight(), 40, -12, 0, duration, 'avatarBehindShot')


def avatarBehindHighShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, -4, -7, 5 + avatar.getHeight(), -30, -35, 0, duration, 'avatarBehindHighShot')


def avatarBehindHighRightShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 4, -7, 5 + avatar.getHeight(), 30, -35, 0, duration, 'avatarBehindHighShot')


def avatarBehindThreeQuarterRightShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 7.67, -8.52, avatar.getHeight() * 0.66, 25, 7.5, 0, duration, 'avatarBehindThreeQuarterRightShot')


def avatarSideFollowAttack(suit, toon, duration, battle):
    windupDuration = duration * (0.1 + random.random() * 0.1)
    projectDuration = duration * 0.75
    impactDuration = duration - windupDuration - projectDuration
    suitHeight = suit.getHeight()
    toonHeight = toon.getHeight()
    suitCentralPoint, origHpr = battle.getActorPosHpr(suit)
    suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
    toonCentralPoint, origHpr = battle.getActorPosHpr(toon)
    toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
    initialX = random.randint(12, 14)
    finalX = random.randint(7, 8)
    initialY = finalY = random.randint(-3, 0)
    initialZ = suitHeight * 0.5 + random.random() * suitHeight
    finalZ = toonHeight * 0.5 + random.random() * toonHeight
    if random.random() > 0.5:
        initialX = -initialX
        finalX = -finalX
    return Sequence(focusShot(initialX, initialY, initialZ, windupDuration, suitCentralPoint), focusMoveShot(finalX, finalY, finalZ, projectDuration, toonCentralPoint), Wait(impactDuration))


def focusCameraBetweenPoints(point1, point2):
    if point1[0] > point2[0]:
        x = point2[0] + (point1[0] - point2[0]) * 0.5
    else:
        x = point1[0] + (point2[0] - point1[0]) * 0.5
    if point1[1] > point2[1]:
        y = point2[1] + (point1[1] - point2[1]) * 0.5
    else:
        y = point1[1] + (point2[1] - point1[1]) * 0.5
    if point1[2] > point2[2]:
        z = point2[2] + (point1[2] - point2[2]) * 0.5
    else:
        z = point1[2] + (point2[2] - point1[2]) * 0.5
    camera.lookAt(Point3(x, y, z))


def randomCamera(suit, toon, battle, attackDuration, openShotDuration):
    return randomAttackCam(suit, toon, battle, attackDuration, openShotDuration, 'suit')


def randomAttackCam(suit, target, battle, attackDuration, openShotDuration, attackerString='suit', defenderString='toon'):
    if openShotDuration > attackDuration:
        openShotDuration = attackDuration

    closeShotDuration = attackDuration - openShotDuration

    if attackerString == 'suit':
        attacker = suit
        defender = target
    else:
        attacker = target
        defender = suit

    randomDouble = random.random()

    if randomDouble > 0.6:
        openShot = randomActorShot(attacker, battle, openShotDuration, attackerString)

    elif randomDouble > 0.2:
        openShot = randomOverShoulderShot(suit, target, battle, openShotDuration, focus=attackerString)

    else:
        openShot = randomActorShot(attacker, battle, openShotDuration, attackerString)

    randomDouble = random.random()

    if randomDouble > 0.6:
        closeShot = randomActorShot(defender, battle, closeShotDuration, defenderString)

    elif randomDouble > 0.2:
        closeShot = randomOverShoulderShot(suit, target, battle, closeShotDuration, focus=defenderString)

    else:
        closeShot = randomActorShot(defender, battle, closeShotDuration, defenderString)

    return Sequence(openShot, closeShot)

def randomAttackCamCheat(suit, toon, battle, attackDuration, openShotDuration, attackerString = 'suit'):
    if openShotDuration > attackDuration:
        openShotDuration = attackDuration
    closeShotDuration = attackDuration - openShotDuration
    if attackerString == 'suit':
        attacker = suit
        defender = toon
        defenderString = 'toon'
    else:
        attacker = toon
        defender = suit
        defenderString = 'suit'
    randomDouble = random.random()
    if randomDouble > 0.6:
        openShot = randomActorShot(attacker, battle, openShotDuration, attackerString)
    elif randomDouble > 0.2:
        openShot = randomOverShoulderShot(suit, toon, battle, openShotDuration, focus=attackerString)
    else:
        openShot = randomActorShot(defender, battle, closeShotDuration, defenderString)
    randomDouble = random.random()
    if randomDouble > 0.6:
        closeShot = randomActorShot(defender, battle, closeShotDuration, defenderString)
    elif randomDouble > 0.2:
        closeShot = randomOverShoulderShot(suit, toon, battle, closeShotDuration, focus=defenderString)
    else:
        closeShot = randomActorShot(defender, battle, closeShotDuration, defenderString)
    return Sequence(openShot, closeShot)

def fromBehindGroupCam(suit, targets, battle, attackDuration, openShotDuration):
    if openShotDuration > attackDuration:
        openShotDuration = attackDuration
    closeShotDuration = attackDuration - openShotDuration
    openShot = fromForwardGroupShot(targets, suit, openShotDuration, battle)
    closeShot = fromBehindGroupShot(targets, suit, closeShotDuration, battle)
    return Sequence(openShot, closeShot)

def randomManagerCheatCam(suit, targets, battle, attackDuration, openShotDuration):
    if openShotDuration > attackDuration:
        openShotDuration = attackDuration
    openShot = randomActorShot(suit, battle, openShotDuration, 'suit', groupShot=0)
    return Sequence(openShot)


def randomGroupAttackCam(suit, targets, battle, attackDuration, openShotDuration):
    if openShotDuration > attackDuration:
        openShotDuration = attackDuration

    closeShotDuration = attackDuration - openShotDuration
    openShot = randomActorShot(suit, battle, openShotDuration, 'suit', groupShot=0)
    closeShot = randomTargetGroupShot(targets, suit, closeShotDuration, battle)

    return Sequence(openShot, closeShot)


def randomActorShot(actor, battle, duration, actorType, groupShot=0):
    height = actor.getHeight()

    def getCentralPoint():
        centralPoint = actor.getPos(battle)
        centralPoint.setZ(centralPoint.getZ() + height * 0.75)
        return centralPoint

    def getRandom():
        return random.random()

    if actorType == "suit":
        x = 4 + getRandom() * 8
        y = -2 - getRandom() * 4
        z = height * 0.5 + getRandom() * height * 1.5
        if groupShot == 1:
            y = -4
            z = height * 0.5
    else:
        x = 2 + getRandom() * 8
        y = -2 + getRandom() * 3
        z = height + getRandom() * height * 1.5
        if groupShot == 1:
            y = y + 3
            z = height * 0.5
    if MovieUtil.shotDirection == "left":
        x = -x

    return focusShot(x, y, z, duration, getCentralPoint)

def randomActorShotFallingKnife(actor, battle, duration, actorType, groupShot = 0):
    height = actor.getHeight()
    centralPoint, origHpr = battle.getActorPosHpr(actor)
    centralPoint.setZ(centralPoint.getZ() + height * 0.75)
    if actorType == 'suit':
        x = 4 + random.random() * 8
        y = -2 - random.random() * 4
        z = height * 0.5 + random.random() * height * 1.5
        if groupShot == 1:
            y = -4
            z = height * 0.5
    else:
        x = 2 + random.random() * 8
        y = -2 + random.random() * 3
        z = height + random.random() * height * 1.5
        if groupShot == 1:
            y = y + 3
            z = height * 0.5
    if MovieUtil.shotDirection == 'left':
        x = -x
    return focusShot(x, y, z, duration, centralPoint)

def randomActorShotCourtRecord(actor, battle, duration, actorType, groupShot = 0):
    height = actor.getHeight()
    centralPoint, origHpr = battle.getActorPosHpr(actor)
    centralPoint.setZ(centralPoint.getZ() + height * 0.75)
    if actorType == 'suit':
        x = 4 + random.random() * 8
        y = -2 - random.random() * 4
        z = height * 0.5 + random.random() * height * 1.5
        if groupShot == 1:
            y = -4
            z = height * 0.5
    else:
        x = 2 + random.random() * 8
        y = -2 + random.random() * 3
        z = height + random.random() * height * 1.5
        if groupShot == 1:
            y = y + 3
            z = height * 0.5
    if MovieUtil.shotDirection == 'left':
        x = -x
    return focusShot(x, y, z, duration, centralPoint)


def randomSplitShot(suit, toon, battle, duration):
    suitHeight = suit.getHeight()
    toonHeight = toon.getHeight()
    suitCentralPoint, origHpr = battle.getActorPosHpr(suit)
    suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
    toonCentralPoint, origHpr = battle.getActorPosHpr(toon)
    toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
    x = 9 + random.random() * 2
    y = -2 - random.random() * 2
    z = suitHeight * 0.5 + random.random() * suitHeight
    if MovieUtil.shotDirection == 'left':
        x = -x
    return focusShot(x, y, z, duration, toonCentralPoint, splitFocusPoint=suitCentralPoint)


def randomOverShoulderShot(suit, toon, battle, duration, focus):
    # the future is now
    # return betterGroupHeldShot(suit, duration)
    """randomOverShouldShot() creates a random, though effective, camera shot for a battle
    shooting the actor specified in arg focus ('avatar' or 'suit') over the shoulder of
    the other actor in the attack"""
    suitHeight = suit.getHeight()
    toonHeight = toon.getHeight()

    def getSuitCentralPoint():
        suitCentralPoint = suit.getPos(battle)
        suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
        return suitCentralPoint

    def getToonCentralPoint():
        toonCentralPoint = toon.getPos(battle)
        toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
        return toonCentralPoint

    x = 2 + random.random() * 10
    if focus == "avatar":
        y = 8 + random.random() * 6
        z = suitHeight * 1.2 + random.random() * suitHeight
    else:
        y = -10 - random.random() * 6
        z = toonHeight * 1.5
    if MovieUtil.shotDirection == "left":
        x = -x

    return focusShot(
    x, y, z, duration,
    getToonCentralPoint(),
    splitFocusPoint=getSuitCentralPoint()
)

def randomCameraSelection(suit, attack, attackDuration, openShotDuration):
    shotChoices = [avatarCloseUpThrowShot,
     avatarCloseUpThreeQuarterLeftShot,
     suitGroupLowLeftShot,
     avatarBehindHighShot]
    if openShotDuration > attackDuration:
        openShotDuration = attackDuration
    closeShotDuration = attackDuration - openShotDuration
    openShot = random.choice(shotChoices)(*[suit, openShotDuration])
    closeShot = chooseSuitCloseShot(attack, closeShotDuration, openShot.getName(), attackDuration)
    return Sequence(openShot, closeShot)

def randomToonGroupShot(toons, suit, duration, battle):
    """randomToonGroupShot() creates a random, though effective camera shot for a group
    of toons (2, 3, or 4) in a battle"""
    # If no toons are available, just return a random actor shot using the suit
    if len(toons) == 0:
        return randomActorShot(suit, battle, duration, "suit", groupShot=0)

    # Grab the average height of these toons for the best shot
    sum = 0
    for t in toons:
        toon = t["avatar"]
        height = toon.getHeight()
        sum = sum + height

    avgHeight = (
        sum / len(toons) * 0.75
    )  # Multiply by 0.75 to get the chest of the toon

    # We shoot from the opposite side of the attacking suit
    suitPos = suit.getPos(battle)
    x = 1 + random.random() * 6
    if suitPos.getX() > 0:
        x = -x

    # We'll either shoot a close up or far back over the shoulders of the suits
    if random.random() > 0.5:  # 50% chance
        y = 4 + random.random() * 1
        z = avgHeight + random.random() * 6
    else:
        y = 11 + random.random() * 2
        z = 13 + random.random() * 2
    focalPoint = Point3(0, -4, avgHeight)
    return focusShot(x, y, z, duration, focalPoint)


def chooseFireShot(throws, suitThrowsDict, attackDuration, battle, enterDuration = 0, exitDuration = 0):
    enterShot = chooseNPCEnterShot(throws, enterDuration)
    openShot = chooseFireOpenShot(throws, suitThrowsDict, attackDuration, battle)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseFireCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration, battle)
    exitShot = chooseNPCExitShot(throws, exitDuration)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track

def fromBehindGroupShot(toons, suit, duration, battle):
    sum = 0
    for t in toons:
        toon = t['toon']
        height = toon.getHeight()
        sum = sum + height

    avgHeight = sum / len(toons) * 0.75
    focalPoint = Point3(0, -4, avgHeight)
    return focusShot(0, 2, avgHeight * 2, duration, focalPoint)

def fromForwardGroupShot(toons, suit, duration, battle):
    sum = 0
    for t in toons:
        toon = t['toon']
        height = toon.getHeight()
        sum = sum + height

    avgHeight = sum / len(toons) * 0.75
    focalPoint = Point3(0, 0, avgHeight)
    return focusShot(random.choice([40, -40]), 0, avgHeight * 1.5, duration, focalPoint)


def chooseFireOpenShot(throws, suitThrowsDict, attackDuration, battle):
    numThrows = len(throws)
    av = None
    duration = 3.0
    if numThrows == 1:
        av = throws[0]['toon']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         avatarBehindShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numThrows >= 2 and numThrows <= 4:
        shotChoices = [suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of throws: %s' % numThrows)
    shotChoice = random.choice(shotChoices)
    track = shotChoice(*[av, duration, battle])
    print('chooseFireOpenShot %s' % shotChoice)
    return track


def chooseFireCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration, battle):
    numSuits = len(suitThrowsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[list(suitThrowsDict.keys())[0]]
        shotChoices = [avatarCloseUpFireShot,
         avatarCloseUpThreeQuarterLeftFireShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= BattleGlobals.MaxBattleAvatars or numSuits == 0:
        shotChoices = [suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    shotChoice = random.choice(shotChoices)
    track = shotChoice(*[av, duration, battle])
    print('chooseFireOpenShot %s' % shotChoice)
    return track


def avatarCloseUpFireShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, 7, 17, avatar.getHeight() * 0.66, 159, 3.6, 0, duration, 'avatarCloseUpFireShot')


def avatarCloseUpThreeQuarterLeftFireShot(avatar, duration, battle=None):
    return heldRelativeShot(avatar, -8.2, 8.45, avatar.getHeight() * 0.66, -131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterLeftShot')


def chooseSueShot(throws, suitThrowsDict, attackDuration, battle, enterDuration = 0.0, exitDuration = 0.0):
    '''
    Honestly, this should not be different from the Throw camera considering the animation for suing a Cog is the same as pie-throwing, but with the lawbook prop.
    '''
    return chooseThrowShot(throws, suitThrowsDict, attackDuration, battle, enterDuration=enterDuration, exitDuration=exitDuration)
