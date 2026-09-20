from toontown.clashsuit.suit.heads.AnimatedSuitHead import *
from direct.interval.IntervalGlobal import *

from toontown.clashsuit.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

filePrefix = 'phase_11/models/char/suits/ttcc_ene_rainmaker-'
anims = (
    ('neutral', 'neutral'),
    ('talk', 'murmur'),
    ('murmur', 'murmur'),
    ('grunt', 'grunt'),
    ('statement', 'statement'),
    ('question', 'question'),
    ('stun', 'stun'),
    ('neutral-lured', 'neutral-lured'),
    ('neutral-hurt', 'neutral-hurt')
)

animDict = {anim[0]: filePrefix + anim[1] for anim in anims}


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='rainmake')
class RainmakerAnimatedSuitHead(AnimatedSuitHead):
    # This is in the same order as it appears on the texture
    FOG = 4
    STORM = 3
    OIL = 2
    HEAVY = 1
    DEFAULT = 0

    def __init__(self, *args, **kwargs):
        AnimatedSuitHead.__init__(self, *args, **kwargs)
        self.hairState = self.DEFAULT
        self.hairTransition = None

    def createHead(self):
        self.loadAnims(animDict)
        self.reparentTo(self.suit.find('**/joint_head'))
        self.setZ(OffsetDict.get(self.suit.style.name, 0))
        self.setTwoSided(True)
        self.loop('neutral')
        self.suit.headParts.append(self)
        self.suit.specialHead = self

    def setHairState(self, state):
        if state != self.hairState:
            self.doHairTransition(self.hairState, state)
            self.hairState = state

    def doHairTransition(self, oldState, newState):

        if self.hairTransition:
            self.hairTransition.finish()

        self.textureStages = self.findAllTextureStages()
        self.hairStage = self.textureStages.findTextureStage('ttcc_ene_rainmaker_hair')

        def rollTexMatrix(t):
            try:
                self.setTexOffset(self.hairStage, 0, t)
            except AssertionError:
                pass

        oldV = oldState * 0.2
        newV = newState * 0.2

        self.hairTransition = LerpFunctionInterval(rollTexMatrix, fromData = oldV, toData = newV, duration = 6, blendType = 'easeInOut')
        self.hairTransition.start()

    def cleanup(self):
        self.ignoreAll()
        AnimatedSuitHead.cleanup(self)
