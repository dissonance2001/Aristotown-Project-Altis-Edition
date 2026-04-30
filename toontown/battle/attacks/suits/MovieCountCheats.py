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

def __soakRemoval(suit, remove=0):
    if remove:
        if suit.style.name == 'hydra':
            color = Point4((0.729, 0.729, 0.729, 1))
        elif suit.style.name == 'charon':
            color = Point4((0.51, 0.49, 0.467, 1))
        elif suit.style.name == 'nix':
            color = Point4((0.6, 0.6, 0.6, 1))
        elif suit.style.name == 'styx':
            color = Point4((0.671, 0.671, 0.671, 1))
        elif suit.style.name == 'kerberos':
            color = Point4((0.62, 0.659, 0.624, 1))
        else:
            color = Point4(1.0, 1.0, 1.0, 1.0)
    else:
        color = SoakColor
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit.find('**/body'), suit.find('**/hands')]
    suitInterval = Sequence()
    if suit.dna.name == 'lgator' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryLitigator))
    for bodyPart in suitBody:
        if bodyPart:
            suitInterval.append(Func(bodyPart.setColor, color))
        return suitInterval

def doHydrationCheck(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    posPoints = [Point3(-.25, 0, -.5), VBase3(0, 0, 0)]
    propTracks = Parallel()
    toonPosTracks = Parallel()
    toonTracks = Parallel()
    toonTracks2 = getToonTracksCheat(attack, 2.3, ['slip-backward'], 2.3, ['nothing'])
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        origPos, origHpr = battle.getActorPosHpr(toon)
        x = origPos.getX()
        y = origPos.getY()
        z = origPos.getZ()
        risePoint = Point3(x, y, z - 50)
        toonPosTrack = Sequence(Wait(2.3), Parallel(ActorInterval(toon, 'slip-backward'), LerpPosHprInterval(toon, 0.5, risePoint, VBase3(360, 0, 0))), Func(toon.hide))
        paper = globalPropPool.getProp('glass')
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
        propTrack.append(Wait(1.3))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.5, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle, target=t))
        soundTrack = getSoundTrack('AA_sound_Opera_Singer_Cog_Glass.ogg', node=suit)
        if dmg > 0:
            toonTrack = Sequence(
                Wait(2.3),
            Func(toon.showHpTextCheat, -dmg, openEnded=0), Func(toon.showHpString, "HYDRATED!"))
            toonTracks.append(toonTrack)
            propTrack.append(Parallel(soundTrack))
            toonPosTracks.append(toonPosTrack)
        propTracks.append(propTrack)
        if dmg == 0:
            glass = globalPropPool.getProp('glass')
            hands = toon.getRightHands()
            hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
            hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
            glassTrack = Sequence(Func(MovieUtil.showProp, glass, hand_jointpath0), Parallel(Func(toon.showHpTextCheat, +36, openEnded=0), Func(toon.showHpString, "HYDRATED!"), ActorInterval(toon, 'spit'), ActorInterval(glass, 'glass')), Func(hand_jointpath1.removeNode), Func(hand_jointpath0.removeNode),
                                  Func(MovieUtil.removeProp, glass))
            toonPosTracks.append(glassTrack)

    return Parallel(suitTrack, toonPosTracks, toonTracks, toonTracks2, propTracks)
