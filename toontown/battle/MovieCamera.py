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


def chooseSuitShot(attack, attackDuration):
    duration = attackDuration
    if duration < 0:
        duration = 1e-06
    diedTrack = None
    groupStatus = attack['group']
    target = attack['target']
    if groupStatus == ATK_TGT_SINGLE:
        toon = target['toon']
        died = attack['target']['died']
        if died != 0:
            pbpText = attack['playByPlayText']
            diedText = toon.getName() + ' was defeated!'
            diedTextList = [diedText]
            diedTrack = pbpText.getToonsDiedInterval(diedTextList, duration)
    elif groupStatus == ATK_TGT_GROUP:
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

    def defaultCamera(attack = attack, attackDuration = attackDuration, openShotDuration = 3.5, target = target):
        if attack['group'] == ATK_TGT_GROUP:
            return randomGroupAttackCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)
        else:
            return randomAttackCam(attack['suit'], target['toon'], attack['battle'], attackDuration, openShotDuration, 'suit')

    def fromBehindCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
        return fromBehindGroupCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)

    def managerCamera(attack=attack, attackDuration=attackDuration, openShotDuration=3.5, target=target):
        return randomManagerCheatCam(attack['suit'], target, attack['battle'], attackDuration, openShotDuration)

    if name == ACID_RAIN:
        camTrack.append(defaultCamera(openShotDuration=1))
    elif name == AUDIT:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Audit!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == BITE:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == GAVEL:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=2.2),
                             defaultCamera(attackDuration=attackDuration - 6, openShotDuration=1.5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Bite!', 3.5)
        pbpDesc3 = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The Scapegoat bans all your gags for 1 turn!', 3.5)))
        pbpTrack3 = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Gavel!', 3.5)))
        return Parallel(pbpTrack2, camTrack2, pbpDesc3, pbpTrack3)
    elif name == BOUNCE_CHECK:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Bounce Check!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Level 6 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == CONDUCTION:
        camTrack.append(defaultCamera())
    elif name == BRAIN_STORM:
        camTrack.append(defaultCamera(openShotDuration=2.4))
    elif name == BOOKKEEPING:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=2), defaultCamera(attackDuration=7, openShotDuration=3),
                             randomActorShot(suit, battle, attackDuration - 11, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Rolodex!', 3.5)
        pbpDesc2 = Sequence(Wait(4.0), pbpDc.getShowIntervalDesc('The Bookkeeper silences a toon when soaked!', 3.5))
        pbpTrack2 = Sequence(Wait(4.0), pbpText.getShowIntervalCheat('Bookkeeping!', 3.5))
        pbpDesc = Sequence(Wait(11.0), (pbpDc.getShowIntervalDesc('Lure and Throw gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(11.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpTrack4, pbpDesc, pbpDesc2, camTrack2)
    elif name == BUZZ_WORD:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=1.8), randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Buzz Word!', 3.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Level 6 gags are off-limits!!', 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpDesc3 = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!!', 3.5)))
        pbpTrack3 = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        pbpDesc4 = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Level 5 gags are off-limits!!', 3.5)))
        pbpTrack4 = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'ste':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        elif attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack3, pbpTrack2, pbpDesc3, camTrack2)
        elif attack['suit'].dna.name == 'blr':
            return Parallel(pbpTrack4, pbpTrack2, pbpDesc4, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.8))
    elif name == BLAST:
        camTrack2 = Sequence(heldShot(8, 11, 5, 150, 0, 0, 4), randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('All toons take a huge loss, rewards are off-limits!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Blast!', 3.5)
        pbpDesc = Sequence(Wait(4), (pbpDc.getShowIntervalDesc("The Groundbreaker is now absorbing damage dealt to\nother cogs!", 3.5)))
        pbpTrack = Sequence(Wait(4), (pbpText.getShowIntervalCheat("Tank Mentality!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == USURY:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1),
                             defaultCamera(attackDuration=attackDuration - 5, openShotDuration=4.0))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Glower Power!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The Chainsaw Consultant retaliates against the most\ndangerous toon!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Sparkplug!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == USURY_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 6))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Canned!', 3.5)
        pbpDesc = Sequence(Wait(6.0), (
            pbpDc.getShowIntervalDesc('The Chainsaw Consultant overcharges all cogs in battle!', 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Scabbard!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == KICK_UP:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=1.8), defaultCamera(attackDuration=4, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Market Crash!', 3.5)
        pbpDesc = Sequence(Wait(6), (
            pbpDc.getShowIntervalDesc("The Dividend King retaliates when soaked!", 3.5)))
        pbpTrack = Sequence(Wait(6), (pbpText.getShowIntervalCheat("Pecking Order!", 3.5)))
        pbpDesc4 = Sequence(Wait(10.0), (pbpDc.getShowIntervalDesc(
            'Level 5 and 7 gags are off-limits!', 3.5)))
        pbpTrack4 = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack4, pbpDesc4, camTrack2)
    elif name == SITDOWN:
        camTrack2 = Sequence(randomActorShot(suit, battle, 4, 'suit'), randomActorShot(suit, battle, 4, 'suit'), defaultCamera(attackDuration=5.0, openShotDuration=2.0),
                             randomActorShot(suit, battle, attackDuration - 13, 'suit'))

        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("An audit is approaching!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Stock Market Audit!', 3.5)
        pbpDesc3 = Sequence(Wait(8.0), (pbpDc.getShowIntervalDesc(
            'The Stock Market has crashed!', 3.5)))
        pbpTrack3 = Sequence(Wait(8.0), (pbpText.getShowIntervalCheat("Stock Market Crash!", 3.5)))
        pbpDesc4 = Sequence(Wait(13.0), (pbpDc.getShowIntervalDesc(
            'Level 5 and 8 gags are off-limits!', 3.5)))
        pbpTrack4 = Sequence(Wait(13.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack4, pbpDesc4, pbpTrack, pbpDesc, camTrack2)
    elif name == TRIBUTE_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5),
                             defaultCamera(attackDuration=4, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Tee Off!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Chairman takes another shot when Dazed!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Mulligan!', 3.5))
        pbpDesc = Sequence(Wait(9.0), (
            pbpDc.getShowIntervalDesc('The Chairman bans Trap for 2 turns!', 3.5)))
        pbpTrack = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == SLUSHFUND_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Pink Slip!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Chairman retaliates when soaked!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Snipe!', 3.5))
        pbpDesc = Sequence(Wait(10.0), (
            pbpDc.getShowIntervalDesc('The Chairman bans Squirt for 2 turns!', 3.5)))
        pbpTrack = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == STAND_UP_GUY:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Piercing Intellect!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Chairman has has enough of the toon's antics!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Enraged!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, camTrack2)
    elif name == NOT_THROW_PIANO:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Piercing Intellect!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Chairman retaliates when dropped!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Throw Piano!', 3.5))
        pbpDesc = Sequence(Wait(10.0), (
            pbpDc.getShowIntervalDesc('The Chairman bans Drop for 2 turns!', 3.5)))
        pbpTrack = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == SHAKEDOWN:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=1.8), defaultCamera(attackDuration=4, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Bounce Check!', 3.5)
        pbpDesc = Sequence(Wait(6), (
            pbpDc.getShowIntervalDesc("The Dividend King retaliates against the most\ndangerous toon!", 3.5)))
        pbpTrack = Sequence(Wait(6), (pbpText.getShowIntervalCheat("Pecking Order!", 3.5)))
        pbpDesc4 = Sequence(Wait(10.0), (pbpDc.getShowIntervalDesc(
            'Level 6 and 7 gags are off-limits!', 3.5)))
        pbpTrack4 = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack4, pbpDesc4, camTrack2)
    elif name == SHAKEDOWN_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=1.8), heldShot(0.0, -15.0, 10.0, 0, -20, 0, 5.0),
                             randomActorShot(suit, battle, attackDuration - 11, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Pecking Order!', 3.5)
        pbpDesc = Sequence(Wait(6), (
            pbpDc.getShowIntervalDesc("The Dividend King heals all cogs in the battle!", 3.5)))
        pbpTrack = Sequence(Wait(6), (pbpText.getShowIntervalCheat("Slush Fund!", 3.5)))
        pbpDesc4 = Sequence(Wait(11.0), (pbpDc.getShowIntervalDesc(
            'Level 7 and 8 gags are off-limits!', 3.5)))
        pbpTrack4 = Sequence(Wait(11.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack4, pbpDesc4, camTrack2)
    elif name == FREE_CRUISE:
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.7))
        camTrack.append(moveShot(-21.0, 8.0, 8.0, -120, 0, 0, 0.5))
        camTrack.append(heldShot(-21.0, 8.0, 8.0, -120, 0, 0, attackDuration - 3.7))
    elif name == BLACK_ORB:
        camTrack.append(defaultCamera(openShotDuration=2.7))
    elif name == HEAVY_RAINFALL:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.0, openShotDuration=1.0),
                             defaultCamera(attackDuration=5.0, openShotDuration=1.0), randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Power Trip!', 3.5)
        pbpDesc2 = Sequence(Wait(4.0), pbpDc.getShowIntervalDesc('The storm is starting to pick up all squirt\nand zap gags are more effective!', 3.5))
        pbpTrack2 = Sequence(Wait(4.0), pbpText.getShowIntervalCheat('Heavy Rain!', 3.5))
        pbpDesc = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('The Liquidator is transitioning!', 3.5)))
        pbpTrack = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Heavy Rain!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, pbpTrack, pbpDesc, camTrack2)
    elif name == AFTERSHOCK:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.0, openShotDuration=1.5),
                             defaultCamera(attackDuration=5, openShotDuration=1.0), randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Liquidate!', 3.5)
        pbpDesc2 = Sequence(Wait(4.0), pbpDc.getShowIntervalDesc('The Liquidator retaliates against the \nmost dangerous toon!', 3.5))
        pbpTrack2 = Sequence(Wait(4.0), pbpText.getShowIntervalCheat('Aftershock!', 3.5))
        pbpDesc = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('The Liquidator is transitioning!', 3.5)))
        pbpTrack = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Storm Cell!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, camTrack2, pbpTrack, pbpDesc)
    elif name == DROWNING:
        camTrack2 = Sequence(defaultCamera(attackDuration=5.0, openShotDuration=1.0),
                             defaultCamera(attackDuration=4.0, openShotDuration=1.0), randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Reorganize!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0), pbpDc.getShowIntervalDesc(
            'The Union Buster retaliates when marked!', 3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Breach of Contract!', 3.5))
        pbpDesc3 = Sequence(Wait(9.0), pbpDc.getShowIntervalDesc(
            'Throw and Zap gags are off-limits!', 3.5))
        pbpTrack3 = Sequence(Wait(9.0), pbpText.getShowIntervalCheat('Quality Control!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, pbpTrack3, pbpDesc3, camTrack2)
    elif name == FREEZING_RAIN:
        camTrack2 = Sequence(defaultCamera(attackDuration=5.0, openShotDuration=1.0),
                             defaultCamera(attackDuration=5.0, openShotDuration=1.0), randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Paradigm Shift!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0), pbpDc.getShowIntervalDesc(
            'The Liquidator slows down all toons!', 3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Freezing Rain!', 3.5))
        pbpDesc3 = Sequence(Wait(10.0), pbpDc.getShowIntervalDesc(
            'Lure and Sound gags are off-limits!', 3.5))
        pbpTrack3 = Sequence(Wait(10.0), pbpText.getShowIntervalCheat('Quality Control!', 3.5))
        pbpDesc = Sequence(Wait(14.0), (pbpDc.getShowIntervalDesc('The Liquidator is transitioning!', 3.5)))
        pbpTrack = Sequence(Wait(14.0), (pbpText.getShowIntervalCheat('Freezing Rain!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpDesc3, pbpTrack4, camTrack2)
    elif name == CHAINSAW_CANNED:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=3), defaultCamera(attackDuration=4, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Blue Chip!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0),
                            pbpDc.getShowIntervalDesc("The Chairman retaliates against toons with cheer!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Snipe!', 3.5))
        pbpDesc = Sequence(Wait(10.0), (
            pbpDc.getShowIntervalDesc('The Chairman bans Toon-Up for 2 turns!', 3.5)))
        pbpTrack = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == CALCULATE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Calculate!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CANNED:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CHOMP:
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == NICKEL_AND_DIME:
        camTrack2 = Sequence(defaultCamera(attackDuration=6.0, openShotDuration=1.0),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 6.0))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc("The High Roller refreshes the toon's damage boost!", 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Rolled!', 3.5)
        pbpDesc = Sequence(Wait(6), (
            pbpDc.getShowIntervalDesc('The High Roller uses the power of refraction to\n clone himself!', 3.5)))
        pbpTrack = Sequence(Wait(6), (pbpText.getShowIntervalCheat("Trick Of The Light!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == QUASH:
        camTrack2 = Sequence(randomActorShot(suit, battle, 5, 'suit'),
                             heldShot(0, 4.0, 4.0, -180, 0, 0, attackDuration - 5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('The High Roller calls upon his trump card!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Ace In The Hole!', 3.5)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == SNAP:
        camTrack2 = Sequence(defaultCamera(attackDuration=5.0, openShotDuration=2.0), defaultCamera(attackDuration=4.5, openShotDuration=2), randomActorShot(suit, battle, attackDuration - 9.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(9.5), pbpDc.getShowIntervalDesc('The Litigator absolutely swamps you with cogs!', 3.5))
        pbpTrack2 = Sequence(Wait(9.5), pbpText.getShowIntervalCheat('Bayou Bash!', 3.5))
        pbpDesc = Sequence(Wait(5.0), pbpDc.getShowIntervalDesc('The Litigator retaliates when soaked!', 3.5))
        pbpTrack = Sequence(Wait(5.0),pbpText.getShowIntervalCheat('Snap!', 3.5))
        pbpTrack4 = pbpText.getShowInterval('Fired!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack, pbpTrack4, pbpDesc, camTrack2)
    elif name == SNAP_WET:
        camTrack2 = Sequence(defaultCamera(attackDuration=5.0, openShotDuration=2.0),
                             defaultCamera(attackDuration=4.5, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 10.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(9.5), pbpDc.getShowIntervalDesc('The Litigator absolutely swamps you with cogs!', 3.5))
        pbpTrack2 = Sequence(Wait(9.5), pbpText.getShowIntervalCheat('Bayou Bash!', 3.5))
        pbpDesc = Sequence(Wait(5.0),
                           pbpDc.getShowIntervalDesc('The Litigator retaliates against the most\ndangerous toon!', 3.5))
        pbpTrack = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Snap!', 3.5))
        pbpTrack4 = pbpText.getShowInterval('Throw Book!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack, pbpTrack4, pbpDesc, camTrack2)
    elif name == CIGAR_SMOKE:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.0, openShotDuration=2.0),
                             randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Cigar Smoke!', 3.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Throw gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'fbd':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CLIPON_TIE:
        camTrack.append(defaultCamera(openShotDuration=2.3))
    elif name == CRUNCH:
        camTrack.append(defaultCamera(openShotDuration=2.4))
    elif name == DEMOTION:
        camTrack.append(defaultCamera(openShotDuration=1.7))
    elif name == DETONATE:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=2),
                         randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Rolodex!', 3.5)
        pbpDesc = Sequence(Wait(6.0), (
        pbpDc.getShowIntervalDesc('The Chainsaw Consultant is now absorbing all damage\ntaken by the cogs!', 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Aggrandize!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == DETONATE_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=3),
                             defaultCamera(attackDuration=5, openShotDuration=3),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Pink Slip!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0),
                            pbpDc.getShowIntervalDesc("The Chairman retaliates when zapped!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Aftershock!', 3.5))
        pbpDesc = Sequence(Wait(10.0), (
            pbpDc.getShowIntervalDesc('The Chairman bans Zap for 2 turns!', 3.5)))
        pbpTrack = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == DETONATE_3:
        camTrack2 = Sequence(defaultCamera(attackDuration=7, openShotDuration=0), randomActorShot(suit, battle, 2, 'suit'), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 4), randomActorShot(suit, battle, attackDuration - 15, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Piercing Intellect!', 1.5)
        pbpDesc3 = Sequence(Wait(7.0), (pbpDc.getShowIntervalDesc(
            'The Ambassador refines all cogs in the battle!', 3.5)))
        pbpTrack3 = Sequence(Wait(7.0), (pbpText.getShowIntervalCheat("Refinement!", 3.5)))
        pbpDesc = Sequence(Wait(15.0), (pbpDc.getShowIntervalDesc(
            "The Ambassador has lost his outer shell!", 3.5)))
        pbpTrack = Sequence(Wait(15.0), (pbpText.getShowIntervalCheat("Overwhelming Authority!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, camTrack2, pbpTrack, pbpDesc)
    elif name == CHAINSAW_DETONATE_3:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=3),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 6))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Falling Knife!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0),
                            pbpDc.getShowIntervalDesc("The Chairman promotes a random cog!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Manager Promotion!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, camTrack2)
    elif name == CHAINSAW_DETONATE_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=3),
                             defaultCamera(attackDuration=attackDuration - 6, openShotDuration=2))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Rolodex!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0),
                            pbpDc.getShowIntervalDesc("The Chainsaw Consultant marks a random toon for\ntermination!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Marked Wood!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, camTrack2)
    elif name == CHAINSAW_DETONATE:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=3),
                             defaultCamera(attackDuration=attackDuration - 6, openShotDuration=4))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Canned!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0),
                            pbpDc.getShowIntervalDesc("The Chainsaw Consultant fires a cog at a random\ntoon!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Offboarding!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, camTrack2)
    elif name == HEAD_ROLLER:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 9.0), randomActorShot(suit, battle, attackDuration - 16, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Falling Knife!', 1.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Ambassador sacrifices a random cog!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Head Roller!', 3.5)))
        pbpDesc3 = Sequence(Wait(16.0), (pbpDc.getShowIntervalDesc('The Ambassador gets stronger and receives a health bonus\nfor every cog he sacrifices!', 3.5)))
        pbpTrack3 = Sequence(Wait(16.0), (pbpText.getShowIntervalCheat("Worker's Compensation!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == HEAD_ROLLER_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 9.0), randomActorShot(suit, battle, attackDuration - 16, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Brainstorm!', 1.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Ambassador sacrifices a random cog!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Head Roller!', 3.5)))
        pbpDesc3 = Sequence(Wait(16.0), (pbpDc.getShowIntervalDesc(
            'The Ambassador gets stronger and receives a health bonus\nfor every cog he sacrifices!', 3.5)))
        pbpTrack3 = Sequence(Wait(16.0), (pbpText.getShowIntervalCheat("Worker's Compensation!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == HEAD_ROLLER_3:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 9.0), randomActorShot(suit, battle, 5.0, 'suit'), randomActorShot(suit, battle, attackDuration - 21, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Blue Chip!', 1.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Ambassador sacrifices every cog in the battle!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Steam Roller!', 3.5)))
        pbpDesc3 = Sequence(Wait(16.0), (pbpDc.getShowIntervalDesc(
            'The Ambassador gets stronger and receives a health bonus\nfor every cog he sacrifices!', 3.5)))
        pbpTrack3 = Sequence(Wait(16.0), (pbpText.getShowIntervalCheat("Worker's Compensation!", 3.5)))
        pbpDesc4 = Sequence(Wait(21.0), (pbpDc.getShowIntervalDesc(
            'All gags have been given a massive damage boost\n for 2 turns!', 3.5)))
        pbpTrack4 = Sequence(Wait(21.0), (pbpText.getShowIntervalCheat("Payback!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack4, pbpDesc4, pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == UNION_BUST:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=1.5), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 9.0), randomActorShot(suit, battle, 5.0, 'suit'),
                             randomActorShot(suit, battle, attackDuration - 20, 'suit'))

        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Reorganize!', 1.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc("The Union Buster sacrifices a random cog!", 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Union Bust!', 3.5)))
        pbpDesc3 = Sequence(Wait(15.0), (pbpDc.getShowIntervalDesc(
            'The Union Buster gets stronger and receives a health bonus\nfor every cog he sacrifices!', 3.5)))
        pbpTrack3 = Sequence(Wait(15.0), (pbpText.getShowIntervalCheat("Worker's Compensation!", 3.5)))
        pbpDesc4 = Sequence(Wait(20.0), (pbpDc.getShowIntervalDesc(
            'Toon-Up and Trap gags are off-limits!', 3.5)))
        pbpTrack4 = Sequence(Wait(20.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack4, pbpDesc4, pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == UNION_BUST_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 9.0), randomActorShot(suit, battle, 5.0, 'suit'),
                             randomActorShot(suit, battle, attackDuration - 21, 'suit'))

        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Falling Knife!', 1.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Union Buster sacrifices a random cog!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Union Bust!', 3.5)))
        pbpDesc3 = Sequence(Wait(16.0), (pbpDc.getShowIntervalDesc(
            'The Union Buster gets stronger and receives a health bonus\nfor every cog he sacrifices!', 3.5)))
        pbpTrack3 = Sequence(Wait(16.0), (pbpText.getShowIntervalCheat("Worker's Compensation!", 3.5)))
        pbpDesc4 = Sequence(Wait(21.0), (pbpDc.getShowIntervalDesc(
            'Toon-Up and Squirt gags are off-limits!', 3.5)))
        pbpTrack4 = Sequence(Wait(21.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack4, pbpDesc4, pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == UNION_BUST_3:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 9.0), randomActorShot(suit, battle, 5.0, 'suit'),
                             randomActorShot(suit, battle, attackDuration - 21, 'suit'))

        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Hostile Takeover!', 1.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Union Buster sacrifices a random cog!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Union Bust!', 3.5)))
        pbpDesc3 = Sequence(Wait(16.0), (pbpDc.getShowIntervalDesc(
            'The Union Buster gets stronger and receives a health bonus\nfor every cog he sacrifices!', 3.5)))
        pbpTrack3 = Sequence(Wait(16.0), (pbpText.getShowIntervalCheat("Worker's Compensation!", 3.5)))
        pbpDesc4 = Sequence(Wait(21.0), (pbpDc.getShowIntervalDesc(
            'Lure and Drop gags are off-limits!', 3.5)))
        pbpTrack4 = Sequence(Wait(21.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack4, pbpDesc4, pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == DOUBLE_TALK:
        camTrack.append(defaultCamera(openShotDuration=1.9))
    elif name == EVICTION_NOTICE:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=2), randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Eviction Notice!', 3.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Zap gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpDesc3 = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Sound gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'csm':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        elif attack['suit'].dna.name == 'fbd':
            return Parallel(pbpTrack3, pbpTrack2, pbpDesc3, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2))
    elif name == BASH:
        shakeIntensity = 5.0
        quake = 1
        camTrack.append(defaultCamera(attackDuration=.75, openShotDuration=0.75))
        camTrack.append(suitCameraShakeShot(suit, attackDuration - .75, shakeIntensity, quake))
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
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=2.0), randomActorShot(suit, battle, 1, 'suit'), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2), heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.0), defaultCamera(attackDuration=5, openShotDuration=2.0), randomActorShot(suit, battle, attackDuration - 17, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(4), pbpDc.getShowIntervalDesc('The Case Manager insures that the cogs in the\nbattle are healed!', 3.5))
        pbpTrack2 = Sequence(Wait(4), pbpText.getShowIntervalCheat('Insurance Plan!', 3.5))
        pbpTrack = pbpText.getShowInterval('Eviction Notice!', 3.5)
        pbpDesc3 = Sequence(Wait(15), (pbpDc.getShowIntervalDesc('Sound and Zap gags are now off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(15), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpDesc4 = Sequence(Wait(10), (pbpDc.getShowIntervalDesc('The Case Manager inflicts a gag debuff on a\nrandom toon!', 3.5)))
        pbpTrack4 = Sequence(Wait(10), (pbpText.getShowIntervalCheat('Corrupted Case Files!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpDesc3, pbpTrack, camTrack2, pbpDesc4, pbpTrack4)
    elif name == OIL_RAIN:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.0, openShotDuration=1.5),
                             defaultCamera(attackDuration=5, openShotDuration=1.0),
                             randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Power Trip!', 3.5)
        pbpDesc2 = Sequence(Wait(4.0),
                            pbpDc.getShowIntervalDesc('All cogs will heal for 50 HP after each attack!',
                                                      3.5))
        pbpTrack2 = Sequence(Wait(4.0), pbpText.getShowIntervalCheat('Oil Rain!', 3.5))
        pbpDesc = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('The Liquidator is transitioning!', 3.5)))
        pbpTrack = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Oil Rain!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, camTrack2, pbpTrack, pbpDesc)
    elif name == HEAT_WAVE:
        camTrack2 = Sequence(randomActorShot(suit, battle, 6.0, 'suit'),
                             defaultCamera(attackDuration=attackDuration - 6, openShotDuration=2.7))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('The temperature is rising!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Temperature Check!', 3.5)
        pbpDesc = Sequence(Wait(6.0), (pbpDc.getShowIntervalDesc("It's getting hot in here!", 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Heat Wave!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack, pbpDesc, camTrack2)
    elif name == EMBEZZLE:
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == FLOOD_THE_MARKET:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Flood The Market!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Level 7 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == MONEY_TRIP:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Synergy!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == WHEEL_SPIN:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == SWIRL_BATH:
        camTrack2 = Sequence(cameraActorShot2(battle, 'highroller-wheelspin', 0),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 8))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc(
            'The High Roller spins the wheel!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Wheel Spin!', 3.5)
        pbpDesc = Sequence(Wait(8.0), (
            pbpDc.getShowIntervalDesc("Time for a commercial break!", 3.5)))
        pbpTrack = Sequence(Wait(8.0), (pbpText.getShowIntervalCheat("Intermission!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == ACCUSATIONS:
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == ACCUSATIONS_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('The storm is starting to pick up!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Oil Rain!', 3.5)
        pbpDesc = Sequence(Wait(4), (
            pbpDc.getShowIntervalDesc("The Powerhouse has had enough of the toon's antics!", 3.5)))
        pbpTrack = Sequence(Wait(4), (pbpText.getShowIntervalCheat("Tank Mentality!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == GAME_SHOW:
        camTrack2 = Sequence(cameraActorShot2(battle, 'highroller-wheelspin', 0), randomActorShot(suit, battle, attackDuration - 8, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('The High Roller spins the wheel!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Wheel Spin!', 3.5)
        pbpDesc = Sequence(Wait(8.0), (
            pbpDc.getShowIntervalDesc("The High Roller fills the battle with contestants!", 3.5)))
        pbpTrack = Sequence(Wait(8.0), (pbpText.getShowIntervalCheat("Game Time!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == EXTRA_TIP:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(5),
                            pbpDc.getShowIntervalDesc('The Litigator absolutely swamps you with cogs!',
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5), pbpText.getShowIntervalCheat('Bayou Bash!', 3.5))
        pbpTrack4 = pbpText.getShowInterval('Power Trip!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, camTrack2)
    elif name == BEGUILE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5), defaultCamera(attackDuration=attackDuration - 5, openShotDuration=2.0))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Fore!', 1.5)
        pbpDesc = Sequence(Wait(6.0), (pbpDc.getShowIntervalDesc("The Ambassador takes another shot!", 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Mulligan!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == REFINEMENT:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=2), randomActorShot(suit, battle, 2, 'suit'), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 10))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Tee Off!', 1.5)
        pbpDesc3 = Sequence(Wait(6.0), (pbpDc.getShowIntervalDesc(
            'The Ambassador refines all cogs in the battle!', 3.5)))
        pbpTrack3 = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat("Refinement!", 3.5)))
        if attack['suit'].dna.name == 'gtk':
            return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, camTrack2)
        else:
            return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, camTrack2)
    elif name == LIFE_INSURANCE:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == WORKERS_COMPENSATION:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == COURT_RECORD_1:
        camTrack2 = Sequence(defaultCamera(attackDuration=attackDuration, openShotDuration=1.25))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Purple Silhouette retaliates when toon's are\ntoo cheery!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Snipe!", 3.5)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == COURT_RECORD_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=attackDuration, openShotDuration=1.25))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Pink Silhouette retaliates when soaked!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Snipe!", 3.5)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == COURT_RECORD_3:
        camTrack2 = Sequence(defaultCamera(attackDuration=attackDuration, openShotDuration=1.25))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Orange Silhouette retaliates when marked!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Snipe!", 3.5)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == COURT_RECORD_4:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             defaultCamera(attackDuration=4.5, openShotDuration=0.25),
                             randomActorShot(suit, battle, attackDuration - 9.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(5),
                            pbpDc.getShowIntervalDesc('The Stenographer retaliates against the least\ndangerous toon!',
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5), pbpText.getShowIntervalCheat('Court Sanction!', 3.5))
        pbpDesc = Sequence(Wait(9.5), (pbpDc.getShowIntervalDesc('Level 6 and 7 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(9.5), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpTrack4 = pbpText.getShowInterval('Mumbo Jumbo!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, pbpTrack, pbpDesc, camTrack2)
    elif name == COURT_RECORD_5:
        camTrack2 = Sequence(defaultCamera(attackDuration=attackDuration, openShotDuration=1.25))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Blue Silhouette applies the winded effect for 5 turns!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Singing Blues!", 3.5)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == SPOTLIGHT:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == COURT_MANDATE:
        camTrack2 = Sequence(defaultCamera(attackDuration=3, openShotDuration=1.5), randomActorShot(suit, battle, attackDuration - 3, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Power Trip!', 3.5)
        pbpDesc = Sequence(Wait(3.0), (
            pbpDc.getShowIntervalDesc("All cogs in the battle are now syphoning health\nfrom the toons!", 3.5)))
        pbpTrack = Sequence(Wait(3.0), (pbpText.getShowIntervalCheat("Tank Mentality!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == COURT_MANDATE_1:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Liquidate!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (
            pbpDc.getShowIntervalDesc("The Powerhouse is now soak resistant!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat("Tank Mentality!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == COURT_MANDATE_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Blue Chip!', 3.5)
        pbpDesc = Sequence(Wait(6.0), (
            pbpDc.getShowIntervalDesc("The Powerhouse is now syphoning health from\nthe toons!", 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat("Tank Mentality!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == COURT_MANDATE_3:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('The Powerhouse unleashes a devastating attack!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Snipe!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The Powerhouse is now entirely immune to lure!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Tank Mentality!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack, pbpDesc, camTrack2)
    elif name == EVIL_EYE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.7),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Evil Eye!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Drop gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dsk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.7))
    elif name == EVIL_EYE_WSI:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 7))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(5),
                            pbpDc.getShowIntervalDesc('The Ambassador heals the other manager!',
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5), pbpText.getShowIntervalCheat('Manager Bonus!', 3.5))
        pbpTrack4 = pbpText.getShowInterval('Tee Off!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, camTrack2)
    elif name == FILIBUSTER:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.5, openShotDuration=2), randomActorShot(suit, battle, attackDuration - 4.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Filibuster!', 3.5)
        pbpDesc = Sequence(Wait(4.5), (pbpDc.getShowIntervalDesc('Level 7 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.5), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpDesc3 = Sequence(Wait(4.5), (pbpDc.getShowIntervalDesc('Level 6 gags are off-limits!!', 3.5)))
        pbpTrack3 = Sequence(Wait(4.5), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'ste':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        elif attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack3, pbpTrack2, pbpDesc3, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.7))
    elif name == FILL_WITH_LEAD:
        camTrack.append(defaultCamera(openShotDuration=3.2))
    elif name == FINGER_WAG:
        camTrack.append(defaultCamera(openShotDuration=2.3))
    elif name == FIRED:
        camTrack.append(defaultCamera(openShotDuration=1.7))
    elif name == FOUNTAIN_PEN:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5), randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Fountain Pen!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Drop gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        if attack['suit'].dna.name == 'csm':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == FREEZE_ASSETS:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == HALF_WINDSOR:
        camTrack.append(defaultCamera(openShotDuration=1.8))
    elif name == HEAD_SHRINK:
        camTrack.append(defaultCamera(openShotDuration=1.3))
    elif name == GLOWER_POWER:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Glower Power!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Toon-Up gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dsk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == CHAINSAW_GLOWER_POWER:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.4),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Glower Power!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Chainsaw Consultant promotes a random cog!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Cut The Slack!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, camTrack2)
    elif name == GUILT_TRIP:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=0.9), randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Guilt Trip!', 3.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Trap gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        if attack['suit'].dna.name == 'csm':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=0.9))
    elif name == GUILT_TRIP_WSI:
        camTrack.append(defaultCamera(openShotDuration=0.9))
    elif name == HANG_UP:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=3.5),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Hang Up!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Level 7 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=3.5))
    elif name == HOT_AIR:
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == MP_HOT_AIR:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.0),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(5), pbpDc.getShowIntervalDesc(
            'The Ottoman is preparing his paperwork!', 3.5))
        pbpTrack2 = Sequence(Wait(5), pbpText.getShowIntervalCheat('Writing Desk!', 3.5))
        pbpTrack = pbpText.getShowInterval('Write Off!', 3.5)
        pbpDesc3 = Sequence(Wait(20), (pbpDc.getShowIntervalDesc('The Ottoman heals all cogs in the battle!', 3.5)))
        pbpTrack3 = Sequence(Wait(20), (pbpText.getShowIntervalCheat('Employee Bonus!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpDesc3, pbpTrack, camTrack2)
    elif name == POISON_SPRAY:
        camTrack2 = Sequence(defaultCamera(attackDuration=6.5, openShotDuration=2.0), randomActorShot(suit, battle, attackDuration - 6.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Paradigm Shift!', 3.5)
        pbpDesc = Sequence(Wait(6.5), (pbpDc.getShowIntervalDesc("The Scapegoat's temperature has cooled down and is now\nprotecting cogs again!", 3.5)))
        pbpTrack = Sequence(Wait(6.5), (pbpText.getShowIntervalCheat("Shield's Up!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == MOB_MENTALITY:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == QUALITY_CONTROL_GAG:
        camTrack2 = Sequence(cameraActorShot2(battle, 'highroller-wheelspin', 0), randomActorShot(suit, battle, attackDuration - 8, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc(
            'The High Roller spins the wheel!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Wheel Spin!', 3.5)
        pbpDesc = Sequence(Wait(8.0), (
            pbpDc.getShowIntervalDesc("The High Roller gives all cogs a wake up call!", 3.5)))
        pbpTrack = Sequence(Wait(8.0), (pbpText.getShowIntervalCheat("Game Time!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == QUALITY_CONTROL_GAG_1:
        camTrack2 = Sequence(cameraActorShot2(battle, 'highroller-wheelspin', 0), randomActorShot(suit, battle, attackDuration - 8, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc(
            'The High Roller spins the wheel!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Wheel Spin!', 3.5)
        pbpDesc = Sequence(Wait(8.0), (
            pbpDc.getShowIntervalDesc("All cogs in the battle are now syphoning the toon's health!", 3.5)))
        pbpTrack = Sequence(Wait(8.0), (pbpText.getShowIntervalCheat("Game Time!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == QUALITY_CONTROL_GAG_2:
        camTrack2 = Sequence(cameraActorShot2(battle, 'highroller-wheelspin', 0), randomActorShot(suit, battle, attackDuration - 8, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc(
            'The High Roller spins the wheel!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Wheel Spin!', 3.5)
        pbpDesc = Sequence(Wait(8.0), (
            pbpDc.getShowIntervalDesc("The High Roller bans all Defensive gags!", 3.5)))
        pbpTrack = Sequence(Wait(8.0), (pbpText.getShowIntervalCheat("Game Time!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == QUALITY_CONTROL_GAG_3:
        camTrack2 = Sequence(cameraActorShot2(battle, 'highroller-wheelspin', 0), randomActorShot(suit, battle, attackDuration - 8, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc(
            'The High Roller spins the wheel!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Wheel Spin!', 3.5)
        pbpDesc = Sequence(Wait(8.0), (
            pbpDc.getShowIntervalDesc("The High Roller bans all offensive gags!", 3.5)))
        pbpTrack = Sequence(Wait(8.0), (pbpText.getShowIntervalCheat("Game Time!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == BAR:
        camTrack2 = Sequence(randomActorShot(suit, battle, 1.5, 'suit'), heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 1.5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Red Silhouette retaliates when trapped or\nleft unlured!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Bar!", 3.5)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == QUALITY_CONTROL_LEVEL:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Freeze Assets!', 1.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Liquidator heals for 250 HP and reverts back to\nher normal state!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Inversion!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == QUALITY_CONTROL_LEVEL_1:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2),
                             randomActorShot(suit, battle, 8, 'suit'), randomActorShot(suit, battle, 5, 'suit'), randomActorShot(suit, battle, 5, 'suit'), defaultCamera(attackDuration=attackDuration - 24, openShotDuration=2.5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Schmooze!', 1.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Radiographer is now absorbing damage dealt to\nother cogs!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Radio Infrequency!', 3.5)))
        pbpDesc3 = Sequence(Wait(13.0),
                            (pbpDc.getShowIntervalDesc('Level 5 and 6 gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(13.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        pbpDesc4 = Sequence(Wait(18.0),
                            (pbpDc.getShowIntervalDesc('Squirt gags are off-limits!', 3.5)))
        pbpTrack4 = Sequence(Wait(18.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        pbpDesc5 = Sequence(Wait(24.0),
                            (pbpDc.getShowIntervalDesc('The Radiographer retaliates when soaked!', 3.5)))
        pbpTrack5 = Sequence(Wait(24.0), (pbpText.getShowIntervalCheat("Breach Of Contract!", 3.5)))
        return Parallel(pbpTrack3, pbpTrack4, pbpDesc4, pbpDesc3, pbpTrack2, pbpTrack, pbpDesc, pbpTrack5, pbpDesc5, camTrack2)
    elif name == QUALITY_CONTROL_LEVEL_2:
        camTrack2 = Sequence(defaultCamera(attackDuration=5.5, openShotDuration=2.0),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 6.0),
                             randomActorShot(suit, battle, attackDuration - 11.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(5.5), pbpDc.getShowIntervalDesc(
            'The Union Buster gives every cog in the battle a contract\nand a raise!', 3.5))
        pbpTrack2 = Sequence(Wait(5.5), pbpText.getShowIntervalCheat('Contract Enforcement!', 3.5))
        pbpTrack = pbpText.getShowInterval('Glower Power!', 3.5)
        pbpDesc3 = Sequence(Wait(11.5), (pbpDc.getShowIntervalDesc('Squirt and Zap gags are now off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(11.5), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpDesc3, pbpTrack, camTrack2)
    elif name == QUALITY_CONTROL_LEVEL_3:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5),
                             defaultCamera(attackDuration=5, openShotDuration=1.5), randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Evil Eye!', 1.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Union Buster retaliates when The Radiographer\nis soaked!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Breach Of Contract!', 3.5)))
        pbpDesc3 = Sequence(Wait(10), (pbpDc.getShowIntervalDesc('Zap and Sound gags are now off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(10), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpTrack3, pbpDesc3, pbpDesc, camTrack2)
    elif name == MANAGERIAL_PROTECTION:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=0),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Piercing Intellect!', 1.5)
        pbpDesc3 = Sequence(Wait(6.0), (pbpDc.getShowIntervalDesc('The Ambassador is now entirely immune to gags!', 3.5)))
        pbpTrack3 = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat("Managerial Protection!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, camTrack2)
    elif name == RADIO_INFREQUENCY:
        camTrack2 = Sequence(defaultCamera(attackDuration=7, openShotDuration=2.5),
                             randomActorShot(suit, battle, 8, 'suit'), randomActorShot(suit, battle, attackDuration - 15, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Song And Dance!', 1.5)
        pbpDesc = Sequence(Wait(7.0), (
            pbpDc.getShowIntervalDesc("The Radiographer inflicts a damage debuff to Lure\n and Sound gags!", 3.5)))
        pbpTrack = Sequence(Wait(7.0), (pbpText.getShowIntervalCheat('Radio Infrequency!', 3.5)))
        pbpDesc3 = Sequence(Wait(15.0),
                            (pbpDc.getShowIntervalDesc('Level 6 and 7 gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(15.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == VOICEMAIL:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.8),
                             randomActorShot(suit, battle, 5.0, 'suit'), randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Filibuster!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("The Wiretapper is now entirely immune to gags!", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Voicemail!', 3.5)))
        pbpDesc3 = Sequence(Wait(10.0), (pbpDc.getShowIntervalDesc('Level 6 and 8 gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat("Quality Control!", 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc3, pbpTrack3, pbpDesc, camTrack2)
    elif name == WIRE_CUT:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2), defaultCamera(attackDuration=5, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Throw Book!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0), pbpDc.getShowIntervalDesc('The Bookkeeper retaliates when marked!', 3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Paper Cut!', 3.5))
        pbpDesc = Sequence(Wait(10.0), (pbpDc.getShowIntervalDesc('Throw and Sound gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack4, pbpDesc2, camTrack2)
    elif name == PAPER_CUT:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2), defaultCamera(attackDuration=8, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 13, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Cigar Smoke!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0), pbpDc.getShowIntervalDesc('The Bookkeeper reduces your gag power!', 3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Paper Cut!', 3.5))
        pbpDesc = Sequence(Wait(13.0), (pbpDc.getShowIntervalDesc('Toon-Up and Zap gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(13.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack4, pbpDesc2, camTrack2)
    elif name == EXPLODING_BILL:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=2), defaultCamera(attackDuration=5, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Eviction Notice!', 3.5)
        pbpDesc2 = Sequence(Wait(4.0), pbpDc.getShowIntervalDesc('The Bookkeeper inflicts a damage vulnerability\non a random toon!', 3.5))
        pbpTrack2 = Sequence(Wait(4.0), pbpText.getShowIntervalCheat('Exploding Document!', 3.5))
        pbpDesc = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('Zap and Drop gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack4, pbpDesc2, camTrack2)
    elif name == FIRE_COG:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=0.5),
                             defaultCamera(attackDuration=attackDuration - 5, openShotDuration=2))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Double Talk!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The Ottoman has trapped you in his whirlwind\nof paperwork!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Whirlwind!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == CAGE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2),
                             defaultCamera(attackDuration=5, openShotDuration=2))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Pink Slip!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Chairman locks up a toon for 1 turn!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Cage!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, camTrack2)
    elif name == GOOD_MORNING_TOONTOWN:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == CARESS:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == COLLECT_CALL_FEES:
        camTrack2 = Sequence(randomActorShot(suit, battle, 3.0, 'suit'), defaultCamera(attackDuration=6, openShotDuration=2.7), randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('An audit is approaching!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Calculating Calling Fees!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The collect call fees are racking up!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Collect Call Costs!', 3.5)))
        pbpDesc3 = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('Level 6 and 8 gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, pbpDesc2, pbpTrack, pbpDesc, camTrack2)
    elif name == COLLECT_CALL:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.5, openShotDuration=2), defaultCamera(attackDuration=9, openShotDuration=1),
                             randomActorShot(suit, battle, attackDuration - 13.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 =  Sequence(Wait(4.5), pbpDc.getShowIntervalDesc("The Wiretapper inflicts a damage vulnerability\non a random toon!", 3.5))
        pbpTrack2 =  Sequence(Wait(4.5),  pbpText.getShowIntervalCheat('Collect Call!', 3.5))
        pbpTrack4 = pbpText.getShowInterval('Filibuster!', 3.5)
        pbpDesc = Sequence(Wait(13.5), (pbpDc.getShowIntervalDesc('Level 5 and 7 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(13.5), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpTrack4, pbpDesc, pbpDesc2, camTrack2)
    elif name == SLUSH_FUND:
        camTrack2 = Sequence(defaultCamera(attackDuration=1.5, openShotDuration=0.5), heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 1.5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The High Roller Silhouette donates part of it's health\nto the High Roller!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Trick Of The Light!", 3.5)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == JURY_NOTICE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.0),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Con-Duck-Tion', 3.5)
        pbpDesc = Sequence(Wait(5), (
            pbpDc.getShowIntervalDesc('The High Roller is now vulnerable for 2 turns!', 3.5)))
        pbpTrack = Sequence(Wait(5), (pbpText.getShowIntervalCheat('Game Time!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == CEASE_AND_DESIST:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.5, openShotDuration=2),
                             defaultCamera(attackDuration=4.5, openShotDuration=0.25),
                             randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(4.5),
                            pbpDc.getShowIntervalDesc('The Stenographer retaliates against unbound Toons!',
                                                      3.5))
        pbpTrack2 = Sequence(Wait(4.5), pbpText.getShowIntervalCheat('Court Sanction!', 3.5))
        pbpDesc = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('Level 5 and 6 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpTrack4 = pbpText.getShowInterval('Mumbo Jumbo!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, pbpTrack, pbpDesc, camTrack2)
    elif name == INVESTMENT:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5), randomActorShot(suit, battle, 1, 'suit'), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 8))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(5),
                            pbpDc.getShowIntervalDesc('Everyone in the battle takes a huge loss!',
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5), pbpText.getShowIntervalCheat('Bombshell!', 3.5))
        pbpTrack4 = pbpText.getShowInterval('Power Trip!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, camTrack2)
    elif name == FIELD_PROMOTION:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.0),
                             randomActorShot(suit, battle, 13.7, 'suit'), randomActorShot(suit, battle, attackDuration - 18.7, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc("The High Roller gives all toons a massive damage boost!", 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Rolled!', 3.5)
        pbpDesc = Sequence(Wait(18.7), (pbpDc.getShowIntervalDesc('The High Roller uses the power of refraction to\n clone himself!', 3.5)))
        pbpTrack = Sequence(Wait(18.7), (pbpText.getShowIntervalCheat('Trick Of The Light!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc2, pbpDesc, camTrack2)
    elif name == WIRETAPPED:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5), defaultCamera(attackDuration=5, openShotDuration=2.5),
                             randomActorShot(suit, battle, 5.0, 'suit'), randomActorShot(suit, battle, attackDuration - 15, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack4 = pbpText.getShowInterval('Paradigm Shift!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0), pbpDc.getShowIntervalDesc("The Wiretapper syphons your health!", 3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Wiretapped!', 3.5))
        pbpDesc = Sequence(Wait(10.0), (pbpDc.getShowIntervalDesc('Level 5 and 6 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        pbpDesc3 = Sequence(Wait(15.0), (pbpDc.getShowIntervalDesc('The Wiretapper is now taking more damage!', 3.5)))
        pbpTrack3 = Sequence(Wait(15.0), (pbpText.getShowIntervalCheat('Payback!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack4, pbpTrack3, pbpDesc3, pbpDesc2, camTrack2)
    elif name == SHORT_SQUEEZE:
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == BLUE_CHIP:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == FALLING_KNIFE:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Falling Knife!', 3.5)
        pbpDesc = Sequence(Wait(6.0), (pbpDc.getShowIntervalDesc('Trap gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dsk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == JARGON:
        camTrack2 = Sequence(defaultCamera(attackDuration=5.5, openShotDuration=2.8), randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Jargon!', 3.5)
        pbpDesc = Sequence(Wait(5.5), (pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.5), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        if attack['suit'].dna.name == 'ste':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LEGALESE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LIQUIDATE:
        camTrack.append(defaultCamera(openShotDuration=1))
    elif name == HOSTILE_TAKEOVER:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=2.5),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Hostile Takeover!', 3.5)
        pbpDesc = Sequence(Wait(6.0), (pbpDc.getShowIntervalDesc('Squirt gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dsk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == MARKET_CRASH:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Market Crash!', 3.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Level 6 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == MUMBO_JUMBO:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.5, openShotDuration=2), randomActorShot(suit, battle, attackDuration - 4.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Mumbo Jumbo!', 3.5)
        pbpDesc = Sequence(Wait(4.5), (pbpDc.getShowIntervalDesc('Level 7 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.5), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        if attack['suit'].dna.name == 'ste':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.8))
    elif name == PARADIGM_SHIFT:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=1.6),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Paradigm Shift!', 3.5)
        pbpDesc = Sequence(Wait(6.0), (pbpDc.getShowIntervalDesc('Level 5 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=1.6))
    elif name == PECKING_ORDER:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Pecking Order!', 3.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Level 5 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == PECKING_ORDER_WSI:
        camTrack.append(defaultCamera(openShotDuration=2.3))
    elif name == PLAY_HARDBALL:
        camTrack.append(defaultCamera(openShotDuration=2.3))
    elif name == PICK_POCKET:
        camTrack.append(allGroupLowShot(suit, 2.7))
    elif name == DENIAL_OF_SERVICE:
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == VOODOO_MAGIC:
        camTrack.append(defaultCamera(openShotDuration=0.25))
    elif name == COURT_SANCTION:
        camTrack2 = Sequence(defaultCamera(attackDuration=5.5, openShotDuration=2), defaultCamera(attackDuration=4.5, openShotDuration=0.25), randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(5.5), pbpDc.getShowIntervalDesc('The Stenographer retaliates against the least\ndangerous toon!', 3.5))
        pbpTrack2 = Sequence(Wait(5.5), pbpText.getShowIntervalCheat('Court Sanction!', 3.5))
        pbpDesc = Sequence(Wait(10), (pbpDc.getShowIntervalDesc('Level 5 and 8 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(10), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpTrack4 = pbpText.getShowInterval('Jargon!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, pbpTrack, pbpDesc, camTrack2)
    elif name == CHAINSAW_REVVING_UP:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Glower Power!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Chainsaw Consultant has interrupted his own\nattack!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Throttle!', 3.5))
        pbpDesc = Sequence(Wait(20.0), (
            pbpDc.getShowIntervalDesc('The Chainsaw Consultant gets stronger after every attack!', 3.5)))
        pbpTrack = Sequence(Wait(20.0), (pbpText.getShowIntervalCheat('Revving Up!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == PINK_SLIP:
        camTrack.append(defaultCamera(openShotDuration=1.8))
    elif name == POUND_KEY:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=2.8), randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Pound Key!', 3.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpDesc3 = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Level 6 gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'ste':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        elif attack['suit'].dna.name == 'frs':
            return Parallel(pbpTrack2, pbpTrack3, pbpDesc3, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.8))
    elif name == CLOSE_THE_LOOP:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             defaultCamera(attackDuration=5, openShotDuration=2.5),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Fountain Pen!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Case Manager legally binds a toon to take\nextra damage!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Legal Bindings!', 3.5))
        pbpDesc = Sequence(Wait(13.0), (pbpDc.getShowIntervalDesc('Trap and Throw gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(13.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == POWER_TIE:
        camTrack.append(defaultCamera(openShotDuration=1.4))
    elif name == POWER_TRIP_WSI:
        camTrack.append(defaultCamera(openShotDuration=1.1))
    elif name == CHAINSAW_QUAKE:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=2),
                             defaultCamera(attackDuration=attackDuration - 6, openShotDuration=4))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Quake!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0),
                            pbpDc.getShowIntervalDesc("The Chainsaw Consultant fires all the cogs at\nthe toons!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Layoffs!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, camTrack2)
    elif name == POWER_TRIP:
        camTrack.append(defaultCamera(openShotDuration=1.1))
    elif name == HR_POWER_TRIP:
        camTrack.append(defaultCamera(openShotDuration=1.1))
    elif name == CHAINSAW_ROLODEX:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Canned!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0),
                            pbpDc.getShowIntervalDesc("The Chainsaw Consultant has received a personality\nupgrade!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Termination Sequence!', 3.5))
        pbpDesc = Sequence(Wait(20.0), (pbpDc.getShowIntervalDesc('The Chainsaw Consultant gets stronger after every attack!', 3.5)))
        pbpTrack = Sequence(Wait(20.0), (pbpText.getShowIntervalCheat('Revving Up!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == RESTRAINING_ORDER_WSI:
        camTrack.append(defaultCamera(openShotDuration=2.8))
    elif name == QUAKE:
        shakeIntensity = 5.15
        quake = 1
        camTrack2 = Sequence(suitCameraShakeShot(suit, 5.5, shakeIntensity, quake),
                             randomActorShot(suit, battle, attackDuration - 5.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Quake!', 3.5)
        pbpDesc = Sequence(Wait(5.5), (pbpDc.getShowIntervalDesc('Throw gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.5), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dsk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(suitCameraShakeShot(suit, attackDuration, shakeIntensity, quake))
    elif name == LD_AFTERSHOCK:
        camTrack2 = Sequence(randomActorShot(suit, battle, 2, 'suit'), randomActorShot(suit, battle, 3.75, 'suit'),
                             heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 5.75))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Dice will randomly decide who gets damaged!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Dice Roulette!", 3.5)
        pbpDesc2 = Sequence(Wait(5.75), pbpDc.getShowIntervalDesc("The Dice will land on all Toons!", 3.5))
        pbpTrack2 = Sequence(Wait(5.75), pbpText.getShowIntervalCheat("Dice Roulette!", 3.5))
        return Parallel(pbpTrack, pbpDesc, pbpTrack2, pbpDesc2, camTrack2)
    elif name == MP_QUAKE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.0),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(5), pbpDc.getShowIntervalDesc(
            'The Ottoman is preparing his paperwork!', 3.5))
        pbpTrack2 = Sequence(Wait(5), pbpText.getShowIntervalCheat('Writing Desk!', 3.5))
        pbpTrack = pbpText.getShowInterval('Short Squeeze!', 3.5)
        pbpDesc3 = Sequence(Wait(20), (pbpDc.getShowIntervalDesc('The Ottoman heals the other Manager in battle!', 3.5)))
        pbpTrack3 = Sequence(Wait(20), (pbpText.getShowIntervalCheat('Manager Bonus!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpDesc3, pbpTrack, camTrack2)
    elif name == LD_QUAKE:
        camTrack2 = Sequence(randomActorShot(suit, battle, 2, 'suit'), randomActorShot(suit, battle, 3.75, 'suit'),
                             heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 5.75))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Dice will randomly decide who gets damaged!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Dice Roulette!", 3.5)
        pbpDesc2 = Sequence(Wait(5.75), pbpDc.getShowIntervalDesc("The Dice will land on everybody in the battle!", 3.5))
        pbpTrack2 = Sequence(Wait(5.75), pbpText.getShowIntervalCheat("Dice Roulette!", 3.5))
        return Parallel(pbpTrack, pbpDesc, pbpTrack2, pbpDesc2, camTrack2)
    elif name == LD_EVICTION_NOTICE:
        camTrack2 = Sequence(randomActorShot(suit, battle, 2, 'suit'), randomActorShot(suit, battle, 3.75, 'suit'),
                             heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 5.75))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Dice will randomly decide who gets damaged!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Dice Roulette!", 3.5)
        pbpDesc2 = Sequence(Wait(5.75), pbpDc.getShowIntervalDesc("The Dice will land on a random Toon!", 3.5))
        pbpTrack2 = Sequence(Wait(5.75), pbpText.getShowIntervalCheat("Dice Roulette!", 3.5))
        return Parallel(pbpTrack, pbpDesc, pbpTrack2, pbpDesc2, camTrack2)
    elif name == RAZZLE_DAZZLE:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=0.5),
                             randomActorShot(suit, battle, attackDuration - 4, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Razzle Dazzle!', 3.5)
        pbpDesc = Sequence(Wait(4.0), (pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'blr':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == RED_TAPE:
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LD_RED_TAPE:
        camTrack2 = Sequence(randomActorShot(suit, battle, 2, 'suit'), randomActorShot(suit, battle, 3.75, 'suit'),
                             heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 5.75))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Dice will randomly decide who gets damaged!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Dice Roulette!", 3.5)
        pbpDesc2 = Sequence(Wait(5.75), pbpDc.getShowIntervalDesc("The Dice will land on nobody!", 3.5))
        pbpTrack2 = Sequence(Wait(5.75), pbpText.getShowIntervalCheat("Dice Roulette!", 3.5))
        return Parallel(pbpTrack, pbpDesc, pbpTrack2, pbpDesc2, camTrack2)
    elif name == RE_ORG:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 4.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Reorganize!', 3.5)
        pbpDesc = Sequence(Wait(4.5), (pbpDc.getShowIntervalDesc('Zap gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.5), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dsk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == LD_RE_ORG:
        camTrack2 = Sequence(randomActorShot(suit, battle, 2, 'suit'), randomActorShot(suit, battle, 3.75, 'suit'),
                             heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 5.75))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc("The Dice will randomly decide who gets damaged!", 3.5)
        pbpTrack = pbpText.getShowIntervalCheat("Dice Roulette!", 3.5)
        pbpDesc2 = Sequence(Wait(5.75), pbpDc.getShowIntervalDesc("The Dice will land on all cogs!", 3.5))
        pbpTrack2 = Sequence(Wait(5.75), pbpText.getShowIntervalCheat("Dice Roulette!", 3.5))
        return Parallel(pbpTrack, pbpDesc, pbpTrack2, pbpDesc2, camTrack2)
    elif name == REARRANGE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.1),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Filibuster!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The Ottoman has decided to pick up the pace\n and now gets stronger after every attack!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Overclocked!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == RESTRAINING_ORDER:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2), randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Restraining Order!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Squirt gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpDesc3 = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Zap gags are off-limits!!', 3.5)))
        pbpTrack3 = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'csm':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        elif attack['suit'].dna.name == 'fbd':
            return Parallel(pbpTrack3, pbpTrack2, pbpDesc3, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2))
    elif name == ROLODEX:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=3.0), randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Rolodex!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Toon-Up gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        pbpDesc3 = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Sound gags are off-limits!!', 3.5)))
        pbpTrack3 = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'csm':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        elif attack['suit'].dna.name == 'fbd':
            return Parallel(pbpTrack3, pbpTrack2, pbpDesc3, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == RUBBER_STAMP:
        camTrack.append(defaultCamera(openShotDuration=3.2))
    elif name == RUB_OUT:
        camTrack.append(defaultCamera(openShotDuration=2.2))
    elif name == SACKED:
        camTrack.append(defaultCamera(openShotDuration=1.9))
    elif name == SCHMOOZE:
        camTrack2 = Sequence(defaultCamera(attackDuration=4.5, openShotDuration=2.0),
                             randomActorShot(suit, battle, attackDuration - 4.5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Schmooze!', 3.5)
        pbpDesc = Sequence(Wait(4.5), (pbpDc.getShowIntervalDesc('Level 7 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(4.5), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'blr':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == CONE_OF_SHAME:
        camTrack2 = Sequence(defaultCamera(attackDuration=9, openShotDuration=2.0),
                             defaultCamera(attackDuration=4, openShotDuration=0.5), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 14))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Fired!', 3.5)
        pbpDesc = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('The Safe-ty Supervisor retaliates against the least\ndangerous toon!', 3.5)))
        pbpTrack = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Safe-ty Breach!', 3.5)))
        pbpDesc3 = Sequence(Wait(15.0), (
            pbpDc.getShowIntervalDesc('The Safe-ty Supervisor promotes a random cog!', 3.5)))
        pbpTrack3 = Sequence(Wait(15.0), (pbpText.getShowIntervalCheat('Safe-ty Promotion!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack3, pbpDesc3, camTrack2)
    elif name == SHAKE:
        shakeIntensity = 1.75
        camTrack.append(suitCameraShakeShot(suit, attackDuration, shakeIntensity))
    elif name == SHRED:
        camTrack.append(defaultCamera(openShotDuration=4.1))
    elif name == SONG_AND_DANCE:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=4.1),
                             randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Song And Dance!', 3.5)
        pbpDesc = Sequence(Wait(6.0), (pbpDc.getShowIntervalDesc('Level 6 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'blr':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == MP_SONG_AND_DANCE:
        camTrack2 = Sequence(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc(
            'The Ottoman is boring his allies with\nconversation!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Meaningful Conversation!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, camTrack2)
    elif name == SPIN:
        camTrack.append(defaultCamera(openShotDuration=1.7))
    elif name == DUCK_SPIN:
        camTrack.append(defaultCamera(openShotDuration=1.7))
    elif name == SYNERGY:
        camTrack2 = Sequence(randomActorShot(suit, battle, 3.0, 'suit'), defaultCamera(attackDuration=6, openShotDuration=2.7), randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('An audit is approaching!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Calculating Interest Fees!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The interest fees are racking up!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Compounding Interest!', 3.5)))
        pbpDesc3 = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('Level 7 and 8 gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, pbpDesc2, pbpTrack, pbpDesc, camTrack2)
    elif name == UNION_DUES:
        camTrack2 = Sequence(randomActorShot(suit, battle, 3.0, 'suit'), defaultCamera(attackDuration=6, openShotDuration=2.7), randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('An audit is approaching!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Calculating Union Dues!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The dues are racking up!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Union Dues!', 3.5)))
        pbpDesc3 = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('Toon-Up and Trap gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, pbpDesc2, pbpTrack, pbpDesc, camTrack2)
    elif name == COURT_COSTS:
        camTrack2 = Sequence(randomActorShot(suit, battle, 3.0, 'suit'), defaultCamera(attackDuration=6, openShotDuration=2.7), randomActorShot(suit, battle, attackDuration - 9, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = pbpDc.getShowIntervalDesc('An audit is approaching!', 3.5)
        pbpTrack2 = pbpText.getShowIntervalCheat('Calculating Costs!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('The fees are racking up!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Court Costs!', 3.5)))
        pbpDesc3 = Sequence(Wait(9.0), (pbpDc.getShowIntervalDesc('Level 6 and 8 gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(9.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        return Parallel(pbpTrack3, pbpDesc3, pbpTrack2, pbpDesc2, pbpTrack, pbpDesc, camTrack2)
    elif name == UNION_BUSTER:
        camTrack2 = Sequence(defaultCamera(attackDuration=6, openShotDuration=2.0),
                             defaultCamera(attackDuration=4, openShotDuration=1.0),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Falling Knife!', 3.5)
        pbpDesc = Sequence(Wait(6.0),(pbpDc.getShowIntervalDesc('The Union Buster applies a damage vulnerability to\na random toon!', 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Union Buster!', 3.5)))
        pbpDesc3 = Sequence(Wait(10.0),
                           (pbpDc.getShowIntervalDesc('Toon-Up and Trap gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, pbpTrack3, pbpDesc3, camTrack2)
    elif name == SNOW:
        camTrack2 = Sequence(suitCameraShakeShot(suit, 5.5, 0.25), randomActorShot(suit, battle, 4.0, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Tremor!', 3.5)
        pbpDesc = Sequence(Wait(5.5), (pbpDc.getShowIntervalDesc("The Scapegoat syphons toon's health when he's alone\nand is now protecting cogs again!", 3.5)))
        pbpTrack = Sequence(Wait(5.5), (pbpText.getShowIntervalCheat('Barnyard Bash!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == BOMB_CAKE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=1.5),
                             defaultCamera(attackDuration=5, openShotDuration=1.5),
                             randomActorShot(suit, battle, attackDuration - 10, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Piercing Intellect!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0),
                            pbpDc.getShowIntervalDesc("The Chairman retaliates when marked!",
                                                      3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Bomb Cake!', 3.5))
        pbpDesc = Sequence(Wait(10.0), (
            pbpDc.getShowIntervalDesc('The Chairman bans Throw for 2 turns!', 3.5)))
        pbpTrack = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpDesc, camTrack2)
    elif name == BOMB:
        camTrack2 = Sequence(defaultCamera(attackDuration=4, openShotDuration=1.5),
                             defaultCamera(attackDuration=4, openShotDuration=0.5),  randomActorShot(suit, battle, attackDuration - 8, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Razzle Dazzle!', 3.5)
        pbpDesc = Sequence(Wait(5.0),
                           (pbpDc.getShowIntervalDesc('The Radiographer releases a devastating attack against\na random toon!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Hot Take!', 3.5)))
        pbpDesc3 = Sequence(Wait(8.0),
                           (pbpDc.getShowIntervalDesc(
                               'Level 6 and 8 gags are off-limits!', 3.5)))
        pbpTrack3 = Sequence(Wait(8.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc3, pbpTrack3, pbpDesc, camTrack2)
    elif name == LEGAL_BINDINGS:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2), defaultCamera(attackDuration=5, openShotDuration=2), randomActorShot(suit, battle, 1, 'suit'), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 2),
                             heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.0), randomActorShot(suit, battle, attackDuration - 16, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack3 = pbpText.getShowInterval('Rolodex!', 3.5)
        pbpDesc2 = Sequence(Wait(5.0), pbpDc.getShowIntervalDesc("The Case Manager legally binds a toon to take\nextra damage!", 3.5))
        pbpTrack2 = Sequence(Wait(5.0), pbpText.getShowIntervalCheat('Legal Bindings!', 3.5))
        pbpDesc4 = Sequence(Wait(10.0), (pbpDc.getShowIntervalDesc('The Case Manager insures that cogs are healed\nevery round!', 3.5)))
        pbpTrack4 = Sequence(Wait(10.0), (pbpText.getShowIntervalCheat('Insurance Plan!', 3.5)))
        pbpDesc = Sequence(Wait(16.0), (pbpDc.getShowIntervalDesc('Toon-Up and Squirt gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(16.0), (pbpText.getShowIntervalCheat('Court Record!', 3.5)))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack3, pbpTrack, pbpTrack4, pbpDesc4, pbpDesc, camTrack2)
    elif name == TABULATE:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2),
                             randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Tabulate!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc('Level 5 gags are off-limits!', 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'dvk':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == TEE_OFF:
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == MULLIGAN:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5),
                             defaultCamera(attackDuration=attackDuration - 5, openShotDuration=1.5))

        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack = pbpText.getShowInterval('Tee Off!', 3.5)
        pbpDesc2 = Sequence(Wait(6.0), pbpDc.getShowIntervalDesc("This cog gets another shot!", 3.5))
        pbpTrack2 = Sequence(Wait(6.0), pbpText.getShowIntervalCheat('Mulligan!', 3.5))
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack, camTrack2)
    elif name == CLOCK_CHANGE:
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == TREMOR:
        shakeIntensity = 0.25
        camTrack.append(suitCameraShakeShot(suit, attackDuration, shakeIntensity))
    elif name == WHITE_POWDER:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.5), defaultCamera(attackDuration=4.5, openShotDuration=2.5), randomActorShot(suit, battle, 4.5, 'suit'), cameraActorShot(suit, 'litigator-bellow', attackDuration - 25.0), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 18))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc2 = Sequence(Wait(9.5),
                            pbpDc.getShowIntervalDesc('The Litigator absolutely swamps you with cogs!', 3.5))
        pbpTrack2 = Sequence(Wait(9.5), pbpText.getShowIntervalCheat('Bayou Bash!', 3.5))
        pbpDesc3 = Sequence(Wait(14.5),
                            pbpDc.getShowIntervalDesc('The Litigator removes all negative effects from the\ncogs!',
                                                      3.5))
        pbpTrack3 = Sequence(Wait(14.5), pbpText.getShowIntervalCheat('Bayou Bellow!', 3.5))
        pbpDesc = Sequence(Wait(5), pbpDc.getShowIntervalDesc('The Litigator retailiates against the most\ndangerous toon!', 3.5))
        pbpTrack = Sequence(Wait(5), pbpText.getShowIntervalCheat('Snap!', 3.5))
        pbpTrack4 = pbpText.getShowInterval('Evil Eye!', 3.5)
        return Parallel(pbpTrack2, pbpDesc2, pbpTrack4, pbpTrack, pbpDesc, camTrack2, pbpDesc3, pbpTrack3)
    elif name == WATERCOOLER:
        camTrack.append(defaultCamera())
    elif name == BLACK_ORB:
        camTrack.append(defaultCamera())
    elif name == WITHDRAWAL:
        camTrack.append(defaultCamera(openShotDuration=1.2))
    elif name == INK_DRAIN:
        camTrack.append(defaultCamera(openShotDuration=2))
        camTrack.append(randomActorShot(suit, battle, 4, 'suit'))
    elif name == WRITE_OFF:
        camTrack.append(defaultCamera())
    elif name == OVERDRAFT:
        camTrack.append(defaultCamera())
    elif name == ENRAGED:
        camTrack2 = Sequence(suitCameraShakeShot(suit, 6, 0.25), randomActorShot(suit, battle, attackDuration - 6, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Tremor!', 3.5)
        pbpDesc = Sequence(Wait(6.0),
                           (pbpDc.getShowIntervalDesc("The Scapegoat's temperature has boiled over!", 3.5)))
        pbpTrack = Sequence(Wait(6.0), (pbpText.getShowIntervalCheat('Enraged!', 3.5)))
        return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
    elif name == THROW_BOOK:
        camTrack2 = Sequence(defaultCamera(attackDuration=5, openShotDuration=2.0), randomActorShot(suit, battle, attackDuration - 5, 'suit'))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpTrack2 = pbpText.getShowInterval('Throw Book!', 3.5)
        pbpDesc = Sequence(Wait(5.0), (pbpDc.getShowIntervalDesc("Squirt gags are off-limits", 3.5)))
        pbpTrack = Sequence(Wait(5.0), (pbpText.getShowIntervalCheat('Quality Control!', 3.5)))
        if attack['suit'].dna.name == 'fbd':
            return Parallel(pbpTrack2, pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(defaultCamera(openShotDuration=2.0))
    else:
        notify.warning('unknown attack id in chooseSuitShot: %d using default cam' % name)
        camTrack.append(defaultCamera())
    pbpText = attack['playByPlayText']
    displayName = TTLocalizer.SuitAttackNames[attack['name']]
    if attack['name'] in TTLocalizer.SuitCheatNames:
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(TTLocalizer.SuitCheatDescription[attack['name']], 3.5)
        pbpTrack = pbpText.getShowIntervalCheat(displayName, 3.5)
        return Parallel(camTrack, pbpTrack, pbpDesc)
    if float(suit.currHP) > float(suit.maxHP * 1.5):
        pbpTrack = pbpText.getShowIntervalOvercharged(displayName, 3.5)
    else:
        pbpTrack = pbpText.getShowInterval(displayName, 3.5)
    track = Parallel(camTrack, pbpTrack)
    if diedTrack == None:
        return track
    pbpTrackDied = Sequence(pbpTrack, diedTrack)
    mtrack = Parallel(track, pbpTrackDied)
    return mtrack  

def chooseSuitCloseShot(attack, openDuration, openName, attackDuration):
    av = None
    duration = attackDuration - openDuration
    if duration < 0:
        duration = 1e-06
    groupStatus = attack['group']
    diedTrack = None
    if groupStatus == ATK_TGT_SINGLE:
        av = attack['target']['toon']
        shotChoices = [avatarCloseUpThreeQuarterRightShot, suitGroupThreeQuarterLeftBehindShot]
        died = attack['target']['died']
        if died != 0:
            pbpText = attack['playByPlayText']
            diedText = av.getName() + ' was defeated!'
            diedTextList = [diedText]
            diedTrack = pbpText.getToonsDiedInterval(diedTextList, 3.5)
    elif groupStatus == ATK_TGT_GROUP:
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
    if diedTrack == None:
        return track
    else:
        mtrack = Parallel(track, diedTrack)
        return mtrack
    return


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
