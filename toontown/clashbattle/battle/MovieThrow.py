from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.chat.constants.ChatGlobals import  CFSpeech, CFTimeout, CFQuicktalker
from toontown.battle.BattleGlobals import ThrowPresHealPercent
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.toon.ToonDNA import *
from toontown.suit.SuitDNA import *
from toontown.battle import MovieUtil
from toontown.battle import MovieLure
from toontown.battle.MovieUtil import calcAvgSuitPos
from toontown.toonbase import TTLocalizer
from collections import OrderedDict
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

import math

notify = getNotify('MovieThrow')
hitSoundFiles = ('AA_tart_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_wholepie_only.ogg', 'AA_throw_cream_pie_cog.ogg', 'AA_throw_wedding_cake_cog.ogg', 'AA_wholepie_only.ogg')
tPieLeavesHand = 2.7
tPieHitsSuit = 3.0
tSuitDodges = 2.45
ratioMissToHit = 1.5
tPieShrink = 0.7
pieFlyTaskName = 'MovieThrow-pieFly'


def __healToon(toon, hp):
    notify.debug('healToon() - toon: %d hp: %d' % (toon.doId, hp))
    cappedHp = min(toon.getMaxHp() - toon.getHp(), hp * ThrowPresHealPercent)
    cappedHp = math.ceil(cappedHp)
    laughter = random.choice(TTLocalizer.MovieHealLaughterHits1)
    toon.setChatAbsolute(laughter, CFSpeech | CFQuicktalker | CFTimeout)
    if toon.getHp() is not None:
        toon.toonUp(cappedHp, False)
    else:
        notify.debug('__healToon() - toon: %d hp: %d' % (toon.doId, hp))
    return


def addHit(dict, suitId, hitCount):
    if suitId in dict:
        dict[suitId] += hitCount
    else:
        dict[suitId] = hitCount


def doThrows(throws):
    if len(throws) == 0:
        return (None, None)
    suitThrowsDict = OrderedDict()

    for throw in throws:
        if attackAffectsGroup(throw['track'], throw['level']):
            pass
        else:
            suitId = throw['target']['suit'].doId
            if suitId in suitThrowsDict:
                suitThrowsDict[suitId].append(throw)
            else:
                suitThrowsDict[suitId] = [throw]

    suitThrows = list(suitThrowsDict.values())
    suitThrows.sort(key=len)
    totalHitDict = {}
    singleHitDict = {}
    groupHitDict = {}
    for throw in throws:
        if attackAffectsGroup(throw['track'], throw['level']):
            for i in range(len(throw['target'])):
                target = throw['target'][i]
                suitId = target['suit'].doId
                if throw['sidestep'] == 0:
                    addHit(groupHitDict, suitId, 1)
                    addHit(totalHitDict, suitId, 1)
                else:
                    addHit(groupHitDict, suitId, 0)
                    addHit(totalHitDict, suitId, 0)

        else:
            suitId = throw['target']['suit'].doId
            if throw['sidestep'] == 0:
                addHit(singleHitDict, suitId, 1)
                addHit(totalHitDict, suitId, 1)
            else:
                addHit(singleHitDict, suitId, 0)
                addHit(totalHitDict, suitId, 0)

    notify.debug('singleHitDict = %s' % singleHitDict)
    notify.debug('groupHitDict = %s' % groupHitDict)
    notify.debug('totalHitDict = %s' % totalHitDict)
    delay = 0.0
    mtrack = Parallel()
    for st in suitThrows:
        if len(st) > 0:
            ival = __doSuitThrows(st)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = random.random() * 0.3

    retTrack = Sequence()
    retTrack.append(mtrack)
    groupThrowIvals = Parallel()
    groupThrows = []
    for throw in throws:
        if attackAffectsGroup(throw['track'], throw['level']):
            groupThrows.append(throw)

    for throw in groupThrows:
        tracks = None
        tracks = __throwGroupPie(throw, 0, groupHitDict, [])
        if tracks:
            for track in tracks:
                groupThrowIvals.append(track)

    retTrack.append(groupThrowIvals)
    allThrows = Sequence(mtrack, groupThrowIvals)
    camDuration = allThrows.getDuration()
    camTrack = throws[0]['battle'].camera.chooseThrowShot(throws, suitThrowsDict, camDuration)
    return (retTrack, camTrack)


def __doSuitThrows(throws):
    toonTracks = Parallel()
    delay = 0.0
    hitCount = 0
    for throw in throws:
        if throw['sidestep'] == 0:
            hitCount += 1
        else:
            break

    # Need an extra delay on the died cog if we had any KB bonus and any level 7+ throw gag
    needExtraDiedDelay = all([
        any([throw['target']['kbbonus'] < 0 for throw in throws]),
        any([throw['level'] >= 6 for throw in throws]),
        any([bool(throw['target']['died'] != 0 or throw['target']['revived'] != 0) for throw in throws]),
    ])

    for throwIndex, throw in enumerate(throws):
        throw['lastThrow'] = throwIndex == len(throws) - 1
        needTargetExtraDied = needExtraDiedDelay and (throw['target']['died'] != 0 or throw['target']['revived'] != 0)
        tracks = __throwPie(throw, delay, hitCount, needTargetExtraDied)
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
            prop.loop(propName)

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
    for ci in range(prop.getNumChildren()):
        prop.getChild(ci).setHpr(0, -90, 0)

    targetPnt = MovieUtil.avatarFacePoint(suit, other=battle)
    prop.lookAt(targetPnt)


def __propPreflightGroup(props, suits, toon, battle):
    prop = props[0]
    toon.update(0)
    prop.wrtReparentTo(battle)
    for ci in range(prop.getNumChildren()):
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


def __getWeddingCakeSoundTrack(level, hitSuit, node = None):
    throwTrack = Sequence()
    if hitSuit:
        throwSound = globalBattleSoundCache.getSound('AA_throw_wedding_cake.ogg')
        songTrack = Sequence()
        songTrack.append(Wait(1.0))
        songTrack.append(SoundInterval(throwSound, node=node))
        splatSound = globalBattleSoundCache.getSound('AA_throw_wedding_cake_cog.ogg')
        splatTrack = Sequence()
        splatTrack.append(Wait(tPieHitsSuit))
        splatTrack.append(SoundInterval(splatSound, node=node))
        throwTrack.append(Parallel(songTrack, splatTrack))
    else:
        throwSound = globalBattleSoundCache.getSound('AA_throw_wedding_cake_miss.ogg')
        throwTrack.append(Wait(tSuitDodges))
        throwTrack.append(SoundInterval(throwSound, node=node))
    return throwTrack


def __getSoundTrack(level, hitSuit, node = None, delay = 0):
    if level == UBER_GAG_LEVEL_INDEX - 1:
        return __getWeddingCakeSoundTrack(level, hitSuit, node)
    throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    throwTrack = Sequence(Wait(2.6 + delay), SoundInterval(throwSound, node=node))
    if hitSuit:
        hitSound = globalBattleSoundCache.getSound(hitSoundFiles[level])
        hitTrack = Sequence(Wait(tPieHitsSuit + delay), SoundInterval(hitSound, node=node))
        return Parallel(throwTrack, hitTrack)
    else:
        return throwTrack


def addSplat(battle, pieName, suit, prestige, hp, toon):
    pieIndex = list(Splats.keys()).index(pieName)
    MovieUtil.applyVisualEffect(suit, VisualEffectEnum.SPLAT, extraArgs=[pieIndex])
    if prestige:
        __healToon(toon, -hp)


def __throwPie(throw, delay, hitCount, needExtraDiedDelay):
    toon = throw["avatar"]
    target = throw['target']
    lastThrow = throw["lastThrow"]
    suit = target['suit']
    hp = target['hp']
    hpbonus = target['hpbonus']
    kbbonus = target['kbbonus']
    sidestep = throw['sidestep']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    level = throw['level']
    battle = throw['battle']
    origHpr = toon.getHpr(battle)
    notify.debug('toon: %s throws tart at suit: %d for hp: %d died: %d' % (toon.getName(), suit.doId, hp, died))
    pieName = pieNames[level]
    hitSuit = throw['sidestep'] == 0
    pie = globalPropPool.getProp(pieName)
    pieType = globalPropPool.getPropType(pieName)
    pies = [pie]
    hands = toon.getRightHands()
    splatName = 'splat-' + pieName
    splat = globalPropPool.getProp(splatName)
    splatType = globalPropPool.getPropType(splatName)
    try:
        prestige = toon.getTrackBonusLevel(AttackEnum.TOON_THROW) >= 1
    except:
        prestige = False
    toonTrack = Sequence()
    toonFace = Func(toon.headsUp, suit)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    toonTrack.append(ActorInterval(toon, 'throw'))
    toonTrack.append(Func(toon.loop, 'neutral'))
    toonTrack.append(Func(toon.setHpr, battle, origHpr))
    pieShow = Func(MovieUtil.showProps, pies, hands)
    pieAnim = Func(__animProp, pies, pieName, pieType)
    pieScale = LerpScaleInterval(pie, 1.0, pie.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    piePreflight = Func(__propPreflight, pies, suit, toon, battle)
    pieTrack = Sequence(Wait(delay), pieShow, pieAnim, pieScale, Func(battle.movie.needRestoreRenderProp, pies[0]), Wait(tPieLeavesHand - 1.0), piePreflight)
    soundTrack = __getSoundTrack(level, hitSuit, toon, delay)
    if hitSuit:
        pieFly = LerpPosInterval(pie, tPieHitsSuit - tPieLeavesHand, pos=lambda suit=suit: MovieUtil.avatarFacePoint(suit, other=battle), name=pieFlyTaskName, other=battle)
        pieHide = Func(MovieUtil.removeProps, pies)
        splatShow = Func(__showProp, splat, suit, Point3(0, 0.2, suit.getHeight()-0.4))
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
        if sidestep:
            suitPoint = lambda suit=suit: MovieUtil.avatarFacePoint(suit, other=battle)
        else:
            suitPoint = lambda suit=suit: __suitMissPoint(suit, other=battle)
        piePreMiss = Func(__piePreMiss, missDict, pie, suitPoint, battle)
        pieMiss = LerpFunctionInterval(__pieMissLerpCallback, extraArgs=[missDict], duration=(tPieHitsSuit - tPieLeavesHand) * ratioMissToHit)
        pieHide = Func(MovieUtil.removeProps, pies)
        pieTrack.append(piePreMiss)
        pieTrack.append(pieMiss)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
    if hitSuit:
        hasBigThrow = level >= 6 and lastThrow
        suitReactAnim = 'pie-large-react' if hasBigThrow else 'pie-small-react'
        suitResponseTrack = Sequence()
        showDamage = Func(suit.showHpText, hp, openEnded=0, attackTrack=AttackEnum.TOON_THROW, extraText=TTLocalizer.HpTextMarked)
        updateHealthBar = Func(suit.updateHealthBar, hp)
        sival = []
        if kbbonus < 0:
            if hasBigThrow:
                suitReactAnim = 'pie-large-react-lured'
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            suitType = getSuitBodyType(suit.getStyleName())
            animTrack = Sequence()
            reactDuration = None if hasBigThrow else 0.2
            moveWaitDuration = 0.0 if hasBigThrow else 0.2
            moveBlend = 'easeOut' if hasBigThrow else 'noBlend'
            animTrack.append(Parallel(ActorInterval(suit, suitReactAnim, duration=reactDuration), Func(addSplat, battle, pieName, suit, prestige, hp, toon)))
            if not hasBigThrow:
                if suitType == 'a':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.43))
                elif suitType == 'b':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=1.94))
                elif suitType == 'c':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.58))
            animTrack.append(MovieUtil.unlureSuit(suit, battle))
            animTrack.append(Func(suit.loop, 'neutral'))
            if suit.specialHead:
                animTrack.append(Func(suit.specialHead.loopNeutral))
            if suit.stunStars:
                animTrack.append(Func(suit.cleanupStunStars))
            moveTrack = Sequence(Wait(moveWaitDuration), LerpPosInterval(suit, 0.6, pos=suitPos, other=battle, blendType=moveBlend))
            sival = Parallel(animTrack, moveTrack)
        elif hitCount == 1:
            sival = Parallel(ActorInterval(suit, suitReactAnim), MovieUtil.createSuitStunInterval(suit, 0.3, 1.3), Func(addSplat, battle, pieName, suit, prestige, hp, toon))
        else:
            sival = Parallel(ActorInterval(suit, suitReactAnim), Func(addSplat, battle, pieName, suit, prestige, hp, toon))
        suitResponseTrack.append(Wait(delay + tPieHitsSuit))
        suitResponseTrack.append(showDamage)
        suitResponseTrack.append(updateHealthBar)
        suitResponseTrack.append(sival)
        bonusTrack = Sequence(Wait(delay + tPieHitsSuit))
        if kbbonus < 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, kbbonus, 2, openEnded=0, attackTrack=AttackEnum.TOON_THROW))
            bonusTrack.append(Func(suit.updateHealthBar, kbbonus))
        if hpbonus < 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, hpbonus, 1, openEnded=0, attackTrack=AttackEnum.TOON_THROW))
            bonusTrack.append(Func(suit.updateHealthBar, hpbonus))
        suitResponseTrack.append(Wait(0.7 if needExtraDiedDelay else 0.0))
        if revived != 0:
            suitResponseTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
        elif died != 0:
            suitResponseTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
        else:
            suitResponseTrack.append(Func(suit.loop, 'neutral'))
        suitResponseTrack = Parallel(suitResponseTrack, bonusTrack)
    else:
        suitResponseTrack = MovieUtil.createSuitDodgeMultitrack(delay + tSuitDodges, suit, leftSuits, rightSuits, battle.activeSuits)
        if suit.specialHead:
            suitResponseTrack.append(Func(suit.specialHead.loopNeutral))
        if suit.stunStars:
             suitResponseTrack.append(Func(suit.cleanupStunStars))
        if suit.isLured:
            suitResponseTrack.append(Sequence(MovieLure.__createSuitResetPosTrack(suit, battle)))
            suitResponseTrack.append(MovieUtil.unlureSuit(suit, battle))
        suitResponseTrack.append(Func(suit.loop, 'neutral'))
    if not hitSuit and delay > 0:
        return [toonTrack, soundTrack, pieTrack]
    else:
        return [toonTrack,
         soundTrack,
         pieTrack,
         suitResponseTrack]


def __createWeddingCakeFlight(throw, groupHitDict, pie, pies):
    toon = throw["avatar"]
    battle = throw['battle']
    level = throw['level']
    sidestep = throw['sidestep']
    numTargets = len(throw['target'])
    pieName = pieNames[level]
    splatName = 'splat-' + pieName
    splat = globalPropPool.getProp(splatName)
    splats = [splat]
    for i in range(numTargets - 1):
        splats.append(MovieUtil.copyProp(splat))

    splatType = globalPropPool.getPropType(splatName)
    if pieName == 'wedding-cake':
        cakePartStrs = ['cake1',
         'cake2',
         'cake3',
         'caketop']
        cakeParts = []
        for part in cakePartStrs:
            cakeParts.append(pie.find('**/%s' % part))
        # Some hacky stuff to support 5/6 suits
        pie5 = cakeParts[1].copyTo(pie)
        pie5.hide()
        pie5.setPos(cakeParts[1].getPos(pie))
        cakeParts.append(pie5)
        pie6 = cakeParts[2].copyTo(pie)
        pie6.hide()
        pie6.setPos(cakeParts[2].getPos(pie))
        cakeParts.append(pie6)
    else:
        cakeParts = []
        for i in range(6):
            cakeParts.append(globalPropPool.getProp('%s-slice' % pieName))

    def getHandPos():
        pos = toon.getRightHands()[0].getPos(battle)
        return (pos[0], pos[1] + 5, pos[2])

    cakePartDivisions = {}
    cakePartDivisions[1] = [[cakeParts[0],
      cakeParts[1],
      cakeParts[2],
      cakeParts[3]]]
    cakePartDivisions[2] = [[cakeParts[0], cakeParts[1]], [cakeParts[2], cakeParts[3]]]
    cakePartDivisions[3] = [[cakeParts[0], cakeParts[1]], [cakeParts[2]], [cakeParts[3]]]
    cakePartDivisions[4] = [[cakeParts[0]],
     [cakeParts[1]],
     [cakeParts[2]],
     [cakeParts[3]]]
    cakePartDivisions[5] = [[cakeParts[0]],
     [cakeParts[1]],
     [cakeParts[4]],
     [cakeParts[2]],
     [cakeParts[3]]]
    cakePartDivisions[6] = [[cakeParts[0]],
     [cakeParts[1]],
     [cakeParts[4]],
     [cakeParts[2]],
     [cakeParts[5]],
     [cakeParts[3]]]
    cakePartDivToUse = cakePartDivisions[len(throw['target'])]
    groupPieTracks = Parallel()
    for i in range(numTargets):
        target = throw['target'][i]
        suit = target['suit']
        hitSuit = throw['sidestep'] == 0
        singlePieTrack = Sequence()
        if hitSuit:
            piePartReparent = Func(reparentCakePart, pie, cakePartDivToUse[i])
            singlePieTrack.append(piePartReparent)
            cakePartTrack = Parallel()
            if pieName == 'wedding-cake':
                for cakePart in cakePartDivToUse[i]:
                    pieFly = LerpPosInterval(cakePart, tPieHitsSuit - tPieLeavesHand, pos=lambda suit=suit: MovieUtil.avatarFacePoint(suit, other=battle), name=pieFlyTaskName, other=battle)
                    cakePartTrack.append(pieFly)
            else:
                for cakePart in cakePartDivToUse[i]:
                    pieFly = LerpPosInterval(cakePart, tPieHitsSuit - tPieLeavesHand, startPos=getHandPos(), pos=lambda suit=suit: MovieUtil.avatarFacePoint(suit, other=battle), name=pieFlyTaskName, other=battle)
                    cakePartTrack.append(pieFly)

            singlePieTrack.append(cakePartTrack)
            pieRemoveCakeParts = Func(MovieUtil.removeProps, cakePartDivToUse[i])
            pieHide = Func(MovieUtil.removeProps, pies)
            splatShow = Func(__showProp, splats[i], suit, Point3(0, 0.2, suit.getHeight()-0.4))
            splatBillboard = Func(__billboardProp, splats[i])
            splatAnim = ActorInterval(splats[i], splatName)
            splatHide = Func(MovieUtil.removeProp, splats[i])
            singlePieTrack.append(pieRemoveCakeParts)
            singlePieTrack.append(pieHide)
            singlePieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
            singlePieTrack.append(splatShow)
            singlePieTrack.append(splatBillboard)
            singlePieTrack.append(splatAnim)
            singlePieTrack.append(splatHide)
        else:
            missDict = {}
            if sidestep:
                suitPoint = lambda suit=suit: MovieUtil.avatarFacePoint(suit, other=battle)
            else:
                suitPoint = lambda suit=suit: __suitMissPoint(suit, other=battle)
            piePartReparent = Func(reparentCakePart, pie, cakePartDivToUse[i])
            piePreMiss = Func(__piePreMissGroup, missDict, cakePartDivToUse[i], suitPoint, battle)
            pieMiss = LerpFunctionInterval(__pieMissGroupLerpCallback, extraArgs=[missDict], duration=(tPieHitsSuit - tPieLeavesHand) * ratioMissToHit)
            pieHide = Func(MovieUtil.removeProps, pies)
            pieRemoveCakeParts = Func(MovieUtil.removeProps, cakePartDivToUse[i])
            singlePieTrack.append(piePartReparent)
            singlePieTrack.append(piePreMiss)
            singlePieTrack.append(pieMiss)
            singlePieTrack.append(pieRemoveCakeParts)
            singlePieTrack.append(pieHide)
            singlePieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
        groupPieTracks.append(singlePieTrack)

    return groupPieTracks


def __throwGroupPie(throw, delay, groupHitDict):
    toon = throw["avatar"]
    battle = throw['battle']
    level = throw['level']
    sidestep = throw['sidestep']
    numTargets = len(throw['target'])
    avgSuitPos = calcAvgSuitPos(throw)
    origHpr = toon.getHpr(battle)
    toonTrack = Sequence()
    toonFace = Func(toon.headsUp, battle, avgSuitPos)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    toonTrack.append(ActorInterval(toon, 'throw'))
    toonTrack.append(Func(toon.loop, 'neutral'))
    toonTrack.append(Func(toon.setHpr, battle, origHpr))
    suits = []
    for i in range(numTargets):
        suits.append(throw['target'][i]['suit'])

    pieName = pieNames[level]
    pie = globalPropPool.getProp(pieName)
    pieType = globalPropPool.getPropType(pieName)
    pies = [pie]
    hands = toon.getRightHands()
    pieShow = Func(MovieUtil.showProps, pies, hands)
    pieAnim = Func(__animProp, pies, pieName, pieType)
    if pieName == 'weddingCake':
        pieScale1 = LerpScaleInterval(pie, 1.0, pie.getScale() * 1.5, startScale=MovieUtil.PNT3_NEARZERO)
        pieScale2 = LerpScaleInterval(pie2, 1.0, pie2.getScale() * 1.5, startScale=MovieUtil.PNT3_NEARZERO)
    else:
        pieScale1 = LerpScaleInterval(pie, 1.0, pie.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
        pieScale2 = LerpScaleInterval(pie2, 1.0, pie2.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    pieScale = Parallel(pieScale1, pieScale2)
    piePreflight = Func(__propPreflightGroup, pies, suits, toon, battle)
    pieTrack = Sequence(Wait(delay), pieShow, pieAnim, pieScale, Func(battle.movie.needRestoreRenderProp, pies[0]), Wait(tPieLeavesHand - 1.0), piePreflight)
    if pieName != 'wedding-cake':
        pieTrack.append(Parallel(Func(pie.setScale, 0.001), Func(pie2.setScale, 0.001)))
    if level >= 4:
        groupPieTracks = __createWeddingCakeFlight(throw, groupHitDict, pie, pies)
    else:
        notify.error('unhandled throw level %d' % level)
    pieTrack.append(groupPieTracks)
    didThrowHitAnyone = False
    for i in range(numTargets):
        target = throw['target'][i]
        hitSuit = throw['sidestep'] == 0
        if hitSuit:
            didThrowHitAnyone = True

    soundTrack = __getSoundTrack(level, didThrowHitAnyone, toon, delay)
    groupSuitResponseTrack = Parallel()
    for i in range(numTargets):
        target = throw['target'][i]
        suit = target['suit']
        hitSuit = throw['sidestep'] == 0
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        hp = target['hp']
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = target['died']
        revived = target['revived']
        try:
            if toon.getTrackBonusLevel(AttackEnum.TOON_THROW) >= 1:
                prestige = True
            else:
                prestige = False
        except:
            prestige = False
        if hitSuit:
            suitReactAnim = 'pie-large-react' if kbbonus == 0 else 'pie-small-react'
            singleSuitResponseTrack = Sequence()
            showDamage = Func(suit.showHpText, -hp, openEnded=0, attackTrack=AttackEnum.TOON_THROW)
            updateHealthBar = Func(suit.updateHealthBar, hp)
            sival = []
            if kbbonus < 0:
                suitPos, suitHpr = battle.getActorPosHpr(suit)
                suitType = getSuitBodyType(suit.getStyleName())
                animTrack = Sequence()
                animTrack.append(Parallel(ActorInterval(suit, suitReactAnim, duration=0.2), Func(addSplat, battle, pieName, suit, prestige, hp, toon)))
                if suitType == 'a':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.43))
                elif suitType == 'b':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=1.94))
                elif suitType == 'c':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.58))
                animTrack.append(MovieUtil.unlureSuit(suit, battle))
                animTrack.append(Func(suit.loop, 'neutral'))
                if suit.specialHead:
                    animTrack.append(Func(suit.specialHead.loopNeutral))
                if suit.stunStars:
                    animTrack.append(Func(suit.cleanupStunStars))
                moveTrack = Sequence(Wait(0.2), LerpPosInterval(suit, 0.6, pos=suitPos, other=battle))
                sival = Parallel(animTrack, moveTrack)
            elif groupHitDict[suit.doId] == 1:
                sival = Parallel(ActorInterval(suit, suitReactAnim), MovieUtil.createSuitStunInterval(suit, 0.3, 1.3), Func(addSplat, battle, pieName, suit, prestige, hp, toon))
            else:
                sival = Parallel(ActorInterval(suit, suitReactAnim), Func(addSplat, battle, pieName, suit, prestige, hp, toon))
            singleSuitResponseTrack.append(Wait(delay + tPieHitsSuit))
            singleSuitResponseTrack.append(showDamage)
            singleSuitResponseTrack.append(updateHealthBar)
            singleSuitResponseTrack.append(sival)
            bonusTrack = Sequence(Wait(delay + tPieHitsSuit))
            if kbbonus < 0:
                bonusTrack.append(Wait(0.75))
                bonusTrack.append(Func(suit.showHpText, kbbonus, 2, openEnded=0, attackTrack=AttackEnum.TOON_THROW))
                bonusTrack.append(Func(suit.updateHealthBar, kbbonus))
            if hpbonus < 0:
                bonusTrack.append(Wait(0.75))
                bonusTrack.append(Func(suit.showHpText, hpbonus, 1, openEnded=0, attackTrack=AttackEnum.TOON_THROW))
                bonusTrack.append(Func(suit.updateHealthBar, hpbonus))
            if revived != 0:
                singleSuitResponseTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
            elif died != 0:
                singleSuitResponseTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
            else:
                singleSuitResponseTrack.append(Func(suit.loop, 'neutral'))
            singleSuitResponseTrack = Parallel(singleSuitResponseTrack, bonusTrack)
        else:
            groupHitValues = list(groupHitDict.values())
            if groupHitValues.count(0) == len(groupHitValues):
                singleSuitResponseTrack = MovieUtil.createSuitDodgeMultitrack(delay + tSuitDodges, suit, leftSuits, rightSuits, battle.activeSuits)
            else:
                singleSuitResponseTrack = Sequence(Wait(tPieHitsSuit - 0.1), Func(MovieUtil.indicateMissed, suit, 1.0))
        groupSuitResponseTrack.append(singleSuitResponseTrack)

    return [toonTrack,
     pieTrack,
     soundTrack,
     groupSuitResponseTrack]


def reparentCakePart(pie, cakeParts):
    pieParent = pie.getParent()
    notify.debug('pieParent = %s' % pieParent)
    for cakePart in cakeParts:
        cakePart.wrtReparentTo(pieParent)
        cakePart.show()
