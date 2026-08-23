import time
import pickle
from direct.distributed.DistributedObjectAI import DistributedObjectAI

class DistributedHQInteriorAI(DistributedObjectAI):
    notify = directNotify.newCategory('DistributedHQInteriorAI')

    def __init__(self, block, air, zoneId):
        DistributedObjectAI.__init__(self, air)

        self.block = block
        self.zoneId = zoneId
        self.tutorial = 0
        self.isDirty = False
        self.accept('leaderboardChanged', self.leaderboardChanged)
        self.accept('leaderboardFlush', self.leaderboardFlush)

    def delete(self):
        self.ignore('leaderboardChanged')
        self.ignore('leaderboardFlush')
        self.ignore('setLeaderBoard')
        self.ignore('AIStarted')

        DistributedObjectAI.delete(self)

    def getZoneIdAndBlock(self):
        return [self.zoneId, self.block]

    def leaderboardChanged(self):
        self.isDirty = True

    def leaderboardFlush(self):
        if self.isDirty:
            self.sendNewLeaderBoard()

    def sendNewLeaderBoard(self):
        if self.air:
            self.isDirty = False
            self.sendUpdate('setLeaderBoard',
                [pickle.dumps(self.air.trophyMgr.getLeaderInfo(), 1)]
            )

    def getLeaderBoard(self):
        return pickle.dumps(self.air.trophyMgr.getLeaderInfo(), 1)

    def getTutorial(self):
        return self.tutorial

    def setTutorial(self, flag):
        if self.tutorial != flag:
            self.tutorial = flag
            self.sendUpdate('setTutorial', [self.tutorial])

    def requestGumballPurchase(self, offerId):
        avId = self.air.getAvatarIdFromSender()
        av = self.air.doId2do.get(avId)
        if not av:
            return
        from toontown.gumball import GumballGlobals
        offer = GumballGlobals.getOffer(offerId, self.zoneId)
        if not offer:
            self.sendUpdateToAvatarId(avId, 'gumballPurchaseResult', [2, int(offerId), 0, 0])
            return
        offerId, boosterType, cost, hours, offerKind = offer
        if av.getGumballs() < cost or not av.takeGumballs(cost):
            self.sendUpdateToAvatarId(avId, 'gumballPurchaseResult', [1, offerId, 0, 0])
            return
        resolvedType = boosterType
        if boosterType == GumballGlobals.RANDOM:
            resolvedType = GumballGlobals.getRandomUsefulBooster(seed=(int(time.time()) + avId + self.zoneId))
        endTimestamp = av.addGumballBooster(resolvedType, int(hours) * 3600)
        self.sendUpdate('setGumballMachineAnim', [1])
        self.sendUpdateToAvatarId(avId, 'gumballPurchaseResult', [0, offerId, int(resolvedType), int(endTimestamp)])
