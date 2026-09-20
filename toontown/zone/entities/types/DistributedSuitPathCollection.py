import time
from panda3d.core import *
from direct.interval.IntervalGlobal import *
from direct.showbase.PythonUtil import fitDestAngle2Src

from toontown.zone.entities.standalone.DistributedPersistentLevelSuit import DistributedPersistentLevelSuit
from toontown.level.BasicEntities import DistributedNodePathEntity
from toontown.level.editor import EditorGlobals
from toontown.toonbase import ToontownGlobals
from toontown.zone.entities.types.SuitPathPoint import SuitPathPoint


class DistributedSuitPathCollection(DistributedNodePathEntity):
    """
    DistributedSuitPathCollection(BasicEntities.NodePathEntity)

    A distributed collection of SuitPathPoints.
    """

    def __init__(self, cr):
        DistributedNodePathEntity.__init__(self, cr)
        self.model = None
        self.suitPaths = []
        self.pathCompletionTime = 0
        self.pointToWalkTime = {}
        self.activeSuits = []
        self.allPointsReady = False

    def announceGenerate(self):
        DistributedNodePathEntity.announceGenerate(self)
        if self.level:
            self.__beginSuitPaths()

        if EditorGlobals.wantLevelEditor():
            self.model = self.attachNewNode('indicatorSphere')
            sphere = loader.loadModel('phase_3/models/misc/sphere')
            sphere.setScale(3)
            sphere.setTransparency(1)
            sphere.setColorScale(0, 1, 0, 0.4)
            sphere.reparentTo(self.model)

    def initializeEntity(self, level, entId):
        DistributedNodePathEntity.initializeEntity(self, level, entId)

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
            self.allPointsReady = True
            messenger.send(self.getAllPointsReadyEvent())

    def getAllPointsReadyEvent(self):
        return self.uniqueName('DistributedSuitPathCollection-AllPointsReady')

    def getWalkTrack(self, suit: DistributedPersistentLevelSuit) -> Sequence:
        # Grab current suit point / leftover of suit
        currPoint, leftover = suit.getPointAndLeftoverBasedOnTime()
        currPos = Vec3(currPoint.getPos(render))

        if currPoint.pointsTo == 0:
            # Point doesn't point to anything, let's just stand still.
            walkTrack = Sequence(
                Func(suit.setPos, currPos),
                Func(suit.loop, 'neutral'),
                Wait(100000),
            )
        else:
            # We have a point, let's make a track showing us walking to it
            nextPoint: SuitPathPoint = self.level.getEntity(currPoint.pointsTo)
            # Get total distance between current point and next point
            nextPos = nextPoint.getPos(render)
            temp = render.attachNewNode('foo')
            temp.setPos(currPos)
            temp.headsUp(nextPos)
            nextHpr = temp.getHpr(render)
            if suit.getH() > 360:
                suit.setH(suit.getH() - 360)
            if suit.getH() < -360:
                suit.setH(suit.getH() + 360)
            nextHpr = (fitDestAngle2Src(suit.getH(), nextHpr[0]), nextHpr[1], nextHpr[2])
            temp.removeNode()
            walkTime = self.pointToWalkTime[currPoint.entId]
            if leftover < 0 and suit.firstWalkDone:
                walkTime -= (walkTime - abs(leftover))

            def updatePoint(suit=suit):
                suit.currentPathPoint = nextPoint

            walkTrack = Sequence(
                Parallel(
                    LerpHprInterval(suit, min(walkTime, 0.2), nextHpr, blendType='easeIn'),
                    LerpPosInterval(suit, walkTime, nextPos, other=render)
                ),
                Func(updatePoint),
            )
        suit.firstWalkDone = True
        return walkTrack

    def delete(self):
        if self.model:
            self.model.removeNode()
            self.model = None
        self.suitPaths = []
        self.pointToWalkTime = {}
        self.activeSuits = []
        DistributedNodePathEntity.delete(self)

    def getSuitPosOnPath(self, suit: DistributedPersistentLevelSuit, timestamp=None):
        timeDiff = (timestamp or time.time()) - suit.spawnTimestamp

        currPath = self.level.getEntity(suit.spawnPointId)
        if timeDiff <= 0:
            # We haven't even moved yet, our path has to be the spawn point
            return Vec3(currPath.getPos(render))

        if self.pathCompletionTime <= 0:
            # Our path is instantly complete, we are stopping immediately
            return Vec3(currPath.getPos(render))

        leftover = timeDiff % self.pathCompletionTime
        # Run through each connecting point until we run out of time remaining
        while leftover > 0:
            nextPathId = currPath.pointsTo
            if nextPathId == 0:
                # We don't point to anything else, we're done
                return Vec3(currPath.getPos(render))

            nextPath = self.level.getEntity(nextPathId)
            # Get time to walk to next point
            walkTime = self.pointToWalkTime[currPath.entId]
            leftover -= walkTime
            if leftover <= 0:
                # We've gone below 0 remaining time.
                # Let's calculate how far along to the next point we are now
                relativeTime = (walkTime - abs(leftover)) / walkTime
                cPos = currPath.getPos(render)
                nPos = nextPath.getPos(render)
                x = lerp(cPos[0], nPos[0], relativeTime)
                y = lerp(cPos[1], nPos[1], relativeTime)
                z = lerp(cPos[2], nPos[2], relativeTime)
                return Vec3(x, y, z)
            else:
                currPath = nextPath

    def getNodePath(self):
        return self

    if EditorGlobals.wantLevelEditor():
        def setEnabled(self, enabled):
            self.enabled = enabled
            self.suitPaths = []
            self.pathCompletionTime = 0
            self.pointToWalkTime = {}
            self.activeSuits = []
            if enabled:
                self.__beginSuitPaths()
