from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
import math
from direct.showutil import Effects
from toontown.battle import SuitBattleGlobals
from toontown.battle.BattleProps import *
from toontown.effects import DustCloud
from toontown.toon import Toon
from otp.otpbase import OTPLocalizerEnglish
from toontown.battle.BattleSounds import *
from toontown.battle.SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import BattleProps
from toontown.suit import Suit
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from toontown.suit.SuitDNA import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownGlobals import *
from toontown.battle.attacks.suits import MovieIntervals

notify = DirectNotifyGlobal.directNotify.newCategory('MovieSuitAttacks')

def throwPos(t, object, duration, target, values, gravity = -32.144):
    origin = values['origin']
    velocity = values['velocity']
    if callable(target):
        target = target()
    x = origin[0] * (1 - t) + target[0] * t
    y = origin[1] * (1 - t) + target[1] * t
    time = t * duration
    z = origin[2] + velocity * time + 0.5 * gravity * time * time
    object.setPos(x, y, z)

def __doDamage(toon, dmg, died):
    return MovieIntervals.__doDamage(toon, dmg, died)

def __doDamageCheat(toon, dmg, died):
    return MovieIntervals.__doDamageCheat(toon, dmg, died)

def __showProp(prop, parent, pos, hpr = None, scale = None):
    return MovieIntervals.__showProp(prop, parent, pos, hpr, scale)

def __animProp(prop, propName, propType = 'actor'):
    return MovieIntervals.__animProp(prop, propName, propType)

def __suitFacePoint(suit, zOffset = 0):
    return MovieIntervals.__suitFacePoint(suit, zOffset)

def __toonFacePoint(toon, zOffset = 0, parent = render):
    return MovieIntervals.__toonFacePoint(toon, zOffset, parent)

def __toonTorsoPoint(toon, zOffset = 0):
    return MovieIntervals.__toonTorsoPoint(toon, zOffset)

def __toonGroundPoint(attack, toon, zOffset = 0, parent = render):
    return MovieIntervals.__toonGroundPoint(attack, toon, zOffset, parent)

def __toonGroundMissPoint(attack, prop, toon, zOffset = 0):
    return MovieIntervals.__toonGroundMissPoint(attack, prop, toon, zOffset)

def __toonMissPoint(prop, toon, yOffset = 0, parent = None):
    return MovieIntervals.__toonMissPoint(prop, toon, yOffset, parent)

def __toonMissBehindPoint(toon, parent = render, offset = 0):
    return MovieIntervals.__toonMissBehindPoint(toon, parent, offset)

def __throwBounceHitPoint(prop, toon):
    return MovieIntervals.__throwBounceHitPoint(prop, toon)

def __throwBounceMissPoint(prop, toon):
    return MovieIntervals.__throwBounceMissPoint(prop, toon)

def __throwBouncePoint(startPoint, endPoint):
    return MovieIntervals.__throwBouncePoint(startPoint, endPoint)

def getResetTrack(suit, battle):
    return MovieIntervals.getResetTrack(suit, battle)

def __createSuitResetPosTrack(suit, battle):
    return MovieIntervals.__createSuitResetPosTrack(suit, battle)

def getSuitTrack(attack, delay = 1e-06, splicedAnims = None, playRate = 1.0):
    return MovieIntervals.getSuitTrack(attack, delay, splicedAnims, playRate)

def getSuitAnimTrack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    return MovieIntervals.getSuitAnimTrack(attack, delay, splicedAnims, playRate)

def getSuitAnimTrackAttack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    return MovieIntervals.getSuitAnimTrackAttack(attack, delay, splicedAnims, playRate)

def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    return MovieIntervals.getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop)

def getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative = 1, softStop = 0):
    return MovieIntervals.getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative, softStop)

def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrack(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)

def getToonTracks(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTracks(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, showDamageExtraTime, showMissedExtraTime)

def getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    return MovieIntervals.getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime)

def getAllyToonsDodgeParallel(target):
    return MovieIntervals.getAllyToonsDodgeParallel(target)

def getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5, startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0, animStartTime = 0.0):
    return MovieIntervals.getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint, scaleUpTime, scaleDownTime, startScale, anim, propName, animDuration, animStartTime)

def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    return MovieIntervals.getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint, scaleUpTime, startScale, poseExtraArgs)

def getPropThrowTrack(attack, prop, hitPoints = [], missPoints = [], hitDuration = 0.25, missDuration = 0.25, hitPointNames = 'none', missPointNames = 'none', lookAt = 'none', groundPointOffSet = 0, missScaleDown = None, parent = render, target = None):
    return MovieIntervals.getPropThrowTrack(attack, prop, hitPoints, missPoints, hitDuration, missDuration, hitPointNames, missPointNames, lookAt, groundPointOffSet, missScaleDown, parent, target)

def getThrowTrack(object, target, duration = 1.0, parent = render, gravity = -32.144):
    return MovieIntervals.getThrowTrack(object, target, duration, parent, gravity)

def getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    return MovieIntervals.getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames, splicedDamageAnims, showDamageExtraTime)

def getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    return MovieIntervals.getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames, splicedDamageAnims, showDamageExtraTime)

def getSplicedAnimsTrack(anims, actor = None):
    return MovieIntervals.getSplicedAnimsTrack(anims, actor)

def getSplicedLerpAnims(animName, origDuration, newDuration, startTime = 0, fps = 30, reverse = 0):
    return MovieIntervals.getSplicedLerpAnims(animName, origDuration, newDuration, startTime, fps, reverse)

def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    return Sequence(Wait(delay), SoundInterval(globalBattleSoundCache.getSound(fileName), duration=duration, node=node))

def getToonTrackCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrackCheat(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)

def getToonTrackCheat2(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrackCheat2(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)


def getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    return MovieIntervals.getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime)


def getToonTracksCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTracksCheat(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, showDamageExtraTime, showMissedExtraTime)


def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    return Sequence(Wait(delay), SoundInterval(globalBattleSoundCache.getSound(fileName), duration=duration, node=node))

def doAccountRollover(attack):
    suit = attack['suit']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    managerHealTrack = Sequence(Sequence(Wait(2.0), Func(suit.checkCompensationDividend)))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, soundTrack, managerHealTrack, soundTrack2)

def doAccountRollover2(attack):
    suit = attack['suit']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    managerHealTrack = Sequence(Sequence(Wait(2.0), Func(suit.checkCompensationDividend2)))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, soundTrack, managerHealTrack, soundTrack2)

def doAccountRollover3(attack):
    suit = attack['suit']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    managerHealTrack = Sequence(Sequence(Wait(2.0), Func(suit.checkCompensationDividend3)))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, soundTrack, managerHealTrack, soundTrack2)

def doAccountRollover4(attack):
    suit = attack['suit']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    managerHealTrack = Sequence(Sequence(Wait(2.0), Func(suit.checkCompensationDividend4)))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, soundTrack, managerHealTrack, soundTrack2)

def doAccountRollover5(attack):
    suit = attack['suit']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    managerHealTrack = Sequence(Sequence(Wait(2.0), Func(suit.checkCompensationDividend5)))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, soundTrack, managerHealTrack, soundTrack2)

def doLiquidationEvent(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    notifyTracks = Parallel()
    suitTrack = Sequence(Wait(0.5), getSuitTrack(attack, playRate=1.25))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    for t in attack['target']:
        toon = t['toon']
        BattleParticles.loadParticles()
        cloud = globalPropPool.getProp('stormcloud')
        rainEffect = BattleParticles.createParticleEffect(file='liquidate2')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate2')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate2')
        initialCloudHeight = suit.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 8)
        cloudPropTrack.append(Wait(0.6))
        cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
        cloudPropTrack.append(Parallel(
            Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=4.1, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=4.0, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=4.0, cleanup=True, softStopT=-1)),
            Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=3.3))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(cloud.removeNode))
        cloudPropTracks.append(cloudPropTrack)
        if t['hp'] != 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(puddle.removeNode))
            puddleTracks.append(puddleTrack)
            notifyTrack = Sequence(Wait(damageDelay), Func(toon.makeLiquidated), Func(toon.addLiquidatedRounds, 3), Func(toon.showHpTextNew, -t['hp'], text="LIQUIDATED!", colorCode=1))
            notifyTracks.append(notifyTrack)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    toonTracks = getToonTracksCheat(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                             dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, puddleTracks, cloudPropTracks, notifyTracks, soundTrack)

def doLiquidationEventDamage(attack):
    battle = attack['battle']
    targets = attack['target']
    suit = attack['suit']
    damageDelay = 1.3
    dodgeDelay = 0.25
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    toonTracks = getToonTracksCheat(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                               dodgeAnimNames=['sidestep'])
    soundTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            cloud = globalPropPool.getProp('stormcloud')
            rainEffect = BattleParticles.createParticleEffect(file='liquidate2')
            rainEffect2 = BattleParticles.createParticleEffect(file='liquidate2')
            rainEffect3 = BattleParticles.createParticleEffect(file='liquidate2')
            initialCloudHeight = suit.height + 3
            cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
            cloudPropTrack = Sequence()
            cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
            cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
            cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
            cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
            targetPoint = __toonFacePoint(toon)
            targetPoint.setZ(targetPoint[2] + 10)
            cloudPropTrack.append(LerpPosInterval(cloud, 0, pos=targetPoint))
            cloudPropTrack.append(Wait(1.1))
            cloudPropTrack.append(Parallel(
                Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=4.1, cleanup=True, softStopT=-1)),
                Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=4.0, cleanup=True, softStopT=-1)),
                Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=4.0, cleanup=True, softStopT=-1)),
                Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=3.3))))
            cloudPropTrack.append(Wait(0.4))
            cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
            cloudPropTrack.append(Func(cloud.removeNode))
            cloudPropTracks.append(cloudPropTrack)
            notifyTrack = Sequence(Wait(damageDelay), Func(toon.showHpTextNew, -t['hp']))
            notifyTracks.append(notifyTrack)
            sandTrap = globalPropPool.getProp('quicksand')
            sandTrap.setHpr(Point3(120, 0, 0))
            sandTrap.setScale(0.01)
            sandTrap.setColor((0.0, 0.0, 1.0, 1))
            puddleTracks.append(Sequence(
                Func(battle.movie.needRestoreRenderProp, sandTrap),
                Wait(damageDelay - 0.7),
                Func(sandTrap.reparentTo, battle),
                Func(sandTrap.setPos, toon.getPos(battle)),
                LerpScaleInterval(sandTrap, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO),
                Wait(0.3 if dmg == 0 else 3.2),
                LerpFunctionInterval(sandTrap.setAlphaScale, fromData=1, toData=0, duration=0.8),
                Func(sandTrap.removeNode)
            ))
            soundTracks.append(getSoundTrack('SA_liquidate.ogg', delay=0.5, duration=0.67 if dmg == 0 else 0.0, node=toon))

    return Parallel(notifyTracks, cloudPropTracks, toonTracks, soundTracks, puddleTracks)

def doPeckingOrderGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDuration = 3.03
    throwDelay = 2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    notifyTracks = Parallel()
    propDelay = 1.5
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        for i in xrange(0, numBirds):
            next = globalPropPool.getProp('bird')
            # next.setScale(0.01)
            # next.reparentTo(suit.getRightHand())
            #  next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            if dmg > 0:
                notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
                notifyTracks.append(notifyTrack)
                hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6,
                                  random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            else:
                hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
            birdTrack = Sequence(Wait(throwDelay), Func(next.setScale, 0.01), Func(next.reparentTo, suit.getRightHand()),
                                 Func(next.setPos, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3), Func(battle.movie.needRestoreRenderProp, next),
                                 Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)),
                                 LerpPosInterval(next, 0.5, hitPoint))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.5, Point3(9, 9, 9)), LerpScaleInterval(next, .5, Point3(0, 0, 0)))
            birdTracks.append(Sequence(Parallel(birdTrack, scaleTrack), Func(MovieUtil.removeProp, next)))
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.14,
                        0.21])
    damageAnims.append(['cringe',
                        0.01,
                        0.14,
                        0.13])
    damageAnims.append(['cringe', 0.01, 0.43])
    toonTrack = getToonTracksCheat(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=0.75,
                                   dodgeAnimNames=['duck'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, notifyTracks, soundTrack, birdTracks)

def doPeckingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDuration = 3.03
    throwDelay = 2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    notifyTracks = Parallel()
    propDelay = 1.5
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        for i in xrange(0, numBirds):
            next = globalPropPool.getProp('bird')
            # next.setScale(0.01)
            # next.reparentTo(suit.getRightHand())
            #  next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            if dmg > 0:
                notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
                notifyTracks.append(notifyTrack)
                hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6,
                                  random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            else:
                hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
            birdTrack = Sequence(Wait(throwDelay), Func(next.setScale, 0.01), Func(next.reparentTo, suit.getRightHand()),
                                 Func(next.setPos, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3), Func(battle.movie.needRestoreRenderProp, next),
                                 Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)),
                                 LerpPosInterval(next, 0.5, hitPoint))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.5, Point3(9, 9, 9)), LerpScaleInterval(next, .5, Point3(0, 0, 0)))
            birdTracks.append(Sequence(Parallel(birdTrack, scaleTrack), Func(MovieUtil.removeProp, next)))
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.14,
                        0.21])
    damageAnims.append(['cringe',
                        0.01,
                        0.14,
                        0.13])
    damageAnims.append(['cringe', 0.01, 0.43])
    toonTrack = getToonTracksCheat(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=0.75,
                                   dodgeAnimNames=['duck'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, notifyTracks, soundTrack, birdTracks)

def doWhirlwind(attack):
    suit = attack['suit']
    target = attack['target']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    cagePropTracks = Parallel()
    toonSpinTracks = Parallel()
    toonLiftTracks = Parallel()
    toonAnimationTracks = Parallel()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind')
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        # cage.setH(90)
        # cage.setPosHpr(0, 0, 0, 180, 0, 0)
        suitPos = suit.getPos(battle)
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        cagePos = [Point3(suitPos.getX(), y + 15, suitPos.getZ()), toon.getHpr(battle)]
        spinTrack = Sequence(LerpHprInterval(cage, 5.5, Point3(-10800, 0, 0)))
        cagePropTrack = Sequence(
            Parallel(cagePosition),
            Parallel(getPropAppearTrack(cage, battle, cagePos, 0.25, scaleUpPoint=Point3(2.0), scaleUpTime=1.0),
                cage.posInterval(0.75, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_toonInWhirlwind.ogg'), duration=0.75, node=cage), spinTrack,
            ),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        sinkPos = toon.getPos(battle)
        sinkPos.setZ(sinkPos.getZ() + 25)
        toonSpinTrack = Sequence(Wait(0.9), LerpHprInterval(toon, 4.5, Point3(10800, 0, 0)),
                                 LerpHprInterval(toon, 0.5, toon.getHpr()), Wait(0.5))
        toonLiftTrack = Sequence(Wait(0.9), LerpPosInterval(toon, 4.5, Point3(toon.getX(), toon.getY(), toon.getZ() + 50)), LerpPosInterval(toon, 0.5, toon.getPos()), Wait(0.5))
        toonSpinTracks.append(toonSpinTrack)
        toonLiftTracks.append(toonLiftTrack)
        damageAnims = []
        damageAnims.append(['duck',
                            0.01,
                            0.01,
                            1.1])
        damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
        damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
        damageAnims.append(['slip-forward'])
        toonAnimationTracks.append(getSplicedAnimsTrack(damageAnims, actor=toon))
    soundTrack = getSoundTrack('tt_s_ara_cfg_whirlwind.ogg', delay=0)
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.append(['slip-forward'])
    return Parallel(suitTrack, cagePropTracks, soundTrack, toonLiftTracks, toonSpinTracks)

def doFootnoteOverload(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    explode = []
    explosionTracks = Parallel()
    propTracks = Parallel()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(2.25))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        for i in xrange(0, 3):
            explode.append(globalPropPool.getProp('explosion'))
        explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
        explodePosPoints1 = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
        explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
        explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
        explodeTracks = Parallel()
        for i in xrange(0, 3):
            explodeTrack = Sequence()
            explodeTrack.append(Wait(2.25))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
            explodeTracks.append(explodeTrack)
        explosionTracks.append(explodeTracks)
        dmg = target[0]['hp']
        tnt = globalPropPool.getProp('shredder-paper')
        paper = globalPropPool.getProp('shredder-paper')
        posPoints = [Point3(.78, -1.89, -.17), VBase3(10, 250, -10)]
        propTrack = Sequence(getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.75, Point3(1, 1, 1), scaleUpTime=0.25))
        propTrack.append(Wait(1.05))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
        propTracks.append(propTrack)
    toonTrack = getToonTracks(attack, 2.5, ['slip-forward'], 0, ['nothing'])
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.25)
    return Parallel(suitTrack, toonTrack, soundTrack, propTracks, explosionTracks)

def doCage(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']


    suitTrack = Sequence(getSuitTrack(attack))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_crg_toonCage')
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(0.4), scaleUpTime=1.0),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), y, 0.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_lower.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['duck', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, toonTrack)

def doPerformanceReview(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    cagePos = [Point3(suitPos.getX() - 3, 6, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=2.0),
            Parallel(
                cage.posInterval(0.75, Point3(suitPos.getX() - 3, 6, 0), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
            Wait(13.75),
            Func(MovieUtil.removeProp, cage)
        )

    cagePropTracks.append(cagePropTrack)
    soundTrack = getSoundTrack('ENC_cogfall_apart.ogg', node=suit)
    suitTrack = Sequence(Wait(2.0), ActorInterval(suit, 'ottoman-writing-start'),
                         Func(suit.setChatAbsolute,
                              "Well, go ahead and make yourself comfortable. I will be sitting here filing my paperwork.",
                              CFSpeech | CFTimeout), ActorInterval(suit, 'ottoman-writing-loop'),
                         ActorInterval(suit, 'ottoman-writing-loop'),
                         ActorInterval(suit, 'ottoman-writing-loop'), ActorInterval(suit, 'ottoman-writing-loop'),
                         ActorInterval(suit, 'ottoman-writing-stop'),
                         Func(suit.setChatAbsolute,
                              "Did you hear something?",
                              CFSpeech | CFTimeout),
                         ActorInterval(suit, 'ottoman-sit-loop')
                         , ActorInterval(suit, 'ottoman-sit-loop'), Parallel(explosionTrack, soundTrack, ActorInterval(suit, 'slip-forward', startTime=2.43),
                         Func(suit.setChatAbsolute,
                              "Well that's unfortunate, I'm off to complete my paperwork.",
                              CFSpeech | CFTimeout)), Func(suit.makeImmortal), Func(suit.setNeutralAnimation), Wait(2.0))
    return Parallel(suitTrack, cagePropTracks)

def doPerformanceReviewRevert(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    healSound = getSoundTrack('LB_toonup.ogg')
    suitTracks = Parallel()
    liftTracks = Parallel()
    for suit in battle.activeSuits:
        liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
        liftEffect.setPos(suit.getPos(battle))
        liftEffect.setZ(liftEffect.getZ() - 1.3)
        liftTracks.append(getPartTrack(liftEffect, 4, 4.0, [liftEffect, battle, 0], softStop=-1))
        suitTrack = Sequence()
        suitTrack.append(Wait(4))
        suitTrack.append(Func(suit.checkPerformanceReview))
        suitTracks.append(suitTrack)
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(battle.unSueSuit, suit))
        suitTracks.append(Sequence(Func(suit.makeNonImmortal), getSuitAnimTrack(attack, playRate=1.5), Func(suit.setNeutralAnimation)))
        suitTracks.append(Wait(6.5))
    posPoints = [Point3(.78, -1.89, -.17), VBase3(10, 250, -10)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = globalPropPool.getProp('shredder-paper')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, 0.75, VBase3(1, 1, 1),
                               scaleUpTime=0.25),
            Wait(0.95),
            Parallel(
                getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                LerpHprInterval(knife, 0.8, VBase3(0, -20, -20))),
            Parallel(LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                     Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4)
    return Parallel(suitTracks, soundTrack2, liftTracks, soundTrack, knifeTracks)

def doRedPenReview(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    BattleParticles.loadParticles()
    checkmark = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
    checkmark.setBillboardPointEye()
    checkmark2 = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
    checkmark2.setBillboardPointEye()
    checkmark3 = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
    checkmark3.setBillboardPointEye()
    checkmark4 = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
    checkmark4.setBillboardPointEye()
    checkmark5 = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
    checkmark5.setBillboardPointEye()
    suitTrack = getSuitTrack(attack)
    padPosPoints = [Point3(-0.25, 1.38, -0.08), VBase3(-19.078, -6.603, -171.594)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57, Point3(1.89, 1.89, 1.89))
    missPoint = lambda checkmark = checkmark, toon = toon: __toonMissPoint(checkmark, toon)
    missPoint2 = lambda checkmark2=checkmark2, toon=toon: __toonMissPoint(checkmark2, toon)
    missPoint3 = lambda checkmark3=checkmark3, toon=toon: __toonMissPoint(checkmark3, toon)
    missPoint4 = lambda checkmark4=checkmark4, toon=toon: __toonMissPoint(checkmark4, toon)
    missPoint5 = lambda checkmark5=checkmark5, toon=toon: __toonMissPoint(checkmark5, toon)
    pencilPosPoints = [Point3(-0.47, 1.08, 0.28), VBase3(21.045, 12.702, -176.374)]
    extraArgsForShowProp = [pencil, suit.getRightHand()]
    extraArgsForShowProp.extend(pencilPosPoints)
    pencilPropTrack = Sequence(Wait(0.5), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2), Func(battle.movie.needRestoreRenderProp, checkmark),
                               Func(checkmark.reparentTo, render), Func(checkmark.setScale, 1.6), Func(checkmark.setPosHpr, pencil, 0, 0, 0, 0, 0, 0),
                               Func(checkmark.setP, 0), Func(checkmark.setR, 0))
    pencilPropTrack.append(getPropThrowTrack(attack, checkmark, [__toonFacePoint(toon)], [missPoint]))
    pencilPropTrack.append(Func(MovieUtil.removeProp, checkmark))
    pencilPropTrack.append(Func(battle.movie.clearRenderProp, checkmark))
    pencilPropTrack.append(Wait(0.3))
    pencilPropTrack.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    #pencilPropTrack.append(Func(MovieUtil.removeProp, pencil))
    pencilPropTrack2 = Sequence(Wait(0.6), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2),
                               Func(battle.movie.needRestoreRenderProp, checkmark2),
                               Func(checkmark2.reparentTo, render), Func(checkmark2.setScale, 1.6), Func(checkmark2.setPosHpr, pencil, 0, 0, 0, 0, 0, 0),
                               Func(checkmark2.setP, 0), Func(checkmark2.setR, 0))
    pencilPropTrack2.append(getPropThrowTrack(attack, checkmark2, [__toonFacePoint(toon)], [missPoint2]))
    pencilPropTrack2.append(Func(MovieUtil.removeProp, checkmark2))
    pencilPropTrack2.append(Func(battle.movie.clearRenderProp, checkmark2))
    pencilPropTrack2.append(Wait(0.3))
    pencilPropTrack2.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    #pencilPropTrack2.append(Func(MovieUtil.removeProp, pencil))
    pencilPropTrack3 = Sequence(Wait(.7), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2),
                               Func(battle.movie.needRestoreRenderProp, checkmark3),
                               Func(checkmark3.reparentTo, render), Func(checkmark3.setScale, 1.6), Func(checkmark3.setPosHpr, pencil, 0, 0, 0, 0, 0, 0),
                               Func(checkmark3.setP, 0), Func(checkmark3.setR, 0))
    pencilPropTrack3.append(getPropThrowTrack(attack, checkmark3, [__toonFacePoint(toon)], [missPoint3]))
    pencilPropTrack3.append(Func(MovieUtil.removeProp, checkmark3))
    pencilPropTrack3.append(Func(battle.movie.clearRenderProp, checkmark3))
    pencilPropTrack3.append(Wait(0.3))
    pencilPropTrack3.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    #pencilPropTrack3.append(Func(MovieUtil.removeProp, pencil))
    pencilPropTrack4 = Sequence(Wait(.8), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2),
                               Func(battle.movie.needRestoreRenderProp, checkmark4),
                               Func(checkmark4.reparentTo, render), Func(checkmark4.setScale, 1.6), Func(checkmark4.setPosHpr, pencil, 0, 0, 0, 0, 0, 0),
                               Func(checkmark4.setP, 0), Func(checkmark4.setR, 0))
    pencilPropTrack4.append(getPropThrowTrack(attack, checkmark4, [__toonFacePoint(toon)], [missPoint4]))
    pencilPropTrack4.append(Func(MovieUtil.removeProp, checkmark4))
    pencilPropTrack4.append(Func(battle.movie.clearRenderProp, checkmark4))
    pencilPropTrack4.append(Wait(0.3))
    pencilPropTrack4.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    #pencilPropTrack4.append(Func(MovieUtil.removeProp, pencil))
    pencilPropTrack5 = Sequence(Wait(.9), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2),
                               Func(battle.movie.needRestoreRenderProp, checkmark5),
                               Func(checkmark5.reparentTo, render), Func(checkmark5.setScale, 1.6), Func(checkmark5.setPosHpr, pencil, 0, 0, 0, 0, 0, 0),
                               Func(checkmark5.setP, 0), Func(checkmark5.setR, 0))
    pencilPropTrack5.append(getPropThrowTrack(attack, checkmark5, [__toonFacePoint(toon)], [missPoint5]))
    pencilPropTrack5.append(Func(MovieUtil.removeProp, checkmark5))
    pencilPropTrack5.append(Func(battle.movie.clearRenderProp, checkmark5))
    pencilPropTrack5.append(Wait(0.3))
    pencilPropTrack5.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    pencilPropTrack5.append(Func(MovieUtil.removeProp, pencil))
    toonTrack = getToonTrack(attack, 3.4, ['slip-forward'], 2.4, ['sidestep'])
    soundTrack = Sequence(Wait(2.3), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_pen_only.ogg'), duration=0.9, node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_ding_only.ogg'), node=suit))
    return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, pencilPropTrack2, pencilPropTrack3, pencilPropTrack4, pencilPropTrack5, soundTrack)

def doShatteringClarity(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    resetPos, resetHpr = battle.getActorPosHpr(theSuit)
    sinkPos = theSuit.getPos(battle)
    dropPos = theSuit.getPos(battle)
    sinkPos2 = theSuit.getPos(battle)
    dropPos2 = theSuit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 16.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    oldcolor = render.getColorScale()
    suitHealTrack = Parallel()
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3, node=suit)
    soundTrack = getSoundTrack('SA_personal_trainer.ogg', delay=1)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    for suit in battle.activeSuits:
        if not suit.dna.name == 'crystal':
            suitHealTrack = Sequence(Wait(3.0), (Func(suit.checkCompensation)))
    moveTrack = Sequence(LerpPosInterval(theSuit, 0, sinkPos, other=battle), Wait(theSuit.getDuration('shot5')), LerpPosInterval(theSuit, 0, resetPos, other=battle), Func(theSuit.setPos, battle, resetPos))
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 2, (0, 0, 0, 0)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    toonTrack = getToonTracksCheat(attack, 4.0, ['cringe'], dodgeDelay=0.7,
                                         dodgeAnimNames=['neutral'])
    notifyTrack = Sequence(Wait(4.0), Func(toon.showHpTextNew, - int(dmg), text="CONFUSED!", colorCode=1))
    return Parallel(suitTrack, soundTrack2, notifyTrack, soundTrack, moveTrack, toonTrack,  suitHealTrack, lightingTrack)

def doFracturedLimits(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(1.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doRefractDamage(attack):
    suit = attack['suit']
    node = suit.getGeomNode().getChild(0)
    suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=.5, colorScale=(0, 1, 0.078, 1),
                                                                blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.5, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'))
    soundTrack = Sequence(getSoundTrack('SA_defense.ogg'))
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(2.0))
    makeShielding = Parallel(Func(suit.makeShielding))
    return Parallel(suitTrack, soundTrack, suitColorTrack, makeShielding)


def doPrismaticDistortion(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.2
    attackDelay = 1.2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = Parallel()
    allHeadTracks = Parallel()
    allChestTracks = Parallel()
    toonTracks2 = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            headParts = toon.getHeadParts()
            sprayEffects = BattleParticles.createParticleEffect('ReOrgSprayNew')
            BattleParticles.loadParticles()
            BattleParticles.setEffectTexture(sprayEffects, 'snow-particle',
                                             color=Vec4(random.random(), random.random(), random.random(), 1))
            partTrack = getPartTrack(sprayEffects, 0.5, 3.0, [sprayEffects, toon, 0], softStop=-1)
            partTracks.append(partTrack)
            toonTrack = Sequence()
            toonTracks2.append(toonTrack)
            print
            '***********headParts pos=', headParts[0].getPos()
            print
            '***********headParts hpr=', headParts[0].getHpr()
            headTracks = Parallel()
            for partNum in xrange(0, headParts.getNumPaths()):
                part = headParts.getPath(partNum)
                x = part.getX()
                y = part.getY()
                z = part.getZ()
                h = part.getH()
                p = part.getP()
                r = part.getR()
                headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)),
                                           LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                           LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)),
                                           LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                           LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)),
                                           LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)),
                                           LerpHprInterval(part, 0.25, VBase3(360, 0, 180)),
                                           LerpPosInterval(part, 0.25, Point3(x, y, z + 3.1)),
                                           LerpPosInterval(part, 0.1, Point3(x, y, z + 0.3)), Wait(0.1),
                                           LerpHprInterval(part, 0.35, VBase3(-745, 0, 180),
                                                           startHpr=VBase3(0, 0, 180)),
                                           LerpHprInterval(part, 0.5, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)),
                                           LerpPosInterval(part, 0.15, Point3(x, y, z + 1)),
                                           LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2),
                                           LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.1)))

            allHeadTracks.append(headTracks)

            def getChestTrack(part, attackDelay=attackDelay):
                origScale = part.getScale()
                return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1),
                                LerpHprInterval(part, 1.1, part.getHpr()))

            chestTracks = Parallel()
            arms = toon.findAllMatches('**/arms')
            sleeves = toon.findAllMatches('**/sleeves')
            hands = toon.findAllMatches('**/hands')
            print
            '*************arms hpr=', arms[0].getHpr()
            for partNum in xrange(0, arms.getNumPaths()):
                chestTracks.append(getChestTrack(arms.getPath(partNum)))
                chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
                chestTracks.append(getChestTrack(hands.getPath(partNum)))

            allChestTracks.append(chestTracks)

    damageAnims = [['neutral',
                    0.01,
                    0.01,
                    0.5], ['juggle',
                           0.01,
                           0.01,
                           1.48], ['think', 0.01, 2.28]]
    dodgeAnims = []
    dodgeAnims.append(['think',
                       0.01,
                       0,
                       0.6])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01,
                               dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    soundTrack = Sequence(Wait(1.0), SoundInterval(globalBattleSoundCache.getSound('SA_mumbo_jumbo.ogg'), node=suit))
    return Parallel(suitTrack, partTracks, soundTrack, toonTracks2, toonTracks, allHeadTracks, allChestTracks)

def doRefractDamageRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    knifeDelay = 2.0
    suitTrack = getSuitAnimTrack(attack)
    knifeTracks = Parallel()
    for i in xrange(120):
        knife = globalPropPool.getProp('dagger')
        knifePos = Point3(random.randrange(-10.0, 10.0), random.randrange(-10.0, -4.0), 10.0)
        landPos = Point3(knifePos.getX() - 3.0, knifePos.getY() - 3, -2.0)
        knifeTrack = Sequence(
            Wait(knifeDelay + 0.025 * i),
            Func(knife.reparentTo, battle),
            Func(knife.setPos, knifePos),
            Func(knife.lookAt, landPos),
            Func(knife.setScale, Point3(0.75)),
            LerpPosInterval(knife, 0.1, landPos),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
    damageAnims = [['slip-forward', 0.01, 0.4, 1.2],
     ['slip-forward', 0.01, 1.0]]
    dodgeAnims = [['duck', 1e-06, 0.8]]
    toonTracks = getToonTracks(attack, damageDelay=knifeDelay + 0.11, splicedDamageAnims=damageAnims, dodgeDelay=knifeDelay - 0.1, splicedDodgeAnims=dodgeAnims)
    soundTrack = Sequence(Wait(2.0), SoundInterval(globalBattleSoundCache.getSound('ttr_s_ene_bat_hostileTakeover.ogg'), node=suit))
    return Parallel(suitTrack, knifeTracks, soundTrack, toonTracks)

def doFracturedLimitsRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    sign = globalPropPool.getProp('smile')
    signPropTracks = Parallel()
    signPropAnimTracks = Parallel()
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        hitSuit = dmg > 0
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect('Smile')
        signPosPoints = [Point3(0.0, -0.42, -0.04), VBase3(105.715, 73.977, 65.932)]
        if hitSuit:
            hitPoint = lambda toon = toon: __toonFacePoint(toon)
        else:
            hitPoint = lambda particleEffect = particleEffect, toon = toon, suit = suit: __toonMissPoint(particleEffect, toon, parent=suit.getRightHand())
        signPropTrack = Sequence(Func(__showProp, sign, suit.getRightHand(), signPosPoints[0], signPosPoints[1]), LerpScaleInterval(sign, 0.5, Point3(0.001, .001, .001)), Wait(0.5), Func(battle.movie.needRestoreParticleEffect, particleEffect), Func(particleEffect.start, suit), Func(particleEffect.wrtReparentTo, render), LerpPosInterval(particleEffect, 1.0, pos=hitPoint), Func(particleEffect.cleanup), LerpScaleInterval(sign, 0.5, Point3(0, 0, 0)), Func(battle.movie.clearRestoreParticleEffect, particleEffect))
        signPropAnimTrack = ActorInterval(sign, 'smile', duration=2.5, startTime=1)
        signPropTracks.append(signPropTrack)
        signPropAnimTracks.append(signPropAnimTrack)
    toonTrack = getToonTracks(attack, 2.0, ['cringe'], 1.3, ['sidestep'])
    soundTrack = getSoundTrack('SA_razzle_dazzle.ogg', delay=0.8, node=suit)
    return Sequence(Parallel(suitTrack, signPropTracks, signPropAnimTracks, toonTrack, soundTrack), Func(MovieUtil.removeProp, sign))

def doTrapRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    explosionTracks = Parallel()
    notifyTracks = Parallel()
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        explosionTrack = Sequence()
        toonPos = toon.getPos(battle)
        explosionTrack.append(Wait(2.25))
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
        explode = []
        for i in xrange(0, 3):
            explode.append(globalPropPool.getProp('explosion'))
        explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
        explodePosPoints1 = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
        explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
        explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
        explodeTracks = Parallel()
        for i in xrange(0, 3):
            explodeTrack = Sequence()
            explodeTrack.append(Wait(2.25))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
            explodeTracks.append(explodeTrack)
        tnt = globalPropPool.getProp('tnt')
        tip = tnt.find('**/joint_attachEmitter')
        sparks = BattleParticles.createParticleEffect(file='tnt')
        tnt.sparksEffect = sparks
        posPoints = [Point3(-0.4109589, -0.0821917, -0.0821917), VBase3(-10.849315, 0, 113.42465753424653)]
        propTrack = Sequence(getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.25, Point3(0.7, 0.7, 0.7), scaleUpTime=0.25))
        propTrack.append(Func(sparks.start, tip))
        propTrack.append(Wait(1.5))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.1, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
        notifyTrack = Sequence(Wait(2.25), Func(toon.showHpTextNew, -int(dmg)))
        if dmg > 0:
            notifyTracks.append(notifyTrack)
            propTracks.append(propTrack)
            explosionTracks.append(explodeTracks)
            explosionTracks.append(explosionTrack)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    toonTrack = getToonTracksCheat(attack, 2.25, ['slip-forward'], 0.5, ['nothing'])
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.25)
    return Parallel(suitTrack, toonTrack, notifyTracks, soundTrack, propTracks, explosionTracks)

def doLureRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    billPropTracks = Parallel()
    notifyTracks = Parallel()
    soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(1.0))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        bill = globalPropPool.getProp('1dollar')
        billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
        billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(1.41, 1.41, 1.41))
        notifyTrack = Sequence(Wait(2.25), Func(toon.showHpTextNew, -int(dmg)))
        if dmg > 0:
            notifyTracks.append(notifyTrack)
            billPropTracks.append(billPropTrack)


    toonTrack = getToonTracksCheat(attack, 0.25, ['cringe'], 0.01, ['sidestep'])
    return Parallel(suitTrack, billPropTracks, notifyTracks, toonTrack, soundTrack)

def __showProp2(prop, parent, pos):
    prop.reparentTo(parent)
    prop.setPos(pos)

def __billboardProp(prop):
    scale = prop.getScale()
    prop.setBillboardPointWorld()
    prop.setScale(scale)

def doThrowRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    notifyTracks = Parallel()
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    for t in targets:
        toon = t['toon']
        splatName = 'splat-birthday-cake'
        splat = globalPropPool.getProp(splatName)
        splatShow = Func(__showProp2, splat, toon, Point3(0, 1, toon.getZ()))
        splatBillboard = Func(__billboardProp, splat)
        splatAnim = ActorInterval(splat, splatName)
        splatHide = Func(MovieUtil.removeProp, splat)
        dmg = t['hp']
        cake = globalPropPool.getProp('birthday-cake')
        cake.loop('birthday-cake')
        posPoints = [Point3(-0.3, 0, -0.25), VBase3(0, 180, 0.00)]
        propTrack = Sequence(
            getPropAppearTrack(cake, suit.getRightHand(), posPoints, 0.5, Point3(0.5082191780821917, 0.5082191780821917, 0.5082191780821917), scaleUpTime=0.5))
        propTrack.append(Wait(1.13))

        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, cake, [hitPoint], [missPoint], .25, parent=battle))
        propTrack.append(splatShow)
        propTrack.append(splatBillboard)
        propTrack.append(splatAnim)
        propTrack.append(splatHide)
        if dmg > 0:
            propTracks.append(propTrack)
            notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextNew, - int(dmg)))
            notifyTracks.append(notifyTrack)
    toonTrack = getToonTracksCheat(attack, 2.5, ['slip-backward'], 2.2, ['jump'])
    soundTrack = getSoundTrack('AA_cake.ogg', delay=2.5, node=suit)
    return Parallel(suitTrack, toonTrack, notifyTracks, soundTrack, propTracks)

def doOvertime(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetSuit = battle.activeSuits[ind]
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    battle = attack['battle']
    targetPos = targetSuit.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    battle = attack['battle']
    targetPos2 = toon.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    headsUp2 = Func(suit.setHpr, battle, origHpr)
    moveTrack = Sequence(LerpPosInterval(suit, suit.getDuration('walk'), sinkPos2, other=battle), Wait(suit.getDuration('speak')), LerpPosInterval(suit, suit.getDuration('walk'), dropPos, other=battle), Func(suit.setPos, battle, resetPos))
    suitTrack = Sequence(ActorInterval(suit, 'walk'), headsUp, getSuitAnimTrack(attack), ActorInterval(suit, 'walk'), headsUp2, Func(suit.setNeutralAnimation))
    selfDamageTrack = Sequence(Wait(suit.getDuration('walk') + 3), Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                "As you desire, Mr. Chairman.",
                                CFSpeech | CFTimeout),
                                                  Func(targetSuit.showHpTextNew, 0, text="+1 Attack!", colorCode=1), Func(targetSuit.makeExtraAttacks, targetSuit.getExtraAttacks() + 1)), Func(targetSuit.setNeutralAnimation))
    return Parallel(suitTrack, moveTrack, selfDamageTrack)

def doTotalMarketMeltdown(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    damageDelay = 1.7
    particleEffect = BattleParticles.createParticleEffect(file='heatwave2')
    waterfallEffect = BattleParticles.createParticleEffect(file='heatwaveWaterfall2')
    partTrack = getPartTrack(particleEffect, 1.0, 3.4, [particleEffect, suit, 0], softStop=-2.0)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.4, [waterfallEffect, suit, 0], softStop=-2.0)
    node = suit.getGeomNode().getChild(0)
    suitTrack = getSuitAnimTrackAttack(attack)
    suitTrack.append(Parallel(Func(suit.showHpTextNew, 0, text="+1 Attack!", colorCode=1), Func(suit.makeExtraAttacks, suit.getExtraAttacks() + 1)))
    dmg = attack['target'][0]['hp']
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()
    partTracks4 = Parallel()
    makeDamageDowns = Parallel()

    def changeColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    colorTracks = Parallel()
    for t in targets:
        toon = t['toon']
        makeDamageDown = Parallel(Func(toon.checkGagBoost, 50), Func(toon.makeGagBoost, 8), Func(toon.addGagBoostRounds, 3))
        makeDamageDowns.append(makeDamageDown)
        BattleParticles.loadParticles()
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
        flameDelay = 1.45
        flameDuration = 1.5
        flecksDelay = flameDelay + 0.8
        flecksDuration = flameDuration - 0.8
        if t['hp'] > 0:
            baseFlameTracks.append(getPartTrack(baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0]))
            flameTracks.append(getPartTrack(flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0]))
            flecksTracks.append(getPartTrack(flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0]))
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTracks.append(Sequence(
                Wait(1.5),
                Func(battle.movie.needRestoreColor),
                changeColor(headParts),
                changeColor(torsoParts),
                changeColor(legsParts),
                Wait(3.1),
                resetColor(headParts),
                resetColor(torsoParts),
                resetColor(legsParts),
                Func(battle.movie.clearRestoreColor)
            ))

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.7,
     0.62])
    damageAnims.append(['slip-forward',
     0.01,
     0.4,
     1.2])
    damageAnims.append(['slip-forward', 0.01, 1.0])
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=.5, node=suit)
    return Parallel(suitTrack, partTracks4, partTrack, makeDamageDowns, waterfallTrack, colorTracks, toonTracks, soundTrack, baseFlameTracks, flameTracks, flecksTracks)

def doTotalMarketMeltdown2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    damageDelay = 1.7
    particleEffect = BattleParticles.createParticleEffect(file='heatwave2')
    waterfallEffect = BattleParticles.createParticleEffect(file='heatwaveWaterfall2')
    partTrack = getPartTrack(particleEffect, 1.0, 3.4, [particleEffect, suit, 0], softStop=-2.0)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.4, [waterfallEffect, suit, 0], softStop=-2.0)
    node = suit.getGeomNode().getChild(0)
    suitTrack = getSuitAnimTrackAttack(attack)
    suitTrack.append(Parallel(Func(suit.showHpTextNew, 0, text="+1 Attack!", colorCode=1), Func(suit.makeExtraAttacks, suit.getExtraAttacks() + 1)))
    dmg = attack['target'][0]['hp']
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()
    partTracks4 = Parallel()
    makeDamageDowns = Parallel()

    def changeColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    colorTracks = Parallel()
    for t in targets:
        toon = t['toon']
        makeDamageDown = Parallel(Func(toon.checkGagBoost, 50), Func(toon.makeGagBoost, 7), Func(toon.addGagBoostRounds, 3))
        makeDamageDowns.append(makeDamageDown)
        BattleParticles.loadParticles()
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
        flameDelay = 1.45
        flameDuration = 1.5
        flecksDelay = flameDelay + 0.8
        flecksDuration = flameDuration - 0.8
        if t['hp'] > 0:
            baseFlameTracks.append(getPartTrack(baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0]))
            flameTracks.append(getPartTrack(flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0]))
            flecksTracks.append(getPartTrack(flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0]))
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            colorTracks.append(Sequence(
                Wait(1.5),
                Func(battle.movie.needRestoreColor),
                changeColor(headParts),
                changeColor(torsoParts),
                changeColor(legsParts),
                Wait(3.1),
                resetColor(headParts),
                resetColor(torsoParts),
                resetColor(legsParts),
                Func(battle.movie.clearRestoreColor)
            ))

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.7,
     0.62])
    damageAnims.append(['slip-forward',
     0.01,
     0.4,
     1.2])
    damageAnims.append(['slip-forward', 0.01, 1.0])
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=.5, node=suit)
    return Parallel(suitTrack, partTracks4, partTrack, makeDamageDowns, waterfallTrack, colorTracks, toonTracks, soundTrack, baseFlameTracks, flameTracks, flecksTracks)

def doTotalMarketMeltdownOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect(file='floodTheMarket')
    waterfallEffect = BattleParticles.createParticleEffect(file='floodTheMarketWaterfall')
    suitTrack = getSuitAnimTrackAttack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 3.4, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.4, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0, showDamageExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    suitTrack.append(Parallel(Func(suit.showHpTextNew, 0, text="+1 Attack!", colorCode=1), Func(suit.makeExtraAttacks, suit.getExtraAttacks() + 1)))
    makeDamageDowns = Parallel()
    if hitAtleastOneToon > 0:
        puddleCounter = 0
        for t in targets:
            toon = t['toon']
            makeDamageDown = Parallel(Func(toon.checkGagBoost, 50), Func(toon.makeGagBoost, 8), Func(toon.addGagBoostRounds, 3), Func(toon.makeGroupDamageDown), Func(toon.addGroupDamageDownRounds, 3))
            makeDamageDowns.append(makeDamageDown)
            if t['hp'] > 0:
                if puddleCounter == 0:
                    puddle = globalPropPool.getProp('quicksand')
                    puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
                    puddle.setHpr(Point3(120, 0, 0))
                    puddle.setScale(0.01)
                    puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
                if puddleCounter == 1:
                    puddle2 = globalPropPool.getProp('quicksand')
                    puddle2.setColor(Vec4(0.0, 0.0, 1.0, 1))
                    puddle2.setHpr(Point3(120, 0, 0))
                    puddle2.setScale(0.01)
                    puddleTrack1 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle2), Func(puddle2.reparentTo, battle), Func(puddle2.setPos, toon.getPos(battle)), LerpScaleInterval(puddle2, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle2.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle2), Func(battle.movie.clearRenderProp, puddle2))
                if puddleCounter == 2:
                    puddle3 = globalPropPool.getProp('quicksand')
                    puddle3.setColor(Vec4(0.0, 0.0, 1.0, 1))
                    puddle3.setHpr(Point3(120, 0, 0))
                    puddle3.setScale(0.01)
                    puddleTrack2 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle3), Func(puddle3.reparentTo, battle), Func(puddle3.setPos, toon.getPos(battle)), LerpScaleInterval(puddle3, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle3.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle3), Func(battle.movie.clearRenderProp, puddle3))
                if puddleCounter == 3:
                    puddle4 = globalPropPool.getProp('quicksand')
                    puddle4.setColor(Vec4(0.0, 0.0, 1.0, 1))
                    puddle4.setHpr(Point3(120, 0, 0))
                    puddle4.setScale(0.01)
                    puddleTrack3 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle4), Func(puddle4.reparentTo, battle), Func(puddle4.setPos, toon.getPos(battle)), LerpScaleInterval(puddle4, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle4.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle4), Func(battle.movie.clearRenderProp, puddle4))
                puddleCounter +=1
        if puddleCounter == 1:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, makeDamageDowns, puddleTrack, toonTracks)
        if puddleCounter == 2:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, makeDamageDowns, puddleTrack, puddleTrack1, toonTracks)
        if puddleCounter == 3:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, makeDamageDowns, puddleTrack, puddleTrack1,  puddleTrack2, toonTracks)
        if puddleCounter == 4:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, makeDamageDowns, puddleTrack, puddleTrack1,  puddleTrack2,  puddleTrack3, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, makeDamageDowns, toonTracks)

def doHostileLiquidation(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetSuit = battle.activeSuits[ind]
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = targetSuit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    battle = attack['battle']
    targetPos = targetSuit.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    battle = attack['battle']
    targetPos2 = toon.getPos(battle)
    hpTrack = Sequence(Wait(suit.getDuration('walk') + .5), Func(targetSuit.checkHeadRollerChairman, suit, battle))
    origPos, origHpr = battle.getActorPosHpr(suit)
    headsUp2 = Func(suit.setHpr, battle, origHpr)
    moveTrack = Sequence(LerpPosInterval(suit, suit.getDuration('walk'), sinkPos2, other=battle), Wait(suit.getDuration('sanction')), LerpPosInterval(suit, suit.getDuration('walk'), dropPos, other=battle), Func(suit.setPos, battle, resetPos))
    suitTrack = Sequence(ActorInterval(suit, 'walk'), headsUp, getSuitAnimTrack(attack), ActorInterval(suit, 'walk'), headsUp2, Func(suit.setNeutralAnimation))
    selfDamageTrack = Sequence(Wait(suit.getDuration('walk') + .5), Parallel(MovieUtil.createSuitWreckingDeathTrack(targetSuit, battle)))
    soundTrack = getSoundTrack('SA_haymaker.ogg', delay=suit.getDuration('walk') + .5)
    soundTrack1 = getSoundTrack('SA_sanction.ogg', delay=suit.getDuration('walk'), node=suit)
    return Parallel(suitTrack, hpTrack, moveTrack, selfDamageTrack, soundTrack, soundTrack1)

def doSnipe(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    explosionTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    suitTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        leftPosPoints = [Point3(0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
        explosionTrack = Sequence()
        explosionTrack.append(Wait(1.5))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        leftKnives = []
        rightKnives = []
        for i in xrange(0, 3):
            leftKnives.append(globalPropPool.getProp('dagger'))
            rightKnives.append(globalPropPool.getProp('dagger'))

        for i in xrange(0, 3):
            knifeDelay = 0.11
            leftTrack = Sequence()
            leftTrack.append(Wait(1.1))
            leftTrack.append(Wait(i * knifeDelay))
            leftTrack.append(
                getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                               hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                leftKnifeTracks.append(leftTrack)
            rightTrack = Sequence()
            rightTrack.append(Wait(1.1))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(
                getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                                hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                rightKnifeTracks.append(rightTrack)

        notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextNew, - int(dmg), text="SNIPED!", colorCode=4))
        #toonTrack = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
        soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=1.5, node=suit)
        suitTrack = Sequence(getSuitAnimTrackAttack(attack))
        suitTrack.append(Wait(2.0))
        if dmg > 0:
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            explosionTracks.append(explosionTrack)
            suitTracks.append(suitTrack)
            notifyTracks.append(notifyTrack)
    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                         dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, toonDamageTrack, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)

def setPosFromOther(dest, source, offset = Point3(0, 0, 0)):
    pos = render.getRelativePoint(source, offset)
    dest.setPos(pos)
    dest.reparentTo(render)

def __getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    pEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) == 3:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))

def doSoundRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    notifyTracks = Parallel()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    can = loader.loadModel('phase_5/models/props/megaphone')
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    suitTrack2 = Sequence(ActorInterval(suit, 'glower', endTime=1.5), Wait(3.0), ActorInterval(suit, 'glower', startTime=1.5), Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(3.0), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    toonTrack = getToonTrackCheat(attack, 4.0, ['cringe'], 0, ['nothing'])
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        notifyTrack = Sequence(Wait(4.0), Func(toon.showHpTextNew, -int(dmg)))
        if dmg > 0:
            notifyTracks.append(notifyTrack)
    return Parallel(suitTrack, toonTrack, notifyTracks, throwTrack, suitTrack2, sprayTrack)

def doDropRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    propTracks = Parallel()
    toonTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        piano = globalPropPool.getProp('piano')
        safe = globalPropPool.getProp('safe')
        boulder = globalPropPool.getProp('boulder')
        weight = globalPropPool.getProp('weight')
        toonPos = toon.getPos(battle)
        toonHpr = battle.getActorPosHpr(toon)
        y = toonPos.getY()
        propPos = Point3(toonPos.getX(), y, 30)
        soundTrack2 = getSoundTrack('AA_drop_piano.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack3 = getSoundTrack('AA_drop_boulder.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack4 = getSoundTrack('AA_drop_safe.ogg', delay=1.75, duration=2.0,  node=suit)
        soundTrack5 = getSoundTrack('AA_drop_bigweight.ogg', delay=1.75, duration=2.0, node=suit)
        propTrack = Sequence(Func(piano.reparentTo, battle),
        getPropAppearTrack(piano, parent=battle, posPoints=[propPos, VBase3(180, 90, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(3), scaleUpTime=1.5),
        LerpPosInterval(piano, 0.25, Point3(toonPos.getX(), y, 1)),
        LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 2)),
        LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
            Wait(1.5),
            LerpScaleInterval(piano, .25, MovieUtil.PNT3_ZERO)
        ))
        propTrack2 = Sequence(Func(safe.reparentTo, battle),
            getPropAppearTrack(safe, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(4.5), scaleUpTime=1.5),
            LerpPosInterval(safe, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(safe, .25, MovieUtil.PNT3_ZERO)
            ))
        propTrack3 = Sequence(Func(boulder.reparentTo, battle),
            getPropAppearTrack(boulder, parent=battle, posPoints=[propPos, VBase3(0, 90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2), scaleUpTime=1.5),
            LerpPosInterval(boulder, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(boulder, .25, MovieUtil.PNT3_ZERO)
            ))
        propTrack4 = Sequence(Func(weight.reparentTo, battle),
            getPropAppearTrack(weight, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(.75), scaleUpTime=1.5),
            LerpPosInterval(weight, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(weight, .25, MovieUtil.PNT3_ZERO)
            ))
        if dmg > 0:
            propTracks.append(random.choice((Parallel(propTrack, soundTrack2), Parallel(propTrack2, soundTrack4), Parallel(propTrack3, soundTrack3), Parallel(propTrack4, soundTrack5))))
        toonTrack = Sequence(
        Wait(1.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpTextNew,  - int(dmg)),
            #Func(__doDamageCheat, toon, dmg, t['died'])
        ),
        Wait(1.75),
        Parallel(
            Sequence(
                Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
        )
        if dmg > 0:
            toonTracks.append(toonTrack)
            smokeTracks.append(smokeTrack)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    toonDamageTrack = getToonTracksCheat(attack, 1.75, ['nothing'], 0, ['neutral'])
    return Parallel(suitTrack, toonDamageTrack, smokeTracks, toonTracks, soundTrack, propTracks)

def doZapRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrackAttack(attack), Wait(2.0))
    targets = attack['target']
    cagePropTracks = Parallel()
    notifyTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        cage = loader.loadModel('phase_5/models/props/lightning')
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        # cage.setH(90)
        # cage.setPosHpr(0, 0, 0, 180, 0, 0)
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        if dmg == 0:
            y -= 5
        cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 1, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0),
            Parallel(cagePosition),
            Parallel(
                cage.posInterval(0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.25),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
        if dmg > 0:
            cagePropTracks.append(cagePropTrack)
            smokeTracks.append(smokeTrack)
            notifyTrack = Sequence(Wait(1.0), Func(toon.showHpTextNew, - int(dmg)))
            notifyTracks.append(notifyTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracksCheat(attack, damageDelay=1, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['sidestep'], splicedDodgeAnims=[], showDamageExtraTime=0)
    return Parallel(suitTrack, cagePropTracks, notifyTracks, smokeTracks, toonTrack)

def doSquirtRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    posPoints = [Point3(-0.5, 0, -1), VBase3(0, 0, 0)]
    knifeTracks = Parallel()
    notifyTracks = Parallel()
    splashTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitTrack = getSuitTrack(attack, playRate=2)
        knife = globalPropPool.getProp('waterBalloon')
        splashdown = globalPropPool.getProp('splashdown')
        splashdown.setScale(1)
        #ta = TransparencyAttrib.make(TransparencyAttrib.MBinary)
        #splashdown.node().setAttrib(ta, 1)
        #splashdown.setBin('fixed', 130, 1)
        animDuration = splashdown.getDuration('splashdown')
        splashTrack = Sequence(Wait(4.0), Func(splashdown.reparentTo, toon), Func(splashdown.show), ActorInterval(splashdown, 'splashdown'), Wait(animDuration), Func(splashdown.hide))
        knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
        notifyTrack = Sequence(Wait(4.0), Func(toon.showHpTextNew, - int(dmg)))
        soundTrack = getSoundTrack('SA_watercooler_spray_only.ogg', delay=4.0, node=suit)
        if dmg > 0:
            knifeTracks.append(knifeTrack)
            notifyTracks.append(notifyTrack)
            splashTracks.append(splashTrack)
            suitTracks.append(suitTrack)
            soundTracks.append(soundTrack)
    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1,
                                   dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, knifeTracks, toonTracks, toonDamageTrack, soundTracks, splashTracks, notifyTracks)

# not chairman boardbot cheats

def doMinutesTaken(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Every escalation extends the record... Your permanent record now contains %s entries." %
                              int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg')
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doMinutesTakenContingency(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Every escalation extends the record... Your permanent record now contains %s entries." %
                              int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg')
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def __makeSanctionedNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText('REDLINED\nREDLINED\nREDLINED')
    tn.setAlign(TextNode.ACenter)
    tntop = hidden.attachNewNode('CancelledTop')
    tnpath = tntop.attachNewNode(tn)
    tnpath.setPosHpr(0, 0, 0, 0, 0, 0)
    tnpath.setScale(1)
    tnpath.setColor(0.7, 0, 0, 1)
    tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
    tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
    tnpath.setScale(1)
    return tntop

def doRedlinedClauseGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    notifyTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    toonTracks = Parallel()
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        suitTrack = getSuitAnimTrack(attack)
        soundTrack = getSoundTrack('SA_sanction.ogg', delay=.5, node=suit)
        notifyTrack = Sequence(Wait(0.8),  Func(toon.showHpTextNew, -int(dmg), text="REDLINED!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.makeCooldown), Func(toon.checkCooldownRounds, 2)))
        if dmg > 0:
            sanctioned = __makeSanctionedNodePath()
            missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
            propTrack = Sequence(
                Wait(0.5),
                Func(battle.movie.needRestoreRenderProp, sanctioned),
                Func(sanctioned.reparentTo, render),
                Func(sanctioned.setScale, 0.6),
                Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 80, 90),
                Func(sanctioned.setP, 0),
                Func(sanctioned.setR, 0),
                getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [__toonFacePoint(toon)], .25),
                Func(sanctioned.removeNode))
            origH = suit.getH(battle)

            # Calculate heading to toon
            origPos, origHpr = battle.getActorPosHpr(suit)
            origPos2 = suit.getPos(battle)
            suit.setPos(battle, origPos)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)

            # Restore original heading
            suit.setH(battle, origH)
            suit.setPos(battle, origPos2)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            propTracks.append(propTrack)
            suitTracks.append(Sequence(Parallel(suitTrack, LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle)), Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)), Func(suit.setNeutralAnimationDrop)))
            soundTracks.append(soundTrack)
            notifyTracks.append(notifyTrack)
    toonDamageTrack = getToonTracksCheat(attack, 0.8, ['conked'], 0, ['neutral'])
    return Parallel(suitTracks, toonTracks, toonDamageTrack, propTracks, soundTracks, notifyTracks)

def doRedlinedClause(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = __makeSanctionedNodePath()
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 0.6),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(sanctioned.removeNode)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0, ['duck'])
    notifyTrack = Sequence(Wait(0.8),  Func(toon.showHpTextNew, -int(dmg), text="REDLINED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.makeCooldown), Func(toon.checkCooldownRounds, 2)))
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doAuditCycle(attack):
    suit = attack['suit']
    toonTracks = Parallel()
    targets = attack['target']
    for t in targets:
        toon = t['toon']
        toonTrack = Parallel(Func(toon.makeGagBan))
        toonTracks.append(toonTrack)
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitType = getSuitBodyType(attack['suitName'])
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    return Parallel(suitTrack, calcPropTrack, toonTracks, suitTrack2, soundTrack)

def doRevisedFiling(attack):
    targets = attack['target']
    suit = attack['suit']
    battle = attack['battle']

    bookshelf = globalPropPool.getProp('LB_AttackShelf')

    throwSfx = loader.loadSfx('phase_5/audio/sfx/SA_hardball_impact_only.ogg')
    throwSfx.setVolume(.25)
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    def throwBook(attack, targets, bookshelf, throwSfx=None, end=False):
        hitTargets = [t for t in targets if t['hp'] > 0]

        if not hitTargets:
            return Sequence()

        neutralTrack = Parallel()
        notifyTrack = Parallel()
        throwTrack2 = Parallel()

        for t in hitTargets:
            dmg = t['hp']
            toon = t['toon']

            book = loader.loadModel('phase_14/models/props/lawbot-book')
            book.setPos(-1.5, 0, 3)
            book.hide()
            book.reparentTo(bookshelf)

            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()

            dustCloudTrack = Sequence(
                Func(dustCloud.reparentTo, toon),
                Func(dustCloud.setPos, Point3(0, -6, 3)),
                dustCloud.track,
                Func(dustCloud.removeNode),
                Wait(1.7)
            )

            throwTrack2.append(Sequence(
                Parallel(
                    Sequence(Wait(.1), SoundInterval(throwSfx, duration=.6)),
                    Sequence(
                        Wait(.2),
                        Func(book.show),
                        Func(book.wrtReparentTo, render),
                        book.posHprInterval(.5, (toon.getX(), toon.getY(), toon.getZ() + 3), (0, 720, 0))
                    )
                ),
                Parallel(dustCloudTrack, Func(book.removeNode))
            ))

            neutralTrack.append(Func(toon.loop, 'neutral'))

            notifyTrack.append(Sequence(
                Wait(0.7),
                Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1),
                Parallel(
                    Func(toon.makeVulnerable),
                    Func(toon.addVulnerabilityRounds, 3),
                    Func(toon.makeDamageUp),
                    Func(toon.addDamageUpRounds, 3)
                )
            ))

            currentBossHealth = -1
            for s in battle.suits:
                if s.dna.name == 'cdirector':
                    currentBossHealth = s.currHP

            if currentBossHealth > 0:
                notifyTrack.append(Parallel(
                    Func(toon.checkVulnerabilityUp, 50),
                    Func(toon.checkDamageUp, 50)
                ))
            else:
                notifyTrack.append(Parallel(
                    Func(toon.checkVulnerabilityUp, 25),
                    Func(toon.checkDamageUp, 25)
                ))

        throwTrack = Parallel(
            getToonTracksCheat(attack, .7, ['slip-forward'], 2.75, ['neutral']),
            neutralTrack
        )

        return Parallel(throwTrack, notifyTrack, throwTrack2)

    if hitAtleastOneToon > 0:
        suitTrack = Parallel(getSuitAnimTrack(attack), Sequence(Func(bookshelf.setH, bookshelf.getH() + 180), Func(bookshelf.wrtReparentTo, battle),
                         Sequence(
                             Wait(1.0), bookshelf.posInterval(0, (0, -125, -22)), bookshelf.hprInterval(0, (180, 0, 0)), bookshelf.scaleInterval(1.0, (3.5, 3.5, 3.5)), Sequence(
                                 Parallel(throwBook(attack, targets, bookshelf, throwSfx, end=True), ActorInterval(bookshelf, 'LB_AttackShelf')), Sequence(bookshelf.scaleInterval(.5, (.01, .01, .01)))),
                                 Sequence(Func(bookshelf.wrtReparentTo, suit), bookshelf.hprInterval(.5, (180, 0, 0)),

                             ),
                             Parallel(
                                 Sequence(Func(bookshelf.removeNode)),
                             ))))
    else:
        suitTrack = Parallel()
    soundTrack2 = loader.loadSfx('phase_5/audio/sfx/SA_bash.ogg')
    soundTrack = SoundInterval(soundTrack2)

    return Parallel(suitTrack, soundTrack)

def doMinutesTakenDamageBooks(attack):
    targets = attack['target']
    suit = attack['suit']
    battle = attack['battle']
    dmg = attack['target'][0]['hp']
    bookshelf = globalPropPool.getProp('LB_AttackShelf')

    throwSfx = loader.loadSfx('phase_5/audio/sfx/SA_hardball_impact_only.ogg')
    throwSfx.setVolume(.25)
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    def throwBook(attack, targets, bookshelf, throwSfx=None, end=False):
        hitTargets = [t for t in targets if t['hp'] > 0]

        if not hitTargets:
            return Sequence()

        neutralTrack = Parallel()
        notifyTrack = Parallel()
        throwTrack = Parallel()
        throwTrack2 = Parallel()

        for t in hitTargets:
            dmg = t['hp']
            toon = t['toon']

            book = globalPropPool.getProp('shredder-paper')
            book.setPos(-1.5, 0, 3)
            book.hide()
            book.reparentTo(bookshelf)
            book.setScale(.5)

            dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
            dustCloud.setBillboardAxis(2.0)
            dustCloud.setZ(3)
            dustCloud.setScale(0.4)
            dustCloud.createTrack()

            dustCloudTrack = Sequence(
                Func(dustCloud.reparentTo, toon),
                Func(dustCloud.setPos, Point3(0, -6, 3)),
                dustCloud.track,
                Func(dustCloud.removeNode),
                Wait(1.7)
            )

            throwTrack2.append(Sequence(
                Parallel(
                    Sequence(Wait(.1), SoundInterval(throwSfx, duration=.6)),
                    Sequence(
                        Wait(.2),
                        Func(book.show),
                        Func(book.wrtReparentTo, render),
                        book.posHprInterval(.5, (toon.getX(), toon.getY(), toon.getZ() + 3), (0, 720, 0))
                    )
                ),
                Parallel(dustCloudTrack, Func(book.removeNode))
            ))

            neutralTrack.append(Func(toon.loop, 'neutral'))

            notifyTrack.append(Sequence(
                Wait(0.7),
                Func(toon.showHpTextNew, -int(dmg)),
                Func(__doDamageCheat, toon, int(dmg), t['died'])
            ))

            throwTrack.append(Parallel(
            Sequence(Wait(.7), ActorInterval(toon, 'slip-forward'), Func(toon.loop, 'neutral'))),
        )
        if end == True:
            return Parallel(throwTrack, notifyTrack, throwTrack2)
        else:
            return Parallel(throwTrack, throwTrack2)

    if hitAtleastOneToon > 0:
        bookThrows = []

        numBooks = int(math.ceil(dmg / 5))

        for i in xrange(numBooks):
            bookThrows.append(
                Sequence(
                    Wait(i * 0.15),
                    throwBook(
                        attack,
                        targets,
                        bookshelf,
                        throwSfx,
                        end=(i == numBooks - 1)
                    )
                )
            )

        throwTrack = Parallel(*bookThrows)

        suitTrack = Parallel(Sequence(Func(bookshelf.setH, bookshelf.getH() + 180), Func(bookshelf.wrtReparentTo, battle),
                         Sequence(
                             Wait(1.0), bookshelf.posInterval(0, (0, -125, -22)), bookshelf.hprInterval(0, (180, 0, 0)), bookshelf.scaleInterval(1.0, (3.5, 3.5, 3.5)), Sequence(
                                 Parallel(Parallel(throwTrack), ActorInterval(bookshelf, 'LB_AttackShelf', playRate=.5)), Sequence(bookshelf.scaleInterval(.5, (.01, .01, .01)))),
                                 Sequence(Func(bookshelf.wrtReparentTo, suit), bookshelf.hprInterval(.5, (180, 0, 0)),

                             ),
                             Parallel(
                                 Sequence(Func(bookshelf.removeNode)),
                             ))))
    else:
        suitTrack = Parallel()

    return Parallel(suitTrack)

def doPermanentRecordAuditBanned(attack):
    targets = attack['target']
    suit = attack['suit']
    battle = attack['battle']

    bookshelf = globalPropPool.getProp('LB_AttackShelf')
    paper = globalPropPool.getProp('lawbook')
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    splatName = 'dust'
    splat = globalPropPool.getProp('dust')
    explode = globalPropPool.getProp('dust')
    explode.setTwoSided(True)
    propTracks = Parallel()
    explode.setBillboardPointWorld(2)
    explodeTrack = Sequence(Wait(2.7))
    
    soundTrack = Sequence(Wait(2.7), getSoundTrack('LB_evidence_miss.ogg', node=suit))
    explodeTrack.append(Parallel(
        getPropAppearTrack(explode, bookshelf, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0)))
    explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
    propTrack = Sequence()
    propTrack.append(Parallel(explodeTrack, soundTrack))
    propTracks.append(propTrack)
    posPoints = [Point3(-0.5, 0, 0), VBase3(0, 0, 180)]
    scale = Point3(2.25, 2.25, 2.25)
    suitTrack = Parallel(Sequence(Func(bookshelf.setH, bookshelf.getH() + 180), Func(bookshelf.wrtReparentTo, battle),
                         Sequence(bookshelf.posInterval(0, (0, -125, -22)), bookshelf.hprInterval(0, (180, 0, 0)), bookshelf.scaleInterval(0.0, (3.5, 3.5, 3.5)), 
                             Parallel(getSuitAnimTrack(attack, playRate=1.5), Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0, scale, scaleUpTime=0.6), Wait(1.5),
                                Parallel(getSoundTrack('SA_hardball_impact_only.ogg'), getThrowTrack(paper, [bookshelf.getX(), bookshelf.getY(), bookshelf.getZ()], duration=0.75, parent=bookshelf, gravity=-100)), Func(paper.removeNode))), Wait(1),
                                 Sequence(bookshelf.scaleInterval(.5, (.01, .01, .01)))),
                                 Sequence(Func(bookshelf.wrtReparentTo, suit), bookshelf.hprInterval(.5, (180, 0, 0)),

                             ),
                             Parallel(
                                 Sequence(Func(bookshelf.removeNode)),
                             )))

    return Parallel(suitTrack, propTracks)

def doPermanentRecordAudit(attack):
    targets = attack['target']
    suit = attack['suit']
    battle = attack['battle']

    bookshelf = globalPropPool.getProp('LB_AttackShelf')
    paper = globalPropPool.getProp('shredder-paper')
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    splatName = 'dust'
    splat = globalPropPool.getProp('dust')
    explode = globalPropPool.getProp('dust')
    explode.setTwoSided(True)
    propTracks = Parallel()
    explode.setBillboardPointWorld(2)
    explodeTrack = Sequence(Wait(2.7))
    
    soundTrack = Sequence(Wait(2.7), getSoundTrack('LB_evidence_miss.ogg', node=suit))
    explodeTrack.append(Parallel(
        getPropAppearTrack(explode, bookshelf, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0)))
    explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
    propTrack = Sequence()
    propTrack.append(Parallel(explodeTrack, soundTrack))
    propTracks.append(propTrack)
    posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
    scale = Point3(1.2, 1.2, 1.2)
    suitTrack = Parallel(Sequence(Func(bookshelf.setH, bookshelf.getH() + 180), Func(bookshelf.wrtReparentTo, battle),
                         Sequence(
                             bookshelf.posInterval(0, (0, -125, -22)), bookshelf.hprInterval(0, (180, 0, 0)), bookshelf.scaleInterval(0.0, (3.5, 3.5, 3.5)), 
                             Parallel(getSuitAnimTrack(attack, playRate=1.5), Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25), Wait(0.95),
                                Parallel(getSoundTrack('SA_hardball_impact_only.ogg'), getThrowTrack(paper, [bookshelf.getX(), bookshelf.getY(), bookshelf.getZ()], duration=0.75, parent=bookshelf, gravity=-100)), Func(paper.removeNode))), Wait(1),
                                 Sequence(bookshelf.scaleInterval(.5, (.01, .01, .01)))),
                                 Sequence(Func(bookshelf.wrtReparentTo, suit), bookshelf.hprInterval(.5, (180, 0, 0)),

                             ),
                             Parallel(
                                 Sequence(Func(bookshelf.removeNode)),
                             )))

    return Parallel(suitTrack, propTracks)

def doMinutesTakenDamage(attack):
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitAnimTrack(attack)
    clockPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        clock = globalPropPool.getProp('clock')
        hourHand = clock.find('**/hour_hand')
        minuteHand = clock.find('**/minute_hand')
        x, y, z = toon.getPos(battle)
        clockPosPoints = [Point3(x, y, z + 0.1), VBase3(toon.getH(), 90, 0)]
        clockPropTrack = Sequence(
            getPropAppearTrack(clock, battle, clockPosPoints, 0.0, scaleUpPoint=Point3(0.75, 0.01, 0.75), scaleUpTime=1.0),
            Parallel(
                LerpHprInterval(minuteHand, 3.0, VBase3(0, 0, -1800)),
                LerpHprInterval(hourHand, 3.0, VBase3(0, 0, -150))
            ),
            Func(base.playSfx, globalBattleSoundCache.getSound('telephone_ring.ogg'), node=clock),
            Wait(0.4),
            LerpColorScaleInterval(clock, 1.0, Vec4(0.0, 0.0, 0.0, 1.0)),
            Wait(0.3 if t['hp'] == 0 else 3.9),
            LerpFunctionInterval(clock.setAlphaScale, duration=0.8, fromData=1, toData=0),
            Func(clock.removeNode)
        )
        clockPropTracks.append(clockPropTrack)

    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=5.1, splicedDamageAnims=damageAnims, dodgeDelay=6.05, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('LB_bell.ogg')
    return Parallel(suitTrack, clockPropTracks, soundTrack, toonTracks)

def doPaperTrail(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    explode = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(2.25))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(Wait(2.25))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    dmg = target[0]['hp']
    tnt = globalPropPool.getProp('shredder-paper')
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
    propTrack = Sequence(getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.75, Point3(1.2, 1.2, 1.2), scaleUpTime=0.25))
    propTrack.append(Wait(.95))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
    toonTrack = getToonTrackCheat(attack, 2.2, ['slip-forward'], 3.4, ['struggle'])
   # toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg), 2.5, ['slip-forward'])
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.25)
    notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextNew, - int(dmg), text="CONFUSED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.makeConfused), Func(toon.addConfusedRounds, 2)))
    leftPosPoints = [Point3(0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
    rightPosPoints = [Point3(-0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    leftKnives = []
    rightKnives = []
    for i in xrange(0, 5):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))

    for i in xrange(0, 5):
        knifeDelay = 0.07
        leftTrack = Sequence()
        leftTrack.append(Wait(2.0))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(
                getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                               hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(2.0))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(
                getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                                hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)
    return Parallel(explodeTracks, suitTrack, toonTrack, soundTrack, propTrack, notifyTrack, explosionTrack)

def doPhantomEntryDamage(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    notifyTracks = Sequence()
    notifyTrack = Sequence(theSuit.makeDamageInterval(battle, 1500))
    notifyTrack.append(Parallel(Func(theSuit.makeUnDamageReduction)))
    cameraTrack = Wait(5.0)
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    return Sequence(notifyTracks)

def doPhantomEntrySacrifice(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    notifyTracks = Sequence(Wait(theSuit.getDuration('mplayer-kneel-into')))
    oldPos, oldHpr = battle.getActorPosHpr(theSuit)
    def getDustCloudIval(oldPos=oldPos):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(0.4)
        dustCloud.createTrack()
        dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
        return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, battle, oldPos + (0, 0, theSuit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                        name='dustCloadIval')
    suitTrack = Sequence(ActorInterval(theSuit, 'mplayer-kneel-into'), Func(theSuit.cleanupAllBattleEffects), Parallel(Func(getDustCloudIval().start), LerpColorScaleInterval(theSuit, 0, (0, 0, 0, 0)), Func(theSuit.hide), Wait(3.0)))
    for suit in battle.activeSuits:
        if suit.dna.name == 'rkeeper':
            notifyTracks.append(Sequence(Func(theSuit.checkPhantomEntrySacrifice, suit)))
            notifyTracks.append(Parallel(Func(suit.makeUnDamageReduction)))
    return Parallel(suitTrack, notifyTracks)

def doPhantomEntrySpawn(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    notifyTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25), Wait(2.0))
    notifyTrack.append(Parallel(Func(theSuit.makeDamageReduction)))
    notifyTracks.append(Parallel(notifyTrack))
    soundTrack2 = getSoundTrack('SA_disruptive_advertisement.ogg')
    return Parallel(soundTrack2, notifyTracks)

def doContingencyClauseOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    squishTracks = Parallel()
    safeTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        toonTrack = Parallel(Func(toon.makeGagBan))
        toonTracks.append(toonTrack)
        safe = loader.loadModel('phase_10/models/cashbotHQ/CashBotSafe')
        safe.setHpr(90, 0, 90)
        safe.setPos(-0.3468208092485554, -0.6936416184971108, -0.43352601156069426)
        safe.setScale(.000001)
        safe.find('**/SafeShadow1').hide()
        toonScale = toon.find('**/actorGeom').getScale()
        appearSfx = loader.loadSfx('phase_5/audio/sfx/SA_watercooler_appear_only.ogg')
        throwSfx = loader.loadSfx('phase_5/audio/sfx/SA_hardball_impact_only.ogg')
        landSfx = loader.loadSfx('phase_5/audio/sfx/AA_drop_bigweight_miss.ogg')
        landSfx.setVolume(.420)
        squishTrack = toon.find('**/actorGeom').scaleInterval(.05, (1, 1, .01))
        safeTrack = Parallel(
            Sequence(Sequence(
                Wait(1.1), Func(safe.reparentTo, suit.getRightHand()),
                Parallel(
                    safe.scaleInterval(.25, (.075, .075, .075)), SoundInterval(appearSfx, duration=.25)
                ),
                Wait(1.1), Func(safe.wrtReparentTo, render),
                Parallel(safe.scaleInterval(.25, (.35, .35, .35)),
                    safe.hprInterval(.9, (0, 360, 0)), SoundInterval(throwSfx, duration=.7),
                    ProjectileInterval(safe, duration=.9, endPos=(toon.getPos()), gravityMult=5.0),
                    Sequence(Wait(.85), Func(landSfx.play), Func(safe.find('**/SafeShadow1').show), squishTrack)
                ),
                Func(safe.wrtReparentTo, toon),
                safe.posInterval(.69, (safe.getX(), safe.getY() - 10, 0), blendType='easeOut'),Wait(.25), Func(safe.wrtReparentTo, render),
                Parallel(
                    Sequence(safe.scaleInterval(.5, (.01, .01, .01)), Func(safe.removeNode)),
                    Parallel(toon.find('**/actorGeom').scaleInterval(.5, (toonScale)), getSoundTrack('toon_decompress.ogg'), ActorInterval(toon, 'jump'))
                )
            )
        ))
        safeTracks.append(safeTrack)

    suitTrack = Parallel(getSuitAnimTrackAttack(attack, playRate=1.25))
    toonTrack = getToonTracksCheat(attack, 4.5, ['jump'], 4.5, ['jump'])

    return Parallel(suitTrack, safeTracks, toonTracks, squishTracks, toonTrack)

def doShadowToon(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    hp = target[0]['hp']
    oldPos, oldHpr = battle.getActorPosHpr(suit)
    toonPos = toon.getPos(battle)
    newPos = oldPos + Point3(0, 5, 0)
    tPieLeavesHand = 2.7
    tPieHitsSuit = 3.0
    tSuitDodges = 2.45
    ratioMissToHit = 1.5

    def createEvilToon(toon = toon, oldPos = oldPos):
        evilToon = Toon.Toon()
        style = toon.style.clone()
        evilToon.setDNA(style)
        evilToon.hat = toon.getHat()
        evilToon.glasses = toon.getGlasses()
        evilToon.backpack = toon.getBackpack()
        evilToon.shoes = toon.getShoes()
        evilToon.generateToonAccessories()
        evilToon.setColorScale(0, 0, 0, 1)
        evilToon.setPos(battle, oldPos)
        evilToon.setHpr(battle, oldHpr)
        return evilToon

    evilToon = createEvilToon()
    evilToon.loop('neutral')

    def getDustCloudIval(evilToon = evilToon, oldPos = oldPos):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(0.4)
        dustCloud.createTrack()
        dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
        return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, battle, oldPos + (0, 0, evilToon.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                        name='dustCloadIval')

    suitTrack = Sequence(
        Parallel(
            LerpPosHprInterval(suit, duration=1.0, pos=(newPos), hpr=(180, 0, 0), other=battle),
            ActorInterval(suit, 'walk', loop=1, playRate=-1, duration=1.0)),
        Parallel(
            Sequence(
                getSuitAnimTrack(attack),
                Func(suit.setNeutralAnimationDrop)),
            Sequence(
                Wait(1.35),
                Func(getDustCloudIval().start),
                Wait(0.5),
                Func(evilToon.addActive),
                Func(evilToon.reparentTo, render)
            ),
        ),
    )
    pieName = 'creampie'
    pie = globalPropPool.getProp(pieName)
    pieType = globalPropPool.getPropType(pieName)
    pie2 = MovieUtil.copyProp(pie)
    pies = [pie, pie2]
    for p in pies:
        p.setColorScale(0, 0, 0, 1)
    hands = evilToon.getRightHands()
    splatName = 'splat-' + pieName
    splat = globalPropPool.getProp(splatName)
    splatType = globalPropPool.getPropType(splatName)
    splat.setColorScale(0, 0, 0, 1)
    evilToonTrack = Sequence()
    toonFace = Func(evilToon.headsUp, battle, toonPos)
    evilToonTrack.append(toonFace)
    evilToonTrack.append(ActorInterval(evilToon, 'throw'))
    evilToonTrack.append(Func(evilToon.loop, 'neutral'))
    evilToonTrack.append(Func(getDustCloudIval().start))
    evilToonTrack.append(Wait(0.5))
    evilToonTrack.append(Func(evilToon.reparentTo, hidden))
    evilToonTrack.append(Sequence(Func(evilToon.removeActive), Func(evilToon.cleanup), Func(evilToon.removeNode)))

    hitToon = hp > 0

    pieShow = Func(MovieUtil.showProps, pies, hands)
    pieAnim = Func(__animProp, pies, pieName, pieType)
    pieScale1 = LerpScaleInterval(pie, 1.0, pie.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    pieScale2 = LerpScaleInterval(pie2, 1.0, pie2.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    pieScale = Parallel(pieScale1, pieScale2)
    piePreflight = Func(__propPreflight, pies, toon, evilToon, battle)
    pieTrack = Sequence(pieShow, pieAnim, pieScale, Func(battle.movie.needRestoreRenderProp, pies[0]), Wait(tPieLeavesHand - 1.0), piePreflight)
    soundTrack = __getSoundTrack(0, hitToon, tPieLeavesHand, evilToon)

    if hitToon:
        pieFly = LerpPosInterval(pie, tPieHitsSuit - tPieLeavesHand, pos=MovieUtil.avatarFacePoint(toon, other=battle), other=battle)
        pieHide = Func(MovieUtil.removeProps, pies)
        splatShow = Func(__showProp, splat, toon, Point3(0, 0, toon.getHeight()))
        splatBillboard = Func(__billboardProp, splat)
        splatAnim = ActorInterval(splat, splatName)
        splatHide = Func(MovieUtil.removeProp, splat)
        pieTrack.append(pieFly)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
        pieTrack.append(splatShow)
        pieTrack.append(splatBillboard)
        pieTrack.append(splatAnim)
        pieTrack.append(splatHide)
    else:
        missDict = {}
        suitPoint = __suitMissPoint(toon, other=battle)
        piePreMiss = Func(__piePreMiss, missDict, pie, suitPoint, battle)
        pieMiss = LerpFunctionInterval(__pieMissLerpCallback, extraArgs=[missDict], duration=(tPieHitsSuit - tPieLeavesHand) * ratioMissToHit)
        pieHide = Func(MovieUtil.removeProps, pies)
        pieTrack.append(piePreMiss)
        pieTrack.append(pieMiss)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveUp = Sequence(Parallel(LerpPosHprInterval(suit, duration=1.0, pos=(oldPos), hpr=(resetHpr), other=battle), ActorInterval(suit, 'walk', loop=1, duration=1.0)),
                      Func(suit.setNeutralAnimationDrop))
    notifyTrack = Sequence(Wait(tPieHitsSuit), Func(toon.showHpTextNew,  - int(hp), "DAMAGE DEBUFF!", colorCode=1))
    currentBossHealth = -1
    for s in battle.suits:
        if s.dna.name == 'cdirector':
            currentBossHealth = s.currHP
    if currentBossHealth > 0:
        notifyTrack.append(Parallel(Func(toon.checkDamageDown, 75)))
    else:
        notifyTrack.append(Parallel(Func(toon.checkDamageDown, 50)))
    notifyTrack.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 2)))
    toonTrack = getToonTrackCheat(attack, tPieHitsSuit, ['slip-backward'], tSuitDodges, ['sidestep'])
    return Sequence(suitTrack, Parallel(evilToonTrack, pieTrack, notifyTrack, soundTrack, toonTrack), moveUp)

def doContingencyClauseRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    propTracks = Parallel()
    toonTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        piano = globalPropPool.getProp('piano')
        safe = globalPropPool.getProp('safe')
        boulder = globalPropPool.getProp('boulder')
        weight = globalPropPool.getProp('weight')
        toonPos = toon.getPos(battle)
        toonHpr = battle.getActorPosHpr(toon)
        y = toonPos.getY()
        propPos = Point3(toonPos.getX(), y, 30)
        soundTrack2 = getSoundTrack('AA_drop_piano.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack3 = getSoundTrack('AA_drop_boulder.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack4 = getSoundTrack('AA_drop_safe.ogg', delay=1.75, duration=2.0,  node=suit)
        soundTrack5 = getSoundTrack('AA_drop_bigweight.ogg', delay=1.75, duration=2.0, node=suit)
        propTrack = Sequence(Func(piano.reparentTo, battle),
        getPropAppearTrack(piano, parent=battle, posPoints=[propPos, VBase3(180, 90, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(3), scaleUpTime=1.5),
        LerpPosInterval(piano, 0.25, Point3(toonPos.getX(), y, 1)),
        LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 2)),
        LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
            Wait(1.5),
            LerpScaleInterval(piano, .25, MovieUtil.PNT3_ZERO)
        ))
        propTrack2 = Sequence(Func(safe.reparentTo, battle),
            getPropAppearTrack(safe, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(4.5), scaleUpTime=1.5),
            LerpPosInterval(safe, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(safe, .25, MovieUtil.PNT3_ZERO), Func(safe.removeNode)
            ))
        propTrack3 = Sequence(Func(boulder.reparentTo, battle),
            getPropAppearTrack(boulder, parent=battle, posPoints=[propPos, VBase3(0, 90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2), scaleUpTime=1.5),
            LerpPosInterval(boulder, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(boulder, .25, MovieUtil.PNT3_ZERO)
            ))
        propTrack4 = Sequence(Func(weight.reparentTo, battle),
            getPropAppearTrack(weight, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(.75), scaleUpTime=1.5),
            LerpPosInterval(weight, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(weight, .25, MovieUtil.PNT3_ZERO)
            ))
        propTracks.append(Parallel(propTrack2, soundTrack4))
        toonTrack = Sequence(
        Wait(1.75),
        Parallel(
            Func(toon.enterFlattened),
            #Func(__doDamageCheat, toon, dmg, t['died'])
        ),
        Wait(1.75),
        Parallel(
            Sequence(
                Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
        )
        toonTracks.append(toonTrack)
        smokeTracks.append(smokeTrack)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    toonDamageTrack = getToonTracksCheat(attack, 1.75, ['nothing'], 0, ['neutral'])
    return Parallel(suitTrack, toonDamageTrack, smokeTracks, toonTracks, soundTrack, propTracks)

hitSoundFiles = ('AA_tart_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_wholepie_only.ogg', 'AA_wholepie_only.ogg')

def __propPreflight(props, suit, toon, battle):
    prop = props[0]
    toon.update(0)
    prop.wrtReparentTo(battle)
    props[1].reparentTo(hidden)
    for ci in range(prop.getNumChildren()):
        prop.getChild(ci).setHpr(0, -90, 0)

    targetPnt = MovieUtil.avatarFacePoint(suit, other=battle)
    prop.lookAt(targetPnt)

def __getSoundTrack(level, hitSuit, tPieLeavesHand, node = None):
    throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    throwTrack = Sequence(Wait(2.6), SoundInterval(throwSound, node=node))
    if hitSuit:
        hitSound = globalBattleSoundCache.getSound('AA_wholepie_only.ogg')
        hitTrack = Sequence(Wait(tPieLeavesHand), SoundInterval(hitSound, node=node))
        return Parallel(throwTrack, hitTrack)
    else:
        return throwTrack

def doMissedPayment(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    soundTracks = Parallel()
    toonTracks = Parallel()
    notifyTracks = Parallel()
    billPropTracks = Parallel()
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    if hitAtleastOneToon > 0:
        soundTracks = Parallel(SoundInterval(globalBattleSoundCache.getSound('AA_drop_safe_miss.ogg')))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        bill = loader.loadModel('phase_4/models/accessories/bosses/backpack_gatekeeper')
        billPosPoints = [Point3(-0.9985528219971052, 0.21707670043415206, -1.0853835021707674), VBase3(-90, -45, 0)]
        billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.25, 1.0, scaleUpPoint=Point3(1.15, 1.15, 1.15))
        suitTrack = Parallel(getSuitAnimTrack(attack))
        notifyTrack = Sequence(Wait(0.52), Func(toon.showHpTextNew, 0, text="NO DEFENSE!", colorCode=1), Func(toon.makeNoDodge), Func(toon.addNoDodgeRounds, 2), ActorInterval(toon, 'cringe'), Func(toon.loop, 'neutral'))
        notifyTrack.append(Parallel(Func(toon.makeDamageUp), Func(toon.addDamageUpRounds, 2)))
        notifyTrack.append(Parallel(Func(toon.checkDamageUp, 10)))
        if dmg > 0:
            origH = suit.getH(battle)

            # Calculate heading to toon
            origPos, origHpr = battle.getActorPosHpr(suit)
            origPos2 = suit.getPos(battle)
            suit.setPos(battle, origPos)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)

            # Restore original heading
            suit.setH(battle, origH)
            suit.setPos(battle, origPos2)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            suitTrack.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'pickpocket'),
                                      Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                      Func(suit.setNeutralAnimationDrop), Wait(1.0)))
            billPropTracks.append(billPropTrack)
            suitTracks.append(suitTrack)
            notifyTracks.append(notifyTrack)
    return Parallel(suitTracks, billPropTracks, soundTracks, toonTracks, notifyTracks)

def doMissedPaymentNOTHINGN(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    bill = loader.loadModel('phase_3.5/models/props/jellybean4')
    bill.setH(0)
    bill.setColor(1,0.9,0)
    glow = loader.loadModel("phase_3.5/models/props/glow.bam")
    glow.reparentTo(bill)
    glow.setScale(0.5)
    glow.setPos(0,0,0)
    glow.setColorScale(Vec4(1, 0.9, 0, 0.3))
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(1.0))
    billPosPoints = [Point3(-0.21707670043415206, 0.30390738060781786, -0.4775687409551388), VBase3(-301.64978292329954, 0, 0)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(2.0, 2.0, 2.0))
    toonTrack = getToonTrackCheat(attack, 0.25, ['cringe'], 0.01, ['sidestep'])
    glowTrack = Sequence()
    glowTrack.append(Wait(2.0))
    glowTrack.append(Func(glow.hide))
    glowTrack.append(Func(glow.removeNode))
    notifyTrack = Sequence(Wait(0.25), Func(toon.showHpTextNew, - int(dmg)))
    multiTrackList = Parallel(suitTrack, notifyTrack, toonTrack, glowTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doForecastCollapse(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']

    selfDamageTracks = Parallel()
    for s in battle.activeSuits:
        if s.getManager() and s.dna.name != 'cdirector':
            targetSuit = s
            selfDamageTrack = Sequence(
                Wait(4.0),
                Parallel(
                    ActorInterval(s, 'mob-mentality'),
                    Func(s.setChatAbsolute, "I won't let you down, Ma'am.", CFSpeech | CFTimeout),
                    Func(s.showHpTextNew, 0, text="+40% Damage!", colorCode=1)
                ),
                Func(s.setNeutralAnimationDrop),
                Func(suit.checkExtraAbilities, 1),
                Func(s.makeDamageUp),
                Func(s.checkDamageUp, 40)
            )
            selfDamageTracks.append(selfDamageTrack)

    origPos, origHpr = battle.getActorPosHpr(suit)
    origPos2 = suit.getPos(battle)

    walkDur = suit.getDuration('walk')

    walkOutPos = Point3(origPos)
    walkOutPos.setY(walkOutPos.getY() - 10.5)

    # Calculate the HPR the suit should have while standing forward
    targetPos = targetSuit.getPos(battle)

    suit.setPos(battle, walkOutPos)
    suit.setHpr(battle, origHpr)
    suit.headsUp(battle, targetPos)
    targetHpr = suit.getHpr(battle)

    # Restore original transform immediately after calculating
    suit.setPos(battle, origPos2)
    suit.setHpr(battle, origHpr)

    walkOutTrack = Parallel(
        ActorInterval(suit, 'walk'),
        LerpPosInterval(
            suit,
            walkDur,
            walkOutPos,
            startPos=origPos,
            other=battle
        ),
        LerpHprInterval(
            suit,
            walkDur,
            targetHpr,
            startHpr=origHpr,
            other=battle
        )
    )

    walkBackTrack = Parallel(
        ActorInterval(suit, 'walk'),
        LerpPosInterval(
            suit,
            walkDur,
            origPos,
            startPos=walkOutPos,
            other=battle
        ),
        LerpHprInterval(
            suit,
            walkDur,
            origHpr,
            startHpr=targetHpr,
            other=battle
        )
    )

    suitTrack = Sequence(
        walkOutTrack,
        getSuitAnimTrack(attack, playRate=1.5),
        walkBackTrack,
        Func(suit.setPos, battle, origPos),
        Func(suit.setHpr, battle, origHpr),
        Func(suit.setNeutralAnimationDrop)
    )

    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=4.0)

    return Parallel(suitTrack, selfDamageTracks, soundTrack2)

def doFailsafeProtocol(attack):
    suit = attack['suit']
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Wait(3.0), Parallel(Func(suit.showHpTextNew, 0, text="+5% Defense!", colorCode=1)), Func(suit.makeDamageReduction), Func(suit.checkDamageReduction, + 5))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
    soundTrack2 = getSoundTrack('SA_cease_and_desist.ogg')
    return Parallel(suitTrack, selfDamageTracks, soundTrack2)

def doExplodingDocument(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    explode = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(2.25))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(Wait(2.25))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    dmg = target[0]['hp']
    tnt = globalPropPool.getProp('shredder-paper')
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
    propTrack = Sequence(
        getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.75, VBase3(1.2, 1.2, 1.2),
                               scaleUpTime=0.25))
    propTrack.append(Wait(0.95))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
    toonTrack = getToonTrackCheat(attack, 2.25, ['slip-forward'], 3.4, ['struggle'])
   # toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg), 2.5, ['slip-forward'])
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.25)
    notifyTrack = Sequence(Wait(2.25), Func(toon.showHpTextNew, -int(dmg), text="MARKED!", colorCode=4))
    notifyTrack.append(Parallel(Func(toon.makeMarkedWood), Func(toon.addMarkedWoodRounds, 4)))
    return Parallel(explodeTracks, suitTrack, toonTrack, soundTrack, propTrack, notifyTrack, explosionTrack)

def doExplodingDocumentGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    suitTrack = Parallel()

    explosionTracks = Parallel()
    explodeTracks = Parallel()
    propTracks = Parallel()
    notifyTracks = Parallel()
    toonTracks = Parallel()

    for t in targets:
        toon = t['toon']
        dmg = t['hp']

        toonPos = toon.getPos(battle)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)

        # --- Explosion ---
        explosionTrack = Sequence(
            Wait(2.25),
            MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3)
        )

        # --- Explosion props ---
        explode = [globalPropPool.getProp('explosion') for _ in xrange(3)]

        explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
        explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]

        # --- TNT throw ---
        tnt = globalPropPool.getProp('shredder-paper')

        posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]

        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)

        missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)

        propTrack = Sequence(
            getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.75, VBase3(1.2, 1.2, 1.2), scaleUpTime=0.25),
            Wait(0.95),
            getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle)
        )

        # --- Toon reaction ---
        toonTrack = getToonTrackCheat(attack, 2.25, ['slip-forward'], 0, ['struggle'])
        toonTracks.append(toonTrack)

        # --- Notify ---
        notifyTrack = Sequence(
            Wait(2.25),
            Func(toon.showHpTextNew, -int(dmg), text="MARKED!", colorCode=4),
            Parallel(ActorInterval(toon, 'slip-forward'),
                Func(toon.makeMarkedWood),
                Func(toon.addMarkedWoodRounds, 4)
            )
        )
        if dmg > 0:
            origH = suit.getH(battle)

            # Calculate heading to toon
            origPos, origHpr = battle.getActorPosHpr(suit)
            origPos2 = suit.getPos(battle)
            suit.setPos(battle, origPos)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)

            # Restore original heading
            suit.setH(battle, origH)
            suit.setPos(battle, origPos2)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            suitTrack.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), Parallel(getSuitAnimTrack(attack), ActorInterval(suit, 'throw-paper', playRate=1.5)),
                                      Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                      Func(suit.setNeutralAnimationDrop), Wait(1.0)))
            for i in xrange(3):
                explodeTrack = Sequence(
                    Wait(2.25),
                    getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1),
                    getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3),
                    getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3),
                    getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1),
                    Func(MovieUtil.removeProp, explode[i])
                )
            explodeTracks.append(explodeTrack)
            notifyTracks.append(notifyTrack)
            propTracks.append(propTrack)
            explosionTracks.append(explosionTrack)

    # --- Sound (play once) ---
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.25)

    return Parallel(
        suitTrack,
        explosionTracks,
        explodeTracks,
        propTracks,
        toonTracks,
        notifyTracks,
        soundTrack
    )

def doRiskThresholdBreach50(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        posPoints = [Point3(-0.3468208092485554, 0, -0.1734104046), VBase3(0, 0, 0)]
        scale = Point3(0.075, 0.075, 0.075)
        paper = loader.loadModel('phase_9/models/char/gearProp')
        paper2 = loader.loadModel('phase_9/models/char/gearProp')
        paper3 = loader.loadModel('phase_9/models/char/gearProp')
        paper4 = loader.loadModel('phase_9/models/char/gearProp')
        paper5 = loader.loadModel('phase_9/models/char/gearProp')
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
        propTrack.append(Wait(0.95))
        propTrack2 = Sequence(getPropAppearTrack(paper2, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
        propTrack2.append(Wait(1.1))
        propTrack3 = Sequence(getPropAppearTrack(paper3, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
        propTrack3.append(Wait(1.25))
        propTrack4 = Sequence(getPropAppearTrack(paper4, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
        propTrack4.append(Wait(1.4))
        propTrack5 = Sequence(getPropAppearTrack(paper5, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
        propTrack5.append(Wait(1.55))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle))
        propTrack2.append(getPropThrowTrack(attack, paper2, [hitPoint], [missPoint], .25, parent=battle))
        propTrack3.append(getPropThrowTrack(attack, paper3, [hitPoint], [missPoint], .25, parent=battle))
        propTrack4.append(getPropThrowTrack(attack, paper4, [hitPoint], [missPoint], .25, parent=battle))
        propTrack5.append(getPropThrowTrack(attack, paper5, [hitPoint], [missPoint], .25, parent=battle))
        propTracks.append(propTrack)
        propTracks.append(propTrack2)
        propTracks.append(propTrack3)
        propTracks.append(propTrack4)
        propTracks.append(propTrack5)
    suitTrack = Parallel(getSuitTrack(attack, playRate=1.5))
    toonTrack = getToonTracks(attack, 2.2, ['slip-backward'], 1.8, ['duck'])
    soundTrack2 = Sequence(Wait(1.95), getSoundTrack('CHQ_VP_frisbee_gears.ogg'))
    return Parallel(suitTrack, soundTrack2, propTracks, toonTrack)

def doRiskThresholdBreach75(attack):
    suit = attack['suit']
    node = suit.getGeomNode().getChild(0)
    suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=.5, colorScale=(0, 1, 0.078, 1),
                                                                blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.5, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'))
    soundTrack = Sequence(getSoundTrack('SA_defense.ogg'))
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(2.0))
    makeShielding = Parallel(Func(suit.makeShielding))
    return Parallel(suitTrack, soundTrack, suitColorTrack, makeShielding)

def makeZapBeamTrack(battle, coil, suit, tDelay, duration):
    beam = globalPropPool.getProp('zap_beam')
    beam.loop('zap_beam')
    beam.setTransparency(1)
    beam.setTwoSided(True)
    beam.hide()
    beam.setH(90)

    beamStageData = []

    def getBeamGeomStages(beam):
        data = []

        for geomNp in beam.findAllMatches('**/+GeomNode'):
            stages = geomNp.findAllTextureStages()

            for i in xrange(stages.getNumTextureStages()):
                ts = stages.getTextureStage(i)

                tex = geomNp.getTexture(ts)
                if tex:
                    tex.setWrapU(tex.WMRepeat)
                    tex.setWrapV(tex.WMRepeat)

                data.append((geomNp, ts))

        return data

    def setupBeam():
        startPos = coil.getPos(render) + Point3(0, 0, coil.getHeight() + 1)
        endPos = suit.getPos(render) + Point3(0, 0, suit.getHeight() * .5)

        beam.reparentTo(render)
        beam.show()
        beam.setPos(startPos)
        beam.headsUp(endPos)

        diff = endPos - startPos
        flatDist = (Point3(endPos[0], endPos[1], startPos[2]) - startPos).length()

        if flatDist > 0.01:
            pitch = math.degrees(math.atan2(diff[2], flatDist))
        else:
            pitch = 0.0

        # If this angles the wrong way, change + pitch to - pitch.
        beam.setP(beam.getP() + pitch)

        dist = diff.length()
        beam.setScale(1, dist * 10, 1)
        beam.setColorScale(1, 1, 1, 1)

        del beamStageData[:]
        beamStageData.extend(getBeamGeomStages(beam))

        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                geomNp.setTexOffset(ts, 0, 0)

    def phaseZap(t):
        offset = t * 14.0

        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                # Keep this axis if it matches your working direction.
                # Swap to (offset, 0), (-offset, 0), or (0, offset) if needed.
                geomNp.setTexOffset(ts, offset, 0)

    def cleanupBeam():
        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                geomNp.clearTexTransform(ts)

        if beam and not beam.isEmpty():
            try:
                beam.stop('zap_beam')
            except:
                pass

            try:
                MovieUtil.removeProp(beam)
            except:
                beam.removeNode()

    return Sequence(
        Wait(tDelay),
        Func(setupBeam),

        Parallel(
            LerpFunctionInterval(
                phaseZap,
                duration,
                fromData=0.0,
                toData=1.0
            ),

            Sequence(
                Wait(max(0.0, duration - 0.2)),
                LerpColorScaleInterval(
                    beam,
                    0.2,
                    Vec4(1, 1, 1, 0),
                    startColorScale=Vec4(1, 1, 1, 1)
                )
            )
        ),

        Wait(0.2),
        Func(cleanupBeam)
    )

def doZapRetaliationDividend(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    targets = attack['target']
    cagePropTracks = Parallel()
    smokeTracks = Parallel()
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    zapTrack = Sequence(Wait(2.0), SoundInterval(zapSfx, volume=0.6))
    notifyTracks = Parallel()
    cagePropTracks = Parallel()
    moveTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(2), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(smoke.removeNode))
        notifyTrack = Sequence(Wait(2.0), Func(toon.showHpTextNew, -int(dmg)))
        notifyTrack.append(toon.makeShockDamageBurstTrack(duration=2.5, sparkCount=40))
        notifyTrack.append(Parallel(Func(toon.makeZapped), Func(toon.addZappedRounds, 3)))
        if dmg > 0:
            cagePropTrack = Sequence(makeZapBeamTrack(
                battle,
                suit,
                toon,
                tDelay=2,
                duration=1.5
            ))
            cagePropTracks.append(cagePropTrack)
            origH = suit.getH(battle)

            # Calculate heading to toon
            origPos, origHpr = battle.getActorPosHpr(suit)
            origPos2 = suit.getPos(battle)
            suit.setPos(battle, origPos)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)

            # Restore original heading
            suit.setH(battle, origH)
            suit.setPos(battle, origPos2)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            moveTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'scabbard'),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            smokeTracks.append(smokeTrack)
            notifyTracks.append(notifyTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracksCheat(attack, damageDelay=2, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['sidestep'], splicedDodgeAnims=[], showDamageExtraTime=0)
    soundTrack = getSoundTrack('SA_sparkplug2.ogg', delay=0, node=suit)
    return Parallel(suitTrack, zapTrack, soundTrack, cagePropTracks, moveTracks, notifyTracks, smokeTracks, toonTrack)

def doZapRetaliationOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
    targets = attack['target']
    cagePropTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        cage = loader.loadModel('phase_5/models/props/lightning')
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        # cage.setH(90)
        # cage.setPosHpr(0, 0, 0, 180, 0, 0)
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        if dmg == 0:
            y -= 5
        cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 1, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0),
            Parallel(cagePosition),
            Parallel(
                cage.posInterval(0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
        if dmg > 0:
            cagePropTracks.append(cagePropTrack)
            smokeTracks.append(smokeTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracks(attack, damageDelay=1, splicedDamageAnims=damageAnims, dodgeDelay=.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, smokeTracks, toonTrack)

def doRiskThresholdBreach(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    node = suit.getGeomNode().getChild(0)
    suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=.25, colorScale=(0, 1, 0.078, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(0, 1, 0.078, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(0, 1, 0.078, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(0, 1, 0.078, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                           blendType='easeInOut')
                              )
    moveTrack = Parallel(Func(suit.checkExtraAbilities, 1), Func(suit.showHpTextNew, 0, text="+1 Ability!", colorCode=1))
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack2 = getSoundTrack('SA_wire_cut_knife.ogg')
    return Parallel(suitTrack, suitColorTrack, moveTrack, soundTrack2)

def doSelfRepair(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    suitTracks = Parallel(Sequence(ActorInterval(suit, 'finger-wag', endTime=2), ActorInterval(suit, 'finger-wag', startTime=2, endTime=0)))
    suitTracks.append(getSuitAnimTrack(attack, playRate=1.5))
    healSounds = Parallel()
    healSound = getSoundTrack('SA_repair.ogg')
    suitTrack = Sequence(Wait(2.0))
    suitTrack.append(Parallel(Func(suit.setHealthForMe, + 750), Func(suit.showHpTextNew, + 750), Func(suit.updateHealthBar, 0)))
    suitTracks.append(suitTrack)
    healSounds.append(healSound)
    return Parallel(suitTracks, healSounds)

def doRedundantAuthority(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    selfDamageTracks = Parallel()
    for s in battle.activeSuits:
        if not s.dna.name == 'cdirector':
            selfDamageTrack = Sequence(Wait(2.0), Parallel(Func(s.checkRedundant), Func(s.checkHealingPhrases, 0)))
            selfDamageTracks.append(selfDamageTrack)
    moveTrack = Parallel(Func(suit.setHealthForMe, - 500), Func(suit.showHpTextNew, - 500), Func(suit.updateHealthBar, 0))
    suitTrack = Sequence(getSuitAnimTrack(attack), suit.makeRedundantAuthorityInterval(battle))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=2.0)
    soundTrack = getSoundTrack('SA_scabbard.ogg')
    return Parallel(suitTrack, moveTrack, selfDamageTracks, soundTrack, soundTrack2)

def doRushHour(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=.75), Func(suit.makeAngry, 2))
    suitTrack.append(Wait(3.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_rush_job_target.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doRiskThresholdBreach25(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    allTubeTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    toonDamageTracks = Parallel()
    suitTrack = Sequence(Wait(3.0), doSnipeCut(attack))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tape.setColor(0, 1, 0.976, 1)
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))
            tubes[i].setColor(0, 1, 0.976, 1)

        hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
        hips = toon.getHipsParts()
        animal = toon.style.getAnimal()
        scale = ToontownGlobals.toonBodyScales[animal]
        legs = toon.style.legs
        torso = toon.style.torso
        torso = torso[0]
        animal = animal[0]
        tubeHeight = -0.8
        if torso == 's':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'm':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'l':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 1.11)
        if animal == 'h' or animal == 'd':
            tubeHeight = -0.87
            scaleUpPoint = Point3(scale * 1.69, scale * 1.69, scale * 0.67)
        tubePosPoints = [Point3(0, 0, tubeHeight), MovieUtil.PNT3_ZERO]
        tubeTracks = Parallel()
        tubeTracks.append(Func(battle.movie.needRestoreHips))
        for partNum in xrange(0, hips.getNumPaths()):
            nextPart = hips.getPath(partNum)
            tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 0, 3, scaleUpPoint=scaleUpPoint))

        tubeTracks.append(Func(battle.movie.clearRestoreHips))
        soundTrack = getSoundTrack('SA_red_tape.ogg', delay=0, node=suit)
        toonDamageTrack = Sequence(ActorInterval(toon, 'struggle'))
        if dmg > 0:
            allTubeTracks.append(tubeTracks)
            soundTracks.append(soundTrack)
            toonDamageTracks.append(toonDamageTrack)
    return Parallel(toonTracks, soundTracks, suitTrack, toonDamageTracks, allTubeTracks)

def doContentSync(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targets = attack['target']
    damageDelay = 1.2
    attackDelay = 1.2
    suitTrack = Sequence(getSuitAnimTrackAttack(attack, playRate=1.25))
    partTracks = Parallel()
    allHeadTracks = Parallel()
    allChestTracks = Parallel()
    toonTracks2 = Parallel()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    for toon in battle.activeToons:
        headParts = toon.getHeadParts()
        sprayEffects = BattleParticles.createParticleEffect('ReOrgSprayNew')
        BattleParticles.loadParticles()
        BattleParticles.setEffectTexture(sprayEffects, 'snow-particle',
                                         color=Vec4(1, 0, 0, 1))
        partTrack = getPartTrack(sprayEffects, 0.5, 3.0, [sprayEffects, toon, 0], softStop=-1)
        partTracks.append(partTrack)
        print
        '***********headParts pos=', headParts[0].getPos()
        print
        '***********headParts hpr=', headParts[0].getHpr()
        headTracks = Parallel()
        for partNum in xrange(0, headParts.getNumPaths()):
            part = headParts.getPath(partNum)
            x = part.getX()
            y = part.getY()
            z = part.getZ()
            h = part.getH()
            p = part.getP()
            r = part.getR()
            damageAnims = [['neutral',
                    0.01,
                    0.01,
                    0.5], ['juggle',
                           0.01,
                           0.01,
                           1.48], ['think', 0.01, 2.28]]
            toonTracks2.append(Sequence(Wait(1.2), getSplicedAnimsTrack(damageAnims, actor=toon)))
            headTracks.append(Func(toon.headsUp, battle, suitPos))
            headTracks.append(Func(toon.makeContentSync, dmg))
            headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)),
                                       LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)),
                                       LerpHprInterval(part, 0.25, VBase3(360, 0, 180)),
                                       LerpPosInterval(part, 0.25, Point3(x, y, z + 3.1)),
                                       LerpPosInterval(part, 0.1, Point3(x, y, z + 0.3)), Wait(0.1),
                                       LerpHprInterval(part, 0.35, VBase3(-745, 0, 180),
                                                       startHpr=VBase3(0, 0, 180)),
                                       LerpHprInterval(part, 0.5, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)),
                                       LerpPosInterval(part, 0.15, Point3(x, y, z + 1)),
                                       LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2),
                                       LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.1)))

        allHeadTracks.append(headTracks)

        def getChestTrack(part, attackDelay=attackDelay):
            origScale = part.getScale()
            return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1),
                            LerpHprInterval(part, 1.1, part.getHpr()))

        chestTracks = Parallel()
        arms = toon.findAllMatches('**/arms')
        sleeves = toon.findAllMatches('**/sleeves')
        hands = toon.findAllMatches('**/hands')
        print
        '*************arms hpr=', arms[0].getHpr()
        for partNum in xrange(0, arms.getNumPaths()):
            chestTracks.append(getChestTrack(arms.getPath(partNum)))
            chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
            chestTracks.append(getChestTrack(hands.getPath(partNum)))

        allChestTracks.append(chestTracks)

    damageAnims = [['neutral',
                    0.01,
                    0.01,
                    0.5], ['juggle',
                           0.01,
                           0.01,
                           1.48], ['think', 0.01, 2.28]]
    dodgeAnims = []
    dodgeAnims.append(['think',
                       0.01,
                       0,
                       0.6])
    return Parallel(suitTrack, partTracks, toonTracks2, allHeadTracks, allChestTracks)

def doOperationalFreeze(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    sprayEffects = Parallel()
    for t in targets:
        toon = t['toon']
        sprayEffect = BattleParticles.createParticleEffect('FreezeSpray')
        sprayEffect2 = BattleParticles.createParticleEffect('FreezeSpray')
        partTrack4 = getPartTrack(sprayEffect, 1.0, 3.0, [sprayEffect2, toon, 0], softStop=-1)
        sprayEffects.append(partTrack4)

    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracksCheat(attack, damageDelay=1.0, splicedDamageAnims=damageAnims, splicedDodgeAnims=damageAnims, dodgeDelay=1.0,
                               showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    soundTrack = getSoundTrack('SA_deepfreeze.ogg', delay=1.0, node=suit)
    return Parallel(suitTrack, toonTracks, sprayEffects, soundTrack)

def doContingencyClause(attack):
    suit = attack['suit']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrackAttack(attack, playRate=1.5))
    tubes = []
    tapePosPoints = [Point3(-0.25, 0, -0.25), VBase3(0, 0, 0)]
    tapeScaleUpPoint = Point3(1, 1, 0.74)
    propTracks = Parallel()
    toonTracks = Parallel()
    allTubeTracks = Parallel()
    notifyTracks = Parallel()
    battle = attack['battle']
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tape.setColor(0, 1, 0.976, 1)
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))
            tubes[i].setColor(0, 1, 0.976, 1)

        propTrack = Sequence(getPropAppearTrack(tape, suit.getRightHand(), tapePosPoints, 0.25, tapeScaleUpPoint, scaleUpTime=0.25))
        propTrack.append(Wait(1.55))
        hitPoint = lambda toon=toon: __toonTorsoPoint(toon)
        propTrack.append(getPropThrowTrack(attack, tape, [hitPoint], [__toonGroundPoint(attack, toon, 0)], .25, target=t))
        propTracks.append(propTrack)
        hips = toon.getHipsParts()
        animal = toon.style.getAnimal()
        scale = ToontownGlobals.toonBodyScales[animal]
        legs = toon.style.legs
        torso = toon.style.torso
        torso = torso[0]
        animal = animal[0]
        tubeHeight = -0.8
        if torso == 's':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'm':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'l':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 1.11)
        if animal == 'h' or animal == 'd':
            tubeHeight = -0.87
            scaleUpPoint = Point3(scale * 1.69, scale * 1.69, scale * 0.67)
        tubePosPoints = [Point3(0, 0, tubeHeight), MovieUtil.PNT3_ZERO]
        tubeTracks = Parallel()
        tubeTracks.append(Func(battle.movie.needRestoreHips))
        for partNum in xrange(0, hips.getNumPaths()):
            nextPart = hips.getPath(partNum)
            tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 2.2, 3.17, scaleUpPoint=scaleUpPoint))

        tubeTracks.append(Func(battle.movie.clearRestoreHips))
        allTubeTracks.append(tubeTracks)
        toonTracks.append(Sequence(Wait(2.4), ActorInterval(toon, 'struggle')))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.75, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack, allTubeTracks, notifyTracks)

def doSnipeCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    explosionTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    suitTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        leftPosPoints = [Point3(0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
        explosionTrack = Sequence()
        explosionTrack.append(Wait(1.5))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        leftKnives = []
        rightKnives = []
        for i in xrange(0, 3):
            leftKnives.append(globalPropPool.getProp('dagger'))
            rightKnives.append(globalPropPool.getProp('dagger'))

        for i in xrange(0, 3):
            knifeDelay = 0.11
            leftTrack = Sequence()
            leftTrack.append(Wait(1.1))
            leftTrack.append(Wait(i * knifeDelay))
            leftTrack.append(
                getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                               hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                leftKnifeTracks.append(leftTrack)
            rightTrack = Sequence()
            rightTrack.append(Wait(1.1))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(
                getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                                hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                rightKnifeTracks.append(rightTrack)

        notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextNew, - int(dmg), text="-40% Damage!", colorCode=4))
        #toonTrack = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
        soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=1.5, node=suit)
        suitTrack = Parallel(getSuitAnimTrack(attack))
        suitTrack.append(Wait(2.0))
        if dmg > 0:
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            explosionTracks.append(explosionTrack)
            suitTracks.append(suitTrack)
            origH = suit.getH(battle)

            # Calculate heading to toon
            origPos, origHpr = battle.getActorPosHpr(suit)
            origPos2 = suit.getPos(battle)
            suit.setPos(battle, origPos)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)

            # Restore original heading
            suit.setH(battle, origH)
            suit.setPos(battle, origPos2)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            suitTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'glower'),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            notifyTracks.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 2), Func(toon.checkDamageDown, 40)))
            notifyTracks.append(notifyTrack)
    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                         dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, toonDamageTrack, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)

# def doSnipeCut(attack):
#     suit = attack['suit']
#     battle = attack['battle']
#     targets = attack['target']
#     explosionTracks = Parallel()
#     toonTracks = Parallel()
#     soundTracks = Parallel()
#     leftKnifeTracks = Parallel()
#     rightKnifeTracks = Parallel()
#     suitTracks = Parallel()
#     notifyTracks = Parallel()
#     for t in targets:
#         toon = t['toon']
#         dmg = t['hp']
#         toonPos = toon.getPos(battle)
#         suitPos, suitHpr = battle.getActorPosHpr(suit)
#         gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
#         leftPosPoints = [Point3(0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
#         rightPosPoints = [Point3(-0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
#         explosionTrack = Sequence()
#         explosionTrack.append(Wait(1.5))
#         explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
#         leftKnives = []
#         rightKnives = []
#         for i in xrange(0, 3):
#             leftKnives.append(globalPropPool.getProp('dagger'))
#             rightKnives.append(globalPropPool.getProp('dagger'))
#
#         for i in xrange(0, 3):
#             knifeDelay = 0.11
#             leftTrack = Sequence()
#             leftTrack.append(Wait(1.1))
#             leftTrack.append(Wait(i * knifeDelay))
#             leftTrack.append(
#                 getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
#             leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'],
#                                                hitDuration=0.3, missDuration=0.3, target=t))
#             if dmg > 0:
#                 leftKnifeTracks.append(leftTrack)
#             rightTrack = Sequence()
#             rightTrack.append(Wait(1.1))
#             rightTrack.append(Wait(i * knifeDelay))
#             rightTrack.append(
#                 getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
#             rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'],
#                                                 hitDuration=0.3, missDuration=0.3, target=t))
#             if dmg > 0:
#                 rightKnifeTracks.append(rightTrack)
#
#         notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextNew, - int(dmg), text="-40% Damage!", colorCode=4))
#         #toonTrack = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
#         soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
#         soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=1.5, node=suit)
#         suitTrack = Sequence(getSuitTrack(attack))
#         suitTrack.append(Wait(2.0))
#         if dmg > 0:
#             soundTracks.append(soundTrack)
#             soundTracks.append(soundTrack2)
#             explosionTracks.append(explosionTrack)
#             suitTracks.append(suitTrack)
#             notifyTracks.append(notifyTrack)
#             notifyTracks.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 2), Func(toon.checkDamageDown, 40)))
#     damageAnims = [['slip-backward', 0.01, 0.35]]
#     toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
#                                          dodgeAnimNames=['neutral'])
#     return Parallel(suitTracks, toonTracks, rightKnifeTracks, toonDamageTrack, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)

def doOilRainDamage(attack):
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.3
    dodgeDelay = 0.25
    selfDamageTracks = Parallel()
    for s in battle.activeSuits:
        selfDamageTrack = Sequence(Parallel(Func(s.checkOilRain)))
        selfDamageTracks.append(selfDamageTrack)
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    puddleTracks = Parallel()
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                               dodgeAnimNames=['sidestep'])
    soundTracks = Parallel()
    soundTracks.append(getSoundTrack('LB_toonup.ogg'))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sandTrap = globalPropPool.getProp('quicksand')
        sandTrap.setHpr(Point3(120, 0, 0))
        sandTrap.setScale(0.01)
        sandTrap.setColor(0, 0, 0, 1)
        puddleTracks.append(Sequence(
            Func(battle.movie.needRestoreRenderProp, sandTrap),
            Wait(damageDelay - 0.7),
            Func(sandTrap.reparentTo, battle),
            Func(sandTrap.setPos, toon.getPos(battle)),
            LerpScaleInterval(sandTrap, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO),
            Wait(0.3 if dmg == 0 else 3.2),
            LerpFunctionInterval(sandTrap.setAlphaScale, fromData=1, toData=0, duration=0.8),
            Func(MovieUtil.removeProp, sandTrap),
            Func(battle.movie.clearRenderProp, sandTrap)
        ))
        soundTracks.append(getSoundTrack('SA_liquidate.ogg', duration=0.67 if dmg == 0 else 0.0, node=toon))

    return Parallel(selfDamageTracks, toonTracks, soundTracks, puddleTracks)

def hair_task(t, node_path, texture_stage):
    # 't' will range from 0.0 to 1.0 over the duration
    # You can interpolate between two points manually if needed, or use 't' directly
    # Example: smoothly shift u-coordinate from 0 to 1
    u_offset = 0
    v_offset = t
    node_path.setTexOffset(texture_stage, u_offset, v_offset)

def doInversion(attack):
    suit = attack['suit']
    hair = None
    hairTracks = Parallel()
    for headPart in suit.animatedHeadParts:
        for stage in headPart.findAllTextureStages("*hair"):
            hairTracks.append(LerpFunc(
            hair_task,
            duration=5.0,
            fromData=1.0,
            toData=0,
            extraArgs=[headPart, stage]
        ))
        # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.setHealthForMe, + 250), Func(suit.showHpTextNew, + 250, "+1 ATTACK!", colorCode=1), Func(suit.updateHealthBar, 0), Func(suit.makeInversion),
                                        Func(suit.makeExtraAttacks, suit.getExtraAttacks() + 1), Func(suit.makeUnDamageReduction), Func(suit.checkDamageReduction, 0)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(1.0))
    soundTrack2 = getSoundTrack('LB_toonup.ogg')
    return Parallel(suitTrack, selfDamageTracks, hairTracks, soundTrack2)

def doStormCell(attack):
    suit = attack['suit']
    hair = None
    hairTracks = Parallel()
    for headPart in suit.animatedHeadParts:
        for stage in headPart.findAllTextureStages("*hair"):
            hairTracks.append(LerpFunc(
            hair_task,
            duration=5.0,
            fromData=0.4,
            toData=0.6,
            extraArgs=[headPart, stage]
        ))
        # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.makeStormCell), Func(suit.addStormCellDamageReverse), Func(suit.makeUnDamageReduction), Func(suit.checkDamageReduction, 0)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(1.0))
    return Parallel(suitTrack, selfDamageTracks, hairTracks)

def doOilRain(attack):
    suit = attack['suit']
    hair = None
    hairTracks = Parallel()
    for headPart in suit.animatedHeadParts:
        for stage in headPart.findAllTextureStages("*hair"):
            hairTracks.append(LerpFunc(
            hair_task,
            duration=5.0,
            fromData=0.0,
            toData=0.4,
            extraArgs=[headPart, stage]
        ))
        # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.makeOilRain), Func(suit.makeUnDamageReduction), Func(suit.checkDamageReduction, 0)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(1.0))
    return Parallel(suitTrack, selfDamageTracks, hairTracks)

def doFreezingRain(attack):
    suit = attack['suit']
    hair = None
    hairTracks = Parallel()
    for headPart in suit.animatedHeadParts:
        for stage in headPart.findAllTextureStages("*hair"):
            hairTracks.append(LerpFunc(
            hair_task,
            duration=5.0,
            fromData=0.0,
            toData=0.8,
            extraArgs=[headPart, stage]
        ))
        # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.makeFreezingRain), Func(suit.makeUnDamageReduction), Func(suit.checkDamageReduction, 0)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(1.0))
    return Parallel(suitTrack, selfDamageTracks, hairTracks)

def doMonsoon(attack):
    suit = attack['suit']
    hair = None
    hairTracks = Parallel()
    for headPart in suit.animatedHeadParts:
        for stage in headPart.findAllTextureStages("*hair"):
            hairTracks.append(LerpFunc(
            hair_task,
            duration=5.0,
            fromData=0.0,
            toData=0.8,
            extraArgs=[headPart, stage]
        ))
        # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.makeMonsoon), Func(suit.makeDamageReduction), Func(suit.checkDamageReduction, + 90)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(1.0))
    return Parallel(suitTrack, selfDamageTracks, hairTracks)

def doHeavyRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    hair = None
    hairTracks = Parallel()
    for headPart in suit.animatedHeadParts:
        for stage in headPart.findAllTextureStages("*hair"):
            hairTracks.append(LerpFunc(
            hair_task,
            duration=5.0,
            fromData=0.0,
            toData=0.2,
            extraArgs=[headPart, stage]
        ))
        # 0 - inversion, 0.2 - heavy rain, 0.4 - oil rain, 0.6 - storm cell, 0.8 - fog
    selfDamageTracks = Parallel()
    for s in battle.activeSuits:
        selfDamageTrack = Sequence(Parallel(Func(s.makeHeavyRain), Func(suit.makeUnDamageReduction), Func(suit.checkDamageReduction, 0)))
        selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(1.0))
    return Parallel(suitTrack, selfDamageTracks, hairTracks)


def doStormCellDamage(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
    targets = attack['target']
    cagePropTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(2), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        cage = loader.loadModel('phase_5/models/props/lightning')
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        # cage.setH(90)
        # cage.setPosHpr(0, 0, 0, 180, 0, 0)
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        if dmg == 0:
            y -= 5
        cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 2, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0),
            Parallel(cagePosition),
            Parallel(
                cage.posInterval(0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        smokeTracks.append(smokeTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracks(attack, damageDelay=2, splicedDamageAnims=damageAnims, dodgeDelay=.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    oldcolor = render.getColorScale()
    return Parallel(suitTrack, cagePropTracks, smokeTracks, toonTrack)

def doHeavyRainDamage(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitDamageTracks = Parallel(ActorInterval(suit, 'transformation', duration=1.5))
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
    for s in battle.activeSuits:
        suitDamageTracks.append(Sequence(Wait(1.5), Func(s.checkHeavyRainDamage, battle), Func(s.makeUnHeavyRain), ActorInterval(s, 'slip-backward'), Func(s.setNeutralAnimationDrop), Wait(1.0)))
    targets = attack['target']
    cagePropTracks = Parallel()
    smokeTracks = Parallel()
    for s in battle.activeSuits:
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.5), Func(smoke.reparentTo, s),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        cage = loader.loadModel('phase_5/models/props/lightning')
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        # cage.setH(90)
        # cage.setPosHpr(0, 0, 0, 180, 0, 0)
        toonPos = s.getPos(battle)
        y = toonPos.getY()
        cagePos = [Point3(toonPos.getX(), y, 100.0), s.getHpr(battle)]
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 1.5, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0),
            Parallel(cagePosition),
            Parallel(
                cage.posInterval(0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        smokeTracks.append(smokeTrack)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.5), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        cage = loader.loadModel('phase_5/models/props/lightning')
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        # cage.setH(90)
        # cage.setPosHpr(0, 0, 0, 180, 0, 0)
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        if dmg == 0:
            y -= 5
        cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 1.5, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0),
            Parallel(cagePosition),
            Parallel(
                cage.posInterval(0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        smokeTracks.append(smokeTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    oldcolor = render.getColorScale()
    return Parallel(suitTrack, cagePropTracks, suitDamageTracks, smokeTracks, toonTrack)

def doTornado(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    battle = attack['battle']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    cagePropTracks = Parallel()
    # for t in attack['target']:
    # toon = t['toon']
    # dmg = t['hp']
    whirlSfx = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_whirlwind.ogg')
    whirlSfx.setLoop(True)
    cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    # cage.setH(90)
    # cage.setPosHpr(0, 0, 0, 180, 0, 0)
    suitPos = suit.getPos(battle)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(suitPos.getX(), y + 15, suitPos.getZ()), toon.getHpr(battle)]
    spinTrack = Sequence(Func(whirlSfx.play), LerpHprInterval(cage, 5.5, Point3(-10800, 0, 0)), Func(whirlSfx.stop))
    cagePropTrack = Sequence(
        Parallel(cagePosition),
        Parallel(getPropAppearTrack(cage, battle, cagePos, 0.25, scaleUpPoint=Point3(2.0), scaleUpTime=1.0),
            cage.posInterval(0.75, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_toonInWhirlwind.ogg'), duration=0.75, node=cage), spinTrack,
        ),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
    )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.append(['slip-forward'])
    sinkPos = toon.getPos(battle)
    sinkPos.setZ(sinkPos.getZ() + 25)
    notifyTrack = Sequence(Wait(5.9), Func(toon.showHpTextNew, -int(dmg), text="CONFUSED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.makeConfused), Func(toon.addConfusedRounds, 2)))
    toonTrack = getToonTrackCheat(attack, damageDelay=.9, splicedDamageAnims=damageAnims, dodgeDelay=0.91,
                             dodgeAnimNames=['sidestep'], showDamageExtraTime=5, showMissedExtraTime=1.0)
    toonSpinTrack = Sequence(Wait(0.9), LerpHprInterval(toon, 4.5, Point3(10800, 0, 0)),
                                 LerpHprInterval(toon, 0.5, toon.getHpr()), Wait(0.5))
    toonLiftTrack = Sequence(Wait(0.9), LerpPosInterval(toon, 4.5, Point3(toon.getX(), toon.getY(), toon.getZ() + 50)), LerpPosInterval(toon, 0.5, toon.getPos()), Wait(0.5))
    return Parallel(suitTrack, cagePropTracks, toonTrack, notifyTrack, toonLiftTrack, toonSpinTrack)

def doRevvingUp(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    selfDamageTracks = Parallel()
    selfDamageTracks.append(Sequence(Func(suit.createSuitRevvingUpInterval)))
    selfDamageTrack = Sequence(Wait(2.0), Parallel(Func(suit.addRPM, dmg), Func(suit.showHpTextNew, 0, text="+%s,000 RPM" % dmg, colorCode=1)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
    soundTrack2 = getSoundTrack('SA_revving_up.ogg')
    return Parallel(suitTrack, selfDamageTracks, soundTrack2)

def doRevvingUpWhipsaw(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    selfDamageTracks = Parallel()
    selfDamageTracks.append(Sequence(Func(suit.createSuitRevvingUpInterval)))
    selfDamageTrack = Sequence(Wait(2.0), Parallel(Func(suit.addRPM, dmg), Func(suit.showHpTextNew, 0, text="+%s,000 RPM" % dmg, colorCode=1)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
    soundTrack2 = getSoundTrack('SA_revving_up.ogg')
    return Parallel(suitTrack, selfDamageTracks, soundTrack2)

def do2000RPMSparkPlug(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.addRPM, - 2), Func(suit.showHpTextNew, 0, text="-2,000 RPM", colorCode=1)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(Wait(2.0), doSparkPlug(attack))
    return Parallel(suitTrack, selfDamageTracks)

def do2000RPMOffboarding(attack, ind):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.addRPM, - 2), Func(suit.showHpTextNew, 0, text="-2,000 RPM", colorCode=1)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(Wait(2.0), doOffboarding(attack, ind))
    return Parallel(suitTrack, selfDamageTracks)

def do3000RPMAggrandize(attack, ind):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.addRPM, - 3), Func(suit.showHpTextNew, 0, text="-3,000 RPM", colorCode=1)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(Wait(2.0), doAggrandize(attack, ind))
    return Parallel(suitTrack, selfDamageTracks)

def do7000RPM(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.addRPM, - 7), Func(suit.showHpTextNew, 0, text="-7,000 RPM", colorCode=1)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(Wait(2.0), doMarkedWood(attack))
    return Parallel(suitTrack, selfDamageTracks)

def do7000RPMScabbard(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.addRPM, - 7), Func(suit.showHpTextNew, 0, text="-7,000 RPM", colorCode=1)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(Wait(2.0), doScabbard(attack))
    return Parallel(suitTrack, selfDamageTracks)

def do10000RPM(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    selfDamageTracks = Parallel()
    selfDamageTrack = Sequence(Parallel(Func(suit.addRPM, - 10), Func(suit.showHpTextNew, 0, text="-10,000 RPM", colorCode=1)))
    selfDamageTracks.append(selfDamageTrack)
    suitTrack = Sequence(Wait(2.0), doLayoffs(attack))
    return Parallel(suitTrack, selfDamageTracks)

def doMarkedWood(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    battle = attack['battle']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(-0.13024602026049337, 0.21707670043415206, -0.21707670043415206), VBase3(90, -180.0, 0)]
        scale = Point3(1, 1, 1)
    else:
        posPoints = [Point3(.78, -1.89, -.17), VBase3(10, 250, -10)]
        scale = Point3(1, 1, 1)
    propTracks = Parallel()
    paper = loader.loadModel('phase_10/models/props/treekiller_log_center')
    propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
    propTrack.append(Wait(0.95))
    hitPoint = __toonFacePoint(toon)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.5, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    splatName = 'dust'
    splat = globalPropPool.getProp('dust')
    explode = globalPropPool.getProp('dust')
    explode.setTwoSided(True)


    explode.setBillboardPointWorld(2)
    explodeTrack = Sequence()
    explodeTrack.append(
    getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
    explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
    soundTrack = getSoundTrack('SA_woodchipper.ogg', node=suit)
    propTrack.append(Parallel(explodeTrack, soundTrack))
    propTracks.append(propTrack)

    toonTracks = getToonTracksCheat(attack, 2.2, ['cringe'], 2, ['jump'])
    notifyTrack = Sequence(Wait(2.25), Func(toon.showHpTextNew, -int(dmg), text="MARKED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.makeMarkedWood), Func(toon.addMarkedWoodRounds, 3)))
    currentBossHealth = -1
    for s in battle.suits:
        if s.dna.name == 'cdirector':
            currentBossHealth = s.currHP
    if currentBossHealth > 0:
        notifyTrack.append(Parallel(Func(toon.checkMarkedWood, 100)))
    else:
        notifyTrack.append(Parallel(Func(toon.checkMarkedWood, 75)))
    return Parallel(suitTrack, toonTracks, notifyTrack, propTracks)

def __suitTargetPoint(suit):
    pnt = suit.getPos(render)
    pnt.setZ(pnt[2] + suit.getHeight() * 0.66)
    return Point3(pnt)

def doSparkPlug(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    battle = attack['battle']
    targetPoint = lambda toon=toon: __suitTargetPoint(toon)
    def getSprayStartPos(suit=suit):
        suit.update(0)
        p = suit.getPos()
        return p
    selfDamageTracks = Parallel()
    sprayTrack = Sequence(Wait(4.0), MovieUtil.getZapTrack(battle, Point4(1.0, 1.0, 0, 1.0), getSprayStartPos, targetPoint, .1, .1, .1, horizScale=.1, vertScale=.1))
    selfDamageTracks.append(Sequence(Func(suit.createSuitSparkPlugInterval)))
    selfDamageTracks.append(Parallel(Func(toon.makeDamageOvertime), Func(toon.addDamageOvertimeRounds, 3)))
    suitTrack = Sequence(getSuitTrack(attack), Wait(2.0))
    soundTrack2 = getSoundTrack('SA_sparkplug.ogg')
    toonTrack = getToonTrack(attack, 4.0, ['slip-backward'], 2, ['jump'])
    return Parallel(suitTrack, toonTrack, sprayTrack, selfDamageTracks, soundTrack2)

def doSparkPlugDamage(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    notifyTracks = Parallel()
    flecksTracks = Parallel()
    colorTracks = Parallel()
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-backward',
                        1e-05,
                        0.4,
                        1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-backward', 0.31, 0.8, startTime=1.2))
    soundTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
        BattleParticles.setEffectTexture(flameEffect, 'fire')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall = BattleParticles.createParticleEffect(file='firedBaseFlame')
        flameSmall = BattleParticles.createParticleEffect('FiredFlame')
        flecksSmall = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(baseFlameSmall, 'fire')
        BattleParticles.setEffectTexture(flameSmall, 'fire')
        BattleParticles.setEffectTexture(flecksSmall, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall.setScale(0.7)
        flameSmall.setScale(0.7)
        flecksSmall.setScale(0.7)
        baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 3.9, [baseFlameEffect, toon, 0], softStop=-1)
        flameTrack = getPartTrack(flameEffect, 1.0, 3.9, [flameEffect, toon, 0], softStop=-1)
        flecksTrack = getPartTrack(flecksEffect, 1.8, 2.1, [flecksEffect, toon, 0], softStop=-1)

        def changeColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for partNum in xrange(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.clearColorScale))

            return track

        notifyTrack = Sequence(Wait(1.5), Func(toon.showHpText, - int(dmg)))
        if dmg > 0:
            soundTrack = getSoundTrack('AA_battery.ogg', delay=1.0, node=suit)
            soundTracks.append(soundTrack)
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            notifyTracks.append(notifyTrack)
            colorTrack = Sequence()
            colorTrack.append(Wait(2.0))
            colorTrack.append(Func(battle.movie.needRestoreColor))
            colorTrack.append(changeColor(headParts))
            colorTrack.append(changeColor(torsoParts))
            colorTrack.append(changeColor(legsParts))
            colorTrack.append(Wait(2.5))
            colorTrack.append(resetColor(headParts))
            colorTrack.append(resetColor(torsoParts))
            colorTrack.append(resetColor(legsParts))
            colorTrack.append(Func(battle.movie.clearRestoreColor))
            baseFlameTracks.append(baseFlameTrack)
            flameTracks.append(flameTrack)
            flecksTracks.append(flecksTrack)
            colorTracks.append(colorTrack)
    toonDamageTrack = getToonTracksCheat(attack, 1.5, ['slip-backward'], 1.3, ['sidestep'])
    return Parallel(notifyTracks, toonDamageTrack, soundTracks)

def doOverride(attack):
    suit = attack['suit']
    battle = attack['battle']

    phase2 = Func(suit.makeChainsawPhase2)
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 30))
    ceaseTrack = ActorInterval(suit, 'rake-react')
    ceaseSpeechTrack = Sequence(Func(suit.makeChainsawPhase2), Func(suit.setChatAbsolute,
                                     "PERSONALITY OVERRIDE ACTIVATED.",
                                     CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute,
                                     "PLEASE WAIT.",
                                     CFSpeech | CFTimeout), ActorInterval(suit, 'lured'), ActorInterval(suit, 'lured'), Func(suit.setNeutralAnimation), Func(suit.setChatAbsolute,
                                     "PERSONALITY OVERRIDE COMPLETE.",
                                     CFSpeech | CFTimeout), Wait(3.0),  Func(suit.setChatAbsolute,
                                     "ADDITIONAL ENTITIES IDENTIFIED. TERMINATION SEQUENCE IN PROGRESS.", CFSpeech | CFTimeout), ActorInterval(suit, 'neutral-override'), Func(suit.setNeutralAnimation))
    ceaseSpeechTrack.append(Wait(2.0))
    return Parallel(phase2, ceaseTrack, makeImmune, ceaseSpeechTrack)

def doOverridePhase3(attack):
    suit = attack['suit']
    battle = attack['battle']

    phase2 = Func(suit.makeChainsawPhase2)
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 30))
    ceaseTrack = ActorInterval(suit, 'rake-react')
    ceaseSpeechTrack = Sequence(Func(suit.makeChainsawPhase4), Func(suit.setChatAbsolute,
                                     "PERSONALITY OVERRIDE ACTIVATED.",
                                     CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute,
                                     "ADDITIONAL ENTITIES IDENTIFIED. TERMINATION SEQUENCE IN PROGRESS.", CFSpeech | CFTimeout), ActorInterval(suit, 'neutral-override'), Func(suit.setNeutralAnimation))
    ceaseSpeechTrack.append(Wait(2.0))
    return Parallel(ceaseTrack, makeImmune, ceaseSpeechTrack)

def doOverrideRemoval(attack):
    suit = attack['suit']
    battle = attack['battle']
    phase3 = Func(suit.makeChainsawPhase3)
    ceaseTrack = ActorInterval(suit, 'throttle')
    selfDamageTrack = Sequence(Func(suit.showHpTextNew, 0, text="+50% Damage!", colorCode=1))
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 20))
   # for headPart in suit.animatedHeadParts:
       # headInterval = ActorInterval(headPart, 'throttle')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_throttle_break.ogg'), node=suit))
    ceaseSpeechTrack = Sequence(Func(suit.setChatAbsolute,
                                     "DAMAGE TO- help- TO- help- TO OVER- me- OVERRIDE DE- toons- DETECTED.",
                                     CFSpeech | CFTimeout), Wait(3.0), ActorInterval(suit, 'lured'), ActorInterval(suit, 'lured'), Func(suit.setChatAbsolute,
                                                                            "ENTERING- i'm- ENTER- trying to- RECOVERY MO- resist it- MODE.",
                                                                            CFSpeech | CFTimeout), Func(suit.setNeutralAnimation), Wait(3.0),
                                Func(suit.setChatAbsolute,
                                     "ACTIVATING- i don't- TEMP- know- TEMPORARY- if i- REFOREST- can- REFORESTATION MODE.",
                                     CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute,
                                     "OVERRIDE- it- SEVERE- hurts- SEVERELY DAMA- let- DAMAGED. ATTEMPT- me- ATTEMPTING- OUT!! FINAL FALLBACK PROCEDURE.",
                                     CFSpeech | CFTimeout), Parallel(ceaseTrack, ceaseSoundTrack, Sequence(Wait(3.75), Func(suit.makeChainsawPhase3))),
                                Func(suit.setNeutralAnimation), selfDamageTrack)
    ceaseSpeechTrack.append(Wait(2.0))
    return Parallel(makeImmune, ceaseSpeechTrack)

def doOverrideRemovalPhase3(attack):
    suit = attack['suit']
    battle = attack['battle']
    phase3 = Func(suit.makeChainsawPhase3)
    ceaseTrack = ActorInterval(suit, 'throttletwo')
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, - 30))
   # for headPart in suit.animatedHeadParts:
     #   headInterval = ActorInterval(headPart, 'throttle2')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_throttle_hit.ogg'), node=suit))
    ceaseSpeechTrack = Sequence(Func(suit.setChatAbsolute,
                                     "DAMAGE TO- help- TO- help- TO OVER- me- OVERRIDE DE- toons- DETECTED.",
                                     CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute,
                                     "OVERRIDE- it- SEVERE- hurts- SEVERELY DAMA- let- DAMAGED. ATTEMPT- me- ATTEMPTING- OUT!! FINAL FALLBACK PROCEDURE.",
                                     CFSpeech | CFTimeout), Parallel(ceaseTrack, ceaseSoundTrack, Sequence(Wait(3.25), Func(suit.makeChainsawPhase3))),
                                Func(suit.setNeutralAnimation))
    ceaseSpeechTrack.append(Wait(2.0))
    return Parallel(ceaseSpeechTrack, makeImmune)

def doScabbard(attack):
    BattleParticles.loadParticles()
    theSuit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    liftTracks = Parallel()
    selfDamageTracks = Parallel()
    posPoints = [Point3(0, 0, 0), VBase3(0, 0, 180)]
    knifeTracks = Parallel()
    suitTracks = Parallel()
    for s in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        suitTrack.append(Func(s.checkScabbard))
        if not s.dna.name == 'dking':
            suitTrack.append(MovieUtil.zapCogPowerhouse(s, 'large-zap', .5, 2.0, battle))
            suitTrack.append(Func(s.setNeutralAnimationDrop))
        theSuit = attack['suit']
        can = loader.loadModel('phase_5/models/props/lightning')
        knifeTrack = Sequence(
            getPropAppearTrack(can, theSuit.getRightHand(), posPoints, 0, VBase3(.1, .1, .1),
                               scaleUpTime=0.25),
            Parallel(Wait(1.85), LerpHprInterval(can, 1.85, VBase3(180, 0, 180))),

            Parallel(
                getThrowTrack(can, (0, 0, s.getHeight() + 2.5), 1.5, s, -20.288),
                Func(can.setR, 0),
                LerpHprInterval(can, 1.5, VBase3(360, 0, 0))
            ),

            Wait(0.15),

            Parallel(
                LerpHprInterval(can, 0.45, VBase3(0, 0, 0)),
                LerpPosInterval(can, 0.45, (0, 0, s.getHeight() - 2.5), other=s, blendType='easeIn'),
                LerpScaleInterval(can, 0.45, VBase3(0.1, 0.1, 0.1), blendType='easeIn')
            ),

            Parallel(
                LerpScaleInterval(can, 0.2, VBase3(0.01, 0.01, 0.01)),
                LerpColorScaleInterval(can, 0.2, Vec4(1, 1, 1, 0))
            ),

            Func(can.removeNode)
        )
        knifeTracks.append(knifeTrack)
        suitTracks.append(suitTrack)
    suitTrack3 = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(theSuit, 'sticker', endTime=1.0), Wait(2.0), ActorInterval(theSuit, 'sticker', startTime=1.0), Func(theSuit.setNeutralAnimationDrop))
    soundTrack1 = getSoundTrack('AA_lightning.ogg', delay=3, node=theSuit)
    soundTrack2 = getSoundTrack('AA_cog_shock.ogg', delay=4.5, node=theSuit)
    return Parallel(suitTrack3, knifeTracks, suitTrack2, selfDamageTracks, suitTracks, soundTrack2, soundTrack1)

def doKickback(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(suit, 'pie-small-react'), Func(suit.setNeutralAnimationDrop))
    suitTrack.append(Wait(3.0))
    makeImmune = Func(suit.makeVulnerable)
    makeDamageUp = Parallel(Func(suit.checkVulnerabilityUp, + 50))
    selfDamageTrack = Func(suit.showHpTextNew, 0, text="KICKBACK!", colorCode=4)
    return Parallel(suitTrack, makeImmune, makeDamageUp, selfDamageTrack)

def doLayoffs(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    damageDelay = 1.7
    suitTrack2 = getSuitAnimTrack(attack)
    suitTrack = Sequence(ActorInterval(suit, 'layoffs', endTime=1.875), Wait(2), ActorInterval(suit, 'layoffs', startTime=1.875), Func(suit.setNeutralAnimationDrop))
    suitResponseTracks = Parallel()
    for targetSuit in battle.activeSuits:
        if not targetSuit.getManager():
            suitResponseTrack = Sequence()
            showDamage = Sequence(Func(targetSuit.showHpTextNew, -targetSuit.currHP, text="FIRED!", colorCode=1), Func(targetSuit.checkLayoffs))
            cannon = loader.loadModel('phase_5/models/props/cannon_cog')
            barrel = cannon.find('**/cannon')
            barrel.setHpr(0, 90, 0)
            cannonHolder = render.attachNewNode('CannonHolder')
            cannon.reparentTo(cannonHolder)
            cannon.setPos(0, 0, -8.6)
            cannonHolder.setPos(targetSuit.getPos(render))
            cannonHolder.setHpr(targetSuit.getHpr(render))
            cannonAttachPoint = barrel.attachNewNode('CannonAttach')
            kapowAttachPoint = barrel.attachNewNode('kapowAttach')
            scaleFactor = 1.6
            iScale = 1 / scaleFactor
            barrel.setScale(scaleFactor, 1, scaleFactor)
            cannonAttachPoint.setScale(iScale, 1, iScale)
            cannonAttachPoint.setPos(0, 6.7, 0)
            kapowAttachPoint.setPos(0, -0.5, 1.9)
            suitLevel = targetSuit.getActualLevel()
            if suitLevel > 12:
                suitLevel = 12
            deep = 2.5 + suitLevel * 0.2
            suitScale = 0.9
            import math
            suitScale = 0.9 - math.sqrt(suitLevel) * 0.1
            sival = []
            posInit = cannonHolder.getPos()
            posFinal = Point3(posInit[0] + 0.0, posInit[1] + 0.0, posInit[2] + 7.0)
            kapow = globalPropPool.getProp('kapow')
            kapow.reparentTo(kapowAttachPoint)
            kapow.hide()
            kapow.setScale(0.25)
            kapow.setBillboardPointEye()
            smoke = loader.loadModel('phase_4/models/props/test_clouds')
            smoke.reparentTo(cannonAttachPoint)
            smoke.setScale(0.5)
            smoke.hide()
            smoke.setBillboardPointEye()
            soundBomb = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_fire_alt.ogg')
            playSoundBomb = SoundInterval(soundBomb)
            soundFly = base.loader.loadSfx('phase_4/audio/sfx/firework_whistle_01.ogg')
            playSoundFly = SoundInterval(soundFly)
            soundCannonAdjust = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_adjust.ogg')
            playSoundCannonAdjust = SoundInterval(soundCannonAdjust, duration=0.6)
            soundCogPanic = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogafssm.ogg')
            playSoundCogPanic = SoundInterval(soundCogPanic)
            reactIval = Parallel(Sequence(Wait(0.0),
                                  LerpPosInterval(cannonHolder, 2.0, posFinal,
                                                  startPos=posInit,
                                                  blendType='easeInOut'),
                                  Parallel(LerpHprInterval(barrel, 0.6,
                                                           Point3(0, 0, 0),
                                                           startHpr=Point3(0,
                                                                           90,
                                                                           0),
                                                           blendType='easeIn'),
                                           playSoundCannonAdjust), Wait(2.0),
                                  Parallel(LerpHprInterval(barrel, 0.6,
                                                           Point3(0, 0, 0),
                                                           startHpr=Point3(0,
                                                                           0,
                                                                           0),
                                                           blendType='easeIn'),
                                           playSoundCannonAdjust),
                                  LerpPosInterval(cannonHolder, 1.0, posInit,
                                                  startPos=posFinal,
                                                  blendType='easeInOut'), Func(cannonHolder.remove)),
                         Sequence(Wait(0.0),
                                  Parallel(Sequence(ActorInterval(targetSuit, 'flail'), Func(targetSuit.setNeutralAnimationTrap)),
                                           targetSuit.scaleInterval(1.0, suitScale),
                                           LerpPosInterval(targetSuit, 0.25, Point3(0, -1.0, 0.0)),
                                           Sequence(Wait(0.25), Parallel(playSoundCogPanic,
                                                                         LerpPosInterval(targetSuit, 1.5,
                                                                                         Point3(0, -deep,
                                                                                                0.0),
                                                                                         blendType='easeIn')))),
                                  Wait(1.5), Parallel(playSoundBomb, playSoundFly, Sequence(Func(smoke.show), Parallel(
                                 LerpScaleInterval(smoke, 0.5, 3),
                                 LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.hide)),
                                                      Sequence(Func(kapow.show),
                                                               ActorInterval(kapow, 'kapow'), Func(kapow.hide)),
                                                      LerpPosInterval(targetSuit, 0.25, Point3(0, 100.0, 0.0)),
                                                      targetSuit.scaleInterval(0.25, 0.01)), Func(targetSuit.hide)))
            sival = Sequence(Parallel(Func(targetSuit.reparentTo, cannonAttachPoint), Func(targetSuit.setPos, (0, 0, 0)), Func(targetSuit.setHpr, (0, -90, 0)), reactIval, MovieUtil.createSuitStunIntervalFired(targetSuit, 0.3, 1.3)))
            suitResponseTrack.append(Wait(0.5))
            suitResponseTrack.append(showDamage)
            suitResponseTrack.append(sival)
            suitResponseTracks.append(suitResponseTrack)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(4.25))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=5))
    toonTracks = getToonTracks(attack, 4.25, ['slip-forward'], 6, ['jump'])
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=4.25, node=suit)
    return Parallel(suitTrack, explosionTrack, suitTrack2, suitResponseTracks, soundTrack1, toonTracks)

def doOffboarding(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    damageDelay = 1.7
    targetSuit = battle.activeSuits[ind]
    suitTrack2 = getSuitAnimTrack(attack)
    suitTrack = Sequence(ActorInterval(suit, 'snap'), Func(suit.setNeutralAnimationDrop))
    suitResponseTracks = Parallel()
    suitResponseTrack = Sequence()
    showDamage = Sequence(Func(targetSuit.showHpTextNew, -targetSuit.currHP, text="FIRED!", colorCode=1), Func(targetSuit.checkLayoffs))
    cannon = loader.loadModel('phase_5/models/props/cannon_cog')
    barrel = cannon.find('**/cannon')
    barrel.setHpr(0, 90, 0)
    cannonHolder = render.attachNewNode('CannonHolder')
    cannon.reparentTo(cannonHolder)
    cannon.setPos(0, 0, -8.6)
    cannonHolder.setPos(targetSuit.getPos(render))
    cannonHolder.setHpr(targetSuit.getHpr(render))
    cannonAttachPoint = barrel.attachNewNode('CannonAttach')
    kapowAttachPoint = barrel.attachNewNode('kapowAttach')
    scaleFactor = 1.6
    iScale = 1 / scaleFactor
    barrel.setScale(scaleFactor, 1, scaleFactor)
    cannonAttachPoint.setScale(iScale, 1, iScale)
    cannonAttachPoint.setPos(0, 6.7, 0)
    kapowAttachPoint.setPos(0, -0.5, 1.9)
    suitLevel = targetSuit.getActualLevel()
    if suitLevel > 12:
        suitLevel = 12
    deep = 2.5 + suitLevel * 0.2
    suitScale = 0.9
    import math
    suitScale = 0.9 - math.sqrt(suitLevel) * 0.1
    sival = []
    posInit = cannonHolder.getPos()
    posFinal = Point3(posInit[0] + 0.0, posInit[1] + 0.0, posInit[2] + 7.0)
    kapow = globalPropPool.getProp('kapow')
    kapow.reparentTo(kapowAttachPoint)
    kapow.hide()
    kapow.setScale(0.25)
    kapow.setBillboardPointEye()
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.reparentTo(cannonAttachPoint)
    smoke.setScale(0.5)
    smoke.hide()
    smoke.setBillboardPointEye()
    soundBomb = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_fire_alt.ogg')
    playSoundBomb = SoundInterval(soundBomb)
    soundFly = base.loader.loadSfx('phase_4/audio/sfx/firework_whistle_01.ogg')
    playSoundFly = SoundInterval(soundFly)
    soundCannonAdjust = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_adjust.ogg')
    playSoundCannonAdjust = SoundInterval(soundCannonAdjust, duration=0.6)
    soundCogPanic = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogafssm.ogg')
    playSoundCogPanic = SoundInterval(soundCogPanic)
    reactIval = Parallel(Sequence(Wait(0.0),
                          LerpPosInterval(cannonHolder, 2.0, posFinal,
                                          startPos=posInit,
                                          blendType='easeInOut'),
                          Parallel(LerpHprInterval(barrel, 0.6,
                                                   Point3(0, 0, 0),
                                                   startHpr=Point3(0,
                                                                   90,
                                                                   0),
                                                   blendType='easeIn'),
                                   playSoundCannonAdjust), Wait(2.0),
                          Parallel(LerpHprInterval(barrel, 0.6,
                                                   Point3(0, 0, 0),
                                                   startHpr=Point3(0,
                                                                   0,
                                                                   0),
                                                   blendType='easeIn'),
                                   playSoundCannonAdjust),
                          LerpPosInterval(cannonHolder, 1.0, posInit,
                                          startPos=posFinal,
                                          blendType='easeInOut'), Func(cannonHolder.remove)),
                 Sequence(Wait(0.0),
                          Parallel(Sequence(ActorInterval(targetSuit, 'flail'), Func(targetSuit.setNeutralAnimationTrap)),
                                   targetSuit.scaleInterval(1.0, suitScale),
                                   LerpPosInterval(targetSuit, 0.25, Point3(0, -1.0, 0.0)),
                                   Sequence(Wait(0.25), Parallel(playSoundCogPanic,
                                                                 LerpPosInterval(targetSuit, 1.5,
                                                                                 Point3(0, -deep,
                                                                                        0.0),
                                                                                 blendType='easeIn')))),
                          Wait(1.5), Parallel(playSoundBomb, playSoundFly, Sequence(Func(smoke.show), Parallel(
                         LerpScaleInterval(smoke, 0.5, 3),
                         LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.hide)),
                                              Sequence(Func(kapow.show),
                                                       ActorInterval(kapow, 'kapow'), Func(kapow.hide)),
                                              LerpPosInterval(targetSuit, 0.25, Point3(0, 100.0, 0.0)),
                                              targetSuit.scaleInterval(0.25, 0.01)), Func(targetSuit.hide)))
    sival = Sequence(Parallel(Func(targetSuit.reparentTo, cannonAttachPoint), Func(targetSuit.setPos, (0, 0, 0)), Func(targetSuit.setHpr, (0, -90, 0)), reactIval, MovieUtil.createSuitStunIntervalFired(targetSuit, 0.3, 1.3)))
    suitResponseTrack.append(Wait(0.5))
    suitResponseTrack.append(showDamage)
    suitResponseTrack.append(sival)
    suitResponseTracks.append(suitResponseTrack)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(4.25))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=5))
    toonTracks = getToonTrack(attack, 4.25, ['slip-forward'], 6, ['jump'])
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=4.25, node=suit)
    soundTrack = getSoundTrack('SA_bash.ogg', delay=0)
    return Parallel(suitTrack, explosionTrack, soundTrack, suitTrack2, suitResponseTracks, soundTrack1, toonTracks)

def doAggrandize(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[ind]
    damageDelay = 1.7
    targetPos = targetSuit.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitPos = targetSuit.getPos(battle)
    y = suitPos.getY()
    dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
    dustCloud.setBillboardAxis(2.0)
    dustCloud.setZ(3)
    dustCloud.setScale(0.4)
    dustCloud.createTrack()
    dustCloudHideIval = Sequence(Func(dustCloud.reparentTo, targetSuit), Func(dustCloud.setPos,
                                                                        Point3(suitPos.getX(), 0,
                                                                               0)),
                                 dustCloud.track, Func(dustCloud.removeNode), Wait(1.7), name='dustCloadIval')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    selfDamageTrack = Sequence(Wait(1.0), Parallel(dustCloudHideIval, ActorInterval(targetSuit, 'slip-forward', startTime=2.43),
                                                   Func(targetSuit.makeIntoCTSManager),
                                                   Func(targetSuit.showHpString, "PROMOTION!"), Func(targetSuit.setMaxHP, 1000), Func(targetSuit.setManager, 1), Func(targetSuit.makeShielding),
                                                   Func(targetSuit.updateHealthBar, 0)),
                               Func(targetSuit.setNeutralAnimation), Func(battle.unSueSuit, targetSuit))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=1.0)
    soundTrack = getSoundTrack('SA_bash.ogg', delay=0)
    return Parallel(suitTrack, selfDamageTrack, soundTrack, soundTrack2)

def setPosFromOther(dest, source, offset = Point3(0, 0, 0)):
    pos = render.getRelativePoint(source, offset)
    dest.setPos(pos)
    dest.reparentTo(render)

def __getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    pEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) == 3:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))

def doMandatoryToll(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    for headPart in suit.animatedHeadParts:
        head = headPart
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(0.5))
    makeDanceSessions = Parallel()
    targets = attack['target']
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        makeDanceSession = Sequence(Wait(2.0), Func(toon.showHpTextNew, 0, text="+%s Toll!" % dmg, colorCode=1), Func(toon.makeMandatoryToll), Func(toon.checkMandatoryToll, +dmg), ActorInterval(toon, 'confused'), Func(toon.loop, 'neutral'))
        if dmg > 0:
            makeDanceSessions.append(makeDanceSession)
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    suitTrack2 = Parallel(getSuitAnimTrack(attack), Func(suit.createSuitBellInterval))
    soundTrack = getSoundTrack('SA_healing_bell.ogg')
    return Parallel(suitTrack2, soundTrack, makeDanceSessions, sprayTrack)

def doLedgerOfSoundOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    for headPart in suit.animatedHeadParts:
        head = headPart
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(0.5))
    makeDanceSessions = Parallel()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    suitTrack2 = Parallel(getSuitAnimTrack(attack), Func(suit.createSuitBellInterval), Func(suit.showHpTextNew, 0, text="+5% Damage!", colorCode=1), Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 5))
    soundTrack = getSoundTrack('SA_healing_bell.ogg')
    return Parallel(suitTrack2, soundTrack, sprayTrack)

def donothing(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    sprayEffects = [BattleParticles.createParticleEffect(file='spinSpray') for t in targets]
    suitTrack = Sequence(getSuitAnimTrack(attack))
    sprayTracks = getPartTracks(attack, sprayEffects, 1.0, 1.9, 0)
    spinTracks1 = Parallel()
    spinTracks2 = Parallel()
    spinTracks3 = Parallel()
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    #toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTracks = Parallel()
    toonSpinTracks = Parallel()
    nothingTrack = Sequence(Wait(1.0))
    notifyTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        BattleParticles.loadParticles()
        spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
        spinEffect1.reparentTo(toon)
        spinEffect2.reparentTo(toon)
        spinEffect3.reparentTo(toon)
        height1 = toon.getHeight() * (random.random() * 0.2 + 0.7)
        height2 = toon.getHeight() * (random.random() * 0.2 + 0.4)
        height3 = toon.getHeight() * (random.random() * 0.2 + 0.1)
        spinEffect1.setPos(0.8, -0.7, height1)
        spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect1.setHpr(spinEffect1, 0, 50, 0)
        spinEffect2.setPos(0.8, -0.7, height2)
        spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect2.setHpr(spinEffect2, 0, 50, 0)
        spinEffect3.setPos(0.8, -0.7, height3)
        spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect3.setHpr(spinEffect3, 0, 50, 0)
        spinEffect1.wrtReparentTo(battle)
        spinEffect2.wrtReparentTo(battle)
        spinEffect3.wrtReparentTo(battle)
        if dmg > 0:
            spinTracks1.append(getPartTrack(spinEffect1, 1.5, 5.9, [spinEffect1, battle, 0], softStop=-2))
            spinTracks2.append(getPartTrack(spinEffect2, 1.5, 5.9, [spinEffect2, battle, 0], softStop=-2))
            spinTracks3.append(getPartTrack(spinEffect3, 1.5, 5.9, [spinEffect3, battle, 0], softStop=-2))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0))
            toonSpinTracks.append(Sequence(Func(toon.makeUnMandatoryToll), Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))
    toonDamageTrack = getToonTracks(attack, damageDelay=damageDelay + 0.9, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['neutral'], showDamageExtraTime=1.0)
    soundTracks.append(Sequence(getSoundTrack('SA_life_insurance_loop.ogg', delay=2.0), getSoundTrack('SA_life_insurance_loop.ogg'), getSoundTrack('SA_life_insurance_loop.ogg')))
    return Parallel(toonTracks, toonSpinTracks, toonDamageTrack, suitTrack, spinTracks1, spinTracks2, spinTracks3, soundTracks)

def doMandatoryTollFinal(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    for headPart in suit.animatedHeadParts:
        head = headPart
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(0.5))
    makeDanceSessions = Parallel()
    targets = attack['target']
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        makeDanceSession = Sequence(Wait(2.0), Func(toon.showHpTextNew, 0, text="+8 Toll!", colorCode=1), Func(toon.makeMandatoryToll), Func(toon.checkMandatoryToll, +8), ActorInterval(toon, 'confused'), Func(toon.loop, 'neutral'))
        if dmg > 0:
            makeDanceSessions.append(makeDanceSession)
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    sprayTrack.append(doMandatoryTollFinal2(attack))
    suitTrack2 = Parallel(getSuitAnimTrack(attack), Func(suit.createSuitBellInterval))
    soundTrack = Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/LB_bell_long.ogg'), node=suit)
    return Parallel(suitTrack2, soundTrack, sprayTrack)

def doMandatoryTollFinal2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(ActorInterval(suit, 'snap'), Func(suit.setNeutralAnimationDrop))
    propTracks = Parallel()
    toonTracks = Parallel()
    smokeTracks = Parallel()
    soundTrack4 = getSoundTrack('AA_drop_safe_miss.ogg', delay=2, node=suit)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        piano = globalPropPool.getProp('piano')
        safe = loader.loadModel('phase_4/models/accessories/bosses/backpack_bellringer')
        boulder = globalPropPool.getProp('boulder')
        weight = globalPropPool.getProp('weight')
        toonPos = toon.getPos(battle)
        toonHpr = battle.getActorPosHpr(toon)
        y = toonPos.getY()
        propPos = Point3(toonPos.getX(), y, 50)
        soundTrack2 = getSoundTrack('AA_drop_piano.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack3 = getSoundTrack('AA_drop_boulder.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack5 = getSoundTrack('AA_drop_bigweight.ogg', delay=1.75, duration=2.0, node=suit)
        propTrack2 = Sequence(Func(safe.reparentTo, battle),
            getPropAppearTrack(safe, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(10), scaleUpTime=1.5),
            LerpPosInterval(safe, 0.5, Point3(toonPos.getX(), y, 2.5)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 3.5)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 2.5)), Sequence(
                Wait(1.5),
                LerpScaleInterval(safe, .25, MovieUtil.PNT3_ZERO)
            ))
        if dmg > 0:
            propTracks.append(Parallel(propTrack2))
        toonTrack = Sequence(
        Wait(2),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpTextNew,  - int(dmg)),
            #Func(__doDamageCheat, toon, dmg, t['died'])
        ),
        Wait(1.75),
        Parallel(
            Sequence(
                Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
        )
        if dmg > 0:
            toonTracks.append(toonTrack)
            toonTracks.append(Func(toon.makeUnMandatoryToll))
            smokeTracks.append(smokeTrack)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    toonDamageTrack = getToonTracksCheat(attack, 2.25, ['nothing'], 0, ['neutral'])
    return Parallel(suitTrack, toonDamageTrack, soundTrack4, smokeTracks, toonTracks, soundTrack, propTracks)

def doEmbezzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    bill = loader.loadModel('phase_3.5/models/props/jellybean4')
    bill.setH(0)
    bill.setColor(1,0.9,0)
    glow = loader.loadModel("phase_3.5/models/props/glow.bam")
    glow.reparentTo(bill)
    glow.setScale(0.5)
    glow.setPos(0,0,0)
    glow.setColorScale(Vec4(1, 0.9, 0, 0.3))
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(1.0))
    billPosPoints = [Point3(-0.21707670043415206, 0.30390738060781786, -0.4775687409551388), VBase3(-301.64978292329954, 0, 0)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.25, 1.0, scaleUpPoint=Point3(2.0, 2.0, 2.0))
    toonTrack = getToonTrackCheat(attack, 0.25, ['cringe'], 0.01, ['sidestep'])
    glowTrack = Sequence()
    glowTrack.append(Wait(4.0))
    glowTrack.append(Func(glow.hide))
    glowTrack.append(Func(glow.removeNode))
    notifyTrack = Sequence(Wait(0.25), Func(toon.showHpTextNew, - int(dmg)))
    multiTrackList = Parallel(suitTrack, notifyTrack, toonTrack, glowTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('ttr_s_ene_bat_embezzle.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doResonanceTax(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.25)
    suitType = getSuitBodyType(attack['suitName'])
    damageSuits = []
    calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    sprayEffect = BattleParticles.createParticleEffect(file='organizeSpray')
    spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect1.reparentTo(targetSuit)
    spinEffect2.reparentTo(targetSuit)
    spinEffect3.reparentTo(targetSuit)
    height1 = targetSuit.getHeight() - (targetSuit.getHeight() / 3)
    height2 = targetSuit.getHeight() - (targetSuit.getHeight() / 2)
    height3 = targetSuit.getHeight() - (targetSuit.getHeight() / 1.25)
    spinEffect1.setPos(0.8, -0.7, height1)
    spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect1.setHpr(spinEffect1, 0, 50, 0)
    spinEffect2.setPos(0.8, -0.7, height2)
    spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect2.setHpr(spinEffect2, 0, 50, 0)
    spinEffect3.setPos(0.8, -0.7, height3)
    spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect3.setHpr(spinEffect3, 0, 50, 0)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 1.1, 5.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 1.1, 5.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 1.1, 5.9, [spinEffect3, suit, 0], softStop=-2)
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, 0, text="+5% Damage!", colorCode=1), Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 5))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doResonanceTax2(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.25)
    suitType = getSuitBodyType(attack['suitName'])
    damageSuits = []
    calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    sprayEffect = BattleParticles.createParticleEffect(file='organizeSpray')
    spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect1.reparentTo(targetSuit)
    spinEffect2.reparentTo(targetSuit)
    spinEffect3.reparentTo(targetSuit)
    height1 = targetSuit.getHeight() - (targetSuit.getHeight() / 3)
    height2 = targetSuit.getHeight() - (targetSuit.getHeight() / 2)
    height3 = targetSuit.getHeight() - (targetSuit.getHeight() / 1.25)
    spinEffect1.setPos(0.8, -0.7, height1)
    spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect1.setHpr(spinEffect1, 0, 50, 0)
    spinEffect2.setPos(0.8, -0.7, height2)
    spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect2.setHpr(spinEffect2, 0, 50, 0)
    spinEffect3.setPos(0.8, -0.7, height3)
    spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect3.setHpr(spinEffect3, 0, 50, 0)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 1.1, 5.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 1.1, 5.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 1.1, 5.9, [spinEffect3, suit, 0], softStop=-2)
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, 0, text="+10% Damage!", colorCode=1), Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 10))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doResonanceTax3(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.25)
    suitType = getSuitBodyType(attack['suitName'])
    damageSuits = []
    calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    sprayEffect = BattleParticles.createParticleEffect(file='organizeSpray')
    spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect1.reparentTo(targetSuit)
    spinEffect2.reparentTo(targetSuit)
    spinEffect3.reparentTo(targetSuit)
    height1 = targetSuit.getHeight() - (targetSuit.getHeight() / 3)
    height2 = targetSuit.getHeight() - (targetSuit.getHeight() / 2)
    height3 = targetSuit.getHeight() - (targetSuit.getHeight() / 1.25)
    spinEffect1.setPos(0.8, -0.7, height1)
    spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect1.setHpr(spinEffect1, 0, 50, 0)
    spinEffect2.setPos(0.8, -0.7, height2)
    spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect2.setHpr(spinEffect2, 0, 50, 0)
    spinEffect3.setPos(0.8, -0.7, height3)
    spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect3.setHpr(spinEffect3, 0, 50, 0)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 1.1, 5.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 1.1, 5.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 1.1, 5.9, [spinEffect3, suit, 0], softStop=-2)
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, 0, text="+15% Damage!", colorCode=1),
                               Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 15))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doResonanceTax4(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.25)
    suitType = getSuitBodyType(attack['suitName'])
    damageSuits = []
    calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    sprayEffect = BattleParticles.createParticleEffect(file='organizeSpray')
    spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect1.reparentTo(targetSuit)
    spinEffect2.reparentTo(targetSuit)
    spinEffect3.reparentTo(targetSuit)
    height1 = targetSuit.getHeight() - (targetSuit.getHeight() / 3)
    height2 = targetSuit.getHeight() - (targetSuit.getHeight() / 2)
    height3 = targetSuit.getHeight() - (targetSuit.getHeight() / 1.25)
    spinEffect1.setPos(0.8, -0.7, height1)
    spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect1.setHpr(spinEffect1, 0, 50, 0)
    spinEffect2.setPos(0.8, -0.7, height2)
    spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect2.setHpr(spinEffect2, 0, 50, 0)
    spinEffect3.setPos(0.8, -0.7, height3)
    spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect3.setHpr(spinEffect3, 0, 50, 0)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 1.1, 5.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 1.1, 5.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 1.1, 5.9, [spinEffect3, suit, 0], softStop=-2)
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, 0, text="+20% Damage!", colorCode=1),
                                Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 20))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doResonanceTax5(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.25)
    suitType = getSuitBodyType(attack['suitName'])
    damageSuits = []
    calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    sprayEffect = BattleParticles.createParticleEffect(file='organizeSpray')
    spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
    spinEffect1.reparentTo(targetSuit)
    spinEffect2.reparentTo(targetSuit)
    spinEffect3.reparentTo(targetSuit)
    height1 = targetSuit.getHeight() - (targetSuit.getHeight() / 3)
    height2 = targetSuit.getHeight() - (targetSuit.getHeight() / 2)
    height3 = targetSuit.getHeight() - (targetSuit.getHeight() / 1.25)
    spinEffect1.setPos(0.8, -0.7, height1)
    spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect1.setHpr(spinEffect1, 0, 50, 0)
    spinEffect2.setPos(0.8, -0.7, height2)
    spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect2.setHpr(spinEffect2, 0, 50, 0)
    spinEffect3.setPos(0.8, -0.7, height3)
    spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
    spinEffect3.setHpr(spinEffect3, 0, 50, 0)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 1.1, 5.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 1.1, 5.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 1.1, 5.9, [spinEffect3, suit, 0], softStop=-2)
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, 0, text="+25% Damage!", colorCode=1),
                                 Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 25))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doBalanceTheLedger(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    suitTracks = Parallel()
    dmg = attack['target'][0]['hp']
    for suit in battle.activeSuits:
        suitTracks.append(Parallel(suit.makeBalanceTheLedgerInterval(dmg, battle, int(math.ceil(dmg * .05)))))
        if suit.getManager():
            suitTracks.append(Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + int(math.ceil(dmg * .05)))))
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(0.5))
    makeDanceSessions = Parallel()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, theSuit, Point3(0, 1.6, theSuit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, theSuit, 0], softStop=-3.5))
    suitTrack3 = Parallel(getSuitAnimTrack(attack), Func(theSuit.createSuitBellInterval))
    suitTrack2 = Sequence(Parallel(
    getSuitAnimTrack(attack),

    ActorInterval(theSuit, 'sacrifice-cog', startTime=2.25, endTime=4.25)),

    Parallel(Func(theSuit.enableBlend),
        ActorInterval(theSuit, 'neutral', loop=1),
        LerpAnimInterval(
            theSuit,
            duration=.75,
            startAnim='sacrifice-cog',
            endAnim='neutral',
            startWeight=0.0,
            endWeight=1.0,
            blendType='easeInOut'
        )
    ),

    Func(theSuit.disableBlend),
    Func(theSuit.setNeutralAnimationDrop)
)
    soundTrack = getSoundTrack('SA_healing_bell.ogg')
    soundTrack2 = getSoundTrack('ENC_cogjump_to_side2.ogg', delay=1, node=theSuit)
    return Parallel(suitTrack2, suitTracks, suitTrack3, soundTrack, soundTrack2, sprayTrack)

def doBalanceTheLedger2(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTracks.append(Parallel(suit.makeBalanceTheLedgerInterval(200, battle, 2)))
        suitTracks.append(Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 10)))
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(0.5))
    makeDanceSessions = Parallel()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, theSuit, Point3(0, 1.6, theSuit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, theSuit, 0], softStop=-3.5))
    suitTrack3 = Parallel(getSuitAnimTrack(attack), Func(theSuit.createSuitBellInterval))
    suitTrack2 = Sequence(ActorInterval(theSuit, 'sacrifice-cog', startTime=2.25), Func(theSuit.setNeutralAnimationDrop), Wait(6.0))
    soundTrack = getSoundTrack('SA_healing_bell.ogg')
    soundTrack2 = getSoundTrack('ENC_cogjump_to_side2.ogg', delay=1.5, node=theSuit)
    return Parallel(suitTrack2, suitTracks, suitTrack3, soundTrack, soundTrack2, sprayTrack)

def doBalanceTheLedger3(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTracks.append(Parallel(suit.makeBalanceTheLedgerInterval(300, battle, 3)))
        suitTracks.append(Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 15)))
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(0.5))
    makeDanceSessions = Parallel()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, theSuit, Point3(0, 1.6, theSuit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, theSuit, 0], softStop=-3.5))
    suitTrack3 = Parallel(getSuitAnimTrack(attack), Func(theSuit.createSuitBellInterval))
    suitTrack2 = Sequence(ActorInterval(theSuit, 'sacrifice-cog', startTime=2.25), Func(theSuit.setNeutralAnimationDrop), Wait(6.0))
    soundTrack = getSoundTrack('SA_healing_bell.ogg')
    soundTrack2 = getSoundTrack('ENC_cogjump_to_side2.ogg', delay=1, node=theSuit)
    return Parallel(suitTrack2, suitTracks, suitTrack3, soundTrack, soundTrack2, sprayTrack)

def doBalanceTheLedger4(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTracks.append(Parallel(suit.makeBalanceTheLedgerInterval(400, battle, 4)))
        suitTracks.append(Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 20)))
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(0.5))
    makeDanceSessions = Parallel()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, theSuit, Point3(0, 1.6, theSuit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, theSuit, 0], softStop=-3.5))
    suitTrack3 = Parallel(getSuitAnimTrack(attack), Func(theSuit.createSuitBellInterval))
    suitTrack2 = Sequence(ActorInterval(theSuit, 'sacrifice-cog', startTime=2.25), Func(theSuit.setNeutralAnimationDrop), Wait(6.0))
    soundTrack = getSoundTrack('SA_healing_bell.ogg')
    soundTrack2 = getSoundTrack('ENC_cogjump_to_side2.ogg', delay=1, node=theSuit)
    return Parallel(suitTrack2, suitTracks, suitTrack3, soundTrack, soundTrack2, sprayTrack)

def doBalanceTheLedger5(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTracks.append(Parallel(suit.makeBalanceTheLedgerInterval(500, battle, 5)))
        suitTracks.append(Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 25)))
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(0.5))
    makeDanceSessions = Parallel()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, theSuit, Point3(0, 1.6, theSuit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, theSuit, 0], softStop=-3.5))
    suitTrack3 = Parallel(getSuitAnimTrack(attack), Func(theSuit.createSuitBellInterval))
    suitTrack2 = Sequence(ActorInterval(theSuit, 'sacrifice-cog', startTime=2.25), Func(theSuit.setNeutralAnimationDrop), Wait(6.0))
    soundTrack = getSoundTrack('SA_healing_bell.ogg')
    soundTrack2 = getSoundTrack('ENC_cogjump_to_side2.ogg', delay=1, node=theSuit)
    return Parallel(suitTrack2, suitTracks, suitTrack3, soundTrack, soundTrack2, sprayTrack)

def doLedgerOfSound(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    explosionTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    suitTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        leftPosPoints = [Point3(0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.5, 5, suit.height - 2.5), MovieUtil.PNT3_ZERO]
        explosionTrack = Sequence()
        explosionTrack.append(Wait(1.5))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        leftKnives = []
        rightKnives = []
        for i in xrange(0, 3):
            leftKnives.append(globalPropPool.getProp('dagger'))
            rightKnives.append(globalPropPool.getProp('dagger'))

        for i in xrange(0, 3):
            knifeDelay = 0.11
            leftTrack = Sequence()
            leftTrack.append(Wait(1.1))
            leftTrack.append(Wait(i * knifeDelay))
            leftTrack.append(
                getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                               hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                leftKnifeTracks.append(leftTrack)
            rightTrack = Sequence()
            rightTrack.append(Wait(1.1))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(
                getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                                hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                rightKnifeTracks.append(rightTrack)

        notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextNew, - int(dmg), text="SNIPED!", colorCode=4))
        #toonTrack = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
        soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=1.5, node=suit)
        suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.makeVulnerable), Func(suit.checkVulnerabilityUp, + 5), Parallel(Func(suit.showHpTextNew, 0, text="+5% Vulnerable!", colorCode=4)),
                             Func(suit.setNeutralAnimationDrop))
        suitTrack.append(Wait(2.0))
        if dmg > 0:
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            explosionTracks.append(explosionTrack)
            suitTracks.append(suitTrack)
            origH = suit.getH(battle)

            # Calculate heading to toon
            origPos, origHpr = battle.getActorPosHpr(suit)
            origPos2 = suit.getPos(battle)
            suit.setPos(battle, origPos)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)

            # Restore original heading
            suit.setH(battle, origH)
            suit.setPos(battle, origPos2)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            suitTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'glower'),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            notifyTracks.append(notifyTrack)
    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                         dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, toonDamageTrack, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)
