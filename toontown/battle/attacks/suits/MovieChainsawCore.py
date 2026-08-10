from direct.interval.IntervalGlobal import *
from panda3d.core import Point3, VBase3, Vec4

from toontown.battle import MovieUtil
from toontown.battle import PlayByPlayText
from toontown.battle import SuitBattleGlobals
from toontown.battle.BattleProps import globalPropPool
from toontown.effects import DustCloud
from toontown.cutscene.ChainsawBattleCutscenes import makeChainsawBattleCutscene


def _damage(toon, dmg, died=0):
    if toon and dmg > 0 and getattr(toon, 'hp', None) is not None:
        toon.takeDamage(dmg)


def _damageTrack(attack, delay):
    track = Parallel()
    for target in attack.get('target', ()):
        toon = target.get('toon')
        dmg = target.get('hp', 0)
        died = target.get('died', 0)
        if toon and dmg > 0:
            track.append(Sequence(
                Wait(delay),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(_damage, toon, dmg, died)))
    return track


def _controller(attack):
    return getattr(attack.get('battle'), 'bossCog', None)


def _syncMeter(attack):
    controller = _controller(attack)
    if not controller:
        return
    meter = getattr(controller, 'chainsawMeter', None)
    if meter:
        try:
            meter.setPhase(controller.chainsawPhase)
            meter.setRPM(controller.chainsawRPM)
        except:
            pass


def _spendMeter(attack, stacks):
    controller = _controller(attack)
    if not controller:
        return
    meter = getattr(controller, 'chainsawMeter', None)
    if not meter:
        return
    try:
        meter.setPhase(controller.chainsawPhase)
        meter.setRPM(max(10, int(round(float(meter.rpm))) - int(stacks)))
    except:
        pass


def _setToonStatusEffect(toon, name, modifier=1, turns=None, mode='setBoth'):
    if not toon:
        return
    if turns is not None and turns > 0:
        turns += 1
    try:
        toon.setToonStatusEffect(name, modifier, turns, mode)
    except:
        pass


def _setSuitStatusEffect(suit, name, modifier=0, turns=None, mode='setBoth'):
    if not suit:
        return
    if turns is not None and turns > 0:
        turns += 1
    try:
        suit.setSuitStatusEffect(name, modifier, turns, mode)
    except:
        pass


def _applyMarkedWoodStatus(toon):
    _setToonStatusEffect(toon, 'vulnerable', 75, 2, 'keepHighest')


def _applyThrottleVulnerability(toon):
    _setToonStatusEffect(toon, 'vulnerable', 25, 2, 'keepHighest')


def _showSuitHpStringCompat(suit, text, duration=0.85, scale=1.0):
    # Current Clash accepts an optional color argument here; Altis's older
    # DistributedSuitBase.showHpString only accepts text/duration/scale.
    try:
        suit.showHpString(text, duration, scale)
        return
    except:
        pass
    try:
        suit.showHpTextNew(0, text=text, colorCode=1)
    except:
        pass


def _getDisplayedRPM(attack):
    controller = _controller(attack)
    if controller is None:
        return None
    meter = getattr(controller, 'chainsawMeter', None)
    if meter is None:
        return None
    try:
        return int(round(float(meter.rpm)))
    except:
        return None


def _descriptionTrack(descText, description, duration, oneLine=False):
    wordwrap = 100000.0 if oneLine else 30.0
    return Sequence(
        Wait(0.5),
        LerpColorScaleInterval(descText, 0, Vec4(0.847, 0.784, 0.992, 1.0)),
        Func(descText.hide),
        Func(descText.textNode.setWordwrap, wordwrap),
        Func(descText.setPos, 0.0, 0.6625),
        Func(descText.setScale, 0.09),
        Func(descText.textNode.setText, description),
        LerpScaleInterval(descText, duration=0, scale=(0, 0, 0)),
        descText.posInterval(0, (0, 0, 0.6625)),
        Func(descText.show),
        Wait(0.5),
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
    try:
        visibleDuration = max(0.5, float(duration) - 2.0)
    except:
        visibleDuration = 3.0
    descText = PlayByPlayText.PlayByPlayText()
    descText.hide()
    return Sequence(
        Parallel(
            pbpText.getShowIntervalCheat(title, visibleDuration),
            _descriptionTrack(descText, description, visibleDuration, oneLine)),
        Func(descText.cleanup))


def _withCheatBanner(attack, track, title, description, oneLine=False):
    try:
        duration = track.getDuration()
    except:
        duration = 5.0
    return Parallel(
        track,
        _cheatBanner(attack, title, description, duration, oneLine))


def _orderedSuits(battle):
    suits = []
    for suit in getattr(battle, 'suits', ()):
        if suit and suit not in suits:
            suits.append(suit)
    for suit in getattr(battle, 'activeSuits', ()):
        if suit and suit not in suits:
            suits.append(suit)
    return suits


def _supportByIndex(attack, index):
    battle = attack['battle']

    # The AI encodes the target using battle.activeSuits.index().  Use that
    # exact list first on the client.  battle.suits may contain old/dead/reserve
    # entries and was the reason Cut the Slack animated a different Cog than
    # the one the server actually promoted.
    active = list(getattr(battle, 'activeSuits', ()) or ())
    if index >= 0 and index < len(active):
        candidate = active[index]
        if candidate is not attack['suit']:
            return candidate

    # Fallback only for older battle implementations which do not expose the
    # active list consistently.
    suits = _orderedSuits(battle)
    if index >= 0 and index < len(suits):
        candidate = suits[index]
        if candidate is not attack['suit']:
            return candidate
    return None


def _parseTrailingIndices(name, prefix):
    suffix = name[len(prefix):]
    result = []
    for char in suffix:
        if char.isdigit():
            result.append(int(char))
    return result


def _parseCutSlackName(name):
    suffix = name[len('ChainsawCoreCutTheSlack'):]
    if 'S' not in suffix:
        indices = _parseTrailingIndices(name, 'ChainsawCoreCutTheSlack')
        return (indices[0] if indices else -1, [])
    targetText, sacrificeText = suffix.split('S', 1)
    try:
        targetIndex = int(targetText)
    except:
        targetIndex = -1
    sacrificeIndices = []
    for char in sacrificeText:
        if char.isdigit():
            sacrificeIndices.append(int(char))
    return targetIndex, sacrificeIndices


def _parseIndexedLevelName(name, prefix):
    suffix = name[len(prefix):]
    if 'L' not in suffix:
        indices = _parseTrailingIndices(name, prefix)
        return (indices[0] if indices else -1, None)
    indexText, levelText = suffix.split('L', 1)
    try:
        index = int(indexText)
    except:
        index = -1
    try:
        level = int(levelText)
    except:
        level = None
    return index, level


def _promotionCloud(target):
    cloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
    cloud.setBillboardAxis(2.0)
    cloud.setZ(3)
    cloud.setScale(1.0)
    cloud.createTrack()
    return Sequence(
        Func(cloud.reparentTo, target),
        cloud.track,
        Func(cloud.destroy))



def _applyPromotion(target, actualLevel, battle=None, aggrandized=False):
    if not target or actualLevel is None:
        return
    try:
        relativeLevel = SuitBattleGlobals.getRelativeFromActualLevel(
            target.dna.name, actualLevel)
        target.setLevel(relativeLevel)
    except:
        return
    try:
        target.setExecutive(1)
    except:
        pass
    try:
        target.setManager(1)
    except:
        pass
    try:
        for name in list(target.getSuitStatusEffects().keys()):
            if name != 'overcharged':
                target.clearSuitStatusEffect(name)
    except:
        pass
    _setSuitStatusEffect(
        target, 'chainsawManagerBeneficiary', 1, None, 'setBoth')
    if aggrandized:
        _setSuitStatusEffect(
            target, 'chainsawAggrandized', 1, None, 'setBoth')
    if battle:
        try:
            battle.unlureSuit(target)
        except:
            pass
    try:
        target.setDisplayName(target.createNameInfo())
    except:
        pass
    try:
        target.healthBar.updateHealthBar(forceUpdate=1)
    except:
        pass

def _applyScabbardState(suit, finalHP, finalMax, overcharged=False):
    if not suit:
        return
    try:
        current = int(suit.getHP())
    except:
        current = int(getattr(suit, 'currHP', finalHP))
    try:
        suit.setMaxHP2(int(finalMax))
    except:
        try:
            suit.maxHP = int(finalMax)
        except:
            pass
    heal = max(0, int(finalHP) - current)
    if heal > 0:
        try:
            suit.showHpTextNew(-heal)
        except:
            pass
        try:
            suit.updateHealthBar(-heal, forceUpdate=1)
        except:
            try:
                suit.setHP(int(finalHP))
            except:
                pass
    else:
        try:
            suit.setHP(int(finalHP))
            suit.updateHealthBar(0, forceUpdate=1)
        except:
            pass
    try:
        if int(suit.getHP()) != int(finalHP):
            suit.setHP(int(finalHP))
            suit.updateHealthBar(0, forceUpdate=1)
    except:
        pass
    if overcharged:
        _setSuitStatusEffect(suit, 'overcharged', 50, None, 'setBoth')


def _parseScabbardStates(attack):
    name = attack.get('name', '')
    suffix = name[len('ChainsawCoreScabbard'):].strip('_')
    if not suffix:
        return []
    values = suffix.split('_')
    result = []
    for offset in xrange(0, len(values) - 3, 4):
        try:
            index = int(values[offset])
            finalHP = int(values[offset + 1])
            finalMax = int(values[offset + 2])
            overcharged = bool(int(values[offset + 3]))
        except:
            continue
        result.append((index, finalHP, finalMax, overcharged))
    return result


def _loopSuitNeutral(suit):
    suit.setNeutralAnimationDrop()
    # try:
    #     suit.loop('lured' if suit.isLured else 'neutral')
    # except:
    #     try:
    #         suit.loop('neutral')
    #     except:
    #         pass


def _parseRevvingGain(attack, whipsaw):
    prefix = 'ChainsawCoreWhipsaw' if whipsaw else 'ChainsawCoreRevvingUp'
    suffix = attack.get('name', '')[len(prefix):]
    parts = suffix.split('_', 1)
    try:
        gained = max(0, int(parts[0]))
    except:
        gained = None
    bonus = None
    if whipsaw and len(parts) > 1:
        try:
            bonus = max(0, int(parts[1]))
        except:
            bonus = None
    return gained, bonus


def doRevvingUp(attack, whipsaw=False):
    suit = attack['suit']
    oldRPM = _getDisplayedRPM(attack)
    controller = _controller(attack)
    newRPM = getattr(controller, 'chainsawRPM', oldRPM) if controller else oldRPM
    gainedStacks, whipsawStacks = _parseRevvingGain(attack, whipsaw)
    if gainedStacks is None:
        try:
            gainedStacks = max(0, int(newRPM) - int(oldRPM))
        except:
            gainedStacks = 0
    gain = gainedStacks * 1000
    try:
        rpm = max(1, min(int(newRPM), 10000))
    except:
        rpm = 1

    rpmRoll = max(1, min(int(newRPM), 10000))

    slowDuration = 1.6
    fastDuration = 0.15

    texDuration = slowDuration - (
        (rpmRoll - 1) / 9999.0
    ) * (slowDuration - fastDuration)
    suit.setChainsawTexRoll(texDuration)
    _setSuitStatusEffect(
        suit, 'chainsawRevvingUp', int(newRPM), None, 'setBoth')
    if whipsaw:
        if whipsawStacks is None:
            phase = getattr(controller, 'chainsawPhase', 1) if controller else 1
            whipsawStacks = 2 * (2 if phase == 3 else 1)
        whipsawGain = min(gain, whipsawStacks * 1000)
        normalGain = max(0, gain - whipsawGain)
        desc = 'THE CHAINSAW CONSULTANT GAINS +%s RPM!' % format(normalGain, ',d')
        desc += '\n(WHIPSAW: +%s RPM)' % format(whipsawGain, ',d')
    else:
        desc = 'THE CHAINSAW CONSULTANT GAINS +%s RPM!' % format(gain, ',d')
    track = makeChainsawBattleCutscene(attack, 'revvedup')
    return _withCheatBanner(attack, track, 'REVVING-UP!', desc)


def doPhaseTwo(attack):
    return makeChainsawBattleCutscene(attack, 'phasetwo')


def doPhaseThree(attack):
    return Sequence(
        Func(attack['battle'].setChainsawChainVisualActive, False),
        makeChainsawBattleCutscene(attack, 'phasethree'))


def doOffboarding(attack):
    indices = _parseTrailingIndices(
        attack.get('name', ''), 'ChainsawCoreOffboarding')
    support = _supportByIndex(attack, indices[0]) if indices else None
    track = Sequence(
        Func(_spendMeter, attack, 2),
        Parallel(
            makeChainsawBattleCutscene(
                attack, 'offboarding', supportSuit=support),
            _damageTrack(attack, 6.0)))
    return _withCheatBanner(
        attack, track, 'OFFBOARDING!',
        'THE CHAINSAW CONSULTANT FIRES A COG... LITERALLY!')


def doCutTheSlack(attack):
    suit = attack['suit']
    targetIndex, sacrificeIndices = _parseCutSlackName(
        attack.get('name', ''))
    target = _supportByIndex(attack, targetIndex)
    if target is None:
        return Sequence(Func(_spendMeter, attack, 4), Wait(2.0))

    targetTrack = Sequence(
        Wait(2.0),
        Func(_applyPromotion, target, 30, attack['battle']),
        Parallel(
            _promotionCloud(target),
            Func(_showSuitHpStringCompat, target, 'PROMOTED!', 0.85, 0.7),
            ActorInterval(target, 'slip-forward', startTime=2.43, partName='modelRoot')),
        Func(_loopSuitNeutral, target))

    sacrificeTrack = Parallel()
    for index in sacrificeIndices:
        support = _supportByIndex(attack, index)
        if support is None or support is target:
            continue
        sacrificeTrack.append(
            MovieUtil.shortCircuitTrack(support, attack['battle']))

    sfx = loader.loadSfx('phase_11/audio/sfx/SA_bash.ogg')
    track = Sequence(
        Func(_spendMeter, attack, 4),
        Parallel(
            ActorInterval(suit, 'snap-override', partName='modelRoot'),
            Sequence(Wait(0.1), SoundInterval(sfx, node=suit)),
            Sequence(Wait(1.0), sacrificeTrack),
            targetTrack))
    return _withCheatBanner(
        attack, track, 'CUT THE SLACK!',
        'THE CHAINSAW CONSULTANT POWERS UP THE STRONGEST EMPLOYEE!')


def doMarkedWood(attack):
    suit = attack['suit']
    targets = attack.get('target', ())
    if not targets:
        return Sequence()
    target = targets[0]
    toon = target.get('toon')
    dmg = target.get('hp', 0)
    died = target.get('died', 0)
    if toon is None:
        return Sequence()

    try:
        log = globalPropPool.getProp('treekiller_log')
    except:
        log = None
    if log is None or log.isEmpty():
        track = Sequence(
            Func(_spendMeter, attack, 7),
            Parallel(
                ActorInterval(suit, 'throw-object', partName='modelRoot'),
                _damageTrack(attack, 3.66),
                Sequence(Wait(3.66), Func(_applyMarkedWoodStatus, toon))))
        return _withCheatBanner(
            attack, track, 'MARKED WOOD!',
            'THE CHAINSAW CONSULTANT MARKS THE MOST DANGEROUS TOON FOR TERMINATION!')

    try:
        rightHand = suit.getRightHand()
    except:
        rightHand = suit
    toonPoint = toon.getPos(attack['battle'])
    toonPoint.setZ(toonPoint.getZ() + toon.getHeight() * 0.6)
    propTrack = Sequence(
        Func(log.reparentTo, rightHand),
        Func(log.setPosHprScale,
             -0.1, 0.6, 0.0,
             -1.152, 86.581, -76.784,
             0.01, 0.01, 0.01),
        LerpScaleInterval(log, 0.25, Point3(0.6, 1.0, 1.0)),
        Wait(2.34),
        Func(log.wrtReparentTo, attack['battle']),
        LerpPosInterval(log, 0.3, toonPoint),
        LerpScaleInterval(log, 0.05, Point3(0.01)),
        Func(MovieUtil.removeProp, log))
    impact = loader.loadSfx('phase_5/audio/sfx/SA_hardball_impact_only.ogg')
    wood = loader.loadSfx('phase_5/audio/sfx/SA_woodchipper.ogg')
    toonTrack = Sequence(
        Wait(3.66),
        Parallel(
            ActorInterval(toon, 'cringe'),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(_damage, toon, dmg, died),
            Func(_applyMarkedWoodStatus, toon)))
    track = Sequence(
        Func(_spendMeter, attack, 7),
        Parallel(
            ActorInterval(suit, 'throw-paper', partName='modelRoot'),
            propTrack,
            Sequence(Wait(2.9), SoundInterval(impact, node=suit)),
            Sequence(Wait(3.56), SoundInterval(wood, node=toon)),
            toonTrack))
    return _withCheatBanner(
        attack, track, 'MARKED WOOD!',
        'THE CHAINSAW CONSULTANT MARKS THE MOST DANGEROUS TOON FOR TERMINATION!')


def doAggrandize(attack):
    suit = attack['suit']
    targetIndex, newLevel = _parseIndexedLevelName(
        attack.get('name', ''), 'ChainsawCoreAggrandize')
    target = _supportByIndex(attack, targetIndex)
    if target is None:
        return Sequence(Func(_spendMeter, attack, 3), Wait(2.0))
    sfx = loader.loadSfx('phase_11/audio/sfx/SA_bash.ogg')
    targetTrack = Sequence(
        Wait(1.0),
        Func(_applyPromotion, target, newLevel, attack['battle'], True),
        Parallel(
            _promotionCloud(target),
            Func(_showSuitHpStringCompat, target, 'PROMOTED!', 0.85, 0.7),
            ActorInterval(target, 'slip-forward', startTime=2.43, partName='modelRoot')),
        Func(_loopSuitNeutral, target))
    track = Sequence(
        Func(_spendMeter, attack, 3),
        Parallel(
            ActorInterval(suit, 'snap-override', partName='modelRoot'),
            Sequence(Wait(0.1), SoundInterval(sfx, node=suit)),
            targetTrack))
    return _withCheatBanner(
        attack, track, 'AGGRANDIZE!',
        'THE CHAINSAW CONSULTANT PROMOTES A COG!')


def doChainLinked(attack):
    track = Sequence(
        Func(_spendMeter, attack, 2),
        Func(attack['battle'].setChainsawChainVisualActive, True),
        makeChainsawBattleCutscene(attack, 'chainlinked'))
    return _withCheatBanner(
        attack, track, 'CHAIN LINKED!',
        'THE CHAINSAW CONSULTANT BINDS THE COGS TOGETHER!')


def doScabbard(attack):
    stateTrack = Parallel()
    for index, finalHP, finalMax, overcharged in _parseScabbardStates(attack):
        support = _supportByIndex(attack, index)
        if support:
            stateTrack.append(Func(
                _applyScabbardState, support, finalHP, finalMax, overcharged))
    track = Sequence(
        Func(_spendMeter, attack, 7),
        Parallel(
            makeChainsawBattleCutscene(attack, 'scabbard'),
            Sequence(Wait(2.0), stateTrack)))
    return _withCheatBanner(
        attack, track, 'SCABBARD!',
        'THE CHAINSAW CONSULTANT RECHARGES THE COGS!')


def doSparkPlug(attack):
    statusTrack = Parallel()
    for target in attack.get('target', ()):
        toon = target.get('toon')
        if toon:
            statusTrack.append(Sequence(
                Wait(5.36),
                Func(_setToonStatusEffect,
                     toon, 'zapped', 20, 2, 'setBoth')))
    track = Sequence(
        Func(_spendMeter, attack, 2),
        Func(attack['suit'].specialHead.exitGlitch),
        Parallel(
            makeChainsawBattleCutscene(attack, 'sparkplug'),
            statusTrack,
            Sequence(
                Wait(5.36),
                Func(attack['suit'].specialHead.enterSemiGlitch))))
    return _withCheatBanner(
        attack, track, 'SPARK PLUG!',
        'THE CHAINSAW CONSULTANT SHOCKS THE HIGHEST LAFF TOON!')


def doSparkPlugDamage(attack):
    sfx = loader.loadSfx('phase_5/audio/sfx/AA_battery.ogg')
    tracks = Parallel()
    for target in attack.get('target', ()):
        toon = target.get('toon')
        dmg = target.get('hp', 0)
        died = target.get('died', 0)
        if toon:
            tracks.append(Sequence(
                Parallel(
                    ActorInterval(toon, 'slip-backward'),
                    SoundInterval(sfx, node=toon)),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(_damage, toon, dmg, died),
                Func(toon.loop, 'neutral')))
    return tracks


def doThrottle(attack):
    key = ('throttletwo' if attack.get('name') == 'ChainsawCoreThrottleTwo'
           else 'throttle')
    statusTrack = Parallel()
    for target in attack.get('target', ()):
        toon = target.get('toon')
        if toon:
            statusTrack.append(Sequence(
                Wait(4.5), Func(_applyThrottleVulnerability, toon)))
    throttleTrack = Parallel(
        makeChainsawBattleCutscene(attack, key),
        _damageTrack(attack, 4.5),
        statusTrack)
    if key == 'throttle':
        deadwoodBanner = _cheatBanner(
            attack, 'DEADWOOD!',
            "YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED",
            3.4, True)
        try:
            throttleBannerDuration = max(3.0, throttleTrack.getDuration() - deadwoodBanner.getDuration())
        except:
            throttleBannerDuration = 5.0
        throttleBanner = _cheatBanner(
            attack, 'THROTTLE!',
            'THE CHAINSAW CONSULTANT INTERRUPTS HIS OWN ATTACK!',
            throttleBannerDuration)
        return Parallel(
            throttleTrack,
            Sequence(deadwoodBanner, throttleBanner))
    return _withCheatBanner(
        attack, throttleTrack, 'THROTTLE!',
        'THE CHAINSAW CONSULTANT INTERRUPTS HIS OWN ATTACK!')


def doLayoffs(attack):
    indices = _parseTrailingIndices(
        attack.get('name', ''), 'ChainsawCoreLayoffs')
    supports = []
    for index in indices:
        support = _supportByIndex(attack, index)
        if support and support not in supports:
            supports.append(support)
    cost = min(10, 6 + len(supports))
    track = Sequence(
        Func(_spendMeter, attack, cost),
        Parallel(
            makeChainsawBattleCutscene(
                attack, 'layoffs', supportSuits=supports),
            _damageTrack(attack, 5.35)))
    return _withCheatBanner(
        attack, track, 'LAYOFFS!',
        'THE CHAINSAW CONSULTANT FIRES EVERY COG!!')


def doDeadwood(attack):
    track = Parallel(
        makeChainsawBattleCutscene(attack, 'deadwood'),
        _damageTrack(attack, 4.0))
    return _withCheatBanner(
        attack, track, 'DEADWOOD!',
        "YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED",
        oneLine=True)


def doKickback(attack):
    suffix = attack.get('name', '')[len('ChainsawCoreKickback'):]
    try:
        percent = int(suffix)
    except:
        percent = 30
    track = Parallel(
        ActorInterval(attack['suit'], 'pie-small-react', partName='modelRoot'),
        Sequence(
            Func(attack['battle'].setChainsawChainVisualActive, False),
            Func(_setSuitStatusEffect,
                 attack['suit'], 'chainsawKickback', percent, 2, 'setBoth')),
        Wait(5.75))
    return _withCheatBanner(
        attack, track, 'KICKBACK!',
        'THE CHAINSAW CONSULTANT IS VULNERABLE FOR THE NEXT FEW ROUNDS!')
