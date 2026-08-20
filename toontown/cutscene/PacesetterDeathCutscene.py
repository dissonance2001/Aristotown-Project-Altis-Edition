# -*- coding: utf-8 -*-
"""Corporate Clash Pacesetter death CTSC adapter for Project Altis/Python 2."""

from __future__ import absolute_import
from __future__ import print_function
from direct.interval.IntervalGlobal import Func, LerpFunctionInterval, Sequence

from toontown.cutscene.AltisCutsceneCompat import (
    cacheResolvedControls,
    configureSuitNametag,
    getAnimatedHead,
    loadAndValidateAdditionalAnimations,
    validateExistingSuitAnimations,
)
from toontown.cutscene.repository.CutsceneRuntime import buildCutscene


CUTSCENE_PATH = 'phase_9/data/cutscenes/pacesetter/pacesetter_death.ctsc'
AFTERIMAGE_EFFECT = 'AFTERIMAGE'

PACESETTER_DEATH_DIALOGUE = (
    "This is fine.",
    "I mean— this is great, actually.",
    "You've BARELY managed to keep up with me so far.",
    "Just as a reminder, that was only a TEST.",
    "And, by the way, you didn't pass. Pretty embarrassing for you, I know. I feel ya.",
    "It's pretty sad because I was just getting started,",
    "I've still got like three forms that you haven't seen yet.",
    "But, uh, maybe you should take a breather. Meet back up for a second session. For your sake.",
    "In the meantime, I'm gonna go over here and uh...",
    "Do some... stretches...",
)

PACESETTER_BODY_ANIMS = (
    'true-neutral',
    'walk',
    'finger-wag',
    'neutral',
    'headless-death',
    'death-pose',
)
PACESETTER_HEAD_ANIMS = ('neutral-hurt', 'neutral')


class PacesetterDeathSetup(object):

    def __init__(self, suit, battle):
        self.suit = suit
        self.battle = battle
        self.controller = self._findController()
        self.head = None
        self.suitAnimationMap = {}
        self.suitAnimationControls = []
        self.suitHeadAnimationControls = []
        self.cutsceneTrack = None
        self.deathEntrySpeed = 1.0
        self.deathSounds = []

    def _findController(self):
        try:
            from toontown.suit import DistributedPacesetterBoss
            controller = DistributedPacesetterBoss.OnePacesetterController
            if controller is not None:
                return controller
        except:
            pass
        return None

    def _prepareAnimations(self):
        suit = self.suit
        additional = {
            'true-neutral': 'phase_4/models/char/suitB-neutral',
            # Altis Suit.generateAnimDict() incorrectly overwrites the normal
            # phase-5 B-body headless-death mapping with the CEO phase-12
            # mapping.  Pacesetter's CTSC needs the normal battle animation.
            'headless-death': 'phase_5/models/char/suitB-headless-death',
            'death-pose': 'phase_9/models/char/suitB-death-pose',
        }
        loadAndValidateAdditionalAnimations(
            suit,
            additional,
            'Pacesetter death body aliases',
            logPrefix='[Pacesetter Death CTSC]')
        validateExistingSuitAnimations(
            suit,
            ('walk', 'finger-wag', 'neutral'),
            'Pacesetter death body controls',
            logPrefix='[Pacesetter Death CTSC]')

        self.suitAnimationMap = suit.generateAnimDict().copy()
        self.suitAnimationMap.update(additional)
        self.suitAnimationControls = [cacheResolvedControls(
            suit,
            PACESETTER_BODY_ANIMS,
            'Pacesetter death body',
            logPrefix='[Pacesetter Death CTSC]')]

        self.head = getAnimatedHead(
            suit,
            'Pacesetter Death',
            logPrefix='[Pacesetter Death CTSC]')
        suit.specialHead = self.head
        validateExistingSuitAnimations(
            self.head,
            PACESETTER_HEAD_ANIMS,
            'Pacesetter death head controls',
            logPrefix='[Pacesetter Death CTSC]')
        self.suitHeadAnimationControls = [cacheResolvedControls(
            self.head,
            PACESETTER_HEAD_ANIMS,
            'Pacesetter death head',
            logPrefix='[Pacesetter Death CTSC]')]

    def _fixHead(self):
        try:
            self.suit.specialHead.stop()
            self.suit.specialHead.pose('neutral-hurt', 0)
            self.suit.specialHead.ignoreNeutral = True
        except Exception as error:
            print('[Pacesetter Death CTSC] fixHead warning: %s' % error)

    def _getDeathEntrySpeed(self):
        # Movie.play() decides the outer battle movie play-rate before it asks
        # MovieUtil to construct this death track.  Capture that exact rate so
        # the special death sequence can cancel it back to real-time x1.
        try:
            movie = getattr(self.battle, 'movie', None)
            speed = float(getattr(movie, 'currentBattleSpeed', 1.0))
            if speed > 0.0:
                return max(1.0, speed)
        except:
            pass
        try:
            speed = float(self.suit.getBattleSpeed())
            if speed > 0.0:
                return max(1.0, speed)
        except:
            pass
        return 1.0

    def _makeCutsceneDict(self):
        controller = self.controller
        if controller is None or getattr(controller, 'paceNodeDeath', None) is None:
            raise RuntimeError('Pacesetter death node/controller is unavailable')
        self.deathSounds = [
            loader.loadSfx('phase_9/audio/sfx/CHQ_FACT_stomper_large.ogg'),
            loader.loadSfx('phase_9/audio/sfx/CHQ_VP_boom.ogg'),
        ]
        return {
            'nodes': [
                render,
                hidden,
                camera,
                self.battle,
                self.suit,
                controller.paceNodeDeath,
            ],
            'affectsCamera': True,
            'maxPlayers': 0,
            'toons': [],
            'suits': [self.suit],
            'actors': [self.suit],
            'messages': PACESETTER_DEATH_DIALOGUE,
            'sounds': self.deathSounds,
            'music': [],
            'particles': [],
            'visualEffects': [AFTERIMAGE_EFFECT],
            'functions': [self._fixHead],
            'arguments': [],
            'bosses': [],
            'elevators': [],
            'suppressSuitNametags': True,
            'suitAnimationMaps': [self.suitAnimationMap],
            'suitAnimationControls': self.suitAnimationControls,
            'suitHeadAnimationControls': self.suitHeadAnimationControls,
        }

    def _prepareDeathState(self):
        # Match Corporate Clash's special-death behavior: Pacesetter is
        # already server-confirmed defeated, but the client actor is NOT
        # sent through Suit.makeDead() and is NOT given the normal lose /
        # gear-explosion sequence.  Keep the actor alive for the authored
        # pacesetter_death.ctsc animation.
        controller = self.controller
        if controller is not None:
            try:
                controller.beginPacesetterDefeat()
            except:
                pass

        # This method only runs after MovieUtil has confirmed Pacesetter is
        # dying.  Match Clash's resetTimescale/updateTimescale behavior: clear
        # the Suit's future speed modifier AND retime the live outer battle
        # movie immediately.  This is what makes the already-running lethal
        # round, including the death CTSC, continue at real x1.
        # Do NOT touch this state for misses/non-lethal hits.
        print('[Pacesetter Death CTSC] Confirmed lethal hit: x%s -> x1' % self.deathEntrySpeed)
        try:
            self.suit.makeUnBattleSpeed()
        except:
            try:
                self.suit.battleSpeed = 0
            except:
                pass

        try:
            movie = getattr(self.battle, 'movie', None)
            if movie is not None:
                movie.currentBattleSpeed = 1.0
                liveTrack = getattr(movie, 'track', None)
                if liveTrack is not None:
                    liveTrack.setPlayRate(1.0)
                    try:
                        movie.setTrackPlayRate(liveTrack, 1.0)
                    except:
                        pass
                    print('[Pacesetter Death CTSC] Live battle movie retimed to x1')
        except Exception as error:
            print('[Pacesetter Death CTSC] Live movie x1 reset warning: %s' % error)

        configureSuitNametag(self.suit, visible=False)

    def _forceDeathAnimationRates(self):
        # The CTSC loop events use the exact cached AnimControl objects
        # directly.  Panda AnimControls retain the play rate they had during
        # accelerated combat, so resetting only the outer Movie timescale is
        # not enough: a later control.loop() can still run at x6/x8.
        #
        # Reset every body/head control used by pacesetter_death.ctsc before
        # the authored cutscene begins.  This is lethal-death-only and does
        # not affect misses or non-lethal combat rounds.
        resetCount = 0
        for cacheList in (self.suitAnimationControls,
                          self.suitHeadAnimationControls):
            for controls in cacheList:
                for control in controls.values():
                    if control is None:
                        continue
                    try:
                        control.setPlayRate(1.0)
                        resetCount += 1
                    except:
                        pass

        # Also reset Actor-facing animation rates.  This covers any CTSC
        # helper that resolves through the Actor rather than the cached
        # control dictionary.
        for animName in PACESETTER_BODY_ANIMS:
            try:
                self.suit.setPlayRate(1.0, animName)
            except:
                pass
        if self.head is not None:
            for animName in PACESETTER_HEAD_ANIMS:
                try:
                    self.head.setPlayRate(1.0, animName)
                except:
                    pass

        print('[Pacesetter Death CTSC] Reset %s cached animation controls to x1' % resetCount)

    def _resetDeathSoundRates(self):
        # Movie.setTrackPlayRate() recursively accelerates SoundIntervals when
        # the lethal round was built at x6/x8.  Restore only the death CTSC
        # sounds after the parent movie has applied that rate.
        for sound in self.deathSounds:
            try:
                sound.setPlayRate(1.0)
            except:
                pass

    def _makeMusicStopTrack(self):
        controller = self.controller
        if controller is None:
            return Sequence()
        if not controller.isPacesetterBattleMusicPlaying():
            return Sequence(Func(controller.stopPacesetterBattleMusic))

        startRate = controller.getActivePacesetterMusicRate()
        return Sequence(
            LerpFunctionInterval(
                controller.setActivePacesetterMusicRate,
                duration=2.0,
                fromData=startRate,
                toData=0.001,
                blendType='easeInOut'),
            Func(controller.stopPacesetterBattleMusic),
            Func(controller.setActivePacesetterMusicRate, 1.0),
        )

    def _finishDeath(self):
        try:
            self.suit.setChatAbsolute('', 0)
        except:
            pass
        if self.controller is not None:
            try:
                self.controller.stopPacesetterBattleMusic()
            except:
                pass

    def build(self):
        print('[Pacesetter Death CTSC] Building original unchanged pacesetter_death.ctsc')
        self.deathEntrySpeed = self._getDeathEntrySpeed()
        self._prepareAnimations()
        self.cutsceneTrack = buildCutscene(CUTSCENE_PATH, self._makeCutsceneDict())
        deathTrack = Sequence(
            Func(self._prepareDeathState),
            Func(self._forceDeathAnimationRates),
            Func(self._resetDeathSoundRates),
            self._makeMusicStopTrack(),
            # Re-assert x1 immediately before the CTSC in case another
            # battle helper touched a control while the music fade ran.
            Func(self._forceDeathAnimationRates),
            self.cutsceneTrack,
            Func(self._finishDeath),
        )

        # _prepareDeathState retimes the LIVE outer Movie track to x1.  Do not
        # counter-scale this child interval as well, or it would become slow
        # motion after the parent movie has already been reset.
        return deathTrack


def makePacesetterDeath(suit, battle):
    return PacesetterDeathSetup(suit, battle).build()
