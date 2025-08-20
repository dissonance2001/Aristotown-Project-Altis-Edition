from toontown.safezone.SCSafeZoneLoader import SCSafeZoneLoader
from toontown.town.SCTownLoader import SCTownLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood


class SCHood(ToonHood):
    notify = directNotify.newCategory('SCHood')

    ID = ToontownGlobals.SkyClan
    TOWNLOADER_CLASS = SCTownLoader
    SAFEZONELOADER_CLASS = SCSafeZoneLoader
    STORAGE_DNA = 'phase_8/dna/storage_BR.pdna' #'phase_13/dna/storage_SC.pdna'
    SKY_FILE = 'phase_3.5/models/props/BR_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (1.0, 0.5, 0.5, 1.0)
