from direct.actor import Actor
from direct.fsm.FSM import FSM, RequestDenied
from direct.interval.IntervalGlobal import Func, Sequence


class SnowmanSteve:
    def __init__(self, geom):
        self.snowmanBody = Actor.Actor(
            models='phase_8/models/props/snowman_steve',
            anims={
                'neutral': 'phase_8/models/char/cc_a_chr_npc_snowman_1-neutral',
                'observe': 'phase_8/models/char/cc_a_chr_npc_snowman_1-observe',
                'approach': 'phase_8/models/char/cc_a_chr_npc_snowman_1-approach',
                'talk': 'phase_8/models/char/cc_a_chr_npc_snowman_1-talk'
            },
            copy=0
        )
        self.snowmanBody.reparentTo(geom)
        self.snowmanBody.setH(-45 + 215)
        self.snowmanBody.setScale(1.25)
        self.snowmanBody.setBlend(frameBlend=base.wantSmoothAnims)
        self.snowmanFSM = SnowmanFSM(self.snowmanBody)

    def cleanup(self):
        if self.snowmanBody:
            self.snowmanBody.cleanup()
            self.snowmanBody.removeNode()
        if self.snowmanFSM:
            self.snowmanFSM.cleanup()


class SnowmanFSM(FSM):
    def __init__(self, snowman: Actor):
        FSM.__init__(self, self.__class__.__name__)
        self.defaultTransitions = {
            'Neutral': ['Observe', 'Approach', 'Talk'],
            'Observe': ['Neutral'],
            'Approach': ['Neutral', 'Talk'],
            'Talk': ['Neutral']
        }
        self.snowman = snowman

    def defaultFilter(self, request, args):
        try:
            super().defaultFilter(request, args)
            return super().defaultFilter(request, args)
        except RequestDenied as rd:
            self.notify.warning(f'Safe FSM ignored: {rd}')
            self.notify.warning(f'Safe FSM {self.__class__.__name__} ignored: {rd}')
            return None

    def cleanup(self):
        super().cleanup()
        del self.snowman

    def enterNeutral(self):
        if not hasattr(self, 'snowman'):
            return

        self.snowman.loop('neutral')

    def exitNeutral(self):
        if not hasattr(self, 'snowman'):
            return

        self.snowman.stop()

    def enterObserve(self):
        Sequence(
            self.snowman.actorInterval('observe'),
            Func(lambda: self.request('neutral'))
        ).start()

    def exitObserve(self):
        pass

    def enterApproach(self):
        Sequence(
            self.snowman.actorInterval('approach'),
            Func(lambda: self.request('neutral'))
        ).start()

    def exitApproach(self):
        pass

    def enterTalk(self):
        Sequence(
            self.snowman.actorInterval('talk'),
            Func(lambda: self.request('neutral'))
        ).start()

    def exitTalk(self):
        pass
