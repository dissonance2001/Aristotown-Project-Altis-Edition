from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
import PlayByPlayText
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
    neutralTrack =  Func(suit.setNeutralAnimation())
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
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
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
    if suit.dna.name == 'scg' and suit.isAngry:
        track.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        track.append(Func(suit.loop, 'neutral-enraged'))
    elif suit.isImmortal and suit.dna.name == 'dsf':
        track.append(
            Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isVulnerable and suit.dna.name == 'crf':
        track.append(
            Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isImmortal:
        track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    else:
        track.append(
            Func(suit.setNeutralAnimation))

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
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
    if suit.dna.name == 'scg' and suit.isAngry:
        track.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        track.append(Func(suit.loop, 'neutral-enraged'))
    elif suit.isImmortal and suit.dna.name == 'dsf':
        track.append(
            Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isVulnerable and suit.dna.name == 'crf':
        track.append(
            Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isImmortal:
        track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    else:
        track.append(
            Func(suit.setNeutralAnimation))
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
     #   suit = attack['suit']
      #  toonTrack.append(Wait(3.0))
       # if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
            #suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
       # else:
          #  suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
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
     #   suit = attack['suit']
      #  toonTrack.append(Wait(3.0))
      #  if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
       #     suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
       # else:
          #  suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
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


def doDesperation(attack):
    suit = attack['suit']
    battle = attack['battle']
    notifyTracks = Sequence(Wait(0.5))
    cameraTracks = Sequence()
    makeDesperates = Parallel()
    makeDamageUps = Parallel()
    theSuit = None
    for s in battle.activeSuits:
        if not suit.isDesperation:
            if s.dna.name == 'ambass' and not suit.dna.name == 'ambass':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'wtapper' and not suit.dna.name == 'wtapper':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'bkeeper' and not suit.dna.name == 'bkeeper':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'phouse' and not suit.dna.name == 'phouse':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'radiog' and not suit.dna.name == 'radiog':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'racket' and not suit.dna.name == 'racket':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'ubuster' and not suit.dna.name == 'ubuster':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'safesupervis' and not suit.dna.name == 'safesupervis':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'stenog' and not suit.dna.name == 'stenog':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'lgator' and not suit.dna.name == 'lgator':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'sgoat' and not suit.dna.name == 'sgoat':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     ' +40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                           '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
            if s.dna.name == 'caseman' and not suit.dna.name == 'caseman':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpText2,
                                            'DESPERATION!',
                                            2), Func(theSuit.showHpStringDesperation,
                                                     '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                                            '+1 Lure Resistance'))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit

    return Sequence(notifyTracks, makeDamageUps, makeDesperates)

def doDesperation2(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    notifyTracks = Sequence(Wait(0.5))
    cameraTracks = Sequence()
    makeDesperates = Parallel()
    makeDamageUps = Parallel()
    notifyTrack = Sequence(Func(theSuit.showHpText2,
                                'DESPERATION!',
                                2), Func(theSuit.showHpStringDesperation,
                                         '+40% Damage'), Func(theSuit.showHpStringDesperation2,
                                                               '+1 Lure Resistance'))
    makeDesperate = Func(theSuit.makeDesperation)
    makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
    cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    makeDesperates.append(makeDesperate)
    makeDamageUps.append(makeDamageUp)
    return Sequence(notifyTracks, makeDamageUps, makeDesperates)

def doAbilityQueued(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    notifyTrack = Sequence(Func(theSuit.showHpStringAbility, "ABILITY QUEUED!"))
    cameraTrack = Wait(2.0)
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    return Sequence(notifyTracks)

def doAbsorbMovie(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    notifyTrack = Sequence(Func(theSuit.checkAbsorbDamage))
    cameraTrack = Wait(3.0)
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    return Sequence(notifyTracks)

def doSoakRemoval(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence()
    suitTrack.append(Parallel(ActorInterval(suit, 'soak', startTime=3.5), __soakRemoval(suit, 1)))
    return suitTrack

def doSueRemoval(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence()
    suitTrack.append(Parallel(ActorInterval(suit, 'soak', startTime=3.5), Func(battle.unSueSuit, suit)))
    suitTrack.append(Func(suit.removeSued))
    return suitTrack

def doSueApplication(attack):
    suit = attack['suit']
    battle = attack['battle']
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    splatName = 'dust'
    splat = globalPropPool.getProp('dust')
    explode = globalPropPool.getProp('dust')
    explode.setTwoSided(True)

    explode.setBillboardPointWorld(2)
    explodeTrack = Sequence()
    explodeTrack.append(
        getPropAppearTrack(explode, suit, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
    explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
    suitTrack = Sequence()
    suitTrack.append(Parallel(ActorInterval(suit, 'pie-small-react'), Func(battle.sueSuit, suit), Func(suit.showHpString, "CEASE AND DESIST!")))
    suitTrack.append(Func(suit.makeSued, 3))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('LB_receive_evidence.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, explodeTrack)

def doSueDamage(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    selfDamageTrack = Sequence(Func(suit.checkSueDamage, battle), Wait(3.0))
    return Parallel(selfDamageTrack)

def doDeathCheck(attack):
    name = attack['name']
    suit = attack['suit']
    battle = attack['battle']
    currentBossHealth = -1
    revives = suit.getSkeleRevives()
    suitTrack = Sequence()
    if suit.isVirtual:
        suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
    elif not suit.isSkeleton and revives >= 2:
        suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
    elif suit.isSkeleton and revives >= 2:
        suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
    elif suit.isSkeleton and revives >= 1 and not suit.isRevive:
        suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
    elif not suit.isSkeleton and revives >= 1:
        suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
    elif not suit.isVirtual:
        suitTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
    return suitTrack

def doSynergy(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 3.9, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.9, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doCourtCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimation), Wait(2.0))
    if suit.isDesperation:
        suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of litigation fees... Price index raised to %s." % int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    else:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Calculating costs of litigation fees... Price index raised to %s." %
                              int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg')
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doCourtRecord(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(1.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)