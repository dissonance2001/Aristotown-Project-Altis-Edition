import random
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.SuitBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import MovieUtil
import PlayByPlayText
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
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseHealMidShot(heals, attackDuration):
    numHeals = len(heals)
    av = None
    duration = 2.1
    shotChoices = [toonGroupHighShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseHealCloseShot(heals, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    shotChoices = [toonGroupShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseTrapShot(traps, attackDuration, enterDuration = 0, exitDuration = 0):
    enterShot = chooseNPCEnterShot(traps, enterDuration)
    openShot = chooseTrapOpenShot(traps, attackDuration)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseTrapCloseShot(traps, openDuration, openName, attackDuration)
    exitShot = chooseNPCExitShot(traps, exitDuration)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseTrapOpenShot(traps, attackDuration):
    numTraps = len(traps)
    av = None
    duration = 3.0
    shotChoices = [allGroupLowShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseTrapCloseShot(traps, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    shotChoices = [allGroupLowShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseLureShot(lures, attackDuration, enterDuration = 0.0, exitDuration = 0.0):
    enterShot = chooseNPCEnterShot(lures, enterDuration)
    openShot = chooseLureOpenShot(lures, attackDuration)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseLureCloseShot(lures, openDuration, openName, attackDuration)
    exitShot = chooseNPCExitShot(lures, exitDuration)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseLureOpenShot(lures, attackDuration):
    numLures = len(lures)
    av = None
    duration = 3.0
    shotChoices = [allGroupLowShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseLureCloseShot(lures, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    hasTrainTrackTrap = False
    battle = lures[0]['battle']
    for suit in battle.suits:
        if hasattr(suit, 'battleTrap') and suit.battleTrap == UBER_GAG_LEVEL_INDEX:
            hasTrainTrackTrap = True

    if hasTrainTrackTrap:
        shotChoices = [avatarTrainShot]
        av = lures[0]['toon']
    else:
        shotChoices = [allGroupLowShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track

def avatarTrainShot(avatar, duration):
    return heldRelativeShot(avatar, 0, -7, 1 + avatar.getHeight(), 0, 0, 0, duration, 'avatarTrainShot')

def chooseSoundShot(sounds, targets, attackDuration, enterDuration = 0.0, exitDuration = 0.0):
    enterShot = chooseNPCEnterShot(sounds, enterDuration)
    openShot = chooseSoundOpenShot(sounds, targets, attackDuration)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseSoundCloseShot(sounds, targets, openDuration, openName, attackDuration)
    exitShot = chooseNPCExitShot(sounds, exitDuration)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseSoundOpenShot(sounds, targets, attackDuration):
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
        if isUber:
            shotChoices = [avatarCloseUpThreeQuarterRightShotWide, allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        else:
            shotChoices = [avatarCloseUpThreeQuarterRightShot, allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    elif numSounds >= 2 and numSounds <= 4:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of sounds: %s' % numSounds)
    track = apply(random.choice(shotChoices), [av, duration])
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
        Wait(remainTime),
        Func(camera.reparentTo, previousParent),
        Func(camera.setPosHpr, node.getX(), node.getY(), node.getZ(), *node.getHpr()),
        Func(cameraActor.cleanup),
        name=name
    )
    return track

def cameraActorShot2(parent, anim, remainTime = 0.0, name = 'cameraActorShot'):
    battle = parent
    numSuits = len(battle.activeSuits)
    previousParent = camera.getParent()
    path = 'phase_3.5/models/misc/camera_actor'
    cameraActor = Actor.Actor(path, {anim: path + '-' + anim})
    node = cameraActor.find('**/CameraBone')
    track = Sequence(
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(camera.setPosHpr, 0, -29, -12, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=0, endTime=1.97),
        Wait(1.49),
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
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(camera.setPosHpr, 5, -29, -12, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=0, endTime=1.97),
        Wait(1.49),
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
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(camera.setPosHpr, 2.5, -29, -12, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=0, endTime=1.97),
        Wait(1.49),
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
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(camera.setPosHpr, 7.5, -29, -12, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=0, endTime=1.97),
        Wait(1.49),
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
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(camera.setPosHpr, 10, -29, -12, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=0, endTime=1.97),
        Wait(1.49),
        Func(camera.setPosHpr, 10, -34.5, -3.5, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=3.46, endTime=6.25),
        Func(camera.setPosHpr, 10, -22.5, -4, 0, 0, 0),
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
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(camera.setPosHpr, 12.5, -31, -12, 0, 0, 0),
        ActorInterval(cameraActor, anim, startTime=0, endTime=1.97),
        Wait(1.49),
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


def chooseSoundCloseShot(sounds, targets, openDuration, openName, attackDuration):
    numSuits = len(targets)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = targets[0]['suit']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterLeftShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= 6:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseThrowShot(throws, suitThrowsDict, attackDuration, enterDuration=0, exitDuration=0):
    enterShot = chooseNPCEnterShot(throws, enterDuration)
    openShot = chooseThrowOpenShot(throws, suitThrowsDict, attackDuration)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    exitShot = chooseNPCExitShot(throws, exitDuration)
    closeShot = chooseThrowCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration)
    track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseThrowOpenShot(throws, suitThrowsDict, attackDuration):
    numThrows = len(throws)
    av = None
    duration = 3.0
    if numThrows == 1:
        av = throws[0]['toon']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         avatarBehindShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numThrows >= 2 and numThrows <= 4:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of throws: %s' % numThrows)
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseThrowCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration):
    numSuits = len(suitThrowsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[suitThrowsDict.keys()[0]]
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterLeftShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= 6 or numSuits == 0:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseSquirtShot(squirts, suitSquirtsDict, attackDuration):
    openShot = chooseSquirtOpenShot(squirts, suitSquirtsDict, attackDuration)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseSquirtCloseShot(squirts, suitSquirtsDict, openDuration, openName, attackDuration)
    track = Sequence(openShot, closeShot)
    return track


def chooseSquirtOpenShot(squirts, suitSquirtsDict, attackDuration):
    numSquirts = len(squirts)
    av = None
    duration = 3.0
    if numSquirts == 1:
        av = squirts[0]['toon']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         avatarBehindShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSquirts >= 2 and numSquirts <= 4:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of squirts: %s' % numSquirts)
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseSquirtCloseShot(squirts, suitSquirtsDict, openDuration, openName, attackDuration):
    numSuits = len(suitSquirtsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[suitSquirtsDict.keys()[0]]
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterLeftShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= 6:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    track = apply(random.choice(shotChoices), [av, duration])
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
    shotChoices = [avatarBehindShot, allGroupLowShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseZapCloseShot(zaps, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    hasTrainTrackTrap = False
    battle = zaps[0]['battle']
    shotChoices = [avatarBehindShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseDropShot(drops, suitDropsDict, attackDuration, enterDuration=0.0, exitDuration=0.0):
    enterShot = chooseNPCEnterShot(drops, enterDuration)
    exitShot = chooseNPCExitShot(drops, exitDuration)
    if any(drop['level'] > 0 for drop in drops):
        fullShot = allGroupHighShot(None, attackDuration)
        track = Sequence(enterShot, fullShot, exitShot)
    else:
        openShot = chooseDropOpenShot(drops, suitDropsDict, attackDuration)
        openDuration = openShot.getDuration()
        openName = openShot.getName()
        closeShot = chooseDropCloseShot(drops, suitDropsDict, openDuration, openName, attackDuration)
        track = Sequence(enterShot, openShot, closeShot, exitShot)
    return track


def chooseDropOpenShot(drops, suitDropsDict, attackDuration):
    numDrops = len(drops)
    av = None
    duration = 3.0
    if numDrops == 1:
        av = drops[0]['toon']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         avatarBehindShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numDrops >= 2 and numDrops <= 4 or numDrops == 0:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of drops: %s' % numDrops)
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseDropCloseShot(drops, suitDropsDict, openDuration, openName, attackDuration):
    numSuits = len(suitDropsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[suitDropsDict.keys()[0]]
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterLeftShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= 6 or numSuits == 0:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    choice = random.choice(shotChoices)
    track = choice(av, duration)
    return track


def chooseNPCEnterShot(enters, entersDuration):
    av = None
    duration = entersDuration
    shotChoices = [toonGroupShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track


def chooseNPCExitShot(exits, exitsDuration):
    av = None
    duration = exitsDuration
    shotChoices = [toonGroupShot]
    track = apply(random.choice(shotChoices), [av, duration])
    return track

def chooseSuitShot(attack, attackDuration, cheat=0):
    duration = attackDuration
    if duration < 0:
        duration = 1e-06
    diedTrack = None
    groupStatus = attack['group']
    target = attack['target']
    deadToons = []
    targetDicts = attack['target']
    for targetDict in targetDicts:
        died = targetDict['died']
        if died != 0:
            deadToons.append(targetDict['toon'])

    if len(deadToons) > 0:
        pbpText = attack['playByPlayText']
        diedTextList = []
        for toon in deadToons:
            pbpText = attack['playByPlayText']
            diedTextList.append(toon.getName() + ' was defeated!')

        diedTrack = pbpText.getToonsDiedInterval(diedTextList, duration)
    suit = attack['suit']
    name = attack['id']
    battle = attack['battle']
    camTrack = Sequence()

    def defaultCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
        if attack['group'] == ATK_TGT_SINGLE:
            return randomAttackCam(attack['suit'], target[0]['toon'], attack['battle'], attackDuration,
                                   openShotDuration, 'suit')
        else:
            return randomGroupAttackCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)

    def fromBehindCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
        return fromBehindGroupCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)

    def managerCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
        return randomManagerCheatCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)

    if name == ACID_RAIN:
        camTrack.append(defaultCamera(openShotDuration=1))
    elif name == AUDIT:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == BITE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == GAVEL:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == BOUNCE_CHECK:
        camTrack.append(defaultCamera(openShotDuration=1.5)) #UNUSED
    elif name == CONDUCTION:
        camTrack.append(defaultCamera())
    elif name == BRAIN_STORM:
        camTrack.append(defaultCamera(openShotDuration=2.4))
    elif name == BOOKKEEPING:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == BUZZ_WORD:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == BLAST:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == USURY:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == USURY_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == KICK_UP:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SITDOWN:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == TRIBUTE_2:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == SLUSHFUND_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == STAND_UP_GUY:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == NOT_THROW_PIANO:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SHAKEDOWN:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SHAKEDOWN_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == FREE_CRUISE:
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.7))
        camTrack.append(moveShot(-21.0, 8.0, 8.0, -120, 0, 0, 0.5))
        camTrack.append(heldShot(-21.0, 8.0, 8.0, -120, 0, 0, attackDuration - 4.2))
    # elif name == BLACK_ORB:
    #     camTrack.append(defaultCamera(openShotDuration=2.7))
    elif name == HEAVY_RAINFALL:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == AFTERSHOCK:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == DROWNING:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == FREEZING_RAIN:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CHAINSAW_CANNED:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CALCULATE:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CANNED:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CHOMP:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == NICKEL_AND_DIME:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == QUASH:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == SNAP:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SNAP_WET:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CIGAR_SMOKE:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CLIPON_TIE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == CRUNCH:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == DEMOTION:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == DETONATE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == DETONATE_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == DETONATE_3:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CHAINSAW_DETONATE_3:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CHAINSAW_DETONATE_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CHAINSAW_DETONATE:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == HEAD_ROLLER:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == HEAD_ROLLER_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == HEAD_ROLLER_3:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == UNION_BUST:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == UNION_BUST_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == UNION_BUST_3:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == DOUBLE_TALK:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == DOUBLE_WINDSOR:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == EVICTION_NOTICE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == BASH:
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == DISASSEMBLE:
        camTrack.append(defaultCamera(openShotDuration=1.2))
    elif name == DATA_CORRUPTION:
        camTrack.append(defaultCamera(openShotDuration=1.2))
    elif name == CLOUD_STORAGE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == DISK_SCRATCH:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == VERSION_CONTROL:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == DATA_BREACH:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == OVERLOAD:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == BREAKTHROUGH:
        camTrack.append(defaultCamera(openShotDuration=3.5))
    elif name == ENCRYPT:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == BOUNCE_RATE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == REPROGRAM:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == ELECTROSTATIC_ENERGY:
        camTrack.append(defaultCamera(openShotDuration=1))
    elif name == INSURANCE_PLAN:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == OIL_RAIN:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == HEAT_WAVE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == EMBEZZLE:
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == FLOOD_THE_MARKET:
        camTrack.append(defaultCamera(openShotDuration=2.0)) #UNUSED
    elif name == MONEY_TRIP:
        camTrack.append(defaultCamera(openShotDuration=2.0)) #UNUSED
    elif name == WHEEL_SPIN:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == RAISING_THE_ANTE:
        camTrack.append(defaultCamera(openShotDuration=1.2))
    elif name == SWIRL_BATH:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == ACCUSATIONS:
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == ACCUSATIONS_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == GAME_SHOW:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == EXTRA_TIP:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == BEGUILE:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == REFINEMENT:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == LIFE_INSURANCE:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == WORKERS_COMPENSATION:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == COURT_RECORD_1:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COURT_RECORD_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COURT_RECORD_3:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COURT_RECORD_4:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COURT_RECORD_5:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SPOTLIGHT:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == COURT_MANDATE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COURT_MANDATE_1:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COURT_MANDATE_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COURT_MANDATE_3:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == EVIL_EYE:
        camTrack.append(defaultCamera(openShotDuration=2.7))
    elif name == EVIL_EYE_WSI:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == FILIBUSTER:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == FILL_WITH_LEAD:
        camTrack.append(defaultCamera(openShotDuration=3.2))
    elif name == FINGER_WAG:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == FIRED:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == FOUNTAIN_PEN:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == FREEZE_ASSETS:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == HALF_WINDSOR:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == HEAD_SHRINK:
        camTrack.append(defaultCamera(openShotDuration=1.3))
    elif name == GLOWER_POWER:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == CHAINSAW_GLOWER_POWER:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == GUILT_TRIP:
        camTrack.append(defaultCamera(openShotDuration=0.9))
    elif name == GUILT_TRIP_WSI:
        camTrack.append(defaultCamera(openShotDuration=0.9))
    elif name == HANG_UP:
        camTrack.append(defaultCamera(openShotDuration=3.5))
    elif name == HOT_AIR:
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == MP_HOT_AIR:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == POISON_SPRAY:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == MOB_MENTALITY:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == QUALITY_CONTROL_GAG:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == QUALITY_CONTROL_GAG_1:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == QUALITY_CONTROL_GAG_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == QUALITY_CONTROL_GAG_3:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == BAR:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == QUALITY_CONTROL_LEVEL:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == QUALITY_CONTROL_LEVEL_1:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == QUALITY_CONTROL_LEVEL_2:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == QUALITY_CONTROL_LEVEL_3:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == MANAGERIAL_PROTECTION:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == RADIO_INFREQUENCY:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == VOICEMAIL:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == WIRE_CUT:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == PAPER_CUT:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == EXPLODING_BILL:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == FIRE_COG:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CAGE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == GOOD_MORNING_TOONTOWN:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == CARESS:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == COLLECT_CALL_FEES:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COLLECT_CALL:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SLUSH_FUND:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == JURY_NOTICE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CEASE_AND_DESIST:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == INVESTMENT:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == FIELD_PROMOTION:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == WIRETAPPED:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SHORT_SQUEEZE:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == BLUE_CHIP:
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == FALLING_KNIFE:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == JARGON:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LEGALESE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LIQUIDATE:
        camTrack.append(defaultCamera(openShotDuration=1))
    elif name == HOSTILE_TAKEOVER:
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == MARKET_CRASH:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == MUMBO_JUMBO:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == PARADIGM_SHIFT:
        camTrack.append(defaultCamera(openShotDuration=1.6))
    elif name == PECKING_ORDER:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == PECKING_ORDER_WSI:
        camTrack.append(defaultCamera(openShotDuration=2.3))
    elif name == PLAY_HARDBALL:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == PICK_POCKET:
        camTrack.append(allGroupLowShot(suit, 2.7))
    elif name == DENIAL_OF_SERVICE:
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == VOODOO_MAGIC:
        camTrack.append(defaultCamera(openShotDuration=0.25))
    elif name == COURT_SANCTION:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CHAINSAW_REVVING_UP:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == PINK_SLIP:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == POUND_KEY:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CLOSE_THE_LOOP:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == POWER_TIE:
        camTrack.append(defaultCamera(openShotDuration=1.4))
    elif name == POWER_TRIP_WSI:
        camTrack.append(defaultCamera(openShotDuration=1.1))
    elif name == CHAINSAW_QUAKE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == POWER_TRIP:
        camTrack.append(defaultCamera(openShotDuration=1.1))
    elif name == HR_POWER_TRIP:
        camTrack.append(defaultCamera(openShotDuration=1.1))
    elif name == CHAINSAW_ROLODEX:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == RESTRAINING_ORDER_WSI:
        camTrack.append(defaultCamera(openShotDuration=2.8))
    elif name == QUAKE:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == LD_AFTERSHOCK:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == MP_QUAKE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == LD_QUAKE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == LD_EVICTION_NOTICE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == RAZZLE_DAZZLE:
       camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == RED_TAPE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LD_RED_TAPE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == RE_ORG:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == LD_RE_ORG:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == REARRANGE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == RESTRAINING_ORDER:
        camTrack.append(defaultCamera(openShotDuration=2))
    elif name == ROLODEX:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == RUBBER_STAMP:
        camTrack.append(defaultCamera(openShotDuration=3.2))
    elif name == RUB_OUT:
        camTrack.append(defaultCamera(openShotDuration=2.2))
    elif name == SACKED:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == SCHMOOZE:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CONE_OF_SHAME:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SHAKE:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == SHRED:
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == SONG_AND_DANCE:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == MP_SONG_AND_DANCE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SPIN:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == DUCK_SPIN:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SYNERGY: #NOT ACTUALLY SYNERGY
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == UNION_DUES:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == COURT_COSTS:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == UNION_BUSTER:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == SNOW:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == BOMB_CAKE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == BOMB:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == LEGAL_BINDINGS:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == TABULATE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == TEE_OFF:
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == MULLIGAN:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == CLOCK_CHANGE:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == TREMOR:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == WHITE_POWDER:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == BLACK_ORB or name == WATERCOOLER:
        camTrack.append(defaultCamera())
    elif name == WITHDRAWAL:
        camTrack.append(defaultCamera(openShotDuration=1.2))
    elif name == INK_DRAIN:
        camTrack.append(defaultCamera(openShotDuration=2.5))  # UNUSED
    elif name == WRITE_OFF:
        camTrack.append(defaultCamera())
    elif name == OVERDRAFT:
        camTrack.append(defaultCamera(openShotDuration=2.5)) #UNUSED
    elif name == ENRAGED:
        camTrack2 = Sequence(suitCameraShakeShot(suit, 6, 0.25))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Tremor!', 3.5)
        return Parallel(pbpTrack2, camTrack2)
    elif name == THROW_BOOK:
        camTrack.append(defaultCamera(openShotDuration=1.5))
        # litigator cheats
    elif name == LITIGATOR_SNAP_SOAK:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LITIGATOR_SNAP:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LITIGATOR_BAYOU_BASH:
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      heldRelativeShot(suit, 0.0, 6.8096, 7.77317, -180, 0.0, 0.0, attackDuration)))
    elif name == LITIGATOR_BAYOU_BELLOW:
        camTrack.append(Sequence(cameraActorShot(suit, 'litigator-bellow', 0), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.5)))
        # stenographer cheats
    elif name == STENOGRAPHER_SANCTION_BINDINGS:
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == STENOGRAPHER_SANCTION:
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == STENOGRAPHER_COURT_RECORD_BAN:
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
            'Due to an illegal action, this toon takes 50 damage!',
            attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Court Record!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        # case manager cheats
    elif name == CASE_MANAGER_INSURANCE_PLAN:
        if not suit.isSkeleton:
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0.7, suit), Wait(2.0), moveShot(0.0, -15.0, 6.0, 0, -20, 0, 1.5), heldShot(0.0, -15.0, 6.0, 0, -20, 0, attackDuration - 4.2)))

        else:
            camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'),
                                      moveShot(0.0, -15.0, 6.0, 0, -20, 0, 1.5),
                                      heldShot(0.0, -15.0, 6.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == CASE_MANAGER_INSURANCE:
        camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == CASE_MANAGER_LEGAL_BINDINGS:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == CASE_MANAGER_LEGALLY_BOUND:
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('This toon takes 20 damage per round!', attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Legally Bound!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == CASE_MANAGER_COURT_RECORD_BAN:
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'Due to an illegal action, this toon takes 50 damage!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Court Record!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        # scapegoat cheats
    elif name == SCAPEGOAT_SHIELDS_UP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == SCAPEGOAT_ENRAGED:
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 8.8096, 5, -180, 0.0, 0.0, attackDuration)))
    elif name == SCAPEGOAT_GAVEL:
        camTrack.append(defaultCamera(openShotDuration=2))
    elif name == SCAPEGOAT_BARNYARD_BASH:
        camTrack.append(defaultCamera(openShotDuration=2))
    elif name == SCAPEGOAT_COURT_RECORD_BAN:
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'Due to an illegal action, this toon takes 50 damage!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Court Record!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    # powerhouse cheats
    elif name == POWERHOUSE_ABSORB:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == POWERHOUSE_SOAK_IMMUNE:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == POWERHOUSE_LURE_IMMUNE:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == POWERHOUSE_SYPHON:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == POWERHOUSE_SYPHON_DESPERATION:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == POWERHOUSE_SNIPE_VULNERABLE:
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse retaliates against toons with existing\nvulnerabilities!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            return camTrack2
    elif name == POWERHOUSE_SNIPE_GAG_BAN:
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse doubles down damage on toons who chose\nbanned gags!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            return camTrack2
    elif name == POWERHOUSE_SNIPE_SOAKED:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == POWERHOUSE_SNIPE_BOOKKEPT:
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse doubles down damage on toons who\nattacked the Bookkeeper while Bookkeeping!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            return camTrack2
    elif name == POWERHOUSE_SNIPE_MULLIGAN:
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse retaliates against toons on cooldown!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == POWERHOUSE_SNIPE_COLLECT_CALL:
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse retaliates against toons with who owe\ncollect call dues!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            return camTrack2
    # bookkeeper cheats
    elif name == BOOKKEEPER_PAPER_CUT_SOAKED:
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == BOOKKEEPER_PAPER_CUT_MARKED:
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == BOOKKEEPER_PAPER_CUT:
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == BOOKKEEPER_EXPLODING_DOCUMENT:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == BOOKKEEPER_BOOKKEEPING_RETALIATION:
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=3.0)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                "The Bookkeeper applies a gag damage debuff to all toons\nwho attacked him while Bookkeeping!",
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Bookkeeping!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == BOOKKEEPER_BOOKKEEPING:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    # wiretapper cheats
    elif name == WIRETAPPER_COLLECT_CALL:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == WIRETAPPER_COLLECT_CALL_DOT:
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                "This toon is forced to pay collect call fees every turn\nuntil their dues are paid!",
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Collect Call Dues!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == WIRETAPPER_GAG_BAN:
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                "Due to an overinflated budget this toon takes 50 damage!",
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == WIRETAPPER_WIRETAPPED:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == WIRETAPPER_VOICEMAIL:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == WIRETAPPER_BROKEN_CONNECTION:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    # ambassador cheats
    elif name == AMBASSADOR_HEAD_ROLLER:
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == AMBASSADOR_HEAD_ROLLER_GROUP:
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == AMBASSADOR_REFINEMENT:
        camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == AMBASSADOR_PHASE_2:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == AMBASSADOR_DAMAGE_UP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == AMBASSADOR_MANAGERIAL_PROTECTION:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == AMBASSADOR_MANAGERIAL_PROTECTION_IMMUNITY:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == AMBASSADOR_MULLIGAN:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    #universal cheats
    elif name == SYNERGY_FEES:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CALCULATING_FEES:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_4:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 4 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_5:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 5 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_6:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 6 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_7:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 7 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_8:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_4_5:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_4_6:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_4_7:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_4_8:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_5_6:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_5_7:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_5_8:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_6_7:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_6_8:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LEVEL_7_8:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TOONUP:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Toon-Up gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TRAP:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Trap gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LURE:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Lure gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_THROW:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Throw gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_SQUIRT:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Squirt gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_ZAP:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Zap gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_SOUND:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Sound gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_DROP:
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Drop gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TOONUP_TRAP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TOONUP_LURE:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TOONUP_THROW:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TOONUP_SQUIRT:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TOONUP_ZAP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TOONUP_SOUND:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TOONUP_DROP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TRAP_LURE:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TRAP_THROW:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TRAP_SQUIRT:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TRAP_ZAP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TRAP_SOUND:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_TRAP_DROP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LURE_THROW:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LURE_SQUIRT:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LURE_ZAP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LURE_SOUND:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_LURE_DROP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_THROW_SQUIRT:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_THROW_ZAP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_THROW_SOUND:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_THROW_DROP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_SQUIRT_ZAP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_SQUIRT_SOUND:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_SQUIRT_DROP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_ZAP_SOUND:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_ZAP_DROP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == BAN_SOUND_DROP:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    else:
        notify.warning('unknown attack id in chooseSuitShot: %d using default cam' % name)
        camTrack.append(defaultCamera())
    pbpText = attack['playByPlayText']
    displayName = TTLocalizer.SuitAttackNames[attack['name']]
    if attack['name'] in TTLocalizer.SuitCheatNames:
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(TTLocalizer.SuitCheatDescription[attack['name']], attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat(displayName, attackDuration - 2)
        return Parallel(camTrack, pbpTrack, pbpDesc)
    if float(suit.currHP) > float(suit.maxHP * 1.5):
        pbpTrack = pbpText.getShowIntervalOvercharged(displayName, attackDuration - 2)
    else:
        pbpTrack = pbpText.getShowInterval(displayName, attackDuration - 2)
    track = Sequence(Parallel(camTrack, pbpTrack))
    return track

def chooseSuitCloseShot(attack, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    if duration < 0:
        duration = 1e-06
    groupStatus = attack['group']
    diedTrack = None
    if groupStatus == ATK_TGT_SINGLE:
        av = attack['target'][0]['toon']
        shotChoices = [avatarCloseUpThreeQuarterRightShot, suitGroupThreeQuarterLeftBehindShot]
        died = attack['target'][0]['died']
        if died != 0:
            pbpText = attack['playByPlayText']
            diedText = av.getName() + ' was defeated!'
            diedTextList = [diedText]
            diedTrack = pbpText.getToonsDiedInterval(diedTextList, 3.5)
    elif groupStatus == ATK_TGT_DOUBLE or groupStatus == ATK_TGT_GROUP:
        av = None
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
        deadToons = []
        targetDicts = attack['target']
        for targetDict in targetDicts:
            died = targetDict['died']
            if died != 0:
                deadToons.append(targetDict['toon'])

        if len(deadToons) > 0:
            pbpText = attack['playByPlayText']
            diedTextList = []
            for toon in deadToons:
                pbpText = attack['playByPlayText']
                diedTextList.append(toon.getName() + ' was defeated!')

            diedTrack = pbpText.getToonsDiedInterval(diedTextList, 3.5)
    else:
        notify.error('Bad groupStatus: %s' % groupStatus)
    track = apply(random.choice(shotChoices), [av, duration])
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
        track.append(Func(camera.lookAt, target))
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
    shotChoices = [avatarCloseUpThreeQuarterRightShot,
     avatarBehindShot,
     avatarBehindHighShot,
     suitGroupThreeQuarterLeftBehindShot]
    track = apply(random.choice(shotChoices), [av, duration])
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
        posTrack = LerpPosInterval(camera, duration, pos=Point3(x, y, z), other=other)
        hprTrack = LerpHprInterval(camera, duration, hpr=Point3(h, p, r), other=other)
    else:
        posTrack = LerpPosInterval(camera, duration, pos=Point3(x, y, z))
        hprTrack = LerpHprInterval(camera, duration, hpr=Point3(h, p, r))
    return Parallel(posTrack, hprTrack)


def allGroupShot(avatar, duration):
    return heldShot(10, 0, 10, 79, -30, 0, duration, 'allGroupShot')


def allGroupLowShot(avatar, duration):
    return heldShot(17, -5, 3, 69, 0, 0, duration, 'allGroupLowShot')


def allGroupLowDiagonalShot(avatar, duration):
    return heldShot(7, 5, 6, 119, -30, 0, duration, 'allGroupLowShot')


def allGroupHighShot(avatar, duration):
    return heldShot(0, -15, 7, 0, 0, 0, duration, 'allGroupHighShot')


def toonGroupShot(avatar, duration):
    return heldShot(10, 0, 10, 115, -30, 0, duration, 'toonGroupShot')


def toonGroupHighShot(avatar, duration):
    return heldShot(5, 0, 1, 115, 45, 0, duration, 'toonGroupHighShot')


def suitGroupShot(avatar, duration):
    return heldShot(10, 0, 10, 65, -30, 0, duration, 'suitGroupShot')


def suitGroupLowLeftShot(avatar, duration):
    return heldShot(8.4, -3.85, 2.75, 36.3, 3.25, 0, duration, 'suitGroupLowLeftShot')


def suitGroupThreeQuarterLeftBehindShot(avatar, duration):
    if random.random() > 0.5:
        x = 12.37
        h = 134.61
    else:
        x = -12.37
        h = -134.61
    return heldShot(x, 11.5, 8.16, h, -22.7, 0, duration, 'suitGroupThreeQuarterLeftBehindShot')


def suitWakeUpShot(avatar, duration):
    return heldShot(10, -5, 10, 65, -30, 0, duration, 'suitWakeUpShot')


def suitCameraShakeShot(avatar, duration, shakeIntensity, quake = 0):
    track = Sequence(name='suitShakeCameraShot')
    if quake == 1:
        shakeDelay = 1.1
        numShakes = 4
    else:
        shakeDelay = 0.3
        numShakes = 5
    postShakeDelay = 0.5
    shakeTime = (duration - shakeDelay - postShakeDelay) / numShakes
    shakeDuration = shakeTime * (1.0 / numShakes)
    shakeWaitInterval = shakeTime * ((numShakes - 1.0) / numShakes)

    def shakeCameraTrack(intensity, shakeWaitInterval = shakeWaitInterval, quake = quake, shakeDuration = shakeDuration, numShakes = numShakes):
        vertShakeTrack = Sequence(Wait(shakeWaitInterval), Func(camera.setZ, camera.getZ() + intensity / 8), Wait(shakeDuration / 8), Func(camera.setZ, camera.getZ() - intensity), Wait(shakeDuration / 8), Func(camera.setZ, camera.getZ() + intensity / 8))
        horizShakeTrack = Sequence(Wait(shakeWaitInterval - shakeDuration / 4), Func(camera.setY, camera.getY() + intensity / 8), Wait(shakeDuration / 8), Func(camera.setY, camera.getY() - intensity / 8), Wait(shakeDuration / 8), Func(camera.setY, camera.getY() + intensity / 8), Wait(shakeDuration / 8), Func(camera.lookAt, Point3(0, 0, 0)))
        shakeTrack = Sequence()
        for i in xrange(0, numShakes):
            if quake == 0:
                shakeTrack.append(vertShakeTrack)
            else:
                shakeTrack.append(Parallel(vertShakeTrack, horizShakeTrack))

        return shakeTrack

    x = 10 + random.random() * 3
    if random.random() > 0.5:
        x = -x
    z = 7 + random.random() * 3
    track.append(Func(camera.setPos, x, 0, z))
    track.append(Func(camera.lookAt, Point3(0, 0, 0)))
    track.append(Wait(shakeDelay))
    track.append(shakeCameraTrack(shakeIntensity))
    track.append(Wait(postShakeDelay))
    return track


def avatarCloseUpShot(avatar, duration):
    return heldRelativeShot(avatar, 0, 8, avatar.getHeight() * 0.66, 179, 15, 0, duration, 'avatarCloseUpShot')


def avatarCloseUpThrowShot(avatar, duration):
    return heldRelativeShot(avatar, 3, 8, avatar.getHeight() * 0.66, 159, 3.6, 0, duration, 'avatarCloseUpThrowShot')


def avatarCloseUpThreeQuarterRightShot(avatar, duration):
    return heldRelativeShot(avatar, 5.2, 5.45, avatar.getHeight() * 0.66, 131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterRightShot')


def avatarCloseUpThreeQuarterRightShotWide(avatar, duration):
    return heldRelativeShot(avatar, 7.2, 8.45, avatar.getHeight() * 0.66, 131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterRightShot')


def avatarCloseUpThreeQuarterLeftShot(avatar, duration):
    return heldRelativeShot(avatar, -5.2, 5.45, avatar.getHeight() * 0.66, -131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterLeftShot')


def avatarCloseUpThreeQuarterRightFollowShot(avatar, duration):
    track = Sequence(name='avatarCloseUpThreeQuarterRightFollowShot')
    track.append(heldRelativeShot(avatar, 5.2, 5.45, avatar.getHeight() * 0.66, 131.5, 3.6, 0, duration * 0.65))
    track.append(LerpHprInterval(nodePath=camera, other=avatar, duration=duration * 0.2, hpr=Point3(110, 3.6, 0), blendType='easeInOut'))
    track.append(Wait(duration * 0.25))
    return track


def avatarCloseUpZoomShot(avatar, duration):
    track = Sequence('avatarCloseUpZoomShot')
    track.append(LerpPosHprInterval(nodePath=camera, other=avatar, duration=duration / 2, startPos=Point3(0, 10, avatar.getHeight()), startHpr=Point3(179, -10, 0), pos=Point3(0, 6, avatar.getHeight()), hpr=Point3(179, -10, 0), blendType='easeInOut'))
    track.append(Wait(duration / 2))
    return track


def avatarBehindShot(avatar, duration):
    return heldRelativeShot(avatar, 5, -7, avatar.getHeight(), 40, -12, 0, duration, 'avatarBehindShot')


def avatarBehindHighShot(avatar, duration):
    return heldRelativeShot(avatar, -4, -7, 5 + avatar.getHeight(), -30, -35, 0, duration, 'avatarBehindHighShot')


def avatarBehindHighRightShot(avatar, duration):
    return heldRelativeShot(avatar, 4, -7, 5 + avatar.getHeight(), 30, -35, 0, duration, 'avatarBehindHighShot')


def avatarBehindThreeQuarterRightShot(avatar, duration):
    return heldRelativeShot(avatar, 7.67, -8.52, avatar.getHeight() * 0.66, 25, 7.5, 0, duration, 'avatarBehindThreeQuarterRightShot')


def avatarSideFollowAttack(suit, toon, duration, battle):
    windupDuration = duration * (0.1 + random.random() * 0.1)
    projectDuration = duration * 0.75
    impactDuration = duration - windupDuration - projectDuration
    suitHeight = suit.getHeight()
    toonHeight = toon.getHeight()
    suitCentralPoint = suit.getPos(battle)
    suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
    toonCentralPoint = toon.getPos(battle)
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


def randomAttackCam(suit, toon, battle, attackDuration, openShotDuration, attackerString = 'suit'):
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
        openShot = randomSplitShot(attacker, defender, battle, openShotDuration)
    randomDouble = random.random()
    if randomDouble > 0.6:
        closeShot = randomActorShot(defender, battle, closeShotDuration, defenderString)
    elif randomDouble > 0.2:
        closeShot = randomOverShoulderShot(suit, toon, battle, closeShotDuration, focus=defenderString)
    else:
        closeShot = randomSplitShot(attacker, defender, battle, closeShotDuration)
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
        openShot = randomSplitShot(attacker, defender, battle, openShotDuration)
    randomDouble = random.random()
    if randomDouble > 0.6:
        closeShot = randomActorShot(defender, battle, closeShotDuration, defenderString)
    elif randomDouble > 0.2:
        closeShot = randomOverShoulderShot(suit, toon, battle, closeShotDuration, focus=defenderString)
    else:
        closeShot = randomSplitShot(attacker, defender, battle, closeShotDuration)
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
    closeShot = randomToonGroupShot(targets, suit, closeShotDuration, battle)
    return Sequence(openShot, closeShot)


def randomActorShot(actor, battle, duration, actorType, groupShot = 0):
    height = actor.getHeight()
    centralPoint = actor.getPos(battle)
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
    centralPoint = actor.getPos(battle)
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
    suitCentralPoint = suit.getPos(battle)
    suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
    toonCentralPoint = toon.getPos(battle)
    toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
    x = 9 + random.random() * 2
    y = -2 - random.random() * 2
    z = suitHeight * 0.5 + random.random() * suitHeight
    if MovieUtil.shotDirection == 'left':
        x = -x
    return focusShot(x, y, z, duration, toonCentralPoint, splitFocusPoint=suitCentralPoint)


def randomOverShoulderShot(suit, toon, battle, duration, focus):
    suitHeight = suit.getHeight()
    toonHeight = toon.getHeight()
    suitCentralPoint = suit.getPos(battle)
    suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
    toonCentralPoint = toon.getPos(battle)
    toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
    x = 2 + random.random() * 10
    if focus == 'toon':
        y = 8 + random.random() * 6
        z = suitHeight * 1.2 + random.random() * suitHeight
    else:
        y = -10 - random.random() * 6
        z = toonHeight * 1.5
    if MovieUtil.shotDirection == 'left':
        x = -x
    return focusShot(x, y, z, duration, toonCentralPoint, splitFocusPoint=suitCentralPoint)

def randomCameraSelection(suit, attack, attackDuration, openShotDuration):
    shotChoices = [avatarCloseUpThrowShot,
     avatarCloseUpThreeQuarterLeftShot,
     allGroupLowShot,
     suitGroupLowLeftShot,
     avatarBehindHighShot]
    if openShotDuration > attackDuration:
        openShotDuration = attackDuration
    closeShotDuration = attackDuration - openShotDuration
    openShot = apply(random.choice(shotChoices), [suit, openShotDuration])
    closeShot = chooseSuitCloseShot(attack, closeShotDuration, openShot.getName(), attackDuration)
    return Sequence(openShot, closeShot)

def randomToonGroupShot(toons, suit, duration, battle):
    sum = 0
    for t in toons:
        toon = t['toon']
        height = toon.getHeight()
        sum = sum + height

    avgHeight = sum / len(toons) * 0.75
    suitPos = suit.getPos(battle)
    x = 1 + random.random() * 6
    if suitPos.getX() > 0:
        x = -x
    if random.random() > 0.5:
        y = 4 + random.random() * 1
        z = avgHeight + random.random() * 6
    else:
        y = 11 + random.random() * 2
        z = 13 + random.random() * 2
    focalPoint = Point3(0, -4, avgHeight)
    return focusShot(x, y, z, duration, focalPoint)


def chooseFireShot(throws, suitThrowsDict, attackDuration, enterDuration = 0, exitDuration = 0):
    enterShot = chooseNPCEnterShot(throws, enterDuration)
    openShot = chooseFireOpenShot(throws, suitThrowsDict, attackDuration)
    openDuration = openShot.getDuration()
    openName = openShot.getName()
    closeShot = chooseFireCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration)
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


def chooseFireOpenShot(throws, suitThrowsDict, attackDuration):
    numThrows = len(throws)
    av = None
    duration = 3.0
    if numThrows == 1:
        av = throws[0]['toon']
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterRightShot,
         avatarBehindShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numThrows >= 2 and numThrows <= 4:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of throws: %s' % numThrows)
    shotChoice = random.choice(shotChoices)
    track = apply(shotChoice, [av, duration])
    print 'chooseFireOpenShot %s' % shotChoice
    return track


def chooseFireCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration):
    numSuits = len(suitThrowsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[suitThrowsDict.keys()[0]]
        shotChoices = [avatarCloseUpFireShot,
         avatarCloseUpThreeQuarterLeftFireShot,
         allGroupLowShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= 6 or numSuits == 0:
        shotChoices = [allGroupLowShot, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    shotChoice = random.choice(shotChoices)
    track = apply(shotChoice, [av, duration])
    print 'chooseFireOpenShot %s' % shotChoice
    return track


def avatarCloseUpFireShot(avatar, duration):
    return heldRelativeShot(avatar, 7, 17, avatar.getHeight() * 0.66, 159, 3.6, 0, duration, 'avatarCloseUpFireShot')


def avatarCloseUpThreeQuarterLeftFireShot(avatar, duration):
    return heldRelativeShot(avatar, -8.2, 8.45, avatar.getHeight() * 0.66, -131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterLeftShot')
