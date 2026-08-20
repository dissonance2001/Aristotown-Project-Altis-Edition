import random
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.battle import MovieUtil
from toontown.suit.SuitDNA import *
from toontown.chat.ChatGlobals import *
from toontown.battle.attacks.toons import MovieNPCSOS
from toontown.battle import MovieCamera
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleParticles
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals

notify = DirectNotifyGlobal.directNotify.newCategory('MovieZap')
hitSoundFiles = ('AA_tesla.ogg', 'AA_carpet.ogg', 'AA_zap_radio.ogg', 'AA_battery.ogg',
                 'AA_zap_tv.ogg', 'AA_zap_stagelight_hit.ogg', 'AA_tesla.ogg', 'AA_lightning.ogg')
missSoundFiles = ('AA_tesla.ogg', 'AA_carpet.ogg', 'AA_zap_radio.ogg', 'AA_battery.ogg',
                 'AA_zap_tv.ogg', 'AA_zap_stagelight_hit.ogg', 'AA_tesla.ogg', 'AA_lightning.ogg')
sprayScales = [
    0.2,   # Joybuzzer, no spray
    0.3,   # Lightbulb, no spray
    0.75,  # Radio
    0.3,   # Kart Battery, no spray
    1.0,   # TV
    1.0,   # Stagelight, no spray
    1.0,   # Tesla
    2.0    # Lightning, no spray
]
perZapTypeDelays = [
    0.4,
    2.2,
    0.0,
    0.0,
    0.0,
    2.45,
    0.0,
    0.0,
]
WaterSprayColor = Point4(1.0, 1.0, 0, 1.0)
zapPos = Point3(0, 0, 0)
zapHpr = Vec3(0, 0, 0)

def lightningPreColor():
    # This function is used to get the area's color scale immediately prior
    # to applying a lightning effect (Zap Lightning, Scope Creep, potentially more).
    # This is useful for avoiding bugs, such as when several lightning effects attempt to overlap.
    # TODO - Reset this colorscale attribute when changing zones, in case of more issues.
    if not hasattr(base, 'definedColorScale'):
        setattr(base, 'definedColorScale', render.getColorScale())
    return getattr(base, 'definedColorScale')


def lightningPostColor():
    # This resets the lightning applied in the above function.
    # Make sure to perform this at the end of a lightning sequence.
    if hasattr(base, 'definedColorScale'):
        delattr(base, 'definedColorScale')

def doZaps(zaps):
    if len(zaps) == 0:
        return (None, None)

    # ---------------------------------------------------------
    # Figure out which Zap is the LAST Zap to actually hit
    # each individual Cog.
    # ---------------------------------------------------------

    lastZapTargetBySuit = {}

    # First clear the flag and remember the most recent
    # target dictionary that actually damages each Cog.
    for zap in zaps:
        targets = zap['target']

        if type(targets) != type([]):
            targets = [targets]

        for target in targets:
            target['lastZapForSuit'] = 0

            suit = target.get('suit')
            hp = target.get('hp', 0)

            if suit is None:
                continue

            # "Last Zap that HITS this Cog"
            # Zero-damage Zap entries don't count.
            if hp <= 0:
                continue

            lastZapTargetBySuit[suit.doId] = target

    # Now mark exactly ONE target dictionary per Cog.
    for target in lastZapTargetBySuit.values():
        target['lastZapForSuit'] = 1

    suitZapsDict = {}
    doneUber = 0
    npcArrivals, npcDepartures, npcs = MovieNPCSOS.doNPCTeleports(zaps)
    skip = 0
    for zap in zaps:
        skip = 0
        if skip:
            pass
        elif type(zap['target']) == type([]):
            if 1:
                target = zap['target'][0]
                suitId = target['suit'].doId
                if suitId in suitZapsDict:
                    suitZapsDict[suitId].append(zap)
                else:
                    suitZapsDict[suitId] = [zap]
        else:
            suitId = zap['target']['suit'].doId
            if suitId in suitZapsDict:
                suitZapsDict[suitId].append(zap)
            else:
                suitZapsDict[suitId] = [zap]

    suitZaps = suitZapsDict.values()

    def compFunc(a, b):
        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1
        return 0
    suitZaps.sort(compFunc)

    delay = 0

    mtrack = Parallel()
    for st in suitZaps:
        if len(st) > 0:
            ival = __doSuitZaps(st, npcs)
            if ival:
                mtrack.append(Sequence(Wait(delay), ival))
            delay = .5
    zapTrack = Sequence(npcArrivals, mtrack, npcDepartures)
    enterDuration = npcArrivals.getDuration()
    exitDuration = npcDepartures.getDuration()
    camDuration = zapTrack.getDuration()
    camTrack = MovieCamera.chooseZapShot(zaps, camDuration, enterDuration, exitDuration)
    return (zapTrack, camTrack)


def __doSuitZaps(zaps, npcs):
    uberClone = 0
    toonTracks = Parallel()
    delay = 0.0

    if type(zaps[0]['target']) == type([]):
        mainTarget = zaps[0]['target'][0]

        if len(zaps) == 1 and mainTarget['hp'] > 0:
            fShowStun = 1
        else:
            fShowStun = 0

    elif len(zaps) == 1 and zaps[0]['target']['hp'] > 0:
        fShowStun = 1
    else:
        fShowStun = 0

    lastZapLevel = -1

    for s in zaps:
        if s['level'] > lastZapLevel:
            if lastZapLevel != -1:
                delay += perZapTypeDelays[lastZapLevel]

            lastZapLevel = s['level']

        lastZap = zaps.index(s) == len(zaps) - 1

        tracks = __doZap(
            s,
            delay,
            fShowStun,
            lastZap,
            uberClone,
            npcs
        )

        if s['level'] >= ToontownBattleGlobals.UBER_GAG_LEVEL_INDEX:
            uberClone = 1

        if tracks:
            for track in tracks:
                toonTracks.append(track)

        # IMPORTANT: accumulate the delay.
        delay += .5

    return toonTracks


def __doZap(zap, delay, fShowStun, lastZap, uberClone=0, npcs=[]):
    zapSequence = Sequence(Wait(delay))

    if type(zap['target']) == type([]):
        targets = zap['target']

        if not targets:
            return [zapSequence]

        # AI/movie target order:
        # [main, jump1, jump2, jump3]
        mainTarget = targets[0]
        chainTargets = targets[1:]
        mainLastZap = mainTarget.get(
            'lastZapForSuit',
            0
        )

        notify.debug(
            'toon: %s zaps MAIN prop: %d at suit: %d for hp: %d' % (
                zap['toon'].getName(),
                zap['level'],
                mainTarget['suit'].doId,
                mainTarget['hp']
            )
        )

        # IMPORTANT:
        # Keep this as a LIST because all of your existing
        # Zap gag functions do:
        #
        # targets = zap['target']
        # for t in targets:
        #
        mainZap = zap.copy()
        mainZap['target'] = [mainTarget]

        if uberClone:
            mainTrack = zapfn_array[zap['level']](
                mainZap,
                0,
                fShowStun,
                mainLastZap,
                uberClone,
                npcs=npcs
            )
        else:
            mainTrack = zapfn_array[zap['level']](
                mainZap,
                0,
                fShowStun,
                mainLastZap,
                npcs=npcs
            )

        combinedTrack = Parallel()

        if mainTrack:
            combinedTrack.append(mainTrack)

        # The other Cogs are chained Zap hits only.
        for chainIndex in xrange(len(chainTargets)):
            target = chainTargets[chainIndex]

            if chainIndex == 0:
                previousTarget = mainTarget
            else:
                previousTarget = chainTargets[chainIndex - 1]

            adjacentLastZap = target.get(
                'lastZapForSuit',
                0
            )

            combinedTrack.append(
                __doAdjacentZap(
                    target,
                    previousTarget,
                    zap,
                    chainIndex + 1,
                    adjacentLastZap
                )
            )

        zapSequence.append(combinedTrack)

    else:
        # Legacy/single target fallback.
        notify.debug(
            'toon: %s zaps prop: %d at suit: %d for hp: %d' % (
                zap['toon'].getName(),
                zap['level'],
                zap['target']['suit'].doId,
                zap['target']['hp']
            )
        )

        singleZap = zap.copy()
        singleZap['target'] = [zap['target']]

        if uberClone:
            mainTrack = zapfn_array[zap['level']](
                mainZap,
                0,
                fShowStun,
                lastZap,
                uberClone,
                npcs=npcs
            )
        else:
            mainTrack = zapfn_array[zap['level']](
                mainZap,
                0,
                fShowStun,
                lastZap,
                npcs=npcs
            )

        if ival:
            zapSequence.append(ival)

    return [zapSequence]

def __getZapContactTime(zap):
    level = zap['level']
    toon = zap['toon']

    if level == 0:
        # Joybuzzer
        return 2.2, 'small-zap'

    elif level == 1:
        # Rug
        return 5.3, 'small-zap'

    elif level == 2:
        # Balloon / Radio in your modified setup
        return 3.1, 'small-zap'

    elif level == 3:
        # Battery
        return (51.0 / toon.getFrameRate('throw')) + 0.8, 'small-zap'

    elif level == 4:
        # TV - tune from its function
        return 2.6, 'large-zap'

    elif level == 5:
        # Stagelight/Tazer
        return 2.5 + 2.20 + .15, 'large-zap'

    elif level == 6:
        # Tesla
        return 2.9, 'large-zap'

    elif level == 7:
        # Lightning
        return 4.1, 'large-zap'

    return 0.0

def __doAdjacentZap(target, previousTarget, zap, chainIndex, lastZap):
    suit = target['suit']
    hp = target['hp']
    died = target['died']
    revived = target['revived']

    battle = zap['battle']
    toon = zap['toon']
    level = zap['level']

    track = Sequence()
    deathTracks = Sequence(Wait(0.8))
    headTrack = Sequence()

    for headPart in suit.animatedHeadParts:
        headTrack.append(Func(headPart.pose, 'stun', 5))
    headTrack.append(Wait(1.0))
    headTrack.append(Func(suit.setNeutralAnimationHead))

    if hp <= 0:
        return track

    # We'll make this gag-specific below.
    tContact, anim = __getZapContactTime(zap)

    # Small delay between electrical jumps.
    # chainIndex 1 = first jump, etc.
    jumpDelay = 0.12 * chainIndex

   # suit.addPendingQueuedDamage(hp)

    track.append(
        Wait(tContact)
    )

    impactTrack = Parallel()
    updateHealthBar = Func(suit.updateHealthBar, hp)
    if toon.getTrackBonusLevel(ZAP_TRACK) > 1:
        showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="AFTERSHOCK!", colorCode=3), Func(suit.setSuitStatusEffect, 'zapped', modifier=int(math.ceil(hp / 2)), turns=2, mode='refreshModifier'))
    else:
        showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="AFTERSHOCK!", colorCode=3), Func(suit.setSuitStatusEffect, 'zapped', modifier=int(math.ceil(hp / 4)), turns=2, mode='refreshModifier'))

    # Damage already calculated by BattleCalculatorAI.
    impactTrack.append(showDamage)
    impactTrack.append(updateHealthBar)
    if suit.getSuitStatusModifier('rushJob') == 5:
        impactTrack.append(Func(suit.clearSuitStatusEffect, 'rushJob'))
    if suit.hasSuitStatusEffect('sued'):
        impactTrack.append(Func(suit.setSuitStatusEffect, 'sued', modifier=1, turns=4))

    # Zap reaction.
    if lastZap:
        impactTrack.append(Parallel(headTrack, MovieUtil.zapCog(suit, anim, .5, 2.0, battle, died, level), MovieUtil.createSuitStunIntervalZap(suit, .5, 2.0), deathTracks))
    else:
        impactTrack.append(Parallel(headTrack, MovieUtil.zapCogNeutral(suit, anim, .5, 2.0, battle)))

    track.append(impactTrack)

    if revived:
        if suit.dna.name == 'redd':
            track.append(
                MovieUtil.createSuitReviveRedd(
                    suit,
                    battle
                )
            )

        elif suit.isSkeleton:
            track.append(
                MovieUtil.createSuitReviveTrackVirtual(
                    suit,
                    battle
                )
            )

        else:
            track.append(
                MovieUtil.createSuitReviveTrack(
                    suit,
                    battle
                )
            )

    elif died:
        if suit.isVirtual:
            track.append(
                Func(
                    suit.clearSuitStatusEffect,
                    'zapped'
                )
            )

            track.append(
                MovieUtil.createVirtualSuitDeathTrack(
                    suit,
                    battle
                )
            )

        elif level > 3 and suit.dna.name != 'chainsaw':
            deathTracks.append(
                Func(
                    suit.clearSuitStatusEffect,
                    'zapped'
                )
            )

            deathTracks.append(
                MovieUtil.shortCircuitTrack(
                    suit,
                    battle
                )
            )

        else:
            track.append(
                Func(
                    suit.clearSuitStatusEffect,
                    'zapped'
                )
            )

            if suit.dna.name == 'chainsaw':
                track.append(Func(MovieUtil.stopZapCogNeutral, suit))
            track.append(
                MovieUtil.createSuitDeathTrack(
                    suit,
                    battle
                )
            )

    else:
        if lastZap:
            track.append(Func(MovieUtil.stopZapCogNeutral, suit))
            track.append(
                Func(
                    suit.setNeutralAnimationTrap
                )
        )

    return track


def __suitTargetPoint(suit):
    pnt = suit.getPos(render)
    pnt.setZ(pnt[2] + suit.getHeight() * 0.66)
    return Point3(pnt)
	
def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr))
    moveTrack = LerpPosInterval(suit, 0, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)
	
def createSuitResetPosTrack(suit, battle):
    return __createSuitResetPosTrack(suit, battle)

def __soakRemoval(suit, remove=0):
    if remove:
        if suit.style.name == 'hydra':
            color = Point4((0.729, 0.729, 0.729, 1))
        elif suit.style.name == 'charon':
            color = Point4((0.51, 0.49, 0.467, 1))
        elif suit.style.name == 'nix':
            color = Point4((0.6, 0.6, 0.6, 1))
        elif suit.style.name == 'styx':
            color = Point4((0.671, 0.671, 0.671, 1))
        elif suit.style.name == 'kerberos':
            color = Point4((0.62, 0.659, 0.624, 1))
        else:
            color = Point4(1.0, 1.0, 1.0, 1.0)
    else:
        color = SoakColor
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit]
    suitInterval = Sequence()
    if suit.style.name == 'lgator' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryLitigator))
    if suit.style.name == 'safesupervis' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryFirestarter))
    if suit.style.name == 'fires' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryFirestarter))
    for bodyPart in suitBody:
        if bodyPart:
            suitInterval.append(Func(bodyPart.setColor, color))
        return suitInterval

def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr))
    moveTrack = LerpPosInterval(suit, 0, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def createSuitResetPosTrack(suit, battle):
    return __createSuitResetPosTrack(suit, battle)

def __getSuitTrack(zap, suit, tContact, tDodge, hp, hpbonus, kbbonus, anim, died, leftSuits, rightSuits, battle, toon, fShowStun, lastZap = 0, beforeStun = 0.5, afterStun = 2.0, uberRepeat = 0, revived = 0, npcs = [], dodge=False):
    if hp > 0:
        level = zap['level']
        suitTrack = Sequence()
        zapTracks = Parallel()
        deathTracks = Sequence(Wait(0.8))
        headTrack = Sequence()

        for headPart in suit.animatedHeadParts:
            headTrack.append(Func(headPart.pose, 'stun', 5))

        headTrack.append(Wait(1.0))
        headTrack.append(Func(suit.setNeutralAnimationHead))
        scapeGoatTrack = Sequence()
        sival = ActorInterval(suit, anim)
        sival = []
        suitIndex = battle.activeSuits.index(suit)
        #if toon.getTrackBonusLevel(ZAP_TRACK) > 1:
           # zapTracks.append(__zapNearby(suit, anim, suitIndex + 1, battle.activeSuits, tContact, hp, battle))
           # zapTracks.append(__zapNearby2(suit, anim, suitIndex + 2, battle.activeSuits, tContact, hp, battle))
            #zapTracks.append(__zapNearby(suit, anim, suitIndex - 1, battle.activeSuits, tContact, hp, battle))
            #zapTracks.append(__zapNearby2(suit, anim, suitIndex - 2, battle.activeSuits, tContact, hp, battle))
       # else:
           # zapTracks.append(__zapNearby2(suit, anim, suitIndex + 1, battle.activeSuits, tContact, hp, battle))
           # zapTracks.append(__zapNearby3(suit, anim, suitIndex + 2, battle.activeSuits, tContact, hp, battle))
           # zapTracks.append(__zapNearby2(suit, anim, suitIndex - 1, battle.activeSuits, tContact, hp, battle))
            #zapTracks.append(__zapNearby3(suit, anim, suitIndex - 2, battle.activeSuits, tContact, hp, battle))
        if toon.getTrackBonusLevel(ZAP_TRACK) > 1:
            showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="AFTERSHOCK!", colorCode=3), Func(suit.setSuitStatusEffect, 'zapped', modifier=int(math.ceil(hp / 2)), turns=2, mode='refreshModifier'))
        else:
            showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="AFTERSHOCK!", colorCode=3), Func(suit.setSuitStatusEffect, 'zapped', modifier=int(math.ceil(hp / 4)), turns=2, mode='refreshModifier'))
        updateHealthBar = Func(suit.updateHealthBar, hp)
        totalDamage = hp

        # add to queued damage BEFORE building interval
       # suit.addPendingQueuedDamage(totalDamage)
        soakRemoval = Func(suit.makeZapped)
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        if suit.getSuitStatusModifier('rushJob') == 5:
            suitTrack.append(Func(suit.clearSuitStatusEffect, 'rushJob'))
        suitTrack.append(updateHealthBar)
        resetPos, resetHpr = battle.getActorPosHpr(suit)
        zapTrack = Sequence(ActorInterval(suit, anim, startTime=0, endTime=0.8))
        if lastZap:
            suitTrack.append(Parallel(headTrack, MovieUtil.zapCog(suit, anim, .5, 2.0, battle, died, level), MovieUtil.createSuitStunIntervalZap(suit, .5, 2.0), deathTracks))
        else:
            suitTrack.append(Parallel(headTrack, MovieUtil.zapCogNeutral(suit, anim, .5, 2.0, battle)))
        bonusTrack = Sequence(Wait(tContact))
        if kbbonus == 0:
            #suitTrack.append(__createSuitResetPosTrack(suit, battle))
            suitTrack.append(Func(battle.unlureSuit, suit))
            suitTrack.append(__createSuitResetPosTrack(suit, battle))
        if hpbonus > 0:
            bonusTrack.append(Wait(0.75))
            bonusTrack.append(Func(suit.showHpText, -hpbonus, 1, openEnded=0, attackTrack=ZAP_TRACK))
            bonusTrack.append(updateHealthBar)
        if suit.dna.name == 'redd' and revived != 0:
            suitTrack.append(MovieUtil.createSuitReviveRedd(suit, battle))
        elif died != 0 and suit.isVirtual:
            suitTrack.append(Func(suit.clearSuitStatusEffect, 'zapped'))
            suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        elif died != 0 and not suit.isVirtual and level > 3 and suit.dna.name != 'chainsaw':
            deathTracks.append(Func(suit.clearSuitStatusEffect, 'zapped'))
            deathTracks.append(MovieUtil.shortCircuitTrack(suit, battle))
        elif died != 0 and not suit.isVirtual:
            suitTrack.append(Func(suit.clearSuitStatusEffect, 'zapped'))
            if suit.dna.name == 'chainsaw':
                suitTrack.append(Func(MovieUtil.stopZapCogNeutral, suit))
            suitTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
        elif revived != 0 and suit.isSkeleton:
            suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
        elif revived != 0 and not suit.isSkeleton and suit.dna.name != 'redd':
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
        else:
            #suitTrack.append(__createSuitResetPosTrack(suit, battle))
            suitTrack.append(Func(battle.unlureSuit, suit))
            #suitTrack.append(__soakRemoval(suit))
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTrack.append(Func(suit.setDizzy, 0))
        suitTrack.append(Func(suit.makeFreshlyZapped))
       # suitTrack.append(createSuitResetPosTrack(suit, battle))
        if lastZap:
            suitTrack.append(Func(MovieUtil.stopZapCogNeutral, suit))
            suitTrack.append(Func(suit.setNeutralAnimationTrap))
        #suitTrack.append(Parallel(__soakRemoval(suit, 1)))
        #suitTrack.append(soakRemoval)
        #suitTrack.append(Func(suit.setNeutralAnimation))
        if suit.hasSuitStatusEffect('sued'):
            suitTrack.append(Func(suit.setSuitStatusEffect, 'sued', modifier=1, turns=4))
        return Parallel(suitTrack, bonusTrack, zapTracks)
    elif dodge:
        return Parallel()
    else:
        return Parallel()
		
def shortCircuitTrack(suit, battle):
    if suit.isHidden():
        return Sequence()
    else:
        suitTrack = Sequence()
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        suitTrack.append(Wait(0.15))
        suitTrack.append(Func(MovieUtil.avatarHide, suit))
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        deathSoundTrack = Sequence(Wait(0.5), SoundInterval(deathSound, volume=0.8))
        BattleParticles.loadParticles()
        smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
        singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
        smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
        bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
        gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
        smallGears.setPos(gearPoint)
        singleGear.setPos(gearPoint)
        smallGears.setDepthWrite(False)
        singleGear.setDepthWrite(False)
        smallGearExplosion.setPos(gearPoint)
        bigGearExplosion.setPos(gearPoint)
        smallGearExplosion.setDepthWrite(False)
        bigGearExplosion.setDepthWrite(False)
        explosionTrack = Sequence()
        explosionTrack.append(MovieUtil.createKapowExplosionTrack(battle, explosionPoint=gearPoint))
        gears1Track = Sequence(Wait(0.5), ParticleInterval(smallGears, battle, worldRelative=0, duration=1.0, cleanup=True), name='gears1Track')
        gears2MTrack = Track(
            (0.1, ParticleInterval(singleGear, battle, worldRelative=0, duration=0.4, cleanup=True)),
            (0.5, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=0.5, cleanup=True)),
            (0.9, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=2.0, cleanup=True)), name='gears2MTrack'
        )

        return Parallel(suitTrack, explosionTrack, deathSoundTrack, gears1Track, gears2MTrack)


def say(statement):
    print statement


def __ScapegoatAbsorb(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding:
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].addAbsorbDamage, suits[suitIndex], int(hp * 0.45)))
        suitTrack.append(showDamage)
        return suitTrack
    else:
        return Sequence()

def __ScapegoatAbsorb1(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding and not suits[suitIndex].dna.name == 'hroller':
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.425), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(hp * 0.425))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'), MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        return suitTrack
    elif len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding and suits[suitIndex].dna.name == 'nothing':
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.115), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(hp * 0.115))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'),
                                  MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        return suitTrack
    else:
        return Sequence()

def __ScapegoatAbsorb2(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding and not suits[suitIndex].dna.name == 'hroller':
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(
            Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.425), openEnded=0, attackTrack=SQUIRT_TRACK),
            Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(hp * 0.425))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'), MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        return suitTrack
    elif len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding and suits[suitIndex].dna.name == 'nothing':
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextAbsorb, -int(hp * 0.115), openEnded=0, attackTrack=SQUIRT_TRACK), Func(suits[suitIndex].showHpString, "ABSORBED!", openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(hp * 0.115))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(ActorInterval(suits[suitIndex], 'pie-small-react'),
                                  MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0)))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        return suitTrack
    else:
        return Sequence()

def __zapNearby(suit, anim, suitIndex, suits, tContact, hp, battle):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal and not (suits[suitIndex].dna.name == 'hrollers' and suits[suitIndex].currHP > 7200 and not suits[suitIndex].currHP > 8000):
        revives = suits[suitIndex].getSkeleRevives()
        soakRemoval = Func(suits[suitIndex].makeUnSoaked)
        suitTrack = Sequence()
        showDamage = Func(suits[suitIndex].showHpText, - int(hp * 0.84))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(value * 0.84))
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        deathTracks = Sequence(Wait(1.6))
        suitTrack.append(Parallel(MovieUtil.zapCog(suits[suitIndex], anim,.5, 2.0, battle), MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0), deathTracks))
        if suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1 and not suits[suitIndex].isRevive:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif not suits[suitIndex].isVirtual:
            deathTracks.append(Func(suits[suitIndex].checkCogHPZap, battle))
        suitTrack.append(Parallel(__soakRemoval(suits[suitIndex], 1)))
        suitTrack.append(__createSuitResetPosTrack(suits[suitIndex], battle))
        suitTrack.append(Func(battle.unlureSuit, suits[suitIndex]))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimationTrap))
        suitTrack.append(soakRemoval)
        suitTrack.append(__ScapegoatAbsorb1(suitIndex - 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex + 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex - 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex + 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex - 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex + 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex - 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex + 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex - 5, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb1(suitIndex + 5, battle.activeSuits, hp, battle))
        return suitTrack
    else:
        return Sequence()

def __zapNearby2(suit, anim, suitIndex, suits, tContact, hp, battle):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal and not (suits[suitIndex].dna.name == 'hrollers' and suits[suitIndex].currHP > 7200 and not suits[suitIndex].currHP > 8000):
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        soakRemoval = Func(suits[suitIndex].makeUnSoaked)
        showDamage = Func(suits[suitIndex].showHpText, - int(hp * 0.67))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(value * 0.67))
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        deathTracks = Sequence(Wait(1.6))
        suitTrack.append(Parallel(MovieUtil.zapCog(suits[suitIndex], anim, .5, 2.0, battle),
                                  MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0), deathTracks))
        if suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1 and not suits[suitIndex].isRevive:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif not suits[suitIndex].isVirtual:
            deathTracks.append(Func(suits[suitIndex].checkCogHPZap, battle))
        suitTrack.append(Parallel(__soakRemoval(suits[suitIndex], 1)))
        suitTrack.append(__createSuitResetPosTrack(suits[suitIndex], battle))
        suitTrack.append(Func(battle.unlureSuit, suits[suitIndex]))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimationTrap))
        suitTrack.append(soakRemoval)
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 5, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 5, battle.activeSuits, hp, battle))
        return suitTrack
    else:
        return Sequence()

def __zapNearby3(suit, anim, suitIndex, suits, tContact, hp, battle):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal and not (suits[suitIndex].dna.name == 'hrollers' and suits[suitIndex].currHP > 7200 and not suits[suitIndex].currHP > 8000):
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        soakRemoval = Func(suits[suitIndex].makeUnSoaked)
        showDamage = Func(suits[suitIndex].showHpText, - int(hp * 0.35))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(value * 0.35))
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        deathTracks = Sequence(Wait(1.6))
        suitTrack.append(Parallel(MovieUtil.zapCog(suits[suitIndex], anim, .5, 2.0, battle),
                                  MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0), deathTracks))
        if suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1 and not suits[suitIndex].isRevive:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif not suits[suitIndex].isVirtual:
            deathTracks.append(Func(suits[suitIndex].checkCogHPZap, battle))
        suitTrack.append(Parallel(__soakRemoval(suits[suitIndex], 1)))
        suitTrack.append(__createSuitResetPosTrack(suits[suitIndex], battle))
        suitTrack.append(Func(battle.unlureSuit, suits[suitIndex]))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimationTrap))
        suitTrack.append(soakRemoval)
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 5, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 5, battle.activeSuits, hp, battle))
        return suitTrack
    else:
        return Sequence()

def __zapNearby4(suit, anim, suitIndex, suits, tContact, hp, battle):
    if len(suits) > suitIndex >= 0 and not suits[suitIndex].isImmortal and not (suits[suitIndex].dna.name == 'hrollers' and suits[suitIndex].currHP > 7200 and not suits[suitIndex].currHP > 8000):
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        soakRemoval = Func(suits[suitIndex].makeUnSoaked)
        showDamage = Func(suits[suitIndex].showHpText, - int(hp * 0.45))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, int(value * 0.45))
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        deathTracks = Sequence(Wait(1.6))
        suitTrack.append(Parallel(MovieUtil.zapCog(suits[suitIndex], anim, .5, 2.0, battle),
                                  MovieUtil.createSuitStunInterval(suits[suitIndex], .5, 2.0), deathTracks))
        if suits[suitIndex].isVirtual:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaser, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 2:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif suits[suitIndex].isSkeleton and revives >= 1 and not suits[suitIndex].isRevive:
            suitTrack.append(Func(suits[suitIndex].checkCogHPLaserRevive, battle))
        elif not suits[suitIndex].isSkeleton and revives >= 1:
            suitTrack.append(Func(suits[suitIndex].checkCogHPRevive, battle))
        elif not suits[suitIndex].isVirtual:
            deathTracks.append(Func(suits[suitIndex].checkCogHPZap, battle))
        suitTrack.append(Parallel(__soakRemoval(suits[suitIndex], 1)))
        suitTrack.append(__createSuitResetPosTrack(suits[suitIndex], battle))
        suitTrack.append(Func(battle.unlureSuit, suits[suitIndex]))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimationTrap))
        suitTrack.append(soakRemoval)
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 1, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 2, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 3, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 4, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex - 5, battle.activeSuits, hp, battle))
        suitTrack.append(__ScapegoatAbsorb2(suitIndex + 5, battle.activeSuits, hp, battle))
        return suitTrack
    else:
        return Sequence()


def __getSoundTrack(level, delay, node = None):
    soundEffect = globalBattleSoundCache.getSound(missSoundFiles[level])
    soundTrack = Sequence()
    if soundEffect:
        if level == 0:
            pass
        else:
            soundTrack.append(Wait(delay))
        soundTrack.append(SoundInterval(soundEffect, node=node))
        return soundTrack


def __doJoybuzzer(zap, delay, fShowStun, lastZap, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    scale = sprayScales[level]
    tTotalFlowerToonAnimationTime = 2
    tFlowerFirstAppears = 1.0
    dFlowerScaleTime = 0.5
    tSprayStarts = tTotalFlowerToonAnimationTime
    dSprayScale = 0.2
    dSprayHold = 0.1
    tContact = tSprayStarts + dSprayScale
    tSuitDodges = tTotalFlowerToonAnimationTime
    tracks = Parallel()
    button = globalPropPool.getProp('joybuzz')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getRightHands()
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands, Vec3((0.3, 0, 0)), Vec3((-10, -60 ,0))), ActorInterval(toon, 'water-gun'), Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    tracks.append(__getSoundTrack(level, tTotalFlowerToonAnimationTime, toon))
    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']
        hitSuit = hp > 0
        suitPos = suit.getPos(battle)
        targetPoint = lambda suit=suit: __suitTargetPoint(suit)

        def getSprayStartPos(toon = toon):
            toon.update(0)
            p = button2.getPos(toon)
            return p

        sprayTrack = MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
        if hp > 0 or delay <= 0:
            tracks.append(sprayTrack)
            tracks.append(__getSuitTrack(zap, suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits, battle, toon, fShowStun, lastZap, revived=revived))
    return tracks


def __doRug(zap, delay, fShowStun, lastZap, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    scale = sprayScales[level]
    tSpray = 5.2
    sprayPoseFrame = 88
    dSprayScale = 0.1
    dSprayHold = 0.1
    tContact = tSpray + dSprayScale
    tSuitDodges = max(tSpray - 0.5, 0.0)
    tracks = Parallel()
    tracks.append(ActorInterval(toon, 'run'))
    soundTrack = __getSoundTrack(level, 0, toon)
    tracks.append(soundTrack)
    rug = globalPropPool.getProp('zapRug')
    rugPos = Point3(0, 0, 0.025)
    rugHpr = Point3(0, 0, 0)
    glassTrack = Sequence(Func(MovieUtil.showProp, rug, toon, rugPos, rugHpr), ActorInterval(toon, 'walk', playRate=0.7), ActorInterval(toon, 'run'), ActorInterval(toon, 'run', playRate=1.1),  ActorInterval(toon, 'run', playRate=1.2),  ActorInterval(toon, 'run', playRate=1.3),  ActorInterval(toon, 'run', playRate=1.4), ActorInterval(toon, 'water', playRate=1, startFrame=0, endFrame=36), Wait(1), Func(MovieUtil.removeProp, rug), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(glassTrack)
    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']
        hitSuit = hp > 0
        suitPos = suit.getPos(battle)
        targetPoint = lambda suit = suit: __suitTargetPoint(suit)

        def getSprayStartPos(toon = toon):
            toon.update(0)
            lod0 = toon.getLOD(toon.getLODNames()[0])
            if base.config.GetBool('want-new-anims', 1):
                if not lod0.find('**/def_joint_right_hold').isEmpty():
                    joint = lod0.find('**/def_joint_right_hold')
                else:
                    joint = lod0.find('**/joint_Rhold')
            else:
                joint = lod0.find('**/joint_Rhold')
            p = joint.getPos(render)
            return p
        if hp > 0:
            sprayTrack = MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
            tracks.append(Sequence(Wait(tSpray), sprayTrack))
        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(zap, suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits, battle, toon, fShowStun, lastZap, revived=revived))
    return tracks


def __doBalloon(zap, delay, fShowStun, lastZap, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    scale = sprayScales[level]
    tPistol = 0.0
    dPistolScale = 3
    dPistolHold = 1.8
    tSpray = 3
    sprayPoseFrame = 63
    dSprayScale = 0.1
    dSprayHold = 0.3
    tContact = tSpray + dSprayScale
    tSuitDodges = 1.1
    tracks = Parallel()
    toonTrack = Sequence(Func(toon.pingpong, 'smooch', fromFrame=40, toFrame=45), Wait(2.5), Func(toon.stop), Func(toon.pingpong, 'cast', fromFrame=30, toFrame=40), Wait(2), Func(toon.stop), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, 0.2, toon)
    tracks.append(soundTrack)
    pistol = globalPropPool.getProp('balloon')
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    pistolTracks = Parallel()
    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']
        hitSuit = hp > 0
        suitPos = suit.getPos(battle)
        targetPoint = lambda suit=suit: __suitTargetPoint(suit)

        def getSprayStartPos(pistol=pistol, toon=toon):
            toon.update(0)
            p = pistol.getPos(render)
            return p

        sprayTrack = Sequence()
        sprayTrack.append(Wait(3.0))
        sprayTrack.append(
            MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold,
                                  dSprayScale,
                                  horizScale=scale, vertScale=scale))

        sprayTrack = MovieUtil.getSprayTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale, horizScale=scale, vertScale=scale)
        pistolPos = Point3(0.28, 0.1, 0.08)
        pistolHpr = VBase3(85.6, -4.44, 94.43)
        pistolTrack = Sequence(Func(MovieUtil.showProp, pistol, hand_jointpath0, pistolPos, pistolHpr), LerpScaleInterval(pistol, dPistolScale, dPistolScale, startScale=MovieUtil.PNT3_NEARZERO), Wait(tSpray - dPistolScale))
        pistolTrack.append(sprayTrack)
        pistolTrack.append(Wait(dPistolHold))
        pistolTrack.append(LerpScaleInterval(pistol, 0.4, MovieUtil.PNT3_NEARZERO, dPistolScale))
        pistolTrack.append(Func(hand_jointpath1.removeNode))
        pistolTrack.append(Func(hand_jointpath0.removeNode))
        pistolTrack.append(Func(MovieUtil.removeProp, pistol))
        if hp > 0:
            tracks.append(pistolTrack)
        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(zap, suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits, battle, toon, fShowStun, lastZap, revived=revived))
    return tracks

def __suitLightTargetPoint(suit, other=render, extraPos=None):
    foo = suit.attachNewNode('foo')
    foo.setZ(suit.getHeight() * 0.6)
    if suit.isSkeleton:
        offsets = {
            'a': 0.5,
            'b': 0.5,
            'c': 0.25,
        }
    else:
        offsets = {
            'a': 1.275,
            'b': 1.3,
            'c': 1.65
        }
    offset = offsets[suit.style.body] * suit.scale

    basePart = suit.find('**/joint_attachMeter')
    foo.setY(basePart.getY() + offset)
    foo.setX(basePart.getX())
    if extraPos:
        foo.setPos(foo.getPos() + Point3(extraPos))
    newPos = foo.getPos(other)
    foo.removeNode()
    return Point3(newPos)


def __doBattery(zap, delay, fShowStun, lastZap, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    origPos = toon.getPos(battle)
    runBackHpr = Vec3(0, 0, 0)
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    tSpray = 51.0 / toon.getFrameRate('throw')
    dSprayScale = 0.7
    tContact = tSpray + dSprayScale + 0.1
    scale = 0.3
    tAppearDelay = 0.7
    dHoseHold = 0.7
    midPos = Point3(toon.getX(battle)*.5, 0, 0)
    runDur = 1
    tSprayDelay = 2.6
    dSprayScale = 0.1
    dSprayHold = 1.8
    tSuitDodges = 2.1
    tracks = Parallel()
    throwSound = globalBattleSoundCache.getSound('AA_pie_throw_only.ogg')
    soundTrack = Parallel(
        Sequence(
            Wait(2.6),
            SoundInterval(throwSound, node=toon)
        ),
    )
    soundTrack.append(__getSoundTrack(level, tSprayDelay, toon))
    tracks.append(soundTrack)

    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']
        battery = globalPropPool.getProp('battery')
        hitSuit = hp > 0
        suitPos = suit.getPos(battle)
        dBalloonScale = 0.825
        suitPoint = lambda suit=suit: __suitLightTargetPoint(suit, other=battle)
        toonTrack = Sequence(ActorInterval(toon, 'throw'),
                                Func(toon.loop, 'neutral'))
        tracks.append(toonTrack)
        def reparentBattery(suit=suit):
            if suit.isSkeleton:
                battery.wrtReparentTo(suit.find('**/joint_attachMeter'))
            else:
                battery.wrtReparentTo(suit.find('**/joint_attachMeter'))
            if suit.style.body == 'c' and not suit.isSkeleton:
                battery.setR(100)
            battery.setPos(suit, __suitLightTargetPoint(suit, other=suit))
            battery.setColorScaleOff(1)

        balloonFly = Sequence(
                Func(battery.wrtReparentTo, render),
                Parallel(
                    LerpPosInterval(battery, 0.3, pos=suitPoint, other=battle),
                    LerpHprInterval(battery, 0.2, (-90, 0, 90), other=suit)
                ),
            )
        balloonFly.append(Func(reparentBattery))
        balloonHide = Func(MovieUtil.removeProp, battery)
        balloonTrack = Sequence(
            Func(MovieUtil.showProp, battery, hand_jointpath0, scale=0.7),
            LerpScaleInterval(battery, 0.5, dBalloonScale, startScale=MovieUtil.PNT3_NEARZERO),
            Wait(tSpray)
        )
        balloonTrack.append(balloonFly)

        if hp > 0:
            BattleParticles.loadParticles()
            particleEffect = BattleParticles.loadParticleFile('batteryGagZap.ptf')
            partTrack = getPartTrack(particleEffect, tContact, 1.7, [particleEffect, battery, 0],
                                        softStop=-0.41, renderParent=render)
            tracks.append(partTrack)

            def updateBatteryX(value, mult=1.0):
                battery.setZ(value*mult)

            totalTime = 1.3
            moveTime = 0.05
            moveAmt = 0.3
            for _ in range(int(totalTime / moveTime)):
                balloonTrack.append(LerpFunctionInterval(updateBatteryX, duration=moveTime / 4, fromData=0, toData=moveAmt))
                balloonTrack.append(LerpFunctionInterval(updateBatteryX, duration=moveTime / 4, fromData=moveAmt, toData=0))
                balloonTrack.append(LerpFunctionInterval(updateBatteryX, duration=moveTime / 4, fromData=0, toData=moveAmt, extraArgs=[-1]))
                balloonTrack.append(LerpFunctionInterval(updateBatteryX, duration=moveTime / 4, fromData=moveAmt, toData=0, extraArgs=[-1]))

            fallPoint = (0.0, 3.0, 0.5)

            fallSeq = Sequence()
            fallSeq.append(Func(battery.wrtReparentTo, render))
            fallSeq.append(Parallel(
                        LerpHprInterval(battery, 0.3, (-90, 0, 50), blendType='easeOut', other=suit),
                        LerpPosInterval(battery, 0.8, fallPoint, blendType='easeIn', other=suit),
                        Sequence(
                            Wait(0.6),
                            LerpScaleInterval(battery, 0.2, MovieUtil.PNT3_NEARZERO, blendType='easeInOut')
                        )
                    ))

            balloonTrack.append(fallSeq)

            balloonTrack.append(Func(hand_jointpath0.removeNode))
            balloonTrack.append(balloonHide)
            tracks.append(balloonTrack)
        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(zap, suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits, battle, toon,
                fShowStun, lastZap, revived=revived))
    
    return tracks


def __doTazer(zap, delay, fShowStun, lastZap, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    origPos = toon.getPos(battle)

    tazer = globalPropPool.getProp('tazer')
    tazer.setHpr(180, 0, 0)
    dSprayScale = 0.1
    dSprayHold = 1.8
    runBackHpr = Vec3(0, 0, 0)
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    BattleParticles.loadParticles()
    tAppearDelay = 0.7
    runDur = 1
    tSprayDelay = 2
    dBeamHold = 1.8
    tContact = 2
    tSuitDodges = 2.1

    tracks = Parallel()

    toonTrack = Sequence(
        Wait(tAppearDelay),
        Func(MovieUtil.showProp, tazer, hand_jointpath0),
        Func(toon.pingpong, 'cast', fromFrame=30, toFrame=40),
        Wait(3),
        Func(toon.loop, 'neutral'),
        Func(MovieUtil.removeProp, tazer),
        Func(hand_jointpath1.removeNode),
        Func(hand_jointpath0.removeNode),
        Func(toon.setHpr, battle, origHpr)
    )

    moveTrack = Sequence(
        Wait(tAppearDelay),
        LerpPosInterval(toon, runDur, Point3(toon.getX(battle) * .5, 0, 0), other=battle),
        Wait(3),
        LerpPosInterval(toon, runDur, origPos, other=battle)
    )

    tracks.append(toonTrack)
    tracks.append(__getSoundTrack(level, tSprayDelay, toon))

    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        scale = sprayScales[level]
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']
        targetPoint = lambda suit = suit: __suitTargetPoint(suit)
        def getBeamStartPos(toon=toon):
            toon.update(0)
            lod0 = toon.getLOD(toon.getLODNames()[0])
            if base.config.GetBool('want-new-anims', 1):
                if not lod0.find('**/def_joint_right_hold').isEmpty():
                    joint = lod0.find('**/def_joint_right_hold')
                else:
                    joint = lod0.find('**/joint_Rhold')
            else:
                joint = lod0.find('**/joint_Rhold')
            return joint.getPos(render)

        if hp > 0:
            particleEffect = BattleParticles.loadParticleFile('teslaGagZap.ptf')
            partTrack = getPartTrack(particleEffect, tSprayDelay - 0.2, 1.8, [particleEffect, tazer, 0],
                                        softStop=-0.41, renderParent=render)
            tracks.append(partTrack)

            sprayTrack = Sequence()
            sprayTrack.append(Wait(tSprayDelay))
            sprayTrack.append(MovieUtil.getZapTrack(battle, WaterSprayColor, getBeamStartPos, targetPoint,
                                                    dSprayScale, dSprayHold, dSprayScale, horizScale=scale,
                                                    vertScale=scale))

            tracks.append(sprayTrack)

        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(zap, 
                suit, tContact, tSuitDodges, hp, hpbonus, kbbonus,
                'shock', died, leftSuits, rightSuits, battle,
                toon, fShowStun, lastZap, revived=revived
            ))

    return tracks


def __doBrokenTV(zap, delay, fShowStun, lastZap, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 3)
    tSprayDelay = 1.8
    dSprayScale = 0.05
    dSprayHold = 1.6
    tContact = 1.9
    tSuitDodges = 1.7
    scale = sprayScales[level]

    tv = globalPropPool.getProp('tv')
    tv.reparentTo(battle)
    tv.setH(180)
    tv.hide()

    tracks = Parallel()
    tracks.append(__getSoundTrack(level, 2.3, toon))

    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()

    toonTrack = Sequence(
        Func(MovieUtil.showProps, buttons, hands),
        Func(toon.headsUp, battle, endPos),
        Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'zap-button')),
        Func(MovieUtil.removeProps, buttons),
        Func(toon.loop, 'neutral'),
        Func(toon.setHpr, battle, origHpr)
    )
    tracks.append(toonTrack)

    coil = globalPropPool.getProp('tv')
    coil.setPos(endPos)
    coil.setH(180)

    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']
        targetPoint = lambda suit = suit: __suitTargetPoint(suit)
        buttonWaitTime = 0.7
        firstSprayAppearT = 1.8 + buttonWaitTime
        propTrack = Sequence(
                    Wait(buttonWaitTime),
                    Func(tv.setPos, endPos),
                    Func(tv.show),
                    LerpScaleInterval(tv, 0.4, 1.1, startScale=0.01, blendType='easeIn'),
                    LerpScaleInterval(tv, 0.15, 1.0, blendType='easeOut'),
                    Wait(0.85),
                    LerpScaleInterval(tv, 0.2, (1.2, 1, 0.6)),
                    LerpScaleInterval(tv, 0.1, 1.1),
                    LerpScaleInterval(tv, 0.05, 1.0),
                    Wait(3.0),
                    LerpScaleInterval(tv, 0.2, MovieUtil.PNT3_NEARZERO, blendType='easeInOut'),
                    Func(MovieUtil.removeProp, tv)
                )
        tracks.append(propTrack)

        antennaZ = 2.1
        antennaDist = 0.38

        def getFirstAntennaStartPoint(tv=tv):
            foo = tv.attachNewNode('foo')
            foo.setPos(-antennaDist, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getSecondAntennaStartPoint(tv=tv):
            foo = tv.attachNewNode('foo')
            foo.setPos(antennaDist, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getAntennaEndPoint(tv=tv):
            foo = tv.attachNewNode('foo')
            foo.setPos(0, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getSprayStartPos(tv = tv, toon = toon):
            toon.update(0)
            p = tv.getPos(render) + Point3(0, 0, 0.7)
            return p
        
        def getBeamStartPos(coil=coil, toon=toon):
            toon.update(0)
            n = hidden.attachNewNode('pointBehindSprayProp')
            n.reparentTo(toon)
            n.setPos(coil.getPos(toon))
            n.setZ(1)
            p = n.getPos(render)
            n.removeNode()
            return p

        if hp > 0:
            firstSprayTrack = Sequence(
                Wait(firstSprayAppearT),
                MovieUtil.getZapTrack(battle, WaterSprayColor, getFirstAntennaStartPoint, getAntennaEndPoint,
                                        dSprayScale, 1.8, dSprayScale, horizScale=0.2, vertScale=0.2)
            )
            tracks.append(firstSprayTrack)
            secondSprayTrack = Sequence(
                Wait(firstSprayAppearT),
                MovieUtil.getZapTrack(battle, WaterSprayColor, getSecondAntennaStartPoint, getAntennaEndPoint,
                                        dSprayScale, 1.8, dSprayScale, horizScale=0.2, vertScale=0.2)
            )
            tracks.append(secondSprayTrack)

            sprayTrack = Sequence()
            sprayTrack.append(Wait(tSprayDelay + buttonWaitTime))
            sprayTrack.append(MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale,
                                horizScale=scale, vertScale=scale))

            tracks.append(sprayTrack)

        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(zap, 
                suit, tContact + buttonWaitTime, tSuitDodges, hp, hpbonus, kbbonus,
                'large-zap', died, leftSuits, rightSuits, battle,
                toon, fShowStun, lastZap, revived=revived
            ))

    return tracks

def __doBrokenRadio(zap, delay, fShowStun, lastZap, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 3)
    tSprayDelay = 1.8
    dSprayScale = 0.05
    dSprayHold = 1.6
    tContact = 1.9
    tSuitDodges = 1.7
    dBeamHold = 1.8
    tSpray = 2.5
    tSuitDodges = 1.8
    shrinkDuration = 0.4
    scale = sprayScales[level]

    tracks = Parallel()
    tracks.append(__getSoundTrack(level, 2.3, toon))

    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()

    toonTrack = Sequence(
        Func(MovieUtil.showProps, buttons, hands),
        Func(toon.headsUp, battle, endPos),
        Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'zap-button')),
        Func(MovieUtil.removeProps, buttons),
        Func(toon.loop, 'neutral'),
        Func(toon.setHpr, battle, origHpr)
    )
    tracks.append(toonTrack)

    coil = globalPropPool.getProp('ttcc_gag_radio')
    coil.setPos(endPos)
    coil.setH(180)

    radio = globalPropPool.getProp('radio')
    radio.reparentTo(battle)
    radio.setH(180)
    radio.hide()
    buttonWaitTime = 0.7
    firstSprayAppearT = 1.8 + buttonWaitTime
    soundTrack = __getSoundTrack(level, firstSprayAppearT, toon)
    tracks.append(soundTrack)

    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']

        tvAppearTrack = Sequence(
                Wait(buttonWaitTime),
                Func(radio.setPos, endPos),
                Func(radio.show),
                LerpScaleInterval(radio, 0.4, 1.1, startScale=0.01, blendType='easeIn'),
                LerpScaleInterval(radio, 0.15, 1.0, blendType='easeOut'),
                Wait(0.85),
                LerpScaleInterval(radio, 0.2, (1.2, 1, 0.6)),
                LerpScaleInterval(radio, 0.1, 1.1),
                LerpScaleInterval(radio, 0.05, 1.0),
                Wait(3.0),
                LerpScaleInterval(radio, 0.2, MovieUtil.PNT3_NEARZERO, blendType='easeInOut'),
                Func(MovieUtil.removeProp, radio)
            )
        tracks.append(tvAppearTrack)

        targetPoint = lambda suit=suit: __suitTargetPoint(suit)

        antennaZ = 1.55
        antennaDist = 0.45

        def getFirstAntennaStartPoint(radio=radio):
            foo = radio.attachNewNode('foo')
            foo.setPos(-antennaDist, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getSecondAntennaStartPoint(radio=radio):
            foo = radio.attachNewNode('foo')
            foo.setPos(antennaDist, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getAntennaEndPoint(radio=radio):
            foo = radio.attachNewNode('foo')
            foo.setPos(0, 0, antennaZ)
            foo.wrtReparentTo(render)
            newPos = foo.getPos(render)
            foo.removeNode()
            return newPos

        def getSprayStartPos(radio=radio, toon=toon):
            toon.update(0)
            p = radio.getPos(render) + Point3(0, 0, 0.45)
            return p


        if hp > 0:
            firstSprayTrack = Sequence(
                Wait(firstSprayAppearT),
                MovieUtil.getZapTrack(battle, WaterSprayColor, getFirstAntennaStartPoint, getAntennaEndPoint,
                                        dSprayScale, 1.8, dSprayScale, horizScale=0.2, vertScale=0.2)
            )
            tracks.append(firstSprayTrack)
            secondSprayTrack = Sequence(
                Wait(firstSprayAppearT),
                MovieUtil.getZapTrack(battle, WaterSprayColor, getSecondAntennaStartPoint, getAntennaEndPoint,
                                        dSprayScale, 1.8, dSprayScale, horizScale=0.2, vertScale=0.2)
            )
            tracks.append(secondSprayTrack)

            sprayTrack = Sequence()
            sprayTrack.append(Wait(tSprayDelay + buttonWaitTime))
            sprayTrack.append(
                MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale,
                                        dSprayHold, dSprayScale,
                                        horizScale=scale, vertScale=scale))

            tracks.append(sprayTrack)

        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(zap, 
                suit, tContact + buttonWaitTime, tSuitDodges, hp, hpbonus, kbbonus,
                'small-zap', died, leftSuits, rightSuits, battle,
                toon, fShowStun, lastZap, revived=revived
            ))

    return tracks

def makeZapBeamTrack(startPosFunc, suit, tDelay, duration):
    beam = globalPropPool.getProp('zap_beam')
    beam.loop('zap_beam')
    beam.setTransparency(1)
    beam.setTwoSided(True)
    beam.hide()

    beamStageData = []

    def setupBeam():
        startPos = startPosFunc()
        endPos = suit.getPos(render) + Point3(0, 0, suit.getHeight() * 0.25)

        beam.reparentTo(render)
        beam.show()
        beam.setPos(startPos)
        beam.headsUp(endPos)

        dist = (endPos - startPos).length()

        beam.setP(beam.getP() + 10)
        beam.setScale(1, dist * 10, 1)
        beam.setColorScale(1, 1, 1, 1)

        del beamStageData[:]
        beamStageData.extend(getBeamGeomStages(beam))

        for geomNp, ts in beamStageData:
            geomNp.setTexOffset(ts, 0, 0)
            geomNp.setTexScale(ts, 1, 1)

    def phaseZap(t):
        # stronger movement so it is obvious
        offset = t * 20.0

        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                # Try V first
                geomNp.setTexOffset(ts, offset, 0)  

    def cleanupBeam():
        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                geomNp.clearTexTransform(ts)

        if beam and not beam.isEmpty():
            MovieUtil.removeProp(beam)

    return Sequence(
        Wait(tDelay),
        Func(setupBeam),
        Parallel(
            LerpFunctionInterval(
                phaseZap,
                duration,
                fromData=0.0,
                toData=1.0
            ),
            Sequence(
                Wait(max(0.0, duration - 0.2)),
                LerpColorScaleInterval(
                    beam,
                    0.2,
                    Vec4(1, 1, 1, 0),
                    startColorScale=Vec4(1, 1, 1, 1)
                )
            )
        ),
        Wait(0.05),
        Func(cleanupBeam)
    )

def getBeamGeomStages(beam):
    data = []

    for geomNp in beam.findAllMatches('**/+GeomNode'):
        stages = geomNp.findAllTextureStages()

        for i in xrange(stages.getNumTextureStages()):
            ts = stages.getTextureStage(i)

            tex = geomNp.getTexture(ts)
            if tex:
                tex.setWrapU(tex.WMRepeat)
                tex.setWrapV(tex.WMRepeat)

            data.append((geomNp, ts))

    return data

def makeZapBeamTrack2(battle, coil, suit, tDelay, duration):
    beam = globalPropPool.getProp('zap_beam')
    beam.loop('zap_beam')
    beam.setTransparency(1)
    beam.setTwoSided(True)
    beam.hide()
    beam.setH(90)

    beamStageData = []

    def getBeamGeomStages(beam):
        data = []

        for geomNp in beam.findAllMatches('**/+GeomNode'):
            stages = geomNp.findAllTextureStages()

            for i in xrange(stages.getNumTextureStages()):
                ts = stages.getTextureStage(i)

                tex = geomNp.getTexture(ts)
                if tex:
                    tex.setWrapU(tex.WMRepeat)
                    tex.setWrapV(tex.WMRepeat)

                data.append((geomNp, ts))

        return data

    def setupBeam():
        startPos = coil.getPos(render) + Point3(0, 0, 4.5)
        endPos = suit.getPos(render) + Point3(0, 0, suit.getHeight() * 0.25)

        beam.reparentTo(render)
        beam.show()
        beam.setPos(startPos)
        beam.headsUp(endPos)

        dist = (endPos - startPos).length()

        beam.setScale(1, dist * 10, 1)
        beam.setColorScale(1, 1, 1, 1)

        del beamStageData[:]
        beamStageData.extend(getBeamGeomStages(beam))

        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                geomNp.setTexOffset(ts, 0, 0)

    def phaseZap(t):
        offset = t * 14.0

        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                # Keep this axis if it matches your working direction.
                # Swap to (offset, 0), (-offset, 0), or (0, offset) if needed.
                geomNp.setTexOffset(ts, offset, 0)

    def cleanupBeam():
        for geomNp, ts in beamStageData:
            if not geomNp.isEmpty():
                geomNp.clearTexTransform(ts)

        if beam and not beam.isEmpty():
            try:
                beam.stop('zap_beam')
            except:
                pass

            try:
                MovieUtil.removeProp(beam)
            except:
                beam.removeNode()

    return Sequence(
        Wait(tDelay),
        Func(setupBeam),

        Parallel(
            LerpFunctionInterval(
                phaseZap,
                duration,
                fromData=0.0,
                toData=1.0
            ),

            Sequence(
                Wait(max(0.0, duration - 0.2)),
                LerpColorScaleInterval(
                    beam,
                    0.2,
                    Vec4(1, 1, 1, 0),
                    startColorScale=Vec4(1, 1, 1, 1)
                )
            )
        ),

        Wait(0.2),
        Func(cleanupBeam)
    )


def __doTesla(zap, delay, fShowStun, lastZap, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']

    origHpr = toon.getHpr(battle)
    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 3)
    dSprayScale = 0.05
    dSprayHold = 1.6
    scale = sprayScales[level]

    tSprayDelay = 2.5
    tContact = 2.9
    tSpray = 2.5
    tSuitDodges = 1.8
    dBeamHold = 1.8
    shrinkDuration = 0.4

    tracks = Parallel()

    # sound
    tracks.append(__getSoundTrack(level, 2.3, toon))

    # button press
    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()

    toonTrack = Sequence(
        Func(MovieUtil.showProps, buttons, hands),
        Func(toon.headsUp, battle, endPos),

        Parallel(
            ActorInterval(toon, 'pushbutton'),
            ActorInterval(button, 'zap-button')
        ),

        Func(MovieUtil.removeProps, buttons),
        Func(toon.loop, 'neutral'),
        Func(toon.setHpr, battle, origHpr)
    )
    tracks.append(toonTrack)

    # tesla coil
    coil = globalPropPool.getProp('tesla')
    coil.setPos(endPos)
    BattleParticles.loadParticles()
    propTrack = Sequence()
    propTrack.append(Func(coil.setScale, MovieUtil.PNT3_NEARZERO))
    propTrack.append(Func(coil.reparentTo, battle))
    propTrack.append(Func(coil.show))
    propTrack.append(Wait(0.5))
    propTrack.append(LerpScaleInterval(coil, 0.8, 1.2, blendType='easeOut'))
    propTrack.append(LerpScaleInterval(coil, 0.2, 1.0, blendType='easeIn'))
    propTrack.append(Wait(0.75))
    propTrack.append(LerpScaleInterval(coil, 0.2, (1.2, 1, 0.8)))
    propTrack.append(LerpScaleInterval(coil, 0.1, 1.1))
    propTrack.append(LerpScaleInterval(coil, 0.05, 1.0))
    propTrack.append(Wait(tSpray + 0.7))
    propTrack.append(LerpScaleInterval(coil, 0.3, 1.2, blendType='easeIn'))
    propTrack.append(LerpScaleInterval(coil, 0.3, MovieUtil.PNT3_NEARZERO, blendType='easeIn'))
    propTrack.append(Func(MovieUtil.removeProp, coil))
    tracks.append(propTrack)

    # targets
    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']

        hitSuit = hp > 0
        targetPoint = lambda suit = suit: __suitTargetPoint(suit)

        def getSprayStartPos(coil = coil, toon = toon):
            toon.update(0)
            p = coil.find('**/zap_origin').getPos(render)
            p.setZ(p.getZ() + 0.4)
            return p
        
        # beam instead of zap track
        if hitSuit:
            particleEffect = BattleParticles.loadParticleFile('teslaGagZap.ptf')
            partTrack = getPartTrack(particleEffect, tSprayDelay - 0.2, 1.8, [particleEffect, coil.find('**/zap_origin'), 0],
                                        softStop=-0.41, renderParent=render)
            tracks.append(partTrack)

            sprayTrack = Sequence()
            sprayTrack.append(Wait(tSprayDelay))
            sprayTrack.append(MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint,
                                                    dSprayScale, dSprayHold, dSprayScale, horizScale=scale,
                                                    vertScale=scale))

            tracks.append(sprayTrack)

        # suit reaction (unchanged)
        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(zap, 
                suit,
                tContact,
                tSuitDodges,
                hp,
                hpbonus,
                kbbonus,
                'large-zap',
                died,
                leftSuits,
                rightSuits,
                battle,
                toon,
                fShowStun, lastZap,
                revived=revived
            ))

    return tracks

def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop=0, renderParent=render):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop, renderParent=renderParent))

def __suitHeadTargetPoint(suit, other=render):
    newPos = suit.find('**/joint_head').getPos(render)
    return newPos

def __doStagelight(zap, delay, fShowStun, lastZap, uberClone = 0, npcs=[]):
    if npcs is None:
        npcs = []
    toon = zap['toon']
    battle = zap['battle']
    targets = zap['target']
    level = zap['level']
    tracks    = Parallel()  # The full animation group.
    hitTracks = Parallel()  # All of the suit reaction tracks.

        # Add the gag soundtrack.
    tracks.append(Sequence(Wait(2.50), __getSoundTrack(level, 0.0, toon)))

    # Some constants for positioning.
    stagelightZOffset = 20   # How far in the sky the stagelight will spawn.
    stagelightScale   = 1.25  # Size of the stagelight.
    stagelightFallOffset = Vec3(12, 12, -15)  # Where the stagelight falls off at.
    stagelightSpinOffset = Vec3(90, 90, 90)   # The end HPR of the stagelight when it falls.
    spotlightAlpha = 0.7  # The alpha  of the actual spotlight (not the stagelight).

    # Some constants for timing.
    stagelightDelay            = 2.50  # The delay before anything stagelight happens.
    stagelightSpawnDelay       = 0.00  # The delay before dropshadows & stagelight spawn. This is relative to stagelightDelay.
    stageLightFallDelay        = 2.20  # The time it waits for the stagelight to start falling
    stagelightFallDuration     = 0.15  # The time it takes for the stagelight & drop shadow to fall.
    stagelightGrowDelay        = 0.08  # The delay before the actual grow effect occurs.
    stagelightGrowDuration     = 0.02  # The duration for the stagelight itself to spawn in.
    stagelightHoldDuration     = 1.00  # How long the stagelight remains on the cog head.
    stagelightShrinkDuration   = [1.35, 0.40]  # The duration for the stagelight to shrink away. First is proj interval, second is hpr/scale
    stagelightFlickerDuration  = 0.05  # The duration of each stagelight flicker.
    stagelightFlickerStart     = 0.60  # The time to wait before performing any flickers.
    stagelightFlickers = [(0.0, 0.6), (0.4, 0.2), (0.6, 0.7), (0.8, 0.4), (0.9, 0.7), (1.1, 0.2), (1.2, 0.0)]  # The timing for each flicker -- the light stays off at the last one. The second value of the tuple is for the alpha upon unflicker.
    stagelightParticleRushTime = 0.00  # How much sooner the particles spawn.
    glassBreakDuration         = 0.40  # The duration of the glass break particles.
    suitSurpriseDelay          = 0.70  # The delay before the Suit gets surprised by the light.
    suitReactionTime           = 0.65  # The reaction time of the Suit attempting to dodge.
    suitReactionBuffer         = 0.05  # A buffer time to end the suit reaction early.
    suitReactionDelay          = stagelightDelay + + stageLightFallDelay + stagelightFallDuration  # The delay before all of the suit zap reactions happen.
    dodgeTime                  = suitReactionDelay - suitReactionTime  # Time before the attack is dodged.
    dropshadowScaleTrack = (
        # The time & scales for the dropshadow (multiplied by the stagelight scale).
        (0.0, 0.01),
        (stagelightFlickers[-1][0] + stagelightFlickerStart, 0.01),
        (stageLightFallDelay + stagelightFallDuration, 1.1),
    )
    dropshadowActive = False  # use the dropshadow?

    # Set up the stagelight for drop usage.
    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']
        hitSuit = hp > 0
        suitPos = suit.getPos(battle)
        tContact = 5.0
        tSpray = 1.5
        tSuitDodges = 4
        targetTracks = Parallel()

        if not hitSuit:
            continue

        stagelight = globalPropPool.getProp('stagelight')
        stagelight.hide()
        node = stagelight.node()
        node.setBounds(OmniBoundingVolume())
        node.setFinal(1)
        stagelight.reparentTo(render)
        spotlight = stagelight.find('**/spotlight')
        spotlight.setColorScale(1.0, 1.0, 1.0, spotlightAlpha)
        if battle.hasLocalToon():
            stagelight.setBin('fixed', 1)

        # Load the button in.
        buttonSound = globalBattleSoundCache.getSound('AA_drop_trigger_box.ogg')
        button = globalPropPool.getProp('zap-button')
        buttons = [button]

        # Make the toon track. They need to take out the button and use it.
        hands = toon.getLeftHands()
        toonTrack = Sequence(
            Func(MovieUtil.showProps, buttons, hands),
            Parallel(
                ActorInterval(button, 'zap-button'),
                ActorInterval(toon, 'pushbutton')
            ),
            Func(MovieUtil.removeProps, buttons),
            Func(toon.loop, 'neutral')
        )
        toonTrack = Parallel(
            toonTrack,
            Sequence(Wait(2.3), SoundInterval(buttonSound, duration=0.67, node=toon))
        )
        targetTracks.append(toonTrack)

        # Set up the stagelight track.
        # The stagelight has hit -- so we do all the special suit reactions for it.
        stagelightTrack = Parallel()
        targetTracks.append(Sequence(Wait(stagelightDelay), stagelightTrack))

        # Add the gag soundtrack.
        #stagelightTrack.append(__getSoundTrack(level, 0.0, toon))

        # Helper method to position the stagelight prop.
        def positionStagelight(stagelight=stagelight, suit=suit):
            stagelight.setPos(suit.getPos(render) + Vec3(0, 0, stagelightZOffset))

        # OK, We'll now make the dropshadow track.
        # Set up the track now.
        dropshadowTrack = Sequence(Wait(stagelightSpawnDelay))
        if dropshadowActive:
            stagelightTrack.append(dropshadowTrack)

        # Create a dropshadow. Base it off the suit because we're lazy.
        dropShadow = MovieUtil.copyProp(suit.getShadowJoint())

        # Helper method to position the dropshadow:
        def posShadow():
            # Drop shadow positioning.
            dropShadow.reparentTo(battle)
            dropShadow.setPos(suit.getPos(battle))
            dropShadow.setHpr(suit.getHpr(battle))

            # Raise the drop shadow to curb level.
            dropShadow.setZ(dropShadow.getZ() + 0.025)

        # Make the shadow track.
        dropshadowTrack.append(Func(battle.movie.needRestoreRenderProp, dropShadow))
        dropshadowTrack.append(Func(posShadow))
        for trackIndex in range(len(dropshadowScaleTrack))[1:]:
            timeA, scaleA = dropshadowScaleTrack[trackIndex - 1]
            timeB, scaleB = dropshadowScaleTrack[trackIndex + 0]
            scaleA *= stagelightScale
            scaleB *= stagelightScale
            dropshadowTrack.append(
                LerpScaleInterval(
                    nodePath=dropShadow, duration=timeB - timeA,
                    startScale=scaleA, scale=scaleB,
                )
            )
        dropshadowTrack.append(Func(MovieUtil.removeProp, dropShadow))
        dropshadowTrack.append(Func(battle.movie.clearRenderProp, dropShadow))

        # From here,
        if hitSuit:
            # Some helper methods for what's about to happen!
            hiddenParts = []

            def reparentStagelight(stagelight=stagelight, suit=suit, hiddenParts=hiddenParts):
                stagelight.wrtReparentTo(suit.find('**/joint_head'))
                stagelight.setPos(0, 0, 0)
                stagelight.setHpr(0, 0, 0)
                stagelight.setColorScaleOff(1)

                if suit.dna.name not in ('lgator', 'treasure'):
                    for part in suit.getHeadParts():
                        if not part.isHidden():
                            part.hide()
                            hiddenParts.append(part)

            def unparentStagelight(stagelight=stagelight, hiddenParts=hiddenParts):
                stagelight.wrtReparentTo(render)

                for part in hiddenParts:
                    part.show()

                hiddenParts[:] = []

            # Create the suit reaction track.
            suitReaction = Sequence()
            suitReaction = Sequence(
                Wait(stagelightSpawnDelay),
                Wait(stagelightGrowDuration),
                Wait(suitSurpriseDelay),
                Func(suit.play, 'soak')
            )

            # The Suit now gets hit and obliterated by the stagelight!
            stagelightEndCallback = lambda suit=suit: __suitHeadTargetPoint(suit, other=render)
            stagelightMoveTrack = Sequence(
                # Wait before the stagelight should go.
                Wait(stagelightSpawnDelay),

                # Initial movement sequence.
                Parallel(
                    # The suit begins its reaction, the stagelight spawns and starts falling.
                    suitReaction,
                    Sequence(
                        # We reveal the stagelight here.
                        Wait(stagelightGrowDelay),

                        # Reveal it now.
                        Func(stagelight.show),

                        # Scale it in.
                        LerpScaleInterval(
                            nodePath=stagelight,
                            duration=stagelightGrowDuration,
                            startScale=MovieUtil.PNT3_NEARZERO,
                            scale=stagelightScale,
                            other=render,
                            blendType='easeIn',
                        ),
                    ),
                    Sequence(
                        Func(positionStagelight),
                        Wait(stageLightFallDelay),
                        LerpPosInterval(
                            nodePath=stagelight,
                            duration=stagelightFallDuration,
                            pos=stagelightEndCallback,
                            blendType='easeIn',
                        ),
                    ),
                    name='stagelightInitialMove',
                ),

                # The stagelight should now stick onto the suit's head and sit there.
                Func(reparentStagelight),
                Wait(stagelightHoldDuration),

                # At this point, the stagelight slumps off.
                Func(unparentStagelight),
                Parallel(
                    ProjectileInterval(
                        node=stagelight,
                        duration=stagelightShrinkDuration[0],
                        endPos=lambda: stagelightEndCallback() + stagelightFallOffset,
                    ),
                    LerpHprInterval(
                        nodePath=stagelight,
                        duration=stagelightShrinkDuration[1],
                        hpr=stagelightSpinOffset,
                    ),
                    LerpScaleInterval(
                        nodePath=stagelight,
                        duration=stagelightShrinkDuration[1],
                        startScale=stagelightScale,
                        scale=MovieUtil.PNT3_NEARZERO,
                        blendType='easeIn',
                    ),
                ),

                # Cleanup.
                Func(MovieUtil.removeProp, stagelight),
                name='stagelightMoveTrack',
            )

            # Make the flicker track.
            flickerTrack = Track()
            completeFlickerSequence = Sequence(
                Wait(stagelightSpawnDelay),
                Wait(stagelightFlickerStart),
                flickerTrack,
            )
            for flickerIndex, flickerData in enumerate(stagelightFlickers):
                flickerTime, flickerAlpha = flickerData
                lastTime = flickerIndex == (len(stagelightFlickers) - 1)
                flickerSeq = Sequence(
                    Func(spotlight.hide),
                    Wait(stagelightFlickerDuration),
                    (Func(spotlight.show) if not lastTime else Wait(0.0)),
                    Func(spotlight.setColorScale, 1.0, 1.0, 1.0, flickerAlpha)
                )
                flickerTrack.append((flickerTime, flickerSeq))

            # Make particle track.
            BattleParticles.loadParticles()
            particleEffect = BattleParticles.loadParticleFile('stagelightGagZap.ptf')
            freezeEffect = BattleParticles.createParticleEffect(file='stagelightGagBreak')
            BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
            particleTrack = Sequence(
                Wait(stagelightSpawnDelay),
                Wait(stageLightFallDelay - stagelightParticleRushTime),
                Wait(stagelightFallDuration),
                Parallel(
                    # Glass break track.
                    getPartTrack(
                        particleEffect=freezeEffect,
                        startDelay=0.0,
                        durationDelay=glassBreakDuration,
                        partExtraArgs=[freezeEffect, stagelight, 0],
                        renderParent=render,
                    ),
                    # Electricity track.
                    getPartTrack(
                        particleEffect=particleEffect,
                        startDelay=0.0,
                        durationDelay=stagelightHoldDuration + stagelightParticleRushTime + stagelightShrinkDuration[1],
                        partExtraArgs=[particleEffect, stagelight, 0],
                        softStop=-stagelightShrinkDuration[1],
                        renderParent=render,
                    ),
                ),
            )

            # Now, put all the sequences together.
            stagelightTrack.append(suitReaction)
            stagelightTrack.append(stagelightMoveTrack)
            stagelightTrack.append(completeFlickerSequence)
            stagelightTrack.append(particleTrack)
            tracks.append(targetTracks)
        if hp > 0 or delay <= 0:
            hitTracks.append(
                __getSuitTrack(zap, suit, 0, tSuitDodges, hp, hpbonus, kbbonus, 'large-zap', died, leftSuits, rightSuits,
                               battle, toon, fShowStun, lastZap, beforeStun=2.6, afterStun=2.3, revived=revived, npcs=npcs))
    tracks.append(Sequence(Wait(suitReactionDelay), hitTracks))


    return tracks


def __doLightning(zap, delay, fShowStun, lastZap, uberClone = 0, npcs=[]):
    if npcs is None:
        npcs = []
    toon = zap['toon']
    battle = zap['battle']
    targets = zap['target']
    level = zap['level']
    tContact = 3.6
    tSuitDodges = 3.1
    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    targets = zap['target']
    origHpr = toon.getHpr(battle)
    tracks = Parallel()
    soundTrack = __getSoundTrack(level, 2.6, toon)
    tracks.append(soundTrack)
    cagePropTracks = Parallel()
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands),
                         Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'zap-button')),
                         Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'))
    tracks.append(toonTrack)
    BattleParticles.loadParticles()
    if not 'npc' in zap:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    for t in targets:
        suit = t['suit']
        hp = t['hp']
        died = t['died']
        revived = t['revived']
        hpbonus = zap['hpbonus']
        leftSuits = t['leftSuits']
        kbbonus = t['kbbonus']
        rightSuits = t['rightSuits']
        hitSuit = hp > 0
        suitPos = suit.getPos(battle)

        if not hitSuit:
            continue

        lightning = globalPropPool.getProp('lightning')
        lightning.reparentTo(battle)
        lightning.hide()
        lightning.setScale(1, 1, 3)

        def getCloudTrack(lightning, suit, battle = battle):
            particleEffect = BattleParticles.loadParticleFile('lightningGagExplosion.ptf')
            particleEffect.setScale(suit.scale * 1.5)
            particleNode = suit.attachNewNode('zap-particle-node')
            particleNode.setColorScaleOff(1)
            particleEffect.getParticlesNamed('particles-1').emitter.setOffsetForce(Vec3(0.0000, 0.0000, 15.0000 + suit.height))
            partTrack = getPartTrack(particleEffect, tContact - 0.61, 3.0, [particleEffect, particleNode, 0], softStop=-2.4, renderParent=particleNode)
            tracks = Parallel()
            track = Sequence(
                Wait(tContact),
                Func(lambda suit=suit: lightning.setPos(suit.getPos(battle))),
                Func(lightning.show),
                Wait(0.1),
                LerpColorScaleInterval(lightning, 1.0, (1, 1, 1, 0)),
                Func(MovieUtil.removeProp, lightning)
            )
            tracks.append(track)
            tracks.append(Sequence(partTrack, Func(particleNode.removeNode)))
            return tracks

        if hp > 0:
            tracks.append(getCloudTrack(lightning, suit))
        if hp > 0 or delay <= 0:
            tracks.append(
                __getSuitTrack(zap, suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'large-zap', died, leftSuits, rightSuits,
                           battle, toon, fShowStun, lastZap, beforeStun=2.6, afterStun=2.3, revived=revived, npcs=npcs))


    tracks.append(cagePropTracks)


    return Sequence(Wait(0.5), tracks)


def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
    if poseExtraArgs:
        propTrack.append(Func(prop.pose, *poseExtraArgs))
    propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale))
    return propTrack

def __showProp(prop, parent, pos, hpr = None, scale = None):
    prop.reparentTo(parent)
    prop.setPos(pos)
    if hpr:
        prop.setHpr(hpr)
    if scale:
        prop.setScale(scale)



zapfn_array = (__doJoybuzzer,
 __doRug,
 __doBrokenRadio,
 __doBattery,
 __doBrokenTV,
               __doStagelight,
               __doTesla,
 __doLightning)
