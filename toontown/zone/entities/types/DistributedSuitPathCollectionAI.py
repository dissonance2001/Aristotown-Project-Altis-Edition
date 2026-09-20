import time
import random
from panda3d.core import Vec3
from toontown.level.DistributedEntityAI import DistributedEntityAI
from toontown.level.editor import EditorGlobals
from toontown.suit import SuitTimings
from toontown.zone.entities.standalone.DistributedPersistentLevelSuitAI import DistributedPersistentLevelSuitAI
from toontown.suit.SuitGlobals import SuitSpawnMethod, SpawnMethodToTiming
from toontown.toonbase import ToontownGlobals
from toontown.utils.DirectNotifyCategory import DirectNotifyCategory
from toontown.zone.data.SuitSpawnData import SuitSpawnRegistry, SuitSpawnID
from toontown.zone.entities.types.DistributedBuildingEntityAI import DistributedBuildingEntityAI
from toontown.zone.entities.types.SuitBattleCellAI import SuitBattleCellAI
from typing import List, Optional


SpawnRng = random.Random()


@DirectNotifyCategory()
class DistributedSuitPathCollectionAI(DistributedEntityAI):
    """
    DistributedSuitPathCollectionAI(DistributedEntityAI)

    A distributed collection of SuitPathPoints.
    """
    SpawnTaskName = 'DistributedSuitPathCollectionAI-SpawnTask'
    BattleCellForgiveness = 11.0

    def __init__(self, level, entId):
        self.notify.debug('init entity %s' % entId)
        DistributedEntityAI.__init__(self, level, entId)
        self.suitPaths = []
        self.pathCompletionTime = 0
        self.pointToWalkTime = {}
        self.activeSuits = []
        self.spawnData = SuitSpawnRegistry[self.spawnDataKey]
        self.buildingToFastestPoint = {}
        self.battleCellIdToActiveSuits = {}
        self.__trackingBattleCells = False
        self.acceptOnce(self.level.getLevelPostCreateEvent(), self.__beginSuitPaths)

    def beginMarkingBuildings(self):
        for entId in self.buildingIds:
            self.level.setEntityCreateCallback(entId, lambda: self.markBuildingTravelTime(entId))

    def markBuildingTravelTime(self, entId):
        # Everytime a building is generated, we will store the fastest point to reach it.
        building = self.level.getEntity(entId)
        fastestPoint, fastestWalkTime = None, 9999
        for point in self.suitPaths:
            # Find the total distance between our current point and the building
            totalDistance = Vec3(point.pos - building.pos).length()
            # Find the time to walk over that distance
            walkTime = (totalDistance / ToontownGlobals.SuitWalkSpeed)
            if walkTime < fastestWalkTime:
                fastestWalkTime = walkTime
                fastestPoint = point

        self.buildingToFastestPoint[entId] = fastestPoint.entId

    def destroy(self):
        self.removeAllTasks()
        self.suitPaths = []
        for suit in self.activeSuits:
            suit.requestDelete()
        self.activeSuits = []
        self.buildingToFastestPoint = {}
        self.spawnData = None
        self.battleCellIdToActiveSuits = {}
        DistributedEntityAI.destroy(self)

    def __initPoints(self):
        # Run through all of the level's suit paths and check which ones belong to us
        for suitPath in self.level.getEntitiesOfType('suitPathPoint'):
            if suitPath.parentEntId == self.entId:
                suitPath.setSuitPathCollection(self)
                self.suitPaths.append(suitPath)

        # Now it is time to calculate the total time needed to complete the path.
        self.__calculateTotalPathTime()

    def __calculateTotalPathTime(self):
        # Run through each suit point and check how long it takes to get there from the last
        currPath = self.suitPaths[0]
        firstPathId = currPath.entId
        while True:
            nextPathId = currPath.pointsTo
            if nextPathId == 0:
                # We don't point to anything else, we're done
                break

            # Get the object of the next suit point
            nextPath = self.level.getEntity(nextPathId)
            # Find the total distance between our current point and the next
            totalDistance = Vec3(nextPath.pos - currPath.pos).length()
            # Keep track of point to walk time
            walkTime = (totalDistance / ToontownGlobals.SuitWalkSpeed)
            self.pointToWalkTime[currPath.entId] = walkTime
            currPath = nextPath
            # We're done if our current path is now our first path. We've done a full loop.
            if currPath.entId == firstPathId:
                break

        # All point to walk times are complete, count the total.
        self.pathCompletionTime = sum(self.pointToWalkTime.values())

    def __beginSuitPaths(self):
        if self.enabled:
            # Run through level entities and find our associated suit paths
            self.__initPoints()
            # Let's mark all the buildings travel times
            self.beginMarkingBuildings()
            # Start spawning cogs now!!!!
            self.__startSpawnTask()

    def __startSpawnTask(self):
        self.removeTask(self.uniqueName(self.SpawnTaskName))
        self.doMethodLater(self.spawnDelay, self.__spawnTask, name=self.uniqueName(self.SpawnTaskName))

    def __spawnTask(self, task=None):
        task.delayTime = self.spawnDelay

        # This spawning code is very preliminary and will need more touch-ups later.

        if len(self.activeSuits) >= self.maxSuits:
            return task.again

        spawnChance = 0.3
        if len(self.activeSuits) < self.minSuits:
            spawnChance = 1.0

        if SpawnRng.random() <= spawnChance:
            suitDict = self.getSuitDict()
            newSuit: DistributedPersistentLevelSuitAI = self.level.planner.genSuitObject(suitDict)
            spawnMethod = SuitSpawnMethod.FlyIn
            newSuit.setSpawnInformation(self.chooseRandomSpawnPoint(), self.entId, spawnMethod, self.getSpawnTimeIncludingSpawnMethod(spawnMethod))
            newSuit.generateWithRequired(self.zoneId)
            self.activeSuits.append(newSuit)

        return task.again

    @staticmethod
    def getSpawnTimeIncludingSpawnMethod(spawnMethod) -> float:
        return time.time() + SpawnMethodToTiming[spawnMethod]

    def chooseRandomSpawnPoint(self) -> int:
        return SpawnRng.choice(self.suitPaths).entId

    def getSuitDict(self) -> dict:
        suitDict = self.spawnData.getRandomSuitDict()
        return suitDict

    def getSuitPosOnPath(self, suit: DistributedPersistentLevelSuitAI):
        timeDiff = time.time() - suit.spawnTimestamp

        currPath = self.level.getEntity(suit.spawnPointId)
        if timeDiff <= 0:
            # We haven't even moved yet, our path has to be the spawn point
            return Vec3(currPath.pos)

        if self.pathCompletionTime <= 0:
            # We have nowhere to go, so they're already in the right spot
            return Vec3(currPath.pos)

        leftover = timeDiff % self.pathCompletionTime
        # Run through each connecting point until we run out of time remaining
        while leftover > 0:
            nextPathId = currPath.pointsTo
            if nextPathId == 0:
                # We don't point to anything else, we're done
                return Vec3(currPath.pos)

            nextPath = self.level.getEntity(nextPathId)
            # Get time to walk to next point
            walkTime = self.pointToWalkTime[currPath.entId]
            leftover -= walkTime
            if leftover <= 0:
                # We've gone below 0 remaining time.
                # Let's calculate how far along to the next point we are now
                relativeTime = (walkTime - abs(leftover)) / walkTime
                cPos = currPath.pos
                nPos = nextPath.pos
                x = lerp(cPos[0], nPos[0], relativeTime)
                y = lerp(cPos[1], nPos[1], relativeTime)
                z = lerp(cPos[2], nPos[2], relativeTime)
                return Vec3(x, y, z)
            else:
                currPath = nextPath

    def getPointAndLeftoverBasedOnTime(self, suit: DistributedPersistentLevelSuitAI):
        # We have no place to go, they haven't moved.
        if self.pathCompletionTime <= 0:
            return self.level.getEntity(suit.spawnPointId), 0.0

        # Get the amount of time that has happened since they spawned
        timeDiff = time.time() - suit.spawnTimestamp
        # Time difference may be eeeever so slightly below 0 if we're coming out of a spawn.
        # We can go ahead and fix that.
        timeDiff = max(timeDiff, 0)
        leftover = timeDiff % self.pathCompletionTime

        # Do some course correction, this suit may have spawned a long time ago
        currPoint = self.level.getEntity(suit.spawnPointId)
        while leftover > 0:
            nextPathId = currPoint.pointsTo
            if nextPathId == 0:
                break

            walkTime = self.pointToWalkTime[currPoint.entId]
            leftover -= walkTime
            # Leftover is greater than zero, so they still have an amount to walk.
            # We're done if its less than zero.
            if leftover > 0:
                currPoint = self.level.getEntity(nextPathId)

        # Leftover will either be zero or a negative number.
        # If zero, their current point is fine and we can continue onwards.
        # If it's negative, then that value indicates how close
        # to the end of the current path they are.
        return currPoint, leftover

    def getWalkTimeToPoint(self, pointId, suit: DistributedPersistentLevelSuitAI):
        # First get their current position on the path
        currPoint, leftover = self.getPointAndLeftoverBasedOnTime(suit)
        # We need to calculate the full walk time til we hit this point
        firstWalkTime = self.pointToWalkTime[currPoint.entId]
        totalTime = 0.0 - (firstWalkTime - abs(leftover))
        while True:
            totalTime += self.pointToWalkTime[currPoint.entId]
            nextPathId = currPoint.pointsTo
            if nextPathId == 0:
                # We're about to get stuck, so just stop as soon as we hit this
                return max(totalTime, 0.0)

            currPoint = self.level.getEntity(nextPathId)
            if currPoint.entId == pointId:
                # The next point is the one we want, we're done
                return max(totalTime, 0.0)

    def getInactiveBattleCells(self) -> List[SuitBattleCellAI]:
        allBattleCells = [self.level.getEntity(battleCellId) for battleCellId in self.battleCellIds]
        return [battleCell for battleCell in allBattleCells if not battleCell.getActive()]

    def getClosestInactiveBattleCell(self, suit: DistributedPersistentLevelSuitAI) -> Optional[SuitBattleCellAI]:
        suitPos = self.getSuitPosOnPath(suit)
        cellDict = {}
        inactiveBattleCells = self.getInactiveBattleCells()
        if len(inactiveBattleCells) <= 0:
            # No battle cell available, die
            return None
        # Create a dictionary containing each battle cell and how far from the suit it is.
        for battleCell in inactiveBattleCells:
            cellDict[battleCell] = Vec3(suitPos - Vec3(battleCell.pos)).length()
        # Sort it in ascending order.
        sortedCells = sorted(cellDict.items(), key=lambda x: x[1], reverse=False)
        chosenCell = sortedCells[0][0]
        return chosenCell

    def chooseBattleCell(self, suit: DistributedPersistentLevelSuitAI) -> Optional[SuitBattleCellAI]:
        return self.getClosestInactiveBattleCell(suit)

    def suitDied(self, suit: DistributedPersistentLevelSuitAI) -> None:
        if suit in self.activeSuits:
            self.activeSuits.remove(suit)
        self.removeTask(self.getSuitTakeOverTaskName(suit))
        self.removeTask(self.getSuitEnterDoorTaskName(suit))

    def getSuitTakeOverTaskName(self, suit: DistributedPersistentLevelSuitAI):
        return self.uniqueName(f'DSPCAI-SuitTakeOverBuilding-{suit.doId}')

    def getSuitEnterDoorTaskName(self, suit: DistributedPersistentLevelSuitAI):
        return self.uniqueName(f'DSPCAI-SuitEnterDoor-{suit.doId}')

    def getCheckBattleCellTaskName(self):
        return self.uniqueName('DSPCAI-CheckBattleCells')

    def markBuildingForTakeover(self, building: DistributedBuildingEntityAI) -> bool:
        if not self.enabled:
            return False

        # We now have a building that we need a suit to take over.
        # We can go ahead and pick a random suit,
        # they'll make their way over there eventually.
        availableSuits = [suit for suit in self.activeSuits if not suit.getInLevelBattle() and
                          time.time() - suit.spawnTimestamp > 0]
        if len(availableSuits) <= 0:
            # Oops, no available Suits. Oh well.
            return False

        chosenSuit = SpawnRng.choice(availableSuits)
        closestPointId = self.buildingToFastestPoint[building.entId]
        walkTime = self.getWalkTimeToPoint(closestPointId, chosenSuit)
        self.doMethodLater(walkTime, self.__suitTakeOverBuilding, self.getSuitTakeOverTaskName(chosenSuit), extraArgs=[chosenSuit, building])
        return True

    def __suitTakeOverBuilding(self, suit: DistributedPersistentLevelSuitAI, building: DistributedBuildingEntityAI):
        # Tell the suit and the building what they need to do.
        building.suitTakeOver(suitTrack=suit.dna.dept, difficulty=suit.getLevel() - 1)
        # We'll pass through the door ID here so that the suit has something to reference.
        # They will need to know where the door is in order to walk into it.
        suit.b_beginTakeOverBuilding(building.doors[0].doId)
        # Also, we can start a small task to tell the building's door to let the suit in
        # once the correct amount of time has elapsed.
        self.doMethodLater(SuitTimings.LevelSuitTakeoverBuildingWalkTime, self.__suitEnterBuildingDoorTask, self.getSuitEnterDoorTaskName(suit), extraArgs=[suit, building.doors[0]])

    def __suitEnterBuildingDoorTask(self, suit, door):
        door.requestSuitEnter(suit.doId)

    def __checkForJoinBattleCellTask(self, task=None):
        task.delayTime = 0.85

        # To be eligible to check if they need to join a battle, a suit must:
        # 1. Not be in another battle, and
        # 2. Have finished spawning (+1 second for safety), and
        # 3. Not be "marked for death" (Currently dancing or flying away)
        eligibleSuits = [suit for suit in self.activeSuits if (not suit.getInLevelBattle()) and time.time() >= (suit.spawnTimestamp + 1.0) and (not suit.getMarkedForDeath())]

        # Run through each battle cell ID and check if we need to try the suit joining the battle.
        for battleCellId in self.battleCellIdToActiveSuits.keys():
            if len(self.battleCellIdToActiveSuits[battleCellId]) > 0:
                # Battle cell is active, check all of our suits and see if they are close enough to join it.
                battleCell = self.level.getEntity(battleCellId)
                for suit in eligibleSuits:
                    if Vec3(self.getSuitPosOnPath(suit) - battleCell.pos).length() <= self.BattleCellForgiveness:
                        # The suit's position on the path is within a certain distance of the battle.
                        # We can now try to let them join the battle.
                        self.level.planner.checkForBattle(battleCellId, suit)

        return task.again

    def suitGotInBattle(self, suit: DistributedPersistentLevelSuitAI, battleCellId: int):
        # Remove any take over tasks if we had them
        self.removeTask(self.getSuitTakeOverTaskName(suit))
        self.removeTask(self.getSuitEnterDoorTaskName(suit))
        # Mark them as in the battle for purposes of checking for other suits
        self.battleCellIdToActiveSuits.setdefault(battleCellId, [])
        if suit.doId not in self.battleCellIdToActiveSuits[battleCellId]:
            self.battleCellIdToActiveSuits[battleCellId].append(suit.doId)
            if not self.__trackingBattleCells:
                self.__trackingBattleCells = True
                self.addTask(self.__checkForJoinBattleCellTask, name=self.getCheckBattleCellTaskName())

    def suitLeftBattle(self, suit: DistributedPersistentLevelSuitAI):
        # Remove them from the battle cell id list if they're in it
        for cellId, activeSuitList in list(self.battleCellIdToActiveSuits.items()):
            if suit.doId in activeSuitList:
                activeSuitList.remove(suit.doId)
            if len(activeSuitList) <= 0:
                del self.battleCellIdToActiveSuits[cellId]

        # After running through every suit, if there are no suits left at all, then stop the battle cell tracking task.
        if len(self.battleCellIdToActiveSuits) <= 0 and self.__trackingBattleCells:
            self.removeTask(self.getCheckBattleCellTaskName())
            self.__trackingBattleCells = False

    if EditorGlobals.wantLevelEditor():
        def setBuildingIds(self, buildingIds):
            self.buildingIds = buildingIds
            if not self.enabled:
                return
            # Refresh and start marking buildings again
            self.buildingToFastestPoint = {}
            self.beginMarkingBuildings()

        def setMaxSuits(self, maxSuits):
            self.maxSuits = maxSuits
            if not self.enabled:
                return
            killAmount = len(self.activeSuits) - self.maxSuits
            suitsLeft = self.activeSuits[:]
            if killAmount >= 1:
                for _ in range(killAmount):
                    suit = suitsLeft.pop()
                    suit.b_beginFlyAway()
                    if not len(suitsLeft):
                        break

        def setEnabled(self, enabled):
            self.enabled = enabled
            self.suitPaths = []
            self.pathCompletionTime = 0
            self.pointToWalkTime = {}
            self.buildingToFastestPoint = {}
            for suit in self.activeSuits[:]:
                suit.requestDelete()
            self.activeSuits = []
            self.removeTask(self.uniqueName(self.SpawnTaskName))
            if enabled:
                self.__beginSuitPaths()

        def setSpawnDataKey(self, spawnDataKey):
            self.spawnDataKey = spawnDataKey
            if self.spawnDataKey in SuitSpawnRegistry:
                self.spawnData = SuitSpawnRegistry[self.spawnDataKey]
            else:
                self.notify.warning(f'Invalid spawn data key!! ({spawnDataKey}). Using default test.')
                self.spawnData = SuitSpawnRegistry[SuitSpawnID.Test]
