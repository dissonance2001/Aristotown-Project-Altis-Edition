from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task

from toontown.clashbattle.battle.SuitBattleGlobals import INVASIONABLE_COGS

from toontown.distributed.OtpDoGlobals import MESSENGER_CHANNEL_AI

from toontown.clashsuit.suit.SuitDNA import suitDepts
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.clashsuit.suit.SuitInvasionGlobals import *

import random
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from toontown.uberdog.ToontownUberRepository import ToontownUberRepository


def getRandomDelay():
    # Always make each run a minimum of 60 seconds.
    return max(int(1000 * random.random()), 60)


@DirectNotifyCategory()
class SuitInvasionManagerUD(DirectObject):
    def __init__(self, air):
        super().__init__()

        self.air = air  # type: ToontownUberRepository
        self.shards = []
        self.occupiedShards = []
        self.safeShards = []
        self.accept('registerShard', self.registerShard)
        self.accept('invasionEnded', self.invasionEnded)

    def invasionEnded(self, shardId):
        if shardId not in self.occupiedShards:
            return
        self.occupiedShards.remove(shardId)

    def startInitialInvasion(self):
        self.air.sendNetEvent('requestShards', channels=[MESSENGER_CHANNEL_AI])
        taskMgr.doMethodLater(600, self.chooseInvasion, 'choose-task')

    def registerShard(self, shardId, online, safe, diagnostics, motd):
        shardId -= 1
        if online and (shardId not in self.shards):
            self.shards.append(shardId)
            if safe:
                self.safeShards.append(shardId)
        elif (not online) and (shardId in self.shards):
            self.shards.remove(shardId)
            if shardId in self.occupiedShards:
                self.occupiedShards.remove(shardId)
            if shardId in self.safeShards:
                self.safeShards.remove(shardId)

    def chooseInvasion(self, task: Task):
        task.delayTime = getRandomDelay()
        if not len(self.shards):
            return task.again

        eligibleShards = set(self.shards) - set(self.safeShards) - set(self.occupiedShards)
        if not eligibleShards:
            return task.again

        shardId = random.choice(list(eligibleShards))

        # 50% chance to not spawn an invasion:
        invasionChance = random.random()
        if invasionChance <= 0.5:
            return task.again

        # Choose the invasion type:
        invasionType = InvasionType.NORMAL

        # Decide whether the invasion will have flags:
        flags = 0  # normal invasion

        dept = random.choice(suitDepts)
        suit = random.choice(INVASIONABLE_COGS.get(dept))

        self.occupiedShards.append(shardId)
        self.air.sendNetEvent(
            'startInvasion',
            [shardId, dept, suit, flags, invasionType.value],
            channels=[MESSENGER_CHANNEL_AI]
        )

        return task.again
