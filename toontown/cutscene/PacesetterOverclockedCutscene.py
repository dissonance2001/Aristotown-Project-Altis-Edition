"""Corporate Clash Pacesetter Overclocked transition adapter for Altis/Python 2."""

from direct.interval.IntervalGlobal import Func, LerpFunctionInterval, Parallel, Sequence, Wait

from toontown.cutscene.AltisCutsceneCompat import (
    cacheResolvedControls,
    getAnimatedHead,
    validateExistingMultipartAnimations,
    validateExistingSuitAnimations,
)
from toontown.cutscene.repository.CutsceneRuntime import buildCutscene


GUITAR_CUTSCENE_PATH = 'phase_9/data/cutscenes/pacesetter/pacesetter_guitarsolo.ctsc'
GUI_CUTSCENE_PATH = 'phase_9/data/cutscenes/pacesetter/pacesetter_overclockedgui.ctsc'
GUITAR_MODEL_PATH = 'phase_9/models/char/paceGuitar'
EXPLOSION_MODEL_PATH = 'phase_3.5/models/props/explosion.bam'
OVERCLOCKED_SFX_PATH = 'phase_9/audio/sfx/SA_overclocked.ogg'
EXPLOSION_SFX_PATH = 'phase_3.5/audio/sfx/ENC_cogfall_apart.ogg'
AFTERIMAGE_EFFECT = 'AFTERIMAGE'

PACESETTER_BODY_ANIMS = ('overclocked', 'neutral')
PACESETTER_HEAD_ANIMS = ('overclocked', 'neutral')
TOON_ANIMS = ('conked', 'neutral')


class PacesetterOverclockedSetup(object):

    def __init__(self, attack, battleSpeed=6):
        self.attack = attack
        self.battleSpeed = battleSpeed
        self.suit = attack['suit']
        self.battle = attack['battle']
        self.toons = list(getattr(self.battle, 'activeToons', []))
        self.controller = self._findController()
        self.head = None
        self.guitar = None
        self.holdJoint = None
        self.explosionRefNode = None
        self.explosion = None
        self.sounds = []
        self.suitAnimationMap = {}
        self.suitAnimationControls = []
        self.suitHeadAnimationControls = []
        self.propsCleaned = False

    def _findController(self):
        try:
            from toontown.suit.DistributedPacesetterBoss import DistributedPacesetterBoss
            for obj in base.cr.doId2do.values():
                if isinstance(obj, DistributedPacesetterBoss):
                    return obj
        except:
            pass
        return None

    def _prepareAnimations(self):
        suit = self.suit
        validateExistingSuitAnimations(
            suit,
            PACESETTER_BODY_ANIMS,
            'Pacesetter Overclocked body controls',
            logPrefix='[Pacesetter Overclocked CTSC]')
        self.suitAnimationMap = suit.generateAnimDict().copy()
        self.suitAnimationControls = [cacheResolvedControls(
            suit,
            PACESETTER_BODY_ANIMS,
            'Pacesetter Overclocked body',
            logPrefix='[Pacesetter Overclocked CTSC]')]

        self.head = getAnimatedHead(
            suit,
            'Pacesetter Overclocked',
            logPrefix='[Pacesetter Overclocked CTSC]')
        suit.specialHead = self.head
        validateExistingSuitAnimations(
            self.head,
            PACESETTER_HEAD_ANIMS,
            'Pacesetter Overclocked head controls',
            logPrefix='[Pacesetter Overclocked CTSC]')
        self.suitHeadAnimationControls = [cacheResolvedControls(
            self.head,
            PACESETTER_HEAD_ANIMS,
            'Pacesetter Overclocked head',
            logPrefix='[Pacesetter Overclocked CTSC]')]

        for toon in self.toons:
            if not toon:
                continue
            validateExistingMultipartAnimations(
                toon,
                TOON_ANIMS,
                'Pacesetter Overclocked Toon %s' % toon.doId,
                logPrefix='[Pacesetter Overclocked CTSC]')

    def _prepareProps(self):
        suit = self.suit
        guitar = loader.loadModel(GUITAR_MODEL_PATH)
        if guitar is None or guitar.isEmpty():
            raise RuntimeError(
                '[Pacesetter Overclocked CTSC] Missing Clash guitar model: %s' %
                GUITAR_MODEL_PATH)

        holdJoint = suit.find('**/joint_Lhold')
        if holdJoint is None or holdJoint.isEmpty():
            try:
                holdJoint = suit.getLeftHand()
            except:
                holdJoint = None
        if holdJoint is None or holdJoint.isEmpty():
            guitar.removeNode()
            raise RuntimeError(
                '[Pacesetter Overclocked CTSC] Pacesetter has no left hold joint')

        guitar.reparentTo(holdJoint)
        guitar.setPosHpr(0, 0, 0, 0, 20, 90)
        guitar.hide()

        explosionRefNode = suit.attachNewNode('explosionRefNode')
        explosion = loader.loadModel(EXPLOSION_MODEL_PATH)
        if explosion is None or explosion.isEmpty():
            guitar.removeNode()
            explosionRefNode.removeNode()
            raise RuntimeError(
                '[Pacesetter Overclocked CTSC] Missing explosion model: %s' %
                EXPLOSION_MODEL_PATH)
        explosion.setBillboardPointEye()
        explosion.setDepthWrite(False)
        explosion.hide()
        explosion.reparentTo(explosionRefNode)

        self.guitar = guitar
        self.holdJoint = holdJoint
        self.explosionRefNode = explosionRefNode
        self.explosion = explosion

        self.sounds = [
            loader.loadSfx(OVERCLOCKED_SFX_PATH),
            loader.loadSfx(EXPLOSION_SFX_PATH),
        ]

    def _cleanupProps(self):
        if self.propsCleaned:
            return
        self.propsCleaned = True
        if self.guitar is not None:
            try:
                self.guitar.removeNode()
            except:
                pass
            self.guitar = None
        if self.explosionRefNode is not None:
            try:
                self.explosionRefNode.removeNode()
            except:
                pass
            self.explosionRefNode = None
        self.explosion = None
        try:
            self.suit.nametag3d.show()
        except:
            pass

    def _updateDiscordRPC(self):
        try:
            discord = getattr(base, 'discord', None)
            if discord is not None:
                discord.applyPreset('psetter_overclocked')
        except:
            pass

    def _makeGuitarCutsceneDict(self):
        return {
            'nodes': [
                render,
                hidden,
                camera,
                self.battle,
                self.suit,
                self.guitar,
                self.holdJoint,
                self.explosionRefNode,
                self.explosion,
            ],
            'affectsCamera': True,
            'maxPlayers': len(self.toons),
            'toons': self.toons,
            'suits': [self.suit],
            'actors': [self.suit],
            'messages': [],
            'sounds': self.sounds,
            'music': [],
            'particles': [],
            'visualEffects': [AFTERIMAGE_EFFECT],
            'functions': [self._cleanupProps, self._updateDiscordRPC],
            'arguments': [],
            'bosses': [],
            'elevators': [],
            'suitAnimationMaps': [self.suitAnimationMap],
            'suitAnimationControls': self.suitAnimationControls,
            'suitHeadAnimationControls': self.suitHeadAnimationControls,
        }

    def _makeGuiCutsceneDict(self):
        return {
            'nodes': [render, hidden, camera],
            'affectsCamera': False,
            'maxPlayers': 0,
            'toons': [],
            'suits': [],
            'actors': [],
            'messages': [],
            'sounds': [],
            'music': [],
            'particles': [],
            'visualEffects': [],
            'functions': [],
            'arguments': [1.0, 999.99],
            'bosses': [],
            'elevators': [],
        }

    def _getPhaseOneMusicRate(self):
        controller = self.controller
        if controller is None:
            return 1.0
        music = getattr(controller, 'battleOneMusic', None)
        if music is not None:
            try:
                return float(music.getPlayRate())
            except:
                pass
        return float(getattr(controller, 'setPhase1MusicRate', 1.0))

    def _setPhaseOneMusicRate(self, rate):
        controller = self.controller
        if controller is None:
            return
        music = getattr(controller, 'battleOneMusic', None)
        if music is not None:
            try:
                music.setPlayRate(rate)
            except:
                pass

    def _stopPhaseOneMusic(self):
        controller = self.controller
        if controller is not None:
            try:
                controller.stopPhaseOneMusic()
            except:
                pass

    def _startPhaseTwoMusic(self):
        controller = self.controller
        if controller is not None:
            try:
                controller.startPhaseTwoMusic()
            except:
                pass

    def _applyAltisOverclockedState(self):
        suit = self.suit
        try:
            suit.makeBattleSpeed(self.battleSpeed)
        except:
            pass
        try:
            if not suit.hasSuitStatusEffect('overclocked'):
                suit.setSuitStatusEffect('overclocked')
        except:
            pass

    def build(self):
        print('[Pacesetter Overclocked CTSC] Building original unchanged pacesetter_guitarsolo.ctsc')
        try:
            self._prepareAnimations()
            self._prepareProps()
            guitarTrack = buildCutscene(
                GUITAR_CUTSCENE_PATH,
                self._makeGuitarCutsceneDict())
            guiTrack = buildCutscene(
                GUI_CUTSCENE_PATH,
                self._makeGuiCutsceneDict())
        except:
            self._cleanupProps()
            raise

        pauseA = 0.1
        slowdownDuration = 1.5
        musicDelay = -4.0
        guitarDuration = guitarTrack.getDuration()
        musicWait = max(
            0.0,
            guitarDuration - pauseA - slowdownDuration + musicDelay)
        startRate = self._getPhaseOneMusicRate()

        musicTrack = Sequence(
            Wait(pauseA),
            LerpFunctionInterval(
                self._setPhaseOneMusicRate,
                duration=slowdownDuration,
                fromData=startRate,
                toData=0.001,
                blendType='easeInOut'),
            Func(self._stopPhaseOneMusic),
            Func(self._setPhaseOneMusicRate, 1.0),
            Wait(musicWait),
            Func(self._startPhaseTwoMusic),
            guiTrack,
        )

        return Sequence(
            Parallel(guitarTrack, musicTrack),
            Func(self._applyAltisOverclockedState),
            Func(self._cleanupProps),
        )


def makePacesetterOverclocked(attack, battleSpeed=6):
    return PacesetterOverclockedSetup(attack, battleSpeed=battleSpeed).build()
