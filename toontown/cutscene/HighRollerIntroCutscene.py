"""Exact Project Altis provider for Clash's unchanged High Roller intro CTSC.

This file does not recreate or replace the cutscene timeline.  It supplies the
existing Altis actors, exact Clash animation aliases, nodes, props and helper
objects expected by highroller_intro.ctsc.
"""

import os

from direct.actor.Actor import Actor
from direct.gui.DirectFrame import DirectFrame
from direct.interval.IntervalGlobal import ActorInterval, Func, LerpPosInterval, Parallel, Sequence, SoundInterval, Wait
from panda3d.core import Filename, NodePath, TransparencyAttrib, Vec3, VirtualFileSystem

from toontown.battle.BattleProps import globalPropPool
from toontown.cutscene.repository.CutsceneRuntime import buildCutscene
from toontown.cutscene.ResolvedActorInterval import (
    ResolvedActorInterval, resolveControl)
from toontown.distributed import DelayDelete


CUTSCENE_PATH = 'phase_13/data/cutscenes/highroller/highroller_intro.ctsc'


HIGH_ROLLER_INTRO_DIALOGUE = [
    'Hachacha!',
    "How's the hoop skip out there toe-taps, can't thank ya enough for these claps!",
    "The due morning dew duet is a pitch perfect harp strum for this singing stringer's symphonic set-strike solicitations!",
    "Takes two to tango, babe, and I am proud and poppin' to introduce today's special guest!",
    'The Casino Cardsharper...',
    'The Roulette Rockabilly...',
    'The Quartet Quack Attacker...',
    'The Spinning Wheel...',
    'Buck Ruffler: The Duck Shuffler!',
    'Buck Ruffler: The Duck Thuffler!',
    "HAHAHALIRIGHT! Let'th thake thome dithe!",
    "THE TABLE ITH HOT AND I'M ON TOP! Let'th play!!",
    "Baby Blue, ya knew my words were true-I told ya we'd meet again!",
    "Oooh, but that's no high class brass, looks like we got some surprise guests!",
    'HHAHAHHAHAHAHA DBSEHIFWEIUABYUEYKTRARTXRVEWIAYRVAESLKUSNARETSYREOYOXMROTEBURASXAEWRNEWIORVUE4OIBRUOEWUPMXAWOTBRUPOE',
    "I gueth we'll have to give em tha thpecial thow though! Come on mic thpam!",
    "Hachahoo hooi-didibadoo! Here's a special shabaadoopdaa-show from we to you!",
    'GOOD MOOORNING TOONTOOOOWN!!!',
    "Welcome back to the Tooniverffe'ff favorite ffhow!",
    "High Roller'f HighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRoller",
    "What'ya waitin' for, babe? Hop on fftage! let'ff get hoppin' and boppin', jumpin' and jinglin', ffingin' and ffwingin'!",
    "Ohoho-no-no, takeff a party to partiffipate and play, and I ffay play!!",
    "Here'ff a ffpinnin wheel I know ya can get behAHAHAHA-hind!",
    'Get ready for the ffho-ho-how of a lifetime, Bobby Dazzler!',
    "High Roller'f HighRoller",
    "High Roller'f HighRollerHighRoller",
    "High Roller'f HighRollerHighRollerHighRollerHighRoller",
    "High Roller'f HighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRoller",
    "High Roller'f HighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRoller",
    "High Roller'f HighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRollerHighRoller",
    'APPLAUSE NOW',
    'Oh my Cogth   \n\nthath me',
    'Waith I needth to thay it too',
    'WARNING\n\nTHE FOLLOWING INSTANCE\nIS NOT CANON',
    '!',
]


HIGH_ROLLER_BODY_ANIMS = {
    'neutral': 'phase_4/models/char/suitA-neutral',
    'walk': 'phase_4/models/char/suitA-walk',
    'taunt': 'phase_5/models/char/suitA-taunt',
    'hr-fusion-shot1': 'phase_12/models/char/suitA-highroller-fusiondance-shot1',
    'hr-fusion-shot2': 'phase_12/models/char/suitA-highroller-fusiondance-shot2',
    'hr-fusion-shot3': 'phase_12/models/char/suitA-highroller-fusiondance-shot3',
    'hr-fusion-shot4': 'phase_12/models/char/suitA-highroller-fusiondance-shot4',
    'hr-fusion-shot5': 'phase_12/models/char/suitA-highroller-fusiondance-shot5',
}

DUCK_SHUFFLER_BODY_ANIMS = {
    'neutral': 'phase_4/models/char/suitB-neutral',
    'walk': 'phase_4/models/char/suitB-walk',
    'slip-forward': 'phase_4/models/char/suitB-slip-forward',
    'small-zap': 'phase_5/models/char/suitB-small-zap',
    'sit-dock': 'phase_5/models/char/suitB-sit-dock',
    'ds-fusion-shot1': 'phase_10/models/char/suitB-fusiondance-shot1',
    'ds-fusion-shot2': 'phase_10/models/char/suitB-fusiondance-shot2',
    'ds-fusion-shot3': 'phase_10/models/char/suitB-fusiondance-shot3',
    'ds-fusion-shot4': 'phase_10/models/char/suitB-fusiondance-shot4',
    'ds-fusion-shot5': 'phase_10/models/char/suitB-fusiondance-shot5',
}

MAJOR_PLAYER_BODY_ANIMS = {
    'neutral': 'phase_12/models/char/suitA-rolled',
    'walk': 'phase_4/models/char/suitA-walk',
    'mp-fusion-shot1': 'phase_12/models/char/suitA-majorplayer-fusiondance-shot1',
    'mp-fusion-shot2': 'phase_12/models/char/suitA-majorplayer-fusiondance-shot2',
    'mp-fusion-shot3': 'phase_12/models/char/suitA-majorplayer-fusiondance-shot3',
    'mp-fusion-shot4': 'phase_12/models/char/suitA-majorplayer-fusiondance-shot4',
    'mp-fusion-shot5': 'phase_12/models/char/suitA-majorplayer-fusiondance-shot5',
}

HIGH_ROLLER_HEAD_ANIMS = {
    'neutral': 'phase_12/models/char/suits/cc_m_chr_ene_highroller-neutral',
    'fusiondance-shot1': 'phase_12/models/char/suits/cc_m_chr_ene_highroller-fusiondance-shot1',
    'fusiondance-shot2': 'phase_12/models/char/suits/cc_m_chr_ene_highroller-fusiondance-shot2',
    'fusiondance-shot3': 'phase_12/models/char/suits/cc_m_chr_ene_highroller-fusiondance-shot3',
    'fusiondance-shot4': 'phase_12/models/char/suits/cc_m_chr_ene_highroller-fusiondance-shot4',
    'fusiondance-shot5': 'phase_12/models/char/suits/cc_m_chr_ene_highroller-fusiondance-shot5',
}

# Altis already loads and starts the High Roller head's own neutral animation
# while generateHead3() builds the Cog.  Re-loading the phase_12 neutral alias
# creates a second control that writes the same duck joints out of phase.
# Preserve that original neutral control and add only the CTSC fusion clips.
HIGH_ROLLER_FUSION_HEAD_ANIMS = {
    name: path for name, path in list(HIGH_ROLLER_HEAD_ANIMS.items())
    if name != 'neutral'
}

DUCK_SHUFFLER_HEAD_ANIMS = {
    'neutral': 'phase_10/models/char/suits/ttcc_ene_duckshuffler-neutral',
    'fusiondance-shot1': 'phase_10/models/char/suits/ttcc_ene_duckshuffler-fusiondance-shot1',
    'fusiondance-shot2': 'phase_10/models/char/suits/ttcc_ene_duckshuffler-fusiondance-shot2',
    'fusiondance-shot3': 'phase_10/models/char/suits/ttcc_ene_duckshuffler-fusiondance-shot3',
    'fusiondance-shot4': 'phase_10/models/char/suits/ttcc_ene_duckshuffler-fusiondance-shot4',
    'fusiondance-shot5': 'phase_10/models/char/suits/ttcc_ene_duckshuffler-fusiondance-shot5',
}

MAJOR_PLAYER_HEAD_ANIMS = {
    'neutral': 'phase_12/models/char/suits/ttcc_ene_majorplayer-neutral',
    'fusiondance-shot1': 'phase_12/models/char/suits/ttcc_ene_majorplayer-fusiondance-shot1',
    'fusiondance-shot2': 'phase_12/models/char/suits/ttcc_ene_majorplayer-fusiondance-shot2',
    'fusiondance-shot3': 'phase_12/models/char/suits/ttcc_ene_majorplayer-fusiondance-shot3',
    'fusiondance-shot4': 'phase_12/models/char/suits/ttcc_ene_majorplayer-fusiondance-shot4',
    'fusiondance-shot5': 'phase_12/models/char/suits/ttcc_ene_majorplayer-fusiondance-shot5',
}

CAMERA_ANIMS = {
    'shot1': 'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot1',
    'shot2': 'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot2',
    'shot3': 'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot3',
    'shot4': 'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot4',
    'shot5': 'phase_12/models/misc/cc_p_cam_highroller-fusiondance-shot5',
}

TOON_ANIMS = ('neutral', 'walk', 'run', 'slip-forward')


def _resourceExists(path):
    filename = path if path.endswith('.bam') else path + '.bam'
    vfs = VirtualFileSystem.getGlobalPtr()
    if vfs.exists(Filename(filename)):
        return True
    relative = filename.lstrip('/\\')
    candidates = (
        os.path.join(os.getcwd(), relative),
        os.path.join(os.getcwd(), 'resources', *relative.split('/')),
        os.path.join(os.getcwd(), '..', 'resources', *relative.split('/')),
    )
    for candidate in candidates:
        if os.path.isfile(candidate):
            return True
    return False


def _getAnimatedHead(suit, label):
    parts = getattr(suit, 'animatedHeadParts', None) or []
    if not parts:
        try:
            parts = suit.getAnimatedHeadParts()
        except:
            parts = []
    if not parts:
        raise RuntimeError('[HighRoller CTSC] %s has no animated head Actor.' % label)
    head = parts[0]
    if head is None:
        raise RuntimeError('[HighRoller CTSC] %s animated head Actor is None.' % label)
    try:
        if head.isEmpty():
            raise RuntimeError('[HighRoller CTSC] %s animated head Actor is empty.' % label)
    except AttributeError:
        pass
    return head


def _queryAnimation(actor, animName):
    # Suit bodies, animated heads and the fusion camera are all single-part
    # Actors.  Ask Panda for the exact modelRoot part every time.  Altis's old
    # Actor implementation can return a valid modelRoot control from
    # getAnimControl() while getDuration()/getNumFrames() (with no part name)
    # inspect a different/default part and return None.
    partName = 'modelRoot'
    try:
        actor.bindAnim(animName, partName)
    except:
        pass
    control = actor.getAnimControl(animName, partName)
    duration = actor.getDuration(animName, partName)
    frames = actor.getNumFrames(animName, partName)
    return control, duration, frames


def _validateExistingSuitAnimations(actor, animNames, label):
    """Validate animations already registered by Altis's Suit generator.

    Do not unload and replace these aliases.  Altis managers intentionally
    override several standard names (High Roller's ``walk`` is ``awalk`` and
    Major Player's ``neutral`` is ``rolled``).  The previous provider removed
    those working mappings and recreated them as lazy controls, which later
    collapsed into a zero-length ``pose`` control while the CTSC was built.
    """
    try:
        generatedMap = actor.generateAnimDict()
    except:
        generatedMap = {}

    failures = []
    validated = []
    for animName in animNames:
        try:
            control, duration, frames = _queryAnimation(actor, animName)
        except Exception as error:
            control = duration = frames = None
            firstError = error
        else:
            firstError = None

        if control is None or duration is None or frames is None or duration <= 0 or frames <= 0:
            # Lazy binding can occasionally be missing on an existing manager
            # actor.  Reload only that actor's own generated mapping, without
            # unloading or replacing any other control.
            animPath = generatedMap.get(animName)
            if animPath:
                try:
                    actor.loadAnims({animName: animPath}, 'modelRoot')
                    control, duration, frames = _queryAnimation(actor, animName)
                except Exception as error:
                    firstError = error

        if control is None or duration is None or frames is None or duration <= 0 or frames <= 0:
            failures.append(
                '%s -> %s (control=%r duration=%r frames=%r error=%r)' %
                (animName, generatedMap.get(animName), control, duration,
                 frames, firstError))
        else:
            validated.append(animName)

    if failures:
        raise RuntimeError(
            '[HighRoller CTSC] %s existing animation validation failed:\n  %s' %
            (label, '\n  '.join(failures)))

    print(('[HighRoller CTSC] Preserved Altis %s: %s' %
          (label, ', '.join(sorted(validated)))))


def _loadAndValidateAdditionalAnimations(actor, animMap, label):
    """Add Clash-only aliases without disturbing Altis's existing controls."""
    missingFiles = []
    for animName, animPath in sorted(animMap.items()):
        if not _resourceExists(animPath):
            missingFiles.append('%s -> %s.bam' % (animName, animPath))
    if missingFiles:
        raise RuntimeError(
            '[HighRoller CTSC] Missing %s animation resources:\n  %s' %
            (label, '\n  '.join(missingFiles)))

    # Deliberately do not call unloadAnims().  Existing distributed Suit
    # actors already own working walk/neutral controls and unloading any alias
    # can invalidate the shared character bundle used by ActorInterval.
    actor.loadAnims(animMap, 'modelRoot')

    failures = []
    for animName, animPath in sorted(animMap.items()):
        try:
            control, duration, frames = _queryAnimation(actor, animName)
        except Exception as error:
            failures.append('%s -> %s (%s)' % (animName, animPath, error))
            continue
        if control is None or duration is None or frames is None or duration <= 0 or frames <= 0:
            failures.append(
                '%s -> %s (control=%r duration=%r frames=%r)' %
                (animName, animPath, control, duration, frames))

    if failures:
        raise RuntimeError(
            '[HighRoller CTSC] %s animation binding failed:\n  %s' %
            (label, '\n  '.join(failures)))

    print(('[HighRoller CTSC] Added Clash %s: %s' %
          (label, ', '.join(sorted(animMap.keys())))))



def _cacheResolvedControls(actor, animNames, label):
    """Capture the exact controls that passed preflight before CTSC build."""
    controls = {}
    failures = []
    for animName in sorted(animNames):
        try:
            control, duration, frames, frameRate = resolveControl(
                actor, animName, 'modelRoot',
                label='[HighRoller CTSC] %s %s' % (label, animName))
            controls[animName] = control
        except Exception as error:
            failures.append('%s (%s)' % (animName, error))
    if failures:
        raise RuntimeError(
            '[HighRoller CTSC] Could not cache exact %s controls:\n  %s' %
            (label, '\n  '.join(failures)))
    print(('[HighRoller CTSC] Cached exact %s controls: %s' %
          (label, ', '.join(sorted(controls.keys())))))
    return controls

def _getToonAnimControls(toon, animName):
    """Bind and return controls for Altis's multipart Toon Actor.

    Toon actors do not have a single ``modelRoot`` part.  Their animations are
    distributed across the legs, torso and head parts for each LOD.  Calling
    getAnimControl(animName) without a part therefore returns None even when
    the animation is valid, which was the cause of the previous startup crash.
    """
    controls = []
    # Altis Toon heads are not Actor animation parts; body animations are
    # carried by legs and torso at each LOD.  Probing a non-existent 'head'
    # part only produces noisy Panda warnings.
    for partName in ('legs', 'torso'):
        for lodName in ('1000', '500', '250'):
            try:
                toon.bindAnim(animName, partName, lodName)
            except:
                pass
            try:
                control = toon.getAnimControl(animName, partName, lodName)
            except:
                control = None
            if control is not None:
                controls.append(control)
    return controls


def _validateExistingAnimations(actor, animNames, label):
    failures = []
    validated = []
    for animName in animNames:
        try:
            controls = _getToonAnimControls(actor, animName)
            duration = actor.getDuration(animName)
            frames = actor.getNumFrames(animName)
        except Exception as error:
            failures.append('%s (%s)' % (animName, error))
            continue
        if not controls or duration is None or frames is None or duration <= 0 or frames <= 0:
            failures.append('%s (controls=%s duration=%r frames=%r)' %
                            (animName, len(controls), duration, frames))
        else:
            validated.append('%s[%s]' % (animName, len(controls)))
    if failures:
        raise RuntimeError(
            '[HighRoller CTSC] %s is missing required existing animations:\n  %s' %
            (label, '\n  '.join(failures)))
    print(('[HighRoller CTSC] Validated multipart %s: %s' %
          (label, ', '.join(validated))))


def _configureSuitNametag(suit, visible=False):
    """Keep Cog names hidden while allowing CTSC speech bubbles."""
    try:
        suit.hideNametag2d()
    except:
        pass
    try:
        nametag3d = suit.nametag.getNametag3d()
        nametag3d.hideNametag()
        nametag3d.showChat()
        nametag3d.showThought()
        nametag3d.update()
    except:
        pass
    try:
        if visible:
            suit.nametag3d.show()
        else:
            suit.nametag3d.hide()
    except:
        pass


def _hideResistanceToon(boss):
    # The old helper accidentally called __showResistanceToon(False), which
    # means "show Mata Hairy without a Cog disguise".  The standalone instance
    # never owns a Resistance Toon; retain a defensive purge for mixed installs.
    try:
        boss._DistributedHighRollerBoss__hideResistanceToon()
    except:
        pass
    toon = getattr(boss, 'resistanceToon', None)
    if toon:
        try:
            toon.removeActive()
        except:
            pass
        try:
            toon.detachNode()
        except:
            pass
        try:
            toon.hide()
        except:
            pass


def _playIntroductionMusic(boss):
    try:
        boss.introduction.stop()
    except:
        pass
    base.playMusic(boss.introduction, looping=1, volume=0.9)


class _AltisHighRollerTelevision(object):
    """Altis wrapper matching Clash's two-node television contract.

    Clash keeps a stationary television root in the scene graph and moves only
    the loaded model beneath it.  The intro camera is parented to that stationary
    root during the APPLAUSE shot.  Altis originally exposed only the loaded
    model, so moving it also dragged the camera.  HighRollerIntroSetup now wraps
    the model in a stationary camera target; this class moves the child only.
    """

    def __init__(self, boss):
        self.boss = boss
        self.model = boss.highRollerTV
        self.basePos = self.model.getPos()
        self.graphic = self.model.find('**/screen_graphic_full')
        self.static = self.model.find('**/screen_graphic_static_seq')
        self.text = DirectFrame(
            parent=self.model,
            relief=None,
            pos=(0, 0, 0),
            hpr=(90, 0, 0),
            scale=1.1,
            text='',
            text_pos=(0, 0),
            text_fg=(1, 1, 1, 1),
            text_wordwrap=16,
        )
        # The Altis BAM has screen geometry in front of the DirectFrame.  Keep
        # the authored 3-D placement but render the text above that geometry.
        try:
            self.text.setDepthTest(False)
            self.text.setDepthWrite(False)
            self.text.setBin('fixed', 100)
        except:
            pass
        self.text.hide()
        try:
            self.text.setTransparency(TransparencyAttrib.MAlpha)
        except:
            pass
        if not self.graphic.isEmpty():
            try:
                self.graphic.setTransparency(TransparencyAttrib.MAlpha)
                self.graphic.setColorScale(1, 1, 1, 0.70)
            except:
                pass
            self.graphic.hide()
        if not self.static.isEmpty():
            try:
                self.static.setTransparency(TransparencyAttrib.MAlpha)
            except:
                pass
            self.static.setColorScale(1, 1, 1, 0.40)
            self.static.show()
        self.model.hide()

    def cleanup(self):
        self._clear()
        try:
            self.model.setPos(self.basePos)
            self.model.hide()
        except:
            pass
        if self.text:
            self.text.destroy()
            self.text = None

    def _lineCount(self, value):
        wordwrap = 16
        count = 0
        for paragraph in (value or '').split('\n'):
            if not paragraph:
                count += 1
                continue
            current = 0
            lines = 1
            for word in paragraph.split(' '):
                size = len(word)
                if current and current + 1 + size > wordwrap:
                    lines += 1
                    current = size
                else:
                    current += size + (1 if current else 0)
            count += lines
        return max(count, 1)

    def _setText(self, value):
        value = value or ''
        if not self.graphic.isEmpty():
            self.graphic.hide()
        if not self.static.isEmpty():
            self.static.setColorScale(1, 1, 1, 0.15)
            self.static.show()
        if self.text:
            try:
                self.text.setText(value)
            except:
                self.text['text'] = value
            self.text.setPos(0, 0, (self._lineCount(value) * 0.33) - 0.5)
            self.text.show()

    def _showGraphic(self):
        if self.text:
            try:
                self.text.setText('')
            except:
                self.text['text'] = ''
            self.text.hide()
        if not self.static.isEmpty():
            self.static.setColorScale(1, 1, 1, 0.40)
            self.static.show()
        if not self.graphic.isEmpty():
            self.graphic.show()

    def _clear(self):
        if self.text:
            try:
                self.text.setText('')
            except:
                self.text['text'] = ''
            self.text.hide()
        try:
            self.text.setTransparency(TransparencyAttrib.MAlpha)
        except:
            pass
        if not self.graphic.isEmpty():
            try:
                self.graphic.setTransparency(TransparencyAttrib.MAlpha)
                self.graphic.setColorScale(1, 1, 1, 0.70)
            except:
                pass
            self.graphic.hide()
        if not self.static.isEmpty():
            try:
                self.static.setTransparency(TransparencyAttrib.MAlpha)
            except:
                pass
            self.static.setColorScale(1, 1, 1, 0.40)
            self.static.show()

    def makeTVSequence(self, questionIndex=None, doSpawn=True, doDespawn=True,
                       dropDuration=1.0, holdDuration=1.0,
                       backDuration=1.0, spawnDistance=30.0,
                       despawnDistance=30.0, overrideString=None,
                       showGraphic=False, hideAnyways=False):
        sequence = Sequence()
        basePos = self.basePos
        spawnPos = basePos + Vec3(0, 0, spawnDistance)
        despawnPos = basePos + Vec3(0, 0, despawnDistance)

        if doSpawn:
            sequence.append(Func(self.model.setPos, spawnPos))
            if not hideAnyways:
                sequence.append(Func(self.model.show))
            sequence.append(LerpPosInterval(
                self.model, dropDuration, basePos,
                startPos=spawnPos, blendType='easeOut'))
            # Altis needs no extra quarter-second before drawing the screen
            # text.  Showing it as soon as the drop completes prevents the
            # non-canon warning from appearing visibly late.
            if showGraphic:
                sequence.append(Func(self._showGraphic))
            elif overrideString is not None:
                sequence.append(Func(self._setText, overrideString))

        sequence.append(Wait(holdDuration))

        if doDespawn:
            sequence.append(LerpPosInterval(
                self.model, backDuration, despawnPos,
                startPos=basePos, blendType='easeIn'))
            sequence.append(Func(self._clear))
            sequence.append(Func(self.model.hide))
            sequence.append(Func(self.model.setPos, basePos))
        return sequence

    def setDice(self, dice):
        pass

    def pulseDice(self, pulseAmt, pulseDuration, dice):
        return Sequence()


class _AltisHighRollerWheel(object):
    def __init__(self, boss):
        self.boss = boss

    def getSpawnWheelSequence(self):
        boss = self.boss
        summon = base.loader.loadSfx(
            'phase_13/audio/sfx/april_toons/highroller/cc_s_sfx_ara_wheel_summon.ogg')
        return Sequence(
            Func(boss.highRollerWheel.hide),
            Func(boss.highRollerWheel2.show),
            Parallel(
                ActorInterval(boss.highRollerWheel2, 'wheel2'),
                SoundInterval(summon),
            ),
            Func(boss.highRollerWheel.show),
            Func(boss.highRollerWheel2.hide),
        )

    def getHurtWheelSequence(self):
        return Sequence(
            Func(self.boss.highRollerWheel2.show),
            ActorInterval(self.boss.highRollerWheel2, 'wheel2'),
            Func(self.boss.highRollerWheel2.hide),
        )

    def getSpinSequence(self, destination=None, duration=3.0, spinCount=3):
        return self.boss.makeHighRollerWheelSpin(duration, spinCount)


class _AltisHighRollerEnvironmentAdapter(object):
    def __init__(self, boss):
        self.tv = _AltisHighRollerTelevision(boss)
        self.wheel = _AltisHighRollerWheel(boss)

    def getEnvironment(self):
        return self

    def getTV(self):
        return self.tv

    def getWheel(self):
        return self.wheel

    def cleanup(self):
        self.tv.cleanup()


class HighRollerIntroSetup(object):
    def __init__(self, boss, delayDeletes):
        self.boss = boss
        self.delayDeletes = delayDeletes
        self.toons = []
        self.suits = []
        self.heads = []
        self.cutsceneRoot = None
        self.toonPosNode = None
        self.tvCameraAnchor = None
        self.cameraMover = None
        self.comedyAnvil = None
        self.anvilText = None
        self.starburst = None
        self.cameraSwapNode = None
        self.cameraBone = None
        self.environmentAdapter = None
        self.environmentStates = []
        self.suitAnimationMaps = []
        self.suitAnimationControls = []
        self.suitHeadAnimationControls = []
        self.cameraAnimationControls = {}
        self.highRollerHeadOriginalLoop = None
        self.cleanedUp = False

    def _validateAndBindActors(self):
        boss = self.boss
        self.suits = [boss.highroller, boss.duckshuffler2, boss.majorplayer2]
        self.heads = [
            _getAnimatedHead(self.suits[0], 'High Roller'),
            _getAnimatedHead(self.suits[1], 'Duck Shuffler'),
            _getAnimatedHead(self.suits[2], 'Major Player'),
        ]

        # Preserve the exact aliases generated by Altis for standard manager
        # motion.  Only the Clash-specific fusion aliases are added below.
        _validateExistingSuitAnimations(
            self.suits[0], ('neutral', 'walk', 'taunt'),
            'High Roller body controls')
        _validateExistingSuitAnimations(
            self.suits[1],
            ('neutral', 'walk', 'slip-forward', 'small-zap', 'sit-dock'),
            'Duck Shuffler body controls')
        _validateExistingSuitAnimations(
            self.suits[2], ('neutral', 'walk'),
            'Major Player body controls')

        _loadAndValidateAdditionalAnimations(
            self.suits[0], dict((name, path) for name, path in
                                list(HIGH_ROLLER_BODY_ANIMS.items())
                                if name.startswith('hr-fusion-')),
            'High Roller fusion body aliases')
        _loadAndValidateAdditionalAnimations(
            self.suits[1], dict((name, path) for name, path in
                                list(DUCK_SHUFFLER_BODY_ANIMS.items())
                                if name.startswith('ds-fusion-')),
            'Duck Shuffler fusion body aliases')
        _loadAndValidateAdditionalAnimations(
            self.suits[2], dict((name, path) for name, path in
                                list(MAJOR_PLAYER_BODY_ANIMS.items())
                                if name.startswith('mp-fusion-')),
            'Major Player fusion body aliases')

        # The generated High Roller head is already looping its original
        # neutral animation.  Validate and keep that exact control instead of
        # replacing it with another phase_12 neutral control.
        try:
            neutralControl, neutralDuration, neutralFrames = _queryAnimation(
                self.heads[0], 'neutral')
        except Exception as error:
            raise RuntimeError(
                '[HighRoller CTSC] Existing High Roller head neutral could not '
                'be resolved: %s' % error)
        if (neutralControl is None or neutralDuration is None or
                neutralFrames is None or neutralDuration <= 0 or
                neutralFrames <= 0):
            raise RuntimeError(
                '[HighRoller CTSC] Existing High Roller head neutral is invalid '
                '(control=%r duration=%r frames=%r)' %
                (neutralControl, neutralDuration, neutralFrames))
        print('[HighRoller CTSC] Preserved original Altis High Roller duck loop')
        _loadAndValidateAdditionalAnimations(
            self.heads[0], HIGH_ROLLER_FUSION_HEAD_ANIMS,
            'High Roller fusion head aliases')
        _loadAndValidateAdditionalAnimations(
            self.heads[1], DUCK_SHUFFLER_HEAD_ANIMS, 'Duck Shuffler head')
        _loadAndValidateAdditionalAnimations(
            self.heads[2], MAJOR_PLAYER_HEAD_ANIMS, 'Major Player head')

        # Preserve the exact control objects that passed preflight.  The old
        # Altis Actor dictionary can later disagree between getAnimControl()
        # and getAnimControls(); the CTSC runtime must not perform that second
        # lookup.
        self.suitAnimationControls = [
            _cacheResolvedControls(
                self.suits[0], list(HIGH_ROLLER_BODY_ANIMS.keys()),
                'High Roller body'),
            _cacheResolvedControls(
                self.suits[1], list(DUCK_SHUFFLER_BODY_ANIMS.keys()),
                'Duck Shuffler body'),
            _cacheResolvedControls(
                self.suits[2], list(MAJOR_PLAYER_BODY_ANIMS.keys()),
                'Major Player body'),
        ]
        self.suitHeadAnimationControls = [
            _cacheResolvedControls(
                self.heads[0], list(HIGH_ROLLER_HEAD_ANIMS.keys()),
                'High Roller head'),
            _cacheResolvedControls(
                self.heads[1], list(DUCK_SHUFFLER_HEAD_ANIMS.keys()),
                'Duck Shuffler head'),
            _cacheResolvedControls(
                self.heads[2], list(MAJOR_PLAYER_HEAD_ANIMS.keys()),
                'Major Player head'),
        ]

        # Do not start neutral here.  Suit.generateHead3() already started
        # this exact original control, and starting it again is what caused the
        # duck positions to alternate/reset in the supplied video.

        # Keep the original High Roller head exactly as Altis built it.
        # Dialogue may request loop('neutral') again; ignore that request only
        # while the original neutral control is already playing, so its duck
        # orbit is not restarted from frame zero after every spoken line.
        self._installHighRollerDuckLoopGuard()

        # Runtime fallback maps let an event rebind only its requested alias if
        # another Altis system lazily replaces a control before playback.
        self.suitAnimationMaps = []
        for suit, additional in (
                (self.suits[0], HIGH_ROLLER_BODY_ANIMS),
                (self.suits[1], DUCK_SHUFFLER_BODY_ANIMS),
                (self.suits[2], MAJOR_PLAYER_BODY_ANIMS)):
            try:
                mapping = suit.generateAnimDict().copy()
            except:
                mapping = {}
            for name, path in list(additional.items()):
                if 'fusion-' in name:
                    mapping[name] = path
            self.suitAnimationMaps.append(mapping)

        for suit, head in zip(self.suits, self.heads):
            suit.specialHead = head
            _configureSuitNametag(suit, visible=False)

        # Altis's Avatar.setChatAbsolute normally interrupts every animated
        # Cog head and restarts neutral when the line ends.  GeneralSequence
        # reads this marker so High Roller can speak without rewinding the
        # duck orbit.  Duck Shuffler and Major Player keep normal head speech.
        self.suits[0]._preserveHighRollerDuckLoopDuringDialogue = True

        for toonId in boss.involvedToons:
            toon = boss.cr.doId2do.get(toonId)
            if not toon:
                continue
            _validateExistingAnimations(
                toon, TOON_ANIMS, 'Toon %s (%s)' % (toonId, toon.getName()))
            self.toons.append(toon)
            self.delayDeletes.append(
                DelayDelete.DelayDelete(toon, 'HighRollerIntroCutscene'))

        while len(self.toons) < 4:
            self.toons.append(None)

    def _installHighRollerDuckLoopGuard(self):
        head = self.heads[0]
        neutralControl = self.suitHeadAnimationControls[0].get('neutral')
        if head is None or neutralControl is None:
            return
        originalLoop = head.loop

        def guardedLoop(animName, *args, **kwargs):
            # Preserve explicit ranged/part-specific calls.  The reset we need
            # to block is the plain loop('neutral') appended by Cog dialogue.
            if animName == 'neutral' and not args and not kwargs:
                try:
                    if neutralControl.isPlaying():
                        return None
                except:
                    pass
                try:
                    # restart=0 resumes the current duck phase instead of
                    # snapping the hat ducks to frame zero.
                    return neutralControl.loop(0)
                except:
                    pass
            return originalLoop(animName, *args, **kwargs)

        try:
            head.loop = guardedLoop
            self.highRollerHeadOriginalLoop = originalLoop
        except:
            self.highRollerHeadOriginalLoop = None

    def _removeHighRollerDuckLoopGuard(self):
        if not self.highRollerHeadOriginalLoop or not self.heads:
            return
        try:
            self.heads[0].loop = self.highRollerHeadOriginalLoop
        except:
            pass
        self.highRollerHeadOriginalLoop = None

    def _saveEnvironmentNode(self, node):
        self.environmentStates.append((
            node,
            node.getParent(),
            node.getTransform(),
            node.isHidden(),
        ))

    def _prepareEnvironment(self):
        boss = self.boss
        self.cutsceneRoot = render.attachNewNode('highRollerClashCutsceneRoot')
        self.cutsceneRoot.setTransform(render, boss.highRollerArena.getTransform(render))

        for node in (boss.highRollerArena, boss.highRollerTV,
                     boss.highRollerWheel, boss.highRollerWheel2):
            self._saveEnvironmentNode(node)
            node.wrtReparentTo(self.cutsceneRoot)

        boss.highRollerArena.setPosHprScale(0, 0, 0, 0, 0, 0, 1, 1, 1)
        boss.highRollerTV.setPosHprScale(
            -25.2532, 36.993, 21.6723,
            -15.536, 0, 0,
            1.4, 1.4, 1.4)

        # Clash's HighRollerTelevision is a stationary NodePath containing a
        # moving model child.  Recreate that hierarchy so camera target index 6
        # stays fixed while the visible TV descends and ascends.
        self.tvCameraAnchor = self.cutsceneRoot.attachNewNode(
            'hr-tv-stands4-hrt-vehicle')
        self.tvCameraAnchor.setPos(boss.highRollerTV.getPos())
        self.tvCameraAnchor.setHpr(boss.highRollerTV.getHpr())
        self.tvCameraAnchor.setScale(boss.highRollerTV.getScale())
        boss.highRollerTV.wrtReparentTo(self.tvCameraAnchor)

        for wheel in (boss.highRollerWheel, boss.highRollerWheel2):
            wheel.setPosHprScale(
                0, 50.5, 4.025,
                -180, 0, 0,
                5, 5, 5)
            wheel.hide()

        self.toonPosNode = self.cutsceneRoot.attachNewNode('toonPosNode')
        for toon in self.toons:
            if toon:
                toon.reparentTo(self.toonPosNode)
                toon.setColorScale(1, 1, 1, 1)

        for suit in self.suits:
            suit.reparentTo(self.cutsceneRoot)
            suit.unstash()
            suit.show()
            _configureSuitNametag(suit, visible=False)
        self.suits[0].stash()

    def _makeCameraMover(self):
        self.cameraMover = Actor(
            'phase_3.5/models/misc/camera_actor', CAMERA_ANIMS)
        self.cameraMover.reparentTo(self.cutsceneRoot)
        self.cameraMover.setPosHpr(0, 0, 0, 0, 0, 0)
        try:
            self.cameraMover.setBlend(frameBlend=base.wantSmoothAnims)
        except:
            pass
        _loadAndValidateAdditionalAnimations(
            self.cameraMover, CAMERA_ANIMS, 'High Roller fusion camera')
        self.cameraAnimationControls = _cacheResolvedControls(
            self.cameraMover, list(CAMERA_ANIMS.keys()),
            'High Roller fusion camera')
        self.cameraBone = self.cameraMover.find('**/CameraBone')
        if self.cameraBone.isEmpty():
            raise RuntimeError('[HighRoller CTSC] Camera mover has no CameraBone joint.')

    def _startFusionCamera(self):
        return Sequence(
            Func(base.camera.reparentTo, self.cameraBone),
            Func(base.camera.setPosHpr, 0, 0, 0, 0, 0, 0),
            ResolvedActorInterval(
                self.cameraMover, 'shot1',
                self.cameraAnimationControls['shot1']),
            ResolvedActorInterval(
                self.cameraMover, 'shot2',
                self.cameraAnimationControls['shot2']),
            ResolvedActorInterval(
                self.cameraMover, 'shot3',
                self.cameraAnimationControls['shot3']),
            ResolvedActorInterval(
                self.cameraMover, 'shot4',
                self.cameraAnimationControls['shot4']),
            Wait(2.0),
            ResolvedActorInterval(
                self.cameraMover, 'shot5',
                self.cameraAnimationControls['shot5']),
        )

    def _makeProps(self):
        self.comedyAnvil = globalPropPool.getProp('anvil')
        self.comedyAnvil.reparentTo(self.cutsceneRoot)
        self.anvilText = DirectFrame(
            parent=self.comedyAnvil,
            relief=None,
            pos=(0, 0, 0),
            scale=1.0,
            hpr=(0, 0, 0),
            text='The Comedy Anvil',
            text_pos=(0, 0),
            text_fg=(1, 1, 1, 1),
            text_scale=0.3,
        )
        self.starburst = loader.loadModel(
            'phase_3.5/models/props/ttcc_gen_starburst')
        self.cameraSwapNode = NodePath('swapNode')
        self.cameraSwapNode.reparentTo(hidden)

    def _makeCutsceneDict(self):
        boss = self.boss
        sounds = [
            loader.loadSfx('phase_11/audio/sfx/LB_camera_shutter_2.ogg'),
            loader.loadSfx('phase_11/audio/sfx/LB_camera_shutter_2.ogg'),
            loader.loadSfx('phase_13/audio/sfx/april_toons/highroller/cc_s_dlg_ene_hroller_good_morning_clash_general.ogg'),
            loader.loadSfx('phase_5/audio/sfx/Toon_bodyfall_synergy.ogg'),
            loader.loadSfx('phase_5/audio/sfx/SA_wager_bust_hit.ogg'),
            loader.loadSfx('phase_5/audio/sfx/SA_finger_wag.ogg'),
            loader.loadSfx('phase_13/audio/sfx/april_toons/highroller/cc_s_dlg_ene_duckshfl_normal_dialog.ogg'),
        ]

        # Clash reserves indexes 0-2 for its scene root, hidden and camera.
        # Clash's arena lives at the origin; Altis places the same arena at an
        # offset.  cutsceneRoot is therefore the translated equivalent of
        # Clash's render slot, preserving every original CTSC coordinate.
        nodes = [
            self.cutsceneRoot,
            hidden,
            camera,
            self.heads[0],
            self.cameraMover,
            self.toonPosNode,
            self.tvCameraAnchor,
            boss.highRollerWheel,
            boss.highRollerArena,
            self.heads[2],
            self.heads[1],
            self.suits[0],
            self.suits[1],
            self.suits[2],
        ] + self.toons + [
            self.comedyAnvil,
            self.anvilText,
            self.suits[1].nametag3d,
            self.suits[2].nametag3d,
            self.suits[0].nametag3d,
            self.starburst,
            self.cameraSwapNode,
            self.cameraBone,
        ]

        if len(nodes) != 26:
            raise RuntimeError(
                '[HighRoller CTSC] Node contract must contain 26 nodes; got %s.' %
                len(nodes))

        return {
            'nodes': nodes,
            'affectsCamera': True,
            'maxPlayers': 4,
            'toons': self.toons,
            'suits': self.suits,
            'actors': self.suits + self.toons,
            'messages': HIGH_ROLLER_INTRO_DIALOGUE,
            'sounds': sounds,
            'music': ['highroller_cutscene'],
            'particles': [],
            'visualEffects': [],
            'functions': [self.cleanup, self._startFusionCamera],
            'arguments': [self.environmentAdapter],
            'bosses': [],
            'elevators': [],
            'suppressSuitNametags': True,
            'suitAnimationMaps': self.suitAnimationMaps,
            'suitAnimationControls': self.suitAnimationControls,
            'suitHeadAnimationControls': self.suitHeadAnimationControls,
        }

    def build(self):
        print('[HighRoller CTSC] Building original unchanged highroller_intro.ctsc')
        _hideResistanceToon(self.boss)
        self.boss.hide()
        try:
            self._validateAndBindActors()
            self._prepareEnvironment()
            self._makeCameraMover()
            self._makeProps()
            self.environmentAdapter = _AltisHighRollerEnvironmentAdapter(self.boss)
            cutsceneTrack = buildCutscene(
                CUTSCENE_PATH, self._makeCutsceneDict())
        except:
            self.cleanup()
            raise

        return Sequence(
            Func(base.camera.reparentTo, render),
            Parallel(
                cutsceneTrack,
                Sequence(
                    Wait(2.5),
                    Func(_playIntroductionMusic, self.boss),
                ),
            ),
        )

    def cleanup(self):
        if self.cleanedUp:
            return
        self.cleanedUp = True

        boss = self.boss
        _hideResistanceToon(boss)
        if self.suits:
            try:
                delattr(
                    self.suits[0],
                    '_preserveHighRollerDuckLoopDuringDialogue')
            except:
                pass
        self._removeHighRollerDuckLoopGuard()
        try:
            boss.introduction.stop()
        except:
            pass

        try:
            base.camera.wrtReparentTo(render)
        except:
            pass

        for toon in self.toons:
            if toon:
                try:
                    toon.wrtReparentTo(render)
                    toon.clearColorScale()
                    try:
                        toon.setAnimState('Happy')
                    except:
                        toon.loop('neutral')
                    toon.show()
                except:
                    pass

        for suit in self.suits:
            if suit:
                try:
                    suit.clearChat()
                    _configureSuitNametag(suit, visible=False)
                    suit.wrtReparentTo(boss.geom)
                    suit.hide()
                    suit.stash()
                except:
                    pass

        if self.environmentAdapter:
            self.environmentAdapter.cleanup()
            self.environmentAdapter = None

        for node, parent, transform, wasHidden in reversed(self.environmentStates):
            try:
                node.reparentTo(parent)
                node.setTransform(transform)
                if wasHidden:
                    node.hide()
                else:
                    node.show()
            except:
                pass
        self.environmentStates = []
        self.suitAnimationMaps = []

        if self.tvCameraAnchor:
            try:
                self.tvCameraAnchor.removeNode()
            except:
                pass
            self.tvCameraAnchor = None

        if self.cameraMover:
            try:
                self.cameraMover.delete()
            except:
                self.cameraMover.removeNode()
            self.cameraMover = None
        if self.anvilText:
            try:
                self.anvilText.destroy()
            except:
                pass
            self.anvilText = None
        if self.comedyAnvil:
            self.comedyAnvil.removeNode()
            self.comedyAnvil = None
        if self.starburst:
            self.starburst.removeNode()
            self.starburst = None
        if self.cameraSwapNode:
            self.cameraSwapNode.removeNode()
            self.cameraSwapNode = None
        if self.toonPosNode:
            self.toonPosNode.removeNode()
            self.toonPosNode = None
        if self.cutsceneRoot:
            self.cutsceneRoot.clearColorScale()
            self.cutsceneRoot.removeNode()
            self.cutsceneRoot = None

        if getattr(boss, '_highRollerIntroSetup', None) is self:
            boss._highRollerIntroSetup = None


def makeHighRollerIntroduction(boss, delayDeletes):
    setup = HighRollerIntroSetup(boss, delayDeletes)
    boss._highRollerIntroSetup = setup
    return setup.build()
