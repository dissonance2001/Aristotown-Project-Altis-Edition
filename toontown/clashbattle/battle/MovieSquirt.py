from direct.interval.IntervalGlobal import *
from toontown.clashbattle.battle.BattleBase import *
from toontown.clashbattle.battle.BattleProps import *
from toontown.clashbattle.battle.BattleSounds import *
from toontown.clashbattle.battle.movielistener.BattleMovieListenerEnum import BMLE
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.toon.ToonDNA import *
from toontown.clashsuit.suit.SuitDNA import *
from toontown.clashbattle.battle import MovieUtil
from toontown.clashbattle.battle import MovieLure
from toontown.clashbattle.battle import BattleParticles
from toontown.clashbattle.battle import BattleGlobals
from collections import OrderedDict

notify = getNotify('MovieSquirt')
hitSoundFiles = ('AA_squirt_flowersquirt.ogg', 'AA_squirt_glasswater.ogg', 'AA_squirt_neonwatergun.ogg', 'Seltzer_squirt_2dgame_hit.ogg', 'AA_squirt_seltzer.ogg', 'firehose_spray.ogg', 'AA_throw_stormcloud.ogg', 'AA_squirt_Geyser.ogg')
missSoundFiles = ('AA_squirt_flowersquirt_miss.ogg', 'AA_squirt_glasswater_miss.ogg', 'AA_squirt_neonwatergun_miss.ogg', 'another_spongebob_reference.ogg', 'AA_squirt_seltzer_miss.ogg', 'firehose_spray.ogg', 'AA_throw_stormcloud_miss.ogg', 'AA_squirt_Geyser.ogg')
sprayScales = [0.2, 0.3, 0.1, 0.6, 0.6, 0.8, 1.0, 2.0, 2.0]
WaterSprayColor = Point4(0.75, 0.75, 1.0, 0.8)
pieFlyTaskName = 'MovieSquirt-pieFly'
tBalloonLeavesHand = 2.7
tBalloonHitsSuit = 3.0
tSuitDodges = 2.45
ratioMissToHit = 1.5
tBalloonShrink = 0.7


def doSquirts(squirts):
    if len(squirts) == 0:
        return (None, None)

    suitSquirtsDict = OrderedDict()
    for squirt in squirts:
        target = squirt['target'][0]
        suitId = target['suit'].doId
        if suitId in suitSquirtsDict:
            suitSquirtsDict[suitId].append(squirt)
        else:
            suitSquirtsDict[suitId] = [squirt]

    suitSquirts = list(suitSquirtsDict.values())
    suitSquirts.sort(key=len)

    delay = 0.0

    mtrack = Parallel()
    for st in suitSquirts:
        if len(st) > 0:
            ival = __doSuitSquirts(st)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay += TOON_SQUIRT_DELAY

    camDuration = mtrack.getDuration()
    # chooseSquirtShot was deprecated as it was a duplicate of chooseThrowShot
    camTrack = squirts[0]['battle'].camera.chooseSquirtShot(squirts, suitSquirtsDict, camDuration)
    return (mtrack, camTrack)


def __doSuitSquirts(squirts):
    uberClone = 0
    toonTracks = Parallel()
    delay = 0.0
    # Determine how many times the suit is hit, if only once, play stun effect
    fShowStun = len(squirts) == 1 and squirts[0]['sidestep'] == 0
    for s in squirts:
        tracks = __doSquirt(s, delay, fShowStun, uberClone)
        if s['level'] >= BattleGlobals.UBER_GAG_LEVEL_INDEX:
            uberClone = 1
        if tracks:
            for track in tracks:
                toonTracks.append(track)

        delay += TOON_SQUIRT_DELAY

    return toonTracks


def __doSquirt(squirt, delay, fShowStun, uberClone=0):
    squirtSequence = Sequence(Wait(delay))
    if uberClone:
        ival = squirtfn_array[squirt['level']](squirt, delay, fShowStun, uberClone)
        if ival:
            squirtSequence.append(ival)
    else:
        ival = squirtfn_array[squirt['level']](squirt, delay, fShowStun)
        if ival:
            squirtSequence.append(ival)
    return [squirtSequence]


def __balloonPreMiss(missDict, balloon, suitPoint, other=render):
    missDict['balloon'] = balloon
    missDict['startScale'] = balloon.getScale()
    missDict['startPos'] = balloon.getPos(other)
    if callable(suitPoint):
        suitPoint = suitPoint()
    v = Vec3(suitPoint - missDict['startPos'])
    endPos = missDict['startPos'] + v * ratioMissToHit
    missDict['endPos'] = endPos


def __balloonMissLerpCallback(t, missDict):
    balloon = missDict['balloon']
    newPos = missDict['startPos'] * (1.0 - t) + missDict['endPos'] * t
    if t < tBalloonShrink:
        tScale = 0.0001
    else:
        tScale = (t - tBalloonShrink) / (1.0 - tBalloonShrink)
    newScale = missDict['startScale'] * max(1.0 - tScale, 0.01)
    balloon.setPos(newPos)
    balloon.setScale(newScale)


def __suitMissPoint(suit, other=render):
    pnt = suit.getPos(other)
    pnt.setY(pnt[1] + suit.getHeight() * 1.3)
    pnt.setZ(pnt[2] + suit.getHeight() * 1.3)
    return pnt


def __suitTargetPoint(suit):
    pnt = suit.getPos(render)
    pnt.setZ(pnt[2] + suit.getHeight() * 0.66)
    return Point3(pnt)


def __suitHitPoint(suit):
    return suit.getHeadParts()[0]


def __getSplashTrack(point, scale, delay, battle, splashHold = 0.01, keepFollow = False, fadeDuration=None):

    def prepSplash(splash, point):
        if callable(point):
            point = point()
        if not isinstance(point, LVecBase3f):
            point = point.getPos()
        splash.reparentTo(render)
        splash.setPos(point)
        scale = splash.getScale()
        splash.setBillboardPointWorld()
        splash.setScale(scale)

    def updateSplashPos(_, point):
        if callable(point):
            point = point()
        if not isinstance(point, LVecBase3f):
            point = point.getPos(render)
        splash.setPos(point)

    splash = globalPropPool.getProp('splash-from-splat')
    splash.setScale(scale)

    splashTrack = Sequence(
        Func(prepSplash, splash, point),
        ActorInterval(splash, 'splash-from-splat'),
        Wait(splashHold),
    )
    moveTrack = Sequence() if not keepFollow else LerpFunctionInterval(
        updateSplashPos, splashTrack.getDuration(), extraArgs=[point]
    )
    fadeTrack = Sequence() if fadeDuration is None else LerpColorScaleInterval(
        splash, fadeDuration, (1, 1, 1, 0),
    )

    return Sequence(
        Func(battle.movie.needRestoreRenderProp, splash),
        Wait(delay),
        Parallel(splashTrack, moveTrack),
        fadeTrack,
        Func(MovieUtil.removeProp, splash),
        Func(battle.movie.clearRenderProp, splash)
    )


def __getSuitTrack(suit, tContact, tDodge, hp, hitSuit, hpbonus, kbbonus, anim, died, 
                   leftSuits, rightSuits, battle, toon, fShowStun, beforeStun = 0.5, 
                   afterStun = 1.8, geyser = 0, uberRepeat = 0, revived = 0, level = -1, 
                   target=None):
    if hitSuit:
        suitTrack = Sequence()
        sival = []
        battle.sendMovieEvent(BMLE.EVENT_ON_SOAKED, suitTrack, suit=suit)
        if kbbonus < 0 and not geyser:
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            suitType = getSuitBodyType(suit.getStyleName())
            animTrack = Sequence()
            if anim != 'squirt-large-react':
                animTrack.append(ActorInterval(suit, anim, duration=0.2))
                if suitType == 'a':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.43))
                elif suitType == 'b':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=1.94))
                elif suitType == 'c':
                    animTrack.append(ActorInterval(suit, 'slip-forward', startTime=2.58))
            else:
                animTrack.append(ActorInterval(suit, anim))
            animTrack.append(MovieUtil.unlureSuit(suit, battle))
            animTrack.append(Func(suit.loop, 'neutral'))
            if suit.specialHead:
                animTrack.append(Func(suit.specialHead.loopNeutral))
            if suit.stunStars:
                animTrack.append(Func(suit.cleanupStunStars))
            moveTrack = Sequence(Wait(0.2), LerpPosInterval(suit, 0.6, pos=suitPos, other=battle))
            sival = Parallel(animTrack, moveTrack)
        elif geyser:
            suitPos, suitHpr = battle.getActiveSuitPosHpr(suit)

            raiseOffset = Point3(0, 0, 14)
            raisePos = suitPos + raiseOffset
            lowerPos = suitPos
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
            sival = Sequence(
                ActorInterval(suit, 'slip-backward', playRate=0.5, startFrame=0, endFrame=startFlailFrame - 1),
                Func(suit.pingpong, 'slip-backward', fromFrame=startFlailFrame, toFrame=endFlailFrame),
                Wait(0.5),
                ActorInterval(suit, 'slip-backward', playRate=1.0, startFrame=endFlailFrame)
            )
            sUp = LerpPosInterval(suit, 1.1, raisePos, other=battle, fluid=1)
            sDown = LerpPosInterval(suit, 0.6, lowerPos, other=battle, fluid=1)
            if suit.specialHead:
                sival.append(Func(suit.specialHead.loopNeutral))
            if suit.stunStars:
                sival.append(Func(suit.cleanupStunStars))
            if suit.isLured:
                sival.append(MovieUtil.unlureSuit(suit, battle))
                sival.append(Sequence(MovieLure.__createSuitResetPosTrack(suit, battle)))
            sival.append(Func(suit.loop, 'neutral'))
        elif fShowStun == 1:
            sival = Parallel(ActorInterval(suit, anim), MovieUtil.createSuitStunInterval(suit, beforeStun, afterStun))
        else:
            sival = ActorInterval(suit, anim)
        frozen = getattr(suit, 'movieFrozen', False)
        if target and target[0]['extraArgs']:
            tgt = target[0]
            roundsWet = tgt['extraArgs'][0]
            if len(tgt['extraArgs']) > 1:
                effectType = tgt['extraArgs'][1]
            else:
                effectType = 0
        else:
            roundsWet = NumRoundsSoaked[level]
            effectType = 0

        if frozen:
            effectType = 2

        showDamage = Func(
            suit.showHpText, hp, openEnded=0, attackTrack=AttackEnum.TOON_SQUIRT, rounds=roundsWet,
            rttIndex=effectType,
        )

        updateHealthBar = Func(suit.updateHealthBar, hp)
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)

        suitTrack.append(Func(MovieUtil.applyVisualEffect, suit, VisualEffectEnum.FROZEN if frozen else VisualEffectEnum.SOAKED))

        otherSuitsTrack = Sequence(Wait(tContact))
        bothSuitsSoaked = Parallel()

        # Soak neighboring suits
        suitsToSoak = target[1:] if target and len(target) > 1 else []

        for suitToSoak in suitsToSoak:
            soakSuit = suitToSoak['suit']
            if not soakSuit.isUntouchable:
                extraSuitSoakTrack = Sequence(
                    # For pacesetter functionality
                    Func(soakSuit.setPlayRate, battle.timescale, 'squirt-small-react'),
                    Func(soakSuit.play, 'squirt-small-react'),
                )
                if not soakSuit.isSoaked:
                    battle.sendMovieEvent(BMLE.EVENT_ON_SOAKED, extraSuitSoakTrack, suit=soakSuit)
                    frozen = getattr(soakSuit, 'movieFrozen', False)
                    extraSuitSoakTrack.append(Sequence(
                        Func(MovieUtil.applyVisualEffect, soakSuit, VisualEffectEnum.FROZEN if frozen else VisualEffectEnum.SOAKED),
                    ))

                if suitToSoak['extraArgs']:
                    roundsWet = suitToSoak['extraArgs'][0]
                else:
                    roundsWet = 0

                hp = suitToSoak['hp']

                loopAnim = 'lured' if soakSuit.isLured else 'neutral'
                extraSuitSoakTrack.append(Sequence(
                    Func(
                        soakSuit.showHpText, hp, openEnded=0, attackTrack=AttackEnum.TOON_SQUIRT,
                        rounds=roundsWet, rttIndex=2 if frozen else 0,
                    ),
                    Func(soakSuit.updateHealthBar, hp),
                    Wait(4),
                ))
                if suitToSoak['revived'] != 0:
                    extraSuitSoakTrack.append(MovieUtil.createSuitReviveTrack(soakSuit, toon, battle))
                elif suitToSoak['died'] != 0:
                    extraSuitSoakTrack.append(MovieUtil.createSuitDeathTrack(soakSuit, toon, battle))
                else:
                    extraSuitSoakTrack.append(Func(soakSuit.loop, loopAnim))
                    # Reset the play rate we put on this animation earlier
                    extraSuitSoakTrack.append(Func(soakSuit.setPlayRate, 1.0, 'squirt-small-react'))
                bothSuitsSoaked.append(extraSuitSoakTrack)

        otherSuitsTrack.append(bothSuitsSoaked)
        if not geyser:
            suitTrack.append(sival)
        elif not uberRepeat:
            geyserMotion = Sequence(sUp, Wait(0.0), sDown)
            suitLaunch = Parallel(sival, geyserMotion)
            suitTrack.append(suitLaunch)
        else:
            suitTrack.append(Wait(5.5))

        bonusTrack = Sequence(Wait(tContact))
        if kbbonus < 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, kbbonus, 2, openEnded=0))
            bonusTrack.append(Func(suit.updateHealthBar, kbbonus))
        if hpbonus < 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, hpbonus, 1, openEnded=0))
            bonusTrack.append(Func(suit.updateHealthBar, hpbonus))
        if died != 0:
            suitTrack.append(MovieUtil.createSuitDeathTrack(suit, toon, battle))
        else:
            suitTrack.append(Func(suit.loop, 'neutral'))
        if revived != 0:
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, toon, battle))
        return Parallel(suitTrack, bonusTrack, otherSuitsTrack)
    else:
        missed = Sequence(MovieUtil.createSuitDodgeMultitrack(tDodge, suit, leftSuits, rightSuits, battle.activeSuits), Func(suit.loop, 'neutral'))
        if suit.specialHead:
            missed.append(Func(suit.specialHead.loopNeutral))
        if suit.stunStars:
            missed.append(Func(suit.cleanupStunStars))
        if suit.isLured:
            missed.append(MovieUtil.unlureSuit(suit, battle))
            missed.append(Sequence(MovieLure.__createSuitResetPosTrack(suit, battle)))
        return missed


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


def __doFlower(squirt, delay, fShowStun):
    toon = squirt["avatar"]
    level = squirt['level']
    target = squirt['target'][0]
    hpbonus = target['hpbonus']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    origHpr = toon.getHpr(battle)
    hitSuit = squirt['sidestep'] == 0
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
    buttons = [button]
    hands = toon.getLeftHands()
    toonTrack = Sequence(
        Func(MovieUtil.showProps, buttons, hands),
        Func(toon.headsUp, suit),
        Parallel(
            ActorInterval(button, 'squirt-button'),
            ActorInterval(toon, 'pushbutton')
        ),
        Func(MovieUtil.removeProps, buttons),
        Func(toon.loop, 'neutral'),
        Func(toon.setHpr, battle, origHpr)
    )
    tracks.append(toonTrack)
    tracks.append(__getSoundTrack(level, hitSuit, tTotalFlowerToonAnimationTime - 0.4, toon))
    flower = globalPropPool.getProp('squirting-flower')
    flower.setScale(1.5, 1.5, 1.5)
    targetPoint = lambda suit=suit: __suitTargetPoint(suit)

    def getSprayStartPos(flower = flower):
        toon.update(0)
        return flower.getPos(render)

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
    if not toon.find('**/def_joint_attachFlower').isEmpty():
        flower_joint0 = toon.find('**/def_joint_attachFlower')
    flower_jointpath0 = flower_joint0.attachNewNode('attachFlower-InstanceNode')
    flowerTrack = Sequence(
        Wait(tFlowerFirstAppears),
        Func(flower.reparentTo, flower_jointpath0),
        LerpScaleInterval(flower, dFlowerScaleTime, flower.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(tTotalFlowerToonAnimationTime - dFlowerScaleTime - tFlowerFirstAppears)
    )
    if not hitSuit:
        flowerTrack.append(Wait(0.5))
    flowerTrack.append(sprayTrack)
    flowerTrack.append(LerpScaleInterval(flower, dFlowerScaleTime, MovieUtil.PNT3_NEARZERO))
    flowerTrack.append(Func(flower_jointpath0.removeNode))
    flowerTrack.append(Func(MovieUtil.removeProp, flower))
    tracks.append(flowerTrack)
    if hitSuit:
        tracks.append(__getSplashTrack(targetPoint, scale, tSprayStarts + dSprayScale, battle))
    if hitSuit or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=level, target=squirt['target']))
    return tracks


def __doWaterGlass(squirt, delay, fShowStun):
    toon = squirt["avatar"]
    level = squirt['level']
    target = squirt['target'][0]
    hpbonus = target['hpbonus']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    hitSuit = squirt['sidestep'] == 0
    scale = sprayScales[level]
    tSpray = 82.0 / toon.getFrameRate('spit')
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
    glassTrack = Sequence(
        Func(MovieUtil.showProp, glass, hand_jointpath0),
        ActorInterval(glass, 'glass'),
        Func(hand_jointpath0.removeNode),
        Func(MovieUtil.removeProp, glass),
        Func(toon.loop, 'neutral')
    )
    tracks.append(glassTrack)
    targetPoint = lambda suit=suit: __suitTargetPoint(suit)

    def getSprayStartPos(toon = toon):
        toon.update(0)
        if not toon.find('**/def_head').isEmpty():
            joint = toon.find('**/def_head')
        else:
            joint = toon.find('**/joint_head')
        n = hidden.attachNewNode('pointInFrontOfHead')
        n.reparentTo(toon)
        n.setPos(joint.getPos(toon) + Point3(0, 0.3, -0.2))
        p = n.getPos(render)
        n.removeNode()
        del n
        return p

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
    tracks.append(Sequence(Wait(tSpray), sprayTrack))
    if hitSuit:
        tracks.append(__getSplashTrack(targetPoint, scale, tSpray + dSprayScale, battle))
    if hitSuit or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=level, target=squirt['target']))
    return tracks


def __doWaterGun(squirt, delay, fShowStun):
    toon = squirt["avatar"]
    level = squirt['level']
    target = squirt['target'][0]
    hpbonus = target['hpbonus']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    origHpr = toon.getHpr(battle)
    hitSuit = squirt['sidestep'] == 0
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
    toonTrack = Sequence(Func(toon.headsUp, suit), ActorInterval(toon, 'water-gun'), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, hitSuit, 1.8, toon)
    tracks.append(soundTrack)
    pistol = globalPropPool.getProp('water-gun')
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    targetPoint = lambda suit=suit: __suitTargetPoint(suit)

    def getSprayStartPos(pistol = pistol, toon = toon):
        toon.update(0)
        joint = pistol.find('**/joint_nozzle')
        p = joint.getPos(render)
        return p

    sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
    pistolPos = Point3(0.28, 0.1, 0.08)
    pistolHpr = VBase3(85.6, -4.44, 94.43)
    pistolTrack = Sequence(
        Func(MovieUtil.showProp, pistol, hand_jointpath0, pistolPos, pistolHpr),
        LerpScaleInterval(pistol, dPistolScale, pistol.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(tSpray - dPistolScale)
    )
    pistolTrack.append(sprayTrack)
    pistolTrack.append(Wait(dPistolHold))
    pistolTrack.append(LerpScaleInterval(pistol, dPistolScale, MovieUtil.PNT3_NEARZERO))
    pistolTrack.append(Func(hand_jointpath0.removeNode))
    pistolTrack.append(Func(MovieUtil.removeProp, pistol))
    tracks.append(pistolTrack)
    if hitSuit:
        tracks.append(__getSplashTrack(targetPoint, 0.3, tSpray + dSprayScale, battle))
    if hitSuit or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=level, target=squirt['target']))
    return tracks


def __doWaterBalloon(squirt, delay, fShowStun):
    toon = squirt["avatar"]
    level = squirt['level']
    target = squirt['target'][0]
    hpbonus = target['hpbonus']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    origHpr = toon.getHpr(battle)
    hitSuit = squirt['sidestep'] == 0
    scale = sprayScales[level]
    dBalloonScale = 0.825
    tSpray = 51.0 / toon.getFrameRate('throw')
    dSprayScale = 0.7
    dSprayHold = 0.1
    tContact = tSpray + dSprayScale
    tSuitDodges = max(tContact - 0.7, 0.0)
    tracks = Parallel()
    toonTrack = Sequence(Func(toon.headsUp, suit), ActorInterval(toon, 'throw'), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    soundTrack = Parallel(Sequence(Wait(2.6), SoundInterval(throwSound, node=toon)), __getSoundTrack(level, hitSuit, tContact, toon))
    tracks.append(soundTrack)
    balloon = globalPropPool.getProp('waterBalloon')
    hands = toon.getRightHands()
    targetPoint = lambda suit=suit: __suitTargetPoint(suit)
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    if hitSuit:
        suitPoint = lambda suit=suit: MovieUtil.avatarFacePoint(suit, other=battle)
    else:
        suitPoint = lambda suit=suit: __suitMissPoint(suit,  other=battle)
    balloonFly = Sequence(Func(balloon.wrtReparentTo, render), LerpPosInterval(balloon, 0.3, pos=suitPoint, name=pieFlyTaskName, other=battle))
    balloonHide = Func(MovieUtil.removeProp, balloon)
    balloonTrack = Sequence(Func(MovieUtil.showProp, balloon, hand_jointpath0), LerpScaleInterval(balloon, 0.5, dBalloonScale, startScale=MovieUtil.PNT3_NEARZERO), Wait(tSpray))
    balloonTrack.append(balloonFly)
    if hitSuit:
        balloonTrack.append(balloonHide)
    else:
        missDict = {}
        balloonPreMiss = Func(__balloonPreMiss, missDict, balloon, suitPoint, battle)
        balloonMiss = LerpFunctionInterval(__balloonMissLerpCallback, extraArgs=[missDict], duration=(tBalloonHitsSuit - tBalloonLeavesHand) * ratioMissToHit)
        balloonTrack.append(balloonPreMiss)
        balloonTrack.append(balloonMiss)
        balloonTrack.append(balloonHide)
    balloonTrack.append(Func(hand_jointpath0.removeNode))
    tracks.append(balloonTrack)
    if hitSuit:
        tracks.append(__getSplashTrack(targetPoint, scale, tSpray + dSprayScale, battle))
    if (hitSuit or delay <= 0) and suit:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=level, target=squirt['target']))
    return tracks


def __doSeltzerBottle(squirt, delay, fShowStun):
    toon = squirt["avatar"]
    level = squirt['level']
    target = squirt['target'][0]
    hpbonus = target['hpbonus']
    suit = target['suit']
    hp = target['hp']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    origHpr = toon.getHpr(battle)
    hitSuit = squirt['sidestep'] == 0
    scale = sprayScales[level]
    dBottleScale = 0.5
    dBottleHold = 3.0
    tSpray = 53.0 / toon.getFrameRate('hold-bottle') + 0.05
    dSprayScale = 0.2
    dSprayHold = 0.1
    tContact = tSpray + dSprayScale
    tSuitDodges = max(tContact - 0.7, 0.0)
    tracks = Parallel()
    toonTrack = Sequence(Func(toon.headsUp, suit), ActorInterval(toon, 'hold-bottle'), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, hitSuit, tSpray - 0.1, toon)
    tracks.append(soundTrack)
    bottle = globalPropPool.getProp('bottle')
    hands = toon.getRightHands()
    targetPoint = lambda suit=suit: __suitTargetPoint(suit)

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
    bottleTrack = Sequence(
        Func(MovieUtil.showProp, bottle, hand_jointpath0),
        LerpScaleInterval(bottle, dBottleScale, bottle.getScale(), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(tSpray - dBottleScale)
    )
    bottleTrack.append(sprayTrack)
    bottleTrack.append(Wait(dBottleHold))
    bottleTrack.append(LerpScaleInterval(bottle, dBottleScale, MovieUtil.PNT3_NEARZERO))
    bottleTrack.append(Func(hand_jointpath0.removeNode))
    bottleTrack.append(Func(MovieUtil.removeProp, bottle))
    tracks.append(bottleTrack)
    if hitSuit:
        tracks.append(__getSplashTrack(targetPoint, scale, tSpray + dSprayScale, battle))
    if (hitSuit or delay <= 0) and suit:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'squirt-small-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=level, target=squirt['target']))
    return tracks


def __doFireHose(squirt, delay, fShowStun):
    toon = squirt["avatar"]
    level = squirt['level']
    scale = 0.3
    tAppearDelay = 0.7
    dHoseHold = 0.7
    dAnimHold = 6.1
    tSprayDelay = 2.8
    dSprayScale = 0.1
    dSprayHold = 54/24
    tContact = 2.9
    tSuitDodges = 2.1

    extraHoseHoldTime = 0.6
    extraHoseHoldFrame = 64
    
    target = squirt['target'][0]
    suit = target['suit']
    hp = target['hp']
    hpbonus = target['hpbonus']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    battle = squirt['battle']
    origHpr = toon.getHpr(battle)
    hitSuit = squirt['sidestep'] == 0
    tracks = Parallel()
    toonTrack = Sequence(
        Wait(tAppearDelay),
        Func(toon.headsUp, suit),
        ActorInterval(toon, 'firehose', duration=extraHoseHoldFrame/24),
        Func(toon.pose, 'firehose', extraHoseHoldFrame),
        Wait(extraHoseHoldTime),
        ActorInterval(toon, 'firehose', startFrame=extraHoseHoldFrame),
        Func(toon.loop, 'neutral'),
        Func(toon.setHpr, battle, origHpr)
    )
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, hitSuit, tSprayDelay, toon)
    tracks.append(soundTrack)
    hose = globalPropPool.getProp('firehose')
    hydrant = globalPropPool.getProp('hydrant')
    hose.reparentTo(hydrant)
    hose.pose('firehose', 2)
    hydrantNode = toon.attachNewNode('hydrantNode')
    hydrantNode.clearTransform(toon.getGeomNode().getChild(0))
    hydrantScale = hydrantNode.attachNewNode('hydrantScale')
    hydrant.reparentTo(hydrantScale)
    toon.pose('firehose', 30)
    toon.update(0)
    torso = toon.getPart('torso')
    if toon.style.torso[0] == 'm':
        hydrant.setPos(torso, 0, 0, -1.85)
    else:
        hydrant.setPos(torso, 0, 0, -1.45)
    hydrant.setPos(0, 0, hydrant.getZ())
    base = hydrant.find('**/base')
    base.setColor(1, 1, 1, 0.5)
    base.setPos(toon, 0, 0, 0)
    toon.loop('neutral')
    missTargetPoint = lambda suit=suit: __suitTargetPoint(suit)
    targetPoint = lambda suit=suit: __suitHitPoint(suit)

    def getSprayMissStartPos(hose = hose, toon = toon, missTargetPoint = missTargetPoint):
        toon.update(0)
        if hose.isEmpty() == 1:
            if callable(missTargetPoint):
                return missTargetPoint()
            else:
                return missTargetPoint
        joint = hose.find('**/joint_water_stream')
        n = hidden.attachNewNode('pointBehindSprayProp')
        n.reparentTo(toon)
        n.setPos(joint.getPos(toon) + Point3(0, -0.55, 0))
        p = n.getPos(render)
        n.removeNode()
        del n
        return p

    def getSprayStartPos(hose = hose, toon = toon, targetPoint = targetPoint):
        toon.update(0)
        if hose.isEmpty() == 1:
            if callable(targetPoint):
                return targetPoint()
            else:
                return targetPoint
        return hose.find('**/joint_water_stream')

    sprayTrack = Sequence()
    sprayTrack.append(Wait(tSprayDelay))
    hydrantNode.detachNode()
    propTrack = Sequence(
        Func(battle.movie.needRestoreRenderProp, hydrantNode),
        Func(hydrantNode.reparentTo, toon),
        LerpScaleInterval(hydrantScale, tAppearDelay * 0.5, Point3(1, 1, 1.4), startScale=Point3(1, 1, 0.01)),
        LerpScaleInterval(hydrantScale, tAppearDelay * 0.3, Point3(1, 1, 0.8), startScale=Point3(1, 1, 1.4)),
        LerpScaleInterval(hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1.2), startScale=Point3(1, 1, 0.8)),
        LerpScaleInterval(hydrantScale, tAppearDelay * 0.1, Point3(1, 1, 1), startScale=Point3(1, 1, 1.2)),
        ActorInterval(hose, 'firehose', duration=extraHoseHoldFrame/24),
        Func(hose.pose, 'firehose', extraHoseHoldFrame),
        Wait(extraHoseHoldTime),
        ActorInterval(hose, 'firehose', startFrame=extraHoseHoldFrame),
        Wait(dHoseHold - 0.2),
        LerpScaleInterval(hydrantScale, 0.2, Point3(1, 1, 0.01), startScale=Point3(1, 1, 1)),
        Func(MovieUtil.removeProps, [hydrantNode, hose]),
        Func(battle.movie.clearRenderProp, hydrantNode)
    )
    if hitSuit:
        sprayTrack.append(
            MovieUtil.getSprayProppedTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale,
                                            dSprayHold, dSprayScale, horizScale=scale, vertScale=scale))
        tracks.append(sprayTrack)
        tracks.append(propTrack)
        tracks.append(__getSplashTrack(targetPoint, 0.4, 2.7, battle, splashHold=1.8, keepFollow=True, fadeDuration=0.2))
    else:
        sprayTrack.append(MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayMissStartPos, missTargetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale))
        tracks.append(sprayTrack)
        tracks.append(propTrack)
        # tracks.append(__getSplashTrack(missTargetPoint, 0.4, 2.7, battle, splashHold=1.5, fadeDuration=0.2))
    if hitSuit or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'squirt-large-react', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived, level=level, target=squirt['target']))
    return tracks


def __doStormCloud(squirt, delay, fShowStun):
    toon = squirt["avatar"]
    tContact = 2.9
    tSuitDodges = 1.8
    level = squirt['level']
    target = squirt['target'][0]
    battle = squirt['battle']
    BattleParticles.loadParticles()
    trickleEffect = BattleParticles.createParticleEffect(file='trickleLiquidate')
    rainEffect = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect2 = BattleParticles.createParticleEffect(file='liquidate')
    rainEffect3 = BattleParticles.createParticleEffect(file='liquidate')

    def getCloudTrack(cloud, suit, cloudPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, cloudHold, useEffect, battle = battle, trickleEffect = trickleEffect):
        track = Sequence(
            Func(MovieUtil.showProp, cloud, suit, cloudPosPoint),
            Func(cloud.pose, 'stormcloud', 0),
            LerpScaleInterval(cloud, 1.5, scaleUpPoint, startScale=MovieUtil.PNT3_NEARZERO),
            Wait(rainDelay)
        )
        if useEffect == 1:
            ptrack = Parallel()
            delay = trickleDuration = cloudHold * 0.25
            trickleTrack = Sequence(
                Func(battle.movie.needRestoreParticleEffect, trickleEffect),
                ParticleInterval(trickleEffect, cloud, worldRelative=0, duration=trickleDuration, cleanup=True),
                Func(battle.movie.clearRestoreParticleEffect, trickleEffect)
            )
            track.append(trickleTrack)
            for i in range(0, 3):
                dur = cloudHold - 2 * trickleDuration
                ptrack.append(Sequence(
                    Func(battle.movie.needRestoreParticleEffect, rainEffects[i]),
                    Wait(delay),
                    ParticleInterval(rainEffects[i], cloud, worldRelative=0, duration=dur, cleanup=True),
                    Func(battle.movie.clearRestoreParticleEffect, rainEffects[i])
                ))
                delay += effectDelay

            ptrack.append(Sequence(Wait(3 * effectDelay), ActorInterval(cloud, 'stormcloud', startTime=1, duration=cloudHold)))
            track.append(ptrack)
        else:
            track.append(ActorInterval(cloud, 'stormcloud', startTime=1, duration=cloudHold))
        track.append(LerpScaleInterval(cloud, 0.5, MovieUtil.PNT3_NEARZERO))
        track.append(Func(MovieUtil.removeProp, cloud))
        return track

    button = globalPropPool.getProp('squirt-button')
    buttons = [button]
    
    tracks = Parallel()
    hands = toon.getLeftHands()
    suit = target['suit']
    hp = target['hp']
    hpbonus = target['hpbonus']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    origHpr = toon.getHpr(battle)
    hitSuit = squirt['sidestep'] == 0
    soundTrack = __getSoundTrack(level, hitSuit, 2.3, toon)
    soundTrack2 = __getSoundTrack(level, hitSuit, 4.6, toon)
    tracks.append(soundTrack)
    tracks.append(soundTrack2)
    toonTrack = Sequence(
        Func(MovieUtil.showProps, buttons, hands),
        Func(toon.headsUp, suit),
        Parallel(
            ActorInterval(button, 'squirt-button'),
            ActorInterval(toon, 'pushbutton')
        ),
        Func(MovieUtil.removeProps, buttons),
        Func(toon.loop, 'neutral'),
        Func(toon.setHpr, battle, origHpr)
    )
    tracks.append(toonTrack)
    cloud = globalPropPool.getProp('stormcloud')
    cloudHeight = suit.height + 3
    cloudPosPoint = Point3(0, 0, cloudHeight)
    scaleUpPoint = Point3(3, 3, 3)
    rainEffects = [rainEffect, rainEffect2, rainEffect3]
    rainDelay = 1
    effectDelay = 0.3
    if hitSuit:
        cloudHold = 4.7
    else:
        cloudHold = 1.7
    tracks.append(getCloudTrack(cloud, suit, cloudPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, cloudHold, useEffect=1))
    if hitSuit or delay <= 0:
        tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'soak', died, leftSuits, rightSuits, battle, toon, fShowStun, beforeStun=2.6, afterStun=2.3, revived=revived, level=level, target=squirt['target']))
    return tracks


def __doGeyser(squirt, delay, fShowStun, uberClone = 0):
    toon = squirt["avatar"]
    tracks = Parallel()
    tContact = 2.9
    tSuitDodges = 1.8
    button = globalPropPool.getProp('squirt-button')
    buttons = [button]
    hands = toon.getLeftHands()
    battle = squirt['battle']
    origHpr = toon.getHpr(battle)
    target = squirt['target'][0]
    suit = target['suit']
    toonTrack = Sequence(
        Func(MovieUtil.showProps, buttons, hands),
        Func(toon.headsUp, suit),
        Parallel(
            ActorInterval(toon, 'pushbutton'),
            ActorInterval(button, 'squirt-button')
        ),
        Func(MovieUtil.removeProps, buttons),
        Func(toon.loop, 'neutral'),
        Func(toon.setHpr, battle, origHpr)
    )
    tracks.append(toonTrack)
    hp = target['hp']
    hpbonus = target['hpbonus']
    kbbonus = target['kbbonus']
    died = target['died']
    revived = target['revived']
    leftSuits = target['leftSuits']
    rightSuits = target['rightSuits']
    hitSuit = squirt['sidestep'] == 0
    level = squirt['level']
    soundTrack = __getSoundTrack(level, hitSuit, 1.8, toon)
    delayTime = random.random()
    tracks.append(Wait(delayTime))
    tracks.append(soundTrack)
    cloud = globalPropPool.getProp('geyser')
    BattleParticles.loadParticles()
    geyserHeight = battle.getH()
    geyserPosPoint = Point3(0, 0, geyserHeight)
    scaleUpPoint = Point3(1.2, 1.2, 1.8)
    rainEffects = []
    rainDelay = 2.5
    effectDelay = 0.3
    if hitSuit:
        geyserHold = 1.5
    else:
        geyserHold = 0.5

    def getGeyserTrack(geyser, suit, geyserPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, geyserHold, useEffect, battle = battle):
        geyserMound = MovieUtil.copyProp(geyser)
        geyserRemoveM = geyserMound.findAllMatches('**/Splash*')
        geyserRemoveM.addPathsFrom(geyserMound.findAllMatches('**/spout'))
        for splashNode in geyserRemoveM:
            splashNode.removeNode()

        geyserWater = MovieUtil.copyProp(geyser)
        geyserRemoveW = geyserWater.findAllMatches('**/hole')
        geyserRemoveW.addPathsFrom(geyserWater.findAllMatches('**/shadow'))
        for holeNode in geyserRemoveW:
            holeNode.removeNode()

        suitPos, suitHpr = battle.getActiveSuitPosHpr(suit)

        track = Sequence(
            Wait(rainDelay),
            Func(MovieUtil.showProp, geyserMound, battle, suitPos),
            Func(MovieUtil.showProp, geyserWater, battle, suitPos),
            LerpScaleInterval(geyserWater, 1.0, scaleUpPoint, startScale=MovieUtil.PNT3_NEARZERO),
            Wait(geyserHold * 0.5), LerpScaleInterval(geyserWater, 0.5, MovieUtil.PNT3_NEARZERO, startScale=scaleUpPoint)
        )
        track.append(LerpScaleInterval(geyserMound, 0.5, MovieUtil.PNT3_NEARZERO))
        track.append(Func(MovieUtil.removeProp, geyserMound))
        track.append(Func(MovieUtil.removeProp, geyserWater))
        track.append(Func(MovieUtil.removeProp, geyser))
        return track

    if not uberClone:
        tracks.append(Sequence(Wait(delayTime), getGeyserTrack(cloud, suit, geyserPosPoint, scaleUpPoint, rainEffects, rainDelay, effectDelay, geyserHold, useEffect=1)))
    if hitSuit or delay <= 0:
        tracks.append(Sequence(Wait(delayTime), __getSuitTrack(suit, tContact, tSuitDodges, hp, hitSuit, hpbonus, kbbonus, 'soak', died, leftSuits, rightSuits, battle, toon, fShowStun, beforeStun=2.6, afterStun=2.3, geyser=1, uberRepeat=uberClone, revived=revived, level=level, target=squirt['target'])))

    return tracks


squirtfn_array = (__doFlower, __doWaterGlass, __doWaterGun, __doWaterBalloon,
                  __doSeltzerBottle, __doFireHose, __doStormCloud, __doGeyser)
