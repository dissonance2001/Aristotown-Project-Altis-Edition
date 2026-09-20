from toontown.clashsuit.suit.heads.AnimatedSuitHead import *
from toontown.clashsuit.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


filePrefix = 'phase_11/models/char/suits/ttcc_ene_litigator-'
animsNormal = (
    ('bellow', 'bellow'),
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
    ('bellow', 'bellow'),
    ('gsnap', 'gsnap')
)
# -nf is No Flame variant, used when soaked.
animsSoak = (
    ('neutral', 'neutral-nf'),
    ('talk', 'murmur-nf'),
    ('murmur', 'murmur-nf'),
    ('grunt', 'grunt-nf'),
    ('statement', 'statement-nf'),
    ('question', 'question-nf'),
    ('stun', 'stun-nf'),
    ('neutral-lured', 'neutral-lured-nf'),
    ('neutral-hurt', 'neutral-hurt-nf'),
    ('death', 'death-nf'),
    ('bellow', 'bellow-nf'),
    ('gsnap', 'gsnap-nf')
)
normalAnimDict = {anim[0]: filePrefix + anim[1] for anim in animsNormal}
soakAnimDict = {anim[0]: filePrefix + anim[1] for anim in animsSoak}


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='lgator')
class LitigatorAnimatedSuitHead(AnimatedSuitHead):
    def __init__(self, *args, **kwargs):
        AnimatedSuitHead.__init__(self, *args, **kwargs)
        self.soaked = False
        self.accept('suitSoaked', self.handleSoaked)
        self.accept('suitUnsoaked', self.handleUnsoaked)

    def createHead(self):
        self.loadAnims(normalAnimDict)
        self.reparentTo(self.suit.find('**/joint_head'))
        self.applyOffset()
        self.setTwoSided(True)
        self.loop('neutral')
        self.suit.headParts.append(self)
        self.suit.specialHead = self

    def handleSoaked(self, suit):
        if not hasattr(self, 'suit'):
            return
        # Make sure the soaked suit is actually us.
        if self.suit is not suit:
            return

        if not self.soaked:
            self.soaked = True
            self.loadAnims(soakAnimDict)

    def handleUnsoaked(self, suit):
        if not hasattr(self, 'suit'):
            return
        # Make sure the unsoaked suit is actually us.
        if self.suit is not suit:
            return

        if self.soaked:
            self.soaked = False
            self.loadAnims(normalAnimDict)

    def cleanup(self):
        self.ignoreAll()
        AnimatedSuitHead.cleanup(self)
