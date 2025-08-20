from panda3d.core import *
from direct.interval.IntervalGlobal import *
import SafeZoneLoader
import SCPlayground

class SCSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = SCPlayground.SCPlayground
        self.musicFile = 'phase_13/audio/bgm/Sc_playground.ogg'
        self.activityMusicFile = 'phase_13/audio/bgm/skyclan.ogg'
        self.dnaFile = 'phase_8/dna/the_burrrgh_sz.pdna' #'phase_13/dna/skyclan_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_8/dna/storage_BR_sz.pdna' #'phase_13/dna/storage_SC_sz.pdna'

        
    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.wind1Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_1.ogg')
        self.wind2Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_2.ogg')
        self.wind3Sound = base.loader.loadSfx('phase_8/audio/sfx/SZ_TB_wind_3.ogg')

        # Spawn all custom Sky Clan props
        self.spawnSkyClanProps()

    def spawnSkyClanProps(self): # This will do until the dna issues can be resolved
        props = [ 
            ('phase_13/models/events/skyclan/skyclan_pg', (0, 0, 0), (0, 0, 0)),
            ('phase_13/models/events/skyclan/fabricworker_msc', (75, 179, -40.7), (75, 0, 0)),
            ('phase_13/models/events/skyclan/hangar_msc', (93, -102, 13.3), (260, 0, 0)),
            ('phase_13/models/events/skyclan/repairshop_msc', (125, 195, -38.8), (295, 4, 0)),
            ('phase_13/models/events/skyclan/workshop_msc', (-104, -156, 27.652), (120, 0, 0)),
            ('phase_13/models/events/skyclan/watchtower_msc', (-49.743, 13.917, -0.15), (245, 0, 0)),
            ('phase_13/models/events/skyclan/clanhall_msc', (-96, -33, 0.028), (130, 0, 0)),
        ]

        for path, pos, hpr in props:
            model = loader.loadModel(path)
            model.reparentTo(self.geom)
            model.setPos(*pos)
            model.setHpr(*hpr)


    def unload(self):
        del self.wind1Sound
        del self.wind2Sound
        del self.wind3Sound
        SafeZoneLoader.SafeZoneLoader.unload(self)
