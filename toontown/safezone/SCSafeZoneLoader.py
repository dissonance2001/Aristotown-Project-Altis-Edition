from panda3d.core import *
from direct.interval.IntervalGlobal import *
from . import SafeZoneLoader
from . import SCPlayground

class SCSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = SCPlayground.SCPlayground
        self.musicFile = 'phase_13/audio/bgm/Sc_playground.ogg'
        self.activityMusicFile = 'phase_13/audio/bgm/skyclan.ogg'
        self.dnaFile = 'phase_13/dna/skyclan_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_13/dna/storage_SC_sz.pdna'

        
    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.wind1Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_1.ogg')
        self.wind2Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_2.ogg')
        self.wind3Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_3.ogg')

    def unload(self):
        del self.wind1Sound
        del self.wind2Sound
        del self.wind3Sound
        SafeZoneLoader.SafeZoneLoader.unload(self)
