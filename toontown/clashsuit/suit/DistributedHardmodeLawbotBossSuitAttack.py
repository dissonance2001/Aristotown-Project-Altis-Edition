from direct.interval.FunctionInterval import Wait, Func
from direct.interval.MetaInterval import Sequence, Parallel
from direct.interval.ParticleInterval import ParticleInterval
from panda3d.core import VBase4, Vec4, CollisionTube, CollisionNode, NodePath

from toontown.suit import BossCogGlobals
from toontown.toonbase import ToontownGlobals
from toontown.battle import BattleParticles
from toontown.suit.DistributedHardmodeLawbotBossSuit import DistributedHardmodeLawbotBossSuit
from toontown.toonbase import ToontownGlobals


class DistributedHardmodeLawbotBossSuitAttack(DistributedHardmodeLawbotBossSuit):
    def __init__(self, cr):
        DistributedHardmodeLawbotBossSuit.__init__(self, cr)
        self.target = None
        self.sequence = None
        self.isInDocketCollision = False
        self.particlesRunning = False
        self.damageDealt = False
        self.particle = None
        self.particleRender = None
        self.paperSfx = loader.loadSfx('phase_11/audio/sfx/LB_boss_paper_spin.ogg')

    def announceGenerate(self):
        """
        Handle all required fields having been filled in.
        """
        DistributedHardmodeLawbotBossSuit.announceGenerate(self)
        self.nametag3d.setColorScale(VBase4(0.9, 0.1, 0.1, 1))  # red nametag
        self.accept(self.uniqueName('enterDocketCSphereNode'), self.handleDocketCollisionEnter)
        self.accept(self.uniqueName('exitDocketCSphereNode'), self.handleDocketCollisionExit)

    def delete(self):
        DistributedHardmodeLawbotBossSuit.delete(self)
        self.ignoreAll()
        taskMgr.remove(self.uniqueName('doDocketDamageTask'))
        taskMgr.remove(self.uniqueName('docketCleanup'))
        taskMgr.remove(self.uniqueName('stopParticleSpawn'))
        taskMgr.remove(self.uniqueName('docketCleanupParticles'))
        self.removeDocketParticles(finish=True)
        self.removeTarget()
        del self.sequence
        del self.target
        del self.paperSfx

    def handleDocketCollisionEnter(self, _):
        self.isInDocketCollision = True
        if self.particlesRunning and not base.localAvatar.isStunned:
            self.damageDealt = True
            self.boss.zapLocalToon(BossCogGlobals.BossCogDocketAoeAttack)

    def handleDocketCollisionExit(self, _):
        self.isInDocketCollision = False

    def beginDocket(self):
        if self.target:
            #  We should forcibly clean up the previous one instead of just returning, this is like
            #  this because the client lagged a significant amount and for sync purposes we should just
            #  remove the old one first, then continue with the brand new one received here.
            #  This is now what we do.
            self.removeDocketParticles(finish=True)
            self.removeTarget()
            taskMgr.remove(self.uniqueName('doDocketDamageTask'))
            taskMgr.remove(self.uniqueName('docketCleanup'))
            taskMgr.remove(self.uniqueName('stopParticleSpawn'))
            taskMgr.remove(self.uniqueName('docketCleanupParticles'))

        self.isInDocketCollision = False
        self.damageDealt = False
        self.particlesRunning = False

        self.target = NodePath('targetNodePath')
        target = loader.loadModel('phase_11/models/lawbotHQ/clo_hm_attack_indicator')
        self.sequence = Sequence(target.colorScaleInterval(0.3, Vec4(1, 1, 1, 1), Vec4(1, 1, 1, 0)), Wait(0.5),
                                 target.colorScaleInterval(0.3, Vec4(1, 1, 1, 0)))
        self.sequence.loop()
        pos = self.getPos()
        pos.setZ(-71.575)
        target.setScale(25)
        target.reparentTo(self.target)
        target.setHpr(0, -90, 0)
        self.target.setPos(pos)
        cSphere = CollisionTube(0.0, 0.0, -1.0, 0.0, 0.0, 50, 12.1875)
        cSphere.setTangible(0)
        cSphereNode = CollisionNode(self.uniqueName('DocketCSphereNode'))
        cSphereNode.addSolid(cSphere)
        cSphereNode.setCollideMask(ToontownGlobals.WallBitmask)

        self.target.attachNewNode(cSphereNode)
        self.target.reparentTo(render)
        taskMgr.doMethodLater(BossCogGlobals.HardmodeLawbotBossDocketDelay + 0.9, self.doDocketDamage,
                              self.uniqueName('doDocketDamageTask'))
        taskMgr.doMethodLater(BossCogGlobals.HardmodeLawbotBossDocketDelay, self.addDocketParticles,
                              self.uniqueName('doDocketDamageTask'))

    def doDocketDamage(self, _):
        if self.isInDocketCollision and not self.damageDealt:
            self.damageDealt = True
            self.boss.zapLocalToon(BossCogGlobals.BossCogDocketAoeAttack)
        self.addDocketParticles()
        taskMgr.doMethodLater(1.9, self.removeTarget, self.uniqueName('docketCleanup'))

    def removeTarget(self, _=None):
        if self.target and not self.target.isEmpty():
            self.target.removeNode()
            self.target = None
        if self.sequence:
            self.sequence.finish()
            self.sequence = None

    def addDocketParticles(self, _=None):
        if not self.particle:
            particle = BattleParticles.loadParticleFile('paperRainDocketCLO.ptf')
            particle.setPos(0, 0, 18)
            particle.setScale(0.1875)
            self.particleRender = self.target.attachNewNode('particleRender')
            self.particleRender.setDepthWrite(0)
            self.particleRender.setBin('fixed', 1)
            self.particle = Parallel(
                Sequence(
                    ParticleInterval(particle, self.particleRender, worldRelative=False, duration=2.8, cleanup=True),
                    Func(self.removeDocketParticles),
                ),
                Sequence(
                    Wait(0.9),
                    Func(self._enableReenterDamage),
                    Wait(1.6),
                    Func(self._disableReenterDamage),
                )
            )
            self.particle.start()
            base.playSfx(self.paperSfx, looping=1, node=self)

    def _enableReenterDamage(self):
        self.particlesRunning = True

    def _disableReenterDamage(self):
        self.particlesRunning = False
        self.paperSfx.stop()

    def removeDocketParticles(self, _=None, finish=False):
        if self.particle:
            if finish:
                self.particle.finish()
            self.particle = None
        if self.particleRender:
            self.particleRender.removeNode()
            self.particleRender = None
