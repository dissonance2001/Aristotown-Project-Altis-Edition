from panda3d.core import *
from direct.interval.IntervalGlobal import *
import SafeZoneLoader
import TSPlayground
from toontown.battle import BattleParticles

class TSSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):
    SnowFadeLerpTime = 2.0

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = TSPlayground.TSPlayground
        self.musicFile = 'phase_13/audio/bgm/winter/christmas_ts_sz.ogg'
        self.activityMusicFile = 'phase_13/audio/bgm/winter/christmas_ts_int.ogg'
        self.dnaFile = 'phase_13/dna/toonseltown_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_13/dna/storage_TS_sz.pdna'
        self.snowPiles = []

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.wind1Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_1.ogg')
        self.wind2Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_2.ogg')
        self.wind3Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_3.ogg')
        self.snow = BattleParticles.loadParticleFile('snowdisk.ptf')
        self.snow.setPos(0, 0, 5)
        self.extraSnow = []
        for snowPos in ((0, 30, 10), (0, 10, 10), (0, 20, 5)):
            snowEffect = BattleParticles.loadParticleFile('snowdisk.ptf')
            snowEffect.setPos(*snowPos)
            self.extraSnow.append(snowEffect)
        self.snowRender = self.geom.attachNewNode('snowRender')
        self.snowRender.setDepthWrite(0)
        self.snowRender.setBin('fixed', 1)
        self.snowFade = None
        snowPilePos = [
            ((-2.408, 103.579, 20.716), 120, 2),
            ((-180.463, -47.426, 20.937), 180, 3),
            ((12.284, 7.393, 8.145), 101.977, 1.6),
        ]
        for pos, heading, scale in snowPilePos:
            snowPileModel = loader.loadModel('phase_8/models/props/snow_pile_full')
            snowPile = snowPileModel.find('**/prop_snow_pile_full')
            if snowPile.isEmpty():
                snowPile = snowPileModel
            else:
                snowPile.wrtReparentTo(self.geom)
                snowPileModel.removeNode()
            if snowPile.getParent().isEmpty():
                snowPile.reparentTo(self.geom)
            snowPile.setPos(*pos)
            snowPile.setH(heading)
            snowPile.setScale(scale)
            for snowCollision in snowPile.findAllMatches('**/+CollisionNode'):
                snowCollision.setTag('giveSnowballs', 'snowballs')
                snowCollision.setTag('surface', 'snow')
            self.snowPiles.append(snowPile)
        return

    def unload(self):
        del self.wind1Sound
        del self.wind2Sound
        del self.wind3Sound
        for snowPile in self.snowPiles:
            if snowPile and not snowPile.isEmpty():
                snowPile.removeNode()
        self.snowPiles = []
        del self.snow
        del self.extraSnow
        del self.snowRender
        SafeZoneLoader.SafeZoneLoader.unload(self)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)
        self.snow.start(camera, self.snowRender)
        for snowEffect in self.extraSnow:
            snowEffect.start(camera, self.snowRender)

    def exit(self):
        self.resetSnowLerp()
        self.snow.cleanup()
        for snowEffect in self.extraSnow:
            snowEffect.cleanup()
        SafeZoneLoader.SafeZoneLoader.exit(self)
        
    def resetSnowLerp(self):
        if self.snowFade != None:
            self.snowFade.stop()
            self.snowFade = None
        return

    def fadeInSnow(self):
        self.resetSnowLerp()
        currentScale = self.snowRender.getColorScale()[3]
        ivals = [LerpFunctionInterval(self.snowRender.setAlphaScale, fromData=currentScale, toData=1.0, duration=self.SnowFadeLerpTime), FunctionInterval(self.snowRender.clearColorScale)]
        self.snowFade = Track(ivals, 'snow-fade')
        self.snowFade.play()

    def fadeOutSnow(self):
        self.resetSnowLerp()
        currentScale = self.snowRender.getColorScale()[3]
        ivals = [LerpFunctionInterval(self.snowRender.setAlphaScale, fromData=currentScale, toData=0.0, duration=self.SnowFadeLerpTime)]
        self.snowFade = Track(ivals, 'snow-fade')
        self.snowFade.play()
