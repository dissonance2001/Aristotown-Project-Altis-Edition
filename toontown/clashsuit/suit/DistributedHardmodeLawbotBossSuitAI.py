from panda3d.core import Vec2, Vec3, Point3

from toontown.suit import BossCogGlobals
from .DistributedLawbotBossSuitAI import *
from toontown.toon.gui.ToonTipGlobals import TTE


class DistributedHardmodeLawbotBossSuitAI(DistributedLawbotBossSuitAI):

    def __init__(self, lawbotBoss, air, suitPlanner, painting):
        DistributedLawbotBossSuitAI.__init__(self, lawbotBoss, air, suitPlanner, painting)
        self.type = BossCogGlobals.LawbotBossSuitNormal
        self.cannonBossState = 'BattleThree'
        self.maxEvidence = BossCogGlobals.HardmodeLawbotBossSoundEvidenceRequirement['max']

    def doNextMove(self, taskName):
        if self.currState == 'BattleFour':
            if self.getElite() and not self.isVirtual and not self.initialMove:
                if self.boss.traps is None:
                    return
                trapDict = {}
                # Create a dictionary containing each trap index and how far from the boss it is.
                for trap in self.boss.traps:
                    trapDict[self.boss.traps.index(trap)] = Vec3(self.boss.getPos() - trap.getPos()).length()
                # Sort it in ascending order.
                sortedTraps = sorted(trapDict.items(), key=lambda x: x[1], reverse=False)
                trapIndex = None
                # Run through the sorted traps, and continually attempt to find the closest one.
                for trapPair in sortedTraps:
                    tIndex = trapPair[0]
                    trap = self.boss.traps[tIndex]
                    if trap.getStatus() != 1 or trap.getSuitId() or trap.getDuringActivation():
                        continue
                    trapIndex = tIndex
                    break
                if not trapIndex:
                    self.doFlying()
                    return
                trap = self.boss.traps[trapIndex]
                self.b_setTrapIndex(trapIndex)
                trap.setSuitId(self.doId)
                trapPos = trap.getPos()
                self.doSwoop(trapPos[0], trapPos[1], trapPos[2])
                # Skelecog Tip
                for avId in self.boss.involvedToons:
                    toon = self.air.doId2do.get(avId)
                    if toon:
                        toon.showToonTip(TTE.TIP_CLO_EXE_DISABLING_TRAP)
            elif self.nearToons or self.targetToon:
                if self.targetToon:
                    toonId = self.targetToon
                    self.targetToon = None
                elif self.nearToons:
                    toonId = random.choice(self.nearToons)
                toon = self.air.doId2do.get(toonId)
                if not toon:
                    self.doFlying()
                    return
                toonPos = toon.getPos()
                toonPos = Point3(toonPos.getX(), toonPos.getY(), toonPos.getZ())
                self.doSwoop(toonPos[0], toonPos[1], toonPos[2])
            else:
                self.doFlying()
        else:
            self.doFlying()

        if self.initialMove:
            self.initialMove = False
