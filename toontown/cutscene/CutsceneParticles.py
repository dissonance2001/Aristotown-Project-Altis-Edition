"""
A module containing a reference to all cutscene particles.
"""
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import *
from panda3d.physics import *
from direct.particles import Particles, ForceGroup

CutsceneParticleTable = {}


def getCutsceneParticleSystem(name):
    effect = ParticleEffect()
    CutsceneParticleTable[name](effect)
    return effect


def getCutsceneParticleSystems(namelist: list):
    return [getCutsceneParticleSystem(name) for name in namelist]


def csparticle(func):
    CutsceneParticleTable[func.__name__] = func


@csparticle
def fireball(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-2')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.1000)
    p0.setLitterSize(3)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.0000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Point factory parameters
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAINOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sprite parameters
    p0.renderer.addTextureFromFile('phase_6/maps/tt_t_efx_ext_smoke.png')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.6000)
    p0.renderer.setFinalXScale(0.3000)
    p0.renderer.setInitialYScale(0.6000)
    p0.renderer.setFinalYScale(0.7000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    p0.renderer.getColorInterpolationManager().addLinear(0.0, 1.0, Vec4(1.0, 0.0, 0.0, 1.0), Vec4(1.0, 1.0, 0.0, 1.0),
                                                         True)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Sphere Volume parameters
    p0.emitter.setRadius(0.1000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('source')
    # Force parameters
    force0 = LinearSourceForce(Point3(0.0000, 0.0000, -4.0000), LinearDistanceForce.FTONEOVERRSQUARED, 1.0000, 1.0000,
                               1)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def jellybeanRainFall(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("GeomParticleRenderer")
    p0.setEmitter("RingEmitter")
    p0.setPoolSize(2000)
    p0.setBirthRate(0.2500)
    p0.setLitterSize(1)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.0000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Point factory parameters
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHANONE)
    p0.renderer.setUserAlpha(1.00)
    # Geom parameters
    # geomRef = loader.loadModel("phase_4/models/props/jellybean4")
    # p0.renderer.setGeomNode(geomRef.node())
    p0.geomReference = ""
    p0.renderer.setXScaleFlag(0)
    p0.renderer.setYScaleFlag(0)
    p0.renderer.setZScaleFlag(0)
    p0.renderer.setInitialXScale(1.0000)
    p0.renderer.setFinalXScale(1.0000)
    p0.renderer.setInitialYScale(1.0000)
    p0.renderer.setFinalYScale(1.0000)
    p0.renderer.setInitialZScale(1.0000)
    p0.renderer.setFinalZScale(1.0000)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(1.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Ring parameters
    p0.emitter.setRadius(1.0000)
    p0.emitter.setRadiusSpread(0.0000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('forces')
    # Force parameters
    force0 = LinearSinkForce(Point3(0.0000, 0.0000, -79.0000), LinearDistanceForce.FTONEOVERRSQUARED, 15.9701, 95.0000,
                             1)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def jellybeanRainLand(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("GeomParticleRenderer")
    p0.setEmitter("RingEmitter")
    p0.setPoolSize(2000)
    p0.setBirthRate(0.2500)
    p0.setLitterSize(1)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.0000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Point factory parameters
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAOUT)
    p0.renderer.setUserAlpha(1.00)
    # Geom parameters
    # geomRef = loader.loadModel("phase_4/models/props/jellybean4")
    # p0.renderer.setGeomNode(geomRef.node())
    p0.geomReference = ""
    p0.renderer.setXScaleFlag(0)
    p0.renderer.setYScaleFlag(0)
    p0.renderer.setZScaleFlag(0)
    p0.renderer.setInitialXScale(1.0000)
    p0.renderer.setFinalXScale(1.0000)
    p0.renderer.setInitialYScale(1.0000)
    p0.renderer.setFinalYScale(1.0000)
    p0.renderer.setInitialZScale(1.0000)
    p0.renderer.setFinalZScale(1.0000)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 2.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(1.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Ring parameters
    p0.emitter.setRadius(1.0000)
    p0.emitter.setRadiusSpread(0.0000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('forces')
    # Force parameters
    force0 = LinearVectorForce(Vec3(0.0000, 0.0000, -5.0000), 1.0000, 0)
    force0.setVectorMasks(0, 0, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def trialByFire(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(500)
    p0.setBirthRate(0.0100)
    p0.setLitterSize(4)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.3)
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
    p0.renderer.setIgnoreScale(1)
    p0.renderer.setTextureFromNode("phase_3.5/models/props/suit-particles", "**/fire")
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.15)
    p0.renderer.setFinalXScale(1.0)
    p0.renderer.setInitialYScale(0.15)
    p0.renderer.setFinalYScale(1.0)
    p0.renderer.setNonanimatedTheta(20.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(5.0697)
    p0.emitter.setAmplitudeSpread(2.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, -4.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Ring parameters
    p0.emitter.setRadius(0.6)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('jfo')
    # Force parameters
    force0 = LinearJitterForce(200.0000, 0)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearSinkForce(Point3(4.0000, 0.0000, 79.0000), LinearDistanceForce.FTONEOVERRSQUARED, 15.9701, 95.0100, 1)
    force1.setActive(1)
    f0.addForce(force1)
    self.addForceGroup(f0)


@csparticle
def trialByFireRing(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("ZSpinParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("RingEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.0200)
    p0.setLitterSize(18)
    p0.setLitterSpread(3)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.0000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Z Spin factory parameters
    p0.factory.setInitialAngle(0.0000)
    p0.factory.setInitialAngleSpread(40.0000)
    p0.factory.enableAngularVelocity(0)
    p0.factory.setFinalAngle(0.0000)
    p0.factory.setFinalAngleSpread(0.0000)
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sprite parameters
    p0.renderer.setTextureFromNode("phase_3.5/models/props/suit-particles", "**/fire")
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(0)
    p0.renderer.setYScaleFlag(0)
    p0.renderer.setAnimAngleFlag(1)
    p0.renderer.setInitialXScale(2.0000)
    p0.renderer.setFinalXScale(10.0000)
    p0.renderer.setInitialYScale(2.0000)
    p0.renderer.setFinalYScale(10.0000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 40.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(1.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Ring parameters
    p0.emitter.setRadius(45.0000)
    p0.emitter.setRadiusSpread(0.5000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('Tornaga')
    # Force parameters
    force0 = LinearSourceForce(Point3(0.0000, 100.0000, 0.0000), LinearDistanceForce.FTONEOVERRSQUARED, 1.0000, 1.0000, 1)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def witchHunterFlagFireBase(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("RingEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.0100)
    p0.setLitterSize(3)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(2.6000)
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
    p0.renderer.addTextureFromNode('phase_3.5/models/props/suit-particles', '**/fire')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.2000)
    p0.renderer.setFinalXScale(1.0000)
    p0.renderer.setInitialYScale(0.2000)
    p0.renderer.setFinalYScale(1.0000)
    p0.renderer.setNonanimatedTheta(20.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 10.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Ring parameters
    p0.emitter.setRadius(1.0000)
    p0.emitter.setRadiusSpread(0.0000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('jfo')
    # Force parameters
    force0 = LinearJitterForce(15.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def witchHunterFlagFireCloth(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("RectangleEmitter")
    p0.setPoolSize(2048)
    p0.setBirthRate(0.0100)
    p0.setLitterSize(6)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(2.6000)
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
    p0.renderer.addTextureFromNode('phase_3.5/models/props/suit-particles', '**/fire')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.2000)
    p0.renderer.setFinalXScale(1.0000)
    p0.renderer.setInitialYScale(0.2000)
    p0.renderer.setFinalYScale(1.0000)
    p0.renderer.setNonanimatedTheta(20.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(1.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Rectangle parameters
    p0.emitter.setMinBound(Point2(-12.0000, -8.0000))
    p0.emitter.setMaxBound(Point2(12.0000, 8.0000))
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('jfo')
    # Force parameters
    force0 = LinearJitterForce(15.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def witchHunterFlagFireClothDust(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("RectangleEmitter")
    p0.setPoolSize(2048)
    p0.setBirthRate(0.0100)
    p0.setLitterSize(6)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(2.6000)
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
    p0.renderer.addTextureFromNode('phase_4/models/props/tt_m_efx_ext_smoke', '**/**')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.2000)
    p0.renderer.setFinalXScale(1.0000)
    p0.renderer.setInitialYScale(0.2000)
    p0.renderer.setFinalYScale(1.0000)
    p0.renderer.setNonanimatedTheta(20.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(1.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Rectangle parameters
    p0.emitter.setMinBound(Point2(-12.0000, -8.0000))
    p0.emitter.setMaxBound(Point2(12.0000, 8.0000))
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('jfo')
    # Force parameters
    force0 = LinearJitterForce(15.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def deepDiverSplash(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("DiscEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.0150)
    p0.setLitterSize(3)
    p0.setLitterSpread(2)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(0.7500)
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
    p0.renderer.addTextureFromNode('phase_4/models/char/bubble','**/fishingBubble')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.2000)
    p0.renderer.setFinalXScale(0.3000)
    p0.renderer.setInitialYScale(0.2000)
    p0.renderer.setFinalYScale(0.3000)
    p0.renderer.setNonanimatedTheta(20.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(1)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(5.0000)
    p0.emitter.setAmplitudeSpread(2.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 25.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(1.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Disc parameters
    p0.emitter.setRadius(3.000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('jfo')
    # Force parameters
    force0 = LinearJitterForce(3.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearVectorForce(Vec3(0.0000, 0.0000, -50.0000), 1.0000, 0)
    force1.setVectorMasks(1, 1, 1)
    force1.setActive(1)
    f0.addForce(force1)
    self.addForceGroup(f0)


@csparticle
def prethinkerJumpSparksCircle(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SparkleParticleRenderer")
    p0.setEmitter("DiscEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.0900)
    p0.setLitterSize(10)
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
    p0.renderer.setCenterColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setEdgeColor(Vec4(1.00, 0.50, 0.00, 1.00))
    p0.renderer.setBirthRadius(0.1000)
    p0.renderer.setDeathRadius(0.1000)
    p0.renderer.setLifeScale(SparkleParticleRenderer.SPNOSCALE)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.4000))
    p0.emitter.setExplicitLaunchVector(Vec3(8.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Disc parameters
    p0.emitter.setRadius(1.0000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('force1')
    # Force parameters
    force0 = LinearJitterForce(5.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def prethinkerJumpSparksUp(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SparkleParticleRenderer")
    p0.setEmitter("DiscEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.0900)
    p0.setLitterSize(10)
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
    p0.renderer.setCenterColor(Vec4(1.00, 0.70, 0.00, 1.00))
    p0.renderer.setEdgeColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setBirthRadius(0.1000)
    p0.renderer.setDeathRadius(0.1000)
    p0.renderer.setLifeScale(SparkleParticleRenderer.SPNOSCALE)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 2.000))
    p0.emitter.setExplicitLaunchVector(Vec3(9.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Disc parameters
    p0.emitter.setRadius(1.0000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('force1')
    # Force parameters
    force0 = LinearJitterForce(50.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def prethinkerRocketDust(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(2048)
    p0.setBirthRate(0.0150)
    p0.setLitterSize(2)
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
    # Sprite parameters
    p0.renderer.addTextureFromNode('phase_4/models/props/tt_m_efx_ext_smoke', '**/**')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.2000)
    p0.renderer.setFinalXScale(2.0000)
    p0.renderer.setInitialYScale(0.2000)
    p0.renderer.setFinalYScale(2.0000)
    p0.renderer.setNonanimatedTheta(20.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Sphere Volume parameters
    p0.emitter.setRadius(1.0000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('jfo')
    # Force parameters
    force0 = LinearJitterForce(3.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)


@csparticle
def rainmakerTornado(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-2')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("BoxEmitter")
    p0.setPoolSize(102400)
    p0.setBirthRate(0.0400)
    p0.setLitterSize(10)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(6.0000)
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
    p0.renderer.addTextureFromFile('phase_6/maps/tt_t_efx_ext_smoke.png')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setInitialXScale(0.5000)
    p0.renderer.setFinalXScale(12.0000)
    p0.renderer.setInitialYScale(0.5000)
    p0.renderer.setFinalYScale(12.0000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    p0.renderer.getColorInterpolationManager().addLinear(1.0, 1.0, Vec4(0.7843137383460999, 0.7843137383460999,
                                                                        0.7843137383460999, 0.19607843458652496),
                                                         Vec4(1.0, 1.0, 0.0, 1.0), True)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(1.0000, 0.0000, 60.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Box parameters
    p0.emitter.setMinBound(Point3(-1.5000, -1.5000, -1.5000))
    p0.emitter.setMaxBound(Point3(1.5000, 1.5000, 1.5000))
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('source')
    # Force parameters
    force0 = LinearCylinderVortexForce(50.0000, 20.0000, 5.0000, 1.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearVectorForce(Vec3(0.0000, 0.0000, -4.0000), 5.0000, 0)
    force1.setVectorMasks(1, 1, 1)
    force1.setActive(1)
    f0.addForce(force1)
    force2 = LinearSinkForce(Point3(0.0000, 0.0000, 2.0000), LinearDistanceForce.FTONEOVERRSQUARED, 1.0000, 1.0000, 1)
    force2.setVectorMasks(1, 1, 1)
    force2.setActive(1)
    f0.addForce(force2)
    self.addForceGroup(f0)


@csparticle
def lightningGagExplosion(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("ZSpinParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("SphereVolumeEmitter")
    p0.setPoolSize(120)
    p0.setBirthRate(0.001)
    p0.setLitterSize(120)
    p0.setLitterSpread(0)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(4.0000)
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
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAINOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sprite parameters
    p0.renderer.addTextureFromNode('phase_3.5/models/gui/material_icons', '**/material_lightning')
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(1)
    p0.renderer.setInitialXScale(1.0000)
    p0.renderer.setFinalXScale(5.0000)
    p0.renderer.setInitialYScale(1.0000)
    p0.renderer.setFinalYScale(5.0000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(8.0000)
    p0.emitter.setAmplitudeSpread(2.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 15.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(1.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Sphere Volume parameters
    p0.emitter.setRadius(0.1000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('forces')
    # Force parameters
    force0 = LinearSinkForce(Point3(0.0000, 0.0000, -79.0000), LinearDistanceForce.FTONEOVERRSQUARED, 15.9701, 80.0000,
                             1)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    force1 = LinearJitterForce(15.0000, 0)
    force1.setVectorMasks(1, 1, 1)
    force1.setActive(1)
    f0.addForce(force1)
    self.addForceGroup(f0)


@csparticle
def chillyAir(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("ZSpinParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("DiscEmitter")
    p0.setPoolSize(100)
    p0.setBirthRate(0.0750)
    p0.setLitterSize(3)
    p0.setLitterSpread(1)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.5000)
    p0.factory.setLifespanSpread(1.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Z Spin factory parameters
    p0.factory.setInitialAngle(0.0000)
    p0.factory.setInitialAngleSpread(360.0000)
    p0.factory.enableAngularVelocity(1)
    p0.factory.setAngularVelocity(0.0000)
    p0.factory.setAngularVelocitySpread(0.0000)
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAINOUT)
    p0.renderer.setUserAlpha(.20)
    # Sprite parameters
    # p0.renderer.setTextureFromNode("phase_8/models/props/snowflake_particle", "**/p1_2")
    p0.renderer.setTexture(loader.loadTexture('phase_3.5/maps/splash_particle.png'))
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, .20))
    p0.renderer.setXScaleFlag(0)
    p0.renderer.setYScaleFlag(0)
    p0.renderer.setAnimAngleFlag(1)
    p0.renderer.setInitialXScale(0.2000)
    p0.renderer.setFinalXScale(0.0000)
    p0.renderer.setInitialYScale(0.2000)
    p0.renderer.setFinalYScale(0.0000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PP_BLEND_CUBIC)
    p0.renderer.setAlphaDisable(0)
    p0.renderer.setColorBlendMode(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(5.0000)
    p0.emitter.setAmplitudeSpread(1.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, -40.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Disc parameters
    p0.emitter.setRadius(20.0000)
    self.addParticles(p0)

@csparticle
def chillyFlakes(self):
    self.reset()
    self.setPos(0.000, 0.000, 0.000)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("ZSpinParticleFactory")
    p0.setRenderer("SpriteParticleRenderer")
    p0.setEmitter("DiscEmitter")
    p0.setPoolSize(100)
    p0.setBirthRate(0.0750)
    p0.setLitterSize(3)
    p0.setLitterSpread(1)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(1.5000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Z Spin factory parameters
    p0.factory.setInitialAngle(0.0000)
    p0.factory.setInitialAngleSpread(360.0000)
    p0.factory.enableAngularVelocity(0)
    p0.factory.setFinalAngle(0.0000)
    p0.factory.setFinalAngleSpread(0.0000)
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAINOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sprite parameters
    # p0.renderer.setTextureFromNode("phase_8/models/props/snowflake_particle", "**/p1_2")
    p0.renderer.setTextureFromNode("phase_3.5/models/props/suit-particles", "**/snow-particle")
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(1)
    p0.renderer.setYScaleFlag(1)
    p0.renderer.setAnimAngleFlag(1)
    p0.renderer.setInitialXScale(1)
    p0.renderer.setFinalXScale(0.0000)
    p0.renderer.setInitialYScale(1)
    p0.renderer.setFinalYScale(0.0000)
    p0.renderer.setNonanimatedTheta(0.0000)
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PPBLENDLINEAR)
    p0.renderer.setColorBlendMode(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)
    p0.renderer.setAlphaDisable(0)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETRADIATE)
    p0.emitter.setAmplitude(8.0000)
    p0.emitter.setAmplitudeSpread(1.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, -40.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Disc parameters
    p0.emitter.setRadius(20.0000)
    self.addParticles(p0)


@csparticle
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


@csparticle
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


@csparticle
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


@csparticle
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


@csparticle
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


@csparticle
def hr_summon(self):
    self.reset()
    self.setPos(0.000, 0.000 + 20, 20.000 + 4)
    self.setHpr(0.000, 0.000, 0.000)
    self.setScale(1.000, 1.000, 1.000)
    p0 = Particles.Particles('particles-1')
    # Particles parameters
    p0.setFactory("PointParticleFactory")
    p0.setRenderer("SparkleParticleRenderer")
    p0.setEmitter("RingEmitter")
    p0.setPoolSize(1024)
    p0.setBirthRate(0.0200)
    p0.setLitterSize(2)
    p0.setLitterSpread(1)
    p0.setSystemLifespan(0.0000)
    p0.setLocalVelocityFlag(1)
    p0.setSystemGrowsOlderFlag(0)
    # Factory parameters
    p0.factory.setLifespanBase(2.0000)
    p0.factory.setLifespanSpread(0.0000)
    p0.factory.setMassBase(1.0000)
    p0.factory.setMassSpread(0.0000)
    p0.factory.setTerminalVelocityBase(400.0000)
    p0.factory.setTerminalVelocitySpread(0.0000)
    # Point factory parameters
    # Renderer parameters
    p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAINOUT)
    p0.renderer.setUserAlpha(1.00)
    # Sparkle parameters
    p0.renderer.setCenterColor(Vec4(0.00, 1.00, 0.00, 1.00))
    p0.renderer.setEdgeColor(Vec4(1.00, 0.00, 0.00, 1.00))
    p0.renderer.setBirthRadius(0.1000)
    p0.renderer.setDeathRadius(0.1000)
    p0.renderer.setLifeScale(SparkleParticleRenderer.SPNOSCALE)
    # Emitter parameters
    p0.emitter.setEmissionType(BaseParticleEmitter.ETEXPLICIT)
    p0.emitter.setAmplitude(1.0000)
    p0.emitter.setAmplitudeSpread(0.0000)
    p0.emitter.setOffsetForce(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, -30.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    # Ring parameters
    p0.emitter.setRadius(2.0000)
    p0.emitter.setRadiusSpread(0.0000)
    self.addParticles(p0)
    f0 = ForceGroup.ForceGroup('fg')
    # Force parameters
    force0 = LinearVectorForce(Vec3(0.0000, 0.0000, 20.0000), 1.0000, 0)
    force0.setVectorMasks(1, 1, 1)
    force0.setActive(1)
    f0.addForce(force0)
    self.addForceGroup(f0)

