import random
from typing import List

from direct.interval.IntervalGlobal import *

from toontown.clashbattle.battle import BattleGlobals, MovieUtil
from toontown.clashbattle.battle.BattleCamera import BattleCamera
from toontown.clashbattle.battle.statuses.StatusEffectEnums import StatusEffectEnum
from toontown.instances.mercs.MajorPlayerBattleRoom import MajorPlayerBattleRoom
from toontown.clashsuit.suit import SuitDNA, SuitGlobals
from toontown.clashsuit.suit.ClashSuitBase import ClashSuitBase
from toontown.toon.DistributedToonBase import DistributedToonBase
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class HighRollerBattleCamera(BattleCamera):
    """
    High Roller's battle camera, with unique mechanics for wait for input.
    """

    minigameBattlePos = Point3(-34, 0, 8.5)
    minigameBattleHpr = Vec3(-90, -6, 0)

    """
    During a minigame round's gag select, we will use a unique wait for input position.
    """

    def getPosWaitForInput(self):
        if self.battle.minigameActive:
            return Point3(-3, -30, 4.0)
        elif self.battle.reserveSpawn == self.battle.ReserveSpawnState.HOLLIES:
            return Point3(0, -14.1, 3.0)
        else:
            return super().getPosWaitForInput()

    def getHprWaitForInput(self):
        if self.battle.minigameActive:
            return Vec3(0, 9, 0)
        elif self.battle.reserveSpawn == self.battle.ReserveSpawnState.HOLLIES:
            return Vec3(0, 12, 0)
        else:
            return super().getHprWaitForInput()

    """
    During a minigame round's battle, we will override the camera to a wide shot.
    """

    def getMinigameCamera(self, attackDuration: float) -> Sequence:
        return Sequence(
            Func(camera.setPos, self.minigameBattlePos),
            Func(camera.setHpr, self.minigameBattleHpr),
            Wait(attackDuration),
        )

    def chooseHealShot(self, heals, attackDuration):
        if self.battle.minigameActive:
            return self.getMinigameCamera(attackDuration)
        return super().chooseHealShot(heals, attackDuration)

    def chooseTrapShot(self, attackDuration):
        if self.battle.minigameActive:
            return self.getMinigameCamera(attackDuration)
        return super().chooseTrapShot(attackDuration)

    def chooseThrowShot(self, throws, suitThrowsDict, attackDuration):
        if self.battle.minigameActive:
            return self.getMinigameCamera(attackDuration)
        return super().chooseThrowShot(throws, suitThrowsDict, attackDuration)

    def chooseZapShot(self, attackDuration):
        if self.battle.minigameActive:
            return self.getMinigameCamera(attackDuration)
        return super().chooseZapShot(attackDuration)

    def chooseSoundShot(self, sounds, targets, attackDuration):
        if self.battle.minigameActive:
            return self.getMinigameCamera(attackDuration)
        return super().chooseSoundShot(sounds, targets, attackDuration)

    def chooseDropShot(self, drops, suitDropsDict, attackDuration):
        if self.battle.minigameActive:
            return self.getMinigameCamera(attackDuration)
        return super().chooseDropShot(drops, suitDropsDict, attackDuration)

    def chooseFireShot(self, fires, suitFiresDict, attackDuration):
        if self.battle.minigameActive:
            return self.getMinigameCamera(attackDuration)
        return super().chooseFireShot(fires, suitFiresDict, attackDuration)

    def chooseSquirtShot(self, squirts, suitSquirtsDict, attackDuration):
        if self.battle.minigameActive:
            return self.getMinigameCamera(attackDuration)
        return super().chooseSquirtShot(squirts, suitSquirtsDict, attackDuration)
