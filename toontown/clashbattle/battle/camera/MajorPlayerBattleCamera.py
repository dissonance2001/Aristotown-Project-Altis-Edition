import random
from typing import List

from direct.interval.IntervalGlobal import *

from toontown.clashbattle.battle import BattleGlobals, MovieUtil
from toontown.clashbattle.battle.BattleCamera import BattleCamera
from toontown.clashbattle.battle.statuses.StatusEffectEnums import StatusEffectEnum
from toontown.instances.mercs.MajorPlayerBattleRoom import MajorPlayerBattleRoom
from toontown.clashsuit.suit import SuitDNA, SuitGlobals
from toontown.clashsuit.suit.DistributedSuitBase import DistributedSuitBase
from toontown.toon.DistributedToonBase import DistributedToonBase
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory


@DirectNotifyCategory()
class MajorPlayerBattleCamera(BattleCamera):
    """
    Major Player's battle camera, with unique mechanics for wait for input.
    """

    """
    When we enter/leave input, we hide the disco ball if we're in the first phase.
    """

    def enterWaitForInput(self, **kwargs) -> None:
        super().enterWaitForInput(**kwargs)

        # If we are in the first phase, hide the disco ball.
        if self.isFirstPhase():
            self.battleRoom.hideCentralBall()

    def exitWaitForInput(self):
        super().exitWaitForInput()

        # If we are in the first phase, re-show the disco ball.
        if self.isFirstPhase():
            self.battleRoom.showCentralBall()

    """
    When in the second phase, we will use a unique wait for input position.
    """

    def getPosWaitForInput(self):
        if self.isSecondPhase():
            return Point3(0, -14.1, 3.0)
        else:
            return super().getPosWaitForInput()

    def getHprWaitForInput(self):
        if self.isSecondPhase():
            return Vec3(0, 12, 0)
        else:
            return super().getHprWaitForInput()

    """
    Getters
    """

    def isFirstPhase(self) -> bool:
        return not self.isSecondPhase()

    def isSecondPhase(self) -> bool:
        """
        Determines if we are in the second phase of the battle.
        """
        for suit in self.suits:
            if suit.style.name == 'mplayer':
                # Major Player is this suit, return True if his effect is maxed out.
                effect = suit.getStatusEffectOfId(StatusEffectEnum.EFFECT_MANAGER_MAJOR_PLAYER)
                return effect and effect.hasRevived()
        # No major player, not in second phase :(
        return False

    @property
    def battleRoom(self) -> MajorPlayerBattleRoom:
        return self.battle.instance.battleRoom
