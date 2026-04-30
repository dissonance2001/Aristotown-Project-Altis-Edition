from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
from direct.showutil import Effects
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


def doPayrollProcessing(attack):
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
        suitTrack.append(Func(suit.checkPayrollProcessing))
        suitTracks.append(suitTrack)
        if not suit.dna.name == 'payman':
            suitTrack.append(Parallel(healSound, Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                           CFSpeech | CFTimeout)))
        suitTracks.append(Sequence(getSuitAnimTrack(attack, playRate=1.5)))
        suitTracks.append(Wait(6.5))
    posPoints = [Point3(-0.3468208092485554, -0.5202312138728331, -0.08670520231213885), VBase3(-7.814761215629517, -177.91907514450867, -188.3236994219653)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = globalPropPool.getProp('bounced-check')
        texture = loader.loadTexture('phase_5/maps/battle/ttcc_suitprops_palette_1_alt.png')
        knife.setTexture(texture, 1)
        knifeTrack = Sequence(
            getPropAppearTrack(
                knife,
                theSuit.getRightHand(),
                posPoints,
                0.5,
                VBase3(8.5, 8.5, 8.5),
                scaleUpTime=0.5
            ),
            Wait(.95),

            Parallel(
                getThrowTrack(knife, (0, 0, suit.getHeight() + 2.5), 1.5, suit, -30.288),
                LerpHprInterval(knife, 1.0, VBase3(0, -90, 0))
            ),

            Wait(0.15),

            Parallel(
                LerpPosInterval(knife, 0.45, (0, 0, suit.getHeight() - 2.5), other=suit, blendType='easeIn'),
                LerpScaleInterval(knife, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
            ),

            Parallel(
                LerpScaleInterval(knife, 0.2, VBase3(0.01, 0.01, 0.01)),
                LerpColorScaleInterval(knife, 0.2, Vec4(1, 1, 1, 0))
            ),

            Func(knife.removeNode)
        )
        knifeTracks.append(knifeTrack)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4)
    return Parallel(suitTracks, soundTrack2, liftTracks, soundTrack, knifeTracks)

def doPerformanceBonus(attack):
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
        if not suit.getManager():
            liftTracks.append(getPartTrack(liftEffect, 4, 4.0, [liftEffect, battle, 0], softStop=-1))
        suitTrack = Sequence()
        suitTrack.append(Wait(4))
        suitTrack.append(Func(suit.checkPerformanceBonus))
        suitTracks.append(suitTrack)
        if not suit.getManager():
            suitTrack.append(Parallel(healSound, Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                           CFSpeech | CFTimeout)))
        suitTracks.append(Sequence(getSuitAnimTrack(attack, playRate=1.5)))
        suitTracks.append(Wait(6.5))
    posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = globalPropPool.getProp('shredder-paper')
        knifeTrack = Sequence(
            getPropAppearTrack(
                knife,
                theSuit.getRightHand(),
                posPoints,
                0.5,
                VBase3(1.2, 1.2, 1.2),
                scaleUpTime=0.5
            ),
            Wait(.95),

            Parallel(
                getThrowTrack(knife, (0, 0, suit.getHeight() + 2.5), 1.5, suit, -20.288),
                LerpHprInterval(knife, 1.0, VBase3(0, -20, -20))
            ),

            Wait(0.15),

            Parallel(
                LerpPosInterval(knife, 0.45, (0, 0, suit.getHeight() - 2.5), other=suit, blendType='easeIn'),
                LerpScaleInterval(knife, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
            ),

            Parallel(
                LerpScaleInterval(knife, 0.2, VBase3(0.01, 0.01, 0.01)),
                LerpColorScaleInterval(knife, 0.2, Vec4(1, 1, 1, 0))
            ),

            Func(knife.removeNode)
        )
        if not suit.getManager():
            knifeTracks.append(knifeTrack)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4)
    return Parallel(suitTracks, soundTrack2, liftTracks, soundTrack, knifeTracks)
