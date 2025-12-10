from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
import PlayByPlayText
import math
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
        endPos = prop.getPos(parent) + v * (baseDistance + 5 + yOffset)
    else:
        endPos = prop.getPos() + v * (baseDistance + 5 + yOffset)
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
    targetPos = toon.getPos(battle)
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    trapStorage = {}
    trapStorage['trap'] = None
    track = Sequence(Wait(delay))
    if attack[
        'suitName'] == 'bkeeper':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    def reparentTrap(suit = suit, battle = battle, trapStorage = trapStorage):
        return

    track.append(Func(reparentTrap))
    track.append(Func(suit.headsUp, battle, targetPos))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
    origPos, origHpr = battle.getActorPosHpr(suit)
    track.append(Func(suit.setHpr, battle, origHpr))
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

    def returnTrapToSuit(suit = suit, trapStorage = trapStorage):
        return

    track.append(Func(returnTrapToSuit))
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
                               Func(MovieUtil.removeProp, indicator))
    if dmg > 0:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
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
                               Func(MovieUtil.removeProp, indicator))
    if dmg > 0:
        animTrack.append(getToonTakeDamageTrackCheat(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
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

        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
    else:
        splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
    soundTrack = getSoundTrack('laff_loss.ogg', delay=delay + showDamageExtraTime, node=toon)
    toonTrack.append(Func(toon.loop, 'neutral'))
  # if toon.hp - dmg <= 0:
      #  suit = attack['suit']
      #  toonTrack.append(Wait(3.0))
       # if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
        #    suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
      #  else:
         #   suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
    return Parallel(toonTrack, indicatorTrack, suitResponseTrack, soundTrack)


def getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    toonTrack = Sequence()
    toonTrack.append(Wait(delay))
    suitResponseTrack = Sequence()
    suit = attack['suit']
    if damageAnimNames:
        for d in damageAnimNames:
            toonTrack.append(ActorInterval(toon, d))

        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamageCheat, toon, dmg, died))
    else:
        splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamageCheat, toon, dmg, died))
    soundTrack = getSoundTrack('laff_loss.ogg', delay=delay + showDamageExtraTime, node=toon)
    toonTrack.append(Func(toon.loop, 'neutral'))
   # if toon.hp - dmg <= 0:
      #  suit = attack['suit']
       # toonTrack.append(Wait(3.0))
        #if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
           # suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
        #else:
         #   suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
    return Parallel(toonTrack, indicatorTrack, suitResponseTrack, soundTrack)


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
        rainEffect = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
        initialCloudHeight = suit.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(0.6))
        cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
        cloudPropTrack.append(Parallel(
            Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
            Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks.append(cloudPropTrack)
        if t['hp'] != 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
            puddleTracks.append(puddleTrack)
            notifyTrack = Sequence(Wait(damageDelay + 2), Func(toon.showHpString, "LIQUIDATED!"))
            notifyTracks.append(notifyTrack)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                             dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTracks, puddleTracks, cloudPropTracks, notifyTracks, soundTrack)

def doLiquidationEventDamage(attack):
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
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    for t in attack['target']:
        toon = t['toon']
        BattleParticles.loadParticles()
        cloud = globalPropPool.getProp('stormcloud')
        rainEffect = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
        initialCloudHeight = suit.height + 3
        cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
        cloudPropTrack = Sequence()
        cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
        cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
        cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
        cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack.append(Wait(0.6))
        cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
        cloudPropTrack.append(Parallel(
            Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=3.1, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
            Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=3.0, cleanup=True, softStopT=-1)),
            Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
        cloudPropTrack.append(Wait(0.4))
        cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
        cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
        cloudPropTracks.append(cloudPropTrack)
        if t['hp'] != 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
            puddleTracks.append(puddleTrack)
            notifyTrack = Sequence(Wait(damageDelay + 2), Func(toon.showHpString, "LIQUIDATED!"))
            notifyTracks.append(notifyTrack)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                             dodgeAnimNames=['sidestep'])
    return Parallel(toonTracks, puddleTracks, cloudPropTracks, soundTrack)

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
    suitTrack = Sequence(getSuitAnimTrack(attack))
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
                                                   Func(targetSuit.showHpString, "+ 1 ATTACK!"), Func(targetSuit.makeExtraAttacks, targetSuit.getExtraAttacks() + 1)), Func(targetSuit.setNeutralAnimation))
    return Parallel(suitTrack, moveTrack, selfDamageTrack)

def doTotalMarketMeltdown(attack):
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
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 3.9, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.9, [waterfallEffect, suit, 0], softStop=-2)
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
    if hitAtleastOneToon > 0:
        puddleCounter = 0
        for t in targets:
            toon = t['toon']
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
        suitTrack = Sequence(getSuitAnimTrack(attack))
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
    suitTrack = Sequence(getSuitAnimTrack(attack))
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
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(2.0))
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
        cage.setColorScale(0, 0.961, 1, 1)
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
            notifyTrack = Sequence(Wait(2.8), Func(toon.showHpTextNew, - int(dmg)))
            notifyTracks.append(notifyTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracksCheat(attack, damageDelay=1, splicedDamageAnims=damageAnims, dodgeDelay=.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 2.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, smokeTracks, toonTrack)

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


