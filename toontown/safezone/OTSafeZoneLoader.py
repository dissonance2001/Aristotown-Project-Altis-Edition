from panda3d.core import *
from direct.interval.IntervalGlobal import *
import SafeZoneLoader
import OTPlayground
from toontown.battle import BattleParticles
from toontown.toonbase import ToontownGlobals

class OTSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = OTPlayground.OTPlayground
        self.musicFile = 'phase_7/audio/bgm/OT_nbrhood.ogg'
        self.activityMusicFile = 'phase_7/audio/bgm/OT_SZ_activity.ogg'
        self.dnaFile = 'phase_7/dna/olde_toontown_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_7/dna/storage_OT_sz.dna'

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        return

    def unload(self):
        SafeZoneLoader.SafeZoneLoader.unload(self)

    def enter(self, requestStatus):
        SafeZoneLoader.SafeZoneLoader.enter(self, requestStatus)

    def exit(self):
        SafeZoneLoader.SafeZoneLoader.exit(self)
