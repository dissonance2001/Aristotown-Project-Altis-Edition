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


def doDesperation(attack):
    suit = attack['suit']
    battle = attack['battle']
    notifyTracks = Sequence(Wait(0.5))
    cameraTracks = Sequence()
    makeDesperates = Parallel()
    makeDamageUps = Parallel()
    theSuit = None
    for s in battle.activeSuits:
        if s.dna.name == 'ambass' and not suit.dna.name == 'ambass':
            theSuit = s
            notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
            makeDesperate = Func(theSuit.makeDesperation)
            makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
            cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
            notifyTracks.append(Parallel(notifyTrack, cameraTrack))
            makeDesperates.append(makeDesperate)
            makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'wtapper' and not suit.dna.name == 'wtapper':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'bkeeper' and not suit.dna.name == 'bkeeper':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'phouse' and not suit.dna.name == 'phouse':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'radiog' and not suit.dna.name == 'radiog':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'racket' and not suit.dna.name == 'racket':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'ubuster' and not suit.dna.name == 'ubuster':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'safesupervis' and not suit.dna.name == 'safesupervis':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'stenog' and not suit.dna.name == 'stenog':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'lgator' and not suit.dna.name == 'lgator':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'sgoat' and not suit.dna.name == 'sgoat':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
        if s.dna.name == 'caseman' and not suit.dna.name == 'caseman':
                theSuit = s
                notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
                cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, theSuit), Wait(3.0))
                makeDesperate = Func(theSuit.makeDesperation)
                makeDamageUp = Parallel(Func(theSuit.makeDamageUp), Func(theSuit.checkDamageUp, + 40))
                notifyTracks.append(Parallel(notifyTrack, cameraTrack))
                makeDesperates.append(makeDesperate)
                makeDamageUps.append(makeDamageUp)
    if theSuit == None:
        print('Error finding manager... using self...')
        theSuit = suit

    return Sequence(notifyTracks, makeDamageUps, makeDesperates)

def doDesperation2(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toonTracks = Parallel()
    # for suit in battle.activeSuits:
    #     toonTracks.append(Func(suit.makeUnBattleSpeed))
    for t in battle.activeToons:
        toonTrack = Parallel(Func(t.clearToonStatusEffect, 'gagBan'))
        toonTracks.append(toonTrack)
    notifyTracks = Sequence(Func(theSuit.setChatAbsoluteSpecial, "", CFSpeech | CFTimeout))
    makeDamageUps = Parallel()
    theSuit.setPendingQueuedDesperation(True)
    if theSuit.isDesperation:
        notifyTrack = Sequence(Func(theSuit.showHpStringDesperationDamage))
    else:
        notifyTrack = Sequence(Func(theSuit.showHpStringDesperation))
    makeDamageUp = Parallel(Func(theSuit.setSuitStatusEffect, 'desperation', modifier=40, mode='refreshModifier'))
    cameraTrack = Sequence(Wait(3.0))
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    makeDamageUps.append(makeDamageUp)
    return Sequence(notifyTracks, toonTracks, makeDamageUps)

def doKnockback(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    notifyTrack = Sequence(Func(theSuit.showHpStringKnockback, 'NICE KNOCKBACK!'))
    cameraTrack = Wait(2.0)
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    return Sequence(notifyTracks)

def doCombo(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    notifyTrack = Sequence(Func(theSuit.showHpStringSacrifice, 'NICE COMBO!'))
    cameraTrack = Wait(2.0)
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    return Sequence(notifyTracks)

def doAbilityQueued(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    notifyTrack = Sequence(Func(theSuit.showHpStringAbility, "ABILITY QUEUED!"))
    cameraTrack = Wait(2.0)
    notifyTracks.append(Parallel(notifyTrack, cameraTrack))
    return Sequence(notifyTracks)

def doAbsorbMovie(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    dmg = attack['target'][0]['hp']
    notifyTracks = Sequence()
    notifyTrack = Parallel(theSuit.makeAbsorbDamageInterval(battle, dmg))
    cameraTrack = Wait(3.0)
    notifyTracks.append(Parallel(notifyTrack))
    return Sequence(notifyTracks)

def doSyphonMovie(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    dmg = attack['target'][0]['hp']
    #notifyTrack = Sequence(Func(theSuit.showHpTextNew, +dmg), Func(theSuit.setHealthForMe, +dmg),
                           #  Func(theSuit.updateHealthBar, 0))
    notifyTrack = Sequence(Func(theSuit.checkSyphonHP, dmg))
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    cameraTrack = Wait(3.0)
    notifyTracks.append(Parallel(notifyTrack, healSound))
    return Sequence(notifyTracks)

def doRageBuilding(attack):
    theSuit = attack['suit']
    suit = attack['suit']
    notifyTracks = Sequence()
    battle = attack['battle']
    dmg = attack['target'][0]['hp']
    suitResponseTrack = Parallel()
    if suit.dna.name == 'sgoat':
        suitResponseTrack.append(Sequence(Func(suit.setSuitStatusEffect, 'rageBuilding', modifier=dmg)))
    if suit.dna.name == 'phouse':
        suitResponseTrack.append(Sequence(Func(suit.setSuitStatusEffect, 'toleranceBuilding', modifier=dmg)))
    return suitResponseTrack

def doDamageMovie(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    battle = attack['battle']
    dmg = attack['target'][0]['hp']
    #notifyTrack = Sequence(Func(theSuit.showHpTextNew, +dmg), Func(theSuit.setHealthForMe, +dmg),
                           #  Func(theSuit.updateHealthBar, 0))
    notifyTrack = Parallel(theSuit.makeDamageInterval(battle, dmg))
    if theSuit.dna.name == 'safesupervis':
        node = theSuit.getGeomNode().getChild(0)
        notifyTrack.append(Parallel(LerpColorScaleInterval(node, duration=1, colorScale=(1, 1, 1, 1),
                                        blendType='easeInOut')))
    healSound = SoundInterval(globalBattleSoundCache.getSound('LB_toonup.ogg'))
    cameraTrack = Wait(3.0)
    notifyTracks.append(Parallel(notifyTrack))
    return Sequence(notifyTracks)

def doAbsorbMovieLevel(attack):
    theSuit = attack['suit']
    notifyTracks = Sequence()
    battle = attack['battle']
    dmg = attack['target'][0]['hp']
    notifyTrack = Parallel(theSuit.makeDamageLevelInterval(battle, dmg))
    cameraTrack = Wait(3.0)
    notifyTracks.append(Parallel(notifyTrack))
    return Sequence(notifyTracks)

def doDrenchDecrement(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Parallel()
    suitTrack.append(Sequence(Func(suit.showHpStringAbility, "-1 DRENCHED ROUND"), ActorInterval(suit, 'soak', startTime=3.5), Func(suit.setNeutralAnimationDrop)))
    return Parallel(suitTrack)

def doSoakRemoval(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Parallel()
    suitTrack.append(Sequence(Parallel(ActorInterval(suit, 'soak', startTime=3.5), Sequence(Wait(1.0), __soakRemoval(suit, 1)), Func(suit.clearSuitStatusEffect, 'soaked'), Func(suit.clearSuitStatusEffect, 'drenched')), Func(suit.setNeutralAnimationDrop)))
    return Parallel(suitTrack)

def __createSuitResetPosTrack2(suit, battle):
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDist = Vec3(suit.getPos(battle) - resetPos).length()
    moveDuration = 0.5
    walkTrack = Sequence(Func(suit.setHpr, battle, resetHpr), ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=0.0001), Func(suit.setNeutralAnimation))
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)

def doLureRemoval(attack):
    suit = attack['suit']
    battle = attack['battle']
    suit.clearPendingQueuedLured()
    suitTrack = Parallel(__createSuitResetPosTrack2(suit, battle), Func(battle.unlureSuit, suit), Func(suit.setDizzy, 0), Func(suit.clearSuitStatusEffect, 'lured'))
    return suitTrack

def doMarkRemoval(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Parallel()
    suitTrack.append(Sequence(Parallel(ActorInterval(attack['suit'], 'squirt-small-react', startTime=2.25), Sequence(Wait(1.0), Func(suit.splatSuit, 0, 1)), Func(suit.clearSuitStatusEffect, 'marked')), Func(suit.setNeutralAnimationDrop)))
    # for suit in battle.activeSuits:
    #     suitTrack.append(Func(suit.checkMarkRounds))
    return suitTrack

def doGovernaughtDeath(attack):
    battle = attack['battle']
    targets = attack['target']
    notifyTracks = Parallel()
    soundTracks = Parallel()
    waitTrack = Sequence(Wait(3.0))
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        soundTrack = getSoundTrack('LB_toonup.ogg', node=toon)
        notifyTrack = Sequence(Func(toon.showHpTextNew, 0, text="+%s" % dmg + "% Damage!", colorCode=1))
        notifyTrack.append(Parallel(Func(toon.setToonStatusEffect, 'damageUpGov', modifier=dmg, mode='refreshModifier')))
        soundTracks.append(soundTrack)
        notifyTracks.append(notifyTrack)
    return Parallel(notifyTracks, soundTracks, waitTrack)

def doSueRemoval(attack):
    suit = attack['suit']
    battle = attack['battle']
    suitTrack = Sequence()
    suitTrack.append(Sequence(Parallel(ActorInterval(suit, 'soak', startTime=3.5), Sequence(Wait(1.0), Func(suit.clearSuitStatusEffect, 'sued')), Func(battle.unSueSuit, suit)), Func(suit.setNeutralAnimationDrop)))
    suitTrack.append(Func(suit.removeSued))
    return suitTrack

def doSueApplication(attack):
    suit = attack['suit']
    battle = attack['battle']
    explodePosPoints = [Point3(0, 0, 0), MovieUtil.PNT3_ZERO]
    splatName = 'dust'
    splat = globalPropPool.getProp('dust')
    explode = globalPropPool.getProp('dust')
    explode.setTwoSided(True)

    explode.setBillboardPointWorld(2)
    explodeTrack = Sequence()
    explodeTrack.append(
        getPropAppearTrack(explode, suit, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
    explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
    suitTrack = Sequence()
    suitTrack.append(Parallel(ActorInterval(suit, 'pie-small-react'), Func(battle.sueSuit, suit), Func(suit.showHpTextNew, 0, text="CEASE AND DESIST!", colorCode=1)))
    suitTrack.append(Func(suit.makeSued, 4))
    suitTrack.append(Func(suit.setNeutralAnimationDrop))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('LB_receive_evidence.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, explodeTrack)

def doSueDamage(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    dmg = attack['target'][0]['hp']
    suitTrack = Parallel()
    suitTrack.append(Parallel(theSuit.makeSueDamageInterval(battle, dmg)))
    return Parallel(suitTrack)

def doZapMovie(attack):
    theSuit = attack['suit']
    battle = attack['battle']
    target = attack['target']
    suitTrack = Parallel()
    dmg = attack['target'][0]['hp']
    suitTrack.append(Parallel(theSuit.makeZapDamageInterval(battle, dmg)))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('AA_battery.ogg'), node=theSuit))
    return Parallel(soundTrack, suitTrack)

def doDeathCheck(attack):
    name = attack['name']
    suit = attack['suit']
    battle = attack['battle']
    currentBossHealth = -1
    revives = suit.getSkeleRevives()
    suitTrack = Sequence()
    suitTrack2 = Parallel()
    if suit.dna.name == 'redd' and not suit.isVirtual:
        suitTrack.append(MovieUtil.createSuitReviveRedd(suit, battle))
    elif suit.isVirtual:
        suitTrack.append(MovieUtil.createVirtualSuitDeathTrack(suit, battle))
    elif not suit.isSkeleton and revives >= 2:
        suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
    elif suit.isSkeleton and revives >= 2:
        suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
    elif suit.isSkeleton and revives >= 1 and not suit.isRevive:
        suitTrack.append(MovieUtil.createSuitReviveTrackVirtual(suit, battle))
    elif not suit.isSkeleton and revives >= 1:
        suitTrack.append(MovieUtil.createSuitReviveTrack(suit, battle))
    elif not suit.isVirtual:
        suitTrack.append(MovieUtil.createSuitDeathTrack(suit, battle))
    for s in battle.activeSuits:
        suitTrack2.append(Sequence(Func(s.checkDeathCheck, battle), Wait(9.0)))
    return Parallel(suitTrack2)

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
    suitTrack = getSuitAnimTrackAttack(attack)
    partTrack = getPartTrack(particleEffect, 1.0, 3.4, [particleEffect, suit, 0], softStop=-2)
    waterfallTrack = getPartTrack(waterfallEffect, 0.8, 3.4, [waterfallEffect, suit, 0], softStop=-2)
    damageAnims = [['slip-forward']]
    dodgeAnims = []
    dodgeAnims.append(['jump',
     0.01,
     0,
     0.6])
    dodgeAnims.extend(getSplicedLerpAnims('jump', 0.31, 1.3, startTime=0.6))
    dodgeAnims.append(['jump', 0, 0.91])
    toonTracks = getToonTracks(attack, damageDelay=damageDelay, damageAnimNames=['slip-forward'], dodgeDelay=0.91, splicedDodgeAnims=dodgeAnims, showMissedExtraTime=1.0)
    synergySoundTrack = Sequence(Wait(0.9), SoundInterval(globalBattleSoundCache.getSound('SA_synergy.ogg'), node=suit))
    if hitAtleastOneToon > 0:
        fallingSoundTrack = Sequence(Wait(damageDelay + 0.5), SoundInterval(globalBattleSoundCache.getSound('Toon_bodyfall_synergy.ogg'), node=suit))
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, fallingSoundTrack, toonTracks)
    else:
        return Parallel(suitTrack, partTrack, waterfallTrack, synergySoundTrack, toonTracks)

def doCourtCalculations(attack):
    suit = attack['suit']
    battle = attack['battle']
    calculator = globalPropPool.getProp('court-costs-calculator')
    calculator.setTwoSided(True)
    calculator.setScale(1.5)
    suitTrack = Sequence(ActorInterval(attack['suit'], 'calculating-costs'),  Func(suit.setNeutralAnimationAttack), Wait(2.0))
    suitSpeechTrack = Func(suit.setChatAbsolute, "Calculating costs of litigation fees... Price index raised to %s." % int(attack['target'][0]['hp']), CFSpeech | CFTimeout)
    calcPosPoints = [Point3(-0.43352601156069426, 0.25, -.05), VBase3(12.485549132947995, 0.0, 181.0)]
    calcPropTrack = Sequence(
        Func(__showProp, calculator, suit.getRightHand(), *calcPosPoints),
        ActorInterval(calculator, 'court-costs-calculator'),
        Func(calculator.removeNode)
    )
    soundTrack = getSoundTrack('SA_calculating_costs.ogg')
    return Parallel(suitTrack, soundTrack, suitSpeechTrack, calcPropTrack)

def doCourtRecord(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        toonTrack = Parallel(Func(toon.setToonStatusEffect, 'gagBan'))
        toonTracks.append(toonTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack))
    suitTrack.append(Wait(1.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_cease_and_desist.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, toonTracks)

def doCourtMandate(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    toonTracks = Parallel()
    for t in targets:
        toon = t['toon']
        toonTrack = Parallel(Func(toon.setToonStatusEffect, 'gagBan'))
        toonTracks.append(toonTrack)
    suitTrack = Sequence(getSuitAnimTrack(attack, playRate=0.75))
    suitTrack.append(Wait(2.0))
    soundTrack = Sequence(SoundInterval(globalBattleSoundCache.getSound('SA_objection.ogg'), node=suit))
    return Parallel(suitTrack, soundTrack, toonTracks)