from direct.distributed import DistributedObjectAI


class DistributedCollectableAI(DistributedObjectAI.DistributedObjectAI):
    def __init__(self, air, treasurePlanner, treasureStyle, x, y, z):
        DistributedObjectAI.DistributedObjectAI.__init__(self, air)
        self.treasurePlanner = treasurePlanner
        self.treasureStyle = treasureStyle
        self.pos = (x, y, z)

    def requestGrab(self):
        pass

    def validAvatar(self, av):
        return 1

    def getTreasureStyle(self):
        return self.treasureStyle

    def d_setGrab(self, avId):
        self.sendUpdate('setGrab', [avId])

    def d_setReject(self, avId):
        self.sendUpdate('setReject', [avId])

    def getPosition(self):
        return self.pos

    def setPosition(self, x, y, z):
        self.pos = (x, y, z)

    def b_setPosition(self, x, y, z):
        self.setPosition(x, y, z)
        self.d_setPosition(x, y, z)

    def d_setPosition(self, x, y, z):
        self.sendUpdate('setPosition', [x, y, z])
