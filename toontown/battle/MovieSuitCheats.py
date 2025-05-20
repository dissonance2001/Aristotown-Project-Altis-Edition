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


def doSuitCheat(cheat):
    #notify.debug('building suit attack in doSuitCheat: %s' % attack['name'])
    name = cheat['id']
    suit = cheat['suit']
    if name == TEST_CHEAT:
        suitTrack = doAcidRain(cheat)
    else:
        notify.warning('unknown attack: %d substituting Finger Wag' % name)
        suitTrack = doDefault(attack)
    camTrack = MovieCamera.chooseSuitShot(attack, suitTrack.getDuration())
    battle = cheat['battle']
    target = cheat['target']
    groupStatus = cheat['group']
    toonHprTrack = Parallel()
    for t in target:
        toon = t['toon']
        toonHprTrack.append(Sequence(Func(toon.headsUp, battle, MovieUtil.PNT3_ZERO), Func(toon.loop, 'neutral')))
    unlureSuit = Func(suit.makeUnLured)
    suitTrack = Sequence(unlureSuit, preWalkTrack, suitTrack, neutralIval, toonHprTrack)
    suitPos = suit.getPos(battle)
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    resetTrack = getResetTrack(suit, battle)
    resetSuitTrack = Sequence(unlureSuit, resetTrack, suitTrack)
    waitTrack = Sequence(Wait(resetTrack.getDuration()), Func(battle.unlureSuit, suit))
    resetCamTrack = Sequence(waitTrack, camTrack)
    return (resetSuitTrack, resetCamTrack)


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


def doDefault(attack):
    notify.debug('building suit attack in doDefault')
    suitName = attack['suitName']
    if suitName == 'f':
        attack['id'] = POUND_KEY
        attack['name'] = 'PoundKey'
        attack['animName'] = 'phone'
        return doPoundKey(attack)
    elif suitName == 'p':
        attack['id'] = FOUNTAIN_PEN
        attack['name'] = 'FountainPen'
        attack['animName'] = 'pen-squirt'
        return doFountainPen(attack)
    elif suitName == 'ym':
        attack['id'] = RUBBER_STAMP
        attack['name'] = 'RubberStamp'
        attack['animName'] = 'rubber-stamp'
        return doRubberStamp(attack)
    elif suitName == 'mm':
        attack['id'] = FINGER_WAG
        attack['name'] = 'FingerWag'
        attack['animName'] = 'finger-wag'
        return doFingerWag(attack)
    elif suitName == 'ds':
        attack['id'] = DEMOTION
        attack['name'] = 'Demotion'
        attack['animName'] = 'magic1'
        return doDemotion(attack)
    elif suitName == 'hh':
        attack['id'] = GLOWER_POWER
        attack['name'] = 'GlowerPower'
        attack['animName'] = 'glower'
        return doGlowerPower(attack)
    elif suitName == 'cr':
        attack['id'] = PICK_POCKET
        attack['name'] = 'PickPocket'
        attack['animName'] = 'pickpocket'
        return doPickPocket(attack)
    elif suitName == 'tbc':
        attack['id'] = GLOWER_POWER
        attack['name'] = 'GlowerPower'
        attack['animName'] = 'glower'
        return doGlowerPower(attack)
    elif suitName == 'cc':
        attack['id'] = POUND_KEY
        attack['name'] = 'PoundKey'
        attack['animName'] = 'phone'
        return doPoundKey(attack)
    elif suitName == 'tm':
        attack['id'] = CLIPON_TIE
        attack['name'] = 'ClipOnTie'
        attack['animName'] = 'throw-paper'
        return doClipOnTie(attack)
    elif suitName == 'nd':
        attack['id'] = PICK_POCKET
        attack['name'] = 'PickPocket'
        attack['animName'] = 'pickpocket'
        return doPickPocket(attack)
    elif suitName == 'gh':
        attack['id'] = FOUNTAIN_PEN
        attack['name'] = 'FountainPen'
        attack['animName'] = 'pen-squirt'
        return doFountainPen(attack)
    elif suitName == 'ms':
        attack['id'] = BRAIN_STORM
        attack['name'] = 'BrainStorm'
        attack['animName'] = 'effort'
        return doBrainStorm(attack)
    elif suitName == 'tf':
        attack['id'] = RED_TAPE
        attack['name'] = 'RedTape'
        attack['animName'] = 'throw-object'
        return doRedTape(attack)
    elif suitName == 'm':
        attack['id'] = BUZZ_WORD
        attack['name'] = 'BuzzWord'
        attack['animName'] = 'speak'
        return doBuzzWord(attack)
    elif suitName == 'mh':
        attack['id'] = RAZZLE_DAZZLE
        attack['name'] = 'RazzleDazzle'
        attack['animName'] = 'smile'
        return doRazzleDazzle(attack)
    elif suitName == 'sc':
        attack['id'] = WATERCOOLER
        attack['name'] = 'Watercooler'
        attack['animName'] = 'water-cooler'
        return doWatercooler(attack)
    elif suitName == 'pp':
        attack['id'] = BOUNCE_CHECK
        attack['name'] = 'BounceCheck'
        attack['animName'] = 'throw-paper'
        return doBounceCheck(attack)
    elif suitName == 'tw':
        attack['id'] = GLOWER_POWER
        attack['name'] = 'GlowerPower'
        attack['animName'] = 'glower'
        return doGlowerPower(attack)
    elif suitName == 'bc':
        attack['id'] = AUDIT
        attack['name'] = 'Audit'
        attack['animName'] = 'phone'
        return doAudit(attack)
    elif suitName == 'nc':
        attack['id'] = RED_TAPE
        attack['name'] = 'RedTape'
        attack['animName'] = 'throw-object'
        return doRedTape(attack)
    elif suitName == 'mb':
        attack['id'] = LIQUIDATE
        attack['name'] = 'Liquidate'
        attack['animName'] = 'magic1'
        return doLiquidate(attack)
    elif suitName == 'ls':
        attack['id'] = WRITE_OFF
        attack['name'] = 'WriteOff'
        attack['animName'] = 'hold-pencil'
        return doWriteOff(attack)
    elif suitName == 'rb':
        attack['id'] = TEE_OFF
        attack['name'] = 'TeeOff'
        attack['animName'] = 'golf-club-swing'
        return doTeeOff(attack)
    elif suitName == 'bf':
        attack['id'] = RUBBER_STAMP
        attack['name'] = 'RubberStamp'
        attack['animName'] = 'rubber-stamp'
        return doRubberStamp(attack)
    elif suitName == 'b':
        attack['id'] = EVICTION_NOTICE
        attack['name'] = 'EvictionNotice'
        attack['animName'] = 'throw-paper'
        return doEvictionNotice(attack)
    elif suitName == 'dt':
        attack['id'] = RUBBER_STAMP
        attack['name'] = 'RubberStamp'
        attack['animName'] = 'rubber-stamp'
        return doRubberStamp(attack)
    elif suitName == 'ac':
        attack['id'] = RED_TAPE
        attack['name'] = 'RedTape'
        attack['animName'] = 'throw-object'
        return doRedTape(attack)
    elif suitName == 'bs':
        attack['id'] = FINGER_WAG
        attack['name'] = 'FingerWag'
        attack['animName'] = 'finger-wag'
        return doFingerWag(attack)
    elif suitName == 'sd':
        attack['id'] = WRITE_OFF
        attack['name'] = 'WriteOff'
        attack['animName'] = 'hold-pencil'
        return doWriteOff(attack)
    elif suitName == 'le':
        attack['id'] = JARGON
        attack['name'] = 'Jargon'
        attack['animName'] = 'speak'
        return doJargon(attack)
    elif suitName == 'bw':
        attack['id'] = FINGER_WAG
        attack['name'] = 'FingerWag'
        attack['animName'] = 'finger-wag'
        return doFingerWag(attack)
    else:
        self.notify.error('doDefault() - unsupported suit type: %s' % suitName)
    return None

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
    name = attack['id']
    targetPos = toon.getPos(battle)
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    trapStorage = {}
    trapStorage['trap'] = None
    track = Sequence(Wait(delay))
    if attack[
        'suitName'] == 'csm':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif attack[
        'suitName'] == 'fbd':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif name == WHITE_POWDER:
        taunt = random.choice(
            ["I've got my eye on you!", "I'll poke you in the eye!", "'Eye' am as evil as they come!'",
             "Wait. I've got something in my eye.", "Could you keep an eye on this for me?",
             "I'm rolling my eye at you.", "I'll put you in the eye of the storm!", "Could you eye-ball this for me?",
             "I'm giving you the evil eye.", "I've got a real eye for evil."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == QUAKE and suit.isChainsawPhase2:
        taunt = random.choice(
            ["EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
             "UNCHARTED NUMBERS DETECTED ON THE RICHTER SCALE.",
             "COMMENCING OPERATION: QUAKE, RATTLE AND ROLL.",
"WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
"ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
"ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == QUAKE and suit.isChainsawPhase3:
        taunt = random.choice(
            ["EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",
"WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
"ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.",
             "UNCHARTED NU- pl- NUMBERS DETECT- please- DETECTED ON THE- help- RICHTER S- me- SCALE.",
             "COMMENCING- stop- OPERATION: QUAKE- stop- RATTLE- the- AND RO- override- ROLL.",
"ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == CANNED and suit.isChainsawPhase2:
        taunt = random.choice(
            ["EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
             "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
             "EXECUTING PROGRAM: 'KICK THE CAN' ROUTINE.",
                                              "ACTIVATING TOON-A CAN SEALING PROCESS.",
             "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
             "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == CANNED and suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",
                "WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
                "ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.",
                "EXECUTING- i- PROGRAM: 'KICK- can't- THE CAN' RO- help it- ROUTINE.",
"ACTIVATING- don't- TOON-A- want- CAN SE- to- SEALING PRO- fight you- PROCESS.",
                "ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == ROLODEX and suit.isChainsawPhase2:
        taunt = random.choice(
            ["EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
             "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
             "ATTEMPTING TO LOCATE TARGET'S EMPLOYMENT CARD.",
             "PROTOCOL FOR PEST EXTERMINATION HAS BEEN TRIGGERED.",
             "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
             "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == ROLODEX and suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",
                "WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
                "ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.",
                "ATTEMPTING- can't- TO LOCATE- hold- TARGET'S EMPLOY- out- EMPLOYMENT CARD.",
                "PROTOCOL FOR- hope- PEST EXT- is- EXTERMINATION HAS- paper- BEEN TRI- thin- TRIGGERED.",
                "ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == GLOWER_POWER and suit.isChainsawPhase2:
        taunt = random.choice(
            ["EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
             "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
             "PIERCING EYES HAVE BEEN ESTABLISHED.",
"UPDATING PROCESSES... MUST STAY ON THE CUTTING EDGE!!",
             "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
             "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == GLOWER_POWER and suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",
                "WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
                "ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.",
                "PIERCING EYES- i'm looking- HAVE BEEN- for a- ESTABLI- way out- ESTABLISHED.",
"UPDATING- no- PROCESSES... MUST- can't- MUST STAY ON THE- give in- CUTTING EDGE!!",
                "ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    elif name == QUALITY_CONTROL_LEVEL_3:
        taunt = random.choice(
            ["I've got my eye on you!", "I'll poke you in the eye!", "'Eye' am as evil as they come!'",
             "Wait. I've got something in my eye.", "Could you keep an eye on this for me?",
             "I'm rolling my eye at you.", "I'll put you in the eye of the storm!", "Could you eye-ball this for me?",
             "I'm giving you the evil eye.", "I've got a real eye for evil."])
        track.append(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
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
    name = attack['id']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    track = Sequence(Wait(delay))
    if attack[
        'suitName'] == 'csm':  # It isn't just 'caseman', it really all depends on the shorthand you have for the Case Manager.  If it is not 'caseman', change it to whatever is the actual shorthand for the Case Manager, or the Case Manager will not grunt as intended.
        track.append(Func(suit.setChatAbsolute, random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...']),
                          CFSpeech | CFTimeout))
    elif attack[
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


def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True))


def getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative = 1):
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
        partTracks.append(getPartTrack(particleEffects[i], startDelay, durationDelay, [particleEffects[i], battle, worldRelative]))

    suit.setHpr(battle, origHpr) # After all that, set the Cog back like nothing ever happened.
    return partTracks


def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target'][0]
    toon = target['toon']
    battle = attack['battle']
    suit = attack['suit']
    name = attack['id']
    suitPos = suit.getPos(battle)
    dmg = target['hp']
    animTrack = Sequence()
    animTrack.append(Func(toon.headsUp, battle, suitPos))
    currentBossHealth = -1
    if suit.style.name == 'csm':
        for s in battle.activeSuits:
            if s.dna.name == 'ste' or s.dna.name == 'lit' or s.dna.name == 'scg':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'scg':
        for s in battle.activeSuits:
            if s.dna.name == 'ste' or s.dna.name == 'lit' or s.dna.name == 'csm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'lit':
        for s in battle.activeSuits:
            if s.dna.name == 'ste' or s.dna.name == 'csm' or s.dna.name == 'scg':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'ste':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'gtk':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'frs':
        for s in battle.activeSuits:
            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'fbd':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'cp':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'ffm':
        for s in battle.activeSuits:
            if s.dna.name == 'dsk' or s.dna.name == 'blr' or s.dna.name == 'dvp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'dsk':
        for s in battle.activeSuits:
            if s.dna.name == 'ffm' or s.dna.name == 'blr' or s.dna.name == 'dvp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'dvp':
        for s in battle.activeSuits:
            if s.dna.name == 'dsk' or s.dna.name == 'blr' or s.dna.name == 'ffm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'blr':
        for s in battle.activeSuits:
            if s.dna.name == 'dsk' or s.dna.name == 'ffm' or s.dna.name == 'dvp':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'cry':
        for s in battle.activeSuits:
            if s.dna.name == 'dvk' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'tcm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvk' or s.dna.name == 'cry' or s.dna.name == 'otm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'otm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvk' or s.dna.name == 'tcm' or s.dna.name == 'cry':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    elif suit.style.name == 'dvk':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                currentBossHealth = s.currHP
        if currentBossHealth == -1:
            animTrack.append(Func(suit.makeDesperation))
            animTrack.append(Func(suit.makeDamageUp))
    for s in battle.activeSuits:
        if s.dna.name == 'csm':
            currentBossHealth = s.currHP
    if currentBossHealth == -1:
        animTrack.append(Func(suit.removeInsured))
    x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
    if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
        syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, +0), Func(suit.showHpString, "SYPHONED!"), Func(suit.setHealthForMe, + 0), Func(suit.updateHealthBar, 0))
        insuredSuitTrack = Parallel(Func(suit.showHpTextCheat, +0), Func(suit.showHpString, "INSURED!"), Func(suit.setHealthForMe, 0), Func(suit.updateHealthBar, 0))
    elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP) and suit.isInsured:
        insuredSuitTrack = Parallel(Func(suit.showHpTextCheat, x), Func(suit.showHpString, "INSURED!"),
                                    Func(suit.setHealthForMe, x), Func(suit.updateHealthBar, 0))
    elif suit.currHP + dmg > (suit.maxHP * suit.hardMaxHP) and suit.isSyphon:
        syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, x), Func(suit.showHpString, "SYPHONED!"),
                                   Func(suit.setHealthForMe, x), Func(suit.updateHealthBar, 0))
    else:
        syphonSuitTrack = Parallel(Func(suit.showHpTextCheat, +dmg), Func(suit.showHpString, "SYPHONED!"),
                                   Func(suit.setHealthForMe, + dmg), Func(suit.updateHealthBar, 0))
        insuredSuitTrack = Parallel(Func(suit.showHpTextCheat, 50), Func(suit.showHpString, "INSURED!"),
                                    Func(suit.setHealthForMe, 50), Func(suit.updateHealthBar, 0))
    if dmg > 0 and name == MULLIGAN and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == MULLIGAN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == KICK_UP:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == SHAKEDOWN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == FIRE_COG and suit.isOttomanPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["You've gotta be quicker than that!", "Move it!", "Think fast!", "Eyes on the prize!",
             "Follow the groove!",
             "Step on it!", "Hurry it up!", "Pump up those reflexes!", "Follow the groove!"])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(ActorInterval(suit, 'come-on', playRate=suit.getPlayRate('pace')))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'pace'))
        return animTrack
    elif dmg > 0 and name == FIRE_COG:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == USURY and suit.isChainsawPhase3:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL- increasing- IDENTIFIED. RETALIATION SHALL BE MET WITH- power- EQUAL FORCE.",
             "OUTER LAYERS AT- getting- RISK. TAKING DEFENSIVE- faster- ACTION.",
             "THREATS HAVE- i have- BEGUN TO- been- ADVANCE. BEGIN- hit- INCREASING ATTACK POWER.", ])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.1x DMG MULTIPLIER!"))
        for headPart in suit.animatedHeadParts:
            headInterval = ActorInterval(headPart, 'revvedup', playRate=suit.getPlayRate('revvedup'))
        animTrack.append(Parallel(headInterval, SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and name == USURY:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == OIL_RAIN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_QUAKE and suit.isChainsawPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
             "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
             "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_QUAKE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_DETONATE_2 and suit.isChainsawPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
             "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
             "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_DETONATE_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_DETONATE and suit.isChainsawPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
             "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
             "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_DETONATE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BEGUILE and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and name == BOMB_CAKE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CHAINSAW_CANNED:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == TRIBUTE_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == SLUSHFUND_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CAGE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == NOT_THROW_PIANO:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == DETONATE_2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BEGUILE:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CEASE_AND_DESIST and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.74), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == CEASE_AND_DESIST:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.74), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == INSURANCE_PLAN and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == INSURANCE_PLAN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 2), damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == UNION_BUSTER:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == WHITE_POWDER:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == WIRETAPPED:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BOOKKEEPING:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == WIRE_CUT:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == FREEZING_RAIN:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == HEAVY_RAINFALL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COLLECT_CALL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == CONE_OF_SHAME:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == QUALITY_CONTROL_LEVEL_3:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == QUALITY_CONTROL_LEVEL_1:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == AFTERSHOCK:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == QUALITY_CONTROL_LEVEL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == BOMB:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == DROWNING:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == PAPER_CUT:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == EXPLODING_BILL:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], (dmg / 2), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == SNAP_WET and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.75), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == SNAP_WET:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.75), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COURT_SANCTION and suit.isInsured:
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                   splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == COURT_SANCTION:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.83), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == COURT_RECORD_4 and suit.isInsured:
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.74), damageDelay, damageAnimNames,
                                   splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == COURT_RECORD_4:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.74), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and name == SNAP and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.69), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and name == SNAP:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], int(dmg / 1.69), damageDelay, damageAnimNames,
                                                splicedDamageAnims, showDamageExtraTime))
        return animTrack
    elif dmg > 0 and suit.isSyphon:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(syphonSuitTrack)
        return animTrack
    elif dmg > 0 and suit.isInsured:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        animTrack.append(insuredSuitTrack)
        return animTrack
    elif dmg > 0 and suit.isOttomanPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        taunt = random.choice(
            ["You've gotta be quicker than that!", "Move it!", "Think fast!", "Eyes on the prize!", "Follow the groove!",
             "Step on it!", "Hurry it up!", "Pump up those reflexes!", "Follow the groove!"])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(ActorInterval(suit, 'come-on', playRate=suit.getPlayRate('pace')))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'pace'))
        return animTrack
    elif dmg > 0 and suit.isChainsawPhase2:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.", "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
             "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
        animTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                           ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0 and suit.isChainsawPhase3:
        animTrack.append(
            getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims,
                                   showDamageExtraTime))
        taunt = random.choice(
            ["DAMAGE TO SHELL- increasing- IDENTIFIED. RETALIATION SHALL BE MET WITH- power- EQUAL FORCE.", "OUTER LAYERS AT- getting- RISK. TAKING DEFENSIVE- faster- ACTION.",
             "THREATS HAVE- i have- BEGUN TO- been- ADVANCE. BEGIN- hit- INCREASING ATTACK POWER.",])
        animTrack.append(Func(suit.setChatAbsolute,
                              taunt,
                              CFSpeech | CFTimeout))
        animTrack.append(Func(suit.showHpString, "1.1x DMG MULTIPLIER!"))
        for headPart in suit.animatedHeadParts:
            headInterval =  ActorInterval(headPart, 'revvedup', playRate=suit.getPlayRate('revvedup'))
        animTrack.append(Parallel(headInterval, SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                                  ActorInterval(suit, 'revvedup', playRate=suit.getPlayRate('revvedup'))))
        animTrack.append(Func(suit.setPlayRate, suit.getPlayRate() + 0.1, 'revvedup'))
        animTrack.append(Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))
        animTrack.append(Func(suit.setNeutralAnimation))
        return animTrack
    elif dmg > 0:
        animTrack.append(getToonTakeDamageTrack(attack, toon, target['died'], dmg, damageDelay, damageAnimNames, splicedDamageAnims, showDamageExtraTime))
        return animTrack
    else:
        animTrack.append(getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime))
        indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime), Func(MovieUtil.indicateMissed, toon))
        return Parallel(animTrack, indicatorTrack)


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


def getPropThrowTrack(attack, prop, hitPoints = [], missPoints = [], hitDuration = 0.25, missDuration = 0.25, hitPointNames = 'none', missPointNames = 'none', lookAt = 'none', groundPointOffSet = 0, missScaleDown = None, parent = render):
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
    name = attack['id']
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
    if died:
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
    if died:
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


def doClipOnTie(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tie = globalPropPool.getProp('clip-on-tie')
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1.25
    damageDelay = 2.5
    dodgeDelay = 1.75
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-1, 1, -.25), VBase3(0, 0, 0)]
    tiePropTrack = Sequence(getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25, poseExtraArgs=['clip-on-tie', 0]))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    splatName = 'dust'
    splat = globalPropPool.getProp('dust')
    explode = globalPropPool.getProp('dust')
    explode.setTwoSided(True)


    explode.setBillboardPointWorld(2)
    explodeTrack = Sequence()
    explodeTrack.append(getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
    explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
    if dmg > 0:
        tiePropTrack.append(ActorInterval(tie, 'clip-on-tie', duration=throwDelay, startTime=1.1))
    else:
        tiePropTrack.append(Wait(throwDelay))
    tiePropTrack.append(Func(tie.setHpr, Point3(0, -90, 0)))
    tiePropTrack.append(getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)], hitDuration=0.25, missDuration=0.25, missScaleDown=1.2))
    soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
    tiePropTrack.append(Parallel(explodeTrack, soundTrack))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=throwDelay + .5, node=suit)
    return Parallel(suitTrack, toonTrack, tiePropTrack, throwSound)

def doDisassemble(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Wait(1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.5
    attackDelay = 1.5
    sprayEffect = BattleParticles.createParticleEffect(file='reorgSpray')
    suitTrack = Sequence(Wait(1), ActorInterval(suit, attack['animName']))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    propTrackNew = Parallel()
    laptopPosPoints = [Point3(-2, 1.5, 2.5), VBase3(0, 0, 0)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.75, 1.75, 1.75)
    propTrackNew.append(
        getPropTrack(card, cage, laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                     anim=1, animStartTime=0.5, animDuration=2.5,
                     propName='ttht_m_ene_techbotLaptop'))
    cagePos = [Point3(suitPos.getX() - 3, suitPos.getY() - 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=1),
        Parallel(
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
        Wait(2.0),
        LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage)
    )

    cagePropTracks.append(cagePropTrack)
    partTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    if dmg > 0:
        headParts = toon.getHeadParts()
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
                                       LerpHprInterval(part, 0.4, VBase3(360, 0, 180)),
                                       LerpPosInterval(part, 0.3, Point3(x, y, z + 3.1)),
                                       LerpPosInterval(part, 0.15, Point3(x, y, z + 0.3)), Wait(0.15),
                                       LerpHprInterval(part, 0.6, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)),
                                       LerpHprInterval(part, 0.8, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)),
                                       LerpPosInterval(part, 0.15, Point3(x, y, z + 1)),
                                       LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2),
                                       LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.9)))

        def getChestTrack(part, attackDelay=attackDelay):
            origScale = part.getScale()
            return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1),
                            LerpHprInterval(part, 1.1, part.getHpr()))

        chestTracks = Parallel()
        arms = toon.findAllMatches('**/arms')
        sleeves = toon.findAllMatches('**/sleeves')
        hands = toon.findAllMatches('**/hands')
        for partNum in xrange(0, arms.getNumPaths()):
            chestTracks.append(getChestTrack(arms.getPath(partNum)))
            chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
            chestTracks.append(getChestTrack(hands.getPath(partNum)))

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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01,
                             dodgeAnimNames=['duck'])
    if dmg > 0:
        return Parallel(suitTrack, tauntInterval, cagePropTracks, toonTrack, propTrackNew, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, tauntInterval, cagePropTracks, propTrackNew, toonTrack)

def doWritingDesk(attack):
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
    suitTrack = Sequence(Wait(2.0), Func(suit.setChatAbsolute, "Oh. Hi there.", CFSpeech | CFTimeout),
                         ActorInterval(suit, 'ottoman-writing-start', playRate=suit.getPlayRate('pace')),
                         Func(suit.setChatAbsolute,
                              "Well, go ahead and make yourself comfortable. I will be sitting here filing my paperwork.",
                              CFSpeech | CFTimeout), ActorInterval(suit, 'ottoman-writing-loop', playRate=suit.getPlayRate('pace')),
                         ActorInterval(suit, 'ottoman-writing-loop', playRate=suit.getPlayRate('pace')),
                         ActorInterval(suit, 'ottoman-writing-loop', playRate=suit.getPlayRate('pace')), ActorInterval(suit, 'ottoman-writing-loop', playRate=suit.getPlayRate('pace')),
                         ActorInterval(suit, 'ottoman-writing-stop', playRate=suit.getPlayRate('pace')),
                         Func(suit.setChatAbsolute,
                              "Did you hear something?",
                              CFSpeech | CFTimeout),
                         ActorInterval(suit, 'ottoman-sit-loop', playRate=suit.getPlayRate('pace'))
                         , ActorInterval(suit, 'ottoman-sit-loop', playRate=suit.getPlayRate('pace')), Parallel(explosionTrack, soundTrack, ActorInterval(suit, 'slip-forward', startTime=2.43),
                         Func(suit.setChatAbsolute,
                              "That's unfortunate, good thing I was able to finish the paperwork I was writing up.",
                              CFSpeech | CFTimeout)), Func(suit.setNeutralAnimation))
    if attack['id'] == MP_HOT_AIR:
        suitTrack.append(Wait(2.0))
        suitTrack.append(doGroupHealing(attack))
    else:
        suitTrack.append(Wait(2.0))
        suitTrack.append(doManagerHeal(attack))
    return Parallel(suitTrack, cagePropTracks)

def doManagerHeal(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    taunt = random.choice(
        ["You did great work today, here's a bonus.",
         "Here's a little something for your trouble."])

    suitTracks = Parallel()
    tauntInterval = Sequence(Func(theSuit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    knifeTracks = Parallel()
    for s in battle.activeSuits:
        if s.dna.name == 'cry':
            print('Found manager... using it...')
            suit = s
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            suitTrack.append(Func(suit.showHpTextCheat, 250))
            suitTrack.append(Func(suit.showHpString, "MANAGER BONUS!"))
            suitTrack.append(Func(suit.setHealthForMe, 250))
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                  CFSpeech | CFTimeout))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
            suitTracks.append(Wait(6.5))
            posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
            hitPoint = suit.getPos(battle)
            hitPoint.setZ(suit.height + 2)
            knife = globalPropPool.getProp('bonus-check')
            knifeTrack = Sequence(
                getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(8.5, 8.5, 8.5),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(-180, 90, 0))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
        elif s.dna.name == 'tcm':
            print('Found manager... using it...')
            suit = s
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            suitTrack.append(Func(suit.showHpTextCheat, 250))
            suitTrack.append(Func(suit.showHpString, "MANAGER BONUS!"))
            suitTrack.append(Func(suit.setHealthForMe, 250))
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                  CFSpeech | CFTimeout))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
            suitTracks.append(Wait(6.5))
            posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
            hitPoint = suit.getPos(battle)
            hitPoint.setZ(suit.height + 2)
            knife = globalPropPool.getProp('bonus-check')
            knifeTrack = Sequence(
                getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(8.5, 8.5, 8.5),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(-180, 90, 0))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
        elif s.dna.name == 'dvk':
            print('Found manager... using it...')
            suit = s
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            suitTrack.append(Func(suit.showHpTextCheat, 250))
            suitTrack.append(Func(suit.showHpString, "MANAGER BONUS!"))
            suitTrack.append(Func(suit.setHealthForMe, 250))
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                       CFSpeech | CFTimeout))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
            suitTracks.append(Wait(6.5))
            posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
            hitPoint = suit.getPos(battle)
            hitPoint.setZ(suit.height + 2)
            knife = globalPropPool.getProp('bonus-check')
            knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(8.5, 8.5, 8.5),
                               scaleUpTime=0.1),
            Wait(2.3),
            Parallel(
                getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                LerpHprInterval(knife, 0.8, VBase3(-180, 90, 0))),
            Parallel(LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() - 10)),
                     Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
    suitTrack = Sequence(Wait(6.0), Func(theSuit.setNeutralAnimation))
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=theSuit)
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    return Parallel(suitTrack, suitTracks, healSound, soundTrack2, knifeTracks)

def doGroupHealing(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    taunt = random.choice(
        ["We all need a little healing sometimes.",
         "All employees are receiving a raise, effective immediately."])

    suitTracks = Parallel()
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpText, 0))
        elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpTextCheat, x))
            suitTrack.append(Func(suit.showHpString, "WAGE RAISE!"))
            suitTrack.append(Func(suit.setHealthForMe, x))
        else:
            suitTrack.append(Func(suit.showHpTextCheat, 125))
            suitTrack.append(Func(suit.showHpString, "WAGE RAISE!"))
            suitTrack.append(Func(suit.setHealthForMe, 125))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'otm':
            suitTrack.append(Parallel(Sequence(Wait(4.0)),
                                      Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                           CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
        suitTracks.append(Wait(6.5))
    posPoints = [Point3(0.25, -1.5, .85), VBase3(0, 220, -10)]
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
    suitTrack = Sequence(Wait(6.0), Func(suit.setNeutralAnimation))
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, soundTrack2, knifeTracks)

def doMeaningfulConversation(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = attack['target']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence(Func(theSuit.setChatAbsolute, "I have a tendency to mumble and ramble to myself, Hope that isn't a bother.", CFSpeech | CFTimeout),
                             ActorInterval(theSuit, 'speak', playRate=theSuit.getPlayRate('pace') + 1),
                             Func(theSuit.setChatAbsolute,
                                  "I got complimented earlier today.",
                                  CFSpeech | CFTimeout), ActorInterval(theSuit, 'speak', playRate=theSuit.getPlayRate('pace') + 1),  Func(theSuit.setChatAbsolute,
                                  "Someone said I have a nice tie.",
                                  CFSpeech | CFTimeout),
                             ActorInterval(theSuit, 'speak', playRate=theSuit.getPlayRate('pace') + 1),  Func(theSuit.setChatAbsolute,
                                                                 "First time in a long while that someone has complimented me.",
                                  CFSpeech | CFTimeout),
                             ActorInterval(theSuit, 'speak', playRate=theSuit.getPlayRate('pace') + 1),  Func(theSuit.setChatAbsolute,
                                                                 "Usually people just step on me.",
                                  CFSpeech | CFTimeout),
                             ActorInterval(theSuit, 'speak', playRate=theSuit.getPlayRate('pace') + 1),  Func(theSuit.setChatAbsolute,
                                                                 "Literally.",
                                  CFSpeech | CFTimeout),
                             ActorInterval(theSuit, 'speak', playRate=theSuit.getPlayRate('pace') + 1),
                             Func(theSuit.setChatAbsolute,"I'm sorry, am I boring you?", CFSpeech | CFTimeout), ActorInterval(theSuit, 'speak', playRate=2),
                             Func(theSuit.setNeutralAnimation))
        if not suit.dna.name == 'otm':
            suitTrack.append(Func(suit.setChatAbsolute, "Yes.", CFSpeech | CFTimeout))
            suitTrack.append(Func(suit.showHpTextCheat, - int(200 * len(battle.activeToons))))
            suitTrack.append(Func(suit.showHpString, "BORED!"))
            suitTrack.append(Func(suit.setHealthForMe, - (200 * len(battle.activeToons))))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Parallel(ActorInterval(suit, 'sound-react-nt')))
        suitTracks.append(suitTrack)
        revives = suit.getMaxSkeleRevives() + 1
        suitTrack.append(Func(suit.setNeutralAnimation))
        if suit.isVirtual and revives > 2:
            suitTrack.append(Func(suit.checkCogHPLaser, battle))
        elif suit.isSkeleton and revives > 2:
            suitTrack.append(Func(suit.checkCogHPLaserRevive, battle))
        elif not suit.isSkeleton and revives > 1:
            suitTrack.append(Func(suit.checkCogHPRevive, battle))
        elif suit.isVirtual:
            suitTrack.append(Func(suit.checkCogHPLaser, battle))
        elif not suit.isVirtual:
            suitTrack.append(Func(suit.checkCogHPBomb, battle))
        suitTrack.append(Wait(5.0))
    toonTracks = getToonTracks(attack, suitTrack.getDuration(), ['slip-backward'], suitTrack.getDuration(), ['shrug'])
    return Parallel(suitTracks, toonTracks)


def doClockChange(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(getSuitAnimTrack(attack))
    toonTracks = getToonTracks(attack, suitTrack.getDuration() - 1.5, ['slip-backward'], suitTrack.getDuration() - 1.5, ['shrug'])
    soundTrack = getSoundTrack('SA_clock_trigger.ogg', node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack)

def doUsury(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(getSuitTrack(attack), ActorInterval(suit, 'finger-wag', startFrame=0, endFrame=20, playRate=.25))
    return suitTrack

def doTribute2(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(getSuitTrack(attack), ActorInterval(suit, 'hypnotized', startFrame=0, endFrame=16), ActorInterval(suit, 'hypnotized', startFrame=16, endFrame=0))
    return suitTrack

def doSlushFund2(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(getSuitTrack(attack))
    return suitTrack

def doShakedown(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(getSuitTrack(attack))
    return suitTrack

def doStandUpGuy(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(getSuitTrack(attack))
    soundTrack = getSoundTrack('SA_defense.ogg', node=suit)
    return Parallel(suitTrack, soundTrack)

def doKickUp(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(getSuitTrack(attack))
    return suitTrack

def doSitdown(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTrack = Sequence(getSuitTrack(attack))
    soundTrack = getSoundTrack('ttcc_int_psetter_bell.ogg', node=suit)
    return Parallel(suitTrack, soundTrack)


def doPoundKey(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('PoundKey')
    BattleParticles.setEffectTexture(particleEffect, 'poundsign', color=Vec4(0, 0, 0, 1))
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTrack = getPartTrack(particleEffect, 1.1, 2.0, [particleEffect, suit, 0])
    phonePosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)), Wait(2.14), Func(receiver.wrtReparentTo, phone), Wait(0.62), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTrack = getToonTrack(attack, 2.0, ['cringe'], 1.3, ['sidestep'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=.5, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Any Level 8 Gags Toons use can and will be held against them in a court of law.",
                                     CFSpeech | CFTimeout))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control has classified that all Level 6 Gags are now classified as defective.",
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'ste':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    elif attack['suit'].dna.name == 'frs':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack2))
    return Parallel(suitTrack, toonTrack, propTrack, partTrack, soundTrack)

def doBayouBash(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(MovieUtil.createSuitSnapInterval(suit), Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.25))
    #cameraTrack = Func(camera.setPosHpr, 0, -10, 10, 0, -30, 0)
    suitSpeechTrack = Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitBashPhrases), CFSpeech | CFTimeout)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    if name == WHITE_POWDER:
        suitTrack.append(doWhitePowder(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack)

def doBayouBashReal(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(MovieUtil.createSuitSnapInterval(suit),  Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.25))
    #cameraTrack = Func(camera.setPosHpr, 0, -10, 10, 0, -30, 0)
    suitSpeechTrack = Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitBashPhrases), CFSpeech | CFTimeout)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, soundTrack, suitSpeechTrack)

def doBayouBashSnap(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('The Litigator absolutely swamps you with cogs!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Bayou Bash!', 3.5)
    suitTrack = Sequence(MovieUtil.createSuitSnapInterval(suit), Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.25))
    #cameraTrack = Func(camera.setPosHpr, 0, -10, 10, 0, -30, 0)
    suitSpeechTrack = Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitBashPhrases), CFSpeech | CFTimeout)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, soundTrack, suitSpeechTrack)

def doBayouBash2(attack):
    name = attack['id']
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'snap'), Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.25))
    #cameraTrack = Func(camera.setPosHpr, 0, -10, 10, 0, -30, 0)
    suitSpeechTrack = Func(suit.setChatAbsolute, random.choice(["What'ya waitin' for, babe? Hop on fftage! let'ff get hoppin' and boppin', jumpin' and jinglin', ffingin' and ffwingin'!", "Ohoho-no-no, takeff a party to partiffipate and play, and I ffay play!!", "Get ready for the ffho-ho-how of a lifetime, Bobby Dazzler!"]), CFSpeech | CFTimeout)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    if name == HEAD_ROLLER:
        suitTrack.append(doHeadRollerHighRoller(attack, 2))
    elif name == HEAD_ROLLER_2:
        suitTrack.append(doHeadRollerHighRoller(attack, 3))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack)

def doHeatWaveCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'soak', playRate=1.25),  Func(suit.setNeutralAnimation), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "The temperature is starting to rise... The heat index is now approaching %s degrees." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    suitTrack.append(doHeatWave(attack))
    return Parallel(suitTrack, suitSpeechTrack)

def doCalculateStocks(attack):
    suit = attack['suit']
    calculator = globalPropPool.getProp('calculator')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect, 'audit-one', color=Vec4(0, 0, 0, 1))
    particleEffect2 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect2, 'audit-two', color=Vec4(0, 0, 0, 1))
    particleEffect3 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect3, 'audit-three', color=Vec4(0, 0, 0, 1))
    particleEffect4 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect4, 'audit-four', color=Vec4(0, 0, 0, 1))
    particleEffect5 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect5, 'audit-mult', color=Vec4(0, 0, 0, 1))
    tauntInterval = Func(suit.setChatAbsolute,
                                     "The stocks are rising, C.O.G.S. share price has been raised to %s..." % int(attack['target'][0]['hp'] / 3),
                                     CFSpeech | CFTimeout)
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'calculator', playRate=1.25))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 7 and 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(doStockCalculations(attack))
    partTrack = getPartTrack(particleEffect, 1.5, 1.5, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 1.6, 1.5, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 1.7, 1.6, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 1.8, 1.7, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 1.9, 1.8, [particleEffect5, suit, 0])
    suitName = attack['suitName']
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='calculator',
                                 animStartTime=0,
                                 animDuration=2.5)
    soundTrack = getSoundTrack('SA_audit.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, calcPropTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)

def doStockCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimation), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "What's this? These rates are skyrocketing! My mistake, the share price has TRIPLED and is now %s!" % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 0.25
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator', animStartTime=0,
                                 animDuration=2.9)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doStockCosts(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doCourtCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimation), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of litigation fees... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 0.25
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator', animStartTime=0,
                                 animDuration=2.9)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doCourtCosts(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doCollectCallCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimation), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of collect call fees... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 0.25
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator',
                                 animStartTime=0,
                                 animDuration=2.9)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doCollectCallFees(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doInterestCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), Func(suit.setNeutralAnimation), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of interest fees... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 0.25
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator',
                                 animStartTime=0,
                                 animDuration=2.9)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doSynergy2(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doUnionCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'), Func(suit.setNeutralAnimation), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of union dues... Price index raised to %s." % attack['target'][0]['hp'], CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.35, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 0.25
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getRightHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='court-costs-calculator',
                                 animStartTime=0,
                                 animDuration=2.9)
    soundTrack = getSoundTrack('SA_calculating_costs.ogg', node=suit)
    suitTrack.append(doUnionDues(attack))
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)


def doShred(attack):
    suit = attack['suit']
    battle = attack['battle']
    paper = globalPropPool.getProp('shredder-paper')
    shredder = globalPropPool.getProp('shredder')
    particleEffect = BattleParticles.createParticleEffect('Shred')
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, 3.5, 1.9, [particleEffect, suit, 0])
    paperPosPoints = [Point3(0.59, -0.31, 0.81), VBase3(79.224, 32.576, -179.449)]
    paperPropTrack = getPropTrack(paper, suit.getRightHand(), paperPosPoints, 2.4, 1e-05, scaleUpTime=0.2, anim=1, propName='shredder-paper', animDuration=1.5, animStartTime=2.8)
    shredderPosPoints = [Point3(0, -0.12, -0.34), VBase3(-90.0, -53.77, -0.0)]
    shredderPropTrack = getPropTrack(shredder, suit.getLeftHand(), shredderPosPoints, 1, 3, scaleUpPoint=Point3(4.81, 4.81, 4.81))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.1, ['conked'], suitTrack.getDuration() - 3.1, ['sidestep'])
    soundTrack = getSoundTrack('SA_shred.ogg', delay=3.4, node=suit)
    return Parallel(suitTrack, paperPropTrack, shredderPropTrack, partTrack, toonTrack, soundTrack)

def doPaperCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    paper = globalPropPool.getProp('shredder-paper')
    #shredder = globalPropPool.getProp('shredder')
    particleEffect = BattleParticles.createParticleEffect('Shred2')
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'sanction', endTime=1), Wait(2.0),
                         ActorInterval(suit, 'sanction', startTime=1), suitReset, Func(suit.setNeutralAnimation))
    partTrack = getPartTrack(particleEffect, 0.5, 3.0, [particleEffect, suit, 0])
    paperPosPoints = [Point3(0.59, -0.31, 0.81), VBase3(79.224, 32.576, -179.449)]
    paperPropTrack = getPropTrack(paper, suit.getRightHand(), paperPosPoints, .1, 1e-05, scaleUpTime=0.1, anim=1, propName='shredder-paper', animDuration=2.0, animStartTime=0.5)
    #shredderPosPoints = [Point3(0, -0.12, -0.34), VBase3(-90.0, -53.77, -0.0)]
    #shredderPropTrack = getPropTrack(shredder, suit.getLeftHand(), shredderPosPoints, 1, 3, scaleUpPoint=Point3(4.81, 4.81, 4.81))
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 2, ['cringe'])
    soundTrack = getSoundTrack('SA_shred.ogg', delay=0.5, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Toon-Up and Zap Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    notifyTrack = Sequence(Wait(2), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "GAG DEBUFF!"))
    return Parallel(suitTrack, paperPropTrack, partTrack, tauntInterval, notifyTrack, toonTrack, soundTrack)

def doPaperCut2(attack):
    suit = attack['suit']
    battle = attack['battle']
    paper = globalPropPool.getProp('shredder-paper')
    #shredder = globalPropPool.getProp('shredder')
    particleEffect = BattleParticles.createParticleEffect('Shred2')
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'sanction', endTime=1), Wait(2.0), ActorInterval(suit, 'sanction', startTime=1), suitReset, Func(suit.setNeutralAnimation))
    partTrack = getPartTrack(particleEffect, 0.5, 3.0, [particleEffect, suit, 0])
    paperPosPoints = [Point3(0.59, -0.31, 0.81), VBase3(79.224, 32.576, -179.449)]
    paperPropTrack = getPropTrack(paper, suit.getRightHand(), paperPosPoints, .1, 1e-05, scaleUpTime=0.1, anim=1, propName='shredder-paper', animDuration=2.0, animStartTime=0.5)
    #shredderPosPoints = [Point3(0, -0.12, -0.34), VBase3(-90.0, -53.77, -0.0)]
    #shredderPropTrack = getPropTrack(shredder, suit.getLeftHand(), shredderPosPoints, 1, 3, scaleUpPoint=Point3(4.81, 4.81, 4.81))
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 2, ['cringe'])
    soundTrack = getSoundTrack('SA_shred.ogg', delay=0.5, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Throw and Sound Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    notifyTrack = Sequence(Wait(2), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "GAG DEBUFF!"))
    return Parallel(suitTrack, paperPropTrack, partTrack, tauntInterval, toonTrack, notifyTrack, soundTrack)

def doSongAndDance(attack):
    suit = attack['suit']
    battle = attack['battle']
    cane = globalPropPool.getProp('cane')
    cogHead = suit.find('**/to_head')
    #encounter = {'isSkelecog': suit.getSkelecog()}
    #if encounter['isSkelecog']:
        #pass
   # else:
        #for part in suit.getHeadParts():
           # part.reparentTo(cogHead)
    hat = globalPropPool.getProp('hat')
    hat.setR(326.98)
    suitTrack = getSuitAnimTrack(attack)
    caneposPoints = [Point3(-0.13, 0.18, -0.08)]
    hatposPoints = [Point3(0, -0.10, 1.66)]
    propTrack = Sequence(getPropAppearTrack(cane, suit.getRightHand(), caneposPoints, 0.4, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(getPropAppearTrack(hat, cogHead, hatposPoints, 0.4, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(Wait(4.6))
    propTrack.append(LerpScaleInterval(hat, 0.1, MovieUtil.PNT3_NEARZERO))
    propTrack.append(LerpScaleInterval(cane, 0.1, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, hat))
    propTrack.append(Func(MovieUtil.removeProp, cane))
    damageAnims = ['cringe']
    dodgeAnims = ['applause']
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 6 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'blr':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    toonTracks = getToonTracks(attack, 4.1, ['cringe'], 4.223, ['applause'])
    soundTrack = getSoundTrack('AA_heal_happydance.ogg', delay=.01, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack)

def doSongAndDanceRadioInfrequency(attack):
    suit = attack['suit']
    battle = attack['battle']
    cane = globalPropPool.getProp('cane')
    cogHead = suit.find('**/to_head')
    #encounter = {'isSkelecog': suit.getSkelecog()}
    #if encounter['isSkelecog']:
        #pass
   # else:
        #for part in suit.getHeadParts():
           # part.reparentTo(cogHead)
    hat = globalPropPool.getProp('hat')
    hat.setR(326.98)
    taunt = getAttackTaunt('SongAndDance', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'song-and-dance'), Func(suit.setNeutralAnimation))
    caneposPoints = [Point3(-0.13, 0.18, -0.08)]
    hatposPoints = [Point3(0, -0.10, 1.66)]
    propTrack = Sequence(getPropAppearTrack(cane, suit.getRightHand(), caneposPoints, 0.4, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(getPropAppearTrack(hat, cogHead, hatposPoints, 0.4, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(Wait(4.6))
    propTrack.append(LerpScaleInterval(hat, 0.1, MovieUtil.PNT3_NEARZERO))
    propTrack.append(LerpScaleInterval(cane, 0.1, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, hat))
    propTrack.append(Func(MovieUtil.removeProp, cane))
    damageAnims = ['cringe']
    dodgeAnims = ['applause']
    suitTrack.append(Wait(2.0))
    suitTrack.append(doRadioInfrequency(attack))
    toonTracks = getToonTracks(attack, 4.1, ['cringe'], 4.223, ['applause'])
    soundTrack = getSoundTrack('AA_heal_happydance.ogg', delay=.01, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack)

def doCaress(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'kneel-into'), ActorInterval(attack['suit'], 'kneel-caress-into'), ActorInterval(attack['suit'], 'caress'), ActorInterval(attack['suit'], 'kneel-caress-out'), ActorInterval(attack['suit'], 'kneel-out'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    toonTracks = getToonTrack(attack, 4.1, ['cringe'], 4.223, ['applause'])
    talkTrack = Sequence(Func(suit.setChatAbsolute, "These perfect prestissimo plays have been played and presented by the powerful proprietor of prowess!", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "You can always find me baby, beyond the sea.", CFSpeech | CFTimeout), Wait(2.5), Func(suit.setChatAbsolute, "But like any good song, it's time for this one man big band to fade out!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute, "Skibidiba-ta-ta!", CFSpeech | CFTimeout))

    return Parallel(suitTrack, toonTracks, talkTrack)


def doFillWithLead(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    pencil = globalPropPool.getProp('pencil')
    sharpener = globalPropPool.getProp('sharpener')
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect(file='fillWithLeadSpray')
    headSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    torsoSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    legsSmotherEffect = BattleParticles.createParticleEffect(file='fillWithLeadSmother')
    BattleParticles.setEffectTexture(sprayEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(headSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(torsoSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(legsSmotherEffect, 'roll-o-dex', color=Vec4(0, 0, 0, 1))
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 2.5, 1.9, [sprayEffect, suit, 0])
    pencilPosPoints = [Point3(-0.29, -0.33, -0.13), VBase3(160.565, -11.653, -169.244)]
    pencilPropTrack = getPropTrack(pencil, suit.getRightHand(), pencilPosPoints, 0.7, 3.2, scaleUpTime=0.2)
    sharpenerPosPoints = [Point3(0.0, 0.0, -0.03), MovieUtil.PNT3_ZERO]
    sharpenerPropTrack = getPropTrack(sharpener, suit.getLeftHand(), sharpenerPosPoints, 1.3, 2.3, scaleUpPoint=MovieUtil.PNT3_ONE)
    damageAnims = []
    damageAnims.append(['conked',
     suitTrack.getDuration() - 1.5,
     1e-05,
     1.4])
    damageAnims.append(['conked',
     1e-05,
     0.7,
     0.7])
    damageAnims.append(['conked',
     1e-05,
     0.7,
     0.7])
    damageAnims.append(['conked', 1e-05, 1.4])
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=suitTrack.getDuration() - 3.1, dodgeAnimNames=['sidestep'], showDamageExtraTime=4.5, showMissedExtraTime=1.6)
    animal = toon.style.getAnimal()
    bodyScale = ToontownGlobals.toonBodyScales[animal]
    headEffectHeight = __toonFacePoint(toon).getZ()
    legsHeight = ToontownGlobals.legHeightDict[toon.style.legs] * bodyScale
    torsoEffectHeight = ToontownGlobals.torsoHeightDict[toon.style.torso] * bodyScale / 2 + legsHeight
    legsEffectHeight = legsHeight / 2
    effectX = headSmotherEffect.getX()
    effectY = headSmotherEffect.getY()
    headSmotherEffect.setPos(effectX, effectY - 1.5, headEffectHeight)
    torsoSmotherEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
    legsSmotherEffect.setPos(effectX, effectY - 0.6, legsEffectHeight)
    partDelay = 3.5
    partIvalDelay = 0.7
    partDuration = 1.0
    headTrack = getPartTrack(headSmotherEffect, partDelay, partDuration, [headSmotherEffect, toon, 0])
    torsoTrack = getPartTrack(torsoSmotherEffect, partDelay + partIvalDelay, partDuration, [torsoSmotherEffect, toon, 0])
    legsTrack = getPartTrack(legsSmotherEffect, partDelay + partIvalDelay * 2, partDuration, [legsSmotherEffect, toon, 0])

    def colorParts(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        return track

    def resetParts(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    if dmg > 0:
        colorTrack = Sequence()
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack.append(Wait(partDelay + 0.2))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(colorParts(headParts))
        colorTrack.append(Wait(partIvalDelay))
        colorTrack.append(colorParts(torsoParts))
        colorTrack.append(Wait(partIvalDelay))
        colorTrack.append(colorParts(legsParts))
        colorTrack.append(Wait(2.5))
        colorTrack.append(resetParts(headParts))
        colorTrack.append(resetParts(torsoParts))
        colorTrack.append(resetParts(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        return Parallel(suitTrack, pencilPropTrack, sharpenerPropTrack, sprayTrack, headTrack, torsoTrack, legsTrack, colorTrack, toonTrack)
    else:
        return Parallel(suitTrack, pencilPropTrack, sharpenerPropTrack, sprayTrack, toonTrack)

def doBeguile(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['glower',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('glower', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['glower', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    toonFace = __toonFacePoint(toon, parent=battle)
    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['cringe', 0.01, 0.3]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('ttr_s_ene_bat_beguile.ogg', delay=1.3, node=suit)
    soundMissTrack = getSoundTrack('ttr_s_ene_bat_beguileMiss.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack)

def doCloseTheLoop(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    phonePosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(0.23, 0.17, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverAdjustScale = MovieUtil.PNT3_ONE
    pickupDelay = 0.74
    dialDuration = 3.07
    finalPhoneDelay = 0.69
    scaleUpPoint = MovieUtil.PNT3_ONE
    propTrack = Sequence(Wait(0.3), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, scaleUpPoint, MovieUtil.PNT3_NEARZERO), Wait(pickupDelay), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpScaleInterval(receiver, 0.01, receiverAdjustScale), LerpPosHprInterval(receiver, 0.0001, Point3(-0.53, 0.21, -0.54), VBase3(-99.49, -35.27, 1.84)), Wait(dialDuration), Func(receiver.wrtReparentTo, phone), Wait(finalPhoneDelay), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTrack = getToonTrack(attack, 5.5, ['slip-backward'], 4.7, ['jump'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doHostileTakeover(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='hostileTakeover')
    rainEffect2 = BattleParticles.createParticleEffect(file='hostileTakeover')
    rainEffect3 = BattleParticles.createParticleEffect(file='hostileTakeover')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 1.2
    damageDelay = 4.5
    dodgeDelay = 3.3
    suitTrack = getSuitTrack(attack, delay=0.9)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Throw and Squirt gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dsk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    cloudPropTrack.append(Wait(1.1))
    cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=2.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 1e-06, 1.6]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=2.6, node=suit)
    #soundTrack = getSoundTrack('ttr_s_ene_bat_hostileTakeover.ogg', delay=2.6, node=suit)
    return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)

def doHostileTakeoverUnionBust(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='hostileTakeover')
    rainEffect2 = BattleParticles.createParticleEffect(file='hostileTakeover')
    rainEffect3 = BattleParticles.createParticleEffect(file='hostileTakeover')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 1.2
    damageDelay = 4.5
    dodgeDelay = 3.3
    suitTrack = getSuitTrack(attack, delay=0.9)
    suitTrack.append(Wait(2.0))
    suitTrack.append(doUnionBust(attack, 4))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    cloudPropTrack.append(Wait(1.1))
    cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=2.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 1e-06, 1.6]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=2.6, node=suit)
    #soundTrack = getSoundTrack('ttr_s_ene_bat_hostileTakeover.ogg', delay=2.6, node=suit)
    return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)

def doNickelAndDime(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect('NickelAndDime')
    waterfallEffect = BattleParticles.createParticleEffect(file='nickelDimeWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    soundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('ttr_s_ene_bat_nickelAndDime.ogg'), node=suit))
    soundMissTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('ttr_s_ene_bat_nickelAndDimeMiss.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        return Parallel(suitTrack, partTrack, waterfallTrack, soundTrack, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, soundMissTrack, toonTracks)

def doQuash(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(1.0, 0.2, 0.2, 0.9)
    edgeColor = Vec4(0.9, 0.9, 0.9, 0.4)
    powerBar1 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar2 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-90, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(90, 0, 0)
    powerBar1.setScale(5)
    powerBar2.setScale(5)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitTrack = getSuitAnimTrack(attack)

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(0.7), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 0.6, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.5, ['slip-forward'], 0.86, ['jump'])
    soundTrack = getSoundTrack('ttr_s_ene_bat_quash.ogg', delay=0.2, node=suit)
    return Parallel(suitTrack, partTrack1, partTrack2, soundTrack, waterfallTrack, toonTracks)


def doFountainPen(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    pen = globalPropPool.getProp('pen')

    def getPenTip(pen = pen):
        tip = pen.find('**/joint_toSpray')
        return tip.getPos(render)

    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    missPoint = lambda prop = pen, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
    hitSprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, hitPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
    missSprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, missPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
    suitTrack = getSuitTrack(attack)
    propTrack = Sequence(Wait(0.01), Func(__showProp, pen, suit.getRightHand(), MovieUtil.PNT3_ZERO), LerpScaleInterval(pen, 0.5, Point3(1.5, 1.5, 1.5)), Wait(1.05))
    if dmg > 0:
        propTrack.append(hitSprayTrack)
    else:
        propTrack.append(missSprayTrack)
    propTrack += [LerpScaleInterval(pen, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, pen)]
    splashTrack = Sequence()
    if dmg > 0:

        def prepSplash(splash, targetPoint):
            splash.reparentTo(render)
            splash.setPos(targetPoint)
            scale = splash.getScale()
            splash.setBillboardPointWorld()
            splash.setScale(scale)

        splash = globalPropPool.getProp('splash-from-splat')
        splash.setColor(0, 0, 0, 1)
        splash.setScale(0.15)
        splashTrack = Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(1.65), Func(prepSplash, splash, __toonFacePoint(toon)), ActorInterval(splash, 'splash-from-splat'), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash))
        headParts = toon.getHeadParts()
        splashTrack.append(Func(battle.movie.needRestoreColor))
        for partNum in xrange(0, headParts.getNumPaths()):
            nextPart = headParts.getPath(partNum)
            splashTrack.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        splashTrack.append(Func(MovieUtil.removeProp, splash))
        splashTrack.append(Wait(2.6))
        for partNum in xrange(0, headParts.getNumPaths()):
            nextPart = headParts.getPath(partNum)
            splashTrack.append(Func(nextPart.clearColorScale))

        splashTrack.append(Func(battle.movie.clearRestoreColor))
    penSpill = BattleParticles.createParticleEffect(file='penSpill')
    penSpill.setPos(getPenTip())
    penSpillTrack = getPartTrack(penSpill, 1.4, 0.7, [penSpill, pen, 0])
    toonTrack = getToonTrack(attack, 1.81, ['conked'], dodgeDelay=0.11, splicedDodgeAnims=[['duck', 0.01, 0.6]], showMissedExtraTime=1.66)
    soundTrack = getSoundTrack('SA_fountain_pen.ogg', delay=1.6, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Drop Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'csm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, penSpillTrack, splashTrack)

def doFountainPenBindings(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    pen = globalPropPool.getProp('pen')

    def getPenTip(pen = pen):
        tip = pen.find('**/joint_toSpray')
        return tip.getPos(render)

    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    missPoint = lambda prop = pen, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
    hitSprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, hitPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
    missSprayTrack = MovieUtil.getSprayTrack(battle, VBase4(0, 0, 0, 1), getPenTip, missPoint, 0.2, 0.2, 0.2, horizScale=0.1, vertScale=0.1)
    propTrack = Sequence(Wait(0.01), Func(__showProp, pen, suit.getRightHand(), MovieUtil.PNT3_ZERO), LerpScaleInterval(pen, 0.5, Point3(1.5, 1.5, 1.5)), Wait(1.05))
    if dmg > 0:
        propTrack.append(hitSprayTrack)
    else:
        propTrack.append(missSprayTrack)
    propTrack += [LerpScaleInterval(pen, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, pen)]
    splashTrack = Sequence()
    if dmg > 0:

        def prepSplash(splash, targetPoint):
            splash.reparentTo(render)
            splash.setPos(targetPoint)
            scale = splash.getScale()
            splash.setBillboardPointWorld()
            splash.setScale(scale)

        splash = globalPropPool.getProp('splash-from-splat')
        splash.setColor(0, 0, 0, 1)
        splash.setScale(0.15)
        splashTrack = Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(1.65), Func(prepSplash, splash, __toonFacePoint(toon)), ActorInterval(splash, 'splash-from-splat'), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash))
        headParts = toon.getHeadParts()
        splashTrack.append(Func(battle.movie.needRestoreColor))
        for partNum in xrange(0, headParts.getNumPaths()):
            nextPart = headParts.getPath(partNum)
            splashTrack.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 1)))

        splashTrack.append(Func(MovieUtil.removeProp, splash))
        splashTrack.append(Wait(2.6))
        for partNum in xrange(0, headParts.getNumPaths()):
            nextPart = headParts.getPath(partNum)
            splashTrack.append(Func(nextPart.clearColorScale))

        splashTrack.append(Func(battle.movie.clearRestoreColor))
    penSpill = BattleParticles.createParticleEffect(file='penSpill')
    penSpill.setPos(getPenTip())
    penSpillTrack = getPartTrack(penSpill, 1.4, 0.7, [penSpill, pen, 0])
    toonTrack = getToonTrack(attack, 1.81, ['conked'], dodgeDelay=0.11, splicedDodgeAnims=[['duck', 0.01, 0.6]], showMissedExtraTime=1.66)
    soundTrack = getSoundTrack('SA_fountain_pen.ogg', delay=1.6, node=suit)
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'pen-squirt', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doLegalBindingsSanction(attack))
    return Parallel(suitTrack, toonTrack, propTrack, tauntInterval, soundTrack, penSpillTrack, splashTrack)


def doBookKeeping(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    toon = attack['target'][0]['toon']
    if attack['suitName'] == 'csm':
        taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    elif attack['suitName'] == 'fbd':
        taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    else:
        taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, attack['animName'], duration=3.0), ActorInterval(suit, 'sanction'), suitReset, Func(suit.setNeutralAnimation))

    soundTrack1 = Sequence(SoundInterval(globalBattleSoundCache.getSound('suit_promotion_sfx.ogg'), node=suit))
    soundTrack2 = Sequence(Wait(3.4), SoundInterval(globalBattleSoundCache.getSound('SA_haymaker.ogg'), node=suit))
    soundTrack = Parallel(soundTrack1, soundTrack2)
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 3.4, ['conked'])
    notifyTrack = Sequence(Wait(3.4), Func(toon.showHpTextCheat, - int(dmg / 2)), Func(toon.showHpString, "SILENCED!"))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Lure and Throw Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    return Parallel(suitTrack, soundTrack, toonTrack, notifyTrack)

def doRadioInfrequency(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = random.choice(
        ["There's only static between us.", "Sounds like your broadcast is ending; all I'm hearing is dead air.",
         "Apologies, but I am changing the station.",
         "It appears our show's runtime has been cut short! I suppose we can move on to the weather."])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'glower', duration=1.5), Wait(4.0),
                         ActorInterval(suit, 'glower', startTime=1.5), Func(suit.setNeutralAnimation))


    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 6 and 7 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'blr':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    soundTrack = getSoundTrack('mus_dialup_0.ogg', delay=1.5)
    return Parallel(suitTrack, soundTrack)

def doRadioInfrequencySquirt(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = random.choice(
        ["There's only static between us.", "Sounds like your broadcast is ending; all I'm hearing is dead air.", "Apologies, but I am changing the station.",
         "It appears our show's runtime has been cut short! I suppose we can move on to the weather."])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'glower', duration=1.5), Wait(4.0), ActorInterval(suit,  'glower', startTime=1.5), Func(suit.setNeutralAnimation))
    ceaseTrack2 = ActorInterval(suit, 'cease')
    ceaseSoundTrack2 = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 and 6 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Squirt gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    makeShielding = Func(suit.makeShielding)
    if attack['suit'].dna.name == 'blr':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack2, ceaseSoundTrack2, ceaseSpeechTrack2))
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
        suitTrack.append(Wait(1.0))
        suitTrack.append(doBreachOfContract(attack))
    soundTrack = getSoundTrack('mus_dialup_0.ogg', delay=1.5)
    return Parallel(suitTrack, soundTrack, makeShielding)

def doElectrostaticEnergy(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    targets = attack['target']
    cagePropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
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
            getPropAppearTrack(cage, battle, cagePos, 1, scaleUpPoint=Point3(2.0, 2.0, 10.0), scaleUpTime=0),
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
        cagePropTracks.append(cagePropTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracks(attack, damageDelay=1, splicedDamageAnims=damageAnims, dodgeDelay=.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 2.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, toonTrack)

def doCourtMandate(attack):
    if attack['suitName'] == 'jur':
        suitTrack = doCourtMandateHeadAttorney(attack)
    else:
        suitTrack = doCourtRecord3(attack)
    return suitTrack


def doCourtMandateHeadAttorney(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, attack['animName'], duration=3.0), ActorInterval(suit, 'objection-out'), ActorInterval(suit, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))

    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_objection.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doCourtRecord1(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    gavelTrack = doGavelCourtRecord(attack)
    return Parallel(suitTrack, soundTrack, gavelTrack)

def doManagerialProtection(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    notifyTrack = Func(suit.showHpTextWhite, 'IMMUNE!')
    makeImmune = Func(suit.makeImmortal)
    makeUnVulnerable = Func(suit.makeUnVulnerable)
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, notifyTrack, makeUnVulnerable, makeImmune)

def doCourtRecord2(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    gavelTrack = doGavelCourtRecord(attack)
    return Parallel(suitTrack, soundTrack, gavelTrack)

def doCourtRecord3(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntTrack = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'cease'), ActorInterval(attack['suit'], 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    gavelTrack = doGavelCourtRecord(attack)
    return Parallel(suitTrack, soundTrack, tauntTrack, gavelTrack)

def doGavelCourtRecord(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        gavel = globalPropPool.getProp('LB_gavel')
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        gavelPos = Point3(toonPos.getX(), 2, 0)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
            Parallel(getSoundTrack('LB_gavel.ogg', node=toon), Sequence(
                Wait(0.1),
                LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
                LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
            ))
        )
        propTracks.append(propTrack)
        toonTrack = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(__doDamage, toon, dmg, t['died'])
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
    return Parallel(toonTracks, propTracks)


def doOceanliner(attack):
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
            bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1.5)
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
        bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1.5)
        objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        shipTrack.append(objAnimShrink)
        MovieUtil.removeProp(ship2)
    shipTrack.append(Func(MovieUtil.removeProp, ship))
    shipTrack.append(Func(battle.movie.clearRenderProp, ship))
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
        Func(MovieUtil.removeProp, dropShadow),
        Func(battle.movie.clearRenderProp, dropShadow)
    )
    toonTracks = getToonTracks(attack, damageDelay=2.86 + freeCruiseDelay, damageAnimNames=['slip-forward'],
                               dodgeDelay=2.86 + freeCruiseDelay)
    soundTrack = getSoundTrack('AA_drop_boat%s.ogg' % ('' if hitAtleastOneToon else '_miss'),
                               delay=(0.9 if targets[0]['hp'] == 0 else 1.0) + freeCruiseDelay, node=suit)
    hitSounds = Parallel()
    hitSounds.append(getSoundTrack('AA_drop_boat_cog.ogg', delay=2.86 + freeCruiseDelay))
    suitTrack.append(Func(suit.makeNonImmortal))
    multiTrackList = Parallel(suitTrack, shipTrack, shadowTrack, toonTracks, soundTrack, hitSounds)
    multiTrackList.append(getSoundTrack('AA_heal_happydance.ogg', node=suit))
    return multiTrackList

def doRubOut(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    headEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getHeadColor())
    torsoEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getArmColor())
    legsEffect = BattleParticles.createParticleEffect('RubOut', color=toon.style.getLegColor())
    suitTrack = getSuitTrack(attack)
    padPosPoints = [Point3(-0.66, 0.81, -0.06), VBase3(14.93, -2.29, 180.0)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57)
    pencilPosPoints = [Point3(0.04, -0.38, -0.1), VBase3(-170.223, -3.762, -62.929)]
    pencilPropTrack = getPropTrack(pencil, suit.getRightHand(), pencilPosPoints, 0.5, 2.57)
    toonTrack = getToonTrack(attack, 2.2, ['conked'], 2.0, ['jump'])
    hideTrack = Sequence()
    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()
    animal = toon.style.getAnimal()
    bodyScale = ToontownGlobals.toonBodyScales[animal]
    headEffectHeight = __toonFacePoint(toon).getZ()
    legsHeight = ToontownGlobals.legHeightDict[toon.style.legs] * bodyScale
    torsoEffectHeight = ToontownGlobals.torsoHeightDict[toon.style.torso] * bodyScale / 2 + legsHeight
    legsEffectHeight = legsHeight / 2
    effectX = headEffect.getX()
    effectY = headEffect.getY()
    headEffect.setPos(effectX, effectY - 1.5, headEffectHeight)
    torsoEffect.setPos(effectX, effectY - 1, torsoEffectHeight)
    legsEffect.setPos(effectX, effectY - 0.6, legsEffectHeight)
    partDelay = 2.5
    headTrack = getPartTrack(headEffect, partDelay + 0, 0.5, [headEffect, toon, 0])
    torsoTrack = getPartTrack(torsoEffect, partDelay + 1.1, 0.5, [torsoEffect, toon, 0])
    legsTrack = getPartTrack(legsEffect, partDelay + 2.2, 0.5, [legsEffect, toon, 0])

    def hideParts(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setTransparency, 1))
            track.append(LerpFunctionInterval(nextPart.setAlphaScale, fromData=1, toData=0, duration=0.2))

        return track

    def showParts(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))
            track.append(Func(nextPart.clearTransparency))

        return track

    soundTrack = getSoundTrack('SA_rubout.ogg', delay=1.7, node=suit)
    if dmg > 0:
        hideTrack.append(Wait(2.2))
        hideTrack.append(Func(battle.movie.needRestoreColor))
        hideTrack.append(hideParts(headParts))
        hideTrack.append(Wait(0.4))
        hideTrack.append(hideParts(torsoParts))
        hideTrack.append(Wait(0.4))
        hideTrack.append(hideParts(legsParts))
        hideTrack.append(Wait(1))
        hideTrack.append(showParts(headParts))
        hideTrack.append(showParts(torsoParts))
        hideTrack.append(showParts(legsParts))
        hideTrack.append(Func(battle.movie.clearRestoreColor))
        return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack, hideTrack, headTrack, torsoTrack, legsTrack)
    else:
        return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack)

def doDiskScratch(attack):
    suit = attack['suit']
    targets = attack['target']
    pad = loader.loadModel('phase_3.5/models/props/cc_m_prp_gen_coin_silver')
    suitTrack = getSuitAnimTrack(attack)
    padPosPoints = [Point3(0, 0, 0), VBase3(14.93, -2.29, 180.0)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57)
    toonTrack = getToonTracks(attack, 2.2, ['cringe'], 2.0, ['jump'])
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 2.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    soundTrack = getSoundTrack('SA_rubout.ogg', delay=1.7, node=suit)

    return Parallel(suitTrack, toonTrack, padPropTrack, soundTrack, lightingTrack)


def doFingerWag(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('FingerWag')
    BattleParticles.setEffectTexture(particleEffect, 'blah', color=Vec4(0.55, 0, 0.55, 1))
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 1.3
    damageDelay = 2.7
    dodgeDelay = 1.7
    suitTrack = getSuitTrack(attack)
    partTrack = getPartTrack(particleEffect, partDelay, 3, [particleEffect, suit, 0])
    suitName = attack['suitName']
    particleEffect.setPos(0.167, 1.9, suit.getHeight() - 1.8)
    particleEffect.setP(-110)
    toonTrack = getToonTrack(attack, damageDelay, ['slip-backward'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_finger_wag.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, soundTrack)


def doWriteOff(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    BattleParticles.loadParticles()
    checkmark = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
    checkmark.setBillboardPointEye()
    suitTrack = getSuitTrack(attack)
    padPosPoints = [Point3(-0.25, 1.38, -0.08), VBase3(-19.078, -6.603, -171.594)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57, Point3(1.89, 1.89, 1.89))
    missPoint = lambda checkmark = checkmark, toon = toon: __toonMissPoint(checkmark, toon)
    pencilPosPoints = [Point3(-0.47, 1.08, 0.28), VBase3(21.045, 12.702, -176.374)]
    extraArgsForShowProp = [pencil, suit.getRightHand()]
    extraArgsForShowProp.extend(pencilPosPoints)
    pencilPropTrack = Sequence(Wait(0.5), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2), Func(battle.movie.needRestoreRenderProp, checkmark), Func(checkmark.reparentTo, render), Func(checkmark.setScale, 1.6), Func(checkmark.setPosHpr, pencil, 0, 0, 0, 0, 0, 0), Func(checkmark.setP, 0), Func(checkmark.setR, 0))
    pencilPropTrack.append(getPropThrowTrack(attack, checkmark, [__toonFacePoint(toon)], [missPoint]))
    pencilPropTrack.append(Func(MovieUtil.removeProp, checkmark))
    pencilPropTrack.append(Func(battle.movie.clearRenderProp, checkmark))
    pencilPropTrack.append(Wait(0.3))
    pencilPropTrack.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    pencilPropTrack.append(Func(MovieUtil.removeProp, pencil))
    toonTrack = getToonTrack(attack, 3.4, ['slip-forward'], 2.4, ['sidestep'])
    soundTrack = Sequence(Wait(2.3), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_pen_only.ogg'), duration=0.9, node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_ding_only.ogg'), node=suit))
    return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack)

def doWriteOffWritingDesk(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    pad = globalPropPool.getProp('pad')
    pencil = globalPropPool.getProp('pencil')
    BattleParticles.loadParticles()
    checkmark = MovieUtil.copyProp(BattleParticles.getParticle('checkmark'))
    checkmark.setBillboardPointEye()

    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)


    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

    taunt = getAttackTaunt('WriteOff', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'hold-pencil'), suitReset,
                     Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.0))
    suitTrack.append(doWritingDesk(attack))
    padPosPoints = [Point3(-0.25, 1.38, -0.08), VBase3(-19.078, -6.603, -171.594)]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 0.5, 2.57, Point3(1.89, 1.89, 1.89))
    missPoint = lambda checkmark = checkmark, toon = toon: __toonMissPoint(checkmark, toon)
    pencilPosPoints = [Point3(-0.47, 1.08, 0.28), VBase3(21.045, 12.702, -176.374)]
    extraArgsForShowProp = [pencil, suit.getRightHand()]
    extraArgsForShowProp.extend(pencilPosPoints)
    pencilPropTrack = Sequence(Wait(0.5), Func(__showProp, *extraArgsForShowProp), LerpScaleInterval(pencil, 0.5, Point3(1.5, 1.5, 1.5), startScale=Point3(0.01)), Wait(2), Func(battle.movie.needRestoreRenderProp, checkmark), Func(checkmark.reparentTo, render), Func(checkmark.setScale, 1.6), Func(checkmark.setPosHpr, pencil, 0, 0, 0, 0, 0, 0), Func(checkmark.setP, 0), Func(checkmark.setR, 0))
    pencilPropTrack.append(getPropThrowTrack(attack, checkmark, [__toonFacePoint(toon)], [missPoint]))
    pencilPropTrack.append(Func(MovieUtil.removeProp, checkmark))
    pencilPropTrack.append(Func(battle.movie.clearRenderProp, checkmark))
    pencilPropTrack.append(Wait(0.3))
    pencilPropTrack.append(LerpScaleInterval(pencil, 0.5, MovieUtil.PNT3_NEARZERO))
    pencilPropTrack.append(Func(MovieUtil.removeProp, pencil))
    toonTrack = getToonTrack(attack, 3.4, ['slip-forward'], 2.4, ['sidestep'])
    soundTrack = Sequence(Wait(2.3), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_pen_only.ogg'), duration=0.9, node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_writeoff_ding_only.ogg'), node=suit))
    return Parallel(suitTrack, toonTrack, padPropTrack, pencilPropTrack, soundTrack)


def doRubberStamp(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    suitTrack = getSuitTrack(attack)
    stamp = globalPropPool.getProp('rubber-stamp')
    pad = globalPropPool.getProp('pad')
    cancelled = __makeCancelledNodePath()
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        padPosPoints = [Point3(-0.65, 0.83, -0.04), VBase3(5.625, 4.456, -165.125)]
        stampPosPoints = [Point3(-0.64, -0.17, -0.03), MovieUtil.PNT3_ZERO]
    elif suitType == 'c':
        padPosPoints = [Point3(0.19, -0.55, -0.21), VBase3(-166.76, -4.001, -1.658)]
        stampPosPoints = [Point3(-0.64, -0.08, 0.11), MovieUtil.PNT3_ZERO]
    else:
        padPosPoints = [Point3(-0.65, 0.83, -0.04), VBase3(5.625, 4.456, -165.125)]
        stampPosPoints = [Point3(-0.64, -0.17, -0.03), MovieUtil.PNT3_ZERO]
    padPropTrack = getPropTrack(pad, suit.getLeftHand(), padPosPoints, 1e-06, 3.2)
    missPoint = lambda cancelled = cancelled, toon = toon: __toonMissPoint(cancelled, toon)
    propTrack = Sequence(Func(__showProp, stamp, suit.getRightHand(), stampPosPoints[0], stampPosPoints[1]), LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_ONE), Wait(2.6), Func(battle.movie.needRestoreRenderProp, cancelled), Func(cancelled.reparentTo, render), Func(cancelled.setScale, 0.6), Func(cancelled.setPosHpr, stamp, 0.81, -1.11, -0.16, 0, 0, 90), Func(cancelled.setP, 0), Func(cancelled.setR, 0))
    propTrack.append(getPropThrowTrack(attack, cancelled, [__toonFacePoint(toon)], [missPoint]))
    propTrack.append(Func(MovieUtil.removeProp, cancelled))
    propTrack.append(Func(battle.movie.clearRenderProp, cancelled))
    propTrack.append(Wait(0.3))
    propTrack.append(LerpScaleInterval(stamp, 0.5, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, stamp))
    toonTrack = getToonTrack(attack, 3.4, ['conked'], 1.9, ['sidestep'])
    soundTrack = getSoundTrack('SA_rubber_stamp.ogg', delay=1.3, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, padPropTrack, soundTrack)

def doDrop(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    suitTrack = getSuitAnimTrack(attack, delay=0)
    objectTracks = Parallel()
    shadowTracks = Parallel()
    toonTracks = getToonTracks(attack, damageDelay=2.86, damageAnimNames=['Squish'], dodgeDelay=2.86, splicedDodgeAnims=[])
    soundTracks = Parallel()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        objName = {
            SANDBAG: 'sandbag',
            ANVIL: 'anvil',
            BIG_WEIGHT: 'weight',
            SAFE: 'safe',
            GRAND_PIANO: 'piano'
        }
        if name == SANDBAG:
            objZOffset = 0.75
            landFrames = 4
        elif name == ANVIL:
            objZOffset = 0.0
            landFrames = 1
        else:
            objZOffset = 0.0
            landFrames = 11
        object = globalPropPool.getProp(objName[name])
        if objName == 'weight':
            object.setScale(object.getScale() * 0.75)
        elif objName == 'safe':
            object.setScale(object.getScale() * 0.85)
        node = object.node()
        node.setBounds(OmniBoundingVolume())
        node.setFinal(1)
        suitTrack = getSuitTrack(attack)
        objectTrack = Sequence()

        def posObject(object, toon, miss, battle = battle):
            object.reparentTo(battle)
            object.setPos(toon.getPos(battle))
            object.setHpr(toon.getHpr(battle))
            if miss:
                object.setY(object.getY(battle) - 5)
            object.setZ(object.getPos(battle)[2] + objZOffset)

        objectTrack.append(Func(battle.movie.needRestoreRenderProp, object))
        objInit = Func(posObject, object, toon, dmg == 0)
        objectTrack.append(Wait(3.3))
        objectTrack.append(objInit)
        if dmg != 0 or name == SANDBAG or name == ANVIL:
            if hasattr(object, 'getAnimControls'):
                animProp = ActorInterval(object, objName[name])
                shrinkProp = LerpScaleInterval(object, 0.3, MovieUtil.PNT3_NEARZERO, startScale=object.getScale())
                objAnimShrink = ParallelEndTogether(animProp, shrinkProp)
                objectTrack.append(objAnimShrink)
            else:
                startingScale = 1.0
                object2 = MovieUtil.copyProp(object)
                posObject(object2, toon, dmg == 0)
                endingPos = object2.getPos()
                startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
                startHpr = object2.getHpr()
                endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
                animProp = LerpPosInterval(object, landFrames / 24.0, endingPos, startPos=startPos)
                shrinkProp = LerpScaleInterval(object, 0.3, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
                bounceProp = Effects.createZBounce(object, 2, endingPos, 0.5, 1.5)
                objAnimShrink = Sequence(Func(object.setScale, startingScale), Func(object.setH, endHpr[0]), animProp, bounceProp, Wait(1.5), shrinkProp)
                objectTrack.append(objAnimShrink)
                MovieUtil.removeProp(object2)
        elif hasattr(object, 'getAnimControls'):
            animProp = ActorInterval(object, objName[name], duration=landFrames / 24.0)

            def poseProp(prop, animName):
                prop.pose(animName, landFrames)

            poseProp = Func(poseProp, object, objName[name])
            wait = Wait(1.0)
            shrinkProp = LerpScaleInterval(object, 0.1, MovieUtil.PNT3_NEARZERO, startScale=object.getScale())
            objectTrack.append(animProp)
            objectTrack.append(poseProp)
            objectTrack.append(wait)
            objectTrack.append(shrinkProp)
        else:
            startingScale = 1.0
            object2 = MovieUtil.copyProp(object)
            posObject(object2, toon, dmg == 0)
            endingPos = object2.getPos()
            startPos = Point3(endingPos[0], endingPos[1], endingPos[2] + 5)
            startHpr = object2.getHpr()
            endHpr = Point3(startHpr[0] + 90, startHpr[1], startHpr[2])
            animProp = LerpPosInterval(object, landFrames / 24.0, endingPos, startPos=startPos)
            shrinkProp = LerpScaleInterval(object, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp = Effects.createZBounce(object, 2, endingPos, 0.5, 1.5)
            objAnimShrink = Sequence(Func(object.setScale, startingScale), Func(object.setH, endHpr[0]), animProp, bounceProp, Wait(1.5), shrinkProp)
            objectTrack.append(objAnimShrink)
            MovieUtil.removeProp(object2)
        objectTrack.append(Func(MovieUtil.removeProp, object))
        objectTrack.append(Func(battle.movie.clearRenderProp, object))
        objectTracks.append(objectTrack)
        dropShadow = MovieUtil.copyProp(toon.dropShadow)
        if name == SANDBAG or name == ANVIL:
            dropShadow.setScale(0.8)
        elif name == BIG_WEIGHT:
            dropShadow.setScale(2.0)
        elif name == SAFE:
            dropShadow.setScale(2.3)
        else:
            dropShadow.setScale(3.6)

        def posShadow(dropShadow = dropShadow, toon = toon, battle = battle, hp = dmg):
            dropShadow.reparentTo(battle)
            dropShadow.setPos(toon.getPos(battle))
            dropShadow.setHpr(toon.getHpr(battle))
            if hp == 0:
                dropShadow.setY(dropShadow.getY(battle) - 5)
            dropShadow.setZ(dropShadow.getZ() + 0.5)

        shadowTracks.append(Sequence(
            Wait(1.0),
            Func(battle.movie.needRestoreRenderProp, dropShadow),
            Func(posShadow),
            LerpScaleInterval(dropShadow, 1.86, dropShadow.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
            Wait(0.3),
            Func(MovieUtil.removeProp, dropShadow),
            Func(battle.movie.clearRenderProp, dropShadow)
        ))
        soundTracks.append(Sequence(
            Wait(1.0),
            SoundInterval(globalBattleSoundCache.getSound('incoming_whistleALT.ogg'), duration=1.5, node=toon),
            SoundInterval(globalBattleSoundCache.getSound('AA_drop_%s%s.ogg' % ({SANDBAG: 'sandbag', ANVIL: 'anvil', BIG_WEIGHT: 'bigweight', SAFE: 'safe', GRAND_PIANO: 'piano'}[name], '_miss' if dmg == 0 else '')), duration=2.0, node=toon)
        ))
    return Parallel(suitTrack, objectTracks, shadowTracks, toonTracks, soundTracks)

def doNONWORKINGSHIT(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    suit = attack['suit']
    battle = attack['battle']
    #targets = attack['target']
    suitTrack = getSuitTrack(attack)
    stomperTracks = Parallel()
    toonTracks = Parallel()
    #for t in targets:
        #toon = t['toon']
        #dmg = t['hp']
    if suit.getStyleDept() == 'Lawbot':
        stomper = loader.loadModel('phase_11/models/lawbotHQ/LB_square_stomper')
    else:
        stomper = loader.loadModel('phase_9/models/cogHQ/square_stomper')
    shaft = stomper.find('**/shaft')
    shaft.setScale(0.75, 15.0, 0.75)
    stomperPrepare = SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_switch_depressed.ogg'), node=stomper)
    stomperPrepareTime = stomperPrepare.getDuration()
    stomperLift = SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_raise.ogg'), node=stomper)
    stomperLiftTime = stomperLift.getDuration()
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.reparentTo(toon)
    smoke.setScale(0.5)
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.hide()
    smoke.setBillboardPointEye()
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    stomperPos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    stomperTrack = Sequence(
            Parallel(
                getPropAppearTrack(stomper, battle, stomperPos, 0.01, scaleUpPoint=0.0, scaleUpTime=1.0),
                stomperPrepare),
            # LerpPosInterval(stomper, 0.25, Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ())),
            LerpPosInterval(stomper, 0.25, stomperPos),
            Parallel(
                SoundInterval(globalBattleSoundCache.getSound('CHQ_FACT_stomper_small.ogg'), node=stomper),
                Sequence(
                    Wait(1.0),
                    Parallel(
                        stomperLift,
                        LerpPosInterval(stomper, 3, toonPos.getX())
                    ),
                    LerpScaleInterval(stomper, 1.5, MovieUtil.PNT3_ZERO)
                ),
                Sequence(
                    Func(smoke.show),
                    Parallel(
                        LerpScaleInterval(smoke, 0.5, 1),
                        LerpColorScaleInterval(smoke, 0.5, Vec4(0.8, 0.7, 0.5, 0))
                    )
                )
            )
        )
    stomperTracks.append(stomperTrack)
    if dmg != 0:
        toonTrack = Sequence(
                Func(toon.headsUp, battle, suit.getPos(battle)),
                Wait(stomperPrepareTime + 0.25),
                Parallel(
                    Func(toon.enterFlattened),
                    Func(toon.showHpText, -dmg, openEnded=0),
                    Func(__doDamage, toon, dmg, target[0]['died'])
                ),
                Wait(2.5),
                Parallel(
                    Sequence(
                        Wait(0.5),
                        Func(toon.exitFlattened)
                    ),
                    SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=toon),
                    Sequence(
                        ActorInterval(toon, 'jump'),
                        Func(toon.loop, 'neutral')
                    )
                )
            )
        #if target[0]['died']:
            #toonTrack.append(Wait(5.0))
    else:
        toonTrack = Sequence(
                Func(toon.headsUp, battle, suit.getPos(battle)),
                getToonDodgeTrack(attack, target[0], 0.9, ['sidestep'], None)
            )
    toonTracks.append(toonTrack)
    return Parallel(suitTrack, stomperTracks, toonTracks)

def doWhirlwind(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    taunt = random.choice(
        ["You're stirring up a whirlwind of paperwork, Toon.", "Does this remind you of anyone?",
         "There's a storm of legal trouble coming your way.", "The amount of paperwork I have to file for this fight is making my head spin!"])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'effort', playRate=1.25), suitReset)
    cagePropTracks = Parallel()
    # for t in attack['target']:
    # toon = t['toon']
    # dmg = t['hp']
    cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    # cage.setH(90)
    # cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
    spinTrack = Sequence(LerpHprInterval(cage, 5, Point3(-7200, 0, 0)))
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, .50, scaleUpPoint=Point3(2.0), scaleUpTime=1.0),
        Parallel(cagePosition),
        Parallel(
            cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_whirlwind.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_toonInWhirlwind.ogg'), node=cage), Parallel(spinTrack),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(MovieUtil.removeProp, cage)
    )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTrack = getToonTrack(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=0.91,
                             dodgeAnimNames=['sidestep'], showMissedExtraTime=1.0)
    toonSpinTrack = Sequence(Wait(0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)),
                                 LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)),
                                 LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)),
                                 LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)),
                                 LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)),
                             LerpHprInterval(toon, 2.0, Point3(-2620, 0, 0)),
                                 LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0.3, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 5.5, (0.9, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, lightingTrack, toonTrack, toonSpinTrack)

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
    gavelPos = Point3(toonPos.getX(), 2, 0)
    propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0, scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
        Parallel(getSoundTrack('LB_gavel.ogg', node=toon), Sequence(
            Wait(0.1),
            LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
            LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
        ))
    )
    taunt = "Any gags Toons use can and will be held against them in a court of law."
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'effort', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
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
                getSoundTrack('toon_decompress.ogg', node=toon),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
    return Parallel(suitTrack, toonTrack, propTrack)

def doBiteGavel(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    teeth = globalPropPool.getProp('teeth')
    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.45
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4),
                                                   scaleUpTime=propScaleUpTime))
    teethAppearTrack.append(Wait(suitDelay))
    teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
    teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
    if dmg > 0:
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
        hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration), ActorInterval(teeth, 'teeth', duration=0.3), Func(teeth.pose, 'teeth', 1), Wait(0.7), ActorInterval(teeth, 'teeth', duration=0.9))
        propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
    else:
        flyPoint = __toonFacePoint(toon, parent=battle)
        flyPoint.setY(flyPoint.getY() - 7.1)
        teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
        teethAppearTrack.append(Func(MovieUtil.removeProp, teeth))
        teethAppearTrack.append(Func(battle.movie.clearRenderProp, teeth))
        propTrack = teethAppearTrack
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
    toonTrack = getToonTrack(attack, damageDelay=2.6, splicedDamageAnims=damageAnims, dodgeDelay=2.3, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.4)
    soundTrack = getSoundTrack('SA_bite.ogg', delay=2.3, node=suit)
    soundTrack2 = getSoundTrack('SA_bite_miss.ogg', delay=2.3, node=suit)
    taunt = getAttackTaunt('Bite', attack['suitName'])
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doGavel(attack))
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, propTrack)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack2, propTrack)


def doGavelOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    gavel = globalPropPool.getProp('LB_gavel')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitTrack = getSuitTrack(attack)
    gavelPosPoints = [Point3(0, 3, 0), VBase3(180, 0, 0)]
    downTime = 0.25
    upTime = 1
    downAngle = .80
    goingDown = LerpHprInterval(gavel, downTime, Point3(0, downAngle, 0), startHpr=Point3(0, 0, 0))
    goingUp = LerpHprInterval(gavel, upTime, Point3(0, 0, 0), startHpr=Point3(0, downAngle, 0))
    gavelPropTrack = Sequence()
    soundTrack = getSoundTrack('LB_gavel.ogg', delay= 2.25, node=toon)
    soundTrack2 = getSoundTrack('LB_gavel.ogg', delay= 4.0, node=toon)
    if dmg > 0 :
        gavelPropTrack.append(Sequence(getPropAppearTrack(gavel, suit, gavelPosPoints, 1e-06, Point3(1, 1, 1), scaleUpTime=1.0), Wait(1), goingDown, Wait(0.5), goingUp, goingDown, Wait(1), goingUp, Wait(0.5),
                                       getPropAppearTrack(gavel, suit, gavelPosPoints, 1e-06, Point3(0, 0, 0), 1.0, Point3(1, 1, 1)),
                                       Func(battle.movie.clearRenderProp, gavel),
                                       Func(MovieUtil.removeProp, gavel)))
        toonTrack = getToonTrack(attack, 2.25, ['neutral'], 1.0, ['sidestep'])
        return Parallel(suitTrack, toonTrack, gavelPropTrack, soundTrack, soundTrack2)
    else:
        gavelPropTrack.append(
            Sequence(getPropAppearTrack(gavel, suit, gavelPosPoints, 1e-06, Point3(1, 1, 1), scaleUpTime=1.0), Wait(1),
                     goingDown, Wait(0.5), goingUp, goingDown, Wait(1), goingUp, Wait(0.5),
                     getPropAppearTrack(gavel, suit, gavelPosPoints, 1e-06, Point3(0, 0, 0), 1.0, Point3(1, 1, 1)),
                     Func(battle.movie.clearRenderProp, gavel),
                     Func(MovieUtil.removeProp, gavel)))
        toonTrack = getToonTrack(attack, 2.25, ['neutral'], 1.0, ['sidestep'])
        return Parallel(suitTrack, toonTrack, gavelPropTrack, soundTrack)

def doStomper(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Quality Control dictates that all Toon-Up and Trap gags are now classified as defective.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(2))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
    cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))
    shaft = cage.find('**/shaft')
    shaft.setScale(0.75, 15.0, 0.75)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.75), scaleUpTime=0.1), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 0.75, ['conked'])
    notifyTrack = Sequence(Wait(.75), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "BUSTED!"))
    return Parallel(suitTrack, cagePropTracks, toonTrack, notifyTrack)

def doCage(attack):
    suit = attack['suit']
    targets = attack['target']
    battle = attack['battle']
    taunt = random.choice(
        ["There's no escaping this time, Toon.", "Good things come to those who wait.",
         "Someone isn't doing their part around here."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'summon', playRate=1.25), Func(suit.setNeutralAnimation))
    cagePropTracks = Parallel()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_crg_toonCage')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        if dmg <= 0:
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
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, toonTracks)

def doCollectCall(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(8.25))
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
        explodeTrack.append(Wait(8.25))
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
    x = toonPos.getX() - 5
    if dmg == 0:
        x -= 10
    cagePos = [Point3(toonPos.getX(), toonPos.getY(), 20.0), toon.getHpr(battle)]
    cagePos2 = [Point3(toonPos.getX(), toonPos.getY(), 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.0), scaleUpTime=1.0),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), x, 0.5), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
            Wait(6.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTrack2 = Sequence(
        getPropAppearTrack(cage2, battle, cagePos2, 0.01, scaleUpPoint=Point3(1.0), scaleUpTime=1.0),
        Parallel(
            cage2.posInterval(0.75, Point3(toonPos.getX(), x, 0.5), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/ashfhadh.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/afhdhsdhsd.ogg'), node=cage2),
        Wait(6.5),
        LerpFunctionInterval(cage2.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage2)
    )
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')

    phonePosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    receiverPosPoints = [Point3(-0.23, 0, -0.11), VBase3(5.939, 2.763, -177.591)]
    propTrack = Sequence(Wait(1.75), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]),
                         Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Wait(0.24),
                         Func(receiver.wrtReparentTo, suit.getRightHand()),
                         LerpPosHprInterval(receiver, 0.0001, Point3(-0.45, 0.48, -0.62), VBase3(-87.47, -18.21, 7.82)),
                         Wait(5.25), Func(receiver.wrtReparentTo, phone), Wait(0.62),
                         LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO),
                         Func(MovieUtil.removeProps, [receiver, phone]))
    suitSpeechTrack = Sequence(Wait(6.0), Func(suit.setChatAbsolute, "You should know not to talk to strangers.", CFSpeech | CFTimeout))
    cagePropTracks.append(cagePropTrack)
    cagePropTracks.append(cagePropTrack2)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 and 7 Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack.append(Sequence(headsUp, ActorInterval(suit, 'phone', duration=3.0), Wait(3.0), ActorInterval(suit, 'phone', startTime=3.0), suitReset, Func(suit.setNeutralAnimation)))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    makeUnvulnerable = Func(suit.makeUnVulnerable)
    soundTrack1 = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=1.75, node=suit)
    soundTrack2 = getSoundTrack('SA_bash.ogg', delay=0, node=suit)
    soundTrack3 = getSoundTrack('ENC_cogfall_apart.ogg', delay=8.25, node=suit)
    soundTrack4 = getSoundTrack('telephone_ring.ogg', delay=2.0, node=suit)
    soundTrack = Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4)
    toonTrack = Sequence(ActorInterval(toon, 'confused'), ActorInterval(toon, 'takePhone'), ActorInterval(toon, 'phoneNeutral', duration=1))
    toonTrack.append(getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 0.5, ['conked']))
    notifyTrack = Sequence(Wait(8.25), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "VULNERABLE!"))
    return Parallel(explodeTracks, suitTrack, cagePropTracks, toonTrack, notifyTrack, makeUnvulnerable, soundTrack, suitSpeechTrack, explosionTrack, propTrack)

def doDiceRoulette(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(2.0), scaleUpTime=0.5),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), y, 2.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    suitTrack.append(Func(suit.makeNonImmortal))
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    cameraTrack = Sequence(
        LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -25, 10), hpr=Point3(0, 0, 0),
                           blendType='easeInOut'))
    return Parallel(suitTrack, cagePropTracks, toonTrack, cameraTrack)

def doAceInTheHole(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Func(suit.makeNonImmortal))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/cc_a_prp_bat_playcard')
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 20.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(2.0), scaleUpTime=0.5),
            Parallel(
                cage.posInterval(0.75, Point3(toonPos.getX(), y, 2.01), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/CHQ_SOS_cage_land.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    cameraTrack = Sequence(
        LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -25, 10), hpr=Point3(0, 0, 0),
                           blendType='easeInOut'))
    return Parallel(suitTrack, cagePropTracks, toonTrack, cameraTrack)

def doBarOLD(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 30.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(2.0), scaleUpTime=0.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=1.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    return Parallel(suitTrack, cagePropTracks, toonTrack)

def doBarNew(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    ship = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    ship4 = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    ship.setScale(4.085, 4.342, 2.928)
    ship4.setScale(4.085, 4.342, 2.928)
    freeCruiseDelay = 0
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitAnimTrack(attack)
        suitTrack.append(Wait(1.36))
        suit.setHealthForMe(int(suit.currHP - (250 * len(battle.activeToons))))
        suitTrack.append(Func(suit.showHpText, - (250 * len(battle.activeToons))))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if suit.currHP <= 0 and not suit.dna.name == 'mad':
            suitTrack.append(MovieUtil.createSuitCrashTrack(suit, battle))
        suitTrack.append(ActorInterval(suit, 'flatten'))
        suitTracks.append(suitTrack)
        if suit.currHP <= 0 and suit.dna.name == 'mad':
            suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        elif suit.isLured:
            suitTrack.append(Func(suit.loop, 'neutral-lured'))
        else:
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
            bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1.5)
            objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp,
                                     bounceProp, Wait(1.5), shrinkProp)
            animProp2 = LerpPosInterval(ship4, landFrames / 24.0, endingPos2, startPos=startPos2)
            shrinkProp2 = LerpScaleInterval(ship4, 0.1, MovieUtil.PNT3_NEARZERO, startScale=startingScale)
            bounceProp2 = Effects.createZBounce(ship4, 2, endingPos2, 0.5, 1.5)
            objAnimShrink2 = Sequence(Func(ship4.setScale, startingScale), Func(ship4.setH, endHpr2[0]), animProp2,
                                     bounceProp2, Wait(1.5), shrinkProp2)
            shipTrack.append(objAnimShrink)
            MovieUtil.removeProp(ship2)
            shipTrack2.append(objAnimShrink2)
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
        bounceProp = Effects.createZBounce(ship, 2, endingPos, 0.5, 1.5)
        objAnimShrink = Sequence(Func(ship.setScale, startingScale), Func(ship.setH, endHpr[0]), animProp, bounceProp,
                                 Wait(1.5), shrinkProp)
        shipTrack.append(objAnimShrink)
        MovieUtil.removeProp(ship2)
    shipTrack.append(Func(MovieUtil.removeProp, ship))
    shipTrack.append(Func(battle.movie.clearRenderProp, ship))
    shipTrack.append(Func(MovieUtil.removeProp, ship4))
    shipTrack.append(Func(battle.movie.clearRenderProp, ship4))
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
        Func(MovieUtil.removeProp, dropShadow),
        Func(battle.movie.clearRenderProp, dropShadow)
    )
    toonTracks = getToonTracks(attack, damageDelay=2.86 + freeCruiseDelay, damageAnimNames=['slip-forward'],
                               dodgeDelay=2.86 + freeCruiseDelay)
    hitSounds = Parallel()
    hitSounds.append(getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=2.86 + freeCruiseDelay))
    multiTrackList = Parallel(suitTracks, shipTrack2, shipTrack, shadowTrack, toonTracks, hitSounds)
    return multiTrackList

def doConeOfShame(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    taunt = "This Toon has been accused of not following proper safe-ty guidelines."
    taunt2 = "Someone isn't doing their part around here."
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    tauntInterval2 = Sequence(Func(suit.setChatAbsolute, taunt2, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'finger-wag'), Func(suit.setNeutralAnimation), Wait(1.0), tauntInterval2, ActorInterval(suit, 'summon', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doHypnoEyes(attack, 3))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_3.5/models/props/barrier_cone')
    cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 30.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(Wait(5.0),
            getPropAppearTrack(cage, battle, cagePos, .5, scaleUpPoint=Point3(3), scaleUpTime=0.1),
            Parallel(
                cage.posInterval(0.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=0.5, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg'), node=cage),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0), Wait(1.5),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 1, 1.3]]
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 5.5, ['slip-forward'])
    notifyTrack = Sequence(Wait(5.5), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "BREACH!"))
    return Parallel(suitTrack, cagePropTracks, toonTrack, notifyTrack)

def doBarMulti(attack):
    suit = attack['suit']
    targets = attack['target']
    target = attack['target']
    #toons = target[0]['toon']
    #dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack)
    cagePropTracks = Parallel()
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_10/models/cashbotHQ/GoldBar')
    #cage.setHpr(90, 90, 90)
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    for t in attack['target']:
        toon = t['toon']
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        cagePos = [Point3(toonPos.getX(), y, 90.0), toon.getHpr(battle)]
        cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(3.0), scaleUpTime=0.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(1.0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/incoming_whistleALT.ogg'), duration=1.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cmg_itemHitsFloor.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        damageAnims = [['slip-forward', 0.0001, 1.3]]
        toonTracks = getToonTracks(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
        cameraTrack = Sequence(
            LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -25, 10), hpr=Point3(0, 0, 0),
                               blendType='easeInOut'))
        return Parallel(suitTrack, cagePropTracks, toonTracks, cameraTrack)

def doAfterShock(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    taunt = random.choice(
        ["I think this is called 'delayed physical aggression.'",  "I'm only going to hit back as hard as you do!'",
         "I bet this one will 'shock' you!",  "I heard you Toons like roughhousing, can I play too?",
         "I can weather the storm, Toons.",
         "Why are you playing with electricity when I have enough for the both of us?!"])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'objection'), suitReset, Func(suit.setNeutralAnimation))
    ceaseTrack = Parallel(Func(suit.makeStormCell), ActorInterval(suit, 'transformation'))
    ceaseTrack.append(Func(suit.showHpString, "HEAVY RAIN!"))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     random.choice(("I think this is called 'delayed physical aggression.'",  "I'm only going to hit back as hard as you do!'",
         "I bet this one will 'shock' you!",  "I heard you Toons like roughhousing, can I play too?",
         "I can weather the storm, Toons.",
         "Why are you playing with electricity when I have enough for the both of us?!")),
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSpeechTrack))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/lightning')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 1.90, scaleUpPoint=Point3(2.0, 2.0, 10.0), scaleUpTime=0), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 2.5, ['slip-forward'])
    notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "SHOCKED!"))
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0.3, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 3.5, (0.9, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, toonTrack, lightingTrack, notifyTrack)

def doAfterShockChairman(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    taunt = random.choice(
        ["I think this is called 'delayed physical aggression.'",  "I'm only going to hit back as hard as you do!'",
         "I bet this one will 'shock' you!",  "I heard you Toons like roughhousing, can I play too?",
         "I can weather the storm, Toons.",
         "Why are you playing with electricity when I have enough for the both of us?!"])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'layoffs'), suitReset, Func(suit.setNeutralAnimation))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "So, I see you are very reliant on your Zap gags. Let's see how you do without them.",
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'tcm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/lightning')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 1.90, scaleUpPoint=Point3(2.0, 2.0, 10.0), scaleUpTime=0),
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
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 2.5, ['slip-forward'])
    notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "SHOCKED!"))
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(0), LerpColorScaleInterval(render, 0.5, (0.3, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 3.5, (0.9, 0.3, 0.3, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, cagePropTracks, toonTrack, lightingTrack, notifyTrack)

def doFreeCruiseOLD(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = getSuitTrack(attack)
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/ship')
    #cage.setHpr(90, 90, 90)
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 30.0), toon.getHpr(battle)]
    cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(1.5), scaleUpTime=0.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(1.5, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_drop_boat.ogg'), duration=3.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/AA_drop_boat_cog.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
    cameraTrack = Sequence(
        LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -20, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    return Parallel(suitTrack, cagePropTracks, toonTrack, cameraTrack)

def doFreeCruiseMulti(attack):
    suit = attack['suit']
    targets = attack['target']
    target = attack['target']
    #toons = target[0]['toon']
    #dmg = target[0]['hp']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack)
    cagePropTracks = Parallel()
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/ship')
    #cage.setHpr(90, 90, 90)
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    for t in attack['target']:
        toon = t['toon']
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
        cagePosition = LerpHprInterval(cage, 0, Point3(90, 0, 0))
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(1.0), scaleUpTime=0.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(2.0, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_drop_boat.ogg'), duration=2.0, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_drop_boat_cog.ogg'), node=cage),
            Wait(1.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )
        cagePropTracks.append(cagePropTrack)
        damageAnims = [['slip-forward', 0.0001, 1.3]]
        toonTracks = getToonTracks(attack, damageDelay=3.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=[], splicedDodgeAnims=[], showDamageExtraTime=0.5)
        cameraTrack = Sequence(
            LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -25, 10), hpr=Point3(0, 0, 0),
                               blendType='easeInOut'))
        return Parallel(suitTrack, cagePropTracks, toonTracks, cameraTrack)

def doDetonate(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    managerTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(manager, 'neutral%s' % ('-hurt' if float(manager.currHP) / float(manager.maxHP) <= 0.25 else '')))
    suitTrack = Sequence(Wait(1.0), Func(targetSuit.showHpText, "DETONATE!", 10), ActorInterval(targetSuit, 'soak', duration = 1.25), Sequence(MovieUtil.createSuitDeathTrack(targetSuit, None, battle, [], False)))
    toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, toonTrack, soundTrack)

def doUnionBust(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    #toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    managerTrack = Sequence(getSuitAnimTrack(attack))
    managerTrack.append(Parallel(Sequence(Func(manager.setChatAbsolute,
                                                       "No unions will be formed under my watch, thank you for your contribution.",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(0.5)))))
    suitTrack = Sequence(Wait(1.0), ActorInterval(targetSuit, 'flatten', duration = 1.25), Sequence(MovieUtil.createSuitCrashTrack(targetSuit, battle)))
    #toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    cagePropTracks = Parallel()
    # for t in attack['target']:
    # toon = t['toon']
    # dmg = t['hp']
    cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
    cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))
    shaft = cage.find('**/shaft')
    shaft.setScale(0.75, 15.0, 0.75)
    targetSuitPos = targetSuit.getPos(battle)
    y = targetSuitPos.getY()
    cagePos = [Point3(targetSuitPos.getX(), y, 20.0), targetSuit.getHpr(battle)]
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.4), scaleUpTime=0.1),
        Parallel(cagePosition),
        Parallel(
            cage.posInterval(0.5, Point3(targetSuitPos.getX(), y, 0.01), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'), duration=1.0, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/toon_decompress.ogg'), node=cage),
        Wait(1.5),
        LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage)
    )
    cagePropTracks.append(cagePropTrack)
    cagePropTrack2 = Sequence(Wait(2), cagePropTrack)
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpTextCheat, -targetSuit.currHP), Func(targetSuit.showHpString, "BUSTED!"), Func(targetSuit.setHealthForMe, - targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2))
    managerHealTrack.append(Wait(8))
    managerHealTrack.append(doWorkersCompensation3(attack, ind))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_quake.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, soundTrack, selfDamageTrack, managerHealTrack, cagePropTrack2)

def doHeadRoller(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.setNeutralAnimation))
    managerTrack.append(Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "Someone isn't doing their part around here, your health is now mine.",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(0.5)))))
    suitTrack = Sequence(Wait(1.0), ActorInterval(targetSuit, 'soak', duration = 2.25), Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                       "Ouch.",
                                                       CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpTextCheat, -targetSuit.currHP), Func(targetSuit.showHpString, "SYPHONED!"), Func(targetSuit.setHealthForMe, - targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2))
    managerHealTrack.append(Wait(8))
    managerHealTrack.append(doWorkersCompensation2(attack, ind))
    #toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, soundTrack, selfDamageTrack, managerHealTrack)

def doHeadRollerGroup(attack, ind, ind2, ind3, ind4, ind5):
    manager = attack['suit']
    battle = attack['battle']
    targetSuit = battle.activeSuits[ind]
    targetSuit1 = battle.activeSuits[ind2]
    targetSuit2 = battle.activeSuits[ind3]
    targetSuit3 = battle.activeSuits[ind4]
    targetSuit4 = battle.activeSuits[ind5]

    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.setNeutralAnimation))
    managerTrack.append(Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "Such a shame, don't worry guys, your health will be put to much better use.",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(0.5)))))
    suitTrack = Sequence(Wait(1.0), ActorInterval(targetSuit, 'soak', duration = 2.25), Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                       "Ouch.",
                                                       CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpTextCheat, -targetSuit.currHP), Func(targetSuit.showHpString, "SYPHONED!"), Func(targetSuit.setHealthForMe,  - targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, 0))
    suitTrack1 = Sequence(Wait(1.1),
                         ActorInterval(targetSuit1, 'soak', duration=2.25),
                         Sequence(MovieUtil.spawnHeadExplosion(targetSuit1, battle)), Func(targetSuit1.setChatAbsolute,
                                                                                          "Ouch.",
                                                                                          CFSpeech | CFTimeout),
                         Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit1, battle))
    selfDamageTrack1 = Sequence(Wait(2), Func(targetSuit1.showHpTextCheat, -targetSuit1.currHP), Func(targetSuit1.showHpString, "SYPHONED!"), Func(targetSuit1.setHealthForMe, - targetSuit1.currHP),
                               Func(targetSuit1.updateHealthBar, 0))
    suitTrack2 = Sequence(Wait(1.2),
                         ActorInterval(targetSuit2, 'soak', duration=2.25),
                         Sequence(MovieUtil.spawnHeadExplosion(targetSuit2, battle)), Func(targetSuit2.setChatAbsolute,
                                                                                          "Ouch.",
                                                                                          CFSpeech | CFTimeout),
                         Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit2, battle))
    selfDamageTrack2 = Sequence(Wait(2), Func(targetSuit2.showHpTextCheat, -targetSuit2.currHP), Func(targetSuit2.showHpString, "SYPHONED!"), Func(targetSuit2.setHealthForMe, - targetSuit2.currHP),
                               Func(targetSuit2.updateHealthBar, 0))
    suitTrack3 = Sequence(Wait(1.3),
                         ActorInterval(targetSuit3, 'soak', duration=2.25),
                         Sequence(MovieUtil.spawnHeadExplosion(targetSuit3, battle)), Func(targetSuit3.setChatAbsolute,
                                                                                          "Ouch.",
                                                                                          CFSpeech | CFTimeout),
                         Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit3, battle))
    selfDamageTrack3 = Sequence(Wait(2), Func(targetSuit3.showHpTextCheat, -targetSuit3.currHP),Func(targetSuit3.showHpString, "SYPHONED!"), Func(targetSuit3.setHealthForMe,  - targetSuit3.currHP)
                                ,
                                Func(targetSuit3.updateHealthBar, 0)
                                )
    suitTrack4 = Sequence(Wait(1.3),
                         ActorInterval(targetSuit4, 'soak', duration=2.25),
                         Sequence(MovieUtil.spawnHeadExplosion(targetSuit4, battle)), Func(targetSuit4.setChatAbsolute,
                                                                                          "Ouch.",
                                                                                          CFSpeech | CFTimeout),
                         Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit4, battle))
    selfDamageTrack4 = Sequence(Wait(2), Func(targetSuit4.showHpTextCheat, -targetSuit4.currHP), Func(targetSuit4.showHpString, "SYPHONED!"),
                               Func(targetSuit4.setHealthForMe, - targetSuit4.currHP), Func(targetSuit4.updateHealthBar, 0))





    managerHealTrack = Sequence(Wait(2))
    managerHealTrack.append(Wait(8))
    managerHealTrack.append(doWorkersCompensationGroup(attack, 1, 2, 3, 4, 5))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=manager))
    return Parallel(managerTrack, suitTrack, suitTrack1, suitTrack2, suitTrack3, suitTrack4, soundTrack, selfDamageTrack, selfDamageTrack1, selfDamageTrack2, selfDamageTrack3, selfDamageTrack4, managerHealTrack)

def doHeadRollerHighRoller(attack, ind):
    manager = attack['suit']
    battle = attack['battle']
    toons = attack['target']
    targetSuit = battle.activeSuits[ind]

    manager.setHealthForMe(int(manager.currHP + targetSuit.currHP))
    targetSuit.setHealthForMe(int(targetSuit.currHP - targetSuit.currHP))

    managerTrack = Sequence(getSuitAnimTrack(attack), Func(manager.setNeutralAnimation))
    managerTrack.append(Parallel(Sequence(Wait(4.0), Func(manager.setChatAbsolute,
                                                       "WHAT A TWIFFT, BUTTERCUP BLUE!.",
                                                       CFSpeech | CFTimeout),
                                       Sequence(Wait(0.5)))))
    suitTrack = Sequence(Wait(1.0), Func(targetSuit.showHpText, "SYPHONED!", 10), ActorInterval(targetSuit, 'soak', duration = 2.25), Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                       "Ouch.",
                                                       CFSpeech | CFTimeout), Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpText, -targetSuit.currHP), Func(targetSuit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(2), Func(manager.showHpText, +targetSuit.currHP), Func(manager.updateHealthBar, 0))
    #toonTrack = getToonTracks(attack, 7.35, ['cringe'], 2.0, ['neutral'])
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=targetSuit))
    return Parallel(managerTrack, suitTrack, soundTrack, selfDamageTrack, managerHealTrack)

def doSpotlight(attack):
    suit = attack['suit']
    battle = attack['battle']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit)

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(3))
        suitTrack.append(Parallel(Sequence(Func(suit.setChatAbsolute, "I'll try my best!", CFSpeech | CFTimeout), ActorInterval(suit, 'dance'), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))))
        suitTrack.append(Parallel(healSound, Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suit.setHealthForMe(int(suit.currHP + 500))
        suitTrack.append(Func(suit.showHpText, 500))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        #suitTrack.append(Parallel(Sequence(Wait(3), Func(suit.setChatAbsolute, "I'll try my best!", ActorInterval(suit, 'dance'), Wait(7), Func(suit.setChatAbsolute, 'Well adjusted.', CFSpeech | CFTimeout)))))
        suitTracks.append(suitTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack1 = getSoundTrack('SA_bash.ogg', node=suit)
    soundTrack2 = getSoundTrack('LB_camera_shutter_2.ogg', delay=1, node=suit)
    soundTrack3 = getSoundTrack('AA_heal_happydance.ogg', delay=3, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2, soundTrack3)
    return Parallel(suitTrack, suitTracks, multiTrack)

def doGroupSyphonCheat(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        makeSyphon = Func(suit.makeSyphon)
        suitTrack = Sequence()
        suitTrack.append(Wait(3))
        suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout))
        suitTrack.append(makeSyphon)
        suitTracks.append(suitTrack)
    suitTrack = Sequence(ActorInterval(theSuit, 'scabbard'), Func(theSuit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    ceaseSpeechTrack = Parallel(Func(theSuit.setChatAbsolute,
                                     "Your attacks will be a little bit more enlightening from now on.",
                                     CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('SA_scabbard.ogg', node=theSuit)
    return Parallel(suitTrack, suitTracks, ceaseSpeechTrack, soundTrack1)



def doRazzleDazzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    sign = globalPropPool.getProp('smile')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Smile')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    signPosPoints = [Point3(0.0, -0.42, -0.04), VBase3(105.715, 73.977, 65.932)]
    if hitSuit:
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
    else:
        hitPoint = lambda particleEffect = particleEffect, toon = toon, suit = suit: __toonMissPoint(particleEffect, toon, parent=suit.getRightHand())
    signPropTrack = Sequence(Func(__showProp, sign, suit.getRightHand(), signPosPoints[0], signPosPoints[1]), LerpScaleInterval(sign, 0.5, Point3(1.39, 1.39, 1.39)), Wait(0.5), Func(battle.movie.needRestoreParticleEffect, particleEffect), Func(particleEffect.start, sign), Func(particleEffect.wrtReparentTo, render), LerpPosInterval(particleEffect, 1.0, pos=hitPoint), Func(particleEffect.cleanup), LerpScaleInterval(sign, 0.5, Point3(0, 0, 0)), Func(battle.movie.clearRestoreParticleEffect, particleEffect))
    signPropAnimTrack = ActorInterval(sign, 'smile', duration=2.5, startTime=0)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 7 and 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'blr':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    toonTrack = getToonTrack(attack, 2.0, ['cringe'], 1.3, ['sidestep'])
    soundTrack = getSoundTrack('SA_razzle_dazzle.ogg', delay=0.8, node=suit)
    return Sequence(Parallel(suitTrack, signPropTrack, signPropAnimTrack, toonTrack, soundTrack), Func(MovieUtil.removeProp, sign))

def doRazzleDazzleBomb(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    sign = globalPropPool.getProp('smile')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Smile')
    taunt = getAttackTaunt('RazzleDazzle', attack['suitName'])
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'smile', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    signPosPoints = [Point3(0.0, -0.42, -0.04), VBase3(105.715, 73.977, 65.932)]
    if hitSuit:
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
    else:
        hitPoint = lambda particleEffect = particleEffect, toon = toon, suit = suit: __toonMissPoint(particleEffect, toon, parent=suit.getRightHand())
    signPropTrack = Sequence(Func(__showProp, sign, suit.getRightHand(), signPosPoints[0], signPosPoints[1]), LerpScaleInterval(sign, 0.5, Point3(1.39, 1.39, 1.39)), Wait(0.5), Func(battle.movie.needRestoreParticleEffect, particleEffect), Func(particleEffect.start, sign), Func(particleEffect.wrtReparentTo, render), LerpPosInterval(particleEffect, 1.0, pos=hitPoint), Func(particleEffect.cleanup), LerpScaleInterval(sign, 0.5, Point3(0, 0, 0)), Func(battle.movie.clearRestoreParticleEffect, particleEffect))
    signPropAnimTrack = ActorInterval(sign, 'smile', duration=2.5, startTime=0)
    suitTrack.append(Wait(1.0))
    suitTrack.append(doBomb(attack))
    toonTrack = getToonTrack(attack, 2.0, ['cringe'], 1.3, ['sidestep'])
    soundTrack = getSoundTrack('SA_razzle_dazzle.ogg', delay=0.8, node=suit)
    return Sequence(Parallel(suitTrack, signPropTrack, signPropAnimTrack, toonTrack, soundTrack), Func(MovieUtil.removeProp, sign))


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
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
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


def doSynergy2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 7 Gags are now off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    pbpDesc2 = pbpDc.getShowIntervalDesc('The interest fees are racking up!', 3.5)
    pbpTrack2 = pbpText.getShowIntervalCheat('Compound Interest!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    costsTrack = Parallel(pbpDesc2, pbpTrack2)
    suitTrack.append(Parallel(Sequence(Wait(0.1), Func(suit.setChatAbsolute,
                                                       'Quality Control dictates that all Level 7 and 8 gags are now classified as defective.',
                                                       CFSpeech | CFTimeout))))
    suitTrack.append(ceaseTrack)
    suitTrack.append(Func(suit.setNeutralAnimation))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0),
                               SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(4.0),
                               SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doUnionDues(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    ceaseTrack = ActorInterval(suit, 'cease')
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Parallel(Sequence(Wait(0.1), Func(suit.setChatAbsolute,
                                                       'Quality Control dictates that all Toon-Up and Zap gags are now classified as defective.',
                                                       CFSpeech | CFTimeout))))
    suitTrack.append(ceaseTrack)
    suitTrack.append(Func(suit.setNeutralAnimation))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0),
                               SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(4.0),
                               SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doCourtCosts(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 8 Gags are now off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Court Record!', 3.5)
    pbpDesc2 = pbpDc.getShowIntervalDesc('The fees are racking up!', 3.5)
    pbpTrack2 = pbpText.getShowIntervalCheat('Court Costs!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    costsTrack = Parallel(pbpDesc2, pbpTrack2)
    suitTrack.append(Parallel(Sequence(Wait(0.1), Func(suit.setChatAbsolute,
                                   'Any Level 6 and 8 Gags Toons use can and will be held against them in a court of law.', CFSpeech | CFTimeout))))
    suitTrack.append(ceaseTrack)
    suitTrack.append(Func(suit.setNeutralAnimation))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(4.0),
                               SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doCollectCallFees(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('Level 6 and 8 Gags are now off-limits!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Quality Control!', 3.5)
    pbpDesc2 = pbpDc.getShowIntervalDesc('The fees are racking up!', 3.5)
    pbpTrack2 = pbpText.getShowIntervalCheat('Collect Call Costs!', 3.5)
    ceaseTrack = ActorInterval(suit, 'cease')
    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    costsTrack = Parallel(pbpDesc2, pbpTrack2)
    suitTrack.append(Parallel(Sequence(Wait(0.1), Func(suit.setChatAbsolute,
                                                       'Quality Control dictates that all Level 6 and 8 gags are now classified as defective.',
                                                       CFSpeech | CFTimeout))))
    suitTrack.append(ceaseTrack)
    suitTrack.append(Func(suit.setNeutralAnimation))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(2.0),
                               SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        soundTrack2 = Sequence(Wait(4.0),
                               SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
        multiTrack = Parallel(soundTrack1, soundTrack2)
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks, multiTrack)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doFreezingRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    sprayEffect = BattleParticles.createParticleEffect('WaterSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 10.6, 6.7))
    waterfallEffect = BattleParticles.createParticleEffect(file='snowWaterfall')
    suitTrack = getSuitAnimTrack(attack)
    ceaseTrack = ActorInterval(suit, 'objection')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Lure and Sound gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    ceaseTrack2 = Parallel(Func(suit.makeFreezingRain), ActorInterval(suit, 'transformation'))
    ceaseTrack2.append(Func(suit.showHpString, "FREEZING RAIN!"))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                     random.choice(("Why don't you take a chill pill?", "You've gone and done it now, haven't you?",
                                                    "This is really gonna freeze you up, Toons.")),
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvp':
        suitTrack.append(Wait(2.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
        suitTrack.append(Wait(2.0))
        suitTrack.append(Parallel(ceaseTrack2, ceaseSpeechTrack2))
    for suit in battle.activeSuits:
        suitTrack.append(Func(suit.removeInsured))
    partTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    damageAnims = [['cringe']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['cringe'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_freeze.ogg')))
    makeFrozen = Func(suit.makeFrozen)
    if hitAtleastOneToon > 0:
        soundTrack1 = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_freeze.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, sprayTrack, makeFrozen, waterfallTrack, synergySoundTrack, toonTracks, soundTrack1)
    else:
        return Parallel(suitTrack, partTrack, sprayTrack, waterfallTrack, synergySoundTrack, toonTracks)


def doHeatWave(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect(file='heatwave')
    waterfallEffect = BattleParticles.createParticleEffect(file='heatwaveWaterfall')
    taunt = random.choice(
        ["You're about to have a meltdown, Toons.", "Hope you wore sunscreen, this battle is about to get even hotter!",
         "If you can't handle the heat, stay out of the kitchen.", "Let's crank up the heat!",
         "Can you handle the heat, Toons?"])

    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, attack['animName']), Func(suit.setNeutralAnimation))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    soundTrack1 = Sequence(Wait(.5), SoundInterval(globalBattleSoundCache.getSound('SA_hot_air.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        return Parallel(suitTrack, partTrack, waterfallTrack, toonTracks, soundTrack1)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, toonTracks, soundTrack1)


def doConDuckTion(attack):
    suit = attack['suit']
    battle = attack['battle']
    propDelay = 0.6
    throwDelay = 1.67
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
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
                Func(MovieUtil.removeProp, next)
            )
            duckTracks.append(duckTrack)

        allDuckTracks.append(duckTracks)
    suitTrack.append(Func(suit.makeNonImmortal))
    damageAnims = [['cringe', 0.01, 0.14, 0.21],
                   ['cringe', 0.01, 0.14, 0.13],
                   ['cringe', 0.01, 0.43]]
    toonTracks = getToonTracks(attack, damageDelay=4.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8,
                               dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('cc_s_sfx_ene_hroller_conducktion.ogg', delay=throwDelay, node=suit)
    return Parallel(suitTrack, allDuckTracks, toonTracks, soundTrack)

def doConDuckTionVulnerable(attack):
    suit = attack['suit']
    battle = attack['battle']
    propDelay = 0.6
    throwDelay = 1.67
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doWheelSpinVulnerable(attack))
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
                Func(MovieUtil.removeProp, next)
            )
            duckTracks.append(duckTrack)

        allDuckTracks.append(duckTracks)
    suitTrack.append(Func(suit.makeNonImmortal))
    damageAnims = [['cringe', 0.01, 0.14, 0.21],
                   ['cringe', 0.01, 0.14, 0.13],
                   ['cringe', 0.01, 0.43]]
    toonTracks = getToonTracks(attack, damageDelay=4.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8,
                               dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('cc_s_sfx_ene_hroller_conducktion.ogg', delay=throwDelay, node=suit)
    return Parallel(suitTrack, allDuckTracks, toonTracks, soundTrack)

def doTvBlast(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.8
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'c':
        suitDelay = 1.13
        dodgeDelay = 3.1
    else:
        suitDelay = 1.83
        dodgeDelay = 3.6
    throwDuration = 1.5
    tv = globalPropPool.getProp('modeltv')
    scale = 1.1
    torso = toon.style.torso
    torso = torso[0]
    if torso == 's':
        scaleUpPoint = Point3(scale * 1.23, scale * 1.23, scale * 1.23)
    elif torso == 'm':
        scaleUpPoint = Point3(scale * 1.23, scale * 1.23, scale * 1.23)
    elif torso == 'l':
        scaleUpPoint = Point3(scale * 1.23, scale * 1.23, scale * 1.23)
    tvHpr = VBase3(-173.47, 0, 0)
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.14, 0.15, 0.08), VBase3(-10.584, 11.945, -161.684)]
    throwTrack = Sequence(getPropAppearTrack(tv, suit.getRightHand(), posPoints, propDelay, Point3(6, 6, 6), scaleUpTime=0.5))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, tv))
    throwTrack.append(getThrowTrack(tv, hitPoint, duration=throwDuration, parent=battle))
    if dmg > 0:
        tv2 = MovieUtil.copyProp(tv)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        tv2Point = Point3(hitPoint.getX(), hitPoint.getY() + 6.4, hitPoint.getZ())
        tv2.setPos(tv2Point)
        tv2.setScale(scaleUpPoint)
        tv2.setHpr(tvHpr)
        throwTrack.append(Func(battle.movie.needRestoreHips))
        throwTrack.append(Func(tv.wrtReparentTo, hips1))
        throwTrack.append(Func(tv2.reparentTo, hips2))
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(MovieUtil.removeProp, tv2))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(tv, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(tv, throwDuration, tvHpr))
        soundTrack = Sequence(Wait(2.6), SoundInterval(globalBattleSoundCache.getSound('SA_TV_pie_throw.ogg'), node=suit), Wait(2.4),SoundInterval(globalBattleSoundCache.getSound('SA_TV_crash.ogg'), node=suit))
    else:
        land = toon.getPos(battle)
        land.setZ(land.getZ() + 0.7)
        bouncePoint1 = Point3(land.getX(), land.getY() - 1.5, land.getZ() + 2.5)
        bouncePoint2 = Point3(land.getX(), land.getY() - 2.1, land.getZ() - 0.2)
        bouncePoint3 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 1.5)
        bouncePoint4 = Point3(land.getX(), land.getY() - 4.1, land.getZ() + 0.3)
        throwTrack.append(LerpPosInterval(tv, 0.4, land))
        throwTrack.append(LerpPosInterval(tv, 0.4, bouncePoint1))
        throwTrack.append(LerpPosInterval(tv, 0.3, bouncePoint2))
        throwTrack.append(LerpPosInterval(tv, 0.3, bouncePoint3))
        throwTrack.append(LerpPosInterval(tv, 0.3, bouncePoint4))
        throwTrack.append(Wait(1.1))
        throwTrack.append(LerpScaleInterval(tv, 0.3, MovieUtil.PNT3_NEARZERO))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(tv, throwDuration, Point3(1.8, 1.8, 1.8)))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(tv, throwDuration, tvHpr), Wait(0.4), LerpHprInterval(tv, 0.4, Point3(83.27, 0, 0)), LerpHprInterval(tv, 0.3, Point3(95.24, 0, 0)), LerpHprInterval(tv, 0.2, Point3(-96.34, 0, 0)))
        soundTrack = getSoundTrack('SA_TV_pie_throw.ogg', delay=2.6, node=suit)
    tvTrack = Sequence(Parallel(throwTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, tv), Func(battle.movie.clearRenderProp, tv))
    damageAnims = [['think',
      propDelay + suitDelay + throwDuration,
      0.01,
      0.7], ['cringe', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['shrug'], showDamageExtraTime=propDelay + suitDelay + 2.4)
    return Parallel(suitTrack, toonTrack, tvTrack, soundTrack)

def doOilRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0.2
    damageDelay = 3.5
    dodgeDelay = 2.45
    taunt = random.choice(
        ["Does this remind you of anyone?", "You Toons are real roustabouts."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'magic3', playRate=1.25),
                     Func(suit.setNeutralAnimation))
    ceaseTrack = Parallel(Func(suit.makeOilRain), ActorInterval(suit, 'transformation'))
    ceaseTrack.append(Func(suit.showHpString, "OIL RAIN!"))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                      random.choice(("Does this remind you of anyone?",
                                                     "You Toons are real roustabouts.")),
                                      CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSpeechTrack))
    for suit in battle.activeSuits:
        suitTrack.append(Func(suit.makeInsured))
    suitTrack.append(Sequence(Func(suit.setNeutralAnimation)))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    for t in attack['target']:
        toon = t['toon']
        rainEffect = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
        effectColor = Vec4(0.00, 1.00, 0.00, 1.00) if attack['id'] == ACID_RAIN else Vec4(0.00, 0.00, 0.00, 1.00)
        BattleParticles.setEffectTexture(rainEffect, 'raindrop', color=effectColor)
        BattleParticles.setEffectTexture(rainEffect2, 'raindrop', color=effectColor)
        BattleParticles.setEffectTexture(rainEffect3, 'raindrop', color=effectColor)
        cloud = globalPropPool.getProp('stormcloud')
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack = Sequence(
            Func(cloud.pose, 'stormcloud', 0),
            getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25),
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
        if t['hp'] != 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 1.0, 0.0, 1) if attack['id'] == ACID_RAIN else Vec4(0.0, 0.0, 0.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(
                Func(battle.movie.needRestoreRenderProp, puddle),
                Wait(damageDelay - 0.7),
                Func(puddle.reparentTo, battle),
                Func(puddle.setPos, toon.getPos(battle)),
                LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO),
                Wait(3.2),
                LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8),
                Func(MovieUtil.removeProp, puddle),
                Func(battle.movie.clearRenderProp, puddle)
            )
            puddleTracks.append(puddleTrack)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack1, puddleTracks)

def doOilRainDerrickHand(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0.2
    damageDelay = 3.5
    dodgeDelay = 2.45
    taunt = random.choice(
        ["Does this remind you of anyone?", "You Toons are real roustabouts."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'magic3', playRate=1.25),
                     Func(suit.setNeutralAnimation))
    ceaseTrack = Func(suit.setHealthForMe, - suit.currHP)
    ceaseSpeechTrack = Parallel( ActorInterval(suit, 'finger-wag'), Func(suit.setChatAbsolute,
                                      "I've had enough of this nonsense. You Toons have pushed me over the edge.",
                                      CFSpeech | CFTimeout))
    suitTrack.append(Wait(2.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSpeechTrack))
    suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
    suitTrack.append(Func(suit.setChatAbsolute,
                                      "Let's see how much power you really have, Toons.",
                                      CFSpeech | CFTimeout))
    suitTrack.append(Sequence(Func(suit.setNeutralAnimation)))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    for t in attack['target']:
        toon = t['toon']
        rainEffect = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
        effectColor = Vec4(0.00, 1.00, 0.00, 1.00) if attack['id'] == ACID_RAIN else Vec4(0.00, 0.00, 0.00, 1.00)
        BattleParticles.setEffectTexture(rainEffect, 'raindrop', color=effectColor)
        BattleParticles.setEffectTexture(rainEffect2, 'raindrop', color=effectColor)
        BattleParticles.setEffectTexture(rainEffect3, 'raindrop', color=effectColor)
        cloud = globalPropPool.getProp('stormcloud')
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack = Sequence(
            Func(cloud.pose, 'stormcloud', 0),
            getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25),
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
        if t['hp'] != 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.0, 1.0, 0.0, 1) if attack['id'] == ACID_RAIN else Vec4(0.0, 0.0, 0.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(
                Func(battle.movie.needRestoreRenderProp, puddle),
                Wait(damageDelay - 0.7),
                Func(puddle.reparentTo, battle),
                Func(puddle.setPos, toon.getPos(battle)),
                LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO),
                Wait(3.2),
                LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8),
                Func(MovieUtil.removeProp, puddle),
                Func(battle.movie.clearRenderProp, puddle)
            )
            puddleTracks.append(puddleTrack)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, soundTrack1, puddleTracks)

def doRolledTrickOfTheLight(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0.2
    damageDelay = 1.5
    dodgeDelay = 1.45
    taunt = getAttackTaunt('SwirlBath', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'magic3', playRate=1.25))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doWheelSpinTrickOfTheLight(attack))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    for t in attack['target']:
        toon = t['toon']
        sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
        sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
        spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
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
        #cloud = globalPropPool.getProp('stormcloud')
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack = Parallel(Sequence(getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0]), Wait(.1),
                Sequence(getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0]), Wait(.1),
                Sequence(getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])))))
        cloudPropTracks.append(cloudPropTrack)
        cloudPropTracks.append(sprayTrack)
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)),
                                 LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)),
                                 LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)),
                                 LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)),
                                 LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)),
                                 LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        toonTracks.append(toonSpinTrack)
    soundTrack = getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit)
    return Parallel(suitTrack, toonTracks, tauntInterval, soundTrack)

def doRolled(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0.2
    damageDelay = 1.5
    dodgeDelay = 1.45
    taunt = getAttackTaunt('SwirlBath', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'magic3', playRate=1.25))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doWheelSpinPhase3(attack))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTracks = Parallel(getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep']))
    for t in attack['target']:
        toon = t['toon']
        sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
        sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
        spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
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
        spinTrack1 = getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0])
        spinTrack2 = getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0])
        spinTrack3 = getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])
        #cloud = globalPropPool.getProp('stormcloud')
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
        cloudPropTrack = Parallel(Sequence(getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0]), Wait(.1),
                Sequence(getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0]), Wait(.1),
                Sequence(getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])))))
        cloudPropTracks.append(cloudPropTrack)
        cloudPropTracks.append(sprayTrack)
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)),
                                 LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)),
                                 LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)),
                                 LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)),
                                 LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)),
                                 LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        toonTracks.append(toonSpinTrack)
    soundTrack = getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit)
    return Parallel(suitTrack, toonTracks, tauntInterval, soundTrack)

def doHeavyRain2(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    partDelay = 0.2
    damageDelay = 3.5
    dodgeDelay = 2.45
    dmg = (attack['target'][0]['hp']) * len(battle.activeToons)
    taunt = random.choice(
        ["Water, water, everywhere!", "I'm not crying, you're crying!",
         "I think this is called 'delayed physical aggression.'", "I'm only going to hit back as hard as you do!'",
         "I can weather the storm, Toons.",
         "I heard you Toons like roughhousing, can I play too?",
         "If I can't make you like me, then I can at least make you fear me!"])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'magic3', playRate=1.25), Func(suit.setNeutralAnimation))
    ceaseTrack = Parallel(Func(suit.makeHeavyRain), ActorInterval(suit, 'transformation'))
    ceaseTrack.append(Func(suit.showHpString, "HEAVY RAIN!"))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     random.choice(("Water, water, everywhere!", "I'm not crying, you're crying!",
         "I think this is called 'delayed physical aggression.'", "I'm only going to hit back as hard as you do!'",
         "I can weather the storm, Toons.",
         "I heard you Toons like roughhousing, can I play too?",
         "If I can't make you like me, then I can at least make you fear me!")),
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSpeechTrack))
    for suit in battle.activeSuits:
        suitTrack.append(Func(suit.removeInsured))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTracks = Parallel()
    puddleTracks = Parallel()
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    for t in attack['target']:
        toon = t['toon']
        rainEffect = BattleParticles.createParticleEffect(file='liquidate2')
        rainEffect2 = BattleParticles.createParticleEffect(file='liquidate2')
        rainEffect3 = BattleParticles.createParticleEffect(file='liquidate2')
        effectColor = Vec4(0.00, 1.00, 1.00, 1.00) #if attack['id'] == ACID_RAIN else Vec4(0.00, 0.00, 0.00, 1.00)
        BattleParticles.setEffectTexture(rainEffect, 'raindrop', color=effectColor)
        BattleParticles.setEffectTexture(rainEffect2, 'raindrop', color=effectColor)
        BattleParticles.setEffectTexture(rainEffect3, 'raindrop', color=effectColor)
        cloud = globalPropPool.getProp('stormcloud')
        targetPoint = __toonFacePoint(toon)
        targetPoint.setZ(targetPoint[2] + 3)
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
        if t['hp'] != 0:
            puddle = globalPropPool.getProp('quicksand')
            puddle.setColor(Vec4(0.00, 0.00, 0.00, 1.00)) #if attack['id'] == ACID_RAIN else Vec4(0.0, 0.0, 0.0, 1))
            puddle.setHpr(Point3(120, 0, 0))
            puddle.setScale(0.01)
            puddleTrack = Sequence(
                Func(battle.movie.needRestoreRenderProp, puddle),
                Wait(damageDelay - 0.7),
                Func(puddle.reparentTo, battle),
                Func(puddle.setPos, toon.getPos(battle)),
                LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO),
                Wait(3.2),
                LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8),
                Func(MovieUtil.removeProp, puddle),
                Func(battle.movie.clearRenderProp, puddle)
            )
            puddleTracks.append(puddleTrack)
    #animTrack = Sequence(Wait(2), Func(suit.play, 'cease'))
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    soundTrack = Parallel(soundTrack1)
    makeUnFrozen = Func(suit.makeUnFrozen)
    return Parallel(suitTrack, toonTracks, cloudPropTracks, makeUnFrozen, soundTrack, puddleTracks)

def doEmbezzle(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    bill = loader.loadModel('phase_3.5/models/props/jellybean4')
    bill.setH(0)
    bill.setColor(1,0.9,0)
    glow = loader.loadModel("phase_3.5/models/props/glow.bam")
    glow.reparentTo(bill)
    glow.setScale(0.5)
    glow.setPos(0,0,0)
    glow.setColorScale(Vec4(1, 0.9, 0, 0.3))
    suitTrack = getSuitTrack(attack)
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(5.0, 5.0, 5.0))
    toonTrack = getToonTrack(attack, 0.6, ['cringe'], 0.01, ['sidestep'])
    glowTrack = Sequence()
    glowTrack.append(Wait(4.0))
    glowTrack.append(Func(glow.hide))
    multiTrackList = Parallel(suitTrack, toonTrack, glowTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doFloodTheMarket(attack):
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
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 7s gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
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

def doFloodTheMarketPeckingGroup(attack):
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
    taunt = getAttackTaunt('FloodTheMarket', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'magic3'))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(3.0))
        suitTrack.append(doPeckingOrderVulnerabilityGroup(attack))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
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

def doStockCosts(attack):
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
    taunt = random.choice(
        ["You won't survive the stock market crash, Toons.", "Investing in the stock market doesn't always pay off, does it?",
         "Hold your breath, you're about to drown in debt."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'magic3'))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 and 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    partTrack = getPartTrack(particleEffect, 1.0, 1.9, [particleEffect, suit, 0])
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 1.9, [waterfallEffect, suit, 0])
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


def doWhitePowder(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.0))
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Func(battle.unlureSuit, suit))
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpText, 0))
        elif suit.currHP + 100 > (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpTextCheat, x))
            suitTrack.append(Func(suit.showHpString, "BELLOW!"))
            suitTrack.append(Func(suit.setHealthForMe, + x))
        else:
            suitTrack.append(Func(suit.showHpTextCheat, 100))
            suitTrack.append(Func(suit.showHpString, "BELLOW!"))
            suitTrack.append(Func(suit.setHealthForMe,  + 100))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(resetTrack)
        if not suit.dna.name == 'lit':
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitBellowPhrases), CFSpeech | CFTimeout))
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ActorInterval(suit, 'soak', startTime=3.5), __soakRemoval(suit, 1)))
        suitTrack.append(
            Func(suit.setNeutralAnimation))
        suitTracks.append(MovieUtil.createSuitBellowInterval(theSuit))
        suitTracks.append(Wait(4.0))
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.setNeutralAnimation))
    soundTrack = getSoundTrack('SA_bellow.ogg', delay=0.1, node=suit)
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTracks, healSound, soundTrack)

def __soakRemoval(suit, remove=0):
    if remove:
        if suit.style.name == 'jl':
            color = Point4((0.729, 0.729, 0.729, 1))
        elif suit.style.name == 'lbs':
            color = Point4((0.51, 0.49, 0.467, 1))
        elif suit.style.name == 'fb':
            color = Point4((0.6, 0.6, 0.6, 1))
        elif suit.style.name == 'tcc':
            color = Point4((0.671, 0.671, 0.671, 1))
        elif suit.style.name == 'gb':
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
    if suit.style.name == 'lit' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryLitigator))
    for bodyPart in suitBody:
        if bodyPart:
            suitInterval.append(Func(bodyPart.setColor, color))
        return suitInterval

def doMobMentality(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitTrack(attack)
        suitTrack.append(Func(suit.play, 'mob-mentality'))
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Wait(3.0))
        suitTrack.append(Func(suit.play,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        for headPart in suit.animatedHeadParts:
            suitTrack.append(Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
            suit.setHealthForMe(int(suit.currHP + 0))
            suitTrack.append(Func(suit.showHpText, 0))
        elif suit.currHP + 100 > (suit.maxHP * suit.hardMaxHP):
            suit.setHealthForMe(int(suit.currHP + x))
            suitTrack.append(Func(suit.showHpText, x))
        else:
            suit.setHealthForMe(int(suit.currHP + 100))
            suitTrack.append(Func(suit.showHpText, 100))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(resetTrack)
        suitTrack.append(
            Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout))
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('SA_mob_mentality.ogg', node=suit)
    healSound = Sequence(Wait(6.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTracks, healSound, soundTrack)

def doGoodMorningToontown(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitTrack(attack)
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(resetTrack)
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.setNeutralAnimation))
        for headPart in suit.animatedHeadParts:
            if suit.style.name == 'crf':
                suitTracks.append(Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''), fromFrame=0, toFrame=22))
            elif suit.style.name == 'mad':
                suitTracks.append(Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''), fromFrame=0, toFrame=22))
            else:
                suitTracks.append(Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('cc_s_dlg_ene_hroller_good_morning_clash_general.ogg', node=suit)
    return Parallel(suitTracks, soundTrack)

def doCeaseAndDesist(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitTrack(attack)
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Func(battle.unlureSuit, suit))
        for headPart in suit.animatedHeadParts:
            suitTrack.append(Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        suitTrack.append(resetTrack)
        suitTracks.append(suitTrack)
        suitTracks.append(Func(suit.loop,  'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('SA_insurance.ogg', node=suit)
    return Parallel(suitTracks, soundTrack)

def doPeckingOrderSlushFund(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    throwDuration = 3.03
    throwDelay = 2
    taunt = getAttackTaunt('PeckingOrder', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'throw-object', playRate=1.5))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(3.0))
        suitTrack.append(doSlushFundReal(attack))
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    propDelay = 1.5
    for i in xrange(0, numBirds):
        next = globalPropPool.getProp('bird')
        next.setScale(0.01)
        next.reparentTo(suit.getRightHand())
        next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
        if dmg > 0:
            # hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6, random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        else:
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        birdTrack = Sequence(Wait(throwDelay), Func(battle.movie.needRestoreRenderProp, next), Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)), LerpPosInterval(next, 0.5, hitPoint))
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.1, Point3(9, 9, 9)))
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
    toonTrack = getToonTrack(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, birdTracks)

def doHypnoEyes(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[ind]
    damageDelay = 1.7
    taunt = random.choice(
        ["You've earned a bonus, keep up the great work.",
         "You've done great work today. Here's a raise."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
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
    spinEffect1.wrtReparentTo(battle)
    spinEffect2.wrtReparentTo(battle)
    spinEffect3.wrtReparentTo(battle)
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
    headsUp2 = Func(suit.headsUp, battle, targetPos2)
    moveTrack = Sequence(LerpPosInterval(suit, 1.5, sinkPos2, other=battle), Wait(3.2), LerpPosInterval(suit, 1.5, dropPos, other=battle), Func(suit.setPos, battle, dropPos))
    suitTrack = Sequence(ActorInterval(suit, 'walk'), tauntInterval, headsUp, ActorInterval(suit, 'mob-mentality'), ActorInterval(suit, 'walk'), headsUp2, Func(suit.setNeutralAnimation))
    sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0])
    spinTrack1 = getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0])
    spinTrack2 = getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0])
    spinTrack3 = getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    x = int((targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP)
    selfDamageTrack = Sequence(Wait(5.7), Parallel(ActorInterval(targetSuit, 'slip-forward', startTime=2.43),
                                                   Func(targetSuit.makeIntoCTSManager),
                                                   Func(targetSuit.showHpString, "PROMOTION!"),
                                                   Func(targetSuit.setMaxHP, 1000),
                                                   Func(targetSuit.setHP, 1000), Func(targetSuit.setManager, 1),
                                                   Func(targetSuit.updateHealthBar, 0)),
                               Func(targetSuit.setNeutralAnimation))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    #toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTrack = getSoundTrack('TL_hypnotize.ogg', delay=4.0, node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=5.7, node=suit)
    #toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
    return Parallel(suitTrack, sprayTrack, moveTrack, selfDamageTrack, soundTrack2, soundTrack, spinTrack1, spinTrack2, spinTrack3)

def doReprogram(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 30.5)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos2 = toon.getPos(battle)
    headsUp2 = Func(suit.setHpr, battle, origHpr)
    moveTrack = Sequence(LerpPosInterval(suit, 2.75, sinkPos2, other=battle), Func(suit.setPos, battle, dropPos))
    suitTrack = Sequence(tauntInterval, headsUp, ActorInterval(suit, 'walk'), ActorInterval(suit, 'walk'), headsUp2, Func(suit.setNeutralAnimation))
    damageAnims = []
    damageAnims.append(['cringe'])
    toonTrack = getToonTrack(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, moveTrack, toonTrack)

def doSlushFundReal(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.7
    taunt = random.choice(
        ["Do I gotta provide the muscle for you?!", "Consider this your share for this operation.", "I said I wouldn't let anyone mess with you, didn't I?!",
         "C'mon you useless hunks of junk, keep yourselves together!"])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'mob-mentality'))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 7 and 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    sprayTracks = Parallel()
    selfDamageTracks = Parallel()
    spinTrack1s = Parallel()
    spinTrack2s = Parallel()
    spinTrack3s = Parallel()
    for targetSuit in battle.activeSuits:
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
        spinEffect1.wrtReparentTo(battle)
        spinEffect2.wrtReparentTo(battle)
        spinEffect3.wrtReparentTo(battle)
        sprayTrack = getPartTrack(sprayEffect, 0, 0, [sprayEffect, targetSuit, 0])
        spinTrack1 = getPartTrack(spinEffect1, 0.1, 3.9, [spinEffect1, battle, 0])
        spinTrack2 = getPartTrack(spinEffect2, 0.1, 3.9, [spinEffect2, battle, 0])
        spinTrack3 = getPartTrack(spinEffect3, 0.1, 3.9, [spinEffect3, battle, 0])
        x = int((targetSuit.maxHP * targetSuit.hardMaxHP) - targetSuit.currHP)
        if targetSuit.dna.name == 'dvk':
            selfDamageTrack = Sequence(Wait(2), Func(targetSuit.showHpTextCheat, + 100), Func(targetSuit.showHpString, "SLUSH FUNDED!"), Func(targetSuit.setHealthForMe, 100),
                                       Func(targetSuit.updateHealthBar, 0))
        elif targetSuit.currHP + 100 > (targetSuit.maxHP * targetSuit.hardMaxHP):
            selfDamageTrack = Sequence(Wait(2), Func(targetSuit.setChatAbsolute,
                                                     random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                                     CFSpeech | CFTimeout), Func(targetSuit.showHpTextCheat, + x), Func(targetSuit.showHpString, "SLUSH FUNDED!"), Func(targetSuit.setHealthForMe, x),
                                       Func(targetSuit.updateHealthBar, 0))
        else:
            selfDamageTrack = Sequence(Wait(2), Func(targetSuit.setChatAbsolute,
                                                       random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                                       CFSpeech | CFTimeout), Func(targetSuit.showHpTextCheat, + 100),
                                       Func(targetSuit.showHpString, "SLUSH FUNDED!"), Func(targetSuit.setHealthForMe, 100),
                                       Func(targetSuit.updateHealthBar, 0))
        selfDamageTracks.append(selfDamageTrack)
        spinTrack1s.append(spinTrack1)
        spinTrack2s.append(spinTrack2)
        spinTrack3s.append(spinTrack3)
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    #toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTrack = getSoundTrack('TL_hypnotize.ogg', node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=2, node=suit)
    #toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
    return Parallel(suitTrack, sprayTracks, selfDamageTracks, soundTrack2, soundTrack, spinTrack1s, spinTrack2s, spinTrack3s)



def doBlast(attack):
    suit = attack['suit']
    battle = attack['battle']
    leftKnives = []
    rightKnives = []
    explode = []
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))
        explode.append(globalPropPool.getProp('explosion'))
        cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.2, pos=Point3(8, 11, 5), hpr=Point3(150, 0, 0),
                                                  blendType='easeInOut'))

    suitTrack = getSuitAnimTrack(attack)
    suitName = suit.getStyleName()
    leftPosPoints = [Point3(0.4, 10, 3.2), MovieUtil.PNT3_ZERO]
    rightPosPoints = [Point3(-0.4, 10, 3.2), MovieUtil.PNT3_ZERO]
    explodePosPoints = [Point3(0, 10, 1), MovieUtil.PNT3_ZERO]
    leftPosPoints1 = [Point3(0.4, 10, 3.2), MovieUtil.PNT3_ZERO]
    rightPosPoints1 = [Point3(-0.4, 10, 3.2), MovieUtil.PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 10, 1), MovieUtil.PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), MovieUtil.PNT3_ZERO]
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    explodeTracks = Parallel()
    explosionTrack = Sequence()
    explosionTrack.append(Wait(1.5))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(1.1, 1.1, 1.1), scaleUpTime=0.1))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.1, 0.1, 0.1), scaleUpTime=0.1))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        rightKnifeTracks.append(rightTrack)
        explodeTrack = Sequence()
        explodeTrack.append(Wait(1.6))
        explodeTrack.append(getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTracks = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack1 = Sequence(Wait(0),SoundInterval(globalBattleSoundCache.getSound('SA_bash.ogg'), node=suit))
    soundTrack2 = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_blast.ogg'), node=suit))
    soundTrack = Parallel(soundTrack1, soundTrack2)
    suitTrack.append(Wait(3))
    suitTrack.append(doBlastShield(attack))
    return Parallel(cameraTrack, suitTrack, toonTracks, soundTrack, leftKnifeTracks, rightKnifeTracks, explodeTracks, explosionTrack)

def doBlastShield(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeShielding)
    makeUnShielding = Func(suit.makeUnSoakResistant)
    makeUnShielding2 = Func(suit.makeUnSyphon)
    makeUnShielding3 = Func(suit.makeUnLureImmune)
    shieldSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     random.choice(("I can't stand seeing the rest of my allies getting hurt.",
                                                    "Don't worry, I got your back.", "Woah, you didn't think we were going down that easily did you?")),
                                     CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(attack['suit'], 'defense' ))
    suitTrack.append(Wait(3.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, makeShielding, makeUnShielding3, makeUnShielding, makeUnShielding2, shieldSpeechTrack)

def doSoakResist(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeSoakResistant)
    makeUnShielding = Func(suit.makeUnSyphon)
    makeUnShielding2 = Func(suit.makeUnShielding)
    makeUnShielding3 = Func(suit.makeUnLureImmune)
    shieldSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     random.choice(("I just bought this suit. Please don't get it wet.",
                                                    "I am not in the mood for a seltzer at the moment.")),
                                     CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(attack['suit'], 'squirt-small-react', startTime=2))
    suitTrack.append(Wait(3.0))
    return Parallel(suitTrack, makeShielding, makeUnShielding2, makeUnShielding3, makeUnShielding, shieldSpeechTrack)

def doLureResist(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeUnSoakResistant)
    makeUnShielding = Func(suit.makeUnSyphon)
    makeUnShielding2 = Func(suit.makeUnShielding)
    makeUnShielding3 = Func(suit.makeLureImmune)
    shieldSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     random.choice(("I will not fall for your mind tricks this time, Toons.",
                                                    "There's no such thing as 'free money' in today's world.")),
                                     CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(attack['suit'], 'rake-react'))
    suitTrack.append(Wait(3.0))
    return Parallel(suitTrack, makeShielding, makeUnShielding2, makeUnShielding3, makeUnShielding, shieldSpeechTrack)

def doSyphon(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeUnSoakResistant)
    makeUnShielding = Func(suit.makeSyphon)
    makeUnShielding2 = Func(suit.makeUnShielding)
    makeUnShielding3 = Func(suit.makeUnLureImmune)
    shieldSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     random.choice(("You're health is mine.",
                                                    "You hit me, I hit you back even harder.", "I'm not ready to give up quite yet.")),
                                     CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(attack['suit'], 'summon'))
    suitTrack.append(Wait(3.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, makeShielding, soundTrack, makeUnShielding3, makeUnShielding2, makeUnShielding, shieldSpeechTrack)

def doBlackOrb(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    eye = globalPropPool.getProp('black-orb')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    if suitName == 'cr':
        posPoints = [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'tf':
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'le':
        posPoints = [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    else:
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    eyeHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['effort',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('effort', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['effort', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)), Wait(eyeHoldDuration * 0.3), LerpHprInterval(eye, 0.02, Point3(205, 40, 0)), Wait(eyeHoldDuration * 0.7), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle))
    toonFace = __toonFacePoint(toon, parent=battle)
    if dmg > 0:
        lerpInterval = LerpPosInterval(eye, moveDuration, toonFace)
    else:
        lerpInterval = LerpPosInterval(eye, moveDuration, Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
    eyeMoveTrack = lerpInterval
    eyeRollTrack = LerpHprInterval(eye, moveDuration, Point3(0, 0, -180))
    eyePropTrack = Sequence(eyeAppearTrack, Parallel(eyeMoveTrack, eyeRollTrack), Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['slip-backward', 0.01, 0.3]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_magic_orb.ogg', delay=0.5, node=suit)
    return Parallel(suitTrack, toonTrack, eyePropTrack, soundTrack)


def doRevvingUp(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    sanctioned = __makeSanctionedNodePath()
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 0.6),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0.81, -1.11, -0.16, 0, 85, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint]),
        Func(MovieUtil.removeProp, sanctioned),
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Parallel(Sequence(Wait(1.0),  Func(suit.setChatAbsolute,
                                   "OFFENSIVE ANOMALY HAS BEEN DETECTED, PUNISHING FROM POINT OF GREATEST RESISTANCE, THREATS HAVE BEGUN TO REPAIR THEMSELVES. TARGETING LARGEST THREAT.",
                                   CFSpeech | CFTimeout),
                              Sequence(Wait(2.5)))))
    soundTrack = getSoundTrack('SA_revving_up.ogg', node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doBreachOfContract(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = __makeBreachNodePath()
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
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], - int(dmg / 2.2), 0.8, ['conked'])
    # toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    taunt = random.choice(
        ["Someone isn't doing their part around here.", "This company will not tolerate any breach of contract, you will be punished.",
         "Your contract has been breached, now suffer the consequence!", "What happened to your little strategy called 'teamwork'?",])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'sanction'), suitReset, Func(suit.setNeutralAnimation))
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextCheat, - int(dmg / 2.2)), Func(toon.showHpString, "BREACHED!"))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)


def doDenialOfService(attack):
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
        Func(sanctioned.setScale, 2),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 80, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [missPoint], .25),
        Func(MovieUtil.removeProp, sanctioned),
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    # toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    taunt = random.choice(
        ["Someone isn't doing their part around here.", "This company will not tolerate any breach of contract, you will be punished.",
         "Your contract has been breached, now suffer the consequence!", "What happened to your little strategy called 'teamwork'?",])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doBreachOfContractSoaked(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = __makeBreachNodePath()
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
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], - int(dmg / 2.2), 0.8, ['conked'])
    # toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    taunt = random.choice(
        ["Someone isn't doing their part around here.",
         "Joining a union will result in a breach in your contract, this will not be tolerated.",
         "No unions will be formed under my watch.",
         "This company will not tolerate any breach of contract, you will be punished.",
         "Your contract has been breached, now suffer the consequence!",
         "What happened to your little strategy called 'teamwork'?", ])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'sanction'), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrackCease =  Parallel(Func(suit.setChatAbsolute,
                                    'Quality Control dictates that all Zap and Sound gags are now classified as defective.',
                                   CFSpeech | CFTimeout), ActorInterval(suit, 'cease'), getSoundTrack('SA_cease_and_desist.ogg', node=suit))
    suitTrack.append(suitTrackCease)
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextCheat, - int(dmg / 2.2)), Func(toon.showHpString, "BREACHED!"))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doBreachOfContractMarked(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = __makeBreachNodePath()
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
        Func(battle.movie.clearRenderProp, sanctioned)
    )
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], - int(dmg / 2.2), 0.8, ['conked'])
    # toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    taunt = random.choice(
        ["Someone isn't doing their part around here.",
         "Joining a union will result in a breach in your contract, this will not be tolerated.",
         "No unions will be formed under my watch.",
         "This company will not tolerate any breach of contract, you will be punished.",
         "Your contract has been breached, now suffer the consequence!",
         "What happened to your little strategy called 'teamwork'?", ])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'sanction'), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrackCease =  Parallel(Func(suit.setChatAbsolute,
                                   'Quality Control dictates that all Throw and Zap gags are now classified as defective.',
                                   CFSpeech | CFTimeout), ActorInterval(suit, 'cease'), getSoundTrack('SA_cease_and_desist.ogg', node=suit))
    suitTrack.append(suitTrackCease)
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextCheat, - int(dmg / 2.2)), Func(toon.showHpString, "BREACHED!"))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)


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
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], - int(dmg / 2.2), 0.8, ['conked'])
    # toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(3.0))
    suitTrackCease =  Parallel(Func(suit.setChatAbsolute,
                                   "Any Level 5 and 8 Gags Toons use can and will be held against them in a court of law.",
                                   CFSpeech | CFTimeout), ActorInterval(suit, 'cease'), getSoundTrack('SA_cease_and_desist.ogg', node=suit))
    suitTrack.append(suitTrackCease)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextCheat, - int(dmg / 2.2)), Func(toon.showHpString, "SANCTIONED!"))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doCourtSanction2(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
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
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], - int(dmg / 2.2), 0.8, ['conked'])
    #toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    suitTrack = getSuitTrack(attack)
    suitTrack.append(Wait(3.0))
    suitTrackCease =  Parallel(Func(suit.setChatAbsolute,
                                   "Any Level 6 and 7 Gags Toons use can and will be held against them in a court of law.",
                                   CFSpeech | CFTimeout), ActorInterval(suit, 'cease'), getSoundTrack('SA_cease_and_desist.ogg', node=suit))
    suitTrackCease2 = Parallel(Func(suit.setChatAbsolute,
                                   "Any Level 5 and 6 Gags Toons use can and will be held against them in a court of law.",
                                   CFSpeech | CFTimeout), ActorInterval(suit, 'cease'),
                              getSoundTrack('SA_cease_and_desist.ogg', node=suit))
    if name == CEASE_AND_DESIST:
        suitTrack.append(suitTrackCease2)
    else:
        suitTrack.append(suitTrackCease)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextCheat, - int(dmg / 2.2)), Func(toon.showHpString, "SANCTIONED!"))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doCourtSanctionBindings(attack):
    suit = attack['suit']
    battle = attack['battle']
    for s in battle.activeSuits:
        if s.dna.name == 'ste':
            theSuit = s
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
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], - int(dmg / 2.38), 0.8, ['conked'])
    # toonTrack = getToonTrack(attack, 0.8, ['conked'], 0.2, ['sidestep'])
    taunt = getAttackTaunt('CourtSanction', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'sanction'), suitReset, Func(suit.setNeutralAnimation))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Trap and Sound Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(2.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextCheat, - int(dmg / 2.38)), Func(toon.showHpString, "SANCTIONED!"))
    return Parallel(suitTrack, toonTrack, tauntInterval, propTrack, soundTrack, notifyTrack)

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

def __makeBreachNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText('BREACHED\nBREACHED\nBREACHED')
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

def doJargonSanction(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect2 = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect3 = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect4 = BattleParticles.createParticleEffect(file='jargonSpray')
    BattleParticles.setEffectTexture(particleEffect, 'jargon-brow', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'jargon-deep', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect3, 'jargon-hoop', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect4, 'jargon-ipo', color=Vec4(0, 0, 0, 1))
    damageDelay = 1
    dodgeDelay = 0.9
    partDelay = 0.25
    partInterval = 1
    taunt = getAttackTaunt('Jargon', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'speak', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.0))
    suitTrack.append(doCourtSanction(attack))
    partTrack = getPartTrack(particleEffect, partDelay + partInterval * 0, 2, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay + partInterval * 1, 2, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, partDelay + partInterval * 2, 2, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, partDelay + partInterval * 3, 1.0, [particleEffect4, suit, 0])
    damageAnims = []
    damageAnims.append(['conked',
                        0.0001,
                        0,
                        0.4])
    damageAnims.append(['conked',
                        0.0001,
                        0.7,
                        0.85])
    damageAnims.append(['conked',
                        0.0001,
                        0.4,
                        0.09])
    damageAnims.append(['conked',
                        0.0001,
                        0.4,
                        0.09])
    damageAnims.append(['conked',
                        0.0001,
                        0.4,
                        0.66])
    damageAnims.append(['conked',
                        0.0001,
                        0.4,
                        0.09])
    damageAnims.append(['conked',
                        0.0001,
                        0.4,
                        0.09])
    damageAnims.append(['conked',
                        0.0001,
                        0.4,
                        0.86])
    damageAnims.append(['conked', 0.0001, 0.4])
    dodgeAnims = [['duck', 0.0001, 1.2], ['duck', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=0.7)
    soundTrack = getSoundTrack('SA_jargon.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, partTrack, tauntInterval, partTrack2, partTrack3, partTrack4)


def doMumboJumboSanction(attack):
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
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='mumboJumboSpray')
    particleEffect2 = BattleParticles.createParticleEffect(file='mumboJumboSpray')
    particleEffect3 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    particleEffect4 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    particleEffect5 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    BattleParticles.setEffectTexture(particleEffect, 'mumbojumbo-boiler', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'mumbojumbo-creative', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect3, 'mumbojumbo-deben', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect4, 'mumbojumbo-high', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect5, 'mumbojumbo-iron', color=Vec4(1, 0, 0, 1))
    taunt = getAttackTaunt('MumboJumbo', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'speak', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.0))
    suitTrack.append(doCourtSanction2(attack))
    partTrack = getPartTrack(particleEffect, 1.5, 2, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 1.5, 2, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 2.25, 1.7, [particleEffect3, toon, 0])
    partTrack4 = getPartTrack(particleEffect4, 2.25, 1.7, [particleEffect4, toon, 0])
    partTrack5 = getPartTrack(particleEffect5, 2.25, 1.7, [particleEffect5, toon, 0])
    toonTrack = getToonTrack(attack, 1.5, ['cringe'], 1.6, ['sidestep'])
    soundTrack = getSoundTrack('SA_mumbo_jumbo.ogg', delay=1.5, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, tauntInterval, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, tauntInterval, partTrack, partTrack2)

def doLifeInsurance(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    suitTrack = getSuitTrack(attack)
    soundTrack1 = getSoundTrack('SA_life_insurance_register.ogg', delay=0.2, node=suit)
    soundTrack2 = getSoundTrack('SA_life_insurance_loop.ogg', delay=1.7, node=suit)
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, +75), Func(suit.setHealthForMe, 75), Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, soundTrack1, soundTrack2, selfDamageTrack)

def doWorkersCompensation(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, +50), Func(suit.setHealthForMe, 50), Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, soundTrack, selfDamageTrack)

def doWorkersCompensation2(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    targetSuit = battle.activeSuits[ind]
    suitTrack = Sequence(ActorInterval(suit, 'frustrated'), Func(suit.setNeutralAnimation))
    speechTrack = Func(suit.setChatAbsolute, "Do you have any idea how much paperwork I will have to file after this?", CFSpeech | CFTimeout)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)
    makeImmune = Func(suit.makeDamageUp)
    selfDamageTrack = Func(suit.showHpText, "1.1x DMG MULTIPLIER!", 2, openEnded=0)
    managerHealTrack = Sequence(Wait(2), Func(suit.showHpTextCheat, + targetSuit.currHP), Func(suit.showHpString, "1.1x DMG MULTIPLIER!"), Func(suit.setHealthForMe, + int(targetSuit.currHP)), Func(suit.updateHealthBar, 0))
    return Parallel(suitTrack, soundTrack, speechTrack, managerHealTrack, makeImmune)

def doWorkersCompensation3(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    targetSuit = battle.activeSuits[ind]
    suitTrack = Sequence(ActorInterval(suit, 'frustrated'), Func(suit.setNeutralAnimation))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)
    makeImmune = Func(suit.makeDamageUp)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Toon-Up and Trap gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    ceaseTrack2 = ActorInterval(suit, 'cease')
    ceaseSoundTrack2 = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Toon-Up and Squirt gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    ceaseTrack3 = ActorInterval(suit, 'cease')
    ceaseSoundTrack3 = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack3 = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Lure and Drop gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if name == UNION_BUST:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    elif name == UNION_BUST_2:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack2, ceaseSoundTrack2, ceaseSpeechTrack2))
    elif name == UNION_BUST_3:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack3, ceaseSoundTrack3, ceaseSpeechTrack3))
    selfDamageTrack = Func(suit.showHpText, "1.1x DMG MULTIPLIER!", 2, openEnded=0)
    speechTrack = Func(suit.setChatAbsolute, "Do you have any idea how much paperwork I will have to file after this?", CFSpeech | CFTimeout)
    managerHealTrack = Sequence(Wait(2), Func(suit.showHpTextCheat, + targetSuit.currHP), Func(suit.showHpString, "1.1x DMG MULTIPLIER!"), Func(suit.setHealthForMe, + int(targetSuit.currHP)), Func(suit.updateHealthBar, 0))

    return Parallel(suitTrack, soundTrack, speechTrack, managerHealTrack, makeImmune)

def doWorkersCompensationGroup(attack, ind, ind2, ind3, ind4, ind5):
    suit = attack['suit']
    battle = attack['battle']
    targetSuit = battle.activeSuits[ind]
    targetSuit1 = battle.activeSuits[ind2]
    targetSuit2 = battle.activeSuits[ind3]
    targetSuit3 = battle.activeSuits[ind4]
    targetSuit4 = battle.activeSuits[ind5]
    suitTrack = Sequence(ActorInterval(suit, 'frustrated'), Func(suit.setNeutralAnimation))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)
    makeImmune = Func(suit.makeDamageUp)
    managerHealTrack = Sequence(Wait(2), Func(suit.showHpTextCheat, +int(targetSuit.currHP + targetSuit1.currHP + targetSuit2.currHP + targetSuit3.currHP + targetSuit4.currHP)), Func(suit.showHpString, "1.5x DMG MULTIPLIER!"), Func(suit.setHealthForMe,  + (targetSuit.currHP + targetSuit1.currHP + targetSuit2.currHP + targetSuit3.currHP + targetSuit4.currHP)), Func(suit.updateHealthBar, 0))
    selfDamageTrack = Func(suit.showHpText, "1.25x DMG MULTIPLIER!", 2, openEnded=0)
    speechTrack = Func(suit.setChatAbsolute, "Do you have any idea how much paperwork I will have to file after this?", CFSpeech | CFTimeout)
    managerHealTrack.append(Wait(2.0))
    managerHealTrack.append(doPayback2(attack))
    return Parallel(suitTrack, soundTrack, speechTrack, makeImmune, managerHealTrack)

def doPayback(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(suit, 'pie-small-react'), Func(suit.setNeutralAnimation))
    makeImmune = Func(suit.makeVulnerable)
    selfDamageTrack = Func(suit.showHpText, "VULNERABLE!", 2, openEnded=0)
    speechTrack = Func(suit.setChatAbsolute, random.choice(("Well, that didn't go how I planned it would.", "What an unfortunate turn of events.", "Come on Toons, show me your hellfire.")), CFSpeech | CFTimeout)
    return Parallel(suitTrack, speechTrack, makeImmune, selfDamageTrack)

def doPayback2(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(suit, 'soak', playRate=1.5), Func(suit.setNeutralAnimation))
    speechTrack = Func(suit.setChatAbsolute, random.choice(("Well, that didn't go how I planned it would.", "What an unfortunate turn of events.", "Come on Toons, show me your hellfire.")), CFSpeech | CFTimeout)
    return Parallel(suitTrack, speechTrack)

def doStealSafe(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    suitTrack = Sequence(getSuitTrack(attack), Func(suit.setNeutralAnimation))
    suit.setHealthForMe(int(suit.currHP + (dmg * 4)))
    toonTrack = getToonTrack(attack, 0.6, ['slip-forward'], 0.01, ['applause'])
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, +(dmg * 4)), Func(suit.updateHealthBar, 0))
    multiTrackList = Parallel(suitTrack, toonTrack, selfDamageTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('AA_drop_safe_miss.ogg', delay=0.2, node=suit)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doStealSafeMulti(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    for t in targets:
        dmg = t['hp']
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.setNeutralAnimation))
    suit.setHealthForMe(int(suit.currHP + ((dmg * 4) * len(battle.activeToons))))
    toonTrack = getToonTracks(attack, 0.6, ['slip-forward'], 0.01, ['applause'])
    selfDamageTrack = Sequence(Wait(2), Func(suit.showHpText, +(dmg * 4)* len(battle.activeToons)), Func(suit.updateHealthBar, 0))
    multiTrackList = Parallel(suitTrack, toonTrack, selfDamageTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('AA_drop_safe_miss.ogg', delay=0.2, node=suit)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doHostileTakeoverNew(attack):
    suit = attack['suit']
    battle = attack['battle']
    knifeDelay = 4.0
    suitTrack = getSuitAnimTrack(attack, playRate=1.25)
    knifeTracks = Parallel()
    for i in xrange(60):
        knife = globalPropPool.getProp('dagger')
        knifePos = Point3(random.randrange(-7.0, 10.0), random.randrange(-6.0, -4.0), 10.0)
        landPos = Point3(knifePos.getX() - 3.0, knifePos.getY(), -2.0)
        knifeTrack = Sequence(
            Wait(knifeDelay + 0.05 * i),
            Func(knife.reparentTo, battle),
            Func(knife.setPos, knifePos),
            Func(knife.lookAt, landPos),
            Func(knife.setScale, Point3(0.4)),
            LerpPosInterval(knife, 0.2, landPos),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
    damageAnims = [['slip-forward', 0.01, 0.4, 1.2],
     ['slip-forward', 0.01, 1.0]]
    dodgeAnims = [['duck', 1e-06, 0.8]]
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Squirt gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dsk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    toonTracks = getToonTracks(attack, damageDelay=knifeDelay + 0.11, splicedDamageAnims=damageAnims, dodgeDelay=knifeDelay - 0.1, splicedDodgeAnims=dodgeAnims)
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=knifeDelay, node=suit)
    return Parallel(suitTrack, knifeTracks, toonTracks, soundTrack)

def doWheelSpin(attack):
    suit = attack['suit']
    battle = attack['battle']
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit), ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1), Func(suit.loop, 'highroller-neutral-levitate-loop'), Wait(9.5), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    talkTrack = Sequence(Wait(7.5), Func(suit.setChatAbsolute, "WhAHAHAHAt a ffhow!", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Oooo-hooo-hooo, ratingff are ffkyrocketing! Line goeff up, head turner! Keep thoffe cameraff rollin'!", CFSpeech | CFTimeout), Wait(4.5), Func(suit.setChatAbsolute, "Let'ff ffee the nefft big play for today!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute, "Hope the folkff at home are ready for a real ffhowfftopper!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute,  "This duet jufft got a hip hump bump to a five-part big band, babe!"
"I'm the hottest fftar on fftage! Ffo come on inamorata, let'ff burn a hole in those goggle boffeff!"
"Better ffmile before ya burn out!", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    return Parallel(talkTrack, suitTrack, soundTrack)

def doWheelSpinPhase3(attack):
    suit = attack['suit']
    battle = attack['battle']
    taunt = random.choice(
        ["Every copy of me iff perffonalized.",
         "One ffhowfftopper jufft iffn't enough! There needff to be more!"])
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(Func(suit.loop, 'neutral2'), Wait(11.3), MovieUtil.createSuitLaughInterval2(suit), ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1), Func(suit.loop, 'highroller-neutral-levitate-loop'), Wait(1.0))
    talkTrack = Sequence(Func(suit.setChatAbsolute, "WhAHAHAHAt a ffhow!", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Oooo-hooo-hooo, ratingff are ffkyrocketing! Line goeff up, head turner! Keep thoffe cameraff rollin'!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute, "Hope the folkff at home are ready for a real ffhowfftopper!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute,  "This duet jufft got a hip hump bump to a five-part big band, babe!"
"I'm the hottest fftar on fftage! Ffo come on inamorata, let'ff burn a hole in those goggle boffeff!"
"Better ffmile before ya burn out!", CFSpeech | CFTimeout), Wait(4.0), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', delay=11.3, node=suit)
    suitTrack.append(Func(suit.makeIntoPhase3))
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeUnVulnerable))
    return Parallel(talkTrack, suitTrack, soundTrack1)

def doWheelSpinTrickOfTheLight(attack):
    suit = attack['suit']
    battle = attack['battle']
    taunt = random.choice(
        ["Every copy of me iff perffonalized.",
         "One ffhowfftopper jufft iffn't enough! There needff to be more!"])
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1), Func(suit.loop, 'highroller-neutral-levitate-loop'), Wait(3.0))
    talkTrack = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeUnVulnerable))
    return Parallel(talkTrack, suitTrack)

def doWheelSpinVulnerable(attack):
    suit = attack['suit']
    battle = attack['battle']
    taunt = random.choice(
        ["WHAT A TWIFFT!!!",
         "One ffhowfftopper jufft iffn't enough! There needff to be more!"])
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(ActorInterval(suit, 'pie-small-react'), Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')), Wait(3.0))
    talkTrack = Func(suit.setChatAbsolute, "WHAT A TWIFFT!!!", CFSpeech | CFTimeout)
    suitTrack.append(Func(suit.makeVulnerable))
    return Parallel(talkTrack, suitTrack)

def doWheelSpin2(attack):
    suit = attack['suit']
    battle = attack['battle']
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit), ActorInterval(suit, 'snap'), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    talkTrack = Sequence(Wait(8.0), Func(suit.setChatAbsolute, "Alright, alright, let'ff get thoffe efftraff on ffet, baby doll. Bring 'em in.", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Peep your eyeff, we've got ffo much in fftore today for you!", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack4 = getSoundTrack('SA_bash.ogg', delay=8.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4))
    suitTrack.append(Wait(2.0))
    suitTrack.append(Func(suit.makeImmortal))
    suitTrack.append(Func(suit.makeShielding))
    return Parallel(talkTrack, suitTrack, soundTrack)

def doWheelSpinDiceRoulette(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    taunt = random.choice(
        ["Hoping we don't land of ffnake eyeff here, right folkff?", "Pain iff ffhared equally between all participantff.",
         "Lady Luck, you better be on my ffide tonight! Let'ff roll on it!", "Everyone getff a piece of thiff! No FFuit or Toon left unharmed.",
         "Where the diffe will land, nobody knowff--effept for me!"])
    talkTrack = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    suitTrack = Sequence(talkTrack, Wait(2.0), MovieUtil.createSuitLaughIntervalDice(suit), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=2.5, node=suit)
    if name == LD_RE_ORG:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Func(suit.makeNonImmortal))
        suitTrack.append(doDiceRouletteCogs(attack))
    elif name == LD_AFTERSHOCK:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Func(suit.makeNonImmortal))
        suitTrack.append(doDiceRouletteToons(attack))
    elif name == LD_QUAKE:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Func(suit.makeNonImmortal))
        suitTrack.append(doDiceRouletteAll(attack))
    elif name == LD_EVICTION_NOTICE:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Func(suit.makeNonImmortal))
        suitTrack.append(doDiceRouletteToon(attack))
    elif name == LD_RED_TAPE:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Func(suit.makeNonImmortal))
        suitTrack.append(doDiceRouletteNothing(attack))
    return Parallel(talkTrack, suitTrack, soundTrack3)

def doDiceRouletteCogs(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    taunt = random.choice(
        ["WHAT A TWIFFT!!!",
         "'FFLAM!' What a ffweet ffound!",
         "Now, you ffigned up for thiff!",
         "Here it comeff, boyff!",])
    suitTrack = Parallel(Func(suit.play, 'snap'), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    for suit in battle.activeSuits:
        suit.setHealthForMe(int(suit.currHP - 250))
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
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
        toonTrack = Sequence(
            Wait(1.5),
            Parallel(
                ActorInterval(suit, 'flatten'),
                Func(suit.showHpText, -250),
                Func(suit.updateHealthBar, 0)
            ))
        if suit.currHP <= 0 and not suit.dna.name == 'mad':
            toonTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
        elif suit.currHP <= 0:
            toonTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        toonTrack.append(
                Func(suit.setNeutralAnimation))
        toonTracks.append(toonTrack)
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack)


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
    suitTrack = Parallel(ActorInterval(suit, 'snap'), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
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
        toonTrack = Sequence(
        Wait(2.0),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
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
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks)


def doDiceRouletteToon(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
    toonPos = toon.getPos(battle)
    initialScale = toon.getScale()
    y = toonPos.getY()
    gavelPos = Point3(toonPos.getX(), y, 30)
    propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(2), scaleUpTime=1.5),
        LerpPosInterval(gavel, 0.25,  Point3(toonPos.getX(), y, 2.01)), LerpPosInterval(gavel, 0.1,  Point3(toonPos.getX(), y, 3)),
                 LerpPosInterval(gavel, 0.1,  Point3(toonPos.getX(), y, 2.01)), Sequence(
            Wait(1.5),
            LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
        ))

    taunt = random.choice(
        ["Can't ffquaffh and fftretch your way out of thiff one, Toonff!", "Who'ff ready for ffome cartoon violenffe?!",
         "FForry, babe, but the ratingff don't lie! Thiff iff what the viewerff want!",
         "And the ratingff FFKYROCKET!!!", "If it meanff anything, thiff iff gonna hurt me a lot more than it hurtff you!", "'Ker-ffplat!' HahaHAHA!!! You Toonff really are funny!"])
    suitTrack = Parallel(ActorInterval(suit, 'snap'), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    toonTrack = Sequence(
        Wait(2.0),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, target[0]['died'])
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
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, soundTrack, toonTrack, propTrack)

def doDiceRouletteNothing(attack):
    suit = attack['suit']
    taunt = random.choice(
        ["Look'ff like nuffin!", "Aww ratff, a total bufft!!",
         "Ffhew! Now that waff a cloffe call, waffn't it, folkff?",
         "Lady Luck iff merffiful today, huh?",
         "And THAT iff why they call you our LUCKY contefftantff!"])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Wait(2.0))
    return suitTrack


def doDiceRouletteAll(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    taunt = random.choice(
        ["WHAT A TWIFFT!!!",
         "'FFLAM!' What a ffweet ffound!",
         "Now, you ffigned up for thiff!",
         "Here it comeff, boyff!", ])
    suitTrack = Parallel(Func(suit.play, 'snap'), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    propTracks = Parallel()
    toonTracks = Parallel()
    propTracks2 = Parallel()
    toonTracks2 = Parallel()
    for suit in battle.activeSuits:
        suit.setHealthForMe(int(suit.currHP - (50 * len(battle.activeToons))))
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
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
        toonTrack = Sequence(
            Wait(1.5),
            Parallel(
                ActorInterval(suit, 'flatten'),
                Func(suit.showHpText, -250),
                Func(suit.updateHealthBar, 0)
            ))
        if suit.currHP <= 0 and not suit.dna.name == 'mad':
            toonTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
        elif suit.currHP <= 0:
            toonTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        toonTrack.append(
            Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        toonTracks.append(toonTrack)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        gavel = loader.loadModel('phase_5/models/props/cc_m_bat_prp_dice')
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y, 30)
        propTrack2 = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y, 2.01)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 3)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y, 2.01)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))

        propTracks2.append(propTrack2)
        toonTrack2 = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(__doDamage, toon, dmg, t['died'])
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
        toonTracks2.append(toonTrack2)
    soundTrack = getSoundTrack('AA_drop_bigweight.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTracks, toonTracks2, propTracks2, propTracks, soundTrack)



def doWheelSpinCheat1(attack):
    manager = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Wait(10.0))
        suitTrack.append(resetTrack)
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTracks.append(suitTrack)
        suitTracks.append(
            Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        for headPart in suit.animatedHeadParts:
            if suit.style.name == 'crf':
                suitTracks.append(Func(headPart.loop, 'neutral%s' % (
                    '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''), fromFrame=0, toFrame=22))
            elif suit.style.name == 'mad':
                suitTracks.append(Func(headPart.loop, 'neutral%s' % (
                    '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''), fromFrame=0, toFrame=22))
            else:
                suitTracks.append(Func(headPart.loop, 'neutral%s' % (
                    '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    managerTrack = Sequence(MovieUtil.createSuitLaughInterval(manager), Func(manager.loop, 'neutral%s' % ('-hurt' if float(manager.currHP) / float(manager.maxHP) <= 0.25 else '')))
    talkTrack = Sequence(Wait(8.0), Func(manager.setChatAbsolute, "GOOD MOOORNING TOONTOOOOWN!!!", CFSpeech | CFTimeout), Wait(2.8), Func(manager.setChatAbsolute, "Ohoho-no-no, takeff a party to partiffipate and play, and I ffay play!!", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=manager)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=manager)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=manager)
    soundTrack4 = getSoundTrack('cc_s_dlg_ene_hroller_good_morning_clash_general.ogg', delay=8.0, node=manager)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4))
    managerTrack.append(Wait(2.0))
    return Parallel(talkTrack, managerTrack, suitTracks, soundTrack)

def doWheelSpinCheat2(attack):
    manager = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        makeSyphon = Func(suit.makeSyphon)
        suitTrack = Sequence()
        suitTrack.append(Wait(11))
        if not suit.dna.name == 'dsf':
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout))
        suitTrack.append(makeSyphon)
        suitTracks.append(suitTrack)
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    managerTrack = Sequence(MovieUtil.createSuitLaughInterval(manager), ActorInterval(manager, 'scabbard'), Func(manager.loop, 'neutral%s' % ('-hurt' if float(manager.currHP) / float(manager.maxHP) <= 0.25 else '')))
    talkTrack = Sequence(Wait(8.0), Func(manager.setChatAbsolute, "Ready to find out which one of you iff really the weakefft link?!", CFSpeech | CFTimeout), Wait(2.8), Func(manager.setChatAbsolute, "Another one biteff the dufft, I ffuppoffe! Anywayff...", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=manager)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=manager)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=manager)
    soundTrack4 = getSoundTrack('SA_scabbard.ogg', delay=8.0, node=manager)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4))
    managerTrack.append(Wait(2.0))
    managerTrack.append(Func(manager.makeUnSyphon))
    return Parallel(talkTrack, managerTrack, suitTracks, soundTrack)

def doWheelSpinCheat3(attack):
    suit = attack['suit']
    battle = attack['battle']
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit), ActorInterval(suit, 'cease'), Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    talkTrack = Sequence(Wait(8.0), Func(suit.setChatAbsolute, "My memory iffn't aff good, but let'ff ffee if you can keep up.", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "One, two, three, two - oh I can't remember! Have you been paying attention?", CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack4 = getSoundTrack('SA_cease_and_desist.ogg', delay=8.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4))
    suitTrack.append(Wait(2.0))
    return Parallel(talkTrack, suitTrack, soundTrack)

def doWheelSpinCheat4(attack):
    suit = attack['suit']
    battle = attack['battle']
    # cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit), ActorInterval(suit, 'cease'), Func(suit.loop,
                                                                                                     'neutral%s' % (
                                                                                                         '-hurt' if float(
                                                                                                             suit.currHP) / float(
                                                                                                             suit.maxHP) <= 0.25 else '')))
    talkTrack = Sequence(Wait(8.0), Func(suit.setChatAbsolute, "My memory iffn't aff good, but let'ff ffee if you can keep up.",
                              CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute,
                                                                     "One, two, three, two - oh I can't remember! Have you been paying attention?",
                                                                     CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack4 = getSoundTrack('SA_cease_and_desist.ogg', delay=8.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4))
    suitTrack.append(Wait(2.0))
    return Parallel(talkTrack, suitTrack, soundTrack)

def doWheelSpinCheat5(attack, ind, ind2, ind3, ind4, ind5):
    suit = attack['suit']
    battle = attack['battle']
    targetSuit = battle.activeSuits[ind]
    targetSuit1 = battle.activeSuits[ind2]
    targetSuit2 = battle.activeSuits[ind3]
    targetSuit3 = battle.activeSuits[ind4]
    targetSuit4 = battle.activeSuits[ind5]

    suitTrack6 = Sequence(Wait(9.0), Func(targetSuit.showHpText, "SYPHONED!", 10),
                         ActorInterval(targetSuit, 'soak', duration=2.25),
                         Sequence(MovieUtil.spawnHeadExplosion(targetSuit, battle)), Func(targetSuit.setChatAbsolute,
                                                                                          "Ouch.",
                                                                                          CFSpeech | CFTimeout),
                         Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit, battle))
    selfDamageTrack = Sequence(Wait(10), Func(targetSuit.showHpText, -targetSuit.currHP),
                               Func(targetSuit.updateHealthBar, targetSuit.currHP))
    suitTrack1 = Sequence(Wait(9.1), Func(targetSuit1.showHpText, "SYPHONED!", 10),
                          ActorInterval(targetSuit1, 'soak', duration=2.25),
                          Sequence(MovieUtil.spawnHeadExplosion(targetSuit1, battle)), Func(targetSuit1.setChatAbsolute,
                                                                                            "Ouch.",
                                                                                            CFSpeech | CFTimeout),
                          Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit1, battle))
    selfDamageTrack1 = Sequence(Wait(10), Func(targetSuit1.showHpText, -targetSuit1.currHP),
                                Func(targetSuit1.updateHealthBar, targetSuit1.currHP))
    suitTrack2 = Sequence(Wait(9.2), Func(targetSuit2.showHpText, "SYPHONED!", 10),
                          ActorInterval(targetSuit2, 'soak', duration=2.25),
                          Sequence(MovieUtil.spawnHeadExplosion(targetSuit2, battle)), Func(targetSuit2.setChatAbsolute,
                                                                                            "Ouch.",
                                                                                            CFSpeech | CFTimeout),
                          Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit2, battle))
    selfDamageTrack2 = Sequence(Wait(10), Func(targetSuit2.showHpText, -targetSuit2.currHP),
                                Func(targetSuit2.updateHealthBar, targetSuit2.currHP))
    suitTrack3 = Sequence(Wait(9.3), Func(targetSuit3.showHpText, "SYPHONED!", 10),
                          ActorInterval(targetSuit3, 'soak', duration=2.25),
                          Sequence(MovieUtil.spawnHeadExplosion(targetSuit3, battle)), Func(targetSuit3.setChatAbsolute,
                                                                                            "Ouch.",
                                                                                            CFSpeech | CFTimeout),
                          Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit3, battle))
    selfDamageTrack3 = Sequence(Wait(10), Func(targetSuit3.showHpText, -targetSuit3.currHP),
                                Func(targetSuit3.updateHealthBar, targetSuit3.currHP))
    suitTrack4 = Sequence(Wait(9.3), Func(targetSuit4.showHpText, "SYPHONED!", 10),
                          ActorInterval(targetSuit4, 'soak', duration=2.25),
                          Sequence(MovieUtil.spawnHeadExplosion(targetSuit4, battle)), Func(targetSuit4.setChatAbsolute,
                                                                                            "Ouch.",
                                                                                            CFSpeech | CFTimeout),
                          Wait(1.0), MovieUtil.createSuitHeadlessDeathTrack(targetSuit4, battle))
    selfDamageTrack4 = Sequence(Wait(10), Func(targetSuit4.showHpText, -targetSuit4.currHP),
                                Func(targetSuit4.updateHealthBar, targetSuit4.currHP))
    # cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence(MovieUtil.createSuitLaughInterval(suit), ActorInterval(suit, 'snap'), Func(suit.loop,
                                                                                                     'neutral%s' % (
                                                                                                         '-hurt' if float(
                                                                                                             suit.currHP) / float(
                                                                                                             suit.maxHP) <= 0.25 else '')))
    talkTrack = Sequence(Wait(8.0), Func(suit.setChatAbsolute, "Lookff like they couldn't take the HAHAheat!",
                              CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute,
                                                                     "I can jufft hear the crowd going wild for thiff intermiffion!",
                                                                     CFSpeech | CFTimeout))
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack4 = getSoundTrack('SA_bash.ogg', delay=8.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3, soundTrack4))
    suitTrack.append(Wait(2.0))
    return Parallel(talkTrack, suitTrack, soundTrack, suitTrack1, suitTrack2, suitTrack3, suitTrack4, suitTrack6, selfDamageTrack1, selfDamageTrack2, selfDamageTrack3, selfDamageTrack4, selfDamageTrack)

def doCaseClosed(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    movePoint = toon.getPos(battle)
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    suitTrack = Sequence()
    suitTrack.append(LerpPosHprInterval(suit, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0)))
    suitTrack.append(Wait(2.0))
    suitTrack.append(MovieUtil.createSuitCaseClosedInterval(suit))
    #suitOpenMouthTrack = MovieUtil.createSuitCaseClosedInterval(suit)
    #talkTrack = Sequence(Wait(7.5), Func(suit.setChatAbsolute, "Alright, alright, let'ff get thoffe efftraff on ffet, baby doll. Bring 'em in.", CFSpeech | CFTimeout), Wait(2.8), Func(suit.setChatAbsolute, "Peep your eyeff, we've got ffo much in fftore today for you!", CFSpeech | CFTimeout), Wait(2.5), Func(suit.setChatAbsolute, "Come on, babe, FFHOW UFF THOFFE NUMBERFF!", CFSpeech | CFTimeout), Wait(3.7), Func(suit.setChatAbsolute, "And now back to our regularly ffcheduled programming.", CFSpeech | CFTimeout))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - -4, ['slip-backward'], suitTrack.getDuration() - -4, ['bored'])
    soundTrack1 = getSoundTrack('ttcc_ene_hroller_laugh.ogg', node=suit)
    soundTrack2 = getSoundTrack('cc_s_sfx_ene_hroller_reappear_after_wheel.ogg', delay=7.0, node=suit)
    soundTrack3 = getSoundTrack('cc_s_sfx_ene_hroller_sweep_before_wheel.ogg', delay=3.0, node=suit)
    soundTrack = (Parallel(soundTrack1, soundTrack2, soundTrack3))
    return Parallel(suitTrack, toonTrack)

def doAccusations2(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    gavel = globalPropPool.getProp('LB_gavel')
    toonPos = toon.getPos(battle)
    gavelPos = Point3(toonPos.getX(), 2, 0)
    propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=10,
                           scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
        Parallel(getSoundTrack('LB_gavel.ogg', node=toon), Sequence(
            Wait(0.1),
            LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
            LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO)
        ))
    )
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'), Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0), blendType='easeInOut'), Wait(2), LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0), blendType='easeInOut'), Wait(3.2), LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0), blendType='easeInOut'))
    #suitTrack = getSuitAnimTrack(attack)
    cameraTrack = Sequence(
            LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'),
            Wait(1.8), LerpPosHprInterval(camera, duration=0.5, pos=Point3(4, -11, 2), hpr=Point3(30, 0, 0),
                                          blendType='easeInOut'), Wait(2),
            LerpPosHprInterval(camera, duration=0, pos=Point3(3, -5, 10), hpr=Point3(30, -15, 0),
                               blendType='easeInOut'), Wait(3.2),
            LerpPosHprInterval(camera, duration=0.5, pos=Point3(0, -15, 3), hpr=Point3(0, 10, 0),
                               blendType='easeInOut'))
    suitTrack = getSuitAnimTrack(attack)
    suit.setHealthForMe(int(suit.currHP - 350))
    selfDamageTrack = Sequence(Wait(11.6), Func(suit.showHpText, -350), Func(suit.updateHealthBar, 0))
    talkTrack = Sequence(Wait(3.5), Func(suit.setChatAbsolute,
                                             "This toon has been accused of damaging countless cogs throughout Toontown.",
                                             CFSpeech | CFTimeout), Wait(2.8),
                             Func(suit.setChatAbsolute, "Here is the evidence to support my claim.",
                                  CFSpeech | CFTimeout), Wait(2.5),
                             Func(suit.setChatAbsolute, "Has the jury reached a verdict?",
                                  CFSpeech | CFTimeout), Wait(3.7),
                             Func(suit.setChatAbsolute, "This toon has proven their innocence. This toon has received a gag damage boost as compensation.",
                                  CFSpeech | CFTimeout))
    animTrack = Sequence(Wait(2), ActorInterval(suit, 'speak', startTime=0, endTime=8.6, playRate=1),
                             ActorInterval(suit, 'soak', startTime=0, endTime=2.5, playRate=1))
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - -4, ['bored'], suitTrack.getDuration() - -4,
                                 ['bored'])
    soundTrack = getSoundTrack('SA_hurry_sickness.ogg', delay=12.5, node=suit)
    return Parallel(cameraTrack, talkTrack, suitTrack, animTrack, toonTrack, soundTrack, selfDamageTrack)

def doAccusations(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    toonPos = toon.getPos(battle)
    #cameraTrack = LerpPosHprInterval(camera, duration=1, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut')
    suitTrack = getSuitAnimTrack(attack)
    suit.setHealthForMe(int(suit.currHP + 1000))
    selfDamageTrack = Sequence(Wait(5), Func(suit.showHpText, + 1000), Func(suit.updateHealthBar, 0))
    notifyTrack = Sequence(Wait(2.5), Func(suit.showHpText, "Desperation!\n+1 Round Lure Resistance!\n1.4x Damage Multiplier", 2, openEnded=0))
    talkTrack = Sequence(Wait(2.5), Func(suit.setChatAbsolute, "You may have defeated my partner, however I'm not going down that easily.", CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute, "Let's see how much power you really have. I will be immune to all gags for 1 turn.", CFSpeech | CFTimeout))
    animTrack = Sequence(Wait(5.0), Func(suit.play, 'frustrated'), Func(suit.loop, 'neutral%s' % (
        '-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=5.0, node=suit)
    return Parallel(talkTrack, suitTrack, animTrack, soundTrack, notifyTrack, selfDamageTrack)

def doSlushFund(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    theSuit = None
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    for s in battle.activeSuits:
        if s.dna.name == 'crf':
            print('Found manager... using it...')
            theSuit = s

    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit

    print('*************************************')

    print('suit.currHP %i' % int(suit.currHP))
    print('setHP() %i' % int(suit.currHP - (suit.currHP / 4)))
    suit.setHealthForMe(int(suit.currHP - (suit.currHP / 4)))
    print('suit.currHP %i' % int(suit.currHP))

    print('ts.currHP %i' % int(theSuit.currHP))
    print('setHP() %i' % int(theSuit.currHP + (suit.currHP / 4)))
    theSuit.setHealthForMe(int(theSuit.currHP + (suit.currHP / 4)))
    print('ts.currHP %i' % int(theSuit.currHP))

    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    moveTrack = Sequence(LerpPosInterval(suit, 1.5, sinkPos2, other=battle), LerpPosInterval(suit, 0, sinkPos, other=battle), Wait(3.9), LerpPosInterval(suit, 0, sinkPos2, other=battle), LerpPosInterval(suit, 1.5, dropPos, other=battle), Func(suit.setPos, battle, dropPos))

    suitTrack = Sequence(ActorInterval(suit, 'walk'), getSuitAnimTrack(attack), ActorInterval(suit, 'walk'))
    soundTrack = Sequence(Wait(4.0), SoundInterval(globalBattleSoundCache.getSound('cc_s_sfx_ara_wheel_tone.ogg'), node=suit))
    selfDamageTrack = Sequence(Wait(4.0), Func(suit.showHpText, -(suit.currHP / 4)), Func(suit.updateHealthBar, 0))
    managerHealTrack = Sequence(Wait(4.0), Func(theSuit.showHpText, (suit.currHP / 4)), Func(theSuit.updateHealthBar, 0),
                                Func(theSuit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHighRollerPhrases),
                                     CFSpeech | CFTimeout),
                                SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    return Parallel(suitTrack, soundTrack, moveTrack, selfDamageTrack, managerHealTrack)

def doBayouBash3(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    theSuit = None
    for s in battle.activeSuits:
        if s.dna.name == 'mad':
            print('Found manager... using it...')
            theSuit = s

    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit


    suitTrack = Sequence(getSuitAnimTrack(attack))
    #soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
    x = int((theSuit.maxHP * theSuit.hardMaxHP) - theSuit.currHP)
    theSuit.setHealthForMe(int(theSuit.currHP + x))
    managerHealTrack = Sequence(Wait(2), Func(theSuit.showHpText, x), Func(theSuit.updateHealthBar, 0),
                                Func(theSuit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                     CFSpeech | CFTimeout),
                                SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    return Parallel(suitTrack, managerHealTrack)


def doPoisonSpray(attack):
    suit = attack['suit']
    makeShielding = Func(suit.makeShielding)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_defense.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, makeShielding)

def doExtraTip(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    theSuit = None

    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit

    print('*************************************')

    print('ts.currHP %i' % int(theSuit.currHP))
    print('setHP() %i' % int(theSuit.currHP + 500))
    theSuit.setHealthForMe(int(theSuit.currHP + 500))
    print('ts.currHP %i' % int(theSuit.currHP))
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(suit, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    soundTrack1 = getSoundTrack('SA_paper_throw.ogg', delay=5, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=3, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(5.0), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, healSound, multiTrack)


def doWaterSpray(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    damageDelay = 1.95
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('WaterSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('SprayLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 4.1, [liftEffect, battle, 0]))
            shadow = toon.dropShadow
            fakeShadow = MovieUtil.copyProp(shadow)
            x = toon.getX()
            y = toon.getY()
            z = toon.getZ()
            height = 3
            groundPoint = Point3(x, y, z)
            risePoint = Point3(x, y, z + height)
            shakeRight = Point3(x, y + 0.7, z + height)
            shakeLeft = Point3(x, y - 0.7, z + height)
            shakeTrack = Sequence()
            shakeTrack.append(Wait(damageDelay + 0.25))
            shakeTrack.append(Func(shadow.hide))
            shakeTrack.append(LerpPosInterval(toon, 1.1, risePoint))
            for i in xrange(0, 17):
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeLeft))
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeRight))

            shakeTrack.append(LerpPosInterval(toon, 0.1, risePoint))
            shakeTrack.append(LerpPosInterval(toon, 0.1, groundPoint))
            shakeTrack.append(Func(shadow.show))
            shadowTrack = Sequence()
            shadowTrack.append(Func(battle.movie.needRestoreRenderProp, fakeShadow))
            shadowTrack.append(Wait(damageDelay + 0.25))
            shadowTrack.append(Func(fakeShadow.hide))
            shadowTrack.append(Func(fakeShadow.setScale, 0.27))
            shadowTrack.append(Func(fakeShadow.reparentTo, toon))
            shadowTrack.append(Func(fakeShadow.setPos, MovieUtil.PNT3_ZERO))
            shadowTrack.append(Func(fakeShadow.wrtReparentTo, battle))
            shadowTrack.append(Func(fakeShadow.show))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.4, Point3(0.17, 0.17, 0.17)))
            shadowTrack.append(Wait(1.81))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.1, Point3(0.27, 0.27, 0.27)))
            shadowTrack.append(Func(MovieUtil.removeProp, fakeShadow))
            shadowTrack.append(Func(battle.movie.clearRenderProp, fakeShadow))
            toonRiseTracks.append(Parallel(shakeTrack, shadowTrack))

    damageAnims = []
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.9, startTime=2.06))
    damageAnims.append(['slip-forward', 0.01, 0.5])
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    if hitAtleastOneToon == 1:
        soundTrack = getSoundTrack('SA_watercooler_spray_only.ogg', delay=4.4, node=suit)
        return Parallel(suitTrack, sprayTrack, soundTrack, liftTracks, toonTracks, toonRiseTracks)
    else:
        return Parallel(suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks)


def doMoneyTrip(attack):
    suit = attack['suit']
    battle = attack['battle']
    cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.25, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    centerColor = Vec4(0, 1.0, 0, 1.0)
    edgeColor = Vec4(0, 1.0, 0, 1.0)
    powerBar1 = BattleParticles.createParticleEffect(file='moneytrip')
    powerBar2 = BattleParticles.createParticleEffect(file='moneytrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    suitTrack = getSuitAnimTrack(attack)

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = Sequence(Wait(1), SoundInterval(globalBattleSoundCache.getSound('SA_money_fall.ogg'), node=suit))
    return Parallel(cameraTrack, suitTrack, partTrack1, partTrack2, waterfallTrack, toonTracks, soundTrack)



def doTeeOff(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.75, 1.75, 1.75)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(1.125))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack)

def doTeeOffGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    club = globalPropPool.getProp('golf-club')
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        ball = globalPropPool.getProp('golf-ball')
        suitName = attack['suitName']
        ballPosPoints = [Point3(5.1, 4.0, 0.1)]
        ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.75, 1.75, 1.75)),
                                 Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                                 Wait(1.125))
        missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
        ballPropTrack.append(getThrowTrack(ball, toon.getPos(battle), 0.1, battle, .1))
        ballPropTrack.append(Func(MovieUtil.removeProp, ball))
        ballPropTracks.append(ballPropTrack)
    dodgeDelay = suitTrack.getDuration()
    toonTracks = getToonTracks(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    mulliganTrack = Sequence(Wait(6.0), doMulliganGroup(attack))
    return Parallel(suitTrack, toonTracks, clubPropTrack, ballPropTracks, mulliganTrack, soundTrack)


def doTeeOff2(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.5, 1.5, 1.5)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(1.125))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    mulliganTrack = Sequence(Wait(6.0), doMulligan(attack))
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack, mulliganTrack)

def doTeeOffRefinementManagerProtection(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    taunt = getAttackTaunt('Golf', attack['suitName'])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'golf-club-swing', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.5, 1.5, 1.5)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(1.125))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    mulliganTrack = Sequence(Wait(6.0), doMulligan(attack))
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack, mulliganTrack)

def doTeeOffTrap(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    taunt = getAttackTaunt('Golf', attack['suitName'])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'golf-club-swing', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.5, 1.5, 1.5)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(1.125))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    mulliganTrack = Sequence(Wait(6.0), doMulligan(attack))
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack, mulliganTrack)

def doTeeOffHeal(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    taunt = getAttackTaunt('Golf', attack['suitName'])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'golf-club-swing', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.5, 1.5, 1.5)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(1.125))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    mulliganTrack = Sequence(Wait(6.0), doManagerHealTeeOff(attack))
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack, mulliganTrack)

def doTeeOffRefinement(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    taunt = getAttackTaunt('Golf', attack['suitName'])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'golf-club-swing', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 3, Point3(1.1, 1.1, 1.1))
    suitName = attack['suitName']
    ballPosPoints = [Point3(5.1, 4.0, 0.1)]
    ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.25, Point3(1.5, 1.5, 1.5)),
                             Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                             Wait(1.125))
    missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
    ballPropTrack.append(getPropThrowTrack(attack, ball, [__toonFacePoint(toon)], [missPoint], .1))
    ballPropTrack.append(Func(battle.movie.clearRenderProp, ball))
    dodgeDelay = suitTrack.getDuration()
    toonTrack = getToonTrack(attack, suitTrack.getDuration() - 1.75, ['slip-backward'], 1.5, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2.5, node=suit)
    mulliganTrack = Sequence(Wait(6.0), doRefinement(attack))
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack, mulliganTrack)

def doManagerHealTeeOff(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    taunt = random.choice(
        ["You did great work today, here's a bonus.",
         "Here's a little something for your trouble."])

    suitTracks = Parallel()
    tauntInterval = Sequence(Func(theSuit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    knifeTracks = Parallel()
    for s in battle.activeSuits:
        if s.dna.name == 'fbd':
            print('Found manager... using it...')
            suit = s
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            suitTrack.append(Func(suit.showHpTextCheat, 250))
            suitTrack.append(Func(suit.showHpString, "MANAGER BONUS!"))
            suitTrack.append(Func(suit.setHealthForMe, 250))
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                  CFSpeech | CFTimeout))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
            suitTracks.append(Wait(6.5))
            posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
            hitPoint = suit.getPos(battle)
            hitPoint.setZ(suit.height + 2)
            knife = globalPropPool.getProp('bonus-check')
            knifeTrack = Sequence(
                getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(8.5, 8.5, 8.5),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(-180, 90, 0))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
        elif s.dna.name == 'cp':
            print('Found manager... using it...')
            suit = s
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            suitTrack.append(Func(suit.showHpTextCheat, 250))
            suitTrack.append(Func(suit.showHpString, "MANAGER BONUS!"))
            suitTrack.append(Func(suit.setHealthForMe, 250))
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                  CFSpeech | CFTimeout))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
            suitTracks.append(Wait(6.5))
            posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
            hitPoint = suit.getPos(battle)
            hitPoint.setZ(suit.height + 2)
            knife = globalPropPool.getProp('bonus-check')
            knifeTrack = Sequence(
                getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(8.5, 8.5, 8.5),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(-180, 90, 0))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
        elif s.dna.name == 'frs':
            print('Found manager... using it...')
            suit = s
            suitTrack = Sequence()
            suitTrack.append(Wait(4.5))
            suitTrack.append(Func(suit.showHpTextCheat, 250))
            suitTrack.append(Func(suit.showHpString, "MANAGER BONUS!"))
            suitTrack.append(Func(suit.setHealthForMe, 250))
            suitTrack.append(Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                       CFSpeech | CFTimeout))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Func(suit.setNeutralAnimation))
            suitTracks.append(suitTrack)
            suitTracks.append(tauntInterval)
            suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
            suitTracks.append(Wait(6.5))
            posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
            hitPoint = suit.getPos(battle)
            hitPoint.setZ(suit.height + 2)
            knife = globalPropPool.getProp('bonus-check')
            knifeTrack = Sequence(
                getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, VBase3(8.5, 8.5, 8.5),
                                   scaleUpTime=0.1),
                Wait(2.3),
                Parallel(
                    getThrowTrack(knife, hitPoint, 1.5, battle, -30.288),
                    LerpHprInterval(knife, 0.8, VBase3(-180, 90, 0))),
                Parallel(
                    LerpPosInterval(knife, 1, VBase3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() - 10)),
                    Sequence(Wait(0.25), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0)))),
                Func(MovieUtil.removeProp, knife)
            )
            knifeTracks.append(knifeTrack)
    suitTrack = Sequence(Wait(6.0), Func(theSuit.setNeutralAnimation))
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=theSuit)
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=theSuit))
    return Parallel(suitTrack, suitTracks, healSound, soundTrack2, knifeTracks)

def doMulliganGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    name = attack['id']
    club = globalPropPool.getProp('golf-club')
    tauntIndex = attack['taunt']
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = random.choice(
        ['Let me just make this quick adjustment...', "That last shot didn't go the way that I wanted it to.",
         "Let's try this again.", 'I certainly will take a mulligan.'])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'golf-club-swing', playRate=1.75), suitReset, Func(suit.setNeutralAnimation))
    clubPosPoints = [Point3(0.2, 3.3, -0.5), VBase3(0.0, 45.0, 270.0)]
    clubPropTrack = getPropTrack(club, suit.getRightHand(), clubPosPoints, 0.25, 2.5, Point3(1.1, 1.1, 1.1))
    ballPropTracks = Parallel()
    for t in targets:
        toon = t['toon']
        ball = globalPropPool.getProp('golf-ball')
        suitName = attack['suitName']
        ballPosPoints = [Point3(5.1, 4.0, 0.1)]
        ballPropTrack = Sequence(getPropAppearTrack(ball, suit, ballPosPoints, 1.2, Point3(1.5, 1.5, 1.5)),
                                 Func(battle.movie.needRestoreRenderProp, ball), Func(ball.wrtReparentTo, render),
                                 Wait(0.75))
        missPoint = lambda ball=ball, toon=toon: __toonMissPoint(ball, toon)
        ballPropTrack.append(getThrowTrack(ball, toon.getPos(battle), 0.1, battle, 0.1))
        ballPropTrack.append(Func(MovieUtil.removeProp, ball))
        ballPropTracks.append(ballPropTrack)
    dodgeDelay = suitTrack.getDuration()
    toonTracks = getToonTracks(attack, 2.5, ['slip-backward'], 1, ['duck'],
                             showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_tee_off.ogg', delay=2, node=suit)
    makeNonImmortal = Func(suit.makeNonImmortal)
    suitTrack.append(makeNonImmortal)
    return Parallel(suitTrack, toonTracks, clubPropTrack, ballPropTracks, soundTrack)

def doMulligan(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    club = globalPropPool.getProp('golf-club')
    ball = globalPropPool.getProp('golf-ball')
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = random.choice(['Let me just make this quick adjustment...', "That last shot didn't go the way that I wanted it to.", "Let's try this again.", 'I certainly will take a mulligan.'])
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'golf-club-swing', playRate=1.75), suitReset, Func(suit.setNeutralAnimation))

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
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                      "So, I see you are very reliant on your Trap gags. Let's see how you do without them.",
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'tcm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    if name == REFINEMENT:
        suitTrack.append(Wait(2))
        suitTrack.append(doRefinement(attack))
    if name == MANAGERIAL_PROTECTION:
        suitTrack.append(Wait(2))
        suitTrack.append(doManagerialProtection(attack))
    return Parallel(suitTrack, toonTrack, clubPropTrack, ballPropTrack, soundTrack)


def doBrainStorm(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    name = attack['id']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    snowEffect = BattleParticles.createParticleEffect('BrainStorm')
    snowEffect2 = BattleParticles.createParticleEffect('BrainStorm')
    snowEffect3 = BattleParticles.createParticleEffect('BrainStorm')
    effectColor = Vec4(0.65, 0.79, 0.93, 0.85)
    BattleParticles.setEffectTexture(snowEffect, 'brainstorm-box', color=effectColor)
    BattleParticles.setEffectTexture(snowEffect2, 'brainstorm-env', color=effectColor)
    BattleParticles.setEffectTexture(snowEffect3, 'brainstorm-track', color=effectColor)
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 1.2
    damageDelay = 3.5
    dodgeDelay = 3.3
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    cloudPropTrack.append(Wait(0.5))
    cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=2.2, cleanup=True), Sequence(Wait(0.5), ParticleInterval(snowEffect2, cloud, worldRelative=0, duration=1.7, cleanup=True)), Sequence(Wait(1.0), ParticleInterval(snowEffect3, cloud, worldRelative=0, duration=1.2, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=2.5, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=1, duration=1.5))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 1e-06, 1.6]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('SA_brainstorm.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)

def doBrainStormHeadRoller(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    name = attack['id']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    snowEffect = BattleParticles.createParticleEffect('BrainStorm')
    snowEffect2 = BattleParticles.createParticleEffect('BrainStorm')
    snowEffect3 = BattleParticles.createParticleEffect('BrainStorm')
    effectColor = Vec4(0.65, 0.79, 0.93, 0.85)
    BattleParticles.setEffectTexture(snowEffect, 'brainstorm-box', color=effectColor)
    BattleParticles.setEffectTexture(snowEffect2, 'brainstorm-env', color=effectColor)
    BattleParticles.setEffectTexture(snowEffect3, 'brainstorm-track', color=effectColor)
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    if suitType == 'a':
        partDelay = 1.2
        damageDelay = 4.5
        dodgeDelay = 3.3
    elif suitType == 'b':
        partDelay = 1.2
        damageDelay = 4.5
        dodgeDelay = 3.3
    elif suitType == 'c':
        partDelay = 1.2
        damageDelay = 4.5
        dodgeDelay = 3.3
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('BrainStorm', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'effort', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), VBase3(180, 0, 0)]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    cloudPropTrack.append(Wait(0.5))
    cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=2.2, cleanup=True), Sequence(Wait(0.5), ParticleInterval(snowEffect2, cloud, worldRelative=0, duration=1.7, cleanup=True)), Sequence(Wait(1.0), ParticleInterval(snowEffect3, cloud, worldRelative=0, duration=1.2, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=2.5, duration=0.5), ActorInterval(cloud, 'stormcloud', startTime=1, duration=1.5))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 1e-06, 1.6]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('SA_brainstorm.ogg', delay=1.9, node=suit)
    if name == HEAD_ROLLER_2:
        suitTrack.append(Wait(2))
        suitTrack.append(doHeadRoller(attack, 3))
    return Parallel(suitTrack, toonTrack, cloudPropTrack, tauntInterval, soundTrack)


def doBuzzWord(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffects = []
    texturesList = ['buzzwords-crash',
     'buzzwords-inc',
     'buzzwords-main',
     'buzzwords-over',
     'buzzwords-syn']
    for i in xrange(0, 5):
        effect = BattleParticles.createParticleEffect('BuzzWord')
        if random.random() > 0.5:
            BattleParticles.setEffectTexture(effect, texturesList[i], color=Vec4(1, 0.94, 0.02, 1))
        else:
            BattleParticles.setEffectTexture(effect, texturesList[i], color=Vec4(0, 0, 0, 1))
        particleEffects.append(effect)

    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 2.25
    partDuration = 3
    damageDelay = 2.5
    dodgeDelay = 2.0
    suitName = suit.getStyleName()
    for effect in particleEffects:
        effect.setPos(0, 2.8, suit.getHeight() - 2.5)
        effect.setHpr(0, -20, 0)

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Level 6 Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                      "Quality Control has classified that all 8 gags are now classified as defective.",
                                      CFSpeech | CFTimeout))
    ceaseSpeechTrack3 = Parallel(Func(suit.setChatAbsolute,
                                      "Quality Control has classified that all 5 gags are now classified as defective.",
                                      CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'ste':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    elif attack['suit'].dna.name == 'frs':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack2))
    elif attack['suit'].dna.name == 'blr':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack3))
    particleTracks = []
    for effect in particleEffects:
        particleTracks.append(getPartTrack(effect, partDelay, partDuration, [effect, suit, 0]))

    toonTrack = getToonTrack(attack, damageDelay=damageDelay, damageAnimNames=['cringe'], splicedDodgeAnims=[['duck', dodgeDelay, 1.4]], showMissedExtraTime=dodgeDelay + 0.5)
    soundTrack = getSoundTrack('SA_buzz_word.ogg', delay=2.0, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, *particleTracks)


def doDemotion(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect('DemotionSpray')
    freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze')
    unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze')
    BattleParticles.setEffectTexture(sprayEffect, 'snow-particle')
    BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
    BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
    facePoint = __toonFacePoint(toon)
    freezeEffect.setPos(0, 0, facePoint.getZ())
    unFreezeEffect.setPos(0, 0, facePoint.getZ())
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTrack = getPartTrack(sprayEffect, 0.7, 1.1, [sprayEffect, suit, 0])
    partTrack2 = getPartTrack(freezeEffect, 1.4, 2.9, [freezeEffect, toon, 0])
    partTrack3 = getPartTrack(unFreezeEffect, 6.65, 0.5, [unFreezeEffect, toon, 0])
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
    toonTrack = getToonTrack(attack, damageDelay=1.0, splicedDamageAnims=damageAnims, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=1.3)
    soundTrack = getSoundTrack('SA_demotion.ogg', delay=1.2, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack)

def doDataBreach(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    partTracks = Parallel()
    partTracks2 = Parallel()
    partTracks3 = Parallel()
    partTracks4 = Parallel()
    for t in targets:
        BattleParticles.loadParticles()
        sprayEffect = BattleParticles.createParticleEffect('DemotionSpray2')
        sprayEffect2 = BattleParticles.createParticleEffect('DemotionSpray2')
        freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze2')
        unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze2')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle')
        BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
        BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
        toon = t['toon']
        dmg = t['hp']
        facePoint = __toonFacePoint(toon)
        freezeEffect.setPos(0, 0, facePoint.getZ())
        unFreezeEffect.setPos(0, 0, facePoint.getZ())
        partTrack = getPartTrack(sprayEffect, 0.7, 1.1, [sprayEffect, suit, 0])
        partTrack4 = getPartTrack(sprayEffect, 1.4, 2.9, [sprayEffect2, toon, 0])
        partTrack2 = getPartTrack(freezeEffect, 1.4, 2.9, [freezeEffect, toon, 0])
        partTrack3 = getPartTrack(unFreezeEffect, 6.65, 0.5, [unFreezeEffect, toon, 0])
        partTracks.append(partTrack)
        if dmg > 0:
            partTracks4.append(partTrack4)
            partTracks2.append(partTrack2)
            partTracks3.append(partTrack3)
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
    toonTrack = getToonTracks(attack, damageDelay=1.0, splicedDamageAnims=damageAnims, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=1.3)
    soundTrack = getSoundTrack('SA_dataBreach.ogg', delay=1.2, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, partTracks, partTracks2, partTracks3, partTracks4)


def doCanned(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.45
    suitType = getSuitBodyType(attack['suitName'])
    suitDelay = 1.23
    dodgeDelay = 2.6
    throwDuration = 1.5
    can = globalPropPool.getProp('can')
    explode = []
    scale = 26
    torso = toon.style.torso
    torso = torso[0]
    if torso == 's':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.9975)
    elif torso == 'm':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.7975)
    elif torso == 'l':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 2.31)
    canHpr = VBase3(-173.47, -0.42, 162.09)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.1, -0.175, 0), VBase3(-10.584, 11.945, -161.684)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, propDelay, Point3(9, 9, 9), scaleUpTime=0.25))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, can))
    throwTrack.append(getThrowTrack(can, hitPoint, duration=throwDuration, parent=battle))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    if dmg > 0:
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        dustTrack = Parallel(Func(splat.reparentTo, toon),
                             Sequence(ActorInterval(splat, splatName), Func(splat.detachNode)))
        can2 = MovieUtil.copyProp(can)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        can2Point = Point3(hitPoint.getX(), hitPoint.getY() + 6.4, hitPoint.getZ())
        can2.setPos(can2Point)
        can2.setScale(scaleUpPoint)
        can2.setHpr(canHpr)
        throwTrack.append(Func(battle.movie.needRestoreHips))
        throwTrack.append(Func(can.wrtReparentTo, hips1))
        throwTrack.append(Func(can2.reparentTo, hips2))
        throwTrack.append(Func(MovieUtil.removeProp, can2))
        throwTrack.append(Func(MovieUtil.removeProp, can))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        throwTrack.append(Parallel(explodeTrack, soundTrack))
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr))
        soundTrack = Sequence(Wait(1.2), SoundInterval(globalBattleSoundCache.getSound('SA_canned_tossup_only.ogg'), node=suit), SoundInterval(globalBattleSoundCache.getSound('SA_canned_impact_only.ogg'), node=suit))
    else:
        land = toon.getPos(battle)
        land.setZ(land.getZ() + 0.7)
        bouncePoint1 = Point3(land.getX(), land.getY() - 1.5, land.getZ() + 2.5)
        bouncePoint2 = Point3(land.getX(), land.getY() - 2.1, land.getZ() - 0.2)
        bouncePoint3 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 1.5)
        bouncePoint4 = Point3(land.getX(), land.getY() - 4.1, land.getZ() + 0.3)
        throwTrack.append(LerpPosInterval(can, 0.4, land))
        throwTrack.append(LerpPosInterval(can, 0.4, bouncePoint1))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint2))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint3))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint4))
        throwTrack.append(Wait(1.1))
        throwTrack.append(LerpScaleInterval(can, 0.3, MovieUtil.PNT3_NEARZERO))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, Point3(11, 11, 11)))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr), Wait(0.4), LerpHprInterval(can, 0.4, Point3(83.27, 19.52, -177.92)), LerpHprInterval(can, 0.3, Point3(95.24, -72.09, 88.65)), LerpHprInterval(can, 0.2, Point3(-96.34, -2.63, 179.89)))
        soundTrack = getSoundTrack('SA_canned_tossup_only.ogg', delay=1.7, node=suit)
    canTrack = Sequence(Parallel(throwTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, can), Func(battle.movie.clearRenderProp, can))
    damageAnims = [['struggle',
      propDelay + suitDelay + throwDuration,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=propDelay + suitDelay + 2.4)
    return Parallel(suitTrack, toonTrack, canTrack, soundTrack)

def doCannedPhase2(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.45
    suitType = getSuitBodyType(attack['suitName'])
    suitDelay = 1.23
    dodgeDelay = 2.6
    throwDuration = 1.5
    can = globalPropPool.getProp('can')
    scale = 26
    torso = toon.style.torso
    torso = torso[0]
    if torso == 's':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.9975)
    elif torso == 'm':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.7975)
    elif torso == 'l':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 2.31)
    canHpr = VBase3(-173.47, -0.42, 162.09)
    taunt = random.choice(
        ["'Can' you handle this?", "Do you like it out of the can?",
         "Ever been attacked by canned goods before?", "Get ready to 'Kick the can'!",
         "I'll throw you in the can!", "You think you 'can', you think you 'can'.",
         "I'm making me a can o' Toon-a!","This one's fresh out of the can!",
         "You don't taste so good out of the can."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'throw-object', playRate=1.5), Func(suit.setNeutralAnimation))
    phase2 = Func(suit.makeChainsawPhase2)
    ceaseTrack = ActorInterval(suit, 'rake-react')
    ceaseSpeechTrack = Sequence(Func(suit.setChatAbsolute,
                                     "PERSONALITY OVERRIDE ACTIVATED.",
                                     CFSpeech | CFTimeout), Wait(3.0), Func(suit.setChatAbsolute,
                                     "PLEASE WAIT.",
                                     CFSpeech | CFTimeout), ActorInterval(suit, 'lured'), ActorInterval(suit, 'lured'), Func(suit.setNeutralAnimation), Func(suit.setChatAbsolute,
                                     "PERSONALITY OVERRIDE COMPLETE.",
                                     CFSpeech | CFTimeout), Wait(3.0),  Func(suit.setChatAbsolute,
                                     "ADDITIONAL ENTITIES IDENTIFIED. TERMINATION SEQUENCE IN PROGRESS.", CFSpeech | CFTimeout), ActorInterval(suit, 'neutral-override'), Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(Parallel(ceaseTrack, phase2, ceaseSpeechTrack))
    taunt = random.choice(
        ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
         "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
         "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
    suitTrack.append(Func(suit.setChatAbsolute,
                          taunt,
                          CFSpeech | CFTimeout))
    suitTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
    suitTrack.append(Parallel(SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                              ActorInterval(suit, 'revvedup')))
    suitTrack.append(Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.1, -0.175, 0), VBase3(-10.584, 11.945, -161.684)]
    throwTrack = Sequence(
        getPropAppearTrack(can, suit.getRightHand(), posPoints, propDelay, Point3(9, 9, 9), scaleUpTime=0.25))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, can))
    throwTrack.append(getThrowTrack(can, hitPoint, duration=throwDuration, parent=battle))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    if dmg > 0:
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        dustTrack = Parallel(Func(splat.reparentTo, toon),
                             Sequence(ActorInterval(splat, splatName), Func(splat.detachNode)))
        can2 = MovieUtil.copyProp(can)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        can2Point = Point3(hitPoint.getX(), hitPoint.getY() + 6.4, hitPoint.getZ())
        can2.setPos(can2Point)
        can2.setScale(scaleUpPoint)
        can2.setHpr(canHpr)
        throwTrack.append(Func(battle.movie.needRestoreHips))
        throwTrack.append(Func(can.wrtReparentTo, hips1))
        throwTrack.append(Func(can2.reparentTo, hips2))
        throwTrack.append(Func(MovieUtil.removeProp, can2))
        throwTrack.append(Func(MovieUtil.removeProp, can))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        throwTrack.append(Parallel(explodeTrack, soundTrack))
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr))
        soundTrack = Sequence(Wait(1.2),
                              SoundInterval(globalBattleSoundCache.getSound('SA_canned_tossup_only.ogg'), node=suit),
                              SoundInterval(globalBattleSoundCache.getSound('SA_canned_impact_only.ogg'), node=suit))
    else:
        land = toon.getPos(battle)
        land.setZ(land.getZ() + 0.7)
        bouncePoint1 = Point3(land.getX(), land.getY() - 1.5, land.getZ() + 2.5)
        bouncePoint2 = Point3(land.getX(), land.getY() - 2.1, land.getZ() - 0.2)
        bouncePoint3 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 1.5)
        bouncePoint4 = Point3(land.getX(), land.getY() - 4.1, land.getZ() + 0.3)
        throwTrack.append(LerpPosInterval(can, 0.4, land))
        throwTrack.append(LerpPosInterval(can, 0.4, bouncePoint1))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint2))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint3))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint4))
        throwTrack.append(Wait(1.1))
        throwTrack.append(LerpScaleInterval(can, 0.3, MovieUtil.PNT3_NEARZERO))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, Point3(11, 11, 11)))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr), Wait(0.4), LerpHprInterval(can, 0.4, Point3(83.27, 19.52, -177.92)), LerpHprInterval(can, 0.3, Point3(95.24, -72.09, 88.65)), LerpHprInterval(can, 0.2, Point3(-96.34, -2.63, 179.89)))
        soundTrack = getSoundTrack('SA_canned_tossup_only.ogg', delay=1.7, node=suit)
    canTrack = Sequence(Parallel(throwTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, can), Func(battle.movie.clearRenderProp, can))
    damageAnims = [['struggle',
      propDelay + suitDelay + throwDuration,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=propDelay + suitDelay + 2.4)
    return Parallel(suitTrack, toonTrack, canTrack, soundTrack)

def doCannedScabbard(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)


    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    hips = toon.getHipsParts()
    propDelay = 0.45
    suitType = getSuitBodyType(attack['suitName'])
    suitDelay = 1.23
    dodgeDelay = 2.6
    throwDuration = 1.5
    can = globalPropPool.getProp('can')
    scale = 26
    torso = toon.style.torso
    torso = torso[0]
    if torso == 's':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.9975)
    elif torso == 'm':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.7975)
    elif torso == 'l':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 2.31)
    canHpr = VBase3(-173.47, -0.42, 162.09)
    if suit.isChainsawPhase3:
        taunt = random.choice(
            ["EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.",

             "WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
             "ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.", "ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED.",
             "EXECUTING- i- PROGRAM: 'KICK- can't- THE CAN' RO- help it- ROUTINE.",
             "ACTIVATING- don't- TOON-A- want- CAN SE- to- SEALING PRO- fight you- PROCESS."])
    else:
        taunt = random.choice(
            ["'Can' you handle this?", "Do you like it out of the can?",
             "Ever been attacked by canned goods before?", "Get ready to 'Kick the can'!",
             "I'll throw you in the can!", "You think you 'can', you think you 'can'.",
             "I'm making me a can o' Toon-a!", "This one's fresh out of the can!",
             "You don't taste so good out of the can."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doScabbard(attack))
    posPoints = [Point3(-0.1, -0.175, 0), VBase3(-10.584, 11.945, -161.684)]
    throwTrack = Sequence(
        getPropAppearTrack(can, suit.getRightHand(), posPoints, propDelay, Point3(9, 9, 9), scaleUpTime=0.25))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, can))
    throwTrack.append(getThrowTrack(can, hitPoint, duration=throwDuration, parent=battle))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    if dmg > 0:
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        dustTrack = Parallel(Func(splat.reparentTo, toon),
                             Sequence(ActorInterval(splat, splatName), Func(splat.detachNode)))
        can2 = MovieUtil.copyProp(can)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        can2Point = Point3(hitPoint.getX(), hitPoint.getY() + 6.4, hitPoint.getZ())
        can2.setPos(can2Point)
        can2.setScale(scaleUpPoint)
        can2.setHpr(canHpr)
        throwTrack.append(Func(battle.movie.needRestoreHips))
        throwTrack.append(Func(can.wrtReparentTo, hips1))
        throwTrack.append(Func(can2.reparentTo, hips2))
        throwTrack.append(Func(MovieUtil.removeProp, can2))
        throwTrack.append(Func(MovieUtil.removeProp, can))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        throwTrack.append(Parallel(explodeTrack, soundTrack))
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr))
        soundTrack = Sequence(Wait(1.2),
                              SoundInterval(globalBattleSoundCache.getSound('SA_canned_tossup_only.ogg'), node=suit),
                              SoundInterval(globalBattleSoundCache.getSound('SA_canned_impact_only.ogg'), node=suit))
    else:
        land = toon.getPos(battle)
        land.setZ(land.getZ() + 0.7)
        bouncePoint1 = Point3(land.getX(), land.getY() - 1.5, land.getZ() + 2.5)
        bouncePoint2 = Point3(land.getX(), land.getY() - 2.1, land.getZ() - 0.2)
        bouncePoint3 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 1.5)
        bouncePoint4 = Point3(land.getX(), land.getY() - 4.1, land.getZ() + 0.3)
        throwTrack.append(LerpPosInterval(can, 0.4, land))
        throwTrack.append(LerpPosInterval(can, 0.4, bouncePoint1))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint2))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint3))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint4))
        throwTrack.append(Wait(1.1))
        throwTrack.append(LerpScaleInterval(can, 0.3, MovieUtil.PNT3_NEARZERO))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, Point3(11, 11, 11)))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr), Wait(0.4), LerpHprInterval(can, 0.4, Point3(83.27, 19.52, -177.92)), LerpHprInterval(can, 0.3, Point3(95.24, -72.09, 88.65)), LerpHprInterval(can, 0.2, Point3(-96.34, -2.63, 179.89)))
        soundTrack = getSoundTrack('SA_canned_tossup_only.ogg', delay=1.7, node=suit)
    canTrack = Sequence(Parallel(throwTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, can), Func(battle.movie.clearRenderProp, can))
    damageAnims = [['struggle',
      propDelay + suitDelay + throwDuration,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=propDelay + suitDelay + 2.4)
    return Parallel(suitTrack, toonTrack, canTrack, soundTrack)

def doCannedOffboarding(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.45
    suitType = getSuitBodyType(attack['suitName'])
    suitDelay = 1.23
    dodgeDelay = 2.6
    throwDuration = 1.5
    can = globalPropPool.getProp('can')
    scale = 26
    torso = toon.style.torso
    torso = torso[0]
    if torso == 's':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.9975)
    elif torso == 'm':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 1.7975)
    elif torso == 'l':
        scaleUpPoint = Point3(scale * 2.63, scale * 2.63, scale * 2.31)
    canHpr = VBase3(-173.47, -0.42, 162.09)
    taunt = random.choice(
            ["EXECUTING- i- PROGRAM: 'KICK- can't- THE CAN' RO- help it- ROUTINE.", "ACTIVATING- don't- TOON-A- want- CAN SE- to- SEALING PRO- fight you- PROCESS.",
             "EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
"WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
"ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
"ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)

    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doOffboarding(attack, 2))
    posPoints = [Point3(-0.1, -0.175, 0), VBase3(-10.584, 11.945, -161.684)]
    throwTrack = Sequence(
        getPropAppearTrack(can, suit.getRightHand(), posPoints, propDelay, Point3(9, 9, 9), scaleUpTime=0.25))
    propDelay = propDelay + 0.5
    throwTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.1)
    hitPoint.setY(hitPoint.getY() - 0.5)
    hitPoint.setZ(hitPoint.getZ() + toon.height + 1.1)
    throwTrack.append(Func(battle.movie.needRestoreRenderProp, can))
    throwTrack.append(getThrowTrack(can, hitPoint, duration=throwDuration, parent=battle))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    if dmg > 0:
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        dustTrack = Parallel(Func(splat.reparentTo, toon),
                             Sequence(ActorInterval(splat, splatName), Func(splat.detachNode)))
        can2 = MovieUtil.copyProp(can)
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        can2Point = Point3(hitPoint.getX(), hitPoint.getY() + 6.4, hitPoint.getZ())
        can2.setPos(can2Point)
        can2.setScale(scaleUpPoint)
        can2.setHpr(canHpr)
        throwTrack.append(Func(battle.movie.needRestoreHips))
        throwTrack.append(Func(can.wrtReparentTo, hips1))
        throwTrack.append(Func(can2.reparentTo, hips2))
        throwTrack.append(Func(MovieUtil.removeProp, can2))
        throwTrack.append(Func(MovieUtil.removeProp, can))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        throwTrack.append(Parallel(explodeTrack, soundTrack))
        throwTrack.append(Wait(2.4))
        throwTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, scaleUpPoint))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr))
        soundTrack = Sequence(Wait(1.2),
                              SoundInterval(globalBattleSoundCache.getSound('SA_canned_tossup_only.ogg'), node=suit),
                              SoundInterval(globalBattleSoundCache.getSound('SA_canned_impact_only.ogg'), node=suit))
    else:
        land = toon.getPos(battle)
        land.setZ(land.getZ() + 0.7)
        bouncePoint1 = Point3(land.getX(), land.getY() - 1.5, land.getZ() + 2.5)
        bouncePoint2 = Point3(land.getX(), land.getY() - 2.1, land.getZ() - 0.2)
        bouncePoint3 = Point3(land.getX(), land.getY() - 3.1, land.getZ() + 1.5)
        bouncePoint4 = Point3(land.getX(), land.getY() - 4.1, land.getZ() + 0.3)
        throwTrack.append(LerpPosInterval(can, 0.4, land))
        throwTrack.append(LerpPosInterval(can, 0.4, bouncePoint1))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint2))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint3))
        throwTrack.append(LerpPosInterval(can, 0.3, bouncePoint4))
        throwTrack.append(Wait(1.1))
        throwTrack.append(LerpScaleInterval(can, 0.3, MovieUtil.PNT3_NEARZERO))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(can, throwDuration, Point3(11, 11, 11)))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(can, throwDuration, canHpr), Wait(0.4), LerpHprInterval(can, 0.4, Point3(83.27, 19.52, -177.92)), LerpHprInterval(can, 0.3, Point3(95.24, -72.09, 88.65)), LerpHprInterval(can, 0.2, Point3(-96.34, -2.63, 179.89)))
        soundTrack = getSoundTrack('SA_canned_tossup_only.ogg', delay=1.2, node=suit)
    canTrack = Sequence(Parallel(throwTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, can), Func(battle.movie.clearRenderProp, can))
    damageAnims = [['struggle',
      propDelay + suitDelay + throwDuration,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=propDelay + suitDelay + 2.4)
    return Parallel(suitTrack, toonTrack, canTrack, soundTrack)

def doOffboarding(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[ind]
    damageDelay = 1.7
    taunt = random.choice(
        ["DAMAGE TO COMPANY PROPERTY WILL BE MET WITH IMMEDIATE DISMISSAL.",
"RADIUS OF AFFECTED SUITS PROCESSED. ASSETS ARE CONSIDERED COMPROMISED.",
"NO ACTION TAKEN. EMPLOYEE IS DEEMED INEFFECTIVE.",
"DEARTH OF TARGETED ACTION PROCESSED. ELIMINATING OFFENSIVE COMPETITION.",
"EXPECTED EXPENSES TO MAINTAIN FORCES EXCEEDED. REDUCING MAINTENANCE COSTS.",
"EFFORT TO OUTPUT RATIO HIGHLY UNSTABLE. CONSOLIDATING FORCES...",
"IMPROPER USE OF TERMINATION AUTHORITY DETECTED.",
"EMPLOYEE WAS DISMISSED BY UNAUTHORIZED PARTY.",
            "IRREPARABLE DAMAGE TO EMPLOYEE SUSTAINED. REDIRECTING USEFULNESS.",
"DAMAGED EMPLOYEE IS NO LONGER OF VALUE TO THE COMPANY.",
"OFFENSIVE INACTION ANALYZED. REDUCING PROBABILITY OF TREND CONTINUATION.",
"ANOMALOUS TARGETING OBSERVED. REDIRECTION OF AGGRESSION SEQUENCE INITIATED.",
"PROJECTIONS WILL BE EXCEEDED ON CURRENT TRAJECTORY. ACTIVATING EXPENSE REDUCTION PROTOCOL.",
"SUBSTANTIAL SELF DEFENSE REQUIRED. REDUCING ENTITIES TO DEFEND.",
"RETALIATORY ACTION TAKEN AGAINST STRUCTURAL VIOLATIONS.",
"UNAUTHORIZED TERMINATION DETECTED. DIVERTING ASSETS TO LOSS PREVENTION."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'snap'), Func(suit.setNeutralAnimation))
    suitResponseTrack = Sequence()
    showDamage = Sequence(Func(targetSuit.showHpTextTrap, -targetSuit.currHP, openEnded=0), Func(targetSuit.showHpString, "FIRED!", openEnded=0), Func(targetSuit.setHealthForMe, -targetSuit.currHP))
    updateHealthBar = Func(targetSuit.updateHealthBar, 0)
    cannon = loader.loadModel('phase_5/models/props/cannon_cog')
    barrel = cannon.find('**/cannon')
    barrel.setHpr(0, 90, 0)
    cannonHolder = render.attachNewNode('CannonHolder')
    cannon.reparentTo(cannonHolder)
    cannon.setPos(0, 0, -8.6)
    cannonHolder.setPos(targetSuit.getPos(render))
    cannonHolder.setHpr(targetSuit.getHpr(render))
    cannonAttachPoint = barrel.attachNewNode('CannonAttach')
    kapowAttachPoint = barrel.attachNewNode('kapowAttach')
    scaleFactor = 1.6
    iScale = 1 / scaleFactor
    barrel.setScale(scaleFactor, 1, scaleFactor)
    cannonAttachPoint.setScale(iScale, 1, iScale)
    cannonAttachPoint.setPos(0, 6.7, 0)
    kapowAttachPoint.setPos(0, -0.5, 1.9)
    targetSuit.reparentTo(cannonAttachPoint)
    targetSuit.setPos(0, 0, 0)
    targetSuit.setHpr(0, -90, 0)
    suitLevel = targetSuit.getActualLevel()
    if suitLevel > 12:
        suitLevel = 12
    deep = 2.5 + suitLevel * 0.2
    suitScale = 0.9
    import math
    suitScale = 0.9 - math.sqrt(suitLevel) * 0.1
    sival = []
    posInit = cannonHolder.getPos()
    posFinal = Point3(posInit[0] + 0.0, posInit[1] + 0.0, posInit[2] + 7.0)
    kapow = globalPropPool.getProp('kapow')
    kapow.reparentTo(kapowAttachPoint)
    kapow.hide()
    kapow.setScale(0.25)
    kapow.setBillboardPointEye()
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.reparentTo(cannonAttachPoint)
    smoke.setScale(0.5)
    smoke.hide()
    smoke.setBillboardPointEye()
    soundBomb = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_fire_alt.ogg')
    playSoundBomb = SoundInterval(soundBomb)
    soundFly = base.loader.loadSfx('phase_4/audio/sfx/firework_whistle_01.ogg')
    playSoundFly = SoundInterval(soundFly)
    soundCannonAdjust = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_adjust.ogg')
    playSoundCannonAdjust = SoundInterval(soundCannonAdjust, duration=0.6)
    soundCogPanic = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogafssm.ogg')
    playSoundCogPanic = SoundInterval(soundCogPanic)
    reactIval = Parallel(Sequence(Wait(0.0),
                                                                          LerpPosInterval(cannonHolder, 2.0, posFinal,
                                                                                          startPos=posInit,
                                                                                          blendType='easeInOut'),
                                                                          Parallel(LerpHprInterval(barrel, 0.6,
                                                                                                   Point3(0, 0, 0),
                                                                                                   startHpr=Point3(0,
                                                                                                                   90,
                                                                                                                   0),
                                                                                                   blendType='easeIn'),
                                                                                   playSoundCannonAdjust), Wait(2.0),
                                                                          Parallel(LerpHprInterval(barrel, 0.6,
                                                                                                   Point3(0, 90, 0),
                                                                                                   startHpr=Point3(0,
                                                                                                                   45,
                                                                                                                   0),
                                                                                                   blendType='easeIn'),
                                                                                   playSoundCannonAdjust),
                                                                          LerpPosInterval(cannonHolder, 1.0, posInit,
                                                                                          startPos=posFinal,
                                                                                          blendType='easeInOut')),
                         Sequence(Wait(0.0), Parallel(Sequence(ActorInterval(targetSuit, 'flail'), Func(targetSuit.setNeutralAnimation)), targetSuit.scaleInterval(1.0, suitScale),
                                                      LerpPosInterval(targetSuit, 0.25, Point3(0, -1.0, 0.0)),
                                                      Sequence(Wait(0.25), Parallel(playSoundCogPanic,
                                                                                    LerpPosInterval(targetSuit, 1.5,
                                                                                                    Point3(0, -deep,
                                                                                                           0.0),
                                                                                                    blendType='easeIn')))),
                                  Wait(2.5), Parallel(playSoundBomb, playSoundFly, Sequence(Func(smoke.show), Parallel(
                                 LerpScaleInterval(smoke, 0.5, 3),
                                 LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.hide)),
                                                      Sequence(Func(kapow.show),
                                                               ActorInterval(kapow, 'kapow'), Func(kapow.hide)),
                                                      LerpPosInterval(targetSuit, 3.0, Point3(0, 150.0, 0.0)),
                                                      targetSuit.scaleInterval(3.0, 0.01)), Func(targetSuit.hide)))
    sival = Sequence(Parallel(reactIval, MovieUtil.createSuitStunIntervalFired(targetSuit, 0.3, 1.3)))
    suitResponseTrack.append(Wait(0.5))
    suitResponseTrack.append(showDamage)
    suitResponseTrack.append(updateHealthBar)
    suitResponseTrack.append(sival)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    damageAnims = [['slip-forward']]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTrack(attack, damageDelay=6.0, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=0)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=5.0, node=suit)
    return Parallel(suitTrack, suitResponseTrack, toonTracks, soundTrack1, soundTrack)

def doQuakeLayoffs(attack): # stomp
    tauntIndex = attack['taunt']
    taunt = random.choice(
        ["UNCHARTED NUMBERS DETECTED ON THE RICHTER SCALE."
"COMMENCING OPERATION: QUAKE, RATTLE AND ROLL."])
    suit = attack['suit']
    suitTrack = Sequence(ActorInterval(suit, 'quick-jump'), Func(suit.setNeutralAnimation))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doLayoffs(attack))
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    soundTrack = getSoundTrack('SA_quake.ogg', node=suit)
    return Parallel(suitTrack, soundTrack, tauntInterval, toonTracks)

def doLayoffs(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    damageDelay = 1.7
    taunt = random.choice(
        ["MASS PRODUCTION OF TERMINATION NOTICES REQUESTED.",
         "EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT.",
         "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
                       "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.",
                       "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED.",
"UNDERPERFORMING DIVISIONS WILL BE ELIMINATED AT-WILL."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'layoffs', endTime=1.75), Wait(2), ActorInterval(suit, 'layoffs', startTime=1.75), Func(suit.setNeutralAnimation))
    suitResponseTracks = Parallel()
    for targetSuit in battle.activeSuits:
        if not targetSuit.dna.name == 'cry' and not targetSuit.dna.name == 'tcm' and not targetSuit.dna.name == 'otm' and not targetSuit.dna.name == 'dvk':
            suitResponseTrack = Sequence()
            showDamage = Sequence(Func(targetSuit.showHpTextTrap, -targetSuit.currHP, openEnded=0), Func(targetSuit.showHpString, "FIRED!", openEnded=0), Func(targetSuit.setHealthForMe, -targetSuit.currHP))
            updateHealthBar = Func(targetSuit.updateHealthBar, 0)
            cannon = loader.loadModel('phase_5/models/props/cannon_cog')
            barrel = cannon.find('**/cannon')
            barrel.setHpr(0, 90, 0)
            cannonHolder = render.attachNewNode('CannonHolder')
            cannon.reparentTo(cannonHolder)
            cannon.setPos(0, 0, -8.6)
            cannonHolder.setPos(targetSuit.getPos(render))
            cannonHolder.setHpr(targetSuit.getHpr(render))
            cannonAttachPoint = barrel.attachNewNode('CannonAttach')
            kapowAttachPoint = barrel.attachNewNode('kapowAttach')
            scaleFactor = 1.6
            iScale = 1 / scaleFactor
            barrel.setScale(scaleFactor, 1, scaleFactor)
            cannonAttachPoint.setScale(iScale, 1, iScale)
            cannonAttachPoint.setPos(0, 6.7, 0)
            kapowAttachPoint.setPos(0, -0.5, 1.9)
            targetSuit.reparentTo(cannonAttachPoint)
            targetSuit.setPos(0, 0, 0)
            targetSuit.setHpr(0, -90, 0)
            suitLevel = targetSuit.getActualLevel()
            if suitLevel > 12:
                suitLevel = 12
            deep = 2.5 + suitLevel * 0.2
            suitScale = 0.9
            import math
            suitScale = 0.9 - math.sqrt(suitLevel) * 0.1
            sival = []
            posInit = cannonHolder.getPos()
            posFinal = Point3(posInit[0] + 0.0, posInit[1] + 0.0, posInit[2] + 7.0)
            kapow = globalPropPool.getProp('kapow')
            kapow.reparentTo(kapowAttachPoint)
            kapow.hide()
            kapow.setScale(0.25)
            kapow.setBillboardPointEye()
            smoke = loader.loadModel('phase_4/models/props/test_clouds')
            smoke.reparentTo(cannonAttachPoint)
            smoke.setScale(0.5)
            smoke.hide()
            smoke.setBillboardPointEye()
            soundBomb = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_fire_alt.ogg')
            playSoundBomb = SoundInterval(soundBomb)
            soundFly = base.loader.loadSfx('phase_4/audio/sfx/firework_whistle_01.ogg')
            playSoundFly = SoundInterval(soundFly)
            soundCannonAdjust = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_adjust.ogg')
            playSoundCannonAdjust = SoundInterval(soundCannonAdjust, duration=0.6)
            soundCogPanic = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogafssm.ogg')
            playSoundCogPanic = SoundInterval(soundCogPanic)
            reactIval = Parallel(Sequence(Wait(0.0),
                                  LerpPosInterval(cannonHolder, 2.0, posFinal,
                                                  startPos=posInit,
                                                  blendType='easeInOut'),
                                  Parallel(LerpHprInterval(barrel, 0.6,
                                                           Point3(0, 0, 0),
                                                           startHpr=Point3(0,
                                                                           90,
                                                                           0),
                                                           blendType='easeIn'),
                                           playSoundCannonAdjust), Wait(2.0),
                                  Parallel(LerpHprInterval(barrel, 0.6,
                                                           Point3(0, 90, 0),
                                                           startHpr=Point3(0,
                                                                           45,
                                                                           0),
                                                           blendType='easeIn'),
                                           playSoundCannonAdjust),
                                  LerpPosInterval(cannonHolder, 1.0, posInit,
                                                  startPos=posFinal,
                                                  blendType='easeInOut')),
                         Sequence(Wait(0.0),
                                  Parallel(Sequence(ActorInterval(targetSuit, 'flail'), Func(targetSuit.setNeutralAnimation)),
                                           targetSuit.scaleInterval(1.0, suitScale),
                                           LerpPosInterval(targetSuit, 0.25, Point3(0, -1.0, 0.0)),
                                           Sequence(Wait(0.25), Parallel(playSoundCogPanic,
                                                                         LerpPosInterval(targetSuit, 1.5,
                                                                                         Point3(0, -deep,
                                                                                                0.0),
                                                                                         blendType='easeIn')))),
                                  Wait(2.5), Parallel(playSoundBomb, playSoundFly, Sequence(Func(smoke.show), Parallel(
                                 LerpScaleInterval(smoke, 0.5, 3),
                                 LerpColorScaleInterval(smoke, 0.5, Vec4(2, 2, 2, 0))), Func(smoke.hide)),
                                                      Sequence(Func(kapow.show),
                                                               ActorInterval(kapow, 'kapow'), Func(kapow.hide)),
                                                      LerpPosInterval(targetSuit, 3.0, Point3(0, 150.0, 0.0)),
                                                      targetSuit.scaleInterval(3.0, 0.01)), Func(targetSuit.hide)))
            sival = Sequence(Parallel(reactIval, MovieUtil.createSuitStunIntervalFired(targetSuit, 0.3, 1.3)))
            suitResponseTrack.append(Wait(0.5))
            suitResponseTrack.append(showDamage)
            suitResponseTrack.append(updateHealthBar)
            suitResponseTrack.append(sival)
            suitResponseTracks.append(suitResponseTrack)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY() - 10, suitPos.getZ() + suit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(6.0))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    damageAnims = [['slip-forward']]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=6.0, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=0)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=5.0, node=suit)
    return Parallel(suitTrack, suitResponseTracks, soundTrack1, toonTracks)

def doScabbard(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    if suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "DECREASED- you- OFFENS- need to- OFFENSIVE PUSH AGAIN- destroy- AGAINST FODD- them- FODDER DETECTED.",

                "OVERFLOW- nothing- OF ASSETS NOT- done- NOTICED."])
    else:
        taunt = random.choice(
            ["All employees are receiving new benefits.",
             "You've done great work today, here's your bonus."])

    suitTracks = Sequence()
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    for headPart in suit.animatedHeadParts:
        headInterval = ActorInterval(headPart, 'scabbard')
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(2.5))
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpText, 0))
            suitTrack.append(Func(suit.showHpString, "SCABBARD!"))
        elif not suit.isManager:
            suitTrack.append(Func(suit.showHpTextCheat, x))
            suitTrack.append(Func(suit.showHpString, "SCABBARD!"))
            suitTrack.append(Func(suit.setHealthForMe, x))
        else:
            pass
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'otm' and not suit.dna.name == 'tcm' and not suit.dna.name == 'cry' and not suit.dna.name == 'dvk':
            suitTrack.append(Parallel(Sequence(Wait(4.0)),
                                      Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                           CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
        suitTracks.append(Parallel(tauntInterval, headInterval, ActorInterval(theSuit, 'scabbard')))
        suitTracks.append(Func(suit.setNeutralAnimation))
        suitTracks.append(Func(suit.setChatAbsolute, '',
                                           CFSpeech | CFTimeout))
        suitTracks.append(Wait(2.5))
    soundTrack2 = getSoundTrack('SA_scabbard.ogg', node=suit)
    return Parallel(suitTracks, soundTrack2)


def doDownsize(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.5
    sprayEffect = BattleParticles.createParticleEffect(file='downsizeSpray')
    cloudEffect = BattleParticles.createParticleEffect(file='downsizeCloud')
    toonPos = toon.getPos(toon)
    cloudPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.getHeight() * 0.55)
    cloudEffect.setPos(cloudPos)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.28, [sprayEffect, suit, 0])
    cloudTrack = getPartTrack(cloudEffect, 2.1, 1.9, [cloudEffect, toon, 0])
    if dmg > 0:
        initialScale = toon.getScale()
        downScale = Vec3(0.4, 0.4, 0.4)
        shrinkTrack = Sequence(Wait(damageDelay + 0.5), Func(battle.movie.needRestoreToonScale), LerpScaleInterval(toon, 1.0, downScale * 1.1), LerpScaleInterval(toon, 0.1, downScale * 0.9), LerpScaleInterval(toon, 0.1, downScale * 1.05), LerpScaleInterval(toon, 0.1, downScale * 0.95), LerpScaleInterval(toon, 0.1, downScale), Wait(2.1), LerpScaleInterval(toon, 0.5, initialScale * 1.5), LerpScaleInterval(toon, 0.15, initialScale * 0.5), LerpScaleInterval(toon, 0.15, initialScale * 1.2), LerpScaleInterval(toon, 0.15, initialScale * 0.8), LerpScaleInterval(toon, 0.15, initialScale), Func(battle.movie.clearRestoreToonScale))
    damageAnims = []
    damageAnims.append(['juggle',
     0.01,
     0.87,
     0.5])
    damageAnims.append(['lose',
     0.01,
     2.17,
     0.93])
    damageAnims.append(['lose',
     0.01,
     3.1,
     -0.93])
    damageAnims.append(['struggle',
     0.01,
     0.8,
     1.8])
    damageAnims.append(['sidestep-right',
     0.01,
     2.97,
     1.49])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.6, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_head_shrink_only.ogg', delay=2, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, sprayTrack, cloudTrack, shrinkTrack, soundTrack, toonTrack)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack)

def doVersionControl(attack):
    suit = attack['suit']
    battle = attack['battle']
    damageDelay = 1.5
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    shrinkTracks = Parallel()
    cloudTracks = Parallel()
    sprayTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sprayEffect = BattleParticles.createParticleEffect(file='downsizeSpray2')
        cloudEffect = BattleParticles.createParticleEffect(file='downsizeCloud2')
        toonPos = toon.getPos(toon)
        cloudPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.getHeight() * 0.55)
        cloudEffect.setPos(cloudPos)
        sprayTrack = getPartTrack(sprayEffect, 1.0, 1.28, [sprayEffect, suit, 0])
        cloudTrack = getPartTrack(cloudEffect, 2.1, 1.9, [cloudEffect, toon, 0])
        if dmg > 0:
            initialScale = toon.getScale()
            downScale = Vec3(0.4, 0.4, 0.4)
            shrinkTrack = Sequence(Wait(damageDelay + 0.5), Func(battle.movie.needRestoreToonScale),
                                   LerpScaleInterval(toon, 1.0, downScale * 1.1),
                                   LerpScaleInterval(toon, 0.1, downScale * 0.9),
                                   LerpScaleInterval(toon, 0.1, downScale * 1.05),
                                   LerpScaleInterval(toon, 0.1, downScale * 0.95),
                                   LerpScaleInterval(toon, 0.1, downScale), Wait(2.1),
                                   LerpScaleInterval(toon, 0.5, initialScale * 1.5),
                                   LerpScaleInterval(toon, 0.15, initialScale * 0.5),
                                   LerpScaleInterval(toon, 0.15, initialScale * 1.2),
                                   LerpScaleInterval(toon, 0.15, initialScale * 0.8),
                                   LerpScaleInterval(toon, 0.15, initialScale),
                                   Func(battle.movie.clearRestoreToonScale))
            shrinkTracks.append(shrinkTrack)
            cloudTracks.append(cloudTrack)
            sprayTracks.append(sprayTrack)
    damageAnims = []
    damageAnims.append(['juggle',
     0.01,
     0.87,
     0.5])
    damageAnims.append(['lose',
     0.01,
     2.17,
     0.93])
    damageAnims.append(['lose',
     0.01,
     3.1,
     -0.93])
    damageAnims.append(['struggle',
     0.01,
     0.8,
     1.8])
    damageAnims.append(['sidestep-right',
     0.01,
     2.97,
     1.49])
    toonTrack = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.6, dodgeAnimNames=['duck'])
    soundTrack = getSoundTrack('SA_head_shrink_only.ogg', delay=2, node=suit)
    return Parallel(suitTrack, sprayTracks, cloudTracks, shrinkTracks, soundTrack, toonTrack)


def doPinkSlip(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDelay = 2.43
    throwDuration = 0.5
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paper = globalPropPool.getProp('pink-slip')
        paperAppearTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, Point3(8, 8, 8), scaleUpTime=0.25))
        paperAppearTrack.append(Wait(0.93))
        hitPoint = __toonGroundPoint(attack, toon, 0.2, parent=battle)
        paperAppearTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperAppearTrack.append(Func(paper.wrtReparentTo, battle))
        paperAppearTrack.append(LerpPosInterval(paper, throwDuration, hitPoint))
        if dmg > 0:
            paperPause = 0.01
            slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ() + 4)
            landPoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(Wait(paperPause))
            paperAppearTrack.append(LerpPosInterval(paper, 0.2, slidePoint))
            paperAppearTrack.append(LerpPosInterval(paper, 1.1, landPoint))
            paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), Wait(paperPause), LerpHprInterval(paper, 1.3, VBase3(-200, 100, 100)))
        else:
            slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
            paperAppearTrack.append(LerpPosInterval(paper, 0.5, slidePoint))
            paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), LerpHprInterval(paper, 0.5, VBase3(10, 0, 0)))
        propTrack = Sequence()
        propTrack.append(Parallel(paperAppearTrack, paperSpinTrack))
        propTrack.append(LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
        propTrack.append(Func(MovieUtil.removeProp, paper))
        propTrack.append(Func(battle.movie.clearRenderProp, paper))
        propTracks.append(propTrack)

    damageAnims = [['jump',
      0.01,
      0.3,
      0.7], ['slip-forward', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.75, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['jump'], showDamageExtraTime=0.9)
    soundTrack = getSoundTrack('SA_pink_slip.ogg', delay=2.1, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack)

def doPinkSlipAftershock(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('pink-slip')
    throwDelay = 2.43
    throwDuration = 0.5
    taunt = getAttackTaunt('PinkSlip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'throw-paper', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doAfterShockChairman(attack))
    posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
    paperAppearTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, Point3(8, 8, 8), scaleUpTime=0.25))
    paperAppearTrack.append(Wait(0.93))
    hitPoint = __toonGroundPoint(attack, toon, 0.2, parent=battle)
    paperAppearTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperAppearTrack.append(Func(paper.wrtReparentTo, battle))
    paperAppearTrack.append(LerpPosInterval(paper, throwDuration, hitPoint))
    if dmg > 0:
        paperPause = 0.01
        slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ() + 4)
        landPoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
        paperAppearTrack.append(Wait(paperPause))
        paperAppearTrack.append(LerpPosInterval(paper, 0.2, slidePoint))
        paperAppearTrack.append(LerpPosInterval(paper, 1.1, landPoint))
        paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), Wait(paperPause), LerpHprInterval(paper, 1.3, VBase3(-200, 100, 100)))
    else:
        slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
        paperAppearTrack.append(LerpPosInterval(paper, 0.5, slidePoint))
        paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), LerpHprInterval(paper, 0.5, VBase3(10, 0, 0)))
    propTrack = Sequence()
    propTrack.append(Parallel(paperAppearTrack, paperSpinTrack))
    propTrack.append(LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, paper))
    propTrack.append(Func(battle.movie.clearRenderProp, paper))
    damageAnims = [['jump',
      0.01,
      0.3,
      0.7], ['slip-forward', 0.01]]
    toonTrack = getToonTrack(attack, damageDelay=1.75, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['jump'])
    soundTrack = getSoundTrack('SA_pink_slip.ogg', delay=2.1, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doPinkSlipCage(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('pink-slip')
    throwDelay = 2.43
    throwDuration = 0.5
    taunt = getAttackTaunt('PinkSlip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'throw-paper', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doCage(attack))
    posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
    paperAppearTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, Point3(8, 8, 8), scaleUpTime=0.25))
    paperAppearTrack.append(Wait(0.93))
    hitPoint = __toonGroundPoint(attack, toon, 0.2, parent=battle)
    paperAppearTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperAppearTrack.append(Func(paper.wrtReparentTo, battle))
    paperAppearTrack.append(LerpPosInterval(paper, throwDuration, hitPoint))
    if dmg > 0:
        paperPause = 0.01
        slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ() + 4)
        landPoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
        paperAppearTrack.append(Wait(paperPause))
        paperAppearTrack.append(LerpPosInterval(paper, 0.2, slidePoint))
        paperAppearTrack.append(LerpPosInterval(paper, 1.1, landPoint))
        paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), Wait(paperPause), LerpHprInterval(paper, 1.3, VBase3(-200, 100, 100)))
    else:
        slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
        paperAppearTrack.append(LerpPosInterval(paper, 0.5, slidePoint))
        paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), LerpHprInterval(paper, 0.5, VBase3(10, 0, 0)))
    propTrack = Sequence()
    propTrack.append(Parallel(paperAppearTrack, paperSpinTrack))
    propTrack.append(LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, paper))
    propTrack.append(Func(battle.movie.clearRenderProp, paper))
    damageAnims = [['jump',
      0.01,
      0.3,
      0.7], ['slip-forward', 0.01]]
    toonTrack = getToonTrack(attack, damageDelay=1.75, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['jump'])
    soundTrack = getSoundTrack('SA_pink_slip.ogg', delay=2.1, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doPinkSlipSnipe(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('pink-slip')
    throwDelay = 2.43
    throwDuration = 0.5
    taunt = getAttackTaunt('PinkSlip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'throw-paper', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doSnipeChairman(attack))
    posPoints = [Point3(-0.25, -0.35, 0), VBase3(-180, 0, 0)]
    paperAppearTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.8, Point3(8, 8, 8), scaleUpTime=0.25))
    paperAppearTrack.append(Wait(0.93))
    hitPoint = __toonGroundPoint(attack, toon, 0.2, parent=battle)
    paperAppearTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperAppearTrack.append(Func(paper.wrtReparentTo, battle))
    paperAppearTrack.append(LerpPosInterval(paper, throwDuration, hitPoint))
    if dmg > 0:
        paperPause = 0.01
        slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ() + 4)
        landPoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
        paperAppearTrack.append(Wait(paperPause))
        paperAppearTrack.append(LerpPosInterval(paper, 0.2, slidePoint))
        paperAppearTrack.append(LerpPosInterval(paper, 1.1, landPoint))
        paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), Wait(paperPause), LerpHprInterval(paper, 1.3, VBase3(-200, 100, 100)))
    else:
        slidePoint = Point3(hitPoint.getX(), hitPoint.getY() - 5, hitPoint.getZ())
        paperAppearTrack.append(LerpPosInterval(paper, 0.5, slidePoint))
        paperSpinTrack = Sequence(Wait(throwDelay), LerpHprInterval(paper, throwDuration, VBase3(300, 0, 0)), LerpHprInterval(paper, 0.5, VBase3(10, 0, 0)))
    propTrack = Sequence()
    propTrack.append(Parallel(paperAppearTrack, paperSpinTrack))
    propTrack.append(LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, paper))
    propTrack.append(Func(battle.movie.clearRenderProp, paper))
    damageAnims = [['jump',
      0.01,
      0.3,
      0.7], ['slip-forward', 0.01]]
    toonTrack = getToonTrack(attack, damageDelay=1.75, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['jump'])
    soundTrack = getSoundTrack('SA_pink_slip.ogg', delay=2.1, duration=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


def doReOrg(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.2
    attackDelay = 1.2
    sprayEffect = BattleParticles.createParticleEffect(file='reorgSpray')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Zap gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dsk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    partTrack = getPartTrack(sprayEffect, 0.5, 1.9, [sprayEffect, suit, 0])
    if dmg > 0:
        headParts = toon.getHeadParts()
        print '***********headParts pos=', headParts[0].getPos()
        print '***********headParts hpr=', headParts[0].getHpr()
        headTracks = Parallel()
        for partNum in xrange(0, headParts.getNumPaths()):
            part = headParts.getPath(partNum)
            x = part.getX()
            y = part.getY()
            z = part.getZ()
            h = part.getH()
            p = part.getP()
            r = part.getR()
            headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)), LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)), LerpHprInterval(part, 0.25, VBase3(360, 0, 180)), LerpPosInterval(part, 0.25, Point3(x, y, z + 3.1)), LerpPosInterval(part, 0.1, Point3(x, y, z + 0.3)), Wait(0.1), LerpHprInterval(part, 0.35, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)), LerpHprInterval(part, 0.5, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)), LerpPosInterval(part, 0.15, Point3(x, y, z + 1)), LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2), LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.1)))

        def getChestTrack(part, attackDelay = attackDelay):
            origScale = part.getScale()
            return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1), LerpHprInterval(part, 1.1, part.getHpr()))

        chestTracks = Parallel()
        arms = toon.findAllMatches('**/arms')
        sleeves = toon.findAllMatches('**/sleeves')
        hands = toon.findAllMatches('**/hands')
        print '*************arms hpr=', arms[0].getHpr()
        for partNum in xrange(0, arms.getNumPaths()):
            chestTracks.append(getChestTrack(arms.getPath(partNum)))
            chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
            chestTracks.append(getChestTrack(hands.getPath(partNum)))

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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01, dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    if dmg > 0:
        return Parallel(suitTrack, partTrack, toonTrack, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, partTrack, toonTrack)

def doReOrgBreachOfContract(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.2
    attackDelay = 1.2
    sprayEffect = BattleParticles.createParticleEffect(file='reorgSpray')
    battle = attack['battle']
    toon = target[0]['toon']
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('ReOrg', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'magic3', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doBreachOfContractMarked(attack))
    partTrack = getPartTrack(sprayEffect, 0.5, 1.9, [sprayEffect, suit, 0])
    if dmg > 0:
        headParts = toon.getHeadParts()
        print '***********headParts pos=', headParts[0].getPos()
        print '***********headParts hpr=', headParts[0].getHpr()
        headTracks = Parallel()
        for partNum in xrange(0, headParts.getNumPaths()):
            part = headParts.getPath(partNum)
            x = part.getX()
            y = part.getY()
            z = part.getZ()
            h = part.getH()
            p = part.getP()
            r = part.getR()
            headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)), LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)), LerpHprInterval(part, 0.25, VBase3(360, 0, 180)), LerpPosInterval(part, 0.25, Point3(x, y, z + 3.1)), LerpPosInterval(part, 0.1, Point3(x, y, z + 0.3)), Wait(0.1), LerpHprInterval(part, 0.35, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)), LerpHprInterval(part, 0.5, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)), LerpPosInterval(part, 0.15, Point3(x, y, z + 1)), LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2), LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.1)))

        def getChestTrack(part, attackDelay = attackDelay):
            origScale = part.getScale()
            return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1), LerpHprInterval(part, 1.1, part.getHpr()))

        chestTracks = Parallel()
        arms = toon.findAllMatches('**/arms')
        sleeves = toon.findAllMatches('**/sleeves')
        hands = toon.findAllMatches('**/hands')
        print '*************arms hpr=', arms[0].getHpr()
        for partNum in xrange(0, arms.getNumPaths()):
            chestTracks.append(getChestTrack(arms.getPath(partNum)))
            chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
            chestTracks.append(getChestTrack(hands.getPath(partNum)))

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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01, dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    if dmg > 0:
        return Parallel(suitTrack, partTrack, toonTrack, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, partTrack, toonTrack)

def doReOrgUnionBust(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.2
    attackDelay = 1.2
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    sprayEffect = BattleParticles.createParticleEffect(file='reorgSpray')
    taunt = getAttackTaunt('ReOrg', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'magic3', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doUnionBust(attack, 2))
    partTrack = getPartTrack(sprayEffect, 0.5, 1.9, [sprayEffect, suit, 0])
    if dmg > 0:
        headParts = toon.getHeadParts()
        print '***********headParts pos=', headParts[0].getPos()
        print '***********headParts hpr=', headParts[0].getHpr()
        headTracks = Parallel()
        for partNum in xrange(0, headParts.getNumPaths()):
            part = headParts.getPath(partNum)
            x = part.getX()
            y = part.getY()
            z = part.getZ()
            h = part.getH()
            p = part.getP()
            r = part.getR()
            headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)), LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)), LerpHprInterval(part, 0.25, VBase3(360, 0, 180)), LerpPosInterval(part, 0.25, Point3(x, y, z + 3.1)), LerpPosInterval(part, 0.1, Point3(x, y, z + 0.3)), Wait(0.1), LerpHprInterval(part, 0.35, VBase3(-745, 0, 180), startHpr=VBase3(0, 0, 180)), LerpHprInterval(part, 0.5, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)), LerpPosInterval(part, 0.15, Point3(x, y, z + 1)), LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2), LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.1)))

        def getChestTrack(part, attackDelay = attackDelay):
            origScale = part.getScale()
            return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1), LerpHprInterval(part, 1.1, part.getHpr()))

        chestTracks = Parallel()
        arms = toon.findAllMatches('**/arms')
        sleeves = toon.findAllMatches('**/sleeves')
        hands = toon.findAllMatches('**/hands')
        print '*************arms hpr=', arms[0].getHpr()
        for partNum in xrange(0, arms.getNumPaths()):
            chestTracks.append(getChestTrack(arms.getPath(partNum)))
            chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
            chestTracks.append(getChestTrack(hands.getPath(partNum)))

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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01, dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    if dmg > 0:
        return Parallel(suitTrack, partTrack, toonTrack, headTracks, chestTracks)
    else:
        return Parallel(suitTrack, partTrack, toonTrack)

def doSacked(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    hips = toon.getHipsParts()
    propDelay = 0.45
    suitDelay = 1.43
    throwDuration = 0.5
    sack = globalPropPool.getProp('sandbag')
    initialScale = Point3(0.5, 0.5, 0.5)
    scaleUpPoint = Point3(0.5, 0.5, 0.5) * 4.0
    sackHpr = VBase3(0, 0, 0)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.35, 0, 0), VBase3(0, 180, 0)]
    sackAppearTrack = Sequence(getPropAppearTrack(sack, suit.getRightHand(), posPoints, propDelay, initialScale, scaleUpTime=0.25))
    propDelay = propDelay + 0.2
    sackAppearTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    if dmg > 0:
        hitPoint.setY(hitPoint.getY() + 0.9)
    else:
        hitPoint.setZ(hitPoint.getZ() - 0.2)
    sackAppearTrack.append(Func(battle.movie.needRestoreRenderProp, sack))
    sackAppearTrack.append(getThrowTrack(sack, hitPoint, duration=throwDuration, parent=battle))
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    if dmg > 0:
        sack2 = MovieUtil.copyProp(sack)
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode, toon, explodePosPoints, 0, Point3(3, 3, 3), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        hips1 = hips.getPath(2)
        hips2 = hips.getPath(1)
        sack2.hide()
        sack2.reparentTo(battle)
        sack2.setPos(Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ()))
        sack2.setScale(scaleUpPoint)
        sack2.setHpr(sackHpr)
        sackAppearTrack.append(Func(battle.movie.needRestoreHips))
        sackAppearTrack.append(Func(sack.wrtReparentTo, hips1))
        sackAppearTrack.append(Func(sack2.show))
        sackAppearTrack.append(Func(sack2.wrtReparentTo, hips2))
        sackAppearTrack.append(Func(MovieUtil.removeProp, sack2))
        sackAppearTrack.append(Func(MovieUtil.removeProp, sack))
        soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
        sackAppearTrack.append(Parallel(explodeTrack, soundTrack))
        sackAppearTrack.append(Wait(2.4))
        sackAppearTrack.append(Func(battle.movie.clearRestoreHips))
        scaleTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(sack, throwDuration, scaleUpPoint), Wait(1.8), LerpScaleInterval(sack, 0.3, MovieUtil.PNT3_NEARZERO))
        hprTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(sack, throwDuration, sackHpr))
        sackTrack = Sequence(Parallel(sackAppearTrack, scaleTrack, hprTrack), Func(MovieUtil.removeProp, sack), Func(battle.movie.clearRenderProp, sack))
    else:
        sackAppearTrack.append(Wait(1.1))
        sackAppearTrack.append(LerpScaleInterval(sack, 0.3, MovieUtil.PNT3_NEARZERO))
        sackTrack = Sequence(sackAppearTrack, Func(MovieUtil.removeProp, sack), Func(battle.movie.clearRenderProp, sack))
    damageAnims = [['struggle',
      0.01,
      0.01,
      0.7], ['slip-backward', 0.01, 0.45]]
    soundTrack = getSoundTrack('SA_sacked.ogg', node=suit)
    toonTrack = getToonTrack(attack, damageDelay=propDelay + suitDelay + throwDuration, splicedDamageAnims=damageAnims, dodgeDelay=1.0, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.8, showMissedExtraTime=0.8)
    return Parallel(suitTrack, toonTrack, soundTrack, sackTrack)


def doGlowerPower(attack):
    suit = attack['suit']
    battle = attack['battle']
    leftKnives = []
    rightKnives = []
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))

    suitTrack = getSuitTrack(attack)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Toon-Up gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dsk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks)

def doGlowerPowerPhase3(attack):
    suit = attack['suit']
    battle = attack['battle']
    leftKnives = []
    rightKnives = []
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))

    taunt = random.choice(
        ["PIERCING EYES HAVE BEEN ESTABLISHED.", "UPDATING PROCESSES... MUST STAY ON THE CUTTING EDGE!!",
         "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.", "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED.",
         "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
         "EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    phase3 = Func(suit.makeChainsawPhase3)
    ceaseTrack = ActorInterval(suit, 'throttle')
    for headPart in suit.animatedHeadParts:
        headInterval = ActorInterval(headPart, 'throttle')
        headInterval2 = ActorInterval(headPart, 'revvedup')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_throttle_break.ogg'), node=suit))
    ceaseSpeechTrack = Sequence(Func(suit.setChatAbsolute,
                                     "DAMAGE TO- help- TO- help- TO OVER- me- OVERRIDE DE- toons- DETECTED.",
                                     CFSpeech | CFTimeout), Wait(3.0), ActorInterval(suit, 'lured'), ActorInterval(suit, 'lured'), Func(suit.setChatAbsolute,
                                                                            "ENTERING- i'm- ENTER- trying to- RECOVERY MO- resist it- MODE.",
                                                                            CFSpeech | CFTimeout), Func(suit.setNeutralAnimation), Wait(3.0),
                                Func(suit.setChatAbsolute,
                                     "ACTIVATING- i don't- TEMP- know- TEMPORARY- if i- REFOREST- can- REFORESTATION MODE.",
                                     CFSpeech | CFTimeout), Parallel(headInterval, ceaseTrack, ceaseSoundTrack), phase3, Func(suit.setChatAbsolute,
                                     "OVERRIDE- it- SEVERE- hurts- SEVERELY DAMA- let- DAMAGED. ATTEMPT- me- ATTEMPTTING- OUT!! FINAL FALLBACK PROCEDURE.",
                                     CFSpeech | CFTimeout),
                                Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(ceaseSpeechTrack)
    taunt = random.choice(
        ["DAMAGE TO SHELL IDENTIFIED. RETALIATION WILL BE MET WITH EQUAL FORCE.",
         "OUTER LAYERS AT RISK. TAKING DEFENSIVE ACTION.",
         "THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER."])
    suitTrack.append(Wait(3.0))
    suitTrack.append(Func(suit.setChatAbsolute,
                          taunt,
                          CFSpeech | CFTimeout))
    suitTrack.append(Func(suit.showHpString, "1.05x DMG MULTIPLIER!"))
    suitTrack.append(Parallel(headInterval2, SoundInterval(base.loadSfx('phase_5/audio/sfx/SA_revving_up.ogg')),
                              ActorInterval(suit, 'revvedup')))
    suitTrack.append(Func(suit.setNeutralAnimation))
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks)

def doGlowerPowerContractEnforcement(attack):
    suit = attack['suit']
    battle = attack['battle']
    leftKnives = []
    rightKnives = []
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

    taunt = getAttackTaunt('GlowerPower', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'glower'), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doContractEnforcement(attack))
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks)

def doGlowerPowerCTS(attack):
    suit = attack['suit']
    battle = attack['battle']
    leftKnives = []
    rightKnives = []
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

    taunt = random.choice(
        ["PIERCING EYES- i'm looking- HAVE BEEN- for a- ESTABLI- way out- ESTABLISHED.", "UPDATING- no- PROCESSES... MUST- can't- MUST STAY ON THE- give in- CUTTING EDGE!!",
         "ADDITIONAL DAMAGE TO SUIT DETECTED, CONTINUITY PLAN ACTIVATED.", "ORDER TO ATTACK HAS BEEN RECEIVED AND PROCESSED.",
         "WARNING: 'GAG' HAS NO DEFINITION. IGNORING...",
         "EMPLOYEES ARE RESISTING TERMINATION, CONTINGENCY PROCEDURES ARE IN EFFECT."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'glower'), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doCutTheSlack(attack, 2))
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks)

def doCutTheSlack(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[ind]
    damageDelay = 1.7
    taunt = random.choice(
        ["FODDER HAS BECOME A LIABILITY, CONDENSING IMMEDIATELY.",
"ADDITIONAL RESOURCES DEPLETING. MOST USEFUL EMPLOYEE WILL RECEIVE ADDITIONAL BENEFITS.",
"REMOVAL OF LEAST EFFICIENT EMPLOYEES STARTING NOW.",
"INSTANCE AT CAPACITY, INCREASING EFFECTIVENESS.",
"ACT OF MARKING INDICATES STRENGTH. REDEVELOPMENT SEQUENCE ACTIVATED.",
         "SURVIVING ENTITIES MUST BE ELIMINATED WITH GREAT PREJUDICE.",
         "LOSSES INCREASING, PREEMPTIVELY TERMINATING WEAKEST LINKS.",
         "ASSESSMENT PROMOTES SUBDIVISION TO SINGULARITY. ACT OF COMBINATION IN PROGRESS.",
         "INSTANCE CONDITIONS RISK OVERLOAD. CONSOLIDATING MASSES.",
         "EMPLOYEE IS MARRED IN LITIGATION. FUNNELING RESOURCES TO LEGAL FUNDS.",
"EMPLOYEE IS MARRED IN LITIGATION. FUNNELING RESOURCES TO LEGAL FUNDS."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'snap'), Func(suit.setNeutralAnimation))
    selfDamageTrack = Sequence(Wait(1.5), Parallel(ActorInterval(targetSuit, 'slip-forward', startTime=2.43), Func(targetSuit.makeIntoCTSManager), Func(targetSuit.showHpString, "PROMOTION!"), Func(targetSuit.setMaxHP, 1500),
                               Func(targetSuit.setHP, 2000), Func(targetSuit.setManager, 1), Func(targetSuit.updateHealthBar, 0)), Func(targetSuit.setNeutralAnimation))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, selfDamageTrack, soundTrack)

def doCutTheSlackChairman(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[ind]
    damageDelay = 1.7
    taunt = random.choice(
        ["I've had enough of you cogs slacking off."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'snap'), Func(suit.setNeutralAnimation))
    selfDamageTrack = Sequence(Wait(1.5), Parallel(ActorInterval(targetSuit, 'slip-forward', startTime=2.43), Func(targetSuit.makeIntoCTSManager), Func(targetSuit.showHpString, "PROMOTION!"), Func(targetSuit.setMaxHP, 1000),
                               Func(targetSuit.setHP, 1500), Func(targetSuit.setManager, 1), Func(targetSuit.updateHealthBar, 0), Func(targetSuit.makeInsured)), Func(targetSuit.setNeutralAnimation))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, selfDamageTrack, soundTrack)

def doGlowerPowerSparkplug(attack):
    suit = attack['suit']
    battle = attack['battle']
    leftKnives = []
    rightKnives = []
    for i in xrange(0, 3):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

    if suit.isChainsawPhase3:
        taunt = random.choice(
            ["EMPLOYEES- i wi- ARE- i wish- RESISTING TERMI- wish i could- TERMINATION, CONTINGENCY- could stop- PROCEDURES ARE- it- IN EFFECT.", "WARNING- this wa- WARNING: 'GAG' HAS- wasn't my- NO DEFINIT- choice- DEFINITION. IGNORING...",
             "ADDITIONAL DAMAGE- i'm not- TO SUIT- in- DETECTED, CONTIN- in control of- CONTINUITY PLAN- my actions- ACTIVATED.", "ORDER- i'm- TO ATTACK HAS- i'm so- HAS BEEN RECEIVED AND- i'm sorry- PROCESSED.",
             "PIERCING EYES- i'm looking- HAVE BEEN- for a- ESTABLI- way out- ESTABLISHED.",
             "UPDATING- no- PROCESSES... MUST- can't- MUST STAY ON THE- give in- CUTTING EDGE!!"])
    else:
        taunt = random.choice(
        ["Here's looking at you, kid.", "How's this for expressive eyes?",
         "Jeepers Creepers, don't you love my peepers?", "I like to stay on the cutting edge.",
         "The eyes have it.",
         "Look into my eyes...",
         "Peekaboo, I see you."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'glower'), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doSparkplug(attack))
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 3):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks)

def doSparkplug(attack):
    suit = attack['suit']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    battle = attack['battle']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

    if suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "FALLBACK- no- PROCE- other- PROCEDURE ACT- action- ACTIVATED.",
                "OTHER- can't- ACTIONS- do- UNA- anything- UNAVAILABLE."])
    else:
        taunt = random.choice(
            ["Careful, this attack may 'shock' you.", "You could say I have a 'shocking' personality."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'sparkplug'), Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, tauntInterval, Parallel(headInterval, ActorInterval(suit, 'sparkplug')), suitReset,
                         Func(suit.setNeutralAnimation))
    suitTrack.append(Func(suit.makeUnShielding))
    cagePropTracks = Parallel()
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    cage = loader.loadModel('phase_5/models/props/lightning')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    #cage.setH(90)
    #cage.setPosHpr(0, 0, 0, 180, 0, 0)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(toonPos.getX(), y, 100.0), toon.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, .90, scaleUpPoint=Point3(4.0), scaleUpTime=3.5), Parallel(cagePosition),
            Parallel(
                cage.posInterval(0.1, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/AA_lightning.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg'), node=cage),
            Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 4.4, ['slip-forward'])
    notifyTrack = Sequence(Wait(4.4), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "SHOCKED!"))
    oldcolor = render.getColorScale()
    soundTrack = getSoundTrack('SA_sparkplug.ogg', node=suit)
    return Parallel(suitTrack, cagePropTracks, toonTrack, soundTrack, notifyTrack)

def doSnipe(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    leftKnives = []
    rightKnives = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(1.5))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 5):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))

    suitTrack = getSuitTrack(attack)
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 5):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    soundTrack2 = getSoundTrack('ENC_cogfall_apart.ogg', delay=1.5, node=suit)
    suitSpeechTrack = Sequence(Wait(2.5), Func(suit.setChatAbsolute, 'You better watch your back, our next few attacks will be very painful.', CFSpeech | CFTimeout))
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks, explosionTrack, soundTrack2, suitSpeechTrack)

def doSnipeHighRoller(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    leftKnives = []
    rightKnives = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(1.5))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 5):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))

    taunt = random.choice(
        ["And the ratingff FFKYROCKET!!!", "If it meanff anything, thiff iff gonna hurt me a lot more than it hurtff you!",
         "FForry, babe, but the ratingff don't lie! Thiff iff what the viewerff want!",
         "Who'ff ready for ffome cartoon violenffe?!", "Can't ffquaffh and fftretch your way out of thiff one, Toonff!"])
    suitTrack = Parallel(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 5):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    soundTrack2 = getSoundTrack('ENC_cogfall_apart.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks, explosionTrack, soundTrack2)

def doSnipeChairman(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    name = attack['id']
    leftKnives = []
    rightKnives = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(1.5))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 5):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))

    taunt = random.choice(
        ["Prepare for pain.", "Yikes, that one's gotta hurt."])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                     "So, I see you are very reliant on your Squirt gags. Let's see how you do without them.",
                                     CFSpeech | CFTimeout))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "So, I see you are very reliant on your Toon-Up gags. Let's see how you do without them.",
                                     CFSpeech | CFTimeout))
    if name == SLUSHFUND_2:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack2))
    if name == CHAINSAW_CANNED:
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 5):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    soundTrack2 = getSoundTrack('ENC_cogfall_apart.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks, explosionTrack, soundTrack2)

def doSnipeLureResistance(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    leftKnives = []
    rightKnives = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(1.5))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    for i in xrange(0, 5):
        leftKnives.append(globalPropPool.getProp('dagger'))
        rightKnives.append(globalPropPool.getProp('dagger'))
    taunt = getAttackTaunt('Caress', attack['suitName'])
    battle = attack['battle']
    toon = target[0]['toon']
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'glower'), suitReset, Func(suit.setNeutralAnimation))
    suitName = suit.getStyleName()
    if suitName == 'hh':
        leftPosPoints = [Point3(0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.3, 4.3, 5.3), MovieUtil.PNT3_ZERO]
    elif suitName == 'tbc':
        leftPosPoints = [Point3(0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.6, 4.5, 6), MovieUtil.PNT3_ZERO]
    else:
        leftPosPoints = [Point3(0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
        rightPosPoints = [Point3(-0.4, 6.0, 7.0), MovieUtil.PNT3_ZERO]
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    for i in xrange(0, 5):
        knifeDelay = 0.11
        leftTrack = Sequence()
        leftTrack.append(Wait(1.1))
        leftTrack.append(Wait(i * knifeDelay))
        leftTrack.append(getPropAppearTrack(leftKnives[i], suit, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        leftKnifeTracks.append(leftTrack)
        rightTrack = Sequence()
        rightTrack.append(Wait(1.1))
        rightTrack.append(Wait(i * knifeDelay))
        rightTrack.append(getPropAppearTrack(rightKnives[i], suit, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
        rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3))
        rightKnifeTracks.append(rightTrack)

    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonTrack = getToonTrack(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
    soundTrack2 = getSoundTrack('ENC_cogfall_apart.ogg', delay=1.5, node=suit)
    suitSpeechTrack = Sequence(Wait(2.5), Func(suit.setChatAbsolute, 'You better watch your back, our next few attacks will be very painful.', CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(doLureResist(attack))
    return Parallel(suitTrack, toonTrack, soundTrack, leftKnifeTracks, rightKnifeTracks, explosionTrack, soundTrack2, suitSpeechTrack)

def doGroupSnipe(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    suitTrack = doGlowerPower(attack)
    explosionTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(1.5))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        if dmg > 0:
            explosionTracks.append(explosionTrack)

    if hitAtleastOneToon > 0:
        soundTrack = getSoundTrack('ENC_cogfall_apart.ogg', delay=1.5, node=suit)
        suitSpeechTrack = Sequence(Wait(2.5), Func(suit.setChatAbsolute,
                                                   'You better watch your back, our next few attacks will be very painful.',
                                                   CFSpeech | CFTimeout))
        return Parallel(suitTrack, explosionTracks, soundTrack, suitSpeechTrack)
    else:
        return Parallel(suitTrack, explosionTracks)


def doHalfWindsor(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tie = globalPropPool.getProp('half-windsor')
    throwDelay = 1.25
    damageDelay = 2.25
    dodgeDelay = 2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-1, 0.5, -.1), VBase3(99, -90, -108.2)]
    tiePropTrack = getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.25)
    tiePropTrack.append(Wait(throwDelay))
    missPoint = __toonMissBehindPoint(toon, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    missPoint.setZ(missPoint.getZ() + 4)
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.1)
    hitPoint.setY(hitPoint.getY() - 0.7)
    hitPoint.setZ(hitPoint.getZ() + 0.9)
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
    tiePropTrack.append(getPropThrowTrack(attack, tie, [hitPoint], [missPoint], hitDuration=0.25, missDuration=0.8, missScaleDown=0.3, parent=battle))
    soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
    tiePropTrack.append(Parallel(explodeTrack, soundTrack))
    damageAnims = [['conked',
      0.01,
      0.01,
      0.4], ['cringe', 0.01, 0.7]]
    soundTrack = getSoundTrack('SA_half_windsor_throw.ogg', delay=2.0, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTrack, tiePropTrack, soundTrack)


def doHeadShrink(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.5
    dodgeDelay = 0.9
    shrinkSpray = BattleParticles.createParticleEffect(file='headShrinkSpray')
    shrinkCloud = BattleParticles.createParticleEffect(file='headShrinkCloud')
    shrinkDrop = BattleParticles.createParticleEffect(file='headShrinkDrop')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(shrinkSpray, 0.3, 1.4, [shrinkSpray, suit, 0])
    shrinkCloud.reparentTo(battle)
    adjust = 0.4
    x = toon.getX(battle)
    y = toon.getY(battle) - adjust
    z = 8
    shrinkCloud.setPos(Point3(x, y, z))
    shrinkDrop.setPos(Point3(0, 0 - adjust, 7.5))
    off = 0.7
    cloudPoints = [Point3(x + off, y, z),
     Point3(x + off / 2, y + off / 2, z),
     Point3(x, y + off, z),
     Point3(x - off / 2, y + off / 2, z),
     Point3(x - off, y, z),
     Point3(x - off / 2, y - off / 2, z),
     Point3(x, y - off, z),
     Point3(x + off / 2, y - off / 2, z),
     Point3(x + off, y, z),
     Point3(x, y, z)]
    circleTrack = Sequence()
    for point in cloudPoints:
        circleTrack.append(LerpPosInterval(shrinkCloud, 0.14, point, other=battle))

    cloudTrack = Sequence()
    cloudTrack.append(Wait(0.82))
    cloudTrack.append(Func(battle.movie.needRestoreParticleEffect, shrinkCloud))
    cloudTrack.append(Func(shrinkCloud.start, battle))
    cloudTrack.append(circleTrack)
    cloudTrack.append(circleTrack)
    cloudTrack.append(LerpFunctionInterval(shrinkCloud.setAlphaScale, fromData=1, toData=0, duration=0.7))
    cloudTrack.append(Func(shrinkCloud.cleanup))
    cloudTrack.append(Func(battle.movie.clearRestoreParticleEffect, shrinkCloud))
    shrinkDelay = 0.4
    shrinkDuration = 0.6
    shrinkTrack = Sequence()
    if dmg > 0:
        headParts = toon.getHeadParts()
        initialScale = headParts.getPath(0).getScale()[0]
        shrinkTrack.append(Wait(damageDelay + shrinkDelay))

        def scaleHeadParallel(scale, duration, headParts = headParts):
            headTracks = Parallel()
            for partNum in xrange(0, headParts.getNumPaths()):
                nextPart = headParts.getPath(partNum)
                headTracks.append(LerpScaleInterval(nextPart, duration, Point3(scale, scale, scale)))

            return headTracks

        shrinkTrack.append(Func(battle.movie.needRestoreHeadScale))
        shrinkTrack.append(scaleHeadParallel(0.6, shrinkDuration))
        shrinkTrack.append(Wait(1.0))
        shrinkTrack.append(scaleHeadParallel(initialScale * 3.2, 0.4))
        shrinkTrack.append(scaleHeadParallel(initialScale * 0.7, 0.4))
        shrinkTrack.append(scaleHeadParallel(initialScale * 2.5, 0.3))
        shrinkTrack.append(scaleHeadParallel(initialScale * 0.8, 0.3))
        shrinkTrack.append(scaleHeadParallel(initialScale * 1.9, 0.2))
        shrinkTrack.append(scaleHeadParallel(initialScale * 0.85, 0.2))
        shrinkTrack.append(scaleHeadParallel(initialScale * 1.7, 0.15))
        shrinkTrack.append(scaleHeadParallel(initialScale * 0.9, 0.15))
        shrinkTrack.append(scaleHeadParallel(initialScale * 1.3, 0.1))
        shrinkTrack.append(scaleHeadParallel(initialScale, 0.1))
        shrinkTrack.append(Func(battle.movie.clearRestoreHeadScale))
        shrinkTrack.append(Wait(0.7))
    dropTrack = getPartTrack(shrinkDrop, 1.0, 2.0, [shrinkDrop, toon, 0])
    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.65,
     0.2])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.64, 1.0, startTime=0.85))
    damageAnims.append(['cringe', 0.4, 1.49])
    damageAnims.append(['conked',
     0.01,
     3.6,
     -1.6])
    damageAnims.append(['conked',
     0.01,
     3.1,
     0.4])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    if dmg > 0:
        shrinkSound = globalBattleSoundCache.getSound('SA_head_shrink_only.ogg')
        growSound = globalBattleSoundCache.getSound('SA_head_grow_back_only.ogg')
        soundTrack = Sequence(Wait(1.5), SoundInterval(shrinkSound, duration=2.1, node=suit), SoundInterval(growSound, node=suit))
        return Parallel(suitTrack, sprayTrack, cloudTrack, dropTrack, toonTrack, shrinkTrack, soundTrack)
    else:
        return Parallel(suitTrack, sprayTrack, cloudTrack, dropTrack, toonTrack)


def doRolodex(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon'] # I normally do not want to, but I'll leave this because the only thing that really needs it is hitPoint, which is pretty much for nothing since Anesidora reveals Disney's Toontown Online cut out one of their Rolodex particles that would have used it.
    rollodex = globalPropPool.getProp('rollodex')
    particleEffect2 = BattleParticles.createParticleEffect(file='rollodexWaterfall')
    particleEffects3 = [BattleParticles.createParticleEffect(file='rollodexStream') for t in targets]
    suitType = getSuitBodyType(attack['suitName'])
    propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
    propScale = Point3(1.2, 1.2, 1.2)
    partDelay = 2.6
    part2Delay = 2.2
    part3Delay = 2.6
    partDuration = 1.6
    part2Duration = 1.3
    part3Duration = 1
    damageDelay = 3.0
    dodgeDelay = 1.9
    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    partTrack2 = getPartTrack(particleEffect2, part2Delay, part2Duration, [particleEffect2, suit, 0])
    partTracks3 = getPartTracks(attack, particleEffects3, part3Delay, part3Duration, 0)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 4.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_rolodex.ogg', delay=1.8, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Toon-Up Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                      "Quality Control has classified that all Trap gags are now classified as defective.",
                                      CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'csm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    elif attack['suit'].dna.name == 'fbd':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack2))
    return Parallel(suitTrack, toonTracks, propTrack, soundTrack, partTrack2, partTracks3)

def doRolodexBindings(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon']
    rollodex = globalPropPool.getProp('rollodex')
    particleEffect2 = BattleParticles.createParticleEffect(file='rollodexWaterfall')
    particleEffects3 = [BattleParticles.createParticleEffect(file='rollodexStream') for t in targets]
    suitType = getSuitBodyType(attack['suitName'])
    propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
    propScale = Point3(1.2, 1.2, 1.2)
    partDelay = 2.6
    part2Delay = 2.2
    part3Delay = 2.6
    partDuration = 1.6
    part2Duration = 1.3
    part3Duration = 1
    damageDelay = 3.0
    dodgeDelay = 1.9
    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    partTrack2 = getPartTrack(particleEffect2, part2Delay, part2Duration, [particleEffect2, suit, 0])
    partTracks3 = getPartTracks(attack, particleEffects3, part3Delay, part3Duration, 0)
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'roll-o-dex', playRate=1.25), Func(suit.setNeutralAnimation))
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 4.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_rolodex.ogg', delay=1.8, node=suit)
    suitTrack.append(Wait(1.0))
    suitTrack.append(doLegalBindings(attack))
    return Parallel(suitTrack, toonTracks, propTrack, tauntInterval, soundTrack, partTrack2, partTracks3)

def doRolodexAggrandized(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon']
    rollodex = globalPropPool.getProp('rollodex')
    particleEffect2 = BattleParticles.createParticleEffect(file='rollodexWaterfall')
    particleEffects3 = [BattleParticles.createParticleEffect(file='rollodexStream') for t in targets]
    suitType = getSuitBodyType(attack['suitName'])
    propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
    propScale = Point3(1.2, 1.2, 1.2)
    partDelay = 2.6
    part2Delay = 2.2
    part3Delay = 2.6
    partDuration = 1.6
    part2Duration = 1.3
    part3Duration = 1
    damageDelay = 3.0
    dodgeDelay = 1.9
    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    partTrack2 = getPartTrack(particleEffect2, part2Delay, part2Duration, [particleEffect2, suit, 0])
    partTracks3 = getPartTracks(attack, particleEffects3, part3Delay, part3Duration, 0)
    # Professor Control: No clue what to do here because it depends on the Chainsaw Consultant's phase.
    if suit.isChainsawPhase3:
        taunt = random.choice(
            [
                "ATTEMPTING- can't- TO LOCATE- hold- TARGET'S EMPLOY- out- EMPLOYMENT CARD.",

                "PROTOCOL FOR- hope- PEST EXT- is- EXTERMINATION HAS- paper- BEEN TRI- thin- TRIGGERED."])
    else:
        taunt = random.choice(
            ["Here's the number for a pest exterminator.", "I want to give you my card.",
             "I want to make sure we stay in touch.", "I'll let my fingers do the knocking.",
             "Is this how I can contact you?", "I've got you covered from A to Z.", "You'll flip over this.",
             "I've got your number right here.", "Take this for a spin.", "Your card's in here somewhere.",
             "Watch out for paper cuts."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'roll-o-dex', playRate=1.25), Func(suit.setNeutralAnimation))
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 4.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_rolodex.ogg', delay=1.8, node=suit)
    soundTrack2 = getSoundTrack('SA_scabbard.ogg', node=suit)
    for headPart in suit.animatedHeadParts:
        headInterval = ActorInterval(headPart, 'scabbard')
    suitTrack.append(Wait(3.0))
    suitTrack.append(Func(suit.makeShielding))
    if suit.isChainsawPhase3:
        taunt2 = random.choice(
            ["ADDITIONAL- not- SUPPORT EXTENDED TO- enough- DAMAGED EMPLOYEE.",
                "FODDER HAS- should- SURVIVED, ADMIRA- have- ADMIRABLE ACTION- destroyed- REWARDED.",
             "SOLE FODDER DETECTED, PRO- one- PROVIDING WITH INCREASED- left- FURNISHINGS.",
                "UNSUPPORTED- too- EMPLOYEE HAS- few- BEEN PROMOTED."])
    else:
        taunt2 = random.choice(
            ["I can't stand seeing my allies getting hurt.",
             "You don't think we're going down that easily, do you?"])
    suitTrack.append(Parallel(headInterval, soundTrack2, Func(suit.setChatAbsolute, taunt2, CFSpeech | CFTimeout), ActorInterval(suit, 'scabbard')))
    suitTrack.append(Func(suit.setChatAbsolute, '', CFSpeech | CFTimeout))
    return Parallel(suitTrack, toonTracks, propTrack, tauntInterval, soundTrack, partTrack2, partTracks3)

def doRolodexBookKeeping(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon']
    rollodex = globalPropPool.getProp('rollodex')
    particleEffect2 = BattleParticles.createParticleEffect(file='rollodexWaterfall')
    particleEffects3 = [BattleParticles.createParticleEffect(file='rollodexStream') for t in targets]
    suitType = getSuitBodyType(attack['suitName'])
    propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
    propScale = Point3(1.2, 1.2, 1.2)
    partDelay = 2.6
    part2Delay = 2.2
    part3Delay = 2.6
    partDuration = 1.6
    part2Duration = 1.3
    part3Duration = 1
    damageDelay = 3.0
    dodgeDelay = 1.9
    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    partTrack2 = getPartTrack(particleEffect2, part2Delay, part2Duration, [particleEffect2, suit, 0])
    partTracks3 = getPartTracks(attack, particleEffects3, part3Delay, part3Duration, 0)
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'roll-o-dex', playRate=1.25), Func(suit.setNeutralAnimation))
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 4.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_rolodex.ogg', delay=1.8, node=suit)
    suitTrack.append(Wait(1.0))
    suitTrack.append(doBookKeeping(attack))
    return Parallel(suitTrack, toonTracks, propTrack, tauntInterval, soundTrack, partTrack2, partTracks3)

def doRolodexMarkedWood(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toon = targets[0]['toon']
    rollodex = globalPropPool.getProp('rollodex')
    particleEffect2 = BattleParticles.createParticleEffect(file='rollodexWaterfall')
    particleEffects3 = [BattleParticles.createParticleEffect(file='rollodexStream') for t in targets]
    suitType = getSuitBodyType(attack['suitName'])
    propPosPoints = [Point3(-0.51, -0.03, -0.1), VBase3(89.673, 2.166, 177.786)]
    propScale = Point3(1.2, 1.2, 1.2)
    partDelay = 2.6
    part2Delay = 2.2
    part3Delay = 2.6
    partDuration = 1.6
    part2Duration = 1.3
    part3Duration = 1
    damageDelay = 3.0
    dodgeDelay = 1.9
    hitPoint = lambda toon = toon: __toonFacePoint(toon)
    partTrack2 = getPartTrack(particleEffect2, part2Delay, part2Duration, [particleEffect2, suit, 0])
    partTracks3 = getPartTracks(attack, particleEffect3, part3Delay, part3Duration, 0)
    battle = attack['battle']
    taunt = random.choice(
        ["OFFENSIVE ANOMALY HAS BEEN DETECTED, PUNISHING FROM POINT OF GREATEST RESISTANCE.", "UNAUTHORIZED PARTY HAS BEGUN TARGETED ACTION. REMOVAL OF GREATEST THREAT REQUIRED.",
         "ONE ANOMALY DEEMED AGGRESSIVE. PROTOCOL TO DISMISS THE ANOMALY ACTIVATED.", "UNSUPPORTED ACTION DETECTED, PUNISHMENT IN PROGRESS.",
         "THREATS HAVE BEGUN TO REPAIR THEMSELVES. TARGETING LARGEST THREAT.", "NON-INSTANCE ENTITY DETECTED, OVERCOMPENSATION ACTIVATED.",
        "THREAT IDENTIFIED. TERMINATION PROTOCOL INITIATED.", "BUG IN THE SYSTEM IDENTIFIED. ELIMINATION IMMINENT.",
        "TARGET HAS HIRED OUTSIDE CONSULTANCY. ADDING INJURY TO OBSERVED INSULT.", "UNAUTHORIZED OUTSOURCING OF JOB DETECTED. ACTIVATING DISCIPLINARY PROTOCOL.",
    "ALL TARGETS ARE RESISTING. PUNISHING PERCEIVED LEADER.", "MAJOR ANOMALY DETECTED. ISOLATING GREATEST CONTRIBUTOR."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'roll-o-dex', playRate=1.25), Func(suit.setNeutralAnimation))
    propTrack = getPropTrack(rollodex, suit.getLeftHand(), propPosPoints, 1e-06, 4.7, scaleUpPoint=propScale, anim=0, propName='rollodex', animDuration=0, animStartTime=0)
    toonTracks = getToonTracks(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTrack = getSoundTrack('SA_rolodex.ogg', delay=1.8, node=suit)
    suitTrack.append(Wait(3.0))
    suitTrack.append(doMarkedWood(attack))
    return Parallel(suitTrack, toonTracks, propTrack, tauntInterval, soundTrack, partTrack2, partTracks3)

def doMarkedWood(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    explode = []
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    dmg = target[0]['hp']
    tnt = loader.loadModel('phase_10/models/props/treekiller_log_center')
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = random.choice(["OFFENSIVE ANOMALY HAS BEEN DETECTED, PUNISHING FROM POINT OF GREATEST RESISTANCE.",
         "UNAUTHORIZED PARTY HAS BEGUN TARGETED ACTION. REMOVAL OF GREATEST THREAT REQUIRED.",
         "ONE ANOMALY DEEMED AGGRESSIVE. PROTOCOL TO DISMISS THE ANOMALY ACTIVATED.",
         "UNSUPPORTED ACTION DETECTED, PUNISHMENT IN PROGRESS.",
         "THREATS HAVE BEGUN TO REPAIR THEMSELVES. TARGETING LARGEST THREAT.",
        "NON-INSTANCE ENTITY DETECTED, OVERCOMPENSATION ACTIVATED.",
        "THREAT IDENTIFIED. TERMINATION PROTOCOL INITIATED.", "BUG IN THE SYSTEM IDENTIFIED. ELIMINATION IMMINENT.",
        "TARGET HAS HIRED OUTSIDE CONSULTANCY. ADDING INJURY TO OBSERVED INSULT.",
        "UNAUTHORIZED OUTSOURCING OF JOB DETECTED. ACTIVATING DISCIPLINARY PROTOCOL.",
        "ALL TARGETS ARE RESISTING. PUNISHING PERCEIVED LEADER.",
        "MAJOR ANOMALY DETECTED. ISOLATING GREATEST CONTRIBUTOR."])
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'throw-paper', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    posPoints = [Point3(0, 0, -0.25), VBase3(90, 0, 0)]
    propTrack = Sequence(
        getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.25, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
    propTrack.append(Wait(1.5))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 2.5, ['cringe'])
    soundTrack = getSoundTrack('SA_peeling_the_bark.ogg', delay=2.25, node=suit)
    notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextCheat, - int(dmg / 2)), Func(toon.showHpString, "MARKED!"))
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack, notifyTrack)

def doEvilEyeBellow(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    eye = globalPropPool.getProp('evil-eye')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    if suitName == 'cr':
        posPoints = [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'tf':
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'le':
        posPoints = [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    else:
        posPoints = [Point3(-0.4, 6.0, 7.0), VBase3(-155.0, -20.0, 0.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    eyeHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['glower',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('glower', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['glower', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)), Wait(eyeHoldDuration * 0.3), LerpHprInterval(eye, 0.02, Point3(205, 40, 0)), Wait(eyeHoldDuration * 0.7), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle))
    toonFace = __toonFacePoint(toon, parent=battle)
    if dmg > 0:
        lerpInterval = LerpPosInterval(eye, moveDuration, toonFace)
    else:
        lerpInterval = LerpPosInterval(eye, moveDuration, Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
    eyeMoveTrack = lerpInterval
    eyeRollTrack = LerpHprInterval(eye, moveDuration, Point3(0, 0, -180))
    eyePropTrack = Sequence(eyeAppearTrack, Parallel(eyeMoveTrack, eyeRollTrack), Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['cringe', 0.01, 0.3]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_evil_eye.ogg', delay=1.3, node=suit)
    suitTrack.append(Wait(1.0))
    suitTrack.append(doSnapBellow(attack))
    return Parallel(suitTrack, toonTrack, eyePropTrack, soundTrack)

def doEvilEyeBreachOfContract(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    eye = globalPropPool.getProp('evil-eye')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    if suitName == 'cr':
        posPoints = [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'tf':
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'le':
        posPoints = [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    else:
        posPoints = [Point3(-0.4, 6.0, 7.0), VBase3(-155.0, -20.0, 0.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    eyeHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['glower',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('glower', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['glower', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)), Wait(eyeHoldDuration * 0.3), LerpHprInterval(eye, 0.02, Point3(205, 40, 0)), Wait(eyeHoldDuration * 0.7), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle))
    toonFace = __toonFacePoint(toon, parent=battle)
    if dmg > 0:
        lerpInterval = LerpPosInterval(eye, moveDuration, toonFace)
    else:
        lerpInterval = LerpPosInterval(eye, moveDuration, Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
    eyeMoveTrack = lerpInterval
    eyeRollTrack = LerpHprInterval(eye, moveDuration, Point3(0, 0, -180))
    eyePropTrack = Sequence(eyeAppearTrack, Parallel(eyeMoveTrack, eyeRollTrack), Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['cringe', 0.01, 0.3]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_evil_eye.ogg', delay=1.3, node=suit)
    suitTrack.append(Wait(1.0))
    suitTrack.append(doBreachOfContractSoaked(attack))
    return Parallel(suitTrack, toonTrack, eyePropTrack, soundTrack)


def doEvilEye(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    eye = globalPropPool.getProp('evil-eye')
    damageDelay = 2.44
    dodgeDelay = 1.64
    suitName = suit.getStyleName()
    if suitName == 'cr':
        posPoints = [Point3(-0.46, 4.85, 5.28), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'tf':
        posPoints = [Point3(-0.4, 3.65, 5.01), VBase3(-155.0, -20.0, 0.0)]
    elif suitName == 'le':
        posPoints = [Point3(-0.64, 4.45, 5.91), VBase3(-155.0, -20.0, 0.0)]
    else:
        posPoints = [Point3(-0.4, 6.0, 7.0), VBase3(-155.0, -20.0, 0.0)]
    appearDelay = 0.8
    suitHoldStart = 1.06
    suitHoldStop = 1.69
    suitHoldDuration = suitHoldStop - suitHoldStart
    eyeHoldDuration = 1.1
    moveDuration = 1.1
    suitSplicedAnims = []
    suitSplicedAnims.append(['glower',
     0.01,
     0.01,
     suitHoldStart])
    suitSplicedAnims.extend(getSplicedLerpAnims('glower', suitHoldDuration, 1.1, startTime=suitHoldStart))
    suitSplicedAnims.append(['glower', 0.01, suitHoldStop])
    suitTrack = getSuitTrack(attack, splicedAnims=suitSplicedAnims)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Drop gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dsk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    eyeAppearTrack = Sequence(Wait(suitHoldStart), Func(__showProp, eye, suit, posPoints[0], posPoints[1]), LerpScaleInterval(eye, suitHoldDuration, Point3(11, 11, 11)), Wait(eyeHoldDuration * 0.3), LerpHprInterval(eye, 0.02, Point3(205, 40, 0)), Wait(eyeHoldDuration * 0.7), Func(battle.movie.needRestoreRenderProp, eye), Func(eye.wrtReparentTo, battle))
    toonFace = __toonFacePoint(toon, parent=battle)
    if dmg > 0:
        lerpInterval = LerpPosInterval(eye, moveDuration, toonFace)
    else:
        lerpInterval = LerpPosInterval(eye, moveDuration, Point3(toonFace.getX(), toonFace.getY() - 5, toonFace.getZ() - 2))
    eyeMoveTrack = lerpInterval
    eyeRollTrack = LerpHprInterval(eye, moveDuration, Point3(0, 0, -180))
    eyePropTrack = Sequence(eyeAppearTrack, Parallel(eyeMoveTrack, eyeRollTrack), Func(battle.movie.clearRenderProp, eye), Func(MovieUtil.removeProp, eye))
    damageAnims = [['duck',
      0.01,
      0.01,
      1.4], ['cringe', 0.01, 0.3]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, damageDelay=damageDelay, dodgeDelay=dodgeDelay, dodgeAnimNames=['duck'], showDamageExtraTime=1.7, showMissedExtraTime=1.7)
    soundTrack = getSoundTrack('SA_evil_eye.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, eyePropTrack, soundTrack)


def doPlayHardball(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    ball = globalPropPool.getProp('baseball')
    suitType = getSuitBodyType(attack['suitName'])
    suitDelay = 1.3
    damageDelay = 2.25
    dodgeDelay = 1.86
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ballPosPoints = [Point3(-0.25, 0.03, -0.31), VBase3(-1.152, 86.581, -76.784)]
    propTrack = Sequence(getPropAppearTrack(ball, suit.getRightHand(), ballPosPoints, 0.5, Point3(7, 7, 7), scaleUpTime=0.25))
    propTrack.append(Wait(suitDelay))
    propTrack.append(Func(battle.movie.needRestoreRenderProp, ball))
    propTrack.append(Func(ball.wrtReparentTo, battle))
    toonPos = toon.getPos(battle)
    x = toonPos.getX()
    y = toonPos.getY()
    z = toonPos.getZ()
    z = z + 0.2
    if dmg > 0:
        propTrack.append(LerpPosInterval(ball, 0.25, __toonFacePoint(toon, parent=battle)))
        propTrack.append(LerpPosInterval(ball, 0.5, Point3(x, y + 3, z)))
        propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y + 5, z + 2)))
        propTrack.append(LerpPosInterval(ball, 0.3, Point3(x, y + 6, z)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 7, z + 1)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 8, z)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 8.5, z + 0.6)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y + 9, z + 0.2)))
        propTrack.append(Wait(0.4))
        soundTrack = getSoundTrack('SA_hardball_impact_only.ogg', delay=1.8, node=suit)
    else:
        propTrack.append(LerpPosInterval(ball, 0.25, Point3(x, y + 2, z)))
        propTrack.append(LerpPosInterval(ball, 0.4, Point3(x, y - 1, z + 2)))
        propTrack.append(LerpPosInterval(ball, 0.3, Point3(x, y - 3, z)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 4, z + 1)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 5, z)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 5.5, z + 0.6)))
        propTrack.append(LerpPosInterval(ball, 0.1, Point3(x, y - 6, z + 0.2)))
        propTrack.append(Wait(0.4))
        soundTrack = getSoundTrack('SA_hardball.ogg', delay=1.8, node=suit)
    propTrack.append(LerpScaleInterval(ball, 0.3, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(MovieUtil.removeProp, ball))
    propTrack.append(Func(battle.movie.clearRenderProp, ball))
    damageAnims = [['conked',
      damageDelay,
      0.01,
      0.5], ['slip-backward', 0.01, 0.7]]
    toonTrack = getToonTrack(attack, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showDamageExtraTime=3.9)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)


def doPowerTie(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tie = globalPropPool.getProp('power-tie')
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1.25
    damageDelay = 2
    dodgeDelay = 1.75
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.8, 0.5, -0.25), VBase3(90, 90, 0)]
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
    tiePropTrack = Sequence(getPropAppearTrack(tie, suit.getRightHand(), posPoints, 0.5, Point3(3.5, 3.5, 3.5), scaleUpTime=0.25))
    tiePropTrack.append(Wait(throwDelay))
    tiePropTrack.append(Func(tie.setBillboardPointEye))
    tiePropTrack.append(getPropThrowTrack(attack, tie, [__toonFacePoint(toon)], [__toonGroundPoint(attack, toon, 0.1)], hitDuration=0.25, missDuration=0.8))
    soundTrack = getSoundTrack('LB_evidence_miss.ogg', node=suit)
    tiePropTrack.append(Parallel(explodeTrack, soundTrack))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    throwSound = getSoundTrack('SA_powertie_throw.ogg', delay=2, node=suit)
    if dmg > 0:
        hitSound = getSoundTrack('SA_powertie_impact.ogg', delay=2.4, node=suit)
        return Parallel(suitTrack, toonTrack, tiePropTrack, throwSound, hitSound)
    else:
        return Parallel(suitTrack, toonTrack, tiePropTrack, throwSound)


def doDoubleTalk(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('DoubleTalkLeft')
    particleEffect2 = BattleParticles.createParticleEffect('DoubleTalkRight')
    BattleParticles.setEffectTexture(particleEffect, 'doubletalk-double', color=Vec4(0, 1.0, 0.0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'doubletalk-good', color=Vec4(0, 1.0, 0.0, 1))
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 2.25
    damageDelay = 2.5
    dodgeDelay = 2.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, partDelay, 1.8, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay, 1.8, [particleEffect2, suit, 0])
    damageAnims = [['duck',
      0.01,
      0.4,
      1.05], ['cringe', 1e-06, 0.8]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
    soundTrack = getSoundTrack('SA_doubletalk.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, partTrack2, soundTrack)

def doDoubleTalkWhirlwind(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('DoubleTalkLeft')
    particleEffect2 = BattleParticles.createParticleEffect('DoubleTalkRight')
    BattleParticles.setEffectTexture(particleEffect, 'doubletalk-double', color=Vec4(0, 1.0, 0.0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'doubletalk-good', color=Vec4(0, 1.0, 0.0, 1))
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 2.25
    damageDelay = 2.5
    dodgeDelay = 2.25
    # Professor Control: No clue what's with the extra phrases (after the value proposition one), but until I figure that out I'll keep it like this.
    taunt = random.choice(
        ["Your services are no longer required here.", "Do you have the bandwidth for this?",
         "Allow me to reverbiagize.", "These words might be out of your grasp.", "You need to look on the bright side.",
         "Why don't I introduce you to my value proposition?", "I'm told I'm quite the thought leader.",
         "See if you can wrap your head around this!", "Full disclosure: You don't stand a chance.",
         "Let me show you some of my pain points."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'speak', playRate=1.5))
    suitTrack.append(Wait(3.0))
    suitTrack.append(doWhirlwind(attack))
    partTrack = getPartTrack(particleEffect, partDelay, 1.8, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay, 1.8, [particleEffect2, suit, 0])
    damageAnims = [['duck',
      0.01,
      0.4,
      1.05], ['cringe', 1e-06, 0.8]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
    soundTrack = getSoundTrack('SA_doubletalk.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, partTrack2, soundTrack)


def doFreezeAssets(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    snowEffect = BattleParticles.createParticleEffect('FreezeAssets')
    BattleParticles.setEffectTexture(snowEffect, 'snow-particle')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0.2
    damageDelay = 2
    dodgeDelay = 1.3
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), MovieUtil.PNT3_ZERO]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    cloudPropTrack.append(Wait(0.6))
    cloudPropTrack.append(LerpPosInterval(cloud, .5, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=2.1, cleanup=True))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.25, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 0.01, 1.6]]
    soundTrack = getSoundTrack('SA_freeze_assets_trim.ogg', delay=2.3, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.2)
    return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)

def doFreezeAssetsAftershock(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    snowEffect = BattleParticles.createParticleEffect('FreezeAssets')
    BattleParticles.setEffectTexture(snowEffect, 'snow-particle')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    partDelay = 0.2
    damageDelay = 2
    dodgeDelay = 1.3
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('FreezeAssets', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'glower', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    ceaseTrack = Parallel(Func(suit.makeInversion), ActorInterval(suit, 'transformation'))
    ceaseTrack.append(Sequence(Func(suit.showHpTextCheat, + 250), Func(suit.showHpString, "INVERSION!"),
                               Func(suit.setHealthForMe, 250), Func(suit.updateHealthBar, 0)))
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     random.choice(("You and I should know that time heals all wounds.", "You are not the only one who needs healing.")),
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvp':
        suitTrack.append(Wait(3.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 3, initialCloudHeight), MovieUtil.PNT3_ZERO]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.25))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    cloudPropTrack.append(Wait(0.6))
    cloudPropTrack.append(LerpPosInterval(cloud, .25, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(ParticleInterval(snowEffect, cloud, worldRelative=0, duration=2.1, cleanup=True))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['cringe',
      0.01,
      0.4,
      0.8], ['duck', 0.01, 1.6]]
    soundTrack = getSoundTrack('SA_freeze_assets_trim.ogg', delay=2.3, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.2)
    return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)


def doHotAir(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect('HotAir')
    baseFlameEffect = BattleParticles.createParticleEffect(file='firedBaseFlame')
    flameEffect = BattleParticles.createParticleEffect('FiredFlame')
    flecksEffect = BattleParticles.createParticleEffect('SpriteFiredFlecks')
    BattleParticles.setEffectTexture(sprayEffect, 'fire')
    BattleParticles.setEffectTexture(baseFlameEffect, 'fire')
    BattleParticles.setEffectTexture(flameEffect, 'fire')
    BattleParticles.setEffectTexture(flecksEffect, 'roll-o-dex', color=Vec4(0.95, 0.95, 0.0, 1))
    sprayDelay = 0.6
    flameDelay = 1.25
    flameDuration = 1.5
    flecksDelay = flameDelay + 0.8
    flecksDuration = flameDuration - 0.8
    damageDelay = 1.5
    dodgeDelay = 1.0
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTrack = getPartTrack(sprayEffect, sprayDelay, 2.3, [sprayEffect, suit, 0])
    baseFlameTrack = getPartTrack(baseFlameEffect, flameDelay, flameDuration, [baseFlameEffect, toon, 0])
    flameTrack = getPartTrack(flameEffect, flameDelay, flameDuration, [flameEffect, toon, 0])
    flecksTrack = getPartTrack(flecksEffect, flecksDelay, flecksDuration, [flecksEffect, toon, 0])

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

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(4.0))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(3.5))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
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
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=0.5, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, sprayTrack, soundTrack, baseFlameTrack, flameTrack, flecksTrack, colorTrack)
    else:
        return Parallel(suitTrack, toonTrack, sprayTrack, soundTrack)


def doPickPocket(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    bill = globalPropPool.getProp('1dollar')
    suitTrack = getSuitTrack(attack)
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55, scaleUpPoint=Point3(1.41, 1.41, 1.41))
    toonTrack = getToonTrack(attack, 0.6, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return multiTrackList

def doVoodooMagic(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 12.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 32)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    targetPos2 = toon.getPos(battle)
    headsUp2 = Func(suit.setHpr, battle, origHpr)
    moveTrack = Sequence(LerpPosInterval(suit, 0, sinkPos2, other=battle), headsUp, Wait(3.0), suitReset, Func(suit.setPos, battle, dropPos))
    suitTrack = Sequence(getSuitTrack(attack))
    dmg = target[0]['hp']
    bill = globalPropPool.getProp('1dollar')
    billPosPoints = [Point3(-0.01, 0.45, -0.25), VBase3(136.424, -46.434, -129.712)]
    billPropTrack = getPropTrack(bill, suit.getRightHand(), billPosPoints, 0.6, 0.55,
                                 scaleUpPoint=Point3(1.41, 1.41, 1.41))
    toonTrack = getToonTrack(attack, 0.6, ['cringe'], 0.01, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    if dmg > 0:
        soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=0.2, node=suit)
        multiTrackList.append(billPropTrack)
        multiTrackList.append(soundTrack)
    return Parallel(suitTrack, moveTrack, multiTrackList, toonTrack)
	
def doCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    if suit.dna.name == 'tld' and not suit.isSkeleton:
        return doHeadHonchoCigarSmoke(attack)
    elif suit.dna.name == 'ffm':
        return doFirestarterCigarSmoke(attack)
    else:
        pass
    BattleParticles.loadParticles()
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    cigar = globalPropPool.getProp('cigar')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    elif suitType == 'c':
        suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), ActorInterval(suit, attack['animName'], duration=4.25), Func(suit.setNeutralAnimation))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Throw Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'fbd':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.6, 2.6, scaleUpPoint=Point3(7.0, 7.0, 7.0))
    toonTrack = getToonTrack(attack, 2.55, ['cringe'], 2.0, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack)
    smokeTrack = getPartTrack(smoke, 2.45, 1.5, [smoke, suit, 0])
    multiTrackList.append(cigarPropTrack)
    multiTrackList.append(smokeTrack)

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

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.6))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(2.2))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        multiTrackList.append(colorTrack)
    return multiTrackList

def doCigarSmokePaperCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    if suit.dna.name == 'tld' and not suit.isSkeleton:
        return doHeadHonchoCigarSmoke(attack)
    elif suit.dna.name == 'ffm':
        return doFirestarterCigarSmoke(attack)
    else:
        pass
    BattleParticles.loadParticles()
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    cigar = globalPropPool.getProp('cigar')
    suitType = getSuitBodyType(attack['suitName'])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = random.choice(
            ["Hmph...", "Hrnhmpf...",
             "Hrm...",
             "Hm, hm..."])
    tauntInterval = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'cigar-smoke', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.0))
    suitTrack.append(doPaperCut(attack))
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.6, 2.6, scaleUpPoint=Point3(7.0, 7.0, 7.0))
    toonTrack = getToonTrack(attack, 2.55, ['cringe'], 2.0, ['sidestep'])
    multiTrackList = Parallel(suitTrack, toonTrack, tauntInterval)
    smokeTrack = getPartTrack(smoke, 2.45, 1.5, [smoke, suit, 0])
    multiTrackList.append(cigarPropTrack)
    multiTrackList.append(smokeTrack)

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

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.6))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(2.2))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        multiTrackList.append(colorTrack)
    return multiTrackList

def doFilibuster(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    battle = attack['battle']
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect4 = BattleParticles.createParticleEffect(file='filibusterSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect, 'filibuster-cut', color=color)
    BattleParticles.setEffectTexture(sprayEffect2, 'filibuster-fiscal', color=color)
    BattleParticles.setEffectTexture(sprayEffect3, 'filibuster-impeach', color=color)
    BattleParticles.setEffectTexture(sprayEffect4, 'filibuster-inc', color=color)
    partDelay = 0.3
    partDuration = 1.15
    damageDelay = 1.25
    dodgeDelay = 0.7
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTrack = getPartTrack(sprayEffect, partDelay, partDuration, [sprayEffect, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
    sprayTrack4 = getPartTrack(sprayEffect4, partDelay + 2.4, partDuration, [sprayEffect4, suit, 0])
    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['cringe',
         1e-05,
         0.3,
         0.8])

    damageAnims.append(['cringe', 1e-05, 0.3])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=0.1, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Level 7 Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                      "Quality Control has classified that all Level 6 gags are now classified as defective.",
                                      CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'ste':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    elif attack['suit'].dna.name == 'frs':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack2))
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, sprayTrack, sprayTrack2, sprayTrack3, sprayTrack4)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, sprayTrack, sprayTrack2, sprayTrack3)

def doFilibusterVoicemail(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    battle = attack['battle']
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect4 = BattleParticles.createParticleEffect(file='filibusterSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect, 'filibuster-cut', color=color)
    BattleParticles.setEffectTexture(sprayEffect2, 'filibuster-fiscal', color=color)
    BattleParticles.setEffectTexture(sprayEffect3, 'filibuster-impeach', color=color)
    BattleParticles.setEffectTexture(sprayEffect4, 'filibuster-inc', color=color)
    partDelay = 0.3
    partDuration = 1.15
    damageDelay = 1.25
    dodgeDelay = 0.7
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('Filibuster', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'speak', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    sprayTrack = getPartTrack(sprayEffect, partDelay, partDuration, [sprayEffect, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
    sprayTrack4 = getPartTrack(sprayEffect4, partDelay + 2.4, partDuration, [sprayEffect4, suit, 0])
    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['cringe',
         1e-05,
         0.3,
         0.8])

    damageAnims.append(['cringe', 1e-05, 0.3])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=0.1, node=suit)
    suitTrack.append(doVoicemail(attack))
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, tauntInterval, sprayTrack, sprayTrack2, sprayTrack3, sprayTrack4)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, tauntInterval, sprayTrack, sprayTrack2, sprayTrack3)

def doFilibusterPhase2(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    battle = attack['battle']
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    BattleParticles.loadParticles()
    sprayEffect = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect4 = BattleParticles.createParticleEffect(file='filibusterSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect, 'filibuster-cut', color=color)
    BattleParticles.setEffectTexture(sprayEffect2, 'filibuster-fiscal', color=color)
    BattleParticles.setEffectTexture(sprayEffect3, 'filibuster-impeach', color=color)
    BattleParticles.setEffectTexture(sprayEffect4, 'filibuster-inc', color=color)
    partDelay = 0.3
    partDuration = 1.15
    damageDelay = 1.25
    dodgeDelay = 0.7
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('Filibuster', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'speak', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    sprayTrack = getPartTrack(sprayEffect, partDelay, partDuration, [sprayEffect, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
    sprayTrack4 = getPartTrack(sprayEffect4, partDelay + 2.4, partDuration, [sprayEffect4, suit, 0])
    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['cringe',
         1e-05,
         0.3,
         0.8])

    damageAnims.append(['cringe', 1e-05, 0.3])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=0.1, node=suit)
    ceaseTrack = ActorInterval(suit, 'come-on')
    ceaseSoundTrack = Func(suit.showHpString, "1.5x DMG MULTIPLIER!")
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Let's pick up the pace a bit, shall we?",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Func(suit.makeOttomanPhase2))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, tauntInterval, sprayTrack, sprayTrack2, sprayTrack3, sprayTrack4)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, tauntInterval, sprayTrack, sprayTrack2, sprayTrack3)

def doFilibusterCollectCall(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    battle = attack['battle']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    BattleParticles.loadParticles()
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    sprayEffect = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='filibusterSpray')
    sprayEffect4 = BattleParticles.createParticleEffect(file='filibusterSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect, 'filibuster-cut', color=color)
    BattleParticles.setEffectTexture(sprayEffect2, 'filibuster-fiscal', color=color)
    BattleParticles.setEffectTexture(sprayEffect3, 'filibuster-impeach', color=color)
    BattleParticles.setEffectTexture(sprayEffect4, 'filibuster-inc', color=color)
    partDelay = 0.3
    partDuration = 1.15
    damageDelay = 1.25
    dodgeDelay = 0.7
    tauntIndex = attack['taunt']
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = getAttackTaunt('Filibuster', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'speak', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    sprayTrack = getPartTrack(sprayEffect, partDelay, partDuration, [sprayEffect, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
    sprayTrack4 = getPartTrack(sprayEffect4, partDelay + 2.4, partDuration, [sprayEffect4, suit, 0])
    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['cringe',
         1e-05,
         0.3,
         0.8])

    damageAnims.append(['cringe', 1e-05, 0.3])
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_filibuster.ogg', delay=0.1, node=suit)
    suitTrack.append(doCollectCall(attack))
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, tauntInterval, sprayTrack, sprayTrack2, sprayTrack3, sprayTrack4)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, tauntInterval, sprayTrack, sprayTrack2, sprayTrack3)


def doSchmooze(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    upperEffects = []
    lowerEffects = []
    textureNames = ['schmooze-genius',
     'schmooze-instant',
     'schmooze-master',
     'schmooze-viz']
    for i in xrange(0, 4):
        upperEffect = BattleParticles.createParticleEffect(file='schmoozeUpperSpray')
        lowerEffect = BattleParticles.createParticleEffect(file='schmoozeLowerSpray')
        BattleParticles.setEffectTexture(upperEffect, textureNames[i], color=Vec4(0, 0, 1, 1))
        BattleParticles.setEffectTexture(lowerEffect, textureNames[i], color=Vec4(0, 0, 1, 1))
        upperEffects.append(upperEffect)
        lowerEffects.append(lowerEffect)

    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0.3
    damageDelay = partDelay + 0.4
    dodgeDelay = 0.4
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 7 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'blr':
        suitTrack.append(Wait(2.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    upperPartTracks = Parallel()
    lowerPartTracks = Parallel()
    for i in xrange(0, 4):
        upperPartTracks.append(getPartTrack(upperEffects[i], partDelay + i * 0.65, 0.8, [upperEffects[i], suit, 0]))
        lowerPartTracks.append(getPartTrack(lowerEffects[i], partDelay + i * 0.65 + 0.7, 1.0, [lowerEffects[i], suit, 0]))

    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['conked',
         0.01,
         0.3,
         0.71])

    damageAnims.append(['conked', 0.01, 0.3])
    dodgeAnims = []
    dodgeAnims.append(['duck',
     0.01,
     0.2,
     2.7])
    dodgeAnims.append(['duck',
     0.01,
     1.22,
     1.28])
    dodgeAnims.append(['duck', 0.01, 3.16])
    soundTrack = getSoundTrack('SA_schmooze.ogg', delay=damageDelay, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.9, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTrack, upperPartTracks, lowerPartTracks, soundTrack)

def doSchmoozeRadioInfrequency(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    upperEffects = []
    lowerEffects = []
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    textureNames = ['schmooze-genius',
     'schmooze-instant',
     'schmooze-master',
     'schmooze-viz']
    for i in xrange(0, 4):
        upperEffect = BattleParticles.createParticleEffect(file='schmoozeUpperSpray')
        lowerEffect = BattleParticles.createParticleEffect(file='schmoozeLowerSpray')
        BattleParticles.setEffectTexture(upperEffect, textureNames[i], color=Vec4(0, 0, 1, 1))
        BattleParticles.setEffectTexture(lowerEffect, textureNames[i], color=Vec4(0, 0, 1, 1))
        upperEffects.append(upperEffect)
        lowerEffects.append(lowerEffect)

    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0.3
    damageDelay = partDelay + 0.4
    dodgeDelay = 0.4
    taunt = getAttackTaunt('Schmooze', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'speak', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doRadioInfrequencySquirt(attack))
    upperPartTracks = Parallel()
    lowerPartTracks = Parallel()
    for i in xrange(0, 4):
        upperPartTracks.append(getPartTrack(upperEffects[i], partDelay + i * 0.65, 0.8, [upperEffects[i], suit, 0]))
        lowerPartTracks.append(getPartTrack(lowerEffects[i], partDelay + i * 0.65 + 0.7, 1.0, [lowerEffects[i], suit, 0]))

    damageAnims = []
    for i in xrange(0, 3):
        damageAnims.append(['conked',
         0.01,
         0.3,
         0.71])

    damageAnims.append(['conked', 0.01, 0.3])
    dodgeAnims = []
    dodgeAnims.append(['duck',
     0.01,
     0.2,
     2.7])
    dodgeAnims.append(['duck',
     0.01,
     1.22,
     1.28])
    dodgeAnims.append(['duck', 0.01, 3.16])
    soundTrack = getSoundTrack('SA_schmooze.ogg', delay=damageDelay, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.9, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTrack, upperPartTracks, lowerPartTracks, soundTrack)


def doQuake(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01], ['jump', 0.01]]
    soundTrack = getSoundTrack('SA_quake.ogg', node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Throw gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dsk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    toonTracks = getToonTracks(attack, damageDelay=1.8, splicedDamageAnims=damageAnims, dodgeDelay=1.1, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, soundTrack)

def doQuakeEnraged(attack): # stomp
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('Tremor', attack['suitName'])
    suit = attack['suit']
    suitTrack = Sequence(ActorInterval(suit, 'stomp'), Func(suit.setNeutralAnimation))
    makeAngry = Func(suit.makeAngry)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doEnraged(attack))
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                               splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    soundTrack = getSoundTrack('SA_tremor.ogg', delay=0.9, node=suit)
    return Parallel(suitTrack, soundTrack, tauntInterval, toonTracks, makeAngry)

def doParadigmShiftScapegoat(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    damageDelay = 1.35
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('ShiftSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    taunt = getAttackTaunt('ParadigmShift', attack['suitName'])
    suit = attack['suit']
    suitTrack = Sequence(ActorInterval(suit, 'magic2', playRate=1.25), Func(suit.setNeutralAnimation))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('ShiftLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 4.1, [liftEffect, battle, 0]))
            shadow = toon.dropShadow
            fakeShadow = MovieUtil.copyProp(shadow)
            x = toon.getX()
            y = toon.getY()
            z = toon.getZ()
            height = 3
            groundPoint = Point3(x, y, z)
            risePoint = Point3(x, y, z + height)
            shakeRight = Point3(x, y + 0.7, z + height)
            shakeLeft = Point3(x, y - 0.7, z + height)
            shakeTrack = Sequence()
            shakeTrack.append(Wait(damageDelay + 0.25))
            shakeTrack.append(Func(shadow.hide))
            shakeTrack.append(LerpPosInterval(toon, 1.1, risePoint))
            for i in xrange(0, 17):
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeLeft))
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeRight))

            shakeTrack.append(LerpPosInterval(toon, 0.1, risePoint))
            shakeTrack.append(LerpPosInterval(toon, 0.1, groundPoint))
            shakeTrack.append(Func(shadow.show))
            shadowTrack = Sequence()
            shadowTrack.append(Func(battle.movie.needRestoreRenderProp, fakeShadow))
            shadowTrack.append(Wait(damageDelay + 0.25))
            shadowTrack.append(Func(fakeShadow.hide))
            shadowTrack.append(Func(fakeShadow.setScale, 0.27))
            shadowTrack.append(Func(fakeShadow.reparentTo, toon))
            shadowTrack.append(Func(fakeShadow.setPos, MovieUtil.PNT3_ZERO))
            shadowTrack.append(Func(fakeShadow.wrtReparentTo, battle))
            shadowTrack.append(Func(fakeShadow.show))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.4, Point3(0.17, 0.17, 0.17)))
            shadowTrack.append(Wait(1.81))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.1, Point3(0.27, 0.27, 0.27)))
            shadowTrack.append(Func(MovieUtil.removeProp, fakeShadow))
            shadowTrack.append(Func(battle.movie.clearRenderProp, fakeShadow))
            toonRiseTracks.append(Parallel(shakeTrack, shadowTrack))

    damageAnims = []
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.9, startTime=2.06))
    damageAnims.append(['slip-backward', 0.01, 0.5])
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    suitTrack.append(Wait(4.0))
    suitTrack.append(doPoisonSpray(attack))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    if hitAtleastOneToon == 1:
        soundTrack = getSoundTrack('SA_paradigm_shift.ogg', delay=1.5, node=suit)
        return Parallel(suitTrack, sprayTrack, soundTrack, liftTracks, toonTracks, toonRiseTracks, tauntInterval)
    else:
        return Parallel(suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks)

def doParadigmShiftFreezingRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    damageDelay = 1.35
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('ShiftSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    taunt = getAttackTaunt('ParadigmShift', attack['suitName'])
    suit = attack['suit']
    suitTrack = Sequence(ActorInterval(suit, 'magic2', playRate=1.25), Func(suit.setNeutralAnimation))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('ShiftLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 4.1, [liftEffect, battle, 0]))
            shadow = toon.dropShadow
            fakeShadow = MovieUtil.copyProp(shadow)
            x = toon.getX()
            y = toon.getY()
            z = toon.getZ()
            height = 3
            groundPoint = Point3(x, y, z)
            risePoint = Point3(x, y, z + height)
            shakeRight = Point3(x, y + 0.7, z + height)
            shakeLeft = Point3(x, y - 0.7, z + height)
            shakeTrack = Sequence()
            shakeTrack.append(Wait(damageDelay + 0.25))
            shakeTrack.append(Func(shadow.hide))
            shakeTrack.append(LerpPosInterval(toon, 1.1, risePoint))
            for i in xrange(0, 17):
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeLeft))
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeRight))

            shakeTrack.append(LerpPosInterval(toon, 0.1, risePoint))
            shakeTrack.append(LerpPosInterval(toon, 0.1, groundPoint))
            shakeTrack.append(Func(shadow.show))
            shadowTrack = Sequence()
            shadowTrack.append(Func(battle.movie.needRestoreRenderProp, fakeShadow))
            shadowTrack.append(Wait(damageDelay + 0.25))
            shadowTrack.append(Func(fakeShadow.hide))
            shadowTrack.append(Func(fakeShadow.setScale, 0.27))
            shadowTrack.append(Func(fakeShadow.reparentTo, toon))
            shadowTrack.append(Func(fakeShadow.setPos, MovieUtil.PNT3_ZERO))
            shadowTrack.append(Func(fakeShadow.wrtReparentTo, battle))
            shadowTrack.append(Func(fakeShadow.show))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.4, Point3(0.17, 0.17, 0.17)))
            shadowTrack.append(Wait(1.81))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.1, Point3(0.27, 0.27, 0.27)))
            shadowTrack.append(Func(MovieUtil.removeProp, fakeShadow))
            shadowTrack.append(Func(battle.movie.clearRenderProp, fakeShadow))
            toonRiseTracks.append(Parallel(shakeTrack, shadowTrack))

    damageAnims = []
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.9, startTime=2.06))
    damageAnims.append(['slip-backward', 0.01, 0.5])
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    suitTrack.append(Wait(4.0))
    suitTrack.append(doFreezingRain(attack))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    if hitAtleastOneToon == 1:
        soundTrack = getSoundTrack('SA_paradigm_shift.ogg', delay=1.5, node=suit)
        return Parallel(suitTrack, sprayTrack, soundTrack, liftTracks, toonTracks, toonRiseTracks, tauntInterval)
    else:
        return Parallel(suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks)

def doParadigmShiftWiretapped(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    damageDelay = 1.35
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('ShiftSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    taunt = getAttackTaunt('ParadigmShift', attack['suitName'])
    suit = attack['suit']
    suitTrack = Sequence(ActorInterval(suit, 'magic2', playRate=1.25), Func(suit.setNeutralAnimation))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('ShiftLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 4.1, [liftEffect, battle, 0]))
            shadow = toon.dropShadow
            fakeShadow = MovieUtil.copyProp(shadow)
            x = toon.getX()
            y = toon.getY()
            z = toon.getZ()
            height = 3
            groundPoint = Point3(x, y, z)
            risePoint = Point3(x, y, z + height)
            shakeRight = Point3(x, y + 0.7, z + height)
            shakeLeft = Point3(x, y - 0.7, z + height)
            shakeTrack = Sequence()
            shakeTrack.append(Wait(damageDelay + 0.25))
            shakeTrack.append(Func(shadow.hide))
            shakeTrack.append(LerpPosInterval(toon, 1.1, risePoint))
            for i in xrange(0, 17):
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeLeft))
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeRight))

            shakeTrack.append(LerpPosInterval(toon, 0.1, risePoint))
            shakeTrack.append(LerpPosInterval(toon, 0.1, groundPoint))
            shakeTrack.append(Func(shadow.show))
            shadowTrack = Sequence()
            shadowTrack.append(Func(battle.movie.needRestoreRenderProp, fakeShadow))
            shadowTrack.append(Wait(damageDelay + 0.25))
            shadowTrack.append(Func(fakeShadow.hide))
            shadowTrack.append(Func(fakeShadow.setScale, 0.27))
            shadowTrack.append(Func(fakeShadow.reparentTo, toon))
            shadowTrack.append(Func(fakeShadow.setPos, MovieUtil.PNT3_ZERO))
            shadowTrack.append(Func(fakeShadow.wrtReparentTo, battle))
            shadowTrack.append(Func(fakeShadow.show))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.4, Point3(0.17, 0.17, 0.17)))
            shadowTrack.append(Wait(1.81))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.1, Point3(0.27, 0.27, 0.27)))
            shadowTrack.append(Func(MovieUtil.removeProp, fakeShadow))
            shadowTrack.append(Func(battle.movie.clearRenderProp, fakeShadow))
            toonRiseTracks.append(Parallel(shakeTrack, shadowTrack))

    damageAnims = []
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.9, startTime=2.06))
    damageAnims.append(['slip-backward', 0.01, 0.5])
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    suitTrack.append(Wait(4.0))
    suitTrack.append(doWiretapped(attack))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    if hitAtleastOneToon == 1:
        soundTrack = getSoundTrack('SA_paradigm_shift.ogg', delay=1.5, node=suit)
        return Parallel(suitTrack, sprayTrack, soundTrack, liftTracks, toonTracks, toonRiseTracks, tauntInterval)
    else:
        return Parallel(suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks)


def doShieldsUp(attack):
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('Tremor', attack['suitName'])
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    dmg = (attack['target'][0]['hp']) * len(battle.activeToons)
    selfDamageTrack = Sequence(Wait(7), Func(suit.showHpText, +dmg), Func(suit.setHealthForMe, dmg), Func(suit.updateHealthBar, 0))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout), Wait(6.0), Func(suit.setChatAbsolute, 'Is this the best you Toons can do?', CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'jump'), ActorInterval(suit, 'defense'), Func(suit.setNeutralAnimation))
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01], ['jump', 0.01]]
    soundTrack = getSoundTrack('SA_tremor.ogg', node=suit)
    makeShielding = Func(suit.makeShielding)
    soundTrack2 = getSoundTrack('SA_defense.ogg', delay=5.0, node=suit)
    soundTrack3 = getSoundTrack('LB_toonup.ogg', delay=7.0, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=1.8, splicedDamageAnims=damageAnims, dodgeDelay=1.1, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, tauntInterval, soundTrack, soundTrack2, soundTrack3, selfDamageTrack, makeShielding)

def doTremor(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    soundTrack = getSoundTrack('SA_tremor.ogg', delay=0.9, node=suit)
    return Parallel(suitTrack, soundTrack, toonTracks)


def doShake(attack):
    suit = attack['suit']
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    soundTrack = getSoundTrack('SA_tremor.ogg', delay=0.9, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    return Parallel(suitTrack, toonTracks, soundTrack)

def doBash(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Wait(1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(Wait(1), ActorInterval(suit, attack['animName']), Func(suit.setNeutralAnimation))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    propTrackNew = Parallel()
    laptopPosPoints = [Point3(-2, 1.5, 2.5), VBase3(0, 0, 0)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.75, 1.75, 1.75)
    propTrackNew.append(
        getPropTrack(card, cage, laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                     anim=1, animStartTime=0.5, animDuration=2.5,
                     propName='ttht_m_ene_techbotLaptop'))
    cagePos = [Point3(suitPos.getX() - 3, suitPos.getY() - 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=1),
            Parallel(
                SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
            ),
            Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
            Wait(2.0),
            LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
            Func(MovieUtil.removeProp, cage)
        )

    cagePropTracks.append(cagePropTrack)
    soundTrack = getSoundTrack('tt_s_ara_cmg_itemHitsFloor.ogg', delay=1.5, node=suit)
    damageAnims = [['slip-backward']]
    dodgeAnims = [['jump']]
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.0, splicedDodgeAnims=dodgeAnims)
    return Parallel(suitTrack, tauntInterval, cagePropTracks, propTrackNew, toonTracks, soundTrack)

def doDataCorruption(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    tauntInterval = Sequence(Wait(1), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(Wait(1), ActorInterval(suit, attack['animName']), Func(suit.setNeutralAnimation))
    suitPos = suit.getPos(battle)
    cagePropTracks = Parallel()
    cage = loader.loadModel('phase_3.5/models/modules/desk_only')
    card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    propTrackNew = Parallel()
    laptopPosPoints = [Point3(-2, 1.5, 2.5), VBase3(0, 0, 0)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.75, 1.75, 1.75)
    propTrackNew.append(
        getPropTrack(card, cage, laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                     anim=1, animStartTime=0.5, animDuration=2.5,
                     propName='ttht_m_ene_techbotLaptop'))
    cagePos = [Point3(suitPos.getX() - 3, suitPos.getY() - 3, 0), suit.getHpr(battle)]
    cagePropTrack = Sequence(
        getPropAppearTrack(cage, battle, cagePos, 0.01, scaleUpPoint=Point3(1.5), scaleUpTime=1),
        Parallel(
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/asfhdfha.ogg'), duration=0.75, node=cage)
        ),
        Func(base.playSfx, base.loader.loadSfx('phase_9/audio/sfx/asfhafhsdh.ogg'), node=cage),
        Wait(2.0),
        LerpFunctionInterval(cage.setAlphaScale, fromData=1, toData=0, duration=1.0),
        Func(MovieUtil.removeProp, cage)
    )

    cagePropTracks.append(cagePropTrack)
    damageAnims = [['cringe']]
    dodgeAnims = [['jump']]
    toonTracks = getToonTracks(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=1.0,
                               splicedDodgeAnims=dodgeAnims)
    oldcolor = render.getColorScale()
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1.5, (0, 0.992, 1, 1)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, tauntInterval, cagePropTracks, toonTracks, propTrackNew, lightingTrack)


def doEnraged(attack):
    suit = attack['suit']
    tauntIndex = attack['taunt']
    name = attack['id']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    damageAnims = [['slip-forward'], ['slip-forward', 0.01]]
    dodgeAnims = [['jump'], ['jump', 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=1.1, splicedDamageAnims=damageAnims, dodgeDelay=0.7, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=2.8, showDamageExtraTime=1.1)
    soundTrack = getSoundTrack('SA_rage.ogg', node=suit)
    suitTrack = Sequence(ActorInterval(suit, attack['animName']), Func(suit.setNeutralAnimation))
    headInterval = Sequence(MovieUtil.createSuitEnragedInterval(suit, 0))
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    return Parallel(suitTrack, soundTrack, headInterval, tauntInterval)


def doHangUp(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
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
    toonTrack = getToonTrack(attack, 3, ['slip-backward'], 2.5, ['jump'])
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 7 Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'frs':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doVoicemail(attack):
    suit = attack['suit']
    battle = attack['battle']
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
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
    suitSpeechTrack = Sequence(Wait(3.0), Func(suit.setChatAbsolute, "Guess you'll have to attack somebody else this turn, I'm taking a break from this nonsense.", CFSpeech | CFTimeout))
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    notifyTrack = Func(suit.showHpTextWhite, 'IMMUNE!')
    makeImmune = Func(suit.makeImmortal)
    makeUnVulnerable = Func(suit.makeUnVulnerable)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 6 and 8 Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    return Parallel(suitTrack, propTrack, soundTrack, makeUnVulnerable, suitSpeechTrack, notifyTrack, makeImmune)

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
                         Func(MovieUtil.removeProps, [receiver, phone]))
    makeVulnerable = Func(suit.makeVulnerable)
    selfDamageTrack = Sequence(Wait(4), Func(suit.showHpTextCheat, +dmg), Func(suit.showHpString, "SYPHONED!", openEnded=0), Func(suit.setHealthForMe, +dmg), Func(suit.updateHealthBar, 0))
    #propTrack = Sequence(Wait(0.3), Func(__showProp, phone, suit.getLeftHand(), phonePosPoints[0], phonePosPoints[1]), Func(__showProp, receiver, suit.getLeftHand(), receiverPosPoints[0], receiverPosPoints[1]), LerpScaleInterval(phone, 0.5, scaleUpPoint, MovieUtil.PNT3_NEARZERO), Wait(pickupDelay), Func(receiver.wrtReparentTo, suit.getRightHand()), LerpScaleInterval(receiver, 0.01, receiverAdjustScale), LerpPosHprInterval(receiver, 0.0001, Point3(-0.53, 0.21, -0.54), VBase3(-99.49, -35.27, 1.84)), Wait(dialDuration), Func(receiver.wrtReparentTo, phone), Wait(finalPhoneDelay), LerpScaleInterval(phone, 0.5, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, [receiver, phone]))
    toonTracks = getToonTracks(attack, 2.8, ['slip-backward'], 4.7, ['jump'])
    suitSpeechTrack = Sequence(Wait(3.0), Func(suit.setChatAbsolute, "I've tapped into your line, your health is now mine.", CFSpeech | CFTimeout))
    soundTrack = getSoundTrack('SA_hangup.ogg', delay=0.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=2.8, node=suit)
    makeNotImmune = Func(suit.makeNonImmortal)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 and 6 Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    suitTrack.append(Wait(1.0))
    suitTrack.append(doPayback(attack))
    return Parallel(suitTrack, propTrack, soundTrack, makeVulnerable, selfDamageTrack, soundTrack1, suitSpeechTrack, toonTracks, makeNotImmune, explodeTracks, explosionTrack)

def doWiretappedHighRoller(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    dmg = (attack['target'][0]['hp']) * len(battle.activeToons)
    phone = globalPropPool.getProp('phone')
    receiver = globalPropPool.getProp('receiver')
    taunt = random.choice(
        ["Now, you ffigned up for thiff!", "You'd befft go big or GO HOME!",
         "It'ff all or nothing, doll!",
         "But what if the fftakeff were EVEN HIGHER?!"])
    suitTrack = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(suit, 'phone', playRate=1.25), Func(suit.setNeutralAnimation))
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
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=2.8, node=suit)
    return Parallel(suitTrack, propTrack, soundTrack, soundTrack1, toonTracks, explodeTracks, explosionTrack)


def doRedTape(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tape = globalPropPool.getProp('redtape')
    tubes = []
    for i in xrange(0, 3):
        tubes.append(globalPropPool.getProp('redtape-tube'))

    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitName = suit.getStyleName()
    tapePosPoints = [Point3(-0.25, 0, -0.25), VBase3(0, 0, 0)]
    tapeScaleUpPoint = Point3(1, 1, 0.74)
    propTrack = Sequence(getPropAppearTrack(tape, suit.getRightHand(), tapePosPoints, 0.25, tapeScaleUpPoint, scaleUpTime=0.25))
    propTrack.append(Wait(1.55))
    hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
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
    toonTrack = getToonTrack(attack, 2.2, ['struggle'], 1.7, ['jump'])
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=1.7, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack, tubeTracks)
    else:
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doLegalBindings(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    tape = globalPropPool.getProp('redtape')
    tubes = []
    for i in xrange(0, 3):
        tubes.append(globalPropPool.getProp('redtape-tube'))
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
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    if suit.isSkeleton:
        suitTrack.append(Wait(2.0))
        suitTrack.append(doCaseInsurancePlanSkelecogInsurance(attack))
    else:
        suitTrack.append(Wait(2.0))
        suitTrack.append(doCaseInsurancePlanInsurance(attack))
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
    toonTrack = getToonTakeDamageTrack(attack, toon, target[0]['died'], 0, 2.2,
                                       ['struggle'])
    #toonTrack = getToonTrack(attack, 2.4, ['struggle'], 3.4, ['struggle'])
    notifyTrack = Sequence(Wait(3.0), Func(toon.showHpTextWhite, "LEGALLY BOUND!", 10))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, tauntInterval, soundTrack, tubeTracks, notifyTrack)

def doLegalBindingsSanction(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    tape = globalPropPool.getProp('redtape')
    tubes = []
    for i in xrange(0, 3):
        tubes.append(globalPropPool.getProp('redtape-tube'))
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    if suit.isSkeleton:
        suitTrack.append(Wait(2.0))
        suitTrack.append(doCaseInsurancePlanSkelecogInsurance(attack))
    else:
        suitTrack.append(Wait(2.0))
        suitTrack.append(doCaseInsurancePlanInsurance(attack))
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
    toonTrack = getToonTakeDamageTrack(attack, toon, target[0]['died'], 0, 2.2,
                                       ['struggle'])
    #toonTrack = getToonTrack(attack, 2.4, ['struggle'], 3.4, ['struggle'])
    notifyTrack = Sequence(Wait(3.0), Func(toon.showHpTextWhite, "LEGALLY BOUND!", 10))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTrack, tauntInterval, propTrack, soundTrack, tubeTracks, notifyTrack)


def doParadigmShift(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    damageDelay = 1.35
    dodgeDelay = 0.95
    sprayEffect = BattleParticles.createParticleEffect('ShiftSpray')
    suitName = suit.getStyleName()
    sprayEffect.setPos(Point3(-5.2, 4.6, 2.7))
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    liftTracks = Parallel()
    toonRiseTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            liftEffect = BattleParticles.createParticleEffect('ShiftLift')
            liftEffect.setPos(toon.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftTracks.append(getPartTrack(liftEffect, 1.1, 4.1, [liftEffect, battle, 0]))
            shadow = toon.dropShadow
            fakeShadow = MovieUtil.copyProp(shadow)
            x = toon.getX()
            y = toon.getY()
            z = toon.getZ()
            height = 3
            groundPoint = Point3(x, y, z)
            risePoint = Point3(x, y, z + height)
            shakeRight = Point3(x, y + 0.7, z + height)
            shakeLeft = Point3(x, y - 0.7, z + height)
            shakeTrack = Sequence()
            shakeTrack.append(Wait(damageDelay + 0.25))
            shakeTrack.append(Func(shadow.hide))
            shakeTrack.append(LerpPosInterval(toon, 1.1, risePoint))
            for i in xrange(0, 17):
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeLeft))
                shakeTrack.append(LerpPosInterval(toon, 0.03, shakeRight))

            shakeTrack.append(LerpPosInterval(toon, 0.1, risePoint))
            shakeTrack.append(LerpPosInterval(toon, 0.1, groundPoint))
            shakeTrack.append(Func(shadow.show))
            shadowTrack = Sequence()
            shadowTrack.append(Func(battle.movie.needRestoreRenderProp, fakeShadow))
            shadowTrack.append(Wait(damageDelay + 0.25))
            shadowTrack.append(Func(fakeShadow.hide))
            shadowTrack.append(Func(fakeShadow.setScale, 0.27))
            shadowTrack.append(Func(fakeShadow.reparentTo, toon))
            shadowTrack.append(Func(fakeShadow.setPos, MovieUtil.PNT3_ZERO))
            shadowTrack.append(Func(fakeShadow.wrtReparentTo, battle))
            shadowTrack.append(Func(fakeShadow.show))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.4, Point3(0.17, 0.17, 0.17)))
            shadowTrack.append(Wait(1.81))
            shadowTrack.append(LerpScaleInterval(fakeShadow, 0.1, Point3(0.27, 0.27, 0.27)))
            shadowTrack.append(Func(MovieUtil.removeProp, fakeShadow))
            shadowTrack.append(Func(battle.movie.clearRenderProp, fakeShadow))
            toonRiseTracks.append(Parallel(shakeTrack, shadowTrack))

    damageAnims = []
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.9, startTime=2.06))
    damageAnims.append(['slip-backward', 0.01, 0.5])
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    if attack['suit'].dna.name == 'frs':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    if hitAtleastOneToon == 1:
        soundTrack = getSoundTrack('SA_paradigm_shift.ogg', delay=1.5, node=suit)
        return Parallel(suitTrack, sprayTrack, soundTrack, liftTracks, toonTracks, toonRiseTracks)
    else:
        return Parallel(suitTrack, sprayTrack, liftTracks, toonTracks, toonRiseTracks)


def doPowerTrip(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = getSoundTrack('SA_powertrip.ogg', delay=1.8, node=suit)
    return Parallel(suitTrack, partTrack1, partTrack2, waterfallTrack, soundTrack, toonTracks)

def doPowerTripKamikaze(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('PowerTrip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'magic1', playRate=1.25), Func(suit.setNeutralAnimation))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = getSoundTrack('SA_powertrip.ogg', delay=1.8, node=suit)
    suitTrack.append(Wait(3.0))
    suitTrack.append(doKamikaze(attack))
    return Parallel(suitTrack, partTrack1, tauntInterval, partTrack2, soundTrack, waterfallTrack, toonTracks)

def doPowerTripHeavyRainfall(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('PowerTrip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'magic1', playRate=1.25), Func(suit.setNeutralAnimation))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = getSoundTrack('SA_powertrip.ogg', delay=1.8, node=suit)
    suitTrack.append(Wait(1.0))
    suitTrack.append(doHeavyRain2(attack))
    return Parallel(suitTrack, partTrack1, tauntInterval, partTrack2, soundTrack, waterfallTrack, toonTracks)

def doPowerTripOilRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('PowerTrip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'magic1', playRate=1.25), Func(suit.setNeutralAnimation))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = getSoundTrack('SA_powertrip.ogg', delay=1.8, node=suit)
    suitTrack.append(Wait(1.0))
    suitTrack.append(doOilRain(attack))
    return Parallel(suitTrack, partTrack1, tauntInterval, partTrack2, soundTrack, waterfallTrack, toonTracks)

def doPowerTripScabbard(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('PowerTrip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'magic1', playRate=1.25), Func(suit.setNeutralAnimation))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = getSoundTrack('SA_powertrip.ogg', delay=1.8, node=suit)
    suitTrack.append(Wait(1.0))
    suitTrack.append(doGroupSyphonCheat(attack))
    return Parallel(suitTrack, partTrack1, tauntInterval, partTrack2, soundTrack, waterfallTrack, toonTracks)

def doPowerTripBayouBash(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(0.1, 0.1, 0.1, 0.4)
    edgeColor = Vec4(0.4, 0.1, 0.9, 0.7)
    powerBar1 = BattleParticles.createParticleEffect(file='powertrip')
    powerBar2 = BattleParticles.createParticleEffect(file='powertrip2')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-60, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(60, 0, 0)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitName = suit.getStyleName()
    if suitName == 'mh':
        waterfallEffect.setPos(0, 4, 3.6)
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('PowerTrip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'magic1', playRate=1.25), Func(suit.setNeutralAnimation))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(1.0), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 1.3, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.8, ['slip-forward'], 1.29, ['jump'])
    soundTrack = getSoundTrack('SA_powertrip.ogg', delay=1.8, node=suit)
    suitTrack.append(Wait(3.0))
    suitTrack.append(doBayouBashReal(attack))
    return Parallel(suitTrack, partTrack1, tauntInterval, partTrack2, soundTrack, waterfallTrack, toonTracks)


def getThrowEndPoint(suit, toon, battle, whichBounce):
    pnt = toon.getPos(toon)
    if whichBounce == 'one':
        pnt.setY(pnt[1] + 8)
    elif whichBounce == 'two':
        pnt.setY(pnt[1] + 5)
    elif whichBounce == 'threeHit':
        pnt.setZ(pnt[2] + toon.shoulderHeight + 0.3)
    elif whichBounce == 'threeMiss':
        pass
    elif whichBounce == 'four':
        pnt.setY(pnt[1] - 5)
    return Point3(pnt)


def doBounceCheck(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    check = globalPropPool.getProp('bounced-check')
    checkPosPoints = [Point3(-0.25, -0.425, 0), VBase3(-180, 0, 0)]
    bounce1Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'one')
    bounce2Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'two')
    hit3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeHit')
    miss3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeMiss')
    bounce4Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'four')
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1
    dodgeDelay = 3.1
    damageDelay = 3.5
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 6 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    checkPropTrack = Sequence(getPropAppearTrack(check, suit.getRightHand(), checkPosPoints, .5, Point3(8.5, 8.5, 8.5), startScale=MovieUtil.PNT3_ONE))
    checkPropTrack.append(Wait(throwDelay))
    checkPropTrack.append(Func(check.wrtReparentTo, toon))
    checkPropTrack.append(Func(check.setHpr, Point3(0, -90, 0)))
    checkPropTrack.append(getThrowTrack(check, bounce1Point, duration=0.5, parent=toon))
    checkPropTrack.append(getThrowTrack(check, bounce2Point, duration=0.5, parent=toon))
    if hitSuit:
        checkPropTrack.append(getThrowTrack(check, hit3Point, duration=0.5, parent=toon))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
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
        checkPropTrack.append(Parallel(explodeTrack, soundTrack))
    else:
        checkPropTrack.append(getThrowTrack(check, miss3Point, duration=0.5, parent=toon))
        checkPropTrack.append(getThrowTrack(check, bounce4Point, duration=0.5, parent=toon))
        checkPropTrack.append(LerpScaleInterval(check, 0.3, MovieUtil.PNT3_NEARZERO))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 1, duration=0.5, node=suit), getSoundTrack('SA_pink_slip.ogg', duration=0.6, node=suit))
    return Parallel(suitTrack, checkPropTrack, toonTrack, soundTracks)

def doBounceRate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    check = globalPropPool.getProp('ttrpg_m_ene_prp_bouncedRate')
    checkPosPoints = [Point3(1.5, 0.65, 0), VBase3(-180, 0, 0)]
    bounce1Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'one')
    bounce2Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'two')
    hit3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeHit')
    miss3Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'threeMiss')
    bounce4Point = lambda suit = suit, toon = toon, battle = battle: getThrowEndPoint(suit, toon, battle, 'four')
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1
    dodgeDelay = 3.1
    damageDelay = 3.5
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    checkPropTrack = Sequence(
        getPropAppearTrack(check, suit.getRightHand(), checkPosPoints, .5, Point3(2, 2, 2),
                           startScale=MovieUtil.PNT3_ONE))
    checkPropTrack.append(Wait(throwDelay))
    checkPropTrack.append(Func(check.wrtReparentTo, toon))
    checkPropTrack.append(Func(check.setHpr, Point3(0, 90, 0)))
    checkPropTrack.append(getThrowTrack(check, bounce1Point, duration=0.5, parent=toon))
    checkPropTrack.append(getThrowTrack(check, bounce2Point, duration=0.5, parent=toon))
    if hitSuit:
        checkPropTrack.append(getThrowTrack(check, hit3Point, duration=0.5, parent=toon))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
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
        checkPropTrack.append(Parallel(explodeTrack, soundTrack))
    else:
        checkPropTrack.append(getThrowTrack(check, miss3Point, duration=0.5, parent=toon))
        checkPropTrack.append(getThrowTrack(check, bounce4Point, duration=0.5, parent=toon))
        checkPropTrack.append(LerpScaleInterval(check, 0.3, MovieUtil.PNT3_NEARZERO))
        checkPropTrack.append(Func(MovieUtil.removeProp, check))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 1, duration=0.5, node=suit), getSoundTrack('SA_pink_slip.ogg', duration=0.6, node=suit))
    return Parallel(suitTrack, checkPropTrack, toonTrack, soundTracks)

def doBounceCheckPecking(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    battle = attack['battle']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    hitSuit = dmg > 0
    check = globalPropPool.getProp('bounced-check')
    checkPosPoints = [Point3(-0.25, -0.425, 0), VBase3(-180, 0, 0)]
    bounce1Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'one')
    bounce2Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'two')
    hit3Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'threeHit')
    miss3Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'threeMiss')
    bounce4Point = lambda suit=suit, toon=toon, battle=battle: getThrowEndPoint(suit, toon, battle, 'four')
    suitType = getSuitBodyType(attack['suitName'])
    throwDelay = 1
    dodgeDelay = 3.1
    damageDelay = 3.5
    taunt = getAttackTaunt('BounceCheck', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'throw-paper', playRate=1.5))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(3.0))
        suitTrack.append(doPeckingOrderVulnerability(attack))
    checkPropTrack = Sequence(getPropAppearTrack(check, suit.getRightHand(), checkPosPoints, .5, Point3(8.5, 8.5, 8.5),
                                                 startScale=MovieUtil.PNT3_ONE))
    checkPropTrack.append(Wait(throwDelay))
    checkPropTrack.append(Func(check.wrtReparentTo, toon))
    checkPropTrack.append(Func(check.setHpr, Point3(0, -90, 0)))
    checkPropTrack.append(getThrowTrack(check, bounce1Point, duration=0.5, parent=toon))
    checkPropTrack.append(getThrowTrack(check, bounce2Point, duration=0.5, parent=toon))
    if hitSuit:
        checkPropTrack.append(getThrowTrack(check, hit3Point, duration=0.5, parent=toon))
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
        checkPropTrack.append(Parallel(explodeTrack, soundTrack))
    else:
        checkPropTrack.append(getThrowTrack(check, miss3Point, duration=0.5, parent=toon))
        checkPropTrack.append(getThrowTrack(check, bounce4Point, duration=0.5, parent=toon))
        checkPropTrack.append(LerpScaleInterval(check, 0.3, MovieUtil.PNT3_NEARZERO))
    checkPropTrack.append(Func(MovieUtil.removeProp, check))
    toonTrack = getToonTrack(attack, damageDelay, ['conked'], dodgeDelay, ['sidestep'])
    soundTracks = Sequence(getSoundTrack('SA_pink_slip.ogg', delay=throwDelay + 1, duration=0.5, node=suit),
                           getSoundTrack('SA_pink_slip.ogg', duration=0.6, node=suit))
    return Parallel(suitTrack, checkPropTrack, toonTrack, soundTracks)


def doWatercooler(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    watercooler = globalPropPool.getProp('cc_a_prp_bat_watercooler')

    def getCoolerSpout(watercooler = watercooler):
        spout = watercooler.find('**/Dispenser') # Unlike the previous model, it appears that the spout's node is Dispenser.
        return spout.getPos(render)

    suitTrack = getSuitAnimTrack(attack) # I'm not going to have the Cog turn since it appears that, ever since Clash v1.7, Cogs no longer turn to face the Toon when performing the Watercooler attack.
    posPoints = [Point3(0.5, 0.2, 0), VBase3(90, 0, 180)]
    # Not a huge fan of how getPropTrack() is handling the watercooler prop.  I'll create my own version, then.
    propTrack = Sequence(
        Func(__showProp, watercooler, suit.getLeftHand(), *posPoints),
        ActorInterval(watercooler, 'cc_a_prp_bat_watercooler'),
        Func(MovieUtil.removeProp, watercooler)
    )
    sprayTracks = Parallel()
    splashTracks = Parallel()

    def prepSplash(splash, targetPoint):
        splash.reparentTo(render)
        splash.setPos(targetPoint)
        scale = splash.getScale()
        splash.setBillboardPointWorld()
        splash.setScale(scale)

    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        hitPoint = lambda toon = toon: __toonFacePoint(toon)
        missPoint = lambda prop = watercooler, toon = toon: __toonMissPoint(prop, toon, 0, parent=render)
        sprayTrack = Sequence()
        sprayTrack.append(Wait(3.11))
        sprayTrack.append(MovieUtil.getSprayTrack(battle, Point4(0.75, 0.75, 1.0, 0.8), getCoolerSpout, hitPoint if dmg > 0 else missPoint, 0.2, 0.2, 0.2, horizScale=0.3, vertScale=0.3))
        sprayTracks.append(sprayTrack)
        if dmg > 0:
            splash = globalPropPool.getProp('splash-from-splat')
            splash.setColor(0.75, 0.75, 1, 0.8)
            splash.setScale(0.3)
            splashTracks.append(Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(3.2), Func(prepSplash, splash, __toonFacePoint(toon)), ActorInterval(splash, 'splash-from-splat'), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash)))

    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=suitTrack.getDuration() - 1.5, damageAnimNames=['cringe'], dodgeDelay=2.4, splicedDodgeAnims=dodgeAnims)
    soundTrack = Sequence(Wait(1.1), SoundInterval(globalBattleSoundCache.getSound('SA_watercooler_appear_only.ogg'), node=suit, duration=1.4722), Wait(0.4), SoundInterval(globalBattleSoundCache.getSound('SA_watercooler_spray_only.ogg'), node=suit, duration=2.313))
    return Parallel(suitTrack, toonTracks, propTrack, sprayTracks, soundTrack, splashTracks)

def doAceInTheHoleNew(attack):
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
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
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


def doFired(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
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
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 1.9, [baseFlameEffect, toon, 0])
    flameTrack = getPartTrack(flameEffect, 1.0, 1.9, [flameEffect, toon, 0])
    flecksTrack = getPartTrack(flecksEffect, 1.8, 1.1, [flecksEffect, toon, 0])
    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 1.9, [baseFlameSmall, toon, 0])
    flameSmallTrack = getPartTrack(flameSmall, 1.0, 1.9, [flameSmall, toon, 0])
    flecksSmallTrack = getPartTrack(flecksSmall, 1.8, 1.1, [flecksSmall, toon, 0])

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

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.0))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(3.5))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
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
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, baseFlameTrack, flameTrack, flecksTrack, toonTrack, colorTrack, soundTrack)
    else:
        return Parallel(suitTrack, baseFlameSmallTrack, flameSmallTrack, flecksSmallTrack, toonTrack, soundTrack)

def doFiredSnap(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
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
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = getAttackTaunt('Fired', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'magic2', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doSnapSoaked(attack))
    baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 1.9, [baseFlameEffect, toon, 0])
    flameTrack = getPartTrack(flameEffect, 1.0, 1.9, [flameEffect, toon, 0])
    flecksTrack = getPartTrack(flecksEffect, 1.8, 1.1, [flecksEffect, toon, 0])
    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 1.9, [baseFlameSmall, toon, 0])
    flameSmallTrack = getPartTrack(flameSmall, 1.0, 1.9, [flameSmall, toon, 0])
    flecksSmallTrack = getPartTrack(flecksSmall, 1.8, 1.1, [flecksSmall, toon, 0])

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

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.0))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(3.5))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
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
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, baseFlameTrack, flameTrack, tauntInterval, flecksTrack, toonTrack, colorTrack, soundTrack)
    else:
        return Parallel(suitTrack, baseFlameSmallTrack, flameSmallTrack, tauntInterval, flecksSmallTrack, toonTrack, soundTrack)

def doFiredConeOfShame(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
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
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = getAttackTaunt('Fired', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'magic2', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doConeOfShame(attack))
    baseFlameTrack = getPartTrack(baseFlameEffect, 1.0, 1.9, [baseFlameEffect, toon, 0])
    flameTrack = getPartTrack(flameEffect, 1.0, 1.9, [flameEffect, toon, 0])
    flecksTrack = getPartTrack(flecksEffect, 1.8, 1.1, [flecksEffect, toon, 0])
    baseFlameSmallTrack = getPartTrack(baseFlameSmall, 1.0, 1.9, [baseFlameSmall, toon, 0])
    flameSmallTrack = getPartTrack(flameSmall, 1.0, 1.9, [flameSmall, toon, 0])
    flecksSmallTrack = getPartTrack(flecksSmall, 1.8, 1.1, [flecksSmall, toon, 0])

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

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.0))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(3.5))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
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
    toonTrack = getToonTrack(attack, damageDelay=1.5, splicedDamageAnims=damageAnims, dodgeDelay=0.3, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=1.0, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, baseFlameTrack, flameTrack, tauntInterval, flecksTrack, toonTrack, colorTrack, soundTrack)
    else:
        return Parallel(suitTrack, baseFlameSmallTrack, flameSmallTrack, tauntInterval, flecksSmallTrack, toonTrack, soundTrack)


def doAudit(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    calculator = globalPropPool.getProp('calculator')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect, 'audit-one', color=Vec4(0, 0, 0, 1))
    particleEffect2 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect2, 'audit-two', color=Vec4(0, 0, 0, 1))
    particleEffect3 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect3, 'audit-three', color=Vec4(0, 0, 0, 1))
    particleEffect4 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect4, 'audit-four', color=Vec4(0, 0, 0, 1))
    particleEffect5 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect5, 'audit-mult', color=Vec4(0, 0, 0, 1))
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    partTrack = getPartTrack(particleEffect, 1.5, 1.5, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 1.6, 1.5, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 1.7, 1.6, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 1.8, 1.7, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 1.9, 1.8, [particleEffect5, suit, 0])
    suitName = attack['suitName']
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='calculator',
                                 animStartTime=0,
                                 animDuration=2.5)
    toonTrack = getToonTrack(attack, 2.6, ['conked'], 0.9, ['duck'], showMissedExtraTime=2.2)
    soundTrack = getSoundTrack('SA_audit.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, calcPropTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)


def doCalculate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    calculator = globalPropPool.getProp('calculator')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect, 'audit-one', color=Vec4(0, 0, 0, 1))
    particleEffect2 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect2, 'audit-plus', color=Vec4(0, 0, 0, 1))
    particleEffect3 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect3, 'audit-mult', color=Vec4(0, 0, 0, 1))
    particleEffect4 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect4, 'audit-three', color=Vec4(0, 0, 0, 1))
    particleEffect5 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect5, 'audit-div', color=Vec4(0, 0, 0, 1))
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    partTrack = getPartTrack(particleEffect, 1.5, 1.5, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 1.6, 1.5, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 1.7, 1.6, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 1.8, 1.7, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 1.9, 1.8, [particleEffect5, suit, 0])
    suitName = attack['suitName']
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='calculator',
                                 animStartTime=0,
                                 animDuration=2.5)
    toonTrack = getToonTrack(attack, 2.6, ['conked'], 1.2, ['sidestep'])
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, calcPropTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)


def doTabulate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    calculator = globalPropPool.getProp('calculator')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect, 'audit-plus', color=Vec4(0, 0, 0, 1))
    particleEffect2 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect2, 'audit-minus', color=Vec4(0, 0, 0, 1))
    particleEffect3 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect3, 'audit-mult', color=Vec4(0, 0, 0, 1))
    particleEffect4 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect4, 'audit-div', color=Vec4(0, 0, 0, 1))
    particleEffect5 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect5, 'audit-one', color=Vec4(0, 0, 0, 1))
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    partTrack = getPartTrack(particleEffect, 1.5, 1.5, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 1.6, 1.5, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 1.7, 1.6, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 1.8, 1.7, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 1.9, 1.8, [particleEffect5, suit, 0])
    suitName = attack['suitName']
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcDuration = 1.3
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    calcPropTrack = getPropTrack(calculator, suit.getLeftHand(), calcPosPoints, 0, calcDuration,
                                 scaleUpPoint=scaleUpPoint, scaleUpTime=0, anim=1, propName='calculator',
                                 animStartTime=0,
                                 animDuration=2.5)
    toonTrack = getToonTrack(attack, 2.6, ['conked'], 1.2, ['sidestep'])
    soundTrack = getSoundTrack('SA_calculate.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, calcPropTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)


def doCrunch(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    throwDuration = 1.75
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    numberNames = ['one',
     'two',
     'three',
     'four',
     'five',
     'six']
    BattleParticles.loadParticles()
    numberSpill1 = BattleParticles.createParticleEffect(file='numberSpill')
    numberSpill2 = BattleParticles.createParticleEffect(file='numberSpill')
    spillTexture1 = random.choice(numberNames)
    spillTexture2 = random.choice(numberNames)
    BattleParticles.setEffectTexture(numberSpill1, 'audit-' + spillTexture1)
    BattleParticles.setEffectTexture(numberSpill2, 'audit-' + spillTexture2)
    numberSpillTrack1 = getPartTrack(numberSpill1, .5, 2.1, [numberSpill1, suit, 0])
    numberSpillTrack2 = getPartTrack(numberSpill2, .5, 2.1, [numberSpill2, suit, 0])
    numberSprayTracks = Parallel()
    numOfNumbers = random.randint(10, 15)
    for i in xrange(0, numOfNumbers - 1):
        nextSpray = BattleParticles.createParticleEffect(file='numberSpray')
        nextTexture = random.choice(numberNames)
        BattleParticles.setEffectTexture(nextSpray, 'audit-' + nextTexture)
        nextStartTime = random.random() * 0.6 + throwDuration
        nextDuration = random.random() * 0.4 + 1.4
        nextSprayTrack = getPartTrack(nextSpray, nextStartTime, nextDuration, [nextSpray, suit, 0])
        numberSprayTracks.append(nextSprayTrack)

    numberTracks = Parallel()
    for i in xrange(0, numOfNumbers):
        texture = random.choice(numberNames)
        next = MovieUtil.copyProp(BattleParticles.getParticle('audit-' + texture))
        next.reparentTo(suit.getRightHand())
        next.setScale(0.01, 0.01, 0.01)
        next.setColor(Vec4(0.0, 0.0, 0.0, 1.0))
        next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
        next.setHpr(VBase3(-1.15, 86.58, -76.78))
        numberTrack = Sequence(Wait(0.5), LerpScaleInterval(next, 0.25, MovieUtil.PNT3_ONE), Wait(1.1), Func(MovieUtil.removeProp, next))
        numberTracks.append(numberTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.14,
     0.28])
    damageAnims.append(['cringe',
     0.01,
     0.16,
     0.3])
    damageAnims.append(['cringe',
     0.01,
     0.13,
     0.22])
    damageAnims.append(['slip-forward', 0.01, 0.6])
    toonTrack = getToonTrack(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=2.6, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_crunch.ogg', delay=3, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, numberSpillTrack1, numberSpillTrack2, numberTracks, numberSprayTracks)



def doLiquidate(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1
    suitTrack = Sequence(Wait(0.5), getSuitTrack(attack, playRate=1.25))
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
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=2.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    if dmg > 0:
        puddle = globalPropPool.getProp('quicksand')
        puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
        puddle.setHpr(Point3(120, 0, 0))
        puddle.setScale(0.01)
        puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack, puddleTrack)
    else:
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)

def doLiquidateSoakResist(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    rainEffect = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('Liquidate', attack['suitName'])
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    tauntInterval = Sequence(Wait(0.5), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, Wait(0.5), ActorInterval(suit, 'magic1', playRate=1.25), suitReset, Func(suit.setNeutralAnimation))
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
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=2.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    suitTrack.append(Wait(2))
    suitTrack.append(doSoakResist(attack))
    if dmg > 0:
        puddle = globalPropPool.getProp('quicksand')
        puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
        puddle.setHpr(Point3(120, 0, 0))
        puddle.setScale(0.01)
        puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack, tauntInterval, puddleTrack)
    else:
        return Parallel(suitTrack, toonTrack, cloudPropTrack, tauntInterval, soundTrack)

def doLiquidateAftershock(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt('Liquidate', attack['suitName'])
    tauntInterval = Sequence(Wait(0.5), Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, Wait(0.5), ActorInterval(suit, 'magic1', playRate=1.25), Func(suit.setNeutralAnimation))
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
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=2.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    suitTrack.append(Wait(2))
    suitTrack.append(doAfterShock(attack))
    if dmg > 0:
        puddle = globalPropPool.getProp('quicksand')
        puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
        puddle.setHpr(Point3(120, 0, 0))
        puddle.setScale(0.01)
        puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack, tauntInterval, puddleTrack)
    else:
        return Parallel(suitTrack, toonTrack, cloudPropTrack, tauntInterval, soundTrack)

def doHeavyRainfall(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        toon = t['toon']
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    BattleParticles.loadParticles()
    damageDelay = 1.5
    dodgeDelay = 1.5
    rainEffect = BattleParticles.createParticleEffect(file='liquidate2')
    rainEffect2 = BattleParticles.createParticleEffect(file='liquidate2')
    rainEffect3 = BattleParticles.createParticleEffect(file='liquidate2')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'b':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    elif suitType == 'c':
        partDelay = 0.2
        damageDelay = 3.5
        dodgeDelay = 2.45
    taunt = random.choice(
        ["Water, water, everywhere!", "I'm not crying, you're crying!",
         "I think this is called 'delayed physical aggression.'", "I'm only going to hit back as hard as you do!'",
         "I can weather the storm, Toons.",
         "I heard you Toons like roughhousing, can I play too?",
         "If I can't make you like me, then I can at least make you fear me!"])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'magic3', playRate=1.25), Func(suit.setNeutralAnimation))
    targetPoint = __toonFacePoint(toon)
    targetPoint.setZ(targetPoint[2] + 3)
    initialCloudHeight = suit.height + 3
    cloudPosPoints = [Point3(0, 0, initialCloudHeight), VBase3(0, 0, 0)]
    cloudPropTrack = Sequence()
    cloudPropTrack.append(Func(cloud.pose, 'stormcloud', 0))
    cloudPropTrack.append(getPropAppearTrack(cloud, suit, cloudPosPoints, 1e-06, Point3(3, 3, 3), scaleUpTime=0.7))
    cloudPropTrack.append(Func(battle.movie.needRestoreRenderProp, cloud))
    cloudPropTrack.append(Func(cloud.wrtReparentTo, render))
    cloudPropTrack.append(Wait(1.1))
    cloudPropTrack.append(LerpPosInterval(cloud, 1, pos=targetPoint))
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=4.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=4.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=4.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    animTrack = Sequence(Wait(2), Func(suit.play,'cease'))
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.7)
    soundTrack1 = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    soundTrack2 = getSoundTrack('SA_cease_and_desist.ogg', delay=4.0, node=suit)
    soundTrack = Parallel(soundTrack1, soundTrack2)
    puddle = globalPropPool.getProp('quicksand')
    puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
    puddle.setHpr(Point3(120, 0, 0))
    puddle.setScale(0.5)
    puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
    return Parallel(suitTrack, toonTracks, cloudPropTrack, soundTrack, puddleTrack, animTrack)

def doDrowning(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.5
    dodgeDelay = 1.5
    hitAtleastOneToon = 0
    for t in targets:
        toon = t['toon']
        if t['hp'] > 0:
            hitAtleastOneToon = 1
    BattleParticles.loadParticles()
    suitType = getSuitBodyType(attack['suitName'])
    suitTrack = getSuitAnimTrack(attack)
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    dodgeAnims = []
    dodgeAnims.append(['jump',
                       0.01,
                       0,
                       0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.0, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=1.0, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                               splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.7)
    puddle = globalPropPool.getProp('quicksand')
    puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
    puddle.setHpr(Point3(120, 0, 0))
    puddle.setScale(0.01)
    puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
    return Parallel(suitTrack, toonTracks, soundTrack, puddleTrack)
		
def doAcidRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    BattleParticles.loadParticles()
    rainEffect = BattleParticles.createParticleEffect(file='acidrain')
    rainEffect2 = BattleParticles.createParticleEffect(file='acidrain')
    rainEffect3 = BattleParticles.createParticleEffect(file='acidrain')
    cloud = globalPropPool.getProp('stormcloud')
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 0
    damageDelay = 1.5
    dodgeDelay = 1
    suitTrack = Sequence(Wait(0.5), getSuitTrack(attack, playRate=1.25))
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
    cloudPropTrack.append(Wait(partDelay))
    cloudPropTrack.append(Parallel(Sequence(ParticleInterval(rainEffect, cloud, worldRelative=0, duration=2.1, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect2, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(Wait(0.1), ParticleInterval(rainEffect3, cloud, worldRelative=0, duration=2.0, cleanup=True)), Sequence(ActorInterval(cloud, 'stormcloud', startTime=3, duration=0.1), ActorInterval(cloud, 'stormcloud', startTime=1, duration=2.3))))
    cloudPropTrack.append(Wait(0.4))
    cloudPropTrack.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
    cloudPropTrack.append(Func(MovieUtil.removeProp, cloud))
    cloudPropTrack.append(Func(battle.movie.clearRenderProp, cloud))
    damageAnims = [['melt'], ['jump', 1.5, 0.4]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_liquidate.ogg', delay=2.0, node=suit)
    if dmg > 0:
        puddle = globalPropPool.getProp('quicksand')
        puddle.setColor(Vec4(0.0, 1.0, 0.0, 1))
        puddle.setHpr(Point3(120, 0, 0))
        puddle.setScale(0.01)
        puddleTrack = Sequence(Func(battle.movie.needRestoreRenderProp, puddle), Wait(damageDelay - 0.7), Func(puddle.reparentTo, battle), Func(puddle.setPos, toon.getPos(battle)), LerpScaleInterval(puddle, 1.7, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO), Wait(3.2), LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8), Func(MovieUtil.removeProp, puddle), Func(battle.movie.clearRenderProp, puddle))
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack, puddleTrack)
    else:
        return Parallel(suitTrack, toonTrack, cloudPropTrack, soundTrack)


def doMarketCrash(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 1.5
    propDelay = .5
    throwDuration = 1.0
    paper = globalPropPool.getProp('newspaper')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 6 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    posPoints = [Point3(-1.6, -0.75, 0.2), VBase3(-90, 170, 0)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(3.5, 3.5, 3.5), scaleUpTime=0))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.2)
    hitPoint.setY(hitPoint.getY() + 1.5)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(paper, throwDuration, Point3(0, 0, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    toonTrack = getToonTrack(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=2.5, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    soundTrack = getSoundTrack('SA_market_crash.ogg', node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)

def doMarketCrashPecking(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 1.75
    propDelay = 0.1
    throwDuration = 1.0
    paper = globalPropPool.getProp('newspaper')
    taunt = getAttackTaunt('MarketCrash', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'throw-object', playRate=1.5))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(3.0))
        suitTrack.append(doPeckingOrderVulnerability(attack))
    posPoints = [Point3(-1.6, -0.75, 0.2), VBase3(-90, 170, 0)]
    paperTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(3.5, 3.5, 3.5), scaleUpTime=0.25))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.2)
    hitPoint.setY(hitPoint.getY() + 1.5)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay), LerpHprInterval(paper, throwDuration, Point3(0, 0, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)),
                         Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper),
                         Func(battle.movie.clearRenderProp, paper))
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
    toonTrack = getToonTrack(attack, damageDelay=3, splicedDamageAnims=damageAnims, dodgeDelay=2.5, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    soundTrack = getSoundTrack('SA_market_crash.ogg', node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doBite(attack):
    suit = attack['suit']
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
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
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
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration), ActorInterval(teeth, 'teeth', duration=0.3), Func(teeth.pose, 'teeth', 1), Wait(0.7), ActorInterval(teeth, 'teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
        else:
            flyPoint = __toonFacePoint(toon, parent=battle)
            flyPoint.setY(flyPoint.getY() - 7.1)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Func(MovieUtil.removeProp, teeth))
            teethAppearTrack.append(Func(battle.movie.clearRenderProp, teeth))
            propTrack = teethAppearTrack
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
    toonTracks = getToonTracks(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.7, splicedDodgeAnims=dodgeAnims, showDamageExtraTime=2.4)
    soundTrack = getSoundTrack('SA_bite%s.ogg' % ('' if hitAtleastOneToon else '_miss'), delay=2, node=suit)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks)


def doSnap(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    teeth = globalPropPool.getProp('litigator-teeth')
    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.55
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4),
                                                   scaleUpTime=propScaleUpTime))
    teethAppearTrack.append(Wait(suitDelay))
    teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
    teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
    if dmg > 0:
        x = toon.getX(battle)
        y = toon.getY(battle)
        z = toon.getZ(battle)
        toonHeight = z + toon.getHeight()
        flyPoint = Point3(x, y + 2.7, toonHeight * 0.7)
        teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
        teethAppearTrack.append(Wait(0.2))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y, toonHeight + 3)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 1.2, toonHeight * 0.7)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.7, toonHeight * 0.4)))
        teethAppearTrack.append(Wait(0.4))
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)), Wait(0.9),
                              LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)), Wait(1.2),
                              LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
        hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2),
                            LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6),
                            LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration),
                             ActorInterval(teeth, 'litigator-teeth', duration=0.3), Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7),
                             ActorInterval(teeth, 'litigator-teeth', duration=0.9))
        propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
                             Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
    else:
        x = toon.getX(battle)
        y = toon.getY(battle)
        z = toon.getZ(battle)
        z = z + 0.2
        flyPoint = Point3(x, y - 2.1, z)
        teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
        teethAppearTrack.append(Wait(0.2))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.5, y - 2.5, z)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.0, y - 3.0, z + 0.4)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.3, y - 3.6, z)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.9, y - 3.1, z + 0.4)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.3, y - 2.6, z)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.1, y - 2.2, z + 0.4)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.4, y - 1.9, z)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.7, y - 2.1, z + 0.4)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.8, y - 2.3, z)))
        teethAppearTrack.append(LerpScaleInterval(teeth, 0.6, MovieUtil.PNT3_NEARZERO))
        hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.5),
                            LerpHprInterval(teeth, 0.4, Point3(80, 0, 0), startHpr=Point3(180, 0, 0)),
                            LerpHprInterval(teeth, 0.8, Point3(-10, 0, 0), startHpr=Point3(80, 0, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=3.6))
        propTrack = Sequence(Parallel(teethAppearTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth),
                             Func(battle.movie.clearRenderProp, teeth))
    damageAnims = [['cringe',
                    0.01,
                    0.7,
                    1.2],
                   ['spit',
                    0.01,
                    2.95,
                    1.47],
                   ['spit',
                    0.01,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit', 0.01, 4.42]]
    dodgeAnims = [['jump', 0.01, 0.01]]
    soundTrack = getSoundTrack('SA_chomp.ogg', delay=2, node=suit)
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2.33), 2.1, splicedDamageAnims=damageAnims, showDamageExtraTime=1)
    notifyTrack = Sequence(Wait(3.1), Func(toon.showHpTextCheat, - int(dmg / 2.33)), Func(toon.showHpString, "VULNERABLE!"))
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitTrack.append(Wait(2))
    suitTrack.append(doBayouBashSnap(attack))
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack, notifyTrack)

def doSnapSoaked(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    teeth = globalPropPool.getProp('litigator-teeth')
    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.55
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4),
                                                   scaleUpTime=propScaleUpTime))
    teethAppearTrack.append(Wait(suitDelay))
    teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
    teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
    if dmg > 0:
        x = toon.getX(battle)
        y = toon.getY(battle)
        z = toon.getZ(battle)
        toonHeight = z + toon.getHeight()
        flyPoint = Point3(x, y + 2.7, toonHeight * 0.7)
        teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
        teethAppearTrack.append(Wait(0.2))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y, toonHeight + 3)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 1.2, toonHeight * 0.7)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.7, toonHeight * 0.4)))
        teethAppearTrack.append(Wait(0.4))
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)), Wait(0.9),
                              LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)), Wait(1.2),
                              LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
        hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2),
                            LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6),
                            LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration),
                             ActorInterval(teeth, 'litigator-teeth', duration=0.3), Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7),
                             ActorInterval(teeth, 'litigator-teeth', duration=0.9))
        propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
                             Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
    else:
        x = toon.getX(battle)
        y = toon.getY(battle)
        z = toon.getZ(battle)
        z = z + 0.2
        flyPoint = Point3(x, y - 2.1, z)
        teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
        teethAppearTrack.append(Wait(0.2))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.5, y - 2.5, z)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.0, y - 3.0, z + 0.4)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.3, y - 3.6, z)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.9, y - 3.1, z + 0.4)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.3, y - 2.6, z)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.1, y - 2.2, z + 0.4)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.4, y - 1.9, z)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.7, y - 2.1, z + 0.4)))
        teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.8, y - 2.3, z)))
        teethAppearTrack.append(LerpScaleInterval(teeth, 0.6, MovieUtil.PNT3_NEARZERO))
        hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.5),
                            LerpHprInterval(teeth, 0.4, Point3(80, 0, 0), startHpr=Point3(180, 0, 0)),
                            LerpHprInterval(teeth, 0.8, Point3(-10, 0, 0), startHpr=Point3(80, 0, 0)))
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=3.6))
        propTrack = Sequence(Parallel(teethAppearTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth),
                             Func(battle.movie.clearRenderProp, teeth))
    damageAnims = [['cringe',
                    0.01,
                    0.7,
                    1.2],
                   ['spit',
                    0.01,
                    2.95,
                    1.47],
                   ['spit',
                    0.01,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit', 0.01, 4.42]]
    dodgeAnims = [['jump', 0.01, 0.01]]
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 1.93), 2.1, splicedDamageAnims=damageAnims, showDamageExtraTime=1)
    notifyTrack = Sequence(Wait(3.1), Func(toon.showHpTextCheat, - int(dmg / 1.93)),
                           Func(toon.showHpString, "VULNERABLE!"))
    soundTrack = getSoundTrack('SA_chomp.ogg', delay=2, node=suit)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitTrack.append(Wait(2))
    suitTrack.append(doBayouBashSnap(attack))
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack, notifyTrack)

def doSnapBellow(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    teeth = globalPropPool.getProp('litigator-teeth')
    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.55
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4),
                                                   scaleUpTime=propScaleUpTime))
    teethAppearTrack.append(Wait(suitDelay))
    teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
    teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
    x = toon.getX(battle)
    y = toon.getY(battle)
    z = toon.getZ(battle)
    toonHeight = z + toon.getHeight()
    flyPoint = Point3(x, y + 2.7, toonHeight * 0.7)
    teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
    teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
    teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
    teethAppearTrack.append(Wait(0.2))
    teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y, toonHeight + 3)))
    teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 1.2, toonHeight * 0.7)))
    teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.7, toonHeight * 0.4)))
    teethAppearTrack.append(Wait(0.4))
    scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)), Wait(0.9),
                          LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)), Wait(1.2),
                          LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
    hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2),
                        LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.6),
                        LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
    animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration),
                         ActorInterval(teeth, 'litigator-teeth', duration=0.3), Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7),
                         ActorInterval(teeth, 'litigator-teeth', duration=0.9))
    propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
                         Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
    damageAnims = [['cringe',
                    0.01,
                    0.7,
                    1.2],
                   ['spit',
                    0.01,
                    2.95,
                    1.47],
                   ['spit',
                    0.01,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit', 0.01, 4.42]]
    dodgeAnims = [['cringe',
                    0.01,
                    0.7,
                    1.2],
                   ['spit',
                    0.01,
                    2.95,
                    1.47],
                   ['spit',
                    0.01,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit', 0.01, 4.42]]
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2.2),
                                            2.1, splicedDamageAnims=damageAnims, showDamageExtraTime=1)
    notifyTrack = Sequence(Wait(3.1), Func(toon.showHpTextCheat, - int(dmg / 2.2)),
                           Func(toon.showHpString, "VULNERABLE!"))
    soundTrack = getSoundTrack('SA_chomp.ogg', delay=2, node=suit)
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    speechTrack = Sequence(Func(suit.setChatAbsolute, getAttackTaunt('Snap', attack['suitName']), CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2))
    suitTrack.append(doBayouBash(attack))
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack, notifyTrack, speechTrack)

def doChomp(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.55
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    posPoints = [Point3(-0.35, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(4, 4, 4),
                                                       scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.7)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y, toonHeight + 3)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 1.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.7, toonHeight * 0.4)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(6, 6, 6)), Wait(0.9),
                                  LerpScaleInterval(teeth, 0.2, Point3(10, 10, 10)), Wait(1.2),
                                  LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2),
                                LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.1),
                                LerpHprInterval(teeth, 0.1, Point3(0, -35, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration),
                                 ActorInterval(teeth, 'teeth', duration=0.3),
                                 Func(teeth.pose, 'teeth', 1), Wait(0.7),
                                 ActorInterval(teeth, 'teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack),
                                 Func(MovieUtil.removeProp, teeth), Func(battle.movie.clearRenderProp, teeth))
        else:
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            z = z + 0.2
            flyPoint = Point3(x, y - 2.1, z)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.5, y - 2.5, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.0, y - 3.0, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 1.3, y - 3.6, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.9, y - 3.1, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x + 0.3, y - 2.6, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.1, y - 2.2, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.4, y - 1.9, z)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.7, y - 2.1, z + 0.4)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.2, pos=Point3(x - 0.8, y - 2.3, z)))
            teethAppearTrack.append(LerpScaleInterval(teeth, 0.6, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.5),
                                LerpHprInterval(teeth, 0.4, Point3(80, 0, 0), startHpr=Point3(180, 0, 0)),
                                LerpHprInterval(teeth, 0.8, Point3(-10, 0, 0), startHpr=Point3(80, 0, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=3.6))
            propTrack = Sequence(Parallel(teethAppearTrack, hprTrack, animTrack), Func(MovieUtil.removeProp, teeth),
                                 Func(battle.movie.clearRenderProp, teeth))
        propTracks.append(propTrack)

    damageAnims = [['cringe',
                    0.01,
                    0.7,
                    1.2],
                   ['spit',
                    0.01,
                    2.95,
                    1.47],
                   ['spit',
                    0.01,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit', 0.01, 4.42]]
    dodgeAnims = [['jump', 0.01, 0.01]]
    toonTracks = getToonTracks(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.75,
                               splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.4)
    soundTrack = getSoundTrack('SA_chomp.ogg', delay=2, node=suit)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks)

def doInject(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    laptop = globalPropPool.getProp('laptop')
    card = globalPropPool.getProp('ttht_m_ene_techbotLaptop')
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect, 'audit-one', color=Vec4(0, 0, 0, 1))
    particleEffect2 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect2, 'audit-two', color=Vec4(0, 0, 0, 1))
    particleEffect3 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect3, 'audit-three', color=Vec4(0, 0, 0, 1))
    particleEffect4 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect4, 'audit-four', color=Vec4(0, 0, 0, 1))
    particleEffect5 = BattleParticles.createParticleEffect('Calculate')
    BattleParticles.setEffectTexture(particleEffect5, 'audit-mult', color=Vec4(0, 0, 0, 1))
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTrack = getPartTrack(particleEffect, 1.5, 1.5, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 1.6, 1.5, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 1.7, 1.6, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, 1.8, 1.7, [particleEffect4, suit, 0])
    partTrack5 = getPartTrack(particleEffect5, 1.9, 1.8, [particleEffect5, suit, 0])
    laptopPosPoints = [Point3(0, 0.75, -0.2), VBase3(0, 0, 180)]
    laptopDuration = 2.8
    scaleUpPoint = Point3(1.5, 1.5, 1.5)
    damageAnims = []
    damageAnims.append(['cringe'])
    soundTrack = getSoundTrack('SA_keyPunch.ogg', node=suit)
    propTrackNew = Parallel()
    propTrackNew.append(getPropTrack(card, suit.getLeftHand(), laptopPosPoints, 1e-06, 2, scaleUpPoint=scaleUpPoint, scaleUpTime=0,
                                              anim=1, animStartTime=0.5, animDuration=2.5,
                                              propName='ttht_m_ene_techbotLaptop'))
    #calcPropTrack = getPropTrack(laptop, suit.getLeftHand(), laptopPosPoints, 1e-06, laptopDuration, scaleUpPoint=scaleUpPoint, anim=0, propName='laptop', animStartTime=0, animDuration=0)
    toonTrack = getToonTrack(attack, 2.8, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['jump'])
    return Parallel(suitTrack, toonTrack, soundTrack, propTrackNew, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)

def doEvictionNotice(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.25, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
    propTrack.append(Wait(1.55))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.5, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle))
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
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Zap Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                      "Quality Control has classified that all Sound gags are now classified as defective.",
                                      CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'csm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    elif attack['suit'].dna.name == 'fbd':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack2))
    toonTrack = getToonTrack(attack, 2, ['conked'], 2, ['jump'])
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack)
    else:
        return Parallel(suitTrack, toonTrack, propTrack)

def doEvictionNoticeInsurance(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('shredder-paper')
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    headsUp = Func(suit.headsUp, battle, targetPos)
    tauntInterval = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'throw-paper', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.25, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
    propTrack.append(Wait(1.55))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.5, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle))
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
    suitTrack.append(Wait(1.5))
    if suit.isSkeleton:
        suitTrack.append(doCaseInsurancePlanSkelecog(attack))
    else:
        suitTrack.append(doCaseInsurancePlan(attack))
    toonTrack = getToonTrack(attack, 2, ['conked'], 2, ['jump'])
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack)
    else:
        return Parallel(suitTrack, toonTrack, propTrack)

def doEvictionNoticeExplodingBill(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('shredder-paper')
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'throw-paper', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.25, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
    propTrack.append(Wait(1.55))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.5, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle))
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
    suitTrack.append(Wait(1.5))
    suitTrack.append(doExplodingBill(attack))
    toonTrack = getToonTrack(attack, 2, ['conked'], 2, ['jump'])
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack)
    else:
        return Parallel(suitTrack, toonTrack, propTrack)


def doInsurancePlan(attack):
    if attack['suitName'] == 'csm':
        suitTrack = doCaseInsurancePlan(attack)
    elif attack['suitName'] == 'cm':
        suitTrack = doCaseInsurancePlan(attack)
    else:
        suitTrack = doOtherInsurancePlan(attack)
    return suitTrack


def doCloseTheLoopNew(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    target = attack['target']
    taunt = random.choice(["Don't bring a Gag to a knife fight.",
"Get to the point!",
"I have some sharp words for you.",
"I won't fall for your childish pranks.",
"I'll use this occasion to sharpen my skills.",
"I'm the sharpest Suit around!",
"It's knife to meet you.",
"My tactics are on the cutting edge.",
"This attack is a cut above the rest.",
"Toons like you can't cut it with us.",
"Twice the pride, double the fall.",
"You'll find that this company never cuts corners.",
"Your chances of victory are in free fall."])
    taunt2 = random.choice(['Let me loop you in on how things work.',
 'This ought to throw you in for a loop.',
 "Oh my, you're really out of the loop!",
 'Found a loophole in the system? Time to close it.',
 "Now I'm closing in on you!"])
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    tauntInterval2 = Func(suit.setChatAbsolute, taunt2, CFSpeech | CFTimeout)
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'effort', duration=2.5, playRate=1.5), tauntInterval2, ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    allKnifeTracks = Parallel()
    toon = target[0]['toon']
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
            Wait(i * 0.1),
            Func(knife.reparentTo, battle),
            Func(knife.setPos, Point3(x, y, 1.0)),
            Func(knife.lookAt, Point3(toon.getX(battle), toon.getY(battle), 1.0)),
            Func(base.playSfx, globalBattleSoundCache.getSound('SA_wire_cut_knife.ogg'), node=toon),
            LerpScaleInterval(knife, 0.25, Point3(0.5), startScale=Point3(0.01)),
            ))

    knifeTracks.append(prepareKnives)
    knifeTracks.append(Wait(1.7))
    closeTrack = Parallel()
    for knife in knives:
        closeTrack.append(Sequence(
                LerpPosInterval(knife, 0.2, Point3(toon.getX(battle), toon.getY(battle), 1.0), blendType='easeIn'),
                Func(MovieUtil.removeProp, knife)
            ))

    knifeTracks.append(closeTrack)
    allKnifeTracks.append(knifeTracks)

    damageAnims = [['slip-backward', 0.01, 0.6]]
    partTracks = Parallel()
    toonTracks = getToonTrack(attack, damageDelay=3.55, splicedDamageAnims=damageAnims, dodgeDelay=2.2,
                               dodgeAnimNames=['jump'])
    soundTracks = Parallel()
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(20)
    sparks.setLitterSize(20)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    partTracks.append(Sequence(
            Wait(3.55),
            Parallel(
                ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                autoFinish=1
            )
        ))
    soundTracks.append(getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=3.55, node=toon))
    name = attack['id']
    if name == DETONATE_3:
        suitTrack.append(Wait(2))
        suitTrack.append(doRefinement(attack))
    if name == REFINEMENT:
        suitTrack.append(Wait(2))
        suitTrack.append(doRefinement(attack))
    if name == MANAGERIAL_PROTECTION:
        suitTrack.append(Wait(2))
        suitTrack.append(doManagerialProtection(attack))
    return Parallel(suitTrack, allKnifeTracks, partTracks, toonTracks, soundTracks)

def doCloseTheLoopBombCake(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    target = attack['target']
    taunt = random.choice(["Don't bring a Gag to a knife fight.",
"Get to the point!",
"I have some sharp words for you.",
"I won't fall for your childish pranks.",
"I'll use this occasion to sharpen my skills.",
"I'm the sharpest Suit around!",
"It's knife to meet you.",
"My tactics are on the cutting edge.",
"This attack is a cut above the rest.",
"Toons like you can't cut it with us.",
"Twice the pride, double the fall.",
"You'll find that this company never cuts corners.",
"Your chances of victory are in free fall."])
    taunt2 = random.choice(['Let me loop you in on how things work.',
 'This ought to throw you in for a loop.',
 "Oh my, you're really out of the loop!",
 'Found a loophole in the system? Time to close it.',
 "Now I'm closing in on you!"])
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    tauntInterval2 = Func(suit.setChatAbsolute, taunt2, CFSpeech | CFTimeout)
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'effort', duration=2.5, playRate=1.5), tauntInterval2, ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    allKnifeTracks = Parallel()
    toon = target[0]['toon']
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
            Wait(i * 0.1),
            Func(knife.reparentTo, battle),
            Func(knife.setPos, Point3(x, y, 1.0)),
            Func(knife.lookAt, Point3(toon.getX(battle), toon.getY(battle), 1.0)),
            Func(base.playSfx, globalBattleSoundCache.getSound('SA_wire_cut_knife.ogg'), node=toon),
            LerpScaleInterval(knife, 0.25, Point3(0.5), startScale=Point3(0.01)),
            ))

    knifeTracks.append(prepareKnives)
    knifeTracks.append(Wait(1.7))
    closeTrack = Parallel()
    for knife in knives:
        closeTrack.append(Sequence(
                LerpPosInterval(knife, 0.2, Point3(toon.getX(battle), toon.getY(battle), 1.0), blendType='easeIn'),
                Func(MovieUtil.removeProp, knife)
            ))

    knifeTracks.append(closeTrack)
    allKnifeTracks.append(knifeTracks)

    damageAnims = [['slip-backward', 0.01, 0.6]]
    partTracks = Parallel()
    toonTracks = getToonTrack(attack, damageDelay=3.55, splicedDamageAnims=damageAnims, dodgeDelay=2.2,
                               dodgeAnimNames=['jump'])
    soundTracks = Parallel()
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(20)
    sparks.setLitterSize(20)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    partTracks.append(Sequence(
            Wait(3.55),
            Parallel(
                ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                autoFinish=1
            )
        ))
    soundTracks.append(getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=3.55, node=toon))
    suitTrack.append(Wait(2))
    suitTrack.append(doBombCake(attack))
    return Parallel(suitTrack, allKnifeTracks, partTracks, toonTracks, soundTracks)

def doCloseTheLoopPiano(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    target = attack['target']
    taunt = random.choice(["Don't bring a Gag to a knife fight.",
"Get to the point!",
"I have some sharp words for you.",
"I won't fall for your childish pranks.",
"I'll use this occasion to sharpen my skills.",
"I'm the sharpest Suit around!",
"It's knife to meet you.",
"My tactics are on the cutting edge.",
"This attack is a cut above the rest.",
"Toons like you can't cut it with us.",
"Twice the pride, double the fall.",
"You'll find that this company never cuts corners.",
"Your chances of victory are in free fall."])
    taunt2 = random.choice(['Let me loop you in on how things work.',
 'This ought to throw you in for a loop.',
 "Oh my, you're really out of the loop!",
 'Found a loophole in the system? Time to close it.',
 "Now I'm closing in on you!"])
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    tauntInterval2 = Func(suit.setChatAbsolute, taunt2, CFSpeech | CFTimeout)
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'effort', duration=2.5, playRate=1.5), tauntInterval2, ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    allKnifeTracks = Parallel()
    toon = target[0]['toon']
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
            Wait(i * 0.1),
            Func(knife.reparentTo, battle),
            Func(knife.setPos, Point3(x, y, 1.0)),
            Func(knife.lookAt, Point3(toon.getX(battle), toon.getY(battle), 1.0)),
            Func(base.playSfx, globalBattleSoundCache.getSound('SA_wire_cut_knife.ogg'), node=toon),
            LerpScaleInterval(knife, 0.25, Point3(0.5), startScale=Point3(0.01)),
            ))

    knifeTracks.append(prepareKnives)
    knifeTracks.append(Wait(1.7))
    closeTrack = Parallel()
    for knife in knives:
        closeTrack.append(Sequence(
                LerpPosInterval(knife, 0.2, Point3(toon.getX(battle), toon.getY(battle), 1.0), blendType='easeIn'),
                Func(MovieUtil.removeProp, knife)
            ))

    knifeTracks.append(closeTrack)
    allKnifeTracks.append(knifeTracks)

    damageAnims = [['slip-backward', 0.01, 0.6]]
    partTracks = Parallel()
    toonTracks = getToonTrack(attack, damageDelay=3.55, splicedDamageAnims=damageAnims, dodgeDelay=2.2,
                               dodgeAnimNames=['jump'])
    soundTracks = Parallel()
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(20)
    sparks.setLitterSize(20)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    partTracks.append(Sequence(
            Wait(3.55),
            Parallel(
                ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                autoFinish=1
            )
        ))
    soundTracks.append(getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=3.55, node=toon))
    suitTrack.append(Wait(2))
    suitTrack.append(doNotThrowPiano(attack))
    return Parallel(suitTrack, allKnifeTracks, partTracks, toonTracks, soundTracks)

def doCloseTheLoopPhase2(attack):
    suit = attack['suit']
    battle = attack['battle']
    name = attack['id']
    target = attack['target']
    taunt = random.choice(["Don't bring a Gag to a knife fight.",
"Get to the point!",
"I have some sharp words for you.",
"I won't fall for your childish pranks.",
"I'll use this occasion to sharpen my skills.",
"I'm the sharpest Suit around!",
"It's knife to meet you.",
"My tactics are on the cutting edge.",
"This attack is a cut above the rest.",
"Toons like you can't cut it with us.",
"Twice the pride, double the fall.",
"You'll find that this company never cuts corners.",
"Your chances of victory are in free fall."])
    taunt2 = random.choice(['Let me loop you in on how things work.',
 'This ought to throw you in for a loop.',
 "Oh my, you're really out of the loop!",
 'Found a loophole in the system? Time to close it.',
 "Now I'm closing in on you!"])
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    tauntInterval2 = Func(suit.setChatAbsolute, taunt2, CFSpeech | CFTimeout)
    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'effort', duration=2.5, playRate=1.5), tauntInterval2, ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    allKnifeTracks = Parallel()
    toon = target[0]['toon']
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
            Wait(i * 0.1),
            Func(knife.reparentTo, battle),
            Func(knife.setPos, Point3(x, y, 1.0)),
            Func(knife.lookAt, Point3(toon.getX(battle), toon.getY(battle), 1.0)),
            Func(base.playSfx, globalBattleSoundCache.getSound('SA_wire_cut_knife.ogg'), node=toon),
            LerpScaleInterval(knife, 0.25, Point3(0.5), startScale=Point3(0.01)),
            ))

    knifeTracks.append(prepareKnives)
    knifeTracks.append(Wait(1.7))
    closeTrack = Parallel()
    for knife in knives:
        closeTrack.append(Sequence(
                LerpPosInterval(knife, 0.2, Point3(toon.getX(battle), toon.getY(battle), 1.0), blendType='easeIn'),
                Func(MovieUtil.removeProp, knife)
            ))

    knifeTracks.append(closeTrack)
    allKnifeTracks.append(knifeTracks)

    damageAnims = [['slip-backward', 0.01, 0.6]]
    partTracks = Parallel()
    toonTracks = getToonTrack(attack, damageDelay=3.55, splicedDamageAnims=damageAnims, dodgeDelay=2.2,
                               dodgeAnimNames=['jump'])
    soundTracks = Parallel()
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(20)
    sparks.setLitterSize(20)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    partTracks.append(Sequence(
            Wait(3.55),
            Parallel(
                ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                autoFinish=1
            )
        ))
    soundTracks.append(getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=3.55, node=toon))
    phase2 = Func(suit.makeChairmanPhase2)
    ceaseTrack = ActorInterval(suit, 'soak', playRate=1.5)
    ceaseSpeechTrack = Sequence(Func(suit.setChatAbsolute,
                                     "You Toons have put up a good fight, but this foolishness must end.",
                                     CFSpeech | CFTimeout), Wait(3.0), Func(suit.setNeutralAnimation), Func(suit.setChatAbsolute,
                                                                     "This ends here and now!",
                                                                     CFSpeech | CFTimeout),
                                Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(Parallel(ceaseTrack, phase2, ceaseSpeechTrack))
    suitTrack.append(Func(suit.showHpString, "2.0x DMG MULTIPLIER!"))
    suitTrack.append(ActorInterval(suit, 'rake-react'))
    suitTrack.append(Func(suit.setNeutralAnimation))
    return Parallel(suitTrack, allKnifeTracks, partTracks, toonTracks, soundTracks)


def doCaseInsurancePlan(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    if attack['suitName'] == 'csm':
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
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'scg':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
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
        else:
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
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
        if not suit.dna.name == 'csm':
            suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(MovieUtil.createSuitInsuranceInterval(theSuit))
        suitTracks.append(Wait(6.5))
    ceaseTracks = Sequence(Wait(6.5))
    ceaseTrack = ActorInterval(theSuit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=theSuit))
    ceaseSpeechTrack = Parallel(Func(theSuit.setChatAbsolute,
                                         'Any Sound and Zap Gags Toons use can and will be held against them in a court of law.',
                                         CFSpeech | CFTimeout))
    ceaseTracks.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
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
    suitTrack.append(doCaseFiles(attack))
    #insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
    soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, multiTrack, knifeTracks)

def doCaseInsurancePlanSkelecog(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    if attack['suitName'] == 'csm':
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
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'scg':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
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
        else:
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
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
        if not suit.dna.name == 'csm':
            suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
        suitTracks.append(Wait(6.5))
    ceaseTracks = Sequence(Wait(6.5))
    ceaseTrack = ActorInterval(theSuit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=theSuit))
    ceaseSpeechTrack = Parallel(Func(theSuit.setChatAbsolute,
                                         'Any Sound and Zap Gags Toons use can and will be held against them in a court of law.',
                                         CFSpeech | CFTimeout))
    ceaseTracks.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
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
    suitTrack.append(doCaseFiles(attack))
    #insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
    soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, multiTrack, knifeTracks)

def doCaseInsurancePlanInsurance(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    if attack['suitName'] == 'csm':
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
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP) and not suit.isLured:
            suitTrack.append(Func(suit.showHpText, 0))
        elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP) and not suit.isLured:
            suitTrack.append(Func(suit.setHealthForMe, x))
        elif not suit.isLured:
            suitTrack.append(Func(suit.setHealthForMe, 50))
        suitTrack.append(Func(suit.showHpTextWhite, "INSURANCE!", 0))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'csm':
            suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(suit.makeInsured))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(MovieUtil.createSuitInsuranceInterval(theSuit))
        suitTracks.append(Wait(6.5))
    ceaseTracks = Sequence(Wait(6.5))
    ceaseTrack = ActorInterval(theSuit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=theSuit))
    ceaseSpeechTrack = Parallel(Func(theSuit.setChatAbsolute,
                                         'Any Toon-Up and Squirt Gags Toons use can and will be held against them in a court of law.',
                                         CFSpeech | CFTimeout))
    ceaseTracks.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
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
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, ceaseTracks, multiTrack, knifeTracks)

def doCaseInsurancePlanSkelecogInsurance(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    if attack['suitName'] == 'csm':
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
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP) and not suit.isLured and not suit.isInsured:
            suitTrack.append(Func(suit.showHpText, 0))
        elif suit.currHP + 50 > (suit.maxHP * suit.hardMaxHP) and not suit.isLured and not suit.isInsured:
            suitTrack.append(Func(suit.setHealthForMe, x))
        elif not suit.isLured:
            suitTrack.append(Func(suit.setHealthForMe, 50))
        suitTrack.append(Func(suit.showHpTextWhite, "INSURANCE!", 0))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'csm':
            suitTrack.append(Parallel(Sequence(Wait(4.0)), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(suit.makeInsured))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
        suitTracks.append(Wait(6.5))
    ceaseTracks = Sequence(Wait(6.5))
    ceaseTrack = ActorInterval(theSuit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=theSuit))
    ceaseSpeechTrack = Parallel(Func(theSuit.setChatAbsolute,
                                         'Any Sound and Zap Gags Toons use can and will be held against them in a court of law.',
                                         CFSpeech | CFTimeout))
    ceaseTracks.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
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
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, ceaseTracks, multiTrack, knifeTracks)

def doContractEnforcement(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    taunt = random.choice(
        ["We all need a little healing sometimes.", "The union ensures that all employees receive health benefits, we must shut them down.",
         "All employees are receiving a raise, effective immediately."])

    suitTracks = Parallel()
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'scg':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                suitTrack.append(Func(suit.showHpText, 0))
                suitTrack.append(Func(suit.showHpString, "CONTRACTED!"))
            elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                suitTrack.append(Func(suit.showHpTextCheat, x))
                suitTrack.append(Func(suit.showHpString, "CONTRACTED!"))
                suitTrack.append(Func(suit.setHealthForMe, x))
            else:
                suitTrack.append(Func(suit.showHpTextCheat, 125))
                suitTrack.append(Func(suit.showHpString, "CONTRACTED!"))
                suitTrack.append(Func(suit.setHealthForMe, 125))
        else:
            x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
            if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
                suitTrack.append(Func(suit.showHpText, 0))
            elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
                suitTrack.append(Func(suit.showHpTextCheat, x))
                suitTrack.append(Func(suit.showHpString, "CONTRACTED!"))
                suitTrack.append(Func(suit.setHealthForMe, x))
            else:
                suitTrack.append(Func(suit.showHpTextCheat, 125))
                suitTrack.append(Func(suit.showHpString, "CONTRACTED!"))
                suitTrack.append(Func(suit.setHealthForMe, 125))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'dsk':
            suitTrack.append(Parallel(Sequence(Wait(4.0)),
                                      Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                           CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(ActorInterval(theSuit, 'throw-paper'))
        suitTracks.append(Wait(6.5))
    ceaseTracks = Sequence(Wait(6.5))
    ceaseTrack = ActorInterval(theSuit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=theSuit))
    ceaseSpeechTrack = Parallel(Func(theSuit.setChatAbsolute,
                                          'Quality Control dictates that all Squirt and Zap gags are now classified as defective.',
                                         CFSpeech | CFTimeout))
    ceaseTracks.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
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
    suitTrack = Sequence(Wait(6.0), Func(suit.setNeutralAnimation))
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    healSound = Sequence(Wait(4.5), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, ceaseTracks, soundTrack2, knifeTracks)


def doHeadHonchoCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    dmg = target[0]['hp']
    taunt = getAttackTaunt('CigarSmoke', attack['suitName'], tauntIndex)
    BattleParticles.loadParticles()
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    #cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    #cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.6, 3.6,
                                  #scaleUpPoint=Point3(6.0, 6.0, 6.0))
    toonTrack = getToonTrack(attack, 2.55, ['cringe'], 2.0, ['sidestep'])
    smokeTrack = getPartTrack(smoke, 2.45, 1.5, [smoke, suit, 0])
    suitTracks = Parallel()
    multiTrackList = Parallel(suitTracks, toonTrack)
    multiTrackList.append(smokeTrack)
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    suitTrack = Sequence()
    suitTracks.append(headsUp)
    suitTracks.append(suitTrack)
    suitTracks.append(tauntInterval)
    suitTracks.append(MovieUtil.createSuitHeadHonchoCigarSmokeInterval(suit))
    suitTracks.append(suitReset)

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

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(2.6))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(2.2))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        multiTrackList.append(colorTrack)
    return multiTrackList

def doFirestarterCigarSmoke(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    dmg = target[0]['hp']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    BattleParticles.loadParticles()
    smoke = BattleParticles.createParticleEffect('Smoke')
    BattleParticles.setEffectTexture(smoke, 'snow-particle')
    # cigar = globalPropPool.getProp('cigar')
    cigarPosPoints = [Point3(-0.05, -0.2, -0.25), VBase3(180.0, 0.0, 0.0)]
    # cigarPropTrack = getPropTrack(cigar, suit.getRightHand(), cigarPosPoints, 0.6, 3.6,
    # scaleUpPoint=Point3(6.0, 6.0, 6.0))
    toonTrack = getToonTrack(attack, 3.55, ['cringe'], 3.0, ['sidestep'])
    smokeTrack = getPartTrack(smoke, 3.45, 1.5, [smoke, suit, 0])
    suitTracks = Parallel()
    multiTrackList = Parallel(suitTracks, toonTrack)
    multiTrackList.append(smokeTrack)
    tauntInterval = Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout)
    suitTrack = Sequence()
    suitTracks.append(suitTrack)
    suitTracks.append(tauntInterval)
    suitTracks.append(MovieUtil.createSuitFirestarterCigarSmokeInterval(suit))

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

    if dmg > 0:
        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Wait(3.6))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(2.2))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        multiTrackList.append(colorTrack)
    return multiTrackList

def doOtherInsurancePlan(attack):
    suit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(3))
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
            suit.setHealthForMe(int(suit.currHP + 0))
            suitTrack.append(Func(suit.showHpText, 0))
        elif suit.currHP + 75 > (suit.maxHP * suit.hardMaxHP):
            suit.setHealthForMe(int(suit.currHP + x))
            suitTrack.append(Func(suit.showHpText, x))
        else:
            suit.setHealthForMe(int(suit.currHP + 75))
            suitTrack.append(Func(suit.showHpText, 75))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Parallel(Sequence(Wait(3)),
                                  Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
        suitTrack.append(Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        suitTracks.append(suitTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack), ActorInterval(suit, 'neutral'))
    soundTrack1 = getSoundTrack('SA_paper_throw.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('SA_extra_tip.ogg', delay=1.5, node=suit)
    #multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(3.0), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=suit))
    return Parallel(suitTrack, suitTracks, healSound, soundTrack)

def doRefinement(attack):
    theSuit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        x = int((suit.maxHP * suit.hardMaxHP) - suit.currHP)
        if suit.currHP >= (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpText, 0))
            suitTrack.append(Func(suit.showHpString, "REFINED!"))
        elif suit.currHP + 125 > (suit.maxHP * suit.hardMaxHP):
            suitTrack.append(Func(suit.showHpTextCheat, x))
            suitTrack.append(Func(suit.showHpString, "REFINED!"))
            suitTrack.append(Func(suit.setHealthForMe, x))
        else:
            suitTrack.append(Func(suit.showHpTextCheat, 125))
            suitTrack.append(Func(suit.showHpString, "REFINED!"))
            suitTrack.append(Func(suit.setHealthForMe, 125))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'gtk':
            suitTrack.append(Parallel(Sequence(Wait(3)),
                                  Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases), CFSpeech | CFTimeout)))
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
    name = attack['id']
    suitTrackAnim = Sequence(Func(theSuit.setChatAbsolute, taunt, CFSpeech | CFTimeout),
                         ActorInterval(theSuit, 'throw-object', playRate=1.5))
    if name == DETONATE_3:
        ambassadorPhase3 = Func(theSuit.makeAmbassadorPhase3)
        soundTrack3 = getSoundTrack('ENC_cogfall_apart.ogg', node=theSuit)
        suitTrackAnim.append(Wait(4))
        suitTrackAnim.append(Func(theSuit.showHpString, "1.5x DMG MULTIPLIER!"))
        suitTrackAnim.append(MovieUtil.createAmbassadorReviveTrack(theSuit, battle))
        suitTrackAnim.append(Wait(2))
        suitTrackAnim.append(Parallel(Func(theSuit.updateHealthBar, 0), ActorInterval(theSuit, 'frustrated'), Func(theSuit.setChatAbsolute, "I've had enough of all of this!!! You Toons are in for a rude awakening now!!!", CFSpeech | CFTimeout)))
    soundTrack1 = getSoundTrack('SA_repair.ogg', delay=2.5, node=theSuit)
    soundTrack2 = getSoundTrack('SA_refinement.ogg', delay=2, node=theSuit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    return Parallel(suitTrackAnim, makeUnVulnerable, suitTracks, multiTrack, knifeTracks)


def doNotThrowPiano(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 1.2
    propDelay = 0.6
    throwDuration = 1.5
    piano = globalPropPool.getProp('piano')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "So, I see you are very reliant on your Drop gags. Let's see how you do without them.",
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'tcm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    posPoints = [Point3(-0.35, 0.25, 0), VBase3(180.00, -90, 0)]
    paperTrack = Sequence(
        getPropAppearTrack(piano, suit.getRightHand(), posPoints, propDelay, Point3(.5, .5, .5), scaleUpTime=0.25))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 1.2)
    hitPoint.setY(hitPoint.getY() + 1.5)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ() + 1.1)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, piano))
    paperTrack.append(Func(piano.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(piano, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(piano, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(piano, throwDuration, Point3(180, 90, 90)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(piano, throwDuration, Point3(6, 6, 6)),
                         Wait(0.95), LerpScaleInterval(piano, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, piano),
                         Func(battle.movie.clearRenderProp, piano))
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
    toonTrack = getToonTrack(attack, damageDelay=3.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4,
                             dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    soundTrack = getSoundTrack('AA_drop_piano_miss.ogg', delay=3.1, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doThrowMoney(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    bill = globalPropPool.getProp('1dollar')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.01, -0.35, 0.15), VBase3(10.584, -11.945, 18.316)]
    propTrack = Sequence(
        getPropAppearTrack(bill, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, bill, [hitPoint], [missPoint], parent=battle))
    toonTrack = getToonTrack(attack, 3.4, ['cringe'], 2.8, ['duck'])
    soundTrack = getSoundTrack('SA_pick_pocket.ogg', delay=2.6, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doAmandasDoughnuts(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    doughnut = globalPropPool.getProp('doughnut')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.01, -0.85, 0.15), VBase3(10.584, -11.945, 18.316)]
    propTrack = Sequence(
        getPropAppearTrack(doughnut, suit.getRightHand(), posPoints, 0.8, MovieUtil.PNT3_ONE, scaleUpTime=0.5))
    propTrack.append(Wait(1.73))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, doughnut, [hitPoint], [missPoint], parent=battle))
    damageAnims = [['spit',
                    0.01,
                    2.95,
                    1.47],
                   ['spit',
                    0.01,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit',
                    0.08,
                    4.42,
                    0.07],
                   ['spit',
                    0.08,
                    4.49,
                    -0.07],
                   ['spit', 0.01, 4.42]]
    dodgeAnims = [['jump', 0.01, 0.01]]
    toonTrack = getToonTrack(attack, damageDelay=3.2, splicedDamageAnims=damageAnims, dodgeDelay=2.75,
                             splicedDodgeAnims=dodgeAnims, showDamageExtraTime=1.4)
    soundTrack = getSoundTrack('SA_doughnuts.ogg', delay=0.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack)


def doBombCake(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(2.5))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    cake = globalPropPool.getProp('birthday-cake')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "So, I see you are very reliant on your Throw gags. Let's see how you do without them.",
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'tcm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    posPoints = [Point3(-0.35, 0, -0.25), VBase3(180.00, 180, 0.00)]
    propTrack = Sequence(
        getPropAppearTrack(cake, suit.getRightHand(), posPoints, 0.75, Point3(.5, .5, .5), scaleUpTime=0.25))
    propTrack.append(Wait(1.13))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, cake, [hitPoint], [missPoint], .25, parent=battle))
    toonTrack = getToonTrack(attack, 2.8, ['slip-backward'], 2.2, ['jump'])
    soundTrack = getSoundTrack('AA_cake.ogg', delay=2.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=2.5, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, propTrack, explosionTrack, soundTrack1)


def doBomb(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    toonPos = toon.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(0.8))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
    explosionTrack2 = Sequence()
    explosionTrack2.append(Wait(1.5))
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
        explodeTrack.append(Wait(0.8))
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
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.showHpTextCheat, - (dmg * 4)), Func(suit.showHpString, "BOMBED!"), Func(suit.setHealthForMe, - (dmg * 4)), ActorInterval(suit, 'slip-backward'), Func(suit.setNeutralAnimation))
    suitTrack.append(Func(suit.setNeutralAnimation))
    suitTrack.append(Func(suit.makeUnShielding))
    revives = suit.getMaxSkeleRevives() + 1
    if suit.isVirtual and revives > 2:
        suitTrack.append(Func(suit.checkCogHPLaser, battle))
    elif suit.isSkeleton and revives > 2:
        suitTrack.append(Func(suit.checkCogHPLaserRevive, battle))
    elif not suit.isSkeleton and revives > 1:
        suitTrack.append(Func(suit.checkCogHPRevive, battle))
    elif suit.isVirtual:
        suitTrack.append(Func(suit.checkCogHPLaser, battle))
    elif not suit.isVirtual:
        suitTrack.append(Func(suit.checkCogHPBomb, battle))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 6 and 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'blr':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    posPoints = [Point3(-0.04, -0.15, -0.78), VBase3(10.584, -11.945, 18.316)]
    propTrack = Sequence(
        getPropAppearTrack(tnt, suit.getRightHand(), posPoints, 0.1, MovieUtil.PNT3_ONE, scaleUpTime=0.1))
    propTrack.append(Wait(0.1))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
    toonTrack = getToonTrack(attack, 0.5, ['slip-forward'], 0.5, ['jump'])
    soundTrack = getSoundTrack('ENC_cogfall_apart.ogg', delay=0.5, node=suit)
    soundTrack2 = getSoundTrack('ENC_cogfall_apart.ogg', delay=1.5, node=suit)
    return Parallel(explodeTracks, suitTrack, toonTrack, soundTrack, soundTrack2, propTrack, explosionTrack, explosionTrack2)

def doExplodingBill(attack):
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
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0))
    propTrack.append(Wait(1.5))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 3.1, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, tnt, [hitPoint], [missPoint], .25, parent=battle))
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2), 2.5, ['slip-forward'])
    soundTrack = getSoundTrack('ENC_cogfall_apart.ogg', delay=2.25, node=suit)
    notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextCheat, - int(dmg / 2)), Func(toon.showHpString, "VULNERABLE!"))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Zap and Drop are now classified as defective.',
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    return Parallel(explodeTracks, suitTrack, toonTrack, soundTrack, propTrack, notifyTrack, explosionTrack)


def doSnowBalls(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='Snowballs')
    BattleParticles.setEffectTexture(particleEffect, 'snow-particle')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 1.2, [particleEffect, suit, 0])
    toonTrack = getToonTrack(attack, 1.2, ['cringe'], 0.2, splicedDodgeAnims=[['duck', 1e-05, 0.8]],
                             showMissedExtraTime=0.8)
    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()

    def changeColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 1, 1)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    soundTrack = getSoundTrack('SA_freeze.ogg', delay=0.4, node=suit)
    if dmg > 0:
        colorTrack = Sequence()
        colorTrack.append(Wait(1.6))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(Parallel(changeColor(headParts), changeColor(torsoParts), changeColor(legsParts)))
        colorTrack.append(Wait(2.9))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack, colorTrack)
    else:
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack)


def doFireBalls(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='Fire')
    BattleParticles.setEffectTexture(particleEffect, 'fire')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 1.2, [particleEffect, suit, 0])
    toonTrack = getToonTrack(attack, 1.2, ['cringe'], 0.2, splicedDodgeAnims=[['duck', 1e-05, 0.8]],
                             showMissedExtraTime=0.8)
    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()

    def changeColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setColorScale, Vec4(0, 0, 0, 0.95)))

        return track

    def resetColor(parts):
        track = Parallel()
        for partNum in xrange(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))

        return track

    soundTrack = getSoundTrack('SA_hot_air.ogg', delay=0.4, node=suit)
    if dmg > 0:
        colorTrack = Sequence()
        colorTrack.append(Wait(1.6))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(Parallel(changeColor(headParts), changeColor(torsoParts), changeColor(legsParts)))
        colorTrack.append(Wait(2.9))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack, colorTrack)
    else:
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack)

def doKamikaze(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = getSuitAnimTrack(attack)
        suitTrack.append(Wait(0.1))
        suitTrack.append(Func(suit.showHpTextCheat, - int(100 * len(battle.activeToons))))
        suitTrack.append(Func(suit.showHpString, "BOMBED!"))
        suitTrack.append(Func(suit.setHealthForMe, - (100 * len(battle.activeToons))))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Parallel(ActorInterval(suit, 'slip-backward'), Func(suit.setChatAbsolute, 'Ouch.', CFSpeech | CFTimeout)))
        suitTracks.append(suitTrack)
        revives = suit.getMaxSkeleRevives() + 1
        suitTrack.append(Func(suit.setNeutralAnimation))
        if suit.isVirtual and revives > 2:
            suitTrack.append(Func(suit.checkCogHPLaser, battle))
        elif suit.isSkeleton and revives > 2:
            suitTrack.append(Func(suit.checkCogHPLaserRevive, battle))
        elif not suit.isSkeleton and revives > 1:
            suitTrack.append(Func(suit.checkCogHPRevive, battle))
        elif suit.isVirtual:
            suitTrack.append(Func(suit.checkCogHPLaser, battle))
        elif not suit.isVirtual:
            suitTrack.append(Func(suit.checkCogHPBomb, battle))
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
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
        knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(0.7), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
        sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
        sparks = sparkEffect.getParticlesNamed('particles-1')
        sparks.setPoolSize(10)
        sparks.setLitterSize(10)
        sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
        sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
        if t['hp'] != 0:
            sparkTracks.append(Sequence(
                Wait(4.0),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))
    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('incoming_whistle.ogg', delay=2.0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=1.5, node=suit)
    soundTrack1 = getSoundTrack('ENC_cogfall_apart.ogg', delay=4.0, node=suit)
    return Parallel(suitTracks, knifeTracks, sparkTracks, toonTracks, soundTrack, soundTrack1, soundTrack2, explosionTrack, explosionTrack2)


def doFallingKnife(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    name = attack['id']
    suitTrack = getSuitTrack(attack)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Trap gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dsk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    for t in targets:
        knife = globalPropPool.getProp('dagger')
        knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
        knifeTracks.append(knifeTrack)
        sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
        sparks = sparkEffect.getParticlesNamed('particles-1')
        sparks.setPoolSize(10)
        sparks.setLitterSize(10)
        sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
        sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
        if dmg != 0:
            sparkTracks.append(Sequence(
                Wait(4.0),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))

    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTracks(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    return Parallel(suitTrack, knifeTracks, sparkTracks, toonTracks, soundTrack)

def doFallingKnifeHeadRoller(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('FallingKnife', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'falling-knife'), headsUp, Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    knife = globalPropPool.getProp('dagger')
    knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
    knifeTracks.append(knifeTrack)
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(10)
    sparks.setLitterSize(10)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    if dmg != 0:
            sparkTracks.append(Sequence(
                Wait(4.0),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))
    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTrack(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    if name == HEAD_ROLLER:
        suitTrack.append(Wait(2))
        suitTrack.append(doHeadRoller(attack, 2))
    return Parallel(suitTrack, knifeTracks, tauntInterval, sparkTracks, toonTracks, soundTrack)

def doFallingKnifeUnionBuster(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('FallingKnife', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'falling-knife'), suitReset, Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    knife = globalPropPool.getProp('dagger')
    knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
    knifeTracks.append(knifeTrack)
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(10)
    sparks.setLitterSize(10)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    if dmg != 0:
            sparkTracks.append(Sequence(
                Wait(4.0),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))
    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTrack(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    suitTrack.append(Wait(2))
    suitTrack.append(doStomper(attack))
    return Parallel(suitTrack, knifeTracks, tauntInterval, sparkTracks, toonTracks, soundTrack)

def doFallingKnifeUnionBust(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('FallingKnife', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'falling-knife'), suitReset, Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    knife = globalPropPool.getProp('dagger')
    knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
    knifeTracks.append(knifeTrack)
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(10)
    sparks.setLitterSize(10)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    if dmg != 0:
            sparkTracks.append(Sequence(
                Wait(4.0),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))
    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTrack(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    suitTrack.append(Wait(2))
    suitTrack.append(doUnionBust(attack, 3))
    return Parallel(suitTrack, knifeTracks, tauntInterval, sparkTracks, toonTracks, soundTrack)

def doFallingKnifePromotion(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    name = attack['id']
    dmg = target[0]['hp']
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('FallingKnife', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'falling-knife'), suitReset, Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.3, 0.4, 0.0), VBase3(0, 0, 90)]
    knifeTracks = Parallel()
    sparkTracks = Parallel()
    knife = globalPropPool.getProp('dagger')
    knifeTrack = Sequence(
            getPropAppearTrack(knife, suit.getRightHand(), posPoints, 0.25, scaleUpPoint=Point3(1.0), scaleUpTime=0.1),
            Wait(1.3),
            Parallel(
                getThrowTrack(knife, toon.getPos(battle), 2.35, battle, -64.288),
                LerpHprInterval(knife, 0.8, VBase3(720, 630, 720))
            ),
            Func(MovieUtil.removeProp, knife)
        )
    knifeTracks.append(knifeTrack)
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    sparks.setPoolSize(10)
    sparks.setLitterSize(10)
    sparks.renderer.setEdgeColor(Vec4(1.0, 1.0, 1.0, 1.0))
    sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    if dmg != 0:
            sparkTracks.append(Sequence(
                Wait(4.0),
                Parallel(
                    ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
                    autoFinish=1
                )
            ))
    damageAnims = [['slip-forward', 0.01, 0.4]]
    toonTracks = getToonTrack(attack, damageDelay=4.0, splicedDamageAnims=damageAnims, dodgeDelay=3.1, dodgeAnimNames=['sidestep'])
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    suitTrack.append(Wait(2))
    suitTrack.append(doCutTheSlackChairman(attack, 3))
    return Parallel(suitTrack, knifeTracks, tauntInterval, sparkTracks, toonTracks, soundTrack)

def doFallingKnifeOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 0.5
    propDelay = 0.6
    throwDuration = 1.5
    paper = globalPropPool.getProp('dagger')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(0.00, -1.00, -1.85), VBase3(270.00, 45.00, 45.00)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(1.25, 1.25, 1.25), scaleUpTime=0.1))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + .2)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ() + 1.1)
    movePoint = Point3(hitPoint.getX() + 10, hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, -90, -90)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(2, 2, 2)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    soundTrack = getSoundTrack('SA_falling_knife.ogg', node=suit)
    toonTrack = getToonTrack(attack, damageDelay=3.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doBlueChipOLD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 1.0
    propDelay = 0.6
    throwDuration = 1.5
    paper = loader.loadModel('phase_5/models/props/cc_m_prp_gen_chip_blue.bam')
    suitTrack = getSuitTrack(attack)
    posPoints = [Point3(-0.01, -0.05, 0.15), VBase3(270.00, 45.00, 45.00)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + 1.5)
    if dmg > 0:
        hitPoint.setZ(hitPoint.getZ() + 1.1)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 90, 90)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(8, 8, 8)), Wait(0.95), LerpScaleInterval(paper, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    soundTrack = getSoundTrack('SA_blue_chip.ogg', delay=1.1, node=suit)
    toonTrack = getToonTracks(attack, damageDelay=3.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doShortSqueeze(attack):
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.0
    suitTrack = getSuitTrack(attack)
    damageAnims = [['struggle', 0.01, 0.01, 1.0],
     ['slip-backward', 0.01, 0.01]]
    shakeTracks = Parallel()
    squeezeTracks = Parallel()
    coinTracks = Parallel()
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.5, dodgeAnimNames=['sidestep'], showDamageExtraTime=1.1)
    soundTracks = Parallel()
    for t in targets:
        dmg = t['hp']
        toon = t['toon']
        if dmg > 0:
            x = toon.getX(); y = toon.getY(); z = toon.getZ()
            groundPoint = Point3(x, y, z)
            moveTime = 0.15
            shakeTrack = Sequence(Wait(damageDelay))
            for i in xrange(0, 8):
                shakeTrack.append(LerpPosInterval(toon, moveTime, Point3(x, y, z + 3)))
                shakeTrack.append(LerpPosInterval(toon, moveTime, Point3(x, y, z + 1.5)))

            shakeTrack.append(LerpPosInterval(toon, 0.15, groundPoint))
            shakeTracks.append(shakeTrack)
            initialScale = toon.getScale()
            xScale, yScale, zScale = initialScale
            squeezeTrack = Sequence(
                Wait(damageDelay),
                Func(battle.movie.needRestoreToonScale),
                LerpScaleInterval(toon, 0.1, Vec3(xScale * 0.6, yScale * 0.46, zScale * 1.2)),
                Wait(1.1),
                LerpScaleInterval(toon, 0.2, Vec3(xScale * 1.2, yScale * 1.2, zScale * 0.8)),
                LerpScaleInterval(toon, 0.2, initialScale),
                Func(battle.movie.clearRestoreToonScale)
            )
            squeezeTracks.append(squeezeTrack)
            coinTrack = Parallel()
            coinTypes = ['bronze', 'silver', 'gold']
            for i in xrange(0, 20):
                coin = loader.loadModel('phase_3.5/models/props/cc_m_prp_gen_coin_' + random.choice(coinTypes) + '.bam')
                pnt = toon.getPos(toon); pnt.setZ(pnt[2] + toon.shoulderHeight - 0.2); startPos = Point3(pnt)
                xOffset = random.random() * 5
                if random.choice([False, True]):
                    xOffset *= -1
                yOffset = random.random() * 5
                if random.choice([False, True]):
                    yOffset *= -1
                landPos = toon.getPos(battle)
                landPos.setX(landPos.getX() + xOffset); landPos.setY(landPos.getY() + yOffset)
                coinTrack.append(Sequence(
                    Wait(damageDelay + 0.1 * i),
                    Func(__showProp, coin, toon, startPos, VBase3(random.randint(0, 359), random.randint(0, 359), random.randint(0, 359)), Point3(1.0)),
                    getThrowTrack(coin, landPos, 1.0, battle),
                    Func(MovieUtil.removeProp, coin)
                ))

            coinTracks.append(coinTrack)
            soundTracks.append(Track(
                (1.0, SoundInterval(globalBattleSoundCache.getSound('SA_short_squeeze.ogg'), node=toon)),
                (2.4, SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=toon))
            ))

    return Parallel(suitTrack, shakeTracks, squeezeTracks, coinTracks, toonTracks, soundTracks)

def doShortSqueezeWritingDesk(attack):
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    damageDelay = 1.0
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)


    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)

    taunt = getAttackTaunt('ShortSqueeze', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'short-squeeze'), suitReset,
                     Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(1.0))
    suitTrack.append(doWritingDesk(attack))
    damageAnims = [['struggle', 0.01, 0.01, 1.0],
     ['slip-backward', 0.01, 0.01]]
    shakeTracks = Parallel()
    squeezeTracks = Parallel()
    coinTracks = Parallel()
    toonTracks = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.5, dodgeAnimNames=['sidestep'], showDamageExtraTime=1.1)
    soundTracks = Parallel()
    if dmg != 0:
            x = toon.getX(); y = toon.getY(); z = toon.getZ()
            groundPoint = Point3(x, y, z)
            moveTime = 0.15
            shakeTrack = Sequence(Wait(damageDelay))
            for i in xrange(0, 8):
                shakeTrack.append(LerpPosInterval(toon, moveTime, Point3(x, y, z + 3)))
                shakeTrack.append(LerpPosInterval(toon, moveTime, Point3(x, y, z + 1.5)))
            shakeTrack.append(LerpPosInterval(toon, 0.15, groundPoint))
            shakeTracks.append(shakeTrack)
            initialScale = toon.getScale()
            xScale, yScale, zScale = initialScale
            squeezeTrack = Sequence(
                Wait(damageDelay),
                Func(battle.movie.needRestoreToonScale),
                LerpScaleInterval(toon, 0.1, Vec3(xScale * 0.6, yScale * 0.46, zScale * 1.2)),
                Wait(1.1),
                LerpScaleInterval(toon, 0.2, Vec3(xScale * 1.2, yScale * 1.2, zScale * 0.8)),
                LerpScaleInterval(toon, 0.2, initialScale),
                Func(battle.movie.clearRestoreToonScale)
            )
            squeezeTracks.append(squeezeTrack)
            coinTrack = Parallel()
            coinTypes = ['bronze', 'silver', 'gold']
            for i in xrange(0, 20):
                coin = loader.loadModel('phase_3.5/models/props/cc_m_prp_gen_coin_' + random.choice(coinTypes) + '.bam')
                pnt = toon.getPos(toon); pnt.setZ(pnt[2] + toon.shoulderHeight - 0.2); startPos = Point3(pnt)
                xOffset = random.random() * 5
                if random.choice([False, True]):
                    xOffset *= -1
                yOffset = random.random() * 5
                if random.choice([False, True]):
                    yOffset *= -1
                landPos = toon.getPos(battle)
                landPos.setX(landPos.getX() + xOffset); landPos.setY(landPos.getY() + yOffset)
                coinTrack.append(Sequence(
                    Wait(damageDelay + 0.1 * i),
                    Func(__showProp, coin, toon, startPos, VBase3(random.randint(0, 359), random.randint(0, 359), random.randint(0, 359)), Point3(1.0)),
                    getThrowTrack(coin, landPos, 1.0, battle),
                    Func(MovieUtil.removeProp, coin)
                ))

            coinTracks.append(coinTrack)
            soundTracks.append(Track(
                (1.0, SoundInterval(globalBattleSoundCache.getSound('SA_short_squeeze.ogg'), node=toon)),
                (2.4, SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=toon))
            ))
    return Parallel(suitTrack, shakeTracks, squeezeTracks, coinTracks, toonTracks, soundTracks)


def doBlueChipSyphon(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    suitDelay = 1.07
    propDelay = 0.6
    throwDuration = 1.0
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    tauntIndex = attack['taunt']
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = getAttackTaunt('BlueChip', attack['suitName'])
    tauntInterval = Sequence(headsUp, Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'blue-chip'), suitReset, Func(suit.setNeutralAnimation))
    if getSuitBodyType(attack['suitName']) == 'a':
        posPoints = [Point3(0.05, 0.5, -0.15), VBase3(70, 0, 0)]
    else:
        posPoints = [Point3(0.0, 0.4, -0.05), VBase3(90, 0, 0)]
    suit.pose('blue-chip', (1.5) * suit.getAnimControls('blue-chip', None, None)[0].getFrameRate() * 1) # The posing thing should be handled in a way similar to the way the defeat animation is handled where the time is gotten from an equation using a frame
    suit.update(0)
    chipFlipLandPos = suit.getRightHand().getPos(battle)
    if getSuitBodyType(attack['suitName']) == 'a':
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.35); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.15)
    else:
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.2); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.05)
    suit.loop('neutral')
    propTracks = Parallel()
    chip = loader.loadModel('phase_5/models/props/cc_m_prp_gen_chip_blue.bam')
    endingPos = chip.getPos()
    chipTrack = Sequence(
            getPropAppearTrack(chip, suit.getRightHand(), posPoints, propDelay - propDelay, Point3(1.0) if getSuitBodyType(attack['suitName']) == 'a' else Point3(0.75), scaleUpTime=0.5),
            Wait(0.5),
            Parallel(
                getThrowTrack(chip, chipFlipLandPos, 0.5, battle, -160.72),
                LerpHprInterval(chip, 0.5, VBase3(90, 450, 90))
            ),
            Func(chip.reparentTo, suit.getRightHand()),
            Func(chip.setPos, Point3(-0.35, 0.0, -0.15) if getSuitBodyType(attack['suitName']) == 'a' else Point3(-0.2, 0.0, -0.05)),
            Wait(suitDelay + propDelay - 1.0)
        )
    hitPoint = toon.getPos(battle)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ())
    chipTrack.append(Func(battle.movie.needRestoreRenderProp, chip))
    chipTrack.append(Func(chip.wrtReparentTo, battle))
    chipTrack.append(getThrowTrack(chip, hitPoint, duration=throwDuration, parent=battle, gravity=-64.288))
    chipTrack.append(Wait(0.6))
    chipTrack.append(LerpPosInterval(chip, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(chip, throwDuration, Point3(0, 810, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(chip, throwDuration, Point3(6)), Wait(0.95), LerpScaleInterval(chip, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(chipTrack, spinTrack, sizeTrack), Effects.createZBounce(chip, 2, endingPos, 0.5, 1.5), Func(MovieUtil.removeProp, chip), Func(battle.movie.clearRenderProp, chip))
    propTracks.append(propTrack)
    toonTracks = getToonTrack(attack, 3.3, ['squish'], 2.0, ['sidestep'])
    squishTrack = Sequence(Wait(3.05), Func(toon.enterFlattened), Wait(2.0), Func(toon.exitFlattened))
    soundTrack = getSoundTrack('SA_blue_chip.ogg', node=suit)
    suitTrack.append(Wait(2))
    suitTrack.append(doSyphon(attack))
    if dmg > 0:
        return Parallel(suitTrack, toonTracks, propTracks, tauntInterval, soundTrack, squishTrack)
    else:
        return Parallel(suitTrack, toonTracks, propTracks, tauntInterval, soundTrack)

def doBlueChipHeadRoller(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    suitDelay = 1.07
    propDelay = 0.6
    throwDuration = 1.0
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('BlueChip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'blue-chip'), suitReset, Func(suit.setNeutralAnimation))
    if getSuitBodyType(attack['suitName']) == 'a':
        posPoints = [Point3(0.05, 0.5, -0.15), VBase3(70, 0, 0)]
    else:
        posPoints = [Point3(0.0, 0.4, -0.05), VBase3(90, 0, 0)]
    suit.pose('blue-chip', (1.5) * suit.getAnimControls('blue-chip', None, None)[0].getFrameRate() * 1) # The posing thing should be handled in a way similar to the way the defeat animation is handled where the time is gotten from an equation using a frame
    suit.update(0)
    chipFlipLandPos = suit.getRightHand().getPos(battle)
    if getSuitBodyType(attack['suitName']) == 'a':
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.35); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.15)
    else:
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.2); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.05)
    suit.loop('neutral')
    propTracks = Parallel()
    chip = loader.loadModel('phase_5/models/props/cc_m_prp_gen_chip_blue.bam')
    endingPos = chip.getPos()
    chipTrack = Sequence(
            getPropAppearTrack(chip, suit.getRightHand(), posPoints, propDelay - propDelay, Point3(1.0) if getSuitBodyType(attack['suitName']) == 'a' else Point3(0.75), scaleUpTime=0.5),
            Wait(0.5),
            Parallel(
                getThrowTrack(chip, chipFlipLandPos, 0.5, battle, -160.72),
                LerpHprInterval(chip, 0.5, VBase3(90, 450, 90))
            ),
            Func(chip.reparentTo, suit.getRightHand()),
            Func(chip.setPos, Point3(-0.35, 0.0, -0.15) if getSuitBodyType(attack['suitName']) == 'a' else Point3(-0.2, 0.0, -0.05)),
            Wait(suitDelay + propDelay - 1.0)
        )
    hitPoint = toon.getPos(battle)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ())
    chipTrack.append(Func(battle.movie.needRestoreRenderProp, chip))
    chipTrack.append(Func(chip.wrtReparentTo, battle))
    chipTrack.append(getThrowTrack(chip, hitPoint, duration=throwDuration, parent=battle, gravity=-64.288))
    chipTrack.append(Wait(0.6))
    chipTrack.append(LerpPosInterval(chip, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(chip, throwDuration, Point3(0, 810, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(chip, throwDuration, Point3(6)), Wait(0.95), LerpScaleInterval(chip, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(chipTrack, spinTrack, sizeTrack), Effects.createZBounce(chip, 2, endingPos, 0.5, 1.5), Func(MovieUtil.removeProp, chip), Func(battle.movie.clearRenderProp, chip))
    propTracks.append(propTrack)
    toonTracks = getToonTrack(attack, 3.3, ['squish'], 2.0, ['sidestep'])
    squishTrack = Sequence(Wait(3.05), Func(toon.enterFlattened), Wait(2.0), Func(toon.exitFlattened))
    soundTrack = getSoundTrack('SA_blue_chip.ogg', node=suit)
    suitTrack.append(Wait(2))
    suitTrack.append(doHeadRollerGroup(attack, 1, 2, 3, 4, 5))
    if dmg > 0:
        return Parallel(suitTrack, toonTracks, propTracks, tauntInterval, soundTrack, squishTrack)
    else:
        return Parallel(suitTrack, toonTracks, propTracks, tauntInterval, soundTrack)

def doBlueChipSnipe(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    suitDelay = 1.07
    propDelay = 0.6
    throwDuration = 1.0
    tauntIndex = attack['taunt']
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = getAttackTaunt('BlueChip', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'blue-chip'), suitReset, Func(suit.setNeutralAnimation))
    if getSuitBodyType(attack['suitName']) == 'a':
        posPoints = [Point3(0.05, 0.5, -0.15), VBase3(70, 0, 0)]
    else:
        posPoints = [Point3(0.0, 0.4, -0.05), VBase3(90, 0, 0)]
    suit.pose('blue-chip', (1.5) * suit.getAnimControls('blue-chip', None, None)[0].getFrameRate() * 1) # The posing thing should be handled in a way similar to the way the defeat animation is handled where the time is gotten from an equation using a frame
    suit.update(0)
    chipFlipLandPos = suit.getRightHand().getPos(battle)
    if getSuitBodyType(attack['suitName']) == 'a':
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.35); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.15)
    else:
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.2); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.05)
    suit.loop('neutral')
    propTracks = Parallel()
    chip = loader.loadModel('phase_5/models/props/cc_m_prp_gen_chip_blue.bam')
    endingPos = chip.getPos()
    chipTrack = Sequence(
            getPropAppearTrack(chip, suit.getRightHand(), posPoints, propDelay - propDelay, Point3(1.0) if getSuitBodyType(attack['suitName']) == 'a' else Point3(0.75), scaleUpTime=0.5),
            Wait(0.5),
            Parallel(
                getThrowTrack(chip, chipFlipLandPos, 0.5, battle, -160.72),
                LerpHprInterval(chip, 0.5, VBase3(90, 450, 90))
            ),
            Func(chip.reparentTo, suit.getRightHand()),
            Func(chip.setPos, Point3(-0.35, 0.0, -0.15) if getSuitBodyType(attack['suitName']) == 'a' else Point3(-0.2, 0.0, -0.05)),
            Wait(suitDelay + propDelay - 1.0)
        )
    hitPoint = toon.getPos(battle)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ())
    chipTrack.append(Func(battle.movie.needRestoreRenderProp, chip))
    chipTrack.append(Func(chip.wrtReparentTo, battle))
    chipTrack.append(getThrowTrack(chip, hitPoint, duration=throwDuration, parent=battle, gravity=-64.288))
    chipTrack.append(Wait(0.6))
    chipTrack.append(LerpPosInterval(chip, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(chip, throwDuration, Point3(0, 810, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(chip, throwDuration, Point3(6)), Wait(0.95), LerpScaleInterval(chip, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(chipTrack, spinTrack, sizeTrack), Effects.createZBounce(chip, 2, endingPos, 0.5, 1.5), Func(MovieUtil.removeProp, chip), Func(battle.movie.clearRenderProp, chip))
    propTracks.append(propTrack)
    toonTracks = getToonTrack(attack, 3.3, ['squish'], 2.0, ['sidestep'])
    squishTrack = Sequence(Wait(3.05), Func(toon.enterFlattened), Wait(2.0), Func(toon.exitFlattened))
    soundTrack = getSoundTrack('SA_blue_chip.ogg', node=suit)
    suitTrack.append(Wait(2))
    suitTrack.append(doSnipeChairman(attack))
    if dmg > 0:
        return Parallel(suitTrack, toonTracks, propTracks, tauntInterval, soundTrack, squishTrack)
    else:
        return Parallel(suitTrack, toonTracks, propTracks, tauntInterval, soundTrack)

def doBlueChip(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    suitDelay = 1.07
    propDelay = 0.6
    throwDuration = 1.0
    suitTrack = getSuitTrack(attack)
    if getSuitBodyType(attack['suitName']) == 'a':
        posPoints = [Point3(0.05, 0.5, -0.15), VBase3(70, 0, 0)]
    else:
        posPoints = [Point3(0.0, 0.4, -0.05), VBase3(90, 0, 0)]
    suit.pose('blue-chip', (1.5) * suit.getAnimControls('blue-chip', None, None)[0].getFrameRate() * 1) # The posing thing should be handled in a way similar to the way the defeat animation is handled where the time is gotten from an equation using a frame
    suit.update(0)
    chipFlipLandPos = suit.getRightHand().getPos(battle)
    if getSuitBodyType(attack['suitName']) == 'a':
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.35); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.15)
    else:
        chipFlipLandPos.setX(chipFlipLandPos.getX() - 0.2); chipFlipLandPos.setY(chipFlipLandPos.getY() + 0.0); chipFlipLandPos.setZ(chipFlipLandPos.getZ() - 0.05)
    suit.loop('neutral')
    propTracks = Parallel()
    chip = loader.loadModel('phase_5/models/props/cc_m_prp_gen_chip_blue.bam')
    endingPos = chip.getPos()
    chipTrack = Sequence(
            getPropAppearTrack(chip, suit.getRightHand(), posPoints, propDelay - propDelay, Point3(1.0) if getSuitBodyType(attack['suitName']) == 'a' else Point3(0.75), scaleUpTime=0.5),
            Wait(0.5),
            Parallel(
                getThrowTrack(chip, chipFlipLandPos, 0.5, battle, -160.72),
                LerpHprInterval(chip, 0.5, VBase3(90, 450, 90))
            ),
            Func(chip.reparentTo, suit.getRightHand()),
            Func(chip.setPos, Point3(-0.35, 0.0, -0.15) if getSuitBodyType(attack['suitName']) == 'a' else Point3(-0.2, 0.0, -0.05)),
            Wait(suitDelay + propDelay - 1.0)
        )
    hitPoint = toon.getPos(battle)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ())
    chipTrack.append(Func(battle.movie.needRestoreRenderProp, chip))
    chipTrack.append(Func(chip.wrtReparentTo, battle))
    chipTrack.append(getThrowTrack(chip, hitPoint, duration=throwDuration, parent=battle, gravity=-64.288))
    chipTrack.append(Wait(0.6))
    chipTrack.append(LerpPosInterval(chip, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(chip, throwDuration, Point3(0, 810, 0)))
    #spinTrack2 = Sequence(Wait(propDelay + suitDelay + 1.45), LerpHprInterval(chip, throwDuration, Point3(0, 0, 90)))
    #bounceTrack2 = Sequence(Wait(propDelay + suitDelay + 1.45), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5), Effects.createZBounce(chip, .25, hitPoint, 0.5, 1.5))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(chip, throwDuration, Point3(6)), Wait(0.95), LerpScaleInterval(chip, 0.4, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(chipTrack, sizeTrack, spinTrack), Effects.createZBounce(chip, 2, endingPos, 0.5, 1.5), Func(MovieUtil.removeProp, chip), Func(battle.movie.clearRenderProp, chip))
    propTracks.append(propTrack)
    toonTracks = getToonTrack(attack, 3.3, ['squish'], 2.0, ['sidestep'])
    squishTrack = Sequence(Wait(3.05), Func(toon.enterFlattened), Wait(2.0), Func(toon.exitFlattened))
    soundTrack = getSoundTrack('SA_blue_chip.ogg', node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTracks, propTracks, soundTrack, squishTrack)
    else:
        return Parallel(suitTrack, toonTracks, propTracks, soundTrack)

	
def doThrowBook(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 1.5
    propDelay = 0.1
    throwDuration = 1.0
    paper = globalPropPool.getProp('lawbook')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.5, 0, 0), VBase3(0, 0, 180)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + 1.5)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 360, 360)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)), Wait(0.95), LerpScaleInterval(paper, 0.75, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Squirt Gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'fbd':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    toonTrack = getToonTrack(attack, damageDelay=3.15, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack)

def doThrowBookSnap(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 1.5
    propDelay = 0.1
    throwDuration = 1.0
    paper = globalPropPool.getProp('lawbook')
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = getAttackTaunt('ThrowBook', attack['suitName'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doSnap(attack))
    posPoints = [Point3(-0.5, 0, 0), VBase3(0, 0, 180)]
    paperTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + 1.5)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2),
                         LerpHprInterval(paper, throwDuration, Point3(-360, 360, 360)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)),
                         Wait(0.95), LerpScaleInterval(paper, 0.75, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper),
                         Func(battle.movie.clearRenderProp, paper))
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
    toonTrack = getToonTrack(attack, damageDelay=3.15, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, tauntInterval, soundTrack)

def doThrowBookPaperCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 1.5
    propDelay = 0.1
    throwDuration = 1.0
    paper = globalPropPool.getProp('lawbook')
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = random.choice(
            ["Hmph...", "Hrnhmpf...",
             "Hrm...",
             "Hm, hm..."])
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doPaperCut(attack))
    posPoints = [Point3(-0.5, 0, 0), VBase3(0, 0, 180)]
    paperTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + 1.5)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2),
                         LerpHprInterval(paper, throwDuration, Point3(-360, 360, 360)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)),
                         Wait(0.95), LerpScaleInterval(paper, 0.75, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper),
                         Func(battle.movie.clearRenderProp, paper))
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
    toonTrack = getToonTrack(attack, damageDelay=3.15, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, tauntInterval, soundTrack)

def doThrowBookWireCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 1.5
    propDelay = 0.1
    throwDuration = 1.0
    paper = globalPropPool.getProp('lawbook')
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    taunt = random.choice(
            ["Hmph...", "Hrnhmpf...",
             "Hrm...",
             "Hm, hm..."])
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, ActorInterval(suit, 'throw-object', playRate=1.5), suitReset, Func(suit.setNeutralAnimation))
    suitTrack.append(Wait(2.0))
    suitTrack.append(doPaperCut2(attack))
    posPoints = [Point3(-0.5, 0, 0), VBase3(0, 0, 180)]
    paperTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(2.25, 2.25, 2.25), scaleUpTime=0.5))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    hitPoint.setX(hitPoint.getX() + 0)
    hitPoint.setY(hitPoint.getY() + 1.5)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY() - 1.8, hitPoint.getZ() + 0.2)
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2),
                         LerpHprInterval(paper, throwDuration, Point3(-360, 360, 360)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpScaleInterval(paper, throwDuration, Point3(6, 6, 6)),
                         Wait(0.95), LerpScaleInterval(paper, 0.75, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(MovieUtil.removeProp, paper),
                         Func(battle.movie.clearRenderProp, paper))
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
    toonTrack = getToonTrack(attack, damageDelay=3.15, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTrack, propTrack, tauntInterval, soundTrack)

def doCloudStorage(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    suitDelay = 0
    propDelay = 2.5
    throwDuration = 1.5
    paper = globalPropPool.getProp('stormcloud')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0, 0, 0), VBase3(0, 0, 0)]
    paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(3.5, 3.5, 3.5), scaleUpTime=0.1))
    paperTrack.append(Wait(suitDelay))
    hitPoint = toon.getPos(battle)
    movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ())
    paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
    paperTrack.append(Func(paper.wrtReparentTo, battle))
    paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle))
    paperTrack.append(Wait(0.6))
    paperTrack.append(LerpPosInterval(paper, 0.1, movePoint))
    spinTrack = Sequence(Wait(propDelay + suitDelay + 0.2), LerpHprInterval(paper, throwDuration, Point3(-360, 0, 0)))
    sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.2), Parallel(LerpScaleInterval(paper, throwDuration, Point3(8, 8, 8)), Func(paper.loop, 'stormcloud')), LerpScaleInterval(paper, 1, MovieUtil.PNT3_NEARZERO))
    propTrack = Sequence(Parallel(paperTrack, sizeTrack), Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper))
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
    shrinkTrack = Sequence(Wait(4.25), LerpScaleInterval(toon, 1, MovieUtil.PNT3_NEARZERO), Wait(2.0), LerpScaleInterval(toon, 0.5, Point3(1, 1, 1)))
    toonTrack = getToonTrack(attack, damageDelay=5.35, splicedDamageAnims=damageAnims, dodgeDelay=2.4, dodgeAnimNames=['sidestep'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack, shrinkTrack)
    else:
        return Parallel(suitTrack, toonTrack, propTrack)


def doWithdrawal(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('Withdrawal')
    BattleParticles.setEffectTexture(particleEffect, 'snow-particle')
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 1.2, [particleEffect, suit, 0])
    toonTrack = getToonTrack(attack, 1.2, ['cringe'], 0.2, splicedDodgeAnims=[['duck', 1e-05, 0.8]], showMissedExtraTime=0.8)
    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()

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

    soundTrack = getSoundTrack('SA_withdrawl.ogg', delay=1.4, node=suit)
    if dmg > 0:
        colorTrack = Sequence()
        colorTrack.append(Wait(1.6))
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(Parallel(changeColor(headParts), changeColor(torsoParts), changeColor(legsParts)))
        colorTrack.append(Wait(2.9))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack, colorTrack)
    else:
        return Parallel(suitTrack, partTrack, toonTrack, soundTrack)


def doJargon(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect2 = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect3 = BattleParticles.createParticleEffect(file='jargonSpray')
    particleEffect4 = BattleParticles.createParticleEffect(file='jargonSpray')
    BattleParticles.setEffectTexture(particleEffect, 'jargon-brow', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'jargon-deep', color=Vec4(0, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect3, 'jargon-hoop', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect4, 'jargon-ipo', color=Vec4(0, 0, 0, 1))
    damageDelay = 1
    dodgeDelay = 0.9
    partDelay = 0.25
    partInterval = 1
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, partDelay + partInterval * 0, 2, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay + partInterval * 1, 2, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, partDelay + partInterval * 2, 2, [particleEffect3, suit, 0])
    partTrack4 = getPartTrack(particleEffect4, partDelay + partInterval * 3, 1.0, [particleEffect4, suit, 0])
    damageAnims = []
    damageAnims.append(['conked',
     0.0001,
     0,
     0.4])
    damageAnims.append(['conked',
     0.0001,
     0.7,
     0.85])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.66])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.09])
    damageAnims.append(['conked',
     0.0001,
     0.4,
     0.86])
    damageAnims.append(['conked', 0.0001, 0.4])
    dodgeAnims = [['duck', 0.0001, 1.2], ['duck', 0.0001, 1.3]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.6, showDamageExtraTime=0.7)
    soundTrack = getSoundTrack('SA_jargon.ogg', delay=1.5, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Level 8 Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'ste':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4)

def doOverload(attack):
    suit = attack['suit']
    battle = attack['battle']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('DoubleTalkLeft')
    particleEffect2 = BattleParticles.createParticleEffect('DoubleTalkRight')
    BattleParticles.setEffectTexture(particleEffect, 'doubletalk-double', color=Vec4(0, 1.0, 0.0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'doubletalk-good', color=Vec4(0, 1.0, 0.0, 1))
    suitType = getSuitBodyType(attack['suitName'])
    partDelay = 2.25
    damageDelay = 2.5
    dodgeDelay = 2.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, partDelay, 1.8, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, partDelay, 1.8, [particleEffect2, suit, 0])
    damageAnims = [['duck',
                    0.01,
                    0.4,
                    1.05], ['cringe', 1e-06, 0.8]]
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay,
                             splicedDodgeAnims=[['duck', 0.01, 1.4]], showMissedExtraTime=0.9, showDamageExtraTime=0.8)
    soundTrack = getSoundTrack('SA_doubletalk.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, partTrack, partTrack2, soundTrack)


def doMumboJumbo(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect(file='mumboJumboSpray')
    particleEffect2 = BattleParticles.createParticleEffect(file='mumboJumboSpray')
    particleEffect3 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    particleEffect4 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    particleEffect5 = BattleParticles.createParticleEffect(file='mumboJumboSmother')
    BattleParticles.setEffectTexture(particleEffect, 'mumbojumbo-boiler', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect2, 'mumbojumbo-creative', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect3, 'mumbojumbo-deben', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect4, 'mumbojumbo-high', color=Vec4(1, 0, 0, 1))
    BattleParticles.setEffectTexture(particleEffect5, 'mumbojumbo-iron', color=Vec4(1, 0, 0, 1))
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    partTrack = getPartTrack(particleEffect, 1.5, 2, [particleEffect, suit, 0])
    partTrack2 = getPartTrack(particleEffect2, 1.5, 2, [particleEffect2, suit, 0])
    partTrack3 = getPartTrack(particleEffect3, 2.25, 1.7, [particleEffect3, toon, 0])
    partTrack4 = getPartTrack(particleEffect4, 2.25, 1.7, [particleEffect4, toon, 0])
    partTrack5 = getPartTrack(particleEffect5, 2.25, 1.7, [particleEffect5, toon, 0])
    toonTrack = getToonTrack(attack, 1.5, ['cringe'], 1.6, ['sidestep'])
    soundTrack = getSoundTrack('SA_mumbo_jumbo.ogg', delay=1.5, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Level 7 Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'ste':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2, partTrack3, partTrack4, partTrack5)
    else:
        return Parallel(suitTrack, toonTrack, soundTrack, partTrack, partTrack2)


def doGuiltTrip(attack):
    suit = attack['suit']
    battle = attack['battle']
    centerColor = Vec4(1.0, 0.2, 0.2, 0.9)
    edgeColor = Vec4(0.9, 0.9, 0.9, 0.4)
    powerBar1 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar2 = BattleParticles.createParticleEffect(file='guiltTrip')
    powerBar1.setPos(0, 6.1, 0.4)
    powerBar1.setHpr(-90, 0, 0)
    powerBar2.setPos(0, 6.1, 0.4)
    powerBar2.setHpr(90, 0, 0)
    powerBar1.setScale(5)
    powerBar2.setScale(5)
    powerBar1Particles = powerBar1.getParticlesNamed('particles-1')
    powerBar2Particles = powerBar2.getParticlesNamed('particles-1')
    powerBar1Particles.renderer.setCenterColor(centerColor)
    powerBar1Particles.renderer.setEdgeColor(edgeColor)
    powerBar2Particles.renderer.setCenterColor(centerColor)
    powerBar2Particles.renderer.setEdgeColor(edgeColor)
    waterfallEffect = BattleParticles.createParticleEffect('Waterfall')
    waterfallEffect.setScale(11)
    waterfallParticles = waterfallEffect.getParticlesNamed('particles-1')
    waterfallParticles.renderer.setCenterColor(centerColor)
    waterfallParticles.renderer.setEdgeColor(edgeColor)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.25))

    def getPowerTrack(effect, suit = suit, battle = battle):
        partTrack = Sequence(Wait(0.7), Func(battle.movie.needRestoreParticleEffect, effect), Func(effect.start, suit), Wait(0.4), LerpPosInterval(effect, 1.0, Point3(0, 15, 0.4)), LerpFunctionInterval(effect.setAlphaScale, fromData=1, toData=0, duration=0.4), Func(effect.cleanup), Func(battle.movie.clearRestoreParticleEffect, effect))
        return partTrack

    partTrack1 = getPowerTrack(powerBar1)
    partTrack2 = getPowerTrack(powerBar2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.6, 0.6, [waterfallEffect, suit, 0])
    toonTracks = getToonTracks(attack, 1.5, ['slip-forward'], 0.86, ['jump'])
    soundTrack = getSoundTrack('SA_guilt_trip.ogg', delay=1.1, node=suit)
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Trap Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'csm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    return Parallel(suitTrack, partTrack1, partTrack2, soundTrack, waterfallTrack, toonTracks)


def doRestrainingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0.375, -1.5, .85), VBase3(0, 220, -10)]
    propTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0))
    propTrack.append(Wait(1.55))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle))
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
    damageAnims = [['conked',
      0.01,
      0.3,
      0.2], ['struggle', 0.01, 0.2]]
    toonTrack = getToonTrack(attack, damageDelay=2.3, splicedDamageAnims=damageAnims, dodgeDelay=1.7, dodgeAnimNames=['sidestep'])
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Any Squirt Gags Toons use can and will be held against them in a court of law.',
                                     CFSpeech | CFTimeout))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                      "Quality Control has classified that all Zap are now classified as defective.",
                                      CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'csm':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    elif attack['suit'].dna.name == 'fbd':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack2))
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack)
    else:
        return Parallel(suitTrack, toonTrack, propTrack)

def doBreakthrough(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = loader.loadModel('phase_5/models/props/lightbulb')
    paper.find('**/Bulb_Coil').hide()
    suitTrack = Sequence(ActorInterval(suit, 'finger-wag', endTime=1), Wait(1.0), getSuitTrack(attack, playRate=1.5))
    cagePosition = Parallel(LerpPosInterval(paper, 0.25, Point3(-0.25, 0, -1.5)))
    posPoints = [Point3(0, 0, suit.height + 2), VBase3(0, 0, 0)]
    propTrack = Sequence(
        getPropAppearTrack(paper, suit, posPoints, 0.25, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25))
    propTrack.append(Wait(1))
    propTrack.append(Func(paper.find('**/Bulb_Coil').show))
    propTrack.append(Wait(1))
    propTrack.append(Parallel(Func(paper.reparentTo, suit.getRightHand()), cagePosition))
    propTrack.append(Wait(1.25))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle))
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
    damageAnims = [['conked',
      0.01,
      0.3,
      0.2], ['struggle', 0.01, 0.2]]
    toonTrack = getToonTrack(attack, damageDelay=4.25, splicedDamageAnims=damageAnims, dodgeDelay=3.5, dodgeAnimNames=['sidestep'])
    soundTrack2 = getSoundTrack('SA_breakthrough.ogg', delay=1.25, node=suit)
    if dmg > 0:
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack2)
    else:
        return Parallel(suitTrack, toonTrack, propTrack, soundTrack2)

def doEncrypt(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('ttht_m_ene_fileFolder')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(0, 0, 0), VBase3(-90, 270, 90)]
    x = toon.getX(battle)
    y = toon.getY(battle)
    z = toon.getZ(battle)
    cagePosition = Parallel(LerpHprInterval(paper, 0.25, Point3(-90, 0, 0)), LerpScaleInterval(paper, 0.25, Point3(2, 2, 2)), LerpPosInterval(paper, 0.25, Point3(x, y + 15, z + 2)))
    cagePosition2 = Parallel(LerpPosInterval(paper, 0.25, Point3(x, y + 10, z + 2)))
    propTrack = Sequence(
        Parallel(Func(paper.play, 'ttht_m_ene_fileFolder'), getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25)),
                 Wait(1.25), Func(paper.reparentTo, toon), cagePosition, Wait(1), cagePosition2)
    propTrack.append(Wait(0.25))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    #propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .5, parent=battle, lookAt=toon))
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
    propTrack.append(Parallel(explodeTrack, soundTrack, Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper)))
    damageAnims = [['struggle', 0.01, 0.2]]
    toonTrack = getToonTrack(attack, damageDelay=3.85, splicedDamageAnims=damageAnims, dodgeDelay=3, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTrack, propTrack)

def doCaseFiles(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    paper = globalPropPool.getProp('ttht_m_ene_fileFolder')
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    taunt = random.choice(
        ["Hmph...", "Hrnhmpf...",
         "Hrm...",
         "Hm, hm..."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    suitTrack = Sequence(headsUp, tauntInterval
    , ActorInterval(suit, 'throw-object', playRate=1.5), suitReset,
                         Func(suit.setNeutralAnimation))
    posPoints = [Point3(0, 0, 0), VBase3(-90, 270, 90)]
    x = toon.getX(battle)
    y = toon.getY(battle)
    z = toon.getZ(battle)
    cagePosition = Parallel(LerpHprInterval(paper, 0.25, Point3(-90, 0, 0)), LerpScaleInterval(paper, 0.25, Point3(2, 2, 2)), LerpPosInterval(paper, 0.25, Point3(x, y + 15, z + 2)))
    cagePosition2 = Parallel(LerpPosInterval(paper, 0.25, Point3(x, y + 10, z + 2)))
    propTrack = Sequence(
        Parallel(Func(paper.play, 'ttht_m_ene_fileFolder'), getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, Point3(1.5, 1.5, 1.5), scaleUpTime=0.25)),
                 Wait(1.25), Func(paper.reparentTo, toon), cagePosition, Wait(1), cagePosition2)
    propTrack.append(Wait(0.25))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    #propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .5, parent=battle, lookAt=toon))
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
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     "Any Sound and Zap Gags Toons use can and will be held against them in a court of law.",
                                     CFSpeech | CFTimeout))
    suitTrack.append(Wait(1.0))
    suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    propTrack.append(Parallel(explodeTrack, soundTrack, Func(MovieUtil.removeProp, paper), Func(battle.movie.clearRenderProp, paper)))
    damageAnims = [['struggle', 0.01, 0.2]]
    toonTrack = getToonTrack(attack, damageDelay=3.85, splicedDamageAnims=damageAnims, dodgeDelay=3, dodgeAnimNames=['sidestep'])
    return Parallel(suitTrack, toonTrack, propTrack)

def doSwirlBath(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.7
    sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
    spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
    spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
    spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
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
    suitTrack = getSuitTrack(attack)
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    spinTrack1 = getPartTrack(spinEffect1, 2.1, 3.9, [spinEffect1, battle, 0])
    spinTrack2 = getPartTrack(spinEffect2, 2.1, 3.9, [spinEffect2, battle, 0])
    spinTrack3 = getPartTrack(spinEffect3, 2.1, 3.9, [spinEffect3, battle, 0])
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91,
                             dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTrack = getSoundTrack('ttcc_ene_hroller_laugh.ogg', delay=0.01, node=suit)
    if dmg > 0:
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        return Parallel(suitTrack, sprayTrack, toonTrack, soundTrack, toonSpinTrack, spinTrack1, spinTrack2, spinTrack3)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack, soundTrack)


def doSpin(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    damageDelay = 1.7
    sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
    spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
    spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
    spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
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
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    sprayTrack = getPartTrack(sprayEffect, 1.0, 1.9, [sprayEffect, suit, 0])
    spinTrack1 = getPartTrack(spinEffect1, 1.5, 3.9, [spinEffect1, battle, 0])
    spinTrack2 = getPartTrack(spinEffect2, 1.5, 3.9, [spinEffect2, battle, 0])
    spinTrack3 = getPartTrack(spinEffect3, 1.5, 3.9, [spinEffect3, battle, 0])
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    if dmg > 0:
        soundTrack = getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit)
        toonSpinTrack = Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5))
        return Parallel(suitTrack, sprayTrack, toonTrack, toonSpinTrack, spinTrack1, spinTrack2, spinTrack3, soundTrack)
    else:
        return Parallel(suitTrack, sprayTrack, toonTrack)


def doLegalese(attack):
    suit = attack['suit']
    BattleParticles.loadParticles()
    sprayEffect1 = BattleParticles.createParticleEffect(file='legaleseSpray')
    sprayEffect2 = BattleParticles.createParticleEffect(file='legaleseSpray')
    sprayEffect3 = BattleParticles.createParticleEffect(file='legaleseSpray')
    color = Vec4(0.4, 0, 0, 1)
    BattleParticles.setEffectTexture(sprayEffect1, 'legalese-hc', color=color)
    BattleParticles.setEffectTexture(sprayEffect2, 'legalese-qpq', color=color)
    BattleParticles.setEffectTexture(sprayEffect3, 'legalese-vd', color=color)
    partDelay = 0.5
    partDuration = 1.25
    damageDelay = 1
    dodgeDelay = 0.8
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    sprayTrack1 = getPartTrack(sprayEffect1, partDelay, partDuration, [sprayEffect1, suit, 0])
    sprayTrack2 = getPartTrack(sprayEffect2, partDelay + 0.8, partDuration, [sprayEffect2, suit, 0])
    sprayTrack3 = getPartTrack(sprayEffect3, partDelay + 1.6, partDuration, [sprayEffect3, suit, 0])
    damageAnims = []
    damageAnims.append(['cringe',
     1e-05,
     0.3,
     0.8])
    damageAnims.append(['cringe',
     1e-05,
     0.3,
     0.8])
    damageAnims.append(['cringe', 1e-05, 0.3])
    soundTrack = getSoundTrack('SA_jargon.ogg', delay=1, node=suit)
    toonTrack = getToonTrack(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=dodgeDelay, dodgeAnimNames=['sidestep'], showMissedExtraTime=0.8)
    return Parallel(suitTrack, toonTrack, soundTrack, sprayTrack1, sprayTrack2, sprayTrack3)


def doPeckingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    throwDuration = 3.03
    throwDelay = 2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    propDelay = 1.5
    for i in xrange(0, numBirds):
        next = globalPropPool.getProp('bird')
        next.setScale(0.01)
        next.reparentTo(suit.getRightHand())
        next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
        if dmg > 0:
            #hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6, random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        else:
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        birdTrack = Sequence(Wait(throwDelay), Func(battle.movie.needRestoreRenderProp, next), Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)), LerpPosInterval(next, 0.5, hitPoint))
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.1, Point3(9, 9, 9)))
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
    toonTrack = getToonTrack(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, birdTracks)

def doPeckingOrderVulnerability(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    name = attack['id']
    throwDuration = 3.03
    throwDelay = 2
    taunt = random.choice(
        ["Why don't you 'peck' on someone your own size?", "The real pecking order is now in action!",
         "If you weren't at the bottom of the pecking order before, this one will put you there.", "Birds of a feather strike together, again!",
         "Do not provoke the birds, if you don't want to get pecked."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    battle = attack['battle']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    suitTrack = Sequence(headsUp, tauntInterval, ActorInterval(suit, 'throw-object', playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 5 and 7 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    ceaseSpeechTrack2 = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 6 and 7 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        if name == KICK_UP:
            suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
        else:
            suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack2))
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    propDelay = 1.5
    for i in xrange(0, numBirds):
        next = globalPropPool.getProp('bird')
        next.setScale(0.01)
        next.reparentTo(suit.getRightHand())
        next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
        if dmg > 0:
            # hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6, random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        else:
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        birdTrack = Sequence(Wait(throwDelay), Func(battle.movie.needRestoreRenderProp, next), Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)), LerpPosInterval(next, 0.5, hitPoint))
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.1, Point3(9, 9, 9)))
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
    toonTrack = getToonTakeDamageTrackCheat(attack, toon, target[0]['died'], int(dmg / 2),
                                            2.5, splicedDamageAnims=damageAnims, showDamageExtraTime=1)
    notifyTrack = Sequence(Wait(2.5), Func(toon.showHpTextCheat, - int(dmg / 2)),
                           Func(toon.showHpString, "VULNERABLE!"))
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, birdTracks, notifyTrack)

def doPeckingOrderVulnerabilityGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    throwDuration = 3.03
    throwDelay = 2
    taunt = random.choice(
        ["Why don't you 'peck' on someone your own size?", "The real pecking order is now in action!",
         "If you weren't at the bottom of the pecking order before, this one will put you there.", "Birds of a feather strike together, again!",
         "Do not provoke the birds, if you don't want to get pecked."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))


    suitTrack = Sequence(tauntInterval, ActorInterval(suit, 'throw-object', playRate=1.5))
    ceaseTrack = ActorInterval(suit, 'cease')
    ceaseSoundTrack = Parallel(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    ceaseSpeechTrack = Parallel(Func(suit.setChatAbsolute,
                                     'Quality Control dictates that all Level 7 and 8 gags are now classified as defective.',
                                     CFSpeech | CFTimeout))
    if attack['suit'].dna.name == 'dvk':
        suitTrack.append(Wait(1.0))
        suitTrack.append(Parallel(ceaseTrack, ceaseSoundTrack, ceaseSpeechTrack))
    toonTracks = Parallel()
    allBirdTracks = Parallel()
    for t in attack['target']:
        toon = t['toon']
        dmg = t['hp']
        numBirds = random.randint(10, 20)
        birdTracks = Parallel()
        toonTrack = Parallel()
        propDelay = 1.5
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
        for i in xrange(0, numBirds):
            next = globalPropPool.getProp('bird')
            next.setScale(0.01)
            next.reparentTo(suit.getRightHand())
            next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            if dmg > 0:
                hitPoint = Point3(random.random() * 5 - 2.5, random.random() * 2 - 1 - 6, random.random() * 3 - 1.5 + toon.getHeight() - 0.9)
            else:
                hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
            birdTrack = Sequence(Wait(throwDelay), Func(battle.movie.needRestoreRenderProp, next), Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)), LerpPosInterval(next, 0.5, hitPoint))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.1, Point3(9, 9, 9)))
            birdTracks.append(Sequence(Parallel(birdTrack, scaleTrack), Func(MovieUtil.removeProp, next)))
            toonTrack.append(getToonTakeDamageTrackCheat(attack, toon, t['died'], int(dmg / 2),
                                                    2.5, splicedDamageAnims=damageAnims, showDamageExtraTime=1))
            notifyTrack.append(Sequence(Wait(2.5), Func(t.showHpTextCheat, - int(dmg / 2)),
                                   Func(t.showHpString, "VULNERABLE!")))
        allBirdTracks.append(birdTracks)
        toonTracks.append(toonTrack)
        toonTracks.append(notifyTrack)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack, allBirdTracks)

def doFreeCruiseBAD(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    dmg = target[0]['hp']
    throwDuration = 1.03
    throwDelay = 3.2
    suitTrack = getSuitTrack(attack)
    numBirds = 1
    birdTracks = Parallel()
    propDelay = 1.5
    for i in xrange(0, numBirds):
        next = globalPropPool.getProp('ship')
        next.setScale(0.5)
        #next.reparentTo(suit.getRightHand)
        next.setPos(random.random() * 2 - 0.3, random.random() * 2 - 0.3, random.random() * 2 - 0.3)
        if dmg > 0:
            hitPoint = Point3(random.random() * 6 - 2.5, random.random() * 6 - 1 - 6, random.random() * 6 - 1.5 + toon.getHeight() - 0.9)
        else:
            hitPoint = Point3(random.random() * 2 - 1, random.random() * 4 - 2 - 15, random.random() * 4 - 2 + 2.2)
        birdTrack = Sequence(Wait(throwDelay), Func(battle.movie.needRestoreRenderProp, next), Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)), LerpPosInterval(next, 1.1, hitPoint))
        scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.15, Point3(9, 9, 9)))
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
    toonTrack = getToonTrack(attack, damageDelay=4.2, splicedDamageAnims=damageAnims, dodgeDelay=2.8, dodgeAnimNames=['sidestep'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=1.9, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack, birdTracks)
