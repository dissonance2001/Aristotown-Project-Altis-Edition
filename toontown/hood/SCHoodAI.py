from direct.directnotify import DirectNotifyGlobal
import HoodAI
from toontown.toonbase import ToontownGlobals

class SCHoodAI(HoodAI.HoodAI):
    notify = DirectNotifyGlobal.directNotify.newCategory('SCHoodAI')

    def __init__(self, air, zoneId=None):
        hoodId = ToontownGlobals.SkyClan
        if zoneId == None:
            zoneId = hoodId
        HoodAI.HoodAI.__init__(self, air, zoneId, hoodId)
        return

    def startup(self):
        HoodAI.HoodAI.startup(self)
