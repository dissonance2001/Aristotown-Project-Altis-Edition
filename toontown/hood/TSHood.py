import ToonHood
from toontown.safezone import TSSafeZoneLoader
from toontown.toonbase.ToontownGlobals import *

class TSHood(ToonHood.ToonHood):

    def __init__(self, parentFSM, doneEvent, dnaStore, hoodId):
        ToonHood.ToonHood.__init__(self, parentFSM, doneEvent, dnaStore, hoodId)
        self.id = Toonseltown
        self.safeZoneLoaderClass = TSSafeZoneLoader.TSSafeZoneLoader
        self.storageDNAFile = 'phase_13/dna/storage_TS.dna'
        self.skyFile = 'phase_3.5/models/props/BR_sky'
        self.spookySkyFile = 'phase_3.5/models/props/BR_sky'
        self.titleColor = (0.3, 0.6, 1.0, 1.0)

    def load(self):
        ToonHood.ToonHood.load(self)
        self.sky.setScale(4.0)
        self.parentFSM.getStateNamed('TSHood').addChild(self.fsm)

    def unload(self):
        self.parentFSM.getStateNamed('TSHood').removeChild(self.fsm)
        ToonHood.ToonHood.unload(self)

    def enter(self, *args):
        ToonHood.ToonHood.enter(self, *args)
        base.camLens.setNearFar(SpeedwayCameraNear, SpeedwayCameraFar)

    def exit(self):
        base.camLens.setNearFar(DefaultCameraNear, DefaultCameraFar)
        ToonHood.ToonHood.exit(self)
