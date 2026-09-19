from toontown.suit.heads.AnimatedSuitHead import *
from toontown.suit.SuitDNA import getSuitBodyType
from toontown.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


skelecogPrefix = 'phase_5/models/char/suit{0}_skeleton_skull-'
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
    ('death', 'death')
)


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='autocad')
class UniqueSkelecogAnimatedSuitHead(AnimatedSuitHead):
    """
    If any Cog has unique head geometry but uses normal skelecog animations, this head class
    can be used to prevent the need to copy paste animation files.
    """
    def getNormalAnimDict(self):
        return {anim[0]: skelecogPrefix.format(getSuitBodyType(self.suit.style.name).upper()) + anim[1] for anim in animsNormal}

    def createHead(self):
        self.loadAnims(self.getNormalAnimDict())
        self.reparentTo(self.suit.find('**/joint_head'))
        self.applyOffset()
        self.setTwoSided(True)
        self.loop('neutral')
        self.suit.headParts.append(self)
        self.suit.specialHead = self
