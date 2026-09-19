import random

from direct.interval.IntervalGlobal import *
from panda3d.core import *
from enum import Enum, auto

from toontown.suit.heads.AnimatedSuitHead import *
from toontown.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass

textureFile = 'phase_12/maps/ttcc_ene_chainsaw'

filePrefix = 'phase_12/models/char/suits/ttcc_ene_chainsaw'
animsNormal = (
    ('neutral', '-neutral'),
    ('talk', '-murmur'),
    ('murmur', '-murmur'),
    ('grunt', '-grunt'),
    ('statement', '-statement'),
    ('question', '-question'),
    ('stun', '-stun'),
    ('neutral-lured', '-neutral-lured'),
    ('neutral-hurt', '-neutral-hurt'),
    ('death', '-death'),
    ('leap', '-cutscene-leap'),
    ('getup', '-cutscene-getup'),
    ('hurt-neutral', '-cutscene-hurt-neutral'),
    ('hurt-walk', '-cutscene-hurt-walk'),
    ('laying', '-cutscene-laying'),
    ('todesk', '-cutscene-todesk'),
    ('desk-neutral', '-cutscene-desk-neutral'),
    ('revvedup', '-revvedup'),
    ('sparkplug', '-sparkplug'),
    ('scabbard', '-scabbard'),
    ('throttle', '-throttle'),
    ('throttle2', '-throttle2'),
)
# _b is override variant, used when he is red and stuff
animsGlitch = (
    ('neutral', '_b-neutral'),
    ('talk', '_b-murmur'),
    ('murmur', '_b-murmur'),
    ('grunt', '_b-grunt'),
    ('statement', '_b-statement'),
    ('question', '_b-question'),
    ('stun', '_b-stun'),
    ('neutral-lured', '_b-neutral-lured'),
    ('neutral-hurt', '_b-neutral-hurt'),
    ('death', '_b-death'),
    ('leap', '-cutscene-leap'),
    ('getup', '-cutscene-getup'),
    ('hurt-neutral', '-cutscene-hurt-neutral'),
    ('hurt-walk', '-cutscene-hurt-walk'),
    ('laying', '-cutscene-laying'),
    ('todesk', '-cutscene-todesk'),
    ('desk-neutral', '-cutscene-desk-neutral'),
    ('revvedup', '-revvedup'),
    ('sparkplug', '-sparkplug'),
    ('scabbard', '-scabbard'),
    ('throttle', '-throttle'),
    ('throttle2', '-throttle2'),
)
normalAnimDict = {anim[0]: filePrefix + anim[1] for anim in animsNormal}
glitchAnimDict = {anim[0]: filePrefix + anim[1] for anim in animsGlitch}

soundPathFilePrefix = 'phase_12/audio/dial/ttcc_ene_chainsaw'

soundPaths = {
    'normal': {
        'grunt': f'{soundPathFilePrefix}_grunt',
        'murmur': f'{soundPathFilePrefix}_murmur',
        'statement': f'{soundPathFilePrefix}_statement',
        'question': f'{soundPathFilePrefix}_question',
    },
    'glitch': {
        'grunt': f'{soundPathFilePrefix}_grunt_or',
        'murmur': f'{soundPathFilePrefix}_murmur_or',
        'statement': f'{soundPathFilePrefix}_statement_or',
        'question': f'{soundPathFilePrefix}_question_or',
    }
}

FreakoutTaskName = 'ChainsawAnimatedSuitHead-NeutralFreakoutTask'
WaitRange = (0.4, 2.0)
RepeatTwitchTimes = [1, 2, 3]
RepeatTwitchWeights = [6, 9, 7]
AngleRange = [10, 25]
TwitchTimeRange = (0.07, 0.12)


class GlitchState(Enum):
    Normal = auto()
    Glitch = auto()
    SemiGlitch = auto()


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='chainsaw')
class ChainsawAnimatedSuitHead(AnimatedSuitHead):
    def __init__(self, *args, **kwargs):
        AnimatedSuitHead.__init__(self, *args, **kwargs)
        self.idleSfx = None
        self.sfxInterval = None
        self.texRollIval = None
        self.freakoutSeq = None
        self.glitchState = GlitchState.Normal
        self.normalTex = None
        self.glitchTex = None
        # Load normal and glitch textures and store them so that we may use them for the semi glitch state
        self.normalTex = self.getModeTexture(glitch=False)
        self.prepareTexture(self.normalTex)
        self.glitchTex = self.getModeTexture(glitch=True)
        self.prepareTexture(self.glitchTex)

    def createHead(self):
        self.loadAnims(normalAnimDict)
        self.reparentTo(self.suit.find('**/joint_head'))
        self.applyOffset()
        self.setTwoSided(True)
        self.loop('neutral')
        self.suit.headParts.append(self)
        self.hat = self.find('**/Hat')
        self.bulbRight = self.find('**/bulbRight')
        self.bulbLeft = self.find('**/bulbLeft')
        self.setScale(0.98)
        self.setZ(0.03)
        self.suit.specialHead = self
        self.texRollIval = None
        self.inGlitch = False
        self.updateSuitVoice(glitch=False)

    def startIdleSfx(self, task=None):
        if not hasattr(self, 'suit'):
            return
        if self.isEmpty():
            return
        if hasattr(self, "Actor_deleted"):
            return

        if self.sfxInterval:
            self.sfxInterval.finish()
        idleSfx = loader.loadSfx('phase_12/audio/dial/ttcc_ene_chainsaw_idle.ogg')
        self.sfxInterval = SoundInterval(idleSfx, node=base.localAvatar, listenerNode=base.localAvatar, seamlessLoop=1, volume=0.5)
        self.sfxInterval.loop()

    def setChainsawTexRoll(self, duration=1.6):
        # Can also be called in cutscene to make the chainsaw roll faster or slower.
        if self.texRollIval:
            self.texRollIval.pause()
        if duration <= 0:
            self.texRollIval = None
            return

        self.texRollIval = self.chainsawMoveInterval(self.find('**/Chain'), duration=duration)
        self.texRollIval.loop()

    @staticmethod
    def chainsawMoveInterval(obj, duration=2.0):
        def rollTexMatrix(t, obj=obj):
            obj.setTexOffset(TextureStage.getDefault(), t, 0)

        return LerpFunctionInterval(rollTexMatrix, fromData=1, toData=0, duration=duration)

    def updateSuitVoice(self, glitch=False):
        if not hasattr(self, 'suit'):
            return
        if not hasattr(self.suit, 'voice'):
            return

        # Load all of the required VOs based on what mode they're in
        fileExtension = '.ogg'
        soundPathBank = soundPaths['glitch' if glitch else 'normal']
        grunt = loader.loadSfx(f"{soundPathBank['grunt']}{fileExtension}")
        murmur = loader.loadSfx(f"{soundPathBank['murmur']}{fileExtension}")
        statement = loader.loadSfx(f"{soundPathBank['statement']}{fileExtension}")
        question = loader.loadSfx(f"{soundPathBank['question']}{fileExtension}")
        sfxArray = (grunt, murmur, statement, question, grunt, murmur, statement)

        # Replace the sfx array on the cog now that we have all of them
        self.suit.voice.voiceArray = sfxArray

    @staticmethod
    def prepareTexture(tex):
        tex.setWrapU(Texture.WM_repeat)
        tex.setWrapV(Texture.WM_repeat)
        tex.setMinfilter(Texture.FTLinearMipmapLinear)
        tex.setMagfilter(Texture.FTLinear)
        return tex

    @staticmethod
    def getModeTexture(glitch=False):
        return loader.loadTexture(f'{textureFile}{"_b" if glitch else ""}.png')

    def enterGlitch(self, temp=None):
        if not hasattr(self, 'suit'):
            return
        self.__stopFreakout()
        self.setTexture(self.glitchTex, 1)
        self.loadAnims(glitchAnimDict)
        self.updateSuitVoice(glitch=True)
        self.glitchState = GlitchState.Glitch
        self.setHurtMode(False)

    def enterSemiGlitch(self, temp=None):
        # This state will have him twitching between normal and override
        if not hasattr(self, 'suit'):
            return
        self.setTexture(self.normalTex, 1)
        self.loadAnims(normalAnimDict)
        self.updateSuitVoice(glitch=False)
        self.glitchState = GlitchState.SemiGlitch
        self.__startFreakout()
        self.setHurtMode(True)

    def uniqueName(self, str):
        if getattr(self, 'suit', None) and getattr(self.suit, 'doId', None):
            return f'{self.suit.doId}-{str}'

        return f'{id(self)}-{str}'

    def __startFreakout(self):
        self.__endOldFreakout()

        self.doMethodLater(0, self.__newFreakout, name=self.uniqueName(FreakoutTaskName))

    def __stopFreakout(self):
        self.__endOldFreakout()

    def __endOldFreakout(self):
        self.removeTask(self.uniqueName(FreakoutTaskName))
        self.__finishFreakoutSeq()

    def __finishFreakoutSeq(self):
        if self.freakoutSeq:
            self.freakoutSeq.finish()
            self.freakoutSeq = None

    def __newFreakout(self, task=None):
        self.__finishFreakoutSeq()
        if not getattr(self, 'suit', None):
            self.__endOldFreakout()
            return

        waitForNextTime = lerp(WaitRange[0], WaitRange[1], random.random())
        twitchRepeatAmt = random.choices(RepeatTwitchTimes, weights=RepeatTwitchWeights)[0]

        self.freakoutSeq = Sequence()
        for i in range(twitchRepeatAmt):
            lastTwitch = i == twitchRepeatAmt - 1
            twitchTime = lerp(TwitchTimeRange[0], TwitchTimeRange[1], random.random())
            isH = random.random() < 0.5
            angleRange = AngleRange if isH else (AngleRange[0] * 2/3, AngleRange[1] * 2/3)
            ourAngle = lerp(angleRange[0], angleRange[1], random.random())
            multiplier = random.choice([-1, 1])
            finalHpr = (ourAngle*multiplier, 0, 0) if isH else (0, 0, ourAngle*multiplier)
            self.freakoutSeq.append(Sequence(
                Func(self.setTexture, self.glitchTex, 1),
                self.hprInterval(twitchTime, finalHpr, startHpr=(0, 0, 0)),
            ))
            if lastTwitch:
                self.freakoutSeq.append(Func(self.setTexture, self.normalTex, 1))
                self.freakoutSeq.append(self.hprInterval(twitchTime * 2, (0, 0, 0), blendType='easeOut'))

        self.freakoutSeq.start()

        task.delayTime = waitForNextTime + self.freakoutSeq.getDuration()
        return task.again

    def exitGlitch(self, temp=None):
        if not hasattr(self, 'suit'):
            return
        self.__stopFreakout()
        self.setTexture(self.normalTex, 1)
        self.loadAnims(normalAnimDict)
        self.updateSuitVoice(glitch=False)
        self.glitchState = GlitchState.Normal
        self.setHurtMode(False)

    def cleanup(self):
        if self.sfxInterval:
            self.sfxInterval.pause()
            self.sfxInterval = None
        if self.texRollIval:
            self.texRollIval.pause()
            self.texRollIval = None
        self.hat = None
        self.bulbLeft = None
        self.bulbRight = None
        self.normalTex = None
        self.glitchTex = None
        self.__stopFreakout()
        super().cleanup()

    def modifyZapHeadActor(self, headGeom):
        """
        Used to modify the geom of zap head actors if necessary, if they use this special head class.
        """
        hideNodes = ('Hat',)
        for nodeName in hideNodes:
            node = headGeom.find(f'**/{nodeName}')
            if node and not node.isEmpty():
                node.hide()

        # Set the texture based on what mode we're in
        tex = self.getModeTexture(glitch=self.glitchState == GlitchState.Glitch)
        self.prepareTexture(tex)
        headGeom.setTexture(tex, 1)
