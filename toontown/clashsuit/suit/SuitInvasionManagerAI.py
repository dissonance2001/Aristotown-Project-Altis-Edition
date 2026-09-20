from __future__ import annotations
import random
import time

from direct.showbase.DirectObject import DirectObject
from panda3d.core import ConfigVariableInt

from toontown.distributed.OtpDoGlobals import MESSENGER_CHANNEL_UD
from toontown.clashbattle.battle import SuitBattleGlobals
from toontown.clashsuit.suit import SuitDNA
from toontown.clashsuit.suit.SuitInvasionGlobals import *
from toontown.toonbase import ToontownGlobals
from toontown.uberdog.DistrictStatsUD import DistrictInvasionStatsUD
from toontown.uberdog.UberdogGlobalsUD import NET_MESSENGER_SHARD_INVASION_STATUS
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


@DirectNotifyCategory()
class SuitInvasionManagerAI(DirectObject):
    def __init__(self, air):
        super().__init__()
        self.air = air  # type: ToontownAIRepository

        self.invading = False
        self.start = 0
        self.remaining = 0
        self.total = 0
        self.suitDept = ''
        self.suitName = ''
        self.flags = 0
        self.type: Optional[InvasionType] = None
        self.hasSentInvasionHalfwayBulletin = False

        self.accept('startInvasion', self.handleStartInvasion)
        self.accept('stopInvasion', self.handleStopInvasion)

        self.sendInvasionStatus()

        self.air.addPostRemove(self.air.netMessenger.prepare(NET_MESSENGER_SHARD_INVASION_STATUS, [self.air.ourChannel, None]))

    def getInvading(self):
        return self.invading

    def getInvadingCog(self):
        return self.suitDept, self.suitName, self.flags

    def getInvasionFlags(self):
        return self.flags

    def startInvasion(self, suitDept: Optional[str] = None, suitName: Optional[str] = None, flags: int = 0, invasionType=InvasionType.NORMAL):
        if self.air.safeDistrict:
            # This is a safe district, no invasions here.
            return False

        if self.invading:
            # An invasion is currently in progress; ignore this request.
            return False

        if (suitDept is None) and (suitName is None) and (not flags):
            # This invasion is no-op.
            return False

        if (suitDept is None) and (suitName is not None):
            # It's impossible to determine the invading Cog.
            return False

        if (flags & IFSkelecog and flags & IFWaiter) or (flags & IFSkelecog and flags & IFV2):
            # The provided flag combination is not possible.
            return False

        if suitDept not in SuitDNA.suitDepts:
            # Invalid suit department.
            return False

        if invasionType not in list(InvasionType):
            # Invalid invasion type.
            return False

        if suitName == UnmarkedDeptInvasion:
            # We're doing a department invasion, so we need to set the placeholder suitName to None:
            suitName = None

        # Looks like we're all good. Begin the invasion:
        self.invading = True
        self.start = int(time.time())
        self.suitDept = suitDept
        self.suitName = suitName
        self.flags = flags

        # How many suits do we want?
        if invasionType == InvasionType.NORMAL:
            self.total = random.randint(1000, 5000)
        elif invasionType == InvasionType.MEGA:
            self.total = 100000
        self.remaining = self.total
        self.type = invasionType

        self.flySuits()
        self.notifyInvasionStarted()

        # Update the invasion tracker on the districts page in the Shticker Book:
        if self.suitDept is not None:
            self.air.distributedDistrict.b_setInvasionStatus(suitDept)
            if suitName is not None:
                self.air.distributedDistrict.b_setInvasionType(suitName)
            else:
                self.air.distributedDistrict.b_setInvasionType(suitDept)
            self.air.distributedDistrict.b_setInvasionFlags(flags)
        else:
            self.air.distributedDistrict.b_setInvasionStatus('')
            if suitName is not None:
                self.air.distributedDistrict.b_setInvasionType(suitName)

        # If this is a normal invasion, and the players take too long to defeat
        # all of the Cogs, we'll want the invasion to timeout:
        if invasionType == InvasionType.NORMAL:
            timeout = ConfigVariableInt('invasion-timeout', random.randint(20, 60) * 60).getValue()
            taskMgr.doMethodLater(timeout, self.stopInvasion, 'invasionTimeout')
            self.air.distributedDistrict.b_setInvasionTimeout(time.time() + timeout)

        self.sendInvasionStatus()
        return True

    def stopInvasion(self, taskName: Optional[str] = None):
        if not self.invading:
            # We are not currently invading.
            return False

        # Stop the invasion timeout task:
        taskMgr.remove('invasionTimeout')

        # Update the invasion tracker on the districts page in the Shticker Book:
        self.air.distributedDistrict.b_setInvasionStatus('')
        self.air.distributedDistrict.b_setInvasionType('')
        self.air.distributedDistrict.b_setInvasionFlags(0)
        self.air.distributedDistrict.b_setInvasionTimeout(0)

        # Revert what was done when the invasion started:
        self.notifyInvasionEnded()
        self.invading = False
        self.start = 0
        self.suitDept = None
        self.suitName = None
        self.flags = 0
        self.total = 0
        self.remaining = 0
        self.type = None
        self.hasSentInvasionHalfwayBulletin = False
        self.flySuits()

        self.sendInvasionStatus()
        self.air.sendNetEvent('invasionEnded', [self.air.ourChannel], channels=[MESSENGER_CHANNEL_UD])

    def notifyInvasionStarted(self):
        msgType = ToontownGlobals.SuitInvasionBegin
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionBegin
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionBegin
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionBegin
        elif self.flags & IFExe:
            msgType = ToontownGlobals.ExeInvasionBegin
        if self.type == InvasionType.MEGA:
            msgType = ToontownGlobals.SuitMegaInvasionBegin
        self.air.newsManager.sendUpdate(
            'setInvasionStatus',
            [msgType, self.suitName if self.suitName else self.suitDept, self.total, self.flags])

    def notifyInvasionEnded(self):
        msgType = ToontownGlobals.SuitInvasionEnd
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionEnd
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionEnd
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionEnd
        elif self.flags & IFExe:
            msgType = ToontownGlobals.ExeInvasionEnd
        if self.type == InvasionType.MEGA:
            msgType = ToontownGlobals.SuitMegaInvasionEnd
        self.air.newsManager.sendUpdate(
            'setInvasionStatus', [msgType, self.suitName if self.suitName else self.suitDept, 0, self.flags])

    def notifyInvasionUpdate(self):
        self.hasSentInvasionHalfwayBulletin = True
        self.air.newsManager.sendUpdate(
            'setInvasionStatus',
            [ToontownGlobals.SuitInvasionUpdate, self.suitName if self.suitName else self.suitDept,
             self.remaining, self.flags])

    def notifyInvasionBulletin(self, avId):
        msgType = ToontownGlobals.SuitInvasionBulletin
        if self.flags & IFSkelecog:
            msgType = ToontownGlobals.SkelecogInvasionBulletin
        elif self.flags & IFWaiter:
            msgType = ToontownGlobals.WaiterInvasionBulletin
        elif self.flags & IFV2:
            msgType = ToontownGlobals.V2InvasionBulletin
        elif self.flags & IFExe:
            msgType = ToontownGlobals.ExeInvasionBulletin
        if self.type == InvasionType.MEGA:
            msgType = ToontownGlobals.SuitMegaInvasionBulletin
        self.air.newsManager.sendUpdateToAvatarId(
            avId, 'setInvasionStatus',
            [msgType, self.suitName if self.suitName else self.suitDept, self.remaining, self.flags])

    def flySuits(self):
        for suitPlanner in list(self.air.suitPlanners.values()):
            suitPlanner.flySuits()

    def handleSuitDefeated(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.stopInvasion()
        elif self.remaining <= (self.total // 2) and not self.hasSentInvasionHalfwayBulletin:
            self.notifyInvasionUpdate()
        self.sendInvasionStatus()

    def handleStartInvasion(self, shardId, *args):
        if shardId == self.air.districtId:
            self.startInvasion(*args)

    def handleStopInvasion(self, shardId):
        if shardId == self.air.districtId:
            self.stopInvasion()

    def getInvasionStatus(self) -> DistrictInvasionStatsUD | None:
        if not self.invading:
            return None

        if self.suitDept:
            if self.suitName:
                invasionType = SuitBattleGlobals.SuitAttributes[self.suitName]['name']
            else:
                invasionType = SuitDNA.getDeptFullname(self.suitDept)
        else:
            invasionType = None

        return DistrictInvasionStatsUD(
            type=invasionType.replace('\x03', '') if isinstance(invasionType, str) else None,
            flags=self.flags,
            remaining=self.remaining,
            total=self.total,
            startedAt=self.start,
            forceEndsIn=self.air.distributedDistrict.getInvasionTimeRemaining(),
        )

    def sendInvasionStatus(self):
        invasionStatus = self.getInvasionStatus()
        if not invasionStatus:
            self.air.netMessenger.send(NET_MESSENGER_SHARD_INVASION_STATUS, [self.air.ourChannel, {}])
        else:
            self.air.netMessenger.send(NET_MESSENGER_SHARD_INVASION_STATUS, [self.air.ourChannel, invasionStatus.toDict()])
