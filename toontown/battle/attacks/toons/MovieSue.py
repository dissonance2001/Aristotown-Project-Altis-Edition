from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.suit.SuitDNA import *
from otp.otpbase import OTPLocalizerEnglish
from toontown.nametag import *
from toontown.chat.ChatGlobals import *
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from direct.directnotify import DirectNotifyGlobal
import random
from toontown.battle import MovieCamera
from toontown.battle.attacks.suits import MovieIntervals
from toontown.battle import MovieUtil
from toontown.battle.attacks.toons import MovieNPCSOS
from toontown.battle.MovieUtil import calcAvgSuitPos

notify = DirectNotifyGlobal.directNotify.newCategory('MovieThrow')
hitSoundFiles = ('AA_tart_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_wholepie_only.ogg', 'AA_wholepie_only.ogg')
tPieLeavesHand = 2.7
tPieHitsSuit = 3.0
tSuitDodges = 2.45
ratioMissToHit = 1.5
tPieShrink = 0.7
pieFlyTaskName = 'MovieThrow-pieFly'

def addHit(dict, suitId, hitCount):
    if suitId in dict:
        dict[suitId] += hitCount
    else:
        dict[suitId] = hitCount


def doSues(sues):
    npcArrivals, npcDepartures, npcs = MovieNPCSOS.doNPCTeleports(sues)
    if len(sues) == 0:
        return (None, None)

    suitSuesDict = {}
    i = 0
    try:
        attempt = sues[0]['target'][i]['suit']
        doAdd = True
    except:
        doAdd = False
    for sue in sues:
        if doAdd:
            suitId = sue['target'][i]['suit'].doId
            i = i + 1
        else:
            suitId = sue['target']['suit'].doId
        if suitId in suitSuesDict:
            suitSuesDict[suitId].append(sue)
        else:
            suitSuesDict[suitId] = [sue]

    suitSues = suitSuesDict.values()
    def compFunc(a, b):
        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1
        return 0
    suitSues.sort(compFunc)

    totalHitDict = {}
    singleHitDict = {}
    groupHitDict = {}

    i = 0
    for sue in sues:
        if doAdd:
            suitId = sue['target'][i]['suit'].doId
        else:
            suitId = sue['target']['suit'].doId
        if 1:
            if doAdd:
                if sue['target'][i]['hp'] > 0:
                    addHit(singleHitDict, suitId, 1)
                    addHit(totalHitDict, suitId, 1)
                else:
                    addHit(singleHitDict, suitId, 0)
                    addHit(totalHitDict, suitId, 0)
                i = i + 1
            else:
                if sue['target']['hp'] > 0:
                    addHit(singleHitDict, suitId, 1)
                    addHit(totalHitDict, suitId, 1)
                else:
                    addHit(singleHitDict, suitId, 0)
                    addHit(totalHitDict, suitId, 0)

    notify.debug('singleHitDict = %s' % singleHitDict)
    notify.debug('groupHitDict = %s' % groupHitDict)
    notify.debug('totalHitDict = %s' % totalHitDict)

    delay = random.choice((0.1, 0.2, 0.3, 0.4, 0.5))
    mtrack = Parallel()
    firedTargets = []
    for ss in suitSues:
        if len(ss) > 0:
            ival = __doSuitSues(ss)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = delay + random.choice((0.1, 0.2, 0.3, 0.4, 0.5))

    retTrack = Sequence()
    retTrack.append(npcArrivals)
    retTrack.append(mtrack)
    retTrack.append(npcDepartures)
    enterDuration = npcArrivals.getDuration()
    exitDuration = npcDepartures.getDuration()
    camDuration = retTrack.getDuration()
    camTrack = MovieCamera.chooseSueShot(sues, suitSuesDict, camDuration, enterDuration, exitDuration)
    return (retTrack, camTrack)

def __doSuitSues(sues):
    toonTracks = Parallel()
    delay = 0.0
    hitCount = 0
    i = 0
    try:
        attempt = sues[0]['target'][i]['suit']
        doAdd = True
    except:
        doAdd = False
    for sue in sues:
        if doAdd:
            if sue['target'][i]['hp'] > 0:
                hitCount += 1
                i = i + 1
            else:
                break
        else:
            if sue['target']['hp'] > 0:
                hitCount += 1
            else:
                break

    suitList = []
    i = 0
    for sue in sues:
        if doAdd:
            if sue['target'][i]['suit'] not in suitList:
                suitList.append(sue['target'][i]['suit'])
            i = i + 1
        else:
            if sue['target']['suit'] not in suitList:
                suitList.append(sue['target']['suit'])

    i = 0
    for sue in sues:
        showSuitCannon = 1
        if doAdd:
            if sue['target'][i]['suit'] not in suitList:
                showSuitCannon = 0
            else:
                suitList.remove(sue['target'][i]['suit'])
            for x in xrange(len(sue['target'])):
                tracks = __throwPie(sue, delay, hitCount)
                i = i + 1
                if tracks:
                    for track in tracks:
                        toonTracks.append(track)

                delay = delay + 0
        else:
            if sue['target']['suit'] not in suitList:
                showSuitCannon = 0
            else:
                suitList.remove(sue['target']['suit'])
            tracks = __throwPie(sue, delay, hitCount)
            if tracks:
                for track in tracks:
                    toonTracks.append(track)

            delay = delay + 0

    return toonTracks


def __showProp(prop, parent, pos):
    prop.reparentTo(parent)
    prop.setPos(pos)


def __animProp(props, propName, propType):
    if 'actor' == propType:
        for prop in props:
            prop.play(propName)

    elif 'model' == propType:
        pass
    else:
        notify.error('No such propType as: %s' % propType)


def __billboardProp(prop):
    scale = prop.getScale()
    prop.setBillboardPointWorld()
    prop.setScale(scale)


def __suitMissPoint(suit, other = render):
    pnt = suit.getPos(other)
    pnt.setZ(pnt[2] + suit.getHeight() * 1.3)
    return pnt


def __propPreflight(props, suit, toon, battle):
    prop = props[0]
    toon.update(0)
    prop.wrtReparentTo(battle)
    props[1].reparentTo(hidden)
    for ci in xrange(prop.getNumChildren()):
        prop.getChild(ci).setHpr(0, -90, 0)

    targetPnt = MovieUtil.avatarFacePoint(suit, other=battle)
    prop.lookAt(targetPnt)


def __propPreflightGroup(props, suits, toon, battle):
    prop = props[0]
    toon.update(0)
    prop.wrtReparentTo(battle)
    props[1].reparentTo(hidden)
    for ci in xrange(prop.getNumChildren()):
        prop.getChild(ci).setHpr(0, -90, 0)

    avgTargetPt = Point3(0, 0, 0)
    for suit in suits:
        avgTargetPt += MovieUtil.avatarFacePoint(suit, other=battle)

    avgTargetPt /= len(suits)
    prop.lookAt(avgTargetPt)


def __piePreMiss(missDict, pie, suitPoint, other = render):
    missDict['pie'] = pie
    missDict['startScale'] = pie.getScale()
    missDict['startPos'] = pie.getPos(other)
    v = Vec3(suitPoint - missDict['startPos'])
    endPos = missDict['startPos'] + v * ratioMissToHit
    missDict['endPos'] = endPos


def __pieMissLerpCallback(t, missDict):
    pie = missDict['pie']
    newPos = missDict['startPos'] * (1.0 - t) + missDict['endPos'] * t
    if t < tPieShrink:
        tScale = 0.0001
    else:
        tScale = (t - tPieShrink) / (1.0 - tPieShrink)
    newScale = missDict['startScale'] * max(1.0 - tScale, 0.01)
    pie.setPos(newPos)
    pie.setScale(newScale)


def __piePreMissGroup(missDict, pies, suitPoint, other = render):
    missDict['pies'] = pies
    missDict['startScale'] = pies[0].getScale()
    missDict['startPos'] = pies[0].getPos(other)
    v = Vec3(suitPoint - missDict['startPos'])
    endPos = missDict['startPos'] + v * ratioMissToHit
    missDict['endPos'] = endPos
    notify.debug('startPos=%s' % missDict['startPos'])
    notify.debug('v=%s' % v)
    notify.debug('endPos=%s' % missDict['endPos'])


def __pieMissGroupLerpCallback(t, missDict):
    pies = missDict['pies']
    newPos = missDict['startPos'] * (1.0 - t) + missDict['endPos'] * t
    if t < tPieShrink:
        tScale = 0.0001
    else:
        tScale = (t - tPieShrink) / (1.0 - tPieShrink)
    newScale = missDict['startScale'] * max(1.0 - tScale, 0.01)
    for pie in pies:
        pie.setPos(newPos)
        pie.setScale(newScale)

def __getSoundTrack(level, hitSuit, node = None):
    soundEffect = globalBattleSoundCache.getSound('LB_receive_evidence.ogg')
    soundEffect2 = globalBattleSoundCache.getSound('LB_evidence_miss.ogg')
    soundTrack = Sequence()
    throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    throwTrack = Sequence(Wait(2.6), SoundInterval(throwSound, node=node))
    soundTrack.append(Wait(tPieHitsSuit))
    soundTrack.append(Parallel(SoundInterval(soundEffect, node=node), SoundInterval(soundEffect2, node=node)))
    if hitSuit:
        return Parallel(throwTrack, soundTrack)
    else:
        return throwTrack

def __getSoundTrack2(level, hitSuit, node = None):
    throwSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
    throwTrack = Sequence(Wait(2.15), SoundInterval(throwSound, node=node))
    return throwTrack


def __throwPie(throw, delay, hitCount):
    toon = throw['toon']
    if 'npc' in throw:
        toon = throw['npc']
    hpbonus = throw['hpbonus']
    target = throw['target']
    suit = target['suit']
    hp = target['hp']
    explodeTrack = Sequence()
    kbbonus = target['kbbonus']
    sidestep = throw['sidestep']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    level = throw['level']
    battle = throw['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    notify.debug('toon: %s throws tart at suit: %d for hp: %d died: %d' % (toon.getName(),
     suit.doId,
     hp,
     died))
    pieName = pieNames[level]
    hitSuit = hp > 0
    pie = globalPropPool.getProp('lawbook')
    pieType = globalPropPool.getPropType('lawbook')
    pie2 = MovieUtil.copyProp(pie)
    pies = [pie, pie2]
    hands = toon.getRightHands()
    soundTrack = __getSoundTrack(level, hitSuit, suit)
    toonTrack = Sequence()
    toonFace = Func(toon.headsUp, battle, suitPos)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    toonTrack.append(Parallel(soundTrack, ActorInterval(toon, 'throw')))
    toonTrack.append(Parallel(Func(toon.setToonStatusEffect, 'cooldown', turns=2)))
    toonTrack.append(Func(toon.loop, 'neutral'))
    if not 'npc' in throw:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    pieShow = Func(MovieUtil.showProps, pies, hands)
    pieAnim = Func(__animProp, pies, pieName, pieType)
    pieScale1 = LerpScaleInterval(pie, 1.0, pie.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    pieScale2 = LerpScaleInterval(pie2, 1.0, pie2.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    pieScale = Parallel(pieScale1, pieScale2)
    piePreflight = Func(__propPreflight, pies, suit, toon, battle)
    pieTrack = Sequence(Wait(delay), pieShow, pieAnim, pieScale, Func(battle.movie.needRestoreRenderProp, pies[0]), Wait(tPieLeavesHand - 1.0), piePreflight)
    if hitSuit:
        pieFly = LerpPosInterval(pie, tPieHitsSuit - tPieLeavesHand, pos=MovieUtil.avatarFacePoint(suit, other=battle), name=pieFlyTaskName, other=battle)
        pieHide = Func(MovieUtil.removeProps, pies)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
    else:
        missDict = {}
        if sidestep:
            suitPoint = MovieUtil.avatarFacePoint(suit, other=battle)
        else:
            suitPoint = __suitMissPoint(suit, other=battle)
        piePreMiss = Func(__piePreMiss, missDict, pie, suitPoint, battle)
        pieMiss = LerpFunctionInterval(__pieMissLerpCallback, extraArgs=[missDict], duration=(tPieHitsSuit - tPieLeavesHand) * ratioMissToHit)
        pieHide = Func(MovieUtil.removeProps, pies)
        pieTrack.append(piePreMiss)
        pieTrack.append(pieMiss)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
    if hitSuit:
        suitResponseTrack = Sequence()
        totalDamage = hp

        hpAfter = suit.getQueuedProjectedHP()
        hpBefore = hpAfter + totalDamage

        showDamage = Parallel(Func(suit.setSued2, 1), Func(suit.showHpTextNew, 0, text="CEASE AND DESIST!", colorCode=1))
        explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
        splatName = 'dust'
        splat = globalPropPool.getProp('dust')
        explode = globalPropPool.getProp('dust')
        explode.setTwoSided(True)

        explode.setBillboardPointWorld(2)
        explodeTrack.append(Sequence(Wait(delay + tPieHitsSuit)))
        explodeTrack.append(
            getPropAppearTrack(explode, suit, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))

        sival = []
        sival = ActorInterval(suit, 'pie-small-react')
        suitResponseTrack.append(Wait(delay + tPieHitsSuit))
        suitResponseTrack.append(Func(suit.setSuitStatusEffect, 'sued', modifier=1, turns=4))
        suitResponseTrack.append(showDamage)
        suitResponseTrack.append(sival)
        bonusTrack = Sequence(Wait(delay + tPieHitsSuit))
        suitResponseTrack.append(Func(suit.setNeutralAnimationDrop))
        suitResponseTrack = Parallel(suitResponseTrack, bonusTrack)
    else:
        if suit.getStyleName() in OTPLocalizerEnglish.SuitSueManager:
            suitResponseTrack = Parallel(Sequence(Wait(delay + 2.45), Func(suit.setChatAbsolute, random.choice(
        OTPLocalizerEnglish.SuitSueManager[suit.getStyleName()]), CFSpeech | CFTimeout)), MovieUtil.createSuitDodgeMultitrackSue(battle, delay + 2.45, suit, leftSuits, rightSuits))
        else:
            suitResponseTrack = Parallel(Sequence(Wait(delay + 2.45), Func(suit.setChatAbsolute, random.choice(
        OTPLocalizerEnglish.SuitSueManagerNone), CFSpeech | CFTimeout)), MovieUtil.createSuitDodgeMultitrackSue(battle, delay + 2.45, suit, leftSuits, rightSuits))
    if not hitSuit and delay > 0:
        return [toonTrack, soundTrack, pieTrack, suitResponseTrack]
    else:
        return [toonTrack, explodeTrack,
         pieTrack,
         suitResponseTrack]
    
def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    return MovieIntervals.getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint, scaleUpTime, startScale, poseExtraArgs)