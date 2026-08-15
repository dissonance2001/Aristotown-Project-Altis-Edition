from toontown.classicchars import DistributedMinnieAI
from toontown.hood import HoodAI
from toontown.safezone import DistributedTrolleyAI
from toontown.toon import NPCToons
from toontown.toonbase import ToontownGlobals
from toontown.ai import DistributedTrickOrTreatTargetAI
from toontown.ai import DistributedWinterCarolingTargetAI

class TSHoodAI(HoodAI.HoodAI):
    def __init__(self, air):
        HoodAI.HoodAI.__init__(self, air,
                               ToontownGlobals.Toonseltown,
                               ToontownGlobals.Toonseltown)

        self.trolley = None
        self.classicChar = None

        self.startup()

    def startup(self):
        HoodAI.HoodAI.startup(self)

        existingNpcIds = set([getattr(obj, 'npcId', None) for obj in self.air.doId2do.values()])
        npcIdList = NPCToons.zone2NpcDict.get(self.zoneId, [])
        for i in xrange(len(npcIdList)):
            npcId = npcIdList[i]
            if npcId not in existingNpcIds:
                npcDesc = NPCToons.NPCToonDict.get(npcId)
                NPCToons.createNPC(self.air, npcId, npcDesc, self.zoneId, posIndex=i)

        # if simbase.config.GetBool('want-minigames', True):
        #     self.createTrolley()
        if simbase.config.GetBool('want-classic-chars', True):
            if simbase.config.GetBool('want-minnie', True):
                self.createClassicChar()

        if simbase.air.wantHalloween:
            self.TrickOrTreatTargetManager = DistributedTrickOrTreatTargetAI.DistributedTrickOrTreatTargetAI(self.air)
            self.TrickOrTreatTargetManager.generateWithRequired(4835)

        if simbase.air.wantChristmas:
            self.WinterCarolingTargetManager = DistributedWinterCarolingTargetAI.DistributedWinterCarolingTargetAI(
                self.air)
            self.WinterCarolingTargetManager.generateWithRequired(4614)

    # def createTrolley(self):
    #     self.trolley = DistributedTrolleyAI.DistributedTrolleyAI(self.air)
    #     self.trolley.generateWithRequired(self.zoneId)
    #     self.trolley.start()

    def createClassicChar(self):
        self.classicChar = DistributedMinnieAI.DistributedMinnieAI(self.air)
        self.classicChar.generateWithRequired(self.zoneId)
        self.classicChar.start()
