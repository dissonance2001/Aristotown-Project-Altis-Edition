from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
from toontown.effects import DustCloud
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

def doThrowBookCog(attack, ind):
    theSuit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    targetSuit = battle.activeSuits[dmg]

    suitTracks = Parallel()
    suitTrack = Sequence()
    suitTrack.append(Wait(2.9))
    suitTrack.append(Parallel(ActorInterval(targetSuit, 'flatten', duration=.55), MovieUtil.createSuitCrashTrack(targetSuit, battle, 7)))
    suitTracks.append(suitTrack)
    posPoints = [Point3(-0.5, 0, 0), VBase3(0, 0, 180)]
    knifeTracks = Parallel()
    hitPoint = targetSuit.getPos(battle)
    hitPoint2 = targetSuit.getPos(battle)
    hitPoint2.setZ(targetSuit.height + 4)
    hitPoint.setY(hitPoint.getY() - .25)
    knife = globalPropPool.getProp('lawbook')
    knifeTrack = Sequence(
            getPropAppearTrack(knife, theSuit.getRightHand(), posPoints, .5, Point3(2.25, 2.25, 2.25),
                               scaleUpTime=0.1),
            Wait(1.5),
            Parallel(
                getThrowTrack(knife, Point3(0, 0, 0), 1.0, targetSuit, -100),
                LerpHprInterval(knife, 0.5, VBase3(0, 0, 0)), LerpScaleInterval(knife, 0, VBase3(8.5, 8.5, 8.5))), Sequence(Wait(1), LerpScaleInterval(knife, 0.5, VBase3(0, 0, 0))),
            Func(knife.removeNode)
        )
    knifeTracks.append(knifeTrack)
    hpTrack = Sequence(Wait(3), Func(targetSuit.checkHeadRoller2, theSuit, battle))
    soundTrack3 = getSoundTrack('LB_toonup.ogg', delay=3, node=theSuit)
    suitTrackAnim = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    soundTrack2 = getSoundTrack('AA_drop_bigweight_miss.ogg', delay=3, node=theSuit)
    multiTrack = Parallel(soundTrack2)
    return Parallel(suitTrackAnim, suitTracks, hpTrack, soundTrack3, multiTrack, knifeTracks)

def doPaperweight(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitDelay = 1.0
    propDelay = 0.1
    throwDuration = 2.0
    paper2 = loader.loadModel('phase_11/models/lawbotHQ/LB_paper_twist_stacks')
    paper = paper2.find('**/paper_stack_1')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    posPoints = [Point3(-0.5, -0.25, 0), VBase3(0, 0, 180)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        paperTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, propDelay, Point3(1, 1, 1), scaleUpTime=1.0))
        paperTrack.append(Wait(suitDelay))
        hitPoint = toon.getPos(battle)
        hitPoint.setX(hitPoint.getX() + 0)
        hitPoint.setY(hitPoint.getY() - .25)
        missPoint2 = toon.getPos(battle)
        missPoint2.setY(hitPoint.getY() - 7)
        movePoint = Point3(hitPoint.getX(), hitPoint.getY(), hitPoint.getZ() + 0.2)
        missPoint = Point3(missPoint2.getX(), missPoint2.getY(), missPoint2.getZ())
        paperTrack.append(Func(battle.movie.needRestoreRenderProp, paper))
        paperTrack.append(Func(paper.wrtReparentTo, battle))
        paperTrack.append(Parallel(Func(toon.setToonStatusEffect, 'cooldown', turns=3, mode='refreshTurns')))
        if dmg > 0:
            paperTrack.append(getThrowTrack(paper, hitPoint, duration=throwDuration, parent=battle, gravity=-100))
            paperTrack.append(Wait(0.6))
            paperTrack.append(LerpPosInterval(paper, 0.4, movePoint))
        else:
            paperTrack.append(getThrowTrack(paper, missPoint2, duration=throwDuration, parent=battle, gravity=-100))
            paperTrack.append(Wait(0.6))
            paperTrack.append(LerpPosInterval(paper, 0.4, missPoint))
        spinTrack = Sequence(Wait(propDelay + suitDelay + 0.7), LerpHprInterval(paper, throwDuration, Point3(-360, 360, 360)))
        sizeTrack = Sequence(Wait(propDelay + suitDelay + 0.7), LerpScaleInterval(paper, throwDuration, Point3(3, 3, 3)), Wait(0.95), LerpScaleInterval(paper, 0.75, MovieUtil.PNT3_NEARZERO))
        propTrack = Sequence(Parallel(paperTrack, spinTrack, sizeTrack), Func(paper.removeNode))
        propTracks.append(propTrack)

    damageAnims = []
    damageAnims.append(['cringe',
     0.01,
     0.21,
     0.08])
    damageAnims.append(['slip-forward',
     0.01,
     0.6,
     0.85])
    damageAnims.extend(getSplicedLerpAnims('slip-forward', 0.31, 0.95, startTime=1.2))
    damageAnims.append(['slip-forward', 0.01, 1.51])
    soundTrack = getSoundTrack('AA_drop_bigweight_miss.ogg', delay=propDelay + suitDelay + 0.7 + throwDuration, node=suit)
    toonTracks = getToonTracks(attack, damageDelay=4, splicedDamageAnims=damageAnims, dodgeDelay=1.5, dodgeAnimNames=['duck'], showDamageExtraTime=0.4, showMissedExtraTime=1.3)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack)

def doPaperRain(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    propTracks = Parallel()
    toonTracks = Parallel()
    smokeTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.8, 0.7, 0.5, 1)
        smoke.setBillboardPointEye()
        smokeTrack = Sequence(Wait(1.75), Func(smoke.reparentTo, toon),
                              Parallel(LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
                                       LerpColorScaleInterval(smoke, 1, Vec4(1, 1, 1, 0))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(smoke.removeNode))
        piano = loader.loadModel('phase_11/models/lawbotHQ/LB_filing_cabB')
        safe = loader.loadModel('phase_11/models/lawbotHQ/LB_filing_cabB')
        boulder = loader.loadModel('phase_11/models/lawbotHQ/LB_filing_cabB')
        weight = loader.loadModel('phase_11/models/lawbotHQ/LB_filing_cabB')
        toonPos = toon.getPos(battle)
        toonHpr = battle.getActorPosHpr(toon)
        y = toonPos.getY()
        propPos = Point3(toonPos.getX(), y, 30)
        soundTrack2 = getSoundTrack('AA_drop_safe.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack3 = getSoundTrack('AA_drop_safe.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack4 = getSoundTrack('AA_drop_safe.ogg', delay=1.75, duration=2.0, node=suit)
        soundTrack5 = getSoundTrack('AA_drop_safe.ogg', delay=1.75, duration=2.0, node=suit)
        propTrack = Sequence(Func(piano.reparentTo, battle),
                             getPropAppearTrack(piano, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                                                scaleUpPoint=Point3(1.5), scaleUpTime=1.5),
                             LerpPosInterval(piano, 0.25, Point3(toonPos.getX(), y, 1)),
                             LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 2)),
                             LerpPosInterval(piano, 0.1, Point3(toonPos.getX(), y, 1)), Sequence(
                Wait(1.5),
                LerpScaleInterval(piano, .25, MovieUtil.PNT3_ZERO)
            ))
        propTrack2 = Sequence(Func(safe.reparentTo, battle),
                              getPropAppearTrack(safe, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                                                 scaleUpPoint=Point3(1.5), scaleUpTime=1.5),
                              LerpPosInterval(safe, 0.25, Point3(toonPos.getX(), y, 0)),
                              LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 1)),
                              LerpPosInterval(safe, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(safe, .25, MovieUtil.PNT3_ZERO)
            ))
        propTrack3 = Sequence(Func(boulder.reparentTo, battle),
                              getPropAppearTrack(boulder, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                                                 scaleUpPoint=Point3(1.5), scaleUpTime=1.5),
                              LerpPosInterval(boulder, 0.25, Point3(toonPos.getX(), y, 0)),
                              LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 1)),
                              LerpPosInterval(boulder, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(boulder, .25, MovieUtil.PNT3_ZERO)
            ))
        propTrack4 = Sequence(Func(weight.reparentTo, battle),
                              getPropAppearTrack(weight, parent=battle, posPoints=[propPos, VBase3(0, 0, 0)], appearDelay=0.0,
                                                 scaleUpPoint=Point3(1.5), scaleUpTime=1.5),
                              LerpPosInterval(weight, 0.25, Point3(toonPos.getX(), y, 0)),
                              LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 1)),
                              LerpPosInterval(weight, 0.1, Point3(toonPos.getX(), y, 0)), Sequence(
                Wait(1.5),
                LerpScaleInterval(weight, .25, MovieUtil.PNT3_ZERO)
            ))
        if dmg > 0:
            propTracks.append(random.choice((Parallel(propTrack, soundTrack2), Parallel(propTrack2, soundTrack4), Parallel(propTrack3, soundTrack3), Parallel(propTrack4, soundTrack5))))
        toonTrack = Sequence(
            Wait(1.75),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpTextNew, -int(dmg), text="COOLDOWN!", colorCode=1),
                # Func(__doDamageCheat, toon, dmg, t['died'])
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
        if dmg > 0:
            toonTracks.append(toonTrack)
            smokeTracks.append(smokeTrack)
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    toonDamageTrack = getToonTracksCheat(attack, 1.75, ['nothing'], 0, ['neutral'])
    return Parallel(suitTrack, toonDamageTrack, smokeTracks, toonTracks, soundTrack, propTracks)

def doWhirlwind(attack):
    suit = attack['suit']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    battle = attack['battle']
    if suit.dna.name == 'clerk':
        suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    else:
        suitTrack = Sequence(getSuitTrack(attack))
    cagePropTracks = Parallel()
    # for t in attack['target']:
    # toon = t['toon']
    # dmg = t['hp']
    whirlSfx = loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_whirlwind.ogg')
    whirlSfx.setLoop(True)
    cage = loader.loadModel('phase_5/models/cogdominium/tt_m_ara_cfg_whirlwind')
    cagePosition = LerpHprInterval(cage, 0, Point3(180, 0, 0))
    # cage.setH(90)
    # cage.setPosHpr(0, 0, 0, 180, 0, 0)
    suitPos = suit.getPos(battle)
    toonPos = toon.getPos(battle)
    y = toonPos.getY()
    if dmg == 0:
        y -= 5
    cagePos = [Point3(suitPos.getX(), y + 15, suitPos.getZ()), toon.getHpr(battle)]
    spinTrack = Sequence(Func(whirlSfx.play), LerpHprInterval(cage, 5.5, Point3(-10800, 0, 0)), Func(whirlSfx.stop))
    cagePropTrack = Sequence(
        Parallel(cagePosition),
        Parallel(getPropAppearTrack(cage, battle, cagePos, 0.25, scaleUpPoint=Point3(2.0), scaleUpTime=1.0),
            cage.posInterval(0.75, Point3(toonPos.getX(), y, 0.1), blendType='easeIn'),
            SoundInterval(base.loader.loadSfx('phase_5/audio/sfx/tt_s_ara_cfg_toonInWhirlwind.ogg'), duration=0.75, node=cage), spinTrack,
        ),
        LerpFunctionInterval(cage.setAlphaScale, fromData=.5, toData=0, duration=0.5),
        Func(cage.removeNode)
    )
    cagePropTracks.append(cagePropTrack)
    damageAnims = [['slip-forward', 0.0001, 0.5]]
    damageAnims = []
    damageAnims.append(['duck',
                        0.01,
                        0.01,
                        1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.append(['slip-forward'])
    sinkPos = toon.getPos(battle)
    sinkPos.setZ(sinkPos.getZ() + 25)
    notifyTrack = Sequence(Wait(5.9), Func(toon.showHpTextNew, -int(dmg), text="CONFUSED!", colorCode=1), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
    toonTrack = getToonTrackCheat(attack, damageDelay=.9, splicedDamageAnims=damageAnims, dodgeDelay=0.91,
                             dodgeAnimNames=['sidestep'], showDamageExtraTime=5, showMissedExtraTime=1.0)
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'confused', turns=2)))
    toonSpinTrack = Sequence(Wait(0.9), LerpHprInterval(toon, 4.0, Point3(10800, 0, 0)),
                                 LerpHprInterval(toon, 0.5, toon.getHpr()), Wait(0.5))
    toonLiftTrack = Sequence(Wait(0.9), LerpPosInterval(toon, 4.5, Point3(toon.getX(), toon.getY(), toon.getZ() + 50)), LerpPosInterval(toon, 0.5, toon.getPos()), Wait(0.5))
    return Parallel(suitTrack, cagePropTracks, toonTrack, notifyTrack, toonLiftTrack, toonSpinTrack)

def doPeckingOrder(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDuration = 3.03
    throwDelay = 2
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    notifyTracks = Parallel()
    propDelay = 1.5
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            notifyTrack = Sequence(Wait(2.5),  Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
            notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'vulnerable', modifier=25, turns=3, mode='keepHighest')))
            notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'damageUp', modifier=25, turns=3, mode='keepHighest')))
            notifyTracks.append(notifyTrack)
        for i in xrange(0, numBirds):
            next = globalPropPool.getProp('bird')
            #next.setScale(0.01)
            #next.reparentTo(suit.getRightHand())
          #  next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
            toonPos = toon.getPos(battle)

            if dmg > 0:
                hitPoint = Point3(
                    toonPos[0] + (random.random() * 1.5 - 0.75),
                    toonPos[1] + (random.random() * 1.0 - 0.5),
                    toonPos[2] + toon.getHeight() * 0.5 + (random.random() * 1.0 - 0.5)
                )
            else:
                hitPoint = Point3(
                    toonPos[0] + (random.random() * 3.0 - 1.5),
                    toonPos[1] - 3.0 + (random.random() * 2.0 - 1.0),
                    toonPos[2] + toon.getHeight() * 0.5 + (random.random() * 2.0 - 1.0)
                )
            birdTrack = Sequence(Wait(throwDelay), Func(next.setScale, 0.01), Func(next.reparentTo, suit.getRightHand()),
                                 Func(next.setPos, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3), Func(battle.movie.needRestoreRenderProp, next),
                                 Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)),
                                 LerpPosInterval(next, 0.5, hitPoint))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.5, Point3(9, 9, 9)), LerpScaleInterval(next, .5, Point3(0, 0, 0)))
            birdTracks.append(Sequence(Parallel(birdTrack, scaleTrack), Func(next.removeNode)))
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0.14,
                        0.21])
    damageAnims.append(['cringe',
                        0.01,
                        0.14,
                        0.13])
    damageAnims.append(['cringe', 0.01, 0.43])
    toonTrack = getToonTracksCheat(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=0.75,
                              dodgeAnimNames=['duck'], showMissedExtraTime=1.1)
    soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
    return Parallel(suitTrack, toonTrack, notifyTracks, soundTrack, birdTracks)

def doSuppression(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    paper = globalPropPool.getProp('shredder-paper')
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    if suitType == 'a':
        posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
        scale = Point3(1.2, 1.2, 1.2)
    else:
        posPoints = [Point3(.78, -1.89, -.17), VBase3(10, 250, -10)]
        scale = Point3(1, 1, 1)
    propTrack = Sequence(
        getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.75, scale, scaleUpTime=0.25))
    propTrack.append(Wait(0.95))
    hitPoint = __toonFacePoint(toon, parent=battle)
    hitPoint.setX(hitPoint.getX() - 1.4)
    missPoint = __toonGroundPoint(attack, toon, 0.7, parent=battle)
    missPoint.setX(missPoint.getX() - 1.1)
    propTrack.append(getPropThrowTrack(attack, paper, [hitPoint], [missPoint], parent=battle))

    headParts = toon.getHeadParts()
    torsoParts = toon.getTorsoParts()
    legsParts = toon.getLegsParts()
    toonPos = toon.getPos(render)

    def hideParts(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.setTransparency, 1))
            track.append(LerpFunctionInterval(nextPart.setAlphaScale, fromData=1, toData=0, duration=0.2))

        return track

    def showParts(parts):
        track = Parallel()
        for partNum in range(0, parts.getNumPaths()):
            nextPart = parts.getPath(partNum)
            track.append(Func(nextPart.clearColorScale))
            track.append(Func(nextPart.clearTransparency))

        return track

    dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
    dustCloud.setBillboardAxis(2.0)
    dustCloud.setZ(3)
    dustCloud.setScale(0.4)
    dustCloud.createTrack()

    toonTrack = Parallel()
    if dmg > 0:
        dustCloudHideIval = Sequence(Func(dustCloud.reparentTo, render),
                                     Func(dustCloud.setPos, Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + 3)),
                                     dustCloud.track, Func(dustCloud.detachNode))

        toonTrack.append(Sequence(
            Wait(2.2),
            Parallel(hideParts(headParts), hideParts(torsoParts), hideParts(legsParts), dustCloudHideIval), Func(toon.hide),
            Wait(1.7)))

    toonTrack.append(getToonTrack(attack, 2.2, ['conked'], 2.5, ['jump']))
    toonTrack.append(Parallel(Func(toon.setToonStatusEffect, 'suppressed', turns=2)))

    return Parallel(suitTrack, toonTrack, propTrack)

def doSuppressionRevert(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']

        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        toonPos = toon.getPos(render)


        def showParts(parts):
            track = Parallel()
            for partNum in range(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.clearColorScale))
                track.append(Func(nextPart.clearTransparency))

            return track

        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(0.4)
        dustCloud.createTrack()

        toonTrack = Parallel()
        if dmg > 0:
            dustCloudShowIval = Sequence(Func(dustCloud.reparentTo, render),
                                         Func(dustCloud.setPos, Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + 3)),
                                         dustCloud.track, Func(dustCloud.detachNode), Func(dustCloud.destroy), Wait(2.0))

            toonTrack.append(Sequence(Func(toon.show),
                Parallel(showParts(headParts), showParts(torsoParts), showParts(legsParts), dustCloudShowIval),
            ))
        toonTracks.append(toonTrack)
    toonTracks.append(getToonTracksCheat(attack, 0, ['conked'], 0, ['nothing']))
    return Parallel(toonTracks)

def doAutoRepair(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']

    suitTracks = Parallel()
    suitTracks.append(getSuitAnimTrack(attack, playRate=1.5))
    healSounds = Parallel()
    healSound = getSoundTrack('SA_repair.ogg')
    for suit in battle.activeSuits:
        suitTrack = Sequence(Wait(2.0))
        suitTrack.append(Func(suit.checkAutoRepair))
        suitTracks.append(suitTrack)
    healSounds.append(healSound)
    return Parallel(suitTracks, healSounds)


def doCeaseAndDesist(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    notifyTrack = Parallel()
    for t in targets:
        toon = t['toon']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    for suit in battle.activeSuits:
        suitTrack.append(Func(suit.checkCogLured, battle))
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTrack.append(Func(battle.unSueSuit, suit))
        suitTrack.append(Func(suit.setSued2, 0))
        suitTrack.append(Func(suit.setDizzy, 0))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'lured'))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'zapped'))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'dazed'))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'marked'))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'soaked'))
        suitTrack.append(Func(suit.makeDeepFrozen, 2))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=theSuit))
    return Parallel(suitTrack, notifyTrack, soundTrack)

def doJuryNotice(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(1.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_jury_notice.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack)

def doSnap2(attack, suit):
    #suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.45
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    moveTracks = Parallel()
    notifyTracks = Parallel()
    posPoints = [Point3(-0.25, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('litigator-teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            origH = suit.getH(battle)
            targetPos = toon.getPos(battle)
            suit.headsUp(battle, targetPos)
            targetH = suit.getH(battle)
            suit.setH(battle, origH)
            delta = (targetH - origH + 180) % 360 - 180
            if delta > 0:
                shuffleAnim = 'shuffle-right'
            else:
                shuffleAnim = 'shuffle-left'
            moveTracks.append(Sequence(LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle), ActorInterval(suit, 'throw-object', playRate=1.5),
                                       Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)),
                                       Func(suit.setNeutralAnimationDrop)))
            notifyTrack = Sequence(Wait(3.1), Func(toon.setToonStatusEffect, 'snapped', modifier=10, turns=3, mode='keepHighest'), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
            notifyTracks.append(notifyTrack)
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.8)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.2, toonHeight * 0.9)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(8, 8, 8)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(14, 14, 14)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.1), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration), ActorInterval(teeth, 'litigator-teeth', duration=0.3), Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7), ActorInterval(teeth, 'litigator-teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(teeth.removeNode))
            propTracks.append(propTrack)

    damageAnims = [['cringe',
      0.01,
      0.7,
      1.2], ['conked',
      0.01,
      0.2,
      2.1], ['conked', 0.01, 3.2]]
    dodgeAnims = [['cringe',
      0.01,
      0.7,
      0.2], ['duck', 0.01, 1.6]]
    #soundTrack = getSoundTrack('SA_bite%s.ogg' % ('' if hitAtleastOneToon else '_miss'), delay=2, node=suit)
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    soundTrack = getSoundTrack('SA_bite.ogg', delay=2, node=suit)
    toonTracks = getToonTracksCheat(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.75,
                               dodgeAnimNames=['neutral'], showDamageExtraTime=1.4)
    return Parallel(suitTrack, toonTracks, moveTracks, soundTrack, propTracks, notifyTracks)

def doSnapBindings(attack, suit):
    #suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.45
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    notifyTracks = Parallel()
    posPoints = [Point3(-0.25, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('litigator-teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            targetPos = toon.getPos(battle)
            suitTrack.append(Func(suit.headsUp, battle, targetPos))
            origPos, origHpr = battle.getActorPosHpr(suit)
            suitTrack.append(Func(suit.setHpr, battle, origHpr))
            notifyTrack = Sequence(Wait(3.1), Func(toon.setToonStatusEffect, 'snapped', modifier=10, turns=3, mode='keepHighest'), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
            notifyTracks.append(notifyTrack)
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.8)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.2, toonHeight * 0.9)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(8, 8, 8)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(14, 14, 14)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.1), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration), ActorInterval(teeth, 'litigator-teeth', duration=0.3), Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7), ActorInterval(teeth, 'litigator-teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(teeth.removeNode))
            propTracks.append(propTrack)

    damageAnims = [['cringe',
      0.01,
      0.7,
      1.2], ['conked',
      0.01,
      0.2,
      2.1], ['conked', 0.01, 3.2]]
    dodgeAnims = [['cringe',
      0.01,
      0.7,
      0.2], ['duck', 0.01, 1.6]]
    #soundTrack = getSoundTrack('SA_bite%s.ogg' % ('' if hitAtleastOneToon else '_miss'), delay=2, node=suit)
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    soundTrack = getSoundTrack('SA_bite.ogg', delay=2, node=suit)
    toonTracks = getToonTracksCheat(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.75,
                               dodgeAnimNames=['neutral'], showDamageExtraTime=1.4)
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks, notifyTracks)

def doSnapStenographer(attack, suit):
    #suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.45
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    notifyTracks = Parallel()
    posPoints = [Point3(-0.25, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('litigator-teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            targetPos = toon.getPos(battle)
            suitTrack.append(Func(suit.headsUp, battle, targetPos))
            origPos, origHpr = battle.getActorPosHpr(suit)
            suitTrack.append(Func(suit.setHpr, battle, origHpr))
            notifyTrack = Sequence(Wait(3.1), Func(toon.setToonStatusEffect, 'snapped', modifier=40, turns=3, mode='keepHighest'), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
            notifyTracks.append(notifyTrack)
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.8)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.2, toonHeight * 0.9)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(8, 8, 8)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(14, 14, 14)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.1), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration), ActorInterval(teeth, 'litigator-teeth', duration=0.3), Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7), ActorInterval(teeth, 'litigator-teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(teeth.removeNode))
            propTracks.append(propTrack)

    damageAnims = [['cringe',
      0.01,
      0.7,
      1.2], ['conked',
      0.01,
      0.2,
      2.1], ['conked', 0.01, 3.2]]
    dodgeAnims = [['cringe',
      0.01,
      0.7,
      0.2], ['duck', 0.01, 1.6]]
    #soundTrack = getSoundTrack('SA_bite%s.ogg' % ('' if hitAtleastOneToon else '_miss'), delay=2, node=suit)
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    soundTrack = getSoundTrack('SA_bite.ogg', delay=2, node=suit)
    toonTracks = getToonTracksCheat(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.75,
                               dodgeAnimNames=['neutral'], showDamageExtraTime=1.4)
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks, notifyTracks)

def doSnap(attack, suit):
    #suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    hitAtleastOneToon = 0
    for t in targets:
        if t['hp'] > 0:
            hitAtleastOneToon = 1

    propDelay = 0.25
    propScaleUpTime = 0.25
    suitDelay = 1.45
    throwDelay = propDelay + propScaleUpTime + suitDelay
    throwDuration = 0.25
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    notifyTracks = Parallel()
    posPoints = [Point3(-0.25, 0, 0), VBase3(90, 180, 0)]
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        teeth = globalPropPool.getProp('litigator-teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            targetPos = toon.getPos(battle)
            suitTrack.append(Func(suit.headsUp, battle, targetPos))
            origPos, origHpr = battle.getActorPosHpr(suit)
            suitTrack.append(Func(suit.setHpr, battle, origHpr))
            notifyTrack = Sequence(Wait(3.1), Func(toon.setToonStatusEffect, 'snapped', modifier=20, turns=3, mode='keepHighest'), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
            notifyTracks.append(notifyTrack)
            x = toon.getX(battle)
            y = toon.getY(battle)
            z = toon.getZ(battle)
            toonHeight = z + toon.getHeight()
            flyPoint = Point3(x, y + 2.7, toonHeight * 0.8)
            teethAppearTrack.append(LerpPosInterval(teeth, throwDuration, pos=flyPoint))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.4, pos=Point3(x, y + 3.2, toonHeight * 0.7)))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.3, pos=Point3(x, y + 4.7, toonHeight * 0.5)))
            teethAppearTrack.append(Wait(0.2))
            teethAppearTrack.append(LerpPosInterval(teeth, 0.1, pos=Point3(x, y - 0.2, toonHeight * 0.9)))
            teethAppearTrack.append(Wait(0.4))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(teeth, throwDuration, Point3(8, 8, 8)), Wait(0.9), LerpScaleInterval(teeth, 0.2, Point3(14, 14, 14)), Wait(1.2), LerpScaleInterval(teeth, 0.3, MovieUtil.PNT3_NEARZERO))
            hprTrack = Sequence(Wait(throwDelay), LerpHprInterval(teeth, 0.3, Point3(180, 0, 0)), Wait(0.2), LerpHprInterval(teeth, 0.4, Point3(180, -35, 0), startHpr=Point3(180, 0, 0)), Wait(0.1), LerpHprInterval(teeth, 0.1, Point3(180, -75, 0), startHpr=Point3(180, -35, 0)))
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'litigator-teeth', duration=throwDuration), ActorInterval(teeth, 'litigator-teeth', duration=0.3), Func(teeth.pose, 'litigator-teeth', 1), Wait(0.7), ActorInterval(teeth, 'litigator-teeth', duration=0.9))
            propTrack = Sequence(Parallel(teethAppearTrack, scaleTrack, hprTrack, animTrack), Func(teeth.removeNode))
            propTracks.append(propTrack)

    damageAnims = [['cringe',
      0.01,
      0.7,
      1.2], ['conked',
      0.01,
      0.2,
      2.1], ['conked', 0.01, 3.2]]
    dodgeAnims = [['cringe',
      0.01,
      0.7,
      0.2], ['duck', 0.01, 1.6]]
    #soundTrack = getSoundTrack('SA_bite%s.ogg' % ('' if hitAtleastOneToon else '_miss'), delay=2, node=suit)
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    soundTrack = getSoundTrack('SA_bite.ogg', delay=2, node=suit)
    toonTracks = getToonTracksCheat(attack, damageDelay=2.1, splicedDamageAnims=damageAnims, dodgeDelay=1.75,
                               dodgeAnimNames=['neutral'], showDamageExtraTime=1.4)
    return Parallel(suitTrack, toonTracks, soundTrack, propTracks, notifyTracks)

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
            if not suit.dna.name == 'cbutcher' and not suit.isShadow:
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

def doBayouBellow(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel()
    sprayEffect = BattleParticles.createParticleEffect(file='soundWave')
    sprayEffect.setDepthWrite(0)
    sprayEffect.setDepthTest(0)
    sprayEffect.setTwoSided(1)
    sprayTrack = Sequence()
    sprayTrack.append(Func(setPosFromOther, sprayEffect, theSuit, Point3(0, 1.6, theSuit.height - 2)))
    sprayTrack.append(__getPartTrack(sprayEffect, 0.0, 6.0, [sprayEffect, theSuit, 0], softStop=-3.5))
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.0))
        resetTrack = getResetTrack(suit, battle)
        suitTrack.append(Func(suit.checkCogLured, battle))
        suitTrack.append(Func(battle.unlureSuit, suit))
        suitTrack.append(Wait(1.0))
        suitTrack.append(Func(battle.unSueSuit, suit))
        suitTrack.append(Func(suit.setSued2, 0))
        suitTrack.append(Func(suit.setDizzy, 0))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'lured'))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'zapped'))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'dazed'))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'marked'))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'soaked'))
        suitTracks.append(Wait(0.5))
        suitTracks.append(Func(theSuit.createSuitBellowInterval))
        suitTracks.append(Wait(4.0))
        suitTracks.append(suitTrack)
    soundTrack = getSoundTrack('SA_bellow.ogg', delay=0.1)
    return Parallel(suitTracks, sprayTrack, soundTrack)

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
    suitInterval = Sequence()
    actorNode = suit.find('**/__Actor_modelRoot')
    actorCollection = actorNode.findAllMatches('*')
    parts = ()
    texture = loader.loadTexture('phase_3.5/maps/ttcc_ene_suittex_unemployed.png')
    for thingIndex in xrange(0, actorCollection.getNumPaths()):
        thing = actorCollection[thingIndex]
        if thing.getName() not in ('joint_attachMeter', 'joint_shadow', 'joint_nameTag', 'def_nameTag'):
            suitInterval.append(Func(thing.setColor, color))
    if not suit.isSkeleton:
        suitInterval.append(Func(suit.find('**/hands').setTexture, texture, 1))
        suitInterval.append(Func(suit.find('**/hands').setColor, suit.handColor))
    if suit.dna.name == 'lgator' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryLitigator))
    if suit.style.name == 'safesupervis' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryFirestarter))
    if suit.style.name == 'fires' and not suit.isSkeleton:
        suitInterval.append(Func(suit.makeDryFirestarter))
    return suitInterval

def doBayouBash(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack2 = Sequence(Func(suit.createSuitSnapInterval), Func(suit.setNeutralAnimationDrop))
    suitTrack2.append(Wait(5.0))
    soundTrack = getSoundTrack('SA_bash.ogg', node=suit)
    return Parallel(suitTrack, suitTrack2, soundTrack)

def doCourtSanction(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = __makeSanctionedNodePath()
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 0.6),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [__toonFacePoint(toon)], .25),
        Func(sanctioned.removeNode)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0, ['duck'])
    notifyTrack = Sequence(Wait(0.8),  Func(toon.showHpTextNew, -int(dmg), text="SANCTIONED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'sanctioned', modifier=50, turns=3, mode='keepHighest')))
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)


def doCourtSanctionLitigator(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = __makeSanctionedNodePath()
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 0.6),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [__toonFacePoint(toon)], .25),
        Func(sanctioned.removeNode)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0, ['duck'])
    notifyTrack = Sequence(Wait(0.8),  Func(toon.showHpTextNew, -int(dmg), text="SANCTIONED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'sanctioned', modifier=75, turns=3, mode='keepHighest')))
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)

def doCourtSanction2(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = target[0]['hp']
    toon = target[0]['toon']
    sanctioned = __makeSanctionedNodePath()
    missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
    propTrack = Sequence(
        Wait(0.5),
        Func(battle.movie.needRestoreRenderProp, sanctioned),
        Func(sanctioned.reparentTo, render),
        Func(sanctioned.setScale, 0.6),
        Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 100, 90),
        Func(sanctioned.setP, 0),
        Func(sanctioned.setR, 0),
        getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [__toonFacePoint(toon)], .25),
        Func(sanctioned.removeNode)
    )
    toonTrack = getToonTrackCheat(attack, 0.8, ['conked'], 0, ['duck'])
    notifyTrack = Sequence(Wait(0.8),  Func(toon.showHpTextNew, -int(dmg), text="SANCTIONED!", colorCode=1))
    notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'sanctioned', modifier=25, turns=3, mode='keepHighest')))
    suitTrack = getSuitTrack(attack)
    soundTrack = getSoundTrack('SA_sanction.ogg', delay =.5, node=suit)
    return Parallel(suitTrack, toonTrack, propTrack, soundTrack, notifyTrack)


def doCourtSanctionBindings(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    notifyTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    toonTracks = Parallel()
    propTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        suitTrack = getSuitAnimTrack(attack)
        soundTrack = getSoundTrack('SA_sanction.ogg', delay=.5, node=suit)
        notifyTrack = Sequence(Wait(.8),  Func(toon.showHpTextNew, -int(dmg), text="SANCTIONED!", colorCode=1))
        if dmg > 0:
            sanctioned = __makeSanctionedNodePath()
            missPoint = lambda sanctioned=sanctioned, toon=toon: __toonMissPoint(sanctioned, toon)
            propTrack = Sequence(
                Wait(0.5),
                Func(battle.movie.needRestoreRenderProp, sanctioned),
                Func(sanctioned.reparentTo, render),
                Func(sanctioned.setScale, 0.6),
                Func(sanctioned.setPosHpr, suit.getLeftHand(), 0, 0.11, -0.16, 0, 80, 90),
                Func(sanctioned.setP, 0),
                Func(sanctioned.setR, 0),
                getPropThrowTrack(attack, sanctioned, [__toonFacePoint(toon)], [__toonFacePoint(toon)], .25),
                Func(sanctioned.removeNode))
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
            propTracks.append(propTrack)
            suitTracks.append(Sequence(Parallel(suitTrack, LerpHprInterval(suit, 0, (origH + delta, 0, 0), startHpr=(origH, 0, 0), other=battle)), Parallel(ActorInterval(suit, shuffleAnim), LerpHprInterval(suit, suit.getDuration(shuffleAnim), (origH, 0, 0), startHpr=(origH + delta, 0, 0), other=battle)), Func(suit.setNeutralAnimationDrop)))
            soundTracks.append(soundTrack)
            notifyTracks.append(notifyTrack)
            notifyTracks.append(Parallel(Func(toon.makeDamageDown), Func(toon.addDamageDownRounds, 3)))
            notifyTracks.append(Parallel(Func(toon.checkDamageDown, 25)))
    toonDamageTrack = getToonTracksCheat(attack, 0.8, ['conked'], 0, ['neutral'])
    return Parallel(suitTracks, toonTracks, toonDamageTrack, propTracks, soundTracks, notifyTracks)

def doGavelCourtRecord2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    toonTracks = Parallel()
    nothingTrack = Sequence(Wait(1.0))
    suitTrack = Sequence(getSuitAnimTrackAttack(attack, playRate=0.75))
    for t in targets:
        toon = t['toon']
        gavel = globalPropPool.getProp('LB_gavel')
        dmg = t['hp']
        toonPos = toon.getPos(battle)
        gavelPos = Point3(toonPos.getX(), -17.5, 0)
        propTrack = Sequence(Wait(2.0),
            getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0,
                               scaleUpPoint=Point3(1), scaleUpTime=1.5),
            LerpHprInterval(gavel, 0.5, VBase3(0, -90, 0)),
            Parallel(getSoundTrack('LB_gavel.ogg'), Sequence(
                Wait(0.1),
                LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
                LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO), Func(gavel.removeNode)
            ))
        )
        toonTrack = Sequence(
            Wait(4.0),
            Parallel(
                Func(toon.enterFlattened), Func(toon.playDialogueForString, "!"),

            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened),
                    Func(toon.showHpText, -dmg, openEnded=0),
                    #Func(__doDamage, toon, dmg, t['died'])
                ),
                getSoundTrack('toon_decompress.ogg'),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
        if dmg > 0:
            propTracks.append(propTrack)
            toonTracks.append(toonTrack)
    toonDamageTrack = getToonTracksCheat(attack, 5.5, ['nothing'], 0, ['neutral'])
    return Parallel(toonTracks, toonDamageTrack, suitTrack, propTracks)

def doGavelCourtRecord(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    propTracks = Parallel()
    toonTracks = Parallel()
    gavelTracks = Parallel()
    nothingTrack = Sequence(Wait(1.0))
    for t in targets:
        toon = t['toon']
        gavel = globalPropPool.getProp('LB_gavel')
        gavelSfx = loader.loadSfx("phase_11/audio/sfx/LB_gavel.ogg")
        gavel.setScale(0.01)
        gavel.setPos(toon, 0, -14, 0)
        gavel.setHpr(toon, 0, 0, 0)
        dmg = t['hp']
        finalScale = 1.75
        finalP = -80
        startHpr = toon.getHpr()
        toon.headsUp(gavel)
        endHpr = toon.getHpr()
        toon.setHpr(startHpr)

        gavelScale = LerpScaleInterval(gavel, 2.0, finalScale, blendType="easeOut")
        gavelShow = Sequence(Func(gavel.wrtReparentTo, render), gavelScale)
        gavelFall1 = LerpHprInterval(
            gavel,
            0.5,
            (startHpr[0], startHpr[1] - 15, startHpr[2]),
            blendType="easeInOut",
        )
        gavelFall2 = LerpHprInterval(
            gavel,
            0.4,
            (startHpr[0], startHpr[1] + finalP, startHpr[2]),
            blendType="easeIn",
        )

        def finishToonEmote():
            if toon.emoteTrack:
                toon.emoteTrack.finish()

        toonWalkTrack = Sequence(
            Func(toon.loop, "walk"),
            LerpHprInterval(toon, 1.0, endHpr),
            Func(toon.loop, "neutral"),
            Func(toon.doEmote, 20),
            Wait(0.39),
            Func(finishToonEmote),
        )

        gavelTrack = Sequence(
            gavelShow,
            gavelFall1,
            Parallel(Sequence(Wait(1), gavelFall2), toonWalkTrack),
        )
        gavelTrack.append(Func(base.playSfx, gavelSfx))
        gavelTrack.append(Func(toon.enterFlattened))
        gavelTrack.append(Func(toon.showHpText, -dmg, openEnded=0))
        gavelTrack.append(Func(toon.playDialogueForString, "!"))
        gavelTrack.append(Func(toon.setHpr, startHpr))
        gavelTrack.append(Wait(1))
        gavelTrack.append(LerpScaleInterval(gavel, 0.5, 0.01))
        gavelTrack.append(Wait(0.5))
        gavelTrack.append(Sequence(
                    
                
                Sequence(
                    Parallel(ActorInterval(toon, 'jump'), getSoundTrack('toon_decompress.ogg'), Sequence(Wait(.5), Func(toon.exitFlattened))),
                    Func(toon.loop, 'neutral')
                )))
        gavelTrack.append(Func(gavel.removeNode))
        gavelTracks.append(gavelTrack)
    toonDamageTrack = getToonTracksCheat(attack, 3.9, ['nothing'], 0, ['neutral'])
    return Parallel(toonTracks, gavelTracks, toonDamageTrack, propTracks)

def doLegalBindings2(attack):
    suit = attack['suit']
    targets = attack['target']
    tape = globalPropPool.getProp('redtape')
    tape.setColorScale(0.25, 0.25, 1.0, 1.0)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    tubes = []
    tapePosPoints = [Point3(-0.25, 0, -0.25), VBase3(0, 0, 0)]
    tapeScaleUpPoint = Point3(1, 1, 0.74)
    propTracks = Parallel()
    toonTracks = Parallel()
    allTubeTracks = Parallel()
    notifyTracks = Parallel()
    battle = attack['battle']
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tape.setColorScale(0.25, 0.25, 1.0, 1.0)
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))
            tubes[i].setColorScale(0.25, 0.25, 1.0, 1.0)

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
        notifyTracks.append(Sequence(Wait(2.4), Func(toon.showHpString, "LEGALLY BOUND!", 10)))
        allTubeTracks.append(tubeTracks)
        toonTracks.append(Sequence(Wait(2.4), Func(toon.setToonStatusEffect, 'bound', turns=3), ActorInterval(toon, 'struggle')))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.4, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack, allTubeTracks, notifyTracks)

def doLegalBindings(attack):
    suit = attack['suit']
    targets = attack['target']
    tape = globalPropPool.getProp('redtape')
    tape.setColor(0.129, 0, 0.329, 1)
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    tubes = []
    tapePosPoints = [Point3(-0.25, 0, -0.25), VBase3(0, 0, 0)]
    tapeScaleUpPoint = Point3(1, 1, 0.74)
    propTracks = Parallel()
    toonTracks = Parallel()
    allTubeTracks = Parallel()
    notifyTracks = Parallel()
    battle = attack['battle']
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        tape = globalPropPool.getProp('redtape')
        tape.setColor(0.129, 0, 0.329, 1)
        tubes = []
        for i in xrange(0, 3):
            tubes.append(globalPropPool.getProp('redtape-tube'))
            tubes[i].setColor(0.129, 0, 0.329, 1)

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
        notifyTracks.append(Sequence(Wait(2.4), Func(toon.showHpString, "LEGALLY BOUND!", 10)))
        allTubeTracks.append(tubeTracks)
        toonTracks.append(Sequence(Wait(2.4), Func(toon.setToonStatusEffect, 'bound', turns=3), ActorInterval(toon, 'struggle')))
    soundTrack = getSoundTrack('SA_red_tape.ogg', delay=2.4, node=suit)
    return Parallel(suitTrack, toonTracks, propTracks, soundTrack, allTubeTracks, notifyTracks)

def doCompensation(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTracks = Parallel(getSuitAnimTrack(attack, playRate=1.25))
    suitTracks.append(Wait(5.0))
    soundTrack = getSoundTrack('SA_sanction.ogg', node=suit)
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    for suit in battle.activeSuits:
        suitTrack = Parallel()
        if not suit.dna.name == 'whistleb':
            suitTrack.append(Sequence(Parallel(Func(suit.checkCompensation), healSound)))
            suitTracks.append(suitTrack)
    return Parallel(suitTracks, soundTrack)

def doCaseInsurance(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    suitTracks = Parallel()
    healSounds = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        if suit.hasSuitStatusEffect('insured'):
            suitTrack.append(Func(suit.checkInsuranceHP))
            suitTracks.append(suitTrack)
            healSounds.append(healSound)
    return Parallel(suitTracks, healSounds)

def doCaseInsuranceScapegoat(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    tauntIndex = attack['taunt']
    toon = attack['target'][0]['toon']
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    suitTracks = Parallel()
    healSounds = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        if suit.hasSuitStatusEffect('insured2'):
            suitTrack.append(Func(suit.checkInsuranceScapegoatHP))
            suitTracks.append(suitTrack)
            healSounds.append(healSound)
    return Parallel(suitTracks, healSounds)

def doLegallyBound(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 0
    sprayEffects = [BattleParticles.createParticleEffect(file='spinSpray') for t in targets]
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.25))
    sprayTracks = getPartTracks(attack, sprayEffects, 1.0, 1.9, 0)
    spinTracks1 = Parallel()
    spinTracks2 = Parallel()
    spinTracks3 = Parallel()
    damageAnims = []
    damageAnims.append(['duck',
     0.01,
     0.01,
     1.1])
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    damageAnims.extend(getSplicedLerpAnims('think', 0.66, 1.1, startTime=2.26))
    #toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['sidestep'], showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTracks = Parallel()
    toonSpinTracks = Parallel()
    nothingTrack = Sequence(Wait(1.0))
    notifyTracks = Parallel()
    toonTracks = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffectBindings')
        spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffectBindings')
        spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffectBindings')
        spinEffect1.reparentTo(toon)
        spinEffect2.reparentTo(toon)
        spinEffect3.reparentTo(toon)
        height1 = toon.getHeight() * (random.random() * 0.2 + 0.7)
        height2 = toon.getHeight() * (random.random() * 0.2 + 0.4)
        height3 = toon.getHeight() * (random.random() * 0.2 + 0.1)
        spinEffect1.setPos(0.8, -0.7, height1)
        spinEffect1.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect1.setHpr(spinEffect1, 0, 50, 0)
        spinEffect2.setPos(0.8, -0.7, height2)
        spinEffect2.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect2.setHpr(spinEffect2, 0, 50, 0)
        spinEffect3.setPos(0.8, -0.7, height3)
        spinEffect3.setHpr(0, 0, -random.random() * 10 - 85)
        spinEffect3.setHpr(spinEffect3, 0, 50, 0)
        spinEffect1.wrtReparentTo(battle)
        spinEffect2.wrtReparentTo(battle)
        spinEffect3.wrtReparentTo(battle)
        notifyTrack = Sequence(Wait(damageDelay + 1.9), Func(toon.showHpTextNew, -int(dmg)))
        if dmg > 0:
            spinTracks1.append(getPartTrack(spinEffect1, 0, 5.9, [spinEffect1, battle, 0], softStop=-2))
            spinTracks2.append(getPartTrack(spinEffect2, 0, 5.9, [spinEffect2, battle, 0], softStop=-2))
            spinTracks3.append(getPartTrack(spinEffect3, 0, 5.9, [spinEffect3, battle, 0], softStop=-2))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=0.9))
            soundTracks.append(getSoundTrack('LB_boss_paper_spin.ogg', delay=0))
            notifyTracks.append(notifyTrack)
            toonSpinTracks.append(Sequence(Wait(.75), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=0.9, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['neutral'], showDamageExtraTime=1.0)
    return Parallel(toonTracks, toonSpinTracks, toonDamageTrack, spinTracks1, spinTracks2, spinTracks3, notifyTracks, soundTracks)

def doCaseInsurancePlanInsuranceScapegoat(attack, ind, ind2, ind3):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    if len(battle.activeSuits) > 1 and ind == 1:
        targetSuit = battle.activeSuits[ind]
    elif ind == 0:
        targetSuit = battle.activeSuits[ind]
    else:
        targetSuit = None
    if len(battle.activeSuits) >= 3 and ind2 == 2:
        targetSuit2 = battle.activeSuits[ind2]
    elif len(battle.activeSuits) >= 4 and ind2 == 3:
        targetSuit2 = battle.activeSuits[ind2]
    else:
        targetSuit2 = None
    if len(battle.activeSuits) >= 5 and ind3 == 4:
        targetSuit3 = battle.activeSuits[ind3]
    elif len(battle.activeSuits) >= 6 and ind3 == 5:
        targetSuit3 = battle.activeSuits[ind3]
    else:
        targetSuit3 = None

    targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3, theSuit) if s is not None]

    suitTracks = Parallel()
    liftTracks = Parallel()
    knifeTracks = Parallel()
    suitAnimTrack = Sequence(MovieUtil.createSuitInsuranceInterval(theSuit), Func(theSuit.setNeutralAnimationDrop))
    taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    tauntInterval = Sequence(Func(suit.setChatAbsoluteSpecial, taunt, CFSpeech | CFTimeout))
    for suit in targetSuits:
        liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
        #liftEffect.setPos(suit.getPos(battle))
        liftEffect.setZ(liftEffect.getZ() - 1.3)
        liftTracks.append(getPartTrack(liftEffect, 4.5, 4.0, [liftEffect, suit, 0], softStop=-2))
        suitTrack = Sequence()
        suitTrack.append(Wait(5.2))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'caseman':
            suitTrack.append(Func(suit.checkHealingPhrases, 0))
        suitTrack.append(Func(suit.showHpTextNew, 0, text="INSURANCE!", colorCode=1))
        #suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(battle.unSueSuit, suit))
        suitTrack.append(Func(suit.setSuitStatusEffect, 'insured2', modifier=1, turns=3))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'sued'))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(Wait(6.5))
        knife = globalPropPool.getProp('shredder-paper')


        posPoints = [Point3(0.4775687409551388, -1.3458755426917506, 0.4775687409551388), VBase3(171.40376266280748, -44.02315484804629, 153.69030390738055)]

        knifeTrack = Sequence(
            getPropAppearTrack(
                knife,
                theSuit.getRightHand(),
                posPoints,
                0.5,
                VBase3(0.8, 0.8, 0.8),
                scaleUpTime=0.1
            ),
            Wait(2.3),

            Parallel(
                getThrowTrack(knife, (0, 0, suit.getHeight() + 2.5), 1.5, suit, -20.288),
                LerpHprInterval(knife, 1.0, VBase3(0, -20, -20))
            ),

            Wait(0.15),

            Parallel(
                LerpPosInterval(knife, 0.45, (0, 0, suit.getHeight() - 2.5), other=suit, blendType='easeIn'),
                LerpScaleInterval(knife, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
            ),

            Parallel(
                LerpScaleInterval(knife, 0.2, VBase3(0.01, 0.01, 0.01)),
                LerpColorScaleInterval(knife, 0.2, Vec4(1, 1, 1, 0))
            ),

            Func(knife.removeNode)
        )
        knifeTracks.append(knifeTrack)
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    #insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
    soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(5.2), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg')))
    return Parallel(suitTracks, healSound, liftTracks, suitAnimTrack, multiTrack, knifeTracks)

def doCaseInsurancePlanInsurance(attack, ind, ind2, ind3):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    if len(battle.activeSuits) > 1 and ind == 1:
        targetSuit = battle.activeSuits[ind]
    elif ind == 0:
        targetSuit = battle.activeSuits[ind]
    else:
        targetSuit = None
    if len(battle.activeSuits) >= 3 and ind2 == 2:
        targetSuit2 = battle.activeSuits[ind2]
    elif len(battle.activeSuits) >= 4 and ind2 == 3:
        targetSuit2 = battle.activeSuits[ind2]
    else:
        targetSuit2 = None
    if len(battle.activeSuits) >= 5 and ind3 == 4:
        targetSuit3 = battle.activeSuits[ind3]
    elif len(battle.activeSuits) >= 6 and ind3 == 5:
        targetSuit3 = battle.activeSuits[ind3]
    else:
        targetSuit3 = None

    targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3, theSuit) if s is not None]

    suitTracks = Parallel()
    liftTracks = Parallel()
    knifeTracks = Parallel()
    suitAnimTrack = Sequence(MovieUtil.createSuitInsuranceInterval(theSuit), Func(theSuit.setNeutralAnimationDrop))
    taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    tauntInterval = Sequence(Func(suit.setChatAbsoluteSpecial, taunt, CFSpeech | CFTimeout))
    for suit in targetSuits:
        liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
        #liftEffect.setPos(suit.getPos(battle))
        liftEffect.setZ(liftEffect.getZ() - 1.3)
        liftTracks.append(getPartTrack(liftEffect, 4.5, 4.0, [liftEffect, suit, 0], softStop=-2))
        suitTrack = Sequence()
        suitTrack.append(Wait(5.2))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'caseman':
            suitTrack.append(Func(suit.checkHealingPhrases, 0))
        suitTrack.append(Func(suit.showHpTextNew, 0, text="INSURANCE!", colorCode=1))
        #suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(battle.unSueSuit, suit))
        suitTrack.append(Func(suit.setSuitStatusEffect, 'insured', modifier=1, turns=3))
        suitTrack.append(Func(suit.clearSuitStatusEffect, 'sued'))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(Wait(6.5))
        knife = globalPropPool.getProp('shredder-paper')


        posPoints = [Point3(0.4775687409551388, -1.3458755426917506, 0.4775687409551388), VBase3(171.40376266280748, -44.02315484804629, 153.69030390738055)]

        knifeTrack = Sequence(
            getPropAppearTrack(
                knife,
                theSuit.getRightHand(),
                posPoints,
                0.5,
                VBase3(0.8, 0.8, 0.8),
                scaleUpTime=0.1
            ),
            Wait(2.3),

            Parallel(
                getThrowTrack(knife, (0, 0, suit.getHeight() + 2.5), 1.5, suit, -20.288),
                LerpHprInterval(knife, 1.0, VBase3(0, -20, -20))
            ),

            Wait(0.15),

            Parallel(
                LerpPosInterval(knife, 0.45, (0, 0, suit.getHeight() - 2.5), other=suit, blendType='easeIn'),
                LerpScaleInterval(knife, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
            ),

            Parallel(
                LerpScaleInterval(knife, 0.2, VBase3(0.01, 0.01, 0.01)),
                LerpColorScaleInterval(knife, 0.2, Vec4(1, 1, 1, 0))
            ),

            Func(knife.removeNode)
        )
        knifeTracks.append(knifeTrack)
    #cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    #insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
    soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(5.2), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg')))
    return Parallel(suitTracks, healSound, liftTracks, suitAnimTrack, multiTrack, knifeTracks)


def doCaseInsurancePlanInsurance2(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    liftTracks = Parallel()
    knifeTracks = Parallel()
    taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    tauntInterval = Sequence(Func(suit.setChatAbsoluteSpecial, taunt, CFSpeech | CFTimeout))
    suitAnimTrack = Sequence(MovieUtil.createSuitInsuranceInterval(theSuit), Func(theSuit.setNeutralAnimationDrop))
    for suit in battle.activeSuits:
        liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
        # liftEffect.setPos(suit.getPos(battle))
        liftEffect.setZ(liftEffect.getZ() - 1.3)
        liftTracks.append(getPartTrack(liftEffect, 4.5, 4.0, [liftEffect, suit, 0], softStop=-2))
        suitTrack = Sequence()
        suitTrack.append(Wait(5.2))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        if not suit.dna.name == 'caseman':
            suitTrack.append(Func(suit.checkHealingPhrases, 0))
        # suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(battle.unSueSuit, suit))
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'lgator':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            suitTrack.append(Func(suit.showHpString, "+10% Damage!"))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Parallel(Func(suit.setSuitStatusEffect, 'damageUp', modifier=10, mode='refreshModifier')))
        else:
            suitTrack.append(Func(suit.showHpString, "+5% Damage!"))
            suitTrack.append(Func(suit.updateHealthBar, 0))
            suitTrack.append(Parallel(Func(suit.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier')))
        suitTrack.append(Func(suit.setSued2, 0))
        suitTracks.append(suitTrack)
        suitTracks.append(tauntInterval)
        suitTracks.append(Wait(6.5))
        knife = globalPropPool.getProp('shredder-paper')

        posPoints = [Point3(0.4775687409551388, -1.3458755426917506, 0.4775687409551388), VBase3(171.40376266280748, -44.02315484804629, 153.69030390738055)]

        knifeTrack = Sequence(
            getPropAppearTrack(
                knife,
                theSuit.getRightHand(),
                posPoints,
                0.5,
                VBase3(0.8, 0.8, 0.8),
                scaleUpTime=0.1
            ),
            Wait(2.3),

            Parallel(
                getThrowTrack(knife, (0, 0, suit.getHeight() + 2.5), 1.5, suit, -20.288),
                LerpHprInterval(knife, 1.0, VBase3(0, -20, -20))
            ),

            Wait(0.15),

            Parallel(
                LerpPosInterval(knife, 0.45, (0, 0, suit.getHeight() - 2.5), other=suit, blendType='easeIn'),
                LerpScaleInterval(knife, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
            ),

            Parallel(
                LerpScaleInterval(knife, 0.2, VBase3(0.01, 0.01, 0.01)),
                LerpColorScaleInterval(knife, 0.2, Vec4(1, 1, 1, 0))
            ),

            Func(knife.removeNode)
        )
        knifeTracks.append(knifeTrack)
    # cameraTrack = Sequence(LerpPosHprInterval(camera, duration=0.95, pos=Point3(0, -15, 2), hpr=Point3(0, 0, 0), blendType='easeInOut'))
    # insuranceTrack = MovieUtil.createSuitInsuranceInterval(suit)
    soundTrack1 = getSoundTrack('SA_insurance.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2.8, node=suit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    healSound = Sequence(Wait(5.2), SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg')))
    return Parallel(suitTracks, healSound, liftTracks, suitAnimTrack, multiTrack, knifeTracks)

def doCaseInsurancePlanSkelecogInsurance2(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']

    healSound = getSoundTrack('LB_toonup.ogg')
    suitTracks = Parallel()
    liftTracks = Parallel()
    knifeTracks = Parallel()
    taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    for target in battle.activeSuits:
        liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
        # liftEffect.setPos(target.getPos(battle))
        liftEffect.setZ(liftEffect.getZ() - 1.3)
        liftEffect.reparentTo(target)
        liftTracks.append(getPartTrack(liftEffect, 4, 4.0, [liftEffect, target, 0], softStop=-2))

        suitTrack = Sequence(
            Wait(4.25)
        )


        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'lgator':
                currentBossHealth = s.currHP
        if currentBossHealth >= 1:
            suitTrack.append(Func(target.showHpString, "+10% Damage!"))
            suitTrack.append(Func(target.updateHealthBar, 0))
            suitTrack.append(Parallel(Func(target.makeDamageUp), Func(target.checkDamageUp, + 10)))
        else:
            suitTrack.append(Func(target.showHpString, "+5% Damage!"))
            suitTrack.append(Func(target.updateHealthBar, 0))
            suitTrack.append(Parallel(Func(target.makeDamageUp), Func(target.checkDamageUp, + 5)))

        if not target.dna.name == 'caseman':
            suitTrack.append(
                Parallel(
                    healSound,
                    Func(
                        target.checkHealingPhrases, 0
                    )
                )
            )

        suitTrack.append(Func(battle.unSueSuit, target))
        suitTracks.append(suitTrack)

        knife = globalPropPool.getProp('shredder-paper')
        posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]

        knifeTrack = Sequence(
            getPropAppearTrack(
                knife,
                theSuit.getRightHand(),
                posPoints,
                0.75,
                VBase3(1.2, 1.2, 1.2),
                scaleUpTime=0.25
            ),
            Wait(0.95),

            Parallel(
                getThrowTrack(knife, (0, 0, target.getHeight() + 2.5), 1.5, target, -20.288),
                LerpHprInterval(knife, 1.0, VBase3(0, -20, -20))
            ),

            Wait(0.15),

            Parallel(
                LerpPosInterval(knife, 0.45, (0, 0, target.getHeight() - 2.5), other=target, blendType='easeIn'),
                LerpScaleInterval(knife, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
            ),

            Parallel(
                LerpScaleInterval(knife, 0.2, VBase3(0.01, 0.01, 0.01)),
                LerpColorScaleInterval(knife, 0.2, Vec4(1, 1, 1, 0))
            ),

            Func(knife.removeNode)
        )
        knifeTracks.append(knifeTrack)

    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4.25)

    return Parallel(tauntInterval,
         Sequence(ActorInterval(theSuit, 'throw-paper', playRate=1.5), Func(suit.setNeutralAnimation)),
        suitTracks,
        soundTrack2,
        liftTracks,
        soundTrack,
        knifeTracks
    )


def doCaseInsurancePlanSkelecogInsurance(attack, ind, ind2, ind3):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    if len(battle.activeSuits) > 1 and ind == 1:
        targetSuit = battle.activeSuits[ind]
    elif ind == 0:
        targetSuit = battle.activeSuits[ind]
    else:
        targetSuit = None
    if len(battle.activeSuits) >= 3 and ind2 == 2:
        targetSuit2 = battle.activeSuits[ind2]
    elif len(battle.activeSuits) >= 4 and ind2 == 3:
        targetSuit2 = battle.activeSuits[ind2]
    else:
        targetSuit2 = None
    if len(battle.activeSuits) >= 5 and ind3 == 4:
        targetSuit3 = battle.activeSuits[ind3]
    elif len(battle.activeSuits) >= 6 and ind3 == 5:
        targetSuit3 = battle.activeSuits[ind3]
    else:
        targetSuit3 = None
    targetSuits = [s for s in (targetSuit, targetSuit2, targetSuit3, theSuit) if s is not None]

    healSound = getSoundTrack('LB_toonup.ogg')
    suitTracks = Parallel()
    liftTracks = Parallel()
    knifeTracks = Parallel()
    taunt = random.choice(['Hrm...', 'Hmph...', 'Hm, hm...', 'Hrnhmpf...'])
    tauntInterval = Sequence(Func(suit.setChatAbsolute, taunt, CFSpeech | CFTimeout))
    if targetSuits:
        currentBossHealth = -1
        for s in battle.suits:
            if s.dna.name == 'safesupervis':
                currentBossHealth = s.currHP
                break

        for target in targetSuits:
            liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
            #liftEffect.setPos(target.getPos(battle))
            liftEffect.setZ(liftEffect.getZ() - 1.3)
            liftEffect.reparentTo(target)
            liftTracks.append(getPartTrack(liftEffect, 4, 4.0, [liftEffect, target, 0], softStop=-2))

            suitTrack = Sequence(
                Wait(4.25)
            )

            suitTrack.append(Func(target.showHpTextNew, 0, text="INSURANCE!", colorCode=1))

            suitTrack.append(Func(suit.setSuitStatusEffect, 'insured', modifier=1, turns=3, mode='refreshTurns'))

            if not target.dna.name == 'caseman':
                suitTrack.append(
                    Parallel(
                        healSound,
                        Func(
                            target.checkHealingPhrases, 0
                        )
                    )
                )

            suitTrack.append(Func(target.clearSuitStatusEffect, 'sued'))
            suitTracks.append(suitTrack)

            knife = globalPropPool.getProp('shredder-paper')
            posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]

            knifeTrack = Sequence(
                getPropAppearTrack(
                    knife,
                    theSuit.getRightHand(),
                    posPoints,
                    0.75,
                    VBase3(1.2, 1.2, 1.2),
                    scaleUpTime=0.25
                ),
                Wait(0.95),

                Parallel(
                    getThrowTrack(knife, (0, 0, target.getHeight() + 2.5), 1.5, target, -20.288),
                    LerpHprInterval(knife, 1.0, VBase3(0, -20, -20))
                ),

                Wait(0.15),

                Parallel(
                    LerpPosInterval(knife, 0.45, (0, 0, target.getHeight() - 2.5), other=target, blendType='easeIn'),
                    LerpScaleInterval(knife, 0.45, VBase3(0.6, 0.6, 0.6), blendType='easeIn')
                ),

                Parallel(
                    LerpScaleInterval(knife, 0.2, VBase3(0.01, 0.01, 0.01)),
                    LerpColorScaleInterval(knife, 0.2, Vec4(1, 1, 1, 0))
                ),

                Func(knife.removeNode)
            )
            knifeTracks.append(knifeTrack)

    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4.25)

    return Parallel(tauntInterval,
                    Sequence(ActorInterval(theSuit, 'throw-paper', playRate=1.5), Func(suit.setNeutralAnimation)),
        suitTracks,
        soundTrack2,
        liftTracks,
        soundTrack,
        knifeTracks
    )

def doLiquidationSale(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack)
    makeDamageUp = Parallel(Func(suit.makeDamageUp), Func(suit.checkDamageUp, + 50))
    suitTrack.append(Wait(2.0))
    return Parallel(suitTrack)

def doEnraged(attack):
    suit = attack['suit']
    battle = attack['battle']
    soundTrack = getSoundTrack('SA_rage.ogg')
    suitColorTrack = Sequence(Wait(0.5), LerpColorScaleInterval(suit, duration=.25, colorScale=(1, 0, 0, 1),
                                                     blendType='easeInOut'), LerpColorScaleInterval(suit, duration=.25, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'), LerpColorScaleInterval(suit, duration=.25, colorScale=(1, 0, 0, 1),
                                                     blendType='easeInOut'), LerpColorScaleInterval(suit, duration=.25, colorScale=(1, 1, 1, 1)))
    makeEnraged = Func(suit.makeAngry, 2)
    suitTrack = getSuitAnimTrack(attack)
    makeDamageUp = Parallel(Func(suit.clearSuitStatusEffect, 'rageBuilding'), Func(suit.clearSuitStatusEffect, 'absorbing'), Func(suit.setSuitStatusEffect, 'enraged', modifier=1, turns=3), Func(suit.makeFireEffect), Func(suit.removeRageBuilding))
    suitTrack.append(Wait(2.0))
    headInterval = Sequence(MovieUtil.createSuitEnragedInterval(suit, 0))
    return Parallel(suitTrack, soundTrack, makeDamageUp, suitColorTrack, headInterval, makeEnraged)

def doShieldsUp(attack):
    suit = attack['suit']
    node = suit.getGeomNode().getChild(0)
    suitColorTrack = Sequence(Wait(0.5 + suit.getDuration('neutral-enraged-return')), LerpColorScaleInterval(node, duration=.5, colorScale=(0, 1, 0.078, 1),
                                                                blendType='easeInOut'),
                              LerpColorScaleInterval(node, duration=.5, colorScale=(1, 1, 1, 1),
                                                     blendType='easeInOut'))
    soundTrack = Sequence(Wait(suit.getDuration('neutral-enraged-return')), getSoundTrack('SA_defense.ogg'))
    suitTrack = Sequence(ActorInterval(suit, 'neutral-enraged-return'), getSuitAnimTrack(attack))
    suitTrack.append(Wait(2.0))
    makeShielding = Parallel(Func(suit.setSuitStatusEffect, 'rageBuilding', modifier=0), Func(suit.clearSuitStatusEffect, 'enraged'), Func(suit.removeRageBuilding))
    return Parallel(suitTrack, soundTrack, suitColorTrack, makeShielding)

def doBarnyardBash(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    dmg = (attack['target'][0]['hp']) * len(battle.activeToons)
    selfDamageTrack = Sequence(Wait(1.5), Func(suit.showHpText, +dmg), Func(suit.setHealthForMe, dmg), Func(suit.updateHealthBar, 0))
    tauntInterval = Func(suit.setChatAbsolute, 'Is this the best you Toons can do?', CFSpeech | CFTimeout)
    suitTrack = getSuitTrack(attack)
    makeShielding = Func(suit.makeShielding)
    soundTrack2 = getSoundTrack('SA_defense.ogg', delay=0, node=suit)
    soundTrack3 = getSoundTrack('LB_toonup.ogg', delay=1.5, node=suit)
    return Parallel(suitTrack, soundTrack2, soundTrack3, selfDamageTrack, makeShielding)

def __makeSanctionedNodePath():
    tn = TextNode('CANCELLED')
    tn.setFont(getSuitFont())
    tn.setText('SANCTIONED\nSANCTIONED\nSANCTIONED')
    tn.setAlign(TextNode.ACenter)
    tntop = hidden.attachNewNode('CancelledTop')
    tnpath = tntop.attachNewNode(tn)
    tnpath.setPosHpr(0, 0, 0, 0, 0, 0)
    tnpath.setScale(1)
    tnpath.setColor(0.7, 0, 0, 1)
    tnpathback = tnpath.instanceUnderNode(tntop, 'backside')
    tnpathback.setPosHpr(0, 0, 0, 180, 0, 0)
    tnpath.setScale(1)
    return tntop

def doGavel(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    battle = attack['battle']
    target = attack['target']
    toon = target[0]['toon']
    targetPos = toon.getPos(battle)
    headsUp = Func(suit.headsUp, battle, targetPos)
    dmg = target[0]['hp']
    gavel = globalPropPool.getProp('LB_gavel')
    toonPos = toon.getPos(battle)
    initialScale = toon.getScale()
    gavelPos = Point3(toonPos.getX(), 0, 0)
    propTrack = Sequence(
        getPropAppearTrack(gavel, parent=battle, posPoints=[gavelPos, VBase3(0, 0, 0)], appearDelay=0.0, scaleUpPoint=Point3(1), scaleUpTime=1.5),
        LerpHprInterval(gavel, 0.5, VBase3(0, 90, 0)),
        Parallel(getSoundTrack('LB_gavel.ogg'), Sequence(
            Wait(0.1),
            LerpHprInterval(gavel, 0.5, VBase3(0, 0, 0)),
            LerpScaleInterval(gavel, 1.5, MovieUtil.PNT3_ZERO), Func(gavel.removeNode)
        ))
    )
    taunt = "Any gags Toons use can and will be held against them in a court of law."
    origPos, origHpr = battle.getActorPosHpr(suit)
    suitReset = Func(suit.setHpr, battle, origHpr)
    suitTrack = getSuitTrack(attack)
    toonTrack = Sequence(
            Wait(2.0),
            Parallel(
                Func(toon.enterFlattened),
                Func(toon.showHpText, 0, openEnded=0),
                Func(__doDamage, toon, 0, target[0]['died'])
            ),
            Wait(1.0),
            Parallel(
                Sequence(
                    Wait(0.5),
                    Func(toon.exitFlattened)
                ),
                getSoundTrack('toon_decompress.ogg'),
                Sequence(
                    ActorInterval(toon, 'jump'),
                    Func(toon.loop, 'neutral')
                )
            )
        )
    return Parallel(suitTrack, toonTrack, propTrack)