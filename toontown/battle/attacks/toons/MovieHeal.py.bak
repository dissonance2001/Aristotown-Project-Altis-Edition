import random
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.task import Task
from toontown.battle.BattleBase import *
from toontown.battle import BattleParticles
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.battle import HealJokes
from toontown.battle import MovieCamera
from toontown.battle.attacks.toons import MovieNPCSOS
from toontown.battle import MovieUtil
from toontown.chat.ChatGlobals import *
from toontown.effects import Splash
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toonbase.ToontownBattleGlobals import AvPropDamage

notify = DirectNotifyGlobal.directNotify.newCategory('MovieHeal')
soundFiles = ('AA_heal_tickle.ogg', 'AA_heal_telljoke.ogg', 'AA_heal_smooch.ogg', 'AA_heal_happydance.ogg', 'AA_heal_pixiedust.ogg', 'AA_heal_juggle.ogg', 'MG_cannon_confetti.ogg', 'AA_heal_High_Dive.ogg')
healPos = Point3(0, 0, 0)
healHpr = Vec3(180.0, 0, 0)
runHealTime = 1.0

def doHeals(heals, hasInteractivePropHealBonus):
    if len(heals) == 0:
        return (None, None)
    track = Sequence()
    for h in heals:
        ival = __doHealLevel(h, hasInteractivePropHealBonus)
        if ival:
            track.append(ival)

    camDuration = track.getDuration()
    camTrack = MovieCamera.chooseHealShot(heals, camDuration)
    return (track, camTrack)


def __doHealLevel(heal, hasInteractivePropHealBonus):
    level = heal['level']
    if level == 0:
        return __healTickle(heal, hasInteractivePropHealBonus)
    elif level == 1:
        return __healJoke(heal, hasInteractivePropHealBonus)
    elif level == 2:
        return __healSmooch(heal, hasInteractivePropHealBonus)
    elif level == 3:
        return __healDance(heal, hasInteractivePropHealBonus)
    elif level == 4:
        return __healSprinkle(heal, hasInteractivePropHealBonus)
    elif level == 5:
        return __healJuggle(heal, hasInteractivePropHealBonus)
    elif level == 6:
        return __healCannon(heal, hasInteractivePropHealBonus)
    elif level == 7:
        return __healDive(heal, hasInteractivePropHealBonus)
    return None


def __runToHealSpot(heal):
    toon = heal['toon']
    battle = heal['battle']
    level = heal['level']
    origPos, origHpr = battle.getActorPosHpr(toon)
    runAnimI = ActorInterval(toon, 'run', duration=runHealTime)
    a = Func(toon.headsUp, battle, healPos)
    b = Parallel(runAnimI, LerpPosInterval(toon, runHealTime, healPos, other=battle))
    if levelAffectsGroup(HEAL, level):
        c = Func(toon.setHpr, battle, healHpr)
    else:
        target = heal['target']['toon']
        targetPos = target.getPos(battle)
        c = Func(toon.headsUp, battle, targetPos)
    return Sequence(a, b, c)


def __returnToBase(heal):
    toon = heal['toon']
    battle = heal['battle']
    origPos, origHpr = battle.getActorPosHpr(toon)
    runAnimI = ActorInterval(toon, 'run', duration=runHealTime)
    a = Func(toon.headsUp, battle, origPos)
    b = Parallel(runAnimI, LerpPosInterval(toon, runHealTime, origPos, other=battle))
    c = Func(toon.setHpr, battle, origHpr)
    d = Func(toon.loop, 'neutral')
    return Sequence(a, b, c, d)


def __healToon(toon, hp, ineffective, hasInteractivePropHealBonus):
    notify.debug('healToon() - toon: %d hp: %d ineffective: %d' % (toon.doId, hp, ineffective))
    if ineffective == 1:
        laughter = random.choice(TTLocalizer.MovieHealLaughterMisses)
    else:
        maxDam = AvPropDamage[0][1][0][1]
        if hp >= maxDam - 1:
            laughter = random.choice(TTLocalizer.MovieHealLaughterHits2)
        else:
            laughter = random.choice(TTLocalizer.MovieHealLaughterHits1)
    toon.setChatAbsolute(laughter, CFSpeech | CFTimeout)
    toon.toonUp(hp, hasInteractivePropHealBonus)
    return

def __healToonToon(toon, hp, ineffective, hasInteractivePropHealBonus):
    maxDam = AvPropDamage[0][1][0][1]
    if hp >= maxDam - 1:
        laughter = random.choice(TTLocalizer.MovieHealLaughterHits2)
    else:
        laughter = random.choice(TTLocalizer.MovieHealLaughterHits1)
    toon.setChatAbsolute(laughter, CFSpeech | CFTimeout)
    if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
        toon.toonUp(int(math.ceil(hp * .45)), hasInteractivePropHealBonus)
    else:
        toon.toonUp(int(math.ceil(hp * .25)), hasInteractivePropHealBonus)
    return


def __getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    pEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) == 3:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))


def __getSoundTrack(level, delay, duration = None, node = None):
    soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    soundIntervals = Sequence()
    if soundEffect:
        if duration:
            playSound = SoundInterval(soundEffect, duration=duration, node=node)
        else:
            playSound = SoundInterval(soundEffect, node=node)
        soundIntervals.append(Wait(delay))
        soundIntervals.append(playSound)
    return soundIntervals

def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    return Sequence(Wait(delay), SoundInterval(globalBattleSoundCache.getSound(fileName), duration=duration, node=node))


def __healTickle(heal, hasInteractivePropHealBonus):
    toon = heal['toon']
    target = heal['target']['toon']
    hp = heal['target']['hp']
    ineffective = heal['sidestep']
    level = heal['level']
    track = Sequence(__runToHealSpot(heal))
    feather = globalPropPool.getProp('feather')
    feather2 = MovieUtil.copyProp(feather)
    feathers = [feather, feather2]
    hands = toon.getRightHands()

    def scaleFeathers(feathers, toon = toon, target = target):
        toon.pose('tickle', 63)
        toon.update(0)
        hand = toon.getRightHands()[0]
        horizDistance = Vec3(hand.getPos(render) - target.getPos(render))
        horizDistance.setZ(0)
        distance = horizDistance.length()
        if target.style.torso[0] == 's':
            distance -= 0.5
        else:
            distance -= 0.3
        featherLen = 2.4
        scale = distance / (featherLen * hand.getScale(render)[0])
        for feather in feathers:
            feather.setScale(scale)

    tFeatherScaleUp = 0.5
    dFeatherScaleUp = 0.5
    dFeatherScaleDown = 0.5
    featherTrack = Parallel(MovieUtil.getActorIntervals(feathers, 'feather'), Sequence(Wait(tFeatherScaleUp), Func(MovieUtil.showProps, feathers, hands), Func(scaleFeathers, feathers), MovieUtil.getScaleIntervals(feathers, dFeatherScaleUp, MovieUtil.PNT3_NEARZERO, feathers[0].getScale)), Sequence(Wait(toon.getDuration('tickle') - dFeatherScaleDown), MovieUtil.getScaleIntervals(feathers, dFeatherScaleDown, None, MovieUtil.PNT3_NEARZERO)))
    tHeal = 3.0
    heal2 = heal['target']['hp']
    selfHealTrack = Sequence(Wait(tHeal), Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus))
    mtrack = Parallel(featherTrack, ActorInterval(toon, 'tickle'), __getSoundTrack(level, 1, node=toon), Sequence(Wait(tHeal), Parallel(Func(__healToon, target, hp, ineffective, hasInteractivePropHealBonus)), ActorInterval(target, 'cringe', startTime=20.0 / target.getFrameRate('cringe'))))
    track.append(mtrack)
    if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
        track.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
    else:
        track.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
    track.append(Func(MovieUtil.removeProps, feathers))
    track.append(__returnToBase(heal))
    target.setChatAbsolute('', CFSpeech | CFTimeout)
    return Parallel(selfHealTrack, track)

def __healCannon(heal, hasInteractivePropHealBonus):
    toon = heal['toon']
    target = heal['target']['toon']
    ineffective = heal['sidestep']
    level = heal['level']
    hp = heal['target']['hp']
    ineffective = heal['sidestep']
    battle = heal['battle']
    origHpr = toon.getHpr(battle)
    track = Sequence()
    cannon = globalPropPool.getProp('cannon')
    targetTrack = Sequence()
    delay = 4.25
    if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
        targetTrack.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
    else:
        targetTrack.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
    sScale = 0.50
    dScale = 1.1
    hands = toon.getLeftHands()

    if not ineffective:
        particleFile = 'cannonConfetti'
        softStop = -0.7
        fireAnim = 'cannon'
        soundIval = __getSoundTrack(level, delay=2.0, node=toon)
    else:
        particleFile = 'cannonConfettiBad'
        softStop = -1.25
        fireAnim = 'cannon-miss'
        soundSfx = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_fail.ogg')
        soundIval = Sequence(Wait(2), SoundInterval(soundSfx, node=toon))

    confettiEffectPurple = BattleParticles.createParticleEffect(file=particleFile)
    confettiEffectYellow = BattleParticles.createParticleEffect(file=particleFile)
    confettiEffectYellow2 = BattleParticles.createParticleEffect(file=particleFile)

    adjustSfx = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_adjust.ogg')
    adjustSoundIval = SoundInterval(adjustSfx, duration=0.45, node=toon)
    soundIval = Parallel(adjustSoundIval, soundIval)
    growthSfx = base.loader.loadSfx('phase_4/audio/sfx/MG_cannon_growth.ogg')
    growthIval = SoundInterval(growthSfx, node=toon)
    buttonSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')

    purple_p0 = confettiEffectPurple.getParticlesNamed('particles-1')
    purple_p0.renderer.getColorInterpolationManager().addConstant(0.0, 1.3, Vec4(0.20, 0.0, 1.0, 1.0), 1)
    yellow_p0 = confettiEffectYellow.getParticlesNamed('particles-1')
    yellow_p0.renderer.getColorInterpolationManager().addConstant(0.0, 1.3, Vec4(1.0, 1.0, 0.25, 1.0), 1)
    yellow2_p0 = confettiEffectYellow2.getParticlesNamed('particles-1')
    yellow2_p0.renderer.getColorInterpolationManager().addConstant(0.0, 1.3, Vec4(1.0, 1.0, 0.25, 1.0), 1)
    cBIval = __getPartTrack(confettiEffectPurple, 2.1, 1.4, [confettiEffectPurple, cannon, 0], softStop=softStop)
    cRIval = __getPartTrack(confettiEffectYellow, 2.1, 1.4, [confettiEffectYellow, cannon, 0], softStop=softStop)
    cYIval = __getPartTrack(confettiEffectYellow2, 2.1, 1.4, [confettiEffectYellow2, cannon, 0], softStop=softStop)

    confettiTrack = Parallel(cBIval, cRIval, cYIval)

    throwTrack = Parallel(
        Sequence(
            ActorInterval(toon, 'feedPet'),
            Func(toon.loop, 'neutral')),
        Sequence(
            Func(cannon.setScale, dScale),
            Func(cannon.reparentTo, toon.rightHand),
            Wait(2.1),
            Func(cannon.wrtReparentTo, battle),
            Func(cannon.setShear, 0, 0, 0),
            Parallel(
                LerpHprInterval(cannon, hpr=(0, 0, 0), duration=1.2),
                ProjectileInterval(cannon, endPos=(0, -1, 0), duration=1.2, gravityMult=0.45)),
            Wait(0.2),
            Parallel(ActorInterval(cannon, 'cannon-grow'),
                     growthIval,
                     Sequence(LerpScaleInterval(cannon, 0.3, (1.0, 1.0, 0.7)),
                              LerpScaleInterval(cannon, 0.5, dScale)))))

    def cannon180():
        targetPos = target.getPos(battle)
        cannon.lookAt(battle, targetPos)
        cannon.setH(cannon.getH() - 180)

    button = globalPropPool.getProp('heal-button')
    buttons = [button]
    toonTrack = Sequence()
    toonTrack.append(Func(MovieUtil.showProps, buttons, hands))
    toonTrack.append(Func(toon.headsUp, battle))
    toonTrack.append(Parallel(ActorInterval(button, 'heal-button'), ActorInterval(toon, 'pushbutton'), Sequence(Wait(2.3), SoundInterval(buttonSound, duration=0.67, node=toon))))
    toonTrack.append(Func(MovieUtil.removeProps, buttons))
    toonTrack.append(Func(toon.loop, 'neutral'))
    heal2 = heal['target']['hp']
    toonTrack.append(Func(toon.setHpr, battle, origHpr))
    if ineffective:
        reactTrack = Sequence()
    else:
        reactTrack = Sequence(Func(target.doEmote, 20), Wait(3.0))
    fireTrack = Sequence(
        Parallel(
            ActorInterval(cannon, fireAnim), confettiTrack, 
            Sequence(
                Wait(2.5), 
                Parallel(Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus), Func(__healToon, target, hp, ineffective, hasInteractivePropHealBonus)), 
                reactTrack
            )
        )
    )
    mtrack = Sequence(
        Parallel(
            Func(cannon.setScale, sScale), 
            Func(cannon.reparentTo, battle), 
            Func(cannon.setY, 0)
        ), 
        Func(cannon.pose, 'cannon-grow', 1), 
        Parallel(
            throwTrack, 
            Sequence(
                Wait(3.0), 
                Parallel(
                    toonTrack, 
                    Sequence(
                        Wait(2.3), 
                        Parallel(
                            fireTrack, 
                            soundIval, 
                            Func(cannon180)
                        )
                    )
                )
            )
        ), 
        LerpScaleInterval(cannon, 0.2, MovieUtil.PNT3_NEARZERO), 
        Func(MovieUtil.removeProp, cannon)
    )
    track.append(mtrack)
    return track

def __healCannonOLD(heal, hasInteractivePropHealBonus):
    npcId = 0
    if 'npcId' in heal:
        npcId = heal['npcId']
        toon = NPCToons.createLocalNPC(npcId)
        if toon == None:
            return
    else:
        toon = heal['toon']
    toon = heal['toon']
    target = heal['target']['toon']
    ineffective = heal['sidestep']
    level = heal['level']
    track = Sequence(Wait(0.5))
    delay = 4.25
    first = 1
    targetTrack = Sequence()
    hp = heal['target']['hp']
    reactIval = Func(__healToon, target, hp, ineffective, hasInteractivePropHealBonus)
    if first == 1:
        targetTrack.append(Wait(delay))
        first = 0
    heal2 = heal['target']['hp']
    selfHealTrack = Sequence(Wait(delay), Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus))
    targetTrack.append(Parallel(reactIval, ActorInterval(target, 'conked')))
    if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
        targetTrack.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
    else:
        targetTrack.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
    button = globalPropPool.getProp('heal-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    track.append(Func(MovieUtil.showProps, buttons, hands))
    track.append(ActorInterval(toon, 'pushbutton'))
    track.append(Func(MovieUtil.removeProps, buttons))
    track.append(Func(toon.loop, 'neutral'))
    cubes = globalPropPool.getProp('cannon')
    cubes.setPos(Point3(0, MovieUtil.SUIT_TRAP_RAKE_DISTANCE, 0))
    cubes2 = globalPropPool.getProp('cannon2')
    cubes2.setPos(Point3(0, MovieUtil.SUIT_TRAP_RAKE_DISTANCE, 0))
    cubes3 = globalPropPool.getProp('cannon3')
    cubes3.setPos(Point3(0, MovieUtil.SUIT_TRAP_RAKE_DISTANCE, 0))
    ladderOffset = Point3(0, 4, 0)
    ladderPos = render.getRelativePoint(target, ladderOffset)
    #hips = [toon.getLOD(toon.getLODNames()[0]).find('**/joint_hips'), toon.getLOD(toon.getLODNames()[1]).find('**/joint_hips')]
    cubeTrack = Sequence(Func(MovieUtil.showProp, cubes, target), ActorInterval(cubes, 'cannon'), Func(MovieUtil.removeProp, cubes),
                         Func(MovieUtil.showProp, cubes2, target), ActorInterval(cubes2, 'cannon2'), Func(MovieUtil.removeProp, cubes2))
    cubeTrack2 = Sequence(Func(MovieUtil.showProp, cubes, target), ActorInterval(cubes, 'cannon'), Func(MovieUtil.removeProp, cubes),
                         Func(MovieUtil.showProp, cubes3, target), ActorInterval(cubes3, 'cannon3'), Func(MovieUtil.removeProp, cubes3))
    mtrack = Parallel(cubeTrack, Sequence(getSoundTrack('MG_cannon_growth.ogg', node=toon),
                                          getSoundTrack('MG_cannon_adjust.ogg', node=toon),
                                          getSoundTrack('MG_cannon_confetti.ogg', node=toon)), targetTrack)
    mtrack2 = Parallel(cubeTrack2, Sequence(getSoundTrack('MG_cannon_growth.ogg', node=toon),
                                            getSoundTrack('MG_cannon_adjust.ogg', node=toon),
                                            getSoundTrack('MG_cannon_fail.ogg', node=toon)), targetTrack)

    target.setChatAbsolute('', CFSpeech | CFTimeout)
    track.append(Wait(2.0))
    maxDam = AvPropDamage[0][1][0][1]
    if hp >= maxDam - 1:
        return Parallel(track, mtrack, selfHealTrack)
    else:
        return Parallel(track, mtrack2, selfHealTrack)


def __healJoke(heal, hasInteractivePropHealBonus):
    npcId = 0
    if 'npcId' in heal:
        npcId = heal['npcId']
        toon = NPCToons.createLocalNPC(npcId)
        if toon == None:
            return
    else:
        toon = heal['toon']
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']
    jokeIndex = heal['hpbonus'] % len(HealJokes.toonHealJokes)
    if npcId != 0:
        track = Sequence(MovieNPCSOS.teleportIn(heal, toon))
    else:
        track = Sequence(__runToHealSpot(heal))
    tracks = Parallel()
    fSpeakPunchline = 58
    tSpeakSetup = 0.0
    tSpeakPunchline = 3.0
    dPunchLine = 3.0
    tTargetReact = tSpeakPunchline + 1.0
    dTargetLaugh = 1.5
    tRunBack = tSpeakPunchline + dPunchLine
    tDoSoundAnimation = tSpeakPunchline - float(fSpeakPunchline) / toon.getFrameRate('sound')
    megaphone = globalPropPool.getProp('megaphone')
    megaphone2 = MovieUtil.copyProp(megaphone)
    megaphones = [megaphone, megaphone2]
    hands = toon.getRightHands()
    dMegaphoneScale = 0.5
    tracks.append(Sequence(Wait(tDoSoundAnimation), Func(MovieUtil.showProps, megaphones, hands), MovieUtil.getScaleIntervals(megaphones, dMegaphoneScale, MovieUtil.PNT3_NEARZERO, MovieUtil.PNT3_ONE), Wait(toon.getDuration('sound') - 2.0 * dMegaphoneScale), MovieUtil.getScaleIntervals(megaphones, dMegaphoneScale, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, megaphones)))
    tracks.append(Sequence(Wait(tDoSoundAnimation), ActorInterval(toon, 'sound')))
    soundTrack = __getSoundTrack(level, 2.0, node=toon)
    tracks.append(soundTrack)
    joke = HealJokes.toonHealJokes[jokeIndex]
    tracks.append(Sequence(Wait(tSpeakSetup), Func(toon.setChatAbsolute, joke[0], CFSpeech | CFTimeout)))
    tracks.append(Sequence(Wait(tSpeakPunchline), Func(toon.setChatAbsolute, joke[1], CFSpeech | CFTimeout)))
    reactTrack = Sequence(Wait(tTargetReact))
    heal2 = heal['target'][0]['hp']
    selfHealTrack = Sequence(Wait(tTargetReact), Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus))
    for target in targets:
        targetToon = target['toon']
        hp = target['hp']
        if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
            reactTrack.append(Parallel(Func(targetToon.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
        else:
            reactTrack.append(Parallel(Func(targetToon.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
        reactTrack.append(Func(__healToon, targetToon, hp, ineffective, hasInteractivePropHealBonus))

    reactTrack.append(Wait(dTargetLaugh))
    for target in targets:
        targetToon = target['toon']
        targetToon.setChatAbsolute('', CFSpeech | CFTimeout)

    tracks.append(reactTrack)
    if npcId != 0:
        track.append(Sequence(Wait(tRunBack), Func(toon.clearChat), *MovieNPCSOS.teleportOut(heal, toon)))
    else:
        tracks.append(Sequence(Wait(tRunBack), Func(toon.clearChat), *__returnToBase(heal)))
    track.append(tracks)
    return Parallel(selfHealTrack, track)


def __healSmooch(heal, hasInteractivePropHealBonus):
    toon = heal['toon']
    target = heal['target']['toon']
    level = heal['level']
    hp = heal['target']['hp']
    ineffective = heal['sidestep']
    track = Sequence(__runToHealSpot(heal))
    lipstick = globalPropPool.getProp('lipstick')
    lipstick2 = MovieUtil.copyProp(lipstick)
    lipsticks = [lipstick, lipstick2]
    rightHands = toon.getRightHands()
    dScale = 0.5
    lipstickTrack = Sequence(Func(MovieUtil.showProps, lipsticks, rightHands, Point3(-0.27, -0.24, -0.95), Point3(-118, -10.6, -25.9)), 
                             MovieUtil.getScaleIntervals(lipsticks, dScale, MovieUtil.PNT3_NEARZERO, MovieUtil.PNT3_ONE), Wait(toon.getDuration('smooch') - 2.0 * dScale), 
                             MovieUtil.getScaleIntervals(lipsticks, dScale, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, lipsticks))
    lips = globalPropPool.getProp('lips')
    dScale = 0.5
    tLips = 2.5
    tThrow = 115.0 / toon.getFrameRate('smooch')
    dThrow = 0.5

    def getLipPos(toon = toon):
        toon.pose('smooch', 57)
        toon.update(0)
        hand = toon.getRightHands()[0]
        return hand.getPos(render)

    lipsTrack = Sequence(Wait(tLips), Func(MovieUtil.showProp, lips, render, getLipPos), Func(lips.setBillboardPointWorld), 
                         LerpScaleInterval(lips, dScale, Point3(3, 3, 3), startScale=MovieUtil.PNT3_NEARZERO), Wait(tThrow - tLips - dScale), 
                         LerpPosInterval(lips, dThrow, Point3(target.getPos() + Point3(0, 0, target.getHeight()))), Func(MovieUtil.removeProp, lips))
    delay = tThrow + dThrow
    heal2 = heal['target']['hp']
    selfHealTrack = Sequence(Wait(delay), Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus))
    mtrack = Parallel(lipstickTrack, lipsTrack, __getSoundTrack(level, 2, node=toon), Sequence(ActorInterval(toon, 'smooch'), *__returnToBase(heal)),
                       Sequence(Wait(delay), ActorInterval(target, 'conked')), Sequence(Wait(delay), Parallel(Func(__healToon, target, hp, ineffective, hasInteractivePropHealBonus))))
    track.append(Parallel(selfHealTrack, mtrack))
    if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
        track.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
    else:
        track.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
    target.setChatAbsolute('', CFSpeech | CFTimeout)
    return Parallel(track)


def __healDance(heal, hasInteractivePropHealBonus):
    npcId = 0
    if 'npcId' in heal:
        npcId = heal['npcId']
        toon = NPCToons.createLocalNPC(npcId)
        if toon == None:
            return
    else:
        toon = heal['toon']
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']
    if npcId != 0:
        track = Sequence(MovieNPCSOS.teleportIn(heal, toon))
    else:
        track = Sequence(__runToHealSpot(heal))
    delay = 3.0
    first = 1
    heal2 = heal['target'][0]['hp']
    selfHealTrack = Sequence(Wait(delay), Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus))
    targetTrack = Sequence()
    for target in targets:
        targetToon = target['toon']
        hp = target['hp']
        reactIval = Parallel(Func(__healToon, targetToon, hp, ineffective, hasInteractivePropHealBonus))
        if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
            reactIval.append(Parallel(Func(targetToon.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
        else:
            reactIval.append(Parallel(Func(targetToon.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
        if first:
            targetTrack.append(Wait(delay))
            first = 0
        targetTrack.append(reactIval)

    hat = globalPropPool.getProp('hat')
    hat2 = MovieUtil.copyProp(hat)
    hats = [hat, hat2]
    cane = globalPropPool.getProp('cane')
    cane2 = MovieUtil.copyProp(cane)
    canes = [cane, cane2]
    leftHands = toon.getLeftHands()
    rightHands = toon.getRightHands()
    dScale = 0.5
    propTrack = Sequence(Func(MovieUtil.showProps, hats, rightHands, Point3(0.23, 0.09, 0.69), Point3(180, 0, 0)), Func(MovieUtil.showProps, canes, leftHands, Point3(-0.28, 0.0, 0.14), Point3(0.0, 0.0, -150.0)), MovieUtil.getScaleIntervals(hats + canes, dScale, MovieUtil.PNT3_NEARZERO, MovieUtil.PNT3_ONE), Wait(toon.getDuration('happy-dance') - 2.0 * dScale), MovieUtil.getScaleIntervals(hats + canes, dScale, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProps, hats + canes))
    mtrack = Parallel(propTrack, ActorInterval(toon, 'happy-dance'), __getSoundTrack(level, 0.2, duration=6.4, node=toon), targetTrack)
    track.append(Func(toon.loop, 'neutral'))
    track.append(Wait(0.1))
    track.append(Parallel(selfHealTrack, mtrack))
    if npcId != 0:
        track.append(MovieNPCSOS.teleportOut(heal, toon))
    else:
        track.append(__returnToBase(heal))
    for target in targets:
        targetToon = target['toon']
        targetToon.setChatAbsolute('', CFSpeech | CFTimeout)

    return Parallel(track)


def __healSprinkle(heal, hasInteractivePropHealBonus):
    toon = heal['toon']
    target = heal['target']['toon']
    hp = heal['target']['hp']
    ineffective = heal['sidestep']
    level = heal['level']
    track = Sequence(__runToHealSpot(heal))
    sprayEffect = BattleParticles.createParticleEffect(file='pixieSpray')
    dropEffect = BattleParticles.createParticleEffect(file='pixieDrop')
    explodeEffect = BattleParticles.createParticleEffect(file='pixieExplode')
    poofEffect = BattleParticles.createParticleEffect(file='pixiePoof')
    wallEffect = BattleParticles.createParticleEffect(file='pixieWall')

    def face90(toon = toon, target = target):
        vec = Point3(target.getPos() - toon.getPos())
        vec.setZ(0)
        temp = vec[0]
        vec.setX(-vec[1])
        vec.setY(temp)
        targetPoint = Point3(toon.getPos() + vec)
        toon.headsUp(render, targetPoint)

    delay = 2.5
    heal2 = heal['target']['hp']
    selfHealTrack = Sequence(Wait(delay), Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus))
    mtrack = Parallel(__getPartTrack(sprayEffect, 1.5, 0.5, [sprayEffect, toon, 0]), __getPartTrack(dropEffect, 1.9, 2.0, [dropEffect, target, 0]), __getPartTrack(explodeEffect, 2.7, 1.0, [explodeEffect, toon, 0]), __getPartTrack(poofEffect, 3.4, 1.0, [poofEffect, target, 0]), __getPartTrack(wallEffect, 4.05, 1.2, [wallEffect, toon, 0]), __getSoundTrack(level, 2, duration=4.1, node=toon), Sequence(Func(face90), ActorInterval(toon, 'sprinkle-dust')), Sequence(Wait(delay), Parallel(Func(__healToon, target, hp, ineffective, hasInteractivePropHealBonus))))
    track.append(Parallel(selfHealTrack, mtrack))
    if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
        track.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
    else:
        track.append(Parallel(Func(target.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
    track.append(__returnToBase(heal))
    target.setChatAbsolute('', CFSpeech | CFTimeout)
    return Parallel(track)


def __healJuggle(heal, hasInteractivePropHealBonus):
    npcId = 0
    if 'npcId' in heal:
        npcId = heal['npcId']
        toon = NPCToons.createLocalNPC(npcId)
        if toon == None:
            return
    else:
        toon = heal['toon']
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']
    if npcId != 0:
        track = Sequence(MovieNPCSOS.teleportIn(heal, toon))
    else:
        track = Sequence(__runToHealSpot(heal))
    delay = 4.0
    first = 1
    
    targetTrack = Sequence()
    for target in targets:
        targetToon = target['toon']
        hp = target['hp']
        reactIval = Parallel(Func(__healToon, targetToon, hp, ineffective, hasInteractivePropHealBonus))
        if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
            reactIval.append(Parallel(Func(targetToon.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
        else:
            reactIval.append(Parallel(Func(targetToon.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
        if first == 1:
            targetTrack.append(Wait(delay))
            first = 0
        targetTrack.append(reactIval)
    heal2 = heal['target'][0]['hp']
    selfHealTrack = Sequence(Wait(delay), Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus))
    cube = globalPropPool.getProp('cubes')
    cube2 = MovieUtil.copyProp(cube)
    cubes = [cube, cube2]
    hips = [toon.getLOD(toon.getLODNames()[0]).find('**/joint_hips'), toon.getLOD(toon.getLODNames()[1]).find('**/joint_hips')]
    cubeTrack = Sequence(Func(MovieUtil.showProps, cubes, hips), MovieUtil.getActorIntervals(cubes, 'cubes'), Func(MovieUtil.removeProps, cubes))
    mtrack = Parallel(cubeTrack, __getSoundTrack(level, 0.7, duration=7.7, node=toon), ActorInterval(toon, 'juggle'), targetTrack)
    track.append(Parallel(selfHealTrack, mtrack))
    if npcId != 0:
        track.append(MovieNPCSOS.teleportOut(heal, toon))
    else:
        track.append(__returnToBase(heal))
    for target in targets:
        targetToon = target['toon']
        targetToon.setChatAbsolute('', CFSpeech | CFTimeout)

    return Parallel(track)


def __healDive(heal, hasInteractivePropHealBonus):
    splash = Splash.Splash(render)
    splash.reparentTo(render)
    npcId = 0
    if 'npcId' in heal:
        npcId = heal['npcId']
        toon = NPCToons.createLocalNPC(npcId)
        if toon == None:
            return
    else:
        toon = heal['toon']
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']
    if npcId != 0:
        track = Sequence(MovieNPCSOS.teleportIn(heal, toon))
    else:
        track = Sequence(__runToHealSpot(heal))
    delay = 7.0
    first = 1
    targetTrack = Sequence()
    heal2 = heal['target'][0]['hp']
    selfHealTrack = Sequence(Wait(delay), Func(__healToonToon, toon, heal2, ineffective, hasInteractivePropHealBonus))
    for target in targets:
        targetToon = target['toon']
        hp = target['hp']
        reactIval = Parallel(Func(__healToon, targetToon, hp, ineffective, hasInteractivePropHealBonus))
        if toon.getTrackBonusLevel(HEAL_TRACK) > 1:
            reactIval.append(Parallel(Func(targetToon.setToonStatusEffect, 'cheer', modifier=2, turns=2)))
        else:
            reactIval.append(Parallel(Func(targetToon.setToonStatusEffect, 'cheer', modifier=1, turns=1)))
        if first == 1:
            targetTrack.append(Wait(delay))
            first = 0
        targetTrack.append(reactIval)

    thisBattle = heal['battle']
    toonsInBattle = thisBattle.toons
    glass = globalPropPool.getProp('glass')
    glass.setHpr(0.0, 90.0, 0.0)
    ladder = globalPropPool.getProp('ladder')
    placeNode = NodePath('lookNode')
    diveProps = [glass, ladder]
    ladderScale = toon.getBodyScale() / 0.66
    scaleUpPoint = Point3(0.5, 0.5, 0.45) * ladderScale
    basePos = toon.getPos()

    glassOffset = Point3(0.3, 1.0, 0.4)
    glassToonOffset = Point3(0, 1.0, 0.4)
    splashOffset = Point3(0, 1.0, 0.4)
    ladderOffset = Point3(0, 4, 0)
    ladderToonSep = Point3(0, 1, 0) * ladderScale
    diveOffset = Point3(0, 0, 10)
    divePos = add3(add3(ladderOffset, diveOffset), ladderToonSep)
    ladder.setH(toon.getH())

    glassPos = render.getRelativePoint(toon, glassOffset)
    glassToonPos = render.getRelativePoint(toon, glassToonOffset)
    ladderPos = render.getRelativePoint(toon, ladderOffset)
    climbladderPos = render.getRelativePoint(toon, add3(ladderOffset, ladderToonSep))
    divePos = render.getRelativePoint(toon, divePos)
    topDivePos = render.getRelativePoint(toon, diveOffset)
    lookBase = render.getRelativePoint(toon, ladderOffset)
    lookTop = render.getRelativePoint(toon, add3(ladderOffset, diveOffset))
    LookGlass = render.getRelativePoint(toon, glassOffset)
    splash.setPos(splashOffset)
    walkToLadderTime = 1.0
    climbTime = 5.0
    diveTime = 1.0
    ladderGrowTime = 1.5
    splash.setPos(glassPos)
    toonNode = toon.getGeomNode()
    placeNode.reparentTo(render)
    placeNode.setScale(5.0)
    placeNode.setPos(toon.getPos(render))
    placeNode.setHpr(toon.getHpr(render))
    toonscale = toonNode.getScale()
    toonFacing = toon.getHpr()
    propTrack = Sequence(Func(MovieUtil.showProp, glass, render, glassPos), Func(MovieUtil.showProp, ladder, render, ladderPos), Func(toonsLook, toonsInBattle, placeNode, Point3(0, 0, 0)), Func(placeNode.setPos, lookBase), LerpScaleInterval(ladder, ladderGrowTime, scaleUpPoint, startScale=MovieUtil.PNT3_NEARZERO), Func(placeNode.setPos, lookTop), Wait(2.1), MovieCamera.toonGroupHighShot(None, 0), Wait(2.1), Func(placeNode.setPos, LookGlass), Wait(0.4), MovieCamera.allGroupLowShot2(None, 0), Wait(1.8), LerpScaleInterval(ladder, ladderGrowTime, MovieUtil.PNT3_NEARZERO, startScale=scaleUpPoint), Func(MovieUtil.removeProps, diveProps))
    mtrack = Parallel(propTrack, __getSoundTrack(level, 0.6, duration=9.0, node=toon), Sequence(Parallel(Sequence(ActorInterval(toon, 'walk', loop=0, duration=walkToLadderTime), ActorInterval(toon, 'neutral', loop=0, duration=0.1)), LerpPosInterval(toon, walkToLadderTime, climbladderPos), Wait(ladderGrowTime)), Parallel(ActorInterval(toon, 'climb', loop=0, endFrame=116), Sequence(Wait(4.6), Func(toonNode.setTransparency, 1), LerpColorScaleInterval(toonNode, 0.25, VBase4(1, 1.0, 1, 0.0), blendType='easeInOut'), LerpScaleInterval(toonNode, 0.01, 0.1, startScale=toonscale), LerpHprInterval(toon, 0.01, toonFacing), LerpPosInterval(toon, 0.0, glassToonPos), Func(toonNode.clearTransparency), Func(toonNode.clearColorScale), Parallel(ActorInterval(toon, 'swim', loop=1, startTime=0.0, endTime=1.0), Wait(1.0))), Sequence(Wait(4.6), Func(splash.play), Wait(1.0), Func(splash.destroy))), Wait(0.5), Parallel(ActorInterval(toon, 'jump', loop=0, startTime=0.2), LerpScaleInterval(toonNode, 0.5, toonscale, startScale=0.1), Func(stopLook, toonsInBattle))), targetTrack)
    track.append(Parallel(selfHealTrack, mtrack))
    if npcId != 0:
        track.append(MovieNPCSOS.teleportOut(heal, toon))
    else:
        track.append(__returnToBase(heal))
    for target in targets:
        targetToon = target['toon']
        targetToon.setChatAbsolute('', CFSpeech | CFTimeout)

    return Parallel(track)


def add3(t1, t2):
    returnThree = Point3(t1[0] + t2[0], t1[1] + t2[1], t1[2] + t2[2])
    return returnThree


def stopLook(toonsInBattle):
    for someToon in toonsInBattle:
        someToon.stopStareAt()


def toonsLook(toons, someNode, offset):
    for someToon in toons:
        someToon.startStareAt(someNode, offset)
