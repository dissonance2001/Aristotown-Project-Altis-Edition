import random
import time

from toontown.level.Entity import Entity
from direct.showbase.PythonUtil import Functor


BuildingRng = random.Random()


class BuildingMgrAI(Entity):
    """This class manages buildings in AI persistent level instances"""
    ManageBuildingsTaskName = 'BuildingMgrAI-ManageBuildingsTask'
    TaskDelay = 30.0
    # Will heavily slow down at this amount
    NearMaxThreshold = 0.75
    # How long until a building can try to get taken over again after its been tried
    BuildingTimeout = 5 * 60

    def __init__(self, level, entId):
        Entity.__init__(self, level, entId)
        self.buildings = []
        self.pathCollections = []
        self.taskName = f'{self.ManageBuildingsTaskName}-{level.doId}-{entId}'
        # If a building has been slotted to be taken over by a path collection,
        # we won't select this building again til it's timestamp has passed.
        self.buildingTimeoutTimestamps = {}  # buildingEntId -> timestamp

        # Listen for every building creation
        self.accept(self.level.getEntityOfTypeCreateEvent('building'), self.handleBuildingCreated)
        # Listen for every suit path collection creation
        self.accept(self.level.getEntityOfTypeCreateEvent('suitPathCollection'), self.handlePathCollectionCreated)
        # Listen for the level to be fully finished to start managing buildings
        self.acceptOnce(self.level.getLevelPostCreateEvent(), self.__beginManageBuildings)

    def destroy(self):
        self.removeAllTasks()
        self.ignoreAll()
        self.buildings = []
        self.pathCollections = []
        self.buildingTimeoutTimestamps = {}
        Entity.destroy(self)

    @property
    def suitBuildings(self):
        return [building for building in self.buildings if building.isSuitBlock()]

    @property
    def toonBuildings(self):
        return [building for building in self.buildings if building.isToonBlock()]

    @property
    def capturableBuildings(self):
        return [building for building in self.toonBuildings if building.capturable and building.enabled and
                building.getCurrentOrNextState() != 'BecomingToon' and
                time.time() > self.buildingTimeoutTimestamps.get(building.entId, 0)]

    def getBuildingSpawnChance(self):
        # Never spawn a building if we're at our desired max
        if len(self.suitBuildings) >= self.suitBuildingMax:
            return 0

        # Always spawn a building 100% if we are below our desired minimum
        if len(self.suitBuildings) < self.suitBuildingMin:
            return 1

        # Very very low chance to spawn a building if we're up to 75% of our max
        if len(self.suitBuildings) >= (self.suitBuildingMax * self.NearMaxThreshold):
            return 0.004

        # Total distance between our minimum amount and our maximum amount
        buildingInbetween = self.suitBuildingMax - self.suitBuildingMin

        # Otherwise, do a lerp to get our percentage chance to spawn one
        # Essentially, we are checking how far we are between the minimum and maximum.
        # At far minimum, we will be at 0.2.
        # At far maximum, we will be at 0.02.
        return lerp(0.2, 0.02, (self.suitBuildingMax - len(self.suitBuildings)) / buildingInbetween)

    def __beginManageBuildings(self):
        self.doMethodLater(self.TaskDelay, self.__manageBuildings, name=self.taskName)

    def __manageBuildings(self, task=None):
        # Return instantly if we already have enough suit buildings
        if len(self.suitBuildings) >= self.suitBuildingMax:
            return task.again

        # Get our spawn chance based on current number of cog buildings
        buildingSpawnChance = self.getBuildingSpawnChance()
        if BuildingRng.random() > buildingSpawnChance:
            # L, they failed the random chance. Better luck next time!!!
            return task.again

        # We're in the clear, we can go ahead and find a random building to take over!

        if len(self.capturableBuildings) <= 0:
            # We've got no capturable toon buildings to take over anyways, so we can die
            return task.again

        ourBuilding = BuildingRng.choice(self.capturableBuildings)
        # We've got a building, now we need to find out what path collections
        # have chosen to be associated with this building
        associatedPaths = [pathColl for pathColl in self.pathCollections if ourBuilding.entId in pathColl.buildingIds and pathColl.enabled]
        if len(associatedPaths) <= 0:
            # We've got no associated paths, so we can also go ahead and die.
            return task.again

        # Go ahead and choose one of the associated paths at random
        pathColl = BuildingRng.choice(associatedPaths)
        # Tell this path that this building has been a bad boy and needs to be punished
        success = pathColl.markBuildingForTakeover(ourBuilding)
        if not success:
            # There actually wasn't a cog available to try and take over this building.
            # Oh well. Try again later.
            return task.again

        # Now mark the timestamp of when this building can be selected for takeover again
        self.buildingTimeoutTimestamps[ourBuilding.entId] = time.time() + self.BuildingTimeout

        # We're all done now!!!!
        # Check back again soon!!!!!
        return task.again

    def handleBuildingCreated(self, entId):
        buildingEnt = self.level.getEntity(entId)
        self.buildings.append(buildingEnt)

        # listen for the building's destruction
        self.accept(self.level.getEntityDestroyEvent(entId), Functor(self.handleBuildingDestroy, entId))

    def handleBuildingDestroy(self, entId):
        buildingEnt = self.level.getEntity(entId)
        if buildingEnt in self.buildings:
            self.buildings.remove(buildingEnt)

    def handlePathCollectionCreated(self, entId):
        pathColl = self.level.getEntity(entId)
        self.pathCollections.append(pathColl)

        # listen for the building's destruction
        self.accept(self.level.getEntityDestroyEvent(entId), Functor(self.handlePathCollectionDestroy, entId))

    def handlePathCollectionDestroy(self, entId):
        pathColl = self.level.getEntity(entId)
        if pathColl in self.pathCollections:
            self.pathCollections.remove(pathColl)
