from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import *
from panda3d.physics import *
from direct.particles import Particles, ForceGroup


def chainsawBulbBreak(self):
    self.reset()
    self.setPos(0.000, 0.000, 2.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(256)
    p0.setBirthRate(0.0500)
    p0.setLitterSize(6)
    p0.setLitterSpread(1)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.1000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Point factory parameters
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHANONE)
    p0.renderer.setUserAlpha(1.00)
    # Sprite parameters
    p0.renderer.addTextureFromNode('phase_3.5/models/props/suit-particles', '**/roll-o-dex')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(0)
    p0.renderer.setYScaleFlag(0)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.0250)
    p0.renderer.setFinalXScale(0.0000)
    p0.renderer.setInitialYScale(0.0250)
    p0.renderer.setFinalYScale(0.0000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.5000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(-18.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Sphere Volume parameters
    p0.emitter.setRadius(0.1000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('gravity')
    # Force parameters
    force0 = LinearNoiseForce(10.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearJitterForce(55.0000, 0)
    force1.setVectorMasks(1, 1, 1)
    force1.setActive(1)
    f0.addForce(force1)
    self.addForceGroup(f0)



def chainsawGlassDrip(self):
    self.reset()
    self.setPos(0.000, 0.000, 2.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(256)
    p0.setBirthRate(0.0500)
    p0.setLitterSize(1)
    p0.setLitterSpread(1)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(0.9000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Point factory parameters
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sprite parameters
    p0.renderer.addTextureFromNode('phase_3.5/models/props/suit-particles', '**/roll-o-dex')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(0)
    p0.renderer.setYScaleFlag(0)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.0250)
    p0.renderer.setFinalXScale(0.0000)
    p0.renderer.setInitialYScale(0.0250)
    p0.renderer.setFinalYScale(0.0000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.5000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, -2.7500))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Sphere Volume parameters
    p0.emitter.setRadius(0.2000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('gravity')
    # Force parameters
    force0 = LinearNoiseForce(2.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearJitterForce(5.0000, 0)
    force1.setVectorMasks(1, 1, 1)
    force1.setActive(1)
    f0.addForce(force1)
    self.addForceGroup(f0)



def chainsawScabbardUp(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("ZSpinParticleFactory")
    p0.setRenderer("SparkleParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.0400)
    p0.setLitterSize(5)
    p0.setLitterSpread(1)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(0.5000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Z Spin factory parameters
    p0.factory.setInitialAngle(0.0000)
    p0.factory.setInitialAngleSpread(0.0000)
    p0.factory.enableAngularVelocity(1)
    p0.factory.setAngularVelocity(30.0000)
    p0.factory.setAngularVelocitySpread(0.0000)
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAINOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sparkle parameters
    p0.renderer.setCenterColor(Vec4(0.50, 1.00, 0.50, 1.00))
    p0.renderer.setEdgeColor(Vec4(0.00, 1.00, 0.00, 1.00))
    p0.renderer.setBirthRadius(0.1000)
    p0.renderer.setDeathRadius(0.3000)
    p0.renderer.setLifeScale(SparkleParticleRenderer.SPSCALE)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 7.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Sphere Volume parameters
    p0.emitter.setRadius(0.6500)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('gravity')
    # Force parameters
    force0 = LinearNoiseForce(7.5000, 0)
    force0.setVectorMasks(1, 1, 0)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearJitterForce(40.0000, 0)
    force1.setVectorMasks(1, 1, 1)
    force1.setActive(1)
    f0.addForce(force1)
    self.addForceGroup(f0)



def chainsawSparkPlugFinger(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(6.000, 6.000, 6.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("ZSpinParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(500)
    p0.setBirthRate(0.0450)
    p0.setLitterSize(1)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.1000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Z Spin factory parameters
    p0.factory.setInitialAngle(0.0000)
    p0.factory.setInitialAngleSpread(0.0000)
    p0.factory.enableAngularVelocity(0)
    p0.factory.setFinalAngle(360.0000)
    p0.factory.setFinalAngleSpread(90.0000)
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sprite parameters
    p0.renderer.addTextureFromFile('phase_6/maps/acorn_acres/chainsawconsultant/ttcc_env_cc_lightning.png')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(1)
    p0.renderer.setInitialXScale(0.2000)
    p0.renderer.setFinalXScale(0.6000)
    p0.renderer.setInitialYScale(0.2000)
    p0.renderer.setFinalYScale(0.6000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.5000)
    p0.emitter.setAmplitudeSpread(0.5000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, -1.5000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Sphere Volume parameters
    p0.emitter.setRadius(0.0100)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('forces')
    # Force parameters
    force0 = LinearJitterForce(80.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearNoiseForce(2.0000, 0)
    force1.setVectorMasks(1, 1, 1)
    force1.setActive(1)
    f0.addForce(force1)
    self.addForceGroup(f0)



def chainsawSparkPlugAcross(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SparkleParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.0500)
    p0.setLitterSize(1)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(0.5000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Point factory parameters
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sparkle parameters
    p0.renderer.setCenterColor(Vec4(1.00, 1.00, 0.00, 1.00))
    p0.renderer.setEdgeColor(Vec4(1.00, 0.62, 0.17, 1.00))
    p0.renderer.setBirthRadius(0.1000)
    p0.renderer.setDeathRadius(0.1000)
    p0.renderer.setLifeScale(SparkleParticleRenderer.SPNOSCALE)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.5000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(-1.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Sphere Volume parameters
    p0.emitter.setRadius(0.0100)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('gravity')
    # Force parameters
    force0 = LinearNoiseForce(1.2000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearJitterForce(12.0000, 0)
    force1.setVectorMasks(1, 1, 1)
    force1.setActive(1)
    f0.addForce(force1)
    self.addForceGroup(f0)



PARTICLE_FACTORIES = {
    'chainsawBulbBreak': chainsawBulbBreak,
    'chainsawGlassDrip': chainsawGlassDrip,
    'chainsawScabbardUp': chainsawScabbardUp,
    'chainsawSparkPlugFinger': chainsawSparkPlugFinger,
    'chainsawSparkPlugAcross': chainsawSparkPlugAcross,
}


def getChainsawParticle(name):
    factory = PARTICLE_FACTORIES.get(name)
    if factory is None:
        raise KeyError('Unknown Chainsaw cutscene particle: %s' % name)
    effect = ParticleEffect()
    factory(effect)
    return effect


def getChainsawParticles(names):
    return [getChainsawParticle(name) for name in names]
