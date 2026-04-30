from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
import random
from toontown.battle import BattleParticles
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.battle import HealJokes
from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.chat.ChatGlobals import *
from toontown.nametag.NametagGlobals import *
from toontown.toon import LaughingManGlobals
from toontown.toon import NPCToons
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.chat import ResistanceChat
from toontown.speedchat import TTSCDecoders

notify = DirectNotifyGlobal.directNotify.newCategory('MovieNPCSOS')
soundFiles = ('AA_heal_tickle.ogg', 'AA_heal_telljoke.ogg', 'AA_heal_smooch.ogg', 'AA_heal_happydance.ogg', 'AA_heal_pixiedust.ogg', 'AA_heal_juggle.ogg')
offset = Point3(0, 4.0, 0)

def __cogsMiss(attack, level, hp):
    return __doCogsMiss(attack, level, hp)


def __toonsHit(attack, level, hp):
    return __doToonsHit(attack, level, hp)


def __restockGags(attack, level, hp):
    return __doRestockGags(attack, level, hp)

def __damageBoost(attack, level, hp):
    return __doDamageBoost(attack, level, hp)


NPCSOSfn_dict = {ToontownBattleGlobals.NPC_COGS_MISS: __cogsMiss,
 ToontownBattleGlobals.NPC_TOONS_HIT: __toonsHit,
 ToontownBattleGlobals.NPC_RESTOCK_GAGS: __restockGags,
 ToontownBattleGlobals.NPC_DAMAGE_BOOST: __damageBoost}

def doNPCSOSs(NPCSOSs):
    if len(NPCSOSs) == 0:
        return (None, None)
    track = Sequence()
    textTrack = Sequence()
    for n in NPCSOSs:
        ival, textIval = __doNPCSOS(n)
        if ival:
            track.append(ival)
            textTrack.append(textIval)

    camDuration = track.getDuration()
    if camDuration > 0.0:
        camTrack = MovieCamera.chooseHealShot(NPCSOSs, camDuration)
    else:
        camTrack = Sequence()
    return (track, Parallel(camTrack, textTrack))


def __doNPCSOS(sos):
    npcId = sos['npcId']
    track, level, hp = NPCToons.getNPCTrackLevelHp(npcId)
    if track != None:
        return NPCSOSfn_dict[track](sos, level, hp)
    else:
        return __cogsMiss(sos, 0, 0)


def __healToon(toon, hp, ineffective = 0):
    notify.debug('healToon() - toon: %d hp: %d ineffective: %d' % (toon.doId, hp, ineffective))
    if ineffective == 1:
        laughter = random.choice(TTLocalizer.MovieHealLaughterMisses)
    else:
        maxDam = ToontownBattleGlobals.AvPropDamage[0][1][0][1]
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
    '''if npc.getName() == 'Magic Cat':
        LaughingManGlobals.addToonEffect(npc)
        npc.nametag3d.hide()'''
    a = Func(npc.reparentTo, attack['battle'])
    b = Func(npc.setPos, pos)
    c = Func(npc.setHpr, hpr)
    d = Func(npc.pose, 'teleport', npc.getNumFrames('teleport') - 1)
    e = npc.getTeleportInTrack()
    ee = Func(npc.addActive)
    if npc.nametag.getText() == 'Donald Frump':
        text = random.choice(TTLocalizer.FrumpGreetings)
    elif npc.nametag.getText() == 'Jakebooy':
        text = random.choice(TTLocalizer.JakebooySOSGreetings)
    elif npc.nametag.getText() == 'Ask Alice':
        text = TTLocalizer.AliceSOSGreeting
    else:
        text = TTLocalizer.MovieNPCSOSGreeting % attack['toon'].getName()
    f = Func(npc.setChatAbsolute, text, CFSpeech | CFTimeout)
    g = ActorInterval(npc, 'wave')
    h = Func(npc.loop, 'neutral')
    seq = Sequence(a, b, c, d, e, ee, f, g, h)
    seq.append(Func(npc.clearChat))
    seq.append(Parallel(Func(attack['toon'].makeCooldown), Func(attack['toon'].addCooldownRounds, 2)))
    if npc.getName() == 'Prince Frizzy':
        princeFrizzyTrack = Sequence()
        princeFrizzyTrack.append(Func(npc.setChatAbsolute, "Start Dancing! I got this covered!", CFSpeech | CFTimeout))
        princeFrizzyTrack.append(Func(attack['toon'].loop, 'victory'))
        seq.append(princeFrizzyTrack)
    return seq


def teleportOut(attack, npc):
    if npc.style.torso[1] == 'd':
        a = ActorInterval(npc, 'curtsy')
    else:
        a = ActorInterval(npc, 'bow')
    if npc.nametag.getText() == 'Donald Frump':
        text = "Oh, by the way, you're fired. Get 'em out of here!"
    elif npc.nametag.getText() == 'Jakebooy':
        text = random.choice(TTLocalizer.JakebooySOSGoodbyes)
    elif npc.nametag.getText() == 'Ask Alice':
        text = TTLocalizer.AliceSOSLeave
    else:
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



def __doSprinkle(attack, recipients, hp = 0):
    toon = NPCToons.createLocalNPC(attack['npcId'])
    if toon == None:
        return
    targets = attack[recipients]
    level = 4
    battle = attack['battle']
    track = Sequence(teleportIn(attack, toon))

    def face90(target, toon, battle):
        vec = Point3(target.getPos(battle) - toon.getPos(battle))
        vec.setZ(0)
        temp = vec[0]
        vec.setX(-vec[1])
        vec.setY(temp)
        targetPoint = Point3(toon.getPos(battle) + vec)
        toon.headsUp(battle, targetPoint)

    delay = 2.5
    targetTrack = Parallel()
    for target in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='pixieSpray')
        dropEffect = BattleParticles.createParticleEffect(file='pixieDrop')
        explodeEffect = BattleParticles.createParticleEffect(file='pixieExplode')
        poofEffect = BattleParticles.createParticleEffect(file='pixiePoof')
        wallEffect = BattleParticles.createParticleEffect(file='pixieWall')
        mtrack = Parallel(__getPartTrack(sprayEffect, 1.5, 0.5, [sprayEffect, toon, 0]), __getPartTrack(dropEffect, 1.9, 2.0, [dropEffect, target, 0]), __getPartTrack(explodeEffect, 2.7, 1.0, [explodeEffect, toon, 0]), __getPartTrack(poofEffect, 3.4, 1.0, [poofEffect, target, 0]), __getPartTrack(wallEffect, 4.05, 1.2, [wallEffect, toon, 0]), __getSoundTrack(level, 2, duration=3.1, node=toon), Sequence(Func(face90, target, toon, battle), ActorInterval(toon, 'sprinkle-dust')), Sequence(Wait(delay), Func(__healToon, target, hp)))
        targetTrack.append(mtrack)

    track.append(effectTrack)
    track.append(Func(toon.setHpr, Vec3(180.0, 0.0, 0.0)))
    track.append(teleportOut(attack, toon))
    return track


def __doUnite(attack, hp = 0, index = 108):
    toon = NPCToons.createLocalNPC(attack['npcId'])
    chatString = TTSCDecoders.decodeTTSCResistanceMsg(index)
    delay = 2
    if toon == None:
        return
    targets = attack['toons']
    track = Sequence(teleportIn(attack, toon))
    track.append(Func(toon.setChatAbsolute, chatString, CFSpeech | CFTimeout))
    track.append(Func(ResistanceChat.doEffect, index, toon, targets))
    track.append(Wait(delay))
    track.append(teleportOut(attack, toon))
    return track


def __doToonsHit(attack, level, hp):
    track = __doSprinkle(attack, 'toons', hp)
    pbpText = attack['playByPlayText']
    if hp == 1:
        text = TTLocalizer.MovieNPCSOSToonsHitS
    else:
        text = TTLocalizer.MovieNPCSOSToonsHitP % hp
    pbpTrack = pbpText.getShowInterval(text, track.getDuration() - 2)
    return (track, pbpTrack)


def __doCogsMiss(attack, level, hp):
    track = __doSprinkleCogs(attack, 'suits', hp)
    pbpText = attack['playByPlayText']
    if hp == 1:
        text = TTLocalizer.MovieNPCSOSCogsMissS
    else:
        text = TTLocalizer.MovieNPCSOSCogsMissP % hp
    pbpTrack = pbpText.getShowInterval(text, track.getDuration() - 2)
    return (track, pbpTrack)


def __doRestockGags(attack, level, hp):
    pbpText = attack['playByPlayText']
    if level == ToontownBattleGlobals.HEAL_TRACK:
        text = TTLocalizer.MovieNPCSOSHeal
        index = 100
    elif level == ToontownBattleGlobals.TRAP_TRACK:
        text = TTLocalizer.MovieNPCSOSTrap
        index = 101
    elif level == ToontownBattleGlobals.LURE_TRACK:
        text = TTLocalizer.MovieNPCSOSLure
        index = 102
    elif level == ToontownBattleGlobals.SOUND_TRACK:
        text = TTLocalizer.MovieNPCSOSSound
        index = 103
    elif level == ToontownBattleGlobals.THROW_TRACK:
        text = TTLocalizer.MovieNPCSOSThrow
        index = 104
    elif level == ToontownBattleGlobals.SQUIRT_TRACK:
        text = TTLocalizer.MovieNPCSOSSquirt
        index = 105
    elif level == ToontownBattleGlobals.ZAP_TRACK:
        text = TTLocalizer.MovieNPCSOSZap
        index = 106
    elif level == ToontownBattleGlobals.DROP_TRACK:
        text = TTLocalizer.MovieNPCSOSDrop
        index = 107
    elif level == -1:
        text = TTLocalizer.MovieNPCSOSAll
        index = 108
    track = __doUnite(attack, hp, index)
    pbpTrack = pbpText.getShowInterval(TTLocalizer.MovieNPCSOSRestockGags % text, track.getDuration() - 2)
    return (track, pbpTrack)

def __doSmooch(attack, level, hp = 0):
    toon = NPCToons.createLocalNPC(attack['npcId'])
    if toon == None:
        return
    targets = attack['toons']
    #level = 2
    battle = attack['battle']
    track2 = Sequence(teleportIn(attack, toon))
    lipstick = globalPropPool.getProp('lipstick')
    lipstick2 = MovieUtil.copyProp(lipstick)
    lipsticks = [lipstick, lipstick2]
    rightHands = toon.getRightHands()
    dScale = 0.5
    lipstickTrack = Sequence(Func(MovieUtil.showProps, lipsticks, rightHands, Point3(-0.27, -0.24, -0.95), Point3(-118, -10.6, -25.9)), MovieUtil.getScaleIntervals(lipsticks, dScale, MovieUtil.PNT3_NEARZERO, MovieUtil.PNT3_ONE), Wait(toon.getDuration('smooch') - 2.0 * dScale), MovieUtil.getScaleIntervals(lipsticks, dScale, MovieUtil.PNT3_ONE, MovieUtil.PNT3_NEARZERO))
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

    effectTrack = Sequence()
    targetTrack = Parallel()
    for target in targets:
        lipcopy = MovieUtil.copyProp(lips)

        lipsTrack = Sequence(
            Wait(tLips),
            Func(MovieUtil.showProp, lipcopy, render, getLipPos),
            Func(lipcopy.setBillboardPointWorld),
            LerpScaleInterval(lipcopy, dScale, Point3(3, 3, 3), startScale=MovieUtil.PNT3_NEARZERO),
            Wait(tThrow - tLips - dScale),
            LerpPosInterval(lipcopy, dThrow, Point3(target.getPos() + Point3(0, 0, target.getHeight()))),
            Func(MovieUtil.removeProp, lipcopy)
        )

        delay = tThrow + dThrow

        buffTrack = Sequence(Wait(delay))

        if level == ToontownBattleGlobals.HEAL_TRACK:
            buffTrack.append(Func(target.makeToonupGagBoost, 1))
            buffTrack.append(Func(target.addToonupGagBoostRounds, 3))
            buffTrack.append(Func(target.checkToonupGagBoost, hp))
        elif level == ToontownBattleGlobals.TRAP_TRACK:
            buffTrack.append(Func(target.makeTrapGagBoost, 2))
            buffTrack.append(Func(target.addTrapGagBoostRounds, 3))
            buffTrack.append(Func(target.checkTrapGagBoost, hp))
        elif level == ToontownBattleGlobals.LURE_TRACK:
            buffTrack.append(Func(target.makeLureGagBoost, 3))
            buffTrack.append(Func(target.addLureGagBoostRounds, 3))
            buffTrack.append(Func(target.checkLureGagBoost, hp))
        elif level == ToontownBattleGlobals.THROW_TRACK:
            buffTrack.append(Func(target.makeThrowGagBoost, 4))
            buffTrack.append(Func(target.addThrowGagBoostRounds, 3))
            buffTrack.append(Func(target.checkThrowGagBoost, hp))
        elif level == ToontownBattleGlobals.SQUIRT_TRACK:
            buffTrack.append(Func(target.makeSquirtGagBoost, 5))
            buffTrack.append(Func(target.addSquirtGagBoostRounds, 3))
            buffTrack.append(Func(target.checkSquirtGagBoost, hp))
        elif level == ToontownBattleGlobals.ZAP_TRACK:
            buffTrack.append(Func(target.makeZapGagBoost, 6))
            buffTrack.append(Func(target.addZapGagBoostRounds, 3))
            buffTrack.append(Func(target.checkZapGagBoost, hp))
        elif level == ToontownBattleGlobals.SOUND_TRACK:
            buffTrack.append(Func(target.makeSoundGagBoost, 7))
            buffTrack.append(Func(target.addSoundGagBoostRounds, 3))
            buffTrack.append(Func(target.checkSoundGagBoost, hp))
        elif level == ToontownBattleGlobals.DROP_TRACK:
            buffTrack.append(Func(target.makeDropGagBoost, 8))
            buffTrack.append(Func(target.addDropGagBoostRounds, 3))
            buffTrack.append(Func(target.checkDropGagBoost, hp))
        elif level == 8:
            buffTrack.append(Func(target.makeDamageUp))
            buffTrack.append(Func(target.addDamageUpRounds, 3))
            buffTrack.append(Func(target.checkDamageUp, hp))

        mtrack = Parallel(
            lipstickTrack,
            lipsTrack,
            __getSoundTrack(2, 2, node=toon),
            Sequence(ActorInterval(toon, 'smooch')),
            Sequence(Wait(delay), ActorInterval(target, 'conked'), Func(target.loop, 'neutral')),
            Sequence(Wait(delay), Func(__healToon, target, 0)),
            buffTrack
        )

        targetTrack.append(mtrack)

    effectTrack.append(targetTrack)
    effectTrack.append(Func(MovieUtil.removeProps, lipsticks))
    track2.append(effectTrack)
    track2.append(teleportOut(attack, toon))
    track2.append(Func(target.clearChat))
    return track2


def __doDamageBoost(attack, level, hp):
    track = __doSmooch(attack, level, hp)
    pbpText = attack['playByPlayText']
    if level == ToontownBattleGlobals.HEAL_TRACK:
        text = TTLocalizer.MovieNPCSOSHeal
    elif level == ToontownBattleGlobals.TRAP_TRACK:
        text = TTLocalizer.MovieNPCSOSTrap
    elif level == ToontownBattleGlobals.LURE_TRACK:
        text = TTLocalizer.MovieNPCSOSLure
    elif level == ToontownBattleGlobals.SOUND_TRACK:
        text = TTLocalizer.MovieNPCSOSSound
    elif level == ToontownBattleGlobals.THROW_TRACK:
        text = TTLocalizer.MovieNPCSOSThrow
    elif level == ToontownBattleGlobals.SQUIRT_TRACK:
        text = TTLocalizer.MovieNPCSOSSquirt
    elif level == ToontownBattleGlobals.ZAP_TRACK:
        text = TTLocalizer.MovieNPCSOSZap
    elif level == ToontownBattleGlobals.DROP_TRACK:
        text = TTLocalizer.MovieNPCSOSDrop
    elif level == 8:
        text = TTLocalizer.MovieNPCSOSAll
    else:
        text = 'Unknown Track'
    pbpTrack = pbpText.getShowInterval(TTLocalizer.MovieNPCSOSBoostGags % (text, hp), track.getDuration() - 2)
    return (track, pbpTrack)


def doNPCTeleports(attacks):
    npcs = []
    npcDatas = []
    arrivals = Sequence()
    departures = Parallel()
    for attack in attacks:
        if 'npcId' in attack:
            npcId = attack['npcId']
            npc = NPCToons.createLocalNPC(npcId)
            if npc != None:
                npcs.append(npc)
                attack['npc'] = npc
                toon = attack['toon']
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
    return (arrivals, unturns, npcs)
