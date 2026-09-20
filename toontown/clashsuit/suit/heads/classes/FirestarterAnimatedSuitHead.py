from toontown.clashsuit.suit.heads.AnimatedSuitHead import *
from toontown.clashsuit.suit.heads.AnimatedSuitHeadRepository import AnimatedSuitHeadClass
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
@AnimatedSuitHeadClass(suitName='fires')
class FirestarterAnimatedSuitHead(AnimatedSuitHead):
    def __init__(self, *args, **kwargs):
        AnimatedSuitHead.__init__(self, *args, **kwargs)
        self.soaked = False
        self.accept('suitSoaked', self.handleSoaked)
        self.accept('suitUnsoaked', self.handleUnsoaked)
        self.fireSeqNode = self.find('**/fire_seq')

    def handleSoaked(self, suit):
        if not hasattr(self, 'suit'):
            return
        # Make sure the soaked suit is actually us.
        if self.suit is not suit:
            return

        if not self.soaked:
            self.soaked = True
            self.fireSeqNode.hide()

    def handleUnsoaked(self, suit):
        if not hasattr(self, 'suit'):
            return
        # Make sure the unsoaked suit is actually us.
        if self.suit is not suit:
            return

        if self.soaked:
            self.soaked = False
            self.fireSeqNode.show()

    def cleanup(self):
        self.ignoreAll()
        AnimatedSuitHead.cleanup(self)
