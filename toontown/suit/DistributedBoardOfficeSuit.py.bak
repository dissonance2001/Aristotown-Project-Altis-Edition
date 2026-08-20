from toontown.suit import DistributedFactorySuit
from direct.directnotify import DirectNotifyGlobal
from toontown.toonbase import TTLocalizer

class DistributedBoardOfficeSuit(DistributedFactorySuit.DistributedFactorySuit):
    notify = DirectNotifyGlobal.directNotify.newCategory('DistributedBoardOfficeSuit')
	
    def renameBoss(self):
        if self.getSkeleRevives() > 0:
            nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.getStyleName(),
             'dept': self.getStyleDept(),
             'level': '%s%s' % (self.getActualLevel(), TTLocalizer.SkeleRevivePostFix)}
            self.setName(TTLocalizer.BoardExecutive)
            self.setDisplayName(nameInfo)
        else:
            nameInfo = TTLocalizer.SuitBaseNameWithLevel % {'name': self.getStyleName(),
             'dept': self.getStyleDept(),
             'level': self.getActualLevel()}
            self.setName(TTLocalizer.BoardExecutive)
            self.setDisplayName(nameInfo)

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
