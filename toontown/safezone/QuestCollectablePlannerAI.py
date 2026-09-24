from direct.showbase import DirectObject
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from direct.task import Task

from toontown.quest3.context.QuestCollectableContext import QuestCollectableContext
from toontown.safezone.DistributedCollectableAI import DistributedCollectableAI
from toontown.safezone.DistributedQuestCollectableAI import DistributedQuestCollectableAI
from toontown.safezone import CollectableGlobals
import time



@DirectNotifyCategory()
class QuestCollectablePlannerAI(DirectObject.DirectObject):
    

    def __init__(self, zoneId, treasureStyle, callback = None, treasureType: str = 'quest'):
        self.zoneId = zoneId
        self.treasureType = treasureType
        self.treasureStyle = treasureStyle
        # Just to be completely sure this is unique.......
        self.taskName = f'QuestCollectablePlannerAI-{zoneId}-{treasureStyle}-{time.time()}'
        self.callback = callback

        self.maxTreasures = 1
        self.spawnInterval = 5

        self.treasureSpawns = []
        for info in CollectableGlobals.Collectable2Pos.get(treasureStyle):
            self.treasureSpawns.append(info)
        self.treasures = [None] * len(self.treasureSpawns)

        self.deleteTaskNames = set()
        self.lastRequestId = None
        self.requestStartTime = None
        self.requestCount = None

    def numTreasures(self):
        counter = 0
        for treasure in self.treasures:
            if treasure:
                counter += 1

        return counter

    def countEmptySpawnPoints(self):
        counter = 0
        for treasure in self.treasures:
            if treasure is None:
                counter += 1

        return counter

    def nthEmptyIndex(self, n):
        emptyCounter = -1
        spawnPointCounter = -1
        while emptyCounter < n:
            spawnPointCounter += 1
            if self.treasures[spawnPointCounter] is None:
                emptyCounter += 1

        return spawnPointCounter

    def findIndexOfTreasureId(self, treasureId):
        counter = 0
        for treasure in self.treasures:
            if treasure is None:
                pass
            elif treasureId == treasure.getDoId():
                return counter
            counter += 1

    def placeAllTreasures(self):
        index = 0
        for treasure in self.treasures:
            if not treasure:
                self.placeTreasure(index)
            index += 1

    def placeTreasure(self, index):
        x, y, z = self.treasureSpawns[index]
        if self.treasureType == 'quest':
            treasure = DistributedQuestCollectableAI(
                simbase.air, self, self.treasureStyle, x, y, z)
        else:
            treasure = DistributedCollectableAI(simbase.air, self, self.treasureStyle, x, y, z)
        treasure.generateWithRequired(self.zoneId)
        self.treasures[index] = treasure

    def validAvatar(self, treasure, av):
        return treasure.validAvatar(av)

    def grabAttempt(self, avId, treasureId, specialArgs = 0):
        if self.lastRequestId == avId:
            self.requestCount += 1
            now = globalClock.getFrameTime()
            elapsed = now - self.requestStartTime
            if elapsed > 10:
                self.requestCount = 1
                self.requestStartTime = now
            else:
                secondsPerGrab = elapsed / self.requestCount
                if self.requestCount >= 3 and secondsPerGrab <= 0.4:
                    simbase.air.writeServerEvent(
                        'suspicious', avId,
                        'TreasurePlannerAI.grabAttempt %s treasures in %s seconds' % (self.requestCount, elapsed)
                    )
        else:
            self.lastRequestId = avId
            self.requestCount = 1
            self.requestStartTime = globalClock.getFrameTime()
        index = self.findIndexOfTreasureId(treasureId)
        if index is None:
            pass
        else:
            av = simbase.air.doId2do.get(avId)
            if av is None:
                simbase.air.writeServerEvent('suspicious', avId, 'TreasurePlannerAI.grabAttempt unknown avatar')
                self.notify.warning('avid: %s does not exist' % avId)
            else:
                treasure = self.treasures[index]
                if isinstance(treasure, DistributedQuestCollectableAI):
                    context = QuestCollectableContext(collectable=treasure.treasureStyle)
                    questId = simbase.air.quest3Manager.progressObjective(quester=av, context=context,
                                                                          completeOnlyOne=True)
                    if questId:
                        self.treasures[index] = None
                        if self.callback:
                            self.callback(avId)
                        treasure.d_setGrab(avId)
                        self.deleteTreasureSoon(treasure)
                    else:
                        treasure.d_setReject(avId)
                else:
                    treasure.d_setReject(avId)

    def deleteTreasureSoon(self, treasure):
        taskName = treasure.uniqueName('deletingTreasure')
        taskMgr.doMethodLater(5, self.__deleteTreasureNow, taskName, extraArgs = (treasure, taskName))
        self.deleteTaskNames.add(taskName)

    def deleteAllTreasuresNow(self):
        for treasure in self.treasures:
            if treasure:
                treasure.requestDelete()

        for taskName in self.deleteTaskNames:
            tasks = taskMgr.getTasksNamed(taskName)
            if len(tasks):
                treasure = tasks[0].getArgs()[0]
                treasure.requestDelete()
                taskMgr.remove(taskName)

        self.deleteTaskNames = set()
        self.treasures = [None] * len(self.treasureSpawns)

    def __deleteTreasureNow(self, treasure, taskName):
        treasure.requestDelete()
        self.deleteTaskNames.remove(taskName)

    def start(self):
        self.preSpawnTreasures()
        self.startSpawning()

    def stop(self):
        self.stopSpawning()

    def stopSpawning(self):
        taskMgr.remove(self.taskName)

    def startSpawning(self):
        self.stopSpawning()
        taskMgr.doMethodLater(self.spawnInterval, self.upkeepTreasurePopulation, self.taskName)

    def upkeepTreasurePopulation(self, task):
        if self.numTreasures() < self.maxTreasures:
            self.placeRandomTreasure()
        taskMgr.doMethodLater(self.spawnInterval, self.upkeepTreasurePopulation, self.taskName)
        return Task.done

    def placeRandomTreasure(self):
        self.notify.debug('Placing a Treasure...')
        spawnPointIndex = 0
        self.placeTreasure(spawnPointIndex)

    def preSpawnTreasures(self):
        for i in range(self.maxTreasures):
            self.placeRandomTreasure()
