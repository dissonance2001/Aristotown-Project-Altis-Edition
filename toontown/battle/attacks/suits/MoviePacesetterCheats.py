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
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.PythonUtil import lerp
from toontown.battle.BattleSounds import *
from toontown.battle.SuitBattleGlobals import *
from toontown.chat.ChatGlobals import *
from toontown.toonbase import ToontownBattleGlobals
from toontown.battle import BattleProps
from toontown.suit import Suit
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from toontown.suit.SuitDNA import *
from toontown.toonbase.ToontownTimer import ToontownTimer
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

def doTurn1(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(3.0))
    return Parallel(suitTrack)

def doTurn2(attack):
    suit = attack['suit']
    suitTrack = Sequence(getSuitAnimTrack(attack), Wait(3.0))
    return Parallel(suitTrack)

def doEarlyOverclocked(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    from toontown.suit.DistributedPacesetterBoss import DistributedPacesetterBoss
    musicTrack = Sequence()
    for obj in base.cr.doId2do.values():
        if isinstance(obj, DistributedPacesetterBoss):
            musicTrack.append(Func(obj.stopPhaseOneMusic))
            musicTrack.append(Parallel(Wait(6.75), getSoundTrack('SA_overclocked.ogg', node=theSuit)))
            musicTrack.append(Func(obj.startPhaseTwoMusic))
    speedTrack = Parallel()
    startScale = 1.0
    endScale = 999.99
    timer = ToontownTimer()
    timer.setScale(.5)
    timer.hide()
    OnscreenText(
        parent=timer,
        text='Battle Speed',
        scale=0.27,
        pos=(0, -0.55),
        fg=(1, 1, 1, 1),
        font=ToontownGlobals.getSignFont(),
    )

    def setTime(time):
        if timer:
            timer.setTimeStr('x{:.2f}'.format(time), scale=0.145)
    setTime(startScale)

    def lerpTimerText(t):
        setTime(lerp(startScale, endScale, t))
    shredder = globalPropPool.getProp('backpack_pacesetter')
    paperPosPoints = [Point3(0.04341534008683112, 0, 0.21707670043415206), VBase3(0, 20.057887120115794, 90)]
    shredderPropTrack = Sequence(getPropTrack(shredder, theSuit.getLeftHand(), paperPosPoints, 0, 7, scaleUpTime=0))
    shredderPropTrack.append(Wait(6.75))
    shredderPropTrack.append(Func(shredder.removeNode))
    toonPos = theSuit.getPos(battle)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + theSuit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(6.75))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=6.75)
    # Make our sequence.
    timerTrack = Sequence(Wait(6.75),
        # Enter Interval
        Func(timer.show),
        LerpPosInterval(
            timer, .25,
            pos=(0, 0, 0), startPos=(0, 0, 2.0),
            blendType='easeOut',
        ),
        # Hold Interval
        LerpFunctionInterval(
            lerpTimerText, duration=theSuit.getDuration('come-on'), blendType='easeInOut',
        ),
        # Leave Interval
        LerpPosInterval(
            timer, .25,
            pos=(0, 0, -2.0), startPos=(0, 0, 0),
            blendType='easeIn',
        ),
        # Cleanup
        Func(timer.destroy),
    )
    for headPart in theSuit.animatedHeadParts:
        speedTrack.append(Sequence(ActorInterval(headPart, 'overclocked'), Func(theSuit.setNeutralAnimationHead)))
    suitTrack = Sequence(Parallel(
    getSuitAnimTrack(attack)),
    Parallel(Func(theSuit.enableBlend), 
        ActorInterval(theSuit, 'neutral', loop=1),
        LerpAnimInterval(
            theSuit,
            duration=.25,
            startAnim='overclocked',
            endAnim='neutral',
            startWeight=0.0,
            endWeight=1.0,
            blendType='easeInOut'
        )
    ),

    Func(theSuit.disableBlend),
    Func(theSuit.setNeutralAnimationDrop), Wait(2.0)
)
    speedTrack.append(Func(theSuit.makeBattleSpeed, 8))
    speedTrack.append(LerpColorScaleInterval(theSuit.getGeomNode(), 0.5, (0.808, 0.682, 0.82, 1), blendType='easeIn'))
    speedTrack.append(Func(theSuit.setSuitStatusEffect, 'overclocked'))
    return Parallel(speedTrack, soundTrack, shredderPropTrack, timerTrack, musicTrack, suitTrack)

def doOverclocked(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    from toontown.suit.DistributedPacesetterBoss import DistributedPacesetterBoss
    musicTrack = Sequence()
    for obj in base.cr.doId2do.values():
        if isinstance(obj, DistributedPacesetterBoss):
            musicTrack.append(Func(obj.stopPhaseOneMusic))
            musicTrack.append(Parallel(Wait(6.75), getSoundTrack('SA_overclocked.ogg', node=theSuit)))
            musicTrack.append(Func(obj.startPhaseTwoMusic))
    speedTrack = Parallel()
    startScale = 1.0
    endScale = 999.99
    timer = ToontownTimer()
    timer.setScale(.5)
    timer.hide()
    OnscreenText(
        parent=timer,
        text='Battle Speed',
        scale=0.27,
        pos=(0, -0.55),
        fg=(1, 1, 1, 1),
        font=ToontownGlobals.getSignFont(),
    )

    def setTime(time):
        if timer:
            timer.setTimeStr('x{:.2f}'.format(time), scale=0.145)
    setTime(startScale)

    def lerpTimerText(t):
        setTime(lerp(startScale, endScale, t))
    shredder = globalPropPool.getProp('backpack_pacesetter')
    paperPosPoints = [Point3(0.04341534008683112, 0, 0.21707670043415206), VBase3(0, 20.057887120115794, 90)]
    shredderPropTrack = Sequence(getPropTrack(shredder, theSuit.getLeftHand(), paperPosPoints, 0, 7, scaleUpTime=0))
    shredderPropTrack.append(Wait(6.75))
    shredderPropTrack.append(Func(shredder.removeNode))
    toonPos = theSuit.getPos(battle)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + theSuit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(Wait(6.75))
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    soundTrack = getSoundTrack('ENC_cogfall_apart_%s.ogg' % random.randint(1, 6), delay=6.75)
    # Make our sequence.
    timerTrack = Sequence(Wait(6.75),
        # Enter Interval
        Func(timer.show),
        LerpPosInterval(
            timer, .25,
            pos=(0, 0, 0), startPos=(0, 0, 2.0),
            blendType='easeOut',
        ),
        # Hold Interval
        LerpFunctionInterval(
            lerpTimerText, duration=theSuit.getDuration('come-on'), blendType='easeInOut',
        ),
        # Leave Interval
        LerpPosInterval(
            timer, .25,
            pos=(0, 0, -2.0), startPos=(0, 0, 0),
            blendType='easeIn',
        ),
        # Cleanup
        Func(timer.destroy),
    )
    for headPart in theSuit.animatedHeadParts:
        speedTrack.append(Sequence(ActorInterval(headPart, 'overclocked'), Func(theSuit.setNeutralAnimationHead)))
    suitTrack = Sequence(Parallel(
    getSuitAnimTrack(attack)),
    Parallel(Func(theSuit.enableBlend), 
        ActorInterval(theSuit, 'neutral', loop=1),
        LerpAnimInterval(
            theSuit,
            duration=.25,
            startAnim='overclocked',
            endAnim='neutral',
            startWeight=0.0,
            endWeight=1.0,
            blendType='easeInOut'
        )
    ),

    Func(theSuit.disableBlend),
    Func(theSuit.setNeutralAnimationDrop), Wait(2.0)
)
    speedTrack.append(Func(theSuit.makeBattleSpeed, 6))
    speedTrack.append(LerpColorScaleInterval(theSuit.getGeomNode(), 0.5, (0.808, 0.682, 0.82, 1), blendType='easeIn'))
    speedTrack.append(Func(theSuit.setSuitStatusEffect, 'overclocked'))
    return Parallel(speedTrack, soundTrack, shredderPropTrack, timerTrack, musicTrack, suitTrack)

def doComeOn(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    from toontown.suit.DistributedPacesetterBoss import DistributedPacesetterBoss
    musicTrack = Parallel()
    suitTrack = Sequence(musicTrack)
    for obj in base.cr.doId2do.values():
        if isinstance(obj, DistributedPacesetterBoss):
            musicTrack.append(Func(obj.setBattleMusicSpeed))
    speedTrack = Parallel()
    if not theSuit.battleSpeed > 0:
        startScale = 1 + (theSuit.getBattleSpeed())
        endScale = 1 + (theSuit.getBattleSpeed() + .25)
    else:
        startScale = (theSuit.getBattleSpeed())
        endScale = (theSuit.getBattleSpeed() + .25)
    timer = ToontownTimer()
    timer.setScale(.5)
    timer.hide()
    OnscreenText(
        parent=timer,
        text='Battle Speed',
        scale=0.27,
        pos=(0, -0.55),
        fg=(1, 1, 1, 1),
        font=ToontownGlobals.getSignFont(),
    )

    def setTime(time):
        if timer:
            timer.setTimeStr('x{:.2f}'.format(time), scale=0.145)
    setTime(startScale)

    def lerpTimerText(t):
        setTime(lerp(startScale, endScale, t))

    # Make our sequence.
    timerTrack = Sequence(
        # Enter Interval
        Func(timer.show),
        LerpPosInterval(
            timer, .25,
            pos=(0, 0, 0), startPos=(0, 0, 2.0),
            blendType='easeOut',
        ),
        # Hold Interval
        LerpFunctionInterval(
            lerpTimerText, duration=theSuit.getDuration('come-on'), blendType='easeInOut',
        ),
        # Leave Interval
        LerpPosInterval(
            timer, .25,
            pos=(0, 0, -2.0), startPos=(0, 0, 0),
            blendType='easeIn',
        ),
        # Cleanup
        Func(timer.destroy),
    )
    for headPart in theSuit.animatedHeadParts:
        speedTrack.append(Sequence(ActorInterval(headPart, 'come-on'), Func(theSuit.setNeutralAnimationHead)))
    suitTrack = Sequence(Parallel(
    getSuitAnimTrack(attack)),
    Parallel(Func(theSuit.enableBlend), 
        ActorInterval(theSuit, 'neutral', loop=1),
        LerpAnimInterval(
            theSuit,
            duration=.25,
            startAnim='come-on',
            endAnim='neutral',
            startWeight=0.0,
            endWeight=1.0,
            blendType='easeInOut'
        )
    ),

    Func(theSuit.disableBlend),
    Func(theSuit.setNeutralAnimationDrop), Wait(2.0)
)
    for suit in battle.activeSuits:
        speedTrack.append(Func(suit.checkBattleSpeed2, theSuit, + .25))
    return Parallel(speedTrack, timerTrack, musicTrack, suitTrack)

def doHurrySickness(attack):
    suit = attack['suit']
    battle = attack['battle']
    damageDelay = 1.5
    suitTrack = Parallel()
    targets = attack['target']
    notifyTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    for suit in battle.activeSuits:
        suitTracks.append(Func(suit.clearSuitStatusEffect, 'rushJob'))
    hitAtLeastOneToon = 0
    for t in targets:
        dmg = t['hp']
        if dmg > 0:
            hitAtLeastOneToon = 1
    if hitAtLeastOneToon:
        suitTrack.append(getSuitAnimTrack(attack))
        soundTracks.append(getSoundTrack('SA_hurry_sickness.ogg', delay=0, node=suit))
        soundTracks.append(getSoundTrack('SA_finger_wag.ogg', delay=1.3, node=suit))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            notifyTracks.append(Sequence(Wait(1.5), Parallel(Func(toon.showHpTextNew, -int(dmg)))))
            notifyTracks.append(Parallel(Func(toon.setToonStatusEffect, 'hurrySickness', modifier=40, turns=2, mode='keepHighest')))
    toonTracks = getToonTracksCheat(attack, damageDelay, ['slip-backward'], 0, ['nothing'])
    return Parallel(suitTrack, suitTracks, toonTracks, notifyTracks, soundTracks)

def doHurrySicknessBan(attack):
    suit = attack['suit']
    battle = attack['battle']
    damageDelay = 1.5
    suitTrack = Parallel()
    targets = attack['target']
    notifyTracks = Parallel()
    suitTracks = Parallel()
    soundTracks = Parallel()
    hitAtLeastOneToon = 0
    for t in targets:
        dmg = t['hp']
        if dmg > 0:
            hitAtLeastOneToon = 1
    if hitAtLeastOneToon:
        suitTrack.append(getSuitAnimTrack(attack))
        soundTracks.append(getSoundTrack('SA_hurry_sickness.ogg', delay=0, node=suit))
        soundTracks.append(getSoundTrack('SA_finger_wag.ogg', delay=1.3, node=suit))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        if dmg > 0:
            notifyTracks.append(Sequence(Wait(1.5), Parallel(Func(toon.showHpTextNew, -int(dmg)))))
            notifyTracks.append(Parallel(Func(toon.setToonStatusEffect, 'hurrySicknessBan', modifier=40, turns=2, mode='keepHighest')))
    toonTracks = getToonTracksCheat(attack, damageDelay, ['slip-backward'], 0, ['nothing'])
    return Parallel(suitTrack, toonTracks, notifyTracks, soundTracks)


def doMovingGoalposts(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles() # We need to be able to change the color of the particle effects.
    damageDelay = 1.7
    toonAnimTracks = Parallel()
    # We want to handle the particle effect differently from Spin since we will be customizing these particle effects.
    sprayEffects = []
    for t in targets:
        sprayEffect = BattleParticles.createParticleEffect(file='spinSpray')
        BattleParticles.setEffectTexture(sprayEffect, 'snow-particle', color=Vec4(1, 0, 0, 1))
        sprayEffects.append(sprayEffect)

    suitTrack = Sequence(getSuitAnimTrackAttack(attack))
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
    toonTracks = getToonTracksCheat(attack, damageDelay=damageDelay, splicedDamageAnims=damageAnims, dodgeDelay=0.91, splicedDodgeAnims=damageAnims, showDamageExtraTime=2.1, showMissedExtraTime=1.0)
    soundTracks = Parallel()
    toonSpinTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        toonAnimTracks.append(Sequence(Wait(damageDelay + 0.9), getSplicedAnimsTrack(damageAnims, actor=toon)))
        toonAnimTracks.append(Parallel(Func(toon.setToonStatusEffect, 'gagBan')))
        spinEffect1 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect2 = BattleParticles.createParticleEffect(file='spinEffect')
        spinEffect3 = BattleParticles.createParticleEffect(file='spinEffect')
        BattleParticles.setEffectTexture(spinEffect1, 'snow-particle', color=Vec4(1, 0, 0, 1))
        BattleParticles.setEffectTexture(spinEffect2, 'snow-particle', color=Vec4(1, 0, 0, 1))
        BattleParticles.setEffectTexture(spinEffect3, 'snow-particle', color=Vec4(1, 0, 0, 1))
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
        spinTracks1.append(getPartTrack(spinEffect1, 1.5, 5.9, [spinEffect1, battle, 0], softStop=-2))
        spinTracks2.append(getPartTrack(spinEffect2, 1.5, 5.9, [spinEffect2, battle, 0], softStop=-2))
        spinTracks3.append(getPartTrack(spinEffect3, 1.5, 5.9, [spinEffect3, battle, 0], softStop=-2))
        soundTracks.append(getSoundTrack('tt_s_ara_cfg_toonInWhirlwind.ogg', delay=2.0, node=suit))
        toonSpinTracks.append(Sequence(Wait(damageDelay + 0.9), LerpHprInterval(toon, 0.7, Point3(-10, 0, 0)), LerpHprInterval(toon, 0.5, Point3(-30, 0, 0)), LerpHprInterval(toon, 0.2, Point3(-60, 0, 0)), LerpHprInterval(toon, 0.7, Point3(-700, 0, 0)), LerpHprInterval(toon, 1.0, Point3(-1310, 0, 0)), LerpHprInterval(toon, 0.4, toon.getHpr()), Wait(0.5)))

    return Parallel(suitTrack, sprayTracks, toonTracks, toonAnimTracks, toonSpinTracks, spinTracks1, spinTracks2, spinTracks3, soundTracks)
