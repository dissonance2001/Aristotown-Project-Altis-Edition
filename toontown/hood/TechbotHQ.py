from __future__ import absolute_import
from toontown.coghq.TechbotCogHQLoader import TechbotCogHQLoader
from toontown.toonbase import ToontownGlobals
from toontown.toonbase import TTLocalizer
from toontown.hood.CogHood import CogHood
from toontown.hood import ZoneUtil

class TechbotHQ(CogHood):
    notify = directNotify.newCategory('TechbotHQ')

    ID = ToontownGlobals.TechbotHQ
    LOADER_CLASS = TechbotCogHQLoader
   # SKY_FILE = 'phase_3.5/models/props/TT_sky'

    def load(self):
        CogHood.load(self)

        self.sky.hide()

    def enter(self, requestStatus):
        CogHood.enter(self, requestStatus)

    def spawnTitleText(self, zoneId, floorNum=None):
        CogHood.spawnTitleText(self, zoneId)
