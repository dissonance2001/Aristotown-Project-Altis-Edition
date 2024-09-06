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
        Suit.loadSuits(3)
        dnaFile = 'phase_7/dna/olde_toontown_' + str(self.canonicalBranchZone) + '.dna'
        self.createHood(dnaFile)

    def unload(self):
        TownLoader.TownLoader.unload(self)
        Suit.unloadSuits(3)
        
    def enter(self, requestStatus):
        TownLoader.TownLoader.enter(self, requestStatus)

    def exit(self):
        TownLoader.TownLoader.exit(self)
