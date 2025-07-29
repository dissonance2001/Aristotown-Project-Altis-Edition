import ToonHood
from toontown.safezone import SCSafeZoneLoader
from toontown.toonbase.ToontownGlobals import *

class SCHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = SkyClan
        self.safeZoneLoaderClass = SCSafeZoneLoader.SCSafeZoneLoader
        self.storageDNAFile = 'phase_13/dna/storage_SC.dna'
        self.skyFile = 'phase_3.5/models/props/BR_sky'
        self.spookySkyFile = 'phase_3.5/models/props/BR_sky'
        self.whiteFogColor = Vec4(0.8, 0.8, 0.8, 1)
        self.titleColor = (1.0, 0.9, 0.5, 1.0)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.parentFSM.getStateNamed('SCHood').addChild(self.fsm)
        self.sky.setScale(2.0)
        self.fog = Fog('SCFog')

    def unload(self):
        self.parentFSM.getStateNamed('SCHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)
        self.fog = None

    def enter(self, *args):
        ToonHood.ToonHood.enter(self, *args)
        base.camLens.setNearFar(SpeedwayCameraNear, SpeedwayCameraFar)

    def exit(self):
        base.camLens.setNearFar(DefaultCameraNear, DefaultCameraFar)
        ToonHood.ToonHood.exit(self)

    def setWhiteFog(self):
        if base.wantFog:
            self.fog.setColor(self.whiteFogColor)
            self.fog.setLinearRange(0.0, 800.0)
            render.clearFog()
            render.setFog(self.fog)
            self.sky.clearFog()
            self.sky.setFog(self.fog)

    def setNoFog(self):
        if base.wantFog:
            render.clearFog()
            self.sky.clearFog()
