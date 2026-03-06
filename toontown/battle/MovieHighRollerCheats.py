from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.effects import Splash
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
from toontown.suit.DistributedLawbotBoss import DistributedLawbotBoss
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
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
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

    # Normalize difference to shortest path
    delta = (targetH - origH + 180) % 360 - 180

    if attack['suitName'] == 'hho' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'fires' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
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
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'HighRollerBust':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'HighRollerDiceRouletteEveryone':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'HighRollerDiceRouletteCogs':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'HighRollerGameTimeSpawn':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'HighRollerCommercialBreak':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'HighRollerDiceRouletteNobody':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'HighRollerDiceRouletteToons':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'BroadcasterDonation':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
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
    #elif suit.isVulnerable and suit.dna.name == 'crf':
    #    track.append(
     #       Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
   # elif suit.isImmortal:
    #    track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
      #  track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    if not attack['name'] == 'BroadcasterDonation':
        track.append(
            Func(suit.setNeutralAnimationDrop))
    return track

def getSuitAnimTrackHighRoller(attack, delay = 0, splicedAnims = None, playRate = 1.0):
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
       # track.append(
        #    Func(suit.setNeutralAnimation))
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
    origPos, origHpr = battle.getActorPosHpr(suit)
    origHpr = battle.getActorPosHpr(suit)[1]
    origPos2 = suit.getPos(battle)
    for i in xrange(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        origHpr = battle.getActorPosHpr(suit)[1] # We only want the rotation.
        suit.setPos(battle, origPos)
        particleEffects[i].reparentTo(suit) # Reparent the particle effect to the Cog.
        suit.headsUp(battle, toon.getPos(battle)) # Briefly turn the Cog to the Toon.
        particleEffects[i].wrtReparentTo(battle) # Drop the particle effect.
        partTracks.append(getPartTrack(particleEffects[i], startDelay, durationDelay, [particleEffects[i], battle, worldRelative], softStop))

    suit.setHpr(battle, origHpr) # After all that, set the Cog back like nothing ever happened.
    suit.setPos(battle, origPos2)
    return partTracks


def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    battle = attack['battle']
    suit = attack['suit']
    if suit:
        suitPos, suitHpr = battle.getActorPosHpr(suit)
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
    if suit:
        suitPos, suitHpr = battle.getActorPosHpr(suit)
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
        animTrack.append(getToonTakeDamageTrackCheat(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        #indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
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

def doPuzzleBan(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(1.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doPuzzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonTrack = Parallel(Func(toon.makeGagBan))
        notifyTracks.append(toonTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(3.0))
    return Parallel(suitTrack, notifyTracks)

def doGameOver(attack):
    suit = attack['suit']
    battle = attack['battle']
    soundTrack3 = getSoundTrack('cc_s_bgm_ara_hroller_int_stinger.ogg', node=suit)
    suitTrack = Sequence(Parallel(getSuitAnimTrack(attack), soundTrack3, Sequence(Wait(4.0), Func(suit.setChatAbsolute, "Ha-HA!", CFSpeech | CFTimeout))))
    suitTrack.append(Wait(1.0))
    toonTracks = getToonTracks(attack, 5.0, ['cringe'], 5.0, ['victory'])
    return Parallel(suitTrack, toonTracks)

def doDonation2(attack):
    suit = attack['suit']
    battle = attack['battle']
    notifyTracks = Parallel()
    cameraTracks = Sequence()
    makeDesperates = Parallel()
    makeDamageUps = Parallel()
    headTracks = Parallel()
    theSuit = None
    for headPart in suit.animatedHeadParts:
        headTrack = Sequence()
        headTrack.append(Wait(1))
        headTrack.append(Func(headPart.loop, 'stun'))
        texture2 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer5.png')
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
        headTrack.append(Func(headPart.setTexture, texture2, 1))
        headTrack.append(Wait(5.0))
        headTrack.append(Func(headPart.setTexture, texture, 1))
        headTrack.append(Func(headPart.loop, 'neutral'))
        headTracks.append(headTrack)
    soundTrack = getSoundTrack('mus_dialup_0.ogg')
    for s in battle.activeSuits:
        if s.dna.name == 'videog' and not suit.dna.name == 'videog':
            theSuit = s
            texture2 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer5.png')
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            headTrack = Sequence()
            for headPart in s.animatedHeadParts:
                headTrack.append(Wait(1))
                headTrack.append(Func(headPart.loop, 'stun'))
                texture2 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer5.png')
                texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
                headTrack.append(Func(headPart.setTexture, texture2, 1))
                headTrack.append(Wait(5.0))
                headTrack.append(Func(headPart.setTexture, texture, 1))
                headTrack.append(Func(headPart.loop, 'neutral'))
            headTracks.append(headTrack)
            notifyTrack = Sequence(Parallel(getSuitAnimTrack(attack), Func(suit.checkBroadcasterDonation, theSuit, battle)),
                                    Wait(6.0))
            notifyTracks.append(notifyTrack)
    if theSuit == None:
        theSuit = suit

    return Parallel(notifyTracks, makeDamageUps, headTracks, soundTrack, makeDesperates)

def doVideographerDeath(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    for s in battle.activeSuits:
        if s.dna.name == 'hroller2':
            theSuit = s
            taunt = random.choice(
                ["Ooo-well, ya know what they ffay: don't hate the Major Player, change the game!",
                        "I can jufft hear the crowd going wild for thiff intermiffion!",
                        "Let'ff get the hip hop ffhop right on top, a-one a-two-let'ff play true!",
                        "We'll be back after a ffhort break, but I'm ffure you'll fftay occupied in the meantime."])
            tauntInterval = Sequence(Func(theSuit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
            suitTrack = Sequence(Parallel(ActorInterval(theSuit, 'snap'), tauntInterval), Func(theSuit.setNeutralAnimation))
            suitTracks.append(suitTrack)
    propTracks = Parallel()
    toonTracks = Parallel()
    selfDamageTracks = Parallel()
    smokeTracks = Parallel()
    suitDeathTracks = Parallel()
    for suit in battle.activeSuits:
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        suitTrack2 = Sequence(Wait(2), Parallel(ActorInterval(suit, 'flatten', duration=1.25),
                                               MovieUtil.createSuitCrashTrack(suit, battle)))
        selfDamageTrack = Sequence(Wait(2),
                Func(suit.showHpText, - suit.currHP),
                                   Func(suit.setHealthForMe, - suit.currHP),
                                   Func(suit.updateHealthBar, 0))
        smokeTrack = Sequence(Wait(2.0), Func(smoke.reparentTo, suit),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_tv.png')
        gavel = loader.loadModel('phase_14/models/char/ttcc_ene_multislacker-zero')
        gavel.setTexture(texture, 1)
        gavel.setP(-90)
        gavel.setH(180)
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y + 2, 30)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(180, -90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2.5), scaleUpTime=2.0),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y + 2, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        if not suit.dna.name == 'hroller2' and not suit.dna.name == 'videog':
            selfDamageTracks.append(selfDamageTrack)
            smokeTracks.append(smokeTrack)
            propTracks.append(propTrack)
            suitDeathTracks.append(suitTrack2)
    soundTrack = getSoundTrack('SA_TV_crash.ogg', delay=2.0, node=suit)
    soundTrack2 = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTracks, smokeTracks, suitDeathTracks, selfDamageTracks, soundTrack2, toonTracks, propTracks, soundTrack)

def doBudgetCuts(attack):
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
        tape.setColor(0, 0, 0, 1)
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))
            tubes[i].setColor(0, 0, 0, 1)

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
    partTrack = getPartTrack(particleEffect, 1.0, 3.4, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.4, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    target = attack['target']
    dmg = target[0]['hp']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'magic3'), Func(suit.setNeutralAnimationDrop))
    if dmg > 80:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                           "This isn't just a movie, it's an event! $%s in total impact!" %
                           int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    elif dmg > 60:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                           "It's official, this film's a mega-production! Estimated $%s on release!" %
                           int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    elif dmg > 40:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                           "The studio's investing heavily; expect $%s on release!" %
                           int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    else:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                               "The premiere begins now... projected gross: $%s." %
                               int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, suitSpeechTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, suitSpeechTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doBudgetExpansion(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculator', playRate=1.25), Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Every fallen producer funds the finale... we're sitting at $%s in damage!" %
                              int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_audit.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    can = loader.loadModel('phase_5/models/props/megaphone')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(suit, 'glower', endTime=1.5), Wait(3.0), ActorInterval(suit, 'glower', startTime=1.5), Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(3.0), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    toonTrack = getToonTrackCheat(attack, 4.0, ['cringe'], 0, ['duck'])
    notifyTrack = Sequence(Wait(4.0), Func(toon.showHpTextNew, -int(dmg), text="DAMAGE CUT!", colorCode=3))
    return Parallel(suitTrack, toonTrack, notifyTrack, throwTrack, suitTrack2, sprayTrack)

def doSingingBluesMegaphone(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    targets = attack['target']
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    can = loader.loadModel('phase_5/models/props/megaphone')
    highRollerHead = globalPropPool.getProp('cc_m_chr_ene_highroller2')
    highRollerHead.reparentTo(can)
    highRollerHead.setScale(0.5)
    highRollerHead.setPos(-1, -1.5, 0.25)
    highRollerHead.setHpr(0, 180, -90)
    highRollerHeadTrack = Sequence(Wait(1.5), ActorInterval(highRollerHead, 'cc_m_chr_ene_highroller2', endTime=3.0))
    sprayTrack.append(Func(setPosFromOther, sprayEffect, highRollerHead, Point3(-1, -1.5, 0.25)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, highRollerHead, 0], softStop=-3.5))
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack1 = Sequence(Wait(1.5), getSoundTrack('ttcc_ene_hroller_laugh.ogg'))
    toonTracks = getToonTracksCheat(attack, 4.0, ['cringe'], 0, ['duck'])
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        notifyTrack = Sequence(Wait(4.0), Func(toon.showHpTextNew, -int(dmg), text="WINDED!", colorCode=1))
        notifyTracks.append(notifyTrack)
    suitTrack2 = Sequence(ActorInterval(suit, 'glower', endTime=1.5), Wait(3.0), ActorInterval(suit, 'glower', startTime=1.5), Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(3.0), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    return Parallel(suitTrack, toonTracks, notifyTracks, soundTrack1, throwTrack, suitTrack2, highRollerHeadTrack, sprayTrack)

def doBackToOnes(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    can = loader.loadModel('phase_5/models/props/megaphone')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(suit, 'glower', endTime=1.5), Wait(3.0), ActorInterval(suit, 'glower', startTime=1.5), Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(3.0), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4.0, node=suit)
    selfDamageTrack = Sequence(Wait(4),
                               Parallel(Func(suit.setHP, suit.maxHP),
                                        Func(suit.showHpString, "BACK TO ONES!"),
                                        Func(suit.updateHealthBar, 0)))
    return Parallel(suitTrack, soundTrack, throwTrack, suitTrack2, selfDamageTrack, sprayTrack)

def doAction(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    can = loader.loadModel('phase_5/models/props/megaphone')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(suit, 'glower', endTime=1.5), Wait(3.0), ActorInterval(suit, 'glower', startTime=1.5), Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(3.0), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    return Parallel(suitTrack, throwTrack, suitTrack2, sprayTrack)

def doCameraFlash(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    can = loader.loadModel('phase_3.5/models/accessories/social/newstoon_camera')
    suitTrack = Sequence(getSuitTrack(attack))
    posPoints = [Point3(-0.25, -.25, 1), VBase3(-90, 0, 0)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=1.0), Wait(suit.getDuration('glower') - 1.5), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    toonTrack = getToonTrackCheat(attack, 1.0, ['conked'], 0, ['duck'])
    notifyTrack = Sequence(Wait(1.0), Func(toon.showHpTextNew, -int(dmg), text="FLASHED!", colorCode=1))
    oldcolor = render.getColorScale()
    soundTrack2 = getSoundTrack('Photo_shutter.ogg', delay=1.0, node=suit)
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0, 0, 0, 0)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, toonTrack, lightingTrack, soundTrack2, notifyTrack, throwTrack)

def doCameraRewind(attack):
    theSuit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        if not suit.dna.name == 'videog' and not suit.dna.name == 'hroller2':
            suitTrack.append(Func(suit.checkCameraRewind))
            suitTrack.append(Func(suit.updateHealthBar, 0))
        if not theSuit:
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
        if not suit.dna.name == 'videog' and not suit.dna.name == 'hroller2':
            theSuit = attack['suit']
            hitPoint = suit.getPos(battle)
            hitPoint.setZ(suit.height + 2)
            hitPoint.setY(hitPoint.getY() + 0.5)
            can = globalPropPool.getProp('redtape')
            can.setColor(0, 0, 0, 1)
            can.setP(90)
            knifeTrack = Sequence(
                getPropAppearTrack(can, theSuit.getRightHand(), posPoints, .5, VBase3(1, 1, 1),
                                   scaleUpTime=0.1),
                Wait(1.5),
                Parallel(
                    getThrowTrack(can, hitPoint, 1.5, battle, -10.288),
                    LerpHprInterval(can, 0.8, VBase3(0, 0, 0)), LerpScaleInterval(can, 0, VBase3(1.5, 1.5, 1.5))),
                Parallel(LerpPosInterval(can, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)),
                         Sequence(Wait(0.25), LerpScaleInterval(can, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, can)
            )
            knifeTracks.append(knifeTrack)
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + theSuit.height - 0.2)
    suitTrackAnim = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=4.5, node=theSuit)
    multiTrack = Parallel(soundTrack2)
    return Parallel(suitTrackAnim, suitTracks, multiTrack, knifeTracks)

def doAttackRewind(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Parallel(getSuitAnimTrack(attack))
    propTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_tv.png')
        gavel = loader.loadModel('phase_14/models/char/ttcc_ene_multislacker-zero')
        gavel.setTexture(texture, 1)
        gavel.setP(-90)
        gavel.setH(180)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y + 2, 30)
        gavelPos2 = Point3(toonPos.getX(), y - 5, 30)
        propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(180, -90, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(2), scaleUpTime=1.5),
        LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y + 2, 1)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 2)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 1)), Sequence(
            Wait(1.5),
            LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
        ))
        propTrack2 = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos2, VBase3(180, -90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y - 5, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y - 5, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y - 5, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        toonTrack = Sequence(
        Wait(1.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
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
        toonTrack2 = Sequence(
            Wait(1.75),
            Parallel(
                Func(MovieUtil.indicateMissed, toon, 2.0),
            ))

        soundTrack2 = getSoundTrack('SA_bash.ogg', node=suit)
        soundTrack = getSoundTrack('SA_TV_crash.ogg', delay=1.5, node=suit)
        if dmg > 0:
            toonTracks.append(toonTrack)
            soundTracks.append(soundTrack)
            propTracks.append(propTrack)
            smokeTracks.append(smokeTrack)
        else:
            toonTracks.append(toonTrack2)
            soundTracks.append(soundTrack)
            propTracks.append(propTrack2)
    return Parallel(suitTrack, toonTracks, smokeTracks, soundTrack2, soundTracks, propTracks)

def doDirectorCuts(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    hollywoods = []
    puddleTracks = Parallel()
    moveTracks = Parallel()
    managerHealTracks = Parallel()
    animTracks = Parallel()
    for s in battle.activeSuits:
        if not s.dna.name == 'director' and not s.dna.name == 'fmaker' and not s.dna.name == 'videog' and not s.dna.name == 'bcaster' and not s.dna.name == 'hroller2':
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Wait(suit.getDuration('song-and-dance')), Func(battle.movie.needRestoreRenderProp, puddle),
                                   Func(puddle.reparentTo, battle), Func(puddle.setPos, s.getPos(battle)),
                                   LerpScaleInterval(puddle, 0.9, Point3(1.7, 1.7, 1.7),
                                                     startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2),
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
            moveTrack = Sequence(Wait(suit.getDuration('song-and-dance') + 1.8), LerpPosInterval(s, 0.9, sinkPos1, other=battle),
                                 LerpPosInterval(s, 0.4, sinkPos2, other=battle), Func(s.hide), Wait(1.1))
            animTrack = Sequence(Wait(suit.getDuration('song-and-dance')+ 0.9), ActorInterval(s, 'flail-qs', endTime=1.75),
                                 ActorInterval(s, 'flail-qs', startTime=1.25, endTime=1.75),
                                 ActorInterval(s, 'flail-qs', startTime=1.25, endTime=1.25))
            managerHealTrack = Sequence(Wait(suit.getDuration('song-and-dance') + 3), Func(suit.showHpTextCheat, + (s.maxHP)),
                                        Func(suit.setHealthForMe, + (s.maxHP)),
                                        Func(suit.updateHealthBar, 0))
            managerHealTracks.append(managerHealTrack)
            animTracks.append(animTrack)
            moveTracks.append(moveTrack)
            puddleTracks.append(puddleTrack)
            hollywoods.append(s)
    soundTrack = getSoundTrack('SA_bash.ogg', delay=suit.getDuration('song-and-dance') + .25, node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3 + suit.getDuration('song-and-dance'), node=suit)

    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(suit, 'snap'), Wait(3.0), doRisingStars2(attack))
    return Parallel(suitTrack, soundTrack, animTracks, moveTracks)

def doRisingStars2(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    taunt = random.choice(
        ["Let me introduce you to some friends of mine."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 16.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    moveTrack = Sequence(LerpPosInterval(suit, 0, sinkPos, other=battle), Wait(suit.getDuration('shot5')), LerpPosInterval(suit, 0, dropPos, other=battle), Func(suit.setPos, battle, dropPos))

    suitTrack = Parallel(ActorInterval(suit, 'shot5'), tauntInterval)
    suitTrack.append(Func(suit.makeImmortal))
    return Parallel(suitTrack, moveTrack)

def doRisingStars(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']

    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 16.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    moveTrack = Sequence(LerpPosInterval(suit, 0, sinkPos, other=battle), Wait(suit.getDuration('shot5')), LerpPosInterval(suit, 0, dropPos, other=battle), Func(suit.setPos, battle, dropPos))

    suitTrack = Sequence(getSuitAnimTrack(attack))
    if suit.isImmortal and attack['name'] == 'VideographerRisingStars' or attack['name'] == 'VideographerRisingStars2':
        suitTrack.append(Func(suit.makeNonImmortal))
    return Parallel(suitTrack, moveTrack)

def doElectricShock(attack, ind):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    targetSuit = battle.activeSuits[ind]
    battle = attack['battle']
    targetPos = targetSuit.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    battle = attack['battle']
    targetPos2 = toon.getPos(battle)
    headsUp2 = Func(suit.headsUp, battle, targetPos2)
    toonPos = toon.getPos(battle)
    suitPos = targetSuit.getPos(battle)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    y = suitPos.getY()
    moveTrack = Sequence(LerpPosInterval(suit, suit.getDuration('walk'), sinkPos2, other=battle),
                         Wait(suit.getDuration('glower')),
                         LerpPosInterval(suit, suit.getDuration('walk'), dropPos, other=battle),
                         Func(suit.setPos, battle, dropPos))
    suitTrack = Sequence(ActorInterval(suit, 'walk'), headsUp, getSuitAnimTrack(attack), ActorInterval(suit, 'walk'),
                         headsUp2, Func(suit.setNeutralAnimation))
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_5/models/props/lightning')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    toonPos = toon.getPos(battle)
    y = suitPos.getY()
    x = int((targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP)
    cagePos = [Point3(suitPos.getX(), y + 2, 100.0), targetSuit.getHpr(battle)]
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.setBillboardPointEye()
    smokeTrack = Sequence(Wait(suit.getDuration('walk') + 1), Func(smoke.reparentTo, targetSuit),
                          Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                   LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                          Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                          Func(MovieUtil.removeProp, smoke))
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, suit.getDuration('walk') + 1, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0, Point3(suitPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    selfDamageTrack = Sequence(Wait(suit.getDuration('walk') + 1), Parallel(ActorInterval(targetSuit, 'large-zap'), Func(targetSuit.setHealthForMe, int(targetSuit.maxHP)), Func(targetSuit.setHP, int(targetSuit.maxHP * 2)),
            Func(targetSuit.showHpTextNew, 0, text="OVERCHARGED!", colorCode=5), Func(targetSuit.updateHealthBar, 0)),
                               Func(targetSuit.setNeutralAnimation))
    return Parallel(suitTrack, cagePropTracks, smokeTrack, moveTrack, selfDamageTrack)


def doVideoStatic(attack):
    suit = attack['suit']
    battle = attack['battle']
    notifyTracks = Sequence(Wait(0.5))
    headTracks = Parallel()
    theSuit = None
    soundTrack = getSoundTrack('tv_static.ogg', delay=1, node=suit)
    soundTrack2 = getSoundTrack('tv_static.ogg', delay=2.5, node=suit)
    soundTrack4 = getSoundTrack('SA_hit.ogg', node=suit)
    for s in battle.activeSuits:
        if s.dna.name == 'videog' and not suit.dna.name == 'videog':
            theSuit = s
            texture2 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer4.png')
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            headTrack = Sequence()
            for headPart in s.animatedHeadParts:
                headTrack.append(Wait(1))
                headTrack.append(Func(headPart.loop, 'stun'))
                headTrack.append(Func(headPart.setTexture, texture2, 1))
                headTrack.append(Wait(theSuit.getDuration('throttletwo') - 4.25))
                headTrack.append(Parallel(Func(headPart.setTexture, texture, 1), soundTrack4, Func(headPart.loop, 'neutral')))
            if suit.dna.name == 'bcaster':
                notifyTrack = Sequence(ActorInterval(theSuit, 'sound-react-nt', endTime=2.5), ActorInterval(theSuit, 'throttletwo', startTime=3), Func(theSuit.showHpText2,
                                                   '+25% Vulnerable',
                                                   2), Func(theSuit.showHpStringLureManager2,
                                                            '+25% Damage'), Func(theSuit.makeDamageUp), Func(theSuit.makeVulnerable), Func(theSuit.setNeutralAnimation), Func(theSuit.checkDamageUp, + 25), Func(theSuit.checkVulnerabilityUp, + 25), Wait(2.0))
            else:
                notifyTrack = Sequence(ActorInterval(theSuit, 'sound-react-nt', endTime=2.5), ActorInterval(theSuit, 'throttletwo', startTime=3), Func(theSuit.showHpText2,
                                                   '+10% Vulnerable',
                                                   2), Func(theSuit.showHpStringLureManager2,
                                                            '+10% Damage'), Func(theSuit.makeDamageUp), Func(theSuit.makeVulnerable), Func(theSuit.setNeutralAnimation), Func(theSuit.checkDamageUp, + 10), Func(theSuit.checkVulnerabilityUp, + 10), Wait(2.0))
            headTracks.append(headTrack)
            cameraTrack = Sequence(MovieCamera.motionShot(0.0, 12.0, 6.0, -180, 0, 0.0, 0, theSuit), Wait(3.0))
            notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    if theSuit == None:
        theSuit = suit

    return Parallel(notifyTracks, soundTrack2, headTracks, soundTrack)


def doRisingStarsSacrifice(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    hollywoods = []
    puddleTracks = Parallel()
    moveTracks = Parallel()
    managerHealTracks = Parallel()
    animTracks = Parallel()
    for s in battle.activeSuits:
        if not s.dna.name == 'director' and not s.dna.name == 'fmaker' and not s.dna.name == 'videog' and not s.dna.name == 'bcaster' and not s.dna.name == 'hroller2':
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle),
                                   Func(puddle.reparentTo, battle), Func(puddle.setPos, s.getPos(battle)),
                                   LerpScaleInterval(puddle, 0.9, Point3(1.7, 1.7, 1.7),
                                                     startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2),
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
            moveTrack = Sequence(Wait(1.8), LerpPosInterval(s, 0.9, sinkPos1, other=battle),
                                 LerpPosInterval(s, 0.4, sinkPos2, other=battle), MovieUtil.createRisingStars(s, battle), Func(s.setPos, battle, dropPos),
                                 Func(s.wrtReparentTo, battle), LerpPosInterval(s, 0, landPos, other=battle), Wait(2), LerpColorScaleInterval(s, 2, (1, 1, 1, 1)), Wait(1.1),
                                 Func(s.showHpString, '+50% Damage'))
            animTrack = Sequence(Wait(0.9), ActorInterval(s, 'flail-qs', endTime=1.75),
                                 ActorInterval(s, 'flail-qs', startTime=1.25, endTime=1.75),
                                 ActorInterval(s, 'flail-qs', startTime=1.25, endTime=1.25), Func(s.setNeutralAnimation))
            managerHealTrack = Sequence(Wait(3), Func(suit.showHpTextCheat, + (s.maxHP / 2)),
                                        Func(suit.setHealthForMe, + (s.maxHP / 2)),
                                        Func(suit.updateHealthBar, 0))
            managerHealTracks.append(managerHealTrack)
            animTracks.append(animTrack)
            moveTracks.append(moveTrack)
            puddleTracks.append(puddleTrack)
            hollywoods.append(s)

    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, moveTracks, animTracks, soundTrack, puddleTracks)

def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.setNeutralAnimationTrap))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)

def doNoAttack(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack2 = Sequence()
    targets = attack['target']
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
    if suit.isImmortal and not suit.dna.name == 'hroller' and not suit.dna.name == 'videog' and suit.isPhase3:
        suitTrack = Sequence(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0), Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '',)))
        suitTrack.append(Func(suit.makeNonImmortal))
        return suitTrack
    else:
        if suit.dna.name == 'hrollers':
            suitTrack = Sequence()
            return suitTrack
        return Parallel(suitTrack2, notifyTracks)

def doDesperation(attack):
    suit = attack['suit']
    suitTrack = Sequence()
    if suit.dna.name == 'caseman':
        for obj in base.cr.doId2do.values():
            if isinstance(obj, DistributedLawbotBoss):
                suitTrack.append(Func(obj.stopCaseManagerMusic))
    if suit.dna.name == 'sgoat':
        for obj in base.cr.doId2do.values():
            if isinstance(obj, DistributedLawbotBoss):
                suitTrack.append(Func(obj.stopScapegoatMusic))
    if suit.dna.name == 'stenog':
        for obj in base.cr.doId2do.values():
            if isinstance(obj, DistributedLawbotBoss):
                suitTrack.append(Func(obj.stopStenographerMusic))
    if suit.dna.name == 'lgator':
        for obj in base.cr.doId2do.values():
            if isinstance(obj, DistributedLawbotBoss):
                suitTrack.append(Func(obj.stopLitigatorMusic))
    return suitTrack

def playSplashEffect(render, x, y, z):
    from toontown.effects import Splash
    splash = Splash.Splash(render)

    splash.setPos(x, y, z)
    splash.setScale(2)
    splash.play()

def doSplashback(attack):
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
        notifyTrack = Sequence(Wait(4.0), Func(toon.showHpTextNew, - int(dmg), text="SOAKED?!", colorCode=1))
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

def doVulnerable(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(Func(suit.makeVulnerable))
    return suitTrack

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
        suitTrack = Parallel(getSuitAnimTrack(attack))
        suitTrack.append(Wait(2.0))
        if dmg > 0:
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            explosionTracks.append(explosionTrack)
            suitTracks.append(suitTrack)
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
            suitTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'glower'),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            notifyTracks.append(notifyTrack)
    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                         dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, toonDamageTrack, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)

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

def doSnipeDamageReduction(attack): #UNUSED
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
        leftPosPoints = [Point3(0.5, 3.0, suit.height - 1), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.5, 3.0, suit.height - 1), MovieUtil.PNT3_ZERO]
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

        damageAnims = [['slip-backward', 0.01, 0.35]]
        toonTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextNew, - int(dmg), text="GAG DEBUFF!", colorCode=1))
        #toonTrack = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
        soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=1.5, node=suit)
        suitTrack = Sequence(getSuitAnimTrack(attack))
        suitTrack.append(Wait(2.0))
        if dmg > 0:
            toonTracks.append(toonTrack)
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            explosionTracks.append(explosionTrack)
            suitTracks.append(suitTrack)
            notifyTracks.append(notifyTrack)
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)

def doSingingBlues(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    notifyTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        notifyTracks.append(Func(toon.makeWinded))
        notifyTracks.append(Func(toon.addWindedRounds, 1))
        notifyTracks.append(Parallel(Func(toon.checkWinded, 50)))
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
                         Func(MovieUtil.removeProps, [receiver, phone]))
    toonTracks = getToonTracks(attack, 2.8, ['slip-backward'], 4.7, ['jump'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.8)
    return Parallel(suitTrack, propTrack, soundTrack, notifyTracks, soundTrack1, toonTracks, explodeTracks, explosionTrack)

def doGameTimeSpawn(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(MovieUtil.createSuitSnapInterval(suit), Func(suit.setNeutralAnimationDrop))
    suitTrack.append(Wait(3.0))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, soundTrack, suitTrack2)

def doSyphon(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    for t in targets:
        dmg = t['hp']
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.setNeutralAnimation))
    suitTrack.append(Func(suit.setHealthForMe, + ((dmg * 4) * len(battle.activeToons))))
    suitTrack.append(Wait(2.0))
    toonTrack = getToonTracks(attack, 0.6, ['slip-forward'], 0.01, ['applause'])
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=0.2, node=suit)
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpTextNew,  +((dmg * 4) * len(battle.activeToons)), text="SYPHONED!", colorCode=1), Func(suit.updateHealthBar, 0), soundTrack2)
    multiTrackList = Parallel(suitTrack, toonTrack, selfDamageTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('AA_drop_safe_miss.ogg', delay=0.2, node=suit)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doDonation(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    theSuit = None
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    for s in battle.activeSuits:
        if s.dna.name == 'hroller2':
            theSuit = s

    if theSuit == None:
        theSuit = suit

    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    moveTrack = Sequence(LerpPosInterval(suit, 1.5, sinkPos2, other=battle), LerpPosInterval(suit, 0, sinkPos, other=battle), Wait(3.9), LerpPosInterval(suit, 0, sinkPos2, other=battle), LerpPosInterval(suit, 1.5, dropPos, other=battle), Func(suit.setPos, battle, resetPos))

    suitTrack = Sequence(ActorInterval(suit, 'walk'), getSuitAnimTrack(attack), ActorInterval(suit, 'walk'))
    selfDamageTrack = Sequence(Wait(4.0), Func(suit.checkHighRollerDonation, theSuit, battle))
    managerHealTrack = Sequence(Wait(4.0), Func(theSuit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHighRollerPhrases),
                                     CFSpeech | CFTimeout),
                                SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    return Parallel(suitTrack, moveTrack, selfDamageTrack, managerHealTrack)

def createTNTExplosionTrack(parent, explosionPoint = None, scale = 1.0):
    explosionTrack = Sequence()
    explosion = BattleProps.globalPropPool.getProp('kapow')
    explosion.setBillboardPointEye()
    explosion.setDepthWrite(False)
    if not explosionPoint:
        explosionPoint = Point3(0, 3.6, 2.1)
    explosionTrack.append(Func(explosion.reparentTo, parent))
    explosionTrack.append(Func(explosion.setPos, explosionPoint))
    explosionTrack.append(Func(explosion.setScale, 0.4 * scale))
    explosionTrack.append(ActorInterval(explosion, 'kapow'))
    explosionTrack.append(Wait(0.6))
    explosionTrack.append(Func(MovieUtil.removeProp, explosion))
    return explosionTrack


def doBar(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    ship = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    ship4 = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    ship.setScale(4.085, 4.342, 2.928)
    ship4.setScale(4.085, 4.342, 2.928)
    freeCruiseDelay = 0
    suitTracks = Parallel()
    toonTracks = Parallel()
    soundTrack2 = getSoundTrack('SA_bash.ogg', node=suit)
    for suit in battle.activeSuits:
        suitTrack = getSuitAnimTrack(attack)
        suitTrack.append(Wait(.25))
        if suit.dna.name == 'hroller2':
            suitTrack.append(Func(suit.setHealthForMe, - (25 * len(battle.activeToons))))
            suitTrack.append(Func(suit.showHpText, - (25 * len(battle.activeToons))))
        else:
            suitTrack.append(Func(suit.setHealthForMe, - (250 * len(battle.activeToons))))
            suitTrack.append(Func(suit.showHpText, - (250 * len(battle.activeToons))))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(ActorInterval(suit, 'flatten'))
        suitTracks.append(suitTrack)
        suitTrack.append(Func(suit.setNeutralAnimation))
    objZOffset = 0.0
    landFrames = 2
    node = ship.node()
    node.setBounds(OmniBoundingVolume())
    node.setFinal(1)
    node2 = ship4.node()
    node2.setBounds(OmniBoundingVolume())
    node2.setFinal(1)
    shipTrack = Sequence()
    shipTrack2 = Sequence()

    def posObject(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)

    def posObject2(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        object.setY(object.getY(battle) + 15)
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)

    shipTrack.append(Func(battle.movie.needRestoreRenderProp, ship))
    shipTrack.append(Wait(2.86 + freeCruiseDelay))
    shipTrack2.append(Func(battle.movie.needRestoreRenderProp, ship4))
    shipTrack2.append(Wait(2.86 + freeCruiseDelay))
    closestTarget = -1
    nearestDistance = 100000.0
    for i in xrange(len(targets)):
        toon = targets[i]['toon']
        toonPos = toon.getPos(battle)
        displacement = Vec3(MovieUtil.calcAvgToonPos(attack))
        displacement -= toonPos
        distance = displacement.lengthSquared()
        if distance < nearestDistance:
            closestTarget = i
            nearestDistance = distance

    hitAtleastOneToon = 1
    shipTrack.append(Func(posObject, ship, targets[closestTarget]['toon'], not hitAtleastOneToon))
    shipTrack2.append(Func(posObject2, ship4, targets[closestTarget]['toon'], not hitAtleastOneToon))
    if hitAtleastOneToon:
        if hasattr(ship, 'getAnimControls'):
            pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
        elif hasattr(ship4, 'getAnimControls'):
            pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
        else:
            startingScale = Point3(2.5, 4.5, 1.5)
            ship2 = MovieUtil.copyProp(ship)
            ship3 = MovieUtil.copyProp(ship4)
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            gearPoint = Point3(suitPos.getX() + 5, suitPos.getY() - 5, suitPos.getZ() + suit.height - 1)
            soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
            explosionTrack = Sequence(Wait(0.5), Parallel(soundTrack, createTNTExplosionTrack(battle, explosionPoint=gearPoint, scale=3)))
            posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
            posObject2(ship3, targets[closestTarget]['toon'], not hitAtleastOneToon)
            endingPos = ship2.getPos()
            startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
            startHpr = ship2.getHpr()
            endingPos2 = ship3.getPos()
            startPos2 = Point3(endingPos2[0], endingPos2[1], endingPos2[2] + 5)
            startHpr2 = ship3.getHpr()
            endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
            endHpr2 = Point3(startHpr2[0] + 90, startHpr2[1], startHpr2[2])
            animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
            shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1)
            objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp,
                                     Parallel(bounceProp, explosionTrack), shrinkProp)
            animProp2 = LerpPosInterval(ship4, landFrames / 24.0, endingPos2, startPos=startPos2)
            shrinkProp2 = LerpScaleInterval(ship4, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp2 = Effects.createZBounce(ship4, 2, endingPos2, 0.5, 1)
            objAnimShrink2 = Sequence(Func(ship4.setScale, startingScale), Func(ship4.setH, endHpr2[0]), animProp2,
                                     bounceProp2, Wait(1.5), shrinkProp2)
            shipTrack.append(objAnimShrink)
            shipTrack2.append(objAnimShrink2)
            MovieUtil.removeProp(ship2)
            MovieUtil.removeProp(ship3)
    elif hasattr(ship, 'getAnimControls'):
        pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
    else:
        startingScale = 1.0
        ship2 = MovieUtil.copyProp(ship)
        posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
        endingPos = ship2.getPos()
        startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
        startHpr = ship2.getHpr()
        endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
        animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
        shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
        bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1)
        objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        shipTrack.append(objAnimShrink)
        MovieUtil.removeProp(ship2)
    shipTrack.append(Func(ship.removeNode))
    shipTrack.append(Func(ship4.removeNode))
    dropShadow = MovieUtil.copyProp(targets[closestTarget]['toon'].dropShadow)
    dropShadow.setScale(3.6)

    def posShadow(dropShadow=dropShadow, toon=toon, battle=battle, hp=targets[0]['hp']):
        dropShadow.reparentTo(battle)
        dropShadow.setPos(toon.getPos(battle))
        dropShadow.setHpr(toon.getHpr(battle))
        if hp == 0:
            dropShadow.setY(dropShadow.getY(battle) - 5)
        dropShadow.setZ(dropShadow.getZ() + 0.5)

    def posShadow2(dropShadow=dropShadow, toon=toon, battle=battle, hp=targets[0]['hp']):
        dropShadow.reparentTo(battle)
        dropShadow.setPos(toon.getPos(battle))
        dropShadow.setHpr(toon.getHpr(battle))
        dropShadow.setY(dropShadow.getY(battle) + 15)
        if hp == 0:
            dropShadow.setY(dropShadow.getY(battle) - 5)
        dropShadow.setZ(dropShadow.getZ() + 0.5)

    shadowTrack = Sequence(
        Wait(1.0 + freeCruiseDelay),
        Func(battle.movie.needRestoreRenderProp, dropShadow),
        Func(posShadow), Func(posShadow2),
        LerpScaleInterval(dropShadow, 1.86, dropShadow.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(0.3),
        Func(dropShadow.removeNode)
    )
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonTrack2 = Sequence(
        Wait(2.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
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
        toonTracks.append(toonTrack2)
    hitSounds = Parallel()
    hitSounds.append(getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=2.86 + freeCruiseDelay))
    multiTrackList = Parallel(soundTrack2, suitTracks, shipTrack2, shipTrack, shadowTrack, toonTracks, hitSounds)
    return multiTrackList

def doFreeCruise(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    ship = globalPropPool.getProp('ship')
    freeCruiseDelay = 3.1
    suitTrack = getSuitAnimTrack(attack)
    objZOffset = 0.0
    landFrames = 2
    node = ship.node()
    node.setBounds(OmniBoundingVolume())
    node.setFinal(1)
    shipTrack = Sequence()

    def posObject(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)

    shipTrack.append(Func(battle.movie.needRestoreRenderProp, ship))
    shipTrack.append(Wait(2.86 + freeCruiseDelay))
    closestTarget = -1
    nearestDistance = 100000.0
    for i in xrange(len(targets)):
        toon = targets[i]['toon']
        toonPos = toon.getPos(battle)
        displacement = Vec3(MovieUtil.calcAvgToonPos(attack))
        displacement -= toonPos
        distance = displacement.lengthSquared()
        if distance < nearestDistance:
            closestTarget = i
            nearestDistance = distance

    hitAtleastOneToon = 1
    shipTrack.append(Func(posObject, ship, targets[closestTarget]['toon'], not hitAtleastOneToon))
    if hitAtleastOneToon:
        if hasattr(ship, 'getAnimControls'):
            pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
        else:
            startingScale = 1.0
            ship2 = MovieUtil.copyProp(ship)
            posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
            endingPos = ship2.getPos()
            startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
            startHpr = ship2.getHpr()
            endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
            animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
            shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1)
            objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp,
                                     bounceProp, Wait(1.5), shrinkProp)
            shipTrack.append(objAnimShrink)
            MovieUtil.removeProp(ship2)
    elif hasattr(ship, 'getAnimControls'):
        pass  # Not imperative at the moment given the Toontanic does not have the getAnimControls attribute
    else:
        startingScale = 1.0
        ship2 = MovieUtil.copyProp(ship)
        posObject(ship2, targets[closestTarget]['toon'], not hitAtleastOneToon)
        endingPos = ship2.getPos()
        startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
        startHpr = ship2.getHpr()
        endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
        animProp = LerpPosInterval(ship, landFrames / 24.0, endingPos, startPos=startPos)
        shrinkProp = LerpScaleInterval(ship, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
        bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1)
        objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        shipTrack.append(objAnimShrink)
        MovieUtil.removeProp(ship2)
    shipTrack.append(Func(ship.removeNode))
    dropShadow = MovieUtil.copyProp(targets[closestTarget]['toon'].dropShadow)
    dropShadow.setScale(3.6)

    def posShadow(dropShadow=dropShadow, toon=toon, battle=battle, hp=targets[0]['hp']):
        dropShadow.reparentTo(battle)
        dropShadow.setPos(toon.getPos(battle))
        dropShadow.setHpr(toon.getHpr(battle))
        if hp == 0:
            dropShadow.setY(dropShadow.getY(battle) - 5)
        dropShadow.setZ(dropShadow.getZ() + 0.5)

    shadowTrack = Sequence(
        Wait(1.0 + freeCruiseDelay),
        Func(battle.movie.needRestoreRenderProp, dropShadow),
        Func(posShadow),
        LerpScaleInterval(dropShadow, 1.86, dropShadow.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(0.3),
        Func(dropShadow.removeNode)
    )
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonTrack2 = Sequence(
        Wait(2.86 + freeCruiseDelay),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
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
        toonTracks.append(toonTrack2)
    soundTrack = getSoundTrack('AA_drop_boat%s.ogg' % ('' if hitAtleastOneToon else '_miss'),
                               delay=(0.9 if targets[0]['hp'] == 0 else 1.0) + freeCruiseDelay, node=suit)
    hitSounds = Parallel()
    hitSounds.append(getSoundTrack('AA_drop_boat_cog.ogg', delay=2.86 + freeCruiseDelay))
    suitTrack.append(Func(suit.makeNonImmortal))
    multiTrackList = Parallel(suitTrack, shipTrack, shadowTrack, toonTracks, soundTrack, hitSounds)
    multiTrackList.append(getSoundTrack('AA_heal_happydance.ogg', node=suit))
    return multiTrackList

def doAceInTheHoleOLD(attack):
    suitHighRoller = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    card = globalPropPool.getProp('cc_a_prp_bat_playcard')
    highRollerHead = globalPropPool.getProp('cc_m_chr_ene_highroller')
    taunt = random.choice(
        ["I'm a flying affe, fforaring in the fog! Prepare to be ffcared, babe.", "You know, I've alwayff got an affe up my ffleeve! Ffee?",
         "I'm the biggefft ffenffation, the talk of the town! Hope you haven't forgotten, doll.",
         "It'ff time for my cloffe up! You're getting in all of the action now, folkff!", "Ffhrouded in mifft, you'll ffoon fee who'ff in control of the ffow now!"])
    tauntInterval = Sequence(Func(suitHighRoller.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrackHighRoller = Parallel(ActorInterval(suitHighRoller, 'neutral'), tauntInterval)
    suitTracks = Parallel()
    objZOffset = 0.0
    toonTracks = Parallel()
    def posObject(object, toon, miss, battle=battle):
        object.reparentTo(battle)
        object.setPos(toon.getPos(battle))
        object.setHpr(toon.getHpr(battle))
        if miss:
            object.setY(object.getY(battle) - 5)
        object.setZ(object.getPos(battle)[2] + objZOffset)
    closestTarget = -1
    nearestDistance = 100000.0
    for i in xrange(len(targets)):
        toon = targets[i]['toon']
        toonPos = toon.getPos(battle)
        displacement = Vec3(MovieUtil.calcAvgToonPos(attack))
        displacement -= toonPos
        distance = displacement.lengthSquared()
        if distance < nearestDistance:
            closestTarget = i
            nearestDistance = distance
    cardPos = [Point3(toonPos.getX(), toonPos.getY() - 25, -3.5), toon.getHpr(battle)]
    headPos = [Point3(toonPos.getX(), toonPos.getY() - 25, -3.5), toon.getHpr(battle)]
    scaleUpPoint = Point3(1.1, 1.1, 1.1)
    hitAtleastOneToon = 1
    propTrackHead = Parallel()
    propTrackNew = Parallel()
    propTrackHead.append(Func(posObject, highRollerHead, targets[closestTarget]['toon'], not hitAtleastOneToon))
    propTrackHead.append(Sequence(Wait(5.5),
                             getPropTrack(highRollerHead, battle, headPos, 1e-06, 0, scaleUpPoint=scaleUpPoint,
                                          anim=1, animStartTime=0, animDuration=3.0,
                                          propName='cc_m_chr_ene_highroller'), Wait(1.6)))
    propTrackHead.append(Func(posObject, card, targets[closestTarget]['toon'], not hitAtleastOneToon))
    propTrackNew.append(Sequence(Wait(5.5),
                            getPropTrack(card, battle, cardPos, 1e-06, 0, scaleUpPoint=scaleUpPoint, scaleUpTime=3,
                                         anim=1, animStartTime=0, animDuration=3.0,
                                         propName='cc_a_prp_bat_playcard'), Wait(1.6)))
    for suit in battle.activeSuits:
        suitTrack = Sequence(Wait(3), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=0, endTime=1), Func(suit.loop, 'highroller-neutral-levitate-loop'))
        suitTrack.append(Wait(8))
        suitTrack.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTracks.append(suitTrack)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonTrack = Sequence(
        Wait(8.5),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpTextNew,  - int(dmg), text="VULNERABLE!", colorCode=4),
            Func(__doDamageCheat, toon, dmg, t['died'])
        ),
        Wait(1.0),
        Parallel(
            Sequence(
                Wait(0.5),
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
    soundTrack = Sequence(Wait(1.0), SoundInterval(globalBattleSoundCache.getSound('cc_s_sfx_ene_hroller_ace_in_the_hole.ogg')))
    return Parallel(suitTrackHighRoller, suitTracks, toonTracks, propTrackNew, propTrackHead, soundTrack)


def doAceInTheHole(attack):
    suitHighRoller = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    card = globalPropPool.getProp('cc_a_prp_bat_playcard')
    card2 = globalPropPool.getProp('cc_a_prp_bat_playcard2')
    highRollerHead = globalPropPool.getProp('cc_m_chr_ene_highroller')
    taunt = getAttackTaunt(attack['name'], attack['suitName'], attack['taunt'])
    suitTrackHighRoller = Sequence(getSuitAnimTrack(attack))
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence(Wait(3), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=0, endTime=1),
                             Func(suit.loop, 'highroller-neutral-levitate-loop'))
        suitTrack.append(Wait(8))
        suitTrack.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitTracks.append(suitTrack)

    headPropTrack = Sequence(
        Wait(5.0),
        Func(__showProp, highRollerHead, battle, Point3(0, -25, -2)),
        ActorInterval(highRollerHead, 'cc_m_chr_ene_highroller'),
        Func(MovieUtil.removeProp, highRollerHead)
    )
    cardPropTrack = Sequence(
        Wait(5.0), Func(__showProp, card2, battle, Point3(0, -25, -2), scale=Point3(1.1, 1.1, 1.1)),
        ActorInterval(card2, 'cc_a_prp_bat_playcard2'),
        Func(MovieUtil.removeProp, card2),
        # I'm not sure of optimal timings, so I'll just copy the old method's timings and let Dissonance decide better ones.  Added 3 more seconds because of the scaleUpTime.
        Func(__showProp, card, battle, Point3(0, -25, -2), scale=Point3(1.1, 1.1, 1.1)),
        ActorInterval(card, 'cc_a_prp_bat_playcard'),
        Func(MovieUtil.removeProp, card))
    toonTracks = Parallel()
    for i in xrange(len(targets)):
        tgt = targets[i]
        toon = tgt['toon']
        dmg = tgt['hp']
        toonTrack = Sequence(
            Wait(8.5),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpTextNew,  - int(dmg), text="VULNERABLE!", colorCode=4),
                Func(__doDamageCheat, toon, dmg, tgt['died'])
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
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

    soundTrack = getSoundTrack('cc_s_sfx_ene_hroller_ace_in_the_hole.ogg')
    return Parallel(suitTrackHighRoller, suitTracks, toonTracks, headPropTrack, cardPropTrack, soundTrack)

def doTrickOfTheLight(attack):
    suit = attack['suit']
    battle = attack['battle']
    taunt = random.choice(
        ["Every copy of me iff perffonalized.",
         "One ffhowfftopper jufft iffn't enough! There needff to be more!"])
    suitTrack2 = Sequence(getSuitAnimTrackHighRoller(attack))
    suitTrack = Sequence(Parallel(ActorInterval(suit, 'neutral2'), Wait(2.0)), ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1), Func(suit.loop, 'highroller-neutral-levitate-loop'), Wait(1.0))
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeUnVulnerable))
    return Parallel(suitTrack, suitTrack2)

def doPhase3(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack2 = Sequence(Parallel(ActorInterval(suit, 'neutral2'), Wait(2.8)), ActorInterval(suit, 'song-and-dance'), Func(suit.loop, 'neutral2'))
    suitTrack = Sequence(Func(suit.loop, 'neutral2'), Wait(13.2), MovieUtil.createSuitLaughInterval2(suit), Wait(1.0))
    talkTrack = Sequence(Func(suit.setChatAbsolute, "AND NOW FOR THE FFFTAR OF OUR FFHOW!!!!!!", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "THAT'FF RIGHT EYE-FFPOT FFPOTLIGHT, thiff turnfftyleff been hot all night, let'ff ffee if you can handle the heat!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute,  "This duet jufft got a hip hump bump to a five-part big band, babe!", CFSpeech | CFTimeout), Wait(3.7),
                         Func(suit.setChatAbsolute,  "I'm the hottest fftar on fftage! Ffo come on inamorata, let'ff burn a hole in those goggle boffeff!", CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute, "Better ffmile before ya burn out!", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', delay=13.2)
    suitTrack.append(Func(suit.makeIntoPhase3))
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeUnVulnerable))
    return Parallel(talkTrack, suitTrack, suitTrack2, soundTrack1)

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
    notifyTrack = Sequence(Wait(2.5), Func(toon.showHpText, - int(dmg)))
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


def doViralSensation(attack):
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
            toonTrack.append(Wait(damageDelay + 5))
            toonTrack.append(Parallel(Func(toon.makeDamageUp), Func(toon.addDamageUpRounds, 1)))
            toonTrack.append(Parallel(Func(toon.checkDamageUp, 50)))
            toonTrack.append(Func(toon.showHpStringViral, "VIRAL SENSATION!"))
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
    return Parallel(suitTrack, partTracks, toonTracks2, toonTracks, allHeadTracks, allChestTracks)

def doRolled(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles() # We need to be able to change the color of the particle effects.
    damageDelay = 1.7
    # We want to handle the particle effect differently from Spin since we will be customizing these particle effects.
    sprayEffects = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle', color=Vec4(random.random(), random.random(), random.random(), 1))
        sprayEffects.append(sprayEffect)

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
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTracks = Parallel()
    toonSpinTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
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
        if dmg > 0:
            spinTracks1.append(getPartTrack(spinEffect1, 1.5, 5.9, [spinEffect1, battle, 0], softStop=-2))
            spinTracks2.append(getPartTrack(spinEffect2, 1.5, 5.9, [spinEffect2, battle, 0], softStop=-2))
            spinTracks3.append(getPartTrack(spinEffect3, 1.5, 5.9, [spinEffect3, battle, 0], softStop=-2))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit))
            toonSpinTracks.append(Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))

    return Parallel(suitTrack, sprayTracks, toonTracks, toonSpinTracks, spinTracks1, spinTracks2, spinTracks3, soundTracks)

def doBust(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    toonTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    talkTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack = Sequence(Wait(5.0),
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 2.01)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 3)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2.01)), Sequence(
                Wait(0.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))

        toonTrack = Sequence(
            Wait(6.5),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                #Func(__doDamage, toon, dmg, t['died'])
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),
                getSoundTrack('toon_decompress.ogg', node=toon),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
        soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=6.5, duration=2.0, node=suit)
        suitTrack = Sequence(MovieUtil.createSuitBustInterval(suit))
        suitTrack.append(Func(suit.setNeutralAnimation))
        talkTrack = Sequence(getSuitAnimTrack(attack))
        soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', delay=0.5)
        soundTrack2 = getSoundTrack('SA_bash.ogg', delay=5.0, node=suit)
        if dmg > 0:
            toonTracks.append(toonTrack)
            propTracks.append(propTrack)
            soundTracks.append(soundTrack)
            suitTracks.append(suitTrack)
            talkTracks.append(talkTrack)
            soundTracks.append(soundTrack1)
            soundTracks.append(soundTrack2)
    toonDamageTrack = getToonTracksCheat(attack, 6.5, ['nothing'], 0, ['neutral'])
    return Parallel(talkTracks, toonDamageTrack, suitTracks, toonTracks, soundTracks, propTracks)

def doWheelSpin(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit))
    if not suit.dna.name == 'hroller2':
        suitTrack.append(Func(suit.makeImmortal))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg')
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    suitTrack.append(Func(suit.setNeutralAnimation))
    return Parallel(suitTrack, soundTrack1, soundTrack1, soundTrack2, soundTrack3)

def doDiceRoulette(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['name']
    suitTrack = Sequence(MovieUtil.createSuitLaughIntervalDice(suit), Func(suit.setNeutralAnimation))
    suitTrack2 = Sequence(getSuitAnimTrack(attack))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg')
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=4.75, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel2.ogg', delay=0.75, node=suit)
    soundTrack = Parallel(soundTrack3)
    if name == 'HighRollerDiceRouletteCogs':
        suitTrack.append(doDiceRouletteCogs(attack))
    elif name == 'HighRollerDiceRouletteToons':
        suitTrack.append(doDiceRouletteToons(attack))
    elif name == 'HighRollerDiceRouletteEveryone':
        suitTrack.append(doDiceRouletteAll(attack))
    elif name == 'HighRollerDiceRouletteNobody':
        suitTrack.append(doDiceRouletteNothing(attack))
    return Parallel(suitTrack, soundTrack, suitTrack2)

def doWheelSpin2(attack):
    suit = attack['suit']
    battle = attack['battle']
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit), ActorInterval(suit, 'snap'), Func(suit.setNeutralAnimation))
    talkTrack = Sequence(Wait(8.0), Func(suit.setChatAbsolute, "Alright, alright, let'ff get thoffe efftraff on ffet, baby doll. Bring 'em in.", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Peep your eyeff, we've got ffo much in fftore today for you!", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg')
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack4 = getSoundTrack('SA_bash.ogg', delay=8.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4))
    suitTrack.append(Wait(2.0))
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeShielding))
    return Parallel(talkTrack, suitTrack, soundTrack)

def doDiceRouletteCogs(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    taunt = random.choice(
        ["WHAT A TWIFFT!!!",
         "'FFLAM!' What a ffweet ffound!",
         "Now, you ffigned up for thiff!",
         "Here it comeff, boyff!", ])
    suitTrack = Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    smokeTracks = Parallel()
    for suit in battle.activeSuits:
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, suit),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 2.01)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 3)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2.01)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        propTracks.append(propTrack)
        if suit.dna.name == 'hroller2':
            toonTrack = Sequence(
                Wait(1.5),
                Parallel(
                    ActorInterval(suit, 'flatten'),
                    Func(suit.setHealthForMe, -25),
                    Func(suit.showHpText, -25),
                    Func(suit.updateHealthBar, 0)
                ))
            toonTrack.append(
                    Func(suit.setNeutralAnimation))
            toonTracks.append(toonTrack)
        else:
            toonTrack = Sequence(
                Wait(1.5),
                Parallel(
                    ActorInterval(suit, 'flatten'),
                    Func(suit.setHealthForMe, -250),
                    Func(suit.showHpText, -250),
                    Func(suit.updateHealthBar, 0)
                ))
            toonTrack.append(
                Func(suit.setNeutralAnimation))
            toonTracks.append(toonTrack)
        smokeTracks.append(smokeTrack)
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, duration=2.0, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack)

def doDiceRouletteNothing(attack):
    suit = attack['suit']
    taunt = random.choice(
        ["Look'ff like nuffin!", "Aww ratff, a total bufft!!",
         "Ffhew! Now that waff a cloffe call, waffn't it, folkff?",
         "Lady Luck iff merffiful today, huh?",
         "And THAT iff why they call you our LUCKY contefftantff!"])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Wait(2.0))
    suitTrack.append(Wait(1.0))
    return suitTrack

def doChoreography(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack)
    toonTracks = getToonTracks(attack, 4.1, ['cringe'], 4.1, ['victory'])
    soundTrack = getSoundTrack('AA_heal_happydance.ogg', delay=.01, node=suit)
    return Parallel(suitTrack, soundTrack, toonTracks)

def doDiceRouletteAll(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    taunt = random.choice(
        ["WHAT A TWIFFT!!!",
         "'FFLAM!' What a ffweet ffound!",
         "Now, you ffigned up for thiff!",
         "Here it comeff, boyff!", ])
    suitTrack = Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    propTracks2 = Parallel()
    toonTracks2 = Parallel()
    smokeTracks = Parallel()
    smokeTracks2 = Parallel()
    for suit in battle.activeSuits:
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2.5), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 2.01)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 3)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2.01)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, suit),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        propTracks.append(propTrack)
        toonTrack = Sequence(
            Wait(1.5),
            Parallel(
                ActorInterval(suit, 'flatten'),
                Func(suit.setHealthForMe, - (250 * len(battle.activeToons))),
                Func(suit.showHpText, - (250 * len(battle.activeToons))),
                Func(suit.updateHealthBar, 0)
            ))
        toonTrack.append(
            Func(suit.setNeutralAnimation))
        toonTracks.append(toonTrack)
        smokeTracks.append(smokeTrack)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack2 = Sequence(Wait(1.75), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        propTrack2 = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))

        propTracks2.append(propTrack2)
        toonTrack2 = Sequence(
            Wait(1.75),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(__doDamage, toon, dmg, t['died'])
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
        toonTracks2.append(toonTrack2)
        smokeTracks2.append(smokeTrack2)
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, duration=2.0, node=suit)
    return Parallel(suitTrack, toonTracks, toonTracks2, propTracks2, propTracks, soundTrack)

def doCommercialBreak(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = attack['target']
    suitTracks = Parallel()
    suitTrackHighRoller = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(MovieUtil.createSuitSnapInterval(theSuit), Func(theSuit.setNeutralAnimationDrop))
    suitTrackHighRoller.append(Wait(3.0))
    soundTrack = getSoundTrack('SA_bash.ogg')
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        if not suit.dna.name == 'hroller':
            suitTrack.append(Wait(1.0))
            suitTrack.append(Parallel(ActorInterval(suit, 'soak', endTime=1), MovieUtil.shortCircuitTrack2(suit, battle)))
        suitTracks.append(suitTrack)
    return Parallel(suitTracks, suitTrack2, soundTrack, suitTrackHighRoller)

def doDiceRouletteToons(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    taunt = random.choice(
        ["Can't ffquaffh and fftretch your way out of thiff one, Toonff!", "Who'ff ready for ffome cartoon violenffe?!",
         "FForry, babe, but the ratingff don't lie! Thiff iff what the viewerff want!",
         "And the ratingff FFKYROCKET!!!",
         "If it meanff anything, thiff iff gonna hurt me a lot more than it hurtff you!",
         "'Ker-ffplat!' HahaHAHA!!! You Toonff really are funny!"])
    suitTrack = Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
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
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 1)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
            Wait(1.5),
            LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
        ))
        toonTrack = Sequence(
        Wait(1.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
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
        soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, duration=2.0, node=suit)
        suitTrack.append(Func(suit.setNeutralAnimation))
        if dmg > 0:
            toonTracks.append(toonTrack)
            soundTracks.append(soundTrack)
            propTracks.append(propTrack)
            smokeTracks.append(smokeTrack)
    return Parallel(suitTrack, toonTracks, soundTracks, propTracks)

def doDamageReduction(attack):
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
            Func(toon.showHpTextNew,  - int(dmg), text="DAZED?!", colorCode=1),
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
            toonTracks.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 1)))
            toonTracks.append(Parallel(Func(toon.checkDamageDown, 50)))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    toonDamageTrack = getToonTracksCheat(attack, 1.75, ['nothing'], 0, ['neutral'])
    return Parallel(suitTrack, toonDamageTrack, smokeTracks, toonTracks, soundTrack, propTracks)

def doGameTimeCog2(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]
    soundTrack3 = getSoundTrack('cc_s_bgm_ara_hroller_int_stinger.ogg', node=manager)
    taunt = random.choice(("Well, babe, let'ff not keep them waiting! HAHAHA!!!",
"Come on, babe, FFHOW UFF THOFFE NUMBERFF!",
"Better hope for ffome HIGH ROLLERFF! HAHAHAHA!",
"Ready to find out which one of you iff really the weakefft link?!",
"WAFFN'T THAT FUN? Let'ff ffee how you did!"))
    x = int((targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP)
    cage = globalPropPool.getProp('ttcc_gag_stagelight')
    texture = loader.loadTexture('phase_5/maps/battle/ttcc_gag_stagelight.png')
    texture2 = loader.loadTexture('phase_3/maps/ttcc_lights_palette.png')
    cage.find('**/stagelight').setTexture(texture, 1)
    cage.find('**/spotlight').setTexture(texture2, 1)
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    suitPos = targetSuit.getPos(battle)
    y = suitPos.getY()
    cage2 = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_promoted')
    cagePos2 = [Point3(suitPos.getX(), y, 0), VBase3(0, 0, 0)]
    cagePropTrack2 = Sequence(
                             getPropAppearTrack(cage2, battle, cagePos2, .5, scaleUpPoint=Point3(1), scaleUpTime=0.1),
                             Parallel(
                                 cage2.posInterval(0.5, Point3(suitPos.getX(), y, 0.1), blendType='easeIn'),
                             ),
                             Wait(13),
                             LerpFunctionInterval(cage2.setAlphaScale, fromData=1, toData=0, duration=1.0),
                             LerpScaleInterval(cage2, .25, MovieUtil.PNT3_ZERO),
                             Func(MovieUtil.removeProp, cage2)
                             )
    cagePos = [Point3(0, 0, targetSuit.height + 15), targetSuit.getHpr(battle)]
    for headPart in targetSuit.headParts:
        head = headPart
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, targetSuit, cagePos, 1, scaleUpPoint=Point3(1.5, 1.5, 1.5), scaleUpTime=0),
        Wait(13), Parallel(SoundInterval(globalBattleSoundCache.getSound('AA_cog_shock.ogg')),
        Func(cage.find('**/spotlight').hide),
        Parallel(cagePosition, Func(cage.reparentTo, head)),
        Parallel(cage.posInterval(0.1, Point3(0, 0, 0), blendType='easeIn'))), Wait(1),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
        )
    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.setNeutralAnimation), Wait(18.0))
    managerTrackQuestion = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "In the standard Sellbot Factory, what is the name of the Factory Foreman's special ability?",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                       taunt,
                                                       CFSpeech | CFTimeout), Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3, Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "Ha-HA!",
                                                       CFSpeech | CFTimeout))))))
    suitTrackQuestion = Sequence(Wait(1.0), Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                       "It's my time to shine!", CFSpeech | CFTimeout), Func(targetSuit.setNeutralAnimation)), Wait(3.0), Func(targetSuit.setChatAbsolute,
                                                       "Union Bust!", CFSpeech | CFTimeout), Wait(7.0), Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack2(targetSuit, battle))
    managerTrackQuestion2 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Who does the Major Player fancy?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion2 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Nobody!", CFSpeech | CFTimeout), Wait(7.0),
                                 Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack2(targetSuit, battle))
    managerTrackQuestion3 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Which hand does the Head Attorney use during 'Objection'?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion3 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Right!", CFSpeech | CFTimeout), Wait(7.0),
                                 Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack2(targetSuit, battle))
    managerTrackQuestion4 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "TRUE or FALSE: The longest employee position name int he company is the Public Relations Representative?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion4 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "FALSE!", CFSpeech | CFTimeout), Wait(7.0),
                                 Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack2(targetSuit, battle))
    managerTrackQuestion5 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Who is the Name Dropper planning on having lunch with?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion5 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "The Mingler!", CFSpeech | CFTimeout), Wait(7.0),
                                 Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack2(targetSuit, battle))
    managerTrackQuestion6 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                              "What does the acronym C.O.G.S. stand for?",
                                                              CFSpeech | CFTimeout),
                                              Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                       taunt,
                                                                       CFSpeech | CFTimeout),
                                                       Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                                Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                         "Ha-HA!",
                                                                                         CFSpeech | CFTimeout))))))
    suitTrackQuestion6 = Sequence(Wait(1.0),
                                  Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                            "It's my time to shine!",
                                                                                            CFSpeech | CFTimeout),
                                           Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                  Func(targetSuit.setChatAbsolute,
                                       "Crush Organics until Green and Sad!", CFSpeech | CFTimeout), Wait(7.0),
                                  Func(targetSuit.loop, 'large-zap'), MovieUtil.shortCircuitTrack2(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(14), Func(targetSuit.showHpTextNew,  - targetSuit.currHP, text="WRONG ANSWER!", colorCode=3),
                               Func(targetSuit.setHealthForMe, - targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, 0))
    suitTrack = random.choice((Parallel(managerTrackQuestion, suitTrackQuestion), Parallel(managerTrackQuestion2, suitTrackQuestion2), Parallel(managerTrackQuestion3, suitTrackQuestion3)
                               , Parallel(managerTrackQuestion5, suitTrackQuestion5), Parallel(managerTrackQuestion6, suitTrackQuestion6), Parallel(managerTrackQuestion4, suitTrackQuestion4)))
    suitTrack.append(Wait(2.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=manager))
    soundTrack2 = getSoundTrack('LB_camera_shutter_2.ogg', delay=1, node=manager)
    return Parallel(managerTrack, suitTrack, soundTrack, cagePropTrack2, soundTrack2, cagePropTrack, selfDamageTrack)

def doGameTimeCog(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]
    soundTrack3 = getSoundTrack('cc_s_bgm_ara_hroller_int_stinger.ogg', node=manager)
    taunt = random.choice(("Well, babe, let'ff not keep them waiting! HAHAHA!!!",
"Come on, babe, FFHOW UFF THOFFE NUMBERFF!",
"Better hope for ffome HIGH ROLLERFF! HAHAHAHA!",
"Ready to find out which one of you iff really the weakefft link?!",
"WAFFN'T THAT FUN? Let'ff ffee how you did!"))
    x = int((targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP)
    cage = globalPropPool.getProp('ttcc_gag_stagelight')
    texture = loader.loadTexture('phase_5/maps/battle/ttcc_gag_stagelight.png')
    texture2 = loader.loadTexture('phase_3/maps/ttcc_lights_palette.png')
    cage.find('**/stagelight').setTexture(texture, 1)
    cage.find('**/spotlight').setTexture(texture2, 1)
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    suitPos = targetSuit.getPos(battle)
    y = suitPos.getY()
    cagePos = [Point3(0, 0, targetSuit.height + 15), targetSuit.getHpr(battle)]
    cage2 = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_promoted')
    cagePos2 = [Point3(suitPos.getX(), y, 0), VBase3(0, 0, 0)]
    cagePropTrack2 = Sequence(
        getPropAppearTrack(cage2, battle, cagePos2, .5, scaleUpPoint=Point3(1), scaleUpTime=0.1),
        Parallel(
            cage2.posInterval(0.5, Point3(suitPos.getX(), y, 0.1), blendType='easeIn'),
        ),
        Wait(13),
        LerpFunctionInterval(cage2.setAlphaScale, fromData=1, toData=0, duration=1.0),
        LerpScaleInterval(cage2, .25, MovieUtil.PNT3_ZERO),
        Func(MovieUtil.removeProp, cage2)
    )
    for headPart in targetSuit.headParts:
        head = headPart
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, targetSuit, cagePos, 1, scaleUpPoint=Point3(1.5, 1.5, 1.5), scaleUpTime=0),
        Wait(13), Parallel(SoundInterval(globalBattleSoundCache.getSound('AA_cog_shock.ogg')),
        Func(cage.find('**/spotlight').hide),
        Parallel(cagePosition, Func(cage.reparentTo, head)),
        Parallel(cage.posInterval(0.1, Point3(0, 0, 0), blendType='easeIn'))),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
    )
    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.setNeutralAnimation), Wait(18.0))
    managerTrackQuestion = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "In the standard Sellbot Factory, what is the name of the Factory Foreman's special ability?",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                       taunt,
                                                       CFSpeech | CFTimeout), Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3, Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "Ha-HA!",
                                                       CFSpeech | CFTimeout))))))
    suitTrackQuestion = Sequence(Wait(1.0), Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                       "It's my time to shine!", CFSpeech | CFTimeout), Func(targetSuit.setNeutralAnimation)), Wait(3.0), Func(targetSuit.setChatAbsolute,
                                                       "Worker's Compensation!", CFSpeech | CFTimeout), Wait(7.0), ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion2 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Who does the Major Player fancy?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion2 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Himself!", CFSpeech | CFTimeout), Wait(7.0),
                                 ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion3 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Which hand does the Head Attorney use during 'Objection'?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion3 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Left!", CFSpeech | CFTimeout), Wait(7.0),
                                 ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion4 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "TRUE or FALSE: The longest employee position name int he company is the Public Relations Representative?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion4 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "TRUE!", CFSpeech | CFTimeout), Wait(7.0),
                                 ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion5 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                             "Who is the Name Dropper planning on having lunch with?",
                                                             CFSpeech | CFTimeout),
                                             Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                      taunt,
                                                                      CFSpeech | CFTimeout),
                                                      Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                               Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                        "Ha-HA!",
                                                                                        CFSpeech | CFTimeout))))))
    suitTrackQuestion5 = Sequence(Wait(1.0),
                                 Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                           "It's my time to shine!",
                                                                                           CFSpeech | CFTimeout),
                                          Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                 Func(targetSuit.setChatAbsolute,
                                      "Mr. Hollywood!", CFSpeech | CFTimeout), Wait(7.0),
                                 ActorInterval(targetSuit, 'large-zap')
                                 , Func(targetSuit.setNeutralAnimation))
    managerTrackQuestion6 = Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                              "What does the acronym C.O.G.S. stand for?",
                                                              CFSpeech | CFTimeout),
                                              Sequence(Wait(5.0), Func(manager.setChatAbsolute,
                                                                       taunt,
                                                                       CFSpeech | CFTimeout),
                                                       Parallel(ActorInterval(manager, 'song-and-dance'), soundTrack3,
                                                                Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                                                         "Ha-HA!",
                                                                                         CFSpeech | CFTimeout))))))
    suitTrackQuestion6 = Sequence(Wait(1.0),
                                  Parallel(ActorInterval(targetSuit, 'mob-mentality'), Func(targetSuit.setChatAbsolute,
                                                                                            "It's my time to shine!",
                                                                                            CFSpeech | CFTimeout),
                                           Func(targetSuit.setNeutralAnimation)), Wait(3.0),
                                  Func(targetSuit.setChatAbsolute,
                                       "Coal, Oil, and Gas Syndicate!", CFSpeech | CFTimeout), Wait(7.0),
                                  ActorInterval(targetSuit, 'large-zap')
                                  , Func(targetSuit.setNeutralAnimation))
    selfDamageTrack = Sequence(Wait(16), Func(targetSuit.showHpTextNew, x, text="OVERCHARGED!", colorCode=1),
                               Func(targetSuit.setHealthForMe, int(targetSuit.maxHP)), Func(targetSuit.setHP,  int(targetSuit.maxHP * 2)), Func(targetSuit.makeExtraAttacks, targetSuit.getExtraAttacks() + 1),
                               Func(targetSuit.updateHealthBar, 0), Wait(2.0), Func(targetSuit.showHpTextWhite, '+1 ATTACK!'))
    suitTrack = random.choice((Parallel(managerTrackQuestion, suitTrackQuestion), Parallel(managerTrackQuestion2, suitTrackQuestion2), Parallel(managerTrackQuestion3, suitTrackQuestion3)
                               , Parallel(managerTrackQuestion5, suitTrackQuestion5), Parallel(managerTrackQuestion6, suitTrackQuestion6), Parallel(managerTrackQuestion4, suitTrackQuestion4)))
    suitTrack.append(Wait(2.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=manager))
    soundTrack2 = getSoundTrack('LB_camera_shutter_2.ogg', delay=1, node=manager)
    soundTrack5 = getSoundTrack('LB_toonup.ogg', delay=16, node=manager)
    return Parallel(managerTrack, suitTrack, soundTrack, soundTrack2, cagePropTrack2, cagePropTrack, soundTrack5, selfDamageTrack)

def doConduction(attack):
    suit = attack['suit']
    battle = attack['battle']
    propDelay = 0.6
    throwDelay = 1.3
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    allDuckTracks = Parallel()
    squishDuck = lambda duck: Sequence(LerpScaleInterval(duck, 0.25, Point3(6.25, 6.25, 2.5)),
                                       LerpScaleInterval(duck, 0.1, Point3(5)))
    for t in attack['target']:
        toon = t['toon']
        duckTracks = Parallel()
        for i in xrange(0, random.randint(7, 10)):
            x = random.random() / 5
            if random.choice([False, True]):
                x *= -1
            y = random.random() / 5
            if random.choice([False, True]):
                y *= -1
            next = loader.loadModel('phase_5/models/props/cc_m_bat_prp_duck_hroller')
            posPoints = [Point3(x, y, -0.5), VBase3(0, 0, 180)]
            duckLandX = (toon.getX(battle) - 0.05) + random.random()
            duckLandY = (toon.getY(battle) - 0.05) + random.random()
            duckTrack = Sequence(
                getPropAppearTrack(next, suit.getRightHand(), posPoints, propDelay, scaleUpPoint=Point3(2.5)),
                Wait(throwDelay - propDelay + random.random()),
                Parallel(
                    getThrowTrack(next, Point3(duckLandX, duckLandY + 5, 0.5), parent=battle),
                    LerpHprInterval(next, 1.0, VBase3(180, 0, 0)),
                    LerpScaleInterval(next, 1.0, Point3(5))
                ),
                squishDuck(next),
                getThrowTrack(next, Point3(duckLandX, duckLandY, 0.5), duration=0.25, parent=battle, gravity=-96.432),
                squishDuck(next),
                getThrowTrack(next, Point3(duckLandX, duckLandY - 5, 0.5), duration=0.25, parent=battle,
                              gravity=-96.432),
                LerpScaleInterval(next, 0.25, Point3(6.25, 6.25, 2.5)),
                LerpScaleInterval(next, 0.25, MovieUtil.PNT3_NEARZERO),
                Func(next.removeNode)
            )
            duckTracks.append(duckTrack)

        allDuckTracks.append(duckTracks)
    suitTrack.append(Func(suit.makeNonImmortal))
    damageAnims = [['cringe', 0.01, 0.14, 0.21],
                   ['cringe', 0.01, 0.14, 0.13],
                   ['cringe', 0.01, 0.43]]
    toonTracks = getToonTracks(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8,
                               dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('cc_s_sfx_ene_hroller_conducktion.ogg', delay=throwDelay, node=suit)
    return Parallel(suitTrack, allDuckTracks, toonTracks, soundTrack)


def doRaisingTheAnte(attack):
    '''
    A battle animation to give Toons the damage boost based on the Raising the Ante status effect in Corporate Clash.
    author: Professor Control
    '''
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitAnimTrack(attack)
    # suitTrack.append(doWheelSpin2(attack))
    partTracks = Parallel()
    explosionTracks = Parallel()  # It seems fitting this source gets to make Toons explode to have their ante raised.
    toonTracks = getToonTracks(attack, 2.0, ['slip-backward'], 2.0, ['shrug'])

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

        # I never got to make an actual particle effect work, so I settled for making a faux particle effect.
        numArrows = 15  # I don't know how long we want the particle effect to go on for, but we can change that depending on how many arrows we want.
        radius = 2.0
        partTrack = Parallel()
        for i in xrange(numArrows):
            # Create the arrow.
            arrow = loader.loadModel('phase_3.5/models/gui/matching_game_gui').find(
                '**/minnieArrow')  # Get an arrow immediately.
            arrow.setScale(5.0)  # Maybe could be adjusted?
            arrow.setBillboardPointEye()  # This could increase how much of a particle effect it's intended to look like.
            arrow.setR(270)  # Arrow points up.
            color = random.choice([(1, 0, 0, 1),
                                   (1, 1, 0, 1),
                                   (0, 0, 1,
                                    1)])  # Color the arrows according to these colors as that is what the status effect icon looks like.
            arrow.setColor(*color)

            # Now get the position of the arrow.
            angle = random.random() * 2.0 * math.pi  # Have a random angle decided.  360-degree limit, but due to the angle being in radians, use such units.  360 degrees in radians is 2 times pi.
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
            explosionTracks.append(Parallel(Func(toon.makeDamageUpGovernaught)))
            explosionTracks.append(Parallel(Func(toon.checkDamageUpGovernaught, toon.getDamageUpGovernaught() + 1250)))
    soundTrack1 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=2.0)

    return Parallel(suitTrack, partTracks, explosionTracks, soundTrack1, toonTracks)



