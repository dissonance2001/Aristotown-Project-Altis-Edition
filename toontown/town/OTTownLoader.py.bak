import TownLoader
import OTStreet
from toontown.suit import Suit
from toontown.battle import BattleParticles

class OTTownLoader(TownLoader.TownLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        TownLoader.TownLoader.__init__(self, hood, parentFSM, doneEvent)
        self.streetClass = OTStreet.OTStreet
        self.musicFile = 'phase_7/audio/bgm/OT_SZ.ogg'
        self.activityMusicFile = 'phase_7/audio/bgm/OT_SZ_activity.ogg'
        self.townStorageDNAFile = 'phase_7/dna/storage_OT_town.dna'

    def load(self, zoneId):
        TownLoader.TownLoader.load(self, zoneId)
        self.crow1Sound = base.loader.loadSfx('phase_7/audio/sfx/yott_c1.ogg')
        self.crow2Sound = base.loader.loadSfx('phase_7/audio/sfx/yott_c2.ogg')
        self.raven1Sound = base.loader.loadSfx('phase_7/audio/sfx/yott_r1.ogg')
        self.raven2Sound = base.loader.loadSfx('phase_7/audio/sfx/yott_r2.ogg')
        self.ravenCrow1Sound = base.loader.loadSfx('phase_7/audio/sfx/yott_rc1.ogg')
        self.ravenCrow2Sound = base.loader.loadSfx('phase_7/audio/sfx/yott_c2.ogg')
        Suit.loadSuits(3)
        dnaFile = 'phase_7/dna/olde_toontown_' + str(self.canonicalBranchZone) + '.dna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
        del self.crow1Sound
        del self.crow2Sound
        del self.raven1Sound
        del self.raven2Sound
        del self.ravenCrow1Sound
        del self.ravenCrow2Sound
        Suit.unloadSuits(3)
        
    def enter(self, requestStatus):
        TownLoader.TownLoader.enter(self, requestStatus)

    def exit(self):
        TownLoader.TownLoader.exit(self)
