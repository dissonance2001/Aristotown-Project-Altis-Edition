from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
from direct.showutil import Effects
from toontown.building import ElevatorConstants
from toontown.building import ElevatorUtils
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
from toontown.battle.attacks.toons import MovieZap

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

def getSuitAnimTrackAttack(attack, delay = 0, splicedAnims = None, playRate = 1.0):
    return MovieIntervals.getSuitAnimTrackAttack(attack, delay, splicedAnims, playRate)

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

def doHydrationCheckRevert(attack):
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.3
    dodgeDelay = 0.25
    damageAnims = [['slip-forward']]
    puddleTracks = Parallel()
    soundTracks = Parallel()
    suitTracks = Parallel()
    toonDamageTrack = getToonTracksCheat(attack, 0.25, ['nothing'], 0, ['neutral'])
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sinkPos = toon.getPos(battle)
        sinkPos.setZ(sinkPos.getZ() + 15)
        dropPos = toon.getPos(battle)
        moveTrack = Sequence(Func(toon.show), LerpPosInterval(toon, 0, sinkPos, other=battle), LerpPosInterval(toon, 0.5, dropPos, other=battle), Func(toon.setPos, battle, dropPos))
        toonTrack = Parallel(Sequence(Wait(0.25), ActorInterval(toon, 'slip-forward'), Func(toon.loop, 'neutral')), Func(toon.showHpText, -dmg, openEnded=0))
        if dmg > 0:
            suitTrack = Sequence(Wait(4.0))
            suitTracks.append(suitTrack)
            puddleTracks.append(toonTrack)
            puddleTracks.append(moveTrack)
            soundTracks.append(getSoundTrack('Toon_bodyfall_synergy.ogg', delay=0.25, duration=0.67 if dmg == 0 else 0.0, node=toon))

    return Parallel(soundTracks, toonDamageTrack, suitTracks, puddleTracks)

def doHydrationCheck(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
    suitType = getSuitBodyType(attack['suitName'])
    posPoints = [Point3(-.25, 0, -.5), VBase3(0, 0, 0)]
    propTracks = Parallel()
    toonPosTracks = Parallel()
    toonTracks = Parallel()
    toonTracks2 = getToonTracksCheat(attack, 2.3, ['slip-backward'], 2.3, ['nothing'])
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        origPos, origHpr = battle.getActorPosHpr(toon)
        x = origPos.getX()
        y = origPos.getY()
        z = origPos.getZ()
        risePoint = Point3(x, y, z - 50)
        freezeEffect = BattleParticles.createParticleEffect(file="demotionUnFreeze")
        BattleParticles.setEffectTexture(freezeEffect, "snow-particle")
        facePoint = __toonFacePoint(toon)
        freezeEffect.setPos(toon.getPos() + (0, 0, facePoint.getZ()))
        partTrack2 = getPartTrack(
            freezeEffect, 0.0, 0.5, [freezeEffect, render, 0]
        )
        toonMoveTrack = Sequence(
                Wait(2.3),
                Parallel(
                    LerpPosInterval(
                        toon, 1.0, Point3(0, -45.0, 0), blendType="easeOut"
                    ),
                    LerpHprInterval(toon, 1.0, Point3(720, 0, 0), blendType="easeOut"),
                    partTrack2, 
                ),
            )
        sfx = Func(toon.playDialogueForString, "!")
        elevatorTracks = Sequence()
        boss = None
        from toontown.suit.DistributedCountErclaimBoss import DistributedCountErclaimBoss

        for obj in base.cr.doId2do.values():
            if isinstance(obj, DistributedCountErclaimBoss):
                boss = obj
                break

        if boss and hasattr(boss, 'elevatorModel') and not boss.elevatorModel.isEmpty():
            bem = boss.elevatorModel
            elevatorTrack = Sequence(
                Wait(1.0),
                ElevatorUtils.getOpenInterval(
                    boss,
                    bem.find("**/left_door"),
                    bem.find("**/right_door"),
                    None,
                    None,
                    ElevatorConstants.ELEVATOR_ERCLAIM,
                ),
                Wait(0.3),
                Parallel(
                    ElevatorUtils.getCloseInterval(
                        boss,
                        bem.find("**/left_door"),
                        bem.find("**/right_door"),
                        None,
                        None,
                        ElevatorConstants.ELEVATOR_ERCLAIM,
                    ),
                    Sequence(
                        Wait(0.5),
                    ),
                ),
                Func(toon.hide),
            )
            if dmg > 0:
                elevatorTracks.append(elevatorTrack)
        toonPosTrack = Sequence(Wait(2.3), Parallel(ActorInterval(toon, 'slip-backward'), LerpPosHprInterval(toon, 0.5, risePoint, VBase3(360, 0, 0))), Func(toon.hide))
        paper = globalPropPool.getProp('glass')
        propTrack = Sequence(getPropAppearTrack(paper, suit.getRightHand(), posPoints, 0.5, MovieUtil.PNT3_ONE, scaleUpTime=0.25))
        propTrack.append(Wait(1.3))
        hitPoint = __toonFacePoint(toon, parent=battle)
        hitPoint.setX(hitPoint.getX() - 1.4)
        missPoint = __toonGroundPoint(attack, toon, 0.5, parent=battle)
        missPoint.setX(missPoint.getX() - 1.1)
        soundTrack = getSoundTrack('SA_hydrate.ogg', node=suit)
        propTrack.append(Parallel(soundTrack, getPropThrowTrack(attack, paper, [hitPoint], [missPoint], .25, parent=battle, target=t)))
        propTrack.append(Parallel(Func(toon.setToonStatusEffect, 'hydrated', turns=3)))
        if dmg > 0:
            toonTrack = Sequence(
                Wait(2.3), sfx,
            Func(toon.showHpTextNew, -dmg, text="HYDRATED!", colorCode=1))
            toonTracks.append(toonTrack)
            toonPosTracks.append(toonMoveTrack)
        propTracks.append(propTrack)
        if dmg == 0:
            glass = globalPropPool.getProp('glass')
            hands = toon.getRightHands()
            hand_jointpath0 = hands[0].attachNewNode('handJoint0-path')
            hand_jointpath1 = hand_jointpath0.instanceTo(hands[1])
            glassTrack = Sequence(Wait(2.3), Func(MovieUtil.showProp, glass, hand_jointpath0), Parallel(Func(toon.showHpTextNew, +8, text="CHECK PASSED!", colorCode=1), ActorInterval(toon, 'spit', duration=2.7), ActorInterval(toon, 'spit', startTime=2.7, endTime=0), 
                                                                                                        ActorInterval(glass, 'glass')), 
                                  Func(hand_jointpath1.removeNode), Func(hand_jointpath0.removeNode),
                                  Func(MovieUtil.removeProp, glass))
            toonPosTracks.append(glassTrack)

    return Parallel(suitTrack, toonPosTracks, elevatorTracks, toonTracks, toonTracks2, propTracks)

def doWringOut(attack):
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.0
    suitTrack = getSuitTrack(attack)
    damageAnims = [['struggle', 0.01, 0.01, 1.0],
     ['slip-backward', 0.01, 0.01]]
    shakeTracks = Parallel()
    squeezeTracks = Parallel()
    partTracks = Parallel()
    partTracks2 = Parallel()
    partTracks3 = Parallel()
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.5, dodgeAnimNames=['sidestep'], showDamageExtraTime=1.1)
    soundTracks = Track()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            particleEffect = BattleParticles.createParticleEffect(file='trickleLiquidate')
            particleEffect2 = BattleParticles.createParticleEffect(file='trickleLiquidate')
            particleEffect3 = BattleParticles.createParticleEffect(file='trickleLiquidate')
            x, y, z = toon.getPos()
            groundPoint = Point3(x, y, z)
            moveTime = 0.15
            shakeTrack = Sequence(Wait(damageDelay))
            for i in range(5):
                shakeTrack.append(LerpPosInterval(toon, moveTime, Point3(x, y, z + 3)))
                shakeTrack.append(LerpPosInterval(toon, moveTime, Point3(x, y, z + 1.5)))
            
            shakeTrack.append(LerpPosInterval(toon, 0.15, groundPoint))
            shakeTracks.append(shakeTrack)
            shakeTracks.append(Parallel(Func(toon.setToonStatusEffect, 'driedOut', modifier=1, turns=3)))
            initialScale = toon.getScale()
            xScale, yScale, zScale = initialScale
            squeezeTrack = Sequence(
                Wait(damageDelay),
                Func(battle.movie.needRestoreToonScale),
                LerpScaleInterval(toon, 0.1, Vec3(xScale * 0.6, yScale * 0.46, zScale * 1.2)),
                Wait(1.1),
                LerpScaleInterval(toon, 0.2, Vec3(xScale * 1.2, yScale * 1.2, zScale * 0.8)),
                LerpScaleInterval(toon, 0.2, initialScale),
                Func(battle.movie.clearRestoreToonScale)
            )
            squeezeTracks.append(squeezeTrack)
            partTracks.append(getPartTrack(particleEffect, 1.0, 1.5, [particleEffect, toon, 0]))
            partTracks2.append(getPartTrack(particleEffect2, 1.1, 1.4, [particleEffect2, toon, 0]))
            partTracks3.append(getPartTrack(particleEffect3, 1.1, 1.4, [particleEffect3, toon, 0]))
            soundTracks.append((1.0, SoundInterval(globalBattleSoundCache.getSound('SA_short_squeeze.ogg'), node=toon)))
            soundTracks.append((2.4, SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=toon)))

    return Parallel(suitTrack, shakeTracks, squeezeTracks, partTracks, partTracks2, partTracks3, toonTracks, soundTracks)

def doProToonShake(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    targetData = targets[0]

    if 'suit' not in targetData:
        return Sequence()

    targetSuit = targetData['suit']
    damage = int(targetData.get('hp', 0))
    heal = int(targetData.get('heal', 0))

    notifyTracks = Parallel()
    toonTrack = Parallel()

    suitTrack = Sequence(getSuitAnimTrack(attack))

    soundTrack2 = getSoundTrack('SA_protoon_shake.ogg', delay=0.5, node=suit)

    resultTrack = Sequence(Wait(0.5))

    # =========================================================
    # ERFIT PAYS HP TO ANOTHER COG
    # =========================================================
    if damage > 0:
        resultTrack.append(Parallel(Func(suit.showHpTextNew, -damage), Func(suit.setHealthForMe, -damage), Func(suit.updateHealthBar, 0)))

    # =========================================================
    # TARGET COG RECEIVES HEALING
    # =========================================================
    if heal > 0:
        resultTrack.append(Parallel(Func(targetSuit.showHpTextNew, heal), Func(targetSuit.setHealthForMe, heal), Func(targetSuit.updateHealthBar, 0)))

    suitAnimTrack = Sequence(
        Parallel(ActorInterval(suit, 'quick-jump', duration=1.3)),
        Parallel(resultTrack, ActorInterval(suit, 'slip-forward')),
        Func(suit.setNeutralAnimationDrop)
    )

    # =========================================================
    # TOON REACTIONS
    # =========================================================
    for toon in battle.activeToons:
        reactionTrack = Sequence(Func(toon.headsUp, battle, suit.getPos(battle)), Wait(1.8), ActorInterval(toon, 'slip-forward', playRate=0.7), Func(toon.loop, 'neutral'))
        toonTrack.append(reactionTrack)

    notifyTracks.append(Parallel(soundTrack2, suitTrack, suitAnimTrack))

    return Parallel(notifyTracks, toonTrack)

def doProToonShakeDamage(attack):
    suit = attack['suit']
    battle = attack['battle']
    dmg = attack['target'][0]['hp']
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=1.8, node=suit)
    if suit.dna.name == 'erfit':
        suitAnimTrack = Sequence(Wait(1.8), suit.checkProToonShake(dmg * 2, battle))
    else:
        suitAnimTrack = Sequence(Wait(1.8), suit.checkProToonShake(dmg, battle))
    return Parallel(suitAnimTrack, soundTrack2)

def doHemmorageHealing(attack):
    suit = attack['suit']
    battle = attack['battle']
    dmg = attack['target'][0]['hp']
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=0, node=suit)
    suitAnimTracks = Parallel()
    targets = attack['target']
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        suitAnimTrack = Sequence(suit.checkProToonShake(dmg, battle))
        if dmg > 0:
            suitAnimTracks.append(suitAnimTrack)
    return Parallel(suitAnimTrack, soundTrack2)

def doHemmorage(attack):
    suit = attack['suit']
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
        teeth = globalPropPool.getProp('teeth')
        teethAppearTrack = Sequence(getPropAppearTrack(teeth, suit.getRightHand(), posPoints, propDelay, Point3(3, 3, 3), scaleUpTime=propScaleUpTime))
        teethAppearTrack.append(Wait(suitDelay))
        teethAppearTrack.append(Func(battle.movie.needRestoreRenderProp, teeth))
        teethAppearTrack.append(Func(teeth.wrtReparentTo, battle))
        if dmg > 0:
            targetPos = toon.getPos(battle)
            suitTrack.append(Func(suit.headsUp, battle, targetPos))
            origPos, origHpr = battle.getActorPosHpr(suit)
            suitTrack.append(Func(suit.setHpr, battle, origHpr))
            notifyTrack = Sequence(Wait(3.1), Func(toon.setToonStatusEffect, 'hemmorage', modifier=25, turns=1), Func(toon.showHpTextNew, -int(dmg), text="VULNERABLE!", colorCode=1))
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
            animTrack = Sequence(Wait(throwDelay), ActorInterval(teeth, 'teeth', duration=throwDuration), ActorInterval(teeth, 'teeth', duration=0.3), Func(teeth.pose, 'teeth', 1), Wait(0.7), ActorInterval(teeth, 'teeth', duration=0.9))
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

def doLaffSteal(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    notifyTracks = Sequence()
    dmg = attack['target'][0]['hp']
    suitTrack = getSuitAnimTrackAttack(attack)
    BattleParticles.loadParticles()
    particleEffectRed = BattleParticles.createParticleEffect("LaffSteal")
    BattleParticles.setEffectTexture(particleEffectRed, "snow-particle")
    partTrack = getPartTrack(
        particleEffectRed,
        1e-05,
        suitTrack.getDuration(),
        [particleEffectRed, theSuit, 0],
        softStop=-1.0,
    )

    sfx = loader.loadSfx(
        "phase_13/audio/sfx/halloween/SA_laff_steal.ogg"
    )

    toonTrack = Parallel()
    for toon in battle.activeToons:
        # Toon Reaction
        reactionTrack = Sequence()
        reactionTrack.append(
            Func(toon.headsUp, battle, theSuit.getPos(battle))
        )
        reactionTrack.append(Wait(0.2))
        reactionTrack.append(ActorInterval(toon, "cringe", playRate=0.7))
        reactionTrack.append(Func(toon.loop, "neutral"))
        toonTrack.append(reactionTrack)

    healSfx = loader.loadSfx("phase_11/audio/sfx/LB_toonup.ogg")
    suitTrack = Sequence(suitTrack, Func(theSuit.setNeutralAnimationDrop))
    return Parallel(
        Sequence(
            Wait(2.0),
            Parallel(theSuit.checkSyphonHPErclaim(dmg),
            SoundInterval(healSfx, node=theSuit)),
        ),
        suitTrack,
        partTrack,
        SoundInterval(sfx, node=theSuit),
        toonTrack,
    )

def doPersonalTrainer(attack):
    suit = attack['suit']
    battle = attack['battle']
    target = attack['target']

    if not target:
        return Sequence()

    targetData = target[0]
    dmg = int(targetData.get('hp', 0))
    died = targetData.get('died', False)

    headTrack = Sequence()

    for headPart in suit.animatedHeadParts:
        headTrack.append(ActorInterval(headPart, 'summon-cog'))
        headTrack.append(Func(suit.setNeutralAnimationHead))

    selfDamageTracks = Parallel(getSuitAnimTrack(attack))

    damageTrack = Sequence(
        Parallel(
            Func(suit.showHpTextNew, -dmg),
            Func(suit.setHealthForMe, -dmg),
            Func(suit.updateHealthBar, 0)
        )
    )

    damageTrack.append(Func(suit.setNeutralAnimationDrop))

    soundTrack = getSoundTrack('SA_personal_trainer.ogg', node=suit)

    return Parallel(headTrack, soundTrack, selfDamageTracks, damageTrack)

def doGainsFromTheScrap(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    sacrificeData = None

    # =========================================================
    # FIND THE SACRIFICE TARGET
    # =========================================================
    for targetData in targets:
        if 'suit' not in targetData:
            continue

        if targetData.get('died', False) and targetData.get('hp', 0) > 0:
            sacrificeData = targetData
            break

    if sacrificeData is None:
        return Sequence()

    targetSuit = sacrificeData['suit']
    dmg = int(sacrificeData.get('hp', 0))

    healTracks = Parallel()
    headTrack = Sequence()

    # =========================================================
    # HEAD ANIMATION
    # =========================================================
    for headPart in suit.animatedHeadParts:
        headTrack.append(ActorInterval(headPart, 'sacrifice-cog'))
        headTrack.append(Func(suit.setNeutralAnimationHead))

    # =========================================================
    # SACRIFICED COG
    # =========================================================
    targetDeathTrack = Sequence(
        Wait(3.55),
        Parallel(
            Func(targetSuit.showHpTextNew, -dmg),
            Func(targetSuit.setHealthForMe, -dmg),
            Func(targetSuit.updateHealthBar, 0)
        ),
        MovieUtil.midairSuitExplodeTrack(targetSuit, battle),
        Func(targetSuit.makeDead)
    )

    # =========================================================
    # SMOKE
    # =========================================================
    smoke = loader.loadModel('phase_4/models/props/test_clouds')
    smoke.setColor(0.8, 0.7, 0.5, 1)
    smoke.setBillboardPointEye()

    smokeTrack = Sequence(
        Wait(3.55),
        Func(smoke.reparentTo, battle),
        Parallel(
            LerpScaleInterval(smoke, 0.2, Point3(4, 1, 4)),
            LerpColorScaleInterval(smoke, 1.0, Vec4(1, 1, 1, 0))
        ),
        Func(smoke.reparentTo, hidden),
        Func(smoke.clearColorScale),
        Func(smoke.removeNode)
    )

    # =========================================================
    # CAGE
    # =========================================================
    cage = loader.loadModel('phase_9/models/cogHQ/square_stomper')
    cagePosition = LerpHprInterval(cage, 0, Point3(0, -90, 0))

    shaft = cage.find('**/shaft')
    shaft.setScale(0.75, 120.0, 0.75)
    shaft.setPos(0, 0, 0)

    cagePos = [Point3(0, 0, 40.0), Point3(0, 0, 0)]

    cagePropTrack = Sequence(
        Wait(3.0),
        getPropAppearTrack(cage, targetSuit, cagePos, 0, scaleUpPoint=Point3(1.4), scaleUpTime=0),
        cagePosition,
        cage.posInterval(0.55, Point3(0, 0, 0.01), blendType='easeIn'),
        Sequence(Wait(1.0), cage.posInterval(2.0, Point3(0, 0, 40), blendType='easeIn')),
        Func(cage.removeNode)
    )

    # =========================================================
    # HEALING / ERFIT SELF DAMAGE
    # =========================================================
    for resultData in targets:
        if 'suit' not in resultData:
            continue

        resultSuit = resultData['suit']

        if resultSuit == targetSuit:
            continue

        heal = int(resultData.get('heal', 0))
        damage = int(resultData.get('hp', 0))
        died = resultData.get('died', False)

        if heal <= 0 and damage <= 0:
            continue

        resultTrack = Sequence(Wait(3.55))

        # -----------------------------------------------------
        # HEAL
        # -----------------------------------------------------
        if heal > 0:
            resultTrack.append(
                Parallel(
                    Func(resultSuit.showHpTextNew, heal),
                    Func(resultSuit.setHealthForMe, heal),
                    Func(resultSuit.updateHealthBar, 0)
                )
            )

        # -----------------------------------------------------
        # ERFIT SELF DAMAGE
        # -----------------------------------------------------
        if damage > 0:
            resultTrack.append(
                Parallel(
                    Func(resultSuit.showHpTextNew, -damage),
                    Func(resultSuit.setHealthForMe, -damage),
                    Func(resultSuit.updateHealthBar, 0)
                )
            )


        healTracks.append(resultTrack)

    # =========================================================
    # MAIN ERFIT TRACK
    # =========================================================
    suitTrack = Parallel(
        getSuitAnimTrack(attack),
        Sequence(
            Wait(5.55),
            Func(suit.showHpTextNew, 0, text='RIPPED!', colorCode=1)
        ),
        Func(suit.setSuitStatusEffect, 'ripped', modifier=5, mode='refreshModifier')
    )

    soundTrack = getSoundTrack('SA_gains_from_the_scrap.ogg', node=suit)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=3.55, node=suit)

    return Parallel(suitTrack, soundTrack2, headTrack, smokeTrack, targetDeathTrack, cagePropTrack, soundTrack, healTracks)

def doSacrifice(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    targetData = targets[0]

    if 'suit' not in targetData:
        return Sequence()

    targetSuit = targetData['suit']
    dmg = int(targetData.get('hp', 0))
    heal = int(targetData.get('heal', 0))
    died = targetData.get('died', False)

    puddleTracks = Parallel()
    moveTracks = Parallel()
    animTracks = Parallel()

    # =========================================================
    # SACRIFICE TARGET
    # =========================================================
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

    speechTrack = Sequence(
        Wait(1.8),
        Func(targetSuit.setChatAbsolute, random.choice(("To my realm I retuuuurnnnnn......!", "But I am not finished!", "No! Noooooo!", "Anything you wish, sire!")), CFSpeech | CFTimeout)
    )

    moveTrack = Sequence(
        Wait(1.8),
        LerpPosInterval(targetSuit, 0.9, Point3(0, 0, -3.1), other=puddle),
        LerpPosInterval(targetSuit, 0.4, Point3(0, 0, -9.1), other=puddle),
        Func(targetSuit.hide)
    )

    animTrack = Sequence(
        Wait(0.9),
        ActorInterval(targetSuit, 'flail-qs', endTime=1.75),
        ActorInterval(targetSuit, 'flail-qs', startTime=1.25, endTime=1.75),
        ActorInterval(targetSuit, 'flail-qs', startTime=1.25, endTime=1.25)
    )

    puddleTracks.append(puddleTrack)
    moveTracks.append(moveTrack)
    animTracks.append(animTrack)

    # =========================================================
    # TARGET DAMAGE
    # =========================================================
    targetDamageTrack = Sequence(Wait(1.8))

    if dmg > 0:
        targetDamageTrack.append(
            Parallel(
                Func(targetSuit.showHpTextNew, -dmg),
                Func(targetSuit.setHealthForMe, -dmg),
                Func(targetSuit.updateHealthBar, 0)
            )
        )

    if died:
        targetDamageTrack.append(Func(targetSuit.makeDead))

    # =========================================================
    # ERCLAIM HEAL
    # =========================================================
    healTrack = Sequence(Wait(1.8))

    if heal > 0:
        healTrack.append(
            Parallel(
                Func(suit.showHpTextNew, heal),
                Func(suit.setHealthForMe, heal),
                Func(suit.updateHealthBar, 0)
            )
        )

    # =========================================================
    # ERCLAIM MAIN ANIMATION
    # =========================================================
    suitTrack = Parallel(
        getSuitAnimTrack(attack),
        Func(suit.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier')
    )

    soundTrack = getSoundTrack('SA_sacrifice.ogg', delay=1.0)
    soundTrack2 = getSoundTrack('LB_toonup.ogg', delay=1.8)

    return Parallel(
        suitTrack,
        soundTrack2,
        speechTrack,
        moveTracks,
        animTracks,
        soundTrack,
        puddleTracks,
        targetDamageTrack,
        healTrack
    )

def doRiseFromTheScrap(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack, playRate=1.25)

    sfx = getSoundTrack(
        "SA_rise_from_the_scrap.ogg",
        delay=0,
        node=theSuit,
    )
    lightningSfx = globalBattleSoundCache.getSound("storm_lightning.ogg")

    oldcolor = MovieZap.lightningPreColor()
    darkenTime = 2.0
    lightenTime = 1.0
    darkenColor = (0.15, 0.15, 0.15, 1.0)
    normalColor = (1.0, 1.0, 1.0, 1.0)

    darkenTrack = Sequence(
        Func(theSuit.wrtReparentTo, render),
        Wait(0.25),
        Parallel(
            LerpColorScaleInterval(
                battle, darkenTime, darkenColor, blendType="easeIn"
            ),
            LerpColorScaleInterval(
                render, darkenTime, darkenColor, blendType="easeIn"
            ),
        ),
        Wait(1.5),
        Parallel(
            LerpColorScaleInterval(
                battle, lightenTime, normalColor, blendType="easeOut"
            ),
            LerpColorScaleInterval(
                render, lightenTime, oldcolor, blendType="easeOut"
            ),
        ),
        Func(MovieZap.lightningPostColor),
        Func(theSuit.wrtReparentTo, battle),
    )

    sfx2 = Sequence(
        Wait(0.7),
        SoundInterval(lightningSfx, node=None),
    )

    flashRed = Sequence(
        LerpColorScaleInterval(
            theSuit, 0.2, colorScale=VBase4(0.9, 0.1, 0.1, 1)
        ),
        LerpColorScaleInterval(theSuit, 0.6, colorScale=VBase4(1, 1, 1, 1)),
    )
    redTrack = Sequence(
        Wait(0.8),
        flashRed,
        Wait(0.5),
        flashRed,
        Wait(0.5),
        flashRed,
        Wait(0.5),
        flashRed,
    )

    suitTrack = Sequence(suitTrack)
    return Parallel(suitTrack, darkenTrack, redTrack, sfx, sfx2)

def doScopeCreep(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    suitTrack = getSuitAnimTrack(attack, playRate=1.25)

    sfx = getSoundTrack(
        "SA_rise_from_the_scrap.ogg",
        delay=0,
        node=theSuit,
    )
    lightningSfx = globalBattleSoundCache.getSound("storm_lightning.ogg")

    oldcolor = MovieZap.lightningPreColor()
    darkenTime = 2.0
    lightenTime = 1.0
    darkenColor = (0.15, 0.15, 0.15, 1.0)
    normalColor = (1.0, 1.0, 1.0, 1.0)

    darkenTrack = Sequence(
        Func(theSuit.wrtReparentTo, render),
        Wait(0.25),
        Parallel(
            LerpColorScaleInterval(
                battle, darkenTime, darkenColor, blendType="easeIn"
            ),
            LerpColorScaleInterval(
                render, darkenTime, darkenColor, blendType="easeIn"
            ),
        ),
        Wait(1.5),
        Parallel(
            LerpColorScaleInterval(
                battle, lightenTime, normalColor, blendType="easeOut"
            ),
            LerpColorScaleInterval(
                render, lightenTime, oldcolor, blendType="easeOut"
            ),
        ),
        Func(MovieZap.lightningPostColor),
        Func(theSuit.wrtReparentTo, battle),
    )

    sfx2 = Sequence(
        Wait(0.7),
        SoundInterval(lightningSfx, node=None),
    )

    flashRed = Sequence(
        LerpColorScaleInterval(
            theSuit, 0.2, colorScale=VBase4(0.9, 0.1, 0.1, 1)
        ),
        LerpColorScaleInterval(theSuit, 0.6, colorScale=VBase4(1, 1, 1, 1)),
    )
    redTrack = Sequence(
        Wait(0.8),
        flashRed,
        Wait(0.5),
        flashRed,
        Wait(0.5),
        flashRed,
        Wait(0.5),
        flashRed,
    )

    suitTrack = Sequence(suitTrack)
    suitTrack.append(Sequence(Parallel(Func(theSuit.showHpTextNew, 0, text="+5% Defense!", colorCode=1)), Func(theSuit.setSuitStatusEffect, 'scopeCreep', modifier=5, mode='refreshModifier')))
    return Parallel(suitTrack, darkenTrack, redTrack, sfx, sfx2)
