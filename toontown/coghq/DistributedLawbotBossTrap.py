from direct.distributed.DistributedObject import *
from direct.fsm.FSM import FSM
from direct.interval.IntervalGlobal import *

from toontown.clashsuit.suit import BossCogGlobals
from toontown.clasbattle.battle import BattleProps
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.distributed.ToontownClientRepository import ToontownClientRepository


@DirectNotifyCategory()
class DistributedLawbotBossTrap(DistributedObject, FSM):
    """
    DistributedLawbotBossTrap(DistributedObject, FSM)
    """

    def __init__(self, cr):
        """
        :param ToontownClientRepository cr: The client repository which maintains all client-side distributed objects.
        """
        DistributedObject.__init__(self, cr)
        FSM.__init__(self, "DistributedLawbotBossTrap")
        self.index = None
        self.trap = None
        self.trapLevel = None
        self.status = 0
        self.prestiged = False
        self.trapScale = Point3(*BossCogGlobals.LawbotBossTrapScale)
        self.boss = None
        self.trapTrack = None

        self.activeColor = VBase4(1, 1, 1, 1)
        self.brokenColor = VBase4(1, 0, 0, 0.8)
        self.prestigeColor = VBase4(0.35, 0.35, 1, 1)

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.boss.traps[self.index] = self

        if self.trapLevel == 4:
            self.trap = BattleProps.globalPropPool.getProp("quicksand")
        elif self.trapLevel == 5:
            self.trap = BattleProps.globalPropPool.getProp("trapdoor")

        self.trap.setPosHpr(*BossCogGlobals.LawbotBossTrapsPosHpr[self.index])
        self.trap.hide()
        self.trap.reparentTo(render)

        self.trapBrokeSfx = base.loader.loadSfx('phase_11/audio/sfx/LB_boss_trap_break.ogg')
        self.trapFixedSfx = base.loader.loadSfx('phase_11/audio/sfx/LB_boss_trap_fix.ogg')

    def delete(self):
        DistributedObject.delete(self)
        self.ignoreAll()
        self.request("Off")
        self.interruptTrapTrack()
        self.trap.detachNode()

        if hasattr(self.boss, 'traps'):
            del self.boss.traps[self.index]

        del self.trap
        del self.index
        del self.trapLevel
        del self.status
        del self.trapScale
        del self.boss

    def setIndex(self, index):
        self.index = index

    def setBossCogId(self, bossCogId):
        self.bossCogId = bossCogId
        self.boss = base.cr.doId2do[bossCogId]

    def setTrapLevel(self, trapLevel):
        self.trapLevel = trapLevel

    def setState(self, state):
        self.request(state)

    def getState(self):
        return self.state

    def interruptTrapTrack(self):
        if self.trapTrack and self.trapTrack.isPlaying():
            self.trapTrack.pause()
        self.trapTrack = None

    def enterEnableTrap(self):
        self.interruptTrapTrack()
        self.trapTrack = Sequence(
            Wait(BossCogGlobals.LawbotBossTrapEnableT),
            Func(self.trap.show),
            Func(self.trap.setScale, Point3(0.1, 0.1, 0.1)),
            LerpScaleInterval(self.trap, 1.2, self.trapScale),
        )
        self.trapTrack.start()

    def enterActivateTrap(self):
        self.interruptTrapTrack()
        self.trapTrack = Sequence()
        if self.trapLevel == 5:
            self.trapTrack.append(Func(self.trap.setColor, VBase4(0, 0, 0, 1)))
        self.trapTrack.append(Wait(2))
        self.trapTrack.append(LerpScaleInterval(self.trap, 1.2, Point3(0.01, 0.01, 0.01)))
        self.trapTrack.append(Func(self.trap.hide))
        if self.trapLevel == 5:
            self.trapTrack.append(Func(self.trap.setColor, VBase4(1, 1, 1, 1)))
        self.trapTrack.start()

    def enterBossLandBroken(self):
        self.interruptTrapTrack()
        self.trapTrack = Sequence()
        goneParallel = Parallel()
        goneParallel.append(
            LerpScaleInterval(
                self.trap,
                BossCogGlobals.LawbotBossTrapLandBrokenT,
                Point3(0.01, 0.01, 0.01)
            )
        )
        goneParallel.append(
            LerpColorInterval(
                self.trap,
                0.75,
                self.brokenColor
            )
        )
        self.trapTrack.append(goneParallel)
        self.trapTrack.append(Func(self.trap.setColor, VBase4(1, 1, 1, 1)))
        self.trapTrack.append(Func(self.trap.hide))
        self.trapTrack.start()

    def enterBreakTrap(self):
        self.interruptTrapTrack()
        self.trapTrack = Sequence(
            Func(self.trap.show),
            Func(self.trap.setScale, self.trapScale),
            LerpColorInterval(
                self.trap,
                BossCogGlobals.LawbotBossTrapBreakT,
                self.brokenColor,
                self.prestigeColor if self.prestiged else self.activeColor
            ),
            Func(base.playSfx, self.trapBrokeSfx),
        )
        self.trapTrack.start()

    def enterInterruptBreak(self):
        self.interruptTrapTrack()
        self.trapTrack = Sequence(
            Func(self.trap.show),
            Func(self.trap.setScale, self.trapScale),
            LerpColorInterval(
                self.trap,
                BossCogGlobals.LawbotBossTrapInterruptBreakT,
                self.prestigeColor if self.prestiged else self.activeColor
            )
        )
        self.trapTrack.start()

    def enterRepairTrap(self):
        self.interruptTrapTrack()
        self.trapTrack = Sequence(
            Func(self.trap.show),
            Func(self.trap.setScale, self.trapScale),
            LerpColorInterval(
                self.trap,
                BossCogGlobals.LawbotBossTrapRepairT,
                self.activeColor,
                self.brokenColor
            ),
            Func(base.playSfx, self.trapFixedSfx)
        )
        self.trapTrack.start()

    def enterPrestigeTrap(self):
        self.interruptTrapTrack()
        self.trapTrack = Sequence(
            Func(self.trap.show),
            Func(self.trap.setScale, self.trapScale),
            LerpColorInterval(
                self.trap,
                BossCogGlobals.LawbotBossTrapBreakT,
                self.prestigeColor,
                self.activeColor
            ),
            Func(base.playSfx, self.trapFixedSfx),
        )
        self.trapTrack.start()

    def updateColor(self):
        if self.status == 1:
            if self.prestiged:
                self.trap.setColor(self.prestigeColor)
            else:
                self.trap.setColor(self.activeColor)
            self.trap.show()
        elif self.status == 0:
            self.trap.setColor(self.activeColor)
            self.trap.hide()
        elif self.status == -1:
            self.trap.setColor(self.brokenColor)
            self.trap.show()

    def setStatus(self, status):
        self.status = status
        self.trap.setScale(self.trapScale)
        self.updateColor()

    def getStatus(self):
        return self.status

    def setPrestiged(self, prestiged):
        self.prestiged = prestiged
        self.updateColor()

    def getPrestiged(self):
        return self.prestiged

    def getTrapLevel(self):
        return self.trapLevel
