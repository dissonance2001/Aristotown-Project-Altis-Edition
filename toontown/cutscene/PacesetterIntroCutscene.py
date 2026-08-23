"""Corporate Clash Pacesetter introduction adapter for Project Altis/Python 2.

The choreography stays in the original, unchanged ``pacesetter_intro.ctsc``.
The actor used by the CTSC is the exact normal distributed ``psetter`` Suit
that immediately continues into Battle One.  No temporary Suit and no BossCog
character are involved.
"""

from direct.interval.IntervalGlobal import Func, Parallel, Sequence, Wait

from toontown.cutscene.AltisCutsceneCompat import (
    cacheResolvedControls,
    configureSuitNametag,
    getAnimatedHead,
    loadAndValidateAdditionalAnimations,
    validateExistingMultipartAnimations,
    validateExistingSuitAnimations,
)
from toontown.cutscene.repository.CutsceneRuntime import buildCutscene
from toontown.distributed import DelayDelete


CUTSCENE_PATH = 'phase_9/data/cutscenes/pacesetter/pacesetter_intro.ctsc'
INTRO_MUSIC_PATH = 'phase_9/audio/bgm/merc/instance_pacesetter_ctscn.ogg'

PACESETTER_INTRO_DIALOGUE = (
    "I have been in here for so LONG and nothing has happened!",
    "This job is a huge waste of my time, I could've been doing something more productive such as...",
    "Being productive!",
    "Hold on a sec...",
    "FINALLY! Entertainment at last! I was feeling myself rust!",
    "And Toon visitors for that matter! Great, we can get down to business!",
    "With you here, we can make some agreements. You can even become a member of the Pace Place!",
    "However, there is a catch.",
    "In the Pace Place, we don't allow anyone to waltz on in.",
    "In order to REALLY be invited, you must pass my test and let me tell you, it is no easy feat.",
    "It is a one percent chance of passing and multiplying that by you, that's a whopping ZERO percent chance!",
    "All that brain mastery you've learned, that is useless here! You are on my racetrack now.",
    "Let's see how long you can keep up against me! Your test starts... NOW!",
)

PACESETTER_BODY_ANIMS = (
    'walk',
    'true-neutral',
    'neutral',
    'effort',
    'quick-jump',
    'come-on',
)

PACESETTER_HEAD_ANIMS = (
    'neutral-hurt',
    'come-on',
    'neutral',
)

TOON_ANIMS = (
    'walk',
    'slip-backward',
    'neutral',
)

# AltisCutsceneCompat maps this token to Suit.makeAfterImages() /
# Suit.removeAfterImages().
AFTERIMAGE_EFFECT = 'AFTERIMAGE'


class PacesetterIntroSetup(object):

    def __init__(self, boss, delayDeletes):
        self.boss = boss
        self.delayDeletes = delayDeletes
        self.toons = []
        self.actualToons = []
        self.pacesetter = None
        self.head = None
        self.suitAnimationMap = {}
        self.suitAnimationControls = []
        self.suitHeadAnimationControls = []
        self.cleanedUp = False
        self.introMusic = None
        self.pacesetterOriginalParent = None
        self.pacesetterOriginalPos = None
        self.pacesetterOriginalHpr = None
        self.pacesetterOriginalScale = None

    def _preparePacesetterActor(self):
        """Prepare the real distributed Battle-One Pacesetter for the CTSC."""
        pace = self.boss.getPacesetterSuit()
        if pace is None:
            raise RuntimeError('Pacesetter CTSC started before the real psetter Suit was generated')

        try:
            self.pacesetterOriginalParent = pace.getParent()
            self.pacesetterOriginalPos = pace.getPos(self.pacesetterOriginalParent)
            self.pacesetterOriginalHpr = pace.getHpr(self.pacesetterOriginalParent)
            self.pacesetterOriginalScale = pace.getScale(self.pacesetterOriginalParent)
        except:
            self.pacesetterOriginalParent = render
            self.pacesetterOriginalPos = pace.getPos(render)
            self.pacesetterOriginalHpr = pace.getHpr(render)
            self.pacesetterOriginalScale = pace.getScale(render)

        # Clash exposes a separate true-neutral alias.  Altis's Pacesetter
        # predates that alias but its phase-4 B-body neutral is compatible.
        trueNeutralPath = 'phase_4/models/char/suitB-neutral'
        loadAndValidateAdditionalAnimations(
            pace,
            {'true-neutral': trueNeutralPath},
            'Pacesetter true-neutral body alias',
            logPrefix='[Pacesetter CTSC]')

        validateExistingSuitAnimations(
            pace,
            ('walk', 'neutral', 'effort', 'quick-jump', 'come-on'),
            'Pacesetter body controls',
            logPrefix='[Pacesetter CTSC]')

        self.suitAnimationMap = pace.generateAnimDict().copy()
        self.suitAnimationMap['true-neutral'] = trueNeutralPath
        self.suitAnimationControls = [cacheResolvedControls(
            pace,
            PACESETTER_BODY_ANIMS,
            'Pacesetter body',
            logPrefix='[Pacesetter CTSC]')]

        self.head = getAnimatedHead(
            pace, 'Pacesetter', logPrefix='[Pacesetter CTSC]')
        pace.specialHead = self.head
        validateExistingSuitAnimations(
            self.head,
            PACESETTER_HEAD_ANIMS,
            'Pacesetter head controls',
            logPrefix='[Pacesetter CTSC]')
        self.suitHeadAnimationControls = [cacheResolvedControls(
            self.head,
            PACESETTER_HEAD_ANIMS,
            'Pacesetter head',
            logPrefix='[Pacesetter CTSC]')]

        configureSuitNametag(pace, visible=True)
        try:
            pace.setActiveShadow(0)
            pace.hideShadow()
        except:
            pass

        pace.wrtReparentTo(render)
        # Preserve the v8.4 reveal timing: he must not be visible through the
        # open elevator before the first authored Pacesetter dialogue.
        pace.hide()
        self.pacesetter = pace

    def _prepareToons(self):
        boss = self.boss
        for toonId in boss.involvedToons:
            toon = boss.cr.doId2do.get(toonId)
            if not toon:
                continue
            validateExistingMultipartAnimations(
                toon,
                TOON_ANIMS,
                'Toon %s (%s)' % (toonId, toon.getName()),
                logPrefix='[Pacesetter CTSC]')
            toon.wrtReparentTo(render)
            self.actualToons.append(toon)
            self.delayDeletes.append(
                DelayDelete.DelayDelete(toon, 'PacesetterIntroCutscene'))

        self.toons = list(self.actualToons)
        while len(self.toons) < 4:
            self.toons.append(None)

    def _fixPaceCornerSignTexture(self):
        # The sign's original orientation is already correct.  The missing
        # lettering is a texture binding issue, so force the exact Clash atlas
        # onto the existing sign node without changing its HPR.
        try:
            sign = self.boss.geom.find('**/pace_corner_sign')
            if sign and not sign.isEmpty():
                texture = loader.loadTexture(
                    'phase_8/maps/drowsy_dreamland/pacesetter/'
                    'ttcc_int_ps_palette_2.png')
                if texture:
                    sign.setTexture(texture, 100)
                    print('[Pacesetter CTSC] Forced Pace Corner sign texture')
                else:
                    print('[Pacesetter CTSC] Pace Corner texture failed to load')
        except Exception as error:
            print(('[Pacesetter CTSC] Could not apply Pace Corner texture: %s' % error))

    def _prepareActors(self):
        self._fixPaceCornerSignTexture()
        self._preparePacesetterActor()
        self._prepareToons()

    def _makeCutsceneDict(self):
        pace = self.pacesetter

        # Clash's loader starts with render/hidden/camera, then appends exactly
        # battleNode, Pacesetter, paceNodeIntro.  The numeric node references in
        # pacesetter_intro.ctsc depend on this order.
        nodes = [
            render,
            hidden,
            camera,
            self.boss.battleNode,
            pace,
            self.boss.paceNodeIntro,
        ]

        return {
            'nodes': nodes,
            'affectsCamera': True,
            'maxPlayers': 4,
            'toons': self.toons,
            'suits': [pace],
            'actors': [pace] + self.actualToons,
            'messages': PACESETTER_INTRO_DIALOGUE,
            'sounds': [],
            'music': [],
            'particles': [],
            'visualEffects': [AFTERIMAGE_EFFECT],
            'functions': [],
            'arguments': [],
            'bosses': [],
            'elevators': [],
            'suppressSuitNametags': True,
            'suitAnimationMaps': [self.suitAnimationMap],
            'suitAnimationControls': self.suitAnimationControls,
            'suitHeadAnimationControls': self.suitHeadAnimationControls,
        }

    def _showPacesetterForFirstDialogue(self):
        pace = self.pacesetter
        if not pace:
            return
        pace.show()
        configureSuitNametag(pace, visible=True)

    def _startIntroMusic(self):
        if self.introMusic is None:
            self.introMusic = base.loader.loadMusic(INTRO_MUSIC_PATH)
        if self.introMusic:
            base.playMusic(self.introMusic, looping=0, volume=1.0)

    def _stopIntroMusic(self):
        if self.introMusic:
            try:
                self.introMusic.stop()
            except:
                pass

    def build(self):
        print('[Pacesetter CTSC] Building original unchanged pacesetter_intro.ctsc')
        try:
            self._prepareActors()
            track = buildCutscene(CUTSCENE_PATH, self._makeCutsceneDict())
        except:
            self.cleanup()
            raise

        # The CTSC does not contain a music event; Clash's instance provider
        # owns instance_pacesetter_ctscn.ogg.  Start it at CTSC time zero.
        # The elevator movie leaves the camera parented to the cabin, while
        # the CTSC's first camera event is authored in render space.
        # The original CTSC's first Pacesetter dialogue starts at 20.0s.
        # Run the unchanged choreography alongside a tiny visibility cue so the
        # actor does not appear before that first line.
        introTrack = Parallel(
            track,
            Sequence(
                Wait(19.90),
                Func(self._showPacesetterForFirstDialogue),
            ),
        )
        return Sequence(
            Func(base.camera.wrtReparentTo, render),
            Func(self._startIntroMusic),
            introTrack,
            Func(self._stopIntroMusic),
        )

    def cleanup(self):
        if self.cleanedUp:
            return
        self.cleanedUp = True
        self._stopIntroMusic()

        pace = self.pacesetter
        if pace:
            try:
                pace.removeAfterImages()
            except:
                pass
            try:
                pace.clearChat()
            except:
                pass
            try:
                pace.stop()
                pace.loop('neutral')
            except:
                pass
            try:
                parent = self.pacesetterOriginalParent
                if parent is None or parent.isEmpty():
                    parent = render
                pace.reparentTo(parent)
                if self.pacesetterOriginalPos is not None:
                    pace.setPos(self.pacesetterOriginalPos)
                if self.pacesetterOriginalHpr is not None:
                    pace.setHpr(self.pacesetterOriginalHpr)
                if self.pacesetterOriginalScale is not None:
                    pace.setScale(self.pacesetterOriginalScale)
            except:
                try:
                    pace.wrtReparentTo(render)
                except:
                    pass
            try:
                pace.setActiveShadow(1)
                pace.showShadow()
            except:
                pass
            configureSuitNametag(pace, visible=True)
            try:
                pace.showNametag2d()
            except:
                pass
            # Keep the actor hidden during the short Introduction barrier
            # handoff.  BattleOne shows this exact same Suit after the battle
            # state has taken ownership of its position.
            try:
                pace.hide()
            except:
                pass
            self.pacesetter = None

        try:
            self.boss.paceNodeIntro.setPosHpr(
                -37.3, 41.4, 0, 0, 0, 0)
        except:
            pass
        try:
            base.camera.wrtReparentTo(render)
        except:
            pass

        for toon in self.actualToons:
            try:
                toon.wrtReparentTo(render)
                toon.clearColorScale()
                toon.show()
            except:
                pass

        if getattr(self.boss, '_pacesetterIntroSetup', None) is self:
            self.boss._pacesetterIntroSetup = None


def makePacesetterIntroduction(boss, delayDeletes):
    setup = PacesetterIntroSetup(boss, delayDeletes)
    boss._pacesetterIntroSetup = setup
    return setup.build()
