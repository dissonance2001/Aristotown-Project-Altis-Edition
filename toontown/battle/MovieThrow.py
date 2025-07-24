import random
from pandac.PandaModules import *
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.suit.SuitDNA import *
from toontown.chat.ChatGlobals import *
from direct.task.Task import Task
from direct.task.TaskManagerGlobal import taskMgr
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import MovieCamera
from toontown.battle import MovieNPCSOS
from toontown.battle import MovieUtil
from toontown.battle.MovieUtil import calcAvgSuitPos

notify = DirectNotifyGlobal.directNotify.newCategory('MovieThrow')
hitSoundFiles = ('AA_tart_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_slice_only.ogg', 'AA_throw_cream_pie_cog.ogg', 'AA_throw_wedding_cake_cog.ogg', 'AA_throw_wedding_cake_cog.ogg')
splatDict = {0: 'splat_cake', 1: 'splat_fruit', 2: 'splat_cream',
             3: 'splat_cake', 4: 'splat_fruit', 5: 'splat_cream', 6: 'splat_cake', 7: 'splat_wedding'}
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


def doThrows(throws):
    npcArrivals, npcDepartures, npcs = MovieNPCSOS.doNPCTeleports(throws)
    if len(throws) == 0:
        return (None, None)
    suitThrowsDict = {}
    for throw in throws:
        if attackAffectsGroup(throw['track'], throw['level']):
            pass
        else:
            suitId = throw['target']['suit'].doId
            if suitId in suitThrowsDict:
                suitThrowsDict[suitId].append(throw)
            else:
                suitThrowsDict[suitId] = [throw]

    suitThrows = suitThrowsDict.values()

    def compFunc(a, b):
        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1
        return 0

    suitThrows.sort(compFunc)
    totalHitDict = {}
    singleHitDict = {}
    groupHitDict = {}
    for throw in throws:
        if attackAffectsGroup(throw['track'], throw['level']):
            for i in xrange(len(throw['target'])):
                target = throw['target'][i]
                suitId = target['suit'].doId
                if target['hp'] > 0:
                    addHit(groupHitDict, suitId, 1)
                    addHit(totalHitDict, suitId, 1)
                else:
                    addHit(groupHitDict, suitId, 0)
                    addHit(totalHitDict, suitId, 0)

        else:
            suitId = throw['target']['suit'].doId
            if throw['target']['hp'] > 0:
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
    for st in suitThrows:
        if len(st) > 0:
            ival = __doSuitThrows(st, npcs)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = delay + random.choice((0.1, 0.2, 0.3, 0.4, 0.5))

    retTrack = Sequence()
    retTrack.append(npcArrivals)
    retTrack.append(mtrack)
    retTrack.append(npcDepartures)
    camDuration = retTrack.getDuration()
    enterDuration = npcArrivals.getDuration()
    exitDuration = npcDepartures.getDuration()
    camTrack = MovieCamera.chooseThrowShot(throws, suitThrowsDict, camDuration, enterDuration=enterDuration, exitDuration=exitDuration)
    return (retTrack, camTrack)


def __doSuitThrows(throws, npcs):
    toonTracks = Parallel()
    delay = 0.0
    hitCount = 0
    for throw in throws:
        if throw['target']['hp'] > 0:
            hitCount += 1
        else:
            break

    for throw in throws:
        tracks = __throwPie(throw, delay, hitCount, npcs)
        if tracks:
            for track in tracks:
                toonTracks.append(track)

        delay = delay + TOON_THROW_DELAY

    return toonTracks

def showMarkRounds(suit, level):
    suit.showHpTextWhite("MARKED!")

def doMarkRemovals(markRemovals):
    mainTrack = Parallel()
    for soakRemoval in soakRemovals:
        if len(soakRemoval) > 0:
            suit = soakRemoval['suit']
            mainTrack.append(Parallel(ActorInterval(suit, 'soak', startTime=6.5), __soakSuit(suit, 1)))

    camDuration = mainTrack.getDuration()
    camTrack = MovieCamera.allGroupHighShot(None, camDuration)
    return mainTrack, camTrack


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

def __getBirthdayCakeSoundTrack(level, hitSuit, node = None):
    throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    throwTrack = Sequence(Wait(2.6), SoundInterval(throwSound, node=node))
    splatSound = globalBattleSoundCache.getSound('AA_throw_wedding_cake_cog.ogg')
    splatTrack = Sequence()
    splatTrack.append(Wait(tPieHitsSuit))
    splatTrack.append(SoundInterval(splatSound, node=node))
    throwTrack.append(Parallel(splatTrack))
    if hitSuit:
        hitSound = globalBattleSoundCache.getSound('AA_throw_wedding_cake_cog.ogg')
        hitTrack = Sequence(Wait(tPieLeavesHand), SoundInterval(hitSound, node=node))
        return Parallel(hitTrack)
    else:
        return throwTrack


def __getCreamPieSoundTrack(level, hitSuit, node = None):
    throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    throwTrack = Sequence(Wait(2.6), SoundInterval(throwSound, node=node))
    splatSound = globalBattleSoundCache.getSound('AA_throw_cream_pie_cog.ogg')
    splatTrack = Sequence()
    splatTrack.append(Wait(tPieHitsSuit))
    splatTrack.append(SoundInterval(splatSound, node=node))
    throwTrack.append(Parallel(splatTrack))
    if hitSuit:
        hitSound = globalBattleSoundCache.getSound('AA_throw_cream_pie_cog.ogg')
        hitTrack = Sequence(Wait(tPieLeavesHand), SoundInterval(hitSound, node=node))
        return Parallel(hitTrack)
    else:
        return throwTrack


def __getSoundTrack(level, hitSuit, node = None):
    soundEffect = globalBattleSoundCache.getSound(hitSoundFiles[level])
    soundTrack = Sequence()
    if level == 7:
        throwSound = globalBattleSoundCache.getSound('AA_throw_wedding_cake.ogg')
    else:
        throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    if level == 7:
        throwTrack = Sequence(Wait(1), SoundInterval(throwSound, node=node))
    else:
        throwTrack = Sequence(Wait(2.6), SoundInterval(throwSound, node=node))
    soundTrack.append(Wait(tPieHitsSuit))
    soundTrack.append(SoundInterval(soundEffect, node=node))
    if hitSuit:
        return Parallel(throwTrack, soundTrack)
    else:
        return throwTrack


def __throwPie(throw, delay, hitCount, npcs):
    toon = throw['toon']
    if 'npc' in throw:
        toon = throw['npc']
    hpbonus = throw['hpbonus']
    target = throw['target']
    suit = target['suit']
    hp = target['hp']
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
    pie = globalPropPool.getProp(pieName)
    pieType = globalPropPool.getPropType(pieName)
    pie2 = MovieUtil.copyProp(pie)
    pies = [pie, pie2]
    hands = toon.getRightHands()
    splatName = 'splat-' + pieName
    if pieName == 'wedding-cake':
        splatName = 'splat-birthday-cake'
    elif pieName == 'birthday-cake-slice':
        splatName = 'splat-birthday-cake'
    splat = globalPropPool.getProp(splatName)
    soundTrack = __getSoundTrack(level, hitSuit, suit)
    splatType = globalPropPool.getPropType(splatName)
    toonTrack = Sequence()
    toonFace = Func(toon.headsUp, battle, suitPos)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    toonTrack.append(Parallel(soundTrack, ActorInterval(toon, 'throw')))
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
    soundTrack = __getSoundTrack(level, hitSuit, suit)
    if hitSuit:
        pieFly = LerpPosInterval(pie, tPieHitsSuit - tPieLeavesHand, pos=MovieUtil.avatarFacePoint(suit, other=battle), name=pieFlyTaskName, other=battle)
        pieHide = Func(MovieUtil.removeProps, pies)
        splatShow = Func(__showProp, splat, suit, Point3(0, 0, suit.getHeight()))
        splatBillboard = Func(__billboardProp, splat)
        splatAnim = ActorInterval(splat, splatName)
        splatHide = Func(MovieUtil.removeProp, splat)
        pieTrack.append(pieFly)
        pieTrack.append(pieHide)
        pieTrack.append(Func(battle.movie.clearRenderProp, pies[0]))
        pieTrack.append(splatShow)
        if level == 0:
            pieTrack.append(Func(random.choice((__splatSuitWedding1, __splatSuitWedding2, __splatSuitWedding3, __splatSuitWedding4)), suit, level))
        if level == 1:
            pieTrack.append(Func(random.choice((__splatSuitFruit1, __splatSuitFruit2, __splatSuitFruit3, __splatSuitFruit4)), suit, level))
        if level == 2:
            pieTrack.append(Func(random.choice((__splatSuitCream1, __splatSuitCream2, __splatSuitCream3, __splatSuitCream4)), suit, level))
        if level == 3:
            pieTrack.append(Func(random.choice((__splatSuitCake1, __splatSuitCake2, __splatSuitCake3, __splatSuitCake4)), suit, level))
        if level == 4:
            pieTrack.append(Func(random.choice((__splatSuitFruit1, __splatSuitFruit2, __splatSuitFruit3, __splatSuitFruit4)), suit, level))
        if level == 5:
            pieTrack.append(Func(random.choice((__splatSuitCream1, __splatSuitCream2, __splatSuitCream3, __splatSuitCream4)), suit, level))
        if level == 6:
            pieTrack.append(Func(random.choice((__splatSuitCake1, __splatSuitCake2, __splatSuitCake3, __splatSuitCake4)), suit, level))
        if level == 7:
            pieTrack.append(Func(random.choice((__splatSuitWedding1, __splatSuitWedding2, __splatSuitWedding3, __splatSuitWedding4)), suit, level))
        pieTrack.append(splatBillboard)
        pieTrack.append(splatAnim)
        pieTrack.append(splatHide)
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
        for s in battle.activeSuits:
            if s.dna.name == 'hrollers' and s.getActualLevel() == 25:
                suitResponseTrack.append(Func(s.showHpStringKnockback, 'NICE KNOCKBACK!'))
            if s.dna.name == 'hrollers' and s.getActualLevel() == 26:
                suitResponseTrack.append(Func(s.showHpStringSacrifice, 'NICE COMBO!'))
        showDamage = Sequence(Func(suit.showHpTextThrow, -hp, openEnded=0, attackTrack=THROW_TRACK), Func(suit.showHpString, "MARKED!", openEnded=0))
        #markDamage = Func(showMarkRounds, suit, level)
        value = hp
        #if kbbonus > 0:
            #value = kbbonus
        #if hpbonus > 0:
            #value = hpbonus
        updateHealthBar = Func(suit.updateHealthBar, value)
        sival = []
        if kbbonus > 0:
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            suitType = getSuitBodyType(suit.getStyleName())
            animTrack = Sequence()
            if level <= 5:
                animTrack.append(ActorInterval(suit, 'pie-small-react', duration=0.2))
            elif level <= 5:
                pass
            if suitType == 'a' and level <= 5:
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.43))
            elif suitType == 'a':
                animTrack.append(ActorInterval(suit, 'pie-large-lured', startTime=0))
            elif suitType == 'b'and level <= 5:
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=1.94))
            elif suitType == 'b':
                animTrack.append(ActorInterval(suit, 'pie-large-lured', startTime=0))
            elif suitType == 'c' and level <= 5:
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.58))
            elif suitType == 'c':
                animTrack.append(ActorInterval(suit, 'pie-large-lured', startTime=0))
            animTrack.append(Func(battle.unlureSuit, suit))
            moveTrack = Sequence(Wait(0.2), LerpPosInterval(suit, 0.6, pos=suitPos, other=battle))
            sival = Parallel(animTrack, moveTrack)
        elif hitCount == 1 and level <= 5:
            sival = Parallel(ActorInterval(suit, 'pie-small-react'), MovieUtil.createSuitStunInterval(suit, 0.3, 1.3))
        elif hitCount == 1:
            sival = Parallel(ActorInterval(suit, 'pie-large'), MovieUtil.createSuitStunInterval(suit, 0.3, 1.3))
        elif level <= 5:
            sival = ActorInterval(suit, 'pie-small-react')
        else:
            sival = ActorInterval(suit, 'pie-large')
        suitResponseTrack.append(Wait(delay + tPieHitsSuit))
        suitResponseTrack.append(showDamage)
        suitResponseTrack.append(updateHealthBar)
        suitResponseTrack.append(sival)
        #suitResponseTrack.append(Wait(0))
        #suitResponseTrack.append(markDamage)
        bonusTrack = Sequence(Wait(delay + tPieHitsSuit))
        if kbbonus > 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, -kbbonus, 2, openEnded=0, attackTrack=THROW_TRACK))
            bonusTrack.append(Func(suit.updateHealthBar, kbbonus))
        if hpbonus > 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, -hpbonus, 1, openEnded=0, attackTrack=THROW_TRACK))
            bonusTrack.append(Func(suit.updateHealthBar, hpbonus))
        if suit.dna.name == 'redd' and revived != 0:
            suitResponseTrack.append(MovieUtil.createSuitReviveRedd(suit, battle))
        if revived != 0 and suit.isSkeleton:
            suitResponseTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
        if revived != 0 and not suit.isSkeleton and not suit.dna.name == 'redd':
            suitResponseTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
        if died != 0 and suit.isVirtual:
            suitResponseTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        if died != 0 and not suit.isVirtual:
            suitResponseTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
        suitResponseTrack.append(Func(suit.setNeutralAnimation))
        suitIndex = battle.activeSuits.index(suit)
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex - 1, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex + 1, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex - 2, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex + 2, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex - 3, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex + 3, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex - 4, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex + 4, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex - 5, battle.activeSuits, hp, battle))
        suitResponseTrack.append(__ScapegoatAbsorb(suitIndex + 5, battle.activeSuits, hp, battle))
        suitResponseTrack = Parallel(suitResponseTrack, bonusTrack)
    else:
        suitResponseTrack = MovieUtil.createSuitDodgeMultitrack(delay + tSuitDodges, suit, leftSuits, rightSuits)
    if not hitSuit and delay > 0:
        return [toonTrack, soundTrack, pieTrack]
    else:
        return [toonTrack,
         pieTrack,
         suitResponseTrack]

def __ScapegoatAbsorb(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding and not suits[suitIndex].dna.name == 'hroller':
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.425), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(value * 0.425))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'), MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        return suitTrack
    elif len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding and suits[suitIndex].dna.name == 'hrolnothingler':
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.115), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(value * 0.115))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'),
                                  MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        return suitTrack
    else:
        return Sequence()


def __createWeddingCakeFlight(throw, groupHitDict, pie, pies):
    toon = throw['toon']
    battle = throw['battle']
    level = throw['level']
    sidestep = throw['sidestep']
    hpbonus = throw['hpbonus']
    numTargets = len(throw['target'])
    pieName = pieNames[level]
    splatName = 'splat-' + pieName
    if pieName == 'wedding-cake':
        splatName = 'splat-birthday-cake'
    splat = globalPropPool.getProp(splatName)
    splats = [splat]
    for i in xrange(numTargets - 1):
        splats.append(MovieUtil.copyProp(splat))

    splatType = globalPropPool.getPropType(splatName)
    cakePartStrs = ['cake1',
     'cake2',
     'cake3',
     'caketop']
    cakeParts = []
    for part in cakePartStrs:
        cakeParts.append(pie.find('**/%s' % part))

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
    cakePartDivToUse = cakePartDivisions[len(throw['target'])]
    groupPieTracks = Parallel()
    for i in xrange(numTargets):
        target = throw['target'][i]
        suit = target['suit']
        hitSuit = target['hp'] > 0
        singlePieTrack = Sequence()
        if hitSuit:
            piePartReparent = Func(reparentCakePart, pie, cakePartDivToUse[i])
            singlePieTrack.append(piePartReparent)
            cakePartTrack = Parallel()
            for cakePart in cakePartDivToUse[i]:
                pieFly = LerpPosInterval(cakePart, tPieHitsSuit - tPieLeavesHand, pos=MovieUtil.avatarFacePoint(suit, other=battle), name=pieFlyTaskName, other=battle)
                cakePartTrack.append(pieFly)

            singlePieTrack.append(cakePartTrack)
            pieRemoveCakeParts = Func(MovieUtil.removeProps, cakePartDivToUse[i])
            pieHide = Func(MovieUtil.removeProps, pies)
            splatShow = Func(__showProp, splats[i], suit, Point3(0, 0, suit.getHeight()))
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
                suitPoint = MovieUtil.avatarFacePoint(suit, other=battle)
            else:
                suitPoint = __suitMissPoint(suit, other=battle)
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


def __throwGroupPie(throw, delay, groupHitDict, npcs):
    toon = throw['toon']
    if 'npc' in throw:
        toon = throw['npc']
    battle = throw['battle']
    level = throw['level']
    sidestep = throw['sidestep']
    hpbonus = throw['hpbonus']
    numTargets = len(throw['target'])
    avgSuitPos = calcAvgSuitPos(throw)
    origHpr = toon.getHpr(battle)
    toonTrack = Sequence()
    toonFace = Func(toon.headsUp, battle, avgSuitPos)
    toonTrack.append(Wait(delay))
    toonTrack.append(toonFace)
    toonTrack.append(ActorInterval(toon, 'throw'))
    toonTrack.append(Func(toon.loop, 'neutral'))
    if not 'npc' in throw:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    suits = []
    for i in xrange(numTargets):
        suits.append(throw['target'][i]['suit'])

    pieName = pieNames[level]
    pie = globalPropPool.getProp(pieName)
    pieType = globalPropPool.getPropType(pieName)
    pie2 = MovieUtil.copyProp(pie)
    pies = [pie, pie2]
    hands = toon.getRightHands()
    pieShow = Func(MovieUtil.showProps, pies, hands)
    pieAnim = Func(__animProp, pies, pieName, pieType)
    pieScale1 = LerpScaleInterval(pie, 1.0, pie.getScale() * 1.5, startScale=MovieUtil.PNT3_NEARZERO)
    pieScale2 = LerpScaleInterval(pie2, 1.0, pie2.getScale() * 1.5, startScale=MovieUtil.PNT3_NEARZERO)
    pieScale = Parallel(pieScale1, pieScale2)
    piePreflight = Func(__propPreflightGroup, pies, suits, toon, battle)
    pieTrack = Sequence(Wait(delay), pieShow, pieAnim, pieScale, Func(battle.movie.needRestoreRenderProp, pies[0]), Wait(tPieLeavesHand - 1.0), piePreflight)
    if level == UBER_GAG_LEVEL_INDEX:
        groupPieTracks = __createWeddingCakeFlight(throw, groupHitDict, pie, pies)
    else:
        notify.error('unhandled throw level %d' % level)
    pieTrack.append(groupPieTracks)
    didThrowHitAnyone = False
    for i in xrange(numTargets):
        target = throw['target'][i]
        hitSuit = target['hp'] > 0
        if hitSuit:
            didThrowHitAnyone = True

    soundTrack = __getSoundTrack(level, didThrowHitAnyone, toon)
    groupSuitResponseTrack = Parallel()
    for i in xrange(numTargets):
        target = throw['target'][i]
        suit = target['suit']
        hitSuit = target['hp'] > 0
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        hp = target['hp']
        kbbonus = target['kbbonus']
        died = target['died']
        revived = target['revived']
        if hitSuit:
            singleSuitResponseTrack = Sequence()
            showDamage = Func(suit.showHpText, -hp, openEnded=0, attackTrack=THROW_TRACK)
            updateHealthBar = Func(suit.updateHealthBar, hp)
            sival = []
            if kbbonus > 0:
                suitPos, suitHpr = battle.getActorPosHpr(suit)
                suitType = getSuitBodyType(suit.getStyleName())
                animTrack = Sequence()
                animTrack.append(ActorInterval(suit, 'pie-small-react', duration=0.2))
                if suitType == 'a':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.43))
                elif suitType == 'b':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=1.94))
                elif suitType == 'c':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.58))
                animTrack.append(Func(battle.unlureSuit, suit))
                moveTrack = Sequence(Wait(0.2), LerpPosInterval(suit, 0.6, pos=suitPos, other=battle))
                sival = Parallel(animTrack, moveTrack)
            elif groupHitDict[suit.doId] == 1:
                sival = Parallel(ActorInterval(suit, 'pie-small-react'), MovieUtil.createSuitStunInterval(suit, 0.3, 1.3))
            else:
                sival = ActorInterval(suit, 'pie-small-react')
            singleSuitResponseTrack.append(Wait(delay + tPieHitsSuit))
            singleSuitResponseTrack.append(showDamage)
            singleSuitResponseTrack.append(updateHealthBar)
            singleSuitResponseTrack.append(sival)
            bonusTrack = Sequence(Wait(delay + tPieHitsSuit))
            if kbbonus > 0:
                bonusTrack.append(Wait(0.75))
                bonusTrack.append(Func(suit.showHpText, -kbbonus, 2, openEnded=0, attackTrack=THROW_TRACK))
                bonusTrack.append(Func(suit.updateHealthBar, kbbonus))
            if hpbonus > 0:
                bonusTrack.append(Wait(0.75))
                bonusTrack.append(Func(suit.showHpText, -hpbonus, 1, openEnded=0, attackTrack=THROW_TRACK))
                bonusTrack.append(Func(suit.updateHealthBar, hpbonus))
            if revived != 0:
                singleSuitResponseTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
            if suit.virtual and died !=0:
                singleSuitResponseTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, toon, battle))
            elif died != 0:
                singleSuitResponseTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
            else:
                singleSuitResponseTrack.append(Func(suit.setNeutralAnimation))
            singleSuitResponseTrack = Parallel(singleSuitResponseTrack, bonusTrack)
        else:
            groupHitValues = groupHitDict.values()
            if groupHitValues.count(0) == len(groupHitValues):
                singleSuitResponseTrack = MovieUtil.createSuitDodgeMultitrack(delay + tSuitDodges, suit, leftSuits, rightSuits)
            else:
                singleSuitResponseTrack = Sequence(Wait(tPieHitsSuit - 0.1), Func(MovieUtil.indicateMissed, suit, 1.0))
        groupSuitResponseTrack.append(singleSuitResponseTrack)

    return [toonTrack,
     pieTrack,
     soundTrack,
     groupSuitResponseTrack]

def __splatSuitWedding1(suit, level):
    splatTex = loader.loadTexture('phase_5/maps/splat_wedding_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_wedding%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    #for headPart in suit.headParts:
        #if not suit.dna.name == 'lit':
            #headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitFruit1(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_fruit_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_fruit%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitCake1(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_cake_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_cake%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitCream1(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_cream_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_cream%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitWedding2(suit, level):
    splatTex = loader.loadTexture('phase_5/maps/splat_wedding_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_wedding%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    #for headPart in suit.headParts:
        #if not suit.dna.name == 'lit':
            #headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitFruit2(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_fruit_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_fruit%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitCake2(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_cake_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_cake%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitCream2(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_cream_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_cream%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitWedding3(suit, level):
    splatTex = loader.loadTexture('phase_5/maps/splat_wedding_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_wedding%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    #for headPart in suit.headParts:
        #if not suit.dna.name == 'lit':
            #headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitFruit3(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_fruit_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_fruit%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitCake3(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_cake_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_cake%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitCream3(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_cream_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_cream%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitWedding4(suit, level):
    splatTex = loader.loadTexture('phase_5/maps/splat_wedding_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_wedding%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    #for headPart in suit.headParts:
        #if not suit.dna.name == 'lit':
            #headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitFruit4(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_fruit_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_fruit%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitCake4(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_cake_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_cake%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)

def __splatSuitCream4(suit, level):
    splatTex = loader.loadTexture(
        'phase_5/maps/splat_cream_%s.png' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splatTex2 = loader.loadTexture('phase_5/maps/tiny_' + splatDict[level] + '.png')
    splat = TextureStage('splat_cream%s' % random.choice((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)))
    splat.setMode(TextureStage.MDecal)
   # splat.setSavedResult(False)
    # for headPart in suit.headParts:
    # if not suit.dna.name == 'lit':
    # headPart.setTexture(splat, splatTex)
    if suit.dna.name == 'dsf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'mad':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.dna.name == 'crf':
        suit.find('**/highroller_body').setTexture(splat, splatTex)
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
    elif suit.isSkeleton:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)
        for headPart in suit.headParts:
            headPart.setTexture(splat, splatTex)
    else:
        suit.find('**/body').setTexture(splat, splatTex)
        suit.find('**/necktie-s').setTexture(splat, splatTex)
        suit.find('**/necktie-w').setTexture(splat, splatTex)
        suit.find('**/bowtie').setTexture(splat, splatTex)


def reparentCakePart(pie, cakeParts):
    pieParent = pie.getParent()
    notify.debug('pieParent = %s' % pieParent)
    for cakePart in cakeParts:
        cakePart.wrtReparentTo(pieParent)
