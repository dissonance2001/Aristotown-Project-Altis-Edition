from direct.interval.IntervalGlobal import *
from direct.showutil import Effects

from toontown.clashbattle.battle.BattleProps import *
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum
from toontown.clashbattle.battle.movielistener.BattleMovieListenerEnum import BMLE
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.toon.ToonDNA import *
from toontown.clashbattle.battle.BattleSounds import *
from toontown.clashbattle.battle import MovieUtil, SpecialSuitDeaths
from otp import *
from panda3d.core import Point3
from toontown.clashbattle.battle import BattleGlobals
from toontown.clashbattle.battle import BattleProps
from toontown.clashbattle.battle import BattleBase
import random
from toontown.toonbase import TTLocalizer
from toontown.utils.DirectNotifyCategory import getNotify

notify = getNotify('MovieLures')
TIME_TO_WALK_BACK = 0.5
QUICK_DEATH_TRAP = ('quicksand', 'trapdoor', 'xspot', 'tnt')


def safeWrtReparentTo(nodePath, parent):
    if nodePath and not nodePath.isEmpty():
        nodePath.wrtReparentTo(parent)


def doLures(lures):
    if len(lures) == 0:
        return (None, None)

    # Set up dictionary to keep track of what targets have been prestige lured.
    targetsPrestige = {suit.doId: False for suit in lures[0]['battle'].activeSuits}
    targetsImmune = {suit.doId: False for suit in lures[0]['battle'].activeSuits}

    mtrack = Parallel()
    for lure in lures:
        toon = lure["avatar"]
        level = lure['level']
        sidestep = lure['sidestep']
        target = lure['target']

        # Populate a dict containing each suit that is prestige lured
        if toon.getTrackBonusLevel(AttackEnum.TOON_LURE) >= 1 and sidestep == 0:
            if BattleBase.attackAffectsGroup(AttackEnum.TOON_LURE, level):
                for t in target:
                    targetsPrestige[t['suit'].doId] = True
            else:
                targetsPrestige[target['suit'].doId] = True

        # Populate a dict containing each suit that is immune
        if BattleBase.attackAffectsGroup(AttackEnum.TOON_LURE, level):
            for t in target:
                if t['kbbonus'] == -2:
                    targetsImmune[t['suit'].doId] = True
        else:
            if target['kbbonus'] == -2:
                targetsImmune[target['suit'].doId] = True

        ival = __doLureLevel(lure, targetsPrestige, targetsImmune)
        if ival:
            mtrack.append(ival)

    camDuration = mtrack.getDuration()
    # chooseLureShot was deprecated as it was a duplicate of chooseTrapShot
    camTrack = lures[0]['battle'].camera.chooseTrapShot(camDuration)
    return (mtrack, camTrack)


def __doLureLevel(lure, presTargets, immuneTargets):
    level = lure['level']
    return lurefn_array[level](lure, presTargets, immuneTargets)


def getSoundTrack(fileName, delay = 0.01, duration = None, node = None):
    soundEffect = globalBattleSoundCache.getSound(fileName)
    if duration:
        return Sequence(Wait(delay), SoundInterval(soundEffect, duration=duration, node=node))
    else:
        return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))


def __createFishingPoleMultiTrack(lure, dollar, dollarName, prestigeTargets, immuneTargets):
    toon = lure["avatar"]
    target = lure['target']
    battle = lure['battle']
    level = lure['level']
    sidestep = lure['sidestep']
    hp = target['hp']
    kbbonus = target['kbbonus']
    suit = target['suit']
    targetPos = suit.getPos(battle)
    died = target['died']
    revived = target['revived']
    reachAnimDuration = 85/24
    trapProp = suit.battleTrapProp
    pole = globalPropPool.getProp('fishing-pole')
    poles = [pole]
    hands = toon.getRightHands()
    prestige = prestigeTargets[suit.doId]
    immune = immuneTargets[suit.doId]

    def positionDollar(dollar, suit):
        dollar.reparentTo(suit)
        dollar.setPos(0, MovieUtil.SUIT_LURE_DOLLAR_DISTANCE, 0)

    dollarTrack = Sequence(
        Func(positionDollar, dollar, suit),
        Func(dollar.wrtReparentTo, battle),
        ActorInterval(dollar, dollarName, duration=3),
        getSplicedLerpAnimsTrack(dollar, dollarName, 0.7, 2.0, startTime=3),
        LerpPosInterval(dollar, 0.2, Point3(0, -10, 7)),
        Func(MovieUtil.removeProp, dollar)
    )
    poleTrack = Sequence(
        Func(MovieUtil.showProps, poles, hands),
        ActorInterval(pole, 'fishing-pole'),
        Func(MovieUtil.removeProps, poles)
    )
    toonTrack = Sequence(
        Func(toon.headsUp, battle, targetPos),
        ActorInterval(toon, 'battlecast'),
        Func(toon.loop, 'neutral')
    )
    tracks = Parallel(dollarTrack, poleTrack, toonTrack)
    if sidestep == 0:
        if immune:
            suitTrack = Sequence()
            suitTrack.append(Func(suit.loop, 'neutral'))
            suitTrack.append(Wait(3.5))
            suitTrack.append(Func(suit.showHpText, 0, 0, openEnded=0, attackTrack=AttackEnum.TOON_LURE, rounds=-2))
            tracks.append(suitTrack)
        elif kbbonus != -1:
            suitTrack = Sequence()
            suitTrack.append(Func(suit.loop, 'neutral'))
            suitTrack.append(Wait(3.5))
            suitPos, suitHpr = battle.getActiveSuitPosHpr(suit, overrideLureStatus=True)
            moveTrack = lerpSuit(suit, 0.0, reachAnimDuration / 2.15, suitPos, battle, trapProp, blendType='easeInOut')
            reachTrack = ActorInterval(suit, 'reach-bill', duration=reachAnimDuration)
            suitTrack.append(Func(suit.showHpText, 0, 0, openEnded=0, attackTrack=AttackEnum.TOON_LURE, rounds=kbbonus))
            suitTrack.append(Parallel(moveTrack, reachTrack))
            if trapProp:
                suitTrack.append(Func(safeWrtReparentTo, trapProp, battle))
            if trapProp:
                suitTrack.append(Func(safeWrtReparentTo, trapProp, suit))
                suit.battleTrapProp = trapProp
            suitTrack.append(MovieUtil.lureSuit(suit))
            suitTrack.append(Func(suit.loop, 'neutral'))
            if prestige:
                suitTrack.append(MovieUtil.createSuitStunInterval(suit, before=0, after=0, cleanup=0, headAnim=0))
            if kbbonus == -3:
                suitTrack.append(__createSuitDamageTrack(battle, target, hp, lure, trapProp, prestige))
            if revived != 0:
                suitTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
            if died != 0:
                if (trapProp.getName() not in QUICK_DEATH_TRAP) or MovieUtil.shouldOverrideSuitDeath(suit):
                    suitTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
            tracks.append(suitTrack)
    else:
        tracks.append(Sequence(Wait(3.5), Parallel(
            Func(MovieUtil.indicateMissed, suit),
            MovieUtil.createSuitTeaseMultiTrack(suit)
        )))
    tracks.append(getSoundTrack('TL_fishing_pole.ogg', delay=0.5, node=toon))
    return tracks


def __createMagnetMultiTrack(lure, magnet, pos, hpr, scale, prestigeTargets, immuneTargets, isSmallMagnet = 1):
    toon = lure["avatar"]
    battle = lure['battle']
    level = lure['level']
    sidestep = lure['sidestep']
    targets = lure['target']
    tracks = Parallel()
    tracks.append(Sequence(ActorInterval(toon, 'hold-magnet'), Func(toon.loop, 'neutral')))
    hands = toon.getLeftHands()
    magnets = [magnet]

    def toggleLightning(mag, forceOff=False):
        lightning = mag.find('**/lightning')
        if lightning.isHidden() and not forceOff:
            lightning.show()
            yScale = 1 + (random.randint(-2, 8) / 10.0)
            girthScale = 1 + (random.randint(-2, 2) / 10.0)
            lightning.setScale(girthScale, yScale, girthScale)
        else:
            lightning.hide()

    for mag in magnets:
        toggleLightning(mag) # Start out the lightning as hidden

    def createLightningTrack(magnets):
        lightningTrack = Sequence()
        initMagTrack = Parallel()
        for mag in magnets:
            initMagTrack.append(Func(toggleLightning, mag))
        lightningTrack.append(Wait(1.8))
        lightningTrack.append(initMagTrack)
        totalTime = 3.2 * 100
        while totalTime > 0:
            flickerTime = random.randint(6, 9) # Choose a random time from 0.06-0.18 seconds
            if flickerTime > totalTime:
                flickerTime = totalTime
            magnetParallel = Parallel()
            for mag in magnets:
                magnetParallel.append(Func(toggleLightning, mag))
            lightningTrack.append(Sequence(magnetParallel, Wait(flickerTime / 100.0)))
            totalTime -= flickerTime
        for mag in magnets:
            lightningTrack.append(Func(toggleLightning, mag, True))
        retTrack = lightningTrack
        return retTrack

    lightningTrack = createLightningTrack(magnets)
    magnetTrack = Sequence(Wait(0.7), Func(MovieUtil.showProps, magnets, hands, pos, hpr, scale), lightningTrack, Wait(1.3), Func(MovieUtil.removeProps, magnets))
    tracks.append(magnetTrack)
    for target in targets:
        suit = target['suit']
        prestige = prestigeTargets[suit.doId]
        immune = immuneTargets[suit.doId]
        trapProp = suit.battleTrapProp
        suitDelay = 2.6
        if sidestep == 0:
            hp = target['hp']
            kbbonus = target['kbbonus']
            died = target['died']
            revived = target['revived']
            if immune:
                suitTrack = Sequence()
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(suit.showHpText, 0, 0, openEnded=0, attackTrack=AttackEnum.TOON_LURE, rounds=-2))
                tracks.append(suitTrack)
            elif kbbonus != -1:
                suitMoveDuration = 0.8
                suitTrack = Sequence()
                opos, ohpr = battle.getActorPosHpr(suit)
                reachDist = MovieUtil.SUIT_LURE_DISTANCE
                reachPos = Point3(opos[0], opos[1] - reachDist, opos[2])
                numShakes = 3
                shakeTotalDuration = 0.8
                shakeDuration = shakeTotalDuration / float(numShakes)
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(suit.showHpText, 0, 0, openEnded=0, attackTrack=AttackEnum.TOON_LURE, rounds=kbbonus))
                suitTrack.append(ActorInterval(suit, 'magnet', startTime=2.37, endTime=1.82))
                for i in range(0, numShakes):
                    suitTrack.append(ActorInterval(suit, 'magnet', startTime=1.82, endTime=1.16, duration=shakeDuration))

                suitTrack.append(ActorInterval(suit, 'magnet', startTime=1.16, endTime=0.7))
                suitTrack.append(ActorInterval(suit, 'magnet', startTime=0.7, duration=1.3))
                suitTrack.append(MovieUtil.lureSuit(suit))
                suitTrack.append(Func(suit.loop, 'neutral'))
                if prestige:
                    suitTrack.append(MovieUtil.createSuitStunInterval(suit, before=0, after=0, cleanup=0, headAnim=0))
                if kbbonus == -3:
                    suitTrack.append(__createSuitDamageTrack(battle, target, hp, lure, trapProp, prestige))
                if revived != 0:
                    suitTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
                elif died != 0:
                    if (trapProp.getName() not in QUICK_DEATH_TRAP) or MovieUtil.shouldOverrideSuitDeath(suit):
                        suitTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
                tracks.append(suitTrack)
                tracks.append(lerpSuit(suit, suitDelay + 0.55 + shakeTotalDuration, suitMoveDuration, reachPos, battle, trapProp))
        else:
            tracks.append(Sequence(Wait(2.6), Parallel(
                Func(MovieUtil.indicateMissed, suit),
                MovieUtil.createSuitTeaseMultiTrack(suit)
            )))

    if isSmallMagnet == 1:
        tracks.append(getSoundTrack('TL_small_magnet.ogg', delay=0.7, node=toon))
    else:
        tracks.append(getSoundTrack('TL_large_magnet.ogg', delay=0.7, node=toon))
    return tracks


def __createHypnoGogglesMultiTrack(lure, prestigeTargets, immuneTargets):
    toon = lure["avatar"]
    targets = lure['target']
    battle = lure['battle']
    level = lure['level']
    sidestep = lure['sidestep']
    goggles = globalPropPool.getProp('hypno-goggles')
    bothGoggles = [goggles]
    pos = Point3(-1.03, 1.04, -0.3)
    hpr = Point3(-96.55, 36.14, -170.59)
    scale = Point3(1.5, 1.5, 1.5)
    hands = toon.getLeftHands()
    gogglesTrack = Sequence(
        Wait(0.6),
        Func(MovieUtil.showProps, bothGoggles, hands, pos, hpr, scale),
        ActorInterval(goggles, 'hypno-goggles', duration=2.55),
        Func(MovieUtil.removeProps, bothGoggles)
    )
    toonTrack = Sequence(ActorInterval(toon, 'hypnotize'), Func(toon.loop, 'neutral'))
    tracks = Parallel(gogglesTrack, toonTrack)
    for target in targets:
        suit = target['suit']
        prestige = prestigeTargets[suit.doId]
        immune = immuneTargets[suit.doId]
        trapProp = suit.battleTrapProp
        if sidestep == 0:
            hp = target['hp']
            kbbonus = target['kbbonus']
            died = target['died']
            revived = target['revived']
            suitDelay = 1.6
            if immune:
                suitTrack = Sequence()
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(suit.showHpText, 0, 0, openEnded=0, attackTrack=AttackEnum.TOON_LURE, rounds=-2))
                tracks.append(suitTrack)
            elif kbbonus != -1:
                suitTrack = Sequence()
                suitAnimDuration = 1.5
                opos, ohpr = battle.getActorPosHpr(suit)
                reachDist = MovieUtil.SUIT_LURE_DISTANCE
                reachPos = Point3(opos[0], opos[1] - reachDist, opos[2])
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(suit.showHpText, 0, 0, openEnded=0, attackTrack=AttackEnum.TOON_LURE, rounds=kbbonus))
                suitTrack.append(ActorInterval(suit, 'hypnotized', duration=83/24))
                suitTrack.append(Func(suit.setPos, battle, reachPos))
                suitTrack.append(MovieUtil.lureSuit(suit))
                suitTrack.append(Func(suit.loop, 'neutral'))
                if prestige:
                    suitTrack.append(MovieUtil.createSuitStunInterval(suit, before=0, after=0, cleanup=0, headAnim=0))
                if kbbonus == -3:
                    suitTrack.append(__createSuitDamageTrack(battle, target, hp, lure, trapProp, prestige))
                if revived != 0:
                    suitTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
                elif died != 0:
                    if trapProp:
                        if (trapProp.getName() not in QUICK_DEATH_TRAP) or MovieUtil.shouldOverrideSuitDeath(suit):
                            suitTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
                tracks.append(suitTrack)
                tracks.append(lerpSuit(suit, suitDelay + 1.7, 0.7, reachPos, battle, trapProp))
        else:
            tracks.append(Sequence(Wait(1.2), Parallel(
                Func(MovieUtil.indicateMissed, suit, 1.1),
                MovieUtil.createSuitTeaseMultiTrack(suit)
            )))

    tracks.append(getSoundTrack('TL_hypnotize.ogg', delay=0.5, node=toon))
    return tracks


def __lureOneDollar(lure, prestigeTargets, immuneTargets):
    dollarProp = '1dollar'
    dollar = globalPropPool.getProp(dollarProp)
    return __createFishingPoleMultiTrack(lure, dollar, dollarProp, prestigeTargets, immuneTargets)


def __lureSmallMagnet(lure, prestigeTargets, immuneTargets):
    magnet = globalPropPool.getProp('small-magnet')
    pos = Point3(-0.27, 0.19, 0.29)
    hpr = Point3(-90.0, 84.17, -180.0)
    scale = Point3(0.85, 0.85, 0.85)
    return __createMagnetMultiTrack(lure, magnet, pos, hpr, scale, prestigeTargets, immuneTargets, isSmallMagnet=1)


def __lureFiveDollar(lure, prestigeTargets, immuneTargets):
    dollarProp = '5dollar'
    dollar = globalPropPool.getProp(dollarProp)
    return __createFishingPoleMultiTrack(lure, dollar, dollarProp, prestigeTargets, immuneTargets)


def __lureLargeMagnet(lure, prestigeTargets, immuneTargets):
    magnet = globalPropPool.getProp('big-magnet')
    pos = Point3(-0.27, 0.08, 0.29)
    hpr = Point3(-90.0, 84.17, -180)
    scale = Point3(1.32, 1.32, 1.32)
    return __createMagnetMultiTrack(lure, magnet, pos, hpr, scale, prestigeTargets, immuneTargets, isSmallMagnet=0)


def __lureTenDollar(lure, prestigeTargets, immuneTargets):
    dollarProp = '10dollar'
    dollar = globalPropPool.getProp(dollarProp)
    return __createFishingPoleMultiTrack(lure, dollar, dollarProp, prestigeTargets, immuneTargets)


def __lureHypnotize(lure, prestigeTargets, immuneTargets):
    return __createHypnoGogglesMultiTrack(lure, prestigeTargets, immuneTargets)


def __lureFiftyDollar(lure, prestigeTargets, immuneTargets):
    dollarProp = '50dollar'
    dollar = globalPropPool.getProp(dollarProp)
    return __createFishingPoleMultiTrack(lure, dollar, dollarProp, prestigeTargets, immuneTargets)


def __lureSlideshow(lure, prestigeTargets, immuneTargets):
    return __createSlideshowMultiTrack(lure, prestigeTargets, immuneTargets)


lurefn_array = (
    __lureOneDollar,
    __lureSmallMagnet,
    __lureFiveDollar,
    __lureLargeMagnet,
    __lureTenDollar,
    __lureHypnotize,
    __lureFiftyDollar,
    __lureSlideshow
)


def __createSuitDamageTrack(battle, target, hp, lure, trapProp, prestige):
    suit = target['suit']
    if (trapProp is None) or trapProp.isEmpty():
        returnval = Sequence(Func(suit.loop, 'neutral'))
        if prestige and not suit.stunStars:
            returnval.append(MovieUtil.createSuitStunInterval(suit, before=0, after=0, cleanup=0, headAnim=0))
        return returnval

    trapProp.wrtReparentTo(battle)
    trapTrack = AttackEnum.TOON_TRAP
    trapLevel = suit.battleTrap
    trapTrackNames = BattleGlobals.AvProps[trapTrack]
    trapName = trapTrackNames[trapLevel]
    result = Sequence()
    canQuickKill = target['died'] and not MovieUtil.shouldOverrideSuitDeath(suit)

    def reparentTrap(trapProp = trapProp, battle = battle):
        if trapProp and not trapProp.isEmpty():
            trapProp.wrtReparentTo(battle)

    result.append(Func(reparentTrap))

    parent = battle
    if suit.battleTrapIsFresh == 1:
        if trapName in ('quicksand', 'trapdoor', 'spring', 'xspot'):
            trapProp.hide()
            trapProp.reparentTo(battle)
            suitPos, _ = battle.getSuitBattlePosHpr(suit, battle.activeSuits)
            suitPos[1] = suitPos[1] - MovieUtil.SUIT_TRAP_DISTANCE
            trapProp.setPos(suitPos)
            trapProp.setHpr(Point3(0, 0, 0))
        elif trapName == 'rake':
            trapProp.hide()
            trapProp.reparentTo(suit)
            trapProp.setPos(0, MovieUtil.SUIT_TRAP_RAKE_DISTANCE, 0)
            trapProp.setHpr(Point3(0, 270, 0))
            trapProp.setScale(Point3(0.7, 0.7, 0.7))
            rakeOffset = MovieUtil.getSuitRakeOffset(suit)
            trapProp.setY(trapProp.getY() + rakeOffset)
        else:
            parent = render
    if trapName == 'banana':
        slidePos = trapProp.getPos(parent)
        slidePos.setY(slidePos.getY() - 5.1)
        moveTrack = Sequence(Wait(0.1), LerpPosInterval(trapProp, 0.1, slidePos, other=battle))
        animTrack = Sequence(ActorInterval(trapProp, 'banana', startTime=3.1), Wait(1.1), LerpScaleInterval(trapProp, 1, Point3(0.01, 0.01, 0.01)))
        suitTrack = ActorInterval(suit, 'slip-backward')
        extraText = '' if target['died'] else TTLocalizer.HpTextDazed
        damageTrack = Sequence(Wait(0.5), Func(suit.showHpText, hp, openEnded=0, extraText=extraText), Func(suit.updateHealthBar, hp))
        soundTrack = Sequence(
            SoundInterval(globalBattleSoundCache.getSound('AA_pie_throw_only.ogg'), node=suit),
            SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit)
        )
        result.append(Parallel(moveTrack, animTrack, suitTrack, damageTrack, soundTrack))
    elif trapName in ('rake', 'rake-react'):
        hpr = trapProp.getHpr(parent)
        upHpr = Vec3(hpr[0], 0, hpr[2])
        bounce1Hpr = Vec3(hpr[0], 10, hpr[2])
        bounce2Hpr = Vec3(hpr[0], 5, hpr[2])
        rakeTrack = Sequence(
            Wait(0.2),
            LerpHprInterval(trapProp, 0.05, upHpr, startHpr=hpr),
            Wait(0.1),
            LerpHprInterval(trapProp, 0.09, hpr, startHpr=upHpr),
            LerpHprInterval(trapProp, 0.09, bounce1Hpr, startHpr=hpr),
            LerpHprInterval(trapProp, 0.1, hpr, startHpr=bounce1Hpr),
            LerpHprInterval(trapProp, 0.1, bounce2Hpr, startHpr=hpr),
            LerpHprInterval(trapProp, 0.1, hpr, startHpr=bounce2Hpr),
            LerpHprInterval(trapProp, 0.11, hpr, startHpr=upHpr),
            LerpHprInterval(trapProp, 0.11, bounce1Hpr, startHpr=hpr),
            LerpHprInterval(trapProp, 0.12, hpr, startHpr=bounce1Hpr),
            LerpHprInterval(trapProp, 0.12, bounce2Hpr, startHpr=hpr),
            LerpHprInterval(trapProp, 0.2, hpr, startHpr=bounce2Hpr),
            Wait(0.2),
            LerpScaleInterval(trapProp, 0.2, Point3(0.01, 0.01, 0.01))
        )
        rakeAnimDuration = 3.125
        suitTrack = ActorInterval(suit, 'rake-react', duration=rakeAnimDuration)
        extraText = '' if target['died'] else TTLocalizer.HpTextDazed
        damageTrack = Sequence(Wait(0.5), Func(suit.showHpText, hp, openEnded=0, extraText=extraText), Func(suit.updateHealthBar, hp))
        soundTrack = getSoundTrack('TL_step_on_rake.ogg', delay=0.2, node=suit)
        result.append(Parallel(rakeTrack, suitTrack, damageTrack, soundTrack))
    elif trapName == 'spring':
        sinkPos = trapProp.getPos(battle)
        dropPos, _ = battle.getActorPosHpr(suit)
        landPos, _ = battle.getActorPosHpr(suit)
        sinkPos.setZ(sinkPos.getZ() + 15)
        dropPos.setZ(dropPos.getZ() + 15)
        trapTrack = Sequence(Wait(2.9), LerpPosInterval(trapProp, 0.3, Point3(trapProp.getX(), trapProp.getY(), -5), blendType='easeIn'))
        moveTrack = Sequence(Wait(2.2), LerpPosInterval(suit, 0.4, sinkPos, other=battle), Func(suit.setPos, battle, dropPos), Func(suit.wrtReparentTo, hidden))
        moveTrack.append(Sequence(Wait(1.1), Func(suit.wrtReparentTo, battle), LerpPosInterval(suit, 0.3, landPos, other=battle)))
        animTrack = Sequence(
            getSplicedLerpAnimsTrack(suit, 'flail', 0.7, 0.25),
            ActorInterval(suit, 'flail', startTime=0.7, endTime=0),
            ActorInterval(suit, 'lured', duration=0.5),
            Parallel(
                LerpPosInterval(trapProp, 0.1, Point3(trapProp.getX(), trapProp.getY(), 2), blendType = 'easeOut'),
                ActorInterval(suit, 'flail', startTime=1.1, duration=0.4)

            )
        )
        animTrack.append(Sequence(Wait(1.0), Func(suit.pose, 'slip-forward', 13), ActorInterval(suit, 'slip-forward')))
        extraText = '' if target['died'] else TTLocalizer.HpTextDazed
        damageTrack = Sequence(Wait(3.7), Func(suit.showHpText, hp, openEnded=0, extraText=extraText), Func(suit.updateHealthBar, hp))
        soundTrack = Sequence(Wait(2.2), SoundInterval(globalBattleSoundCache.getSound('AA_spring_activate.ogg'), node=suit), Wait(0.45))
        soundTrack.append(SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        result.append(Parallel(trapTrack, moveTrack, animTrack, damageTrack, soundTrack))
    elif trapName == 'marbles':
        slidePos = trapProp.getPos(parent)
        slidePos.setY(slidePos.getY() - 6.5)
        moveTrack = Sequence(Wait(0.1), LerpPosInterval(trapProp, 0.8, slidePos, other=battle), Wait(1.1), LerpScaleInterval(trapProp, 1, Point3(0.01, 0.01, 0.01)))
        animTrack = ActorInterval(trapProp, 'marbles', startTime=3.1)
        suitTrack = ActorInterval(suit, 'slip-backward')
        extraText = '' if target['died'] else TTLocalizer.HpTextDazed
        damageTrack = Sequence(Wait(0.5), Func(suit.showHpText, hp, openEnded=0, extraText=extraText), Func(suit.updateHealthBar, hp))
        soundTrack = Sequence(
            SoundInterval(globalBattleSoundCache.getSound('AA_pie_throw_only.ogg'), duration=0.55, node=suit),
            SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit)
        )
        result.append(Parallel(moveTrack, animTrack, suitTrack, damageTrack, soundTrack))
    elif trapName == 'quicksand':
        sinkPos1 = trapProp.getPos(battle)
        sinkPos2 = trapProp.getPos(battle)
        dropPos, _ = battle.getActorPosHpr(suit)
        landPos, _ = battle.getActorPosHpr(suit)
        sinkPos1.setZ(sinkPos1.getZ() - 3.1)
        sinkPos2.setZ(sinkPos2.getZ() - 9.1)
        dropPos.setZ(dropPos.getZ() + 15)
        startScale = Vec3(0.01, 0.01, 0.01)
        xBounce = Effects.createScaleXBounce(trapProp, 4, startScale, 0.6, 0.25)
        yBounce = Effects.createScaleYBounce(trapProp, 4, startScale, 0.6, 0.125)
        trapTrack = Sequence(Wait(2.4), Parallel(xBounce, yBounce))
        moveTrack = Sequence(
            Wait(0.9),
            LerpPosInterval(suit, 0.9, sinkPos1, other=battle),
            LerpPosInterval(suit, 0.4, sinkPos2, other=battle),
            Func(suit.setPos, battle, dropPos),
            Func(suit.wrtReparentTo, hidden)
        )
        if not canQuickKill:
            moveTrack.append(Sequence(Wait(1.1),
                                      Func(suit.wrtReparentTo, battle),
                                      LerpPosInterval(suit, 0.3, landPos, other=battle)))
        animTrack = Sequence(
            Parallel(
                ActorInterval(suit, 'flail-qs'),
                Sequence(
                    Wait(41/24),
                    LerpScaleInterval(suit, 0.45, 0.01))
            )
        )

        if canQuickKill:
            damageTrackParallelHolder = Parallel()
            battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, damageTrackParallelHolder, suit=suit)
            withinDmgTrack = Sequence()
            battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, withinDmgTrack, suit=suit)
            damageTrackParallelHolder.append(withinDmgTrack)
            damageTrack = Sequence(damageTrackParallelHolder)
        else:
            animTrack.append(Sequence(Wait(0.4), Func(suit.setScale, 1), Func(suit.pose, 'slip-forward', 13), Wait(0.5), ActorInterval(suit, 'slip-forward')))
            extraText = '' if target['died'] else TTLocalizer.HpTextDazed
            damageTrack = Sequence(Wait(3.7), Func(suit.showHpText, hp, openEnded=0, extraText=extraText), Func(suit.updateHealthBar, hp))
        soundTrack = Sequence(Wait(0.7), SoundInterval(globalBattleSoundCache.getSound('TL_quicksand.ogg'), node=suit), Wait(0.45))
        if not canQuickKill:
            soundTrack.append(SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        result.append(Parallel(trapTrack, moveTrack, animTrack, damageTrack, soundTrack))
    elif trapName == 'trapdoor':
        sinkPos = trapProp.getPos(battle)
        dropPos, _ = battle.getActorPosHpr(suit)
        landPos, _ = battle.getActorPosHpr(suit)
        sinkPos.setZ(sinkPos.getZ() - 9.1)
        dropPos.setZ(dropPos.getZ() + 15)
        startScale = Vec3(0.01, 0.01, 0.01)
        xBounce = Effects.createScaleXBounce(trapProp, 4, startScale, 0.6, 0.25)
        yBounce = Effects.createScaleYBounce(trapProp, 4, startScale, 0.6, 0.125)
        trapTrack = Sequence(Wait(2.4), Parallel(xBounce, yBounce))
        moveTrack = Sequence(Wait(2.2), LerpPosInterval(suit, 0.4, sinkPos, other=battle), Func(suit.setPos, battle, dropPos), Func(suit.wrtReparentTo, hidden))
        if not canQuickKill:
            moveTrack.append(Sequence(Wait(1.1), Func(suit.wrtReparentTo, battle), LerpPosInterval(suit, 0.3, landPos, other=battle)))
        animTrack = Sequence(
            getSplicedLerpAnimsTrack(suit, 'flail', 0.7, 0.25),
            Func(trapProp.setColor, Vec4(0, 0, 0, 1)),
            ActorInterval(suit, 'flail', startTime=0.6, endTime=0),
            ActorInterval(suit, 'flail', startTime=25/24, endTime=15/24),
            Parallel(
                ActorInterval(suit, 'flail', startTime=1.1),
                Sequence(
                    Wait(0.3),
                    LerpScaleInterval(suit, 0.45, 0.01)
                )
            )
        )

        if canQuickKill:
            damageTrackParallelHolder = Parallel()
            battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, damageTrackParallelHolder, suit=suit)
            withinDmgTrack = Sequence()
            battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, withinDmgTrack, suit=suit)
            damageTrackParallelHolder.append(withinDmgTrack)
            damageTrack = Sequence(damageTrackParallelHolder)
        else:
            animTrack.append(Sequence(Wait(0.4), Func(suit.setScale, 1), Func(suit.pose, 'slip-forward', 13), ActorInterval(suit, 'slip-forward')))
            extraText = '' if target['died'] else TTLocalizer.HpTextDazed
            damageTrack = Sequence(Wait(3.7), Func(suit.showHpText, hp, openEnded=0, extraText=extraText), Func(suit.updateHealthBar, hp))
        soundTrack = Sequence(Wait(0.8), SoundInterval(globalBattleSoundCache.getSound('TL_trap_door.ogg'), node=suit), Wait(0.45))

        if not canQuickKill:
            soundTrack.append(SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        result.append(Parallel(trapTrack, moveTrack, animTrack, damageTrack, soundTrack))
    elif trapName == 'xspot':
        sinkPos = trapProp.getPos(battle)
        dropPos, _ = battle.getActorPosHpr(suit)
        landPos, _ = battle.getActorPosHpr(suit)
        wreckingBall = globalPropPool.getProp('wreckingball')
        wreckingBall.reparentTo(battle)
        wreckingBall.hide()
        suitSize = suit.scale
        maxScale = 1.0
        minScale = 0.3
        scaleDiff = maxScale - minScale
        maxedOutScale = max(min(suitSize, maxScale), minScale) - minScale
        suitScaleRatio = maxedOutScale / scaleDiff
        ballScale = lerp(0.5, 1.0, suitScaleRatio)
        wreckingBall.setScale(ballScale)
        wreckingBall.setColorScale(1, 1, 1, 0)
        sinkPos = (sinkPos.getX(), (sinkPos.getY() + 12)*ballScale, (sinkPos.getZ() + 12)*ballScale)
        dropPos.setZ(dropPos.getZ() + 15)
        startScale = Vec3(0.01, 0.01, 0.01)
        xBounce = Effects.createScaleXBounce(trapProp, 4, startScale, 0.6, 0.25)
        yBounce = Effects.createScaleYBounce(trapProp, 4, startScale, 0.6, 0.125)
        trapTrack = Sequence(Wait(2.4), Parallel(xBounce, yBounce))
        suitDelay = 0.0
        angleBase = 60
        if suit.style.name == 'mm':
            suitDelay = 0.05

        suitPos, _ = battle.getSuitBattlePosHpr(suit, battle.activeSuits)

        wreckingTrack = Sequence(
            Wait(0.7),
            Func(wreckingBall.setPos, (suitPos[0], 0, 20.6 * ballScale)),
            Func(wreckingBall.show),
            LerpHprInterval(wreckingBall, 1, (0, angleBase, 0), startHpr = (0, -angleBase, 0)),
            Func(MovieUtil.removeProp, wreckingBall))
        colorBallTrack = Sequence(
            Wait(0.7 + suitDelay),
            LerpColorScaleInterval(wreckingBall, 0.2, (1, 1, 1, 1), blendType='easeInOut'),
            Wait(0.6),
            LerpColorScaleInterval(wreckingBall, 0.2, (1, 1, 1, 0), blendType='easeInOut')
        )
        if canQuickKill:
            hitSfx = globalBattleSoundCache.getSound(f'AA_trap_wreckingball_{suit.style.body.upper()}.ogg')
            animTrackParallelHolder = Parallel()
            battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, animTrackParallelHolder, suit=suit)
            animTrack = Sequence(
                Wait(0.7 + suitDelay),
                ActorInterval(suit, 'flail', startTime=1.1, endTime=1.52),
                ActorInterval(suit, 'wrecked')
            )
            animTrack.append(Func(suit.stash))
            battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, animTrack, suit=suit)
            animTrackParallelHolder.append(animTrack)

            soundTrack = Sequence(Wait(1.1 + suitDelay), SoundInterval(hitSfx, node=suit))
            result = Sequence(Parallel(trapTrack, wreckingTrack, animTrackParallelHolder, soundTrack, colorBallTrack))
            result.append(Func(battle.removeTrap, suit, True))
            result.append(MovieUtil.unlureSuit(suit, battle))
        else:
            hitSfx = globalBattleSoundCache.getSound('AA_trap_wreckingball_nonfatal.ogg')
            animTrack = Sequence(
                Wait(0.8),
                Parallel(
                    Sequence(
                        ActorInterval(suit, 'flail-wb', startTime=1.1),
                        Func(suit.pose, 'slip-forward', 13),
                        Wait(0.55),
                        ActorInterval(suit, 'slip-forward'),
                    ),
                    Sequence(
                        Wait(0.5),
                        Func(suit.setTransparency, 1),
                        LerpColorScaleInterval(suit, 0.3, (1, 1, 1, 0)),
                        Wait(1.0),
                        Func(suit.setColorScale, (1, 1, 1, 1)),
                        Func(suit.clearTransparency),
                    ),
                ),
            )
            moveTrack = Sequence(
                Wait(1.2),
                LerpPosInterval(suit, 0.4, sinkPos, other=battle),
                Func(suit.setPos, battle, dropPos),
                Func(suit.wrtReparentTo, hidden),
                Wait(1.1),
                Func(suit.wrtReparentTo, battle),
                LerpPosInterval(suit, 0.3, landPos, other=battle)
            )
            extraText = '' if target['died'] else TTLocalizer.HpTextDazed
            damageTrack = Sequence(
                Wait(3.05),
                Func(suit.showHpText, hp, openEnded=0, extraText=extraText),
                Func(suit.updateHealthBar, hp)
            )
            soundTrack = Sequence(
                Wait(1.1),
                SoundInterval(hitSfx, node=suit, duration=1.5),
                Wait(0.15),
                SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit)
            )
            result.append(Parallel(trapTrack, wreckingTrack, moveTrack, animTrack, damageTrack, soundTrack, colorBallTrack))

    elif trapName == 'tnt':
        tntTrack = ActorInterval(trapProp, 'tnt')
        explosionTrack = Sequence(Wait(2.3), createTNTExplosionTrack(battle, trapProp=trapProp, relativeTo=parent))
        origPos, _ = battle.getActorPosHpr(suit)
        flyPos = Point3(*origPos)
        flyPos.setZ(suit.getZ() + 4)

        # Cog looks down and up
        suitTrack = Sequence(ActorInterval(suit, 'lured', startTime=1 / 24, endTime=4 / 24))
        suitTrack.append(ActorInterval(suit, 'flail', startTime=1 / 24, endTime=9 / 24))
        suitTrack.append(ActorInterval(suit, 'flail', startTime=10 / 24, endTime=4 / 24))
        suitTrack.append(ActorInterval(suit, 'flail', startTime=4 / 24, endTime=43 / 24))

        if not canQuickKill:
            tntTrack = ActorInterval(trapProp, 'tnt')
            suitTrack.append(Sequence(
                Wait(0.1),
                Parallel(
                    LerpPosInterval(suit, 0.5, flyPos, other=battle, blendType='easeOut'),
                    ActorInterval(suit, 'slip-backward', duration=0.1),
                    Func(battle.movie.needRestoreColor),
                    Sequence(
                        Wait(0.1),
                        Func(suit.setColorScale, Vec4(0.2, 0.2, 0.2, 1)),
                        Func(trapProp.reparentTo, hidden),
                    ),
                ),
                Parallel(
                    LerpPosInterval(suit, 0.5, origPos, other=battle, blendType='easeIn'),
                    ActorInterval(suit, 'slip-backward', startTime=0.1)
                ),
                Func(suit.setColorScale, Vec4(1, 1, 1, 1)),
                Func(trapProp.sparksEffect.cleanup),
                Func(battle.movie.clearRestoreColor)
            ))
        else:
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            suitPos[1] -= MovieUtil.SUIT_TRAP_DISTANCE
            explosionPos = Point3(suitPos[0], suitPos[1], suitPos[2])
            explosionPos[2] = suitPos.getZ() + (suit.height / 2.0)
            explodeTrackParallelHolder = Parallel()
            battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, explodeTrackParallelHolder, suit=suit)
            tntExplodeTrack = Sequence(
                Func(battle.removeTrap, suit, True),
                Func(trapProp.sparksEffect.cleanup),
                Parallel(MovieUtil.createKapowExplosionTrack(battle, explosionPos),
                         Func(suit.setColorScale, 0.2, 0.2, 0.2, 1), Func(suit.pose, 'lose', 164)),
                Wait(1.5),
                ActorInterval(suit, 'lose', startFrame=164),
                Func(suit.hide),
            )
            battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, tntExplodeTrack, suit=suit)
            explodeTrackParallelHolder.append(tntExplodeTrack)
            suitTrack.append(explodeTrackParallelHolder)

        extraText = '' if target['died'] else TTLocalizer.HpTextDazed
        damageTrack = Sequence(Wait(2.3), Func(suit.showHpText, hp, openEnded=0, extraText=extraText), Func(suit.updateHealthBar, hp))
        explosionSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        soundTrack = Sequence(
            SoundInterval(globalBattleSoundCache.getSound('TL_dynamite.ogg'), duration=2.0, node=suit),
            SoundInterval(explosionSound, duration=0.6, node=suit)
        )
        result.append(Parallel(tntTrack, suitTrack, damageTrack, explosionTrack, soundTrack))
    else:
        notify.warning('unknown trapName: %s detected on suit: %s' % (trapName, suit))
    suit.battleTrapProp = trapProp
    if not (trapName == 'tnt' and target['died']):
        result.append(Func(battle.removeTrap, suit, True))
    result.append(MovieUtil.unlureSuit(suit, battle))
    if trapName not in ('spring', 'quicksand', 'trapdoor', 'xspot', 'tnt'):
        result.append(__createSuitResetPosTrack(suit, battle))
    result.append(Func(suit.loop, 'neutral'))
    if trapName == 'traintrack':
        result.append(Func(MovieUtil.removeProp, trapProp))
    return result


def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.loop, 'neutral'))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def createSuitResetPosTrack(suit, battle):
    return __createSuitResetPosTrack(suit, battle)


def createSuitGotoLurePosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.loop, 'neutral'))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def getSplicedLerpAnimsTrack(obj, animName, origDuration, newDuration, startTime = 0, fps = 30):
    track = Sequence()
    addition = 0
    numIvals = origDuration * fps
    timeInterval = newDuration / numIvals
    animInterval = origDuration / numIvals
    for i in range(0, int(numIvals)):
        track.append(Wait(timeInterval))
        track.append(ActorInterval(obj, animName, startTime=startTime + addition, duration=animInterval))
        addition += animInterval

    return track


def lerpSuit(suit, delay, duration, reachPos, battle, trapProp, blendType='noBlend'):
    track = Sequence()
    if trapProp:
        track.append(Func(safeWrtReparentTo, trapProp, battle))
    track.append(Wait(delay))
    track.append(LerpPosInterval(suit, duration, reachPos, other=battle, blendType=blendType))
    if trapProp:
        if trapProp.getName() == 'traintrack':
            notify.debug('UBERLURE MovieLure.lerpSuit deliberately not parenting trainTrack to suit')
        else:
            track.append(Func(safeWrtReparentTo, trapProp, suit))
        suit.battleTrapProp = trapProp
    return track


def createTNTExplosionTrack(parent, explosionPoint = None, trapProp = None, relativeTo = render):
    explosionTrack = Sequence()
    explosion = BattleProps.globalPropPool.getProp('kapow')
    explosion.setBillboardPointEye()
    if not explosionPoint:
        if trapProp:
            explosionPoint = trapProp.getPos(relativeTo)
            explosionPoint.setZ(explosionPoint.getZ() + 2.3)
        else:
            explosionPoint = Point3(0, 3.6, 2.1)
    explosionTrack.append(Func(explosion.reparentTo, parent))
    explosionTrack.append(Func(explosion.setPos, explosionPoint))
    explosionTrack.append(Func(explosion.setScale, 0.26))
    explosionTrack.append(ActorInterval(explosion, 'kapow'))
    explosionTrack.append(Func(MovieUtil.removeProp, explosion))
    return explosionTrack


def __createSlideshowMultiTrack(lure, prestigeTargets, immuneTargets):
    toon = lure["avatar"]
    battle = lure['battle']
    level = lure['level']
    lookStraight = toon.getPos(battle)
    lookStraight.setY(lookStraight.getY() + 7)
    origHpr = toon.getHpr(battle)
    sidestep = lure['sidestep']
    slideshowDelay = 2.5
    hands = toon.getLeftHands()
    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 4)
    button = globalPropPool.getProp('lure-button')
    buttons = [button]
    toonTrack = Sequence()
    moveTrack = Sequence()
    toonTrack.append(Func(MovieUtil.showProps, buttons, hands))
    toonTrack.append(Func(toon.headsUp, battle, endPos))
    toonTrack.append(Parallel(ActorInterval(button, 'lure-button'), ActorInterval(toon, 'pushbutton')))
    toonTrack.append(Func(MovieUtil.removeProps, buttons))
    toonTrack.append(Func(toon.loop, 'neutral'))
    toonTrack.append(Func(toon.setHpr, battle, origHpr))
    slideShowProp = globalPropPool.getProp('slideshow')
    propTrack = Sequence()
    propTrack.append(Wait(slideshowDelay))
    propTrack.append(Func(slideShowProp.show))
    propTrack.append(Func(slideShowProp.setScale, Point3(0.1, 0.1, 0.1)))
    propTrack.append(Func(slideShowProp.reparentTo, battle))
    propTrack.append(Func(slideShowProp.setPos, endPos))
    propTrack.append(LerpScaleInterval(slideShowProp, 1.2, Point3(1.0, 1.0, 1.0)))
    shrinkDuration = 0.4
    totalDuration = 7.1
    propTrackDurationAtThisPoint = propTrack.getDuration()
    waitTime = totalDuration - propTrackDurationAtThisPoint - shrinkDuration
    if waitTime > 0:
        propTrack.append(Wait(waitTime))
    propTrack.append(LerpScaleInterval(nodePath=slideShowProp, scale=Point3(1.0, 1.0, 0.1), duration=shrinkDuration))
    propTrack.append(Func(MovieUtil.removeProp, slideShowProp))
    tracks = Parallel(propTrack, toonTrack, moveTrack)
    targets = lure['target']
    for target in targets:
        suit = target['suit']
        prestige = prestigeTargets[suit.doId]
        immune = immuneTargets[suit.doId]
        trapProp = suit.battleTrapProp
        if sidestep == 0:
            hp = target['hp']
            kbbonus = target['kbbonus']
            died = target['died']
            revived = target['revived']
            suitDelay = 3.8
            if immune:
                suitTrack = Sequence()
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(suit.showHpText, 0, 0, openEnded=0, attackTrack=AttackEnum.TOON_LURE, rounds=-2))
                tracks.append(suitTrack)
            elif kbbonus != -1:
                suitTrack = Sequence()
                suitAnimDuration = 1.5
                opos, ohpr = battle.getActorPosHpr(suit)
                reachDist = MovieUtil.SUIT_LURE_DISTANCE
                reachPos = Point3(opos[0], opos[1] - reachDist, opos[2])
                suitTrack.append(Func(suit.loop, 'neutral'))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(suit.showHpText, 0, 0, openEnded=0, attackTrack=AttackEnum.TOON_LURE, rounds=kbbonus))
                suitTrack.append(ActorInterval(suit, 'hypnotized', duration=83/24))
                suitTrack.append(Func(suit.setPos, battle, reachPos))
                suitTrack.append(MovieUtil.lureSuit(suit))
                suitTrack.append(Func(suit.loop, 'neutral'))
                if prestige:
                    suitTrack.append(MovieUtil.createSuitStunInterval(suit, before=0, after=0, cleanup=0, headAnim=0))
                if kbbonus == -3:
                    suitTrack.append(__createSuitDamageTrack(battle, target, hp, lure, trapProp, prestige))
                if revived != 0:
                    suitTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
                elif died != 0:
                    if trapProp:
                        if (trapProp.getName() not in QUICK_DEATH_TRAP) or MovieUtil.shouldOverrideSuitDeath(suit):
                            suitTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
                tracks.append(suitTrack)
                tracks.append(lerpSuit(suit, suitDelay + 1.7, 0.7, reachPos, battle, trapProp))
        else:
            tracks.append(Sequence(Wait(3.3), Parallel(
                Func(MovieUtil.indicateMissed, suit, 1.1),
                MovieUtil.createSuitTeaseMultiTrack(suit)
            )))

    tracks.append(getSoundTrack('TL_presentation.ogg', delay=2.3, node=toon))
    tracks.append(getSoundTrack('AA_drop_trigger_box.ogg', delay=slideshowDelay, node=toon))
    return tracks
