from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
from toontown.effects import DustCloud
from toontown.toon import Toon
from direct.showutil import Effects
from toontown.battle import SuitBattleGlobals
from toontown.effects import DustCloud
from toontown.battle.BattleProps import *
from otp.otpbase import OTPLocalizerEnglish
from toontown.battle.BattleSounds import *
from toontown.battle.SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import BattleProps
import math
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

def __makeCancelledNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText(TTLocalizer.MovieSuitCancelled)
    tn.setAlign(TextNode.ACenter)
    tntop = hidden.attachNewNode('CancelledTop')
    tnpath = tntop.attachNewNode(tn)
    tnpath.setPosHpr(0, 0, 0, 90, 0, 0)
    tnpath.setScale(1)
    tnpath.setColor(0.7, 0, 0, 1)
    tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
    tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
    tnpath.setScale(1)
    return tntop

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

def doHighPressure(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    suitTracks = Parallel()
    knifeTracks = Parallel()

    toonTargets = []

    posPoints = [
        Point3(-0.4109589, -0.0821917, -0.0821917),
        VBase3(-10.849315, 0, 113.42465753424653)
    ]

    # =========================================================
    # EXPLOSIONS
    # =========================================================
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)

    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + theSuit.height - 0.2)
    gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + theSuit.height - 0.2)

    explosionTrack = Sequence(
        Wait(4.0),
        MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3)
    )

    explosionTrack2 = Sequence(
        Wait(4.0),
        MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint2, scale=3)
    )

    # =========================================================
    # TARGETS
    # =========================================================
    for targetData in targets:
        dmg = int(targetData.get('hp', 0))

        if dmg <= 0:
            continue

        # =====================================================
        # COG TARGET
        # =====================================================
        if 'suit' in targetData:
            targetSuit = targetData['suit']
            died = targetData.get('died', False)

            targetTrack = Sequence(
                Wait(4.0),
                Parallel(
                    Func(targetSuit.showHpTextNew, -dmg),
                    Func(targetSuit.setHealthForMe, -dmg),
                    Func(targetSuit.updateHealthBar, 0),
                    Func(targetSuit.playDialogueForString, "!")
                )
            )

            if died:
                targetTrack.append(Parallel(ActorInterval(targetSuit, 'flail'), MovieUtil.shortCircuitTrack(targetSuit, battle)))
                targetTrack.append(Func(targetSuit.makeDead))

            else:
                targetTrack.append(
                    Parallel(
                        ActorInterval(targetSuit, 'slip-backward'),
                    )
                )

                targetTrack.append(Func(targetSuit.setNeutralAnimationDrop))

            suitTracks.append(targetTrack)

        # =====================================================
        # TOON TARGET
        # =====================================================
        elif 'toon' in targetData:
            toon = targetData['toon']

            toonTargets.append(targetData)

            knife = globalPropPool.getProp('tnt')
            tip = knife.find('**/joint_attachEmitter')

            sparks = BattleParticles.createParticleEffect(file='tnt')
            knife.sparksEffect = sparks

            knifeTrack = Sequence(
                getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, 0, scaleUpPoint=Point3(.7), scaleUpTime=0.25),
                Func(sparks.start, tip),
                Wait(1.3),
                Parallel(
                    getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                    LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
                ),
                Func(knife.removeNode)
            )

            knifeTracks.append(knifeTrack)

    # =========================================================
    # TOON DAMAGE TRACKS
    # =========================================================
    if toonTargets:
        toonAttack = attack.copy()
        toonAttack['target'] = toonTargets

        damageAnims = [
            ['slip-forward', 0.01, 0.4]
        ]

        toonTracks = Sequence(
            Wait(4.0),
            getToonTracks(toonAttack, damageDelay=0.0, splicedDamageAnims=damageAnims, dodgeDelay=0.0, dodgeAnimNames=['sidestep'])
        )
    else:
        toonTracks = Sequence()

    # =========================================================
    # ATTACKER ANIMATION
    # =========================================================
    attackerTrack = Sequence(
        getSuitAnimTrackAttack(attack, playRate=2.0),
        Func(theSuit.setNeutralAnimationDrop)
    )

    # =========================================================
    # SOUNDS
    # =========================================================
    soundTrack = getSoundTrack('incoming_whistle.ogg', delay=2.0, node=theSuit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=1.5, node=theSuit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=4.0)

    return Parallel(attackerTrack, suitTracks, knifeTracks, toonTracks, soundTrack, soundTrack1, soundTrack2, explosionTrack, explosionTrack2)

def doHeatWaveCalculation(attack):
    BattleParticles.loadParticles()
    suit = attack['suit']
    targets = attack.get('target', [])

    if not targets:
        return Sequence()

    targetData = targets[0]
    node = suit.getGeomNode().getChild(0)
    suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=3, colorScale=(1, 0, 0, 1),
                                                     blendType='easeInOut'), Wait(1.0),
                              LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1)))
    baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
    flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
    flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
    baseFlameTrack = getPartTrack(baseFlameEffect, 0, 5.5, [baseFlameEffect, suit, 0], softStop=-1)
    flameTrack = getPartTrack(flameEffect, 0, 5.5, [flameEffect, suit, 0], softStop=-1)
    flecksTrack = getPartTrack(flecksEffect, 0, 5.5, [flecksEffect, suit, 0], softStop=-1)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_boilerplate_a.ogg')))
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Under pressure, things get hot fast... this battlefield now burns at %s degrees and climbing." % targetData.get('hp', 0), CFSpeech | CFTimeout)
    return Parallel(suitTrack, suitSpeechTrack, baseFlameTrack, suitColorTrack, flameTrack, flecksTrack, soundTrack)

def doFloodTheMarket(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect(file='floodTheMarket2')
    waterfallEffect = BattleParticles.createParticleEffect(file='floodTheMarketWaterfall2')
    value = int(attack['target'][0]['hp'] / 2)
    suitTrack = Parallel(Func(suit.showHpString, "+%s%% Damage!" % int(value)), getSuitAnimTrackAttack(attack))
    suitTrack.append(Parallel(Func(suit.setSuitStatusEffect, 'damageUp', modifier=int(value), mode='refreshModifier')))
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
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('ttr_s_ene_bat_floodTheMarket.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        puddleCounter = 0
        for t in targets:
            toon = t['toon']
            if t['hp'] > 0:
                if puddleCounter == 0:
                    puddle = globalPropPool.getProp('quicksand')
                    puddle.setColor(Vec4(1.0, 0.0, 0.0, 1))
                    puddle.setHpr(Point3(120, 0, 0))
                    puddle.setScale(0.01)
                    puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
                if puddleCounter == 1:
                    puddle2 = globalPropPool.getProp('quicksand')
                    puddle2.setColor(Vec4(1.0, 0.0, 0.0, 1))
                    puddle2.setHpr(Point3(120, 0, 0))
                    puddle2.setScale(0.01)
                    puddleTrack1 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle2), Func(puddle2.reparentTo, battle), Func(puddle2.setPos, toon.getPos(battle)), LerpScaleInterval(puddle2, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle2.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle2), Func(battle.movie.clearRenderProp, puddle2))
                if puddleCounter == 2:
                    puddle3 = globalPropPool.getProp('quicksand')
                    puddle3.setColor(Vec4(1.0, 0.0, 0.0, 1))
                    puddle3.setHpr(Point3(120, 0, 0))
                    puddle3.setScale(0.01)
                    puddleTrack2 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle3), Func(puddle3.reparentTo, battle), Func(puddle3.setPos, toon.getPos(battle)), LerpScaleInterval(puddle3, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle3.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle3), Func(battle.movie.clearRenderProp, puddle3))
                if puddleCounter == 3:
                    puddle4 = globalPropPool.getProp('quicksand')
                    puddle4.setColor(Vec4(1.0, 0.0, 0.0, 1))
                    puddle4.setHpr(Point3(120, 0, 0))
                    puddle4.setScale(0.01)
                    puddleTrack3 = Sequence(Func(battle.movie.needRestoreRenderProp, puddle4), Func(puddle4.reparentTo, battle), Func(puddle4.setPos, toon.getPos(battle)), LerpScaleInterval(puddle4, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle4.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle4), Func(battle.movie.clearRenderProp, puddle4))
                puddleCounter +=1
        if puddleCounter == 1:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, puddleTrack, toonTracks)
        if puddleCounter == 2:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, puddleTrack, puddleTrack1, toonTracks)
        if puddleCounter == 3:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, puddleTrack, puddleTrack1,  puddleTrack2, toonTracks)
        if puddleCounter == 4:
            puddleCounter = 0
            return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, puddleTrack, puddleTrack1,  puddleTrack2,  puddleTrack3, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

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
    suitTrack = Parallel(getSuitAnimTrackAttack(attack), MovieUtil.createSuitFirestarterCigarSmokeInterval2(suit))
    hitAtleastOneToon = False
    BattleParticles.loadParticles()
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
        BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))
        baseFlameSmall = BattleParticles.createParticleEffect(file='firedBaseFlame2')
        flameSmall = BattleParticles.createParticleEffect('FiredFlame2')
        flecksSmall = BattleParticles.createParticleEffect('SpriteFiredFlecks')
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
        sprayEffect = BattleParticles.createParticleEffect('FireSpray')
        sprayEffect2 = BattleParticles.createParticleEffect('FireSpray')
        partTrack4 = getPartTrack(sprayEffect, 1, 3.25, [sprayEffect2, toon, 0], softStop=-1)
        notifyTrack = Sequence(Wait(1.5), Func(toon.showHpTextNew, -int(dmg)))
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
            suitTrack.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'magic3-alt'),
                                      Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                      Func(suit.setNeutralAnimationDrop)))
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
    toonTracks = getToonTracksCheat(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3,
                                    dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_boilerplate_a.ogg', delay=1.0, node=suit)
    if hitAtleastOneToon == True:
        multiTrackList = Parallel(suitTrack, baseFlameTracks, notifyTracks, flameTracks, partTracks4, flecksTracks,
                                  toonTracks, colorTracks, soundTrack)
    else:
        multiTrackList = Parallel()
    return multiTrackList

def doOverheat2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    flameTracks = Parallel()
    explosionTracksGroup = Parallel()
    notifyTracks = Parallel()
    propTracks = Parallel()
    toonTracks = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(5.45))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        knife = loader.loadModel('phase_12/models/bossbotHQ/canoffood')
        tnt = knife.find('**/can')
        flameEffect = BattleParticles.createParticleEffect('FireSprayCan')
        flameTrack = getPartTrack(flameEffect, 0.5, 4.0, [flameEffect, tnt, 0], softStop=-1)
        posPoints = [Point3(-0.25, 0, 0), VBase3(-65, 180, 0)]
        propTrack = Sequence(getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.25, Point3(.5, .5, .5), scaleUpTime=0.25))
        propTrack.append(Parallel(LerpColorScaleInterval(tnt, duration=4, colorScale=(0.867, 0, 1, 1),
                                    blendType='easeInOut'), Wait(4.7)))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
        notifyTrack = Sequence(Wait(5.45), Func(toon.showHpTextNew, - int(dmg)))
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
            propTracks.append(propTrack)
            toonTracks.append(Sequence(Parallel(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle)),
                                       Sequence(Parallel(ActorInterval(suit, 'throw-object', duration=1.5, playRate=1.5)), Wait(3.175),
                                                ActorInterval(suit, 'throw-object', startTime=1.5, playRate=1.5)),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            notifyTracks.append(notifyTrack)
            propTracks.append(propTrack)
            flameTracks.append(flameTrack)
            explosionTracksGroup.append(explosionTrack)
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=5.45)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack2 = getSoundTrack('SA_boilerplate_a.ogg', delay=0.5, node=suit)
    suitHeadAnimTrack = MovieUtil.createSuitFirestarterCigarSmokeInterval2(suit)
    toonTrack = getToonTracksCheat(attack, 5.45, ['slip-forward'], 3.4, ['struggle'])
    suitAnimTrack = Sequence(Parallel(ActorInterval(suit, 'throw-object', duration=1.5, playRate=1.5)), Wait(3.175),
                         ActorInterval(suit, 'throw-object', startTime=1.5, playRate=1.5), Func(suit.setNeutralAnimationDrop))
    return Parallel(explosionTracksGroup, toonTracks, suitHeadAnimTrack, flameTracks, soundTrack2, suitAnimTrack, suitTrack, toonTrack, soundTrack, propTracks, notifyTracks)

def doOverpressured(attack, ind):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    target = attack['target']

    if not target:
        return Sequence()

    targetSuit = target[0]['suit']
    flameTracks = Parallel()
    explosionTracksGroup = Parallel()
    notifyTracks = Parallel()
    propTracks = Parallel()
    targetTrack = Sequence(Wait(7.0), MovieUtil.createOverpressuredInterval(targetSuit, battle), Func(targetSuit.setSuitStatusEffect, 'overpressured', modifier=1))
    BattleParticles.loadParticles()
    toonPos = targetSuit.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(targetSuit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + targetSuit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(7.0))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    knife = loader.loadModel('phase_12/models/bossbotHQ/canoffood')
    tnt = knife.find('**/can')
    flameEffect = BattleParticles.createParticleEffect('FireSprayCan')
    flameTrack = getPartTrack(flameEffect, 0.5, 4.0, [flameEffect, tnt, 0], softStop=-1)
    posPoints = [Point3(-0.25, 0, 0), VBase3(-65, 180, 0)]
    hitPoint = targetSuit.getPos(battle)
    hitPoint.setZ(targetSuit.height + 2)
    hitPoint.setY(hitPoint.getY() + 0.5)
    propTrack = Sequence(
        getPropAppearTrack(tnt, theSuit.getRightHand(), posPoints, .5, VBase3(0.5, 0.5, 0.5),
                           scaleUpTime=0.1),
        LerpColorScaleInterval(tnt, duration=4, colorScale=(0.867, 0, 1, 1),
                               blendType='easeInOut'), Wait(0.5),
        Parallel(
            getThrowTrack(tnt, Point3(0, 0, targetSuit.height + 2), 1.5, targetSuit, -25.288),
            LerpHprInterval(tnt, 0.8, VBase3(0, 0, 0)), LerpScaleInterval(tnt, 0, VBase3(1, 1, 1))),
        Parallel(
            LerpPosInterval(tnt, 0.5, (0, 0, targetSuit.getHeight() - 2.5), other=targetSuit, blendType='easeIn'),
            LerpScaleInterval(tnt, 0.5, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
        ),
        Parallel(
            LerpScaleInterval(tnt, 0.2, VBase3(0.01, 0.01, 0.01)),
            LerpColorScaleInterval(tnt, 0.2, Vec4(1, 1, 1, 0))
        ),
        Func(tnt.removeNode)
    )
    propTracks.append(propTrack)
    flameTracks.append(flameTrack)
    explosionTracksGroup.append(explosionTrack)
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=7.0)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack2 = getSoundTrack('SA_boilerplate_a.ogg', delay=0.5, node=suit)
    suitHeadAnimTrack = MovieUtil.createSuitFirestarterCigarSmokeInterval2(suit)
    suitAnimTrack = Sequence(Parallel(ActorInterval(suit, 'throw-object', duration=1.5, playRate=1.5)), Wait(3.175),
                             ActorInterval(suit, 'throw-object', startTime=1.5, playRate=1.5), Func(suit.setNeutralAnimationDrop))
    return Parallel(explosionTracksGroup, targetTrack, suitHeadAnimTrack, flameTracks, soundTrack2, suitAnimTrack, suitTrack, soundTrack, propTracks, notifyTracks)

def doHeatWave(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    toonTargets = []
    suitTargets = []

    for t in targets:
        if 'toon' in t:
            toonTargets.append(t)
        elif 'suit' in t:
            suitTargets.append(t)

    BattleParticles.loadParticles()

    damageDelay = 1.7

    particleEffect = BattleParticles.createParticleEffect(file='heatwave')
    waterfallEffect = BattleParticles.createParticleEffect(file='heatwaveWaterfall')

    node = suit.getGeomNode().getChild(0)

    attackAnimTrack = getSuitAnimTrackAttack(attack)

    suitTrack = Sequence(
        Parallel(
            LerpColorScaleInterval(node, duration=3, colorScale=(1, 0, 0, 1), blendType='easeInOut'),
            attackAnimTrack,
            MovieUtil.createSuitFirestarterCigarSmokeInterval2(suit)
        )
    )

    # ==================================================
    # SUIT TARGET / OVERHEATED REACTION
    # ==================================================
    suitReactionTracks = Parallel()

    for targetData in suitTargets:
        targetSuit = targetData['suit']
        dmg = targetData['hp']
        died = targetData['died']

        if dmg <= 0:
            continue

        if died:
            showDamage = Sequence(
                Wait(attackAnimTrack.getDuration()),
                Parallel(Parallel(Func(targetSuit.setChatAbsolute, random.choice(("Pressure's critical... PERFECT!", "I'm cooked... but so are you!", "If this is my last reading, I'm making it count!")), CFSpeech | CFTimeout)),
                   Parallel(ActorInterval(targetSuit, 'flail'), MovieUtil.shortCircuitTrack(targetSuit, battle)),
                    Func(targetSuit.showHpTextNew, -dmg, text='OVERHEATED!', colorCode=5),
                    Func(targetSuit.setHealthForMe, -dmg),
                    Func(targetSuit.updateHealthBar, 0)
                ),
                Func(targetSuit.setNeutralAnimationDrop)
            )
        else:
            showDamage = Sequence(
                Wait(attackAnimTrack.getDuration()),
                Parallel(Parallel(LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                            blendType='easeInOut')),
                    ActorInterval(targetSuit, 'pie-small-react'),
                    Func(targetSuit.showHpTextNew, -dmg, text='OVERHEATED!', colorCode=5),
                    Func(targetSuit.setHealthForMe, -dmg),
                    Func(targetSuit.updateHealthBar, 0)
                ),
                Func(targetSuit.setNeutralAnimationDrop)
            )

        suitReactionTracks.append(showDamage)

    # ==================================================
    # HEAT WAVE PARTICLES ON ATTACKER
    # ==================================================
    baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
    flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
    flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')

    BattleParticles.setEffectTexture(
        flecksEffect,
        'roll-o-dex',
        color=Vec4(0.95, 0.95, 0.0, 1)
    )

    baseFlameTrack2 = getPartTrack(baseFlameEffect, 1, 4.9, [baseFlameEffect, suit, 0], softStop=-1)
    flameTrack2 = getPartTrack(flameEffect, 1, 4.9, [flameEffect, suit, 0], softStop=-1)
    flecksTrack2 = getPartTrack(flecksEffect, 1, 4.9, [flecksEffect, suit, 0], softStop=-1)

    partTrack = getPartTrack(particleEffect, 1.0, 3.9, [particleEffect, suit, 0], softStop=-2.0)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.7, [waterfallEffect, suit, 0], softStop=-2.0)

    particleEffect2 = BattleParticles.createParticleEffect(file='heatwave')
    waterfallEffect2 = BattleParticles.createParticleEffect(file='heatwaveWaterfall')

    partTrack2 = getPartTrack(particleEffect2, 1.0, 3.9, [particleEffect2, suit, 0])
    waterfallTrack2 = getPartTrack(waterfallEffect2, 0.8, 3.7, [waterfallEffect2, suit, 0], softStop=-2.0)

    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()
    partTracks4 = Parallel()
    colorTracks = Parallel()

    # ==================================================
    # COLOR HELPERS
    # ==================================================
    def changeColor(parts):
        track = Parallel()

        for partNum in xrange(parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetColor(parts):
        track = Parallel()

        for partNum in xrange(parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    # ==================================================
    # TOON TARGET EFFECTS
    # ==================================================
    for t in toonTargets:
        toon = t['toon']

        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
        flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')

        BattleParticles.setEffectTexture(
            flecksEffect,
            'roll-o-dex',
            color=Vec4(0.95, 0.95, 0.0, 1)
        )

        sprayEffect = BattleParticles.createParticleEffect('FireSpray')
        sprayEffect2 = BattleParticles.createParticleEffect('FireSpray')

        partTrack4 = getPartTrack(sprayEffect, 1, 3.25, [sprayEffect2, toon, 0], softStop=-1)

        flameDelay = 1.45
        flameDuration = 1.5
        flecksDelay = flameDelay + 0.8
        flecksDuration = flameDuration - 0.8

        if t['hp'] > 0:
            baseFlameTracks.append(
                getPartTrack(baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0])
            )

            flameTracks.append(
                getPartTrack(flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0])
            )

            flecksTracks.append(
                getPartTrack(flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0])
            )

            partTracks4.append(partTrack4)

            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()

            colorTracks.append(
                Sequence(
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
                )
            )

    # ==================================================
    # TOON DAMAGE / DODGE ANIMS
    # ==================================================
    damageAnims = []

    damageAnims.append(['cringe', 0.01, 0.7, 0.62])
    damageAnims.append(['slip-forward', 0.01, 0.4, 1.2])
    damageAnims.append(['slip-forward', 0.01, 1.0])

    dodgeAnims = []

    dodgeAnims.append(['jump', 0.01, 0, 0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])

    # IMPORTANT:
    # getToonTracks should only receive Toon targets.
    toonAttack = attack.copy()
    toonAttack['target'] = toonTargets

    toonTracks = getToonTracks(
        toonAttack,
        damageDelay=damageDelay,
        splicedDamageAnims=damageAnims,
        dodgeDelay=0.91,
        splicedDodgeAnims=dodgeAnims,
        showMissedExtraTime=1.0
    )

    # ==================================================
    # SOUNDS
    # ==================================================
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=.5, node=suit)

    soundTrack2 = Sequence(
        Wait(.5),
        SoundInterval(globalBattleSoundCache.getSound('SA_boilerplate_a.ogg'))
    )

    # ==================================================
    # FINAL MOVIE
    # ==================================================
    return Parallel(
        suitTrack,
        suitReactionTracks,
        partTrack,
        soundTrack2,
        partTracks4,
        waterfallTrack,
        partTrack2,
        baseFlameTrack2,
        flameTrack2,
        flecksTrack2,
        waterfallTrack2,
        toonTracks,
        soundTrack,
        baseFlameTracks,
        flameTracks,
        flecksTracks,
        colorTracks
    )

def doOverpressureDeath(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    suitTracks = Parallel()
    toonTracks = Parallel()

    suitSpeechTrack = Sequence(
        Func(
            theSuit.setChatAbsolute,
            random.choice((
                "Well, I suppose everyone has their limit. Pleasure doing business with you.",
                "H-Hey, I don't think I'm built to support this much-",
                "I'm activating the 'explosion when overpressured' clause of my contract.",
                "Graph #132A shows that destroing a Suit under the current circumstances can have unfortunate consequences.",
                "Last I checked, Suits weren't designed to operate under these conditions.",
                "Ah! I'm heating up, I'm heating up!"
            )),
            CFSpeech | CFTimeout
        )
    )

    explosionTrack = Sequence(Wait(3.0), MovieUtil.createSuitDeathTrackExplosiveForeman(theSuit, battle))

    for targetData in targets:
        dmg = int(targetData.get('hp', 0))
        died = targetData.get('died', False)

        if dmg <= 0:
            continue

        # =====================================================
        # COG TARGET
        # =====================================================
        if 'suit' in targetData:
            targetSuit = targetData['suit']

            if targetSuit == theSuit:
                continue

            if not died:
                targetTrack = Sequence(
                    Wait(3.0),
                    Parallel(
                        Func(targetSuit.setHealthForMe, -dmg),
                        Func(targetSuit.showHpTextNew, -dmg),
                        Func(targetSuit.updateHealthBar, 0),
                        ActorInterval(targetSuit, 'slip-backward')
                    )
                )
            else:
                targetTrack = Sequence(
                    Wait(3.0),
                    Parallel(
                        Func(targetSuit.setHealthForMe, -dmg),
                        Func(targetSuit.showHpTextNew, -dmg),
                        Func(targetSuit.updateHealthBar, 0)
                    )
                )

            if died:
                if targetSuit.isVirtual:
                    targetTrack.append(MovieUtil.createVirtualSuitDeathTrack(targetSuit, battle))
                else:
                    targetTrack.append(Parallel(ActorInterval(targetSuit, 'flail'), MovieUtil.shortCircuitTrack(targetSuit, battle)))
            else:
                targetTrack.append(Func(targetSuit.setNeutralAnimationDrop))

            suitTracks.append(targetTrack)

        # =====================================================
        # TOON TARGET
        # =====================================================
        elif 'toon' in targetData:
            toon = targetData['toon']

            toonTrack = Sequence(
                Wait(3.0),
                Parallel(
                    ActorInterval(toon, 'slip-backward'),
                    Func(toon.showHpText, -dmg, openEnded=0),
                    Func(__doDamage, toon, dmg, targetData['died'])
                ),
                Func(toon.loop, 'neutral')
            )

            toonTracks.append(toonTrack)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=3.0)

    return Parallel(suitTracks, suitSpeechTrack, explosionTrack, toonTracks, soundTrack1)


def doDetourNew(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitDelay = 1.5
    propDelay = 0.1
    throwDuration = 1.0
    paper = loader.loadModel('phase_3.5/models/props/barrier_cone')
    paper.setHpr(0, 180, 0)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0, 0, 0), VBase3(0, 0, 180)]
    propTracks = Parallel()
    notifyTracks = Parallel()
    explosionTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(1, 1, 1), scaleUpTime=0.5))
        paperTrack.append(Wait(suitDelay))
        hitPoint = toon.getPos(battle)
        hitPoint.setX(hitPoint.getX() + 0)
        hitPoint.setY(hitPoint.getY() - .25)
        missPoint2 = toon.getPos(battle)
        missPoint2.setY(hitPoint.getY() - 7)
        movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() + 0.2)
        missPoint = Point3(missPoint2.getX(), missPoint2.getY(), missPoint2.getZ())
        paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperTrack.append(Func(paper.wrtReparentTo, battle))
        notifyTrack = Sequence(Wait(3.0), Func(toon.showHpTextNew, -int(dmg), text="DETOURED!", colorCode=3))
        notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'confused', turns=2)))
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(3.0))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        if dmg > 0:
            notifyTracks.append(notifyTrack)
            explosionTracks.append(explosionTrack)
        if dmg > 0:
            paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle, gravity=-100))
            paperTrack.append(Wait(0.6))
            paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
        else:
            paperTrack.append(getThrowTrack(paper, missPoint2, duration=throwDuration, parent=battle, gravity=-100))
            paperTrack.append(Wait(0.6))
            paperTrack.append(LerpPosInterval(paper, 0.4, missPoint))
        spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 360, 360)))
        sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(2, 2, 2)), Wait(0.25), LerpScaleInterval(paper, 0, MovieUtil.PNT3_NEARZERO))
        propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(paper.removeNode))
        propTracks.append(propTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.21,
     0.08])
    damageAnims.append(['slip-forward',
     0.01,
     0.6,
     0.85])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.95, startTime=1.2))
    damageAnims.append(['slip-forward', 0.01, 1.51])
    appearSfx = loader.loadSfx('phase_5/audio/sfx/SA_watercooler_appear_only.ogg')
    throwSfx = loader.loadSfx('phase_5/audio/sfx/SA_hardball_impact_only.ogg')
    landSfx = loader.loadSfx('phase_5/audio/sfx/AA_drop_bigweight_miss.ogg')
    landSfx.setVolume(.420)
    soundTracks = Parallel()
    soundTracks.append(getSoundTrack('SA_watercooler_appear_only.ogg', delay=.5))
    soundTracks.append(Sequence(Wait(2.0), SoundInterval(throwSfx, duration=.75)))
    toonTracks = getToonTracksCheat(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=1.5, dodgeAnimNames=['duck'], showDamageExtraTime=0, showMissedExtraTime=1.3)
    soundTrack3 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=3)
    return Parallel(soundTrack3, suitTrack, notifyTracks, explosionTracks, toonTracks, propTracks, soundTracks)

def doPromotion(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[dmg]
    targetSuit.addPendingQueuedHealing(1250)

    damageDelay = 1.7

    BattleParticles.loadParticles()
    baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
    flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
    flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))

    baseFlameSmall = BattleParticles.createParticleEffect(file='firedBaseFlame2')
    flameSmall = BattleParticles.createParticleEffect('FiredFlame2')
    flecksSmall = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(flecksSmall, 'roll-o-dex', color=Vec4(0.8, 0.8, 0.8, 1))

    baseFlameSmall.setScale(0.7)
    flameSmall.setScale(0.7)
    flecksSmall.setScale(0.7)

    baseFlameTrack = getPartTrack(baseFlameEffect, 2.1, 3.9, [baseFlameEffect, targetSuit, 0], softStop=-1)
    flameTrack = getPartTrack(flameEffect, 2.1, 3.9, [flameEffect, targetSuit, 0], softStop=-1)
    flecksTrack = getPartTrack(flecksEffect, 2.9, 2.1, [flecksEffect, targetSuit, 0], softStop=-1)

    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 2.1, 3.9, [baseFlameSmall, targetSuit, 0], softStop=-1)
    flameSmallTrack = getPartTrack(flameSmall, 2.1, 3.9, [flameSmall, targetSuit, 0], softStop=-1)
    flecksSmallTrack = getPartTrack(flecksSmall, 2.9, 2.1, [flecksSmall, targetSuit, 0], softStop=-1)

    sprayEffect = BattleParticles.createParticleEffect('FireSprayPromotion')
    sprayEffect2 = BattleParticles.createParticleEffect('FireSprayPromotion')
    partTrack4 = getPartTrack(sprayEffect, 2.1, 3.25, [sprayEffect2, targetSuit, 0], softStop=-1)

    origPos, origHpr = battle.getActorPosHpr(suit)
    origPos2 = suit.getPos(battle)

    walkDur = 1.5
    attackDur = suit.getDuration('magic3')

    walkOutPos = Point3(origPos)
    walkOutPos.setY(walkOutPos.getY() - 12.5)

    targetPos = targetSuit.getPos(battle)

    # Calculate the HPR the suit should have while standing out front
    suit.setPos(battle, walkOutPos)
    suit.setHpr(battle, origHpr)
    suit.headsUp(battle, targetPos)
    targetHpr = suit.getHpr(battle)

    # Restore original transform immediately after calculating
    suit.setPos(battle, origPos2)
    suit.setHpr(battle, origHpr)


    walkOutTrack = Parallel(
        ActorInterval(suit, 'walk', duration=1.5),
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

    turnBackTrack = Parallel(
        ActorInterval(suit, 'walk', duration=1.5),
        LerpHprInterval(
            suit,
            walkDur,
            origHpr,
            startHpr=targetHpr,
            other=battle
        ),
        LerpPosInterval(
            suit,
            walkDur,
            origPos,
            startPos=walkOutPos,
            other=battle
        )
    )



    suitTrack = Sequence(
        walkOutTrack,
        getSuitAnimTrack(attack),
        turnBackTrack,
        Func(suit.setPos, battle, origPos),
        Func(suit.setHpr, battle, origHpr),
        Func(suit.setNeutralAnimationDrop)
    )

    suitPos = targetSuit.getPos(battle)
    y = suitPos.getY()

    dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
    dustCloud.setBillboardAxis(2.0)
    dustCloud.setZ(3)
    dustCloud.setScale(0.4)
    dustCloud.createTrack()

    dustCloudHideIval = Sequence(
        Func(dustCloud.reparentTo, targetSuit),
        Func(dustCloud.setPos, Point3(suitPos.getX(), 0, 0)),
        dustCloud.track,
        Func(dustCloud.detachNode),
        Wait(1.7),
        name='dustCloadIval'
    )

    suitColorTrack = Parallel()
    actorNode = targetSuit.find('**/__Actor_modelRoot')
    actorCollection = actorNode.findAllMatches('*')
    for thingIndex in range(actorCollection.getNumPaths()):
        thing = actorCollection[thingIndex]
        if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
            suitColorTrack.append(
                Sequence(Wait(2.0),
                    LerpColorScaleInterval(thing, 3.0, (0, 0, 0, 1))
                )
            )
    # Keep your original effect timing
    selfDamageTrack = Parallel(suitColorTrack, Sequence(
        Wait(5.0),
        Parallel(
            dustCloudHideIval,
            Sequence(
                ActorInterval(targetSuit, 'slip-forward', startTime=2.43),
                Func(targetSuit.setNeutralAnimation)
            ),
            Func(targetSuit.makeIntoCTSManager),
            Func(targetSuit.showHpString, "PROMOTION!"),
            Func(targetSuit.setMaxHP, 1250),
            Func(targetSuit.makeShadow),
            Func(targetSuit.setManager, 1),
            Func(targetSuit.setDisplayName, targetSuit.createNameInfoShadow()),
            Func(targetSuit.makeShielding),
            Func(targetSuit.updateHealthBar, 0)
        ),
        Func(battle.unSueSuit, targetSuit)
    ))

    soundTrack = getSoundTrack('SA_boilerplate_a.ogg', delay=2.5, node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=5.0)

    return Parallel(
        baseFlameSmallTrack,
        flecksTrack,
        flameTrack,
        partTrack4,
        baseFlameTrack,
        suitTrack,
        selfDamageTrack,
        soundTrack2,
        flecksSmallTrack,
        flameSmallTrack,
        soundTrack
    )

def doViolation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    cagePropTracks = Parallel()
    toonTracks = Parallel()
    suitTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        cage = loader.loadModel('phase_3.5/models/props/barrier_cone')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        cagePos = [Point3(toonPos.getX(), y, 30.0), toon.getHpr(battle)]
        suitTrack = Sequence(getSuitTrack(attack))
        cagePropTrack = Sequence(Wait(1.5),
                                 getPropAppearTrack(cage, battle, cagePos, .5, scaleUpPoint=Point3(3), scaleUpTime=0.1),
                                 Parallel(
                                     cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                                     SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'),
                                                   duration=0.5, node=cage)
                                 ),
                                 Func(base.playSfx,
                                      base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg'),
                                      node=cage),
                                 LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
                                 Wait(1.5),
                                 LerpScaleInterval(cage, .25, MovieUtil.PNT3_ZERO),
                                 Func(cage.removeNode)
                                 )
        toonTrack = Sequence(
        Wait(2.5),
        Parallel(
            Func(toon.enterFlattened), Func(toon.playDialogueForString, "!"),
            Func(toon.showHpText, -dmg, openEnded=0),
           # Func(__doDamage, toon, dmg, t['died'])
        ),
        Wait(2.5),
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
            suitTracks.append(suitTrack)
            cagePropTracks.append(cagePropTrack)
    toonDamageTrack = getToonTracksCheat(attack, 5, ['nothing'], 0, ['neutral'])
    return Parallel(suitTracks, cagePropTracks, toonDamageTrack, toonTracks)

def doUnionCalculator(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "You can't stop production; Toons are now required to work %s extra hours." % int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(calculator.removeNode)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg')
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doContractEnforcementHealingOLD(attack):
    manager = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    selfDamageTracks = Parallel()
    suitTrack = getSuitAnimTrack(attack)
    cagePropTracks = Parallel()
    soundTracks = Parallel()
    soundTracks.append(getSoundTrack('SA_bash.ogg', delay=0, node=manager))
    hitAtleastOneSuit = 0
    for targetSuit in battle.activeSuits:
        hitAtleastOneSuit = 1
    if hitAtleastOneSuit > 0:
        soundTracks.append(getSoundTrack('LB_camera_shutter_2.ogg', delay=1, node=manager))
        soundTracks.append(getSoundTrack('LB_toonup.ogg', delay=1, node=manager))
    for targetSuit in battle.activeSuits:
        selfDamageTrack = Sequence(Wait(1.0), targetSuit.makeCongestionInterval())
        cage = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_promoted')
        cage.find('**/geo_hole_01').hide()
        platform = cage.find('**/geo_gearLift_01')
        cagePos = [Point3(0, 0, 0), Point3(180, 0, 0)]
        if targetSuit.dna.name == 'ubuster':
            cagePropTrack = Sequence(Wait(1.0), getPropAppearTrack(cage, targetSuit, cagePos, 0, scaleUpPoint=Point3(1), scaleUpTime=0),
                                 Parallel(LerpPosInterval(platform, 0.5, Point3(0, 0, 0)), LerpHprInterval(platform, 3.0, Point3(360, 0, 0)),
                                          ),
            LerpScaleInterval(cage, 0.5, Point3(0.01, 0.01, 0.01)),
            Func(cage.removeNode)
        )
        else:
            cagePropTrack = Sequence(Wait(1.0), getPropAppearTrack(cage, targetSuit, cagePos, 0, scaleUpPoint=Point3(1), scaleUpTime=0),
                                 Parallel(LerpPosInterval(platform, 0.5, Point3(0, 0, 0)), LerpHprInterval(platform, 3.0, Point3(360, 0, 0)),
                                          Sequence(ActorInterval(targetSuit, 'slip-forward', startTime=2.43), Func(targetSuit.setNeutralAnimationDrop))),
            LerpScaleInterval(cage, 0.5, Point3(0.01, 0.01, 0.01)),
            Func(cage.removeNode)
        )
        cagePropTracks.append(cagePropTrack)
        selfDamageTracks.append(selfDamageTrack)
    return Parallel(suitTracks, suitTrack, cagePropTracks, soundTracks, selfDamageTracks)

def doUnionBuster(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = Sequence(Parallel(
    getSuitAnimTrack(attack),

    ActorInterval(suit, 'sacrifice-cog', startTime=2.25, endTime=4.25)),

    Parallel(Func(suit.enableBlend),
        ActorInterval(suit, 'neutral', loop=1),
        LerpAnimInterval(
            suit,
            duration=.75,
            startAnim='sacrifice-cog',
            endAnim='neutral',
            startWeight=0.0,
            endWeight=1.0,
            blendType='easeInOut'
        )
    ),

    Func(suit.disableBlend),
    Func(suit.setNeutralAnimationDrop)
)
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
    cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))
    shaft = cage.find('**/shaft')
    shaft.setScale(0.75, 120.0, 0.75)
    shaft.setPos(0, 0, 0)
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.setBillboardPointEye()
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 40.0), toon.getHpr(battle)]
    smokeTrack = Sequence(Wait(1.5), Func(smoke.reparentTo, toon), Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                   LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                          Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale), Func(smoke.removeNode))
    cagePropTrack = Sequence(Wait(1.0), 
            getPropAppearTrack(cage, battle, cagePos, 0, scaleUpPoint=Point3(1.75), scaleUpTime=0), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.01), blendType='easeIn')),
                Parallel(SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0)
            ,cage.posInterval(3, Point3(toonPos.getX(), y, 40), blendType='easeIn')),
            Func(cage.removeNode)
        )
    toonTrack = Sequence(
        Wait(1.6),
        Parallel(
            Func(toon.enterFlattened), Func(toon.playDialogueForString, "!"),
        ), Wait(1),
        Parallel(Func(toon.showHpTextNew, -int(dmg), text="EMPLOYED!", colorCode=4),
            Func(__doDamageCheat, toon, dmg, target[0]['died']),
            Sequence(Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg'),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
    )
    toonTrack.append(Parallel(Func(toon.setToonStatusEffect, 'employed', turns=4)))
    cagePropTracks.append(cagePropTrack)
    soundTrack2 = getSoundTrack('ENC_cogjump_to_side2.ogg', delay=1, node=suit)
    return Parallel(suitTrack, soundTrack2, cagePropTracks, smokeTrack, toonTrack)

def doUnionBusterDamage(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    propDelay = 0.7
    propTracks = Parallel()
    pressTracks = Parallel()
    soundTracks = Parallel()
    suitTrack = Parallel(getSuitTrack(attack))
    suitTracks = Parallel()
    notifyTracks = Parallel()
    hitAtleastOneToon = 0
    soundTracks.append(
                Track(
                    (0.9, SoundInterval(loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=toon)),
                    (1.9, SoundInterval(globalBattleSoundCache.getSound('CHQ_FACT_stomper_small.ogg'), node=toon))
                )
            )
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg)))
        underPressure = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_underPressure')
        underPressure.setScale(0.75)
        leftGear = underPressure.find('**/geo_gear01')
        rightGear = underPressure.find('**/geo_gear02')
        underPressure.find('**/geo_hole01').hide()
        underPressure.find('**/geo_hole02').hide()
        stomper = underPressure.find('**/geo_stomperBase')
        stomper.setPos(Point3(0, 0, 35))
        propTrack = Sequence(
            Func(__showProp, underPressure, battle, pos=toon.getPos(battle)),
            Wait(propDelay),
            Parallel(
                LerpHprInterval(leftGear, 0.2, VBase3(0, -90, 0)),
                LerpHprInterval(rightGear, 0.2, VBase3(0, 90, 0))
            ),
            Wait(0.5),
            Parallel(
                LerpHprInterval(leftGear, 0.4, VBase3(0, 0, 0), blendType='easeIn'),
                LerpHprInterval(rightGear, 0.4, VBase3(0, 0, 0), blendType='easeIn')
            )
        )
        if dmg > 0:
            notifyTracks.append(notifyTrack)
            # TODO if possible: Get actual Under Pressure sound effects.
            propTrack.append(LerpPosInterval(stomper, 0.1, Point3(0, 0, 7)))
            propTrack.append(Wait(0.5))
            propTrack.append(LerpPosInterval(stomper, 0.9, Point3(0, 0, 30), blendType='easeInOut'))
            pressTracks.append(Sequence(
                Wait(0.8),
                LerpScaleInterval(toon, 0.1, VBase3(1, 0.05, 1), blendType='easeInOut'),
                Wait(0.9),
                LerpScaleInterval(toon, 0.1, VBase3(2, 2, 0.025)),
                Wait(1.0),
                Parallel(
                    Sequence(
                        Wait(0.4),
                        LerpScaleInterval(toon, 0.1, VBase3(1.4, 1.4, 1.4), blendType='easeInOut'),
                        LerpScaleInterval(toon, 0.05, VBase3(0.8, 0.8, 0.8), blendType='easeInOut'),
                        LerpScaleInterval(toon, 0.1 / 3.0, VBase3(1.0, 1.0, 1.0), blendType='easeInOut')
                    ),
                    SoundInterval(loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=toon)
                )
            ))
            propTrack.append(Func(underPressure.removeNode))
            propTracks.append(propTrack)

    toonTracks = Parallel()
    for i in range(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        dmg = tgt['hp']
        died = tgt['died']
        toonTrack = Sequence(Func(toon.headsUp, battle, suit.getPos(battle)))
        if dmg > 0:
            animTrack = Sequence(
                Wait(0.9),
                ActorInterval(toon, 'cringe', duration=2.0),
                ActorInterval(toon, 'jump', startTime=0.2),
                Func(toon.loop, 'neutral')
            )
            indicatorTrack = Sequence(
                Wait(0.91),
                Func(__doDamage, toon, dmg, died)
            )
            # If I, Professor Control, am right, you cut out the extra time when a Toon went sad.  If you don't like the sad extension, remove the condition and what's under it.
            toonTrack.append(Parallel(animTrack, indicatorTrack))
            toonTracks.append(toonTrack)

    return Parallel(propTracks, suitTracks, notifyTracks, pressTracks, toonTracks, soundTracks)

def doUnionBusterDamageSingle(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    target = attack['target']
    propDelay = 0.7
    propTracks = Parallel()
    pressTracks = Parallel()
    soundTracks = Parallel()
    suitTracks = Parallel(getSuitTrack(attack))
    dmg = target[0]['hp']
    toon = target[0]['toon']
    currentBossHealth = -1
    for s in battle.suits:
        if s.dna.name == 'safesupervis':
            currentBossHealth = s.currHP
    if currentBossHealth > 0:
        notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="-75% Damage!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 3)))
        notifyTrack.append(Parallel(Func(toon.checkDamageDown, 75)))
    else:
        notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="-50% Damage!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 3)))
        notifyTrack.append(Parallel(Func(toon.checkDamageDown, 50)))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        underPressure = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_underPressure')
        underPressure.setScale(0.75)
        leftGear = underPressure.find('**/geo_gear01')
        rightGear = underPressure.find('**/geo_gear02')
        underPressure.find('**/geo_hole01').hide()
        underPressure.find('**/geo_hole02').hide()
        stomper = underPressure.find('**/geo_stomperBase')
        stomper.setPos(Point3(0, 0, 35))
        propTrack = Sequence(
            Func(__showProp, underPressure, battle, pos=toon.getPos(battle)),
            Wait(propDelay),
            Parallel(
                LerpHprInterval(leftGear, 0.2, VBase3(0, -90, 0)),
                LerpHprInterval(rightGear, 0.2, VBase3(0, 90, 0))
            ),
            Wait(0.5),
            Parallel(
                LerpHprInterval(leftGear, 0.4, VBase3(0, 0, 0), blendType='easeIn'),
                LerpHprInterval(rightGear, 0.4, VBase3(0, 0, 0), blendType='easeIn')
            )
        )
        if dmg > 0:
            # TODO if possible: Get actual Under Pressure sound effects.
            propTrack.append(LerpPosInterval(stomper, 0.1, Point3(0, 0, 7)))
            propTrack.append(Wait(0.5))
            propTrack.append(LerpPosInterval(stomper, 0.9, Point3(0, 0, 30), blendType='easeInOut'))
            pressTracks.append(Sequence(
                Wait(0.8),
                LerpScaleInterval(toon, 0.1, VBase3(1, 0.05, 1), blendType='easeInOut'),
                Wait(0.9),
                LerpScaleInterval(toon, 0.1, VBase3(2, 2, 0.025)),
                Wait(1.0),
                Parallel(
                    Sequence(
                        Wait(0.4),
                        LerpScaleInterval(toon, 0.1, VBase3(1.4, 1.4, 1.4), blendType='easeInOut'),
                        LerpScaleInterval(toon, 0.05, VBase3(0.8, 0.8, 0.8), blendType='easeInOut'),
                        LerpScaleInterval(toon, 0.1 / 3.0, VBase3(1.0, 1.0, 1.0), blendType='easeInOut')
                    ),
                    SoundInterval(loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=toon)
                )
            ))
            soundTracks.append(
                Track(
                    (0.9, SoundInterval(loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=toon)),
                    (1.9, SoundInterval(globalBattleSoundCache.getSound('CHQ_FACT_stomper_small.ogg'), node=toon))
                )
            )
            propTrack.append(Func(underPressure.removeNode))
            propTracks.append(propTrack)

    toonTracks = Parallel()
    for i in range(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        dmg = tgt['hp']
        died = tgt['died']
        toonTrack = Sequence(Func(toon.headsUp, battle, suit.getPos(battle)))
        if dmg > 0:
            animTrack = Sequence(
                Wait(0.9),
                ActorInterval(toon, 'cringe', duration=2.0),
                ActorInterval(toon, 'jump', startTime=0.2)
            )
            indicatorTrack = Sequence(
                Wait(0.91),
                Func(__doDamage, toon, dmg, died)
            )
            # If I, Professor Control, am right, you cut out the extra time when a Toon went sad.  If you don't like the sad extension, remove the condition and what's under it.
            toonTrack.append(Parallel(animTrack, indicatorTrack))
            toonTracks.append(toonTrack)

    return Parallel(propTracks, notifyTrack, suitTracks, pressTracks, toonTracks, soundTracks)

def doContractEnforcementBan(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrackAttack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
        scale = Point3(1.2, 1.2, 1.2)
    else:
        posPoints = [Point3(.78, -1.89, -.17), VBase3(10, 250, -10)]
        scale = Point3(1, 1, 1)
    propTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        paper = globalPropPool.getProp('shredder-paper')
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
        propTrack.append(Wait(0.95))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.5, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [hitPoint], .25, parent=battle, target=t))
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
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        propTrack.append(Parallel(explodeTrack, soundTrack))
        propTracks.append(propTrack)
        toonTracks.append(Parallel(Func(toon.makeCollectCalled), Func(toon.addCollectCallRounds, 2)))
        toonTracks.append(Sequence(Wait(2.2), ActorInterval(toon, 'conked')))
    return Parallel(suitTrack, toonTracks, propTracks)

# def doContingencyClauseRetaliation(attack):
#     suit = attack['suit']
#     battle = attack['battle']
#     targets = attack['target']
#     suitTrack = Sequence(getSuitAnimTrackAttack(attack))
#     propTracks = Parallel()
#     toonTracks = Parallel()
#     smokeTracks = Parallel()
#     for t in targets:
#         toon = t['toon']
#         dmg = t['hp']
#         smoke = loader.loadModel('phase_4/models/props/test_clouds')
#         smoke.setColor(0.8, 0.7, 0.5, 1)
#         smoke.setBillboardPointEye()
#         smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, toon),
#                               Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
#                                        LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
#                               Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
#                               Func(MovieUtil.removeProp, smoke))
#         piano = globalPropPool.getProp('piano')
#         safe = globalPropPool.getProp('safe')
#         boulder = globalPropPool.getProp('boulder')
#         weight = globalPropPool.getProp('weight')
#         toonPos = toon.getPos(battle)
#         toonHpr = battle.getActorPosHpr(toon)
#         y = toonPos.getY()
#         propPos = Point3(toonPos.getX(), y, 30)
#         soundTrack2 = getSoundTrack('AA_drop_piano.ogg', delay=1.75, duration=2.0, node=suit)
#         soundTrack3 = getSoundTrack('AA_drop_boulder.ogg', delay=1.75, duration=2.0, node=suit)
#         soundTrack4 = getSoundTrack('AA_drop_safe.ogg', delay=1.75, duration=2.0,  node=suit)
#         soundTrack5 = getSoundTrack('AA_drop_bigweight.ogg', delay=1.75, duration=2.0, node=suit)
#         propTrack = Sequence(Func(piano.reparentTo, battle),
#         getPropAppearTrack(piano, parent=battle, posPoints=[propPos, VBase3(180, 90, 0)], appearDelay=0.0,
#                            scaleUpPoint=Point3(3), scaleUpTime=1.5),
#         LerpPosInterval(piano, 0.25, Point3(toonPos.getX(), y, 1)),
#         LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 2)),
#         LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
#             Wait(1.5),
#             LerpScaleInterval(piano, .25, MovieUtil.PNT3_ZERO)
#         ))
#         propTrack2 = Sequence(Func(safe.reparentTo, battle),
#             getPropAppearTrack(safe, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
#                                scaleUpPoint=Point3(4.5), scaleUpTime=1.5),
#             LerpPosInterval(safe, 0.25, Point3(toonPos.getX(), y, 0)),
#             LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 1)),
#             LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
#                 Wait(1.5),
#                 LerpScaleInterval(safe, .25, MovieUtil.PNT3_ZERO), Func(safe.removeNode)
#             ))
#         propTrack3 = Sequence(Func(boulder.reparentTo, battle),
#             getPropAppearTrack(boulder, parent=battle, posPoints=[propPos, VBase3(0, 90, 0)], appearDelay=0.0,
#                                scaleUpPoint=Point3(2), scaleUpTime=1.5),
#             LerpPosInterval(boulder, 0.25, Point3(toonPos.getX(), y, 0)),
#             LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 1)),
#             LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
#                 Wait(1.5),
#                 LerpScaleInterval(boulder, .25, MovieUtil.PNT3_ZERO)
#             ))
#         propTrack4 = Sequence(Func(weight.reparentTo, battle),
#             getPropAppearTrack(weight, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
#                                scaleUpPoint=Point3(.75), scaleUpTime=1.5),
#             LerpPosInterval(weight, 0.25, Point3(toonPos.getX(), y, 0)),
#             LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 1)),
#             LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
#                 Wait(1.5),
#                 LerpScaleInterval(weight, .25, MovieUtil.PNT3_ZERO)
#             ))
#         propTracks.append(Parallel(propTrack2, soundTrack4))
#         toonTrack = Sequence(
#         Wait(1.75),
#         Parallel(
#             Func(toon.enterFlattened),
#             #Func(__doDamageCheat, toon, dmg, t['died'])
#         ),
#         Wait(1.75),
#         Parallel(
#             Sequence(
#                 Wait(.5),
#                 Func(toon.exitFlattened)
#             ),
#             getSoundTrack('toon_decompress.ogg', node=toon),
#             Sequence(
#                 ActorInterval(toon, 'jump'),
#                 Func(toon.loop, 'neutral')
#             )
#         )
#         )
#         toonTracks.append(toonTrack)
#         smokeTracks.append(smokeTrack)
#     soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
#     toonDamageTrack = getToonTracksCheat(attack, 1.75, ['nothing'], 0, ['neutral'])
#     return Parallel(suitTrack, toonDamageTrack, smokeTracks, toonTracks, soundTrack, propTracks)

def doExclusiveRetaliation(attack):
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
        rightPosPoints = [Point3(0, 0, 0), VBase3(90, 0, 0)]
        explosionTrack = Sequence()
        explosionTrack.append(Wait(1.5))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        leftKnives = []
        rightKnives = []
        for i in xrange(0, 3):
            rightKnives.append(globalPropPool.getProp('dagger'))

        for i in xrange(0, 3):
            knifeDelay = 0.11
            rightTrack = Sequence()
            rightTrack.append(Wait(1.0))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(getPropAppearTrack(rightKnives[i], suit.getLeftHand(), rightPosPoints, 1e-06, Point3(1, 1, 1), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['face'], hitDuration=0.25, missDuration=0.25, target=t))
            if dmg > 0:
                rightKnifeTracks.append(rightTrack)

        notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextNew, - int(dmg)))
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
            suitTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'objection'),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            notifyTracks.append(Parallel(Parallel(Func(toon.makeHidden), Func(toon.addHiddenRounds, 2))))
            notifyTracks.append(notifyTrack)
    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                         dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, toonDamageTrack, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)

#notifyTracks.append(Parallel(Parallel(Func(toon.makeHidden), Func(toon.addHiddenRounds, 2))))

def doLimitedTimeOfferDenied(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    for suit in battle.activeSuits:
        suitTrack.append(Func(suit.checkLimitedTimeOffer))
        suitTrack.append(Func(suit.makeUnTrapRushJob))
        suitTrack.append(Func(suit.makeUnLureRushJob))
        suitTrack.append(Func(suit.makeUnThrowRushJob))
        suitTrack.append(Func(suit.makeUnSquirtRushJob))
        suitTrack.append(Func(suit.makeUnZapRushJob))
        suitTrack.append(Func(suit.makeUnSoundRushJob))
        suitTrack.append(Func(suit.makeUnDropRushJob))
    suitTrack.append(Wait(2.0))
    notifyTracks = Parallel()
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_objection_overruled.ogg'), node=theSuit))
    managerHealTrack = Sequence(Wait(3))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=theSuit.getDuration('frustrated'), node=theSuit)
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True
    if hitAtleastOneToon:
        return Parallel(suitTrack, managerHealTrack, soundTrack2, notifyTracks, soundTrack)
    else:
        return Parallel()


def doLimitedTimeOfferApprove(attack):
    battle = attack['battle']
    targets = attack['target']
    notifyTracks = Parallel()
    soundTracks = Parallel()
    suitTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        soundTrack = getSoundTrack('LB_toonup.ogg', node=toon)
        notifyTrack = Sequence(Func(toon.showHpTextNew, 0, text="+5% Damage!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.makeDamageUpGovernaught)))
        notifyTrack.append(Parallel(Func(toon.checkDamageUpGovernaught, 5)))
        if dmg > 0:
            suitTracks.append(getSuitAnimTrack(attack))
            soundTracks.append(soundTrack)
            soundTracks.append(Wait(3.0))
            notifyTracks.append(notifyTrack)
    return Parallel(notifyTracks, suitTracks, soundTracks)

def doUnionBusterDamageOld(attack):
    battle = attack['battle']
    targets = attack['target']
    cagePropTracks = Parallel()
    toonTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
        cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))
        shaft = cage.find('**/shaft')
        shaft.setScale(0.75, 120.0, 0.75)
        shaft.setPos(0, 0, 0)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        y = toonPos.getY()
        if dmg == 0:
            y -= 5
        cagePos = [Point3(toonPos.getX(), y, 40.0), toon.getHpr(battle)]
        smokeTrack = Sequence(Wait(0.6), Func(smoke.reparentTo, toon), Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                   LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                          Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale), Func(smoke.removeNode))
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0, scaleUpPoint=Point3(1.75), scaleUpTime=0), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.01), blendType='easeIn')),
                SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0)
            ,
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0), cage.posInterval(3, Point3(toonPos.getX(), y, 40), blendType='easeIn'),
            Func(cage.removeNode)
        )
        toonTrack = Sequence(
        Wait(.5),
        Parallel(
            Func(toon.enterFlattened), Func(toon.playDialogueForString, "!"),
        ),
        Wait(2.5),
        Parallel(Func(toon.showHpText, - int(dmg)),
            #Func(__doDamage, toon, dmg, t['died']),
            Sequence(
                Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg'),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
    )
        if dmg > 0:
            cagePropTracks.append(cagePropTrack)
            toonTracks.append(toonTrack)
            smokeTracks.append(smokeTrack)
    toonDamageTrack = getToonTracksCheat(attack, 3.2, ['nothing'], 0, ['neutral'])
    return Parallel(cagePropTracks, smokeTracks, toonDamageTrack, toonTracks)

def doUnionBust(attack):
    manager = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    managerTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
    targetMovies = Parallel()

    for index in xrange(len(targets)):
        targetData = targets[index]

        dmg = targetData.get('hp', 0)

        if 'suit' not in targetData:
            continue

        targetSuit = targetData['suit']

        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()

        cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
        cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))

        shaft = cage.find('**/shaft')
        shaft.setScale(0.75, 120.0, 0.75)
        shaft.setPos(0, 0, 0)

        cagePos = [Point3(0, 0, 40.0), Point3(0, 0, 0)]

        suitTrack = Sequence(
            Wait(2.0),
            Parallel(Func(targetSuit.showHpTextNew, -dmg, text="BUSTED!", colorCode=4), Func(targetSuit.setHealthForMe, - dmg),
                               Func(targetSuit.updateHealthBar, 0), 
                ActorInterval(targetSuit, 'flatten', duration=.55),
                MovieUtil.createSuitCrashTrack(targetSuit, battle, 7)
            )
        )

        smokeTrack = Sequence(
            Wait(2.0),
            Func(smoke.reparentTo, targetSuit),
            Parallel(
                LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                LerpColorScaleInterval(smoke, 1.0, Vec4(1, 1, 1, 0))
            ),
            Func(smoke.reparentTo, hidden),
            Func(smoke.clearColorScale),
            Func(smoke.removeNode)
        )

        hpTrack = Sequence(
            Wait(2.0),
            Sequence(Parallel(Func(manager.setSuitStatusEffect, 'damageUp', modifier=int(math.ceil(dmg * .05)), mode='refreshModifier')), 
                                     Parallel(Func(manager.showHpTextNew, +dmg, text="+%s%%" % int(math.ceil(dmg * .05)) + " Damage!", colorCode=1),
                                                   Func(manager.setHealthForMe, +dmg),
                                                   Func(manager.updateHealthBar, 0)),
                               Func(manager.setNeutralAnimation))
        )

        cagePropTrack = Sequence(
            Wait(1.6),
            getPropAppearTrack(cage, targetSuit, cagePos, 0, scaleUpPoint=Point3(1.4), scaleUpTime=0),
            cagePosition,
            cage.posInterval(0.5, Point3(0, 0, 0.01), blendType='easeIn'),
            Parallel(
                SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0),
                Sequence(
                    Wait(1.0),
                    cage.posInterval(2.0, Point3(0, 0, 40), blendType='easeIn')
                )
            ),
            Func(cage.removeNode)
        )

        targetMovie = Parallel(
            suitTrack,
            hpTrack,
            cagePropTrack,
            smokeTrack
        )

        targetMovies.append(Sequence(Wait(index * 1.0), targetMovie))

    soundTrack = SoundInterval(globalBattleSoundCache.getSound('SA_quake.ogg'), node=manager)

    return Parallel(
        managerTrack,
        soundTrack,
        targetMovies
    )

def doUnionWages(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(calculator.removeNode)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
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
    suitTrack = Sequence(getSuitAnimTrack(attack))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 0, 3.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 0, 3.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 0, 3.9, [spinEffect3, suit, 0], softStop=-2)
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 5))
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, + 100, text="+5% Damage!", colorCode=1),
                                Func(suit.setHealthForMe, + 100),
                                Func(suit.updateHealthBar, 0))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, makeImmune, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doUnionWages2(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(calculator.removeNode)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
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
    suitTrack = Sequence(getSuitAnimTrack(attack))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 0, 3.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 0, 3.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 0, 3.9, [spinEffect3, suit, 0], softStop=-2)
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 10))
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, + 200, text="+10% Damage!", colorCode=1),
                                Func(suit.setHealthForMe, + 200),
                                Func(suit.updateHealthBar, 0))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, makeImmune, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doUnionWages3(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(calculator.removeNode)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
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
    suitTrack = Sequence(getSuitAnimTrack(attack))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 0, 3.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 0, 3.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 0, 3.9, [spinEffect3, suit, 0], softStop=-2)
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 15))
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, + 300, text="+15% Damage!", colorCode=1),
                                Func(suit.setHealthForMe, + 300),
                                Func(suit.updateHealthBar, 0))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, makeImmune, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doUnionWages4(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(calculator.removeNode)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
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
    suitTrack = Sequence(getSuitAnimTrack(attack))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 0, 3.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 0, 3.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 0, 3.9, [spinEffect3, suit, 0], softStop=-2)
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 20))
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, + 400, text="+20% Damage!", colorCode=1),
                                Func(suit.setHealthForMe, + 400),
                                Func(suit.updateHealthBar, 0))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, makeImmune, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doUnionWages5(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(calculator.removeNode)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
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
    suitTrack = Sequence(getSuitAnimTrack(attack))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0], softStop=-2)
    spinTrack1 = getPartTrack(spinEffect1, 0, 3.9, [spinEffect1, suit, 0], softStop=-2)
    spinTrack2 = getPartTrack(spinEffect2, 0, 3.9, [spinEffect2, suit, 0], softStop=-2)
    spinTrack3 = getPartTrack(spinEffect3, 0, 3.9, [spinEffect3, suit, 0], softStop=-2)
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 25))
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextNew, + 500, text="+25% Damage!", colorCode=1),
                                Func(suit.setHealthForMe, + 500),
                                Func(suit.updateHealthBar, 0))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, makeImmune, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

def doNoStrikeClause(attack):
    suit = attack['suit']
    targets = attack['target']
    tape = globalPropPool.getProp('redtape')
    tape.setColor(0.129, 0, 0.329, 1)
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
        notifyTracks.append(Sequence(Wait(2.4), Func(toon.showHpString, "NO DEFENSE!", 10)))
        allTubeTracks.append(tubeTracks)
        toonTracks.append(Sequence(Wait(2.4), ActorInterval(toon, 'struggle')))
        toonTracks.append(Parallel(Func(toon.makeNoDodge), Func(toon.addNoDodgeRounds, 3)))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.75, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack, allTubeTracks, notifyTracks)

def doBreachOfContract(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = loader.loadModel('phase_5/models/props/ttrpg_m_ene_prp_deniedSign')
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 4.0),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), -.6, 0, -0.25, 0, 90, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(sanctioned.removeNode)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="BREACHED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'breached', modifier=50, turns=3, mode='keepHighest')))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doBreachOfContract2(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = loader.loadModel('phase_5/models/props/ttrpg_m_ene_prp_deniedSign')
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 4.0),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), -.6, 0, -0.25, 0, 90, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(sanctioned.removeNode)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="BREACHED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.checkDamageDown, 25)))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'breached', modifier=25, turns=3, mode='keepHighest')))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doDetourOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    suitTrack = getSuitTrack(attack)
    partTracks = Parallel()
    explosionTracks = Parallel()
    toonTrack = getToonTrackCheat(attack, 2.0, ['conked'], 0.2, ['sidestep'])
    notifyTrack = Sequence(Wait(2.0), Func(toon.showHpTextNew, -int(dmg), text="DETOURED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.makeConfused), Func(toon.addConfusedRounds, 2)))

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

    for t in targets:
        toon = t['toon']
        dmg = t['hp']

        numArrows = 20
        radius = 2.0
        partTrack = Parallel()
        for i in xrange(numArrows):
            # Create the arrow.
            arrow = loader.loadModel('phase_3.5/models/gui/matching_game_gui').find(
                '**/minnieArrow') 
            arrow.setScale(5.0)
            arrow.setBillboardPointEye()
            arrow.setR(random.randint(0, 360))
            arrow.setColor((random.random(), random.random(), random.random(), 1))

            # Now get the position of the arrow.
            angle = random.random() * 2.0 * math.pi 
            x = radius * math.cos(angle) + toon.getX(battle)
            y = radius * math.sin(angle) + toon.getY(battle)

            # Now assemble the arrow movement.
            oneArrowTrack = Sequence(
                Wait(0.9 + i * 0.25),  # The delay for the arrow.
                Func(arrow.reparentTo, battle),
                Func(arrow.setPos, Point3(x, y, 0)),
                Track(
                    (0.0, LerpFunctionInterval(arrow.setZ, 0.8, 0, 3, blendType='easeOut')),  # Raise the arrow.
                    (0.6, LerpFunctionInterval(arrow.setAlphaScale, 0.2, 1, 0))
                    # Before the arrow completes raising, make it fade.
                ),
                Func(MovieUtil.removeProp, arrow)
            )
            partTrack.append(oneArrowTrack)

        partTracks.append(partTrack)

        if dmg > 0:
            headParts = toon.getHeadParts()
            torsoParts = toon.getTorsoParts()
            legsParts = toon.getLegsParts()
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
            explosionTracks.append(Sequence(
                Wait(2.0),
                MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3)
            ))
            # I guess it doesn't hurt to put the color track inside of explosionTracks.
            explosionTracks.append(Sequence(
                Wait(2.0),
                changeColor(headParts),
                changeColor(torsoParts),
                changeColor(legsParts),
                Wait(3.5),
                resetColor(headParts),
                resetColor(torsoParts),
                resetColor(legsParts)
            ))
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.0)

    return Parallel(suitTrack, notifyTrack, partTracks, explosionTracks, soundTrack1, toonTrack)

def doRoadBlock(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    squishTracks = Parallel()
    safeTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    appearSfx = loader.loadSfx('phase_5/audio/sfx/SA_watercooler_appear_only.ogg')
    throwSfx = loader.loadSfx('phase_5/audio/sfx/SA_hardball_impact_only.ogg')
    landSfx = loader.loadSfx('phase_5/audio/sfx/AA_drop_bigweight_miss.ogg')
    landSfx.setVolume(.420)
    soundTracks.append(getSoundTrack('SA_watercooler_appear_only.ogg', delay=.85))
    soundTracks.append(Sequence(Wait(.85 + 1.6), SoundInterval(throwSfx, duration=.75)))
    soundTracks.append(Sequence(Wait(.85 + 1.6 + .9), SoundInterval(landSfx)))
    for t in targets:
        toon = t['toon']
        toonTrack = Parallel(Func(toon.setToonStatusEffect, 'gagBan'))
        toonTracks.append(toonTrack)
        safe = loader.loadModel('phase_3.5/models/props/barrier_cone')
        safe.setHpr(0, 180, 0)
        safe.setPos(0, 0, 0)
        safe.setScale(.000001)
        toonScale = toon.find('**/actorGeom').getScale()
        squishTrack = toon.find('**/actorGeom').scaleInterval(.05, (1, 1, .01))
        safeTrack = Parallel(
            Sequence(Sequence(
                Wait(0.6), Func(safe.reparentTo, suit.getRightHand()),
                Parallel(
                    safe.scaleInterval(.25, (1, 1, 1)), 
                ),
                Wait(1.6), Func(safe.wrtReparentTo, render),
                Parallel(safe.scaleInterval(.25, (2, 2, 2)),
                    safe.hprInterval(.9, (0, 360, 0)), 
                    ProjectileInterval(safe, duration=.9, endPos=(toon.getPos()), gravityMult=5.0),
                    Sequence(Wait(.85), squishTrack)
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

    return Parallel(suitTrack, soundTracks, safeTracks, toonTracks, squishTracks)

def doSalesPitch(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = False
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = True

    suitType = getSuitBodyType(attack['suitName'])
    suitDelay = 1.3
    damageDelay = 2.25
    dodgeDelay = 1.86
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ballPosPoints = [Point3(-0.25, 0.03, -0.31), VBase3(-1.152, 86.581, -76.784)]
    propTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        ball = globalPropPool.getProp('baseball')
        propTrack = Sequence(getPropAppearTrack(ball, suit.getRightHand(), ballPosPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.25))
        propTrack.append(Wait(suitDelay))
        propTrack.append(Func(battle.movie.needRestoreRenderProp, ball))
        propTrack.append(Func(ball.wrtReparentTo, battle))
        toonPos = toon.getPos(battle)
        x = toonPos.getX()
        y = toonPos.getY()
        z = toonPos.getZ()
        z = z + 0.2
        toonTrack = Sequence(
        Wait(suitDelay + 3.1),
        Parallel(
            Func(toon.enterFlattened), Func(toon.playDialogueForString, "!"),
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
        propTrack.append(Parallel(Func(ball.setScale, 25), getThrowTrack(ball, toon.getPos(battle), 2.35, battle, -64.288)))
        propTrack.append(Sequence(Func(ball.reparentTo, battle),
        LerpPosInterval(ball, 0.1, Point3(toonPos.getX(), y, 2)),
        LerpPosInterval(ball, 0.1, Point3(toonPos.getX(), y, 1)),
        LerpPosInterval(ball, 0.1, Point3(toonPos.getX(), y, 2)),
            LerpPosInterval(ball, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
            Wait(1.5),
            LerpScaleInterval(ball, .25, MovieUtil.PNT3_ZERO), Func(MovieUtil.removeProp, ball), Func(battle.movie.clearRenderProp, ball)
        )))
        propTracks.append(propTrack)

    soundTrack = getSoundTrack('SA_extra_tip.ogg', delay=1.8, node=suit)
    soundTrack2 = getSoundTrack('AA_drop_bigweight.ogg', delay=suitDelay + 3.1, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack2, propTracks, soundTrack)

def doClosingTime(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    speedTrack = Parallel()
    for headPart in theSuit.animatedHeadParts:
        speedTrack.append(Sequence(ActorInterval(headPart, 'come-on'), Func(theSuit.setNeutralAnimationHead)))
    suitTrack = Sequence(Parallel(
    getSuitAnimTrack(attack)),
    Parallel(Func(theSuit.enableBlend), 
        ActorInterval(theSuit, 'pace', loop=1),
        LerpAnimInterval(
            theSuit,
            duration=.25,
            startAnim='come-on',
            endAnim='pace',
            startWeight=0.0,
            endWeight=1.0,
            blendType='easeInOut'
        )
    ),

    Func(theSuit.disableBlend),
    Func(theSuit.setNeutralAnimationDrop), Wait(2.0)
)
    speedTrack.append(Func(theSuit.checkBattleSpeed2, theSuit, + .25))
    makeImmune = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 5))
    managerHealTrack = Sequence(Func(theSuit.showHpTextNew, 0, text="+5% Damage!", colorCode=1))
    return Parallel(speedTrack, managerHealTrack, makeImmune, suitTrack)

# def doDetour(attack):
#     suit = attack['suit']
#     battle = attack['battle']
#     target = attack['target']
#     dmg = target[0]['hp']
#     toon = target[0]['toon']
#     sanctioned = loader.loadModel('phase_5/models/props/ttrpg_m_ene_prp_deniedSign')
#     missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
#     propTrack = Sequence(
#         Wait(0.5),
#         Func(battle.movie.needRestoreRenderProp, sanctioned),
#         Func(sanctioned.reparentTo, render),
#         Func(sanctioned.setScale, 3.5),
#         Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
#         Func(sanctioned.setP, 0),
#         Func(sanctioned.setR, 0),
#         getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
#         Func(sanctioned.removeNode)
#     )
#     toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0.2, ['sidestep'])
#     suitTrack = getSuitTrack(attack)
#     soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
#     notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="DETOURED!", colorCode=1))
#     notifyTrack.append(Parallel(Func(toon.makeConfused), Func(toon.addConfusedRounds, 2)))
#     return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doCompensationClaims(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    target = attack['target']
    suitTrack = Sequence(ActorInterval(suit, 'soak', duration=2.0), Parallel(Func(suit.setSuitStatusEffect, 'compensationClaims', modifier=15, mode='refreshModifier'), Func(suit.setDizzy3, 1), 
                                                                             Func(suit.setSuitStatusEffect, 'unionBusterNoAttack', turns=2), 
                                                                             Func(suit.showHpTextNew, 0, text="+15% Vulnerable!", colorCode=4), ActorInterval(suit, 'flatten')), Func(suit.setNeutralAnimationDrop))
    propTracks = Parallel()
    toonTracks = Parallel()
    smokeTracks = Parallel()
    paper2 = loader.loadModel('phase_11/models/lawbotHQ/LB_paper_twist_stacks')
    paper = paper2.find('**/paper_stack_1')
    toonPos = suit.getPos(battle)
    gavelPos = Point3(0, 0, 30)
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.setBillboardPointEye()
    toonHpr = battle.getActorPosHpr(suit)
    y = toonPos.getY()
    propPos = Point3(toonPos.getX(), y, 30)
    smokeTrack = Sequence(Wait(2.25), Func(smoke.reparentTo, suit),
                            Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                    LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                            Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                            Func(MovieUtil.removeProp, smoke))
    propTrack = Sequence(Func(paper.reparentTo, battle),
    getPropAppearTrack(paper, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                        scaleUpPoint=Point3(4), scaleUpTime=2.0),
    LerpPosInterval(paper, 0.25, Point3(toonPos.getX(), y, 1)),
    LerpPosInterval(paper, 0.1, Point3(toonPos.getX(), y, 2)),
    LerpPosInterval(paper, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
        Wait(1.5),
        LerpScaleInterval(paper, .25, MovieUtil.PNT3_ZERO)
    ))
    propTracks.append(propTrack)
    smokeTracks.append(smokeTrack)
    soundTrack = getSoundTrack('AA_drop_bigweight_miss.ogg', delay=2.25, node=suit)
    soundTrack2 = getSoundTrack('incoming_whistleALT.ogg', node=suit)
    return Parallel(suitTrack, soundTrack2, smokeTracks, toonTracks, propTracks, soundTrack)

def doGreenLight(attack):
    suit = attack['suit']
    manager = attack['suit']
    battle = attack['battle']
    target = attack['target']

    if not target:
        return Sequence()

    targetSuit = target[0]['suit']
    node = targetSuit.getGeomNode().getChild(0)
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
    suitTrack = Sequence(
            # Let the damage/reaction animation reach its ending pose.
            ActorInterval(
                manager,
                'neutral',
                endTime=0
            ),

            Func(manager.enableBlend),

            # Both animations must be actively controlled during the blend.
            Func(manager.loop, 'neutral'),
            Func(manager.loop, 'sanction'),

            Parallel(getSuitAnimTrack(attack), LerpAnimInterval(
                manager,
                duration=0.25,
                startAnim='neutral',
                endAnim='sanction',
                startWeight=0.0,
                endWeight=1.0,
                blendType='easeInOut'
            ), Sequence(ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1
            ), ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - .9), 
                ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1
            ), ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1.1
            ))),

            Func(manager.disableBlend),

            # Ensure the intended neutral animation remains playing.
            Func(manager.setNeutralAnimationDrop), Wait(2.0)
        )
    soundTrack2 = getSoundTrack('SA_sanction.ogg')
    suitTrack.append(Func(targetSuit.setSuitStatusEffect, 'greenLight', modifier=1, turns=2))
    suitTrack.append(Wait(2.0))
    return Parallel(suitTrack, suitColorTrack, soundTrack2)

def doContingencyClauseRetaliation(attack):
    suit = attack['suit']
    manager = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    suitTrack = Sequence(
            # Let the damage/reaction animation reach its ending pose.
            ActorInterval(
                manager,
                'neutral',
                endTime=0
            ),

            Func(manager.enableBlend),

            # Both animations must be actively controlled during the blend.
            Func(manager.loop, 'neutral'),
            Func(manager.loop, 'sanction'),

            Parallel(getSuitAnimTrack(attack), LerpAnimInterval(
                manager,
                duration=0.25,
                startAnim='neutral',
                endAnim='sanction',
                startWeight=0.0,
                endWeight=1.0,
                blendType='easeInOut'
            ), Sequence(ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1
            ), ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - .9), 
                ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1
            ), ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1.1
            ))),

            Func(manager.disableBlend),

            # Ensure the intended neutral animation remains playing.
            Func(manager.setNeutralAnimationDrop), Wait(2.0)
        )
    propTracks = Parallel()
    toonTracks = Parallel()
    notifyTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(.5), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        safe = loader.loadModel('phase_3.5/models/props/barrier_cone')
        toonPos = toon.getPos(battle)
        toonHpr = battle.getActorPosHpr(toon)
        y = toonPos.getY()
        propPos = Point3(toonPos.getX(), y, 30)
        soundTrack4 = getSoundTrack('AA_drop_safe_miss.ogg', delay=.5, duration=2.0, node=suit)
        propTrack2 = Sequence(Func(safe.reparentTo, battle),
            getPropAppearTrack(safe, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2.5), scaleUpTime=.25),
            LerpPosInterval(safe, 0.25, Point3(toonPos.getX(), y, 0)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.0),
                LerpScaleInterval(safe, .25, MovieUtil.PNT3_ZERO), Func(safe.removeNode)
            ))
        toonTrack = Sequence(
        Wait(.5),
        Parallel(
            Func(toon.enterFlattened), Func(toon.playDialogueForString, "!"),
            #Func(__doDamageCheat, toon, dmg, t['died'])
        ),
        Wait(1.25),
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
        notifyTrack = Sequence(Wait(.5), Func(toon.showHpTextNew, - int(dmg), text="-50% Damage!", colorCode=4))
        notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'damageDown', modifier=50, turns=2, mode='keepHighest')))
        if dmg > 0:
            notifyTracks.append(notifyTrack)
            toonTracks.append(toonTrack)
            smokeTracks.append(smokeTrack)
            propTracks.append(Parallel(propTrack2, soundTrack4))
    soundTrack = getSoundTrack('SA_sanction.ogg', node=suit)
    toonDamageTrack = getToonTracksCheat(attack, .5, ['nothing'], 0, ['neutral'])
    if hitAtleastOneToon:
        return Parallel(suitTrack, toonDamageTrack, notifyTracks, smokeTracks, toonTracks, soundTrack, propTracks)
    else:
        return Parallel()

def doContractEnforcementHealing(attack):
    manager = attack['suit']
    targets = attack['target']

    if not targets:
        return Sequence()

    targetTracks = Parallel()

    suitTrack = Sequence(
        ActorInterval(manager, 'neutral', endTime=0),
        Func(manager.enableBlend),
        Func(manager.loop, 'neutral'),
        Func(manager.loop, 'sanction'),
        Parallel(
            getSuitAnimTrack(attack),
            LerpAnimInterval(manager, duration=0.25, startAnim='neutral', endAnim='sanction', startWeight=0.0, endWeight=1.0, blendType='easeInOut'),
            Sequence(
                ActorInterval(manager, 'sanction', startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1),
                ActorInterval(manager, 'sanction', startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - .9),
                ActorInterval(manager, 'sanction', startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1),
                ActorInterval(manager, 'sanction', startTime=manager.getDuration('sanction') - 1.1)
            )
        ),
        Func(manager.disableBlend),
        Func(manager.setNeutralAnimationDrop),
        Wait(2.0)
    )

    soundTrack = Parallel(
        getSoundTrack('SA_sanction.ogg'),
        getSoundTrack('LB_toonup.ogg', node=manager)
    )

    for targetData in targets:
        if 'suit' not in targetData:
            continue

        targetSuit = targetData['suit']

        if targetSuit.dna.name == 'hustle':
            targetTrack = Sequence(
                Wait(1.0),
                Parallel(
                    Func(targetSuit.showHpString, '+5% Defense!'),
                    Func(targetSuit.setSuitStatusEffect, 'shielding', modifier=5, mode='refreshModifier')
                ),
                Func(targetSuit.setNeutralAnimationDrop)
            )

        else:
            targetTrack = Sequence(
                Wait(1.0),
                Parallel(
                    Sequence(
                        ActorInterval(targetSuit, 'effort', startTime=targetSuit.getDuration('effort'), endTime=max(0, targetSuit.getDuration('effort') - 1.0), playRate=-1.0),
                        ActorInterval(targetSuit, 'effort', startTime=max(0, targetSuit.getDuration('effort') - 1.0))
                    ),
                    Func(targetSuit.showHpString, '+5% Defense!'),
                    Func(targetSuit.setSuitStatusEffect, 'shielding', modifier=5, mode='refreshModifier')
                ),
                Func(targetSuit.setNeutralAnimationDrop)
            )

        targetTracks.append(targetTrack)

    return Parallel(suitTrack, soundTrack, targetTracks)

def doYellowLight(attack):
    suit = attack['suit']
    manager = attack['suit']
    battle = attack['battle']
    target = attack['target']
    node = suit.getGeomNode().getChild(0)
    suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=.25, colorScale=(0.973, 1, 0, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(0.973, 1, 0, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(0.973, 1, 0, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(0.973, 1, 0, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                           blendType='easeInOut')
                              )
    suitTrack = Sequence(
            # Let the damage/reaction animation reach its ending pose.
            ActorInterval(
                manager,
                'neutral',
                endTime=0
            ),

            Func(manager.enableBlend),

            # Both animations must be actively controlled during the blend.
            Func(manager.loop, 'neutral'),
            Func(manager.loop, 'sanction'),

            Parallel(getSuitAnimTrack(attack), LerpAnimInterval(
                manager,
                duration=0.25,
                startAnim='neutral',
                endAnim='sanction',
                startWeight=0.0,
                endWeight=1.0,
                blendType='easeInOut'
            ), Sequence(ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1
            ), ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - .9), 
                ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1
            ), ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1.1
            ))),

            Func(manager.disableBlend),

            # Ensure the intended neutral animation remains playing.
            Func(manager.setNeutralAnimationDrop), Wait(2.0)
        )
    soundTrack2 = getSoundTrack('SA_sanction.ogg')
    suitTrack.append(Wait(2.0))
    for targetSuit in battle.activeSuits:
        suitTrack.append(Func(targetSuit.setSuitStatusEffect, 'yellowLight', modifier=-50, turns=2))
    for toon in battle.activeToons:
        suitTrack.append(Func(toon.setToonStatusEffect, 'yellowLight', modifier=-50, turns=2))
    return Parallel(suitTrack, suitColorTrack, soundTrack2)

def doRedLight(attack):
    suit = attack['suit']
    manager = attack['suit']
    battle = attack['battle']
    target = attack['target']

    if not target:
        return Sequence()

    targetSuit = target[0]['suit']
    node = targetSuit.getGeomNode().getChild(0)
    suitColorTrack = Sequence(LerpColorScaleInterval(node, duration=.25, colorScale=(1, 0, 0, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(1, 0, 0, 1),
                                                     blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(1, 0, 0, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(1, 0, 0, 1),
                           blendType='easeInOut'),
    LerpColorScaleInterval(node, duration=.25, colorScale=(1, 1, 1, 1),
                           blendType='easeInOut')
                              )
    suitTrack = Sequence(
            # Let the damage/reaction animation reach its ending pose.
            ActorInterval(
                manager,
                'neutral',
                endTime=0
            ),

            Func(manager.enableBlend),

            # Both animations must be actively controlled during the blend.
            Func(manager.loop, 'neutral'),
            Func(manager.loop, 'sanction'),

            Parallel(getSuitAnimTrack(attack), LerpAnimInterval(
                manager,
                duration=0.25,
                startAnim='neutral',
                endAnim='sanction',
                startWeight=0.0,
                endWeight=1.0,
                blendType='easeInOut'
            ), Sequence(ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1
            ), ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - .9), 
                ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1, endTime=manager.getDuration('sanction') - 1.1
            ), ActorInterval(
                manager,
                'sanction',
                startTime=manager.getDuration('sanction') - 1.1
            ))),

            Func(manager.disableBlend),

            # Ensure the intended neutral animation remains playing.
            Func(manager.setNeutralAnimationDrop), Wait(2.0)
        )
    soundTrack2 = getSoundTrack('SA_sanction.ogg')
    suitTrack.append(Func(targetSuit.setSuitStatusEffect, 'redLight', modifier=1, turns=2))
    suitTrack.append(Wait(2.0))
    return Parallel(suitTrack, suitColorTrack, soundTrack2)

def doDetour(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = loader.loadModel('phase_5/models/modules/ttcc_prop_sign_construction_suit')
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 0.25),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 5, 0, -1, -90, 90, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(sanctioned.removeNode)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['slip-backward'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('AA_drop_safe_miss.ogg', delay =.8, node=suit)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(0.8), Func(toon.showHpTextNew, -int(dmg), text="DETOURED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.makeConfused), Func(toon.addConfusedRounds, 2)))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doYield(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = loader.loadModel('phase_5/models/props/ttrpg_m_ene_prp_deniedSign')
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 4.0),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), -.6, 0, -0.25, 0, 90, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(sanctioned.removeNode)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="YIELDED!", colorCode=1))
    currentBossHealth = -1
    for s in battle.suits:
        if s.dna.name == 'safesupervis':
            currentBossHealth = s.currHP
    if currentBossHealth > 0:
        notifyTrack.append(Parallel(Func(toon.checkDamageDown, 75)))
    else:
        notifyTrack.append(Parallel(Func(toon.checkDamageDown, 50)))
    notifyTrack.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 3)))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doYieldGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    notifyTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    toonTracks = Parallel()
    propTracks = Parallel()
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    if hitAtleastOneToon > 0:
        soundTracks.append(soundTrack)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        suitTrack = getSuitAnimTrack(attack)
        soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
        notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="YIELDED!", colorCode=1))
        if dmg > 0:
            sanctioned = loader.loadModel('phase_5/models/props/ttrpg_m_ene_prp_deniedSign')
            missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
            propTrack = Sequence(
                Wait(0.5),
                Func(battle.movie.needRestoreRenderProp, sanctioned),
                Func(sanctioned.reparentTo, render),
                Func(sanctioned.setScale, 4.0),
                Func(sanctioned.setPosHpr, suit.getLeftHand(), -.6, 0, -0.25, 0, 90, 0),
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
            suitTracks.append(Sequence(Parallel(suitTrack, LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle)),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            notifyTrack.append(Parallel(Func(toon.checkDamageDown, 25)))
            notifyTrack.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 3)))
            notifyTracks.append(notifyTrack)
    toonDamageTrack = getToonTracksCheat(attack, 0.8, ['conked'], 0, ['neutral'])
    return Parallel(suitTracks, toonTracks, propTracks, soundTracks, toonDamageTrack, notifyTracks)

def doContractEnforcement(attack, ind, ind2, ind3):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    if len(battle.activeSuits) > 1 and ind == 1:
        targetSuit = battle.activeSuits[ind]
    elif ind == 0:
        targetSuit = battle.activeSuits[ind]
    else:
        targetSuit = None
    if len(battle.activeSuits) >= 3 and ind2 == 2:
        targetSuit2 = battle.activeSuits[ind2]
    elif len(battle.activeSuits) >= 4 and ind2 == 3:
        targetSuit2 = battle.activeSuits[ind2]
    else:
        targetSuit2 = None
    if len(battle.activeSuits) >= 5 and ind3 == 4:
        targetSuit3 = battle.activeSuits[ind3]
    elif len(battle.activeSuits) >= 6 and ind3 == 5:
        targetSuit3 = battle.activeSuits[ind3]
    else:
        targetSuit3 = None
    targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3, theSuit) if s is not None]
    suitTracks = Parallel()
    liftTracks = Parallel()
    knifeTracks = Parallel()
    soundTrack2 = getSoundTrack('SA_bash.ogg', node=theSuit)
    suitTrack2 = Sequence(Parallel(
        getSuitAnimTrack(attack)))
    if targetSuits:
        for target in targetSuits:
            liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
            #liftEffect.setPos(target.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftEffect.reparentTo(target)
            liftTracks.append(getPartTrack(liftEffect, 2, 4.0, [liftEffect, target, 0], softStop=-2))

            suitTrack = Sequence(
                Wait(1.5)
            )
            suitTrack.append(Parallel(Func(target.checkContracted)))
            suitTracks.append(suitTrack)
            cage = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_promoted')
            cage.find('**/geo_hole_01').hide()
            platform = cage.find('**/geo_gearLift_01')
            cagePos = [Point3(0, 0, 0), Point3(180, 0, 0)]
            knifeTrack = Sequence(Wait(1.5), getPropAppearTrack(cage, target, cagePos, 0, scaleUpPoint=Point3(1), scaleUpTime=0),
                                     Parallel(LerpPosInterval(platform, 0.5, Point3(0, 0, 0)), LerpHprInterval(platform, 3.0, Point3(360, 0, 0)), getSoundTrack('LB_toonup.ogg', node=suit),
                                              Sequence(ActorInterval(target, 'slip-forward', startTime=2.43), Func(target.setNeutralAnimationDrop))),
                                     LerpScaleInterval(cage, 0.5, Point3(0.01, 0.01, 0.01)),
                                     Func(cage.removeNode)
                                     )
            knifeTrack2 = Sequence(Wait(1.5), getPropAppearTrack(cage, target, cagePos, 0, scaleUpPoint=Point3(1), scaleUpTime=0),
                                     Parallel(LerpPosInterval(platform, 0.5, Point3(0, 0, 0)), LerpHprInterval(platform, 3.0, Point3(360, 0, 0)), getSoundTrack('LB_toonup.ogg', node=suit),
                                              ),
                                     LerpScaleInterval(cage, 0.5, Point3(0.01, 0.01, 0.01)),
                                     Func(cage.removeNode)
                                     )
            if not target.dna.name == 'ubuster':
                knifeTracks.append(knifeTrack)
            else:
                knifeTracks.append(knifeTrack2)
    soundTrack = getSoundTrack('LB_camera_shutter_2.ogg', delay=1.5)

    return Parallel(
        suitTrack2,
        suitTracks,
        liftTracks,
        soundTrack2,
        soundTrack,
        knifeTracks
    )

def doProfiteering(attack, ind):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    targetSuit = battle.activeSuits[dmg]
    battle = attack['battle']
    origPos, origHpr = battle.getActorPosHpr(suit)
    targetSuitPos, targetSuitHpr = battle.getActorPosHpr(targetSuit)
    targetSuitAnimTrack = Sequence(Wait(5.25), ActorInterval(targetSuit, 'flatten', endTime=0.55))
    selfDamageTrack = Sequence(Wait(5.25), Func(targetSuit.checkProfiteering, suit, battle), targetSuit.makeProfiteeringInterval(suit, battle))
    soundTrack3 = getSoundTrack('SA_protoon_shake.ogg', delay=0.5, node=suit)
    suitAnimTrack = Sequence(Parallel(soundTrack3, Sequence(Wait(.75), LerpPosInterval(suit, .55, origPos, other=battle)), Sequence(ActorInterval(suit, 'quick-jump', duration=1.3),
                             ActorInterval(suit, 'slip-forward', playRate=1.25))), Func(suit.setNeutralAnimationDrop))
    moveTrack = Sequence(ActorInterval(suit, 'sacrifice-cog', endTime=1.5),

    Parallel(Sequence(ActorInterval(suit, 'quick-jump', endTime=.5), Wait(.5)), Sequence(Func(suit.enableBlend),
        LerpAnimInterval(
            suit,
            duration=.5,
            startAnim='sacrifice-cog',
            endAnim='quick-jump',
            startWeight=0.0,
            endWeight=1.0,
            blendType='easeInOut'
        ),  Func(suit.disableBlend))),  Wait(.25), Parallel(ActorInterval(suit, 'quick-jump', startTime=.5, endTime=1.0),
                                                                                                       Sequence(Wait(.25), LerpPosInterval(suit, 0.5, Point3(0, 0, 10), other=suit))), Wait(1.5),
                                 LerpPosInterval(suit, 0.25, Point3(0, 0, 0), other=targetSuit), ActorInterval(suit, 'quick-jump', startTime=4.5), 
                                 Func(suit.setNeutralAnimationDrop), Func(suit.setPos, targetSuit, Point3(0, 0, 0)), Wait(0.5), suitAnimTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack2 = getSoundTrack('SA_castling.ogg', delay=2.0)
    soundTrack4 = getSoundTrack('SA_gains_from_the_scrap2.ogg')
    return Parallel(suitTrack, soundTrack2, soundTrack4, selfDamageTrack, targetSuitAnimTrack, moveTrack)

def doProfiteeringOLD(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[dmg]
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    targetSuitAnimTrack = Sequence(Wait(2.0), ActorInterval(targetSuit, 'drop-react'), Func(targetSuit.setNeutralAnimationDrop))
    selfDamageTrack = Sequence(Wait(2.0), Func(targetSuit.checkProfiteering, suit, battle), targetSuit.makeProfiteeringInterval(suit, battle))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=2.0)
    return Parallel(suitTrack, selfDamageTrack, soundTrack2)

def doExtortion(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    partTracks = Parallel()
    partTracks4 = Parallel()
    toonAnimTracks = Parallel()
    suitTrack = Sequence(getSuitAnimTrack(attack))
    selfDamageTracks = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sprayEffect2 = BattleParticles.createParticleEffect('DemotionSprayExtortion')
        BattleParticles.setEffectTexture(sprayEffect2, 'dollar-sign')
        facePoint = __toonFacePoint(toon)
        partTrack4 = getPartTrack(sprayEffect2, 4, 2.0, [sprayEffect2, toon, 0], softStop=-1)
        partTracks4.append(partTrack4)
        toonAnimTrack = Sequence(Wait(4), ActorInterval(toon, 'slip-forward', playRate=.675))
        toonAnimTracks.append(toonAnimTrack)
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
    toonTrack = getToonTracks(attack, 4, ['nothing'], 0, ['neutral'])
    multiTrackList = Parallel(suitTrack, toonTrack, toonAnimTracks, selfDamageTracks, partTracks4)
    soundTrack = getSoundTrack('SA_gains_from_the_scrap.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_life_insurance_register.ogg', delay=4, node=suit)
    multiTrackList.append(soundTrack)
    multiTrackList.append(soundTrack2)
    return multiTrackList

def doProtectionPayout(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    sprayEffects = [BattleParticles.createParticleEffect(file='spinSpray') for t in targets]
    suitTrack = Sequence(Wait(1.0), getSuitAnimTrack(attack))
    sprayTracks = getPartTracks(attack, sprayEffects, 1.0, 1.9, 0)
    spinTracks1 = Parallel()
    spinTracks2 = Parallel()
    spinTracks3 = Parallel()
    partTracks4 = Parallel()
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
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sprayEffect2 = BattleParticles.createParticleEffect('DemotionSprayExtortion')
        BattleParticles.setEffectTexture(sprayEffect2, 'dollar-sign')
        facePoint = __toonFacePoint(toon)
        partTrack4 = getPartTrack(sprayEffect2, 2.0, 4.0, [sprayEffect2, toon, 0], softStop=-1)
        partTracks4.append(partTrack4)
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
        notifyTrack = Sequence(Wait(3.0), Func(toon.showHpTextNew, -int(dmg)))
        if dmg > 0:
            spinTracks1.append(getPartTrack(spinEffect1, 0, 7.9, [spinEffect1, battle, 0], softStop=-2))
            spinTracks2.append(getPartTrack(spinEffect2, 0, 7.9, [spinEffect2, battle, 0], softStop=-2))
            spinTracks3.append(getPartTrack(spinEffect3, 0, 7.9, [spinEffect3, battle, 0], softStop=-2))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=0))
            soundTracks.append(getSoundTrack('SA_life_insurance_register.ogg', delay=0))
            soundTracks.append(getSoundTrack('ttr_s_ene_bat_embezzle.ogg', delay=2.0, node=suit))
            notifyTracks.append(notifyTrack)
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=0, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['neutral'], showDamageExtraTime=3.0)
    return Parallel(toonTracks, toonSpinTracks, partTracks4, suitTrack, toonDamageTrack, spinTracks1, spinTracks2, spinTracks3, notifyTracks, soundTracks)

def __makeBudgetNodePath():
    tn = TextNode('BUDGET CUTS')
    tn.setFont(getSuitFont())
    tn.setText('CONTINGENCY\nCLAUSE\nCOMPLIANCE')
    tn.setAlign(TextNode.ACenter)
    tntop = hidden.attachNewNode('CancelledTop')
    tnpath = tntop.attachNewNode(tn)
    tnpath.setPosHpr(0, 0, 0, 90, 0, 0)
    tnpath.setScale(1)
    tnpath.setColor(0.7, 0, 0, 1)
    tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
    tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
    tnpath.setScale(1)
    return tntop

def doMandatoryCompliance(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'rubber-stamp'), Func(suit.setNeutralAnimationDrop))
    toonTracks = Parallel()
    notifyTracks = Parallel()
    propTracks = Parallel()
    pad = globalPropPool.getProp('cc_m_prp_bat_rubberStamp_pad')
    stamp = globalPropPool.getProp('cc_m_prp_bat_rubberStamp')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        padPosPoints = [Point3(-0.75, 0.1, -0.125), VBase3(90, 0, 180)]
    if suitType == 'b':
        padPosPoints = [Point3(-0.75, 0, -0.125), VBase3(90, 0, 180)]
    if suitType == 'c':
        padPosPoints = [Point3(-0.25, 0.25, -0.125), VBase3(90, 0, 180)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 1e-06, 3.2)
    stampPosPoints = [Point3(-0.08219178082191902, -0.7397260273972606, -0.125), VBase3(90, 0, 90)]
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        cancelled = __makeBudgetNodePath()
        missPoint = lambda cancelled = cancelled, toon = toon: __toonMissPoint(cancelled, toon)
        propTrack = Sequence(Func(__showProp, stamp, suit.getRightHand(), stampPosPoints[0], stampPosPoints[1]), LerpScaleInterval(stamp, 0.5, Point3(1.2, 1.2, 1.2)), Wait(2.6), Func(battle.movie.needRestoreRenderProp, cancelled), Func(cancelled.reparentTo, render), Func(cancelled.setScale, 0.6), Func(cancelled.setPosHpr, stamp, 0.81, -1.11, -0.16, 0, 0, 90), Func(cancelled.setP, 0), Func(cancelled.setR, 0))
        propTrack.append(getPropThrowTrack(attack, cancelled, [__toonFacePoint(toon)], [__toonFacePoint(toon)]))
        propTrack.append(Func(cancelled.removeNode))
        propTrack.append(Wait(0.3))
        propTrack.append(LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(stamp.removeNode))
        toonTrack = Parallel(getToonTrackCheat(attack, 3.25, ['conked'], 3.1, ['conked']))
        toonTrack.append(Sequence(Wait(3.25), ActorInterval(toon, 'conked')))
        toonTrack2 = Parallel(Func(toon.makeGagBan))
        toonTracks.append(toonTrack2)
        notifyTrack = Sequence(Wait(3.25))
        propTracks.append(propTrack)
        toonTracks.append(toonTrack)
        notifyTracks.append(notifyTrack)
    soundTrack = getSoundTrack('SA_rubber_stamp.ogg', delay=0.5, node=suit)
    #soundTrack2 = getSoundTrack('SA_rubber_stamp.ogg', delay=3.25, node=suit)
    return Parallel(suitTrack, toonTracks, suitTrack2, notifyTracks, propTracks, padPropTrack, soundTrack)



def doHustling(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(3.0))
    soundTrack = getSoundTrack('SA_rush_job_target.ogg', node=suit)
    return Parallel(suitTrack, soundTrack)

def doCustomerRetention(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks2 = Parallel(Wait(5.0))
    screen = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_marketResearch')
    screenPosPoints = [Point3(0, 0, 30), MovieUtil.PNT3_ZERO]
    screenTrack = Sequence()
    screenTrack.append(
            getPropAppearTrack(screen, battle, screenPosPoints, 0, Point3(3, 3, 3), scaleUpTime=0))
    screenTrack.append(LerpPosInterval(screen, 1.0, Point3(0, 0, 5)))
    screenTrack.append(Wait(3.0))
    screenTrack.append(LerpPosInterval(screen, 1.0, Point3(0, 0, 30)))
    screenTrack.append(Func(screen.removeNode))
    suitTracks = Sequence(Parallel(
    getSuitAnimTrack(attack)))
    healSound = SoundInterval(globalBattleSoundCache.getSound('TL_presentation.ogg'))
    for suit in battle.activeSuits:
        suitTrack = Parallel()
        suitTrack.append(Parallel(Func(suit.checkCompensation)))
        suitTrack.append(healSound)
        suitTracks2.append(suitTrack)
    return Parallel(suitTracks, screenTrack, suitTracks2)


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

def doRadioInfrequency(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    headTracks = Sequence()
    for headPart in suit.animatedHeadParts:
        headTracks.append(ActorInterval(headPart, 'death', startTime=headPart.getDuration('death') - 1.5))
        headTracks.append(Wait(4.0))
        headTracks.append(ActorInterval(headPart, 'death', startTime=headPart.getDuration('death'), endTime=headPart.getDuration('death') - 1.5))
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(1.5))
    targets = attack['target']
    makeDamageDowns = Parallel()
    for t in targets:
        toon = t['toon']
        makeDamageDown = Parallel(Func(toon.setToonStatusEffect, 'groupDamageDown', modifier=50, turns=3))
        makeDamageDowns.append(makeDamageDown)
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    suitTrack = Sequence(ActorInterval(suit, 'glower', duration=1.5), Wait(4.0),
                         ActorInterval(suit, 'glower', startTime=1.5), Func(suit.setNeutralAnimation))
    suitTrack2 = getSuitAnimTrack(attack)
    soundTrack = getSoundTrack('mus_dialup_0.ogg', delay=1.5)
    return Parallel(suitTrack, headTracks, makeDamageDowns, soundTrack, suitTrack2, sprayTrack)

def doDanceSession(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    makeDanceSession = Parallel(Func(suit.makeDamageDown), Func(suit.checkDamageDown, + 30), Func(suit.makeDanceSession))
    makeImmune = Parallel(Func(suit.makeDamageReduction), Func(suit.checkDamageReduction, + 30))
    suitTrack = getSuitAnimTrackAttack(attack)
    toonTracks = getToonTracks(attack, 4.1, ['victory'], 4.1, ['victory'])
    soundTrack = getSoundTrack('AA_heal_happydance.ogg', delay=.01, node=suit)
    return Parallel(suitTrack, soundTrack, toonTracks)

def doHotTake(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(2.25))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
    explosionTrack2 = Sequence()
    explosionTrack2.append(Wait(2.25))
    explosionTrack2.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint2, scale=3))
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
    dmg = target[0]['hp']
    tnt = globalPropPool.getProp('tnt')
    tip = tnt.find('**/joint_attachEmitter')
    sparks = BattleParticles.createParticleEffect(file='tnt')
    tnt.sparksEffect = sparks
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.4109589, -0.0821917, -0.0821917), VBase3(-10.849315, 0, 113.42465753424653)]
    propTrack = Sequence(getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.25, Point3(0.7, 0.7, 0.7), scaleUpTime=0.25))
    propTrack.append(Func(sparks.start, tip))
    propTrack.append(Wait(1.5))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
    toonTrack = getToonTrackCheat(attack, 2.25, ['slip-forward'], 0.5, ['jump'])
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.25)
    notifyTrack = Sequence(Wait(2.25), Func(toon.showHpTextNew, -int(dmg), text="BOMBED!", colorCode=3))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'bombed', modifier=50, turns=3)))
    return Parallel(explodeTracks, suitTrack, toonTrack, notifyTrack, soundTrack, propTrack, explosionTrack, explosionTrack2)

def doHotTakeDamage(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    explodeTracks2 = Parallel()
    toonTracks = Parallel()
    notifyTracks = Parallel()
    soundTracks = Parallel()
    explosionTracks = Parallel()
    explosionTrack2s = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        explosionTrack = Sequence()
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
        explosionTrack2 = Sequence()
        explosionTrack2.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint2, scale=3))
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
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
            explodeTrack.append(
                getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
            explodeTracks.append(explodeTrack)
        soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
        notifyTrack = Sequence(Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=3))
        notifyTrack.append(Parallel(Func(toon.clearToonStatusEffect, 'bombed')))
        notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'bombed2', modifier=50, turns=2), Func(toon.setToonStatusEffect, 'bombedDamage', modifier=50, turns=2)))
        notifyTrack.append(Wait(5.0))
        if dmg > 0:
            soundTracks.append(soundTrack)
            explodeTracks2.append(explodeTracks)
            explosionTrack2.append(explosionTrack)
            explosionTrack2s.append(explosionTrack2)
            notifyTracks.append(notifyTrack)
    toonTrack = getToonTracksCheat(attack, 0, ['conked'], 0, ['jump'])
    return Parallel(explodeTracks2, toonTrack, notifyTracks, soundTracks, explosionTracks, explosionTrack2s)

def __createSuitResetPosTrackOvermodulated(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), Func(suit.setNeutralAnimationAttack))
    moveTrack = LerpPosInterval(suit, 0.6, resetPos, other=battle, blendType='easeOut')
    return Parallel(walkTrack, moveTrack)

def doOvermodulated(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']

    if not target:
        return Sequence()

    targetSuit = target[0]['suit']

    origPos, origHpr = battle.getActorPosHpr(suit)
    origPos2 = suit.getPos(battle)

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

    moveTrack = Sequence(
        Parallel(LerpHprInterval(
        suit,
        1.5,
        targetHpr,
        startHpr=origHpr,
        other=battle
    ),
            LerpPosInterval(
            suit,
            1.5,
            walkOutPos,
            startPos=origPos,
            other=battle
        )),
        Wait(suit.getDuration('sanction')),
        Parallel(LerpHprInterval(
            suit,
            1.5,
            origHpr,
            startHpr=targetHpr,
            other=battle
        ),
            LerpPosInterval(
            suit,
            1.5,
            origPos,
            startPos=walkOutPos,
            other=battle
        )),
        Func(suit.setPos, battle, origPos),
        Func(suit.setHpr, battle, origHpr)
    )

    suitTrack = Sequence(
        ActorInterval(suit, 'walk', duration=1.5),
        Parallel(getSuitAnimTrack(attack)),
        ActorInterval(suit, 'walk', duration=1.5),
        Func(suit.setNeutralAnimationDrop)
    )

    selfDamageTrack = Sequence(
        Wait((1.5) + 0.5),
        Parallel(
            ActorInterval(targetSuit, 'pie-large-lured'),
            Func(battle.unlureSuit, targetSuit),
            Func(targetSuit.setDizzy, 0),
            __createSuitResetPosTrackOvermodulated(targetSuit, battle),
            Func(targetSuit.clearSuitStatusEffect, 'lured'),
            Func(targetSuit.showHpString, "+1 ATTACK!"),
            Func(targetSuit.setSuitStatusEffect, 'extraAttacks', modifier=1, mode='refreshModifier')
        ),
        Func(targetSuit.setNeutralAnimationDrop)
    )

    soundTrack = getSoundTrack('SA_haymaker.ogg', delay=(1.5) + 0.5)
    soundTrack1 = getSoundTrack('SA_sanction.ogg', delay=(1.5), node=suit)

    return Parallel(suitTrack, moveTrack, selfDamageTrack, soundTrack, soundTrack1)

hitSoundFiles = ('AA_tart_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_wholepie_only.ogg', 'AA_wholepie_only.ogg')

def __showProp2(prop, parent, pos):
    prop.reparentTo(parent)
    prop.setPos(pos)

def __billboardProp(prop):
    scale = prop.getScale()
    prop.setBillboardPointWorld()
    prop.setScale(scale)

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
        return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, battle, oldPos + (0, 0, evilToon.getHeight())), dustCloud.track, Func(dustCloud.destroy),
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
    sprayEffect = BattleParticles.createParticleEffect('FireSprayPromotion')
    sprayEffect2 = BattleParticles.createParticleEffect('FireSprayPromotion')
    sprayEffect2.setPos(oldPos)
    partTrack4 = getPartTrack(sprayEffect, 2.0, 3.0, [sprayEffect2, battle, 0], softStop=-1)

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
        splatHide = Func(splat.removeNode)
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
    notifyTrack = Sequence(Wait(tPieHitsSuit), Func(toon.showHpTextNew,  - int(hp), "CONTAMINATED!", colorCode=1))
    notifyTrack.append(Func(toon.setToonStatusEffect, 'contaminated', turns=2))
    toonTrack = getToonTrackCheat(attack, tPieHitsSuit, ['slip-backward'], tSuitDodges, ['sidestep'])
    soundTrack2 = getSoundTrack('SA_hot_air.ogg', delay=2.0, node=suit)
    return Sequence(Parallel(suitTrack, soundTrack2, partTrack4), Parallel(evilToonTrack, soundTrack, pieTrack, notifyTrack, toonTrack), moveUp)

def doMandatoryOvertime(attack):
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
    suitTrack = Sequence(getSuitTrack(attack))
    notifyTracks = Parallel()
    BattleParticles.loadParticles()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        cloud = globalPropPool.getProp('stormcloud')
        rainEffect = BattleParticles.createParticleEffect(file='paperRainfall')
        rainEffect2 = BattleParticles.createParticleEffect(file='paperRainfall')
        rainEffect3 = BattleParticles.createParticleEffect(file='paperRainfall')
        initialCloudHeight = suit.height + 30
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Wait(0.6))
        cloudPropTrack.append(Parallel(
            Sequence(ParticleInterval(rainEffect, toon, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect2, toon, worldRelative=0, duration=4.0, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect3, toon, worldRelative=0, duration=4.0, cleanup=True, softStopT=-1))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTracks.append(cloudPropTrack)
    soundTrack1 = getSoundTrack('LB_boss_paper_spin.ogg', delay=1.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    damageAnims = [['cringe',
                    0.01,
                    0.4,
                    0.8], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims,
                                    dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, cloudPropTracks, notifyTracks, soundTrack)

