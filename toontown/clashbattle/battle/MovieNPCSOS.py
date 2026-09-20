from direct.interval.IntervalGlobal import *
from panda3d.core import Point3

from toontown.clashbattle.battle import BattleParticles, MovieUtil
from toontown.clashbattle.battle.BattleProps import *
from toontown.clashbattle.battle.BattleSounds import *
from toontown.clashbattle.battle.MovieUtil import applyVisualEffect
from otp import *
from toontown.clashbattle.battle.attacks.base.AttackEnum import AttackEnum

from toontown.clashbattle.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.inventory.registry.IOURegistry import IOURegistry, IOUItemDefinition
from toontown.toon import NPCToons # Until NPCs are added we will use Reia's NPCToon port file
from toontown.toonbase import TTLocalizer
from toontown.clashbattle.battle import BattleGlobals
from toontown.utils.DirectNotifyCategory import getNotify
from toontown.chat.constants.ChatGlobals import CFSpeech, CFTimeout

notify = getNotify('MovieNPCSOS')
soundFiles = ('AA_heal_tickle.ogg', 'AA_heal_telljoke.ogg', 'AA_heal_smooch.ogg', 'AA_heal_happydance.ogg', 'AA_heal_pixiedust.ogg', 'AA_heal_juggle.ogg')
offset = Point3(0, 4.0, 0)


def doNPCSOSs(NPCSOSs):
    if len(NPCSOSs) == 0:
        return None, None
    track = Sequence()
    textTrack = Sequence()
    for n in NPCSOSs:
        ival, textIval = __doNPCSOS(n)
        if ival:
            track.append(ival)
            textTrack.append(textIval)

    camDuration = track.getDuration()
    if camDuration > 0.0:
        camTrack = NPCSOSs[0]['battle'].camera.chooseHealShot(NPCSOSs, camDuration)
    else:
        camTrack = Sequence()
    return track, Parallel(camTrack, textTrack)


def __doNPCSOS(sos):
    iou = IOURegistry.get(sos['level'])
    if iou:
        toon = sos['avatar']
        # Immediately apply unite cooldown visual to toons, don't do it inside of the movie
        # The cooldown applies immediately on the AI so they should visually see it immediately as well
        MovieUtil.applyVisualEffect(toon, VisualEffectEnum.UNITE_COOLDOWN)
        return __doToonsDamageUp(sos, iou)
    return Sequence()


def __healToon(toon, hp, ineffective = 0):
    notify.debug('healToon() - toon: %d hp: %d ineffective: %d' % (toon.doId, hp, ineffective))
    if ineffective == 1:
        laughter = random.choice(TTLocalizer.MovieHealLaughterMisses)
    else:
        maxDam = BattleGlobals.AvPropDamage[0][1][0][1]
        if hp >= maxDam - 1:
            laughter = random.choice(TTLocalizer.MovieHealLaughterHits2)
        else:
            laughter = random.choice(TTLocalizer.MovieHealLaughterHits1)
    toon.setChatAbsolute(laughter, CFSpeech | CFTimeout)


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


def teleportIn(attack, npc, pos = Point3(0, 0, 0), hpr = Vec3(180.0, 0.0, 0.0)):
    a = Func(npc.reparentTo, attack['battle'])
    b = Func(npc.setPos, pos)
    c = Func(npc.setHpr, hpr)
    d = Func(npc.pose, 'teleport', npc.getNumFrames('teleport') - 1)
    e = npc.getTeleportInTrack()
    ee = Func(npc.addActive)
    text = TTLocalizer.MovieNPCSOSGreeting % attack["avatar"].getName()
    f = Func(npc.setChatAbsolute, text, CFSpeech | CFTimeout)
    g = ActorInterval(npc, 'wave')
    h = Func(npc.loop, 'neutral')
    i = Func(npc.clearChat)
    return Sequence(a, b, c, d, e, ee, f, g, h, i)


def teleportOut(attack, npc):
    if npc.style.getGender() == 'm' or npc.style.torso[1] == 's':
        a = ActorInterval(npc, 'bow')
    else:
        a = ActorInterval(npc, 'curtsy')

    text = TTLocalizer.MovieNPCSOSGoodbye
    b = Func(npc.setChatAbsolute, text, CFSpeech | CFTimeout)
    c = npc.getTeleportOutTrack()
    seq = Sequence(a, b, c)
    seq.append(Func(npc.removeActive))
    seq.append(Func(npc.detachNode))
    seq.append(Func(npc.delete))
    return seq


def __getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs):
    pEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) == 3:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True))


def __doSprinkle(attack, toonTrack, npcId, hp=0, visualEffectTrack=None):
    toon = NPCToons.createLocalNPC(npcId)
    if toon is None:
        return Sequence()
    targets = [target["avatar"] for target in attack["target"]]
    level = 4
    battle = attack['battle']
    track = Sequence(teleportIn(attack, toon))

    def face90(toon, targets, battle):
        avgPoint = Point3(0, 0, 0)
        for target in targets:
            avgPoint += target.getPos(battle)
        avgPoint /= len(targets)
        vec = Point3(avgPoint - toon.getPos(battle))
        vec.setZ(0)
        temp = vec[0]
        vec.setX(-vec[1])
        vec.setY(temp)
        targetPoint = Point3(toon.getPos(battle) + vec)
        toon.headsUp(battle, targetPoint)

    delay = 2.5
    effectTrack = Parallel()
    for target in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='pixieSpray')
        dropEffect = BattleParticles.createParticleEffect(file='pixieDrop')
        explodeEffect = BattleParticles.createParticleEffect(file='pixieExplode')
        poofEffect = BattleParticles.createParticleEffect(file='pixiePoof')
        wallEffect = BattleParticles.createParticleEffect(file='pixieWall')
        if level != -1:
            for effect in (sprayEffect, dropEffect, explodeEffect, poofEffect, wallEffect):
                effect.setColorScale(Vec4(*BattleGlobals.TrackColors[toonTrack], 1))
        sprinkleNode = battle.attachNewNode('sprinkleNode')
        sprinkleNode.setPos(toon.getPos())
        face90(sprinkleNode, (target,), battle)
        mtrack = Parallel(
            __getPartTrack(sprayEffect, 1.5, 0.5, [sprayEffect, sprinkleNode, 0]),
            __getPartTrack(dropEffect, 1.9, 2.0, [dropEffect, target, 0]),
            __getPartTrack(explodeEffect, 2.7, 1.0, [explodeEffect, toon, 0]),
            __getPartTrack(poofEffect, 3.4, 1.0, [poofEffect, target, 0]),
            __getPartTrack(wallEffect, 4.05, 1.2, [wallEffect, toon, 0]),
            Sequence(
                Wait(delay),
                Func(__healToon, target, hp),
                visualEffectTrack or Sequence(),
                Func(sprinkleNode.removeNode)
            )
        )
        effectTrack.append(mtrack)
    effectTrack.append(Parallel(__getSoundTrack(level, 2, duration=3.1, node=toon), Sequence(Func(face90, toon, targets, battle), ActorInterval(toon, 'sprinkle-dust'))))
    track.append(effectTrack)
    track.append(Func(toon.setHpr, Vec3(180.0, 0.0, 0.0)))
    track.append(teleportOut(attack, toon))
    return track


def __doToonsDamageUp(attack, iou: IOUItemDefinition):
    pbpText = attack['playByPlayText']
    track = iou.getGagTrack()
    hp = iou.getBoost()
    uses = iou.getUses()
    gagText = TTLocalizer.ToonTrackNames.get(track, '')
    if track == AttackEnum.TOON_HEAL:
        index = 0
    elif track == AttackEnum.TOON_TRAP:
        index = 1
    elif track == AttackEnum.TOON_LURE:
        index = 2
    elif track == AttackEnum.TOON_SOUND:
        index = 3
    elif track == AttackEnum.TOON_SQUIRT:
        index = 4
    elif track == AttackEnum.TOON_ZAP:
        index = 5
    elif track == AttackEnum.TOON_THROW:
        index = 6
    elif track == AttackEnum.TOON_DROP:
        index = 7
    else:
        index = 8

    effectFunc = Parallel()
    for target in attack['target']:
        av = target["avatar"]
        effectFunc.append(
            Func(applyVisualEffect, av, VisualEffectEnum.TOON_BOOST, [uses, index])
        )
    track = __doSprinkle(attack, track, iou.getNpcId(), hp, visualEffectTrack=effectFunc)
    plural = '' if uses == 1 else 'S'
    damageText = {AttackEnum.TOON_LURE: 'KNOCKBACK DAMAGE',
                  AttackEnum.TOON_HEAL: 'LAFF'}.get(track, 'DAMAGE')
    fullAttackName = f' {uses} ' if uses != 1 else ' '
    fullAttackName += f"{gagText}{'' if gagText == '' else ' '}GAG{plural}"
    text = TTLocalizer.MovieNPCSOSToonsDamageUpS % (hp, damageText, fullAttackName)
    pbpTrack = pbpText.getShowInterval(text, track.getDuration())
    return track, pbpTrack


def doNPCTeleports(attacks):
    npcs = []
    npcDatas = []
    arrivals = Sequence()
    departures = Parallel()
    for attack in attacks:
        if 'npcId' in attack:
            npcId = attack['npcId']
            npc = NPCToons.createLocalNPC(npcId)
            if npc is not None:
                npcs.append(npc)
                attack['npc'] = npc
                toon = attack["avatar"]
                battle = attack['battle']
                pos = toon.getPos(battle) + offset
                hpr = toon.getHpr(battle)
                npcDatas.append((npc, battle, hpr))
                arrival = teleportIn(attack, npc, pos=pos)
                arrivals.append(arrival)
                departure = teleportOut(attack, npc)
                departures.append(departure)

    turns = Parallel()
    unturns = Parallel()
    hpr = Vec3(180.0, 0, 0)
    for npc in npcDatas:
        turns.append(Func(npc[0].setHpr, npc[1], npc[2]))
        unturns.append(Func(npc[0].setHpr, npc[1], hpr))

    arrivals.append(turns)
    unturns.append(departures)
    return arrivals, unturns, npcs
