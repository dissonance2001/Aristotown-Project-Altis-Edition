from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
from direct.showutil import Effects
from toontown.battle import SuitBattleGlobals
from toontown.battle.BattleProps import *
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

def doOverheat(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    partTracks4 = Parallel()
    notifyTracks = Parallel()
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()
    colorTracks = Parallel()
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        BattleParticles.loadParticles()
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
        baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 3.9, [baseFlameSmall, toon, 0], softStop=-1)
        flameSmallTrack = getPartTrack(flameSmall, 1.0, 3.9, [flameSmall, toon, 0], softStop=-1)
        flecksSmallTrack = getPartTrack(flecksSmall, 1.8, 2.1, [flecksSmall, toon, 0], softStop=-1)

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
        sprayEffect = BattleParticles.createParticleEffect('BurnSpray')
        sprayEffect2 = BattleParticles.createParticleEffect('BurnSpray')
        BattleParticles.setEffectTexture(sprayEffect2, 'fire')
        BattleParticles.setEffectTexture(sprayEffect, 'fire')
        partTrack4 = getPartTrack(sprayEffect, 1, 3.25, [sprayEffect2, toon, 0], softStop=-1)
        notifyTrack = Sequence(Wait(1.5), Func(toon.showHpTextNew, -int(dmg), text="SMOKED!", colorCode=4))
        if dmg > 0:
            partTracks4.append(partTrack4)
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
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
            notifyTracks.append(notifyTrack)
            notifyTracks.append(Parallel(Func(toon.makeBurned), Func(toon.addBurnedRounds, 4)))
            baseFlameTracks.append(baseFlameTrack)
            flameTracks.append(flameTrack)
            flecksTracks.append(flecksTrack)
            colorTracks.append(colorTrack)
            baseFlameTracks.append(baseFlameSmallTrack)
            flameTracks.append(flameSmallTrack)
            flecksTracks.append(flecksSmallTrack)
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.7,
                        0.62])
    damageAnims.append(['slip-forward',
                        1e-05,
                        0.4,
                        1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=1.2))
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    toonTracks = getToonTracksCheat(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3,
                                    dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_boilerplate_a.ogg', delay=1.0, node=suit)
    if hitAtleastOneToon == True:
        multiTrackList = Parallel(suitTrack, baseFlameTracks, notifyTracks, flameTracks, partTracks4, flecksTracks,
                                  toonTracks, colorTracks, soundTrack)
    else:
        multiTrackList = Parallel()
    return multiTrackList

def doRolled(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles() # We need to be able to change the color of the particle effects.
    damageDelay = 1.7
    toonAnimTracks = Parallel()
    # We want to handle the particle effect differently from Spin since we will be customizing these particle effects.
    sprayEffects = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
        sprayEffects.append(sprayEffect)

    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
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
    toonTracks = getToonTracksCheat(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, splicedDodgeAnims=damageAnims, showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTracks = Parallel()
    toonSpinTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonAnimTracks.append(Sequence(Wait(damageDelay + 0.9), ActorInterval(toon, 'think', playRate=0.75), Func(toon.loop, 'neutral')))
        spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
        BattleParticles.setEffectTexture(spinEffect1, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
        BattleParticles.setEffectTexture(spinEffect2, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
        BattleParticles.setEffectTexture(spinEffect3, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
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
        spinTracks1.append(getPartTrack(spinEffect1, 1.5, 5.9, [spinEffect1, battle, 0], softStop=-2))
        spinTracks2.append(getPartTrack(spinEffect2, 1.5, 5.9, [spinEffect2, battle, 0], softStop=-2))
        spinTracks3.append(getPartTrack(spinEffect3, 1.5, 5.9, [spinEffect3, battle, 0], softStop=-2))
        soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit))
        toonSpinTracks.append(Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))

    return Parallel(suitTrack, sprayTracks, toonTracks, toonAnimTracks, toonSpinTracks, spinTracks1, spinTracks2, spinTracks3, soundTracks)

def doHurrySickness(attack):
    suit = attack['suit']
    battle = attack['battle']
    damageDelay = 1.5
    suitTrack = getSuitAnimTrack(attack)
    targets = attack['target']
    notifyTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            suitTracks.append(getSuitAnimTrackAttack(attack))
            soundTracks.append(getSoundTrack('SA_hurry_sickness.ogg', delay=0, node=suit))
            soundTracks.append(getSoundTrack('SA_finger_wag.ogg', delay=1.3, node=suit))
            notifyTracks.append(Sequence(Wait(1.5), Parallel(Func(toon.showHpTextNew, -int(dmg)))))
            notifyTracks.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 2)))
            notifyTracks.append(Parallel(Func(toon.checkDamageDown, 40)))
    toonTracks = getToonTracksCheat(attack, damageDelay, ['slip-backward'], 0, ['nothing'])
    return Parallel(suitTracks, toonTracks, notifyTracks, soundTracks)

def doOverseer(attack):
    suit = attack['suit']
    battle = attack['battle']
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=0, node=suit)
    dmg = attack['target'][0]['hp']
    suit.addPendingQueuedHealing(dmg)
    suitTrack = Sequence(Func(suit.showHpTextNew, +dmg), Func(suit.setHealthForMe, +dmg),
                               Func(suit.updateHealthBar, 0), Func(suit.setNeutralAnimationDrop), Wait(2.0))
    return Parallel(suitTrack, soundTrack)

def doRedTape(attack):
    suit = attack['suit']
    targets = attack['target']
    tape = globalPropPool.getProp('redtape')
    tape.setColor(0.129, 0, 0.329, 1)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
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
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))

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
        damageAnims = [['nothing', 0.01, 0.35]]
        notifyTracks.append(Sequence(Wait(2.4), Parallel(Func(toon.showHpTextNew, -int(dmg), text="COOLDOWN!", colorCode=1))))
        notifyTracks.append(Parallel(Func(toon.makeCooldown), Func(toon.checkCooldownRounds, 2)))
        allTubeTracks.append(tubeTracks)
        toonTracks.append(Sequence(Wait(2.4), ActorInterval(toon, 'struggle')))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.75, node=suit)
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=2.4, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['neutral'])
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack, allTubeTracks, notifyTracks, toonDamageTrack)

def getResetTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    unluredTrack = Func(battle.unlureSuit, suit)
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05), (Func(suit.setNeutralAnimationTrap)))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, walkTrack, moveTrack)

def doExtraTip(attack, ind):
    theSuit = attack['suit']
    battle = attack['battle']
    targetSuit = battle.activeSuits[ind]

    suitTracks = Parallel()
    suitTrack = Sequence()
    suitTrack.append(Wait(4.0))
    suitTrack.append(Func(targetSuit.checkExtraTip))
    suitTrack.append(Parallel(Func(targetSuit.makeDamageUp), Func(targetSuit.checkDamageUp, + 10)))
    suitTrack.append(Func(targetSuit.updateHealthBar, 0))
    suitTrack.append(Func(targetSuit.setDizzy, 0))
    suitTrack.append(Func(targetSuit.setChatAbsolute,
                                               random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                               CFSpeech | CFTimeout))
    suitTrack.append(getResetTrack(targetSuit, battle))
    suitTrack.append(Wait(2.0))
    suitTracks.append(suitTrack)
    knifeTracks = Parallel()
    hitPoint = targetSuit.getPos(battle)
    hitPoint.setZ(targetSuit.height + 2)
    hitPoint.setY(hitPoint.getY() + 0.5)
    can = globalPropPool.getProp('bounced-check')
    texture = loader.loadTexture('phase_5/maps/battle/ttcc_suitprops_palette_1_alt.png')
    can.setTexture(texture, 1)
    posPoints = [Point3(-0.3468208092485554, -0.5202312138728331, -0.08670520231213885), VBase3(-7.814761215629517, -177.91907514450867, -188.3236994219653)]
    knifeTrack = Sequence(
        getPropAppearTrack(can, theSuit.getRightHand(), posPoints, .5, VBase3(8.5, 8.5, 8.5),
                           scaleUpTime=0.5),
        Wait(0.95),

        Parallel(
            getThrowTrack(can, (0, 0, targetSuit.getHeight() + 2.5), 1.5, targetSuit, -30.288),
            LerpHprInterval(can, 1.0, VBase3(0, -90, 0))
        ),

        Wait(0.15),

        Parallel(
            LerpPosInterval(can, 0.45, (0, 0, targetSuit.getHeight() - 2.5), other=targetSuit, blendType='easeIn'),
            LerpScaleInterval(can, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
        ),

        Parallel(
            LerpScaleInterval(can, 0.2, VBase3(0.01, 0.01, 0.01)),
            LerpColorScaleInterval(can, 0.2, Vec4(1, 1, 1, 0))
        ),

        Func(can.removeNode)
    )
    knifeTracks.append(knifeTrack)
    suitTrackAnim = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    soundTrack1 = getSoundTrack('SA_extra_tip.ogg', delay=2)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=4.0)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    return Parallel(suitTrackAnim, suitTracks, multiTrack, knifeTracks)

def doExplosion(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence(Func(theSuit.setChatAbsolute, "My people need me.",
                          CFSpeech | CFTimeout))
        suitTrack.append(Wait(3.0))
        suitTrack.append(Parallel(MovieUtil.createSuitDeathTrackExplosiveForeman(theSuit, battle), Func(suit.setHealthForMe, - (50 * len(battle.activeToons))), Func(suit.showHpTextNew, - int(50 * len(battle.activeToons))), Func(suit.updateHealthBar, 0), Func(suit.checkCogHPBomb, battle), ActorInterval(suit, 'slip-backward')))
        suitTracks.append(suitTrack)
        suitTrack.append(Func(suit.setNeutralAnimationDrop))
    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=3.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=3.0)
    return Parallel(suitTracks, toonTracks, soundTrack1)

def doContractor(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    suitTrack = Sequence(Func(theSuit.setChatAbsolute, "Please fill out paperwork with me.",
                          CFSpeech | CFTimeout))
    toonTrack = Sequence(Wait(3.0), Func(toon.setChatAbsolute, "I am compelled to fill out paperwork with you.",
                          CFSpeech | CFTimeout), Wait(3.0))
    return Parallel(suitTrack, toonTrack)

def doPuzzling(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    suitTrack = Sequence(Func(theSuit.setChatAbsolute, random.choice(("Your combat skills are laughable.", "You can't outsmart me!", "Prepare to be mind-meddled!")),
                          CFSpeech | CFTimeout))
    toonTrack = Sequence(Wait(3.0), Func(toon.setChatAbsolute, random.choice(("Your wish is my command.", "As you desire, Mr. President.", "As you wish.")),
                          CFSpeech | CFTimeout), Wait(3.0))
    toonTrack.append(Parallel(Func(toon.makeConfused), Func(toon.addConfusedRounds, 2)))
    return Parallel(suitTrack, toonTrack)

def doSleepyOvercharge(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    suitTrack = Sequence()
    suitTrack.append(Parallel(Func(theSuit.setHealthForMe, + 900), Func(theSuit.showHpTextNew, + 900, text="NAP OVER!", colorCode=1), Func(theSuit.updateHealthBar, 0)))
    suitTrack.append(Func(theSuit.makeUnSleepy))
    suitTracks.append(suitTrack)
    soundTrack1 = getSoundTrack('LB_toonup.ogg')
    return Parallel(suitTracks, soundTrack1)

def doFraudulentDamage(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    notifyTrack = Sequence(Func(theSuit.checkFraudulentDamage))
    cameraTrack = Wait(3.0)
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    return Sequence(notifyTracks)

def doHighStakes(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack))
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
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        toonHpr = battle.getActorPosHpr(toon)
        y = toonPos.getY()
        propPos = Point3(toonPos.getX(), y, 30)
        gavelPos = Point3(toonPos.getX(), y, 30)
        soundTrack2 = getSoundTrack('AA_drop_bigweight.ogg', delay=1.75, duration=2.0, node=suit)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        propTracks.append(Parallel(propTrack, soundTrack2))
        toonTrack = Sequence(
        Wait(1.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpTextNew, 0, text="?!", colorCode=1),
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

def doSyphon(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    partTracks = Parallel()
    partTracks4 = Parallel()
    toonAnimTracks = Parallel()
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    selfDamageTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        BattleParticles.loadParticles()
        sprayEffect = BattleParticles.createParticleEffect('DemotionSpray2')
        sprayEffect2 = BattleParticles.createParticleEffect('DemotionSpray2')
        freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze2')
        unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze2')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle')
        BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
        BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
        BattleParticles.setEffectTexture(sprayEffect2, 'snow-particle',
                                         color=Vec4(1, 0, 0, 1))
        facePoint = __toonFacePoint(toon)
        freezeEffect.setPos(0, 0, facePoint.getZ())
        unFreezeEffect.setPos(0, 0, facePoint.getZ())
        partTrack4 = getPartTrack(sprayEffect, 1, 4.0, [sprayEffect2, toon, 0], softStop=-1)
        partTracks4.append(partTrack4)
        toonAnimTrack = ActorInterval(toon, 'cringe', playRate=.5)
        toonAnimTracks.append(toonAnimTrack)
        suitTrack.append(Sequence(Func(suit.setHealthForMe, + dmg), Func(suit.updateHealthBar, 0)))
        selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, +dmg))
        selfDamageTracks.append(selfDamageTrack)
    dodgeAnims = [['duck', 1e-06, 0.8]]
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0,
                        0.5])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.4, 0.5, startTime=0.5))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.5, startTime=0.9))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.6, startTime=1.2))
    damageAnims.append(['cringe', 2.6, 1.5])
    toonTrack = getToonTracks(attack, 1, ['nothing'], 0, ['neutral'])
    multiTrackList = Parallel(suitTrack, toonTrack, toonAnimTracks, selfDamageTracks, partTracks4)
    soundTrack = getSoundTrack('SA_ink_drain.ogg', delay=0, node=suit)
    multiTrackList.append(soundTrack)
    return multiTrackList

def doDeepFreeze(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    sprayEffect = BattleParticles.createParticleEffect('WaterSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 10.6, 6.7))
    waterfallEffect = BattleParticles.createParticleEffect(file='snowWaterfall')
    suitTrack = getSuitAnimTrackAttack(attack)
    partTrack = getPartTrack(sprayEffect, 1.0, 5.9, [sprayEffect, suit, 0], softStop=1)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 5.9, [waterfallEffect, suit, 0], softStop=1)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 5.9, [sprayEffect, suit, 0], softStop=1)
    damageAnims = [['cringe']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['cringe'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_freeze.ogg')))
    makeFrozen = Func(suit.makeFrozen)
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_freeze.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, sprayTrack, makeFrozen, waterfallTrack, synergySoundTrack, toonTracks, soundTrack1)
    else:
        return Parallel(suitTrack, partTrack, sprayTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doCompensation(attack):
    suit = attack['suit']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    suitTrack = Parallel(getSuitAnimTrack(attack), Wait(2.0))
    suitTrack.append(Sequence(Wait(2.0), Func(suit.checkCompensationForeman), healSound))
    return Parallel(suitTrack)

def doLifeInsurance(attack):
    suit = attack['suit']
    healSound = SoundInterval(globalBattleSoundCache.getSound('SA_life_insurance_loop.ogg'))
    suitTrack = Parallel(getSuitAnimTrack(attack), Wait(5.0))
    suitTrack.append(Sequence(Func(suit.checkLifeInsurance), healSound))
    return Parallel(suitTrack)

def doAccountantRequirement(attack):
    suit = attack['suit']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'calculator', playRate=1.25), Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        calcPosPoints = [Point3(-0.7803468208092497, 0.26011560693641655, -0.1), VBase3(0, 0.0, 170.63583815028903)]
        calculator.setScale(1.25)
    if suitType == 'b':
        calcPosPoints = [Point3(0, 0.43352601156069426, 0), VBase3(0, 0.0, 180.0)]
        calculator.setScale(1)
    if suitType == 'c':
        calcPosPoints = [Point3(0, 0.34682080924855896, 0), VBase3(0, 0.0, 180.0)]
        calculator.setScale(1)
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    return Parallel(suitTrack, calcPropTrack, suitTrack2, soundTrack)

def doApproveDisapprove(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(3.0))
    return Parallel(suitTrack)

def doPolicyTerminated(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    suitTrack = Sequence()
    suitTrack.append(Func(theSuit.showHpTextNew, 0, text="POLICY TERMINATED!", colorCode=1))
    suitTrack.append(Wait(2.0))
    suitTracks.append(suitTrack)
    return Parallel(suitTracks)

def doCompensation2(attack):
    suit = attack['suit']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    suitTrack = Parallel(getSuitAnimTrack(attack), Wait(2.0))
    suitTrack.append(Sequence(Wait(2.0), Func(suit.checkCompensation2), healSound))
    return Parallel(suitTrack)

def doCompensation3(attack):
    suit = attack['suit']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    suitTrack = Parallel(getSuitAnimTrack(attack), Wait(2.0))
    suitTrack.append(Sequence(Wait(2.0), Func(suit.checkCompensation3), healSound))
    return Parallel(suitTrack)

def doCompensation4(attack):
    suit = attack['suit']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    suitTrack = Parallel(getSuitAnimTrack(attack), Wait(2.0))
    suitTrack.append(Sequence(Wait(2.0), Func(suit.checkCompensation4), healSound))
    return Parallel(suitTrack)

def doCompensation5(attack):
    suit = attack['suit']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    suitTrack = Parallel(getSuitAnimTrack(attack), Wait(2.0))
    suitTrack.append(Sequence(Wait(2.0), Func(suit.checkCompensation5), healSound))
    return Parallel(suitTrack)

def doMulligan(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.75))

    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 2.5, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.2, Point3(1.5, 1.5, 1.5)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(0.75))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(ball.removeNode))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, 2.5, ['slip-backward'], 1, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack)

def doObjection(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=0.75))
    suitTrack.append(Wait(2.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_objection.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doObjectionOverruled(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(2.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_objection_overruled.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doObjectionSustained(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(1.0, 0.2, 0.2, 0.9)
    edgeColor = Vec4(0.9, 0.9, 0.9, 0.4)
    powerBar1 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar2 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-90, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(90, 0, 0)
    powerBar1.setScale(5)
    powerBar2.setScale(5)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitTrack = Sequence(getSuitAnimTrackAttack(attack, playRate=1.25))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(0.7), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 25, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.6, [waterfallEffect, suit, 0], softStop=-1)
    toonTracks = getToonTracks(attack, 1.5, ['slip-forward'], 0.86, ['jump'])
    soundTrack = getSoundTrack('SA_guilt_trip.ogg', delay=1.1, node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=0, node=suit)
    dmg = attack['target'][0]['hp']
    suitHealTrack = Sequence(Func(suit.showHpTextNew, +(dmg * 3)), Func(suit.setHealthForMe, +(dmg * 3)),
                         Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, partTrack1, partTrack2, suitHealTrack, soundTrack2, soundTrack, waterfallTrack, toonTracks)

def doComeOn(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
    if not suit.getPlayRate2() >= 8.0:
        suitTrack.append(Func(suit.setPlayRate2, suit.getPlayRate2() + .5))
    return suitTrack

def doRushJob(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel(getSuitAnimTrack(attack, playRate=1.25))
    suitTracks.append(Wait(2.0))
    soundTrack = getSoundTrack('SA_rush_job_target.ogg', node=suit)
    return Parallel(suitTracks, soundTrack)

def doDriver(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    club = globalPropPool.getProp('golf-club')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        ball = globalPropPool.getProp('golf-ball')
        ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.75, 1.75, 1.75)),
                                 Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                                 Wait(1.125))
        if dmg > 0:
            ballPropTracks.append(Parallel(Func(toon.checkDamageDown, 25)))
            ballPropTracks.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 3)))
        missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
        ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1, target=t))
        ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
        ballPropTracks.append(ballPropTrack)

    dodgeDelay = suitTrack.getDuration()
    toonTracks = getToonTracks(attack, 3, ['slip-backward'], 1.5, ['duck'],
                               showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    return Parallel(suitTrack, toonTracks, clubPropTrack, ballPropTracks, soundTrack)

def doDriverNO(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrackAttack(attack, playRate=1.75))
    club = globalPropPool.getProp('golf-club')
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 2.25, Point3(1.1, 1.1, 1.1))
    ballPosPoints = [Point3(7.1, -50.0, 0)]
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            ballPropTracks.append(Parallel(Func(toon.checkDamageDown, 25)))
            ballPropTracks.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 3)))
        numBalls = 5  # Change this to any number you want
        startDelay = 2.0  # When first ball appears
        intervalDelay = 0.075  # Time between each ball

        ballScale = 2.5

        # Load base model once (better performance)
        baseBall = loader.loadModel('phase_6/models/golf/golf_ball')
        baseBall.setColorScale(0.75, 0.75, 0.75, 0.5)
        baseBall.setTransparency(1)
        baseBall.setScale(ballScale)

        for i in range(numBalls):
            ball = baseBall.copyTo(render)  # Instance instead of reloading

            delay = startDelay + (i * intervalDelay)

            ballTrack = Sequence(
                Wait(delay),
                getPropAppearTrack(ball, suit, ballPosPoints, 0, ballScale),
                Func(ball.wrtReparentTo, render)
            )

            missPoint = lambda b=ball, toon=toon: __toonMissPoint(b, toon)

            ballTrack.append(
                getPropThrowTrack(
                    attack,
                    ball,
                    [__toonFacePoint(toon)],
                    [missPoint],
                    0.1,
                    target=t
                )
            )

            ballTrack.append(Func(ball.removeNode))  # Clean up properly

            ballPropTracks.append(ballTrack)
    toonTracks = getToonTracks(attack, 2.5, ['slip-forward'], 1, ['duck'],
                               showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2, node=suit)
    return Parallel(suitTrack, ballPropTracks, toonTracks, soundTrack, clubPropTrack)

def doDriverOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.75))
    club = globalPropPool.getProp('golf-club')
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 2.25, Point3(1.1, 1.1, 1.1))
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            ballPropTracks.append(Parallel(Func(toon.checkDamageDown, 25)))
            ballPropTracks.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 3)))
        ball = loader.loadModel('phase_6/models/golf/golf_ball')
        ball.setColorScale(0.75, 0.75, 0.75, 0.5)
        ball.setTransparency(1)
        ballScale = 2.5
        ball.setScale(ballScale)
        ball2 = loader.loadModel('phase_6/models/golf/golf_ball')
        ball2.setColorScale(0.75, 0.75, 0.75, 0.5)
        ball2.setTransparency(1)
        ball2.setScale(ballScale)
        ball3 = loader.loadModel('phase_6/models/golf/golf_ball')
        ball3.setColorScale(0.75, 0.75, 0.75, 0.5)
        ball3.setTransparency(1)
        ball3.setScale(ballScale)
        ball4 = loader.loadModel('phase_6/models/golf/golf_ball')
        ball4.setColorScale(0.75, 0.75, 0.75, 0.5)
        ball4.setTransparency(1)
        ball4.setScale(ballScale)
        ball5 = loader.loadModel('phase_6/models/golf/golf_ball')
        ball5.setColorScale(0.75, 0.75, 0.75, 0.5)
        ball5.setTransparency(1)
        ball5.setScale(ballScale)
        ballPropTrack = Sequence(Wait(1.25), getPropAppearTrack(ball, suit, ballPosPoints, 0, ballScale),
                                 Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                                 Wait(0.75))
        missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
        ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1, target=t))
        ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
        ballPropTrack2 = Sequence(Wait(1.35), getPropAppearTrack(ball2, suit, ballPosPoints, 0, ballScale),
                                 Func(battle.movie.needRestoreRenderProp, ball2), Func(ball2.wrtReparentTo, render),
                                 Wait(0.75))
        missPoint = lambda ball2=ball2, toon=toon: __toonMissPoint(ball2, toon)
        ballPropTrack2.append(getPropThrowTrack(attack, ball2, [__toonFacePoint(toon)], [missPoint], .1, target=t))
        ballPropTrack2.append(Func(battle.movie.clearRenderProp, ball2))
        ballPropTrack3 = Sequence(Wait(1.45), getPropAppearTrack(ball3, suit, ballPosPoints, 0, ballScale),
                                 Func(battle.movie.needRestoreRenderProp, ball3), Func(ball3.wrtReparentTo, render),
                                 Wait(0.75))
        missPoint = lambda ball3=ball3, toon=toon: __toonMissPoint(ball3, toon)
        ballPropTrack3.append(getPropThrowTrack(attack, ball3, [__toonFacePoint(toon)], [missPoint], .1, target=t))
        ballPropTrack3.append(Func(battle.movie.clearRenderProp, ball3))
        ballPropTrack4 = Sequence(Wait(1.55), getPropAppearTrack(ball4, suit, ballPosPoints, 0, ballScale),
                                 Func(battle.movie.needRestoreRenderProp, ball4), Func(ball4.wrtReparentTo, render),
                                 Wait(0.75))
        missPoint = lambda ball4=ball4, toon=toon: __toonMissPoint(ball4, toon)
        ballPropTrack4.append(getPropThrowTrack(attack, ball4, [__toonFacePoint(toon)], [missPoint], .1, target=t))
        ballPropTrack4.append(Func(battle.movie.clearRenderProp, ball4))
        ballPropTrack5 = Sequence(Wait(1.65), getPropAppearTrack(ball5, suit, ballPosPoints, 0, ballScale),
                                 Func(battle.movie.needRestoreRenderProp, ball5), Func(ball5.wrtReparentTo, render),
                                 Wait(0.75))
        missPoint = lambda ball5=ball5, toon=toon: __toonMissPoint(ball5, toon)
        ballPropTrack5.append(getPropThrowTrack(attack, ball5, [__toonFacePoint(toon)], [missPoint], .1, target=t))
        ballPropTrack5.append(Func(battle.movie.clearRenderProp, ball5))
        ballPropTracks.append(ballPropTrack)
        ballPropTracks.append(ballPropTrack2)
        ballPropTracks.append(ballPropTrack3)
        ballPropTracks.append(ballPropTrack4)
        ballPropTracks.append(ballPropTrack5)
    toonTracks = getToonTracks(attack, 2.5, ['slip-backward'], 1, ['duck'],
                               showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2, node=suit)
    return Parallel(suitTrack, ballPropTracks, toonTracks, soundTrack, clubPropTrack)
