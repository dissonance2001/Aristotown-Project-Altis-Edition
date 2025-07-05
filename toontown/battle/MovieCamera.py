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

def cameraActorShotHighRoller(parent, anim, remainTime = 0.0, name = 'cameraActorShot'):
    previousParent = camera.getParent()
    path = 'phase_3.5/models/misc/camera_actor'
    cameraActor = Actor.Actor(path, {anim: path + '-' + anim})
    node = cameraActor.find('**/CameraBone')
    track = Sequence(
        Func(cameraActor.reparentTo, parent),
        Func(camera.reparentTo, node),
        Func(cameraActor.setPosHpr, 0, -27.5, -25, 180, 80, 0),
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
    name = attack['name']
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

    if name == 'AcidRain':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Audit':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'Bash':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'Beguile':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'CloseTheLoop':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HostileTakeover':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'NickelAndDime':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Quash':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'PennyPinch':
        camTrack.append(allGroupLowShot(suit, attackDuration))
    elif name == 'Disassemble':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'DataCorruption':
        camTrack.append(defaultCamera(openShotDuration=2.5))
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
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'DiskScratch':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'VoodooMagic':
        camTrack.append(defaultCamera(openShotDuration=0.75))
    elif name == 'ElectrostaticEnergy':
        camTrack.append(defaultCamera(openShotDuration=0.5))
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
        camTrack.append(defaultCamera(openShotDuration=3.0))
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
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'FreezeAssets':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'GlowerPower':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'ReArrange':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'ShortSqueeze':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'BlueChip':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'FallingKnife':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'GuiltTrip':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Embezzle':
        camTrack.append(allGroupLowShot(suit, attackDuration))
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
        camTrack.append(allGroupLowShot(suit, attackDuration))
    elif name == 'PinkSlip':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PlayHardball':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PoundKey':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'PowerTie':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'PowerTrip':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'Quake':
        camTrack.append(defaultCamera(openShotDuration=3.0))
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
    elif name == 'Shake':
        camTrack.append(defaultCamera(openShotDuration=2.0))
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
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'Withdrawal':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'WriteOff':
        camTrack.append(defaultCamera(openShotDuration=2.0))
        # redd heir wing cheats
    elif name == 'ReddLiquidationSale':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'ReddPeckingOrder':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'ReddAutoRepair':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        # witness stand-in cheats
    elif name == 'WSIJuryNotice':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'WSICeaseAndDesist':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
        # litigator cheats
    elif name == 'LitigatorSnapSoak':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'LitigatorSnap':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'LitigatorBayouBash':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      heldRelativeShot(suit, 0.0, 6.8096, 8, -180, -10.0, 0.0, attackDuration)))
    elif name == 'LitigatorBayouBellow':
        camTrack.append(Sequence(cameraActorShot(suit, 'litigator-bellow', 0), heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration - 4.5)))
        # stenographer cheats
    elif name == 'StenographerSanctionBindings':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=0.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'StenographerSanction':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'StenographerCourtRecordBan':
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
    elif name == 'CaseManagerInsurancePlan':
        if not suit.isSkeleton:
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                      motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0.7, suit), Wait(2.0), moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5), heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 4.2)))

        else:
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                     motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0.7, suit), Wait(2.0),
                                     moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                     heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 4.2)))
    elif name == 'CaseManagerInsurance':
        camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'CaseManagerLegalBindings':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'CaseManagerLegallyBound':
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('Legally Bound Toons take 20 damage per round!', attackDuration - 2)
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
            pbpDesc = pbpDc.getShowIntervalDesc(
                'Due to an illegal action, this toon takes 50 damage!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Court Record!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
        # scapegoat cheats
    elif name == 'ScapegoatShieldsUp':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'ScapegoatEnraged':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 heldRelativeShot(suit, 0.0, 6.8096, 7, -180, -20.0, 0.0, attackDuration)))
    elif name == 'ScapegoatGavel':
        camTrack.append(defaultCamera(openShotDuration=2))
    elif name == 'ScapegoatBarnyardBash':
        camTrack.append(defaultCamera(openShotDuration=2))
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
    elif name == 'PowerhouseLureImmune':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseSyphon':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseSyphonDesperation':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'PowerhouseSnipeVulnerable':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.0)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse retaliates against toons with existing\nvulnerabilities!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.0)
            return camTrack2
    elif name == 'PowerhouseSnipeGagBan':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.0)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse doubles down damage on toons who chose\nbanned gags!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.0)
            return camTrack2
    elif name == 'PowerhouseSnipeSoaked':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'PowerhouseSnipeBookkept':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.0)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse doubles down damage on toons who\nattacked the Bookkeeper while Bookkeeping!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.0)
            return camTrack2
    elif name == 'PowerhouseSnipeMulligan':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.0)
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
    elif name == 'PowerhouseSnipeCollectCall':
        if attackDuration > 2:
            camTrack2 = defaultCamera(openShotDuration=1.0)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                'The Powerhouse retaliates against toons with who owe\ncollect call dues!',
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Snipe!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=1.0)
            return camTrack2
    # bookkeeper cheats
    elif name == 'BookkeeperPaperCutSoaked':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'BookkeeperPaperCutMarked':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'BookkeeperPaperCut':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'BookkeeperExplodingDocument':
        camTrack.append(defaultCamera(openShotDuration=2.0))
    elif name == 'BookkeeperBookkeepingRetaliation':
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
    elif name == 'BookkeeperBookkeeping':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    # wiretapper cheats
    elif name == 'WiretapperCollectCall':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'WiretapperCollectCallDamage':
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc(
                "Toons are forced to pay collect call fees every turn\nuntil their dues are paid!",
                attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Collect Call Dues!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'WiretapperGagBan':
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
    elif name == 'WiretapperWiretapped':
        camTrack.append(Sequence(defaultCamera(openShotDuration=2.0, attackDuration=4.0), randomActorShot(suit, battle, attackDuration - 4, 'suit')))
    elif name == 'WiretapperVoicemail':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'WiretapperBrokenConnection':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    # ambassador cheats
    elif name == 'AmbassadorHeadRoller':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'AmbassadorHeadRollerGroup':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'AmbassadorRefinement':
        camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == 'AmbassadorRefinementManager':
        camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
    elif name == 'AmbassadorGhostMentality':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'AmbassadorPhase2':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorDamageUp':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorManagerialProtection':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorManagerialProtectionImmunity':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'AmbassadorMulligan':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    # safety supervisor cheats
    elif name == 'SafetyHighPressure':
        camTrack.append(defaultCamera(openShotDuration=3.0))
    elif name == 'SafetyHeatWave':
        camTrack.append(Sequence(defaultCamera(openShotDuration=1.5, attackDuration=4.0), randomActorShot(suit, battle, attackDuration - 4, 'suit')))
    elif name == 'SafetyHeatWaveCalculation':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'SafetyViolation':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=2.0))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'SafetyPromotion':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    # union buster cheats
    elif name == 'UnionBusterUnionDues':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'UnionBusterUnionCalculator':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'UnionBusterUnionBust':
        camTrack.append(heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'UnionBusterUnionBuster':
        camTrack.append(defaultCamera(openShotDuration=1.0))
    elif name == 'UnionBusterUnionBusterDamage':
        if attackDuration > 2:
            camTrack2 = heldShot(10, 0, 10, 115, -30, 0, attackDuration)
            pbpText = attack['playByPlayText']
            pbpDc = PlayByPlayText.PlayByPlayText()
            pbpDesc = pbpDc.getShowIntervalDesc('Busted Toons are forced to take damage every round!', attackDuration - 2)
            pbpTrack = pbpText.getShowIntervalCheat('Union Buster!', attackDuration - 2)
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'UnionBusterUnionWages':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'UnionBusterBreachOfContract':
        camTrack.append(defaultCamera(openShotDuration=0.5))
    elif name == 'UnionBusterBreachOfContract2':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=0.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'UnionBusterBreachOfContract3':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=0.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'UnionBusterBreachOfContract4':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=0.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'UnionBusterContractEnforcement':
        camTrack.append(Sequence(randomActorShot(suit, battle, 2, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3.5)))
        # racketeer
    elif name == 'RacketeerProfiteering':
        camTrack.append(heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'RacketeerExtortion':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'RacketeerExtortion2':
        if attackDuration > 2:
            camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, attackDuration))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'RacketeerCompensation':
        camTrack.append(heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'RacketeerHustling':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'RacketeerRacketeering':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'RacketeerPeckingOrderRetaliation':
        if attackDuration > 2:
            camTrack.append(defaultCamera(openShotDuration=2.0))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'RacketeerPeckingOrderRetaliationSoak':
        camTrack.append(defaultCamera(openShotDuration=1.5))
        # radiographer
    elif name == 'RadiographerRadioInfrequency':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'RadiographerHotTake':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0.5, attackDuration=1.5), randomActorShot(suit, battle, attackDuration - 1.5, 'suit')))
    elif name == 'RadiographerHotTakeRetaliation':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0.5, attackDuration=1.5), randomActorShot(suit, battle, attackDuration - 1.5, 'suit')))
    elif name == 'RadiographerOvermodulated':
        camTrack.append(Sequence(randomActorShot(suit, battle, 1.5, 'suit'),
                                 moveShot(0.0, -10.0, 10.0, 0, -20, 0, 1.5),
                                 heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration - 3)))
    #high roller phase 1 cheats
    elif name == 'HighRollerNoAttack':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        return camTrack2
    elif name == 'HighRollerWheelSpin':
        camTrack.append(Sequence(motionShot(0.0, 5, 8, -180, 0.0, 0.0, 0, suit), Wait(3.5),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 motionShot(0.0, 10, 8, -180, 0.0, 0.0, 0, suit), Wait(attackDuration - 5.75)))
    elif name == 'HighRollerCommercialBreak':
        camTrack.append(heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'HighRollerGameTimeSpawn':
        camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0.7, suit), Wait(attackDuration - .7)))
    elif name == 'HighRollerGameTimeCog':
        camTrack.append(heldShot(0.0, -10.0, 12.0, 0, -10, 0, attackDuration))
    elif name == 'HighRollerGameTimeCog2':
        camTrack.append(heldShot(0.0, -10.0, 12.0, 0, -10, 0, attackDuration))
    elif name == 'HighRollerBust':
        if attackDuration > 2:
            camTrack.append(Sequence(defaultCamera(openShotDuration=0, attackDuration=0),
                                 motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0.7, suit), Wait(5.0),
                                 moveShot(0.0, -20.0, 10.0, 0, -20, 0, 0.5),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 6.2)))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    # high roller phase 2 cheats
    elif name == 'HighRollerPhase3':
        camTrack2 = Sequence(motionShot(0.0, 8.8096, 7.77317, -180, 0.0, 0.0, 0, suit), Wait(attackDuration))
        return camTrack2
    # high roller phase 3 cheats
    elif name == 'HighRollerFreeCruise':
        camTrack.append(heldShot(0.0, -15.0, 10.0, 0, -20, 0, 3.7))
        camTrack.append(moveShot(-21.0, 8.0, 8.0, -120, 0, 0, 0.5))
        camTrack.append(heldShot(-21.0, 8.0, 8.0, -120, 0, 0, attackDuration - 4.2))
    elif name == 'HighRollerConduction':
        camTrack.append(heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration))
    elif name == 'HighRollerRolled':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HighRollerRaisingTheAnte':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HighRollerDiceRouletteCogs':
        camTrack.append(Sequence(randomActorShot(suit, battle, 3.5, 'suit'),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 motionShot(0.0, 10, 8, -180, 0.0, 0.0, 0, suit), Wait(2.0),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 7.75)))
    elif name == 'HighRollerDiceRouletteToons':
        camTrack.append(Sequence(randomActorShot(suit, battle, 3.5, 'suit'),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 motionShot(0.0, 10, 8, -180, 0.0, 0.0, 0, suit), Wait(2.0),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 7.75)))
    elif name == 'HighRollerDiceRouletteEveryone':
        camTrack.append(Sequence(randomActorShot(suit, battle, 3.5, 'suit'),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 motionShot(0.0, 10, 8, -180, 0.0, 0.0, 0, suit), Wait(2.0),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 7.75)))
    elif name == 'HighRollerDiceRouletteNobody':
        camTrack.append(Sequence(randomActorShot(suit, battle, 3.5, 'suit'),
                                 motionShot(0.0, 1.5, 9, -180, 0.0, 0.0, 0, suit), Wait(2.25),
                                 motionShot(0.0, 10, 8, -180, 0.0, 0.0, 0, suit), Wait(2.0),
                                 heldShot(0.0, -20.0, 10.0, 0, -20, 0, attackDuration - 7.75)))
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
    elif name == 'HighRollerSingingBlues':
        camTrack.append(defaultCamera(openShotDuration=2.5))
    elif name == 'HighRollerDamageReduction':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'HighRollerSplashback':
        if attackDuration > 1:
            camTrack.append(defaultCamera(openShotDuration=1.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    elif name == 'HighRollerCheerRetaliation':
        if attackDuration > 1:
            camTrack.append(defaultCamera(openShotDuration=1.5))
        else:
            camTrack2 = defaultCamera(openShotDuration=0)
            return camTrack2
    #universal cheats
    elif name == 'Desperation':
        camTrack2 = heldShot(0.0, -10.0, 10.0, 0, -20, 0, attackDuration)
        return camTrack2
    elif name == 'SynergyFees':
        camTrack.append(defaultCamera(openShotDuration=1.5))
    elif name == 'CalculatingFees':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'DeathCheck':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        return camTrack2
    elif name == 'SoakRemoval':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        return camTrack2
    elif name == 'BanLevel4':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 4 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel5':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 5 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel6':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 6 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel7':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 7 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel8':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 8 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel45':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 4 and 5 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel46':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 4 and 6 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel47':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 4 and 7 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel48':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 4 and 8 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel56':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 5 and 6 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel57':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 5 and 7 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel58':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 5 and 8 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel67':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 7 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel68':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 8 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLevel78':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Level 7 and 8 gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
        if attack['suit'].dna.name == 'safesupervis':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanToonup':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Toon-Up gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanTrap':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Trap gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLure':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Lure gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanThrow':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Throw gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanSquirt':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Squirt gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanZap':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Zap gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanSound':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Sound gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanDrop':
        camTrack2 = randomActorShot(suit, battle, attackDuration, 'suit')
        pbpText = attack['playByPlayText']
        pbpDc = PlayByPlayText.PlayByPlayText()
        pbpDesc = pbpDc.getShowIntervalDesc('Drop gags are off-limits!', 3.5)
        pbpTrack = pbpText.getShowIntervalCheat('Budget Cuts!', 3.5)
        if attack['suit'].dna.name == 'wtapper':
            return Parallel(pbpTrack, pbpDesc, camTrack2)
        else:
            camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanToonupTrap':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanToonupLure':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanToonupThrow':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanToonupSquirt':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanToonupZap':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanToonupSound':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanToonupDrop':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanTrapLure':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanTrapThrow':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanTrapSquirt':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanTrapZap':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanTrapSound':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanTrapDrop':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLureThrow':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLureSquirt':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLureZap':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLureSound':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanLureDrop':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanThrowSquirt':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanThrowZap':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanThrowSound':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanThrowDrop':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanSquirtZap':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanSquirtSound':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanSquirtDrop':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanZapSound':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanZapDrop':
        camTrack.append(randomActorShot(suit, battle, attackDuration, 'suit'))
    elif name == 'BanSoundDrop':
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
