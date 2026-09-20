from toontown.battle import BattleManagerAI
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.coghq import BattleExperienceAggregatorAI
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from toontown.ai.ToontownAIRepository import ToontownAIRepository


# from toontown.toonbase import ToontownGlobals


@DirectNotifyCategory()
class PersistentLevelBattleManagerAI(BattleManagerAI.BattleManagerAI):
    """
    PersistentLevelBattleManagerAI(BattleManagerAI)
    """

    def __init__(self, air, level, battleCtor):
        """
        :type air: ToontownAIRepository
        """
        self.notify.debug("init")
        BattleManagerAI.BattleManagerAI.__init__(self, air)
        self.battleCtor = battleCtor
        self.level = level

    def destroyBattleMgr(self):
        battles = list(self.cellId2battle.values())
        for battle in battles:
            self.destroy(battle)

        del self.cellId2battle

    def newBattle(self, cellId, zoneId, pos, suit, toonId, roundCallback=None, finishCallback=None, maxSuits=4):
        """
        :type maxSuits: int
        :return: battleCtor
        """
        battle = self.cellId2battle.get(cellId, None)
        if battle is not None:
            self.notify.debug('battle already created by battle blocker, add toon %d' % toonId)
            battle.signupToon(toonId, pos[0], pos[1], pos[2])
            return battle, False

        battle = self.battleCtor(
            self.air, self, pos, suit,
            toonId, zoneId, self.level,
            cellId, roundCallback, finishCallback, maxSuits
        )

        battle.addToon(toonId)
        self.cellId2battle[cellId] = battle
        # Mark the battle cell as currently active
        self.level.getEntity(cellId).setActive(True)
        return battle, True

    def destroy(self, battle):
        cellId = battle.battleCellId
        super().destroy(battle)
        # Mark the battle cell as no longer active
        self.level.getEntity(cellId).setActive(False)
