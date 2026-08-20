from direct.interval.IntervalGlobal import *
from pandac.PandaModules import Fog, LinearJitterForce, LinearVectorForce, Vec3, Vec4
from toontown.battle import BattleParticles


class PlutocratEnvironment(object):
    FogColor = Vec4(0.749, 0.749, 0.759, 1.0)
    NormalDensity = 0.017
    SquallDensity = 0.0525
    NormalBirthRate = 0.02
    SquallBirthRate = 0.01

    def __init__(self, geom):
        self.geom = geom
        self.fogTrack = None
        self.snowTrack = None
        self.snow = BattleParticles.loadParticleFile('plutocratSnow.ptf')
        self.snow.setPos(0, 0, 5)
        self.snowRender = geom.attachNewNode('plutocratSnowRender')
        self.snowRender.setDepthWrite(0)
        self.snowRender.setBin('fixed', 1)
        self.snow.start(camera, self.snowRender)
        self.snowParticles = self.snow.getParticlesList()[0]
        forceGroup = self.snow.getForceGroupNamed('gravity')
        self.normalVectorForce = LinearVectorForce(Vec3(0, 0, -1), 1.5, 0)
        self.normalVectorForce.setActive(1)
        self.normalJitterForce = LinearJitterForce(10.0, 0)
        self.normalJitterForce.setActive(1)
        self.squallVectorForce = LinearVectorForce(Vec3(0, 0, -2), 1.5, 0)
        self.squallVectorForce.setActive(0)
        self.squallJitterForce = LinearJitterForce(30.0, 0)
        self.squallJitterForce.setActive(0)
        if forceGroup:
            forceGroup.addForce(self.normalVectorForce)
            forceGroup.addForce(self.normalJitterForce)
            forceGroup.addForce(self.squallVectorForce)
            forceGroup.addForce(self.squallJitterForce)
        self.areaFog = Fog('plutocrat-area-fog')
        self.areaFog.setColor(self.FogColor)
        self.areaFog.setExpDensity(self.NormalDensity)
        render.setFog(self.areaFog)
        self.sfxLoop = loader.loadSfx('phase_10/audio/sfx/SA_snowsquall_loop.ogg')
        self.setDefault(instant=1)

    def _updateParticleScale(self, value):
        renderer = self.snowParticles.renderer
        renderer.setInitialXScale(lerp(0.03125, 0.05, value))
        renderer.setFinalXScale(lerp(0.50, 0.8, value))
        renderer.setInitialYScale(lerp(0.03125, 0.05, value))
        renderer.setFinalYScale(lerp(0.50, 0.8, value))

    def _setForces(self, squall):
        self.normalVectorForce.setActive(0 if squall else 1)
        self.normalJitterForce.setActive(0 if squall else 1)
        self.squallVectorForce.setActive(1 if squall else 0)
        self.squallJitterForce.setActive(1 if squall else 0)
        self.snowParticles.setPoolSize(2048 if squall else 1024)
        self.snowParticles.setLitterSize(4 if squall else 1)
        self.snowParticles.setLitterSpread(1 if squall else 0)

    def _change(self, density, birthRate, squall, instant=0):
        render.setFog(self.areaFog)
        if self.fogTrack:
            try:
                self.fogTrack.pause()
            except:
                pass
            self.fogTrack = None
        if self.snowTrack:
            try:
                self.snowTrack.pause()
            except:
                pass
            self.snowTrack = None
        if instant:
            self.areaFog.setColor(self.FogColor)
            self.areaFog.setExpDensity(density)
            self.snowParticles.setBirthRate(birthRate)
            self._setForces(squall)
            self._updateParticleScale(1.0 if squall else 0.0)
        else:
            self.fogTrack = Parallel(
                LerpFunc(
                    self.areaFog.setExpDensity,
                    fromData=self.areaFog.getExpDensity(),
                    toData=density,
                    duration=3.0,
                    blendType='easeInOut'),
                LerpFunc(
                    self.areaFog.setColor,
                    fromData=self.areaFog.getColor(),
                    toData=self.FogColor,
                    duration=3.0,
                    blendType='easeInOut'))
            self.snowTrack = Parallel(
                Sequence(Func(self._setForces, squall)),
                LerpFunc(
                    self.snowParticles.setBirthRate,
                    fromData=self.snowParticles.getBirthRate(),
                    toData=birthRate,
                    duration=3.0,
                    blendType='easeInOut'),
                LerpFunc(
                    self._updateParticleScale,
                    fromData=0.0 if squall else 1.0,
                    toData=1.0 if squall else 0.0,
                    duration=3.0,
                    blendType='easeInOut'))
            self.fogTrack.start()
            self.snowTrack.start()
        if squall:
            try:
                base.playSfx(self.sfxLoop, looping=1)
            except:
                try:
                    self.sfxLoop.setLoop(1)
                    self.sfxLoop.play()
                except:
                    pass
        else:
            try:
                self.sfxLoop.stop()
            except:
                pass

    def setDefault(self, instant=0):
        self._change(self.NormalDensity, self.NormalBirthRate, False, instant)

    def setSnowSquall(self, instant=0):
        self._change(self.SquallDensity, self.SquallBirthRate, True, instant)

    def cleanup(self):
        if self.fogTrack:
            try:
                self.fogTrack.pause()
            except:
                pass
            self.fogTrack = None
        if self.snowTrack:
            try:
                self.snowTrack.pause()
            except:
                pass
            self.snowTrack = None
        try:
            self.sfxLoop.stop()
        except:
            pass
        try:
            self.snow.cleanup()
        except:
            try:
                self.snow.disable()
            except:
                pass
        if self.snowRender and not self.snowRender.isEmpty():
            self.snowRender.removeNode()
        self.snowRender = None
        render.clearFog()
