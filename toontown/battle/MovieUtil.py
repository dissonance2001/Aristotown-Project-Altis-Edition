import random
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from direct.directnotify import DirectNotifyGlobal
from direct.particles import ParticleEffect
from toontown.battle import BattleParticles
from toontown.battle import BattleProps
from panda3d.core import *
from toontown.suit import SuitBase
from toontown.chat.ChatGlobals import *
from toontown.nametag import NametagGlobals
from toontown.nametag.NametagGlobals import *
from panda3d.direct import *
from toontown.toonbase import TTLocalizer

notify = DirectNotifyGlobal.directNotify.newCategory('MovieUtil')
SUIT_LOSE_DURATION = 6.0
SUIT_LURE_DISTANCE = 4
SUIT_LURE_DOLLAR_DISTANCE = 4
SUIT_EXTRA_REACH_DISTANCE = -4
SUIT_EXTRA_RAKE_DISTANCE = 1.1
SUIT_TRAP_DISTANCE = 4
SUIT_TRAP_RAKE_DISTANCE = 4.5
SUIT_TRAP_MARBLES_DISTANCE = 3.7
SUIT_TRAP_TNT_DISTANCE = 5.2
PNT3_NEARZERO = Point3(0.01, 0.01, 0.01)
PNT3_ZERO = Point3(0.0, 0.0, 0.0)
PNT3_ONE = Point3(1.0, 1.0, 1.0)
largeSuits = ['f',
 'cc',
 'gh',
 'tw',
 'bf',
 'sc',
 'ds',
 'hh',
 'cr',
 'tbc',
 'hho',            
 'bs',
 'sd',
 'le',
 'bw',
 'mg',             
 'nc',
 'mb',
 'ls',
 'rb',
 'bfh',
 'ms',
 'tf',
 'm',
 'mh',
 'txm']
shotDirection = 'left'

def avatarDodge(leftAvatars, rightAvatars, leftData, rightData):
    if len(leftAvatars) > len(rightAvatars):
        PoLR = rightAvatars
        PoMR = leftAvatars
    else:
        PoLR = leftAvatars
        PoMR = rightAvatars
    upper = 1 + 4 * abs(len(leftAvatars) - len(rightAvatars))
    if random.randint(0, upper) > 0:
        avDodgeList = PoLR
    else:
        avDodgeList = PoMR
    if avDodgeList is leftAvatars:
        data = leftData
    else:
        data = rightData
    return (avDodgeList, data)


def avatarHide(avatar):
    notify.debug('avatarHide(%d)' % avatar.doId)
    if hasattr(avatar, 'battleTrapProp'):
        notify.debug('avatar.battleTrapProp = %s' % avatar.battleTrapProp)
    avatar.detachNode()

	
def miscHide(misc):
    misc.detachNode()


def copyProp(prop):
    from direct.actor import Actor
    if isinstance(prop, Actor.Actor):
        return Actor.Actor(other=prop)
    else:
        return prop.copyTo(hidden)


def showProp(prop, hand, pos = None, hpr = None, scale = None):
    prop.reparentTo(hand)
    if pos:
        if callable(pos):
            pos = pos()
        prop.setPos(pos)
    if hpr:
        if callable(hpr):
            hpr = hpr()
        prop.setHpr(hpr)
    if scale:
        if callable(scale):
            scale = scale()
        prop.setScale(scale)


def showProps(props, hands, pos = None, hpr = None, scale = None):
    index = 0
    for prop in props:
        if not prop or prop.isEmpty():
            continue
        prop.reparentTo(hands[index])
        if pos:
            prop.setPos(pos)
        if hpr:
            prop.setHpr(hpr)
        if scale:
            prop.setScale(scale)
        index += 1


def hideProps(props):
    for prop in props:
        prop.detachNode()


def removeProp(prop):
    from direct.actor import Actor
    if prop.isEmpty() == 1 or prop == None:
        return
    prop.detachNode()
    if isinstance(prop, Actor.Actor):
        prop.cleanup()
    else:
        prop.removeNode()
    return


def removeProps(props):
    for prop in props:
        removeProp(prop)


def getActorIntervals(props, anim):
    tracks = Parallel()
    for prop in props:
        tracks.append(ActorInterval(prop, anim))

    return tracks


def getScaleIntervals(props, duration, startScale, endScale):
    tracks = Parallel()
    for prop in props:
        tracks.append(LerpScaleInterval(prop, duration, endScale, startScale=startScale))

    return tracks


def avatarFacePoint(av, other = render):
    pnt = av.getPos(other)
    pnt.setZ(pnt[2] + av.getHeight())
    return pnt


def insertDeathSuit(suit, deathSuit, battle = None, pos = None, hpr = None):
    holdParent = suit.getParent()
    if suit.getVirtual():
        virtualize(deathSuit)
    avatarHide(suit)
    if deathSuit != None and not deathSuit.isEmpty():
        if holdParent and 0:
            deathSuit.reparentTo(holdParent)
        else:
            deathSuit.reparentTo(render)
        if battle != None and pos != None:
            deathSuit.setPos(battle, pos)
        if battle != None and hpr != None:
            deathSuit.setHpr(battle, hpr)
    return


def removeDeathSuit(suit, deathSuit):
    notify.debug('removeDeathSuit()')
    if not deathSuit.isEmpty():
        deathSuit.detachNode()
        suit.cleanupLoseActor()
		
def insertZapSuit(suit, zapSuit, battle = None, pos = None, hpr = None):
    holdParent = suit.getParent()
    if suit.getVirtual():
        virtualize(zapSuit)
    if zapSuit != None and not zapSuit.isEmpty():
        if holdParent and 0:
            zapSuit.reparentTo(holdParent)
        else:
            zapSuit.reparentTo(render)
        if battle != None and pos != None:
            zapSuit.setPos(battle, pos)
        if battle != None and hpr != None:
            zapSuit.setHpr(battle, hpr)
    return
	
def removeZapSuit(suit, zapSuit):
    notify.debug('removeDeathSuit()')
    if not zapSuit.isEmpty():
        zapSuit.detachNode()
        suit.cleanupZapActor()


def insertReviveSuit(suit, deathSuit, battle = None, pos = None, hpr = None):
    holdParent = suit.getParent()
    if suit.getVirtual():
        virtualize(deathSuit)
    suit.hide()
    if deathSuit != None and not deathSuit.isEmpty():
        if holdParent and 0:
            deathSuit.reparentTo(holdParent)
        else:
            deathSuit.reparentTo(render)
        if battle != None and pos != None:
            deathSuit.setPos(battle, pos)
        if battle != None and hpr != None:
            deathSuit.setHpr(battle, hpr)
    return


def removeReviveSuit(suit, deathSuit):
    notify.debug('removeDeathSuit()')
    suit.setSkelecog(1)
    suit.show()
    if not deathSuit.isEmpty():
        deathSuit.detachNode()
        suit.cleanupLoseActor()
    suit.healthBar.show()
    suit.resetHealthBarForSkele()


def virtualize(deathsuit):
    actorNode = deathsuit.find('**/__Actor_modelRoot')
    actorCollection = actorNode.findAllMatches('*')
    parts = ()
    for thingIndex in xrange(0, actorCollection.getNumPaths()):
        thing = actorCollection[thingIndex]
        if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
            thing.setColorScale(1.0, 1.0, 1.0, 1.0)
            thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
            thing.setDepthWrite(False)
            thing.setBin('fixed', 1)


def createTrainTrackAppearTrack(dyingSuit, toon, battle, npcs):
    retval = Sequence()
    return retval
    possibleSuits = []
    for suitAttack in battle.movie.suitAttackDicts:
        suit = suitAttack['suit']
        if not suit == dyingSuit:
            if hasattr(suit, 'battleTrapProp') and suit.battleTrapProp and suit.battleTrapProp.getName() == 'traintrack':
                possibleSuits.append(suitAttack['suit'])

    closestXDistance = 10000
    closestSuit = None
    for suit in possibleSuits:
        suitPoint, suitHpr = battle.getActorPosHpr(suit)
        xDistance = abs(suitPoint.getX())
        if xDistance < closestXDistance:
            closestSuit = suit
            closestXDistance = xDistance

    if closestSuit and closestSuit.battleTrapProp.isHidden():
        closestSuit.battleTrapProp.setColorScale(1, 1, 1, 0)
        closestSuit.battleTrapProp.show()
        newRelativePos = dyingSuit.battleTrapProp.getPos(closestSuit)
        newHpr = dyingSuit.battleTrapProp.getHpr(closestSuit)
        closestSuit.battleTrapProp.setPos(newRelativePos)
        closestSuit.battleTrapProp.setHpr(newHpr)
        retval.append(LerpColorScaleInterval(closestSuit.battleTrapProp, 3.0, Vec4(1, 1, 1, 1)))
    else:
        notify.debug('could not find closest suit, returning empty sequence')
    return retval


def createSuitReviveTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    if suit.style.name == 'rainmake':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    elif suit.style.name == 'arbit':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    else:
        for headPart in suit.animatedHeadParts:
            headInterval = ActorInterval(headPart, 'death')
            hasAnimatedHead = True
    suitTrack.append(
        ActorInterval(suit, 'lose', duration=SUIT_LOSE_DURATION))
    suitTrack.append(Func(suit.hide))
    for headPart in suit.headParts:
        suitTrack.append(Func(headPart.hide))
    suitTrack.append(Func(suit.setSkelecog2, True))
    suitTrack.append(Func(battle.unlureSuit, suit))
    suitTrack.append(Func(battle.unSueSuit, suit))
    suitTrack.append(Func(suit.setDizzy, 0))
    suitTrack.append(Func(suit.setSued2, 0))
    suitTrack.append(Func(suit.show))
    suitTrack.append(ActorInterval(suit, 'landing', startTime=1.25))
    suitTrack.append(Sequence(Func(suit.showHpText2,
                                   '0.5x HP MULTIPLIER',
                                   2), Func(suit.showHpStringLureManager2,
                                            '+ 50% Damage'), Func(suit.showHpString,
                                                                         '-1 Revive')))
    suitTrack.append(Func(suit.loop, 'neutral-unstable'))
    suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() / 2)))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.checkDamageUp, 50))
    suitTrack.append(Func(suit.makeRevive))
    if suit.style.name == 'caseman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'stenog' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'ddiver' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
    elif suit.style.name == 'sgoat' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
    elif suit.style.name == 'lgator' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'bellring' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'whunter' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'racket' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'chairman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'ottoman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'fires' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'prethink' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'duckshfl' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'hrollers' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'chainsaw' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'chainsaw2' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'treek' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
    elif suit.style.name == 'mouthp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
    elif suit.style.name == 'hroller2' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'rainmake' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'mplayer' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'psetter' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'videog' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'bkeeper' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'phouse' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'wtapper' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'hroller' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'ambass':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'safesupervis' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'dold' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'duckshfl' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'derrhand' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'derrhand' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'derrman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
    elif suit.style.name == 'fbed' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'arbit' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
    elif suit.style.name == 'dopa':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'dopr':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'ubuster':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'radiog':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'djockey' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'ptjockey' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'pcrat' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'racket' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'dking' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'redd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.isFemale and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.isFemaleSkelecog and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.isSkelecogDialogue:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    elif deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    else:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
    deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    deathSoundTrack = Sequence(Wait(0.8), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2), SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8), SoundInterval(deathSound, volume=0.32))
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
    explosionTrack.append(Wait(5.4))
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    gears1Track = Sequence(Wait(2.1), ParticleInterval(smallGears, battle, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
    gears2MTrack = Track((0.0, explosionTrack), (0.7, ParticleInterval(singleGear, battle, worldRelative=0, duration=5.7, cleanup=True)), (5.2, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=1.2, cleanup=True)), (5.4, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')
    toonMTrack = Parallel(name='toonMTrack')
    for mtoon in battle.toons:
        toonMTrack.append(Sequence(Wait(1.0), ActorInterval(mtoon, 'duck'), ActorInterval(mtoon, 'duck', startTime=1.8), Func(mtoon.loop, 'neutral')))

    returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    if hasAnimatedHead:
        returnval.append(headInterval)
    return returnval

def createAmbassadorReviveTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    suitTrack.append(Func(suit.hide))
    for headPart in suit.headParts:
        suitTrack.append(Func(headPart.hide))
    suitTrack.append(Func(suit.setSkelecog2, True))
    suitTrack.append(Func(suit.show))
    suitTrack.append(Func(suit.setMaxHP2, 4990))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.checkDamageUp, 50))
    suitTrack.append(Func(suit.makeRevive))
    suitTrack.append(ActorInterval(suit, 'pie-small-react'))
    suitTrack.append(Func(suit.setNeutralAnimation))
    deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    deathSoundTrack = Sequence(SoundInterval(deathSound, volume=0.32))
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
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    returnval = Parallel(suitTrack, deathSoundTrack, explosionTrack)
    return returnval

def createSuitReviveRedd(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'death'), Func(headPart.loop, 'neutral'))
        headInterval2 = Func(headPart.loop, 'neutral')
        hasAnimatedHead = True
    suitTrack.append(
        ActorInterval(suit, 'lose', duration=SUIT_LOSE_DURATION))
    suitTrack.append(Func(suit.hide))
    #suitTrack.append(Func(suit.setSkelecog2, True))
    suitTrack.append(Func(suit.setVirtual, True, True))
    suitTrack.append(Func(suit.setCog, True))
    suitTrack.append(Func(suit.setName, suit.createNameInfoVirtual()))
    suitTrack.append(Func(suit.show))
    suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() / 2)))
    suitTrack.append(Func(suit.setHealthForMe, 0))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.checkDamageUp, 50))
    suitTrack.append(Func(suit.makeLaserRevive))
    suitTrack.append(ActorInterval(suit, 'landing', startTime=1.25))
    suitTrack.append(Sequence(Func(suit.showHpText2,
                                           '0.5x HP MULTIPLIER',
                                           2), Func(suit.showHpStringLureManager2,
                                           '+ 50% Damage'), Func(suit.showHpString,
                                           '-1 Revive')))
    suitTrack.append(Func(suit.loop, 'neutral-unstable'))
    if suit.style.name == 'redd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    else:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
    deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    deathSoundTrack = Sequence(Wait(0.8), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2), SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8), SoundInterval(deathSound, volume=0.32))
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
    explosionTrack.append(Wait(5.4))
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    gears1Track = Sequence(Wait(2.1), ParticleInterval(smallGears, battle, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
    gears2MTrack = Track((0.0, explosionTrack), (0.7, ParticleInterval(singleGear, battle, worldRelative=0, duration=5.7, cleanup=True)), (5.2, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=1.2, cleanup=True)), (5.4, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')
    toonMTrack = Parallel(name='toonMTrack')
    if suit.style.name == 'redd':
        from toontown.battle import MovieCamera
        suitTrack.append(MovieCamera.motionShot(0.0, 10.0, 8.0, -180, -10.0, 0.0, 0, suit))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "Your persistence awes me. You come back, again and again, to make sure I stay down.",
                              CFSpeech | CFTimeout))
        suitTrack.append(ActorInterval(suit, 'rage'))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Wait(2.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "Unfortunately for you, I too will not budge. My motivation runs stronger than your puerility.",
                              CFSpeech | CFTimeout))
        suitTrack.append(Wait(4.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "Corrosion is vile, Toon, Once a Cog's functions grow corrupt, they are never the same.",
                              CFSpeech | CFTimeout))
        suitTrack.append(Wait(4.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "I will not let this hinder him further! I will not let him suffer in silence!",
                              CFSpeech | CFTimeout))
        suitTrack.append(Wait(4.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "EN GARDE!",
                              CFSpeech | CFTimeout))
        suitTrack.append(ActorInterval(suit, 'come-on'))
        suitTrack.append(Func(suit.showHpString, '+1 ATTACK!'))
        suitTrack.append(Func(suit.makeExtraAttacks, suit.getExtraAttacks() + 1))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Wait(2.0))
    for mtoon in battle.toons:
        toonMTrack.append(Sequence(Wait(1.0), ActorInterval(mtoon, 'duck'), ActorInterval(mtoon, 'duck', startTime=1.8), Func(mtoon.loop, 'neutral')))

    returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    if hasAnimatedHead:
        returnval.append(headInterval)
    return returnval

def createGhostMentalityTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend=base.wantSmoothAnims)
    suitTrack.append(Func(suit.hide))
    #suitTrack.append(Func(suit.setSkelecog2, True))
    suitTrack.append(Func(suit.setVirtual, True, True))
    suitTrack.append(Func(suit.setCog, True))
    suitTrack.append(Func(suit.show))
    suitTrack.append(Func(suit.showHpString, '+50% Damage', 2))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.checkDamageUp, 50))
    suitTrack.append(Func(suit.makeLaserRevive))
    suitTrack.append(ActorInterval(suit, 'slip-backward'))
    suitTrack.append(Func(suit.setNeutralAnimation))
    deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    deathSoundTrack = Sequence(SoundInterval(deathSound, volume=0.32))
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
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    returnval = Parallel(suitTrack, deathSoundTrack, explosionTrack)
    return returnval

def createRisingStars(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend=base.wantSmoothAnims)
    suitTrack.append(Func(suit.hide))
    #suitTrack.append(Func(suit.setSkelecog2, True))
    suitTrack.append(Func(suit.setVirtual, True, True))
    suitTrack.append(Func(suit.setCog, True))
    suitTrack.append(Func(suit.show))
    suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() / 2)))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.checkDamageUp, 50))
    suitTrack.append(Func(suit.makeLaserRevive))
    suitTrack.append(LerpColorScaleInterval(suit, 0, (0, 0, 0, 0)))
    suitTrack.append(Func(suit.setNeutralAnimation))
    returnval = Parallel(suitTrack)
    return returnval

def createSuitReviveTrackVirtual(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'death'), Func(headPart.loop, 'neutral'))
        headInterval2 = Func(headPart.loop, 'neutral')
        hasAnimatedHead = True
    suitTrack.append(
        ActorInterval(suit, 'lose', duration=SUIT_LOSE_DURATION))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.setSkelecog2, True))
    suitTrack.append(Func(suit.setVirtual, True, True))
    suitTrack.append(Func(suit.setName, suit.createNameInfoVirtual()))
    suitTrack.append(Func(suit.show))
    suitTrack.append(ActorInterval(suit, 'landing', startTime=1.25))
    suitTrack.append(Sequence(Func(suit.showHpText2,
                                           '0.5x HP MULTIPLIER',
                                           2), Func(suit.showHpStringLureManager2,
                                           '+ 50% Damage'), Func(suit.showHpString,
                                           '-1 Revive')))
    suitTrack.append(Func(suit.loop, 'neutral-unstable'))
    suitTrack.append(Func(battle.unlureSuit, suit))
    suitTrack.append(Func(battle.unSueSuit, suit))
    suitTrack.append(Func(suit.setDizzy, 0))
    suitTrack.append(Func(suit.setSued2, 0))
    suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() / 2)))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.checkDamageUp, 50))
    suitTrack.append(Func(suit.makeLaserRevive))
    if suit.style.name == 'caseman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'stenog' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'ddiver' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
    elif suit.style.name == 'sgoat' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
    elif suit.style.name == 'lgator' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'bellring' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'whunter' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'racket' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'chairman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'ottoman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'fires' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'prethink' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'duckshfl' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'hrollers' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'chainsaw' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'chainsaw2' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'treek' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
    elif suit.style.name == 'mouthp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
    elif suit.style.name == 'hroller2' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'rainmake' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'mplayer' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'psetter' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'videog' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'bkeeper' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'phouse' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'wtapper' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'hroller' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'ambass':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'safesupervis' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'dold' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'duckshfl' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'derrhand' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'derrhand' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'derrman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
    elif suit.style.name == 'fbed' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'arbit' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
    elif suit.style.name == 'dopa':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'dopr':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'ubuster':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'radiog':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'djockey' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'ptjockey' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'pcrat' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'racket' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'dking' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'redd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.isFemale and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.isFemaleSkelecog and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.isSkelecogDialogue:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    elif deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    else:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
    deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    deathSoundTrack = Sequence(Wait(0.8), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2), SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8), SoundInterval(deathSound, volume=0.32))
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
    explosionTrack.append(Wait(5.4))
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    gears1Track = Sequence(Wait(2.1), ParticleInterval(smallGears, battle, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
    gears2MTrack = Track((0.0, explosionTrack), (0.7, ParticleInterval(singleGear, battle, worldRelative=0, duration=5.7, cleanup=True)), (5.2, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=1.2, cleanup=True)), (5.4, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')
    toonMTrack = Parallel(name='toonMTrack')
    if suit.style.name == 'wsi':
        from toontown.battle import MovieCamera
        suitTrack.append(MovieCamera.motionShot(0.0, 10.0, 8.0, -180, -10.0, 0.0, 0, suit))
        suitTrack.append(Func(suit.setChatAbsolute,
                              'If you believe this is the end for me, think again.',
                              CFSpeech | CFTimeout))
        suitTrack.append(ActorInterval(suit, 'frustrated'))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Wait(2.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              'I have worked tirelessly, day and night, to get this department in order.',
                              CFSpeech | CFTimeout))
        suitTrack.append(Wait(4.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "I'm tired of your antics, Toons...",
                              CFSpeech | CFTimeout))
        suitTrack.append(Wait(4.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "You have not only made a mockery of C.O.G.S Incorporated, but my family as well.",
                              CFSpeech | CFTimeout))
        suitTrack.append(Wait(4.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "En garde, Toons! Show me this 'power' you claim to have.",
                              CFSpeech | CFTimeout))
        suitTrack.append(ActorInterval(suit, 'taunt'))
        suitTrack.append(Func(suit.showHpString, '+1 ATTACK!'))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Func(suit.makeExtraAttacks, suit.getExtraAttacks() + 1))
        suitTrack.append(Wait(2.0))
    for mtoon in battle.toons:
        toonMTrack.append(Sequence(Wait(1.0), ActorInterval(mtoon, 'duck'), ActorInterval(mtoon, 'duck', startTime=1.8), Func(mtoon.loop, 'neutral')))

    returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    if hasAnimatedHead:
        returnval.append(headInterval)
    return returnval

def createVirtualSuitDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    deathSuit = suit
    headInterval = Parallel()
    hasAnimatedHead = False
    if suit.style.name == 'wsi':
        from toontown.battle import MovieCamera
        suitTrack.append(MovieCamera.motionShot(0.0, 10.0, 8.0, -180, -10.0, 0.0, 0, suit))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "Ugh... I don't get paid enough for this...",
                              CFSpeech | CFTimeout))
        suitTrack.append(ActorInterval(suit, 'defeated-into'))
        suitTrack.append(Func(suit.loop, 'defeated-loop'))
        suitTrack.append(Wait(4.0))
        suitTrack.append(Func(suit.setChatAbsolute,
                              "My requital will be gained one way or another. This isn't over.",
                              CFSpeech | CFTimeout))
        suitTrack.append(Wait(4.0))
        suitTrack.append(ActorInterval(suit, 'defeated-out'))
    for headPart in suit.animatedHeadParts:
        headInterval.append(ActorInterval(headPart, 'death', duration=2))
        hasAnimatedHead = True
    if suit.style.name == 'hrollers' or suit.style.name == 'bcaster':
        suitTrack.append(Func(notify.debug, 'before insertDeathSuit'))
        suitTrack.append(Func(insertDeathSuit, suit, deathSuit, battle))
        suitTrack.append(Parallel(ActorInterval(suit, 'mplayer-kneel-into')))
        deathSound = base.loadSfx('phase_11/audio/sfx/LB_capacitor_discharge_3.ogg')
        suitTrack.append(Parallel(Func(suit.loop, 'mplayer-kneel-neutral'), LerpColorScaleInterval(suit, duration=1.25, colorScale=(0, 0, 0, 0),
                                   blendType='easeInOut'), SoundInterval(deathSound, volume=0.5)))
        suitTrack.append(Func(notify.debug, 'before removeDeathSuit'))
        suitTrack.append(Func(removeDeathSuit, suit, deathSuit, name='remove-death-suit'))
        suitTrack.append(Func(notify.debug, 'after removeDeathSuit'))
        suitTrack.append(Func(suit.makeDead))
    else:
        suitTrack.append(Func(notify.debug, 'before insertDeathSuit'))
        suitTrack.append(Func(insertDeathSuit, suit, suit, battle, suitPos, suitHpr))
        suitTrack.append(Parallel(ActorInterval(suit, 'lose', duration=2), headInterval))
        deathSound = base.loadSfx('phase_11/audio/sfx/LB_laser_beam_off_death.ogg')
        suitTrack.append(Parallel(ActorInterval(suit, 'slip-forward', duration=2),
                                  LerpColorScaleInterval(suit, duration=1.0, colorScale=(0, 0, 0, 0),
                                                         blendType='easeInOut'), SoundInterval(deathSound, volume=0.5)))
        suitTrack.append(Func(notify.debug, 'before removeDeathSuit'))
        suitTrack.append(Func(removeDeathSuit, suit, suit, name='remove-death-suit'))
        suitTrack.append(Func(notify.debug, 'after removeDeathSuit'))
        suitTrack.append(Func(suit.makeDead))
    suitTrack.append(Func(suit.hide))
    returnval = Parallel()
    multiTrack = Parallel(suitTrack, returnval)
    if hasAnimatedHead:
        if not suit.style.name == 'wsi' and not suit.style.name == 'bcaster' and not suit.style.name == 'hrollers':
            returnval.append(headInterval)
    return multiTrack


def createSuitDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    if suit.style.name == 'arbit':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    elif suit.style.name == 'rainmake':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    elif suit.style.name == 'videog':
        for headPart in suit.animatedHeadParts:
            texture = loader.loadTexture('phase_9/maps/ttcc_ene_videographer2.png')
            headInterval = Parallel(ActorInterval(headPart, 'death'), Func(headPart.setTexture, texture, 1))
            hasAnimatedHead = True
    else:
        for headPart in suit.animatedHeadParts:
            headInterval = ActorInterval(headPart, 'death')
            hasAnimatedHead = True
    suitTrack.append(Func(battle.unlureSuit, suit))
    suitTrack.append(Func(battle.unSueSuit, suit))
    suitTrack.append(Func(suit.setDizzy, 0))
    suitTrack.append(Func(suit.setSued2, 0))
    suitTrack.append(Func(insertDeathSuit, suit, suit, battle, suitPos, suitHpr))
    suitTrack.append(ActorInterval(suit, 'lose'))
    suitTrack.append(Func(removeDeathSuit, suit, suit, name='remove-death-suit'))
    suitTrack.append(Func(suit.hide))
    if suit.style.name == 'caseman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'stenog' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'ddiver' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
    elif suit.style.name == 'sgoat' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
    elif suit.style.name == 'lgator' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'bellring' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'whunter' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'racket' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'chairman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'ottoman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'fires' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'prethink' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'duckshfl' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'hrollers' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'chainsaw' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'chainsaw2' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'treek' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
    elif suit.style.name == 'mouthp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
    elif suit.style.name == 'hroller2' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'rainmake' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'mplayer' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'psetter' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'videog' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'bkeeper' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'phouse' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'wtapper' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'hroller' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'ambass':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'safesupervis' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'dold' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'duckshfl' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'derrhand' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'derrhand' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'derrman' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
    elif suit.style.name == 'fbed' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'arbit' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
    elif suit.style.name == 'dopa':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'dopr':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'ubuster':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'radiog':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'djockey' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'ptjockey' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'pcrat' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'racket' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'dking' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'redd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.isFemale and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.isFemaleSkelecog and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.isSkelecogDialogue:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    elif deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    else:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
    deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    deathSoundTrack = Sequence(Wait(0.8), SoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.2), SoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.8), SoundInterval(deathSound, volume=0.32))
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
    explosionTrack.append(Wait(5.4))
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    suitIndex = battle.activeSuits.index(suit)
    if suit.getExecutive() or suit.getGovernaught():
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
    else:
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
    gears1Track = Sequence(Wait(2.1), ParticleInterval(smallGears, battle, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
    gears2MTrack = Track((0.0, explosionTrack), (0.7, ParticleInterval(singleGear, battle, worldRelative=0, duration=5.7, cleanup=True)), (5.2, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=1.2, cleanup=True)), (5.4, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')
    toonMTrack = Parallel(name='toonMTrack')
    for mtoon in battle.toons:
        toonMTrack.append(Sequence(Wait(1.0), ActorInterval(mtoon, 'duck'), ActorInterval(mtoon, 'duck', startTime=1.8), Func(mtoon.loop, 'neutral')))
    returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    if hasAnimatedHead:
        returnval.append(headInterval)
    return returnval

def __HighRollerAbsorb(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].dna.name == 'hroller':
        showDamage = Sequence(Func(suits[suitIndex].addLevelDamage, suits[suitIndex], int(hp)))
        return showDamage
    else:
        return Sequence()

def __ComboSilhouette(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].dna.name == 'hrollers' and suits[suitIndex].getActualLevel() == 25:
        from toontown.battle import MovieCamera
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextStringSacrifice, 'NICE COMBO!', openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, hp)
        cameraTrack = Sequence(MovieCamera.randomActorShot(suits[suitIndex], battle, 0, 'suit'))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(cameraTrack))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        return suitTrack
    else:
        return Sequence()

def __KnockbackSilhouette(suitIndex, suits, hp, battle):
    if len(suits) > suitIndex >= 0 and suits[suitIndex].dna.name == 'hrollers' and suits[suitIndex].getActualLevel() == 26:
        from toontown.battle import MovieCamera
        revives = suits[suitIndex].getSkeleRevives()
        suitTrack = Sequence()
        showDamage = Sequence(Func(suits[suitIndex].showHpTextStringKnockback, 'NICE KNOCKBACK!', openEnded=0))
        value = hp
        updateHealthBar = Func(suits[suitIndex].updateHealthBar, hp)
        cameraTrack = Sequence(MovieCamera.randomActorShot(suits[suitIndex], battle, 0, 'suit'))
        suitTrack.append(showDamage)
        suitTrack.append(updateHealthBar)
        suitTrack.append(Parallel(cameraTrack))
        suitTrack.append(Func(suits[suitIndex].setNeutralAnimation))
        return suitTrack
    else:
        return Sequence()

def createSuitHeadlessDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitTrack.append(ActorInterval(suit, 'lose2', duration=4.0))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.cleanupLoseActor))
    suitTrack.append(Func(suit.makeDead))
    deathSound = base.loadSfx('phase_5/audio/sfx/COG_headless_death.ogg')
    deathSoundTrack = Sequence(Wait(0), SoundInterval(deathSound, volume=0.6))
    suitIndex = battle.activeSuits.index(suit)
    if suit.getExecutive() or suit.getGovernaught():
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
    else:
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
    returnval = Parallel(suitTrack, deathSoundTrack)
    return returnval

def createSuitWreckingDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    deathSound = base.loadSfx('phase_5/audio/sfx/AA_trap_wreckingball_%s.ogg' % random.randint(1, 3))
    deathSoundTrack = Sequence(Wait(0), SoundInterval(deathSound, volume=0.6))
    suitTrack.append(ActorInterval(suit, 'lose3', duration=4.0))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.cleanupLoseActor))
    suitTrack.append(Func(suit.makeDead))
    suitIndex = battle.activeSuits.index(suit)
    if suit.getExecutive() or suit.getGovernaught():
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
    else:
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
    returnval = Parallel(suitTrack, deathSoundTrack)
    return returnval

def createSuitCrashTrack(suit, battle):
    suitScale = suit.getScale()
    node = suit.getGeomNode().getChild(0)
    suitPos = suit.getPos()
    hitTime = 0.1
    shrinkStartDelay = 3.0
    #crashSoundEffects = []
    #for sound in crashSounds:
        #crashSoundEffects.append(globalBattleSoundCache.getSound(sound))
    soundTrack = base.loadSfx('phase_5/audio/sfx/drop_react.ogg')
    deathSoundTrack = Sequence(Wait(0), SoundInterval(soundTrack, volume=1.0))
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(Wait(0.25), (ActorInterval(headPart, 'neutral', startTime=0, endTime=0)))
        hasAnimatedHead = True
    suitTrack = Sequence(Wait(0.175), Func(suit.setZ, suit.getZ() + .1),
                         Func(node.setScale, Point3(suitScale[0], suitScale[1], suitScale[2] * 0.0001)),
                         Func(node.setColorScale, Vec4(0.0, 0.0, 0.0, 1)),
                         Func(suit.deleteDropShadow),
                         Wait(shrinkStartDelay),
                         LerpScaleInterval(suit, 0.8, Point3(0.0001, 0.0001, 0.0001), blendType='easeIn'))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.cleanupLoseActor))
    suitTrack.append(Func(suit.makeDead))
    suitIndex = battle.activeSuits.index(suit)
    if suit.getExecutive() or suit.getGovernaught():
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
    else:
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
    if hasAnimatedHead:
        return Parallel(suitTrack, deathSoundTrack, headInterval)
    else:
        return Parallel(suitTrack, deathSoundTrack)

def midairSuitExplodeTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    #suitPos.setZ(suitPos.getZ() + 17)
    #suitTrack.append(Wait(0.15))
    suitTrack.append(Func(avatarHide, suit))
    suitTrack.append(Func(suit.cleanupLoseActor))
    suitTrack.append(Func(suit.makeDead))
    deathSound = base.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    suitIndex = battle.activeSuits.index(suit)
    if suit.getExecutive() or suit.getGovernaught():
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
    else:
        suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
    gears1Track = Sequence(Wait(0.5), ParticleInterval(smallGears, battle, worldRelative=0, duration=1.0, cleanup=True), name='gears1Track')
    gears2MTrack = Track(
        (0.1, ParticleInterval(singleGear, battle, worldRelative=0, duration=0.4, cleanup=True)),
        (0.5, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=0.5, cleanup=True)),
        (0.9, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=2.0, cleanup=True)), name='gears2MTrack'
    )
    return Parallel(suitTrack, explosionTrack, deathSoundTrack, gears1Track, gears2MTrack, Wait(4.5))

def createDesperationTrack(suit):
    from toontown.battle import MovieCamera
    theSuit = suit
    makeDesperate = Func(suit.makeDesperation)
    makeDamageUp = Func(suit.makeDamageUp)
    notifyTrack = Sequence(Wait(2.0), Func(theSuit.showHpText2,
                                           'DESPERATION!',
                                           2), Func(theSuit.showHpStringLureManager2,
                                           '1.4x Dmg Multiplier'), Func(theSuit.showHpString,
                                           '+1 Round Lure Resistance'))
    cameraTrack = Sequence(MovieCamera.motionShot(0.0, 10.0, 15.0, -180, -30.0, 0.0, 0, suit), Wait(2.0))
    talkTrack = Sequence(Wait(2.0), Func(theSuit.setChatAbsolute,
                              "Hmmm.",
                              CFSpeech | CFTimeout), Wait(4.0),
                         Func(theSuit.setChatAbsolute,
                              "Let's make this a little more interesting.",
                              CFSpeech | CFTimeout),
                         Wait(2.0))

    return Sequence(notifyTrack, cameraTrack, makeDamageUp, makeDesperate)

def shortCircuitTrackOLD(suit, battle):
    if suit.isHidden():
        return Sequence()
    else:
        suitTrack = Sequence()
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        suitTrack.append(Wait(0.15))
        suitTrack.append(Func(avatarHide, suit))
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
        explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
        gears1Track = Sequence(Wait(0.5), ParticleInterval(smallGears, battle, worldRelative=0, duration=1.0, cleanup=True), name='gears1Track')
        gears2MTrack = Track(
            (0.1, ParticleInterval(singleGear, battle, worldRelative=0, duration=0.4, cleanup=True)),
            (0.5, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=0.5, cleanup=True)),
            (0.9, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=2.0, cleanup=True)), name='gears2MTrack'
        )

        return Parallel(suitTrack, explosionTrack, deathSoundTrack, gears1Track, gears2MTrack)

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

def shortCircuitTrack(suit, battle):
    if suit.isHidden():
        return Sequence()
    else:
        suitTrack = Sequence(Wait(1.0))
        colorTracks = Parallel()
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.3, 0.3, 0.3)
        smoke.setScale(0.75, 1, 1)
        smoke.setTransparency(1)
        smoke.setTwoSided(True)
        smoke.setBillboardPointEye()
        actorNode = suit.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        for headPart in suit.headParts:
            colorTracks.append(Sequence(Func(headPart.setDepthWrite, False), Func(headPart.setBin, 'fixed', 1),
                                        LerpColorScaleInterval(headPart, 1.0, (0, 0, 0, 0)),
                                        Func(headPart.setAttrib, ColorBlendAttrib.make(ColorBlendAttrib.MAdd))))
        for thingIndex in xrange(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            colorTracks.append(Sequence(Func(thing.setDepthWrite, False), Func(thing.setBin, 'fixed', 1),
                                        LerpColorScaleInterval(thing, 1.0, (0, 0, 0, 0)),
                                        Func(thing.setAttrib, ColorBlendAttrib.make(ColorBlendAttrib.MAdd))))
        smokeTrack = Sequence(Func(smoke.reparentTo, battle), LerpPosInterval(smoke, 0, Point3(toonPos.getX(), y - 5, toonPos.getZ())),
                              Parallel(Sequence(LerpScaleInterval(smoke, 2.0, Point3(.5, 1, 5)),
                                                LerpScaleInterval(smoke, 2.5, Point3(.5, 1, 10))),
                                       Sequence(Wait(1.5), LerpColorScaleInterval(smoke, 2.0, Vec4(1, 1, 1, 0)))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(removeProp, smoke))
        suitPos = suit.getPos(battle)
        suitTrack.append(Func(suit.hide))
        suitTrack.append(Func(suit.cleanupLoseActor))
        suitTrack.append(Func(suit.makeDead))
        suitTrack.append(Wait(1.0))
        BattleParticles.loadParticles()
        explodePosPoints = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ()), PNT3_ZERO]
        splatName = 'dust2'
        explode = globalPropPool.getProp('dust2')
        explode.setTwoSided(True)
        explode.setColor(0.251, 0.251, 0.251, 1)
        explode.setTransparency(1)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence(Wait(0.3))
        explodeTrack.append(
            getPropAppearTrack(explode, battle, explodePosPoints, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        explodePosPoints2 = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() - 2), PNT3_ZERO]
        splatName = 'dust2'
        explode2 = globalPropPool.getProp('dust2')
        explode2.setTwoSided(True)
        explode2.setColor(0.251, 0.251, 0.251, 1)
        explode2.setTransparency(1)
        explode2.setBillboardPointWorld(2)
        explodeTrack2 = Sequence(Wait(.15))
        explodeTrack2.append(
            getPropAppearTrack(explode2, battle, explodePosPoints2, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=0))
        explodeTrack2.append(Sequence(ActorInterval(explode2, splatName), Func(explode2.detachNode)))
        explodePosPoints3 = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + 2), PNT3_ZERO]
        splatName = 'dust2'
        explode3 = globalPropPool.getProp('dust2')
        explode3.setTwoSided(True)
        explode3.setColor(0.251, 0.251, 0.251, 1)
        explode3.setTransparency(1)
        explode3.setBillboardPointWorld(2)
        explodeTrack3 = Sequence(Wait(.45))
        explodeTrack3.append(
            getPropAppearTrack(explode3, battle, explodePosPoints3, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=0))
        explodeTrack3.append(Sequence(ActorInterval(explode3, splatName), Func(explode3.detachNode)))
        explodePosPoints4 = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + 4), PNT3_ZERO]
        explode4 = globalPropPool.getProp('dust2')
        explode4.setTwoSided(True)
        explode4.setColor(0.251, 0.251, 0.251, 1)
        explode4.setTransparency(1)
        explode4.setBillboardPointWorld(2)
        explodeTrack4 = Sequence(Wait(.6))
        explodeTrack4.append(
            getPropAppearTrack(explode3, battle, explodePosPoints4, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=0))
        explodeTrack4.append(Sequence(ActorInterval(explode4, splatName), Func(explode4.detachNode)))
        explodePosPoints5 = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() - 4), PNT3_ZERO]
        explode5 = globalPropPool.getProp('dust2')
        explode5.setTwoSided(True)
        explode5.setColor(0.251, 0.251, 0.251, 1)
        explode5.setTransparency(1)
        explode5.setBillboardPointWorld(2)
        explodeTrack5 = Sequence()
        explodeTrack5.append(
            getPropAppearTrack(explode5, battle, explodePosPoints5, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=0))
        explodeTrack5.append(Sequence(ActorInterval(explode5, splatName), Func(explode5.detachNode)))
        suitIndex = battle.activeSuits.index(suit)
        if suit.getExecutive() or suit.getGovernaught():
            suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 7), battle))
        else:
            suitTrack.append(__HighRollerAbsorb(suitIndex - 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 1, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex - 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 2, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex - 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 3, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex - 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 4, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex - 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
            suitTrack.append(__HighRollerAbsorb(suitIndex + 5, battle.activeSuits, (suit.getActualLevel() * 4), battle))
        return Parallel(suitTrack, explodeTrack, explodeTrack2, explodeTrack3, explodeTrack4, explodeTrack5, colorTracks)

def shortCircuitTrack2(suit, battle):
    if suit.isHidden():
        return Sequence()
    else:
        suitTrack = Sequence(Wait(1.5))
        colorTracks = Parallel()
        smoke = loader.loadModel('phase_4/models/props/test_clouds')
        smoke.setColor(0.3, 0.3, 0.3)
        smoke.setScale(0.75, 1, 1)
        smoke.setTransparency(1)
        smoke.setTwoSided(True)
        smoke.setBillboardPointEye()
        actorNode = suit.find('**/__Actor_modelRoot')
        actorCollection = actorNode.findAllMatches('*')
        parts = ()
        toonPos = suit.getPos(battle)
        y = toonPos.getY()
        for headPart in suit.headParts:
            colorTracks.append(Sequence(Func(headPart.setDepthWrite, False), Func(headPart.setBin, 'fixed', 1),
                                        LerpColorScaleInterval(headPart, 1.0, (0, 0, 0, 0)),
                                        Func(headPart.setAttrib, ColorBlendAttrib.make(ColorBlendAttrib.MAdd))))
        for thingIndex in xrange(0, actorCollection.getNumPaths()):
            thing = actorCollection[thingIndex]
            colorTracks.append(Sequence(Func(thing.setDepthWrite, False), Func(thing.setBin, 'fixed', 1),
                                        LerpColorScaleInterval(thing, 1.0, (0, 0, 0, 0)),
                                        Func(thing.setAttrib, ColorBlendAttrib.make(ColorBlendAttrib.MAdd))))
        smokeTrack = Sequence(Func(smoke.reparentTo, battle), LerpPosInterval(smoke, 0, Point3(toonPos.getX(), y - 5, toonPos.getZ())),
                              Parallel(Sequence(LerpScaleInterval(smoke, 2.0, Point3(.5, 1, 5)),
                                                LerpScaleInterval(smoke, 2.5, Point3(.5, 1, 10))),
                                       Sequence(Wait(1.5), LerpColorScaleInterval(smoke, 2.0, Vec4(1, 1, 1, 0)))),
                              Func(smoke.reparentTo, hidden), Func(smoke.clearColorScale),
                              Func(removeProp, smoke))
        suitPos = suit.getPos(battle)
        suitTrack.append(Func(suit.hide))
        suitTrack.append(Func(suit.cleanupLoseActor))
        suitTrack.append(Func(suit.makeDead))
        suitTrack.append(Wait(1.0))
        BattleParticles.loadParticles()
        explodePosPoints = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ()), PNT3_ZERO]
        splatName = 'dust2'
        explode = globalPropPool.getProp('dust2')
        explode.setTwoSided(True)
        explode.setColor(0.251, 0.251, 0.251, 1)
        explode.setTransparency(1)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence(Wait(0.3))
        explodeTrack.append(
            getPropAppearTrack(explode, battle, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        explodePosPoints2 = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() - 2), PNT3_ZERO]
        splatName = 'dust2'
        explode2 = globalPropPool.getProp('dust2')
        explode2.setTwoSided(True)
        explode2.setColor(0.251, 0.251, 0.251, 1)
        explode2.setTransparency(1)
        explode2.setBillboardPointWorld(2)
        explodeTrack2 = Sequence(Wait(.15))
        explodeTrack2.append(
            getPropAppearTrack(explode2, battle, explodePosPoints2, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack2.append(Sequence(ActorInterval(explode2, splatName), Func(explode2.detachNode)))
        explodePosPoints3 = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + 2), PNT3_ZERO]
        splatName = 'dust2'
        explode3 = globalPropPool.getProp('dust2')
        explode3.setTwoSided(True)
        explode3.setColor(0.251, 0.251, 0.251, 1)
        explode3.setTransparency(1)
        explode3.setBillboardPointWorld(2)
        explodeTrack3 = Sequence(Wait(.45))
        explodeTrack3.append(
            getPropAppearTrack(explode3, battle, explodePosPoints3, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack3.append(Sequence(ActorInterval(explode3, splatName), Func(explode3.detachNode)))
        explodePosPoints4 = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + 4), PNT3_ZERO]
        explode4 = globalPropPool.getProp('dust2')
        explode4.setTwoSided(True)
        explode4.setColor(0.251, 0.251, 0.251, 1)
        explode4.setTransparency(1)
        explode4.setBillboardPointWorld(2)
        explodeTrack4 = Sequence(Wait(.6))
        explodeTrack4.append(
            getPropAppearTrack(explode3, battle, explodePosPoints4, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack4.append(Sequence(ActorInterval(explode4, splatName), Func(explode4.detachNode)))
        explodePosPoints5 = [Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() - 4), PNT3_ZERO]
        explode5 = globalPropPool.getProp('dust2')
        explode5.setTwoSided(True)
        explode5.setColor(0.251, 0.251, 0.251, 1)
        explode5.setTransparency(1)
        explode5.setBillboardPointWorld(2)
        explodeTrack5 = Sequence()
        explodeTrack5.append(
            getPropAppearTrack(explode3, battle, explodePosPoints5, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack5.append(Sequence(ActorInterval(explode5, splatName), Func(explode5.detachNode)))
        return Parallel(suitTrack, explodeTrack, explodeTrack2, explodeTrack3, explodeTrack4, explodeTrack5, colorTracks)


def createSuitDodgeMultitrack(tDodge, suit, leftSuits, rightSuits):
    suitTracks = Parallel()
    soundTrack = base.loadSfx('phase_5/audio/sfx/ENC_cogjump_to_side.ogg')
    suitDodgeList, sidestepAnim = avatarDodge(leftSuits, rightSuits, 'sidestep-left', 'sidestep-right')
    for s in suitDodgeList:
        suitTracks.append(Sequence(ActorInterval(s, sidestepAnim),  Func(s.setNeutralAnimationDrop)))

    suitTracks.append(Sequence(ActorInterval(suit, sidestepAnim), Func(suit.setNeutralAnimationDrop)))
    suitTracks.append(Func(indicateMissed, suit))
    suitTracks.append(Sequence(SoundInterval(soundTrack, volume=0.7)))
    return Sequence(Wait(tDodge), suitTracks)


def createToonDodgeMultitrack(tDodge, toon, leftToons, rightToons):
    toonTracks = Parallel()
    if len(leftToons) > len(rightToons):
        PoLR = rightToons
        PoMR = leftToons
    else:
        PoLR = leftToons
        PoMR = rightToons
    upper = 1 + 4 * abs(len(leftToons) - len(rightToons))
    if random.randint(0, upper) > 0:
        toonDodgeList = PoLR
    else:
        toonDodgeList = PoMR
    if toonDodgeList is leftToons:
        sidestepAnim = 'sidestep-left'
        for t in toonDodgeList:
            toonTracks.append(Sequence(ActorInterval(t, sidestepAnim), Func(t.loop, 'neutral')))

    else:
        sidestepAnim = 'sidestep-right'
    toonTracks.append(Sequence(ActorInterval(toon, sidestepAnim), Func(toon.loop, 'neutral')))
    toonTracks.append(Func(indicateMissed, toon))
    return Sequence(Wait(tDodge), toonTracks)


def createSuitTeaseMultiTrack(suit, battle, delay = 0.01):
    if suit.dna.name == 'sgoat' and suit.isAngry:
        suitTrack = Sequence(Wait(delay - 1), ActorInterval(suit, 'neutral-enraged-return'), ActorInterval(suit, 'gag-miss'))
    elif suit.isImmortal and not suit.dna.name == 'hroller' and not suit.dna.name == 'wtapper' and not suit.dna.name == 'videog' and suit.isPhase3:
        suitTrack = Sequence(Wait(delay - 1), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0, duration=1), ActorInterval(suit, 'gag-miss'))
    else:
        suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'))
    if suit.isLured:
        suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'), Func(suit.loop, 'lured'))
    elif suit.dna.name == 'sgoat' and suit.isAngry:
        suitTrack.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        suitTrack.append(Func(suit.loop, 'neutral-enraged'))
    elif suit.dna.name == 'hroller2' and suit.isVulnerable:
        suitTrack.append(Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isImmortal and not suit.dna.name == 'hroller' and not suit.dna.name == 'wtapper' and not suit.dna.name == 'videog' and suit.isPhase3:
        suitTrack.append(Sequence(ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1),
                                  Func(suit.loop, 'highroller-neutral-levitate-loop')))
    else:
        suitTrack.append(Func(suit.setNeutralAnimationDrop))
    missedTrack = Sequence(Wait(delay + 0.2), Func(indicateMissed, suit, 0.9))
    return Parallel(suitTrack, missedTrack)

def createSuitTeaseMultiTrackSound(suit, battle, delay = 0.01):
    if suit.dna.name == 'sgoat' and suit.isAngry:
        suitTrack = Sequence(Wait(delay - 1), ActorInterval(suit, 'neutral-enraged-return'), ActorInterval(suit, 'gag-miss'))
    elif suit.isImmortal and not suit.dna.name == 'hroller' and not suit.dna.name == 'wtapper' and not suit.dna.name == 'videog' and suit.isPhase3:
        suitTrack = Sequence(Wait(delay - 1), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0, duration=1), ActorInterval(suit, 'gag-miss'))
    else:
        suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'))
    if suit.isLured:
        suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'), Func(suit.setNeutralAnimationTrap))
    elif suit.dna.name == 'sgoat' and suit.isAngry:
        suitTrack.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        suitTrack.append(Func(suit.loop, 'neutral-enraged'))
    elif suit.dna.name == 'hroller2' and suit.isVulnerable:
        suitTrack.append(Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isImmortal and not suit.dna.name == 'hroller' and not suit.dna.name == 'wtapper' and not suit.dna.name == 'videog' and suit.isPhase3:
        suitTrack.append(Sequence(ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1),
                                  Func(suit.loop, 'highroller-neutral-levitate-loop')))
    else:
        suitTrack.append(Func(suit.setNeutralAnimationTrap))
    missedTrack = Sequence(Wait(delay + 0.2), Func(indicateMissed, suit, 0.9))
    return Parallel(suitTrack, missedTrack)

def createSuitTeaseMultiTrackDrop(suit, battle, delay = 0.01):
    suitTrack = Sequence(Wait(delay), Wait(2.5), Func(suit.setNeutralAnimationDrop))
    missedTrack = Sequence(Wait(delay + 0.2))
    return Parallel(missedTrack)


SPRAY_LEN = 1.5

def getSprayTrack(battle, color, origin, target, dScaleUp, dHold, dScaleDown, horizScale = 1.0, vertScale = 1.0, parent = render):
    track = Sequence()
    sprayProp = globalPropPool.getProp('spray')
    sprayScale = hidden.attachNewNode('spray-parent')
    sprayRot = hidden.attachNewNode('spray-rotate')
    spray = sprayRot
    spray.setColor(color)
    if color[3] < 1.0:
        spray.setTransparency(1)

    def showSpray(sprayScale, sprayRot, sprayProp, origin, target, parent):
        if callable(origin):
            origin = origin()
        if callable(target):
            target = target()
        sprayRot.reparentTo(parent)
        sprayRot.clearMat()
        sprayScale.reparentTo(sprayRot)
        sprayScale.clearMat()
        sprayProp.reparentTo(sprayScale)
        sprayProp.clearMat()
        sprayRot.setPos(origin)
        sprayRot.lookAt(Point3(target))

    track.append(Func(battle.movie.needRestoreRenderProp, sprayProp))
    track.append(Func(showSpray, sprayScale, sprayRot, sprayProp, origin, target, parent))

    def calcTargetScale(target = target, origin = origin, horizScale = horizScale, vertScale = vertScale):
        if callable(target):
            target = target()
        if callable(origin):
            origin = origin()
        distance = Vec3(target - origin).length()
        yScale = distance / SPRAY_LEN
        targetScale = Point3(yScale * horizScale, yScale, yScale * vertScale)
        return targetScale

    track.append(LerpScaleInterval(sprayScale, dScaleUp, calcTargetScale, startScale=PNT3_NEARZERO))
    track.append(Wait(dHold))

    def prepareToShrinkSpray(spray, sprayProp, origin, target):
        if callable(target):
            target = target()
        if callable(origin):
            origin = origin()
        sprayProp.setPos(Point3(0.0, -SPRAY_LEN, 0.0))
        spray.setPos(target)

    track.append(Func(prepareToShrinkSpray, spray, sprayProp, origin, target))
    track.append(LerpScaleInterval(sprayScale, dScaleDown, PNT3_NEARZERO))

    def hideSpray(spray, sprayScale, sprayRot, sprayProp, propPool):
        sprayProp.detachNode()
        removeProp(sprayProp)
        sprayRot.removeNode()
        sprayScale.removeNode()

    track.append(Func(hideSpray, spray, sprayScale, sprayRot, sprayProp, globalPropPool))
    track.append(Func(battle.movie.clearRenderProp, sprayProp))
    return track

def getZapTrack(battle, color, origin, target, dScaleUp, dHold, dScaleDown, horizScale = 1.0, vertScale = 1.0, parent = render):
    track = Sequence()
    sprayProp = globalPropPool.getProp('spray')
    sprayScale = hidden.attachNewNode('spray-parent')
    sprayRot = hidden.attachNewNode('spray-rotate')
    spray = sprayRot
    spray.setColor(color)
    if color[3] < 1.0:
        spray.setTransparency(1)

    def showSpray(sprayScale, sprayRot, sprayProp, origin, target, parent):
        if callable(origin):
            origin = origin()
        if callable(target):
            target = target()
        sprayRot.reparentTo(parent)
        sprayRot.clearMat()
        sprayScale.reparentTo(sprayRot)
        sprayScale.clearMat()
        sprayProp.reparentTo(sprayScale)
        sprayProp.clearMat()
        sprayRot.setPos(origin)
        sprayRot.lookAt(Point3(target))

    track.append(Func(battle.movie.needRestoreRenderProp, sprayProp))
    track.append(Func(showSpray, sprayScale, sprayRot, sprayProp, origin, target, parent))

    def calcTargetScale(target = target, origin = origin, horizScale = horizScale, vertScale = vertScale):
        if callable(target):
            target = target()
        if callable(origin):
            origin = origin()
        distance = Vec3(target - origin).length()
        yScale = distance / SPRAY_LEN
        targetScale = Point3(yScale * horizScale, yScale, yScale * vertScale)
        return targetScale

    track.append(LerpScaleInterval(sprayScale, dScaleUp, calcTargetScale, startScale=PNT3_NEARZERO))
    track.append(Wait(dHold))

    def prepareToShrinkSpray(spray, sprayProp, origin, target):
        if callable(target):
            target = target()
        if callable(origin):
            origin = origin()
        sprayProp.setPos(Point3(0.0, -SPRAY_LEN, 0.0))
        spray.setPos(target)

    track.append(Func(prepareToShrinkSpray, spray, sprayProp, origin, target))
    track.append(LerpScaleInterval(sprayScale, dScaleDown, PNT3_NEARZERO))

    def hideSpray(spray, sprayScale, sprayRot, sprayProp, propPool):
        sprayProp.detachNode()
        removeProp(sprayProp)
        sprayRot.removeNode()
        sprayScale.removeNode()

    track.append(Func(hideSpray, spray, sprayScale, sprayRot, sprayProp, globalPropPool))
    track.append(Func(battle.movie.clearRenderProp, sprayProp))
    return track


T_HOLE_LEAVES_HAND = 1.708
T_TELEPORT_ANIM = 3.3
T_HOLE_CLOSES = 0.3

def createButtonInterval(battle, delay, originHpr, suitPos, toon):
    button = globalPropPool.getProp('button')
    button2 = copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    toonTrack = Sequence(Wait(delay),
                         Func(toon.headsUp, battle, suitPos),
                         ActorInterval(toon, 'pushbutton'),
                         Func(toon.loop, 'neutral'),
                         Func(toon.setHpr, battle, originHpr))
    buttonTrack = Sequence(Wait(delay),
                           Func(showProps, buttons, hands),
                           LerpScaleInterval(button, 1.0, button.getScale(), startScale=Point3(0.01, 0.01, 0.01)),
                           Wait(2.5),
                           LerpScaleInterval(button, 1.0, Point3(0.01, 0.01, 0.01), startScale=button.getScale()),
                           Func(removeProps, buttons))
    return toonTrack, buttonTrack

def createButtonIntervalZap(battle, delay, originHpr, suitPos, toon):
    button = globalPropPool.getProp('zap-button')
    button2 = copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    toonTrack = Sequence(Wait(delay),
                         Func(toon.headsUp, battle, suitPos),
                         ActorInterval(toon, 'pushbutton'),
                         Func(toon.loop, 'neutral'),
                         Func(toon.setHpr, battle, originHpr))
    buttonTrack = Sequence(Wait(delay),
                           Func(showProps, buttons, hands), ActorInterval(button, 'zap-button'),
                           LerpScaleInterval(button, 1.0, Point3(0.01, 0.01, 0.01), startScale=button.getScale()),
                           Func(removeProps, buttons))
    return toonTrack, buttonTrack

def createButtonIntervalDrop(battle, delay, originHpr, suitPos, toon):
    button = globalPropPool.getProp('drop-button')
    button2 = copyProp(button)
    buttons = [button, button2]
    hands = toon.getLeftHands()
    toonTrack = Sequence(Wait(delay),
                         Func(toon.headsUp, battle, suitPos),
                         ActorInterval(toon, 'pushbutton'),
                         Func(toon.loop, 'neutral'),
                         Func(toon.setHpr, battle, originHpr))
    buttonTrack = Sequence(Wait(delay),
                           Func(showProps, buttons, hands),
                           ActorInterval(button, 'drop-button'),
                           LerpScaleInterval(button, 1.0, Point3(0.01, 0.01, 0.01), startScale=button.getScale()),
                           Func(removeProps, buttons))
    return toonTrack, buttonTrack


def getToonTeleportOutInterval(toon):
    holeActors = toon.getHoleActors()
    holes = [holeActors[0], holeActors[1]]
    hole = holes[0]
    hole2 = holes[1]
    hands = toon.getRightHands()
    delay = T_HOLE_LEAVES_HAND
    dur = T_TELEPORT_ANIM
    holeTrack = Sequence()
    holeTrack.append(Func(showProps, holes, hands))
    (holeTrack.append(Wait(0.5)),)
    holeTrack.append(Func(base.playSfx, toon.getSoundTeleport()))
    holeTrack.append(Wait(delay - 0.5))
    holeTrack.append(Func(hole.reparentTo, toon))
    holeTrack.append(Func(hole2.reparentTo, hidden))
    holeAnimTrack = Sequence()
    holeAnimTrack.append(ActorInterval(hole, 'hole', duration=dur))
    holeAnimTrack.append(Func(hideProps, holes))
    runTrack = Sequence(ActorInterval(toon, 'teleport', duration=dur), Wait(T_HOLE_CLOSES), Func(toon.detachNode))
    return Parallel(runTrack, holeAnimTrack, holeTrack)


def getToonTeleportInInterval(toon):
    hole = toon.getHoleActors()[0]
    holeAnimTrack = Sequence()
    holeAnimTrack.append(Func(toon.detachNode))
    holeAnimTrack.append(Func(hole.reparentTo, toon))
    pos = Point3(0, -2.4, 0)
    holeAnimTrack.append(Func(hole.setPos, toon, pos))
    holeAnimTrack.append(ActorInterval(hole, 'hole', startTime=T_TELEPORT_ANIM, endTime=T_HOLE_LEAVES_HAND))
    holeAnimTrack.append(ActorInterval(hole, 'hole', startTime=T_HOLE_LEAVES_HAND, endTime=T_TELEPORT_ANIM))
    holeAnimTrack.append(Func(hole.reparentTo, hidden))
    delay = T_TELEPORT_ANIM - T_HOLE_LEAVES_HAND
    jumpTrack = Sequence(Wait(delay), Func(toon.reparentTo, render), ActorInterval(toon, 'jump'))
    return Parallel(holeAnimTrack, jumpTrack)

def getSuitStuns(attacks):
    fShowStun = 0
    if isGroupAttack(attacks[0]):
        for target in attacks[0]['target']:
            fShowStun = len(attacks) == 1 and target['hp'] > 0
    else:
        fShowStun = len(attacks) == 1 and attacks[0]['target']['hp'] > 0
    return fShowStun


def isGroupAttack(attack):
    return isinstance(attack['target'], type([]))


def getSuitRakeOffset(suit):
    return 0


def startSparksIval(tntProp):
    tip = tntProp.find('**/joint_attachEmitter')
    sparks = BattleParticles.createParticleEffect(file='tnt')
    return Func(sparks.start, tip)


def indicateMissed(actor, duration = 1.1, scale = 0.7):
    actor.showHpStringMissed(TTLocalizer.AttackMissed, duration=duration, scale=scale)


def createKapowExplosionTrack(parent, explosionPoint = None, scale = 1.0):
    explosionTrack = Sequence()
    explosion = loader.loadModel('phase_3.5/models/props/explosion.bam')
    explosion.setBillboardPointEye()
    explosion.setDepthWrite(False)
    if not explosionPoint:
        explosionPoint = Point3(0, 3.6, 2.1)
    explosionTrack.append(Func(explosion.reparentTo, parent))
    explosionTrack.append(Func(explosion.setPos, explosionPoint))
    explosionTrack.append(Func(explosion.setScale, 0.4 * scale))
    explosionTrack.append(Wait(0.6))
    explosionTrack.append(Func(removeProp, explosion))
    return explosionTrack


def createKapowExplosionTrackAttack(parent, explosionPoint = None, scale = 1.0):
    explosionTrack = Sequence()
    explosion = loader.loadModel('phase_3.5/models/props/explosion.bam')
    explosion.setBillboardPointEye()
    explosion.setDepthWrite(False)
    if not explosionPoint:
        explosionPoint = Point3(0, 3.6, 2.1)
    explosionTrack.append(Func(explosion.reparentTo, parent))
    explosionTrack.append(Func(explosion.setPos, explosionPoint))
    explosionTrack.append(Func(explosion.setScale, 1.4 * scale))
    explosionTrack.append(Wait(.6))
    explosionTrack.append(Func(removeProp, explosion))
    return explosionTrack


def createSuitEnragedInterval(suit, before):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'enraged'), Func(headPart.loop,
                        'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        headInterval2 = Sequence(Wait(0.5), ActorInterval(headPart, 'death', duration=2), ActorInterval(headPart, 'grunt'))
        headLoop = ActorInterval(suit, 'neutral-enraged', duration=4)
        headLoop2 = Func(headPart.loop,
                        'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        hasAnimatedHead = True
    if hasAnimatedHead and not suit.isSkeleton:
        return Sequence(Wait(before), headInterval, headLoop2)
    elif hasAnimatedHead:
        return Sequence(Wait(before), headInterval2, headLoop2)
    else:
        return Sequence(Wait(before), headInterval, headLoop2)

def createSuitLaughInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    suitInterval = ActorInterval(suit, 'wheelspin')
    for headPart in suit.animatedHeadParts:
        headInterval = ActorInterval(headPart, 'wheelspin')
        headLoop = Func(headPart.loop,
                            'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        hasAnimatedHead = True
        return Parallel(headInterval, suitInterval)
    else:
        return stunInterval

def createSuitLaughIntervalDice(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    suitInterval = ActorInterval(suit, 'wheelspin', startTime=2.25, endTime=5.75)
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'wheelspin', startTime=2.25, endTime=5.75),  Func(headPart.loop,
                        'neutral'))
        headLoop = ActorInterval(suit, 'wheelspin', startTime=2.5, endTime=5.5)
        hasAnimatedHead = True
        return Parallel(headInterval, suitInterval)
    else:
        return stunInterval

def createSuitBustInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    suitInterval = ActorInterval(suit, 'bust')
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'bust'),  Func(headPart.loop,
                        'neutral'))
        headLoop = ActorInterval(suit, 'bust')
        hasAnimatedHead = True
        return Parallel(headInterval, suitInterval)
    else:
        return stunInterval

def createSuitLaughInterval2(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    suitInterval = ActorInterval(suit, 'wheelspin')
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'wheelspin', startTime=0, endTime=2.5),  Func(headPart.loop,
                            'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
        headLoop = Func(headPart.loop,
                            'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        hasAnimatedHead = True
        return headInterval
    else:
        return stunInterval

def createSuitInsuranceInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    suitInterval = ActorInterval(suit, 'throw-insurance')
    if suit.style.name == 'caseman':
        suitInterval = ActorInterval(suit, 'throw-insurance')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'insurance'), Func(headPart.loop, 'neutral'))
            headLoop = Func(headPart.loop,
                        'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval)
    else:
        return stunInterval

def createSuitInsuranceInterval2(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.setNeutralAnimation)
    hasAnimatedHead = False
    suitInterval = ActorInterval(suit, 'throw-paper')
    if suit.style.name == 'ubuster':
        suitInterval = ActorInterval(suit, 'throw-paper')
        return suitInterval
    else:
        return stunInterval

def createSuitBellowInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    if suit.style.name == 'lgator':
        suitInterval = ActorInterval(suit, 'bellow')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'bellow'), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    elif suit.style.name == 'chairman':
        suitInterval = ActorInterval(suit, 'bellow')
        for headPart in suit.animatedHeadParts:
            headInterval = ActorInterval(headPart, 'bellow')
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    else:
        return stunInterval

def createSuitSnapInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    if suit.style.name == 'lgator':
        if suit.isSkeleton:
            suitInterval = ActorInterval(suit, 'snap')
        else:
            suitInterval = ActorInterval(suit, 'snap2')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'gsnap'), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    else:
        return stunInterval

def createSuitCaseClosedInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    if suit.style.name == 'cm':
        suitInterval = Sequence(ActorInterval(suit, 'glower', duration=1.0), Wait(3.0), ActorInterval(suit, 'glower', startTime=1.0))
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'death', duration=1.0), ActorInterval(headPart, 'death', startTime=1.0, endTime=0, playRate=4.0))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval)
    else:
        return stunInterval

def createSuitHeadHonchoCigarSmokeInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
    hasAnimatedHead = False
    if suit.style.name == 'hho':
        #suitInterval = ActorInterval(suit, 'headhoncho-cigar-smoke')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'cigar-smoke'), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, headLoop)
    else:
        return stunInterval

def createSuitFirestarterCigarSmokeInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral')
    hasAnimatedHead = False
    if suit.style.name == 'fires':
        suitInterval = ActorInterval(suit, 'cigar-smoke')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'cigar-smoke'), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval)
    elif suit.style.name == 'safesupervis':
        suitInterval = ActorInterval(suit, 'cigar-smoke')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'cigar-smoke'), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval)
    else:
        return stunInterval

def createSuitFirestarterCigarSmokeInterval2(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    stunInterval = Func(suit.loop, 'neutral')
    hasAnimatedHead = False
    if suit.style.name == 'safesupervis':
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'cigar-smoke', startTime=2), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval)
    else:
        return stunInterval

def createSuitStunInterval(suit, before, after):
    hasAnimatedHead = False
    updateTrack = Parallel(Func(suit.setNeutralAnimationHead))
    if suit.style.name == 'hroller2':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
            hasAnimatedHead = True
    if suit.style.name == 'hrollers':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
            hasAnimatedHead = True
    if suit.style.name == 'hroller':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
            hasAnimatedHead = True
    else:
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'stun')
            hasAnimatedHead = True
    if hasAnimatedHead:
        return Sequence(Wait(before), Func(suit.setDizzy2, 1), headInterval, Wait(after),
                            Func(suit.setDizzy2, 0), updateTrack)
    else:
        return Sequence(Wait(before), Func(suit.setDizzy2, 1), Wait(after), Func(suit.setDizzy2, 0))


def createSuitStunIntervalFired(suit, before, after):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    stars.setPosHprScale(0, 0, .75, 0, 0, 0, 1, 1, 1)
    stars.setBlend(frameBlend=base.wantSmoothAnims)
    head = suit.find('**/to_head')
    head.calcTightBounds(p1, p2)
    hasAnimatedHead = False
    makeFiredInterval = Func(suit.makeFired)
    for headPart in suit.animatedHeadParts:
        headInterval = Func(headPart.loop, 'stun')
        headLoop = Func(headPart.loop,
                            'neutral-hurt')
        hasAnimatedHead = True
    if hasAnimatedHead:
        return Sequence(Wait(before), makeFiredInterval, Func(stars.reparentTo, head),
                        Func(stars.loop, 'stun'), headInterval, Wait(after), headLoop, Func(stars.cleanup),
                        Func(stars.removeNode))
    else:
        return Sequence(Wait(before), makeFiredInterval, Func(stars.reparentTo, head),
                        Func(stars.loop, 'stun'), Wait(after), Func(stars.cleanup),
                        Func(stars.removeNode))

def createSuitLureInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        headLoopLure = Func(headPart.loop, 'neutral-lured')
        headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
        hasAnimatedHead = True
    if hasAnimatedHead:
        return Parallel(Func(stars.reparentTo, head), Func(stars.setZ, max(0.0, p2[2] - 1.0)),
                        Func(stars.loop, 'stun'), headLoopLure)
    else:
        return Parallel(Func(stars.reparentTo, head), Func(stars.setZ, max(0.0, p2[2] - 1.0)),
                        Func(stars.loop, 'stun'))


def createLureStunInterval(suit):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    return Sequence(Func(stars.reparentTo, head), Func(stars.setZ, max(0.0, p2[2] - 1.0)), Func(stars.loop, 'stun'), Func(stars.cleanup), Func(stars.removeNode))

def createDesperation(suit):
    suitTrack = Func(suit.showHpTextRed, 'Desperation!')
    return Parallel(suitTrack)

def zapCog(suit, anim, before, after, battle):
    zapSuit = suit
    zapSuit.setBlend(frameBlend = base.wantSmoothAnims)
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    p1 = Point3(0)
    p2 = Point3(0)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    headLoop = head.hprInterval(0.5, Vec3(0, 0, 0))
    headNormal = head.hprInterval(0, Vec3(0, 0, 0))
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit.find('**/body'), suit.find('**/hands')]
    zapTrack = Sequence(Wait(before), SoundInterval(zapSfx, volume=0.6))
    flashTrack = Sequence()
    for bodyPart in suitBody:
        if bodyPart:
            flashTrack.append(Sequence(Wait(before), Func(bodyPart.setColorScale, (0, 0, 0, 1)),
                                  Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
                                  Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
                                  Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
                                  Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
                                  Func(bodyPart.setColorScale, (1, 1, 1, 1))))
    spazzTrack = Sequence(ActorInterval(suit, anim, startTime=0, endTime=0.8), ActorInterval(zapSuit, anim, startTime=0))
    return Parallel(zapTrack, flashTrack, spazzTrack)

def spawnHeadExplosion(suit, battle):
    headParts = suit.getHeadParts()
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    suitTrack.append(Wait(0.15))
    explodeTrack = Parallel()
    for part in headParts:
        explodeTrack.append(Func(part.detachNode))
    suitTrack.append(explodeTrack)
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    deathSoundTrack = Sequence(SoundInterval(deathSound, volume=0.8))
    BattleParticles.loadParticles()
    gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height + 1)
    smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
    smallGears.setPos(gearPoint)
    smallGears.setDepthWrite(False)
    gears1Track = Sequence(Wait(0.5),ParticleInterval(smallGears, battle, worldRelative=False, duration=1.0, cleanup=True),name='gears1Track')
    explosionTrack = Sequence()
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    bigGearExplosion, singleGear, smallGearExplosion = getExplosionGears(gearPoint)
    gears2MTrack = createShortExplosionInterval(battle, bigGearExplosion, singleGear, smallGearExplosion)

    return Parallel(suitTrack, explosionTrack, deathSoundTrack, gears1Track, gears2MTrack)

def removeTrainTrack(suit, battle, suitTrack):
    if hasattr(suit, 'battleTrapProp') and suit.battleTrapProp and suit.battleTrapProp.getName() == 'traintrack' and not suit.battleTrapProp.isHidden():
        suitTrack.append(createTrainTrackAppearTrack(suit, None, battle, None))

def getExplosionGears(gearPoint):
    singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
    singleGear.setPos(gearPoint)
    singleGear.setDepthWrite(False)
    smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
    smallGearExplosion.setPos(gearPoint)
    smallGearExplosion.setDepthWrite(False)
    bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
    bigGearExplosion.setPos(gearPoint)
    bigGearExplosion.setDepthWrite(False)
    return bigGearExplosion, singleGear, smallGearExplosion

def createShortExplosionInterval(battle, bigGearExplosion, singleGear, smallGearExplosion):
    gears2MTrack = Track(
        (0.1, ParticleInterval(singleGear, battle, worldRelative=False, duration=0.4, cleanup=True)),
        (0.5, ParticleInterval(smallGearExplosion, battle, worldRelative=False, duration=0.5, cleanup=True)),
        (0.9, ParticleInterval(bigGearExplosion, battle, worldRelative=False, duration=2.0, cleanup=True)),
        name='gears2MTrack'
    )
    return gears2MTrack


def calcAvgSuitPos(throw):
    battle = throw['battle']
    avgSuitPos = Point3(0, 0, 0)
    numTargets = len(throw['target'])
    for i in xrange(numTargets):
        suit = throw['target'][i]['suit']
        avgSuitPos += suit.getPos(battle)

    avgSuitPos /= numTargets
    return avgSuitPos

def calcAvgToonPos(attack):
    battle = attack['battle']
    avgToonPos = Point3(0, 0, 0)
    numTargets = len(attack['target'])
    for i in xrange(numTargets):
        toon = attack['target'][i]['toon']
        avgToonPos += toon.getPos(battle)

    avgToonPos /= numTargets
    return avgToonPos

def sortAttacks(attacksDict):
    attacks = attacksDict.values()

    def compFunc(a, b):
        if len(a) > len(b):
            return 1
        elif len(a) < len(b):
            return -1
        return 0

    attacks.sort(compFunc)
    return attacks