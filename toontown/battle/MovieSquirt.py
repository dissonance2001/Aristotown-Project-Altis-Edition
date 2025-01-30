import random
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.suit.SuitDNA import *
from toontown.chat.ChatGlobals import *
from toontown.battle import MovieUtil
from toontown.battle import MovieThrow
import PlayByPlayText
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
            updateTrack = Parallel(Func(suit.setChatAbsolute,
                                        '',
                                        CFSpeech | CFTimeout))
            animTrack.append(updateTrack)
            sival = Parallel(animTrack, moveTrack)
        elif geyser:
            animTrack = Sequence()
            suitStartPos = suit.getPos()
            suitFloat = Point3(0, 0, 14)
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
        showDamage = Sequence(Func(suit.showHpTextSquirt, level, -hp, openEnded=0, attackTrack=SQUIRT_TRACK), Func(suit.showHpString, 'SOAKED %i ROUNDS' % ToontownBattleGlobals.AvSoakRounds[level], openEnded=0))
        value = hp
        #if kbbonus > 0:
            #value += kbbonus
        #if hpbonus > 0:
            #value += hpbonus
        updateHealthBar = Func(suit.updateHealthBar, value)
        soakSuit = Func(suit.makeSoaked)
        suitTrack.append(Wait(tContact))
        suitTrack.append(__soakSuit(suit, tContact))
        suitIndex = battle.activeSuits.index(suit)
        soakTracks.append(Wait(tContact))
        if toon.getTrackBonusLevel(SQUIRT_TRACK) > 1:
            soakTracks.append(__soakNearby(suit, suitIndex + 1, battle.activeSuits, tContact, hp, died, battle, level))
            soakTracks.append(__soakNearby2(suit, suitIndex - 1, battle.activeSuits, tContact, hp, died, battle, level))
        else:
            soakTracks.append(__soakNearby3(suit, suitIndex + 1, battle.activeSuits, tContact, hp, died, battle, level))
            soakTracks.append(__soakNearby4(suit, suitIndex - 1, battle.activeSuits, tContact, hp, died, battle, level))
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
        if revived != 0 and suit.isSkeleton:
            suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
        if revived != 0 and not suit.isSkeleton:
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
        if died != 0 and suit.isVirtual:
            suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        if died != 0 and not suit.isVirtual:
            suitTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(suit.setChatAbsolute,
                 '',
                 CFSpeech | CFTimeout))
        suitTrack.append(__ScapegoatAbsorb(suitIndex - 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex + 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex - 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex + 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex - 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex + 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex - 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex + 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex - 5, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb(suitIndex + 5, battle.activeSuits, hp, battle))
        return Parallel(suitTrack, bonusTrack, soakTracks)
    else:
        return MovieUtil.createSuitDodgeMultitrack(tDodge, suit, leftSuits, rightSuits)


def say(statement):
    print statement

def __ScapegoatAbsorb(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding and not suits[suitIndex].dna.name == 'dsf':
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.425), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(value * 0.425))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'), MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        if suits[suitIndex].isVirtual and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHP, battle))
        return suitTrack
    elif len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding:
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
        if suits[suitIndex].isVirtual and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHP, battle))
        return suitTrack
    else:
        return Sequence()

def __ScapegoatAbsorbSplash(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding and not suits[suitIndex].dna.name == 'dsf':
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.425), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(hp * 0.425))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'), MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        if suits[suitIndex].isVirtual and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHP, battle))
        return suitTrack
    elif len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding:
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.115), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(hp * 0.115))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'),
                                  MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        if suits[suitIndex].isVirtual and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHP, battle))
        return suitTrack
    else:
        return Sequence()

def __soakNearby(suit, suitIndex, suits, tContact, hp, died, battle, level=0):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal:
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        value = (hp / 2)
        showDamage = Sequence(Func(suits[suitIndex].showHpTextSquirt, level, -(hp / 2), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, 'SOAKED %i ROUNDS' % ToontownBattleGlobals.AvSoakRounds[level], openEnded=0))
        soakSuit = Func(suits[suitIndex].makeSoaked)
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, value)
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'squirt-small-react'), __soakSuit(suits[suitIndex], tContact)))
        suitTrack.append(soakSuit)
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        if suits[suitIndex].isVirtual and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHP, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 1, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 1, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 2, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 2, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 3, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 3, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 4, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 4, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 5, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 5, battle.activeSuits, value, battle))
        return suitTrack
    else:
        return Sequence()

def __soakNearby2(suit, suitIndex, suits, tContact, hp, died, battle, level=0):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal:
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        value = (hp / 2)
        showDamage = Sequence(Func(suits[suitIndex].showHpTextSquirt, level, -(hp / 2), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, 'SOAKED %i ROUNDS' % ToontownBattleGlobals.AvSoakRounds[level], openEnded=0))
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, value)
        soakSuit = Func(suits[suitIndex].makeSoaked)
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'squirt-small-react'), __soakSuit(suits[suitIndex], tContact)))
        suitTrack.append(soakSuit)
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        if suits[suitIndex].isVirtual and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHP, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 1, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 1, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 2, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 2, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 3, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 3, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 4, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 4, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 5, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 5, battle.activeSuits, value, battle))
        return suitTrack
    else:
        return Sequence()

def __soakNearby3(suit, suitIndex, suits, tContact, hp, died, battle, level=0):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal:
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        value = (hp / 4)
        showDamage = Sequence(Func(suits[suitIndex].showHpTextSquirt, level, -(hp / 4), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, 'SOAKED %i ROUNDS' % ToontownBattleGlobals.AvSoakRounds[level], openEnded=0))
        soakSuit = Func(suits[suitIndex].makeSoaked)
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, value)
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'squirt-small-react'), __soakSuit(suits[suitIndex], tContact)))
        suitTrack.append(soakSuit)
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        if suits[suitIndex].isVirtual and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHP, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 1, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 1, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 2, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 2, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 3, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 3, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 4, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 4, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 5, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 5, battle.activeSuits, value, battle))
        return suitTrack
    else:
        return Sequence()

def __soakNearby4(suit, suitIndex, suits, tContact, hp, died, battle, level=0):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal:
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        value = (hp / 4)
        showDamage = Sequence(Func(suits[suitIndex].showHpTextSquirt, level, -(hp / 4), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, 'SOAKED %i ROUNDS' % ToontownBattleGlobals.AvSoakRounds[level], openEnded=0))
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, value)
        soakSuit = Func(suits[suitIndex].makeSoaked)
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'squirt-small-react'), __soakSuit(suits[suitIndex], tContact)))
        suitTrack.append(soakSuit)
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        if suits[suitIndex].isVirtual and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHP, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 1, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 1, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 2, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 2, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 3, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 3, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 4, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 4, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex - 5, battle.activeSuits, value, battle))
        suitTrack.append(__ScapegoatAbsorbSplash(suitIndex + 5, battle.activeSuits, value, battle))
        return suitTrack
    else:
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
    suit.showHpTextWhite("SOAKED %i ROUNDS" % ToontownBattleGlobals.AvSoakRounds[level])

def __soakSuit(suit, tContact, remove=0):
    if remove:
        color = Point4(1.0, 1.0, 1.0)
    else:
        color = SoakColor
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit.find('**/body'), suit.find('**/hands')]
    suitInterval = Sequence()
    if suit.style.name == 'lit' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeWetLitigator))
    for bodyPart in suitBody:
        if bodyPart:
            suitInterval.append(Func(bodyPart.setColor, color))
        return suitInterval

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

def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
    if poseExtraArgs:
        propTrack.append(Func(prop.pose, *poseExtraArgs))
    propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale))
    return propTrack

def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    if not target:
        target = attack['target']
    toon = attack['toon']
    battle = attack['battle']
    suit = target['suit']
    suitPos = suit.getPos(battle)
    animTrack = Sequence()
    animTrack.append(Func(toon.headsUp, battle, suitPos))
    indicatorTrack = Sequence(Wait(dodgeDelay + showMissedExtraTime))
    return Parallel(animTrack, indicatorTrack)

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

def getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    toonTrack = Sequence()
    toonTrack.append(Wait(delay))
    suitResponseTrack = Sequence()
    if damageAnimNames:
        for d in damageAnimNames:
            toonTrack.append(ActorInterval(toon, d))

        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
    else:
        splicedAnims = getSplicedAnimsTrack(splicedDamageAnims, actor=toon)
        toonTrack.append(splicedAnims)
        indicatorTrack = Sequence(Wait(delay + showDamageExtraTime), Func(__doDamage, toon, dmg, died))
    soundTrack = base.loader.loadSfx('phase_4/audio/sfx/laff_loss.ogg')
    toonTrack.append(Func(toon.loop, 'neutral'))
    if died:
        suit = attack['suit']
        toonTrack.append(Wait(3.0))
        if suit.getStyleName() in OTPLocalizerEnglish.SuitDefeatTaunts:
            suitResponseTrack.append(Parallel(Sequence(Wait(3.0), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTaunts[suit.getStyleName()]), CFSpeech | CFTimeout))))
        else:
            suitResponseTrack.append(Parallel(Sequence(Wait(3.0), Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitDefeatTauntsNone), CFSpeech | CFTimeout))))
    return Parallel(toonTrack, indicatorTrack, suitResponseTrack, soundTrack)

def doSnapBellow(attack):
    battle = attack['battle']
    target = attack['target']
    suit = target['suit']
    toon = attack['toon']
    dmg = target['hp']
    pbpText = attack['playByPlayText']
    pbpDc = PlayByPlayText.PlayByPlayText()

    pbpDesc = pbpDc.getShowIntervalDesc('The Litigator retaliates when soaked!', 3.5)
    pbpTrack = pbpText.getShowIntervalCheat('Snap!', 3.5)
    teeth = globalPropPool.getProp('litigator-teeth')
    propDelay = 0.8
    propScaleUpTime = 0.5
    suitDelay = 1.13
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.4
    posPoints = [Point3(-0.05, 0.41, -0.54), VBase3(4.465, -3.563, 51.479)]
    teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3),
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
        animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=3.6))
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
    toonTrack = Sequence(Wait(3.4), Func(toon.play, 'cringe'), ActorInterval(toon, 'spit', startTime=2.95))
    soundEffect = globalBattleSoundCache.getSound('SA_chomp.ogg')
    soundTrack = Sequence()
    soundTrack.append(Wait(2))
    soundTrack.append(SoundInterval(soundEffect, node=suit))
    notifyTrack = Sequence(Wait(6), Func(toon.showHpTextWhite, "VULNERABLE!", 10))
    speechTrack = Sequence(Func(suit.setChatAbsolute, random.choice(('These chompers can cut out diamonds!', "My colleagues don't like it when I get snappy.", 'This may hurt a little, but what comes next will hurt a lot.', "I've had enough with you!")), CFSpeech | CFTimeout))
    suitTrack = Sequence(ActorInterval(suit, 'throw-object', playRate=1.25))
    return Parallel(suitTrack, toonTrack, propTrack, pbpTrack, pbpDesc, notifyTrack, soundTrack, speechTrack)


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
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle, suitPos), ActorInterval(toon, 'pushbutton'), Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
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
        missDict = {}
        suitPoint = MovieThrow.__suitMissPoint(suit, other=battle)
        balloonTrack.append(Func(MovieThrow.__piePreMiss, missDict, balloon, suitPoint, battle))
        balloonTrack.append(LerpFunctionInterval(__pieMissLerpCallback, extraArgs=[missDict],
                                                 duration=(tContact - tLaunch) * ratioMissToHit))
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
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle, suitPos), ActorInterval(toon, 'pushbutton'), Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
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
    origHpr = toon.getHpr(battle)
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle), ActorInterval(toon, 'pushbutton'), Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
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
    scaleUpPoint = Point3(1.8, 1.8, 1.8)
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