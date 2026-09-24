from panda3d.core import *
from direct.interval.IntervalGlobal import *


# region Instance Mercs
class PrethinkerBrainstormCloud(NodePath):
    ParticleDelay = 0.15

    def __init__(self, battle, isEditor=False):
        NodePath.__init__(self, 'PrethinkerBrainstormCloud')

        from toontown.clashbattle.battle.BattleProps import globalPropPool
        from toontown.clashbattle.battle import BattleParticles
        self.reparentTo(battle)
        self.geom = globalPropPool.getProp('stormcloud')
        self.geom.setScale(0.01)
        self.geom.reparentTo(self)
        self.geom.hide()
        BattleParticles.loadParticles()
        self.snowEffects = [BattleParticles.createParticleEffect(file="prethinkerForwardThinkingBrainStorm") for _ in range(3)]
        effectColor = Vec4(0.65, 0.79, 0.93, 0.85)
        BattleParticles.setEffectTexture(
            self.snowEffects[0], "brainstorm-box", color=effectColor
        )
        BattleParticles.setEffectTexture(
            self.snowEffects[1], "brainstorm-env", color=effectColor
        )
        BattleParticles.setEffectTexture(
            self.snowEffects[2], "brainstorm-track", color=effectColor
        )
        self.isEditor = isEditor
        self.seq = self.getSeq()

    def startParticles(self):
        if not self.snowEffects:
            return

        for effect in self.snowEffects:
            effect.start(parent=self.geom, renderParent=render)

    def stopParticles(self):
        [snowEffect.cleanup() for snowEffect in self.snowEffects]
        self.snowEffects = []

    def getSeq(self):
        return Sequence(
            Func(self.geom.pose, "stormcloud", 0),
            Func(self.geom.show),
            LerpScaleInterval(self.geom, 0.7, scale=4, blendType='easeIn'),
            Wait(self.ParticleDelay),
            Parallel(
                ParticleInterval(
                    self.snowEffects[0], self.geom, worldRelative=0, duration=8.5, cleanup=False,
                ),
                Sequence(
                    Wait(0.5),
                    ParticleInterval(
                        self.snowEffects[1], self.geom, worldRelative=0, duration=8.5, cleanup=False,
                    ),
                ),
                Sequence(
                    Wait(1.0),
                    ParticleInterval(
                        self.snowEffects[2], self.geom, worldRelative=0, duration=8.5, cleanup=False,
                    ),
                ),
                Sequence(
                    ActorInterval(self.geom, "stormcloud", startTime=3, duration=0.5),
                    ActorInterval(self.geom, "stormcloud", startTime=2.5, duration=0.5),
                    ActorInterval(self.geom, "stormcloud", startTime=1, duration=8.5),
                ),
            ),
        )

    def runSeq(self):
        return self.seq

    def cleanup(self):
        # Don't clean up if we're in the editor
        if self.isEditor:
            return

        if self.seq:
            self.seq.finish()
            self.seq = None
        self.stopParticles()
        self.geom.cleanup()
        self.geom = None
# endregion
