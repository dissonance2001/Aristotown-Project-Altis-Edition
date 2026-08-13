import random
from direct.interval.IntervalGlobal import *
from toontown.battle.BattleBase import *
from toontown.battle.BattleProps import *
from direct.directnotify import DirectNotifyGlobal
from direct.particles import ParticleEffect
from toontown.battle import BattleParticles
from toontown.battle import BattleProps
from toontown.battle.BattleSounds import *
from toontown.effects import DustCloud
from panda3d.core import *
from toontown.suit import SuitBase
from toontown.suit.SuitDNA import *
from toontown.chat.ChatGlobals import *
from toontown.suit import SuitTimings
from toontown.toonbase import ToontownGlobals
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
SUIT_TRAP_TNT_DISTANCE = 6.2
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

def cleanupAllBattleEffects(suit):
    suit.cleanupShockAura()
    # -------------------------
    # suit-owned intervals
    # -------------------------
    intervalAttrs = [
        'mtrack',
        'splashInterval',
        'headInterval',
        'shockAuraTrack',
        'neutralInterval',
        'deathInterval',
        'headInterval2',
        'healInterval',
        'absorbInterval',
        'damageInterval',
        'hpTextInterval',
        'hpTextInterval2',

        # custom suit effect intervals
        'knifeTrack',
        'cheerTrack2',
        'bombTrack',
        'flameTrack',
        'liquidTrack',
        'oilTrack',
        'cheerTrack',
    ]

    for attr in intervalAttrs:
        interval = getattr(suit, attr, None)
        if interval:
            try:
                interval.pause()
            except:
                pass
            try:
                interval.finish()
            except:
                pass
            setattr(suit, attr, None)

    # -------------------------
    # suit sound sequences
    # -------------------------
    soundSequenceList = getattr(suit, 'soundSequenceList', None)
    if soundSequenceList:
        for seq in soundSequenceList:
            try:
                seq.finish()
            except:
                pass
        suit.soundSequenceList = []

    # -------------------------
    # suit particle effects
    # -------------------------
    particleAttrs = [
        'cheerEffect2',
        'flameEffect',
        'liquidEffect',
        'oilEffect',
        'cheerEffect',
    ]
    if suit.dna.name == 'videog':
        suit.stopHeadFreakout()
    for attr in particleAttrs:
        effect = getattr(suit, attr, None)
        if effect:
            try:
                effect.disable()
            except:
                pass
            try:
                if hasattr(effect, 'renderParent'):
                    effect.cleanup()
            except:
                pass
            try:
                effect.detachNode()
            except:
                pass
            try:
                if not effect.isEmpty():
                    effect.removeNode()
            except:
                pass
            setattr(suit, attr, None)

    # -------------------------
    # suit nodepaths / pivots
    # -------------------------
    nodeAttrs = [
        'knifePivot',
        'bombPivot',
    ]

    for attr in nodeAttrs:
        node = getattr(suit, attr, None)
        if node:
            try:
                if not node.isEmpty():
                    node.removeNode()
            except:
                pass
            setattr(suit, attr, None)

    # -------------------------
    # suit prop lists
    # -------------------------
    listAttrs = [
        'bombProps',
    ]

    for attr in listAttrs:
        props = getattr(suit, attr, None)
        if props:
            for prop in props:
                if prop:
                    if hasattr(prop, 'sparksEffect') and prop.sparksEffect:
                        effect = prop.sparksEffect
                        prop.sparksEffect = None

                        try:
                            effect.disable()
                        except:
                            pass
                        try:
                            if hasattr(effect, 'renderParent'):
                                effect.cleanup()
                        except:
                            pass
                        try:
                            effect.detachNode()
                        except:
                            pass

                    try:
                        if not prop.isEmpty():
                            MovieUtil.removeProp(prop)
                    except:
                        pass

            setattr(suit, attr, [])

    # -------------------------
    # stock status props on suits
    # -------------------------
    for attr in ('stars', 'suedstars'):
        prop = getattr(suit, attr, None)
        if prop:
            try:
                prop.stop()
            except:
                pass
            try:
                prop.detachNode()
            except:
                pass


def removeDeathSuit(suit, deathSuit):
    notify.debug('removeDeathSuit()')

    if not deathSuit.isEmpty():
        deathSuit.detachNode()
        suit.cleanupLoseActor()

SUIT_INTERVAL_ATTRS = [
    'mtrack',
    'splashInterval',
    'headInterval',
    'neutralInterval',
    'deathInterval',
    'headInterval2',
    'healInterval',
    'absorbInterval',
    'playByPlayInterval',
    'damageInterval',
    'hpTextInterval',
    'hpTextInterval2',
    'knifeTrack',
    'cheerTrack2',
]

SUIT_PARTICLE_ATTRS = [
    'cheerEffect2',
]

SUIT_NODE_ATTRS = [
    'knifePivot',
]
		
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
    notify.debug('removeZapSuit()')

    if zapSuit is not None and not zapSuit.isEmpty():
        zapSuit.detachNode()

def removeZapSuitPowerhouse(suit, zapSuit):
    notify.debug('removeDeathSuit()')
    if not zapSuit.isEmpty():
        zapSuit.detachNode()
        suit.cleanupZapActorPowerhouse()

def removeZapSuitPowerhouseSquirt(suit, zapSuit):
    notify.debug('removeDeathSuit()')
    if not zapSuit.isEmpty():
        zapSuit.detachNode()
        suit.cleanupZapActorPowerhouseSquirt()

def removeZapSuitPowerhouseZap(suit, zapSuit):
    notify.debug('removeDeathSuit()')
    if not zapSuit.isEmpty():
        zapSuit.detachNode()
        suit.cleanupZapActorPowerhouseZap()


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

def makeErclaimDeath(suit, battle):
    suitTrack = Sequence()
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    batNode = render.attachNewNode('batNode')
    batNode.setPos(suit, 0, 0, 0)

    # Instance Count death
    BattleParticles.loadParticles()
    particleEffectLight = BattleParticles.createParticleEffect('Bats')
    partTrackLight = ParticleInterval(particleEffectLight, batNode, 0, duration=2, cleanup=True, softStopT=-1.0)
    particle = particleEffectLight.getParticlesNamed('particles-1')
    particle.setBirthRate(0.0500)
    particle.setLitterSize(1)

    particleEffectMedium = BattleParticles.createParticleEffect('Bats')
    partTrackMedium = ParticleInterval(particleEffectMedium, batNode, 0, duration=3, cleanup=True, softStopT=-1.0)
    particle = particleEffectMedium.getParticlesNamed('particles-1')
    particle.setBirthRate(0.0300)
    particle.setLitterSize(2)

    particleEffectHeavy = BattleParticles.createParticleEffect('Bats')
    partTrackHeavy = ParticleInterval(particleEffectHeavy, batNode, 0, duration=3, cleanup=True, softStopT=-1.0)
    particle = particleEffectHeavy.getParticlesNamed('particles-1')
    particle.setBirthRate(0.0200)
    particle.setLitterSize(6)

    deathSfx = loader.loadSfx('phase_13/audio/sfx/halloween/COUNT_defeat.ogg')

    def setSuitPartTransparency():
        actorNode = suit.find('**/__Actor_modelRoot')
        actorNode.setTransparency(1)

    partTrack = Track(
        (0.0, Func(base.playSfx, deathSfx)),
        (0.0, partTrackLight),
        (1.0, partTrackMedium),
        (3.0, partTrackHeavy),
        (4.0, Sequence(Func(setSuitPartTransparency), Func(suit.setChatAbsolute, "", CFSpeech),
                        LerpColorScaleInterval(suit, 1.0, (1, 1, 1, 0)))),
        (7.0, Func(batNode.removeNode))
    )

    # If Count has been assigned defeat dialog, use it. (This happens when his intro is made.)
    countDialog = random.choice(TTLocalizer.CountDefeatDialogDefaults)

    suitTrack = Track(
        (0.0, Func(suit.loop, 'neutral-hurt')),
        (0.5, Func(base.camera.setPosHpr, suit, 0, 22, 10, 180, -18, 0)),
        (1.0, Func(suit.setChatAbsolute, countDialog[0], CFSpeech)),
        (5.0, Func(suit.setChatAbsolute, countDialog[1], CFSpeech)),
        (9.0, Func(suit.setChatAbsolute, countDialog[2], CFSpeech)),
        (13.0, Func(suit.setChatAbsolute, countDialog[3], CFSpeech)),
        (13.0, partTrack)
    )
    return suitTrack

def createSuitReviveTrack(suit, battle):
    suitTrack = Sequence()
    if suit.style.name == 'erfit':
        return createErfitReviveTrack(suit, battle)
    if suit.style.name == 'erclaim':
        trapProp = globalPropPool.getProp('quicksand')
        trapProp.setColor(Vec4(0.1, 0.1, 1.0, 1))
        trapProp.setHpr(Point3(300, 0, 0))
        trapProp.setScale(0.01)
        trapProp.setPos(suit.getPos(render))
        trapProp.reparentTo(render)
        smallScale = 0.01
        bigScale = 2.25
        biggerScale = 2.5
        trapTrack = Sequence(
            Wait(0.65),
            LerpScaleInterval(trapProp, 0.65, biggerScale, blendType='easeIn'),
            LerpScaleInterval(trapProp, 0.15, bigScale, blendType='easeOut'),
            Wait(4.0),
            LerpScaleInterval(trapProp, 0.15, biggerScale, blendType='easeIn'),
            LerpScaleInterval(trapProp, 0.65, smallScale, blendType='easeOut'),
            Func(trapProp.removeNode)
        )

        def soakSuit():
            pass

        def suitNeutral():
            suit.setNeutralAnimation()

        def suitInbetweens():
            suit.hide()
            for headPart in suit.headParts:
                headPart.hide()
            suit.setSkelecog2(True)
            suit.setMaxHP(1922)
            suit.updateHealthBar(0)
            suit.setSuitStatusEffect('damageUp', modifier=25, mode='refreshModifier')
            suit.makeRevive()
            suit.makeUnDead()
            suit.wrtReparentTo(battle)
            suit.show()

        def createSuitMoveIval(suit, destPos, hole):
            dur = suit.getDuration('landing')
            fr = suit.getFrameRate('landing')
            landingDur = dur
            totalDur = 7.3
            animTimeInAir = totalDur - dur
            flyingDur = animTimeInAir
            moveIval = Sequence(
                Func(suit.pose, 'landing', 0),
                    Parallel(
                        Sequence(
                            ProjectileInterval(suit, duration=flyingDur, endPos=destPos, gravityMult=0.125),
                            ActorInterval(suit, 'landing')
                        ),
                        Sequence(
                            Wait(0.5),
                            Func(suit.showHpTextNew, 0, text="+25% Damage!", colorCode=1)
                        )
                    ),
                    Func(suitNeutral)
            )
            if suit.prop is None:
                suit.prop = globalPropPool.getProp('propeller')
            propDur = suit.prop.getDuration('propeller')
            lastSpinFrame = 8
            fr = suit.prop.getFrameRate('propeller')
            spinTime = lastSpinFrame / fr
            openTime = (lastSpinFrame + 1) / fr
            propTrack = Parallel(
                SoundInterval(suit.propInSound, duration=flyingDur, node=suit),
                Sequence(
                    ActorInterval(suit.prop, 'propeller', constrainedLoop=1, duration=flyingDur + 1, startTime=0.0, endTime=spinTime),
                    ActorInterval(suit.prop, 'propeller', duration=landingDur, startTime=openTime),
                    Func(suit.detachPropeller)
                )
            )
            hole.setPos(battle, destPos[0], destPos[1], destPos[2])
            underPos = destPos + Point3(0, 0, (-SuitTimings.fromSky * ToontownGlobals.SuitWalkSpeed)/2)
            result = Parallel(
                Func(suit.attachPropeller),
                Sequence(
                    Func(suit.setPos, underPos),
                    Parallel(moveIval, propTrack)
                )
            )
            return result
        destPos, destHpr = battle.getActorPosHpr(suit)
        suit.wrtReparentTo(battle)
        moveIval = createSuitMoveIval(suit, destPos, trapProp)

        sinkPos1 = trapProp.getPos(battle)
        sinkPos2 = trapProp.getPos(battle)
        sinkPos1.setZ(sinkPos1.getZ() - 3.1)
        sinkPos2.setZ(sinkPos2.getZ() - 9.1)

        moveTrack = Sequence(
            Wait(0.9),
            LerpPosInterval(suit, 0.9, sinkPos1, other=battle),
            LerpPosInterval(suit, 0.4, sinkPos2, other=battle),
            Func(suit.wrtReparentTo, hidden)
        )
        animTrack = Sequence(
            ActorInterval(suit, 'flail'),
            ActorInterval(suit, 'flail', startTime=1.1)
        )
        fallingSoundTrack = Sequence(
            Wait(0.7),
            SoundInterval(globalBattleSoundCache.getSound('TL_quicksand.ogg'), node=suit),
            Wait(0.1)
        )
        suitFallTrack = Sequence(
            Func(suitNeutral),
            Wait(0.6),
            Parallel(moveTrack, animTrack, fallingSoundTrack)
        )
        # suitInbetweenTrack = Sequence(Func(suit.setSkelecog, 1), Func(suit.healthBar.show), Func(soakSuit), Func(suit.setHp, suit.getMaxHp()), Func(suit.wrtReparentTo, battle))
        suitInbetweenTrack = Func(suitInbetweens)
        suitTrack = Sequence(suitFallTrack, suitInbetweenTrack, moveIval)

        return Parallel(suitTrack, trapTrack)
    else:
        suit.setPendingQueuedRevive(True)
        suitPos, suitHpr = battle.getActorPosHpr(suit)
        removeTrainTrack(suit, battle, suitTrack)
        deathSuit = suit
        deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
        hasAnimatedHead = False
        if suit.style.name == 'rainmake' and not suit.isSkeleton:
            for headPart in suit.animatedHeadParts:
                headInterval = Sequence(Func(headPart.loop, 'murmur'))
                hasAnimatedHead = True
        elif suit.style.name == 'payman' and not suit.isSkeleton:
            for headPart in suit.animatedHeadParts:
                headInterval = Sequence(Func(headPart.loop, 'murmur'))
                hasAnimatedHead = True
        elif suit.style.name == 'pcrat' and not suit.isSkeleton:
            for headPart in suit.animatedHeadParts:
                headInterval = Sequence(Func(headPart.loop, 'murmur'))
                hasAnimatedHead = True
        # elif suit.style.name == 'cdirector' and not suit.isSkeleton:
        #     for headPart in suit.animatedHeadParts:
        #         headInterval = Sequence(Func(headPart.loop, 'murmur'))
        #         hasAnimatedHead = True
        else:
            for headPart in suit.animatedHeadParts:
                hasAnimatedHead = True
            if hasAnimatedHead:
                if suit.dna.name in ('treasure', 'lgator'):
                    for headPart in suit.headParts:
                        headInterval = Sequence(ActorInterval(headPart, 'death'), Func(headPart.loop, 'neutral'))
                else:
                    for headPart in suit.animatedHeadParts:
                        headInterval = Sequence(ActorInterval(headPart, 'death'), Func(headPart.loop, 'neutral'))
        suitTrack.append(Func(suit.makeDead))
        if suit.isSkeleton:
            suitTrack.append(
            ActorInterval(suit, 'skeleton-lose', duration=SUIT_LOSE_DURATION))
        else:
            suitTrack.append(
            ActorInterval(suit, 'lose', duration=SUIT_LOSE_DURATION))
        suitTrack.append(Func(suit.hide))
        for headPart in suit.headParts:
            suitTrack.append(Func(headPart.hide))
        suitTrack.append(Func(suit.setSkelecog2, True))
        suitTrack.append(Func(suit.show))
        suitTrack.append(Sequence(Func(suit.showHpStringSkeletonRevive)))
        suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() / 2)))
        suitTrack.append(Func(suit.updateHealthBar, 0))
        suitTrack.append(Func(suit.setSuitStatusEffect, 'damageUp', modifier=50, mode='refreshModifier'))
        suitTrack.append(Func(suit.makeRevive))
        suitTrack.append(Func(suit.makeUnDead))
        suitTrack.append(ActorInterval(suit, 'landing', startTime=1.25))
        suitTrack.append(Func(suit.loop, 'neutral'))
        if suit.style.name == 'caseman' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
        elif suit.style.name == 'stenog' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
        elif suit.style.name == 'crystal' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
        elif suit.style.name == 'ddiver' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
        elif suit.style.name == 'sgoat' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
        elif suit.style.name == 'lgator' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
        elif suit.style.name == 'treasure' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
        elif suit.style.name == 'liquidr' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_gatekeep_death.ogg')
        elif suit.style.name == 'hustle' and not suit.isSkeleton:
             spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
        elif suit.style.name == 'bookkeep' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
        elif suit.style.name == 'bellring' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
        elif suit.style.name == 'whunter' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
        elif suit.style.name == 'racket' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
        elif suit.style.name == 'chairman' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
        elif suit.style.name == 'ottoman' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
        elif suit.style.name == 'fires' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
        elif suit.style.name == 'prethink' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
        elif suit.style.name == 'duckshfl' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
        elif suit.style.name == 'hrollers' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
        elif suit.style.name == 'chainsaw' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
        elif suit.style.name == 'chainsaw2' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
        elif suit.style.name == 'treek' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
        elif suit.style.name == 'mouthp' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
        elif suit.style.name == 'hroller2' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
        elif suit.style.name == 'rainmake' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
        elif suit.style.name == 'mplayer' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
        elif suit.style.name == 'director' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
        elif suit.style.name == 'psetter' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
        elif suit.style.name == 'videog' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
        elif suit.style.name == 'bkeeper' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
        elif suit.style.name == 'phouse' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
        elif suit.style.name == 'wtapper' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
        elif suit.style.name == 'hroller' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
        elif suit.style.name == 'ambass':
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ambass_death.ogg')
        elif suit.style.name == 'safesupervis' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
        elif suit.style.name == 'dold' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
        elif suit.style.name == 'dold' and suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death_skel.ogg')
        elif suit.style.name == 'duckshfl' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
        elif suit.style.name == 'derrhand' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
        elif suit.style.name == 'derrhand' and suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
        elif suit.style.name == 'derrman' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
        elif suit.style.name == 'fbed' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_fbed_death.ogg')
        elif suit.style.name == 'arbit' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
        elif suit.style.name == 'cdirector':
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
        elif suit.style.name == 'rkeeper' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
        elif suit.style.name == 'liquid' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
        elif suit.style.name == 'cbutcher' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
        elif suit.style.name == 'dopa':
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
        elif suit.style.name == 'dopr':
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
        elif suit.style.name == 'ubuster':
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
        elif suit.style.name == 'radiog':
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
        elif suit.style.name == 'djockey' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
        elif suit.style.name == 'ptjockey' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
        elif suit.style.name == 'hustle' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_dola_death.ogg')
        elif suit.style.name == 'dola' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_dola_death.ogg')
        elif suit.style.name == 'pcrat' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
        elif suit.style.name == 'payman' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
        elif suit.style.name == 'racket' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
        elif suit.style.name == 'dking' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
        elif suit.style.name == 'redd' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
        elif suit.isFemale and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
        elif suit.isFemaleSkelecog and suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
        elif suit.isSkelecogDialogue:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
        elif suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
        else:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
            toonMTrack.append(Sequence(Wait(2.0), ActorInterval(mtoon, 'duck'), ActorInterval(mtoon, 'duck', startTime=1.8), Func(mtoon.loop, 'neutral')))

        returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
        if hasAnimatedHead:
            returnval.append(headInterval)
        return returnval

def startCameraSpinTask(suit):
    taskMgr.add(cameraSpinTask, 'cameraSpinTask', extraArgs=[suit], appendTask=True)

def endCameraSpinTask():
    taskMgr.remove('cameraSpinTask')

def cameraSpinTask(suit, task = None):
    taskTime = task.time
    if round(taskTime * 100) % 2:
        return task.cont

    # Get the center position.
    #x, y, z = CountErclaimBattleAPosHpr[:3]
    suitPos = suit.getPos()
    x = suitPos.getX()
    y = suitPos.getY()

    # Move the Z up.
    z = 10

    # Get X and Y offsets.
    startRadians = math.pi / 2
    spinSpeed = 1 / 5.5
    radius = 19
    xOffset = math.sin((taskTime * spinSpeed) + startRadians) * radius
    yOffset = math.cos((taskTime * spinSpeed) + startRadians) * radius

    # Get heading for camera.
    heading = (-math.degrees((taskTime * spinSpeed) + startRadians) + 180) % 360

    # Set camera pos.
    camera.setPosHpr(x + xOffset, -y + yOffset, z, heading, -12, 0)

    # # Set erfit, if we need to.
    # if not self.erfitSet:
    #     self.placeAliveSuits()
    #     self.erfitSet = True

    return task.cont

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
    suitTrack.append(Func(suit.makeSwole))
    suitTrack.append(Func(suit.setMaxHP2, 4990))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.setSuitStatusEffect, 'ambassadorPhase', modifier=1))
    suitTrack.append(Func(suit.makeRevive))
    suitTrack.append(ActorInterval(suit, 'pie-small-react'))
    suitTrack.append(LerpColorScaleInterval(suit.getGeomNode(), 0.5, (1, .2, .2, 1), blendType='easeIn'))
    suitTrack.append(Func(suit.setNeutralAnimation))
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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

def createErfitDeathTrack(suit, battle):
    suitTrack = Sequence()
    from toontown.battle import MovieCamera
    suitTrack.append(MovieCamera.heldShot(0.0, -15.0, 10.0, 0, -20, 0, 0))
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    # deathSuit = suit
    # deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    startTalkTime = 0
    msgTime = 3.0
    endDelay = 2
    returnval = Parallel(suitTrack)
    return Parallel(returnval, Track(
            (startTalkTime, Parallel(Func(suit.setChatAbsolute, "I can't believe I've been bested at my game!", CFSpeech))),
            (startTalkTime + (msgTime * 1), Func(suit.setChatAbsolute, "By a Toon, no less, with no muscles or fame!", CFSpeech)),
            (startTalkTime + (msgTime * 2), Func(suit.setChatAbsolute, "Well, my bro, I hope this won't be the end.", CFSpeech)),
            (startTalkTime + (msgTime * 3), Func(suit.setChatAbsolute, "Just come back for a rematch, and bring a lazy friend!", CFSpeech)),
            (startTalkTime + (msgTime * 3), Sequence(Wait(3.0), Parallel(SoundInterval(base.loader.loadSfx('phase_13/audio/sfx/april_toons/erfit_defeat.ogg'), volume=0.62), Func(suit.makeUnSwole), Func(suit.hide)))),
        ))

def createErfitReviveTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    # deathSuit = suit
    # deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    startTalkTime = 1.5
    msgTime = 4.0
    endDelay = 2
    # suitTrack.append(Func(suit.hide))
    # for headPart in suit.headParts:
    #     suitTrack.append(Func(headPart.hide))
   # suitTrack.append(Func(suit.setSkelecog2, True))
  #  suitTrack.append(Func(suit.show))
    from toontown.suit.DistributedCountErclaimBoss import DistributedCountErclaimBoss
    for obj in base.cr.doId2do.values():
        if isinstance(obj, DistributedCountErclaimBoss):
            suitTrack.append(Func(obj.stopPhaseOneMusic))
            suitTrack.append(Func(obj.erfitRevive))
    suitTrack.append(Func(suit.setHP, 15777))
    suitTrack.append(Func(suit.getGeomNode().setScale, 7.5 / 6.06))
    suitTrack.append(Func(suit.setHeight, 10.5))
    suitTrack.append(Func(suit.setMaxHP2, 15777))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.setSuitStatusEffect, 'damageUp', modifier=30, mode='refreshModifier'))
    suitTrack.append(Func(suit.makeSwole))
    suitTrack.append(LerpColorScaleInterval(suit.getGeomNode(), 0.5, (1, .2, .2, 1), blendType='easeIn'))
    suitTrack.append(Func(suit.makeRevive))
    # suitTrack.append(ActorInterval(suit, 'pie-small-react'))
    suitTrack.append(Func(suit.setNeutralAnimation))
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
    return Parallel(returnval, Func(startCameraSpinTask, suit), Track(
            (startTalkTime, Parallel(Func(suit.setChatAbsolute, "Check it, bros. The fight maxed out my arms!", CFSpeech))),
            (startTalkTime + (msgTime * 1), Func(suit.setChatAbsolute, "My muscles are so huge! It's time to sound the alarms!", CFSpeech)),
            (startTalkTime + (msgTime * 2), Func(suit.setChatAbsolute, "Get ready for a show, Toon, you'll surely cower!", CFSpeech)),
            (startTalkTime + (msgTime * 3) - 1, Parallel(ActorInterval(suit, 'smile'),
                                                         Func(suit.showHpTextNew, 0,
                                                              text='+40% Damage',
                                                              colorCode=1))),
            (startTalkTime + (msgTime * 3), Func(suit.setChatAbsolute, "Brace yourselves Toons... This is the definition of POWER!", CFSpeech)),
            (startTalkTime + (msgTime * 3) - 1 + 3.95, Func(suit.setNeutralAnimationDrop)),
            (startTalkTime + (msgTime * 3) - 1 + 3.95 + endDelay, Parallel(Func(suit.setChatAbsolute, "", CFSpeech | CFTimeout), Func(endCameraSpinTask))),
        ))

def createSuitReviveRedd(suit, battle):
    suitTrack = Sequence()
    suit.setPendingQueuedRevive(True)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        hasAnimatedHead = True
    if hasAnimatedHead:
        if suit.dna.name in ('treasure', 'lgator'):
            for headPart in suit.headParts:
                headInterval = Sequence(ActorInterval(headPart, 'death'), Func(headPart.loop, 'neutral'))
        else:
            for headPart in suit.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'death'), Func(headPart.loop, 'neutral'))
    if suit.isSkeleton:
        suitTrack.append(
        ActorInterval(suit, 'skeleton-lose', duration=SUIT_LOSE_DURATION))
    else:
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
    suitTrack.append(Func(suit.setSuitStatusEffect, 'damageUp', modifier=50, mode='refreshModifier'))
    suitTrack.append(Func(suit.makeLaserRevive))
    suitTrack.append(ActorInterval(suit, 'landing', startTime=1.25))
    suitTrack.append(Sequence(Func(suit.showHpStringSkeletonRevive)))
    suitTrack.append(Func(suit.loop, 'neutral'))
    if suit.style.name == 'redd' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    else:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
        suitTrack.append(Func(suit.setSuitStatusEffect, 'extraAttacks', modifier=1, mode='refreshModifier'))
        suitTrack.append(Func(suit.setNeutralAnimation))
        suitTrack.append(Wait(2.0))
    for mtoon in battle.toons:
        toonMTrack.append(Sequence(Wait(2.0), ActorInterval(mtoon, 'duck'), ActorInterval(mtoon, 'duck', startTime=1.8), Func(mtoon.loop, 'neutral')))

    returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    if hasAnimatedHead:
        returnval.append(headInterval)
    return returnval

def createPromotionTrackPressurizer(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend=base.wantSmoothAnims)
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.setVirtual, True, True))
    suitTrack.append(Func(suit.setCog, True))
    suitTrack.append(Func(suit.show))
    suitTrack.append(Wait(3.0))
    suitTrack.append(Func(suit.showHpString, 'VIRTUALIZED!', 2))
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
    suitTrack.append(Func(suit.setSuitStatusEffect, 'damageUp', modifier=50, mode='refreshModifier'))
    suitTrack.append(Func(suit.makeLaserRevive))
    suitTrack.append(ActorInterval(suit, 'slip-backward'))
    suitTrack.append(Func(suit.setNeutralAnimation))
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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

def createOverpressuredInterval(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend=base.wantSmoothAnims)
    suitTrack.append(Func(suit.hide))
    if suit.isSkeleton:
        suitTrack.append(Func(suit.setVirtual, True, True))
        suitTrack.append(Func(suit.makeLaserRevive))
    else:
        suitTrack.append(Func(suit.setSkelecog2, True))
        suitTrack.append(Func(suit.makeRevive))
    suitTrack.append(Func(suit.setCog, True))
    suitTrack.append(Func(suit.show))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() * 2)))
    suitTrack.append(Func(suit.setSuitStatusEffect, 'vulnerable', modifier=50, mode='refreshModifier'))
    suitTrack.append(Func(suit.setSuitStatusEffect, 'damageUp', modifier=50, mode='refreshModifier'))
    suitTrack.append(Sequence(Func(suit.showHpStringSkeletonReviveOverpressured)))
    suitTrack.append(Func(suit.setDisplayName, suit.createNameInfoOverpressured()))
    suitTrack.append(ActorInterval(suit, 'slip-backward'))
    suitTrack.append(Func(suit.setNeutralAnimation))
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
    suitTrack.append(Func(suit.setSuitStatusEffect, 'damageUp', modifier=50, mode='refreshModifier'))
    suitTrack.append(Func(suit.makeLaserRevive))
    suitTrack.append(LerpColorScaleInterval(suit, 0, (0, 0, 0, 0)))
    suitTrack.append(Func(suit.setNeutralAnimation))
    returnval = Parallel(suitTrack)
    return returnval

def createSuitReviveTrackVirtual(suit, battle):
    suitTrack = Sequence()
    suit.setPendingQueuedRevive(True)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        hasAnimatedHead = True
    if hasAnimatedHead:
        if suit.dna.name in ('treasure', 'lgator'):
            for headPart in suit.headParts:
                headInterval = Sequence(ActorInterval(headPart, 'death'), Func(headPart.loop, 'neutral'))
        else:
            for headPart in suit.animatedHeadParts:
                headInterval = Sequence(ActorInterval(headPart, 'death'), Func(headPart.loop, 'neutral'))
    suitTrack.append(Func(suit.makeDead))
    if suit.isSkeleton:
        suitTrack.append(
        ActorInterval(suit, 'skeleton-lose', duration=SUIT_LOSE_DURATION))
    else:
        suitTrack.append(
        ActorInterval(suit, 'lose', duration=SUIT_LOSE_DURATION))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.setSkelecog2, True))
    suitTrack.append(Func(suit.setVirtual, True, True))
    suitTrack.append(Func(suit.setName, suit.createNameInfoVirtual()))
    suitTrack.append(Func(suit.show))
    suitTrack.append(Func(suit.makeUnDead))
    suitTrack.append(Sequence(Func(suit.showHpStringSkeletonRevive)))
    suitTrack.append(Func(battle.unlureSuit, suit))
    suitTrack.append(Func(battle.unSueSuit, suit))
    suitTrack.append(Func(suit.setDizzy, 0))
    suitTrack.append(Func(suit.setMaxHP, (suit.getMaxHP() / 2)))
    suitTrack.append(Func(suit.updateHealthBar, 0))
    suitTrack.append(Func(suit.setSuitStatusEffect, 'damageUp', modifier=50, mode='refreshModifier'))
    suitTrack.append(Func(suit.makeLaserRevive))
    suitTrack.append(ActorInterval(suit, 'landing', startTime=1.25))
    suitTrack.append(Func(suit.loop, 'neutral'))
    if suit.style.name == 'caseman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'stenog' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'crystal' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'ddiver' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
    elif suit.style.name == 'sgoat' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
    elif suit.style.name == 'lgator' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'treasure' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'liquidr' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_gatekeep_death.ogg')
    elif suit.style.name == 'hustle' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'bookkeep' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'bellring' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'whunter' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'racket' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'chairman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'ottoman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'fires' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'prethink' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'duckshfl' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'hrollers' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'chainsaw' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'chainsaw2' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'treek' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
    elif suit.style.name == 'mouthp' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
    elif suit.style.name == 'hroller2' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'rainmake' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'mplayer' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'director' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'psetter' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'videog' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'bkeeper' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'phouse' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'wtapper' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'hroller' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'ambass':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ambass_death.ogg')
    elif suit.style.name == 'safesupervis' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'dold' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'dold' and suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death_skel.ogg')
    elif suit.style.name == 'duckshfl' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'derrhand' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'derrhand' and suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'derrman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
    elif suit.style.name == 'fbed' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'arbit' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
    elif suit.style.name == 'cdirector':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'rkeeper' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'liquid' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'cbutcher' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'dopa':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'dopr':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'ubuster':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'radiog':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'djockey' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'ptjockey' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'pcrat' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'hustle' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_dola_death.ogg')
    elif suit.style.name == 'dola' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_dola_death.ogg')
    elif suit.style.name == 'payman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'racket' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'dking' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'redd' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.isFemale and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.isFemaleSkelecog and suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.isSkelecogDialogue:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    elif suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    else:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
        toonMTrack.append(Sequence(Wait(2.0), ActorInterval(mtoon, 'duck'), ActorInterval(mtoon, 'duck', startTime=1.8), Func(mtoon.loop, 'neutral')))

    returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    if hasAnimatedHead:
        returnval.append(headInterval)
    return returnval

def createVirtualSuitDeathTrack(suit, battle):
    suitTrack = Sequence()
    suit._pendingQueuedDeath = True
    if suit.hasSuitStatusEffect('overpressured'):
        return Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    deathSuit = suit
    headInterval = Sequence()
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        hasAnimatedHead = True
    if hasAnimatedHead:
        if suit.dna.name in ('treasure', 'lgator'):
            for headPart in suit.headParts:
                headInterval.append(ActorInterval(headPart, 'death', duration=2))
        else:
            for headPart in suit.animatedHeadParts:
                headInterval.append(ActorInterval(headPart, 'death', duration=2))
    if suit.style.name == 'wsi':
        from toontown.battle import MovieCamera
        suitTrack.append(Func(suit.makeDead))
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
        suitTrack.append(Parallel(ActorInterval(suit, 'lose', duration=2)))
        deathSound = base.loader.loadSfx('phase_11/audio/sfx/LB_laser_beam_off_death.ogg')
        suitTrack.append(Parallel(ActorInterval(suit, 'slip-forward', duration=2),
                                  LerpColorScaleInterval(suit, duration=1.0, colorScale=(0, 0, 0, 0),
                                                         blendType='easeInOut'), SoundInterval(deathSound, volume=0.5)))
        suitTrack.append(Func(suit.cleanupAllBattleEffects))
        suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    elif suit.style.name in ('hrollers', 'bcaster', 'mplayers'):
        deathSound = base.loader.loadSfx('phase_11/audio/sfx/LB_capacitor_discharge_3.ogg')
        suitTrack.append(Parallel(ActorInterval(suit, 'mplayer-kneel-into'), LerpColorScaleInterval(suit, duration=1.25, colorScale=(0, 0, 0, 0),
                                   blendType='easeInOut'), SoundInterval(deathSound, volume=0.5)))
        suitTrack.append(Func(suit.loop, 'mplayer-kneel-neutral'))
        suitTrack.append(Func(suit.makeDead))
        suitTrack.append(Func(suit.cleanupAllBattleEffects))
        suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    else:
        suitTrack.append(Func(suit.makeDead))
        suitTrack.append(Parallel(ActorInterval(suit, 'lose', duration=2)))
        deathSound = base.loader.loadSfx('phase_11/audio/sfx/LB_laser_beam_off_death.ogg')
        suitTrack.append(Parallel(ActorInterval(suit, 'slip-forward', duration=2),
                                  LerpColorScaleInterval(suit, duration=1.0, colorScale=(0, 0, 0, 0),
                                                         blendType='easeInOut'), SoundInterval(deathSound, volume=0.5)))
        suitTrack.append(Func(suit.cleanupAllBattleEffects))
        suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    suitTrack.append(Func(suit.hide))
    returnval = Parallel()
    multiTrack = Parallel(suitTrack, returnval)
    if hasAnimatedHead:
        if suit.style.name not in ('wsi', 'bcaster', 'mplayers', 'hrollers'):
            returnval.append(headInterval)
    return multiTrack


def createSuitDeathTrack(suit, battle):
    suitTrack = Sequence()
    suit._pendingQueuedDeath = True

    # Corporate Clash Pacesetter special death.  Choose it here before
    # Altis constructs the normal Cog lose / gear-explosion track.
    if suit.style.name == 'psetter':
        from toontown.cutscene.PacesetterDeathCutscene import makePacesetterDeath
        return makePacesetterDeath(suit, battle)
    if suit.style.name == 'chainsaw':
        controller = getattr(battle, 'bossCog', None)
        if controller is not None and hasattr(controller, 'chainsawPhase'):
            from toontown.cutscene.ChainsawDeathCutscenes import makeChainsawDeath
            return makeChainsawDeath(suit, battle)
    suitTrackErfit = Sequence(createErfitDeathTrack(suit, battle))
    if suit.hasSuitStatusEffect('overpressured'):
        return Sequence()
    if suit.style.name == 'erclaim':
        return makeErclaimDeath(suit, battle)
    if suit.style.name == 'erfit':
        return createErfitDeathTrack(suit, battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    if suit.style.name == 'rainmake' and not suit.isSkeleton:
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(Func(headPart.loop, 'murmur'))
            hasAnimatedHead = True
    elif suit.style.name == 'payman' and not suit.isSkeleton:
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(Func(headPart.loop, 'murmur'))
            hasAnimatedHead = True
    elif suit.style.name == 'pcrat' and not suit.isSkeleton:
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(Func(headPart.loop, 'murmur'))
            hasAnimatedHead = True
    # elif suit.style.name == 'cdirector' and not suit.isSkeleton:
    #     for headPart in suit.animatedHeadParts:
    #         headInterval = Sequence(Func(headPart.loop, 'murmur'))
    #         hasAnimatedHead = True
    else:
        for headPart in suit.animatedHeadParts:
            hasAnimatedHead = True
        if hasAnimatedHead:
            if suit.dna.name in ('treasure', 'lgator'):
                for headPart in suit.headParts:
                    headInterval = Sequence(ActorInterval(headPart, 'death'))
            else:
                for headPart in suit.animatedHeadParts:
                    headInterval = Sequence(ActorInterval(headPart, 'death'))
    suitTrack.append(Func(suit.makeDead))
    if suit.isSkeleton:
        suitTrack.append(
        ActorInterval(suit, 'skeleton-lose', duration=SUIT_LOSE_DURATION))
    else:
        suitTrack.append(
        ActorInterval(suit, 'lose', duration=SUIT_LOSE_DURATION))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    if suit.style.name == 'caseman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'stenog' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'crystal' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'ddiver' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ddiver_death.ogg')
    elif suit.style.name == 'sgoat' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_sgoat_death.ogg')
    elif suit.style.name == 'lgator' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'treasure' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_lgator_death.ogg')
    elif suit.style.name == 'liquidr' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_gatekeep_death.ogg')
    elif suit.style.name == 'hustle' and not suit.isSkeleton:
            spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'bookkeep' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'bellring' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'whunter' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_whunter_death.ogg')
    elif suit.style.name == 'racket' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'chairman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chairman_death.ogg')
    elif suit.style.name == 'ottoman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ottoman_death.ogg')
    elif suit.style.name == 'fires' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'prethink' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_prethink_death.ogg')
    elif suit.style.name == 'duckshfl' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'hrollers' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'chainsaw' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'chainsaw2' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'treek' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_treek_death.ogg')
    elif suit.style.name == 'mouthp' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mouthp_death.ogg')
    elif suit.style.name == 'hroller2' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'rainmake' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_rainmake_death.ogg')
    elif suit.style.name == 'mplayer' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'director' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_mplayer_death.ogg')
    elif suit.style.name == 'psetter' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'videog' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_psetter_death.ogg')
    elif suit.style.name == 'hustle' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_dola_death.ogg')
    elif suit.style.name == 'dola' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_dola_death.ogg')
    elif suit.style.name == 'bkeeper' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_caseman_death.ogg')
    elif suit.style.name == 'phouse' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'wtapper' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'hroller' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_hroller_death.ogg')
    elif suit.style.name == 'ambass':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_ambass_death.ogg')
    elif suit.style.name == 'safesupervis' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fires_death.ogg')
    elif suit.style.name == 'dold' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death.ogg')
    elif suit.style.name == 'dold' and suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dold_death_skel.ogg')
    elif suit.style.name == 'duckshfl' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_duckshfl_death.ogg')
    elif suit.style.name == 'derrhand' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death.ogg')
    elif suit.style.name == 'derrhand' and suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_derrhand_death_skel.ogg')
    elif suit.style.name == 'derrman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_derrman_death.ogg')
    elif suit.style.name == 'fbed' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'arbit' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_clo_death.ogg')
    elif suit.style.name == 'cdirector':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_chainsaw_death.ogg')
    elif suit.style.name == 'rkeeper' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'liquid' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_bellring_death.ogg')
    elif suit.style.name == 'cbutcher' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_stenog_death.ogg')
    elif suit.style.name == 'dopa':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'dopr':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'ubuster':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopr_death_skel.ogg')
    elif suit.style.name == 'radiog':
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_dopa_death_skel.ogg')
    elif suit.style.name == 'djockey' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'ptjockey' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_ptjockey_death.ogg')
    elif suit.style.name == 'pcrat' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'payman' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_pcrat_death.ogg')
    elif suit.style.name == 'racket' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/dial/ttcc_ene_fbed_death.ogg')
    elif suit.style.name == 'dking' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.style.name == 'redd' and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/ttcc_ene_redd_death.ogg')
    elif suit.isFemale and not suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death_f.ogg')
    elif suit.isFemaleSkelecog and suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death_f.ogg')
    elif suit.isSkelecogDialogue:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    elif suit.isSkeleton:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Skel_Cog_Death.ogg')
    else:
        spinningSound = base.loader.loadSfx('phase_3.5/audio/sfx/Cog_Death.ogg')
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
    if suit.style.name == 'erfit':
        returnval = Parallel(suitTrackErfit)
    else:
        returnval = Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    if hasAnimatedHead and not suit.style.name == 'erfit':
        returnval.append(headInterval)
    return returnval

def getPropAppearTrack(prop, parent, posPoints, appearDelay, scaleUpPoint = Point3(1), scaleUpTime = 0.5, startScale = Point3(0.01), poseExtraArgs = None):
    propTrack = Sequence(Wait(appearDelay), Func(__showProp, prop, parent, *posPoints))
    if poseExtraArgs:
        propTrack.append(Func(prop.pose, *poseExtraArgs))
    propTrack.append(LerpScaleInterval(prop, scaleUpTime, scaleUpPoint, startScale=startScale))
    return propTrack

def createSuitDeathTrackExplosiveForeman(suit, battle):
    suitTrack = Sequence()
    suit._pendingQueuedDeath = True
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    hasAnimatedHead = False
    toonPos = suit.getPos(battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + suit.height - 0.2)
    explosionTrack3 = Sequence()
    explosionTrack3.append(createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint, scale=3))
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    gearPoint2 = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height - 0.2)
    explosionTrack2 = Sequence()
    explosionTrack2.append(createKapowExplosionTrackAttack(battle, explosionPoint=gearPoint2, scale=3))
    explode = []
    for i in xrange(0, 3):
        explode.append(globalPropPool.getProp('explosion'))
    explodePosPoints = [Point3(0, 15, 5), PNT3_ZERO]
    explodePosPoints1 = [Point3(0, 15, 5), PNT3_ZERO]
    explodeHprPoints = [Point3(180, 0, 0), PNT3_ZERO]
    explodeHprPoints1 = [Point3(180, 0, 0), PNT3_ZERO]
    explodeTracks = Parallel()
    for i in xrange(0, 3):
        explodeTrack = Sequence()
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints, 1e-06, Point3(1.7, 1.7, 1.7), scaleUpTime=0.1))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodePosPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints, 1e-06, Point3(0, 0, 0), scaleUpTime=0.3))
        explodeTrack.append(
            getPropAppearTrack(explode[i], suit, explodeHprPoints1, 1e-06, Point3(0, 0, 0), scaleUpTime=0.1))
        explodeTracks.append(explodeTrack)
    suitTrack.append(Func(battle.unlureSuit, suit))
    suitTrack.append(Func(battle.unSueSuit, suit))
    suitTrack.append(Func(suit.setDizzy, 0))
    suitTrack.append(Func(insertDeathSuit, suit, suit, battle, suitPos, suitHpr))
    if suit.isSkeleton:
        suitTrack.append(
        ActorInterval(suit, 'skeleton-lose', startTime=6))
    else:
        suitTrack.append(
        ActorInterval(suit, 'lose', startTime=6))
    suitTrack.append(Func(removeDeathSuit, suit, suit, name='remove-death-suit'))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
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
    gears1Track = Sequence(Wait(2.1), ParticleInterval(smallGears, battle, worldRelative=0, duration=4.3, cleanup=True), name='gears1Track')
    gears2MTrack = Track((0.0, explosionTrack), (0.7, ParticleInterval(singleGear, battle, worldRelative=0, duration=5.7, cleanup=True)), (5.2, ParticleInterval(smallGearExplosion, battle, worldRelative=0, duration=1.2, cleanup=True)), (5.4, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=1.0, cleanup=True)), name='gears2MTrack')
    toonMTrack = Parallel(name='toonMTrack')
    for mtoon in battle.toons:
        toonMTrack.append(Sequence(Wait(1.0), ActorInterval(mtoon, 'duck'), ActorInterval(mtoon, 'duck', startTime=1.8), Func(mtoon.loop, 'neutral')))
    returnval = Parallel(suitTrack, deathSoundTrack, explosionTrack3, explosionTrack2, explosionTrack)
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
    suit._pendingQueuedDeath = True
    if suit.hasSuitStatusEffect('overpressured'):
        return Sequence()
    suitTrack = Sequence()
    if suit.style.name == 'erclaim':
        return makeErclaimDeath(suit, battle)
    if suit.style.name == 'erfit':
        return createErfitDeathTrack(suit, battle)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitTrack.append(ActorInterval(suit, 'lose2', duration=4.0))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.cleanupLoseActor))
    suitTrack.append(Func(suit.makeDead))
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    suitType = getSuitBodyType(suit.dna.name)
    if suitType == 'a':
        deathSound = base.loader.loadSfx('phase_5/audio/sfx/cc_s_sfx_ene_suit_headlessDeath_A.ogg')
    elif suitType == 'b':
        deathSound = base.loader.loadSfx('phase_5/audio/sfx/cc_s_sfx_ene_suit_headlessDeath_B.ogg')
    else:
        deathSound = base.loader.loadSfx('phase_5/audio/sfx/cc_s_sfx_ene_suit_headlessDeath_C.ogg')
    deathSoundTrack = Sequence(Wait(0), SoundInterval(deathSound, volume=0.6))
    returnval = Parallel(suitTrack, deathSoundTrack)
    return returnval

def createSuitWreckingDeathTrack(suit, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    removeTrainTrack(suit, battle, suitTrack)
    deathSuit = suit
    deathSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitType = getSuitBodyType(suit.dna.name)
    if suitType == 'a':
        deathSound = base.loader.loadSfx('phase_5/audio/sfx/AA_trap_wreckingball_A.ogg')
    elif suitType == 'b':
        deathSound = base.loader.loadSfx('phase_5/audio/sfx/AA_trap_wreckingball_B.ogg')
    else:
        deathSound = base.loader.loadSfx('phase_5/audio/sfx/AA_trap_wreckingball_C.ogg')
    deathSoundTrack = Sequence(Wait(0), SoundInterval(deathSound, volume=0.6))
    suitTrack.append(ActorInterval(suit, 'lose3', duration=4.0))
    suitTrack.append(Func(suit.hide))
    suitTrack.append(Func(suit.cleanupLoseActor))
    suitTrack.append(Func(suit.makeDead))
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    returnval = Parallel(suitTrack, deathSoundTrack)
    return returnval

def createSuitCrashTrack(suit, battle, level):
    suitScale = suit.getGeomNode().getScale()
    suit._pendingQueuedDeath = True
    fallSound = globalBattleSoundCache.getSound('cogbldg_land.ogg')
    crushSound = base.loader.loadSfx('phase_5/audio/sfx/TL_train_cog.ogg')

    # To make it match up a little better, make the squish sound start a little sooner for these gags.
    times = {4: 1.25, 5: 0.7, 6: 0.65, 7: 0.0}
    startTime = times.get(level, 0)

    # Functions for quick death drop extension.
    finalSeq = Sequence(
        Wait(3),  # Delay 3 seconds
        LerpScaleInterval(suit, 0.5, (0.01, 0.01, 0.01), blendType='easeIn'),  # Shrink the silhouette
        Func(suit.hide), Func(suit.cleanupAllBattleEffects), Func(suit.clearAllSuitStatusEffects)    # Hide the silhouette
    )

    initialZ = suit.getZ()

    # Define this here so that we can grab the length.
    suitFlatten = Sequence(Parallel(LerpFunc(suit.setZ, duration=0.125, fromData=initialZ, toData=initialZ - 1),
                                    ActorInterval(suit, 'flatten', startFrame=0, endFrame=4)))
    suitFlattenDuration = suitFlatten.getDuration()

    def waitPlaySquishSound():
        seq = Sequence(Wait(suitFlattenDuration - startTime), Func(base.playSfx, crushSound))
        seq.start()

    def suitSquished():
        node = suit.getGeomNode().getChild(0)
        node.setColorScale(0, 0, 0, 1)
        # Flatten the suit
        suit.pose('flatten', 5)
        # Position the suit slightly above the ground to prevent clipping
        suit.setZ(initialZ + 0.1)
        # Set the scale of the suit to be regular, but flattened
        suit.getGeomNode().setScale(suitScale[0], suitScale[1], 0.025)

    suitGettingHitParallelHolder = Parallel()
    suitReact = Sequence(Func(waitPlaySquishSound), 
                            suitFlatten,                              
                            Func(base.playSfx, fallSound, volume=0.65),
                            Func(suit.splatSuit, 0, 1), Func(suit.makeUnMarked), 
                            Func(suitSquished),                                   
                            finalSeq)                          
    suitGettingHitInternal = Sequence(suitReact)
    suitGettingHitParallelHolder.append(suitGettingHitInternal)
    hasAnimatedHead = False
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(Func(waitPlaySquishSound), (ActorInterval(headPart, 'neutral', startTime=0, endTime=0)))
        hasAnimatedHead = True
    if hasAnimatedHead:
        suitGettingHitParallelHolder.append(headInterval)
    suitGettingHit = Sequence(suitGettingHitParallelHolder)
    return suitGettingHit

def createSuitCrashTrackOLD(suit, battle):
    suitScale = suit.getScale()
    node = suit.getGeomNode().getChild(0)
    suitPos = suit.getPos()
    hitTime = 0.1
    shrinkStartDelay = 3.0
    #crashSoundEffects = []
    #for sound in crashSounds:
        #crashSoundEffects.append(globalBattleSoundCache.getSound(sound))
    soundTrack = base.loader.loadSfx('phase_5/audio/sfx/drop_react.ogg')
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
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    if hasAnimatedHead:
        return Parallel(suitTrack, deathSoundTrack, headInterval)
    else:
        return Parallel(suitTrack, deathSoundTrack)

def midairSuitExplodeTrack(suit, battle):
    suitTrack = Sequence()
    suit._pendingQueuedDeath = True
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    #suitPos.setZ(suitPos.getZ() + 17)
    #suitTrack.append(Wait(0.15))
    suitTrack.append(Func(suit.pose, 'lose', 164))
    suitTrack.append(Wait(2.0))
    suitTrack.append(ActorInterval(suit, 'lose', startFrame=164))
    suitTrack.append(Func(suit.setColorScale, 0.2, 0.2, 0.2, 1))
    suitTrack.append(Func(avatarHide, suit))
    suitTrack.append(Func(suit.cleanupLoseActor))
    suitTrack.append(Func(suit.makeDead))
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart_%s.ogg' % random.randint(1, 6))
    deathSoundTrack = Sequence(SoundInterval(deathSound, volume=0.8))
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
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    explosionTrack.append(createKapowExplosionTrack(battle, explosionPoint=gearPoint))
    gears1Track = Sequence(ParticleInterval(smallGears, battle, worldRelative=0, duration=1.0, cleanup=True), name='gears1Track')
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

def makeZapDeathScorch(pos, parent=render):
    scorch = loader.loadModel('phase_5.5/models/estate/dirt_mound')
    scorch.reparentTo(parent)
    scorch.setBillboardPointWorld()
    scorch.setPos(pos)
    scorch.setP(-90)
    scorch.setScale(0.6)
    scorch.setColorScale(0.05, 0.05, 0.05, 0.85)
    scorch.setTransparency(1)

    scorchTrack = Sequence(
        Wait(0.4),
        Parallel(
            LerpScaleInterval(scorch, 1.2, 1.1, startScale=0.6),
            LerpColorScaleInterval(
                scorch,
                1.2,
                Vec4(0.05, 0.05, 0.05, 0.0),
                startColorScale=Vec4(0.05, 0.05, 0.05, 0.85)
            )
        ),
        Func(scorch.removeNode)
    )
    scorchTrack.start()
    return scorch

def shortCircuitTrack(suit, battle=None):
    suit._pendingQueuedDeath = True
    if suit.hasSuitStatusEffect('overpressured'):
        return Sequence()
    # Make a clip plane to erase the cog as we vaporize it
    
    plane = Plane(0, 0, 1, 0)  # Create the plane with a surface normal facing straight up, origin at 0
    planeNode = PlaneNode("suitClipPlane", plane)
    planeNodePath = suit.attachNewNode(planeNode)
    ashNodePath = suit.attachNewNode('ashNodePath')
    suit.setClipPlane(planeNodePath)  # Initialize the clip plane at the suit's feet.
    
    # Attach the particle to the plane as it slides up the suit, create an ash pile at feet to begin scaling up
    BattleParticles.loadParticles()
    ashEffect = BattleParticles.createParticleEffect(file='suitDistintegrate')
    
    ashPile = base.loader.loadModel('props/general/models/cc_m_prp_gen_mound_dirt')
    ashPile.setColor(0.25, 0.25, 0.25, 1)
    ashPile.reparentTo(suit)
    ashPile.hide()
    
    # Assemble the track
    
    planeStartPos = planeNodePath.getPos()
    planeEndPos = Vec3(planeStartPos[0], planeStartPos[1], suit.getHeight() + 3.5)

    ashNodeEndPosCallback = lambda: Vec3(ashNodePath.getX(), ashNodePath.getY(), suit.getHeight() + 3)
    
    dDisintegrate = 1.5
    dDisappear = 0.5

    deathHolderTrack = Parallel()
    suitTrack = Parallel(
        Func(ashEffect.start, parent=ashNodePath, renderParent=ashNodePath),
        LerpColorScaleInterval(suit, dDisintegrate / 2.0, Vec4(0, 0, 0, 1)),
        LerpPosInterval(planeNodePath, dDisintegrate, planeEndPos, startPos = planeStartPos, blendType = 'easeInOut'), # Clip plane moving up
        LerpPosInterval(ashNodePath, dDisintegrate, ashNodeEndPosCallback, blendType = 'easeInOut'), # Clip plane moving up
        Func(ashPile.wrtReparentTo, battle),
        Func(ashNodePath.wrtReparentTo, battle),
        Func(ashPile.show),
        LerpScaleInterval(ashPile, dDisintegrate, suit.getScale() * 1.5, startScale=PNT3_NEARZERO), Func(suit.cleanupAllBattleEffects), Func(suit.clearAllSuitStatusEffects)
    )  # Ash pile growing
    hideAshPile = Sequence(
        LerpScaleInterval(ashPile, dDisappear, PNT3_NEARZERO, blendType='easeIn'),
        Func(ashPile.detachNode)
    )

    finalTrack = Sequence(suitTrack, Func(BattleParticles.cleanupSystem, ashEffect, 2), Wait(1.2), Parallel(hideAshPile, Func(suit.hide)))
    deathHolderTrack.append(finalTrack)
    return deathHolderTrack


def shortCircuitTrackOLDER(suit, battle):
    if suit.isHidden():
        return Sequence()

    suitPos = suit.getPos(battle)
    # Base suit track
    suitTrack = Sequence(
        Wait(1.0),
        Func(suit.hide),
        Func(suit.cleanupLoseActor),
        Func(suit.makeDead),
        Wait(1.0)
    )
    suitTrack.append(Func(suit.cleanupAllBattleEffects))
    suitTrack.append(Func(suit.clearAllSuitStatusEffects))
    # Fade out suit parts
    colorTracks = Parallel()
    actorNode = suit.find('**/__Actor_modelRoot')
    actorCollection = actorNode.findAllMatches('*')
    for thingIndex in range(actorCollection.getNumPaths()):
        thing = actorCollection[thingIndex]
        colorTracks.append(Sequence(
            Func(thing.setDepthWrite, False),
            Func(thing.setBin, 'fixed', 1),
            LerpColorScaleInterval(thing, 1.0, (0, 0, 0, 0)),
            Func(thing.setAttrib, ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        ))

    # Smoke effect
    toonPos = suit.getPos(battle)

    # Explosion effects (reuse a loop)
    explodeTracks = Parallel()
    offsets = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]  # z offsets for explosions
    for offset in offsets:
        explode = globalPropPool.getProp('dust2')
        explode.setTwoSided(True)
        explode.setColor(0, 0, 0, 1)
        explode.setBillboardPointWorld(2)

        explodePosPoints = [Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ() + offset), PNT3_ZERO]
        delay = abs(offset) * 0.1  # small stagger
        explodeTrack = Sequence(
            Wait(delay),
            getPropAppearTrack(explode, battle, explodePosPoints, 0, Point3(2.5, 2.5, 2.5), scaleUpTime=0),
            Sequence(ActorInterval(explode, 'dust2'), Func(explode.removeNode))
        )
        explodeTracks.append(explodeTrack)

    # Return all tracks in parallel
    return Parallel(suitTrack, explodeTracks, colorTracks)

def shortCircuitTrack2(suit, battle):
    oldPos, oldHpr = battle.getActorPosHpr(suit)
    def getDustCloudIval(oldPos=oldPos):
        dustCloud = DustCloud.DustCloud(fBillboard=0, wantSound=1)
        dustCloud.setBillboardAxis(2.0)
        dustCloud.setZ(3)
        dustCloud.setScale(Point3(5.0, 1.0, 1.0))
        dustCloud.createTrack()
        dustCloud.setColorScale(0, 0, 0, 1)
        return Sequence(Func(dustCloud.reparentTo, battle), Func(dustCloud.setPos, battle, oldPos + (0, 0, suit.getHeight())), dustCloud.track, Func(dustCloud.removeNode),
                        name='dustCloadIval')

    suitTrack = Sequence(Parallel(Func(getDustCloudIval().start), Func(suit.hide)))
    return suitTrack


def createSuitDodgeMultitrack(battle, tDodge, suit, leftSuits, rightSuits):
    suitTracks = Parallel()
    soundTrack = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogjump_to_side.ogg')
    suitDodgeList, sidestepAnim = avatarDodge(leftSuits, rightSuits, 'sidestep-left', 'sidestep-right')
    for s in suitDodgeList:
        suitTracks.append(Sequence(ActorInterval(s, sidestepAnim),  Func(s.setNeutralAnimationDrop)))

    suitTracks.append(Sequence(ActorInterval(suit, sidestepAnim), Func(suit.setNeutralAnimationDrop), suit.makeCogStepBackDeathInterval(battle)))
    suitTracks.append(Func(indicateMissed, suit))
    suitTracks.append(Sequence(SoundInterval(soundTrack, volume=0.7)))
    return Sequence(Wait(tDodge), suitTracks)

def createSuitDodgeMultitrackSue(battle, tDodge, suit, leftSuits, rightSuits):
    suitTracks = Parallel()
    soundTrack = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogjump_to_side.ogg')
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
    suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'))
    suitTrack.append(Func(suit.setNeutralAnimationDrop))
    missedTrack = Sequence(Wait(delay + 0.2), Func(indicateMissed, suit, 0.9))
    return Parallel(suitTrack, missedTrack)

def createSuitTeaseMultiTrackSound(suit, battle, delay = 0.01):
    suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'))
    suitTrack.append(Func(suit.setNeutralAnimationTrap))
    missedTrack = Sequence(Wait(delay + 0.2), Func(indicateMissed, suit, 0.9))
    return Parallel(suitTrack, missedTrack)

def createSuitTeaseMultiTrackDrop(suit, battle, delay = 0.01):
    suitTrack = Sequence(Wait(delay), Wait(2.5), Func(suit.setNeutralAnimationDrop))
    missedTrack = Sequence(Wait(delay + 0.2))
    return Parallel(missedTrack)


SPRAY_LEN = 1.5

def getSprayProppedTrack(battle, color, origin, target, dScaleUp, dHold, dScaleDown, horizScale = 1.0, vertScale = 1.0, parent = render):
    track = Sequence()
    sprayProp = globalPropPool.getProp('spray')
    sprayScale = hidden.attachNewNode('spray-parent')
    sprayRot = hidden.attachNewNode('spray-rotate')
    spray = sprayRot
    spray.setColor(color)
    if callable(target):
        target = target()
    if callable(origin):
        origin = origin()
    if color[3] < 1.0:
        spray.setTransparency(1)

    def showSpray():
        sprayRot.reparentTo(parent)
        sprayRot.clearMat()
        sprayScale.reparentTo(sprayRot)
        sprayScale.clearMat()
        sprayProp.reparentTo(sprayScale)
        sprayProp.clearMat()
        sprayRot.setPos(origin.getPos(render))
        sprayRot.lookAt(Point3(target.getPos(render)))

    track.append(Func(battle.movie.needRestoreRenderProp, sprayProp))
    track.append(Func(showSpray))

    def setTargetScale(t):
        targetPos = target.getPos(render)
        posDifference = Vec3(targetPos - origin.getPos(render))
        distance = posDifference.length()
        yScale = (distance / SPRAY_LEN) * t
        sprayRot.setPos(origin.getPos(render))
        sprayRot.lookAt(Point3(target.getPos(render)))
        sprayScale.setScale(Point3(
            max(yScale * horizScale, 0.01),
            max(yScale, 0.01),
            max(yScale * vertScale, 0.01)
        ))

    def prepareToShrinkSpray():
        sprayProp.setPos(Point3(0.0, -SPRAY_LEN, 0.0))
        spray.setPos(target.getPos(render))

    def hideSpray():
        sprayProp.detachNode()
        removeProp(sprayProp)
        sprayRot.removeNode()
        sprayScale.removeNode()

    sprayTrack = Sequence(
        LerpFunctionInterval(setTargetScale, duration=dScaleUp, blendType='easeOut'),
        LerpFunctionInterval(setTargetScale, duration=dHold,    fromData=1),
        Func(prepareToShrinkSpray),
        LerpScaleInterval(sprayScale, dScaleDown, PNT3_NEARZERO),
        Func(hideSpray),
        Func(battle.movie.clearRenderProp, sprayProp)
    )

    return Sequence(track, sprayTrack)

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

def getZapTrack(battle, color, origin, target, dScaleUp, dHold, dScaleDown, horizScale = 1.0, vertScale = 1.0, parent = render, activeTrack=False):
    track = Sequence()
    zapProp = globalPropPool.getProp('zapbeam')
    zapScale = hidden.attachNewNode('zap-parent')
    zapRot = hidden.attachNewNode('zap-rotate')
    
    def rollTexMatrix(t, obj = zapProp):
        if not obj.isEmpty():
            obj.setTexOffset(TextureStage.getDefault(), -t, 0)
    
    zapProp.loop('zapbeam')
    zapTexSlide = LerpFunctionInterval(rollTexMatrix, fromData = 0, toData = 1, duration = 0.125)
    zapTexSlide.loop()
    
    zap = zapRot
    zap.setDepthWrite(False)
    zap.setColor(color)
    if color[3] < 1.0:
        zap.setTransparency(1)

    def showZap(zapScale, zapRot, zapProp, origin, target, parent):
        if callable(origin):
            origin = origin()
        if callable(target):
            target = target()
        zapRot.reparentTo(parent)
        zapRot.clearMat()
        zapScale.reparentTo(zapRot)
        zapScale.clearMat()
        zapProp.reparentTo(zapScale)
        zapProp.clearMat()
        zapRot.setPos(origin)
        zapRot.lookAt(Point3(target))

    track.append(Func(battle.movie.needRestoreRenderProp, zapProp))
    track.append(Func(showZap, zapScale, zapRot, zapProp, origin, target, parent))

    def calcTargetScale(target = target, origin = origin, horizScale = horizScale, vertScale = vertScale):
        if callable(target):
            target = target()
        if callable(origin):
            origin = origin()
        distance = Vec3(target - origin).length()
        yScale = distance / 0.1
        targetScale = Point3(horizScale, yScale, vertScale)
        return targetScale

    def trackBeam(_, target=target, origin=origin, horizScale=horizScale, vertScale=vertScale, zapRot=zapRot, zapScale=zapScale):
        if callable(target):
            target = target()
        if callable(origin):
            origin = origin()
        zapRot.setPos(origin)
        zapRot.lookAt(Point3(target))
        zapScale.setScale(calcTargetScale(target, origin, horizScale, vertScale))

    track.append(LerpScaleInterval(zapScale, dScaleUp, calcTargetScale, startScale=PNT3_NEARZERO))
    if activeTrack:
        track.append(LerpFunctionInterval(trackBeam, duration=dHold, fromData=0.0, toData=0.0))
    else:
        track.append(Wait(dHold))

    def prepareToShrinkZap(zap, zapProp, origin, target):
        if callable(target):
            target = target()
        if callable(origin):
            origin = origin()
        #zapProp.setPos(Point3(0.0, -SPRAY_LEN, 0.0))
        #zap.setPos(target)

    def updateScaleXZ(value, node=zapScale):
        xScale = horizScale * value
        yScale = node.getScale()[1]
        zScale = vertScale * value
        node.setScale(xScale, yScale, zScale)

    track.append(Func(prepareToShrinkZap, zap, zapProp, origin, target))
    track.append(LerpFunctionInterval(updateScaleXZ, duration=dScaleDown, fromData=1.0, toData=0.0))

    def hideZap(zap, zapScale, zapRot, zapProp, propPool):
        zapProp.detachNode()
        removeProp(zapProp)
        zapRot.removeNode()
        zapScale.removeNode()

    track.append(Func(hideZap, zap, zapScale, zapRot, zapProp, globalPropPool))
    track.append(Func(zapTexSlide.finish))
    track.append(Func(battle.movie.clearRenderProp, zapProp))
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
        for headPart in suit.headParts:
            headInterval = Sequence(ActorInterval(headPart, 'bellow'), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    elif suit.style.name == 'chairman':
        suitInterval = ActorInterval(suit, 'bellow')
        for headPart in suit.headParts:
            headInterval = ActorInterval(headPart, 'bellow')
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    elif suit.style.name == 'clubpres':
        suitInterval = ActorInterval(suit, 'bellow')
        for headPart in suit.headParts:
            headInterval = ActorInterval(headPart, 'bellow')
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    else:
        return stunInterval

def createShot1(suit):
    suitInterval = ActorInterval(suit, 'shot1')
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'fusiondance-shot1'), Func(headPart.loop,
                        'neutral'))
    else:
        return Parallel(headInterval, suitInterval)

def createShot2(suit):
    suitInterval = ActorInterval(suit, 'shot2')
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'fusiondance-shot2'), Func(headPart.loop,
                        'neutral'))
    else:
        return Parallel(headInterval, suitInterval)

def createShot3(suit):
    suitInterval = ActorInterval(suit, 'shot3')
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'fusiondance-shot3'), Func(headPart.loop,
                        'neutral'))
    else:
        return Parallel(headInterval, suitInterval)

def createShot4(suit):
    suitInterval = ActorInterval(suit, 'shot4')
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'fusiondance-shot4'), Func(headPart.loop,
                        'neutral'))
    else:
        return Parallel(headInterval, suitInterval)

def createShot5(suit):
    suitInterval = ActorInterval(suit, 'shot5')
    for headPart in suit.animatedHeadParts:
        headInterval = Sequence(ActorInterval(headPart, 'fusiondance-shot5'), Func(headPart.loop,
                        'neutral'))
    else:
        return Parallel(headInterval, suitInterval)

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
            suitInterval = ActorInterval(suit, 'snap2')
        else:
            suitInterval = ActorInterval(suit, 'snap2')
        for headPart in suit.headParts:
            headInterval = Sequence(ActorInterval(headPart, 'gsnap'), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval, suitInterval, headLoop)
    elif suit.style.name == 'hroller':
        if suit.isSkeleton:
            suitInterval = ActorInterval(suit, 'snap2')
        else:
            suitInterval = ActorInterval(suit, 'snap2')
        for headPart in suit.headParts:
            headInterval = Sequence(ActorInterval(headPart, 'wheelspin', startTime=2.5, endTime=4.5), Func(headPart.loop,
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
    if suit.style.name in ('hho', 'payman', 'cinema', 'fmaker', 'choreo'):
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
        suitInterval = ActorInterval(suit, 'cigar-smoke', playRate=1.25)
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'cigar-smoke', playRate=1.25), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval)
    elif suit.style.name == 'safesupervis':
        suitInterval = ActorInterval(suit, 'cigar-smoke', playRate=1.25)
        for headPart in suit.animatedHeadParts:
            headInterval = Sequence(ActorInterval(headPart, 'cigar-smoke', playRate=1.25), Func(headPart.loop,
                        'neutral'))
            headLoop = Func(headPart.loop, 'neutral%s' % ('-hurt' if float(suit.currHP) / float(suit.maxHP) <= 0.25 else ''))
            hasAnimatedHead = True
        return Parallel(headInterval)
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
    
def startSuitStunHeadInterval(suit):
    # kill any existing loop first
    if hasattr(suit, 'stunIntervalHead') and suit.stunIntervalHead:
        suit.stunIntervalHead.finish()
        suit.stunIntervalHead = None

    if suit.dna.name in ('treasure', 'lgator'):
        for headPart in suit.headParts:
            suit.stunIntervalHead = ActorInterval(headPart, 'stun')
            suit.stunIntervalHead.loop()
    else:
        for headPart in suit.animatedHeadParts:
            suit.stunIntervalHead = ActorInterval(headPart, 'stun')
            suit.stunIntervalHead.loop()

def stopSuitStunHeadInterval(suit):
    if hasattr(suit, 'stunIntervalHead') and suit.stunIntervalHead:
        suit.stunIntervalHead.finish()
        suit.stunIntervalHead = None

def createSuitStunInterval(suit, before, after):
    hasAnimatedHead = False
    headInterval2 = Func(suit.createSuitStunInterval)
    updateTrack = Sequence(Func(stopSuitStunHeadInterval, suit), Func(suit.setNeutralAnimationHead))
    for headPart in suit.animatedHeadParts:
        headInterval = Func(startSuitStunHeadInterval, suit)
        hasAnimatedHead = True
    if hasAnimatedHead:
        return Sequence(Wait(before), Func(suit.setDizzy2, 1), headInterval, Wait(after),
                            Func(suit.setDizzy2, 0), updateTrack)
    else:
        return Sequence(Wait(before), Func(suit.setDizzy2, 1), Wait(after), Func(suit.setDizzy2, 0))

def createSuitStunIntervalZap(suit, before, after):
    updateTrack = Parallel(Func(suit.setNeutralAnimationHead))
    return Sequence(Wait(before), Func(suit.setDizzy2, 1), Wait(after), updateTrack, Func(suit.setDizzy2, 0))


def createSuitStunIntervalLawbotLawyers(suit, before, after):
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
    for headPart in suit.animatedHeadParts:
        headInterval = Func(headPart.loop, 'stun')
        headLoop = Func(headPart.loop,
                            'neutral')
        hasAnimatedHead = True
    if hasAnimatedHead:
        return Sequence(Wait(before), Func(stars.reparentTo, head),
                        Func(stars.loop, 'stun'), headInterval, Wait(after), headLoop, Func(stars.cleanup),
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

def startZapCogNeutral(suit, anim):
    # kill any existing loop first
    if hasattr(suit, 'zapNeutralLoop') and suit.zapNeutralLoop:
        suit.zapNeutralLoop.finish()
        suit.zapNeutralLoop = None

    suit.zapNeutralLoop = ActorInterval(suit, anim, startFrame=0, endFrame=19)
    suit.zapNeutralLoop.loop()

def stopZapCogNeutral(suit):
    if hasattr(suit, 'zapNeutralLoop') and suit.zapNeutralLoop:
        suit.zapNeutralLoop.finish()
        suit.zapNeutralLoop = None

def zapCogNeutral(suit, anim, before, after, battle):
    suitPos = suit.getPos(battle)
    suitHpr = suit.getHpr(battle)
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit.find('**/body')]
    zapTrack = Sequence(SoundInterval(zapSfx, volume=0.6))
    spazzTrack = Func(startZapCogNeutral, suit, anim)
    if suit.isShadow or suit.dna.name == 'cbutcher':
        flashTrack = Sequence()
    else:
        flashTrack = Sequence(Func(suit.setColorScale, (1,1,0,1)), Wait(.2), Func(suit.setColorScale, (1,1,1,1)), Wait(after))
    return Sequence(Parallel(zapTrack, flashTrack, spazzTrack))

def zapCog(suit, anim, before, after, battle, died, level):
    zapSuit = suit.getZapActor()
    zapSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitPos = suit.getPos(battle)
    suitHpr = suit.getHpr(battle)
    zapSuit.setBin("fixed", 0)
    zapSuit.setDepthTest(False)
    zapSuit.setDepthWrite(False)
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit.find('**/body')]
    zapTrack = Sequence(SoundInterval(zapSfx, volume=0.6))
    # for bodyPart in suitBody:
    #     if bodyPart and not suit.isShadow and suit.dna.name != 'cbutcher':
    #         flashTrack.append(Sequence(Wait(before), Func(bodyPart.setColorScale, (0, 0, 0, 1)),
    #                               Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1))))
    if not died or suit.isVirtual or suit.hasSuitStatusEffect('overpressured') or suit.dna.name in ['erclaim', 'erfit', 'wsi', 'redd'] or level <= 3:
        spazzTrack = Sequence(Func(stopZapCogNeutral, suit), ActorInterval(suit, anim, startTime=0), suit.makeCogStepBackDeathInterval(battle))
        spazzTrack2 = Sequence(ActorInterval(zapSuit, anim, startFrame=0, endFrame=19), Wait(after))
    else:
        spazzTrack = Sequence(Func(stopZapCogNeutral, suit), Func(startZapCogNeutral, suit, anim))
        spazzTrack2 = Sequence(ActorInterval(zapSuit, anim, startFrame=0, endFrame=19), Wait(after))
    if suit.isShadow or suit.dna.name == 'cbutcher':
        flashTrack = Sequence(Func(insertZapSuit, suit, zapSuit, suit, Point3(0, 0, 0), Point3(0, 0, 0)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(removeZapSuit, suit, zapSuit), Wait(after))
    else:
        flashTrack = Sequence(Func(suit.setColorScale, (0,0,0,1)), Func(insertZapSuit, suit, zapSuit, suit, Point3(0, 0, 0), Point3(0, 0, 0)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(removeZapSuit, suit, zapSuit), Func(suit.setColorScale, (1,1,1,1)), Wait(after))
    return Sequence(Parallel(zapTrack, flashTrack, spazzTrack2, spazzTrack))

def zapCogPowerhouseZap(suit, anim, before, after, battle):
    zapSuit = suit.getZapActorPowerhouseZap()
    zapSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitPos = suit.getPos(battle)
    suitHpr = suit.getHpr(battle)
    zapSuit.setBin("fixed", 0)
    zapSuit.setDepthTest(False)
    zapSuit.setDepthWrite(False)
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit.find('**/body')]
    zapTrack = Sequence(SoundInterval(zapSfx, volume=0.6))
    # for bodyPart in suitBody:
    #     if bodyPart and not suit.isShadow and suit.dna.name != 'cbutcher':
    #         flashTrack.append(Sequence(Wait(before), Func(bodyPart.setColorScale, (0, 0, 0, 1)),
    #                               Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1))))
    spazzTrack = Sequence(ActorInterval(suit, anim, startTime=0))
    if suit.isShadow or suit.dna.name == 'cbutcher':
        flashTrack = Sequence(Func(insertZapSuit, suit, zapSuit, suit, Point3(0, 0, 0), Point3(0, 0, 0)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(removeZapSuitPowerhouseZap, suit, zapSuit), Wait(after))
    else:
        flashTrack = Sequence(Func(suit.setColorScale, (0,0,0,1)), Func(insertZapSuit, suit, zapSuit, suit, Point3(0, 0, 0), Point3(0, 0, 0)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(removeZapSuitPowerhouseZap, suit, zapSuit), Func(suit.setColorScale, (1,1,1,1)), Wait(after))
    spazzTrack2 = Sequence(ActorInterval(zapSuit, anim, startFrame=0, endFrame=19), Wait(after))
    return Sequence(Parallel(zapTrack, flashTrack, spazzTrack2, spazzTrack))

def zapCogPowerhouseSquirt(suit, anim, before, after, battle):
    zapSuit = suit.getZapActorPowerhouseSquirt()
    zapSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitPos = suit.getPos(battle)
    suitHpr = suit.getHpr(battle)
    zapSuit.setBin("fixed", 0)
    zapSuit.setDepthTest(False)
    zapSuit.setDepthWrite(False)
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit.find('**/body')]
    zapTrack = Sequence(SoundInterval(zapSfx, volume=0.6))
    # for bodyPart in suitBody:
    #     if bodyPart and not suit.isShadow and suit.dna.name != 'cbutcher':
    #         flashTrack.append(Sequence(Wait(before), Func(bodyPart.setColorScale, (0, 0, 0, 1)),
    #                               Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1))))
    spazzTrack = Sequence(ActorInterval(suit, anim, startTime=0))
    if suit.isShadow or suit.dna.name == 'cbutcher':
        flashTrack = Sequence(Func(insertZapSuit, suit, zapSuit, suit, Point3(0, 0, 0), Point3(0, 0, 0)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(removeZapSuitPowerhouseSquirt, suit, zapSuit), Wait(after))
    else:
        flashTrack = Sequence(Func(suit.setColorScale, (0,0,0,1)), Func(insertZapSuit, suit, zapSuit, suit, Point3(0, 0, 0), Point3(0, 0, 0)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(removeZapSuitPowerhouseSquirt, suit, zapSuit), Func(suit.setColorScale, (1,1,1,1)), Wait(after))
    spazzTrack2 = Sequence(ActorInterval(zapSuit, anim, startFrame=0, endFrame=19), Wait(after))
    return Sequence(Parallel(zapTrack, flashTrack, spazzTrack2, spazzTrack))

def zapCogPowerhouse(suit, anim, before, after, battle):
    zapSuit = suit.getZapActorPowerhouse()
    zapSuit.setBlend(frameBlend = base.wantSmoothAnims)
    suitPos = suit.getPos(battle)
    suitHpr = suit.getHpr(battle)
    zapSuit.setBin("fixed", 0)
    zapSuit.setDepthTest(False)
    zapSuit.setDepthWrite(False)
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    if suit.isSkeleton:
        suitBody = [suit]
    else:
        suitBody = [suit.find('**/body')]
    zapTrack = Sequence(SoundInterval(zapSfx, volume=0.6))
    # for bodyPart in suitBody:
    #     if bodyPart and not suit.isShadow and suit.dna.name != 'cbutcher':
    #         flashTrack.append(Sequence(Wait(before), Func(bodyPart.setColorScale, (0, 0, 0, 1)),
    #                               Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 0, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1)), Wait(.2),
    #                               Func(bodyPart.setColorScale, (1, 1, 1, 1))))
    spazzTrack = Sequence(ActorInterval(suit, anim, startTime=0))
    if suit.isShadow or suit.dna.name == 'cbutcher':
        flashTrack = Sequence(Func(insertZapSuit, suit, zapSuit, suit, Point3(0, 0, 0), Point3(0, 0, 0)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(removeZapSuitPowerhouse, suit, zapSuit), Wait(after))
    else:
        flashTrack = Sequence(Func(suit.setColorScale, (0,0,0,1)), Func(insertZapSuit, suit, zapSuit, suit, Point3(0, 0, 0), Point3(0, 0, 0)), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,0,1)), Wait(.2), Func(zapSuit.setColorScale, (1,1,1,1)), Wait(.2), Func(removeZapSuitPowerhouse, suit, zapSuit), Func(suit.setColorScale, (1,1,1,1)), Wait(after))
    spazzTrack2 = Sequence(ActorInterval(zapSuit, anim, startFrame=0, endFrame=19), Wait(after))
    return Sequence(Parallel(zapTrack, flashTrack, spazzTrack2, spazzTrack))

def spawnHeadExplosion(suit, battle):
    headParts = suit.getHeadParts()
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
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
    gears1Track = Sequence(ParticleInterval(smallGears, battle, worldRelative=False, duration=1.0, cleanup=True),name='gears1Track')
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
        (0.9, ParticleInterval(bigGearExplosion, battle, worldRelative=False, duration=1.0, cleanup=True)),
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