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
from toontown.toon import IOURegistry
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownBattleGlobals
from toontown.chat import ResistanceChat
from toontown.speedchat import TTSCDecoders
from otp.otpbase import OTPGlobals
from pandac.PandaModules import TextProperties, TextPropertiesManager, TextGraphic, TextNode

notify = DirectNotifyGlobal.directNotify.newCategory('MovieNPCSOS')
soundFiles = ('AA_heal_tickle.ogg', 'AA_heal_telljoke.ogg', 'AA_heal_smooch.ogg', 'AA_heal_happydance.ogg', 'AA_heal_pixiedust.ogg', 'AA_heal_juggle.ogg')
offset = Point3(0, 4.0, 0)
IOUAnimationSpeed = 1.6
IOUSpawnPositions = (Point3(0, 0, 0), Point3(4.0, 0, 0), Point3(-4.0, 0, 0), Point3(8.0, 0, 0))

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
    track = Parallel()
    textTrack = Parallel()
    iouIndex = 0
    for n in NPCSOSs:
        definition = IOURegistry.getIOU(n.get('level', -1))
        if definition is not None:
            if iouIndex < len(IOUSpawnPositions):
                n['_iouSpawnPos'] = IOUSpawnPositions[iouIndex]
            else:
                n['_iouSpawnPos'] = Point3(4.0 * iouIndex, 0, 0)
            iouIndex += 1
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
    definition = IOURegistry.getIOU(sos.get('level', -1))
    if definition is not None:
        return __doClashIOU(sos, definition)
    npcId = sos['npcId']
    track, level, hp = NPCToons.getNPCTrackLevelHp(npcId)
    if track != None:
        return NPCSOSfn_dict[track](sos, level, hp)
    else:
        return __cogsMiss(sos, 0, 0)



def __doClashIOU(attack, definition):
    toon = NPCToons.createLocalNPC(definition.getNpcId())
    if toon is None:
        return (Sequence(), Sequence())
    targets = [target['avatar'] for target in attack.get('target', [])]
    if not targets:
        return (Sequence(), Sequence())
    battle = attack['battle']
    gagTrack = definition.getGagTrack()
    boost = definition.getBoost()
    uses = definition.getUses()
    spawnPos = attack.pop('_iouSpawnPos', Point3(0, 0, 0))
    track = Sequence(teleportInIOU(attack, toon, pos=spawnPos, cooldownTurns=definition.getRewardCooldown()))

    def face90(actor, recipients, battle):
        avgPoint = Point3(0, 0, 0)
        for recipient in recipients:
            avgPoint += recipient.getPos(battle)
        avgPoint /= len(recipients)
        vec = Point3(avgPoint - actor.getPos(battle))
        vec.setZ(0)
        temp = vec[0]
        vec.setX(-vec[1])
        vec.setY(temp)
        targetPoint = Point3(actor.getPos(battle) + vec)
        actor.headsUp(battle, targetPoint)

    timeScale = 1.0 / IOUAnimationSpeed
    delay = 2.5 * timeScale
    effectTrack = Parallel()
    for target in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='pixieSpray')
        dropEffect = BattleParticles.createParticleEffect(file='pixieDrop')
        explodeEffect = BattleParticles.createParticleEffect(file='pixieExplode')
        poofEffect = BattleParticles.createParticleEffect(file='pixiePoof')
        wallEffect = BattleParticles.createParticleEffect(file='pixieWall')
        color = ToontownBattleGlobals.TrackColors[gagTrack]
        for effect in (sprayEffect, dropEffect, explodeEffect, poofEffect, wallEffect):
            effect.setColorScale(Vec4(color[0], color[1], color[2], 1))
        sprinkleNode = battle.attachNewNode('sprinkleNode')
        sprinkleNode.setPos(toon.getPos())
        face90(sprinkleNode, (target,), battle)
        mtrack = Parallel(
            __getPartTrack(sprayEffect, 1.5 * timeScale, 0.5 * timeScale, [sprayEffect, sprinkleNode, 0]),
            __getPartTrack(dropEffect, 1.9 * timeScale, 2.0 * timeScale, [dropEffect, target, 0]),
            __getPartTrack(explodeEffect, 2.7 * timeScale, 1.0 * timeScale, [explodeEffect, toon, 0]),
            __getPartTrack(poofEffect, 3.4 * timeScale, 1.0 * timeScale, [poofEffect, target, 0]),
            __getPartTrack(wallEffect, 4.05 * timeScale, 1.2 * timeScale, [wallEffect, toon, 0]),
            Sequence(Wait(delay), Func(__healToon, target, boost), Func(__playIOUBoostArrows, target, gagTrack), Func(__showIOUBoostPopup, target, boost, gagTrack, uses), Func(sprinkleNode.removeNode))
        )
        effectTrack.append(mtrack)
    effectTrack.append(Parallel(__getSoundTrack(4, 2 * timeScale, duration=3.1 * timeScale, node=toon), Sequence(Func(face90, toon, targets, battle), ActorInterval(toon, 'sprinkle-dust', playRate=IOUAnimationSpeed))))
    track.append(effectTrack)
    track.append(Func(toon.setHpr, Vec3(180.0, 0.0, 0.0)))
    track.append(teleportOut(attack, toon))
    return (track, Sequence())

def __showIOUBoostPopup(toon, boost, gagTrack, uses):
    useText = 'use' if uses == 1 else 'uses'
    manager = TextPropertiesManager.getGlobalPtr()
    if gagTrack == -1:
        color = (1.0, 1.0, 1.0, 1.0)
        propertyName = 'iouGlobalBoost'
        graphicName = 'iouGlobalBoostIcon'
        trackProperties = TextProperties()
        trackProperties.setTextColor(color[0], color[1], color[2], color[3])
        manager.setProperties(propertyName, trackProperties)
        statusModel = loader.loadModel('phase_3.5/models/gui/status_effects')
        icon = statusModel.find('**/toon_damage_up_icon')
        if not icon.isEmpty():
            icon.setColorScale(color[0], color[1], color[2], color[3])
            iconGraphic = TextGraphic()
            iconGraphic.setModel(icon)
            iconGraphic.setFrame((-0.18, 0.18, -0.275, 0.2))
            manager.setGraphic(graphicName, iconGraphic)
            text = '\x01%s\x01+%d  \x05%s\x05  (%d %s)\x02' % (propertyName, boost, graphicName, uses, useText)
        else:
            text = '\x01%s\x01+%d (%d %s)\x02' % (propertyName, boost, uses, useText)
    else:
        color = ToontownBattleGlobals.TrackColors[gagTrack]
        trackProperties = TextProperties()
        trackProperties.setTextColor(color[0], color[1], color[2], 1)
        propertyName = 'iouTrack%d' % gagTrack
        graphicName = 'iouLevel6Gag%d' % gagTrack
        manager.setProperties(propertyName, trackProperties)
        invModel = loader.loadModel('phase_3.5/models/gui/inventory_icons')
        gagGeom = invModel.find('**/' + ToontownBattleGlobals.AvPropsNew[gagTrack][5])
        if not gagGeom.isEmpty():
            gagGeom.setScale(7)
            gagGeom.setColorScale(color[0], color[1], color[2], 1)
            gagGraphic = TextGraphic()
            gagGraphic.setModel(gagGeom)
            gagGraphic.setFrame((-0.18, 0.18, -0.275, 0.2))
            manager.setGraphic(graphicName, gagGraphic)
            text = '\x01%s\x01+%d  \x05%s\x05  (%d %s)\x02' % (propertyName, boost, graphicName, uses, useText)
        else:
            text = '\x01%s\x01+%d (%d %s)\x02' % (propertyName, boost, uses, useText)

    textNode = TextNode('iouBoostPopup')
    textNode.setFont(OTPGlobals.getSignFont())
    textNode.setText(text)
    textNode.clearShadow()
    textNode.setAlign(TextNode.ACenter)
    popup = toon.attachNewNode(textNode.generate())
    popup.setScale(0.8)
    popup.setBillboardPointEye()
    popup.setBin('fixed', 100)
    popupIndex = getattr(toon, '_iouPopupDisplayCount', 0)
    toon._iouPopupDisplayCount = popupIndex + 1
    startZ = toon.height / 2.0 + popupIndex * 0.8
    popup.setPos(0, 0, startZ)

    def cleanupPopup():
        if not popup.isEmpty():
            popup.removeNode()
        current = getattr(toon, '_iouPopupDisplayCount', 1)
        toon._iouPopupDisplayCount = max(0, current - 1)

    popupTrack = Sequence(
        popup.posInterval(1.0, Point3(0, 0, toon.height + 1.5 + popupIndex * 0.8), blendType='easeOut'),
        Wait(1.0),
        LerpColorScaleInterval(popup, 0.25, Vec4(0, 0, 0, 0)),
        Func(cleanupPopup)
    )
    popupTrack.start()
    if gagTrack == -1:
        statusModel.removeNode()
    else:
        invModel.removeNode()

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


def __playIOUBoostArrows(toon, gagTrack):
    playAura = getattr(toon, 'playIOUBoostArrowAura', None)
    if playAura:
        playAura(gagTrack)


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


def teleportIn(attack, npc, pos = Point3(0, 0, 0), hpr = Vec3(180.0, 0.0, 0.0), cooldownTurns = 2, speed = 1.0):
    '''if npc.getName() == 'Magic Cat':
        LaughingManGlobals.addToonEffect(npc)
        npc.nametag3d.hide()'''
    a = Func(npc.reparentTo, attack['battle'])
    b = Func(npc.setPos, pos)
    c = Func(npc.setHpr, hpr)
    d = Func(npc.pose, 'teleport', npc.getNumFrames('teleport') - 1)
    e = npc.getTeleportInTrack()
    e.setPlayRate(speed)
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
    g = Wait(npc.getDuration('wave') / speed)
    h = Func(npc.loop, 'neutral')
    seq = Sequence(a, b, c, d, e, ee, h, f, g)
    seq.append(Func(npc.clearChat))
    if cooldownTurns > 0:
        seq.append(Parallel(Func(attack['toon'].setToonStatusEffect, 'cooldown', turns=cooldownTurns)))
    if npc.getName() == 'Prince Frizzy':
        princeFrizzyTrack = Sequence()
        princeFrizzyTrack.append(Func(npc.setChatAbsolute, "Start Dancing! I got this covered!", CFSpeech | CFTimeout))
        princeFrizzyTrack.append(Func(attack['toon'].loop, 'victory'))
        seq.append(princeFrizzyTrack)
    return seq


def teleportInIOU(attack, npc, pos = Point3(0, 0, 0), hpr = Vec3(180.0, 0.0, 0.0), cooldownTurns = 2, speed = 1.0):
    a = Func(npc.reparentTo, attack['battle'])
    b = Func(npc.setPos, pos)
    c = Func(npc.setHpr, hpr)
    d = Func(npc.pose, 'teleport', npc.getNumFrames('teleport') - 1)
    e = npc.getTeleportInTrack()
    e.setPlayRate(speed)
    ee = Func(npc.addActive)
    ef = Func(npc.stopBlink)
    eg = Func(npc.openEyes)
    eh = Func(npc.stopLookAroundNow)
    if npc.nametag.getText() == 'Donald Frump':
        text = random.choice(TTLocalizer.FrumpGreetings)
    elif npc.nametag.getText() == 'Jakebooy':
        text = random.choice(TTLocalizer.JakebooySOSGreetings)
    elif npc.nametag.getText() == 'Ask Alice':
        text = TTLocalizer.AliceSOSGreeting
    else:
        text = TTLocalizer.MovieNPCSOSGreeting % attack['toon'].getName()
    f = Func(npc.setChatAbsolute, text, CFSpeech | CFTimeout)
    h = Func(npc.loop, 'neutral')
    seq = Sequence(a, b, c, d, f, e, ee, ef, eg, eh, h, Func(npc.clearChat))
    return seq


def teleportOut(attack, npc, speed = 1.0):
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
    c.setPlayRate(speed)
    seq = Sequence(b, c)
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
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'toonupBoost', modifier=hp, turns=3)))
        elif level == ToontownBattleGlobals.TRAP_TRACK:
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'trapBoost', modifier=hp, turns=3)))
        elif level == ToontownBattleGlobals.LURE_TRACK:
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'lureBoost', modifier=hp, turns=3)))
        elif level == ToontownBattleGlobals.THROW_TRACK:
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'throwBoost', modifier=hp, turns=3)))
        elif level == ToontownBattleGlobals.SQUIRT_TRACK:
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'squirtBoost', modifier=hp, turns=3)))
        elif level == ToontownBattleGlobals.ZAP_TRACK:
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'zapBoost', modifier=hp, turns=3)))
        elif level == ToontownBattleGlobals.SOUND_TRACK:
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'soundBoost', modifier=hp, turns=3)))
        elif level == ToontownBattleGlobals.DROP_TRACK:
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'dropBoost', modifier=hp, turns=3)))
        elif level == 8:
            buffTrack.append(Parallel(Func(target.setToonStatusEffect, 'damageUp', modifier=hp, turns=3)))

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
