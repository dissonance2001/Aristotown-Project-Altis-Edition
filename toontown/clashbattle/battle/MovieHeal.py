from direct.interval.IntervalGlobal import *
from toontown.clashbattle.battle.BattleBase import *
from toontown.clashbattle.battle import BattleParticles
from toontown.clashbattle.battle.BattleProps import *
from toontown.clashbattle.battle.BattleSounds import *
from toontown.clashbattle.battle import MovieUtil
from otp import *
from toontown.chat.constants.ChatGlobals import CFSpeech, CFQuicktalker, CFTimeout
from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.effects import Splash
from toontown.gui.game.condition import ConditionGlobals
from toontown.toonbase import TTLocalizer
from toontown.clashbattle.battle.BattleGlobals import AvPropDamage
from toontown.utils.DirectNotifyCategory import getNotify
from toontown.chat.enums.ChatChannel import ChatChannel
from toontown.chat.enums.ChatContentType import ChatContentType
from toontown.chat.enums.ChatZoneModifier import ChatZoneModifier

notify = getNotify('MovieHeal')

soundFiles  = ('AA_heal_tickle.ogg',
              'AA_heal_telljoke.ogg',
              'AA_heal_smooch.ogg',
              'AA_heal_happydance.ogg',
              'AA_heal_pixiedust.ogg', 
              'AA_heal_juggle.ogg',
              'MG_cannon_confetti.ogg',
              'AA_heal_High_Dive.ogg')
              
healPos         = Point3(0, 0, 0)   # Position relative to battle where Toon runs to Toon-Up
healPosOffset   = Point3(0, -2.8, 0)# Position for Toon to run to when offset. Used by high-dive
healHpr         = Vec3(180.0, 0, 0) # Relative rotation Toon should take when reaching healPos
runHealTime     = 1.0               # Time, in seconds, it takes for Toon to run to healPos

def doHeals(heals, hasInteractivePropHealBonus):
    """ doHeals(heals)
        Heals occur in the following order:
        1) level 1 heals one at a time, from right to left
        2) level 2 heals one at a time, from right to left
        etc.
    """
    if len(heals) == 0:
        return (None, None)
    track = Sequence()
    for h in heals:
        ival = __doHealLevel(h, hasInteractivePropHealBonus)
        if ival:
            def broadcastHeals():
                for targets in h.get('target', []):
                    messenger.send(ConditionGlobals.AskIconMsg, [targets.get('avatar'),
                                   ConditionGlobals.ConditionIconType.HEAL_ARROW])

            track.append(Sequence(Func(broadcastHeals), ival))

    camDuration = track.getDuration()
    camTrack = heals[0]['battle'].camera.chooseHealShot(heals, camDuration)
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


def __runToHealSpot(heal, offset = False):
    """ Generates a track that does the following:
        a) Face the heal spot
        b) Run to the heal spot
        c) Turn to face the target
    """
    toon = heal["avatar"]
    battle = heal['battle']
    level = heal['level']
    if offset:
        pos = healPosOffset
    else:
        pos = healPos
    a = Func(toon.headsUp, battle, pos)
    b = Parallel(Func(toon.loop, 'run'), LerpPosInterval(toon, runHealTime, pos, other=battle))

    # For group heals, face the center of the group
    if levelAffectsGroup(AttackEnum.TOON_HEAL, level):
        c = Func(toon.setHpr, battle, healHpr)
    else:
        # For single heals, face the target toon
        target = heal['target'][0]["avatar"]
        targetPos = target.getPos(battle)
        c = Func(toon.headsUp, battle, targetPos)
    return Sequence(a, b, c)


def __returnToBase(heal):
    """ Generates a track that does the following:
        a) Face the toons starting place
        b) Run to the starting place
        c) Turn to face the center of the battle
    """
    toon = heal["avatar"]
    battle = heal['battle']
    origPos, origHpr = battle.getActorPosHpr(toon)
    a = Func(toon.headsUp, battle, origPos)
    b = Parallel(Func(toon.loop, 'run'), LerpPosInterval(toon, runHealTime, origPos, other=battle))
    c = Func(toon.setHpr, battle, origHpr)
    d = Func(toon.loop, 'neutral')
    return Sequence(a, b, c, d)


def __healToon(toon, invoker, hp, ineffective, hasInteractivePropHealBonus, wantLaugh: bool=True):
    notify.debug('healToon() - toon: %d hp: %d ineffective: %d' % (toon.doId, hp, ineffective))
    cappedHp = min(toon.getMaxHp() - toon.getHp(), hp)
    if wantLaugh:
        if ineffective == 1:
            laughter = random.choice(TTLocalizer.MovieHealLaughterMisses)
        else:
            maxDam = AvPropDamage[0][1][0][1]
            if cappedHp >= maxDam - 1:
                laughter = random.choice(TTLocalizer.MovieHealLaughterHits2)
            else:
                laughter = random.choice(TTLocalizer.MovieHealLaughterHits1)
        toon.setChatAbsolute(laughter, CFSpeech | CFQuicktalker | CFTimeout)
    if not ineffective and toon != invoker:
        MovieUtil.applyVisualEffect(toon, VisualEffectEnum.CHEER)
    if toon.getHp() is not None:
        toon.toonUp(cappedHp, hasInteractivePropHealBonus)
    else:
        notify.debug('__healToon() - toon: %d hp: %d' % (toon.doId, hp))
    return


def __getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop=0):
    """ This function returns the default particle track for a suit attack
        animation. 
        Arguments:
            startDelay      = Time delay before particle effect begins
            durationDelay   = Time delay before particles are cleaned up
            partExtraArgs   = extraArgs for startParticleEffect function, the first
            softStop        = Time it should take for particles to fade out smoothly. Unused currently.
            element of which is always the particle effect (function relies on this)
    """
    pEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) == 3:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))


def __getSoundTrack(level, delay, duration = None, node = None, override = None):
    # level: The level of attack, int 0-7
    # delay: Time delay before playing sound

    if not override:
        soundEffect = globalBattleSoundCache.getSound(soundFiles[level])
    else:
        soundEffect = globalBattleSoundCache.getSound(override)

    soundIntervals = Sequence()

    if soundEffect:
        if duration:
            playSound = SoundInterval(soundEffect, duration=duration, node=node)
        else:
            playSound = SoundInterval(soundEffect, node=node)
        soundIntervals.append(Wait(delay))
        soundIntervals.append(playSound)

    return soundIntervals


def __healTickle(heal, hasInteractivePropHealBonus):
    toon = heal["avatar"]
    target = heal['target'][0]["avatar"]
    hp = heal['target'][0]['hp']
    ineffective = heal['sidestep']
    level = heal['level']
    
    # Make a 'sandwich' around the track specific interval
    track = Sequence(__runToHealSpot(heal))
    feather = globalPropPool.getProp('feather')
    feathers = [feather]
    hands = toon.getRightHands()

    def scaleFeathers(feathers, toon = toon, target = target):
        toon.pose('tickle', 63)
        toon.update(0) # Make sure LOD 0 is posed
        hand = toon.getRightHands()[0]
        horizDistance = Vec3(hand.getPos(render) - target.getPos(render))
        horizDistance.setZ(0)
        distance = horizDistance.length()
        if target.style.torso[0] == 's':
            distance -= 0.5 # For fat Toons
        else:
            distance -= 0.3 # For skinny Toons
        featherLen = 2.4
        scale = distance / (featherLen * hand.getScale(render)[0])
        for feather in feathers:
            feather.setScale(scale)

    tFeatherScaleUp = 0.5
    dFeatherScaleUp = 0.5
    dFeatherScaleDown = 0.5
    featherTrack = Parallel(MovieUtil.getActorIntervals(feathers, 'feather'),
                            Sequence(Wait(tFeatherScaleUp),
                                     Func(MovieUtil.showProps, feathers, hands),
                                     Func(scaleFeathers, feathers),
                                     MovieUtil.getScaleIntervals(feathers, dFeatherScaleUp, MovieUtil.PNT3_NEARZERO, feathers[0].getScale)),
                            Sequence(Wait(toon.getDuration('tickle') - dFeatherScaleDown),
                                     MovieUtil.getScaleIntervals(feathers, dFeatherScaleDown, None, MovieUtil.PNT3_NEARZERO)))
    tHeal = 3.0
    invokerHeal = tHeal + track.getDuration()

    mtrack = Parallel(featherTrack,
                      ActorInterval(toon, 'tickle'),
                      __getSoundTrack(level, 1, node=toon),
                      Sequence(Wait(tHeal),
                               Func(__healToon, target, toon, hp, ineffective, hasInteractivePropHealBonus),
                               ActorInterval(target, 'cringe', startTime=20.0 / target.getFrameRate('cringe')),
                               Func(target.loop, 'neutral')))

    track.append(mtrack)
    track.append(Func(MovieUtil.removeProps, feathers))
    track.append(__returnToBase(heal))
    if len(heal['target']) > 1:
        pHp = heal['target'][1]['hp']
        track = Parallel(
            track,
            Sequence(
                Wait(invokerHeal),
                Func(__healToon, toon, toon, pHp, ineffective, hasInteractivePropHealBonus)
            )
        )
    return track


def __healJoke(heal, hasInteractivePropHealBonus):
    toon = heal["avatar"]
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']
    if heal['extraArgs']:
        jokeIndex = heal['extraArgs'][0] % len(TTLocalizer.ToonHealJokes)
    else:
        jokeIndex = 0

    # Make a 'sandwich' around the track specific interval
    track = Sequence(__runToHealSpot(heal))

    # SStart a multitrack
    tracks = Parallel()
    
    # Frame which the Toon says the punchline
    fSpeakPunchline = 58

    tSpeakSetup = 0.0
    tSpeakPunchline = 3.0
    dPunchLine = 3.0
    tTargetReact = tSpeakPunchline + 1.0
    dTargetLaugh = 1.5
    tRunBack = tSpeakPunchline + dPunchLine
    tDoSoundAnimation = tSpeakPunchline - float(fSpeakPunchline) / toon.getFrameRate('sound')

    # Megaphone track
    megaphone = globalPropPool.getProp('megaphone')
    megaphones = [megaphone]
    hands = toon.getRightHands()

    dMegaphoneScale = 0.5

    tracks.append(Sequence(Wait(tDoSoundAnimation),
                           Func(MovieUtil.showProps, megaphones, hands),
                           MovieUtil.getScaleIntervals(megaphones, dMegaphoneScale, MovieUtil.PNT3_NEARZERO, MovieUtil.PNT3_ONE),
                           Wait(toon.getDuration('sound') - 2.0 * dMegaphoneScale),
                           MovieUtil.getScaleIntervals(megaphones, dMegaphoneScale, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO),
                           Func(MovieUtil.removeProps, megaphones)))
                           
    # Toon Track
    tracks.append(Sequence(Wait(tDoSoundAnimation),
                           ActorInterval(toon, 'sound')))
                           
    # Sound Track
    soundTrack = __getSoundTrack(level, 2.0, node=toon)
    tracks.append(soundTrack)
    
    # Joke chat track
    joke = TTLocalizer.ToonHealJokes[jokeIndex]
    # The set-up
    tracks.append(Sequence(Wait(tSpeakSetup),
                           Func(toon.setChatAbsolute, joke[0], CFSpeech | CFQuicktalker | CFTimeout),
                           Func(base.cr.chatManager.receiveChatMessage, ChatChannel.Zone, ChatZoneModifier.Normal, ChatContentType.Text, joke[0], toon.doId, toon.getName())))
    # The punchline
    tracks.append(Sequence(Wait(tSpeakPunchline),
                           Func(toon.setChatAbsolute, joke[1], CFSpeech | CFQuicktalker | CFTimeout),
                           Func(base.cr.chatManager.receiveChatMessage, ChatChannel.Zone, ChatZoneModifier.Normal, ChatContentType.Text, joke[1], toon.doId, toon.getName())))
    
    # Toon reaction Track
    reactTrack = Sequence(Wait(tTargetReact))
    for target in targets:
        targetToon = target["avatar"]
        hp = target['hp']
        reactTrack.append(
            Func(__healToon, targetToon, toon, hp, ineffective, hasInteractivePropHealBonus, wantLaugh=targetToon != toon)
        )

    reactTrack.append(Wait(dTargetLaugh))
    for target in targets:
        targetToon = target["avatar"]
    tracks.append(reactTrack)
    
    # just have the Toon run back
    tracks.append(Sequence(Wait(tRunBack), *__returnToBase(heal)))
                      
    # Lay down the multitrack
    track.append(tracks)

    return track


def __healSmooch(heal, hasInteractivePropHealBonus):
    toon = heal["avatar"]
    target = heal['target'][0]["avatar"]
    level = heal['level']
    hp = heal['target'][0]['hp']
    ineffective = heal['sidestep']

    # Make a 'sandwich' around the track specific interval
    track = Sequence(__runToHealSpot(heal))

    lipstick = globalPropPool.getProp('lipstick')
    lipsticks = [lipstick]
    rightHands = toon.getRightHands()
    dScale = 0.5
    lipstickTrack = Sequence(Func(MovieUtil.showProps, lipsticks, rightHands, Point3(-0.27, -0.24, -0.95), Point3(-118, -10.6, -25.9)),
                             MovieUtil.getScaleIntervals(lipsticks, dScale, MovieUtil.PNT3_NEARZERO, MovieUtil.PNT3_ONE),
                             Wait(toon.getDuration('smooch') - 2.0 * dScale),
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

    lipsTrack = Sequence(Wait(tLips),
                         Func(MovieUtil.showProp, lips, render, getLipPos),
                         Func(lips.setBillboardPointWorld),
                         LerpScaleInterval(lips, dScale, Point3(3, 3, 3), startScale=MovieUtil.PNT3_NEARZERO),
                         Wait(tThrow - tLips - dScale),
                         LerpPosInterval(lips, dThrow, Point3(target.getPos() + Point3(0, 0, target.getHeight()))),
                         Func(MovieUtil.removeProp, lips))
 
    delay = tThrow + dThrow
    mtrack = Parallel(lipstickTrack,
                      lipsTrack,
                      __getSoundTrack(level, 2, node=toon),
                      Sequence(ActorInterval(toon, 'smooch'), *__returnToBase(heal)),
                      Sequence(Wait(delay),
                               Func(__healToon, target, toon, hp, ineffective, hasInteractivePropHealBonus),
                               ActorInterval(target, 'conked'),
                               Func(target.loop, 'neutral')))
    tHeal = track.getDuration()
    track.append(mtrack)
    if len(heal['target']) > 1:
        pHp = heal['target'][1]['hp']
        track = Parallel(
            track,
            Sequence(
                Wait(tHeal + delay),
                Func(__healToon, toon, toon, pHp, ineffective, hasInteractivePropHealBonus)
            )
        )
    return track


def __healDance(heal, hasInteractivePropHealBonus):
    toon = heal["avatar"]
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']

    # Make a 'sandwich' around the track specific interval
    track = Sequence(__runToHealSpot(heal))

    delay = 3.0
    first = 1
    targetTrack = Sequence()
    for target in targets:
        targetToon = target["avatar"]
        hp = target['hp']
        reactIval = Func(__healToon, targetToon, toon, hp, ineffective, hasInteractivePropHealBonus)
        if first:
            targetTrack.append(Wait(delay))
            first = 0
        targetTrack.append(reactIval)

    hat = globalPropPool.getProp('hat')
    hats = [hat]
    cane = globalPropPool.getProp('cane')
    canes = [cane]
    leftHands = toon.getLeftHands()
    rightHands = toon.getRightHands()
    dScale = 0.5
    propTrack = Sequence(Func(MovieUtil.showProps, hats, rightHands, Point3(0.23, 0.09, 0.69), Point3(180, 0, 0)),
                         Func(MovieUtil.showProps, canes, leftHands, Point3(-0.28, 0.0, 0.14), Point3(0.0, 0.0, -150.0)),
                         MovieUtil.getScaleIntervals(hats + canes, dScale, MovieUtil.PNT3_NEARZERO, MovieUtil.PNT3_ONE),
                         Wait(toon.getDuration('happy-dance') - 2.0 * dScale),
                         MovieUtil.getScaleIntervals(hats + canes, dScale, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO),
                         Func(MovieUtil.removeProps, hats + canes))
    mtrack = Parallel(propTrack,
                      ActorInterval(toon, 'happy-dance'),
                      __getSoundTrack(level, 0.2, duration=6.4, node=toon),
                      targetTrack)

    # Wait a split second before dancing
    track.append(Func(toon.loop, 'neutral'))
    track.append(Wait(0.1))
    tHeal = track.getDuration()
    track.append(mtrack)
    
    # just have the Toon run back
    track.append(__returnToBase(heal))
    for target in targets:
        targetToon = target["avatar"]

    return track


def __healSprinkle(heal, hasInteractivePropHealBonus):
    toon = heal["avatar"]
    target = heal['target'][0]["avatar"]
    hp = heal['target'][0]['hp']
    ineffective = heal['sidestep']
    level = heal['level']
    
    # Make a 'sandwich' around the track specific interval
    track = Sequence(__runToHealSpot(heal))
    
    sprayEffect     = BattleParticles.createParticleEffect(file='pixieSpray')
    dropEffect      = BattleParticles.createParticleEffect(file='pixieDrop')
    explodeEffect   = BattleParticles.createParticleEffect(file='pixieExplode')
    poofEffect      = BattleParticles.createParticleEffect(file='pixiePoof')
    wallEffect      = BattleParticles.createParticleEffect(file='pixieWall')

    def face90(toon = toon, target = target):
        # Turn the toon so that the right side
        # of their body faces their target
        vec = Point3(target.getPos() - toon.getPos())
        vec.setZ(0)
        temp = vec[0]
        vec.setX(-vec[1])
        vec.setY(temp)
        targetPoint = Point3(toon.getPos() + vec)
        toon.headsUp(render, targetPoint)

    delay = 2.5
    mtrack = Parallel(__getPartTrack(sprayEffect, 1.5, 0.5, [sprayEffect, toon, 0]),
                      __getPartTrack(dropEffect, 1.9, 2.0, [dropEffect, target, 0]),
                      __getPartTrack(explodeEffect, 2.7, 1.0, [explodeEffect, toon, 0]),
                      __getPartTrack(poofEffect, 3.4, 1.0, [poofEffect, target, 0]),
                      __getPartTrack(wallEffect, 4.05, 1.2, [wallEffect, toon, 0]),
                      __getSoundTrack(level, 2, duration=4.1, node=toon),
                      Sequence(Func(face90),
                               ActorInterval(toon, 'sprinkle-dust')),
                      Sequence(Wait(delay),
                               Func(__healToon, target, toon, hp, ineffective, hasInteractivePropHealBonus)))
    tHeal = track.getDuration()
    track.append(mtrack)
    track.append(__returnToBase(heal))
    if len(heal['target']) > 1:
        pHp = heal['target'][1]['hp']
        track = Parallel(
            track,
            Sequence(
                Wait(tHeal + delay),
                Func(__healToon, toon, toon, pHp, ineffective, hasInteractivePropHealBonus)
            )
        )
    return track
    
def __healJuggle(heal, hasInteractivePropHealBonus):
    toon = heal["avatar"]
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']
    
    # Make a 'sandwich' around the track specific interval
    track = Sequence(__runToHealSpot(heal))
    delay = 4.0
    first = 1
    targetTrack = Sequence()
    for target in targets:
        targetToon = target["avatar"]
        hp = target['hp']
        reactIval = Func(__healToon, targetToon, toon, hp, ineffective, hasInteractivePropHealBonus)
        if first == 1:
            targetTrack.append(Wait(delay))
            first = 0
        targetTrack.append(reactIval)

    cube = globalPropPool.getProp('cubes')
    cubes = [cube]
    hips = toon.getHipsParts()
    cubeTrack = Sequence(Func(MovieUtil.showProps, cubes, hips),
                         MovieUtil.getActorIntervals(cubes, 'cubes'),
                         Func(MovieUtil.removeProps, cubes))

    mtrack = Parallel(cubeTrack,
                      __getSoundTrack(level, 0.7, duration=7.7, node=toon),
                      ActorInterval(toon, 'juggle'),
                      targetTrack)
    tHeal = track.getDuration()
    track.append(mtrack)
    
    # just have the Toon run back
    track.append(__returnToBase(heal))
    for target in targets:
        targetToon = target["avatar"]

    return track

# @Deprecated
def __healChest(heal, hasInteractivePropHealBonus):
    toon = heal["avatar"]
    target = heal['target'][0]["avatar"]
    level = heal['level']
    hp = heal['target'][0]['hp']
    ineffective = heal['sidestep']
    battle = heal['battle']
    track = Sequence(__runToHealSpot(heal, True))
    chest = globalPropPool.getProp('treasure-chest')
    popsicle = globalPropPool.getProp('popsicle')
    popsicleTwo = globalPropPool.getProp('popsicle')
    popsicleThree = globalPropPool.getProp('popsicle')
    delay = 0.2
    dScale = 0.5
    tChest = 0.5
    tGrab = 0.1
    dGrab = 0.5

    popOneTrack     = Sequence(Func(MovieUtil.showProp, popsicle, render, battle.getPos() + Point3(0, 0, 1.5)),
                               Func(popsicle.setBillboardPointWorld),
                               LerpScaleInterval(popsicle, dScale, Point3(0.5, 0.5, 0.5), startScale=MovieUtil.PNT3_NEARZERO),
                               Wait(1),
                               LerpPosInterval(popsicle, dGrab, Point3(target.getPos())),
                               Func(MovieUtil.removeProp, popsicle))

    popTwoTrack     = Sequence(Func(MovieUtil.showProp, popsicleTwo, render, battle.getPos() + Point3(-0.75, 0, 0.75)),
                               Func(popsicleTwo.setBillboardPointWorld),
                               LerpScaleInterval(popsicleTwo, dScale, Point3(0.5, 0.5, 0.5), startScale=MovieUtil.PNT3_NEARZERO),
                               Wait(1),
                               LerpPosInterval(popsicleTwo, dGrab, Point3(target.getPos())),
                               Func(MovieUtil.removeProp, popsicleTwo))

    popThreeTrack   = Sequence(Func(MovieUtil.showProp, popsicleThree, render, battle.getPos() + Point3(0.75, 0, 0.75)),
                               Func(popsicleThree.setBillboardPointWorld),
                               LerpScaleInterval(popsicleThree, dScale, Point3(0.5, 0.5, 0.5), startScale=MovieUtil.PNT3_NEARZERO),
                               Wait(1),
                               LerpPosInterval(popsicleThree, dGrab, Point3(target.getPos())),
                               Parallel(ActorInterval(target, 'conked'),
                                        Func(__healToon, target, toon, hp, ineffective, hasInteractivePropHealBonus),
                                        Func(MovieUtil.removeProp, popsicleThree)))
    delay = tGrab + dGrab
    mtrack = Sequence(Parallel(Func(chest.reparentTo, battle),
                               Func(chest.setY, 0)),
                               Func(toon.headsUp, chest),
                               Parallel(Func(toon.pingpong, 'cast', fromFrame=30, toFrame=40),
                                        ActorInterval(chest, 'treasure-chest'),
                                        __getSoundTrack(level, 2, node=toon)),
                               __returnToBase(heal),
                               Parallel(popOneTrack,
                                        popTwoTrack,
                                        popThreeTrack),
                               LerpScaleInterval(chest, 0.2, MovieUtil.PNT3_NEARZERO),
                               Func(MovieUtil.removeProp, chest))
    track.append(mtrack)
    return track


def __healCannon(heal, hasInteractivePropHealBonus):
    toon = heal["avatar"]
    target = heal['target'][0]["avatar"]
    level = heal['level']
    hp = heal['target'][0]['hp']
    ineffective = heal['sidestep']
    battle = heal['battle']
    origHpr = toon.getHpr(battle)
    track = Sequence()
    cannon = globalPropPool.getProp('cannon')
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
                Func(__healToon, target, toon, hp, ineffective, hasInteractivePropHealBonus), 
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
    if len(heal['target']) > 1:
        pHp = heal['target'][1]['hp']
        track = Parallel(
            track,
            Sequence(
                Wait(3 + 2.3 + 2.5),
                Func(__healToon, toon, toon, pHp, ineffective, hasInteractivePropHealBonus)
            )
        )
    return track


def __healDive(heal, hasInteractivePropHealBonus):
    splash = Splash.Splash(render)
    splash.reparentTo(render)

    toon = heal["avatar"]
    targets = heal['target']
    ineffective = heal['sidestep']
    level = heal['level']
    
    # Make a 'sandwich' around the track specific interval
    track = Sequence(__runToHealSpot(heal))
    delay = 7.0
    first = 1
    targetTrack = Sequence()
    for target in targets:
        targetToon = target["avatar"]
        hp = target['hp']
        reactIval = Func(__healToon, targetToon, toon, hp, ineffective, hasInteractivePropHealBonus)
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

    propTrack = Sequence(Func(MovieUtil.showProp, glass, render, glassPos),
                         Func(MovieUtil.showProp, ladder, render, ladderPos),
                         Func(toonsLook, toonsInBattle, placeNode, Point3(0, 0, 0)),
                         Func(placeNode.setPos, lookBase),
                         LerpScaleInterval(ladder, ladderGrowTime, scaleUpPoint, startScale=MovieUtil.PNT3_NEARZERO),
                         Func(placeNode.setPos, lookTop),
                         Wait(4.2),
                         Func(placeNode.setPos, LookGlass),
                         Wait(2.2),
                         LerpScaleInterval(ladder, ladderGrowTime, MovieUtil.PNT3_NEARZERO, startScale=scaleUpPoint),
                         Func(MovieUtil.removeProps, diveProps))
 
    mtrack = Parallel(
        propTrack,
        __getSoundTrack(level, 0.6, duration=9.0, node=toon),
        Sequence(
            Parallel(
                Sequence(
                    ActorInterval(toon, 'walk', loop=0, duration=walkToLadderTime),
                    ActorInterval(toon, 'neutral', loop=0, duration=0.1)
                ),
                LerpPosInterval(toon, walkToLadderTime, climbladderPos),
                Wait(ladderGrowTime)
            ),
            Parallel(
                ActorInterval(toon, 'climb', loop=0, endFrame=116),
                Sequence(
                    Wait(4.6),
                    Func(toonNode.setTransparency, 1),
                    LerpColorScaleInterval(toonNode, 0.25, VBase4(1, 1.0, 1, 0.0), blendType='easeInOut'),
                    LerpScaleInterval(toonNode, 0.01, 0.1, startScale=toonscale),
                    LerpHprInterval(toon, 0.01, toonFacing),
                    LerpPosInterval(toon, 0.0, glassToonPos),
                    Func(toonNode.clearTransparency),
                    Func(toonNode.clearColorScale),
                    Parallel(
                        ActorInterval(toon, 'swim', loop=1, startTime=0.0, endTime=1.0),
                        Wait(1.0)
                    )
                ),
                Sequence(
                    Wait(4.6),
                    Func(splash.play),
                    Wait(1.0),
                    Func(splash.destroy)
                )
            ),
            Wait(0.5),
            Parallel(
                ActorInterval(toon, 'jump', loop=0, startTime=0.2),
                LerpScaleInterval(toonNode, 0.5, toonscale, startScale=0.1),
                Func(stopLook, toonsInBattle)
            )
        ),
        targetTrack
    )
    tHeal = track.getDuration()
    track.append(mtrack)

    track.append(__returnToBase(heal))
    for target in targets:
        targetToon = target["avatar"]

    return track


def add3(t1, t2):
    returnThree = Point3(t1[0] + t2[0], t1[1] + t2[1], t1[2] + t2[2])
    return returnThree


def stopLook(toonsInBattle):
    for someToon in toonsInBattle:
        someToon.stopStareAt()


def toonsLook(toons, someNode, offset):
    for someToon in toons:
        someToon.startStareAt(someNode, offset)
