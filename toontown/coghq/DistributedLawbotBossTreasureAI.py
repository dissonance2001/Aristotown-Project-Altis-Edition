from toontown.safezone import DistributedTreasureAI
from toontown.safezone import TreasureGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class DistributedLawbotBossTreasureAI(DistributedTreasureAI.DistributedTreasureAI):

    def __init__(self, air, boss, lawyer, style, sx, sy, sz, fx, fy, fz):
        pos = lawyer.getPos()
        type = TreasureGlobals.SafeZoneTreasureSpawns[style][0]
        DistributedTreasureAI.DistributedTreasureAI.__init__(self, air, boss, type, pos[0], pos[1], 0)
        self.lawyerId = lawyer.doId
        self.style = style
        self.startPosition = (sx, sy, sz)
        self.finalPosition = (fx, fy, fz)

    def validAvatar(self, av):
        # Don't allow healing to toons that are at maxHp or are sad
        if 0 < av.getHp() < av.getMaxHp():
            av.toonUp(self.healAmount)
            return True
        else:
            return False

    def getLawyerId(self):
        return self.lawyerId

    def setLawyerId(self, lawyerId):
        self.lawyerId = lawyerId

    def b_setLawyerId(self, lawyerId):
        self.setLawyerId(lawyerId)
        self.d_setLawyerId(lawyerId)

    def d_setLawyerId(self, lawyerId):
        self.sendUpdate('setLawyerId', [lawyerId])

    def getStyle(self):
        return self.style

    def setStyle(self, hoodId):
        self.style = hoodId

    def b_setStyle(self, hoodId):
        self.setStyle(hoodId)
        self.d_setStyle(hoodId)

    def d_setStyle(self, hoodId):
        self.sendUpdate('setStyle', [hoodId])

    def getFinalPosition(self):
        return self.finalPosition

    def setFinalPosition(self, x, y, z):
        self.finalPosition = (x, y, z)

    def b_setFinalPosition(self, x, y, z):
        self.setFinalPosition(x, y, z)
        self.d_setFinalPosition(x, y, z)

    def d_setFinalPosition(self, x, y, z):
        self.sendUpdate('setFinalPosition', [x, y, z])

    def getStartPosition(self):
        return self.startPosition

    def setStartPosition(self, x, y, z):
        self.startPosition = (x, y, z)

    def b_setStartPosition(self, x, y, z):
        self.setStartPosition(x, y, z)
        self.d_setStartPosition(x, y, z)

    def d_setStartPosition(self, x, y, z):
        self.sendUpdate('setStartPosition', [x, y, z])
