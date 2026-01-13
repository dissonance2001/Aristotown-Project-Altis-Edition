from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
import PlayByPlayText
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
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'RacketeerPeckingOrderRetaliationSoak':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyHeatWave':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyViolation':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
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
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack[
        'name'] == 'RacketeerPeckingOrderRetaliationSoak':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyHeatWave':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyViolation':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'RacketeerPeckingOrderRetaliation':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
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
        partTracks.append(getPartTrack(particleEffects[i], startDelay, durationDelay, [particleEffects[i], battle, worldRelative]), softStop)

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
           # suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
       # else:
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
     #   suit = attack['suit']
      #  toonTrack.append(Wait(3.0))
       # if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
          #  suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
       # else:
            #suitResponseTrack.append(Parallel(Sequence(Wait(delay + showDamageExtraTime), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
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

def doHighPressure(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitAnimTrack(attack, playRate=2.0)
        suitTrack.append(Wait(1.75))
        suitTrack.append(Func(suit.showHpTextNew, - int(50 * len(battle.activeToons)), text="OVERWORKED!", colorCode=3))
        suitTrack.append(Func(suit.setHealthForMe, - (50 * len(battle.activeToons))))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Parallel(Func(suit.checkCogHPBomb, battle), ActorInterval(suit, 'slip-backward')))
        suitTracks.append(suitTrack)
        revives = suit.getMaxSkeleRevives() + 1
        suitTrack.append(Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.4109589, -0.0821917, -0.0821917), VBase3(-10.849315, 0, 113.42465753424653)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(4.0))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)
    gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
    explosionTrack2 = Sequence()
    explosionTrack2.append(Wait(4.0))
    explosionTrack2.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint2, scale=3))
    for t in targets:
        toon = t['toon']
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
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)

    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('incoming_whistle.ogg', delay=2.0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=1.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=4.0)
    return Parallel(suitTracks, knifeTracks, toonTracks, soundTrack, soundTrack1, soundTrack2, explosionTrack, explosionTrack2)

def doHeatWaveCalculation(attack):
    BattleParticles.loadParticles()
    suit = attack['suit']
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
    suitSpeechTrack = Func(suit.setChatAbsolute, "Under pressure, things get hot fast... this battlefield now burns at %s degrees and climbing." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    return Parallel(suitTrack, suitSpeechTrack, baseFlameTrack, suitColorTrack, flameTrack, flecksTrack, soundTrack)

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
    suitTrack = Parallel(getSuitTrack(attack), MovieUtil.createSuitFirestarterCigarSmokeInterval2(suit))
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
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        BattleParticles.loadParticles()
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
            notifyTracks.append(notifyTrack)
            propTracks.append(propTrack)
            flameTracks.append(flameTrack)
            explosionTracksGroup.append(explosionTrack)
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=5.45)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack2 = getSoundTrack('SA_boilerplate_a.ogg', delay=0.5, node=suit)
    suitHeadAnimTrack = MovieUtil.createSuitFirestarterCigarSmokeInterval2(suit)
    toonTrack = getToonTracks(attack, 5.45, ['slip-forward'], 3.4, ['struggle'])
    suitAnimTrack = Sequence(Parallel(ActorInterval(suit, 'throw-object', duration=1.5, playRate=1.5)), Wait(3.175),
                         ActorInterval(suit, 'throw-object', startTime=1.5, playRate=1.5), Func(suit.setNeutralAnimationDrop))
    return Parallel(explosionTracksGroup, suitHeadAnimTrack, flameTracks, soundTrack2, suitAnimTrack, suitTrack, toonTrack, soundTrack, propTracks, notifyTracks)

def doHeatWave(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    damageDelay = 1.7
    particleEffect = BattleParticles.createParticleEffect(file='heatwave')
    waterfallEffect = BattleParticles.createParticleEffect(file='heatwaveWaterfall')
    node = suit.getGeomNode().getChild(0)
    suitTrack = Sequence(Parallel(Parallel(LerpColorScaleInterval(node, duration=3, colorScale=(1, 0, 0, 1),
                                    blendType='easeInOut')), getSuitAnimTrack(attack),  MovieUtil.createSuitFirestarterCigarSmokeInterval2(suit)))
    dmg = attack['target'][0]['hp']
    baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
    flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
    flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
    baseFlameTrack2 = getPartTrack(baseFlameEffect, 1, 4.9, [baseFlameEffect, suit, 0], softStop=-1)
    flameTrack2 = getPartTrack(flameEffect, 1, 4.9, [flameEffect, suit, 0], softStop=-1)
    flecksTrack2 = getPartTrack(flecksEffect, 1, 4.9, [flecksEffect, suit, 0], softStop=-1)
    suitDamageTrack = Sequence(Wait(4.0),
                         Func(suit.updateHealthBar, 0), Parallel(Func(suit.setNeutralAnimationDrop)))
    partTrack = getPartTrack(particleEffect, 1.0, 3.9, [particleEffect, suit, 0], softStop=-2.0)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.9, [waterfallEffect, suit, 0], softStop=-2.0)
    partTrack2 = getPartTrack(particleEffect, 1.0, 3.9, [particleEffect, suit, 0])
    waterfallTrack2 = getPartTrack(waterfallEffect, 0.8, 3.9, [waterfallEffect, suit, 0], softStop=-2.0)
    baseFlameTracks = Parallel()
    flameTracks = Parallel()
    flecksTracks = Parallel()

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
        BattleParticles.loadParticles()
        sprayEffect = BattleParticles.createParticleEffect('HotAir')
        baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame2')
        flameEffect = BattleParticles.createParticleEffect('FiredFlame2')
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
    return Parallel(suitTrack, partTrack, suitDamageTrack, waterfallTrack, partTrack2, baseFlameTrack2, flameTrack2, flecksTrack2, waterfallTrack2, toonTracks, soundTrack, baseFlameTracks, flameTracks, flecksTracks, colorTracks)

def doPromotion(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[ind]
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
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    targetPos = targetSuit.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    headsUp2 = Func(suit.setHpr, battle, origHpr)
    cage = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_promoted')
    toonPos = toon.getPos(battle)
    suitPos = targetSuit.getPos(battle)
    y = suitPos.getY()
    cagePos = [Point3(suitPos.getX(), y, 0), VBase3(0, 0, 0)]
    dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
    dustCloud.setBillboardAxis(2.0)
    dustCloud.setZ(3)
    dustCloud.setScale(0.4)
    dustCloud.createTrack()
    dustCloudHideIval = Sequence(Func(dustCloud.reparentTo, suit), Func(dustCloud.setPos,
                                                                        Point3(suitPos.getX(), 0,
                                                                               0)),
                                 dustCloud.track, Func(dustCloud.detachNode), Wait(1.7), name='dustCloadIval')
    moveTrack = Sequence(LerpPosInterval(suit, suit.getDuration('walk'), sinkPos2, other=battle), Wait(suit.getDuration('magic3')), LerpPosInterval(suit, suit.getDuration('walk'), dropPos, other=battle), Func(suit.setPos, battle, resetPos))
    suitTrack = Sequence(ActorInterval(suit, 'walk'), headsUp, getSuitAnimTrack(attack), ActorInterval(suit, 'walk'), headsUp2, Func(suit.setNeutralAnimation))
    selfDamageTrack = Sequence(Wait(5.0), Parallel(dustCloudHideIval, ActorInterval(targetSuit, 'slip-forward', startTime=2.43),
                                                   Func(targetSuit.makeIntoCTSManager),
                                                   Func(targetSuit.showHpString, "PROMOTION!"), Func(targetSuit.setMaxHP, 1000), Func(targetSuit.setManager, 1), Func(targetSuit.makeShielding),
                                                   Func(targetSuit.updateHealthBar, 0)),
                               Func(targetSuit.setNeutralAnimation), Func(battle.unSueSuit, targetSuit))
    soundTrack = getSoundTrack('SA_boilerplate_a.ogg', delay=2.5, node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=5.0)
    return Parallel(baseFlameSmallTrack, flecksTrack, flameTrack, partTrack4, baseFlameTrack, suitTrack, moveTrack, selfDamageTrack, soundTrack2, flecksSmallTrack, flameSmallTrack, soundTrack)

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
                                 Func(MovieUtil.removeProp, cage)
                                 )
        toonTrack = Sequence(
        Wait(2.5),
        Parallel(
            Func(toon.enterFlattened),
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
    if suit.isDesperation:
        suitSpeechTrack = Func(suit.setChatAbsolute, "You can't stop production; Union Dues have been increased to %s." % int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    else:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                               "You can't stop production; Union Dues have been increased to %s." %
                              int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg')
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doUnionBuster(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
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
    smokeTrack = Sequence(Wait(0.6), Func(smoke.reparentTo, toon), Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                   LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                          Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale), Func(MovieUtil.removeProp, smoke))
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0, scaleUpPoint=Point3(1.75), scaleUpTime=0), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.01), blendType='easeIn')),
                SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0)
            ,
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0), cage.posInterval(3, Point3(toonPos.getX(), y, 40), blendType='easeIn'),
            Func(MovieUtil.removeProp, cage)
        )
    toonTrack = Sequence(
        Wait(.6),
        Parallel(
            Func(toon.enterFlattened),
        ),
        Wait(2.5),
        Parallel(Func(toon.showHpTextNew, -int(dmg), text="BUSTED!", colorCode=4),
            Func(__doDamageCheat, toon, dmg, target[0]['died']),
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
    cagePropTracks.append(cagePropTrack)
    return Parallel(suitTrack, cagePropTracks, smokeTrack, toonTrack)

def doUnionBusterDamage(attack):
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
                          Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale), Func(MovieUtil.removeProp, smoke))
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0, scaleUpPoint=Point3(1.75), scaleUpTime=0), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.01), blendType='easeIn')),
                SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0)
            ,
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0), cage.posInterval(3, Point3(toonPos.getX(), y, 40), blendType='easeIn'),
            Func(MovieUtil.removeProp, cage)
        )
        toonTrack = Sequence(
        Wait(.5),
        Parallel(
            Func(toon.enterFlattened),
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
    managerTrack = Sequence(getSuitAnimTrack(attack))
    suitTracks = Parallel()
    selfDamageTracks = Parallel()
    cagePropTracks = Parallel()
    smokeTracks = Parallel()
    for targetSuit in battle.activeSuits:
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        suitTrack = Sequence(Wait(2), Parallel(ActorInterval(targetSuit, 'flatten', duration = .55), MovieUtil.createSuitCrashTrack(targetSuit, battle)))
        selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpTextNew, -targetSuit.currHP, text="BUSTED!", colorCode=3),
                                   Func(targetSuit.setHealthForMe, - targetSuit.currHP),
                                   Func(targetSuit.updateHealthBar, 0))
        smokeTrack = Sequence(Wait(2.0), Func(smoke.reparentTo, targetSuit),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale), Func(MovieUtil.removeProp, smoke))
        cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
        cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))
        shaft = cage.find('**/shaft')
        shaft.setScale(0.75, 120.0, 0.75)
        shaft.setPos(0, 0, 0)
        targetSuitPos = targetSuit.getPos(battle)
        y = targetSuitPos.getY()
        cagePos = [Point3(targetSuitPos.getX(), y, 40.0), targetSuit.getHpr(battle)]
        cagePropTrack = Sequence(Wait(1.6),
        getPropAppearTrack(cage, battle, cagePos, 0, scaleUpPoint=Point3(1.4), scaleUpTime=0),
        Parallel(cagePosition),
        Parallel(
            cage.posInterval(0.5, Point3(targetSuitPos.getX(), y, 0.01), blendType='easeIn')),
            SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0),
        Wait(1.5),
        LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0), cage.posInterval(3, Point3(targetSuitPos.getX(), y, 40), blendType='easeIn'),
        Func(MovieUtil.removeProp, cage)
    )
        if not targetSuit.isContracted and not targetSuit.dna.name == 'ubuster':
            cagePropTracks.append(cagePropTrack)
            suitTracks.append(suitTrack)
            selfDamageTracks.append(selfDamageTrack)
            smokeTracks.append(smokeTrack)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_quake.ogg'), node=manager))
    return Parallel(managerTrack, suitTracks, cagePropTracks, soundTrack, smokeTracks, selfDamageTracks)

def doUnionWages(attack):
    targetSuit = attack['suit']
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    damageDelay = 1.7
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitType = getSuitBodyType(attack['suitName'])
    damageSuits = []
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
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
    for targetSuit in battle.activeSuits:
        if not targetSuit.isContracted and not targetSuit.dna.name == 'ubuster':
            damageSuits.append(targetSuit)
    makeImmune = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, +  (5 * len(damageSuits))))
    managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextCheat, + (100 * len(damageSuits))),
                                Func(suit.showHpString, "+%s" % (5 * len(damageSuits)) + "%" + " Damage!"), Func(suit.setHealthForMe, + (100 * len(damageSuits))),
                                Func(suit.updateHealthBar, 0))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.0, node=suit)
    return Parallel(suitTrack, calcPropTrack, sprayTrack, soundTrack, makeImmune, managerHealTrack, soundTrack2, spinTrack1, spinTrack2, spinTrack3)

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
        Func(sanctioned.setScale, 3.5),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(MovieUtil.removeProp, sanctioned),
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="BREACHED!", colorCode=1))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doBreachOfContractGroup(attack):
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
        targetPos = toon.getPos(battle)
        origPos, origHpr = battle.getActorPosHpr(suit)
        sanctioned = loader.loadModel('phase_5/models/props/ttrpg_m_ene_prp_deniedSign')
        missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
        propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 3.5),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(MovieUtil.removeProp, sanctioned),
        Func(battle.movie.clearRenderProp, sanctioned))
        suitTrack = getSuitTrack(attack)
        soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
        notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="BREACHED!", colorCode=1))
        if dmg > 0:
            headsUp = Func(suit.headsUp, battle, targetPos)
            propTracks.append(propTrack)
            suitTracks.append(Sequence(Parallel(suitTrack, headsUp), Func(suit.setHpr, battle, origHpr)))
            soundTracks.append(soundTrack)
            notifyTracks.append(notifyTrack)
    toonDamageTrack = getToonTracksCheat(attack, 0.8, ['conked'], 0, ['neutral'])
    return Parallel(suitTracks, toonTracks, propTracks, soundTracks, toonDamageTrack, notifyTracks)

def doContractEnforcement(attack):
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
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'safesupervis':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            suitTrack.append(Func(suit.checkContractEnforcementSafety))
            suitTrack.append(Func(suit.makeContracted))
            suitTracks.append(suitTrack)
        else:
            suitTrack.append(Func(suit.checkContractEnforcement))
            suitTrack.append(Func(suit.makeContracted))
            suitTracks.append(suitTrack)
        if not suit.dna.name == 'ubuster':
            suitTrack.append(Parallel(healSound, Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                           CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(battle.unSueSuit, suit))
        suitTracks.append(Sequence(getSuitAnimTrack(attack, playRate=1.5), Func(suit.setNeutralAnimation)))
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
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, 0.75, VBase3(1.2, 1.2, 1.2),
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

def doProfiteering(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[ind]
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    selfDamageTrack = Sequence(Wait(2.0), Func(targetSuit.checkProfiteering, suit, battle), Wait(4.0))
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
        partTrack4 = getPartTrack(sprayEffect, 4, 3.0, [sprayEffect2, toon, 0], softStop=-1)
        partTracks4.append(partTrack4)
        toonAnimTrack = Sequence(Wait(4), ActorInterval(toon, 'slip-forward', playRate=.5))
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
    multiTrackList.append(soundTrack)
    return multiTrackList

def __makeBudgetNodePath():
    tn = TextNode('BUDGET CUTS')
    tn.setFont(getSuitFont())
    tn.setText('MANDATORY\nCOMPLIANCE\nRESTRICTIONS')
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
    stampPosPoints = [Point3(-0.08219178082191902, -0.7397260273972606, -0.125), VBase3(90, 0, 90)]
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        cancelled = __makeBudgetNodePath()
        missPoint = lambda cancelled = cancelled, toon = toon: __toonMissPoint(cancelled, toon)
        propTrack = Sequence(Func(__showProp, stamp, suit.getRightHand(), stampPosPoints[0], stampPosPoints[1]), LerpScaleInterval(stamp, 0.5, Point3(1.2, 1.2, 1.2)), Wait(2.6), Func(battle.movie.needRestoreRenderProp, cancelled), Func(cancelled.reparentTo, render), Func(cancelled.setScale, 0.6), Func(cancelled.setPosHpr, stamp, 0.81, -1.11, -0.16, 0, 0, 90), Func(cancelled.setP, 0), Func(cancelled.setR, 0))
        propTrack.append(getPropThrowTrack(attack, cancelled, [__toonFacePoint(toon)], [__toonFacePoint(toon)]))
        propTrack.append(Func(MovieUtil.removeProp, cancelled))
        propTrack.append(Func(battle.movie.clearRenderProp, cancelled))
        propTrack.append(Wait(0.3))
        propTrack.append(LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, stamp))
        toonTrack = Parallel(getToonTrackCheat(attack, 3.25, ['conked'], 3.1, ['conked']))
        toonTrack.append(Sequence(Wait(3.25), ActorInterval(toon, 'conked')))
        notifyTrack = Sequence(Wait(3.25))
        propTracks.append(propTrack)
        toonTracks.append(toonTrack)
        notifyTracks.append(notifyTrack)
    soundTrack = getSoundTrack('SA_rubber_stamp.ogg', delay=0.5, node=suit)
    #soundTrack2 = getSoundTrack('SA_rubber_stamp.ogg', delay=3.25, node=suit)
    return Parallel(suitTrack, toonTracks, suitTrack2, notifyTracks, propTracks, padPropTrack, soundTrack)

def doExtortion2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    partTracks4 = Parallel()
    selfDamageTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    notifyTracks = Parallel()
    toonAnimTracks = Parallel()
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
        partTrack4 = getPartTrack(sprayEffect, 4, 3.0, [sprayEffect2, toon, 0], softStop=-1)
        toonAnimTrack = Sequence(Wait(4), ActorInterval(toon, 'slip-forward', playRate=.5))
        notifyTrack = Sequence(Wait(4), Func(toon.showHpText, - int(dmg)))
        if dmg > 0:
            partTracks4.append(partTrack4)
            toonAnimTracks.append(toonAnimTrack)
            notifyTracks.append(notifyTrack)
            toonAnimTracks.append(toonAnimTrack)
            partTracks4.append(partTrack4)
    toonTrack = getToonTracksCheat(attack, 4, ['nothing'], 0, ['neutral'])
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack = getSoundTrack('SA_gains_from_the_scrap.ogg', delay=0, node=suit)
    multiTrackList = Parallel(suitTrack, toonAnimTracks, toonTrack, notifyTracks, soundTrack, selfDamageTracks, partTracks4)
    return multiTrackList

def doRacketeering(attack):
    suit = attack['suit']
    suitTrack = Parallel(getSuitAnimTrack(attack), Sequence(ActorInterval(suit, 'smile'),
                                                            Func(suit.setNeutralAnimationDrop)))
    suitTrack.append(Wait(3.0))
    soundTrack = getSoundTrack('SA_rush_job_target.ogg', node=suit)
    return Parallel(suitTrack, soundTrack)

def doHustling(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(3.0))
    soundTrack = getSoundTrack('SA_rush_job_target.ogg', node=suit)
    return Parallel(suitTrack, soundTrack)

def doCompensation(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel(getSuitAnimTrack(attack), Sequence(ActorInterval(suit, 'sacrifice-cog', endTime=.75), ActorInterval(suit, 'sacrifice-cog', startTime=1.5, endTime=0, playRate=0.5),
                          Func(suit.setNeutralAnimationDrop)))
    suitTracks.append(Wait(5.0))
    soundTrack = getSoundTrack('SA_rush_job_target.ogg', node=suit)
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    for suit in battle.activeSuits:
        suitTrack = Parallel()
        if not suit.dna.name == 'racket':
            suitTrack.append(Sequence(Parallel(Func(suit.checkCompensation), healSound)))
            suitTracks.append(suitTrack)
    return Parallel(suitTracks, soundTrack)

def doPeckingOrderGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDuration = 3.03
    throwDelay = 2
    suitTracks = Parallel()
    soundTracks = Parallel()
    notifyTracks = Parallel()
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    propDelay = 1.5
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
        for i in xrange(0, numBirds):
            next = globalPropPool.getProp('bird')
            #next.setScale(0.01)
           # next.reparentTo(suit.getRightHand())
            #next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            if dmg > 0:
                hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6, random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            else:
                hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
            birdTrack = Sequence(Wait(throwDelay), Func(next.setScale, 0.01),
                                 Func(next.reparentTo, suit.getRightHand()),
                                 Func(next.setPos, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3,
                                      random.random() * 0.6 - 0.3), Func(battle.movie.needRestoreRenderProp, next),
                                 Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)),
                                 LerpPosInterval(next, 0.5, hitPoint))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.5, Point3(9, 9, 9)), LerpScaleInterval(next, .5, Point3(0, 0, 0)))
            if dmg > 0:
                birdTracks.append(Sequence(Parallel(birdTrack, scaleTrack), Func(MovieUtil.removeProp, next)))
        suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
        notifyTrack = Sequence(Wait(2.5), Func(toon.showHpText, - int(dmg)))
        if dmg > 0:
            soundTracks.append(soundTrack)
            suitTracks.append(suitTrack)
            notifyTracks.append(notifyTrack)
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
    toonTrack = getToonTracksCheat(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['neutral'], showMissedExtraTime=1.1)
    return Parallel(suitTracks, toonTrack, soundTracks, notifyTracks, birdTracks)

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
    for headPart in suit.animatedHeadParts:
        head = headPart
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence(Wait(1.5))
    makeDanceSession = Parallel(Func(suit.makeUnDamageDown), Func(suit.checkDamageDown, - 30), Func(suit.removeDanceSession))
    makeImmune = Parallel(Func(suit.makeUnDamageReduction), Func(suit.checkDamageReduction, - 30))
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    suitTrack = Sequence(ActorInterval(suit, 'glower', duration=1.5), Wait(4.0),
                         ActorInterval(suit, 'glower', startTime=1.5), Func(suit.setNeutralAnimation))
    suitTrack2 = getSuitAnimTrack(attack)
    soundTrack = getSoundTrack('mus_dialup_0.ogg', delay=1.5)
    return Parallel(suitTrack, soundTrack, makeImmune, makeDanceSession, suitTrack2, sprayTrack)

def doDanceSession(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    makeDanceSession = Parallel(Func(suit.makeDamageDown), Func(suit.checkDamageDown, + 30), Func(suit.makeDanceSession))
    makeImmune = Parallel(Func(suit.makeDamageReduction), Func(suit.checkDamageReduction, + 30))
    suitTrack = getSuitAnimTrack(attack)
    toonTracks = getToonTracks(attack, 4.1, ['victory'], 4.1, ['victory'])
    soundTrack = getSoundTrack('AA_heal_happydance.ogg', delay=.01, node=suit)
    return Parallel(suitTrack, soundTrack, toonTracks, makeImmune, makeDanceSession)

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
    notifyTrack = Sequence(Wait(2.25), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=3))
    return Parallel(explodeTracks, suitTrack, toonTrack, notifyTrack, soundTrack, propTrack, explosionTrack, explosionTrack2)

def doOvermodulated(attack, ind):
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
    moveTrack = Sequence(LerpPosInterval(suit, suit.getDuration('walk'), sinkPos2, other=battle), Wait(suit.getDuration('sanction')), LerpPosInterval(suit, suit.getDuration('walk'), dropPos, other=battle), Func(suit.setPos, battle, resetPos))
    suitTrack = Sequence(ActorInterval(suit, 'walk'), headsUp, getSuitAnimTrack(attack), ActorInterval(suit, 'walk'), headsUp2, Func(suit.setNeutralAnimation))
    selfDamageTrack = Sequence(Wait(suit.getDuration('walk') + .5), Parallel(ActorInterval(targetSuit, 'slip-backward'),
                                                   Func(targetSuit.showHpString, "+ 1 ATTACK!"), Func(targetSuit.makeExtraAttacks, targetSuit.getExtraAttacks() + 1)), Func(targetSuit.setNeutralAnimation))
    soundTrack = getSoundTrack('SA_haymaker.ogg', delay=suit.getDuration('walk') + .5)
    soundTrack1 = getSoundTrack('SA_sanction.ogg', delay=suit.getDuration('walk'), node=suit)
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
                        LerpPosInterval(suit, duration=1.0, pos=(newPos), other=battle),
                        ActorInterval(suit, 'walk', loop=1, playRate=-1, duration=1.0)),
                    Parallel(
                        Sequence(
                            getSuitTrack(attack),
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

    moveUp = Sequence(Parallel(LerpPosInterval(suit, duration=1.0, pos=(oldPos), other=battle), ActorInterval(suit, 'walk', loop=1, duration=1.0)),
                      Func(suit.setNeutralAnimationDrop))
    notifyTrack = Sequence(Wait(tPieHitsSuit), Func(toon.showHpTextNew,  - int(hp), "CONFUSED!", colorCode=1))
    toonTrack = getToonTrackCheat(attack, tPieHitsSuit, ['slip-backward'], tSuitDodges, ['sidestep'])
    soundTrack2 = getSoundTrack('SA_hot_air.ogg', delay=2.0, node=suit)
    return Sequence(Parallel(suitTrack, soundTrack2, partTrack4), Parallel(evilToonTrack, soundTrack, pieTrack, notifyTrack, toonTrack), moveUp)

