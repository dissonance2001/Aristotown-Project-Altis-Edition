import random
import math
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.battle import MovieCamera
from toontown.suit.SuitDNA import *
from toontown.chat.ChatGlobals import *
from toontown.battle import MovieUtil
from toontown.battle.attacks.toons import MovieThrow
from toontown.chat.ChatGlobals import *
from toontown.battle import MovieCamera
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleParticles
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals

notify = DirectNotifyGlobal.directNotify.newCategory('MovieSquirt')
hitSoundFiles = ('AA_squirt_flowersquirt.ogg', 'AA_squirt_glasswater.ogg', 'AA_squirt_neonwatergun.ogg',
                 'SA_watercooler_spray_only.ogg', 'AA_squirt_seltzer.ogg', 'firehose_spray.ogg',
                 'AA_throw_stormcloud.ogg', 'AA_squirt_Geyser.ogg')
missSoundFiles = ('AA_squirt_flowersquirt_miss.ogg', 'AA_squirt_glasswater_miss.ogg', 'AA_squirt_neonwatergun_miss.ogg',
                  'AA_pie_throw_only.ogg', 'AA_squirt_seltzer_miss.ogg', 'firehose_spray.ogg',
                  'AA_throw_stormcloud_miss.ogg', 'AA_squirt_Geyser.ogg')
sprayScales = [0.2, 0.3, 0.3, 0.4, 0.6, 0.8, 1.0, 2.0]
WaterSprayColor = Point4(0.75, 0.75, 1.0, 0.8)
SoakColor = Point4(0.65, 0.65, 1.0, 1.0)
pieFlyTaskName = 'MovieThrow-pieFly'

def doSquirts(squirts):
    if len(squirts) == 0:
        return (None, None)

    suitSquirtsDict = {}
    doneUber = 0
    skip = 0
    for squirt in squirts:
        skip = 0
        if skip:
            pass
        elif type(squirt['target']) == type([]):
            if 1:
                target = squirt['target'][0]
                suitId = target['suit'].doId
                if suitId in suitSquirtsDict:
                    suitSquirtsDict[suitId].append(squirt)
                else:
                    suitSquirtsDict[suitId] = [squirt]
        else:
            suitId = squirt['target']['suit'].doId
            if suitId in suitSquirtsDict:
                suitSquirtsDict[suitId].append(squirt)
            else:
                suitSquirtsDict[suitId] = [squirt]

    suitSquirts = suitSquirtsDict.values()

    def compFunc(a, b):
        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1
        return 0
    suitSquirts.sort(compFunc)

    delay = random.choice((0.1, 0.2, 0.3, 0.4, 0.5))

    mtrack = Parallel()
    for st in suitSquirts:
        if len(st) > 0:
            ival = __doSuitSquirts(st)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = delay + random.choice((0.1, 0.2, 0.3, 0.4, 0.5))

    camDuration = mtrack.getDuration()
    camTrack = MovieCamera.chooseSquirtShot(squirts, suitSquirtsDict, camDuration)
    return (mtrack, camTrack)


def __doSuitSquirts(squirts):
    uberClone = 0
    toonTracks = Parallel()
    delay = 0.0
    if type(squirts[0]['target']) == type([]):
        for target in squirts[0]['target']:
            if len(squirts) == 1 and target['hp'] > 0:
                fShowStun = 1
            else:
                fShowStun = 0

    elif len(squirts) == 1 and squirts[0]['target']['hp'] > 0:
        fShowStun = 1
    else:
        fShowStun = 0
    for s in squirts:
        tracks = __doSquirt(s, delay, fShowStun, uberClone)
        if s['level'] >= ToontownBattleGlobals.UBER_GAG_LEVEL_INDEX:
            uberClone = 1
        if tracks:
            for track in tracks:
                toonTracks.append(track)

        delay = delay + TOON_SQUIRT_DELAY

    return toonTracks

def doSoakRemovals(soakRemovals):
    mainTrack = Parallel()
    for soakRemoval in soakRemovals:
        if len(soakRemoval) > 0:
            suit = soakRemoval['suit']
            mainTrack.append(Parallel(ActorInterval(suit, 'soak', startTime=6.5), __soakSuit(suit, 1)))

    camDuration = mainTrack.getDuration()
    camTrack = MovieCamera.allGroupHighShot(None, camDuration)
    return mainTrack, camTrack


def __doSquirt(squirt, delay, fShowStun, uberClone = 0):
    squirtSequence = Sequence(Wait(delay))
    if type(squirt['target']) == type([]):
        for target in squirt['target']:
            notify.debug('toon: %s squirts prop: %d at suit: %d for hp: %d' % (squirt['toon'].getName(),
             squirt['level'],
             target['suit'].doId,
             target['hp']))

    else:
        notify.debug('toon: %s squirts prop: %d at suit: %d for hp: %d' % (squirt['toon'].getName(),
         squirt['level'],
         squirt['target']['suit'].doId,
         squirt['target']['hp']))
    if uberClone:
        ival = squirtfn_array[squirt['level']](squirt, delay, fShowStun, uberClone)
        if ival:
            squirtSequence.append(ival)
    else:
        ival = squirtfn_array[squirt['level']](squirt, delay, fShowStun)
        if ival:
            squirtSequence.append(ival)
    return [squirtSequence]


def __suitTargetPoint(suit):
    pnt = suit.getPos(render)
    pnt.setZ(pnt[2] + suit.getHeight() * 0.66)
    return Point3(pnt)


def __getSplashTrack(point, scale, delay, battle, splashHold = 0.01):

    def prepSplash(splash, point):
        if callable(point):
            point = point()
        splash.reparentTo(render)
        splash.setPos(point)
        scale = splash.getScale()
        splash.setBillboardPointWorld()
        splash.setScale(scale)

    splash = globalPropPool.getProp('splash-from-splat')
    splash.setScale(scale)
    return Sequence(Func(battle.movie.needRestoreRenderProp, splash), Wait(delay), Func(prepSplash, splash, point), ActorInterval(splash, 'splash-from-splat'), Wait(splashHold), Func(MovieUtil.removeProp, splash), Func(battle.movie.clearRenderProp, splash))

def __createSuitResetPosTrack2(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.setNeutralAnimationTrap))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def __getSuitTrack(suit, tContact, tDodge, attack, hp, hpbonus, kbbonus, anim, died, leftSuits, rightSuits, battle, toon, fShowStun, beforeStun = 0.5, afterStun = 1.8, geyser = 0, uberRepeat = 0, revived = 0, level = 0):
    if hp > 0:
        suitTrack = Sequence()
        soakTracks = Parallel()
        sival = ActorInterval(suit, anim)
        sival = []
        if kbbonus > 0 and not geyser:
            level = attack['level']
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            suitType = getSuitBodyType(suit.getStyleName())
            animTrack = Sequence()
            if level == 5:
                animTrack.append(ActorInterval(suit, anim, duration=1.0))
            else:
                animTrack.append(ActorInterval(suit, anim, duration=0.2))
            if suitType == 'a' and level == 5:
                animTrack.append(ActorInterval(suit, anim, startTime=1))
            elif suitType == 'b' and level == 5:
                animTrack.append(ActorInterval(suit, anim, startTime=1))
            elif suitType == 'c' and level == 5:
                animTrack.append(ActorInterval(suit, anim, startTime=1))
            elif suitType == 'a':
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.43))
            elif suitType == 'b':
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=1.94))
            elif suitType == 'c':
                animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.58))
            animTrack.append(Func(battle.unlureSuit, suit))
            moveTrack = Sequence(Wait(0.2), LerpPosInterval(suit, 0.6, pos=suitPos, other=battle))
            sival = Parallel(animTrack, moveTrack)
        elif geyser:
            animTrack = Sequence()
            suitStartPos = suit.getPos()
            suitFloat = Point3(0, 0, 20)
            suitEndPos = Point3(suitStartPos[0] + suitFloat[0], suitStartPos[1] + suitFloat[1], suitStartPos[2] + suitFloat[2])
            suitType = getSuitBodyType(suit.getStyleName())
            if suitType == 'a':
                startFlailFrame = 16
                endFlailFrame = 16
            elif suitType == 'b':
                startFlailFrame = 15
                endFlailFrame = 15
            else:
                startFlailFrame = 15
                endFlailFrame = 15
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            moveTrack = Sequence(LerpPosInterval(suit, 0.6, pos=suitPos, other=battle))
            sival = Sequence(ActorInterval(suit, 'slip-backward', playRate=0.5, startFrame=0, endFrame=startFlailFrame - 1), Func(suit.pingpong, 'slip-backward', fromFrame=startFlailFrame, toFrame=endFlailFrame), moveTrack, ActorInterval(suit, 'slip-backward', playRate=1.0, startFrame=endFlailFrame))
            sUp = LerpPosInterval(suit, 1.1, suitEndPos, startPos=suitStartPos, fluid=1)
            sDown = LerpPosInterval(suit, 0.6, suitStartPos, startPos=suitEndPos, fluid=1)
        elif fShowStun == 1:
            sival = Parallel(ActorInterval(suit, anim), MovieUtil.createSuitStunInterval(suit, beforeStun, afterStun))
        else:
            sival = ActorInterval(suit, anim)
        #soakTracks.append(__soakSuit(suit, tContact))
        totalDamage = hp

        if kbbonus > 0:
            totalDamage += kbbonus
        if hpbonus > 0:
            totalDamage += hpbonus

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)

        hpAfter = suit.getQueuedProjectedHP()
        hpBefore = hpAfter + totalDamage
        if suit.dna.name == 'redd':
            showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="SOAKED 1 ROUND", attackTrack=SQUIRT_TRACK, colorCode=1))
        elif suit.isVirtual:
            showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="SOAKED 2 ROUNDS", attackTrack=SQUIRT_TRACK, colorCode=1))
        elif suit.isSkeleton:
            showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="SOAKED 3 ROUNDS", attackTrack=SQUIRT_TRACK, colorCode=1))
        else:
            showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="SOAKED 4 ROUNDS", attackTrack=SQUIRT_TRACK, colorCode=1))
        value = hp
        #if kbbonus > 0:
            #value += kbbonus
        #if hpbonus > 0:
            #value += hpbonus
        updateHealthBar = Func(suit.updateHealthBar, value)
        if suit.dna.name == 'redd':
            soakSuit = (Func(suit.makeSoaked, 1))
        elif suit.isVirtual:
            soakSuit = (Func(suit.makeSoaked, 1))
        elif suit.isSkeleton:
            soakSuit = (Func(suit.makeSoaked, 2))
        else:
            soakSuit = (Func(suit.makeSoaked, 3))
        suitTrack.append(Func(suit.setSoaked, 1))
        if suit.dna.name == 'sgoat' and suit.isShielding:
            suitTrack.append(Func(suit.addRageBuilding, hp + 150))
        if suit.dna.name == 'phouse':
            suitTrack.append(Func(suit.addPowerhouseRotation, hp + 150))
        if suit.dna.name == 'liquid' and suit.isStormCell:
            suitTrack.append(Func(suit.addStormCellDamage))
        if suit.isHeavyRain:
            suitTrack.append(Func(suit.addHeavyRainDamage, hp))
        if suit.isSued:
            suitTrack.append(Func(suit.makeSued, 3))
        suitTrack.append(Wait(tContact))
        if suit.squirtRushJob:
            suitTrack.append(Func(suit.makeUnSquirtRushJob))
        suitTrack.append(__soakSuit(suit, tContact))
        suitIndex = battle.activeSuits.index(suit)
        soakTracks.append(Wait(tContact))
        if toon.getTrackBonusLevel(SQUIRT_TRACK) > 1:
            soakTracks.append(__soakNearby(suit, suitIndex + 1, battle.activeSuits, tContact, hp, died, battle, 1, SQUIRT_TRACK, level))
            soakTracks.append(__soakNearby2(suit, suitIndex - 1, battle.activeSuits, tContact, hp, died, battle, 1, SQUIRT_TRACK, level))
        else:
            soakTracks.append(__soakNearby3(suit, suitIndex + 1, battle.activeSuits, tContact, hp, died, battle, 0, SQUIRT_TRACK, level))
            soakTracks.append(__soakNearby4(suit, suitIndex - 1, battle.activeSuits, tContact, hp, died, battle, 0, SQUIRT_TRACK, level))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(soakSuit)
        if geyser:
            suitTrack.append(Func(battle.unlureSuit, suit))
        durationToWait = 0
        if kbbonus > 0:
            durationToWait += 0.75
        if hpbonus > 0:
            durationToWait += 0.75
        if not geyser:
            suitTrack.append(Parallel(sival))
        elif not uberRepeat:
            geyserMotion = Sequence(sUp, Wait(0.0), sDown)
            suitLaunch = Parallel(sival, geyserMotion)
            suitTrack.append(suitLaunch)
        else:
            suitTrack.append(Wait(5.5))
        bonusTrack = Sequence(Wait(tContact))
        if kbbonus > 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, -kbbonus, 2, openEnded=0, attackTrack=SQUIRT_TRACK))
            bonusTrack.append(Func(suit.updateHealthBar, kbbonus))
        if hpbonus > 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, -hpbonus, 1, openEnded=0, attackTrack=SQUIRT_TRACK))
            bonusTrack.append(Func(suit.updateHealthBar, hpbonus))
        if kbbonus == 0:
            suitTrack.append(Sequence(__createSuitResetPosTrack2(suit, battle), Func(battle.unlureSuit, suit), Func(suit.makeUnLured)))
        suitTrack.append(Func(suit.setDizzy, 0))
        suit.setPendingQueuedLured(False)
        suitTrack.append(Func(suit.setNeutralAnimation))
        if suit.dna.name == 'redd' and revived != 0:
            suitTrack.append(MovieUtil.createSuitReviveRedd(suit, battle))
        if revived != 0 and suit.isSkeleton:
            suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
        if revived != 0 and not suit.isSkeleton and not suit.dna.name == 'redd':
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
        if died != 0 and suit.isVirtual and not suit.isOverpressured:
            suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        if died != 0 and not suit.isVirtual and not suit.isOverpressured:
            suitTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
        if not died:
            suitTrack.append(suit.makeDeathCheckInterval(0, battle))
        return Parallel(suitTrack, bonusTrack, soakTracks)
    else:
        return MovieUtil.createSuitDodgeMultitrack(battle, tDodge, suit, leftSuits, rightSuits)


def say(statement):
    print statement

def __ScapegoatAbsorb(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding:
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].addAbsorbDamage, suits[suitIndex], int(hp * 0.45)))
        suitTrack.append(showDamage)
        return suitTrack
    else:
        return Sequence()

def __ScapegoatAbsorbSplash(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding:
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].addAbsorbDamage, suits[suitIndex], int(hp * 0.45)))
        suitTrack.append(showDamage)
        return suitTrack
    else:
        return Sequence()

def __soakNearby(suit, suitIndex, suits, tContact, hp, died, battle, bonus, attackTrack, level):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal and not suits[suitIndex].isOilRain:
        value = math.ceil(hp * 0.75)
        return Sequence(
            Wait(tContact),  __soakSuit(suits[suitIndex], tContact),
            suits[suitIndex].makeSplashAndDeathInterval(
                tContact, value, battle, bonus, attackTrack, level=0
            ),
            Func(suits[suitIndex].setNeutralAnimationDrop),
            Func(suits[suitIndex].addStormCellDamage)
                if suits[suitIndex].dna.name == 'liquid' and suits[suitIndex].isStormCell
                else Wait(0),
            Func(suits[suitIndex].addHeavyRainDamage, value)
                if suits[suitIndex].isHeavyRain
                else Wait(0)
        )
    return Sequence()

def __soakNearby2(suit, suitIndex, suits, tContact, hp, died, battle, bonus, attackTrack, level):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal and not suits[suitIndex].isOilRain:
        value = math.ceil(hp * 0.75)
        return Sequence(
            Wait(tContact),  __soakSuit(suits[suitIndex], tContact),
            suits[suitIndex].makeSplashAndDeathInterval(
                tContact, value, battle, bonus, attackTrack, level=0
            ),
            Func(suits[suitIndex].setNeutralAnimationDrop),
            Func(suits[suitIndex].addStormCellDamage)
                if suits[suitIndex].dna.name == 'liquid' and suits[suitIndex].isStormCell
                else Wait(0),
            Func(suits[suitIndex].addHeavyRainDamage, value)
                if suits[suitIndex].isHeavyRain
                else Wait(0)
        )
    return Sequence()

def __soakNearby3(suit, suitIndex, suits, tContact, hp, died, battle, bonus, attackTrack, level):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal and not suits[suitIndex].isOilRain:
        value = math.ceil(hp / 3)
        return Sequence(
            Wait(tContact),  __soakSuit(suits[suitIndex], tContact),
            suits[suitIndex].makeSplashAndDeathInterval(
                tContact, value, battle, bonus, attackTrack, level=0
            ),
            Func(suits[suitIndex].setNeutralAnimationDrop),
            Func(suits[suitIndex].addStormCellDamage)
                if suits[suitIndex].dna.name == 'liquid' and suits[suitIndex].isStormCell
                else Wait(0),
            Func(suits[suitIndex].addHeavyRainDamage, value)
                if suits[suitIndex].isHeavyRain
                else Wait(0)
        )
    return Sequence()

def __soakNearby4(suit, suitIndex, suits, tContact, hp, died, battle, bonus, attackTrack, level):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal and not suits[suitIndex].isOilRain:
        value = math.ceil(hp / 3)
        return Sequence(
            Wait(tContact),             __soakSuit(suits[suitIndex], tContact),
            suits[suitIndex].makeSplashAndDeathInterval(
                tContact, value, battle, bonus, attackTrack, level=0
            ),
            Func(suits[suitIndex].setNeutralAnimationDrop),
            Func(suits[suitIndex].addStormCellDamage)
            if suits[suitIndex].dna.name == 'liquid' and suits[suitIndex].isStormCell
            else Wait(0),
            Func(suits[suitIndex].addHeavyRainDamage, value)
            if suits[suitIndex].isHeavyRain
            else Wait(0)
        )
    return Sequence()


def __getSoundTrack(level, hitSuit, delay, node = None):
    if hitSuit:
        soundEffect = globalBattleSoundCache.getSound(hitSoundFiles[level])
    else:
        soundEffect = globalBattleSoundCache.getSound(missSoundFiles[level])
    soundTrack = Sequence()
    if soundEffect:
        soundTrack.append(Wait(delay))
        soundTrack.append(SoundInterval(soundEffect, node=node))
    return soundTrack


def showSoakRounds(suit, level):
    suit.showHpTextWhite("SOAKED %i ROUNDS" % ToontownBattleGlobals.AvSoakRounds[level + 1])

def __soakSuit(suit, tContact, remove=0):
    if remove:
        color = Point4(1.0, 1.0, 1.0, 1.0)
    else:
        color = SoakColor
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit]
    suitInterval = Sequence()
    actorNode = suit.find('**/__Actor_modelRoot')
    actorCollection = actorNode.findAllMatches('*')
    parts = ()
    texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_soaked.png')
    for thingIndex in xrange(0, actorCollection.getNumPaths()):
        thing = actorCollection[thingIndex]
        if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
            if not suit.dna.name == 'cbutcher' and not suit.isShadow:
                suitInterval.append(Func(thing.setColor, color))
    if not suit.isSkeleton and not suit.isShadow:
        hands = suit.find('**/hands')
        handTint = Vec4(
            suit.handColor[0] * color[0],
            suit.handColor[1] * color[1],
            suit.handColor[2] * color[2],
            suit.handColor[3] * color[3]
        )
        suitInterval.append(Func(hands.setColorScale, handTint))
    if suit.dna.name == 'lgator' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeWetLitigator))
    if suit.dna.name == 'treasure' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeWetTreasurer))
    if suit.style.name == 'safesupervis' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeWetFirestarter))
        suitInterval.append(Parallel(Func(suit.makeDamageDown), Func(suit.checkDamageDown, + 25)))
    if suit.style.name == 'fires' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeWetFirestarter))
    return suitInterval


def __doFlower(squirt, delay, fShowStun):
    toon = squirt['toon']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    tTotalFlowerToonAnimationTime = 2.5
    tFlowerFirstAppears = 1.0
    dFlowerScaleTime = 0.5
    tSprayStarts = tTotalFlowerToonAnimationTime
    dSprayScale = 0.2
    dSprayHold = 0.1
    tContact = tSprayStarts + dSprayScale
    tSuitDodges = tTotalFlowerToonAnimationTime
    tracks = Parallel()
    button = globalPropPool.getProp('squirt-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle, suitPos), Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'squirt-button')), Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    tracks.append(__getSoundTrack(level, hitSuit, tTotalFlowerToonAnimationTime - 0.4, toon))
    flower = globalPropPool.getProp('squirting-flower')
    flower.setScale(1.5, 1.5, 1.5)
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)

    def getSprayStartPos(flower = flower):
        toon.update(0)
        return flower.getPos(render)

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
    lodnames = toon.getLODNames()
    toonlod0 = toon.getLOD(lodnames[0])
    toonlod1 = toon.getLOD(lodnames[1])
    if base.config.GetBool('want-new-anims', 1):
        if not toonlod0.find('**/def_joint_attachFlower').isEmpty():
            flower_joint0 = toonlod0.find('**/def_joint_attachFlower')
    else:
        flower_joint0 = toonlod0.find('**/joint_attachFlower')
    if base.config.GetBool('want-new-anims', 1):
        if not toonlod1.find('**/def_joint_attachFlower').isEmpty():
            flower_joint1 = toonlod1.find('**/def_joint_attachFlower')
    else:
        flower_joint1 = toonlod1.find('**/joint_attachFlower')
    flower_jointpath0 = flower_joint0.attachNewNode('attachFlower-InstanceNode')
    flower_jointpath1 = flower_jointpath0.instanceTo(flower_joint1)
    flowerTrack = Sequence(Wait(tFlowerFirstAppears), Func(flower.reparentTo, flower_jointpath0), LerpScaleInterval(flower, dFlowerScaleTime, flower.getScale(), startScale=MovieUtil.PNT3_NEARZERO), Wait(tTotalFlowerToonAnimationTime - dFlowerScaleTime - tFlowerFirstAppears))
    if hp <= 0:
        flowerTrack.append(Wait(0.5))
    flowerTrack.append(sprayTrack)
    flowerTrack.append(LerpScaleInterval(flower, dFlowerScaleTime, MovieUtil.PNT3_NEARZERO))
    flowerTrack.append(Func(flower_jointpath1.removeNode))
    flowerTrack.append(Func(flower_jointpath0.removeNode))
    flowerTrack.append(Func(MovieUtil.removeProp, flower))
    tracks.append(flowerTrack)
    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, scale, tSprayStarts + dSprayScale, battle))
    if hp > 0 or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, squirt, hp, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=0))
    return tracks


def __doWaterGlass(squirt, delay, fShowStun):
    toon = squirt['toon']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    dGlassHold = 5.0
    dGlassScale = 0.5
    tSpray = 82.0 / toon.getFrameRate('spit')
    sprayPoseFrame = 88
    dSprayScale = 0.1
    dSprayHold = 0.1
    tContact = tSpray + dSprayScale
    tSuitDodges = max(tSpray - 0.5, 0.0)
    tracks = Parallel()
    tracks.append(ActorInterval(toon, 'spit'))
    soundTrack = __getSoundTrack(level, hitSuit, 1.7, toon)
    tracks.append(soundTrack)
    glass = globalPropPool.getProp('glass')
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    glassTrack = Sequence(Func(MovieUtil.showProp, glass, hand_jointpath0), ActorInterval(glass, 'glass'), Func(hand_jointpath1.removeNode), Func(hand_jointpath0.removeNode), Func(MovieUtil.removeProp, glass))
    tracks.append(glassTrack)
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)

    def getSprayStartPos(toon = toon):
        toon.update(0)
        lod0 = toon.getLOD(toon.getLODNames()[0])
        if base.config.GetBool('want-new-anims', 1):
            if not lod0.find('**/def_head').isEmpty():
                joint = lod0.find('**/def_head')
            else:
                joint = lod0.find('**/joint_head')
        else:
            joint = lod0.find('**/joint_head')
        n = hidden.attachNewNode('pointInFrontOfHead')
        n.reparentTo(toon)
        n.setPos(joint.getPos(toon) + Point3(0, 0.3, -0.2))
        p = n.getPos(render)
        n.removeNode()
        del n
        return p

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
    tracks.append(Sequence(Wait(tSpray), sprayTrack))
    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, scale, tSpray + dSprayScale, battle))
    if hp > 0 or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, squirt, hp, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=1))
    return tracks


def __doWaterGun(squirt, delay, fShowStun):
    toon = squirt['toon']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    tPistol = 0.0
    dPistolScale = 0.5
    dPistolHold = 1.8
    tSpray = 48.0 / toon.getFrameRate('water-gun')
    sprayPoseFrame = 63
    dSprayScale = 0.1
    dSprayHold = 0.3
    tContact = tSpray + dSprayScale
    tSuitDodges = 1.1
    tracks = Parallel()
    toonTrack = Sequence(Func(toon.headsUp, battle, suitPos), ActorInterval(toon, 'water-gun'), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, hitSuit, 1.8, toon)
    tracks.append(soundTrack)
    pistol = globalPropPool.getProp('water-gun')
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)

    def getSprayStartPos(pistol = pistol, toon = toon):
        toon.update(0)
        joint = pistol.find('**/joint_nozzle')
        p = joint.getPos(render)
        return p

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
    pistolPos = Point3(0.28, 0.1, 0.08)
    pistolHpr = VBase3(85.6, -4.44, 94.43)
    pistolTrack = Sequence(Func(MovieUtil.showProp, pistol, hand_jointpath0, pistolPos, pistolHpr), LerpScaleInterval(pistol, dPistolScale, pistol.getScale(), startScale=MovieUtil.PNT3_NEARZERO), Wait(tSpray - dPistolScale))
    pistolTrack.append(sprayTrack)
    pistolTrack.append(Wait(dPistolHold))
    pistolTrack.append(LerpScaleInterval(pistol, dPistolScale, MovieUtil.PNT3_NEARZERO))
    pistolTrack.append(Func(hand_jointpath1.removeNode))
    pistolTrack.append(Func(hand_jointpath0.removeNode))
    pistolTrack.append(Func(MovieUtil.removeProp, pistol))
    tracks.append(pistolTrack)
    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, 0.3, tSpray + dSprayScale, battle))
    if hp > 0 or delay <= 0:
        tracks.append(
            __getSuitTrack(suit, tContact, tSuitDodges, squirt, hp, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits,
                           rightSuits, battle, toon, fShowStun, revived=revived, level=2))
    return tracks

def __doWaterBalloon(squirt, delay, fShowStun):
    toon = squirt['toon']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    balloonName = pieNames[8]
    tWindUp = 1.7
    tLaunch = tWindUp + 0.9
    tContact = tLaunch + 0.3
    tSuitDodges = max(tContact - 0.7, 0.0)
    balloon = globalPropPool.getProp('waterBalloon')
    balloon.setColor(0.2, 1, 0.4, 1)
    balloon.setScale(1.2, 1.2, 0.8)
    balloon2 = MovieUtil.copyProp(balloon)
    balloons = [balloon, balloon2]
    hands = toon.getRightHands()
    tracks = Parallel()
    toonTrack = toonThrowTrack(toon, battle, delay, suitPos, origHpr)
    tracks.append(toonTrack)
    balloonShow = Func(MovieUtil.showProps, balloons, hands)
    balloonScale1 = LerpScaleInterval(balloon, 1.0, balloon.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    balloonScale2 = LerpScaleInterval(balloon2, 1.0, balloon2.getScale(), startScale=MovieUtil.PNT3_NEARZERO)
    balloonScale = Parallel(balloonScale1, balloonScale2)
    balloonPreflight = Func(__propPreflight, balloons, suit, toon, battle)
    balloonTrack = Sequence(Wait(delay), balloonShow, balloonScale,
                            Func(battle.movie.needRestoreRenderProp, balloons[0]), Wait(tLaunch - 1.0),
                            balloonPreflight)

    targetPoint = __suitTargetPoint(suit)

    soundThrow = Sequence(Wait(2.6), SoundInterval(globalBattleSoundCache.getSound('AA_pie_throw_only.ogg'), node=toon))
    soundSplash = __getSoundTrack(level, hitSuit, tContact, toon)
    soundTracks = Parallel(soundThrow, soundSplash)
    tracks.append(soundTracks)

    if hitSuit:
        balloonTrack.append(LerpPosInterval(balloon, tContact - tLaunch,
                                            pos=MovieUtil.avatarFacePoint(suit, other=battle),
                                            name=pieFlyTaskName, other=battle))
        balloonTrack.append(Func(MovieUtil.removeProps, balloons))
        balloonTrack.append(Func(battle.movie.clearRenderProp, balloons[0]))

    else:
        balloonTrack.append(LerpPosInterval(balloon, tContact - tLaunch,
                                            pos=MovieUtil.avatarFacePoint(suit, other=battle),
                                            name=pieFlyTaskName, other=battle))
        balloonTrack.append(Func(MovieUtil.removeProps, balloons))
        balloonTrack.append(Func(battle.movie.clearRenderProp, balloons[0]))
    tracks.append(balloonTrack)

    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, scale, tContact, battle))
    if hp > 0 or delay <= 0:
        tracks.append(
            __getSuitTrack(suit, tContact, tSuitDodges, squirt, hp, hpbonus, kbbonus, 'squirt-small-react', died,
                           leftSuits,
                           rightSuits, battle, toon, fShowStun, revived=revived, level=3))
    return tracks

def toonThrowTrack(toon, battle, delay, suitPos, origHpr):
    return Sequence(Wait(delay), Func(toon.headsUp, battle, suitPos), ActorInterval(toon, 'throw'),
                    Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))

def __propPreflight(props, suit, toon, battle):
    prop = props[0]
    toon.update(0)
    prop.wrtReparentTo(battle)
    props[1].reparentTo(hidden)
    for ci in xrange(prop.getNumChildren()):
        prop.getChild(ci).setHpr(0, -90, 0)

    targetPnt = MovieUtil.avatarFacePoint(suit, other=battle)
    prop.lookAt(targetPnt)

def __piePreMiss(missDict, pie, suitPoint, other=render):
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


def __doSeltzerBottle(squirt, delay, fShowStun):
    toon = squirt['toon']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    tBottle = 0.0
    dBottleScale = 0.5
    dBottleHold = 3.0
    tSpray = 53.0 / toon.getFrameRate('hold-bottle') + 0.05
    dSprayScale = 0.2
    dSprayHold = 0.1
    tContact = tSpray + dSprayScale
    tSuitDodges = max(tContact - 0.7, 0.0)
    tracks = Parallel()
    toonTrack = Sequence(Func(toon.headsUp, battle, suitPos), ActorInterval(toon, 'hold-bottle'), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, hitSuit, tSpray - 0.1, toon)
    tracks.append(soundTrack)
    bottle = globalPropPool.getProp('bottle')
    hands = toon.getRightHands()
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)

    def getSprayStartPos(bottle = bottle, toon = toon):
        toon.update(0)
        joint = bottle.find('**/joint_toSpray')
        n = hidden.attachNewNode('pointBehindSprayProp')
        n.reparentTo(toon)
        n.setPos(joint.getPos(toon) + Point3(0, -0.4, 0))
        p = n.getPos(render)
        n.removeNode()
        del n
        return p

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    bottleTrack = Sequence(Func(MovieUtil.showProp, bottle, hand_jointpath0), LerpScaleInterval(bottle, dBottleScale, bottle.getScale(), startScale=MovieUtil.PNT3_NEARZERO), Wait(tSpray - dBottleScale))
    bottleTrack.append(sprayTrack)
    bottleTrack.append(Wait(dBottleHold))
    bottleTrack.append(LerpScaleInterval(bottle, dBottleScale, MovieUtil.PNT3_NEARZERO))
    bottleTrack.append(Func(hand_jointpath1.removeNode))
    bottleTrack.append(Func(hand_jointpath0.removeNode))
    bottleTrack.append(Func(MovieUtil.removeProp, bottle))
    tracks.append(bottleTrack)
    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, scale, tSpray + dSprayScale, battle))
    if (hp > 0 or delay <= 0) and suit:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, squirt, hp, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=3))
    return tracks


def __doFireHose(squirt, delay, fShowStun):
    toon = squirt['toon']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = 0.3
    tAppearDelay = 0.7
    dHoseHold = 0.7
    dAnimHold = 5.1
    tSprayDelay = 2.8
    tSpray = 0.2
    dSprayScale = 0.1
    dSprayHold = 1.8
    tContact = 2.9
    tSuitDodges = 2.1
    tracks = Parallel()
    toonTrack = Sequence(Wait(tAppearDelay), Func(toon.headsUp, battle, suitPos), ActorInterval(toon, 'firehose'), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, hitSuit, tSprayDelay, toon)
    tracks.append(soundTrack)
    hose = globalPropPool.getProp('firehose')
    hydrant = globalPropPool.getProp('hydrant')
    hose.reparentTo(hydrant)
    (hose.pose('firehose', 2),)
    hydrantNode = toon.attachNewNode('hydrantNode')
    hydrantNode.clearTransform(toon.getGeomNode().getChild(0))
    hydrantScale = hydrantNode.attachNewNode('hydrantScale')
    hydrant.reparentTo(hydrantScale)
    toon.pose('firehose', 30)
    toon.update(0)
    torso = toon.getPart('torso', '1000')
    if toon.style.torso[0] == 'm':
        hydrant.setPos(torso, 0, 0, -1.85)
    else:
        hydrant.setPos(torso, 0, 0, -1.45)
    hydrant.setPos(0, 0, hydrant.getZ())
    base = hydrant.find('**/base')
    base.setColor(1, 1, 1, 0.5)
    base.setPos(toon, 0, 0, 0)
    toon.loop('neutral')
    targetPoint = lambda suit = suit: __suitTargetPoint(suit)

    def getSprayStartPos(hose = hose, toon = toon, targetPoint = targetPoint):
        toon.update(0)
        if hose.isEmpty() == 1:
            if callable(targetPoint):
                return targetPoint()
            else:
                return targetPoint
        joint = hose.find('**/joint_water_stream')
        n = hidden.attachNewNode('pointBehindSprayProp')
        n.reparentTo(toon)
        n.setPos(joint.getPos(toon) + Point3(0, -0.55, 0))
        p = n.getPos(render)
        n.removeNode()
        del n
        return p

    sprayTrack = Sequence()
    sprayTrack.append(Wait(tSprayDelay))
    sprayTrack.append(MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale))
    tracks.append(sprayTrack)
    hydrantNode.detachNode()
    propTrack = Sequence(Func(battle.movie.needRestoreRenderProp, hydrantNode), Func(hydrantNode.reparentTo, toon), LerpScaleInterval(hydrantScale, tAppearDelay * 0.5, Point3(1, 1, 1.4), startScale=Point3(1, 1, 0.01)), LerpScaleInterval(hydrantScale, tAppearDelay * 0.3, Point3(1, 1, 0.8), startScale=Point3(1, 1, 1.4)), LerpScaleInterval(hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1.2), startScale=Point3(1, 1, 0.8)), LerpScaleInterval(hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1), startScale=Point3(1, 1, 1.2)), ActorInterval(hose, 'firehose', duration=dAnimHold), Wait(dHoseHold - 0.2), LerpScaleInterval(hydrantScale, 0.2, Point3(1, 1, 0.01), startScale=Point3(1, 1, 1)), Func(MovieUtil.removeProps, [hydrantNode, hose]), Func(battle.movie.clearRenderProp, hydrantNode))
    tracks.append(propTrack)
    if hp > 0:
        tracks.append(__getSplashTrack(targetPoint, 0.4, 2.7, battle, splashHold=1.5))
    if hp > 0 or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, squirt, hp, hpbonus, kbbonus, 'squirt-large-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=4))
    return tracks


def __doStormCloud(squirt, delay, fShowStun):
    toon = squirt['toon']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    hitSuit = hp > 0
    scale = sprayScales[level]
    tButton = 0.0
    dButtonScale = 0.5
    dButtonHold = 3.0
    tContact = 2.9
    tSpray = 1
    tSuitDodges = 1.8
    tracks = Parallel()
    soundTrack = __getSoundTrack(level, hitSuit, 2.3, toon)
    soundTrack2 = __getSoundTrack(level, hitSuit, 4.6, toon)
    tracks.append(soundTrack)
    tracks.append(soundTrack2)
    button = globalPropPool.getProp('squirt-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle, suitPos), Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'squirt-button')), Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    cloud = globalPropPool.getProp('stormcloud')
    cloud2 = MovieUtil.copyProp(cloud)
    BattleParticles.loadParticles()
    trickleEffect = BattleParticles.createParticleEffect(file='trickleLiquidate')
    rainEffect = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')
    cloudHeight = suit.height + 3
    cloudPosPoint = Point3(0, 0, cloudHeight)
    scaleUpPoint = Point3(3, 3, 3)
    rainEffects = [rainEffect, rainEffect2, rainEffect3]
    rainDelay = 1
    effectDelay = 0.3
    if hp > 0:
        cloudHold = 4.7
    else:
        cloudHold = 1.7

    def getCloudTrack(cloud, suit, cloudPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, cloudHold, useEffect, battle = battle, trickleEffect = trickleEffect):
        track = Sequence(Func(MovieUtil.showProp, cloud, suit, cloudPosPoint), Func(cloud.pose, 'stormcloud', 0), LerpScaleInterval(cloud, 1.5, scaleUpPoint, startScale=MovieUtil.PNT3_NEARZERO), Wait(rainDelay))
        if useEffect == 1:
            ptrack = Parallel()
            delay = trickleDuration = cloudHold * 0.25
            trickleTrack = Sequence(Func(battle.movie.needRestoreParticleEffect, trickleEffect), ParticleInterval(trickleEffect, cloud, worldRelative=0, duration=trickleDuration, cleanup=True), Func(battle.movie.clearRestoreParticleEffect, trickleEffect))
            track.append(trickleTrack)
            for i in xrange(0, 3):
                dur = cloudHold - 2 * trickleDuration
                ptrack.append(Sequence(Func(battle.movie.needRestoreParticleEffect, rainEffects[i]), Wait(delay), ParticleInterval(rainEffects[i], cloud, worldRelative=0, duration=dur, cleanup=True), Func(battle.movie.clearRestoreParticleEffect, rainEffects[i])))
                delay += effectDelay

            ptrack.append(Sequence(Wait(3 * effectDelay), ActorInterval(cloud, 'stormcloud', startTime=1, duration=cloudHold)))
            track.append(ptrack)
        else:
            track.append(ActorInterval(cloud, 'stormcloud', startTime=1, duration=cloudHold))
        track.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        track.append(Func(MovieUtil.removeProp, cloud))
        return track

    tracks.append(getCloudTrack(cloud, suit, cloudPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, cloudHold, useEffect=1))
    tracks.append(getCloudTrack(cloud2, suit, cloudPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, cloudHold, useEffect=0))
    if hp > 0 or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, squirt, hp, hpbonus, kbbonus, 'soak', died, leftSuits, rightSuits, battle, toon, fShowStun, beforeStun=2.6, afterStun=2.3, revived=revived, level=5))
    return tracks


def __doGeyser(squirt, delay, fShowStun, uberClone = 0):
    toon = squirt['toon']
    level = squirt['level']
    hpbonus = squirt['hpbonus']
    target = squirt['target']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    tracks = Parallel()
    tButton = 0.0
    dButtonScale = 0.5
    dButtonHold = 3.0
    tContact = 2.9
    tSpray = 1
    tSuitDodges = 1.8
    button = globalPropPool.getProp('squirt-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    battle = squirt['battle']
    suitPos = suit.getPos(battle)
    origHpr = toon.getHpr(battle)
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle, suitPos), Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'squirt-button')), Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    hitSuit = hp > 0
    scale = sprayScales[level]
    soundTrack = __getSoundTrack(level, hitSuit, 1.8, toon)
    delayTime = random.random()
    tracks.append(Wait(delayTime))
    tracks.append(soundTrack)
    cloud = globalPropPool.getProp('geyser')
    cloud2 = MovieUtil.copyProp(cloud)
    BattleParticles.loadParticles()
    geyserHeight = battle.getH()
    geyserPosPoint = Point3(0, 0, geyserHeight)
    scaleUpPoint = Point3(1.1, 1.1, 2.0)
    rainEffects = []
    rainDelay = 2.5
    effectDelay = 0.3
    if hp > 0:
        geyserHold = 1.5
    else:
        geyserHold = 0.5

    def getGeyserTrack(geyser, suit, geyserPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, geyserHold, useEffect, battle = battle):
        geyserMound = MovieUtil.copyProp(geyser)
        geyserRemoveM = geyserMound.findAllMatches('**/Splash*')
        geyserRemoveM.addPathsFrom(geyserMound.findAllMatches('**/spout'))
        for i in xrange(geyserRemoveM.getNumPaths()):
            geyserRemoveM[i].removeNode()

        geyserWater = MovieUtil.copyProp(geyser)
        geyserRemoveW = geyserWater.findAllMatches('**/hole')
        geyserRemoveW.addPathsFrom(geyserWater.findAllMatches('**/shadow'))
        for i in xrange(geyserRemoveW.getNumPaths()):
            geyserRemoveW[i].removeNode()

        track = Sequence(Wait(rainDelay), Func(MovieUtil.showProp, geyserMound, battle, suit.getPos(battle)), Func(MovieUtil.showProp, geyserWater, battle, suit.getPos(battle)), LerpScaleInterval(geyserWater, 1.0, scaleUpPoint, startScale=MovieUtil.PNT3_NEARZERO), Wait(geyserHold * 0.5), LerpScaleInterval(geyserWater, 0.5, MovieUtil.PNT3_NEARZERO, startScale=scaleUpPoint))
        track.append(LerpScaleInterval(geyserMound, 0.5, MovieUtil.PNT3_NEARZERO))
        track.append(Func(MovieUtil.removeProp, geyserMound))
        track.append(Func(MovieUtil.removeProp, geyserWater))
        track.append(Func(MovieUtil.removeProp, geyser))
        return track

    if not uberClone:
        tracks.append(Sequence(Wait(delayTime), getGeyserTrack(cloud, suit, geyserPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, geyserHold, useEffect=1)))
    if hp > 0 or delay <= 0:
        tracks.append(Sequence(Wait(delayTime), __getSuitTrack(suit, tContact, tSuitDodges, squirt, hp, hpbonus, kbbonus, 'soak', died, leftSuits, rightSuits, battle, toon, fShowStun, beforeStun=2.6, afterStun=2.3, geyser=1, uberRepeat=uberClone, revived=revived, level=6)))

    return tracks


squirtfn_array = (__doFlower,
                   __doWaterGlass,
                   __doWaterGun,
                   __doWaterBalloon,
                   __doSeltzerBottle,
                   __doFireHose,
                   __doStormCloud,
                   __doGeyser)