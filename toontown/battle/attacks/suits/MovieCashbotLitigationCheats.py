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


def doPayrollProcessing(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    healSound = getSoundTrack('LB_toonup.ogg')
    suitTracks = Parallel()
    liftTracks = Parallel()
    for suit in battle.activeSuits:
        liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
        liftEffect.setPos(suit.getPos(battle))
        liftEffect.setZ(liftEffect.getZ() - 1.3)
        liftTracks.append(getPartTrack(liftEffect, 4, 4.0, [liftEffect, battle, 0], softStop=-1))
        suitTrack = Sequence()
        suitTrack.append(Wait(4))
        suitTrack.append(Func(suit.checkPayrollProcessing))
        suitTracks.append(suitTrack)
        if suit.dna.name != 'payman':
            suitTrack.append(Parallel(healSound, Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                           CFSpeech | CFTimeout)))
        suitTracks.append(Sequence(getSuitAnimTrack(attack, playRate=1.5)))
        suitTracks.append(Wait(6.5))
    posPoints = [Point3(-0.3468208092485554, -0.5202312138728331, -0.08670520231213885), VBase3(-7.814761215629517, -177.91907514450867, -188.3236994219653)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = globalPropPool.getProp('bounced-check')
        texture = loader.loadTexture('phase_5/maps/battle/ttcc_suitprops_palette_1_alt.png')
        knife.setTexture(texture, 1)
        knifeTrack = Sequence(
            getPropAppearTrack(
                knife,
                theSuit.getRightHand(),
                posPoints,
                0.5,
                VBase3(8.5, 8.5, 8.5),
                scaleUpTime=0.5
            ),
            Wait(.95),

            Parallel(
                getThrowTrack(knife, (0, 0, suit.getHeight() + 2.5), 1.5, suit, -30.288),
                LerpHprInterval(knife, 1.0, VBase3(0, -90, 0))
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
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4)
    return Parallel(suitTracks, soundTrack2, liftTracks, soundTrack, knifeTracks)

def doPerformanceBonus(attack):
    suit = attack['suit']
    theSuit = attack['suit']
    battle = attack['battle']
    healSound = getSoundTrack('LB_toonup.ogg')
    suitTracks = Parallel()
    liftTracks = Parallel()
    for suit in battle.activeSuits:
        liftEffect = BattleParticles.createParticleEffect('InsuranceLift')
        liftEffect.setPos(suit.getPos(battle))
        liftEffect.setZ(liftEffect.getZ() - 1.3)
        if not suit.getManager():
            liftTracks.append(getPartTrack(liftEffect, 4, 4.0, [liftEffect, battle, 0], softStop=-1))
        suitTrack = Sequence()
        suitTrack.append(Wait(4))
        suitTrack.append(Func(suit.checkPerformanceBonus))
        suitTracks.append(suitTrack)
        if not suit.getManager():
            suitTrack.append(Parallel(healSound, Func(suit.setChatAbsolute, random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                           CFSpeech | CFTimeout)))
        suitTracks.append(Sequence(getSuitAnimTrack(attack, playRate=1.5)))
        suitTracks.append(Wait(6.5))
    posPoints = [Point3(0.88, -2.21917, -0.22), VBase3(10, 250, -10)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = globalPropPool.getProp('shredder-paper')
        knifeTrack = Sequence(
            getPropAppearTrack(
                knife,
                theSuit.getRightHand(),
                posPoints,
                0.5,
                VBase3(1.2, 1.2, 1.2),
                scaleUpTime=0.5
            ),
            Wait(.95),

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
        if not suit.getManager():
            knifeTracks.append(knifeTrack)
    soundTrack2 = getSoundTrack('SA_extra_tip.ogg', delay=2, node=suit)
    soundTrack = getSoundTrack('LB_toonup.ogg', delay=4)
    return Parallel(suitTracks, soundTrack2, liftTracks, soundTrack, knifeTracks)

def doOverextendedLeverage(attack):
    suit = attack['suit']
    notifyTracks = Parallel()
    suitTrack = Sequence(getSuitAnimTrack(attack), Func(suit.setSuitStatusEffect, 'vulnerable', modifier=10, mode='refreshModifier'))
    soundTrack2 = getSoundTrack('SA_protoon_shake.ogg', delay=0.5, node=suit)
    suitAnimTrack = Sequence(Parallel(ActorInterval(suit, 'quick-jump', duration=1.3)),
                             ActorInterval(suit, 'slip-forward'), Func(suit.setNeutralAnimationDrop))
    cameraTrack = Wait(5.0)
    notifyTracks.append(Func(suit.showHpString, "+10% Vulnerable!"))
    notifyTracks.append(Parallel(soundTrack2, suitTrack, suitAnimTrack, cameraTrack))
    return Sequence(notifyTracks)

def doProtectedRacket(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence(ActorInterval(attack['suit'], 'summon-cog', startTime=suit.getDuration('summon-cog'), endTime=suit.getDuration('summon-cog') - 1), Wait(1.0),
                         ActorInterval(attack['suit'], 'summon-cog', startTime=suit.getDuration('summon-cog') - 1, endTime=suit.getDuration('summon-cog') - 0.25),
                         Func(suit.setNeutralAnimationDrop), Wait(2.0))
    suitTrack2 = Sequence(getSuitAnimTrack(attack))
    soundTrack = SoundInterval(globalBattleSoundCache.getSound('SA_life_insurance_register.ogg'))
    makeRacket = Func(suit.setSuitStatusEffect, 'protectionRacket', modifier=int(attack['target'][0]['hp']))
    return Parallel(suitTrack, makeRacket, soundTrack, suitTrack2)

def doProfiteering(attack, ind):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']

    if not targets:
        return Sequence()

    targetData = targets[0]
    targetSuit = targetData['suit']

    dmg = targetData.get('hp', 0)
    heal = targetData.get('heal', 0)
    died = targetData.get('died', 0)

    origPos, origHpr = battle.getActorPosHpr(suit)
    targetSuitPos, targetSuitHpr = battle.getActorPosHpr(targetSuit)

    revives = targetSuit.getSkeleRevives()

    # =========================================================
    # TARGET COG REACTION
    # =========================================================

    targetSuitTrack = Sequence()
    racketeerSuitTrack = Sequence()

    if dmg > 0:
        if not died:
            targetSuitTrack.append(Sequence(Wait(5.25), Parallel(ActorInterval(targetSuit, 'flatten', endTime=0.55), Func(targetSuit.showHpTextNew, -dmg, text='SYPHONED!', colorCode=1), Func(targetSuit.setHealthForMe, -dmg), Func(targetSuit.updateHealthBar, 0))))
        else:
            targetSuitTrack.append(Sequence(Wait(5.25), Parallel(Func(targetSuit.showHpTextNew, -dmg, text='SYPHONED!', colorCode=1), Func(targetSuit.setHealthForMe, -dmg), Func(targetSuit.updateHealthBar, 0))))

    if heal > 0:
        racketeerSuitTrack.append(Sequence(Wait(5.25), Parallel(Func(suit.showHpTextNew, heal, text='SYPHONED!', colorCode=1), Func(suit.setHealthForMe, + heal), Func(suit.updateHealthBar, 0))))

    # =========================================================
    # SURVIVED
    # =========================================================

    if not died:
        targetSuitTrack.append(ActorInterval(targetSuit, 'flatten', startTime=0.55))
        targetSuitTrack.append(Func(targetSuit.setNeutralAnimationDrop))

    # =========================================================
    # REVIVED / DIED
    # =========================================================
    else:
        if targetSuit.isVirtual:
            targetSuitTrack.append(ActorInterval(targetSuit, 'flatten', startTime=0.55))
            targetSuitTrack.append(MovieUtil.createVirtualSuitDeathTrack(targetSuit, battle))
            targetSuitTrack.append(Func(targetSuit.makeDead))
        else:
            targetSuitTrack.append(Parallel(ActorInterval(targetSuit, 'flatten', endTime=0.55), MovieUtil.createSuitCrashTrack(targetSuit, battle, 7)))
            targetSuitTrack.append(Func(targetSuit.makeDead))

    # =========================================================
    # RACKETEER MOVEMENT
    # =========================================================

    soundTrack3 = getSoundTrack('SA_protoon_shake.ogg', delay=0.5, node=suit)

    suitAnimTrack = Sequence(Parallel(soundTrack3, Sequence(Wait(.75), LerpPosInterval(suit, .55, origPos, other=battle)), Sequence(ActorInterval(suit, 'quick-jump', duration=1.3), ActorInterval(suit, 'slip-forward', playRate=1.25))), Func(suit.setNeutralAnimationDrop))

    moveTrack = Sequence(
        ActorInterval(suit, 'sacrifice-cog', endTime=1.5),
        Parallel(Sequence(ActorInterval(suit, 'quick-jump', endTime=.5), Wait(.5)), Sequence(Func(suit.enableBlend), LerpAnimInterval(suit, duration=.5, startAnim='sacrifice-cog', endAnim='quick-jump', startWeight=0.0, endWeight=1.0, blendType='easeInOut'), Func(suit.disableBlend))),
        Wait(.25),
        Parallel(ActorInterval(suit, 'quick-jump', startTime=.5, endTime=1.0), Sequence(Wait(.25), LerpPosInterval(suit, 0.5, Point3(0, 0, 10), other=suit))),
        Wait(1.5),
        LerpPosInterval(suit, 0.25, Point3(0, 0, 0), other=targetSuit),
        ActorInterval(suit, 'quick-jump', startTime=4.5),
        Func(suit.setNeutralAnimationDrop),
        Func(suit.setPos, targetSuit, Point3(0, 0, 0)),
        Wait(0.5),
        suitAnimTrack
    )

    suitTrack = Sequence(getSuitAnimTrack(attack))
    soundTrack2 = getSoundTrack('SA_castling.ogg', delay=2.0)
    soundTrack4 = getSoundTrack('SA_gains_from_the_scrap2.ogg')

    return Parallel(suitTrack, racketeerSuitTrack, soundTrack2, soundTrack4, targetSuitTrack, moveTrack)

def doExtortion(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    partTracks = Parallel()
    partTracks4 = Parallel()
    toonAnimTracks = Parallel()
    suitTrack = Sequence(getSuitAnimTrack(attack))
    selfDamageTracks = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sprayEffect2 = BattleParticles.createParticleEffect('DemotionSprayExtortion')
        BattleParticles.setEffectTexture(sprayEffect2, 'dollar-sign')
        facePoint = __toonFacePoint(toon)
        partTrack4 = getPartTrack(sprayEffect2, 4, 2.0, [sprayEffect2, toon, 0], softStop=-1)
        partTracks4.append(partTrack4)
        toonAnimTrack = Sequence(Wait(4), ActorInterval(toon, 'slip-forward', playRate=.675))
        toonAnimTracks.append(toonAnimTrack)
    dodgeAnims = [['duck', 1e-06, 0.8]]
    damageAnims = []
    damageAnims.append(['cringe',
                        0.01,
                        0,
                        0.5])
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.4, 0.5, startTime=0.5))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.5, startTime=0.9))
    damageAnims.extend(getSplicedLerpAnims('cringe', 0.3, 0.6, startTime=1.2))
    damageAnims.append(['cringe', 2.6, 1.5])
    toonTrack = getToonTracks(attack, 4, ['nothing'], 0, ['neutral'])
    multiTrackList = Parallel(suitTrack, toonTrack, toonAnimTracks, selfDamageTracks, partTracks4)
    soundTrack = getSoundTrack('SA_gains_from_the_scrap.ogg', delay=0, node=suit)
    soundTrack2 = getSoundTrack('SA_life_insurance_register.ogg', delay=4, node=suit)
    multiTrackList.append(soundTrack)
    multiTrackList.append(soundTrack2)
    return multiTrackList

def doProtectionPayout(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    damageDelay = 1.7
    sprayEffects = [BattleParticles.createParticleEffect(file='spinSpray') for t in targets]
    suitTrack = Sequence(Wait(1.0), getSuitAnimTrack(attack))
    sprayTracks = getPartTracks(attack, sprayEffects, 1.0, 1.9, 0)
    spinTracks1 = Parallel()
    spinTracks2 = Parallel()
    spinTracks3 = Parallel()
    partTracks4 = Parallel()
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
        sprayEffect2 = BattleParticles.createParticleEffect('DemotionSprayExtortion')
        BattleParticles.setEffectTexture(sprayEffect2, 'dollar-sign')
        facePoint = __toonFacePoint(toon)
        partTrack4 = getPartTrack(sprayEffect2, 2.0, 4.0, [sprayEffect2, toon, 0], softStop=-1)
        partTracks4.append(partTrack4)
        spinEffect1 = BattleParticles.createParticleEffect(file='organizeEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='organizeEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='organizeEffect')
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
        notifyTrack = Sequence(Wait(3.0), Func(toon.showHpTextNew, -int(dmg)))
        if dmg > 0:
            spinTracks1.append(getPartTrack(spinEffect1, 0, 7.9, [spinEffect1, battle, 0], softStop=-2))
            spinTracks2.append(getPartTrack(spinEffect2, 0, 7.9, [spinEffect2, battle, 0], softStop=-2))
            spinTracks3.append(getPartTrack(spinEffect3, 0, 7.9, [spinEffect3, battle, 0], softStop=-2))
            soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=0))
            soundTracks.append(getSoundTrack('SA_life_insurance_register.ogg', delay=0))
            soundTracks.append(getSoundTrack('ttr_s_ene_bat_embezzle.ogg', delay=2.0, node=suit))
            notifyTracks.append(notifyTrack)
    toonDamageTrack = getToonTracksCheat(attack, damageDelay=0, splicedDamageAnims=damageAnims, dodgeDelay=0.91, dodgeAnimNames=['neutral'], showDamageExtraTime=3.0)
    return Parallel(toonTracks, toonSpinTracks, partTracks4, suitTrack, toonDamageTrack, spinTracks1, spinTracks2, spinTracks3, notifyTracks, soundTracks)

def doRacketeering(attack):
    suit = attack['suit']
    targets = attack['target']
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        toonTrack = Parallel(Func(toon.setToonStatusEffect, 'gagBan'))
        toonTracks.append(toonTrack)
    suitTrack = Parallel(getSuitAnimTrack(attack), Sequence(ActorInterval(suit, 'smile'),
                                                            Func(suit.setNeutralAnimationDrop)))
    suitTrack.append(Wait(3.0))
    soundTrack = getSoundTrack('SA_rush_job_target.ogg', node=suit)
    return Parallel(suitTrack, toonTracks, soundTrack)

def doCompensation(attack):
    attacker = attack['suit']
    battle = attack['battle']
    targets = attack.get('target', [])

    if not targets:
        return Sequence()

    suitTracks2 = Parallel(Wait(5.0))
    targetTracks = Parallel()

    attackerTrack = Sequence(
        Parallel(
            getSuitAnimTrack(attack),
            ActorInterval(attacker, 'sacrifice-cog', endTime=.75)
        ),

        Parallel(
            Func(attacker.enableBlend),
            ActorInterval(attacker, 'neutral', loop=1),
            LerpAnimInterval(attacker, duration=0.75, startAnim='sacrifice-cog', endAnim='neutral', startWeight=0.0, endWeight=1.0, blendType='easeInOut')
        ),

        Func(attacker.disableBlend),
        Func(attacker.setNeutralAnimationDrop)
    )

    for targetData in targets:
        if 'suit' not in targetData:
            continue

        targetSuit = targetData['suit']

        targetTrack = Sequence(
            Wait(0.5),

            Parallel(
                Parallel(SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'), node=targetSuit), Sequence(ActorInterval(targetSuit, 'effort', startTime=targetSuit.getDuration('effort'), endTime=max(0, targetSuit.getDuration('effort') - 1.0), playRate=-1.0),
                                                           ActorInterval(targetSuit, 'effort', startTime=max(0, targetSuit.getDuration('effort') - 1.0))),
                                                  Func(targetSuit.showHpString, "+5% Damage!"), Func(targetSuit.setSuitStatusEffect, 'lureResist', modifier=1), 
                                                  Func(targetSuit.setSuitStatusEffect, 'damageUp', modifier=5, mode='refreshModifier')), Func(targetSuit.setNeutralAnimationDrop),
            )
        )

        targetTracks.append(targetTrack)

    return Parallel(
        attackerTrack, targetTracks,
        suitTracks2
    )

def doPeckingOrderGroup(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    throwDuration = 3.03
    throwDelay = 2
    suitTracks = Parallel()
    soundTracks = Parallel()
    notifyTracks = Parallel()
    numBirds = random.randint(10, 20)
    birdTracks = Parallel()
    propDelay = 1.5
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        soundTrack = getSoundTrack('tt_s_ara_cfg_eagleCry.ogg', delay=2, node=suit)
        for i in range(0, numBirds):
            next = globalPropPool.getProp('bird')
            #next.setScale(0.01)
           # next.reparentTo(suit.getRightHand())
            #next.setPos(random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3)
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
            birdTrack = Sequence(Wait(throwDelay), Func(next.setScale, 0.01),
                                 Func(next.reparentTo, suit.getRightHand()),
                                 Func(next.setPos, random.random() * 0.6 - 0.3, random.random() * 0.6 - 0.3,
                                      random.random() * 0.6 - 0.3), Func(battle.movie.needRestoreRenderProp, next),
                                 Func(next.wrtReparentTo, battle), Func(next.setHpr, Point3(90, 20, 0)),
                                 LerpPosInterval(next, 0.5, hitPoint))
            scaleTrack = Sequence(Wait(throwDelay), LerpScaleInterval(next, 0.5, Point3(9, 9, 9)), LerpScaleInterval(next, .5, Point3(0, 0, 0)))
            if dmg > 0:
                birdTracks.append(Sequence(Parallel(birdTrack, scaleTrack), Func(next.removeNode)))
        suitTrack = Sequence(getSuitTrack(attack, playRate=1.5))
        notifyTrack = Sequence(Wait(2.5), Func(toon.showHpText, - int(dmg)))
        if dmg > 0:
            soundTracks.append(soundTrack)
            suitTracks.append(suitTrack)
            notifyTracks.append(notifyTrack)
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
    toonTrack = getToonTracksCheat(attack, damageDelay=2.5, splicedDamageAnims=damageAnims, dodgeDelay=1.75, dodgeAnimNames=['neutral'], showMissedExtraTime=1.1)
    return Parallel(suitTracks, toonTrack, soundTracks, notifyTracks, birdTracks)

def doExtortion2(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    partTracks4 = Parallel()
    selfDamageTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    notifyTracks = Parallel()
    toonAnimTracks = Parallel()
    BattleParticles.loadParticles()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        sprayEffect = BattleParticles.createParticleEffect('DemotionSpray2')
        sprayEffect2 = BattleParticles.createParticleEffect('DemotionSpray2')
        freezeEffect = BattleParticles.createParticleEffect('DemotionFreeze2')
        unFreezeEffect = BattleParticles.createParticleEffect(file='demotionUnFreeze2')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle')
        BattleParticles.setEffectTexture(freezeEffect, 'snow-particle')
        BattleParticles.setEffectTexture(unFreezeEffect, 'snow-particle')
        BattleParticles.setEffectTexture(sprayEffect2, 'snow-particle',
                                         color=Vec4(1, 0, 0, 1))
        facePoint = __toonFacePoint(toon)
        freezeEffect.setPos(0, 0, facePoint.getZ())
        unFreezeEffect.setPos(0, 0, facePoint.getZ())
        partTrack4 = getPartTrack(sprayEffect, 4, 2.0, [sprayEffect2, toon, 0], softStop=-1)
        toonAnimTrack = Sequence(Wait(4), ActorInterval(toon, 'slip-forward', playRate=.5))
        notifyTrack = Sequence(Wait(4), Func(toon.showHpText, - int(dmg)))
        if dmg > 0:
            partTracks4.append(partTrack4)
            toonAnimTracks.append(toonAnimTrack)
            notifyTracks.append(notifyTrack)
            toonAnimTracks.append(toonAnimTrack)
            partTracks4.append(partTrack4)
    toonTrack = getToonTracksCheat(attack, 4, ['nothing'], 0, ['neutral'])
    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
    soundTrack = getSoundTrack('SA_gains_from_the_scrap.ogg', delay=0, node=suit)
    multiTrackList = Parallel(suitTrack, toonAnimTracks, toonTrack, notifyTracks, soundTrack, selfDamageTracks, partTracks4)
    return multiTrackList
