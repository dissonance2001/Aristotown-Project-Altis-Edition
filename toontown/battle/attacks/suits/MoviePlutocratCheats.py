from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Point3, Vec4
from toontown.battle import BattleParticles
from toontown.battle import MovieUtil
from toontown.battle import PlayByPlayText
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
    track = _say(
        suit,
        random.choice(phrases),
        'defense',
        3.0,
        'phase_5/audio/sfx/SA_defense.ogg')
    return _finish(
        attack, track,
        'STAND-UP GUY!',
        'CHARON IS ABSORBING DAMAGE DEALT TO OTHER COGS THIS ROUND!')


def doShakedown(attack):
    parts = _parse(attack['name'])
    toonId = int(parts[-2]) if len(parts) > 2 else 0
    mode = int(parts[-1]) if len(parts) > 1 else 0
    toon = _findToon(attack, toonId)
    suit = attack['suit']
    phrases = (
        "Maybe this'll shake some sense into ya.",
        "No one ever gave ya the rundown on how this place works, ey?",
        "Ya look a little shaken up, Toon.",
        "Let's shake things up.",
    )
    toonTrack = Parallel()
    if toon:
        ground = toon.getPos(attack['battle'])
        rise = Point3(ground[0], ground[1], ground[2] + 3.0)
        left = Point3(rise[0], rise[1] - 0.7, rise[2])
        right = Point3(rise[0], rise[1] + 0.7, rise[2])
        shake = Sequence(
            Wait(1.6),
            LerpPosInterval(toon, 1.0, rise, other=attack['battle']))
        for i in xrange(12):
            shake.append(LerpPosInterval(
                toon, 0.035, left, other=attack['battle']))
            shake.append(LerpPosInterval(
                toon, 0.035, right, other=attack['battle']))
        shake.append(LerpPosInterval(
            toon, 0.15, ground, other=attack['battle']))
        try:
            lift = BattleParticles.createParticleEffect('ShiftLift')
            lift.setPos(ground)
            particle = ParticleInterval(
                lift, attack['battle'], worldRelative=0,
                duration=3.8, cleanup=True)
        except:
            particle = Sequence()
        toonTrack = Parallel(shake, particle)
    track = Parallel(
        _say(
            suit,
            random.choice(phrases),
            'magic3',
            4.5,
            'phase_5/audio/sfx/SA_paradigm_shift.ogg'),
        toonTrack)
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
        _say(
            suit,
            random.choice(phrases),
            'mob-mentality',
            4.0,
            'phase_5/audio/sfx/SA_extra_tip.ogg'),
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
        PlutocratCutscenes.makeKickUp(boss, hydra, target),
        Sequence(Wait(1.143), Func(_showHpString, target, 'DAMAGE UP!')),
        _say(hydra, random.choice(phrases), 'throw-object', 4.0))
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
    bell = 'phase_5/audio/sfx/ttcc_int_psetter_bell.ogg'
    track = Parallel(
        PlutocratCutscenes.makeSitdown(boss, styx),
        Sequence(Wait(0.40), SoundInterval(loader.loadSfx(bell))),
        Sequence(Wait(0.56), SoundInterval(loader.loadSfx(bell))),
        _say(styx, random.choice(phrases), 'sit-hungry-left', 3.5))
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
        PlutocratCutscenes.makeUsury(boss, styx, waiter),
        _say(styx, random.choice(phrases), 'effort', 5.0))
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
        PlutocratCutscenes.makeUsuryFodder(boss, styx, fodders),
        _say(styx, random.choice(phrases), 'effort', 5.0))
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
        PlutocratCutscenes.makeTribute(boss, kerberos, target),
        _say(kerberos, random.choice(phrases), 'effort', 5.5))
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
    track = Parallel(
        PlutocratCutscenes.makeDeepFreeze(boss, plutocrat),
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
        _deepFreezeParticles(attack))
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
        PlutocratCutscenes.makeSnowSquall(
            boss, plutocrat, active),
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
        PlutocratCutscenes.makeSnowSquallDamage(boss),
        _temporaryColdColor(attack),
        Sequence(Wait(5.5), Func(_damageToons, attack)))
    return _finish(
        attack, track,
        'SNOW SQUALL!',
        'ALL TOONS ARE BUFFETED BY THE SNOW SQUALL!')


def doShatter(attack):
    parts = _parse(attack['name'])
    if len(parts) < 5:
        return Sequence(Wait(0.01))
    battle = attack['battle']
    sourceId = int(parts[1])
    data = parts[2:]
    source = _findSuit(attack, sourceId)
    damageTracks = Parallel()
    bubbleBurst = False
    i = 0
    while i + 2 < len(data):
        targetId = int(data[i])
        damage = int(data[i + 1])
        burst = int(data[i + 2])
        i += 3
        target = _findSuit(attack, targetId)
        if not target:
            continue
        react = random.choice(('squirt-small-react', 'pie-small-react'))
        seq = Sequence(
            Parallel(
                SoundInterval(
                    loader.loadSfx('phase_10/audio/sfx/SA_shatter_hit.ogg'),
                    node=target),
                ActorInterval(target, react),
                Sequence(
                    Wait(0.1),
                    Func(target.showHpText, -damage, openEnded=0))),
            Func(target.loop, 'neutral'))
        if burst:
            bubbleBurst = True
            seq = Parallel(
                seq,
                Sequence(
                    Wait(1.4),
                    Func(target.hideHpText),
                    Func(target.showHpString, 'BUBBLE BURST!', 0.85, 0.7)))
        damageTracks.append(seq)
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
