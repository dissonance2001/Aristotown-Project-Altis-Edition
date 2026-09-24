from toontown.safezone import DistributedCollectableAI


class DistributedQuestCollectableAI(DistributedCollectableAI.DistributedCollectableAI):

    def __init__(self, air, treasurePlanner, treasureStyle, x, y, z):
        DistributedCollectableAI.DistributedCollectableAI.__init__(self, air, treasurePlanner, treasureStyle, x, y, z)

    def requestGrab(self):
        avId = self.air.getAvatarIdFromSender()
        self.treasurePlanner.grabAttempt(avId, self.getDoId())
