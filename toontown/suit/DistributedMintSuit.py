from toontown.suit import DistributedFactorySuit
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer

class DistributedMintSuit(DistributedFactorySuit.DistributedFactorySuit):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedMintSuit')
	
    def renameBoss(self):
        pass

    def setNeutralAnimation(self):
        pass

    def checkCogLured(self, battle):
        pass

    def checkCogHP(self, battle):
        pass

    def checkCogHPDrop(self, battle):
        pass

    def checkCogHPBomb(self, battle):
        pass

    def checkCogHPZap(self, battle):
        pass

    def checkCogHPLaserRevive(self, battle):
        pass

    def checkCogHPLaser(self, battle):
        pass

    def checkCogHPRevive(self, battle):
        pass

    def checkCogOvercharge(self):
        pass

    def setNeutralAnimationRolled(self):
        pass

    def setNeutralAnimationTrap(self):
        pass