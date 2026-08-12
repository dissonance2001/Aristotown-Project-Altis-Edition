from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from toontown.suit.SuitBase import *
from toontown.toon.ToonDNA import *
from toontown.battle.BattleSounds import *
from toontown.battle import MovieCamera
from toontown.battle import SuitBattleGlobals
from direct.directnotify import DirectNotifyGlobal
from toontown.suit import Suit
from toontown.suit import SuitDNA
from toontown.battle import MovieUtil
from toontown.chat.ChatGlobals import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import BattleParticles
from toontown.battle import BattleProps
from toontown.battle.attacks.toons import MovieNPCSOS
import random
notify = DirectNotifyGlobal.directNotify.newCategory('MovieLures')

def safeWrtReparentTo(nodePath, parent):
    if nodePath and not nodePath.isEmpty():
        nodePath.wrtReparentTo(parent)


def doLures(lures):
    if len(lures) == 0:
        return (None, None)
    npcArrivals, npcDepartures, npcs = MovieNPCSOS.doNPCTeleports(lures)
    mtrack = Parallel()
    for l in lures:
        battle = l['battle']
        ival = __doLureLevel(l, npcs)
        if ival:
            mtrack.append(ival)

    lureTrack = Sequence(npcArrivals, mtrack, npcDepartures)
    camDuration = mtrack.getDuration()
    enterDuration = npcArrivals.getDuration()
    exitDuration = npcDepartures.getDuration()
    camTrack = MovieCamera.chooseLureShot(lures, camDuration, battle, enterDuration, exitDuration)
    return (lureTrack, camTrack)

def showLureRounds(suit, battle, level):
    trapProp = suit.battleTrapProp
    currentBossHealth = -1
    if trapProp:
        suit.showHpStringRed("TRAPPED")
    elif suit.dna.name in ['hroller2', 'videog', 'bcaster', 'mplayers', 'hroller', 'fires', 'fbed', 'psetter', 'mouthp', 'rainmake', 'chainsaw',
                         'whunter', 'wsi', 'redd', 'duckshfl', 'treek', 'bellring', 'ddiver', 'gatekeep', 'director']:
        suit.showHpStringGreen("LURED 1 ROUND")
    elif suit.hasSuitStatusEffect('unionBusterNoAttack'):
        suit.showHpStringGreen("LURED 2 ROUNDS")
    elif suit.hasSuitStatusEffect('desperation'):
        suit.showHpStringGreen("LURED 1 ROUND")
    elif suit.hasSuitStatusEffect('starOfTheShow'):
        suit.showHpStringGreen("LURED 1 ROUND")
    elif suit.hasSuitStatusEffect('enraged'):
        suit.showHpStringGreen("LURED 1 ROUND")
    elif suit.hasSuitStatusEffect('closedSession'):
        suit.showHpStringGreen("LURED 1 ROUND")
    elif suit.getManager():
        suit.showHpStringGreen("LURED 2 ROUNDS")
    elif suit.getGovernaught():
        suit.showHpStringGreen("LURED 2 ROUNDS")
    elif suit.hasSuitStatusEffect('lureResist'):
        suit.showHpStringGreen("LURED 2 ROUNDS")
    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2'):
        suit.showHpStringGreen("LURED 2 ROUNDS")
    elif suit.isSkeleton and suit.currHP > (suit.maxHP * 1.5):
        suit.showHpStringGreen("LURED 1 ROUND")
    elif suit.currHP > (suit.maxHP * 1.5):
        suit.showHpStringGreen("LURED 2 ROUNDS")
    elif suit.isVirtual:
        suit.showHpStringGreen("LURED %i ROUNDS" % (ToontownBattleGlobals.AvLureRounds[level] - 1))
    elif suit.isSkeleton:
        suit.showHpStringGreen("LURED %i ROUNDS" % (ToontownBattleGlobals.AvLureRounds[level]))
    else:
        suit.showHpStringGreen("LURED %i ROUNDS" % (ToontownBattleGlobals.AvLureRounds[level] + 1))


def __doLureLevel(lure, npcs):
    level = lure['level']
    if level == 0:
        return __lureOneDollar(lure, npcs)
    elif level == 1:
        return __lureSmallMagnet(lure, npcs)
    elif level == 2:
        return __lureFiveDollar(lure, npcs)
    elif level == 3:
        return __lureLargeMagnet(lure, npcs)
    elif level == 4:
        return __lureTenDollar(lure, npcs)
    elif level == 5:
        return __lureHypnotize(lure, npcs)
    elif level == 6:
        return __lureFiftyDollar(lure, npcs)
    elif level == 7:
        return __lureSlideshow(lure, npcs)
    
    return None


def getSoundTrack(fileName, delay = 0.01, duration = None, node = None):
    soundEffect = globalBattleSoundCache.getSound(fileName)
    if duration:
        return Sequence(Wait(delay), SoundInterval(soundEffect, duration=duration, node=node))
    else:
        return Sequence(Wait(delay), SoundInterval(soundEffect, node=node))


def __createFishingPoleMultiTrack(lure, dollarName, npcs = []):
    toon = lure['toon']
    if 'npc' in lure:
        toon = lure['npc']
    targets = lure['target']
    battle = lure['battle']
    sidestep = lure['sidestep']
    reachAnimDuration = 85/24
    pole = globalPropPool.getProp('fishing-pole')
    pole2 = MovieUtil.copyProp(pole)
    poles = [pole, pole2]
    hands = toon.getRightHands()

    def positionDollar(dollar, suit):
        dollar.reparentTo(suit)
        dollar.setPos(0, 7.5, 0)

    poleTrack = Sequence(Func(MovieUtil.showProps, poles, hands), ActorInterval(pole, 'fishing-pole'), Func(MovieUtil.removeProps, poles))
    toonTrack = Sequence(Func(toon.headsUp, battle, MovieUtil.calcAvgSuitPos(lure)), ActorInterval(toon, 'battlecast'), Func(toon.loop, 'neutral'))
    tracks = Parallel(poleTrack, toonTrack)
    for target in targets:
        hp = target['hp']
        kbbonus = target['kbbonus']
        suit = target['suit']
        died = target['died']
        revived = target['revived']
        trapProp = suit.battleTrapProp
        dollar = globalPropPool.getProp(dollarName)
        tracks.append(Sequence(Func(positionDollar, dollar, suit), Func(dollar.wrtReparentTo, battle), ActorInterval(dollar, dollarName, duration=3), getSplicedLerpAnimsTrack(dollar, dollarName, 0.7, 2.0, startTime=3), LerpPosInterval(dollar, 0.2, Point3(0, -5, 7)), Func(MovieUtil.removeProp, dollar)))
        if sidestep == 0:
            if kbbonus == 1 or hp > 0:
                suitTrack = Sequence()
                makeUnLured = Func(suit.clearSuitStatusEffect, 'lured')
                if toon.getTrackBonusLevel(LURE_TRACK) > 1:
                    if suit.getManager() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.getGovernaught() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.hasSuitStatusEffect('lureResist') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.currHP > (suit.maxHP * 1.5) and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.isVirtual:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] - 1)
                    elif suit.isSkeleton:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']])
                    else:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] + 1)
                else:
                    if suit.getManager() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.getGovernaught() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.hasSuitStatusEffect('lureResist') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.currHP > (suit.maxHP * 1.5) and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.isVirtual:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] - 1)
                    elif suit.isSkeleton:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']])
                    else:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] + 1)
                opos, ohpr = battle.getActorPosHpr(suit)
                reachDist = MovieUtil.SUIT_LURE_DISTANCE
                reachPos = Point3(opos[0], opos[1] - reachDist, opos[2])
                suit.setPendingQueuedLured(True)
                if suit.dna.name in ('hrollers', 'mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'director', 'fmaker', 'cinema', 'choreo'):
                    suitTrack.append(Func(suit.setNeutralAnimationRolled))
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'trapped'))
                else:
                    suitTrack.append(Func(suit.setNeutralAnimation))
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'trapped'))
                suitTrack.append(Wait(3.5))
                suitName = suit.getStyleName()
                suitPos, suitHpr = battle.getActorPosHpr(suit)
                suitPos.setY(suitPos.getY() + MovieUtil.SUIT_EXTRA_REACH_DISTANCE)
                suitTrack.append(Func(showLureRounds, suit, battle, lure['level']))
                moveTrack = lerpSuit(suit, 0.0, reachAnimDuration / 2.15, suitPos, battle, trapProp, blendType='easeInOut')
                reachTrack = ActorInterval(suit, 'reach')
                suitTrack.append(Parallel(moveTrack, reachTrack))
                if trapProp:
                    suitTrack.append(Func(trapProp.wrtReparentTo, battle))
                suitTrack.append(Func(suit.setPos, battle, reachPos))
                if trapProp:
                    suitTrack.append(Func(trapProp.wrtReparentTo, suit))
                    suit.battleTrapProp = trapProp
                suitTrack.append(Func(suit.setDizzy, 1))
                suitTrack.append(Func(suit.loopSyncedLuredAnimations))
                suitTrack.append(Func(battle.lureSuit, suit))
                suitTrack.append(makeLured)
                if suit.getSuitStatusModifier('rushJob') == 2:
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'rushJob'))
                if hp > 0:
                    for headPart in suit.animatedHeadParts:
                        suitTrack.append(Func(headPart.loop, 'stun'))
                    suitTrack.append(__createSuitDamageTrack(battle, suit, hp, lure, trapProp, revived, died))
                    suitTrack.append(makeUnLured)
                    suitTrack.append(Func(suit.setDizzy, 0))
                    suitTrack.append(Func(suit.setSuitStatusEffect, 'dazed', modifier=1, turns=2))
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'trapped'))
                    if suit.hasSuitStatusEffect('sued'):
                        suitTrack.append(Func(suit.setSuitStatusEffect, 'sued', modifier=1, turns=4))
                tracks.append(suitTrack)
        else:
            if not suit.isLured:
                tracks.append(MovieUtil.createSuitTeaseMultiTrack(suit, battle, 3.3))

    tracks.append(getSoundTrack('TL_fishing_pole.ogg', delay=0.5, node=toon))
    return tracks


def __createMagnetMultiTrack(lure, magnet, pos, hpr, scale, isSmallMagnet = 1, npcs = []):
    toon = lure['toon']
    if 'npc' in lure:
        toon = lure['npc']
    battle = lure['battle']
    sidestep = lure['sidestep']
    targets = lure['target']
    tracks = Parallel()
    tracks.append(Sequence(ActorInterval(toon, 'hold-magnet'), Func(toon.loop, 'neutral')))
    hands = toon.getLeftHands()
    magnet2 = MovieUtil.copyProp(magnet)
    magnets = [magnet, magnet2]
    magnetTrack = Sequence(Wait(0.7), Func(MovieUtil.showProps, magnets, hands, pos, hpr, scale), Wait(6.3), Func(MovieUtil.removeProps, magnets))
    tracks.append(magnetTrack)
    for target in targets:
        suit = target['suit']
        trapProp = suit.battleTrapProp
        if sidestep == 0:
            hp = target['hp']
            kbbonus = target['kbbonus']
            died = target['died']
            revived = target['revived']
            if kbbonus == 1 or hp > 0:
                suitTrack = Sequence()
                suitDelay = 2.6
                suitMoveDuration = 0.8
                makeUnLured = Func(suit.clearSuitStatusEffect, 'lured')
                if toon.getTrackBonusLevel(LURE_TRACK) > 1:
                    if suit.getManager() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.getGovernaught() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.hasSuitStatusEffect('lureResist') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.currHP > (suit.maxHP * 1.5) and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.isVirtual:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] - 1)
                    elif suit.isSkeleton:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']])
                    else:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] + 1)
                else:
                    if suit.getManager() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.getGovernaught() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.hasSuitStatusEffect('lureResist') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.currHP > (suit.maxHP * 1.5) and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.isVirtual:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] - 1)
                    elif suit.isSkeleton:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']])
                    else:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] + 1)
                opos, ohpr = battle.getActorPosHpr(suit)
                reachDist = MovieUtil.SUIT_LURE_DISTANCE
                reachPos = Point3(opos[0], opos[1] - reachDist, opos[2])
                numShakes = 3
                shakeTotalDuration = 0.8
                shakeDuration = shakeTotalDuration / float(numShakes)
                suit.setPendingQueuedLured(True)
                if suit.dna.name in ('hrollers', 'mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'director', 'fmaker', 'cinema', 'choreo'):
                    suitTrack.append(Func(suit.setNeutralAnimationRolled))
                    suitTrack.append(Func(suit.makeUnTrapped))
                else:
                    suitTrack.append(Func(suit.setNeutralAnimation))
                    suitTrack.append(Func(suit.makeUnTrapped))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(showLureRounds, suit, battle, lure['level']))
                suitTrack.append(ActorInterval(suit, 'magnet', startTime=2.37, endTime=1.82))
                for i in xrange(0, numShakes):
                    suitTrack.append(
                        ActorInterval(suit, 'magnet', startTime=1.82, endTime=1.16, duration=shakeDuration))

                suitTrack.append(ActorInterval(suit, 'magnet', startTime=1.16, endTime=0.7))
                suitTrack.append(ActorInterval(suit, 'magnet', startTime=0.7, duration=1.3))
                suitTrack.append(Func(suit.setDizzy, 1))
                suitTrack.append(Func(suit.loopSyncedLuredAnimations))
                suitTrack.append(Func(battle.lureSuit, suit))
                suitTrack.append(makeLured)
                if suit.getSuitStatusModifier('rushJob') == 2:
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'rushJob'))
                if hp > 0:
                    for headPart in suit.animatedHeadParts:
                        suitTrack.append(Func(headPart.loop, 'stun'))
                    suitTrack.append(__createSuitDamageTrack(battle, suit, hp, lure, trapProp, revived, died))
                    suitTrack.append(makeUnLured)
                    suitTrack.append(Func(suit.setDizzy, 0))
                    suitTrack.append(Func(suit.setSuitStatusEffect, 'dazed', modifier=1, turns=2))
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'trapped'))
                    if suit.hasSuitStatusEffect('sued'):
                        suitTrack.append(Func(suit.setSuitStatusEffect, 'sued', modifier=1, turns=4))
                tracks.append(suitTrack)
                tracks.append(lerpSuit(suit, suitDelay + 0.55 + shakeTotalDuration, suitMoveDuration, reachPos, battle, trapProp))
        else:
            if not suit.isLured:
                tracks.append(MovieUtil.createSuitTeaseMultiTrack(suit, battle, 2.75))

    if isSmallMagnet == 1:
        tracks.append(getSoundTrack('TL_small_magnet.ogg', delay=0.7, node=toon))
    else:
        tracks.append(getSoundTrack('TL_large_magnet.ogg', delay=0.7, node=toon))
    return tracks


def __createHypnoGogglesMultiTrack(lure, npcs = []):
    toon = lure['toon']
    if 'npc' in lure:
        toon = lure['npc']
    targets = lure['target']
    battle = lure['battle']
    sidestep = lure['sidestep']
    goggles = globalPropPool.getProp('hypno-goggles')
    goggles2 = MovieUtil.copyProp(goggles)
    bothGoggles = [goggles, goggles2]
    pos = Point3(-1.03, 1.04, -0.3)
    hpr = Point3(-96.55, 36.14, -170.59)
    scale = Point3(1.5, 1.5, 1.5)
    hands = toon.getLeftHands()
    gogglesTrack = Sequence(Wait(0.6), Func(MovieUtil.showProps, bothGoggles, hands, pos, hpr, scale), ActorInterval(goggles, 'hypno-goggles', duration=2.2), Func(MovieUtil.removeProps, bothGoggles))
    toonTrack = Sequence(ActorInterval(toon, 'hypnotize'), Func(toon.loop, 'neutral'))
    tracks = Parallel(gogglesTrack, toonTrack)
    for target in targets:
        suit = target['suit']
        trapProp = suit.battleTrapProp
        if sidestep == 0:
            hp = target['hp']
            kbbonus = target['kbbonus']
            died = target['died']
            revived = target['revived']
            if kbbonus == 1 or hp > 0:
                suitTrack = Sequence()
                makeUnLured = Func(suit.clearSuitStatusEffect, 'lured')
                if toon.getTrackBonusLevel(LURE_TRACK) > 1:
                    if suit.getManager() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.getGovernaught() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.hasSuitStatusEffect('lureResist') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.currHP > (suit.maxHP * 1.5) and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.isVirtual:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] - 1)
                    elif suit.isSkeleton:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']])
                    else:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] + 1)
                else:
                    if suit.getManager() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.getGovernaught() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.hasSuitStatusEffect('lureResist') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.currHP > (suit.maxHP * 1.5) and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.isVirtual:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] - 1)
                    elif suit.isSkeleton:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']])
                    else:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] + 1)
                suitDelay = 1.6
                suitAnimDuration = 1.5
                opos, ohpr = battle.getActorPosHpr(suit)
                reachDist = MovieUtil.SUIT_LURE_DISTANCE
                reachPos = Point3(opos[0], opos[1] - reachDist, opos[2])
                suit.setPendingQueuedLured(True)
                if suit.dna.name in ('hrollers', 'mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'director', 'fmaker', 'cinema', 'choreo'):
                    suitTrack.append(Func(suit.setNeutralAnimationRolled))
                    suitTrack.append(Func(suit.makeUnTrapped))
                else:
                    suitTrack.append(Func(suit.setNeutralAnimation))
                    suitTrack.append(Func(suit.makeUnTrapped))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(showLureRounds, suit, battle, lure['level']))
                suitTrack.append(ActorInterval(suit, 'hypnotized'))
                suitTrack.append(Func(suit.setPos, battle, reachPos))
                suitTrack.append(Func(suit.setDizzy, 1))
                suitTrack.append(Func(suit.loopSyncedLuredAnimations))
                suitTrack.append(Func(battle.lureSuit, suit))
                suitTrack.append(makeLured)
                if suit.getSuitStatusModifier('rushJob') == 2:
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'rushJob'))
                if hp > 0:
                    for headPart in suit.animatedHeadParts:
                        suitTrack.append(Func(headPart.loop, 'stun'))
                    suitTrack.append(__createSuitDamageTrack(battle, suit, hp, lure, trapProp, revived, died))
                    suitTrack.append(makeUnLured)
                    suitTrack.append(Func(suit.setDizzy, 0))
                    suitTrack.append(Func(suit.setSuitStatusEffect, 'dazed', modifier=1, turns=2))
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'trapped'))
                    if suit.hasSuitStatusEffect('sued'):
                        suitTrack.append(Func(suit.setSuitStatusEffect, 'sued', modifier=1, turns=4))
                tracks.append(suitTrack)
                tracks.append(lerpSuit(suit, suitDelay + 1.7, 0.7, reachPos, battle, trapProp))
        else:
            if not suit.isLured:
                tracks.append(MovieUtil.createSuitTeaseMultiTrack(suit, battle, 1.5))

    tracks.append(getSoundTrack('TL_hypnotize.ogg', delay=0.5, node=toon))
    return tracks


def __lureOneDollar(lure, npcs = []):
    dollarProp = '1dollar'
    return __createFishingPoleMultiTrack(lure, dollarProp, npcs=npcs)


def __lureSmallMagnet(lure, npcs = []):
    magnet = globalPropPool.getProp('small-magnet')
    texture = loader.loadTexture('phase_5/maps/gag_palette_3.png')
    texture2 = loader.loadTexture('phase_10/maps/cashbotHQExt_palette_2tmla_1.png')
    magnet.setTexture(texture, 1)
    magnet.find('**/lightning').hide()
    magnet.find('**/lightning').setTexture(texture2, 1)
    sizeTrack = Sequence(
        Func(magnet.find('**/lightning').setScale, 1, random.uniform(1, 1.5), 1))
    sizeTrack2 = Sequence(
        Func(magnet.find('**/lightning').setScale, 1, random.uniform(.5, 1), 1))
    sizeTrack3 = Sequence(
        Func(magnet.find('**/lightning').setScale, 1, random.uniform(1.5, 2), 1))
    sizeTrack4 = Sequence(
        Func(magnet.find('**/lightning').setScale, 1, 1, 1))
    flickerTrack = Sequence(Wait(0.05), Func(sizeTrack.loop), Func(magnet.find('**/lightning').show), Wait(0.075),
                            Func(sizeTrack.finish), Func(magnet.find('**/lightning').hide),
                            Wait(0.05), Func(sizeTrack2.loop), Func(magnet.find('**/lightning').show), Wait(0.075),
                            Func(sizeTrack2.finish), Func(magnet.find('**/lightning').hide),
                            Wait(0.05), Func(sizeTrack3.loop), Func(magnet.find('**/lightning').show), Wait(0.075),
                            Func(sizeTrack3.finish), Func(magnet.find('**/lightning').hide),
                            Wait(0.05), Func(sizeTrack4.loop), Func(magnet.find('**/lightning').show), Wait(0.075),
                            Func(sizeTrack4.finish), Func(magnet.find('**/lightning').hide))
    lightningTrack = Sequence(Wait(2.6), Func(flickerTrack.loop), Wait(3.7), Func(flickerTrack.finish))
    pos = Point3(-0.27, 0.08, 0.29)
    hpr = Point3(-90.0, 84.17, -180)
    scale = Point3(0.75, 0.75, 0.75)
    return Parallel(lightningTrack, __createMagnetMultiTrack(lure, magnet, pos, hpr, scale, isSmallMagnet=1, npcs=npcs))


def __lureFiveDollar(lure, npcs = []):
    dollarProp = '5dollar'
    return __createFishingPoleMultiTrack(lure, dollarProp, npcs=npcs)


def __lureLargeMagnet(lure, npcs = []):
    magnet = globalPropPool.getProp('big-magnet')
    magnet.find('**/lightning').hide()
    sizeTrack = Sequence(
        Func(magnet.find('**/lightning').setScale, 1, random.uniform(1, 1.5), 1))
    sizeTrack2 = Sequence(
        Func(magnet.find('**/lightning').setScale, 1, random.uniform(.5, 1), 1))
    sizeTrack3 = Sequence(
        Func(magnet.find('**/lightning').setScale, 1, random.uniform(1.5, 2), 1))
    sizeTrack4 = Sequence(
        Func(magnet.find('**/lightning').setScale, 1, 1, 1))
    flickerTrack = Sequence(Wait(0.025), Func(sizeTrack.loop), Func(magnet.find('**/lightning').show), Wait(0.1),Func(sizeTrack.finish), Func(magnet.find('**/lightning').hide),
                            Wait(0.025), Func(sizeTrack2.loop), Func(magnet.find('**/lightning').show), Wait(0.1),Func(sizeTrack2.finish), Func(magnet.find('**/lightning').hide),
                            Wait(0.025), Func(sizeTrack3.loop), Func(magnet.find('**/lightning').show), Wait(0.1),Func(sizeTrack3.finish), Func(magnet.find('**/lightning').hide),
                            Wait(0.025), Func(sizeTrack4.loop), Func(magnet.find('**/lightning').show), Wait(0.1),Func(sizeTrack4.finish), Func(magnet.find('**/lightning').hide))
    lightningTrack = Sequence(Wait(2.6), Func(flickerTrack.loop), Wait(3.7), Func(flickerTrack.finish))
    pos = Point3(-0.27, 0.08, 0.29)
    hpr = Point3(-90.0, 84.17, -180)
    scale = Point3(1.32, 1.32, 1.32)
    return Parallel(lightningTrack, __createMagnetMultiTrack(lure, magnet, pos, hpr, scale, isSmallMagnet=0, npcs=npcs))


def __lureTenDollar(lure, npcs = []):
    dollarProp = '10dollar'
    return __createFishingPoleMultiTrack(lure, dollarProp, npcs=npcs)


def __lureHypnotize(lure, npcs = []):
    return __createHypnoGogglesMultiTrack(lure, npcs)


def __lureFiftyDollar(lure, npcs = []):
    dollarProp = '50dollar'
    return __createFishingPoleMultiTrack(lure, dollarProp, npcs=npcs)


def __lureSlideshow(lure, npcs):
    return __createSlideshowMultiTrack(lure, npcs)


def showDazeRounds(suit):
    suit.showHpTextWhite("DAZED!")


def __createSuitDamageTrack(battle, suit, hp, lure, trapProp, revived=0, died=0):
    if (trapProp is None) or trapProp.isEmpty():
        return Func(suit.loop, 'lured')
    toon = lure['toon']
    trapProp.wrtReparentTo(battle)
    trapTrack = ToontownBattleGlobals.TRAP_TRACK
    trapLevel = suit.battleTrap
    trapTrackNames = ToontownBattleGlobals.AvProps[trapTrack]
    trapName = trapTrackNames[trapLevel]
    result = Sequence()
    suitGone = 0
    pacesetterSpecialDeath = bool(died) and suit.dna.name == 'psetter'
    suitStartPos = suit.getPos()

    def reparentTrap(trapProp = trapProp, battle = battle):
        if trapProp and not trapProp.isEmpty():
            trapProp.wrtReparentTo(battle)

    result.append(Func(reparentTrap))
    parent = battle
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    if suit.battleTrapIsFresh:
        if trapName == 'quicksand' or trapName == 'trapdoor':
            trapProp.hide()
            trapProp.reparentTo(suit)
            trapProp.setPos(Point3(0, MovieUtil.SUIT_TRAP_DISTANCE, 0))
            trapProp.setHpr(Point3(0, 0, 0))
            trapProp.wrtReparentTo(battle)
        elif trapName == 'xspot':
            trapProp.hide()
            trapProp.reparentTo(suit)
            trapProp.setScale(Point3(2, 2, 2))
            trapProp.setPos(Point3(0, MovieUtil.SUIT_TRAP_DISTANCE, 0))
            trapProp.setHpr(Point3(0, 0, 0))
            trapProp.wrtReparentTo(battle)
        elif trapName == 'rake':
            trapProp.hide()
            trapProp.reparentTo(suit)
            trapProp.setPos(0, MovieUtil.SUIT_TRAP_RAKE_DISTANCE, 0)
            trapProp.setHpr(Point3(0, 270, 0))
            trapProp.setScale(Point3(0.7, 0.7, 0.7))
            rakeOffset = MovieUtil.getSuitRakeOffset(suit)
            trapProp.setY(trapProp.getY() + rakeOffset)
        elif trapName == 'spring':
            trapProp.hide()
            trapProp.reparentTo(suit)
            trapProp.setPos(0, MovieUtil.SUIT_TRAP_RAKE_DISTANCE, -.5)
            trapProp.setHpr(Point3(0, 0, 0))
            trapProp.setScale(Point3(1, 1, 1))
            rakeOffset = MovieUtil.getSuitRakeOffset(suit)
            trapProp.setY(trapProp.getY() + rakeOffset)
        else:
            parent = render
    if trapName == 'banana':
        totalDamage = hp

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)
        slidePos = trapProp.getPos(parent)
        slidePos.setY(slidePos.getY() - 5.1)
        moveTrack = Sequence(Wait(0.1), LerpPosInterval(trapProp, 0.1, slidePos, other=battle))
        animTrack = Sequence(ActorInterval(trapProp, 'banana', startTime=3.1), Wait(1.1), LerpScaleInterval(trapProp, 1, Point3(0.01, 0.01, 0.01)), Func(MovieUtil.removeProp, trapProp))
        suitTrack = Sequence()
        suitTrack.append(ActorInterval(suit, 'slip-backward'))
        damageTrack = Sequence(Wait(0.5), Func(suit.showHpTextNew, -hp, text="DAZED!", colorCode=1), Func(suit.updateHealthBar, hp))
        if random.random() <= 0.01:
            soundTrack = Sequence(Parallel(SoundInterval(globalBattleSoundCache.getSound('AA_pie_throw_only.ogg'), node=suit), Func(base.playSfx, globalBattleSoundCache.getSound('AA_WHATAREYOUDOING.ogg'))), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        else:
            soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('AA_pie_throw_only.ogg'), node=suit), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        suitTrack.append(Func(suit.setNeutralAnimationTrap))
        suit.setPendingQueuedLured(False)
        result.append(Parallel(moveTrack, animTrack, suitTrack, damageTrack, soundTrack))
    elif trapName == 'rake' or trapName == 'rake-react':
        totalDamage = hp

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)
        hpr = trapProp.getHpr(parent)
        upHpr = Vec3(hpr[0], 179.9999, hpr[2])
        bounce1Hpr = Vec3(hpr[0], 120, hpr[2])
        bounce2Hpr = Vec3(hpr[0], 100, hpr[2])
        rakeTrack = Sequence(Wait(0.5), LerpHprInterval(trapProp, 0.1, upHpr, startHpr=hpr), Wait(0.7), LerpHprInterval(trapProp, 0.4, hpr, startHpr=upHpr), LerpHprInterval(trapProp, 0.15, bounce1Hpr, startHpr=hpr), LerpHprInterval(trapProp, 0.05, hpr, startHpr=bounce1Hpr), LerpHprInterval(trapProp, 0.15, bounce2Hpr, startHpr=hpr), LerpHprInterval(trapProp, 0.05, hpr, startHpr=bounce2Hpr), Wait(0.2), LerpScaleInterval(trapProp, 0.2, Point3(0.01, 0.01, 0.01)), Func(MovieUtil.removeProp, trapProp))
        rakeAnimDuration = 3.125
        suitTrack = Sequence()
        suitTrack.append(ActorInterval(suit, 'rake-react', duration=rakeAnimDuration))
        damageTrack = Sequence(Wait(0.5), Func(suit.showHpTextNew, -hp, text="DAZED!", colorCode=1), Func(suit.updateHealthBar, hp))
        soundTrack = getSoundTrack('TL_step_on_rake.ogg', delay=0.6, node=suit)
        suitTrack.append(Func(suit.setNeutralAnimationTrap))
        suit.setPendingQueuedLured(False)
        result.append(Parallel(rakeTrack, suitTrack, damageTrack, soundTrack))
    elif trapName == 'marbles':
        totalDamage = hp

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)
        slidePos = trapProp.getPos(parent)
        slidePos.setY(slidePos.getY() - 6.5)
        moveTrack = Sequence(Wait(0.1), LerpPosInterval(trapProp, 0.8, slidePos, other=battle), Wait(1.1), LerpScaleInterval(trapProp, 1, Point3(0.01, 0.01, 0.01)), Func(MovieUtil.removeProp, trapProp))
        animTrack = ActorInterval(trapProp, 'marbles', startTime=3.1)
        suitTrack = Sequence()
        suitTrack.append(ActorInterval(suit, 'slip-backward'))
        damageTrack = Sequence(Wait(0.5), Func(suit.showHpTextNew, -hp, text="DAZED!", colorCode=1), Func(suit.updateHealthBar, hp))
        soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('AA_pie_throw_only.ogg'), duration=0.55, node=suit), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        suitTrack.append(Func(suit.setNeutralAnimationTrap))
        suit.setPendingQueuedLured(False)
        result.append(Parallel(moveTrack, animTrack, suitTrack, damageTrack, soundTrack))
    elif trapName == 'quicksand':
        totalDamage = hp

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)
        sinkPos1 = trapProp.getPos(battle)
        sinkPos2 = trapProp.getPos(battle)
        dropPos = trapProp.getPos(battle)
        landPos = trapProp.getPos(battle)
        sinkPos1.setZ(sinkPos1.getZ() - 3.1)
        sinkPos2.setZ(sinkPos2.getZ() - 9.1)
        dropPos.setZ(dropPos.getZ() + 40)
        landPos.setY(dropPos.getY() + 4)
        if base.config.GetBool('want-new-cogs', 0):
            nameTag = suit.find('**/def_nameTag')
        else:
            nameTag = suit.find('**/joint_nameTag')
        trapTrack = Sequence(Wait(2.4), LerpScaleInterval(trapProp, 0.8, Point3(0.01, 0.01, 0.01)), Func(MovieUtil.removeProp, trapProp))
        moveTrack = Sequence(Wait(0.9), LerpPosInterval(suit, 0.9, sinkPos1, other=battle), LerpPosInterval(suit, 0.4, sinkPos2, other=battle), Func(suit.setPos, battle, dropPos), Func(suit.wrtReparentTo, hidden), Wait(1.1))
        animTrack = Sequence(ActorInterval(suit, 'flail-qs', endTime=1.75), ActorInterval(suit, 'flail-qs', startTime=1.25, endTime=1.75), ActorInterval(suit, 'flail-qs', startTime=1.25, endTime=1.25), Wait(0.7))
        soundTrack = Sequence(Wait(0.7),
                              SoundInterval(globalBattleSoundCache.getSound('TL_quicksand.ogg'), node=suit))
        if died and not pacesetterSpecialDeath and not suit.isVirtual and not suit.hasSuitStatusEffect('overpressured') and suit.dna.name not in ('erfit', 'erclaim'):
            suitGone = 1
            damageTrack = Sequence(Wait(3.5), Func(suit.updateHealthBar, hp))
            damageTrack.append(Func(suit.makeDead))
            damageTrack.append(Func(suit.cleanupAllBattleEffects))
        else:
            moveTrack.append(Func(suit.wrtReparentTo, battle))
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            moveTrack.append(Parallel(LerpHprInterval(suit, 0.3, resetHpr, other=battle), LerpPosInterval(suit, 0.3, resetPos, other=battle)))
            damageTrack = Sequence(Wait(3.5), Func(suit.showHpTextNew, -hp, text="DAZED!", colorCode=1), Func(suit.updateHealthBar, hp))
            animTrack.append(ActorInterval(suit, 'slip-forward', playRate=1.25))
            soundTrack.append(Wait(0.25))
            soundTrack.append(SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
            animTrack.append(Func(suit.setNeutralAnimationTrap))
            suit.setPendingQueuedLured(False)
        result.append(Parallel(trapTrack, moveTrack, animTrack, damageTrack, soundTrack))
    elif trapName == 'spring':
        totalDamage = hp

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)
        sinkPos1 = trapProp.getPos(battle)
        sinkPos2 = trapProp.getPos(battle)
        sinkPos3 = trapProp.getPos(battle)
        dropPos = trapProp.getPos(battle)
        landPos = trapProp.getPos(battle)
        sinkPos1.setZ(sinkPos1.getZ() + 20)
        sinkPos2.setZ(sinkPos2.getZ() + 3)
        sinkPos3.setZ(sinkPos3.getZ() - 10)
        dropPos.setZ(dropPos.getZ() + 40)
        landPos.setY(dropPos.getY() + 4)
        if base.config.GetBool('want-new-cogs', 0):
            nameTag = suit.find('**/def_nameTag')
        else:
            nameTag = suit.find('**/joint_nameTag')
        trapTrack = Sequence(Wait(1.25), LerpPosInterval(trapProp, 0.25, sinkPos2), Wait(1.0), LerpPosInterval(trapProp, 0.25, sinkPos3), Func(MovieUtil.removeProp, trapProp))
        moveTrack = Sequence(Wait(1.25), LerpPosInterval(suit, 0.25, sinkPos1, other=battle), Func(suit.setPos, battle, dropPos), Func(suit.wrtReparentTo, hidden), Wait(1.1))
        animTrack = Sequence(ActorInterval(suit, 'flail-qs', endTime=1.375), Wait(1.1))
        soundTrack = Sequence(Wait(1.25),
                              SoundInterval(globalBattleSoundCache.getSound('AA_spring_activate.ogg'), node=suit))
        if died and not pacesetterSpecialDeath and not suit.isVirtual and not suit.hasSuitStatusEffect('overpressured') and suit.dna.name not in ('erfit', 'erclaim'):
            suitGone = 1
            damageTrack = Sequence(Wait(2.75), Func(suit.updateHealthBar, hp))
            damageTrack.append(Func(suit.makeDead))
            damageTrack.append(Func(suit.cleanupAllBattleEffects))
        else:
            moveTrack.append(Func(suit.wrtReparentTo, battle))
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            moveTrack.append(Parallel(LerpHprInterval(suit, 0.3, resetHpr, other=battle), LerpPosInterval(suit, 0.3, resetPos, other=battle)))
            damageTrack = Sequence(Wait(2.75), Func(suit.showHpTextNew, -hp, text="DAZED!", colorCode=1), Func(suit.updateHealthBar, hp))
            animTrack.append(ActorInterval(suit, 'slip-forward', playRate=1.25))
            soundTrack.append(Wait(0.375))
            soundTrack.append(SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
            animTrack.append(Func(suit.setNeutralAnimationTrap))
            suit.setPendingQueuedLured(False)
        result.append(Parallel(trapTrack, moveTrack, animTrack, damageTrack, soundTrack))
    elif trapName == 'trapdoor':
        totalDamage = hp

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)
        sinkPos = trapProp.getPos(battle)
        dropPos = trapProp.getPos(battle)
        landPos = trapProp.getPos(battle)
        sinkPos.setZ(sinkPos.getZ() - 9.1)
        dropPos.setZ(dropPos.getZ() + 40)
        landPos.setY(dropPos.getY() + 4)
        trapTrack = Sequence(Wait(2.4), LerpScaleInterval(trapProp, 0.8, Point3(0.01, 0.01, 0.01)), Func(MovieUtil.removeProp, trapProp))
        moveTrack = Sequence(Wait(2.2), LerpPosInterval(suit, 0.4, sinkPos, other=battle), Func(suit.setPos, battle, dropPos), Func(suit.wrtReparentTo, hidden), Wait(1.1))
        animTrack = Sequence(getSplicedLerpAnimsTrack(suit, 'flail-qs', 0.7, 0.25),
                             Func(trapProp.setColor, Vec4(0, 0, 0, 1)),
                             ActorInterval(suit, 'flail-qs', startTime=0.7, endTime=0),
                             ActorInterval(suit, 'lured', duration=0.5), ActorInterval(suit, 'flail-qs', startTime=1.1, endTime=1.375))
        soundTrack = Sequence(Wait(0.8), SoundInterval(globalBattleSoundCache.getSound('TL_trap_door.ogg'), node=suit))
        if died and not pacesetterSpecialDeath and not suit.isVirtual and not suit.hasSuitStatusEffect('overpressured') and suit.dna.name not in ('erfit', 'erclaim'):
            suitGone = 1
            damageTrack = Sequence(Wait(3.5), Func(suit.updateHealthBar, hp))
            damageTrack.append(Func(suit.makeDead))
            damageTrack.append(Func(suit.cleanupAllBattleEffects))
        else:
            moveTrack.append(Func(suit.wrtReparentTo, battle))
            moveTrack.append(Parallel(LerpHprInterval(suit, 0.3, resetHpr, other=battle), LerpPosInterval(suit, 0.3, resetPos, other=battle)))
            animTrack.append(Wait(1.0))
            suitPos, suitHpr = battle.getActorPosHpr(suit)
            animTrack.append(ActorInterval(suit, 'slip-forward', playRate=1.25))
            animTrack.append(Func(suit.setNeutralAnimationTrap))
            suit.setPendingQueuedLured(False)
            damageTrack = Sequence(Wait(3.5), Func(suit.showHpTextNew, -hp, text="DAZED!", colorCode=1), Func(suit.updateHealthBar, hp))
            soundTrack.append(Wait(0.5))
            soundTrack.append(SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        result.append(Parallel(trapTrack, moveTrack, animTrack, damageTrack, soundTrack))
    elif trapName == 'xspot':
        totalDamage = hp

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)
        ballPropTrack = Sequence()
        suitPos = trapProp.getPos(battle)
        y = suitPos.getY()
        ballPosPoints = [Point3(suitPos.getX(), y - 4, 21.0), VBase3(0, -90, 0)]
        ball = loader.loadModel('phase_5/models/char/wreckingball-ball')
        ballPropTrack.append(Func(battle.movie.needRestoreRenderProp, ball))
        #ballPropTrack.append(Func(ball.wrtReparentTo, render))
        targetPoint = battle.getActorPosHpr(suit)
        ballPropTrack.append(Wait(.425))
        ballPropTrack.append(getPropAppearTrack(ball, battle, ballPosPoints, 0, Point3(1, 1, 1), scaleUpTime=0))
        ballPropTrack.append(LerpHprInterval(ball, 0.75, VBase3(0, 0, 0)))
        ballPropTrack.append(Parallel(Sequence(Wait(.375), LerpColorScaleInterval(ball, 0.375, (1, 1, 1, 0), blendType='easeInOut')), LerpHprInterval(ball, 0.75, VBase3(0, 90, 0))))
        #ballPropTrack.append(Func(battle.movie.clearRenderProp, trapProp))
        ballPropTrack.append(Func(ball.removeNode))
        sinkPos = trapProp.getPos(battle)
        dropPos = trapProp.getPos(battle)
        landPos = battle.getActorPosHpr(suit)
        sinkPos.setZ(sinkPos.getZ() + 15)
        sinkPos.setY(sinkPos.getY() + 12.5)
        dropPos.setZ(dropPos.getZ() + 40)
        #landPos.setY(dropPos.getY() + 4)
        if died and not pacesetterSpecialDeath and not suit.isVirtual and not suit.hasSuitStatusEffect('overpressured') and suit.dna.name not in ('erfit', 'erclaim'):
            suitGone = 1
            damageTrack = Sequence(Wait(2.5), Func(suit.updateHealthBar, hp))
            damageTrack.append(Func(suit.makeDead))
            animTrack = Sequence(ActorInterval(suit, 'lured', endTime=.75),
                                     ActorInterval(suit, 'flail-wb', startTime=1, endTime=1.35))
            animTrack.append(MovieUtil.createSuitWreckingDeathTrack(suit, battle))
            trapTrack = Sequence(Wait(3.4), LerpScaleInterval(trapProp, 0.8, Point3(0.01, 0.01, 0.01)),
                                 Func(MovieUtil.removeProp, trapProp))
            result.append(Parallel(animTrack, trapTrack, damageTrack, ballPropTrack))
            suitIndex = battle.activeSuits.index(suit)

        else:
            trapTrack = Sequence(Wait(2.4), LerpScaleInterval(trapProp, 0.8, Point3(0.01, 0.01, 0.01)), Func(MovieUtil.removeProp, trapProp))
            moveTrack = Sequence(Wait(1.25), Parallel(Sequence(Wait(.125), Func(suit.setTransparency, 1),
                        LerpColorScaleInterval(suit, 0.375, (1, 1, 1, 0)),
                        Func(suit.setColorScale, (1, 1, 1, 1)), Func(suit.clearTransparency)), LerpPosInterval(suit, 0.5, sinkPos, other=battle)),
                                 Func(suit.setPos, battle, dropPos), Func(suit.wrtReparentTo, hidden), Wait(1.6))
            soundTrack = Sequence(Wait(1.2),
                                  SoundInterval(globalBattleSoundCache.getSound('AA_trap_wreckingball_nonfatal.ogg'),
                                                node=suit))
            moveTrack.append(Func(suit.wrtReparentTo, battle))
            moveTrack.append(Parallel(LerpHprInterval(suit, 0.3, resetHpr, other=battle), LerpPosInterval(suit, 0.3, resetPos, other=battle)))
            animTrack = Sequence(ActorInterval(suit, 'lured', endTime=.75),
                                     ActorInterval(suit, 'flail-wb', startTime=1))
            animTrack.append(Wait(1.25))
            animTrack.append(ActorInterval(suit, 'slip-forward', playRate=1.25))
            animTrack.append(Func(suit.setNeutralAnimationTrap))
            suit.setPendingQueuedLured(False)
            damageTrack = Sequence(Wait(2.5), Func(suit.showHpTextNew, -hp, text="DAZED!", colorCode=1), Func(suit.updateHealthBar, hp))
            soundTrack.append(Wait(1))
            soundTrack.append(SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
            result.append(Parallel(trapTrack, moveTrack, animTrack, damageTrack, soundTrack, ballPropTrack))
    elif trapName == 'tnt':
        totalDamage = hp

        # add to queued damage BEFORE building interval
        suit.addPendingQueuedDamage(totalDamage)
        tntTrack = ActorInterval(trapProp, 'tnt')
        explosionTrack = Sequence(Wait(2.3), createTNTExplosionTrack(battle, trapProp=trapProp, relativeTo=parent))
        origPos, _ = battle.getActorPosHpr(suit)
        flyPos = Point3(*origPos)
        flyPos.setZ(suit.getZ() + 4)
        dropPos = suit.getPos()
        oldCamera = base.camera.getPos()
        oldHPR = base.camera.getHpr()
        
        # Cog looks down and up
        suitTrack = Sequence()
        suitTrack.append(ActorInterval(suit, 'tnt-react', endTime=2))
        
        if base.localAvatar in battle.activeToons:
            if not died or pacesetterSpecialDeath:
                suitTrack.append(Sequence(
                Wait(0.1),
                Parallel(
                    LerpPosInterval(suit, 0.5, flyPos, other=battle, blendType='easeOut'),
                    ActorInterval(suit, 'slip-backward', duration=0.1),
                    Func(battle.movie.needRestoreColor),
                    Sequence(
                        Wait(0.1),
                        Func(suit.setColorScale, Vec4(0.2, 0.2, 0.2, 1)),
                        Func(trapProp.reparentTo, hidden),
                    ),
                ),
                Parallel(
                    LerpPosInterval(suit, 0.5, origPos, other=battle, blendType='easeIn'),
                    ActorInterval(suit, 'slip-backward', startTime=0.1)
                ),
                Func(suit.setColorScale, Vec4(1, 1, 1, 1)),
                Func(trapProp.sparksEffect.cleanup),
                Func(battle.movie.clearRestoreColor)
            ))
        else:
            suitTrack.append(Sequence(
                Wait(0.1),
                Parallel(
                    LerpPosInterval(suit, 0.5, flyPos, other=battle, blendType='easeOut'),
                    ActorInterval(suit, 'slip-backward', duration=0.1),
                    Func(battle.movie.needRestoreColor),
                    Sequence(
                        Wait(0.1),
                        Func(suit.setColorScale, Vec4(0.2, 0.2, 0.2, 1)),
                        Func(trapProp.reparentTo, hidden),
                    ),
                ),
                Parallel(
                    LerpPosInterval(suit, 0.5, origPos, other=battle, blendType='easeIn'),
                    ActorInterval(suit, 'slip-backward', startTime=0.1)
                ),
                Func(suit.setColorScale, Vec4(1, 1, 1, 1)),
                Func(trapProp.sparksEffect.cleanup),
                Func(battle.movie.clearRestoreColor)
            ))
        if died and not pacesetterSpecialDeath and not suit.isVirtual and not suit.hasSuitStatusEffect('overpressured') and suit.dna.name not in ('erfit', 'erclaim'):
            suitGone = 1
            damageTrack = Sequence(Wait(2.4), Func(suit.showHpTextNew, -hp, colorCode=1), Func(suit.updateHealthBar, hp), MovieUtil.midairSuitExplodeTrack(suit, battle))
            explosionSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
            soundTrack = Sequence(
                SoundInterval(globalBattleSoundCache.getSound('TL_dynamite.ogg'), duration=2.0, node=suit),
                SoundInterval(explosionSound, duration=0.6, node=suit)
            )
        else:
            pass

            damageTrack = Sequence(Wait(2.3), Func(suit.showHpTextNew, -hp, text="DAZED!", colorCode=1), Func(suit.updateHealthBar, hp))
            explosionSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
            soundTrack = Sequence(
                SoundInterval(globalBattleSoundCache.getSound('TL_dynamite.ogg'), duration=2.0, node=suit),
                SoundInterval(explosionSound, duration=0.6, node=suit)
            )
        result.append(Parallel(tntTrack, suitTrack, damageTrack, explosionTrack, soundTrack))
    elif trapName == 'traintrack':
        result.append(createIncomingTrainInterval(battle, suit, hp, lure, trapProp))
        result.append(Func(MovieUtil.removeProp, trapProp))
        result.append(Func(battle.unlureSuit, suit))
        result.append(Func(suit.setDizzy, 0))
        result.append(Func(suit.loop, 'neutral'))
        if died and not pacesetterSpecialDeath:
            suitGone = 1
            #result.append(createIncomingTrainInterval(battle, suit, hp, lure, trapProp))
            result.append(MovieUtil.createSuitCrashTrack(suit))
            result.append(Func(MovieUtil.removeProp, trapProp))

    if suitGone and trapName == 'tnt':
        #result.append(MovieUtil.createSuitCrashTrack(suit, battle))
        pass
    else:
        result.append(Func(battle.unlureSuit, suit))
        result.append(Func(suit.setDizzy, 0))
        #result.append(MovieUtil.createSuitResetPosTrack(suit, battle))
        #result.append(Func(suit.setNeutralAnimationTrap))
        suit.setPendingQueuedLured(False)
        if suit.dna.name == 'redd' and revived != 0:
            result.append(MovieUtil.createSuitReviveRedd(suit, battle))
        elif suit.dna.name == 'erfit' and revived != 0:
            result.append(MovieUtil.createErfitReviveTrack(suit, battle))
        elif revived != 0 and suit.isSkeleton:
            result.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
        elif revived != 0 and not suit.isSkeleton and suit.dna.name != 'redd':
            result.append(MovieUtil.createSuitReviveTrack(suit, battle))
        elif died != 0 and suit.isVirtual and not suit.hasSuitStatusEffect('overpressured'):
            result.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
        elif died != 0 and not suit.isVirtual and not suitGone and not suit.hasSuitStatusEffect('overpressured'):
            result.append(MovieUtil.createSuitDeathTrack(suit, battle))
        else:
            result.append(Func(suit.setNeutralAnimationTrap))
    return result

def __ScapegoatAbsorb(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].isShielding:
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].addAbsorbDamage, suits[suitIndex], int(hp * 0.45)))
        suitTrack.append(showDamage)
        return suitTrack
    else:
        return Sequence()


def __createSuitResetPosTrack(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    updateTrack = Parallel(Func(suit.setChatAbsolute,
                                '',
                                CFSpeech | CFTimeout))
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.loop, 'neutral'))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, updateTrack, moveTrack)
	
def midairSuitExplodeTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    suitPos.setZ(suitPos.getZ() + 17)
    suitTrack.append(Wait(0.15))
    suitTrack.append(Func(MovieUtil.avatarHide, suit))
    deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
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

    return Parallel(suitTrack, explosionTrack, deathSoundTrack, gears1Track, gears2MTrack, Wait(4.5))


def getSplicedLerpAnimsTrack(object, animName, origDuration, newDuration, startTime = 0, fps = 30):
    track = Sequence()
    addition = 0
    numIvals = origDuration * fps
    timeInterval = newDuration / numIvals
    animInterval = origDuration / numIvals
    for i in xrange(0, int(numIvals)):
        track.append(Wait(timeInterval))
        track.append(ActorInterval(object, animName, startTime=startTime + addition, duration=animInterval))
        addition += animInterval

    return track


def lerpSuit(suit, delay, duration, reachPos, battle, trapProp, blendType='noBlend'):
    track = Sequence()
    if trapProp:
        track.append(Func(safeWrtReparentTo, trapProp, battle))
    track.append(Wait(delay))
    track.append(LerpPosInterval(suit, duration, reachPos, other=battle, blendType=blendType))
    if trapProp:
        track.append(Func(safeWrtReparentTo, trapProp, suit))
        suit.battleTrapProp = trapProp
    return track


def createTNTExplosionTrack(parent, explosionPoint = None, trapProp = None, relativeTo = render):
    explosionTrack = Sequence(Func(trapProp.hide))
    explosion = BattleProps.globalPropPool.getProp('kapow')
    explosion.setBillboardPointEye()
    if not explosionPoint:
        if trapProp:
            explosionPoint = trapProp.getPos(relativeTo)
            explosionPoint.setZ(explosionPoint.getZ() + 2.3)
        else:
            explosionPoint = Point3(0, 3.6, 2.1)
    explosionTrack.append(Func(explosion.reparentTo, parent))
    explosionTrack.append(Func(explosion.setPos, explosionPoint))
    explosionTrack.append(Func(explosion.setScale, 0.11))
    explosionTrack.append(ActorInterval(explosion, 'kapow'))
    explosionTrack.append(Func(MovieUtil.removeProp, explosion))
    return explosionTrack


TRAIN_STARTING_X = -7.131
TRAIN_TUNNEL_END_X = 7.1
TRAIN_TRAVEL_DISTANCE = 45
TRAIN_SPEED = 35.0
TRAIN_DURATION = TRAIN_TRAVEL_DISTANCE / TRAIN_SPEED
TRAIN_MATERIALIZE_TIME = 4
TOTAL_TRAIN_TIME = TRAIN_DURATION + TRAIN_MATERIALIZE_TIME

def createSuitReactionToTrain(battle, suit, hp, lure, trapProp):
    head = suit.getHeadParts()[0]
    toon = lure['toon']
    retval = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    distance = suitPos.getX() - TRAIN_STARTING_X
    timeToGetHit = distance / TRAIN_SPEED
    suitTrack = Sequence()
    showDamage = Func(suit.showHpText, -hp, openEnded=0)
    updateHealthBar = Func(suit.updateHealthBar, hp)
    anim = 'flatten'
    suitReact = ActorInterval(suit, anim)
    cogGettingHit = getSoundTrack('TL_train_cog.ogg', node=toon)
    suitTrack.append(Func(suit.loop, 'neutral'))
    suitTrack.append(Parallel(Sequence(Wait(timeToGetHit-2), Func(suit.setChatAbsolute, 'Uh Oh...', CFSpeech | CFTimeout)), Sequence(LerpHprInterval(head, 1, (-60, 0, 0)), Wait(1), LerpHprInterval(head, 1, (0, 0, 0))), Wait(timeToGetHit + TRAIN_MATERIALIZE_TIME)))
    suitTrack.append(updateHealthBar)
    suitTrack.append(Parallel(suitReact, cogGettingHit))
    suitTrack.append(showDamage)
    curDuration = suitTrack.getDuration()
    timeTillEnd = TOTAL_TRAIN_TIME - curDuration
    if timeTillEnd > 0:
        suitTrack.append(Wait(timeTillEnd))
    retval.append(suitTrack)
    return retval


def createIncomingTrainInterval(battle, suit, hp, lure, trapProp):
    toon = lure['toon']
    retval = Parallel()
    suitTrack = createSuitReactionToTrain(battle, suit, hp, lure, trapProp)
    retval.append(suitTrack)
    if not trapProp.find('**/train_gag').isEmpty():
        return retval
    clipper = PlaneNode('clipper')
    clipper.setPlane(Plane(Vec3(1, 0, 0), Point3(TRAIN_STARTING_X, 0, 0)))
    clipNP = trapProp.attachNewNode(clipper)
    trapProp.setClipPlane(clipNP)
    clipper2 = PlaneNode('clipper2')
    clipper2.setPlane(Plane(Vec3(-1, 0, 0), Point3(TRAIN_TUNNEL_END_X, 0, 0)))
    clipNP2 = trapProp.attachNewNode(clipper2)
    trapProp.setClipPlane(clipNP2)
    train = globalPropPool.getProp('train')
    train.hide()
    train.reparentTo(trapProp)
    tempScale = trapProp.getScale()
    trainScale = Vec3(1.0 / tempScale[0], 1.0 / tempScale[1], 1.0 / tempScale[2])
    trainIval = Sequence()
    trainIval.append(Func(train.setScale, trainScale))
    trainIval.append(Func(train.setH, 90))
    trainIval.append(Func(train.setX, TRAIN_STARTING_X))
    trainIval.append(Func(train.setTransparency, 1))
    trainIval.append(Func(train.setColorScale, Point4(1, 1, 1, 0)))
    trainIval.append(Func(train.show))
    tunnel2 = trapProp.find('**/tunnel3')
    tunnel3 = trapProp.find('**/tunnel2')
    tunnels = [tunnel2, tunnel3]
    for tunnel in tunnels:
        trainIval.append(Func(tunnel.setTransparency, 1))
        trainIval.append(Func(tunnel.setColorScale, Point4(1, 1, 1, 0)))
        trainIval.append(Func(tunnel.setScale, Point3(1.0, 0.01, 0.01)))
        trainIval.append(Func(tunnel.show))

    materializeIval = Parallel()
    materializeIval.append(LerpColorScaleInterval(train, TRAIN_MATERIALIZE_TIME, Point4(1, 1, 1, 1)))
    for tunnel in tunnels:
        materializeIval.append(LerpColorScaleInterval(tunnel, TRAIN_MATERIALIZE_TIME, Point4(1, 1, 1, 1)))

    for tunnel in tunnels:
        tunnelScaleIval = Sequence()
        tunnelScaleIval.append(LerpScaleInterval(tunnel, TRAIN_MATERIALIZE_TIME - 1.0, Point3(1.0, 2.0, 2.5)))
        tunnelScaleIval.append(LerpScaleInterval(tunnel, 0.5, Point3(1.0, 3.0, 1.5)))
        tunnelScaleIval.append(LerpScaleInterval(tunnel, 0.5, Point3(1.0, 2.5, 2.0)))
        materializeIval.append(tunnelScaleIval)

    trainIval.append(materializeIval)
    endingX = TRAIN_STARTING_X + TRAIN_TRAVEL_DISTANCE
    trainIval.append(LerpPosInterval(train, TRAIN_DURATION, Point3(endingX, 0, 0), other=battle))
    trainIval.append(LerpColorScaleInterval(train, TRAIN_MATERIALIZE_TIME, Point4(1, 1, 1, 0)))
    retval.append(trainIval)
    trainSoundTrack = getSoundTrack('TL_train.ogg', node=toon)
    retval.append(trainSoundTrack)
    return retval


def __createSlideshowMultiTrack(lure, npcs = []):
    toon = lure['toon']
    battle = lure['battle']
    sidestep = lure['sidestep']
    origHpr = toon.getHpr(battle)
    slideshowDelay = 2.5
    hands = toon.getLeftHands()
    endPos = toon.getPos(battle)
    endPos.setY(endPos.getY() + 4)
    button = globalPropPool.getProp('lure-button')
    button2 = MovieUtil.copyProp(button)
    buttons = [button, button2]
    toonTrack = Sequence()
    toonTrack.append(Func(MovieUtil.showProps, buttons, hands))
    toonTrack.append(Func(toon.headsUp, battle, endPos))
    toonTrack.append(Parallel(ActorInterval(toon, 'pushbutton'), ActorInterval(button, 'lure-button')))
    toonTrack.append(Func(MovieUtil.removeProps, buttons))
    toonTrack.append(Func(toon.loop, 'neutral'))
    toonTrack.append(Func(toon.setHpr, battle, origHpr))
    slideShowProp = globalPropPool.getProp('slideshow')
    propTrack = Sequence()
    propTrack.append(Wait(slideshowDelay))
    propTrack.append(Func(slideShowProp.show))
    propTrack.append(Func(slideShowProp.setScale, Point3(0.1, 0.1, 0.1)))
    propTrack.append(Func(slideShowProp.reparentTo, battle))
    propTrack.append(Func(slideShowProp.setPos, endPos))
    propTrack.append(LerpScaleInterval(slideShowProp, 1.2, Point3(1.0, 1.0, 1.0)))
    shrinkDuration = 0.4
    totalDuration = 7.1
    propTrackDurationAtThisPoint = propTrack.getDuration()
    waitTime = totalDuration - propTrackDurationAtThisPoint - shrinkDuration
    if waitTime > 0:
        propTrack.append(Wait(waitTime))
    propTrack.append(LerpScaleInterval(nodePath=slideShowProp, scale=Point3(1.0, 1.0, 0.1), duration=shrinkDuration))
    propTrack.append(Func(MovieUtil.removeProp, slideShowProp))
    tracks = Parallel(propTrack, toonTrack)
    targets = lure['target']
    for target in targets:
        suit = target['suit']
        trapProp = suit.battleTrapProp
        if sidestep == 0:
            hp = target['hp']
            kbbonus = target['kbbonus']
            died = target['died']
            revived = target['revived']
            if kbbonus == 1 or hp > 0:
                suitTrack = Sequence()
                makeUnLured = Func(suit.clearSuitStatusEffect, 'lured')
                if toon.getTrackBonusLevel(LURE_TRACK) > 1:
                    if suit.getManager() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.getGovernaught() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.hasSuitStatusEffect('lureResist') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.currHP > (suit.maxHP * 1.5) and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=2)
                    elif suit.isVirtual:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] - 1)
                    elif suit.isSkeleton:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']])
                    else:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=2, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] + 1)
                else:
                    if suit.getManager() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.getGovernaught() and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.hasSuitStatusEffect('lureResist') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.hasSuitStatusEffect('insured') or suit.hasSuitStatusEffect('insured2') and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.currHP > (suit.maxHP * 1.5) and not trapProp:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=2)
                    elif suit.isVirtual:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] - 1)
                    elif suit.isSkeleton:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']])
                    else:
                        makeLured = Func(suit.setSuitStatusEffect, 'lured', modifier=1, turns=ToontownBattleGlobals.AvLureRounds[lure['level']] + 1)
                suitDelay = 3.8
                suitAnimDuration = 1.5
                opos, ohpr = battle.getActorPosHpr(suit)
                reachDist = MovieUtil.SUIT_LURE_DISTANCE
                reachPos = Point3(opos[0], opos[1] - reachDist, opos[2])
                suit.setPendingQueuedLured(True)
                if suit.dna.name in ('hrollers', 'mh2', 'std2', 'cnd2', 'videog', 'bcaster', 'director', 'fmaker', 'cinema', 'choreo'):
                    suitTrack.append(Func(suit.setNeutralAnimationRolled))
                    suitTrack.append(Func(suit.makeUnTrapped))
                else:
                    suitTrack.append(Func(suit.setNeutralAnimation))
                    suitTrack.append(Func(suit.makeUnTrapped))
                suitTrack.append(Wait(suitDelay))
                suitTrack.append(Func(showLureRounds, suit, battle, lure['level']))
                suitTrack.append(ActorInterval(suit, 'hypnotized'))
                suitTrack.append(Func(suit.setPos, battle, reachPos))
                suitTrack.append(Func(suit.setDizzy, 1))
                suitTrack.append(Func(suit.loopSyncedLuredAnimations))
                suitTrack.append(Func(battle.lureSuit, suit))
                suitTrack.append(makeLured)
                if suit.getSuitStatusModifier('rushJob') == 2:
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'rushJob'))
                if hp > 0:
                    for headPart in suit.animatedHeadParts:
                        suitTrack.append(Func(headPart.loop, 'stun'))
                    suitTrack.append(__createSuitDamageTrack(battle, suit, hp, lure, trapProp, revived, died))
                    suitTrack.append(makeUnLured)
                    suitTrack.append(Func(suit.setDizzy, 0))
                    suitTrack.append(Func(suit.setSuitStatusEffect, 'dazed', modifier=1, turns=2))
                    suitTrack.append(Func(suit.clearSuitStatusEffect, 'trapped'))
                    if suit.hasSuitStatusEffect('sued'):
                        suitTrack.append(Func(suit.setSuitStatusEffect, 'sued', modifier=1, turns=4))
                tracks.append(suitTrack)
                tracks.append(lerpSuit(suit, suitDelay + 1.7, 0.7, reachPos, battle, trapProp))
        else:
            if not suit.isLured:
                tracks.append(MovieUtil.createSuitTeaseMultiTrack(suit, battle, 3.3))

    tracks.append(getSoundTrack('TL_presentation.ogg', delay=2.3, node=toon))
    tracks.append(getSoundTrack('AA_drop_trigger_box.ogg', delay=slideshowDelay, node=toon))
    return tracks

def __showProp(prop, parent, pos, hpr = None, scale = None):
    prop.reparentTo(parent)
    prop.setPos(pos)
    if hpr:
        prop.setHpr(hpr)
    if scale:
        prop.setScale(scale)

def getPropTrack(prop, parent, posPoints, appearDelay, remainDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, scaleDownTime = 0.5, startScale = Point3(0.01), anim = 0, propName = 'none', animDuration = 0.0, animStartTime = 0.0):
    if anim == 1:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), ActorInterval(prop, propName, duration=animDuration, startTime=animStartTime), Wait(remainDelay), Func(MovieUtil.removeProp, prop))
    else:
        track = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints), LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale), Wait(remainDelay), LerpScaleInterval(prop, scaleDownTime, MovieUtil.PNT3_NEARZERO), Func(MovieUtil.removeProp, prop))
    return track

def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
    if poseExtraArgs:
        propTrack.append(Func(prop.pose, *poseExtraArgs))
    propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale))
    return propTrack
