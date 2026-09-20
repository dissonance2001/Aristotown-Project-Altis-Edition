import random

from direct.showbase.PythonUtil import lerp

from toontown.battle import MovieUtil
from toontown.battle.BattleProps import globalPropPool
from toontown.battle.attacks.base.AttackEnum import AttackEnum
from toontown.battle.visuals.VisualEffectEnums import VisualEffectEnum
from toontown.battle.BattleSounds import globalBattleSoundCache
from toontown.cutscene import CutsceneLocalizer
from toontown.cutscene.editor import CSEditorUtil
from toontown.cutscene.repository.CutsceneKeyEnum import CutsceneKeyEnum
from toontown.cutscene.repository.CutsceneLoader import cutsceneSetup, CutsceneLoader
from toontown.cutscene.repository.CutsceneObjects import *
from toontown.suit.SuitDNA import getSuitBodyType
from toontown.toonbase import TTLocalizer, ToontownGlobals



class CutsceneSetupException(BaseException):
    pass


# region Taskline Instance Bosses
# region Derrickman
@cutsceneSetup(CutsceneKeyEnum.Derrickman_Intro)
def __derrickmanIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('derrman', 'gh', 'gh', 'gh')
        derrickman = suits[0]
        for actor in toons + suits:
            actor.reparentTo(render)
        # Load the instance
        from toontown.instances.DistributedDerrickMan import DistributedDerrickMan
        instance = DistributedDerrickMan(base.cr)
        # Give it a fake doId so it can load the elevator
        instance.doId = -77
        instance.loadEnvironment()

        shopOwnerNpc = instance.shopOwnerNpc
        # Manipulate some stuff so Rain's emotes doesn't crash the CS Editor
        # god this sucks
        base.localAvatar = toons[0]
        base.localAvatar.isToonIgnored = lambda _: False
        base.localAvatar.unlockControlsForEntry = lambda: None

        # Locator node for the destination
        destNode = NodePath('destNode')
        destNode.reparentTo(render)
        destNode.setPos(0, 0, 0)
        destNode.setHpr(0, 0, 0)

        elevator = instance.elevatorModel
    else:
        toons, derrickman, suits, shopOwnerNpc, destNode, elevator = CSEditorUtil.getKwargs(kwargs, 'toons', 'derrickman', 'suits', 'shopOwnerNpc', 'destNode', 'elevator')

    def updateDerrickHp():
        derrickman.showHpText(-10)
        derrickman.updateHealthBar(-10)

    CSEditorUtil.populateList(toons)
    cutsceneLoader.addToonsToCutscene(toons + [shopOwnerNpc], maxToonCount=5)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=4)
    cutsceneLoader.addActorsToCutscene([derrickman, shopOwnerNpc, suits[-1], suits[-2], suits[-3]])
    cutsceneLoader.addFunctionsToCutscene([updateDerrickHp])
    cutsceneLoader.addNodesToCutscene([destNode, derrickman, shopOwnerNpc])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.DerrickManIntro)
    cutsceneLoader.addElevatorsToCutscene([elevator])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Derrickman_Death)
def __derrickmanDeath(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        derrickman, *suits = CSEditorUtil.makeSuits('derrman')
        battle = render.attachNewNode('battle')

        from toontown.instances.DistributedDerrickMan import DistributedDerrickMan
        instance = DistributedDerrickMan(base.cr)
        instance.doId = -77
        instance.loadEnvironment()
        shopOwnerNpc = instance.shopOwnerNpc

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[derrickman] + suits, newParent=battle)
    else:
        toons, derrickman, suits, battle, shopOwnerNpc = CSEditorUtil.getKwargs(kwargs, 'toons', 'derrickman', 'suits', 'battle', 'shopOwnerNpc')

    # Populate cutscene loader.
    allSuits = [derrickman] + suits
    CSEditorUtil.populateList(toons)
    cutsceneLoader.addToonsToCutscene(toons + [shopOwnerNpc], maxToonCount=5)
    cutsceneLoader.addSuitsToCutscene(allSuits, maxSuitCount=4)
    cutsceneLoader.addActorsToCutscene([derrickman, shopOwnerNpc])
    cutsceneLoader.addNodesToCutscene([battle, derrickman, shopOwnerNpc])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.DerrickManEnd)
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Derrickman_Vict)
def __derrickmanVict(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)

        from toontown.instances.DistributedDerrickMan import DistributedDerrickMan
        instance = DistributedDerrickMan(base.cr)
        instance.doId = -77
        instance.loadEnvironment()
        shopOwnerNpc = instance.shopOwnerNpc
        # Add Rain to the end of the toons list
        elevator = instance.elevatorModel

        cagedoor = instance.geom.find('**/cage_door')
        cageDoorSfx = loader.loadSfx('phase_5/audio/sfx/CHQ_SOS_cage_door.ogg')

        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[], newParent=battle)
    else:
        toons, cagedoor, shopOwnerNpc, elevator, cageDoorSfx, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'cagedoor', 'shopOwnerNpc', 'elevator', 'cageDoorSfx', 'instance')

    # Populate cutscene loader.
    CSEditorUtil.populateList(toons)
    cutsceneLoader.addToonsToCutscene(toons + [shopOwnerNpc], maxToonCount=5)
    cutsceneLoader.addActorsToCutscene([shopOwnerNpc])
    cutsceneLoader.addNodesToCutscene([cagedoor, shopOwnerNpc, instance.cage])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.DerrickManVictory)
    cutsceneLoader.addElevatorsToCutscene([elevator])
    cutsceneLoader.addSoundsToCutscene([cageDoorSfx])

    return cutsceneLoader
# endregion


# region Land Acquisition Architect
@cutsceneSetup(CutsceneKeyEnum.Dola_Intro)
def __dolaIntroCutsceneSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load the instance
        from toontown.instances.DistributedLandAcquisition import DistributedLandAcquisition
        instance = DistributedLandAcquisition(base.cr)
        # Give it a fake doId so it can load the elevator
        instance.doId = -77
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('dlao', 'gh', 'gh', 'gh')
    else:
        toons, suits = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits')

    # This cutscene is designed for 4 suits so make sure we pad the list, since it also impacts the actors
    if len(suits) < 4:
        suits.extend([None] * (4 - len(suits)))

    # Make sure everything's parented to render
    for actor in toons + suits:
        actor.reparentTo(render)
    camera.reparentTo(render)

    sounds = [
        'phase_14/audio/sfx/instance_dola_ctscn_introquake.ogg',
        'phase_14/audio/sfx/instance_dola_ctscn_march.ogg',
    ]

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.LandAcquisitionIntro)
    cutsceneLoader.addSoundsToCutscene(sounds)
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Dola_Death)
def __dolaDeathCutsceneSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load the instance
        from toontown.instances.DistributedLandAcquisition import DistributedLandAcquisition
        instance = DistributedLandAcquisition(base.cr)
        # Give it a fake doId so it can load the elevator
        instance.doId = -77
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('dlao', 'gh', 'gh', 'gh')
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        toons, battle, suits = CSEditorUtil.getKwargs(kwargs, 'toons', 'battle', 'suits')

    # The LAA should be the first element of suits.
    laa = suits[0]

    # Make hole
    holeModel = loader.loadModel("phase_5/models/props/ttcc_prp_holes")
    hole = holeModel.find("**/hole_ground_2").copyTo(battle)
    holeModel.removeNode()
    hole.setPos(0, 0, 0.1)
    hole.setColorScale(0, 0, 0, 1)
    hole.setScale(0.1)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addNodesToCutscene([hole, laa, battle])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.LandAcquisitionEnd[0] + [])
    cutsceneLoader.addSoundsToCutscene(['phase_14/audio/sfx/instance_dola_ctscn_quake.ogg'])
    return cutsceneLoader
# endregion


# region Public Relations Representative
@cutsceneSetup(CutsceneKeyEnum.Dopr_Intro)
def __doprIntroCutsceneSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load the instance
        from toontown.instances.DistributedOldeToontownDungeon import DistributedOldeToontownDungeon
        instance = DistributedOldeToontownDungeon(base.cr)
        instance.doId = -77
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('dopr')
        room = instance.geom
    else:
        toons, suits, room = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'room')

    # Make sure everything's parented to render
    for actor in toons + suits:
        actor.reparentTo(render)
    camera.reparentTo(render)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([room])
    cutsceneLoader.addDialogueToCutscene([""] + TTLocalizer.PublicRelationsIntro[0])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Dopr_Death)
def __doprDeathCutsceneSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load the instance
        from toontown.instances.DistributedOldeToontownDungeon import DistributedOldeToontownDungeon
        instance = DistributedOldeToontownDungeon(base.cr)
        instance.doId = -77
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('dopr')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=instance.battleANode)
    else:
        toons, suits = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits')

    diesound = globalBattleSoundCache.getSound(f'cc_s_sfx_ene_suit_headlessDeath_{getSuitBodyType(suits[0].dna.name).upper()}.ogg')

    def fixHead():
        suits[0].specialHead.stop()
        suits[0].specialHead.pose('neutral-hurt', 0)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addNodesToCutscene([suits[0]])
    cutsceneLoader.addDialogueToCutscene(["Are you surprised to see me?"] + TTLocalizer.PublicRelationsEnd[0])
    cutsceneLoader.addSoundsToCutscene([diesound])
    cutsceneLoader.addFunctionsToCutscene([fixHead])
    return cutsceneLoader
# endregion
# endregion


# region Street Mercs
# region Duck Shuffler
@cutsceneSetup(CutsceneKeyEnum.DuckShuffler_Wager_Base)
def __duckShufflerWagerSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('duckshfl', 'duckshfl', 'duckshfl', 'duckshfl', 'duckshfl', 'duckshfl')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)

        invoker = suits[0]
        eyeLandIndex = random.randint(0, 4)
        dialogue = 'TIME TO SPIN!!! (PLACEHOLDER)'
        resultSound = 'phase_5/audio/sfx/SA_wager_spin.ogg'
    else:
        invoker, battle, eyeLandIndex, dialogue, resultSound = CSEditorUtil.getKwargs(kwargs, 'invoker', 'battle', 'eyeLandIndex', 'dialogue', 'resultSound')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([invoker])
    cutsceneLoader.addActorsToCutscene([invoker])
    cutsceneLoader.addNodesToCutscene(
        [battle, invoker, invoker.specialHead]
    )
    cutsceneLoader.addDialogueToCutscene([dialogue])
    cutsceneLoader.addSoundsToCutscene([
        'phase_5/audio/sfx/SA_wager_spin.ogg',
        resultSound
    ])
    cutsceneLoader.addArgumentsToCutscene([eyeLandIndex])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.DuckShuffler_Wager_Bar)
def __duckShufflerBarSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('duckshfl', 'duckshfl', 'duckshfl', 'duckshfl', 'duckshfl', 'duckshfl')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        toons, suits, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'battle')

    # Get props for the cutscene.
    bar_a = globalPropPool.getProp("goldbar")
    bar_a.reparentTo(battle)
    bar_a.hide()
    bar_b = globalPropPool.getProp("goldbar")
    bar_b.reparentTo(battle)
    bar_b.hide()
    shadow_a = loader.loadModel("phase_3/models/props/square_drop_shadow")
    shadow_a.reparentTo(battle)
    shadow_a.hide()
    shadow_b = loader.loadModel("phase_3/models/props/square_drop_shadow")
    shadow_b.reparentTo(battle)
    shadow_b.hide()

    def cleanup():
        if editor:
            return
        bar_a.removeNode()
        bar_b.removeNode()
        shadow_a.removeNode()
        shadow_b.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=6)
    cutsceneLoader.addNodesToCutscene(
        [battle, bar_a, bar_b, shadow_a, shadow_b]
    )
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.DuckShuffler_Wager_Beans)
def __duckShufflerBeansSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('duckshfl', 'duckshfl', 'duckshfl', 'duckshfl', 'duckshfl', 'duckshfl')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)

        toon = toons[0]
    else:
        toon, *_ = CSEditorUtil.getKwargs(kwargs, 'toon')

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene([toon])
    cutsceneLoader.addNodesToCutscene([toon])
    cutsceneLoader.addParticleSystemsToCutscene(["jellybeanRainFall", "jellybeanRainLand"])
    return cutsceneLoader
# endregion


# region Deep Diver
@cutsceneSetup(CutsceneKeyEnum.DeepDiver_Dive)
def __deepDiverDiveSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('ddiver')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)

        # Rest of the arguments
        invoker = suits[0]
    else:
        invoker, toons, battle = CSEditorUtil.getKwargs(kwargs, 'invoker', 'toons', 'battle')

    # Reference position node
    referenceNode = battle.attachNewNode("referenceNode")
    referenceNode.setPos(invoker.getPos(battle))
    referenceNode.setHpr(invoker.getHpr(battle))

    # Make splash thingy
    from toontown.effects.Splash import Splash
    splash = Splash(referenceNode)

    def cleanup():
        if editor:
            return
        splash.destroy()
        referenceNode.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons)
    cutsceneLoader.addSuitsToCutscene([invoker], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([invoker, invoker.specialHead])
    cutsceneLoader.addNodesToCutscene([battle, invoker, referenceNode, splash, invoker.dropShadow])
    cutsceneLoader.addParticleSystemsToCutscene(["deepDiverSplash"])
    cutsceneLoader.addSoundsToCutscene(['phase_4/audio/sfx/MG_cannon_splash.ogg'])
    cutsceneLoader.addFunctionsToCutscene([splash.play, splash.stop, cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.DeepDiver_SinkOrSwim)
def __deepDiverSinkOrSwimSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('ddiver')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)

        # Rest of the arguments
        invoker = suits[0]
    else:
        invoker, battle = CSEditorUtil.getKwargs(kwargs, 'invoker', 'battle')

    # Reference position node
    referenceNode = battle.attachNewNode("referenceNode")
    referenceNode.setPos(invoker.getPos(battle))
    referenceNode.setHpr(invoker.getHpr(battle))

    # Make splash thingy
    from toontown.effects.Splash import Splash
    splash = Splash(referenceNode)

    def cleanup():
        if editor:
            return
        splash.destroy()
        referenceNode.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([invoker], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([invoker])
    cutsceneLoader.addNodesToCutscene([battle, invoker, referenceNode, splash])
    cutsceneLoader.addParticleSystemsToCutscene(["deepDiverSplash"])
    cutsceneLoader.addSoundsToCutscene(['phase_4/audio/sfx/MG_cannon_splash.ogg',
                                        'phase_5/audio/sfx/tt_s_ara_cmg_cogStomp.ogg'])
    cutsceneLoader.addFunctionsToCutscene([splash.play, splash.stop, cleanup])
    return cutsceneLoader
# endregion


# region Featherbedder
@cutsceneSetup(CutsceneKeyEnum.Featherbedder_Insomnia)
def __featherbedderInsomniaSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        fbed, *_ = CSEditorUtil.makeSuits('fbed')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[fbed], newParent=battle)
    else:
        toons, fbed, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'fbed', 'battle')

    featherbedderCopies = []
    featherBedderCopySeqs = []
    renderColorSeqDown = Sequence(
        LerpColorScaleInterval(render, 0.6, (0.4, 0.4, 0.4, 1.0), blendType='easeIn'),
    )
    renderColorSeqBack = Sequence(
        LerpColorScaleInterval(render, 0.6, (1.0, 1.0, 1.0, 1.0), blendType='easeIn'),
    )

    def newCopy():
        holder = fbed.attachNewNode('fbed-copy-holder')
        copy = fbed.getGeomNode().copyTo(holder)
        copy.setTransparency(1)
        copy.setColorScale(1, 0, 0, 0.7)
        copy.setDepthWrite(False)
        copy.setDepthTest(False)
        featherbedderCopies.append(copy)
        copySeq = Parallel(
            LerpColorScaleInterval(copy, 0.6, (1, 0, 0, 0.0), blendType='easeOut'),
            LerpScaleInterval(copy, 0.6, 2.2, startScale=0.99, blendType='easeOut')
        )
        featherBedderCopySeqs.append(copySeq)
        copySeq.start()

    def cleanupCopies():
        nonlocal featherBedderCopySeqs
        nonlocal featherbedderCopies
        for seq in featherBedderCopySeqs:
            seq.finish()
        featherBedderCopySeqs = []
        for fbedCopy in featherbedderCopies:
            fbedCopy.removeNode()
        featherbedderCopies = []

    def playColorShiftDown():
        return
        if editor or battle.hasLocalToon():
            renderColorSeqDown.start()

    def playColorShiftBack():
        return
        if editor or battle.hasLocalToon():
            renderColorSeqBack.start()

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([fbed])
    cutsceneLoader.addActorsToCutscene([fbed])
    cutsceneLoader.addNodesToCutscene([fbed, battle])
    cutsceneLoader.addFunctionsToCutscene([newCopy, cleanupCopies, playColorShiftDown, playColorShiftBack])
    return cutsceneLoader
# endregion
# endregion


# region Instance Mercs
# region Prethinker
@cutsceneSetup(CutsceneKeyEnum.Prethinker_Intro)
def __prethinkerIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    # Define sounds for the cutscene
    sounds = [
        # Toon flying at board
        'phase_5/audio/sfx/incoming_whistle.ogg',
        # Toon hits board
        'phase_4/audio/sfx/MG_cannon_hit_tower.ogg',
        # Toon slips on banana
        'phase_5/audio/sfx/TL_banana.ogg',
        # Open Door
        'phase_3.5/audio/sfx/Door_Open_1.ogg',
    ]

    if editor:
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('prethink', 'ptjockey', 'ptjockey', 'ptjockey')
        for actor in toons + suits:
            actor.reparentTo(render)
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = room.find('**/suit_origin')
        battle.setPosHpr(0, 3, 0, 90, 0, 0)

        doorA = loader.loadModel("phase_3.5/models/schoolhouse/schoolhouse_interior_door")
        doorA.reparentTo(room.find("**/door_origin_0"))
        doorAHinge = doorA.find('**/doorA_main')
        banana = globalPropPool.getProp('banana')
        banana.reparentTo(room)
    else:
        toons, suits, battle, doorAHinge, banana = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'battle', 'doorAHinge', 'banana')

    flyingToonNode = render.attachNewNode('flyingToonNode')

    def cleanup():
        if editor:
            return
        flyingToonNode.removeNode()

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=4)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([battle, suits[0], doorAHinge, banana, flyingToonNode, toons[0]])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['prethink'][0])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Prethinker_Death)
def __prethinkerDeathSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    sounds = [
        # Open Door
        'phase_3.5/audio/sfx/Door_Open_1.ogg',
        # Close Door
        'phase_3.5/audio/sfx/Door_Close_1.ogg',
    ]

    if editor:
        toons = CSEditorUtil.makeToons(4)
        suit, *_ = CSEditorUtil.makeSuits('prethink')
        for actor in toons + [suit]:
            actor.reparentTo(render)
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = room.find('**/suit_origin')
        battle.setPosHpr(0, 3, 0, 90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[suit], newParent=battle)

        doorB = loader.loadModel("phase_3.5/models/schoolhouse/schoolhouse_interior_door")
        doorB.reparentTo(room.find("**/door_origin_1"))
        doorBHinge = doorB.find('**/doorB_main')
        doorBReferenceNode = room.attachNewNode('doorB_ReferenceNode')
        doorBReferenceNode.setPos(doorB, 0, -6.0, 0.2)
    else:
        toons, suit, battle, doorBHinge, doorBReferenceNode = CSEditorUtil.getKwargs(kwargs, 'toons', 'suit', 'battle', 'doorBHinge', 'doorBReferenceNode')

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([suit], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([suit])
    cutsceneLoader.addNodesToCutscene([battle, suit, doorBHinge, doorBReferenceNode])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['prethink'][1])
    cutsceneLoader.addSoundsToCutscene(sounds)
    return cutsceneLoader


def __prethinkerCastlingSetup(cutsceneLoader: CutsceneLoader, editor: bool, **kwargs) -> CutsceneLoader:
    if editor:
        toons = CSEditorUtil.makeToons(4)
        prethink, *_ = CSEditorUtil.makeSuits('prethink')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[prethink], newParent=battle)

        indicatorNode = battle.attachNewNode('indicator-node')
        indicatorNode.setPos(prethink.getPos(battle))
        indicatorNode.setHpr(prethink.getHpr(battle))

        newPosNode = battle.attachNewNode('new-pos-node')
        pX, pY, pZ = prethink.getPos(battle)
        pH, pP, pR = prethink.getHpr(battle)
        newPosNode.setPos(pX, pY, pZ)
        newPosNode.setHpr(pH, pP, pR)

        rotateNode = battle.attachNewNode('camera-rotate-node')
        rotateNode.setPos(newPosNode.getPos(battle))
        rotateNode.setHpr(newPosNode.getHpr(battle))

        usedIndicatorNode = indicatorNode if cutsceneLoader.cutsceneKey == CutsceneKeyEnum.Prethinker_Castling_Exit else newPosNode
    else:
        toons, prethink, battle, usedIndicatorNode, rotateNode = CSEditorUtil.getKwargs(kwargs, 'toons', 'prethinker', 'battle', 'indicatorNode', 'rotateNode')

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([prethink], maxSuitCount=6)
    cutsceneLoader.addNodesToCutscene([battle, prethink, usedIndicatorNode, prethink.nametag3d, rotateNode, prethink.dropShadow, prethink.getShadowJoint()])
    cutsceneLoader.addSoundsToCutscene(['phase_9/audio/sfx/SA_castling.ogg'])
    cutsceneLoader.addParticleSystemsToCutscene(['prethinkerJumpSparksCircle', 'prethinkerJumpSparksUp'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Prethinker_Castling_Exit)
def __prethinkerCastlingExitSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader(CutsceneKeyEnum.Prethinker_Castling_Exit)
    return __prethinkerCastlingSetup(cutsceneLoader=cutsceneLoader, editor=editor, **kwargs)


@cutsceneSetup(CutsceneKeyEnum.Prethinker_Castling_Enter)
def __prethinkerCastlingEnterSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader(CutsceneKeyEnum.Prethinker_Castling_Enter)
    return __prethinkerCastlingSetup(cutsceneLoader=cutsceneLoader, editor=editor, **kwargs)


@cutsceneSetup(CutsceneKeyEnum.FindTheFamily_Attorney_Castling_Exit)
def __attorneyCastlingExitSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader(CutsceneKeyEnum.FindTheFamily_Attorney_Castling_Exit)
    return __prethinkerCastlingSetup(cutsceneLoader=cutsceneLoader, editor=editor, **kwargs)


@cutsceneSetup(CutsceneKeyEnum.Prethinker_ForwardThinking)
def __prethinkerForwardThinkingSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        prethink, *_ = CSEditorUtil.makeSuits('prethink')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[prethink], newParent=battle)
    else:
        toons, prethink, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'prethinker', 'battle')

    brainstormClouds = [PrethinkerBrainstormCloud(battle=battle, isEditor=editor) for _ in range(6)]

    sounds = [
        'phase_9/audio/sfx/SA_forward_thinking_intro.ogg',
    ]

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([prethink])
    cutsceneLoader.addActorsToCutscene([prethink])
    cutsceneLoader.addNodesToCutscene([prethink, battle] + brainstormClouds)
    cutsceneLoader.addFunctionsToCutscene([cloud.runSeq for cloud in brainstormClouds] + [cloud.cleanup for cloud in brainstormClouds])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.PRETHINKER_BRAIN_STORM])
    return cutsceneLoader
# endregion


# region Rainmaker
@cutsceneSetup(CutsceneKeyEnum.Rainmaker_Intro)
def __rainmakerIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        battle = instance.battleNode
        toons = CSEditorUtil.makeToons(4)
        rainmaker, *_ = CSEditorUtil.makeSuits('rainmake')
    else:
        rainmaker, toons, battle = CSEditorUtil.getKwargs(kwargs, 'rainmaker', 'toons', 'battle')

    # make sure these guys are real
    for avatar in [rainmaker] + toons:
        if avatar:
            avatar.reparentTo(render)

    # Populate cutscene loader.
    CSEditorUtil.populateList(toons)
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([rainmaker], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([rainmaker] + toons)
    cutsceneLoader.addNodesToCutscene([battle, rainmaker, rainmaker.nametag3d] + toons)
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['rainmake'][0])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_Transformation)
def __rainmakerTransCameraSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        rainmaker, *_ = CSEditorUtil.makeSuits('rainmake')
        battle = render.attachNewNode('battle')
        battle.setPos(0, 28, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[rainmaker], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        node = rainmaker.attachNewNode('cameraHelperNode')
    else:
        node, *_ = CSEditorUtil.getKwargs(kwargs, 'node')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([None], maxSuitCount=1)
    cutsceneLoader.addNodesToCutscene([node])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_Tornado)
def __rainmakerTornadoSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        rainmaker, *_ = CSEditorUtil.makeSuits('rainmake')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[rainmaker], newParent=battle)
    else:
        toons, rainmaker, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'rainmaker', 'battle')

    tornadoNode = battle.attachNewNode('tornadoNode')
    tornadoNode.setPos(0, -35, 0)

    tornadoNodeDeluxe = battle.attachNewNode('tornadoNodeDeluxe')
    tornadoNodeDeluxe.setPos(0, -97, 24)

    playerFunnyNode = battle.attachNewNode('playerFunnyNode')
    playerFunnyNode.setPos(0, -6, 0)

    # some stormclouds
    CSEditorUtil.populateList(toons)
    clouds = []
    dropshadows = []
    for toon in toons:
        if toon is None:
            clouds.append(None)
            dropshadows.append(None)
            continue
        cloud = loader.loadModel('phase_5.5/models/estate/bumper_cloud')
        cloud.setColorScale(0.95, 0.95, 0.95, 1.0)
        clouds.append(cloud)
        dropshadows.append(toon.dropShadow)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([rainmaker])
    cutsceneLoader.addActorsToCutscene([rainmaker])
    cutsceneLoader.addNodesToCutscene([rainmaker, battle, tornadoNode, playerFunnyNode] + toons + dropshadows + [
        tornadoNodeDeluxe] + clouds)
    cutsceneLoader.addParticleSystemsToCutscene(['rainmakerTornado', 'rainmakerTornado'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_ToonsComeHome)
def __rainmakerToonsComeHomeSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        rainmaker, *_ = CSEditorUtil.makeSuits('rainmake')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[rainmaker], newParent=battle)
    else:
        toons, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'battle')
    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addNodesToCutscene([battle])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_HeavyRainDamage)
def __rainmakerHeavyRainDamageSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        allSuits = CSEditorUtil.makeSuits('rainmake', 'dt', 'b', 'bf')
        rainmaker = allSuits[0]
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=allSuits, newParent=battle)
    else:
        toons, rainmaker, allSuits, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'rainmaker', 'allSuits', 'battle')

    lightning = globalPropPool.getProp('lightning')
    lightning.reparentTo(battle)
    lightning.hide()
    lightning.setScale(1, 1, 3)

    # Populate cutscene loader.
    CSEditorUtil.populateList(toons)
    CSEditorUtil.populateList(allSuits)
    if rainmaker in allSuits:
        allSuits.remove(rainmaker)
        allSuits.insert(0, rainmaker)
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([rainmaker])
    cutsceneLoader.addNodesToCutscene([rainmaker, battle] + toons + [lightning])
    cutsceneLoader.addParticleSystemsToCutscene(['lightningGagExplosion'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_StormCellDamage)
def __rainmakerStormCellDamageSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(2)
        suits = CSEditorUtil.makeSuits('rainmake')
        rainmaker = suits[0]
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)

        strikes = []
        for _ in range(4):
            lightning = globalPropPool.getProp('lightning')
            lightning.reparentTo(battle)
            lightning.hide()
            lightning.setScale(1, 1, 3)
            strikes.append(lightning)
    else:
        toons, rainmaker, battle, strikes = CSEditorUtil.getKwargs(kwargs, 'toons', 'rainmaker', 'battle',
                                                                   'strikes')

    CSEditorUtil.populateList(toons)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([rainmaker])
    cutsceneLoader.addNodesToCutscene([battle, rainmaker] + toons + strikes)
    cutsceneLoader.addParticleSystemsToCutscene(['lightningGagExplosion'] * 4)
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_Ending_1)
def __rainmakerEnding1Setup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        rainmaker, *_ = CSEditorUtil.makeSuits('rainmake')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[rainmaker], newParent=battle)
    else:
        rainmaker, battle, instance = CSEditorUtil.getKwargs(kwargs, 'rainmaker', 'battle', 'instance')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([rainmaker])
    cutsceneLoader.addNodesToCutscene([battle, rainmaker])
    cutsceneLoader.addActorsToCutscene([rainmaker])
    cutsceneLoader.addDialogueToCutscene([
        "I don't get it.",
        "Even when I stayed out of everyone's way...",
        "...you still tried to hurt me.",
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_Ending_2)
def __rainmakerEnding2Setup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        rainmaker, *_ = CSEditorUtil.makeSuits('rainmake')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[rainmaker], newParent=battle)
    else:
        rainmaker, battle, instance = CSEditorUtil.getKwargs(kwargs, 'rainmaker', 'battle', 'instance')

    def setEnvironment():
        instance.environment.request('OilRain')
        rainmaker.specialHead.setHairState(rainmaker.specialHead.OIL)

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([rainmaker])
    cutsceneLoader.addNodesToCutscene([battle, rainmaker, rainmaker.specialHead])
    cutsceneLoader.addActorsToCutscene([rainmaker])
    cutsceneLoader.addDialogueToCutscene([
        "Oh, don't play dumb with me!",
        "Lying only makes it worse.",
        "You knew what you came here to do.",
    ])
    cutsceneLoader.addFunctionsToCutscene([setEnvironment])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_Ending_3)
def __rainmakerEnding3Setup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        rainmaker, *_ = CSEditorUtil.makeSuits('rainmake')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[rainmaker], newParent=battle)

        instance.environment.request('OilRain')
        rainmaker.specialHead.setHairState(rainmaker.specialHead.OIL)
    else:
        rainmaker, battle, instance = CSEditorUtil.getKwargs(kwargs, 'rainmaker', 'battle', 'instance')

    def setEnvironmentA():
        instance.environment.request('HeavyRain')
        rainmaker.specialHead.setHairState(rainmaker.specialHead.HEAVY)

    def setEnvironmentB():
        instance.environment.request('StormCell')
        rainmaker.specialHead.setHairState(rainmaker.specialHead.STORM)

    startNode = rainmaker.attachNewNode('startNode')
    startNode.wrtReparentTo(battle)

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([rainmaker])
    cutsceneLoader.addNodesToCutscene([battle, rainmaker, rainmaker.specialHead, startNode])
    cutsceneLoader.addActorsToCutscene([rainmaker])
    cutsceneLoader.addDialogueToCutscene([
        "I want to be friends with you Toons.",
        "I don't see why it can't happen.",
        "But every time I try, you're mean to me!",
        "I remember I went up to this Toon named Bessie.",
        "I asked her if we could play tic-tac-toe.",
        "She tried to drop a piano on me!",
        "Why did she do that?! There was no reason!",
    ])
    cutsceneLoader.addFunctionsToCutscene([setEnvironmentA, setEnvironmentB])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Rainmaker_Ending_4)
def __rainmakerEnding4Setup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceRainmaker import DistributedInstanceRainmaker
        instance = DistributedInstanceRainmaker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        rainmaker, *_ = CSEditorUtil.makeSuits('rainmake')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[rainmaker], newParent=battle)

        instance.environment.request('StormCell')
        rainmaker.specialHead.setHairState(rainmaker.specialHead.STORM)
    else:
        rainmaker, battle, instance = CSEditorUtil.getKwargs(kwargs, 'rainmaker', 'battle', 'instance')

    def setEnvironmentA():
        instance.environment.request('OilRain')
        rainmaker.specialHead.setHairState(rainmaker.specialHead.OIL)

    def setEnvironmentB():
        instance.environment.request('Fog')
        rainmaker.specialHead.setHairState(rainmaker.specialHead.FOG)

    def setEnvironmentC():
        instance.environment.request('Default')

    startNode = rainmaker.attachNewNode('startNode')
    startNode.wrtReparentTo(battle)

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([rainmaker])
    cutsceneLoader.addNodesToCutscene([battle, rainmaker, rainmaker.specialHead, startNode])
    cutsceneLoader.addActorsToCutscene([rainmaker])
    cutsceneLoader.addDialogueToCutscene([
        "It's really easy, from where you are, to judge me.",
        "I know you do. Bessie wasn't the only one I talked to.",
        "But the shame of it is, you're not even the worst.",
        "Those other Suits have hurt me too.",
        "They've hurt me in ways that you wouldn’t understand.",
        "Maybe someday, I’ll share some of that pain with someone like you.",
    ])
    cutsceneLoader.addFunctionsToCutscene([setEnvironmentA, setEnvironmentB, setEnvironmentC])
    return cutsceneLoader
# endregion


# region Witch Hunter
@cutsceneSetup(CutsceneKeyEnum.Witchhunter_Intro)
def __witchHunterIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceWitchhunter import DistributedInstanceWitchhunter
        instance = DistributedInstanceWitchhunter(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('whunter', 'ptjockey', 'ptjockey', 'ptjockey')
    else:
        toons, suits, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'instance')

    # make sure these guys are real
    for actor in toons + suits:
        actor.reparentTo(render)

    # pad the suits list
    CSEditorUtil.populateList(suits)

    # Create nodes for cutscene
    instance.geom.setTransparency(TransparencyAttrib.MDual)
    flagCloth = instance.geom.attachNewNode('flag-cloth')
    flagCloth.setPos(9, 1, 30)
    flagCloth.setP(90)
    clothButSlightlyCloser = instance.geom.attachNewNode('flag-cloth-closer')
    clothButSlightlyCloser.setPos(9, 3, 30)
    clothButSlightlyCloser.setP(90)

    # Define sounds for the cutscene
    sounds = [
        'phase_3.5/audio/sfx/target_cloud.ogg',
        'phase_5/audio/sfx/SA_trial_by_fire_a.ogg',
        'phase_5/audio/sfx/SA_trial_by_fire_hit.ogg',
        'phase_11/audio/sfx/instance_witchhunter_ctscn_flagburn.ogg',
    ]

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=4)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene(
        [instance.battleNode, suits[0].getLeftHand(), suits[0].getRightHand(), instance.flag, flagCloth,
         clothButSlightlyCloser])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['whunter'][0])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addParticleSystemsToCutscene(['trialByFire', 'trialByFire', 'trialByFireRing',
                                                 'witchHunterFlagFireBase', 'witchHunterFlagFireCloth',
                                                 'witchHunterFlagFireClothDust'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Witchhunter_Death)
def __witchHunterDeathSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceWitchhunter import DistributedInstanceWitchhunter
        instance = DistributedInstanceWitchhunter(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        instance.flag.hide()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('whunter', 'ptjockey', 'ptjockey')
        suits[1].reparentTo(render)
        suits[2].reparentTo(render)

        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[suits[0]], newParent=battle)
    else:
        toons, suits, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'battle')

    toonTurnPoint = battle.attachNewNode('toon-turn-point')
    toonTurnPoint.setPos(-17.5, 0, 0)

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=3)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([battle, suits[0], toonTurnPoint])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['whunter'][1])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Witchhunter_MobMentality)
def __witchHunterMobMentalitySetup(editor: bool, **kwargs) -> CutsceneLoader:
    if editor:
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('whunter', 'mh', 'mh', 'mh')
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)

        from toontown.instances.mercs.DistributedInstanceWitchhunter import DistributedInstanceWitchhunter
        instance = DistributedInstanceWitchhunter(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        toons, suits, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'instance')

    # set cutscene dict
    cutsceneLoader = CutsceneLoader()
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=6)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([instance.battleNode])
    cutsceneLoader.addDialogueToCutscene([
        ""
    ])
    cutsceneLoader.addSoundsToCutscene(['phase_11/audio/sfx/SA_mob_mentality.ogg'])
    cutsceneLoader.addParticleSystemsToCutscene(['fireball'])
    cutsceneLoader.addArgumentsToCutscene([0])

    return cutsceneLoader
# endregion


# region Multislacker
@cutsceneSetup(CutsceneKeyEnum.Multislacker_Intro)
def __multislackerIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMultislacker import DistributedInstanceMultislacker
        instance = DistributedInstanceMultislacker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        multislacker, *_ = CSEditorUtil.makeSuits('mslacker')
    else:
        toons, multislacker, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'multislacker', 'instance')

    # make sure these guys are real
    for avatar in toons:
        avatar.reparentTo(render)

    # put multislacker in his chair :)
    multislacker.reparentTo(instance.chairNode)

    def cleanupDustClouds():
        if editor:
            return
        for toon in toons:
            if not hasattr(toon, 'dustCloud') or toon.dustCloud is None:
                continue
            toon.dustCloud.detachNode()
            toon.dustCloud.destroy()
            del toon.dustCloud

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([multislacker], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([multislacker] + toons)
    cutsceneLoader.addNodesToCutscene([instance.battleNode, multislacker, instance.chairNode])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['mslacker'][0])
    cutsceneLoader.addFunctionsToCutscene([cleanupDustClouds, instance.activateHallwayClippingPlane])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Multislacker_Death)
def __multislackerDeathSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMultislacker import DistributedInstanceMultislacker
        instance = DistributedInstanceMultislacker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode
        instance.chairNode.setH(-180)

        toons = CSEditorUtil.makeToons(4)
        multislacker, *_ = CSEditorUtil.makeSuits('mslacker')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[multislacker], newParent=battle)
    else:
        multislacker, battle = CSEditorUtil.getKwargs(kwargs, 'multislacker', 'battle')
        instance = battle.instance

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([multislacker], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([multislacker])
    cutsceneLoader.addNodesToCutscene([battle, multislacker, instance.chairNode])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['mslacker'][1])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Multislacker_MandatoryLunch_Start)
def __multislackerLunchStartSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMultislacker import DistributedInstanceMultislacker
        instance = DistributedInstanceMultislacker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode
        instance.chairNode.setH(-180)

        toons = CSEditorUtil.makeToons(4)
        multislacker, *_ = CSEditorUtil.makeSuits('mslacker')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[multislacker], newParent=battle)
    else:
        multislacker, battle = CSEditorUtil.getKwargs(kwargs, 'multislacker', 'battle')

    bossEatNode = battle.attachNewNode('battleNode-eatSpot')
    bossEatNode.setPos(10, 9, 0)

    sandwich = loader.loadModel('phase_6/models/golf/picnic_sandwich.bam')
    sandwich.setScale(2)

    starburstNode = render.attachNewNode('starburst-node')
    starburst = loader.loadModel('phase_3.5/models/props/ttcc_gen_starburst')
    starburst.setScale(1.5)
    starburst.setColorScale(1.0, 1.0, 0.7, 0.0)
    starburst.reparentTo(starburstNode)

    starburstSeq = Parallel(
        Sequence(
            LerpHprInterval(starburst, 1.7, (0, 0, 360))
        ),
        Sequence(
            LerpColorScaleInterval(starburst, 0.4, (1.0, 1.0, 0.7, 0.9)),
            Wait(0.9),
            LerpColorScaleInterval(starburst, 0.4, (1.0, 1.0, 0.7, 0))
        )
    )

    def startStarburst():
        starburstSeq.start()

    def cleanup():
        if editor:
            return
        starburstSeq.finish()
        starburstNode.removeNode()
        multislacker.delete()
        bossEatNode.removeNode()
        sandwich.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([multislacker], maxSuitCount=1)
    cutsceneLoader.addNodesToCutscene([battle, multislacker.getRightHand(), sandwich, bossEatNode, multislacker, starburstNode])
    cutsceneLoader.addSoundsToCutscene(['phase_5/audio/sfx/SZ_MM_fanfare.ogg'])
    cutsceneLoader.addActorsToCutscene([multislacker])
    cutsceneLoader.addFunctionsToCutscene([cleanup, startStarburst])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Multislacker_MandatoryLunch_End)
def __multislackerLunchEndSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMultislacker import DistributedInstanceMultislacker
        instance = DistributedInstanceMultislacker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode
        instance.chairNode.setH(-180)

        toons = CSEditorUtil.makeToons(4)
        multislacker, *_ = CSEditorUtil.makeSuits('mslacker')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[multislacker], newParent=battle)

        visualEffect = multislacker.addVisualEffect(VisualEffectEnum.MANDATORY_LUNCH_MSLACKER)
        multislacker.reapplyAllVisualEffects()
    else:
        multislacker, visualEffect = CSEditorUtil.getKwargs(kwargs, 'multislacker', 'visualEffect')

    # Nodes for cutscene
    fakeSuit = visualEffect.fakeSuit
    sandwich = visualEffect.sandwich
    referenceNode = render.attachNewNode('battleReturnNode')

    # Base dialogue off of current HP, for pseudo-randomization that is the same for all clients.
    dialogue = [
        CutsceneLocalizer.MultislackerEndMandatoryLunch[0][multislacker.hp % len(CutsceneLocalizer.MultislackerEndMandatoryLunch[0])],
        CutsceneLocalizer.MultislackerEndMandatoryLunch[1][multislacker.hp % len(CutsceneLocalizer.MultislackerEndMandatoryLunch[1])],
    ]

    def cleanup():
        if editor:
            return
        referenceNode.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([fakeSuit], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([fakeSuit])
    cutsceneLoader.addNodesToCutscene([fakeSuit, sandwich, referenceNode, multislacker])
    cutsceneLoader.addDialogueToCutscene(dialogue)
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Multislacker_Foreman_UnionBust)
def __multislackerForemanUnionBustSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMultislacker import DistributedInstanceMultislacker
        instance = DistributedInstanceMultislacker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode
        instance.chairNode.setH(-180)

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('msfore', 'gh', 'tf', 'ms')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        toons, suits, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'battle')

    suitsWithoutForeman = suits[1:]
    stomperSounds = ['phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'] * len(suitsWithoutForeman)
    while len(stomperSounds) < 3:
        stomperSounds.append(None)

    stompers = []
    stomperReferenceNodes = []
    for i in range(len(suitsWithoutForeman)):
        stomper = loader.loadModel('phase_9/models/cogHQ/square_stomper')
        stomper.setScale(2)
        stomper.setP(-90)
        stomper.find('**/shaft').setScale(Vec3(1.0, 15.0, 1.0))
        stomperRotateNode = NodePath('ms-stomper-rotate-node')
        stomper.reparentTo(stomperRotateNode)
        stomperReferenceNode = battle.attachNewNode('ms-stomper-reference-node')
        stomperReferenceNode.setPos(suitsWithoutForeman[i].getPos(battle))
        stomperRotateNode.reparentTo(stomperReferenceNode)
        stomperRotateNode.hide()
        stompers.append(stomperRotateNode)
        stomperReferenceNodes.append(stomperReferenceNode)
    while len(stompers) < 3:
        stompers.append(None)
    while len(stomperReferenceNodes) < 3:
        stomperReferenceNodes.append(None)

    def cleanup():
        if editor:
            return
        for referenceNode in stomperReferenceNodes:
            if referenceNode is not None:
                referenceNode.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=4)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addSoundsToCutscene(['phase_5/audio/sfx/SA_quake.ogg'] + stomperSounds)
    cutsceneLoader.addNodesToCutscene([suits[0], battle] + stompers + stomperReferenceNodes + suitsWithoutForeman)
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Multislacker_JoinBattle_Foreman)
def __multislackerJoinBattleForemanSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMultislacker import DistributedInstanceMultislacker
        instance = DistributedInstanceMultislacker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode
        instance.chairNode.setH(-180)
        centerSilo = instance.centerSiloGeom

        suits = CSEditorUtil.makeSuits('msfore', 'mh', 'mi', 'tf')
        CSEditorUtil.moveActorsToBattlePositions(suits=suits, newParent=battle)
    else:
        suits, battle, centerSilo = CSEditorUtil.getKwargs(kwargs, 'suits', 'battle', 'centerSilo')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addNodesToCutscene([battle, centerSilo] + suits)
    cutsceneLoader.addDialogueToCutscene(CutsceneLocalizer.MultislackerForemanJoinDialogue)
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Multislacker_JoinBattle_Generic)
def __multislackerJoinBattleGenericSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMultislacker import DistributedInstanceMultislacker
        instance = DistributedInstanceMultislacker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode

        suits = CSEditorUtil.makeSuits('ms', 'mh', 'mi', 'tf')
        CSEditorUtil.moveActorsToBattlePositions(suits=suits, newParent=battle)
    else:
        suits, battle = CSEditorUtil.getKwargs(kwargs, 'suits', 'battle')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addNodesToCutscene([battle] + suits)
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Multislacker_WastefulManagement)
def __multislackerWastefulManagementSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMultislacker import DistributedInstanceMultislacker
        instance = DistributedInstanceMultislacker(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode

        multislacker, *_ = CSEditorUtil.makeSuits('mslacker')
        CSEditorUtil.moveActorsToBattlePositions(suits=[multislacker], newParent=battle)
    else:
        multislacker, battle = CSEditorUtil.getKwargs(kwargs, 'multislacker', 'battle')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([multislacker], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([multislacker])
    cutsceneLoader.addNodesToCutscene([battle, multislacker])
    return cutsceneLoader
# endregion


# region Major Player
@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_Intro_Start)
def __majorplayerIntroStartSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        mplayer, *_ = CSEditorUtil.makeSuits('mplayer')
    else:
        toons, mplayer, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'mplayer', 'instance')

    # make sure these guys are real
    for avatar in toons + [mplayer]:
        avatar.reparentTo(render)

    # Create buffer nodes
    talkingAudience = instance.battleRoom.talkingAudience
    talkingAudienceHeads = [av.find('**/joint_head') for av in talkingAudience]
    bufferNodes = []
    for head in talkingAudienceHeads:
        children = head.getChildren()
        bufferNode = head.attachNewNode('bufferNode')
        for child in children:
            child.reparentTo(bufferNode)
        bufferNodes.append(bufferNode)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([mplayer])
    cutsceneLoader.addActorsToCutscene([mplayer] + talkingAudience)
    cutsceneLoader.addNodesToCutscene([instance.battleNode, mplayer] + bufferNodes)
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['mplayer'][0])
    cutsceneLoader.addElevatorsToCutscene([instance.elevatorModel])
    cutsceneLoader.addFunctionsToCutscene([instance.battleRoom.loopAudience])
    cutsceneLoader.addArgumentsToCutscene(['sit', 'sit-angry'])
    cutsceneLoader.addElevatorsToCutscene([instance.elevatorModel])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_Intro_End)
def __majorplayerIntroEndSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        mplayer, *_ = CSEditorUtil.makeSuits('mplayer')

        # Get to the end of the start of the intro.
        introStartTrack = CutsceneLoader.createLoader(
            key=CutsceneKeyEnum.MajorPlayer_Intro_Start,
            toons=toons,
            mplayer=mplayer,
            instance=instance
        ).buildCutscene()
        introStartTrack.start()
        introStartTrack.finish()
    else:
        toons, mplayer, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'mplayer', 'instance')

    # Get buffer nodes
    talkingAudience = instance.battleRoom.talkingAudience
    talkingAudienceHeads = [av.find('**/joint_head') for av in talkingAudience]
    bufferNodes = [head.find('**/bufferNode') for head in talkingAudienceHeads]

    # Randomly select a phrase from the tuple in the intro end dialogue
    dialogue = list(TTLocalizer.InstanceMinibossCutscenes['mplayer'][1])
    # Seed randomness with doId so all clients see same thing
    state = random.getstate()
    random.seed(instance.rngSeed)
    dialogue[2] = random.choice(dialogue[2])
    random.setstate(state)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([mplayer])
    cutsceneLoader.addActorsToCutscene([mplayer] + talkingAudience)
    cutsceneLoader.addNodesToCutscene([instance.battleNode, mplayer] + bufferNodes)
    cutsceneLoader.addDialogueToCutscene(dialogue)
    cutsceneLoader.addElevatorsToCutscene([instance.elevatorModel])
    cutsceneLoader.addFunctionsToCutscene([instance.battleRoom.loopAudience])
    cutsceneLoader.addArgumentsToCutscene(['sit', 'sit-angry'])
    cutsceneLoader.addElevatorsToCutscene([instance.elevatorModel])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_Revive)
def __majorplayerReviveSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, *suits = CSEditorUtil.makeSuits('mplayer', 'mh', 'mh', 'mh')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer] + suits, newParent=battle)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        toons, mplayer, suits, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'mplayer', 'suits', 'instance')

    # Populate cutscene loader.
    toonNodes = [None] * 4
    for i, toon in enumerate(toons):
        toonNodes[i] = toon
    allSuits = [mplayer, suits[2], suits[1], suits[0]]
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene(toonNodes + allSuits)
    cutsceneLoader.addNodesToCutscene([instance.battleNode, toonNodes[0],
                                       mplayer, mplayer.nametag3d,
                                       instance.geom, instance.battleRoom.discoballs[0],
                                       toonNodes[1], toonNodes[2], toonNodes[3],
                                       allSuits[1], allSuits[2], allSuits[3]])
    cutsceneLoader.addDialogueToCutscene([
        "Boo!-booyodididdlyyodoo!",
        "Where are you going babe? It's only the second act!",
        "Hit the floor babe, disco ain't dead, and neither am I!",
        "Let's see if you can handle these greatest hits!",
    ])
    cutsceneLoader.addElevatorsToCutscene([instance.elevatorModel])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_Death)
def __majorplayerDeathSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, *otherSuits = CSEditorUtil.makeSuits('mplayer', 'mh', 'mh', 'mh', 'mh', 'mh')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 180, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer, *otherSuits], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        toons, mplayer, otherSuits, battle, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'mplayer', 'otherSuits', 'battle', 'instance')

    CLONE, *_ = CSEditorUtil.makeSuits('mplayer')
    CLONE.hideNametag2d()
    CLONE.hide()
    CLONE.reparentTo(instance.geom)

    rose = loader.loadModel('phase_6/models/miniboss/majorplayer_rose')
    rose.hide()
    rose.reparentTo(battle)

    rose_shadow = loader.loadModel('phase_3/models/props/drop_shadow')
    rose_shadow.flattenMedium()
    rose_shadow.setColorScale(1, 1, 1, 0.65)
    rose_shadow.reparentTo(battle)
    rose_shadow.hide()

    audience = instance.battleRoom.getNextAudienceSuit()

    def showAllAudience():
        for member in instance.battleRoom.suitList + [audience]:
            if member:
                member.show()

    def hideAllAudience():
        for member in instance.battleRoom.suitList + [audience]:
            if member:
                member.hide()

    CSEditorUtil.populateList(toons, n=4)
    CSEditorUtil.populateList(otherSuits, n=5)
    if base.localAvatar in toons:
        toons.remove(base.localAvatar)
        toons.insert(0, base.localAvatar)
    cutsceneLoader.addToonsToCutscene(toons)
    cutsceneLoader.addSuitsToCutscene([mplayer] + otherSuits + [audience, CLONE])
    cutsceneLoader.addActorsToCutscene([mplayer] + otherSuits + [audience, CLONE])
    cutsceneLoader.addNodesToCutscene([battle, mplayer] + otherSuits + toons +
                                      [audience.specialHead if audience.specialHead else audience.getHeadParts()[0],
                                       toons[0].find('**/__Actor_head'), mplayer.specialHead, CLONE, CLONE.getGeomNode(),
                                       audience, rose, rose_shadow])
    cutsceneLoader.addFunctionsToCutscene([showAllAudience, hideAllAudience])

    # this stupid guys dialogue
    rng = random.Random(x=mplayer.doId if hasattr(mplayer, 'doId') else random.random())
    line1 = rng.choice([
        "Ring-ding-ding! Now that's a kick in the head if I ever seen one!",
        "Oooh hoo hoo, now that was a fun toe tap!",
    ])
    line3 = rng.choice([
        "I'm tellin ya babe, ya got some shining star cuts to dance with the sun I am!",
        "This night poked a hole in the sky, and I think there's a new star I do, I do!",
    ])
    line4 = rng.choice([
        "I played it my way and babe, your way only made it beeedeepidee-better!",
        "Tap a new tune babe, find that rhythm find that swing; find what I found in you before you play your last bar.",
    ])
    line5, line6 = rng.sample([
        "The bababadapadaaa - bands gotta stop playing eventually, and the night, and the music stop with them...",
        "I know you'll miss these nights but babe, you never miss those steps.",
        "There may be teardrops to shed, but babe, whatever song plays next, I know you can dance to whatever is ahead.",
        "Don't catch those bidddlydoopdoo-blues just cause the moon is over the hill, babe.",
        "I'm tellin' ya now: keep this song in your head, don't lose that tempo that soul. You got pep; a master step!",
        "Subito sempre simile that swingin' shuffle song sung sweetly this night.",
        "Poco a poco, I played loco, and the people went coco!",
    ], k=2)

    cutsceneLoader.addDialogueToCutscene([
        line1,
        "This congregating concert crowd's clapping concerto concentrated concussive chords of congratulations, babe!",
        line3, line4, line5, line6,
        "I can't believe it...",
        "That's all folks!",
        "These perfect prestissimo plays have been played and presented by the powerful proprietor of prowess!",
        "Dave BruBot!",
        "Wink!",
        "You can always find me baby, beyond the sea.",
        "But like any good song, it's time for this one man big band to fade out!",
        "Skibidiba-ta-ta!",
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_RisingStar_A)
def __majorplayerRisingStarASetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, *_ = CSEditorUtil.makeSuits('mplayer')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        audience = instance.battleRoom.getNextAudienceSuit()
    else:
        toons, mplayer, audience = CSEditorUtil.getKwargs(kwargs, 'toons', 'mplayer', 'audience')

    # Yes head
    head = audience.find('**/joint_head')
    if head:
        children = head.getChildren()
        bufferNode = head.attachNewNode('bufferNode')
        for child in children:
            child.reparentTo(bufferNode)
    else:
        bufferNode = None

    # Populate cutscene loader.
    suits = [mplayer, audience]
    CSEditorUtil.populateList(toons)
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(toons + suits)
    cutsceneLoader.addNodesToCutscene([suits[0], suits[1], bufferNode, audience.nametag3d])
    cutsceneLoader.addDialogueToCutscene([
        random.choice([
            "Wait, what?",
            "What's going on?",
            "Please pick me, please pick me...",
            "Is he talking to me?",
            "Finally, it's my time to shine!",
            "I'm gonna be a big shot!",  # :aol: :aol: :aol: :aol: :aol: :aol: :aol:
        ])
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_RisingStar_B)
def __majorplayerRisingStarBSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, newReserve = CSEditorUtil.makeSuits('mplayer', 'sd')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer, newReserve], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        toons, mplayer, newReserve, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'mplayer', 'newReserve', 'battle')

    # Populate cutscene loader.
    suits = [mplayer, newReserve]
    CSEditorUtil.populateList(toons)
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(toons + suits)
    cutsceneLoader.addNodesToCutscene([suits[0], suits[1], battle])
    cutsceneLoader.addDialogueToCutscene([
        random.choice([
            "It's my time to shine!",
            "Oh. Okay.",
            "...",
        ])
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_BeginMatching)
def __majorplayerBeginMatchingSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, *suits = CSEditorUtil.makeSuits('mplayer', 'sd', 'sd', 'sd', 'sd', 'sd')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer, *suits], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        toons, suits, mplayer, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'mplayer', 'battle')

    suitPosNodes = []
    for i, suit in enumerate(suits):
        posNode = suit.attachNewNode(f'suitPos-{i}')
        posNode.wrtReparentTo(render)
        suitPosNodes.append(posNode)

    centerPoint = battle.attachNewNode('suitCenter')
    centerPoint.setPos(0, 3, 0)

    # Populate cutscene loader.
    suitNodes = suits + [NodePath() for _ in range(len(suits), 5)]
    suits = [mplayer] + suits
    CSEditorUtil.populateList(toons)
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(toons + suits)
    cutsceneLoader.addNodesToCutscene([
        battle, mplayer, centerPoint, *suitNodes, *suitPosNodes])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_DancePartners)
def __majorplayerDancePartnersSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, *suits = CSEditorUtil.makeSuits('mplayer', 'sd', 'sd', 'sd', 'sd', 'sd')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer, *suits], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        mplayer, battle = CSEditorUtil.getKwargs(kwargs, 'mplayer', 'battle')

    cutsceneLoader.addSuitsToCutscene([mplayer])
    cutsceneLoader.addActorsToCutscene([mplayer])
    cutsceneLoader.addNodesToCutscene([battle, mplayer])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_StarOfTheShow)
def __majorplayerStarOfTheShowSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, *suits = CSEditorUtil.makeSuits('mplayer', 'sd', 'sd', 'sd', 'sd', 'sd')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer, *suits], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        mplayer, battle = CSEditorUtil.getKwargs(kwargs, 'mplayer', 'battle')

    cutsceneLoader.addSuitsToCutscene([mplayer])
    cutsceneLoader.addActorsToCutscene([mplayer])
    cutsceneLoader.addNodesToCutscene([battle, mplayer])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_GuestVerse)
def __majorplayerGuestVerseSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, guest, *suits = CSEditorUtil.makeSuits('mplayer', 'mh', 'sd', 'sd', 'sd', 'sd')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer, *suits, guest], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        mplayer, guest, battle = CSEditorUtil.getKwargs(kwargs, 'mplayer', 'guest', 'battle')

    cutsceneLoader.addSuitsToCutscene([mplayer, guest])
    cutsceneLoader.addActorsToCutscene([mplayer, guest])
    cutsceneLoader.addNodesToCutscene([battle, mplayer, guest])
    cutsceneLoader.addDialogueToCutscene([
        random.choice([
            "Okay, I think I'm ready!",
            "Here goes...",
            "I'll do my best!",
            "Right now? Let's do this!",
        ])
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.MajorPlayer_DancePartnersSpawn)
def __majorplayerDancePartnersSpawnSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        mplayer, *suits = CSEditorUtil.makeSuits('mplayer', 'sd', 'sd', 'sd', 'sd', 'sd')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 125, 5.351, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[mplayer, *suits], newParent=battle)

        for suit in suits:
            suit.reparentTo(render)

        from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
        instance = DistributedInstanceMajorplayer(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        suits, battle = CSEditorUtil.getKwargs(kwargs, 'suits', 'battle')

    CSEditorUtil.populateList(suits, n=5)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addNodesToCutscene([battle] + suits)
    return cutsceneLoader

# endregion


# region Plutocrat
@cutsceneSetup(CutsceneKeyEnum.Plutocrat_Intro)
def __plutocratIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('pcrat', *random.sample(['charon', 'nix', 'hydra', 'styx', 'kerberos'], 3))
        doorLeft = instance.doorLeft
        doorRight = instance.doorRight
    else:
        toons, suits, doorLeft, doorRight = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'doorLeft', 'doorRight')

    # make sure these guys are real
    for avatar in toons + suits:
        avatar.reparentTo(render)

    sounds = [
        'phase_9/audio/sfx/CHQ_door_open.ogg',
        'phase_9/audio/sfx/CHQ_door_close.ogg',
    ]

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=4)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([doorLeft, doorRight])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['pcrat'][0])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_Death)
def __plutocratDeathSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('pcrat', 'charon', 'nix', 'hydra', 'styx', 'kerberos')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        suits, battle = CSEditorUtil.getKwargs(kwargs, 'suits', 'battle')
        instance = battle.instance

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=6)
    cutsceneLoader.addActorsToCutscene([suits[0]])
    cutsceneLoader.addNodesToCutscene(
        [battle, suits[0], instance.chuteLeft, instance.chuteRight, suits[0].nametag3d])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['pcrat'][2])
    cutsceneLoader.addSoundsToCutscene(['phase_4/audio/sfx/CHQ_FACT_stomper_small.ogg'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_JoinBattle_Generic)
def __plutocratJoinBattleGenericSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('pcrat', *random.sample(['charon', 'nix', 'hydra', 'styx', 'kerberos'], 3))
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)

        # Locator node for the destination
        destNode = NodePath('destNode')
        destNode.reparentTo(instance.battleNode)
        destNode.setPos(4, 8.2, 0)
        destNode.setHpr(170, 0, 0)

        # Suit to join
        suit = suits[0]
    else:
        suit, battle, destNode = CSEditorUtil.getKwargs(kwargs, 'suit', 'battle', 'destNode')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([suit], maxSuitCount=1)
    cutsceneLoader.addNodesToCutscene([battle, destNode, suit])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_JoinBattle_Pcrat)
def __plutocratJoinBattlePcratSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suit, *_ = CSEditorUtil.makeSuits('pcrat')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[suit], newParent=battle)

        # Locator node for the destination
        destNode = NodePath('destNode')
        destNode.reparentTo(instance.battleNode)
        destNode.setPos(0, 0, 0)
        destNode.setHpr(0, 0, 0)
    else:
        toons, suit, battle, destNode = CSEditorUtil.getKwargs(kwargs, 'toons', 'suit', 'battle', 'destNode')

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons)
    cutsceneLoader.addSuitsToCutscene([suit], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([suit])
    cutsceneLoader.addNodesToCutscene([battle, destNode, suit])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['pcrat'][1])
    return cutsceneLoader


def __plutocratJoinBattleHatchSetup(cutsceneLoader: CutsceneLoader, editor: bool, **kwargs) -> CutsceneLoader:
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('pcrat', *random.sample(['charon', 'nix', 'hydra', 'styx', 'kerberos'], 3))
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        instance, *_ = CSEditorUtil.getKwargs(kwargs, 'instance')

    # Populate cutscene loader.
    cutsceneLoader.addNodesToCutscene([instance.chuteLeft, instance.chuteRight])
    cutsceneLoader.addSoundsToCutscene(['phase_4/audio/sfx/CHQ_FACT_stomper_small.ogg'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_JoinBattle_Hatch_Open)
def __plutocratJoinBattleHatchOpenSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader(CutsceneKeyEnum.Plutocrat_JoinBattle_Hatch_Open)
    return __plutocratJoinBattleHatchSetup(cutsceneLoader=cutsceneLoader, editor=editor, **kwargs)


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_JoinBattle_Hatch_Close)
def __plutocratJoinBattleHatchCloseSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader(CutsceneKeyEnum.Plutocrat_JoinBattle_Hatch_Close)
    return __plutocratJoinBattleHatchSetup(cutsceneLoader=cutsceneLoader, editor=editor, **kwargs)


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_Investor_SitDown)
def __plutocratSitdownSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        styx, *_ = CSEditorUtil.makeSuits('styx')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[styx], newParent=battle)
    else:
        styx, battle, *_ = CSEditorUtil.getKwargs(kwargs, 'styx', 'battle')

    # Populate cutscene loader.
    styxChairNode = styx.attachNewNode('chairbase')
    pizzaTable = loader.loadModel("phase_8/models/props/ttcc_prp_pc_table")
    pizzaChair = pizzaTable.find('**/pizza_chair_1')
    pizzaChair.reparentTo(styx)
    pizzaChair.setPosHpr(0, 0, 0, 0, 0, 0)
    pizzaChair.hide()
    pizzaTable.removeNode()
    styxSubnode = battle.attachNewNode(':)')
    cutsceneLoader.addSuitsToCutscene([styx])
    cutsceneLoader.addActorsToCutscene([styx])
    cutsceneLoader.addNodesToCutscene([styx, battle, styxSubnode, pizzaChair, styxChairNode])
    cutsceneLoader.addDialogueToCutscene([
        "Boo!-booyodididdlyyodoo!",
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_Investor_Usury)
def __plutocratUsurySetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        styx, waiter, *_ = CSEditorUtil.makeSuits('styx', 'tf')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[styx, waiter], newParent=battle)
    else:
        styx, waiter, battle, *_ = CSEditorUtil.getKwargs(kwargs, 'styx', 'waiter', 'battle')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([styx, waiter])
    cutsceneLoader.addActorsToCutscene([styx, waiter])
    cutsceneLoader.addNodesToCutscene([styx, waiter, battle])
    cutsceneLoader.addDialogueToCutscene([
        "Boo!-booyodididdlyyodoo!",
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_Investor_Usury_Fodder)
def __plutocratUsuryFodderSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        styx, *suits = CSEditorUtil.makeSuits('styx', 'tf', 'tf', 'tf', 'tf', 'tf')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[styx, *suits], newParent=battle)
    else:
        styx, suits, battle, *_ = CSEditorUtil.getKwargs(kwargs, 'styx', 'suits', 'battle')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([styx] + suits)
    cutsceneLoader.addActorsToCutscene([styx] + suits)
    cutsceneLoader.addNodesToCutscene([battle, styx] + suits)
    cutsceneLoader.addDialogueToCutscene([
        "Boo!-booyodididdlyyodoo!",
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_Investor_Kickup)
def __plutocratKickupSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        hydra, target, *_ = CSEditorUtil.makeSuits('hydra', 'styx')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hydra, target], newParent=battle)
    else:
        hydra, target, battle, *_ = CSEditorUtil.getKwargs(kwargs, 'hydra', 'target', 'battle')

    # Populate cutscene loader.
    helperNode = battle.attachNewNode('hydraKicknode')
    cutsceneLoader.addSuitsToCutscene([hydra, target])
    cutsceneLoader.addActorsToCutscene([hydra, target])
    cutsceneLoader.addNodesToCutscene([hydra, target, battle, helperNode])
    cutsceneLoader.addDialogueToCutscene([
        "Boo!-booyodididdlyyodoo!",
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_Investor_Tribute)
def __plutocratTributeSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        kerberos, target, *_ = CSEditorUtil.makeSuits('kerberos', 'styx')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[kerberos, target], newParent=battle)
    else:
        kerberos, target, battle, *_ = CSEditorUtil.getKwargs(kwargs, 'kerberos', 'target', 'battle')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([kerberos, target])
    cutsceneLoader.addActorsToCutscene([kerberos, target])
    cutsceneLoader.addNodesToCutscene([kerberos, target, battle])
    cutsceneLoader.addDialogueToCutscene([
        "Boo!-booyodididdlyyodoo!",
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_DeepFreeze_Camera)
def __plutocratDeepFreezeCameraSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('pcrat', 'ls', 'rb', 'rb', 'styx')
        plutocrat = suits[0]
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[plutocrat], newParent=battle)
    else:
        plutocrat, battle = CSEditorUtil.getKwargs(kwargs, 'plutocrat', 'battle')

    # Populate cutscene loader.
    cutsceneLoader.addNodesToCutscene([plutocrat, battle])
    return cutsceneLoader

    
@cutsceneSetup(CutsceneKeyEnum.Plutocrat_SnowSquall_Start)
def __plutocratSnowSquallStartSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        plutocrat, *_ = CSEditorUtil.makeSuits('pcrat')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[plutocrat], newParent=battle)
    else:
        toons, plutocrat, battle, instance, *_ = CSEditorUtil.getKwargs(kwargs, 'toons', 'plutocrat', 'battle', 'instance')

    # Populate cutscene loader.
    particleNode = instance.particleRender

    cutsceneLoader.addSuitsToCutscene([plutocrat])
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addActorsToCutscene(toons + [plutocrat])
    cutsceneLoader.addNodesToCutscene([plutocrat, battle, particleNode])
    cutsceneLoader.addParticleSystemsToCutscene(['chillyAir', 'chillyFlakes'])
    cutsceneLoader.addSoundsToCutscene(['phase_10/audio/sfx/SA_snowsquall_start.ogg'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_SnowSquall_End)
def __plutocratSnowSquallEndSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        plutocrat, *_ = CSEditorUtil.makeSuits('pcrat')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[plutocrat], newParent=battle)
    else:
        toons, plutocrat, battle, instance, *_ = CSEditorUtil.getKwargs(kwargs, 'toons', 'plutocrat', 'battle', 'instance')

    # Populate cutscene loader.
    particleNode = instance.particleRender

    cutsceneLoader.addSuitsToCutscene([plutocrat])
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addActorsToCutscene(toons + [plutocrat])
    cutsceneLoader.addNodesToCutscene([plutocrat, battle, particleNode])
    cutsceneLoader.addParticleSystemsToCutscene(['chillyAir', 'chillyFlakes'])
    cutsceneLoader.addSoundsToCutscene(['phase_10/audio/sfx/SA_snowsquall_start.ogg'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Plutocrat_SnowSquall_Damage)
def __plutocratSnowSquallDamageSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePlutocrat import DistributedInstancePlutocrat
        instance = DistributedInstancePlutocrat(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('pcrat', 'ls', 'rb', 'rb', 'styx')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(-14, 0, 0, -90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        toons, battle, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'battle', 'instance')

    # Populate cutscene loader.
    particleNode = instance.particleRender
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addNodesToCutscene([battle, particleNode])
    cutsceneLoader.addParticleSystemsToCutscene(['chillyAir', 'chillyFlakes'])
    cutsceneLoader.addSoundsToCutscene(['phase_10/audio/sfx/SA_snowsquall_dot.ogg'])
    return cutsceneLoader


# endregion


# region Chainsaw Consultant
@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_Intro)
def __chainsawIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('chainsaw', 'f')
    else:
        toons, suits, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'instance')

    # make sure these guys are real
    for avatar in toons + suits:
        avatar.reparentTo(render)

    sounds = [
        'phase_9/audio/sfx/CHQ_door_open.ogg',
        'phase_9/audio/sfx/CHQ_door_close.ogg',
        'phase_12/audio/sfx/instance_chainsawconsultant_ctscn_intro_override.ogg',
    ]

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=2)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([instance.battleNode, instance.geom, suits[0]] + instance.doorList)
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.CHAINSAW_OVERRIDE])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['chainsaw'][0])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_Death)
def __chainsawDeathSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        chainsaw, *otherBattleSuits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')
        chainsaw.specialHead.enterGlitch()
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + otherBattleSuits, newParent=battle)
    else:
        toons, chainsaw, otherBattleSuits, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'chainsaw', 'otherSuits', 'battle')
        instance = battle.instance

    suitName = 'ym'
    fakeSuit, *_ = CSEditorUtil.makeSuits(suitName)
    fakeSuit.reparentTo(instance.geom)
    fakeSuit.setPosHpr(0, 0, 0, 0, 0, 0)
    fakeSuit.hide()
    allSuits = [chainsaw, fakeSuit] + otherBattleSuits

    # Make buffer node for fakeSuit so we can move it's head.
    head = fakeSuit.find('**/joint_head')
    children = head.getChildren()
    bufferNode = head.attachNewNode('bufferNode')
    for child in children:
        child.reparentTo(bufferNode)

    # Load in the camera mover with the relevant animations.
    cameraAnimPaths = [
        'phase_12/models/misc/camera_actor-chainsaw-cutscene-leap',
    ]
    cameraMover = CSEditorUtil.makeCameraMover(*cameraAnimPaths)
    cameraMover.reparentTo(instance.geom)
    cameraMover.setPosHpr(0, 0, 0, 0, 0, 0)
    cameraBone = cameraMover.find('**/CameraBone')

    sounds = [
        'phase_9/audio/sfx/CHQ_door_open.ogg',
        'phase_9/audio/sfx/CHQ_door_close.ogg',
        'phase_12/audio/sfx/instance_chainsawconsultant_ctscn_death.ogg',
    ]

    def cleanup():
        if editor:
            return
        fakeSuit.delete()
        cameraMover.delete()

    def getCameraInterval(animName):
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ActorInterval(cameraMover, animName),
        )

    def getCameraLoop(animName):
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            Func(cameraMover.loop, animName),
        )

    def createSuitStepBackTrack():
        masterTrack = Parallel()
        delay = 0.0
        for suit in otherBattleSuits:
            def getStepBackPos(suit=suit):
                return suit.getPos() + Point3(0, 4, 0)

            moveDuration = 0.8
            walkTrack = Sequence(
                ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05),
                Func(suit.loop, 'neutral'),
            )
            moveTrack = LerpPosInterval(suit, moveDuration, getStepBackPos, other=battle)
            masterTrack.append(Sequence(Wait(delay), Parallel(walkTrack, moveTrack)))
            # Delay between each suit
            delay += 0.6
        return masterTrack

    def exitGlitch():
        if chainsaw.specialHead.sfxInterval:
            chainsaw.specialHead.sfxInterval.finish()
        chainsaw.specialHead.setChainsawTexRoll(0)
        chainsaw.specialHead.exitGlitch()

    def reparentOtherSuitsToGeom():
        for suit in otherBattleSuits:
            suit.wrtReparentTo(instance.geom)

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(allSuits, maxSuitCount=6)
    cutsceneLoader.addActorsToCutscene(allSuits)
    cutsceneLoader.addNodesToCutscene([battle, cameraMover, chainsaw, fakeSuit, bufferNode, instance.cogEntrance_1_1, instance.cogEntrance_1_2])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['chainsaw'][1])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addMusicToCutscene(['chainsaw_end'])
    cutsceneLoader.addFunctionsToCutscene([cleanup, getCameraInterval, getCameraLoop, createSuitStepBackTrack, exitGlitch, chainsaw.specialHead.enterGlitch, reparentOtherSuitsToGeom])
    cutsceneLoader.addArgumentsToCutscene(cameraMover.getAnimNames())
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_Ending)
def __chainsawEndingSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        localToon = toons[0]
        chainsaw, *_ = CSEditorUtil.makeSuits('chainsaw')
        battle = instance.battleNode
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw], newParent=battle)
    else:
        localToon, toons, chainsaw, instance = CSEditorUtil.getKwargs(kwargs, 'localToon', 'toons', 'chainsaw', 'instance')

    # Reparent all toons to render
    for toon in toons:
        toon.wrtReparentTo(render)

    if localToon in toons:
        toons.remove(localToon)

    # Load in the camera mover with the relevant animations.
    cameraAnimPaths = [
        'phase_12/models/misc/camera_actor-chainsaw-cutscene-laying',
        'phase_12/models/misc/camera_actor-chainsaw-cutscene-getup-cam1',
        'phase_12/models/misc/camera_actor-chainsaw-cutscene-getup-cam2',
        'phase_12/models/misc/camera_actor-chainsaw-cutscene-todesk',
    ]
    cameraMover = CSEditorUtil.makeCameraMover(*cameraAnimPaths)
    cameraMover.reparentTo(instance.geom)
    cameraMover.setPosHpr(0, 0, 0, 0, 0, 0)
    cameraBone = cameraMover.find('**/CameraBone')

    sounds = [
        'phase_9/audio/sfx/CHQ_door_open.ogg',
        'phase_9/audio/sfx/CHQ_door_close.ogg',
        'phase_12/audio/sfx/instance_chainsawconsultant_ctscn_end_main.ogg',
        'phase_12/audio/sfx/instance_chainsawconsultant_ctscn_end_shuffling.ogg',
        'phase_12/audio/sfx/instance_chainsawconsultant_ctscn_end_yell.ogg',
        'phase_12/audio/sfx/instance_chainsawconsultant_ctscn_end_footsteps.ogg',
    ]

    def cleanup():
        if editor:
            return
        cameraMover.delete()

    def getCameraInterval(animName):
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ActorInterval(cameraMover, animName),
        )

    def getCameraLoop(animName):
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            Func(cameraMover.loop, animName),
        )

    def resetChair():
        instance.throwableChair.pose('getThrown', 0)

    def getChairThrownInterval():
        return ActorInterval(instance.throwableChair, 'getThrown')

    cutsceneLoader.addToonsToCutscene([localToon] + toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([chainsaw], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([chainsaw, localToon])
    cutsceneLoader.addNodesToCutscene([cameraMover, cameraMover, chainsaw])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['chainsaw'][2])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addFunctionsToCutscene([cleanup, getCameraInterval, getCameraLoop, resetChair,
                                           getChairThrownInterval, base.transitions.noTransitions,
                                           lambda: base.transitions.fadeOut(0), lambda: chainsaw.specialHead.setForceUnhurtMode(1)])
    cutsceneLoader.addArgumentsToCutscene(cameraMover.getAnimNames())
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_Deadwood)
def __chainsawDeadwoodSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()

        battle = instance.battleNode
        doors = instance.doorList

        taunt = TTLocalizer.SuitAttackTaunts[AttackEnum.DEADWOOD][0]

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        toons, chainsaw, suits, battle, doors, taunt = CSEditorUtil.getKwargs(
            kwargs, 'toons', 'chainsaw', 'suits', 'battle', 'doors', 'taunt')
    
    pointCannonAtNode = NodePath('pointCannonAt')
    pointCannonAtNode.reparentTo(render)

    def cleanup():
        if editor:
            return
        pointCannonAtNode.removeNode()
        [toon.wrtReparentTo(render) for toon in toons if toon]

    # Populate cutscene loader.
    allSuits = [chainsaw] + suits
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw, *doors, pointCannonAtNode])
    cutsceneLoader.addDialogueToCutscene([taunt])
    cutsceneLoader.addSoundsToCutscene([
        "phase_12/audio/sfx/SA_deadwood.ogg",
    ])
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_Throttle)
@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_ThrottleTwo)
def __chainsawThrottleSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()

        battle = instance.battleNode

        taunt = TTLocalizer.SuitAttackTaunts[AttackEnum.THROTTLE][0]

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        toons, chainsaw, suits, battle, taunt = CSEditorUtil.getKwargs(
            kwargs, 'toons', 'chainsaw', 'suits', 'battle', 'taunt')
    
    pointCannonAtNode = NodePath('pointCannonAt')
    pointCannonAtNode.reparentTo(render)

    CSEditorUtil.populateList(toons)
    fallPoints = [NodePath(f'fallPoint{i}') if toon else None for i, toon in enumerate(toons)]
    for toon, point in zip(toons, fallPoints):
        if toon is None:
            continue
        if point is None:
            continue
        point.reparentTo(toon)
        point.wrtReparentTo(render)
        point.setHpr(0, 0, 0)

    def cleanup():
        chainsaw.specialHead.loopNeutral()

        if editor:
            return
        pointCannonAtNode.removeNode()
        [fallPoint.removeNode() for fallPoint in fallPoints if fallPoint]
        [toon.wrtReparentTo(render) for toon in toons if toon]
        camera.wrtReparentTo(battle)

    # Populate cutscene loader.
    allSuits = [chainsaw] + suits
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw, pointCannonAtNode, *fallPoints, *toons])
    cutsceneLoader.addDialogueToCutscene([taunt])
    cutsceneLoader.addSoundsToCutscene([
        'phase_4/audio/sfx/MG_cannon_hit_tower.ogg',
        'phase_12/audio/sfx/SA_throttle_break.ogg',
        'phase_12/audio/sfx/SA_throttle_hit.ogg',
    ])
    cutsceneLoader.addParticleSystemsToCutscene(['chainsawBulbBreak', 'chainsawGlassDrip'])
    cutsceneLoader.addFunctionsToCutscene([cleanup, chainsaw.specialHead.bulbLeft.hide, chainsaw.specialHead.bulbLeft.show, chainsaw.specialHead.enterSemiGlitch])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_Scabbard)
def __chainsawScabbardSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()

        battle = instance.battleNode

        taunt = TTLocalizer.SuitAttackTaunts[AttackEnum.SCABBARD][0][0]

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        toons, chainsaw, suits, battle, taunt = CSEditorUtil.getKwargs(
            kwargs, 'toons', 'chainsaw', 'suits', 'battle', 'taunt')

    # Populate cutscene loader.
    allSuits = [chainsaw] + suits
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw])
    cutsceneLoader.addDialogueToCutscene([taunt])
    cutsceneLoader.addSoundsToCutscene(['phase_12/audio/sfx/SA_scabbard.ogg'])
    cutsceneLoader.addFunctionsToCutscene([chainsaw.specialHead.loopNeutral])
    cutsceneLoader.addParticleSystemsToCutscene(['chainsawScabbardUp'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_RevvedUp)
def __chainsawRevvedUpSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()

        battle = instance.battleNode

        taunt = TTLocalizer.SuitAttackTaunts[AttackEnum.REVVING_UP][0][0]

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        toons, chainsaw, suits, battle, taunt = CSEditorUtil.getKwargs(
            kwargs, 'toons', 'chainsaw', 'suits', 'battle', 'taunt')

    from toontown.suit.heads.classes.ChainsawAnimatedSuitHead import GlitchState
    headAnim = chainsaw.specialHead.actorInterval('revvedup')

    def playHeadAnim():
        if chainsaw.specialHead.glitchState == GlitchState.SemiGlitch:
            headAnim.start()

    # Populate cutscene loader.
    allSuits = [chainsaw] + suits
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw])
    cutsceneLoader.addDialogueToCutscene([taunt])
    cutsceneLoader.addSoundsToCutscene(['phase_12/audio/sfx/SA_revving_up.ogg'])
    cutsceneLoader.addFunctionsToCutscene([playHeadAnim, headAnim.finish, chainsaw.specialHead.loopNeutral])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_SparkPlug)
def __chainsawSparkPlugSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()

        battle = instance.battleNode

        taunt = TTLocalizer.SuitAttackTaunts[AttackEnum.SPARK_PLUG][0]

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        toons, chainsaw, suits, battle, taunt = CSEditorUtil.getKwargs(
            kwargs, 'toons', 'chainsaw', 'suits', 'battle', 'taunt')

    # Populate cutscene loader.
    allSuits = [chainsaw] + suits
    cutsceneLoader.addToonsToCutscene(toons[:1], maxToonCount=1)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw, toons[0], chainsaw.leftHand])
    cutsceneLoader.addDialogueToCutscene([taunt])
    cutsceneLoader.addSoundsToCutscene(['phase_5/audio/sfx/AA_zap_tv.ogg', 'phase_12/audio/sfx/SA_sparkplug.ogg'])
    cutsceneLoader.addParticleSystemsToCutscene(['chainsawSparkPlugFinger', 'chainsawSparkPlugAcross'])
    cutsceneLoader.addFunctionsToCutscene([chainsaw.specialHead.loopNeutral])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_Offboarding)
def __chainsawOffboardingSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()

        battle = instance.battleNode

        taunt = TTLocalizer.SuitAttackTaunts[AttackEnum.OFFBOARDING][0][0]

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        toons, chainsaw, suits, battle, taunt = CSEditorUtil.getKwargs(
            kwargs, 'toons', 'chainsaw', 'suits', 'battle', 'taunt')

    toonPosNode = toons[0].attachNewNode('toonPosNode')
    toonPosNode.wrtReparentTo(render)

    def cleanup():
        if editor:
            return
        toonPosNode.removeNode()
        if toons[0]:
            toons[0].wrtReparentTo(render)

    # Populate cutscene loader.
    allSuits = [chainsaw] + suits
    cutsceneLoader.addToonsToCutscene(toons[:1], maxToonCount=1)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw, toons[0], toonPosNode])
    cutsceneLoader.addDialogueToCutscene([taunt])
    cutsceneLoader.addSoundsToCutscene([
        "phase_11/audio/sfx/SA_bash.ogg",
        'phase_3.5/audio/sfx/ENC_cogfall_apart.ogg',
        'phase_4/audio/sfx/avatar_emotion_surprise.ogg'
    ])
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_Layoffs)
def __chainsawLayoffsSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()

        battle = instance.battleNode

        taunt = TTLocalizer.SuitAttackTaunts[AttackEnum.LAYOFFS][0]

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        toons, chainsaw, suits, battle, taunt = CSEditorUtil.getKwargs(
            kwargs, 'toons', 'chainsaw', 'suits', 'battle', 'taunt')

    toonPosNodes = []
    for i, toon in enumerate(toons):
        toonPosNode = toon.attachNewNode(f'toonPosNode-{i}')
        toonPosNode.wrtReparentTo(render)
        toonPosNodes.append(toonPosNode)

    for i in range(4 - len(toons)):
        toons.append(None)

    def cleanup():
        if editor:
            return
        [toonPosNode.removeNode() for toonPosNode in toonPosNodes if toonPosNode]
        [toon.wrtReparentTo(render) for toon in toons if toon]

    # Populate cutscene loader.
    allSuits = [chainsaw] + suits
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw, *toons, *toonPosNodes])
    cutsceneLoader.addDialogueToCutscene([taunt])
    cutsceneLoader.addSoundsToCutscene([
        'phase_3.5/audio/sfx/ENC_cogfall_apart.ogg',
        'phase_4/audio/sfx/avatar_emotion_surprise.ogg'
    ])
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_ChainLinked)
def __chainsawChainLinkedSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()

        battle = instance.battleNode

        taunt = TTLocalizer.SuitAttackTaunts[AttackEnum.CHAIN_LINKED][0][0]

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        toons, chainsaw, suits, battle, taunt = CSEditorUtil.getKwargs(
            kwargs, 'toons', 'chainsaw', 'suits', 'battle', 'taunt')

    def showText(*s):
        for suit in s:
            suit.showHpString("CHAIN LINKED!", color=(1, 1, 1, 1))
            MovieUtil.applyVisualEffect(suit, VisualEffectEnum.CHAIN_LINKED)

    # Populate cutscene loader.
    allSuits = [chainsaw] + suits
    cutsceneLoader.addToonsToCutscene(toons[:1], maxToonCount=1)
    cutsceneLoader.addSuitsToCutscene(allSuits)
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw, toons[0]])
    cutsceneLoader.addDialogueToCutscene([taunt])
    cutsceneLoader.addFunctionsToCutscene([showText])
    cutsceneLoader.addArgumentsToCutscene([suits])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_PhaseTwo)
@cutsceneSetup(CutsceneKeyEnum.ChainsawConsultant_PhaseThree)
def __chainsawPhaseChangeSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        chainsaw, *suits = CSEditorUtil.makeSuits('chainsaw', 'tbc', 'tbc', 'tbc', 'tbc')

        from toontown.instances.mercs.DistributedInstanceChainsaw import DistributedInstanceChainsaw
        instance = DistributedInstanceChainsaw(base.cr)
        instance.doId = -69
        instance.loadEnvironment()
        battle = instance.battleNode

        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[chainsaw] + suits, newParent=battle)
    else:
        chainsaw, battle = CSEditorUtil.getKwargs(kwargs, 'chainsaw', 'battle')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([chainsaw])
    cutsceneLoader.addActorsToCutscene([chainsaw])
    cutsceneLoader.addNodesToCutscene([battle, chainsaw, chainsaw.specialHead])
    cutsceneLoader.addDialogueToCutscene([
        "DAMAGE TO- \1CHOVER\1help-\2 TO- \1CHOVER\1help-\2 TO OVER- \1CHOVER\1me-\2 OVERRIDE DE- \1CHOVER\1toons-\2 DETECTED.",
        "ENTERING- \1CHOVER\1i'm-\2 ENTER- \1CHOVER\1trying to-\2 RECOVERY MO- \1CHOVER\1resist it-\2 MODE.",
        "ACTIVATING- \1CHOVER\1i don't-\2 TEMP- \1CHOVER\1know-\2 TEMPORARY- \1CHOVER\1if i-\2 REFOREST- \1CHOVER\1can-\2 REFORESTATION MODE.",
        "RECOV- \1CHOVER\1i-\2 RECOVERY AT- \1CHOVER\1can't-\2 RECOV- \1CHOVER\1stop it-\2",
        "\1CHOVER\1please-\2 RECOV- \1CHOVER\1save-\2 RECOV-",
        "\1CHOVER\1save yourselves!\2",
        "RECOVERY COMPLETE.",
        "ENTERING FINAL TERMINATION MODE.",
        "ALL RAM CLEARED. OFFENSIVE DIVISION AT MAXIMUM PERFORMANCE.",
    ])
    return cutsceneLoader
# endregion


# region Pacesetter
@cutsceneSetup(CutsceneKeyEnum.Pacesetter_Intro)
def __pacesetterIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePacesetter import DistributedInstancePacesetter
        instance = DistributedInstancePacesetter(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        pacesetter, *_ = CSEditorUtil.makeSuits('psetter')
    else:
        toons, pacesetter, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'pacesetter', 'instance')

    # make sure these guys are real
    for avatar in toons + [pacesetter]:
        if avatar:
            avatar.wrtReparentTo(render)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([pacesetter], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([pacesetter] + toons)
    cutsceneLoader.addNodesToCutscene([instance.battleNode, pacesetter, instance.paceNodeIntro])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['psetter'][0])
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.AFTERIMAGE])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Pacesetter_Death)
def __pacesetterDeathSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePacesetter import DistributedInstancePacesetter
        instance = DistributedInstancePacesetter(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode

        toons = CSEditorUtil.makeToons(4)
        pacesetter, *otherSuits = CSEditorUtil.makeSuits('psetter', 'mh', 'tbc', 'bw', 'hho')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[pacesetter] + otherSuits, newParent=battle)

        # Apply visual effect
        pacesetter.addVisualEffect(VisualEffectEnum.AFTERIMAGE)
        pacesetter.reapplyAllVisualEffects()
    else:
        pacesetter, battle = CSEditorUtil.getKwargs(kwargs, 'pacesetter', 'battle')
        instance = battle.instance

    sounds = [
        'phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg',
        'phase_9/audio/sfx/CHQ_VP_boom.ogg'
    ]

    def fixHead():
        pacesetter.specialHead.stop()
        pacesetter.specialHead.pose('neutral-hurt', 0)
        pacesetter.specialHead.ignoreNeutral = True

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([pacesetter], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([pacesetter])
    cutsceneLoader.addNodesToCutscene([battle, pacesetter, instance.paceNodeDeath])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.InstanceMinibossCutscenes['psetter'][1])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addFunctionsToCutscene([fixHead])
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.AFTERIMAGE])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Pacesetter_GuitarSolo)
def __pacesetterGuitarSoloSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstancePacesetter import DistributedInstancePacesetter
        instance = DistributedInstancePacesetter(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        battle = instance.battleNode

        toons = CSEditorUtil.makeToons(4)
        suit, *otherSuits = CSEditorUtil.makeSuits('psetter', 'mh', 'tbc', 'bw', 'hho')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[suit] + otherSuits, newParent=battle)
    else:
        toons, suit, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'suit', 'battle')

    # load in guitar and attach it to the suit's hold joint
    guitar = loader.loadModel('phase_9/models/char/paceGuitar')
    holdJoint = suit.find('**/joint_Lhold')
    guitar.reparentTo(holdJoint)
    # adjust guitar's angle to match the intended angle for the animation
    guitar.setPosHpr(0, 0, 0, 0, 20, 90)
    guitar.hide()

    # reference node for the explosion
    explosionRefNode = suit.attachNewNode('explosionRefNode')

    # Explosion for when he throws guitar at ground
    explosion = loader.loadModel('phase_3.5/models/props/explosion.bam')
    explosion.setBillboardPointEye()
    explosion.setDepthWrite(False)
    explosion.hide()
    explosion.reparentTo(explosionRefNode)

    sounds = [
        'phase_9/audio/sfx/SA_overclocked.ogg',
        'phase_3.5/audio/sfx/ENC_cogfall_apart.ogg'
    ]

    def cleanup():
        if editor:
            return
        Func(guitar.removeNode)
        Func(explosionRefNode.removeNode)
        Func(suit.nametag3d.show)

    def updateDiscordRPC():
        if editor:
            return
        base.discord.applyPreset('psetter_overclocked')

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons)
    cutsceneLoader.addSuitsToCutscene([suit], maxSuitCount=1)
    cutsceneLoader.addActorsToCutscene([suit])
    cutsceneLoader.addNodesToCutscene([battle, suit, guitar, holdJoint, explosionRefNode, explosion])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.AFTERIMAGE])
    cutsceneLoader.addFunctionsToCutscene([cleanup, updateDiscordRPC])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Pacesetter_OverclockedGUI)
def __pacesetterOverclockedGUISetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        oldSpeed = 1.0
    else:
        oldSpeed, *_ = CSEditorUtil.getKwargs(kwargs, 'oldSpeed')

    # Populate cutscene loader.
    newSpeed = 999.99
    cutsceneLoader.addArgumentsToCutscene([oldSpeed, newSpeed])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Pacesetter_PickUpThePace)
def __pacesetterPickUpThePaceSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        pacesetter, *_ = CSEditorUtil.makeSuits('psetter')
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[pacesetter], newParent=battle)
        oldSpeed, newSpeed = 1.0, 5.0
    else:
        toons, pacesetter, battle, oldSpeed, newSpeed = CSEditorUtil.getKwargs(kwargs, 'toons', 'pacesetter', 'battle', 'oldSpeed', 'newSpeed')

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([pacesetter])
    cutsceneLoader.addNodesToCutscene([battle, pacesetter])
    cutsceneLoader.addArgumentsToCutscene([oldSpeed, newSpeed])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.FindTheFamily_Attorney_RushJob)
@cutsceneSetup(CutsceneKeyEnum.Pacesetter_RushJob)
def __pacesetterRushJobSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        pacesetter, target, *_ = CSEditorUtil.makeSuits('psetter', 'mh')
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[pacesetter, target], newParent=battle)
    else:
        toons, pacesetter, target, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'pacesetter', 'target', 'battle')

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([pacesetter, target])
    cutsceneLoader.addNodesToCutscene([battle, pacesetter, target])
    return cutsceneLoader
# endregion
# endregion


# region Event Bosses
# TODO: FIX THE ERFIT STUFF. It's a bit broken in editor and I don't feel like fixing it atm.
@cutsceneSetup(CutsceneKeyEnum.Erfit_Intro)
def __erfitIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.DistributedCountErfit import DistributedCountErfit
        instance = DistributedCountErfit(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        instance.bossGeom.reparentTo(render)

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('erfit', 'mh', 'mh', 'mh')

        # make sure these guys are real
        for avatar in toons + suits:
            avatar.reparentTo(render)
    else:
        toons, suits, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'instance')

    dialogue = TTLocalizer.ErfitBloodsuckerIntro + TTLocalizer.ErfitIntroDialogDefault[0]

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=4)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([instance.geom, instance.bossElevatorModel])
    cutsceneLoader.addElevatorsToCutscene([instance.bossElevatorModel])
    cutsceneLoader.addDialogueToCutscene(dialogue)
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Erfit_Intro_Elevator)
def __erfitIntroElevatorSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.DistributedCountErfit import DistributedCountErfit
        instance = DistributedCountErfit(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        instance.bossGeom.reparentTo(render)

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('erfit', 'btto')

        # make sure these guys are real
        for avatar in toons + suits:
            avatar.reparentTo(render)
    else:
        toons, suits, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'instance')

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=4)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([instance.geom, instance.bossElevatorModel])
    cutsceneLoader.addElevatorsToCutscene([instance.bossElevatorModel])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_Intro)
def __highrollerIntroSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()

        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('hroller', 'duckshfl', 'mplayer')
    else:
        toons, suits, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'instance')

    # make sure actors are all on render
    for avatar in suits:
        if avatar:
            avatar.reparentTo(render)
    CSEditorUtil.populateList(toons)

    # Setup Toon pos for better floating
    toonPosNode = render.attachNewNode('toonPosNode')

    for avatar in toons:
        if avatar:
            avatar.reparentTo(toonPosNode)

    cameraAnimPaths = [
        'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot1',
        'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot2',
        'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot3',
        'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot4',
        'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot5',
    ]
    cameraMover = CSEditorUtil.makeCameraMover(*cameraAnimPaths)
    cameraMover.reparentTo(instance.geom)
    cameraMover.setPosHpr(0, 0, 0, 0, 0, 0)
    cameraBone = cameraMover.find('**/CameraBone')

    camAnims = cameraMover.getAnimNames()

    def startFusionCam():
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ActorInterval(cameraMover, camAnims[0]),
            ActorInterval(cameraMover, camAnims[1]),
            ActorInterval(cameraMover, camAnims[2]),
            ActorInterval(cameraMover, camAnims[3]),
            Wait(2.0),
            ActorInterval(cameraMover, camAnims[4]),
        )

    sfx = [loader.loadSfx('phase_11/audio/sfx/LB_camera_shutter_2.ogg'),
           loader.loadSfx('phase_11/audio/sfx/LB_camera_shutter_2.ogg'),
           loader.loadSfx('phase_13/audio/sfx/april_toons/highroller/cc_s_dlg_ene_hroller_good_morning_clash_general.ogg'),
           loader.loadSfx('phase_5/audio/sfx/Toon_bodyfall_synergy.ogg'),
           loader.loadSfx('phase_5/audio/sfx/SA_wager_bust_hit.ogg'),
           loader.loadSfx('phase_5/audio/sfx/SA_finger_wag.ogg'),
           loader.loadSfx('phase_13/audio/sfx/april_toons/highroller/cc_s_dlg_ene_duckshfl_normal_dialog.ogg'),]

    # The comedy anvil!!
    comedyAnvil = globalPropPool.getProp('anvil')
    comedyAnvil.reparentTo(instance.getEnvironment().getGeom())
    from direct.gui.DirectFrame import DirectFrame
    anvilText = DirectFrame(
        parent=comedyAnvil, relief=None,
        pos=(0, 0, 0), scale=1.0, hpr=(0, 0, 0),
        text='The Comedy Anvil',
        text_pos=(0, 0),
        text_fg=(1, 1, 1, 1),
        text_scale=0.3,
    )

    # Starburst
    starburst = loader.loadModel('phase_3.5/models/props/ttcc_gen_starburst')

    # Helper node
    cameraSwapNode = NodePath('swapNode')
    cameraSwapNode.reparentTo(hidden)

    def cleanup():
        if editor:
            return
        for avatar in toons:
            if avatar:
                avatar.wrtReparentTo(render)
        toonPosNode.removeNode()
        cameraMover.delete()
        comedyAnvil.removeNode()
        starburst.removeNode()
        cameraSwapNode.removeNode()

    # Populate cutscene loader
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([suits[0].specialHead, cameraMover, toonPosNode,
                                       instance.getEnvironment().getTV(), instance.getEnvironment().getWheel(),
                                       instance.getEnvironment().getGeom(), suits[2].specialHead, suits[1].specialHead,
                                       suits[0], suits[1], suits[2]] + toons + [comedyAnvil, anvilText, suits[1].nametag3d, suits[2].nametag3d,
                                       suits[0].nametag3d, starburst, cameraSwapNode, cameraBone])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.HighRollerIntro + ['APPLAUSE NOW', 'Oh my Cogth   \n\nthath me', 'Waith I needth to thay it too', 'WARNING\n\nTHE FOLLOWING INSTANCE\nIS NOT CANON', '!'])
    cutsceneLoader.addFunctionsToCutscene([cleanup, startFusionCam])
    cutsceneLoader.addArgumentsToCutscene([instance])
    cutsceneLoader.addSoundsToCutscene(sfx)
    cutsceneLoader.addMusicToCutscene(['highroller_cutscene'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_Death)
def __highrollerDeathSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()

        # Show the wheel
        instance.battleRoom.getWheel().getSpawnWheelSequence().finish()

        toons = CSEditorUtil.makeToons(4)
        localToon = random.choice(toons)
        hroller, *otherSuits = CSEditorUtil.makeSuits('hroller', 'hroller', 'hroller', 'hroller', 'hroller')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller, *otherSuits], newParent=battle)
    else:
        toons, localToon, hroller, otherSuits, battle, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'localToon', 'hroller', 'otherSuits', 'battle', 'instance')

    # Record all the toon's positions so we can return them after all the shenanigans
    toonResetPositions = []
    for toon in toons:
        toonResetPositions.append((toon.getPos(), toon.getHpr()))

    # Dupe some toons in the toons list if we don't have the max of 4
    # This is to handle the ending sequence
    if len(toons) == 1:
        toons = toons * 4
    elif len(toons) == 2:
        toons = toons * 2
    elif len(toons) == 3:
        toons.append(toons[0])
    print(toons)

    # Loading props or models
    ship = globalPropPool.getProp("ship")
    ship.reparentTo(battle)
    ship.hide()

    shadow = loader.loadModel("phase_3/models/props/drop_shadow")
    shadow.reparentTo(battle)
    shadow.hide()

    # The comedy anvil!!
    comedyAnvil = globalPropPool.getProp('anvil')
    comedyAnvil.reparentTo(instance.getEnvironment().getGeom())
    comedyAnvil.setPosHpr(16.709, 43.856, 4.0, -31.233, -1.156, 0.0)
    comedyAnvil.setScale(8)
    from direct.gui.DirectFrame import DirectFrame
    # Anvil Text
    DirectFrame(
        parent=comedyAnvil, relief=None,
        pos=(0, -0.6427, 0.3856), scale=1.0, hpr=(0, 0, 0),
        text='The Comedy Anvil',
        text_pos=(0, 0),
        text_fg=(1, 1, 1, 1),
        text_scale=0.3,
    )
    comedyAnvil.hide()

    # Create buffer node for High Roller head
    # Check to see if it has already be made though
    bufferNode = hroller.find('**/bufferNode')
    if not bufferNode:
        head = hroller.find('**/joint_head')
        children = head.getChildren()
        bufferNode = head.attachNewNode('bufferNode')
        for child in children:
            child.reparentTo(bufferNode)

    # Display region helper functions
    displayRegion = base.camNode.getDisplayRegion(0)

    def displayRegionLerp(dr, start, end, t) -> None:
        dr.setDimensions(lerp(start[0], end[0], t), lerp(start[1], end[1], t), lerp(start[2], end[2], t), lerp(start[3], end[3], t))

    def displayRegionSequence(dr, start, end, duration=0.5) -> LerpFunc:
        return LerpFunc(lambda t: displayRegionLerp(dr, start, end, t), duration=duration)

    def resetBaseDisplayRegion() -> None:
        dr = base.camNode.getDisplayRegion(0)
        dr.setActive(1)
        dr.setDimensions(0, 1, 0, 1)

    # Spawn the gui labels
    guiLabels = []

    from direct.gui.DirectFrame import DirectFrame
    from toontown.toonbase.ToontownGlobals import getSuitFont

    def createLabel(message, wordwrap=20) -> DirectFrame:
        label = DirectFrame(
            parent=render2d,
            relief=None,
            pos=(0, 0, 0), hpr=(0, 0, 0), scale=(0.5, 1.0, 1.0),
            text=message,
            text_font=getSuitFont(),
            text_fg=(1, 1, 1, 1),
            text_wordwrap=wordwrap,
            text_scale=0.075,
        )
        label.hide()
        label.setBin('fixed', 5000)
        guiLabels.append(label)
        return label

    def creditsScrollLerp(t, label) -> None:
        offset = 1.2
        label.resetFrameSize()
        start = -offset
        end = label.getHeight() + offset
        label.setZ(lerp(start, end, t))

    def formatCreditPair(pair) -> str:
        return f'\1TextSubtitle\1{pair[0]}\2\n\1TextShrink\1{pair[1]}\2\n\n'

    # Generate initial credits
    compliedCredits = ''
    for creditPair in CutsceneLocalizer.HighRollerCreditsInitial:
        compliedCredits += formatCreditPair(creditPair)
    initialCreditsLabel = createLabel(compliedCredits)

    # Second credits with titles for the toons
    highRollerLabel = createLabel(formatCreditPair(("High Roller", CutsceneLocalizer.HighRollerCreditsFinal[0])))
    toonLabelOne = createLabel(formatCreditPair((toons[0].getName(), CutsceneLocalizer.HighRollerCreditsFinal[1])))
    toonLabelTwo = createLabel(formatCreditPair((toons[1].getName(), CutsceneLocalizer.HighRollerCreditsFinal[2])))
    toonLabelThree = createLabel(formatCreditPair((toons[2].getName(), CutsceneLocalizer.HighRollerCreditsFinal[3])))
    toonLabelFour = createLabel(formatCreditPair((toons[3].getName(), CutsceneLocalizer.HighRollerCreditsFinal[4])))

    # Freeze frame functions for toons
    def forceToonsToSmile() -> None:
        for toon in toons:
            # Cleanup Eyes (have to close and open eyes to refresh)
            toon.normalEyes()
            toon.closeEyes()
            toon.openEyes()

            # Cleanup Muzzles
            toon.hideSadMuzzle()
            toon.hideSurpriseMuzzle()
            toon.hideLaughMuzzle()
            toon.hideAngryMuzzle()
            toon.hideSmileMuzzle()

            # No Blinking!
            toon.stopBlink()

            # todo: disable emotes during cutscene
            # Make 'em smile!
            toon.showSmileMuzzle()

    def endToonsSmiling() -> None:
        for toon in toons:
            toon.hideSmileMuzzle()
            toon.startBlink()

    # Redefining this here because I think if I import SpecialSuitDeaths then it would be a circular import
    def silhouetteDeathSequence() -> Parallel:
        suitTrack = Parallel()
        delay = 0.0
        for suit in otherSuits:
            deathSound = base.loader.loadSfx('phase_11/audio/sfx/laser_cog_death.ogg')
            suitTrack.append(
                Sequence(
                    Wait(delay),
                    Parallel(
                        SoundInterval(deathSound, duration=1.2, startTime=0, volume=1),
                        LerpScaleInterval(suit, 0.5, 0.01),
                        LerpColorScaleInterval(suit, 0.5, (0, 0, 0, 0))
                    ),
                    Func(suit.stash)
                )
            )
            delay += 0.2
        return suitTrack

    def cleanup() -> None:
        resetBaseDisplayRegion()

        if editor:
            return

        # Cleanup labels
        for label in guiLabels:
            if label:
                label['text'] = ''
                label.setColorScale(1, 1, 1, 0)
                label.destroy()

        # Cleanup props
        ship.removeNode()
        shadow.removeNode()
        comedyAnvil.removeNode()

        # Reset toon positions
        for i, position in enumerate(toonResetPositions):
            toons[i].setPos(position[0])
            toons[i].setHpr(position[1])

    def clearAllVisualEffects():
        for avatar in [hroller] + otherSuits + toons:
            avatar.requestUnapplyAllVisualEffects()

    # Populate cutscene loader
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([hroller] + otherSuits)
    cutsceneLoader.addActorsToCutscene([hroller] + otherSuits + toons)
    cutsceneLoader.addNodesToCutscene([
        hroller, localToon, initialCreditsLabel, ship, shadow, bufferNode, comedyAnvil,
        highRollerLabel, toonLabelOne, toonLabelTwo, toonLabelThree, toonLabelFour
    ])
    cutsceneLoader.addSoundsToCutscene([
        "phase_5/audio/sfx/incoming_whistleALT.ogg",
        "phase_5/audio/sfx/AA_drop_boat.ogg"
    ])
    cutsceneLoader.addDialogueToCutscene(CutsceneLocalizer.HighRollerEndingDialogue)
    from toontown.utils.text import wordwrapWithVerticalCentering
    from toontown.toon import TTEmote
    cutsceneLoader.addFunctionsToCutscene([
        cleanup,
        lambda: displayRegionSequence(displayRegion, (0, 1, 0, 1), (0, 0.6, 0, 1)),
        resetBaseDisplayRegion,
        creditsScrollLerp,
        lambda: displayRegionSequence(displayRegion, (0, 0.6, 0, 1), (0, 1, 0, 1)),
        lambda: displayRegionSequence(displayRegion, (0, 1, 0, 1), (0.4, 1, 0, 1)),
        hroller.specialHead.startFakeNeutral,
        hroller.specialHead.stopFakeNeutral,
        forceToonsToSmile,
        endToonsSmiling,
        instance.battleRoom.freezeAudience,
        instance.battleRoom.unfreezeAudience,
        lambda: displayRegionSequence(displayRegion, (0.4, 1, 0, 1), (1, 1.6, 0, 1), 2.0),
        lambda label: wordwrapWithVerticalCentering(label, 20),
        lambda: TTEmote.globalEmote.disableAll(base.localAvatar),
        lambda: TTEmote.globalEmote.releaseAll(base.localAvatar),
        silhouetteDeathSequence,
        clearAllVisualEffects,
    ])
    cutsceneLoader.addArgumentsToCutscene([
        instance, initialCreditsLabel, highRollerLabel, toonLabelOne, toonLabelTwo, toonLabelThree, toonLabelFour
    ])

    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_PhaseTwo)
def __highrollerPhaseTwoSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()

        # Show the wheel
        instance.battleRoom.getWheel().getSpawnWheelSequence().finish()

        toons = CSEditorUtil.makeToons(4)
        hroller, *otherSuits = CSEditorUtil.makeSuits('hroller', 'mh', 'mh', 'mh')

        # Make them hollys fashionable
        for holly in otherSuits:
            holly.makeExecutive()
            holly.reparentTo(render)
            holly.stash()

        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller], newParent=battle)
    else:
        toons, hroller, otherSuits, battle, instance = CSEditorUtil.getKwargs(kwargs, 'toons', 'hroller', 'otherSuits', 'battle', 'instance')

    uninflatedToons = toons[:]

    # Toon inflation
    CSEditorUtil.populateList(toons, 4)

    # Put them hollys on render
    for holly in otherSuits:
        holly.reparentTo(render)
        holly.stash()

    # Create buffer node for High Roller head
    # Check to see if it has already be made though
    bufferNode = hroller.find('**/bufferNode')
    if not bufferNode:
        head = hroller.find('**/joint_head')
        children = head.getChildren()
        bufferNode = head.attachNewNode('bufferNode')
        for child in children:
            child.reparentTo(bufferNode)

    # Randomly select a phrase from the tuple in the intro end dialogue
    dialogue = CutsceneLocalizer.HighRollerPhaseTwoDialogue[:]
    # Seed randomness with doId so all clients see same thing
    state = random.getstate()
    random.seed(instance.rngSeed)
    dialogue[6] = random.choice(dialogue[6])
    random.setstate(state)
    hroller.setColorScaleOff()

    sounds = [
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_start.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_loop.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_end.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_tone.ogg',
        'phase_9/audio/sfx/SA_hurry_sickness.ogg'
    ]

    def cleanup() -> None:
        if editor:
            return
        # Stash High Roller
        hroller.stash()
        # Reparent the hollys to the battle
        for holly in otherSuits:
            holly.wrtReparentTo(battle)

    # Populate cutscene loader
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([hroller] + otherSuits)
    cutsceneLoader.addActorsToCutscene(toons + [hroller] + otherSuits)
    cutsceneLoader.addNodesToCutscene([hroller, bufferNode, battle] + otherSuits)
    cutsceneLoader.addDialogueToCutscene(dialogue)
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addFunctionsToCutscene([
        cleanup,
        hroller.specialHead.stopFakeNeutral,
        lambda: CSEditorUtil.moveActorsToBattlePositions(toons=uninflatedToons, suits=[hroller], newParent=battle)
    ])
    cutsceneLoader.addArgumentsToCutscene([instance, instance.battleRoom.getWheel().WheelDestination.DEATH])

    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_RandomGame)
def __highrollerRandomGameSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        hroller, *suits = CSEditorUtil.makeSuits('hroller')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller, *suits], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -420
        instance.loadEnvironment()

        wheel = instance.battleRoom.getWheel()
        # Show the wheel
        wheelSeq = wheel.getSpawnWheelSequence()
        wheelSeq.start()
        wheelSeq.finish()
        wheelDest = wheel.WheelDestination(random.randint(0, 2))
    else:
        hroller, battle, toons, wheelDest = CSEditorUtil.getKwargs(kwargs, 'hroller', 'battle', 'toons', 'wheelDest')
        instance = battle.instance

    sounds = [
        'phase_10/audio/dial/ttcc_ene_hroller_laugh.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_start.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_loop.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_end.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_tone.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ene_hroller_sweep_before_wheel.ogg',
        'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ene_hroller_reappear_after_wheel.ogg',
    ]

    # Load in the camera mover with the relevant animations.
    cameraAnimPaths = [
        'phase_12/models/misc/cc_p_cam_highroller-wheelspin',
    ]
    cameraMover = CSEditorUtil.makeCameraMover(*cameraAnimPaths)
    cameraMover.reparentTo(instance.geom)
    cameraMover.setPosHpr(0, 0, 0, 0, 0, 0)
    cameraBone = cameraMover.find('**/CameraBone')

    def cleanup():
        if editor:
            return
        cameraMover.delete()

    def getCameraStartInterval(animName):
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ActorInterval(cameraMover, animName, duration=6.7),
        )

    def getCameraEndInterval(animName):
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ActorInterval(cameraMover, animName, startTime=6.7),
        )
    CSEditorUtil.populateList(toons, n=4)
    cutsceneLoader.addSuitsToCutscene([hroller])
    cutsceneLoader.addActorsToCutscene([hroller])
    cutsceneLoader.addNodesToCutscene([battle, hroller, cameraMover] + toons + [instance.battleRoom.getWheel(), instance.geom])
    cutsceneLoader.addFunctionsToCutscene([cleanup, getCameraStartInterval, getCameraEndInterval, hroller.specialHead.stopFakeNeutral])
    cutsceneLoader.addArgumentsToCutscene([instance, wheelDest] + cameraMover.getAnimNames())
    cutsceneLoader.addSoundsToCutscene(sounds)
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_RandomGameSpawn)
def __highrollerRandomGameSpawnSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        hroller, *suits = CSEditorUtil.makeSuits('hroller', 'sd', 'sd', 'sd', 'sd', 'sd')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller, *suits], newParent=battle)

        for suit in suits:
            suit.reparentTo(render)

        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        suits, battle, hroller = CSEditorUtil.getKwargs(kwargs, 'suits', 'battle', 'hroller')

    CSEditorUtil.populateList(suits, n=5)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addNodesToCutscene([battle] + suits + [hroller])
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.HIGHROLLER_TRIVIA])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_RandomGameSpawn_Podium)
def __highrollerRandomGameSpawnPodiumSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        hroller, *suits = CSEditorUtil.makeSuits('hroller', 'f', 'f', 'f', 'f')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 90, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller, *suits], newParent=battle)

        for suit in suits:
            suit.reparentTo(render)

        questionIndex = 0
        overrideString = "Wow!"

        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
        environment = instance.getEnvironment()
        environment.getSuitPodiumRow().show()
    else:
        instance, suits, battle, hroller, questionIndex, overrideString = \
            CSEditorUtil.getKwargs(kwargs, 'instance', 'suits', 'battle', 'hroller', 'questionIndex', 'overrideString')

    # Custom shift operation to put None suits at the beginning (preserve leftmost property of podiums).
    listShift = []
    for i in range(4 - len(suits)):
        listShift.append(None)
    suits = listShift + suits

    podiumNodes = []
    environment = instance.getEnvironment()
    if environment:
        podiumRow = environment.getSuitPodiumRow()
        for i in range(podiumRow.getPodiumCount()):
            podium = podiumRow.getPodium(i)
            if podium:
                podiumNodes.append(podium)

    CSEditorUtil.populateList(podiumNodes, n=4)

    def safeReparent(index):
        suitIndex = 3 - index
        if suits[suitIndex] and podiumNodes[index]:
            suits[suitIndex].reparentTo(podiumNodes[index])

    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addNodesToCutscene([battle] + suits + [hroller] + podiumNodes + [instance.getEnvironment().getTV()])
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.HIGHROLLER_TRIVIA])
    cutsceneLoader.addDialogueToCutscene([overrideString])
    cutsceneLoader.addFunctionsToCutscene([safeReparent])
    cutsceneLoader.addArgumentsToCutscene([instance] + [questionIndex] + [i for i in range(4)])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_Commercial_Start)
def __highrollerCommercialStartSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        hroller, *suits = CSEditorUtil.makeSuits('hroller')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller, *suits], newParent=battle)

        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        instance, hroller, battle = CSEditorUtil.getKwargs(kwargs, 'instance', 'hroller', 'battle')

    def cleanup():
        if editor:
            return
        hroller.delete()

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([hroller], maxSuitCount=1)
    cutsceneLoader.addNodesToCutscene([battle, hroller])
    cutsceneLoader.addSoundsToCutscene(['phase_5/audio/sfx/SZ_MM_fanfare.ogg'])
    cutsceneLoader.addActorsToCutscene([hroller])
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    cutsceneLoader.addArgumentsToCutscene([instance])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_Commercial_End)
def __highrollerCommercialEndSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()

        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        hroller, *suits = CSEditorUtil.makeSuits('hroller', 'sd', 'sd', 'sd', 'sd')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)

        visualEffect = hroller.addVisualEffect(VisualEffectEnum.HIGHROLLER_COMMERCIAL)
        hroller.reapplyAllVisualEffects()
    else:
        instance, battle, suits, hroller, visualEffect = CSEditorUtil.getKwargs(kwargs, 'instance', 'battle', 'suits', 'hroller', 'visualEffect')

    # Nodes for cutscene
    fakeSuit = visualEffect.fakeSuit

    sounds = ['phase_11/audio/sfx/SA_bash.ogg']

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([fakeSuit] + suits, maxSuitCount=5)
    cutsceneLoader.addActorsToCutscene([fakeSuit])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addNodesToCutscene([battle, fakeSuit, hroller])
    cutsceneLoader.addArgumentsToCutscene([instance])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_CloneSpawn)
def __highrollerCloneSpawnSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        hroller, *suits = CSEditorUtil.makeSuits('hroller', 'hrollerc', 'hrollerc', 'hrollerc', 'hrollerc')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller], newParent=battle)

        for suit in suits:
            suit.reparentTo(render)

        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        suits, battle, hroller = CSEditorUtil.getKwargs(kwargs, 'suits', 'battle', 'hroller')

    for suit in suits:
        suit.reparentTo(battle)

    nametags = []
    for suit in suits:
        nametags.append((suit.nametag3d) if suit else (None))

    CSEditorUtil.populateList(suits, n=4)
    cutsceneLoader.addSuitsToCutscene([hroller] + suits)
    cutsceneLoader.addActorsToCutscene([hroller] + suits)
    cutsceneLoader.addNodesToCutscene([hroller] + suits + nametags)
    cutsceneLoader.addStuffToCutscene(
        battle, VisualEffectEnum.HIGHROLLER_CLONE,
        particleNames=['hr_summon', 'hr_summon', 'hr_summon', 'hr_summon']
    )
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_PhaseThree)
def __highrollerPhaseThreeSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        hroller, *suits = CSEditorUtil.makeSuits('hroller', 'hroller', 'hroller', 'hroller', 'hroller')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller, *suits], newParent=battle)

        for suit in suits:
            suit.reparentTo(render)

        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -420
        instance.loadEnvironment()
    else:
        suits, hroller, battle = CSEditorUtil.getKwargs(kwargs, 'suits', 'hroller', 'battle')

    spotlightNode = render.attachNewNode("spotlightNode")
    cutsceneStagelight = None

    def stagelight_in_center():
        nonlocal cutsceneStagelight
        from toontown.utils import ColorHelper
        target = spotlightNode
        stagelightAlpha = 0.28
        fadeawayDuration = 1.0
        litDuration = 5.0

        # Hack to clear a stagelight
        if cutsceneStagelight is not None:
            cutsceneStagelight.removeNode()
            del cutsceneStagelight
            cutsceneStagelight = None

        # Make the stagelight.
        stagelight = globalPropPool.getProp('stagelight')
        cutsceneStagelight = stagelight
        stagelight.hide()
        node = stagelight.node()
        node.setBounds(OmniBoundingVolume())
        node.setFinal(1)
        stagelight.find('**/stagelight').hide()

        # Position the stagelight.
        stagelight.reparentTo(target)
        stagelight.setPos(0, 0, 15 * 4)
        stagelight.setScale(2, 2, 4)
        stagelight.setColor(ColorHelper.hexToPCol('FEFDA8', a=int(stagelightAlpha * 255)))

        target.setColorScale(1, 1, 1, 1)

        # Stagelight SFX sequence
        soundIval = SoundInterval(sound=loader.loadSfx('phase_11/audio/sfx/LB_camera_shutter_2.ogg'))

        if fadeawayDuration != 0.0:
            soundIval = Parallel(
                soundIval,
                Sequence(
                    Wait(litDuration),
                    LerpColorInterval(
                        nodePath=stagelight, duration=fadeawayDuration,
                        color=ColorHelper.hexToPCol('FEFDA8', a=0),
                        startColor=ColorHelper.hexToPCol('FEFDA8', a=int(stagelightAlpha * 255)),
                        blendType='easeOut',
                    ),
                    Func(stagelight.hide),
                )
            )

        return Sequence(
            Func(stagelight.show),
            # (Func(target.overrideClearScaleFunc, target) if disableColorScale else Wait(0.0)),
            soundIval,
        )

    def cleanup():
        if editor:
            return
        nonlocal cutsceneStagelight
        if cutsceneStagelight is not None:
            cutsceneStagelight.removeNode()
            del cutsceneStagelight
            cutsceneStagelight = None
        spotlightNode.remove()

    sounds = [
        'phase_10/audio/dial/ttcc_ene_hroller_laugh.ogg',
    ]

    def startHrSuitSeq():
        if editor:
            return
        battle.hrChangeSeq.start()

    CSEditorUtil.populateList(suits, n=4)
    cutsceneLoader.addSuitsToCutscene([hroller] + suits)
    cutsceneLoader.addActorsToCutscene([hroller] + suits)
    # dont judge me for this one
    cutsceneLoader.addNodesToCutscene([battle] + suits + [hroller, spotlightNode])
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.HIGHROLLER_CLONE])
    cutsceneLoader.addDialogueToCutscene(TTLocalizer.HighRollerAfterimages)
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addFunctionsToCutscene([stagelight_in_center, cleanup, hroller.specialHead.stopFakeNeutral, startHrSuitSeq])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_Clone_Trap)
def __highRollerTrapSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('duckshfl', 'duckshfl', 'duckshfl', 'duckshfl', 'duckshfl', 'duckshfl')
        room = loader.loadModel('phase_3.5/models/schoolhouse/schoolhouse_interior_basement')
        room.reparentTo(render)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        toons, suits, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'battle')

    # Get props for the cutscene.
    bar_a = globalPropPool.getProp("goldbar")
    bar_a.reparentTo(battle)
    bar_a.hide()
    bar_b = globalPropPool.getProp("goldbar")
    bar_b.reparentTo(battle)
    bar_b.hide()
    shadow_a = loader.loadModel("phase_3/models/props/square_drop_shadow")
    shadow_a.reparentTo(battle)
    shadow_a.hide()
    shadow_b = loader.loadModel("phase_3/models/props/square_drop_shadow")
    shadow_b.reparentTo(battle)
    shadow_b.hide()

    # reference node for the explosion
    explosionRefNode_a = battle.attachNewNode('explosionRefNodeA')
    explosionRefNode_b = battle.attachNewNode('explosionRefNodeB')

    # Explosion for when he throws guitar at ground
    explosion_a = loader.loadModel('phase_3.5/models/props/explosion.bam')
    explosion_a.setBillboardPointEye()
    explosion_a.setDepthWrite(False)
    explosion_a.hide()
    explosion_a.reparentTo(explosionRefNode_a)

    explosion_b = loader.loadModel('phase_3.5/models/props/explosion.bam')
    explosion_b.setBillboardPointEye()
    explosion_b.setDepthWrite(False)
    explosion_b.hide()
    explosion_b.reparentTo(explosionRefNode_b)

    kapow = globalPropPool.getProp('kapow')
    kapow.reparentTo(explosionRefNode_a)
    kapow.hide()
    kapow.setScale(0.25)
    kapow.setBillboardPointEye()

    explosionSound = ['phase_3.5/audio/sfx/ENC_cogfall_apart.ogg']

    def explode():
        ActorInterval(kapow, 'kapow').start()

    def cleanup():
        if editor:
            return
        bar_a.removeNode()
        bar_b.removeNode()
        shadow_a.removeNode()
        shadow_b.removeNode()
        explosion_a.removeNode()
        explosion_b.removeNode()
        kapow.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=6)
    cutsceneLoader.addNodesToCutscene(
        [battle, bar_a, bar_b, shadow_a, shadow_b, explosionRefNode_a, explosionRefNode_b, explosion_a, explosion_b, kapow]
    )
    cutsceneLoader.addSoundsToCutscene(explosionSound)
    cutsceneLoader.addFunctionsToCutscene([cleanup, explode])
    cutsceneLoader.addArgumentsToCutscene([bar_a, bar_b])
    return cutsceneLoader
# endregion


@cutsceneSetup(CutsceneKeyEnum.HighRoller_FreeCruise)
def __highRollerFreeCruiseSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()

        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('hroller', 'hroller', 'hroller', 'hroller', 'hroller', 'hroller')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        toons, suits, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'battle')

    # Get props for the cutscene.
    ship = globalPropPool.getProp("ship")
    ship.reparentTo(battle)
    ship.hide()
    shadow = loader.loadModel("phase_3/models/props/drop_shadow")
    shadow.reparentTo(battle)
    shadow.hide()

    def cleanup():
        if editor:
            return
        ship.removeNode()
        shadow.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=6)
    cutsceneLoader.addNodesToCutscene(
        [battle, ship, shadow]
    )
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_FreeCruiseMissed)
def __highRollerFreeCruiseMissedSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()
        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('hroller', 'hroller', 'hroller', 'hroller', 'hroller', 'hroller')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        toons, suits, battle = CSEditorUtil.getKwargs(kwargs, 'toons', 'suits', 'battle')

    # Get props for the cutscene.
    ship = globalPropPool.getProp("ship")
    ship.reparentTo(battle)
    ship.hide()
    shadow = loader.loadModel("phase_3/models/props/drop_shadow")
    shadow.reparentTo(battle)
    shadow.hide()

    def cleanup():
        if editor:
            return
        ship.removeNode()
        shadow.removeNode()

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=6)
    cutsceneLoader.addNodesToCutscene([battle, ship, shadow])
    cutsceneLoader.addFunctionsToCutscene([cleanup])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_DiceRouletteNothing)
def __highRollerDiceRouletteNothingSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()

        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('hroller', 'hroller', 'hroller', 'hroller', 'hroller', 'hroller')
        hroller = suits[0]
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        setDicePair = (random.randint(1, 6), 5)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        hroller, battle, setDicePair = CSEditorUtil.getKwargs(kwargs, 'hroller', 'battle', 'setDicePair')
        instance = battle.instance
    fanfare = globalBattleSoundCache.getSound('SZ_MM_fanfare.ogg')
    diceSelect = base.loader.loadSfx('phase_4/audio/sfx/MG_sfx_travel_game_red_arrow.ogg')
    hrFacingNode = NodePath('hr-facing-node')

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene([hroller])
    cutsceneLoader.addActorsToCutscene([hroller])
    cutsceneLoader.addNodesToCutscene([battle, instance.getEnvironment().getTV(), hrFacingNode, hroller])
    cutsceneLoader.addSoundsToCutscene([fanfare, diceSelect, diceSelect, diceSelect, diceSelect])
    cutsceneLoader.addDialogueToCutscene(
        [random.choice(CutsceneLocalizer.HighRollerDiceRouletteDialog[0]),
         random.choice(CutsceneLocalizer.HighRollerDiceRouletteDialog[1])])
    cutsceneLoader.addArgumentsToCutscene(
        [instance, *[(random.randint(1, 6), random.randint(1, 6)) for _ in range(12)], setDicePair])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_DiceRouletteSuitsDamaged)
def __highRollerDiceRouletteSuitsDamagedSetup(editor: bool, **kwargs) -> CutsceneLoader:
    diceSize = 2.0
    fallDuration = 0.4
    bounceDuration = 0.25
    bounceHeightAmt = 2.25
    bounceRotateAmt = (10.0, 20.0, 20.0)
    diceSizeVariance = {1: 0.65, 2: 0.75, 3: 0.85, 4: 0.95, 5: 1.05, 6: 1.15}

    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()

        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('hroller', 'hroller', 'hroller', 'hroller', 'hroller')
        hroller = suits[0]
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        setDicePair = (random.randint(1, 6), 6)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        hroller, battle, setDicePair = CSEditorUtil.getKwargs(kwargs, 'hroller', 'battle', 'setDicePair')
        suits = battle.activeSuits[:]
        instance = battle.instance
    diceSize *= diceSizeVariance.get(setDicePair[0], 1)
    fanfare = globalBattleSoundCache.getSound('SZ_MM_fanfare.ogg')
    diceSelect = globalBattleSoundCache.getSound('MG_sfx_travel_game_red_arrow.ogg')
    fallingWhistle = globalBattleSoundCache.getSound('incoming_whistle.ogg')
    dropSfx = globalBattleSoundCache.getSound('AA_drop_bigweight.ogg')
    CSEditorUtil.populateList(suits, 6)
    hrFacingNode = NodePath('hr-facing-node')
    if hroller in suits and hroller != suits[0]:
        suits.remove(hroller)
        suits.insert(0, hroller)

    # Get props for the cutscene.
    dice = []
    shadows = []
    for suit in suits:
        if not suit:
            continue
        dice.append(globalPropPool.getProp("dice"))
        dice[-1].reparentTo(suit)
        dice[-1].setPosHprScale(0, 0, 60, *(random.choice([0, 90, 180, -90]) for _ in range(3)), *(diceSize for _ in range(3)))
        shadows.append(loader.loadModel("phase_3/models/props/drop_shadow"))
        shadows[-1].reparentTo(suit)
        shadows[-1].setPosHprScale(0, 0, 0.01, 0, 0, 0, 0, 0, 0)
        shadows[-1].setColor(0, 0, 0, 0.5)

    def cleanup():
        if editor:
            return
        [node.removeNode() for node in [*dice, *shadows]]

    def dropDice():
        dieHprs = [die.getHpr() for die in dice]
        dieRandomBounce = [random.uniform(-bounceRotateAmt[0], bounceRotateAmt[0]) for _ in dice]
        return Parallel(*[Sequence(
            Wait(1.5 - fallDuration),
            LerpPosInterval(die, duration=fallDuration, pos=(0, 0, diceSize)),
            Parallel(
                Sequence(
                    LerpPosInterval(die, duration=bounceDuration / 2, pos=(0, 0, diceSize + bounceHeightAmt), blendType='easeOut'),
                    LerpPosInterval(die, duration=bounceDuration / 2, pos=(0, 0, diceSize), blendType='easeIn')),
                Sequence(
                    LerpHprInterval(die, duration=bounceDuration / 2, blendType='easeOut', hpr=(
                        dieHprs[i][0] + dieRandomBounce[i] / 2,
                        dieHprs[i][1] + random.uniform(-bounceRotateAmt[1], bounceRotateAmt[1]),
                        dieHprs[i][2] + random.uniform(-bounceRotateAmt[2], bounceRotateAmt[2]))),
                    LerpHprInterval(die, duration=bounceDuration / 2, blendType='easeIn', hpr=(
                        dieHprs[i][0] + dieRandomBounce[i] / 2, dieHprs[i][1], dieHprs[i][2])))))
            for i, die in enumerate(dice)], *[LerpScaleInterval(shadow, duration=1.5, scale=1.5) for shadow in shadows])

    def diceGoByeBye():
        return Sequence(Parallel(*[LerpScaleInterval(node, duration=0.15, scale=0) for node in [*dice, *shadows]]), Func(cleanup))

    # Populate cutscene loader.
    cutsceneLoader.addSuitsToCutscene(suits, maxSuitCount=6)
    cutsceneLoader.addActorsToCutscene([hroller])
    cutsceneLoader.addNodesToCutscene([battle, instance.getEnvironment().getTV(), hrFacingNode, hroller, *dice, *shadows])
    cutsceneLoader.addSoundsToCutscene([fanfare, diceSelect, diceSelect, diceSelect, diceSelect, fallingWhistle, dropSfx])
    cutsceneLoader.addDialogueToCutscene(
        [random.choice(CutsceneLocalizer.HighRollerDiceRouletteDialog[0]),
         random.choice(CutsceneLocalizer.HighRollerDiceRouletteDialog[2])])
    cutsceneLoader.addArgumentsToCutscene(
        [instance, *[(random.randint(1, 6), random.randint(1, 6)) for _ in range(12)], setDicePair])
    cutsceneLoader.addFunctionsToCutscene([dropDice, diceGoByeBye])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_DiceRouletteToonsDamaged)
def __highRollerDiceRouletteToonsDamagedSetup(editor: bool, **kwargs) -> CutsceneLoader:
    diceSize = 1.5
    fallDuration = 0.2
    bounceDuration = 0.25
    bounceHeightAmt = 2.25
    bounceRotateAmt = (7.5, 5.0, 10.0)
    diceSizeVariance = {1: 0.6, 2: 0.7, 3: 0.8, 4: 0.9, 6: 1.1}

    cutsceneLoader = CutsceneLoader()
    if editor:
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -11
        instance.loadEnvironment()

        # Load environment and actors
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('hroller', 'hroller', 'hroller', 'hroller', 'hroller')
        hroller = suits[0]
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        setDicePair = (random.randint(1, 6), random.randint(1, 4))
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        toons, hroller, battle, setDicePair = CSEditorUtil.getKwargs(kwargs, 'toons', 'hroller', 'battle', 'setDicePair')
        instance = battle.instance
    diceSize *= diceSizeVariance.get(setDicePair[0], 1)
    fanfare = globalBattleSoundCache.getSound('SZ_MM_fanfare.ogg')
    diceSelect = globalBattleSoundCache.getSound('MG_sfx_travel_game_red_arrow.ogg')
    fallingWhistle = globalBattleSoundCache.getSound('incoming_whistle.ogg')
    dropSfx = globalBattleSoundCache.getSound('AA_drop_bigweight.ogg')
    if __debug__:
        while len(toons) > setDicePair[1]:
            toons.remove(random.choice(toons))
    CSEditorUtil.populateList(toons, 4)
    hrFacingNode = NodePath('hr-facing-node')

    # Get props for the cutscene.
    dice = []
    shadows = []
    for toon in toons:
        if not toon:
            continue
        dice.append(globalPropPool.getProp("dice"))
        dice[-1].reparentTo(toon)
        dice[-1].setPosHprScale(0, 0, 60, *(random.choice([0, 90, 180, -90]) for _ in range(3)), *(diceSize for _ in range(3)))
        shadows.append(loader.loadModel("phase_3/models/props/drop_shadow"))
        shadows[-1].reparentTo(toon)
        shadows[-1].setPosHprScale(0, 0, 0.01, 0, 0, 0, 0, 0, 0)
        shadows[-1].setColor(0, 0, 0, 0.5)

    def cleanup():
        if editor:
            return
        [node.removeNode() for node in [*dice, *shadows]]

    def dropDice():
        dieHprs = [die.getHpr() for die in dice]
        dieRandomBounce = [random.uniform(-bounceRotateAmt[0], bounceRotateAmt[0]) for _ in dice]
        return Parallel(*[Sequence(
            Wait(1.5 - fallDuration),
            LerpPosInterval(die, duration=fallDuration, pos=(0, 0, diceSize)),
            Parallel(
                Sequence(
                    LerpPosInterval(die, duration=bounceDuration / 2, pos=(0, 0, diceSize + bounceHeightAmt), blendType='easeOut'),
                    LerpPosInterval(die, duration=bounceDuration / 2, pos=(0, 0, diceSize), blendType='easeIn')),
                Sequence(
                    LerpHprInterval(die, duration=bounceDuration / 2, blendType='easeOut', hpr=(
                        dieHprs[i][0] + dieRandomBounce[i] / 2,
                        dieHprs[i][1] + random.uniform(-bounceRotateAmt[1], bounceRotateAmt[1]),
                        dieHprs[i][2] + random.uniform(-bounceRotateAmt[2], bounceRotateAmt[2]))),
                    LerpHprInterval(die, duration=bounceDuration / 2, blendType='easeIn', hpr=(
                        dieHprs[i][0] + dieRandomBounce[i] / 2, dieHprs[i][1], dieHprs[i][2])))))
            for i, die in enumerate(dice)], *[LerpScaleInterval(shadow, duration=1.5, scale=1.5) for shadow in shadows])

    def diceGoByeBye():
        return Sequence(Parallel(*[LerpScaleInterval(node, duration=0.15, scale=0) for node in [*dice, *shadows]]), Func(cleanup))

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([hroller], maxSuitCount=6)
    cutsceneLoader.addActorsToCutscene([hroller])
    cutsceneLoader.addNodesToCutscene([battle, instance.getEnvironment().getTV(), hrFacingNode, hroller, *dice, *shadows])
    cutsceneLoader.addSoundsToCutscene([fanfare, diceSelect, diceSelect, diceSelect, diceSelect, fallingWhistle, dropSfx])
    cutsceneLoader.addDialogueToCutscene(
        [random.choice(CutsceneLocalizer.HighRollerDiceRouletteDialog[0]),
         random.choice(CutsceneLocalizer.HighRollerDiceRouletteDialog[3])])
    cutsceneLoader.addArgumentsToCutscene(
        [instance, *[(random.randint(1, 6), random.randint(1, 6)) for _ in range(12)], setDicePair])
    cutsceneLoader.addFunctionsToCutscene([dropDice, diceGoByeBye])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_AceInTheHole)
def __highrollerAceInTheHoleSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        suits = CSEditorUtil.makeSuits('hroller', 'hroller', 'hroller', 'hroller', 'hroller')
        hroller = suits[0]
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -7
        instance.loadEnvironment()
        instance.getEnvironment().makeEnterPhaseSequence(5.0).finish()

    else:
        hroller, battle = CSEditorUtil.getKwargs(kwargs, 'hroller', 'battle')
        toons = battle.activeToons[:]
        suits = battle.activeSuits[:]
    if hroller in suits and hroller != suits[0]:
        suits.remove(hroller)
        suits.insert(0, hroller)
    CSEditorUtil.populateList(toons, 4)
    CSEditorUtil.populateList(suits, 6)
    suitColorDict = {}

    # Loading card and High Roller's head.
    # Getting High Roller's Head (Spawn fake HR and remove head)
    from direct.actor.Actor import Actor
    animDict = {
        "ace-in-the-hole": "phase_12/models/char/suits/cc_m_chr_ene_highroller-ace-in-the-hole",
        "neutral": "cc_m_chr_ene_highroller-neutral"
    }
    rollerHead = Actor("phase_12/models/char/suits/cc_m_chr_ene_highroller-zero", animDict)
    rollerHead.setBlend(frameBlend=base.wantSmoothAnims)
    rollerHead.reparentTo(render)
    rollerHead.hide()

    # Function to use rollerHead animation.
    def getHeadAnim():
        return ActorInterval(rollerHead, 'ace-in-the-hole')

    def doHeadNeutral():
        return Func(rollerHead.loop, 'neutral')

    # Make card actor.
    animDict = {
        "slam": "phase_5/models/props/cc_m_anim_bat_prp_playing_card-slam",
        "wind-up": "phase_5/models/props/cc_m_anim_bat_prp_playing_card-wind-up"
    }
    cardActor = Actor("phase_5/models/props/cc_m_chr_bat_prp_playing_card", animDict)
    cardActor.setBlend(frameBlend=base.wantSmoothAnims)
    cardActor.reparentTo(render)
    cardActor.hide()
    tex = loader.loadTexture('phase_5/maps/battle_props/cc_t_bat_prp_card_front_ace_hr.png')
    tex.setMinfilter(Texture.FTLinearMipmapLinear)
    tex.setMagfilter(Texture.FTLinear)
    cardActor.replaceTexture(cardActor.findTexture('cc_t_bat_prp_card_front'), tex)

    # Functions to use card animations.
    def getSlamAnim():
        return ActorInterval(cardActor, 'slam')

    def getWindUpAnim():
        return ActorInterval(cardActor, 'wind-up')

    def createSuitStepBackTrack():
        masterTrack = Parallel()
        delay = 0.0
        for suit in [suit for suit in suits if suit]:
            def getStepBackPos():
                return suit.getPos(battle) + Point3(9, 25, 0)

            suitColorDict[suit] = suit.getColorScale()
            moveDuration = 5.0
            walkTrack = Sequence(
                ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05, loop=1),
                Func(suit.loop, 'neutral'),
            )
            moveTrack = LerpPosInterval(suit, moveDuration, getStepBackPos)
            fadeTrack = LerpColorScaleInterval(suit, moveDuration,
                (suitColorDict[suit][0], suitColorDict[suit][1], suitColorDict[suit][2], 0.0), blendType='easeOut')
            masterTrack.append(Sequence(Wait(delay), Parallel(walkTrack, fadeTrack, moveTrack)))
            # Delay between each suit
            delay += 0.1
        return masterTrack

    def cleanup():
        from toontown.battle.BattleBase import BattleBase
        existingSuits = getattr(battle, "activeSuits", [suit for suit in suits if suit])
        existingToons = getattr(battle, "activeToons", [toon for toon in toons if toon])
        suitPointList = BattleBase.suitPoints[len(existingSuits) - 1]
        toonPointList = BattleBase.toonPoints[len(existingToons) - 1]
        for i, suit in enumerate(existingSuits):
            xyz, h = suitPointList[i]
            suit.setPos(xyz)
            suit.setH(h)
            suit.setColorScale(*suitColorDict[suit])
        for i, toon in enumerate(existingToons):
            xyz, h = toonPointList[i]
            toon.setPos(xyz)
            toon.setH(h)
        cardActor.cleanup()

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits + toons)
    cutsceneLoader.addNodesToCutscene([hroller, battle, rollerHead, cardActor])
    cutsceneLoader.addFunctionsToCutscene([createSuitStepBackTrack, getHeadAnim, getWindUpAnim, getSlamAnim, doHeadNeutral, cleanup])
    cutsceneLoader.addDialogueToCutscene([random.choice(CutsceneLocalizer.HighRollerAceInTheHoleDialogue[0])])

    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.HighRoller_MinigameResults)
def __highrollerMinigameResultsSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        toons = CSEditorUtil.makeToons(4)
        hroller, *suits = CSEditorUtil.makeSuits('hroller', 'f', 'f', 'f', 'f')
        battle = render.attachNewNode('battle')
        battle.setPosHpr(0, 35, 4, 0, 0, 0)
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=[hroller, *suits], newParent=battle)
        from toontown.instances.mercs.DistributedInstanceHighroller import DistributedInstanceHighroller
        instance = DistributedInstanceHighroller(base.cr)
        instance.doId = -7
        instance.loadEnvironment()
        # Which toons succeeded?
        successfulToons = random.sample(toons, random.randint(1, 4))
    else:
        toons, hroller, instance, battle, successfulToons = CSEditorUtil.getKwargs(kwargs, 'toons', 'hroller', 'instance', 'battle', 'successfulToons')
        suits = battle.activeSuits[:]
    sounds = [
        'phase_4/audio/sfx/target_happydance.ogg',
        'phase_5/audio/sfx/SZ_MM_fanfare.ogg'
    ]

    hroller.wrtReparentTo(render)

    # Emote for toons
    def toonsReact() -> None:
        for i, toon in enumerate(toons):
            # Cleanup Eyes (have to close and open eyes to refresh)
            toon.normalEyes()
            toon.closeEyes()
            toon.openEyes()

            # Cleanup Muzzles
            toon.hideSadMuzzle()
            toon.hideSurpriseMuzzle()
            toon.hideLaughMuzzle()
            toon.hideAngryMuzzle()
            toon.hideSmileMuzzle()

            # Based on index, do a different emote/expression
            # Also, based on if toons should be happy or not
            if toon in successfulToons:
                if i == 0:
                    # Surprise
                    toon.doEmote(20)
                elif i == 1:
                    # Bow
                    toon.doEmote(13)
                    toon.showLaughMuzzle()
                elif i == 2:
                    # Applause
                    toon.doEmote(9)
                    toon.showSmileMuzzle()
                elif i == 3:
                    # Happy
                    toon.doEmote(1)
                    toon.showSmileMuzzle()
            else:
                if i == 0:
                    # Cringe
                    toon.doEmote(10)
                    toon.showSadMuzzle()
                    toon.sadEyes()
                    toon.closeEyes()
                    toon.openEyes()
                elif i == 1:
                    # Furious
                    toon.doEmote(23)
                elif i == 2:
                    # Confused
                    toon.doEmote(11)
                elif i == 3:
                    # Shrug
                    toon.doEmote(5)
                    toon.sadEyes()
                    toon.closeEyes()
                    toon.openEyes()

    def resetToonExpressions() -> None:
        for toon in toons:
            # Cleanup Eyes (have to close and open eyes to refresh)
            toon.normalEyes()
            toon.closeEyes()
            toon.openEyes()

            # Cleanup Muzzles
            toon.hideSadMuzzle()
            toon.hideSurpriseMuzzle()
            toon.hideLaughMuzzle()
            toon.hideAngryMuzzle()
            toon.hideSmileMuzzle()

    def createSuitStepBackTrack():
        masterTrack = Parallel()
        delay = 0.0
        for suit in suits:
            def getStepBackPos(suit=suit):
                return suit.getPos() + Point3(0, 4, 0)

            moveDuration = 0.8
            walkTrack = Sequence(
                ActorInterval(suit, 'walk', startTime=1, duration=moveDuration, endTime=1e-05),
                Func(suit.loop, 'neutral'),
            )
            moveTrack = LerpPosInterval(suit, moveDuration, getStepBackPos, other=battle)
            masterTrack.append(Sequence(Wait(delay), Parallel(walkTrack, moveTrack)))
            # Delay between each suit
            delay += 0.6
        return masterTrack

    cutsceneLoader.addToonsToCutscene(toons, maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene([hroller])
    cutsceneLoader.addActorsToCutscene([hroller] + toons)
    cutsceneLoader.addNodesToCutscene([hroller.specialHead, battle])
    cutsceneLoader.addSoundsToCutscene(sounds)
    cutsceneLoader.addDialogueToCutscene([
        random.choice(CutsceneLocalizer.HighRollerMinigameResultsDialogue[0]),
        CutsceneLocalizer.HighRollerMinigameResultsDialogue[1]
    ])
    cutsceneLoader.addFunctionsToCutscene([toonsReact, resetToonExpressions])

    return cutsceneLoader


# region Litigation Team
@cutsceneSetup(CutsceneKeyEnum.Litigator_Bellow)
def __litigatorBellowSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load the environment, Litigator and Toons
        from toontown.instances.mercs.DistributedInstancePrethinker import DistributedInstancePrethinker
        instance = DistributedInstancePrethinker(base.cr)
        instance.doId = -12
        instance.loadEnvironment()
        suits = CSEditorUtil.makeSuits('lgator', 'bw', 'bw', 'bw', 'bw', 'sgoat')
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(suits=suits, newParent=battle)
        litigator = suits[0]
    else:
        litigator, battle = CSEditorUtil.getKwargs(kwargs, 'litigator', 'battle')

    affectsCamera, *_ = CSEditorUtil.getKwargs(kwargs, 'affectsCamera')

    cameraAnimPaths = [
        'phase_11/models/misc/camera_actor-litigator-bellow',
    ]
    cameraMover = CSEditorUtil.makeCameraMover(*cameraAnimPaths)
    cameraMover.reparentTo(litigator)
    cameraMover.setPosHpr(0, 0, 0, 0, 0, 0)
    cameraBone = cameraMover.find('**/CameraBone')

    def getCameraInterval(animName, affectsCamera=affectsCamera):
        if not affectsCamera:
            return Sequence()
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ActorInterval(cameraMover, animName),
        )

    def getCameraLoop(animName, affectsCamera=affectsCamera):
        if not affectsCamera:
            return Sequence()
        return Sequence(
            Func(base.camera.reparentTo, cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            Func(cameraMover.loop, animName),
        )

    # Populate cutscene loader
    cutsceneLoader.addSuitsToCutscene([litigator])
    cutsceneLoader.addActorsToCutscene([litigator])
    cutsceneLoader.addNodesToCutscene([litigator, litigator.specialHead, battle, cameraMover])
    cutsceneLoader.addSoundsToCutscene(['phase_11/audio/sfx/SA_bellow.ogg'])
    cutsceneLoader.addFunctionsToCutscene([getCameraInterval, getCameraLoop])
    cutsceneLoader.addArgumentsToCutscene(cameraMover.getAnimNames())
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Scapegoat_Enraged)
def __scapegoatEnragedSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load environment, Spawn cogs and toons.
        from toontown.instances.mercs.DistributedInstancePrethinker import DistributedInstancePrethinker
        instance = DistributedInstancePrethinker(base.cr)
        instance.doId = -12
        instance.loadEnvironment()
        suits = CSEditorUtil.makeSuits('sgoat', 'bw', 'bw', 'lgator')
        scapegoat = suits[0]
        toons = CSEditorUtil.makeToons(4)
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(toons=toons, suits=suits, newParent=battle)
    else:
        scapegoat, toons, battle = CSEditorUtil.getKwargs(kwargs, 'scapegoat', 'toons', 'battle')

    # Populate cutscene loader
    cutsceneLoader.addSuitsToCutscene([scapegoat])
    cutsceneLoader.addToonsToCutscene(toons)
    cutsceneLoader.addActorsToCutscene([scapegoat] + toons)
    cutsceneLoader.addNodesToCutscene([scapegoat, battle])
    cutsceneLoader.addSoundsToCutscene(['phase_11/audio/sfx/SA_rage.ogg'])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.CaseManager_Insurance)
def __casemanagerInsuranceSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if editor:
        # Load environment & actors
        from toontown.instances.mercs.DistributedInstancePrethinker import DistributedInstancePrethinker
        instance = DistributedInstancePrethinker(base.cr)
        instance.doId = -12
        instance.loadEnvironment()
        suits = CSEditorUtil.makeSuits('caseman', 'bw', 'bw', 'bw', 'bw', 'stenog')
        casemanager = suits[0]
        battle = render.attachNewNode('battle')
        CSEditorUtil.moveActorsToBattlePositions(suits=suits, newParent=battle)
    else:
        casemanager, suits, battle = CSEditorUtil.getKwargs(kwargs, 'casemanager', 'suits', 'battle')

    # Populate cutscene loader
    cutsceneLoader.addSuitsToCutscene([casemanager])
    cutsceneLoader.addActorsToCutscene([casemanager])
    cutsceneLoader.addNodesToCutscene([casemanager, casemanager.specialHead, battle])
    cutsceneLoader.addSoundsToCutscene([
        'phase_11/audio/sfx/SA_insurance.ogg',
        'phase_5/audio/sfx/SA_extra_tip.ogg'
    ])
    return cutsceneLoader
# endregion


# region Clash Meta
@cutsceneSetup(CutsceneKeyEnum.Trailer_HiresAndHeroesOpeningA)
def __trailerHiresAndHeroesOpeningASetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if not editor:
        raise CutsceneSetupException

    # Get the NPCs!
    names = TTLocalizer.NPCToonNames
    from toontown.toon.npc.NPCToons import NPCToon
    toons = CSEditorUtil.makeToonsFromNPCToons(
        NPCToon(6818, names[6301], 'mls', 'ms', 's', 'm', (0.325, 0.407, 0.601, 1.0), (0.325, 0.407, 0.601, 1.0), (0.325, 0.407, 0.601, 1.0), 122, 57, 109, 57, 51, 57, hat=14),
        NPCToon(6816, names[6302], 'dll', 'ls', 's', 'f', (0.242, 0.742, 0.516, 1.0), (0.242, 0.742, 0.516, 1.0), (0.242, 0.742, 0.516, 1.0), 7, 7, 7, 7, 9, 22),
        NPCToon(6817, names[6303], 'xls', 'md', 's', 'm', (0.576, 0.439, 0.859, 1.0), (0.576, 0.439, 0.859, 1.0), (0.576, 0.439, 0.859, 1.0), 15, 5, 11, 5, 166, 9),
        NPCToon(6819, names[6304], 'fll', 'sd', 'l', 'm', (0.804, 0.498, 0.196, 1.0), (0.804, 0.498, 0.196, 1.0), (0.804, 0.498, 0.196, 1.0), 9, 6, 9, 6, 8, 3),
        NPCToon(6821, names[6305], 'dss', 'ls', 'l', 'm', (0.996, 0.255, 0.392, 1.0), (0.996, 0.255, 0.392, 1.0), (0.996, 0.255, 0.392, 1.0), 6, 2, 6, 2, 161, 22),
        NPCToon(6836, names[6306], 'fll', 'ms', 'm', 'f', (0.968, 0.749, 0.349, 1.0), (0.968, 0.749, 0.349, 1.0), (0.968, 0.749, 0.349, 1.0), 17, 7, 0, 7, 2, 18),
        NPCToon(6835, names[6307], 'rsl', 'ss', 'l', 'm', (0.641, 0.355, 0.27, 1.0), (0.641, 0.355, 0.27, 1.0), (0.641, 0.355, 0.27, 1.0), 7, 12, 7, 12, 160, 9),
        NPCToon(6823, names[6308], 'dsl', 'ms', 'l', 'm', (0.749, 1.0, 0.847, 1.0), (0.749, 1.0, 0.847, 1.0), (0.749, 1.0, 0.847, 1.0), 19, 3, 13, 3, 160, 1),
        NPCToon(6824, names[6309], 'mss', 'ss', 'm', 'f', (0.996, 0.957, 0.598, 1.0), (0.996, 0.957, 0.598, 1.0), (0.996, 0.957, 0.598, 1.0), 9, 9, 9, 9, 1, 20),
        NPCToon(6825, names[6310], 'mls', 'ls', 'm', 'm', (0.749, 1.0, 0.847, 1.0), (0.749, 1.0, 0.847, 1.0), (0.749, 1.0, 0.847, 1.0), 10, 27, 0, 27, 159, 0),
        NPCToon(6826, names[6311], 'csl', 'ls', 'l', 'm', (0.984, 0.537, 0.396, 1.0), (0.984, 0.537, 0.396, 1.0), (0.984, 0.537, 0.396, 1.0), 5, 9, 5, 9, 159, 10),
        NPCToon(6827, names[6312], 'rsl', 'md', 'l', 'f', (0.89, 0.812, 0.341, 1.0), (0.89, 0.812, 0.341, 1.0), (0.89, 0.812, 0.341, 1.0), 13, 11, 11, 11, 0, 7),
        NPCToon(6828, names[6313], 'rll', 'ls', 'm', 'm', (0.855, 0.934, 0.492, 1.0), (0.855, 0.934, 0.492, 1.0), (0.855, 0.934, 0.492, 1.0), 19, 9, 13, 9, 5, 14),
        NPCToon(6829, names[6314], 'mls', 'ss', 's', 'm', (0.968, 0.749, 0.349, 1.0), (0.968, 0.749, 0.349, 1.0), (0.968, 0.749, 0.349, 1.0), 5, 8, 5, 8, 162, 11),
        NPCToon(6831, names[6315], 'cll', 'ss', 's', 'm', (1.0, 1.0, 0.941, 1.0), (1.0, 1.0, 0.941, 1.0), (1.0, 1.0, 0.941, 1.0), 5, 3, 5, 3, 158, 11),
        NPCToon(6832, names[6316], 'hls', 'ss', 'l', 'm', (0.996, 0.695, 0.512, 1.0), (0.996, 0.695, 0.512, 1.0), (0.996, 0.695, 0.512, 1.0), 11, 10, 0, 10, 162, 14),
        NPCToon(6833, names[6317], 'fls', 'ss', 'l', 'm', (0.285, 0.328, 0.727, 1.0), (0.285, 0.328, 0.727, 1.0), (0.285, 0.328, 0.727, 1.0), 8, 1, 8, 1, 160, 12),
        NPCToon(6834, names[6318], 'dll', 'ss', 'm', 'f', (0.434, 0.906, 0.836, 1.0), (0.434, 0.906, 0.836, 1.0), (0.434, 0.906, 0.836, 1.0), 22, 11, 0, 11, 9, 2),
        NPCToon(6315, names[2421], 'ess', 'ms', 'm', 'f', 12, 12, 12, 203, 27, 187, 27, 289, 27),
    )

    # Load the cutscene.
    from toontown.dna.DNAStorage import DNAStorage
    from toontown.dna.DNAParser import DNABulkLoader
    safeZoneStorageDNAFile = 'phase_6/dna/storage_OZ_sz.pdna'
    storageDNAFile = 'phase_6/dna/storage_OZ.pdna'
    dnaFile = 'phase_6/dna/outdoor_zone_6300.pdna'
    dnaStore = DNAStorage()
    files = ('phase_4/dna/storage.pdna',
             'phase_3.5/dna/storage_interior.pdna',
             storageDNAFile,
             safeZoneStorageDNAFile,
             'phase_5/dna/storage_town.pdna', 'phase_6/dna/storage_OZ_town.pdna')
    dnaBulk = DNABulkLoader(dnaStore, files)
    dnaBulk.loadDNAFiles()
    node = loader.loadDNAFile(dnaStore, dnaFile)
    scene = render.attachNewNode(node)
    scene.show()

    cameraStart = render.attachNewNode('cameraStart')
    toonBase = render.attachNewNode('toonBase')
    for toon in toons:
        toon.reparentTo(toonBase)
        toon.show()

    # Add sky
    sky = loader.loadModel('phase_3.5/models/props/TT_sky')
    sky.reparentTo(render)
    sky.show()
    from toontown.hood import SkyUtil
    SkyUtil.startCloudSky(hood=None, parent=cameraStart, sky=sky)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons)
    cutsceneLoader.addActorsToCutscene(toons)
    cutsceneLoader.addNodesToCutscene([cameraStart, toonBase] + toons + [])
    cutsceneLoader.addDialogueToCutscene([
        "I LOVE TOONTOWN"
    ])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Trailer_HiresAndHeroesOpeningB)
def __trailerHiresAndHeroesOpeningBSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if not editor:
        raise CutsceneSetupException

    names = TTLocalizer.NPCToonNames
    from toontown.toon.npc.NPCToons import NPCToon
    toons = CSEditorUtil.makeToonsFromNPCToons(
        NPCToon(2643, names[2123], 'cls', 'md', 'l', 'f', 4, 4, 4, 0, 5, 0, 5, 14, 27, hat=40),
        NPCToon(2644, names[2124], 'dll', 'sd', 'l', 'f', 21, 21, 21, 0, 5, 0, 5, 8, 21, hat=115, glasses=23),
        NPCToon(2649, names[2125], 'dss', 'ss', 'l', 'm', 12, 12, 12, 254, 27, 227, 27, 159, 10, hat=83, glasses=3),
        NPCToon(2654, names[2126], 'dls', 'ld', 'l', 'f', 4, 4, 4, 167, 27, 153, 27, 44, 27, hat=12, glasses=13, backpack=23),
        NPCToon(2655, names[2127], 'fsl', 'ms', 'l', 'm', 19, 19, 19, 82, 36, 71, 35, 209, 40, hat=24, glasses=17, shoes=1, shoesTex=31),
        NPCToon(2656, names[2128], 'fss', 'ss', 'l', 'm', 12, 12, 12, 65, 27, 54, 27, 200, 27, hat=47, glasses=3, backpack=66, shoes=3, shoesTex=40),
        NPCToon(2657, names[2129], 'rll', 'ss', 'l', 'm', 4, 4, 4, 1, 5, 1, 5, 156, 9, hat=103, glasses=1),
        NPCToon(2659, names[2130], 'rss', 'md', 'l', 'f', 19, 19, 19, 17, 15, 0, 15, 8, 37, glasses=14, backpack=71),
        NPCToon(2660, names[2131], 'rls', 'ls', 'l', 'f', 12, 12, 12, 1, 8, 1, 8, 1, 26, hat=27, glasses=12, backpack=7, shoes=1, shoesTex=10),
        NPCToon(2661, names[2132], 'mls', 'ss', 'l', 'm', 4, 4, 4, 206, 27, 190, 27, 5, 17, hat=25, glasses=1, backpack=30, shoes=3, shoesTex=26),  # Daffy Don
        NPCToon(2662, names[2133], 'hll', 'ls', 'l', 'm', 18, 18, 18, 99, 26, 126, 26, 155, 39, hat=96, hatColor=35, glasses=13, shoes=2, shoesTex=18),  # Dr. Euphoric
        NPCToon(2664, names[2134], 'zss', 'ms', 'm', 'f', (0.996, 0.255, 0.392, 1.0), (0.996, 0.255, 0.392, 1.0), (0.996, 0.255, 0.392, 1.0), 207, 27, 191, 27, 271, 27, hat=99),
        NPCToon(2665, names[2135], 'hls', 'ms', 'l', 'f', 3, 3, 3, 0, 12, 0, 12, 2, 26, hat=17, glasses=7, backpack=15, shoes=2, shoesTex=14),
        NPCToon(2666, names[2136], 'csl', 'ls', 'l', 'm', 18, 18, 18, 118, 27, 105, 27, 162, 15, hat=45, shoes=2, shoesTex=8),
        NPCToon(2667, names[2137], 'css', 'sd', 'l', 'f', 11, 11, 11, 0, 21, 0, 21, 24, 27),
        NPCToon(2669, names[2138], 'dll', 'ss', 'l', 'm', 3, 3, 3, 0, 39, 0, 39, 156, 39, hat=51, glasses=7, shoes=2, shoesTex=21),
        NPCToon(2670, names[2139], 'fsl', 'ms', 'l', 'm', (0.898, 0.617, 0.906, 1.0), (0.898, 0.617, 0.906, 1.0), (0.898, 0.617, 0.906, 1.0), 149, 27, 136, 27, 63, 27, hat=13, backpack=80, shoes=1, shoesTex=10),
        NPCToon(2156, names[2140], 'dls', 'ls', 'l', 'm', 10, 10, 10, 1, 9, 1, 9, 156, 10, hat=18),
    )
    suits = CSEditorUtil.makeSuits('duckshfl')
    ducky = suits[0]
    ducky.reparentTo(render)
    ducky.specialHead.setEyePos(0.27)

    # Load the cutscene.
    from toontown.dna.DNAStorage import DNAStorage
    from toontown.dna.DNAParser import DNABulkLoader
    safeZoneStorageDNAFile = 'phase_4/dna/storage_TT_sz.pdna'
    storageDNAFile = 'phase_4/dna/storage_TT.pdna'
    dnaFile = 'phase_5/dna/toontown_central_2100.pdna'
    dnaStore = DNAStorage()
    files = (
        'phase_4/dna/storage.pdna',
        'phase_3.5/dna/storage_interior.pdna',
        storageDNAFile,
        safeZoneStorageDNAFile,
        'phase_5/dna/storage_town.pdna',
        'phase_5/dna/storage_TT_town.pdna',
    )
    dnaBulk = DNABulkLoader(dnaStore, files)
    dnaBulk.loadDNAFiles()
    node = loader.loadDNAFile(dnaStore, dnaFile)
    scene = render.attachNewNode(node)
    scene.show()

    cameraStart = render.attachNewNode('cameraStart')
    cameraShake = render.attachNewNode('cameraShake')
    toonBase = render.attachNewNode('toonBase')
    toonBase2 = render.attachNewNode('toonBase2')
    for toon in toons:
        toon.reparentTo(toonBase)
        toon.show()
    toons[9].reparentTo(toonBase2)
    toons[12].reparentTo(toonBase2)
    toons[17].reparentTo(toonBase2)
    daffy = toons[9]

    # Add sky
    sky = loader.loadModel('phase_3.5/models/props/TT_sky')
    sky.reparentTo(render)
    sky.show()
    from toontown.hood import SkyUtil
    SkyUtil.startCloudSky(hood=None, parent=cameraStart, sky=sky)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene(toons)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(toons)
    cutsceneLoader.addNodesToCutscene([cameraStart, toonBase, toonBase2] + toons + [cameraShake, ducky, daffy.toonGlasses.accessoryGeom])
    cutsceneLoader.addDialogueToCutscene([
        "I LOVE TOONTOWN"
    ])
    cutsceneLoader.addArgumentsToCutscene([0])
    return cutsceneLoader


@cutsceneSetup(CutsceneKeyEnum.Trailer_MajorPlayer)
def __majorplayerTrailerSetup(editor: bool, **kwargs) -> CutsceneLoader:
    cutsceneLoader = CutsceneLoader()
    if not editor:
        raise CutsceneSetupException

    from toontown.instances.mercs.DistributedInstanceMajorplayer import DistributedInstanceMajorplayer
    instance = DistributedInstanceMajorplayer(base.cr)
    instance.doId = -420
    instance.loadEnvironment(overrideSuitCount=24)
    suits = CSEditorUtil.makeSuits(
        'duckshfl', 'ddiver', 'gatekeep', 'bellring', 'mouthp', 'fires', 'treek', 'fbed',
        'prethink', 'rainmake', 'whunter', 'mslacker', 'mplayer', 'pcrat', 'chainsaw', 'psetter',
        'charon', 'nix', 'hydra', 'styx', 'kerberos', 'ptjockey', 'ptjockey'
    )
    fbed = suits[7]
    fires = suits[5]
    psetter = suits[15]
    ddiver = suits[1]
    gatekeep = suits[2]

    for suit in suits:
        suit.reparentTo(render)
        suit.makeExecutive()

    def init():
        def overrideClearScaleFunc(suit):
            suit.setColorScale(1, 1, 1, 1)
        for suit in suits:
            suit.setColorScale(0, 0, 0, 1)
            setattr(suit, 'overrideClearScaleFunc', overrideClearScaleFunc)

    # Populate cutscene loader.
    cutsceneLoader.addToonsToCutscene([], maxToonCount=4)
    cutsceneLoader.addSuitsToCutscene(suits)
    cutsceneLoader.addActorsToCutscene(suits)
    cutsceneLoader.addNodesToCutscene(suits + [instance.geom, instance.battleRoom.discoballs[1],
                                               fbed.specialHead,
                                               fires.specialHead,
                                               psetter.specialHead,
                                               ddiver.nametag3d,
                                               gatekeep.nametag3d,
                                               psetter.nametag3d,])
    cutsceneLoader.addDialogueToCutscene([
        "\1white\1\5bossbot\5 \2Major Player\n\1TextSmaller\1Medley Monstrosity\2",
        "\1white\1\5cashbot\5 \2Duck Shuffler\n\1TextSmaller\1Roulette Rigmarole\2",
        "\1white\1\5sellbot\5 \2Prethinker\n\1TextSmaller\1Boastful Brainiac\2",
        "\1white\1\5lawbot\5 \2Rainmaker\n\1TextSmaller\1Sorrowful Sympathist\2",
        "\1white\1\5sellbot\5 \2Bellringer\n\1TextSmaller\1Eavesdropping Earpopper\2",
        "\1white\1\5boardbot\5 \2Deep Diver\n\1TextSmaller\1Sidewalk Swimmer\2",
        "\1white\1\5cashbot\5 \2Treekiller\n\1TextSmaller\1Wretched Woodsplitter\2",
        "\1white\1\5bossbot\5 \2Chainsaw Consultant\n\1TextSmaller\1Temperamental Terminator\2",
        "\1white\1\5sellbot\5 \2Multislacker\n\1TextSmaller\1Professional Procrastinator\2",
        "\1white\1\5lawbot\5 \2Mouthpiece\n\1TextSmaller\1Rusty Ringleader\2",
        "\1white\1\5lawbot\5 \2Witch Hunter\n\1TextSmaller\1Mob Master\2",
        "\1white\1\5bossbot\5 \2Featherbedder\n\1TextSmaller\1Soundless Sleeper\2",
        "\1white\1\5boardbot\5 \2Gatekeeper\n\1TextSmaller\1Vainglorious Vanguard\2",
        "\1white\1\5cashbot\5 \2Plutocrat\n\1TextSmaller\1Galactic Godfather\2",
        "\1white\1\5bossbot\5 \2Firestarter\n\1TextSmaller\1Apprehensive Arsonist\2",
        "\1white\1\5sellbot\5 \2Pacesetter\n\1TextSmaller\1Expeditious Egotist\2",
        "\1white\1\5cashbot\5 \2Charon\n",
        "\1white\1\5cashbot\5 \2Nix\n",
        "\1white\1\5cashbot\5 \2Hydra\n",
        "\1white\1\5cashbot\5 \2Styx\n",
        "\1white\1\5cashbot\5 \2Kerberos\n",
    ])
    cutsceneLoader.addElevatorsToCutscene([instance.elevatorModel])
    cutsceneLoader.addFunctionsToCutscene([init])
    cutsceneLoader.addVisualEffectsToCutscene([VisualEffectEnum.AFTERIMAGE, VisualEffectEnum.DIVING])
    cutsceneLoader.addArgumentsToCutscene([0])
    return cutsceneLoader
# endregion
