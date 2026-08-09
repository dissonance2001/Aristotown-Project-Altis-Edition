from direct.actor import Actor
from direct.interval.IntervalGlobal import ActorInterval, Func, LerpPosInterval, Parallel, Sequence, Wait
from panda3d.core import Point3

from toontown.cutscene.AltisCutsceneCompat import (
    cacheResolvedControls,
    configureSuitNametag,
    validateExistingMultipartAnimations,
    validateExistingSuitAnimations,
)
from toontown.cutscene.ChainsawIntroCutscene import installChainsawBattleHead
from toontown.cutscene.repository.CutsceneRuntime import buildCutscene
from toontown.suit import Suit
from toontown.suit import SuitDNA


DEATH_PATH = 'phase_12/data/cutscenes/chainsawconsultant/chainsawconsultant_death.ctsc'
ENDING_PATH = 'phase_12/data/cutscenes/chainsawconsultant/chainsawconsultant_ending.ctsc'

DEATH_DIALOGUE = (
    "OVERRIDE- \1CHOVER\1it-\2 SEVERE- \1CHOVER\1hurts-\2 SEVERELY DAMA- \1CHOVER\1let-\2 DAMAGED. ATTEMPT- \1CHOVER\1me-\2 ATTEMPTING- \1CHOVER\1OUT!!\2 FINAL FALLBACK PROCEDURE.",
    "Awaiting orders, sir!",
    "Um, sir?",
    "I don't think he's getting up.",
    "Listen here, Toons, you probably think this is a cowardly move, and you're right.",
    "But you have no idea what it's like to work under that Suit.",
    "You saw nothing.",
)

ENDING_DIALOGUE = (
    "Ugh.",
    "That damned override...",
    "I wish I never worked for this company in the first place!",
    "If you see Spruce, don't tell him what you saw here.",
    "That Suit is like a brother to me. The only one I have.",
    "If he knew what I've become, he would abandon me in fear... like all the others.",
    "You should leave as soon as possible.",
    "I don't want you to be here when that monster comes back.",
    "Go.",
)

DEATH_BODY_ANIMS = ('neutral', 'walk', 'leap', 'laying')
DEATH_HEAD_ANIMS = ('neutral', 'leap', 'laying')
ENDING_BODY_ANIMS = ('laying', 'getup', 'hurt-neutral', 'todesk', 'desk-neutral')
ENDING_HEAD_ANIMS = ('laying', 'getup', 'hurt-neutral', 'todesk', 'desk-neutral')


class ChainsawDeathSetup(object):

    def __init__(self, suit, battle):
        self.suit = suit
        self.battle = battle
        self.controller = getattr(battle, 'bossCog', None)
        self.head = None
        self.otherSuits = []
        self.fakeSuit = None
        self.cameraMover = None
        self.cameraBone = None
        self.suitAnimationMaps = []
        self.suitAnimationControls = []
        self.suitHeadAnimationControls = []

    def _allToons(self):
        result = []
        for toon in getattr(self.battle, 'activeToons', ()):
            if toon and not hasattr(toon, 'doId'):
                try:
                    toon = base.cr.doId2do.get(toon)
                except:
                    toon = None
            if toon and toon not in result:
                result.append(toon)
        while len(result) < 4:
            result.append(None)
        return result[:4]

    def _prepareChainsaw(self):
        self.head = installChainsawBattleHead(self.suit, 3)
        if self.head is None:
            raise RuntimeError('[Chainsaw Death CTSC] Could not install Chainsaw head')
        validateExistingSuitAnimations(
            self.suit, DEATH_BODY_ANIMS, 'Chainsaw death body',
            logPrefix='[Chainsaw Death CTSC]')
        validateExistingSuitAnimations(
            self.head, DEATH_HEAD_ANIMS, 'Chainsaw death head',
            logPrefix='[Chainsaw Death CTSC]')

    def _prepareFakeSuit(self):
        dna = SuitDNA.SuitDNA()
        dna.newSuit('ym')
        fake = Suit.Suit()
        fake.setDNA(dna)
        fake.dna = dna
        fake.doId = -2552
        fake.getActualLevel = lambda: 3
        fake.reparentTo(self.controller.geom)
        fake.setPosHpr(0, 0, 0, 0, 0, 0)
        fake.loop('neutral')
        fake.hide()
        configureSuitNametag(fake, visible=False)
        self.fakeSuit = fake

    def _prepareOtherSuits(self):
        for suit in getattr(self.battle, 'activeSuits', ()):
            if suit is self.suit:
                continue
            try:
                if suit.getHP() <= 0:
                    continue
            except:
                pass
            if suit and suit not in self.otherSuits:
                self.otherSuits.append(suit)
        self.otherSuits = self.otherSuits[:4]

    def _prepareCameraMover(self):
        path = 'phase_3.5/models/misc/camera_actor'
        anim = 'chainsaw-cutscene-leap'
        animPath = 'phase_12/models/misc/camera_actor-chainsaw-cutscene-leap'
        self.cameraMover = Actor.Actor(path, {anim: animPath})
        self.cameraMover.reparentTo(self.controller.geom)
        self.cameraMover.setPosHpr(0, 0, 0, 0, 0, 0)
        self.cameraBone = self.cameraMover.find('**/CameraBone')
        if self.cameraBone.isEmpty():
            raise RuntimeError('[Chainsaw Death CTSC] Camera mover has no CameraBone')

    def _makeAnimationCaches(self, suits):
        for index, suit in enumerate(suits):
            if suit is None:
                self.suitAnimationMaps.append({})
                self.suitAnimationControls.append({})
                self.suitHeadAnimationControls.append({})
                continue
            if suit is self.suit:
                bodyNames = DEATH_BODY_ANIMS
                headNames = DEATH_HEAD_ANIMS
                self.suitAnimationMaps.append(suit.generateAnimDict().copy())
                self.suitAnimationControls.append(cacheResolvedControls(
                    suit, bodyNames, 'Chainsaw death body',
                    logPrefix='[Chainsaw Death CTSC]'))
                self.suitHeadAnimationControls.append(cacheResolvedControls(
                    self.head, headNames, 'Chainsaw death head',
                    logPrefix='[Chainsaw Death CTSC]'))
            else:
                validateExistingSuitAnimations(
                    suit, ('neutral', 'walk'), 'Chainsaw death suit %s' % index,
                    logPrefix='[Chainsaw Death CTSC]')
                self.suitAnimationMaps.append(suit.generateAnimDict().copy())
                self.suitAnimationControls.append(cacheResolvedControls(
                    suit, ('neutral', 'walk'), 'Chainsaw death suit %s' % index,
                    logPrefix='[Chainsaw Death CTSC]'))
                self.suitHeadAnimationControls.append({})

    def _validateToons(self, toons):
        for toon in toons:
            if toon:
                validateExistingMultipartAnimations(
                    toon, ('neutral', 'walk', 'sidestep-right'),
                    'Chainsaw death Toon %s' % getattr(toon, 'doId', '?'),
                    logPrefix='[Chainsaw Death CTSC]')

    def _getCameraInterval(self, animName):
        return Sequence(
            Func(camera.reparentTo, self.cameraBone),
            Func(camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ActorInterval(self.cameraMover, animName))

    def _getCameraLoop(self, animName):
        return Sequence(
            Func(camera.reparentTo, self.cameraBone),
            Func(camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            Func(self.cameraMover.loop, animName))

    def _stepBackSuits(self):
        track = Parallel()
        delay = 0.0
        for suit in self.otherSuits:
            moveDuration = 0.8
            pos = suit.getPos(self.battle) + Point3(0, 4, 0)
            walk = Sequence(
                ActorInterval(
                    suit, 'walk', startTime=1, duration=moveDuration,
                    endTime=0.00001, partName='modelRoot'),
                Func(suit.loop, 'neutral'))
            move = LerpPosInterval(
                suit, moveDuration, pos, other=self.battle)
            track.append(Sequence(Wait(delay), Parallel(walk, move)))
            delay += 0.6
        return track

    def _exitGlitch(self):
        try:
            self.head.endSemiGlitchFreakout()
        except:
            pass
        try:
            self.head.setChainsawTexRoll(0)
        except:
            pass
        self.head.exitGlitch()

    def _reparentOtherSuits(self):
        for suit in self.otherSuits:
            try:
                suit.wrtReparentTo(self.controller.geom)
            except:
                pass

    def _snapshotEndingActor(self):
        scene = getattr(self.controller, 'sceneSuit', None)
        if scene is None:
            return
        try:
            pos = self.suit.getPos(render)
            hpr = self.suit.getHpr(render)
            scale = self.suit.getScale(render)
            scene.reparentTo(render)
            scene.setPos(render, pos)
            scene.setHpr(render, hpr)
            scene.setScale(scale)
            head = installChainsawBattleHead(scene, 3)
            if head:
                head.exitGlitch()
                head.loop('laying')
            scene.loop('laying')
            scene.hide()
        except Exception as error:
            print('[Chainsaw Death CTSC] Could not preserve ending actor: %s' % error)

    def _cleanup(self):
        self._snapshotEndingActor()
        try:
            camera.wrtReparentTo(self.battle)
        except:
            pass
        if self.fakeSuit:
            try:
                self.fakeSuit.cleanup()
            except:
                try:
                    self.fakeSuit.removeNode()
                except:
                    pass
            self.fakeSuit = None
        if self.cameraMover:
            try:
                self.cameraMover.cleanup()
            except:
                try:
                    self.cameraMover.removeNode()
                except:
                    pass
            self.cameraMover = None

    def _makeDict(self):
        if self.controller is None or getattr(self.controller, 'geom', None) is None:
            raise RuntimeError('[Chainsaw Death CTSC] Chainsaw controller is unavailable')
        self._prepareChainsaw()
        self._prepareOtherSuits()
        self._prepareFakeSuit()
        self._prepareCameraMover()
        toons = self._allToons()
        self._validateToons(toons)
        suits = [self.suit, self.fakeSuit] + self.otherSuits
        while len(suits) < 6:
            suits.append(None)
        self._makeAnimationCaches(suits)
        fakeHead = self.fakeSuit.find('**/joint_head')
        bufferNode = fakeHead.attachNewNode('bufferNode')
        for child in fakeHead.getChildren():
            if child != bufferNode:
                child.reparentTo(bufferNode)
        nodes = [
            render,
            hidden,
            camera,
            self.battle,
            self.cameraMover,
            self.suit,
            self.fakeSuit,
            bufferNode,
            self.controller.cogEntrance_1_1,
            self.controller.cogEntrance_1_2,
        ]
        return {
            'nodes': nodes,
            'affectsCamera': True,
            'maxPlayers': 4,
            'toons': toons,
            'suits': suits,
            'actors': suits,
            'messages': DEATH_DIALOGUE,
            'sounds': [
                loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg'),
                loader.loadSfx('phase_9/audio/sfx/CHQ_door_close.ogg'),
                loader.loadSfx('phase_12/audio/sfx/instance_chainsawconsultant_ctscn_death.ogg'),
            ],
            'music': ['phase_12/audio/bgm/merc/instance_chainsaw_end.ogg'],
            'particles': [],
            'visualEffects': [],
            'functions': [
                self._cleanup,
                self._getCameraInterval,
                self._getCameraLoop,
                self._stepBackSuits,
                self._exitGlitch,
                self.head.enterGlitch,
                self._reparentOtherSuits,
            ],
            'arguments': ['chainsaw-cutscene-leap'],
            'bosses': [],
            'elevators': [],
            'suppressSuitNametags': True,
            'suitAnimationMaps': self.suitAnimationMaps,
            'suitAnimationControls': self.suitAnimationControls,
            'suitHeadAnimationControls': self.suitHeadAnimationControls,
        }

    def build(self):
        try:
            self.controller.stopChainsawBattleMusic()
        except:
            pass
        track = buildCutscene(DEATH_PATH, self._makeDict())
        cameraFixes = Parallel(
            Sequence(Wait(17.25), Func(camera.wrtReparentTo, render)),
            Sequence(Wait(26.05), Func(camera.wrtReparentTo, self.battle)))
        return Parallel(track, cameraFixes)


class ChainsawEndingSetup(object):

    def __init__(self, controller):
        self.controller = controller
        self.chainsaw = controller.sceneSuit
        self.head = None
        self.cameraMover = None
        self.cameraBone = None
        self.throwableChair = None
        self.actualToons = []
        self.toons = []

    def _prepareToons(self):
        for toonId in self.controller.involvedToons:
            toon = self.controller.cr.doId2do.get(toonId)
            if toon and toon not in self.actualToons:
                toon.wrtReparentTo(render)
                validateExistingMultipartAnimations(
                    toon, ('neutral', 'walk', 'run'),
                    'Chainsaw ending Toon %s' % toonId,
                    logPrefix='[Chainsaw Ending CTSC]')
                self.actualToons.append(toon)
        local = localAvatar if localAvatar in self.actualToons else None
        ordered = []
        if local:
            ordered.append(local)
        for toon in self.actualToons:
            if toon not in ordered:
                ordered.append(toon)
        while len(ordered) < 4:
            ordered.append(None)
        self.toons = ordered[:4]
        return local

    def _prepareChainsaw(self):
        if self.chainsaw is None:
            raise RuntimeError('[Chainsaw Ending CTSC] Persistent Chainsaw actor is unavailable')
        self.chainsaw.wrtReparentTo(render)
        self.chainsaw.show()
        self.chainsaw.unstash()
        self.head = installChainsawBattleHead(self.chainsaw, 3)
        if self.head is None:
            raise RuntimeError('[Chainsaw Ending CTSC] Could not install Chainsaw head')
        self.head.exitGlitch()
        validateExistingSuitAnimations(
            self.chainsaw, ENDING_BODY_ANIMS, 'Chainsaw ending body',
            logPrefix='[Chainsaw Ending CTSC]')
        validateExistingSuitAnimations(
            self.head, ENDING_HEAD_ANIMS, 'Chainsaw ending head',
            logPrefix='[Chainsaw Ending CTSC]')
        configureSuitNametag(self.chainsaw, visible=False)

    def _prepareCameraMover(self):
        path = 'phase_3.5/models/misc/camera_actor'
        animations = {
            'chainsaw-cutscene-laying': 'phase_12/models/misc/camera_actor-chainsaw-cutscene-laying',
            'chainsaw-cutscene-getup-cam1': 'phase_12/models/misc/camera_actor-chainsaw-cutscene-getup-cam1',
            'chainsaw-cutscene-getup-cam2': 'phase_12/models/misc/camera_actor-chainsaw-cutscene-getup-cam2',
            'chainsaw-cutscene-todesk': 'phase_12/models/misc/camera_actor-chainsaw-cutscene-todesk',
        }
        self.cameraMover = Actor.Actor(path, animations)
        self.cameraMover.reparentTo(self.controller.geom)
        self.cameraMover.setPosHpr(0, 0, 0, 0, 0, 0)
        self.cameraBone = self.cameraMover.find('**/CameraBone')
        if self.cameraBone.isEmpty():
            raise RuntimeError('[Chainsaw Ending CTSC] Camera mover has no CameraBone')

    def _prepareChair(self):
        self.throwableChair = Actor.Actor(
            'phase_12/models/props/chair_actor',
            {'getThrown': 'phase_12/models/props/chair_actor-todesk'})
        self.throwableChair.reparentTo(self.controller.geom)
        self.throwableChair.pose('getThrown', 0)

    def _getCameraInterval(self, animName):
        return Sequence(
            Func(camera.reparentTo, self.cameraBone),
            Func(camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ActorInterval(self.cameraMover, animName))

    def _getCameraLoop(self, animName):
        return Sequence(
            Func(camera.reparentTo, self.cameraBone),
            Func(camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            Func(self.cameraMover.loop, animName))

    def _resetChair(self):
        self.throwableChair.pose('getThrown', 0)

    def _getChairThrownInterval(self):
        return ActorInterval(self.throwableChair, 'getThrown')

    def _fadeOut(self):
        base.transitions.fadeOut(0)

    def _forceUnhurt(self):
        try:
            self.head.exitGlitch()
        except:
            pass

    def _cleanup(self):
        try:
            camera.wrtReparentTo(render)
        except:
            pass
        if self.cameraMover:
            try:
                self.cameraMover.cleanup()
            except:
                try:
                    self.cameraMover.removeNode()
                except:
                    pass
            self.cameraMover = None
        if self.throwableChair:
            try:
                self.throwableChair.cleanup()
            except:
                try:
                    self.throwableChair.removeNode()
                except:
                    pass
            self.throwableChair = None
        try:
            self.chainsaw.hide()
        except:
            pass

    def _makeDict(self):
        self._prepareChainsaw()
        local = self._prepareToons()
        if local is None:
            raise RuntimeError('[Chainsaw Ending CTSC] Local Toon is unavailable')
        self._prepareCameraMover()
        self._prepareChair()
        bodyMap = self.chainsaw.generateAnimDict().copy()
        bodyControls = cacheResolvedControls(
            self.chainsaw, ENDING_BODY_ANIMS, 'Chainsaw ending body',
            logPrefix='[Chainsaw Ending CTSC]')
        headControls = cacheResolvedControls(
            self.head, ENDING_HEAD_ANIMS, 'Chainsaw ending head',
            logPrefix='[Chainsaw Ending CTSC]')
        return {
            'nodes': [
                render,
                hidden,
                camera,
                self.cameraMover,
                self.cameraMover,
                self.chainsaw,
            ],
            'affectsCamera': True,
            'maxPlayers': 4,
            'toons': self.toons,
            'suits': [self.chainsaw],
            'actors': [self.chainsaw, local],
            'messages': ENDING_DIALOGUE,
            'sounds': [
                loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg'),
                loader.loadSfx('phase_9/audio/sfx/CHQ_door_close.ogg'),
                loader.loadSfx('phase_12/audio/sfx/instance_chainsawconsultant_ctscn_end_main.ogg'),
                loader.loadSfx('phase_12/audio/sfx/instance_chainsawconsultant_ctscn_end_shuffling.ogg'),
                loader.loadSfx('phase_12/audio/sfx/instance_chainsawconsultant_ctscn_end_yell.ogg'),
                loader.loadSfx('phase_12/audio/sfx/instance_chainsawconsultant_ctscn_end_footsteps.ogg'),
            ],
            'music': [],
            'particles': [],
            'visualEffects': [],
            'functions': [
                self._cleanup,
                self._getCameraInterval,
                self._getCameraLoop,
                self._resetChair,
                self._getChairThrownInterval,
                base.transitions.noTransitions,
                self._fadeOut,
                self._forceUnhurt,
            ],
            'arguments': [
                'chainsaw-cutscene-laying',
                'chainsaw-cutscene-getup-cam1',
                'chainsaw-cutscene-getup-cam2',
                'chainsaw-cutscene-todesk',
            ],
            'bosses': [],
            'elevators': [],
            'suppressSuitNametags': True,
            'suitAnimationMaps': [bodyMap],
            'suitAnimationControls': [bodyControls],
            'suitHeadAnimationControls': [headControls],
        }

    def build(self):
        track = buildCutscene(ENDING_PATH, self._makeDict())
        cameraFix = Sequence(Wait(36.85), Func(camera.wrtReparentTo, render))
        return Parallel(track, cameraFix)


def makeChainsawDeath(suit, battle):
    return ChainsawDeathSetup(suit, battle).build()


def makeChainsawEnding(controller):
    return ChainsawEndingSetup(controller).build()
