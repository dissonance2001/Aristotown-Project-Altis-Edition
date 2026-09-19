import random
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.suit.SuitDNA import *
from toontown.battle import MovieUtil, SpecialSuitDeaths
from toontown.battle import BattleParticles
from toontown.battle import BattleGlobals
from collections import OrderedDict

notify = getNotify('MovieZap')
hitSoundFiles  = ('AA_buzzer.ogg', 'AA_zap_lightbulb_impact.ogg', 'AA_zap_radio.ogg', 'AA_battery.ogg', 'AA_zap_tv.ogg', 'AA_zap_stagelight_hit.ogg',  'AA_tesla.ogg', 'AA_lightning.ogg')
missSoundFiles = ('AA_buzzer.ogg', 'AA_zap_lightbulb_impact.ogg', 'AA_zap_radio.ogg', 'AA_battery.ogg', 'AA_zap_tv.ogg', 'AA_zap_stagelight_miss.ogg', 'AA_tesla.ogg', 'AA_lightning.ogg')
sprayScales = [
    0.2,   # Joybuzzer, no spray
    0.3,   # Lightbulb, no spray
    0.75,  # Radio
    0.3,   # Kart Battery, no spray
    1.0,   # TV
    1.0,   # Stagelight, no spray
    1.0,   # Tesla
    2.0    # Lightning, no spray
]
WaterSprayColor = Point4(1.0, 1.0, 0, 1.0)
zapPos = Point3(0, 0, 0)
zapHpr = Vec3(0, 0, 0)
TIME_TO_WALK_BACK = 0.5
ratioMissToHit = 1.5
tBalloonShrink = 0.7
tBalloonLeavesHand = 2.7
tBalloonHitsSuit = 3.0
pieFlyTaskName = 'MovieZap-pieFly'
perZapTypeDelays = [
    0.4,
    2.2,
    0.0,
    0.0,
    0.0,
    2.45,
    0.0,
    0.0,
]


def __hasLuredSuits(zap):
    retval = False
    for target in zap['target']:
        kbbonus = target['kbbonus']
        if kbbonus == 0:
            retval = True
            break
    return retval


def lightningPreColor():
    # This function is used to get the area's color scale immediately prior
    # to applying a lightning effect (Zap Lightning, Scope Creep, potentially more).
    # This is useful for avoiding bugs, such as when several lightning effects attempt to overlap.
    # TODO - Reset this colorscale attribute when changing zones, in case of more issues.
    if not hasattr(base, 'definedColorScale'):
        setattr(base, 'definedColorScale', render.getColorScale())
    return getattr(base, 'definedColorScale')


def lightningPostColor():
    # This resets the lightning applied in the above function.
    # Make sure to perform this at the end of a lightning sequence.
    if hasattr(base, 'definedColorScale'):
        delattr(base, 'definedColorScale')


def doZaps(zaps):
    if len(zaps) == 0:
        return (None, None)

    delay = 0.0

    mtrack = Parallel()
    for st in [zaps]:
        st = [s for s in st if (s['extraArgs'][0:1] or [0])[0]]
        if len(st) > 0:
            ival = __doSuitZaps(st)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay += TOON_ZAP_SUIT_DELAY
    camDuration = mtrack.getDuration()
    camTrack = zaps[0]['battle'].camera.chooseZapShot(camDuration)
    return (mtrack, camTrack)


def __doSuitZaps(zaps):
    toonTracks = Parallel()
    delay = 0.0

    # List of suit doIds that died
    suitsDied = []
    # Dict of suitId -> Last Zap gag used on them
    finalZap = {}
    # Dict of suitId -> First Zap gag used on them
    firstZap = {}
    for s in zaps:
        for target in s['target']:
            # Keep track of what suits have dodged from zap to determine
            # if we need to force a dodge from them later
            target['suit'].zapDodged = False
            suitId = target['suit'].doId
            if target['died'] and suitId not in suitsDied:
                suitsDied.append(suitId)
            finalZap[suitId] = s["avatar"].doId
            if suitId not in firstZap:
                firstZap[suitId] = s["avatar"].doId

    # Keep track of what the last zap level used was to determine
    # If and when we need to insert particular level-based delays.
    lastZapLevel = -1
    for s in zaps:
        if s['level'] > lastZapLevel:
            if lastZapLevel != -1:
                delay = delay + perZapTypeDelays[lastZapLevel]
            lastZapLevel = s['level']

        tracks = __doZap(s, delay, suitsDied, firstZap, finalZap)
        if tracks:
            for track in tracks:
                toonTracks.append(track)

        delay = delay + TOON_ZAP_DELAY

    return toonTracks


def __doZap(zap, delay, suitsDied=[], firstZap={}, finalZap={}):
    zapSequence = Sequence(Wait(delay))
    for target in zap['target']:
        notify.debug('toon: %s zaps prop: %d at suit: %d for hp: %d' % (zap["avatar"].getName(),
         zap['level'],
         target['suit'].doId,
         target['hp']))
    ival = zapfn_array[zap['level']](zap, delay, True, suitsDied=suitsDied, firstZap=firstZap, finalZap=finalZap)
    if ival:
        zapSequence.append(ival)
    return [zapSequence]


def __suitLightTargetPoint(suit, other=render, extraPos=None):
    foo = suit.attachNewNode('foo')
    foo.setZ(suit.getHeight() * 0.6)
    if suit.isSkeleton:
        offsets = {
            'a': 0.5,
            'b': 0.5,
            'c': 0.25,
        }
    else:
        offsets = {
            'a': 1.275,
            'b': 1.3,
            'c': 1.65
        }
    offset = offsets[suit.style.body] * suit.scale

    basePart = suit.find('**/joint_attachMeter') if suit.isSkeleton else suit.healthBar.hpParts[0]
    foo.setY(basePart.getY() + offset)
    foo.setX(basePart.getX())
    if extraPos:
        foo.setPos(foo.getPos() + Point3(extraPos))
    newPos = foo.getPos(other)
    foo.removeNode()
    return Point3(newPos)


def __suitMiddleTargetPoint(suit, other=render):
    newPos = suit.find('**/joint_head').getPos(render)
    newPos.setZ(suit.getZ(render) + suit.getHeight() * 0.5)
    return newPos


def __suitHeadTargetPoint(suit, other=render):
    newPos = suit.find('**/joint_head').getPos(render)
    return newPos


def __suitTargetPoint(suit, other=render):
    pnt = suit.getPos(other)
    pnt.setZ(pnt[2] + suit.getHeight() * 0.5)
    return Point3(pnt)


def __suitMissPoint(suit, other = render):
    pnt = suit.getPos(other)
    pnt.setY(pnt[1] + suit.getHeight() * 1.3)
    pnt.setZ(pnt[2] + suit.getHeight() * 0.5)
    return pnt


def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.loop, 'neutral'))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def createSuitResetPosTrack(suit, battle):
    return __createSuitResetPosTrack(suit, battle)


def __getSuitTrack(suit, target, tContact, tDodge, hp, hitSuit, hpbonus, kbbonus, anim, died, leftSuits, rightSuits, battle, toon, fShowStun, revived=0, finalZap=False, dodge=True, zapLevel=0, hideSkeleHead: bool = False):
    if hitSuit:
        suitTrack = Sequence()
        hasSpecialDeath = MovieUtil.shouldOverrideSuitDeath(suit)
        if hp != 1:
            # Level 1 to prevent showing the skelecog unless its the last zap
            movieZapLevel = zapLevel if finalZap else 0
            if (not finalZap) or (died and zapLevel >= 4) and not hasSpecialDeath:
                sival = Parallel(Func(suit.loop, anim, fromFrame=0, toFrame=19), MovieUtil.zapCog(suit, battle, movieZapLevel, anim, hideSkeleHead=hideSkeleHead))
            else:
                sival = Parallel(ActorInterval(suit, anim), MovieUtil.zapCog(suit, battle, movieZapLevel, anim, hideSkeleHead=hideSkeleHead))
        else:
            sival = Sequence()
        if target and target['extraArgs']:
            effectType = target['extraArgs'][0]
        else:
            effectType = None
        showDamage = Func(suit.showHpText, hp, openEnded=0, attackTrack=AttackEnum.TOON_ZAP, rttIndex=effectType)
        updateHealthBar = Func(suit.updateHealthBar, hp)
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(sival)
        bonusTrack = Sequence(Wait(tContact))
        if (suit.isLured or kbbonus > 0) and not died:
            suitTrack.append(__createSuitResetPosTrack(suit, battle))
            suitTrack.append(MovieUtil.unlureSuit(suit, battle))
            if suit.specialHead:
                suitTrack.append(Func(suit.specialHead.loopNeutral))
            if suit.stunStars:
                suitTrack.append(Func(suit.cleanupStunStars))
        if died and finalZap:
            if zapLevel <= 3 or hasSpecialDeath:
                suitTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
            else:
                suitTrack.append(MovieUtil.suitDisintegrateTrack(suit, battle))
        elif revived != 0 and finalZap:
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
        else:
            if finalZap and not died:
                suitTrack.append(Func(suit.loop, 'neutral'))
                if suit.specialHead:
                    suitTrack.append(Func(suit.specialHead.loopNeutral))
        return Parallel(suitTrack, bonusTrack)
    elif dodge:
        suit.zapDodged = True  # Tell non joybuzzer/rug movies to force a dodge
        missed = Sequence(MovieUtil.createSuitDodgeMultitrack(tDodge, suit, leftSuits, rightSuits, battle.activeSuits), Func(suit.loop, 'neutral'))
        if suit.specialHead:
            missed.append(Func(suit.specialHead.loopNeutral))
        if suit.stunStars:
            missed.append(Func(suit.cleanupStunStars))
        if suit.isLured:
            missed.append(MovieUtil.unlureSuit(suit, battle))
            missed.append(Sequence(__createSuitResetPosTrack(suit, battle)))
        return missed
    else:
        miss = Sequence(Wait(tDodge), Func(MovieUtil.indicateMissed, toon), Func(suit.loop, 'neutral'))
        if suit.specialHead:
            miss.append(Func(suit.specialHead.loopNeutral))
        if suit.stunStars:
            miss.append(Func(suit.cleanupStunStars))
        if suit.isLured:
            miss.append(MovieUtil.unlureSuit(suit, battle))
            miss.append(Sequence(__createSuitResetPosTrack(suit, battle)))
        return miss


def getZapJumpTrack(zap, battle, target, delay=0.0):
    targetIndex = zap['target'].index(target)
    lastSuit = zap['target'][targetIndex - 1]['suit']

    def getOtherSuitStartPos():
        return __suitMiddleTargetPoint(lastSuit, render)

    def targetPoint():
        return __suitMiddleTargetPoint(target['suit'], render)

    otherSprayTrack = Sequence()
    otherSprayTrack.append(Wait(delay))
    otherSprayTrack.append(
        MovieUtil.getZapTrack(battle, WaterSprayColor, getOtherSuitStartPos, targetPoint, 0.2, 1.0, 0.2,
                              horizScale=0.6, vertScale=0.6, activeTrack=True))
    return otherSprayTrack


def __getSoundTrack(level, hitSuit, delay, node = None, duration = 0):
    if hitSuit:
        soundEffect = globalBattleSoundCache.getSound(hitSoundFiles[level])
    else:
        soundEffect = globalBattleSoundCache.getSound(missSoundFiles[level])
    soundTrack = Sequence()
    if soundEffect:
        soundTrack.append(Wait(delay))
        if duration:
            soundTrack.append(SoundInterval(soundEffect, node=node, duration=duration))
        else:
            soundTrack.append(SoundInterval(soundEffect, node=node))
        return soundTrack


def __doJoybuzzer(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    initialZap = True
    tracks = Parallel()
    for target in zap['target']:
        suit = target['suit']
        hp = target['hp']
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = suit.doId in suitsDied
        isFinalZap = finalZap[suit.doId] == toon.doId
        isFirstZap = firstZap[suit.doId] == toon.doId
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        battle = zap['battle']
        suitPos = suit.getPos(battle)
        origHpr = toon.getHpr(battle)
        origPos = toon.getPos(battle)
        midPos = lambda toon=toon, suit=suit: Point3(toon.getX(battle)*-0.25, 0, 0) + Point3(suit.getX(battle), 0, 0)
        runDur = 1
        runBackHpr = Vec3(0, 0, 0)
        hitSuit = zap['sidestep'] == 0
        tTotalFlowerToonAnimationTime = 2
        tContact = 3.35
        tSuitDodges = tTotalFlowerToonAnimationTime
        button = globalPropPool.getProp('joybuzz')
        buttons = [button]
        hands = toon.getRightHands()
        if initialZap:
            toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, suit), Func(toon.loop, 'run'), Wait(1),
                                 ActorInterval(toon, 'water-gun'), Func(MovieUtil.removeProps, buttons), Func(toon.setHpr, battle, runBackHpr),
                                 Func(toon.loop, 'run'), Wait(1), Func(toon.stop), Func(toon.loop, 'neutral'),  Func(toon.setHpr, battle, origHpr))

            moveTrack = Sequence(LerpPosInterval(toon, runDur, midPos, other=battle), Wait(5), LerpPosInterval(toon, runDur, origPos, other=battle))
            tracks.append(toonTrack)
            tracks.append(moveTrack)
            tracks.append(__getSoundTrack(level, hitSuit, tContact, toon))

        if hitSuit or isFirstZap:
            suitTrack = Sequence(Wait(tSuitDodges))
            if initialZap:
                suitTrack.append(ActorInterval(suit, 'reach', startFrame=0, endFrame=20))
            else:
                suitTrack.append(Wait(20/24))
            suitTrack.append(__getSuitTrack(
                        suit, target, 0, 0, hp, hitSuit, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits,
                        battle, toon, fShowStun, revived=revived, dodge=False, finalZap=isFinalZap, zapLevel=level))
            if hitSuit and not initialZap:
                # Show Zap chains between jumped cogs
                tracks.append(getZapJumpTrack(zap, battle, target, delay=tSuitDodges + (20/24)))

        else:
            suitTrack = Sequence(Wait(tSuitDodges), __getSuitTrack(suit, target, 0, 0, hp, hitSuit, hpbonus, kbbonus,
                                                                   'small-zap', died, leftSuits, rightSuits, battle,
                                                                   toon, fShowStun, revived=revived, dodge=False,
                                                                   finalZap=isFinalZap, zapLevel=level))
        tracks.append(suitTrack)
        initialZap = False
        if not hitSuit:
            break

    return tracks


def __doRug(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    initialZap = True
    tracks = Parallel()
    for target in zap['target']:
        suit = target['suit']
        hp = target['hp']
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = suit.doId in suitsDied
        isFinalZap = finalZap[suit.doId] == toon.doId
        isFirstZap = firstZap[suit.doId] == toon.doId
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        battle = zap['battle']
        origHpr = toon.getHpr(battle)
        hitSuit = zap['sidestep'] == 0
        scale = sprayScales[level]
        tSpray = 2.2
        dSprayScale = 0.05
        dSprayHold = 0.1
        tContact = tSpray + dSprayScale
        tSuitDodges = max(tSpray - 0.5, 0.0)
        tracks.append(ActorInterval(toon, 'run'))
        if hitSuit:
            soundTrack = __getSoundTrack(level, hitSuit, 0, toon)
        else:
            soundTrack = __getSoundTrack(level, hitSuit, 0, toon, duration=2.2)
        tracks.append(soundTrack)
        rug = globalPropPool.getProp('zapRug')
        rugPos = Point3(0, 0, 0.025)
        rugHpr = Point3(0, 0, 0)
        if initialZap:
            if hitSuit:
                glassTrack = Sequence(
                    Func(MovieUtil.showProp, rug, toon, rugPos, rugHpr),
                    ActorInterval(toon, 'walk', playRate=0.7),
                    ActorInterval(toon, 'run'),
                    ActorInterval(toon, 'water', playRate=1, startFrame=0, endFrame=36),
                    Wait(1),
                    Func(MovieUtil.removeProp, rug),
                    Func(toon.loop, 'neutral'),
                    Func(toon.setHpr, battle, origHpr)
                )
            else:
                glassTrack = Sequence(
                    Func(MovieUtil.showProp, rug, toon, rugPos, rugHpr),
                    ActorInterval(toon, 'walk', playRate=0.7),
                    ActorInterval(toon, 'run'),
                    ActorInterval(toon, 'slip-forward', playRate=1, startFrame=0, endFrame=36),
                    Func(MovieUtil.removeProp, rug),
                    Func(toon.loop, 'neutral'),
                    Func(toon.setHpr, battle, origHpr)
                )
            tracks.append(glassTrack)
        targetPoint = lambda suit = suit: __suitTargetPoint(suit)

        def getSprayStartPos(toon = toon):
            toon.update(0)
            if not toon.find('**/def_joint_right_hold').isEmpty():
                joint = toon.find('**/def_joint_right_hold')
            else:
                joint = toon.find('**/joint_Rhold')
            p = joint.getPos(render)
            return p

        if initialZap:
            if hitSuit:
                sprayTrack = MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
                tracks.append(Sequence(Wait(tSpray), sprayTrack))
        if hitSuit or isFirstZap:
            tracks.append(__getSuitTrack(suit, target, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'small-zap', died,
                                         leftSuits, rightSuits, battle, toon, fShowStun, revived=revived,
                                         finalZap=isFinalZap, dodge=False, zapLevel=level))
        if hitSuit and not initialZap:
            # Show Zap chains between jumped cogs
            tracks.append(getZapJumpTrack(zap, battle, target, delay=tContact))
        initialZap = False
        if not hitSuit:
            break

    return tracks


def __doLightbulb(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    initialZap = True
    tracks = Parallel()
    lightbulb = globalPropPool.getProp('lightbulb')
    offNode = lightbulb.find('**/off')
    onNode = lightbulb.find('**/on')
    shineNode = lightbulb.find('**/shine')
    onSfx = globalBattleSoundCache.getSound('AA_zap_lightbulb_on.ogg')
    fallSfx = globalBattleSoundCache.getSound('AA_zap_lightbulb_fall.ogg')
    impactSfx = globalBattleSoundCache.getSound('AA_zap_lightbulb_impact.ogg')
    appearSfx = globalBattleSoundCache.getSound('AA_zap_lightbulb_appear.ogg')
    offNode.show()
    onNode.hide()
    shineNode.hide()
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    dBalloonScale = 0.825
    tSpray = 1.5
    throwPlayrate = 1.0
    thinkPlayrate = 1.5
    thinkDur = (toon.getDuration('think') - (10 / 24.0)) * (1.0 / thinkPlayrate)
    tContact = tSpray + 3.5
    tSuitDodges = max(tContact - 0.7, 0.0)
    for target in zap['target']:
        suit = target['suit']
        hp = target['hp']
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = suit.doId in suitsDied
        isFinalZap = finalZap[suit.doId] == toon.doId
        isFirstZap = firstZap[suit.doId] == toon.doId
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        battle = zap['battle']
        origHpr = toon.getHpr(battle)
        hitSuit = zap['sidestep'] == 0

        if initialZap:
            tracks = Parallel()
            toonTrack = Sequence(
                Func(toon.headsUp, suit),
                ActorInterval(toon, 'think', playRate=thinkPlayrate, duration=thinkDur),
                ActorInterval(toon, 'throw', playRate=throwPlayrate),
                Func(toon.loop, 'neutral'),
                Func(toon.setHpr, battle, origHpr)
            )
            tracks.append(toonTrack)
            throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
            soundTrack = Parallel(
                Parallel(
                    Func(base.playSfx, appearSfx, node=toon),
                    Sequence(
                        Wait(1.5),
                        SoundInterval(onSfx, node=toon),
                    ),
                    Sequence(
                        Wait(2.9),
                        SoundInterval(fallSfx, node=toon),
                    ),
                    Sequence(
                        Wait(4.6),
                        SoundInterval(throwSound, node=toon),
                    ),
                ),
            )
            if hitSuit:
                soundTrack.append(Sequence(Wait(tContact - 0.1), SoundInterval(impactSfx, node=toon)))
            tracks.append(soundTrack)

            if hitSuit:
                suitPoint = lambda suit=suit: __suitLightTargetPoint(suit, other=battle)
            else:
                suitPoint = lambda suit=suit: __suitMissPoint(suit, other=battle)

            balloonFly = Sequence(
                Func(lightbulb.wrtReparentTo, render),
                Parallel(
                    LerpPosInterval(lightbulb, 0.3, pos=suitPoint, name=pieFlyTaskName, other=battle),
                    # LerpHprInterval(battery, 0.15, (0, -90, 0), other=suit)
                ),
            )
            if hitSuit:
                balloonFly.append(Func(lightbulb.hide))
            else:
                balloonFly = Parallel(
                    balloonFly,
                    Sequence(Wait(0.2), LerpScaleInterval(lightbulb, 0.1, MovieUtil.PNT3_NEARZERO))
                )
            balloonHide = Func(MovieUtil.removeProp, lightbulb)
            balloonTrack = Sequence(
                Func(MovieUtil.showProp, lightbulb, toon, scale=0.7, pos=(0, 0, toon.height + 3)),
                Parallel(
                    LerpScaleInterval(lightbulb, 0.5, dBalloonScale, startScale=MovieUtil.PNT3_NEARZERO),
                    LerpPosInterval(lightbulb, 0.4, (0, 0, toon.height + 1), startPos=(0, 0, toon.height - 0.5), blendType='easeOut')
                ),
                Wait(1.0),
                Func(offNode.hide),
                Func(onNode.show),
                Func(shineNode.show),
                Wait(1.4),
                Func(lightbulb.wrtReparentTo, hand_jointpath0),
                Parallel(
                    LerpPosHprInterval(lightbulb, 0.3, (1.0, 0, 0.5), (0, 0, -90), blendType='easeIn'),
                    LerpColorScaleInterval(shineNode, 0.1, (1, 1, 1, 0), blendType='easeIn')
                ),
                Wait(tSpray)
            )
            balloonTrack.append(balloonFly)
            if hitSuit:
                BattleParticles.loadParticles()
                particleEffect = BattleParticles.loadParticleFile('batteryGagZap.ptf')
                particleEffect.getParticlesNamed('particles-1').emitter.setAmplitude(9.000)
                partTrack = getPartTrack(particleEffect, tContact, 0.8, [particleEffect, lightbulb, 0],
                                         softStop=-0.4, renderParent=render)
                tracks.append(partTrack)

                freezeEffect = BattleParticles.createParticleEffect(file='lightbulbGagBreak')
                BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
                partTrack2 = getPartTrack(freezeEffect, tContact, 0.4, [freezeEffect, lightbulb, 0],
                                          renderParent=render)
                tracks.append(partTrack2)

            balloonTrack.append(Func(hand_jointpath0.removeNode))
            balloonTrack.append(balloonHide)
            tracks.append(balloonTrack)

        if hitSuit or isFirstZap or (not isFirstZap and not suit.zapDodged):
            tracks.append(__getSuitTrack(suit, target, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'small-zap', died,
                                         leftSuits, rightSuits, battle, toon, fShowStun, revived=revived,
                                         finalZap=isFinalZap, zapLevel=level))
        if hitSuit and not initialZap:
            # Show Zap chains between jumped cogs
            tracks.append(getZapJumpTrack(zap, battle, target, delay=tContact))

        initialZap = False
        if not hitSuit:
            break

    return tracks


def __doRadio(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    battle = zap['battle']
    tSprayDelay = 1.8
    dSprayScale = 0.05
    dSprayHold = 1.6
    tContact = 1.9
    tSuitDodges = 1.7
    scale = sprayScales[level]
    tracks = Parallel()

    radio = globalPropPool.getProp('radio')
    radio.reparentTo(battle)
    radio.setH(180)
    radio.hide()

    buttonSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
    button = globalPropPool.getProp('zap-button')
    buttons = [button]

    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    initialZap = True
    for target in zap['target']:
        suit = target['suit']
        hp = target['hp']
        buttonWaitTime = 0.7
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = suit.doId in suitsDied
        isFinalZap = finalZap[suit.doId] == toon.doId
        isFirstZap = firstZap[suit.doId] == toon.doId
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        origHpr = toon.getHpr(battle)
        endPos = toon.getPos(battle)
        endPos.setY(endPos.getY() + 3)
        firstSprayAppearT = 1.8 + buttonWaitTime
        hands = toon.getLeftHands()
        hitSuit = zap['sidestep'] == 0
        if initialZap:
            tvAppearTrack = Sequence(
                Wait(buttonWaitTime),
                Func(radio.setPos, endPos),
                Func(radio.show),
                LerpScaleInterval(radio, 0.4, 1.1, startScale=0.01, blendType='easeIn'),
                LerpScaleInterval(radio, 0.15, 1.0, blendType='easeOut'),
                Wait(0.85),
                LerpScaleInterval(radio, 0.2, (1.2, 1, 0.6)),
                LerpScaleInterval(radio, 0.1, 1.1),
                LerpScaleInterval(radio, 0.05, 1.0),
                Wait(3.0),
                LerpScaleInterval(radio, 0.2, MovieUtil.PNT3_NEARZERO, blendType='easeInOut'),
                Func(MovieUtil.removeProp, radio)
            )

            toonTrack = Sequence(
                Func(MovieUtil.showProps, buttons, hands),
                Parallel(
                    ActorInterval(button, 'zap-button'),
                    ActorInterval(toon, 'pushbutton')
                ),
                Func(MovieUtil.removeProps, buttons),
                Func(toon.loop, 'neutral'),
                Func(toon.setHpr, battle, origHpr)
            )
            toonTrack = Parallel(
                toonTrack,
                Sequence(Wait(2.3), SoundInterval(buttonSound, duration=0.67, node=toon))
            )

            tracks.append(tvAppearTrack)
            tracks.append(toonTrack)
            soundTrack = __getSoundTrack(level, hitSuit, firstSprayAppearT, toon)
            tracks.append(soundTrack)
        targetPoint = lambda suit=suit: __suitTargetPoint(suit)

        antennaZ = 1.55
        antennaDist = 0.45

        def getFirstAntennaStartPoint(radio=radio):
            foo = radio.attachNewNode('foo')
            foo.setPos(-antennaDist, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getSecondAntennaStartPoint(radio=radio):
            foo = radio.attachNewNode('foo')
            foo.setPos(antennaDist, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getAntennaEndPoint(radio=radio):
            foo = radio.attachNewNode('foo')
            foo.setPos(0, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getSprayStartPos(radio=radio, toon=toon):
            toon.update(0)
            p = radio.getPos(render) + Point3(0, 0, 0.45)
            return p

        if initialZap:
            firstSprayTrack = Sequence(
                Wait(firstSprayAppearT),
                MovieUtil.getZapTrack(battle, WaterSprayColor, getFirstAntennaStartPoint, getAntennaEndPoint,
                                        dSprayScale, 1.8, dSprayScale, horizScale=0.2, vertScale=0.2)
            )
            tracks.append(firstSprayTrack)
            secondSprayTrack = Sequence(
                Wait(firstSprayAppearT),
                MovieUtil.getZapTrack(battle, WaterSprayColor, getSecondAntennaStartPoint, getAntennaEndPoint,
                                        dSprayScale, 1.8, dSprayScale, horizScale=0.2, vertScale=0.2)
            )
            tracks.append(secondSprayTrack)

            sprayTrack = Sequence()
            sprayTrack.append(Wait(tSprayDelay + buttonWaitTime))
            sprayTrack.append(
                MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale,
                                        dSprayHold, dSprayScale,
                                        horizScale=scale, vertScale=scale))

            tracks.append(sprayTrack)

        if hitSuit or isFirstZap or (not isFirstZap and not suit.zapDodged):
            tracks.append(__getSuitTrack(suit, target, tContact + buttonWaitTime, tSuitDodges, hp, hitSuit, hpbonus,
                                            kbbonus, 'large-zap', died, leftSuits, rightSuits, battle, toon, fShowStun,
                                            revived=revived, finalZap=isFinalZap, zapLevel=level))
        if hitSuit and not initialZap:
            # Show Zap chains between jumped cogs
            tracks.append(getZapJumpTrack(zap, battle, target, delay=tContact + buttonWaitTime))

        initialZap = False
        if not hitSuit:
            break

    return tracks


def __doBattery(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    initialZap = True
    tracks = Parallel()
    battery = globalPropPool.getProp('battery')
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    dBalloonScale = 0.825
    tSpray = 51.0 / toon.getFrameRate('throw')
    dSprayScale = 0.7
    tContact = tSpray + dSprayScale + 0.1
    tSuitDodges = max(tContact - 0.7, 0.0)
    for target in zap['target']:
        suit = target['suit']
        hp = target['hp']
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = suit.doId in suitsDied
        isFinalZap = finalZap[suit.doId] == toon.doId
        isFirstZap = firstZap[suit.doId] == toon.doId
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        battle = zap['battle']
        suitPos = suit.getPos(battle)
        origHpr = toon.getHpr(battle)
        hitSuit = zap['sidestep'] == 0

        if initialZap:
            tracks = Parallel()
            toonTrack = Sequence(Func(toon.headsUp, suit), ActorInterval(toon, 'throw'),
                                 Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
            tracks.append(toonTrack)
            throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
            soundTrack = Parallel(
                Sequence(
                    Wait(2.6),
                    SoundInterval(throwSound, node=toon)
                ),
            )
            if hitSuit:
                soundTrack.append(__getSoundTrack(level, hitSuit, tContact, toon, duration=1.5))
            tracks.append(soundTrack)

            if hitSuit:
                suitPoint = lambda suit=suit: __suitLightTargetPoint(suit, other=battle)
            else:
                suitPoint = lambda suit=suit: __suitMissPoint(suit, other=battle)

            def reparentBattery(suit=suit):
                if suit.isSkeleton:
                    battery.wrtReparentTo(suit.find('**/joint_attachMeter'))
                else:
                    battery.wrtReparentTo(suit.healthBar.hpParts[0])
                if suit.style.body == 'c' and not suit.isSkeleton:
                    battery.setR(100)
                battery.setPos(suit, __suitLightTargetPoint(suit, other=suit))
                battery.setColorScaleOff(1)

            balloonFly = Sequence(
                Func(battery.wrtReparentTo, render),
                Parallel(
                    LerpPosInterval(battery, 0.3, pos=suitPoint, name=pieFlyTaskName, other=battle),
                    LerpHprInterval(battery, 0.2, (-90, 0, 90), other=suit)
                ),
            )
            if hitSuit:
                balloonFly.append(Func(reparentBattery))
            else:
                balloonFly = Parallel(
                    balloonFly,
                    Sequence(Wait(0.2), LerpScaleInterval(battery, 0.1, MovieUtil.PNT3_NEARZERO))
                )
            balloonHide = Func(MovieUtil.removeProp, battery)
            balloonTrack = Sequence(
                Func(MovieUtil.showProp, battery, hand_jointpath0, scale=0.7),
                LerpScaleInterval(battery, 0.5, dBalloonScale, startScale=MovieUtil.PNT3_NEARZERO),
                Wait(tSpray)
            )
            balloonTrack.append(balloonFly)
            if hitSuit:
                BattleParticles.loadParticles()
                particleEffect = BattleParticles.loadParticleFile('batteryGagZap.ptf')
                partTrack = getPartTrack(particleEffect, tContact, 1.7, [particleEffect, battery, 0],
                                         softStop=-0.41, renderParent=render)
                tracks.append(partTrack)

                def updateBatteryX(value, mult=1.0):
                    battery.setZ(value*mult)

                totalTime = 1.3
                moveTime = 0.05
                moveAmt = 0.3
                for _ in range(int(totalTime / moveTime)):
                    balloonTrack.append(LerpFunctionInterval(updateBatteryX, duration=moveTime / 4, fromData=0, toData=moveAmt))
                    balloonTrack.append(LerpFunctionInterval(updateBatteryX, duration=moveTime / 4, fromData=moveAmt, toData=0))
                    balloonTrack.append(LerpFunctionInterval(updateBatteryX, duration=moveTime / 4, fromData=0, toData=moveAmt, extraArgs=[-1]))
                    balloonTrack.append(LerpFunctionInterval(updateBatteryX, duration=moveTime / 4, fromData=moveAmt, toData=0, extraArgs=[-1]))

                fallPoint = (0.0, 3.0, 0.5)

                fallSeq = Sequence()
                if died and not MovieUtil.shouldOverrideSuitDeath(suit):
                    fallSeq.append(Sequence(
                        Wait(0.4),
                        LerpScaleInterval(battery, 0.2, MovieUtil.PNT3_NEARZERO, blendType='easeInOut')
                    ))
                else:
                    fallSeq.append(Func(battery.wrtReparentTo, render))
                    fallSeq.append(Parallel(
                        LerpHprInterval(battery, 0.3, (-90, 0, 50), blendType='easeOut', other=suit),
                        LerpPosInterval(battery, 0.8, fallPoint, blendType='easeIn', other=suit),
                        Sequence(
                            Wait(0.6),
                            LerpScaleInterval(battery, 0.2, MovieUtil.PNT3_NEARZERO, blendType='easeInOut')
                        )
                    ))

                balloonTrack.append(fallSeq)

            balloonTrack.append(Func(hand_jointpath0.removeNode))
            balloonTrack.append(balloonHide)
            tracks.append(balloonTrack)

        if hitSuit or isFirstZap or (not isFirstZap and not suit.zapDodged):
            tracks.append(__getSuitTrack(suit, target, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'small-zap', died,
                                         leftSuits, rightSuits, battle, toon, fShowStun, revived=revived,
                                         finalZap=isFinalZap, zapLevel=level))
        if hitSuit and not initialZap:
            # Show Zap chains between jumped cogs
            tracks.append(getZapJumpTrack(zap, battle, target, delay=tContact))

        initialZap = False
        if not hitSuit:
            break

    return tracks


def __doTv(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    battle = zap['battle']
    tSprayDelay = 1.8
    dSprayScale = 0.05
    dSprayHold = 1.6
    tContact = 1.9
    tSuitDodges = 1.7
    scale = sprayScales[level]

    tv = globalPropPool.getProp('tv')
    tv.reparentTo(battle)
    tv.setH(180)
    tv.hide()

    tracks = Parallel()

    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    initialZap = True
    for target in zap['target']:
        suit = target['suit']
        hp = target['hp']
        buttonWaitTime = 0.7
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = suit.doId in suitsDied
        isFinalZap = finalZap[suit.doId] == toon.doId
        isFirstZap = firstZap[suit.doId] == toon.doId
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        origHpr = toon.getHpr(battle)
        endPos = toon.getPos(battle)
        endPos.setY(endPos.getY() + 3)
        firstSprayAppearT = 1.8 + buttonWaitTime
        hands = toon.getLeftHands()
        hitSuit = zap['sidestep'] == 0
        if initialZap:
            tvAppearTrack = Sequence(
                Wait(buttonWaitTime),
                Func(tv.setPos, endPos),
                Func(tv.show),
                LerpScaleInterval(tv, 0.4, 1.1, startScale=0.01, blendType='easeIn'),
                LerpScaleInterval(tv, 0.15, 1.0, blendType='easeOut'),
                Wait(0.85),
                LerpScaleInterval(tv, 0.2, (1.2, 1, 0.6)),
                LerpScaleInterval(tv, 0.1, 1.1),
                LerpScaleInterval(tv, 0.05, 1.0),
                Wait(3.0),
                LerpScaleInterval(tv, 0.2, MovieUtil.PNT3_NEARZERO, blendType='easeInOut'),
                Func(MovieUtil.removeProp, tv)
            )

            buttonSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
            button = globalPropPool.getProp('zap-button')
            buttons = [button]

            toonTrack = Sequence(
                Func(MovieUtil.showProps, buttons, hands),
                Parallel(
                    ActorInterval(button, 'zap-button'),
                    ActorInterval(toon, 'pushbutton')
                ),
                Func(MovieUtil.removeProps, buttons),
                Func(toon.loop, 'neutral'),
                Func(toon.setHpr, battle, origHpr)
            )
            toonTrack = Parallel(
                toonTrack,
                Sequence(Wait(2.3), SoundInterval(buttonSound, duration=0.67, node=toon))
            )

            tracks.append(tvAppearTrack)
            tracks.append(toonTrack)
            soundTrack = __getSoundTrack(level, hitSuit, tSprayDelay, toon)
            tracks.append(soundTrack)
        targetPoint = lambda suit = suit: __suitTargetPoint(suit)

        antennaZ = 2.1
        antennaDist = 0.38

        def getFirstAntennaStartPoint(tv=tv):
            foo = tv.attachNewNode('foo')
            foo.setPos(-antennaDist, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getSecondAntennaStartPoint(tv=tv):
            foo = tv.attachNewNode('foo')
            foo.setPos(antennaDist, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getAntennaEndPoint(tv=tv):
            foo = tv.attachNewNode('foo')
            foo.setPos(0, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getSprayStartPos(tv = tv, toon = toon):
            toon.update(0)
            p = tv.getPos(render) + Point3(0, 0, 0.7)
            return p

        if initialZap:
            firstSprayTrack = Sequence(
                Wait(firstSprayAppearT),
                MovieUtil.getZapTrack(battle, WaterSprayColor, getFirstAntennaStartPoint, getAntennaEndPoint,
                                        dSprayScale, 1.8, dSprayScale, horizScale=0.2, vertScale=0.2)
            )
            tracks.append(firstSprayTrack)
            secondSprayTrack = Sequence(
                Wait(firstSprayAppearT),
                MovieUtil.getZapTrack(battle, WaterSprayColor, getSecondAntennaStartPoint, getAntennaEndPoint,
                                        dSprayScale, 1.8, dSprayScale, horizScale=0.2, vertScale=0.2)
            )
            tracks.append(secondSprayTrack)

            sprayTrack = Sequence()
            sprayTrack.append(Wait(tSprayDelay + buttonWaitTime))
            sprayTrack.append(MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale,
                                horizScale=scale, vertScale=scale))

            tracks.append(sprayTrack)

        if hitSuit or isFirstZap or (not isFirstZap and not suit.zapDodged):
            tracks.append(__getSuitTrack(suit, target, tContact + buttonWaitTime, tSuitDodges, hp, hitSuit, hpbonus,
                                            kbbonus, 'large-zap', died, leftSuits, rightSuits, battle, toon, fShowStun,
                                            revived=revived, finalZap=isFinalZap, zapLevel=level))
        if hitSuit and not initialZap:
            # Show Zap chains between jumped cogs
            tracks.append(getZapJumpTrack(zap, battle, target, delay=tContact + buttonWaitTime))

        initialZap = False
        if not hitSuit:
            break

    return tracks


def __doStagelight(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    hitSuit = False

    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    tracks    = Parallel()  # The full animation group.
    hitTracks = Parallel()  # All of the suit reaction tracks.

    # Some constants for positioning.
    stagelightZOffset = 20   # How far in the sky the stagelight will spawn.
    stagelightScale   = 1.25  # Size of the stagelight.
    stagelightFallOffset = Vec3(12, 12, -15)  # Where the stagelight falls off at.
    stagelightSpinOffset = Vec3(90, 90, 90)   # The end HPR of the stagelight when it falls.
    spotlightAlpha = 0.7  # The alpha  of the actual spotlight (not the stagelight).

    # Some constants for timing.
    stagelightDelay            = 2.50  # The delay before anything stagelight happens.
    stagelightSpawnDelay       = 0.00  # The delay before dropshadows & stagelight spawn. This is relative to stagelightDelay.
    stageLightFallDelay        = 2.20  # The time it waits for the stagelight to start falling
    stagelightFallDuration     = 0.15  # The time it takes for the stagelight & drop shadow to fall.
    stagelightGrowDelay        = 0.08  # The delay before the actual grow effect occurs.
    stagelightGrowDuration     = 0.02  # The duration for the stagelight itself to spawn in.
    stagelightHoldDuration     = 1.00  # How long the stagelight remains on the cog head.
    stagelightShrinkDuration   = [1.35, 0.40]  # The duration for the stagelight to shrink away. First is proj interval, second is hpr/scale
    stagelightFlickerDuration  = 0.05  # The duration of each stagelight flicker.
    stagelightFlickerStart     = 0.60  # The time to wait before performing any flickers.
    stagelightFlickers = [(0.0, 0.6), (0.4, 0.2), (0.6, 0.7), (0.8, 0.4), (0.9, 0.7), (1.1, 0.2), (1.2, 0.0)]  # The timing for each flicker -- the light stays off at the last one. The second value of the tuple is for the alpha upon unflicker.
    stagelightParticleRushTime = 0.00  # How much sooner the particles spawn.
    glassBreakDuration         = 0.40  # The duration of the glass break particles.
    suitSurpriseDelay          = 0.70  # The delay before the Suit gets surprised by the light.
    suitReactionTime           = 0.65  # The reaction time of the Suit attempting to dodge.
    suitReactionBuffer         = 0.05  # A buffer time to end the suit reaction early.
    suitReactionDelay          = stagelightDelay + + stageLightFallDelay + stagelightFallDuration  # The delay before all of the suit zap reactions happen.
    dodgeTime                  = suitReactionDelay - suitReactionTime  # Time before the attack is dodged.
    dropshadowScaleTrack = (
        # The time & scales for the dropshadow (multiplied by the stagelight scale).
        (0.0, 0.01),
        (stagelightFlickers[-1][0] + stagelightFlickerStart, 0.01),
        (stageLightFallDelay + stagelightFallDuration, 1.1),
    )
    dropshadowActive = False  # use the dropshadow?

    # Set up the stagelight for drop usage.
    stagelight = globalPropPool.getProp('stagelight')
    stagelight.hide()
    node = stagelight.node()
    node.setBounds(OmniBoundingVolume())
    node.setFinal(1)

    # Get the first suit.
    firstSuit = None
    if zap['target']:
        firstSuit = zap['target'][0]['suit']

    # Go over each target the Zap has hit.
    for zapIndex, target in enumerate(zap['target']):
        # Figure out if this is the first iteration.
        initialZap = (zapIndex == 0)

        # Some useful constants for reference.
        suit    = target['suit']
        hitSuit = zap['sidestep'] == 0
        battle  = zap['battle']
        isFirstZap = firstZap[suit.doId] == toon.doId
        origHpr = toon.getHpr(battle)

        # We only want to calculate certain things for the first Zap used.
        if initialZap:
            # Some setup.
            tracks = Parallel()
            stagelight.reparentTo(render)
            spotlight = stagelight.find('**/spotlight')
            spotlight.setColorScale(1.0, 1.0, 1.0, spotlightAlpha)
            if battle.hasLocalToon():
                stagelight.setBin('fixed', 1)

            # Load the button in.
            buttonSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
            button = globalPropPool.getProp('zap-button')
            buttons = [button]

            # Make the toon track. They need to take out the button and use it.
            hands = toon.getLeftHands()
            toonTrack = Sequence(
                Func(MovieUtil.showProps, buttons, hands),
                Parallel(
                    ActorInterval(button, 'zap-button'),
                    ActorInterval(toon, 'pushbutton')
                ),
                Func(MovieUtil.removeProps, buttons),
                Func(toon.loop, 'neutral'),
                Func(toon.setHpr, battle, origHpr)
            )
            toonTrack = Parallel(
                toonTrack,
                Sequence(Wait(2.3), SoundInterval(buttonSound, duration=0.67, node=toon))
            )
            tracks.append(toonTrack)

            # Set up the stagelight track.
            # The stagelight has hit -- so we do all the special suit reactions for it.
            stagelightTrack = Parallel()
            tracks.append(Sequence(Wait(stagelightDelay), stagelightTrack))

            # Add the gag soundtrack.
            stagelightTrack.append(__getSoundTrack(level, hitSuit, 0.0, toon))

            # Helper method to position the stagelight prop.
            def positionStagelight():
                stagelight.setPos(firstSuit.getPos(render) + Vec3(0, 0, stagelightZOffset))

            # OK, We'll now make the dropshadow track.
            # Set up the track now.
            dropshadowTrack = Sequence(Wait(stagelightSpawnDelay))
            if dropshadowActive:
                stagelightTrack.append(dropshadowTrack)

            # Create a dropshadow. Base it off the suit because we're lazy.
            dropShadow = MovieUtil.copyProp(firstSuit.getShadowJoint())

            # Helper method to position the dropshadow:
            def posShadow():
                # Drop shadow positioning.
                dropShadow.reparentTo(battle)
                dropShadow.setPos(firstSuit.getPos(battle))
                dropShadow.setHpr(firstSuit.getHpr(battle))

                # Raise the drop shadow to curb level.
                dropShadow.setZ(dropShadow.getZ() + 0.025)

            # Make the shadow track.
            dropshadowTrack.append(Func(battle.movie.needRestoreRenderProp, dropShadow))
            dropshadowTrack.append(Func(posShadow))
            for trackIndex in range(len(dropshadowScaleTrack))[1:]:
                timeA, scaleA = dropshadowScaleTrack[trackIndex - 1]
                timeB, scaleB = dropshadowScaleTrack[trackIndex + 0]
                scaleA *= stagelightScale
                scaleB *= stagelightScale
                dropshadowTrack.append(
                    LerpScaleInterval(
                        nodePath=dropShadow, duration=timeB - timeA,
                        startScale=scaleA, scale=scaleB,
                    )
                )
            dropshadowTrack.append(Func(MovieUtil.removeProp, dropShadow))
            dropshadowTrack.append(Func(battle.movie.clearRenderProp, dropShadow))

            # From here,
            if hitSuit:
                # Some helper methods for what's about to happen!
                hiddenParts = []

                def reparentStagelight():
                    stagelight.wrtReparentTo(firstSuit.find('**/joint_head'))
                    stagelight.setPos(0, 0, 0)
                    stagelight.setHpr(0, 0, 0)
                    stagelight.setColorScaleOff(1)
                    for part in firstSuit.getHeadParts():
                        if not part.isHidden():
                            part.hide()
                            hiddenParts.append(part)

                def unparentStagelight(hp=hiddenParts):
                    stagelight.wrtReparentTo(render)
                    for part in hp:
                        part.show()
                    del hp

                # Create the suit reaction track.
                suitReaction = Sequence()
                if isFirstZap:
                    suitReaction = Sequence(
                        Wait(stagelightSpawnDelay),
                        Wait(stagelightGrowDuration),
                        Wait(suitSurpriseDelay),
                        ActorInterval(
                            actor=firstSuit,
                            animName='soak',
                            startTime=0.0,
                            endTime=(stageLightFallDelay
                                     + stagelightFallDuration
                                     - stagelightGrowDuration
                                     - suitSurpriseDelay
                                     - suitReactionBuffer),
                        )
                    )

                # The Suit now gets hit and obliterated by the stagelight!
                stagelightEndCallback = lambda firstSuit=firstSuit: __suitHeadTargetPoint(firstSuit, other=render)
                stagelightMoveTrack = Sequence(
                    # Wait before the stagelight should go.
                    Wait(stagelightSpawnDelay),

                    # Initial movement sequence.
                    Parallel(
                        # The suit begins its reaction, the stagelight spawns and starts falling.
                        suitReaction,
                        Sequence(
                            # We reveal the stagelight here.
                            Wait(stagelightGrowDelay),

                            # Reveal it now.
                            Func(stagelight.show),

                            # Scale it in.
                            LerpScaleInterval(
                                nodePath=stagelight,
                                duration=stagelightGrowDuration,
                                startScale=MovieUtil.PNT3_NEARZERO,
                                scale=stagelightScale,
                                other=render,
                                blendType='easeIn',
                            ),
                        ),
                        Sequence(
                            Func(positionStagelight),
                            Wait(stageLightFallDelay),
                            LerpPosInterval(
                                nodePath=stagelight,
                                duration=stagelightFallDuration,
                                pos=stagelightEndCallback,
                                blendType='easeIn',
                            ),
                        ),
                        name='stagelightInitialMove',
                    ),

                    # The stagelight should now stick onto the suit's head and sit there.
                    Func(reparentStagelight),
                    Wait(stagelightHoldDuration),

                    # At this point, the stagelight slumps off.
                    Func(unparentStagelight),
                    Parallel(
                        ProjectileInterval(
                            node=stagelight,
                            duration=stagelightShrinkDuration[0],
                            endPos=lambda: stagelightEndCallback() + stagelightFallOffset,
                        ),
                        LerpHprInterval(
                            nodePath=stagelight,
                            duration=stagelightShrinkDuration[1],
                            hpr=stagelightSpinOffset,
                        ),
                        LerpScaleInterval(
                            nodePath=stagelight,
                            duration=stagelightShrinkDuration[1],
                            startScale=stagelightScale,
                            scale=MovieUtil.PNT3_NEARZERO,
                            blendType='easeIn',
                        ),
                    ),

                    # Cleanup.
                    Func(MovieUtil.removeProp, stagelight),
                    name='stagelightMoveTrack',
                )

                # Make the flicker track.
                flickerTrack = Track()
                completeFlickerSequence = Sequence(
                    Wait(stagelightSpawnDelay),
                    Wait(stagelightFlickerStart),
                    flickerTrack,
                )
                for flickerIndex, flickerData in enumerate(stagelightFlickers):
                    flickerTime, flickerAlpha = flickerData
                    lastTime = flickerIndex == (len(stagelightFlickers) - 1)
                    flickerSeq = Sequence(
                        Func(spotlight.hide),
                        Wait(stagelightFlickerDuration),
                        (Func(spotlight.show) if not lastTime else Wait(0.0)),
                        Func(spotlight.setColorScale, 1.0, 1.0, 1.0, flickerAlpha)
                    )
                    flickerTrack.append((flickerTime, flickerSeq))

                # Make particle track.
                BattleParticles.loadParticles()
                particleEffect = BattleParticles.loadParticleFile('stagelightGagZap.ptf')
                freezeEffect = BattleParticles.createParticleEffect(file='stagelightGagBreak')
                BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
                particleTrack = Sequence(
                    Wait(stagelightSpawnDelay),
                    Wait(stageLightFallDelay - stagelightParticleRushTime),
                    Wait(stagelightFallDuration),
                    Parallel(
                        # Glass break track.
                        getPartTrack(
                            particleEffect=freezeEffect,
                            startDelay=0.0,
                            durationDelay=glassBreakDuration,
                            partExtraArgs=[freezeEffect, stagelight, 0],
                            renderParent=render,
                        ),
                        # Electricity track.
                        getPartTrack(
                            particleEffect=particleEffect,
                            startDelay=0.0,
                            durationDelay=stagelightHoldDuration + stagelightParticleRushTime + stagelightShrinkDuration[1],
                            partExtraArgs=[particleEffect, stagelight, 0],
                            softStop=-stagelightShrinkDuration[1],
                            renderParent=render,
                        ),
                    ),
                )

                # Now, put all the sequences together.
                stagelightTrack.append(suitReaction)
                stagelightTrack.append(stagelightMoveTrack)
                stagelightTrack.append(completeFlickerSequence)
                stagelightTrack.append(particleTrack)
            else:
                # The stagelight misses. That sucks.
                # Create the suit reaction track.
                suitReaction = Sequence(
                    Wait(stagelightSpawnDelay),
                    Wait(stagelightGrowDuration),
                    Wait(suitSurpriseDelay),
                    ActorInterval(
                        actor=firstSuit,
                        animName='soak',
                        startTime=0.0,
                        endTime=(stageLightFallDelay
                                 + stagelightFallDuration
                                 - stagelightGrowDuration
                                 - suitSurpriseDelay
                                 - suitReactionBuffer),
                    )
                )

                # The stagelight falls and bounces pathetically.
                stagelightEndCallback = lambda firstSuit=firstSuit: firstSuit.getPos(render)
                stagelightMoveTrack = Sequence(
                    # Wait before the stagelight should go.
                    Wait(stagelightSpawnDelay),

                    # Initial movement sequence.
                    Parallel(
                        # The suit begins its reaction, the stagelight spawns and starts falling.
                        suitReaction,
                        Sequence(
                            # We reveal the stagelight here.
                            Wait(stagelightGrowDelay),

                            # Reveal it now.
                            Func(stagelight.show),

                            # Scale it in.
                            LerpScaleInterval(
                                nodePath=stagelight,
                                duration=stagelightGrowDuration,
                                startScale=MovieUtil.PNT3_NEARZERO,
                                scale=stagelightScale,
                                other=render,
                                blendType='easeIn',
                            ),
                        ),
                        Sequence(
                            Func(positionStagelight),
                            Wait(stageLightFallDelay),
                            LerpPosInterval(
                                nodePath=stagelight,
                                duration=stagelightFallDuration,
                                pos=stagelightEndCallback,
                                blendType='easeIn',
                            ),
                        ),
                        name='stagelightInitialMove',
                    ),

                    # At this point, the stagelight slumps off.
                    Parallel(
                        ProjectileInterval(
                            node=stagelight,
                            duration=stagelightShrinkDuration[0],
                            endPos=lambda: stagelightEndCallback() + stagelightFallOffset,
                        ),
                        LerpHprInterval(
                            nodePath=stagelight,
                            duration=stagelightShrinkDuration[1],
                            hpr=stagelightSpinOffset,
                        ),
                        LerpScaleInterval(
                            nodePath=stagelight,
                            duration=stagelightShrinkDuration[1],
                            startScale=stagelightScale,
                            scale=MovieUtil.PNT3_NEARZERO,
                            blendType='easeIn',
                        ),
                    ),

                    # Cleanup.
                    Func(MovieUtil.removeProp, stagelight),
                    name='stagelightMoveTrack',
                )

                # Make the flicker track.
                flickerTrack = Track()
                completeFlickerSequence = Sequence(
                    Wait(stagelightSpawnDelay),
                    Wait(stagelightFlickerStart),
                    flickerTrack,
                )
                for flickerIndex, flickerData in enumerate(stagelightFlickers):
                    flickerTime, flickerAlpha = flickerData
                    lastTime = flickerIndex == (len(stagelightFlickers) - 1)
                    flickerSeq = Sequence(
                        Func(spotlight.hide),
                        Wait(stagelightFlickerDuration),
                        (Func(spotlight.show) if not lastTime else Wait(0.0)),
                        Func(spotlight.setColorScale, 1.0, 1.0, 1.0, flickerAlpha)
                    )
                    flickerTrack.append((flickerTime, flickerSeq))

                # Make particle track.
                BattleParticles.loadParticles()
                freezeEffect = BattleParticles.createParticleEffect(file='lightbulbGagBreak')
                BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
                particleTrack = Sequence(
                    Wait(stagelightSpawnDelay),
                    Wait(stageLightFallDelay - stagelightParticleRushTime),
                    Wait(stagelightFallDuration),
                    Parallel(
                        # Glass break track.
                        getPartTrack(
                            particleEffect=freezeEffect,
                            startDelay=0.0,
                            durationDelay=glassBreakDuration,
                            partExtraArgs=[freezeEffect, stagelight, 0],
                            renderParent=render,
                        ),
                    ),
                )

                # Now, put all the sequences together.
                stagelightTrack.append(suitReaction)
                stagelightTrack.append(stagelightMoveTrack)
                stagelightTrack.append(completeFlickerSequence)
                stagelightTrack.append(particleTrack)

        # Separated from everything else, we'll make the zap jump tracks once.
        if hitSuit and not initialZap:
            hitTracks.append(getZapJumpTrack(zap, battle, target, delay=0.0))

        # The suit will only have this reaction to the first zap used against them.
        if hitSuit or isFirstZap or (not isFirstZap and not suit.zapDodged):
            # Constants for the suit track.
            hp = target['hp']
            hpbonus = target['hpbonus']
            kbbonus = target['kbbonus']
            died = suit.doId in suitsDied
            revived = target['revived']
            leftSuits = target['leftSuits']
            rightSuits = target['rightSuits']
            isFinalZap = finalZap[suit.doId] == toon.doId

            # Now make the hit sequence!
            hitTracks.append(
                __getSuitTrack(suit, target, 0.0, 0.0, hp, hitSuit, hpbonus, kbbonus, 'large-zap',
                               died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived,
                               finalZap=isFinalZap, zapLevel=level, hideSkeleHead=initialZap))

    # Some final track mastering
    if hitSuit:
        # The attack hit, do the hit tracks when we get hit.
        tracks.append(Sequence(Wait(suitReactionDelay), hitTracks))
    else:
        # We need to dodge a little bit sooner to dodge the attacks!
        tracks.append(Sequence(Wait(dodgeTime), hitTracks))

    # We're done here.
    return tracks


def __doTesla(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    battle = zap['battle']
    tracks = Parallel()
    dSprayScale = 0.05
    dSprayHold = 1.6
    tContact = 2.6
    tSpray = 2.5
    tSprayDelay = 2.5
    tSuitDodges = 1.8
    shrinkDuration = 0.4
    button = globalPropPool.getProp('zap-button')
    buttons = [button]

    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    initialZap = True

    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 3)
    coil = globalPropPool.getProp('tesla')
    coil.setPos(endPos)
    coil.hide()
    for target in zap['target']:
        suit = target['suit']
        hp = target['hp']
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = suit.doId in suitsDied
        isFinalZap = finalZap[suit.doId] == toon.doId
        isFirstZap = firstZap[suit.doId] == toon.doId
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        origHpr = toon.getHpr(battle)
        hitSuit = zap['sidestep'] == 0
        scale = sprayScales[level]
        soundTrack = __getSoundTrack(level, hitSuit, 1.6, toon)
        tracks.append(soundTrack)
        hands = toon.getLeftHands()
        if initialZap:
            toonTrack = Sequence(
                Func(MovieUtil.showProps, buttons, hands),
                Func(toon.headsUp, battle, endPos),
                Parallel(
                    ActorInterval(button, 'zap-button'),
                    ActorInterval(toon, 'pushbutton')
                ),
                Func(MovieUtil.removeProps, buttons),
                Func(toon.loop, 'neutral'),
                Func(toon.setHpr, battle, origHpr)
            )
            buttonSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
            toonTrack = Parallel(
                toonTrack,
                Sequence(Wait(2.3), SoundInterval(buttonSound, duration=0.67, node=toon))
            )

            tracks.append(toonTrack)
            propTrack = Sequence()
            propTrack.append(Func(coil.setScale, MovieUtil.PNT3_NEARZERO))
            propTrack.append(Func(coil.reparentTo, battle))
            propTrack.append(Func(coil.show))
            propTrack.append(Wait(0.5))
            propTrack.append(LerpScaleInterval(coil, 0.8, 1.2, blendType='easeOut'))
            propTrack.append(LerpScaleInterval(coil, 0.2, 1.0, blendType='easeIn'))
            propTrack.append(Wait(0.75))
            propTrack.append(LerpScaleInterval(coil, 0.2, (1.2, 1, 0.8)))
            propTrack.append(LerpScaleInterval(coil, 0.1, 1.1))
            propTrack.append(LerpScaleInterval(coil, 0.05, 1.0))
            propTrack.append(Wait(tSpray + 0.7))
            propTrack.append(LerpScaleInterval(coil, 0.3, 1.2, blendType='easeIn'))
            propTrack.append(LerpScaleInterval(coil, 0.3, MovieUtil.PNT3_NEARZERO, blendType='easeIn'))
            propTrack.append(Func(MovieUtil.removeProp, coil))
            tracks.append(propTrack)

        targetPoint = lambda suit = suit: __suitTargetPoint(suit)

        def getSprayStartPos(coil = coil, toon = toon):
            toon.update(0)
            p = coil.find('**/zap_origin').getPos(render)
            p.setZ(p.getZ() + 0.4)
            return p

        if initialZap:
            BattleParticles.loadParticles()
            particleEffect = BattleParticles.loadParticleFile('teslaGagZap.ptf')
            partTrack = getPartTrack(particleEffect, tSprayDelay - 0.2, 1.8, [particleEffect, coil.find('**/zap_origin'), 0],
                                        softStop=-0.41, renderParent=render)
            tracks.append(partTrack)

            sprayTrack = Sequence()
            sprayTrack.append(Wait(tSprayDelay))
            sprayTrack.append(MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint,
                                                    dSprayScale, dSprayHold, dSprayScale, horizScale=scale,
                                                    vertScale=scale))

            tracks.append(sprayTrack)

        if hitSuit or isFirstZap or (not isFirstZap and not suit.zapDodged):
            tracks.append(__getSuitTrack(suit, target, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'large-zap',
                                            died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived,
                                            finalZap=isFinalZap, zapLevel=level))
        if hitSuit and not initialZap:
            # Show Zap chains between jumped cogs
            tracks.append(getZapJumpTrack(zap, battle, target, delay=tContact))

        initialZap = False
        if not hitSuit:
            break

    return tracks


def __doLightning(zap, delay, fShowStun, suitsDied=[], firstZap={}, finalZap={}):
    toon = zap["avatar"]
    level = zap['level']
    tracks = Parallel()
    tContact = 3.6
    tSuitDodges = 3.1
    button = globalPropPool.getProp('zap-button')
    buttons = [button]
    hands = toon.getLeftHands()
    battle = zap['battle']
    origHpr = toon.getHpr(battle)

    for target in zap['target']:
        suit = target['suit']
        break

    suitPos = suit.getPos(battle)
    lookStraight = zap["avatar"].getPos(battle)
    lookStraight.setY(lookStraight.getY() + 7)
    toonTrack = Sequence(
        Func(MovieUtil.showProps, buttons, hands),
        Func(toon.headsUp, suit),
        Parallel(ActorInterval(button, 'zap-button'),
                 ActorInterval(toon, 'pushbutton')
                 ),
        Func(MovieUtil.removeProps, buttons),
        Func(toon.loop, 'neutral')
    )

    toonTrack.append(Func(toon.setHpr, battle, origHpr))

    tracks.append(toonTrack)

    # Sorry for the confusing names here between initialZap and firstZap.
    # Initial Zap refers to the first zap of a set of zap jumps from one gag.
    # First Zap refers to the first zap gag that targets this suit overall.
    initialZap = True

    for target in zap['target']:
        suit = target['suit']
        hp = target['hp']
        hpbonus = target['hpbonus']
        kbbonus = target['kbbonus']
        died = suit.doId in suitsDied
        isFinalZap = finalZap[suit.doId] == toon.doId
        isFirstZap = firstZap[suit.doId] == toon.doId
        revived = target['revived']
        leftSuits = target['leftSuits']
        rightSuits = target['rightSuits']
        battle = zap['battle']
        hitSuit = zap['sidestep'] == 0
        soundTrack = __getSoundTrack(level, hitSuit, 2.6, toon)
        tracks.append(soundTrack)
        lightning = globalPropPool.getProp('lightning')
        lightning.reparentTo(battle)
        lightning.hide()
        lightning.setScale(1, 1, 3)

        def getCloudTrack(lightning, suit, battle = battle):
            BattleParticles.loadParticles()
            particleEffect = BattleParticles.loadParticleFile('lightningGagExplosion.ptf')
            particleEffect.setScale(suit.scale * 1.5)
            particleNode = suit.attachNewNode(f'suit-{suit.doId}-zap-particle-node')
            particleNode.setColorScaleOff(1)
            particleEffect.getParticlesNamed('particles-1').emitter.setOffsetForce(Vec3(0.0000, 0.0000, 15.0000 + suit.height))
            partTrack = getPartTrack(particleEffect, tContact - 0.61, 3.0, [particleEffect, particleNode, 0], softStop=-2.4, renderParent=particleNode)
            tracks = Parallel()
            track = Sequence(
                Wait(tContact),
                Func(lambda suit=suit: lightning.setPos(suit.getPos(battle))),
                Func(lightning.show),
                Wait(0.1),
                LerpColorScaleInterval(lightning, 1.0, (1, 1, 1, 0)),
                Func(MovieUtil.removeProp, lightning)
            )
            tracks.append(track)
            tracks.append(Sequence(partTrack, Func(particleNode.removeNode)))
            return tracks

        if initialZap:
            tracks.append(getCloudTrack(lightning, suit))
            buttonSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
            soundTrack = Sequence(Wait(2.3), SoundInterval(buttonSound, duration=0.67, node=toon), Wait(0.3))
            tracks.append(soundTrack)

        if hitSuit or isFirstZap or (not isFirstZap and not suit.zapDodged):
            tracks.append(__getSuitTrack(suit, target, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'large-zap',
                                            died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived,
                                            finalZap=isFinalZap, zapLevel=level))
        if hitSuit and not initialZap:
            # Show Zap chains between jumped cogs
            tracks.append(getZapJumpTrack(zap, battle, target, delay=tContact))
        initialZap = False
        if not hitSuit:
            break

    return tracks


def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop=0, renderParent=render):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop, renderParent=renderParent))


zapfn_array = (__doJoybuzzer,
               __doLightbulb,
               __doRadio,
               __doBattery,
               __doTv,
               __doStagelight,
               __doTesla,
               __doLightning)
