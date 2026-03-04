from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
import random
from toontown.battle.BattleBase import *
import PlayByPlayText
import math
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
from toontown.suit import Suit
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from toontown.suit.SuitDNA import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownGlobals import *

notify = DirectNotifyGlobal.directNotify.newCategory('MovieSuitAttacks')

def __doDamage(toon, dmg, died):
    if dmg > 0 and toon.hp != None:
        toon.takeDamage(dmg)

def __doDamageCheat(toon, dmg, died):
    if dmg > 0 and toon.hp != None:
        toon.takeDamageCheat(dmg)

def __showProp(prop, parent, pos, hpr = None, scale = None):
    prop.reparentTo(parent)
    prop.setPos(pos)
    if hpr:
        prop.setHpr(hpr)
    if scale:
        prop.setScale(scale)

def __animProp(prop, propName, propType = 'actor'):
    if 'actor' == propType:
        prop.play(propName)
    elif 'model' == propType:
        pass
    else:
        self.notify.error('No such propType as: %s' % propType)

def __suitFacePoint(suit, zOffset = 0):
    pnt = suit.getPos()
    pnt.setZ(pnt[2] + suit.shoulderHeight + 0.3 + zOffset)
    return Point3(pnt)


def __toonFacePoint(toon, zOffset = 0, parent = render):
    pnt = toon.getPos(parent)
    pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3 + zOffset)
    return Point3(pnt)


def __toonTorsoPoint(toon, zOffset = 0):
    pnt = toon.getPos()
    pnt.setZ(pnt[2] + toon.shoulderHeight - 0.2)
    return Point3(pnt)


def __toonGroundPoint(attack, toon, zOffset = 0, parent = render):
    pnt = toon.getPos(parent)
    battle = attack['battle']
    pnt.setZ(battle.getZ(parent) + zOffset)
    return Point3(pnt)


def __toonGroundMissPoint(attack, prop, toon, zOffset = 0):
    point = __toonMissPoint(prop, toon)
    battle = attack['battle']
    point.setZ(battle.getZ() + zOffset)
    return Point3(point)


def __toonMissPoint(prop, toon, yOffset = 0, parent = None):
    if parent:
        p = __toonFacePoint(toon) - prop.getPos(parent)
    else:
        p = __toonFacePoint(toon) - prop.getPos()
    v = Vec3(p)
    baseDistance = v.length()
    v.normalize()
    if parent:
        endPos = prop.getPos(parent) + v * (baseDistance + 10 + yOffset)
    else:
        endPos = prop.getPos() + v * (baseDistance + 10 + yOffset)
    return Point3(endPos)


def __toonMissBehindPoint(toon, parent = render, offset = 0):
    point = toon.getPos(parent)
    point.setY(point.getY() - 5 + offset)
    return point


def __throwBounceHitPoint(prop, toon):
    startPoint = prop.getPos()
    endPoint = __toonFacePoint(toon)
    return __throwBouncePoint(startPoint, endPoint)


def __throwBounceMissPoint(prop, toon):
    startPoint = prop.getPos()
    endPoint = __toonFacePoint(toon)
    return __throwBouncePoint(startPoint, endPoint)


def __throwBouncePoint(startPoint, endPoint):
    midPoint = startPoint + (endPoint - startPoint) / 2.0
    midPoint.setZ(0)
    return Point3(midPoint)


def getResetTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    updateTrack = Parallel(Func(suit.setChatAbsolute,
                                '',
                                CFSpeech | CFTimeout))
    unluredTrack = Func(battle.unlureSuit, suit)
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05), (Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, updateTrack, walkTrack, moveTrack)


def __makeCancelledNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText(TTLocalizer.MovieSuitCancelled)
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


def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    neutralTrack =  Func(suit.setNeutralAnimation)
    unluredTrack = Func(battle.unlureSuit, suit)
    updateTrack = Parallel(Func(suit.setChatAbsolute,
                                '',
                                CFSpeech | CFTimeout))
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), neutralTrack)
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, updateTrack, walkTrack, moveTrack)

def getSuitTrack(attack, delay = 1e-06, splicedAnims = None, playRate = 1.0):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target[0]['toon']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
    origH = suit.getH(battle)

    # Calculate heading to toon
    targetPos = toon.getPos(battle)
    suit.headsUp(battle, targetPos)
    targetH = suit.getH(battle)

    # Restore original heading
    suit.setH(battle, origH)

    # Normalize difference to shortest path
    delta = (targetH - origH + 180) % 360 - 180

    if attack[
        'suitName'] == 'bkeeper':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    track.append(Sequence(
        LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle)))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        if attack['suitName'] == 'hho' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:
            track.append(ActorInterval(suit, 'headhoncho-cigar-smoke', playRate=playRate))
        elif attack['suitName'] == 'fires' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:
            track.append(ActorInterval(suit, 'firestarter-cigar-smoke', playRate=playRate))
        elif attack['suitName'] == 'safesupervis' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:
            track.append(ActorInterval(suit, 'firestarter-cigar-smoke', playRate=playRate))
        else:
            track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
    if delta > 0:
        shuffleAnim = 'shuffle-right'
    else:
        shuffleAnim = 'shuffle-left'
    track.append(Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle))
    )
    track.append(
        Func(suit.setNeutralAnimationDrop))
    return track


def getSuitAnimTrack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    suit = attack['suit']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
    if attack[
        'suitName'] == 'bkeeper':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
        # if suit.dna.name == 'scg' and suit.isAngry:
        #     track.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        #     track.append(Func(suit.loop, 'neutral-enraged'))
        # elif suit.isImmortal and suit.dna.name == 'dsf':
        #     track.append(
        #        Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        # elif suit.isVulnerable and suit.dna.name == 'crf':
        #    track.append(
        #       Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        # elif suit.isImmortal:
        #    track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        #  track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    track.append(
            Func(suit.setNeutralAnimationDrop))
    return track


def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))


def getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative = 1, softStop = 0):
    '''
    Author: Professor Control
    '''
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    partTracks = Parallel()
    origHpr = battle.getActorPosHpr(suit)[1]
    for i in xrange(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        origHpr = battle.getActorPosHpr(suit)[1] # We only want the rotation.
        particleEffects[i].reparentTo(suit) # Reparent the particle effect to the Cog.
        suit.headsUp(battle, toon.getPos(battle)) # Briefly turn the Cog to the Toon.
        particleEffects[i].wrtReparentTo(battle) # Drop the particle effect.
        partTracks.append(getPartTrack(particleEffects[i], startDelay, durationDelay, [particleEffects[i], battle, worldRelative], softStop))

    suit.setHpr(battle, origHpr) # After all that, set the Cog back like nothing ever happened.
    return partTracks


def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    battle = attack['battle']
    suit = attack['suit']
    if suit:
        suitPos = suit.getPos(battle)
    toonPos = toon.getPos(battle)
    indicator = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
    indicator.setHpr(0, -90, 0)
    indicator.setPos(toonPos.getX(), toonPos.getY(), .05)
    dmg = target['hp']
    animTrack = Sequence()
    if suit:
        animTrack.append(Func(toon.headsUp, battle, suitPos))
    indicatorTracks = Sequence(Func(indicator.reparentTo, battle), LerpScaleInterval(indicator, 0, Point3(4, 1, 4)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                               Func(indicator.reparentTo, hidden), Func(indicator.clearColorScale),
                               Func(indicator.removeNode))
    if dmg > 0:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
        #indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return Parallel(animTrack, indicatorTracks)


def getToonTracks(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    toonTracks = Parallel()
    targets = attack['target']
    for i in xrange(len(targets)):
        tgt = targets[i]
        toonTracks.append(getToonTrack(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target=tgt, showDamageExtraTime=showDamageExtraTime, showMissedExtraTime=showMissedExtraTime))

    return toonTracks


def getToonTrackCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    battle = attack['battle']
    suit = attack['suit']
    name = attack['name']
    if suit:
        suitPos = suit.getPos(battle)
    toonPos = toon.getPos(battle)
    indicator = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
    indicator.setHpr(0, -90, 0)
    indicator.setPos(toonPos.getX(), toonPos.getY(), .05)
    dmg = target['hp']
    animTrack = Sequence()
    animTrack.append(Func(toon.headsUp, battle, suitPos))
    indicatorTracks = Sequence(Func(indicator.reparentTo, battle), LerpScaleInterval(indicator, 0, Point3(4, 1, 4)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                               Func(indicator.reparentTo, hidden), Func(indicator.clearColorScale),
                               Func(indicator.removeNode))
    if dmg > 0:
        animTrack.append(getToonTakeDamageTrackCheat(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
        #indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return animTrack


def getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    toon = target['toon']
    toonTrack = Sequence()
    # toonTrack.append(Wait(dodgeDelay))
    # if dodgeAnimNames:
    # for d in dodgeAnimNames:
    #  if d == 'sidestep':
    #    toonTrack.append(getAllyToonsDodgeParallel(target))
    #  else:
    #  toonTrack.append(ActorInterval(toon, d))

    #  else:
    #  toonTrack.append(getSplicedAnimsTrack(splicedDodgeAnims, actor=toon))
    toonTrack.append(Func(toon.loop, 'neutral'))
    return toonTrack


def getToonTracksCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    toonTracks = Parallel()
    targets = attack['target']
    for i in xrange(len(targets)):
        tgt = targets[i]
        toonTracks.append(getToonTrackCheat(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target=tgt, showDamageExtraTime=showDamageExtraTime, showMissedExtraTime=showMissedExtraTime))

    return toonTracks


def getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    toon = target['toon']
    toonTrack = Sequence()
    toonTrack.append(Wait(dodgeDelay))
    if dodgeAnimNames:
        for d in dodgeAnimNames:
            if d == 'sidestep':
                toonTrack.append(getAllyToonsDodgeParallel(target))
            else:
                toonTrack.append(ActorInterval(toon, d))

    else:
        toonTrack.append(getSplicedAnimsTrack(splicedDodgeAnims, actor=toon))
    toonTrack.append(Func(toon.loop, 'neutral'))
    return toonTrack


def getAllyToonsDodgeParallel(target):
    toon = target['toon']
    leftToons = target['leftToons']
    rightToons = target['rightToons']
    if len(leftToons) > len(rightToons):
        PoLR = rightToons
        PoMR = leftToons
    else:
        PoLR = leftToons
        PoMR = rightToons
    upper = 1 + 4 * abs(len(leftToons) - len(rightToons))
    if random.randint(0, upper) > 0:
        toonDodgeList = PoLR
    else:
        toonDodgeList = PoMR
    if toonDodgeList is leftToons:
        sidestepAnim = 'sidestep-left'
        soundEffect = globalBattleSoundCache.getSound('AV_side_step.ogg')
    else:
        sidestepAnim = 'sidestep-right'
        soundEffect = globalBattleSoundCache.getSound('AV_jump_to_side.ogg')
    toonTracks = Parallel()
    for t in toonDodgeList:
        toonTracks.append(Sequence(ActorInterval(t, sidestepAnim), Func(t.loop, 'neutral')))

    toonTracks.append(Sequence(ActorInterval(toon, sidestepAnim), Func(toon.loop, 'neutral')))
    toonTracks.append(Sequence(Wait(0.5), SoundInterval(soundEffect, node=toon)))
    return toonTracks


def getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5, startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0, animStartTime = 0.0):
    if anim == 1:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), ActorInterval(prop, propName, duration=animDuration, startTime=animStartTime), Wait(remainDelay), Func(MovieUtil.removeProp, prop))
    else:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), Wait(remainDelay), LerpScaleInterval(prop, scaleDownTime, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, prop))
    return track


def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
    if poseExtraArgs:
        propTrack.append(Func(prop.pose, *poseExtraArgs))
    propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale))
    return propTrack


def getPropThrowTrack(attack, prop, hitPoints = [], missPoints = [], hitDuration = 0.25, missDuration = 0.25, hitPointNames = 'none', missPointNames = 'none', lookAt = 'none', groundPointOffSet = 0, missScaleDown = None, parent = render, target = None):
    '''
    target: Similar to what getToonTrack() has, we will use this to take note of a target.  Leave as none so that, by default, only the first targeted Toon gets the object thrown at them.
    '''
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    dmg = target['hp']
    battle = attack['battle']

    def getLambdas(list, prop, toon):
        for i in xrange(len(list)):
            if list[i] == 'face':
                list[i] = lambda toon = toon: __toonFacePoint(toon)
            elif list[i] == 'miss':
                list[i] = lambda prop = prop, toon = toon: __toonMissPoint(prop, toon)
            elif list[i] == 'bounceHit':
                list[i] = lambda prop = prop, toon = toon: __throwBounceHitPoint(prop, toon)
            elif list[i] == 'bounceMiss':
                list[i] = lambda prop = prop, toon = toon: __throwBounceMissPoint(prop, toon)

        return list

    if hitPointNames != 'none':
        hitPoints = getLambdas(hitPointNames, prop, toon)
    if missPointNames != 'none':
        missPoints = getLambdas(missPointNames, prop, toon)
    propTrack = Sequence()
    propTrack.append(Func(battle.movie.needRestoreRenderProp, prop))
    propTrack.append(Func(prop.wrtReparentTo, parent))
    if lookAt != 'none':
        propTrack.append(Func(prop.lookAt, lookAt))
    if dmg > 0:
        for i in xrange(len(hitPoints)):
            pos = hitPoints[i]
            propTrack.append(LerpPosInterval(prop, hitDuration, pos=pos))

    else:
        for i in xrange(len(missPoints)):
            pos = missPoints[i]
            propTrack.append(LerpPosInterval(prop, missDuration, pos=pos))

        if missScaleDown:
            propTrack.append(LerpScaleInterval(prop, missScaleDown, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, prop))
    propTrack.append(Func(battle.movie.clearRenderProp, prop))
    return propTrack


def getThrowTrack(object, target, duration = 1.0, parent = render, gravity = -32.144):
    values = {}

    def calcOriginAndVelocity(object = object, target = target, values = values, duration = duration, parent = parent, gravity = gravity):
        if callable(target):
            target = target()
        object.wrtReparentTo(parent)
        values['origin'] = object.getPos(parent)
        origin = object.getPos(parent)
        values['velocity'] = (target[2] - origin[2] - 0.5 * gravity * duration * duration) / duration

    return Sequence(Func(calcOriginAndVelocity), LerpFunctionInterval(throwPos, fromData=0.0, toData=1.0, duration=duration, extraArgs=[object,
     duration,
     target,
     values,
     gravity]))


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


def getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    toonTrack = Sequence()
    toonTrack.append(Wait(delay))
    suitResponseTrack = Sequence()
    suit = attack['suit']
    if damageAnimNames:
        for d in damageAnimNames:
            toonTrack.append(ActorInterval(toon, d))

        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died), Func(toon.checkCogDeath, suit))
    else:
        splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died), Func(toon.checkCogDeath, suit))
    toonTrack.append(Func(toon.loop, 'neutral'))
    return Parallel(toonTrack, indicatorTrack, suitResponseTrack)


def getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    toonTrack = Sequence()
    toonTrack.append(Wait(delay))
    suitResponseTrack = Sequence()
    suit = attack['suit']
    if damageAnimNames:
        for d in damageAnimNames:
            toonTrack.append(ActorInterval(toon, d))

        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamageCheat, toon, dmg, died), Func(toon.checkCogDeath, suit))
    else:
        splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamageCheat, toon, dmg, died), Func(toon.checkCogDeath, suit))
    toonTrack.append(Func(toon.loop, 'neutral'))
    return Parallel(toonTrack, indicatorTrack, suitResponseTrack)


def getSplicedAnimsTrack(anims, actor = None):
    track = Sequence()
    for nextAnim in anims:
        delay = 1e-06
        if len(nextAnim) >= 2:
            if nextAnim[1] > 0:
                delay = nextAnim[1]
        if len(nextAnim) <= 0:
            track.append(Wait(delay))
        elif len(nextAnim) == 1:
            track.append(ActorInterval(actor, nextAnim[0]))
        elif len(nextAnim) == 2:
            track.append(Wait(delay))
            track.append(ActorInterval(actor, nextAnim[0]))
        elif len(nextAnim) == 3:
            track.append(Wait(delay))
            track.append(ActorInterval(actor, nextAnim[0], startTime=nextAnim[2]))
        elif len(nextAnim) == 4:
            track.append(Wait(delay))
            duration = nextAnim[3]
            if duration < 0:
                startTime = nextAnim[2]
                endTime = startTime + duration
                if endTime <= 0:
                    endTime = 0.01
                track.append(ActorInterval(actor, nextAnim[0], startTime=startTime, endTime=endTime))
            else:
                track.append(ActorInterval(actor, nextAnim[0], startTime=nextAnim[2], duration=duration))
        elif len(nextAnim) == 5:
            track.append(Wait(delay))
            track.append(ActorInterval(nextAnim[4], nextAnim[0], startTime=nextAnim[2], duration=nextAnim[3]))

    return track


def getSplicedLerpAnims(animName, origDuration, newDuration, startTime = 0, fps = 30, reverse = 0):
    anims = []
    addition = 0
    numAnims = origDuration * fps
    timeInterval = newDuration / numAnims
    animInterval = origDuration / numAnims
    if reverse == 1:
        animInterval = -animInterval
    for i in xrange(0, int(numAnims)):
        anims.append([animName,
         timeInterval,
         startTime + addition,
         animInterval])
        addition += animInterval

    return anims


def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    return Sequence(Wait(delay), SoundInterval(globalBattleSoundCache.getSound(fileName), duration=duration, node=node))

def doMandatoryFiling(attack):
    targets = attack['target']
    suit = attack['suit']
    battle = attack['battle']

    bookshelf = globalPropPool.getProp('LB_AttackShelf')

    throwSfx = loader.loadSfx('phase_5/audio/sfx/SA_hardball_impact_only.ogg')
    throwSfx.setVolume(.25)

    def throwBook(attack, targets, bookshelf, throwSfx=None, end=False):
        if end:
            neutralTrack = Parallel()
            notifyTrack = Parallel()
            throwTrack2 = Parallel()
            for toon in targets:
                dmg = toon['hp']
                toon = toon['toon']
                x = -1.5
                book = loader.loadModel('phase_14/models/props/lawbot-book')
                book.setPos(x, 0, 3)
                book.hide()
                book.reparentTo(bookshelf)
                dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
                dustCloud.setBillboardAxis(2.0)
                dustCloud.setZ(3)
                dustCloud.setScale(0.4)
                dustCloud.createTrack()
                dustCloudHideIval = Sequence(Func(dustCloud.reparentTo, toon), Func(dustCloud.setPos,
                                                                                    Point3(toon.getX(), toon.getY() - 6, toon.getZ() + 3)),
                                             dustCloud.track, Func(dustCloud.removeNode), Wait(1.7), name='dustCloadIval')

                x += 1
                throwTrack2.append(
                    Sequence(
                        Parallel(
                            Sequence(Wait(.1), SoundInterval(throwSfx, duration=.6)),
                            Sequence(
                                Wait(.2), Func(book.show), Func(book.wrtReparentTo, render),
                                book.posHprInterval(.5, (toon.getX(), toon.getY(), toon.getZ() + 3), (0, 720, 0))
                            )
                        ),
                        Parallel(dustCloudHideIval, Func(book.removeNode))
                    )
                )
                neutralTrack.append(Func(toon.loop, 'neutral'))
                notifyTrack.append(Sequence(Wait(0.7), Func(toon.showHpTextNew, -int(dmg), text="NO DEFENSE!", colorCode=1)))
            throwTrack = Parallel(
                getToonTracksCheat(attack, .7, ['slip-forward'], 2.75, ['sidestep']), neutralTrack
            )
            return Parallel(throwTrack, notifyTrack, throwTrack2)
        else:
            throwTrack = Parallel()
            throwTrack2 = Parallel()
            x = -1.5
            for toon in targets:
                toon = toon['toon']
                book = loader.loadModel('phase_14/models/props/lawbot-book')
                book.setPos(x, 0, 3)
                book.hide()
                book.reparentTo(bookshelf)
                throwTrack2.append(Sequence(Wait(.7),
                    ActorInterval(toon, 'slip-backward', startTime=.5, playRate=2.0)
                ))

                x += 1
                throwTrack.append(
                    Sequence(
                        Parallel(
                            Sequence(Wait(.1), SoundInterval(throwSfx, duration=.6)),
                            Sequence(
                                Wait(.2), Func(book.show), Func(book.wrtReparentTo, render),
                                book.posHprInterval(.5, (toon.getX(), toon.getY(), toon.getZ() + 3), (0, 720, 0))
                            )
                        ),
                        Func(book.removeNode)
                    )
                )
            return Parallel(throwTrack, throwTrack2)

    suitTrack = Parallel(getSuitAnimTrack(attack), Sequence(Func(bookshelf.setH, bookshelf.getH() + 180), Func(bookshelf.wrtReparentTo, battle),
                         Sequence(
                             Wait(1.0), bookshelf.posInterval(0, (0, -75, 0)), bookshelf.hprInterval(0, (180, 0, 0)), bookshelf.scaleInterval(1.0, (2.0, 2.0, 2.0)), Sequence(
                                 Parallel(throwBook(attack, targets, bookshelf, throwSfx, end=True), ActorInterval(bookshelf, 'LB_AttackShelf')), Sequence(bookshelf.scaleInterval(.5, (.01, .01, .01)))),
                                 Sequence(Func(bookshelf.wrtReparentTo, suit), bookshelf.hprInterval(.5, (180, 0, 0)),

                             ),
                             Parallel(
                                 Sequence(Func(bookshelf.removeNode)),
                             ))))
    soundTrack2 = loader.loadSfx('phase_5/audio/sfx/SA_bash.ogg')
    soundTrack = SoundInterval(soundTrack2)

    return Parallel(suitTrack, soundTrack)

def doPaperCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toonTrack = getToonTracksCheat(attack, .5, ['cringe'], 3.4, ['struggle'])
    partTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect('Shred2')
        targetPos = toon.getPos(battle)
        origPos, origHpr = battle.getActorPosHpr(suit)
        partTrack = getPartTrack(particleEffect, .5, 3.5, [particleEffect, toon, 0], softStop=-2)
        toonTrack = getToonTracksCheat(attack, .5, ['cringe'], 3.4, ['struggle'])
        notifyTrack = Sequence(Wait(.5), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
        if dmg > 0:
            notifyTracks.append(notifyTrack)
            notifyTracks.append(Parallel(Func(toon.makeVulnerable), Func(toon.addVulnerabilityRounds, 2)))
            currentBossHealth = -1
            for s in battle.suits:
                if s.dna.name == 'phouse':
                    currentBossHealth = s.currHP
            if currentBossHealth > 0:
                notifyTracks.append(Parallel(Func(toon.checkVulnerabilityUp, 50)))
            else:
                notifyTracks.append(Parallel(Func(toon.checkVulnerabilityUp, 25)))
            partTracks.append(partTrack)
    suitTrack = Parallel(getSuitTrack(attack))
    soundTrack = getSoundTrack('SA_shred.ogg', delay=.5, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    return Parallel(suitTrack, partTracks, notifyTracks, toonTrack, soundTrack)

def doPaperCutMulti(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toonTrack = getToonTracksCheat(attack, .5, ['cringe'], 3.4, ['struggle'])
    partTracks = Parallel()
    notifyTracks = Parallel()
    moveTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        BattleParticles.loadParticles()
        particleEffect = BattleParticles.createParticleEffect('Shred2')
        targetPos = toon.getPos(battle)
        origPos, origHpr = battle.getActorPosHpr(suit)
        partTrack = getPartTrack(particleEffect, .5, 3.5, [particleEffect, toon, 0], softStop=-2)
        toonTrack = getToonTracksCheat(attack, .5, ['cringe'], 3.4, ['struggle'])
        notifyTrack = Sequence(Wait(.5), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
        if dmg > 0:
            origH = suit.getH(battle)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)
            suit.setH(battle, origH)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            moveTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'sanction'),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)), Func(suit.setNeutralAnimationDrop)))
            notifyTracks.append(notifyTrack)
            notifyTracks.append(Parallel(Func(toon.makeVulnerable), Func(toon.addVulnerabilityRounds, 2)))
            notifyTracks.append(Parallel(Func(toon.checkVulnerabilityUp, 15)))
            partTracks.append(partTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack = getSoundTrack('SA_shred.ogg', delay=.5, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    return Parallel(suitTrack, partTracks, moveTracks, notifyTracks, toonTrack, soundTrack)

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
    notifyTrack = Sequence(Wait(2.25), Func(toon.showHpTextNew, -int(dmg), text="NO DEFENSE!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.makeNoDodge), Func(toon.addNoDodgeRounds, 2)))
    return Parallel(explodeTracks, suitTrack, toonTrack, soundTrack, propTrack, notifyTrack, explosionTrack)

def doBookkeepingRetaliation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    soundTracks = Parallel()
    toonTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        targetPos = toon.getPos(battle)
        origPos, origHpr = battle.getActorPosHpr(suit)
        suitTrack = Sequence(getSuitAnimTrack(attack))
        suitTrack2 = Sequence(ActorInterval(suit, 'effort', duration=3.0), ActorInterval(suit, 'sanction'), Func(suit.setNeutralAnimationDrop))
        notifyTrack = Sequence(Wait(3.4), Func(toon.showHpTextNew, -int(dmg), text="NO GAGS!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.makeHidden), Func(toon.addHiddenRounds, 1)))
        soundTrack1 = Sequence(SoundInterval(globalBattleSoundCache.getSound('suit_promotion_sfx.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(3.4), SoundInterval(globalBattleSoundCache.getSound('SA_haymaker.ogg')))
        soundTrack = Parallel(soundTrack1, soundTrack2)
        if dmg > 0:
            headsUp = Func(suit.headsUp, battle, targetPos)
            soundTracks.append(soundTrack)
            suitTracks.append(suitTrack)
            suitTracks.append(Sequence(Parallel(suitTrack2, headsUp), Func(suit.setHpr, battle, origHpr)))
            notifyTracks.append(notifyTrack)
    damageAnims = [['conked']]
    makeDamageUp = Func(suit.removeBookkeeping)
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=3.4, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                   dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, makeDamageUp, toonDamageTrack, soundTracks, toonTracks, notifyTracks)

def doOilRainHeal(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    puddleTracks = Parallel()
    moveTracks = Parallel()
    cloudPropTracks = Parallel()
    managerHealTracks = Parallel()
    animTracks = Parallel()
    for s in battle.activeSuits:
        currentBossHealth = -1
        if s.dna.name == 'phouse':
            currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            if s.dna.name == 'ambass':
                managerHealTracks.append(Func(s.checkRefinementPowerhouse))
        else:
            if s.dna.name == 'ambass':
                managerHealTracks.append(Func(s.checkRefinement))
        if not s.dna.name == 'ambass':
            BattleParticles.loadParticles()
            cloud = globalPropPool.getProp('stormcloud')
            rainEffect = BattleParticles.createParticleEffect(file='oilRain')
            rainEffect2 = BattleParticles.createParticleEffect(file='oilRain')
            rainEffect3 = BattleParticles.createParticleEffect(file='oilRain')
            rainEffect.setColor(0.259, 0.259, 0.259, 1)
            rainEffect2.setColor(0.259, 0.259, 0.259, 1)
            rainEffect3.setColor(0.259, 0.259, 0.259, 1)
            initialCloudHeight = s.height + 3
            cloudPosPoints = [Point3(0, 0, initialCloudHeight), VBase3(180, 0, 0)]
            cloudPropTrack = Sequence()
            cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
            cloudPropTrack.append(getPropAppearTrack(cloud, s, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
            cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
            cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
            cloudPropTrack.append(Wait(0.6))
            cloudPropTrack.append(Parallel(
                Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)),
                Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
                Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
                Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
            cloudPropTrack.append(Wait(0.4))
            cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
            cloudPropTrack.append(Func(cloud.removeNode))
            cloudPropTracks.append(cloudPropTrack)
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0, 0, 0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle),
                                   Func(puddle.reparentTo, battle), Func(puddle.setPos, s.getPos(battle)),
                                   LerpScaleInterval(puddle, 0.9, Point3(1.7, 1.7, 1.7),
                                                     startScale=MovieUtil.PNT3_NEARZERO), Wait(6.2),
                                   LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8),
                                   Func(puddle.removeNode))
            sinkPos1 = s.getPos(battle)
            sinkPos2 = s.getPos(battle)
            dropPos = s.getPos(battle)
            landPos = s.getPos(battle)
            sinkPos1.setZ(sinkPos1.getZ() - 3.1)
            sinkPos2.setZ(sinkPos2.getZ() - 9.1)
            dropPos.setZ(dropPos.getZ())
            landPos.setY(dropPos.getY())
            if currentBossHealth >= 1:
                moveTrack = Sequence(Wait(1.8), LerpPosInterval(s, 0.9, sinkPos1, other=battle),
                                     LerpPosInterval(s, 0.4, sinkPos2, other=battle),
                                     Func(s.checkRefinementPowerhouse))
            else:
                moveTrack = Sequence(Wait(1.8), LerpPosInterval(s, 0.9, sinkPos1, other=battle),
                                 LerpPosInterval(s, 0.4, sinkPos2, other=battle),
                                 Func(s.checkRefinement))
            animTrack = Sequence(Wait(0.9), ActorInterval(s, 'flail-qs', endTime=1.75),
                                 ActorInterval(s, 'flail-qs', startTime=1.25, endTime=1.75),
                                 ActorInterval(s, 'flail-qs', startTime=1.25, endTime=1.25), Func(s.setPos, battle, dropPos), LerpPosInterval(s, 0, landPos, other=battle),
                                 Func(s.wrtReparentTo, battle), ActorInterval(s, 'reanimated'), Func(s.checkCogLured, battle), Func(s.makeUnLured), Func(battle.unlureSuit, s), Func(s.setDizzy, 0), Func(s.setNeutralAnimation))
            animTracks.append(animTrack)
            moveTracks.append(moveTrack)
            puddleTracks.append(puddleTrack)

    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(.5), ActorInterval(suit, 'summon-cog'), Func(suit.setNeutralAnimation))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    soundTrack4 = getSoundTrack('SA_liquidate.ogg', node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.1, node=suit)
    soundTrack3 = getSoundTrack('SA_zombie_cogs_rising.ogg', delay=suit.getDuration('snap') + .5, node=suit)
    return Parallel(suitTrack, moveTracks, soundTrack4, soundTrack3, soundTrack2, animTracks, managerHealTracks, cloudPropTracks, soundTrack, puddleTracks)

def doOilRainHealManager(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    puddleTracks = Parallel()
    moveTracks = Parallel()
    managerHealTracks = Parallel()
    cloudPropTracks = Parallel()
    animTracks = Parallel()
    for s in battle.activeSuits:
        currentBossHealth = -1
        if s.dna.name == 'phouse':
            currentBossHealth = s.currHP
        if s.getManager() and not s.dna.name == 'ambass':
            BattleParticles.loadParticles()
            cloud = globalPropPool.getProp('stormcloud')
            rainEffect = BattleParticles.createParticleEffect(file='oilRain')
            rainEffect2 = BattleParticles.createParticleEffect(file='oilRain')
            rainEffect3 = BattleParticles.createParticleEffect(file='oilRain')
            rainEffect.setColor(0.259, 0.259, 0.259, 1)
            rainEffect2.setColor(0.259, 0.259, 0.259, 1)
            rainEffect3.setColor(0.259, 0.259, 0.259, 1)
            initialCloudHeight = s.height + 3
            cloudPosPoints = [Point3(0, 0, initialCloudHeight), VBase3(180, 0, 0)]
            cloudPropTrack = Sequence()
            cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
            cloudPropTrack.append(getPropAppearTrack(cloud, s, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
            cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
            cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
            cloudPropTrack.append(Wait(0.6))
            cloudPropTrack.append(Parallel(
                Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)),
                Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
                Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
                Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
            cloudPropTrack.append(Wait(0.4))
            cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
            cloudPropTrack.append(Func(cloud.removeNode))
            cloudPropTracks.append(cloudPropTrack)
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0, 0, 0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle),
                                   Func(puddle.reparentTo, battle), Func(puddle.setPos, s.getPos(battle)),
                                   LerpScaleInterval(puddle, 0.9, Point3(1.7, 1.7, 1.7),
                                                     startScale=MovieUtil.PNT3_NEARZERO), Wait(6.2),
                                   LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8),
                                   Func(puddle.removeNode))
            sinkPos1 = s.getPos(battle)
            sinkPos2 = s.getPos(battle)
            dropPos = s.getPos(battle)
            landPos = s.getPos(battle)
            sinkPos1.setZ(sinkPos1.getZ() - 3.1)
            sinkPos2.setZ(sinkPos2.getZ() - 9.1)
            dropPos.setZ(dropPos.getZ())
            landPos.setY(dropPos.getY())
            if currentBossHealth >= 1:
                moveTrack = Sequence(Wait(1.8), LerpPosInterval(s, 0.9, sinkPos1, other=battle),
                                     LerpPosInterval(s, 0.4, sinkPos2, other=battle),
                                     Func(s.checkRefinementPowerhouseManager))
            else:
                moveTrack = Sequence(Wait(1.8), LerpPosInterval(s, 0.9, sinkPos1, other=battle),
                                     LerpPosInterval(s, 0.4, sinkPos2, other=battle),
                                     Func(s.checkRefinementManager))
            animTrack = Sequence(Wait(0.9), ActorInterval(s, 'flail-qs', endTime=1.75),
                                 ActorInterval(s, 'flail-qs', startTime=1.25, endTime=1.75),
                                 ActorInterval(s, 'flail-qs', startTime=1.25, endTime=1.25), Func(s.setPos, battle, dropPos), LerpPosInterval(s, 0, landPos, other=battle),
                                 Func(s.wrtReparentTo, battle), ActorInterval(s, 'reanimated'), Func(s.checkCogLured, battle), Func(s.makeUnLured), Func(battle.unlureSuit, s), Func(s.setDizzy, 0), Func(s.setNeutralAnimation))
            animTracks.append(animTrack)
            moveTracks.append(moveTrack)
            puddleTracks.append(puddleTrack)

    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(.5), ActorInterval(suit, 'summon-cog'), Func(suit.setNeutralAnimation))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.1, node=suit)
    soundTrack3 = getSoundTrack('SA_zombie_cogs_rising.ogg', delay=suit.getDuration('snap') + .5, node=suit)
    return Parallel(suitTrack, soundTrack3, moveTracks, animTracks, cloudPropTracks, soundTrack2, soundTrack, puddleTracks)


def doCollectCall(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    origH = suit.getH(battle)

    # Calculate heading to toon
    targetPos = toon.getPos(battle)
    suit.headsUp(battle, targetPos)
    targetH = suit.getH(battle)

    # Restore original heading
    suit.setH(battle, origH)

    # Normalize difference to shortest path
    delta = (targetH - origH + 180) % 360 - 180
    if delta > 0:
        shuffleAnim = 'shuffle-right'
    else:
        shuffleAnim = 'shuffle-left'
    headsUp = Func(suit.headsUp, battle, targetPos)
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = Sequence(Parallel(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), getSuitAnimTrack(attack)))
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(4.75))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    cagePropTracks = Parallel()
    explodePosPoints = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 15, 5), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explode = []
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(Wait(4.75))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5.5/models/estate/prop_phone-mod')
    cage2 = loader.loadModel('phase_5.5/models/estate/phoneMount-mod')
    toonPos = toon.getPos(battle)
    toonHpr = battle.getActorPosHpr(toon)
    y = toonPos.getY()
    propPos = Point3(toonPos.getX(), y, 30)
    x = toonPos.getX() - 5
    if dmg == 0:
        x -= 10
    cagePos = [Point3(toonPos.getX(), toonPos.getY() + 7.5, 30.0)]
    cagePos2 = [Point3(toonPos.getX(), toonPos.getY() + 7.5, 30.0)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.0), scaleUpTime=1.0),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), toonPos.getY() + 5, 0.5), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
            Wait(2.0),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTrack2 = Sequence(
        getPropAppearTrack(cage2, battle, cagePos2, 0.01, scaleUpPoint=Point3(1.0), scaleUpTime=1.0),
        Parallel(
            cage2.posInterval(0.75, Point3(toonPos.getX(), toonPos.getY() + 5, 0.5), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/ashfhadh.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/afhdhsdhsd.ogg'), node=cage2),
        Wait(2.0),
        LerpFunctionInterval(cage2.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage2)
    )
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')

    phonePosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Wait(suit.getDuration('snap')), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]),
                         Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24),
                         Func(receiver.wrtReparentTo, suit.getRightHand()),
                         LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)),
                         Wait(1.75), Func(receiver.wrtReparentTo, phone), Wait(0.62),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO),
                         Func(MovieUtil.removeProps, [receiver, phone]))
    cagePropTracks.append(cagePropTrack)
    cagePropTracks.append(cagePropTrack2)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack.append(Sequence(ActorInterval(suit, 'phone', playRate=1.5), Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)), Func(suit.setNeutralAnimationDrop)))
    soundTrack1 = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=1.75, node=suit)
    soundTrack2 = getSoundTrack('SA_bash.ogg', delay=0, node=suit)
    soundTrack3 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=4.75)
    soundTrack4 = getSoundTrack('telephone_ring.ogg', delay=2.0, node=suit)
    soundTrack = Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4)
    toonTrack = Sequence(Wait(1.0), ActorInterval(toon, 'takePhone', duration=3.75))
    toonTrack.append(getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg), 0, ['conked']))
    notifyTrack = Sequence(Wait(4.75), Func(toon.makeCollectCalled), Func(toon.addCollectCallRounds, 1), Func(toon.showHpTextNew, 0, text="CONNECTED!", colorCode=1))
    return Parallel(explodeTracks, suitTrack, cagePropTracks, toonTrack, notifyTrack, soundTrack, explosionTrack, propTrack)

def doAdvancement(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    liftTracks = Parallel()
    suitTrack3 = getSuitAnimTrack(attack)
    suitTrack2 = Sequence(ActorInterval(suit, 'sacrifice-cog', startTime=2.25), Func(suit.setNeutralAnimationDrop))
    for targetSuit in battle.activeSuits:
        suitTrack = Sequence(Wait(1.5), Func(targetSuit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitMarkedPhrases), CFSpeech | CFTimeout), ActorInterval(targetSuit, 'slip-forward'),
                             Func(targetSuit.makeTarget), Func(targetSuit.setNeutralAnimationDrop))
        if not targetSuit.dna.name == 'ambass':
            if not targetSuit.isManager:
                suitTracks.append(suitTrack)
    soundTrack2 = getSoundTrack('ENC_cogjump_to_side2.ogg', delay=1, node=theSuit)
    return Parallel(suitTracks, soundTrack2, suitTrack3, suitTrack2)

def doBrokenConnection(attack):
    suit = attack['suit']
    battle = attack['battle']
    theSuit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    notifyTrack = Sequence(ActorInterval(theSuit, 'sound-react-nt', endTime=2.5), ActorInterval(theSuit, 'throttletwo', startTime=3), Func(theSuit.setNeutralAnimationDrop), Wait(2.0))
    soundTrack = getSoundTrack('mus_dialup_0.ogg')
    soundTrack4 = getSoundTrack('SA_hit.ogg', delay=Wait(theSuit.getDuration('throttletwo') - 4),node=suit)
    selfDamageTrack = Sequence(Wait(3), Func(suit.showHpText, "CONNECTION DROPPED!", 2, openEnded=0))
    makeImmune = Func(suit.makeVulnerable)
    makeImmune2 = Parallel(Func(suit.makeAngry, 4))
    makeDamageUp = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 30), Func(suit.checkVulnerabilityUp, + 30))
    return Parallel(notifyTrack, makeImmune, makeImmune2, makeDamageUp, selfDamageTrack, suitTrack, soundTrack4, soundTrack)

def doBrokenConnectionOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(3.0))
    makeImmune = Func(suit.makeVulnerable)
    makeImmune2 = Parallel(Func(suit.makeNonImmortal))
    makeDamageUp = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 30), Func(suit.checkVulnerabilityUp, + 30))
    selfDamageTrack = Func(suit.showHpText, "CONNECTION DROPPED!", 2, openEnded=0)
    return Parallel(suitTrack, makeImmune, makeImmune2, makeDamageUp, selfDamageTrack)

def doVoicemail(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack = Sequence( ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute,
                           "Every call costs more, and I always keep track... Updating billing record to %s dollars." %
                           int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(calculator.removeNode)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg')
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doVoicemailReal(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25), Wait(2.0))
    suitName = suit.getStyleName()
    phonePosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]),
                         Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24),
                         Func(receiver.wrtReparentTo, suit.getRightHand()),
                         LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)),
                         Wait(2.14), Func(receiver.wrtReparentTo, phone), Wait(0.62),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO),
                         Func(MovieUtil.removeProps, [receiver, phone]))
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    makeImmune = Func(suit.makeImmortal)
    return Parallel(suitTrack, propTrack, soundTrack, makeImmune)

def doBusySignal(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    allKnifeTracks2 = Parallel()
    partTracks2 = Parallel()
    soundTracks = Parallel()
    notifyTracks = Parallel()
    suitTrack2 = Parallel()
    suitTrack = Sequence(getSuitAnimTrack(attack))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        allKnifeTracks = Parallel()
        numKnives = 15
        knifeTracks = Sequence()
        knives = [globalPropPool.getProp('dagger') for i in range(numKnives)]
        step = math.radians(360.0 / numKnives)
        radius = 4.0
        prepareKnives = Parallel()
        for i in range(len(knives)):
            angle = i * step
            x = radius * math.cos(angle) + toon.getX(battle)
            y = radius * math.sin(angle) + toon.getY(battle)
            knife = knives[i]
            prepareKnives.append(Sequence(
                Wait(i * 0.05),
                Func(knife.reparentTo, battle),
                Func(knife.setPos, Point3(x, y, 1.0)),
                Func(knife.lookAt, Point3(toon.getX(battle), toon.getY(battle), 1.0)),
                Func(base.playSfx, globalBattleSoundCache.getSound('SA_piercing.ogg'), node=toon),
                LerpScaleInterval(knife, 0.25, Point3(0.5), startScale=Point3(0.01)),
            ))

        knifeTracks.append(prepareKnives)
        knifeTracks.append(Wait(1.5))
        closeTrack = Parallel()
        for knife in knives:
            closeTrack.append(Sequence(
                LerpPosInterval(knife, 0.2, Point3(toon.getX(battle), toon.getY(battle), 1.0), blendType='easeIn'),
                Func(MovieUtil.removeProp, knife)
            ))
        partTracks = Parallel()
        sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
        sparks = sparkEffect.getParticlesNamed('particles-1')
        sparks.setPoolSize(20)
        sparks.setLitterSize(20)
        sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
        sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
        partTracks.append(Sequence(
            Wait(2.75),
            Parallel(
                ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                autoFinish=1
            )
        ))
        notifyTrack = Sequence(Wait(2.75), Func(toon.showHpTextNew, - int(dmg), text="CONFUSED!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.makeConfused), Func(toon.addConfusedRounds, 1)))
        if dmg > 0:
            origH = suit.getH(battle)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)
            suit.setH(battle, origH)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            suitTrack2.append(Sequence(Wait(1.5), Parallel(suitTrack, LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle)),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            knifeTracks.append(closeTrack)
            allKnifeTracks.append(knifeTracks)
            allKnifeTracks2.append(allKnifeTracks)
            partTracks2.append(partTracks)
            notifyTracks.append(notifyTrack)
            soundTracks.append(getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=2.75, node=suit))
    damageAnims = [['slip-backward', 0.01, 0.6]]
    toonTracks = getToonTracksCheat(attack, damageDelay=2.75, splicedDamageAnims=damageAnims, dodgeDelay=2.2,
                                    dodgeAnimNames=['nothing'])
    return Parallel(allKnifeTracks2, suitTrack2, partTracks2, notifyTracks, toonTracks, soundTracks)


def doWiretapped(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    dmg = (attack['target'][0]['hp']) * len(battle.activeToons)
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    suitName = suit.getStyleName()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(2.7))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    explode = []
    explodePosPoints = [Point3(0, 10, 1), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 10, 1), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(Wait(2.7))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    phonePosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]),
                         Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24),
                         Func(receiver.wrtReparentTo, suit.getRightHand()),
                         LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)),
                         Wait(2.14), Func(receiver.wrtReparentTo, phone), Wait(0.62),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO),
                         Func(MovieUtil.removeProps, [receiver, phone]))#propTrack = Sequence(Wait(0.3), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, scaleUpPoint, MovieUtil.PNT3_NEARZERO), Wait(pickupDelay), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpScaleInterval(receiver, 0.01, receiverAdjustScale), LerpPosHprInterval(receiver, 0.0001, Point3(-0.53, 0.21, -0.54), VBase3(-99.49, -35.27, 1.84)), Wait(dialDuration), Func(receiver.wrtReparentTo, phone), Wait(finalPhoneDelay), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTracks = getToonTracks(attack, 2.8, ['slip-backward'], 4.7, ['jump'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.8)
    makeNotImmune = Func(suit.makeNonImmortal)
    makeNotImmune2 = Sequence(Func(suit.makeUnVulnerable), Func(suit.checkVulnerabilityUp, - 30))
    if suit.getDamageUp() > 30:
        makeDamageUp = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, - 30))
    else:
        makeDamageUp = Parallel(Func(suit.makeUnDamageUp), Func(suit.checkDamageUp, - 30))
    return Parallel(suitTrack, propTrack, soundTrack, makeDamageUp, soundTrack1, toonTracks, makeNotImmune, makeNotImmune2, explodeTracks, explosionTrack)

def doManagerialProtectionImmunity(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    notifyTrack = Func(suit.showHpTextWhite, 'IMMUNE!')
    makeImmune = Func(suit.makeImmortal)
    makeUnVulnerable = Func(suit.makeUnVulnerable)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, notifyTrack, makeUnVulnerable, makeImmune)

def doManagerialProtection(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(2.0))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, soundTrack)

def doRefinement(attack):
    theSuit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'phouse':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            suitTrack.append(Func(suit.checkRefinementPowerhouse))
        else:
            suitTrack.append(Func(suit.checkRefinement))
        suitTrack.append(Func(battle.unSueSuit, suit))
        if not suit.dna.name == 'ambass':
            suitTrack.append(Parallel(Sequence(Wait(3)),
                                          Func(suit.setChatAbsolute,
                                               random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                               CFSpeech | CFTimeout)))
        suitTrack.append(
                Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
    posPoints = [Point3(-0.25, 0, 0), VBase3(0, 180, 0)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = loader.loadModel('phase_12/models/bossbotHQ/canoffood')
        can = knife.find('**/can')
        can.setScale(.5)
        knifeTrack = Sequence(
            getPropAppearTrack(can, theSuit.getRightHand(), posPoints, .5, VBase3(0.5, 0.5, 0.5),
                               scaleUpTime=0.1),
            Wait(1.5),
            Parallel(
                getThrowTrack(can, hitPoint, 1.5, battle, -10.288),
                LerpHprInterval(can, 0.8, VBase3(0, 0, 0)), LerpScaleInterval(can, 0, VBase3(1, 1, 1))),
        Parallel(LerpPosInterval(can, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)), Sequence(Wait(0.25), LerpScaleInterval(can, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, can)
        )
        knifeTracks.append(knifeTrack)
    tauntIndex = attack['taunt']
    taunt = random.choice(
        ["It's important to stay adequately oiled when defeating Toons.", "I'm suspending this well.",
"Freshly drilled to keep us in working order."])
    makeUnVulnerable = Func(theSuit.makeUnVulnerable)
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + theSuit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    suitTrackAnim = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    soundTrack1 = getSoundTrack('SA_repair.ogg', delay=2.5)
    soundTrack2 = getSoundTrack('SA_refinement.ogg', delay=2, node=theSuit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    makeNotImmune = Func(theSuit.makeNonImmortal)
    return Parallel(suitTrackAnim, makeUnVulnerable, makeNotImmune, suitTracks, multiTrack, knifeTracks)

def doRefinementManager(attack):
    theSuit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'phouse':
                currentBossHealth = s.currHP
        if suit.dna.name == 'wtapper':
            if currentBossHealth >= 1:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpTextNew, 0, text="REFINED!", colorCode=1))
                elif suit.currHP + 350 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextNew, x, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextNew, 350, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, 350))
            else:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpTextNew, 0, text="REFINED!", colorCode=1))
                elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextNew, x, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextNew, 200, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, 200))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            if not suit.dna.name == 'ambass':
                suitTrack.append(Parallel(Sequence(Wait(3)),
                                          Func(suit.setChatAbsolute,
                                               random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                               CFSpeech | CFTimeout)))
        if suit.dna.name == 'bkeeper':
            if currentBossHealth >= 1:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpTextNew, 0, text="REFINED!", colorCode=1))
                elif suit.currHP + 350 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextNew, x, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextNew, 350, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, 350))
            else:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpTextNew, 0, text="REFINED!", colorCode=1))
                elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextNew, x, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextNew, 200, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, 200))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            if not suit.dna.name == 'ambass':
                suitTrack.append(Parallel(Sequence(Wait(3)),
                                          Func(suit.setChatAbsolute,
                                               random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                               CFSpeech | CFTimeout)))
        if suit.dna.name == 'phouse':
            if currentBossHealth >= 1:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpTextNew, 0, text="REFINED!", colorCode=1))
                elif suit.currHP + 350 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextNew, x, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextNew, 350, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, 350))
            else:
                x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpTextNew, 0, text="REFINED!", colorCode=1))
                elif suit.currHP + 200 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextNew, x, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextNew, 200, text="REFINED!", colorCode=1))
                    suitTrack.append(Func(suit.setHealthForMe, 200))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            if not suit.dna.name == 'ambass':
                suitTrack.append(Parallel(Sequence(Wait(3)),
                                          Func(suit.setChatAbsolute,
                                               random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                               CFSpeech | CFTimeout)))
        suitTrack.append(
                Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
    posPoints = [Point3(-0.25, 0, 0), VBase3(0, 180, 0)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = loader.loadModel('phase_12/models/bossbotHQ/canoffood')
        can = knife.find('**/can')
        can.setScale(.5)
        knifeTrack = Sequence(
            getPropAppearTrack(can, theSuit.getRightHand(), posPoints, .5, VBase3(0.5, 0.5, 0.5),
                               scaleUpTime=0.1),
            Wait(1.5),
            Parallel(
                getThrowTrack(can, hitPoint, 1.5, battle, -10.288),
                LerpHprInterval(can, 0.8, VBase3(0, 0, 0)), LerpScaleInterval(can, 0, VBase3(1, 1, 1))),
        Parallel(LerpPosInterval(can, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)), Sequence(Wait(0.25), LerpScaleInterval(can, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, can)
        )
        if suit.dna.name == 'bkeeper' or suit.dna.name == 'wtapper' or suit.dna.name == 'phouse':
            knifeTracks.append(knifeTrack)
    makeUnVulnerable = Func(theSuit.makeUnVulnerable)
    suitTrackAnim = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    soundTrack1 = getSoundTrack('SA_repair.ogg', delay=2.5)
    soundTrack2 = getSoundTrack('SA_refinement.ogg', delay=2, node=theSuit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    makeNotImmune = Func(theSuit.makeNonImmortal)
    return Parallel(suitTrackAnim, makeUnVulnerable, makeNotImmune, suitTracks, multiTrack, knifeTracks)

def doHeadRoller(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    targetSuit = battle.activeSuits[ind]

    managerTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack = Sequence(Wait(1.0), ActorInterval(targetSuit, 'soak', duration=2.25),
                         Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                                                          "Ouch.",
                                                                                          CFSpeech | CFTimeout),
                         Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    hpTrack = Sequence(Wait(3.25), Func(targetSuit.checkHeadRoller, manager, battle), Func(manager.makeDamageUp), Func(manager.checkDamageUp, + 5), Wait(3.0), Func(manager.showHpString, "+5% Damage!"))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.25, node=manager)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=manager))
    return Parallel(managerTrack, soundTrack2, hpTrack, suitTrack, soundTrack)

def doHeadRollerGroup(attack):
    manager = attack['suit']
    battle = attack['battle']
    selfDamageTracks = Parallel()
    suitTracks = Parallel()
    waitTrack = Sequence(Wait(10.0))
    managerTrack = Sequence(getSuitAnimTrack(attack))

    for targetSuit in battle.activeSuits:
        suitTrack = Sequence(Wait(1.0), Func(targetSuit.checkHeadRoller, battle))
        selfDamageTrack = Sequence(Wait(7))
        suitTrack2 = Sequence(Wait(1.0), ActorInterval(targetSuit, 'soak', duration=2.25),
                              Parallel(ActorInterval(targetSuit, 'pie-small-react', duration=2.25),
                                       Func(targetSuit.setChatAbsolute,
                                            "Nice try.",
                                            CFSpeech | CFTimeout)),
                              Wait(1.0), Func(targetSuit.checkCogHP, battle), Func(targetSuit.setNeutralAnimation))
        selfDamageTrack2 = Sequence(Wait(3.25), Func(targetSuit.showHpTextCheat, -250),
                                    Func(targetSuit.showHpStringDamaged, "DAMAGED!"),
                                    Func(targetSuit.setHealthForMe, -250),
                                    Func(targetSuit.updateHealthBar, 0))
        if not targetSuit.dna.name == 'ambass':
            if not targetSuit.isManager and targetSuit.isTarget:
                selfDamageTracks.append(selfDamageTrack)
                suitTracks.append(suitTrack)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=manager))
    return Parallel(managerTrack, suitTracks, soundTrack, waitTrack)

def doGhostMentality(attack):
    manager = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    managerTracks = Parallel()
    moveTracks = Parallel()

    for targetSuit in battle.activeSuits:
        targetPos = targetSuit.getPos(battle)
        origH = suit.getH(battle)
        targetPos = targetSuit.getPos(battle)
        suit.headsUp(battle, targetPos)
        targetH = suit.getH(battle)
        suit.setH(battle, origH)
        delta = (targetH - origH + 180) % 360 - 180
        if delta > 0:
            shuffleAnim = 'shuffle-right'
        else:
            shuffleAnim = 'shuffle-left'
        headsUp = LerpHprInterval(suit, 0, (origH + delta - 45, 0, 0), startHpr=(origH, 0, 0), other=battle)
        sinkPos = manager.getPos(battle)
        dropPos = manager.getPos(battle)
        sinkPos2 = manager.getPos(battle)
        dropPos2 = manager.getPos(battle)
        target = attack['target']
        toon = target[0]['toon']
        sinkPos.setY(sinkPos.getY() + 12.5)
        sinkPos.setZ(sinkPos.getZ() - 4.5)
        sinkPos2.setY(sinkPos.getY() - 22.5)
        battle = attack['battle']
        targetPos2 = toon.getPos(battle)
        origPos, origHpr = battle.getActorPosHpr(manager)
        headsUp2 = Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta - 45, 0, 0), other=battle))
        moveTrack = Sequence(LerpPosInterval(manager, manager.getDuration('walk'), sinkPos2, other=battle),
                             Wait(manager.getDuration('deadwood')),
                             LerpPosInterval(manager, manager.getDuration('walk'), dropPos, other=battle),
                             Func(manager.setPos, battle, dropPos))
        managerTrack = Sequence(ActorInterval(manager, 'walk'), headsUp, getSuitAnimTrack(attack),
                             ActorInterval(manager, 'walk'), headsUp2, Func(manager.setNeutralAnimation))
        managerTracks.append(managerTrack)
        moveTracks.append(moveTrack)
        suitTrack = Sequence(Wait(manager.getDuration('deadwood') + manager.getDuration('walk') - 1.5), MovieUtil.createGhostMentalityTrack(targetSuit, battle))
        suitTrack2 = Sequence(Wait(manager.getDuration('deadwood') + manager.getDuration('walk') - 1.5), Func(targetSuit.showHpString, "+50% Damage!"), Func(targetSuit.checkDamageUp, 50))
        suitTrack.append(Func(battle.unSueSuit, targetSuit))
        if not targetSuit.dna.name == 'ambass':
            if targetSuit.isManager:
                pass
            if not targetSuit.isManager and not targetSuit.isVirtual:
                suitTracks.append(suitTrack)
            if targetSuit.isVirtual:
                suitTracks.append(suitTrack2)
    soundTrack = Sequence(Wait(manager.getDuration('walk')), SoundInterval(globalBattleSoundCache.getSound('SA_deadwood.ogg'), node=manager))
    return Parallel(managerTracks, moveTracks, suitTracks, soundTrack)

def doAmbassadorPhase2(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrackAnim = Sequence()
    soundTrack3 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    suitTrackAnim.append(MovieUtil.createAmbassadorReviveTrack(theSuit, battle))
    suitTrackAnim.append(Func(theSuit.makeAmbassadorPhase3))
    suitTrackAnim.append(Func(theSuit.setNeutralAnimationDrop))
    suitTrackAnim.append(Sequence(Parallel(Func(theSuit.updateHealthBar, 0), getSuitAnimTrack(attack),
                                  Func(theSuit.showHpString, "+50% Damage!")),
                                  Func(theSuit.setNeutralAnimationDrop)))
    suitTrackAnim.append(Wait(3))
    return Parallel(suitTrackAnim, soundTrack3)

def doAmbassadorFlyMove(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrackAnim = Sequence(Func(theSuit.beginSupaFlyMove, theSuit.getPos(battle), ))
    return Parallel(suitTrackAnim)

def doCollectCallDues(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    whirlSeq = Parallel()
    tornadoTrack = Parallel()
    toonSpinTracks = Parallel()
    toonLiftTracks = Parallel()

    # -------------------------------------------------
    # Load SFX ONCE
    # -------------------------------------------------
    whirlSfx = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_whirlwind.ogg')
    whirlSfx.setLoop(True)

    # -------------------------------------------------
    # Damage animation setup (unchanged)
    # -------------------------------------------------
    damageAnims = [
        ['duck', 0.01, 0.01, 1.1]
    ]
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 2.1, startTime=2.26))
    damageAnims.append(['slip-forward'])

    # Predefine bill types (no random.choice every loop)
    billTypes = ('10dollar', '1dollar', '5dollar', '50dollar')

    for t in targets:
        toon = t['toon']

        # -------------------------------------------------
        # Tornado node
        # -------------------------------------------------
        tornadoNode = NodePath("tornadoNode")
        tornadoNode.reparentTo(render)
        tornadoNode.setPos(toon.getPos(render))
        tornadoNode.setZ(tornadoNode.getZ() + 1)
        tornadoNode.setScale(0.2)

        # -------------------------------------------------
        # Toon Spin (unchanged timing)
        # -------------------------------------------------
        originalHpr = toon.getHpr()
        originalPos = toon.getPos()

        toonSpinTracks.append(
            Sequence(
                Wait(0.9),

                # Big spin while lifted
                LerpHprInterval(
                    toon,
                    5.0,
                    Point3(originalHpr.getX() + 10800, 20, 10),
                    blendType='easeInOut'
                ),

                # Snap cleanly back
                LerpHprInterval(
                    toon,
                    0.4,
                    originalHpr
                )
            )
        )

        toonLiftTracks.append(
            Sequence(
                Wait(0.9),
                LerpPosInterval(toon, 5.5,
                                Point3(originalPos.getX(),
                                       originalPos.getY(),
                                       originalPos.getZ() + 20)),
                LerpPosInterval(toon, 0.5, originalPos)
            )
        )

        # -------------------------------------------------
        # Bills (same count, optimized structure)
        # -------------------------------------------------
        BILL_COUNT = 80
        ATTACK_DURATION = 7.0
        STAGGER = 0.05
        RADIUS = 100.0

        for x in range(BILL_COUNT):
            billNode = tornadoNode.attachNewNode("billNode")
            bill = globalPropPool.getProp(billTypes[x % 4])
            bill.setTwoSided(True)
            bill.setPosHprScale(0, 0, 0, random.randint(0, 360), 0, random.randint(0, 360), 10.0 - (x * 0.03),
                                10.0 - (x * 0.03), 10.0 - (x * 0.03))
            bill.reparentTo(billNode)
            bill.hide()

            startDelay = x * STAGGER
            activeTime = max(0.1, ATTACK_DURATION - startDelay)

            # Spread starting angles evenly
            startAngle = (x / float(BILL_COUNT)) * 360

            # def spiralMotion(node, duration, baseAngle, heightOffset):
            #     def updateSpiral(t):
            #         progress = t / duration
            #
            #         # Orbit speed (keep your fast spin if you like)
            #         angle = math.radians(baseAngle + (t * 1880))
            #
            #         radius = RADIUS * (0.2 + (progress * 0.8))
            #
            #         xPos = math.cos(angle) * radius
            #         yPos = math.sin(angle) * radius
            #
            #         # Keep your vertical climb behavior
            #         zPos = heightOffset + (progress * 40)
            #
            #         node.setPos(xPos, yPos, zPos)
            #
            #     return LerpFunc(updateSpiral, duration=duration)

            def spiralMotion(node, duration, baseAngle, heightOffset):
                def updateSpiral(t):
                    progress = t / duration
                    angle = math.radians(baseAngle + (t * 10800))  # 2 full spins
                    radius = RADIUS * (0.1 + (progress * 0.9))

                    xPos = math.cos(angle) * radius
                    yPos = math.sin(angle) * radius
                    zPos = heightOffset + (t * 40)

                    node.setPos(xPos, yPos, zPos)

                return LerpFunc(updateSpiral, duration=duration)

            whirlSeq.append(
                Sequence(
                    Wait(startDelay),
                    Func(bill.show),
                    spiralMotion(billNode, activeTime, startAngle, x),
                    Func(MovieUtil.removeProp, bill)
                )
            )

        # -------------------------------------------------
        # Tornado movement + sound (single sequence)
        # -------------------------------------------------
        tornadoTrack.append(
            Sequence(
                Func(whirlSfx.play),
                Wait(7.0),
                Func(whirlSfx.stop),
                Func(tornadoNode.removeNode)
            )
        )

    suitTrack = Sequence(getSuitAnimTrack(attack))

    toonTrack = getToonTracks(
        attack,
        damageDelay=.9,
        splicedDamageAnims=damageAnims,
        dodgeDelay=0.91,
        dodgeAnimNames=['sidestep'],
        showDamageExtraTime=6,
        showMissedExtraTime=1.0
    )

    soundTrack = Sequence(
        Wait(6.9),
        SoundInterval(
            globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'),
            node=suit
        )
    )

    return Parallel(
        suitTrack,
        toonTrack,
        toonLiftTracks,
        toonSpinTracks,
        whirlSeq,
        tornadoTrack,
        soundTrack
    )

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
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, 2.5, ['slip-backward'], 1, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack)

def doAmbassadorDamageUpDesperation(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)
    makeImmune = Func(suit.makeDamageUp)
    managerHealTrack = Sequence(Wait(2), Func(suit.showHpTextCheat, + 250), Func(suit.showHpString, "1.25x DMG MULTIPLIER!"), Func(suit.setHealthForMe, + 250), Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doAmbassadorDamageUp(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    destroyedSuits = []
    syphonedManagerSuit = []
    for suit in battle.activeSuits:
        if not suit.dna.name in SuitBattleGlobals.SpecialCogDict and suit.isTarget:
            destroyedSuits.append(suit)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0)
    makeImmune =  Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + (5 * len(destroyedSuits))))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpTextCheat, + (100 * len(destroyedSuits))), Func(theSuit.showHpString, "+%s" % (5 * len(destroyedSuits)) + "%" + " Damage!"), Func(theSuit.setHealthForMe, + (100 * len(destroyedSuits))), Func(theSuit.updateHealthBar, 0), Wait(3.0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doDamageUp1(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0)
    makeImmune =  Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 5))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpTextNew, 100, text="+5%" + " Damage!", colorCode=1), Func(theSuit.setHealthForMe, + 100), Func(theSuit.updateHealthBar, 0), Wait(3.0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doDamageUp2(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0)
    makeImmune =  Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 10))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpTextNew, 200, text="+10%" + " Damage!", colorCode=1), Func(theSuit.setHealthForMe, + 200), Func(theSuit.updateHealthBar, 0), Wait(3.0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doDamageUp3(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0)
    makeImmune =  Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 15))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpTextNew, 300, text="+15%" + " Damage!", colorCode=1), Func(theSuit.setHealthForMe, + 300), Func(theSuit.updateHealthBar, 0), Wait(3.0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doDamageUp4(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0)
    makeImmune =  Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 20))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpTextNew, 400, text="+20%" + " Damage!", colorCode=1), Func(theSuit.setHealthForMe, + 400), Func(theSuit.updateHealthBar, 0), Wait(3.0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doDamageUp5(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0)
    makeImmune =  Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 25))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpTextNew, 500, text="+25%" + " Damage!", colorCode=1), Func(theSuit.setHealthForMe, + 500), Func(theSuit.updateHealthBar, 0), Wait(3.0))
    return Parallel(suitTrack, soundTrack, managerHealTrack, makeImmune)

def doCollectCallDamage(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
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
    damageDelay = 1.7
    sprayEffects = [BattleParticles.createParticleEffect(file='spinSpray') for t in targets]
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
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
    soundTracks = Parallel()
    for toon in battle.activeSuits:
        if not toon.dna.name == 'wtapper':
            spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
            spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
            spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
            spinEffect1.reparentTo(toon)
            spinEffect2.reparentTo(toon)
            spinEffect3.reparentTo(toon)
            soundTracks.append(Sequence(Wait(2.0), Func(toon.showHpTextNew, 0, text='+10% Damage!', colorCode=1)))
            soundTracks.append(Parallel(Func(toon.makeDamageUp), Func(toon.checkDamageUp, + 10)))
            height1 = toon.getHeight() - (toon.getHeight() / 3)
            height2 = toon.getHeight() - (toon.getHeight() / 2)
            height3 = toon.getHeight() - (toon.getHeight() / 1.25)
            spinEffect1.setPos(0.8, -0.7, height1)
            spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
            spinEffect1.setHpr(spinEffect1, 0, 50, 0)
            spinEffect2.setPos(0.8, -0.7, height2)
            spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
            spinEffect2.setHpr(spinEffect2, 0, 50, 0)
            spinEffect3.setPos(0.8, -0.7, height3)
            spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
            spinEffect3.setHpr(spinEffect3, 0, 50, 0)
            spinEffect1.wrtReparentTo(toon)
            spinEffect2.wrtReparentTo(toon)
            spinEffect3.wrtReparentTo(toon)
            spinTracks1.append(getPartTrack(spinEffect1, 1.5, 5.9, [spinEffect1, toon, 0], softStop=-2))
            spinTracks2.append(getPartTrack(spinEffect2, 1.5, 5.9, [spinEffect2, toon, 0], softStop=-2))
            spinTracks3.append(getPartTrack(spinEffect3, 1.5, 5.9, [spinEffect3, toon, 0], softStop=-2))
    soundTracks.append(Sequence(getSoundTrack('SA_life_insurance_loop.ogg', delay=2.0), getSoundTrack('SA_life_insurance_loop.ogg'), getSoundTrack('SA_life_insurance_loop.ogg')))
    return Parallel(spinTracks1, soundTrack, calcPropTrack, spinTracks2, spinTracks3, suitTrack, soundTracks)

def doCloseTheLoopNew(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    allKnifeTracks2 = Parallel()
    partTracks2 = Parallel()
    soundTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        allKnifeTracks = Parallel()
        numKnives = 15
        knifeTracks = Sequence()
        knives = [globalPropPool.getProp('dagger') for i in range(numKnives)]
        step = math.radians(360.0 / numKnives)
        radius = 4.0
        prepareKnives = Parallel()
        for i in range(len(knives)):
            angle = i * step
            x = radius * math.cos(angle) + toon.getX(battle)
            y = radius * math.sin(angle) + toon.getY(battle)
            knife = knives[i]
            prepareKnives.append(Sequence(
                Wait(i * 0.05),
                Func(knife.reparentTo, battle),
                Func(knife.setPos, Point3(x, y, 1.0)),
                Func(knife.lookAt, Point3(toon.getX(battle), toon.getY(battle), 1.0)),
                Func(base.playSfx, globalBattleSoundCache.getSound('SA_piercing.ogg'), node=toon),
                LerpScaleInterval(knife, 0.25, Point3(0.5), startScale=Point3(0.01)),
                ))

        knifeTracks.append(prepareKnives)
        knifeTracks.append(Wait(1.5))
        closeTrack = Parallel()
        for knife in knives:
            closeTrack.append(Sequence(
                    LerpPosInterval(knife, 0.2, Point3(toon.getX(battle), toon.getY(battle), 1.0), blendType='easeIn'),
                    Func(MovieUtil.removeProp, knife)
                ))
        partTracks = Parallel()
        sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
        sparks = sparkEffect.getParticlesNamed('particles-1')
        sparks.setPoolSize(20)
        sparks.setLitterSize(20)
        sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
        sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
        partTracks.append(Sequence(
                Wait(2.75),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))
        notifyTrack = Sequence(Wait(2.75), Func(toon.showHpText, - int(dmg)))
        if dmg > 0:
            knifeTracks.append(closeTrack)
            allKnifeTracks.append(knifeTracks)
            allKnifeTracks2.append(allKnifeTracks)
            partTracks2.append(partTracks)
            notifyTracks.append(notifyTrack)
            soundTracks.append(getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=2.75, node=suit))
    damageAnims = [['slip-backward', 0.01, 0.6]]
    toonTracks = getToonTracksCheat(attack, damageDelay=2.75, splicedDamageAnims=damageAnims, dodgeDelay=2.2,
                              dodgeAnimNames=['nothing'])
    return Parallel(allKnifeTracks2, partTracks2, notifyTracks, toonTracks, soundTracks)

def doWiretapperGagBan(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    allTubeTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))

        hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
        hips = toon.getHipsParts()
        animal = toon.style.getAnimal()
        scale = ToontownGlobals.toonBodyScales[animal]
        knife = globalPropPool.getProp('dagger')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.0),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 3.0, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
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
        soundTrack2 = getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=4)
        notifyTrack = Sequence(Wait(4), Func(toon.showHpText, - int(dmg)))
        if dmg > 0:
            allTubeTracks.append(tubeTracks)
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            knifeTracks.append(knifeTrack)
            notifyTracks.append(notifyTrack)
    damageAnims = [['struggle'], ['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=0, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                  dodgeAnimNames=['neutral'], showDamageExtraTime=4)
    return Parallel(toonTracks, soundTracks, knifeTracks, notifyTracks, toonDamageTrack, allTubeTracks)

def doBookkeeping(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    makeDamageUp = Func(suit.makeBookkeeping)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('suit_promotion_sfx.ogg'), node=suit))
    return Parallel(suitTrack, makeDamageUp, soundTrack)

def doFore(attack):
    theSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    oldPos, oldHpr = battle.getActorPosHpr(theSuit)
    moveTracks = Parallel()
    moveTracks.append(Sequence(LerpPosInterval(suit, 0, (0, -50, 0), other=battle),
                               LerpHprInterval(suit, 0, (0, 0, 0), other=battle),
                               Func(suit.setNeutralAnimationDrop)))
    def getDustCloudIval(oldPos=oldPos):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(0.4)
        dustCloud.createTrack()
        dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
        return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, battle, oldPos + (0, 0, theSuit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                        name='dustCloadIval')
    def getDustCloudIval2(oldPos=oldPos):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(0.4)
        dustCloud.createTrack()
        dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
        return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, battle, oldPos + (0, -50, theSuit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                        name='dustCloadIval')
    suitTrack = Sequence(Parallel(Func(getDustCloudIval().start), Func(theSuit.hide)), Wait(2.0), Parallel(Func(getDustCloudIval2().start), Func(theSuit.show)))
    cameraTrack = Sequence(Wait(2.0), doForeAttack(attack))
    return Parallel(suitTrack, moveTracks, cameraTrack)

def doForeRevert(attack):
    theSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    oldPos, oldHpr = battle.getActorPosHpr(theSuit)
    moveTracks = Parallel()
    moveTracks.append(Sequence(LerpPosInterval(suit, 0, resetPos, other=battle),
                               LerpHprInterval(suit, 0, resetHpr, other=battle),
                               Func(suit.setNeutralAnimationDrop)))
    def getDustCloudIval(oldPos=oldPos):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(0.4)
        dustCloud.createTrack()
        dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
        return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, battle, oldPos + (0, 0, theSuit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                        name='dustCloadIval')
    def getDustCloudIval2(oldPos=oldPos):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(0.4)
        dustCloud.createTrack()
        dustCloud.setColorScale(0.2, 0.2, 0.2, 1)
        return Sequence(Func(dustCloud.reparentTo, render), Func(dustCloud.setPos, battle, oldPos + (0, -50, theSuit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                        name='dustCloadIval')
    suitTrack = Sequence(Parallel(Func(getDustCloudIval2().start), Func(theSuit.hide)), Wait(0.5), Parallel(Func(getDustCloudIval().start), Func(theSuit.show), Wait(1.0)))
    return Parallel(suitTrack, moveTracks)

def doForeAttack2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.75), doForeRevert(attack))
    club = globalPropPool.getProp('golf-club')
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 2.25, Point3(1.1, 1.1, 1.1))
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
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

def doForeAttack(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.75), doForeRevert(attack))
    club = globalPropPool.getProp('golf-club')
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 2.25, Point3(1.1, 1.1, 1.1))
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
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

def doGeneration2(attack):
    suit = attack['suit']
    target = attack['target']
    battle = attack['battle']
    targetSuit = attack['suit']
    battle = attack['battle']
    suitPos = targetSuit.getPos(battle)
    headTrack = Sequence(Wait(1))
    suitTrack = Sequence(Parallel(getSuitAnimTrack(attack), ActorInterval(suit, 'mob-mentality', endTime=1)), Parallel(Func(suit.makeVulnerable), Func(suit.checkDamageUp, + 5), Func(suit.checkVulnerabilityUp, + 5)), ActorInterval(suit, 'large-zap'), Func(suit.setNeutralAnimationDrop))
    cagePropTracks = Parallel()
    texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker2.png')
    for headPart in suit.headParts:
        if not suit.isSkeleton:
            headTrack.append(Func(headPart.setTexture, texture2, 1))
    y = suitPos.getY()
    suitPos = targetSuit.getPos(battle)
    cage = loader.loadModel('phase_5/models/props/lightning')
    suitTrack2 = Sequence(Wait(1.0), Parallel(Func(suit.showHpText2, '+5% Vulnerable', 2), Func(suit.showHpStringLureManager2, '+5% Damage')))
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    cagePos = [Point3(suitPos.getX(), y + 1, 100.0), targetSuit.getHpr(battle)]
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.setBillboardPointEye()
    smokeTrack = Sequence(Wait(1), Func(smoke.reparentTo, targetSuit),
                          Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                   LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                          Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                          Func(MovieUtil.removeProp, smoke))
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 1, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0), Parallel(cagePosition),
        Parallel(
            cage.posInterval(0, Point3(suitPos.getX(), y, 0.1), blendType='easeIn'),

        ),
        Wait(0.5),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
    )
    cagePropTracks.append(cagePropTrack)
    makeDamageUp = Func(suit.makeDamageUp)
    soundTrack = getSoundTrack('AA_lightning.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('AA_cog_shock.ogg', delay=1.0, node=suit)
    if suit.isShielding:
        makeImmune2 = Parallel(Func(suit.makeUnDamageReduction), Func(suit.checkDamageReduction, - 30))
    else:
        makeImmune2 = Parallel()
    makeUnShielding7 = Func(suit.makeUnSyphon)
    makeUnShielding2 = Func(suit.makeUnShielding)
    makeUnShielding3 = Func(suit.makeUnLureImmune)
    makeUnShielding4 = Func(suit.makeUnSoakResistant)
    makeUnShielding5 = Func(suit.makeUnZapResistant)
    makeUnShielding6 = Func(suit.makeUnDropResistant)
    return Parallel(suitTrack, cagePropTracks, headTrack, soundTrack, makeUnShielding7, makeImmune2, makeUnShielding2, makeUnShielding3, makeUnShielding4, makeUnShielding5, makeUnShielding6, suitTrack2, soundTrack2, makeDamageUp, smokeTrack)

def doGeneration(attack):
    suit = attack['suit']
    target = attack['target']
    battle = attack['battle']
    targetSuit = attack['suit']
    battle = attack['battle']
    suitPos = targetSuit.getPos(battle)
    suitTrack = Sequence(Parallel(getSuitAnimTrack(attack), ActorInterval(suit, 'mob-mentality', endTime=1)), Parallel(Func(suit.makeVulnerable), Func(suit.checkDamageUp, + 5), Func(suit.checkVulnerabilityUp, + 5)), ActorInterval(suit, 'large-zap'), Func(suit.setNeutralAnimationDrop))
    cagePropTracks = Parallel()
    y = suitPos.getY()
    suitPos = targetSuit.getPos(battle)
    cage = loader.loadModel('phase_5/models/props/lightning')
    suitTrack2 = Sequence(Wait(1.0), Parallel(Func(suit.showHpText2, '+5% Vulnerable', 2), Func(suit.showHpStringLureManager2, '+5% Damage')))
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    cagePos = [Point3(suitPos.getX(), y + 1, 100.0), targetSuit.getHpr(battle)]
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.setBillboardPointEye()
    smokeTrack = Sequence(Wait(1), Func(smoke.reparentTo, targetSuit),
                          Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                   LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                          Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                          Func(MovieUtil.removeProp, smoke))
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 1, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0), Parallel(cagePosition),
        Parallel(
            cage.posInterval(0, Point3(suitPos.getX(), y, 0.1), blendType='easeIn'),

        ),
        Wait(0.5),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
    )
    cagePropTracks.append(cagePropTrack)
    makeDamageUp = Func(suit.makeDamageUp)
    soundTrack = getSoundTrack('AA_lightning.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('AA_cog_shock.ogg', delay=1.0, node=suit)
    return Parallel(suitTrack, cagePropTracks, soundTrack, suitTrack2, soundTrack2, makeDamageUp, smokeTrack)

def doGeneration3(attack):
    suit = attack['suit']
    target = attack['target']
    battle = attack['battle']
    targetSuit = attack['suit']
    battle = attack['battle']
    suitPos = targetSuit.getPos(battle)
    suitTrack = Sequence(Parallel(getSuitAnimTrack(attack), ActorInterval(suit, 'mob-mentality', endTime=1)), Func(suit.makeUnSoaked), Parallel(Func(suit.makeVulnerable), Func(suit.checkDamageUp, + 10), Func(suit.checkVulnerabilityUp, + 10)), ActorInterval(suit, 'large-zap'), Func(suit.setNeutralAnimationDrop))
    cagePropTracks = Parallel()
    y = suitPos.getY()
    suitPos = targetSuit.getPos(battle)
    cage = loader.loadModel('phase_5/models/props/lightning')
    suitTrack2 = Sequence(Wait(1.0), Parallel(Func(suit.showHpText2, '+10% Vulnerable', 2), Func(suit.showHpStringLureManager2, '+10% Damage')))
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    cagePos = [Point3(suitPos.getX(), y + 1, 100.0), targetSuit.getHpr(battle)]
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.setBillboardPointEye()
    smokeTrack = Sequence(Wait(1), Func(smoke.reparentTo, targetSuit),
                          Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                   LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                          Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                          Func(MovieUtil.removeProp, smoke))
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 1, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0), Parallel(cagePosition),
        Parallel(
            cage.posInterval(0, Point3(suitPos.getX(), y, 0.1), blendType='easeIn'),

        ),
        Wait(0.5),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
    )
    cagePropTracks.append(cagePropTrack)
    makeDamageUp = Parallel(Func(suit.makeDamageUp))
    soundTrack = getSoundTrack('AA_lightning.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('AA_cog_shock.ogg', delay=1.0, node=suit)
    return Parallel(suitTrack, cagePropTracks, soundTrack, suitTrack2, soundTrack2, makeDamageUp, smokeTrack)

def doAbsorb(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeShielding)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    node = suit.getGeomNode().getChild(0)
    headTrack = Sequence(Wait(.5))
    suitTrack.append(Wait(3.0))
    suitColorTrack = Sequence(Wait(0.5), LerpColorScaleInterval(node, duration=.5, colorScale=(0, 1, 0.078, 1),
                                                                blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.5, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, suitColorTrack, makeShielding)

def doSoakImmune(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeSoakResistant)
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.removePowerhouseRotation))
    texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker_squirt.png')
    headTrack = Sequence()
    suitTrack.append(Wait(3.0))
    for headPart in suit.headParts:
        if not suit.isSkeleton:
            headTrack.append(Func(headPart.setTexture, texture2, 1))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'squirt-small-react', startTime=2.25), Func(suit.setNeutralAnimationDrop))
    return Parallel(suitTrack, headTrack, makeShielding, suitTrack2)

def doDropImmune(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeDropResistant)
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.removePowerhouseRotation))
    headTrack = Sequence()
    suitTrack.append(Wait(1))
    texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker_drop.png')
    for headPart in suit.headParts:
        if not suit.isSkeleton:
            headTrack.append(Func(headPart.setTexture, texture2, 1))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'slip-forward'), Func(suit.setNeutralAnimationDrop))
    return Parallel(suitTrack, makeShielding, headTrack, suitTrack2)

def doZapImmune(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeZapResistant)
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.removePowerhouseRotation))
    suitTrack.append(Wait(3.0))
    headTrack = Sequence(Wait(1))
    texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker_zap.png')
    for headPart in suit.headParts:
        if not suit.isSkeleton:
            headTrack.append(Func(headPart.setTexture, texture2, 1))
    suitTrack2 = Sequence(Parallel(getSuitAnimTrack(attack), ActorInterval(suit, 'mob-mentality', endTime=1)), ActorInterval(suit, 'slip-backward'), Func(suit.setNeutralAnimationDrop))
    return Parallel(suitTrack, headTrack, makeShielding, suitTrack2)

def doSyphon(attack):
    suit = attack['suit']
    battle = attack['battle']
    makeShielding = Func(suit.makeUnSoakResistant)
    liftTracks = Parallel()
    headTrack = Sequence()
    liftEffect = BattleParticles.createParticleEffect('SyphonLift')
    liftEffect.setPos(suit.getPos(battle))
    liftEffect.setZ(liftEffect.getZ() - 1.3)
    liftTracks.append(getPartTrack(liftEffect, 0, 5.1, [liftEffect, battle, 0], softStop=-1))
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25), Func(suit.removePowerhouseRotation))
    suitTrack.append(Wait(3.0))
    texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker_syphon.png')
    for headPart in suit.headParts:
        if not suit.isSkeleton:
            headTrack.append(Func(headPart.setTexture, texture2, 1))
    return Parallel(suitTrack, liftTracks, headTrack, makeShielding)

def doSyphonDesperation(attack):
    BattleParticles.loadParticles()
    theSuit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    liftTracks = Parallel()
    for s in battle.activeSuits:
        liftEffect = BattleParticles.createParticleEffect('SyphonLift')
        liftEffect.setPos(s.getPos(battle))
        liftEffect.setZ(liftEffect.getZ() - 1.3)
        liftTracks.append(getPartTrack(liftEffect, 0, 5.1, [liftEffect, battle, 0], softStop=-1))
        makeSyphon = Func(s.makeSyphon, battle)
        suitTrack = Sequence()
        suitTrack.append(Wait(3))
        if not s.dna.name == 'phouse':
            suitTrack.append(Func(s.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout))
        suitTrack.append(makeSyphon)
        suitTrack.append(Func(s.setNeutralAnimationDrop))
        suitTracks.append(suitTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(theSuit.removePowerhouseRotation))
    suitTrack.append(Wait(3.0))
    soundTrack1 = getSoundTrack('SA_scabbard.ogg', node=theSuit)
    return Parallel(suitTrack, suitTracks, liftTracks, soundTrack1)

def doSlowBurn(attack):
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
    damageAnims.append(['slip-forward',
                        1e-05,
                        0.4,
                        1.2])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.8, startTime=1.2))
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
            soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0, node=suit)
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
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3, dodgeAnimNames=['sidestep'])
    return Parallel(baseFlameTracks, flameTracks, flecksTracks, notifyTracks, toonDamageTrack, colorTracks, soundTracks)

def doLureImmune(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeLureImmune)
    headTrack = Sequence()
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.removePowerhouseRotation))
    suitTrack.append(Wait(3.0))
    texture2 = loader.loadTexture('phase_14/maps/cc_t_ene_circuitbreaker_lure.png')
    for headPart in suit.headParts:
        if not suit.isSkeleton:
            headTrack.append(Func(headPart.setTexture, texture2, 1))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'rake-react'), Func(suit.setNeutralAnimationDrop))
    return Parallel(suitTrack, suitTrack2, makeShielding, headTrack)

def doLiquidateGROUP(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1
    notifyTracks = Parallel()
    suitTrack = Sequence(Wait(0.5), getSuitTrack(attack, playRate=1.25))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = [['cringe',
                    0.01,
                    0.4,
                    0.8], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracksCheat(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    for t in attack['target']:
        toon = t['toon']
        rainEffect = BattleParticles.createParticleEffect(file='paperRainfall')
        rainEffect2 = BattleParticles.createParticleEffect(file='paperRainfall')
        rainEffect3 = BattleParticles.createParticleEffect(file='paperRainfall')
        cloud = globalPropPool.getProp('stormcloud')
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 30)
        notifyTrack = Sequence(Wait(1.5), Func(toon.showHpTextNew, -int(dmg), text="GAG DEBUFF!", colorCode=1))
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'wtapper':
                currentBossHealth = s.currHP
        if currentBossHealth > 0:
            notifyTrack.append(Parallel(Func(toon.checkDamageDown, 75)))
        else:
            notifyTrack.append(Parallel(Func(toon.checkDamageDown, 50)))
        if t['hp'] != 0:
            notifyTracks.append(notifyTrack)
        cloudPropTrack = Sequence(
            Func(cloud.pose, 'stormcloud', 0),
            getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7),
            Func(battle.movie.needRestoreRenderProp, cloud),
            Func(cloud.wrtReparentTo, render),
            Wait(0.5),
            LerpPosInterval(cloud, .5, pos=targetPoint),
            Wait(partDelay),
            Parallel(
                Sequence(
                    ParticleInterval(rainEffect, cloud, worldRelative=0, duration=4.1, cleanup=True)
                ),
                Sequence(
                    Wait(0.1),
                    ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=4.0, cleanup=True)
                ),
                Sequence(
                    Wait(0.1),
                    ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=4.0, cleanup=True)
                ),
                Sequence(
                    ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1),
                    ActorInterval(cloud, 'stormcloud', startTime=1, duration=4.3)
                )
            ),
            Wait(0.4),
            LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO),
            Func(MovieUtil.removeProp, cloud),
            Func(battle.movie.clearRenderProp, cloud)
        )
        cloudPropTracks.append(cloudPropTrack)
    soundTrack1 = getSoundTrack('LB_boss_paper_spin.ogg', delay=1.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack)

def doThrowBook(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitDelay = 1.5
    propDelay = 0.1
    throwDuration = 1.0
    paper = globalPropPool.getProp('lawbook')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.5, 0, 0), VBase3(0, 0, 180)]
    propTracks = Parallel()
    notifyTracks = Parallel()
    explosionTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
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
        notifyTrack = Sequence(Wait(3.0), Func(toon.showHpTextNew, -int(dmg), text="GAG DEBUFF!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 2)))
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(3.0))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'wtapper':
                currentBossHealth = s.currHP
        if currentBossHealth > 0:
            notifyTrack.append(Parallel(Func(toon.checkDamageDown, 75)))
        else:
            notifyTrack.append(Parallel(Func(toon.checkDamageDown, 50)))
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
        sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(7, 7, 7)), Wait(0.25), LerpScaleInterval(paper, 0, MovieUtil.PNT3_NEARZERO))
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
    soundTrack = getSoundTrack('SA_throw_book.ogg', node=suit)
    toonTracks = getToonTracksCheat(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=1.5, dodgeAnimNames=['duck'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    soundTrack3 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=3)
    return Parallel(soundTrack3, suitTrack, notifyTracks, explosionTracks, toonTracks, propTracks, soundTrack)

def doPaperRain(attack):
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
    suitTrack = Sequence(Wait(0.5), getSuitTrack(attack))
    notifyTracks = Parallel()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        BattleParticles.loadParticles()
        cloud = globalPropPool.getProp('stormcloud')
        rainEffect = BattleParticles.createParticleEffect(file='paperRainfall')
        rainEffect2 = BattleParticles.createParticleEffect(file='paperRainfall')
        rainEffect3 = BattleParticles.createParticleEffect(file='paperRainfall')
        initialCloudHeight = suit.height + 30
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 30)
        notifyTrack = Sequence(Wait(1.5), Func(toon.showHpTextNew, -int(dmg), text="GAG DEBUFF!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 2)))
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'wtapper':
                currentBossHealth = s.currHP
        if currentBossHealth > 0:
            notifyTrack.append(Parallel(Func(toon.checkDamageDown, 75)))
        else:
            notifyTrack.append(Parallel(Func(toon.checkDamageDown, 50)))
        if dmg > 0:
            notifyTracks.append(notifyTrack)
        cloudPropTrack.append(Wait(0.6))
        cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
        cloudPropTrack.append(Parallel(
            Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=4.0, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=4.0, cleanup=True, softStopT=-1)),
            Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks.append(cloudPropTrack)
    soundTrack1 = getSoundTrack('LB_boss_paper_spin.ogg', delay=1.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    damageAnims = [['cringe',
                    0.01,
                    0.4,
                    0.8], ['duck', 0.01, 1.6]]
    toonTracks = getToonTracksCheat(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims,
                                    dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, cloudPropTracks, notifyTracks, soundTrack)

def doBudgetCuts(attack):
    suit = attack['suit']
    targets = attack['target']
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        toonTrack = Parallel(Func(toon.makeGagBan))
        toonTracks.append(toonTrack)
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'calculator', playRate=1.25), Func(suit.setNeutralAnimationDrop), Wait(2.0))
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    return Parallel(suitTrack, calcPropTrack, suitTrack2, toonTracks, soundTrack)

def __makeBudgetNodePath():
    tn = TextNode('BUDGET CUTS')
    tn.setFont(getSuitFont())
    tn.setText('BUDGET CUTS\nBUDGET CUTS\nBUDGET CUTS')
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

def doBudgetCutsOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack))
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
    stampPosPoints = [Point3(-0.25, -0.5, -0.25), VBase3(0, -90, 0)]
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        cancelled = __makeBudgetNodePath()
        missPoint = lambda cancelled = cancelled, toon = toon: __toonMissPoint(cancelled, toon)
        propTrack = Sequence(Func(__showProp, stamp, suit.getRightHand(), stampPosPoints[0], stampPosPoints[1]), LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_ONE), Wait(2.6), Func(battle.movie.needRestoreRenderProp, cancelled), Func(cancelled.reparentTo, render), Func(cancelled.setScale, 0.6), Func(cancelled.setPosHpr, stamp, 0.81, -1.11, -0.16, 0, 0, 90), Func(cancelled.setP, 0), Func(cancelled.setR, 0))
        propTrack.append(getPropThrowTrack(attack, cancelled, [__toonFacePoint(toon)], [missPoint]))
        propTrack.append(Func(MovieUtil.removeProp, cancelled))
        propTrack.append(Func(battle.movie.clearRenderProp, cancelled))
        propTrack.append(Wait(0.3))
        propTrack.append(LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, stamp))
        toonTrack = Parallel(getToonTrackCheat(attack, 3.4, ['conked'], 3.4, ['conked']))
        toonTrack.append(Sequence(Wait(3.4), ActorInterval(toon, 'conked')))
        notifyTrack = Sequence(Wait(3.4), Func(toon.showHpTextNew, 0, text="BUDGET CUTS!", colorCode=1))
        propTracks.append(propTrack)
        toonTracks.append(toonTrack)
        notifyTracks.append(notifyTrack)
    soundTrack = getSoundTrack('SA_rubber_stamp.ogg', delay=1.3, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTracks, suitTrack2, notifyTracks, propTracks, padPropTrack, soundTrack)

def doBudgetCuts2(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), Func(suit.setNeutralAnimationDrop))
    suitTrack2.append(Wait(2.0))
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 0.25
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator', animStartTime=0,
                                 animDuration=2.9)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    return Parallel(suitTrack, soundTrack, suitTrack2, calcPropTrack)

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
    moveTracks = Parallel()
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
        notifyTrack = Sequence(Wait(1.5), Func(toon.showHpTextNew, -int(dmg), text="BURNED!", colorCode=4))
        notifyTrack.append(Parallel(Func(toon.makeBurned), Func(toon.addBurnedRounds, 3)))
        if dmg > 0:
            origH = suit.getH(battle)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)
            suit.setH(battle, origH)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            moveTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'magic3-alt'),
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
    suitTrack = Sequence(getSuitAnimTrack(attack))
    toonTracks = getToonTracksCheat(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3,
                                    dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_boilerplate_a.ogg', delay=1.0, node=suit)
    if hitAtleastOneToon == True:
        multiTrackList = Parallel(suitTrack, moveTracks, baseFlameTracks, notifyTracks, flameTracks, partTracks4, flecksTracks,
                                  toonTracks, colorTracks, soundTrack)
    else:
        multiTrackList = Parallel()
    return multiTrackList

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

        notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextNew, -int(dmg), text="SNIPED!", colorCode=4))
        soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
        soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=1.5)
        suitTrack = Sequence(getSuitTrack(attack))
        suitTrack.append(Wait(2.0))
        if dmg > 0:
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            explosionTracks.append(explosionTrack)
            suitTracks.append(suitTrack)
            notifyTracks.append(notifyTrack)
    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, notifyTracks, toonDamageTrack, leftKnifeTracks, explosionTracks, soundTracks)

def doGroundbreaker(attack):
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.3
    dodgeDelay = 0.25
    suitTrack = getSuitTrack(attack)
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    puddleTracks = Parallel()
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                               dodgeAnimNames=['sidestep'])
    soundTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sandTrap = globalPropPool.getProp('quicksand')
        sandTrap.setHpr(Point3(120, 0, 0))
        sandTrap.setScale(0.01)
        sandTrap.setColor(0, 0, 0, 1)
        puddleTracks.append(Parallel(Func(toon.makeHidden), Func(toon.addHiddenRounds, 1)))
        puddleTracks.append(Sequence(Wait(5.0), Func(toon.hide)))
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
        soundTracks.append(getSoundTrack('SA_quake.ogg', duration=0.67 if dmg == 0 else 0.0, node=toon))

    return Parallel(suitTrack, toonTracks, soundTracks, puddleTracks)

def doGroundbreakerRevert(attack):
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.3
    dodgeDelay = 0.25
    damageAnims = [['slip-forward']]
    puddleTracks = Parallel()
    soundTracks = Parallel()
    suitTracks = Parallel()
    toonDamageTrack = getToonTracksCheat(attack, 0.25, ['nothing'], 0, ['neutral'])
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sinkPos = toon.getPos(battle)
        sinkPos.setZ(sinkPos.getZ() + 15)
        dropPos = toon.getPos(battle)
        moveTrack = Sequence(Func(toon.show), LerpPosInterval(toon, 0, sinkPos, other=battle), LerpPosInterval(toon, 0.5, dropPos, other=battle), Func(toon.setPos, battle, dropPos))
        toonTrack = Parallel(Sequence(Wait(0.25), ActorInterval(toon, 'slip-forward'), Func(toon.loop, 'neutral')), Func(toon.showHpText, -dmg, openEnded=0))
        if dmg > 0:
            suitTrack = Sequence(Wait(4.0))
            suitTracks.append(suitTrack)
            puddleTracks.append(toonTrack)
            puddleTracks.append(moveTrack)
            soundTracks.append(getSoundTrack('Toon_bodyfall_synergy.ogg', delay=0.25, duration=0.67 if dmg == 0 else 0.0, node=toon))

    return Parallel(soundTracks, toonDamageTrack, suitTracks, puddleTracks)

