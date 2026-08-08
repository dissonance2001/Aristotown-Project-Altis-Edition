from direct.interval.IntervalGlobal import *
from panda3d.core import Point3, VBase3

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


def _cheatBanner(attack, title, description, duration):
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
            descText.getShowIntervalDesc(description, visibleDuration)),
        Func(descText.cleanup))


def _withCheatBanner(attack, track, title, description):
    try:
        duration = track.getDuration()
    except:
        duration = 5.0
    return Parallel(track, _cheatBanner(attack, title, description, duration))


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



def _applyPromotion(target, actualLevel):
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
        target.setMaxHP(int(round(target.getHP() * 1.5)))
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


def _loopSuitNeutral(suit):
    try:
        suit.loop('lured' if suit.isLured else 'neutral')
    except:
        try:
            suit.loop('neutral')
        except:
            pass


def doRevvingUp(attack, whipsaw=False):
    oldRPM = _getDisplayedRPM(attack)
    controller = _controller(attack)
    newRPM = getattr(controller, 'chainsawRPM', oldRPM) if controller else oldRPM
    try:
        gain = max(0, (int(newRPM) - int(oldRPM)) * 1000)
    except:
        gain = 0
    if whipsaw:
        phase = getattr(controller, 'chainsawPhase', 1) if controller else 1
        whipsawGain = 2000 * (2 if phase == 3 else 1)
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
    return makeChainsawBattleCutscene(attack, 'phasethree')


def doOffboarding(attack):
    indices = _parseTrailingIndices(
        attack.get('name', ''), 'ChainsawCoreOffboarding')
    support = _supportByIndex(attack, indices[0]) if indices else None
    track = Parallel(
        makeChainsawBattleCutscene(
            attack, 'offboarding', supportSuit=support),
        _damageTrack(attack, 6.0))
    return _withCheatBanner(
        attack, track, 'OFFBOARDING!',
        'THE CHAINSAW CONSULTANT FIRES A COG... LITERALLY!')


def doCutTheSlack(attack):
    suit = attack['suit']
    targetIndex, sacrificeIndices = _parseCutSlackName(
        attack.get('name', ''))
    target = _supportByIndex(attack, targetIndex)
    if target is None:
        return Sequence(Func(_syncMeter, attack), Wait(2.0))

    targetTrack = Sequence(
        Wait(2.0),
        Func(_applyPromotion, target, 30),
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
            MovieUtil.createSuitDeathTrack(support, attack['battle']))

    sfx = loader.loadSfx('phase_11/audio/sfx/SA_bash.ogg')
    track = Parallel(
        ActorInterval(suit, 'snap-override', partName='modelRoot'),
        Sequence(Wait(0.1), SoundInterval(sfx, node=suit)),
        Sequence(Wait(1.0), sacrificeTrack),
        targetTrack,
        Func(_syncMeter, attack))
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

    log = globalPropPool.getProp('treekiller_log')
    if log is None:
        return Parallel(
            ActorInterval(suit, 'throw-paper', partName='modelRoot'),
            _damageTrack(attack, 3.66))

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
            Func(_damage, toon, dmg, died)))
    track = Parallel(
        ActorInterval(suit, 'throw-paper', partName='modelRoot'),
        propTrack,
        Sequence(Wait(2.9), SoundInterval(impact, node=suit)),
        Sequence(Wait(3.56), SoundInterval(wood, node=toon)),
        toonTrack,
        Func(_syncMeter, attack))
    return _withCheatBanner(
        attack, track, 'MARKED WOOD!',
        'THE CHAINSAW CONSULTANT MARKS THE MOST DANGEROUS TOON FOR TERMINATION!')


def doAggrandize(attack):
    suit = attack['suit']
    targetIndex, newLevel = _parseIndexedLevelName(
        attack.get('name', ''), 'ChainsawCoreAggrandize')
    target = _supportByIndex(attack, targetIndex)
    if target is None:
        return Sequence(Func(_syncMeter, attack), Wait(2.0))
    sfx = loader.loadSfx('phase_11/audio/sfx/SA_bash.ogg')
    targetTrack = Sequence(
        Wait(1.0),
        Func(_applyPromotion, target, newLevel),
        Parallel(
            _promotionCloud(target),
            Func(_showSuitHpStringCompat, target, 'PROMOTED!', 0.85, 0.7),
            ActorInterval(target, 'slip-forward', startTime=2.43, partName='modelRoot')),
        Func(_loopSuitNeutral, target))
    track = Parallel(
        ActorInterval(suit, 'snap-override', partName='modelRoot'),
        Sequence(Wait(0.1), SoundInterval(sfx, node=suit)),
        targetTrack,
        Func(_syncMeter, attack))
    return _withCheatBanner(
        attack, track, 'AGGRANDIZE!',
        'THE CHAINSAW CONSULTANT PROMOTES A COG!')


def doChainLinked(attack):
    track = makeChainsawBattleCutscene(attack, 'chainlinked')
    return _withCheatBanner(
        attack, track, 'CHAIN LINKED!',
        'THE CHAINSAW CONSULTANT BINDS THE COGS TOGETHER!')


def doScabbard(attack):
    track = makeChainsawBattleCutscene(attack, 'scabbard')
    return _withCheatBanner(
        attack, track, 'SCABBARD!',
        'THE CHAINSAW CONSULTANT RECHARGES THE COGS!')


def doSparkPlug(attack):
    track = Sequence(
        Func(attack['suit'].specialHead.exitGlitch),
        Parallel(
            makeChainsawBattleCutscene(attack, 'sparkplug'),
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
    track = Parallel(
        makeChainsawBattleCutscene(attack, key),
        _damageTrack(attack, 4.5))
    return _withCheatBanner(
        attack, track, 'THROTTLE!',
        'THE CHAINSAW CONSULTANT INTERRUPTS HIS OWN ATTACK!')


def doLayoffs(attack):
    indices = _parseTrailingIndices(
        attack.get('name', ''), 'ChainsawCoreLayoffs')
    supports = []
    for index in indices:
        support = _supportByIndex(attack, index)
        if support and support not in supports:
            supports.append(support)
    track = Parallel(
        makeChainsawBattleCutscene(
            attack, 'layoffs', supportSuits=supports),
        _damageTrack(attack, 5.35))
    return _withCheatBanner(
        attack, track, 'LAYOFFS!',
        'THE CHAINSAW CONSULTANT FIRES EVERY COG!!')


def doDeadwood(attack):
    track = Parallel(
        makeChainsawBattleCutscene(attack, 'deadwood'),
        _damageTrack(attack, 4.0))
    return _withCheatBanner(
        attack, track, 'DEADWOOD!',
        "YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED YOU'RE FIRED")


def doKickback(attack):
    track = Parallel(
        ActorInterval(attack['suit'], 'pie-small-react', partName='modelRoot'),
        Wait(5.75),
        Func(_syncMeter, attack))
    return _withCheatBanner(
        attack, track, 'KICKBACK!',
        'THE CHAINSAW CONSULTANT IS VULNERABLE FOR THE NEXT FEW ROUNDS!')
