from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3, Vec4
from toontown.battle import BattleParticles
from toontown.battle import MovieUtil
from toontown.battle import MovieCamera
from toontown.battle import PlayByPlayText
from toontown.battle.BattleSounds import globalBattleSoundCache
from toontown.chat.ChatGlobals import CFSpeech
from toontown.cutscene import PlutocratCutscenes
import random


INVESTORS = ('charon', 'nix', 'hydra', 'styx', 'kerberos')


def _boss(attack):
    return getattr(attack.get('battle'), 'bossCog', None)


def _findSuit(attack, doId):
    battle = attack.get('battle')
    if not battle:
        return None
    for group in (
            getattr(battle, 'suits', ()),
            getattr(battle, 'activeSuits', ()),
            getattr(battle, 'joiningSuits', ()),
            getattr(battle, 'pendingSuits', ())):
        for suit in group:
            if getattr(suit, 'doId', None) == doId:
                return suit
    return base.cr.doId2do.get(doId)


def _findToon(attack, doId):
    battle = attack.get('battle')
    if battle:
        for toon in getattr(battle, 'activeToons', ()):
            if getattr(toon, 'doId', None) == doId:
                return toon
    return base.cr.doId2do.get(doId)


def _parse(name):
    return name.split('_')


def _descriptionTrack(descText, description, duration, oneLine=False):
    wordwrap = 100000.0 if oneLine else 30.0
    return Sequence(
        Wait(0.5),
        LerpColorScaleInterval(
            descText, 0, Vec4(0.847, 0.784, 0.992, 1.0)),
        Func(descText.hide),
        Func(descText.textNode.setWordwrap, wordwrap),
        Func(descText.setPos, 0.0, 0.6625),
        Func(descText.setScale, 0.09),
        Func(descText.textNode.setText, description),
        LerpScaleInterval(descText, 0, (0, 0, 0)),
        Func(descText.show),
        Parallel(
            descText.scaleInterval(0.25, (1.2, 1.1, 1.1)),
            descText.posInterval(0.25, (0, 0, -0.040))),
        Parallel(
            descText.scaleInterval(0.25, (1.1, 1.1, 1.1)),
            descText.posInterval(0.25, (0, 0, -0.040))),
        Wait(max(0.0, duration - 0.5)),
        LerpColorScaleInterval(descText, 0.25, Vec4(0, 0, 0, 0)),
        Func(descText.hide))


def _cheatBanner(attack, title, description, duration, oneLine=False):
    pbpText = attack.get('playByPlayText')
    if pbpText is None:
        return Sequence()
    visibleDuration = max(0.75, float(duration) - 1.0)
    descText = PlayByPlayText.PlayByPlayText()
    descText.hide()
    return Sequence(
        Parallel(
            pbpText.getShowIntervalCheat(title, visibleDuration),
            _descriptionTrack(
                descText, description, visibleDuration, oneLine)),
        Func(descText.cleanup))


def _restore(attack):
    boss = _boss(attack)
    battle = attack.get('battle')
    if battle:
        try:
            camera.wrtReparentTo(battle)
        except:
            pass
    if boss:
        boss.restoreBattlePresentation(resetCamera=0)


def _finish(attack, track, title, description, oneLine=False):
    try:
        duration = track.getDuration()
    except:
        duration = 5.0
    return Sequence(
        Parallel(
            track,
            _cheatBanner(
                attack, title, description, duration, oneLine)),
        Func(_restore, attack))


def _say(suit, text, anim='finger-wag', duration=2.5, sfx=None):
    if not suit:
        return Sequence(Wait(0.01))
    tracks = [
        Sequence(
            Func(suit.setChatAbsolute, text, CFSpeech),
            ActorInterval(suit, anim),
            Func(suit.setChatAbsolute, '', CFSpeech),
            Func(suit.loop, 'neutral'))
    ]
    if sfx:
        tracks.append(SoundInterval(loader.loadSfx(sfx), node=suit))
    return Parallel(*tracks)


def _chat(suit, text, delay=0.0, duration=3.0):
    if not suit:
        return Sequence(Wait(0.01))
    return Sequence(
        Wait(delay),
        Func(suit.setChatAbsolute, text, CFSpeech),
        Wait(duration),
        Func(suit.setChatAbsolute, '', CFSpeech))


def _showHpString(suit, text):
    if not suit:
        return
    try:
        suit.hideHpText()
    except:
        pass
    try:
        suit.showHpString(text, 0.85, 0.7)
    except:
        try:
            suit.showHpTextNew(0, text=text, colorCode=1)
        except:
            pass


def doStandupGuy(attack):
    suit = attack['suit']
    phrases = (
        "Alright, that's enough. I'm takin' a stand.",
        "I can't stand seeing the rest of 'em get hurt!",
        "I won't stand for your harassment anymore.",
    )
    track = Sequence(
        Func(attack['battle'].unlureSuit, suit),
        _say(
            suit,
            random.choice(phrases),
            'defense',
            3.0,
            'phase_5/audio/sfx/SA_defense.ogg'))
    return _finish(
        attack, track,
        'STAND-UP GUY!',
        'CHARON IS ABSORBING DAMAGE DEALT TO OTHER COGS THIS ROUND!')


def _splicedThinkTrack(toon):
    track = Sequence()
    origDuration = 0.66
    newDuration = 1.9
    fps = 30.0
    numAnims = int(origDuration * fps)
    timeInterval = newDuration / (origDuration * fps)
    animInterval = origDuration / (origDuration * fps)
    addition = 0.0
    for unused in xrange(numAnims):
        track.append(Wait(timeInterval))
        track.append(ActorInterval(
            toon, 'think', startTime=2.06 + addition,
            duration=animInterval))
        addition += animInterval
    track.append(Wait(0.01))
    track.append(ActorInterval(toon, 'slip-backward', startTime=0.5))
    return track


def _showShortSqueezeCoin(coin, toon):
    coin.reparentTo(toon)
    coin.setPos(0, 0, toon.shoulderHeight - 0.2)
    coin.setHpr(
        random.randint(0, 359),
        random.randint(0, 359),
        random.randint(0, 359))
    coin.show()


def _shortSqueezeToonTrack(toon, battle, nix):
    ground = toon.getPos(battle)
    x = ground.getX()
    y = ground.getY()
    z = ground.getZ()
    shake = Sequence(Wait(1.0))
    for unused in xrange(5):
        shake.append(LerpPosInterval(
            toon, 0.15, Point3(x, y, z + 3.0), other=battle))
        shake.append(LerpPosInterval(
            toon, 0.15, Point3(x, y, z + 1.5), other=battle))
    shake.append(LerpPosInterval(toon, 0.15, ground, other=battle))

    initialScale = toon.getScale()
    squeeze = Sequence(
        Wait(1.0),
        Func(battle.movie.needRestoreToonScale),
        LerpScaleInterval(
            toon, 0.1,
            Point3(
                initialScale[0] * 0.6,
                initialScale[1] * 0.46,
                initialScale[2] * 1.2)),
        Wait(1.1),
        LerpScaleInterval(
            toon, 0.2,
            Point3(
                initialScale[0] * 1.2,
                initialScale[1] * 1.2,
                initialScale[2] * 0.8)),
        LerpScaleInterval(toon, 0.2, initialScale),
        Func(battle.movie.clearRestoreToonScale))

    coins = Parallel()
    coinTypes = ('bronze', 'silver', 'gold')
    for i in xrange(20):
        coin = loader.loadModel(
            'phase_3.5/models/props/cc_m_prp_gen_coin_%s.bam' %
            random.choice(coinTypes))
        land = Point3(
            x + random.uniform(-5.0, 5.0),
            y + random.uniform(-5.0, 5.0),
            z)
        coins.append(Sequence(
            Wait(1.1 + 0.05 * i),
            Func(_showShortSqueezeCoin, coin, toon),
            Func(coin.wrtReparentTo, battle),
            Parallel(
                LerpPosInterval(coin, 0.75, land, other=battle),
                LerpHprInterval(
                    coin, 0.75,
                    Point3(
                        random.randint(360, 720),
                        random.randint(360, 720),
                        random.randint(360, 720)))),
            Func(coin.removeNode)))

    reaction = Sequence(
        Func(toon.headsUp, nix),
        Wait(0.95),
        ActorInterval(toon, 'struggle', duration=1.25),
        ActorInterval(toon, 'slip-backward', startTime=0.5),
        Func(toon.loop, 'neutral'))

    sound = Track(
        (1.0, SoundInterval(
            globalBattleSoundCache.getSound('SA_short_squeeze.ogg'),
            node=toon)),
        (2.4, SoundInterval(
            globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'),
            node=toon)))
    return Parallel(shake, squeeze, coins, reaction, sound)


def doShakedown(attack):
    parts = _parse(attack['name'])
    toonId = int(parts[-2]) if len(parts) > 2 else 0
    mode = int(parts[-1]) if len(parts) > 1 else 0
    toon = _findToon(attack, toonId)
    nix = attack['suit']
    battle = attack['battle']
    phrases = (
        "Maybe this'll shake some sense into ya.",
        "No one ever gave ya the rundown on how this place works, ey?",
        "Ya look a little shaken up, Toon.",
        "Let's shake things up.",
    )
    toonTrack = Sequence()
    if toon:
        toonTrack = _shortSqueezeToonTrack(toon, battle, nix)
    suitTrack = Sequence(
        Func(battle.unlureSuit, nix),
        Func(nix.setChatAbsolute, random.choice(phrases), CFSpeech),
        ActorInterval(nix, 'short-squeeze'),
        Func(nix.setChatAbsolute, '', CFSpeech),
        Func(nix.loop, 'neutral'))
    actionTrack = Parallel(suitTrack, toonTrack)
    totalDuration = actionTrack.getDuration()
    if toon:
        cameraTrack = MovieCamera.randomAttackCam(
            nix, toon, battle, totalDuration, 1.6, 'suit')
    else:
        cameraTrack = Sequence(Wait(totalDuration))
    track = Parallel(actionTrack, cameraTrack)
    description = (
        'NIX INFLICTS A RANDOM TOON WITH A REWARD COOLDOWN!'
        if mode == 0 else
        'NIX INFLICTS A RANDOM TOON WITH A DAMAGE VULNERABILITY!')
    return _finish(attack, track, 'SHAKEDOWN!', description)

def doGhostPayroll(attack):
    responses = {
        'charon': "Guess we gotta make use of this raise somehow!",
        'nix': "We ain't forgettin' ya, gotta use this while it lasts!",
        'kerberos': "Every little bit counts in tha end!",
        'hydra': "Money can't provide happiness above the family, but it'll do for now!",
        'styx': "I'm sure tha raise will be put ta good use!",
    }
    suit = attack['suit']
    name = getattr(getattr(suit, 'dna', None), 'name', '')
    track = _say(
        suit,
        responses.get(name, 'Ghost Payroll!'),
        'mob-mentality',
        3.5,
        'phase_5/audio/sfx/SA_extra_tip.ogg')
    return _finish(
        attack, track,
        'GHOST PAYROLL!',
        'EACH SATELLITE INVESTOR DEFEATED GIVES A DAMAGE BUFF!')


def doSlushFund(attack):
    suit = attack['suit']
    battle = attack['battle']
    phrases = (
        "Do I gotta provide the muscle for ya?!",
        "Consider this ya share for this operation.",
        "C'mon ya neutron stars, keep yourselves together!",
        "I said I wouldn't let anyone mess with ya, didn't I?!",
    )
    fundTracks = Parallel()
    for target in getattr(battle, 'activeSuits', ()):
        if target is suit:
            continue
        try:
            effectA = BattleParticles.createParticleEffect(file='backburnerBuff')
            effectB = BattleParticles.createParticleEffect(file='backburnerBuff')
            effectB.setH(180)
            BattleParticles.setEffectTexture(
                effectA, 'dollar-sign',
                color=(0.5 * random.random() + 0.3, 0.8, 1, 1))
            BattleParticles.setEffectTexture(
                effectB, 'dollar-sign',
                color=(0.5 * random.random() + 0.3, 0.8, 1, 1))
            fundTracks.append(Parallel(
                ParticleInterval(
                    effectA, target, worldRelative=0,
                    duration=2.6, cleanup=True),
                ParticleInterval(
                    effectB, target, worldRelative=0,
                    duration=2.6, cleanup=True),
                Sequence(Wait(1.6), Func(_showHpString, target, 'FUNDED!'))))
        except:
            fundTracks.append(
                Sequence(Wait(1.6), Func(_showHpString, target, 'FUNDED!')))
    track = Parallel(
        Sequence(
            Func(battle.unlureSuit, suit),
            _say(
                suit,
                random.choice(phrases),
                'mob-mentality',
                4.0,
                'phase_5/audio/sfx/SA_extra_tip.ogg')),
        SoundInterval(
            loader.loadSfx(
                'phase_5/audio/sfx/SA_life_insurance_register.ogg'),
            node=suit),
        fundTracks)
    name = getattr(getattr(suit, 'dna', None), 'name', 'pcrat')
    displayName = {
        'pcrat': 'PLUTOCRAT',
        'charon': 'CHARON',
        'nix': 'NIX',
        'hydra': 'HYDRA',
        'styx': 'STYX',
        'kerberos': 'KERBEROS',
    }.get(name, 'THE COG')
    return _finish(
        attack, track,
        'SLUSH FUND!',
        '%s BUFFS THE DEFENSES OF ALL OTHER COGS!' % displayName)


def doKickUp(attack):
    boss = _boss(attack)
    parts = _parse(attack['name'])
    target = _findSuit(attack, int(parts[-1]))
    hydra = attack['suit']
    if not boss or not target:
        return Sequence(Wait(0.01))
    phrases = (
        "Look out, this might have a bit of a kick.",
        "I bet an extra kick will send 'em flyin'.",
        "Ya gonna be kickin' yourself for not plannin' ahead, Toon.",
        "We'll get a kick out of this.",
    )
    track = Parallel(
        Sequence(
            Func(attack['battle'].unlureSuit, hydra),
            PlutocratCutscenes.makeKickUp(boss, hydra, target, attack['battle'])),
        Sequence(Wait(1.143), Func(_showHpString, target, 'DAMAGE UP!')),
        _chat(hydra, random.choice(phrases), duration=4.0))
    targetName = getattr(
        getattr(target, 'dna', None), 'name', 'COG').upper()
    return _finish(
        attack, track, 'KICK UP!',
        'HYDRA GIVES A DAMAGE BUFF TO %s!' % targetName)


def doSitdown(attack):
    boss = _boss(attack)
    styx = attack['suit']
    if not boss:
        return Sequence(Wait(0.01))
    phrases = (
        "Let me introduce ya to my little friend.",
        "Waiter, please.",
        "I think ya gonna like this one, they's a good fella.",
    )
    bell = 'phase_8/audio/sfx/ttcc_int_psetter_bell.ogg'
    track = Parallel(
        Sequence(
            Func(attack['battle'].unlureSuit, styx),
            PlutocratCutscenes.makeSitdown(boss, styx, attack['battle'])),
        Sequence(Wait(0.40), SoundInterval(loader.loadSfx(bell))),
        Sequence(Wait(0.56), SoundInterval(loader.loadSfx(bell))),
        _chat(styx, random.choice(phrases), delay=0.1, duration=3.2))
    return _finish(
        attack, track, 'SITDOWN!', 'STYX SUMMONS A WAITER!')


def doUsuryWaiter(attack):
    boss = _boss(attack)
    parts = _parse(attack['name'])
    waiter = _findSuit(attack, int(parts[-2]))
    styx = attack['suit']
    if not boss or not waiter:
        return Sequence(Wait(0.01))
    phrases = (
        "These rates are astronomical!",
        "Ya gonna be light-years away from paying your debts.",
        'Consider this a fiscal "black hole," if ya will.',
    )
    track = Parallel(
        Sequence(
            Func(attack['battle'].unlureSuit, styx),
            PlutocratCutscenes.makeUsury(boss, styx, waiter, attack['battle'])),
        _chat(styx, random.choice(phrases), duration=5.0))
    return _finish(
        attack, track, 'USURY!',
        "STYX STEALS SOME OF THE WAITER'S HEALTH!")


def doUsuryFodder(attack):
    boss = _boss(attack)
    parts = _parse(attack['name'])
    fodders = []
    for token in parts[1:]:
        try:
            target = _findSuit(attack, int(token))
        except:
            target = None
        if target:
            fodders.append(target)
    styx = attack['suit']
    if not boss or not fodders:
        return Sequence(Wait(0.01))
    phrases = (
        "These rates are astronomical!",
        "Ya gonna be light-years away from paying your debts.",
        'Consider this a fiscal "black hole," if ya will.',
    )
    track = Parallel(
        Sequence(
            Func(attack['battle'].unlureSuit, styx),
            PlutocratCutscenes.makeUsuryFodder(boss, styx, fodders, attack['battle'])),
        _chat(styx, random.choice(phrases), duration=5.0))
    return _finish(
        attack, track, 'USURY!',
        "STYX STEALS SOME OF THE COGS' HEALTH!")


def doTribute(attack):
    boss = _boss(attack)
    parts = _parse(attack['name'])
    target = _findSuit(attack, int(parts[-3]))
    kerberos = attack['suit']
    if not boss or not target:
        return Sequence(Wait(0.01))
    phrases = (
        "In honor of my fallen Satellites.",
        "To the Don!",
        "Suits like us gotta look out for each other.",
    )
    track = Parallel(
        Sequence(
            Func(attack['battle'].unlureSuit, kerberos),
            Func(attack['battle'].unlureSuit, target),
            PlutocratCutscenes.makeTribute(boss, kerberos, target, attack['battle'])),
        _chat(kerberos, random.choice(phrases), duration=5.5))
    targetName = getattr(
        getattr(target, 'dna', None), 'name', 'COG').upper()
    return _finish(
        attack, track, 'TRIBUTE!',
        'KERBEROS GIVES UP SOME HEALTH TO %s!' % targetName)


def _deepFreezeParticles(attack):
    tracks = Parallel()
    for target in getattr(attack['battle'], 'activeToons', ()):
        try:
            effect = BattleParticles.loadParticleFile(
                'plutocratDeepFreeze.ptf')
            node = target.attachNewNode(
                'plutocratDeepFreeze-%s' % target.doId)
            node.setZ(-3)
            tracks.append(Sequence(
                ParticleInterval(
                    effect, node, worldRelative=0,
                    duration=4.0, cleanup=True),
                Func(node.removeNode)))
        except:
            pass
    return tracks


def doDeepFreeze(attack):
    boss = _boss(attack)
    plutocrat = attack['suit']
    if not boss:
        return Sequence(Wait(0.01))
    parts = _parse(attack['name'])
    rounds = int(parts[-1])
    phrases = (
        "I refuse to be dwarfed by the likes of you!",
        "Ya won't be able to handle the gravity of this!",
        "Y'know what? It's 'bout time you take a chill pill.",
        "You've gone and done it now, haven'tcha!",
    )
    toonReactions = Parallel()
    for toon in getattr(attack['battle'], 'activeToons', ()):
        try:
            toonReactions.append(Sequence(
                Func(toon.headsUp, attack['battle'], plutocrat.getPos(attack['battle'])),
                Wait(2.1),
                ActorInterval(toon, 'cringe', playRate=0.4),
                Func(toon.loop, 'neutral')))
        except:
            pass
    track = Parallel(
        Sequence(
            Func(attack['battle'].unlureSuit, plutocrat),
            PlutocratCutscenes.makeDeepFreeze(boss, plutocrat, attack['battle'])),
        _say(
            plutocrat,
            random.choice(phrases),
            'magic3',
            5.5),
        Sequence(
            Wait(1.2),
            SoundInterval(
                loader.loadSfx(
                    'phase_10/audio/sfx/SA_deepfreeze.ogg'),
                node=plutocrat)),
        Sequence(
            Wait(1.5),
            Func(boss.applyDeepFreezeVisuals, rounds)),
        _deepFreezeParticles(attack),
        toonReactions)
    return _finish(
        attack, track, 'DEEP FREEZE!', 'ALL TOONS SLOW DOWN!')


def doSnowSquall(attack):
    boss = _boss(attack)
    plutocrat = attack['suit']
    if not boss:
        return Sequence(Wait(0.01))
    active = bool(int(_parse(attack['name'])[-1]))
    if active:
        phrase = random.choice((
            "I'm 'boutta storm up a squall ya wont ever forget!",
            "This is really gonna freeze ya up, chumps!",
        ))
        description = "THE ROOM'S TEMPERATURE HAS GONE BELOW FREEZING!"
    else:
        phrase = random.choice((
            "The squall ain't over just yet!",
            "Ya still gonna be frozen in fear even after this is over!",
        ))
        description = "THE ROOM'S TEMPERATURE HAS RETURNED TO NORMAL!"
    track = Parallel(
        Sequence(
            Func(attack['battle'].unlureSuit, plutocrat),
            PlutocratCutscenes.makeSnowSquall(
                boss, plutocrat, active, attack['battle'])),
        _say(plutocrat, phrase, 'effort', 5.0),
        Sequence(
            Wait(1.5),
            Func(boss.setSnowSquallActive, active)))
    return _finish(
        attack, track, 'SNOW SQUALL!', description)


def _damageToons(attack):
    for target in attack.get('target', ()):
        toon = target.get('toon')
        damage = target.get('hp', 0)
        if toon and damage > 0:
            try:
                toon.showHpText(-damage, openEnded=0)
            except:
                pass
            try:
                toon.takeDamage(damage)
            except:
                pass


def _temporaryColdColor(attack):
    tracks = Parallel()
    for target in attack.get('target', ()):
        toon = target.get('toon')
        if not toon:
            continue
        for part in (
                list(toon.getHeadParts()) +
                list(toon.getTorsoParts()) +
                list(toon.getLegsParts())):
            tracks.append(Sequence(
                LerpColorScaleInterval(
                    part, 0.5, Vec4(0.5, 0.9, 1.0, 1.0)),
                Wait(4.5),
                LerpColorScaleInterval(
                    part, 0.5, Vec4(1, 1, 1, 1))))
    return tracks


def doSnowSquallDamage(attack):
    boss = _boss(attack)
    if not boss:
        return Sequence(Func(_damageToons, attack))
    track = Parallel(
        PlutocratCutscenes.makeSnowSquallDamage(boss, attack['battle']),
        _temporaryColdColor(attack),
        Sequence(Wait(6.0), Func(_damageToons, attack)))
    return _finish(
        attack, track,
        'SNOW SQUALL!',
        'ALL TOONS ARE BUFFETED BY THE SNOW SQUALL!')


def doFreezeSuit(attack):
    boss = _boss(attack)
    parts = _parse(attack['name'])
    if not boss or len(parts) < 3:
        return Sequence(Wait(0.01))
    suit = _findSuit(attack, int(parts[-2]))
    try:
        rounds = int(parts[-1])
    except:
        rounds = 1
    if not suit:
        return Sequence(Wait(0.01))
    return Sequence(
        Func(boss.applyFrozenSuitVisual, suit, rounds),
        Wait(0.01))


def _shatterHitSound():
    sound = loader.loadSfx('phase_10/audio/sfx/SA_shatter_hit.ogg')
    if sound:
        return sound
    return loader.loadSfx('phase_10/audio/sfx/SA_shatter.ogg')


def doShatter(attack):
    parts = _parse(attack['name'])
    if len(parts) < 6:
        return Sequence(Wait(0.01))
    battle = attack['battle']
    sourceId = int(parts[1])
    data = parts[2:]
    source = _findSuit(attack, sourceId)
    damageTracks = Parallel()
    bubbleBurst = False
    i = 0
    while i + 3 < len(data):
        targetId = int(data[i])
        damage = int(data[i + 1])
        burst = int(data[i + 2])
        died = int(data[i + 3])
        i += 4
        target = _findSuit(attack, targetId)
        if not target:
            continue
        react = random.choice(('squirt-small-react', 'pie-small-react'))
        hitTrack = Sequence(
            Parallel(
                SoundInterval(_shatterHitSound(), node=target),
                ActorInterval(target, react),
                Sequence(
                    Wait(0.1),
                    Func(target.showHpText, -damage, openEnded=0),
                    Func(target.updateHealthBar, damage))),
            Func(target.loop, 'neutral'))
        if died:
            hitTrack = Sequence(
                hitTrack,
                MovieUtil.createSuitDeathTrack(target, battle))
        if burst:
            bubbleBurst = True
            try:
                suitPos, unusedHpr = battle.getActorPosHpr(target)
                explosionPoint = Point3(
                    suitPos.getX(), suitPos.getY(),
                    suitPos.getZ() + target.height - 0.5)
                burstTrack = Parallel(
                    Sequence(
                        Wait(2.0),
                        Func(target.hideHpText),
                        Func(target.showHpString,
                             'BUBBLE BURST!', 0.85, 0.7)),
                    MovieUtil.createKapowExplosionTrack(
                        battle, explosionPoint=explosionPoint))
            except:
                burstTrack = Sequence(
                    Wait(2.0),
                    Func(target.hideHpText),
                    Func(target.showHpString,
                         'BUBBLE BURST!', 0.85, 0.7))
            hitTrack = Parallel(hitTrack, burstTrack)
        damageTracks.append(hitTrack)
    if source:
        try:
            source.hideHpText()
        except:
            pass
    title = 'SHATTER!'
    description = 'A FROZEN COG SHATTERS AND DAMAGES ADJACENT COGS!'
    if bubbleBurst:
        description = "SHATTER BURSTS THE PLUTOCRAT'S MARKET BUBBLE!"
    return _finish(attack, damageTracks, title, description)

