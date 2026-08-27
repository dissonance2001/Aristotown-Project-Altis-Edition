from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
from direct.showutil import Effects
from toontown.battle.BattleProps import *
from otp.otpbase import OTPLocalizerEnglish
from toontown.battle.BattleSounds import *
from toontown.battle.SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import BattleProps
from toontown.suit import Suit
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from toontown.suit.SuitDNA import *
from toontown.toonbase import TTLocalizer
from toontown.toonbase import ToontownGlobals
from toontown.toonbase.ToontownGlobals import *
from toontown.battle.attacks.suits import MovieIntervals

notify = DirectNotifyGlobal.directNotify.newCategory('MovieSuitAttacks')

def throwPos(t, object, duration, target, values, gravity = -32.144):
    origin = values['origin']
    velocity = values['velocity']
    if callable(target):
        target = target()
    x = origin[0] * (1 - t) + target[0] * t
    y = origin[1] * (1 - t) + target[1] * t
    time = t * duration
    z = origin[2] + velocity * time + 0.5 * gravity * time * time
    object.setPos(x, y, z)

def __doDamage(toon, dmg, died):
    return MovieIntervals.__doDamage(toon, dmg, died)

def __doDamageCheat(toon, dmg, died):
    return MovieIntervals.__doDamageCheat(toon, dmg, died)

def __showProp(prop, parent, pos, hpr = None, scale = None):
    return MovieIntervals.__showProp(prop, parent, pos, hpr, scale)

def __animProp(prop, propName, propType = 'actor'):
    return MovieIntervals.__animProp(prop, propName, propType)

def __suitFacePoint(suit, zOffset = 0):
    return MovieIntervals.__suitFacePoint(suit, zOffset)

def __toonFacePoint(toon, zOffset = 0, parent = render):
    return MovieIntervals.__toonFacePoint(toon, zOffset, parent)

def __toonTorsoPoint(toon, zOffset = 0):
    return MovieIntervals.__toonTorsoPoint(toon, zOffset)

def __toonGroundPoint(attack, toon, zOffset = 0, parent = render):
    return MovieIntervals.__toonGroundPoint(attack, toon, zOffset, parent)

def __toonGroundMissPoint(attack, prop, toon, zOffset = 0):
    return MovieIntervals.__toonGroundMissPoint(attack, prop, toon, zOffset)

def __toonMissPoint(prop, toon, yOffset = 0, parent = None):
    return MovieIntervals.__toonMissPoint(prop, toon, yOffset, parent)

def __toonMissBehindPoint(toon, parent = render, offset = 0):
    return MovieIntervals.__toonMissBehindPoint(toon, parent, offset)

def __throwBounceHitPoint(prop, toon):
    return MovieIntervals.__throwBounceHitPoint(prop, toon)

def __throwBounceMissPoint(prop, toon):
    return MovieIntervals.__throwBounceMissPoint(prop, toon)

def __throwBouncePoint(startPoint, endPoint):
    return MovieIntervals.__throwBouncePoint(startPoint, endPoint)

def getResetTrack(suit, battle):
    return MovieIntervals.getResetTrack(suit, battle)

def __createSuitResetPosTrack(suit, battle):
    return MovieIntervals.__createSuitResetPosTrack(suit, battle)

def getSuitTrack(attack, delay = 1e-06, splicedAnims = None, playRate = 1.0):
    return MovieIntervals.getSuitTrack(attack, delay, splicedAnims, playRate)

def getSuitAnimTrack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    return MovieIntervals.getSuitAnimTrack(attack, delay, splicedAnims, playRate)

def getSuitAnimTrackAttack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    return MovieIntervals.getSuitAnimTrackAttack(attack, delay, splicedAnims, playRate)

def getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    return MovieIntervals.getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop)

def getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative = 1, softStop = 0):
    return MovieIntervals.getPartTracks(attack, particleEffects, startDelay, durationDelay, worldRelative, softStop)

def getToonTrack(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrack(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)

def getToonTracks(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTracks(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, showDamageExtraTime, showMissedExtraTime)

def getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    return MovieIntervals.getToonDodgeTrack(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime)

def getAllyToonsDodgeParallel(target):
    return MovieIntervals.getAllyToonsDodgeParallel(target)

def getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5, startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0, animStartTime = 0.0):
    return MovieIntervals.getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint, scaleUpTime, scaleDownTime, startScale, anim, propName, animDuration, animStartTime)

def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    return MovieIntervals.getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint, scaleUpTime, startScale, poseExtraArgs)

def getPropThrowTrack(attack, prop, hitPoints = [], missPoints = [], hitDuration = 0.25, missDuration = 0.25, hitPointNames = 'none', missPointNames = 'none', lookAt = 'none', groundPointOffSet = 0, missScaleDown = None, parent = render, target = None):
    return MovieIntervals.getPropThrowTrack(attack, prop, hitPoints, missPoints, hitDuration, missDuration, hitPointNames, missPointNames, lookAt, groundPointOffSet, missScaleDown, parent, target)

def getThrowTrack(object, target, duration = 1.0, parent = render, gravity = -32.144):
    return MovieIntervals.getThrowTrack(object, target, duration, parent, gravity)

def getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    return MovieIntervals.getToonTakeDamageTrack(attack, toon, died, dmg, delay, damageAnimNames, splicedDamageAnims, showDamageExtraTime)

def getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames = None, splicedDamageAnims = None, showDamageExtraTime = 0.01):
    return MovieIntervals.getToonTakeDamageTrackCheat(attack, toon, died, dmg, delay, damageAnimNames, splicedDamageAnims, showDamageExtraTime)

def getSplicedAnimsTrack(anims, actor = None):
    return MovieIntervals.getSplicedAnimsTrack(anims, actor)

def getSplicedLerpAnims(animName, origDuration, newDuration, startTime = 0, fps = 30, reverse = 0):
    return MovieIntervals.getSplicedLerpAnims(animName, origDuration, newDuration, startTime, fps, reverse)

def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    return Sequence(Wait(delay), SoundInterval(globalBattleSoundCache.getSound(fileName), duration=duration, node=node))

def getToonTrackCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrackCheat(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)

def getToonTrackCheat2(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 0.0001, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, target = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTrackCheat2(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, target, showDamageExtraTime, showMissedExtraTime)


def getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime):
    return MovieIntervals.getToonDodgeTrackCheat(target, dodgeDelay, dodgeAnimNames, splicedDodgeAnims, showMissedExtraTime)


def getToonTracksCheat(attack, damageDelay = 1e-06, damageAnimNames = None, dodgeDelay = 1e-06, dodgeAnimNames = None, splicedDamageAnims = None, splicedDodgeAnims = None, showDamageExtraTime = 0.01, showMissedExtraTime = 0.5):
    return MovieIntervals.getToonTracksCheat(attack, damageDelay, damageAnimNames, dodgeDelay, dodgeAnimNames, splicedDamageAnims, splicedDodgeAnims, showDamageExtraTime, showMissedExtraTime)


def getSoundTrack(fileName, delay = 0.01, duration = 0.0, node = None):
    return Sequence(Wait(delay), SoundInterval(globalBattleSoundCache.getSound(fileName), duration=duration, node=node))

def doStarOfTheShow(attack):
    manager = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    targetData = targets[0]

    if 'suit' not in targetData:
        return Sequence()

    targetSuit = targetData['suit']
    heal = int(targetData.get('heal', 0))

    suitTracks = Parallel()
    selfDamageTracks = Parallel()
    cagePropTracks = Parallel()
    soundTracks = Parallel()

    suitTrack = getSuitAnimTrack(attack)

    soundTracks.append(getSoundTrack('SA_bash.ogg', delay=0, node=manager))
    soundTracks.append(getSoundTrack('LB_camera_shutter_2.ogg', delay=1, node=manager))
    soundTracks.append(getSoundTrack('LB_toonup.ogg', delay=1, node=manager))

    cage = loader.loadModel('phase_5/models/props/ttr_m_ara_cbg_promoted')
    cage.find('**/geo_hole_01').hide()

    platform = cage.find('**/geo_gearLift_01')
    cagePos = [Point3(0, 0, 0), Point3(180, 0, 0)]

    if targetSuit.dna.name == 'ubuster':
        cagePropTrack = Sequence(Wait(1.0), getPropAppearTrack(cage, targetSuit, cagePos, 0, scaleUpPoint=Point3(1), scaleUpTime=0), Parallel(LerpPosInterval(platform, 0.5, Point3(0, 0, 0)), LerpHprInterval(platform, 3.0, Point3(360, 0, 0))), LerpScaleInterval(cage, 0.5, Point3(0.01, 0.01, 0.01)), Func(cage.removeNode))
    else:
        cagePropTrack = Sequence(Wait(1.0), getPropAppearTrack(cage, targetSuit, cagePos, 0, scaleUpPoint=Point3(1), scaleUpTime=0), Parallel(LerpPosInterval(platform, 0.5, Point3(0, 0, 0)), LerpHprInterval(platform, 3.0, Point3(360, 0, 0)), Sequence(ActorInterval(targetSuit, 'slip-forward', startTime=2.43), Func(targetSuit.setNeutralAnimationDrop))), LerpScaleInterval(cage, 0.5, Point3(0.01, 0.01, 0.01)), Func(cage.removeNode))

    cagePropTracks.append(cagePropTrack)

    targetTrack = Sequence(Wait(1.0), Func(targetSuit.setSuitStatusEffect, 'starOfTheShow'), Func(targetSuit.setSuitStatusEffect, 'extraAttacks', modifier=1, mode='refreshModifier'))

    if heal > 0:
        targetTrack.append(Parallel(Func(targetSuit.showHpTextNew, heal), Func(targetSuit.setHealthForMe, heal), Func(targetSuit.updateHealthBar, 0)))

    selfDamageTracks.append(targetTrack)

    return Parallel(suitTracks, selfDamageTracks, suitTrack, cagePropTracks, soundTracks)

def doHardCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.2
    attackDelay = 1.2
    suitTrack = Sequence(getSuitAnimTrackAttack(attack, playRate=1.25))
    partTracks = Parallel()
    allHeadTracks = Parallel()
    allChestTracks = Parallel()
    toonTracks2 = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toon = t['toon']
        dmg = t['hp']
        headParts = toon.getHeadParts()
        sprayEffects = BattleParticles.createParticleEffect('ReOrgSprayNew')
        BattleParticles.setEffectTexture(sprayEffects, 'snow-particle',
                                         color=Vec4(random.random(), random.random(), random.random(), 1))
        partTrack = getPartTrack(sprayEffects, 0.5, 3.0, [sprayEffects, toon, 0], softStop=-1)
        partTracks.append(partTrack)
        print
        '***********headParts pos=', headParts[0].getPos()
        print
        '***********headParts hpr=', headParts[0].getHpr()
        headTracks = Parallel()
        for partNum in xrange(0, headParts.getNumPaths()):
            part = headParts.getPath(partNum)
            x = part.getX()
            y = part.getY()
            z = part.getZ()
            h = part.getH()
            p = part.getP()
            r = part.getR()
            headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                       LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)),
                                       LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)),
                                       LerpHprInterval(part, 0.25, VBase3(360, 0, 180)),
                                       LerpPosInterval(part, 0.25, Point3(x, y, z + 3.1)),
                                       LerpPosInterval(part, 0.1, Point3(x, y, z + 0.3)), Wait(0.1),
                                       LerpHprInterval(part, 0.35, VBase3(-745, 0, 180),
                                                       startHpr=VBase3(0, 0, 180)),
                                       LerpHprInterval(part, 0.5, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)),
                                       LerpPosInterval(part, 0.15, Point3(x, y, z + 1)),
                                       LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2),
                                       LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.1)))

        allHeadTracks.append(headTracks)

        def getChestTrack(part, attackDelay=attackDelay):
            origScale = part.getScale()
            return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1),
                            LerpHprInterval(part, 1.1, part.getHpr()))

        chestTracks = Parallel()
        arms = toon.findAllMatches('**/arms')
        sleeves = toon.findAllMatches('**/sleeves')
        hands = toon.findAllMatches('**/hands')
        print
        '*************arms hpr=', arms[0].getHpr()
        for partNum in xrange(0, arms.getNumPaths()):
            chestTracks.append(getChestTrack(arms.getPath(partNum)))
            chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
            chestTracks.append(getChestTrack(hands.getPath(partNum)))

        allChestTracks.append(chestTracks)

    damageAnims = [['neutral',
                    0.01,
                    0.01,
                    0.5], ['juggle',
                           0.01,
                           0.01,
                           1.48], ['think', 0.01, 2.28]]
    dodgeAnims = []
    dodgeAnims.append(['think',
                       0.01,
                       0,
                       0.6])
    toonTracks = getToonTracksCheat(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, splicedDodgeAnims=damageAnims, dodgeDelay=damageDelay,
                               showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    return Parallel(suitTrack, partTracks, toonTracks2, toonTracks, allHeadTracks, allChestTracks)

def doViralSensation(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.2
    attackDelay = 1.2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    partTracks = Parallel()
    allHeadTracks = Parallel()
    allChestTracks = Parallel()
    toonTracks2 = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            headParts = toon.getHeadParts()
            sprayEffects = BattleParticles.createParticleEffect('ReOrgSprayNew')
            BattleParticles.setEffectTexture(sprayEffects, 'snow-particle',
                                             color=Vec4(random.random(), random.random(), random.random(), 1))
            partTrack = getPartTrack(sprayEffects, 0.5, 3.0, [sprayEffects, toon, 0], softStop=-1)
            partTracks.append(partTrack)
            toonTrack = Sequence()
            toonTrack.append(Wait(damageDelay + 5))
            toonTrack.append(Parallel(Func(toon.setToonStatusEffect, 'viralSensation', modifier=50, turns=2)))
            toonTrack.append(Func(toon.showHpStringViral, "VIRAL SENSATION!"))
            toonTracks2.append(toonTrack)
            print
            '***********headParts pos=', headParts[0].getPos()
            print
            '***********headParts hpr=', headParts[0].getHpr()
            headTracks = Parallel()
            for partNum in xrange(0, headParts.getNumPaths()):
                part = headParts.getPath(partNum)
                x = part.getX()
                y = part.getY()
                z = part.getZ()
                h = part.getH()
                p = part.getP()
                r = part.getR()
                headTracks.append(Sequence(Wait(attackDelay), LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.03)),
                                           LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                           LerpPosInterval(part, 0.1, Point3(x - 0.4, y, z - 0.03)),
                                           LerpPosInterval(part, 0.1, Point3(x + 0.4, y, z - 0.03)),
                                           LerpPosInterval(part, 0.1, Point3(x - 0.2, y, z - 0.04)),
                                           LerpPosInterval(part, 0.25, Point3(x, y, z + 2.2)),
                                           LerpHprInterval(part, 0.25, VBase3(360, 0, 180)),
                                           LerpPosInterval(part, 0.25, Point3(x, y, z + 3.1)),
                                           LerpPosInterval(part, 0.1, Point3(x, y, z + 0.3)), Wait(0.1),
                                           LerpHprInterval(part, 0.35, VBase3(-745, 0, 180),
                                                           startHpr=VBase3(0, 0, 180)),
                                           LerpHprInterval(part, 0.5, VBase3(25, 0, 180), startHpr=VBase3(0, 0, 180)),
                                           LerpPosInterval(part, 0.15, Point3(x, y, z + 1)),
                                           LerpHprInterval(part, 0.3, VBase3(h, p, r)), Wait(0.2),
                                           LerpPosInterval(part, 0.1, Point3(x, y, z)), Wait(0.1)))

            allHeadTracks.append(headTracks)

            def getChestTrack(part, attackDelay=attackDelay):
                origScale = part.getScale()
                return Sequence(Wait(attackDelay), LerpHprInterval(part, 1.1, VBase3(180, 0, 0)), Wait(1.1),
                                LerpHprInterval(part, 1.1, part.getHpr()))

            chestTracks = Parallel()
            arms = toon.findAllMatches('**/arms')
            sleeves = toon.findAllMatches('**/sleeves')
            hands = toon.findAllMatches('**/hands')
            print
            '*************arms hpr=', arms[0].getHpr()
            for partNum in xrange(0, arms.getNumPaths()):
                chestTracks.append(getChestTrack(arms.getPath(partNum)))
                chestTracks.append(getChestTrack(sleeves.getPath(partNum)))
                chestTracks.append(getChestTrack(hands.getPath(partNum)))

            allChestTracks.append(chestTracks)

    damageAnims = [['neutral',
                    0.01,
                    0.01,
                    0.5], ['juggle',
                           0.01,
                           0.01,
                           1.48], ['think', 0.01, 2.28]]
    dodgeAnims = []
    dodgeAnims.append(['think',
                       0.01,
                       0,
                       0.6])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.01,
                               dodgeAnimNames=['duck'], showDamageExtraTime=2.1, showMissedExtraTime=2.0)
    return Parallel(suitTrack, partTracks, toonTracks2, toonTracks, allHeadTracks, allChestTracks)

def clearCorporateRestructuringTraps(battle):
    for suit in battle.activeSuits:
        suit.battleTrap = NO_TRAP
        suit.battleTrapIsFresh = 0

        if suit.hasSuitStatusEffect('trapped'):
            suit.clearSuitStatusEffect('trapped')

def doPlacesEveryone(attack):
    suit = attack['suit']
    battle = attack['battle']
    oldActiveSuits = battle.activeSuits[:]
    if len(oldActiveSuits) < 2:
        return Sequence(getSuitAnimTrack(attack))
    payload = int(attack.get('hp', 0))
    oldIndexes = []
    for index in xrange(len(oldActiveSuits)):
        oldIndexes.append((payload >> (index * 3)) & 7)
    if sorted(oldIndexes) != range(len(oldActiveSuits)):
        return Sequence(getSuitAnimTrack(attack))
    newActiveSuits = [oldActiveSuits[index] for index in oldIndexes]
    suitTrack = Sequence(Func(suit.stop), getSuitAnimTrack(attack))
    suitTracks = Parallel()
    for otherSuit in oldActiveSuits:
        pendingDeath = False
        if hasattr(otherSuit, 'getPendingQueuedDeath'):
            pendingDeath = otherSuit.getPendingQueuedDeath()
        if getattr(otherSuit, 'isDead', False) or pendingDeath:
            continue
        newPos, newHpr = battle.getActorPosHpr(otherSuit, newActiveSuits)
        if otherSuit.isLured:
            newPos.setY(newPos.getY() - MovieUtil.SUIT_LURE_DISTANCE)
        startPos = otherSuit.getPos(battle)
        startHpr = otherSuit.getHpr(battle)
        if otherSuit == suit:
            if oldActiveSuits.index(otherSuit) != newActiveSuits.index(otherSuit):
                lookNode = battle.attachNewNode('corporate-restructuring-look')
                lookNode.setPos(startPos)
                lookNode.lookAt(newPos)
                turnHpr = lookNode.getHpr(battle)
                lookNode.removeNode()
                suitTrack = Sequence(
            Parallel(suitTrack,
                LerpPosInterval(otherSuit, otherSuit.getDuration('song-and-dance') - 1, newPos, startPos=startPos, other=battle, blendType='easeInOut'),
                LerpHprInterval(otherSuit, 1, newHpr, startHpr=startHpr, other=battle, blendType='easeInOut')),
            Func(otherSuit.setPosHpr, battle, newPos, newHpr))
            else:
                suitTrack = Parallel(suitTrack, Sequence(
                    Wait(1.5),
                    Func(otherSuit.setPosHpr, battle, newPos, newHpr)))
            continue
        floatOffset = Point3(0, 0, 0)
        raisedStart = startPos + floatOffset
        raisedEnd = newPos + floatOffset
        suitType = getSuitBodyType(otherSuit.getStyleName())
        flailFrame = 16 if suitType == 'a' else 15
        animTrack = Sequence(
            Func(otherSuit.stop),
            ActorInterval(otherSuit, 'song-and-dance'),
            Func(otherSuit.setNeutralAnimationDrop))
        moveTrack = Sequence(
            Parallel(
                LerpPosInterval(otherSuit, otherSuit.getDuration('song-and-dance') - 1, newPos, startPos=startPos, other=battle, blendType='easeInOut'),
                LerpHprInterval(otherSuit, 1, newHpr, startHpr=startHpr, other=battle, blendType='easeInOut')),
            Func(otherSuit.setPosHpr, battle, newPos, newHpr))
        suitTracks.append(Parallel(animTrack, moveTrack))
    quakeSound = globalBattleSoundCache.getSound('AA_heal_happydance.ogg')
    soundTrack = Sequence(Func(quakeSound.stop), SoundInterval(quakeSound, node=suit))
    return Sequence(
        Parallel(suitTrack, soundTrack, Sequence(suitTracks)),
        Func(battle.setClientSuitOrder, newActiveSuits))

def doBackToOnes(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    healTracks = Parallel()

    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)

    sprayTrack = Sequence(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)), __getPartTrack(sprayEffect, 0.0, 5.0, [sprayEffect, suit, 0], softStop=-3.5))

    can = loader.loadModel('phase_5/models/props/megaphone')

    suitTrack = Sequence(getSuitAnimTrack(attack))

    suitTrack2 = Sequence(ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimationDrop))

    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]

    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(0.5), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))

    # =========================================================
    # GROUP TARGET HEALING
    # =========================================================
    for targetData in targets:
        if 'suit' not in targetData:
            continue

        targetSuit = targetData['suit']
        heal = int(targetData.get('heal', 0))

        if heal <= 0:
            continue

        healTrack = Sequence(Wait(2.0), Parallel(Func(targetSuit.showHpTextNew, heal, text='BACK TO ONES!', colorCode=1), Func(targetSuit.setHealthForMe, heal), Func(targetSuit.updateHealthBar, 0)))

        healTracks.append(healTrack)

    soundTrack = getSoundTrack('LB_toonup.ogg', delay=2.0, node=suit)

    return Parallel(suitTrack, soundTrack, throwTrack, suitTrack2, healTracks, sprayTrack)

def doAction(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 5.0, [sprayEffect, suit, 0], softStop=-3.5))
    can = loader.loadModel('phase_5/models/props/megaphone')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimationDrop))
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(0.5), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    return Parallel(suitTrack, throwTrack, suitTrack2, sprayTrack)

def doActionCog(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    targetData = targets[0]

    if 'suit' not in targetData:
        return Sequence()

    targetSuit = targetData['suit']

    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)

    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 5.0, [sprayEffect, suit, 0], softStop=-3.5))

    can = loader.loadModel('phase_5/models/props/megaphone')

    suitTrack = Sequence(getSuitAnimTrack(attack), Func(targetSuit.setSuitStatusEffect, 'directorAction', modifier=1, turns=2))

    suitTrack2 = Sequence(ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimationDrop), Wait(2.0))

    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]

    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(0.5), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))

    return Parallel(suitTrack, throwTrack, suitTrack2, sprayTrack)

def doActionPartner(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 5.0, [sprayEffect, suit, 0], softStop=-3.5))
    can = loader.loadModel('phase_5/models/props/megaphone')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimationDrop))
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(0.5), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    notifyTrack = Sequence(Wait(2.0), ActorInterval(toon, 'confused'))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'actionPartner', turns=2)))
    return Parallel(suitTrack, notifyTrack, throwTrack, suitTrack2, sprayTrack)

def createMiniStagelightTrack(
        targetSuit,
        initialDelay=0.0,
        steadyLightDuration=1.5,
        postFlickerFallDelay=0.15):

    """
    Creates a standalone stagelight animation for a Suit.

    Sequence:
        1. Stagelight appears above targetSuit.
        2. Light remains steadily on.
        3. Light flickers.
        4. Spotlight shuts off.
        5. Stagelight falls onto the Suit's head.
        6. Particles play.
        7. Stagelight falls away and cleans itself up.

    No Toon, attack, HP, damage, death, or battle target data is required.
    """

    # ------------------------------------------------------------------
    # Position and scale
    # ------------------------------------------------------------------

    stagelightZOffset = 20.0
    stagelightScale = 1.25

    stagelightFallOffset = Vec3(
        12,
        12,
        -15
    )

    stagelightSpinOffset = Vec3(
        90,
        90,
        90
    )

    spotlightAlpha = 0.7

    # ------------------------------------------------------------------
    # Timing
    # ------------------------------------------------------------------

    stagelightGrowDelay = 0.08
    stagelightGrowDuration = 0.02

    stagelightFallDuration = 0.15
    stagelightHoldDuration = 1.0

    stagelightShrinkProjectileDuration = 1.35
    stagelightShrinkDuration = 0.40

    stagelightFlickerDuration = 0.05

    glassBreakDuration = 0.40

    # Each tuple is:
    # (time relative to flicker start, alpha after flicker)
    stagelightFlickers = [
        (0.0, 0.6),
        (0.4, 0.2),
        (0.6, 0.7),
        (0.8, 0.4),
        (0.9, 0.7),
        (1.1, 0.2),
        (1.2, 0.0),
    ]

    # ------------------------------------------------------------------
    # Load stagelight prop
    # ------------------------------------------------------------------

    stagelight = globalPropPool.getProp(
        'stagelight'
    )

    stagelight.hide()
    stagelight.reparentTo(render)

    stagelightNode = stagelight.node()

    stagelightNode.setBounds(
        OmniBoundingVolume()
    )

    stagelightNode.setFinal(1)

    spotlight = stagelight.find(
        '**/spotlight'
    )

    if not spotlight.isEmpty():
        spotlight.setColorScale(
            1.0,
            1.0,
            1.0,
            spotlightAlpha
        )

        spotlight.show()

    hiddenHeadParts = []

    # ------------------------------------------------------------------
    # Position helpers
    # ------------------------------------------------------------------

    def getSuitHeadPoint(
            targetSuit=targetSuit):

        headJoint = targetSuit.find(
            '**/joint_head'
        )

        if not headJoint.isEmpty():
            return headJoint.getPos(render)

        try:
            suitHeight = targetSuit.getHeight()
        except:
            suitHeight = 5.0

        return (
            targetSuit.getPos(render)
            + Vec3(0, 0, suitHeight)
        )

    def positionStagelight(
            stagelight=stagelight,
            targetSuit=targetSuit):

        stagelight.reparentTo(render)

        stagelight.setPos(
            targetSuit.getPos(render)
            + Vec3(
                0,
                0,
                stagelightZOffset
            )
        )

        stagelight.setHpr(
            render,
            Vec3(0, 0, 0)
        )

        stagelight.setScale(
            MovieUtil.PNT3_NEARZERO
        )

    def attachStagelight(
            stagelight=stagelight,
            targetSuit=targetSuit,
            hiddenHeadParts=hiddenHeadParts):

        headJoint = targetSuit.find(
            '**/joint_head'
        )

        if not headJoint.isEmpty():
            stagelight.wrtReparentTo(
                headJoint
            )
        else:
            stagelight.wrtReparentTo(
                targetSuit
            )

        stagelight.setPos(
            0,
            0,
            0
        )

        stagelight.setHpr(
            0,
            0,
            0
        )

        stagelight.setScale(
            stagelightScale
        )

        # Prevent the Suit's inherited color scale
        # from affecting the stagelight.
        stagelight.setColorScaleOff(1)

        try:
            headParts = targetSuit.getHeadParts()
        except:
            headParts = []

        for part in headParts:
            if part is None:
                continue

            if part.isEmpty():
                continue

            if not part.isHidden():
                part.hide()
                hiddenHeadParts.append(part)

    def detachStagelight(
            stagelight=stagelight,
            hiddenHeadParts=hiddenHeadParts):

        stagelight.wrtReparentTo(render)

        for part in hiddenHeadParts:
            if part is None:
                continue

            if not part.isEmpty():
                part.show()

        hiddenHeadParts[:] = []

    def cleanupStagelight(
            stagelight=stagelight,
            hiddenHeadParts=hiddenHeadParts):

        # Always restore hidden head parts, even if the interval
        # ended or was interrupted unexpectedly.
        for part in hiddenHeadParts:
            if part is None:
                continue

            if not part.isEmpty():
                part.show()

        hiddenHeadParts[:] = []

        if (
            stagelight is not None
            and not stagelight.isEmpty()
        ):
            MovieUtil.removeProp(
                stagelight
            )

    # ------------------------------------------------------------------
    # Flicker track
    # ------------------------------------------------------------------

    flickerTrack = Sequence()

    previousFlickerTime = 0.0

    for flickerIndex, flickerData in enumerate(
            stagelightFlickers):

        flickerTime = flickerData[0]
        flickerAlpha = flickerData[1]

        waitTime = (
            flickerTime
            - previousFlickerTime
        )

        if waitTime > 0:
            flickerTrack.append(
                Wait(waitTime)
            )

        isLastFlicker = (
            flickerIndex
            == len(stagelightFlickers) - 1
        )

        currentFlicker = Sequence(
            Func(
                spotlight.hide
            ),

            Wait(
                stagelightFlickerDuration
            )
        )

        if not isLastFlicker:
            currentFlicker.append(
                Func(
                    spotlight.show
                )
            )

            currentFlicker.append(
                Func(
                    spotlight.setColorScale,
                    1.0,
                    1.0,
                    1.0,
                    flickerAlpha
                )
            )

        flickerTrack.append(
            currentFlicker
        )

        previousFlickerTime = flickerTime

    # Guarantee that the light stays off before impact.
    flickerTrack.append(
        Func(
            spotlight.hide
        )
    )

    # ------------------------------------------------------------------
    # Calculate exact impact time for particles
    # ------------------------------------------------------------------

    flickerTrackDuration = (
        stagelightFlickers[-1][0]
        + stagelightFlickerDuration
    )

    impactDelay = (
        stagelightGrowDelay
        + stagelightGrowDuration
        + steadyLightDuration
        + flickerTrackDuration
        + postFlickerFallDelay
        + stagelightFallDuration
    )

    # ------------------------------------------------------------------
    # Particle effects
    # ------------------------------------------------------------------

    BattleParticles.loadParticles()

    electricityEffect = (
        BattleParticles.loadParticleFile(
            'stagelightGagZap.ptf'
        )
    )

    glassBreakEffect = (
        BattleParticles.createParticleEffect(
            file='stagelightGagBreak'
        )
    )

    BattleParticles.setEffectTexture(
        glassBreakEffect,
        'snow-particle'
    )

    particleTrack = Sequence(
        Wait(
            impactDelay
        ),

        Parallel(
            getPartTrackLightning(
                particleEffect=glassBreakEffect,
                startDelay=0.0,
                durationDelay=glassBreakDuration,
                partExtraArgs=[
                    glassBreakEffect,
                    stagelight,
                    0
                ],
                renderParent=render
            ),

            getPartTrackLightning(
                particleEffect=electricityEffect,
                startDelay=0.0,
                durationDelay=(
                    stagelightHoldDuration
                    + stagelightShrinkDuration
                ),
                partExtraArgs=[
                    electricityEffect,
                    stagelight,
                    0
                ],
                softStop=(
                    -stagelightShrinkDuration
                ),
                renderParent=render
            )
        )
    )

    # ------------------------------------------------------------------
    # Complete stagelight movement
    # ------------------------------------------------------------------

    movementTrack = Sequence(
    Func(positionStagelight),
    Wait(stagelightGrowDelay),
    Func(stagelight.show),
    LerpScaleInterval(stagelight, stagelightGrowDuration, startScale=MovieUtil.PNT3_NEARZERO, scale=stagelightScale, other=render, blendType='easeIn'),
    Wait(steadyLightDuration),
    flickerTrack,
    Wait(postFlickerFallDelay),

    # First impact.
    Parallel(LerpScaleInterval(stagelight, stagelightFallDuration, startScale=1, scale=2.5, blendType='easeIn'),
                 LerpPosInterval(stagelight, stagelightFallDuration, lambda: getSuitHeadPoint() + Vec3(0, 0, 0.5), other=render, blendType='easeIn')),

    # Big rebound.
    Parallel(
        LerpPosInterval(stagelight, 0.12, lambda: getSuitHeadPoint() + Vec3(0, 0, 2.0), other=render, blendType='easeOut'),
        LerpHprInterval(stagelight, 0.12, Vec3(0, 0, 0), blendType='easeOut')
    ),

    # Second impact.
    Parallel(
        LerpPosInterval(stagelight, 0.10, lambda: getSuitHeadPoint() + Vec3(0, 0, 0.5), other=render, blendType='easeIn'),
        LerpHprInterval(stagelight, 0.10, Vec3(0, 0, 0), blendType='easeIn')
    ),

    # Smaller rebound.
    Parallel(
        LerpPosInterval(stagelight, 0.09, lambda: getSuitHeadPoint() + Vec3(0, 0, 1.0), other=render, blendType='easeOut'),
        LerpHprInterval(stagelight, 0.09, Vec3(0, 0, 0), blendType='easeOut')
    ),

    # Final impact.
    Parallel(
        LerpPosInterval(stagelight, 0.08, lambda: getSuitHeadPoint() + Vec3(0, 0, 0.5), other=render, blendType='easeIn'),
        LerpHprInterval(stagelight, 0.08, Vec3(0, 0, 0), blendType='easeIn')
    ),

    Wait(0.15),

    # Existing fall-away.
    Parallel(
        ProjectileInterval(stagelight, duration=stagelightShrinkProjectileDuration, endPos=lambda: getSuitHeadPoint() + stagelightFallOffset),
        LerpHprInterval(stagelight, stagelightShrinkDuration, stagelightSpinOffset),
        LerpScaleInterval(stagelight, stagelightShrinkDuration, startScale=2.5, scale=MovieUtil.PNT3_NEARZERO, blendType='easeIn')
    )
)
    

    # ------------------------------------------------------------------
    # Final combined track
    # ------------------------------------------------------------------

    return Sequence(
        Wait(
            initialDelay
        ),

        Parallel(
            movementTrack,
            particleTrack
        ),

        Func(
            cleanupStagelight
        )
    )

def createBouncingStagelightTrack(targetSuit, battle, steadyLightDuration=2.0):
    stagelight = globalPropPool.getProp(
        'stagelight'
    )

    targetPos = targetSuit.getPos(render)

    startPos = Point3(targetPos)
    startPos.setZ(startPos.getZ() + 30)

    landPos = Point3(targetPos)
    landPos.setZ(landPos.getZ())

    bouncePos = Point3(landPos)
    bouncePos.setZ(bouncePos.getZ() + 1)

    smallBouncePos = Point3(landPos)
    smallBouncePos.setZ(smallBouncePos.getZ() + 0.5)

    stagelight.setPos(startPos)
    stagelight.setScale(2.5)

    return Sequence(
        Func(battle.movie.needRestoreRenderProp, stagelight),
        Func(stagelight.reparentTo, render),

        Func(stagelight.setColorScale, 1, 1, 1, 1),
        Wait(0.08),
        Func(stagelight.setColorScale, 1, 1, 1, 0.15),
        Wait(0.06),
        Func(stagelight.setColorScale, 1, 1, 1, 1),
        Wait(0.10),
        Func(stagelight.setColorScale, 1, 1, 1, 0.25),
        Wait(0.07),
        Func(stagelight.setColorScale, 1, 1, 1, 1),
        Wait(0.12),
        Func(stagelight.setColorScale, 1, 1, 1, 0),

        Wait(0.15),

        Parallel(LerpScaleInterval(stagelight, 0.45, startScale=1, scale=3, blendType='easeIn'),
                 LerpPosInterval(stagelight, 0.45, landPos, startPos=startPos, blendType='easeIn')),

        Parallel(
            LerpPosInterval(stagelight, 0.14, bouncePos, blendType='easeOut'),
            LerpHprInterval(stagelight, 0.14, Vec3(0, 0, 0), blendType='easeOut')
        ),

        Parallel(
            LerpPosInterval(stagelight, 0.12, landPos, blendType='easeIn'),
            LerpHprInterval(stagelight, 0.12, Vec3(0, 0, 0), blendType='easeIn')
        ),

        Parallel(
            LerpPosInterval(stagelight, 0.09, smallBouncePos, blendType='easeOut'),
            LerpHprInterval(stagelight, 0.09, Vec3(0, 0, 0), blendType='easeOut')
        ),

        Parallel(
            LerpPosInterval(stagelight, 0.08, landPos, blendType='easeIn'),
            LerpHprInterval(stagelight, 0.08, Vec3(0, 0, 0), blendType='easeIn')
        ),

        Func(stagelight.wrtReparentTo, targetSuit),
        Wait(steadyLightDuration),
        Func(stagelight.removeNode)
    )

def createSignalLostTextureRandomizer(headPart, textureA, textureB, finalTexture):
    track = Sequence()

    tickSound = globalBattleSoundCache.getSound('MG_sfx_travel_game_red_arrow.ogg')

    for i in xrange(10):
        track.append(Func(headPart.setTexture, textureA, 1))
        track.append(Func(tickSound.play))
        track.append(Wait(0.175))

        track.append(Func(headPart.setTexture, textureB, 1))
        track.append(Func(tickSound.play))
        track.append(Wait(0.175))

    track.append(Func(headPart.setTexture, finalTexture, 1))
    track.append(Func(tickSound.play))
    track.append(Wait(1.0))

    return track

def doSignalLost(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    name = attack['name']

    if not targets:
        return Sequence()

    headTracks = Sequence()

    textureA = loader.loadTexture('phase_9/maps/ttcc_ene_videographer_cogs.png')
    textureB = loader.loadTexture('phase_9/maps/ttcc_ene_videographer_toons.png')
    if name == 'VideographerStagelightsCogs':
        finalTexture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer_cogs.png')
    elif name == 'VideographerStagelightsToons':
        finalTexture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer_toons.png')
    textureOriginal = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')

    for headPart in suit.animatedHeadParts:
        randomizerTrack = createSignalLostTextureRandomizer(headPart, textureA, textureB, finalTexture)

        headTrack = Sequence(
            Func(suit.pauseHeadFreakout),
            Wait(1.0),
            Func(headPart.loop, 'stun'),
            randomizerTrack,
            Func(headPart.loop, 'neutral'), Func(headPart.setTexture, textureOriginal, 1),
            Func(suit.resumeHeadFreakout)
        )

        headTracks.append(headTrack)

    suitAnimTrack = Sequence(getSuitAnimTrack(attack))
    if name == 'VideographerStagelightsCogs':
        headTracks.append(doStagelightsCogs(attack))
    elif name == 'VideographerStagelightsToons':
        headTracks.append(doStagelightsToons(attack))

    return Parallel(suitAnimTrack, headTracks)

def doStagelightsCogs(attack):
    manager = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    managerTrack = Sequence(ActorInterval(manager, 'snap'), Func(manager.setNeutralAnimationDrop))
    targetTracks = Parallel()
    stagelightTracks = Parallel()
    notifyTracks = Parallel()
    soundTrack2 = getSoundTrack('SA_bash.ogg', node=manager)
    soundTrack = getSoundTrack('AA_zap_stagelight_hit.ogg', delay=1, node=manager)
    taunt = random.choice(
        ["CUT THE LIGHTS! CUT THE LIGHTS!",
         "That's my crew you're crushing!",
         "Who wired this set?!",
         "Someone get this signal under control!!"])
    tauntInterval = Sequence(Func(manager.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    for target in targets:
        targetSuit = target['suit']
        hp = target.get('hp', 0)
        died = target.get('died', 0)
        revived = target.get('revived', 0)

        notifyTrack = Sequence(Wait(3.0),
        Parallel(
            Func(targetSuit.showHpTextNew, -hp),
            Func(targetSuit.setHealthForMe, -hp),
            Func(targetSuit.updateHealthBar, 0),
        ),
    )
        if died and not targetSuit.dna.name == 'videog':
            notifyTrack.append(Parallel(ActorInterval(targetSuit, 'flatten', duration=.55), MovieUtil.createSuitCrashTrack(targetSuit, battle, 7)))
            notifyTrack.append(Func(targetSuit.makeDead))
        else:
            notifyTrack.append(Sequence(
                ActorInterval(targetSuit, 'flatten'),
                Func(targetSuit.setNeutralAnimationDrop)
            ))

        stagelightTrack = Sequence(
            createMiniStagelightTrack(targetSuit, steadyLightDuration=1.0)
        )

        stagelightTracks.append(stagelightTrack)
        notifyTracks.append(notifyTrack)

    return Parallel(managerTrack, tauntInterval, notifyTracks, soundTrack, soundTrack2, targetTracks, stagelightTracks)

def doStagelightsToons(attack):
    manager = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    managerTrack = Sequence(ActorInterval(manager, 'snap'), Func(manager.setNeutralAnimationDrop))
    toonTracks = Parallel()
    stagelightTracks = Parallel()
    soundTracks = Parallel()

    taunt = random.choice(("Looks like the spotlight still knows its mark!", "See? Everything's under control!", "Right where I would've put them!", "The show goes on!"))
    tauntInterval = Sequence(Func(manager.setChatAbsolute, taunt, CFSpeech | CFTimeout))

    for target in targets:
        toon = target['toon']
        dmg = target.get('hp', 0)
        died = target.get('died', 0)

        if dmg <= 0:
            continue

        stagelightTrack = Sequence(
            createMiniStagelightTrack(toon, steadyLightDuration=1.0)
        )

        toonTrack = Sequence(
            Wait(3.0),

            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, -dmg, openEnded=0),
                Func(__doDamage, toon, dmg, died)
            ),

            Wait(1.75),

            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),

                getSoundTrack('toon_decompress.ogg', node=toon),

                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )

        stagelightTracks.append(stagelightTrack)
        toonTracks.append(toonTrack)

    hitSound = getSoundTrack('AA_zap_stagelight_hit.ogg', delay=1, node=manager)
    bashSound = getSoundTrack('SA_bash.ogg', node=manager)

    return Parallel(managerTrack, tauntInterval, toonTracks, stagelightTracks, hitSound, bashSound)

def getPartTrackLightning(particleEffect, startDelay, durationDelay, partExtraArgs, softStop=0, renderParent=render):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop, renderParent=renderParent))

def doChoreography(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = getSuitAnimTrackAttack(attack)
    toonTracks = Sequence(getToonTracks(attack, 4.1, ['cringe'], 4.1, ['victory']))
    soundTrack = getSoundTrack('AA_heal_happydance.ogg', delay=.01, node=suit)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            toonTracks.append(Parallel(Func(toon.setToonStatusEffect, 'vulnerable', modifier=25, turns=3)))
    return Parallel(suitTrack, soundTrack, toonTracks)

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
        elif suit.style.name == 'cbutcher':
            color = Point4((0, 0, 0, 1))
        else:
            color = Point4(1.0, 1.0, 1.0, 1.0)
    else:
        color = SoakColor
    suitInterval = Parallel()
    actorNode = suit.find('**/__Actor_modelRoot')
    actorCollection = actorNode.findAllMatches('*')
    parts = ()
    texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
    for thingIndex in xrange(0, actorCollection.getNumPaths()):
        thing = actorCollection[thingIndex]
        if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
            if suit.dna.name != 'cbutcher' and not suit.isShadow:
                suitInterval.append(Func(thing.setColor, Point4(1.0, 1.0, 1.0, 1.0)))
    if not suit.isSkeleton and not suit.isShadow:
        hands = suit.find('**/hands')
        handTint = Vec4(
            suit.handColor[0] * color[0],
            suit.handColor[1] * color[1],
            suit.handColor[2] * color[2],
            suit.handColor[3] * color[3]
        )
        suitInterval.append(Func(hands.setColorScale, suit.handColor))
    if suit.dna.name == 'lgator' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryLitigator))
    if suit.dna.name == 'treasure' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryTreasurer))
    if suit.style.name == 'safesupervis' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryFirestarter))
    if suit.style.name == 'fires' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryFirestarter))
    return suitInterval

def doInFocus(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    can = loader.loadModel('phase_3.5/models/accessories/social/newstoon_camera')
    suitTrack = Sequence(getSuitTrack(attack))
    posPoints = [Point3(-0.25, -.25, 1), VBase3(-90, 0, 0)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=1.0), Wait(suit.getDuration('glower') - 1.5), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    toonTrack = getToonTrackCheat(attack, 1.0, ['angry'], 1, ['angry'])
    notifyTrack = Sequence(Wait(1.0), Func(toon.showHpTextNew, -int(dmg), text="FOCUSED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'noDodge', turns=2)))
    oldcolor = render.getColorScale()
    soundTrack2 = getSoundTrack('Photo_zoom.ogg', delay=1.0, node=suit)
    return Parallel(suitTrack, toonTrack, soundTrack2, notifyTrack, throwTrack)

def doCaughtOnCamera(attack):
    suit = attack['suit']
    can = loader.loadModel('phase_3.5/models/accessories/social/newstoon_camera')
    suitTrack = Sequence(getSuitTrack(attack))
    posPoints = [Point3(-0.25, -.25, 1), VBase3(-90, 0, 0)]
    sparkle = globalPropPool.getProp('smile')
    sparkle.setScale(5.0)
    sparkle.setTwoSided(True)
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=1.0), Wait(suit.getDuration('glower') - 1.5), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    sparklePosPoints = [Point3(3, -8, -7), VBase3(180, 40, 0)]
    sparklePropTrack = Sequence(Wait(1.0))
    sparklePropTrack.append(Func(__showProp, sparkle, suit.getRightHand(), sparklePosPoints[0], sparklePosPoints[1]))
    sparklePropTrack.append(Func(sparkle.find('**/scale_joint_sign').hide))
    sparklePropTrack.append(ActorInterval(sparkle, 'smile', startFrame=39))
    sparklePropTrack.append(Func(MovieUtil.removeProp, sparkle))
    soundTrack2 = getSoundTrack('Photo_shutter.ogg', delay=1.0, node=suit)
    return Parallel(suitTrack, sparklePropTrack, soundTrack2, throwTrack)

def doCameraFlash(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sparkle = globalPropPool.getProp('smile')
    sparkle.setScale(5.0)
    sparkle.setTwoSided(True)
    can = loader.loadModel('phase_3.5/models/accessories/social/newstoon_camera')
    suitTrack = Sequence(getSuitTrack(attack))
    sparklePosPoints = [Point3(3, -8, -7), VBase3(180, 40, 0)]
    sparklePropTrack = Sequence(Wait(1.0))
    sparklePropTrack.append(Func(__showProp, sparkle, suit.getRightHand(), sparklePosPoints[0], sparklePosPoints[1]))
    sparklePropTrack.append(Func(sparkle.find('**/scale_joint_sign').hide))
    sparklePropTrack.append(ActorInterval(sparkle, 'smile', startFrame=39))
    sparklePropTrack.append(Func(MovieUtil.removeProp, sparkle))
    posPoints = [Point3(-0.25, -.25, 1), VBase3(-90, 0, 0)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=1.0), Wait(suit.getDuration('glower') - 1.5), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    toonTrack = getToonTrackCheat(attack, 1.0, ['conked'], 0, ['duck'])
    notifyTrack = Sequence(Wait(1.0), Func(toon.showHpTextNew, -int(dmg), text="FLASHED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'confused', turns=2)))
    oldcolor = render.getColorScale()
    soundTrack2 = getSoundTrack('Photo_shutter.ogg', delay=1.0, node=suit)
    lightingTrack = Sequence(Wait(1), LerpColorScaleInterval(render, 0.5, (0, 0, 0, 0)),
                             LerpColorScaleInterval(render, 1, (oldcolor)))
    return Parallel(suitTrack, toonTrack, sparklePropTrack, lightingTrack, soundTrack2, notifyTrack, throwTrack)

def doWrappedInTheFilm(attack):
    suit = attack['suit']
    targets = attack['target']
    tape = globalPropPool.getProp('redtape')
    tape.setColor(0.129, 0, 0.329, 1)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    tubes = []
    tapePosPoints = [Point3(-0.21707670043415206, 0.04341534008683112, -0.390738060781473), VBase3(0, 90, 90)]
    tapeScaleUpPoint = Point3(.9, .9, .9)
    propTracks = Parallel()
    toonTracks = Parallel()
    allTubeTracks = Parallel()
    notifyTracks = Parallel()
    battle = attack['battle']
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tape.setColor(0, 0, 0, 1)
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))
            tubes[i].setColor(0, 0, 0, 1)

        propTrack = Sequence(getPropAppearTrack(tape, suit.getRightHand(), tapePosPoints, 0.25, tapeScaleUpPoint, scaleUpTime=0.25))
        propTrack.append(Wait(1.55))
        hitPoint = lambda toon=toon: __toonTorsoPoint(toon)
        propTrack.append(getPropThrowTrack(attack, tape, [hitPoint], [__toonGroundPoint(attack, toon, 0)], .25, target=t))
        propTracks.append(propTrack)
        hips = toon.getHipsParts()
        animal = toon.style.getAnimal()
        scale = ToontownGlobals.toonBodyScales[animal]
        legs = toon.style.legs
        torso = toon.style.torso
        torso = torso[0]
        animal = animal[0]
        tubeHeight = -0.8
        if torso == 's':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'm':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'l':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 1.11)
        if animal == 'h' or animal == 'd':
            tubeHeight = -0.87
            scaleUpPoint = Point3(scale * 1.69, scale * 1.69, scale * 0.67)
        tubePosPoints = [Point3(0, 0, tubeHeight), MovieUtil.PNT3_ZERO]
        tubeTracks = Parallel()
        tubeTracks.append(Func(battle.movie.needRestoreHips))
        for partNum in xrange(0, hips.getNumPaths()):
            nextPart = hips.getPath(partNum)
            tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 2.2, 3.17, scaleUpPoint=scaleUpPoint))

        tubeTracks.append(Func(battle.movie.clearRestoreHips))
        notifyTracks.append(Sequence(Wait(2.4), Func(toon.showHpString, "WRAPPED!", 10)))
        allTubeTracks.append(tubeTracks)
        toonTracks.append(Sequence(Wait(2.4), Func(toon.setToonStatusEffect, 'wrapped', turns=3), ActorInterval(toon, 'struggle')))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.4, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack, allTubeTracks, notifyTracks)

def doCameraRewind(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    suitTracks = Parallel()
    knifeTracks = Parallel()

    tapePosPoints = [Point3(-0.21707670043415206, 0.04341534008683112, -0.390738060781473), VBase3(0, 90, 90)]
    tapeScaleUpPoint = Point3(.9, .9, .9)

    for targetData in targets:
        if 'suit' not in targetData:
            continue

        targetSuit = targetData['suit']
        heal = int(targetData.get('heal', 0))

        if targetSuit.dna.name not in ('director', 'fmaker', 'cinema', 'choreo'):
            continue

        # =========================================================
        # TARGET EFFECT
        # =========================================================
        targetTrack = Sequence(Wait(4.5))

        if heal > 0:
            targetTrack.append(Parallel(Func(targetSuit.showHpTextNew, heal), Func(targetSuit.setHealthForMe, heal), Func(targetSuit.updateHealthBar, 0)))

            if targetSuit.dna.name in ('director', 'cinema', 'choreo'):
                targetTrack.append(Func(targetSuit.checkHealingPhrases, 0))

        else:
            targetTrack.append(Func(targetSuit.showHpTextNew, 0, text="+10% Damage!", colorCode=1))
            targetTrack.append(Func(targetSuit.setSuitStatusEffect, 'damageUp', modifier=10, mode='refreshModifier'))
            targetTrack.append(Func(targetSuit.updateHealthBar, 0))

        suitTracks.append(targetTrack)

        # =========================================================
        # TAPE PROP
        # =========================================================
        can = globalPropPool.getProp('redtape')
        can.setColor(0, 0, 0, 1)
        can.setP(90)

        knifeTrack = Sequence(
            getPropAppearTrack(can, theSuit.getRightHand(), tapePosPoints, .5, tapeScaleUpPoint, scaleUpTime=0.1),
            Wait(1.5),
            Parallel(getThrowTrack(can, (0, 0, targetSuit.getHeight() + 2.5), 1.5, targetSuit, -20.288), LerpHprInterval(can, 1.0, VBase3(0, 0, 0))),
            Wait(0.15),
            Parallel(LerpPosInterval(can, 0.45, (0, 0, targetSuit.getHeight() - 2.5), other=targetSuit, blendType='easeIn'), LerpScaleInterval(can, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')),
            Parallel(LerpScaleInterval(can, 0.2, VBase3(0.01, 0.01, 0.01)), LerpColorScaleInterval(can, 0.2, Vec4(1, 1, 1, 0))),
            Func(can.removeNode)
        )

        knifeTracks.append(knifeTrack)

    suitTrackAnim = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4.5, node=theSuit)

    return Parallel(suitTrackAnim, suitTracks, soundTrack, knifeTracks)

def doAttackRewind(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Parallel(getSuitAnimTrackAttack(attack))
    propTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_tv.png')
        gavel = loader.loadModel('phase_14/models/char/ttcc_ene_multislacker-zero')
        gavel.setTexture(texture, 1)
        gavel.setP(-90)
        gavel.setH(180)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        toonPos = toon.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y + 2, 30)
        gavelPos2 = Point3(toonPos.getX(), y - 5, 30)
        propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(180, -90, 0)], appearDelay=0.0,
                           scaleUpPoint=Point3(2), scaleUpTime=1.5),
        LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y + 2, 1)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 2)),
        LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 1)), Sequence(
            Wait(1.5),
            LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
        ))
        propTrack2 = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos2, VBase3(180, -90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2), scaleUpTime=1.5),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y - 5, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y - 5, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y - 5, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        toonTrack = Sequence(
        Wait(1.75),
        Parallel(
            Func(toon.enterFlattened),
            Func(toon.showHpText, -dmg, openEnded=0),
            Func(__doDamage, toon, dmg, t['died'])
        ),
        Wait(1.75),
        Parallel(
            Sequence(
                Wait(.5),
                Func(toon.exitFlattened)
            ),
            getSoundTrack('toon_decompress.ogg', node=toon),
            Sequence(
                ActorInterval(toon, 'jump'),
                Func(toon.loop, 'neutral')
            )
        )
        )
        toonTrack2 = Sequence(
            Wait(1.75),
            Parallel(
                Func(MovieUtil.indicateMissed, toon, 2.0),
            ))

        soundTrack2 = getSoundTrack('SA_bash.ogg', node=suit)
        soundTrack = getSoundTrack('SA_TV_crash.ogg', delay=1.5, node=suit)
        if dmg > 0:
            toonTracks.append(toonTrack)
            soundTracks.append(soundTrack)
            propTracks.append(propTrack)
            smokeTracks.append(smokeTrack)
        else:
            toonTracks.append(toonTrack2)
            soundTracks.append(soundTrack)
            propTracks.append(propTrack2)
    return Parallel(suitTrack, toonTracks, smokeTracks, soundTrack2, soundTracks, propTracks)

def doPhase3Videographer(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    hollywoods = []
    puddleTracks = Parallel()
    moveTracks = Parallel()
    managerHealTracks = Parallel()
    animTracks = Parallel()
    propTracks = Parallel()
    selfDamageTracks = Parallel()
    smokeTracks = Parallel()
    suitDeathTracks = Parallel()
    for suit in battle.activeSuits:
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        suitTrack2 = Sequence(Wait(2), Parallel(ActorInterval(suit, 'flatten', duration=.55),
                                               MovieUtil.createSuitCrashTrack(suit, battle, 7)))
        selfDamageTrack = Sequence(Wait(2),
                Func(suit.showHpText, - suit.currHP),
                                   Func(suit.setHealthForMe, - suit.currHP),
                                   Func(suit.updateHealthBar, 0))
        smokeTrack = Sequence(Wait(2.0), Func(smoke.reparentTo, suit),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_tv.png')
        gavel = loader.loadModel('phase_14/models/char/ttcc_ene_multislacker-zero')
        gavel.setTexture(texture, 1)
        gavel.setP(-90)
        gavel.setH(180)
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y + 2, 30)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(180, -90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2.5), scaleUpTime=2.0),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y + 2, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        if suit.dna.name not in ('hroller2', 'videog', 'hroller'):
            selfDamageTracks.append(selfDamageTrack)
            smokeTracks.append(smokeTrack)
            propTracks.append(propTrack)
            suitDeathTracks.append(suitTrack2)
    soundTrack = getSoundTrack('SA_bash.ogg', delay=.25, node=suit)
    from toontown.suit.DistributedVideographerBoss import DistributedVideographerBoss
    musicTrack = Parallel()
    for obj in base.cr.doId2do.values():
        if isinstance(obj, DistributedVideographerBoss):
            musicTrack.append(Func(obj.startPhase2Particles))
    suitTrack = Sequence(ActorInterval(theSuit, 'snap'), Func(theSuit.setNeutralAnimationDrop), Wait(5.0 - theSuit.getDuration('snap')))
    destPos, h = battle.suitPendingPointsSilhouettesHighRoller[7]
    startPos = destPos + Point3(0, 0, 0)
    suitTrack.append(Sequence(musicTrack, Func(theSuit.reparentTo, battle), Func(theSuit.setPos, startPos), Func(theSuit.headsUp, battle),
                              Parallel(Sequence(ActorInterval(theSuit, 'frustrated'), Func(theSuit.loop, 'neutral2')), Func(theSuit.setChatAbsolute, "Cut! Cut!", CFSpeech | CFTimeout)), 
                              Parallel(Func(theSuit.setChatAbsolute, "Something's missing here.", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.nametag3d.setScale, 2.5), Func(theSuit.setChatAbsolute, "Of course!", CFSpeech | CFTimeout)), Wait(2.0), 
                              Parallel(Sequence(ActorInterval(theSuit, 'finger-wag'), Func(theSuit.loop, 'neutral2')), Func(theSuit.setChatAbsolute, "Every great production needs a good crew!", CFSpeech | CFTimeout)), 
                              Parallel(Func(theSuit.setChatAbsolute, "And lucky for me...", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Sequence(ActorInterval(theSuit, 'summon'), Func(theSuit.loop, 'rolled')), Func(theSuit.setChatAbsolute, "I brought my Producers.", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.nametag3d.setScale, 1.0), Func(theSuit.setChatAbsolute, "Places everyone! Let's give our guests some proper direction!", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "Now...", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "Take it from the top!", CFSpeech | CFTimeout)), Wait(4.0), 
                              ))
    suitTrack.append(Func(theSuit.setSuitStatusEffect, 'videographerImmune', modifier=1))
    return Parallel(suitTrack, soundTrack, propTracks, smokeTracks, selfDamageTracks, suitDeathTracks)

def doDirectorCuts(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    hollywoods = []
    puddleTracks = Parallel()
    moveTracks = Parallel()
    managerHealTracks = Parallel()
    animTracks = Parallel()
    propTracks = Parallel()
    selfDamageTracks = Parallel()
    smokeTracks = Parallel()
    suitDeathTracks = Parallel()
    for suit in battle.activeSuits:
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        suitTrack2 = Sequence(Wait(2), Parallel(ActorInterval(suit, 'flatten', duration=.55),
                                               MovieUtil.createSuitCrashTrack(suit, battle, 7)))
        selfDamageTrack = Sequence(Wait(2),
                Func(suit.showHpText, - suit.currHP),
                                   Func(suit.setHealthForMe, - suit.currHP),
                                   Func(suit.updateHealthBar, 0))
        smokeTrack = Sequence(Wait(2.0), Func(smoke.reparentTo, suit),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_tv.png')
        gavel = loader.loadModel('phase_14/models/char/ttcc_ene_multislacker-zero')
        gavel.setTexture(texture, 1)
        gavel.setP(-90)
        gavel.setH(180)
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y + 2, 30)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(180, -90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2.5), scaleUpTime=2.0),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y + 2, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        if suit.dna.name not in ('hroller2', 'videog', 'hroller'):
            selfDamageTracks.append(selfDamageTrack)
            smokeTracks.append(smokeTrack)
            propTracks.append(propTrack)
            suitDeathTracks.append(suitTrack2)
    soundTrack = getSoundTrack('SA_bash.ogg', delay=.25, node=suit)
    from toontown.suit.DistributedVideographerBoss import DistributedVideographerBoss
    musicTrack = Parallel()
    for obj in base.cr.doId2do.values():
        if isinstance(obj, DistributedVideographerBoss):
            musicTrack.append(Func(obj.startPhase2Particles))
    suitTrack = Sequence(ActorInterval(theSuit, 'snap'), Func(theSuit.setNeutralAnimationDrop), Wait(5.0 - theSuit.getDuration('snap')))
    destPos, h = battle.suitPendingPointsSilhouettesHighRoller[7]
    startPos = destPos + Point3(0, 0, 0)
    suitTrack.append(Sequence(musicTrack, Func(theSuit.reparentTo, battle), Func(theSuit.setPos, startPos), Func(theSuit.headsUp, battle),
                              Parallel(Sequence(ActorInterval(theSuit, 'frustrated'), Func(theSuit.loop, 'neutral2')), Func(theSuit.setChatAbsolute, "Cut! Cut!", CFSpeech | CFTimeout)), 
                              Parallel(Func(theSuit.setChatAbsolute, "Something's missing here.", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "Of course!", CFSpeech | CFTimeout)), Wait(2.0), 
                              Parallel(Sequence(ActorInterval(theSuit, 'finger-wag'), Func(theSuit.loop, 'neutral2')), Func(theSuit.setChatAbsolute, "Every great production needs a good crew!", CFSpeech | CFTimeout)), 
                              Parallel(Func(theSuit.nametag3d.setScale, 2.5), Func(theSuit.setChatAbsolute, "And lucky for me...", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Sequence(ActorInterval(theSuit, 'summon'), Func(theSuit.loop, 'rolled')), Func(theSuit.setChatAbsolute, "I brought my Producers.", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.nametag3d.setScale, 1.0), Func(theSuit.setChatAbsolute, "Places everyone! Let's give our guests some proper direction!", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "Now...", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "Take it from the top!", CFSpeech | CFTimeout)), Wait(4.0), 
                              ))
    suitTrack.append(Func(theSuit.clearSuitStatusEffect, 'vulnerable'))
    suitTrack.append(Func(theSuit.clearSuitStatusEffect, 'soaked'))
    suitTrack.append(Func(theSuit.clearSuitStatusEffect, 'marked'))
    suitTrack.append(__soakRemoval(theSuit, 1))
    suitTrack.append(Func(theSuit.splatSuit, 0, 1))
    suitTrack.append(Func(theSuit.clearSuitStatusEffect, 'zapped'))
    suitTrack.append(Func(theSuit.clearSuitStatusEffect, 'dazed'))
    suitTrack.append(Func(theSuit.setSuitStatusEffect, 'videographerImmune', modifier=1))
    return Parallel(suitTrack, soundTrack, propTracks, smokeTracks, selfDamageTracks, suitDeathTracks)

def doRisingStars2(attack):
    suit = attack['suit']
    battle = attack['battle']
    taunt = random.choice(
        ["Let me introduce you to some friends of mine."])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 16.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    moveTrack = Sequence(LerpPosInterval(suit, 0, sinkPos, other=battle), Wait(suit.getDuration('shot5')), LerpPosInterval(suit, 0, dropPos, other=battle), Func(suit.setPos, battle, dropPos))

    suitTrack = Parallel(ActorInterval(suit, 'shot5'), tauntInterval)
    suitTrack.append(Func(suit.setSuitStatusEffect, 'videographerImmune', modifier=1))
    return Parallel(suitTrack, moveTrack)

def doRisingStars(attack):
    suit = attack['suit']
    battle = attack['battle']

    resetPos, resetHpr = battle.getActorPosHpr(suit)
    sinkPos = suit.getPos(battle)
    dropPos = suit.getPos(battle)
    sinkPos2 = suit.getPos(battle)
    dropPos2 = suit.getPos(battle)
    sinkPos.setY(sinkPos.getY() + 16.5)
    sinkPos.setZ(sinkPos.getZ() - 4.5)
    sinkPos2.setY(sinkPos.getY() - 22.5)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    if suit.hasSuitStatusEffect('videographerImmune') and attack['name'] == 'VideographerRisingStars' or attack['name'] == 'VideographerRisingStars2':
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'videographerImmune'))
    return Parallel(suitTrack)

def getPartTrackLightning(particleEffect, startDelay, durationDelay, partExtraArgs, softStop=0, renderParent=render):
    particleEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) > 2:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(particleEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop, renderParent=renderParent))

def doTouchUp(attack):
    manager = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    suitTrack = Sequence(getSuitAnimTrack(attack))
    cagePropTracks = Parallel()
    selfDamageTracks = Parallel()

    BattleParticles.loadParticles()

    def getCloudTrack(lightning, targetSuit, battle=battle):
        particleEffect = BattleParticles.loadParticleFile('lightningGagExplosion.ptf')
        particleEffect.setScale(targetSuit.scale * 1.5)

        particleNode = targetSuit.attachNewNode('zap-particle-node')
        particleNode.setColorScaleOff(1)

        particleEffect.getParticlesNamed('particles-1').emitter.setOffsetForce(Vec3(0.0, 0.0, 15.0 + targetSuit.height))

        partTrack = getPartTrackLightning(particleEffect, 0, 3.0, [particleEffect, particleNode, 0], softStop=-2.4, renderParent=particleNode)

        track = Sequence(Func(lambda targetSuit=targetSuit, lightning=lightning: lightning.setPos(targetSuit.getPos(battle))), Func(lightning.show), Wait(0.1), LerpColorScaleInterval(lightning, 1.0, (1, 1, 1, 0)), Func(MovieUtil.removeProp, lightning))

        return Parallel(track, Sequence(partTrack, Func(particleNode.removeNode)))

    for targetData in targets:
        if 'suit' not in targetData:
            continue

        targetSuit = targetData['suit']

        lightning = globalPropPool.getProp('lightning')
        lightning.reparentTo(battle)
        lightning.hide()
        lightning.setScale(1, 1, 3)

        cagePropTrack = Sequence(Wait(1.0), getCloudTrack(lightning, targetSuit))
        cagePropTracks.append(cagePropTrack)

        targetTrack = Sequence(Wait(1.0), Parallel(Func(targetSuit.setSuitStatusEffect, 'damageUp', modifier=10, mode='refreshModifier'), MovieUtil.zapCogPowerhouse(targetSuit, 'large-zap', .5, 2.0, battle), Func(targetSuit.showHpTextNew, 0, text="+10% Damage!", colorCode=5)), Func(targetSuit.setNeutralAnimationDrop))

        selfDamageTracks.append(targetTrack)

    soundTrack = getSoundTrack('SA_bash.ogg', delay=0.25, node=manager)
    soundTrack2 = getSoundTrack('AA_lightning.ogg', node=manager)

    return Parallel(suitTrack, soundTrack, soundTrack2, cagePropTracks, selfDamageTracks)

def doHardCutBan(attack):
    suit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    taunt = getAttackTaunt(attack['name'], attack['suitName'], tauntIndex)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    targets = attack['target']
    cagePropTracks = Parallel()
    smokeTracks = Parallel()
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    zapTrack = Sequence(Wait(2.0), SoundInterval(zapSfx, volume=0.6))
    notifyTracks = Parallel()
    cagePropTracks = Parallel()
    suitTrack2 = Sequence(
        Parallel(
            getSuitAnimTrack(attack),
        ),

        Func(suit.enableBlend),

        Parallel(ActorInterval(suit, 'sparkplug', startTime=2.5),

        LerpAnimInterval(
            suit,
            duration=.5,
            startAnim='neutral',
            endAnim='sparkplug',
            startWeight=0.0,
            endWeight=1.0,
            blendType='easeInOut'
        )),

        Func(suit.disableBlend)
    )
    moveTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        def getChainsawFingerPos():
            handNode = suit.leftHand.attachNewNode('foo')
            handNode.setPos(-1.5631, 0.3, 0.0)
            handPos = handNode.getPos(render)
            handNode.removeNode()
            return handPos
        
        def getToonTargetPoint(toon):
            pnt = toon.getPos(render)
            pnt.setZ(pnt[2] + toon.getHeight() * 0.5)
            return Point3(pnt)
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(2), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(smoke.removeNode))
        notifyTrack = Sequence(Wait(2.0), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=3))
        notifyTrack.append(toon.makeShockDamageBurstTrack(duration=2.5, sparkCount=40))
        notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'vulnerable', modifier=50, turns=3, mode='refreshModifier')))
        targetPoint = lambda toon = toon: getToonTargetPoint(toon)
        targetPos = toon.getPos(battle)
        dSprayScale = 0.05
        if dmg > 0:
            cagePropTrack = Sequence(Wait(2.0), MovieUtil.getZapTrack(
                            battle,
                            Point4(1.0, 1.0, 0, 1.0),
                            getChainsawFingerPos,
                            targetPoint,
                            dSprayScale, 0.2, dSprayScale,
                        ))
            cagePropTracks.append(cagePropTrack)
            origH = suit.getH(battle)

            # Calculate heading to toon
            origPos, origHpr = battle.getActorPosHpr(suit)
            origPos2 = suit.getPos(battle)
            suit.setPos(battle, origPos)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)

            # Restore original heading
            suit.setH(battle, origH)
            suit.setPos(battle, origPos2)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            moveTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), Wait(3.5),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            smokeTracks.append(smokeTrack)
            notifyTracks.append(notifyTrack)
    #for t in attack['target']:
        #toon = t['toon']
        #dmg = t['hp']
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    toonTrack = getToonTracksCheat(attack, damageDelay=2, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['sidestep'], splicedDodgeAnims=[], showDamageExtraTime=0)
    soundTrack = getSoundTrack('SA_sparkplug2.ogg', delay=0, node=suit)
    return Parallel(suitTrack, zapTrack, suitTrack2, soundTrack, cagePropTracks, moveTracks, notifyTracks, smokeTracks, toonTrack)


def doPhantomEntryDamage(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    targetData = targets[0]

    if 'suit' not in targetData:
        return Sequence()

    targetSuit = targetData['suit']
    dmg = int(targetData.get('hp', 0))
    died = targetData.get('died', False)

    notifyTrack = Sequence(
        Parallel(
            Func(targetSuit.showHpTextNew, -dmg),
            Func(targetSuit.setHealthForMe, -dmg),
            Func(targetSuit.updateHealthBar, 0),
            ActorInterval(targetSuit, 'pie-small-react')
        ),
    )
    if died:
        if targetSuit.isVirtual:
            notifyTrack.append(MovieUtil.createVirtualSuitDeathTrack(targetSuit, battle))
            notifyTrack.append(Func(targetSuit.makeDead))
        else:
            notifyTrack.append(MovieUtil.createSuitDeathTrack(targetSuit, battle))
            notifyTrack.append(Func(targetSuit.makeDead))

    notifyTrack.append(
            Func(targetSuit.setNeutralAnimationDrop)
        )

    cameraTrack = Wait(5.0)

    return Sequence(
        Parallel(
            notifyTrack,
            cameraTrack
        )
    )

def doDonationFail(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    notifyTracks = Parallel()
    headTracks = Parallel()

    texture2 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer5.png')
    texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')

    for headPart in suit.animatedHeadParts:
        headTrack = Sequence(Wait(1.0), Func(headPart.loop, 'stun'), Func(headPart.setTexture, texture2, 1), Wait(1.0), Func(headPart.setTexture, texture, 1), Func(headPart.loop, 'neutral'))
        headTracks.append(headTrack)

    for targetData in targets:
        if 'suit' not in targetData:
            continue

        targetSuit = targetData['suit']
        damage = int(targetData.get('hp', 0))
        heal = int(targetData.get('heal', 0))
        died = targetData.get('died', False)

        # =========================================================
        # BROADCASTER DAMAGE
        # =========================================================
        if targetSuit.dna.name == 'bcaster' and damage > 0:
            targetTrack = Sequence(ActorInterval(suit, 'mob-mentality', endTime=1), Parallel(Func(suit.showHpTextNew, -damage), Func(suit.setHealthForMe, -damage), Func(suit.updateHealthBar, 0)), ActorInterval(suit, 'slip-forward'))

            if died:
                if suit.isVirtual:
                    targetTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
                    targetTrack.append(Func(suit.makeDead))
                else:
                    targetTrack.append(Parallel(ActorInterval(suit, 'flail'), MovieUtil.shortCircuitTrack(suit, battle)))
                    targetTrack.append(Func(suit.makeDead))
            else:
                targetTrack.append(Func(suit.setNeutralAnimationDrop))

            notifyTracks.append(targetTrack)

        # =========================================================
        # VIDEOGRAPHER HEAL
        # =========================================================
        elif targetSuit.dna.name == 'videog' and heal > 0:
            for headPart in targetSuit.animatedHeadParts:
                headTrack = Sequence(Func(targetSuit.pauseHeadFreakout), Wait(1.0), Func(headPart.loop, 'stun'), Func(headPart.setTexture, texture2, 1), Wait(1.0), Func(headPart.setTexture, texture, 1), Func(headPart.loop, 'neutral'), Func(targetSuit.resumeHeadFreakout))
                headTracks.append(headTrack)

            targetTrack = Sequence(ActorInterval(targetSuit, 'mob-mentality', endTime=1), Parallel(Func(targetSuit.showHpTextNew, heal), Func(targetSuit.setHealthForMe, heal), Func(targetSuit.updateHealthBar, 0)), ActorInterval(targetSuit, 'pie-small-react'), Func(targetSuit.setNeutralAnimationDrop))

            notifyTracks.append(targetTrack)

    dialogueTrack = Sequence(Wait(1.0), Func(suit.setChatAbsolute, "Hold on... we're losing signal!", CFSpeech | CFTimeout))
    suitAnimTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack = getSoundTrack('mus_dialup_0_fail.ogg')

    return Parallel(suitAnimTrack, dialogueTrack, notifyTracks, headTracks, soundTrack)

def doDonation2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    notifyTracks = Parallel()
    headTracks = Parallel()

    texture2 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer5.png')
    texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')

    # =========================================================
    # BROADCASTER HEAD
    # =========================================================
    for headPart in suit.animatedHeadParts:
        headTrack = Sequence(Wait(1.0), Func(headPart.loop, 'stun'), Func(headPart.setTexture, texture2, 1), Wait(5.0), Func(headPart.setTexture, texture, 1), Func(headPart.loop, 'neutral'))
        headTracks.append(headTrack)

    # =========================================================
    # TARGET RESULTS
    # =========================================================
    for targetData in targets:
        if 'suit' not in targetData:
            continue

        targetSuit = targetData['suit']
        damage = int(targetData.get('hp', 0))
        heal = int(targetData.get('heal', 0))
        died = targetData.get('died', False)

        if targetSuit.dna.name == 'bcaster' and damage > 0:
            targetTrack = Sequence(ActorInterval(suit, 'mob-mentality', endTime=1), Wait(5.0), Parallel(ActorInterval(suit, 'mob-mentality', startTime=1, endTime=0), Func(suit.showHpTextNew, -damage), Func(suit.setHealthForMe, -damage), Func(suit.updateHealthBar, 0)))

            if died:
                if suit.isVirtual:
                    targetTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
                    targetTrack.append(Func(suit.makeDead))
                else:
                    targetTrack.append(Parallel(ActorInterval(suit, 'flail'), MovieUtil.shortCircuitTrack(suit, battle)))
                    targetTrack.append(Func(suit.makeDead))
            else:
                targetTrack.append(Func(suit.setNeutralAnimationDrop))

            notifyTracks.append(targetTrack)

        elif targetSuit.dna.name == 'videog' and heal > 0:
            for headPart in targetSuit.animatedHeadParts:
                headTrack = Sequence(Func(targetSuit.pauseHeadFreakout), Wait(1.0), Func(headPart.loop, 'stun'), Func(headPart.setTexture, texture2, 1), Wait(5.0), Func(headPart.setTexture, texture, 1), Func(headPart.loop, 'neutral'), Func(targetSuit.resumeHeadFreakout))
                headTracks.append(headTrack)

            targetTrack = Sequence(ActorInterval(targetSuit, 'mob-mentality', endTime=1), Wait(5.0), Parallel(Func(targetSuit.showHpTextNew, heal), Func(targetSuit.setHealthForMe, heal), Func(targetSuit.updateHealthBar, 0)), ActorInterval(targetSuit, 'mob-mentality', startTime=1, endTime=0), Func(targetSuit.setNeutralAnimationDrop))
            notifyTracks.append(targetTrack)

    suitAnimTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack = getSoundTrack('mus_dialup_0.ogg')

    return Parallel(suitAnimTrack, notifyTracks, headTracks, soundTrack)

def doVideographerDeath(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTracks = Parallel()
    for s in battle.activeSuits:
        if s.dna.name == 'hroller2':
            theSuit = s
            taunt = random.choice(
                ["Ooo-well, ya know what they ffay: don't hate the Major Player, change the game!",
                        "I can jufft hear the crowd going wild for thiff intermiffion!",
                        "Let'ff get the hip hop ffhop right on top, a-one a-two-let'ff play true!",
                        "We'll be back after a ffhort break, but I'm ffure you'll fftay occupied in the meantime."])
            tauntInterval = Sequence(Func(theSuit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
            suitTrack = Sequence(Parallel(ActorInterval(theSuit, 'snap'), tauntInterval), Func(theSuit.setNeutralAnimation))
            suitTracks.append(suitTrack)
    propTracks = Parallel()
    toonTracks = Parallel()
    selfDamageTracks = Parallel()
    smokeTracks = Parallel()
    suitDeathTracks = Parallel()
    for suit in battle.activeSuits:
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        suitTrack2 = Sequence(Wait(2), Parallel(ActorInterval(suit, 'flatten', duration=1.25),
                                               MovieUtil.createSuitCrashTrack(suit, battle, 7)))
        selfDamageTrack = Sequence(Wait(2),
                Func(suit.showHpText, - suit.currHP),
                                   Func(suit.setHealthForMe, - suit.currHP),
                                   Func(suit.updateHealthBar, 0))
        smokeTrack = Sequence(Wait(2.0), Func(smoke.reparentTo, suit),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(MovieUtil.removeProp, smoke))
        texture = loader.loadTexture('phase_9/maps/ttcc_ene_tv.png')
        gavel = loader.loadModel('phase_14/models/char/ttcc_ene_multislacker-zero')
        gavel.setTexture(texture, 1)
        gavel.setP(-90)
        gavel.setH(180)
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        gavelPos = Point3(toonPos.getX(), y + 2, 30)
        propTrack = Sequence(
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(180, -90, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(2.5), scaleUpTime=2.0),
            LerpPosInterval(gavel, 0.25, Point3(toonPos.getX(), y + 2, 1)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 2)),
            LerpPosInterval(gavel, 0.1, Point3(toonPos.getX(), y + 2, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(gavel, .25, MovieUtil.PNT3_ZERO)
            ))
        if suit.dna.name not in ('hroller2', 'videog', 'hroller'):
            selfDamageTracks.append(selfDamageTrack)
            smokeTracks.append(smokeTrack)
            propTracks.append(propTrack)
            suitDeathTracks.append(suitTrack2)
    soundTrack = getSoundTrack('SA_TV_crash.ogg', delay=2.0, node=suit)
    soundTrack2 = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTracks, smokeTracks, suitDeathTracks, selfDamageTracks, toonTracks, propTracks, soundTrack)

def doBudgetCuts(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    allTubeTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    toonDamageTracks = Parallel()
    suitTrack = Sequence(Wait(3.0), doSnipeCut(attack))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tape.setColor(0, 0, 0, 1)
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))
            tubes[i].setColor(0, 0, 0, 1)

        hitPoint = lambda toon = toon: __toonTorsoPoint(toon)
        hips = toon.getHipsParts()
        animal = toon.style.getAnimal()
        scale = ToontownGlobals.toonBodyScales[animal]
        legs = toon.style.legs
        torso = toon.style.torso
        torso = torso[0]
        animal = animal[0]
        tubeHeight = -0.8
        if torso == 's':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'm':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 0.7975)
        elif torso == 'l':
            scaleUpPoint = Point3(scale * 2.03, scale * 2.03, scale * 1.11)
        if animal == 'h' or animal == 'd':
            tubeHeight = -0.87
            scaleUpPoint = Point3(scale * 1.69, scale * 1.69, scale * 0.67)
        tubePosPoints = [Point3(0, 0, tubeHeight), MovieUtil.PNT3_ZERO]
        tubeTracks = Parallel()
        tubeTracks.append(Func(battle.movie.needRestoreHips))
        for partNum in xrange(0, hips.getNumPaths()):
            nextPart = hips.getPath(partNum)
            tubeTracks.append(getPropTrack(tubes[partNum], nextPart, tubePosPoints, 0, 3, scaleUpPoint=scaleUpPoint))

        tubeTracks.append(Func(battle.movie.clearRestoreHips))
        soundTrack = getSoundTrack('SA_red_tape.ogg', delay=0, node=suit)
        toonDamageTrack = Sequence(ActorInterval(toon, 'struggle'))
        if dmg > 0:
            allTubeTracks.append(tubeTracks)
            soundTracks.append(soundTrack)
            toonDamageTracks.append(toonDamageTrack)
    return Parallel(toonTracks, soundTracks, suitTrack, toonDamageTracks, allTubeTracks)

def setPosFromOther(dest, source, offset = Point3(0, 0, 0)):
    pos = render.getRelativePoint(source, offset)
    dest.setPos(pos)
    dest.reparentTo(render)

def __getPartTrack(particleEffect, startDelay, durationDelay, partExtraArgs, softStop = 0):
    pEffect = partExtraArgs[0]
    parent = partExtraArgs[1]
    if len(partExtraArgs) == 3:
        worldRelative = partExtraArgs[2]
    else:
        worldRelative = 1
    return Sequence(Wait(startDelay), ParticleInterval(pEffect, parent, worldRelative, duration=durationDelay, cleanup=True, softStopT=softStop))

def doSynergy(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    particleEffect = BattleParticles.createParticleEffect('Synergy')
    waterfallEffect = BattleParticles.createParticleEffect(file='synergyWaterfall')
    partTrack = getPartTrack(particleEffect, 1.0, 3.4, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.4, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    target = attack['target']
    dmg = target[0]['hp']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'magic3'), Func(suit.setNeutralAnimationDrop))
    if dmg > 80:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                           "This isn't just a movie, it's an event! $%s in total impact!" %
                           int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    elif dmg > 60:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                           "It's official, this film's a mega-production! Estimated $%s on release!" %
                           int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    elif dmg > 40:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                           "The studio's investing heavily; expect $%s on release!" %
                           int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    else:
        suitSpeechTrack = Func(suit.setChatAbsolute,
                               "The premiere begins now... projected gross: $%s." %
                               int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, suitSpeechTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, suitSpeechTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doBudgetExpansion(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculator', playRate=1.25), Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute,
                               "Every fallen producer funds the finale... we're sitting at $%s in damage!" %
                              int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-.85, 0.25, -0.1), VBase3(1.352, 0.0, 180.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getLeftHand(), *calcPosPoints),
        ActorInterval(calculator, 'calculator', playRate=1.25),
        Func(MovieUtil.removeProp, calculator)
    )
    soundTrack = getSoundTrack('SA_audit.ogg', delay=1.3, node=suit)
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    targets = attack['target']
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, suit, Point3(0, 1.6, suit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, suit, 0], softStop=-3.5))
    rightKnives = []
    partTracks = Parallel()
    rightKnifeTracks = Parallel()
    sparkEffect = BattleParticles.loadParticleFile('resistanceEffectSparkle.ptf')
    sparks = sparkEffect.getParticlesNamed('particles-1')
    rightPosPoints = [Point3(0, 0, 0), VBase3(0, -90, 0)]
    if sparks:
        sparks.setPoolSize(10)
        sparks.setLitterSize(10)
        sparks.renderer.setEdgeColor(Vec4(1.0, 0.0, 0.0, 1.0))
    partTracks.append(Sequence(
        Wait(0.8),
        Parallel(
            ParticleInterval(sparkEffect, toon, worldRelative=0, duration=3.0, cleanup=True),
            autoFinish=1
        )
    ))
    for i in xrange(0, 3):
        rightKnives.append(globalPropPool.getProp('dagger'))
    for t in targets:
        for i in xrange(0, 3):
            knifeDelay = 0.11
            rightTrack = Sequence()
            rightTrack.append(Wait(0.5))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(getPropAppearTrack(rightKnives[i], suit.getRightHand(), rightPosPoints, 1e-06, Point3(.375, .375, .375), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['face'], hitDuration=0.25, missDuration=0.25, target=t))
            rightKnifeTracks.append(rightTrack)
    can = loader.loadModel('phase_5/models/props/megaphone')
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(ActorInterval(suit, 'glower'), Func(suit.setNeutralAnimation))
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(1.0), LerpScaleInterval(can, 0.5, (0, 0, 0)), Func(MovieUtil.removeProp, can))
    toonTrack = getToonTrackCheat(attack, .8, ['cringe'], 0, ['duck'])
    notifyTrack = Sequence(Wait(.8), Func(toon.showHpTextNew, -int(dmg), text="DAMAGE CUT!", colorCode=3))
    notifyTrack.append(Func(toon.setToonStatusEffect, 'damageDown', modifier=50, turns=2, mode='keepHighest'))
    soundTrack = getSoundTrack('SA_glower_power.ogg', delay=0.5, node=suit)
    soundTrack2 = getSoundTrack('tt_s_ara_cmg_toonHit.ogg', delay=.8, node=suit)
    return Parallel(soundTrack2, soundTrack, suitTrack, partTracks, rightKnifeTracks, toonTrack, notifyTrack, throwTrack, suitTrack2, sprayTrack)

def doVideographerPhase3(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    from toontown.suit.DistributedVideographerBoss import DistributedVideographerBoss
    musicTrack = Parallel()
    for obj in base.cr.doId2do.values():
        if isinstance(obj, DistributedVideographerBoss):
            musicTrack.append(Func(obj.startPhase3Particles))
    notifyTracks = Sequence(Wait(0.5))
    headTracks = Parallel()
    suitTrack = Sequence()
    soundTrack = getSoundTrack('tv_static.ogg', node=suit)
    soundTrack2 = getSoundTrack('tv_static.ogg', delay=1.5, node=suit)
    soundTrack4 = getSoundTrack('SA_hit.ogg', node=suit)
    texture2 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer4.png')
    texture3 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
    texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
    headTrack = Sequence()
    for headPart in suit.animatedHeadParts:
        headTrack.append(Func(suit.stopHeadFreakout))
        headTrack.append(Wait(1))
        headTrack.append(Func(headPart.loop, 'stun'))
        headTrack.append(Func(headPart.setTexture, texture2, 1))
        headTrack.append(Wait(suit.getDuration('throttletwo') - 4.25))
        headTrack.append(Parallel(Func(headPart.setTexture, texture, 1), soundTrack4, Func(headPart.loop, 'neutral')))
        headTrack.append(Func(suit.setupHeadFreakout, headPart, texture, texture3, texture2))
        headTrack.append(Func(suit.startHeadFreakout))
    notifyTrack = Sequence(ActorInterval(suit, 'chainsaw-cutscene-leap', startTime=2, endTime=2.5), Parallel(Parallel(soundTrack, soundTrack2), Sequence(ActorInterval(suit, 'sound-react-nt', endTime=2.5), ActorInterval(suit, 'throttletwo', startTime=3),
                            Func(suit.setSuitStatusEffect, 'videoStatic', modifier=100, mode='refreshModifier'),
                            Func(suit.loop, 'neutral2'))))
    destPos, h = battle.suitPendingPointsSilhouettesHighRoller[7]
    startPos = destPos + Point3(0, 0, 0)
    headTrackLook = Sequence()
    for headPart in suit.animatedHeadParts:
        headTrackLook.append(Sequence(LerpHprInterval(headPart, 1, VBase3(-80, 0, 0), blendType='easeInOut'), LerpHprInterval(headPart, 2, VBase3(80, 0, 0), blendType='easeInOut'),
                             LerpHprInterval(headPart, 1, VBase3(0, 0, 0), blendType='easeInOut')))
    suitTrack.append(Sequence(Func(theSuit.clearSuitStatusEffect, 'videographerImmune'), Func(theSuit.reparentTo, battle), Func(theSuit.setPos, startPos), Func(theSuit.headsUp, battle),
                              Parallel(headTrackLook, Sequence(Func(theSuit.loop, 'neutral2')), Func(theSuit.setChatAbsolute, "My Producers...", CFSpeech | CFTimeout)),
                              Parallel(Func(theSuit.setChatAbsolute, "You've cleared the entire set?!", CFSpeech | CFTimeout)), Wait(3.0), 
                              Parallel(Sequence(ActorInterval(theSuit, 'frustrated'), Func(theSuit.loop, 'neutral2')), Func(theSuit.setChatAbsolute, "Do you have ANY idea what you've just done?!", CFSpeech | CFTimeout)), 
                              Parallel(Func(theSuit.setChatAbsolute, "You took ALL of my producers off the air!!", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "Do you know how much work goes into a production like this?!", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "All of the planning, the staging, the shooting... and you just TRASHED IT!!", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "...What's this??", CFSpeech | CFTimeout), ActorInterval(suit, 'chainsaw-cutscene-leap', duration=2)),
                              Parallel(notifyTrack, headTrack),
                              Func(theSuit.setChatAbsolute, "We-we're getting inter-fer-ference...", CFSpeech | CFTimeout), Wait(4.0),
                              Parallel(Func(theSuit.nametag3d.setScale, 2.5), Sequence(ActorInterval(theSuit, 'finger-wag'), Func(theSuit.loop, 'neutral-unstable')), Func(theSuit.setChatAbsolute, "I M-M-MUST keep the feed rol-l-l-ling!!", CFSpeech | CFTimeout)), 
                              Parallel(Sequence(ActorInterval(theSuit, 'rake-react', playRate=2.0), Func(theSuit.loop, 'neutral-unstable')), Func(theSuit.setChatAbsolute, "I d-didn't come ---KZZZZT--- this far j-j-just to...", CFSpeech | CFTimeout)), Wait(2.0),
                              Parallel(Sequence(ActorInterval(theSuit, 'small-zap', duration=2), Func(theSuit.loop, 'neutral-unstable')), Func(theSuit.setChatAbsolute, "KZZZT---", CFSpeech | CFTimeout)), 
                              Parallel(Sequence(ActorInterval(theSuit, 'pie-small-react'), Func(theSuit.loop, 'neutral-unstable')), Func(theSuit.setChatAbsolute, "...CUT TO STATIC!!", CFSpeech | CFTimeout)), 
                              Parallel(Func(theSuit.nametag3d.setScale, 1.0), musicTrack, LerpScaleInterval(theSuit, suit.getDuration('effort'), 1.125, startScale=1, blendType='easeInOut'), 
                                       Func(theSuit.makeSwole), LerpColorScaleInterval(suit.getGeomNode(), suit.getDuration('effort'), (0.58, 0.2, 1, 1), blendType='easeIn'),
                                       Sequence(ActorInterval(theSuit, 'effort'), Func(theSuit.loop, 'rolled')), Func(theSuit.setChatAbsolute, "Oh... now THIS is an effect!!", CFSpeech | CFTimeout)), 
                              Parallel(Func(theSuit.setChatAbsolute, "Well Toons, you've made it to the part of the show nobody was supposed to see...", CFSpeech | CFTimeout)), Wait(4.0), 
                              Func(theSuit.setChatAbsolute, "Forget the Producers.", CFSpeech | CFTimeout), Wait(2.0),
                              Func(theSuit.setChatAbsolute, "Forget the script.", CFSpeech | CFTimeout), Wait(2.0),
                              Func(theSuit.setChatAbsolute, "Forget everything you thought you were watching!", CFSpeech | CFTimeout), Wait(4.0),
                              Parallel(Func(theSuit.setChatAbsolute, "The cameras are rolling, the signal is breaking, and I'm going off-script!!", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "You wanted all the attention? Then keep your eyes on ME!", CFSpeech | CFTimeout)), Wait(4.0), 
                              Parallel(Func(theSuit.setChatAbsolute, "WELCOME TO THE FINAL ACT!!", CFSpeech | CFTimeout)), Wait(4.0), 
                              ))
    headTracks.append(headTrack)
    cameraTrack = Sequence(MovieCamera.motionShot(0.0, 14.0, 10.0, -180, 0, 0.0, 0, theSuit), Wait(3.0))

    return Parallel(suitTrack)


def doVideoStatic(attack):
    suit = attack['suit']
    battle = attack['battle']
    notifyTracks = Sequence(Wait(0.5))
    headTracks = Parallel()
    theSuit = None
    soundTrack = getSoundTrack('tv_static.ogg', delay=1, node=suit)
    soundTrack2 = getSoundTrack('tv_static.ogg', delay=2.5, node=suit)
    soundTrack4 = getSoundTrack('SA_hit.ogg', node=suit)
    for s in battle.activeSuits:
        if s.dna.name == 'videog' and suit.dna.name != 'videog':
            theSuit = s
            texture2 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer4.png')
            texture3 = loader.loadTexture('phase_9/maps/ttcc_ene_videographer3.png')
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            headTrack = Sequence()
            for headPart in s.animatedHeadParts:
                headTrack.append(Func(theSuit.stopHeadFreakout))
                headTrack.append(Wait(1))
                headTrack.append(Func(headPart.loop, 'stun'))
                headTrack.append(Func(headPart.setTexture, texture2, 1))
                headTrack.append(Wait(theSuit.getDuration('throttletwo') - 4.25))
                headTrack.append(Parallel(Func(headPart.setTexture, texture, 1), soundTrack4, Func(headPart.loop, 'neutral')))
                headTrack.append(Func(theSuit.setupHeadFreakout, headPart, texture, texture3, texture2))
                headTrack.append(Func(theSuit.startHeadFreakout))
            notifyTrack = Sequence(ActorInterval(theSuit, 'sound-react-nt', endTime=2.5), ActorInterval(theSuit, 'throttletwo', startTime=3),
                                       Func(theSuit.showHpStringVideographer20),
                                       Func(theSuit.setSuitStatusEffect, 'videoStatic', modifier=20, mode='refreshModifier'),
                                       Func(theSuit.setNeutralAnimation), Wait(2.0))
            headTracks.append(headTrack)
            cameraTrack = Sequence(MovieCamera.motionShot(0.0, 14.0, 10.0, -180, 0, 0.0, 0, theSuit), Wait(3.0))
            notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    if theSuit == None:
        theSuit = suit

    return Parallel(notifyTracks, soundTrack2, headTracks, soundTrack)


def doRisingStarsSacrifice(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    targetSuit = targets[0].get('suit')

    if targetSuit is None:
        return Sequence()

    dmg = targets[0].get('hp', 0)

    puddle = globalPropPool.getProp('quicksand')
    puddle.setColor(Vec4(0.0, 0.0, 1.0, 1))
    puddle.setHpr(Point3(120, 0, 0))
    puddle.setScale(0.01)

    puddleTrack = Sequence(
        Func(battle.movie.needRestoreRenderProp, puddle),
        Func(puddle.reparentTo, targetSuit),
        Func(puddle.wrtReparentTo, render),
        LerpScaleInterval(puddle, 0.9, Point3(1.7, 1.7, 1.7), startScale=MovieUtil.PNT3_NEARZERO),
        Wait(3.0),
        LerpFunctionInterval(puddle.setAlphaScale, fromData=1, toData=0, duration=0.8),
        Func(puddle.removeNode)
    )

    moveTrack = Sequence(
        Wait(1.8),
        LerpPosInterval(targetSuit, 0.9, Point3(0, 0, -3.1), other=puddle),
        LerpPosInterval(targetSuit, 0.4, Point3(0, 0, -9.1), other=puddle),
        MovieUtil.createRisingStars(targetSuit, battle),
        Func(targetSuit.setPos, puddle, Point3(0, 0, 0)),
        Wait(2),
        LerpColorScaleInterval(targetSuit, 2, (1, 1, 1, 1)),
        Wait(1.1),
        Func(targetSuit.showHpString, '+50% Damage')
    )

    animTrack = Sequence(
        Wait(0.9),
        ActorInterval(targetSuit, 'flail-qs', endTime=1.75),
        ActorInterval(targetSuit, 'flail-qs', startTime=1.25, endTime=1.75),
        ActorInterval(targetSuit, 'flail-qs', startTime=1.25, endTime=1.25), Func(targetSuit.setNeutralAnimationDrop),
    )

    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)

    return Parallel(
        suitTrack,
        moveTrack,
        animTrack,
        soundTrack,
        puddleTrack
    )

def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.setNeutralAnimationTrap))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)

def doRecordCut(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    explosionTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    recordTracks = Parallel()
    suitTracks = Parallel()
    notifyTracks = Parallel()
    suitTrack = Parallel(getSuitAnimTrack(attack))
    suitAnimTrack = Sequence(ActorInterval(suit, 'effort', endTime=3.0), ActorInterval(suit, 'sanction'), Func(suit.setNeutralAnimationDrop))
    posPoints = [Point3(0, 2.5, 5), VBase3(0, 90, 0)]
    soundTrack = getSoundTrack('SA_magic_orb.ogg', node=suit)
    soundTrack3 = getSoundTrack('CHQ_VP_frisbee_gears.ogg', delay=3.8,  node=suit)
    soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=3.8, node=suit)
    soundTracks.append(soundTrack)
    soundTracks.append(soundTrack3)
    soundTracks.append(soundTrack2)
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        leftPosPoints = [Point3(0, 0, 0), VBase3(0, 0, 90)]
        rightPosPoints = [Point3(0, 0, 0), VBase3(0, 0, 90)]
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        explosionTrack = Sequence()
        explosionTrack.append(Wait(3.8))
        record = loader.loadModel('props/general/models/cc_m_gen_prp_vinyl_disk')
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        recordTrack = Sequence(Parallel(LerpHprInterval(record, 3.5, (0, 90, 2700), startHpr=(0, 90, 0), other=suit),
                                         getPropAppearTrack(record, suit, posPoints, 0, Point3(1, 1, 1), scaleUpTime=2.0)), 
                               Parallel(LerpHprInterval(record, .3, (0, 90, 900), startHpr=(0, 90, 0), other=suit),
                                         getPropThrowTrack(attack, record, hitPointNames=['face'], missPointNames=['miss'], hitDuration=0.3, missDuration=0.3, target=t)))
        recordTracks.append(recordTrack)

        notifyTrack = Sequence(Wait(3.8), Func(toon.showHpTextNew, - int(dmg), text="DAMAGE CUT!", colorCode=4))
        notifyTrack.append(Func(toon.setToonStatusEffect, 'damageDown', modifier=50, turns=2, mode='keepHighest'))
        #toonTrack = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        if dmg > 0:
            explosionTracks.append(explosionTrack)
            notifyTracks.append(notifyTrack)
    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=3.8, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                         dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, suitTrack, toonTracks, toonDamageTrack, notifyTracks, explosionTracks, soundTracks, recordTracks, suitAnimTrack)

def doSnipeMegaphone(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    explosionTracks = Parallel()
    toonTracks = Parallel()
    soundTracks = Parallel()
    leftKnifeTracks = Parallel()
    rightKnifeTracks = Parallel()
    suitTracks = Parallel()
    notifyTracks = Parallel()
    can = loader.loadModel('phase_5/models/props/megaphone')
    posPoints = [Point3(-0.5, 0, .5), VBase3(0, 0, 90)]
    throwTrack = Sequence(getPropAppearTrack(can, suit.getRightHand(), posPoints, 0, Point3(2, 2, 2), scaleUpTime=1.5), Wait(1.0), LerpScaleInterval(can, 0.5, (0, 0, 0)),
                          Func(MovieUtil.removeProp, can))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + toon.height - 0.2)
        leftPosPoints = [Point3(0, 0, 0), VBase3(0, 0, 90)]
        rightPosPoints = [Point3(0, 0, 0), VBase3(0, 0, 90)]
        explosionTrack = Sequence()
        explosionTrack.append(Wait(1.5))
        explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
        leftKnives = []
        rightKnives = []
        for i in xrange(0, 5):
            leftKnives.append(globalPropPool.getProp('dagger'))
            rightKnives.append(globalPropPool.getProp('dagger'))

        for i in xrange(0, 3):
            knifeDelay = 0.11
            leftTrack = Sequence()
            leftTrack.append(Wait(1.1))
            leftTrack.append(Wait(i * knifeDelay))
            leftTrack.append(
                getPropAppearTrack(leftKnives[i], can, leftPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            leftTrack.append(getPropThrowTrack(attack, leftKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                               hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                leftKnifeTracks.append(leftTrack)
            rightTrack = Sequence()
            rightTrack.append(Wait(1.1))
            rightTrack.append(Wait(i * knifeDelay))
            rightTrack.append(
                getPropAppearTrack(rightKnives[i], can, rightPosPoints, 1e-06, Point3(0.4, 0.4, 0.4), scaleUpTime=0.1))
            rightTrack.append(getPropThrowTrack(attack, rightKnives[i], hitPointNames=['face'], missPointNames=['miss'],
                                                hitDuration=0.3, missDuration=0.3, target=t))
            if dmg > 0:
                rightKnifeTracks.append(rightTrack)

        notifyTrack = Sequence(Wait(1.6), Func(toon.showHpTextNew, - int(dmg), text="DAMAGE CUT!", colorCode=4))
        notifyTrack.append(Func(toon.setToonStatusEffect, 'damageDown', modifier=50, turns=2, mode='keepHighest'))
        #toonTrack = getToonTracks(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7, dodgeAnimNames=['neutral'])
        soundTrack = getSoundTrack('SA_glower_power.ogg', delay=1.1, node=suit)
        soundTrack2 = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=1.5, node=suit)
        suitTrack = Parallel(getSuitAnimTrack(attack, disrespectBlend=True))
        suitTrack.append(Wait(2.0))
        if dmg > 0:
            soundTracks.append(soundTrack)
            soundTracks.append(soundTrack2)
            explosionTracks.append(explosionTrack)
            suitTracks.append(suitTrack)
            origH = suit.getH(battle)

            # Calculate heading to toon
            origPos, origHpr = battle.getActorPosHpr(suit)
            origPos2 = suit.getPos(battle)
            suit.setPos(battle, origPos)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)

            # Restore original heading
            suit.setH(battle, origH)
            suit.setPos(battle, origPos2)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            suitTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'glower'),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            notifyTracks.append(notifyTrack)
            notifyTracks.append(throwTrack)
    damageAnims = [['slip-backward', 0.01, 0.35]]
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=1.6, splicedDamageAnims=damageAnims, dodgeDelay=0.7,
                                         dodgeAnimNames=['neutral'])
    return Parallel(suitTracks, toonTracks, rightKnifeTracks, toonDamageTrack, notifyTracks, leftKnifeTracks, explosionTracks, soundTracks)
