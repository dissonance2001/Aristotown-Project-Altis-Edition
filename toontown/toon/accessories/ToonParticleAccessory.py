from .ToonAccessory import ToonAccessory
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.battle import BattleParticles


@DirectNotifyCategory()
class ToonParticleAccessory(ToonAccessory):
    # May be the name of a particle, or a list of names of particles.
    ParticleName = None
    ParticleNodePos = (0, 0, 0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.particleSystems = []
        self.particleNode = None

    def load(self):
        super().load()

        def startParticles():
            if not self.accessoryGeom.isHidden():
                self.startParticles()

        # Particles will begin once the accessory has fully async loaded
        self.async_addLoadCallback(startParticles)

    def unload(self):
        super().unload()
        if self.particleNode:
            self.particleNode.removeNode()
            self.particleNode = None
        self.particleSystems = []

    def stop(self):
        for system in self.particleSystems:
            system.cleanup()

    @property
    def renderParent(self):
        # Only use render on distributed toons, otherwise this stuff will start showing
        # in render space from the UI which is no bueno
        return render if self.toonIsReal else self.accessoryNodes[0]

    def setupParticleNode(self):
        self.particleNode = self.accessoryNodes[0].attachNewNode('accessoryParticleNode')
        self.particleNode.setPos(self.ParticleNodePos)

    def startParticles(self):
        self.setupParticleNode()

        # None means no particle systems
        if self.ParticleName is None:
            return
        # Do not touch the particles if this toon is not a real toon.
        # It looks really really really bad.
        if not self.toonIsReal:
            return

        # Make sure its in a tuple/list to allow for multiple particle systems per accessory
        if type(self.ParticleName) not in (list, tuple):
            self.ParticleName = [self.ParticleName]

        BattleParticles.loadParticles()
        # Load each particle defined and add it to the list
        for particleName in self.ParticleName:
            system = BattleParticles.loadParticleFile(f'{particleName}.ptf')
            system.start(parent=self.particleNode, renderParent=self.renderParent)
            self.particleSystems.append(system)
