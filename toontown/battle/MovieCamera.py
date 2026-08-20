from __future__ import absolute_import
from __future__ import print_function
import random
from panda3d.core import *
from toontown.suit import SuitBase
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.toonbase.ToontownBattleGlobals import *
from toontown.battle.SuitBattleGlobals import *
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import MovieUtil
from direct.task.Task import Task
from . import PlayByPlayText
from six.moves import range
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
            shotChoices = [avatarCloseUpThreeQuarterRightShotWide, allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
        else:
            shotChoices = [avatarCloseUpThreeQuarterRightShot, allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    elif numSounds >= 2 and numSounds <= 4:
        shotChoices = [allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of sounds: %s' % numSounds)
    track = random.choice(shotChoices)(*[av, duration])
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


def chooseSoundCloseShot(sounds, targets, openDuration, openName, attackDuration):
    numSuits = len(targets)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = targets[0]['suit']
        shotChoices = [avatarCloseUpThrowShot]
    elif numSuits >= 2 and numSuits <= 7:
        shotChoices = [allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    track = random.choice(shotChoices)(*[av, duration])
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
         avatarBehindShot]
    elif numThrows >= 2 and numThrows <= 4:
        shotChoices = [allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of throws: %s' % numThrows)
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseThrowCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration):
    numSuits = len(suitThrowsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[list(suitThrowsDict.keys())[0]]
        shotChoices = [avatarCloseUpThrowShot,
                       allGroupLowShot2, 
         avatarCloseUpThreeQuarterLeftShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= 7 or numSuits == 0:
        shotChoices = [allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    track = random.choice(shotChoices)(*[av, duration])
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
         avatarBehindShot]
    elif numSquirts >= 2 and numSquirts <= 4:
        shotChoices = [allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of squirts: %s' % numSquirts)
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseSquirtCloseShot(squirts, suitSquirtsDict, openDuration, openName, attackDuration):
    numSuits = len(suitSquirtsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[list(suitSquirtsDict.keys())[0]]
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterLeftShot]
    elif numSuits >= 2 and numSuits <= 7:
        shotChoices = [allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    track = random.choice(shotChoices)(*[av, duration])
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
    track = random.choice(shotChoices)(*[av, duration])
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
         allGroupLowShot2, 
         avatarBehindShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numDrops >= 2 and numDrops <= 4 or numDrops == 0:
        shotChoices = [allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of drops: %s' % numDrops)
    track = random.choice(shotChoices)(*[av, duration])
    return track


def chooseDropCloseShot(drops, suitDropsDict, openDuration, openName, attackDuration):
    numSuits = len(suitDropsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[list(suitDropsDict.keys())[0]]
        shotChoices = [avatarCloseUpThrowShot,
         avatarCloseUpThreeQuarterLeftShot,
         allGroupLowShot2, 
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= 7 or numSuits == 0:
        shotChoices = [allGroupLowShot2, suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    choice = random.choice(shotChoices)
    track = choice(av, duration)
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

    if name == 'AcidRain':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Audit':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'Bash':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.75, attackDuration=1.75), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(attackDuration - 3.75)))
    elif name == 'Beguile':
        camTrack.append(Sequence(motionShot(5, 12.5, 10, -210, -20.0, 0.0, 0, suit), Wait(2.1), defaultCamera(openShotDuration=0, attackDuration=attackDuration - 2.1)))
        #camTrack.append(defaultCamera(openShotDuration=2.1))
    elif name == 'CloseTheLoop':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'HostileTakeover':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'NickelAndDime':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Quash':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'PennyPinch':
        camTrack.append(allGroupLowShot(suit, attackDuration, battle))
    elif name == 'Disassemble':
        camTrack.append(defaultCamera(openShotDuration=1.75))
    elif name == 'DataCorruption':
        camTrack.append(defaultCamera(openShotDuration=1.75))
    elif name == 'DataBreach':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'VersionControl':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'DenialOfService':
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == 'Overload':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'Breakthrough':
        camTrack.append(defaultCamera(openShotDuration=3.5))
    elif name == 'Encrypt':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'BounceRate':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Reprogram':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'CloudStorage':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'DiskScratch':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'VoodooMagic':
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == 'ElectrostaticEnergy':
        camTrack.append(defaultCamera(openShotDuration=1.75))
    elif name == 'Bite':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'BounceCheck':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'BrainStorm':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'BuzzWord':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Calculate':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Canned':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'EvictionNotice':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Chomp':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Watercooler':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'CigarSmoke':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'SmokeAndMirrors':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'ClipOnTie':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Crunch':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Demotion':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'DoubleTalk':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Downsize':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'EvictionNotice':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'EvilEye':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'DoubleCross':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'Forecast':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'MysteriousDisappearance':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'GoldRush':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'GoldDust':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'FiveOClockShadow':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'SandTrap':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Filibuster':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'FillWithLead':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'FingerWag':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Fired':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'FountainPen':
        camTrack.append(defaultCamera(openShotDuration=1.75))
    elif name == 'FreezeAssets':
        camTrack.append(defaultCamera(openShotDuration=1.75))
    elif name == 'GlowerPower':
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == 'ReArrange':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'ShortSqueeze':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'BlueChip':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'FallingKnife':
        camTrack.append(Sequence(defaultCamera(attackDuration=3.0, openShotDuration=3.0), heldRelativeShot(target[0]['toon'], 2.5, 10, 1, 165, 25, 0, attackDuration - 3.0)))
    elif name == 'GuiltTrip':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Embezzle':
        camTrack.append(allGroupLowShot(suit, attackDuration, battle))
    elif name == 'FloodTheMarket':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'MoneyTrip':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HalfWindsor':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'HangUp':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'HeadShrink':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HotAir':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Jargon':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Legalese':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'LawBook':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Liquidate':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'MarketCrash':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'MumboJumbo':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ParadigmShift':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'PeckingOrder':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PickPocket':
        camTrack.append(allGroupLowShot(suit, attackDuration, battle))
    elif name == 'StolenScene':
        camTrack.append(allGroupLowShot(suit, attackDuration, battle))
    elif name == 'PinkSlip':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PlayHardball':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PoundKey':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PowerTie':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PowerTrip':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Quake':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'Aftershock':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5),
                                 Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'RazzleDazzle':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'RedTape':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'ReOrg':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'RestrainingOrder':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Rolodex':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'RubberStamp':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'RubOut':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Sacked':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Schmooze':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'TestSchmooze':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Shake':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5),
                                 Func(taskMgr.add, shake_camera_tremor, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'Inject':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Shred':
        camTrack.append(defaultCamera(openShotDuration=3.5))
    elif name == 'SongAndDance':
        camTrack.append(defaultCamera(openShotDuration=4.0))
    elif name == 'Spin':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Synergy':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Tabulate':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'Golf':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'ThrowBook':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Novel':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Newspaper':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Tremor':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5),
                                 Func(taskMgr.add, shake_camera_tremor, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'Withdrawal':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'WriteOff':
        camTrack.append(defaultCamera(openShotDuration=2.0))
        # redd heir wing cheats
    elif name == 'ReddLiquidationSale':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ReddPeckingOrder':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'ReddAutoRepair':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        # witness stand-in cheats
    elif name == 'WSIJuryNotice':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'WSICeaseAndDesist':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ArbitratorObjection':
        camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 2)))
    elif name == 'ArbitratorPaperFiling':
        camTrack.append(Sequence(defaultCamera(openShotDuration=2.5, attackDuration=2.5), motionShot(2.5, 10, 1, 165, 25, 0, 0, target[0]['toon']), Wait(attackDuration - 2.5)))
    elif name == 'ArbitratorWhirlwind':
        camTrack.append(Sequence(randomActorShot(suit, battle, 0.5, 'suit'), heldShot(20, 0, 20, 115, -30, 0, attackDuration - .5)))
    elif name == 'ArbitratorThrowBook':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.0),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 2.7)))
    elif name == 'ArbitratorThrowBook2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.7),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.2)))
    elif name == 'ArbitratorThrowBook3':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.7),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.2)))
    elif name == 'ArbitratorThrowBook4':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.7),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.2)))
    elif name == 'ArbitratorThrowBook5':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.7),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.2)))
        # litigator cheats
    elif name == 'LitigatorSnapSoak':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'LitigatorSnapBindings':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'LitigatorSnap':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'LitigatorSnapStenographer':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'LitigatorBayouBash':
        camTrack.append(Sequence(motionShot(.5, 9.0, suit.height - 1, 175, 0, 0.0, 0, suit), moveCameraOnly(-1.0, 9.0, suit.height - 1, 1, suit, h=190, p=0, startH=175, startP=0), Wait(attackDuration - 1)))
    elif name == 'LitigatorBayouBellow':
        camTrack.append(Sequence(cameraActorShot(suit, 'litigator-bellow', attackDuration)))
        # stenographer cheats
    elif name == 'StenographerSanctionBindings':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=0.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'StenographerSanctionSuppression':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=0.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'StenographerSanction':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'StenographerSanctionLitigator':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'StenographerCourtRecordBan':
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = suit.makePlayByPlayTextCourtRecordInterval(pbpDc, attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Court Record!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        # case manager cheats
    elif name == 'CaseManagerInsurancePlanScapegoat':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'CaseManagerInsurancePlanScapegoat2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'CaseManagerInsurancePlan':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'CaseManagerInsurancePlan2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'CaseManagerInsurance':
        camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'CaseManagerInsurance2':
        camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'CaseManagerLegalBindings':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'CaseManagerLegalBindings2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7), moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'CaseManagerLegallyBound':
        if attackDuration > 2:
            camTrack2 = randomActorShot(target[0]['toon'], battle, attackDuration, 'toon')
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('Legally Bound Toons take %s damage per round!' % attack['target'][0]['hp'], attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Legally Bound!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'CaseManagerCourtRecordBan':
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = suit.makePlayByPlayTextCourtRecordInterval(pbpDc, attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Court Record!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        # scapegoat cheats
    elif name == 'ScapegoatRageBuilding':
        camTrack2 = Sequence(Wait(attackDuration))
        return camTrack2
    elif name == 'ScapegoatShieldsUp':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ScapegoatEnraged':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 10, 8, -180, -20.0, 0.0, attackDuration)))
    elif name == 'ScapegoatGavel':
        camTrack.append(defaultCamera(openShotDuration=2))
    elif name == 'ScapegoatBarnyardBash':
        if attackDuration > 2:
            camTrack.append(randomActorShot(target[0]['toon'], battle, attackDuration, 'toon'))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'ScapegoatCourtRecordBan':
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
    elif name == 'PowerhouseAbsorb':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseSoakImmune':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseDropImmune':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseZapImmune':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseLureImmune':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseSyphon':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseSyphonDesperation':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'PowerhouseGroundbreaker':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'PowerhouseGroundbreakerRevert':
        if attackDuration > 2:
            camTrack.append(Parallel(heldShot(0.0, 0.0, 3.5, 180, -20, 0, attackDuration)))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'PowerhouseSnipeVulnerable':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseSnipeGagBan':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.75)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse  retaliates against toon who chose banned gags!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Power Surge!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.75)
            return camTrack2
    elif name == 'PowerhouseSnipeSoaked':
        camTrack.append(defaultCamera(openShotDuration=1.75))
    elif name == 'PowerhouseToleranceBuilding':
        camTrack2 = Sequence(Wait(attackDuration))
        return camTrack2
    elif name == 'PowerhouseSnipeBookkept':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.75)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse retaliates against toons who attacked the Bookkeeper while Bookkeeping!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Power Surge!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.75)
            return camTrack2
    elif name == 'PowerhouseSnipeMulligan':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseSnipeCollectCall':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 9, 10, -180, -20.0, 0.0, attackDuration)))
    elif name == 'PowerhouseGeneration':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 9, 10, -180, -20.0, 0.0, attackDuration)))
    elif name == 'PowerhouseGeneration2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 9, 10, -180, -20.0, 0.0, attackDuration)))
    elif name == 'PowerhouseBurnDamage':
        if attackDuration > 2:
            camTrack2 = Parallel(motionShot(2.5, 10, 1, 165, 25, 0, 0, target[0]['toon']), Wait(attackDuration))
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('Surged Toons take %s extra damage per round!' % attack['target'][0]['hp'], attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Short Circuit!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    # bookkeeper cheats
    elif name == 'BookkeeperPaperCutSoaked':
        camTrack.append(defaultCamera(openShotDuration=.5))
    elif name == 'BookkeeperPaperCutMarked':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BookkeeperPaperCut':
        camTrack.append(defaultCamera(openShotDuration=.5))
    elif name == 'BookkeeperExplodingDocument':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'BookkeeperMandatoryFiling':
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == 'BookkeeperBookkeepingRetaliation':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=3.0)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                "The Commissioner applies a gag damage debuff to all toons who attacked him!",
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Closed Session!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'BookkeeperBookkeeping':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    # wiretapper cheats
    elif name == 'WiretapperCollectCall':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'WiretapperCollectCall2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'WiretapperCollectCallDamage':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'WiretapperBusySignal':
        camTrack.append(Sequence(randomActorShot(target[0]['toon'], battle, 1.5, 'toon'), randomActorShot(suit, battle, 1.0, 'suit'), randomActorShot(target[0]['toon'], battle, attackDuration - 2.5, 'toon')))
    elif name == 'WiretapperGagBan':
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = suit.makePlayByPlayTextInflationInterval(pbpDc, attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Wire Cut!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'WiretapperWiretapped':
        camTrack.append(Sequence(defaultCamera(openShotDuration=2.0)))
    elif name == 'WiretapperVoicemail':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'WiretapperBrokenConnection':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    # ambassador cheats
    elif name == 'AmbassadorHeadRoller':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorHeadRoller2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorHeadRoller3':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorHeadRoller4':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorHeadRoller5':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorHeadRollerGroup':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'AmbassadorAdvancement':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 0),
                                 Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                 Func(taskMgr.remove, 'camera_shake'),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'AmbassadorAdvancement2':
        camTrack.append(defaultCamera(openShotDuration=.5))
    elif name == 'AmbassadorAdvancement3':
        camTrack.append(defaultCamera(openShotDuration=.5))
    elif name == 'AmbassadorAdvancement4':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'AmbassadorAdvancement5':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'AmbassadorRefinement':
        camTrack.append(Sequence(heldShot(0.0, -15.0, 10.0, 0, -20, 0, suit.getDuration('snap') + .5), cameraActorShot(suit, 'summon-cog', (attackDuration - (suit.getDuration('snap') + .5)))))
    elif name == 'AmbassadorRefinementManager':
        camTrack.append(Sequence(heldShot(0.0, -15.0, 10.0, 0, -20, 0, suit.getDuration('snap') + .5), cameraActorShot(suit, 'summon-cog', (attackDuration - (suit.getDuration('snap') + .5)))))
    elif name == 'AmbassadorGhostMentality':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'AmbassadorPhase2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorDamageUp':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorManagerialProtection':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'AmbassadorManagerialProtectionImmunity':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'AmbassadorMulligan':
        camTrack.append(Sequence(defaultCamera(openShotDuration=2, attackDuration=2.0), heldShot(0, -60, 20, 0, -20, 0, attackDuration - 2)))
    # safety supervisor cheats
    elif name == 'SafetyOverpressured':
        target = attack['target']
        targetSuit = target[0]['suit']
        camTrack2 = Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 moveShot(0.0, -20.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 6.5))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('The Pressurizer pushes the %s to their limit!' % (targetSuit.name), attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Overpressured!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'SafetyOverpressured2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 moveShot(0.0, -20.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 6.5)))
    elif name == 'SafetyOverpressured3':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 moveShot(0.0, -20.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 6.5)))
    elif name == 'SafetyOverpressured4':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 moveShot(0.0, -20.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 6.5)))
    elif name == 'SafetyOverpressured5':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 moveShot(0.0, -20.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 6.5)))
    elif name == 'SafetyHighPressure':
        camTrack.append(Sequence(defaultCamera(openShotDuration=4, attackDuration=4), moveShot(0.0, -20.0, 10.0, 0, -20, 0, 0),
                                 Func(taskMgr.add, shake_camera_high_pressure, 'camera_shake'), Wait(3.0),
                                 Func(taskMgr.remove, 'camera_shake'),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 7)))
    elif name == 'SafetyHeatWave':
        camTrack.append(Sequence(motionShot(4.0, -10.0, suit.height + 5, 30, -30.0, 0.0, 0, suit), moveCameraOnly(-4, -10.0, suit.height + 5, suit.getDuration('magic3-alt'), suit, h=-30, p=-30, startH=30, startP=-30), motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration - suit.getDuration('magic3-alt'))))
    elif name == 'SafetyHeatWaveCalculation':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 5.0, 180, 30.0, 0.0, 0, suit), moveCameraOnly(0.0, 9.0, suit.height + 5, attackDuration - 2, suit, h=180, p=-30), Wait(2)))
    elif name == 'SafetyOverpressureDeath':
        camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'SafetyViolation':
        if attackDuration > 2:
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 defaultCamera(openShotDuration=0, attackDuration=attackDuration-5)))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'SafetyPromotion':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'SafetyPromotion2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=2.0)))
    elif name == 'SafetyPromotion3':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'SafetyPromotion4':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'SafetyPromotion5':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'SafetySoakRetaliation':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 defaultCamera(openShotDuration=0, attackDuration=attackDuration-5)))
        # hustler cheats
    elif name == 'HustlerLimitedTimeOfferApprove':
        if attackDuration > 2:
            camTrack.append(heldShot(10, 0, 10, 115, -30, 0, attackDuration))
        else:
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
    elif name == 'HustlerLimitedTimeOfferDenied':
        if attackDuration > 2:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        else:
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
    elif name == 'HustlerSalesPitch':
        camTrack.append(Sequence(defaultCamera(openShotDuration=3, attackDuration=3), motionShot(2.5, 10, 1, 165, 25, 0, 0, target[0]['toon']), Wait(attackDuration - 3)))
    elif name == 'HustlerClosingTime':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      heldRelativeShot(suit, 0.0, 7.8096, 9, -180, -10.0, 0.0, attackDuration)))
    elif name == 'HustlerBaitAndSwitch':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'HustlerCustomerRetention':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        #camTrack.append(Sequence(heldShot(0, 15, 20, -180, -20, 0, attackDuration)))
    elif name == 'HustlerExclusiveOfferRetaliation':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HustlerExclusiveOffer':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'HustlerHalfWindsor':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    # traffic manager cheats
    elif name == 'TrafficDetour':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'TrafficCongestionPricing':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'TrafficRedLight':
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
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('The %s now has the %s and must not be targeted!' % (targetSuit.name, redLight), attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Red Light!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'TrafficTrafficViolation':
        if attackDuration > 2:
            camTrack.append(Sequence(motionShot(2.0, -2.0, suit.height, 0, -20.0, 0.0, 0, suit), Wait(attackDuration - 0)))
        else:
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
    elif name == 'TrafficRedLightRetaliation':
        if attackDuration > 2:
            camTrack.append(Sequence(motionShot(2.0, -2.0, suit.height, 0, -20.0, 0.0, 0, suit), Wait(attackDuration - 0)))
        else:
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
    elif name == 'TrafficGreenLight':
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
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('The %s now has the %s and must be targeted!' % (targetSuit.name, greenLight), attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Green Light!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'TrafficYellowLight':
        tpMgr = TextPropertiesManager.getGlobalPtr()

        def addTextColor(name, r, g, b):
            prop = TextProperties()
            prop.setTextColor(r, g, b, 1)
            tpMgr.setProperties(name, prop)

        addTextColor('yellowLight', 0.973, 1, 0)
        yellowLight = '\1yellowLight\1Yellow Light\2'
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Everyone has been given the %s and will deal less damage this round!' % (yellowLight), attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Yellow Light!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'TrafficGreenLightRetaliation':
        if attackDuration > 2:
            camTrack.append(Sequence(motionShot(2.0, -2.0, suit.height, 0, -20.0, 0.0, 0, suit), Wait(attackDuration - 0)))
        else:
            camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
            return camTrack2
    elif name == 'TrafficYield':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    # union buster cheats
    elif name == 'UnionBusterCompensationClaims':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'UnionBusterContractEnforcementHealing':
        camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'UnionBusterUnionDues':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'UnionBusterNoStrikeClause':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'UnionBusterUnionCalculator':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'UnionBusterUnionBust':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'UnionBusterUnionBuster':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'UnionBusterUnionBusterDamage':
        if attackDuration > 2:
            camTrack2 = randomActorShot(target[0]['toon'], battle, attackDuration, 'toon')
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('Employed Toons will %s more damage per round!' % attack['target'][0]['hp'], attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('At-Will Employment!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'UnionBusterUnionWages':
        camTrack.append(Sequence(motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), moveCameraOnly(-4.0, 9.0, suit.height - 1, attackDuration - 3, suit, h=210, p=0, startH=150, startP=0), Wait(3)))
    elif name == 'UnionBusterUnionWages2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'UnionBusterUnionWages3':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'UnionBusterUnionWages4':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'UnionBusterUnionWages5':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'UnionBusterBreachOfContract':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'UnionBusterBreachOfContract2':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'UnionBusterBreachOfContract3':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'UnionBusterBreachOfContract4':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'UnionBusterContractEnforcement':
        camTrack.append(defaultCamera(openShotDuration=6.75))
    elif name == 'UnionBusterContractEnforcement2':
        camTrack.append(defaultCamera(openShotDuration=1.5))
        # racketeer
    elif name == 'RacketeerOverextendedLeverage2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'RacketeerOverextendedLeverage':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'RacketeerProfiteering':
        camTrack.append(Sequence(motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(3.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 5.2)))
    elif name == 'RacketeerProfiteering2':
        camTrack.append(Parallel(cameraActorShot(suit, 'summon-cog', attackDuration), Wait(attackDuration)))
    elif name == 'RacketeerProfiteering3':
        camTrack.append(Parallel(cameraActorShot(suit, 'summon-cog', attackDuration), Wait(attackDuration)))
    elif name == 'RacketeerProfiteering4':
        camTrack.append(Parallel(cameraActorShot(suit, 'summon-cog', attackDuration), Wait(attackDuration)))
    elif name == 'RacketeerProfiteering5':
        camTrack.append(Parallel(cameraActorShot(suit, 'summon-cog', attackDuration), Wait(attackDuration)))
    elif name == 'RacketeerExtortion':
        camTrack.append(Parallel(cameraActorShot(suit, 'sacrifice-cog', attackDuration), Wait(attackDuration)))
    elif name == 'RacketeerExtortion2':
        camTrack.append(Sequence(heldShot(10, 0, 10, 115, -30, 0, 1.0), Parallel(Wait(attackDuration - 1), cameraActorShot(suit, 'summon-cog', attackDuration - 1))))
    elif name == 'RacketeerCompensation':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'RacketeerHustling':
        camTrack2 = defaultCamera(openShotDuration=0)
        return camTrack2
    elif name == 'RacketeerRacketeering':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'RacketeerPeckingOrderRetaliation':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=1.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'RacketeerPeckingOrderRetaliationSoak':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 9, 6, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 defaultCamera(openShotDuration=0, attackDuration=attackDuration-5)))
        # radiographer
    elif name == 'RadiographerRadioInfrequency':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'RadiographerHotTake':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'RadiographerHotTakeDamage':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=0))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'RadiographerHotTakeRetaliation':
        camTrack.append(defaultCamera(openShotDuration=6.75))
    elif name == 'RadiographerOvermodulated':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'RadiographerOvermodulated2':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'RadiographerOvermodulated3':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'RadiographerOvermodulated4':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'RadiographerOvermodulated5':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'RadiographerDanceSession': # Target Check
        camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
        #derrick man
    elif name == 'DerrickManRefinement':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 5.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -20.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
        #dola
    elif name == 'DOLAInkDrain':
        camTrack.append(defaultCamera(openShotDuration=1.0))
        #dopr
    elif name == 'DOPRAmbushMarketing':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        #dividend king
    elif name == 'DividendZapRetaliation':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'DividendAccountRollover':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'DividendAccountRollover2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'DividendAccountRollover3':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'DividendAccountRollover4':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'DividendAccountRollover5':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'DividendLiquidationEvent':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'DividendLiquidationEventDamage':
        if attackDuration > 2:
            camTrack2 = randomActorShot(target[0]['toon'], battle, attackDuration, 'toon')
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('Liquidated Toons take %s damage per round!' % attack['target'][0]['hp'], attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Liquidation Event!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'DividendTotalMarketMeltdown':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'DividendTotalMarketMeltdown2':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'DividendTotalMarketMeltdownDamage':
        camTrack2 = heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration)
        return camTrack2
    elif name == 'DividendPeckingOrder':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'DividendPeckingOrderZapped':
        camTrack.append(allGroupLowShot(suit, attackDuration, battle))
        # ottoman cheats
    elif name == 'OttomanRevisedDraft':
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == 'OttomanRedPenReview':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'OttomanFootnoteOverload':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'OttomanPerformanceReview':
        camTrack.append(heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'OttomanPerformanceReviewRevert':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
        # crystalline cheats
    elif name == 'CrystalShatteringClarity':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'CrystalRefractDamage':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'CrystalRefractDamageRetaliation':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'CrystalFracturedLimitsOffensive':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'CrystalFracturedLimitsDefensive':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'CrystalFracturedLimitsRetaliation':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'CrystalPrismaticDistortion':
        camTrack.append(defaultCamera(openShotDuration=0.5))
        # chairman cheats
    elif name == 'ChairmanTrapRetaliation':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ChairmanLureRetaliation':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'ChairmanThrowRetaliation':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ChairmanSquirtRetaliation':
        camTrack.append(Sequence(defaultCamera(openShotDuration=2, attackDuration=2),
                                 heldShot(5, 0, .5, 155, 35, 0, attackDuration - 2)))
    elif name == 'ChairmanZapRetaliation':
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == 'ChairmanSoundRetaliation':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 15, 5, -180, 0.0, 0.0, 0, suit), Wait(4)))
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=attackDuration - 4)))
    elif name == 'ChairmanDropRetaliation':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ChairmanCage':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'ChairmanPhase2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ChairmanOvertime':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanOvertime2':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanOvertime3':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanOvertime4':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanOvertime5':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanHostileLiquidation':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanHostileLiquidation2':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanHostileLiquidation3':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanHostileLiquidation4':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanHostileLiquidation5':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    elif name == 'ChairmanSnipe':
        camTrack.append(defaultCamera(openShotDuration=1.5))
        # liquidator cheats
    elif name == 'LiquidatorOilRain':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, attackDuration)))
    elif name == 'LiquidatorOilRainDamage':
        camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'LiquidatorFreezingRain':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, attackDuration)))
    elif name == 'LiquidatorHeavyRain':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, attackDuration)))
    elif name == 'LiquidatorHeavyRainDamage':
        camTrack2 = heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration)
        return camTrack2
    elif name == 'LiquidatorStormCell':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, attackDuration)))
    elif name == 'LiquidatorStormCellDamage':
        camTrack2 = defaultCamera(openShotDuration=1.0)
        return camTrack2
    elif name == 'LiquidatorInversion':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 10.8096, 8, -180, -10.0, 0.0, attackDuration)))
    elif name == 'LiquidatorMonsoon':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 10.8096, 10, -180, -10.0, 0.0, attackDuration)))
    elif name == 'LiquidatorTornado':
        camTrack.append(Sequence(randomActorShot(suit, battle, 0.5, 'suit'), heldShot(20, 0, 20, 115, -30, 0, attackDuration - .5)))
        # tollmaster
    elif name == 'TollmasterMandatoryToll':
        camTrack.append(Sequence(motionShot(0, -6, suit.height + 2, 0, 0, 0.0, 0, suit), moveCameraOnly(2, -1, suit.height, attackDuration - 2, suit, h=0, p=-10, startH=0, startP=0), Wait(2)))
        #camTrack.append(Sequence(motionShot(0.0, 10.0, 5.0, -180, 30.0, 0.0, 0, suit), motionShot(2.0, -2.0, suit.height, 0, -20.0, 0.0, 2, suit), Wait(attackDuration - 2)))
    elif name == 'TollmasterMandatoryTollFinal':
        camTrack.append(Sequence(randomActorShot(suit, battle, 6.5, 'suit'), 
                                 heldShot(0, 15, 20, -180, -20, 0, attackDuration - 6.5)))
    elif name == 'TollmasterRushHour':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'TollmasterResonanceTax':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'TollmasterResonanceTax2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'TollmasterResonanceTax3':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'TollmasterResonanceTax4':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'TollmasterResonanceTax5':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'TollmasterMissedPayment':
        if attackDuration > 2:
            camTrack.append(allGroupLowShot(suit, attackDuration, battle))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'TollmasterLedgerOfSound':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5)))
    elif name == 'TollmasterBalanceTheLedger':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 0),
                                 Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                 Func(taskMgr.remove, 'camera_shake'),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'TollmasterBalanceTheLedger2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 0),
                                 Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                 Func(taskMgr.remove, 'camera_shake'),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'TollmasterBalanceTheLedger3':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 0),
                                 Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                 Func(taskMgr.remove, 'camera_shake'),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'TollmasterBalanceTheLedger4':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 0),
                                 Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                 Func(taskMgr.remove, 'camera_shake'),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'TollmasterBalanceTheLedger5':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 0),
                                 Func(taskMgr.add, shake_camera_advancement, 'camera_shake'), Wait(0.5),
                                 Func(taskMgr.remove, 'camera_shake'),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
        # record keeper
    elif name == 'RecordkeeperMinutesTaken':
        camTrack.append(Sequence(randomActorShot(suit, battle, 2.0, 'suit'), heldShot(0, 15, 20, -180, -20, 0, attackDuration - 2)))
    elif name == 'RecordkeeperMinutesTakenContingency':
        camTrack.append(Sequence(randomActorShot(suit, battle, 2.0, 'suit'), heldShot(0, 15, 20, -180, -20, 0, attackDuration - 2)))
    elif name == 'RecordkeeperMinutesTakenDamage':
        camTrack.append(heldShot(0, 15, 20, -180, -20, 0, attackDuration))
    elif name == 'RecordkeeperPaperTrail':
        camTrack.append(defaultCamera(openShotDuration=6.75))
    elif name == 'RecordkeeperRevisedFiling':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.0, 'suit'), heldShot(0, 15, 20, -180, -20, 0, attackDuration - 1)))
    elif name == 'RecordkeeperRevisedFilingLiquidation':
        camTrack.append(defaultCamera(openShotDuration=6.75))
    elif name == 'RecordkeeperRedlinedClause':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'RecordkeeperRedlinedClauseMissedPayment':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'RecordkeeperAuditCycle':
        camTrack.append(Sequence(motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), moveCameraOnly(-4.0, 9.0, suit.height - 1, attackDuration - 3, suit, h=210, p=0, startH=150, startP=0), Wait(3)))
    elif name == 'RecordkeeperPhantomEntryDamage':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration)))
    elif name == 'RecordkeeperPhantomEntrySpawn':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 5.0, 180, 30.0, 0.0, 0, suit), moveCameraOnly(0.0, 9.0, suit.height + 5, attackDuration - 2, suit, h=180, p=-30), Wait(2)))
    elif name == 'RecordkeeperPhantomEntrySacrifice':
        camTrack.append(Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)))
        # corporate butcherer
    elif name == 'ButcherOverride':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 10.0, 10.0, -180, -10.0, 0.0, attackDuration)))
    elif name == 'ButcherOverrideRemoval':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 10.0, 10.0, -180, -10.0, 0.0, attackDuration)))
    elif name == 'ButcherRevvingUp':
        camTrack2 = Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 10.0, 10.0, -180, -10.0, 0.0, attackDuration))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('The Corporate Butcherer gains %s,000 RPM!' % target[0]['hp'], attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Revving Up!', attackDuration - 2)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'ButcherRevvingUpWhipsaw':
        camTrack2 = Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 10.0, 10.0, -180, -10.0, 0.0, attackDuration))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('The Corporate Butcherer gains %s,000 RPM! (Whipsaw: +4,000 RPM)' % (target[0]['hp'] - 4), attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Revving Up!', attackDuration - 2)
        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'ButcherKickback':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ButcherMarkedWood':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), defaultCamera(openShotDuration=1.5, attackDuration=attackDuration - 2)))
    elif name == 'ButcherOffboarding':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), randomActorShot(suit, battle, 1, 'suit'), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3)))
    elif name == 'ButcherOffboarding2':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), randomActorShot(suit, battle, 1, 'suit'), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3)))
    elif name == 'ButcherOffboarding3':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), randomActorShot(suit, battle, 1, 'suit'), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3)))
    elif name == 'ButcherOffboarding4':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), randomActorShot(suit, battle, 1, 'suit'), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3)))
    elif name == 'ButcherOffboarding5':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), randomActorShot(suit, battle, 1, 'suit'), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3)))
    elif name == 'ButcherAggrandize':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'ButcherAggrandize2':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'ButcherAggrandize3':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'ButcherAggrandize4':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'ButcherAggrandize5':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'ButcherSparkPlug':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldRelativeShot(suit, 0.0, 8.8096, 8, -180, -10.0, 0.0, 3.0), defaultCamera(openShotDuration=0, attackDuration=attackDuration - 5)))
    elif name == 'ButcherSparkPlugDamage':
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('Zapped Toons take extra damage per round!', attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Spark Plug!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'ButcherScabbard':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'ButcherLayoffs':
        camTrack.append(Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, 3.875), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3.875)))
        # contingency director
    elif name == 'ContingencyOverrideRevert':
        camTrack2 = Sequence(randomActorShot(suit, battle, attackDuration, 'suit'))
        return camTrack2
    elif name == 'ContingencyOverride':
        camTrack2 = Sequence(randomActorShot(suit, battle, attackDuration, 'suit'))
        return camTrack2
    elif name == 'ContingencySelfRepair':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      heldRelativeShot(suit, 0.0, 7.8096, 9, -180, -10.0, 0.0, attackDuration)))
    elif name == 'ContingencyFailsafeProtocol':
        camTrack.append(allGroupHighShot(suit, attackDuration))
    elif name == 'ContingencyRiskThresholdBreach':
        dmg = attack['target'][0]['hp']
        if dmg > 1:
            banDesc = 'The Contingency Director has gained %s new abilities!' % dmg
        else:
            banDesc = 'The Contingency Director has gained 1 new ability!'

        camTrack2 = Sequence(motionShot(6.0, 7.0, suit.height, 225, -10, 0.0, 0, suit), moveCameraOnly(-6.0, 7.0, suit.height, attackDuration - 2, suit, h=225, p=-10, startH=135, startP=-20), Wait(2))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(banDesc, attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Risk Threshold Breach!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'ContingencyRiskThresholdBreach75':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ContingencyMarkLiquidated':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ContingencyRiskThresholdBreach50':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ContingencyMarkRevisedFiling':
        camTrack2 = defaultCamera(openShotDuration=0)
        return camTrack2
    elif name == 'ContingencyRiskThresholdBreach25':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=0.75)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('The Contingency Director retaliates against marked Toons!', attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Targeted Neutralization!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'ContingencyContingencyClause':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ContingencyContingencyClauseRetaliation':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=3), defaultCamera(openShotDuration=1.5, attackDuration=attackDuration-3)))
    elif name == 'ContingencyRedundantAuthority':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'ContingencyOperationalFreeze':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'ContingencyForecastCollapse':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        #cashbot litigation
    elif name == 'PayrollPayrollProcessing':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 4.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'PayrollPerformanceBonus':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 4.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'ErclaimLaffSteal':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'ErclaimRiseFromTheScrap':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ErclaimScopeCreep':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ErclaimPhase2':
        camTrack2 = Sequence()
        return camTrack2
    elif name == 'ErclaimSacrifice':
        camTrack.append(Sequence(heldShot(20, -10, 15, 50, -30, 0, 1.5), Func(taskMgr.add, shake_camera_sacrifice, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErclaimSacrifice2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErclaimSacrifice3':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErclaimSacrifice4':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErclaimSacrifice5':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErfitHydrationCheck':
        if attack['target'][0]['hp'] > 0:
            camTrack.append(Sequence(defaultCamera(openShotDuration=2.0, attackDuration=2), heldShot(0, 15, 20, -180, -20, 0, attackDuration - 2)))
        else:
            camTrack.append(Sequence(defaultCamera(openShotDuration=2.0)))
    elif name == 'ErfitWringOut':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'ErfitHydrationCheckRevert':
        if attackDuration > 2:
            camTrack2 = Parallel(heldShot(0.0, 0.0, 3.5, 180, -20, 0, attackDuration))
            return camTrack2
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'ErclaimHemmorage':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'ErfitProToonShake':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'ErclaimHemmorageHealing':
        camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'ErfitGainsFromTheScrap':
        camTrack.append(Parallel(cameraActorShot(suit, 'sacrifice-cog', attackDuration), Wait(attackDuration)))
    elif name == 'ErfitGainsFromTheScrap2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErfitGainsFromTheScrap3':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErfitGainsFromTheScrap4':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErfitGainsFromTheScrap5':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=1.5), Func(taskMgr.add, shake_camera, 'camera_shake'), Wait(attackDuration - 2.0),
                                 Func(taskMgr.remove, 'camera_shake'), Wait(0.5)))
    elif name == 'ErfitPersonalTrainer':
        camTrack.append(Parallel(cameraActorShot(suit, 'summon-cog', attackDuration), Wait(attackDuration)))
    elif name == 'ErfitPhase2':
        camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    #high roller phase 1 cheats
    elif name == 'HighRollerNoAttack':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        return camTrack2
    elif name == 'HighRollerWheelSpin':
        camTrack.append(Sequence(motionShot(0.0, 5, 8, -180, 0.0, 0.0, 0, suit), Wait(3.5),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 motionShot(0.0, 8, 8, -180, 0.0, 0.0, 0, suit), Wait(attackDuration - 5.75)))
    elif name == 'HighRollerGameOver':
        camTrack.append(Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, 4 + suit.getDuration('snap')), motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, .5, suit), Wait(1.0),
                                 defaultCamera(openShotDuration=0, attackDuration=attackDuration - (5.5 + suit.getDuration('snap')))))
    elif name == 'HighRollerGameOver2':
        camTrack.append(Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, 4 + suit.getDuration('snap')), motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, .5, suit), Wait(1.0),
                                 defaultCamera(openShotDuration=0, attackDuration=attackDuration - (5.5 + suit.getDuration('snap')))))
    elif name == 'HighRollerPuzzle':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'HighRollerPuzzleBan':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'HighRollerCommercialBreak':
        camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'HighRollerGameTimeSpawn':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      heldRelativeShot(suit, 0.0, 7.8096, 9, -180, -10.0, 0.0, attackDuration)))
    elif name == 'HighRollerGameTimeCog':
        dmg = attack['target'][0]['hp']
        targetSuit = battle.activeSuits[dmg]
        banDesc = 'The High Roller asks the %s to participate in his game show!' % (targetSuit.name)

        camTrack2 = Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.0),
                                 motionShot(0.0, 9.0, targetSuit.height + 5, -180, -30.0, 0.0, 0, targetSuit), Wait(3.0), heldShot(0.0, -20.0, 12.0, 0, -10, 0, 7.5), Wait(3.5), 
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, .5, suit), Wait(.5), motionShot(0.0, 9.0, targetSuit.height + 5, -180, -30.0, 0.0, 0, targetSuit), Wait(attackDuration - 16))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(banDesc, attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Trivia!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'HighRollerGameTimeCog2':
        dmg = attack['target'][0]['hp']
        targetSuit = battle.activeSuits[dmg]
        banDesc = 'The High Roller asks the %s to participate in his game show!' % (targetSuit.name)

        camTrack2 = Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.0),
                                 motionShot(0.0, 9.0, targetSuit.height + 5, -180, -30.0, 0.0, 0, targetSuit), Wait(3.0), heldShot(0.0, -20.0, 12.0, 0, -10, 0, 7.5), Wait(3.5), 
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, .5, suit), Wait(.5), motionShot(0.0, 9.0, targetSuit.height + 5, -180, -30.0, 0.0, 0, targetSuit), Wait(attackDuration - 16))
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(banDesc, attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Trivia!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'HighRollerGameTimeCog3':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'HighRollerGameTimeCog4':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'HighRollerGameTimeCog5':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'HighRollerGameTimeCog6':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'HighRollerGameTimeCog7':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'HighRollerGameTimeCog8':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'HighRollerGameTimeCog9':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'HighRollerGameTimeCog10':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'HighRollerBust':
        if attackDuration > 2:
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(5.0),
                                 moveShot(0.0, -20.0, 10.0, 0, -20, 0, 0.5),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 5.5)))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    # high roller phase 2 cheats
    elif name == 'HighRollerPhase3':
        camTrack2 = Sequence(heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration))
        return camTrack2
    # high roller phase 3 cheats
    elif name == 'HighRollerPhase2':
        camTrack2 = Sequence(motionShot(0.0, 8.8096, 9.77317, -180, 0.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'HighRollerFreeCruise':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.7))
        camTrack.append(moveShot(-21.0, 8.0, 8.0, -120, 0, 0, 0.5))
        camTrack.append(heldShot(-21.0, 8.0, 8.0, -120, 0, 0, attackDuration - 4.2))
    elif name == 'HighRollerConduction':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'HighRollerRolled':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HighRollerRaisingTheAnte':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.7))
        camTrack.append(moveShot(-21.0, 8.0, 8.0, -120, 0, 0, 0.5))
        camTrack.append(heldShot(-21.0, 8.0, 8.0, -120, 0, 0, attackDuration - 4.2))
    elif name == 'HighRollerDiceRouletteCogs':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.25, 'suit'),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == 'HighRollerDiceRouletteToons':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.25, 'suit'),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == 'HighRollerDiceRouletteEveryone':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.25, 'suit'),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == 'HighRollerDiceRouletteNobody':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.25, 'suit'),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == 'HighRollerVulnerable':
        camTrack2 = defaultCamera(openShotDuration=0)
        return camTrack2
    elif name == 'HighRollerTrickOfTheLight':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'HighRollerAceInTheHole':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0.7, suit), Wait(3.0),
                                 moveShot(0, 15, 20, -180, -20, 0, 1.0),
                                 heldShot(0, 15, 20, -180, -20, 0, attackDuration - 4.7)))
    # high roller silhouette cheats
    elif name == 'HighRollerDonation':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'), heldShot(0.0, -20.0, 10.0, 0, -20, 0, 3.875), randomActorShot(suit, battle, attackDuration - 5.375, 'suit')))
    elif name == 'HighRollerSyphon':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0.5, attackDuration=2.0), randomActorShot(suit, battle, attackDuration - 2, 'suit')))
    elif name == 'HighRollerBar':
        camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
    elif name == 'HighRollerBar2':
        camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
    elif name == 'HighRollerLureResistance':
        camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
    elif name == 'HighRollerLureResistance2':
        camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
    elif name == 'HighRollerSingingBlues':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 15, 5, -180, 0.0, 0.0, 0, suit), Wait(attackDuration)))
    elif name == 'HighRollerDamageReduction':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HighRollerSplashback':
        if attackDuration > 1:
            camTrack.append(Sequence(defaultCamera(openShotDuration=3, attackDuration=3), motionShot(2.5, 10, 1, 165, 25, 0, 0, target[0]['toon']), Wait(attackDuration - 3)))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'HighRollerCheerRetaliation':
        if attackDuration > 1:
            camTrack.append(defaultCamera(openShotDuration=1.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        #videographer cheats
    elif name == 'VideographerStarOfTheShow':
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
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('The Videographer has made the %s the star of the show!' % (targetSuit.name), attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Star Of The Show!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'VideographerHardCut':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'VideographerRisingStars':
        camTrack.append(Sequence(motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), moveCameraOnly(-4.0, 9.0, suit.height - 1, attackDuration, suit, h=210, p=0, startH=150, startP=0)))
    elif name == 'VideographerRisingStars2':
        camTrack.append(Sequence(motionShot(4.0, 9.0, suit.height - 1, 150, 0, 0.0, 0, suit), moveCameraOnly(-4.0, 9.0, suit.height - 1, attackDuration, suit, h=210, p=0, startH=150, startP=0)))
    elif name == 'VideographerRisingStarsSacrifice':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'VideographerRisingStarsSilhouette':
        camTrack.append(Sequence(motionShot(0.0, 10.8096, 10.77317, -180, 0.0, 0.0, 0, suit), Wait(attackDuration)))
    elif name == 'VideographerVideoStatic':
        camTrack.append(heldShot(0.0, -15.0, 12.5, 0, -20, 0, attackDuration))
    elif name == 'VideographerElectricShock':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'VideographerElectricShock2':
        camTrack.append(Sequence(motionShot(0.0, 12.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration)))
    elif name == 'VideographerElectricShock3':
        camTrack.append(Sequence(motionShot(0, -6, suit.height + 2, 0, 0, 0.0, 0, suit), moveCameraOnly(-2, -1, suit.height, attackDuration - 2, suit, h=0, p=-10, startH=0, startP=0), Wait(2)))
    elif name == 'VideographerElectricShock4':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'VideographerDeath':
        camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'VideographerAttackRewind':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'VideographerDirectorCuts':
        camTrack2 = Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, 5), motionShot(6.0, 12.0, suit.height - 1, 150, 0, 0.0, 0, suit), 
                             moveCameraOnly(-6.0, 12.0, suit.height - 1, suit.getDuration('finger-wag') + suit.getDuration('frustrated') + 4, suit, h=210, p=0, startH=150, startP=0), 
                             motionShot(0, -50.0, suit.height - 1, 0, 0, 0.0, 0, suit), 
                             moveCameraOnly(0, -15.0, suit.height - 1, 2 + suit.getDuration('finger-wag') + suit.getDuration('summon') + 4, suit, h=0, p=0, startH=0, startP=0),
                             motionShot(0, 15.0, suit.height, 180, 0, 0.0, 0, suit), 
                             moveCameraOnly(0, 10.0, suit.height, attackDuration - (2 + 5 + suit.getDuration('finger-wag') + suit.getDuration('summon') + 4 + suit.getDuration('finger-wag') + suit.getDuration('frustrated') + 4), suit, h=180, p=0, startH=180, startP=0))
        return camTrack2
        # broadcaster cheats
    elif name == 'BroadcasterDonation':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'BroadcasterDonation2':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'BroadcasterViralSensation':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    #filmmaker cheats
    elif name == 'ChoreoChoreography':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'FilmmakerCameraFlash':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'FilmmakerCameraRewind':
        camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == 'FilmmakerBudgetCuts':
        camTrack2 = defaultCamera(openShotDuration=0)
        return camTrack2
    #director cheats
    elif name == 'DirectorActionCog':
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
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('The Director requires all Toons to attack the %s!' % (targetSuit.name), attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Action!', attackDuration - 2)

        return Parallel(pbpTrack, pbpDesc, camTrack2)
    elif name == 'DirectorActionRetaliation':
        camTrack.append(defaultCamera(openShotDuration=3.55))
    elif name == 'DirectorActionPartner':
        camTrack.append(Sequence(defaultCamera(openShotDuration=2.0, attackDuration=2), heldShot(0.0, 0.0, 3.5, 180, -20, 0, attackDuration - 2)))
    elif name == 'DirectorCut':
        camTrack.append(defaultCamera(openShotDuration=3.55))
    elif name == 'DirectorAction':
        camTrack.append(Sequence(motionShot(0.0, 12.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration)))
    elif name == 'DirectorActionRetaliation':
        camTrack.append(defaultCamera(openShotDuration=3.55))
    elif name == 'DirectorBackToOnes':
        camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
    elif name == 'DirectorProductionBudget':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'DirectorBudgetExpansion':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    #face the family
    elif name == 'ForemanSnipe':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=1.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'ForemanRedTape':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'ForemanContractor':
        camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(3), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 3))
        return camTrack2
    elif name == 'ForemanContributing':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ForemanUnionized':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'ForemanContractorDeath':
        camTrack2 = Sequence(Wait(attackDuration))
        return camTrack2
    elif name == 'ForemanBurning':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ForemanExtortion':
        camTrack.append(Parallel(cameraActorShot(suit, 'sacrifice-cog', attackDuration), Wait(attackDuration)))
    elif name == 'ForemanPolish':
        camTrack.append(Sequence(heldShot(0.0, -15.0, 10.0, 0, -20, 0, suit.getDuration('snap') + .5), cameraActorShot(suit, 'summon-cog', (attackDuration - (suit.getDuration('snap') + .5)))))
    elif name == 'ForemanBurningDamage':
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc("Smoked Toons take damage every round!", attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Smoked!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'ForemanSleepyOvercharge':
        camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'ForemanExplosion':
        camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'ForemanCompensation':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ForemanCompensation2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ForemanCompensation3':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ForemanCompensation4':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ForemanCompensation5':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintUsury':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(1.0),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.0),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 2)))
    elif name == 'MintLureResistance':
        camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
    elif name == 'MintLureResistance2':
        camTrack.append(heldShot(20.0, -20.0, 10.0, 45, -20, 0, attackDuration))
    elif name == 'MintMovingGoalposts':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'MintAudit':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintLedger':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=suit.getDuration('glower')), randomActorShot(suit, battle, attackDuration - suit.getDuration('glower'), 'suit')))
    elif name == 'MintHurrySickness':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.5)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc("The Mint Supervisor punishes Toons who chose banned gags!", attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Hurry Sickness!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'MintLifeInsurance':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration)))
    elif name == 'MintPolicyTerminated':
        camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'MintFraudulentDamage':
        camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'MintCompoundingInterest':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'MintAbacusAbove15':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintAbacusBelow15':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintAccountant1':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintAccountant2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintAccountant3':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintAccountant4':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintAccountant5':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'MintApprove':
        camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'MintDisapprove':
        camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'MintSynergy':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'MintScheming':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'WhistleCompensation':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'AttorneyObjection':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AttorneyDrainingPower':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AttorneyShakedownVulnerable':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'AttorneyShakedownCooldown':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'AttorneyInkDrain':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'AttorneyDizzy':
        camTrack.append(Sequence(randomActorShot(suit, battle, 0.5, 'suit'), heldShot(20, 0, 20, 115, -30, 0, attackDuration - .5)))
    elif name == 'AttorneyRemand':
        camTrack.append(Sequence(motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(3.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 5.2)))
    elif name in (
        'AttorneyOverseer',
        'AttorneyOverseerDrop',
        'AttorneyOverseerSquirt',
        'AttorneyOverseerThrow'
        ):
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'AttorneyObjectionSustained':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'AttorneyObjectionOverruled':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AttorneyChrono':
        camTrack.append(Sequence(motionShot(0, 15, suit.height - 2.5, 180, 0, 0.0, 0, suit), 
                             moveCameraOnly(0, 7.0, suit.height - 2.5, 1.5, suit, h=180, p=0, startH=180, startP=0), Wait(attackDuration - 1.5)))
    elif name == 'PacesetterComeOn':
        camTrack.append(Sequence(motionShot(0, 15, suit.height - 2.5, 180, 0, 0.0, 0, suit), 
                             moveCameraOnly(0, 7.0, suit.height - 2.5, 1.5, suit, h=180, p=0, startH=180, startP=0), Wait(attackDuration - 1.5)))
    elif name == 'AttorneyRushJob':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      heldRelativeShot(suit, 0.0, 7.8096, 9, -180, -10.0, 0.0, attackDuration)))
    elif name == 'AttorneyHurrySickness':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=1.5))
        else:
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
    elif name == 'PresidentTargetCheck':
        camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'PresidentLiability2':
        camTrack.append(defaultCamera(openShotDuration=.5))
    elif name == 'PresidentLiability':
        camTrack.append(defaultCamera(openShotDuration=.5))
    elif name == 'PresidentMandatoryFiling':
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == 'PacesetterTurn1':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'PacesetterTurn2':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'PacesetterEarlyOverclocked':
        # Same as Clash's normal OVERCLOCKED attack: the guitar-solo CTSC
        # owns the camera for the entire transition.
        return Sequence(Wait(attackDuration))
    elif name == 'PacesetterHurrySickness':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=1.5))
        else:
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
    elif name == 'PacesetterHurrySicknessBan':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=1.5))
        else:
            camTrack2 = Sequence(Wait(attackDuration))
            return camTrack2
    elif name == 'PacesetterContentSync':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'PacesetterCorporateRestructuring':
        camTrack.append(allGroupHighShot(suit, attackDuration))
    elif name == 'PacesetterMovingGoalposts':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'PacesetterOverclocked':
        # The original Clash guitar-solo CTSC owns the camera for the whole
        # Overclocked transition.
        return Sequence(Wait(attackDuration))
    elif name in ('RushJobTrap',
            'RushJobLure',
            'RushJobThrow',
            'RushJobSquirt',
            'RushJobZap',
            'RushJobSound',
            'RushJobDrop'):
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
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(banDesc[name], attackDuration - 2)
        pbpDesc2 = pbpDc.getShowIntervalDesc(banDesc[name], attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Rush Job!', attackDuration - 2)
        pbpTrack2 = pbpText.getShowIntervalCheat('Limited Time Offer!', attackDuration - 2)

        if suit.dna.name == 'hustle':
            return Parallel(pbpTrack2, pbpDesc2, camTrack2)
        else:
            return Parallel(pbpTrack, pbpDesc, camTrack2)

    elif name == 'PresidentExtraTip':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'PresidentExtraTip2':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'PresidentExtraTip3':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'PresidentExtraTip4':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'PresidentExtraTip5':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'PresidentExtraTip6':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(2.7),
                                 moveShot(0.0, -15.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'PresidentSnap':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PresidentSensational':
        camTrack.append(heldShot(0.0, -20.0, 12.0, 0, -10, 0, attackDuration - 1.5))
    elif name == 'PresidentViralSensation':
        camTrack2 = Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        return camTrack2
    elif name == 'PresidentSyphon':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'PresidentBayouBellow':
        camTrack.append(Parallel(Wait(attackDuration), Sequence(cameraActorShot(suit, 'litigator-bellow', attackDuration))))
    elif name == 'PresidentSnipe':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'PresidentDeepFreeze':
        camTrack.append(Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(3.0), defaultCamera(openShotDuration=1.5, attackDuration=attackDuration - 3)))
    elif name == 'PresidentFrozenDeath':
        camTrack2 = heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'PresidentPuzzling':
        camTrack2 = Sequence(motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2), heldShot(10, 0, 10, 115, -30, 0, attackDuration - 2))
        return camTrack2
    elif name == 'PresidentDriver':
        camTrack.append(defaultCamera(openShotDuration=2.25))
    elif name == 'PresidentMulligan':
        camTrack.append(defaultCamera(openShotDuration=2.25))
    elif name == 'PresidentHighStakes':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name in (
    'HighStakesHeal',
    'HighStakesTrap',
    'HighStakesLure',
    'HighStakesSound',
    'HighStakesThrow',
    'HighStakesSquirt',
    'HighStakesZap',
    'HighStakesDrop'
        ):
        camTrack2 = Sequence(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
        if attackDuration > 1:
            return camTrack2
        else:
            return Parallel()
    #universal cheats
    elif name == 'Desperation':
        camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'Desperation2':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name in (
        'KnockbackThrow',
    'KnockbackSquirt'
    ):
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name in (
            'ComboThrow',
    'ComboSquirt',
    'ComboDrop'
    ):
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'AbilityQueued':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'AbilityQueuedPreToon':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'SynergyFees':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'CalculatingFees':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'DeathCheck':
        camTrack2 = Sequence(Wait(attackDuration))
        return camTrack2
    elif name == 'CogSpawn':
        camTrack2 = Sequence(Wait(attackDuration))
        return camTrack2
    elif name == 'TargetCheck':
        camTrack2 = Sequence(Wait(attackDuration))
        return camTrack2
    elif name == 'AmbassadorTargetCheck':
        camTrack2 = Sequence(Wait(attackDuration))
        return camTrack2
    elif name == 'UnstableTransformation':
        camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'DrenchDecrement':
        camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'SoakRemoval':
        camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'OilRemoval':
        camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'GovernaughtDeath':
        camTrack2 = Sequence(heldShot(10, 0, 10, 115, -30, 0, attackDuration))
        return camTrack2
    elif name == 'MarkRemoval':
        camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name in (
        'LureRemovalPreToon',
        'LureRemoval',
        'LureRemovalHeal',
        'LureRemovalTrap',
        'LureRemovalLure',
        'LureRemovalSound',
        'LureRemovalThrow',
        'LureRemovalSquirt',
        'LureRemovalZap',
        'LureRemovalDrop'
            ):
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        return camTrack2
    elif name == 'SueApplication':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        return camTrack2
    elif name == 'SueRemoval':
        camTrack2 = heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'AbsorbMovie':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'AbsorbMovieLevel':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name in (
        'AbsorbMovieLure',
        'AbsorbMovieThrow',
        'AbsorbMovieSquirt',
        'AbsorbMovieZap',
        'AbsorbMovieSound',
        'AbsorbMovieDrop'
    ):
        camTrack2 = Sequence(
            motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit),
            Wait(attackDuration)
        )
        return camTrack2

    elif name in (
        'AbsorbMovieLevelLure',
        'AbsorbMovieLevelThrow',
        'AbsorbMovieLevelSquirt',
        'AbsorbMovieLevelZap',
        'AbsorbMovieLevelSound',
        'AbsorbMovieLevelDrop'
    ):
        camTrack2 = Sequence(
            motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit),
            Wait(attackDuration)
        )
        return camTrack2
    elif name == 'ZapMovie':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'SueDamage':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'SyphonMovie':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name == 'DamageMovie':
        camTrack2 = Sequence(motionShot(0.0, 9.0, suit.height + 5, -180, -30.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    elif name in (
        'BanLevel4', 'BanLevel5', 'BanLevel6', 'BanLevel7', 'BanLevel8',
        'BanToonup', 'BanTrap', 'BanLure', 'BanThrow',
        'BanSquirt', 'BanZap', 'BanSound', 'BanDrop'
    ):
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
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(banDesc[name], attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Wire Cut!', attackDuration - 2)

        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))

    elif name in (
        'BanLevel45', 'BanLevel46', 'BanLevel47', 'BanLevel48',
        'BanLevel56', 'BanLevel57', 'BanLevel58',
        'BanLevel67', 'BanLevel68', 'BanLevel78'
    ):
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
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(banDesc[name], attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Contingency Clause!', attackDuration - 2)
        pbpTrack2 = pbpText.getShowIntervalCheat('Wire Cut!', attackDuration - 2)
        pbpTrack3 = pbpText.getShowIntervalCheat('Contract Enforcement!', attackDuration - 2)

        if attack['suit'].dna.name == 'cdirector':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        elif attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack2, pbpDesc, camTrack3)
        elif attack['suit'].dna.name == 'ubuster':
            return Parallel(pbpTrack3, pbpDesc, camTrack4)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name in (
        'BanToonupTrap', 'BanToonupLure', 'BanToonupThrow', 'BanToonupSquirt',
        'BanToonupZap', 'BanToonupSound', 'BanToonupDrop',
        'BanTrapLure', 'BanTrapThrow', 'BanTrapSquirt', 'BanTrapZap',
        'BanTrapSound', 'BanTrapDrop',
        'BanLureThrow', 'BanLureSquirt', 'BanLureZap', 'BanLureSound', 'BanLureDrop',
        'BanThrowSquirt', 'BanThrowZap', 'BanThrowSound', 'BanThrowDrop',
        'BanSquirtZap', 'BanSquirtSound', 'BanSquirtDrop',
        'BanZapSound', 'BanZapDrop',
        'BanSoundDrop'
    ):
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
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc(banDesc[name], attackDuration - 2)
        pbpTrack = pbpText.getShowIntervalCheat('Contingency Clause!', attackDuration - 2)
        pbpTrack2 = pbpText.getShowIntervalCheat('Wire Cut!', attackDuration - 2)

        if attack['suit'].dna.name == 'cdirector':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        elif attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack2, pbpDesc, camTrack3)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name in (
        'DisableToonupTrap', 'DisableToonupLure', 'DisableToonupThrow', 'DisableToonupSquirt',
        'DisableToonupZap', 'DisableToonupSound', 'DisableToonupDrop',
        'DisableTrapLure', 'DisableTrapThrow', 'DisableTrapSquirt', 'DisableTrapZap',
        'DisableTrapSound', 'DisableTrapDrop',
        'DisableLureThrow', 'DisableLureSquirt', 'DisableLureZap', 'DisableLureSound', 'DisableLureDrop',
        'DisableThrowSquirt', 'DisableThrowZap', 'DisableThrowSound', 'DisableThrowDrop',
        'DisableSquirtZap', 'DisableSquirtSound', 'DisableSquirtDrop',
        'DisableZapSound', 'DisableZapDrop',
        'DisableSoundDrop',
        'DisableLevel45', 'DisableLevel46', 'DisableLevel47', 'DisableLevel48',
        'DisableLevel56', 'DisableLevel57', 'DisableLevel58',
        'DisableLevel67', 'DisableLevel68', 'DisableLevel78'
    ):
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name in (
        'GagBanRetaliationHeal',
        'GagBanRetaliationTrap',
        'GagBanRetaliationLure',
        'GagBanRetaliationThrow',
        'GagBanRetaliationSquirt',
        'GagBanRetaliationZap',
        'GagBanRetaliationSound',
        'GagBanRetaliationDrop'
    ):
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDescUnionBuster = pbpDc.getShowIntervalDesc('The Union Buster retaliates against Toons who chose banned gags!', attackDuration - 2)
        pbpTrackUnionBuster = pbpText.getShowIntervalCheat('Breach Of Contract!', attackDuration - 2)
        pbpDescContingency = pbpDc.getShowIntervalDesc('The Contingency Director punishes Toons for using banned gags!', attackDuration - 2)
        pbpTrackContingency = pbpText.getShowIntervalCheat('Contingency Clause!', attackDuration - 2)
        pbpDescRacketeer = pbpDc.getShowIntervalDesc("The Racketeer retaliates against Toons who used banned gags!", attackDuration - 2)
        pbpTrackRacketeer = pbpText.getShowIntervalCheat("Corporate Dominion!", attackDuration - 2)
        pbpDescWiretapper = pbpDc.getShowIntervalDesc('Due to an overinflated budget this toon takes %s damage!' % attack['target'][0]['hp'], attackDuration - 2)
        pbpTrackWiretapper = pbpText.getShowIntervalCheat('Wire Cut!', attackDuration - 2)
        pbpDescStenoCase = pbpDc.getShowIntervalDesc('Due to an illegal action, this toon takes %s damage!' % attack['target'][0]['hp'], attackDuration - 2)
        pbpTrackStenoCase = pbpText.getShowIntervalCheat('Court Record!', attackDuration - 2)
        camTrack2 = Parallel(Wait(attackDuration), Sequence(heldRelativeShot(target[0]['toon'], 3, 10, 3, 163, 0, 0, 2.5, "courtRecordDamageHeldShot"), LerpFunctionInterval(camera.setP, 0.5, fromData=0, toData=10)))
        camTrack3 = Parallel(Wait(attackDuration), Sequence(heldRelativeShot(target[0]['toon'], 3, 10, 3, 163, 0, 0, 2.5, "courtRecordDamageHeldShot")))
        camTrackRacketeer = defaultCamera(openShotDuration=1.5)
        camTrackUnionBuster = defaultCamera(openShotDuration=0.75)
        camTrackContingnency = Sequence(defaultCamera(openShotDuration=0, attackDuration=3), defaultCamera(openShotDuration=1.5, attackDuration=attackDuration-3))
        if attackDuration > 2:
            if suit.dna.name in ('caseman', 'stenog'):
                return Parallel(pbpTrackStenoCase, pbpDescStenoCase, camTrack2)
            elif suit.dna.name == 'wtapper':
                return Parallel(pbpTrackWiretapper, pbpDescWiretapper, camTrack3)
            elif suit.dna.name == 'racket':
                return Parallel(pbpTrackRacketeer, pbpDescRacketeer, camTrackRacketeer)
            elif suit.dna.name == 'cdirector':
                return Parallel(pbpTrackContingency, pbpDescContingency, camTrackContingnency)
            elif suit.dna.name == 'ubuster':
                    return Parallel(pbpTrackUnionBuster, pbpDescUnionBuster, camTrackUnionBuster)
        else:
            return camTrack2
    else:
        camTrack.append(defaultCamera())
    pbpText = attack['playByPlayText']
    displayName = TTLocalizer.SuitAttackNames[attack['name']]
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
            pbpDesc = pbpDc.getShowIntervalDesc(TTLocalizer.SuitCheatDescription[attack['name']], attackDuration - 2)
            pbpTrack = suit.makePlayByPlayTextCheatInterval(pbpText, displayName, attackDuration - 2)
        else:
            pbpDesc = pbpDc.getShowIntervalDesc(TTLocalizer.SuitCheatDescription[attack['name']], attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat(displayName, attackDuration - 2)
        return Parallel(camTrack, pbpTrack, pbpDesc)
    else:
        pbpTrack = suit.makePlayByPlayTextInterval(pbpText, displayName, attackDuration - 2)
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
    track = random.choice(shotChoices)(*[av, duration])
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


def allGroupShot(avatar, duration):
    return heldShot(10, 0, 10, 79, -30, 0, duration, 'allGroupShot')


def allGroupLowShot2(avatar, duration):
    shot2 = heldShot(-18, -5, 5, -69, 0, 0, duration, 'allGroupLowShot')
    shot3 = heldShot(18, -5, 5, 69, 0, 0, duration, 'allGroupLowShot')
    return random.choice((shot2, shot3))


def allGroupLowShot(avatar, duration, battle):
    numSuits = len(battle.activeSuits)
    if numSuits > 5:
        return heldShot(20.0, -15.0, 10.0, 45, -20, 0, duration, 'allGroupLowShot')
    else:
        return heldShot(17, -5, 5, 69, 0, 0, duration, 'allGroupLowShot')


def allGroupLowDiagonalShot(avatar, duration):
    return heldShot(7, 5, 6, 119, -30, 0, duration, 'allGroupLowShot')


def allGroupHighShot(avatar, duration):
    return heldShot(0, -15, 8, 0, -10, 0, duration, 'allGroupHighShot')


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
        for i in range(0, numShakes):
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


def randomActorShot(actor, battle, duration, actorType, groupShot = 0):
    height = actor.getHeight()
    centralPoint, origHpr = battle.getActorPosHpr(actor)
    centralPoint.setZ(centralPoint.getZ() + height * 0.75)
    if actorType == 'suit':
        x = 4 + random.random() * 1.5
        y = -2 - random.random() * 2
        z = height * 0.5 + random.random() * height * .75
        if groupShot == 1:
            y = -4
            z = height * 0.5
    else:
        x = 4 + random.random() * 1.5
        y = -2 - random.random() * 2
        z = height + random.random() * height * .75
        if groupShot == 1:
            y = y + 3
            z = height * 0.5
    if MovieUtil.shotDirection == 'left':
        x = -x
    return focusShot(x, y, z, duration, centralPoint)

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
    suitHeight = suit.getHeight()
    toonHeight = toon.getHeight()
    suitCentralPoint, origHpr = battle.getActorPosHpr(suit)
    suitCentralPoint.setZ(suitCentralPoint.getZ() + suitHeight * 0.75)
    toonCentralPoint, origHpr = battle.getActorPosHpr(toon)
    toonCentralPoint.setZ(toonCentralPoint.getZ() + toonHeight * 0.75)
    x = 2 + random.random() * 7
    if focus == 'toon':
        y = 6 + random.random() * 4
        z = suitHeight * 1.2 + random.random() * suitHeight
    else:
        y = -10 - random.random() * 4
        z = toonHeight * 1.5
    if MovieUtil.shotDirection == 'left':
        x = -x
    return focusShot(x, y, z, duration, toonCentralPoint, splitFocusPoint=suitCentralPoint)

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
    sum = 0
    for t in toons:
        toon = t['toon']
        height = toon.getHeight()
        sum = sum + height

    avgHeight = sum / len(toons) * 0.75
    suitPos, origHpr = battle.getActorPosHpr(suit)
    x = 1 + random.random() * 3
    if suitPos.getX() > 0:
        x = -x
    if random.random() > 0.5:
        y = 3 + random.random() * 1
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
         suitGroupThreeQuarterLeftBehindShot]
    elif numThrows >= 2 and numThrows <= 4:
        shotChoices = [suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of throws: %s' % numThrows)
    shotChoice = random.choice(shotChoices)
    track = shotChoice(*[av, duration])
    print('chooseFireOpenShot %s' % shotChoice)
    return track


def chooseFireCloseShot(throws, suitThrowsDict, openDuration, openName, attackDuration):
    numSuits = len(suitThrowsDict)
    av = None
    duration = attackDuration - openDuration
    if numSuits == 1:
        av = base.cr.doId2do[list(suitThrowsDict.keys())[0]]
        shotChoices = [avatarCloseUpFireShot,
         avatarCloseUpThreeQuarterLeftFireShot,
         suitGroupThreeQuarterLeftBehindShot]
    elif numSuits >= 2 and numSuits <= 7 or numSuits == 0:
        shotChoices = [suitGroupThreeQuarterLeftBehindShot]
    else:
        notify.error('Bad number of suits: %s' % numSuits)
    shotChoice = random.choice(shotChoices)
    track = shotChoice(*[av, duration])
    print('chooseFireOpenShot %s' % shotChoice)
    return track


def avatarCloseUpFireShot(avatar, duration):
    return heldRelativeShot(avatar, 7, 17, avatar.getHeight() * 0.66, 159, 3.6, 0, duration, 'avatarCloseUpFireShot')


def avatarCloseUpThreeQuarterLeftFireShot(avatar, duration):
    return heldRelativeShot(avatar, -8.2, 8.45, avatar.getHeight() * 0.66, -131.5, 3.6, 0, duration, 'avatarCloseUpThreeQuarterLeftShot')


def chooseSueShot(throws, suitThrowsDict, attackDuration, enterDuration = 0.0, exitDuration = 0.0):
    '''
    Honestly, this should not be different from the Throw camera considering the animation for suing a Cog is the same as pie-throwing, but with the lawbook prop.
    '''
    return chooseThrowShot(throws, suitThrowsDict, attackDuration, enterDuration=enterDuration, exitDuration=exitDuration)
