import random

from otp.ai.AIBaseGlobal import *
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory

from toontown.battle import SuitBattleGlobals
from toontown.suit import DistributedSuitBaseAI
from toontown.suit import SuitTimings
from toontown.suit import SuitDialog
from toontown.building import SuitBuildingGlobals


@DirectNotifyCategory()
class DistributedPersistentLevelSuitAI(DistributedSuitBaseAI.DistributedSuitBaseAI):
    def __init__(self, air, suitPlanner):
        DistributedSuitBaseAI.DistributedSuitBaseAI.__init__(self, air, suitPlanner)
        self.levelGone = 0
        self.spawnPointId = None
        self.spawnPathCollectionId = None
        self.spawnMethod = None
        self.spawnTimestamp = 0
        self.inLevelBattle = False
        self.__markedForDeath = False

    def levelIsGoingDown(self):
        self.levelGone = 1

    def setInLevelBattle(self, inLevelBattle: bool, battleCellId: int):
        oldBattleState = self.inLevelBattle
        self.inLevelBattle = inLevelBattle
        if inLevelBattle:
            # Suit has entered a level battle, let our spawn collection know
            self.persistentLevel.getEntity(self.spawnPathCollectionId).suitGotInBattle(self, battleCellId)
        elif bool(oldBattleState) and not self.inLevelBattle:
            # We were in a battle and aren't anymore, also let our spawn collection know
            self.persistentLevel.getEntity(self.spawnPathCollectionId).suitLeftBattle(self)

    def getInLevelBattle(self):
        return self.inLevelBattle

    def requestDelete(self):
        self.persistentLevel.getEntity(self.spawnPathCollectionId).suitDied(self)
        super().requestDelete()

    def delete(self):
        self.ignoreAll()
        self.removeAllTasks()
        DistributedSuitBaseAI.DistributedSuitBaseAI.delete(self)

    def setLevelDoId(self, levelDoId):
        self.levelDoId = levelDoId
        self.persistentLevel = self.air.getDo(self.levelDoId)

    def getLevelDoId(self):
        return self.levelDoId

    def getBattleCell(self):
        return self.persistentLevel.getEntity(self.spawnPathCollectionId).chooseBattleCell(self)

    def requestBattle(self, x, y, z, h, p, r):
        toonId = self.air.getAvatarIdFromSender()
        if self.notify.getDebug():
            self.notify.debug(str(self.getDoId()) + str(self.zoneId) + ': request battle with toon: %d' % toonId)

        if self.__markedForDeath:
            # We're gone, tell the Toon to go away!!!
            self.b_setBrushOff(SuitDialog.getBrushOffIndex(self.getStyleName()))
            self.d_denyBattle(toonId)
            return

        self.confrontPos = Point3(x, y, z)
        self.confrontHpr = Vec3(h, p, r)
        if self.sp.requestBattle(self, toonId):
            if self.notify.getDebug():
                self.notify.debug(
                    'Suit %d requesting battle in zone %d with toon %d' % (self.getDoId(), self.zoneId, toonId))
        else:
            if self.notify.getDebug():
                self.notify.debug(
                    'requestBattle from suit %d, toon %d- denied by battle manager' % (toonId, self.getDoId()))
            # self.b_setBrushOff(SuitDialog.getBrushOffIndex(self.getStyleName()))
            self.d_denyBattle(toonId)

    def getConfrontPosHpr(self):
        return (self.confrontPos, self.confrontHpr)

    def resume(self):
        self.notify.debug('Suit %s resume' % self.doId)
        self.setInLevelBattle(False, -1)
        if self.hp <= 0:
            messenger.send(self.getDeathEvent())
            self.notify.debug('Suit %s dead after resume' % self.doId)
            self.requestRemoval()
        else:
            self.b_beginDanceThenFlyAway()
        return None

    def getSpawnInformation(self):
        return self.spawnPointId, self.spawnPathCollectionId, self.spawnMethod, self.spawnTimestamp

    def b_setSpawnInformation(self, spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp):
        self.setSpawnInformation(spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp)
        self.d_setSpawnInformation(spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp)

    def setSpawnInformation(self, spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp):
        self.spawnPointId, self.spawnPathCollectionId, self.spawnMethod, self.spawnTimestamp = spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp

    def d_setSpawnInformation(self, spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp):
        self.sendUpdate('setSpawnInformation', [spawnPointId, spawnPathCollectionId, spawnMethod, spawnTimestamp])

    def __deathTask(self, task=None):
        self.requestDelete()
        return task.done

    def getMarkedForDeath(self):
        return self.__markedForDeath

    def b_beginFlyAway(self):
        self.__markedForDeath = True
        self.sendUpdate('beginFlyAway', [time.time()])
        self.doMethodLater(SuitTimings.toSky + 5.0, self.__deathTask, name=self.uniqueName('LevelSuitAI-DeathTask'))

    def b_beginDanceThenFlyAway(self):
        self.__markedForDeath = True
        self.sendUpdate('beginDanceThenFlyAway', [time.time()])
        self.doMethodLater(SuitTimings.victoryDance + SuitTimings.toSky + 5.0, self.__deathTask, name=self.uniqueName('LevelSuitAI-DeathTask'))

    def b_beginTakeOverBuilding(self, buildingEntId):
        self.__markedForDeath = True
        self.sendUpdate('beginTakeOverBuilding', [buildingEntId, time.time()])
        self.doMethodLater(SuitBuildingGlobals.LEVEL_CLEAR_OUT_TOON_BLDG_TIME + 5.0, self.__deathTask, name=self.uniqueName('LevelSuitAI-DeathTask'))
