from direct.interval.IntervalGlobal import *
from direct.showbase.PythonUtil import lerp

from toontown.audio.IsolatedSoundInterval import IsolatedSoundInterval
from toontown.battle.BattleProps import *
from toontown.battle import BattleParticles, BattleSounds, SuitBattleGlobals
from otp import *
from panda3d.core import *

from toontown.battle.movielistener.BattleMovieListenerEnum import BMLE
from toontown.battle.statuses.StatusEffectEnums import StatusEffectEnum
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.battle.SpecialSuitDeaths import getSpecialDeathTrack
from toontown.suit.Suit import loadDialog
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.suit import SuitTimings, SuitHealthMeter
from toontown.suit.SuitDefinitionsBase import suitGetOverrideDeaths, suitGetExtendMovieTime
from toontown.utils.DirectNotifyCategory import getNotify

notify = getNotify('MovieUtil')
SUIT_LOSE_DURATION = 6.0
SUIT_LURE_DISTANCE = 2.6
SUIT_LURE_DOLLAR_DISTANCE = 5.1
SUIT_EXTRA_REACH_DISTANCE = 0.9
SUIT_EXTRA_RAKE_DISTANCE = 1.1
SUIT_TRAP_DISTANCE = 2.6
SUIT_TRAP_RAKE_DISTANCE = 4.5
SUIT_TRAP_MARBLES_DISTANCE = 3.7
SUIT_TRAP_TNT_DISTANCE = 5.1
# At what level do Zap gags begin to show the skelecog? (Actually 6, 0-based levels)
SUIT_ZAP_SUIT_THRESHOLD_LEVEL = 5
PNT3_NEARZERO = Point3(0.01, 0.01, 0.01)
PNT3_ZERO = Point3(0.0, 0.0, 0.0)
PNT3_ONE = Point3(1.0, 1.0, 1.0)

OVERRIDE_SPECIAL_DEATHS = SuitBattleGlobals.OVERRIDE_SPECIAL_DEATHS
DEATH_EXTEND_MOVIE_TIME = SuitBattleGlobals.DEATH_EXTEND_MOVIE_TIME

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
    if prop.isEmpty() == 1 or prop is None:
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


def insertDeathSuitWithoutDetach(suit, deathSuit, battle = None, pos = None, hpr = None):
    holdParent = suit.getParent()
    if suit.getVirtual():
        virtualize(deathSuit)
    if deathSuit is not None and not deathSuit.isEmpty():
        if holdParent and 0:
            deathSuit.reparentTo(holdParent)
        else:
            deathSuit.reparentTo(render)
        if battle is not None and pos is not None:
            deathSuit.setPos(battle, pos)
        if battle is not None and hpr is not None:
            deathSuit.setHpr(battle, hpr)
    return


def insertZapSuit(suit, zapSuit, battle = None, pos = None, hpr = None):
    holdParent = suit.getParent()
    if suit.getVirtual():
        virtualize(zapSuit)
    if zapSuit is not None and not zapSuit.isEmpty():
        if holdParent and 0:
            zapSuit.reparentTo(holdParent)
        else:
            zapSuit.reparentTo(render)
        if battle is not None and pos is not None:
            zapSuit.setPos(battle, pos)
        if battle is not None and hpr is not None:
            zapSuit.setHpr(battle, hpr)
    return


def removeSuit(suit):
    if not suit.isEmpty():
        suit.detachNode()


def removeZapSuit(suit, zapSuit):
    if not zapSuit.isEmpty():
        zapSuit.detachNode()
        suit.cleanupZapActor()


def virtualize(deathsuit):
    actorNode = deathsuit.find('**/__Actor_modelRoot')
    actorCollection = actorNode.findAllMatches('*')
    for thing in actorCollection:
        if thing.getName() not in ('joint_attachMeter', 'joint_nameTag', 'def_nameTag'):
            thing.setColorScale(1.0, 0.0, 0.0, 1.0)
            thing.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
            thing.setDepthWrite(False)
            thing.setBin('fixed', 1)


def createTrainTrackAppearTrack(dyingSuit, toon, battle):
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


def headExplodeTrack(suit, battle):
    headParts = suit.getHeadParts()
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    suitTrack.append(Wait(0.15))
    explodeTrack = Parallel()
    for part in headParts:
        explodeTrack.append(Func(part.detachNode))
    suitTrack.append(explodeTrack)
    deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
    deathSoundTrack = Sequence(IsolatedSoundInterval(deathSound, volume=0.5))
    BattleParticles.loadParticles()
    smallGears = BattleParticles.createParticleEffect(file='gearExplosionSmall')
    singleGear = BattleParticles.createParticleEffect('GearExplosion', numParticles=1)
    smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
    bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
    gearPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height + 1)
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
        (0.9, ParticleInterval(bigGearExplosion, battle, worldRelative=0, duration=0.6, cleanup=True)), name='gears2MTrack'
    )

    return Parallel(suitTrack, explosionTrack, deathSoundTrack, gears1Track, gears2MTrack)


def suitDisintegrateTrack(suit, battle):
    # Make a clip plane to erase the cog as we vaporize it
    
    plane = Plane(0, 0, 1, 0)  # Create the plane with a surface normal facing straight up, origin at 0
    planeNode = PlaneNode(f"suitClipPlane-{suit.id}", plane)
    planeNodePath = suit.attachNewNode(planeNode)
    ashNodePath = suit.attachNewNode(f'ashNodePath-{suit.id}')
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
    battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, deathHolderTrack, suit=suit)
    suitTrack = Parallel(
        Func(ashEffect.start, parent=ashNodePath, renderParent=ashNodePath),
        LerpColorScaleInterval(suit, dDisintegrate / 2.0, Vec4(0, 0, 0, 1)),
        LerpPosInterval(planeNodePath, dDisintegrate, planeEndPos, startPos = planeStartPos, blendType = 'easeInOut'), # Clip plane moving up
        LerpPosInterval(ashNodePath, dDisintegrate, ashNodeEndPosCallback, blendType = 'easeInOut'), # Clip plane moving up
        Func(ashPile.wrtReparentTo, battle),
        Func(ashNodePath.wrtReparentTo, battle),
        Func(ashPile.show),
        LerpScaleInterval(ashPile, dDisintegrate, suit.getScale() * 1.5, startScale=PNT3_NEARZERO)
    )  # Ash pile growing
    hideAshPile = Sequence(
        LerpScaleInterval(ashPile, dDisappear, PNT3_NEARZERO, blendType='easeIn'),
        Func(ashPile.detachNode)
    )

    finalTrack = Sequence(suitTrack, Func(BattleParticles.cleanupSystem, ashEffect, 2), Wait(1.2), Parallel(hideAshPile, Func(suit.hide)))
    battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, finalTrack, suit=suit)
    deathHolderTrack.append(finalTrack)
    return deathHolderTrack


def getSpecialSuitRevive(suit, toon, battle):
    suitTrack = Sequence()
    if suit.style.name == 'count':
        def inInstance():
            return hasattr(battle, 'bossCogId')
        trapProp = globalPropPool.getProp('quicksand')
        trapProp.setColor(Vec4(0.1, 0.1, 1.0, 1))
        trapProp.setHpr(Point3(300, 0, 0))
        trapProp.setScale(0.01)
        trapProp.setPos(suit.getPos(render))
        if inInstance():
            trapProp.wrtReparentTo(render)
        else:
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
            if suit.isSoaked:
                applyVisualEffect(suit, VisualEffectEnum.SOAKED)

        def suitNeutral():
            suit.loop('neutral')
            if suit.specialHead:
                suit.specialHead.loopNeutral()

        def suitInbetweens():
            suit.setSkelecog(1)
            suit.healthBar.show()
            soakSuit()
            suit.setHp(suit.getMaxHp())
            suit.wrtReparentTo(battle)
            suit.initializeDropShadow()

        def createSuitMoveIval(suit, destPos, hole):
            dur = suit.getDuration('landing')
            fr = suit.getFrameRate('landing')
            landingDur = dur
            totalDur = 7.3
            animTimeInAir = totalDur - dur
            flyingDur = animTimeInAir
            dmgMult = SuitBattleGlobals.REVIVE_ATTRIBUTES['count'][1]
            moveIval = Sequence(
                Func(suit.pose, 'landing', 0),
                    Parallel(
                        Sequence(
                            ProjectileInterval(suit, duration=flyingDur, endPos=destPos, gravityMult=0.125),
                            ActorInterval(suit, 'landing')
                        ),
                        Sequence(
                            Wait(0.5),
                            Func(suit.showHpString, text=TTLocalizer.SuitAttackDmgMult % str(dmgMult), color=(0.45, 0.45, 1.0, 1.0))
                        ) if dmgMult != 1.00 else Wait(0.5)
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
        if inInstance():
            suit.reparentTo(battle)
        else:
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
            Func(suit.specialHead.play, 'death'),
            ActorInterval(suit, 'flail'),
            ActorInterval(suit, 'flail', startTime=1.1)
        )
        fallingSoundTrack = Sequence(
            Wait(0.7),
            SoundInterval(BattleSounds.globalBattleSoundCache.getSound('TL_quicksand.ogg'), node=suit, duration=2.5),
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
    elif suit.style.name == 'erfit':
        # actual revive handled in ErfitRevive.py
        return Sequence(Wait(0.1))  # sequence we return needs to have substance
    else:
        return None


def createSuitReviveTrack(suit, toon, battle):
    suitTrack = Sequence()
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    specialRevive = getSpecialSuitRevive(suit, toon, battle)
    if suit.stunStars:
        suitTrack.append(Func(suit.cleanupStunStars))
    if not specialRevive:
        if suit.specialHead:
            suitTrack.append(Func(suit.specialHead.play, 'death'))

        if suit.isSkeleton:
            suitTrack.append(ActorInterval(suit, 'skeleton-lose', duration=SUIT_LOSE_DURATION))
        else:
            suitTrack.append(ActorInterval(suit, 'lose', duration=SUIT_LOSE_DURATION))
        suitTrack.append(Func(suit.setSkelecog, 1, name='remove-death-suit'))
        if suit.afterReviveDamage[1] != 0:
            suitTrack.append(Func(suit.setMaxHp, suit.afterReviveDamage[1]))
            suitTrack.append(Func(suit.setHp, suit.afterReviveDamage[0]))
        else:
            suitTrack.append(Func(suit.setHp, suit.getMaxHp()))
        suitTrack.append(Func(suit.updateHealthMeterMode, SuitHealthMeter.MODE_BATTLE))
        suitTrack.append(Func(suit.updateHealthBar, 0, forceUpdate=1))

        def soakSuit():
            if suit.isSoaked:
                applyVisualEffect(suit, VisualEffectEnum.SOAKED)

        suitTrack.append(Func(soakSuit))
        suitTrack.append(Parallel(ActorInterval(suit, 'slip-forward'), Func(suit.showHpString, text=TTLocalizer.SuitAttackDmgMult % '1.50', color=(0.45, 0.45, 1.0, 1.0))))
        suitTrack.append(Func(suit.loop, 'neutral'))
        suitVoice = loadDialog(suit)
        spinningSound = suitVoice.getDeathSound(skelecog=suit.isSkeleton)
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        deathSoundTrack = Sequence(Wait(0.8), IsolatedSoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.15), IsolatedSoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.6), IsolatedSoundInterval(deathSound, volume=0.32))
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
            toonMTrack.append(Sequence(Wait(1.0), ActorInterval(mtoon, 'duck', endFrame = 83), ActorInterval(mtoon, 'duck', startFrame=43), Func(mtoon.loop, 'neutral')))

        return Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack)
    else:
        suitTrack.append(specialRevive)
        return suitTrack


def shouldOverrideSuitDeath(suit):
    return (
        suit.style.name in OVERRIDE_SPECIAL_DEATHS or  # manager bosses and the like
        suit.healthColored or  # virtual cogs
        suit.getStatusEffectOfId(StatusEffectEnum.EFFECT_SUIT_FROZEN) or getattr(suit, 'movieFrozen', False)  # dying with Frozen
    )


def createSuitDeathTrack(suit, toon, battle, headless = False, affectToons=True):
    deathParallelHolder = Parallel()
    suitTrack = Sequence()
    if suit is None or battle is None:
        return suitTrack
    battle.sendMovieEvent(BMLE.EVENT_SUIT_PREDIED, deathParallelHolder, suit=suit)
    suitPos, suitHpr = battle.getActorPosHpr(suit)
    specialDeath = getSpecialDeathTrack(suit, toon, battle)
    if suit.stunStars:
        suitTrack.append(Func(suit.cleanupStunStars))
    if specialDeath is None:
        if suit.specialHead:
            suitTrack.append(Func(suit.specialHead.play, 'death'))
        if suit.isSkeleton:
            suitTrack.append(ActorInterval(suit, 'skeleton-lose', duration=SUIT_LOSE_DURATION))
        else:
            suitTrack.append(ActorInterval(suit, 'lose', duration=SUIT_LOSE_DURATION))
        suitTrack.append(Func(removeSuit, suit, name='remove-death-suit'))
        suitVoice = loadDialog(suit)
        spinningSound = suitVoice.getDeathSound(skelecog=suit.isSkeleton)
        deathSound = base.loader.loadSfx('phase_3.5/audio/sfx/ENC_cogfall_apart.ogg')
        deathSoundTrack = Sequence(Wait(0.8), IsolatedSoundInterval(spinningSound, duration=1.2, startTime=1.5, volume=0.15), IsolatedSoundInterval(spinningSound, duration=3.0, startTime=0.6, volume=0.6), IsolatedSoundInterval(deathSound, volume=0.32))
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
        if affectToons:
            for mtoon in battle.toons:
                toonMTrack.append(Sequence(Wait(1.0), ActorInterval(mtoon, 'duck', endFrame = 83), ActorInterval(mtoon, 'duck', startFrame=43), Func(mtoon.loop, 'neutral')))

        retval = Sequence(Parallel(suitTrack, deathSoundTrack, gears1Track, gears2MTrack, toonMTrack))
    else:
        suitTrack.append(specialDeath)
        retval = suitTrack

    battle.sendMovieEvent(BMLE.EVENT_SUIT_DIED, retval, suit=suit)
    deathParallelHolder.append(retval)
    return deathParallelHolder


def createSuitDodgeMultitrack(tDodge, suit, leftSuits, rightSuits, activeSuits):
    # Adjust left and right suit lists to accommodate for the order of suits changing.
    lenSuits = len(activeSuits)
    suitIndex = activeSuits.index(suit)
    for si in range(0, suitIndex):
        asuit = activeSuits[si]
        if asuit in rightSuits:
            rightSuits.remove(asuit)
            leftSuits.append(asuit)

    if lenSuits > suitIndex + 1:
        for si in range(suitIndex + 1, lenSuits):
            asuit = activeSuits[si]
            if asuit in leftSuits:
                leftSuits.remove(asuit)
                rightSuits.append(asuit)

    # Now make the dodge tracks
    suitTracks = Parallel()
    sidestepSound = base.loader.loadSfx('phase_5/audio/sfx/ENC_cogjump_to_side.ogg')
    suitDodgeList, sidestepAnim = avatarDodge(leftSuits, rightSuits, 'sidestep-left', 'sidestep-right')
    for s in suitDodgeList:
        suitTracks.append(Sequence(Parallel(SoundInterval(sidestepSound, node=s, volume=0.6), s.actorInterval(sidestepAnim)), Func(s.loop, 'neutral')))

    suitTracks.append(Sequence(Parallel(SoundInterval(sidestepSound, node=suit, volume=0.6), suit.actorInterval(sidestepAnim)), Func(suit.loop, 'neutral')))
    suitTracks.append(Func(indicateMissed, suit))
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


def createSuitTeaseMultiTrack(suit, delay = 0.01, wantIndicateMiss=False):
    suitTrack = Sequence(Wait(delay), ActorInterval(suit, 'gag-miss'), Func(suit.loop, 'neutral'))
    indicateMissFunc = Func(indicateMissed, suit, 0.9) if wantIndicateMiss else Sequence()
    missedTrack = Sequence(Wait(delay + 0.2), indicateMissFunc)
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


def getToonTeleportOutInterval(toon):
    hole = toon.getHoleActor()
    hand = toon.getRightHand()
    delay = T_HOLE_LEAVES_HAND
    dur = T_TELEPORT_ANIM
    holeTrack = Sequence()
    holeTrack.append(Func(showProps, [hole], [hand]))
    holeTrack.append(Wait(0.5))
    holeTrack.append(Func(base.playSfx, toon.getSoundTeleport()))
    holeTrack.append(Wait(delay - 0.5))
    holeTrack.append(Func(hole.reparentTo, toon))
    holeAnimTrack = Sequence()
    holeAnimTrack.append(ActorInterval(hole, 'hole', duration=dur))
    holeAnimTrack.append(Func(hideProps, [hole]))
    runTrack = Sequence(ActorInterval(toon, 'teleport', duration=dur), Wait(T_HOLE_CLOSES), Func(toon.detachNode))
    return Parallel(runTrack, holeAnimTrack, holeTrack)


def getToonTeleportInInterval(toon):
    hole = toon.getHoleActor()
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


def getSuitRakeOffset(suit):
    suitName = suit.getStyleName()
    return SuitRakeOffsets.get(suitName, 0)


def startSparksIval(tntProp):
    tip = tntProp.find('**/joint_attachEmitter')
    sparks = BattleParticles.createParticleEffect(file='tnt')
    return Func(sparks.start, tip)


def indicateMissed(actor, duration = 1.1, scale = 0.7):
    actor.showHpString(TTLocalizer.AttackMissed, duration=duration, scale=scale)


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


def createSuitStunInterval(suit, before, after, cleanup=1, headAnim=1):
    p1 = Point3(0)
    p2 = Point3(0)
    stars = globalPropPool.getProp('stun')
    stars.setColor(1, 1, 1, 1)
    stars.adjustAllPriorities(100)
    if suit.isSkeleton:
        actorNode = suit.find('**/__Actor_modelRoot')
        head = actorNode.find('**/joint_head')
        if suit.style.body == 'a':
            zVal = max(0.0, p2[2] + 0.8)
        else:
            zVal = max(0.0, p2[2])
    else:
        head = suit.find('**/joint_head')
        if suit.style.body == 'c':
            zVal = max(0.0, p2[2] + 0.4)
        else:
            zVal = max(0.0, p2[2] + 0.8)
    head.calcTightBounds(p1, p2)

    def cleanupStunStars():
        if suit.stunStars:
            suit.cleanupStunStars()
        suit.stunStars = stars

    def headPlayStun(suit):
        # Split this off into its own function so that 2.0 cogs work properly
        if suit.specialHead:
            suit.specialHead.playStun()

    def headLoopNeutral(suit):
        # Also split this one off for the same reasons
        if suit.specialHead:
            suit.specialHead.loopNeutral()

    track = Sequence(Wait(before), Func(cleanupStunStars), Func(stars.reparentTo, head), Func(stars.setZ, zVal), Func(stars.loop, 'stun'))
    if suit.specialHead and headAnim:
        track.append(Func(headPlayStun, suit))
    if cleanup:
        track.append(Sequence(Wait(after), Func(suit.cleanupStunStars)))
        if suit.specialHead:
            track.append(Func(headLoopNeutral, suit))
    return track


def zapCog(suit, battle, zapLevel, anim, hideSkeleHead: bool = False):
    zapSfx = loader.loadSfx('phase_5/audio/sfx/AA_cog_shock.ogg')
    if suit.specialHead:
        # We picked frame 5 for the stun animation so it doesnt look too goofy
        zapTrack = Sequence(Func(suit.specialHead.pose, 'stun', 5), Func(base.playSfx, zapSfx))
    else:
        zapTrack = Sequence(Func(base.playSfx, zapSfx))
    # If our level is less than the threshold, we only play sfx, don't make a skelecog
    if zapLevel < SUIT_ZAP_SUIT_THRESHOLD_LEVEL:
        # Wait 0.8 to retain timing parity with attacks past the threshold
        zapTrack.append(Wait(0.8))
        if suit.specialHead:
            zapTrack.append(Func(suit.specialHead.loopNeutral))
        return zapTrack

    zapSuit = suit.getZapActor()
    if hideSkeleHead:
        suit.zapHeadActor.hide()
    zapSuit.setBlend(frameBlend=base.wantSmoothAnims)
    zapSuit.setBin("fixed", 0)
    zapSuit.setDepthTest(False)
    zapSuit.setDepthWrite(False)
    suitColScale = suit.getColorScale()
    flashTrack = Sequence(Func(suit.setColorScale, (0, 0, 0, 1)),
                          Func(lambda: insertZapSuit(suit, zapSuit, battle, suit.getPos(battle), suit.getHpr(battle))),
                          Func(zapSuitColorScale, zapSuit, (1, 1, 0, 1)), Wait(.2),
                          Func(zapSuitColorScale, zapSuit, (1, 1, 1, 1)), Wait(.2),
                          Func(zapSuitColorScale, zapSuit, (1, 1, 0, 1)), Wait(.2),
                          Func(zapSuitColorScale, zapSuit, (1, 1, 1, 1)), Wait(.2), Func(removeZapSuit, suit, zapSuit),
                          Func(suit.setColorScale, suitColScale))
    if suit.specialHead:
        flashTrack.append(Func(suit.specialHead.loopNeutral))
    spazzTrack = Func(zapSuitLoop, zapSuit, anim)
    return Parallel(zapTrack, flashTrack, spazzTrack)


def zapSuitColorScale(suit, color):
    if not suit.isEmpty():
        suit.setColorScale(color)
    else:
        pass


def zapSuitLoop(zapSuit, anim):
    if not zapSuit.isEmpty():
        zapSuit.loop(anim)
    else:
        pass


def calcAvgSuitPos(throw):
    battle = throw['battle']
    avgSuitPos = Point3(0, 0, 0)
    numTargets = len(throw['target'])
    for i in range(numTargets):
        suit = throw['target'][i]['suit']
        avgSuitPos += suit.getPos(battle)

    avgSuitPos /= numTargets
    return avgSuitPos


def createSuitUnlureTrack(suit, battle):
    suit.isLured = False
    resetPos, resetHpr = battle.getActorPosHpr(suit)
    moveDuration = 0.5
    walkTrack = Sequence(
        Func(suit.setHpr, battle, resetHpr),
        ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05),
        Func(battle.unlureSuit, suit),
        Func(suit.loop, 'neutral'),
        Wait(0.1),
    )
    moveTrack = LerpPosInterval(suit, moveDuration, resetPos, other=battle)
    return Parallel(walkTrack, moveTrack)


def getRailroadXScale(battle):
    return max(1.0, 1.0 + ((len(battle.activeSuits) - 4) * 0.275))


def getRailroadTextureXScale(battle):
    return max(1.0, 1.0 + ((len(battle.activeSuits) - 4) * 0.25))


def applyVisualEffect(av, effectEnum, extraArgs=None, useMovieApply=False):
    """
    Applies a visual effect to the target avId.
    Only for client movies; the server will apply
    the distributed visual effect to make it persistent
    """
    if av.hasCleanedUpBattle:
        return
    visualEffect = av.addVisualEffect(effectEnum, extraArgs=extraArgs)
    visualEffect.onMovieAdd(extraArgs=extraArgs)
    if not useMovieApply:
        av.reapplyAllVisualEffects()
        return
    return visualEffect.getApplyMovie()


def unapplyVisualEffect(av, effectEnum, wantApplyLock: bool = False):
    """
    Requests a visual effect to unapply on the target avId.
    Only for client movies.
    """
    if type(effectEnum) is not list:
        effectEnum = [effectEnum]
    for ee in effectEnum:
        av.requestUnapplyVisualEffect(ee, wantApplyLock)


def lureSuit(suit):
    suit.isLured = True
    return Func(applyVisualEffect, suit, VisualEffectEnum.LURED)


def unlureSuit(suit, battle):
    suit.isLured = False
    return Func(battle.unlureSuit, suit)


def createTurnToPointIval(node, point, duration, blendType='noBlend'):
    def getHprBetweenPoints(a: Point3, b: Point3) -> Point3:
        """
        Gets the HPR between two points.
        Assumption is that they're both relative to the same point.

        :param a: Point A in 3D space
        :param b: Point B in 3D space
        """
        # Get two temporary nodes.
        x, y, z = a
        tempA = render.attachNewNode('tempA')
        tempA.setPos(x, y, z)

        x, y, z = b
        tempB = render.attachNewNode('tempB')
        tempB.setPos(x, y, z)

        # Have one node face the other.
        tempA.lookAt(tempB)
        goalHpr = tempA.getHpr()

        # Cleanup.
        tempA.removeNode()
        tempB.removeNode()

        # We're done here.
        return goalHpr

    turnDict = {
        'startH': 0,
        'endH': 0
    }

    # Get the goal H for this node.
    def setupTurnDict():
        startH = node.getH(render) % 360
        a = node.getPos(render)
        # Sometimes we're passed in a function instead of a position (for proper turning to node)
        if callable(point):
            b = point()
        elif isinstance(point, tuple):
            b = LVecBase3f(*point)
        else:
            b = point
        endH, _, _ = getHprBetweenPoints(a, b)
        endH %= 360
        difference = startH - endH
        if difference > 180:
            startH -= 360
        elif difference < -180:
            endH -= 360
        turnDict['startH'] = startH
        turnDict['endH'] = endH

    def turnCallback(t):
        node.setH(render, lerp(turnDict['startH'], turnDict['endH'], t))

    # Create the sequence.
    track = Sequence(
        Func(setupTurnDict),
        LerpFunc(
            turnCallback,
            duration=duration,
            blendType=blendType
        ),
    )
    return track


# TODO: PUT THE LAWBOT ALTERNATES IN HERE @tubby
SuitRakeOffsets = {
    "gh": 1.4,
    "f": 1.0,
    "cc": 0.7,
    "tw": 1.3,
    "bf": 1.0,
    "sc": 0.8,
    "ym": 0.1,
    "mm": 0.05,
    "tm": 0.07,
    "nd": 0.07,
    "pp": 0.04,
    "bc": 0.36,
    "b": 0.41,
    "dt": 0.31,
    "ac": 0.39,
    "ds": 0.41,
    "hh": 0.8,
    "cr": 2.1,
    "tbc": 1.4,
    "hho": 1.4,
    "bs": 0.4,
    "sd": 1.02,
    "le": 1.3,
    "bw": 1.4,
    "br": 1.4,
    "nc": 0.6,
    "mb": 1.85,
    "ls": 1.4,
    "rb": 1.6,
    "shw": 1.85,
    "ms": 0.7,
    "tf": 0.75,
    "mi": 0.9,
    "mh": 1.3,
    "dl": 1.4
}
