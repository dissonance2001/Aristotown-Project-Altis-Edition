from __future__ import absolute_import
from toontown.safezone.DLSafeZoneLoader import DLSafeZoneLoader
from toontown.town.DLTownLoader import DLTownLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood

class DLHood(ToonHood):
    notify = directNotify.newCategory('DLHood')

    ID = ToontownGlobals.DonaldsDreamland
    TOWNLOADER_CLASS = DLTownLoader
    SAFEZONELOADER_CLASS = DLSafeZoneLoader
    STORAGE_DNA = 'phase_8/dna/storage_DL.dna'
    SKY_FILE = 'phase_8/models/props/DL_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (1.0, 0.9, 0.5, 1.0)

    HOLIDAY_DNA = {
      ToontownGlobals.WINTER_DECORATIONS: ['phase_8/dna/winter_storage_DL.dna'],
      ToontownGlobals.WACKY_WINTER_DECORATIONS: ['phase_8/dna/winter_storage_DL.dna'],
      ToontownGlobals.HALLOWEEN_PROPS: ['phase_8/dna/halloween_props_storage_DL.dna'],
      ToontownGlobals.SPOOKY_PROPS: ['phase_8/dna/halloween_props_storage_DL.dna']}
      
    def load(self):
        ToonHood.load(self)

        self.fog = Fog('DLFog')