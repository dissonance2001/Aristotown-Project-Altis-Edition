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
    if suit.dna.name == 'sgoat' and suit.isAngry:
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
    if suit.dna.name == 'sgoat' and suit.isAngry:
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
                               LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
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
                               LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(1, 0, 0, 1)),
                               LerpColorScaleInterval(indicator, 0.5, Vec4(0, 0, 0, 0)),
                               Func(indicator.reparentTo, hidden), Func(indicator.clearColorScale),
                               Func(MovieUtil.removeProp, indicator))
    if dmg > 0:
        animTrack.append(getToonTakeDamageTrackCheat(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        #indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return animTrack


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
    if toon.hp - dmg <= 0:
        suit = attack['suit']
        toonTrack.append(Wait(3.0))
        if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
            suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
        else:
            suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
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
    if toon.hp - dmg <= 0:
        suit = attack['suit']
        toonTrack.append(Wait(3.0))
        if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
            suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
        else:
            suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
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
            #next.setScale(0.01)
            #next.reparentTo(suit.getRightHand())
          #  next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            if dmg > 0:
                notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextCheat, - int(dmg)),
                                       Func(toon.showHpString, "VULNERABLE!"))
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

def doAutoRepair(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']

    suitTracks = Parallel()
    suitTracks.append(getSuitAnimTrack(attack, playRate=1.5))
    healSounds = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence(Wait(2.0))
        healSound = getSoundTrack('SA_repair.ogg')
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpText, 0))
            suitTrack.append(Func(suit.showHpString, "REPAIRED!"))
        elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpTextCheat, x))
            suitTrack.append(Func(suit.showHpString, "REPAIRED!"))
            suitTrack.append(Func(suit.setHealthForMe, x))
        else:
            suitTrack.append(Func(suit.showHpTextCheat, 125))
            suitTrack.append(Func(suit.showHpString, "REPAIRED!"))
            suitTrack.append(Func(suit.setHealthForMe, 125))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTracks.append(suitTrack)
        healSounds.append(healSound)
    return Parallel(suitTracks, healSounds)


def doCeaseAndDesist(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(1.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doJuryNotice(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(1.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_jury_notice.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doSnap(attack, suit):
    #suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.45
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    suitTrack = getSuitTrack(attack)
    notifyTracks = Parallel()
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('litigator-teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            notifyTrack = Sequence(Wait(3.1), Func(toon.showHpTextCheat, - int(dmg)),
                                   Func(toon.showHpString, "VULNERABLE!"))
            notifyTracks.append(notifyTrack)
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.8)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.2, toonHeight * 0.9)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(8, 8, 8)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(14, 14, 14)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.1), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration), ActorInterval(teeth, 'litigator-teeth', duration=0.3), Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7), ActorInterval(teeth, 'litigator-teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
            propTracks.append(propTrack)

    damageAnims = [['cringe',
      0.01,
      0.7,
      1.2], ['conked',
      0.01,
      0.2,
      2.1], ['conked', 0.01, 3.2]]
    dodgeAnims = [['cringe',
      0.01,
      0.7,
      0.2], ['duck', 0.01, 1.6]]
    #soundTrack = getSoundTrack('SA_bite%s.ogg' % ('' if hitAtleastOneToon else '_miss'), delay=2, node=suit)
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    soundTrack = getSoundTrack('SA_bite.ogg', delay=2, node=suit)
    toonTracks = getToonTracksCheat(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.75,
                               dodgeAnimNames=['neutral'], showDamageExtraTime=1.4)
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks, notifyTracks)

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

def doBayouBellow(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, theSuit, Point3(0, 1.6, theSuit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, theSuit, 0], softStop=-3.5))
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.0))
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTrack.append(resetTrack)
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ActorInterval(suit, 'soak', startTime=3.5), __soakRemoval(suit, 1)))
        suitTrack.append(
            Func(suit.setNeutralAnimation))
        suitTracks.append(Wait(0.5))
        suitTracks.append(MovieUtil.createSuitBellowInterval(theSuit))
        suitTracks.append(Wait(4.0))
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.setNeutralAnimation))
    soundTrack = getSoundTrack('SA_bellow.ogg', delay=0.1)
    return Parallel(suitTracks, sprayTrack, soundTrack)

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
    if suit.style.name == 'lgator' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryLitigator))
    for bodyPart in suitBody:
        if bodyPart:
            suitInterval.append(Func(bodyPart.setColor, color))
        return suitInterval

def doBayouBash(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(MovieUtil.createSuitSnapInterval(suit), Func(suit.setNeutralAnimation))
    suitTrack2.append(Wait(1.25))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, suitTrack2, soundTrack)

def doCourtSanction(attack):
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
        Func(MovieUtil.removeProp, sanctioned),
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0, ['duck'])
    notifyTrack = Sequence(Wait(0.8), Func(toon.showHpTextCheat, - int(dmg)),
                           Func(toon.showHpString, "SANCTIONED!"))
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)


def doCourtSanctionBindings(attack):
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
            getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
            Func(MovieUtil.removeProp, sanctioned),
            Func(battle.movie.clearRenderProp, sanctioned))
        suitTrack = getSuitTrack(attack)
        soundTrack = getSoundTrack('SA_sanction.ogg', delay=.5, node=suit)
        notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextCheat, - int(dmg)), Func(toon.showHpString, "SANCTIONED!"))
        if dmg > 0:
            propTracks.append(propTrack)
            suitTracks.append(suitTrack)
            soundTracks.append(soundTrack)
            notifyTracks.append(notifyTrack)
    toonDamageTrack = getToonTracksCheat(attack, 0.8, ['conked'], 0, ['neutral'])
    return Parallel(suitTracks, toonTracks, toonDamageTrack, propTracks, soundTracks, notifyTracks)

def doGavelCourtRecord(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    toonTracks = Parallel()
    nothingTrack = Sequence(Wait(1.0))
    for t in targets:
        toon = t['toon']
        gavel = globalPropPool.getProp('LB_gavel')
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        gavelPos = Point3(toonPos.getX(), -17.5, 0)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpHprInterval(gavel, 0.5, VBase3(0, -90, 0)),
            Parallel(getSoundTrack('LB_gavel.ogg'), Sequence(
                Wait(0.1),
                LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
                LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
            ))
        )
        toonTrack = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),

            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened),
                    Func(toon.showHpText, -dmg, openEnded=0),
                    #Func(__doDamage, toon, dmg, t['died'])
                ),
                getSoundTrack('toon_decompress.ogg'),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
        if dmg > 0:
            propTracks.append(propTrack)
            toonTracks.append(toonTrack)
    toonDamageTrack = getToonTracksCheat(attack, 3.5, ['nothing'], 0, ['neutral'])
    return Parallel(toonTracks, toonDamageTrack, propTracks)

def doLegalBindings(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    tape = globalPropPool.getProp('redtape')
    tape.setColor(0.129, 0, 0.329, 1)
    tubes = []
    for i in xrange(0, 3):
        tubes.append(globalPropPool.getProp('redtape-tube'))
        tubes[i].setColor(0.129, 0, 0.329, 1)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = random.choice(
            ["Hmph...", "Hrnhmpf...",
             "Hrm...",
             "Hm, hm..."])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = getSuitTrack(attack, playRate=1.5)
    suitName = suit.getStyleName()
    tapePosPoints = [Point3(-0.25, 0, -0.25), VBase3(0, 0, 0)]
    tapeScaleUpPoint = Point3(1, 1, 0.74)
    propTrack = Sequence(
        getPropAppearTrack(tape, suit.getRightHand(), tapePosPoints, 0.25, tapeScaleUpPoint, scaleUpTime=0.25))
    propTrack.append(Wait(1.55))
    hitPoint = lambda toon=toon: __toonTorsoPoint(toon)
    propTrack.append(getPropThrowTrack(attack, tape, [hitPoint], [__toonGroundPoint(attack, toon, 0)], .25))
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
    toonTrack = Parallel(getToonTrackCheat(attack, 2.4, ['struggle'], 2.4, ['struggle']))
    toonTrack.append(Sequence(Wait(2.0), ActorInterval(toon, 'struggle')))
    notifyTrack = Sequence(Wait(2.4), Func(toon.showHpTextWhite, "LEGALLY BOUND!", 10))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.4, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, tubeTracks, notifyTrack)

def doCaseInsurance(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']

    suitTracks = Parallel()
    healSounds = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'sgoat':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
            if suit.isInsured:
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                elif suit.currHP + 85 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextCheat, x))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 85))
                else:
                    suitTrack.append(Func(suit.showHpTextCheat, 85))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 85))
                suitTrack.append(Func(suit.updateHealthBar, 0))
                suitTracks.append(suitTrack)
                healSounds.append(healSound)
        else:
            healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
            if suit.isInsured:
                if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpText, 0))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP):
                    suitTrack.append(Func(suit.showHpTextCheat, x))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, x))
                else:
                    suitTrack.append(Func(suit.showHpTextCheat, 50))
                    suitTrack.append(Func(suit.showHpString, "INSURANCE!"))
                    suitTrack.append(Func(suit.setHealthForMe, 50))
                suitTrack.append(Func(suit.updateHealthBar, 0))
                suitTracks.append(suitTrack)
                healSounds.append(healSound)
    return Parallel(suitTracks, healSounds)

def doLegallyBound(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    sprayEffects = [BattleParticles.createParticleEffect(file='spinSpray') for t in targets]
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
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
        spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffectBindings')
        spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffectBindings')
        spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffectBindings')
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
        notifyTrack = Sequence(Wait(damageDelay + 1.9), Func(toon.showHpText, - int(dmg)))
        if dmg > 0:
            spinTracks1.append(getPartTrack(spinEffect1, 1.5, 5.9, [spinEffect1, battle, 0], softStop=-2))
            spinTracks2.append(getPartTrack(spinEffect2, 1.5, 5.9, [spinEffect2, battle, 0], softStop=-2))
            spinTracks3.append(getPartTrack(spinEffect3, 1.5, 5.9, [spinEffect3, battle, 0], softStop=-2))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0))
            soundTracks.append(getSoundTrack('LB_boss_paper_spin.ogg', delay=2.0))
            notifyTracks.append(notifyTrack)
            toonSpinTracks.append(Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=damageDelay + 0.9, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['neutral'], showDamageExtraTime=1.0)
    return Parallel(toonTracks, toonSpinTracks, toonDamageTrack, spinTracks1, spinTracks2, spinTracks3, notifyTracks, soundTracks)

def doCaseInsurancePlanInsurance(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    if attack['suitName'] == 'caseman':
        taunt = 'Hrm...'
    elif attack['suitName'] == 'fbd':
        taunt = 'Hrm...'
    else:
        taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)

    suitTracks = Parallel()
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        suitTrack.append(Func(suit.showHpTextWhite, "INSURANCE!", 0))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'caseman':
            suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(suit.makeInsured))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(MovieUtil.createSuitInsuranceInterval(theSuit))
        suitTracks.append(Wait(6.5))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = globalPropPool.getProp('shredder-paper')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(1, 1, 1),
                               scaleUpTime=0.1),
            Wait(2.3),
            Parallel(
                getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                LerpHprInterval(knife, 0.8, VBase3(0, -20, -20))),
            Parallel(LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                     Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    suitTrack = Sequence(Wait(6.0), Func(suit.setNeutralAnimation))
    #insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
    soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg')))
    return Parallel(suitTrack, suitTracks, healSound, multiTrack, knifeTracks)

def doCaseInsurancePlanSkelecogInsurance(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    if attack['suitName'] == 'caseman':
        taunt = random.choice(
            ["Hmph...", "Hrnhmpf...",
             "Hrm...",
             "Hm, hm..."])
    elif attack['suitName'] == 'fbd':
        taunt = 'Hrm...'
    else:
        taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)

    suitTracks = Parallel()
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        suitTrack.append(Func(suit.showHpTextWhite, "INSURANCE!", 0))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'caseman':
            suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(suit.makeInsured))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
        suitTracks.append(Wait(6.5))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = globalPropPool.getProp('shredder-paper')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(1, 1, 1),
                               scaleUpTime=0.1),
            Wait(2.3),
            Parallel(
                getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                LerpHprInterval(knife, 0.8, VBase3(0, -20, -20))),
            Parallel(LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                     Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    suitTrack = Sequence(Wait(6.0), Func(suit.setNeutralAnimation))
    #insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
    #soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    multiTrack = soundTrack2
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg')))
    return Parallel(suitTrack, suitTracks, healSound, multiTrack, knifeTracks)

def doEnraged(attack):
    suit = attack['suit']
    soundTrack = getSoundTrack('SA_rage.ogg', node=suit)
    makeEnraged = Func(suit.makeAngry)
    suitTrack = getSuitAnimTrack(attack)
    suitTrack.append(Wait(2.0))
    headInterval = Sequence(MovieUtil.createSuitEnragedInterval(suit, 0))
    return Parallel(suitTrack, soundTrack, headInterval, makeEnraged)

def doShieldsUp(attack):
    suit = attack['suit']
    soundTrack = getSoundTrack('SA_defense.ogg', node=suit)
    suitTrack = getSuitAnimTrack(attack)
    suitTrack.append(Wait(2.0))
    makeShielding = Func(suit.makeShielding)
    return Parallel(suitTrack, soundTrack, makeShielding)

def doBarnyardBash(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    dmg = (attack['target'][0]['hp']) * len(battle.activeToons)
    selfDamageTrack = Sequence(Wait(1.5), Func(suit.showHpText, +dmg), Func(suit.setHealthForMe, dmg), Func(suit.updateHealthBar, 0))
    tauntInterval = Func(suit.setChatAbsolute, 'Is this the best you Toons can do?', CFSpeech | CFTimeout)
    suitTrack = getSuitTrack(attack)
    makeShielding = Func(suit.makeShielding)
    soundTrack2 = getSoundTrack('SA_defense.ogg', delay=0, node=suit)
    soundTrack3 = getSoundTrack('LB_toonup.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, soundTrack2, soundTrack3, selfDamageTrack, makeShielding)

def __makeSanctionedNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText('SANCTIONED\nSANCTIONED\nSANCTIONED')
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

def doGavel(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    dmg = target[0]['hp']
    gavel = globalPropPool.getProp('LB_gavel')
    toonPos = toon.getPos(battle)
    initialScale = toon.getScale()
    gavelPos = Point3(toonPos.getX(), 0, 0)
    propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0, scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
        Parallel(getSoundTrack('LB_gavel.ogg'), Sequence(
            Wait(0.1),
            LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
            LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
        ))
    )
    taunt = "Any gags Toons use can and will be held against them in a court of law."
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = getSuitTrack(attack)
    toonTrack = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, 0, openEnded=0),
                Func(__doDamage, toon, 0, target[0]['died'])
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),
                getSoundTrack('toon_decompress.ogg'),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
    return Parallel(suitTrack, toonTrack, propTrack)