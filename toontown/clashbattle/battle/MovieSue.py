from direct.interval.IntervalGlobal import *
from toontown.clashbattle.battle.BattleBase import *
from toontown.clashbattle.battle.BattleProps import *
from toontown.clashbattle.battle.BattleSounds import *
from otp import *

from toontown.clashbattle.battle.MovieUtil import applyVisualEffect
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.clashbattle.battle.SuitBattleGlobals import ITERATIVE_CHAT
from toontown.toon.ToonDNA import *
from toontown.clashsuit.suit.SuitDNA import *
from toontown.clashbattle.battle import MovieUtil
from toontown.toonbase import TTLocalizer
from toontown.clashbattle.battle.statuses.StatusEffects import MinibossResistancesStatusEffect
from toontown.utils.DirectNotifyCategory import getNotify


notify = getNotify('MovieSue')
tPieLeavesHand = 2.7
tPieHitsSuit = 3.0
tSuitDodges = 2.45
ratioMissToHit = 1.5
tPieShrink = 0.7
pieFlyTaskName = 'MovieSue-pieFly'


def addHit(dict, suitId, hitCount):
    if suitId in dict:
        dict[suitId] += hitCount
    else:
        dict[suitId] = hitCount


def doSues(sues):
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

    suitSues = list(suitSuesDict.values())
    suitSues.sort(key=len)

    totalHitDict = {}
    singleHitDict = {}
    groupHitDict = {}

    i = 0
    for sue in sues:
        if doAdd:
            suitId = sue['target'][i]['suit'].doId
        else:
            suitId = sue['target']['suit'].doId

        if sue['sidestep'] == 0 > 0:
            addHit(singleHitDict, suitId, 1)
            addHit(totalHitDict, suitId, 1)
        else:
            addHit(singleHitDict, suitId, 0)
            addHit(totalHitDict, suitId, 0)
        if doAdd:
            i += 1

    notify.debug('singleHitDict = %s' % singleHitDict)
    notify.debug('groupHitDict = %s' % groupHitDict)
    notify.debug('totalHitDict = %s' % totalHitDict)

    delay = 0.0
    mtrack = Parallel()
    for sf in suitSues:
        if len(sf) > 0:
            ival = __doSuitSues(sf)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = random.random() * 0.3

    camDuration = mtrack.getDuration()
    camTrack = sues[0]['battle'].camera.chooseThrowShot(sues, suitSuesDict, camDuration)
    return (mtrack, camTrack)


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
        if sue['sidestep'] == 0 > 0:
            hitCount += 1
            if doAdd:
                i += 1
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
            for x in range(len(sue['target'])):
                tracks = __throwPie(sue, i, delay, hitCount, showSuitCannon)
                i = i + 1
                if tracks:
                    for track in tracks:
                        toonTracks.append(track)

                delay = delay + TOON_THROW_DELAY
        else:
            if sue['target']['suit'] not in suitList:
                showSuitCannon = 0
            else:
                suitList.remove(sue['target']['suit'])
            tracks = __throwPie(sue, i, delay, hitCount, showSuitCannon)
            if tracks:
                for track in tracks:
                    toonTracks.append(track)

            delay = delay + TOON_THROW_DELAY

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
    if len(props) > 1:
        props[1].reparentTo(hidden)
    for ci in range(prop.getNumChildren()):
        prop.getChild(ci).setHpr(0, -90, 0)

    targetPnt = MovieUtil.avatarFacePoint(suit, other=battle)
    prop.lookAt(targetPnt)


def __piePreMiss(missDict, pie, suitPoint, other = render):
    missDict['pie'] = pie
    missDict['startScale'] = pie.getScale()
    missDict['startPos'] = pie.getPos(other)
    if callable(suitPoint):
        suitPoint = suitPoint()
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


def __getSoundTrack(hitSuit, delay, node = None):
    throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    throwTrack = Sequence(Wait(2.6 + delay), SoundInterval(throwSound, node=node))
    if hitSuit:
        hitSound = globalBattleSoundCache.getSound('LB_receive_evidence.ogg')
        hitTrack = Sequence(Wait(tPieHitsSuit + delay), SoundInterval(hitSound, node=node))
        return Parallel(throwTrack, hitTrack)
    else:
        return throwTrack


def __throwPie(sue, i, delay, hitCount, showCannon = 1):
    toon = sue["avatar"]
    target = sue['target']
    suit = target['suit']
    hp = target['hp']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = sue['battle']
    origHpr = toon.getHpr(battle)
    notify.debug('toon: %s sues tart at suit: %d for hp: %d died: %d' % (toon.getName(), suit.doId, hp, died))
    pieName = 'lawbook'
    hitSuit = target['landed']

    pie = globalPropPool.getProp(pieName)
    pieType = globalPropPool.getPropType(pieName)
    pies = [pie]
    hands = toon.getRightHands()
    splatName = 'dust'
    splat = globalPropPool.getProp(splatName)
    toonTrack = Sequence()
    toonFace = Func(toon.headsUp, suit)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    toonTrack.append(ActorInterval(toon, 'throw'))
    toonTrack.append(Func(toon.loop, 'neutral'))
    toonTrack.append(Func(toon.setHpr, battle, origHpr))
    pieShow = Func(MovieUtil.showProps, pies, hands)
    pieAnim = Func(__animProp, pies, pieName, pieType)
    pieScale1 = LerpScaleInterval(pie, 1.0, pie.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    pieScale = Parallel(pieScale1)
    piePreflight = Func(__propPreflight, pies, suit, toon, battle)
    pieTrack = Sequence(Wait(delay), pieShow, pieAnim, pieScale, Func(battle.movie.needRestoreRenderProp, pies[0]), Wait(tPieLeavesHand - 1.0), piePreflight)
    soundTrack = __getSoundTrack(hitSuit, delay, toon)
    if hitSuit:
        # Immediately apply unite cooldown visual to toons, don't do it inside of the movie
        # The cooldown applies immediately on the AI so they should visually see it immediately as well
        MovieUtil.applyVisualEffect(toon, VisualEffectEnum.UNITE_COOLDOWN)

        pieFly = LerpPosInterval(pie, tPieHitsSuit - tPieLeavesHand, pos=lambda: MovieUtil.avatarFacePoint(suit, other=battle), name=pieFlyTaskName, other=battle)
        pieHide = Func(MovieUtil.removeProps, pies)
        splatShow = Func(__showProp, splat, suit, Point3(0, 0, suit.getHeight()))
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
        suitPoint = lambda: __suitMissPoint(suit, other=battle)
        piePreMiss = Func(__piePreMiss, missDict, pie, suitPoint, battle)
        pieMiss = LerpFunctionInterval(__pieMissLerpCallback, extraArgs=[missDict], duration=(tPieHitsSuit - tPieLeavesHand) * ratioMissToHit)
        pieHide = Func(MovieUtil.removeProps, pies)
        pieTrack.append(piePreMiss)
        pieTrack.append(pieMiss)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
    if hitSuit:
        suitResponseTrack = Sequence()
        showDamage = Func(suit.showHpText, 0, openEnded=0, attackTrack=AttackEnum.TOON_SUE)
        sival = Parallel(
            ActorInterval(suit, 'pie-small-react'),
            Func(applyVisualEffect, suit, VisualEffectEnum.SUED),
        )
        suitResponseTrack.append(Wait(delay + tPieHitsSuit))
        suitResponseTrack.append(showDamage)
        suitResponseTrack.append(sival)
        bonusTrack = Sequence(Wait(delay + tPieHitsSuit))
        if revived != 0:
            suitResponseTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
        elif died != 0:
            suitResponseTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
        else:
            suitResponseTrack.append(Func(suit.loop, 'neutral'))
        suitResponseTrack = Parallel(suitResponseTrack, bonusTrack)
    else:
        chatFunc = suit.setChatIterative if suit.style.name in ITERATIVE_CHAT else suit.setChatAbsolute
        suitResponseTrack = Parallel(
            MovieUtil.createSuitDodgeMultitrack(
                delay + tSuitDodges, suit, leftSuits, rightSuits, battle.activeSuits
            ),
            Sequence(
                Wait(delay + tSuitDodges),
                Func(chatFunc, TTLocalizer.SueFailMessages.get(suit.dna.name, TTLocalizer.SueFailMessage), CFSpeech),
                Wait(3),
                Func(suit.clearChat)
            )
        )
    if not hitSuit and delay > 0:
        return [toonTrack, soundTrack, pieTrack]

    return [toonTrack, soundTrack, pieTrack, suitResponseTrack]
