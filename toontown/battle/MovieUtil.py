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
SUIT_LURE_DISTANCE = 3.6
SUIT_LURE_DOLLAR_DISTANCE = 5.1
SUIT_EXTRA_REACH_DISTANCE = 0.9
SUIT_EXTRA_RAKE_DISTANCE = 1.1
SUIT_TRAP_DISTANCE = 3.6
SUIT_TRAP_RAKE_DISTANCE = 4.5
SUIT_TRAP_MARBLES_DISTANCE = 3.7
SUIT_TRAP_TNT_DISTANCE = 5.1
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
    if suit.style.name == 'auh':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    elif suit.style.name == 'th':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    elif suit.style.name == 'tlr':
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
    suitTrack.append(Func(suit.show))
    suitTrack.append(ActorInterval(suit, 'landing', startTime=1.25))
    suitTrack.append(Sequence(Func(suit.showHpText2,
                                   '0.5x HP MULTIPLIER',
                                   2), Func(suit.showHpStringLureManager2,
                                            '1.5x Dmg Multiplier'), Func(suit.showHpString,
                                                                         '-1 Skeletal Revive')))
    suitTrack.append(Func(suit.loop, 'neutral-unstable'))
    suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() / 2)))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.makeRevive))
    if suit.style.name == 'csm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'ste' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'dty' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
    elif suit.style.name == 'dty' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'ste' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'scg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
    elif suit.style.name == 'lit' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'fm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'kc' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'ghd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'dvp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'tcm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'otm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'dsk':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'tg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'jg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'mes' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'mad' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'adc' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'drm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'dm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
    elif suit.style.name == 'ggm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
    elif suit.style.name == 'crf' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'th' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'th' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'tb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'ts' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'prr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'sft' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'fbd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'cp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dola_death.ogg')
    elif suit.style.name == 'frs' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'frs' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'dsf' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'gtk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'bsh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'ffm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'mes' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'kb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'kb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'cry' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'msr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
    elif suit.style.name == 'tlr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
    elif suit.style.name == 'tlr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'fd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'nar' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'dsk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'dsk' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'blr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'ghd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'tyh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'tyh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'yuh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'wrt' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'dar' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'gh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'gh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'ssm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'ssm' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'trk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'rb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'rb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cvy' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cvy' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cm' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'jdg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'jgd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'bby' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'auh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'nhy' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'phs' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'phs' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'blr':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'cfp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cfp' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'le' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'le' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'gry' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'gry' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'hh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'hh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'bdb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'bdb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
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
    suitTrack.append(Func(suit.setMaxHP, 4880))
    suitTrack.append(Func(suit.setHP, 1500))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.makeRevive))
    suitTrack.append(ActorInterval(suit, 'pie-small-react'))
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
                                           '1.5x Dmg Multiplier'), Func(suit.showHpString,
                                           '-1 Virtual Revive')))
    suitTrack.append(Func(suit.loop, 'neutral-unstable'))
    suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() / 2)))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.makeDamageUp))
    suitTrack.append(Func(suit.makeLaserRevive))
    if suit.style.name == 'csm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'ste' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'ste' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'scg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
    elif suit.style.name == 'lit' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'fm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'kc' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'ghd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'bdb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'bdb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'dvp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'tcm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'otm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'dsk':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'tg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'dty' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
    elif suit.style.name == 'dty' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'gry' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'gry' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'jg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'mes' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'mad' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'adc' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'drm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'dm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
    elif suit.style.name == 'ggm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
    elif suit.style.name == 'crf' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'th' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'cr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'dsk' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'blr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'th' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'tb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'ts' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'prr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'sft' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'fbd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'frs' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'frs' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'dsf' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'gtk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'cp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dola_death.ogg')
    elif suit.style.name == 'bsh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'ffm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'mes' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'kb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'kb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'cry' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'msr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
    elif suit.style.name == 'tlr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
    elif suit.style.name == 'tlr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'fd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'nar' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'dsk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'ghd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'tyh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'tyh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'yuh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'wrt' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'dar' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'gh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'gh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'ssm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'ssm' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'trk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'rb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'rb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cvy' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cvy' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cm' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'jdg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'jgd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'bby' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'auh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'nhy' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'phs' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'phs' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'blr':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'cfp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cfp' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'le' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'le' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'hh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'hh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
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

def createVirtualSuitDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    deathSuit = suit
    headInterval = Parallel()
    for headPart in suit.animatedHeadParts:
        headInterval.append(Func(headPart.play, 'death'))
    suitTrack.append(Func(notify.debug, 'before insertDeathSuit'))
    suitTrack.append(Func(insertDeathSuit, suit, deathSuit, battle, suitPos, suitHpr))
    suitTrack.append(Parallel(ActorInterval(suit, 'lose', duration=2), headInterval))
    deathSound = base.loadSfx('phase_11/audio/sfx/LB_laser_beam_off_death.ogg')
    suitTrack.append(Parallel(ActorInterval(suit, 'slip-forward', duration=2),
        Func(suit.nametag3d.hide),
        SoundInterval(deathSound, volume=0.5),
        LerpScaleInterval(deathSuit, 0.3, 0.0001,)))
    suitTrack.append(Func(notify.debug, 'before removeDeathSuit'))
    suitTrack.append(Func(removeDeathSuit, suit, deathSuit, name='remove-death-suit'))
    suitTrack.append(Func(notify.debug, 'after removeDeathSuit'))
    suitTrack.append(Func(suit.makeDead))
    if suit.style.name == 'csm':
        for s in battle.activeSuits:
            if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'scg':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'lit':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'scg' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ste':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ffm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvp':
        for s in battle.activeSuits:
            if s.dna.name == 'ffm' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsk':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'blr':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'crf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'crf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'prr':
        for s in battle.activeSuits:
            if s.dna.name == 'crf' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tb':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'crf':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'gtk':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'frs':
        for s in battle.activeSuits:
            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'fbd':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cp':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tcm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cry':
        for s in battle.activeSuits:
            if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvk':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'otm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                suitTrack.append(createDesperationTrack(s))
    return suitTrack


def createSuitDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    if suit.style.name == 'dvp':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    elif suit.style.name == 'auh':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    elif suit.style.name == 'tlr':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    elif suit.style.name == 'th':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'murmur')
            hasAnimatedHead = True
    else:
        for headPart in suit.animatedHeadParts:
            headInterval = ActorInterval(headPart, 'death')
            hasAnimatedHead = True
    suitTrack.append(Func(notify.debug, 'before insertDeathSuit'))
    suitTrack.append(Func(insertDeathSuit, suit, deathSuit, battle, suitPos, suitHpr))
    suitTrack.append(Func(notify.debug, 'before actorInterval lose'))
    suitTrack.append(ActorInterval(deathSuit, 'lose'))
    suitTrack.append(Func(notify.debug, 'before removeDeathSuit'))
    suitTrack.append(Func(removeDeathSuit, suit, deathSuit, name='remove-death-suit'))
    suitTrack.append(Func(notify.debug, 'after removeDeathSuit'))
    suitTrack.append(Func(suit.makeDead))
    if suit.style.name == 'csm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'ste' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'ste' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'scg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
    elif suit.style.name == 'lit' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'fm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'kc' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'ghd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'dvp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'gry' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'gry' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'tcm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'otm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'dsk':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'tg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'jg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'mes' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'mad' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'adc' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'drm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'dm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
    elif suit.style.name == 'ggm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
    elif suit.style.name == 'crf' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'th' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'th' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'dsk' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'blr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'bdb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'bdb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'tb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'ts' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'prr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'dty' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
    elif suit.style.name == 'dty' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'sft' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'fbd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'cr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dola_death.ogg')
    elif suit.style.name == 'frs' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'frs' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'dsf' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'gtk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'bsh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'ffm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'mes' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'kb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'kb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'cry' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'msr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
    elif suit.style.name == 'tlr' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
    elif suit.style.name == 'tlr' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'fd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'nar' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'dsk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'ghd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'tyh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'tyh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'yuh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'wrt' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'dar' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'gh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'gh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'ssm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'ssm' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'trk' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'rb' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'rb' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cvy' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cvy' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cm' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'cm' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'jdg' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'jgd' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'bby' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'auh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'nhy' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'phs' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'phs' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'blr':
        spinningSound = base.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'cfp' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'cfp' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'le' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'le' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.style.name == 'hh' and not deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.style.name == 'hh' and deathSuit.isSkeleton:
        spinningSound = base.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
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
    if suit.style.name == 'csm':
        for s in battle.activeSuits:
            if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'scg':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'lit':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'scg' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ste':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ffm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvp':
        for s in battle.activeSuits:
            if s.dna.name == 'ffm' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsk':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'blr':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'crf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'crf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'prr':
        for s in battle.activeSuits:
            if s.dna.name == 'crf' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tb':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'crf':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'gtk':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'frs':
        for s in battle.activeSuits:
            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'fbd':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cp':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tcm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cry':
        for s in battle.activeSuits:
            if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvk':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'otm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                suitTrack.append(createDesperationTrack(s))

    returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    if hasAnimatedHead:
        returnval.append(headInterval)
    return returnval

def createSuitHeadlessDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitTrack.append(Func(notify.debug, 'before insertDeathSuit'))
    suitTrack.append(Func(insertDeathSuit, suit, deathSuit, battle, suitPos, suitHpr))
    suitTrack.append(Func(notify.debug, 'before actorInterval lose'))
    suitTrack.append(ActorInterval(deathSuit, 'lose2', duration=3.0))
    suitTrack.append(Func(notify.debug, 'before removeDeathSuit'))
    suitTrack.append(Func(removeDeathSuit, suit, deathSuit, name='remove-death-suit'))
    suitTrack.append(Func(notify.debug, 'after removeDeathSuit'))
    deathSound = base.loadSfx('phase_5/audio/sfx/COG_headless_death.ogg')
    deathSoundTrack = Sequence(Wait(0), SoundInterval(deathSound, volume=0.6))
    if suit.style.name == 'csm':
        for s in battle.activeSuits:
            if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'scg':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'lit':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'scg' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ste':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ffm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvp':
        for s in battle.activeSuits:
            if s.dna.name == 'ffm' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsk':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'blr':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'crf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'crf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'prr':
        for s in battle.activeSuits:
            if s.dna.name == 'crf' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tb':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'crf':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'gtk':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'frs':
        for s in battle.activeSuits:
            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'fbd':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cp':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tcm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cry':
        for s in battle.activeSuits:
            if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvk':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'otm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                suitTrack.append(createDesperationTrack(s))

    returnval = Parallel(suitTrack, deathSoundTrack)
    return returnval

def createSuitWreckingDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitTrack.append(Func(notify.debug, 'before insertDeathSuit'))
    suitTrack.append(Func(insertDeathSuit, suit, deathSuit, battle, suitPos, suitHpr))
    suitTrack.append(Func(notify.debug, 'before actorInterval lose'))
    suitTrack.append(ActorInterval(deathSuit, 'lose3', duration=4.0))
    suitTrack.append(Func(notify.debug, 'before removeDeathSuit'))
    suitTrack.append(Func(removeDeathSuit, suit, deathSuit, name='remove-death-suit'))
    suitTrack.append(Func(notify.debug, 'after removeDeathSuit'))
    deathSound = base.loadSfx('phase_5/audio/sfx/AA_trap_wreckingball_%s.ogg' % random.randint(1, 3))
    deathSoundTrack = Sequence(Wait(0), SoundInterval(deathSound, volume=0.6))
    if suit.style.name == 'csm':
        for s in battle.activeSuits:
            if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'scg':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'lit':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'scg' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ste':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ffm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvp':
        for s in battle.activeSuits:
            if s.dna.name == 'ffm' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsk':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'blr':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'crf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'crf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'prr':
        for s in battle.activeSuits:
            if s.dna.name == 'crf' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tb':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'crf':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'gtk':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'frs':
        for s in battle.activeSuits:
            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'fbd':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cp':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tcm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cry':
        for s in battle.activeSuits:
            if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvk':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'otm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                suitTrack.append(createDesperationTrack(s))
    returnval = Parallel(suitTrack, deathSoundTrack)
    return returnval

def createSuitCrashTrack(suit, battle):
    suitScale = suit.getScale()
    node = suit.getGeomNode().getChild(0)
    suitPos = suit.getPos()
    hitTime = 0.1
    shrinkStartDelay = 2.0
    #crashSoundEffects = []
    #for sound in crashSounds:
        #crashSoundEffects.append(globalBattleSoundCache.getSound(sound))
    soundTrack = base.loadSfx('phase_5/audio/sfx/drop_react.ogg')
    deathSoundTrack = Sequence(Wait(0), SoundInterval(soundTrack, volume=1.0))
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        headInterval = ActorInterval(headPart, 'neutral', startTime=0, endTime=0)
        hasAnimatedHead = True
    suitTrack = Sequence(Wait(hitTime),
                         Func(node.setScale, Point3(suitScale[0], suitScale[1], suitScale[2] * 0.0001)),
                         Func(node.setColorScale, Vec4(0.0, 0.0, 0.0, 1)),
                         Func(suit.deleteDropShadow),
                         Wait(shrinkStartDelay),
                         LerpScaleInterval(suit, 0.8, Point3(0.0001, 0.0001, 0.0001), blendType='easeIn'),
                         Func(suit.hide))
    if suit.style.name == 'csm':
        for s in battle.activeSuits:
            if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'scg':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'lit':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'scg' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ste':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ffm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvp':
        for s in battle.activeSuits:
            if s.dna.name == 'ffm' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsk':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'blr':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'crf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'crf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'prr':
        for s in battle.activeSuits:
            if s.dna.name == 'crf' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tb':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'crf':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'gtk':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'frs':
        for s in battle.activeSuits:
            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'fbd':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cp':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tcm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cry':
        for s in battle.activeSuits:
            if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvk':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'otm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                suitTrack.append(createDesperationTrack(s))
    if hasAnimatedHead:
        return Parallel(suitTrack, deathSoundTrack, headInterval)
    else:
        return Parallel(suitTrack, deathSoundTrack)

def midairSuitExplodeTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    suitPos.setZ(suitPos.getZ() + 17)
    suitTrack.append(Wait(0.15))
    suitTrack.append(Func(avatarHide, suit))
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
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    gears1Track = Sequence(Wait(0.5), ParticleInterval(smallGears, battle, worldRelative=0, duration=1.0, cleanup=True), name='gears1Track')
    gears2MTrack = Track(
        (0.1, ParticleInterval(singleGear, battle, worldRelative=0, duration=0.4, cleanup=True)),
        (0.5, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=0.5, cleanup=True)),
        (0.9, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=2.0, cleanup=True)), name='gears2MTrack'
    )
    if suit.style.name == 'csm':
        for s in battle.activeSuits:
            if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'scg':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'lit':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'scg' or s.dna.name == 'ste':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ste':
        for s in battle.activeSuits:
            if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'ffm':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvp':
        for s in battle.activeSuits:
            if s.dna.name == 'ffm' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsk':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'blr':
        for s in battle.activeSuits:
            if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'crf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dsf':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'crf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'prr':
        for s in battle.activeSuits:
            if s.dna.name == 'crf' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tb':
        for s in battle.activeSuits:
            if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'crf':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'gtk':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'frs':
        for s in battle.activeSuits:
            if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'fbd':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cp':
        for s in battle.activeSuits:
            if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'tcm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'cry':
        for s in battle.activeSuits:
            if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'dvk':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                suitTrack.append(createDesperationTrack(s))
    elif suit.style.name == 'otm':
        for s in battle.activeSuits:
            if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                suitTrack.append(createDesperationTrack(s))

    return Parallel(suitTrack, explosionTrack, deathSoundTrack, gears1Track, gears2MTrack, Wait(4.5))

def createDesperationTrack(suit):
    theSuit = suit
    makeDesperate = Func(suit.makeDesperation)
    makeDamageUp = Func(suit.makeDamageUp)
    notifyTrack = Sequence(Wait(2.0), Func(theSuit.showHpText2,
                                           'DESPERATION!',
                                           2), Func(theSuit.showHpStringLureManager2,
                                           '1.4x Dmg Multiplier'), Func(theSuit.showHpString,
                                           '+1 Round Lure Resistance'))
    cameraTrack = Sequence(
        LerpPosHprInterval(camera, duration=1.5, pos=Point3(0, -10, 5), hpr=Point3(0, 0, 0),
                           blendType='easeInOut'))
    talkTrack = Sequence(Wait(2.0), Func(theSuit.setChatAbsolute,
                              "Hmmm.",
                              CFSpeech | CFTimeout), Wait(4.0),
                         Func(theSuit.setChatAbsolute,
                              "Let's make this a little more interesting.",
                              CFSpeech | CFTimeout),
                         Wait(2.0))

    return Sequence(notifyTrack, cameraTrack, makeDamageUp, makeDesperate, talkTrack)

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
        if suit.style.name == 'csm':
            for s in battle.activeSuits:
                if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'ste':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'scg':
            for s in battle.activeSuits:
                if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'ste':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'lit':
            for s in battle.activeSuits:
                if s.dna.name == 'csm' or s.dna.name == 'scg' or s.dna.name == 'ste':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'ste':
            for s in battle.activeSuits:
                if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'ffm':
            for s in battle.activeSuits:
                if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'dvp':
            for s in battle.activeSuits:
                if s.dna.name == 'ffm' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'dsk':
            for s in battle.activeSuits:
                if s.dna.name == 'dvp' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'blr':
            for s in battle.activeSuits:
                if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'crf':
            for s in battle.activeSuits:
                if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'dsf':
            for s in battle.activeSuits:
                if s.dna.name == 'prr' or s.dna.name == 'crf' or s.dna.name == 'tb':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'prr':
            for s in battle.activeSuits:
                if s.dna.name == 'crf' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'tb':
            for s in battle.activeSuits:
                if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'crf':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'gtk':
            for s in battle.activeSuits:
                if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'frs':
            for s in battle.activeSuits:
                if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'fbd':
            for s in battle.activeSuits:
                if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'cp':
            for s in battle.activeSuits:
                if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'tcm':
            for s in battle.activeSuits:
                if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'cry':
            for s in battle.activeSuits:
                if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'dvk':
            for s in battle.activeSuits:
                if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'otm':
            for s in battle.activeSuits:
                if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                    suitTrack.append(createDesperationTrack(s))

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
        suitTrack = Sequence()
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        suitTrack.append(LerpColorScaleInterval(suit, 0.8, (0, 0, 0, 0)))
        suitTrack.append(Func(avatarHide, suit))
        BattleParticles.loadParticles()
        explodePosPoints = [Point3(0, 0, 0), PNT3_ZERO]
        splatName = 'dust2'
        explode = globalPropPool.getProp('dust2')
        explode.setTwoSided(True)
        explode.setBillboardPointWorld(2)
        explodeTrack = Sequence()
        explodeTrack.append(
        getPropAppearTrack(explode, suit, explodePosPoints, 0, Point3(2, 2, 2), scaleUpTime=0))
        explodeTrack.append(Sequence(ActorInterval(explode, splatName), Func(explode.detachNode)))
        if suit.style.name == 'csm':
            for s in battle.activeSuits:
                if s.dna.name == 'scg' or s.dna.name == 'lit' or s.dna.name == 'ste':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'scg':
            for s in battle.activeSuits:
                if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'ste':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'lit':
            for s in battle.activeSuits:
                if s.dna.name == 'csm' or s.dna.name == 'scg' or s.dna.name == 'ste':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'ste':
            for s in battle.activeSuits:
                if s.dna.name == 'csm' or s.dna.name == 'lit' or s.dna.name == 'scg':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'ffm':
            for s in battle.activeSuits:
                if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'dvp':
            for s in battle.activeSuits:
                if s.dna.name == 'ffm' or s.dna.name == 'dsk' or s.dna.name == 'blr':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'dsk':
            for s in battle.activeSuits:
                if s.dna.name == 'dvp' or s.dna.name == 'ffm' or s.dna.name == 'blr':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'blr':
            for s in battle.activeSuits:
                if s.dna.name == 'dvp' or s.dna.name == 'dsk' or s.dna.name == 'ffm':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'crf':
            for s in battle.activeSuits:
                if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'dsf':
            for s in battle.activeSuits:
                if s.dna.name == 'prr' or s.dna.name == 'crf' or s.dna.name == 'tb':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'prr':
            for s in battle.activeSuits:
                if s.dna.name == 'crf' or s.dna.name == 'dsf' or s.dna.name == 'tb':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'tb':
            for s in battle.activeSuits:
                if s.dna.name == 'prr' or s.dna.name == 'dsf' or s.dna.name == 'crf':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'gtk':
            for s in battle.activeSuits:
                if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'frs':
            for s in battle.activeSuits:
                if s.dna.name == 'gtk' or s.dna.name == 'fbd' or s.dna.name == 'cp':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'fbd':
            for s in battle.activeSuits:
                if s.dna.name == 'frs' or s.dna.name == 'gtk' or s.dna.name == 'cp':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'cp':
            for s in battle.activeSuits:
                if s.dna.name == 'frs' or s.dna.name == 'fbd' or s.dna.name == 'gtk':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'tcm':
            for s in battle.activeSuits:
                if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'cry':
            for s in battle.activeSuits:
                if s.dna.name == 'tcm' or s.dna.name == 'dvk' or s.dna.name == 'otm':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'dvk':
            for s in battle.activeSuits:
                if s.dna.name == 'cry' or s.dna.name == 'tcm' or s.dna.name == 'otm':
                    suitTrack.append(createDesperationTrack(s))
        elif suit.style.name == 'otm':
            for s in battle.activeSuits:
                if s.dna.name == 'cry' or s.dna.name == 'dvk' or s.dna.name == 'tcm':
                    suitTrack.append(createDesperationTrack(s))

        return Parallel(suitTrack, explodeTrack)


def createSuitDodgeMultitrack(tDodge, suit, leftSuits, rightSuits):
    suitTracks = Parallel()
    soundTrack = base.loadSfx('phase_5/audio/sfx/ENC_cogjump_to_side.ogg')
    suitDodgeList, sidestepAnim = avatarDodge(leftSuits, rightSuits, 'sidestep-left', 'sidestep-right')
    for s in suitDodgeList:
        suitTracks.append(Sequence(ActorInterval(s, sidestepAnim),  Func(suit.setNeutralAnimation)))

    suitTracks.append(Sequence(ActorInterval(suit, sidestepAnim), Func(suit.setNeutralAnimation)))
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
    if suit.dna.name == 'scg' and suit.isAngry:
        suitTrack = Sequence(Wait(delay - 1), ActorInterval(suit, 'neutral-enraged-return'), ActorInterval(suit, 'gag-miss'))
    elif suit.isImmortal and not suit.dna.name == 'dsf':
        suitTrack = Sequence(Wait(delay - 1), ActorInterval(suit, 'highroller-neutral-levitate-in-out', startTime=1, endTime=0, duration=1), ActorInterval(suit, 'gag-miss'))
    else:
        suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'))
    if suit.isLured:
        suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'), Func(suit.loop, 'lured'))
    elif suit.dna.name == 'scg' and suit.isAngry:
        suitTrack.append(ActorInterval(suit, 'neutral-enraged-return', startTime=1, endTime=0))
        suitTrack.append(Func(suit.loop, 'neutral-enraged'))
    elif suit.dna.name == 'crf' and suit.isVulnerable:
        suitTrack.append(Func(suit.loop, 'neutral2%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
    elif suit.isImmortal and not suit.dna.name == 'dsf':
        suitTrack.append(Sequence(ActorInterval(suit, 'highroller-neutral-levitate-in-out', duration=1),
                                  Func(suit.loop, 'highroller-neutral-levitate-loop')))
    else:
        suitTrack.append(Func(suit.setNeutralAnimation))
    missedTrack = Sequence(Wait(delay + 0.2), Func(indicateMissed, suit, 0.9))
    return Parallel(suitTrack, missedTrack)

def createSuitTeaseMultiTrackDrop(suit, battle, delay = 0.01):
    suitTrack = Sequence(Wait(delay), Func(suit.play, 'gag-miss'), Wait(2.5), Func(suit.setNeutralAnimation))
    missedTrack = Sequence(Wait(delay + 0.2), Func(indicateMissed, suit, 0.9))
    return Parallel(suitTrack, missedTrack)


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
                           Func(showProps, buttons, hands),
                           LerpScaleInterval(button, 1.0, button.getScale(), startScale=Point3(0.01, 0.01, 0.01)),
                           Wait(2.5),
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
                           LerpScaleInterval(button, 1.0, button.getScale(), startScale=Point3(0.01, 0.01, 0.01)),
                           Wait(2.5),
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
    suitName = suit.getStyleName()
    if suitName == 'gh':
        return 1.4
    elif suitName == 'f':
        return 1.0
    elif suitName == 'cc':
        return 0.7
    elif suitName == 'tw':
        return 1.3
    elif suitName == 'bf':
        return 1.0
    elif suitName == 'sc':
        return 0.8
    elif suitName == 'ym':
        return 0.1
    elif suitName == 'mm':
        return 0.05
    elif suitName == 'tm':
        return 0.07
    elif suitName == 'nd':
        return 0.07
    elif suitName == 'pp':
        return 0.04
    elif suitName == 'bc':
        return 0.36
    elif suitName == 'b':
        return 0.41
    elif suitName == 'dt':
        return 0.31
    elif suitName == 'ac':
        return 0.39
    elif suitName == 'ds':
        return 0.41
    elif suitName == 'hh':
        return 0.8
    elif suitName == 'cr':
        return 2.1
    elif suitName == 'tbc':
        return 1.4
    elif suitName == 'hho':
        return 1.4
    elif suitName == 'bs':
        return 0.4
    elif suitName == 'sd':
        return 1.02
    elif suitName == 'le':
        return 1.3
    elif suitName == 'bw':
        return 1.4
    elif suitName == 'br':
        return 1.4
    elif suitName == 'nc':
        return 0.6
    elif suitName == 'mb':
        return 1.85
    elif suitName == 'ls':
        return 1.4
    elif suitName == 'rb':
        return 1.6
    elif suitName == 'bfh':
        return 1.85
    elif suitName == 'ms':
        return 0.7
    elif suitName == 'tf':
        return 0.75
    elif suitName == 'm':
        return 0.9
    elif suitName == 'mh':
        return 1.3
    elif suitName == 'txm':
        return 1.4
    else:
        notify.warning('getSuitRakeOffset(suit) - Unknown suit name: %s' % suitName)
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
        return Sequence(Wait(before), headInterval, headLoop, headLoop2)
    elif hasAnimatedHead:
        return Sequence(Wait(before), headInterval2, headLoop, headLoop2)
    else:
        return Sequence(Wait(before), headInterval, headLoop, headLoop2)

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
                            'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''), fromFrame=0, toFrame=22))
        headLoop = ActorInterval(suit, 'wheelspin', startTime=2.5)
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
                            'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''), fromFrame=0, toFrame=22))
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
    if suit.style.name == 'csm':
        suitInterval = ActorInterval(suit, 'throw-insurance')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'insurance'), Func(headPart.loop,
                        'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
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
    if suit.style.name == 'dsk':
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
    if suit.style.name == 'lit':
        suitInterval = ActorInterval(suit, 'bellow')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'bellow'), Func(headPart.loop,
                        'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    elif suit.style.name == 'cm':
        suitInterval = ActorInterval(suit, 'bellow')
        for headPart in suit.animatedHeadParts:
            headInterval = ActorInterval(headPart, 'bellow')
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    elif suit.style.name == 'tcm':
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
    if suit.style.name == 'lit':
        suitInterval = ActorInterval(suit, 'snap2')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'gsnap'), Func(headPart.loop,
                        'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
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
    if suit.style.name == 'tld':
        suitInterval = ActorInterval(suit, 'headhoncho-cigar-smoke')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'cigar-smoke'), Func(headPart.loop,
                        'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
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
    if suit.style.name == 'tc':
        suitInterval = ActorInterval(suit, 'firestarter-cigar-smoke')
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'cigar-smoke'), Func(headPart.loop,
                        'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else '')))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval)
    else:
        return stunInterval

def createSuitStunInterval(suit, before, after):
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
    updateTrack = Parallel(Func(suit.setChatAbsolute,
                                   '',
                                   CFSpeech | CFTimeout))
    if suit.style.name == 'crf':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
            if suit.isLured:
                headLoop = Func(headPart.loop,
                            'neutral-lured', fromFrame=0, toFrame=22)
            else:
                headLoop = Func(headPart.loop,
                                'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''),
                                fromFrame=0, toFrame=22)
            hasAnimatedHead = True
    if suit.style.name == 'mad':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
            if suit.isLured:
                headLoop = Func(headPart.loop,
                                'neutral-lured', fromFrame=0, toFrame=22)
            else:
                headLoop = Func(headPart.loop,
                                'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''),
                                fromFrame=0, toFrame=22)
            hasAnimatedHead = True
    if suit.style.name == 'dsf':
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'stun', fromFrame=0, toFrame=22)
            if suit.isLured:
                headLoop = Func(headPart.loop,
                                'neutral-lured', fromFrame=0, toFrame=22)
            else:
                headLoop = Func(headPart.loop,
                                'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''),
                                fromFrame=0, toFrame=22)
            hasAnimatedHead = True
    else:
        for headPart in suit.animatedHeadParts:
            headInterval = Func(headPart.loop, 'stun')
            if suit.isLured:
                headLoop = Func(headPart.loop,
                                'neutral-lured', fromFrame=0, toFrame=22)
            else:
                headLoop = Func(headPart.loop,
                                'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''),
                                fromFrame=0, toFrame=22)
            hasAnimatedHead = True
    if hasAnimatedHead:
        return Sequence(Wait(before), Func(stars.reparentTo, head),
                            Func(stars.loop, 'stun'), headInterval, Wait(after), updateTrack,
                            Func(stars.cleanup),
                            Func(stars.removeNode))
    else:
        return Sequence(Wait(before), Func(stars.reparentTo, head),
                        Func(stars.loop, 'stun'), Wait(after), Func(stars.cleanup),
                        Func(stars.removeNode))


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
    suitPos = suit.getPos(battle)
    suitHpr = suit.getHpr(battle)
    zapSuit.setBin("fixed", 0)
    zapSuit.setDepthTest(True)
    zapSuit.setDepthWrite(True)
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    p1 = Point3(0)
    p2 = Point3(0)
    head = suit.getHeadParts()[0]
    head.calcTightBounds(p1, p2)
    headLoop = head.hprInterval(0.5, Vec3(0, 0, 0))
    headNormal = head.hprInterval(0, Vec3(0, 0, 0))
    zapTrack = Sequence(Wait(before), SoundInterval(zapSfx, volume=0.6))
    flashTrack = Sequence(Wait(before), Func(suit.setColorScale, (0,0,0,1)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(suit.setColorScale, (1,1,1,1)))
    spazzTrack = Sequence(ActorInterval(zapSuit, anim, startTime=0, endTime=0.8), ActorInterval(zapSuit, anim, startTime=0, endTime=0.8), Func(zapSuit.play, anim))
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
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
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