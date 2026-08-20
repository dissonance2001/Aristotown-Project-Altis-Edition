from __future__ import absolute_import
from toontown.safezone.OTSafeZoneLoader import OTSafeZoneLoader
from toontown.town.OTTownLoader import OTTownLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood


class OTHood(ToonHood):
    notify = directNotify.newCategory('OTHood')

    ID = ToontownGlobals.YeOlde
    TOWNLOADER_CLASS = OTTownLoader
    SAFEZONELOADER_CLASS = OTSafeZoneLoader
    STORAGE_DNA = 'phase_7/dna/storage_OT.pdna'
    SKY_FILE = 'phase_7/models/props/OT_sky'
    SPOOKY_SKY_FILE = 'phase_7/models/props/OT_sky'
    TITLE_COLOR = (1.0, 0.5, 0.5, 1.0)
