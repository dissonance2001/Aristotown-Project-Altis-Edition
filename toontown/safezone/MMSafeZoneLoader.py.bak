from toontown.safezone import MMPlayground
from toontown.safezone import SafeZoneLoader
from toontown.safezone.MMDrumTrampolines import MMDrumTrampolines


class MMSafeZoneLoader(SafeZoneLoader.SafeZoneLoader):

    def __init__(self, hood, parentFSM, doneEvent):
        SafeZoneLoader.SafeZoneLoader.__init__(self, hood, parentFSM, doneEvent)
        self.playgroundClass = MMPlayground.MMPlayground
        self.musicFile = 'phase_6/audio/bgm/MM_nbrhood.ogg'
        self.activityMusicFile = 'phase_6/audio/bgm/MM_SZ_activity.ogg'
        self.dnaFile = 'phase_6/dna/minnies_melody_land_sz.pdna'
        self.safeZoneStorageDNAFile = 'phase_6/dna/storage_MM_sz.pdna'
        self.drumTrampolines = None

    def load(self):
        SafeZoneLoader.SafeZoneLoader.load(self)
        self.drumTrampolines = MMDrumTrampolines()
        self.drumTrampolines.load()

    def unload(self):
        if self.drumTrampolines:
            self.drumTrampolines.unload()
            self.drumTrampolines = None
        SafeZoneLoader.SafeZoneLoader.unload(self)
