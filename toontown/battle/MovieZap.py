import random
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.battle.BattleSounds import *
from toontown.toon.ToonDNA import *
from toontown.battle import MovieUtil
from toontown.suit.SuitDNA import *
from toontown.battle import MovieUtil
from toontown.chat.ChatGlobals import *
from toontown.battle import MovieNPCSOS
from toontown.battle import MovieCamera
from direct.directnotify import DirectNotifyGlobal
from toontown.battle import BattleParticles
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import ToontownBattleGlobals

notify = DirectNotifyGlobal.directNotify.newCategory('MovieZap')
hitSoundFiles = ('AA_tesla.ogg', 'AA_carpet.ogg', 'AA_balloon.ogg', 'AA_zap_radio.ogg',
                 'AA_zap_tv.ogg', 'AA_zap_stagelight_hit.ogg', 'AA_tesla.ogg', 'AA_lightning.ogg')
missSoundFiles = ('AA_tesla.ogg', 'AA_carpet.ogg', 'AA_balloon.ogg', 'AA_zap_radio.ogg',
                 'AA_zap_tv.ogg', 'AA_zap_stagelight_miss.ogg', 'AA_tesla.ogg', 'AA_lightning.ogg')
sprayScales = [0.2,
               0.3,
               0.1,
               0.6,
               0.8,
               1.0,
               2.0]
WaterSprayColor = Point4(1.0, 1.0, 0, 1.0)
zapPos = Point3(0, 0, 0)
zapHpr = Vec3(0, 0, 0)

def doZaps(zaps):
    if len(zaps) == 0:
        return (None, None)

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
            delay = delay + TOON_ZAP_SUIT_DELAY
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
        for target in zaps[0]['target']:
            if len(zaps) == 1 and target['hp'] > 0:
                fShowStun = 1
            else:
                fShowStun = 0

    elif len(zaps) == 1 and zaps[0]['target']['hp'] > 0:
        fShowStun = 1
    else:
        fShowStun = 0
    for s in zaps:
        tracks = __doZap(s, delay, fShowStun, uberClone, npcs)
        if s['level'] >= ToontownBattleGlobals.UBER_GAG_LEVEL_INDEX:
            uberClone = 1
        if tracks:
            for track in tracks:
                toonTracks.append(track)

        delay = delay + TOON_ZAP_DELAY

    return toonTracks


def __doZap(zap, delay, fShowStun, uberClone = 0, npcs=[]):
    zapSequence = Sequence(Wait(delay))
    if type(zap['target']) == type([]):
        for target in zap['target']:
            notify.debug('toon: %s zaps prop: %d at suit: %d for hp: %d' % (zap['toon'].getName(),
             zap['level'],
             target['suit'].doId,
             target['hp']))

    else:
        notify.debug('toon: %s zaps prop: %d at suit: %d for hp: %d' % (zap['toon'].getName(),
         zap['level'],
         zap['target']['suit'].doId,
         zap['target']['hp']))
    if uberClone:
        ival = zapfn_array[zap['level']](zap, delay, fShowStun, uberClone, npcs=npcs)
        if ival:
            zapSequence.append(ival)
    else:
        ival = zapfn_array[zap['level']](zap, delay, fShowStun, npcs=npcs)
        if ival:
            zapSequence.append(ival)
    return [zapSequence]


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

def __getSuitTrack(suit, tContact, tDodge, hp, hpbonus, kbbonus, anim, died, leftSuits, rightSuits, battle, toon, fShowStun, beforeStun = 0.5, afterStun = 2.0, uberRepeat = 0, revived = 0, npcs = [], dodge=False):
    if hp > 0:
        suitTrack = Sequence()
        zapTracks = Parallel()
        deathTracks = Sequence(Wait(0.8))
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
            showDamage = Sequence(Func(suit.showHpTextNew, -hp, text="AFTERSHOCK!", colorCode=3), Func(suit.makeZapped, +int(math.ceil(hp / 4))), Func(suit.makeSoaked, 0))
        else:
            showDamage = Func(suit.showHpText, -hp, openEnded=0, attackTrack=ZAP_TRACK)
        updateHealthBar = Func(suit.updateHealthBar, hp)
        soakRemoval = Func(suit.makeZapped)
        suitTrack.append(Func(suit.makeSoaked, 0))
        suitTrack.append(Wait(tContact))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        resetPos, resetHpr = battle.getActorPosHpr(suit)
        zapTrack = Sequence(ActorInterval(suit, anim, startTime=0, endTime=0.8))
        suitTrack.append(Parallel(MovieUtil.zapCog(suit, anim, .5, 2.0, battle), MovieUtil.createSuitStunInterval(suit, .5, 2.0), deathTracks))
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
        if died != 0 and suit.isVirtual:
            suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        if died != 0 and not suit.isVirtual:
            deathTracks.append(MovieUtil.shortCircuitTrack(suit, battle))
        else:
            #suitTrack.append(__createSuitResetPosTrack(suit, battle))
            suitTrack.append(Func(battle.unlureSuit, suit))
            #suitTrack.append(__soakRemoval(suit))
        if revived != 0 and suit.isSkeleton:
            suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
        if revived != 0 and not suit.isSkeleton and not suit.dna.name == 'redd':
            suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTrack.append(Func(suit.setDizzy, 0))
       # suitTrack.append(createSuitResetPosTrack(suit, battle))
        suitTrack.append(Func(suit.setNeutralAnimationTrap))
        #suitTrack.append(Parallel(__soakRemoval(suit, 1)))
        #suitTrack.append(soakRemoval)
        #suitTrack.append(Func(suit.setNeutralAnimation))
        if suit.dna.name == 'sgoat' and suit.isShielding:
            suitTrack.append(Func(suit.addRageBuilding, hp))
        if suit.dna.name == 'phouse':
            suitTrack.append(Func(suit.addPowerhouseRotation, hp))
        if suit.dna.name == 'liquid' and suit.isStormCell:
            suitTrack.append(Func(suit.removeStormCellDamage, -6))
        if suit.isHeavyRain:
            suitTrack.append(Func(suit.addHeavyRainDamage, hp))
        if suit.isSued:
            suitTrack.append(Func(suit.makeSued, 3))
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


def __doJoybuzzer(zap, delay, fShowStun, npcs=[]):
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
            tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived))
    return tracks


def __doRug(zap, delay, fShowStun, npcs=[]):
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
            tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived))
    return tracks


def __doBalloon(zap, delay, fShowStun, npcs=[]):
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
            tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits, battle, toon, fShowStun, revived=revived))
    return tracks


def __doBattery(zap, delay, fShowStun, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    target = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    origPos = toon.getPos(battle)
    battery = globalPropPool.getProp('battery')
    runBackHpr = Vec3(0, 0, 0)
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    scale = 0.3
    tAppearDelay = 0.7
    dHoseHold = 0.7
    midPos = Point3(toon.getX(battle)*.5, 0, 0)
    runDur = 1
    tSprayDelay = 2
    tSpray = 1
    dSprayScale = 0.1
    dSprayHold = 1.8
    tContact = 2
    tSuitDodges = 2.1
    tracks = Parallel()
    toonTrack = Sequence(Wait(tAppearDelay), Func(MovieUtil.showProp, battery, hand_jointpath0),
        Func(toon.loop, 'catch-run'), Wait(1), Func(toon.loop, 'catch-neutral'), Wait(3), Func(toon.stop), Func(toon.setHpr, battle, runBackHpr),
        Func(toon.loop, 'run'), Wait(1), Func(toon.stop), Func(toon.loop, 'catch-run'), Func(toon.loop, 'neutral'), Func(MovieUtil.removeProp, battery), Func(toon.setHpr, battle, origHpr))
    
    moveTrack = Sequence(Wait(tAppearDelay), LerpPosInterval(toon, runDur, midPos, other=battle), Wait(3), LerpPosInterval(toon, runDur, origPos, 
        other=battle))
    
    tracks.append(toonTrack)
    tracks.append(moveTrack)
    soundTrack = __getSoundTrack(level, tSprayDelay, toon)
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
        hitSuit = hp > 0
        suitPos = suit.getPos(battle)
        targetPoint = lambda suit=suit: __suitTargetPoint(suit)

        def getSprayStartPos(coil=coil, toon=toon):
            toon.update(0)
            p = coil.getPos(render)
            p.setZ(5)  # Temp "fix," this doesn't like to cooperate
            return p

        sprayTrack = Sequence()
        sprayTrack.append(Wait(tSprayDelay))
        sprayTrack.append(
            MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold,
                                  dSprayScale,
                                  horizScale=scale, vertScale=scale))

        if hp > 0:
            tracks.append(sprayTrack)
        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'shock', died, leftSuits, rightSuits, battle, toon,
                fShowStun, revived=revived))
    
    return tracks


def __doTazer(zap, delay, fShowStun, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    origPos = toon.getPos(battle)
    tazer = globalPropPool.getProp('tazer')
    tazer.setHpr(180, 0, 0)
    runBackHpr = Vec3(0, 0, 0)
    hands = toon.getRightHands()
    hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
    hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
    scale = 0.3
    tAppearDelay = 0.7
    dHoseHold = 0.7
    midPos = Point3(toon.getX(battle)*.5, 0, 0)
    runDur = 1
    tSprayDelay = 2
    tSpray = 1
    dSprayScale = 0.1
    dSprayHold = 1.8
    tContact = 2
    tSuitDodges = 2.1
    tracks = Parallel()
    toonTrack = Sequence(Wait(tAppearDelay), Func(MovieUtil.showProp, tazer, hand_jointpath0),
        Func(toon.loop, 'run'), Wait(1), Func(toon.pingpong, 'cast', fromFrame=30, toFrame=40), Wait(3), Func(toon.stop), 
        Func(toon.setHpr, battle, runBackHpr), Func(toon.loop, 'run'), Wait(1), Func(toon.stop), Func(toon.loop, 'neutral'), 
        Func(MovieUtil.removeProp, tazer), Func(toon.setHpr, battle, origHpr))
    
    moveTrack = Sequence(Wait(tAppearDelay), LerpPosInterval(toon, runDur, midPos, other=battle), Wait(3), LerpPosInterval(toon, runDur, origPos, 
        other=battle))
    
    tracks.append(toonTrack)
    tracks.append(moveTrack)
    soundTrack = __getSoundTrack(level, tSprayDelay, toon)
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
        hitSuit = hp > 0
        suitPos = suit.getPos(battle)
        targetPoint = lambda suit=suit: __suitTargetPoint(suit)

        def getSprayStartPos(coil=coil, toon=toon):
            toon.update(0)
            p = coil.getPos(render)
            p.setZ(5)  # Temp "fix," this doesn't like to cooperate
            return p

        sprayTrack = Sequence()
        sprayTrack.append(Wait(tSprayDelay))
        sprayTrack.append(
            MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold,
                                  dSprayScale,
                                  horizScale=scale, vertScale=scale))

        if hp > 0:
            tracks.append(sprayTrack)
        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'shock', died, leftSuits, rightSuits, battle,
                toon, fShowStun, revived=revived))
    
    return tracks


def __doBrokenTV(zap, delay, fShowStun, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 3)
    scale = sprayScales[level]
    tButton = 0.0
    dButtonScale = 0.5
    dButtonHold = 3.0
    dSprayScale = 0.1
    dSprayHold = 1.8
    tContact = 2.9
    tSpray = 2.5
    tSprayDelay = 2.5
    tSuitDodges = 1.8
    shrinkDuration = 0.4
    tracks = Parallel()
    soundTrack = __getSoundTrack(level, 2.3, toon)
    tracks.append(soundTrack)
    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle, endPos),
                         Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'zap-button')),
                         Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'),
                         Func(toon.setHpr, battle, origHpr))

    tracks.append(toonTrack)
    coil = globalPropPool.getProp('tv')
    coil.setPos(endPos)
    coil.setH(180)
    propTrack = Sequence()
    propTrack.append(Func(coil.show))
    propTrack.append(Func(coil.setScale, Point3(0.1, 0.1, 0.1)))
    propTrack.append(Func(coil.reparentTo, battle))
    propTrack.append(LerpScaleInterval(coil, 1.5, Point3(1.0, 1.0, 1.0)))
    propTrack.append(Wait(tSpray + 2))
    propTrack.append(LerpScaleInterval(nodePath=coil, scale=Point3(1.0, 1.0, 0.1), duration=shrinkDuration))
    propTrack.append(Func(MovieUtil.removeProp, coil))
    tracks.append(propTrack)
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

        def getSprayStartPos(coil=coil, toon=toon):
            toon.update(0)
            p = coil.getPos(render)
            p.setZ(5)  # Temp "fix," this doesn't like to cooperate
            return p

        sprayTrack = Sequence()
        sprayTrack.append(Wait(tSprayDelay))
        sprayTrack.append(
            MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold,
                                  dSprayScale,
                                  horizScale=scale, vertScale=scale))

        if hp > 0:
            tracks.append(sprayTrack)
        if hp > 0 or delay <= 0:
            tracks.append(
                __getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'large-zap', died, leftSuits, rightSuits,
                           battle,
                           toon, fShowStun, revived=revived))

    return tracks

def __doBrokenRadio(zap, delay, fShowStun, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 3)
    scale = sprayScales[level]
    tButton = 0.0
    dButtonScale = 0.5
    dButtonHold = 3.0
    dSprayScale = 0.1
    dSprayHold = 1.8
    tContact = 2.9
    tSpray = 2.5
    tSprayDelay = 2.5
    tSuitDodges = 1.8
    shrinkDuration = 0.4
    tracks = Parallel()
    soundTrack = __getSoundTrack(level, 2.3, toon)
    tracks.append(soundTrack)
    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle, endPos),
                         Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'zap-button')),
                         Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'),
                         Func(toon.setHpr, battle, origHpr))

    tracks.append(toonTrack)
    coil = globalPropPool.getProp('ttcc_gag_radio')
    coil.setPos(endPos)
    coil.setH(180)
    propTrack = Sequence()
    propTrack.append(Func(coil.show))
    propTrack.append(Func(coil.setScale, Point3(0.1, 0.1, 0.1)))
    propTrack.append(Func(coil.reparentTo, battle))
    propTrack.append(LerpScaleInterval(coil, 1.5, Point3(1.0, 1.0, 1.0)))
    propTrack.append(Wait(tSpray + 2))
    propTrack.append(LerpScaleInterval(nodePath=coil, scale=Point3(1.0, 1.0, 0.1), duration=shrinkDuration))
    propTrack.append(Func(MovieUtil.removeProp, coil))
    tracks.append(propTrack)
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

        def getSprayStartPos(coil=coil, toon=toon):
            toon.update(0)
            p = coil.getPos(render)
            p.setZ(5)  # Temp "fix," this doesn't like to cooperate
            return p

        sprayTrack = Sequence()
        sprayTrack.append(Wait(tSprayDelay))
        sprayTrack.append(
            MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold,
                                  dSprayScale,
                                  horizScale=scale, vertScale=scale))

        if hp > 0:
            tracks.append(sprayTrack)
        if hp > 0 or delay <= 0:
            tracks.append(
                __getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'small-zap', died, leftSuits, rightSuits,
                               battle,
                               toon, fShowStun, revived=revived))

    return tracks


def __doTesla(zap, delay, fShowStun, npcs=[]):
    toon = zap['toon']
    level = zap['level']
    hpbonus = zap['hpbonus']
    targets = zap['target']
    battle = zap['battle']
    origHpr = toon.getHpr(battle)
    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 3)
    scale = sprayScales[level]
    tButton = 0.0
    dButtonScale = 0.5
    dButtonHold = 3.0
    dSprayScale = 0.1
    dSprayHold = 1.8
    tContact = 2.9
    tSpray = 2.5
    tSprayDelay = 2.5
    tSuitDodges = 1.8
    shrinkDuration = 0.4
    tracks = Parallel()
    soundTrack = __getSoundTrack(level, 2.3, toon)
    tracks.append(soundTrack)
    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands), Func(toon.headsUp, battle, endPos), Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'zap-button')),
        Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'), Func(toon.setHpr, battle, origHpr))
    
    tracks.append(toonTrack)
    coil = globalPropPool.getProp('tesla')
    coil.setPos(endPos)
    propTrack = Sequence()
    propTrack.append(Func(coil.show))
    propTrack.append(Func(coil.setScale, Point3(0.1, 0.1, 0.1)))
    propTrack.append(Func(coil.reparentTo, battle))
    propTrack.append(LerpScaleInterval(coil, 1.5, Point3(1.0, 1.0, 1.0)))
    propTrack.append(Wait(tSpray + 2))
    propTrack.append(LerpScaleInterval(nodePath=coil, scale=Point3(1.0, 1.0, 0.1), duration=shrinkDuration))
    propTrack.append(Func(MovieUtil.removeProp, coil))
    tracks.append(propTrack)
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

        def getSprayStartPos(coil = coil, toon = toon):
            toon.update(0)
            p = coil.getPos(render)
            p.setZ(5) #Temp "fix," this doesn't like to cooperate
            return p


        sprayTrack = Sequence()
        sprayTrack.append(Wait(tSprayDelay))
        sprayTrack.append(MovieUtil.getZapTrack(battle, WaterSprayColor, getSprayStartPos, targetPoint, dSprayScale, dSprayHold, dSprayScale,
            horizScale=scale, vertScale=scale))

        if hp > 0:
            tracks.append(sprayTrack)
        if hp > 0 or delay <= 0:
            tracks.append(__getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'large-zap', died, leftSuits, rightSuits, battle,
                toon, fShowStun, revived=revived))
    
    return tracks

def __doStagelight(zap, delay, fShowStun, uberClone = 0, npcs=[]):
    if npcs is None:
        npcs = []
    toon = zap['toon']
    battle = zap['battle']
    targets = zap['target']
    level = zap['level']
    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    origHpr = toon.getHpr(battle)
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands),
                         Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'zap-button')),
                         Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'))
    if not 'npc' in zap:
        toonTrack.append(Func(toon.setHpr, battle, origHpr))
    tracks = Parallel()
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, 3, toon)
    tracks.append(soundTrack)
    cagePropTracks = Parallel()
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
        cage = globalPropPool.getProp('ttcc_gag_stagelight')
        texture = loader.loadTexture('phase_5/maps/battle/ttcc_gag_stagelight.png')
        texture2 = loader.loadTexture('phase_3/maps/ttcc_lights_palette.png')
        cage.find('**/stagelight').setTexture(texture, 1)
        cage.find('**/spotlight').setTexture(texture2, 1)
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        y = suitPos.getY()
        cagePos = [Point3(0, 0, suit.height + 15), suit.getHpr(battle)]
        for headPart in suit.headParts:
            head = headPart
            headPartShow = Parallel(Func(headPart.show))
            headPartHide = Parallel(Func(headPart.hide))
        if hitSuit:
            cagePropTrack = Sequence(getPropAppearTrack(cage, suit, cagePos, 3, scaleUpPoint=Point3(1.5, 1.5, 1.5), scaleUpTime=0),
                                     Parallel(ActorInterval(suit, 'soak', endTime=1.5), Func(suit.setNeutralAnimation)),
                                     Wait(0.25),
            Func(cage.find('**/spotlight').hide),
                Parallel(cagePosition, Func(cage.reparentTo, head)),
                Parallel(cage.posInterval(0.1, Point3(0, 0, 0), blendType='easeIn')), Wait(2),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
            )
            tracks.append(cagePropTrack)
        else:
            cagePropTrack = Sequence(
                getPropAppearTrack(cage, suit, cagePos, 3, scaleUpPoint=Point3(1.5, 1.5, 1.5), scaleUpTime=0),
                Parallel(ActorInterval(suit, 'soak', endTime=1.5), Func(suit.setNeutralAnimation)),
                Wait(0.25),
                Func(cage.find('**/spotlight').hide),
            Parallel(cagePosition),
            Parallel(cage.posInterval(0.1, Point3(suitPos.getX(), 0, 0), blendType='easeIn')),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
        )
        if hp > 0 or delay <= 0:
            tracks.append(
                __getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'large-zap', died, leftSuits, rightSuits,
                               battle, toon, fShowStun, beforeStun=2.6, afterStun=2.3, revived=revived, npcs=npcs))
    tracks.append(cagePropTracks)


    return tracks


def __doLightning(zap, delay, fShowStun, uberClone = 0, npcs=[]):
    if npcs is None:
        npcs = []
    toon = zap['toon']
    battle = zap['battle']
    targets = zap['target']
    level = zap['level']
    button = globalPropPool.getProp('zap-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    targets = zap['target']
    origHpr = toon.getHpr(battle)
    tracks = Parallel()
    cagePropTracks = Parallel()
    toonTrack = Sequence(Func(MovieUtil.showProps, buttons, hands),
                         Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'zap-button')),
                         Func(MovieUtil.removeProps, buttons), Func(toon.loop, 'neutral'))
    tracks.append(toonTrack)
    soundTrack = __getSoundTrack(level, 2.5, toon)
    tracks.append(soundTrack)
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
        tContact = 3.5
        tSpray = 1.5
        tSuitDodges = 1.5
        cage = loader.loadModel('phase_5/models/props/lightning')
        cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
        y = suitPos.getY()
        cagePos = [Point3(suitPos.getX(), y, 100.0), suit.getHpr(battle)]
        cagePropTrack = Sequence(
            getPropAppearTrack(cage, battle, cagePos, 3.5, scaleUpPoint=Point3(5.0, 2.0, 10.0), scaleUpTime=0),
            Parallel(cagePosition),
            Parallel(cage.posInterval(0, Point3(suitPos.getX(), y + 1, 0.1), blendType='easeIn')), Wait(0.5),
            LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
            Func(MovieUtil.removeProp, cage)
            )
        if hp > 0:
            cagePropTracks.append(cagePropTrack)
        if hp > 0 or delay <= 0:
            tracks.append(
                __getSuitTrack(suit, tContact, tSuitDodges, hp, hpbonus, kbbonus, 'large-zap', died, leftSuits, rightSuits,
                           battle, toon, fShowStun, beforeStun=2.6, afterStun=2.3, revived=revived, npcs=npcs))


    tracks.append(cagePropTracks)


    return tracks


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
 __doBalloon,
 __doBrokenRadio,
 __doBrokenTV,
               __doStagelight,
               __doTesla,
 __doLightning)
