from toontown.hood import HoodAI
from toontown.toonbase import ToontownGlobals
from toontown.distributed.DistributedTimerAI import DistributedTimerAI
from toontown.classicchars import DistributedChipAI
from toontown.classicchars import DistributedDaleAI
from toontown.safezone import DistributedTrolleyAI
from toontown.dna.DNAParser import DNAGroup, DNAVisGroup
from toontown.safezone.DistributedPicnicBasketAI import DistributedPicnicBasketAI
from toontown.safezone import DistributedGameTableAI
from toontown.hood import ZoneUtil

class OZHoodAI(HoodAI.HoodAI):
    
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.OutdoorZone,
                               ToontownGlobals.OutdoorZone)

        self.trolley = None
        self.timer = None

        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)
        if simbase.config.GetBool('want-minigames', True):
            self.createTrolley()
            pass

    def createTrolley(self):
        self.trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
        self.trolley.generateWithRequired(self.zoneId)
        self.trolley.start()
