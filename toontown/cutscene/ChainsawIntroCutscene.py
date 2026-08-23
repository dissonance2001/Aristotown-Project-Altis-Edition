import random

"""Corporate Clash Chainsaw Consultant intro adapter for Project Altis/Python 2.

The original ``chainsawconsultant_intro.ctsc`` remains unchanged.  This file
only supplies the exact actors, nodes, resources and small compatibility
bridges that Clash normally provides around the CTSC runtime.
"""

from direct.actor import Actor
from direct.interval.IntervalGlobal import (
    ActorInterval, Func, LerpFunctionInterval, LerpHprInterval, Parallel, ProjectileInterval,
    Sequence, SoundInterval, Wait)

from panda3d.core import Texture, TextureStage, Vec3

from toontown.cutscene.AltisCutsceneCompat import (
    cacheResolvedControls,
    configureSuitNametag,
    validateExistingMultipartAnimations,
    validateExistingSuitAnimations,
)
from toontown.cutscene.repository.CutsceneRuntime import buildCutscene
from toontown.cutscene.sequences import GeneralSequence, SuitSequence
from toontown.battle import BattleProps
from toontown.distributed import DelayDelete
from toontown.suit import Suit
from toontown.suit import SuitDNA


CUTSCENE_PATH = (
    'phase_12/data/cutscenes/chainsawconsultant/'
    'chainsawconsultant_intro.ctsc')
INTRO_MUSIC_PATH = 'phase_12/audio/bgm/merc/instance_chainsaw_ctscn.ogg'
OVERRIDE_SFX_PATH = (
    'phase_12/audio/sfx/'
    'instance_chainsawconsultant_ctscn_intro_override.ogg')
CHAINSAW_LANDING_ANIM_PATH = (
    'phase_12/models/char/suitA-chainsaw-intro-landing')

CHAINSAW_PROJECTED_DIALOGUE = (
    'Now.',
    'TERMINATION SEQUENCE IN PROGRESS.',
)

CHAINSAW_DIALOGUE = (
    "Ugh, it's you critters again.",
    "You're lucky that none of you work for this company or else you'd be out of here in a cannon.",
    "I'm kind of busy right now, can you go away?",
    "Please don't do that. You don't want to see what happens when I get angry.",
    "I'll have you know that I already called security, they should be here right...",
    "Now.",
    "Mr. Revvington, sir! I came as soon as I learned that your office was under attack by Toons!",
    "Where's the rest of the security? There's supposed to be four of you.",
    "I'm a member of the Deforester Force!",
    "No, you're not! I don't remember you being part of that at all.",
    "I was told that you fired all of them yesterday!",
    "See, I don't remember that, so there's clearly no record of it!",
    "If there's no record, then I can't file a report detailing it!",
    "And if I can't file a report, then what's the point of-",
    "PERSONALITY OVERRIDE ACTIVATED.",
    "PLEASE WAIT.",
    "PERSONALITY OVERRIDE COMPLETE.",
    "Now you'll never stop us! Chip and I are gonna send you straight to the Chairman!",
    "ENTERING EMPLOYEE TERMINATION MODE.",
    "Wait! No! We were going to be a team!",
    "ADDITIONAL ENTITIES IDENTIFIED.",
    "TERMINATION SEQUENCE IN PROGRESS.",
)

CHAINSAW_BODY_ANIMS = (
    'sit',
    'sit-lose',
    'rake-react',
    'neutral-override',
    'lured',
    'walk',
    'neutral',
    'landing',
)

FLUNKY_BODY_ANIMS = (
    'walk',
    'neutral',
    'flail',
    'pie-small-react',
)

TOON_ANIMS = (
    'walk',
    'duck',
    'neutral',
)

CHAINSAW_OVERRIDE_EFFECT = 'CHAINSAW_OVERRIDE'

_HEAD_PREFIX = 'phase_12/models/char/suits/ttcc_ene_chainsaw'
_HEAD_NORMAL = {
    'neutral': _HEAD_PREFIX + '-neutral',
    'talk': _HEAD_PREFIX + '-murmur',
    'murmur': _HEAD_PREFIX + '-murmur',
    'grunt': _HEAD_PREFIX + '-grunt',
    'statement': _HEAD_PREFIX + '-statement',
    'question': _HEAD_PREFIX + '-question',
    'stun': _HEAD_PREFIX + '-stun',
    'neutral-lured': _HEAD_PREFIX + '-neutral-lured',
    'neutral-hurt': _HEAD_PREFIX + '-neutral-hurt',
    'death': _HEAD_PREFIX + '-death',
    'leap': _HEAD_PREFIX + '-cutscene-leap',
    'getup': _HEAD_PREFIX + '-cutscene-getup',
    'hurt-neutral': _HEAD_PREFIX + '-cutscene-hurt-neutral',
    'hurt-walk': _HEAD_PREFIX + '-cutscene-hurt-walk',
    'laying': _HEAD_PREFIX + '-cutscene-laying',
    'todesk': _HEAD_PREFIX + '-cutscene-todesk',
    'desk-neutral': _HEAD_PREFIX + '-cutscene-desk-neutral',
    'revvedup': _HEAD_PREFIX + '-revvedup',
    'sparkplug': _HEAD_PREFIX + '-sparkplug',
    'scabbard': _HEAD_PREFIX + '-scabbard',
    'throttle': _HEAD_PREFIX + '-throttle',
    'throttle2': _HEAD_PREFIX + '-throttle2',
}
_HEAD_GLITCH = {
    'neutral': _HEAD_PREFIX + '_b-neutral',
    'talk': _HEAD_PREFIX + '_b-murmur',
    'murmur': _HEAD_PREFIX + '_b-murmur',
    'grunt': _HEAD_PREFIX + '_b-grunt',
    'statement': _HEAD_PREFIX + '_b-statement',
    'question': _HEAD_PREFIX + '_b-question',
    'stun': _HEAD_PREFIX + '_b-stun',
    'neutral-lured': _HEAD_PREFIX + '_b-neutral-lured',
    'neutral-hurt': _HEAD_PREFIX + '_b-neutral-hurt',
    'death': _HEAD_PREFIX + '_b-death',
    'leap': _HEAD_PREFIX + '-cutscene-leap',
    'getup': _HEAD_PREFIX + '-cutscene-getup',
    'hurt-neutral': _HEAD_PREFIX + '-cutscene-hurt-neutral',
    'hurt-walk': _HEAD_PREFIX + '-cutscene-hurt-walk',
    'laying': _HEAD_PREFIX + '-cutscene-laying',
    'todesk': _HEAD_PREFIX + '-cutscene-todesk',
    'desk-neutral': _HEAD_PREFIX + '-cutscene-desk-neutral',
    # These battle-only head animations are shared by all three head modes.
    'revvedup': _HEAD_PREFIX + '-revvedup',
    'sparkplug': _HEAD_PREFIX + '-sparkplug',
    'scabbard': _HEAD_PREFIX + '-scabbard',
    'throttle': _HEAD_PREFIX + '-throttle',
    'throttle2': _HEAD_PREFIX + '-throttle2',
}

CHAINSAW_BATTLE_BODY_ANIMS = {
    'deadwood': 'phase_12/models/char/suitA-deadwood',
    'layoffs': 'phase_12/models/char/suitA-layoffs',
    'summon': 'phase_5/models/char/suitA-summon',
    'soak': 'phase_5/models/char/suitA-soak',
    'neutral-override': 'phase_12/models/char/suitA-neutral-override',
    'neutral-override-glitched': 'phase_12/models/char/suitA-neutral-override-glitched',
    'revvedup': 'phase_12/models/char/suitA-revvedup',
    'scabbard': 'phase_12/models/char/suitA-scabbard',
    'snap-override': 'phase_12/models/char/suitA-snap-override',
    'sparkplug': 'phase_12/models/char/suitA-sparkplug',
    'throttle': 'phase_12/models/char/suitA-throttle',
    'throttletwo': 'phase_12/models/char/suitA-throttletwo',
    'leap': 'phase_12/models/char/suitA-chainsaw-cutscene-leap',
    'getup': 'phase_12/models/char/suitA-chainsaw-cutscene-getup',
    'hurt-neutral': 'phase_12/models/char/suitA-chainsaw-cutscene-hurt-neutral',
    'hurt-walk': 'phase_12/models/char/suitA-chainsaw-cutscene-hurt-walk',
    'laying': 'phase_12/models/char/suitA-chainsaw-cutscene-laying',
    'todesk': 'phase_12/models/char/suitA-chainsaw-cutscene-todesk',
    'desk-neutral': 'phase_12/models/char/suitA-chainsaw-cutscene-desk-neutral',
}

_VOICE_NORMAL = (
    'phase_12/audio/dial/ttcc_ene_chainsaw_grunt.ogg',
    'phase_12/audio/dial/ttcc_ene_chainsaw_murmur.ogg',
    'phase_12/audio/dial/ttcc_ene_chainsaw_statement.ogg',
    'phase_12/audio/dial/ttcc_ene_chainsaw_question.ogg',
)
_VOICE_GLITCH = (
    'phase_12/audio/dial/ttcc_ene_chainsaw_grunt_or.ogg',
    'phase_12/audio/dial/ttcc_ene_chainsaw_murmur_or.ogg',
    'phase_12/audio/dial/ttcc_ene_chainsaw_statement_or.ogg',
    'phase_12/audio/dial/ttcc_ene_chainsaw_question_or.ogg',
)


class _ChainsawIntroHead(Actor.Actor):
    """Small Python-2 adapter for Clash's ChainsawAnimatedSuitHead."""

    def __init__(self, suit):
        self.suit = suit
        self.inGlitch = False
        self.glitchState = 'normal'
        self.sfx = None
        self.texRollIval = None
        self.freakoutSeq = None
        self.freakoutTaskName = 'chainsawHeadFreakout-%s' % id(self)
        self.freakoutOriginalHpr = None

        allAnims = dict(_HEAD_NORMAL)
        for name, path in list(_HEAD_GLITCH.items()):
            allAnims['glitch-' + name] = path

        Actor.Actor.__init__(self, _HEAD_PREFIX + '-zero', allAnims)
        self.normalTex = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw.png')
        self.glitchTex = loader.loadTexture('phase_12/maps/ttcc_ene_chainsaw_b.png')
        self._prepareTexture(self.normalTex)
        self._prepareTexture(self.glitchTex)
        self.setTexture(self.normalTex, 1)
        self.setTwoSided(True)
        self.setScale(0.98)
        self.setZ(0.03)
        self.bulbLeft = self.find('**/bulbLeft')
        self.bulbRight = self.find('**/bulbRight')
        self.normalVoiceArray = self._loadVoiceArray(_VOICE_NORMAL)
        self.glitchVoiceArray = self._loadVoiceArray(_VOICE_GLITCH)
        self.loop('neutral')
        self.updateSuitVoice(False)

    @staticmethod
    def _prepareTexture(tex):
        if not tex:
            return
        try:
            tex.setWrapU(Texture.WM_repeat)
            tex.setWrapV(Texture.WM_repeat)
        except:
            try:
                tex.setWrapU(Texture.WMRepeat)
                tex.setWrapV(Texture.WMRepeat)
            except:
                pass
        try:
            tex.setMinfilter(Texture.FTLinearMipmapLinear)
            tex.setMagfilter(Texture.FTLinear)
        except:
            pass

    def _animName(self, name):
        if self.inGlitch and name in _HEAD_GLITCH:
            return 'glitch-' + name
        return name

    def getAnimControl(self, animName=None, *args, **kwargs):
        return Actor.Actor.getAnimControl(
            self, self._animName(animName), *args, **kwargs)

    def getDuration(self, animName=None, *args, **kwargs):
        return Actor.Actor.getDuration(
            self, self._animName(animName), *args, **kwargs)

    def getNumFrames(self, animName=None, *args, **kwargs):
        return Actor.Actor.getNumFrames(
            self, self._animName(animName), *args, **kwargs)

    def loop(self, animName, *args, **kwargs):
        return Actor.Actor.loop(
            self, self._animName(animName), *args, **kwargs)

    def play(self, animName, *args, **kwargs):
        return Actor.Actor.play(
            self, self._animName(animName), *args, **kwargs)

    def pose(self, animName, *args, **kwargs):
        return Actor.Actor.pose(
            self, self._animName(animName), *args, **kwargs)

    def pingpong(self, animName, *args, **kwargs):
        return Actor.Actor.pingpong(
            self, self._animName(animName), *args, **kwargs)

    def actorInterval(self, animName, *args, **kwargs):
        return ActorInterval(
            self, self._animName(animName), *args, **kwargs)

    def loopNeutral(self):
        self.loop('neutral')

    @staticmethod
    def _loadVoiceArray(paths):
        sounds = [loader.loadSfx(path) for path in paths]
        grunt, murmur, statement, question = sounds
        return (
            grunt, murmur, statement, question,
            grunt, murmur, statement)

    def getDialogueArray(self):
        if self.inGlitch:
            return self.glitchVoiceArray
        return self.normalVoiceArray

    def updateSuitVoice(self, glitch=False):
        voiceArray = self.glitchVoiceArray if glitch else self.normalVoiceArray
        voice = getattr(self.suit, 'voice', None)
        if voice:
            voice.voiceArray = voiceArray

    def _setFreakoutTexture(self, texture):
        if texture:
            self.setTexture(texture, 1)

    def _chooseFreakoutRepeatCount(self):
        roll = random.randint(1, 14)
        if roll <= 10:
            return 1
        if roll <= 13:
            return 2
        return 3

    def _doFreakout(self, task):
        if self.glitchState != 'semi':
            return task.done

        if self.freakoutSeq:
            try:
                self.freakoutSeq.pause()
            except:
                pass
            self.freakoutSeq = None

        originalHpr = self.freakoutOriginalHpr
        if originalHpr is None:
            originalHpr = self.getHpr()
            self.freakoutOriginalHpr = Vec3(originalHpr)

        repeatCount = self._chooseFreakoutRepeatCount()
        seq = Sequence()

        for index in range(repeatCount):
            twitchTime = random.uniform(0.07, 0.12)
            useHeading = random.random() < 0.5
            if useHeading:
                minimumAngle = 10.0
                maximumAngle = 25.0
            else:
                minimumAngle = 10.0 * (2.0 / 3.0)
                maximumAngle = 25.0 * (2.0 / 3.0)

            angle = random.uniform(minimumAngle, maximumAngle)
            angle *= random.choice((-1, 1))

            if useHeading:
                finalHpr = Vec3(
                    originalHpr.getX() + angle,
                    originalHpr.getY(),
                    originalHpr.getZ())
            else:
                finalHpr = Vec3(
                    originalHpr.getX(),
                    originalHpr.getY(),
                    originalHpr.getZ() + angle)

            seq.append(Sequence(
                Func(self._setFreakoutTexture, self.glitchTex),
                LerpHprInterval(
                    self, twitchTime, finalHpr,
                    startHpr=originalHpr)))

            if index == repeatCount - 1:
                seq.append(Func(self._setFreakoutTexture, self.normalTex))
                seq.append(LerpHprInterval(
                    self, twitchTime * 2.0, originalHpr,
                    blendType='easeOut'))

        self.freakoutSeq = seq
        seq.start()
        task.delayTime = random.uniform(1.5, 4.0) + seq.getDuration()
        return task.again

    def _stopFreakout(self):
        try:
            taskMgr.remove(self.freakoutTaskName)
        except:
            pass
        if self.freakoutSeq:
            try:
                self.freakoutSeq.pause()
            except:
                pass
            self.freakoutSeq = None
        if self.freakoutOriginalHpr is not None:
            self.setHpr(self.freakoutOriginalHpr)
        self.freakoutOriginalHpr = None
        if self.normalTex and self.glitchState == 'semi':
            self.setTexture(self.normalTex, 1)

    def _startFreakout(self):
        self._stopFreakout()
        self.freakoutOriginalHpr = Vec3(self.getHpr())
        taskMgr.doMethodLater(
            random.uniform(1.5, 4.0),
            self._doFreakout,
            self.freakoutTaskName)

    def enterGlitch(self, temp=None):
        self._stopFreakout()
        self.inGlitch = True
        self.glitchState = 'glitch'
        self.loadAnims(_HEAD_GLITCH)
        if self.glitchTex:
            self.setTexture(self.glitchTex, 1)
        self.updateSuitVoice(True)
        self.loop('neutral')
        try:
            self.suit.setSuitStatusEffect('glitched')
            self.suit.clearSuitStatusEffect('semi-glitched')
            self.suit.setChainsawTexRoll()
        except:
            pass

    def enterSemiGlitch(self, temp=None):
        self.inGlitch = False
        self.glitchState = 'semi'
        self.loadAnims(_HEAD_NORMAL)
        if self.normalTex:
            self.setTexture(self.normalTex, 1)
        self.updateSuitVoice(False)
        self.loop('neutral')
        try:
            self.suit.clearSuitStatusEffect('glitched')
            self.suit.setSuitStatusEffect('semi-glitched')
        except:
            pass

    def beginSemiGlitchFreakout(self):
        self.enterSemiGlitch()
        self._startFreakout()

    def endSemiGlitchFreakout(self):
        self._stopFreakout()

    def exitGlitch(self, temp=None):
        self._stopFreakout()
        self.inGlitch = False
        self.glitchState = 'normal'
        self.loadAnims(_HEAD_NORMAL)
        if self.normalTex:
            self.setTexture(self.normalTex, 1)
        self.updateSuitVoice(False)
        self.loop('neutral')
        try:
            self.suit.clearSuitStatusEffect('glitched')
            self.suit.clearSuitStatusEffect('semi-glitched')
        except:
            pass

    def setChainsawTexRoll(self, duration=1.6):
        if self.texRollIval:
            try:
                self.texRollIval.pause()
            except:
                pass
            self.texRollIval = None
        if duration <= 0:
            return
        chain = self.find('**/Chain')
        if chain.isEmpty():
            return

        def rollTexMatrix(t, obj=chain):
            obj.setTexOffset(TextureStage.getDefault(), t, 0)

        self.texRollIval = LerpFunctionInterval(
            rollTexMatrix, fromData=1, toData=0, duration=duration)
        self.texRollIval.loop()

    def startIdleSfx(self):
        if self.sfx:
            try:
                self.sfx.stop()
            except:
                pass
        self.sfx = loader.loadSfx(
            'phase_12/audio/dial/ttcc_ene_chainsaw_idle.ogg')
        if self.sfx:
            try:
                self.sfx.setLoop(True)
                self.sfx.setVolume(0.5)
            except:
                pass
            self.sfx.play()

    def stopIntroEffects(self):
        self._stopFreakout()
        if self.sfx:
            try:
                self.sfx.stop()
            except:
                pass
            self.sfx = None
        if self.texRollIval:
            try:
                self.texRollIval.pause()
            except:
                pass
            self.texRollIval = None


def installChainsawBattleHead(suit, phase=1):
    """Install the exact Clash Chainsaw head/body controls on a live Suit.

    This is deliberately Chainsaw-specific.  It does not modify Suit.py or any
    shared boss/battle class, and can safely be called repeatedly as the
    distributed battle Suit becomes available.
    """
    if suit is None:
        return None

    head = getattr(suit, 'specialHead', None)
    if not isinstance(head, _ChainsawIntroHead):
        oldHeads = list(getattr(suit, 'headParts', []) or [])
        for oldHead in oldHeads:
            try:
                oldHead.hide()
            except:
                pass

        head = _ChainsawIntroHead(suit)
        joint = suit.find('**/joint_head')
        if joint.isEmpty():
            try:
                head.cleanup()
            except:
                pass
            return None
        head.reparentTo(joint)
        suit.headParts = [head]
        suit.animatedHeadParts = [head]
        suit.specialHead = head
        suit.getDialogueArray = head.getDialogueArray
        suit._chainsawAltisOldHeadParts = oldHeads

    try:
        suit.loadAnims(CHAINSAW_BATTLE_BODY_ANIMS, 'modelRoot')
    except:
        pass

    try:
        summonControl = suit.getAnimControl('summon')
    except:
        summonControl = None
    if summonControl is None:
        try:
            suit.loadAnims({'summon': 'phase_4/models/char/suitA-summon'}, 'modelRoot')
        except:
            pass

    if not hasattr(suit, 'leftHand') or suit.leftHand is None:
        try:
            suit.leftHand = suit.getLeftHand()
        except:
            try:
                suit.leftHand = suit.find('**/joint_Lhold')
            except:
                suit.leftHand = suit

    phase = max(1, min(3, int(phase)))
    if phase == 1:
        head.enterGlitch()
    elif phase == 2:
        head.enterSemiGlitch()
    else:
        head.enterGlitch()
    return head


class ChainsawIntroSetup(object):

    def __init__(self, boss, delayDeletes):
        self.boss = boss
        self.delayDeletes = delayDeletes
        self.actualToons = []
        self.toons = []
        self.chainsaw = None
        self.fakeSuit = None
        self.head = None
        self.oldHeadParts = None
        self.oldAnimatedHeadParts = None
        self.oldSpecialHead = None
        self.oldGetDialogueArray = None
        self.introMusic = None
        self.cleanedUp = False
        self.suitAnimationMaps = []
        self.suitAnimationControls = []

    def _installProjectilePropellerCompat(self, suit):
        if not hasattr(suit, 'prop'):
            suit.prop = None
        if not hasattr(suit, 'propInSound') or suit.propInSound is None:
            suit.propInSound = base.loader.loadSfx(
                'phase_5/audio/sfx/ENC_propeller_in.ogg')
        if not hasattr(suit, 'propOutSound') or suit.propOutSound is None:
            suit.propOutSound = base.loader.loadSfx(
                'phase_5/audio/sfx/ENC_propeller_out.ogg')
        if not hasattr(suit, 'lockProp'):
            suit.lockProp = False

        def attachPropeller():
            if suit.prop is None:
                suit.prop = BattleProps.globalPropPool.getProp('propeller')
            head = suit.find('**/to_head')
            if head.isEmpty():
                head = suit.find('**/joint_head')
            if not head.isEmpty():
                suit.prop.reparentTo(head)

        def setPropellerLocked(locked=False):
            suit.lockProp = locked
            if not locked:
                detachPropeller()

        def detachPropeller():
            prop = getattr(suit, 'prop', None)
            if getattr(suit, 'lockProp', False):
                if prop:
                    try:
                        prop.hide()
                    except:
                        pass
                return
            if prop:
                try:
                    prop.cleanup()
                except:
                    pass
                try:
                    prop.removeNode()
                except:
                    pass
                suit.prop = None

        suit.attachPropeller = attachPropeller
        suit.setPropellerLocked = setPropellerLocked
        suit.detachPropeller = detachPropeller

    def _createProjectileMoveIval(self, suit, destPos, duration, gravityMult=0.4):
        """Clash projectile flight, explicitly bound to Altis modelRoot."""
        partName = 'modelRoot'
        landingDur = suit.getDuration('landing', partName)
        flyingDur = duration - landingDur

        def holdAirbornePose(value):
            try:
                suit.pose('landing', 0, partName)
            except:
                suit.pose('landing', 0)

        moveIval = Sequence(
            Func(holdAirbornePose, 0.0),
            Parallel(
                ProjectileInterval(
                    suit, duration=flyingDur, endPos=destPos,
                    gravityMult=gravityMult),
                LerpFunctionInterval(
                    holdAirbornePose, fromData=0.0, toData=1.0,
                    duration=flyingDur),
            ),
            ActorInterval(suit, 'landing', partName=partName),
        )

        if suit.prop is None:
            suit.prop = BattleProps.globalPropPool.getProp('propeller')

        lastSpinFrame = 8
        frameRate = suit.prop.getFrameRate('propeller')
        spinTime = float(lastSpinFrame) / frameRate
        openTime = float(lastSpinFrame + 1) / frameRate

        propTrack = Parallel(
            SoundInterval(suit.propInSound, duration=flyingDur, node=suit),
            Sequence(
                ActorInterval(
                    suit.prop, 'propeller', constrainedLoop=1,
                    duration=flyingDur + 1, startTime=0.0,
                    endTime=spinTime),
                ActorInterval(
                    suit.prop, 'propeller', duration=landingDur,
                    startTime=openTime),
                Func(suit.detachPropeller),
            ),
        )

        return Parallel(
            Sequence(
                Func(suit.attachPropeller),
                ActorInterval(
                    suit.prop, 'propeller', startFrame=lastSpinFrame,
                    endFrame=suit.prop.getNumFrames('propeller'),
                    playRate=-1.6),
            ),
            Sequence(Wait(0.5), Parallel(moveIval, propTrack)),
        )

    def _buildCutsceneWithProjectileCompat(self):
        originalProjectile = SuitSequence.createSuitMoveIval
        originalDetached = GeneralSequence.DETACHED_DIALOGUE_MESSAGES

        detached = list(originalDetached)
        for message in CHAINSAW_PROJECTED_DIALOGUE:
            if message not in detached:
                detached.append(message)
        GeneralSequence.DETACHED_DIALOGUE_MESSAGES = tuple(detached)

        # These two authored scale=3 bubbles are lost by Altis's native
        # Nametag3d during their camera cuts.  Keep their Clash emphasis but
        # project them from the authored head-height point with no unrelated
        # High Roller screen offset.
        GeneralSequence.DETACHED_DIALOGUE_SCREEN_OFFSETS['Now.'] = (0.0, 0.0)
        GeneralSequence.DETACHED_DIALOGUE_SCREEN_OFFSETS[
            'TERMINATION SEQUENCE IN PROGRESS.'] = (0.40, 0.42)
        GeneralSequence.DETACHED_DIALOGUE_SCREEN_SCALES['Now.'] = 1.0
        GeneralSequence.DETACHED_DIALOGUE_SCREEN_SCALES[
            'TERMINATION SEQUENCE IN PROGRESS.'] = 0.72

        SuitSequence.createSuitMoveIval = self._createProjectileMoveIval
        try:
            return buildCutscene(CUTSCENE_PATH, self._makeCutsceneDict())
        finally:
            SuitSequence.createSuitMoveIval = originalProjectile
            GeneralSequence.DETACHED_DIALOGUE_MESSAGES = originalDetached

    def _installCannonCompat(self, suit):
        if not hasattr(suit, 'makeUnemployed'):
            suit.makeUnemployed = lambda: None

        originalCreateNameInfo = getattr(suit, 'createNameInfo', None)

        def createNameInfo(wantDept=False):
            if originalCreateNameInfo:
                try:
                    return originalCreateNameInfo()
                except:
                    pass
            return 'Flunky'

        suit.createNameInfo = createNameInfo

    def _prepareChainsaw(self):
        suit = self.boss.sceneSuit
        if not suit:
            raise RuntimeError('[Chainsaw CTSC] Chainsaw actor is not ready')

        suit.wrtReparentTo(render)
        suit.show()
        suit.unstash()
        self._installProjectilePropellerCompat(suit)

        bodyMap = suit.generateAnimDict().copy()
        bodyMap['sit'] = 'phase_12/models/char/suitA-sit'
        bodyMap['sit-lose'] = 'phase_12/models/char/suitA-sit-lose'
        bodyMap['neutral-override'] = (
            'phase_12/models/char/suitA-neutral-override')
        # The projectile sequence holds frame 0 of ``landing`` while Chainsaw
        # is airborne.  Use Clash's exact BAM locally so Altis's general Suit
        # landing asset cannot turn that authored flying pose into a stand.
        bodyMap['landing'] = CHAINSAW_LANDING_ANIM_PATH
        suit.loadAnims({
            'sit': bodyMap['sit'],
            'sit-lose': bodyMap['sit-lose'],
            'neutral-override': bodyMap['neutral-override'],
            'landing': bodyMap['landing'],
        }, 'modelRoot')
        validateExistingSuitAnimations(
            suit, CHAINSAW_BODY_ANIMS,
            'Chainsaw body controls', logPrefix='[Chainsaw CTSC]')

        self.suitAnimationMaps.append(bodyMap)
        self.suitAnimationControls.append(cacheResolvedControls(
            suit, CHAINSAW_BODY_ANIMS,
            'Chainsaw body', logPrefix='[Chainsaw CTSC]'))

        self.oldHeadParts = list(getattr(suit, 'headParts', []) or [])
        self.oldAnimatedHeadParts = list(
            getattr(suit, 'animatedHeadParts', []) or [])
        self.oldSpecialHead = getattr(suit, 'specialHead', None)
        for oldHead in self.oldHeadParts:
            try:
                oldHead.hide()
            except:
                pass

        head = _ChainsawIntroHead(suit)
        joint = suit.find('**/joint_head')
        if joint.isEmpty():
            raise RuntimeError('[Chainsaw CTSC] Chainsaw has no joint_head')
        head.reparentTo(joint)
        suit.headParts = [head]
        suit.animatedHeadParts = [head]
        suit.specialHead = head
        self.oldGetDialogueArray = getattr(suit, 'getDialogueArray', None)
        suit.getDialogueArray = head.getDialogueArray
        self.head = head
        self.boss._chainsawSpecialHead = head

        configureSuitNametag(suit, visible=False)
        self.chainsaw = suit

    def _prepareFakeSuit(self):
        dna = SuitDNA.SuitDNA()
        dna.newSuit('f')
        fake = Suit.Suit()
        fake.setDNA(dna)
        fake.dna = dna
        fake.doId = -2550
        fake.getActualLevel = lambda: 5
        self._installCannonCompat(fake)
        try:
            fake.setDisplayName(fake.createNameInfo())
        except:
            try:
                fake.setDisplayName('Flunky')
            except:
                pass
        try:
            fake.setPickable(0)
        except:
            pass
        fake.reparentTo(render)
        fake.setPos(-6.71751, 7.08061, 0.0)
        fake.loop('neutral')
        fake.stash()
        configureSuitNametag(fake, visible=False)

        validateExistingSuitAnimations(
            fake, FLUNKY_BODY_ANIMS,
            'Flunky body controls', logPrefix='[Chainsaw CTSC]')
        fakeMap = fake.generateAnimDict().copy()
        self.suitAnimationMaps.append(fakeMap)
        self.suitAnimationControls.append(cacheResolvedControls(
            fake, FLUNKY_BODY_ANIMS,
            'Flunky body', logPrefix='[Chainsaw CTSC]'))
        self.fakeSuit = fake

    def _prepareToons(self):
        for toonId in self.boss.involvedToons:
            toon = self.boss.cr.doId2do.get(toonId)
            if not toon:
                continue
            validateExistingMultipartAnimations(
                toon, TOON_ANIMS,
                'Toon %s (%s)' % (toonId, toon.getName()),
                logPrefix='[Chainsaw CTSC]')
            toon.wrtReparentTo(render)
            self.actualToons.append(toon)
            self.delayDeletes.append(
                DelayDelete.DelayDelete(toon, 'ChainsawIntroCutscene'))
        self.toons = list(self.actualToons)
        while len(self.toons) < 4:
            self.toons.append(None)

    def _prepareActors(self):
        self._prepareChainsaw()
        self._prepareFakeSuit()
        self._prepareToons()

    def _makeCutsceneDict(self):
        # Clash CutsceneLoader starts with render/hidden/camera.  The original
        # Chainsaw setup then appends battleNode, geom, Chainsaw, then six door
        # leaves.  The CTSC's numeric node indices depend on this exact order.
        nodes = [
            render,
            hidden,
            camera,
            self.boss.battleNode,
            self.boss.geom,
            self.chainsaw,
        ] + list(self.boss.doorList)

        return {
            'nodes': nodes,
            'affectsCamera': True,
            'maxPlayers': 4,
            'toons': self.toons,
            'suits': [self.chainsaw, self.fakeSuit],
            'actors': [self.chainsaw, self.fakeSuit] + self.actualToons,
            'messages': CHAINSAW_DIALOGUE,
            'sounds': [
                base.loader.loadSfx('phase_9/audio/sfx/CHQ_door_open.ogg'),
                base.loader.loadSfx('phase_9/audio/sfx/CHQ_door_close.ogg'),
                base.loader.loadSfx(OVERRIDE_SFX_PATH),
            ],
            'music': [],
            'particles': [],
            'visualEffects': [CHAINSAW_OVERRIDE_EFFECT],
            'functions': [],
            'arguments': [],
            'bosses': [],
            'elevators': [],
            'suppressSuitNametags': True,
            'suitAnimationMaps': self.suitAnimationMaps,
            'suitAnimationControls': self.suitAnimationControls,
            'suitHeadAnimationControls': [],
        }

    def _startMusic(self):
        if self.introMusic is None:
            self.introMusic = base.loader.loadMusic(INTRO_MUSIC_PATH)
        if self.introMusic:
            self.introMusic.setLoop(True)
            self.introMusic.setVolume(1.0)
            self.introMusic.play()

    def _adjustChainsawNametag(self):
        suit = self.chainsaw
        try:
            suit.nametag3d.setPos(
                suit.nametag3d.getX() - 0.2,
                suit.nametag3d.getY() - 2.0,
                suit.nametag3d.getZ() - 1.5)
        except:
            pass

    def _resetChainsawNametag(self):
        suit = self.chainsaw
        try:
            suit.nametag3d.setPos(0, 0, suit.height + 1.0)
        except:
            pass

    def _startOverrideEffects(self):
        if not self.head:
            return
        self.head.setChainsawTexRoll()
        self.head.startIdleSfx()

    def _cleanupFakeSuit(self):
        fake = self.fakeSuit
        if not fake:
            return
        try:
            fake.cleanup()
        except:
            try:
                fake.removeNode()
            except:
                pass
        self.fakeSuit = None

    def build(self):
        print('[Chainsaw CTSC] Building original unchanged chainsawconsultant_intro.ctsc')
        self._prepareActors()
        try:
            cutsceneTrack = self._buildCutsceneWithProjectileCompat()
        except:
            self.cleanup(removeHead=True)
            raise

        return Sequence(
            Func(camera.wrtReparentTo, render),
            Func(self._startMusic),
            Parallel(
                cutsceneTrack,
                Sequence(
                    Func(self._adjustChainsawNametag),
                    Wait(41.085),
                    Func(self._resetChainsawNametag)),
                Sequence(
                    Wait(67.6),
                    Func(self._startOverrideEffects))),
            Func(self._cleanupFakeSuit))

    def stopMusic(self):
        if self.introMusic:
            try:
                self.introMusic.stop()
            except:
                pass

    def cleanup(self, removeHead=False):
        if self.cleanedUp:
            return
        self.cleanedUp = True
        self.stopMusic()
        self._cleanupFakeSuit()
        if self.chainsaw and getattr(self.chainsaw, 'prop', None):
            try:
                self.chainsaw.detachPropeller()
            except:
                pass

        if removeHead and self.head:
            try:
                self.head.stopIntroEffects()
            except:
                pass
            suit = self.chainsaw
            if suit:
                try:
                    self.head.cleanup()
                except:
                    try:
                        self.head.removeNode()
                    except:
                        pass
                suit.headParts = self.oldHeadParts or []
                suit.animatedHeadParts = self.oldAnimatedHeadParts or []
                suit.specialHead = self.oldSpecialHead
                if self.oldGetDialogueArray is not None:
                    suit.getDialogueArray = self.oldGetDialogueArray
                for oldHead in suit.headParts:
                    try:
                        oldHead.show()
                    except:
                        pass
            self.head = None
            self.boss._chainsawSpecialHead = None


def makeChainsawIntroduction(boss, delayDeletes):
    setup = ChainsawIntroSetup(boss, delayDeletes)
    boss._chainsawIntroSetup = setup
    return setup.build()
