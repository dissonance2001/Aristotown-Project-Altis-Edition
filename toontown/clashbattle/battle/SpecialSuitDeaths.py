from panda3d.core import *
from toontown.chat.constants.ChatGlobals import CFSpeech
from direct.interval.IntervalGlobal import *
import random

from toontown.battle import BattleParticles, MovieUtil
from toontown.battle.statuses.StatusEffectEnums import StatusEffectEnum
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.cutscene.repository.CutsceneKeyEnum import CutsceneKeyEnum
from toontown.toonbase import TTLocalizer
from toontown.cutscene.repository.CutsceneLoader import CutsceneLoader

PNT3_NEARZERO = Point3(0.01, 0.01, 0.01)
PNT3_ZERO = Point3(0.0, 0.0, 0.0)
PNT3_ONE = Point3(1.0, 1.0, 1.0)


def getSpecialDeathTrack(suit, toon, battle):
    deathTrack = None
    if suit.style.name == 'rainmake':
        deathTrack = makeRainmakerDeath(suit, battle)
    elif suit.style.name in TTLocalizer.SuitFleeDeathDialogue:
        deathTrack = makeFleeDeath(suit, battle)
    elif suit.style.name == 'count':
        deathTrack = makeErclaimDeath(suit, toon, battle)
    elif suit.style.name == 'erfit':
        deathTrack = makeErfitDeath(suit, battle)
    elif suit.style.name == 'hroller':
        deathTrack = makeHighRollerDeath(suit, battle)
    elif suit.style.name == 'prethink':
        deathTrack = makePrethinkerDeath(suit, battle)
    elif suit.style.name == 'whunter':
        deathTrack = makeWitchHunterDeath(suit, battle)
    elif suit.style.name == 'mslacker':
        deathTrack = makeMultislackerDeath(suit, battle)
    elif suit.style.name == 'mplayer':
        # Should we actually do this yet?
        effect = suit.getStatusEffectOfId(StatusEffectEnum.EFFECT_MANAGER_MAJOR_PLAYER)
        if effect:
            if not effect.hasRevived():
                return None
        deathTrack = makeMajorPlayerDeath(suit, battle)
    elif suit.style.name == 'pcrat':
        deathTrack = makePlutocratDeath(suit, battle)
    elif suit.style.name == 'chainsaw':
        deathTrack = makeChainsawConsultantDeath(suit, battle)
    elif suit.style.name == 'psetter':
        deathTrack = makePacesetterDeath(suit, battle)
    elif suit.style.name == 'dopr':
        deathTrack = makeDoprDeath(suit, battle)
    elif suit.style.name == 'dlao':
        deathTrack = makeLAADeath(battle)
    elif suit.style.name == 'derrman':
        deathTrack = makeDerrickmanDeath(battle)
    elif suit.healthColored or suit.style.name == 'hrollerc':
        deathTrack = makeHealthColoredDeath(suit, toon, battle)
    elif suit.getStatusEffectOfId(StatusEffectEnum.EFFECT_SUIT_FROZEN) or getattr(suit, 'movieFrozen', False):
        deathTrack = makeFrozenDeath(suit, battle)
    if not deathTrack:
        return None

    return Sequence(Func(suit.loop, 'neutral'), deathTrack)


def makeFleeDeath(suit, battle):
    suitFleeDialogue = TTLocalizer.SuitFleeDeathDialogue[suit.dna.name]
    chat = suitFleeDialogue[suit.doId % len(suitFleeDialogue)]
    camSeq = Func(base.camera.setPosHpr, suit, 0, 22, 10, 180, -18, 0) if battle.hasLocalToon() else Sequence()
    return Sequence(
        camSeq,
        Func(suit.setChatAbsolute, chat, CFSpeech),
        Wait(4.0),
        suit.beginSupaFlyMove(suit.getPos(), 0, 'flyOut')
    )


def makeRainmakerDeath(suit, battle):
    deathTrack = makeFleeDeath(suit, battle)
    return Parallel(deathTrack, Func(base.musicMgr.crossfadeIntoMusic, 'None', 1.5))


def makeHealthColoredDeath(suit, toon, battle):
    suitTrack = Sequence()

    deathSound = base.loader.loadSfx('phase_11/audio/sfx/laser_cog_death.ogg')
    suitTrack.append(Parallel(SoundInterval(deathSound, duration=1.2, startTime=0, volume=1),
                              LerpScaleInterval(suit, 0.5, PNT3_NEARZERO),
                              LerpColorScaleInterval(suit, 0.5, (0, 0, 0, 0))))
    return suitTrack


def makeFrozenDeath(suit, battle):
    # take dead frozen suit from extraArgs and make their death anim

    iceModel = base.loader.loadModel('cosmetics/hat/models/cc_m_acc_hat_over_icecube')
    frozenDeathTrack = ParallelEndTogether()
    # make freezing animation
    actorTrack = ActorInterval(suit, 'large-zap', duration=1.0, playRate=0.07, startFrame=0, endFrame=1, name='freeze-actor')
    headTrack = Sequence(name='freeze-head')
    if suit.specialHead:
        headTrack.append(ActorInterval(suit.specialHead, 'grunt', endFrame=5))
        headTrack.append(Func(suit.specialHead.pose, 'grunt', 5))
    iceNode = suit.attachNewNode('iceNode')
    iceModel.copyTo(iceNode)
    iceNode.setTransparency(True)
    iceNode.setColorScale(1, 1, 1, 0)
    height = suit.height / 7
    scale = height / 2
    if suit.style.body == 'c':
        scale = height / 1.5
    elif suit.style.body == 'b':
        scale = height / 2.5
    iceNode.setScale(.3, .3, height)
    iceNode.setHpr(random.randrange(-15, 15), random.randrange(-5, 5), random.randrange(-5, 5))
    iceTrack = Parallel(
        LerpScaleInterval(iceNode, 1.0, (scale / .8, scale, height)),
        LerpColorScaleInterval(iceNode, 1.0, (1, 1, 1, 1)),
        name='freeze-icecube'
    )
    # ice cube shaking
    suitPos, (suitH, _, _) = battle.getActorPosHpr(suit)
    part = suit.getGeomNode()
    explosionPoint = Point3(suitPos.getX(), suitPos.getY(), suitPos.getZ() + suit.height / 1.6)
    trembleTrack = Sequence(name='freeze-tremble')
    for _ in range(50):
        randOffset = (random.uniform(-.1, .1), random.uniform(-.1, .1), random.uniform(-.1, .1))
        trembleTrack.append(LerpPosInterval(suit, .01, suitPos + randOffset))
    # particles
    smallGearExplosion = BattleParticles.createParticleEffect('GearExplosion', numParticles=10)
    bigGearExplosion = BattleParticles.createParticleEffect('BigGearExplosion', numParticles=30)
    icyExplosion = BattleParticles.createParticleEffect(file='snowflakeBurst')
    snowyExplosion = BattleParticles.createParticleEffect(file='snowyExplosion')
    snowyExplosion.setScale(suit.scale)
    snowyExplosion.setColorScaleOff(1)
    snowyExplosion.getParticlesNamed('particles-1').emitter.setOffsetForce(Vec3(0.0000, 0.0000, 7.0000 + suit.height))

    smallGearExplosion.setPos(explosionPoint)
    bigGearExplosion.setPos(explosionPoint)
    icyExplosion.setPos(explosionPoint)
    snowyExplosion.setPos(explosionPoint)
    smallGearExplosion.setDepthWrite(False)
    bigGearExplosion.setDepthWrite(False)
    icyExplosion.setDepthWrite(False)
    snowyExplosion.setDepthWrite(False)
    particleTrack = Parallel(
        ParticleInterval(smallGearExplosion, battle, worldRelative=False, duration=1.2, cleanup=True),
        ParticleInterval(bigGearExplosion, battle, worldRelative=False, duration=1.0, cleanup=True),
        ParticleInterval(icyExplosion, battle, worldRelative=False, duration=1.1, cleanup=True),
        ParticleInterval(snowyExplosion, battle, worldRelative=False, duration=2, softStopT=-1.4, cleanup=True),
        name='freeze-particles'
    )
    # boom!!!
    sfx = base.loader.loadSfx('phase_10/audio/sfx/SA_shatter.ogg')
    sfxTrack = SoundInterval(sfx)

    track = Sequence(
        headTrack,
        ParallelEndTogether(
            actorTrack,
            LerpColorScaleInterval(part, 1.0, (.75, 1.0, 1.0, 1.0)),
            iceTrack
        ),
        Wait(0.3),
        trembleTrack,
        Parallel(
            Func(MovieUtil.removeSuit, suit, name='remove-death-suit'),
            particleTrack,
            Func(iceNode.removeNode),
            MovieUtil.createKapowExplosionTrack(battle, explosionPoint=explosionPoint, scale=1.5)
        )
    )
    frozenDeathTrack.append(track)
    return Parallel(sfxTrack, frozenDeathTrack)


def makeErfitDeath(suit, battle):
    suitTrack = Sequence()

    def hideSuit():
        actorNode = suit.find('**/__Actor_modelRoot')
        actorNode.hide()

    deathSfx = loader.loadSfx('phase_13/audio/sfx/april_toons/erfit_defeat.ogg')
    erfitDialog = TTLocalizer.ErfitDefeatDialog
    # erfitDialog = TTLocalizer.ErfitDefeatDialogSelf

    removeEffectFunc = Sequence()

    reviveEffect = suit.getVisualEffectOfId(VisualEffectEnum.ERFIT_REVIVE)
    if reviveEffect:
        removeEffectFunc = Func(reviveEffect.stopDisplaySeqs)

    if len(erfitDialog) > 1:
        suitTrack = Track(
            (0.0, Func(suit.loop, 'neutral')),
            (0.0, removeEffectFunc),
            (0.5, Func(base.camera.setPosHpr, suit, 0, 22, 10, 180, -18, 0)),
            (1.5, Func(suit.setChatAbsolute, erfitDialog[0], CFSpeech)),
            (4.0, Func(suit.setChatAbsolute, erfitDialog[1], CFSpeech)),
            (6.5, Func(suit.setChatAbsolute, erfitDialog[2], CFSpeech)),
            (9.0, Func(suit.setChatAbsolute, erfitDialog[3], CFSpeech)),
            (11.5, Func(base.playSfx, deathSfx)),
            (11.5, Sequence(Func(suit.clearChat), Func(suit.hide))),
            (11.5, Func(base.cr.chatManager.sendSystemMessageLocally, "", TTLocalizer.ErfitLeftGame)),
            (11.5, Wait(1.5)),
            (11.5, Func(base.musicMgr.stopMusic, 'erfit_supreme')),
        )
    else:
        suitTrack = Track(
            (0.0, Func(suit.loop, 'neutral')),
            (0.5, Func(base.camera.setPosHpr, suit, 0, 22, 10, 180, -18, 0)),
            (1.5, Func(suit.setChatAbsolute, erfitDialog, CFSpeech)),
            (3.5, Func(base.playSfx, deathSfx)),
            (3.5, Sequence(Func(suit.clearChat), Func(suit.hide))),
            (3.5, Func(base.cr.chatManager.sendSystemMessageLocally, "", TTLocalizer.ErfitLeftGame)),
            (3.5, Func(base.musicMgr.stopMusic, 'erfit_supreme')),
        )
    return Sequence(suitTrack, Wait(0.5))


def makeErclaimDeath(suit, toon, battle):
    suitTrack = Sequence()

    batNode = render.attachNewNode('batNode')
    batNode.setPos(suit, 0, 0, 0)

    if hasattr(battle, 'bossCogId'):
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
            (4.0, Sequence(Func(suit.clearChat), Func(setSuitPartTransparency),
                           LerpColorScaleInterval(suit, 1.0, (1, 1, 1, 0)))),
            (7.0, Func(batNode.removeNode))
        )

        # If Count has been assigned defeat dialog, use it. (This happens when his intro is made.)
        if hasattr(suit, 'dialogList'):
            countDialog = suit.dialogList
        else:
            countDialog = random.choice(TTLocalizer.CountDefeatDialogDefaults)

        suitTrack = Track(
            (0.0, Func(suit.loop, 'neutral')),
            (0.5, Func(base.camera.setPosHpr, suit, 0, 22, 10, 180, -18, 0)),
            (1.0, Func(suit.setChatAbsolute, countDialog[0], CFSpeech)),
            (5.0, Func(suit.setChatAbsolute, countDialog[1], CFSpeech)),
            (9.0, Func(suit.setChatAbsolute, countDialog[2], CFSpeech)),
            (13.0, Func(suit.setChatAbsolute, countDialog[3], CFSpeech)),
            (13.0, partTrack)
        )
        return suitTrack
    else:
        # Street Count death
        BattleParticles.loadParticles()
        particleEffectLight = BattleParticles.createParticleEffect('Bats')
        partTrackLight = ParticleInterval(particleEffectLight, batNode, 0, duration=2, cleanup=True, softStopT=-1.0)
        particle = particleEffectLight.getParticlesNamed('particles-1')
        particle.setBirthRate(0.0500)
        particle.setLitterSize(1)

        particleEffectMedium = BattleParticles.createParticleEffect('Bats')
        partTrackMedium = ParticleInterval(particleEffectMedium, batNode, 0, duration=3, cleanup=True,
                                           softStopT=-1.0)
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
            (2.0, partTrackHeavy),
            (3.0, Sequence(Func(suit.clearChat), Func(setSuitPartTransparency),
                           LerpColorScaleInterval(suit, 1.0, (1, 1, 1, 0)))),
            (5.0, Func(batNode.removeNode))
        )

        countDialog = random.choice(TTLocalizer.CountDefeatDialogStreet)
        if base.localAvatar in battle.toons:
            suitTrack = Track(
                (0.0, Func(suit.loop, 'neutral')),
                (0.5, Func(base.camera.setPosHpr, suit, 0, 22, 10, 180, -18, 0)),
                (1.0, Func(suit.setChatAbsolute, countDialog, CFSpeech)),
                (3.0, partTrack)
            )
        else:
            suitTrack = Track(
                (0.0, Func(suit.loop, 'neutral')),
                (1.0, Func(suit.setChatAbsolute, countDialog, CFSpeech)),
                (3.0, partTrack)
            )
        return Sequence(suitTrack, Wait(0.5))


def makeHighRollerDeath(suit, battle):
    def reallyToggleGui(state):
        if state:
            if aspect2d.isHidden():
                aspect2d.show()
        else:
            if not aspect2d.isHidden():
                aspect2d.hide()
        base.guiToggleDisabled = not state

    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    # Find the other suits that aren't dead yet.
    otherSuits = [av for av in battle.activeSuits if not getattr(av, 'deadOrAboutToBe', False) and av is not suit]

    cutsceneTrack = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.HighRoller_Death,
        toons=battle.activeToons[:],
        localToon=base.localAvatar if base.localAvatar in battle.activeToons else None,
        hroller=suit,
        otherSuits=otherSuits,
        battle=battle,
        instance=battle.instance,
    ).buildCutscene()

    return Parallel(
        Func(base.musicMgr.crossfadeIntoMusic, battle.instance.endingMusic, duration=1.0, delay=0.0, looping=0,
             matchTime=False, volume=1.0, musicCode='highroller_end'),
        Func(base.localAvatar.hideLaffMeters, True),
        Func(reallyToggleGui, False),
        battle.instance.getEnvironment().makeExitPhaseSequence(),
        Sequence(cutsceneTrack, Func(base.localAvatar.hideLaffMeters, False), Func(reallyToggleGui, True))
    )


def makeDoprDeath(suit, battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    # Load cutscene
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.Dopr_Death,
        toons=battle.activeToons[:],
        suits=[suit]
    )

    return Parallel(
        Func(base.musicMgr.crossfadeIntoMusic, battle.instance.preloadedDeathMusic, duration=1.0, delay=0.0, looping=0,
             matchTime=False, volume=0.9, musicCode=battle.instance.deathMusic),
        cutsceneLoader.buildCutscene()
    )


def makeLAADeath(battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    suits = []
    for suitId in base.instanceSuits:
        suit = base.cr.doId2do.get(suitId)
        if not suit:
            continue
        if suit.style.name == 'dlao':
            suits.insert(0, suit)
        elif not getattr(suit, 'deadOrAboutToBe', False):
            suits.append(suit)

    # Load the cutscene
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.Dola_Death,
        toons=battle.activeToons[:],
        suits=suits,
        battle=battle
    )

    return Parallel(
        Func(base.musicMgr.crossfadeIntoMusic, battle.instance.preloadedDeathMusic, duration=1.0, delay=0.0, looping=0,
             matchTime=False, volume=0.9, musicCode=battle.instance.deathMusic),
        cutsceneLoader.buildCutscene()
    )


def makeDerrickmanDeath(battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    activeSuits = []
    for suit in battle.activeSuits:
        if suit.style.name == 'derrman':
            activeSuits.insert(0, suit)
        elif not getattr(suit, 'deadOrAboutToBe', False):
            activeSuits.append(suit)

    # Load the cutscene
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.Derrickman_Death,
        battle=battle,
        toons=battle.activeToons[:],
        suits=activeSuits[1:],
        derrickman=activeSuits[0],
        shopOwnerNpc=battle.instance.shopOwnerNpc
    )

    track = Parallel(
        cutsceneLoader.buildCutscene(),
        Func(base.musicMgr.crossfadeIntoMusic, base.instance.deathMusic, duration=0.0, delay=0.0, looping=0, matchTime=False, volume=1.0),
    )
    return track


def makePrethinkerDeath(suit, battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    # set cutscene dict
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.Prethinker_Death,
        toons=battle.activeToons[:],
        suit=suit,
        battle=battle,
        doorBHinge=battle.instance.doorBHinge,
        doorBReferenceNode=battle.instance.doorBReferenceNode,
    )

    # Supplemental brain blast sequence
    # Increase pulse rate and make brain red
    brainBlastTiming = 18.326  # Update this if cutscene gets updated
    redTrack = suit.specialHead.makeBrainRedTrack()
    preBrainBlastTrack = Sequence(
        Wait(brainBlastTiming - 8.0),
        Func(suit.specialHead.setBrainPulseSpeed, 2.0),
        redTrack,
        Wait(4.0),
        Func(suit.specialHead.setBrainPulseSpeed, 4.0),
    )

    # Now we explode all other suits when brain blast happens
    # Add all suits that haven't died yet
    suitsToExplode = [av for av in battle.activeSuits if not getattr(av, 'deadOrAboutToBe', False) and av is not suit]
    explodeTrack = Parallel()
    seqFinishTrack = Parallel()
    for av in suitsToExplode:
        seq = MovieUtil.createSuitDeathTrack(av, None, battle, affectToons=False)
        explodeTrack.append(Sequence(Func(seq.play), Func(seq.setT, 5.3)))
        seqFinishTrack.append(Func(seq.finish))
    explodeTrack = Sequence(Wait(brainBlastTiming), explodeTrack)

    # Music change track
    musicTrack = Sequence(
        Wait(brainBlastTiming - 1.25),
        Func(base.musicMgr.crossfadeIntoMusic, 'None', 1.0),
        Wait(1.25),
        Func(base.musicMgr.playMusic, 'prethinker_end')
    )

    track = Parallel(Sequence(cutsceneLoader.buildCutscene(), seqFinishTrack), preBrainBlastTrack, explodeTrack, musicTrack)
    return track


def makeWitchHunterDeath(suit, battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    from toontown.suit import DistributedSuitBase, SuitDNA

    nextLocalDoId = -2450

    # Load the cutscene in.
    cutsceneSuits = [suit]
    extraSuits = []
    ranGen = random.Random(suit.doId)
    possibleSuits = ['bw', 'le', 'sd', 'br', 'sh', 'ad']
    levelRange = [8, 9, 10, 11, 12]
    for _ in range(2):
        newSuit = DistributedSuitBase.DistributedSuitBase(base.cr)
        d = SuitDNA.SuitDNA()
        newSuitType = ranGen.choice(possibleSuits)
        d.newSuit(name=newSuitType)
        newSuitLevel = random.choice(levelRange)
        newSuit.setDNA(d)
        newSuit.dna = d
        newSuit.doId = nextLocalDoId
        nextLocalDoId -= 1
        newSuit.generate()
        newSuit.announceGenerate()
        newSuit.loop('neutral', 0)
        newSuit.getActualLevel = lambda: newSuitLevel
        nameInfo = newSuit.createNameInfo()
        newSuit.setDisplayName(nameInfo)
        newSuit.setPickable(0)
        newSuit.reparentTo(render)
        newSuit.stash()
        cutsceneSuits.append(newSuit)
        extraSuits.append(newSuit)

    # set cutscene dict
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.Witchhunter_Death,
        toons=battle.activeToons[:],
        suits=cutsceneSuits,
        battle=battle
    )

    def cleanupSuits():
        for extraSuit in extraSuits:
            extraSuit.disable()
            extraSuit.delete()
            del extraSuit

    # Add flyout sequences for all suits in the fight
    flyOutTrack = Parallel()
    # Add all suits that haven't died yet, then append self
    suitsToFlyOut = [av for av in battle.activeSuits if not getattr(av, 'deadOrAboutToBe', False) and av is not suit]
    suitsToFlyOut.append(suit)

    for i, av in enumerate(suitsToFlyOut):
        destPos = Point3(0, 0, 0)
        flyOutTrack.append(Sequence(Wait(45.34 + (0.2 * i)), av.beginSupaFlyMove(destPos, 0, 'flyOut', flyOutBasedOnCurrentPos=True)))

    return Sequence(
        Parallel(
            cutsceneLoader.buildCutscene(),
            Func(base.musicMgr.crossfadeIntoMusic, 'None', 2.5),
            Sequence(
                Wait(18.5),
                Func(base.musicMgr.playMusic, 'witchhunter_end')
            ),
            flyOutTrack,
        ),
        Func(base.musicMgr.playMusic, 'witchhunter_battle', looping=1),
        Func(cleanupSuits)
    )


def makeMultislackerDeath(suit, battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    # Load the cutscene in.
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.Multislacker_Death,
        multislacker=suit,
        battle=battle
    )
    return Parallel(
        Func(base.musicMgr.crossfadeIntoMusic, 'multislacker_end', duration=1.0, delay=0.0, looping=0, matchTime=False, volume=1.0),
        cutsceneLoader.buildCutscene()
    )


def makeMajorPlayerDeath(suit, battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    otherSuits = battle.activeSuits[:]
    if suit in otherSuits:
        otherSuits.remove(suit)

    cutsceneTrack = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.MajorPlayer_Death,
        toons=battle.activeToons[:],
        mplayer=suit,
        otherSuits=otherSuits,
        battle=battle,
        instance=battle.instance,
    ).buildCutscene()
    return Parallel(
        Func(base.musicMgr.crossfadeIntoMusic, battle.instance.endingMusic, duration=1.0, delay=0.0, looping=0, matchTime=False, volume=1.0, musicCode='majorplayer_end'),
        cutsceneTrack,
    )


def makePlutocratDeath(suit, battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    # Add all suits that haven't died yet, then insert self at front
    cutsceneSuits = [av for av in battle.activeSuits if not getattr(av, 'deadOrAboutToBe', False) and av is not suit]
    cutsceneSuits.insert(0, suit)

    # set cutscene dict
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.Plutocrat_Death,
        suits=cutsceneSuits,
        battle=battle
    )
    cutscene = cutsceneLoader.buildCutscene()

    return Parallel(
        Sequence(
            Wait(12.0),
            Func(base.musicMgr.crossfadeIntoMusic, 'plutocrat_end', duration=1.0, delay=0.0, looping=1, matchTime=False, volume=1.0)
        ),
        cutscene
    )


def makeChainsawConsultantDeath(suit, battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    # Find the other suits that aren't dead yet.
    otherSuits = [av for av in battle.activeSuits if not getattr(av, 'deadOrAboutToBe', False) and av is not suit]

    # Load cutscene in.
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.ChainsawConsultant_Death,
        toons=battle.activeToons[:],
        chainsaw=suit,
        otherSuits=otherSuits,
        battle=battle
    )

    # Unlure all the suits before we start
    unlureTrack = Parallel()
    for suit in otherSuits:
        if suit.isLured:
            unlureTrack.append(MovieUtil.createSuitUnlureTrack(suit, battle))

    from toontown.battle.gui.special.ChainsawMeterGUI import ChainsawMeterGUI
    return Sequence(
        unlureTrack,
        Parallel(
            cutsceneLoader.buildCutscene(),
            Func(messenger.send, ChainsawMeterGUI.getShatterEvent()),
        ),
    )


def makePacesetterDeath(suit, battle):
    # If we can't find the instance, just do generic death
    if not hasattr(battle, 'instance'):
        return

    # Load in cutscene.
    cutsceneLoader = CutsceneLoader.createLoader(
        key=CutsceneKeyEnum.Pacesetter_Death,
        pacesetter=suit,
        battle=battle
    )

    def getSpeedTrack() -> Sequence:
        bml = battle.battleMusicListener
        newSpeed = 0.001

        if bml.storedMusic is None:
            bml.lookForSuits(battle.suits, None)

        slowdownDuration = 2.0
        return Sequence(
            Func(bml.changePlaybackSpeed, newSpeed, duration=slowdownDuration),
            Wait(slowdownDuration),
            Func(bml.stopMusic),
            Func(bml.changePlaybackSpeed, 1.0, 0.0),
        )

    return Sequence(
        getSpeedTrack(),
        cutsceneLoader.buildCutscene(),
    )
