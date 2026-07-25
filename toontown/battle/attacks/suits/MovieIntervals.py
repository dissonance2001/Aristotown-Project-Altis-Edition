from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from toontown.effects import DustCloud
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


def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.setNeutralAnimationAttack))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def getResetTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0
    unluredTrack = Func(battle.unlureSuit, suit)
    unSuedTrack = Func(battle.unSueSuit, suit)
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), Func(suit.setNeutralAnimationAttack))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, unSuedTrack, walkTrack, moveTrack)


def doDefault(attack):
    notify.debug('building suit attack in doDefault')
    suitName = attack['suitName']
    attack['name'] = 'SoakRemoval'
    attack['animName'] = 'nothing'
    return MovieUniversalCheats.SoakRemoval(attack)

def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    neutralTrack =  Func(suit.setNeutralAnimationAttack)
    unluredTrack = Func(battle.unlureSuit, suit)
    updateTrack = Func(battle.unSueSuit, suit)
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), neutralTrack)
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(unluredTrack, updateTrack, walkTrack, moveTrack)


def getSuitTrack(attack, delay = 1e-06, splicedAnims = None, playRate = 1.0, disrespectBlend=False):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target[0]['toon']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
    origH = suit.getH(battle)

    # Calculate heading to toon
    targets = attack['target']
    origPos, origHpr = battle.getActorPosHpr(suit)
    # for t in targets:
    #     toon = t['toon']
    #     track.append(Func(toon.headsUp, origPos))
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
    elif attack['suitName'] in ['cinema', 'choreo', 'fmaker'] and attack['name'] == 'SmokeAndMirrors' and not attack['suit'].isSkeleton:  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'fires' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'payman' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
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
        elif attack['suitName'] in ['cinema', 'choreo', 'fmaker'] and attack['name'] == 'SmokeAndMirrors' and not attack['suit'].isSkeleton:
            track.append(ActorInterval(suit, 'headhoncho-cigar-smoke', playRate=playRate))
        elif attack['suitName'] == 'payman' and attack['name'] == 'CigarSmoke' and not attack['suit'].isSkeleton:
            track.append(ActorInterval(suit, 'headhoncho-cigar-smoke', playRate=playRate))
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
    if not attack['name'] == 'BroadcasterDonation' and not attack['name'] == 'ScapegoatEnraged' and not attack['name'] == 'AmbassadorHeadRollerGroup':
            if not attack['animName'] == 'none' and not attack['animName'] == 'nothing':
                if not disrespectBlend == True:
                    track.append(
                suit.makeBlendInterval(shuffleAnim))
                else:
                    track.append(
                    Func(suit.setNeutralAnimationDrop))
    return track

def getToonGroupCenter(attack, battle):
    targets = attack.get('target', [])
    points = []

    for toon in battle.activeToons:
        points.append(toon.getPos(battle))

    if not points:
        return None

    avg = Point3(0, 0, 0)
    for p in points:
        avg += p

    avg /= float(len(points))
    return avg

def getSuitAnimTrackAttack(attack, delay = 0, splicedAnims = None, playRate = 1.0, disrespectBlend=False):
    suit = attack['suit']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
    unsueTrack = Func(battle.unSueSuit, suit)
    origH = suit.getH(battle)
    targets = attack['target']
    origPos, origHpr = battle.getActorPosHpr(suit)
    origPos2 = suit.getPos(battle)

    suit.setPos(battle, origPos)

    targetPos = getToonGroupCenter(attack, battle)
    if targetPos is None:
        target = attack['target']
        toon = target[0]['toon']
        targetPos = toon.getPos(battle)

    suit.headsUp(battle, targetPos)
    targetH = suit.getH(battle)

    suit.setH(battle, origH)
    suit.setPos(battle, origPos2)

    suitActualPos = suit.getPos(battle)

    for t in targets:
        toon = t['toon']
        track.append(Func(toon.headsUp, battle, suitActualPos))

    delta = (targetH - origH + 180) % 360 - 180
    # for s in battle.activeSuits:
    #     if s.dna.name == 'psetter':
    #         theSuit = s
    #         track.append(Func(s.setPlayRate2, theSuit.getPlayRate2() + .5))
    if attack['suitName'] == 'radiog' and attack[
        'name'] == 'RadiographerRadioInfrequency':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack[
        'name'] == 'RacketeerPeckingOrderRetaliationSoak':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'erfit' and attack[
        'name'] == 'ErfitPersonalTrainer':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'erfit' and attack[
        'name'] == 'ErfitGainsFromTheScrap':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack[
        'name'] == 'SafetySoakRetaliation':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
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
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured2':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured3':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured4':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured5':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'HighRollerBust':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'ContingencyRedundantAuthority':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'ContingencyRiskThresholdBreach':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
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
    elif attack[
        'name'] == 'BroadcasterDonation2':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cbutcher' and attack[
        'name'] == 'ButcherRevvingUp':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cbutcher' and attack[
        'name'] == 'ButcherRevvingUpWhipsaw':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cbutcher' and attack[
        'name'] == 'ButcherSparkPlug':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cbutcher' and attack[
        'name'] == 'ButcherScabbard':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterMandatoryToll':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterMandatoryTollFinal':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger2':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger3':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger4':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger5':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    track.append(Sequence(
        LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle)))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
        # elif suit.isImmortal and suit.dna.name == 'dsf':
        #     track.append(
        #        Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        # elif suit.isVulnerable and suit.dna.name == 'crf':
        #    track.append(
        #       Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        # elif suit.isImmortal:
        #    track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        #  track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    if delta > 0:
        shuffleAnim = 'shuffle-right'
    else:
        shuffleAnim = 'shuffle-left'

    track.append(
        Parallel(
            ActorInterval(suit, shuffleAnim),
            LerpHprInterval(
                suit,
                suit.getDuration(shuffleAnim),
                (origH, 0, 0),
                startHpr=(origH + delta, 0, 0),
                other=battle
            )
        )
    )
    if attack['name'] == 'AmbassadorHeadRollerGroup':
        track.append(
            Func(suit.loop, 'neutral-override'))
    elif attack['name'] == 'ScapegoatEnraged':
        track.append(
            Func(suit.loop, 'neutral-enraged'))
    else:
        if not attack['name'] == 'BroadcasterDonation' and not attack['name'] == 'ScapegoatEnraged' and not attack['name'] == 'AmbassadorHeadRollerGroup':
            if not attack['animName'] == 'none' and not attack['animName'] == 'nothing':
                if not disrespectBlend == True:
                    track.append(
                suit.makeBlendInterval(shuffleAnim))
                else:
                    track.append(
                    Func(suit.setNeutralAnimationDrop))
    track.append(unsueTrack)
    return track


def getSuitAnimTrack(attack, delay = 0, splicedAnims = None, playRate = 1.0, disrespectBlend=False):
    suit = attack['suit']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
    unsueTrack = Func(battle.unSueSuit, suit)
    # for s in battle.activeSuits:
    #     if s.dna.name == 'psetter':
    #         theSuit = s
    #         track.append(Func(s.setPlayRate2, theSuit.getPlayRate2() + .5))
    if attack['suitName'] == 'radiog' and attack[
        'name'] == 'RadiographerRadioInfrequency':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack[
        'name'] == 'RacketeerPeckingOrderRetaliationSoak':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'erfit' and attack[
        'name'] == 'ErfitPersonalTrainer':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'erfit' and attack[
        'name'] == 'ErfitGainsFromTheScrap':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack[
        'name'] == 'SafetySoakRetaliation':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyHeatWave':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'hustle' and attack['name'] == 'HustlerClosingTime':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyViolation':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['name'] == 'ScapegoatEnraged':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['name'] == 'LitigatorBayouBash':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['name'] == 'CaseManagerInsurancePlan2':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['name'] == 'CaseManagerInsurancePlan':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['name'] == 'CaseManagerLegalBindings2':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'RacketeerPeckingOrderRetaliation':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cdirector' and attack['name'] in (
        'BanLevel4', 'BanLevel5', 'BanLevel6', 'BanLevel7', 'BanLevel8',
        'BanLevel45', 'BanLevel46', 'BanLevel47', 'BanLevel48',
        'BanLevel56', 'BanLevel57', 'BanLevel58',
        'BanLevel67', 'BanLevel68', 'BanLevel78',

        'BanToonup', 'BanTrap', 'BanLure', 'BanThrow',
        'BanSquirt', 'BanZap', 'BanSound', 'BanDrop',

        'BanToonupTrap', 'BanToonupLure', 'BanToonupThrow', 'BanToonupSquirt',
        'BanToonupZap', 'BanToonupSound', 'BanToonupDrop',

        'BanTrapLure', 'BanTrapThrow', 'BanTrapSquirt', 'BanTrapZap',
        'BanTrapSound', 'BanTrapDrop',

        'BanLureThrow', 'BanLureSquirt', 'BanLureZap',
        'BanLureSound', 'BanLureDrop',

        'BanThrowSquirt', 'BanThrowZap', 'BanThrowSound', 'BanThrowDrop',

        'BanSquirtZap', 'BanSquirtSound', 'BanSquirtDrop',

        'BanZapSound', 'BanZapDrop',

        'BanSoundDrop'
    ):  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured2':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured3':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured4':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'safesupervis' and attack['name'] == 'SafetyOverpressured5':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
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
        'name'] == 'ContingencyRedundantAuthority':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack[
        'name'] == 'ContingencyRiskThresholdBreach':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
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
    elif attack[
        'name'] == 'BroadcasterDonation2':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cbutcher' and attack[
        'name'] == 'ButcherRevvingUp':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cbutcher' and attack[
        'name'] == 'ButcherRevvingUpWhipsaw':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cbutcher' and attack[
        'name'] == 'ButcherSparkPlug':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'cbutcher' and attack[
        'name'] == 'ButcherScabbard':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterMandatoryToll':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterMandatoryTollFinal':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger2':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger3':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger4':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    elif attack['suitName'] == 'liquid' and attack[
        'name'] == 'TollmasterBalanceTheLedger5':  # Special track for when Head Honchos use cigar smoke so the animations are no longer playing at the same time.
        track.append(Func(suit.setChatAbsoluteSpecial, taunt,
                          CFSpeech | CFTimeout))
    else:
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    if splicedAnims:
        track.append(getSplicedAnimsTrack(splicedAnims, actor=suit))
    else:
        track.append(ActorInterval(suit, attack['animName'], playRate=playRate))
        # elif suit.isImmortal and suit.dna.name == 'dsf':
        #     track.append(
        #        Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        # elif suit.isVulnerable and suit.dna.name == 'crf':
        #    track.append(
        #       Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        # elif suit.isImmortal:
        #    track.append(ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0))
        #  track.append(Func(suit.loop, 'highroller-neutral-levitate-loop'))
    if attack['name'] == 'AmbassadorHeadRollerGroup':
        track.append(
            Func(suit.loop, 'neutral-override'))
    elif attack['name'] == 'ScapegoatEnraged':
        track.append(
            Func(suit.loop, 'neutral-enraged'))
    else:
        if not attack['name'] == 'BroadcasterDonation' and not attack['name'] == 'ScapegoatEnraged' and not attack['name'] == 'AmbassadorHeadRollerGroup':
            if not attack['animName'] == 'none' and not attack['animName'] == 'nothing':
                if not disrespectBlend == True:
                    track.append(
                suit.makeBlendInterval('neutral'))
                else:
                    track.append(
                    Func(suit.setNeutralAnimationDrop))
    track.append(unsueTrack)
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
                                   LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)), LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                                 LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)),
                                 LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                                 LerpColorScaleInterval(indicator, 0.25, Vec4(1, 0, 0, 1)), LerpColorScaleInterval(indicator, 0.25, Vec4(0, 0, 0, 0)),
                          Func(indicator.reparentTo, hidden), Func(indicator.clearColorScale), Func(indicator.removeNode))
    if suit:
        if dmg > 0:
            animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
            origPos, origHpr = battle.getActorPosHpr(toon)
            if not attack['name'] == 'RacketeerExtortion' and not attack['name'] == 'ForemanExtortion' and not attack['name'] == 'RacketeerExtortion2' and not attack['name'] == 'PresidentSyphon':
                animTrack.append(Func(toon.setHpr, battle, origHpr))
            return Parallel(animTrack, indicatorTracks)
        else:
            animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
            indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
            origPos, origHpr = battle.getActorPosHpr(toon)
            animTrack.append(Func(toon.setHpr, battle, origHpr))
            return Parallel(animTrack, indicatorTrack, indicatorTracks)
    elif dmg > 0:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return Parallel(animTrack, indicatorTrack, indicatorTracks)


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
        suitPos, suitHpr = battle.getActorPosHpr(suit)
    toonPos = toon.getPos(battle)
    indicator = loader.loadModel('phase_5/models/effects/cc_m_txc_fx_bat_target_indicators')
    indicator.setHpr(0, -90, 0)
    indicator.setPos(toonPos.getX(), toonPos.getY(), .05)
    dmg = target['hp']
    animTrack = Sequence()
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
        animTrack.append(Func(toon.headsUp, battle, suitPos))
        animTrack.append(getToonTakeDamageTrackCheat(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
        return Parallel(animTrack, indicatorTracks)
    else:
        animTrack.append(Func(toon.headsUp, battle, suitPos))
        if attack['name'] == 'MintMovingGoalposts':
            for t in battle.activeToons:
                animTrack.append(Func(t.headsUp, battle, suitPos))
        if attack['name'] == 'HighRollerDamageReduction':
            for t in battle.activeToons:
                animTrack.append(Func(t.headsUp, battle, suitPos))
        if attack['name'] == 'HustlerBaitAndSwitch':
            for t in battle.activeToons:
                animTrack.append(Func(t.headsUp, battle, suitPos))
        if attack['name'] == 'ContingencyOperationalFreeze':
            for t in battle.activeToons:
                animTrack.append(Func(t.headsUp, battle, suitPos))
        if attack['name'] in ('VideographerHardCut', 'MintMovingGoalposts', 'HighRollerDamageReduction', 'HustlerBaitAndSwitch', 'ContingencyOperationalFreeze'):
            animTrack.append(getToonDodgeTrackCheat2(attack, target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        else:
            animTrack.append(getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        #indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        origPos, origHpr = battle.getActorPosHpr(toon)
        animTrack.append(Func(toon.setHpr, battle, origHpr))
        return animTrack


def getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    toon = target['toon']
    toonTrack = Sequence()
    toonTrack.append(Func(toon.loop, 'neutral'))
    return toonTrack

def getToonDodgeTrackCheat2(attack, target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    toon = target['toon']
    battle = attack['battle']
    toonTrack = Sequence()
    if attack['name'] == 'MintMovingGoalposts':
        for t in battle.activeToons:
            toonTrack.append(Wait(dodgeDelay))
            if dodgeAnimNames:
                for d in dodgeAnimNames:
                    if d == 'sidestep':
                        toonTrack.append(getAllyToonsDodgeParallel(target))
                    else:
                        toonTrack.append(ActorInterval(t, d))

            else:
                toonTrack.append(getSplicedAnimsTrack(splicedDodgeAnims, actor=t))
            toonTrack.append(Func(t.loop, 'neutral'))
    elif attack['name'] == 'HighRollerDamageReduction':
        for t in battle.activeToons:
            toonTrack.append(Wait(dodgeDelay))
            if dodgeAnimNames:
                for d in dodgeAnimNames:
                    if d == 'sidestep':
                        toonTrack.append(getAllyToonsDodgeParallel(target))
                    else:
                        toonTrack.append(ActorInterval(t, d))

            else:
                toonTrack.append(getSplicedAnimsTrack(splicedDodgeAnims, actor=t))
            toonTrack.append(Func(t.loop, 'neutral'))
    elif attack['name'] == 'HustlerBaitAndSwitch':
        for t in battle.activeToons:
            toonTrack.append(Wait(dodgeDelay))
            if dodgeAnimNames:
                for d in dodgeAnimNames:
                    if d == 'sidestep':
                        toonTrack.append(getAllyToonsDodgeParallel(target))
                    else:
                        toonTrack.append(ActorInterval(t, d))

            else:
                toonTrack.append(getSplicedAnimsTrack(splicedDodgeAnims, actor=t))
            toonTrack.append(Func(t.loop, 'neutral'))
    elif attack['name'] == 'ContingencyOperationalFreeze':
        for t in battle.activeToons:
            toonTrack.append(Wait(dodgeDelay))
            if dodgeAnimNames:
                for d in dodgeAnimNames:
                    if d == 'sidestep':
                        toonTrack.append(getAllyToonsDodgeParallel(target))
                    else:
                        toonTrack.append(ActorInterval(t, d))

            else:
                toonTrack.append(getSplicedAnimsTrack(splicedDodgeAnims, actor=t))
            toonTrack.append(Func(t.loop, 'neutral'))
    elif attack['name'] == 'VideographerHardCut':
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
    else:
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
    sidestepAnim = random.choice(('sidestep-right', 'sidestep-left'))
    soundEffect = globalBattleSoundCache.getSound(random.choice(('AV_jump_to_side.ogg', 'AV_side_step.ogg')))
    toonTracks = Parallel()
    toonTracks.append(Sequence(ActorInterval(toon, sidestepAnim), Func(toon.loop, 'neutral')))
    toonTracks.append(Sequence(Wait(0.5), SoundInterval(soundEffect, node=toon)))
    return toonTracks


def getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5, startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0, animStartTime = 0.0):
    if anim == 1:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), ActorInterval(prop, propName, duration=animDuration, startTime=animStartTime), Wait(remainDelay), Func(MovieUtil.removeProp, prop))
    else:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), Wait(remainDelay), LerpScaleInterval(prop, scaleDownTime, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, prop))
    return track


def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None, blendType='noBlend'):
    propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
    if poseExtraArgs:
        propTrack.append(Func(prop.pose, *poseExtraArgs))
    propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale, blendType=blendType))
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

