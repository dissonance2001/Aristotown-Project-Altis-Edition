from toontown.suit.heads.AnimatedSuitHead import *
from toontown.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

filePrefix = 'phase_14/models/char/suits/ttcc_ene_chairman-'
animsNormal = (
    ('neutral', 'neutral'),
    ('talk', 'murmur'),
    ('murmur', 'murmur'),
    ('grunt', 'grunt'),
    ('statement', 'statement'),
    ('question', 'question'),
    ('stun', 'stun'),
    ('neutral-lured', 'neutral-lured'),
    ('neutral-hurt', 'neutral-hurt'),
    ('death', 'death'),
    ('mouth-drop', 'mouthdrop')
)
# -a is an Angry variant
animsAngry = (
    ('neutral', 'neutral-a'),
    ('talk', 'murmur-a'),
    ('murmur', 'murmur-a'),
    ('grunt', 'grunt-a'),
    ('statement', 'statement-a'),
    ('question', 'question-a')
)
normalAnimDict = {anim[0]: filePrefix + anim[1] for anim in animsNormal}
angryAnimDict = normalAnimDict.copy()
for anim in animsAngry:
    angryAnimDict[anim[0]] = filePrefix + anim[1]


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='chairman')
class ChairmanAnimatedSuitHead(AnimatedSuitHead):
    def __init__(self, *args, **kwargs):
        AnimatedSuitHead.__init__(self, *args, **kwargs)
        self.angry = False

    def createHead(self):
        self.loadAnims(normalAnimDict)
        self.reparentTo(self.suit.find('**/joint_head'))
        self.setZ(OffsetDict.get(self.suit.style.name, 0))
        self.setTwoSided(True)
        self.loop('neutral')
        self.suit.headParts.append(self)
        self.suit.specialHead = self

    def setAngry(self, angry):
        self.angry = angry
        self.loadAnims(angryAnimDict if angry else normalAnimDict)
        self.loop('neutral')
