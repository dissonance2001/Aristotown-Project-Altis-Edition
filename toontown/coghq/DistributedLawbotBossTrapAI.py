from direct.distributed.DistributedNodeAI import DistributedNodeAI

from toontown.clashsuit.suit import BossCogGlobals
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


@DirectNotifyCategory()
class DistributedLawbotBossTrapAI(DistributedNodeAI):
    """
    DistributedLawbotBossTrapAI(DistributedNodeAI)
    """

    def __init__(self, air, lawbotBoss, index, trapLevel):
        """
        :type air: ToontownAIRepository
        """
        DistributedNodeAI.__init__(self, air)
        self.boss = lawbotBoss
        self.bossId = lawbotBoss.doId
        self.index = index
        self.suitId = None
        self.trapLevel = trapLevel
        self.status = 0
        self.prestiged = False
        self.duringActivation = 0
        self.trapTask = None

    def announceGenerate(self):
        DistributedNodeAI.announceGenerate(self)
        self.trapTask = self.uniqueName("setTrapStatus")

    def getPosHpr(self):
        return (
            self.getX(),
            self.getY(),
            self.getZ(),
            self.getH(),
            self.getP(),
            self.getR()
        )

    def getBossCogId(self):
        return self.bossId

    def getIndex(self):
        return self.index

    def getTrapLevel(self):
        return self.trapLevel

    def delete(self):
        DistributedNodeAI.delete(self)
        self.removeTrapTask()

    def removeTrapTask(self):
        taskMgr.remove(self.trapTask)

    def b_setStatus(self, status):
        self.d_setStatus(status)
        self.setStatus(status)

    def d_setStatus(self, status):
        self.sendUpdate('setStatus', [status])

    def setStatus(self, status):
        # Set prestige to false if either: Trap is created or trap is broken
        if status == 1:
            self.setDuringActivation(0)
            if self.status != 1:
                self.b_setPrestiged(False)
        elif status == -1:
            self.b_setPrestiged(False)
        self.status = status
        self.setSuitId(None)

    def getStatus(self):
        return self.status

    def b_setPrestiged(self, prestiged):
        self.d_setPrestiged(prestiged)
        self.setPrestiged(prestiged)

    def d_setPrestiged(self, prestiged):
        self.sendUpdate('setPrestiged', [prestiged])

    def setPrestiged(self, prestiged):
        self.prestiged = prestiged
        self.setSuitId(None)
        if self.status == 1:
            self.setDuringActivation(0)

    def getPrestiged(self):
        return self.prestiged

    def setDuringActivation(self, flag):
        self.duringActivation = flag

    def getDuringActivation(self):
        return self.duringActivation

    def setSuitId(self, lawyerDoId):
        self.suitId = lawyerDoId

    def getSuitId(self):
        return self.suitId

    def d_setState(self, status):
        self.sendUpdate("setState", [status])

    def startEnable(self):
        self.removeTrapTask()
        self.d_setState('EnableTrap')
        taskMgr.doMethodLater(BossCogGlobals.LawbotBossTrapEnableT, self.b_setStatus, self.trapTask, extraArgs = [1])

    def startActivate(self):
        self.removeTrapTask()
        self.d_setState('ActivateTrap')
        taskMgr.doMethodLater(BossCogGlobals.LawbotBossTrapActivateT, self.b_setStatus, self.trapTask, extraArgs = [0])

    def startBreak(self):
        self.removeTrapTask()
        self.d_setState('BreakTrap')
        taskMgr.doMethodLater(BossCogGlobals.LawbotBossTrapBreakT, self.b_setStatus, self.trapTask, extraArgs = [-1])

    def startRepair(self):
        self.removeTrapTask()
        self.d_setState('RepairTrap')
        taskMgr.doMethodLater(BossCogGlobals.LawbotBossTrapRepairT, self.b_setStatus, self.trapTask, extraArgs = [1])

    def startInterruptBreak(self):
        self.removeTrapTask()
        self.d_setState('InterruptBreak')
        taskMgr.doMethodLater(BossCogGlobals.LawbotBossTrapInterruptBreakT, self.b_setStatus, self.trapTask, extraArgs=[1])

    def startLandBroken(self):
        self.removeTrapTask()
        self.d_setState('BossLandBroken')
        taskMgr.doMethodLater(
            BossCogGlobals.LawbotBossTrapLandBrokenT,
            self.b_setStatus,
            self.trapTask,
            extraArgs = [0]
        )

    def startPrestige(self):
        self.removeTrapTask()
        self.d_setState('PrestigeTrap')
        # Set this to prevent Skelecogs from attempting to break the trap while it is being prestiged.
        self.setDuringActivation(1)
        taskMgr.doMethodLater(
            BossCogGlobals.LawbotBossTrapPrestigeT,
            self.b_setPrestiged,
            self.trapTask,
            extraArgs = [True]
        )
