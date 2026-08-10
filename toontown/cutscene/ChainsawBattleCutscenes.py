"""Corporate Clash Chainsaw Consultant battle CTSC adapter for Altis/Python 2."""

from direct.interval.IntervalGlobal import Func, LerpHprInterval, LerpPosHprInterval, Parallel, Sequence, Wait
from panda3d.core import NodePath

from toontown.cutscene.AltisCutsceneCompat import (
    cacheResolvedControls,
    validateExistingMultipartAnimations,
    validateExistingSuitAnimations,
)
from toontown.cutscene.ChainsawCutsceneParticles import getChainsawParticles
from toontown.cutscene.ChainsawIntroCutscene import installChainsawBattleHead
from toontown.cutscene.repository.CutsceneRuntime import buildCutscene


ROOT = 'phase_12/data/cutscenes/chainsawconsultant/chainsawconsultant_'
CUTSCENES = {
    'deadwood': ROOT + 'deadwood.ctsc',
    'throttle': ROOT + 'throttle.ctsc',
    'throttletwo': ROOT + 'throttletwo.ctsc',
    'scabbard': ROOT + 'scabbard.ctsc',
    'revvedup': ROOT + 'revvedup.ctsc',
    'sparkplug': ROOT + 'sparkplug.ctsc',
    'offboarding': ROOT + 'offboarding.ctsc',
    'layoffs': ROOT + 'layoffs.ctsc',
    'chainlinked': ROOT + 'chainlinked.ctsc',
    'phasetwo': ROOT + 'phasetwo.ctsc',
    'phasethree': ROOT + 'phasethree.ctsc',
}

PHASE_DIALOGUE = (
    "DAMAGE TO- \1CHOVER\1help-\2 TO- \1CHOVER\1help-\2 TO OVER- \1CHOVER\1me-\2 OVERRIDE DE- \1CHOVER\1toons-\2 DETECTED.",
    "ENTERING- \1CHOVER\1i'm-\2 ENTER- \1CHOVER\1trying to-\2 RECOVERY MO- \1CHOVER\1resist it-\2 MODE.",
    "ACTIVATING- \1CHOVER\1i don't-\2 TEMP- \1CHOVER\1know-\2 TEMPORARY- \1CHOVER\1if i-\2 REFOREST- \1CHOVER\1can-\2 REFORESTATION MODE.",
    "RECOV- \1CHOVER\1i-\2 RECOVERY AT- \1CHOVER\1can't-\2 RECOV- \1CHOVER\1stop it-\2",
    "\1CHOVER\1please-\2 RECOV- \1CHOVER\1save-\2 RECOV-",
    "\1CHOVER\1save yourselves!\2",
    "RECOVERY COMPLETE.",
    "ENTERING FINAL TERMINATION MODE.",
    "ALL RAM CLEARED. OFFENSIVE DIVISION AT MAXIMUM PERFORMANCE.",
)

TAUNTS = {
    'deadwood': 'IMMEDIATE DISMISSAL OF UNAUTHORIZED PARTIES APPROVED.',
    'throttle': 'IMMEDIATE- \1CHOVER\1not-\2 DISMISSAL OF- \1CHOVER\1this-\2 UNAUTHORIZED PARTIES- \1CHOVER\1time-\2 APPROVED.',
    'throttletwo': 'IMMEDIATE DISMISSAL OF UNAUTHORIZED PARTIES APPROVED.',
    'scabbard': "OVERFLOW- \1CHOVER\1nothing-\2 OF ASSETS NOT \1CHOVER\1-done\2 NOTICED.",
    'revvedup': 'THREATS HAVE BEGUN TO ADVANCE. BEGIN INCREASING ATTACK POWER.',
    'sparkplug': "OTHER- \1CHOVER\1can't-\2 ACTIONS- \1CHOVER\1do-\2 UNA- \1CHOVER\1anything-\2 UNAVAILABLE.",
    'offboarding': 'IRREPARABLE DAMAGE TO EMPLOYEE SUSTAINED. REDIRECTING USEFULNESS.',
    'layoffs': 'UNDERPERFORMING DIVISIONS WILL BE ELIMINATED AT-WILL.',
    'chainlinked': 'DIVISION- \1CHOVER\1hit-\2 IS TO- \1CHOVER\1from-\2 TOO THIN, EXTEND- \1CHOVER\1the-\2 EXTENDING BASE RE-HIRE NO- \1CHOVER\1end-\2 NOTICES.',
}

BOSS_ANIMS = {
    'deadwood': ('deadwood', 'neutral'),
    'throttle': ('throttle', 'neutral'),
    'throttletwo': ('throttletwo', 'neutral'),
    'scabbard': ('scabbard', 'neutral'),
    'revvedup': ('revvedup', 'neutral'),
    'sparkplug': ('sparkplug', 'neutral'),
    'offboarding': ('neutral',),
    'layoffs': ('layoffs', 'neutral'),
    'chainlinked': ('summon', 'neutral'),
    'phasetwo': ('finger-wag', 'neutral'),
    'phasethree': ('soak', 'neutral'),
}

HEAD_ANIMS = {
    'throttle': ('throttle',),
    'throttletwo': ('throttle2',),
    'scabbard': ('scabbard',),
    'revvedup': ('revvedup',),
    'sparkplug': ('sparkplug',),
}

SUPPORT_ANIMS = ('rake-react', 'flail', 'pie-small-react', 'neutral')
TOON_ANIMS = ('neutral', 'slip-backward', 'conked', 'slip-forward')


def _notEmpty(node):
    if node is None:
        return False
    try:
        return not node.isEmpty()
    except:
        return True


class ChainsawBattleCutsceneSetup(object):

    def __init__(self, attack, key, supportSuit=None, supportSuits=None):
        self.attack = attack
        self.key = key
        self.battle = attack['battle']
        self.chainsaw = attack['suit']
        self.supportSuit = supportSuit
        self.supportSuits = list(supportSuits or [])
        self.controller = getattr(self.battle, 'bossCog', None)
        self.cleanupNodes = []
        self.compatRestores = []
        self.particles = []

        phase = getattr(self.controller, 'chainsawPhase', 1)
        self.head = installChainsawBattleHead(self.chainsaw, phase)
        if self.head is None:
            raise RuntimeError('[Chainsaw Battle CTSC] Could not install Chainsaw animated head')

    def _targets(self):
        result = []
        for target in self.attack.get('target', ()):
            toon = target.get('toon')
            if toon and toon not in result:
                result.append(toon)
        return result

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
        if not result:
            result = self._targets()
        return result

    def _allSupports(self):
        result = []
        for suit in getattr(self.battle, 'suits', ()):
            if suit is self.chainsaw:
                continue
            if suit and suit not in result:
                result.append(suit)
        for suit in getattr(self.battle, 'activeSuits', ()):
            if suit is self.chainsaw:
                continue
            if suit and suit not in result:
                result.append(suit)
        if self.supportSuit and self.supportSuit not in result:
            result.append(self.supportSuit)
        for suit in self.supportSuits:
            if suit and suit not in result:
                result.append(suit)
        return result

    def _pad(self, items, count):
        values = list(items[:count])
        while len(values) < count:
            values.append(None)
        return values

    def _loadSounds(self, paths):
        return [loader.loadSfx(path) for path in paths]

    def _prepareCannonCompat(self, suit):
        if suit is None:
            return
        oldMake = getattr(suit, 'makeUnemployed', None)
        oldCreate = getattr(suit, 'createNameInfo', None)

        if oldMake is None:
            suit.makeUnemployed = lambda: None

        if oldCreate:
            def createNameInfo(*args, **kwargs):
                try:
                    return oldCreate()
                except:
                    return 'Cog'
            suit.createNameInfo = createNameInfo

        self.compatRestores.append((suit, oldMake, oldCreate))

    def _restoreCompat(self):
        for suit, oldMake, oldCreate in self.compatRestores:
            try:
                if oldMake is None:
                    del suit.makeUnemployed
                else:
                    suit.makeUnemployed = oldMake
            except:
                pass
            try:
                if oldCreate:
                    suit.createNameInfo = oldCreate
            except:
                pass
        self.compatRestores = []

    def _cleanup(self):
        self._restoreCompat()
        for node in self.cleanupNodes:
            try:
                if _notEmpty(node):
                    node.removeNode()
            except:
                pass
        self.cleanupNodes = []
        for particle in self.particles:
            try:
                particle.softStop()
            except:
                pass
            try:
                particle.cleanup()
            except:
                pass
        self.particles = []
        try:
            camera.wrtReparentTo(self.battle)
        except:
            pass

    def _syncMeter(self):
        controller = self.controller
        if controller is None:
            return
        meter = getattr(controller, 'chainsawMeter', None)
        if meter:
            try:
                meter.setPhase(controller.chainsawPhase)
                meter.setRPM(controller.chainsawRPM)
            except:
                pass

    def _phaseVisual(self, phase):
        controller = self.controller
        if phase == 2:
            self.head.enterSemiGlitch()
        elif phase == 3:
            self.head.enterGlitch()
        if controller:
            meter = getattr(controller, 'chainsawMeter', None)
            if meter:
                try:
                    meter.setPhase(phase)
                    if phase == 2:
                        meter.setRPM(10)
                except:
                    pass
            # Phase 2 owns a timed crossfade from the CTSC wrapper so the
            # music begins changing on the Reforestation Mode dialogue rather
            # than as soon as the phase network field arrives. Phase 3 keeps
            # the existing handoff at its authored visual-change moment.
            if phase == 3:
                try:
                    controller.playChainsawBattleMusic()
                except:
                    pass

    def _animationData(self, suits):
        maps = []
        controls = []
        headControls = []
        for index, suit in enumerate(suits):
            if suit is None:
                maps.append({})
                controls.append({})
                headControls.append({})
                continue
            if suit is self.chainsaw:
                names = BOSS_ANIMS.get(self.key, ('neutral',))
                validateExistingSuitAnimations(
                    suit, names, 'Chainsaw %s body' % self.key,
                    logPrefix='[Chainsaw Battle CTSC]')
                maps.append(suit.generateAnimDict().copy())
                controls.append(cacheResolvedControls(
                    suit, names, 'Chainsaw %s body' % self.key,
                    logPrefix='[Chainsaw Battle CTSC]'))
                headNames = HEAD_ANIMS.get(self.key, ())
                if headNames:
                    validateExistingSuitAnimations(
                        self.head, headNames, 'Chainsaw %s head' % self.key,
                        logPrefix='[Chainsaw Battle CTSC]')
                    headControls.append(cacheResolvedControls(
                        self.head, headNames, 'Chainsaw %s head' % self.key,
                        logPrefix='[Chainsaw Battle CTSC]'))
                else:
                    headControls.append({})
            else:
                needed = SUPPORT_ANIMS if self.key in ('chainlinked', 'offboarding', 'layoffs') else ('neutral',)
                validateExistingSuitAnimations(
                    suit, needed, 'Chainsaw support %s' % index,
                    logPrefix='[Chainsaw Battle CTSC]')
                maps.append(suit.generateAnimDict().copy())
                controls.append(cacheResolvedControls(
                    suit, needed, 'Chainsaw support %s' % index,
                    logPrefix='[Chainsaw Battle CTSC]'))
                headControls.append({})
        return maps, controls, headControls

    def _validateToons(self, toons):
        if self.key not in ('deadwood', 'throttle', 'throttletwo', 'sparkplug', 'offboarding', 'layoffs'):
            return
        for toon in toons:
            if toon:
                validateExistingMultipartAnimations(
                    toon, TOON_ANIMS,
                    'Chainsaw battle Toon %s' % getattr(toon, 'doId', '?'),
                    logPrefix='[Chainsaw Battle CTSC]')

    def _baseDict(self, nodes, toons, suits, messages, sounds=None,
                  particles=None, functions=None, arguments=None):
        self._validateToons(toons)
        maps, controls, headControls = self._animationData(suits)
        return {
            'nodes': nodes,
            'affectsCamera': self.key not in ('deadwood', 'phasetwo'),
            'maxPlayers': len(toons),
            'toons': toons,
            'suits': suits,
            'actors': [self.chainsaw],
            'messages': messages,
            'sounds': sounds or [],
            'music': [],
            'particles': particles or [],
            'visualEffects': [],
            'functions': functions or [],
            'arguments': arguments or [],
            'bosses': [],
            'elevators': [],
            'suitAnimationMaps': maps,
            'suitAnimationControls': controls,
            'suitHeadAnimationControls': headControls,
        }

    def _deadwoodCameraTrack(self):
        return Sequence(
            Func(camera.reparentTo, self.chainsaw),
            Func(camera.setPosHpr,
                 0.0, 12.16477, 7.08061,
                 180.0, 0.0, 0.0),
            Wait(1.0),
            LerpHprInterval(
                camera, 0.15, (180.0, 0.0, 3.0),
                startHpr=(180.0, 0.0, 0.0), blendType='easeInOut'),
            LerpHprInterval(
                camera, 0.1, (180.0, 0.0, -3.0),
                startHpr=(180.0, 0.0, 3.0), blendType='easeInOut'),
            LerpHprInterval(
                camera, 0.1, (180.0, 0.0, 3.0),
                startHpr=(180.0, 0.0, -3.0), blendType='easeInOut'),
            LerpHprInterval(
                camera, 0.1, (180.0, 0.0, -3.0),
                startHpr=(180.0, 0.0, 3.0), blendType='easeInOut'),
            LerpHprInterval(
                camera, 0.1, (180.0, 0.0, 3.0),
                startHpr=(180.0, 0.0, -3.0), blendType='easeInOut'),
            LerpHprInterval(
                camera, 0.1, (180.0, 0.0, -3.0),
                startHpr=(180.0, 0.0, 3.0), blendType='easeInOut'),
            LerpHprInterval(
                camera, 0.2, (180.0, 0.0, 2.00001),
                startHpr=(180.0, 0.0, -3.0), blendType='easeInOut'),
            LerpHprInterval(
                camera, 0.35, (180.0, 0.0, -2.00001),
                startHpr=(180.0, 0.0, 2.00001), blendType='easeInOut'),
            LerpHprInterval(
                camera, 0.4, (180.0, 0.0, 0.0),
                startHpr=(180.0, 0.0, -2.00001), blendType='easeInOut'),
            Wait(1.4),
            Func(camera.reparentTo, render),
            Func(camera.setPosHpr,
                 -16.18102, 7.4942, 9.07771,
                 -43.85632, -8.16993, 0.0),
            Wait(0.7),
            LerpPosHprInterval(
                camera, 1.5,
                (0.0, 6.0, 5.0), (0.0, 0.0, 0.0),
                startPos=(-16.18102, 7.4942, 9.07771),
                startHpr=(-43.85632, -8.16993, 0.0),
                blendType='easeInOut'))

    def _deadwood(self):
        toons = self._pad(self._allToons(), 4)
        supports = self._allSupports()[:4]
        suits = [self.chainsaw] + supports
        while len(suits) < 5:
            suits.append(None)
        doors = list(getattr(self.controller, 'doorList', ()) or ())
        while len(doors) < 6:
            doors.append(None)
        point = render.attachNewNode('chainsawDeadwoodPointCannonAt')
        self.cleanupNodes.append(point)
        nodes = [render, hidden, camera, self.battle, self.chainsaw] + doors[:6] + [point]
        return self._baseDict(
            nodes, toons, suits, [TAUNTS['deadwood']],
            self._loadSounds(['phase_12/audio/sfx/SA_deadwood.ogg']),
            functions=[self._cleanup])

    def _throttle(self):
        toons = self._pad(self._allToons(), 4)
        supports = self._allSupports()[:4]
        suits = [self.chainsaw] + supports
        point = render.attachNewNode('chainsawThrottlePointCannonAt')
        self.cleanupNodes.append(point)
        fallPoints = []
        for index, toon in enumerate(toons):
            if toon:
                node = toon.attachNewNode('chainsawThrottleFallPoint-%s' % index)
                node.wrtReparentTo(render)
                node.setHpr(0, 0, 0)
            else:
                node = None
            fallPoints.append(node)
            if node:
                self.cleanupNodes.append(node)

        functions = [self._cleanup]
        if self.key == 'throttle':
            functions += [self.head.bulbLeft.hide, self.head.bulbLeft.show, self.head.beginSemiGlitchFreakout]
            self.particles = getChainsawParticles(('chainsawBulbBreak', 'chainsawGlassDrip'))
        nodes = [render, hidden, camera, self.battle, self.chainsaw, point] + fallPoints + toons
        return self._baseDict(
            nodes, toons, suits, [TAUNTS[self.key]],
            self._loadSounds([
                'phase_4/audio/sfx/MG_cannon_hit_tower.ogg',
                'phase_12/audio/sfx/SA_throttle_break.ogg',
                'phase_12/audio/sfx/SA_throttle_hit.ogg',
            ]), self.particles, functions=functions)

    def _scabbard(self):
        toons = self._pad(self._allToons(), 4)
        supports = self._allSupports()[:4]
        suits = [self.chainsaw] + supports
        self.particles = getChainsawParticles(('chainsawScabbardUp',))
        nodes = [render, hidden, camera, self.battle, self.chainsaw]
        return self._baseDict(
            nodes, toons, suits, [TAUNTS['scabbard']],
            self._loadSounds(['phase_12/audio/sfx/SA_scabbard.ogg']),
            self.particles, functions=[self.head.loopNeutral])

    def _revvedup(self):
        toons = self._pad(self._allToons(), 4)
        supports = self._allSupports()[:4]
        suits = [self.chainsaw] + supports
        headAnim = self.head.actorInterval('revvedup')

        def playHeadAnim():
            if getattr(self.head, 'glitchState', '') == 'semi':
                headAnim.start()

        # Every original Chainsaw battle CTSC uses node index 4 as the
        # actual Chainsaw actor. Do not substitute a rotated camera anchor:
        # the t=0 Parallel reparent/move callbacks then become order-dependent.
        nodes = [render, hidden, camera, self.battle, self.chainsaw]
        return self._baseDict(
            nodes, toons, suits, [TAUNTS['revvedup']],
            self._loadSounds(['phase_12/audio/sfx/SA_revving_up.ogg']),
            functions=[playHeadAnim, headAnim.finish, self.head.loopNeutral])

    def _sparkplug(self):
        targets = self._targets()
        toon = targets[0] if targets else None
        toons = [toon]
        supports = self._allSupports()[:4]
        suits = [self.chainsaw] + supports
        leftHand = getattr(self.chainsaw, 'leftHand', None)
        self.particles = getChainsawParticles(('chainsawSparkPlugFinger', 'chainsawSparkPlugAcross'))
        nodes = [render, hidden, camera, self.battle, self.chainsaw, toon, leftHand]
        return self._baseDict(
            nodes, toons, suits, [TAUNTS['sparkplug']],
            self._loadSounds([
                'phase_5/audio/sfx/AA_zap_tv.ogg',
                'phase_12/audio/sfx/SA_sparkplug.ogg',
            ]), self.particles, functions=[self.head.loopNeutral])

    def _offboarding(self):
        targets = self._targets()
        toon = targets[0] if targets else None
        support = self.supportSuit
        if support is None:
            supports = self._allSupports()
            support = supports[0] if supports else None
        self._prepareCannonCompat(support)
        toonNode = toon.attachNewNode('chainsawOffboardingToonPos') if toon else NodePath('chainsawOffboardingToonPos')
        if toon:
            toonNode.wrtReparentTo(render)
        else:
            toonNode.reparentTo(render)
        self.cleanupNodes.append(toonNode)
        def cleanupOffboarding():
            # The original Clash setup explicitly restores the Toon from the
            # temporary toonPosNode before that node is destroyed.  Without
            # this, Altis leaves the Toon parented beneath a removed NodePath,
            # making it disappear from later normal battle movies.
            if toon:
                try:
                    toon.wrtReparentTo(render)
                except:
                    pass
            self._cleanup()

        suits = [self.chainsaw, support]
        nodes = [render, hidden, camera, self.battle, self.chainsaw, toon, toonNode]
        return self._baseDict(
            nodes, [toon], suits, [TAUNTS['offboarding']],
            self._loadSounds([
                'phase_11/audio/sfx/SA_bash.ogg',
                'phase_3.5/audio/sfx/ENC_cogfall_apart.ogg',
                'phase_4/audio/sfx/avatar_emotion_surprise.ogg',
            ]), functions=[cleanupOffboarding])

    def _layoffs(self):
        targets = self._pad(self._targets(), 4)
        supports = self._pad(self.supportSuits or self._allSupports(), 4)
        for support in supports:
            self._prepareCannonCompat(support)
        toonNodes = []
        for index, toon in enumerate(targets):
            if toon:
                node = toon.attachNewNode('chainsawLayoffsToonPos-%s' % index)
                node.wrtReparentTo(render)
            else:
                node = None
            toonNodes.append(node)
            if node:
                self.cleanupNodes.append(node)
        def cleanupLayoffs():
            # Layoffs uses the same temporary Toon-anchor pattern as
            # Offboarding.  Restore every affected Toon before removing the
            # anchors so later battle movies still have visible Toon actors.
            for toon in targets:
                if toon:
                    try:
                        toon.wrtReparentTo(render)
                    except:
                        pass
            self._cleanup()

        suits = [self.chainsaw] + supports
        nodes = [render, hidden, camera, self.battle, self.chainsaw] + targets + toonNodes
        return self._baseDict(
            nodes, targets, suits, [TAUNTS['layoffs']],
            self._loadSounds([
                'phase_3.5/audio/sfx/ENC_cogfall_apart.ogg',
                'phase_4/audio/sfx/avatar_emotion_surprise.ogg',
            ]), functions=[cleanupLayoffs])

    def _chainlinked(self):
        toons = self._allToons()
        firstToon = toons[0] if toons else None
        supports = self._allSupports()[:4]
        suits = [self.chainsaw] + supports

        def showText(*values):
            for suit in values:
                if suit:
                    try:
                        suit.showHpString('CHAIN LINKED!', color=(1, 1, 1, 1))
                    except:
                        try:
                            suit.showHpTextNew(0, text='CHAIN LINKED!', colorCode=1)
                        except:
                            pass

        nodes = [render, hidden, camera, self.battle, self.chainsaw, firstToon]
        return self._baseDict(
            nodes, [firstToon], suits, [TAUNTS['chainlinked']],
            functions=[showText], arguments=[supports])

    def _phase(self):
        suits = [self.chainsaw]
        nodes = [render, hidden, camera, self.battle, self.chainsaw, self.head]
        return self._baseDict(nodes, [], suits, list(PHASE_DIALOGUE))

    def _makeDict(self):
        if self.key == 'deadwood':
            return self._deadwood()
        if self.key in ('throttle', 'throttletwo'):
            return self._throttle()
        if self.key == 'scabbard':
            return self._scabbard()
        if self.key == 'revvedup':
            return self._revvedup()
        if self.key == 'sparkplug':
            return self._sparkplug()
        if self.key == 'offboarding':
            return self._offboarding()
        if self.key == 'layoffs':
            return self._layoffs()
        if self.key == 'chainlinked':
            return self._chainlinked()
        if self.key in ('phasetwo', 'phasethree'):
            return self._phase()
        raise KeyError('Unknown Chainsaw battle CTSC key: %s' % self.key)

    def build(self):
        path = CUTSCENES[self.key]
        print('[Chainsaw Battle CTSC] Building original unchanged %s' % path)
        try:
            track = buildCutscene(path, self._makeDict())
        except:
            self._cleanup()
            raise

        extras = Parallel()
        if self.key == 'chainlinked':
            extras.append(Sequence(Wait(0.499), Func(camera.wrtReparentTo, self.battle)))
        elif self.key == 'layoffs':
            extras.append(Sequence(Wait(0.479), Func(camera.wrtReparentTo, render)))
        elif self.key == 'offboarding':
            extras.append(Sequence(Wait(1.439), Func(camera.wrtReparentTo, self.battle)))
        elif self.key == 'scabbard':
            extras.append(Sequence(Wait(0.999), Func(camera.wrtReparentTo, self.battle)))
        elif self.key == 'sparkplug':
            extras.append(Sequence(Wait(2.436), Func(camera.wrtReparentTo, self.battle)))
        if self.key == 'revvedup':
            extras.append(Sequence(Wait(1.0), Func(self._syncMeter)))
        elif self.key == 'phasetwo':
            extras.append(Sequence(Wait(4.753), Func(self._phaseVisual, 2)))
            if self.controller:
                try:
                    extras.append(Sequence(
                        Wait(8.0),
                        self.controller.makeChainsawPhaseTwoMusicHandoff()))
                except Exception as error:
                    print('[Chainsaw Battle CTSC] Could not build phase-two music handoff: %s' % error)
        elif self.key == 'phasethree':
            extras.append(Sequence(Wait(7.5), Func(self.head.endSemiGlitchFreakout)))
            extras.append(Sequence(Wait(7.6), Func(self._phaseVisual, 3)))

        preTrack = Sequence()
        if self.key in ('revvedup', 'throttle', 'throttletwo',
                        'chainlinked', 'layoffs', 'offboarding', 'scabbard',
                        'sparkplug'):
            preTrack.append(Func(camera.wrtReparentTo, self.chainsaw))

        if self.key == 'deadwood':
            cameraTrack = self._deadwoodCameraTrack()
        else:
            cameraTrack = Sequence()

        finish = Sequence()
        if self.key == 'revvedup':
            finish.append(Func(self._syncMeter))

        return Sequence(
            preTrack,
            Parallel(track, extras, cameraTrack),
            finish,
            Func(self._cleanup))


def makeChainsawBattleCutscene(attack, key, supportSuit=None, supportSuits=None):
    return ChainsawBattleCutsceneSetup(
        attack, key, supportSuit=supportSuit,
        supportSuits=supportSuits).build()
