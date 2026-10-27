from toontown.battle import DistributedBattleAI
from direct.directnotify import DirectNotifyGlobal
from toontown.dna import DNABattleCell

class BattleManagerAI:
    notify = DirectNotifyGlobal.directNotify.newCategory('BattleManagerAI')

    def __init__(self, air):
        self.air = air
        self.cellId2battle = {}
        self.battleConstructor = DistributedBattleAI.DistributedBattleAI

    def cellHasBattle(self, cellId):
        return cellId in self.cellId2battle

    def getBattle(self, cellId):
        if cellId in self.cellId2battle:
            return self.cellId2battle[cellId]
        return None

    def newBattle(self, cellId, zoneId, pos, suit, toonId, finishCallback = None, maxSuits = 4, interactivePropTrackBonus = -1):
        if cellId in self.cellId2battle:
            self.notify.info("A battle is already present in the suit's zone!")
            if not self.requestBattleAddSuit(cellId, suit):
                suit.flyAwayNow()
            battle = self.cellId2battle[cellId]
            battle.signupToon(toonId, pos[0], pos[1], pos[2])
        else:
            battle = self.battleConstructor(self.air, self, pos, suit, toonId, zoneId, finishCallback, maxSuits, interactivePropTrackBonus=interactivePropTrackBonus)
            battle.battleCellId = cellId
            self.cellId2battle[cellId] = battle
            battle.generateWithRequired(zoneId)
        return battle

    def requestBattleAddSuit(self, cellId, suit):
        return self.cellId2battle[cellId].suitRequestJoin(suit)

    def destroy(self, battle):
        cellId = getattr(battle, 'battleCellId', None)
        if cellId is None or self.cellId2battle.get(cellId) is not battle:
            cellId = next((key for key, value in self.cellId2battle.items() if value is battle), None)
        if cellId is not None and self.cellId2battle.get(cellId) is battle:
            self.notify.debug('BattleManager - destroying battle %d' % cellId)
            del self.cellId2battle[cellId]
        battle.requestDelete()