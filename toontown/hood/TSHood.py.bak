from toontown.safezone.TSSafeZoneLoader import TSSafeZoneLoader
from toontown.town.TSTownLoader import TSTownLoader
from toontown.toonbase import ToontownGlobals
from toontown.hood.ToonHood import ToonHood


class TSHood(ToonHood):
    notify = directNotify.newCategory('TSHood')

    ID = ToontownGlobals.Toonseltown
    TOWNLOADER_CLASS = TSTownLoader
    SAFEZONELOADER_CLASS = TSSafeZoneLoader
    STORAGE_DNA = 'phase_13/dna/storage_TS.pdna'
    SKY_FILE = 'phase_3.5/models/props/BR_sky'
    SPOOKY_SKY_FILE = 'phase_3.5/models/props/BR_sky'
    TITLE_COLOR = (0.3, 0.6, 1.0, 1.0)

    def unload(self):
        if getattr(base, 'localAvatar', None) and getattr(base.localAvatar, 'pieType', -1) == 9:
            base.localAvatar.clearSnowballs()
        ToonHood.unload(self)
