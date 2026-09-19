from toontown.battle import MovieCamera
from toontown.battle import MovieUtil
from toontown.battle import BattleParticles
from direct.directnotify import DirectNotifyGlobal
from direct.interval.IntervalGlobal import *
from direct.particles import ParticleEffect
from toontown.battle.BattleBase import *
from toontown.battle.BattleBase import *
from direct.showutil import Effects
from toontown.battle import SuitBattleGlobals
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
from toontown.battle.attacks.suits.MovieIntervals import (
    throwPos,
    __doDamage,
    __doDamageCheat,
    __showProp,
    __animProp,
    __suitFacePoint,
    __toonFacePoint,
    __toonTorsoPoint,
    __toonGroundPoint,
    __toonGroundMissPoint,
    __toonMissPoint,
    __toonMissBehindPoint,
    __throwBounceHitPoint,
    __throwBounceMissPoint,
    __throwBouncePoint,
    getResetTrack,
    __createSuitResetPosTrack,
    getSuitTrack,
    getSuitAnimTrack,
    getPartTrack,
    getPartTracks,
    getToonTrack,
    getToonTracks,
    getToonDodgeTrack,
    getAllyToonsDodgeParallel,
    getPropTrack,
    getPropAppearTrack,
    getPropThrowTrack,
    getThrowTrack,
    getToonTakeDamageTrack,
    getToonTakeDamageTrackCheat,
    getSplicedAnimsTrack,
    getSplicedLerpAnims,
    getSoundTrack,
    getToonTrackCheat,
    getToonDodgeTrackCheat,
    getToonTracksCheat
)
from toontown.battle.attacks.suits.MovieBossbotLitigationCheats import getToonTrackCheat2

notify = DirectNotifyGlobal.directNotify.newCategory('MovieSuitAttacks')

def doRefinementDerrickMan(attack):
    theSuit = attack['suit']
    battle = attack['battle']

    suitTracks = Parallel()
    for suit in battle.activeSuits:
        suitTrack = Sequence()
        suitTrack.append(Wait(4.5))
        suitTrack.append(Func(suit.checkRefinementDerrickMan))
        suitTrack.append(Func(battle.unSueSuit, suit))
        if suit.dna.name != 'derrman':
            suitTrack.append(Parallel(Sequence(Wait(3)),
                                          Func(suit.setChatAbsolute,
                                               random.choice(OTPLocalizerEnglish.SuitHealingPhrases),
                                               CFSpeech | CFTimeout)))
        suitTrack.append(
                Func(suit.setNeutralAnimation))
        suitTracks.append(suitTrack)
    posPoints = [Point3(-0.25, 0, 0), VBase3(0, 180, 0)]
    knifeTracks = Parallel()
    for suit in battle.activeSuits:
        theSuit = attack['suit']
        hitPoint = suit.getPos(battle)
        hitPoint.setZ(suit.height + 2)
        hitPoint.setY(hitPoint.getY() + 0.5)
        knife = loader.loadModel('phase_12/models/bossbotHQ/canoffood')
        can = knife.find('**/can')
        can.setScale(.5)
        knifeTrack = Sequence(
            getPropAppearTrack(can, theSuit.getRightHand(), posPoints, .5, VBase3(0.5, 0.5, 0.5),
                               scaleUpTime=0.1),
            Wait(1.5),
            Parallel(
                getThrowTrack(can, hitPoint, 1.5, battle, -10.288),
                LerpHprInterval(can, 0.8, VBase3(0, 0, 0)), LerpScaleInterval(can, 0, VBase3(1, 1, 1))),
        Parallel(LerpPosInterval(can, 1, VBase3(hitPoint.getX(), hitPoint.getY() + 0.5, hitPoint.getZ() - 10)), Sequence(Wait(0.25), LerpScaleInterval(can, 0.5, VBase3(0, 0, 0)))),
            Func(MovieUtil.removeProp, can)
        )
        knifeTracks.append(knifeTrack)
    tauntIndex = attack['taunt']
    taunt = random.choice(
        ["It's important to stay adequately oiled when defeating Toons.", "I'm suspending this well.",
"Freshly drilled to keep us in working order."])
    makeUnVulnerable = Func(theSuit.makeUnVulnerable)
    suitPos, suitHpr = battle.getActorPosHpr(theSuit)
    gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + theSuit.height - 0.2)
    explosionTrack = Sequence()
    explosionTrack.append(MovieUtil.createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    suitTrackAnim = Sequence(getSuitAnimTrack(attack, playRate=1.5))
    soundTrack1 = getSoundTrack('SA_repair.ogg', delay=2.5)
    soundTrack2 = getSoundTrack('SA_refinement.ogg', delay=2, node=theSuit)
    multiTrack = Parallel(soundTrack1, soundTrack2)
    makeNotImmune = Func(theSuit.makeNonImmortal)
    return Parallel(suitTrackAnim, makeUnVulnerable, makeNotImmune, suitTracks, multiTrack, knifeTracks)

def doInkDrainDOLA(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    BattleParticles.loadParticles()
    particleEffect = BattleParticles.createParticleEffect('InkDrain')
    BattleParticles.setEffectTexture(particleEffect, 'snow-particle', color=Vec4(0.463, 0.635, 0.388, 1))
    particleEffect2 = BattleParticles.createParticleEffect('InkDrain')
    BattleParticles.setEffectTexture(particleEffect2, 'snow-particle', color=Vec4(0.427, 0.478, 0.608, 1))
    particleEffect3 = BattleParticles.createParticleEffect('InkDrain')
    BattleParticles.setEffectTexture(particleEffect3, 'snow-particle', color=Vec4(0.498, 0.22, 0.275, 1))
    particleEffect4 = BattleParticles.createParticleEffect('InkDrain')
    BattleParticles.setEffectTexture(particleEffect4, 'snow-particle', color=Vec4(0.639, 0.639, 0.639, 1))
    suitTrack = getSuitAnimTrack(attack)
    partTrack = getPartTrack(particleEffect, 1e-05, suitTrack.getDuration() + 5.2, [particleEffect, suit, 0], softStop=-1)
    partTrack2 = getPartTrack(particleEffect2, 1e-05, suitTrack.getDuration() + 5.2, [particleEffect2, suit, 0], softStop=-1)
    partTrack3 = getPartTrack(particleEffect3, 1e-05, suitTrack.getDuration() + 5.2, [particleEffect3, suit, 0], softStop=-1)
    partTrack4 = getPartTrack(particleEffect4, 1e-05, suitTrack.getDuration() + 5.2, [particleEffect4, suit, 0], softStop=-1)
    toonTracks = Parallel()

    soundTrack = getSoundTrack('SA_ink_drain.ogg', delay=1.4, node=suit)
    colorTracks = Parallel()
    for t in targets:
        toon = t['toon']
        dmg = t['hp']
        def changeColor(parts):
            track = Parallel()
            for partNum in range(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(nextPart.colorScaleInterval(0.1, Vec4(0.5, 0.5, 0.5, 1)))

            return track

        def resetColor(parts):
            track = Parallel()
            for partNum in range(0, parts.getNumPaths()):
                nextPart = parts.getPath(partNum)
                track.append(Func(nextPart.clearColorScale))

            return track

        headParts = toon.getHeadParts()
        torsoParts = toon.getTorsoParts()
        legsParts = toon.getLegsParts()
        colorTrack = Sequence()
        colorTrack.append(Func(battle.movie.needRestoreColor))
        colorTrack.append(changeColor(headParts))
        colorTrack.append(changeColor(torsoParts))
        colorTrack.append(changeColor(legsParts))
        colorTrack.append(Wait(suitTrack.getDuration() + 5.2))
        colorTrack.append(resetColor(headParts))
        colorTrack.append(resetColor(torsoParts))
        colorTrack.append(resetColor(legsParts))
        colorTrack.append(Func(battle.movie.clearRestoreColor))
        colorTracks.append(colorTrack)
        toonTracks.append(Parallel(Func(toon.setToonStatusEffect, 'inkDrain', modifier=25, turns=3)))
        toonTracks.append(ActorInterval(toon, 'cringe', playRate=0.25))
        toonTracks.append(Func(toon.loop, 'neutral'))

    return Parallel(suitTrack, colorTracks, partTrack, partTrack2, partTrack3, partTrack4, toonTracks, soundTrack, colorTracks)

def doAmbushMarketing(attack):
    suit = attack['suit']
    battle = attack['battle']
    targets = attack['target']
    suitTrack = Parallel(getSuitAnimTrack(attack))
    soundTrack = getSoundTrack('SA_multi_level_marketing.ogg', node=suit)
    suitTrack.append(Func(suit.setSuitStatusEffect, 'extraAttacks', modifier=5, mode='refreshModifier'))
    return Parallel(suitTrack, soundTrack)
